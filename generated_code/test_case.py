import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from generated_code.generated_selenium_code import login # Assuming the login function is in this file


class TestLogin(unittest.TestCase):

    def test_successful_login(self):
        url = "http://127.0.0.1:4000/login"
        username = "manasakonduru11@gmail.com"
        password = "123456"
        home_page_url_segment = "http://127.0.0.1:4000/dashboard"
        driver = login(url, username, password, home_page_url_segment)
        self.assertTrue(driver is not False, "Login failed")
        self.assertIn(home_page_url_segment, driver.current_url)
        driver.quit()


    def test_invalid_password(self):
        url = "http://127.0.0.1:4000/login"
        username = "manasakonduru11@gmail.com"
        password = "wrong_password"
        home_page_url_segment = "http://127.0.0.1:4000/dashboard"
        result = login(url, username, password, home_page_url_segment)
        self.assertFalse(result, "Login should have failed with invalid password")


    def test_invalid_username(self):
        url = "http://127.0.0.1:4000/login"
        username = "invalid_username@example.com"
        password = "123456"
        home_page_url_segment = "http://127.0.0.1:4000/dashboard"
        result = login(url, username, password, home_page_url_segment)
        self.assertFalse(result, "Login should have failed with invalid username")


    def test_missing_username(self):
        url = "http://127.0.0.1:4000/login"
        username = ""
        password = "123456"
        home_page_url_segment = "http://127.0.0.1:4000/dashboard"
        result = login(url, username, password, home_page_url_segment)
        self.assertFalse(result, "Login should have failed with missing username")


    def test_missing_password(self):
        url = "http://127.0.0.1:4000/login"
        username = "manasakonduru11@gmail.com"
        password = ""
        home_page_url_segment = "http://127.0.0.1:4000/dashboard"
        result = login(url, username, password, home_page_url_segment)
        self.assertFalse(result, "Login should have failed with missing password")



if __name__ == '__main__':
    unittest.main()