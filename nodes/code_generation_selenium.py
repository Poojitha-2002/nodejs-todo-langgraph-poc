import os
import base64
import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from schemas.state_schemas import AppState

def extract_code_blocks(text: str) -> str:
    code_match = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    return code_match.group(1).strip() if code_match else text.strip()

def generate_selenium_code(state: AppState) -> dict:
    load_dotenv()

    spec = state["login_spec"]
    html = state["page_html"]
    image_path = state["image_path"]
    webdriver_path = state.get("driver_path", "")
    login_url = state["login_url"]

    image_data = ""
    if image_path and os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            image_data = base64.b64encode(img_file.read()).decode("utf-8")

    driver_line = (
        f'driver = webdriver.Chrome("{webdriver_path}")  # Path provided explicitly'
        if webdriver_path
        else 'driver = webdriver.Chrome()  # Assuming ChromeDriver is in system PATH'
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful coding assistant. Only return clean, executable Python code with no explanation."),
        ("human",
         "Given the following login specification and the HTML of a login page, generate Python Selenium code that:\n"
         "- Loads the login page using the provided URL\n"
         "- Ensures the page is loaded correctly\n"
         "- Locates the username, password fields, and login button based on spec or HTML\n"
         "- Enters provided credentials and submits the form\n"
         "Use the attached screenshot (if any) to assist.\n"
         "- Initializes the WebDriver as:\n  {driver_line}\n\n"
         "### Login URL:\n{login_url}\n\n"
         "### Login Spec:\n{spec}\n\n"
         "### Page HTML:\n{html}\n\n"
         "Return only a Python function named `login(url, username, password)`, no extra text."
        )
    ])

    formatted_messages = prompt.format_messages(
        driver_line=driver_line,
        login_url=login_url,
        spec=spec,
        html=html
    )

    if image_data:
        formatted_messages[-1].content = [
            {"type": "text", "text": formatted_messages[-1].content},
            {
                "type": "image",
                "source_type": "base64",
                "data": image_data,
                "mime_type": "image/jpeg"
            }
        ]

    llm = ChatOpenAI(temperature=0.2, model="gpt-4o-mini")

    response = llm.invoke(formatted_messages)
    generated_code_raw = response.content
    parsed_code = extract_code_blocks(generated_code_raw)

    output_dir = "generated_code"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "generated_selenium_code.py")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(parsed_code)

    return {"selenium_code_path": output_path}
