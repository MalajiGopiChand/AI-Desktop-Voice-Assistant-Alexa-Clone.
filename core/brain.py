"""Natural language reasoning engine — conversation, Q&A, and task understanding."""
from core.llm_client import chat, FAST_MODEL
from core.memory import memory


SYSTEM_PROMPT = """You are JARVIS, an intelligent desktop AI operating system.
You help the user with conversations, reasoning, coding, research, and desktop tasks.
Be concise — responses may be spoken aloud via text-to-speech.
When you lack live data, say so honestly.
Never store or ask for passwords."""


class Brain:
    def converse(self, user_message):
        context = memory.get_context(limit=8)
        facts = memory.recall_facts(limit=10)
        fact_str = "\n".join(f"- {f}" for f in facts) if facts else "None stored yet."
        username = memory.get_preference("username", "User")

        messages = [
            {"role": "system", "content": f"{SYSTEM_PROMPT}\nUser name: {username}\nKnown facts:\n{fact_str}"},
        ]
        for msg in context:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_message})

        return chat(messages, model=FAST_MODEL, max_tokens=300)

    def classify_intent(self, user_message):
        """Returns 'simple', 'complex', or 'conversation'."""
        lower = user_message.lower()
        complex_triggers = [
            "then", "after", "first", "next", "open chrome", "send message",
            "send email", "whatsapp", "search for", "apply for", "summarize",
            "take screenshot", "read screen", "create", "automate",
            "weather", "calendar", "schedule", "analyze", "chart", "pdf",
            "excel", "word", "organize", "duplicate", "remind",
        ]
        simple_triggers = ["time", "date", "battery", "system info", "volume", "mute"]

        if any(t in lower for t in simple_triggers) and len(lower.split()) < 8:
            return "simple"
        if any(t in lower for t in complex_triggers) or len(lower.split()) > 6:
            return "complex"
        return "conversation"


brain = Brain()
