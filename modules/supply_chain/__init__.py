from flask import Blueprint

bp = Blueprint('supply_chain', __name__, url_prefix='/supply-chain')

from modules.supply_chain import routes
