# Standard library imports
import random
import time
import tkinter as tk

class ShurikenGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Naruto: Shuriken Target Practice")
        self.root.resizable(False, False)

        # Game Settings
        self.width = 600
        self.height = 500
        self.player_speed = 20
        self.shuriken_speed = 10
        self.target_speed = 3
        self.spawn_interval = 800  # milliseconds
        
        # Time tracking
        self.last_spawn_time = 0
        self.last_shot_time = 0
        self.shot_cooldown = 300  # milliseconds
        
        self.score = 0
        self.lives = 3
        
        # KEY CHANGE: Start with game_over = True so the game waits for the user
        self.game_over = True 
        
        self.shurikens = [] # List to hold shuriken IDs
        self.targets = []   # List to hold target IDs

        # Create Canvas
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="skyblue")
        self.canvas.pack()

        # UI Elements
        self.score_text = self.canvas.create_text(50, 20, text="Score: 0", fill="black", font=("Arial", 14, "bold"))
        self.lives_text = self.canvas.create_text(self.width - 80, 20, text="Lives: 3", font=("Arial", 14, "bold"))
        
        # Start Screen Text
        self.game_over_text = self.canvas.create_text(self.width/2, self.height/2, text="NARUTO TRAINING", fill="orange", font=("Arial", 30, "bold"))
        self.restart_text = self.canvas.create_text(self.width/2, self.height/2 + 50, text="Press ENTER to Start", fill="black", font=("Arial", 15))

        # Create Player (Naruto represented by Orange Block)
        player_start_x = self.width / 2 - 20
        self.player = self.canvas.create_rectangle(player_start_x, 450, player_start_x + 40, 480, fill="orange", outline="black")

        # Controls
        self.root.bind("<Left>", self.move_left)
        self.root.bind("<Right>", self.move_right)
        self.root.bind("<space>", self.shoot_shuriken)
        self.root.bind("<Return>", self.restart_game)

        # Note: We do NOT call update_game() here. It starts when you press Enter.

    def move_left(self, event):
        if not self.game_over:
            coords = self.canvas.coords(self.player)
            # Safety check if player exists
            if coords and coords[0] > 0:
                self.canvas.move(self.player, -self.player_speed, 0)

    def move_right(self, event):
        if not self.game_over:
            coords = self.canvas.coords(self.player)
            if coords and coords[2] < self.width:
                self.canvas.move(self.player, self.player_speed, 0)

    def shoot_shuriken(self, event):
        if self.game_over:
            return

        now = time.time() * 1000  # Convert to milliseconds
        if now - self.last_shot_time < self.shot_cooldown:
            return

        self.last_shot_time = now
        
        p_coords = self.canvas.coords(self.player)
        if not p_coords: return

        center_x = (p_coords[0] + p_coords[2]) / 2
        top_y = p_coords[1]

        # Create Shuriken (Grey Diamond shape)
        shuriken = self.canvas.create_polygon(
            center_x, top_y - 10,       # Top
            center_x - 5, top_y,        # Left
            center_x, top_y + 10,       # Bottom
            center_x + 5, top_y,        # Right
            fill="grey", outline="black"
        )
        self.shurikens.append(shuriken)

    def spawn_target(self, now):
        if now - self.last_spawn_time >= self.spawn_interval:
            self.last_spawn_time = now

            y_pos = random.randint(60, 200)
            direction = random.choice([-1, 1])

            if direction == 1:
                x1, x2 = -50, 0
            else:
                x1, x2 = self.width, self.width + 50

            target = self.canvas.create_rectangle(
                x1, y_pos, x2, y_pos + 20,
                fill="saddlebrown", outline="black"
            )

            self.targets.append({
                "id": target,
                "dir": direction,
                "speed": self.target_speed
            }) 

    def miss_target(self):
        self.lives -= 1
        self.canvas.itemconfig(self.lives_text, text=f"Lives: {self.lives}")

        if self.lives <= 0:
            self.end_game()

    def check_collisions(self):
        for s in list(self.shurikens):
            s_box = self.canvas.bbox(s)
            if not s_box:
                continue

            for t in list(self.targets):
                t_box = self.canvas.bbox(t["id"])
                if not t_box:
                    continue

                if self.box_overlap(s_box, t_box):
                    self.handle_hit(s, t)
                    break

    def box_overlap(self, a, b):
        return not (
            a[2] < b[0] or
            a[0] > b[2] or
            a[3] < b[1] or
            a[1] > b[3]
        )

    def handle_hit(self, shuriken, target):
        self.score += 10
        self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")

        self.canvas.delete(shuriken)
        self.canvas.delete(target["id"])

        self.shurikens.remove(shuriken)
        self.targets.remove(target)

        self.increase_difficulty()

    def increase_difficulty(self):
        if self.score % 50 == 0:
            self.target_speed += 0.5
            self.spawn_interval = max(300, self.spawn_interval - 50)

    def update_game(self):
        if not self.game_over:
            now = time.time() * 1000
            self.spawn_target(now)

            # --- Move Shurikens ---
            for s in list(self.shurikens):
                self.canvas.move(s, 0, -self.shuriken_speed)
                coords = self.canvas.coords(s)
                
                if not coords:
                    if s in self.shurikens: self.shurikens.remove(s)
                    continue

                if coords[1] < 0:
                    self.canvas.delete(s)
                    if s in self.shurikens: self.shurikens.remove(s)

            # --- Move Targets ---
            for t in list(self.targets):
                self.canvas.move(t['id'], t['speed'] * t['dir'], 0)
                coords = self.canvas.coords(t['id'])
                
                if not coords:
                    if t in self.targets: self.targets.remove(t)
                    continue
                
                if (t['dir'] == 1 and coords[0] > self.width) or (t['dir'] == -1 and coords[2] < 0):
                    self.canvas.delete(t['id'])
                    self.targets.remove(t)
                    self.miss_target()

            self.check_collisions()

            self.root.after(30, self.update_game)

    def end_game(self):
        self.game_over = True
        self.canvas.itemconfig(self.game_over_text, text="GAME OVER")
        self.canvas.itemconfig(self.restart_text, text="Press ENTER to Restart")
        print(f"FINAL_SCORE:{self.score}")  # Print score for launcher to capture
        self.root.after(3000, self.root.quit)

    def restart_game(self, event):
        # Only restart if the game is currently over/paused
        if self.game_over:
            self.game_over = False
            self.score = 0
            self.lives = 3
            self.target_speed = 3
            self.spawn_interval = 800
            self.last_spawn_time = 0
            self.last_shot_time = 0
            
            self.canvas.itemconfig(self.score_text, text="Score: 0")
            self.canvas.itemconfig(self.lives_text, text="Lives: 3")
            self.canvas.itemconfig(self.game_over_text, text="")
            self.canvas.itemconfig(self.restart_text, text="")
            
            # Clear existing items
            for s in self.shurikens: self.canvas.delete(s)
            for t in self.targets: self.canvas.delete(t['id'])
            self.shurikens.clear()
            self.targets.clear()
            
            # Reset Player Position
            self.canvas.delete(self.player)
            player_start_x = self.width / 2 - 20
            self.player = self.canvas.create_rectangle(player_start_x, 450, player_start_x + 40, 480, fill="orange", outline="black")
            
            # Start the loop
            self.update_game()


if __name__ == "__main__":
    root = tk.Tk()
    game = ShurikenGame(root)
    root.mainloop()