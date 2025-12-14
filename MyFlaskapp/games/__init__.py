from flask import Blueprint

games_bp = Blueprint('games', __name__, template_folder='templates')

from . import routes