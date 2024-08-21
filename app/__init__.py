from flask import Flask, session, request
from config import Config
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_session import Session
import uuid
from .models import db, User  # Импортируем User из models
from .auth.routes import auth_bp
from .main.routes import main_bp
from .logging_config import configure_logging
from .admin import create_admin

app = Flask(__name__)
app.config.from_object(Config)

# Настройка базы данных
db.init_app(app)
migrate = Migrate(app, db)

# Настройка логирования
configure_logging(app)
app.logger.info('Logging is set up and running.')

# Настройка авторизации
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Сессии
Session(app)

# Регистрация Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)

# Создание админки
admin = create_admin(app)  # Вызов функции для создания админки


# Настройка пользователя
@login_manager.user_loader
def load_user(user_id):
    return User()


# Логирование перед каждым запросом
@app.before_request
def log_user_action():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())  # Создать уникальный ID для сессии
    app.logger.info(
        f'Session ID: {session["session_id"]}, '
        f'IP: {request.remote_addr}, '
        f'Path: {request.path}, '
        f'Method: {request.method}, '
        f'User-Agent: {request.headers.get("User-Agent")}'
    )


# Основной файл для запуска приложения
if __name__ == '__main__':
    with app.app_context():
        app.run(host="0.0.0.0", port=3060)
