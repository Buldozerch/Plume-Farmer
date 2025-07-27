from curl_cffi.requests import AsyncSession
from curl_cffi import CurlError
import asyncio
from typing import Dict, Tuple, Optional
from loguru import logger
from utils.db_api_async.db_api import Session
from utils.db_api_async.models import User
from utils.resource_manager import ResourceManager
from data.settings import Settings


class BaseHttpClient:
    """Base HTTP client for making requests"""

    def __init__(self, user: User):
        """
        Initialize the base HTTP client

        Args:
            user: User with private key and proxy
        """
        self.user = user
        self.cookies = {}
        # Proxy error counter
        self.proxy_errors = 0
        # Settings for automatic resource error handling
        self.settings = Settings()
        self.max_proxy_errors = self.settings.resources_max_failures
        # Time of last captcha solve
        self.last_captcha_time = None

    async def get_headers(self, additional_headers: Optional[Dict] = None) -> Dict:
        """
        Creates base headers for requests

        Args:
            additional_headers: Additional headers to include

        Returns:
            Formatted headers
        """
        base_headers = {
            "User-Agent": f"{self.user.user_agent}",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Referer": "https://relay.link/bridge/",
            "Content-Type": "application/json",
            "relay-sdk-version": "2.3.0",
            "relay-kit-ui-version": "2.15.7",
            "Origin": "https://relay.link",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
        }
        if additional_headers:
            base_headers.update(additional_headers)

        return base_headers

    async def request(
        self,
        url: str,
        method: str,
        data: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        cookies: Optional[Dict] = None,
        timeout: int = 30,
        retries: int = 5,
    ) -> Tuple[bool, str]:
        """
        Performs an HTTP request with automatic captcha and proxy error handling

        Args:
            url: URL for the request
            method: Request method (GET, POST, etc.)
            data: Form data
            json_data: JSON data
            params: URL parameters
            headers: Additional headers
            timeout: Request timeout in seconds
            retries: Number of retry attempts

        Returns:
            (bool, data): Success status and response data
        """
        if not headers:
            base_headers = await self.get_headers(headers)
        else:
            base_headers = headers

        # Configure request parameters
        request_kwargs = {
            "url": url,
            "proxy": self.user.proxy,
            "headers": base_headers,
            "cookies": self.cookies,
            "timeout": timeout,
        }
        # Add optional parameters
        if json_data is not None:
            request_kwargs["json"] = json_data
        if data is not None:
            request_kwargs["data"] = data
        if params is not None:
            request_kwargs["params"] = params

        response_text = ""
        for attempt in range(retries):
            try:
                async with AsyncSession(impersonate="chrome") as session:
                    resp = await getattr(session, method.lower())(**request_kwargs)

                    response_text = resp.text
                    # Successful response
                    if resp.status_code == 200 or resp.status_code == 202:
                        # Reset proxy error counter on successful request
                        self.proxy_errors = 0
                        self.captcha_errors = 0
                        try:
                            json_resp = resp.json()
                            return True, json_resp
                        except Exception:
                            return True, resp.text

                    else:
                        logger.warning(
                            f"{self.user} received status {resp.status_code}, resp text {response_text}, retry attempt {attempt + 1}/{retries}"
                        )
                        await asyncio.sleep(2**attempt)  # Exponential backoff
                        continue

            except CurlError as e:
                logger.warning(
                    f"{self.user} connection error during request to {url}: {str(e)}"
                )

                # Increment proxy error counter
                if (
                    "proxy" in str(e).lower()
                    or "connection" in str(e).lower()
                    or "connect" in str(e).lower()
                ):
                    self.proxy_errors += 1
                    proxy_error_occurred = True

                    # If error limit exceeded, mark proxy as bad
                    if self.proxy_errors >= self.max_proxy_errors:
                        logger.warning(
                            f"{self.user} proxy error limit exceeded ({self.proxy_errors}/{self.max_proxy_errors}), marking as BAD"
                        )

                        resource_manager = ResourceManager()
                        await resource_manager.mark_proxy_as_bad(self.user.id)

                        # If auto-replace is enabled, try to replace proxy
                        if self.settings.resources_auto_replace:
                            success, message = await resource_manager.replace_proxy(
                                self.user.id
                            )
                            if success:
                                logger.info(
                                    f"{self.user} proxy replaced automatically: {message}"
                                )
                                # Update proxy for current client
                                async with Session() as session:
                                    updated_user = await session.get(User, self.user.id)
                                    if updated_user:
                                        self.user.proxy = updated_user.proxy
                                        # Update proxy in request parameters
                                        request_kwargs["proxy"] = self.user.proxy
                                        # Reset error counter
                                        self.proxy_errors = 0
                            else:
                                logger.error(
                                    f"{self.user} failed to replace proxy: {message}"
                                )

                await asyncio.sleep(2**attempt)  # Exponential backoff
                continue
            except Exception as e:
                logger.error(
                    f"{self.user} unexpected error during request to {url}: {str(e)}"
                )
                return False, str(e)

        return False, response_text
