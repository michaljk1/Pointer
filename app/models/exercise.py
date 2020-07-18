#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from datetime import datetime
from sqlalchemy import TEXT
from werkzeug.utils import secure_filename
from app import db
from app.services.DateUtil import get_current_date, get_offset_aware
from app.models.test import Test


class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'))
    content = db.Column(TEXT)
    end_date = db.Column(db.DateTime)
    max_attempts = db.Column(db.Integer, default=3)
    program_name = db.Column(db.String(50))
    compile_command = db.Column(db.String(100))
    run_command = db.Column(db.String(100), nullable=False)
    is_published = db.Column(db.Boolean, default=False)
    timeout = db.Column(db.Integer, nullable=False)
    interval = db.Column(db.Integer, nullable=False)
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
        return [solution for solution in self.solutions if solution.user_id == user_id]

    def get_user_active_solution(self, user_id):
        for solution in self.solutions:
            if solution.user_id == user_id and solution.status == solution.Status['APPROVED']:
                return solution
        return None

    def create_test(self, input_file, output_file, points):
        input_name, output_name = secure_filename(input_file.filename), secure_filename(output_file.filename)
        test = Test(points=points, input_name=input_name, output_name=output_name, exercise_id=self.id,
                    order=len(self.tests.all()))
        self.tests.append(test)
        db.session.commit()
        test_directory = test.get_directory()
        os.makedirs(test_directory)
        input_file.save(os.path.join(test_directory, input_name))
        output_file.save(os.path.join(test_directory, output_name))

    def is_finished(self):
        return get_current_date() > get_offset_aware(self.end_date)

    def get_end_time(self):
        return str(self.end_date.hour) + ':' + str(self.end_date.minute)

    def values_by_form(self, form, content):
        end_date, end_time = form.end_date.data, form.end_time.data
        end_datetime = datetime(year=end_date.year, month=end_date.month, day=end_date.day, hour=end_time.hour,
                                minute=end_time.minute, second=end_time.second)
        self.max_attempts = form.max_attempts.data
        self.compile_command = form.compile_command.data
        self.end_date = end_datetime
        self.run_command = form.run_command.data
        self.program_name = form.program_name.data
        self.timeout = form.timeout.data
        self.interval = form.interval.data
        self.content = content
