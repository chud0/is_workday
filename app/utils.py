import csv
import datetime
from collections import OrderedDict
from pathlib import Path
from typing import Iterator

YEAR = 'Год/Месяц'


def load_data(path: Path, delimiter: str = ',', quotechar: str = '"', newline=''):
    result = set()
    with path.open(newline=newline) as csv_file:
        csv_dict_reader: Iterator[OrderedDict] = csv.DictReader(csv_file, delimiter=delimiter, quotechar=quotechar)
        for row in csv_dict_reader:
            year = int(row.pop(YEAR))
            for month_num, str_values in enumerate(row.values(), 1):
                if month_num > 12:
                    continue
                for str_day in str_values.split(','):
                    holiday_maybe = str_day.replace('+', '')
                    if holiday_maybe.isdigit():
                        result.add(datetime.date(year, month_num, int(holiday_maybe)))
        return result
