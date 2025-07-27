from typing import Optional

from curl_cffi import requests

from utils.db_api.models import Wallet

DEFAULT_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"

class BaseAsyncSession(requests.AsyncSession):
    def __init__(
            self,
            proxy: str = None,
            user_agent: str = DEFAULT_UA,
            *,
            impersonate: requests.BrowserType = requests.BrowserType.chrome136,
            **session_kwargs,
    ):
        proxies = {"http": proxy, "https": proxy}
        headers = session_kwargs.pop("headers", {})
        headers["user-agent"] = user_agent
        super().__init__(
            proxies=proxies,
            headers=headers,
            impersonate=impersonate,
            **session_kwargs,
        )

    @property
    def user_agent(self) -> str:
        return self.headers["user-agent"]


class Browser:
    __module__ = 'Browser'

    def __init__(self, wallet: Wallet):
        self.wallet: Wallet = wallet
        self.async_session: Optional[BaseAsyncSession] = None

    #todo Client Headers Constuctor by platfrom+version

    async def __aenter__(self):
        self.async_session = BaseAsyncSession(proxy=self.wallet.proxy)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.async_session.close()

    async def _ensure_session(self):
        if self.async_session is None:
            raise RuntimeError("Browser must be used within 'async with'.")

    async def get(self, **kwargs):
        await self._ensure_session()
        r = await self.async_session.get(**kwargs)

        return r

    async def post(self, **kwargs):
        await self._ensure_session()
        r = await self.async_session.post(**kwargs)

        return r

    async def put(self, **kwargs):
        await self._ensure_session()
        r = await self.async_session.put(**kwargs)

        return r
