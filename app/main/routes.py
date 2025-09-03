import os

from flask import Blueprint, render_template, request, jsonify, current_app, send_from_directory

import logging
from ..models import *

main_bp = Blueprint('main', __name__)
logger = logging.getLogger('app_logger')


@main_bp.route('/')
@main_bp.route('/home')
def index():
    return render_template('index.html')


@main_bp.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(current_app.root_path, 'static'),
                               'favicon.png', mimetype='image/vnd.microsoft.icon')
