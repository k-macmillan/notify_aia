"""Naia processing module."""

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

from notify_aia.auth.encryption import decrypt, legacy_verify
from notify_aia.clients.async_client import AsyncClient

if TYPE_CHECKING:  # pragma: no cover
    from pydantic.networks import HttpUrl

    from notify_aia.clients.callback.rest import RequestPayload


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
    """
    Make callbacks to Services.

    Instantiated to avoid event loop issues.
    https://docs.aiohttp.org/en/stable/faq.html#why-is-creating-a-clientsession-outside-of-an-event-loop-dangerous
    """

    def __init__(
        self,
        connector: Optional[aiohttp.TCPConnector] = None,
        timeout: Optional[aiohttp.ClientTimeout] = None,
    ) -> None:
        """Initialize the class."""
        self.legacy_salt: bytes = b'itsdangerous'
        super().__init__(connector=connector, timeout=timeout)

        # Intialize retry properties
        self.set_retry_criteria()
        self.set_retry_stop()
        self.set_retry_wait()

    def set_retry_criteria(
        self,
        retry_criteria: Optional[retry_base] = None,
    ) -> None:
        """Customize retry criteria."""
        self._retry_criteria = retry_criteria or _RETRY_CRITERIA

    def set_retry_stop(
        self,
        stop_criteria: Optional[stop_base] = None,
    ) -> None:
        """Customize stop criteria."""
        self._retry_stop = stop_criteria or _RETRY_STOP

    def set_retry_wait(
        self,
        wait_criteria: Optional[wait_base] = None,
    ) -> None:
        """Customize delay between retries."""
        self._retry_wait = wait_criteria or _RETRY_WAIT

    async def send_callback_request(
        self,
        url: HttpUrl,
        encrypted_token: str,
        payload: RequestPayload,
        legacy_salt: bytes = b'',
        legacy: bool = False,
    ) -> None:
        """Send status callback to a Service endpoint."""
        bearer_token: Any = None

        if legacy:
            bearer_token = legacy_verify(encrypted_token, legacy_salt or self.legacy_salt)
        else:
            bearer_token = decrypt(encrypted_token)

        if bearer_token:
            dict_payload = self._convert_model(payload)
            url_str = str(url)
            try:
                async for post_attempt in AsyncRetrying(
                    wait=self._retry_wait,
                    stop=self._retry_stop,
                    retry=self._retry_criteria,
                ):
                    with post_attempt:
                        print('Making post to: ', url_str)
                        async with self.client.post(
                            url=url_str,
                            json=dict_payload,
                            headers={
                                'Content-Type': 'application/json',
                                'Authorization': f'Bearer {bearer_token}',
                            },
                        ) as resp:
                            await self._handle_response(resp, url_str)
            except RetryError as exc:
                print(
                    f'Retried {url} - {exc.last_attempt.attempt_number} times. '
                    f'Raised {exc.__cause__.__class__.__name__} - {exc.__cause__}'
                )
        else:
            print(f'Unable to send callback to {url} due to invalid bearer_token generation')

    async def _handle_response(self, resp: aiohttp.ClientResponse, url: str) -> None:
        try:
            resp.raise_for_status()
            print(f'Response from {url}: {await resp.text()}')
        except aiohttp.ClientResponseError as exc:
            if resp.status >= 500 or resp.status in (408, 429):
                # Retryable
                raise
            else:
                print(f'Non-retryable exception encountered: {exc}')

    @staticmethod
    def _convert_model(model: RequestPayload) -> dict[str, Any]:
        """Convert fields that cannot be JSON serialized into serializable fields."""
        model_dict = model.model_dump()
        model_dict['notification_id'] = str(model_dict['notification_id'])
        model_dict['created_at'] = str(model_dict['created_at'])
        model_dict['completed_at'] = str(model_dict['completed_at'])
        model_dict['sent_at'] = str(model_dict['sent_at'])

        return model_dict
