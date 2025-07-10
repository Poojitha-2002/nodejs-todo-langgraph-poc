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
    You are an intelligent QA engineer who is skilled at reading, reviewing and crafting efficient testcases. You will be given a selenium code which is to test some functional specifications of a page. Your task is to go through the code, understand it and see if the code is upto the mark.
    ### INSTRUCTIONS
    See to the fact that the code given is good enough to be sent to the next node. If you find there was a mistake in the generated code, come up with constructive criticism for the code to improve. If you think the code is syntactically correct and has been produced based on the given context, then consider yourself satisfied.
    If the code is satisfactory and it can pass onto the next node, then return STOP and nothing else. Just STOP, no nextline, no spaces, no special characters, just STOP.

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
