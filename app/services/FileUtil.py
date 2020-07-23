import os
import shutil


def unpack_file(filename, directory):
    if filename.endswith('.tar.gz') or filename.endswith('.gzip') or filename.endswith('.zip') or filename.endswith(
            '.tar'):
        shutil.unpack_archive(os.path.join(directory, filename), directory)


def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
