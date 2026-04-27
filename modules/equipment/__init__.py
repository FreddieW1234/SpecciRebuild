from flask import Blueprint

bp = Blueprint('equipment', __name__, url_prefix='/equipment')

from modules.equipment import routes
