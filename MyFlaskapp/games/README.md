# Games Directory

This directory contains all the Naruto-themed mini-games for the NinjaVerse Flask application.

## Available Games

### 1. Shuriken Target Practice
- **File**: `shuriken_game.py`
- **Description**: Practice throwing shurikens at moving targets as Naruto
- **Controls**: 
  - Left/Right Arrow Keys: Move Naruto
  - Spacebar: Shoot shuriken
  - R: Restart (when game over)
  - ESC: Quit game
- **Objective**: Hit moving log targets with shurikens before they reach the opposite side
- **Scoring**: 10 points per successful hit

### 2. Roof Run
- **File**: `roof_run_game.py`
- **Description**: Endless runner where Naruto runs across rooftops avoiding obstacles
- **Controls**: 
  - Spacebar: Jump/Start Game
  - R: Restart (when game over)
  - ESC: Quit game
- **Objective**: Run as far as possible while avoiding chimneys and flying kunai
- **Scoring**: 1 point per meter traveled

### 3. Hand Sign Memory
- **File**: `hand_sign_memory_game.py`
- **Description**: Test your memory by repeating Kakashi's ninja hand sign sequences
- **Controls**: 
  - Spacebar: Start Game
  - Mouse Click: Select hand signs (TIGER, SNAKE, DRAGON, BIRD)
  - R: Restart (when game over)
  - ESC: Quit game
- **Objective**: Memorize and repeat increasingly long sequences of ninja hand signs
- **Scoring**: 1 point per level completed

### 4. Ramen Shop
- **File**: `ramen_shop_game.py`
- **Description**: Run Ichiraku Ramen Shop by serving customers their exact orders quickly
- **Controls**: 
  - Mouse Click: Select ingredients and serve orders
  - OPEN SHOP: Start game
  - SERVE ORDER!: Submit completed ramen bowl
  - Trash/Reset: Clear current bowl
- **Objective**: Assemble ramen orders matching customer requests before time runs out
- **Scoring**: 10 points per successful order served

### 5. Other Games
The project includes several other Naruto-themed games. Refer to the database schema for the complete list.

## Game Structure

All games inherit from the `GameBase` class in `game_base.py`, which provides:
- Common Tkinter setup and window management
- Input handling system
- Game state management
- Score tracking
- Standard game loop structure

## Adding New Games

1. Create a new game file inheriting from `GameBase`
2. Implement the required `update()` and `draw()` methods
3. Add the game to the database using the `add_shuriken_game.sql` template
4. The game will be automatically available through the web interface

## Technical Notes

- Games use Tkinter for the GUI
- The `game_launcher.py` handles subprocess execution for web integration
- Scores are automatically captured and stored in the database
- All games follow the same input patterns for consistency