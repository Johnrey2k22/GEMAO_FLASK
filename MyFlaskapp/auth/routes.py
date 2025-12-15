from flask import render_template, redirect, url_for, flash, request, session, jsonify, current_app
from functools import wraps
from . import auth_bp
from MyFlaskapp.db import get_db_connection
from werkzeug.security import check_password_hash, generate_password_hash
from MyFlaskapp.utils import validate_email, validate_password, generate_otp, send_otp_email, store_otp, verify_otp, check_duplicate_user, can_resend_otp, Alert_Success, Alert_Fail
from MyFlaskapp.rate_limiter import rate_limit, otp_rate_limit
import random

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/test')
def test():
    return "Test endpoint working"

@auth_bp.route('/login', methods=['GET', 'POST'])
# @rate_limit(max_attempts=5, window_seconds=5)  # 5 attempts per 5 seconds - DISABLED
def login():
    if request.method == 'POST':
        print(f"DEBUG: Login request received")
        print(f"DEBUG: Request headers: {dict(request.headers)}")
        print(f"DEBUG: Form data: {dict(request.form)}")
        
        username = request.form.get('username')
        password = request.form.get('password')
        
        print(f"DEBUG: Username: {username}, Password: {'***' if password else 'None'}")
        
        # Validate input
        if not username or not password:
            print("DEBUG: Missing username or password")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'status': 'fail', 'message': 'Username and password are required'}), 400
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            sql_query = "SELECT * FROM user_tb WHERE username = %s"
            cursor.execute(sql_query, (username,))
            user = cursor.fetchone()
            conn.close()
            
            if user and check_password_hash(user['password'], password):
                session.permanent = True
                session['user_id'] = user['user_id']
                session['user_name'] = f"{user['firstname']} {user['lastname']}"
                session['user_role'] = 'admin' if user['user_type'] in ['admin', ''] else 'user'
                session['user_info'] = user
                
                # Handle AJAX requests from modal
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    redirect_url = url_for('admin.admin_dashboard') if session['user_role'] == 'admin' else url_for('user.dashboard')
                    return jsonify({'status': 'success', 'redirect': redirect_url})
                
                flash('You were successfully logged in', 'success')
                
                if session['user_role'] == 'admin':
                    return redirect(url_for('admin.admin_dashboard'))
                else:
                    return redirect(url_for('user.dashboard'))
            else:
                # Handle AJAX requests from modal
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'status': 'fail', 'message': 'Incorrect Credentials'}), 400
                
                flash('Incorrect Credentials', 'danger')
        else:
            # Database connection error
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'status': 'fail', 'message': 'Database connection failed'}), 500
            flash('Database connection failed', 'danger')
    
    # For GET requests or failed POST without AJAX, check if this is an AJAX request
    if request.method == 'GET' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'fail', 'message': 'Invalid request method'}), 400
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
# @rate_limit(max_attempts=3, window_seconds=600)  # 3 registration attempts per 10 minutes - DISABLED
def register():
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        birthdate = request.form.get('birthdate')
        address = request.form.get('address')
        mobile = request.form.get('mobile')
        
        # Validation
        if not all([firstname, lastname, username, email, password, confirm_password, birthdate, address, mobile]):
            Alert_Fail('All fields are required.')
            return redirect(url_for('auth.register'))
        
        if not validate_email(email):
            Alert_Fail('Invalid email format.')
            return redirect(url_for('auth.register'))
        
        valid_pass, pass_msg = validate_password(password)
        if not valid_pass:
            Alert_Fail(pass_msg)
            return redirect(url_for('auth.register'))
        
        if password != confirm_password:
            Alert_Fail('Passwords do not match.')
            return redirect(url_for('auth.register'))
        
        if check_duplicate_user(email, username):
            Alert_Fail('Email or username already exists.')
            return redirect(url_for('auth.register'))
        
        # Generate and send OTP
        otp = generate_otp()
        mail = current_app.extensions.get('mail')
        if store_otp(email, otp) and send_otp_email(email, otp, mail):
            session['registration_data'] = {
                'firstname': firstname,
                'lastname': lastname,
                'username': username,
                'email': email,
                'password': generate_password_hash(password),
                'birthdate': birthdate,
                'address': address,
                'mobile': mobile
            }
            Alert_Success('OTP sent to your email. Please verify.')
            return redirect(url_for('auth.verify_otp_route'))
        else:
            Alert_Fail('Failed to send OTP. Please check email configuration or try again.')
            return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html')

