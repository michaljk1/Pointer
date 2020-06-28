import os
from datetime import datetime

from werkzeug.utils import secure_filename

from pointer import db
from pointer.DefaultUtil import get_current_date
from pointer.models.test import Test


class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'))
    content = db.Column(db.String(500))
    end_date = db.Column(db.DateTime)
    max_attempts = db.Column(db.Integer, default=3)
    program_name = db.Column(db.String(50))
    compile_command = db.Column(db.String(100))
    run_command = db.Column(db.String(100))
    timeout = db.Column(db.Integer, default=0, nullable=False)
    solutions = db.relationship('Solution', backref='exercise', lazy='dynamic')
    tests = db.relationship('Test', backref='executor', lazy='dynamic')

    def get_course(self):
        return self.lesson.course

    def get_directory(self):
        return os.path.join(self.lesson.get_directory(), self.name.replace(" ", "_"))

    def get_max_points(self):
        max_points = 0
        for test in self.tests:
            max_points += test.points
        return max_points

    def get_user_solutions(self, user_id):
        user_solutions = []
        for solution in self.solutions:
            if solution.user_id == user_id:
                user_solutions.append(solution)
        return user_solutions

    def get_max_points(self):
        points = 0
        for test in self.tests:
            points += test.points
        return points

    def create_test(self, input_file, output_file, points):
        input_name, output_name = secure_filename(input_file.filename), secure_filename(output_file.filename)
        test = Test(points=points, input_name=input_name, output_name=output_name, exercise_id=self.id,
                    order=len(self.tests.all()))
        self.tests.append(test)
        test_directory = test.get_directory()
        os.makedirs(test_directory)
        input_file.save(os.path.join(test_directory, input_name))
        output_file.save(os.path.join(test_directory, output_name))

    def is_finished(self):
        current_datetime = get_current_date()
        end_datetime = datetime(year=self.end_date.year, month=self.end_date.month, day=self.end_date.day, hour=self.end_date.hour,
                                minute=self.end_date.minute, tzinfo=current_datetime.tzinfo)
        return current_datetime > end_datetime

