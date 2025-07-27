import csv
import os
import random
from datetime import datetime
from types import SimpleNamespace
from typing import List, Dict, Optional

from loguru import logger

from data import config
from data.config import FILES_DIR

from libs.eth_async.client import Client
from libs.eth_async.data.models import Networks
from libs.eth_async.utils.files import touch
from utils.db_api.wallet_api import get_wallet, db
from utils.db_api.models import Wallet
from utils.encryption import get_private_key
import settings

class Import:

    @staticmethod
    def _read_lines(path: str) -> List[str]:

        file_path = os.path.join(FILES_DIR, path)
        if not os.path.isfile(file_path):
            return []
        with open(file_path, encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]

    @staticmethod
    def parse_wallet_from_txt() -> List[Dict[str, Optional[str]]]:

        private_keys   = Import._read_lines("privatekeys.txt")
        proxies        = Import._read_lines("proxy.txt")
        twitter_tokens = Import._read_lines("twitter_tokens.txt")
        discord_tokens = Import._read_lines("discord_tokens.txt")

        if not private_keys or not proxies:
            raise ValueError("File privatekeys.txt и proxy.txt must contain information")

        record_count = len(private_keys)

        def pick_proxy(i: int) -> Optional[str]:
            if not proxies:
                return None
            if i < len(proxies):
                return proxies[i % len(proxies)]

            return random.choice(proxies)

        wallets: List[Dict[str, Optional[str]]] = []
        for i in range(record_count):
            wallets.append({
                "private_key": private_keys[i],
                "proxy": pick_proxy(i),
                "twitter_token": twitter_tokens[i] if i < len(twitter_tokens) else None,
                "discord_token": discord_tokens[i] if i < len(discord_tokens) else None,
            })

        return wallets


    @staticmethod
    async def wallets():
        raw_wallets = Import.parse_wallet_from_txt()

        wallets = [SimpleNamespace(**w) for w in raw_wallets]

        imported: list[Wallet] = []
        edited: list[Wallet] = []
        total = len(wallets)

        for wl in wallets:
            wallet_instance = get_wallet(private_key=wl.private_key)

            if wallet_instance:
                changed = False

                if wallet_instance.proxy != wl.proxy:
                    wallet_instance.proxy = wl.proxy
                    changed = True

                if hasattr(wallet_instance, "twitter_token") and wallet_instance.twitter_token != wl.twitter_token:
                    wallet_instance.twitter_token = wl.twitter_token
                    changed = True

                if hasattr(wallet_instance, "discord_token") and wallet_instance.discord_token != wl.discord_token:
                    wallet_instance.discord_token = wl.discord_token
                    changed = True

                if changed:
                    db.commit()
                    edited.append(wallet_instance)

                continue

            if settings.PRIVATE_KEY_ENCRYPTION:
                client = Client(private_key=get_private_key(wl.private_key),
                                network=Networks.Ethereum)
            else:
                client = Client(private_key=wl.private_key,
                                network=Networks.Ethereum)

            wallet_instance = Wallet(
                private_key=wl.private_key,
                address=client.account.address,
                proxy=wl.proxy,
                twitter_token=wl.twitter_token,
                discord_token=wl.discord_token,
            )

            if not wallet_instance.twitter_token:
                logger.warning(f'{wallet_instance.id} | {wallet_instance.address} | Twitter Token not found, Twitter Action will be skipped')

            if not wallet_instance.discord_token:
                logger.warning(f'{wallet_instance.id} | {wallet_instance.address} | Discord Token not found, Discord Action will be skipped')

            db.insert(wallet_instance)
            imported.append(wallet_instance)

        logger.success(
            f'Done! imported wallets: {len(imported)}/{total}; '
            f'edited wallets: {len(edited)}/{total}; total: {total}'
        )
