import asyncio
import datetime
import pathlib
import sys
from unittest import TestCase

sys.path.append(str(pathlib.Path.cwd() / 'app'))

from utils import MonthIter


class DateTest(TestCase):
    def test_month_iter_ok(self):
        async def get_test_data(*args, **kwargs):
            return [day async for day in MonthIter(*args, **kwargs)]

        start_date = datetime.date(2019, 7, 20)

        month_days = asyncio.run(get_test_data(start_date))

        self.assertEqual(month_days[0], start_date.replace(day=1))
        self.assertEqual(month_days[-1], start_date.replace(day=31))
        self.assertEqual(len(month_days), 31)

    def test_month_inter_not_ok(self):
        start_date = datetime.date

        with self.assertRaises(TypeError):
            MonthIter(start_date.isoformat())
