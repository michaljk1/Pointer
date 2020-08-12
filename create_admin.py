import sys

from app import db
from pointer import app

with app.app_context():
    from app.models.usercourse import Admin

    admin = Admin(email=sys.argv[1], name=sys.argv[2],
                  surname=sys.argv[3], role='ADMIN', is_confirmed=True)
    admin.set_password(sys.argv[4])
    db.session.add(admin)
    db.session.commit()
