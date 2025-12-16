import pytest
from flask import session
from unittest.mock import patch, MagicMock
from MyFlaskapp import create_app
import tempfile
import os

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
def authenticated_client(client):
    """Create an authenticated client for testing."""
    with client.session_transaction() as sess:
        sess['user_id'] = 'test123'
        sess['user_name'] = 'Test User'
        sess['user_role'] = 'user'
    return client

@pytest.fixture
def admin_client(client):
    """Create an admin authenticated client."""
    with client.session_transaction() as sess:
        sess['user_id'] = 'admin123'
        sess['user_name'] = 'Admin User'
        sess['user_role'] = 'admin'
    return client

@pytest.fixture
def mock_game_file():
    """Create a temporary game file for testing."""
    game_content = '''
import pygame
import sys

class TestGame:
    def __init__(self):
        self.title = "Test Game"
        self.score = 0
    
    def run(self):
        print("100")  # Output score
        return 100

if __name__ == "__main__":
    game = TestGame()
    score = game.run()
    print(score)
'''
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(game_content)
        temp_file = f.name
    
    yield temp_file
    
    # Cleanup
    if os.path.exists(temp_file):
        os.unlink(temp_file)

class TestGamesRoutes:
    def test_games_list_unauthenticated(self, client):
        """Test games list access without authentication."""
        response = client.get('/games/')
        assert response.status_code == 302  # Redirect to login

    def test_games_list_admin_access_denied(self, admin_client):
        """Test games list access by admin (should be denied)."""
        response = admin_client.get('/games/')
        assert response.status_code == 302  # Redirect to admin dashboard

    @patch('MyFlaskapp.games.routes.scan_games_directory')
    @patch('MyFlaskapp.games.routes.get_db_connection')
    def test_games_list_authenticated(self, mock_db, mock_scan, authenticated_client):
        """Test games list access with authentication."""
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
        
        with patch('MyFlaskapp.games.routes.get_or_create_game_in_db') as mock_create:
            mock_create.return_value = 1
            with patch('MyFlaskapp.db.get_top_scores_for_game') as mock_scores:
                mock_scores.return_value = []
                
                response = authenticated_client.get('/games/')
                assert response.status_code == 200

    @patch('MyFlaskapp.games.routes.scan_games_directory')
    @patch('MyFlaskapp.games.routes.get_db_connection')
    def test_games_list_with_db_scores(self, mock_db, mock_scan, authenticated_client):
        """Test games list with database scores."""
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
        mock_cursor.fetchall.return_value = [
            {'id': 1, 'file_path': 'games/test_game.py', 'name': 'Test Game'}
        ]
        
        with patch('MyFlaskapp.db.get_top_scores_for_game') as mock_scores:
            mock_scores.return_value = [
                {'username': 'user1', 'score': 100},
                {'username': 'user2', 'score': 80}
            ]
            
            response = authenticated_client.get('/games/')
            assert response.status_code == 200

    @patch('MyFlaskapp.games.routes.scan_games_directory')
    def test_play_game_by_filename_unauthenticated(self, mock_scan, client):
        """Test game play without authentication."""
        mock_scan.return_value = []
        response = client.get('/games/play/test_game.py')
        assert response.status_code == 302

    @patch('MyFlaskapp.games.routes.scan_games_directory')
    @patch('MyFlaskapp.games.routes.check_game_access')
    def test_play_game_by_filename_access_denied(self, mock_access, mock_scan, authenticated_client):
        """Test game play with access denied."""
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
        mock_access.return_value = False
        
        response = authenticated_client.get('/games/play/test_game.py')
        assert response.status_code == 302  # Redirect to games list

    @patch('MyFlaskapp.games.routes.scan_games_directory')
    @patch('MyFlaskapp.games.routes.check_game_access')
    def test_play_game_by_filename_success(self, mock_access, mock_scan, authenticated_client):
        """Test successful game play by filename."""
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
        mock_access.return_value = True
        
        response = authenticated_client.get('/games/play/test_game.py')
        assert response.status_code == 200

    @patch('MyFlaskapp.games.routes.scan_games_directory')
    @patch('MyFlaskapp.games.routes.check_game_access')
    def test_play_game_by_filename_not_found(self, mock_access, mock_scan, authenticated_client):
        """Test game play with non-existent game."""
        mock_scan.return_value = []  # No games found
        mock_access.return_value = True
        
        response = authenticated_client.get('/games/play/nonexistent.py')
        assert response.status_code == 302  # Redirect to games list

    @patch('MyFlaskapp.games.routes.get_db_connection')
    def test_play_game_by_id_unauthenticated(self, mock_db, client):
        """Test game play by ID without authentication."""
        response = client.get('/games/play/1')
        assert response.status_code == 302

    @patch('MyFlaskapp.games.routes.get_db_connection')
    def test_play_game_by_id_authenticated(self, mock_db, authenticated_client):
        """Test game play by ID with authentication."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {
            'id': 1,
            'name': 'Test Game',
            'description': 'A test game',
            'file_path': 'games/test_game.py'
        }
        
        response = authenticated_client.get('/games/play/1')
        assert response.status_code == 200

    @patch('MyFlaskapp.games.routes.get_db_connection')
    def test_play_game_by_id_not_found(self, mock_db, authenticated_client):
        """Test game play by ID with non-existent game."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        response = authenticated_client.get('/games/play/999')
        assert response.status_code == 302  # Redirect to games list

    @patch('MyFlaskapp.games.routes.subprocess.run')
    @patch('MyFlaskapp.games.routes.get_db_connection')
    @patch('MyFlaskapp.games.routes.validate_game_file_path')
    def test_launch_game_success(self, mock_validate, mock_db, mock_subprocess, authenticated_client):
        """Test successful game launch."""
        mock_validate.return_value = (True, '/path/to/game.py')
        mock_subprocess.return_value = MagicMock(stdout='100', returncode=0)
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {
            'id': 1,
            'name': 'Test Game',
            'description': 'A test game',
            'file_path': 'games/test_game.py'
        }
        
        with patch('MyFlaskapp.db.submit_score') as mock_submit:
            mock_submit.return_value = True
            
            response = authenticated_client.get('/games/launch_game/1')
            assert response.status_code == 302  # Redirect to games list

    @patch('MyFlaskapp.games.routes.subprocess.run')
    @patch('MyFlaskapp.games.routes.get_db_connection')
    @patch('MyFlaskapp.games.routes.validate_game_file_path')
    def test_launch_game_invalid_file(self, mock_validate, mock_db, mock_subprocess, authenticated_client):
        """Test game launch with invalid file."""
        mock_validate.return_value = (False, 'Invalid file path')
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {
            'id': 1,
            'name': 'Test Game',
            'description': 'A test game',
            'file_path': 'games/test_game.py'
        }
        
        response = authenticated_client.get('/games/launch_game/1')
        assert response.status_code == 302  # Redirect to games list

    @patch('MyFlaskapp.games.routes.subprocess.run')
    @patch('MyFlaskapp.games.routes.get_db_connection')
    def test_launch_game_timeout(self, mock_db, mock_subprocess, authenticated_client):
        """Test game launch with timeout."""
        from subprocess import TimeoutExpired
        mock_subprocess.side_effect = TimeoutExpired('python', 300)
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {
            'id': 1,
            'name': 'Test Game',
            'description': 'A test game',
            'file_path': 'games/test_game.py'
        }
        
        with patch('MyFlaskapp.games.routes.validate_game_file_path') as mock_validate:
            mock_validate.return_value = (True, '/path/to/game.py')
            
            response = authenticated_client.get('/games/launch_game/1')
            assert response.status_code == 302  # Redirect to games list

    @patch('MyFlaskapp.games.routes.subprocess.run')
    @patch('MyFlaskapp.games.routes.get_db_connection')
    def test_submit_score_success(self, mock_db, mock_subprocess, authenticated_client):
        """Test successful score submission."""
        mock_subprocess.return_value = MagicMock(stdout='100', returncode=0)
        
        with patch('MyFlaskapp.db.submit_score') as mock_submit:
            mock_submit.return_value = True
            
            response = authenticated_client.post('/games/submit_score/1', data={'score': '100'})
            assert response.status_code == 302  # Redirect to games list

    @patch('MyFlaskapp.games.routes.subprocess.run')
    @patch('MyFlaskapp.games.routes.get_db_connection')
    def test_submit_score_failure(self, mock_db, mock_subprocess, authenticated_client):
        """Test failed score submission."""
        mock_subprocess.return_value = MagicMock(stdout='100', returncode=0)
        
        with patch('MyFlaskapp.db.submit_score') as mock_submit:
            mock_submit.return_value = False
            
            response = authenticated_client.post('/games/submit_score/1', data={'score': '100'})
            assert response.status_code == 302  # Redirect to games list

    def test_submit_score_unauthenticated(self, client):
        """Test score submission without authentication."""
        response = client.post('/games/submit_score/1', data={'score': '100'})
        assert response.status_code == 302  # Redirect to login

