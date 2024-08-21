import logging
from logging.handlers import RotatingFileHandler
from flask import request, session

def configure_logging(app):
    # Создаем логгер
    logger = logging.getLogger('app_logger')
    logger.setLevel(logging.INFO)

    handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    @app.before_request
    def log_user_action():
        logger.info(
            f'Path: {request.path}, '
            f'Method: {request.method}, '
            f'Session ID: {session.get("session_id", "Unknown")}, '
            f'User-Agent: {request.headers.get("User-Agent")}'
        )

    @app.errorhandler(Exception)
    def log_error(e):
        logger.error(
            f'Path: {request.path}, Error: {str(e)}, '
            f'Session ID: {session.get("session_id", "Unknown")}, '
            f'User-Agent: {request.headers.get("User-Agent")}'
        )
        return "An error occurred", 500
