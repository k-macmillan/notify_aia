"""Naia naia module."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any, Callable, Coroutine, Dict, Iterable, List, Mapping, Optional, Sequence, TypeVar

from fastapi import APIRouter, FastAPI, Response
from fastapi.datastructures import Default
from fastapi.params import Depends
from fastapi.responses import UJSONResponse
from fastapi.utils import generate_unique_id
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.routing import BaseRoute

from notify_aia import __version__
from notify_aia.auth.encryption import init_encryption, t_bytes_str, t_secret_key
from notify_aia.clients.async_client import AsyncClient

if TYPE_CHECKING:  # pragma: no cover
    from contextlib import AbstractAsyncContextManager

    from fastapi.routing import APIRoute

    from notify_aia.clients.callback.processing import CallbackAsyncClient

AppType = TypeVar('AppType', bound='Naia')


class Naia(FastAPI):
    """Wrapper around FastAPI to configure a naia app."""

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
        """Initialize the app."""
        self.callback_client: CallbackAsyncClient
        self._async_clients: List[AsyncClient] = []

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
    async def lifespan(
        self,
        app: FastAPI,
    ) -> AsyncGenerator[Any, Any]:
        """Clean up the app."""
        print('Starting app')
        yield
        # Clean up - test with kill -15 (SIGTERM)
        print('cleaning up')
        for client in self._async_clients:
            await client.close_client()

    def initialize_app(
        self,
        encryption_keys: Iterable[t_bytes_str],
        callback_client: Optional[CallbackAsyncClient] = None,
        routers: Optional[Iterable[APIRouter]] = None,
        encryption_legacy_key: Optional[t_secret_key] = '',
        encryption_legacy_salt: Optional[t_bytes_str] = '',
    ) -> 'Naia':
        """Prepare the app with encryption, callback clients, and routers."""
        init_encryption(
            b64_keys=encryption_keys,
            legacy_key=encryption_legacy_key,
            legacy_salt=encryption_legacy_salt,
        )
        self._initialize_callback_client(callback_client)
        self._initialize_routers(routers)
        return self

    def _initialize_callback_client(
        self,
        callback_client: Optional[CallbackAsyncClient] = None,
    ) -> None:
        """Initialize the default callback client or a custom one derived from CallbackAsyncClient."""
        if callback_client is None:
            # Only import this if it's being used
            from notify_aia.clients.callback.processing import CallbackAsyncClient

            callback_client = CallbackAsyncClient()

        self.callback_client = callback_client
        self._async_clients.append(callback_client)

    def _initialize_routers(
        self,
        routers: Optional[Iterable[APIRouter]] = None,
    ) -> None:
        """Initialize the default callback router or accepts a custom FastAPI APIRouter object."""
        if routers is None:
            # Only import this if it's being used
            from notify_aia.clients.callback.rest import callback_router, set_app

            set_app(self)
            routers = [callback_router]

        for router in routers:
            self.include_router(router)
