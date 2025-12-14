
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash
from flask import current_app

def get_db_connection():
    """Establishes a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(
            host=current_app.config.get('DB_HOST', 'localhost'),
            user=current_app.config.get('DB_USER', 'root'),
            password=current_app.config.get('DB_PASSWORD', ''),
            database=current_app.config.get('DB_NAME', 'gemao_db')
        )
        if conn.is_connected():
            print("Connected to database: gemao_db")
            return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def create_tables():
    """Creates the necessary tables in the database."""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_tb (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id VARCHAR(50) UNIQUE,
                    firstname VARCHAR(100),
                    lastname VARCHAR(100),
                    username VARCHAR(100) UNIQUE,
                    password VARCHAR(255),
                    user_type VARCHAR(20),
                    birthdate DATE,
                    address VARCHAR(255),
                    mobile_number VARCHAR(20),
                    email VARCHAR(100),
                    is_active BOOLEAN DEFAULT TRUE,
                    profile_image VARCHAR(255),
                    personal_intro TEXT,
                    dream_it_job VARCHAR(255)
                )
            """)
            # Games table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS games_tb (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100),
                    description TEXT,
                    file_path VARCHAR(255),
                    max_score INT DEFAULT NULL
                )
            """)
            # Game access table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS game_access (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    game_id INT,
                    is_enabled BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES user_tb(id) ON DELETE CASCADE,
                    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_user_game (user_id, game_id)
                )
            """)
            # Scores table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scores_tb (
                    leaderboard_id INT AUTO_INCREMENT PRIMARY KEY,
                    game_id INT,
                    user_id INT,
                    score INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_tb(id),
                    FOREIGN KEY (game_id) REFERENCES games_tb(id),
                    INDEX idx_game_score (game_id, score)
                )
            """)
            # Tournaments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tournaments_tb (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100),
                    game_id INT,
                    creator_id INT,
                    status ENUM('open', 'ongoing', 'completed') DEFAULT 'open',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (game_id) REFERENCES games_tb(id),
                    FOREIGN KEY (creator_id) REFERENCES user_tb(id)
                )
            """)
            # Tournament participants
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tournament_participants_tb (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    tournament_id INT,
                    user_id INT,
                    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tournament_id) REFERENCES tournaments_tb(id),
                    FOREIGN KEY (user_id) REFERENCES user_tb(id)
                )
            """)
            # Matches table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS matches_tb (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    tournament_id INT,
                    round_num INT,
                    player1_id INT,
                    player2_id INT,
                    winner_id INT,
                    score1 INT,
                    score2 INT,
                    status ENUM('pending', 'completed') DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tournament_id) REFERENCES tournaments_tb(id),
                    FOREIGN KEY (player1_id) REFERENCES user_tb(id),
                    FOREIGN KEY (player2_id) REFERENCES user_tb(id),
                    FOREIGN KEY (winner_id) REFERENCES user_tb(id)
                )
            """)
            # OTP Verification table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS otp_verification (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(100) UNIQUE,
                    otp VARCHAR(6),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NULL DEFAULT NULL,
                    verified BOOLEAN DEFAULT FALSE
                )
            """)
            conn.commit()
            print("Tables created successfully.")

            # Insert default users
            cursor.execute("DELETE FROM user_tb WHERE username IN ('', 'user', 'admin')")
            
            # Insert users
            users_data = [
                ('221', 'john', 'rey', 'user', generate_password_hash('user_password'), 'user', '2003-06-12', '123 Main St, Anytown, USA', '094563421', 'j23245164@gmail.com', None, '', ''),
                ('001', 'admin', 'user', 'admin', generate_password_hash('admin_password'), 'admin', '1990-01-01', 'Admin Address', '0000000000', 'admin@example.com', None, '', '')
            ]
            for user_data in users_data:
                cursor.execute("INSERT INTO user_tb (user_id, firstname, lastname, username, password, user_type, birthdate, address, mobile_number, email, profile_image, personal_intro, dream_it_job) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", user_data)
            
            # Insert default games
            cursor.execute("DELETE FROM games_tb")
            games = [
                ('Naruto Run', 'Run as Naruto avoiding obstacles.', 'games/naruto_run.py'),
                ('Chakra Collector', 'Collect chakra orbs in the forest.', 'games/chakra_collector.py'),
                ('Jutsu Battle', 'Battle with jutsus against enemies.', 'games/jutsu_battle.py'),
                ('Ramen Eater', 'Eat as much ramen as possible.', 'games/ramen_eater.py'),
                ('Ninja Maze', 'Navigate through a maze as a ninja.', 'games/ninja_maze.py'),
                ('Sharingan Puzzle', 'Solve puzzles with Sharingan powers.', 'games/sharingan_puzzle.py'),
                ('Sage Mode Training', 'Train to achieve Sage Mode.', 'games/sage_mode_training.py'),
                ('Akatsuki Hunt', 'Hunt down Akatsuki members.', 'games/akatsuki_hunt.py'),
                ('Village Defense', 'Defend the village from invaders.', 'games/village_defense.py'),
                ('Bijuu Capture', 'Capture and control Bijuu.', 'games/bijuu_capture.py')
            ]
            for name, desc, path in games:
                cursor.execute("INSERT INTO games_tb (name, description, file_path) VALUES (%s, %s, %s)", (name, desc, path))
            
            # Insert default user game access
            cursor.execute("INSERT IGNORE INTO game_access (user_id, game_id, is_enabled) SELECT u.id, g.id, TRUE FROM user_tb u CROSS JOIN games_tb g")
            
            conn.commit()
            print("Default data inserted.")
        except Error as e:
            print(f"Error creating tables: {e}")
        finally:
            if conn.is_connected():
                conn.close()

if __name__ == '__main__':
    create_tables()

def get_top_scores_for_game(game_id, limit=10):
    conn = get_db_connection()
    scores = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT l.score, u.username, l.created_at as date_played
            FROM scores_tb l
            JOIN user_tb u ON l.user_id = u.id
            WHERE l.game_id = %s
            ORDER BY l.score DESC
            LIMIT %s
        """, (game_id, limit))
        scores = cursor.fetchall()
        conn.close()
    return scores

def get_all_scores_for_game(game_id):
    conn = get_db_connection()
    scores = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT l.leaderboard_id, l.score, u.username, l.created_at as date_played
            FROM scores_tb l
            JOIN user_tb u ON l.user_id = u.id
            WHERE l.game_id = %s
            ORDER BY l.score DESC
        """, (game_id,))
        scores = cursor.fetchall()
        conn.close()
    return scores

def submit_score(user_id, game_id, score):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        # Get the user id (INT) from user_id (VARCHAR)
        cursor.execute("SELECT id FROM user_tb WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return False
            
        user_db_id = user['id']
        
        cursor.execute("SELECT max_score FROM games_tb WHERE id = %s", (game_id,))
        game = cursor.fetchone()
        if game and game['max_score'] and score > game['max_score']:
            score = game['max_score']
        # Insert score using the database id
        cursor.execute("INSERT INTO scores_tb (user_id, game_id, score) VALUES (%s, %s, %s)", (user_db_id, game_id, score))
        conn.commit()
        conn.close()
        return True
    return False

def delete_scores_for_game(game_id):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM scores_tb WHERE game_id = %s", (game_id,))
        conn.commit()
        conn.close()
        return True
    return False
