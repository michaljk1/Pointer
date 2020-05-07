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


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()


def send_create_account_email(email, course_name):
    token = get_reset_password_token(email)
    token += '_' + course_name
    send_email('[Microblog] Reset Your Password',
               sender=current_app.config['ADMINS'][0],
               recipients=[email],
               text_body=render_template('email/create_account_request.txt', token=token),
               html_body=render_template('admin/create_account.html', token=token))


def get_reset_password_token(email, expires_in=600):
    return jwt.encode(
        {'create_account': email, 'exp': time() + expires_in},
        current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')


@staticmethod
def verify_reset_password_token(token):
    try:
        id = jwt.decode(token, current_app.config['SECRET_KEY'],
                        algorithms=['HS256'])['reset_password']
    except:
        return
