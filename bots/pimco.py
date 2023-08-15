import os
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
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

    # Helper function to click buttons
    def click_button(css_selector):
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, css_selector)))
            button = driver.find_element(By.CSS_SELECTOR, css_selector)
            button.click()
            time.sleep(2)  # delay to allow the page to react
        except (NoSuchElementException, TimeoutException):
            pass

    # Click the "ETF Filter Options" menu
    click_button('#uc_5_ctl02_filtersPanel > div.fund-select.fund-filter > div.header-fund-medium.no-print > '
                 'span.filter-expand-collapse.pimcon-round-button-white.collapsed > span')

    # Click the "Sector" menu
    click_button('#uc_5_ctl02_sectorFilter > div.header-choosen > i.icomoon.icon-arrow-down10')

    # Select sectors to filter by
    sector_selectors = [
        '#uc_5_ctl02_sectorFilter > div.content-choosen.sectors-choosen > div > div.mutil-choosen > div:nth-child(1) '
        '> div > span',
        '#uc_5_ctl02_sectorFilter > div.content-choosen.sectors-choosen > div > div.mutil-choosen > div:nth-child(2) '
        '> div > span',
        '#uc_5_ctl02_sectorFilter > div.content-choosen.sectors-choosen > div > div.mutil-choosen > div:nth-child(3) '
        '> div > span',
        '#uc_5_ctl02_sectorFilter > div.content-choosen.sectors-choosen > div > div.mutil-choosen > div:nth-child(5) '
        '> div > span',
        '#uc_5_ctl02_sectorFilter > div.content-choosen.sectors-choosen > div > div.mutil-choosen > div:nth-child(6) '
        '> div > span'
    ]

    for selector in sector_selectors:
        click_button(selector)

    time.sleep(10)  # delay before proceeding to next step


