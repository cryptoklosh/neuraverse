import random
from datetime import datetime

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Wallet(Base):
    __tablename__ = 'wallets'

    id: Mapped[int] = mapped_column(primary_key=True)
    private_key: Mapped[str] = mapped_column(unique=True, index=True)
    address: Mapped[str] = mapped_column()
    proxy: Mapped[str] = mapped_column(default=None, nullable=True)
    discord_token: Mapped[str] = mapped_column(default=None, nullable=True)
    twitter_token: Mapped[str] = mapped_column(default=None, nullable=True)
    next_activity_action_time: Mapped[datetime | None] = mapped_column(default=None)


    def __repr__(self):
        return f'[wallet_id: {self.id}] | [{self.address}]'