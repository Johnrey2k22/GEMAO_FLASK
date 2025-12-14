from flask import render_template
from . import user_bp
from MyFlaskapp.authentication.decorators import login_required

"""
This file only defines the blueprint object. Routes are now in routes.py.
"""
