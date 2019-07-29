import datetime
from typing import NamedTuple, Optional, Any

from marshmallow import Schema, fields, EXCLUDE


class DaySchema(Schema):
    class Meta:
        ordered = True

    request_date = fields.Date()
    result = fields.Bool()
    description = fields.String()


class MonthSchema(DaySchema):
    class Meta:
        ordered = True

    request_date = fields.Date(format='%Y-%m')
    result = fields.Nested(DaySchema, many=True)


is_workday_ser = DaySchema(unknown=EXCLUDE)
many_day_ser = MonthSchema(unknown=EXCLUDE)


class IsWDResponse(NamedTuple):
    request_date: Optional[datetime.date] = None
    result: Optional[Any] = None
    description: Optional[str] = None
    status: int = 200

    def get_response(self) -> dict:
        result = self._asdict()
        result.pop('status')
        return result
