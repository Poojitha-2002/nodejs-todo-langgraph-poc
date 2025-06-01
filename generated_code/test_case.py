import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def login(url, username, password):
    driver = webdriver.Chrome()
    driver.get(url)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@type='submit']")))

    email_field = driver.find_element(By.ID, "email")
    password_field = driver.find_element(By.ID, "password")
    login_button = driver.find_element(By.XPATH, "//input[@type='submit']")

    email_field.send_keys(username)
    password_field.send_keys(password)
    login_button.click()
    return driver


class TestLogin(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome()

    def test_successful_login(self):
        driver = login("http://127.0.0.1:4000/login", "manasakonduru11@gmail.com", "123456")
        try:
            WebDriverWait(driver, 10).until(EC.url_contains("/dashboard"))
            self.assertTrue("/dashboard" in driver.current_url)
        except:
            self.fail("Login failed")
        finally:
            driver.quit()

    def tearDown(self):
        self.driver.quit()

if __name__ == "__main__":
    unittest.main()