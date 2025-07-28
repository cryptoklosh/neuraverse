import getpass

from cryptography.fernet import InvalidToken
import sys

from loguru import logger

import settings
from data import config

import base64
import hashlib
from cryptography.fernet import Fernet

def _derive_fernet_key(password: bytes) -> bytes:

    digest = hashlib.sha256(password).digest()
    return base64.urlsafe_b64encode(digest)


def set_cipher_suite(password) -> Fernet:
    if settings.PRIVATE_KEY_ENCRYPTION:
        cipher = Fernet(_derive_fernet_key(password))

        config.CIPHER_SUITE = cipher

        return cipher

def get_private_key(enc_value: str) -> str:
    try:
        if settings.PRIVATE_KEY_ENCRYPTION:
            return config.CIPHER_SUITE.decrypt(enc_value.encode()).decode()
        return enc_value
    except InvalidToken:
        raise Exception(f"{enc_value} | wrong password! Decrypt failed")
        #sys.exit(f"{enc_value} | wrong password! Decrypt failed")

def prk_encrypt(value: str) -> str:
    if settings.PRIVATE_KEY_ENCRYPTION:
        return config.CIPHER_SUITE.encrypt(value.encode()).decode()
    return value


def check_encrypt_param(confirm: bool = False, attempts: int = 3):
    if settings.PRIVATE_KEY_ENCRYPTION:

        for try_num in range(1, attempts + 1):
            pwd1 = getpass.getpass(
                "[DECRYPTOR] Enter password (input hidden): "
            ).strip().encode()

            if confirm:
                pwd2 = getpass.getpass(
                    "[DECRYPTOR] Repeat password: "
                ).strip().encode()

                if pwd1 != pwd2:
                    print(f"Passwords do not match (attempt {try_num}/{attempts})\n")
                    continue

            if not pwd1:
                print("Password cannot be empty.\n")
                continue

            return set_cipher_suite(pwd1)

        raise RuntimeError("Password confirmation failed – too many attempts.")