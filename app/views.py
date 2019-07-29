import datetime
import logging
from functools import partial

from aiohttp import web

from consts import REQUEST_VALUE, SETTINGS, NON_WORKING_DAYS, ALLOWED_DATE_MIN, ALLOWED_DATE_MAX, QUERY_WORD_DATE
from routes import routes
from serializers import is_workday_ser, IsWDResponse, many_day_ser
from utils import MonthIter

logger = logging.getLogger('app')

json_responder = partial(web.json_response, dumps=is_workday_ser.dumps)


@routes.view(f'/', name='main')
class MainView(web.View):
    async def get(self):
        app_routes = {
            name: f'{self.request.scheme}://{self.request.host}{resource.canonical}'
            for name, resource in self.request.app.router.named_resources().items()
        }
        result = dict(resources=app_routes)
        return web.json_response(result, status=200)


class DateBaseView(web.View):
    async def get_iwd_response(self, raw_date):
        try:
            parsed_date = self.parse_date(raw_date, self.request.app[SETTINGS].ALLOW_DATE_FORMATS)
            self.check_date_range(parsed_date)
        except ValueError:
            return IsWDResponse(description='ERROR: Not parsed', status=400)
        except IndexError:
            return IsWDResponse(description='ERROR: Date not in calendar range', status=400)
        else:
            return IsWDResponse(parsed_date, self.is_workday(parsed_date))

    @staticmethod
    def parse_date(str_date: str, allowed_formats) -> datetime.date:
        for date_format in allowed_formats:
            try:
                parsed_date = datetime.datetime.strptime(str_date, date_format)
            except ValueError:
                continue
            else:
                return parsed_date.date()

        raise ValueError

    def check_date_range(self, date_: datetime.date) -> datetime.date:
        if self.request.app[ALLOWED_DATE_MIN] <= date_ <= self.request.app[ALLOWED_DATE_MAX]:
            return date_

        raise IndexError

    def is_workday(self, date_: datetime.date) -> bool:
        logger.debug('check workday, date: %s', date_)
        return date_ not in self.request.app[NON_WORKING_DAYS]


@routes.view(f'/day/', name='day')
class DayView(DateBaseView):
    async def get(self):
        raw_date: str = self.request.query.get(QUERY_WORD_DATE)
        response = await self.get_iwd_response(raw_date)
        return json_responder(response.get_response(), status=response.status)


@routes.view(f'/day/{{{REQUEST_VALUE}}}', name='day_short')
class DayShortView(web.View):
    async def get(self):
        raw_date: str = self.request.match_info.get(REQUEST_VALUE)
        location_url = self.request.app.router['day'].url_for()
        location = location_url.update_query({QUERY_WORD_DATE: raw_date})
        raise web.HTTPPermanentRedirect(location=location)


@routes.view(f'/month/', name='month')
class MonthView(DateBaseView):
    async def get(self):
        raw_date: str = self.request.query.get(QUERY_WORD_DATE)
        parsed_date = self.parse_date(raw_date, self.request.app[SETTINGS].ALLOW_DATE_FORMATS)
        result = [
            (await self.get_iwd_response(str(current_date)))._asdict() async for current_date in MonthIter(parsed_date)
        ]
        response = IsWDResponse(parsed_date, result)
        return web.json_response(response._asdict(), dumps=many_day_ser.dumps, status=200)
