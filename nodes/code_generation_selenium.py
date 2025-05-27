from schemas import AppState
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
import base64

def generate_selenium_code(state: AppState) -> dict:
    spec = state["login_spec"]
    html = state["page_html"]
    image_path = state["image_path"]


    image_base64 = ""
    if image_path and os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            image_bytes = img_file.read()
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")


    # Define the prompt template
    prompt = ChatPromptTemplate.from_template("""
    Given the following login specification and the HTML of a login page, generate Python Selenium code that:
    - Loads the login page using the provided URL
    - Ensures the page is loaded correctly
    - Locates the username, password fields, and login button based on spec or HTML
    - Enters provided credentials and submits the form

    ### Login URL:
    {login_url}

    ### Login Spec:
    {spec}

    ### Page HTML:
    {html}

    ### Screenshot (Base64 Encoded, if available):
    {image_base64}                                                                                               

    Provide only the Python function definition, no extra text.
    """)

    # Format the prompt with current state
    formatted_prompt = prompt.format_messages(
        login_url=state["login_url"],
        spec=spec,
        html=html,
        image_base64=image_base64 or "[No screenshot provided]"
    )

    # Initialize LLM
    llm = ChatOpenAI(temperature=0.2, model="gpt-3.5-turbo")

    # Generate the code
    response = llm.invoke(formatted_prompt)
    generated_code = response.content

    return {"selenium_code": generated_code}
