#!/usr/bin/env python3
"""
Ramen Shop Game - Naruto-themed restaurant game
Serve customers by assembling ramen orders correctly and quickly!
"""

# Standard library imports
import random
import tkinter as tk

class RamenShopGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Ichiraku Ramen Server")
        self.root.geometry("600x550")
        self.root.resizable(False, False)

        # --- Game Data ---
        self.ingredients_list = ["Noodles", "Broth", "Pork", "Egg", "Naruto", "Scallion"]
        # Colors for buttons to make them look distinct without images
        self.ing_colors = {
            "Noodles": "khaki", "Broth": "saddlebrown", "Pork": "lightpink",
            "Egg": "white", "Naruto": "hotpink", "Scallion": "lightgreen"
        }
        
        self.current_order = []
        self.player_bowl = []
        self.score = 0
        self.time_left = 0
        self.game_running = False
        self.max_time = 15 # Seconds per customer (gets lower)
        
        # Timer and input control
        self.timer_job = None
        self.input_locked = False
        self.combo = 0

        # --- UI Setup ---
        
        # 1. Header (Score and Timer)
        header_frame = tk.Frame(root, pady=10)
        header_frame.pack(fill="x")
        
        self.score_label = tk.Label(header_frame, text="Score: 0 | Combo x0", font=("Arial", 14, "bold"), fg="blue")
        self.score_label.pack(side="left", padx=20)
        
        self.timer_label = tk.Label(header_frame, text="Time: 0", font=("Arial", 14, "bold"), fg="red")
        self.timer_label.pack(side="right", padx=20)

        # 2. Customer Order Area
        order_frame = tk.LabelFrame(root, text="Current Order", font=("Arial", 12, "bold"), pady=10, padx=10)
        order_frame.pack(pady=10, fill="x", padx=20)

        self.customer_text = tk.Label(order_frame, text="Press Start to Open Shop", font=("Arial", 12))
        self.customer_text.pack()
        
        self.order_display = tk.Label(order_frame, text="", font=("Courier", 14, "bold"), fg="darkred", wraplength=550)
        self.order_display.pack(pady=5)

        # 3. Player's Work Area (Current Bowl)
        bowl_frame = tk.LabelFrame(root, text="Your Bowl (Construction)", font=("Arial", 12, "bold"), pady=10, padx=10, bg="#fff8e7")
        bowl_frame.pack(pady=10, fill="x", padx=20)

        self.bowl_display = tk.Label(bowl_frame, text="[ Empty ]", font=("Courier", 12), bg="#fff8e7")
        self.bowl_display.pack()

        # 4. Action Buttons (Serve / Trash)
        action_frame = tk.Frame(root)
        action_frame.pack(pady=5)
        
        self.serve_btn = tk.Button(action_frame, text="SERVE ORDER!", bg="gold", font=("Arial", 12, "bold"), command=self.serve_order, state="disabled")
        self.serve_btn.pack(side="left", padx=10)
        
        self.trash_btn = tk.Button(action_frame, text="Trash/Reset", bg="grey", fg="white", font=("Arial", 12), command=self.reset_bowl, state="disabled")
        self.trash_btn.pack(side="left", padx=10)

        # 5. Ingredient Buttons (The Kitchen)
        kitchen_frame = tk.Frame(root, pady=20)
        kitchen_frame.pack()
        
        self.ing_buttons = []
        # Create a 2x3 grid of buttons
        row = 0
        col = 0
        for item in self.ingredients_list:
            btn = tk.Button(kitchen_frame, text=item, bg=self.ing_colors[item], width=12, height=3, font=("Arial", 10, "bold"),
                            command=lambda i=item: self.add_ingredient(i))
            btn.grid(row=row, column=col, padx=5, pady=5)
            self.ing_buttons.append(btn)
            
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        # 6. Main Start Button
        self.start_btn = tk.Button(root, text="OPEN SHOP", bg="orange", font=("Arial", 16, "bold"), command=self.start_game)
        self.start_btn.pack(side="bottom", pady=20)
        
        self.toggle_kitchen(False)

    def toggle_kitchen(self, state):
        status = "normal" if state else "disabled"
        for btn in self.ing_buttons:
            btn.config(state=status)
        self.serve_btn.config(state=status)
        self.trash_btn.config(state=status)

    def start_game(self):
        self.game_running = True
        self.score = 0
        self.combo = 0
        self.max_time = 15
        self.score_label.config(text="Score: 0 | Combo x0")
        self.start_btn.pack_forget() # Hide start button
        self.toggle_kitchen(True)
        self.next_customer()
        self.update_timer()

    def next_customer(self):
        # 1. Determine Difficulty (Length of order)
        num_items = random.randint(3, 6)
        
        # 2. Generate Order (Allow duplicates, e.g., double pork)
        self.current_order = [random.choice(self.ingredients_list) for _ in range(num_items)]
        
        # 3. Reset Player Bowl
        self.reset_bowl()
        
        # 4. Update UI
        names = ["Naruto", "Sakura", "Sasuke", "Kakashi", "Choji", "Hinata"]
        customer = random.choice(names)
        self.customer_text.config(text=f"Customer: {customer}")
        
        # Display order nicely with arrows
        order_str = " -> ".join(self.current_order)
        self.order_display.config(text=order_str)
        
        # 5. Reset Timer
        self.time_left = self.max_time
        self.timer_label.config(text=f"Time: {self.time_left}")

    def update_timer(self):
        if not self.game_running:
            return

        self.time_left -= 1
        self.timer_label.config(text=f"Time: {self.time_left}")

        if self.time_left <= 0:
            self.game_over()
        else:
            self.timer_job = self.root.after(1000, self.update_timer)

    def add_ingredient(self, item):
        if not self.game_running or self.input_locked:
            return
        
        self.player_bowl.append(item)
        
        # Update display
        bowl_str = " + ".join(self.player_bowl)
        self.bowl_display.config(text=bowl_str)
        
        # Visual validation feedback
        idx = len(self.player_bowl) - 1
        if idx < len(self.current_order):
            if self.player_bowl[idx] != self.current_order[idx]:
                self.bowl_display.config(fg="red")
            else:
                self.bowl_display.config(fg="green")
        else:
            self.bowl_display.config(fg="red")
        
        # Auto-fail if bowl is already longer than order
        if len(self.player_bowl) > len(self.current_order):
            self.bowl_display.config(text="TOO MANY ITEMS! (Reset)", fg="red")

    def reset_bowl(self):
        self.player_bowl = []
        self.bowl_display.config(text="[ Empty ]", fg="black")

    def serve_order(self):
        if not self.game_running or self.input_locked:
            return
        
        # Check logic: Lists must match exactly
        if self.player_bowl == self.current_order:
            # Success!
            self.combo += 1
            points = 10 + (self.combo * 2)
            self.score += points
            self.score_label.config(text=f"Score: {self.score} | Combo x{self.combo}")
            
            # Smooth difficulty scaling
            self.max_time = max(5, 15 - (self.score // 20))
            
            self.next_customer()
        else:
            # Failed Order
            self.combo = 0
            self.input_locked = True
            self.time_left = max(0, self.time_left - 5)
            self.bowl_display.config(text="WRONG ORDER! -5 Seconds", fg="red")
            self.root.after(800, self.unlock_bowl)

    def game_over(self):
        self.game_running = False
        
        # Cancel timer
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None
            
        self.toggle_kitchen(False)
        self.customer_text.config(text="SHOP CLOSED")
        self.order_display.config(text=f"Final Score: {self.score}\nBest Combo: {self.combo}")
        self.start_btn.config(text="Play Again")
        self.start_btn.pack(side="bottom", pady=20)
        
        # Print final score for game launcher integration
        print(f"FINAL_SCORE:{self.score}")
        self.root.after(3000, self.root.quit)
        
    def unlock_bowl(self):
        self.player_bowl = []
        self.bowl_display.config(text="[ Empty ]", fg="black")
        self.input_locked = False

if __name__ == "__main__":
    root = tk.Tk()
    game = RamenShopGame(root)
    root.mainloop()
