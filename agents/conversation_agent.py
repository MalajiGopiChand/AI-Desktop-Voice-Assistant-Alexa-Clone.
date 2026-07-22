from agents.base_agent import BaseAgent
from core.brain import brain


class ConversationAgent(BaseAgent):
    def __init__(self):
        super().__init__("conversation_agent")

    def execute(self, action, params):
        if action == "chat":
            message = params.get("message", "")
            response = brain.converse(message)
            return {"success": True, "message": response, "data": {"response": response}}
        return {"success": False, "message": f"Unknown action: {action}", "data": {}}
