import os
import time
import pandas as pd
from tqdm import tqdm
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.drivers import setup_driver


def scroll_down(driver, percentage=0.05):
    # Scroll down about 5% of the webpage
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    driver.execute_script(f"window.scrollTo(0, {scroll_height * percentage});")
    time.sleep(1)  # delay to allow the page to load


def navigate_to_page(driver, url):
    """
    :description: Navigate to the target page

    :param driver: Selenium driver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :param url: The url of the target page
    :type url: str
    :return: None
    :rtype: None
    """
    driver.get(url)
    try:
        # Handle the pop-up
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#marquee--7646 > div.container > div > div.marquee__content.col-12 > '
                              'div.marquee__attachment.col-12 > div > div > div > div:nth-child(1) > div > a')))
        limited_experience_button = driver.find_element(By.CSS_SELECTOR,
                                                        '#marquee--7646 > div.container > div > '
                                                        'div.marquee__content.col-12 > div.marquee__attachment.col-12 '
                                                        '> div > div > div > div:nth-child(1) > div > a')
        limited_experience_button.click()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'body > div.ui-dialog.ui-corner-all.ui-widget.ui-widget-content.ui-front.ui-dialog'
                              '-buttons > div.ui-dialog-buttonpane.ui-widget-content.ui-helper-clearfix > div > '
                              'button:nth-child(1)')))
        confirm_button = driver.find_element(By.CSS_SELECTOR,
                                             'body > div.ui-dialog.ui-corner-all.ui-widget.ui-widget'
                                             '-content.ui-front.ui-dialog-buttons > '
                                             'div.ui-dialog-buttonpane.ui-widget-content.ui-helper'
                                             '-clearfix > div > button:nth-child(1)')
        confirm_button.click()
    except (NoSuchElementException, TimeoutException, ElementNotInteractableException):
        # Ignore if the pop-up is not found
        pass

    # Re-navigate to the URL after handling the pop-up
    driver.get(url)

    # Wait for the table to load
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((
        By.CSS_SELECTOR,
        '#page_product_finder'
    )))


def get_links(driver):
    """
    :description: Get the links to the ETF pages

    :param driver: Selenium driver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :return: The links to the ETF pages
    :rtype: list
    """
    scroll_down(driver)

    links = []
    i = 1
    while True:
        try:
            link_element = driver.find_element(
                By.CSS_SELECTOR,
                f'#page_product_finder > table.views-table.views-table--responsive.views-view-table.cols-7.sticky'
                f'-enabled.table--page_product_finder.table-funds.d-none.d-lg-table.sticky-table > tbody > '
                f'tr:nth-child({i}) > td.td--fund.views-field.row-data > a'
            )
            links.append(link_element.get_attribute('href'))
            i += 1
        except NoSuchElementException:
            break
    return links


def get_yield_data(driver, links):
    """
    :description: Get the yield data

    :param driver: Selenium driver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :param links: The links to the ETF pages
    :type links: list
    :return: The yield data
    :rtype: dict
    """
    wait_time = 5
    data = {}
    for link in tqdm(links):
        try:
            driver.get(link)
            time.sleep(2)

            ticker = link.split('/')[-1].upper()

            name_element = driver.find_element(
                By.XPATH,
                "//*[starts-with(@id, 'product_intro--')]"
            )
            name = name_element.text.split('\n')[0]

            yield_element = (
                By.CSS_SELECTOR,
                '#sfm-table--yields > table > tbody > tr:nth-child(3) > td:nth-child(3)'
            )
            yield_element = WebDriverWait(driver, wait_time).until(EC.presence_of_element_located(yield_element))
            yield_to_maturity = yield_element.get_attribute("innerText")

            as_of_element = driver.find_element(
                By.CSS_SELECTOR,
                '#sfm-table--yields > table > tbody > tr:nth-child(3) > th > div'
            )
            as_of = as_of_element.get_attribute("innerText")

            data[ticker] = {
                'Name': name,
                'Yield to Maturity': yield_to_maturity,
                'As of': as_of.split(' ')[-1]
            }
        except TimeoutException:
            print(f"TimeoutException encountered for {link}. Skipping to next link.")
            continue

    return data


def create_and_save_dataframe(data, file_path):
    """
    :description: Create a dataframe from the data and save it to a CSV file

    :param data: The data
    :type data: dict
    :param file_path: The path to the CSV file
    :type file_path: str
    :return: The dataframe
    :rtype: pd.DataFrame
    """
    df = pd.DataFrame.from_dict(data, orient='index')
    df['Yield to Maturity'] = df['Yield to Maturity'].str.rstrip('%').astype('float') / 100.0
    df['As of'] = pd.to_datetime(df['As of'])
    df['As of'] = df['As of'].dt.strftime('%m-%d-%Y')
    df.index.name = 'Ticker'
    df.to_csv(file_path)
    return df


def schwab_bot(return_df=False, headless=True):
    """
    :description: Download Vanguard ETF yield data and save it to a CSV file

    :param return_df: Whether to return the dataframe
    :type return_df: bool
    :param headless: Whether to run the bot in headless mode
    :type headless: bool
    :return: The dataframe
    :rtype: pd.DataFrame
    """
    print('Downloading Schwab ETF yield data...')
    url = 'https://www.schwabassetmanagement.com/product-finder?combine=&field_product_solution_target_id%5B%5D=291' \
          '&field_asset_class_target_id%5B%5D=271&field_asset_class_target_id%5B%5D=286'
    driver = setup_driver(headless)
    navigate_to_page(driver, url)
    links = get_links(driver)
    data = get_yield_data(driver, links)
    driver.quit()

    # Get the absolute path of the project's root directory
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Change the working directory to the project's root directory
    os.chdir(project_dir)

    # Construct the paths to your CSV files relative to the project's root directory
    csv_path = os.path.join(project_dir, 'data', 'schwab.csv')

    print('Saving Schwab ETF yield data to CSV file...')
    df = create_and_save_dataframe(data, csv_path)
    print('Done!')
    if return_df:
        return df
