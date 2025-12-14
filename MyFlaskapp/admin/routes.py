from flask import render_template, session, redirect, url_for, request, flash
from functools import wraps
from . import admin_bp
from MyFlaskapp.db import get_db_connection
from werkzeug.security import generate_password_hash
from MyFlaskapp.utils import validate_email, validate_password, generate_otp, send_otp_email, store_otp, verify_otp, check_duplicate_user, can_resend_otp, Alert_Success, Alert_Fail
from MyFlaskapp.games.routes import scan_games_directory
import random
import os

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_role') != 'admin':
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    users = []
    games = []
    scores = []
    
    # Get directory-scanned games
    scanned_games = scan_games_directory()
    
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_tb")
        users = cursor.fetchall()
        
        # Get scores from database (if any exist)
        cursor.execute("SELECT l.*, g.name as game_name, u.username FROM leaderboards l JOIN games g ON l.game_id = g.id JOIN user_tb u ON l.user_id = u.id ORDER BY l.score DESC LIMIT 10")
        scores = cursor.fetchall()
        conn.close()
    
    # Use scanned games instead of database games
    games = scanned_games
    
    return render_template('admin/dashboard.html', users=users, games=games, scores=scores)

@admin_bp.route('/add_user', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    if request.method == 'POST':
        user_id = request.form['user_id']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']
        birthdate = request.form['birthdate']
        address = request.form['address']
        mobile = request.form['mobile']
        email = request.form['email']
        
        # Validation
        if not all([user_id, firstname, lastname, username, password, user_type, birthdate, address, mobile, email]):
            Alert_Fail('All fields are required.')
            return redirect(url_for('admin.add_user'))
        
        if not validate_email(email):
            Alert_Fail('Invalid email format.')
            return redirect(url_for('admin.add_user'))
        
        valid_pass, pass_msg = validate_password(password)
        if not valid_pass:
            Alert_Fail(pass_msg)
            return redirect(url_for('admin.add_user'))
        
        if check_duplicate_user(email, username):
            Alert_Fail('Email or username already exists.')
            return redirect(url_for('admin.add_user'))
        
        # Generate and send OTP
        otp = generate_otp()
        if store_otp(email, otp) and send_otp_email(email, otp):
            session['admin_add_user_data'] = {
                'user_id': user_id,
                'firstname': firstname,
                'lastname': lastname,
                'username': username,
                'password': generate_password_hash(password),
                'user_type': user_type,
                'birthdate': birthdate,
                'address': address,
                'mobile': mobile,
                'email': email
            }
            Alert_Success('OTP sent to the email. Please verify to add user.')
            return redirect(url_for('admin.verify_add_user_otp'))
        else:
            Alert_Fail('Failed to send OTP. Try again.')
            return redirect(url_for('admin.add_user'))
    
    return render_template('admin/add_user.html')

@admin_bp.route('/verify_add_user_otp', methods=['GET', 'POST'])
@login_required
@admin_required
def verify_add_user_otp():
    if 'admin_add_user_data' not in session:
        return redirect(url_for('admin.add_user'))
    
    if request.method == 'POST':
        otp = request.form.get('otp')
        email = session['admin_add_user_data']['email']
        
        if verify_otp(email, otp):
            # Create user
            data = session['admin_add_user_data']
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO user_tb (user_id, firstname, lastname, username, password, user_type, birthdate, address, mobile_number, email) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                               (data['user_id'], data['firstname'], data['lastname'], data['username'], data['password'], data['user_type'], data['birthdate'], data['address'], data['mobile'], data['email']))
                conn.commit()
                conn.close()
                session.pop('admin_add_user_data', None)
                Alert_Success('User added successfully.')
                return redirect(url_for('admin.admin_dashboard'))
            else:
                Alert_Fail('Database error.')
        else:
            Alert_Fail('Invalid or expired OTP.')
    
    return render_template('admin/verify_add_user_otp.html')

@admin_bp.route('/resend_add_user_otp')
@login_required
@admin_required
def resend_add_user_otp():
    if 'admin_add_user_data' not in session:
        return redirect(url_for('admin.add_user'))
    
    email = session['admin_add_user_data']['email']
    if can_resend_otp(email):
        otp = generate_otp()
        if store_otp(email, otp) and send_otp_email(email, otp):
            Alert_Success('OTP resent to the email.')
        else:
            Alert_Fail('Failed to resend OTP.')
    else:
        Alert_Fail('Please wait before requesting another OTP.')
    
    return redirect(url_for('admin.verify_add_user_otp'))

@admin_bp.route('/add_game', methods=['GET', 'POST'])
@login_required
@admin_required
def add_game():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        file_path = request.form['file_path']
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO games (name, description, file_path) VALUES (%s, %s, %s)",
                           (name, description, file_path))
            conn.commit()
            conn.close()
            flash('Game added successfully.', 'success')
            return redirect(url_for('admin.admin_dashboard'))
    return render_template('admin/add_game.html')

