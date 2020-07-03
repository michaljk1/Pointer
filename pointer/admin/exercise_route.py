import os
import shutil
from datetime import datetime
from flask import render_template, url_for, flash, request
from flask_login import login_required, current_user
from pointer.admin import bp
from pointer.admin.forms import ExerciseForm, TestForm
from werkzeug.utils import redirect
from pointer.models.test import Test
from pointer.models.usercourse import Course, role
from pointer.models.lesson import Lesson
from pointer.models.exercise import Exercise

from pointer import db
from pointer.services.RouteService import validate_exists, validate_role_course, validate_role


@bp.route('/exercise/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def view_exercise(exercise_id):
    exercise = Exercise.query.filter_by(id=exercise_id).first()
    validate_role_course(current_user, role['ADMIN'], exercise.lesson.course)
    return render_template('admin/exercise.html', exercise=exercise)


@bp.route('/activate_exercise/<string:exercise_id>', methods=['GET', 'POST'])
@login_required
def activate_exercise(exercise_id):
    exercise: Exercise = Exercise.query.filter_by(id=exercise_id).first()
    validate_role_course(current_user, role['ADMIN'], exercise.lesson.course)
    exercise.is_published = not exercise.is_published
    db.session.commit()
    flash('Opublikowano', 'message')
    return redirect(url_for('admin.view_exercise', exercise_id=exercise.id))


@bp.route('/test/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def add_test(exercise_id):
    exercise = Exercise.query.filter_by(id=exercise_id).first()
    validate_role_course(current_user, role['ADMIN'], exercise.lesson.course)
    form = TestForm()
    if request.method == 'POST' and form.validate_on_submit():
        exercise.create_test(request.files['input'], request.files['output'], form.max_points.data)
        flash('Dodano test', 'message')
        return redirect(url_for('admin.view_exercise', exercise_id=exercise.id))
    return render_template('admin/add_test.html', exercise=exercise, form=form)


@bp.route('/<int:test_id>', methods=['GET', 'POST'])
@login_required
def delete_test(test_id):
    test = Test.query.filter_by(id=test_id).first()
    exercise_id = test.exercise_id
    validate_role_course(current_user, role['ADMIN'], test.get_course())
    shutil.rmtree(test.get_directory(), ignore_errors=True)
    db.session.delete(test)
    db.session.commit()
    flash('Usunięto test', 'message')
    return redirect(url_for('admin.view_exercise', exercise_id=exercise_id))


@bp.route('/<string:course_name>/<string:lesson_name>/add_exercise', methods=['GET', 'POST'])
@login_required
def add_exercise(course_name, lesson_name):
    course = Course.query.filter_by(name=course_name).first()
    validate_exists(course)
    lesson: Lesson = course.get_lesson_by_name(lesson_name)
    validate_exists(lesson)
    validate_role_course(current_user, role['ADMIN'], course)
    form = ExerciseForm()
    if request.method == 'POST' and form.validate_on_submit():
        if not lesson.is_exercise_name_proper(form.name.data):
            flash('Wprowadź inną nazwę lekcji', 'error')
            return render_template('admin/add_template.html', form=form, lesson=lesson)
        end_date, end_time = form.end_date.data, form.end_time.data
        end_datetime = datetime(year=end_date.year, month=end_date.month, day=end_date.day, hour=end_time.hour,
                                minute=end_time.minute)
        exercise = Exercise(name=form.name.data, content=form.content.data, lesson_id=lesson.id,
                            max_attempts=form.max_attempts.data, compile_command=form.compile_command.data,
                            end_date=end_datetime, run_command=form.run_command.data,
                            program_name=form.program_name.data, timeout=form.timeout.data, interval=form.interval.data)
        lesson.exercises.append(exercise)
        os.makedirs(exercise.get_directory())
        exercise.create_test(request.files['input'], request.files['output'], form.max_points.data)
        return redirect(url_for('admin.view_lesson', lesson_name=lesson.name))
    return render_template('admin/add_template.html', form=form, lesson=lesson)
