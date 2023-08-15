import os
import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from tqdm import tqdm


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


def get_etf_data(ticker):
    """
    :description: Get the ETF data

    :param ticker: The ETF ticker
    :type ticker: str
    :return: ETF data
    :rtype: dict
    """
    url = f'https://www.ftportfolios.com/Retail/Etf/EtfSummary.aspx?Ticker={ticker}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

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
    csv_path = os.path.join('data', 'first_trust.csv')

    print('Saving First Trust ETF yield data to CSV file...')
    df.to_csv(csv_path)
    print('Done!')
    if return_df:
        return df
