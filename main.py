from bots.ishares import ishares_bot
from bots.vanguard import vanguard_bot
from bots.state_street import state_street_bot
from bots.schwab import schwab_bot
from bots.invesco import invesco_bot
from bots.first_trust import first_trust_bot
from bots.jpmorgan import jpmorgan_bot
from bots.pimco import pimco_bot
from bots.wisdomtree import wisdomtree_bot
from bots.vaneck import vaneck_bot
from bots.goldman_sachs import goldman_sachs_bot
from bots.janus_henderson import janus_henderson_bot
from bots.dimensional import dimensional_bot
from bots.flexshares import flexshares_bot
from utils.processing import process_data


def main():
    """
    :description: This function runs all the bots and processes the data.

    :return: None
    :rtype: None
    """
    ishares_bot()
    vanguard_bot()
    state_street_bot()
    schwab_bot()
    invesco_bot()
    first_trust_bot()
    jpmorgan_bot()
    pimco_bot()
    wisdomtree_bot()
    vaneck_bot()
    goldman_sachs_bot()
    dimensional_bot()
    janus_henderson_bot()
    flexshares_bot()
    print('Processing bond ETF yield data...')
    df = process_data()
    print('Saving bond ETF yield data...')
    df.to_csv('data/bond_etf_yield.csv')
    print('Done!')


if __name__ == "__main__":
    main()
