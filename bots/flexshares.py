import os
import time
import random
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from utils.drivers import setup_driver
from tqdm import tqdm


def reject_cookies(driver):
    """
    :description: Reject the cookies

    :param driver: Selenium driver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :return: None
    :rtype: None
    """
    try:
        cookie_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#onetrust-reject-all-handler')))
        cookie_button.click()
    except TimeoutException:
        pass


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
    time.sleep(random.randint(2, 10))  # delay before accessing the URL
    driver.get(url)

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((
        By.CSS_SELECTOR,
        '#container-8d26eb3d06 > div > div.fund-performance.aem-GridColumn.aem-GridColumn--default--12 > div > div > '
        'div.table-responsive > table'
    )))
    reject_cookies(driver)
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((
        By.CSS_SELECTOR,
        '#container-8d26eb3d06 > div > div.fund-performance.aem-GridColumn.aem-GridColumn--default--12 > div > div > '
        'div.cmp-fund-performance__filters > div.d-md-flex.d-none.cmp-fund-performance__filters__gap-40 > '
        'div:nth-child(1) > div:nth-child(2) > div > fieldset > div > div:nth-child(3) > label > span'
    ))).click()
    time.sleep(random.randint(2, 10))  # delay after accessing the URL


def get_links(driver):
    """
    :description: Get the links to the ETF pages

    :param driver: Selenium driver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :return: The links to the ETF pages
    :rtype: list
    """
    link_elements = driver.find_elements(By.CSS_SELECTOR,
                                         '#container-8d26eb3d06 > div > '
                                         'div.fund-performance.aem-GridColumn.aem-GridColumn--default--12 > div > div '
                                         '> div.table-responsive > table > tbody > tr > td:nth-child(1) > div > a')
    links = [elem.get_attribute('href') for elem in link_elements]
    return links


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
    data = []

    for link in tqdm(links):
        driver.get(link)
        time.sleep(3)  # wait for the page to load completely

        # Extract the ticker and name
        ticker = driver.find_element(By.CSS_SELECTOR, 'div.cmp-fund-intro > h1').text
        name = driver.find_element(By.CSS_SELECTOR, 'div.cmp-fund-intro__desc-wrapper > h2').text
        as_of_date = driver.find_element(By.CSS_SELECTOR, '#quick-stats > div > div > div > div > p').text

        table_elements = driver.find_elements(By.CSS_SELECTOR,
                                              '.cmp-quick-stats__item')

        data_row = {"TICKER": ticker, "NAME": name, "AS OF DATE": as_of_date}  # start the row with the ticker and name
        for element in table_elements:
            label = element.find_element(By.CSS_SELECTOR, '.cmp-quick-stats__label > p').text
            value = element.find_element(By.CSS_SELECTOR, '.cmp-quick-stats__value').text
            data_row[label] = value

        data.append(data_row)

    df = pd.DataFrame(data)
    df.set_index('TICKER', inplace=True)

    # Convert to a numeric value
    df['WEIGHTED AVG YIELD TO MATURITY'] = df['WEIGHTED AVG YIELD TO MATURITY'].str.rstrip('%').astype('float') / 100.0
    df['WEIGHTED AVG YIELD TO WORST'] = df['WEIGHTED AVG YIELD TO WORST'].str.rstrip('%').astype('float') / 100.0
    df['WEIGHTED AVG NOMINAL YIELD'] = df['WEIGHTED AVG NOMINAL YIELD'].str.rstrip('%').astype('float') / 100.0
    df['WEIGHTED AVG COUPON'] = df['WEIGHTED AVG COUPON'].str.rstrip('%').astype('float') / 100.0

    # Remove the 'as of ' prefix from the As of Date column
    df['AS OF DATE'] = df['AS OF DATE'].str.replace('AS OF ', '')

    # Convert the As of Date column to datetime format
    df['AS OF DATE'] = pd.to_datetime(df['AS OF DATE'], format='%m/%d/%Y')

    # Convert the datetime format to MM-DD-YYYY
    df['AS OF DATE'] = df['AS OF DATE'].dt.strftime('%m-%d-%Y')

    return df


def flexshares_bot(return_df=False, headless=True):
    """
    :description: Run the FlexShares ETF yield bot

    :param return_df: return the DataFrame if True, default is False
    :type return_df: bool, optional
    :param headless: run the bot in headless mode if True, default is True
    :type headless: bool, optional
    :return: FlexShares ETF yield data
    :rtype: pd.DataFrame
    """
    print('Downloading FlexShares ETF yield data...')
    url = 'https://www.flexshares.com/us/en/individual/funds'
    driver = setup_driver(headless)
    navigate_to_page(driver, url)
    links = get_links(driver)
    df = get_etf_data(driver, links)

    # Get the absolute path of the project's root directory
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Change the working directory to the project's root directory
    os.chdir(project_dir)

    # Construct the path to your CSV file relative to the project's root directory
    csv_path = os.path.join('data', 'flexshares.csv')

    print('Saving FlexShares ETF yield data to CSV file...')
    df.to_csv(csv_path)
    print('Done!')
    if return_df:
        return df
