import os
import time
import pandas as pd
from tqdm import tqdm
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.drivers import setup_driver


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
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((
        By.CSS_SELECTOR,
        'body > app-root > vfa-list-page > div > div:nth-child(2) > div.col-md-9.col-sm-12 > div > vfa-results > div '
        '> vfa-overview > div > div > table'
    )))


def get_links(driver):
    """
    :description: Get the links to the ETF pages

    :param driver: Selenium driver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :return: The links to the ETF pages
    :rtype: list
    """
    links = []
    i = 1
    while True:
        try:
            link_element = driver.find_element(
                By.CSS_SELECTOR,
                f'body > app-root > vfa-list-page > div > div:nth-child(2) > div.col-md-9.col-sm-12 > div > '
                f'vfa-results > div > vfa-overview > div > div > table > tbody > tr:nth-child({i}) > th > p > '
                f'span:nth-child(2) > a'
            )
            links.append(link_element.get_attribute('href'))
            i += 1
        except NoSuchElementException:
            break
    return links


def get_yield_data(driver, links):
    """
    :description: Get the yield data

    :param driver: Selenium driver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :param links: The links to the ETF pages
    :type links: list
    :return: The yield data
    :rtype: dict
    """
    wait_time = 10
    data = {}
    for link in tqdm(links):
        driver.get(link)
        time.sleep(4)
        ticker_element = driver.find_element(
            By.CSS_SELECTOR,
            '#Dashboard > div.container > div > div.col-md-6.col-lg-8 > h1.ticker.rps-display-one'
        )
        ticker = ticker_element.text

        name_element = driver.find_element(
            By.CSS_SELECTOR,
            '#Dashboard > div.container > div > div.col-md-6.col-lg-8 > h1.fund-name.rps-display-two'
        )
        name = name_element.text

        yield_element = (
            By.CSS_SELECTOR,
            '#characteristics-tabset > characteristics-contianer > div > div > div > fixed-income-characteristic > '
            'div > div > table > tr:nth-child(3) > td:nth-child(2)'
        )
        yield_element = WebDriverWait(driver, wait_time).until(EC.presence_of_element_located(yield_element))
        yield_to_maturity = yield_element.get_attribute("innerText")

        as_of_element = driver.find_element(
            By.CSS_SELECTOR,
            '#characteristics-tabset > characteristics-contianer > div > div > p'
        )
        as_of = as_of_element.get_attribute("innerText")

        data[ticker] = {
            'Name': name,
            'Yield to Maturity': yield_to_maturity,
            'As of': as_of.split(' ')[-1]
        }
    return data


def create_and_save_dataframe(data, file_path):
    """
    :description: Create a dataframe from the data and save it to a CSV file

    :param data: The data
    :type data: dict
    :param file_path: The path to the CSV file
    :type file_path: str
    :return: The dataframe
    :rtype: pd.DataFrame
    """
    df = pd.DataFrame.from_dict(data, orient='index')
    df['Yield to Maturity'] = df['Yield to Maturity'].str.rstrip('%').astype('float') / 100.0
    df['As of'] = pd.to_datetime(df['As of'])
    df['As of'] = df['As of'].dt.strftime('%m-%d-%Y')
    df.index.name = 'Ticker'
    df.to_csv(file_path)
    return df


def vanguard_bot(return_df=False, headless=True):
    """
    :description: Download Vanguard ETF yield data and save it to a CSV file

    :param return_df: Whether to return the dataframe
    :type return_df: bool
    :param headless: Whether to run the bot in headless mode
    :type headless: bool
    :return: The dataframe
    :rtype: pd.DataFrame
    """
    print('Downloading Vanguard ETF yield data...')
    url = 'https://investor.vanguard.com/investment-products/list/etfs?assetclass=fixed_income'
    driver = setup_driver(headless)
    navigate_to_page(driver, url)
    links = get_links(driver)
    data = get_yield_data(driver, links)
    driver.quit()

    # Get the absolute path of the project's root directory
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Change the working directory to the project's root directory
    os.chdir(project_dir)

    # Construct the paths to your CSV files relative to the project's root directory
    csv_path = os.path.join(project_dir, 'data', 'vanguard.csv')

    print('Saving Vanguard ETF yield data to CSV file...')
    df = create_and_save_dataframe(data, csv_path)
    print('Done!')
    if return_df:
        return df
