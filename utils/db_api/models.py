from sqlalchemy import JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from data.constants import PROJECT_SHORT_NAME
from data.settings import Settings


class Base(DeclarativeBase):
    pass


class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(primary_key=True)
    private_key: Mapped[str] = mapped_column(unique=True, index=True)
    address: Mapped[str] = mapped_column(unique=True)
    proxy: Mapped[str] = mapped_column(default=None, nullable=True)
    points: Mapped[int] = mapped_column(default=0)
    trading_volume: Mapped[int] = mapped_column(default=0)
    rank: Mapped[int] = mapped_column(default=0)
    faucet_last_claim: Mapped[str] = mapped_column(default="", nullable=True)
    session_token: Mapped[str] = mapped_column(default=None, nullable=True)
    identity_token: Mapped[str] = mapped_column(default=None, nullable=True)
    cookies: Mapped[dict] = mapped_column(JSON, default={}, nullable=True)
    twitter_token: Mapped[str] = mapped_column(default=None, nullable=True)
    twitter_status: Mapped[str] = mapped_column(default="OK", nullable=True)
    discord_token: Mapped[str] = mapped_column(default=None, nullable=True)
    discord_status: Mapped[str] = mapped_column(default=None, nullable=True)
    discord_proxy: Mapped[str] = mapped_column(default=None, nullable=True)

    def __repr__(self):
        if Settings().show_wallet_address_logs:
            return f"[{PROJECT_SHORT_NAME} | {self.id} | {self.address}]"
        return f"[{PROJECT_SHORT_NAME} | {self.id}]"
