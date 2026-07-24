"""Calendar agent — Google Calendar events and reminders."""
from agents.base_agent import BaseAgent
from services.calendar_service import list_upcoming_events, create_reminder


class CalendarAgent(BaseAgent):
    def __init__(self):
        super().__init__("calendar_agent")

    def execute(self, action, params):
        try:
            if action == "list_events":
                _, msg = list_upcoming_events(params.get("limit", 5))
                return {"success": True, "message": msg, "data": {}}
            if action == "create_reminder":
                ok, msg = create_reminder(
                    params.get("title", "Metis Reminder"),
                    int(params.get("minutes", 30)),
                )
                return {"success": ok, "message": msg, "data": {}}
            if action == "today_schedule":
                events, msg = list_upcoming_events(10)
                if events:
                    msg = "Today's schedule: " + "; ".join(events)
                return {"success": True, "message": msg, "data": {"events": events}}
            return {"success": False, "message": f"Unknown action: {action}", "data": {}}
        except Exception as e:
            return {"success": False, "message": str(e), "data": {}}
