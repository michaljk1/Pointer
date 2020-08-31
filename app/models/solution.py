# -*- coding: utf-8 -*-
import os

from flask import current_app
from sqlalchemy import TEXT

from app import db
from app.models.task import Task
from app.services.DateUtil import get_formatted_date


class Solution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.ForeignKey('exercise.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    send_date = db.Column(db.DateTime, nullable=False)
    points = db.Column(db.Float, nullable=False, default=0)
    filename = db.Column(db.String(100), nullable=False)
    output_file = db.Column(db.String(100))
    attempt = db.Column(db.Integer, nullable=False)
    ip_address = db.Column(db.String(20), nullable=False)
    os_info = db.Column(TEXT, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Oddano')
    tasks = db.relationship('Task', backref='solution', lazy='dynamic')
    error_msg = db.Column(TEXT)
    comment = db.Column(TEXT)
    Status = {
        'SEND': 'Oddano',
        'REFUSED': 'Odrzucono',
        'ALL': 'Dowolny',
        'APPROVED': 'Zaakceptowano',
        'COMPILE_ERROR': 'Error - kompilacja',
        'TEST_ERROR': 'Error - testowanie',
        'TIMEOUT_ERROR': 'Error - timeout',
        'NOT_ACTIVE': 'Nieaktywne'
    }

    def get_student_status(self):
        if not self.exercise.is_finished() and self.status in [self.Status['APPROVED'], self.Status['REFUSED'],
                                                               self.Status['NOT_ACTIVE']]:
            return self.Status['NOT_ACTIVE']
        else:
            return self.status

    def get_student_points(self):
        if self.exercise.is_finished():
            return self.points
        else:
            return '-'

    def get_lesson(self):
        return self.exercise.lesson

    def get_course(self):
        return self.exercise.get_course()

    def get_directory(self):
        return os.path.join(self.exercise.get_directory(), self.author.university_id, str(self.attempt))

    def get_str_send_date(self):
        return get_formatted_date(self.send_date)

    def tasks_finished(self):
        for task in self.tasks:
            if not task.complete:
                return False
        return True

    def enqueue_execution(self):
        method_name = 'point_solution'
        rq_job = current_app.solution_queue.enqueue('app.redis_tasks.' + method_name, self.id)
        task = Task(id=rq_job.get_id(), name=method_name, description='Pointing solution',
                    task_type=Task.Type['SOLUTION'], solution=self)
        db.session.add(task)
        db.session.commit()
        return task

    def test_passed(self, test_points: float):
        self.points += test_points
        self.output_file = None

    def init_pointing(self):
        self.points = 0
        self.status = Solution.Status['SEND']
        self.output_file, self.error_msg = None, None

    def timeout_occurred(self):
        self.error_msg = 'Przekroczono limit czasu podczas testowania'
        self.status = self.Status['TIMEOUT_ERROR']

    def passed_all_tests(self):
        return self.points == self.exercise.get_max_points()
