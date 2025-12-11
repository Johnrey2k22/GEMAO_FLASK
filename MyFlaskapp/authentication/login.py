from flask import render_template, request, redirect, url_for, flash, session, jsonify
from . import auth_bp

# Use the package-level DB helper that was moved into MyFlaskapp/__init__.py
from .. import get_db_connection


def Alert_Success(message):
    """Flashes a success message."""
    flash(message, 'success')
    return {'status': 'success', 'message': message}


def Alert_Fail(message):
    """Flashes a danger/error message."""
    flash(message, 'danger')
    return {'status': 'fail', 'message': message}


@auth_bp.route('/')
def index():
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Attempt to authenticate against the `user_tb` table in your 2b_db
        conn = get_db_connection()
        if not conn:
            Alert_Fail('Database connection error')
            return jsonify(status='fail', message='Database connection error')

        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, username, password, role FROM user_tb WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user and password and password == user.get('password'):
                # authenticated
                session['user_id'] = user.get('username')
                session['user_type'] = user.get('role')
                Alert_Success('Login successful!')
                if user.get('role') == 'cashier':
                    return jsonify(status='success', redirect=url_for('cashier.cashier_dashboard'))
                else:
                    return jsonify(status='success', redirect=url_for('user.user_dashboard'))
            else:
                Alert_Fail('Invalid credentials.')
                return jsonify(status='fail', message='Invalid credentials.')
        except Exception as e:
            Alert_Fail('Authentication error')
            return jsonify(status='fail', message=str(e))
        finally:
            try:
                cursor.close()
            except Exception:
                pass
            try:
                conn.close()
            except Exception:
                pass
    return render_template('login.html')