def get_links(driver):
    """
    :description: Get the links to the ETF pages

    :param driver: Selenium driver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :return: The links to the ETF pages
    :rtype: list
    """
    links = set()

    # Helper function to get scroll height
    def get_scroll_height():
        # Adding a wait condition here for the page to fully load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body')))
        return driver.execute_script("return document.body.scrollHeight")

    # Initial height
    last_height = get_scroll_height()

    while True:
        # Gather the links
        link_elements = driver.find_elements(By.CSS_SELECTOR, 'tr > td.name.excel > p > a')
        links.update([elem.get_attribute('href') for elem in link_elements if elem.get_attribute('href')])

        # Scroll down by chunk
        driver.execute_script("window.scrollBy(0, 800);")  # Adjust this value according to your needs
        time.sleep(2)  # Adjust this value according to your internet speed or webpage's response time

        # Calculate new scroll height and compare with last scroll height
        new_height = get_scroll_height()
        if new_height == last_height:  # If heights are the same it will exit the function
            break
        last_height = new_height

    return list(links)  # Return the links as a list


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

    # Check for the pop-up
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#SplashPage1 > section > div > div.listOfRoles > ul > li:nth-child(1) > label')))
        financial_advisor_button = driver.find_element(By.CSS_SELECTOR,
                                                       '#SplashPage1 > section > div > div.listOfRoles > ul > '
                                                       'li:nth-child(1) > label')
        financial_advisor_button.click()
    except (NoSuchElementException, TimeoutException, ElementNotInteractableException):
        # Ignore if the pop-up is not found
        pass

    # Check for the "Provide Feedback" pop-up
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                        'body > div.QSIWebResponsive > div > div > '
                                                                        'div.QSIWebResponsiveDialog-Layout1'
                                                                        '-SI_25LWeavDH1uFWca_button-container > '
                                                                        'button:nth-child(2)')))
        no_thanks_button = driver.find_element(By.CSS_SELECTOR,
                                               'body > div.QSIWebResponsive > div > div > '
                                               'div.QSIWebResponsiveDialog-Layout1-SI_25LWeavDH1uFWca_button'
                                               '-container > button:nth-child(2)')
        no_thanks_button.click()
    except (NoSuchElementException, TimeoutException):
        # Ignore if the pop-up is not found
        pass

    # Scroll down about 5% of the webpage
    scroll_height = driver.execute_script("return document.body.scrollHeight")
    driver.execute_script(f"window.scrollTo(0, {scroll_height * 0.05});")
    time.sleep(2)  # delay to allow the page to load

    try:
        # First try with the usual CSS selector
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#pageWrapper > section:nth-child(2) > div:nth-child(19) > div.row > div > div > div')))
        yield_to_maturity = driver.find_element(By.CSS_SELECTOR,
                                                '#pageWrapper > section:nth-child(2) > div:nth-child(19) > div.row > '
                                                'div > div > div > div > div:nth-child(4) > div.datapoint').text
    except NoSuchElementException:
        # If the usual CSS selector fails, try the second CSS selector
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                            '#pageWrapper > section:nth-child(2) > '
                                                                            'div:nth-child(20) > div.row > div > div '
                                                                            '> div')))
            yield_to_maturity = driver.find_element(By.CSS_SELECTOR,
                                                    '#pageWrapper > section:nth-child(2) > div:nth-child(20) > '
                                                    'div.row > div > div > div > div > div:nth-child(4) > '
                                                    'div.datapoint').text
        except NoSuchElementException:
            return None  # Returns None if yield_to_maturity is not present, which leads to skipping this ETF
    except TimeoutException:
        # If it takes too long to find an element
        return None

    # Extract the info
    name = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, '#etf-header > div.container > div.etf-title-row > div.etf-name'))).text

    try:
        # First try with the usual CSS selector
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, '#pageWrapper > section:nth-child(2) > div:nth-child(19) > div.row > div > div > div')))
        as_of_date = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                                     '#pageWrapper > '
                                                                                     'section:nth-child(2) > '
                                                                                     'div:nth-child(19) > div.row > '
                                                                                     'div > div > div > div > '
                                                                                     'div:nth-child(4) > '
                                                                                     'div.as-of-date'))).text
    except (NoSuchElementException, TimeoutException):
        try:
            # If the usual CSS selector fails, try the second CSS selector
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                            '#pageWrapper > section:nth-child(2) > '
                                                                            'div:nth-child(20) > div.row > div > div '
                                                                            '> div')))
            as_of_date = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                                         '#pageWrapper > '
                                                                                         'section:nth-child(2) > '
                                                                                         'div:nth-child(20) > div.row '
                                                                                         '> div > div > div > div > '
                                                                                         'div:nth-child(4) > '
                                                                                         'div.as-of-date'))).text
        except NoSuchElementException:
            raise Exception(f"Failed to find the 'as_of_date' element on {url}")
    except TimeoutException:
        # If it takes too long to find an element
        raise Exception(f"Timed out when trying to find the 'as_of_date' element on {url}")

    ticker = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                                             '#etf-header > div.container > '
                                                                             'div.etf-title-row > h1'))).text

    return {"Ticker": ticker, "Name": name, "Yield to Maturity": yield_to_maturity, "As of Date": as_of_date}


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
        etf_data = extract_etf_info(driver, link)

        # Only add the etf_data to the list if it's not None
        if etf_data is not None:
            data.append(etf_data)

    # Convert data list to a pandas DataFrame
    df = pd.DataFrame(data)

    # Set 'ticker' as index
    df.set_index('Ticker', inplace=True)

    # Convert 'yield_to_maturity' to a numeric value
    df['Yield to Maturity'] = df['Yield to Maturity'].str.rstrip('%').astype('float') / 100.0

    # Convert 'as_of_date' to datetime
    df['As of Date'] = df['As of Date'].str.replace('as of ', '', case=False)
    df['As of Date'] = pd.to_datetime(df['As of Date'], format="%m/%d/%Y")
    df['As of Date'] = df['As of Date'].dt.strftime('%m-%d-%Y')

    return df


def pimco_bot(return_df=False, headless=True):
    """
    :description: Run the PIMCO ETF yield bot

    :param return_df: Whether to return the DataFrame
    :type return_df: bool
    :param headless: Whether to run the bot in headless mode
    :type headless: bool
    :return: The ETF data
    :rtype: pd.DataFrame
    """
    print('Downloading PIMCO ETF yield data...')
    url = 'https://www.pimco.com/en-us/investments/etf'
    driver = setup_driver(headless)
    navigate_to_page(driver, url)
    links = get_links(driver)
    df = get_etf_data(driver, links)

    # Get the absolute path of the project's root directory
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Change the working directory to the project's root directory
    os.chdir(project_dir)

    # Construct the paths to your CSV files relative to the project's root directory
    csv_path = os.path.join('data', 'pimco.csv')

    print('Saving PIMCO ETF yield data to CSV file...')
    df.to_csv(csv_path)
    print('Done!')
    if return_df:
        return df
