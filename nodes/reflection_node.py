import os
import re
import logging
from schemas.state_schemas import AppState
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser


def extract_code_blocks(text: str) -> str:
    match = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()


def reflect_and_correct_test_case(state: AppState) -> AppState:
    error = state.get("error", "")
    selenium_code_path = state.get("selenium_code_path")
    test_case_path = state.get("test_case_path")
    page_html = state.get("page_html")

    if not error or not selenium_code_path or not test_case_path:
        logging.warning("Missing required context for test case reflection.")
        return state

    with open(selenium_code_path, "r", encoding="utf-8") as f:
        selenium_code = f.read()

    with open(test_case_path, "r", encoding="utf-8") as f:
        test_case_code = f.read()

    test_case_critique_prompt = """
### ROLE
You are a detail-oriented QA engineer. You will receive a Selenium function, a corresponding test case, an error message from a failed test run, and the HTML body of the page under test.

### INSTRUCTIONS
Your task is to analyze the compatibility of the test case with the Selenium function. If the test case is broken or incompatible, provide a **corrected** version of the test case as a Python function that can run successfully. If the test case looks perfect and ready for execution, then **only return the word `STOP`** (no code, no whitespace, no newline).

### CONTEXT:
Selenium Function:
{selenium_code}

Test Case:
{test_case_code}

Error Message:
{error}

HTML Body:
{page_html}
"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a senior QA engineer reviewing a test case."),
            ("human", test_case_critique_prompt),
            MessagesPlaceholder("messages"),
        ]
    )

    latest_test_case = (
        state.get("messages", [])[-1].content
        if state.get("messages")
        else test_case_code
    )

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)
    chain = prompt | llm | StrOutputParser()

    response = chain.invoke(
        {
            "selenium_code": selenium_code,
            "test_case_code": latest_test_case,
            "error": error,
            "page_html": page_html,
            "messages": state.get("messages", []),
        }
    )

    if response == "STOP":
        logging.info("Test case validated successfully. Proceeding without changes.")
        state["status"] = "success"
    else:
        corrected_test_code = extract_code_blocks(response)
        output_dir = "generated_code"
        corrected_test_case_path = os.path.join(output_dir, "corrected_test_case.py")
        with open(corrected_test_case_path, "w", encoding="utf-8") as f:
            f.write(corrected_test_code)

        logging.info("Reflected and corrected test case saved.")
        state["test_case_path"] = corrected_test_case_path
        state["retry_count"] = state.get("retry_count", 0) + 1
        state["messages"] = state.get("messages", []) + [HumanMessage(content=response)]

    return state
