import os
import time
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from utils.drivers import setup_driver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


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
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'tab-content')))


def accept_cookies(driver):
    """
    :description: Accept the cookies

    :param driver: Selenium driver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :return: None
    :rtype: None
    """
    try:
        cookie_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#js-ssmp-clrButtonLabel')))
        cookie_button.click()
    except TimeoutException:
        pass


def get_links(driver):
    """
    :description: Get the links to the ETF pages

    :param driver: Selenium driver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :return: The links to the ETF pages
    :rtype: list
    """
    link_elements = driver.find_elements(By.CSS_SELECTOR, 'td.fundName > a')
    links = [elem.get_attribute('href') for elem in link_elements]
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
    data = {}
    for link in tqdm(links):
        driver.get(link)
        time.sleep(2)
        ticker = link.split('-')[-1].upper()
        try:
            name_element = driver.find_element(
                By.CSS_SELECTOR,
                '#main-wrapper > div > div.fundpageheader.fundcomps.aem-GridColumn.aem-GridColumn--default--12 > div '
                '> h1 > span:nth-child(1)')
            name = name_element.text
            as_of_date_element = driver.find_element(
                By.CSS_SELECTOR,
                '#overview > div > div:nth-child(8) > section > h2 > span'
            )
            as_of_date = as_of_date_element.text
            as_of_date = as_of_date.split(' ')[-3:]
            date_string = ' '.join(as_of_date)
            date = datetime.strptime(date_string, "%b %d %Y")
            as_of_date = date.strftime("%m-%d-%Y")
            table_rows = driver.find_elements(
                By.CSS_SELECTOR,
                '#overview > div > div > section > div.section-content > table > tbody > tr')
            yield_data = None
            for row in table_rows:
                if "Yield to Maturity" in row.text or "Weighted Average All in Rate" in row.text \
                        or "Current Yield" in row.text:
                    data_element = row.find_element(By.CSS_SELECTOR, 'td.data')
                    yield_data = data_element.text
                    break
            if yield_data is not None:
                data[ticker] = {"Name": name, "Yield to Maturity": yield_data, "As of Date": as_of_date}
        except NoSuchElementException:
            pass
    return data


def create_and_save_dataframe(data, file_path):
    """
    :description: Create a DataFrame from the data and save it to a CSV file

    :param data: The data
    :type data: dict
    :param file_path: The path to the CSV file
    :type file_path: str
    :return: The DataFrame
    :rtype: pd.DataFrame
    """
    df = pd.DataFrame.from_dict(data, orient='index')
    df['Yield to Maturity'] = df['Yield to Maturity'].str.rstrip('%').astype('float') / 100.0
    df.index.name = 'Ticker'
    df.to_csv(file_path)
    return df


def state_street_bot(return_df=False):
    """
    :description: Run the State Street bot

    :param return_df: Whether to return the DataFrame, default is False
    :type return_df: bool, optional
    :return: The DataFrame
    :rtype: pd.DataFrame
    """
    print('Downloading State Street ETF yield data...')
    url = 'https://www.ssga.com/us/en/intermediary/etfs/fund-finder?g=assetclass%3Afixed-income'
    driver = setup_driver()
    navigate_to_page(driver, url)
    accept_cookies(driver)
    links = get_links(driver)
    data = get_yield_data(driver, links)
    driver.quit()

    # Get the absolute path of the project's root directory
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Change the working directory to the project's root directory
    os.chdir(project_dir)

    # Construct the paths to your CSV files relative to the project's root directory
    csv_path = os.path.join(project_dir, 'data', 'state_street.csv')

    print('Saving State Street ETF yield data to CSV file...')
    df = create_and_save_dataframe(data, csv_path)
    print('Done!')

    if return_df:
        return df
