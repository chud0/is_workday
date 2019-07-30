import datetime
from typing import NamedTuple, Optional, Any

from marshmallow import Schema, fields, EXCLUDE

from utils.date import parse_date

MAIN_DATE_FORMAT = '%Y%m%d'
ALLOW_DATE_FORMATS = (MAIN_DATE_FORMAT, '%Y-%m-%d')

ALLOW_DATE_MONTH_FORMATS = ('%Y-%m', '%Y%m') + ALLOW_DATE_FORMATS


class BaseResponse(Schema):
    class Meta:
        ordered = True

    request_date = fields.Date()
    result = fields.Bool()
    description = fields.Dict()


class DaySchema(BaseResponse):
    pass


class MonthSchema(BaseResponse):

    request_date = fields.Date(format='%Y-%m')
    result = fields.Nested(DaySchema, many=True)


base_response_ser = BaseResponse(unknown=EXCLUDE)
is_workday_ser = DaySchema(unknown=EXCLUDE)
many_day_ser = MonthSchema(unknown=EXCLUDE)


class MultipleFormatDateField(fields.Date):
    @staticmethod
    def _make_object_from_format(value, data_format):
        return parse_date(value, data_format)


class DayRequest(Schema):
    date = MultipleFormatDateField(format=ALLOW_DATE_FORMATS, required=True)


class MonthRequest(Schema):
    date = MultipleFormatDateField(format=ALLOW_DATE_MONTH_FORMATS, required=True)


month_req_ser = MonthRequest()
day_req_ser = DayRequest()


class IsWDResponse(NamedTuple):
    request_date: Optional[datetime.date] = None
    result: Optional[Any] = None
    description: Optional[str] = None
    status: int = 200

    def get_response(self) -> dict:
        result = self._asdict()
        result.pop('status')
        return result
