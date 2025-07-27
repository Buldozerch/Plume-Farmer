import os
import random
from typing import List, Tuple, Optional
from loguru import logger
from utils.db_api_async.db_api import Session
from utils.db_api_async.db_activity import DB
from data import config


class ResourceManager:
    """Class for managing resources (proxies, Twitter tokens)"""

    def __init__(self):
        """Initialize the resource manager"""
        pass

    def _load_from_file(self, file_path: str) -> List[str]:
        """
        Loads data from a file

        Args:
            file_path: Path to the file

        Returns:
            List of strings from the file
        """
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            with open(file_path, "r") as file:
                return [line.strip() for line in file if line.strip()]
        return []

    def _save_to_file(self, file_path: str, data: List[str]) -> bool:
        """
        Saves data to a file

        Args:
            file_path: Path to the file
            data: List of strings to save

        Returns:
            Success status
        """
        try:
            with open(file_path, "w") as file:
                for line in data:
                    file.write(f"{line}\n")
            return True
        except Exception as e:
            logger.error(f"Error saving to file {file_path}: {str(e)}")
            return False

    def _get_available_proxy(self) -> Optional[str]:
        """
        Gets an available reserve proxy and removes it from the file

        Returns:
            Proxy or None if none are available
        """
        # Load the list of proxies from the file
        all_proxies = self._load_from_file(config.RESERVE_PROXY_FILE)

        if not all_proxies:
            logger.warning("No available proxies in the file")
            return None

        # Select a random proxy
        proxy = random.choice(all_proxies)

        # Remove the selected proxy from the list
        all_proxies.remove(proxy)

        # Save the updated list back to the file
        if self._save_to_file(config.RESERVE_PROXY_FILE, all_proxies):
            logger.info(
                f"Proxy successfully selected and removed from the file. Remaining: {len(all_proxies)}"
            )
        else:
            logger.warning(f"Failed to update the proxy file, but a proxy was selected")

        return proxy

    async def replace_proxy(self, user_id: int) -> Tuple[bool, str]:
        """
        Replaces a user's proxy

        Args:
            user_id: User ID

        Returns:
            (success, message): Success status and message
        """
        new_proxy = self._get_available_proxy()
        if not new_proxy:
            return False, "No available reserve proxies"

        async with Session() as session:
            db = DB(session)
            success = await db.replace_bad_proxy(user_id, new_proxy)

            if success:
                return True, f"Proxy successfully replaced with {new_proxy}"
            else:
                # Do not return the proxy to the file as it may already be used
                return False, "Failed to replace the proxy"

    async def mark_proxy_as_bad(self, user_id: int) -> bool:
        """
        Marks a user's proxy as bad

        Args:
            user_id: User ID

        Returns:
            Success status
        """
        async with Session() as session:
            db = DB(session)
            return await db.mark_proxy_as_bad(user_id)

    async def get_bad_proxies(self) -> List:
        """
        Gets a list of wallets with bad proxies

        Returns:
            List of wallets
        """
        async with Session() as session:
            db = DB(session)
            return await db.get_wallets_with_bad_proxy()

    async def replace_all_bad_proxies(self) -> Tuple[int, int]:
        """
        Replaces all bad proxies

        Returns:
            (replaced, total): Number of replaced proxies and total number of bad proxies
        """
        replaced = 0

        async with Session() as session:
            db = DB(session)
            bad_proxies = await db.get_wallets_with_bad_proxy()

            for wallet in bad_proxies:
                success, _ = await self.replace_proxy(wallet.id)
                if success:
                    replaced += 1

            return replaced, len(bad_proxies)
