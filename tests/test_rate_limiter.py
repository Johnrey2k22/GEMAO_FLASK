import os
import sys

# Ensure the repository root is on sys.path so tests can import the MyFlaskapp package
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
import time
from MyFlaskapp.rate_limiter import RateLimiter, rate_limit, otp_rate_limit, rate_limiter

class TestRateLimiter:
    def setup_method(self):
        """Reset rate limiter before each test."""
        rate_limiter.attempts.clear()

    def test_is_rate_limited_under_limit(self):
        """Test rate limiting when under the limit."""
        key = 'test_key'
        result = rate_limiter.is_rate_limited(key, 5, 60)
        assert result is False
        assert len(rate_limiter.attempts[key]) == 1

    def test_is_rate_limited_over_limit(self):
        """Test rate limiting when over the limit."""
        key = 'test_key'
        max_attempts = 3
        
        # Add attempts up to the limit
        for i in range(max_attempts):
            result = rate_limiter.is_rate_limited(key, max_attempts, 60)
            assert result is False
        
        # Next attempt should be rate limited
        result = rate_limiter.is_rate_limited(key, max_attempts, 60)
        assert result is True

    def test_is_rate_limited_window_expires(self):
        """Test rate limiting when time window expires."""
        key = 'test_key'
        max_attempts = 2
        window_seconds = 1  # 1 second window
        
        # Add attempts up to the limit
        for i in range(max_attempts):
            result = rate_limiter.is_rate_limited(key, max_attempts, window_seconds)
            assert result is False
        
        # Next attempt should be rate limited
        result = rate_limiter.is_rate_limited(key, max_attempts, window_seconds)
        assert result is True
        
        # Wait for window to expire
        time.sleep(1.1)
        
        # Should be allowed again
        result = rate_limiter.is_rate_limited(key, max_attempts, window_seconds)
        assert result is False

    def test_get_remaining_time_no_attempts(self):
        """Test remaining time with no attempts."""
        key = 'test_key'
        remaining = rate_limiter.get_remaining_time(key, 60)
        assert remaining == 0

    def test_get_remaining_time_with_attempts(self):
        """Test remaining time with existing attempts."""
        key = 'test_key'
        window_seconds = 60
        
        # Add an attempt
        rate_limiter.is_rate_limited(key, 5, window_seconds)
        
        remaining = rate_limiter.get_remaining_time(key, window_seconds)
        assert 0 < remaining <= 60

    def test_get_remaining_time_expired_attempts(self):
        """Test remaining time with expired attempts."""
        key = 'test_key'
        window_seconds = 1
        
        # Add an attempt
        rate_limiter.is_rate_limited(key, 5, window_seconds)
        
        # Wait for expiration
        time.sleep(1.1)
        
        remaining = rate_limiter.get_remaining_time(key, window_seconds)
        assert remaining == 0

class TestRateLimitDecorator:
    def setup_method(self):
        """Reset rate limiter before each test."""
        rate_limiter.attempts.clear()

    def test_rate_limit_decorator_under_limit(self):
        """Test rate limit decorator when under limit."""
        app = Flask(__name__)
        app.config['MAX_LOGIN_ATTEMPTS'] = 5
        app.config['LOGIN_ATTEMPT_TIMEOUT_MINUTES'] = 5
        
        with app.test_request_context('/'):
            @rate_limit(max_attempts=5, window_seconds=60)
            def test_function():
                return "success"
            
            result = test_function()
            assert result == "success"

    def test_rate_limit_decorator_over_limit(self):
        """Test rate limit decorator when over limit."""
        app = Flask(__name__)
        app.config['MAX_LOGIN_ATTEMPTS'] = 2
        app.config['LOGIN_ATTEMPT_TIMEOUT_MINUTES'] = 5
        
        with app.test_request_context('/'):
            @rate_limit(max_attempts=2, window_seconds=60)
            def test_function():
                return "success"
            
            # First two attempts should succeed
            assert test_function() == "success"
            assert test_function() == "success"
            
            # Third attempt should be rate limited
            result = test_function()
            assert result[1] == 429  # HTTP 429 Too Many Requests

    def test_rate_limit_decorator_ajax_request(self):
        """Test rate limit decorator with AJAX request."""
        app = Flask(__name__)
        app.config['MAX_LOGIN_ATTEMPTS'] = 1
        app.config['LOGIN_ATTEMPT_TIMEOUT_MINUTES'] = 5
        
        with app.test_request_context('/', headers={'X-Requested-With': 'XMLHttpRequest'}):
            @rate_limit(max_attempts=1, window_seconds=60)
            def test_function():
                return "success"
            
            # First attempt succeeds
            assert test_function() == "success"
            
            # Second attempt should return JSON error
            result = test_function()
            assert result[1] == 429
            json_data = result[0].get_json()
            assert json_data['status'] == 'fail'
            assert 'Too many attempts' in json_data['message']

    def test_rate_limit_decorator_login_redirect(self):
        """Test rate limit decorator redirects login attempts."""
        app = Flask(__name__)
        app.config['MAX_LOGIN_ATTEMPTS'] = 1
        app.config['LOGIN_ATTEMPT_TIMEOUT_MINUTES'] = 5
        
        # Add a dummy index route for testing
        @app.route('/')
        def index():
            return "index page"
        
        with app.test_request_context('/'):
            @rate_limit(max_attempts=1, window_seconds=60)
            def login():
                return "login page"
            
            # First attempt succeeds
            assert login() == "login page"
            
            # Second attempt should redirect
            result = login()
            assert result.status_code == 302  # Redirect

    def test_rate_limit_decorator_custom_key_func(self):
        """Test rate limit decorator with custom key function."""
        app = Flask(__name__)
        app.config['MAX_LOGIN_ATTEMPTS'] = 2
        app.config['LOGIN_ATTEMPT_TIMEOUT_MINUTES'] = 5
        
        with app.test_request_context('/'):
            @rate_limit(max_attempts=2, window_seconds=60, key_func=lambda: 'custom_key')
            def test_function():
                return "success"
            
            # Should use custom key
            assert test_function() == "success"
            assert 'custom_key' in rate_limiter.attempts

    def test_rate_limit_decorator_default_config(self):
        """Test rate limit decorator uses default config."""
        app = Flask(__name__)
        app.config['MAX_LOGIN_ATTEMPTS'] = 10
        app.config['LOGIN_ATTEMPT_TIMEOUT_MINUTES'] = 15
        
        with app.test_request_context('/'):
            @rate_limit()  # Use defaults
            def test_function():
                return "success"
            
            # Should use config values
            assert test_function() == "success"

