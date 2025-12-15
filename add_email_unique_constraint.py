import mysql.connector
from mysql.connector import Error

def add_email_unique_constraint():
    """Add UNIQUE constraint to email field in user_tb table"""
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
            
            # Check if constraint already exists
            cursor.execute("""
                SELECT CONSTRAINT_NAME 
                FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
                WHERE TABLE_SCHEMA = 'gemao_db' 
                AND TABLE_NAME = 'user_tb' 
                AND CONSTRAINT_TYPE = 'UNIQUE'
            """)
            existing_constraints = [row[0] for row in cursor.fetchall()]
            
            if 'email' in existing_constraints or 'user_tb_email_unique' in existing_constraints:
                print("Email UNIQUE constraint already exists!")
                return True
            
            # Add UNIQUE constraint to email field
            alter_query = "ALTER TABLE user_tb ADD CONSTRAINT user_tb_email_unique UNIQUE (email)"
            cursor.execute(alter_query)
            connection.commit()
            print("Email UNIQUE constraint added successfully!")
            
            # Verify constraint was added
            cursor.execute("""
                SELECT CONSTRAINT_NAME 
                FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS 
                WHERE TABLE_SCHEMA = 'gemao_db' 
                AND TABLE_NAME = 'user_tb' 
                AND CONSTRAINT_TYPE = 'UNIQUE'
            """)
            updated_constraints = [row[0] for row in cursor.fetchall()]
            
            if 'user_tb_email_unique' in updated_constraints:
                print("Constraint verification: SUCCESS")
                return True
            else:
                print("Constraint verification: FAILED")
                return False

    except Error as e:
        print(f"Error adding constraint: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    add_email_unique_constraint()
