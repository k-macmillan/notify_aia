from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Dict, List, Mapping, Optional, Sequence, TypeVar

from fastapi import APIRouter, FastAPI, Response
from fastapi.datastructures import Default
from fastapi.params import Depends
from fastapi.responses import UJSONResponse
from fastapi.utils import generate_unique_id
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.routing import BaseRoute

from naia import __version__
from naia.auth.encryption import init_encryption
from naia.clients.async_client import AsyncClient
from naia.clients.callback.processing import CallbackAsyncClient

if TYPE_CHECKING:
    from contextlib import AbstractAsyncContextManager

    from fastapi.routing import APIRoute

# from fastapi.applications import AppType
AppType = TypeVar('AppType', bound='Naia')


class Naia(FastAPI):
    def __init__(
        self: AppType,
        *,
        debug: bool = False,
        routes: List[BaseRoute] | None = None,
        title: str = 'Notify Asynchronous Internal API - naia',
        summary: str | None = None,
        description: str = 'Internal API to make asynchronous HTTP requests',
        version: str = __version__,
        openapi_url: str | None = '/openapi.json',
        openapi_tags: List[Dict[str, Any]] | None = None,
        servers: List[Dict[str, str | Any]] | None = None,
        dependencies: Sequence[Depends] | None = None,
        default_response_class: type[Response] = Default(UJSONResponse),
        redirect_slashes: bool = True,
        docs_url: str | None = '/docs',
        redoc_url: str | None = '/redoc',
        swagger_ui_oauth2_redirect_url: str | None = '/docs/oauth2-redirect',
        swagger_ui_init_oauth: Dict[str, Any] | None = None,
        middleware: Sequence[Middleware] | None = None,
        exception_handlers: Dict[int | type[Exception], Callable[[Request, Any], Coroutine[Any, Any, Response]]]
        | None = None,
        on_startup: Sequence[Callable[[], Any]] | None = None,
        on_shutdown: Sequence[Callable[[], Any]] | None = None,
        lifespan: Callable[[AppType], AbstractAsyncContextManager[None]]
        | Callable[[AppType], AbstractAsyncContextManager[Mapping[str, Any]]]
        | None = None,
        terms_of_service: str | None = None,
        contact: Dict[str, str | Any] | None = None,
        license_info: Dict[str, str | Any] | None = None,
        openapi_prefix: str = '',
        root_path: str = '',
        root_path_in_servers: bool = True,
        responses: Dict[int | str, Dict[str, Any]] | None = None,
        callbacks: List[BaseRoute] | None = None,
        webhooks: APIRouter | None = None,
        deprecated: bool | None = None,
        include_in_schema: bool = True,
        swagger_ui_parameters: Dict[str, Any] | None = None,
        generate_unique_id_function: Callable[[APIRoute], str] = Default(generate_unique_id),
        separate_input_output_schemas: bool = True,
        **extra: Any,
    ) -> None:
        self.callback_client: CallbackAsyncClient
        self._async_clients: list[AsyncClient] = []

        super().__init__(
            debug=debug,
            routes=routes,
            title=title,
            summary=summary,
            description=description,
            version=version,
            openapi_url=openapi_url,
            openapi_tags=openapi_tags,
            servers=servers,
            dependencies=dependencies,
            default_response_class=default_response_class,
            redirect_slashes=redirect_slashes,
            docs_url=docs_url,
            redoc_url=redoc_url,
            swagger_ui_oauth2_redirect_url=swagger_ui_oauth2_redirect_url,
            swagger_ui_init_oauth=swagger_ui_init_oauth,
            middleware=middleware,
            exception_handlers=exception_handlers,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            lifespan=lifespan,
            terms_of_service=terms_of_service,
            contact=contact,
            license_info=license_info,
            openapi_prefix=openapi_prefix,
            root_path=root_path,
            root_path_in_servers=root_path_in_servers,
            responses=responses,
            callbacks=callbacks,
            webhooks=webhooks,
            deprecated=deprecated,
            include_in_schema=include_in_schema,
            swagger_ui_parameters=swagger_ui_parameters,
            generate_unique_id_function=generate_unique_id_function,
            separate_input_output_schemas=separate_input_output_schemas,
            **extra,
        )

    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AsyncGenerator[Any, Any]:
        print('Starting app')
        yield
        # Clean up - test with kill -15 (SIGTERM)
        print('cleaning up')
        for client in self._async_clients:
            await client.close_client()

    def initialize_app(
        self,
        encryption: dict[str, Any],
        callback_client: Optional[CallbackAsyncClient] = None,
    ) -> 'Naia':
        init_encryption(**encryption)
        self._initialize_callback_client(callback_client)
        return self

    def _initialize_callback_client(
        self,
        callback_client: Optional[CallbackAsyncClient] = None,
    ) -> None:
        if callback_client is None:
            callback_client = CallbackAsyncClient()
        self.callback_client = callback_client
        self._async_clients.append(callback_client)
