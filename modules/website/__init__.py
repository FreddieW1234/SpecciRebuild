from flask import Blueprint

bp = Blueprint('website', __name__, url_prefix='/website')

from modules.website import routes
