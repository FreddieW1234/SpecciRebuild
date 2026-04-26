from flask import Blueprint

bp = Blueprint('pricing', __name__, url_prefix='/pricing')

from modules.pricing import routes
