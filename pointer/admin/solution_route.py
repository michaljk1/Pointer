from flask import render_template, flash, request, redirect, url_for
from flask_login import login_required, current_user

from pointer import db
from pointer.admin import bp
from pointer.admin.admin_forms import SolutionForm, SolutionAdminSearchForm
from pointer.models.usercourse import Course, role
from pointer.models.solution import Solution
from pointer.services.QueryService import exercise_admin_query
from pointer.services.RouteService import validate_exists, validate_role_course, validate_role


@bp.route('/solutions', methods=['GET', 'POST'])
@login_required
def view_solutions():
    validate_role(current_user, role['ADMIN'])
    course, lesson, exercise = request.args.get('course'), request.args.get('lesson'), request.args.get('exercise')
    course_db = Course.query.filter_by(name=course).first()
    solutions = []
    if course is None or lesson is None or exercise is None or course_db is None or course_db not in current_user.courses:
        form = SolutionAdminSearchForm()
    else:
        form = SolutionAdminSearchForm(course=course, lesson=lesson, exercise=exercise)
        solutions = exercise_admin_query(form=form, courses=current_user.get_course_names()).all()
    for course in current_user.courses:
        form.course.choices.append((course.name, course.name))
    if request.method == 'POST' and form.validate_on_submit():
        solutions = exercise_admin_query(form=form, courses=current_user.get_course_names()).all()
    return render_template('admin/solutions.html', form=form, solutions=solutions)


@bp.route('/solution/<int:solution_id>', methods=['GET', 'POST'])
@login_required
def view_solution(solution_id):
    solution = Solution.query.filter_by(id=solution_id).first()
    validate_exists(solution)
    validate_role_course(current_user, role['ADMIN'], solution.get_course())
    solution_form = SolutionForm(obj=solution, email=solution.author.email, points=solution.points,
                                 admin_ref=(solution.status == solution.Status['REFUSED']))
    if request.method == 'POST' and solution_form.validate_on_submit():
        if solution_form.submit_points.data:
            form_points = solution_form.points.data
            if form_points > solution.exercise.get_max_points():
                flash('Za duża ilość punktów', 'error')
                return render_template('admin/solution.html', form=solution_form, solution=solution)
            solution.points = form_points
            flash('Zmieniono ilość punktów', 'message')
        if solution_form.submit_comment.data:
            solution.comment = solution_form.comment.data
            flash('Dodano komentarz', 'message')
        db.session.commit()
        return redirect(url_for('admin.view_solution', solution_id=solution.id))
    return render_template('admin/solution.html', form=solution_form, solution=solution)


@bp.route('/decline_solution/<int:solution_id>', methods=['GET', 'POST'])
@login_required
def decline_solution(solution_id):
    solution = Solution.query.filter_by(id=solution_id).first()
    validate_role_course(current_user, role['ADMIN'], solution.get_course())
    solution.status = solution.Status['REFUSED']
    db.session.commit()
    flash('Odrzucono zadanie', 'message')
    return redirect(url_for('admin.view_solution', solution_id=solution.id))


@bp.route('/approve_solution/<int:solution_id>', methods=['GET', 'POST'])
@login_required
def approve_solution(solution_id):
    solution = Solution.query.filter_by(id=solution_id).first()
    validate_role_course(current_user, role['ADMIN'], solution.get_course())
    solution.status = solution.Status['APPROVED']
    user_solutions = solution.exercise.get_student_solutions(solution.user_id)
    user_solutions.remove(solution)
    for user_solution in user_solutions:
        if user_solution.status == Solution.Status['APPROVED']:
            user_solution.status = Solution.Status['NOT_ACTIVE']
    db.session.commit()
    flash('Zaakceptowano zadanie', 'message')
    return redirect(url_for('admin.view_solution', solution_id=solution.id))
