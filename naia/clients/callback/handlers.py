from time import monotonic
from typing import Any, Callable, Coroutine, Union

from fastapi import Request
from fastapi.logger import logger
from fastapi.responses import Response
from fastapi.routing import APIRoute


class CallbackLoggingRoute(APIRoute):
    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Union[Response, None]]]:  # type: ignore
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Union[Response, None]:
            status_code = None
            resp = None
            try:
                start = monotonic()
                resp = await original_route_handler(request)
                status_code = resp.status_code
            except Exception as exc:
                logger.critical('UNKNOWN EXCEPTION: %s %s', type(exc).__name__, exc)
            finally:
                logger.info(f'{request.method} {request.url} {status_code} {monotonic() - start:6f}s')
            return resp

        return custom_route_handler
