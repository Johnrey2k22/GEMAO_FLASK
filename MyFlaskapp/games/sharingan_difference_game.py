import tkinter as tk
from tkinter import messagebox
import random

class SharinganDifferenceGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Sharingan Training: Spot the Difference")
        self.root.resizable(False, False)

        # Game Constants
        self.width = 800
        self.height = 400
        self.midpoint = 400  # The split line
        self.time_limit = 30
        self.remaining_time = self.time_limit
        self.score = 0
        self.total_diffs = 5
        self.game_running = False

        # Store the hitboxes of the differences
        # Format: {'x1': val, 'y1': val, 'x2': val, 'y2': val, 'found': False}
        self.differences = []

        # UI Setup with themed colors
        self.root.configure(bg="#F0F0F0")
        top_frame = tk.Frame(root, pady=10, bg="#F0F0F0")
        top_frame.pack()

        self.time_label = tk.Label(top_frame, text=f"Time: {self.time_limit}", 
                                   font=("Impact", 18, "bold"), fg="red", bg="#F0F0F0")
        self.time_label.pack(side=tk.LEFT, padx=20)

        self.score_label = tk.Label(top_frame, text=f"Found: 0/{self.total_diffs}", 
                                    font=("Impact", 18, "bold"), fg="#D4AF37", bg="#F0F0F0")
        self.score_label.pack(side=tk.LEFT, padx=20)

        # The Game Area
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="white")
        self.canvas.pack()

        # Divider Line with themed color
        self.canvas.create_line(self.midpoint, 0, self.midpoint, self.height, width=5, fill="red")

        # Instruction / Start Overlay
        self.start_text = self.canvas.create_text(self.width/2, self.height/2, text="Activate SHARINGAN\nPress ENTER to Start", 
                                                  font=("Arial", 24, "bold"), fill="black", justify="center")

        # Controls
        self.canvas.bind("<Button-1>", self.on_click)
        self.root.bind("<Return>", self.start_game)

    def start_game(self, event=None):
        if not self.game_running:
            self.game_running = True
            self.remaining_time = self.time_limit
            self.score = 0
            
            self.score_label.config(text=f"Found: 0/{self.total_diffs}")
            self.canvas.delete("all")  # Clear canvas
            
            # Redraw Divider with themed color
            self.canvas.create_line(self.midpoint, 0, self.midpoint, self.height, width=5, fill="red")
            
            # Generate random differences for this round
            self.differences = self._generate_differences_for_round()
            
            # Draw Scenes with dynamic differences
            self.draw_scene(offset_x=0, is_right_side=False)      # Original (Left)
            self.draw_scene(offset_x=self.midpoint, is_right_side=True)  # Altered (Right)
            
            self.update_timer()

    def _generate_differences_for_round(self):
        """Generate random differences for the current round"""
        differences = []
        
        # Randomly select which differences to include (always include 5)
        diff_types = random.sample([
            'sun_color', 'log_scratch', 'missing_apple', 
            'headband_color', 'cloud_position'
        ], 5)
        
        # Store the selected difference types for use in drawing methods
        self.active_differences = diff_types
        
        return differences

    def _get_difficulty_params(self):
        """Get randomized parameters for differences"""
        return {
            'sun_base_radius': random.randint(25, 35),
            'sun_diff_radius': random.randint(20, 30),
            'cloud_base_x': random.randint(40, 60),
            'cloud_diff_x': random.randint(70, 90),
            'apple_present': random.choice([True, False]),
            'headband_base_color': 'blue',
            'headband_diff_color': 'red'
        }

    def draw_scene(self, offset_x, is_right_side):
        """ Draws the entire scene. If is_right_side is True, it draws the differences. """
        self._draw_sky_and_ground(offset_x)
        self._draw_mountains(offset_x)
        self._draw_sun(offset_x, is_right_side)
        self._draw_target_log(offset_x, is_right_side)
        self._draw_tree(offset_x, is_right_side)
        self._draw_ninja(offset_x, is_right_side)
        self._draw_cloud(offset_x, is_right_side)

    def _draw_sky_and_ground(self, offset_x):
        """Draw sky and ground background"""
        self.canvas.create_rectangle(0 + offset_x, 0, 400 + offset_x, 300, fill="#87CEEB", outline="")  # Sky
        self.canvas.create_rectangle(0 + offset_x, 300, 400 + offset_x, 400, fill="#32CD32", outline="")  # Grass

    def _draw_mountains(self, offset_x):
        """Draw mountain range"""
        self.canvas.create_polygon(50 + offset_x, 300, 150 + offset_x, 100, 250 + offset_x, 300, fill="grey", outline="black")
        self.canvas.create_polygon(200 + offset_x, 300, 300 + offset_x, 150, 400 + offset_x, 300, fill="grey", outline="black")

    def _draw_sun(self, offset_x, is_right_side):
        """Draw sun with color difference"""
        if hasattr(self, 'active_differences') and 'sun_color' in self.active_differences:
            params = self._get_difficulty_params()
            sun_color = "yellow"
            sun_radius = params['sun_base_radius']
            
            if is_right_side:
                sun_color = "orange"  # Difference
                sun_radius = params['sun_diff_radius']
                # Store Hitbox
                self.differences.append({
                    'x1': 30+offset_x, 'y1': 30, 
                    'x2': 30+offset_x + sun_radius*2, 'y2': 30 + sun_radius*2, 
                    'found': False
                })
            
            self.canvas.create_oval(30 + offset_x, 30, 30 + offset_x + sun_radius*2, 30 + sun_radius*2, 
                                   fill=sun_color, outline="orange", width=2)
        else:
            # Default sun if not selected as difference
            self.canvas.create_oval(30 + offset_x, 30, 90 + offset_x, 90, 
                                   fill="yellow", outline="orange", width=2)

    def _draw_target_log(self, offset_x, is_right_side):
        """Draw wooden target log with optional scratch"""
        self.canvas.create_rectangle(100 + offset_x, 250, 140 + offset_x, 320, fill="saddlebrown", outline="black")
        
        if hasattr(self, 'active_differences') and 'log_scratch' in self.active_differences:
            if is_right_side:
                # Draw a scratch
                self.canvas.create_line(110 + offset_x, 270, 130 + offset_x, 290, fill="black", width=2)
                self.differences.append({'x1': 110+offset_x, 'y1': 270, 'x2': 130+offset_x, 'y2': 290, 'found': False})

    def _draw_tree(self, offset_x, is_right_side):
        """Draw tree with fruit difference"""
        self.canvas.create_rectangle(350 + offset_x, 220, 380 + offset_x, 320, fill="saddlebrown", outline="")  # Trunk
        self.canvas.create_oval(320 + offset_x, 150, 410 + offset_x, 240, fill="darkgreen", outline="")  # Leaves

        # Apple 1 (Both sides)
        self.canvas.create_oval(340 + offset_x, 180, 355 + offset_x, 195, fill="red", outline="black")
        
        if hasattr(self, 'active_differences') and 'missing_apple' in self.active_differences:
            if not is_right_side:
                # Apple 2 (Left only)
                self.canvas.create_oval(370 + offset_x, 200, 385 + offset_x, 215, fill="red", outline="black")
            else:
                # Right side, the apple is missing. The hitbox is where the apple SHOULD be.
                self.differences.append({'x1': 365+offset_x, 'y1': 195, 'x2': 390+offset_x, 'y2': 220, 'found': False})
        else:
            # Default: both sides have apple 2
            self.canvas.create_oval(370 + offset_x, 200, 385 + offset_x, 215, fill="red", outline="black")

    def _draw_ninja(self, offset_x, is_right_side):
        """Draw ninja silhouette with headband color difference"""
        # Head
        self.canvas.create_oval(250 + offset_x, 280, 270 + offset_x, 300, fill="black")
        # Body
        self.canvas.create_line(260 + offset_x, 300, 260 + offset_x, 340, width=3)
        # Arms
        self.canvas.create_line(240 + offset_x, 310, 280 + offset_x, 310, width=3) 
        # Legs
        self.canvas.create_line(260 + offset_x, 340, 250 + offset_x, 370, width=3)
        self.canvas.create_line(260 + offset_x, 340, 270 + offset_x, 370, width=3)

        # Headband with color difference
        if hasattr(self, 'active_differences') and 'headband_color' in self.active_differences:
            params = self._get_difficulty_params()
            band_color = params['headband_base_color']
            if is_right_side:
                band_color = params['headband_diff_color']
                self.differences.append({'x1': 250+offset_x, 'y1': 280, 'x2': 270+offset_x, 'y2': 300, 'found': False})
        else:
            # Default headband color
            band_color = "blue"
        
        self.canvas.create_line(250 + offset_x, 285, 268 + offset_x, 285, fill=band_color, width=2)

    def _draw_cloud(self, offset_x, is_right_side):
        """Draw cloud with position difference"""
        if hasattr(self, 'active_differences') and 'cloud_position' in self.active_differences:
            params = self._get_difficulty_params()
            cloud_x = params['cloud_base_x']
            if is_right_side:
                cloud_x = params['cloud_diff_x']  # Moved randomly
                self.differences.append({'x1': cloud_x+offset_x, 'y1': 40, 'x2': cloud_x+60+offset_x, 'y2': 70, 'found': False})
        else:
            # Default cloud position
            cloud_x = 50
        
        self.canvas.create_oval(cloud_x + offset_x, 40, cloud_x + 60 + offset_x, 70, fill="white", outline="")

    def update_timer(self):
        if self.game_running:
            self.remaining_time -= 1
            self.time_label.config(text=f"Time: {self.remaining_time}")

            if self.remaining_time <= 0:
                self.end_game(won=False)
            else:
                self.root.after(1000, self.update_timer)

    def on_click(self, event):
        if not self.game_running:
            return

        # Only accept clicks on the RIGHT side (> 400)
        if event.x < self.midpoint:
            return

        click_x = event.x
        click_y = event.y
        
        hit_something = False

        for diff in self.differences:
            if not diff['found']:
                if diff['x1'] <= click_x <= diff['x2'] and diff['y1'] <= click_y <= diff['y2']:
                    # HIT!
                    self.found_difference(diff)
                    hit_something = True
                    break
        
        if not hit_something:
            # Click penalty: deduct 3 seconds for missed clicks
            self.remaining_time = max(0, self.remaining_time - 3)
            self.time_label.config(text=f"Time: {self.remaining_time}", fg="darkred")
            # Flash effect for penalty
            self.root.after(200, lambda: self.time_label.config(fg="red"))
            if self.remaining_time <= 0:
                self.end_game(won=False)

    def found_difference(self, diff):
        diff['found'] = True
        self.score += 1
        self.score_label.config(text=f"Found: {self.score}/{self.total_diffs}")
        
        # Visual Feedback: Draw a Sharingan Ring (concentric circles)
        center_x = (diff['x1'] + diff['x2']) / 2
        center_y = (diff['y1'] + diff['y2']) / 2
        radius = 25
        
        # Outer Ring (Thick)
        self.canvas.create_oval(center_x - radius, center_y - radius, 
                                center_x + radius, center_y + radius, 
                                outline="red", width=4, tags="feedback")
        
        # Inner Ring (Thinner, Black) - Themed look
        self.canvas.create_oval(center_x - radius/2, center_y - radius/2, 
                                center_x + radius/2, center_y + radius/2, 
                                outline="black", width=2, tags="feedback")
        
        if self.score == self.total_diffs:
            self.end_game(won=True)

    def end_game(self, won=False):
        self.game_running = False
        if won:
            messagebox.showinfo("Mission Complete", f"Great job! Your Sharingan saw through the Genjutsu!\nTime left: {self.remaining_time}s")
        else:
            messagebox.showerror("Mission Failed", "The Genjutsu was too strong. You ran out of time!")
        
        print(f"FINAL_SCORE:{self.score}")  # Print score for launcher to capture
        self.root.after(3000, self.root.quit)

if __name__ == "__main__":
    root = tk.Tk()
    game = SharinganDifferenceGame(root)
    root.mainloop()
