import os
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from schemas.state_schemas import AppState

load_dotenv()


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
        llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
        response = llm.invoke(formatted_messages)
        test_code_raw = response.content
        parsed_code = extract_code_blocks(test_code_raw)

        output_dir = "generated_code"
        os.makedirs(output_dir, exist_ok=True)
        test_file_path = os.path.join(output_dir, "test_case.py") 

        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write(parsed_code)

        print(
            f":white_check_mark: Test case generated and saved to '{test_file_path}'."
        )
        return {
            "test_file_path": test_file_path,
            "test_code": parsed_code,
            "message": "Login test file generated using LLM",
        }

    except Exception as e:
        print(f":x: Error generating test case: {e}")
        return {"error": str(e)}
