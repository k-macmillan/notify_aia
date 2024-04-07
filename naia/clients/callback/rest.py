import asyncio
from typing import Optional

from fastapi import APIRouter, status
from pydantic import UUID4, AnyUrl, AwareDatetime, BaseModel, UrlConstraints
from typing_extensions import Annotated, Any

from naia.clients.callback.handlers import CallbackLoggingRoute
from naia.clients.callback.processing import callback_client

EVENT_LOOP = None

callback_router = APIRouter(
    prefix='/callback',
    tags=['callback'],
    # dependencies=[Depends(validate_client_auth)],
    responses={404: {'description': 'Not found'}},
    route_class=CallbackLoggingRoute,
)


HttpsUrl = Annotated[AnyUrl, UrlConstraints(allowed_schemes=['https'])]


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
    url: HttpsUrl
    encrypted_token: str
    payload: RequestPayload

    model_config = {
        'json_schema_extra': {
            'examples': [
                {
                    'url': 'https://example.com/vanotify',
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


def get_event_loop() -> asyncio.AbstractEventLoop:
    global EVENT_LOOP
    if EVENT_LOOP is None:
        EVENT_LOOP = asyncio.get_event_loop()
    return EVENT_LOOP


@callback_router.post('/send', status_code=status.HTTP_202_ACCEPTED, summary='Send a callback')
async def send_callback(
    data: RequestCallback,
    # api_key: str = Security(validate_admin_auth),
) -> ResponseCallback:
    # Do not wait for the response
    get_event_loop().create_task(
        callback_client.send_callback_request(
            data.url,
            data.encrypted_token,
            data.payload,
        )
    )
    return ResponseCallback(message='Accepted')