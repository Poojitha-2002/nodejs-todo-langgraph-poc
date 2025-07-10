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


import inspect


def load_generated_function(path: str):
    module_name = "dynamic_generated_module"
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)


def extract_code_blocks(text: str) -> str:
    code_match = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    return code_match.group(1).strip() if code_match else text.strip()


def generate_test_case(state: AppState) -> dict:
    selenium_code_path = state["selenium_code_path"]
    specific_url = state["specific_url"]
    email = state["email"]
    password = state["password"]
    redirect_url = state["redirect_url"]
    functional_spec = state["spec_md"]

    if selenium_code_path and os.path.exists(selenium_code_path):
        with open(selenium_code_path, "r", encoding="utf-8") as f:
            selenium_code = f.read()
    else:
        selenium_code = state.get("selenium_code", "")

    if not selenium_code:
        return {"error": "Missing selenium_code or valid selenium_code_path in state."}
    if not specific_url:
        return {"error": "Missing specific_url in state."}
    if not redirect_url:
        return {"error": "Missing redirect_url in state."}
    if not functional_spec:
        return {"error": "Missing functional_spec in state."}

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a senior QA automation engineer specializing in writing robust, maintainable test cases using
                - Python's built-in `unittest` framework and Selenium.
                - The Selenium driver session (including cookies and current URL) is already stored in a file named `driver_session.pkl`.

                Your test code must:
                - Load this pickle file in the `setUpClass()` method to initialize the WebDriver.
                - Navigate to the base domain using `driver.get("http://<domain>")` before setting cookies with `add_cookie()`. This is required to avoid InvalidCookieDomainException.
                - After setting cookies, navigate to the original stored URL.

                You must analyze a functional specification and the provided Selenium automation code and generate a full test suite that ensures the implemented automation meets the spec.

                Use best practices including modular design, assertive checks, negative path testing, and proper driver management via `setUpClass()` and `tearDownClass()`.

                """,
            ),
            (
                "human",
                """Please write a complete Python unittest-based test suite using the following inputs:
                - **Specific URL**: `{specific_url}`
                - **Functional Specification**:'{functional_spec}'
                - **Selenium Automation Code**:```python{selenium_code}```
                ### Output Instructions:
                - Use the `unittest` module from the Python standard library.
                - Include a test class inheriting from `unittest.TestCase`.
                - In the `setUpClass()` method:
                    - Load the driver session from `driver_session.pkl`
                    - Initialize a Selenium Chrome driver and inject cookies from the file.
                    - Navigate to the previously stored page URL. 
                - Implement test methods (prefixed with `test_`) for each behavior in the spec.
                - Write both positive and negative test cases.
                - Include `assert` statements to verify expected outcomes (element presence, values, navigation, etc.).
                - Reuse code or methods from the provided Selenium script where applicable.
                - Include docstrings and inline comments to explain each test.
                - Output only the complete Python test code — no explanation, no extra text.
                """,
            ),
        ]
    )

    formatted_messages = prompt.format_messages(
        specific_url=specific_url,
        selenium_code=selenium_code,
        # email=email,
        # password=password,
        # redirect_url=redirect_url,
        functional_spec=functional_spec,
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
        test_case_path = os.path.join(output_dir, "test_case.py")

        with open(test_case_path, "w", encoding="utf-8") as f:
            f.write(parsed_code)

        print(f"Test case generated and saved to '{test_case_path}'.")
        return {
            "test_case_path": test_case_path,
            "test_code": parsed_code,
        }
    except Exception as e:
        print(f"Error generating test case: {e}")
        return {"error": str(e)}


def run_tests_and_get_output(test_case_path: str) -> str:
    command = ["python", "-m", "unittest", "generated_code.test_case"]
    result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    return result.stdout


# def run_tests_and_get_output(test_module: str) -> str:
#     env = os.environ.copy()
#     env["COVERAGE_PROCESS_START"] = ".coveragerc"

#     command = [
#         sys.executable,
#         "-m",
#         "coverage",
#         "run",
#         "--parallel-mode",
#         "-m",
#         "unittest",
#         test_module,  # <-- this is the module name
#     ]

#     result = subprocess.run(
#         command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env
#     )
#     return result.stdout


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
            "test_report_path": None,
            "test_code": None,
            "report_generated": False,
            "status": "fail",
            "error": result["error"],
        }

    state["error"] = None
    test_report_path = result["test_case_path"]
    parsed_code = result["test_code"]

    # ✅ Just run the test case without trying to call any generated function
    raw_output = run_tests_and_get_output("test_case_path")
    print("Generating test report from raw output...")

    report = generate_test_report_from_output(raw_output)
    print("Saving test report...")
    report_path = "generated_code/test_report.html"
    save_test_report(report, report_path)

    report_generated = os.path.exists(report_path)
    status = "success" if report_generated else "fail"
    print("Test Case Generation Status:", status)

    return {
        "test_report_path": test_report_path,
        "test_code": parsed_code,
        "report_generated": report_generated,
        "status": status,
        "error": None if report_generated else "Report not generated",
        "test_report_path": report_path if report_generated else None,
    }
