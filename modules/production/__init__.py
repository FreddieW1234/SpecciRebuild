from flask import Blueprint

bp = Blueprint('production', __name__, url_prefix='/production')

from modules.production import routes
