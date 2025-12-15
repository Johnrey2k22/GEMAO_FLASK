import tkinter as tk
from abc import ABC, abstractmethod

class GameBase(ABC):
    """
    Abstract base class for all Naruto-themed mini-games using Tkinter.
    Demonstrates abstraction by defining the interface for games.
    """
    def __init__(self, screen_width=800, screen_height=600, title="Naruto Game"):
        """
        Initializes the game with common Tkinter setup.
        Encapsulation: Internal state and window management is within the class.
        """
        self.root = tk.Tk()
        self.root.title(title)
        self.root.resizable(False, False)
        
        # Center the window (optional polish)
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = (ws/2) - (screen_width/2)
        y = (hs/2) - (screen_height/2)
        self.root.geometry('%dx%d+%d+%d' % (screen_width, screen_height, x, y))

        # Canvas setup
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.canvas = tk.Canvas(self.root, width=self.screen_width, height=self.screen_height, bg="black")
        self.canvas.pack()

        # Game State
        self.running = True
        self.game_over = False
        self.score = 0
        
        # Input State (To allow smooth movement in subclasses)
        self.keys_pressed = set()
        
        # Bind Input Events
        self.root.bind("<KeyPress>", self._on_key_press)
        self.root.bind("<KeyRelease>", self._on_key_release)
        self.root.protocol("WM_DELETE_WINDOW", self.quit_game)

        # Common colors (Hex codes for Tkinter)
        self.WHITE = "#FFFFFF"
        self.BLACK = "#000000"
        self.RED = "#FF0000"
        self.GREEN = "#00FF00"
        self.BLUE = "#0000FF"
        
        # Font settings (Tuple format for Tkinter)
        self.font_style = ("Arial", 24)
        self.game_over_font_style = ("Arial", 48, "bold")

    @abstractmethod
    def update(self):
        """
        Abstract method for updating game logic.
        Polymorphism: Each game implements its own update logic.
        """
        pass
    
    @abstractmethod
    def draw(self):
        """
        Abstract method for drawing game elements.
        Polymorphism: Each game implements its own drawing.
        Note: In Tkinter, you typically use self.canvas.create_...
        """
        pass

    def _on_key_press(self, event):
        """Internal handler to track keys and handle global commands."""
        self.keys_pressed.add(event.keysym)
        
        # Handle Global Global Hotkeys
        if event.keysym == "Escape":
            self.quit_game()
        elif event.keysym.lower() == "r" and self.game_over:
            self.restart_game()
            
        # Hook for subclasses to handle single-press events (like shooting)
        self.handle_single_press(event.keysym)

    def _on_key_release(self, event):
        """Internal handler to stop tracking keys."""
        if event.keysym in self.keys_pressed:
            self.keys_pressed.remove(event.keysym)

    def handle_single_press(self, key):
        """
        Optional hook: Override this in subclasses if you need 
        to trigger actions exactly once per key press (e.g., firing a bullet).
        """
        pass
    
    def restart_game(self):
        """Restart the game - to be overridden by subclasses"""
        self.game_over = False
        self.score = 0
        # Subclasses should override this to reset their specific game state,
        # but they must call super().restart_game() or reset these flags themselves.
    
    def quit_game(self):
        """Safely close the window"""
        self.running = False
        self.root.destroy()

    def draw_game_over_screen(self):
        """Draw game over screen elements on the canvas"""
        # Draw "GAME OVER" text
        self.canvas.create_text(
            self.screen_width // 2, self.screen_height // 2 - 50,
            text="GAME OVER", fill=self.RED, font=self.game_over_font_style
        )
        
        # Draw final score
        self.canvas.create_text(
            self.screen_width // 2, self.screen_height // 2 + 20,
            text=f"Final Score: {self.score}", fill=self.WHITE, font=self.font_style
        )
        
        # Draw restart instruction
        self.canvas.create_text(
            self.screen_width // 2, self.screen_height // 2 + 80,
            text="Press R to Restart or ESC to Quit", fill=self.WHITE, font=("Arial", 16)
        )
    
    def run(self):
        """
        Main game loop using Tkinter's event loop.
        Returns the final score.
        """
        def game_loop():
            if not self.running:
                return

            if not self.game_over:
                # 1. Update Game Logic
                self.update()
                
                # 2. Draw Frame (only dynamic elements)
                # Note: Canvas is NOT cleared here to preserve static elements
                self.draw()

            else:
                # Game Over State
                self.canvas.delete("all")
                self.draw_game_over_screen()
                self.root.after(3000, self.root.quit)

            # Schedule next frame (approx 60 FPS -> 16ms)
            self.root.after(16, game_loop)

        # Start the loop and the main window
        game_loop()
        self.root.mainloop()
        
        return self.score