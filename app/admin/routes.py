from flask import Blueprint, render_template

log_bp = Blueprint('log', __name__)


@log_bp.route('/logs')
def view_logs():
    with open('app.log', 'r') as f:
        logs = f.readlines()
    return render_template('logs.html', logs=logs)
