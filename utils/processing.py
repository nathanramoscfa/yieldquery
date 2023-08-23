from arch.__future__ import reindexing

import os
import pandas as pd
from yahooquery import Ticker
from arch import arch_model
from tqdm import tqdm
import numpy as np


def ishares():
    """
    :description: This function retrieves the iShares ETF data.

    :return: The iShares ETF data
    :rtype: pd.DataFrame
    """
    file_path = os.path.abspath('./data/ishares.csv')
    df = pd.read_csv(file_path, index_col=0)
    df = df[['Name', 'Avg. Yield (%)', 'Avg. Yield as of Date']]
    df.rename(columns={'Avg. Yield (%)': 'Yield to Maturity', 'Avg. Yield as of Date': 'Date'}, inplace=True)
    return df


def vanguard():
    """
    :description: This function retrieves the Vanguard ETF data.

    :return: The Vanguard ETF data
    :rtype: pd.DataFrame
    """
    df = pd.read_csv('./data/vanguard.csv', index_col=0)
    df = df[['Name', 'Yield to Maturity', 'As of']]
    df.rename(columns={'Avg. Yield (%)': 'Yield to Maturity', 'As of': 'Date'}, inplace=True)
    return df


def state_street():
    """
    :description: This function retrieves the State Street ETF data.

    :return: The State Street ETF data
    :rtype: pd.DataFrame
    """
    df = pd.read_csv('./data/state_street.csv', index_col=0)
    df = df[['Name', 'Yield to Maturity', 'As of Date']]
    df.rename(columns={'Avg. Yield (%)': 'Yield to Maturity', 'As of Date': 'Date'}, inplace=True)
    return df


def schwab():
    """
    :description: This function retrieves the Schwab ETF data.

    :return: The Schwab ETF data
    :rtype: pd.DataFrame
    """
    df = pd.read_csv('./data/schwab.csv', index_col=0)
    df = df[['ETF Name', 'Average Yield to Maturity', 'Average Yield to Maturity Date']]
    df.rename(columns={
        'ETF Name': 'Name',
        'Average Yield to Maturity': 'Yield to Maturity',
        'Average Yield to Maturity Date': 'Date'
    }, inplace=True)
    return df


def invesco():
    """
    :description: This function retrieves the Invesco ETF data.

    :return: The Invesco ETF data
    :rtype: pd.DataFrame
    """
    df = pd.read_csv('./data/invesco.csv', index_col=0)
    df = df[['Product Name', 'YTM (%)', 'As of Date']]
    df.rename(columns={'Product Name': 'Name', 'YTM (%)': 'Yield to Maturity', 'As of Date': 'Date'}, inplace=True)
    return df


def first_trust():
    """
    :description: This function retrieves the First Trust ETF data.

    :return: The First Trust ETF data
    :rtype: pd.DataFrame
    """
    df = pd.read_csv('./data/first_trust.csv', index_col=0)
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
    df = pd.read_csv('./data/jpmorgan.csv', index_col=0)
    df = df[['Name', 'Yield to Maturity', 'As of Date']]
    df.rename(columns={'As of Date': 'Date'}, inplace=True)
    return df


def pimco():
    """
    :description: This function retrieves the PIMCO ETF data.

    :return: The PIMCO ETF data
    :rtype: pd.DataFrame
    """
    df = pd.read_csv('./data/pimco.csv', index_col=0)
    df = df[['Name', 'Yield to Maturity', 'As of Date']]
    df.rename(columns={'As of Date': 'Date'}, inplace=True)
    return df


def wisdomtree():
    """
    :description: This function retrieves the WisdomTree ETF data.

    :return: The WisdomTree ETF data
    :rtype: pd.DataFrame
    """
    df = pd.read_csv('./data/wisdomtree.csv', index_col=0)
    df = df[['Name', 'Yield to Maturity', 'As of Date']]
    df.rename(columns={'As of Date': 'Date'}, inplace=True)
    return df


def vaneck():
    """
    :description: This function retrieves the VanEck ETF data.

    :return: The VanEck ETF data
    :rtype: pd.DataFrame
    """
    df = pd.read_csv('./data/vaneck.csv', index_col=0)
    df = df[['Name', 'Yield to Maturity', 'As of Date']]
    df.rename(columns={'As of Date': 'Date'}, inplace=True)
    return df


