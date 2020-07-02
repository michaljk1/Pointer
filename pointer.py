from pointer import create_app

app = create_app()


from pointer.models.usercourse import User
from pointer import db
with app.app_context():
    mod = User.query.filter_by(role='MODERATOR').all()
    if len(mod) == 0:
        user = User(email='mod@admin.com', login='moderator', name='Moderator', surname='Moderator',
                    role='MODERATOR', is_confirmed=True)
        user.set_password('admin')
        db.session.add(user)
        db.session.commit()