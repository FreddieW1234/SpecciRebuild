from flask import Blueprint

bp = Blueprint('crm', __name__, url_prefix='/crm')

from modules.crm import routes
