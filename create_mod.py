from app import db
from pointer import app

with app.app_context():
    from app.models.usercourse import User

    moderators = User.query.filter_by(role='MODERATOR').all()
    if len(moderators) == 0:
        user = User(email=app.config['MOD_EMAIL'], login=app.config['MOD_LOGIN'], name=app.config['MOD_NAME'],
                    surname=app.config['MOD_SURNAME'], role='MODERATOR', is_confirmed=True)
        user.set_password(app.config['MOD_PASSWORD'])
        db.session.add(user)
        db.session.commit()