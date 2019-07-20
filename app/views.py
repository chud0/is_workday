import datetime
import logging

from aiohttp import web

from consts import REQUEST_VALUE, SETTINGS, NON_WORKING_DAYS, ALLOWED_DATE_MIN, ALLOWED_DATE_MAX
from routes import routes
from serializers import is_workday_ser

logger = logging.getLogger('app')


@routes.view(f'/', name='main')
class MainView(web.View):
    async def get(self):
        app_routes = {
            name: f'{self.request.scheme}://{self.request.host}{resource.canonical}'
            for name, resource in self.request.app.router.named_resources().items()
        }
        result = dict(resources=app_routes)
        return web.json_response(result, status=200)


@routes.view(f'/is_workday/{{{REQUEST_VALUE}}}', name='is_workday')
class StationView(web.View):
    async def get(self):
        raw_date: str = self.request.match_info.get(REQUEST_VALUE)

        try:
            parsed_date = self.parse_date(raw_date, self.request.app[SETTINGS].ALLOW_DATE_FORMATS)
            self.check_date_range(parsed_date)
        except ValueError:
            return web.json_response({REQUEST_VALUE: 'Not parsed', 'result': None}, status=400)
        except IndexError:
            return web.json_response({REQUEST_VALUE: 'Date not in calendar range', 'result': None}, status=400)

        result_data = {REQUEST_VALUE: parsed_date, 'result': self.is_workday(parsed_date)}
        result = is_workday_ser.dump(result_data)

        return web.json_response(result, status=200)

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

    def check_date_range(self, date_: datetime.date):
        if self.request.app[ALLOWED_DATE_MIN] <= date_ <= self.request.app[ALLOWED_DATE_MAX]:
            return date_

        raise IndexError

    def is_workday(self, date_: datetime.date):
        logger.debug('check workday, date: %s', date_)
        return date_ not in self.request.app[NON_WORKING_DAYS]
