import os
import pandas as pd
import numpy as np
from yahooquery import Ticker
from arch import arch_model
from arch.__future__ import reindexing
from tqdm import tqdm
from typing import Tuple

processing_dir = os.path.dirname(__file__)
project_root = os.path.dirname(processing_dir)


def build_file_path(file_name):
    """
    :description: Build an absolute file path for the given file name in the 'data' directory.

    :param file_name: Name of the file in the 'data' directory
    :type file_name: str
    :return: Absolute file path
    :rtype: str
    """
    return os.path.join(project_root, 'data', file_name)


def ishares():
    """
    :description: This function retrieves the iShares ETF data.

    :return: The iShares ETF data
    :rtype: pd.DataFrame
    """
    file_path = build_file_path('ishares.csv')
    df = pd.read_csv(file_path, index_col=0)
    df = df[['Name', 'Avg. Yield (%)', 'Avg. Yield as of Date']]
    df.rename(columns={
        'Avg. Yield (%)': 'Yield to Maturity',
        'Avg. Yield as of Date': 'Date'
    }, inplace=True)
    return df


def vanguard():
    """
    :description: This function retrieves the Vanguard ETF data.

    :return: The Vanguard ETF data
    :rtype: pd.DataFrame
    """
    filepath = build_file_path('vanguard.csv')
    df = pd.read_csv(filepath, index_col=0)
    df = df[['Name', 'Yield to Maturity', 'As of']]
    df.rename(columns={'Avg. Yield (%)': 'Yield to Maturity', 'As of': 'Date'}, inplace=True)
    return df


def state_street():
    """
    :description: This function retrieves the State Street ETF data.

    :return: The State Street ETF data
    :rtype: pd.DataFrame
    """
    filepath = build_file_path('state_street.csv')
    df = pd.read_csv(filepath, index_col=0)
    df = df[['Name', 'Yield to Maturity', 'As of Date']]
    df.rename(columns={'Avg. Yield (%)': 'Yield to Maturity', 'As of Date': 'Date'}, inplace=True)
    return df


def schwab():
    """
    :description: This function retrieves the Schwab ETF data.

    :return: The Schwab ETF data
    :rtype: pd.DataFrame
    """
    filepath = build_file_path('schwab.csv')
    df = pd.read_csv(filepath, index_col=0)
    # df = df[['ETF Name', 'Average Yield to Maturity', 'Average Yield to Maturity Date']]
    # df.rename(columns={
    #     'ETF Name': 'Name',
    #     'Average Yield to Maturity': 'Yield to Maturity',
    #     'Average Yield to Maturity Date': 'Date'
    # }, inplace=True)
    df.rename(columns={
        'As of': 'Date'
    }, inplace=True)
    return df


def invesco():
    """
    :description: This function retrieves the Invesco ETF data.

    :return: The Invesco ETF data
    :rtype: pd.DataFrame
    """
    filepath = build_file_path('invesco.csv')
    df = pd.read_csv(filepath, index_col=0)
    df = df[[
        'ETF Name',
        'Yield to Maturity (%)',
        'Yield to Worst (%)',
        'Yield (%)',
        'As of Date'
    ]]
    df.rename(columns={
        'ETF Name': 'Name',
        'Yield to Maturity (%)': 'Yield to Maturity',
        'Yield to Worst (%)': 'Yield to Worst',
        'Yield (%)': 'Yield',
        'As of Date': 'Date'
    }, inplace=True)
    df['Yield to Maturity'] = df.apply(
        lambda x: x['Yield to Worst'] if pd.notnull(x['Yield to Worst']) else (
            x['Yield'] if pd.notnull(x['Yield']) else x['Yield to Maturity']),
        axis=1
    )
    df.drop(columns=['Yield to Worst', 'Yield'], inplace=True)
    return df


def first_trust():
    """
    :description: This function retrieves the First Trust ETF data.

    :return: The First Trust ETF data
    :rtype: pd.DataFrame
    """
    filepath = build_file_path('first_trust.csv')
    df = pd.read_csv(filepath, index_col=0)
    df = df[['ETF Name', 'Weighted Average Yield-to-Worst', 'As of']]
    df.rename(columns={
        'ETF Name': 'Name',
        'Weighted Average Yield-to-Worst': 'Yield to Maturity',
        'As of': 'Date'
    }, inplace=True)
    return df


def jpmorgan():
    """
    :description: This function retrieves the JPMorgan ETF data.

    :return: The JPMorgan ETF data
    :rtype: pd.DataFrame
    """
    filepath = build_file_path('jpmorgan.csv')
    df = pd.read_csv(filepath, index_col=0)
    df = df[['Name', 'Yield to Maturity', 'As of Date']]
    df.rename(columns={'As of Date': 'Date'}, inplace=True)
    return df


