from dataclasses import dataclass
import random
import asyncio
from web3.types import TxParams
from loguru import logger
from typing import Dict, Optional
from utils.db_api_async.models import User
from libs.eth_async import create_client
from libs.eth_async import TokenAmount, Client


@dataclass
class TransactionResult:
    """Результат выполнения транзакции"""

    success: bool
    tx_hash: Optional[str] = None
    error_message: Optional[str] = None
    receipt: Optional[Dict] = None


class Base:
    def __init__(self, user: User, client: Client) -> None:
        self.user = user
        self.client = client

    async def execute_transaction(
        self,
        tx_params: TxParams,
        activity_type: str = "unknown",
        timeout: int = 180,
        retry_count: int = 0,
    ) -> TransactionResult:
        attempt = 0
        last_error = None

        while attempt <= retry_count:
            try:
                logger.info(
                    f"{self.user} Executing transaction {activity_type}"
                    f"{f' (attempt {attempt + 1})' if attempt > 0 else ''}"
                )
                # Отправляем транзакцию
                tx = await self.client.transactions.sign_and_send(tx_params=tx_params)

                # Ждем подтверждения
                receipt = await tx.wait_for_receipt(self.client, timeout=timeout)

                if receipt and tx.params:
                    # Проверяем статус
                    status = receipt.get("status", 1)
                    if status == 0:
                        raise Exception("Transaction reverted")

                    logger.success(
                        f"{self.client.account.address} Transaction confirmed: 0x{tx.hash.hex() if tx.hash else 0}"
                    )

                    return TransactionResult(
                        success=True,
                        tx_hash=tx.hash.hex() if tx.hash else "0",
                        receipt=receipt,
                    )
                else:
                    raise Exception("Transaction receipt timeout")

            except Exception as e:
                last_error = str(e)
                logger.error(f"Transaction failed on attempt {attempt + 1}: {e}")

                # Проверяем специфичные ошибки
                if "insufficient funds" in str(e).lower():
                    # Не имеет смысла повторять
                    break
                if attempt < retry_count:
                    # Ждем перед повтором
                    await asyncio.sleep(5 * (attempt + 1))

                attempt += 1

        return TransactionResult(
            success=False,
            error_message=last_error or "Unknown error",
        )

    async def approve_token(
        self, token_address: str, spender: str, amount: TokenAmount
    ):
        """
        Универсальный метод для approve токенов
        """

        try:
            # Проверяем текущий allowance
            approved = await self.client.transactions.approved_amount(
                token=token_address, spender=spender
            )

            if approved.Wei >= amount.Wei:
                logger.debug(f"Token already approved: {approved.Ether}")
                return

            logger.info(f"Approving {amount.Ether} tokens for {spender[:10]}...")

            # Делаем infinite approve для удобства
            tx = await self.client.transactions.approve(
                token=token_address,
                spender=spender,
                amount=None,  # Infinite
            )

            receipt = await tx.wait_for_receipt(self.client, timeout=60)
            if receipt:
                logger.success("Token approved successfully")
                await asyncio.sleep(random.randint(5, 8))
            else:
                raise Exception("Approve transaction failed")

        except Exception as e:
            logger.error(f"Approve error: {e}")
            raise
