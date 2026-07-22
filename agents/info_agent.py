"""Weather and news agent."""
from agents.base_agent import BaseAgent
from services.weather_service import get_weather
from services.news_service import get_news
from core.llm_client import chat, FAST_MODEL


class InfoAgent(BaseAgent):
    def __init__(self):
        super().__init__("info_agent")

    def execute(self, action, params):
        try:
            if action == "weather":
                _, msg = get_weather(params.get("city"))
                return {"success": True, "message": msg, "data": {}}
            if action == "news":
                headlines, _ = get_news(params.get("query", "technology"), params.get("limit", 5))
                if not headlines:
                    return {"success": False, "message": "No news available.", "data": {}}
                summary = chat(
                    [{"role": "system", "content": "Summarize these headlines in 2-3 sentences for voice."},
                     {"role": "user", "content": "\n".join(headlines)}],
                    model=FAST_MODEL, max_tokens=200,
                )
                return {"success": True, "message": summary, "data": {"headlines": headlines}}
            if action == "headlines":
                headlines, msg = get_news(params.get("query", "technology"))
                text = "; ".join(headlines[:5]) if headlines else msg
                return {"success": True, "message": text, "data": {"headlines": headlines}}
            return {"success": False, "message": f"Unknown action: {action}", "data": {}}
        except Exception as e:
            return {"success": False, "message": str(e), "data": {}}
