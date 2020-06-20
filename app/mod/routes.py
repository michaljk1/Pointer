from flask import url_for, abort, flash, render_template, redirect
from flask_login import current_user, login_required
from sqlalchemy import desc

from app import db
from app.mod.forms import RoleForm, LoginInfoForm
from app.mod import bp
from app.models import role, User
from app.services.QueryService import login_query
from app.services.RouteService import validate_role


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    validate_role(current_user, role['MODERATOR'])
    return redirect(url_for('mod.change_role'))


@bp.route('/roles', methods=['GET', 'POST'])
@login_required
def change_role():
    validate_role(current_user, role['MODERATOR'])
    form = RoleForm()
    roles = []
    for user in User.query.filter(User.role != role['MODERATOR']).all():
        form.email.choices.append((user.email, user.email))
    roles.append([role['ADMIN'], role['ADMIN']])
    roles.append([role['STUDENT'], role['STUDENT']])
    form.roles.choices = roles
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        user.role = form.roles.data
        db.session.commit()
        flash('Zmieniono status')
    return render_template('mod/roles.html', form=form)


@bp.route('/logins', methods=['GET', 'POST'])
@login_required
def view_logins():
    validate_role(current_user, role['MODERATOR'])
    form = LoginInfoForm()
    form.email.choices.append(('All', 'All'))
    for user in User.query.filter(User.role == role['ADMIN']).all():
        form.email.choices.append((user.email, user.email))
    if form.validate_on_submit():
        logins = login_query(form, current_user.role).order_by(desc(User.email)).all()
        return render_template('mod/logins.html', form=form, logins=logins)
    return render_template('mod/logins.html', form=form, logins=[])
