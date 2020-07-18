
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import render_template, flash, request, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.admin import bp
from app.admin.admin_forms import SolutionForm, SolutionAdminSearchForm
from app.models.usercourse import Course, User
from app.models.solution import Solution
from app.services.QueryUtil import exercise_admin_query
from app.services.ValidationUtil import validate_role, validate_solution_admin


@bp.route('/solutions', methods=['GET', 'POST'])
@login_required
def view_solutions():
    validate_role(current_user, User.Roles['ADMIN'])
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
    validate_solution_admin(current_user, User.Roles['ADMIN'], solution)
    solution_form = SolutionForm(obj=solution, email=solution.author.email, points=solution.points,
                                 admin_ref=(solution.status == solution.Status['REFUSED']))
    if request.method == 'POST' and solution_form.validate_on_submit():
        if solution_form.submit_points.data:
            form_points = solution_form.points.data
            if form_points > solution.exercise.get_max_points():
                flash('Za duża ilość punktów', 'error')
                return redirect(url_for('admin.view_solution', solution_id=solution.id))
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
    validate_solution_admin(current_user, User.Roles['ADMIN'], solution)
    solution.status = solution.Status['REFUSED']
    db.session.commit()
    flash('Odrzucono zadanie', 'message')
    return redirect(url_for('admin.view_solution', solution_id=solution.id))


@bp.route('/approve_solution/<int:solution_id>', methods=['GET', 'POST'])
@login_required
def approve_solution(solution_id):
    solution = Solution.query.filter_by(id=solution_id).first()
    validate_solution_admin(current_user, User.Roles['ADMIN'], solution)
    solution.status = solution.Status['APPROVED']
    user_solutions = solution.exercise.get_user_solutions(solution.user_id)
    user_solutions.remove(solution)
    for user_solution in user_solutions:
        if user_solution.status == Solution.Status['APPROVED']:
            user_solution.status = Solution.Status['NOT_ACTIVE']
    db.session.commit()
    flash('Zaakceptowano zadanie', 'message')
    return redirect(url_for('admin.view_solution', solution_id=solution.id))


@bp.route('/reprocess_solution/<int:solution_id>', methods=['GET', 'POST'])
@login_required
def reprocess_solution(solution_id):
    solution = Solution.query.filter_by(id=solution_id).first()
    validate_solution_admin(current_user, User.Roles['ADMIN'], solution)
    if solution.tasks_finished():
        solution.launch_execute('point_solution', 'Pointing solution')
        flash('Uruchomiono ponowne ocenianie', 'message')
    else:
        flash('Ćwiczenie jest już oceniane', 'error')
    return redirect(url_for('admin.view_solution', solution_id=solution.id))
