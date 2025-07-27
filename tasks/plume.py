from eth_typing.encoding import HexStr
import json
from libs.eth_async.data.models import TxArgs
from web3.types import TxParams
from data.contracts import Contracts
from tasks.base import Base
from tasks.http_client import BaseHttpClient
from libs.eth_async import TokenAmount
from loguru import logger
import random
from data.settings import Settings
import asyncio


RELAY_URL = "https://api.relay.link/quote"

settings = Settings()


class Bridge(Base, BaseHttpClient):
    def __init__(self, user, client):
        Base.__init__(self, user=user, client=client)  # Прямой вызов Base
        BaseHttpClient.__init__(self, user=user)

    def get_random_id_network_for_withdraw(self):
        network_to_withdraw = []
        network_ids = {"Base": 8453, "Optimism": 10, "Arbitrum": 42161}
        use_base, use_arb, use_op = settings.get_bridge_settings()
        if use_base:
            network_to_withdraw.append("Base")
        if use_arb:
            network_to_withdraw.append("Arbitrum")
        if use_op:
            network_to_withdraw.append("Optimism")
        if not network_to_withdraw:
            raise Exception("No network to withdraw from Plume")
        random.shuffle(network_to_withdraw)
        network_to_withdraw = network_to_withdraw[0]
        network_id = network_ids.get(network_to_withdraw)
        return network_to_withdraw, network_id

    async def bridge_from_plume(self, amount: TokenAmount, to):
        network_name, network_id = self.get_random_id_network_for_withdraw()

        logger.info(f"{self.user} start Bridge {amount.Ether} Plume to {network_name}")
        json_data = {
            "user": f"{self.user.public_key}",
            "originChainId": self.client.network.chain_id,
            "destinationChainId": network_id,
            "originCurrency": "0x0000000000000000000000000000000000000000",
            "destinationCurrency": "0x0000000000000000000000000000000000000000",
            "recipient": f"{to}",
            "tradeType": "EXACT_INPUT",
            "amount": f"{amount.Wei}",
            "referrer": "relay.link",
            "useExternalLiquidity": False,
            "useDepositAddress": False,
            "topupGas": False,
        }
        request, data = await self.request(
            url=RELAY_URL, method="POST", json_data=json_data
        )

        if request and data:
            trans_data = data["steps"][-1]["items"][0]["data"]["data"]  # type: ignore
            to = data["steps"][-1]["items"][0]["data"]["to"]  # type: ignore
            value = data["steps"][-1]["items"][0]["data"]["value"]  # type: ignore
        else:
            raise

        balance = await self.client.wallet.balance()
        bridge_value = TokenAmount(amount=value, wei=True)
        if balance.Wei < bridge_value.Wei:
            logger.error(
                f"{self.user} Not enough Plume For Bridge balance now: {balance}"
            )
            return False

        tx_params = TxParams(
            to=self.client.w3.to_checksum_address(to),
            data=HexStr(trans_data),
            value=bridge_value.Wei,
        )
        bridge_transaction = await self.execute_transaction(
            tx_params=tx_params, activity_type="Bridge_from_plume"
        )
        if bridge_transaction.success:
            return network_name
        else:
            return False

    async def bridge_to_plume(self, amount: TokenAmount):
        logger.info(f"{self.user} start Bridge {amount.Ether} ETH to Plume")
        json_data = {
            "user": f"{self.user.public_key}",
            "originChainId": self.client.network.chain_id,
            "destinationChainId": 98866,
            "originCurrency": "0x0000000000000000000000000000000000000000",
            "destinationCurrency": "0x0000000000000000000000000000000000000000",
            "recipient": f"{self.user.public_key}",
            "tradeType": "EXACT_INPUT",
            "amount": f"{amount.Wei}",
            "referrer": "relay.link",
            "useExternalLiquidity": False,
            "useDepositAddress": False,
            "topupGas": False,
        }
        request, data = await self.request(
            url=RELAY_URL, method="POST", json_data=json_data
        )

        if request and data:
            trans_data = data["steps"][-1]["items"][0]["data"]["data"]  # type: ignore
            to = data["steps"][-1]["items"][0]["data"]["to"]  # type: ignore
            value = data["steps"][-1]["items"][0]["data"]["value"]  # type: ignore
        else:
            raise

        balance = await self.client.wallet.balance()
        bridge_value = TokenAmount(amount=value, wei=True)
        if balance.Wei < bridge_value.Wei:
            logger.error(
                f"{self.user} Not enough ETH For Bridge balance now: {balance}"
            )
            return False

        tx_params = TxParams(
            to=self.client.w3.to_checksum_address(to),
            data=HexStr(trans_data),
            value=bridge_value.Wei,
        )
        bridge_transaction = await self.execute_transaction(
            tx_params=tx_params, activity_type="Bridge_to_plume"
        )
        if bridge_transaction.success:
            return True
        else:
            return False


class PlumeSwap(Base, BaseHttpClient):
    def __init__(self, user, client):
        Base.__init__(self, user=user, client=client)  # Прямой вызов Base
        BaseHttpClient.__init__(self, user=user)

    async def unwrap_plume(self):
        contract = await self.client.contracts.get(contract_address=Contracts.WPLUME)
        amount_wplume = await self.client.wallet.balance(token=contract.address)
        if amount_wplume.Wei > 0:
            logger.info(f"{self.user} start Swap {amount_wplume.Ether} Wplume to Plume")
            swap_params = TxArgs(amount=amount_wplume.Wei)

            data = contract.encode_abi("withdraw", args=(swap_params.tuple()))
            tx_params = TxParams(
                to=contract.address,
                data=data,
            )
            swap_transaction = await self.execute_transaction(
                tx_params=tx_params, activity_type="Swap_to_PLUME"
            )
            if swap_transaction.success:
                return True
            else:
                return False

    async def swap_plume(self):
        contract = await self.client.contracts.get(contract_address=Contracts.WPLUME)
        amount_wplume = await self.client.wallet.balance(token=contract.address)
        if amount_wplume.Wei > 0:
            logger.info(f"{self.user} start Swap {amount_wplume.Ether} Wplume to Plume")
            swap_params = TxArgs(amount=amount_wplume.Wei)

            data = contract.encode_abi("withdraw", args=(swap_params.tuple()))
            tx_params = TxParams(
                to=contract.address,
                data=data,
            )
            swap_transaction = await self.execute_transaction(
                tx_params=tx_params, activity_type="Swap_to_PLUME"
            )
            if swap_transaction.success:
                return True
            else:
                return False
        else:
            amount = await self.client.wallet.balance()
            random_procent = random.uniform(0.3, 0.5)
            amount = int(amount.Wei * random_procent)
            amount = TokenAmount(amount=amount, wei=True)
            logger.info(f"{self.user} start Swap {amount.Ether} Plume to WPlume")

            data = contract.encode_abi(
                "deposit",
            )
            tx_params = TxParams(
                to=contract.address,
                data=data,
                value=amount.Wei,
            )
            swap_transaction = await self.execute_transaction(
                tx_params=tx_params, activity_type="Swap_to_WPLUME"
            )
            if swap_transaction.success:
                return True
            else:
                return False
