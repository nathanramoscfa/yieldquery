import os
import time
import shutil
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.drivers import webdriver_path

base_url = 'https://www.ishares.com'
filepath = '../data/downloads/ishares.xml'


def get_soup(url):
    """
    :description: Get the BeautifulSoup object from the url

    :param url: The url of the target page
    :type url: str
    :return: The BeautifulSoup object
    :rtype: bs4.BeautifulSoup
    """
    response = requests.get(url)
    if response.status_code != 200:
        print(f'Failed to retrieve page: {url}')
        return None
    return BeautifulSoup(response.content, 'html.parser')


def get_etf_list():
    """
    :description: Get the ETF list

    :return: The ETF list
    :rtype: bs4.BeautifulSoup
    """
    etf_list_url = base_url + '/us/products/etf-investments#/?productView=etf&fac=43549%7C43563%7C43566%7C43567' \
                              '%7C43573%7C43588%7C43590%7C43775%7C60556&pageNumber=1&sortColumn=totalNetAssets' \
                              '&sortDirection=desc&dataView=keyFacts'
    return get_soup(etf_list_url)


def get_yield_data(url):
    """
    :description: Get the yield data from the url

    :param url: The url of the target page
    :type url: str
    :return: The yield data
    :rtype: tuple
    """
    soup = get_soup(url)
    if soup:
        yield_div = soup.find('div', attrs={'class': 'col-yieldToWorst'})
        if yield_div:
            yield_data = yield_div.find('span', class_='data')
            as_of_date = yield_div.find('span', class_='as-of-date')
            if yield_data:
                return yield_data.text.strip(), as_of_date.text.strip()
    return 'N/A'


def ishares_query():
    """
    :description: Get the iShares ETF yield data

    :return: The iShares ETF yield data
    :rtype: pd.DataFrame
    """
    soup = get_etf_list()
    if soup is None:
        return
    data = []
    table = soup.find('table')
    for row in tqdm(table.find_all('tr')):
        link_elements = row.find_all('a')
        if link_elements:
            ticker_link = link_elements[0]
            ticker = ticker_link.text.strip()
            link = base_url + ticker_link['href']
            etf_name_link = link_elements[1]
            etf_name = etf_name_link.text.strip()
            yield_data, as_of_date = get_yield_data(link)
            data.append([ticker, etf_name, link, yield_data, as_of_date])
            time.sleep(1)
    df = pd.DataFrame(data, columns=['Ticker', 'ETF Name', 'Link', 'Yield to Worst', 'As of Date'])
    df.set_index('Ticker', inplace=True)
    df.drop('Link', axis=1, inplace=True)
    df = df[df['Yield to Worst'] != 'N/A']
    df['As of Date'] = pd.to_datetime(df['As of Date'])
    df['As of Date'] = df['As of Date'].dt.strftime('%m-%d-%Y')
    return df


def download_xls():
    """
    :description: Download the iShares ETF list as a xls file

    :return: None
    :rtype: None
    """
    # Prepare Chrome options. Headless mode means the browser is run in the background
    webdriver_options = Options()
    webdriver_options.add_argument('--headless')

    # Set default download directory and disable download prompt
    download_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
    prefs = {
        'download.default_directory': download_dir,
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'safebrowsing.enabled': True,
    }
    webdriver_options.add_experimental_option('prefs', prefs)

    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome(service=Service(webdriver_path()), options=webdriver_options)

    # Go to the webpage
    etf_list_url = 'https://www.ishares.com/us/products/etf-investments#/?productView=etf&fac=43549%7C43563%7C435' \
                   '66%7C43567%7C43573%7C43588%7C43590%7C43775%7C60556&pageNumber=1&sortColumn=totalNetAssets' \
                   '&sortDirection=desc&dataView=keyFacts'
    driver.get(etf_list_url)

    # Wait for the cookie notice to appear and click "Required Only" if it does
    try:
        cookie_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#onetrust-reject-all-handler')))
        ActionChains(driver).move_to_element(cookie_button).click(cookie_button).perform()
    except:
        pass

    # Wait for the DOWNLOAD button to become clickable
    wait = WebDriverWait(driver, 10)  # wait for up to 10 seconds
    download_button = wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR, '#c1612780367522 > div > product-screener > screener-main > screener-control-bar > div > '
                         'screener-download-funds > button')))
    ActionChains(driver).move_to_element(download_button).click(download_button).perform()

    # Find the "DOWNLOAD FILTERED FUNDS (XLS)" button within the dropdown menu and click it
    download_xls_button = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#mat-menu-panel-0 > div > button:nth-child(2)')))
    ActionChains(driver).move_to_element(download_xls_button).click(download_xls_button).perform()

    # We need to wait for the file to be downloaded. This delay depends on your internet speed.
    time.sleep(5)

    # Close the browser
    driver.quit()


