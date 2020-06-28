import os
import shutil
from datetime import datetime

import pytz


def get_current_date():
    return datetime.now(pytz.timezone('Europe/Warsaw'))


def unpack_file(filename, solution_directory):
    if filename.endswith('.tar.gz') or filename.endswith('.gzip') or filename.endswith('.zip') or filename.endswith('.tar'):
        shutil.unpack_archive(os.path.join(solution_directory, filename), solution_directory)
