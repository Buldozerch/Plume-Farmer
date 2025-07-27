import os
from loguru import logger
import asyncio
import random
from libs.eth_async import create_client
from libs.eth_async import TokenAmount
from fake_useragent import UserAgent
from tasks.plume import Bridge, PlumeSwap
from utils.resource_manager import ResourceManager
from libs.eth_async.utils.utils import parse_proxy
from utils.db_api_async.db_api import Session
from utils.db_api_async.db_activity import DB
from utils.db_api_async.models import User
from data import config
from data.settings import Settings

settings = Settings()

# Загружаем данные из файлов
private_file = config.PRIVATE_FILE
if os.path.exists(private_file):
    with open(private_file, "r") as private_file:
        private = [line.strip() for line in private_file if line.strip()]
else:
    private = []

proxy_file = config.PROXY_FILE
if os.path.exists(proxy_file):
    with open(proxy_file, "r") as proxy_file:
        proxys = [line.strip() for line in proxy_file if line.strip()]
else:
    proxys = []

MINIMAL_BALANCE_FOR_WORK = 0.0008


async def add_wallets_db():
    if not private:
        logger.error("Not private keys in files/private.txt")
        return

    logger.info(f"Importing {len(private)} wallets in database")
    for i in range(len(private)):
        user_agent = UserAgent(platforms="desktop")
        private_key = private[i]
        proxy = proxys[i] if i < len(proxys) else None
        proxy = parse_proxy(proxy) if proxy else None

        try:
            client = create_client(private_key=private_key)
            public_key = client.account.address

            async with Session() as session:
                db = DB(session=session)
                success = await db.add_wallet(
                    private_key=private_key,
                    public_key=public_key,
                    proxy=proxy,
                    user_agent=user_agent.random,
                )

                if success:
                    logger.success(f"Wallet {public_key} add in database")
                else:
                    logger.warning(f"Wallet {public_key} already in database")
        except Exception as e:
            logger.error(f"Error with add wallet: {str(e)}")

    logger.success("Import wallets success")
    return


async def main_process(user: User):
    user = user
    startup_min, startup_max = settings.get_wallet_startup_delay()
    time_for_sleep = random.uniform(startup_min, startup_max)
    logger.info(f"Start wallet {user} after {int(time_for_sleep)} seconds.")
    await asyncio.sleep(time_for_sleep)
    bridge = await process_bridge(user=user)
    if not bridge:
        logger.error(f"{user} can't bridge")
        return False
    swaps = await process_swap(user=user)
    if swaps:
        logger.success(f"{user} work done")
        return True


async def get_random_network_for_bridge(user: User):
    use_base, use_arbitrum, use_optimism = settings.get_bridge_settings()

    balance_ready_for_work = []
    if use_base:
        client_base = create_client(
            private_key=user.private_key, network="Base", proxy=user.proxy
        )
        balance_base = await client_base.wallet.balance()
        await client_base.close()
        if balance_base.Ether >= MINIMAL_BALANCE_FOR_WORK:
            balance_ready_for_work.append("Base")
    if use_arbitrum:
        client_arb = create_client(
            private_key=user.private_key, network="Arbitrum", proxy=user.proxy
        )
        balance_arb = await client_arb.wallet.balance()
        await client_arb.close()

        if balance_arb.Ether >= MINIMAL_BALANCE_FOR_WORK:
            balance_ready_for_work.append("Arbitrum")
    if use_optimism:
        client_op = create_client(
            private_key=user.private_key, network="Optimism", proxy=user.proxy
        )
        balance_op = await client_op.wallet.balance()
        await client_op.close()
        if balance_op.Ether >= MINIMAL_BALANCE_FOR_WORK:
            balance_ready_for_work.append("Optimism")
    if balance_ready_for_work:
        random.shuffle(balance_ready_for_work)
        return balance_ready_for_work[0]
    else:
        return False


async def check_plume_balance(user: User):
    client_plume = create_client(
        private_key=user.private_key, network="Plume", proxy=user.proxy
    )
    balance_plume = TokenAmount(0)
    resource_manager = ResourceManager()
    proxy_errors = 0
    auto_replace, max_failures = settings.get_resource_settings()
    for _ in range(max_failures):
        try:
            balance_plume = await client_plume.wallet.balance()
            break

        except Exception as e:
            proxy_errors += 1
            logger.warning(f"{user} Maybe proxy trouble {e}")

            # Добавляем задержку после ошибки
            error_delay = random.uniform(2, 3)
            logger.info(f"{user} delay {error_delay:.1f} seconds. after error")
            await asyncio.sleep(error_delay)

            if proxy_errors >= 3:
                await resource_manager.mark_proxy_as_bad(user.id)

                if auto_replace:
                    success, message = await resource_manager.replace_proxy(user.id)
                    if success:
                        logger.info(f"{user} proxy replaced: {message}, try again...")

                        async with Session() as session:
                            db = DB(session=session)
                            user = await db.get_user(user_id=user.id)

                        continue
                    else:
                        logger.error(
                            f"{user} can't replace proxy: {message} try again after 120 seconds"
                        )
                        await asyncio.sleep(120)
                        continue
            else:
                continue
    if balance_plume.Ether > 5:
        return True
    else:
        return False


