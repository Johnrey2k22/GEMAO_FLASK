-- GEMAO Database Schema
-- Run this in phpMyAdmin or MySQL command line

CREATE DATABASE IF NOT EXISTS gemao_db;
USE gemao_db;

-- Users table
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
    profile_image VARCHAR(255),
    personal_intro TEXT,
    dream_it_job VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE
);

-- Games table
CREATE TABLE IF NOT EXISTS games_tb (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    file_path VARCHAR(255),
    max_score INT DEFAULT NULL
);

-- Scores table
CREATE TABLE IF NOT EXISTS scores_tb (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50),
    game_id INT,
    score INT,
    date_played DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_id) REFERENCES games_tb(id)
);

-- User Game Access table
CREATE TABLE IF NOT EXISTS user_game_access_tb (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50),
    game_id INT,
    is_enabled BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES user_tb(user_id) ON DELETE CASCADE,
    FOREIGN KEY (game_id) REFERENCES games_tb(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_game (user_id, game_id)
);

-- Insert default users
INSERT INTO user_tb (user_id, firstname, lastname, username, password, user_type, birthdate, address, mobile_number, email) VALUES
('001', 'admin', 'user', 'admin', 'admin_password', 'admin', '1990-01-01', 'Admin Address', '0000000000', 'admin@example.com'),
('573', 'carlo', 'arguilles', '', '_password', '', '2008-06-26', 'mhv', '09634628387', 'nevop74006@gmail.com'),
('221', 'john', 'rey', 'user', 'user_password', 'user', '2003-06-12', '123 Main St, Anytown, USA', '094563421', 'j23245164@gmail.com');

-- Insert default games
INSERT INTO games_tb (name, description, file_path) VALUES
('Naruto Run', 'Run as Naruto avoiding obstacles.', 'games/naruto_run.py'),
('Chakra Collector', 'Collect chakra orbs in the forest.', 'games/chakra_collector.py'),
('Jutsu Battle', 'Battle with jutsus against enemies.', 'games/jutsu_battle.py'),
('Ramen Eater', 'Eat as much ramen as possible.', 'games/ramen_eater.py'),
('Ninja Maze', 'Navigate through a maze as a ninja.', 'games/ninja_maze.py'),
('Sharingan Puzzle', 'Solve puzzles with Sharingan powers.', 'games/sharingan_puzzle.py'),
('Sage Mode Training', 'Train to achieve Sage Mode.', 'games/sage_mode_training.py'),
('Akatsuki Hunt', 'Hunt down Akatsuki members.', 'games/akatsuki_hunt.py'),
('Village Defense', 'Defend the village from invaders.', 'games/village_defense.py'),
('Bijuu Capture', 'Capture and control Bijuu.', 'games/bijuu_capture.py');