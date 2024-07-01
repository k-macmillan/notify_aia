"""Naia async_client module."""

import asyncio
from abc import ABCMeta
from typing import Optional

import aiohttp
import ujson


class AsyncClient(metaclass=ABCMeta):
    """
    Base class for asynchronous clients using aiohttp.

    Instantiated to avoid event loop issues.
    https://docs.aiohttp.org/en/stable/faq.html#why-is-creating-a-clientsession-outside-of-an-event-loop-dangerous
    """

    def __init__(
        self,
        connector: Optional[aiohttp.TCPConnector] = None,
        timeout: Optional[aiohttp.ClientTimeout] = None,
    ) -> None:
        """Initialize the AsyncClient."""
        self._client: Optional[aiohttp.ClientSession] = None
        default_timeout_total: int = 10
        default_host_pool_size: int = 50
        default_dns_cache_duration: int = 2 * 60

        self.timeout = timeout or aiohttp.ClientTimeout(
            total=default_timeout_total,
        )
        # TCPConnector fails with a deprecation warning if the event loop is not active. assert for lower envs
        assert asyncio.get_running_loop() is not None
        self.connector = connector or aiohttp.TCPConnector(
            # Awaits a future in `connect` of aiohttp.connector.BaseConnector so one bad host does not block all
            limit_per_host=default_host_pool_size,
            ttl_dns_cache=default_dns_cache_duration,
        )

    def __del__(self) -> None:
        """Protection to ensure clients are being closed correctly."""
        assert self._client is None, 'Must call close_client() before exiting the program'

    @property
    def client(self) -> aiohttp.ClientSession:
        """Initializes a ClientSession if necessary and returns it."""
        # Creates the client if it does not exist
        if self._client is None or self._client.closed:
            self._client = aiohttp.ClientSession(
                timeout=self.timeout,
                connector=self.connector,
                json_serialize=ujson.dumps,
            )
            print('Created aiohttp.ClientSession')
        return self._client

    async def close_client(self) -> None:
        """Close the class' aiohttp.ClientSession."""
        if self._client:
            await self._client.close()
            self._client = None
            print('Closed aiohttp.ClientSession')
            # TODO: Remove with aiohttp 4.0 - https://github.com/aio-libs/aiohttp/issues/1925#issuecomment-715977247
            await asyncio.sleep(0.250)
