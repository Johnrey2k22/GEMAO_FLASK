from flask import render_template, redirect, url_for, flash, request, session
from functools import wraps
from . import auth_bp
from MyFlaskapp.db import get_db_connection

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Server-side validation
        errors = []
        
        # Username validation
        if not username:
            errors.append('Username is required')
        elif len(username) < 3:
            errors.append('Username must be at least 3 characters long')
        elif len(username) > 50:
            errors.append('Username must not exceed 50 characters')
        elif not username.replace('_', '').replace('-', '').isalnum():
            errors.append('Username can only contain letters, numbers, underscores, and hyphens')
        
        # Password validation
        if not password:
            errors.append('Password is required')
        elif len(password) < 4:
            errors.append('Password must be at least 4 characters long')
        elif len(password) > 100:
            errors.append('Password must not exceed 100 characters')
        
        # If validation errors exist, flash them and re-render the form
        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/login.html')
        
        print(f"Attempting login with username: {username}, password: {password}")
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            sql_query = "SELECT * FROM user_tb WHERE username = %s"
            cursor.execute(sql_query, (username,))
            user = cursor.fetchone()
            conn.close()
            print(f"User retrieved from DB: {user}")
            if user:
                print(f"Password from DB: {user['password']}")
                print(f"Password comparison result: {user['password'] == password}")
            
            if user and user['password'] == password:
                session.permanent = True
                session['user_id'] = user['user_id']
                session['user_name'] = f"{user['firstname']} {user['lastname']}"
                session['user_role'] = user['user_type']
                session['user_info'] = user
                
                flash('You were successfully logged in', 'success')
                
                if user['user_type'] == 'admin':
                    return redirect(url_for('admin.admin_dashboard'))
                else:
                    return redirect(url_for('user.dashboard'))
            else:
                flash('Incorrect Credentials', 'danger')
        else:
            flash('Database connection error. Please try again later.', 'danger')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', 
                         username=session.get('user_name'),
                         user_role=session.get('user_role'))
