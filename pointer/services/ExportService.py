import csv
import json
import os
from typing import List

from pointer import db
from pointer.DefaultUtil import get_current_date
from pointer.models.solution import Solution
from pointer.models.solutionexport import Export
from pointer.models.statistics import Statistics
from pointer.models.usercourse import User


def create_csv_solution_export(solutions: List[Solution], current_user: User):
    current_date = get_current_date()
    filename = ('solutionCSV' + str(current_date) + '.csv').replace(" ", "_")
    with open(os.path.join(current_user.get_admin_directory(), filename), 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter='|', quoting=csv.QUOTE_MINIMAL)
        for solution in solutions:
            exercise, lesson, course = solution.exercise, solution.get_lesson(), solution.get_course()
            csv_writer.writerow(
                [solution.author.email] + [course.name] + [lesson.name] + [exercise.name] + [solution.send_date] + [
                    solution.points] + [solution.status])
    export = Export(user_id=current_user.id, file_name=filename, generation_date=current_date, type='csv',
                    format=Export.formats['SOLUTION'])
    db.session.add(export)
    db.session.commit()
    return export


def create_csv_statistics_export(statistics, current_user: User):
    current_date = get_current_date()
    filename = ('statisticsCSV' + str(current_date) + '.csv').replace(" ", "_")
    with open(os.path.join(current_user.get_admin_directory(), filename), 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter='|', quoting=csv.QUOTE_MINIMAL)
        for statistic in statistics:
            statistic_json = json.loads(statistic.replace("\'", "\""))
            csv_writer.writerow(
                [statistic_json['user_email']] + [statistic_json['course_name']] + [statistic_json['course_points']] +
                [statistic_json['user_points']] + [statistic_json['percent_value']])
    export = Export(user_id=current_user.id, file_name=filename, generation_date=current_date, type='csv',
                    format=Export.formats['STATISTICS'])
    db.session.add(export)
    db.session.commit()
    return export
