import os
from shutil import copy2


class FileService:
    @staticmethod
    def prepare_file(solution):
        exercise = solution.template
        module_name = os.path.join(exercise.get_directory(), exercise.test_path)
        copy2(module_name, solution.get_directory())
