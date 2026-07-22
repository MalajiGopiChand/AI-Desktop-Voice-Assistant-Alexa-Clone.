"""Continuous improvement — track command usage and suggest shortcuts."""
from core.memory import memory


class LearningEngine:
    def __init__(self):
        self._ensure_table()

    def _ensure_table(self):
        memory.cursor.execute("""
            CREATE TABLE IF NOT EXISTS command_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command_pattern TEXT UNIQUE,
                use_count INTEGER DEFAULT 1,
                last_used DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        memory.conn.commit()

    def record(self, command):
        pattern = self._normalize(command)
        memory.cursor.execute(
            "SELECT use_count FROM command_usage WHERE command_pattern = ?", (pattern,)
        )
        row = memory.cursor.fetchone()
        if row:
            memory.cursor.execute(
                "UPDATE command_usage SET use_count = use_count + 1, last_used = CURRENT_TIMESTAMP WHERE command_pattern = ?",
                (pattern,),
            )
        else:
            memory.cursor.execute(
                "INSERT INTO command_usage (command_pattern) VALUES (?)", (pattern,)
            )
        memory.conn.commit()

    def _normalize(self, command):
        for word in ("jarvis", "hey", "hello", "please", "can you"):
            command = command.replace(word, "")
        return " ".join(command.split())[:80].strip()

    def get_frequent_commands(self, limit=5):
        memory.cursor.execute(
            "SELECT command_pattern, use_count FROM command_usage ORDER BY use_count DESC LIMIT ?",
            (limit,),
        )
        return [{"command": r[0], "count": r[1]} for r in memory.cursor.fetchall()]

    def suggest_shortcut(self):
        frequent = self.get_frequent_commands(1)
        if frequent and frequent[0]["count"] >= 3:
            cmd = frequent[0]["command"]
            return f"You often say '{cmd}'. Want me to create a shortcut?"
        return None


learning = LearningEngine()
