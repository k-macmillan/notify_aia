from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Optional

from fastapi import APIRouter, BackgroundTasks, status
from pydantic import UUID4, AwareDatetime, BaseModel, HttpUrl
from typing_extensions import Any

from naia.clients.callback.handlers import CallbackLoggingRoute

if TYPE_CHECKING:  # pragma: no cover
    from naia.naia import Naia


_EVENT_LOOP = None
_APP: Naia

callback_router = APIRouter(
    prefix='/callback',
    tags=['callback'],
    # dependencies=[Depends(validate_client_auth)],
    responses={404: {'description': 'Not found'}},
    route_class=CallbackLoggingRoute,
)


class RequestPayload(BaseModel):
    notification_id: UUID4
    refererence: Optional[str] = None
    to: str
    status: str
    created_at: AwareDatetime
    completed_at: AwareDatetime
    sent_at: AwareDatetime
    notification_type: str
    status_reason: Optional[str] = None
    provider: Optional[str] = None
    provider_payload: Optional[Any] = None


class RequestCallback(BaseModel):
    url: HttpUrl
    encrypted_token: str
    payload: RequestPayload

    model_config = {
        'json_schema_extra': {
            'examples': [
                {
                    'url': 'https://example.com',
                    'encrypted_token': 'eyJhIjoxMCwiaGVsbG8iOiJieWUiLCJteV9saXN0IjpbMiwzLDUsNywxMV19.H44dU0G4pa7Aom3EgAD1uVAhZUU',
                    'payload': {
                        'notification_id': '2dfc614b-6885-4f78-adf1-8ee4b8d2433b',
                        'to': 'bob@gmail.com',
                        'status': 'delivered',
                        'created_at': '2024-03-10 20:15:34.349640+00:00',
                        'completed_at': '2024-03-10 20:15:34.449798+00:00',
                        'sent_at': '2024-03-10 20:15:34.449798+00:00',
                        'notification_type': 'email',
                    },
                }
            ]
        }
    }


class ResponseCallback(BaseModel):
    message: str


def set_app(app: Naia) -> None:
    global _APP
    _APP = app


def get_event_loop() -> asyncio.AbstractEventLoop:
    global _EVENT_LOOP
    if _EVENT_LOOP is None:
        _EVENT_LOOP = asyncio.get_event_loop()
    return _EVENT_LOOP


@callback_router.post('/send', status_code=status.HTTP_202_ACCEPTED, summary='Send a callback')
async def send_callback(
    data: RequestCallback,
    background_tasks: BackgroundTasks,
    # api_key: str = Security(validate_admin_auth),
) -> ResponseCallback:
    # Do not wait for the response
    background_tasks.add_task(
        _APP.callback_client.send_callback_request,
        url=data.url,
        encrypted_token=data.encrypted_token,
        payload=data.payload,
    )
    return ResponseCallback(message='Accepted')
