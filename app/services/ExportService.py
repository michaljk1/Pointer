import csv
import os
from typing import List

from app.models.solutionexport import Export
from app.models.statistics import Statistics


def create_csv_solution_export(solutions, directory, current_date, user_id):
    filename = ('solutionCSV' + str(current_date) + '.csv').replace(" ", "_")
    with open(os.path.join(directory, filename), 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter='|', quoting=csv.QUOTE_MINIMAL)
        for solution in solutions:
            exercise, lesson, course = solution.exercise, solution.get_lesson(), solution.get_course()
            csv_writer.writerow(
                [solution.author.email] + [course.name] + [lesson.name] + [exercise.name] + [solution.send_date] + [
                    solution.points] + [solution.status])
    return Export(user_id=user_id, file_name=filename, generation_date=current_date, type='csv', format=Export.formats['SOLUTIONS'])


def create_csv_sstatistics_export(statistics: List[Statistics], directory, current_date, user_id):
    filename = ('statisticsCSV' + str(current_date) + '.csv').replace(" ", "_")
    with open(os.path.join(directory, filename), 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter='|', quoting=csv.QUOTE_MINIMAL)
        for statistic in statistics:
            csv_writer.writerow(
                [statistic.user_email] + [statistic.course_name] + [statistic.course_points] + [statistic.user_points] + [statistic.get_percent_value()])
    return Export(user_id=user_id, file_name=filename, generation_date=current_date, type='csv', format=Export.formats['STATISTICS'])