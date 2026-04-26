from flask import Blueprint

bp = Blueprint('compliance', __name__, url_prefix='/compliance')

from modules.compliance import routes
