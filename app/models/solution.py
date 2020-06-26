import os
from datetime import datetime

from app import db
from app.DefaultUtil import get_current_date


class Solution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.ForeignKey('exercise.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    send_date = db.Column(db.DateTime)
    points = db.Column(db.Float, nullable=False)
    file_path = db.Column(db.String(100), nullable=False)
    attempt = db.Column(db.Integer, nullable=False)
    ip_address = db.Column(db.String(20), nullable=False)
    os_info = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    Status = {
        'SEND': 'Oddano',
        'REFUSED': 'Odrzucono',
        'ACTIVE': 'Aktywne',
        'ALL': 'Status',
        'COMPILE_ERROR': 'Błąd kompilacji',
        'RUN_ERROR': 'Błąd uruchomienia',
        'ERROR': 'Error',
        'NOT_ACTIVE': 'Nieaktywne'
    }

    def get_lesson(self):
        return self.exercise.lesson

    def get_course(self):
        return self.exercise.lesson.course

    def get_directory(self):
        return os.path.join(self.exercise.get_directory(), self.author.login, str(self.attempt))

    def is_visible(self):
        current_datetime = get_current_date()
        end_date = self.exercise.end_date
        end_datetime = datetime(year=end_date.year, month=end_date.month, day=end_date.day, hour=end_date.hour,
                                minute=end_date.minute, tzinfo=current_datetime.tzinfo)
        return current_datetime > end_datetime
