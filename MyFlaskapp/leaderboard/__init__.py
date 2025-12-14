from flask import Blueprint

leaderboard_bp = Blueprint('leaderboard', __name__, template_folder='templates')

from . import routes