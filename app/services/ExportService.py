import csv
import os

from app.models.solutionexport import SolutionExport


def create_csv_export(solutions, directory, current_date, user_id):
    filename = ('exportCSV' + str(current_date) + '.csv').replace(" ", "_")
    with open(os.path.join(directory, filename), 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter='|', quoting=csv.QUOTE_MINIMAL)
        for solution in solutions:
            exercise, lesson, course = solution.exercise, solution.get_lesson(), solution.get_course()
            csv_writer.writerow(
                [solution.author.email] + [course.name] + [lesson.name] + [exercise.name] + [solution.send_date] + [
                    solution.points] + [solution.status])
    return SolutionExport(user_id=user_id, file_name=filename, generation_date=current_date, type='csv')

