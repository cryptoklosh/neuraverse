import os
import csv

from libs.eth_async.utils.utils import update_dict
from libs.eth_async.utils.files import touch, write_json, read_json

from data import config
from data.models import WalletCSV


def create_files():
    touch(path=config.FILES_DIR)
    touch(path=config.LOG_FILE, file=True)
    touch(path=config.ERRORS_FILE, file=True)

    if not os.path.exists(config.IMPORT_FILE):
        with open(config.IMPORT_FILE, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(WalletCSV.header)

    try:
        current_settings: dict | None = read_json(path=config.SETTINGS_FILE)
    except Exception:
        current_settings = {}

    # settings = {
    #     'private_key_encryption': False,
    #     'withdraw_usd': {'from': 10, 'to': 15},
    #     'eth_minimal_balance': 0.0005,
    #     'eth_minimal_balance_usd': 15,
    #     'max_gas_price': 0.015,
    #     'okx': {
    #         'minimum_balance': 0.006,
    #         'withdraw_amount': {'from': 200, 'to': 1000},
    #         'delay_between_withdrawals': {'from': 1200, 'to': 1500},
    #         'credentials': {
    #             'api_key': '',
    #             'secret_key': '',
    #             'passphrase': '',
    #         }
    #     },
    #     'activity_actions_delay': {'from': 30, 'to': 90},
    #     'initial_actions_delay': {'from': 60, 'to': 180},
    #     'percent_to_bridge': {'from': 25, 'to': 40},
    #     'percent_to_swap': {'from': 10, 'to': 15},
    #     'max_tx_onchain': 290
    # }
    #
    # write_json(path=config.SETTINGS_FILE, obj=update_dict(modifiable=current_settings, template=settings), indent=2)

create_files()
