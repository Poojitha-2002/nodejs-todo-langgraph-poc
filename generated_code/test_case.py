import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def login(driver, url, username, password):
    driver.get(url)
    
    WebDriverWait(driver, 10).until(EC.title_contains("Login"))
    
    email_field = driver.find_element(By.ID, "email")
    password_field = driver.find_element(By.ID, "password")
    login_button = driver.find_element(By.XPATH, "//input[@type='submit']")
    
    email_field.send_keys(username)
    password_field.send_keys(password)
    login_button.click()

class TestLogin(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.url = "http://example.com/login"  # Replace with the actual login URL

    def tearDown(self):
        self.driver.quit()

    def test_login_success(self):
        login(self.driver, self.url, "testuser", "testpassword")  # Replace with actual test credentials
        
        # Verify successful login
        WebDriverWait(self.driver, 10).until(EC.url_changes(self.url))
        self.assertIn("Dashboard", self.driver.title)  # Replace with the expected title after login
        self.assertTrue(self.driver.find_element(By.ID, "logout"))  # Replace with an actual element that appears after login

if __name__ == "__main__":
    unittest.main()