async def process_bridge(user: User, delay: bool = False):
    user = user
    if await check_plume_balance(user=user):
        logger.info(f"{user} already have balance in Plume")
        return True
    if delay:
        startup_min, startup_max = settings.get_wallet_startup_delay()
        time_for_sleep = random.uniform(startup_min, startup_max)
        logger.info(f"Start wallet {user} after {int(time_for_sleep)} seconds.")
        await asyncio.sleep(time_for_sleep)
    network = await get_random_network_for_bridge(user=user)
    if not network:
        raise Exception("Wallet don't have balance in any Network for bridge")
    client = create_client(
        private_key=user.private_key, network=network, proxy=user.proxy
    )

    auto_replace, max_failures = settings.get_resource_settings()
    for _ in range(max_failures):
        try:
            balance = await client.wallet.balance()
            bridge = Bridge(user=user, client=client)
            balance = int(balance.Wei * 0.95)
            amount = TokenAmount(amount=balance, wei=True)
            bridge = await bridge.bridge_to_plume(amount=amount)
            if bridge:
                while True:
                    plume_balance = await check_plume_balance(user=user)
                    if plume_balance:
                        logger.success(f"{user} Plume Arrived!")
                        return True
                    else:
                        logger.info(f"{user} wait for Plume Arrived")
                        await asyncio.sleep(5)
                        continue
            return True
        except Exception as e:
            logger.error(f"{user} error with bridge to Plume {e}")
            random_time_for_sleep = random.randint(0, 30)
            logger.warning(
                f"{user} sleep {random_time_for_sleep} seconds before new try"
            )
            await asyncio.sleep(random_time_for_sleep)
            continue
    return False


async def process_swap(user: User, delay: bool = False):
    if not await check_plume_balance(user=user):
        logger.info(f"{user} don't have balance in Plume")
        return False
    if delay:
        startup_min, startup_max = settings.get_wallet_startup_delay()
        time_for_sleep = random.uniform(startup_min, startup_max)
        logger.info(f"Start wallet {user} after {int(time_for_sleep)} seconds.")
        await asyncio.sleep(time_for_sleep)
    client = create_client(
        private_key=user.private_key, network="Plume", proxy=user.proxy
    )
    auto_replace, max_failures = settings.get_resource_settings()
    resource_manager = ResourceManager()
    proxy_errors = 0
    auto_replace, max_failures = settings.get_resource_settings()
    while True:
        nonce = 0
        try:
            nonce = await client.wallet.nonce()
            logger.info(f"{user} have {nonce} transactions in Plume")

        except Exception as e:
            proxy_errors += 1
            logger.warning(f"{user} Maybe proxy trouble {e}")

            # Добавляем задержку после ошибки
            error_delay = random.uniform(2, 3)
            logger.info(f"{user} delay {error_delay:.1f} seconds. after error")
            await asyncio.sleep(error_delay)

            if proxy_errors >= 3:
                await resource_manager.mark_proxy_as_bad(user.id)

                if auto_replace:
                    success, message = await resource_manager.replace_proxy(user.id)
                    if success:
                        logger.info(f"{user} proxy replaced: {message}, try again...")

                        async with Session() as session:
                            db = DB(session=session)
                            user = await db.get_user(user_id=user.id)

                        continue
                    else:
                        logger.error(
                            f"{user} can't replace proxy: {message} try again after 120 seconds"
                        )
                        await asyncio.sleep(120)
                        continue
            else:
                continue

        if int(nonce) >= 400:
            logger.success(f"{user} already have {nonce} transactions")
            return True
        swap = PlumeSwap(user=user, client=client)
        await swap.swap_plume()
        min_sleep, max_sleep = settings.get_wallet_transactins_delay()
        random_sleep = random.randint(min_sleep, max_sleep)
        logger.info(f"{user} sleep {random_sleep} seconds before next swap")
        await asyncio.sleep(random_sleep)
        continue


async def process_tasks(specific_task: str):
    try:
        async with Session() as session:
            db = DB(session=session)
            all_wallets = await db.get_all_wallets()

        if not all_wallets:
            logger.error("Not wallets in Data Base. Import first")
            return

        wallet_start, wallet_end = settings.get_wallet_range()
        if wallet_end > 0 and wallet_end <= len(all_wallets):
            wallets = all_wallets[wallet_start:wallet_end]
        else:
            wallets = all_wallets[wallet_start:]

        logger.info(f"Found {len(all_wallets)} wallets")
        logger.info(
            f"Will be processed {len(wallets)} wallets (from {wallet_start + 1} to {wallet_start + len(wallets)})"
        )

        random.shuffle(wallets)

        tasks = []

        if specific_task == "main":
            for i, wallet in enumerate(wallets):
                task = asyncio.create_task(main_process(wallet))
                tasks.append(task)

        elif specific_task == "bridge":
            for i, wallet in enumerate(wallets):
                task = asyncio.create_task(process_bridge(wallet, delay=True))
                tasks.append(task)

        elif specific_task == "swaps":
            for i, wallet in enumerate(wallets):
                task = asyncio.create_task(process_swap(wallet, delay=True))
                tasks.append(task)

        if not tasks:
            logger.warning("Not wallets for process")
            return

        results = await asyncio.gather(*tasks, return_exceptions=True)

        success_count = sum(1 for result in results if result is True)
        error_count = sum(
            1 for result in results if isinstance(result, Exception) or result is False
        )

        logger.info(f"Process done: success {success_count}, with wrong {error_count}")

    except Exception as e:
        logger.error(f"Wrong: {str(e)}")
