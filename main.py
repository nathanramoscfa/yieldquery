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
import logging


def run_bot(bot, name):
    max_retries = 2
    for i in range(max_retries + 1):  # Attempting the bot max_retries + 1 times (original run plus two retries)
        try:
            bot()
            print(f'{name} ran successfully!')
            return
        except Exception as e:
            if i < max_retries:
                print(f'{name} failed on attempt {i + 1}. Retrying...')
            else:
                logging.error(f'{name} failed on all attempts. Error: {e}')


def main():
    """
    :description: This function runs all the bots and processes the data.

    :return: None
    :rtype: None
    """
    bot_list = [
        (ishares_bot, 'ishares_bot'),
        (vanguard_bot, 'vanguard_bot'),
        (state_street_bot, 'state_street_bot'),
        (schwab_bot, 'schwab_bot'),
        (invesco_bot, 'invesco_bot'),
        (first_trust_bot, 'first_trust_bot'),
        (jpmorgan_bot, 'jpmorgan_bot'),
        (pimco_bot, 'pimco_bot'),
        (wisdomtree_bot, 'wisdomtree_bot'),
        (vaneck_bot, 'vaneck_bot'),
        (goldman_sachs_bot, 'goldman_sachs_bot'),
        (dimensional_bot, 'dimensional_bot'),
        (janus_henderson_bot, 'janus_henderson_bot'),
        (flexshares_bot, 'flexshares_bot')
    ]

    for bot, name in bot_list:
        run_bot(bot, name)

    print('Processing bond ETF yield data...')
    df = process_data()
    print('Saving bond ETF yield data...')
    df.to_csv('data/bond_etf_yield.csv')
    print('Done!')


if __name__ == "__main__":
    main()
