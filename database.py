"""
Database Management Module.
"""
import sqlite3
import os
import datetime
from config import DATABASE_PATH

def get_connection():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    return sqlite3.connect(DATABASE_PATH)

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, created_at TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS Settings (id INTEGER PRIMARY KEY AUTOINCREMENT, setting_key TEXT UNIQUE, setting_value TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS History (id INTEGER PRIMARY KEY AUTOINCREMENT, command TEXT, status TEXT, timestamp TIMESTAMP)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS CustomCommands (id INTEGER PRIMARY KEY AUTOINCREMENT, trigger_phrase TEXT UNIQUE, action_type TEXT, action_value TEXT)''')
    conn.commit()
    conn.close()

def save_history(command, status="Executed"):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO History (command, status, timestamp) VALUES (?, ?, ?)", (command, status, timestamp))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving history: {e}")

def get_history(limit=50):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT command, status, timestamp FROM History ORDER BY id DESC LIMIT ?", (limit,))
    results = cursor.fetchall()
    conn.close()
    return [{"command": r[0], "status": r[1], "timestamp": r[2]} for r in results]

def add_custom_command(trigger, action_type, action_value):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO CustomCommands (trigger_phrase, action_type, action_value) VALUES (?, ?, ?)", 
                       (trigger.lower(), action_type, action_value))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding custom command: {e}")
        return False

def get_custom_commands():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT trigger_phrase, action_type, action_value FROM CustomCommands")
    results = cursor.fetchall()
    conn.close()
    return {r[0]: {"type": r[1], "value": r[2]} for r in results}

def get_setting(key, default=None):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT setting_value FROM Settings WHERE setting_key = ?", (key,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else default
    except:
        return default

def set_setting(key, value):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO Settings (setting_key, setting_value) VALUES (?, ?)", (key, str(value)))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving setting: {e}")
        return False
