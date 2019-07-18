from marshmallow import Schema, fields, EXCLUDE


class IsWorkdaySchema(Schema):
    class Meta:
        ordered = True

    request_date = fields.Date()
    result = fields.Bool()


is_workday_ser = IsWorkdaySchema(unknown=EXCLUDE)
