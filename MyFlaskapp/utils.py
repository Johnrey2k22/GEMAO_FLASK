from flask import flash
import re
import random
import string
from datetime import datetime, timedelta
from flask_mail import Message
from MyFlaskapp.db import get_db_connection

def Alert_Success(message):
    flash(message, 'success')

def Alert_Fail(message):
    flash(message, 'fail')

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character."
    return True, "Password is valid."

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

def send_otp_email(email, otp, mail):
    if not mail:
        print("Error: Mail service not configured")
        return False
    
    if not mail.username or not mail.password:
        print("Error: Mail credentials not configured - check MAIL_USERNAME and MAIL_PASSWORD environment variables")
        return False
    
    msg = Message('Your OTP Verification Code', recipients=[email])
    msg.body = f'Your OTP code is: {otp}. It expires in 10 minutes.'
    try:
        mail.send(msg)
        print(f"OTP email sent successfully to {email}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def store_otp(email, otp):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO otp_verification (email, otp, created_at, expires_at, verified) "
            "VALUES (%s, %s, NOW(), DATE_ADD(NOW(), INTERVAL 10 MINUTE), FALSE)",
            (email, otp)
        )
        conn.commit()
        conn.close()
        return True
    return False

def verify_otp(email, otp):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id
            FROM otp_verification 
            WHERE email = %s AND otp = %s AND expires_at > NOW() AND verified = FALSE
        """, (email, otp))
        record = cursor.fetchone()
        if record:
            record_id = record.get('id') if isinstance(record, dict) else None
            if record_id is not None:
                cursor.execute("UPDATE otp_verification SET verified = TRUE WHERE id = %s", (record_id,))
                conn.commit()
            conn.close()
            return True
        conn.close()
    return False

def check_duplicate_user(email, username):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_tb WHERE email = %s OR username = %s", (email, username))
        user = cursor.fetchone()
        conn.close()
        return user is not None
    return False

def can_resend_otp(email):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT created_at FROM otp_verification WHERE email = %s ORDER BY created_at DESC LIMIT 1", (email,))
        record = cursor.fetchone()
        conn.close()
        if record:
            last_sent = record['created_at']
            if isinstance(last_sent, str):
                last_sent = datetime.fromisoformat(last_sent.replace('Z', '+00:00'))
            time_diff = datetime.now() - last_sent
            return time_diff.total_seconds() > 60
        return True
    return False
