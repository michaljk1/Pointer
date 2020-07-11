import os
import shutil
from datetime import datetime

import pytz


def get_current_date():
    return datetime.now(pytz.timezone('Europe/Warsaw'))


def get_offset_aware(my_datetime: datetime):
    end_datetime = datetime(year=my_datetime.year, month=my_datetime.month, day=my_datetime.day,
                            hour=my_datetime.hour, minute=my_datetime.minute, tzinfo=get_current_date().tzinfo)
    return end_datetime


def unpack_file(filename, solution_directory):
    if filename.endswith('.tar.gz') or filename.endswith('.gzip') or filename.endswith('.zip') or filename.endswith(
            '.tar'):
        shutil.unpack_archive(os.path.join(solution_directory, filename), solution_directory)