def pimco():
    """
    :description: This function retrieves the PIMCO ETF data.

    :return: The PIMCO ETF data
    :rtype: pd.DataFrame
    """
    filepath = build_file_path('pimco.csv')
    df = pd.read_csv(filepath, index_col=0)
    df = df[['Name', 'Yield to Maturity', 'As of Date']]
    df.rename(columns={'As of Date': 'Date'}, inplace=True)
    return df


def wisdomtree():
    """
    :description: This function retrieves the WisdomTree ETF data.

    :return: The WisdomTree ETF data
    :rtype: pd.DataFrame
    """
    filepath = build_file_path('wisdomtree.csv')
    df = pd.read_csv(filepath, index_col=0)
    df = df[['Name', 'Yield to Maturity', 'As of Date']]
    df.rename(columns={'As of Date': 'Date'}, inplace=True)
    return df


def vaneck():
    """
    :description: This function retrieves the VanEck ETF data.

    :return: The VanEck ETF data
    :rtype: pd.DataFrame
    """
    filepath = build_file_path('vaneck.csv')
    df = pd.read_csv(filepath, index_col=0)
    df = df[['Name', 'Yield to Maturity', 'As of Date']]
    df.rename(columns={'As of Date': 'Date'}, inplace=True)
    return df


def goldman_sachs():
    """
    :description: This function retrieves the Goldman Sachs ETF data.

    :return: The Goldman Sachs ETF data
    :rtype: pd.DataFrame
    """
    filepath = build_file_path('goldman_sachs.csv')
    df = pd.read_csv(filepath, index_col=0)
    df = df[['Name', 'Yield to Maturity', 'As of Date']]
    df.rename(columns={'As of Date': 'Date'}, inplace=True)
    return df


def janus_henderson():
    """
    :description: This function retrieves the Janus Henderson ETF data.

    :return: The Janus Henderson ETF data
    :rtype: pd.DataFrame
    """
    filepath = build_file_path('janus_henderson.csv')
    df = pd.read_csv(filepath, index_col=0)
    df = df[['Name', 'Yield to Worst', 'As of Date']]
    df.rename(columns={'Yield to Worst': 'Yield to Maturity', 'As of Date': 'Date'}, inplace=True)
    return df


def dimensional():
    """
    :description: This function retrieves the Dimensional ETF data.

    :return: The Dimensional ETF data
    :rtype: pd.DataFrame
    """
    filepath = build_file_path('dimensional.csv')
    df = pd.read_csv(filepath, index_col=0)
    df = df[['Name', 'Yield to Maturity', 'As of Date']]
    df.rename(columns={'As of Date': 'Date'}, inplace=True)
    return df


def flexshares():
    """
    :description: This function retrieves the FlexShares ETF data.

    :return: The FlexShares ETF data
    :rtype: pd.DataFrame
    """
    filepath = build_file_path('flexshares.csv')
    df = pd.read_csv(filepath, index_col=0)
    df['WEIGHTED AVG YIELD TO MATURITY'] = df['WEIGHTED AVG YIELD TO MATURITY'].fillna(
        df['WEIGHTED AVG YIELD TO WORST'])
    df['WEIGHTED AVG YIELD TO MATURITY'] = df['WEIGHTED AVG YIELD TO MATURITY'].fillna(df['WEIGHTED AVG NOMINAL YIELD'])
    df = df[['NAME', 'WEIGHTED AVG YIELD TO MATURITY', 'AS OF DATE']]
    df.rename(columns={
        'NAME': 'Name',
        'WEIGHTED AVG YIELD TO MATURITY': 'Yield to Maturity',
        'AS OF DATE': 'Date'
    }, inplace=True)
    df.index.name = 'Ticker'
    return df


def combine_data():
    """
    :description: This function processes the ETF data.

    :return: The processed ETF data
    :rtype: pd.DataFrame
    """
    ishares_df = ishares()
    vanguard_df = vanguard()
    state_street_df = state_street()
    schwab_df = schwab()
    invesco_df = invesco()
    first_trust_df = first_trust()
    jpmorgan_df = jpmorgan()
    pimco_df = pimco()
    wisdomtree_df = wisdomtree()
    vaneck_df = vaneck()
    goldman_sachs_df = goldman_sachs()
    janus_henderson_df = janus_henderson()
    dimensional_df = dimensional()
    flexshares_df = flexshares()

    # List of dataframes
    dfs = [
        ishares_df,
        vanguard_df,
        state_street_df,
        schwab_df,
        invesco_df,
        first_trust_df,
        jpmorgan_df,
        pimco_df,
        wisdomtree_df,
        vaneck_df,
        goldman_sachs_df,
        janus_henderson_df,
        dimensional_df,
        flexshares_df
    ]

    # Drop all-NA columns from each DataFrame before concatenation
    cleaned_dfs = [df.dropna(axis=1, how='all') for df in dfs]

    combined_df = pd.concat(cleaned_dfs)

    # Drop rows with any NA values
    return combined_df.dropna()


