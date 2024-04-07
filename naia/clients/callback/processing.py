from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

import aiohttp
from tenacity import (
    AsyncRetrying,
    RetryError,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)
from tenacity.retry import retry_base
from tenacity.stop import stop_base
from tenacity.wait import wait_base

from naia.auth.encryption import decrypt
from naia.clients.async_client import AsyncClient

if TYPE_CHECKING:
    from naia.clients.callback.rest import HttpsUrl, RequestPayload

_RETRY_CRITERIA = retry_if_exception_type(aiohttp.ClientResponseError)

_RETRY_ATTEMPTS: int = 10
_RETRY_STOP = stop_after_attempt(_RETRY_ATTEMPTS)

_RETRY_WAIT = wait_random_exponential(
    multiplier=2.0,
    max=60,
    exp_base=2.0,
    min=0.0,
)


class CallbackAsyncClient(AsyncClient):
    """Make callbacks to Services

    Instantiated to avoid event loop issues.
    https://docs.aiohttp.org/en/stable/faq.html#why-is-creating-a-clientsession-outside-of-an-event-loop-dangerous
    """

    def __init__(
        self,
        connector: Optional[aiohttp.TCPConnector] = None,
        timeout: Optional[aiohttp.ClientTimeout] = None,
    ) -> None:
        self._salt: str = ''
        super().__init__(connector=connector, timeout=timeout)

        # Intialize retry properties
        self.set_retry_criteria()
        self.set_retry_stop()
        self.set_retry_wait()

    def set_retry_criteria(
        self,
        retry_criteria: Optional[retry_base] = None,
    ) -> None:
        self._retry_criteria = retry_criteria or _RETRY_CRITERIA

    def set_retry_stop(
        self,
        stop_criteria: Optional[stop_base] = None,
    ) -> None:
        self._retry_stop = stop_criteria or _RETRY_STOP

    def set_retry_wait(
        self,
        wait_criteria: Optional[wait_base] = None,
    ) -> None:
        self._retry_wait = wait_criteria or _RETRY_WAIT

    def set_salt(
        self,
        salt: str,
    ) -> None:
        """Sets the salt parameter"""
        self._salt = salt

    async def send_callback_request(
        self,
        url: HttpsUrl,
        encrypted_token: str,
        payload: RequestPayload,
        salt: str = '',
    ) -> None:
        """Send status callback to a Service endpoint"""
        try:
            bearer_token: Any = decrypt(encrypted_token, salt or self._salt)
        except RuntimeError:
            # TODO: log and abort
            pass

        try:
            async for post_attempt in AsyncRetrying(
                wait=self._retry_wait,
                stop=self._retry_stop,
                retry=self._retry_criteria,
            ):
                with post_attempt:
                    async with self.client.post(
                        url=str(url),
                        json=payload,
                        headers={
                            'Content-Type': 'application/json',
                            'Authorization': f'Bearer {bearer_token}',
                        },
                    ) as resp:
                        # No need to async/await
                        if resp.ok:
                            print(f'callback processed by {url}')
                        else:
                            self._handle_not_ok_response(resp)
        except RetryError as exc:
            print(
                f'Retried {url} - {exc.last_attempt.attempt_number} times. '
                f'Raised {exc.__cause__.__class__.__name__} - {exc.__cause__}'
            )

    def _handle_not_ok_response(self, resp: aiohttp.ClientResponse) -> None:
        try:
            resp.raise_for_status()
        except aiohttp.ClientResponseError as exc:
            if resp.status >= 500 or resp.status in (408, 429):
                # Retryable
                raise
            else:
                print(f'Non-retryable exception encountered: {exc}')


callback_client = CallbackAsyncClient()
