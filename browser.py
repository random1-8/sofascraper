import config
import json
import os.path
import time
from seleniumwire import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Using selenium-wire extension to add custom headers, shhhh... we don't want to get caught by Cloudflare bot detection.
# I have to delete headers first because HTTP does allow duplicate headers
def interceptor(request):
    del request.headers['accept']
    del request.headers['accept-language']
    del request.headers['cache-control']
    del request.headers['origin']
    del request.headers['referer']
    del request.headers['sec-ch-ua']
    del request.headers['sec-ch-ua-mobile']
    del request.headers['sec-ch-ua-platform']
    del request.headers['sec-fetch-dest']
    del request.headers['sec-fetch-mode']
    del request.headers['sec-fetch-site']
    del request.headers['sec-fetch-user']
    del request.headers['upgrade-insecure-requests']
    del request.headers['user-agent']

    request.headers['accept'] = '*/*'
    request.headers['accept-language'] = 'en-US,en;q=0.9'
    request.headers['cache-control'] = 'max-age=0'
    request.headers['origin'] = 'https://www.sofascore.com/'
    request.headers['referer'] = 'https://www.sofascore.com/'
    request.headers['sec-ch-ua'] = '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"'
    request.headers['sec-ch-ua-mobile'] = '?0'
    request.headers['sec-ch-ua-platform'] = '"Windows"'
    request.headers['sec-fetch-dest'] = 'empty'
    request.headers['sec-fetch-mode'] = 'cors'
    request.headers['sec-fetch-site'] = 'same-site'
    request.headers['user-agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'

def create_browser(path=None):
    # Setup chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless") # Ensure GUI is off
    chrome_options.add_argument("--no-sandbox")

    # Set path to chromedriver as per your configuration
    # By default is where my chromedriver is because fuck you.
    if not path:
        homedir = os.path.expanduser("~")
        path = f"{homedir}/chromedriver/stable/chromedriver"
    webdriver_service = Service(path)

    # Choose Chrome Browser
    browser = webdriver.Chrome(service=webdriver_service, options=chrome_options)

    # Custom headers
    browser.request_interceptor = interceptor

    return browser



# We're going to repeat this operation a lot: go to url -> parse the response -> return a dict
# to_wait is the number of seconds before requesting another JSON (1 second by default). But why?
# Because doing a lot of requests in short spaces of time will flag our IP as a scraper and we'll get banned.
# Been there, done that.
def extract_json(url, to_wait = 0.1):
    current = time.time()
    if config.last_get:
        elapsed = round(current - config.last_get, 1)
        if elapsed < 1:
            print(f"Waiting {to_wait} seconds before another request...")
            time.sleep(to_wait)
        else:
            print(f"{elapsed} seconds since last request.")

    try:
        print(f"URL: {url}")
        config.driver.get(url)
        config.last_get = time.time()
        response = config.driver.requests[0].response # if no requests this will crash
        if response and response.status_code == 200:
            print("200: OK!")
            ugly_json = config.driver.find_element(By.TAG_NAME, "pre").text
        elif response and response.status_code == 403:
            print("You are banned :c")
            raise Exception
        elif response and response.status_code != 200:
            print(f"Response different than expected. Status code: {response.status_code}")
            raise Exception
        elif not response:
            print("No response from server")
            raise Exception
    except NoSuchElementException as err:
        print("Element 'pre' was not found in the DOM.")
        return {}

    return json.loads(ugly_json)