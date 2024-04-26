import os
import time
import random
import pandas as pd
from tqdm import tqdm
from traceback import print_exc
from typing import List, Dict, Optional, Union
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from utils.drivers import setup_driver

url = ('https://www.invesco.com/us/financial-products/etfs/performance?'
       'audienceType=Advisor')

# CSS selectors
tab_content_css = '#etfPerformancesTable'
filter_button_css = ('body > div.responsive-container > main > div > '
                     'div:nth-child(3) > div > '
                     'div.upper-panel-a47793f1-b43b-4b25-ba1a-cf247f753f28 > '
                     'div > '
                     'div.usp_filter.usp_filter_controls.filter-controls'
                     '.uspPlt_a47793f1-b43b-4b25-ba1a-cf247f753f28 > div > '
                     'div > a > h3 > i')
filter_asset_class_css = ('body > div.responsive-container > main > div > '
                          'div:nth-child(3) > div > '
                          'div.upper-panel-a47793f1-b43b-4b25-ba1a'
                          '-cf247f753f28 > div > '
                          'div.usp_filter.usp_filter_controls.filter-controls'
                          '.uspPlt_a47793f1-b43b-4b25-ba1a-cf247f753f28 > div '
                          '> div > div.row-fluid.effect > div:nth-child(2) > '
                          'a > h3 > i')
alternatives_option_css = ('#navFilterInputassetType_a47793f1-b43b-4b25-ba1a'
                           '-cf247f753f28 > ul > li:nth-child(1) > a')
fixed_income_option_css = ('#navFilterInputassetType_a47793f1-b43b-4b25'
                           '-ba1a-cf247f753f28 > ul > li:nth-child(4) > a')
user_preferences_css = '#FinancialProfessional > div > label'
yield_table_css1 = '#overview-details > div:nth-child(6)'
yield_table_css2 = '#overview-details > div:nth-child(7)'
name_css = ('body > div.responsive-container > main > div > section > header > '
            'div.fund-detail-text > h1')
as_of_date_css = '#overview-details > div:nth-child(6) > span'


def navigate_to_page(driver):
    """
    :description: Navigate to the page with the ETF data

    :param driver: The Selenium WebDriver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :return: None
    """
    driver.get(url)

    try:
        # Attempt to click the 'Financial Professional' button if it appears
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((
            By.CSS_SELECTOR, user_preferences_css
        ))).click()
    except TimeoutException:
        # If the button doesn't appear within 5 seconds, move on
        pass

    # Wait for the content to load
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((
        By.CSS_SELECTOR, tab_content_css
    )))

    # Click the 'Filter' button
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((
        By.CSS_SELECTOR, filter_button_css
    ))).click()

    # Click the 'Asset Class' filter
    filter_asset_class = driver.find_element(
        By.CSS_SELECTOR, filter_asset_class_css
    )
    driver.execute_script(
        "arguments[0].click();",
        filter_asset_class
    )

    # # Click the 'Alternatives' option
    # filter_alternatives_option = driver.find_element(
    #     By.CSS_SELECTOR, alternatives_option_css
    # )
    # driver.execute_script(
    #     "arguments[0].click();", filter_alternatives_option
    # )

    # Click the 'Asset Class' option
    filter_asset_class_option = driver.find_element(
        By.CSS_SELECTOR, fixed_income_option_css
    )
    driver.execute_script(
        "arguments[0].click();", filter_asset_class_option
    )


