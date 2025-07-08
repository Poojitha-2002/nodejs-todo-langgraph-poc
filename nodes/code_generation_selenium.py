import os
import re
import base64
from dotenv import load_dotenv
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from schemas.state_schemas import AppState
import logging


def extract_code_blocks(text: str) -> str:
    match = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()


def generate_selenium_code(state: AppState) -> dict:
    """
    Generates Selenium code based on the given HTML, URL, spec_md.
    
    Takes page HTML, spec_md, and optional image.
    Sends a prompt to LLM to create Python code.
    Saves the code to a file and returns the path.

    Args:
        state (AppState): Page context and settings.

    Returns:
        dict: Path to code and updated retry count.
    """
    load_dotenv()
    # gemini_api_key = os.getenv("GEMINI_API_KEY")
    # if not gemini_api_key:
    #     raise ValueError("GEMINI_API_KEY not set in .env file")

    api_key = os.environ["OPENAI_API_KEY"]
    logging.info("Section: Generate Selenium Code")

    url = state["url"] 
    logging.info(f"URL: {url}")
    spec_md = state["spec_md"]
    # logging.info("SPEC_MD: ", spec_md)
    # page_html = state["page_html"]
    page_html = state.get("page_html")
    # logging.info("PAGE_HTML here: \n: ",page_html)
    image_path = state.get("image_path")
    webdriver_path = state.get("driver_path", "")
    retry_count = state.get("retry_count", 0)
    error = state.get("error", "")
    reflect_loop_count = state.get("reflect_loop_count",0)

    driver_line = (
        f'driver = webdriver.Chrome("{webdriver_path}")'
        if webdriver_path
        else "driver = webdriver.Chrome()"
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
             '''You are given the HTML content of a web page, the page URL, its functional specification, and (optionally) the error that occurred during a previous test execution.

            Your task:

            - Write a **Python function** named `{function_name}(driver)` that uses Selenium to test the functionality of the page as described.
            - The function must load the page using the provided URL and interact with the DOM according to the specification.
            - Wait for elements to load using `WebDriverWait` and explicit waits — do NOT use `sleep()`.
            - Identify elements using the best available selectors from the HTML (id, name, type, placeholder, role, aria-label, etc.). Prefer CSS selectors or attribute-based XPath.
            - Ensure selectors are **robust** — avoid brittle strategies like tag names or deeply nested paths.
            - Follow the functional specification to define the correct interactions, assertions, and expectations.
            - If an error from a previous test run is provided, adjust the function to prevent that failure.
            - If an element is dynamic or might not be immediately available, use appropriate wait conditions (e.g., `presence_of_element_located`, `element_to_be_clickable`, etc.).
            - You may use comments if something requires human review or cannot be fully determined from the inputs.
            - Do not generate example usage or invocation of the function.
            - Ensure the code is fully formed, properly indented, and valid Python.
            - The function should include assertions to verify whether the functionality described in the spec works as expected.
            - Do not limit your solution to login pages — this should work for any functional UI described in the spec.

            Inputs:
            ---

            ### Page HTML:
            {page_html}

            ### Page URL:
            {url}

            ### Functional Specification (Markdown):
            {spec_md}

            ### Previous Error (if any):
            {error}'''
        ),
        MessagesPlaceholder("messages")
    ])

    messages = prompt.format_messages(
    messages=state['messages'],
    page_html=page_html,
    function_name = url.replace("http://127.0.0.1:4000/", ""),
    url=url,
    spec_md=spec_md,
    error=error,
)
    if image_data:
        messages[-1].content = [
            {"type": "text", "text": messages[-1].content},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_data}",
                    "mime_type": "image/jpeg",
                },
            },
        ]
        image_note = "\nA screenshot is also provided as base64:\n" + image_data[:500] + "...\n"
        messages[-1].content += image_note


    # llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)
    llm = ChatOpenAI(model='gpt-4o-mini', api_key = api_key)

    chain = prompt | llm | StrOutputParser()

    response = chain.invoke({
        "messages": [HumanMessage(content=messages[-1].content)],
        "page_html": page_html,
        'url':url,
        'spec_md':spec_md,
        'error':error,
        "function_name":url.replace("http://127.0.0.1:4000/", "")})

    # response = chain.invoke({'messages': messages})

    generated_code = extract_code_blocks(response)

    output_dir = "generated_code"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "generated_selenium_code.py")

    if not os.access(output_dir, os.W_OK):
        logging.error(f"Output directory '{output_dir}' is not writable. Please check permissions.")
        raise PermissionError(f"Cannot write to output directory: {output_dir}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(generated_code)

    print("Selenium code generated successfully!")

    return {
        "selenium_code_path": output_path,
        "retry_count": retry_count + 1,
        "reflect_loop_count" : reflect_loop_count+1,
        'messages': response
    }
