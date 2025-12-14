#!/usr/bin/env python3
"""
Enhanced Clash Game - Naruto vs Sasuke Jutsu Clash
A polished button-mashing battle with dynamic difficulty, smooth animations, and visual effects.
"""

# Standard library imports
import math
import os
import random
import sys
import time

# Add the parent directory to the path to import game_base
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game_base import GameBase

class ClashGameEnhanced(GameBase):
    def __init__(self):
        super().__init__(screen_width=900, screen_height=500, title="Naruto vs Sasuke: Enhanced Jutsu Clash")

        self.center_y = self.screen_height // 2
        
        # Game state
        self.clash_position = 50.0
        self.base_cpu_strength = 0.08
        self.cpu_strength = self.base_cpu_strength
        self.player_strength = 4.5
        self.stamina = 100.0
        self.max_stamina = 100.0
        self.game_started = False
        self.game_time = 0
        self.last_update = time.time()
        
        # Enhanced scoring system
        self.score = 0
        self.mash_count = 0
        self.last_mash_time = 0
        self.mash_speed_bonus = 0
        self.stamina_efficiency_bonus = 1.0
        self.position_score = 0
        
        # Animation and effects
        self.particles = []
        self.glow_intensity = 0
        self.screen_shake = 0
        self.animation_offset = 0
        
        # Dynamic difficulty
        self.difficulty_multiplier = 1.0
        self.cpu_boost_timer = 0
        
        # Key action mapping
        self.key_actions = {
            "Return": self.start_game,
            "space": self.player_push,
            "r": self.restart_game
        }
        
        self.setup_graphics()

    def setup_graphics(self):
        # Graphics setup moved to draw() method since canvas is cleared each frame
        pass

    def handle_single_press(self, key):
        action = self.key_actions.get(key)
        if action:
            if key == "space" and (not self.game_started or self.game_over):
                return
            action()

    def start_game(self):
        self.game_started = True
        self.game_over = False
        self.clash_position = 50.0
        self.stamina = self.max_stamina
        self.game_time = 0
        self.difficulty_multiplier = 1.0
        self.cpu_strength = self.base_cpu_strength
        self.particles.clear()
        self.last_update = time.time()
        
        # Reset scoring system
        self.score = 0
        self.mash_count = 0
        self.last_mash_time = 0
        self.mash_speed_bonus = 0
        self.stamina_efficiency_bonus = 1.0
        self.position_score = 0

    def player_push(self):
        if self.stamina <= 0:
            return
        
        current_time = time.time()
        
        # Enhanced push with screen shake effect
        self.clash_position = min(100.0, self.clash_position + self.player_strength)
        self.stamina -= 1.8
        self.screen_shake = 5
        self.glow_intensity = 10
        
        # Update mash tracking
        self.mash_count += 1
        time_since_last_mash = current_time - self.last_mash_time if self.last_mash_time > 0 else 0
        self.last_mash_time = current_time
        
        # Calculate mash speed bonus (faster mashing = higher bonus)
        if time_since_last_mash < 0.2:  # Very fast mash
            self.mash_speed_bonus = 3.0
        elif time_since_last_mash < 0.4:  # Fast mash
            self.mash_speed_bonus = 2.0
        elif time_since_last_mash < 0.6:  # Normal mash
            self.mash_speed_bonus = 1.5
        else:  # Slow mash
            self.mash_speed_bonus = 1.0
        
        # Calculate stamina efficiency bonus (higher stamina = higher bonus)
        self.stamina_efficiency_bonus = 0.5 + (self.stamina / self.max_stamina) * 1.5
        
        # Add points for this mash
        mash_points = int(self.player_strength * self.mash_speed_bonus * self.stamina_efficiency_bonus)
        self.score += mash_points
        
        # Create particles for impact effect
        self.create_clash_particles()
        
        # Power burst mechanic
        if self.stamina > 70:
            bonus_push = self.player_strength * 0.5
            self.clash_position = min(100.0, self.clash_position + bonus_push)
            # Bonus points for power burst
            self.score += int(bonus_push * 2)

    def update(self):
        if not self.game_started or self.game_over:
            return
        
        current_time = time.time()
        dt = current_time - self.last_update
        self.last_update = current_time
        self.game_time += dt
        
        # Dynamic difficulty scaling
        self.update_difficulty()
        
        # Enhanced CPU logic with patterns
        self.update_cpu_behavior()
        
        # Apply CPU push
        cpu_push = self.cpu_strength * self.difficulty_multiplier
        if self.clash_position > 80:  # Reduced desperation threshold
            cpu_push *= 1.3  # Reduced desperation boost
        self.clash_position = max(0.0, self.clash_position - cpu_push)
        
        # Enhanced stamina regeneration with rate based on performance
        stamina_rate = 0.5 if self.clash_position < 30 else 0.4
        self.stamina = min(self.max_stamina, self.stamina + stamina_rate)
        
        # Update visual effects
        self.update_effects()
        
        # Victory conditions with enhanced scoring
        if self.clash_position >= 100.0:
            self.game_over = True
            # Victory bonus based on performance
            victory_bonus = int(100 * self.difficulty_multiplier)
            time_bonus = int(max(0, 30 - self.game_time) * 10)  # Faster victory = more points
            stamina_bonus = int(self.stamina * 2)  # More stamina left = bonus
            
            self.score += victory_bonus + time_bonus + stamina_bonus
            self.create_victory_effects("naruto")
        elif self.clash_position <= 0.0:
            self.game_over = True
            # Consolation points for effort
            consolation_points = int(self.score * 0.3)  # 30% of accumulated score
            self.score = max(10, consolation_points)  # Minimum 10 points for trying
            self.create_victory_effects("sasuke")

    def update_difficulty(self):
        # Gradually increase difficulty over time (slower scaling)
        self.difficulty_multiplier = 1.0 + (self.game_time / 60.0)  # 1x to 2x over 60 seconds

    def update_cpu_behavior(self):
        # CPU becomes more aggressive over time
        base_strength = self.base_cpu_strength
        
        # Add some randomness to CPU behavior
        if random.random() < 0.1:  # 10% chance of CPU burst
            self.cpu_boost_timer = 0.5
            self.cpu_strength = base_strength * 2.0
        elif self.cpu_boost_timer > 0:
            self.cpu_boost_timer -= 0.016  # Assuming 60 FPS
            if self.cpu_boost_timer <= 0:
                self.cpu_strength = base_strength
        else:
            self.cpu_strength = base_strength

    def update_effects(self):
        # Update screen shake
        if self.screen_shake > 0:
            self.screen_shake *= 0.9
            if self.screen_shake < 0.1:
                self.screen_shake = 0
        
        # Update glow intensity
        if self.glow_intensity > 0:
            self.glow_intensity *= 0.95
            if self.glow_intensity < 0.1:
                self.glow_intensity = 0
        
        # Update particles
        self.update_particles()

    def create_clash_particles(self):
        # Create particle effects at clash point
        padding = 90
        span = self.screen_width - padding * 2
        clash_x = padding + (self.clash_position / 100.0) * span
        
        for _ in range(8):
            particle = {
                'x': clash_x,
                'y': self.center_y + random.randint(-20, 20),
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-3, 3),
                'life': 1.0,
                'color': random.choice(['cyan', 'magenta', 'yellow', 'white'])
            }
            self.particles.append(particle)

    def update_particles(self):
        # Update and remove dead particles
        alive_particles = []
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 0.05
            particle['vy'] += 0.2  # Gravity
            
            if particle['life'] > 0:
                alive_particles.append(particle)
        
        self.particles = alive_particles

    def create_victory_effects(self, winner):
        # Create victory particle explosion
        padding = 90
        span = self.screen_width - padding * 2
        clash_x = padding + (self.clash_position / 100.0) * span
        
        for _ in range(20):
            particle = {
                'x': clash_x,
                'y': self.center_y,
                'vx': random.uniform(-5, 5),
                'vy': random.uniform(-8, 2),
                'life': 2.0,
                'color': 'cyan' if winner == 'naruto' else 'magenta'
            }
            self.particles.append(particle)

    def draw(self):
        # Draw background
        self.canvas.create_rectangle(0, 0, 450, 500, fill="#000044", outline="")
        self.canvas.create_rectangle(450, 0, 900, 500, fill="#440044", outline="")
        
        # Battle zone indicator
        self.canvas.create_rectangle(200, 150, 700, 350, fill="", outline="yellow", width=2, dash=(5, 5))
        
        if not self.game_started:
            # Draw start screen
            self.canvas.create_text(450, 200, text="NARUTO VS SASUKE", fill="white", 
                                   font=("Arial", 32, "bold"))
            self.canvas.create_text(450, 250, text="JUTSU CLASH", fill="yellow", 
                                   font=("Arial", 24, "bold"))
            self.canvas.create_text(450, 320, text="Press ENTER to Start", fill="white", 
                                   font=("Arial", 18))
            self.canvas.create_text(450, 360, text="MASH [SPACE] TO WIN!", fill="cyan", 
                                   font=("Arial", 16))
            return
        
        if self.game_over:
            self.draw_game_over()
        else:
            self.update_graphics()
            self.draw_particles()

    def update_graphics(self):
        # Apply screen shake offset
        shake_x = random.uniform(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        shake_y = random.uniform(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        
        # Draw characters
        self.canvas.create_rectangle(30 + shake_x, self.center_y - 40 + shake_y, 90 + shake_x, self.center_y + 40 + shake_y, 
                                   fill="orange", outline="white", width=3)
        self.canvas.create_oval(35 + shake_x, self.center_y - 70 + shake_y, 85 + shake_x, self.center_y - 30 + shake_y, 
                               fill="orange", outline="white", width=2)
        self.canvas.create_text(60 + shake_x, self.center_y - 85 + shake_y, text="NARUTO", fill="orange", 
                               font=("Arial", 12, "bold"))
        
        self.canvas.create_rectangle(810 + shake_x, self.center_y - 40 + shake_y, 870 + shake_x, self.center_y + 40 + shake_y, 
                                   fill="purple", outline="white", width=3)
        self.canvas.create_oval(815 + shake_x, self.center_y - 70 + shake_y, 865 + shake_x, self.center_y - 30 + shake_y, 
                               fill="purple", outline="white", width=2)
        self.canvas.create_text(840 + shake_x, self.center_y - 85 + shake_y, text="SASUKE", fill="purple", 
                               font=("Arial", 12, "bold"))
        
        padding = 90
        span = self.screen_width - padding * 2
        x = padding + (self.clash_position / 100.0) * span + shake_x
        
        # Enhanced beam widths with pulsing effect
        pulse = math.sin(self.game_time * 10) * 2
        r_w = 15 + self.clash_position / 4 + pulse + self.glow_intensity / 2
        c_w = 35 - self.clash_position / 4 + pulse + self.glow_intensity / 2
        
        # Draw Rasengan with glow effect
        self.canvas.create_rectangle(90 + shake_x, self.center_y - r_w + shake_y, 
                                   x, self.center_y + r_w + shake_y, fill="#00FFFF", outline="white", width=2)
        glow_size = r_w + 10 + self.glow_intensity
        self.canvas.create_rectangle(90 + shake_x, self.center_y - glow_size + shake_y, 
                                   x, self.center_y + glow_size + shake_y, fill="#00FFFF", outline="", stipple="gray50")
        
        # Draw Chidori with glow effect
        self.canvas.create_rectangle(x, self.center_y - c_w + shake_y, 
                                   810 + shake_x, self.center_y + c_w + shake_y, fill="#FF00FF", outline="white", width=2)
        glow_size = c_w + 10 + self.glow_intensity
        self.canvas.create_rectangle(x, self.center_y - glow_size + shake_y, 
                                   810 + shake_x, self.center_y + glow_size + shake_y, fill="#FF00FF", outline="", stipple="gray50")
        
        # Enhanced clash ball with dynamic sizing
        base_size = 35 + abs(50 - self.clash_position) / 2
        size_pulse = math.sin(self.game_time * 15) * 3
        size = base_size + size_pulse + self.glow_intensity
        
        self.canvas.create_oval(x - size, self.center_y - size + shake_y, 
                              x + size, self.center_y + size + shake_y, fill="white", outline="yellow", width=4)
        core_size = size * 0.6
        self.canvas.create_oval(x - core_size, self.center_y - core_size + shake_y, 
                              x + core_size, self.center_y + core_size + shake_y, fill="yellow", outline="")
        
        # Draw UI elements
        self.canvas.create_text(450, 80, text="MASH [SPACE]!", fill="white", 
                               font=("Arial", 24, "bold"))
        
        # Enhanced stamina bar with better styling
        self.canvas.create_text(300, 35, text="STAMINA", fill="white", font=("Arial", 12, "bold"))
        self.canvas.create_rectangle(350, 25, 550, 45, fill="#222222", outline="white", width=2)
        bar_width = int(200 * (self.stamina / self.max_stamina))
        color = "#00FF00" if self.stamina > 60 else "#FFFF00" if self.stamina > 30 else "#FF0000"
        self.canvas.create_rectangle(350, 25, 350 + bar_width, 45, fill=color, outline="")
        
        # Power meter indicator
        self.canvas.create_text(600, 35, text="POWER", fill="white", font=("Arial", 12, "bold"))
        self.canvas.create_rectangle(650, 25, 750, 45, fill="#222222", outline="white", width=2)
        power_width = int(100 * (self.clash_position / 100.0))
        power_color = "#FFD700" if self.clash_position > 70 else "#FFA500" if self.clash_position > 30 else "#FF6347"
        self.canvas.create_rectangle(650, 25, 650 + power_width, 45, fill=power_color, outline="")
        
        # Enhanced score display with bonus indicators
        score_color = "#00FF00" if self.score > 500 else "#FFFF00" if self.score > 200 else "#FFFFFF"
        self.canvas.create_text(450, 400, text=f"SCORE: {self.score}", fill=score_color, 
                               font=("Arial", 18, "bold"))
        
        # Timer display
        self.canvas.create_text(450, 430, text=f"Time: {self.game_time:.1f}s", fill="white", 
                               font=("Arial", 14))
        
        # Difficulty indicator
        self.canvas.create_text(450, 460, text=f"Difficulty: {self.difficulty_multiplier:.1f}x", fill="orange", 
                               font=("Arial", 12))
        
        # Mash speed indicator
        if self.mash_speed_bonus >= 3.0:
            speed_text = "SPEED: BLAZING!"
            speed_color = "#FF00FF"
        elif self.mash_speed_bonus >= 2.0:
            speed_text = "SPEED: FAST!"
            speed_color = "#00FFFF"
        elif self.mash_speed_bonus >= 1.5:
            speed_text = "SPEED: GOOD"
            speed_color = "#00FF00"
        else:
            speed_text = "SPEED: SLOW"
            speed_color = "#FFFF00"
        
        self.canvas.create_text(150, 430, text=speed_text, fill=speed_color, 
                               font=("Arial", 12, "bold"))

    def draw_particles(self):
        # Clear old particle drawings (would need to track particle objects in a real implementation)
        # For now, this is a placeholder for particle rendering
        
        for particle in self.particles:
            size = 3 * particle['life']
            # Create temporary particle circles (in a real implementation, you'd track these objects)
            self.canvas.create_oval(
                particle['x'] - size, particle['y'] - size,
                particle['x'] + size, particle['y'] + size,
                fill=particle['color'], outline="", tags="particle"
            )
        
        # Remove old particle drawings
        self.canvas.delete("particle")

    def draw_game_over(self):
        winner_text = "RASENGAN VICTORY!" if self.clash_position >= 100.0 else "CHIDORI VICTORY!"
        winner_color = "cyan" if self.clash_position >= 100.0 else "magenta"
        
        self.canvas.create_text(450, 150, text=winner_text, fill=winner_color, 
                               font=("Arial", 36, "bold"))
        
        # Enhanced score display
        self.canvas.create_text(450, 200, text=f"FINAL SCORE: {self.score}", fill="yellow", 
                               font=("Arial", 28, "bold"))
        
        # Performance breakdown
        stats_y = 250
        self.canvas.create_text(450, stats_y, text=f"Mashes: {self.mash_count}", fill="white", 
                               font=("Arial", 16))
        self.canvas.create_text(450, stats_y + 30, text=f"Time: {self.game_time:.1f}s", fill="white", 
                               font=("Arial", 16))
        self.canvas.create_text(450, stats_y + 60, text=f"Difficulty: {self.difficulty_multiplier:.1f}x", fill="white", 
                               font=("Arial", 16))
        
        # Performance rating
        if self.score >= 1000:
            rating = "LEGENDARY!"
            rating_color = "#FFD700"
        elif self.score >= 500:
            rating = "EXCELLENT!"
            rating_color = "#00FF00"
        elif self.score >= 200:
            rating = "GOOD!"
            rating_color = "#00FFFF"
        elif self.score >= 100:
            rating = "FAIR"
            rating_color = "#FFFF00"
        else:
            rating = "KEEP PRACTICING"
            rating_color = "#FF6347"
        
        self.canvas.create_text(450, stats_y + 100, text=f"RATING: {rating}", fill=rating_color, 
                               font=("Arial", 20, "bold"))
        
        self.canvas.create_text(450, 420, text="Press R to Restart or ESC to Quit", fill="white", 
                               font=("Arial", 16))

    def restart_game(self):
        super().restart_game()
        self.game_started = False
        self.clash_position = 50.0
        self.stamina = self.max_stamina
        self.game_time = 0
        self.difficulty_multiplier = 1.0
        self.cpu_strength = self.base_cpu_strength
        self.particles.clear()
        self.screen_shake = 0
        self.glow_intensity = 0
        
        # Reset scoring system
        self.score = 0
        self.mash_count = 0
        self.last_mash_time = 0
        self.mash_speed_bonus = 0
        self.stamina_efficiency_bonus = 1.0
        self.position_score = 0
        
        # Reset UI (no longer needed since graphics are recreated each frame)


if __name__ == "__main__":
    game = ClashGameEnhanced()
    score = game.run()
    print(f"FINAL_SCORE:{score}")
