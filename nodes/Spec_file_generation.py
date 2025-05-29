from typing import TypedDict
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langchain.prompts import ChatPromptTemplate
import requests
import re
import os
from dotenv import load_dotenv
import time
from langgraph.graph import StateGraph, END


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

class AppState(TypedDict):
    github_url: str
    readme: str
    login_context: str
    spec_md: str

def fetch_readme(state: AppState) -> AppState:
    github_url = state['github_url'].rstrip('/')
    match = re.match(r'https://github\.com/([^/]+)/([^/]+)', github_url)
    if not match:
        raise ValueError("Invalid GitHub URL")

    user, repo = match.groups()
    raw_url = f"https://raw.githubusercontent.com/{user}/{repo}/master/README.md"
    response = requests.get(raw_url)

    if response.status_code != 200:
        raise ValueError(f"Could not fetch README.md from {raw_url}")
    
    print("fetch_readme method called.")
    return {**state, "readme": response.text}


def extract_login_info(state: AppState) -> AppState:
    start_time = time.time()
    readme = state["readme"]
    image_urls = re.findall(r'!\[.*?\]\((https?://[^\s)]+)\)', readme)
    images_text = "\n".join(image_urls) if image_urls else "No image URLs found."

    prompt_template = ChatPromptTemplate.from_template("""
From the provided README document and the list of image URLs, you are to extract ONLY the information that is strictly and exclusively related to the **Login Page** or **Login Functionality**.

**Focus your extraction on the following aspects of the Login Page:**
1.  **Input Fields:** Identify all fields visible on the login screen (e.g., "email address input", "password field", "username").
2.  **Expected Behavior & Scenarios:** Describe the expected outcomes of user interactions, including:
    *   Successful login process.
    *   Failure cases (e.g., incorrect credentials, invalid input format, account lockout).
3.  **Validation Rules:** Detail any validation performed on the input fields (e.g., "email must be a valid format", "password must be at least 8 characters").
4.  **Relevant Screenshot URLs:** From the "Screenshot URLs" list provided below, identify and list ONLY those URLs that clearly and directly depict the Login Page itself or critical elements of the login process.

**Strictly Exclude:**
*   Any information not directly pertaining to the login page or login functionality.
*   General UI descriptions or screenshots that are not focused on login, even if the login elements are part of a larger screen. Only include URLs if the primary subject of the screenshot is the login interface.

**Input Data:**

**Screenshot URLs:**
{image_urls}

**README Content:**
{readme}

""")

    formatted_prompt = prompt_template.format_messages(
        image_urls=images_text,
        readme=readme
    )

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest",
        google_api_key="AIzaSyAYJE8n_m_jEUWQL2LZvFpcshqLVN5oEBg",
        temperature=0)
    response = llm.invoke(formatted_prompt)
    end_time = time.time()
    print(f"extract_login_info took {end_time - start_time:.2f} seconds")

    return {**state, "login_context": response.content.strip()}


def generate_spec(state: AppState) -> AppState:
    start_time = time.time()
    login_info = state["login_context"]

    prompt_template = ChatPromptTemplate.from_template("""
From the provided README document and the list of image URLs, you are to extract ONLY the information that is strictly and exclusively related to the **Login Page** or **Login Functionality**.

**Focus your extraction on the following aspects of the Login Page:**
1. **Login Page Specification:** 
2. **Description:** Add the login page description here
3.  **Input Fields:** Identify all fields visible on the login screen (e.g., "email address input", "password field", "username").
4.  **Validation Rules:** Detail any validation performed on the input fields (e.g., "email must be a valid format", "password must be at least 8 characters").

**Strictly Exclude:**
*   Any information not directly pertaining to the login page or login functionality.
*   General UI descriptions or screenshots that are not focused on login, even if the login elements are part of a larger screen. Only include URLs if the primary subject of the screenshot is the login interface.

**Input Data:**


**Login Info:**
{login_info}

""")

    formatted_prompt = prompt_template.format_messages(login_info=login_info)
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest",
        google_api_key="AIzaSyAYJE8n_m_jEUWQL2LZvFpcshqLVN5oEBg",
        temperature=0)   
    response = llm.invoke(formatted_prompt)
    end_time = time.time()
    print(f"generate_spec took {end_time - start_time:.2f} seconds")

    return {**state, "spec_md": response.content.strip()}