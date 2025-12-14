from abc import ABC, abstractmethod
from werkzeug.security import generate_password_hash, check_password_hash
from MyFlaskapp.db import get_db_connection
from datetime import datetime

class User(ABC):
    """
    Abstract base class for users.
    Demonstrates abstraction and encapsulation.
    """
    def __init__(self, user_id, firstname, lastname, username, password, user_type, birthdate, address, mobile_number, email):
        self.user_id = user_id
        self.firstname = firstname
        self.lastname = lastname
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.user_type = user_type
        self.birthdate = birthdate
        self.address = address
        self.mobile_number = mobile_number
        self.email = email
        self.is_active = True

    @abstractmethod
    def get_dashboard_url(self):
        """
        Abstract method to get dashboard URL based on user type.
        Polymorphism: Different user types have different dashboards.
        """
        pass

    def check_password(self, password):
        """Encapsulation: Password checking is internal."""
        return check_password_hash(self.password_hash, password)

    def save_to_db(self):
        """Save user to database."""
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_tb (user_id, firstname, lastname, username, password, user_type, birthdate, address, mobile_number, email, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (self.user_id, self.firstname, self.lastname, self.username, self.password_hash, self.user_type,
                  self.birthdate, self.address, self.mobile_number, self.email, self.is_active))
            conn.commit()
            conn.close()

    @staticmethod
    def get_by_username(username):
        """Factory method to get user from database."""
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM user_tb WHERE username = %s", (username,))
            user_data = cursor.fetchone()
            conn.close()
            if user_data:
                user_type = user_data['user_type']
                if user_type == 'admin':
                    return AdminUser(**user_data)
                else:
                    return RegularUser(**user_data)
        return None

class AdminUser(User):
    """
    Admin user class.
    Inheritance: Inherits from User.
    """
    def get_dashboard_url(self):
        return '/admin/dashboard'

class RegularUser(User):
    """
    Regular user class.
    Inheritance: Inherits from User.
    """
    def get_dashboard_url(self):
        return '/user/dashboard'

class Game:
    """
    Game data class.
    Encapsulation: Manages game data.
    """
    def __init__(self, name, description, file_path, max_score=None, id=None):
        self.id = id
        self.name = name
        self.description = description
        self.file_path = file_path
        self.max_score = max_score

    def save_to_db(self):
        """Save game to database."""
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO games (name, description, file_path, max_score)
                VALUES (%s, %s, %s, %s)
            """, (self.name, self.description, self.file_path, self.max_score))
            conn.commit()
            conn.close()

    @staticmethod
    def get_all():
        """Get all games from database."""
        conn = get_db_connection()
        games = []
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM games")
            game_data = cursor.fetchall()
            conn.close()
            for data in game_data:
                games.append(Game(**data))
        return games