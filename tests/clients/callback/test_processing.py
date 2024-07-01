from typing import Callable, Optional, Tuple
from unittest.mock import MagicMock, patch

import pytest
from pydantic.networks import HttpUrl

from naia.auth.encryption import t_secret_key
from naia.clients.callback.processing import CallbackAsyncClient
from naia.clients.callback.rest import RequestPayload
from naia.naia import Naia


async def initialize_app(
    app: Naia,
    enc_key: Tuple[str],
    legacy_key: Optional[t_secret_key] = '',
) -> None:
    app.initialize_app(
        encryption_keys=enc_key,
        encryption_legacy_key=legacy_key,
    )


@pytest.mark.asyncio
async def test_wb_init_callback_async_client_good() -> None:
    cc = CallbackAsyncClient()
    assert cc.connector is not None


def test_wb_init_callback_async_client_needs_event_loop() -> None:
    # TCP connector cannot make a connection if there is no running loop
    with pytest.raises(RuntimeError, match='no running event loop'):
        CallbackAsyncClient()


@pytest.mark.asyncio
@patch('naia.clients.callback.processing.CallbackAsyncClient.client')
async def test_wb_send_callback_request(
    mock_post: MagicMock,
    delivered_payload: RequestPayload,
    get_app: Naia,
    enc_key: Tuple[str],
    encrypted_str: Callable[[str], str],
) -> None:
    url = HttpUrl('https://localhost/')
    await initialize_app(get_app, enc_key)
    bearer_token = encrypted_str('some bearer token')
    mock_post.return_value = {'status_code': 200}

    await get_app.callback_client.send_callback_request(
        url=url,
        encrypted_token=bearer_token,
        payload=delivered_payload,
    )


@pytest.mark.asyncio
@patch('naia.clients.callback.processing.CallbackAsyncClient.client')
async def test_wb_send_callback_legacy_request(
    mock_post: MagicMock,
    delivered_payload: RequestPayload,
    get_app: Naia,
    enc_key: Tuple[str],
    legacy_verify_str: Callable[[str], str],
) -> None:
    url = HttpUrl('https://localhost/')
    await initialize_app(get_app, enc_key, legacy_key=enc_key[0])
    bearer_token = legacy_verify_str('some bearer token')
    mock_post.return_value = {'status_code': 200}

    await get_app.callback_client.send_callback_request(
        url=url,
        encrypted_token=bearer_token,
        payload=delivered_payload,
        legacy=True,
    )
