from app import db


class LoginInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ip_address = db.Column(db.String(40), nullable=False)
    login_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), nullable=False)
    Status = {
        'SUCCESS': 'Success',
        'ERROR': 'Error',
        'ALL': 'All'
    }