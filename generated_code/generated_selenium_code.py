from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def login(url, username, password, home_page_url_segment):
    driver = webdriver.Chrome()
    driver.get(url)
    try:
        email_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))
        password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
        submit_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']")))

        email_field.send_keys(username)
        password_field.send_keys(password)
        submit_button.click()

        WebDriverWait(driver, 10).until(EC.url_contains(home_page_url_segment))

    except (TimeoutException, NoSuchElementException) as e:
        print(f"Login failed: {e}")
    finally:
        driver.quit()