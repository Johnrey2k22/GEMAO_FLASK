from flask import Blueprint

# Templates are served from the project's top-level `templates/` directory.
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

from . import routes
