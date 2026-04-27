from flask import Blueprint

bp = Blueprint('finished_products', __name__, url_prefix='/finished-products')

from modules.finished_products import routes
