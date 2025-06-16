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
        selenium_code_path = state.get("selenium_code_path", "")

    if not selenium_code_path:
        return {"error": "Missing selenium_code or valid selenium_code_path in state."}
    if not login_url:
        return {"error": "Missing login_url in state."}
    if not home_page_url:
        return {"error": "Missing home_page_url in state."}

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful Python test engineer. Return only executable Python `unittest` code with appropriate imports and clean structure. Use mocking when required. Do not include any markdown or explanation.",
            ),
            (
                "human",
                """Given a file path `generated_code/generated_selenium_code.py`, generate a Python unittest file named `test_case.py`.

                Instructions:
                - Import the existing `login()` function from `generated_code.generated_selenium_code`. Do NOT redefine it.
                - The `login()` function accepts: `url`, `username`, `password`, and `home_page_url_segment`.
                - If login is successful, it returns a WebDriver instance.
                - If login fails (due to invalid credentials, missing inputs, timeouts, etc.), it returns `False` and quits the driver internally.

                The generated `test_case.py` must:
                1. Include tests for:
                    - Successful login
                    - Login with wrong password
                    - Login with wrong username
                    - Empty username
                    - Empty password
                2. Include additional unit tests for `test_case_generation.py` failure paths, such as:
                    - Missing `login_url` in the input state
                    - Missing `home_page_url` in the input state
                    - Missing or invalid `selenium_code_path`
                    - Error during loading `login()` from file
                    - LLM failure during test case generation
                    - Pre-validation failure (login fails due to bad credentials or unexpected result)

                Test Techniques:
                - Use `unittest.mock.patch()` where needed to simulate:
                    - LLM invocation errors
                    - `load_login_function_from_path()` exceptions
                    - `login()` returning False
                - Validate test cases by checking if redirection reaches `{home_page_url}` segment.

                Other Notes:
                - Use `unittest.TestCase`
                - Keep all code self-contained and ready to run
                - Use `assertTrue`, `assertFalse`, or `assertIn` as appropriate
                - Use the following values:
                    - Email: '{email}'
                    - Password: '{password}'
                    - Login URL: {login_url}
                    - Expected Redirect URL Segment: {home_page_url}

                ### Provided Selenium `login()` Function (already implemented, import and use):
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
    # command = ["python", "-m", "unittest", test_file_path]
    # result = subprocess.run(
    #     command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    # )
    # return result.stdout
    env = os.environ.copy()
    env["COVERAGE_PROCESS_START"] = ".coveragerc"

    command = ["coverage", "run", "--parallel-mode", "-m", "unittest", test_file_path]
    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,  # 👈 This enables coverage inside the subprocess
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

        if isinstance(prevalidate_result, dict) and not prevalidate_result.get("success", True):
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
