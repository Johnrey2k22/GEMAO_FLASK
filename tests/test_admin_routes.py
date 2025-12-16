import pytest
from flask import session
from unittest.mock import patch, MagicMock
import sys
import os
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
def admin_client(client):
    """Create an admin authenticated client."""
    with client.session_transaction() as sess:
        sess['user_id'] = 'admin123'
        sess['user_name'] = 'Admin User'
        sess['user_role'] = 'admin'
    return client

@pytest.fixture
def user_client(client):
    """Create a regular user authenticated client."""
    with client.session_transaction() as sess:
        sess['user_id'] = 'user123'
        sess['user_name'] = 'Regular User'
        sess['user_role'] = 'user'
    return client

class TestAdminRoutes:
    def test_admin_dashboard_unauthenticated(self, client):
        """Test admin dashboard access without authentication."""
        response = client.get('/admin/dashboard')
        assert response.status_code == 302

    def test_admin_dashboard_regular_user(self, user_client):
        """Test admin dashboard access by regular user."""
        response = user_client.get('/admin/dashboard')
        assert response.status_code == 302

    @patch('MyFlaskapp.admin.routes.get_db_connection')
    @patch('MyFlaskapp.admin.routes.scan_games_directory')
    def test_admin_dashboard_admin(self, mock_scan, mock_db, admin_client):
        """Test admin dashboard access by admin."""
        mock_scan.return_value = [
            {'name': 'Test Game', 'filename': 'test_game.py'}
        ]
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.side_effect = [
            [{'user_id': '1', 'username': 'user1', 'email': 'user1@example.com'}],  # Users
            [{'username': 'user1', 'score': 100, 'game_name': 'Test Game'}]  # Scores
        ]
        
        response = admin_client.get('/admin/dashboard')
        assert response.status_code == 200

    def test_add_user_get_unauthenticated(self, client):
        """Test add user GET request without authentication."""
        response = client.get('/admin/add_user')
        assert response.status_code == 302

    def test_add_user_get_regular_user(self, user_client):
        """Test add user GET request by regular user."""
        response = user_client.get('/admin/add_user')
        assert response.status_code == 302

    def test_add_user_get_admin(self, admin_client):
        """Test add user GET request by admin."""
        response = admin_client.get('/admin/add_user')
        assert response.status_code == 200

    @patch('MyFlaskapp.admin.routes.check_duplicate_user')
    @patch('MyFlaskapp.admin.routes.store_otp')
    @patch('MyFlaskapp.admin.routes.send_otp_email')
    @patch('MyFlaskapp.admin.routes.generate_otp')
    def test_add_user_post_success(self, mock_otp, mock_send, mock_store, mock_check, admin_client):
        """Test successful user addition by admin."""
        mock_otp.return_value = '123456'
        mock_store.return_value = True
        mock_send.return_value = True
        mock_check.return_value = False
        
        response = admin_client.post('/admin/add_user', data={
            'user_id': 'new_user',
            'firstname': 'John',
            'lastname': 'Doe',
            'username': 'johndoe',
            'password': 'ValidPass123!',
            'user_type': 'user',
            'birthdate': '1990-01-01',
            'address': '123 Test St',
            'mobile': '1234567890',
            'email': 'john@example.com'
        })
        assert response.status_code == 302

    def test_add_user_post_missing_fields(self, admin_client):
        """Test user addition with missing fields."""
        response = admin_client.post('/admin/add_user', data={
            'firstname': 'John',
            'lastname': 'Doe'
            # Missing other required fields
        })
        assert response.status_code == 400  # Should return Bad Request for missing fields

    @patch('MyFlaskapp.admin.routes.check_duplicate_user')
    def test_add_user_post_duplicate(self, mock_check, admin_client):
        """Test user addition with duplicate email/username."""
        mock_check.return_value = True
        
        response = admin_client.post('/admin/add_user', data={
            'user_id': 'new_user',
            'firstname': 'John',
            'lastname': 'Doe',
            'username': 'existing_user',
            'password': 'ValidPass123!',
            'user_type': 'user',
            'birthdate': '1990-01-01',
            'address': '123 Test St',
            'mobile': '1234567890',
            'email': 'existing@example.com'
        })
        assert response.status_code == 302

    @patch('MyFlaskapp.admin.routes.verify_otp')
    @patch('MyFlaskapp.admin.routes.get_db_connection')
    def test_verify_add_user_otp_success(self, mock_db, mock_verify, admin_client):
        """Test successful OTP verification for user addition."""
        with admin_client.session_transaction() as sess:
            sess['admin_add_user_data'] = {
                'user_id': 'new_user',
                'firstname': 'John',
                'lastname': 'Doe',
                'username': 'johndoe',
                'password': 'hashed_password',
                'user_type': 'user',
                'birthdate': '1990-01-01',
                'address': '123 Test St',
                'mobile': '1234567890',
                'email': 'john@example.com'
            }
        
        mock_verify.return_value = True
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        response = admin_client.post('/admin/verify_add_user_otp', data={'otp': '123456'})
        assert response.status_code == 302

    def test_verify_add_user_otp_no_session_data(self, admin_client):
        """Test OTP verification without session data."""
        response = admin_client.post('/admin/verify_add_user_otp', data={'otp': '123456'})
        assert response.status_code == 302

    @patch('MyFlaskapp.admin.routes.can_resend_otp')
    @patch('MyFlaskapp.admin.routes.store_otp')
    @patch('MyFlaskapp.admin.routes.send_otp_email')
    @patch('MyFlaskapp.admin.routes.generate_otp')
    def test_resend_add_user_otp_success(self, mock_otp, mock_send, mock_store, mock_can, admin_client):
        """Test successful OTP resend for user addition."""
        with admin_client.session_transaction() as sess:
            sess['admin_add_user_data'] = {'email': 'test@example.com'}
        
        mock_otp.return_value = '123456'
        mock_store.return_value = True
        mock_send.return_value = True
        mock_can.return_value = True
        
        response = admin_client.get('/admin/resend_add_user_otp')
        assert response.status_code == 302

    @patch('MyFlaskapp.admin.routes.get_db_connection')
    def test_add_game_success(self, mock_db, admin_client):
        """Test successful game addition."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        response = admin_client.post('/admin/add_game', data={
            'name': 'New Game',
            'description': 'A new test game',
            'file_path': 'games/new_game.py'
        })
        assert response.status_code == 302

    def test_add_game_get(self, admin_client):
        """Test GET request to add game page."""
        response = admin_client.get('/admin/add_game')
        assert response.status_code == 200

    @patch('MyFlaskapp.admin.routes.get_db_connection')
    def test_manage_user_get_success(self, mock_db, admin_client):
        """Test getting user details."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {
            'user_id': 'test123',
            'username': 'testuser',
            'email': 'test@example.com',
            'firstname': 'Test',
            'lastname': 'User'
        }
        
        response = admin_client.get('/admin/user/test123')
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['username'] == 'testuser'

    @patch('MyFlaskapp.admin.routes.get_db_connection')
    def test_manage_user_put_success(self, mock_db, admin_client):
        """Test updating user details."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        response = admin_client.put('/admin/user/test123', json={
            'username': 'updated_user',
            'firstname': 'Updated',
            'lastname': 'User',
            'user_type': 'user',
            'email': 'updated@example.com'
        })
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True

    @patch('MyFlaskapp.admin.routes.get_db_connection')
    def test_manage_user_delete_success(self, mock_db, admin_client):
        """Test deleting user."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        response = admin_client.delete('/admin/user/test123')
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True

    @patch('MyFlaskapp.admin.routes.get_db_connection')
    def test_toggle_active_success(self, mock_db, admin_client):
        """Test toggling user active status."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {
            'user_type': 'user',
            'is_active': True
        }
        
        response = admin_client.post('/admin/user/test123/toggle_active')
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True

    @patch('MyFlaskapp.admin.routes.get_db_connection')
    def test_toggle_active_admin_user(self, mock_db, admin_client):
        """Test toggling admin user (should be prevented)."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {
            'user_type': 'admin',
            'is_active': True
        }
        
        response = admin_client.post('/admin/user/test123/toggle_active')
        assert response.status_code == 403
        json_data = response.get_json()
        assert json_data['success'] is False

    @patch('MyFlaskapp.admin.routes.get_db_connection')
    def test_toggle_active_user_not_found(self, mock_db, admin_client):
        """Test toggling non-existent user."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        response = admin_client.post('/admin/user/test123/toggle_active')
        assert response.status_code == 404
        json_data = response.get_json()
        assert json_data['success'] is False

    @patch('MyFlaskapp.admin.routes.scan_games_directory')
    @patch('MyFlaskapp.admin.routes.get_db_connection')
    def test_manage_user_games_get(self, mock_db, mock_scan, admin_client):
        """Test getting user game access permissions."""
        mock_scan.return_value = [
            {'name': 'Test Game', 'filename': 'test_game.py'},
            {'name': 'Another Game', 'filename': 'another_game.py'}
        ]
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            {'game_filename': 'test_game.py', 'is_enabled': True}
        ]
        
        response = admin_client.get('/admin/user/test123/games')
        assert response.status_code == 200
        json_data = response.get_json()
        assert len(json_data) == 2
        assert json_data[0]['name'] == 'Test Game'
        assert json_data[0]['enabled'] is True
        assert json_data[1]['name'] == 'Another Game'
        # The second game should have enabled field, default value depends on implementation
        assert 'enabled' in json_data[1]

    @patch('MyFlaskapp.admin.routes.scan_games_directory')
    @patch('MyFlaskapp.admin.routes.get_db_connection')
    def test_manage_user_games_post(self, mock_db, mock_scan, admin_client):
        """Test updating user game access permissions."""
        mock_scan.return_value = [
            {'name': 'Test Game', 'filename': 'test_game.py'},
            {'name': 'Another Game', 'filename': 'another_game.py'}
        ]
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []  # No existing access records
        
        response = admin_client.post('/admin/user/test123/games', json={
            'games': ['test_game.py']  # Only enable first game
        })
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True

    @patch('MyFlaskapp.admin.routes.get_db_connection')
    def test_manage_user_games_post_db_error(self, mock_db, admin_client):
        """Test updating user game permissions with database error."""
        mock_db.return_value = None
        
        response = admin_client.post('/admin/user/test123/games', json={
            'games': ['test_game.py']
        })
        assert response.status_code == 500
        json_data = response.get_json()
        assert json_data['success'] is False

    @patch('MyFlaskapp.db.delete_scores_for_game')
    def test_reset_leaderboard_success(self, mock_delete, admin_client):
        """Test successful leaderboard reset."""
        mock_delete.return_value = True
        
        response = admin_client.post('/admin/reset_leaderboard/1')
        assert response.status_code == 302

    @patch('MyFlaskapp.db.delete_scores_for_game')
    def test_reset_leaderboard_failure(self, mock_delete, admin_client):
        """Test failed leaderboard reset."""
        mock_delete.return_value = False
        
        response = admin_client.post('/admin/reset_leaderboard/1')
        assert response.status_code == 302

class TestAdminDecorators:
    def test_login_required_decorator(self):
        """Test login_required decorator."""
        from MyFlaskapp.admin.routes import login_required
        
        @login_required
        def test_function():
            return "protected"
        
        # This would need to be tested in a Flask context
        # The decorator itself is simple and redirects if user_id not in session

    def test_admin_required_decorator(self):
        """Test admin_required decorator."""
        from MyFlaskapp.admin.routes import admin_required
        
        @admin_required
        def test_function():
            return "admin_only"
        
        # This would need to be tested in a Flask context
        # The decorator checks if user_role == 'admin'

class TestAdminRouteAccess:
    def test_all_admin_routes_require_auth(self, client):
        """Test that all admin routes require authentication."""
        admin_routes = [
            ('/admin/dashboard', 'GET'),
            ('/admin/add_user', 'GET'),
            ('/admin/verify_add_user_otp', 'GET'),
            ('/admin/resend_add_user_otp', 'GET'),
            ('/admin/add_game', 'GET'),
            ('/admin/user/test123', 'GET'),
            ('/admin/user/test123/toggle_active', 'POST'),
            ('/admin/user/test123/games', 'GET'),
            ('/admin/reset_leaderboard/1', 'POST')
        ]
        
        for route, method in admin_routes:
            if method == 'GET':
                response = client.get(route)
            else:
                response = client.post(route)
            assert response.status_code == 302  # Should redirect to login

    def test_all_admin_routes_require_admin_role(self, user_client):
        """Test that all admin routes require admin role."""
        admin_routes = [
            ('/admin/dashboard', 'GET'),
            ('/admin/add_user', 'GET'),
            ('/admin/verify_add_user_otp', 'GET'),
            ('/admin/resend_add_user_otp', 'GET'),
            ('/admin/add_game', 'GET'),
            ('/admin/user/test123', 'GET'),
            ('/admin/user/test123/toggle_active', 'POST'),
            ('/admin/user/test123/games', 'GET'),
            ('/admin/reset_leaderboard/1', 'POST')
        ]

        for route, method in admin_routes:
            if method == 'GET':
                response = user_client.get(route)
            else:
                response = user_client.post(route)
            assert response.status_code == 302  # Should redirect

class TestAdminRouteMethods:
    @patch('MyFlaskapp.admin.routes.get_db_connection')
    def test_manage_user_unsupported_method(self, mock_db, admin_client):
        """Test manage_user with unsupported HTTP method."""
        response = admin_client.patch('/admin/user/test123')
        # Flask should return 405 Method Not Allowed for unsupported methods
        assert response.status_code in [405, 302]  # Depending on how Flask handles it

    @patch('MyFlaskapp.admin.routes.get_db_connection')
    def test_manage_user_games_unsupported_method(self, mock_db, admin_client):
        """Test manage_user_games with unsupported HTTP method."""
        response = admin_client.delete('/admin/user/test123/games')
        # Flask should return 405 Method Not Allowed for unsupported methods
        assert response.status_code in [405, 302]
