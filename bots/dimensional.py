import os
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
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
    try:
        # Try to find and click the "A Financial Advisor" button
        # advisor_button_selector = 'body > div.main > div > div > div > div.public-global-splash-content > ' \
        #                           'div.public-global-splash-right > div > ul > li:nth-child(1) > button'
        advisor_button_selector = 'body > div.main > div > div > div > div.public-global-splash-content > div > ' \
                                  'div.public-global-splash-right > div > ul > li:nth-child(1) > button > div'
        button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, advisor_button_selector)))
        button.click()
        # Wait for the redirection to complete
        time.sleep(5)

        # Try to find and click the "I have read and agree to the terms" checkbox
        checkbox_selector = '#I\\ have\\ read\\ and\\ agree\\ to\\ the\\ terms\\.'
        checkbox = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, checkbox_selector)))
        checkbox.click()

        # Try to find and click the "Accept and Continue" button
        accept_and_continue_button_selector = 'body > div.ReactModalPortal > div > div > ' \
                                              'div.audience-sort-professional-affirmation-terms-wrapper.audience-sort' \
                                              '-professional-affirmation-terms-wrapper-nav > div > ' \
                                              'div.audience-sort-professional-affirmation-check-area > button'
        accept_button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, accept_and_continue_button_selector)))
        accept_button.click()

        # Add delay and then redirect back to the target page
        time.sleep(10)
        driver.get(url)

    except NoSuchElementException:
        # Ignore if the elements are not found
        pass

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((
        By.CSS_SELECTOR,
        '#funds > div > div.tools-table.tools-fund-listing-table.tools-sticky-header > div.tools-table-body > div'
    )))


def get_links(driver):
    """
    :description: Get the links to the ETFs

    :param driver: Selenium driver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :return: List of links to the ETFs
    :rtype: list
    """
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((
        By.CSS_SELECTOR,
        '#funds div.tools-fund-listing-table-col-fund-name.tools-fund-listing-table-col-fund-name-public a'
    )))
    links = driver.find_elements(By.CSS_SELECTOR,
                                 '#funds div.tools-fund-listing-table-col-fund-name.tools-fund-listing-table-col-fund'
                                 '-name-public a')
    return [link.get_attribute('href') for link in links]


def extract_etf_info(driver, url):
    """
    :description: Extract the ETF info from the page

    :param driver: Selenium driver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :param url: The url of the target page
    :return: The ETF info
    :rtype: dict
    """
    # Navigate to the url
    driver.get(url)

    # Try to extract yield_to_maturity, if it's not available print the ticker and skip to next link
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                        '#funds > div > span > div > div > '
                                                                        'div.tools-compare-content > '
                                                                        'div.tools-tracked-scroll.tools-compare'
                                                                        '-lenses > div > div:nth-child(13) > div > '
                                                                        'div.tools-lens-characteristics.tools-lens'
                                                                        '-characteristics-fixed-income > div > '
                                                                        'div:nth-child(6) > '
                                                                        'div.tools-lens-type-characteristics-title')))
        yield_to_maturity = driver.find_element(By.CSS_SELECTOR,
                                                '#funds > div > span > div > div > div.tools-compare-content > '
                                                'div.tools-tracked-scroll.tools-compare-lenses > div > div:nth-child('
                                                '13) > div > '
                                                'div.tools-lens-characteristics.tools-lens-characteristics-fixed'
                                                '-income > div > div:nth-child(6) > '
                                                'div.tools-lens-type-characteristics-title').text
    except TimeoutException:
        return None  # Returns None if yield_to_maturity is not present, which leads to skipping this ETF

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                    '#funds > div > span > div > div > '
                                                                    'div.tools-compare-content > '
                                                                    'div.tools-tracked-scroll.tools-compare-lenses > '
                                                                    'div > div:nth-child(2) > section > div > div')))

    # Extract the info
    name = driver.find_element(By.CSS_SELECTOR, '#modal-funddetails-label').text
    as_of_date = driver.find_element(By.CSS_SELECTOR,
                                     '#funds > div > span > div > div > div.tools-compare-content > '
                                     'div.tools-tracked-scroll.tools-compare-lenses > div > div:nth-child(12) > '
                                     'section > div > div').text
    ticker = driver.find_element(By.CSS_SELECTOR,
                                 '#funds > div > span > div > div > div.tools-compare-content > '
                                 'div.tools-compare-content-header > div.tools-compare-content-header-title > '
                                 'div').text  # Extract the ticker from the page

    return {"Ticker": ticker, "Name": name, "Yield to Maturity": yield_to_maturity, "As of Date": as_of_date}


def get_etf_data(driver, links):
    """
    :description: Get the ETF data

    :param driver: Selenium driver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :param links: List of links to the ETFs
    :type links: list
    :return: ETF data
    :rtype: pd.DataFrame
    """
    # Get data for all ETFs
    data = []
    for link in tqdm(links):
        etf_data = extract_etf_info(driver, link)

        # Only add the etf_data to the list if it's not None and if Yield to Maturity is not '—'
        if etf_data is not None and etf_data['Yield to Maturity'] != '—':
            data.append(etf_data)

        time.sleep(3)

    # Convert data list to a pandas DataFrame
    df = pd.DataFrame(data)

    # Set 'ticker' as index
    df.set_index('Ticker', inplace=True)

    # Convert 'yield_to_maturity' to a numeric value
    df['Yield to Maturity'] = df['Yield to Maturity'].str.rstrip('%').astype('float') / 100.0

    # Convert 'as_of_date' to datetime
    df['As of Date'] = df['As of Date'].str.replace('as of ', '', case=False)
    df['As of Date'] = pd.to_datetime(df['As of Date'], format="%m/%d/%Y")
    df['As of Date'] = df['As of Date'].dt.strftime('%m-%d-%Y')

    return df


def dimensional_bot(return_df=False, headless=True):
    """
    :description: Run the Dimensional ETF yield bot

    :param return_df: return the DataFrame if True, default is False
    :type return_df: bool, optional
    :param headless: run the bot in headless mode if True, default is True
    :type headless: bool, optional
    :return: Dimensional ETF yield data
    :rtype: pd.DataFrame
    """
    print('Downloading Dimensional ETF yield data...')
    url = 'https://www.dimensional.com/us-en/funds?ac=fixed-income&ft=etf'
    driver = setup_driver(headless)
    navigate_to_page(driver, url)
    links = get_links(driver)
    df = get_etf_data(driver, links)

    # Get the absolute path of the project's root directory
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Change the working directory to the project's root directory
    os.chdir(project_dir)

    # Construct the path to your CSV file relative to the project's root directory
    csv_path = os.path.join(project_dir, 'data', 'dimensional.csv')

    print('Saving Dimensional ETF yield data to CSV file...')
    df.to_csv(csv_path)
    print('Done!')
    if return_df:
        return df
