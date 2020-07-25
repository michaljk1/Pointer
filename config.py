import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = 'change-it-not-to-be-guessed'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')  # local db
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = 'redis://'  # local server
    # Flask-Mail SMTP server settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    SERVER_NAME = '127.0.0.1:5000'

    INSTANCE_DIR = '/home/michal/PycharmProjects/Pointer/instance'
    MAX_MEMORY_MB = 5000  # sample

    # POINTER EMAIL SENDER
    MAIL_USERNAME = 'pointerlicmail@gmail.com'
    MAIL_PASSWORD = 'TeRmalica!1'
    ADMINS = ['pointerlicmail@gmail.com']

    TOKEN_EXPIRES_IN = 600#seconds

    # MODERATOR CREDENTIALS
    MOD_EMAIL = 'moderator@admin.com'
    MOD_NAME = 'modname'
    MOD_SURNAME = 'modsurname'
    MOD_PASSWORD = 'Admin123'
