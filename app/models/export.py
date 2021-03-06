# -*- coding: utf-8 -*-
import os

from app import db
from app.services.DateUtil import get_formatted_date


class Export(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    file_name = db.Column(db.String(100))
    type = db.Column(db.String(15))
    format = db.Column(db.String(15))
    generation_date = db.Column(db.DateTime)
    formats = {
        'SOLUTION': 'Rozwiązania',
        'STATISTICS': 'Statystyki'
    }
    types = {
        'CSV': 'csv',
        'PDF': 'pdf'
    }

    def get_filename(self):
        return self.file_name

    def get_directory(self):
        return os.path.join(self.user.get_directory())

    def get_str_generation_date(self):
        return get_formatted_date(self.generation_date)
