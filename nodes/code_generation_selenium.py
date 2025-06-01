import os
import re
import base64
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain.prompts import ChatPromptTemplate
from nodes.state_schemas import AppState

def extract_code_blocks(text: str) -> str:
    match = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()

def generate_selenium_code(state: AppState) -> dict:
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
             "- Write a Python function named `login(url, username, password)` using Selenium.\n"
             f"### Page HTML:\n{page_html}\n\n"
             "- Loads the login page using the provided URL\n"
             "- Waits for the page to fully load and ensures the presence of login elements.\n"
             "- Locates the username and password fields in HTML page using the most appropriate selectors based on available attributes (e.g., `id`, `name`, `type`)\n"
             "- Locates the login or submit button using clear selectors defined in HTML page— avoid using only tag names\n"
             "- If a field lacks a unique ID, use XPath or CSS selectors that rely on attributes\n"
             "- Fill in the username and password fields, then click the login button to submit\n"
             "- Use the attached screenshot (if any) to assist.\n"
             f"- Initializes the WebDriver as:\n  {driver_line}\n\n"
             f"### Login URL:\n{login_url}\n\n"
             f"### Login Spec:\n{login_spec}\n\n"
             "Return only a Python function named `login(url, username, password)`, no extra text."
        )
    ])

    messages = prompt.format_messages()

    if image_data:
        messages[-1].content = [
            {"type": "text", "text": messages[-1].content},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_data}",
                    "mime_type": "image/jpeg"
                }
            }
        ]

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)

    response = llm.invoke([HumanMessage(content=messages[-1].content)])

    generated_code = extract_code_blocks(response.content)

    output_dir = "generated_code"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "generated_selenium_code.py")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(generated_code)

    return {
        "selenium_code_path": output_path,
        "retry_count": retry_count + 1
    }
