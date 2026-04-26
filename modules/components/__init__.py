from flask import Blueprint

bp = Blueprint('components', __name__, url_prefix='/components')

from modules.components import routes
