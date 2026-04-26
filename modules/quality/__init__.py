from flask import Blueprint

bp = Blueprint('quality', __name__, url_prefix='/quality')

from modules.quality import routes
