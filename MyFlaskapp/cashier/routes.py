from flask import render_template
from . import cashier_bp

@cashier_bp.route('/cashier_dashboard')
def cashier_dashboard():
    return render_template('cashier_dashboard.html')
