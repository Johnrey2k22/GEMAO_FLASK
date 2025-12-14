#!/usr/bin/env python3
"""
Script to update the games database with all current game files
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from MyFlaskapp.db import get_db_connection

def update_games_database():
    """Update the games table with all current game files"""
    
    # Create app context
    from MyFlaskapp import create_app
    app = create_app()
    
    with app.app_context():
        # List of all current games with their descriptions
        games = [
            ('Chakra Typing Game', 'Test your typing speed while collecting chakra', 'games/chakra_typing_game.py'),
            ('Clash Game Enhanced', 'Enhanced clash battle game with special moves', 'games/clash_game_enhanced.py'),
            ('Hand Sign Memory Game', 'Memorize and repeat ninja hand signs', 'games/hand_sign_memory_game.py'),
            ('Ninja Cat Game', 'Guide the ninja cat through obstacles', 'games/ninja_cat_game.py'),
            ('Ramen Shop Game', 'Serve ramen to customers quickly', 'games/ramen_shop_game.py'),
            ('Roof Run Game', 'Run across rooftops avoiding obstacles', 'games/roof_run_game.py'),
            ('Shadow Clone Whack-a-Mole', 'Hit shadow clones as they appear', 'games/shadow_clone_whack_a_mole.py'),
            ('Sharingan Difference Game', 'Find differences using Sharingan eyes', 'games/sharingan_difference_game.py'),
            ('Shuriken Game', 'Throw shurikens at targets', 'games/shuriken_game.py'),
            ('Tree Climbing Game', 'Climb trees using chakra control', 'games/tree_climbing_game.py')
        ]
        
        conn = get_db_connection()
        if not conn:
            print("Failed to connect to database")
            return False
        
        try:
            cursor = conn.cursor()
            
            # Clear existing games
            cursor.execute("DELETE FROM games")
            conn.commit()
            
            # Insert all games
            insert_query = "INSERT INTO games (name, description, file_path) VALUES (%s, %s, %s)"
            
            for game_name, description, file_path in games:
                cursor.execute(insert_query, (game_name, description, file_path))
                print(f"Added game: {game_name}")
            
            conn.commit()
            print(f"Successfully added {len(games)} games to the database")
            return True
            
        except Exception as e:
            print(f"Error updating games database: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

if __name__ == "__main__":
    update_games_database()
