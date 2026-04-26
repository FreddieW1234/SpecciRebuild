from flask import Blueprint

bp = Blueprint('traceability', __name__, url_prefix='/traceability')

from modules.traceability import routes
