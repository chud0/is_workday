from aiohttp import web

import middlewares as md
import settings
import signals
import views
from consts import SETTINGS, NON_WORKING_DAYS
from routes import routes
from utils import load_data

VIEWS_MOD = views  # только чтобы хоть как то использовать


if __name__ == '__main__':
    app = web.Application(middlewares=[md.headers_prepare_middleware])
    app.add_routes(routes)
    app.on_response_prepare.append(signals.headers_prepare)
    app[SETTINGS] = settings
    app[NON_WORKING_DAYS] = load_data(settings.DATA_PATH)

    web.run_app(app)