class TestGameUtilities:
    def test_safe_int_convert_valid(self):
        """Test safe integer conversion with valid input."""
        from MyFlaskapp.games.routes import safe_int_convert
        
        assert safe_int_convert('100') == 100
        assert safe_int_convert('0') == 0
        assert safe_int_convert('  50  ') == 50
        assert safe_int_convert(100) == 100

    def test_safe_int_convert_invalid(self):
        """Test safe integer conversion with invalid input."""
        from MyFlaskapp.games.routes import safe_int_convert
        
        assert safe_int_convert('') == 0
        assert safe_int_convert(None) == 0
        assert safe_int_convert('abc') == 0
        assert safe_int_convert('12.5') == 0
        assert safe_int_convert([]) == 0

    def test_safe_int_convert_custom_default(self):
        """Test safe integer conversion with custom default."""
        from MyFlaskapp.games.routes import safe_int_convert
        
        assert safe_int_convert('', default=-1) == -1
        assert safe_int_convert(None, default=999) == 999
        assert safe_int_convert('abc', default=5) == 5

    @patch('MyFlaskapp.games.routes.get_db_connection')
    def test_check_game_access_enabled(self, mock_db):
        """Test game access check when enabled."""
        from MyFlaskapp.games.routes import check_game_access
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {'is_enabled': True}
        
        result = check_game_access('user123', 'test_game.py')
        assert result is True

    @patch('MyFlaskapp.games.routes.get_db_connection')
    def test_check_game_access_disabled(self, mock_db):
        """Test game access check when disabled."""
        from MyFlaskapp.games.routes import check_game_access
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {'is_enabled': False}
        
        result = check_game_access('user123', 'test_game.py')
        assert result is False

    @patch('MyFlaskapp.games.routes.get_db_connection')
    def test_check_game_access_no_record(self, mock_db):
        """Test game access check with no record (default to enabled)."""
        from MyFlaskapp.games.routes import check_game_access
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None
        
        result = check_game_access('user123', 'test_game.py')
        assert result is True

    @patch('MyFlaskapp.games.routes.get_db_connection')
    def test_check_game_access_db_error(self, mock_db):
        """Test game access check with database error (default to enabled)."""
        from MyFlaskapp.games.routes import check_game_access
        
        mock_db.return_value = None
        
        result = check_game_access('user123', 'test_game.py')
        assert result is True

    @patch('MyFlaskapp.games.routes.get_db_connection')
    def test_get_or_create_game_in_db_existing(self, mock_db):
        """Test getting existing game from database."""
        from MyFlaskapp.games.routes import get_or_create_game_in_db
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = {'id': 1}
        
        game = {'name': 'Test Game', 'description': 'A test', 'file_path': 'games/test.py'}
        result = get_or_create_game_in_db(game)
        assert result == 1

    @patch('MyFlaskapp.games.routes.get_db_connection')
    def test_get_or_create_game_in_db_new(self, mock_db):
        """Test creating new game in database."""
        from MyFlaskapp.games.routes import get_or_create_game_in_db
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None  # No existing game
        mock_cursor.lastrowid = 5
        
        game = {'name': 'Test Game', 'description': 'A test', 'file_path': 'games/test.py'}
        result = get_or_create_game_in_db(game)
        assert result == 5

    @patch('MyFlaskapp.games.routes.get_db_connection')
    def test_get_or_create_game_in_db_error(self, mock_db):
        """Test game database operation with error."""
        from MyFlaskapp.games.routes import get_or_create_game_in_db
        
        mock_db.return_value = None
        
        game = {'name': 'Test Game', 'description': 'A test', 'file_path': 'games/test.py'}
        result = get_or_create_game_in_db(game)
        assert result is None

