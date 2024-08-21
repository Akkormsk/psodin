from flask import Flask, session, request, g
from config import Config
from flask_migrate import Migrate
from flask_session import Session
import uuid
from .models import *
from .auth.routes import auth_bp
from .main.routes import main_bp
from app.logging.logging_config import configure_logging  # Изменен путь для импорта
from app.admin.admin import create_admin
from .admin.routes import log_bp

app = Flask(__name__)
app.config.from_object(Config)

# Настройка базы данных
db.init_app(app)
migrate = Migrate(app, db)

# Настройка логирования
configure_logging(app)
app.logger.info('Logging is set up and running.')

# Сессии
Session(app)

# Регистрация Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(log_bp)

# Создание админки
admin = create_admin(app)

# Основной файл для запуска приложения
if __name__ == '__main__':
    with app.app_context():
        app.run()
