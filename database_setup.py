import pymysql
from pymysql.err import OperationalError

DB_NAME = "scanner_db"
DB_USER = "root"
DB_PASSWORD = "password"
DB_HOST = "localhost"

def create_database():
    """Create MySQL database and tables."""
    try:
        conn = pymysql.connect(host=DB_HOST, user="root", password="")
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.execute(f"CREATE USER IF NOT EXISTS '{DB_USER}'@'localhost' IDENTIFIED BY '{DB_PASSWORD}'")
        cursor.execute(f"GRANT ALL PRIVILEGES ON {DB_NAME}.* TO '{DB_USER}'@'localhost'")
        conn.commit()
        conn.close()
        print("[INFO] Database setup completed!")
    except OperationalError as e:
        print(f"[ERROR] Database error: {e}")

if __name__ == "__main__":
    create_database()
