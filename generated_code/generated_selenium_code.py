from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def login(url, username, password):
    driver = webdriver.Chrome() # Replace with your webdriver initialization
    driver.get(url)

    # Wait for elements to be present
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//input[@type='submit']")))


    email_field = driver.find_element(By.ID, "email")
    password_field = driver.find_element(By.ID, "password")
    login_button = driver.find_element(By.XPATH, "//input[@type='submit']")

    email_field.send_keys(username)
    password_field.send_keys(password)
    login_button.click()

    # Add any necessary assertions or waits for post-login actions here.  For example, wait for redirection or check for a specific element on the next page.

    #driver.quit() #Uncomment if you want to close the browser after login