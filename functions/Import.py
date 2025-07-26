import csv
import random
from datetime import datetime

from loguru import logger

from data import config
from data.models import WalletCSV
from libs.eth_async.client import Client
from libs.eth_async.data.models import Networks
from utils.db_api.wallet_api import get_wallet, db
from utils.db_api.models import Wallet
from utils.encryption import get_private_key
import settings

class Import:
    @staticmethod
    def get_wallets_from_csv(csv_path: str, skip_first_line: bool = True) -> list[WalletCSV]:
        wallets = []

        # with open(csv_path) as f:
        #     reader = csv.reader(f)
        #     for row in reader:
        #         if skip_first_line:
        #             skip_first_line = False
        #             continue
        #
        #         wallets.append(WalletCSV(
        #             e_mail=row[0],
        #             private_key=row[1],
        #             name=row[2],
        #             proxy=row[3],
        #             hyperbolic_key=row[4] if row[4] else None,
        #             nous_key=row[5] if row[5] else None,
        #             openrouter_key=row[6] if row[6] else None
        #         ))

        return wallets

    @staticmethod
    async def wallets():

        wallets = Import.get_wallets_from_csv(csv_path=config.IMPORT_FILE)

        imported = []
        edited = []
        total = len(wallets)

        for wallet in wallets:
            wallet_instance = get_wallet(e_mail=wallet.e_mail)
            if wallet_instance and (
                    wallet_instance.e_mail != wallet.e_mail or
                    wallet_instance.private_key != wallet.private_key or
                    wallet_instance.name != wallet.name or
                    wallet_instance.proxy != wallet.proxy or
                    wallet_instance.hyperbolic_key != wallet.hyperbolic_key or
                    wallet_instance.nous_key != wallet.nous_key or
                    wallet_instance.openrouter_key != wallet.openrouter_key
            ):
                wallet_instance.e_mail = wallet.e_mail
                wallet_instance.private_key = wallet.private_key
                wallet_instance.proxy = wallet.proxy
                wallet_instance.name = wallet.name
                wallet_instance.hyperbolic_key = wallet.hyperbolic_key
                wallet_instance.nous_key = wallet.nous_key
                wallet_instance.openrouter_key = wallet.openrouter_key
                db.commit()
                edited.append(wallet_instance)

            if not wallet_instance:
                if settings.private_key_encryption:
                    client = Client(private_key=get_private_key(wallet.private_key), network=Networks.Ethereum)
                else:
                    client = Client(private_key=wallet.private_key, network=Networks.Ethereum)
                wallet_instance = Wallet(
                    e_mail=wallet.e_mail,
                    name=wallet.name,
                    private_key=wallet.private_key,
                    address=client.account.address,
                    proxy=wallet.proxy,
                    hyperbolic_key=wallet.hyperbolic_key,
                    nous_key=wallet.nous_key,
                    openrouter_key=wallet.openrouter_key,
                    )
                db.insert(wallet_instance)
                imported.append(wallet_instance)

        logger.success(f'Done! imported wallets: {len(imported)}/{total}; '
                       f'edited wallets: {len(edited)}/{total}; total: {total}')