def download_stock_data(tickers, period='3y'):
    """
    :description: This function downloads the stock data.

    :param tickers: Tickers to download
    :type tickers: list
    :param period: Period to download
    :type period: str
    :return: The stock data
    :rtype: pd.DataFrame
    """
    ticker_str = ' '.join(tickers)
    ticker_obj = Ticker(ticker_str, asynchronous=True)
    stock_data = ticker_obj.history(period=period)

    return stock_data


def get_standard_deviation(stock_data):
    """
    :description: This function calculates the standard deviation of the stock data.

    :param stock_data: The stock data
    :type stock_data: pd.DataFrame
    :return: Standard deviation of the stock data
    :rtype: pd.DataFrame
    """
    std_devs = {}
    for symbol in stock_data.index.get_level_values('symbol').unique():
        symbol_data = stock_data.loc[symbol]
        returns = symbol_data['close'].pct_change().dropna()
        annualized_std_dev = returns.std() * np.sqrt(252)
        std_devs[symbol] = annualized_std_dev

    return round(pd.DataFrame.from_dict(std_devs, orient='index', columns=['Historical Volatility']), 4)


# Function to tune GARCH parameters
def tune_garch_parameters(returns):
    best_aic = np.inf
    best_order = None
    p_values = range(1, 3)
    q_values = range(1, 3)
    for p in p_values:
        for q in q_values:
            try:
                model = arch_model(returns, vol='Garch', p=p, o=0, q=q, rescale=False)
                res = model.fit(disp='off')
                if res.aic < best_aic:
                    best_aic = res.aic
                    best_order = (p, q)
            except:
                continue
    return best_order


def get_expected_standard_deviation(stock_data):
    expected_std_devs = {}
    for symbol in tqdm(stock_data.index.get_level_values('symbol').unique()):
        symbol_data = stock_data.loc[symbol]
        returns = symbol_data['close'].pct_change().dropna() * 100

        # Call the tuning function to get the best p and q
        try:
            best_p, best_q = tune_garch_parameters(returns)
        except TypeError:
            continue

        # Fit a GARCH model with the best p and q
        model = arch_model(returns, vol='GARCH', p=best_p, o=0, q=best_q, rescale=False)
        res = model.fit(disp='off')

        # Get the last forecast of the conditional volatility and annualize it
        forecast = res.forecast(start=0).variance.iloc[-1][0] ** 0.5 * np.sqrt(252)

        # Rescale the forecast back to the original scale
        expected_std_dev = forecast / 100

        # Store the result
        expected_std_devs[symbol] = round(expected_std_dev, 4)

    # Return the results as a DataFrame
    return pd.DataFrame.from_dict(expected_std_devs, orient='index', columns=['Expected Volatility'])


def get_expected_semi_deviation(stock_data):
    expected_semi_devs = {}
    for symbol in tqdm(stock_data.index.get_level_values('symbol').unique()):
        symbol_data = stock_data.loc[symbol]
        returns = symbol_data['close'].pct_change().dropna() * 100

        # Filter negative returns
        negative_returns = returns[returns < returns.mean()]

        # Call the tuning function to get the best p and q
        try:
            best_p, best_q = tune_garch_parameters(negative_returns)
        except TypeError:
            continue

        # Fit a GARCH model with the best p and q
        model = arch_model(negative_returns, vol='GARCH', p=best_p, o=0, q=best_q, rescale=False)
        res = model.fit(disp='off')

        # Get the last forecast of the conditional volatility and annualize it
        forecast = res.forecast(start=0).variance.iloc[-1].iloc[0] ** 0.5 * np.sqrt(252)

        # Rescale the forecast back to the original scale
        expected_semi_dev = forecast / 100

        # Store the result
        expected_semi_devs[symbol] = round(expected_semi_dev, 4)

    # Return the results as a DataFrame
    return pd.DataFrame.from_dict(
        expected_semi_devs,
        orient='index',
        columns=['Downside Volatility']
    )


def get_risk_free_rate(ticker: str = '^TNX') -> Tuple[float, str]:
    """
    Fetch the risk-free rate from a specific ticker, typically a Treasury note yield.

    Parameters:
    - ticker (str, optional): The ticker symbol for the risk-free rate, defaults to '^TNX' for 10-year Treasury note
                              yield.

    Returns:
    - Tuple[float, str]: A tuple containing the risk-free rate as a float and the long name of the risk-free rate
                         source.
    """
    data_dict = Ticker(ticker).price
    risk_free_rate = pd.DataFrame.from_dict(data_dict, orient='index').transpose()
    risk_free_rate_name = risk_free_rate.loc['longName'].squeeze()
    risk_free_rate = round(risk_free_rate.loc['regularMarketPrice'].squeeze() / 100, 4)
    return risk_free_rate, risk_free_rate_name


