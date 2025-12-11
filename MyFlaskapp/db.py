
import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """Establishes a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        if conn.is_connected():
            cursor = conn.cursor()
            cursor.execute("CREATE DATABASE IF NOT EXISTS gemao_db")
            cursor.execute("USE gemao_db")
            print("Connected to database: gemao_db")
            return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def create_user_table():
    """Creates the user_tb table in the database."""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_tb (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id VARCHAR(50) UNIQUE,
                    firstname VARCHAR(100),
                    lastname VARCHAR(100),
                    username VARCHAR(100) UNIQUE,
                    password VARCHAR(255),
                    user_type ENUM('user', 'admin'),
                    birthdate DATE,
                    address VARCHAR(255),
                    mobile_number VARCHAR(20),
                    email VARCHAR(100)
                )
            """)
            conn.commit()
            print("Table 'user_tb' created successfully.")

            # Insert default users if they don't exist
            # Delete existing admin user to update with new details
            cursor.execute("DELETE FROM user_tb WHERE username = 'admin'")
            
            # Insert the new admin user with specified details
            cursor.execute("INSERT INTO user_tb (id, user_id, firstname, lastname, username, password, user_type, birthdate, address, mobile_number, email) VALUES (NULL, '573', 'carlo', 'arguilles', 'admin', 'admin_password', 'admin', '2008-06-26', 'mhv', '09634628387', 'nevop74006@gmail.com')")
            
            # Delete existing user to update with new details
            cursor.execute("DELETE FROM user_tb WHERE username = 'user'")
            
            # Insert the new user with specified details
            cursor.execute("INSERT INTO user_tb (id, user_id, firstname, lastname, username, password, user_type, birthdate, address, mobile_number, email) VALUES (NULL, '221', 'john', 'rey ', 'user', 'user_password', 'user', '2003-06-12', '123 Main St, Anytown, USA', '094563421', 'j23245164@gmail.com')")
            conn.commit()
            print("Default users 'admin' and 'user' ensured.")
        except Error as e:
            print(f"Error creating table: {e}")
        finally:
            if conn.is_connected():
                conn.close()

if __name__ == '__main__':
    create_user_table()
