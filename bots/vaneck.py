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
    :description: Navigate to the target page

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
        '#overview'
    )))


def get_links(driver):
    """
    :description: Get the links to the ETF pages

    :param driver: Selenium driver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :return: The links to the ETF pages
    :rtype: list
    """
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((
        By.CSS_SELECTOR,
        '.fund-explorer-table-tooltip-item, .bold.text-left a'
    )))

    links1 = driver.find_elements(By.CSS_SELECTOR, '.fund-explorer-table-tooltip-item')
    links2 = driver.find_elements(By.CSS_SELECTOR, '.bold.text-left a')

    links = links1 + links2

    return sorted(list(set([link.get_attribute('href') + 'portfolio/' for link in links if link.get_attribute('href') is not None])))


def scroll_until_found(driver, css_selector):
    """
    :description: Scroll until the element is found

    :param driver: Selenium driver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :param css_selector: The CSS selector of the element
    :type css_selector: str
    :return: The element
    :rtype: selenium.webdriver.remote.webelement.WebElement
    """
    SCROLL_PAUSE_TIME = 0.5  # Pause time between scrolls
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to next viewport
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(SCROLL_PAUSE_TIME)  # wait time after each scroll
        try:
            element = driver.find_element(By.CSS_SELECTOR, css_selector)
            # Scroll so the element is in the center of viewport
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            break
        except NoSuchElementException:
            pass
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            raise NoSuchElementException("Could not find element with selector: {}".format(css_selector))
        last_height = new_height
    return element


