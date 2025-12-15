"""
Rate limiting utilities for authentication endpoints
"""
from datetime import datetime, timedelta
from flask import session, current_app
from functools import wraps
import time

class RateLimiter:
    def __init__(self):
        self.attempts = {}  # In-memory storage for attempts
    
    def is_rate_limited(self, key, max_attempts, window_seconds):
        """Check if the key has exceeded rate limit"""
        now = time.time()
        
        if key not in self.attempts:
            self.attempts[key] = []
        
        # Remove old attempts outside the window
        self.attempts[key] = [
            attempt_time for attempt_time in self.attempts[key]
            if now - attempt_time < window_seconds
        ]
        
        # Check if under limit
        if len(self.attempts[key]) < max_attempts:
            self.attempts[key].append(now)
            return False
        
        return True
    
    def get_remaining_time(self, key, window_seconds):
        """Get remaining time until rate limit resets"""
        if key not in self.attempts or not self.attempts[key]:
            return 0
        
        oldest_attempt = min(self.attempts[key])
        reset_time = oldest_attempt + window_seconds
        remaining = max(0, reset_time - time.time())
        return int(remaining)

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(max_attempts=None, window_seconds=None, key_func=None):
    """
    Rate limiting decorator
    
    Args:
        max_attempts: Maximum number of attempts (from config if None)
        window_seconds: Time window in seconds (from config if None)
        key_func: Function to generate rate limit key (IP-based if None)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Use config values if not specified
            if max_attempts is None:
                max_attempts_config = current_app.config.get('MAX_LOGIN_ATTEMPTS', 5)
            else:
                max_attempts_config = max_attempts
                
            if window_seconds is None:
                window_seconds_config = current_app.config.get('LOGIN_ATTEMPT_TIMEOUT_MINUTES', 5)
            else:
                window_seconds_config = window_seconds
            
            # Generate rate limit key
            if key_func is None:
                # Use IP address as key
                from flask import request
                key = request.remote_addr
            else:
                key = key_func()
            
            print(f"DEBUG: Rate limit check - Key: {key}, Attempts: {len(rate_limiter.attempts.get(key, []))}, Max: {max_attempts_config}")
            
            # Check rate limit
            if rate_limiter.is_rate_limited(key, max_attempts_config, window_seconds_config):
                print(f"DEBUG: Rate limit exceeded for key: {key}")
                remaining_time = rate_limiter.get_remaining_time(key, window_seconds_config)
                
                # Check if this is an AJAX request
                from flask import request
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    from flask import jsonify
                    return jsonify({
                        'status': 'fail',
                        'message': f'Too many attempts. Please wait {remaining_time} seconds before trying again.'
                    }), 429
                
                # For non-AJAX requests
                # from flask import flash
                # flash(f'Too many attempts. Please wait {remaining_time} seconds before trying again.', 'danger')
                
                # For login attempts, redirect to landing page
                if f.__name__ == 'login':
                    from flask import redirect, url_for
                    return redirect(url_for('index'))
                else:
                    # For other endpoints, return error response
                    from flask import jsonify
                    return jsonify({
                        'success': False,
                        'message': f'Rate limit exceeded. Try again in {remaining_time} seconds.'
                    }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def otp_rate_limit(max_attempts=None, window_seconds=None):
    """Specific rate limiter for OTP requests"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Use OTP-specific config
            max_attempts_config = max_attempts or 3  # Max 3 OTP attempts per email
            window_seconds_config = window_seconds or current_app.config.get('OTP_EXPIRY_MINUTES', 10) * 60
            
            # Use email as key for OTP
            if 'registration_data' in session:
                email = session['registration_data'].get('email', '')
                key = f"otp_{email}"
            else:
                from flask import request
                key = f"otp_{request.remote_addr}"
            
            if rate_limiter.is_rate_limited(key, max_attempts_config, window_seconds_config):
                remaining_time = rate_limiter.get_remaining_time(key, window_seconds_config)
                # from flask import flash
                # flash(f'Too many OTP attempts. Please wait {remaining_time} seconds.', 'danger')
                return redirect(url_for('auth.register'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
