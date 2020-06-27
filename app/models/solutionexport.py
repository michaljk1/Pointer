import os

from flask import current_app

from app import db
from app.models.usercourse import User


class Export(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    file_name = db.Column(db.String(100))
    type = db.Column(db.String(10))
    format = db.Column(db.String(10))
    generation_date = db.Column(db.DateTime)
    formats = {
        'SOLUTION': 'SOLUTION',
        'STATISTICS': 'STATISTICS'
    }
    types = {
        'CSV': 'csv',
        'PDF': 'pdf'
    }

    def get_directory(self):
        user = User.query.filter_by(id=self.user_id).first()
        return os.path.join(current_app.instance_path, user.login)