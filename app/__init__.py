from flask import Flask, session, request, g
import os
from config import Config
from flask_migrate import Migrate
from flask_session import Session
from .models import db
from .auth.routes import auth_bp
from .main.routes import main_bp
from .datamatrix.routes import datamatrix_bp
from .calculator.routes import calculator_bp
from app.logging.logging_config import configure_logging
from app.admin.admin import create_admin

app = Flask(__name__)
app.config.from_object(Config)

# Настройка базы данных
db.init_app(app)
migrate = Migrate(app, db)

# Настройка сессий
if app.config.get('SESSION_TYPE') == 'filesystem':
    session_dir = app.config.get('SESSION_FILE_DIR')
    if session_dir:
        os.makedirs(session_dir, exist_ok=True)
Session(app)

# Настройка логирования
configure_logging(app)

# Регистрация Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(datamatrix_bp)
app.register_blueprint(calculator_bp)

# Создание админки
admin = create_admin(app)

# Основной файл для запуска приложения
if __name__ == '__main__':
    with app.app_context():
        app.run()
