from flask import render_template, session, redirect, url_for, flash
from functools import wraps
from . import admin_bp

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    if session.get('user_role') != 'admin':
        flash('Access denied. This area is for admins only.', 'danger')
        return redirect(url_for('auth.login'))
    return render_template('admin/admin_dashboard.html')
