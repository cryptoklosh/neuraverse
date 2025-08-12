from libs.eth_async.classes import Singleton
from data.config import SETTINGS_FILE
import yaml


class Settings(Singleton):
    def __init__(self):
        with open(SETTINGS_FILE, 'r') as file:
            json_data = yaml.safe_load(file) or {}

        self.private_key_encryption = json_data.get("private_key_encryption", False)
        self.threads = json_data.get("threads", 4)
        self.exact_wallets_to_run = json_data.get("exact_wallets_to_run", [])
        self.shuffle_wallets = json_data.get("shuffle_wallets", True)
        self.hide_wallet_address_log = json_data.get("hide_wallet_address_log", True)
        self.log_level = json_data.get("log_level", "INFO")
        self.sleep_after_each_cycle_hours = json_data.get("sleep_after_each_cycle_hours", 0)
        self.random_pause_between_wallets_min = json_data.get("random_pause_between_wallets",{}).get("min")
        self.random_pause_between_wallets_max = json_data.get("random_pause_between_wallets", {}).get("max")
        self.random_pause_between_actions_min = json_data.get("random_pause_between_actions", {}).get("min")
        self.random_pause_between_actions_max = json_data.get("random_pause_between_actions", {}).get("max")
        self.tg_bot_id = json_data.get("tg_bot_id", "")
        self.tg_user_id = json_data.get("tg_user_id", "")
        self.retry = json_data.get("retry", {})