def process_data(mar: float = None) -> pd.DataFrame:
    """
    :description: This function processes the ETF data.

    :param mar: The minimum acceptable return.
    :type mar: float
    :return: The processed ETF data.
    :rtype: pd.DataFrame
    """
    df = combine_data()  # Assuming this returns a DataFrame with ETF data
    tickers = list(df.index)
    stock_data_dict = download_stock_data(tickers)
    expected_semi_dev_df = get_expected_semi_deviation(stock_data_dict)
    expected_semi_dev_df.index.name = 'Ticker'

    # Ensure both DataFrames have 'Ticker' as their index name for clarity
    df.index.name = 'Ticker'

    # Check and remove any duplicate indices to ensure uniqueness
    df = df[~df.index.duplicated(keep='first')]
    expected_semi_dev_df = expected_semi_dev_df[~expected_semi_dev_df.index.duplicated(keep='first')]

    # Compute the intersection of indices (common tickers) explicitly
    common_tickers = df.index.intersection(expected_semi_dev_df.index)

    # Reindex both DataFrames to only include the common tickers
    df_common = df.reindex(common_tickers)
    expected_semi_dev_common = expected_semi_dev_df.reindex(common_tickers)

    # Concatenate the filtered DataFrames
    final_df = pd.concat(
        [df_common, expected_semi_dev_common],
        axis=1,
        join='inner'
    ).dropna()

    if mar is not None:
        final_df['Sortino Ratio'] = round(
            (final_df['Yield to Maturity'] - mar) /
            final_df['Downside Volatility'],
            2
        )
    else:
        rf = get_risk_free_rate()[0]
        final_df['Sortino Ratio'] = round(
            (final_df['Yield to Maturity'] - rf) /
            final_df['Downside Volatility'],
            2
        )

    final_df['P/E Ratio'] = round(1 / final_df['Yield to Maturity'], 2)

    final_df = final_df[[
        'Name',
        'Yield to Maturity',
        'Downside Volatility',
        'Sortino Ratio',
        'P/E Ratio',
        'Date'
    ]]

    final_df['Yield to Maturity'] = (final_df['Yield to Maturity'])
    final_df['Downside Volatility'] = (final_df['Downside Volatility'])
    final_df['Sortino Ratio Z-Score'] = round(
        (final_df['Sortino Ratio'] - final_df['Sortino Ratio'].mean()) /
        final_df['Sortino Ratio'].std(),
        2
    )

    final_df = final_df[[
        'Name',
        'Yield to Maturity',
        'Downside Volatility',
        'Sortino Ratio',
        'Sortino Ratio Z-Score',
        'P/E Ratio',
        'Date'
    ]]

    return final_df


def filtered_df(
        final_df: pd.DataFrame,
        min_zscore: float = 1.5,
        sort_by: str = 'Yield to Maturity',
        ascending: bool = False,
        file_path: str = None,
        return_df: bool = True
) -> pd.DataFrame:
    """
    :description: Filters and sorts a DataFrame based on specified criteria, and optionally saves it to a CSV file.

    :param final_df: DataFrame to be filtered and sorted.
    :type final_df: pd.DataFrame
    :param min_zscore: Minimum Z-Score to filter the DataFrame.
    :type min_zscore: float
    :param sort_by: Column name to sort the DataFrame.
    :type sort_by: str
    :param ascending: Sort order. If False, sort in descending order.
    :type ascending: bool
    :param file_path: Path to save the DataFrame as a CSV file. If None, file is not saved.
    :type file_path: str
    :param return_df: If True, returns the modified DataFrame.
    :type return_df: bool
    :return: Optionally returns the filtered and sorted DataFrame.
    :rtype: pd.DataFrame
    """
    if not isinstance(final_df, pd.DataFrame):
        raise ValueError("final_df must be a pandas DataFrame.")

    if sort_by not in final_df.columns:
        raise ValueError(f"Column '{sort_by}' not found in DataFrame.")

    df = final_df.copy()

    # Filtering and sorting
    df = df[df['Sortino Ratio Z-Score'] >= min_zscore].sort_values(by=sort_by, ascending=ascending)

    # Formatting columns
    df['Yield to Maturity'] = df['Yield to Maturity'].apply(lambda x: f"{x * 100:.2f}%")
    df['Downside Volatility'] = df['Downside Volatility'].apply(lambda x: f"{x * 100:.2f}%")

    # Save to CSV if file_path is provided
    if file_path:
        try:
            df.to_csv(file_path)
        except Exception as e:
            raise IOError(f"Failed to save DataFrame to {file_path}: {e}")

    # Return DataFrame if return_df is True
    if return_df:
        return df
