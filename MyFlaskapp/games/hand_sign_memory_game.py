#!/usr/bin/env python3
"""
Naruto Hand Sign Memory Game
A Simon-style memory game where players must repeat sequences of ninja hand signs.
"""

# Standard library imports
import random

from game_base import GameBase

class HandSignMemoryGame(GameBase):
    def __init__(self):
        super().__init__(screen_width=600, screen_height=500, title="Naruto: Hand Sign Memory")
        
        # --- Game Constants ---
        self.colors = ["#FF4500", "#32CD32", "#1E90FF", "#FFD700"]  # Red, Green, Blue, Yellow
        self.names = ["TIGER", "SNAKE", "DRAGON", "BIRD"]
        
        # Game State
        self.sequence = []      # The computer's sequence
        self.input_step = 0     # Where the player is in the sequence
        self.is_player_turn = False
        self.base_speed = 1000  # ms between flashes (gets faster)
        self.game_started = False
        self.input_locked = True  # Prevent input during sequence playback
        self.default_btn_color = "lightgrey"  # Store default button color
        
        # --- UI Setup ---
        self.setup_ui()
        
        # Disable buttons initially
        self.toggle_buttons(False)
    
    def run(self):
        """
        Override run method to prevent canvas clearing for this UI-heavy game
        """
        def game_loop():
            if not self.running:
                return

            if not self.game_over:
                # 1. Update Game Logic
                self.update()
                
                # 2. Draw Frame (without clearing canvas to preserve UI elements)
                self.draw()
                
                # Draw Score HUD
                if not hasattr(self, 'score_text') or not self.score_text:
                    self.score_text = self.canvas.create_text(10, 10, anchor="nw", text=f"Score: {self.score}", fill=self.WHITE, font=self.font_style)
                else:
                    self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")

            else:
                # Game Over State - only clear once
                self.canvas.delete("all")
                self.draw_game_over_screen()

            # Schedule next frame (approx 60 FPS -> 16ms)
            self.root.after(16, game_loop)

        # Start the loop and the main window
        game_loop()
        self.root.mainloop()
        
        return self.score

    def setup_ui(self):
        """Setup the game UI components"""
        # Store UI elements for recreation
        self.ui_elements = {}
        self.setup_ui_elements()
        
    def setup_ui_elements(self):
        """Setup the actual UI elements"""
        # 1. Info Bar (using canvas text instead of label)
        self.ui_elements['info_text'] = self.canvas.create_text(
            self.screen_width // 2, 30,
            text="Press SPACE to begin training", 
            fill=self.WHITE, 
            font=("Arial", 14)
        )

        # 2. Main Display (Kakashi's Hands)
        self.display_frame = tk.Frame(self.root, bg="black", width=300, height=200, bd=5, relief="ridge")
        self.ui_elements['display_frame_window'] = self.canvas.create_window(
            self.screen_width // 2, 150,
            window=self.display_frame,
            width=300, height=200
        )
        self.display_frame.pack_propagate(False)

        self.display_label = tk.Label(
            self.display_frame, 
            text="?", 
            bg="black", 
            fg="white", 
            font=("Arial", 30, "bold")
        )
        self.display_label.pack(expand=True)

        # 3. Player Controls (The Buttons)
        self.btn_frame = tk.Frame(self.root)
        self.ui_elements['btn_frame_window'] = self.canvas.create_window(
            self.screen_width // 2, 320,
            window=self.btn_frame
        )

        self.buttons = []
        for i in range(4):
            btn = tk.Button(
                self.btn_frame, 
                text=self.names[i], 
                bg="lightgrey", 
                width=10, height=3,
                font=("Arial", 10, "bold"),
                command=lambda idx=i: self.player_click(idx)
            )
            btn.grid(row=0, column=i, padx=5)
            self.buttons.append(btn)

        # 4. Instructions
        self.ui_elements['instruction_text'] = self.canvas.create_text(
            self.screen_width // 2, 450,
            text="Press SPACE to Start | ESC to Quit", 
            fill=self.WHITE, 
            font=("Arial", 12)
        )

    def toggle_buttons(self, state):
        """Enable or disable player buttons"""
        for btn in self.buttons:
            btn.config(state="normal" if state else "disabled")

    def update(self):
        """Update game logic (called from game loop)"""
        # This game is event-driven, so most updates happen in response to events
        pass

    def draw(self):
        """Draw game elements (called from game loop)"""
        # Update info text based on game state
        if not self.game_started:
            text = "Press SPACE to begin training"
        elif self.game_over:
            text = f"Game Over! Final Level: {self.score}"
        elif self.is_player_turn:
            text = f"Level {self.score + 1}: Repeat the signs!"
        else:
            text = f"Level {self.score + 1}: Watch closely..."
        
        if 'info_text' in self.ui_elements:
            self.canvas.itemconfig(self.ui_elements['info_text'], text=text)

    def handle_single_press(self, key):
        """Handle single key press events"""
        if key == "space":
            if not self.game_started or self.game_over:
                if self.game_started:
                    self.restart_game()
                else:
                    self.start_game()
        elif key.lower() == "r" and self.game_over:
            self.restart_game()

    def reset_state(self):
        """Reset all game state variables"""
        self.sequence = []
        self.input_step = 0
        self.score = 0
        self.base_speed = 1000
        self.game_started = True
        self.game_over = False
        self.is_player_turn = False
        self.input_locked = True

    def start_game(self):
        """Start a new game"""
        self.reset_state()
        if 'info_text' in self.ui_elements:
            self.canvas.itemconfig(self.ui_elements['info_text'], text="Watch Kakashi's Signs...")
        self.next_level()

    def next_level(self):
        """Advance to the next level"""
        self.input_step = 0
        self.is_player_turn = False
        self.input_locked = True
        self.toggle_buttons(False)
        
        # Add a new step to the sequence (cap at 20 for balance)
        if len(self.sequence) < 20:
            next_sign = random.randint(0, 3)
            self.sequence.append(next_sign)

        # Speed up slightly every level (capped at 300ms)
        self.base_speed = max(300, int(self.base_speed * 0.9))

        # Start the display sequence after a short pause
        self.root.after(1000, self.play_sequence)

    def play_sequence(self):
        """Play the current sequence for the player to memorize"""
        start_delay = 800  # Pause before first sign
        for i, sign_idx in enumerate(self.sequence):
            # Calculate when to flash ON and when to flash OFF
            delay_on = start_delay + i * self.base_speed
            delay_off = delay_on + (self.base_speed // 2)

            self.root.after(delay_on, lambda s=sign_idx: self.flash_sign(s))
            self.root.after(delay_off, self.clear_sign)

        # Calculate when the sequence finishes to enable player input
        total_time = start_delay + (len(self.sequence) + 1) * self.base_speed
        self.root.after(total_time, self.activate_player_turn)

    def flash_sign(self, sign_idx):
        """Flash a specific hand sign on the display"""
        color = self.colors[sign_idx]
        name = self.names[sign_idx]
        self.display_label.config(text=name, bg=color, fg="white")
        # Also highlight the corresponding button temporarily
        self.buttons[sign_idx].config(bg=color)

    def clear_sign(self):
        """Clear the display and reset button colors"""
        self.display_label.config(text="...", bg="black", fg="white")
        # Reset buttons to default color
        for btn in self.buttons:
            btn.config(bg=self.default_btn_color)

    def activate_player_turn(self):
        """Enable player input"""
        self.is_player_turn = True
        self.input_locked = False
        self.toggle_buttons(True)

    def player_click(self, sign_idx):
        """Handle player button clicks"""
        if self.input_locked or not self.is_player_turn:
            return

        # Flash the screen briefly to show feedback
        self.flash_sign(sign_idx)
        self.root.after(200, self.clear_sign)

        # Logic Check
        expected_sign = self.sequence[self.input_step]

        if sign_idx == expected_sign:
            # Correct!
            self.input_step += 1
            
            # Check if sequence is complete
            if self.input_step == len(self.sequence):
                self.score += 1  # Increment score only after successful completion
                self.is_player_turn = False
                self.input_locked = True
                self.toggle_buttons(False)
                if 'info_text' in self.ui_elements:
                    self.canvas.itemconfig(self.ui_elements['info_text'], text="Correct! Get ready...")
                self.root.after(800, self.next_level)
        else:
            # Wrong! Game Over
            self.wrong_feedback()

    def wrong_feedback(self):
        """Show immediate wrong input feedback"""
        self.display_label.config(bg="darkred")
        self.root.after(300, self.game_over_func)

    def game_over_func(self):
        """Handle game over"""
        self.game_over = True
        self.is_player_turn = False
        self.input_locked = True
        self.toggle_buttons(False)
        self.display_label.config(text="FAIL", bg="red")
        if 'info_text' in self.ui_elements:
            self.canvas.itemconfig(self.ui_elements['info_text'], text=f"Game Over! Final Level: {self.score}")
        if 'instruction_text' in self.ui_elements:
            self.canvas.itemconfig(self.ui_elements['instruction_text'], text="Press SPACE or R to Restart | ESC to Quit")

    def restart_game(self):
        """Restart the game"""
        self.display_label.config(text="?", bg="black", fg="white")
        self.toggle_buttons(False)
        self.start_game()

def main():
    """Main entry point for running the game directly"""
    game = HandSignMemoryGame()
    final_score = game.run()
    print(f"FINAL_SCORE:{final_score}")  # Print score for launcher to capture
    return final_score

if __name__ == "__main__":
    main()
