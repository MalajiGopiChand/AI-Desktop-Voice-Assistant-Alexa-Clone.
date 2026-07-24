"""
Database Management Module.
Supports MySQL (localhost:3306) with seamless SQLite fallback.
Includes Error Logging table (ErrorLogs) for real-time error auditing.
"""
import sqlite3
import os
import datetime
from config import DATABASE_PATH

# MySQL Configs
MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
MYSQL_DB = os.environ.get("MYSQL_DB", "jarvis_db")


def get_mysql_connection():
    try:
        import pymysql
        conn = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            autocommit=True
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB}")
        conn.select_db(MYSQL_DB)
        return conn
    except Exception:
        return None


def get_connection():
    # Attempt MySQL first if available
    mysql_conn = get_mysql_connection()
    if mysql_conn:
        return mysql_conn, "mysql"

    # SQLite Fallback
    db_dir = os.path.dirname(DATABASE_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    return sqlite3.connect(DATABASE_PATH), "sqlite"


def create_tables():
    conn, db_type = get_connection()
    cursor = conn.cursor()

    if db_type == "mysql":
        cursor.execute('''CREATE TABLE IF NOT EXISTS Users (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255) UNIQUE, created_at DATETIME)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Settings (id INT AUTO_INCREMENT PRIMARY KEY, setting_key VARCHAR(255) UNIQUE, setting_value TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS History (id INT AUTO_INCREMENT PRIMARY KEY, command TEXT, status TEXT, timestamp DATETIME)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS CustomCommands (id INT AUTO_INCREMENT PRIMARY KEY, trigger_phrase VARCHAR(255) UNIQUE, action_type VARCHAR(50), action_value TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS ErrorLogs (id INT AUTO_INCREMENT PRIMARY KEY, module VARCHAR(255), error_message TEXT, traceback TEXT, timestamp DATETIME)''')
    else:
        cursor.execute('''CREATE TABLE IF NOT EXISTS Users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, created_at TIMESTAMP)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS Settings (id INTEGER PRIMARY KEY AUTOINCREMENT, setting_key TEXT UNIQUE, setting_value TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS History (id INTEGER PRIMARY KEY AUTOINCREMENT, command TEXT, status TEXT, timestamp TIMESTAMP)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS CustomCommands (id INTEGER PRIMARY KEY AUTOINCREMENT, trigger_phrase TEXT UNIQUE, action_type TEXT, action_value TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS ErrorLogs (id INTEGER PRIMARY KEY AUTOINCREMENT, module TEXT, error_message TEXT, traceback TEXT, timestamp TIMESTAMP)''')
        conn.commit()

    conn.close()


def log_error(module, error_message, traceback_info=None):
    try:
        conn, db_type = get_connection()
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if db_type == "mysql":
            query = "INSERT INTO ErrorLogs (module, error_message, traceback, timestamp) VALUES (%s, %s, %s, %s)"
        else:
            query = "INSERT INTO ErrorLogs (module, error_message, traceback, timestamp) VALUES (?, ?, ?, ?)"
        cursor.execute(query, (str(module), str(error_message), str(traceback_info or ""), timestamp))
        if db_type == "sqlite":
            conn.commit()
        conn.close()
        print(f"[ERROR LOGGED -> {db_type.upper()}] ({module}) {error_message}")
    except Exception as e:
        print(f"Failed to log error: {e}")


def save_history(command, status="Executed"):
    try:
        conn, db_type = get_connection()
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ph = "%s" if db_type == "mysql" else "?"
        cursor.execute(f"INSERT INTO History (command, status, timestamp) VALUES ({ph}, {ph}, {ph})", (command, status, timestamp))
        if db_type == "sqlite":
            conn.commit()
        conn.close()
    except Exception as e:
        log_error("database.save_history", str(e))


def get_history(limit=50):
    try:
        conn, db_type = get_connection()
        cursor = conn.cursor()
        ph = "%s" if db_type == "mysql" else "?"
        cursor.execute(f"SELECT command, status, timestamp FROM History ORDER BY id DESC LIMIT {ph}", (limit,))
        results = cursor.fetchall()
        conn.close()
        return [{"command": r[0], "status": r[1], "timestamp": str(r[2])} for r in results]
    except Exception as e:
        log_error("database.get_history", str(e))
        return []


def add_custom_command(trigger, action_type, action_value):
    try:
        conn, db_type = get_connection()
        cursor = conn.cursor()
        if db_type == "mysql":
            query = "INSERT INTO CustomCommands (trigger_phrase, action_type, action_value) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE action_type=%s, action_value=%s"
            cursor.execute(query, (trigger.lower(), action_type, action_value, action_type, action_value))
        else:
            query = "INSERT OR REPLACE INTO CustomCommands (trigger_phrase, action_type, action_value) VALUES (?, ?, ?)"
            cursor.execute(query, (trigger.lower(), action_type, action_value))
            conn.commit()
        conn.close()
        return True
    except Exception as e:
        log_error("database.add_custom_command", str(e))
        return False


def get_custom_commands():
    try:
        conn, db_type = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT trigger_phrase, action_type, action_value FROM CustomCommands")
        results = cursor.fetchall()
        conn.close()
        return {r[0]: {"type": r[1], "value": r[2]} for r in results}
    except Exception as e:
        log_error("database.get_custom_commands", str(e))
        return {}


def get_setting(key, default=None):
    try:
        conn, db_type = get_connection()
        cursor = conn.cursor()
        ph = "%s" if db_type == "mysql" else "?"
        cursor.execute(f"SELECT setting_value FROM Settings WHERE setting_key = {ph}", (key,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else default
    except Exception as e:
        return default


def set_setting(key, value):
    try:
        conn, db_type = get_connection()
        cursor = conn.cursor()
        if db_type == "mysql":
            query = "INSERT INTO Settings (setting_key, setting_value) VALUES (%s, %s) ON DUPLICATE KEY UPDATE setting_value=%s"
            cursor.execute(query, (key, str(value), str(value)))
        else:
            query = "INSERT OR REPLACE INTO Settings (setting_key, setting_value) VALUES (?, ?)"
            cursor.execute(query, (key, str(value)))
            conn.commit()
        conn.close()
        return True
    except Exception as e:
        log_error("database.set_setting", str(e))
        return False


def fetch_recent_errors(limit=5):
    try:
        conn, db_type = get_connection()
        cursor = conn.cursor()
        ph = "%s" if db_type == "mysql" else "?"
        cursor.execute(f"SELECT module, error_message, timestamp FROM ErrorLogs ORDER BY id DESC LIMIT {ph}", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [{"source": r[0], "message": r[1], "timestamp": str(r[2])} for r in rows]
    except Exception:
        return []
