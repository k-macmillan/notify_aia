from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Tuple

import pytest
from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
from fastapi.testclient import TestClient

from naia.clients.callback.handlers import CallbackLoggingRoute

if TYPE_CHECKING:
    from naia import Naia


@pytest.fixture()
def callback_setup() -> APIRouter:
    callback_router = APIRouter(
        prefix='/test',
        route_class=CallbackLoggingRoute,
    )

    @callback_router.get('/', status_code=status.HTTP_200_OK)
    async def get_route() -> Dict[str, str]:
        return {'msg': 'Hello World'}

    @callback_router.get('/item/')
    async def get_item_route() -> None:
        raise HTTPException(status_code=404, detail='get_item_route failure test')

    @callback_router.get('/exception/')
    async def get_exception_route() -> None:
        raise ValueError

    return callback_router


@pytest.mark.asyncio
async def test_wb_exercise_happy_path(
    get_app: Naia,
    enc_key: Tuple[str],
    callback_setup: APIRouter,
) -> None:
    get_app.initialize_app(encryption_keys=enc_key, routers=[callback_setup])
    client = TestClient(get_app)

    response = client.get('/test/')
    assert response.status_code == 200
    assert response.json() == {'msg': 'Hello World'}


@pytest.mark.asyncio
async def test_wb_exercise_route_not_found(
    get_app: Naia,
    enc_key: Tuple[str],
    callback_setup: APIRouter,
) -> None:
    get_app.initialize_app(encryption_keys=enc_key, routers=[callback_setup])
    client = TestClient(get_app)

    response = client.get('/test/item/')
    assert response.status_code == 404
    assert response.json() == {'error': 'get_item_route failure test'}


@pytest.mark.asyncio
async def test_wb_exercise_unknown_exception(
    get_app: Naia,
    enc_key: Tuple[str],
    callback_setup: APIRouter,
) -> None:
    get_app.initialize_app(encryption_keys=enc_key, routers=[callback_setup])
    client = TestClient(get_app)

    response = client.get('/test/exception/')
    assert response.status_code == 500
    assert response.json() == {'error': 'Unexpected error'}
