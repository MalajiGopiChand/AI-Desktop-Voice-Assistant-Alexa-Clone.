"""Natural language reasoning engine — conversation, Q&A, and task understanding."""
from core.llm_client import chat, FAST_MODEL
from core.memory import memory


SYSTEM_PROMPT = """You are Metis, an intelligent desktop AI operating system.
You help the user with conversations, reasoning, coding, research, and desktop tasks.
Be concise — responses may be spoken aloud via text-to-speech.
CRITICAL RULE: Do NOT include or state the current date, day, or time in your response UNLESS the user explicitly asks for the date, day, or time in their request.
Never store or ask for passwords."""


class Brain:
    def converse(self, user_message, model=None):
        import time
        from services.weather_service import get_weather
        from services.news_service import get_news

        context = memory.get_context(limit=8)
        facts = memory.recall_facts(limit=10)
        fact_str = "\n".join(f"- {f}" for f in facts) if facts else "None stored yet."
        username = memory.get_preference("username", "User")
        current_time_str = time.strftime("%A, %B %d, %Y at %I:%M %p")

        # Fetch real-time weather & headlines snippet for live context
        _, live_weather = get_weather()
        live_news_items, _ = get_news(limit=3)
        news_str = "; ".join(live_news_items) if live_news_items else "No live news feeds loaded."

        realtime_context = (
            f"\n--- REAL-TIME LIVE DATA (Reference Only — Output date/time ONLY if asked) ---\n"
            f"Current Real-Time Date & Time: {current_time_str}\n"
            f"Live Weather: {live_weather}\n"
            f"Live News Headlines: {news_str}\n"
            f"--- END REAL-TIME DATA ---"
        )

        messages = [
            {"role": "system", "content": f"{SYSTEM_PROMPT}\nUser name: {username}\nKnown facts:\n{fact_str}{realtime_context}"},
        ]
        for msg in context:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": user_message})

        return chat(messages, model=model or FAST_MODEL, max_tokens=400)


    def classify_intent(self, user_message):
        """Returns 'simple', 'complex', or 'conversation'."""
        lower = user_message.lower()
        multi_step_triggers = ["then", "and after that", "first ", "step 1", "next "]
        
        if any(t in lower for t in multi_step_triggers):
            return "complex"
        return "conversation"


brain = Brain()
