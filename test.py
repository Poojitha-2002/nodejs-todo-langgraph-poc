from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# Your local Django URL
url = "http://127.0.0.1:8000/polls/list/user/"

# Your Django session cookies
cookies = {
    "csrftoken": "hJUJdNzsUKNxrYpwtr5p4viWSN7O0kSj",
    "sessionid": "6grjrsbwqtq16ms7tdfdoycbl4l0x5xs",
}

# Set up Selenium browser
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# Step 1: Load base URL to set domain (must visit once before adding cookies)
driver.get("http://127.0.0.1:8000/")

# Step 2: Add each cookie
for name, value in cookies.items():
    driver.add_cookie({"name": name, "value": value, "domain": "127.0.0.1"})

# Step 3: Visit the protected page
driver.get(url)

# Wait to see the result
time.sleep(10)

# Close the browser
driver.quit()
