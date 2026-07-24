import sqlite3
import os
import json
from datetime import datetime
from config import MEMORY_DB_PATH

class MemorySystem:
    def __init__(self, db_path=None):
        self.db_path = db_path or MEMORY_DB_PATH
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self):
        # User Preferences and Settings
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # Long-Term Memory (Facts, Projects, Important info)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS long_term_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Short-Term / Context Memory (Recent conversations/tasks)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS short_term_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT,
                content TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    # --- Preferences ---
    def set_preference(self, key, value):
        self.cursor.execute("REPLACE INTO preferences (key, value) VALUES (?, ?)", (key, str(value)))
        self.conn.commit()

    def get_preference(self, key, default=None):
        self.cursor.execute("SELECT value FROM preferences WHERE key = ?", (key,))
        row = self.cursor.fetchone()
        return row[0] if row else default

    # --- Long-Term Memory ---
    def remember_fact(self, category, content):
        """Store long term facts like 'User name', 'Projects', etc."""
        # Never store passwords
        if "password" in content.lower() or "secret" in content.lower():
            return False
        
        self.cursor.execute("INSERT INTO long_term_memory (category, content) VALUES (?, ?)", (category, content))
        self.conn.commit()
        return True
        
    def recall_facts(self, category=None, limit=50):
        if category:
            self.cursor.execute(
                "SELECT content FROM long_term_memory WHERE category = ? ORDER BY timestamp DESC LIMIT ?",
                (category, limit),
            )
        else:
            self.cursor.execute(
                "SELECT content FROM long_term_memory ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            )
        return [row[0] for row in self.cursor.fetchall()]

    # --- Context / Short-Term Memory ---
    def add_context(self, role, content):
        """Add to conversation history."""
        self.cursor.execute("INSERT INTO short_term_memory (role, content) VALUES (?, ?)", (role, content))
        self.conn.commit()
        
    def get_context(self, limit=10):
        """Retrieve recent conversation history."""
        self.cursor.execute("SELECT role, content FROM short_term_memory ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = self.cursor.fetchall()
        # Return in chronological order
        return [{"role": r[0], "content": r[1]} for r in reversed(rows)]
        
    def clear_short_term_memory(self):
        self.cursor.execute("DELETE FROM short_term_memory")
        self.conn.commit()

# Singleton instance
memory = MemorySystem()
