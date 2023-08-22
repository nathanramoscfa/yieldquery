import os
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from utils.drivers import setup_driver
from tqdm import tqdm


def navigate_to_page(driver, url):
    """
    :description: Navigate to the target page and accept the terms and conditions

    :param driver: Selenium driver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :param url: The url of the target page
    :type url: str
    :return: None
    :rtype: None
    """
    driver.get(url)

    WebDriverWait(driver, 20).until(EC.presence_of_element_located((
        By.CSS_SELECTOR,
        '#fundFinder'
    )))


def get_links(driver):
    """
    :description: Get the links to the ETF pages

    :param driver: Selenium driver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :return: The links to the ETF pages
    :rtype: list
    """
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((
        By.CSS_SELECTOR,
        '#gridContainerWrapper'
    )))

    links = []
    index = 0

    while True:
        try:
            # Wait for the row to load
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((
                By.CSS_SELECTOR,
                f"#gridContainerWrapper > div.dockedColumns > div.spacetop_list > "
                f"div.main_table_row.white_row_bg.actionable._data_row_{index}.{'odd' if index % 2 == 0 else 'even'} "
                f"> div:nth-child(1) > div > div > div.col4.assetclass-col > a"
            )))

            # Get the link
            link = driver.find_element(
                By.CSS_SELECTOR,
                f"#gridContainerWrapper > div.dockedColumns > div.spacetop_list > "
                f"div.main_table_row.white_row_bg.actionable._data_row_{index}.{'odd' if index % 2 == 0 else 'even'} "
                f"> div:nth-child(1) > div > div > div.col4.assetclass-col > a"
            ).get_attribute('href')

            # Append the link to the list of links
            links.append(link)

            # Increment the index for the next row
            index += 1

        except (NoSuchElementException, TimeoutException):
            # No more rows found
            break

    return links


def extract_etf_info(driver, url):
    """
    :description: Extract the ETF info from the page

    :param driver: Selenium driver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :param url: The url of the target page
    :type url: str
    :return: The ETF info
    :rtype: dict
    """
    # Navigate to the url
    driver.get(url)

    # Wait for the table to load
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((
        By.CSS_SELECTOR,
        '#holdTabContainerRight > section > div'
    )))

    name = driver.find_element(By.CSS_SELECTOR,
                               'body > div.container-fluid.header-section-container > div:nth-child(12) > div > h1'
                               ).text
    as_of_date = driver.find_element(By.CSS_SELECTOR,
                                     '#holdTabContainerRight > section > h2 > span').text
    ticker = driver.find_element(By.CSS_SELECTOR,
                                 '#SCMpreferedValue').text  # Extract the ticker from the page

    etf_info = {"Ticker": ticker, "Name": name}
    index = 1

    while True:
        try:
            try:
                # Try to get the first column value for 2-column table
                first_column_value = driver.find_element(
                    By.CSS_SELECTOR,
                    f"#holdTabContainerRight > section > div > div:nth-child({index}) > span.altRows__left"
                ).text

                # Try to get the second column value for 2-column table
                second_column_value = driver.find_element(
                    By.CSS_SELECTOR,
                    f"#holdTabContainerRight > section > div > div:nth-child({index}) > span.altRows__right"
                ).text

            except NoSuchElementException:
                # If not found, it is a 3-column table
                first_column_value = driver.find_element(
                    By.CSS_SELECTOR,
                    f"#holdTabContainerRight > section > div > div:nth-child({index}) > span.altRows__col1"
                ).text

                second_column_value = driver.find_element(
                    By.CSS_SELECTOR,
                    f"#holdTabContainerRight > section > div > div:nth-child({index}) > span.altRows__col2"
                ).text

            # Add the data to the dictionary
            etf_info[first_column_value] = second_column_value

            # Increment the index for the next row
            index += 1

        except NoSuchElementException:
            # No more rows found
            break

        etf_info['As of Date'] = as_of_date

    return etf_info


