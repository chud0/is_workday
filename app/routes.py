from typing import Any

from aiohttp import web

API_VERSION = 'v1'


class VersionedRouteTableDef(web.RouteTableDef):
    def __init__(self, api_version: str):
        self.api_version = api_version

        super().__init__()

    def view(self, path: str, **kwargs: Any):
        path = f'/{self.api_version}{path}'
        return super().view(path, **kwargs)


routes = VersionedRouteTableDef(API_VERSION)
