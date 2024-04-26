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

import os
import sys
import logging

# Suppress 'DevTools listening on...' messages
os.environ['WDM_LOG_LEVEL'] = '0'
sys.stderr = open(os.devnull, 'w')


def run_bot(bot, name):
    """
    This function runs a bot and retries if it fails.

    """
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


def vpn_check():
    """
    :description: This function checks if the user is on a VPN.

    :return: None
    :rtype: None
    """
    # VPN Confirmation
    print("Please switch to a VPN.")
    while True:
        vpn_confirmation = input("Confirm that you are on a VPN before proceeding (Y/N) or (Yes/No): ").strip().lower()
        if vpn_confirmation in ['y', 'yes']:
            break
        elif vpn_confirmation in ['n', 'no']:
            print("Please switch to a VPN and then run the script again.")
            return
        else:
            print("Invalid input. Please enter Yes or No.")


def main():
    """
    :description: This function runs all the bots and processes the data.

    :return: None
    :rtype: None
    """
    # Global logging configuration
    logging.basicConfig(filename='bot_failures.log',
                        level=logging.ERROR,
                        format='%(asctime)s:%(levelname)s:%(message)s')

    # VPN Check
    vpn_check()

    # Run the bots
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

    logging.info('Starting the main function.')

    # Print current working directory for debugging
    logging.info(f'Current working directory: {os.getcwd()}')

    print('Processing bond ETF yield data...')
    try:
        df = process_data(mar=0)
        print(df)
        print('Saving bond ETF yield data...')
        # Explicitly mention the full path for debugging or confirm directory
        full_path = os.path.join(os.path.dirname(__file__), 'data', 'bond_etf_yield.csv')
        df.to_csv(full_path)
        logging.info(f'Data saved successfully to {full_path}.')
        print('Done!')
    except Exception as e:
        logging.error(f'Error during processing or saving: {e}')
        print(f'An error occurred: {e}')
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
