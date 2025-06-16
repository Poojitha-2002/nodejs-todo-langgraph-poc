import os
import re
import base64
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from schemas.state_schemas import AppState

def extract_code_blocks(text: str) -> str:
    match = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()

def generate_selenium_code(state: AppState) -> dict:
    """
        Generates Selenium login code using Gemini AI.

        Takes page HTML, login spec, and optional image.
        Sends a prompt to Gemini to create Python code.
        Saves the code to a file and returns the path.

        Args:
            state (AppState): Login info and settings.

        Returns:
            dict: Path to code and updated retry count.
    """
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY not set in .env file")

    os.environ["GOOGLE_API_KEY"] = gemini_api_key

    login_url = state["login_url"]
    login_spec = state["login_spec"]
    page_html = state["page_html"]
    image_path = state.get("image_path")
    webdriver_path = state.get("driver_path", "")
    retry_count = state.get("retry_count", 0)
    error = state.get("error", "")
    reflect_loop_count = state.get("reflect_loop_count",0)

    driver_line = (
        f'driver = webdriver.Chrome("{webdriver_path}")'
        if webdriver_path else 'driver = webdriver.Chrome()'
    )

    image_data = ""
    if image_path and os.path.exists(image_path):
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")

    prompt = ChatPromptTemplate.from_messages([
        (
            "system", "You are a helpful coding assistant. Only return clean, executable Python code with no explanation."
        ),
        (
            "human",
             "You are given a login page's HTML and its functional specification.\n\n"
             "Your task:\n"
             "- Write a Python function named `login(url, username, password, home_page_url_segment)` using Selenium.\n"
             f"### HTML Page:\n{page_html}\n\n"
             "- Loads the login page using the provided URL\n"
             "- Wait for the page to fully load.\n"
             "- Use the provided HTML Page to determine selectors."
             "- Locate the username and password fields using the best available selectors (id, name, type)\n"
             "- Locate the login/submit button using attribute-based XPath or CSS selectors — do not use tag names alone.\n"
             "- If needed, use XPath or CSS based on attributes when IDs aren't available.\n"
             "- Use the attached screenshot (if any) to assist.\n"
             f"### Login URL:\n{login_url}\n\n"
             f"### Login Spec:\n{login_spec}\n\n"
             "- Ensure all code blocks are complete, properly indented, and not left empty — include at least a pass or a meaningful comment if needed."
             "- Do not generate the example usage of the code"
             f"If the function is likely to fail or run into issues, adjust and regenerate to fix them. Error message : {error}"
        ),
        MessagesPlaceholder("messages")
    ])

    messages = prompt.format_messages(
    messages=state.get("messages", []),
    page_html=page_html,
    login_url=login_url,
    login_spec=login_spec,
    error=error,
)
    if image_data:
        image_note = "\nA screenshot is also provided as base64:\n" + image_data[:500] + "...\n"
        messages[-1].content += image_note


    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)

    chain = prompt | llm | StrOutputParser()

    response = chain.invoke({"messages": [HumanMessage(content=messages[-1].content)]})

    generated_code = extract_code_blocks(response)

    output_dir = "generated_code"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "generated_selenium_code.py")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(generated_code)

    # output_path = "generated_code/generated_selenium_code.py"
    #
    # with open(output_path, "r", encoding="utf-8") as f:
    #     f.read()

    print("Selenium code generated successfully!")

    return {
        "selenium_code_path": output_path,
        "retry_count": retry_count + 1,
        "reflect_loop_count" : reflect_loop_count+1
    }
