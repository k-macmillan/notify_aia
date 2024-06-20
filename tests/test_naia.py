from typing import Tuple

import pytest
from pytest_mock import MockerFixture

from naia import Naia
from naia.clients.async_client import AsyncClient
from naia.clients.callback.processing import CallbackAsyncClient
from naia.clients.callback.rest import callback_router


@pytest.fixture
def naia() -> Naia:
    return Naia()


@pytest.fixture
def keys() -> Tuple[str]:
    return ('YXNkZmFzZGZhc2RmYXNkZmFzZGZhc2RmYXNkZmFzZGY=',)


def test_wb_empty_init(naia: Naia) -> None:
    assert naia is not None


@pytest.mark.asyncio
async def test_wb_naia_init_app(naia: Naia, keys: Tuple[str]) -> None:
    naia.initialize_app(keys)


def test_ut_naia_init_app_no_event_loop(naia: Naia, keys: Tuple[str]) -> None:
    with pytest.raises(RuntimeError, match='no running event loop'):
        naia.initialize_app(keys)


@pytest.mark.asyncio
async def test_wb_naia_lifespan(naia: Naia, keys: Tuple[str]) -> None:
    naia.initialize_app(keys)
    async with naia.lifespan(naia):
        assert naia._async_clients
        # Load a client
        naia._async_clients[0].client
        assert naia._async_clients[0]._client is not None
    # Make sure the clients are closed
    assert naia._async_clients[0]._client is None


@pytest.mark.asyncio
async def test_wb_initialize_app_callback_automatic_setup(naia: Naia, keys: Tuple[str]) -> None:
    naia.initialize_app(keys)
    assert isinstance(naia.callback_client, AsyncClient)
    assert naia._async_clients


@pytest.mark.asyncio
async def test_wb_initialize_app_routers_automatic_setup(naia: Naia, keys: Tuple[str], mocker: MockerFixture) -> None:
    mock_routers = mocker.patch('naia.Naia.include_router')
    naia.initialize_app(keys)
    # Should have one router (the default)
    mock_routers.assert_called_once()


@pytest.mark.asyncio
async def test_ut_callback_automatic_setup(naia: Naia, keys: Tuple[str]) -> None:
    naia.initialize_app(encryption_keys=keys)
    assert isinstance(naia.callback_client, AsyncClient)
    assert naia._async_clients


@pytest.mark.asyncio
async def test_ut_callback_manual_setup(naia: Naia, keys: Tuple[str]) -> None:
    naia.initialize_app(encryption_keys=keys, callback_client=CallbackAsyncClient())
    assert isinstance(naia.callback_client, AsyncClient)
    assert naia._async_clients


@pytest.mark.asyncio
async def test_ut_routers_automatic_setup(naia: Naia, keys: Tuple[str], mocker: MockerFixture) -> None:
    mock_routers = mocker.patch('naia.Naia.include_router')
    naia.initialize_app(encryption_keys=keys)
    # Should have one router (the default)
    mock_routers.assert_called_once()


@pytest.mark.asyncio
async def test_ut_routers_manual_setup(naia: Naia, keys: Tuple[str], mocker: MockerFixture) -> None:
    mock_routers = mocker.patch('naia.Naia.include_router')
    naia.initialize_app(encryption_keys=keys, routers=(callback_router,))
    # Should have one router (the default)
    mock_routers.assert_called_once()
