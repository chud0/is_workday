import datetime
import json
import logging
from functools import partial

from aiohttp import web

from consts import REQUEST_VALUE, SETTINGS, NON_WORKING_DAYS, ALLOWED_DATE_MIN, ALLOWED_DATE_MAX, QUERY_WORD_DATE
from routes import routes
from serializers import is_workday_ser, IsWDResponse, many_day_ser, month_req_ser, day_req_ser
from utils import MonthIter

logger = logging.getLogger('app')

json_responder = partial(web.json_response, dumps=is_workday_ser.dumps)


@routes.view('/docs/', name='docs')
class DocsView(web.View):
    async def get(self):
        return web.FileResponse(self.request.app[SETTINGS].DOCS_PATH)


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
    async def get_iwd_response(self, date: datetime.date):
        try:
            self.check_date_range(date)
        except IndexError as e:
            return IsWDResponse(date, description=e.args[0], status=400)
        else:
            return IsWDResponse(date, self.is_workday(date))

    def check_date_range(self, date_: datetime.date) -> datetime.date:
        if self.request.app[ALLOWED_DATE_MIN] <= date_ <= self.request.app[ALLOWED_DATE_MAX]:
            return date_

        raise IndexError(dict(date=['Not in calendar range']))

    def is_workday(self, date_: datetime.date) -> bool:
        logger.debug('check workday, date: %s', date_)
        return date_ not in self.request.app[NON_WORKING_DAYS]


@routes.view(f'/day/', name='day')
class DayView(DateBaseView):
    async def get(self):
        validated_request = day_req_ser.load(self.request.query)
        date = validated_request[QUERY_WORD_DATE]
        response = await self.get_iwd_response(date)
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
        validated_request = month_req_ser.load(self.request.query)
        date = validated_request[QUERY_WORD_DATE]
        result = [(await self.get_iwd_response(current_date))._asdict() async for current_date in MonthIter(date)]
        response = IsWDResponse(date, result)
        return web.json_response(response._asdict(), dumps=many_day_ser.dumps, status=200)
