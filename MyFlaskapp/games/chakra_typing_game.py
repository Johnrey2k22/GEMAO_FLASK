# Standard library imports
import random
import time
import tkinter as tk

class ChakraTypingGame:
    def __init__(self, root):
        self.root = root
        self.root.title("🔥 Naruto: Chakra Typing Defense 🔥")
        self.root.resizable(False, False)

        # --- Game Constants ---
        self.width = 800
        self.height = 500
        self.player_x_limit = 80 # New: Player defense line

        # Word Bank: Categorized for thematic flair
        self.word_bank = {
            "NINJA": ["NARUTO", "SASUKE", "SAKURA", "KAKASHI", "HOKAGE", "GENIN", "CHUNIN", "JONIN", "SHINOBI", "VILLAGE"],
            "JUTSU": ["RASENGAN", "CHIDORI", "FIREBALL", "SHADOW", "CLONE", "SEAL", "TSUKUYOMI", "SUSANOO"],
            "WEAPON": ["KUNAI", "SHURIKEN", "KATANA", "EXPLOSIVE"],
            "KEKKEI": ["SHARINGAN", "BYAKUGAN", "RINNEGAN", "SENJU", "UCHIHA", "UZUMAKI"],
            "AKATSUKI": ["ITACHI", "PAIN", "KISAME", "DEIDARA", "OBITO", "MADARA"]
        }
        self.all_words = sum(self.word_bank.values(), [])

        # Game State
        self.score = 0
        self.health = 100
        self.combo = 0 # New: Combo system
        self.game_running = False
        self.base_spawn_rate = 2000  # ms
        self.base_enemy_speed = 1.5 # Slower base speed
        self.current_spawn_rate = self.base_spawn_rate
        self.current_enemy_speed = self.base_enemy_speed
        
        # Enemy Management
        self.enemies = []
        self.current_target = None
        self.typed_index = 0
        self.last_key_time = 0 # For WPM-based difficulty

        # --- UI Setup ---
        # Changed background to a slightly more thematic color
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="#404040") 
        self.canvas.pack()

        # Player (Blue Chakra Field/Wall)
        self.player = self.canvas.create_rectangle(10, 0, self.player_x_limit, self.height, fill="blue", stipple="gray25", outline="cyan", width=3)
        self.canvas.create_text(45, self.height/2, text="DEFENSE\nLINE", fill="white", font=("Arial", 10, "bold"))

        # HUD Improvement: Added Combo/WPM
        self.score_text = self.canvas.create_text(100, 30, text="Score: 0", fill="white", font=("Arial", 14, "bold"))
        self.combo_text = self.canvas.create_text(self.width/2, 30, text="Combo: 0", fill="yellow", font=("Arial", 14, "bold"))
        self.health_text = self.canvas.create_text(700, 30, text="Health: 100%", fill="lime", font=("Arial", 14, "bold"))
        
        # Start Screen
        self.center_msg = self.canvas.create_text(self.width/2, self.height/2, 
                                                text="TYPE TO SURVIVE\nPress ENTER to Start\n\nWords: Ninja, Jutsu, Akatsuki", 
                                                fill="orange", font=("Arial", 24, "bold"), justify="center")

        # Input Binding: Changed to <Key> to catch all characters (including non-letters for future)
        self.root.bind("<Key>", self.handle_keypress)
        self.root.bind("<Return>", self.start_game)

    def start_game(self, event=None):
        if not self.game_running:
            self.game_running = True
            self.score = 0
            self.health = 100
            self.combo = 0
            self.current_spawn_rate = self.base_spawn_rate
            self.current_enemy_speed = self.base_enemy_speed
            self.current_target = None
            self.typed_index = 0
            
            # Clear old enemies
            for e in self.enemies:
                self.canvas.delete(e['id_body'])
                self.canvas.delete(e['id_text'])
            self.enemies.clear()

            # Reset HUD
            self.canvas.itemconfig(self.score_text, text="Score: 0")
            self.canvas.itemconfig(self.combo_text, text="Combo: 0", fill="yellow")
            self.canvas.itemconfig(self.health_text, text="Health: 100%", fill="lime")
            self.canvas.itemconfig(self.center_msg, text="")
            
            # Start game loops
            self.spawn_enemy()
            self.move_enemies()

    def spawn_enemy(self):
        if self.game_running:
            # Word choice: Get a word from the full list
            word = random.choice(self.all_words)
            y_pos = random.randint(70, self.height - 70) # Adjusted range to avoid HUD
            
            # Enemy Body: Made it look a bit more like a scroll/icon
            enemy_body = self.canvas.create_oval(self.width - 90, y_pos - 15, self.width - 40, y_pos + 15, 
                                                fill="red", outline="gold", width=2)
            enemy_text = self.canvas.create_text(self.width - 65, y_pos, text=word, fill="white", 
                                                 font=("Arial", 11, "bold"))
            
            # Enemy object
            enemy = {
                'word': word,
                'x': self.width - 65, # Center X for the text
                'y': y_pos,
                'id_body': enemy_body,
                'id_text': enemy_text,
                'typed': ""
            }
            self.enemies.append(enemy)
            
            # Schedule next spawn using the current dynamic rate
            self.root.after(int(self.current_spawn_rate), self.spawn_enemy)

    def move_enemies(self):
        if self.game_running:
            enemies_to_remove = []
            
            for enemy in self.enemies:
                # Move enemy left using the current dynamic speed
                dx = -self.current_enemy_speed
                self.canvas.move(enemy['id_body'], dx, 0)
                self.canvas.move(enemy['id_text'], dx, 0)
                enemy['x'] += dx
                
                # Check collision with player's defense line
                if enemy['x'] <= self.player_x_limit + 10: 
                    self.take_damage(15) # Increased damage for impact
                    enemies_to_remove.append(enemy)
            
            # Remove collided enemies
            for enemy in enemies_to_remove:
                self.remove_enemy(enemy)
            
            # Continue movement loop (50ms = 20 FPS)
            self.root.after(50, self.move_enemies)

    def handle_keypress(self, event):
        if not self.game_running or not event.char.isalpha():
            return
            
        key = event.char.upper()
        
        # Calculate time since last keypress for combo timeout
        current_time = time.time()
        time_elapsed = current_time - self.last_key_time
        self.last_key_time = current_time

        # Check for combo break (e.g., more than 1 second between keys)
        if self.current_target and time_elapsed > 1.0:
            self.combo = 0
            self.canvas.itemconfig(self.combo_text, text="Combo: 0", fill="yellow")

        # 1. Target Management: Find, Confirm, or Miss
        if not self.current_target:
            # 1a. Try to find a new target
            for enemy in self.enemies:
                if enemy['word'].startswith(key):
                    self.current_target = enemy
                    self.typed_index = 1
                    enemy['typed'] = key
                    self.update_enemy_display(enemy, is_target=True)
                    break
        else:
            # 1b. Continue typing the current target
            expected_char = self.current_target['word'][self.typed_index]
            if key == expected_char:
                self.typed_index += 1
                self.current_target['typed'] += key
                self.update_enemy_display(self.current_target, is_target=True)
                
                # Word complete!
                if self.typed_index == len(self.current_target['word']):
                    self.destroy_enemy(self.current_target)
                    self.current_target = None
                    self.typed_index = 0
            else:
                # 1c. Wrong key - combo break and reset target word progress
                self.take_damage(5) # Minor penalty for mistyping
                self.combo = 0 # Break combo
                self.canvas.itemconfig(self.combo_text, text="Combo: 0", fill="yellow")
                self.reset_target(self.current_target) # Reset current word's typed progress
                self.current_target = None
                self.typed_index = 0

    def update_enemy_display(self, enemy, is_target=False):
        # Improved: Use TKinter tags for colored segments (more complex but better visual)
        
        self.canvas.delete(enemy['id_text']) # Delete old text object
        
        typed_part = enemy['typed']
        untyped_part = enemy['word'][len(typed_part):]
        
        x, y = self.canvas.coords(enemy['id_body'])[0] + 25, self.canvas.coords(enemy['id_body'])[1] + 15

        # Create new text object with two color segments
        # Typed part (green for progress, red if wrong in the original code but kept yellow for target)
        typed_color = "lime" if is_target else "white" 
        
        text_id = self.canvas.create_text(x, y, text=enemy['word'], 
                                           fill=typed_color if not is_target else "yellow", 
                                           font=("Arial", 11, "bold"), anchor='center')
        
        # This part is simplified for tk.Canvas which doesn't natively support easy text segment coloring.
        # A more advanced GUI library would be needed for true segment coloring, so we stick to the simpler
        # text update but change the color/fill of the enemy icon.
        
        if is_target:
            self.canvas.itemconfig(enemy['id_body'], fill="orange", outline="yellow")
        else:
            self.canvas.itemconfig(enemy['id_body'], fill="red", outline="gold")

        enemy['id_text'] = text_id # Update the reference

    def destroy_enemy(self, enemy):
        # 1. Update Score & Combo
        self.combo += 1
        points = 10 + self.combo * 2 # Combo points!
        self.score += points
        
        combo_color = "red" if self.combo >= 10 else "orange" if self.combo >= 5 else "yellow"
        self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")
        self.canvas.itemconfig(self.combo_text, text=f"Combo: {self.combo} (+{points})", fill=combo_color)
        
        # 2. Remove Enemy
        self.remove_enemy(enemy)
        
        # 3. Dynamic Difficulty Scaling
        self.update_difficulty()

    def update_difficulty(self):
        # Difficulty scales faster with higher score
        
        # 1. Spawn Rate (Min 500ms)
        difficulty_factor_rate = self.score // 50 * 50 # Every 50 points
        new_rate = self.base_spawn_rate - difficulty_factor_rate * 50
        self.current_spawn_rate = max(500, new_rate) 

        # 2. Speed (Max 6.0)
        difficulty_factor_speed = self.score // 100 * 100 # Every 100 points
        new_speed = self.base_enemy_speed + difficulty_factor_speed * 0.05
        self.current_enemy_speed = min(6.0, new_speed)
        
        # Visual feedback on difficulty (e.g. Health bar border flash)
        if self.score % 100 == 0 and self.score > 0:
             print(f"Difficulty increased! Speed: {self.current_enemy_speed:.1f}, Rate: {self.current_spawn_rate}ms")


    def remove_enemy(self, enemy):
        if enemy in self.enemies:
            self.canvas.delete(enemy['id_body'])
            self.canvas.delete(enemy['id_text'])
            self.enemies.remove(enemy)
            if enemy == self.current_target:
                self.current_target = None
                self.typed_index = 0

    def reset_target(self, enemy):
        # Only resets the visual back to untargeted, but keeps the word
        enemy['typed'] = ""
        self.update_enemy_display(enemy, is_target=False)

    def take_damage(self, damage):
        self.health -= damage
        self.health = max(0, self.health)
        self.combo = 0 # Damage breaks combo
        self.canvas.itemconfig(self.combo_text, text="Combo: 0", fill="yellow")

        # Update health display
        health_color = "lime" if self.health > 60 else "yellow" if self.health > 30 else "red"
        self.canvas.itemconfig(self.health_text, text=f"Health: {self.health}%", fill=health_color)
        
        # Visual Damage Effect (Red flash on defense line)
        original_fill = self.canvas.itemcget(self.player, "fill")
        self.canvas.itemconfig(self.player, fill="red")
        self.root.after(100, lambda: self.canvas.itemconfig(self.player, fill=original_fill))

        # Check game over
        if self.health <= 0:
            self.game_over()

    def game_over(self):
        self.game_running = False
        self.canvas.itemconfig(self.center_msg, text=f"GAME OVER\nFinal Score: {self.score}\nPress ENTER to Restart", 
                               fill="red", font=("Arial", 24, "bold"), justify="center")
        print(f"FINAL_SCORE:{self.score}")  # Print score for launcher to capture
        self.root.after(3000, self.root.quit)

def main():
    root = tk.Tk()
    game = ChakraTypingGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()