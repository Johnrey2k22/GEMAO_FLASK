import pytest
from unittest.mock import patch, MagicMock
import pygame
from MyFlaskapp.games.naruto_run import NarutoRun

class TestNarutoRun:
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_init(self, mock_font, mock_clock, mock_set_caption, mock_set_mode, mock_init):
        """Test NarutoRun initialization."""
        game = NarutoRun()
        assert game._player_x == 100
        assert game._player_y == 300
        assert game._player_speed == 5
        assert game._obstacles == []
        assert game._obstacle_speed == 5
        assert game._obstacle_spawn_rate == 5

    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    @patch('pygame.key.get_pressed')
    def test_update_movement_left(self, mock_keys, mock_font, mock_clock, mock_set_caption, mock_set_mode, mock_init):
        """Test player movement left."""
        mock_keys.return_value = {pygame.K_LEFT: True, pygame.K_RIGHT: False, pygame.K_UP: False, pygame.K_DOWN: False}
        game = NarutoRun()
        initial_x = game._player_x
        game.update()
        assert game._player_x == initial_x - game._player_speed

    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    @patch('pygame.key.get_pressed')
    def test_update_movement_right(self, mock_keys, mock_font, mock_clock, mock_set_caption, mock_set_mode, mock_init):
        """Test player movement right."""
        mock_keys.return_value = {pygame.K_LEFT: False, pygame.K_RIGHT: True, pygame.K_UP: False, pygame.K_DOWN: False}
        game = NarutoRun()
        initial_x = game._player_x
        game.update()
        assert game._player_x == initial_x + game._player_speed

    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    @patch('random.randint')
    def test_obstacle_spawning(self, mock_randint, mock_font, mock_clock, mock_set_caption, mock_set_mode, mock_init):
        """Test obstacle spawning."""
        mock_randint.return_value = 1  # Less than 5, so spawn
        game = NarutoRun()
        game._update_obstacles()
        assert len(game._obstacles) == 1

    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    @patch('pygame.font.Font')
    def test_collision_detection(self, mock_font, mock_clock, mock_set_caption, mock_set_mode, mock_init):
        """Test collision detection."""
        game = NarutoRun()
        # Add obstacle at player position
        game._obstacles.append(pygame.Rect(game._player_x, game._player_y, 50, 50))
        assert game._check_collision() is True

        # No collision
        game._obstacles = []
        game._obstacles.append(pygame.Rect(200, 200, 50, 50))
        assert game._check_collision() is False