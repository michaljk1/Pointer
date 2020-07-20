import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = 'change-it-not-to-be-guessed'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db') #local db
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = 'redis://' #local server
    # Flask-Mail SMTP server settings
    MAIL_SERVER = 'sample'
    MAIL_PORT = 'sample'
    MAIL_USE_TLS = 'sample'
    SERVER_NAME = '127.0.0.1:5000'

    INSTANCE_DIR = '/home/mich/Pointer/instance'
    MAX_MEMORY_MB = 5000#sample

    #POINTER EMAIL SENDER
    MAIL_USERNAME = 'pointerlicmail@gmail.com'
    MAIL_PASSWORD = ''
    ADMINS = ['pointerlicmail@gmail.com']

    #MODERATOR CREDENTIALS
    MOD_EMAIL = 'moderator@admin.com'
    MOD_LOGIN = 'moderator'
    MOD_NAME = 'modname'
    MOD_SURNAME = 'modsurname'
    MOD_PASSWORD = 'Admin123'
