import os
import requests
import pandas as pd
import numpy as np
from tqdm import tqdm
from bs4 import BeautifulSoup

base_url = 'https://www.schwabassetmanagement.com'
table_url = 'https://www.schwabassetmanagement.com/product-finder?combine=&field_product_solution_target_id%5B%5D=291' \
            '&field_asset_class_target_id%5B%5D=271&field_asset_class_target_id%5B%5D=286'


def get_soup(url):
    """
    :description: Get the BeautifulSoup object

    :param url: The url of the target page
    :type url: str
    :return: The BeautifulSoup object
    :rtype: bs4.BeautifulSoup
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/91.0.4472.164 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
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
    soup = get_soup(table_url)
    if soup is not None:
        table = soup.find('div', class_='view-content')
        return table
    else:
        print("Failed to get soup.")
        return None


def get_links(table_html):
    links = []
    h3_tags = table_html.find_all('h3', class_='accordion-title')
    for tag in tqdm(h3_tags):
        a_tag = tag.find('a')
        if a_tag:
            relative_link = a_tag['href']
            absolute_link = base_url + relative_link
            links.append(absolute_link)
    return links


def get_tickers_and_names(table_html):
    """
    :description: Get the tickers and names of the ETFs

    :param table_html: The table HTML
    :type table_html: bs4.element.Tag
    :return: The tickers and names of the ETFs
    :rtype: list
    """
    items = table_html.find_all('li', class_='product-table-mobile-list__item')
    tickers_and_names = []
    for item in tqdm(items):
        ticker = item.find('span', class_='symbol').text
        name = item.find('h3', class_='accordion-title').find('a').text.replace(ticker, '').strip()
        tickers_and_names.append((ticker, name))

    return tickers_and_names


def get_yield_data(links):
    """
    :description: Get the yield data

    :param links: The links to the ETF pages
    :type links: list
    :return: The yield data
    :rtype: list
    """
    data = []
    for link in tqdm(links):
        soup = get_soup(link)
        if soup is not None:
            table = soup.find('div', id='sfm-table--yields')
            if table is not None:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if cols:  # Skip the header row
                        # Extract yield type, as-of date, and yield value
                        yield_type = row.find('span').text
                        as_of_date = cols[0].text
                        yield_value = cols[1].text
                        data.append([link, yield_type, as_of_date, yield_value])
            else:
                print("Table not found.")
        else:
            print("Failed to get soup.")
    return data


def data_to_dataframe(tickers_and_names, yield_data):
    """
    Convert the yield data to a DataFrame.

    :param tickers_and_names: The tickers and names of the ETFs
    :type tickers_and_names: list
    :param yield_data: The yield data
    :type yield_data: list
    :return: The yield data as a DataFrame
    :rtype: pd.DataFrame
    """
    df = pd.DataFrame(yield_data, columns=['Link', 'Yield Type', 'As of Date', 'Yield Value'])

    tickers_names_dict = {
        f"https://www.schwabassetmanagement.com/products/{ticker.lower()}": (ticker, name)
        for ticker, name in tickers_and_names
    }

    # Map each link to its corresponding ticker and name
    df['Ticker'] = df['Link'].apply(lambda x: tickers_names_dict.get(x, (np.nan, np.nan))[0])
    df['ETF Name'] = df['Link'].apply(lambda x: tickers_names_dict.get(x, (np.nan, np.nan))[1])

    # Convert yield values and dates
    df['Yield Value'] = df['Yield Value'].str.rstrip('%').astype('float') / 100.0
    df['As of Date'] = pd.to_datetime(df['As of Date'], format='%m/%d/%Y').dt.strftime('%m-%d-%Y')

    # Pivot DataFrame
    df_pivot_yield = df.pivot(index='Ticker', columns='Yield Type', values='Yield Value')
    df_pivot_date = df.pivot(index='Ticker', columns='Yield Type', values='As of Date')

    # Join the two pivot tables
    df_pivot = df_pivot_yield.join(df_pivot_date, lsuffix='', rsuffix=' Date')

    # Add ETF Name back into the DataFrame
    df_pivot['ETF Name'] = df_pivot.index.map(lambda x: tickers_names_dict.get(
        f"https://www.schwabassetmanagement.com/products/{x.lower()}", (np.nan, np.nan))[1])

    # Rearrange columns
    column_order = ['ETF Name', 'SEC Yield (30 Day)', 'SEC Yield (30 Day) Date', 'Distribution Yield (TTM)',
                    'Distribution Yield (TTM) Date', 'Average Yield to Maturity',
                    'Average Yield to Maturity Date']
    df_pivot = df_pivot.reindex(columns=column_order)

    # Remove column name
    df_pivot.rename_axis(None, axis=1, inplace=True)

    return df_pivot


def schwab_bot(return_df=False):
    """
    :description: Run the Schwab ETF yield bot

    :param return_df: return the DataFrame if True, default is False
    :type return_df: bool, optional
    :return: Schwab ETF yield data
    :rtype: pd.DataFrame
    """
    print('Downloading Schwab ETF yield data...')
    table_html = get_table()
    links = get_links(table_html)
    tickers_and_names = get_tickers_and_names(table_html)
    yield_data = get_yield_data(links)
    df = data_to_dataframe(tickers_and_names, yield_data)

    # Get the absolute path of the project's root directory
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Change the working directory to the project's root directory
    os.chdir(project_dir)

    # Construct the paths to your CSV files relative to the project's root directory
    csv_path = os.path.join(project_dir, 'data', 'schwab.csv')

    print('Saving Schwab ETF yield data to CSV file...')
    df.to_csv(csv_path)
    print('Done!')

    if return_df:
        return df
