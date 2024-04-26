import os
import datetime
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
    :description: Navigate to the target page

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
        '#fundlisting > div > div:nth-child(2) > div.table-responsive > table'
    )))

    asset_class_menu_selector = '#fundlisting > div > div.fund > div > div:nth-child(1) > div:nth-child(2) > div'
    asset_class_menu = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, asset_class_menu_selector)))
    asset_class_menu.click()

    fixed_income_selector = '#react-select-3-option-6'
    select_fixed_income = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, fixed_income_selector)))
    select_fixed_income.click()


def get_links(driver):
    """
    :description: Get the links to the ETF pages

    :param driver: Selenium driver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :return: The links to the ETF pages
    :rtype: list
    """
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((
        By.CSS_SELECTOR,
        '#fundlisting > div > div:nth-child(2) > div.table-responsive > table'
    )))

    idx = 1  # index for nth-child in css selector
    links = []

    while True:
        try:
            # Try finding the link in the current row
            link = driver.find_element(By.CSS_SELECTOR,
                                       f'#fundlisting > div > div:nth-child(2) > div.table-responsive > table > '
                                       f'tbody > tr:nth-child({idx}) > td.nameLink > a')
            links.append(link.get_attribute('href'))
            idx += 1
        except NoSuchElementException:
            # If the link in the current row was not found, stop the loop
            break

    return links


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

    # Try to extract yield_to_maturity, if it's not available print the ticker and skip to next link
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                        '#fund-overview > div > div:nth-child(1) > '
                                                                        'table')))
        yield_to_maturity = driver.find_element(By.CSS_SELECTOR,
                                                '#fund-overview > div > div:nth-child(1) > table > tbody > '
                                                'tr:nth-child(9) > td:nth-child(2)').text
    except TimeoutException:
        return None  # Returns None if yield_to_maturity is not present, which leads to skipping this ETF

    # Extract the info
    name = driver.find_element(By.CSS_SELECTOR, '#details-left-panel-wrapper > h1').text

    # Extract the as_of_date, remove the prefix and convert it to a datetime
    raw_as_of_date = driver.find_element(By.CSS_SELECTOR,
                                         '#fund-overview > div > div:nth-child(1) > table > tbody > tr:nth-child(9) > '
                                         'td:nth-child(1)').text
    if 'a/o' in raw_as_of_date:
        as_of_date = raw_as_of_date.split('a/o ')[-1].strip(' )')
        as_of_date = datetime.datetime.strptime(as_of_date, '%m/%d/%Y')
    else:
        return None  # Returns None if as_of_date is not present, which leads to skipping this ETF

    ticker = driver.find_element(By.CSS_SELECTOR,
                                 '#details-left-panel-wrapper > h2').text  # Extract the ticker from the page

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
        try:
            etf_data = extract_etf_info(driver, link)

            # Only add the etf_data to the list if it's not None
            if etf_data is not None:
                data.append(etf_data)
        except NoSuchElementException:
            print(f"Failed to retrieve data for {link}. Skipping to next link.")

    # Convert data list to a pandas DataFrame
    df = pd.DataFrame(data)

    # Set 'ticker' as index
    df.set_index('Ticker', inplace=True)

    # Convert 'yield_to_maturity' to a numeric value
    df['Yield to Maturity'] = df['Yield to Maturity'].str.rstrip('%').astype('float') / 100.0

    # Convert 'as_of_date' to datetime
    df['As of Date'] = pd.to_datetime(df['As of Date'], format="%m/%d/%Y")
    df['As of Date'] = df['As of Date'].dt.strftime('%m-%d-%Y')

    # Drop rows where 'As of Date' is NaN
    df.dropna(subset=['As of Date'], inplace=True)

    return df


def wisdomtree_bot(return_df=False, headless=True):
    """
    :description: Download WisdomTree ETF yield data

    :param return_df: Whether to return the DataFrame
    :type return_df: bool
    :param headless: Whether to run the bot in headless mode
    :type headless: bool
    :return: The DataFrame
    :rtype: pd.DataFrame
    """
    print('Downloading WisdomTree ETF yield data...')
    url = 'https://www.wisdomtree.com/etfs'
    driver = setup_driver(headless)
    navigate_to_page(driver, url)
    links = get_links(driver)
    df = get_etf_data(driver, links)

    # Get the absolute path of the project's root directory
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Change the working directory to the project's root directory
    os.chdir(project_dir)

    # Construct the paths to your CSV files relative to the project's root directory
    csv_path = os.path.join('data', 'wisdomtree.csv')

    print('Saving WisdomTree ETF yield data to CSV file...')
    df.to_csv(csv_path)
    print('Done!')
    if return_df:
        return df
