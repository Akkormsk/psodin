import logging
from logging.handlers import RotatingFileHandler
from flask import current_app as app, g, session, request
from sqlalchemy import event
from sqlalchemy.engine import Engine
from flask_login import current_user


def configure_logging(app):
    handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

    # Event listener for SQLAlchemy queries
    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        app.logger.info(f"User: {g.user}, Executing: {statement}, Parameters: {parameters}")

    # Log user actions before each request
    @app.before_request
    def log_user_action():
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())

        user = current_user.get_id() if current_user.is_authenticated else 'Anonymous'
        g.user = user

        app.logger.info(
            f'User: {user}, '
            f'Session ID: {session["session_id"]}, '
            f'IP: {request.remote_addr}, '
            f'Path: {request.path}, '
            f'Method: {request.method}, '
            f'User-Agent: {request.headers.get("User-Agent")}'
        )

    # Log errors
    @app.errorhandler(Exception)
    def log_error(e):
        user = getattr(g, 'user', 'Unknown')
        app.logger.error(
            f'User: {user}, Path: {request.path}, Error: {str(e)}, '
            f'Session ID: {session.get("session_id", "Unknown")}, '
            f'IP: {request.remote_addr}, '
            f'User-Agent: {request.headers.get("User-Agent")}'
        )
        return "An error occurred", 500

