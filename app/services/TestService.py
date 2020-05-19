import importlib.util
import unittest
from unittest import TextTestRunner
import os.path

class UnitTestService:
    @staticmethod
    def grade(solution):
        exercise = solution.template
        # module = importlib.util.module_from_spec(spec)
        try:
            full_module_name = solution.get_directory() + ".pointstest"
            spec = importlib.util.spec_from_file_location("pointstest", "/home/michal/python/z6/pointstest.py")
            foo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(foo)
            suite = unittest.TestLoader().loadTestsFromModule(foo)
            results = TextTestRunner(verbosity=2).run(suite)
            if results.testsRun == 0:
                solution.points = 0
            else:
                solution.points = exercise.max_points - len(results.failures)
        except:
            solution.points = 0
