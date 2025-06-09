from schemas.state_schemas import AppState
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain.prompts import ChatPromptTemplate
import os
import re


def extract_code_blocks(text: str) -> str:
    match = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()


def reflect_and_correct_code(state: AppState) -> AppState:
    error = state.get("error", "")
    prev_code_path = state.get("selenium_code_path")
    page_html = state.get("page_html")

    if not error or not prev_code_path:
        return state  # Nothing to reflect on

    with open(prev_code_path, "r", encoding="utf-8") as f:
        prev_code = f.read()

    template = """### Previous Selenium Code:\n{prev_code}\n
    ### Test Error Message:\n{error}\n
    ### HTML body:\n{page_html}\n
    Please return a fully corrected Python function named `login(...)`.
    """

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are a senior QA engineer. Given failed test output and the previous Selenium code, reflect and correct it. Output only the corrected Python function.",
        ),
        (
            "human",
            template
        )
    ])

    messages = prompt.format_messages(prev_code=prev_code, error=error, page_html=page_html)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)
    response = llm.invoke([HumanMessage(content=messages[-1].content)])
    corrected_code = extract_code_blocks(response.content)

    output_dir = "generated_code"
    corrected_path = os.path.join(output_dir, "corrected_selenium_code.py")
    with open(corrected_path, "w", encoding="utf-8") as f:
        f.write(corrected_code)

    print("Reflected and corrected Selenium code saved.")

    state["selenium_code_path"] = corrected_path
    state["retry_count"] = state.get("retry_count", 0) + 1
    return state
