import pymysql
from config import web_config

def create_database():
    """Initialize MySQL database for the web application"""
    try:
        connection = pymysql.connect(
            host=web_config["db_host"],
            user=web_config["db_user"],
            password=web_config["db_pass"]
        )
        cursor = connection.cursor()
        
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {web_config['db_name']}")
        cursor.execute(f"USE {web_config['db_name']}")
        
        # Create user table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                first_login BOOLEAN DEFAULT TRUE
            )
        """)
        
        # Insert default admin user (hashed password)
        import bcrypt
        hashed_password = bcrypt.hashpw(web_config["admin_pass"].encode(), bcrypt.gensalt()).decode()
        cursor.execute("INSERT IGNORE INTO users (username, password_hash) VALUES (%s, %s)",
                       (web_config["admin_user"], hashed_password))
        
        connection.commit()
        print("[INFO] Database setup completed!")
    
    except pymysql.MySQLError as e:
        print(f"[ERROR] Database error: {e}")
    
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    create_database()
