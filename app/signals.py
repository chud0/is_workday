from aiohttp import hdrs


async def headers_prepare(request, response):
    response.headers[hdrs.SERVER] = '---------*----------'
