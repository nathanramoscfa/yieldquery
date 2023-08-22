import os
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from utils.drivers import setup_driver
from tqdm import tqdm


def navigate_to_page(driver, url):
    """
    :description: Navigate to the target page and accept the terms and conditions

    :param driver: Selenium driver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :param url: The url of the target page
    :type url: str
    :return: None
    :rtype: None
    """
    driver.get(url)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((
        By.CSS_SELECTOR,
        '#fx-body-wrapper > div:nth-child(1) > div > div '
        '> div:nth-child(1) > div > '
        'div.ReactVirtualized__Grid'
        '.ReactVirtualized__Table__Grid')))


def select_asset_classes(driver):
    """
    :description: Select the asset classes

    :param driver: Selenium driver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :return: None
    :rtype: None
    """
    dropdown_downarrow = driver.find_element(By.CSS_SELECTOR, '#assetClassDropdown > div.dropdown-display > '
                                                              'span.npe-icon-down-arrow')
    dropdown_downarrow.click()

    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                '#assetClassDropdown > div.dropdown-list > div > '
                                                                'div:nth-child(4) > div:nth-child(1) > a > '
                                                                'span'))).click()
    time.sleep(1)
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                '#assetClassDropdown > div.dropdown-list > div > '
                                                                'div:nth-child(5) > div:nth-child(1) > a > '
                                                                'span'))).click()
    time.sleep(1)
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                '#assetClassDropdown > div.dropdown-list > div > '
                                                                'div:nth-child(6) > div:nth-child(1) > a > '
                                                                'span'))).click()
    time.sleep(1)
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                '#assetClassDropdown > div.dropdown-list > div > '
                                                                'div:nth-child(7) > div:nth-child(1) > a > '
                                                                'span'))).click()
    time.sleep(1)
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#assetClassDropdown > div.dropdown-display.clicked'))).click()
    time.sleep(1)


def get_links(driver):
    """
    :description: Get the links to the ETF pages

    :param driver: Selenium driver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :return: The links to the ETF pages
    :rtype: list
    """
    # Initialize the set for unique links
    links = set()

    # Initial height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Gather the links
        link_elements = driver.find_elements(By.CSS_SELECTOR, 'div.ReactVirtualized__Grid'
                                                              '.ReactVirtualized__Table__Grid a')
        for elem in link_elements:
            link = elem.get_attribute('href')
            if link is not None and "content" not in link:
                links.add(link)

        # Scroll down by chunk
        driver.execute_script("window.scrollBy(0, 800);")  # Adjust this value according to your needs
        time.sleep(2)  # Adjust this value according to your internet speed or webpage's response time

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:  # If heights are the same it will exit the function
            break
        last_height = new_height

    return list(links)  # Return the links as a list


def extract_etf_info(driver, url):
    """
    :description: Extract the ETF info from the page

    :param driver: Selenium driver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :param url: The url of the target page
    :type url: str
    :return: The ETF info
    :rtype: dict
    """
    # Navigate to the url
    driver.get(url)

    # Wait until the elements are present
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#fund-name > div')))

    # Try to extract yield_to_maturity, if it's not available print the ticker and skip to next link
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#ytm-gross')))
        yield_to_maturity = driver.find_element(By.CSS_SELECTOR, '#ytm-gross').text
    except TimeoutException:
        return None  # Returns None if yield_to_maturity is not present, which leads to skipping this ETF

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#ytm-as-of-date > span')))

    # Extract the info
    name = driver.find_element(By.CSS_SELECTOR, '#fund-name > div').text
    as_of_date = driver.find_element(By.CSS_SELECTOR, '#ytm-as-of-date > span').text
    ticker = driver.find_element(By.CSS_SELECTOR, '#ticker').text  # Extract the ticker from the page

    return {"Ticker": ticker, "Name": name, "Yield to Maturity": yield_to_maturity, "As of Date": as_of_date}


def get_etf_data(driver, links):
    """
    :description: Get the ETF data

    :param driver: Selenium driver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :param links: The links to the ETF pages
    :type links: list
    :return: The ETF data
    :rtype: pd.DataFrame
    """
    # Get data for all ETFs
    data = []
    for link in tqdm(links):
        etf_data = extract_etf_info(driver, link)

        # Only add the etf_data to the list if it's not None
        if etf_data is not None:
            data.append(etf_data)

    # Convert data list to a pandas DataFrame
    df = pd.DataFrame(data)

    # Set 'ticker' as index
    df.set_index('Ticker', inplace=True)

    # Convert 'yield_to_maturity' to a numeric value
    df['Yield to Maturity'] = df['Yield to Maturity'].str.rstrip('%').astype('float') / 100.0

    # Convert 'as_of_date' to datetime
    df['As of Date'] = pd.to_datetime(df['As of Date'], format="%m/%d/%Y")
    df['As of Date'] = df['As of Date'].dt.strftime('%m-%d-%Y')

    return df


def jpmorgan_bot(return_df=False, headless=True):
    """
    :description: Run the JPMorgan ETF yield bot

    :param return_df: Whether to return the DataFrame
    :type return_df: bool
    :param headless: Whether to run the bot in headless mode
    :type headless: bool
    :return: The ETF data
    :rtype: pd.DataFrame
    """
    print('Downloading JPMorgan ETF yield data...')
    url = 'https://am.jpmorgan.com/us/en/asset-management/adv/products/fund-explorer/etf'
    driver = setup_driver(headless)
    navigate_to_page(driver, url)
    select_asset_classes(driver)
    links = get_links(driver)
    df = get_etf_data(driver, links)

    # Get the absolute path of the project's root directory
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Change the working directory to the project's root directory
    os.chdir(project_dir)

    # Construct the paths to your CSV files relative to the project's root directory
    csv_path = os.path.join(project_dir, 'data', 'jpmorgan.csv')

    print('Saving JPMorgan ETF yield data to CSV file...')
    df.to_csv(csv_path)
    print('Done!')
    if return_df:
        return df
