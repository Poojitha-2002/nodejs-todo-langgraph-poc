from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def login(url, username, password, home_page_url_segment):
    """
    Logs in to a website using Selenium.

    Args:
        url: The URL of the login page.
        username: The username.
        password: The password.
        home_page_url_segment:  A URL segment that indicates successful login (e.g., '/home').  Used to check if login was successful.

    Returns:
        True if login was successful, False otherwise.  Raises exceptions for other errors.
    """
    try:
        driver = webdriver.Chrome()  # Or other webdriver like Firefox, Edge etc.
        driver.get(url)

        # Explicit wait for the page to load (adjust timeout as needed)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))

        # Locate elements using IDs (best practice if available)
        email_field = driver.find_element(By.ID, "email")
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.XPATH, "//input[@type='submit' and @value='Login']") #Using XPath for submit button

        email_field.send_keys(username)
        password_field.send_keys(password)
        login_button.click()

        #Check for successful login by checking if the home page URL segment is present.
        WebDriverWait(driver, 10).until(EC.url_contains(home_page_url_segment)) #Wait for redirection to home page

        return True

    except TimeoutException:
        print("Timeout: Page did not load or login failed.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        raise  # Re-raise the exception to be handled by the calling function.
    finally:
        if 'driver' in locals():
            driver.quit()