import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = 'sample'
    SQLALCHEMY_DATABASE_URI = 'sample'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = 'sample'
    # Flask-Mail SMTP server settings
    MAIL_SERVER = 'sample'
    MAIL_PORT = 'sample'
    MAIL_USE_TLS = 'sample'
    SERVER_NAME = '127.0.0.1:5000'
    MAIL_USERNAME = 'sample'
    MAIL_PASSWORD = 'sample'
    ADMINS = ['sample']
    MAIN_DIR = '/home/michal/PycharmProjects/Pointer/instance'
    MAX_MEMORY_MB = 3123#sample
