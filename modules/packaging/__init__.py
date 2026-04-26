from flask import Blueprint

bp = Blueprint('packaging', __name__, url_prefix='/packaging')

from modules.packaging import routes
