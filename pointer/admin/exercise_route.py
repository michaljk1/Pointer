import shutil
from flask import render_template, url_for, flash, request
from flask_login import login_required, current_user
from pointer.admin import bp
from pointer.admin.admin_forms import ExerciseForm, TestForm, ExerciseEditForm
from werkzeug.utils import redirect
from pointer.models.test import Test
from pointer.models.usercourse import role
from pointer.models.lesson import Lesson
from pointer.models.exercise import Exercise
from pointer import db
from pointer.services.RouteService import validate_admin_exercise, validate_test, validate_lesson


@bp.route('/exercise/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def view_exercise(exercise_id):
    exercise = Exercise.query.filter_by(id=exercise_id).first()
    validate_admin_exercise(current_user, role['ADMIN'], exercise)
    return render_template('admin/exercise.html', exercise=exercise)


@bp.route('/activate_exercise/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def activate_exercise(exercise_id):
    exercise: Exercise = Exercise.query.filter_by(id=exercise_id).first()
    validate_admin_exercise(current_user, role['ADMIN'], exercise)
    exercise.is_published = not exercise.is_published
    db.session.commit()
    flash('Zapisano zmiany', 'message')
    return redirect(url_for('admin.view_exercise', exercise_id=exercise.id))


@bp.route('/test/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def add_test(exercise_id):
    exercise = Exercise.query.filter_by(id=exercise_id).first()
    validate_admin_exercise(current_user, role['ADMIN'], exercise)
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
    validate_test(current_user, role['ADMIN'], test)
    exercise_id = test.exercise_id
    shutil.rmtree(test.get_directory(), ignore_errors=True)
    db.session.delete(test)
    db.session.commit()
    flash('Usunięto test', 'message')
    return redirect(url_for('admin.view_exercise', exercise_id=exercise_id))


@bp.route('/<string:course_name>/lesson/<int:lesson_id>/add_exercise', methods=['GET', 'POST'])
@login_required
def add_exercise(course_name, lesson_id):
    lesson: Lesson = Lesson.query.filter_by(id=lesson_id).first()
    validate_lesson(current_user, role['ADMIN'], lesson)
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
    validate_admin_exercise(current_user, role['ADMIN'], exercise)
    form = ExerciseEditForm(obj=exercise)
    if request.method == 'POST' and form.validate_on_submit():
        exercise.values_by_form(form, request.form.get('editordata'))
        db.session.commit()
        flash('Zapisano zmiany', 'message')
        return redirect(url_for('admin.view_exercise', exercise_id=exercise.id))
    return render_template('admin/edit_exercise.html', form=form, exercise=exercise)
