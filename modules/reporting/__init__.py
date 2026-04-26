from flask import Blueprint

bp = Blueprint('reporting', __name__, url_prefix='/reporting')

from modules.reporting import routes
