import aiohttp
import pytest

from notify_aia.clients.async_client import AsyncClient


@pytest.mark.asyncio
async def test_wb_init_client_no_params() -> None:
    AsyncClient()


@pytest.mark.asyncio
async def test_wb_init_client_with_connector() -> None:
    AsyncClient(connector=aiohttp.TCPConnector())


@pytest.mark.asyncio
async def test_wb_init_client_with_timeout() -> None:
    AsyncClient(timeout=aiohttp.ClientTimeout())


@pytest.mark.asyncio
async def test_wb_init_client_with_connector_and_timeout() -> None:
    AsyncClient(connector=aiohttp.TCPConnector(), timeout=aiohttp.ClientTimeout())


def test_ut_no_event_loop_warning() -> None:
    with pytest.raises(RuntimeError, match='no running'):
        AsyncClient()


@pytest.mark.asyncio
async def test_ut_client_is_created() -> None:
    ac = AsyncClient()
    assert isinstance(ac.client, aiohttp.ClientSession)
    await ac.close_client()


@pytest.mark.asyncio
async def test_ut_client_is_closed() -> None:
    ac = AsyncClient()
    # Start a ClientSession
    assert ac.client is not None
    await ac.close_client()
    assert ac._client is None
