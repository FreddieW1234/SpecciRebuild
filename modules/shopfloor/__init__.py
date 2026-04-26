from flask import Blueprint

bp = Blueprint('shopfloor', __name__, url_prefix='/shopfloor')

from modules.shopfloor import routes
