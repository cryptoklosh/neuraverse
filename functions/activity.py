import asyncio
import random
from datetime import datetime, timedelta

from curl_cffi import AsyncSession
from loguru import logger

from data.config import ThematicSettings
from functions.controller import Controller
from utils.db_api.models import Wallet
from utils.db_api.wallet_api import db

async def reset_data():

    wallets = db.all(Wallet)
    for wallet in wallets:

        if wallet.next_activity_action_time is None:
            continue

        wallet_date = wallet.next_activity_action_time.strftime('%Y-%m-%d')

        now_utc = datetime.utcnow()
        current_date = now_utc.strftime('%Y-%m-%d')

        if wallet_date != current_date:
            logger.debug(f'{wallet.name} | Next day come, refreshing db, Current Date - {current_date}, Wallet Date - {wallet_date}')

            if wallet.klok_session is not None:
                wallet.klok = True

            wallet.chainopera = True

            db.commit()
        else:
            logger.debug(f'{wallet.name} | Skipping refresh db. Current Date - {current_date}, Wallet Date - {wallet_date}')

async def activity():

    while True:
        client = Controller()

        await reset_data()

        wallets = db.all(Wallet)

        nous = len([wallet for wallet in wallets if wallet.nous_key])
        chainopera = len(wallets)
        openrouter = len([wallet for wallet in wallets if wallet.openrouter_key])
        hyperbolic = len([wallet for wallet in wallets if wallet.hyperbolic_key])
        count = hyperbolic + nous + chainopera + openrouter
        await client.run_all_conversations(count=15)

        sleep = random.randint(3600, 5600)
        logger.debug(f'Cicle completed, start sleep for {sleep // 60} minutes ({round(sleep // 60 / 60, 2)} hrs)...')
        await asyncio.sleep(sleep)
