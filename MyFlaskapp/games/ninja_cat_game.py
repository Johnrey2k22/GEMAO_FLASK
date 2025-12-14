# Standard library imports
import math
import random
import time
import tkinter as tk

# --- GameBase Class (Minimal Functional Implementation) ---
class GameBase:
    def __init__(self, screen_width, screen_height, title):
        self.root = tk.Tk()
        self.root.title(title)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.canvas = tk.Canvas(self.root, width=screen_width, height=screen_height, bg="black")
        self.canvas.pack()
        self.game_over = False
        self.score = 0
        self.delay_ms = 16
        self.root.bind('<r>', self.restart_game)
        self.root.bind('<Escape>', lambda e: self.root.quit())
        
    def update(self): pass
    
    # NOTE: draw is now implicit or defined by the abstract base. 
    # If using Python's 'abc' module, this would require @abstractmethod,
    # but for a minimal base class, we just ensure it's overridden.
    
    def loop(self): 
        if not self.game_over:
            self.update()
            self.root.after(self.delay_ms, self.loop)
            
    def run(self):
        self.loop()
        self.root.mainloop()
        return self.score
        
    def restart_game(self, event=None):
        if self.game_over:
            self.game_over = False
            self.canvas.delete("all")

# --- Cat Class ---
class Cat:
    """Represents a single Ninja Cat object."""
    CAT_SIZE = 20
    
    def __init__(self, canvas, tag, x, y, color):
        self.canvas = canvas
        self.tag = tag
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.color = color
        
        self.draw()

    def draw(self):
        """Draws the cat using multiple canvas objects grouped by the tag."""
        r = self.CAT_SIZE
        
        # 1. Body (Oval)
        self.canvas.create_oval(self.x-r, self.y-r, self.x+r, self.y+r, 
                                 fill=self.color, outline="black", tags=self.tag)
        
        # 2. Ears (Triangles)
        # Left Ear
        self.canvas.create_polygon(self.x - r/2, self.y - r, 
                                   self.x - r, self.y - r*1.5, 
                                   self.x - r*1.5, self.y - r, 
                                   fill=self.color, outline="black", tags=self.tag)
        # Right Ear
        self.canvas.create_polygon(self.x + r/2, self.y - r, 
                                   self.x + r, self.y - r*1.5, 
                                   self.x + r*1.5, self.y - r, 
                                   fill=self.color, outline="black", tags=self.tag)
        
        # 3. Eyes
        eye_color = "yellow" if self.color != "white" else "blue"
        # Left Eye
        self.canvas.create_oval(self.x - r/2, self.y - r/4, 
                                self.x - r/4, self.y + r/4, 
                                fill=eye_color, tags=self.tag)
        # Right Eye
        self.canvas.create_oval(self.x + r/4, self.y - r/4, 
                                self.x + r/2, self.y + r/4, 
                                fill=eye_color, tags=self.tag)
        
    def move_visuals(self, dx_move, dy_move):
        """Updates the position of all canvas objects associated with this cat's tag."""
        self.canvas.move(self.tag, dx_move, dy_move)

    def update_position(self, screen_width, screen_height, friction):
        """Applies physics and updates the cat's (x, y) coordinates."""
        r = self.CAT_SIZE 
        
        old_x = self.x
        old_y = self.y
        
        # Apply Friction
        self.vx *= friction
        self.vy *= friction
        
        # Update Position based on velocity
        self.x += self.vx
        self.y += self.vy
        
        # Wall Bouncing (Collision Detection) with 80% elasticity
        if self.x - r < 0: 
            self.x = r
            self.vx *= -0.8
        elif self.x + r > screen_width: 
            self.x = screen_width - r
            self.vx *= -0.8
            
        if self.y - r < 0:
            self.y = r 
            self.vy *= -0.8
        elif self.y + r > screen_height:
            self.y = screen_height - r
            self.vy *= -0.8
            
        # Calculate true movement delta for the canvas
        dx_move = self.x - old_x
        dy_move = self.y - old_y
            
        self.move_visuals(dx_move, dy_move)


