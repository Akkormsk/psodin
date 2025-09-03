from flask import Blueprint

calculator_bp = Blueprint('calculator', __name__, url_prefix='/calculator', template_folder='../templates/Calculator')
