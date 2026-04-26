from flask import Blueprint

bp = Blueprint('marketing', __name__, url_prefix='/marketing')

from modules.marketing import routes