# --- NinjaCatGame Class ---
class NinjaCatGame(GameBase):
    """
    Team 7 Mission: Catch the Ninja Cats
    A physics-based game where cats evade the mouse cursor and must be clicked to catch.
    """
    
    def __init__(self):
        super().__init__(screen_width=800, screen_height=600, title="Team 7 Mission: Catch the Ninja Cats")
        
        # --- Game Constants ---
        self.cat_count = 5
        self.caught_count = 0
        self.game_started = False
        self.start_time = 0
        self.end_time = 0
        
        # Physics Settings (Base Values)
        self.base_friction = 0.96
        self.base_run_speed = 3.0
        self.scare_distance = 180 
        
        # Dynamic Physics (Current Values)
        self.current_friction = self.base_friction
        self.current_run_speed = self.base_run_speed
        
        # Mouse Position Tracker
        self.mouse_x = 0
        self.mouse_y = 0

        # Cat Data Storage: List of Cat objects
        self.cats = []

        # Event Bindings
        self.canvas.bind("<Motion>", self.track_mouse)
        self.canvas.bind("<Button-1>", self.attempt_catch)
        self.root.bind("<Return>", self.start_game)

        self.setup_initial_ui()

    # --- FIX: Implement the required abstract method 'draw' ---
    def draw(self):
        """
        Placeholder method to satisfy the abstract requirement from GameBase.
        Actual drawing/moving is handled in update(), setup_initial_ui(), and end_game().
        """
        pass
    # --------------------------------------------------------

    def setup_initial_ui(self):
        """Setup the initial UI (run once at start and on restart)"""
        self.canvas.delete("start_screen_ui") 
        self.canvas.delete("game_over_ui") 
        
        self.canvas.config(bg="#47a54a")
        
        self.score_text = self.canvas.create_text(100, 30, text=f"Caught: {self.caught_count}/{self.cat_count}", fill="white", font=("Arial", 16, "bold"))
        
        self.center_msg = self.canvas.create_text(self.screen_width/2, self.screen_height/2, 
                                                 text="MISSION START\nClick the Cats!\n(They will run from your mouse)", 
                                                 fill="yellow", font=("Arial", 24, "bold"), justify="center", tags="start_screen_ui")
        self.sub_msg = self.canvas.create_text(self.screen_width/2, self.screen_height/2 + 80, 
                                             text="Press ENTER to Begin", fill="white", font=("Arial", 14), tags="start_screen_ui")


    def start_game(self, event=None):
        """Start the game"""
        if not self.game_started and not self.game_over:
            self.game_started = True
            self.game_over = False
            self.caught_count = 0
            self.cats.clear()
            self.start_time = time.time() 
            
            # Reset difficulty
            self.current_friction = self.base_friction
            self.current_run_speed = self.base_run_speed
            
            self.canvas.delete("start_screen_ui") 
            self.canvas.delete("game_over_ui") 
            
            self.canvas.delete(self.score_text)
            self.score_text = self.canvas.create_text(100, 30, text="Caught: 0/5", fill="white", font=("Arial", 16, "bold"))
            
            self.spawn_cats()

    def spawn_cats(self):
        """Spawn cats with random positions and initial velocities."""
        colors = ["black", "white", "orange", "grey", "sienna"]
        r = Cat.CAT_SIZE 
        
        for i in range(self.cat_count):
            x = random.randint(r * 2, self.screen_width - r * 2)
            y = random.randint(r * 2, self.screen_height - r * 2)
            
            tag = f"cat_{i}"
            color = colors[i % len(colors)]
            
            new_cat = Cat(self.canvas, tag, x, y, color)
            self.cats.append(new_cat)
            
            if i == 2: # Tora ribbon feature
                self.canvas.create_oval(x-5, y+r-5, x+5, y+r+5, fill="red", tags=tag)

    def track_mouse(self, event):
        """Track mouse position for cat evasion"""
        self.mouse_x = event.x
        self.mouse_y = event.y

    def attempt_catch(self, event):
        """Attempt to catch a cat with mouse click."""
        if not self.game_started or self.game_over: return
        
        click_radius = 25 
        items = self.canvas.find_overlapping(event.x - click_radius, event.y - click_radius, 
                                             event.x + click_radius, event.y + click_radius)
        
        for cat in list(self.cats):
            cat_parts = self.canvas.find_withtag(cat.tag)
            
            if not set(items).isdisjoint(cat_parts):
                self.catch_cat(cat)
                return 

    def catch_cat(self, cat):
        """Handle catching a cat"""
        self.canvas.delete(cat.tag) 
        self.cats.remove(cat)
        
        # Show "POOF" with fading color 
        poof = self.canvas.create_text(cat.x, cat.y, text="POOF!", fill="#FFFF00", font=("Arial", 16, "bold"))
        self.root.after(100, lambda: self.canvas.itemconfig(poof, fill="#FFA500")) 
        self.root.after(300, lambda: self.canvas.delete(poof))
        
        self.caught_count += 1
        self.score = self.caught_count * 100
        
        # Difficulty Scaling
        if self.caught_count < self.cat_count:
            self.current_run_speed += 0.5
            self.current_friction = max(0.85, self.current_friction - 0.015) 
        
        if self.score_text:
            self.canvas.itemconfig(self.score_text, text=f"Caught: {self.caught_count}/{self.cat_count}")
        
        if self.caught_count == self.cat_count:
            self.end_game()

    def update(self):
        """Update game logic for all cats."""
        if not self.game_started or self.game_over:
            return
            
        for cat in self.cats:
            # 1. Calculate Distance and Evasion Logic
            dx = cat.x - self.mouse_x
            dy = cat.y - self.mouse_y
            dist = math.sqrt(dx*dx + dy*dy)
            
            if dist < self.scare_distance and dist > 0.1: 
                norm_x = dx / dist
                norm_y = dy / dist
                
                # Use current run speed, which scales up
                force_magnitude = self.current_run_speed * (1 - dist / self.scare_distance) 

                cat.vx += norm_x * force_magnitude
                cat.vy += norm_y * force_magnitude

            # 2. Apply physics updates (using current friction)
            cat.update_position(self.screen_width, self.screen_height, self.current_friction)

    def end_game(self):
        """End the game"""
        self.game_over = True
        self.game_started = False
        self.end_time = time.time() 
        
        time_elapsed = self.end_time - self.start_time
        
        # Enhanced End Screen
        time_msg = f"Time Taken: {time_elapsed:.2f} seconds"
        score_msg = f"Final Score: {self.score} points"
        
        self.canvas.create_text(self.screen_width/2, self.screen_height/2 - 40, 
                               text="MISSION COMPLETE!", fill="gold", font=("Arial", 30, "bold"), tags="game_over_ui")
        
        self.canvas.create_text(self.screen_width/2, self.screen_height/2 + 10, 
                               text=time_msg, fill="#FFFFFF", font=("Arial", 18), tags="game_over_ui")
                               
        self.canvas.create_text(self.screen_width/2, self.screen_height/2 + 50, 
                               text=score_msg, fill="#FFFFFF", font=("Arial", 18), tags="game_over_ui")
                               
        self.canvas.create_text(self.screen_width/2, self.screen_height/2 + 100, 
                               text="Press R to Replay or ESC to Quit", fill="light grey", font=("Arial", 14), tags="game_over_ui")
        # Auto-close after 3 seconds to allow score capture
        self.root.after(3000, self.root.quit)

    def restart_game(self, event=None):
        """Restart the game"""
        super().restart_game()
        
        self.game_started = False
        self.caught_count = 0
        self.cats.clear()
        
        # Reset current physics values to base values for the new game
        self.current_friction = self.base_friction
        self.current_run_speed = self.base_run_speed
        
        self.setup_initial_ui()

    def run(self):
        """Override run to print score for launcher"""
        score = super().run()
        print(f"FINAL_SCORE:{score}")  # Clear marker for score extraction
        return score

# --- Main Execution ---
if __name__ == "__main__":
    game = NinjaCatGame()
    final_score = game.run()