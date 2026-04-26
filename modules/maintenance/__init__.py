from flask import Blueprint

bp = Blueprint('maintenance', __name__, url_prefix='/maintenance')

from modules.maintenance import routes
