import datetime
import pathlib
import sys
from json import dumps

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from yarl import URL

sys.path.append(str(pathlib.Path.cwd() / 'app'))

from main import get_application
import views as views
from consts import SETTINGS, NON_WORKING_DAYS, ALLOWED_DATE_MIN, ALLOWED_DATE_MAX

VIEWS_MOD = views  # только чтобы хоть как то использовать


class TestSettings:
    MAIN_DATE_FORMAT = '%Y-%m-%d'
    ALLOW_DATE_FORMATS = [MAIN_DATE_FORMAT, '%Y%m%d']


class MyAppTestCase(AioHTTPTestCase):
    MIN_DATE = datetime.date(2019, 1, 1)
    MAX_DATE = datetime.date(2020, 1, 1)
    WEEKENDS = [datetime.date(2019, 11, 4)]

    async def get_application(self):
        app = get_application()
        app[SETTINGS] = TestSettings
        app[NON_WORKING_DAYS] = {self.MIN_DATE, self.MAX_DATE, *self.WEEKENDS}
        app[ALLOWED_DATE_MIN] = min(app[NON_WORKING_DAYS])
        app[ALLOWED_DATE_MAX] = max(app[NON_WORKING_DAYS])
        return app

    @unittest_run_loop
    async def test_ok(self):
        test_date = datetime.date(2019, 1, 2)
        resp = await self.client.request('GET', f'/v1/day/{test_date.isoformat()}')
        assert resp.status == 200
        text = await resp.text()
        expected_data = dumps(dict(request_date=test_date.isoformat(), result=True, description=None))
        assert expected_data == text

    @unittest_run_loop
    async def test_weekend(self):
        test_date = self.WEEKENDS[0]
        resp = await self.client.request('GET', f'/v1/day/{test_date.isoformat()}')
        assert resp.status == 200
        text = await resp.text()
        expected_data = dumps(dict(request_date=test_date.isoformat(), result=False, description=None))
        assert expected_data == text

    @unittest_run_loop
    async def test_not_in_range_min(self):
        test_date = self.MIN_DATE - datetime.timedelta(days=5)
        resp = await self.client.request('GET', f'/v1/day/{test_date.isoformat()}')
        assert resp.status == 400
        text = await resp.text()
        expected_data = dumps(
            dict(request_date=test_date.isoformat(), result=None, description={'date': ['Not in calendar range']}),
        )
        assert expected_data == text

    @unittest_run_loop
    async def test_bad_format(self):
        test_date = self.MIN_DATE + datetime.timedelta(days=50)
        resp = await self.client.request(
            'GET',
            URL('/v1/day/').with_query(date=datetime.date.strftime(test_date, '%yTTT%duu%m')),
        )
        assert resp.status == 400
        text = await resp.text()
        expected_data = dumps(dict(request_date=None, result=None, description={'date': ['Not a valid date.']}))
        assert expected_data == text

    @unittest_run_loop
    async def test_month_ok(self):
        test_date = self.MIN_DATE
        resp = await self.client.request(
            'GET',
            URL('/v1/month/').with_query(date=test_date.isoformat()),
        )
        assert resp.status == 200
        result = await resp.json()
        assert result['request_date'] == datetime.date.strftime(test_date, '%Y-%m')
        assert len(result['result']) == 31
        assert result['description'] is None

    @unittest_run_loop
    async def test_main_ok(self):
        resp = await self.client.request('GET', URL('/v1/'))
        assert resp.status == 200
