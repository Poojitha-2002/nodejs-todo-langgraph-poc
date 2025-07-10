from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from schemas.state_schemas import AppState
import time


def load_login_page(state: AppState):
    print("Initializing Selenium WebDriver...")

    driver = state.get("driver_path")
    url = state.get("specific_url", "")

    driver.get(url)
    time.sleep(2)

    # else:
    #     print(
    #         "Reusing existing authenticated driver to load the page again (if needed)..."
    #     )
    #     # In your case, the authenticated page was already loaded in the previous node
        # So you can either reload the URL or assume it's already on that page

    try:
        # Save screenshot of the current loaded page
        screenshot_path = "page_loaded.png"
        driver.save_screenshot(screenshot_path)
        html_body = driver.page_source
        title = driver.title

        print(f"\n✅ Page loaded successfully! Screenshot saved: {screenshot_path}")
        return {
            "page_html": html_body,
            "image_path": screenshot_path,
            "title": title,
            "driver": driver,  # return for potential reuse
        }

    except Exception as e:
        print(f"\n❌ Error loading page: {str(e)}")
        if driver:
            driver.quit()
        return {}


# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from schemas.state_schemas import AppState
# import time

# def load_login_page(state: AppState):
#     print("Initializing Selenium WebDriver...")
#     url = state["specific_url"]

#     # Set up Chrome options
#     chrome_options = Options()
#     chrome_options.add_argument("--headless")  # Run without opening browser window
#     chrome_options.add_argument("--no-sandbox")
#     chrome_options.add_argument("--disable-dev-shm-usage")

#     try:
#         # Automatic driver management using webdriver-manager
#         service = Service(ChromeDriverManager().install())
#         driver = webdriver.Chrome(service=service, options=chrome_options)

#         print(f"Loading URL: {url}")
#         driver.get(url)
#         time.sleep(2)  # Wait for page to load

#         # Get page details
#         page_title = driver.title
#         html_body = driver.page_source
#         screenshot_path = "page_loaded.png"
#         driver.save_screenshot(screenshot_path)

#         print(f"\nPage loaded successfully! saved as: {screenshot_path}")
#         print("Final page loaded in page load, title:", driver.title)
#         print("Screenshot saved in page load:", screenshot_path)
#         print("HTML length in page load:", len(driver.page_source))

#         return {
#             "page_html": html_body,
#             "image_path": screenshot_path,
#             "title": page_title,
#             "driver_path": driver  # Returning driver object for subsequent nodes
#         }
#     except Exception as e:
#         print(f"\nError loading page: {str(e)}")
#         if 'driver' in locals():
#             driver.quit()
#         return None

# Example usage
# if __name__ == "__main__":
#     specific_url = "http://127.0.0.1:4000/login"
#     print("Starting Node 1 - Page Loader")
#     print("="*50)

#     page_data = load_login_page(specific_url)

#     if page_data:
#         print("\nNode 1 executed successfully!")
#         print("You can now proceed to Node 2 with these outputs:")
#         print(f"- Page title: {page_data['title']}")
#         print(f"- HTML body length: {len(page_data['page_html'])} characters")
#         print(f"- Screenshot: {page_data['screenshot']}")
#         print(f"- Driver object retained for next steps")
#     else:
#         print("\nNode 1 failed. Please check the error message above.")
