import os
import re
import requests
import pandas as pd
import numpy as np
from tqdm import tqdm
from bs4 import BeautifulSoup

url = 'https://www.invesco.com/us/financial-products/etfs/performance/yields?audienceType=Advisor'


def get_soup():
    """
    :description: Get the BeautifulSoup object

    :return: The BeautifulSoup object
    :rtype: bs4.BeautifulSoup
    """
    response = requests.get(url)
    if response.status_code != 200:
        print(f'Failed to retrieve page: {url}')
        return None
    return BeautifulSoup(response.content, 'html.parser')


def get_table():
    """
    :description: Get the table from the soup object

    :return: The table
    :rtype: bs4.element.Tag
    """
    soup = get_soup()
    table = soup.find('div', class_='tab-content')
    return table


def invesco_bot():
    """
    :description: Run the Invesco ETF yield bot

    :return: Invesco ETF yield data
    :rtype: pd.DataFrame
    """
    print('Downloading Invesco ETF yield data...')
    table_html = get_table()
    table = table_html.find('table', {'id': 'pricesTable'})

    # Find the 'th' elements which contain 'as of' text
    date_headers = table.find_all('th', string=re.compile('as of'))

    # Extract the 'as of' date from the first 'th' element found
    date_text = date_headers[0].text if date_headers else None

    # Get only the date part
    date = re.search(r'as of (\d{2}/\d{2}/\d{4})', date_text).group(1) if date_text else None

    headers = []
    for th in table.find_all('th'):
        headers.append(th.text.strip())
    headers = headers[:13]  # Considering only the first 11 headers
    headers = headers[:1] + headers[3:]
    headers = [header.replace('\n', '').replace('\t', '').replace('\r', '') for header in headers]  # Clean the headers

    data = []
    tickers = []
    product_names = []
    for row in tqdm(table.find_all('tr')):
        if "subhead" not in row.get('class', []):  # Skip subhead rows
            cols = row.find_all('td')
            cols = [col.text.strip() for col in cols]
            link = row.find('a', href=True)
            if link:
                tickers.append(link['href'].split('=')[-1])  # Extract ticker from the href attribute
                product_names.append(link.text)  # Get the product name from the text within the <a> tag
            if len(cols) == len(headers):  # Only include rows with the same number of cols as headers
                data.append(cols)

    df = pd.DataFrame(data, columns=headers)

    # Clean the data in the DataFrame
    df = df.applymap(lambda x: x.replace('\n', '').replace('\t', '').replace('\r', '') if isinstance(x, str) else x)

    # Add ticker and edit product name columns
    df['Ticker'] = tickers
    df['Product Name'] = product_names

    df.set_index('Ticker', inplace=True)

    df = df[['Product Name', 'YTM (%)', 'YTW (%)', 'Total Exp. Ratio (%)', 'AUM($M)']]
    df.replace('N/A', np.nan, inplace=True)
    df.dropna(inplace=True)

    # Convert percentage columns to decimal
    df['YTM (%)'] = df['YTM (%)'].apply(lambda x: float(x.replace('%', '')) / 100)
    df['YTW (%)'] = df['YTW (%)'].apply(lambda x: float(x.replace('%', '')) / 100)
    df['Total Exp. Ratio (%)'] = df['Total Exp. Ratio (%)'].apply(lambda x: float(x.replace('%', '')) / 100)

    # Convert AUM($M) to float
    df['AUM($M)'] = df['AUM($M)'].astype(float).round(2)

    # Then, add the date to each row
    df['As of Date'] = date
    df['As of Date'] = pd.to_datetime(df['As of Date'], format='%m/%d/%Y')
    df['As of Date'] = df['As of Date'].dt.strftime('%m-%d-%Y')

    # Get the absolute path of the project's root directory
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Change the working directory to the project's root directory
    os.chdir(project_dir)

    # Construct the paths to your CSV files relative to the project's root directory
    csv_path = os.path.join(project_dir, 'data', 'invesco.csv')

    # Save to CSV file
    print('Saving Invesco ETF yield data to CSV file...')
    df.to_csv(csv_path)
    print('Done!')

    return df
