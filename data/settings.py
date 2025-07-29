from libs.eth_async.utils.files import read_json
from libs.eth_async.classes import AutoRepr, Singleton
from data.config import SETTINGS_FILE


class Settings(Singleton, AutoRepr):
    def __init__(self):
        json_data = read_json(path=SETTINGS_FILE)
        if type(json_data) is not dict:
            return

        self.use_withdraw_address = json_data.get("withdraw", True)
        self.use_base_bridge = json_data.get("bridge", {}).get("use_base", True)

        self.use_arbitrum_bridge = json_data.get("bridge", {}).get("use_arbitrum", True)

        self.use_optimism_bridge = json_data.get("bridge", {}).get("use_optimism", True)
        self.max_eth_for_bridge = json_data.get("bridge", {}).get("max_eth_for_bridge", 0.001)
        self.wallet_range_start = (
            json_data.get("wallets", {}).get("range", {}).get("start", 0)
        )
        self.wallet_range_end = (
            json_data.get("wallets", {}).get("range", {}).get("end", 0)
        )

        self.wallet_startup_delay_min = (
            json_data.get("wallets", {}).get("startup_delay", {}).get("min", 5)
        )
        self.wallet_startup_delay_max = (
            json_data.get("wallets", {}).get("startup_delay", {}).get("max", 15)
        )
        self.wallet_transactions_delay_min = (
            json_data.get("wallets", {}).get("transcations_delay", {}).get("min", 0)
        )
        self.wallet_transactions_delay_max = (
            json_data.get("wallets", {}).get("transcations_delay", {}).get("max", 30)
        )

        self.resources_auto_replace = json_data.get("resources", {}).get(
            "auto_replace", True
        )
        self.resources_max_failures = json_data.get("resources", {}).get(
            "max_failures", 3
        )

    def get_withdraw_settings(self) -> tuple:
        return self.use_withdraw_address

    def get_bridge_settings(self) -> tuple:
        return self.use_base_bridge, self.use_arbitrum_bridge, self.use_optimism_bridge

    def get_wallet_startup_delay(self) -> tuple:
        return self.wallet_startup_delay_min, self.wallet_startup_delay_max

    def get_wallet_range(self) -> tuple:
        return self.wallet_range_start, self.wallet_range_end

    def get_wallet_transactins_delay(self) -> tuple:
        return self.wallet_transactions_delay_min, self.wallet_transactions_delay_max

    def get_resource_settings(self) -> tuple:
        return self.resources_auto_replace, self.resources_max_failures
