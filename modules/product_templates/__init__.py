from flask import Blueprint

bp = Blueprint('product_templates', __name__, url_prefix='/product-templates')

from modules.product_templates import routes
