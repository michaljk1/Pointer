from flask import url_for, abort, flash, render_template

from app import db
from app.mod.forms import RoleForm
from app.mod import bp
from app.models import Role, User


@bp.route('/roles', methods=['GET', 'POST'])
def change_role():
    form = RoleForm()
    users, roles = [], []
    for user in User.query.filter(User.role != Role.MODERATOR).all():
        data = (user.email, user.email)
        users.append(data)
    form.email.choices = users
    roles.append([Role.ADMIN, Role.ADMIN])
    roles.append([Role.STUDENT, Role.STUDENT])
    form.roles.choices = roles
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        user.role = form.roles.data
        db.session.commit()
        flash('Zmieniono status')
    return render_template('mod/roles.html', form=form)

