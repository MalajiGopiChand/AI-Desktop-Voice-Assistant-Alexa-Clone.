"""
Metis AI OS — Smart Clipboard History Engine.
Tracks clipboard copies, history search, and text summarization ("Paste the API key I copied yesterday").
"""
import time
from core.llm_client import chat, FAST_MODEL

class SmartClipboardEngine:
    def __init__(self):
        self.history = []

    fun_add_item = lambda self, text: self.history.insert(0, {"text": text, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")})

    def search_clipboard(self, query):
        matches = [item for item in self.history if query.lower() in item["text"].lower()]
        return matches[:5]

    def summarize_clipboard(self):
        if not self.history:
            return "Clipboard history is currently empty."
        latest = self.history[0]["text"]
        return chat(
            [
                {"role": "system", "content": "Summarize this copied clipboard text concisely."},
                {"role": "user", "content": latest}
            ],
            model=FAST_MODEL,
            max_tokens=150
        )


clipboard_engine = SmartClipboardEngine()