class TestOTPRateLimit:
    def setup_method(self):
        """Reset rate limiter before each test."""
        rate_limiter.attempts.clear()

    def test_otp_rate_limit_with_session_data(self):
        """Test OTP rate limit with session data."""
        app = Flask(__name__)
        app.config['OTP_EXPIRY_MINUTES'] = 10
        app.config['SECRET_KEY'] = 'test-secret-key'
        
        with app.test_client(use_cookies=True) as client:
            with client.session_transaction() as sess:
                sess['registration_data'] = {'email': 'test@example.com'}
            
            @otp_rate_limit(max_attempts=3, window_seconds=600)
            def otp_function():
                return "otp_sent"
            
            with app.test_request_context('/'):
                # First attempt should succeed
                result = otp_function()
                assert result == "otp_sent"

    def test_otp_rate_limit_without_session_data(self):
        """Test OTP rate limit without session data."""
        app = Flask(__name__)
        app.config['OTP_EXPIRY_MINUTES'] = 10
        
        with app.test_request_context('/'):
            @otp_rate_limit(max_attempts=3, window_seconds=600)
            def otp_function():
                return "otp_sent"
            
            # Should use IP as key
            result = otp_function()
            assert result == "otp_sent"

    def test_otp_rate_limit_exceeded(self):
        """Test OTP rate limit when exceeded."""
        app = Flask(__name__)
        app.config['OTP_EXPIRY_MINUTES'] = 10
        app.config['SECRET_KEY'] = 'test-secret-key'
        
        # Add a dummy register route for testing
        @app.route('/register', endpoint='auth.register')
        def register():
            return "register page"
        
        with app.test_client(use_cookies=True) as client:
            with client.session_transaction() as sess:
                sess['registration_data'] = {'email': 'test@example.com'}
            
            @otp_rate_limit(max_attempts=2, window_seconds=600)
            def otp_function():
                return "otp_sent"
            
            with app.test_request_context('/'):
                # First two attempts should succeed
                assert otp_function() == "otp_sent"
                assert otp_function() == "otp_sent"
                
                # Third attempt should be rate limited
                result = otp_function()
                assert result.status_code == 302  # Redirect to register

    def test_otp_rate_limit_default_config(self):
        """Test OTP rate limit uses default config."""
        app = Flask(__name__)
        app.config['OTP_EXPIRY_MINUTES'] = 5
        
        with app.test_request_context('/'):
            @otp_rate_limit()  # Use defaults
            def otp_function():
                return "otp_sent"
            
            # Should use config values
            result = otp_function()
            assert result == "otp_sent"

class TestRateLimiterIntegration:
    def setup_method(self):
        """Reset rate limiter before each test."""
        rate_limiter.attempts.clear()

    def test_multiple_keys_independent(self):
        """Test that different keys are rate limited independently."""
        key1 = 'user1'
        key2 = 'user2'
        max_attempts = 2
        
        # Exhaust limit for key1
        for i in range(max_attempts):
            rate_limiter.is_rate_limited(key1, max_attempts, 60)
        
        # key1 should be rate limited
        assert rate_limiter.is_rate_limited(key1, max_attempts, 60) is True
        
        # key2 should still be allowed
        assert rate_limiter.is_rate_limited(key2, max_attempts, 60) is False

    def test_concurrent_attempts(self):
        """Test rate limiting with concurrent-like attempts."""
        key = 'concurrent_test'
        max_attempts = 5
        window_seconds = 60
        
        # Add multiple attempts quickly
        start_time = time.time()
        for i in range(max_attempts):
            result = rate_limiter.is_rate_limited(key, max_attempts, window_seconds)
            assert result is False
        
        # All attempts should be within the window
        assert time.time() - start_time < 1
        
        # Next attempt should be rate limited
        assert rate_limiter.is_rate_limited(key, max_attempts, window_seconds) is True

    def test_cleanup_old_attempts(self):
        """Test that old attempts are cleaned up."""
        key = 'cleanup_test'
        max_attempts = 3
        window_seconds = 1  # Very short window
        
        # Add attempts
        for i in range(max_attempts):
            rate_limiter.is_rate_limited(key, max_attempts, window_seconds)
        
        assert len(rate_limiter.attempts[key]) == max_attempts
        
        # Wait for window to expire
        time.sleep(1.1)
        
        # Add new attempt - should clean up old ones
        rate_limiter.is_rate_limited(key, max_attempts, window_seconds)
        
        # Should only have the new attempt
        assert len(rate_limiter.attempts[key]) == 1
