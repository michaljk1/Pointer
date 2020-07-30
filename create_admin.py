import sys

from app import db
from pointer import app

with app.app_context():
    from app.models.usercourse import User

    admins = User.query.filter_by(role='ADMIN').all()
    user = User(email=sys.argv[1], name=sys.argv[2],
                surname=sys.argv[3], role='ADMIN', is_confirmed=True, index=str(len(admins)+1))
    user.set_password(sys.argv[4])
    db.session.add(user)
    db.session.commit()
