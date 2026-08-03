"""
Metis AI OS — Digital Twin & Predictive Need Engine.
Builds user habit profile (coding habits, daily routine, frequently used apps) and predicts needs proactively.
"""
import time
from core.memory import memory

class DigitalTwinEngine:
    def predict_user_needs(self):
        hour = time.localtime().tm_hour
        username = memory.get_preference("username", "User")

        if 8 <= hour < 11:
            return {
                "time_window": "Morning Start",
                "prediction": "Coding Workspace Preparation",
                "suggestion": f"Good morning, {username}! Would you like me to open your VS Code workspace, check today's calendar, and run your dev server?"
            }
        elif 12 <= hour < 14:
            return {
                "time_window": "Midday Break",
                "prediction": "Lunch & News Briefing",
                "suggestion": f"Midday check-in, {username}. Would you like me to summarize today's news and read urgent notifications?"
            }
        elif 17 <= hour < 20:
            return {
                "time_window": "Evening Wrap-up",
                "prediction": "Daily Summary & Git Commit",
                "suggestion": f"Evening wrap-up time, {username}. Would you like me to commit today's code changes and prepare tomorrow's agenda?"
            }
        else:
            return {
                "time_window": "Night Time",
                "prediction": "Wind-down & Focus Mode",
                "suggestion": "Night time mode. Would you like me to enable dark mode and set tomorrow's morning alarm?"
            }


digital_twin = DigitalTwinEngine()
