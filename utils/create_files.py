from data.config import FILES_DIR
from libs.eth_async.utils.files import touch
import os

REQUIRED_FILES = [
    "privatekeys.txt",
    "proxy.txt",
    "twitter_tokens.txt",
    "discord_tokens.txt",
]

def create_files() -> None:
    touch(path=FILES_DIR)
    for name in REQUIRED_FILES:
        touch(path=os.path.join(FILES_DIR, name), file=True)


create_files()