def extract_etf_info(driver, url):
    """
    :description: Extract the ETF info

    :param driver: Selenium driver
    :type driver: selenium.webdriver.chrome.webdriver.WebDriver
    :param url: The url of the ETF page
    :type url: str
    :return: The ETF info
    :rtype: dict
    """
    # Navigate to the url
    driver.get(url)

    # Wait for the page to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#overview')))

    # Check for the pop-up
    try:
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                    '#gateway-modal > div > div > div > '
                                                                    'div.row.justify-content-center > div > div > '
                                                                    'div.form-row.mb-lg-0.mb-4 > '
                                                                    'div.col-lg-6.scroll-to-investor > div.dropdown > '
                                                                    'button')))
        investor_type_menu = driver.find_element(By.CSS_SELECTOR,
                                                 '#gateway-modal > div > div > div > div.row.justify-content-center > '
                                                 'div > div > div.form-row.mb-lg-0.mb-4 > '
                                                 'div.col-lg-6.scroll-to-investor > div.dropdown > button')
        investor_type_menu.click()
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                    '#gateway-modal > div > div > div > '
                                                                    'div.row.justify-content-center > div > div > '
                                                                    'div.form-row.mb-lg-0.mb-4 > '
                                                                    'div.col-lg-6.scroll-to-investor > '
                                                                    'div.dropdown.show > div > button:nth-child(3)')))
        financial_advisor_option = driver.find_element(By.CSS_SELECTOR,
                                                       '#gateway-modal > div > div > div > '
                                                       'div.row.justify-content-center > div > div > '
                                                       'div.form-row.mb-lg-0.mb-4 > div.col-lg-6.scroll-to-investor > '
                                                       'div.dropdown.show > div > button:nth-child(3)')
        financial_advisor_option.click()
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                    '#disclaimer_block > div.mt-3 > '
                                                                    'button.btn.btn-primary.gateway__action.agree')))
        agree_button = driver.find_element(By.CSS_SELECTOR,
                                           '#disclaimer_block > div.mt-3 > button.btn.btn-primary.gateway__action.agree'
                                           )
        agree_button.click()
    except (NoSuchElementException, TimeoutException):
        # Ignore if the pop-up is not found
        pass

    # Extract the info
    try:
        ticker_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                '#root > main > div.container > '
                'div.fund-page-secondary-nav-wrp.fixed-nav > '
                've-fundpagesecondarynav > div > div > div.inner-container > '
                'div.fund-label.d-flex > div.ticker-label.pr-2.font-weight-bold'
            )))
        ticker = ticker_element.text

        name_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.CSS_SELECTOR,
                '#root > main > div.container > '
                'div.fund-page-secondary-nav-wrp.fixed-nav > '
                've-fundpagesecondarynav > div > div > div.inner-container > '
                'div.fund-label.d-flex > div.fund-name-label.px-2'
            )))
        name = name_element.text
    except TimeoutException:
        return None

    name_element = None

    # Scroll to the yield_to_worst element
    try:
        # scroll_until_found(
        #     driver,
        #     '#portfolio'
        # )
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((
            By.CSS_SELECTOR,
            '#portfolio > div > div:nth-child(1) > ve-contentareablock > '
            'section > div > div:nth-child(1) > ul'
        )))
        name_element = driver.find_element(
            By.CSS_SELECTOR,
            '#portfolio > div > div:nth-child(1) > ve-contentareablock > '
            'section > div > div:nth-child(1) > ul > li:nth-child(1) > '
            'div:nth-child(1)'
        ).text
        if name_element == 'Yield to Maturity':
            yield_to_worst = None
        elif name_element == 'Yield to Worst':
            yield_to_worst_element = driver.find_element(
                By.CSS_SELECTOR,
                '#portfolio > div > div:nth-child(1) > '
                've-contentareablock > section > div > div:nth-child(1) > ul > '
                'li:nth-child(1) > div:nth-child(2)'
            )
            yield_to_worst = yield_to_worst_element.text
        else:
            yield_to_worst = None
    except NoSuchElementException:
        yield_to_worst = None
    except TimeoutException:
        yield_to_worst = None

    # Try to extract yield_to_maturity
    try:
        if name_element == 'Yield to Maturity':
            yield_to_maturity = driver.find_element(
                By.CSS_SELECTOR,
                '#portfolio > div > div:nth-child(1) > '
                've-contentareablock > section > div > div:nth-child(1) > ul > '
                'li:nth-child(1) > div:nth-child(2)'
            ).text
        elif name_element == 'Yield to Worst':
            yield_to_maturity = driver.find_element(
                By.CSS_SELECTOR,
                '#portfolio > div > div:nth-child(1) > '
                've-contentareablock > section > div > div:nth-child(1) > ul > '
                'li:nth-child(3) > div:nth-child(2)'
            ).text
        else:
            yield_to_maturity = None
    except TimeoutException:
        yield_to_maturity = None

    # Try to extract as_of_date
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((
            By.CSS_SELECTOR,
            '#portfolio > div > div:nth-child(1) > ve-contentareablock > '
            'section > div > div:nth-child(1) > h3 > span'
        )))
        as_of_date = driver.find_element(
            By.CSS_SELECTOR,
            '#portfolio > div > div:nth-child(1) > ve-contentareablock > '
            'section > div > div:nth-child(1) > h3 > span'
        ).text
    except TimeoutException:
        as_of_date = None  # Returns None if yield_to_maturity is not present

    return {
        "Ticker": ticker,
        "Name": name,
        "Yield to Worst": yield_to_worst,
        "Yield to Maturity": yield_to_maturity,
        "As of Date": as_of_date
    }


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

    # Convert the data list into a DataFrame
    df = pd.DataFrame(data)

    # Create a list of the indices of the rows that contain NaN values
    nan_rows = df[df.isna().any(axis=1)].index.tolist()

    # Create a list of the links that correspond to these indices
    nan_links = [links[i] for i in nan_rows]

    # Re-run the loop for these links
    for link in tqdm(nan_links):
        etf_data = extract_etf_info(driver, link)
        # Only add the etf_data to the list if it's not None
        if etf_data is not None:
            # Find the index of this link in the original list
            index = links.index(link)
            # Update the corresponding row in the DataFrame
            df.loc[index] = etf_data

    # Set 'ticker' as index
    df.set_index('Ticker', inplace=True)

    try:
        # Convert to a numeric value
        df['Yield to Worst'] = df['Yield to Worst'].str.rstrip('%').astype('float') / 100.0
    except ValueError:
        df['Yield to Worst'] = None

    try:
        df['Yield to Maturity'] = df['Yield to Maturity'].str.rstrip('%').astype('float') / 100.0
    except ValueError:
        df['Yield to Maturity'] = None

    # Convert 'as_of_date' to datetime
    df['As of Date'] = df['As of Date'].str.replace('as of ', '', case=False)
    df['As of Date'] = pd.to_datetime(df['As of Date'], format="%m/%d/%Y")
    df['As of Date'] = df['As of Date'].dt.strftime('%m-%d-%Y')

    # Remove rows where 'Yield to Maturity' is NaN
    df = df.dropna(subset=['Yield to Maturity'])

    return df


def vaneck_bot(return_df=False, headless=True):
    """
    :description: Run the VanEck ETF yield bot

    :param return_df: Whether to return the DataFrame
    :type return_df: bool
    :param headless: Whether to run the bot in headless mode
    :type headless: bool
    :return: The VanEck ETF yield data
    :rtype: pd.DataFrame
    """
    print('Downloading VanEck ETF yield data...')
    url = ('https://www.vaneck.com/us/en/etf-mutual-fund-finder/etfs/'
           'prices-returns/?InvType=etf&AssetClass=cb,ib,mb,fr&Funds=emf,esf,'
           'grf,iigf,mwmf,emlf,embf,ccif&ShareClass=a,c,i,y,z&'
           'tab=price-returns&Sort=name&SortDesc=true')
    driver = setup_driver(headless)
    navigate_to_page(driver, url)
    links = get_links(driver)
    df = get_etf_data(driver, links)

    # Get the absolute path of the project's root directory
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Change the working directory to the project's root directory
    os.chdir(project_dir)

    # Construct the paths to your CSV files relative to the project's root directory
    csv_path = os.path.join(project_dir, 'data', 'vaneck.csv')

    print('Saving VanEck ETF yield data to CSV file...')
    df.to_csv(csv_path)
    print('Done!')
    if return_df:
        return df
