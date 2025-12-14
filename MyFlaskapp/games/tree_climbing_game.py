#!/usr/bin/env python3
"""
Tree Climbing Game - Naruto Chakra Focusing Training
A timing-based game where players focus chakra to climb trees by pressing spacebar at the right moment.
"""

# Standard library imports
import os
import random
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from game_base import GameBase


class TreeClimbingGame(GameBase):
    def __init__(self):
        super().__init__(screen_width=600, screen_height=600, title="Naruto: Tree Climbing Training")
        
        # Game Constants
        self.width = self.screen_width
        self.height = self.screen_height
        
        # Gameplay Variables
        self.player_height = 0  # 0 to 100 (Percentage up the tree)
        self.meter_value = 0    # 0 to 100 (Position of the moving bar)
        self.meter_dir = 1      # 1 = Up, -1 = Down
        self.meter_speed = 1.0  # Speed of the bar (increases with difficulty)
        
        self.target_start = 0  # Bottom of green zone (0-100)
        self.target_size = 30  # Size of green zone (decreases with difficulty)
        
        # Enhanced gameplay features
        self.combo_count = 0    # Consecutive perfect hits
        self.target_player_y = 520  # For smooth animation
        
        self.game_started = False
        self.is_waiting_input = False # True when bar is moving
        
        # Visual elements storage
        self.tree_id = None
        self.player_id = None
        self.target_zone_id = None
        self.indicator_id = None
        self.info_text_id = None
        self.center_msg_id = None
        self.tree_texture_ids = []
        self.score_text_id = None
        self.height_text_id = None
        self.combo_text_id = None
        self.cloud_ids = []
        
        # Performance optimization: store pixel_range
        self.pixel_range = 470  # 520 (start y) - 50 (goal y)
        
        # Timing
        self.last_update = time.time()
        
        # Key action mapping
        self.key_actions = {
            "Return": self.start_game,
            "space": self.attempt_climb,
            "r": self.restart_game
        }
        
        self.setup_game()

    def setup_game(self):
        """Initialize game graphics and UI elements"""
        # Ensure canvas background is drawn first by clearing any default black
        self.canvas.delete("all")
        self.draw_static_elements()
        self.draw_dynamic_elements()
        # Set initial text states
        self.update_ui_text() 
        self.canvas.itemconfig(self.center_msg_id, text="Press ENTER to Start")
        self.canvas.itemconfig(self.info_text_id, text="Press SPACE to Focus Chakra")


    def draw_static_elements(self):
        """Draw elements that never change during gameplay"""
        self.draw_environment()
        self.draw_chakra_meter()
        self.draw_ui_text()
        
    def draw_dynamic_elements(self):
        """Draw elements that update during gameplay"""
        self.draw_player()

    def draw_environment(self):
        """Draw the tree environment with enhanced visuals"""
        # --- FIX: Ensure sky is drawn FIRST (cleared by canvas.delete("all") in setup_game) ---
        # Gradient sky background
        for i in range(10):
            color_value = 135 + i * 12  # Light blue to darker blue
            # Using more vibrant blue for better visibility on startup
            color = f"#{color_value:02x}{206:02x}{235:02x}"
            self.canvas.create_rectangle(0, i * 60, self.width, (i + 1) * 60, fill=color, outline="")
        
        # Clouds
        for i in range(3):
            x = 100 + i * 150
            y = 80 + i * 30
            cloud_id = self.canvas.create_oval(x, y, x + 60, y + 30, fill="white", outline="")
            self.cloud_ids.append(cloud_id)
            cloud_id = self.canvas.create_oval(x + 20, y - 10, x + 80, y + 20, fill="white", outline="")
            self.cloud_ids.append(cloud_id)
        
        # Ground
        self.canvas.create_rectangle(0, 550, self.width, 600, fill="green", outline="")
        
        # The Tree (Left Side)
        self.tree_id = self.canvas.create_rectangle(50, 0, 250, 550, fill="saddlebrown", outline="black")
        
        # Tree Texture (Lines)
        for i in range(12):
            y = i * 50
            width = 1 + (i % 3)
            color_intensity = 60 + (i * 5) % 40
            color = f"#{color_intensity:02x}{40:02x}{33:02x}"
            line_id = self.canvas.create_line(50, y, 250, y, fill=color, width=width)
            self.tree_texture_ids.append(line_id)

        # Goal Line (Top of Tree)
        self.canvas.create_line(40, 50, 260, 50, fill="red", width=3, dash=(4, 4))
        self.canvas.create_text(150, 30, text="GOAL", fill="red", font=("Arial", 12, "bold"))

    def draw_player(self):
        """Draw Naruto character"""
        # Starting at bottom (y=530 approx)
        self.player_id = self.canvas.create_oval(130, 520, 170, 560, fill="orange", outline="black", width=2)

    def draw_chakra_meter(self):
        """Draw the chakra meter on the right side"""
        # Frame
        self.meter_x = 400
        self.meter_y_top = 100
        self.meter_y_bot = 500
        self.meter_height = self.meter_y_bot - self.meter_y_top
        
        self.canvas.create_rectangle(self.meter_x, self.meter_y_top, self.meter_x + 50, self.meter_y_bot, 
                                     fill="grey", outline="black", width=2)
        self.canvas.create_text(self.meter_x + 25, self.meter_y_top - 20, text="CHAKRA", 
                                 font=("Arial", 10, "bold"))

        # The Target Zone (Green)
        # Initial coordinates are dummy/zero, will be set in start_new_round
        self.target_zone_id = self.canvas.create_rectangle(0, 0, 0, 0, fill="lime")
        
        # The Moving Indicator (Red Line)
        self.indicator_id = self.canvas.create_line(self.meter_x - 10, self.meter_y_bot, self.meter_x + 60, self.meter_y_bot, 
                                                     fill="red", width=4)

    def draw_ui_text(self):
        """Draw UI text elements with persistent score display"""
        # Status Text (Bottom Info)
        self.info_text_id = self.canvas.create_text(self.width/2, 575, text="", # Initial text set in setup_game
                                                     font=("Arial", 16, "bold"), fill="white")
        # Center Message (Start/Win/Lose)
        self.center_msg_id = self.canvas.create_text(self.width/2, self.height/2, text="", # Initial text set in setup_game
                                                     font=("Arial", 24, "bold"), fill="blue")
        
        # Persistent UI elements
        self.score_text_id = self.canvas.create_text(50, 20, text="Score: 0", 
                                                     font=("Arial", 14, "bold"), fill="black", anchor="w")
        self.height_text_id = self.canvas.create_text(self.width/2, 20, text="Height: 0%", 
                                                     font=("Arial", 14, "bold"), fill="black")
        self.combo_text_id = self.canvas.create_text(self.width - 50, 20, text="Combo: x0", 
                                                     font=("Arial", 14, "bold"), fill="orange", anchor="e")

    def handle_single_press(self, key):
        """Handle single key press events (Called from GameBase)"""
        action = self.key_actions.get(key)
        if action:
            # Prevent 'space' from being pressed before game starts or after game over
            if key == "space" and (not self.game_started or self.game_over):
                return
            # Allow 'r' to restart only when game is over
            if key == "r" and not self.game_over:
                return
            
            # Allow 'space' if game is running and waiting for input
            if key == "space" and self.game_started and self.is_waiting_input:
                action()
            # Allow 'Return' to start the game
            elif key == "Return":
                action()
            # Allow 'r' to restart the game
            elif key == "r" and self.game_over:
                 action()


    def start_game(self):
        """Start a new game"""
        if not self.game_started:
            self.game_started = True
            self.game_over = False
            self.player_height = 0
            self.target_player_y = 520
            self.combo_count = 0
            self.meter_speed = 1.0
            self.target_size = 30
            self.score = 0
            self.update_player_pos()
            self.update_ui_text()
            self.canvas.itemconfig(self.center_msg_id, text="")
            self.start_new_round()

    def start_new_round(self):
        """Start a new round of chakra focusing with dynamic difficulty"""
        if self.game_over: # Prevent starting a new round if the game is over
            return
            
        # Dynamic difficulty based on height
        self.target_size = max(10, 30 - int(self.player_height / 4))  # Smaller as player climbs
        self.meter_speed = 1.0 + (self.player_height / 40)  # Slower meter with height
        
        # Randomize Target Zone location
        max_start = 100 - self.target_size
        self.target_start = random.randint(0, max_start)
        
        # Update Visuals for Target Zone
        # Convert 0-100% to canvas pixel coordinates
        px_bottom = self.meter_y_bot - (self.target_start / 100 * self.meter_height)
        px_top = self.meter_y_bot - ((self.target_start + self.target_size) / 100 * self.meter_height)
        
        self.canvas.coords(self.target_zone_id, self.meter_x + 2, px_top, self.meter_x + 48, px_bottom)
        self.canvas.itemconfig(self.target_zone_id, fill="lime") # Reset color

        # Reset Meter
        self.meter_value = 0
        self.meter_dir = 1
        self.is_waiting_input = True
        
        self.canvas.itemconfig(self.info_text_id, text="Press SPACE in the Green Zone!", fill="white")

    def update_ui_text(self):
        """Update persistent UI text elements"""
        self.canvas.itemconfig(self.score_text_id, text=f"Score: {int(self.score)}")
        self.canvas.itemconfig(self.height_text_id, text=f"Height: {int(self.player_height)}%")
        self.canvas.itemconfig(self.combo_text_id, text=f"Combo: x{self.combo_count}")
        
        # Update combo text color and size based on streak
        if self.combo_count >= 5:
            self.canvas.itemconfig(self.combo_text_id, fill="red", font=("Arial", 18, "bold"))
        elif self.combo_count >= 3:
            self.canvas.itemconfig(self.combo_text_id, fill="orange", font=("Arial", 16, "bold"))
        else:
            self.canvas.itemconfig(self.combo_text_id, fill="orange", font=("Arial", 14, "bold"))
    
    def update(self):
        """Update game logic with smooth animations"""
        if not self.game_started or self.game_over:
            return
        
        current_time = time.time()
        # Use a small delta time (dt) for smoother, frame-rate independent movement
        dt = current_time - self.last_update
        self.last_update = current_time
        
        # Update meter if waiting for input
        if self.is_waiting_input:
            self.update_meter(dt)
        
        # Note: update_player_pos and update_ui_text are handled in draw() for visual consistency
        # but the physics/logic should happen here.

    def update_meter(self, dt):
        """Update the moving chakra meter with smooth animation and proper scaling"""
        
        # Frame-rate independent movement: speed * direction * scaled_time
        # Multiplied by 100 to scale from a base speed to a percentage change per second
        self.meter_value += self.meter_speed * self.meter_dir * dt * 100  
        
        # Bounce logic
        if self.meter_value >= 100:
            self.meter_value = 100
            self.meter_dir = -1
        elif self.meter_value <= 0:
            self.meter_value = 0
            self.meter_dir = 1
        
        # The visual update for the meter indicator happens in draw()
        
    def attempt_climb(self):
        """Attempt to climb based on meter position"""
        if self.game_started and self.is_waiting_input and not self.game_over:
            self.is_waiting_input = False
            
            # Check Hit
            target_end = self.target_start + self.target_size
            
            if self.target_start <= self.meter_value <= target_end:
                self.success()
            else:
                self.fail()

    def update_clouds(self):
        """Animate clouds for parallax effect"""
        for cloud_id in self.cloud_ids:
            # Move left slowly
            self.canvas.move(cloud_id, -0.5, 0)
            coords = self.canvas.coords(cloud_id)
            if coords and coords[2] < 0:  # If right edge of the cloud goes offscreen (coords[2] is x2)
                # Wrap around to the right side of the canvas with a buffer
                self.canvas.move(cloud_id, self.width + 100, 0) 

    def success(self):
        """Handle successful chakra focus with combo system and visual feedback"""
        self.combo_count += 1
        bonus = 50 * self.combo_count
        self.score += 100 + bonus
        
        # Visual feedback - flash target zone
        self.canvas.itemconfig(self.target_zone_id, fill="#AEEA00")
        self.root.after(200, lambda: self.canvas.itemconfig(self.target_zone_id, fill="lime"))
        
        self.canvas.itemconfig(self.info_text_id, text=f"PERFECT! Combo x{self.combo_count}!", fill="lime")
        self.update_ui_text()
        
        # Climb Up Logic
        self.player_height += 15
        if self.player_height >= 100:
            self.player_height = 100
            self.win_game()
            return

        self.update_player_pos()
        
        # Wait a moment then next round
        self.root.after(1000, self.start_new_round)

    def fail(self):
        """Handle failed chakra focus with visual feedback and check for Game Over"""
        self.combo_count = 0  # Reset combo
        
        # Visual feedback - flash target zone red
        self.canvas.itemconfig(self.target_zone_id, fill="red")
        self.root.after(200, lambda: self.canvas.itemconfig(self.target_zone_id, fill="lime"))
        
        self.canvas.itemconfig(self.info_text_id, text="TOO UNSTABLE! Falling...", fill="red")
        self.update_ui_text()
        
        # Fall Down Logic
        self.player_height -= 20
        
        if self.player_height <= 0:
            self.player_height = 0
            self.update_player_pos()
            self.game_over_fall() # *** NEW GAME OVER CALL ***
            return
            
        self.update_player_pos()
        
        self.root.after(1000, self.start_new_round)

    def game_over_fall(self):
        """
        Handle the Game Over state when the player falls to the ground (0% height).
        """
        self.game_over = True
        self.is_waiting_input = False
        
        # Stop the game meter visuals
        self.canvas.coords(self.target_zone_id, 0, 0, 0, 0) # Hide target zone
        self.canvas.coords(self.indicator_id, 0, 0, 0, 0) # Hide indicator
        
        # Final messages
        self.canvas.itemconfig(self.center_msg_id, 
                               text="GAME OVER\nChakra Exhausted!", 
                               fill="darkred")
        self.canvas.itemconfig(self.info_text_id, 
                               text="Press R to restart training.", 
                               fill="red")
        self.update_ui_text()


    def update_player_pos(self):
        """Update player position with smooth animation using cached pixel_range"""
        # Calculate the final target Y center coordinate (520 is the start Y, 50 is the goal Y)
        self.target_player_y = 520 - (self.player_height / 100 * self.pixel_range)
        
        # Get current position
        current_coords = self.canvas.coords(self.player_id)
        if current_coords:
            # Find the current center Y position
            current_y_center = (current_coords[1] + current_coords[3]) / 2
            
            # Smooth transition (20% movement towards target per frame)
            new_y_center = current_y_center + (self.target_player_y - current_y_center) * 0.2
            # Update coordinates (player is 40x40, so offset by 20 for center)
            self.canvas.coords(self.player_id, 130, new_y_center - 20, 170, new_y_center + 20)
        else:
            # Initial positioning
            self.canvas.coords(self.player_id, 130, self.target_player_y - 20, 170, self.target_player_y + 20)

    def win_game(self):
        """Handle game victory with celebration animation"""
        self.game_over = True
        self.is_waiting_input = False # Stop the meter
        # Victory bonus
        self.score += 500
        
        # Stop the game meter visuals
        self.canvas.coords(self.target_zone_id, 0, 0, 0, 0) # Hide target zone
        self.canvas.coords(self.indicator_id, 0, 0, 0, 0) # Hide indicator
        
        # Victory animation - flash gold multiple times
        for i in range(3):
            # Flash Gold
            self.root.after(i * 300, lambda: self.canvas.configure(bg="gold"))
            # Flash Back to Sky Blue
            self.root.after(i * 300 + 150, lambda: self.canvas.configure(bg="#87CEEB")) # Re-using a sky color

        self.canvas.itemconfig(self.center_msg_id, text="TRAINING COMPLETE!", fill="gold")
        self.canvas.itemconfig(self.info_text_id, text="Press R to play again", fill="white")
        self.update_ui_text()

    def draw(self):
        """Only update dynamic elements each frame for visual refresh"""
        if self.game_started and not self.game_over:
            # Update clouds for parallax effect
            self.update_clouds()
            
            # Update dynamic elements
            self.update_player_pos()
            self.update_ui_text()
            
            # Update meter indicator position only
            y_pos = self.meter_y_bot - (self.meter_value / 100 * self.meter_height)
            self.canvas.coords(self.indicator_id, self.meter_x - 10, y_pos, self.meter_x + 60, y_pos)

    def restart_game(self):
        """Restart the game"""
        if not self.game_over:
            # Only allow restart if the game is over
            return
            
        super().restart_game()
        self.game_started = False
        self.player_height = 0
        self.target_player_y = 520
        self.combo_count = 0
        self.meter_speed = 1.0
        self.target_size = 30
        self.target_start = 0
        self.meter_value = 0
        self.meter_dir = 1
        self.is_waiting_input = False
        self.last_update = time.time()
        
        # Reset UI
        self.canvas.itemconfig(self.center_msg_id, text="Press ENTER to Start", fill="blue")
        self.canvas.itemconfig(self.info_text_id, text="Press SPACE to Focus Chakra", fill="white")
        
        # Reset visual position
        self.update_player_pos()
        
        # Hide/reset target zone and indicator coordinates
        self.canvas.coords(self.target_zone_id, 0, 0, 0, 0)
        self.canvas.coords(self.indicator_id, self.meter_x - 10, self.meter_y_bot, self.meter_x + 60, self.meter_y_bot)
        
        # Ensure all texts are reset
        self.update_ui_text()


if __name__ == "__main__":
    game = TreeClimbingGame()
    # Call the new start_app method to handle scheduling and mainloop()
    score = game.run() 
    print(f"FINAL_SCORE:{score}")