"""
Database Management Module.
This file handles connecting to the SQLite database and saving data.
We use it to store a history of all commands given to the assistant.
"""

import sqlite3
import os
import datetime
from config import DATABASE_PATH

def get_connection():
    """
    Creates and returns a connection to the SQLite database.
    If the database file doesn't exist, SQLite will create it automatically.
    """
    # Ensure the database directory exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    return sqlite3.connect(DATABASE_PATH)

def create_tables():
    """
    Creates the necessary tables in the database if they don't already exist.
    We need tables for Users, History, and Settings.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            created_at TIMESTAMP
        )
    ''')

    # Create Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            setting_key TEXT UNIQUE,
            setting_value TEXT
        )
    ''')

    # Create History table to track all commands
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS History (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command TEXT,
            status TEXT,
            timestamp TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

def save_history(command, status="Executed"):
    """
    Saves a given command and its execution status to the History table.
    
    Args:
        command (str): The command spoken by the user.
        status (str): The result of the command (e.g., 'Executed', 'Failed').
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO History (command, status, timestamp) VALUES (?, ?, ?)",
            (command, status, timestamp)
        )
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving history to database: {e}")

def get_history(limit=10):
    """
    Retrieves the most recent history entries.
    
    Args:
        limit (int): Number of history items to return.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT command, status, timestamp FROM History ORDER BY id DESC LIMIT ?", (limit,))
    results = cursor.fetchall()
    conn.close()
    return results
