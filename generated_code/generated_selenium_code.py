from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def login(url, username, password):
    driver = webdriver.Chrome("<selenium.webdriver.chrome.webdriver.WebDriver (session='dc201cf5cc6078c4fced8e76a48c48e7')>")
    driver.get(url)
    
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))
    
    email_field = driver.find_element(By.ID, "email")
    password_field = driver.find_element(By.ID, "password")
    login_button = driver.find_element(By.XPATH, "//input[@type='submit']")
    
    email_field.send_keys(username)
    password_field.send_keys(password)
    login_button.click()