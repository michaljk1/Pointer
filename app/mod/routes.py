from flask import url_for, abort, flash, render_template, redirect
from flask_login import current_user, login_required

from app import db
from app.mod.forms import RoleForm
from app.mod import bp
from app.models import role, User
from app.services.RouteService import RouteService


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    RouteService.validate_role(current_user, role['MODERATOR'])
    return redirect(url_for('mod.change_role'))


@bp.route('/roles', methods=['GET', 'POST'])
@login_required
def change_role():
    RouteService.validate_role(current_user, role['MODERATOR'])
    form = RoleForm()
    users, roles = [], []
    for user in User.query.filter(User.role != role['MODERATOR']).all():
        data = (user.email, user.email)
        users.append(data)
    form.email.choices = users
    roles.append([role['ADMIN'], role['ADMIN']])
    roles.append([role['STUDENT'], role['STUDENT']])
    form.roles.choices = roles
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        user.role = form.roles.data
        db.session.commit()
        flash('Zmieniono status')
    return render_template('mod/roles.html', form=form)

