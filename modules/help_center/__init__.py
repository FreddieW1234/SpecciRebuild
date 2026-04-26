from flask import Blueprint

bp = Blueprint('help_center', __name__, url_prefix='/help-center')

from modules.help_center import routes