def extract_hyperlinks(driver):
    """
    :description: Extract hyperlinks from the resulting table

    :param driver: The Selenium WebDriver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :return: List of hyperlinks
    :rtype: list
    """
    # Wait for the table content to load
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((
        By.CSS_SELECTOR, tab_content_css
    )))

    # Find all the rows in the table
    rows = driver.find_elements(
        By.CSS_SELECTOR,
        f'{tab_content_css} tbody tr'
    )

    hyperlinks = []

    # Iterate through each row to extract the hyperlinks
    for row in rows:
        try:
            # Find the link element within each row
            link_element = row.find_element(By.TAG_NAME, 'a')
            # Extract the href attribute, which is the hyperlink
            hyperlink = link_element.get_attribute('href')
            hyperlinks.append(hyperlink)
        except NoSuchElementException:
            # If no link is found in the row, continue to the next row
            continue

    # Add ICLO and BKLN ETFs
    hyperlinks.append('https://www.invesco.com/us/financial-products/etfs'
                      '/product-detail?audienceType=Investor&ticker=ICLO')
    hyperlinks.append('https://www.invesco.com/us/financial-products/etfs'
                      '/product-detail?audienceType=Investor&ticker=BKLN')

    return hyperlinks


def find_table(driver, css_selector):
    """
    Attempt to find the table element using the given CSS selector.
    If the element is found but does not contain "Yield to Maturity" or "Yield
    to Worst" in its text, or if the element is not found initially, try a
    modified version of the selector.

    :param driver: The Selenium WebDriver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :param css_selector: CSS selector for the table
    :type css_selector: str
    :return: The found table element or None
    """
    element = None
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                css_selector
            )))
        element = driver.find_element(By.CSS_SELECTOR, css_selector)
        if ("Yield to Maturity" in element.text or "Yield to Worst" in
                element.text or "Yield" in element.text):
            return element
        else:
            raise ValueError()
    except (TimeoutException, ValueError):
        if ("Price/Earnings Ratio" in element.text or "Price/Book Ratio" in
                element.text):
            modified_css_selector = css_selector.replace('6', '7')
        else:
            modified_css_selector = css_selector.replace('6', '5')
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR, modified_css_selector
                )))
            return driver.find_element(By.CSS_SELECTOR, modified_css_selector)
        except TimeoutException:
            return None


def extract_data(driver, hyperlinks):
    """
    :description: Extract data from each hyperlink

    :param driver: The Selenium WebDriver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :param hyperlinks: List of hyperlinks
    :type hyperlinks: list
    :return: List of extracted data
    :rtype: list
    """
    data = []

    # Iterate through each hyperlink to extract data
    for hyperlink in tqdm(hyperlinks):
        driver.get(hyperlink)

        # Find the table elements
        table1 = find_table(driver, yield_table_css1)
        table2 = find_table(driver, yield_table_css2)

        # Find ticker and name
        ticker = hyperlink.split('=')[-1]
        name = driver.find_element(By.CSS_SELECTOR, name_css).text

        # Extract the text content of the table and ticker from the hyperlink
        table_text1 = ticker + '\n' + name + '\n' + table1.text
        table_text2 = ticker + '\n' + name + '\n' + table2.text

        # Append the extracted data to the list
        data.append(table_text1)
        data.append(table_text2)

        # Add a delay to avoid being blocked
        time.sleep(random.randint(2, 10))

    return data


