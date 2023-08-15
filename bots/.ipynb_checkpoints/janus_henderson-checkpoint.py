import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_yield_to_worst(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f'Failed to retrieve page: {url}')
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', attrs={'id': 'portfolio_characteristics_table'})

    for row in table.find_all('tr'):
        first_col = row.find('td')
        if first_col and 'Yield to Worst' in first_col.text:
            return first_col.find_next_sibling('td').text
    return None


def get_etf_data(driver):
    wait = WebDriverWait(driver, 10)
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


def janus_henderson_scraper(chrome_driver_path):
    options = Options()
    options.add_argument('--headless')

    with webdriver.Chrome(service=Service(chrome_driver_path), options=options) as driver:
        driver.get('https://www.janushenderson.com/en-us/advisor/product/?vehicle=ETF')
        data = get_etf_data(driver)

    df = pd.DataFrame(data, columns=['Ticker', 'Name', 'Link'])
    df.set_index('Ticker', inplace=True)
    df['Yield to Worst'] = df['Link'].map(get_yield_to_worst)
    df.drop('Link', axis=1, inplace=True)
    return df
