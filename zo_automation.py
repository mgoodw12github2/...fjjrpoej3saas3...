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

VALID_KEYS = {
    "name", "value", "path", "domain",
    "secure", "httpOnly", "expiry", "sameSite"
}

SAMESITE_MAP = {
    "strict": "Strict",
    "lax": "Lax",
    "none": "None",
    "no_restriction": "None",
    "unspecified": None,
    "": None,
}

def normalize_cookie(raw_cookie):
    cookie = {}

    # keep only keys Selenium understands
    for key in VALID_KEYS:
        if key in raw_cookie:
            cookie[key] = raw_cookie[key]

    # some exporters use expirationDate instead of expiry
    if "expiry" not in cookie and "expirationDate" in raw_cookie:
        cookie["expiry"] = raw_cookie["expirationDate"]

    # expiry must be int
    if "expiry" in cookie:
        try:
            cookie["expiry"] = int(cookie["expiry"])
        except Exception:
            cookie.pop("expiry", None)

    # normalize sameSite
    if "sameSite" in cookie:
        raw_value = cookie["sameSite"]

        if raw_value is None:
            cookie.pop("sameSite", None)
        else:
            mapped = SAMESITE_MAP.get(str(raw_value).strip().lower())
            if mapped is None:
                cookie.pop("sameSite", None)
            else:
                cookie["sameSite"] = mapped

    # browsers expect SameSite=None cookies to also be Secure
    if cookie.get("sameSite") == "None":
        cookie["secure"] = True

    return cookie

driver = webdriver.Chrome(options=chrome_options)

try:
    # first open parent domain
    driver.get("https://zo.computer")
    print("Visited zo.computer")

    with open("zo.cookies", "r") as file:
        cookies = json.load(file)

    added = 0
    skipped = 0

    for raw_cookie in cookies:
        try:
            cookie = normalize_cookie(raw_cookie)

            # require name/value
            if "name" not in cookie or "value" not in cookie:
                skipped += 1
                print(f"Skipped invalid cookie: {raw_cookie}")
                continue

            driver.add_cookie(cookie)
            added += 1
            print(f"Added cookie: {cookie.get('name')}")

        except Exception as e:
            skipped += 1
            print(f"Skipped cookie {raw_cookie.get('name')}: {e}")

    print(f"Loaded {added} cookies, skipped {skipped}")

    driver.get("https://dedinside.zo.computer")
    print("Visited dedinside.zo.computer")

    print("Waiting 50 seconds...")
    time.sleep(50)

    driver.save_screenshot("final.png")
    print("Screenshot saved as final.png")

finally:
    driver.quit()
