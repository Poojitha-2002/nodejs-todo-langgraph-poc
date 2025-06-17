from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def login(url, username, password, home_page_url_segment):
    with webdriver.Chrome() as driver:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))
        driver.find_element(By.ID, "email").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, "//input[@type='submit']").click()
        # Assertion to check if redirection to home page happened.  This requires knowledge of the home page URL structure.
        #  Replace with actual assertion based on your application's behavior.
        # assert home_page_url_segment in driver.current_url