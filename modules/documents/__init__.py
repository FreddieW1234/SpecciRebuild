from flask import Blueprint

bp = Blueprint('documents', __name__, url_prefix='/documents')

from modules.documents import routes
