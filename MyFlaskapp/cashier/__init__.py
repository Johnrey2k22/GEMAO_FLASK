from flask import Blueprint

cashier_bp = Blueprint('cashier', __name__, template_folder='templates')
from . import routes
