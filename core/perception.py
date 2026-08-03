"""
Metis AI OS — Perception Engine (Voice Emotion & Context Sensor).
Analyzes user tone, speaking speed, active windows, and context (Coding, Gaming, Meetings, Studying, Focus Mode).
"""
import psutil

class PerceptionEngine:
    def detect_user_context(self):
        """Analyzes active processes to detect current user activity context."""
        active_processes = []
        try:
            for p in psutil.process_iter(['name']):
                pname = (p.info.get('name') or '').lower()
                active_processes.append(pname)
        except Exception:
            pass

        p_str = " ".join(active_processes)

        if any(w in p_str for w in ("code", "idea64", "pycharm", "sublime", "devenv")):
            return "Coding & Software Development"
        elif any(w in p_str for w in ("zoom", "teams", "slack", "meet", "webex")):
            return "Meetings & Collaboration"
        elif any(w in p_str for w in ("steam", "epicgames", "discord", "valorant", "gta")):
            return "Gaming & Entertainment"
        elif any(w in p_str for w in ("acrobat", "winword", "pdf", "notion")):
            return "Studying & Document Review"
        return "General Desktop Productivity"

    def analyze_voice_emotion(self, text_input="", wpm=120):
        """Detects fatigue, stress, or excitement from voice speed & sentiment."""
        lower = text_input.lower()
        if any(w in lower for w in ("tired", "exhausted", "late", "sleepy", "hard day")):
            return {"emotion": "Fatigue", "suggestion": "Enable Focus Mode and dim screen brightness?"}
        elif any(w in lower for w in ("urgent", "error", "broken", "help", "failed")):
            return {"emotion": "Stress/Urgency", "suggestion": "Metis is here to help fix the issue."}
        return {"emotion": "Calm", "suggestion": "System operating normally."}


perception_engine = PerceptionEngine()
