import random
from datetime import datetime

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Wallet(Base):
    __tablename__ = 'wallets'

    id: Mapped[int] = mapped_column(primary_key=True)
    e_mail: Mapped[str] = mapped_column(unique=True, index=True)
    private_key: Mapped[str] = mapped_column()
    address: Mapped[str] = mapped_column()
    proxy: Mapped[str] = mapped_column(default=None)
    next_activity_action_time: Mapped[datetime | None] = mapped_column(default=None)


    def __repr__(self):
        return f'[ID: {self.id}] | [{self.address}]'