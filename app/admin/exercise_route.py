
# -*- coding: utf-8 -*-
import shutil
from flask import render_template, url_for, flash, request
from flask_login import login_required, current_user
from app.admin import bp
from app.admin.admin_forms import ExerciseForm, TestForm, ExerciseEditForm
from werkzeug.utils import redirect
from app.models.test import Test
from app.models.usercourse import User
from app.models.lesson import Lesson
from app.models.exercise import Exercise
from app import db
from app.services.SolutionUtil import add_solution
from app.services.ValidationUtil import validate_exercise_admin, validate_test, validate_lesson
from app.student.student_forms import UploadForm


@bp.route('/exercise/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def view_exercise(exercise_id):
    exercise = Exercise.query.filter_by(id=exercise_id).first()
    validate_exercise_admin(current_user, User.Roles['ADMIN'], exercise)
    solutions = sorted(exercise.get_user_solutions(current_user.id), key=lambda sol: sol.send_date, reverse=True)
    form = UploadForm()
    if request.method == 'POST' and form.validate_on_submit():
        add_solution(exercise=exercise, current_user=current_user, file=request.files['file'],
                     ip_address=request.remote_addr, attempt_nr=(1+len(solutions)), os_info=str(request.user_agent))
        return redirect(url_for('admin.view_exercise', exercise_id=exercise.id))
    return render_template('admin/exercise.html', exercise=exercise, form=form, solutions=solutions)


@bp.route('/activate_exercise/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def activate_exercise(exercise_id):
    exercise: Exercise = Exercise.query.filter_by(id=exercise_id).first()
    validate_exercise_admin(current_user, User.Roles['ADMIN'], exercise)
    exercise.is_published = not exercise.is_published
    db.session.commit()
    flash('Zapisano zmiany', 'message')
    return redirect(url_for('admin.view_exercise', exercise_id=exercise.id))


@bp.route('/test/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def add_test(exercise_id):
    exercise = Exercise.query.filter_by(id=exercise_id).first()
    validate_exercise_admin(current_user, User.Roles['ADMIN'], exercise)
    form = TestForm()
    if request.method == 'POST' and form.validate_on_submit():
        exercise.create_test(request.files['input'], request.files['output'], form.max_points.data)
        flash('Dodano test', 'message')
        return redirect(url_for('admin.view_tests', exercise_id=exercise.id))
    return render_template('admin/add_test.html', exercise=exercise, form=form)


@bp.route('/<int:test_id>', methods=['GET', 'POST'])
@login_required
def delete_test(test_id):
    test = Test.query.filter_by(id=test_id).first()
    validate_test(current_user, User.Roles['ADMIN'], test)
    exercise_id = test.exercise_id
    shutil.rmtree(test.get_directory(), ignore_errors=True)
    db.session.delete(test)
    db.session.commit()
    flash('Usunięto test', 'message')
    return redirect(url_for('admin.view_tests', exercise_id=exercise_id))


@bp.route('/<string:course_name>/lesson/<int:lesson_id>/add_exercise', methods=['GET', 'POST'])
@login_required
def add_exercise(course_name, lesson_id):
    lesson: Lesson = Lesson.query.filter_by(id=lesson_id).first()
    validate_lesson(current_user, User.Roles['ADMIN'], lesson)
    form = ExerciseForm()
    if request.method == 'POST' and form.validate_on_submit():
        if not lesson.is_exercise_name_proper(form.name.data):
            flash('Wprowadź inną nazwę lekcji', 'error')
            return render_template('admin/add_exercise.html', form=form, lesson=lesson)
        exercise = lesson.create_exercise(form, request.form.get('editordata'))
        exercise.create_test(request.files['input'], request.files['output'], form.max_points.data)
        return redirect(url_for('admin.view_lesson', lesson_id=lesson.id))
    return render_template('admin/add_exercise.html', form=form, lesson=lesson)


@bp.route('/edit_exercise/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def edit_exercise(exercise_id):
    exercise = Exercise.query.filter_by(id=exercise_id).first()
    validate_exercise_admin(current_user, User.Roles['ADMIN'], exercise)
    form = ExerciseEditForm(obj=exercise)
    if request.method == 'POST' and form.validate_on_submit():
        exercise.values_by_form(form, request.form.get('editordata'))
        db.session.commit()
        flash('Zapisano zmiany', 'message')
        return redirect(url_for('admin.view_exercise', exercise_id=exercise.id))
    return render_template('admin/edit_exercise.html', form=form, exercise=exercise)


@bp.route('/view_tests/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def view_tests(exercise_id):
    exercise = Exercise.query.filter_by(id=exercise_id).first()
    validate_exercise_admin(current_user, User.Roles['ADMIN'], exercise)
    return render_template('admin/tests.html', exercise=exercise)
