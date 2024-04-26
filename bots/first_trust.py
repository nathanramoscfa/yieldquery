import os
import re
import time
import requests
import random
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from tqdm import tqdm
from time import sleep
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def get_as_of_date(soup):
    """
    :description: Extract the as of date from the soup object

    :param soup: BeautifulSoup object
    :type soup: bs4.BeautifulSoup
    :return: The as of date
    :rtype: str
    """
    container = soup.find('div', {'id': 'FundCharacteristics_FundControlContainer'})
    if container is not None:
        header_bar = container.find('div', {'class': 'fundControlHeaderBar'})
        if header_bar is not None:
            # Extract the date from the string
            date_str = re.search(r'\d{1,2}/\d{1,2}/\d{4}', header_bar.text)
            if date_str is not None:
                # Convert the date string to a datetime object
                date = datetime.strptime(date_str.group(), '%m/%d/%Y')
                # Convert the datetime object to a string in the desired format
                formatted_date = date.strftime('%m-%d-%Y')
                return formatted_date
    return None


def clean_index_field(field):
    """
    :description: Clean the index field

    :param field: The index field
    :type field: str
    :return: The cleaned index field
    :rtype: str
    """
    return re.sub(r'\d+$', '', field)


# Pool of user agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 "
    "Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 "
    "Safari/605.1.15",
    # Add more user agents here if needed
]


def get_etf_data(ticker):
    """
    :description: Get the ETF data

    :param ticker: The ETF ticker
    :type ticker: str
    :return: ETF data
    :rtype: dict
    """
    url = f'https://www.ftportfolios.com/Retail/Etf/EtfSummary.aspx?Ticker={ticker}'

    # Select a random user-agent
    headers = {
        'User-Agent': random.choice(USER_AGENTS)
    }

    # Retry strategy
    retry_strategy = Retry(
        total=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
        backoff_factor=1
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)

    # Making the request with retries and random delays
    for attempt in range(3):
        try:
            response = http.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            etf_name = None

            # Extract ETF name
            etf_name_span = soup.find('span', {'id': 'FundNavigation_lblPageHeader'})
            if etf_name_span is not None:
                etf_name = re.sub(r' \(.*\)', '', etf_name_span.text)

            table = soup.find('table', {'id': 'FundCharacteristics_FundControlContainer_NameValuePairListing'})

            data_dict = {}
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                field_name = clean_index_field(cols[0].text.strip())
                value = cols[1].text.strip()
                data_dict[field_name] = value
            data_dict['As of'] = get_as_of_date(soup)
            data_dict['ETF Name'] = etf_name
            return data_dict

        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            sleep(random.uniform(1, 5))  # Random delay between 1 and 5 seconds

    print(f"Failed to retrieve data for ticker {ticker} after 3 attempts.")
    return None


def first_trust_bot(return_df=False):
    """
    :description: Run the First Trust ETF yield bot

    :param return_df: return the DataFrame if True, default is False
    :type return_df: bool, optional
    :return: First Trust ETF yield data
    :rtype: pd.DataFrame
    """
    tickers = [
        'FEMB',
        'FTSM',
        'HISF',
        'FSIG',
        'LGOV',
        'LMBS',
        'LDSF',
        'FTSL',
        'HYLS',
        'EFIX',
        'FIXD',
        'DEED',
        'UCON',
        'FCAL',
        'MFLX',
        'FMB',
        'FMHI',
        'FMNY',
        'FSMB',
        'FUMB'
    ]

    print('Downloading First Trust ETF yield data...')
    data = {}
    for ticker in tqdm(tickers):
        data[ticker] = get_etf_data(ticker)
        time.sleep(2)

    df = pd.DataFrame(data)
    df = df.loc[['ETF Name', 'Weighted Average Yield-to-Worst', 'As of']].dropna(axis=1).T
    df.index.name = 'Ticker'
    df['Weighted Average Yield-to-Worst'] = df['Weighted Average Yield-to-Worst'].apply(
        lambda x: float(x.replace('%', '')) / 100)

    # Get the absolute path of the project's root directory
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Change the working directory to the project's root directory
    os.chdir(project_dir)

    # Construct the paths to your CSV files relative to the project's root directory
    csv_path = os.path.join(project_dir, 'data', 'first_trust.csv')

    print('Saving First Trust ETF yield data to CSV file...')
    df.to_csv(csv_path)
    print('Done!')
    if return_df:
        return df
