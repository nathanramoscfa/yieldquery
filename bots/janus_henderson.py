import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from utils.drivers import webdriver_path
from datetime import datetime


def get_yield_to_worst(url):
    """
    :description: Get the yield to worst and as of date from the ETF page

    :param url: The url of the ETF page
    :type url: str
    :return: The yield to worst and as of date
    :rtype: tuple
    """
    response = requests.get(url)
    if response.status_code != 200:
        print(f'Failed to retrieve page: {url}')
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', attrs={'id': 'portfolio_characteristics_table'})

    # Find the as_of_date
    as_of_date_div = soup.find('span', {'class': 'as-of-text-characteristics'})
    if as_of_date_div:
        as_of_date_span = as_of_date_div.find('span', {'class': 'notranslate'})
        if as_of_date_span:
            as_of_date_text = as_of_date_span.text.strip()
            as_of_date = datetime.strptime(as_of_date_text, '%m/%d/%Y').strftime('%m-%d-%Y')
        else:
            as_of_date = None
    else:
        as_of_date = None

    yield_to_worst = None
    for row in table.find_all('tr'):
        first_col = row.find('td')
        if first_col and 'Yield to Worst' in first_col.text:
            yield_to_worst = first_col.find_next_sibling('td').text
            break

    return yield_to_worst, as_of_date


def reject_cookies(driver):
    """
    :description: Reject the cookies

    :param driver: Selenium driver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :return: None
    :rtype: None
    """
    try:
        cookie_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#onetrust-reject-all-handler')))
        cookie_button.click()
    except TimeoutException:
        pass


def get_etf_data(driver):
    """
    :description: Get the ETF data

    :param driver: Selenium driver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :return: The ETF data
    :rtype: list
    """
    wait = WebDriverWait(driver, 10)
    reject_cookies(driver)
    checkbox = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.jh-checkbox input[type=checkbox][name="Fixed Income"]')))
    driver.execute_script("arguments[0].click();", checkbox)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'table')))
    table = driver.find_element(By.CLASS_NAME, "table")
    rows = table.find_elements(By.TAG_NAME, 'tr')

    data = [
        [
            cols[1].find_element(By.TAG_NAME, 'span').text,
            cols[1].find_element(By.TAG_NAME, 'a').text,
            cols[1].find_element(By.TAG_NAME, 'a').get_attribute('href')
        ]
        for cols in (row.find_elements(By.TAG_NAME, 'td') for row in rows[3:])
        if cols
    ]
    return data


def janus_henderson_bot(return_df=False, headless=True):
    """
    :description: Run the Janus Henderson ETF yield bot

    :param return_df: Whether to return the DataFrame
    :type return_df: bool
    :param headless: Whether to run the bot in headless mode
    :type headless: bool
    :return: The ETF data
    :rtype: pd.DataFrame
    """
    print('Downloading Janus Henderson ETF yield data...')
    options = Options()
    if headless:
        options.add_argument('--headless')

    with webdriver.Chrome(service=Service(webdriver_path()), options=options) as driver:
        driver.get('https://www.janushenderson.com/en-us/advisor/product/?vehicle=ETF')
        data = get_etf_data(driver)

    df = pd.DataFrame(data, columns=['Ticker', 'Name', 'Link'])
    df.set_index('Ticker', inplace=True)
    df['Yield to Worst'], df['As of Date'] = zip(*df['Link'].map(get_yield_to_worst))
    df['Yield to Worst'] = df['Yield to Worst'].str.rstrip('%').astype('float') / 100.0
    df.drop('Link', axis=1, inplace=True)

    # Get the absolute path of the project's root directory
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Change the working directory to the project's root directory
    os.chdir(project_dir)

    # Construct the paths to your CSV files relative to the project's root directory
    csv_path = os.path.join(project_dir, 'data', 'janus_henderson.csv')

    print('Saving Janus Henderson ETF yield data to CSV file...')
    df.to_csv(csv_path)
    print('Done!')
    if return_df:
        return df
