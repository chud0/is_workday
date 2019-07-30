import datetime
from abc import ABC, abstractmethod
from typing import List


def parse_date(str_date: str, allowed_formats: List[str]) -> datetime.date:
    for date_format in allowed_formats:
        try:
            parsed_date = datetime.datetime.strptime(str_date, date_format)
        except ValueError:
            continue
        else:
            return parsed_date.date()

    raise ValueError


class DateIter(ABC):
    resolution = datetime.timedelta(days=1)

    @abstractmethod
    def get_init_date(self, date: datetime.date) -> datetime.date:
        ...  # pragma: no cover

    @abstractmethod
    def get_target_pattern(self, date: datetime.date) -> int:
        ...  # pragma: no cover

    def __init__(self, target_date: datetime.date):
        self.previous_date = self.get_init_date(target_date) - self.resolution
        self.target_pattern = self.get_target_pattern(target_date)

    def __aiter__(self):
        return self

    async def __anext__(self):
        next_date = self.previous_date + self.resolution
        if self.get_target_pattern(next_date) != self.target_pattern:
            raise StopAsyncIteration
        self.previous_date = next_date
        return next_date


class MonthIter(DateIter):
    def get_init_date(self, date: datetime.date) -> datetime.date:
        return date.replace(day=1)

    def get_target_pattern(self, date: datetime.date) -> int:
        return date.month
