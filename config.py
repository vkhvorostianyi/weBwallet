import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    POSTGRES = {
        'user': 'w_app_user',
        'pw': 'p@ss@!worD2',
        'db': 'app',
        'host': 'localhost',
        'port': '5432'
    }

    SQLALCHEMY_DATABASE_URI = 'sqlite:////test.db'
    SEND_FILE_MAX_AGE_DEFAULT = 0
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my_task_secret_key'
