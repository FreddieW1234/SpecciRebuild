from flask import Blueprint

bp = Blueprint('rnd', __name__, url_prefix='/rnd')

from modules.rnd import routes
