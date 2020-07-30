# -*- coding: utf-8 -*-
from app import db
from app.services.DateUtil import get_formatted_date


class LoginInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ip_address = db.Column(db.String(40), nullable=False)
    login_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    Status = {
        'SUCCESS': 'Sukces',
        'ERROR': 'Error',
        'ALL': 'Dowolny'
    }

    def get_str_login_date(self):
        return get_formatted_date(self.login_date)
