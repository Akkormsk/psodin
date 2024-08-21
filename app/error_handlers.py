from flask import Blueprint, render_template, current_app

errors_bp = Blueprint('errors', __name__)


@errors_bp.app_errorhandler(404)
def not_found_error(error):
    current_app.logger.error(f"404 Error: {error}")
    return render_template('errors/404.html'), 404


@errors_bp.app_errorhandler(500)
def internal_error(error):
    current_app.logger.error(f"500 Error: {error}")
    return render_template('errors/500.html'), 500


@errors_bp.app_errorhandler(Exception)
def handle_exception(error):
    current_app.logger.error(f"Exception: {error}")
    return render_template('errors/500.html'), 500
