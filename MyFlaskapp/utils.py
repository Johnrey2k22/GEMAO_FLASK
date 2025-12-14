from flask import flash
import re
import random
import string
from datetime import datetime, timedelta
from flask_mail import Message, Mail
from MyFlaskapp.db import get_db_connection

mail = Mail()

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

def send_otp_email(email, otp):
    msg = Message('Your OTP Verification Code', recipients=[email])
    msg.body = f'Your OTP code is: {otp}. It expires in 10 minutes.'
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def store_otp(email, otp):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        expires_at = datetime.now() + timedelta(minutes=10)
        cursor.execute("INSERT INTO otp_verification (email, otp, expires_at) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE otp=%s, expires_at=%s, verified=FALSE",
                       (email, otp, expires_at, otp, expires_at))
        conn.commit()
        conn.close()
        return True
    return False

def verify_otp(email, otp):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM otp_verification WHERE email = %s AND otp = %s AND expires_at > NOW() AND verified = FALSE",
                       (email, otp))
        record = cursor.fetchone()
        if record:
            cursor.execute("UPDATE otp_verification SET verified = TRUE WHERE id = %s", (record['id'],))
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
            return time_diff.total_seconds() > 60  # 1 minute throttle
        return True
    return False
