import os
import json
import time
import logging
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from schemas.state_schemas import AppState  # Make sure this exists

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# === 1. AUTH CHECK FUNCTION ===
def check_authentication_required_with_llm(state: AppState) -> dict:
    """
    Uses Gemini via LangChain to check if authentication is required
    based on the specification file content.
    """
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        logging.error("GEMINI_API_KEY not set in .env file.")
        raise ValueError("GEMINI_API_KEY not set in .env file")

    os.environ["GOOGLE_API_KEY"] = gemini_api_key

    spec_text = state.get("spec_md", "")
    if not spec_text.strip():
        logging.warning(
            "Empty spec provided. Cannot check for authentication requirement."
        )
        return {"authentication_required": False}

    logging.info("Sending spec to Gemini to check for authentication requirement...")

    system_message = SystemMessage(
        content="You are an expert software assistant. Respond only with True or False."
    )

    human_message = HumanMessage(
        content=(
            "Given the following specification document, your task is to decide whether the application described explicitly requires user authentication or login.\n\n"
            "Only respond with:\n"
            "- `True` → if the specification **explicitly mentions** terms like `login`, `authentication`, `sign in`, `session`, `user must be logged in`, or similar.\n"
            "- `False` → if there is **no explicit** mention of such requirements. Do not infer based on UI elements like 'Logout', 'My Account', etc.\n\n"
            "Respond with only one word: `True` or `False`.\n\n"
            f"### Specification:\n{spec_text}"
        )
    )

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    try:
        result = llm.invoke([system_message, human_message])
        answer = result.content.strip().lower()
        print(f"Gemini response: {answer}")
        if "true" in answer:
            return {"authentication_required": True}
        elif "false" in answer:
            return {"authentication_required": False}
        else:
            logging.warning(f"Unexpected response from Gemini: {answer}")
            return {"authentication_required": False}
    except Exception as e:
        logging.error(f"LLM error: {e}")
        return {"authentication_required": False}


# === 2. TOKEN LOADER (OPTIONAL USE) ===
def load_token_and_cookies(token_path: str = "token/token.json") -> dict:
    """
    Load access_token, csrftoken, and sessionid from a JSON file.
    """
    try:
        with open(token_path, "r") as file:
            data = json.load(file)
            print("Tokens loaded successfully.")
            return {
                "access_token": data.get("access_token", ""),
                "csrftoken": data.get("csrftoken", ""),
                "sessionid": data.get("sessionid", ""),
            }
    except Exception as e:
        logging.error(f"Failed to load token and cookies: {e}")
        return {"access_token": "", "csrftoken": "", "sessionid": ""}


# === 3. SELENIUM: AUTHENTICATED PAGE ACCESS ===
def open_authenticated_page_with_selenium(
    cookies: dict, base_url: str, target_url: str
) -> webdriver.Chrome:
    """
    Launches a Chrome browser, injects session cookies, and navigates to the target URL.
    Accepts base_url and target_url as parameters.
    Returns the Selenium WebDriver instance.
    """
    # Set up Selenium options
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)

    # Step 1: Visit base domain so cookies can be set
    driver.get(base_url)

    # Extract domain for cookie setting
    domain = base_url.split("//")[-1].split("/")[0]

    # Step 2: Set cookies for the domain
    for name, value in cookies.items():
        driver.add_cookie({"name": name, "value": value})

    # Step 3: Navigate to the protected page
    driver.get(target_url)

    # Optional delay to visually verify
    time.sleep(10)

    return driver


def handle_url_access(state: AppState) -> dict:
    import pickle

    base_url = state.get("specific_url", "")
    redirect_url = state.get("redirect_url", "")
    if not base_url:
        logging.error("No URL found in state.")
        return state

    # Step 1: Use Gemini to check if authentication is required
    auth_result = state["authentication_required"]

    if auth_result:
        logging.info("Authentication required. Using token-based login...")

        # Step 2: Load tokens and login via Selenium with cookies
        cookies = load_token_and_cookies()
        driver = open_authenticated_page_with_selenium(cookies, redirect_url, base_url)

        if driver:
            state["driver_path"] = driver

            # === Save driver session to pickle file ===
            try:
                session_data = {
                    "cookies": driver.get_cookies(),
                    "current_url": driver.current_url,
                }
                with open("driver_session.pkl", "wb") as f:
                    pickle.dump(
                        {"cookies": driver.get_cookies(), "url": driver.current_url},
                        f,
                    )

                logging.info("Driver session saved to 'driver_session.pkl'")
            except Exception as e:
                logging.error(f"Failed to save driver session: {e}")

        else:
            logging.warning("Driver not initialized after auth.")
            state["driver_path"] = None

        logging.info("Page loaded successfully with authentication.")
        return state

    else:
        logging.info("Authentication not required. Defer page loading to next node.")
        state["driver_path"] = None
        return state


# def handle_url_access(state: AppState) -> dict:
#     base_url = state.get("specific_url", "")
#     redirect_url = state.get("redirect_url", "")
#     if not base_url:
#         logging.error("No URL found in state.")
#         return state

#     # Step 1: Use Gemini to check if authentication is required
#     auth_result = state["authentication_required"]
#     # state.update(auth_result)

#     if auth_result:
#         logging.info("Authentication required. Using token-based login...")

#         # Step 2: Load tokens and login via Selenium with cookies
#         cookies = load_token_and_cookies()
#         driver = open_authenticated_page_with_selenium(cookies, redirect_url, base_url)

#         if driver:
#             state["driver_path"] = (
#                 driver  # You can rename this to just "driver" if preferred
#             )
#         else:
#             logging.warning("Driver not initialized after auth.")
#             state["driver_path"] = None
#         # print("state", state)
#         logging.info("Page loaded successfully with authentication.")
#         return state
#     else:
#         logging.info("Authentication not required. Defer page loading to next node.")
#         state["driver_path"] = None
#         # print("state", state)
#         return state


# if __name__ == "__main__":
#     state = AppState(
#         spec_md="Paste your UI spec content here",
#         specific_url="http://127.0.0.1:8000/polls/list/user/",
#     )
#     handle_url_access(state)
