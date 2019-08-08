import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'jZTg_qxs54M-n_?=xVhA?43HkW2ee_&-'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////peoplecounter/server/main.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
