# -*- coding: utf-8 -*-
from flask import render_template, url_for, request
from flask_login import login_required, current_user
from werkzeug.utils import redirect

from app.admin import bp
from app.models.solution import Solution
from app.models.usercourse import User
from app.services.ExportUtil import get_csv_solution_export, get_csv_statistics_export, get_pdf_solution_export, \
    get_pdf_statistics_export
from app.services.ValidationUtil import validate_role


@bp.route('/export_solutions_csv')
@login_required
def export_solutions_csv():
    validate_role(current_user, User.Roles['ADMIN'])
    solutions = Solution.query.filter(Solution.id.in_(request.args.getlist('ids'))).all()
    export = get_csv_solution_export(solutions, current_user)
    return redirect(url_for('admin.download', domain='export', id=export.id))


@bp.route('/export_statistics_csv')
@login_required
def export_statistics_csv():
    validate_role(current_user, User.Roles['ADMIN'])
    export = get_csv_statistics_export(request.args.getlist('statistics_info'), current_user)
    return redirect(url_for('admin.download', domain='export', id=export.id))


@bp.route('/export_solutions_pdf')
@login_required
def export_solutions_pdf():
    validate_role(current_user, User.Roles['ADMIN'])
    solutions = Solution.query.filter(Solution.id.in_(request.args.getlist('ids'))).all()
    export = get_pdf_solution_export(solutions, current_user)
    return redirect(url_for('admin.download', domain='export', id=export.id))


@bp.route('/export_statistics_pdf')
@login_required
def export_statistics_pdf():
    validate_role(current_user, User.Roles['ADMIN'])
    export = get_pdf_statistics_export(request.args.getlist('statistics_info'), current_user)
    return redirect(url_for('admin.download', domain='export', id=export.id))


@bp.route('/view_exports')
@login_required
def view_exports():
    validate_role(current_user, User.Roles['ADMIN'])
    exports = sorted(current_user.exports, key=lambda export: export.id, reverse=True)
    return render_template('admin/exports.html', exports=exports)
