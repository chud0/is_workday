import json
import logging
from time import monotonic_ns

from aiohttp import web
from aiohttp.web_response import Response
from marshmallow import ValidationError

from serializers import base_response_ser, IsWDResponse

logger = logging.getLogger('app')


@web.middleware
async def headers_prepare_middleware(request, handler):
    time_start = monotonic_ns()

    result: Response = await handler(request)

    result.headers['Duration_ms'] = str((monotonic_ns() - time_start) // 10 ** 6)
    return result


@web.middleware
async def catch_errors_middleware(request, handler):
    try:
        result: Response = await handler(request)
    except ValidationError as e:
        return web.json_response(base_response_ser.dump(IsWDResponse(description=e.args[0])._asdict()), status=400)
    else:
        return result
