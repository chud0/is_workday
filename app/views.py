import datetime
import logging
from functools import partial

from aiohttp import web

from consts import REQUEST_VALUE, SETTINGS, NON_WORKING_DAYS, ALLOWED_DATE_MIN, ALLOWED_DATE_MAX, QUERY_WORD_DATE
from routes import routes
from serializers import is_workday_ser, IsWDResponse

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


@routes.view(f'/is_workday/', name='is_workday')
class IsWorkdayView(web.View):
    async def get(self):
        raw_date: str = self.request.query.get(QUERY_WORD_DATE, '')

        try:
            parsed_date = self.parse_date(raw_date, self.request.app[SETTINGS].ALLOW_DATE_FORMATS)
            self.check_date_range(parsed_date)
        except ValueError:
            return json_responder(IsWDResponse(description='ERROR: Not parsed')._asdict(), status=400)
        except IndexError:
            return json_responder(IsWDResponse(description='ERROR: Date not in calendar range')._asdict(), status=400)

        result_data = IsWDResponse(parsed_date, self.is_workday(parsed_date))._asdict()

        return json_responder(result_data, status=200)

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


@routes.view(f'/is_workday/{{{REQUEST_VALUE}}}', name='is_workday_short')
class IsWorkdayShortView(web.View):
    async def get(self):
        raw_date: str = self.request.match_info.get(REQUEST_VALUE)
        location_url = self.request.app.router['is_workday'].url_for()
        location = location_url.update_query({QUERY_WORD_DATE: raw_date})
        raise web.HTTPPermanentRedirect(location=location)
