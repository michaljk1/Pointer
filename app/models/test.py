# -*- coding: utf-8 -*-
import os
from datetime import datetime

from app import db


class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.ForeignKey('exercise.id'))
    output_name = db.Column(db.String(100))
    input_name = db.Column(db.String(100))
    timeout = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Float)
    create_date = db.Column(db.DateTime, nullable=False)

    def get_directory(self):
        return os.path.join(self.solution.get_directory(), 'tests', 'test' + str(datetime.timestamp(self.create_date)))

    def get_course(self):
        return self.solution.get_course()

    def get_input_path(self):
        return os.path.join(self.get_directory(), self.input_name)

    def get_output_path(self):
        return os.path.join(self.get_directory(), self.output_name)
