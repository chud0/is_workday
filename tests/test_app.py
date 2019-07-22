import datetime
from json import dumps

from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

import app.middlewares as md
import app.signals as signals
import app.views as views
from app.consts import SETTINGS, NON_WORKING_DAYS, ALLOWED_DATE_MIN, ALLOWED_DATE_MAX
from app.routes import routes

VIEWS_MOD = views  # только чтобы хоть как то использовать


class TestSettings:
    MAIN_DATE_FORMAT = '%Y-%m-%d'
    ALLOW_DATE_FORMATS = [MAIN_DATE_FORMAT, '%Y%m%d']


class MyAppTestCase(AioHTTPTestCase):
    MIN_DATE = datetime.date(2019, 1, 1)
    MAX_DATE = datetime.date(2020, 1, 1)
    WEEKENDS = [datetime.date(2019, 11, 4)]

    async def get_application(self):
        app = web.Application(middlewares=[md.headers_prepare_middleware])
        app.add_routes(routes)
        app.on_response_prepare.append(signals.headers_prepare)
        app[SETTINGS] = TestSettings
        app[NON_WORKING_DAYS] = {self.MIN_DATE, self.MAX_DATE, *self.WEEKENDS}
        app[ALLOWED_DATE_MIN] = min(app[NON_WORKING_DAYS])
        app[ALLOWED_DATE_MAX] = max(app[NON_WORKING_DAYS])
        return app

    @unittest_run_loop
    async def test_ok(self):
        test_date = datetime.date(2019, 1, 2)
        resp = await self.client.request('GET', f'/v1/is_workday/{test_date.isoformat()}')
        assert resp.status == 200
        text = await resp.text()
        expected_data = dumps(dict(request_date=test_date.isoformat(), result=True))
        assert expected_data == text

    @unittest_run_loop
    async def test_weekend(self):
        test_date = self.WEEKENDS[0]
        resp = await self.client.request('GET', f'/v1/is_workday/{test_date.isoformat()}')
        assert resp.status == 200
        text = await resp.text()
        expected_data = dumps(dict(request_date=test_date.isoformat(), result=False))
        assert expected_data == text

    @unittest_run_loop
    async def test_not_in_range_min(self):
        test_date = self.MIN_DATE - datetime.timedelta(days=5)
        resp = await self.client.request('GET', f'/v1/is_workday/{test_date.isoformat()}')
        assert resp.status == 400
        text = await resp.text()
        expected_data = dumps(dict(request_date='Date not in calendar range', result=None))
        assert expected_data == text
