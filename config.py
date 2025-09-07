import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # База данных: сначала берём переменную окружения, иначе локальная SQLite
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'print_shop.db'))

    # Закомментированное подключение к удаленной базе данных
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user1:Ps123456@147.45.138.165:3306/psadmin_db?charset=utf8mb4'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-me')
    SECRET_ADMIN_PASSWORD = '1111'
    FLASK_ADMIN_FLUID_LAYOUT = True
    SESSION_TYPE = 'filesystem'
