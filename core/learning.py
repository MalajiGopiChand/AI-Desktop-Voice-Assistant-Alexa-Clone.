"""
Continuous Learning & Real-Time Human Adaptation Engine.
Learns voice phrase variations, handles typos, and maps synonyms dynamically.
"""
import re
import difflib
from core.memory import memory


TYPO_MAP = {
    r"\b(opeing|opning|opn|launching|stating|openning)\b": "open",
    r"\b(whats app|what app|watsapp|wtsapp|whats-app)\b": "whatsapp",
    r"\b(ko pilot|co pilot|co-pilot|copilot app)\b": "copilot",
    r"\b(chorme|gogle chrome|gchrome)\b": "chrome",
    r"\b(note pad|notepd)\b": "notepad",
    r"\b(calculater|calcu)\b": "calculator",
    r"\b(vsc|vs code|visual studio code)\b": "vscode",
    r"\b(speck|spk|saying|tell me)\b": "speak",
    r"\b(massaien|massage|massages|msg|text msg)\b": "message",
}


class LearningEngine:
    def __init__(self):
        self._ensure_table()

    def _ensure_table(self):
        try:
            memory.cursor.execute("""
                CREATE TABLE IF NOT EXISTS command_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command_pattern TEXT UNIQUE,
                    use_count INTEGER DEFAULT 1,
                    last_used DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            memory.cursor.execute("""
                CREATE TABLE IF NOT EXISTS human_synonyms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_phrase TEXT UNIQUE,
                    target_command TEXT,
                    confidence FLOAT DEFAULT 1.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            memory.conn.commit()
        except Exception as e:
            print(f"Learning table init notice: {e}")

    def record(self, command):
        pattern = self._normalize(command)
        if not pattern:
            return
        try:
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
        except Exception:
            pass

    def learn_human_synonym(self, phrase, target_command):
        phrase_clean = self._normalize(phrase)
        target_clean = self._normalize(target_command)
        if not phrase_clean or not target_clean:
            return
        try:
            memory.cursor.execute(
                "INSERT OR REPLACE INTO human_synonyms (user_phrase, target_command) VALUES (?, ?)",
                (phrase_clean, target_clean),
            )
            memory.conn.commit()
            print(f"[REAL-TIME HUMAN ADAPTATION] Learned: '{phrase_clean}' -> '{target_clean}'")
        except Exception as e:
            print(f"Error saving synonym: {e}")

    def resolve_semantic_phrase(self, raw_command):
        if not raw_command:
            return ""

        clean = raw_command.lower().strip()

        # Apply Regex Typo & Synonym Normalization
        for pattern, replacement in TYPO_MAP.items():
            clean = re.sub(pattern, replacement, clean)

        # Check Learned Human Synonyms in DB
        try:
            memory.cursor.execute(
                "SELECT target_command FROM human_synonyms WHERE user_phrase = ?", (clean,)
            )
            row = memory.cursor.fetchone()
            if row and row[0]:
                return row[0]
        except Exception:
            pass

        return clean

    def _normalize(self, command):
        command = command.lower()
        for word in ("metis", "jarvis", "hey", "hello", "please", "can you", "could you", "i want to"):
            command = command.replace(word, "")
        return " ".join(command.split())[:120].strip()

    def get_frequent_commands(self, limit=5):
        try:
            memory.cursor.execute(
                "SELECT command_pattern, use_count FROM command_usage ORDER BY use_count DESC LIMIT ?",
                (limit,),
            )
            return [{"command": r[0], "count": r[1]} for r in memory.cursor.fetchall()]
        except Exception:
            return []

    def suggest_shortcut(self):
        frequent = self.get_frequent_commands(1)
        if frequent and frequent[0]["count"] >= 4:
            cmd = frequent[0]["command"]
            return f"You frequently use '{cmd}'. I have adapted to execute it automatically."
        return None


learning = LearningEngine()
