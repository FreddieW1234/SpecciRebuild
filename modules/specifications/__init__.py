from flask import Blueprint

bp = Blueprint('specifications', __name__, url_prefix='/specifications')

from modules.specifications import routes
