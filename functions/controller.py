import asyncio
import logging
import random
from typing import Any
from zoneinfo import available_timezones

from eth_utils.network import networks
from loguru import logger

from data.models import Bridges, Contracts
from libs.eth_async.client import Client
from libs.eth_async.data.models import Networks, Network, TokenAmount
from libs.eth_async.utils.utils import randfloat
from tasks.base import Base
from tasks.bungee import Bungee
from tasks.chain_api import BlockScout
from tasks.jumper import Jumper, JumperBridges
from tasks.matcha import Matcha
from tasks.opensea import OpenSea
from tasks.relayer import Relayer
from tasks.stargate import Stargate
from tasks.superchain_safe import Safe
from tasks.uniswap import Uniswap
from utils.db_api.models import Wallet
from utils.db_api.wallet_api import db
from utils.logs import log_methods_with_module_name
from utils.logs_decorator import controller_log


class Controller(Base):

    def __init__(self, client: Client, wallet: Wallet):
        super().__init__(client)
        self.wallet = wallet
