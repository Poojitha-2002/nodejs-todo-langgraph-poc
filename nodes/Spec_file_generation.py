from typing import TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import requests
import re
import os
from dotenv import load_dotenv
load_dotenv()
import time
# from node_poc_langgraph_prompts.extract_login_info_prompt import EXTRACT_LOGIN_INFO_PROMPT
# from node_poc_langgraph_prompts.generate_spec_prompt import GENERATE_SPEC_FILE_PROMPT

api_key = os.getenv("OPENAI_API_KEY")


class AppState(TypedDict):
    github_url: str
    readme: str
    login_context: str
    spec_md: str
    
    
def fetch_readme(state: AppState) -> AppState:
    github_url = state['github_url'].rstrip('/')

    # Extract user/repo
    match = re.match(r'https://github\.com/([^/]+)/([^/]+)', github_url)
    if not match:
        raise ValueError("Invalid GitHub URL")
    
    user, repo = match.groups()

    # Using master branch here!
    raw_url = f"https://raw.githubusercontent.com/{user}/{repo}/master/README.md"

    response = requests.get(raw_url)
    if response.status_code != 200:
        raise ValueError(f"Could not fetch README.md from {raw_url}")
    print("fetch_readme method called.")
    return {**state, "readme": response.text}


def extract_login_info(state: AppState) -> AppState:
    start_time = time.time()
    readme = state["readme"]
    
    # Extract image URLs from Markdown
    image_urls = re.findall(r'!\[.*?\]\((https?://[^\s)]+)\)', readme)
    images_text = "\n".join(image_urls) if image_urls else "No image URLs found."

    prompt = f"""
From the following README and list of image URLs, extract ONLY the information strictly related to the **Login Page**.

Focus on:
- What fields are shown on the login screen (e.g., email, password)
- What behavior is expected (successful login, failure cases)
- What validation is performed
- Screenshot URLs that clearly relate to login (ignore unrelated UI other than login page)

Exclude:
- Any general UI screenshots not related to login

Screenshot URLs:
{images_text}

README:
{readme}
"""

    llm = ChatOpenAI(api_key=api_key,model="gpt-4o-mini", temperature=0)
    response = llm.invoke([HumanMessage(content=prompt)])
    end_time = time.time()
    print(f"extract_login_info took {end_time - start_time:.2f} seconds")
    return {**state, "login_context": response.content.strip()}


def generate_spec(state: AppState) -> AppState:
    start_time = time.time()
    login_info = state["login_context"]

    prompt = f"""
Generate a Markdown file named `spec.md` for the **Login Page** using the info below.

Format it like:
# Login Page Specification
## Description
## Input Fields
## Validation Rules

Do not include any additional sections beyond what is specified above.
Login Page Details:
{login_info}
"""
    llm = ChatOpenAI(api_key=api_key,model="gpt-4o-mini", temperature=0)
    response = llm.invoke([HumanMessage(content=prompt)])
    end_time = time.time()
    print(f"generate_spec took {end_time - start_time:.2f} seconds")
    return {**state, "spec_md": response.content.strip()}