def process_data(data_list: List[str]) -> pd.DataFrame:
    data_dict: Dict[str, List[Optional[Union[float, str]]]] = {
        'Ticker': [],
        'ETF Name': [],
        'Effective Duration (yrs)': [],
        'Modified Duration (yrs)': [],
        'Yield to Maturity (%)': [],
        'Yield to Worst (%)': [],
        'Years to Maturity': [],
        'Weighted Avg Coupon (%)': [],
        'Weighted Avg Price': [],
        'As of Date': []
    }

    all_keys = ['Effective Duration (yrs)', 'Modified Duration (yrs)',
                'Yield to Maturity (%)',
                'Yield to Worst (%)', 'Years to Maturity',
                'Weighted Avg Coupon (%)', 'Weighted Avg Price']

    as_of_dates_captured = {}

    for data in data_list:
        if 'Fund Characteristics' in data:
            lines = data.split('\n')
            ticker = lines[0]
            etf_name = lines[1]
            temp_dict = {key: None for key in all_keys}
            temp_dict['As of Date'] = None

            for i, line in enumerate(lines):
                if line == 'Effective Duration':
                    try:
                        # noinspection PyTypeChecker
                        temp_dict['Effective Duration (yrs)'] = float(
                            lines[i + 1].split(' ')[0])
                    except ValueError:
                        # noinspection PyTypeChecker
                        temp_dict['Effective Duration (yrs)'] = '7-Day Reset'
                elif line == 'Modified Duration':
                    try:
                        # noinspection PyTypeChecker
                        temp_dict['Modified Duration (yrs)'] = float(
                            lines[i + 1].split(' ')[0])
                    except ValueError:
                        # noinspection PyTypeChecker
                        temp_dict['Modified Duration (yrs)'] = '7-Day Reset'
                elif line == 'Yield to Maturity':
                    # noinspection PyTypeChecker
                    temp_dict['Yield to Maturity (%)'] = float(
                        lines[i + 1].rstrip('%')) / 100
                elif line == 'Yield to Worst':
                    # noinspection PyTypeChecker
                    temp_dict['Yield to Worst (%)'] = float(
                        lines[i + 1].rstrip('%')) / 100
                elif line == 'Years to Maturity':
                    # noinspection PyTypeChecker
                    temp_dict['Years to Maturity'] = float(lines[i + 1])
                elif line == 'Weighted Avg Coupon':
                    # noinspection PyTypeChecker
                    temp_dict['Weighted Avg Coupon (%)'] = float(
                        lines[i + 1].rstrip('%')) / 100
                elif line == 'Weighted Avg Price':
                    try:
                        # noinspection PyTypeChecker
                        temp_dict['Weighted Avg Price'] = float(lines[i + 2])
                    except ValueError:
                        # noinspection PyTypeChecker
                        temp_dict['Weighted Avg Price'] = float(lines[i + 1])
                elif line.startswith(
                        'as of') and ticker not in as_of_dates_captured:
                    # noinspection PyTypeChecker
                    temp_dict['As of Date'] = pd.to_datetime(
                        line.split(' ')[-1],
                        format='%m/%d/%Y'
                    ).strftime('%Y-%m-%d')
                    as_of_dates_captured[ticker] = True

            for key in all_keys:
                # noinspection PyTypeChecker
                data_dict[key].append(temp_dict[key])

            # noinspection PyTypeChecker
            data_dict['As of Date'].append(temp_dict['As of Date'])
            data_dict['Ticker'].append(ticker)
            data_dict['ETF Name'].append(etf_name)

    df = pd.DataFrame(data_dict).set_index('Ticker')

    # Post-processing to remove duplicates without "As of Date"
    df_reset = df.reset_index()
    df_sorted = df_reset.sort_values(by=['Ticker', 'As of Date'],
                                     ascending=[True, False])
    df_final = df_sorted.drop_duplicates(subset='Ticker',
                                         keep='first').set_index('Ticker')

    return df_final


def invesco_bot(headless=True):
    """
    :description: Run the Invesco ETF yield bot

    :param headless: Whether to run the WebDriver in headless mode
    :type headless: bool
    :return: Invesco ETF yield data
    :rtype: pd.DataFrame
    """
    print('Downloading Invesco ETF yield data...')

    # Set up the Chrome WebDriver
    driver = setup_driver(headless)

    try:
        # Navigate to the page with the ETF data
        navigate_to_page(driver)

        # Extract hyperlinks from the resulting table
        hyperlinks = extract_hyperlinks(driver)

        # Extract data from each hyperlink
        data = extract_data(driver, hyperlinks)

        # Process the data into a DataFrame
        df = process_data(data)

        # Save the data to a CSV file
        # Get the absolute path of the project's root directory
        project_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))

        # Change the working directory to the project's root directory
        os.chdir(project_dir)

        # Construct the paths to your CSV files relative to the project's root
        # directory
        csv_path = os.path.join(project_dir, 'data', 'invesco.csv')

        # Save to CSV file
        print('Saving Invesco ETF yield data to CSV file...')
        df.to_csv(csv_path)
        print('Done!')

    except (TimeoutException, ElementNotInteractableException):
        print_exc()
        df = pd.DataFrame()

    finally:
        # Close the WebDriver
        driver.quit()

    return df
