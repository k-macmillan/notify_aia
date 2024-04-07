import tomllib
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html

from naia.clients.callback.processing import callback_client
from naia.clients.callback.rest import callback_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, Any]:
    print('Starting app')
    yield
    # Clean up - test with kill -15 (SIGTERM)
    print('cleaning up')
    await callback_client.close_client()


with open('pyproject.toml', 'rb') as f:
    _pyproject_data = tomllib.load(f)


app = FastAPI(
    title='Notify Asynchronous Internal API - naia',
    description='Internal API to make asynchronous HTTP requests',
    version=_pyproject_data['tool']['poetry']['version'],
    contact={
        'name': 'Kyle MacMillan',
        'email': 'kyle.w.macmillan@gmail.com',
    },
    lifespan=lifespan,
    # dependencies=[Depends(validate_client_auth)]),
)


app.include_router(callback_router)


# http://localhost:5309/redoc
# http://localhost:5309/docs
@app.get('/docs', include_in_schema=False)
async def swagger_ui_html() -> Any:
    return get_swagger_ui_html(openapi_url='/openapi.json', title='naia', swagger_favicon_url='')
