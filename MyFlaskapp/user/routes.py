from flask import render_template, session, redirect, url_for
from functools import wraps
from . import user_bp
from MyFlaskapp.db import get_db_connection

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def user_role_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        if session.get('user_role') != 'user':
            return redirect(url_for('admin.admin_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@user_bp.route('/dashboard')
@user_role_required
def dashboard():
    user_id = session['user_id']
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_tb WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        if user:
            session['user_info'] = user
        conn.close()
    return render_template('user/dashboard.html')

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    from flask import request, flash
    from datetime import datetime
    user_id = session['user_id']
    conn = get_db_connection()
    if request.method == 'POST':
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        birthdate = request.form.get('birthdate')
        mobile_number = request.form.get('mobile_number')
        email = request.form.get('email')
        personal_intro = request.form.get('personal_intro')
        dream_it_job = request.form.get('dream_it_job')
        profile_image = request.files.get('profile_image')
        
        # Calculate age
        age = None
        if birthdate:
            birth = datetime.strptime(birthdate, '%Y-%m-%d').date()
            today = datetime.now().date()
            age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        
        # Handle image upload with security validation
        image_path = None
        if profile_image and profile_image.filename:
            from MyFlaskapp.security_utils import safe_file_save
            success, result = safe_file_save(profile_image)
            if success:
                image_path = result
            else:
                flash(f'Error uploading image: {result}', 'danger')
                return redirect(url_for('user.profile'))
        
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM user_tb WHERE user_id = %s", (user_id,))
            user_rec = cursor.fetchone()
            if user_rec:
                user_id_int = user_rec['id']
                cursor.execute("UPDATE user_tb SET firstname=%s, lastname=%s, birthdate=%s, mobile_number=%s, email=%s, profile_image=%s, personal_intro=%s, dream_it_job=%s WHERE id=%s", (firstname, lastname, birthdate, mobile_number, email, image_path or '', personal_intro or '', dream_it_job or '', user_id_int))
                conn.commit()
                conn.close()
                # Update session
                session['user_info'].update({
                    'firstname': firstname, 'lastname': lastname, 'birthdate': birthdate,
                    'mobile_number': mobile_number, 'email': email, 'personal_intro': personal_intro,
                    'dream_it_job': dream_it_job
                })
                if image_path:
                    session['user_info']['profile_image'] = image_path
                flash('Profile updated successfully', 'success')
                return redirect(url_for('user.profile'))
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_tb WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        conn.close()
        # Calculate age
        age = None
        if user['birthdate']:
            birth = user['birthdate']
            today = datetime.now().date()
            age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    else:
        user = session.get('user_info', {})
        age = None
    return render_template('user/profile.html', user=user, age=age)
