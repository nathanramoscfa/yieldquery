import pandas as pd


def ishares():
    """
    :description: This function retrieves the iShares ETF data.

    :return: The iShares ETF data
    :rtype: pd.DataFrame
    """
    df = pd.read_csv('../data/ishares.csv', index_col=0)
    df = df[['Name', 'Avg. Yield (%)', 'Avg. Yield as of Date']]
    df.rename(columns={'Avg. Yield (%)': 'Yield to Maturity', 'Avg. Yield as of Date': 'Date'}, inplace=True)
    return df


def vanguard():
    """
    :description: This function retrieves the Vanguard ETF data.

    :return: The Vanguard ETF data
    :rtype: pd.DataFrame
    """
    df = pd.read_csv('../data/vanguard.csv', index_col=0)
    df = df[['Name', 'Yield to Maturity', 'As of']]
    df.rename(columns={'Avg. Yield (%)': 'Yield to Maturity', 'As of': 'Date'}, inplace=True)
    return df


def state_street():
    """
    :description: This function retrieves the State Street ETF data.

    :return: The State Street ETF data
    :rtype: pd.DataFrame
    """
    df = pd.read_csv('../data/state_street.csv', index_col=0)
    df = df[['Name', 'Yield to Maturity', 'As of Date']]
    df.rename(columns={'Avg. Yield (%)': 'Yield to Maturity', 'As of Date': 'Date'}, inplace=True)
    return df


def schwab():
    """
    :description: This function retrieves the Schwab ETF data.

    :return: The Schwab ETF data
    :rtype: pd.DataFrame
    """
    df = pd.read_csv('../data/schwab.csv', index_col=0)
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
    df = pd.read_csv('../data/invesco.csv', index_col=0)
    df = df[['Product Name', 'YTM (%)', 'As of Date']]
    df.rename(columns={'Product Name': 'Name', 'YTM (%)': 'Yield to Maturity', 'As of Date': 'Date'}, inplace=True)
    return df


def first_trust():
    """
    :description: This function retrieves the First Trust ETF data.

    :return: The First Trust ETF data
    :rtype: pd.DataFrame
    """
    df = pd.read_csv('../data/first_trust.csv', index_col=0)
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
    df = pd.read_csv('../data/jpmorgan.csv', index_col=0)
    df = df[['Name', 'Yield to Maturity', 'As of Date']]
    df.rename(columns={'As of Date': 'Date'}, inplace=True)
    return df


def pimco():
    """
    :description: This function retrieves the PIMCO ETF data.

    :return: The PIMCO ETF data
    :rtype: pd.DataFrame
    """
    df = pd.read_csv('../data/pimco.csv', index_col=0)
    df = df[['Name', 'Yield to Maturity', 'As of Date']]
    df.rename(columns={'As of Date': 'Date'}, inplace=True)
    return df


def wisdomtree():
    """
    :description: This function retrieves the WisdomTree ETF data.

    :return: The WisdomTree ETF data
    :rtype: pd.DataFrame
    """
    df = pd.read_csv('../data/wisdomtree.csv', index_col=0)
    df = df[['Name', 'Yield to Maturity', 'As of Date']]
    df.rename(columns={'As of Date': 'Date'}, inplace=True)
    return df


def vaneck():
    """
    :description: This function retrieves the VanEck ETF data.

    :return: The VanEck ETF data
    :rtype: pd.DataFrame
    """
    df = pd.read_csv('../data/vaneck.csv', index_col=0)
    df = df[['Name', 'Yield to Maturity', 'As of Date']]
    df.rename(columns={'As of Date': 'Date'}, inplace=True)
    return df


def goldman_sachs():
    """
    :description: This function retrieves the Goldman Sachs ETF data.

    :return: The Goldman Sachs ETF data
    :rtype: pd.DataFrame
    """
    df = pd.read_csv('../data/goldman_sachs.csv', index_col=0)
    df = df[['Name', 'Yield to Maturity', 'As of Date']]
    df.rename(columns={'As of Date': 'Date'}, inplace=True)
    return df


def janus_henderson():
    """
    :description: This function retrieves the Janus Henderson ETF data.

    :return: The Janus Henderson ETF data
    :rtype: pd.DataFrame
    """
    df = pd.read_csv('../data/janus_henderson.csv', index_col=0)
    df = df[['Name', 'Yield to Worst', 'As of Date']]
    df.rename(columns={'Yield to Worst': 'Yield to Maturity', 'As of Date': 'Date'}, inplace=True)
    return df


def dimensional():
    """
    :description: This function retrieves the Dimensional ETF data.

    :return: The Dimensional ETF data
    :rtype: pd.DataFrame
    """
    df = pd.read_csv('../data/dimensional.csv', index_col=0)
    df = df[['Name', 'Yield to Maturity', 'As of Date']]
    df.rename(columns={'As of Date': 'Date'}, inplace=True)
    return df


def flexshares():
    """
    :description: This function retrieves the FlexShares ETF data.

    :return: The FlexShares ETF data
    :rtype: pd.DataFrame
    """
    df = pd.read_csv('../data/flexshares.csv', index_col=0)
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


def process_data():
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
