from aiohttp import web
from consts import SETTINGS

import middlewares as md
import settings
import signals
import views
from routes import routes

VIEWS_MOD = views  # только чтобы хоть как то использовать


if __name__ == '__main__':
    app = web.Application(middlewares=[md.headers_prepare_middleware])
    app.add_routes(routes)
    app.on_response_prepare.append(signals.headers_prepare)
    app[SETTINGS] = settings

    web.run_app(app)
