import logging

from aiohttp import web

import middlewares as md
import signals
import views
from consts import SETTINGS, NON_WORKING_DAYS, ALLOWED_DATE_MIN, ALLOWED_DATE_MAX
from routes import routes
from utils import load_data

logger = logging.getLogger('app')

VIEWS_MOD = views  # только чтобы хоть как то использовать


def get_application():
    app = web.Application(middlewares=[md.headers_prepare_middleware, md.catch_errors_middleware])
    app.add_routes(routes)
    app.on_response_prepare.append(signals.headers_prepare)
    return app


if __name__ == '__main__':
    import settings

    app = get_application()
    app[SETTINGS] = settings
    app[NON_WORKING_DAYS] = load_data(settings.DATA_PATH)
    app[ALLOWED_DATE_MIN] = min(app[NON_WORKING_DAYS])
    app[ALLOWED_DATE_MAX] = max(app[NON_WORKING_DAYS])

    web.run_app(app, print=logger.debug, access_log_format='%{X-Real-IP}i %s %Tf "%r" "%{User-Agent}i"')
