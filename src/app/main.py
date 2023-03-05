import os
import sys
from time import sleep
from enum import Enum
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager


class BrowserOptions(Enum):
    FIREFOX = "FIREFOX"
    CHROME = "CHROME"

    @classmethod
    def validate(cls, browser_option):
        return BrowserOptions[browser_option.upper()]  if browser_option.upper() in cls._member_names_ else None

def validate_browser_option(browser_option):
    return BrowserOptions.validate(browser_option)

def get_webdriver(browser_option):
    driver = None
    if browser_option is BrowserOptions.CHROME:
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    elif browser_option is BrowserOptions.FIREFOX:
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
    return driver

def load_script(target):
    f = open(target)
    script = f.read()
    f.close()
    return script

def redirect_event_condition(driver):
    url_snapshot = driver.current_url
    event_condition = lambda driver: driver.current_url != url_snapshot
    return event_condition

def wait_until_button_press_event_condition():
    event_condition = lambda driver: driver.execute_script("return window.buttonSentinel === true;")
    return event_condition

def page_load_event_condition():
    event_condition = lambda driver: driver.execute_script("return document.readyState == 'complete';")
    return event_condition

def event(event_condition, target_script=None, timeout=10):
    try:
        if target_script is not None:
            script = load_script(target_script)
            driver.execute_script(script)
        WebDriverWait(driver, timeout).until(event_condition)
        print("Event detected")
    except TimeoutException:
        print("Event not detected.")

def bootstrap(driver, root_url):
    driver.get(root_url)
    event(wait_until_button_press_event_condition(), "../webopticjs/waitUntilButtonPress.js", 20)
    event(redirect_event_condition(driver), "../webopticjs/goToGoogle.js")
    event(page_load_event_condition())
    event(wait_until_button_press_event_condition(), "../webopticjs/waitUntilButtonPress.js", 20)
    event(redirect_event_condition(driver), "../webopticjs/goToStackoverflow.js")
    event(page_load_event_condition())
    event(wait_until_button_press_event_condition(), "../webopticjs/waitUntilButtonPress.js", 20)
    driver.close()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Incorrect number of arguments.")
        sys.exit(1)
    
    browser_option = validate_browser_option(sys.argv[1])
    if browser_option is None:
        print("Not a valid browser option.")
        sys.exit(1)
        
    # we don't validate the root_url because
    #   the browser will do that for us
    root_url = sys.argv[2]

    os.environ['WDM_LOCAL'] = '1'
    driver = get_webdriver(browser_option)
    if driver is None:
        print("Error creating webdriver.")
        sys.exit(1)

    bootstrap(driver, root_url)