@auth_bp.route('/verify_otp', methods=['GET', 'POST'])
# @otp_rate_limit(max_attempts=3, window_seconds=600)  # 3 OTP attempts per 10 minutes - DISABLED
def verify_otp_route():
    if 'registration_data' not in session:
        return redirect(url_for('auth.register'))
    
    if request.method == 'POST':
        otp = request.form.get('otp')
        email = session['registration_data']['email']
        
        if verify_otp(email, otp):
            # Create user
            data = session['registration_data']
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_tb (user_id, firstname, lastname, username, password, user_type, birthdate, address, mobile_number, email)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    f"{random.randint(100,999)}",  # Simple user_id generation
                    data['firstname'], data['lastname'], data['username'], data['password'],
                    'user', data['birthdate'], data['address'], data['mobile'], data['email']
                ))
                conn.commit()
                conn.close()
                session.pop('registration_data', None)
                Alert_Success('Registration successful. Please login.')
                return redirect(url_for('auth.login'))
            else:
                Alert_Fail('Database error.')
        else:
            Alert_Fail('Invalid or expired OTP.')
    
    return render_template('auth/verify_otp.html')

@auth_bp.route('/resend_otp')
# @rate_limit(max_attempts=2, window_seconds=300)  # 2 resend attempts per 5 minutes - DISABLED
def resend_otp():
    if 'registration_data' not in session:
        return redirect(url_for('auth.register'))
    
    email = session['registration_data']['email']
    if can_resend_otp(email):
        otp = generate_otp()
        mail = current_app.extensions.get('mail')
        if store_otp(email, otp) and send_otp_email(email, otp, mail):
            Alert_Success('OTP resent to your email.')
        else:
            Alert_Fail('Failed to resend OTP. Please check email configuration.')
    else:
        Alert_Fail('Please wait before requesting another OTP.')
    
    return redirect(url_for('auth.verify_otp_route'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # Handle profile update
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': 'User not authenticated'}), 401
        
        data = request.get_json()
        firstname = data.get('firstname')
        lastname = data.get('lastname')
        username = data.get('username')
        email = data.get('email')
        mobile = data.get('mobile')
        birthdate = data.get('birthdate')
        address = data.get('address')
        
        # Validation
        if not all([firstname, lastname, username, email]):
            return jsonify({'success': False, 'message': 'Required fields missing'}), 400
        
        if not validate_email(email):
            return jsonify({'success': False, 'message': 'Invalid email format'}), 400
        
        # Check if username or email is taken by another user
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT user_id FROM user_tb WHERE (username = %s OR email = %s) AND user_id != %s", 
                         (username, email, user_id))
            existing = cursor.fetchone()
            if existing:
                conn.close()
                return jsonify({'success': False, 'message': 'Username or email already taken'}), 400
            
            # Update user
            cursor.execute("""
                UPDATE user_tb SET firstname = %s, lastname = %s, username = %s, email = %s, 
                mobile_number = %s, birthdate = %s, address = %s WHERE user_id = %s
            """, (firstname, lastname, username, email, mobile, birthdate, address, user_id))
            conn.commit()
            conn.close()
            
            # Update session
            session['user_name'] = f"{firstname} {lastname}"
            
            return jsonify({'success': True, 'message': 'Profile updated successfully'})
        else:
            return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    # GET request - display profile
    user_id = session.get('user_id')
    conn = get_db_connection()
    user = None
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_tb WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        conn.close()
    
    return render_template('auth/profile.html', 
                         user=user,
                         user_role=session.get('user_role'))