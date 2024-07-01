"""Naia handlers module."""

from time import monotonic
from typing import Any, Callable, Coroutine, Union

from fastapi import Request, status
from fastapi.exceptions import HTTPException
from fastapi.logger import logger
from fastapi.responses import JSONResponse, Response
from fastapi.routing import APIRoute


class CallbackLoggingRoute(APIRoute):
    """Simple custom route logging for callbacks."""

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Union[Response, None]]]:  # type: ignore
        """Define custom handling."""
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Union[JSONResponse, Response, None]:
            """Handle route pre and post handling."""
            status_code = None
            resp = None
            try:
                start = monotonic()
                resp = await original_route_handler(request)
                status_code = resp.status_code
            except HTTPException as exc:
                resp = JSONResponse(content={'error': exc.detail}, status_code=exc.status_code)
            except Exception as exc:
                logger.critical('UNKNOWN EXCEPTION: %s %s', type(exc).__name__, exc)
                resp = JSONResponse(
                    content={'error': 'Unexpected error'},
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            finally:
                logger.info(f'{request.method} {request.url} {status_code} {monotonic() - start:6f}s')
            return resp

        return custom_route_handler