@admin_bp.route('/user/<user_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
@admin_required
def manage_user(user_id):
    from flask import jsonify
    conn = get_db_connection()
    if request.method == 'GET':
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM user_tb WHERE user_id = %s", (user_id,))
            user = cursor.fetchone()
            conn.close()
            return jsonify(user)
    elif request.method == 'PUT':
        data = request.get_json()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE user_tb SET username=%s, firstname=%s, lastname=%s, user_type=%s, email=%s
                WHERE user_id=%s
            """, (data['username'], data['firstname'], data['lastname'], data['user_type'], data['email'], user_id))
            conn.commit()
            conn.close()
            return jsonify({'success': True})
    elif request.method == 'DELETE':
        if conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user_tb WHERE user_id = %s", (user_id,))
            conn.commit()
            conn.close()
            return jsonify({'success': True})

@admin_bp.route('/user/<user_id>/toggle_active', methods=['POST'])
@login_required
@admin_required
def toggle_active(user_id):
    from flask import jsonify
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        
        # Check if user is admin
        cursor.execute("SELECT user_type, is_active FROM user_tb WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            conn.close()
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Prevent deactivating admin users
        if user['user_type'] == 'admin' and user['is_active']:
            conn.close()
            return jsonify({'success': False, 'message': 'Admin users cannot be deactivated'}), 403
        
        # Toggle active status
        cursor.execute("UPDATE user_tb SET is_active = NOT is_active WHERE user_id = %s", (user_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'User status updated successfully'})

@admin_bp.route('/user/<user_id>/games', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_user_games(user_id):
    from flask import jsonify
    
    if request.method == 'GET':
        # Get directory-scanned games
        scanned_games = scan_games_directory()
        
        # Get user's current game access permissions
        conn = get_db_connection()
        user_access = {}
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT game_filename, is_enabled FROM user_scanned_game_access_tb WHERE user_id = %s", (user_id,))
            access_records = cursor.fetchall()
            user_access = {record['game_filename']: record['is_enabled'] for record in access_records}
            conn.close()
        
        # Build games list with actual access states
        games_with_access = []
        for game in scanned_games:
            game_filename = game['filename']
            # Default to enabled if no record exists, otherwise use stored value
            is_enabled = user_access.get(game_filename, True)
            
            games_with_access.append({
                'id': game_filename,  # Use filename as ID
                'name': game['name'],
                'enabled': is_enabled
            })
        
        return jsonify(games_with_access)
    
    elif request.method == 'POST':
        data = request.get_json()
        enabled_games = data.get('games', [])
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            # Get all scanned games
            scanned_games = scan_games_directory()
            all_game_filenames = [game['filename'] for game in scanned_games]
            
            # Get current user access
            cursor.execute("SELECT game_filename, is_enabled FROM user_scanned_game_access_tb WHERE user_id = %s", (user_id,))
            current_access = {record['game_filename']: record['is_enabled'] for record in cursor.fetchall()}
            
            # Update or insert records for enabled games
            for game_filename in enabled_games:
                if game_filename in all_game_filenames:
                    if game_filename in current_access:
                        # Update existing record if changed
                        if not current_access[game_filename]:
                            cursor.execute(
                                "UPDATE user_scanned_game_access_tb SET is_enabled = %s WHERE user_id = %s AND game_filename = %s",
                                (True, user_id, game_filename)
                            )
                    else:
                        # Insert new record for enabled game
                        cursor.execute(
                            "INSERT INTO user_scanned_game_access_tb (user_id, game_filename, is_enabled) VALUES (%s, %s, %s)",
                            (user_id, game_filename, True)
                        )
            
            # Update or insert records for disabled games
            for game_filename in all_game_filenames:
                if game_filename not in enabled_games:
                    if game_filename in current_access:
                        # Update existing record if changed
                        if current_access[game_filename]:
                            cursor.execute(
                                "UPDATE user_scanned_game_access_tb SET is_enabled = %s WHERE user_id = %s AND game_filename = %s",
                                (False, user_id, game_filename)
                            )
                    else:
                        # Insert new record for disabled game
                        cursor.execute(
                            "INSERT INTO user_scanned_game_access_tb (user_id, game_filename, is_enabled) VALUES (%s, %s, %s)",
                            (user_id, game_filename, False)
                        )
            
            conn.commit()
            conn.close()
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Database connection failed'}), 500

@admin_bp.route('/reset_leaderboard/<int:game_id>', methods=['POST'])
@login_required
@admin_required
def reset_leaderboard(game_id):
    from MyFlaskapp.db import delete_scores_for_game
    if delete_scores_for_game(game_id):
        flash('Leaderboard reset successfully.', 'success')
    else:
        flash('Failed to reset leaderboard.', 'danger')
    return redirect(url_for('admin.admin_dashboard'))