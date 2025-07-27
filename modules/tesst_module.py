from libs.eth_async.client import Client
from modules.base import Base
from modules.browser import Browser
from utils.db_api.models import Wallet
from utils.logs_decorator import controller_log


class TestModule(Base):
    __module_name__ = "Test Module 1"

    def __init__(self, client: Client, wallet: Wallet):
        self.client = client
        self.wallet = wallet
        self.browser = Browser(wallet=self.wallet)

        self.headers = {
            "Origin": "https://app.testings.Headers",
            "user-agent": "Mozilla/10050000.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
            "sec-ch-ua-platform" : "Windows"
            }

    @controller_log("Testing Requests")
    async def test_module_reqs(self):

        url = 'https://webhook.site/2c8dec4c-2fc5-4d38-a868-2e5091ba81c6'

        async with self.browser:
            r = await self.browser.get(url=url, headers=self.headers)
            r.raise_for_status()
            r = await self.browser.get(url=url)

            return r.json()
