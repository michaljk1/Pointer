# TODO
# maksymalna ilosc pamieci
from flask import render_template, url_for, request
from flask_login import login_required, current_user
from sqlalchemy import desc
from pointer.admin import bp
from werkzeug.utils import redirect
from pointer.models.usercourse import role
from pointer.models.export import Export
from pointer.models.solution import Solution
from pointer.services.ExportService import get_csv_solution_export, get_csv_statistics_export, get_pdf_solution_export, \
    get_pdf_statistics_export
from pointer.services.RouteService import validate_role


@bp.route('/export_solutions_csv')
@login_required
def export_solutions_csv():
    validate_role(current_user, role['ADMIN'])
    ids = request.args.getlist('ids')
    solutions = Solution.query.filter(Solution.id.in_(ids)).all()
    export = get_csv_solution_export(solutions, current_user)
    return redirect(url_for('admin.download', domain='export', id=export.id))


@bp.route('/export_statistics_csv')
@login_required
def export_statistics_csv():
    validate_role(current_user, role['ADMIN'])
    export = get_csv_statistics_export(request.args.getlist('statistics_info'), current_user)
    return redirect(url_for('admin.download', domain='export', id=export.id))


@bp.route('/export_solutions_pdf')
@login_required
def export_solutions_pdf():
    validate_role(current_user, role['ADMIN'])
    ids = request.args.getlist('ids')
    solutions = Solution.query.filter(Solution.id.in_(ids)).all()
    export = get_pdf_solution_export(solutions, current_user)
    return redirect(url_for('admin.download', domain='export', id=export.id))


@bp.route('/export_statistics_pdf')
@login_required
def export_statistics_pdf():
    validate_role(current_user, role['ADMIN'])
    export = get_pdf_statistics_export(request.args.getlist('statistics_info'), current_user)
    return redirect(url_for('admin.download', domain='export', id=export.id))


@bp.route('/view_exports')
@login_required
def view_exports():
    validate_role(current_user, role['ADMIN'])
    exports = Export.query.filter_by(user_id=current_user.id).order_by(desc(Export.id)).all()
    return render_template('admin/exports.html', exports=exports)
