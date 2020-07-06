import os
from datetime import datetime

from sqlalchemy.dialects.mysql import LONGTEXT

from pointer import db
from pointer.models.exercise import Exercise


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    content_text = db.Column(LONGTEXT)
    content_pdf_path = db.Column(db.String(100))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    exercises = db.relationship('Exercise', backref='lesson', lazy='dynamic')

    def get_directory(self):
        return os.path.join(self.course.get_directory(), self.name.replace(" ", "_"))

    def is_exercise_name_proper(self, exercise_name):
        exercise_name = exercise_name.lower()
        for exercise in self.exercises:
            if exercise.name.replace(" ", "_").lower() == exercise_name.replace(" ", "_"):
                return False
        return True

    def create_exercise(self, form, content):
        end_date, end_time = form.end_date.data, form.end_time.data
        end_datetime = datetime(year=end_date.year, month=end_date.month, day=end_date.day, hour=end_time.hour,
                                minute=end_time.minute)
        exercise = Exercise(name=form.name.data, content=content, lesson_id=self.id,
                            max_attempts=form.max_attempts.data, compile_command=form.compile_command.data,
                            end_date=end_datetime, run_command=form.run_command.data,
                            program_name=form.program_name.data, timeout=form.timeout.data, interval=form.interval.data)
        self.exercises.append(exercise)
        os.makedirs(exercise.get_directory())
        return exercise
