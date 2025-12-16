import mysql.connector
from mysql.connector import Error

def setup_database():
    """Create database and tables with updated schema including email UNIQUE constraint"""
    try:
        # Connect to MySQL without specifying database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',  # Update with your MySQL password
        )

        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database
            cursor.execute("CREATE DATABASE IF NOT EXISTS gemao_db")
            cursor.execute("USE gemao_db")
            print("Database 'gemao_db' created/selected successfully!")
            
            # Drop existing table to recreate with updated schema
            cursor.execute("DROP TABLE IF EXISTS user_tb")
            print("Existing user_tb table dropped for recreation with updated schema!")
            
            # Create user_tb table with updated schema
            create_user_table = """
            CREATE TABLE user_tb (
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
                email VARCHAR(100) UNIQUE,
                profile_image VARCHAR(255),
                personal_intro TEXT,
                dream_it_job VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE
            )
            """
            cursor.execute(create_user_table)
            print("user_tb table created with email UNIQUE constraint!")
            
            # Create OTP verification table
            create_otp_table = """
            CREATE TABLE IF NOT EXISTS otp_verification (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(100),
                otp VARCHAR(6),
                expires_at DATETIME,
                verified BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_email_otp (email)
            )
            """
            cursor.execute(create_otp_table)
            print("otp_verification table created!")
            
            # Insert default admin user
            cursor.execute("""
                INSERT INTO user_tb (user_id, firstname, lastname, username, password, user_type, email) 
                VALUES ('001', 'admin', 'user', 'admin', 'admin_password', 'admin', 'admin@example.com')
            """)
            print("Default admin user inserted!")
            
            connection.commit()
            
            # Verify constraints
            cursor.execute("""
                SELECT CONSTRAINT_NAME 
                FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
                WHERE TABLE_SCHEMA = 'gemao_db' 
                AND TABLE_NAME = 'user_tb' 
                AND CONSTRAINT_TYPE = 'UNIQUE'
            """)
            constraints = [row[0] for row in cursor.fetchall()]
            print(f"UNIQUE constraints on user_tb: {constraints}")
            
            return True

    except Error as e:
        print(f"Error setting up database: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    setup_database()
