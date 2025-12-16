import mysql.connector
from mysql.connector import Error

def create_missing_table():
    """Create the user_scanned_game_access_tb table"""
    try:
        # Connect to MySQL database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',  # Update with your MySQL password
            database='gemao_db'
        )

        if connection.is_connected():
            cursor = connection.cursor()
            
            # SQL to create the table
            create_table_query = """
            CREATE TABLE IF NOT EXISTS user_scanned_game_access_tb (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id VARCHAR(50),
                game_filename VARCHAR(255),
                is_enabled BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_tb(user_id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_scanned_game (user_id, game_filename)
            );
            """
            
            cursor.execute(create_table_query)
            connection.commit()
            print("Table 'user_scanned_game_access_tb' created successfully!")
            
            # Verify table exists
            cursor.execute("SHOW TABLES LIKE 'user_scanned_game_access_tb'")
            result = cursor.fetchone()
            if result:
                print("Table verification: EXISTS")
            else:
                print("Table verification: NOT FOUND")

    except Error as e:
        print(f"Error creating table: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    create_missing_table()
