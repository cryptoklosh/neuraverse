from utils.db_api.models import Base, Wallet
from utils.db_api.db import DB

from data.config import WALLETS_DB


def get_wallets(sqlite_query: bool = False) -> list[Wallet]:
    if sqlite_query:
        return db.execute('SELECT * FROM wallets')

    return db.all(entities=Wallet)


def get_wallet(e_mail: str, sqlite_query: bool = False) -> Wallet | None:
    if sqlite_query:
        return db.execute('SELECT * FROM wallets WHERE private_key = ?', (e_mail,), True)

    return db.one(Wallet, Wallet.e_mail == e_mail)


db = DB(f'sqlite:///{WALLETS_DB}', echo=False, pool_recycle=3600, connect_args={'check_same_thread': False})
db.create_tables(Base)
