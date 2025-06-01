import os
import re
import subprocess
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from nodes.state_schemas import AppState

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")


def extract_code_blocks(text: str) -> str:
    code_match = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    return code_match.group(1).strip() if code_match else text.strip()


def generate_test_case(state: AppState) -> dict:
    selenium_code = ""
    selenium_code_path = state.get("selenium_code_path")
    login_url = state.get("login_url")
    email = state.get("email")
    password = state.get("password")

    if selenium_code_path and os.path.exists(selenium_code_path):
        with open(selenium_code_path, "r", encoding="utf-8") as f:
            selenium_code = f.read()
    else:
        selenium_code = state.get("selenium_code", "")

    if not selenium_code:
        return {"error": "Missing selenium_code or valid selenium_code_path in state."}
    if not login_url:
        return {"error": "Missing login_url in state."}

    print("Invoking LLM to generate login test case...")
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful Python test engineer. Return only executable Python unittest code with no explanations.",
            ),
            (
                "human",
                "Given the following Python Selenium function that performs a login operation, generate a test file `test_case.py` that:\n"
                "- Reuses the exact email `{email}` and password `{password}` values.\n"
                "- Imports necessary modules (`unittest`, `selenium`, etc.)\n"
                "- Sets up and tears down the Selenium WebDriver correctly\n"
                "- Calls the login function with appropriate arguments\n"
                "- Verifies successful login by checking that the current URL contains '/dashboard' after login, page title, or specific element\n"
                "- Defines all required classes and methods cleanly\n\n"
                "### Login URL:\n{login_url}\n\n"
                "### Selenium Function:\n{selenium_code}",
            ),
        ]
    )

    formatted_messages = prompt.format_messages(
        login_url=login_url,
        selenium_code=selenium_code,
        email=state.get("email", ""),
        password=state.get("password", ""),
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
                "You are a Python QA engineer. Create a clean, readable test report based on the raw output from Python's unittest.",
            ),
            (
                "human",
                """Here is the raw unittest output:\n\n{raw_output}\n\n
Generate a test report in markdown format with:
- Summary section (total, passed, failed)
- Bullet points for each test with result
- Clear formatting""",
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


def save_test_report(report: str, path: str = "generated_code/test_report.md"):
    with open(path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f": Test report saved to {path}")


def generate_test_case_with_report(state: AppState) -> dict:
    result = generate_test_case(state)
    if "error" in result:
        return {
            "test_file_path": None,
            "test_code": None,
            "report_generated": False,
            "status": "fail",
            "error": result["error"],
        }

    test_file_path = result["test_file_path"]
    parsed_code = result["test_code"]

    raw_output = run_tests_and_get_output(test_file_path)
    print("\n:test_tube: Raw Test Output:\n", raw_output)

    report = generate_test_report_from_output(raw_output)
    report_path = "generated_code/test_report.md"
    save_test_report(report, report_path)

    report_generated = os.path.exists(report_path)
    return {
        "test_file_path": test_file_path,
        "test_code": parsed_code,
        "report_generated": report_generated,
        "status": "success" if report_generated else "fail",
        "error": None if report_generated else "Report not generated",
    }


# if __name__ == "__main__":
#     selenium_code = """
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

# def login(url, username, password):
#     driver = webdriver.Chrome() # Replace with your webdriver initialization
#     driver.get(url)

#     # Wait for the page to load and elements to be present
#     WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))
#     WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
#     WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "form"))) #Added to ensure form is loaded


#     email_field = driver.find_element(By.ID, "email")
#     password_field = driver.find_element(By.ID, "password")
#     login_button = driver.find_element(By.XPATH, "//form/div[3]/input[@type='submit']") #Using XPath for submit button

#     email_field.send_keys(username)
#     password_field.send_keys(password)
#     login_button.click()

#     # Add any necessary assertions or actions after login here.  For example, check for successful login redirect.

#     #driver.quit() #Uncomment if you want to close the browser after login
# """
#     state = AppState(
#         {
#             "selenium_code": selenium_code,
#             "login_url": "http://localhost:4000/login",
#             "email": "manasakonduru11@gmail.com",
#             "password": "123456",
#         }
#     )

#     result = generate_test_case_with_report(state)
#     print("\n:clipboard: Final Result:\n", result)
