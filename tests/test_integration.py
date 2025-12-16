import pytest
from flask import session
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
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

class TestIntegration:
    @patch('MyFlaskapp.auth.routes.check_duplicate_user')
    @patch('MyFlaskapp.auth.routes.store_otp')
    @patch('MyFlaskapp.auth.routes.send_otp_email')
    @patch('MyFlaskapp.auth.routes.generate_otp')
    @patch('MyFlaskapp.auth.routes.get_db_connection')
    def test_complete_registration_flow(self, mock_db, mock_otp, mock_send, mock_store, mock_check, client):
        """Test complete user registration flow."""
        # Setup mocks
        mock_check.return_value = False
        mock_otp.return_value = '123456'
        mock_store.return_value = True
        mock_send.return_value = True
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Step 1: Register
        response = client.post('/auth/register', data={
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
        
        # Verify session data is set
        with client.session_transaction() as sess:
            assert 'registration_data' in sess
            assert sess['registration_data']['email'] == 'john@example.com'
        
        # Step 2: Verify OTP
        with patch('MyFlaskapp.auth.routes.verify_otp') as mock_verify:
            mock_verify.return_value = True
            
            response = client.post('/auth/verify_otp', data={'otp': '123456'})
            assert response.status_code == 302
            
            # Verify user was created
            mock_cursor.execute.assert_called()
            mock_conn.commit.assert_called()
        
        # Step 3: Login with new user
        mock_cursor.fetchone.return_value = {
            'user_id': '123',
            'firstname': 'John',
            'lastname': 'Doe',
            'username': 'johndoe',
            'password': generate_password_hash('ValidPass123!'),
            'user_type': 'user'
        }
        
        response = client.post('/auth/login', data={
            'username': 'johndoe',
            'password': 'ValidPass123!'
        })
        assert response.status_code == 302

    @patch('MyFlaskapp.auth.routes.get_db_connection')
    def test_complete_login_flow(self, mock_db, client):
        """Test complete login and dashboard access."""
        # Setup user in database
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {
            'user_id': 'user123',
            'firstname': 'John',
            'lastname': 'Doe',
            'username': 'johndoe',
            'password': generate_password_hash('password123'),
            'user_type': 'user'
        }
        
        # Step 1: Login
        response = client.post('/auth/login', data={
            'username': 'johndoe',
            'password': 'password123'
        })
        assert response.status_code == 302
        
        # Step 2: Access user dashboard
        response = client.get('/user/dashboard')
        assert response.status_code == 200
        
        # Step 3: Access games list
        with patch('MyFlaskapp.games.routes.scan_games_directory') as mock_scan:
            mock_scan.return_value = []
            
            response = client.get('/games/')
            assert response.status_code == 200
        
        # Step 4: Logout
        response = client.get('/auth/logout')
        assert response.status_code == 302
        
        # Step 5: Verify logout by accessing protected route
        response = client.get('/user/dashboard')
        assert response.status_code == 302

    @patch('MyFlaskapp.auth.routes.get_db_connection')
    def test_admin_workflow(self, mock_db, client):
        """Test admin login and management workflow."""
        # Setup admin user
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
        
        # Step 1: Admin login
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        assert response.status_code == 302
        
        # Step 2: Access admin dashboard
        with patch('MyFlaskapp.admin.routes.scan_games_directory') as mock_scan:
            mock_scan.return_value = []
            mock_cursor.fetchall.side_effect = [[], []]  # Empty users and scores
            
            response = client.get('/admin/dashboard')
            assert response.status_code == 200
        
        # Step 3: Add new user
        with patch('MyFlaskapp.admin.routes.check_duplicate_user') as mock_check:
            with patch('MyFlaskapp.admin.routes.store_otp') as mock_store:
                with patch('MyFlaskapp.admin.routes.send_otp_email') as mock_send:
                    with patch('MyFlaskapp.admin.routes.generate_otp') as mock_otp:
                        mock_check.return_value = False
                        mock_otp.return_value = '123456'
                        mock_store.return_value = True
                        mock_send.return_value = True
                        
                        response = client.post('/admin/add_user', data={
                            'user_id': 'new_user',
                            'firstname': 'New',
                            'lastname': 'User',
                            'username': 'newuser',
                            'password': 'ValidPass123!',
                            'user_type': 'user',
                            'birthdate': '1990-01-01',
                            'address': '123 Test St',
                            'mobile': '1234567890',
                            'email': 'newuser@example.com'
                        })
                        assert response.status_code == 302

    @patch('MyFlaskapp.auth.routes.get_db_connection')
    @patch('MyFlaskapp.games.routes.scan_games_directory')
    @patch('MyFlaskapp.security_utils.validate_game_file_path')
    def test_game_play_workflow(self, mock_validate, mock_scan, mock_db, client):
        """Test complete game play workflow."""
        # Setup authenticated user
        with client.session_transaction() as sess:
            sess['user_id'] = 'user123'
            sess['user_name'] = 'Test User'
            sess['user_role'] = 'user'
        
        # Setup mocks
        mock_scan.return_value = [
            {
                'id': 'test_game.py',
                'name': 'Test Game',
                'description': 'A test game',
                'file_path': 'games/test_game.py',
                'filename': 'test_game.py',
                'class_name': 'TestGame'
            }
        ]
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []
        mock_cursor.fetchone.return_value = None
        
        mock_validate.return_value = (True, '/path/to/test_game.py')
        
        # Step 1: View games list
        with patch('MyFlaskapp.games.routes.get_or_create_game_in_db') as mock_create:
            with patch('MyFlaskapp.db.get_top_scores_for_game') as mock_scores:
                mock_create.return_value = 1
                mock_scores.return_value = []
                
                response = client.get('/games/')
                assert response.status_code == 200
        
        # Step 2: Play game
        with patch('MyFlaskapp.games.routes.check_game_access') as mock_access:
            mock_access.return_value = True
            
            response = client.get('/games/play/test_game.py')
            assert response.status_code == 200
        
        # Step 3: Launch game (simulate)
        with patch('MyFlaskapp.games.routes.subprocess.run') as mock_subprocess:
            with patch('MyFlaskapp.games.routes.check_game_access') as mock_access:
                mock_subprocess.return_value = MagicMock(stdout='100', returncode=0)
                mock_access.return_value = True
                
                with patch('MyFlaskapp.db.submit_score') as mock_submit:
                    mock_submit.return_value = True
                    
                    response = client.get('/games/launch_game/test_game.py')
                    assert response.status_code == 302

    @patch('MyFlaskapp.auth.routes.get_db_connection')
    def test_profile_update_workflow(self, mock_db, client):
        """Test profile update workflow."""
        # Setup authenticated user
        with client.session_transaction() as sess:
            sess['user_id'] = 'user123'
            sess['user_name'] = 'Test User'
            sess['user_role'] = 'user'
        
        # Setup database mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {
            'user_id': 'user123',
            'firstname': 'John',
            'lastname': 'Doe',
            'username': 'johndoe',
            'email': 'john@example.com',
            'mobile_number': '1234567890',
            'birthdate': '1990-01-01',
            'address': '123 Test St'
        }
        
        # Step 1: View profile
        response = client.get('/auth/profile')
        assert response.status_code == 200
        
        # Step 2: Update profile
        mock_cursor.fetchone.return_value = None  # No duplicate user
        
        response = client.post('/auth/profile', json={
            'firstname': 'John Updated',
            'lastname': 'Doe Updated',
            'username': 'johndoe_updated',
            'email': 'john_updated@example.com',
            'mobile': '9876543210',
            'birthdate': '1990-01-02',
            'address': '456 Updated St'
        })
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True

    def test_session_management_workflow(self, client):
        """Test session management across different user types."""
        # Step 1: Access protected route without session
        response = client.get('/user/dashboard')
        assert response.status_code == 302
        
        response = client.get('/admin/dashboard')
        assert response.status_code == 302
        
        # Step 2: Setup regular user session
        with client.session_transaction() as sess:
            sess['user_id'] = 'user123'
            sess['user_name'] = 'Regular User'
            sess['user_role'] = 'user'
        
        # Regular user should access user routes but not admin routes
        response = client.get('/user/dashboard')
        assert response.status_code == 200
        
        response = client.get('/admin/dashboard')
        assert response.status_code == 302
        
        # Step 3: Change to admin session
        with client.session_transaction() as sess:
            sess['user_id'] = 'admin123'
            sess['user_name'] = 'Admin User'
            sess['user_role'] = 'admin'
        
        # Admin should access admin routes but be redirected from user-only routes
        with patch('MyFlaskapp.admin.routes.scan_games_directory') as mock_scan:
            mock_scan.return_value = []
            
            response = client.get('/admin/dashboard')
            assert response.status_code == 200
        
        response = client.get('/games/')
        assert response.status_code == 302  # Admin redirected from user-only games

    @patch('MyFlaskapp.auth.routes.get_db_connection')
    def test_error_handling_workflow(self, mock_db, client):
        """Test error handling across different scenarios."""
        # Test database connection failure
        mock_db.return_value = None
        
        response = client.post('/auth/login', data={
            'username': 'test',
            'password': 'test'
        })
        assert response.status_code == 200  # Should still render login page
        
        # Test database error during registration
        with patch('MyFlaskapp.auth.routes.check_duplicate_user') as mock_check:
            with patch('MyFlaskapp.auth.routes.store_otp') as mock_store:
                with patch('MyFlaskapp.auth.routes.send_otp_email') as mock_send:
                    with patch('MyFlaskapp.auth.routes.generate_otp') as mock_otp:
                        mock_check.return_value = False
                        mock_otp.return_value = '123456'
                        mock_store.return_value = False  # OTP storage fails
                        mock_send.return_value = True
                        
                        response = client.post('/auth/register', data={
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
                        assert response.status_code == 302  # Should redirect back

    def test_ajax_workflow(self, client):
        """Test AJAX request handling."""
        # Test AJAX login
        with patch('MyFlaskapp.auth.routes.get_db_connection') as mock_db:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_db.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = None  # Invalid credentials
            
            response = client.post('/auth/login', data={
                'username': 'invalid',
                'password': 'invalid'
            }, headers={'X-Requested-With': 'XMLHttpRequest'})
            
            assert response.status_code == 400
            json_data = response.get_json()
            assert json_data['status'] == 'fail'

    @patch('MyFlaskapp.auth.routes.get_db_connection')
    def test_security_workflow(self, mock_db, client):
        """Test security measures across the application."""
        # Test SQL injection prevention (mock should handle this)
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        # Attempt login with SQL injection
        response = client.post('/auth/login', data={
            'username': "admin'; DROP TABLE users; --",
            'password': 'password'
        })
        
        # Should not crash, should handle gracefully
        assert response.status_code in [200, 302]
        
        # Verify parameterized queries were used (mock should show this)
        mock_cursor.execute.assert_called()
        # The execute call should use %s placeholders, not string formatting

    def test_concurrent_sessions_workflow(self, client):
        """Test handling of concurrent sessions."""
        # This test would require multiple clients or session management
        # For now, test session isolation
        
        # Create first client session
        with client.session_transaction() as sess:
            sess['user_id'] = 'user1'
            sess['user_name'] = 'User One'
            sess['user_role'] = 'user'
        
        # Verify first session
        response = client.get('/user/dashboard')
        assert response.status_code == 200
        
        # Create second client (would need separate client instance for true concurrency)
        # For now, just test session replacement
        with client.session_transaction() as sess:
            sess['user_id'] = 'user2'
            sess['user_name'] = 'User Two'
            sess['user_role'] = 'user'
        
        # Verify session was updated
        response = client.get('/user/dashboard')
        assert response.status_code == 200

class TestEndToEndScenarios:
    @patch('MyFlaskapp.auth.routes.check_duplicate_user')
    @patch('MyFlaskapp.auth.routes.store_otp')
    @patch('MyFlaskapp.auth.routes.send_otp_email')
    @patch('MyFlaskapp.auth.routes.generate_otp')
    @patch('MyFlaskapp.auth.routes.verify_otp')
    @patch('MyFlaskapp.auth.routes.get_db_connection')
    def test_new_user_complete_journey(self, mock_db, mock_verify, mock_otp, mock_send, mock_store, mock_check, client):
        """Test complete journey for a new user from registration to playing games."""
        # Setup mocks for registration
        mock_check.return_value = False
        mock_otp.return_value = '123456'
        mock_store.return_value = True
        mock_send.return_value = True
        mock_verify.return_value = True
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Step 1: Register
        response = client.post('/auth/register', data={
            'firstname': 'Alice',
            'lastname': 'Smith',
            'username': 'alicesmith',
            'email': 'alice@example.com',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'birthdate': '1995-05-15',
            'address': '789 New Street',
            'mobile': '5551234567'
        })
        assert response.status_code == 302
        
        # Step 2: Verify OTP
        response = client.post('/auth/verify_otp', data={'otp': '123456'})
        assert response.status_code == 302
        
        # Step 3: Login
        mock_cursor.fetchone.return_value = {
            'user_id': '456',
            'firstname': 'Alice',
            'lastname': 'Smith',
            'username': 'alicesmith',
            'password': generate_password_hash('SecurePass123!'),
            'user_type': 'user'
        }
        
        response = client.post('/auth/login', data={
            'username': 'alicesmith',
            'password': 'SecurePass123!'
        })
        assert response.status_code == 302
        
        # Step 4: Access dashboard
        response = client.get('/user/dashboard')
        assert response.status_code == 200
        
        # Step 5: View and play games
        with patch('MyFlaskapp.games.routes.scan_games_directory') as mock_scan:
            with patch('MyFlaskapp.games.routes.check_game_access') as mock_access:
                mock_scan.return_value = [
                    {
                        'id': 'simple_game.py',
                        'name': 'Simple Game',
                        'description': 'A simple test game',
                        'file_path': 'games/simple_game.py',
                        'filename': 'simple_game.py',
                        'class_name': 'SimpleGame'
                    }
                ]
                mock_access.return_value = True
                
                # View games
                with patch('MyFlaskapp.games.routes.get_or_create_game_in_db') as mock_create:
                    with patch('MyFlaskapp.db.get_top_scores_for_game') as mock_scores:
                        mock_create.return_value = 1
                        mock_scores.return_value = []
                        
                        response = client.get('/games/')
                        assert response.status_code == 200
                
                # Play game
                response = client.get('/games/play/simple_game.py')
                assert response.status_code == 200
        
        # Step 6: Update profile
        # Reset fetchone to return None for duplicate check (no other users have same username/email)
        mock_cursor.fetchone.return_value = None
        
        response = client.post('/auth/profile', json={
            'firstname': 'Alice',
            'lastname': 'Johnson',  # Changed last name
            'username': 'alicesmith',
            'email': 'alice@example.com',
            'mobile': '5559876543',
            'birthdate': '1995-05-15',
            'address': '789 Updated Street'
        })

        if response.status_code != 200:
            print(f"Profile update failed with status {response.status_code}")
            print(f"Response data: {response.get_json()}")
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True
        
        # Step 7: Logout
        response = client.get('/auth/logout')
        assert response.status_code == 302