def get_etf_data(driver, links):
    """
    :description: Get the ETF data

    :param driver: Selenium driver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :param links: The links to the ETF pages
    :type links: list
    :return: The ETF data
    :rtype: pd.DataFrame
    """
    # Get data for all ETFs
    data = []
    for link in tqdm(links):
        etf_data = extract_etf_info(driver, link + '#activeTab=holdings')

        # Only add the etf_data to the list if it's not None
        if etf_data is not None:
            data.append(etf_data)

        time.sleep(5)

    # Convert data list to a pandas DataFrame
    df = pd.DataFrame(data)

    # Set 'ticker' as index
    df.set_index('Ticker', inplace=True)

    # Convert to a numeric value
    df['Weighted Avg YTM'] = df['Weighted Avg YTM'].str.rstrip('%').astype('float') / 100.0
    df['Yield to Worst'] = df['Yield to Worst'].str.rstrip('%').astype('float') / 100.0
    df['Weighted Avg Coupon'] = df['Weighted Avg Coupon'].str.rstrip('%').astype('float') / 100.0
    df['Effective Duration'] = df['Effective Duration'].str.rstrip('%').astype('float')
    df['Weighted Avg Maturity'] = df['Weighted Avg Maturity'].str.rstrip('%').astype('float')
    df['Option Adjusted Spread'] = df['Option Adjusted Spread'].str.rstrip('%').astype('float')
    df['Average Price'] = df['Average Price'].str.rstrip('%').astype('float')

    # Remove the 'as of ' prefix from the As of Date column
    df['As of Date'] = df['As of Date'].str.replace('as of ', '')

    # Convert the As of Date column to datetime format
    df['As of Date'] = pd.to_datetime(df['As of Date'], format='%m.%d.%y')

    # Convert the datetime format to MM-DD-YYYY
    df['As of Date'] = df['As of Date'].dt.strftime('%m-%d-%Y')

    # Rename column
    df.rename(columns={'Weighted Avg YTM': 'Yield to Maturity'}, inplace=True)

    # Replace the NaN values in 'Yield to Maturity' and 'Yield to Worst' with the values from the capped columns
    try:
        df['Yield to Maturity'].fillna(df['Yield to Maturity,capped (YTM,%)'] / 100.0, inplace=True)
        df['Yield to Worst'].fillna(df['Yield to Worst,capped (YTW,%)'] / 100.0, inplace=True)
    except TypeError:
        return df

    # Drop the capped columns
    df.drop(['Yield to Maturity,capped (YTM,%)', 'Yield to Worst,capped (YTW,%)'], axis=1, inplace=True)

    # Drop unwanted ETFs
    df.dropna(subset=['Yield to Maturity'], inplace=True)

    # Filter columns
    df = df[[
        'Name', 'Yield to Maturity', 'As of Date', 'Weighted Avg Coupon',
        'Effective Duration', 'Weighted Avg Maturity', 'Option Adjusted Spread',
        'Yield to Worst', 'Average Price', 'Number of Holdings',
        'Average Coupon (%)', 'Effective Maturity (yrs)',
        'Option Adjusted Duration (yrs)'
    ]]

    return df


def goldman_sachs_bot(return_df=False, headless=True):
    """
    :description: Run the Goldman Sachs ETF yield bot

    :param return_df: return the DataFrame if True, default is False
    :type return_df: bool, optional
    :param headless: run the bot in headless mode if True, default is True
    :type headless: bool, optional
    :return: Goldman Sachs ETF yield data
    :rtype: pd.DataFrame
    """
    print('Downloading Goldman Sachs ETF yield data...')
    url = 'https://www.gsam.com/content/gsam/us/en/advisors/fund-center/etf-fund-finder.html#activeTab=charTab&sortF' \
          '=SUPER_ASSETCLASS&sortO=desc'
    driver = setup_driver(headless)
    navigate_to_page(driver, url)
    links = get_links(driver)
    df = get_etf_data(driver, links)

    # Get the absolute path of the project's root directory
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Change the working directory to the project's root directory
    os.chdir(project_dir)

    # Construct the path to your CSV file relative to the project's root directory
    csv_path = os.path.join(project_dir, 'data', 'goldman_sachs.csv')

    print('Saving Goldman Sachs ETF yield data to CSV file...')
    df.to_csv(csv_path)
    print('Done!')
    if return_df:
        return df
