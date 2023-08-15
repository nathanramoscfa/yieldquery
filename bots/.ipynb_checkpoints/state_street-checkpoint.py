from utils.drivers import webdriver_path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from tqdm import tqdm
import time
import pandas as pd


def setup_driver(headless=True):
    options = Options()
    if headless:
        options.add_argument('--headless')
    driver = webdriver.Chrome(service=Service(webdriver_path()), options=options)
    return driver


def navigate_to_page(driver, url):
    driver.get(url)
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'tab-content')))


def accept_cookies(driver):
    try:
        cookie_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#js-ssmp-clrButtonLabel')))
        cookie_button.click()
    except TimeoutException:
        pass


def get_links(driver):
    link_elements = driver.find_elements(By.CSS_SELECTOR, 'td.fundName > a')
    links = [elem.get_attribute('href') for elem in link_elements]
    return links


def get_yield_data(driver, links):
    data = {}
    for link in tqdm(links):
        driver.get(link)
        time.sleep(2)
        ticker = link.split('-')[-1].upper()
        try:
            name_element = driver.find_element(By.CSS_SELECTOR, '#main-wrapper > div > '
                                                                'div.fundpageheader.fundcomps.aem-GridColumn.aem'
                                                                '-GridColumn--default--12 > div > h1 > '
                                                                'span:nth-child(1)')
            name = name_element.text
            table_rows = driver.find_elements(By.CSS_SELECTOR, '#overview > div > div > section > div.section-content '
                                                               '> table > tbody > tr')
            yield_data = None
            for row in table_rows:
                if "Average Yield To Worst" in row.text or "Weighted Average All in Rate" in row.text \
                        or "Current Yield" in row.text:
                    data_element = row.find_element(By.CSS_SELECTOR, 'td.data')
                    yield_data = data_element.text
                    break
            if yield_data is not None:
                data[ticker] = {"Name": name, "Yield to Worst": yield_data}
        except NoSuchElementException:
            pass
    return data


def create_and_save_dataframe(data, file_path):
    df = pd.DataFrame.from_dict(data, orient='index')
    df['Yield to Worst'] = df['Yield to Worst'].str.rstrip('%').astype('float') / 100.0
    df.index.name = 'Ticker'
    df.to_csv(file_path)
    return df


def state_street_scraper(return_df=False):
    print('Downloading State Street ETF data...')
    url = 'https://www.ssga.com/us/en/intermediary/etfs/fund-finder?g=assetclass%3Afixed-income'
    driver = setup_driver()
    navigate_to_page(driver, url)
    accept_cookies(driver)
    links = get_links(driver)
    data = get_yield_data(driver, links)
    driver.quit()
    print('Saving State Street ETF data...')
    df = create_and_save_dataframe(data, "../data/state_street.csv")
    print('Done.')
    if return_df:
        return df
