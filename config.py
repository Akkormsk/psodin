import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'print_shop.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = '1111'
    SECRET_ADMIN_PASSWORD = '1111'  # Установите ваш пароль здесь
    FLASK_ADMIN_FLUID_LAYOUT = False
