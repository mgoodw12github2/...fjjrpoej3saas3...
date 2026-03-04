from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import json

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.binary_location = "/usr/bin/chromium-browser"

driver = webdriver.Chrome(options=chrome_options)

try:
    # Visit zo.computer first (no redirect)
    driver.get("https://zo.computer")
    print("Visited zo.computer")

    # Load cookies
    with open("zo.cookies", 'r') as file:
        cookies = json.load(file)

    for cookie in cookies:
        driver.add_cookie(cookie)
        print(f"Added cookie: {cookie.get('name')}")

    print(f"Loaded {len(cookies)} cookies")

    # Now visit dedinside.zo.computer
    driver.get("https://dedinside.zo.computer")
    print("Visited dedinside.zo.computer")
    
    # Wait 20 seconds
    print("Waiting 20 seconds...")
    time.sleep(20)
    
    # Take final screenshot
    driver.save_screenshot("final.png")
    print("Screenshot saved as final.png")

finally:
    driver.quit()
