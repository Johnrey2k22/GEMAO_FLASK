# Standard library imports
import random
import time

from game_base import GameBase

class RoofRunGame(GameBase):
    """
    Naruto: Infinite Roof Run - A side-scrolling endless runner game
    where Naruto runs across rooftops avoiding obstacles.
    """
    
    def __init__(self):
        super().__init__(screen_width=800, screen_height=400, title="Naruto: Infinite Roof Run")
        
        # --- Game Constants ---
        self.ground_level = 350
        self.gravity = 1.5
        self.jump_power = -22
        self.scroll_speed = 8
        
        # --- Game State ---
        self.dy = 0  # Vertical velocity
        self.obstacles = []  # List to hold obstacle IDs
        self.game_started = False
        
        # --- Time-based spawning ---
        self.last_spawn_time = 0
        self.spawn_interval = 900  # milliseconds
        
        # --- Jump physics improvements ---
        self.coyote_time = 6      # frames
        self.jump_buffer = 6
        self.coyote_counter = 0
        self.jump_buffer_counter = 0
        
        # --- Obstacle patterns ---
        self.last_pattern = None
        
        # --- Player Properties ---
        self.player_x = 100
        self.player_y = self.ground_level - 40
        self.player_width = 40
        self.player_height = 40
        
        # Override the default key bindings for this specific game
        self.root.unbind("<space>")  # Remove default space binding
        self.root.bind("<space>", self._handle_space)

    def handle_single_press(self, key):
        """Handle single key press events"""
        if key == "space" and self.game_over:
            self.restart_game()

    def _handle_space(self, event):
        """Custom space handler for jumping"""
        if self.game_over:
            self.restart_game()
            return

        if not self.game_started:
            self.game_started = True

        # Always buffer jump
        self.jump_buffer_counter = self.jump_buffer

    def update(self):
        """Update game logic"""
        if not self.game_started:
            return
            
        # 1. Time-based spawning
        now = int(time.time() * 1000)
        self.spawn_obstacle(now)
        
        # 2. Proper jump physics
        self.dy += self.gravity
        self.player_y += self.dy

        on_ground = self.player_y >= self.ground_level - self.player_height

        if on_ground:
            self.player_y = self.ground_level - self.player_height
            self.dy = 0
            self.coyote_counter = self.coyote_time
        else:
            self.coyote_counter -= 1

        # Jump buffer logic
        if self.jump_buffer_counter > 0:
            self.jump_buffer_counter -= 1
            if self.coyote_counter > 0:
                self.dy = self.jump_power
                self.coyote_counter = 0
                self.jump_buffer_counter = 0

        # 3. Move Obstacles & Cleanup
        for ob in list(self.obstacles):
            ob['x'] -= self.scroll_speed
            
            # If off screen left, remove
            if ob['x'] + ob['width'] < 0:
                self.obstacles.remove(ob)

        # 4. Check Collision
        if self.check_collisions():
            self.game_over = True

        # 5. Update Score & Scale Difficulty
        self.score += 1
        self.scale_difficulty()

    def draw(self):
        """Draw all game elements"""
        # Draw background (dark blue sky)
        self.canvas.create_rectangle(0, 0, self.screen_width, self.screen_height, fill="#1a1a2e", outline="")

        # Draw the Moon
        self.canvas.create_oval(650, 50, 750, 150, fill="lightyellow", outline="")

        # Draw the Ground (The Roof)
        self.canvas.create_rectangle(0, self.ground_level, self.screen_width, self.screen_height, fill="#2e2e2e", outline="")

        # Draw Player (Naruto)
        self.canvas.create_rectangle(
            self.player_x, self.player_y, 
            self.player_x + self.player_width, self.player_y + self.player_height,
            fill="orange", outline="black"
        )

        # Draw Obstacles
        for ob in self.obstacles:
            if ob['type'] == 'chimney':
                self.canvas.create_rectangle(
                    ob['x'], self.ground_level - ob['height'],
                    ob['x'] + ob['width'], self.ground_level,
                    fill="grey40", outline="black"
                )
            else:  # kunai
                y = self.ground_level - ob['height_offset']
                # Draw a triangle pointing left
                self.canvas.create_polygon(
                    ob['x'], y,          # Tip
                    ob['x'] + 40, y - 5, # Back Top
                    ob['x'] + 40, y + 5, # Back Bottom
                    fill="silver", outline="black"
                )

        # Draw UI Text
        if not self.game_started:
            self.canvas.create_text(
                self.screen_width/2, self.screen_height/2,
                text="Infinite Roof Run\nPress SPACE to Start",
                fill="orange", font=("Arial", 24, "bold"), justify="center"
            )
        else:
            self.canvas.create_text(
                50, 30, text=f"Distance: {self.score}m",
                fill="white", font=("Arial", 14, "bold"), anchor="w"
            )

    def spawn_obstacle(self, now):
        """Time-based obstacle spawning"""
        if now - self.last_spawn_time < self.spawn_interval:
            return

        self.last_spawn_time = now

        # Prevent impossible patterns
        if self.obstacles and self.obstacles[-1]['x'] > self.screen_width - 250:
            return

        # Pattern-based spawning to prevent unfair sequences
        if self.last_pattern == "chimney" and random.random() < 0.6:
            self.spawn_kunai()
            self.last_pattern = "kunai"
        else:
            self.spawn_chimney()
            self.last_pattern = "chimney"
    
    def spawn_chimney(self):
        """Spawn a ground chimney obstacle"""
        self.obstacles.append({
            'type': 'chimney',
            'x': self.screen_width,
            'width': random.randint(30, 50),
            'height': random.randint(30, 60)
        })
    
    def spawn_kunai(self):
        """Spawn a flying kunai obstacle"""
        self.obstacles.append({
            'type': 'kunai',
            'x': self.screen_width,
            'width': 40,
            'height_offset': random.randint(50, 100)
        })
    
    def scale_difficulty(self):
        """Gradual difficulty scaling"""
        self.scroll_speed = 8 + self.score // 600
        self.spawn_interval = max(400, 900 - self.score // 3)

    def check_collisions(self):
        """Check for collisions between player and obstacles"""
        # Player hitbox (slightly smaller for forgiveness)
        player_hitbox = {
            'x1': self.player_x + 5,
            'y1': self.player_y + 5,
            'x2': self.player_x + self.player_width - 5,
            'y2': self.player_y + self.player_height - 5
        }
        
        # Check against all obstacles
        for ob in self.obstacles:
            # Forgive very early overlap on spawn
            if ob['x'] > self.screen_width - 20:
                continue
                
            if ob['type'] == 'chimney':
                ob_hitbox = {
                    'x1': ob['x'],
                    'y1': self.ground_level - ob['height'],
                    'x2': ob['x'] + ob['width'],
                    'y2': self.ground_level
                }
            else:  # kunai
                y = self.ground_level - ob['height_offset']
                ob_hitbox = {
                    'x1': ob['x'],
                    'y1': y - 5,
                    'x2': ob['x'] + 40,
                    'y2': y + 5
                }
            
            # Check rectangle overlap
            if (player_hitbox['x1'] < ob_hitbox['x2'] and 
                player_hitbox['x2'] > ob_hitbox['x1'] and
                player_hitbox['y1'] < ob_hitbox['y2'] and 
                player_hitbox['y2'] > ob_hitbox['y1']):
                return True  # Collision detected
                
        return False

    def restart_game(self):
        """Restart the game"""
        super().restart_game()
        self.game_started = True
        self.dy = 0
        self.player_y = self.ground_level - self.player_height
        self.obstacles.clear()
        
        # Reset timing and physics
        self.last_spawn_time = int(time.time() * 1000)
        self.spawn_interval = 900
        self.coyote_counter = 0
        self.jump_buffer_counter = 0
        self.last_pattern = None
        
        # Explicit game state reset
        self.scroll_speed = 8
        self.score = 0

    def draw_game_over_screen(self):
        """Override the default game over screen"""
        # Draw the game background first
        self.draw()
        
        # Draw semi-transparent overlay
        self.canvas.create_rectangle(
            0, 0, self.screen_width, self.screen_height,
            fill="black", stipple="gray50"
        )
        
        # Draw game over text
        self.canvas.create_text(
            self.screen_width/2, self.screen_height/2 - 50,
            text="GAME OVER", fill="red", font=("Arial", 48, "bold")
        )
        
        # Draw final score
        self.canvas.create_text(
            self.screen_width/2, self.screen_height/2 + 20,
            text=f"Distance: {self.score}m", fill="white", font=("Arial", 24, "bold")
        )
        
        # Draw restart instruction
        self.canvas.create_text(
            self.screen_width/2, self.screen_height/2 + 80,
            text="Press SPACE to Restart or ESC to Quit", 
            fill="white", font=("Arial", 16)
        )

if __name__ == "__main__":
    game = RoofRunGame()
    final_score = game.run()
    print(f"FINAL_SCORE:{final_score}")
