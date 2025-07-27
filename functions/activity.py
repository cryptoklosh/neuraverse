import asyncio
import random
from datetime import datetime, timedelta

from curl_cffi import AsyncSession
from loguru import logger

from functions.controller import Controller
from libs.eth_async.client import Client
from libs.eth_async.data.models import Networks
from utils.db_api.models import Wallet
from utils.db_api.wallet_api import db

async def activity(action: int):
    wallets = db.all(Wallet)

    if action == 1:
        tasks = [test_activity(wallet=wallet) for wallet in wallets]
        await asyncio.gather(*tasks)

    if action == 2:
        tasks = [test_requests(wallet=wallet) for wallet in wallets]
        await asyncio.gather(*tasks)

    if action == 3:
        tasks = [test_web3(wallet=wallet) for wallet in wallets]
        await asyncio.gather(*tasks)


async def test_activity(wallet):
    client = Client(private_key=wallet.private_key, proxy=wallet.proxy, network=Networks.Ethereum)

    controller = Controller(client=client, wallet=wallet)

    c = await controller.testings_info()
    logger.success(c)

async def test_requests(wallet):
    client = Client(private_key=wallet.private_key, proxy=wallet.proxy, network=Networks.Ethereum)

    controller = Controller(client=client, wallet=wallet)

    c = await controller.testings_requests()
    logger.success(c)

async def test_web3(wallet):
    client = Client(private_key=wallet.private_key, proxy=wallet.proxy, network=Networks.Ethereum)

    controller = Controller(client=client, wallet=wallet)

    c = await controller.testing_web3()
    logger.success(c)
