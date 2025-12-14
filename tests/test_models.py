import pytest
from unittest.mock import patch, MagicMock
from MyFlaskapp.models import User, AdminUser, RegularUser, Game

class TestUser:
    def test_user_abstract(self):
        """Test that User is abstract."""
        with pytest.raises(TypeError):
            User('id', 'first', 'last', 'user', 'pass', 'type', 'birth', 'addr', 'mobile', 'email')

    def test_admin_user(self):
        """Test AdminUser creation and dashboard URL."""
        user = AdminUser('id', 'first', 'last', 'user', 'pass', 'admin', 'birth', 'addr', 'mobile', 'email')
        assert user.user_type == 'admin'
        assert user.get_dashboard_url() == '/admin/dashboard'

    def test_regular_user(self):
        """Test RegularUser creation and dashboard URL."""
        user = RegularUser('id', 'first', 'last', 'user', 'pass', 'user', 'birth', 'addr', 'mobile', 'email')
        assert user.user_type == 'user'
        assert user.get_dashboard_url() == '/user/dashboard'

    def test_password_check(self):
        """Test password checking."""
        user = AdminUser('id', 'first', 'last', 'user', 'password123', 'admin', 'birth', 'addr', 'mobile', 'email')
        assert user.check_password('password123') is True
        assert user.check_password('wrong') is False

    @patch('MyFlaskapp.models.get_db_connection')
    def test_save_to_db(self, mock_conn):
        """Test saving user to database."""
        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor
        user = AdminUser('id', 'first', 'last', 'user', 'pass', 'admin', 'birth', 'addr', 'mobile', 'email')
        user.save_to_db()
        mock_cursor.execute.assert_called_once()
        mock_conn.return_value.commit.assert_called_once()

class TestGame:
    def test_game_creation(self):
        """Test Game creation."""
        game = Game('Naruto Run', 'A running game', 'naruto_run.py', 1000)
        assert game.name == 'Naruto Run'
        assert game.description == 'A running game'
        assert game.file_path == 'naruto_run.py'
        assert game.max_score == 1000

    @patch('MyFlaskapp.models.get_db_connection')
    def test_save_to_db(self, mock_conn):
        """Test saving game to database."""
        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor
        game = Game('Naruto Run', 'A running game', 'naruto_run.py', 1000)
        game.save_to_db()
        mock_cursor.execute.assert_called_once()
        mock_conn.return_value.commit.assert_called_once()

    @patch('MyFlaskapp.models.get_db_connection')
    def test_get_all(self, mock_conn):
        """Test getting all games."""
        mock_cursor = MagicMock()
        mock_conn.return_value.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [
            {'name': 'Game1', 'description': 'Desc1', 'file_path': 'path1', 'max_score': 100},
            {'name': 'Game2', 'description': 'Desc2', 'file_path': 'path2', 'max_score': 200}
        ]
        games = Game.get_all()
        assert len(games) == 2
        assert games[0].name == 'Game1'
        assert games[1].name == 'Game2'