import datetime

from aiohttp import web, ClientSession

from consts import REQUEST_VALUE
from routes import routes
from serializers import is_workday_ser
from settings import DATE_FORMAT, CAL_PATH


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
            parsed_date = datetime.datetime.strptime(raw_date.replace('-', ''), DATE_FORMAT)
        except ValueError:
            return web.json_response({REQUEST_VALUE: 'Not parsed', 'result': None}, status=404)

        async with ClientSession() as session:  # for example only!
            async with session.get(f'{CAL_PATH}{parsed_date.strftime(DATE_FORMAT)}') as resp:
                is_workday = await resp.text() == '0'

        result_data = {REQUEST_VALUE: parsed_date, 'result': is_workday}
        result = is_workday_ser.dump(result_data)

        return web.json_response(result, status=200)