class TestGameScanning:
    def test_scan_games_directory(self):
        """Test scanning games directory."""
        from MyFlaskapp.games.routes import scan_games_directory
        
        # This test would need to mock os.listdir and other file operations
        with patch('os.listdir') as mock_listdir:
            mock_listdir.return_value = ['test_game.py', 'another_game.py', '__init__.py']
            
            with patch('MyFlaskapp.games.routes.extract_game_metadata') as mock_extract:
                mock_extract.side_effect = [
                    {'name': 'Test Game', 'description': 'A test game', 'file_path': 'games/test_game.py'},
                    {'name': 'Another Game', 'description': 'Another test game', 'file_path': 'games/another_game.py'}
                ]
                
                games = scan_games_directory()
                assert len(games) == 2
                assert games[0]['name'] == 'Test Game'
                assert games[1]['name'] == 'Another Game'

    def test_extract_game_metadata(self):
        """Test extracting metadata from game file."""
        from MyFlaskapp.games.routes import extract_game_metadata
        
        game_content = '''
class NarutoGame:
    def __init__(self):
        self.title = "Naruto Run"
        pass
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(game_content)
            temp_file = f.name
        
        try:
            with patch('os.path.basename') as mock_basename:
                mock_basename.return_value = 'naruto_game.py'
                
                metadata = extract_game_metadata(temp_file)
                assert metadata['name'] == 'Naruto Run'
                assert metadata['filename'] == 'naruto_game.py'
                assert metadata['class_name'] == 'NarutoGame'
        finally:
            os.unlink(temp_file)

    def test_generate_description_from_title(self):
        """Test generating description from title."""
        from MyFlaskapp.games.routes import generate_description_from_title
        
        # Test known keywords
        desc = generate_description_from_title('Naruto Typing Game', 'typing_game.py')
        assert 'typing' in desc.lower()
        
        # Test default description
        desc = generate_description_from_title('Unknown Game', 'unknown.py')
        assert 'ninja world' in desc.lower()
        assert 'Unknown Game' in desc
