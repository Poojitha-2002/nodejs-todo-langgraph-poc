import os
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from schemas.state_schemas import AppState
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

def extract_code_blocks(text: str) -> str:
    code_match = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    return code_match.group(1).strip() if code_match else text.strip()

def generate_test_case(state: AppState) -> dict:
    selenium_code = ""
    selenium_code_path = state.get("selenium_code_path")
    if selenium_code_path and os.path.exists(selenium_code_path):
        with open(selenium_code_path, "r", encoding="utf-8") as f:
            selenium_code = f.read()
    else:
        selenium_code = state.get("selenium_code", "")
    if not selenium_code:
        return {"error": "Missing selenium_code or valid selenium_code_path in state."}
    
    print("Invoking LLM to generate login test case code...")

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful Python test engineer. Return only executable Python unittest code with no explanations.",
            ),
            (
                "human",
                "Given the following Python Selenium function that performs a login operation, generate a test file `test_case.py` that:\n"
                "- Imports necessary modules (`unittest`, `selenium`, etc.)\n"
                "- Sets up and tears down the Selenium WebDriver correctly\n"
                "- Calls the login function with appropriate arguments\n"
                "- Verifies successful login by checking URL, page title, or specific element\n"
                "- Defines all required classes and methods cleanly\n\n"
                "### Selenium Function:\n{selenium_code}",
            ),
        ]
    )
    formatted_messages = prompt.format_messages(selenium_code=selenium_code)

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
        print(
            f" Test case generated and saved to '{test_file_path}'."
        )

        return {
            "test_file_path": test_file_path,
            "test_code": parsed_code,
            "message": "Login test file generated using LLM",
        }
    
    except Exception as e:
        print(f":x: Error generating test case: {e}")
        return {"error": str(e)}
    

def main():
    selenium_code = """
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
def login(url, username, password):
    driver = webdriver.Chrome()
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.title_contains("Login"))
    email_field = driver.find_element(By.ID, "email")
    password_field = driver.find_element(By.ID, "password")
    login_button = driver.find_element(By.XPATH, "//input[@type='submit']")
    email_field.send_keys(username)
    password_field.send_keys(password)
    login_button.click()
"""
    state = AppState({"selenium_code": selenium_code})
    result = generate_test_case(state)
    if "error" in result:
        print(f"Test generation failed: {result['error']}")
    else:
        print(f"Test case successfully generated at {result['test_file_path']}")

        
if __name__ == "__main__":
    main()


    