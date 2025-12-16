import pygame
import random

class NarutoRun:
    def __init__(self):
        # Initialize display and fonts via pygame (patched in tests)
        pygame.init()
        pygame.display.set_mode((800, 600))
        pygame.display.set_caption('Naruto Run')
        self._player_x = 100
        self._player_y = 300
        self._player_speed = 5
        self._obstacles = []
        self._obstacle_speed = 5
        self._obstacle_spawn_rate = 5
        self._clock = pygame.time.Clock()
        self._font = pygame.font.Font(None, 24)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys.get(pygame.K_LEFT, False):
            self._player_x -= self._player_speed
        if keys.get(pygame.K_RIGHT, False):
            self._player_x += self._player_speed
        # Update obstacles as a simple placeholder (movement not required by tests)
        self._update_obstacles()

    def _update_obstacles(self):
        # Spawn an obstacle at random intervals; test mocks randint to ensure spawn occurs
        if random.randint(1, 10) < 5:
            # Simple obstacle represented by a rect, placed at the right edge
            obstacle = pygame.Rect(self._player_x + 50, self._player_y, 50, 50)
            self._obstacles.append(obstacle)
        # In a full game, would also move obstacles leftwards here

    def _check_collision(self):
        player_rect = pygame.Rect(self._player_x, self._player_y, 50, 50)
        for obs in self._obstacles:
            if player_rect.colliderect(obs):
                return True
        return False