def goldman_sachs():
    """
    :description: This function retrieves the Goldman Sachs ETF data.

    :return: The Goldman Sachs ETF data
    :rtype: pd.DataFrame
    """
    df = pd.read_csv('./data/goldman_sachs.csv', index_col=0)
    df = df[['Name', 'Yield to Maturity', 'As of Date']]
    df.rename(columns={'As of Date': 'Date'}, inplace=True)
    return df


def janus_henderson():
    """
    :description: This function retrieves the Janus Henderson ETF data.

    :return: The Janus Henderson ETF data
    :rtype: pd.DataFrame
    """
    df = pd.read_csv('./data/janus_henderson.csv', index_col=0)
    df = df[['Name', 'Yield to Worst', 'As of Date']]
    df.rename(columns={'Yield to Worst': 'Yield to Maturity', 'As of Date': 'Date'}, inplace=True)
    return df


def dimensional():
    """
    :description: This function retrieves the Dimensional ETF data.

    :return: The Dimensional ETF data
    :rtype: pd.DataFrame
    """
    df = pd.read_csv('./data/dimensional.csv', index_col=0)
    df = df[['Name', 'Yield to Maturity', 'As of Date']]
    df.rename(columns={'As of Date': 'Date'}, inplace=True)
    return df


def flexshares():
    """
    :description: This function retrieves the FlexShares ETF data.

    :return: The FlexShares ETF data
    :rtype: pd.DataFrame
    """
    df = pd.read_csv('./data/flexshares.csv', index_col=0)
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
    print("process_data is being called.")
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

    combined_df = pd.concat([
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
    ])

    return combined_df.dropna()


def download_stock_data(tickers, period='3y'):
    ticker_str = ' '.join(tickers)
    ticker_obj = Ticker(ticker_str, asynchronous=True)
    stock_data = ticker_obj.history(period=period)

    return stock_data


def get_standard_deviation(stock_data):
    std_devs = {}
    for symbol in stock_data.index.get_level_values('symbol').unique():
        symbol_data = stock_data.loc[symbol]
        returns = symbol_data['close'].pct_change().dropna()
        annualized_std_dev = returns.std() * np.sqrt(252)
        std_devs[symbol] = annualized_std_dev

    return round(pd.DataFrame.from_dict(std_devs, orient='index', columns=['Standard Deviation']), 4)


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
    return pd.DataFrame.from_dict(expected_std_devs, orient='index', columns=['Expected Annualized Std Dev'])


def process_data():
    df = combine_data()
    tickers = list(df.index)
    stock_data_dict = download_stock_data(tickers)
    std_dev_df = get_standard_deviation(stock_data_dict)
    expected_std_dev_df = get_expected_standard_deviation(stock_data_dict)
    std_dev_df_df = std_dev_df.join(expected_std_dev_df)
    std_dev_df_df.index.name = 'Ticker'

    final_df = pd.concat([df, std_dev_df_df], axis=1).dropna()
    final_df['Yield to Volatility'] = round(final_df['Yield to Maturity'] / final_df['Expected Annualized Std Dev'], 2)
    final_df['P/E Ratio'] = round(1 / final_df['Yield to Maturity'], 2)
    final_df = final_df[[
        'Name', 'Yield to Maturity', 'Expected Annualized Std Dev', 'P/E Ratio', 'Yield to Volatility', 'Date'
    ]]
    final_df['Yield to Maturity'] = (final_df['Yield to Maturity'])
    final_df['Expected Annualized Std Dev'] = (final_df['Expected Annualized Std Dev'])
    final_df['Yield ZScore'] = round(np.abs(
        (final_df['Yield to Maturity'] - final_df['Yield to Maturity'].mean()) / final_df['Yield to Maturity'].std()),
                                     2)
    final_df = final_df[
        ['Name', 'Yield to Maturity', 'Expected Annualized Std Dev', 'P/E Ratio', 'Yield to Volatility', 'Yield ZScore',
         'Date']]

    return final_df


def filtered_df(final_df):
    df = final_df.copy()
    df['Yield to Maturity'] = (df['Yield to Maturity'] * 100).apply(lambda x: f"{x:.2f}%")
    df['Expected Annualized Std Dev'] = (df['Expected Annualized Std Dev'] * 100).apply(
        lambda x: f"{x:.2f}%")
    return df.sort_values(
        by='Yield to Volatility',
        ascending=False
    ).head(30).sort_values(
        by='Yield to Maturity',
        ascending=False
    )
