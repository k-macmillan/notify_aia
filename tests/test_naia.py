from typing import Tuple

import pytest
from pytest_mock import MockerFixture

from naia import Naia
from naia.clients.async_client import AsyncClient
from naia.clients.callback.processing import CallbackAsyncClient
from naia.clients.callback.rest import callback_router


def test_wb_empty_init(get_app: Naia) -> None:
    assert get_app is not None


@pytest.mark.asyncio
async def test_wb_naia_init_app(get_app: Naia, enc_key: Tuple[str]) -> None:
    get_app.initialize_app(enc_key)


def test_ut_naia_init_app_no_event_loop(get_app: Naia, enc_key: Tuple[str]) -> None:
    with pytest.raises(RuntimeError, match='no running event loop'):
        get_app.initialize_app(enc_key)


@pytest.mark.asyncio
async def test_wb_naia_lifespan(get_app: Naia, enc_key: Tuple[str]) -> None:
    get_app.initialize_app(enc_key)
    async with get_app.lifespan(get_app):
        assert get_app._async_clients
        # Load a client
        get_app._async_clients[0].client
        assert get_app._async_clients[0]._client is not None
    # Make sure the clients are closed
    assert get_app._async_clients[0]._client is None


@pytest.mark.asyncio
async def test_wb_initialize_app_callback_automatic_setup(get_app: Naia, enc_key: Tuple[str]) -> None:
    get_app.initialize_app(enc_key)
    assert isinstance(get_app.callback_client, AsyncClient)
    assert get_app._async_clients


@pytest.mark.asyncio
async def test_wb_initialize_app_routers_automatic_setup(get_app: Naia, enc_key: Tuple[str], mocker: MockerFixture) -> None:
    mock_routers = mocker.patch('naia.Naia.include_router')
    get_app.initialize_app(enc_key)
    # Should have one router (the default)
    mock_routers.assert_called_once()


@pytest.mark.asyncio
async def test_ut_callback_automatic_setup(get_app: Naia, enc_key: Tuple[str]) -> None:
    get_app.initialize_app(encryption_keys=enc_key)
    assert isinstance(get_app.callback_client, AsyncClient)
    assert get_app._async_clients


@pytest.mark.asyncio
async def test_ut_callback_manual_setup(get_app: Naia, enc_key: Tuple[str]) -> None:
    get_app.initialize_app(encryption_keys=enc_key, callback_client=CallbackAsyncClient())
    assert isinstance(get_app.callback_client, AsyncClient)
    assert get_app._async_clients


@pytest.mark.asyncio
async def test_ut_routers_automatic_setup(get_app: Naia, enc_key: Tuple[str], mocker: MockerFixture) -> None:
    mock_routers = mocker.patch('naia.Naia.include_router')
    get_app.initialize_app(encryption_keys=enc_key)
    # Should have one router (the default)
    mock_routers.assert_called_once()


@pytest.mark.asyncio
async def test_ut_routers_manual_setup(get_app: Naia, enc_key: Tuple[str], mocker: MockerFixture) -> None:
    mock_routers = mocker.patch('naia.Naia.include_router')
    get_app.initialize_app(encryption_keys=enc_key, routers=(callback_router,))
    # Should have one router (the default)
    mock_routers.assert_called_once()
