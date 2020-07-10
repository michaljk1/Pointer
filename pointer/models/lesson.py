import os

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
        exercise = Exercise(name=form.name.data, lesson_id=self.id)
        exercise.values_by_form(form, content)
        self.exercises.append(exercise)
        os.makedirs(exercise.get_directory())
        return exercise

    def get_course(self):
        return self.course

    def get_exercises(self):
        active_exercises = []
        for exercise in self.exercises:
            if exercise.is_published:
                active_exercises.append(exercise)
        return active_exercises
