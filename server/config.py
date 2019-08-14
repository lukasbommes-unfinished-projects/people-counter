class Config(object):
    SECRET_KEY = b'\x91\xd8\xfe\x83\xe6\x13\x11\x0f\xb9\xf1\x9cm9\xe7\x85\xee'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////peoplecounter/server/main.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
