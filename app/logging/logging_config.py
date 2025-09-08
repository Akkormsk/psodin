import logging
from logging.handlers import RotatingFileHandler
import sys # Добавляем импорт sys
import os
from flask import request, session
from sqlalchemy import event
from sqlalchemy.engine import Engine

def configure_logging(app):
    # Создаем логгер
    logger = logging.getLogger('app_logger')
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')

    # Обработчик для записи в файл (в /tmp), с безопасным фолбэком
    log_path = app.config.get('LOG_FILE', '/tmp/app.log')
    try:
        log_dir = os.path.dirname(log_path)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        file_handler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=1)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception:
        # Если не удалось создать файл — пишем только в stdout
        pass

    # Обработчик для вывода в консоль (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    @app.before_request
    def log_user_action():
        logger.info(
            f'Пользователь перешел на страницу: {request.path}, '
            f'Метод: {request.method}, '
            f'ID сессии: {session.get("session_id", "Unknown")}'
        )

    @app.errorhandler(Exception)
    def log_error(e):
        logger.error(
            f'Ошибка на странице: {request.path}, Ошибка: {str(e)}, '
            f'ID сессии: {session.get("session_id", "Unknown")}'
        )
        return "Произошла ошибка", 500

    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        # Логирование SQL-запросов
        logger.info(
            f'Выполнение SQL-запроса: {statement}, '
            f'Параметры: {parameters}'
        )
