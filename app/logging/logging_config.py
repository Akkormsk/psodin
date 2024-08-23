# import logging
# from logging.handlers import RotatingFileHandler
# from flask import request, session
# from sqlalchemy import event
# from sqlalchemy.engine import Engine
#
# def configure_logging(app):
#     # Создаем логгер
#     logger = logging.getLogger('app_logger')
#     logger.setLevel(logging.INFO)
#
#     handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
#     formatter = logging.Formatter(
#         '%(asctime)s %(levelname)s: %(message)s'
#     )
#     handler.setFormatter(formatter)
#     logger.addHandler(handler)
#
#     @app.before_request
#     def log_user_action():
#         logger.info(
#             f'Пользователь перешел на страницу: {request.path}, '
#             f'Метод: {request.method}, '
#             f'ID сессии: {session.get("session_id", "Unknown")}'
#         )
#
#     @app.errorhandler(Exception)
#     def log_error(e):
#         logger.error(
#             f'Ошибка на странице: {request.path}, Ошибка: {str(e)}, '
#             f'ID сессии: {session.get("session_id", "Unknown")}'
#         )
#         return "Произошла ошибка", 500
#
#     @event.listens_for(Engine, "before_cursor_execute")
#     def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
#         # Логирование SQL-запросов
#         logger.info(
#             f'Выполнение SQL-запроса: {statement}, '
#             f'Параметры: {parameters}'
#         )


from flask import request, session
from sqlalchemy import event
from sqlalchemy.engine import Engine


def configure_logging(app):
    # Удаляем логгер и оставляем стандартный вывод в терминал
    pass

    @app.before_request
    def log_user_action():
        pass

    @app.errorhandler(Exception)
    def log_error(e):
        pass

    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        pass
