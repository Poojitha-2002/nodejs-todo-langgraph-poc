import os
import re
import subprocess
from typing import Any
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from schemas.state_schemas import AppState
import importlib.util
import sys

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")


def load_login_function_from_path(path: str):
    module_name = "dynamic_login_module"
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module.login


def extract_code_blocks(text: str) -> str:
    code_match = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    return code_match.group(1).strip() if code_match else text.strip()


def generate_test_case(state: AppState) -> dict:
    selenium_code_path = state["selenium_code_path"]
    login_url = state["login_url"]
    email = state["email"]
    password = state["password"]
    home_page_url = state["home_page_url"]

    if selenium_code_path and os.path.exists(selenium_code_path):
        with open(selenium_code_path, "r", encoding="utf-8") as f:
            selenium_code = f.read()
    else:
        selenium_code = state.get("selenium_code", "")

    if not selenium_code:
        return {"error": "Missing selenium_code or valid selenium_code_path in state."}
    if not login_url:
        return {"error": "Missing login_url in state."}
    if not home_page_url:
        return {"error": "Missing home_page_url in state."}

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a highly skilled Python test engineer specializing in Selenium WebDriver. "
                "Your task is to generate comprehensive and executable `unittest` code for the given Selenium script. "
                "Analyze the provided Selenium code to identify all functions and their parameters. "
                "For each identified functionality, create dedicated test methods "
                "that cover **all possible positive and negative test scenarios**. Focus on robust test coverage, "
                "including valid inputs, invalid inputs, edge cases, and error handling. "
                "Your output must be **only** executable Python `unittest` code with appropriate imports and "
                "clean structure. Do not include any markdown fences (```) or conversational text. "
                "**Crucially, ensure WebDriver setup (`self.driver = webdriver.Chrome()`) is ONLY in `setUp` "
                "and teardown (`self.driver.quit()`) is ONLY in `tearDown`**. "
                "NEVER call `driver.quit()` or `driver.close()` within individual test methods. "
                "Pass all necessary arguments to the Selenium functions, including URLs if the function expects one."
                "Infer sensible dummy values for credentials, URLs, or other inputs when not explicitly provided.",
            ),
            (
                "human",
                """Given the following Python Selenium script, which is located at `generated_code/generated_selenium_code.py`,
                generate a Python `unittest` file named `test_case.py`.
                **Instructions for `test_case.py`:**
                - Import relevant functions, classes, or the entire module from `generated_code.generated_selenium_code`. Do NOT redefine the original Selenium logic.
                - For each distinct functionality or interaction identified in the `selenium_code` (e.g., navigating to a page, filling a form, clicking a button, asserting element presence), create dedicated test methods.
                - When calling Selenium functions from `generated_selenium_code`, ensure all required parameters are passed. If a function expects a `url` parameter, use `'{login_url}'` as the base URL.
                - Implement **positive test cases** (e.g., successful navigation, correct data submission, expected element interaction).
                - Implement **negative test cases** (e.g., invalid data input, missing required fields, attempting actions on non-existent elements, unexpected pop-ups, handling errors).
                - Use `unittest` assertions (e.g., `self.assertTrue()`, `self.assertFalse()`, `self.assertEqual()`, `self.assertIn()`) to verify outcomes.
                - Manage WebDriver instance correctly: Initialize it in `setUp` and quit it in `tearDown` for each test class.
                - Ensure the `test_case.py` is self-contained and executable.
                **Use the following default values where appropriate for test scenarios (feel free to vary for negative tests):**
                - **Base Login URL**: `'{login_url}'`
                - **Default Username**: `'{email}'`
                - **Default Password**: `'{password}'`
                - **Expected Home Page URL Segment (for assertions)**: `'{home_page_url}'`
                **Provided Selenium Code (from `generated_code/generated_selenium_code.py`):**
                {selenium_code}
                """,
            ),
        ]
    )

    formatted_messages = prompt.format_messages(
        login_url=login_url,
        selenium_code=selenium_code,
        email=email,
        password=password,
        home_page_url=home_page_url,
    )

    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-latest", google_api_key=api_key, temperature=0
        )
        response = llm.invoke(formatted_messages)
        test_code_raw = response.content
        parsed_code = extract_code_blocks(test_code_raw)

        output_dir = "generated_code"
        os.makedirs(output_dir, exist_ok=True)
        test_file_path = os.path.join(output_dir, "test_case.py")

        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write(parsed_code)

        print(f"Test case generated and saved to '{test_file_path}'.")
        return {
            "test_file_path": test_file_path,
            "test_code": parsed_code,
        }
    except Exception as e:
        print(f"Error generating test case: {e}")
        return {"error": str(e)}


def run_tests_and_get_output(test_file_path: str) -> str:
    command = ["python", "-m", "unittest", test_file_path]
    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    return result.stdout


def generate_test_report_from_output(raw_output: str) -> str:
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a Python QA engineer. Create a clean, HTML test report based on the raw output from Python's unittest.",
            ),
            (
                "human",
                """Here is the raw unittest output:\n\n{raw_output}\n\n
                Generate a test report in HTML format with:
                - Summary section (total, passed, failed)
                - Bullet points for each test with result
                - Clear formatting
                - Only valid HTML content in the response.(No markdown)
                """,
            ),
        ]
    )

    messages = prompt.format_messages(raw_output=raw_output)
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-latest", google_api_key=api_key, temperature=0.2
        )
        response = llm.invoke(messages)
        return response.content
    except Exception as e:
        print(f":x: Failed to generate test report: {e}")
        return f"Error: {e}"


def save_test_report(report: str, path: str = "generated_code/test_report.html"):
    with open(path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f": Test report saved to {path}")


def generate_test_case_with_report(
    state: AppState,
) -> dict[str, bool | str | None | Any] | AppState:
    result = generate_test_case(state)
    if "error" in result:
        return {
            "test_file_path": None,
            "test_code": None,
            "report_generated": False,
            "status": "fail",
            "error": result["error"],
        }
    state["error"] = None

    test_file_path = result["test_file_path"]
    parsed_code = result["test_code"]

    login_url = state.get("login_url")
    username = state.get("email")
    password = state.get("password")
    home_page_url = state.get("home_page_url")

    try:

        selenium_code_path = state["selenium_code_path"]
        login = load_login_function_from_path(selenium_code_path)
        prevalidate_result = login(login_url, username, password, home_page_url)

        if isinstance(prevalidate_result, dict) and not prevalidate_result.get(
            "success", True
        ):
            state["status"] = "fail"
            state["error"] = prevalidate_result.get("error", "Unknown error")
            return state
        else:
            try:
                prevalidate_result.quit()
            except Exception:
                pass
            state["error"] = None
    except Exception as e:
        state["status"] = "fail"
        state["error"] = f"Pre-validation error: {str(e)}"
        return state

    raw_output = run_tests_and_get_output(test_file_path)

    # if "Traceback" in raw_output and "login" in raw_output:
    #     print("❌ Test failed. Passing error to code generator.")
    #     state["error"] = raw_output  # this is where your raw_output goes
    #     state["status"] = "fail"
    #     state["retry_count"] = state.get("retry_count", 0) + 1
    #     return state

    report = generate_test_report_from_output(raw_output)
    report_path = "generated_code/test_report.html"
    save_test_report(report, report_path)

    report_generated = os.path.exists(report_path)
    return {
        "test_file_path": test_file_path,
        "test_code": parsed_code,
        "report_generated": report_generated,
        "status": "success" if report_generated else "fail",
        "error": None if report_generated else "Report not generated",
    }
