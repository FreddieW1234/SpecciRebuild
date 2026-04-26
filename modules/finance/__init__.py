from flask import Blueprint

bp = Blueprint('finance', __name__, url_prefix='/finance')

from modules.finance import routes
