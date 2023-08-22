from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def webdriver_path():
    """
    Get the path to the webdriver

    :return: The path to the webdriver
    :rtype: str
    """
    return ChromeDriverManager().install()


def setup_driver(headless=True):
    """
    Set up the webdriver

    :param headless: Whether to run the webdriver in headless mode
    :type headless: bool
    :return: The webdriver
    :rtype: selenium.webdriver.chrome.webdriver.WebDriver
    """
    options = Options()
    if headless:
        options.add_argument('--headless')
        options.add_argument('--window-size=1920x1080')

    # Set user-agent
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/89.0.4389.82 Safari/537.36")

    driver = webdriver.Chrome(service=Service(webdriver_path()), options=options)
    return driver
