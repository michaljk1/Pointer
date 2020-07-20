# !/usr/bin/env python# -*- coding: utf-8 -*-
from datetime import datetime
import pytz


def get_current_date() -> datetime:
    return datetime.now(pytz.timezone('Europe/Warsaw'))


def get_offset_aware(my_datetime: datetime) -> datetime:
    end_datetime = datetime(year=my_datetime.year, month=my_datetime.month, day=my_datetime.day,
                            hour=my_datetime.hour, minute=my_datetime.minute, second=my_datetime.second,
                            tzinfo=get_current_date().tzinfo)
    return end_datetime

