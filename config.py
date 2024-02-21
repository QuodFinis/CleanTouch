import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:password@localhost/cleantouch'
    SQLALCHEMY_TRACK_MODIFICATIONS = False