def move_xls():
    """
    :description: Move the downloaded xls file to the data/downloads directory and rename it to "ishares.xml"

    :return: None
    :rtype: None
    """
    # Get list of all files from the download directory
    files = os.listdir(os.path.expanduser('~/Downloads'))
    # Find the latest downloaded xls file
    xls_file = max([f for f in files if f.endswith('.xls')],
                   key=lambda x: os.path.getctime(os.path.join(os.path.expanduser('~/Downloads'), x)))

    # Define old and new location
    old_file_location = os.path.join(os.path.expanduser('~/Downloads'), xls_file)
    new_dir = '../data/downloads'
    new_file_location = os.path.join(new_dir, 'ishares.xml')  # changed the extension to .xml

    # Create the new directory if it does not exist
    os.makedirs(new_dir, exist_ok=True)

    # Delete the existing file in new directory if it exists
    if os.path.exists(new_file_location):
        os.remove(new_file_location)

    # Move the file to the new location and rename it to "ishares.xml"
    shutil.copy(old_file_location, new_file_location)


def load_xls():
    """
    :description: Load the xls file into a pandas DataFrame

    :return: The pandas DataFrame
    :rtype: pd.DataFrame
    """
    # Define file location
    file_location = '../data/downloads/ishares.xml'

    # Load the data into a pandas DataFrame, skipping the first row
    try:
        data = pd.read_excel(file_location, engine='xlrd')  # for .xls
    except ValueError:
        data = pd.read_excel(file_location, engine='openpyxl')  # for .xlsx

    # Return the DataFrame
    return data


def xml_to_df():
    """
    :description: Convert the xls file to a pandas DataFrame

    :return: The pandas DataFrame
    :rtype: pd.DataFrame
    """
    # Parse the XML file
    tree = ET.parse(filepath)
    root = tree.getroot()

    data = []

    # Loop over each row in the Worksheet
    for row in root.iter('{urn:schemas-microsoft-com:office:spreadsheet}Row'):
        rowData = []
        for cell in row.iter('{urn:schemas-microsoft-com:office:spreadsheet}Cell'):
            # Get the cell data
            for dataElem in cell.iter('{urn:schemas-microsoft-com:office:spreadsheet}Data'):
                rowData.append(dataElem.text)
        data.append(rowData)

    # Convert to pandas DataFrame and return
    df = pd.DataFrame(data)

    # Gather main columns
    main_columns = df.loc[0][pd.notnull(df.loc[0])][:16]

    # Gather sub-columns
    sub_columns = df.loc[1]
    sub_columns = sub_columns[pd.notnull(sub_columns)]

    # Assign column headers
    df.columns = list(pd.concat([main_columns, sub_columns]))

    # Remove first two unneeded rows
    df = df.loc[2:]

    # Find the first row index where all cells are None
    index_of_none_row = df[df.isnull().all(axis=1)].index[0]

    # Retain only the rows before the first None row
    df = df.loc[:index_of_none_row - 1]

    # Filter df columns
    df = df[[
        'Ticker',
        'Name',
        'Net Expense Ratio (%)',
        'Net Assets (USD)',
        'Asset Class',
        'Sub Asset Class',
        'Region',
        'Market',
        'Location',
        'Investment Style',
        'Duration (yrs)',
        'Avg. Yield (%)',
        'Avg. Yield as of Date'
    ]]

    # Process the data
    df.set_index('Ticker', inplace=True)
    df['Net Expense Ratio (%)'] = pd.to_numeric(df['Net Expense Ratio (%)'], errors='coerce') / 100.0
    df['Net Assets (USD)'] = df['Net Assets (USD)'].astype(float).round(2)
    df['Duration (yrs)'] = pd.to_numeric(df['Duration (yrs)'], errors='coerce').round(2)
    df['Avg. Yield (%)'] = pd.to_numeric(df['Avg. Yield (%)'], errors='coerce') / 100.0
    df['Avg. Yield as of Date'] = pd.to_datetime(df['Avg. Yield as of Date'])
    df['Avg. Yield as of Date'] = df['Avg. Yield as of Date'].dt.strftime('%m-%d-%Y')

    return df


def ishares_bot(method='xls', return_df=False):
    """
    Downloads, moves, and loads iShares ETF data into a pandas DataFrame.

    :param method: 'xls' or 'query'
    :type method: str
    :param return_df: True or False
    :type return_df: bool
    :return: pandas DataFrame
    :rtype: pd.DataFrame
    """
    if method == 'xls':
        print('Downloading iShares ETF yield data...')
        download_xls()
        move_xls()
        df = xml_to_df()
        print('Saving iShares ETF data...')
    elif method == 'query':
        print('Downloading iShares ETF yield data...')
        df = ishares_query()
        print('Saving iShares ETF yield data...')
    else:
        raise ValueError('method must be "xls" or "query"')

    # Get the absolute path of the project's root directory
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Change the working directory to the project's root directory
    os.chdir(project_dir)

    # Construct the paths to your CSV files relative to the project's root directory
    csv_path = os.path.join('data', 'ishares.csv')

    # Save DataFrame to csv
    df.to_csv(csv_path)

    print('Done!')
    if return_df:
        return df
