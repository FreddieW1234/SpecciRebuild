from flask import Blueprint

bp = Blueprint('hr', __name__, url_prefix='/hr')

from modules.hr import routes
