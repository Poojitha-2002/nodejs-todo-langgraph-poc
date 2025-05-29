import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def login(url, username, password):
    driver = webdriver.Chrome()
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "form")))

        email_field = driver.find_element(By.ID, "email")
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.XPATH, "//form/div[3]/input[@type='submit']")

        email_field.send_keys(username)
        password_field.send_keys(password)
        login_button.click()
        return driver
    except TimeoutException:
        return None


class TestLogin(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()

    def test_successful_login(self):
        driver = login("https://www.example.com", "testuser", "password123") # Replace with your login URL, username, and password
        if driver:
            try:
                WebDriverWait(driver, 10).until(EC.url_contains("/dashboard")) #Example assertion, adjust as needed
                self.assertTrue("dashboard" in driver.current_url)
            except TimeoutException:
                self.fail("Login failed: Did not redirect to dashboard")
            finally:
                driver.quit()
        else:
            self.fail("Login failed: Timeout")


    def tearDown(self):
        if 'driver' in locals() and self.driver:
            self.driver.quit()

if __name__ == "__main__":
    unittest.main()