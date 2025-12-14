#!/usr/bin/env python3
"""
Sync Games Database Script
Updates the database with actual game files from the games directory.
"""

import os
import sys
import re
import mysql.connector
from mysql.connector import Error

# Add the MyFlaskapp directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'MyFlaskapp'))

def extract_game_metadata(filepath):
    """Extract metadata from a game file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        filename = os.path.basename(filepath)
        
        # Extract game title from various patterns
        title_patterns = [
            r'root\.title\(["\']([^"\']+)["\']\)',
            r'super\(\).__init__\([^)]*title=["\']([^"\']+)["\']',
            r'title=["\']([^"\']+)["\']',
        ]
        
        title = None
        for pattern in title_patterns:
            match = re.search(pattern, content)
            if match:
                title = match.group(1).strip()
                break
        
        # If no title found, use filename
        if not title:
            title = filename.replace('.py', '').replace('_', ' ').title()
        
        # Set default description
        description = f'Experience the ninja world in {title}.'
        
        return {
            'name': title,
            'description': description,
            'file_path': f'games/{filename}',  # Relative path for launcher
        }
        
    except Exception as e:
        print(f"Error extracting metadata from {filepath}: {e}")
        return None


def get_database_connection():
    """Get database connection."""
    try:
        # Update these credentials according to your database setup
        connection = mysql.connector.connect(
            host='localhost',
            database='gemao_db',
            user='root',
            password=''
        )
        return connection
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

def sync_games_database():
    """Sync the games database with the games directory."""
    games_dir = os.path.join(os.path.dirname(__file__), 'MyFlaskapp', 'games')
    
    # List of game files to exclude (utility files, etc.)
    exclude_files = {'__init__.py', 'game_launcher.py', 'game_base.py', 'routes.py'}
    
    # Get all game files from directory
    game_files = []
    for filename in os.listdir(games_dir):
        if filename.endswith('.py') and filename not in exclude_files:
            filepath = os.path.join(games_dir, filename)
            game_info = extract_game_metadata(filepath)
            if game_info:
                game_files.append(game_info)
    
    # Connect to database
    conn = get_database_connection()
    if not conn:
        print("Failed to connect to database")
        return
    
    try:
        cursor = conn.cursor()
        
        # Get existing games from database
        cursor.execute("SELECT id, file_path FROM games")
        existing_games = {row[1]: row[0] for row in cursor.fetchall()}
        
        # Update or insert games
        for game in game_files:
            file_path = game['file_path']
            if file_path in existing_games:
                # Update existing game
                game_id = existing_games[file_path]
                cursor.execute("""
                    UPDATE games 
                    SET name = %s, description = %s 
                    WHERE id = %s
                """, (game['name'], game['description'], game_id))
                print(f"Updated: {game['name']}")
            else:
                # Insert new game
                cursor.execute("""
                    INSERT INTO games (name, description, file_path) 
                    VALUES (%s, %s, %s)
                """, (game['name'], game['description'], file_path))
                print(f"Added: {game['name']}")
        
        # Remove games that no longer exist in directory
        existing_paths = {game['file_path'] for game in game_files}
        for db_path, game_id in existing_games.items():
            if db_path not in existing_paths:
                cursor.execute("DELETE FROM games WHERE id = %s", (game_id,))
                print(f"Removed: {db_path}")
        
        conn.commit()
        print(f"Database synced successfully! Processed {len(game_files)} games.")
        
    except Error as e:
        print(f"Error syncing database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    sync_games_database()
