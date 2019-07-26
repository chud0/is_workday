import datetime
from typing import NamedTuple, Optional

from marshmallow import Schema, fields, EXCLUDE


class IsWorkdaySchema(Schema):
    class Meta:
        ordered = True

    request_date = fields.Date()
    result = fields.Bool()
    description = fields.String()


is_workday_ser = IsWorkdaySchema(unknown=EXCLUDE)


class IsWDResponse(NamedTuple):
    request_date: Optional[datetime.date] = None
    result: Optional[bool] = None
    description: Optional[str] = None
