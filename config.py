import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    # База данных: сначала берём переменную окружения, иначе локальная SQLite
    # По умолчанию используем /tmp, так как она доступна на большинстве платформ
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:////tmp/print_shop.db')

    # Закомментированное подключение к удаленной базе данных
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user1:Ps123456@147.45.138.165:3306/psadmin_db?charset=utf8mb4'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-me')
    SECRET_ADMIN_PASSWORD = '1111'
    FLASK_ADMIN_FLUID_LAYOUT = True
    SESSION_TYPE = 'filesystem'
    # Хранилище сессий в файловой системе: используем /tmp для совместимости с read-only rootfs
    SESSION_FILE_DIR = os.getenv('SESSION_FILE_DIR', os.path.join('/tmp', 'flask_session'))
    # Путь к лог-файлу; по умолчанию /tmp/app.log, чтобы избежать ошибок записи
    LOG_FILE = os.getenv('LOG_FILE', '/tmp/app.log')
