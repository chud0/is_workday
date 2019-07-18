import logging
from time import monotonic_ns

from aiohttp import web
from aiohttp.web_response import Response

logger = logging.getLogger('app')


@web.middleware
async def headers_prepare_middleware(request, handler):
    time_start = monotonic_ns()

    result: Response = await handler(request)

    result.headers['Duration_ms'] = str((monotonic_ns() - time_start) // 10 ** 6)
    return result
