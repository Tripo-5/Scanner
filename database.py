import mysql.connector
from mysql.connector import Error

# Database connection settings
DB_CONFIG = {
    "host": "localhost",
    "user": "scanner_user",  # Ensure this is your MySQL username
    "password": "yourpassword",  # Ensure this matches the password set up in MySQL
    "database": "scanner_db"
}

def get_db_connection():
    """Establish a database connection"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"[ERROR] Database connection error: {e}")
        return None

# Global database object
db = get_db_connection()
