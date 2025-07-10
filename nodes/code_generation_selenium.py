import os
import re
import base64
import logging
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from schemas.state_schemas import (
    AppState,
)

# Configure logging for better debugging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def extract_code_blocks(text: str) -> str:
    """
    Extracts Python code blocks from a given text.
    It looks for content enclosed within triple backticks (```python or ```).

    Args:
        text (str): The input text potentially containing code blocks.

    Returns:
        str: The extracted code block, or the original text if no block is found.
    """
    match = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()


def generate_selenium_code(state: AppState) -> dict:
    """
    Generates Selenium login code using Gemini AI.

    Takes page HTML, login spec, and optional image.
    Sends a prompt to Gemini to create Python code.
    Saves the code to a file and returns the path.

    Args:
        state (AppState): A dictionary-like object containing login information and settings.
                          Expected keys: "specific_url", "spec_md", "page_html" (optional),
                          "image_path" (optional), "driver_path" (optional), "retry_count" (optional),
                          "error" (optional), "reflect_loop_count" (optional).

    Returns:
        dict: A dictionary containing the path to the generated code, updated retry count,
              and updated reflection loop count.
              Keys: "selenium_code_path", "retry_count", "reflect_loop_count".
    """
    print("\n=== Entered generate_selenium_code ===")
    # print("Keys in state:", list(state.keys()))

    # Optional: Show HTML length or file path
    driver = state.get("driver_path")
    page_html = state.get("page_html", "")

    if not page_html and driver:
        try:
            logging.info("Fetching page HTML from authenticated driver...")
            page_html = driver.page_source
            state["page_html"] = page_html
        except Exception as e:
            logging.warning(f"Could not extract page HTML from driver: {e}")

    html = state.get("page_html", "")
    driver = state.get("driver_path")
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        logging.error("GEMINI_API_KEY not set in .env file. Please set it to proceed.")
        raise ValueError("GEMINI_API_KEY not set in .env file")

    # Set GOOGLE_API_KEY environment variable for Langchain
    os.environ["GOOGLE_API_KEY"] = gemini_api_key

    # Extract necessary state variables
    url = state["specific_url"]
    functional_spec = state["spec_md"]
    page_html = state.get("page_html")
    image_path = state.get("image_path")
    retry_count = state.get("retry_count", 0)
    error = state.get("error", "")
    reflect_loop_count = state.get("reflect_loop_count", 0)

    image_data = ""
    if image_path and os.path.exists(image_path):
        try:
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")
            logging.info(f"Image data loaded successfully from: {image_path}")
        except IOError as e:
            logging.error(f"Error reading image file {image_path}: {e}")
            image_data = ""

    # Construct the base textual content for the human message.
    # *** IMPORTANT MODIFICATION HERE ***
    human_text_content = (
        "You are a senior Python automation engineer specialized in writing clean, functional, and maintainable Selenium code.\n\n"
        "Your task is to write Python Selenium automation code based on the following inputs:\n"
        "1. An HTML snippet of the target web page.\n"
        "2. The full URL of the page.\n"
        "3. A detailed functional specification describing what the automation should do.\n\n"
        "### Inputs\n\n"
        "#### 1. HTML Page:\n"
        f"{page_html}\n\n"
        "#### 2. Page URL:\n"
        f"{url}\n\n"
        "#### 3. Functional Specification:\n"
        f"{functional_spec}\n\n"
        "### Output Instructions:\n"
        "- Generate complete Python Selenium code to automate the described functionality.\n"
        "- Use `selenium.webdriver.Chrome()` with appropriate options.\n"
        "- Include login/session handling if necessary.\n"
        "- Ensure the code covers all specified functionalities in the spec.\n"
        "- Add comments for major steps.\n"
        "- Output **only the complete Python code**.\n"
    )

    # Add previous error context if available, for reflection/correction by the model
    if error:
        human_text_content += f"### Previous Error for Reflection:\n{error}\n\n"
        logging.info("Adding previous error to prompt for reflection.")

    # Final instructions for the model
    human_text_content += (
        "- Do not generate example usage or explanations outside the function.\n"
        "- Only return a complete Python function implementing the task. Include necessary imports (like `webdriver`, `By`, `WebDriverWait`, `expected_conditions`, and relevant exceptions from `selenium.common.exceptions`)."
    )

    # Prepare multimodal content list for the HumanMessage.
    human_message_parts = [{"type": "text", "text": human_text_content}]

    if image_data:
        human_message_parts.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_data}",
                    "mime_type": "image/jpeg",
                },
            }
        )
        human_message_parts.append(
            {
                "type": "text",
                "text": f"\n(A screenshot is also provided, first 500 characters of base64: {image_data[:500]}...)\n",
            }
        )
        logging.info("Image data included in the human message.")

    messages_to_llm = [
        SystemMessage(
            content="You are a helpful coding assistant. Only return clean, executable Python code for the requested function, including all necessary imports."
        ),
        HumanMessage(content=human_message_parts),
    ]

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)

    logging.info("Invoking Gemini model for code generation...")
    try:
        response_message = llm.invoke(messages_to_llm)
        generated_code = extract_code_blocks(response_message.content)
        logging.info("Selenium code generated by Gemini.")
    except Exception as e:
        logging.error(f"Error during Gemini model invocation: {e}")
        generated_code = (
            "# Error: Could not generate code. Please check logs for details."
        )

    output_dir = "generated_code"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "generated_selenium_code.py")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(generated_code)
    logging.info(f"Generated Selenium code saved to: {output_path}")

    print("Selenium code generated successfully!")

    return {
        "selenium_code_path": output_path,
        "retry_count": retry_count + 1,
        "reflect_loop_count": reflect_loop_count + 1,
        "messages": generated_code
    }
