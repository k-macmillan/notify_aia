from typing import Callable, Tuple
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from naia.clients.callback import rest as naia_rest
from naia.clients.callback.processing import CallbackAsyncClient
from naia.naia import Naia


@pytest.mark.asyncio
async def test_wb_get_event_loop() -> None:
    naia_rest._EVENT_LOOP = None
    assert naia_rest.get_event_loop() is not None


@pytest.mark.asyncio
@patch('naia.clients.callback.processing.CallbackAsyncClient.client')
async def test_wb_exercise_happy_path(
    mock_post: MagicMock,
    get_app: Naia,
    enc_key: Tuple[str],
    encrypted_str: Callable[[str], str],
    delivered_payload: naia_rest.RequestPayload,
) -> None:
    get_app.initialize_app(encryption_keys=enc_key)
    client = TestClient(get_app)
    mock_post.return_value = {'message': 'ok'}
    bearer_token = encrypted_str('some bearer token')

    data = {
        'url': 'https://localhost/',
        'encrypted_token': bearer_token,
        'payload': CallbackAsyncClient._convert_model(delivered_payload),
    }

    response = client.post('/callback/send', json=data)
    assert response.status_code == 202
    assert response.json() == {'message': 'Accepted'}
