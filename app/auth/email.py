from threading import Thread
from flask import render_template, current_app
from app import mail
from flask_mail import Message
from flask import current_app
from time import time
import jwt


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()


def send_confirm_email(email):
    token = get_confirm_email_token(email)
    send_email('[Pointer] Potwierdź email',
               sender=current_app.config['ADMINS'][0],
               recipients=[email],
               html_body=render_template('email/confirm_email_request.html', token=token))


def send_course_email(email, course_name, role):
    send_email('[Pointer] Nowy kurs',
               sender=current_app.config['ADMINS'][0],
               recipients=[email],
               html_body=render_template('email/confirm_course.html', role=role, course_name=course_name))


def get_confirm_email_token(email, expires_in=600):
    return jwt.encode(
        {'confirm_email': email, 'exp': time() + expires_in},
        current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
