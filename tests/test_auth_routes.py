import pytest
import sys
import os
from flask import session
from unittest.mock import patch, MagicMock

# Add the project root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from MyFlaskapp import create_app
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_db():
    with patch('MyFlaskapp.auth.routes.get_db_connection') as mock:
        yield mock

class TestAuthRoutes:
    def test_login_get(self, client):
        """Test GET request to login page."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower()

    def test_login_success_admin(self, client, mock_db):
        """Test successful admin login."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {
            'user_id': 'admin123',
            'firstname': 'Admin',
            'lastname': 'User',
            'username': 'admin',
            'password': generate_password_hash('admin123'),
            'user_type': 'admin'
        }
        
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        assert response.status_code == 302
        assert b'admin' in response.data

    def test_login_success_regular_user(self, client, mock_db):
        """Test successful regular user login."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {
            'user_id': 'user123',
            'firstname': 'Regular',
            'lastname': 'User',
            'username': 'user',
            'password': generate_password_hash('user123'),
            'user_type': 'user'
        }
        
        response = client.post('/login', data={
            'username': 'user',
            'password': 'user123'
        })
        assert response.status_code == 302

    def test_login_invalid_credentials(self, client, mock_db):
        """Test login with invalid credentials."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        response = client.post('/login', data={
            'username': 'invalid',
            'password': 'invalid'
        })
        assert response.status_code == 200

    def test_login_ajax_success(self, client, mock_db):
        """Test AJAX login success."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {
            'user_id': 'user123',
            'firstname': 'Test',
            'lastname': 'User',
            'username': 'test',
            'password': generate_password_hash('test123'),
            'user_type': 'user'
        }
        
        response = client.post('/login', data={
            'username': 'test',
            'password': 'test123'
        }, headers={'X-Requested-With': 'XMLHttpRequest'})
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['status'] == 'success'

    def test_logout(self, client):
        """Test logout functionality."""
        with client.session_transaction() as sess:
            sess['user_id'] = 'test123'
        
        response = client.get('/logout')
        assert response.status_code == 302
        assert 'user_id' not in session

    def test_register_get(self, client):
        """Test GET request to registration page."""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'register' in response.data.lower()

    @patch('MyFlaskapp.auth.routes.check_duplicate_user')
    @patch('MyFlaskapp.auth.routes.store_otp')
    @patch('MyFlaskapp.auth.routes.send_otp_email')
    @patch('MyFlaskapp.auth.routes.generate_otp')
    def test_register_success(self, mock_otp, mock_send, mock_store, mock_check, client):
        """Test successful registration."""
        mock_otp.return_value = '123456'
        mock_store.return_value = True
        mock_send.return_value = True
        mock_check.return_value = False
        
        response = client.post('/register', data={
            'firstname': 'John',
            'lastname': 'Doe',
            'username': 'johndoe',
            'email': 'john@example.com',
            'password': 'ValidPass123!',
            'confirm_password': 'ValidPass123!',
            'birthdate': '1990-01-01',
            'address': '123 Test St',
            'mobile': '1234567890'
        })
        assert response.status_code == 302

    def test_register_missing_fields(self, client):
        """Test registration with missing fields."""
        response = client.post('/register', data={
            'firstname': 'John',
            'lastname': ''
        })
        assert response.status_code == 302

    @patch('MyFlaskapp.auth.routes.verify_otp')
    @patch('MyFlaskapp.auth.routes.get_db_connection')
    def test_verify_otp_success(self, mock_db, mock_verify, client):
        """Test successful OTP verification."""
        with client.session_transaction() as sess:
            sess['registration_data'] = {
                'firstname': 'John',
                'lastname': 'Doe',
                'username': 'johndoe',
                'email': 'john@example.com',
                'password': 'hashed_password',
                'birthdate': '1990-01-01',
                'address': '123 Test St',
                'mobile': '1234567890'
            }
        
        mock_verify.return_value = True
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        response = client.post('/verify_otp', data={'otp': '123456'})
        assert response.status_code == 302

    def test_verify_otp_no_session_data(self, client):
        """Test OTP verification without session data."""
        response = client.post('/verify_otp', data={'otp': '123456'})
        assert response.status_code == 302

    @patch('MyFlaskapp.auth.routes.can_resend_otp')
    @patch('MyFlaskapp.auth.routes.store_otp')
    @patch('MyFlaskapp.auth.routes.send_otp_email')
    @patch('MyFlaskapp.auth.routes.generate_otp')
    def test_resend_otp_success(self, mock_otp, mock_send, mock_store, mock_can, client):
        """Test successful OTP resend."""
        with client.session_transaction() as sess:
            sess['registration_data'] = {'email': 'test@example.com'}
        
        mock_otp.return_value = '123456'
        mock_store.return_value = True
        mock_send.return_value = True
        mock_can.return_value = True
        
        response = client.get('/resend_otp')
        assert response.status_code == 302

    def test_profile_get_unauthenticated(self, client):
        """Test profile access without authentication."""
        response = client.get('/profile')
        assert response.status_code == 302

    @patch('MyFlaskapp.auth.routes.get_db_connection')
    def test_profile_get_authenticated(self, mock_db, client):
        """Test profile access with authentication."""
        with client.session_transaction() as sess:
            sess['user_id'] = 'test123'
            sess['user_role'] = 'user'
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {
            'user_id': 'test123',
            'firstname': 'John',
            'lastname': 'Doe',
            'username': 'johndoe',
            'email': 'john@example.com'
        }
        
        response = client.get('/profile')
        assert response.status_code == 200

    @patch('MyFlaskapp.auth.routes.get_db_connection')
    def test_profile_update_success(self, mock_db, client):
        """Test successful profile update."""
        with client.session_transaction() as sess:
            sess['user_id'] = 'test123'
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None  # No duplicate user
        
        response = client.post('/profile', json={
            'firstname': 'John',
            'lastname': 'Doe',
            'username': 'johndoe',
            'email': 'john@example.com',
            'mobile': '1234567890',
            'birthdate': '1990-01-01',
            'address': '123 Test St'
        })
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True

    def test_test_endpoint(self, client):
        """Test the test endpoint."""
        response = client.get('/test')
        assert response.status_code == 200
        assert response.data == b'Test endpoint working'
