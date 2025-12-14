import tkinter as tk
import random

class ShadowCloneWhackAMole:
    def __init__(self, root):
        self.root = root
        self.root.title("Naruto: Shadow Clone Whack-a-Mole")
        self.root.resizable(False, False)

        # Game Settings
        self.score = 0
        self.time_left = 30
        self.game_running = False
        
        # Combo system
        self.combo = 0
        
        # Smarter spawning
        self.max_active = 1  # how many holes can be active at once
        self.active_count = 0
        
        # Difficulty parameters
        self.spawn_speed = 800 # Milliseconds between spawns (start)
        self.stay_time = 700   # How long a mole stays up

        # UI Layout
        top_frame = tk.Frame(root, pady=10)
        top_frame.pack()

        self.score_label = tk.Label(top_frame, text="Score: 0", font=("Arial", 14, "bold"))
        self.score_label.pack(side=tk.LEFT, padx=20)

        self.time_label = tk.Label(top_frame, text="Time: 30", font=("Arial", 14, "bold"))
        self.time_label.pack(side=tk.RIGHT, padx=20)

        # Combo display
        self.combo_label = tk.Label(top_frame, text="Combo: 0", font=("Arial", 12, "bold"))
        self.combo_label.pack(side=tk.RIGHT, padx=20)

        # The Grid Area
        grid_frame = tk.Frame(root, padx=20, pady=20)
        grid_frame.pack()

        self.buttons = []
        self.hole_states = [] # To track what is in each hole ('empty', 'naruto', 'log')

        # Create 3x3 Grid of Buttons
        for i in range(9):
            # Create a button. Note the lambda to pass the specific index 'i'
            btn = tk.Button(grid_frame, text="", width=10, height=4, font=("Arial", 10, "bold"),
                            bg="lightgrey", command=lambda index=i: self.on_hole_click(index))
            
            # Grid math: Row is i divided by 3, Col is i modulo 3
            btn.grid(row=i//3, column=i%3, padx=5, pady=5)
            
            self.buttons.append(btn)
            self.hole_states.append("empty")

        # Start Button
        self.start_btn = tk.Button(root, text="START MISSION", font=("Arial", 12, "bold"), 
                                   bg="orange", fg="white", command=self.start_game)
        self.start_btn.pack(pady=10)

    def start_game(self):
        if not self.game_running:
            self.game_running = True
            self.score = 0
            self.time_left = 30
            self.combo = 0
            self.spawn_speed = 800
            self.max_active = 1
            
            self.score_label.config(text="Score: 0")
            self.time_label.config(text="Time: 30")
            self.combo_label.config(text="Combo: 0")
            self.start_btn.config(state="disabled", text="Mission in Progress...")
            
            # Reset all buttons
            for i in range(9):
                self.reset_hole(i)

            # Start Loops
            self.update_timer()
            self.spawn_loop()

    def update_timer(self):
        if self.game_running:
            self.time_left -= 1
            self.time_label.config(text=f"Time: {self.time_left}")
            
            # Make game faster as time runs out
            if self.time_left < 20: self.spawn_speed = 700
            if self.time_left < 10: self.spawn_speed = 500

            if self.time_left <= 0:
                self.end_game()
            else:
                self.root.after(1000, self.update_timer)

    def spawn_loop(self):
        if not self.game_running:
            return

        empty_indices = [i for i, s in enumerate(self.hole_states) if s == "empty"]

        # Allow multiple spawns later in the game
        spawn_count = min(self.max_active, len(empty_indices))

        for index in random.sample(empty_indices, spawn_count):
            is_naruto = random.random() > 0.25

            if is_naruto:
                self.hole_states[index] = "naruto"
                self.buttons[index].config(
                    text="NARUTO", bg="orange", activebackground="orange"
                )
            else:
                self.hole_states[index] = "log"
                self.buttons[index].config(
                    text="LOG", bg="saddlebrown", fg="white"
                )

            self.root.after(self.stay_time, lambda idx=index: self.miss_check(idx))

        self.root.after(self.spawn_speed, self.spawn_loop)

    def miss_check(self, index):
        if not self.game_running:
            return

        if self.hole_states[index] == "naruto":
            # Missed Naruto = penalty
            self.score -= 3
            self.score_label.config(text=f"Score: {self.score}")
            self.combo = 0
            self.combo_label.config(text="Combo: 0")

        if self.hole_states[index] in ["naruto", "log"]:
            self.reset_hole(index)

    def auto_hide(self, index):
        # Only reset if it hasn't been clicked yet (still equals naruto or log)
        if self.game_running and self.hole_states[index] in ["naruto", "log"]:
            self.miss_check(index)

    def reset_hole(self, index):
        self.hole_states[index] = "empty"
        self.buttons[index].config(text="", bg="lightgrey", fg="black", activebackground="lightgrey")

    def adjust_difficulty(self):
        if self.score >= 100:
            self.spawn_speed = 500
            self.stay_time = 600
            self.max_active = 2

        if self.score >= 250:
            self.spawn_speed = 400
            self.stay_time = 500
            self.max_active = 3

    def on_hole_click(self, index):
        if not self.game_running: return

        state = self.hole_states[index]

        if state == "naruto":
            self.combo += 1
            points = 10 + (self.combo * 2)
            self.score += points

            self.score_label.config(text=f"Score: {self.score}")
            self.combo_label.config(text=f"Combo: {self.combo}")

            self.buttons[index].config(text="POOF!", bg="lightgreen")
            self.hole_states[index] = "hit"
            self.root.after(300, lambda: self.reset_hole(index))
            
            self.adjust_difficulty()

        elif state == "log":
            self.combo = 0
            self.score -= 10
            self.time_left -= 2   # TIME penalty

            self.time_label.config(text=f"Time: {self.time_left}")
            self.score_label.config(text=f"Score: {self.score}")
            self.combo_label.config(text="Combo: 0")

            self.buttons[index].config(text="TRAPPED!", bg="red")
            self.hole_states[index] = "hit"
            self.root.after(300, lambda: self.reset_hole(index))

    def end_game(self):
        self.game_running = False
        self.start_btn.config(state="normal", text="Restart Mission")
        self.time_label.config(text="Time: 0")
        
        # Show Game Over on all buttons
        for btn in self.buttons:
            btn.config(text="---", bg="grey")
        
        # Show final message
        final_msg = f"Mission Complete!\nFinal Score: {self.score}"
        tk.messagebox.showinfo("Result", final_msg)
        print(f"FINAL_SCORE:{self.score}")  # Print score for launcher to capture
        self.root.after(3000, self.root.quit)

if __name__ == "__main__":
    import tkinter.messagebox # Needed for the pop-up at the end
    root = tk.Tk()
    game = ShadowCloneWhackAMole(root)
    root.mainloop()
