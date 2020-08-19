# -*- coding: utf-8 -*-
from flask import render_template, flash, request, redirect, url_for
from flask_login import login_required, current_user

from app import db
from app.teacher import bp
from app.teacher.teacher_forms import SolutionForm, SolutionTeacherSearchForm
from app.models.solution import Solution
from app.models.usercourse import Course, User
from app.services.QueryUtil import exercise_teacher_query
from app.services.ValidationUtil import validate_role, validate_solution_teacher


@bp.route('/solutions', methods=['GET', 'POST'])
@login_required
def view_solutions():
    validate_role(current_user, User.Roles['TEACHER'])
    course, lesson, exercise = request.args.get('course'), request.args.get('lesson'), request.args.get('exercise')
    course_db = Course.query.filter_by(name=course).first()
    solutions = []
    if course is None or lesson is None or exercise is None or course_db is None or course_db not in current_user.courses:
        form = SolutionTeacherSearchForm()
    else:
        form = SolutionTeacherSearchForm(course=course, lesson=lesson, exercise=exercise)
        solutions = exercise_teacher_query(form=form, courses=current_user.get_course_names()).all()
    for course in current_user.courses:
        form.course.choices.append((course.name, course.name))
    if request.method == 'POST' and form.validate_on_submit():
        solutions = exercise_teacher_query(form=form, courses=current_user.get_course_names()).all()
        if len(solutions) == 0:
            flash('Brak rozwiązań odpowiadających danym kryteriom', 'message')
    return render_template('teacher/solutions.html', form=form, solutions=solutions)


@bp.route('/solution/<int:solution_id>', methods=['GET', 'POST'])
@login_required
def view_solution(solution_id):
    solution = Solution.query.filter_by(id=solution_id).first()
    validate_solution_teacher(current_user, User.Roles['TEACHER'], solution)
    solution_form = SolutionForm(obj=solution, email=solution.author.email, points=solution.points)
    if request.method == 'POST' and solution_form.validate_on_submit():
        if solution_form.submit_points.data:
            form_points = solution_form.points.data
            if form_points > solution.exercise.get_max_points():
                flash('Za duża ilość punktów', 'error')
                return redirect(url_for('teacher.view_solution', solution_id=solution.id))
            solution.points = form_points
            flash('Zmieniono ilość punktów', 'message')
        if solution_form.submit_comment.data:
            solution.comment = solution_form.comment.data
            flash('Dodano komentarz', 'message')
        db.session.commit()
        return redirect(url_for('teacher.view_solution', solution_id=solution.id))
    return render_template('teacher/solution.html', form=solution_form, solution=solution)


@bp.route('/decline_solution/<int:solution_id>', methods=['GET', 'POST'])
@login_required
def decline_solution(solution_id):
    solution = Solution.query.filter_by(id=solution_id).first()
    validate_solution_teacher(current_user, User.Roles['TEACHER'], solution)
    solution.status = solution.Status['REFUSED']
    db.session.commit()
    flash('Odrzucono zadanie', 'message')
    return redirect(url_for('teacher.view_solution', solution_id=solution.id))


@bp.route('/approve_solution/<int:solution_id>', methods=['GET', 'POST', 'UPDATE'])
@login_required
def approve_solution(solution_id):
    solution = Solution.query.filter_by(id=solution_id).first()
    validate_solution_teacher(current_user, User.Roles['TEACHER'], solution)
    prev_active_solution = solution.exercise.get_user_active_solution(user_id=solution.author.id)
    if prev_active_solution is not None:
        prev_active_solution.status = Solution.Status['NOT_ACTIVE']
    solution.status = solution.Status['APPROVED']
    db.session.commit()
    flash('Zaakceptowano zadanie', 'message')
    return redirect(url_for('teacher.view_solution', solution_id=solution.id))


@bp.route('/reprocess_solution/<int:solution_id>', methods=['GET', 'POST'])
@login_required
def reprocess_solution(solution_id):
    solution = Solution.query.filter_by(id=solution_id).first()
    validate_solution_teacher(current_user, User.Roles['TEACHER'], solution)
    if solution.tasks_finished():
        solution.enqueue_execution()
        flash('Uruchomiono ponowne ocenianie', 'message')
    else:
        flash('Program jest już oceniany', 'error')
    return redirect(url_for('teacher.view_solution', solution_id=solution.id))
