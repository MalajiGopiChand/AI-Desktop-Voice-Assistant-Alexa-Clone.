"""
Unified command processor — single pipeline for voice, web UI, and API.
"""
from core.memory import memory
from core.brain import brain
from core.planner import planner
from core.learning import learning
from core.safety import requires_confirmation, build_confirmation_prompt
from database import get_custom_commands, save_history

from agents.desktop_agent import DesktopAgent
from agents.browser_agent import BrowserAgent
from agents.research_agent import ResearchAgent
from agents.vision_agent import VisionAgent
from agents.comms_agent import CommsAgent
from agents.coding_agent import CodingAgent
from agents.automation_agent import AutomationAgent
from agents.conversation_agent import ConversationAgent
from agents.calendar_agent import CalendarAgent
from agents.office_agent import OfficeAgent
from agents.analytics_agent import AnalyticsAgent
from agents.math_agent import MathAgent
from agents.file_agent import FileAgent
from agents.media_agent import MediaAgent
from agents.info_agent import InfoAgent


class CommandProcessor:
    def __init__(self):
        self.agents = {
            "desktop_agent": DesktopAgent(),
            "browser_agent": BrowserAgent(),
            "research_agent": ResearchAgent(),
            "vision_agent": VisionAgent(),
            "comms_agent": CommsAgent(),
            "coding_agent": CodingAgent(),
            "automation_agent": AutomationAgent(),
            "conversation_agent": ConversationAgent(),
            "calendar_agent": CalendarAgent(),
            "office_agent": OfficeAgent(),
            "analytics_agent": AnalyticsAgent(),
            "math_agent": MathAgent(),
            "file_agent": FileAgent(),
            "media_agent": MediaAgent(),
            "info_agent": InfoAgent(),
        }
        self._last_result_data = {}
        self._pending_confirmation = None

    def process(self, command, confirm_callback=None, speak_callback=None, model=None):
        raw_cmd = (command or "").strip().lower()
        if not raw_cmd:
            return ""

        command = learning.resolve_semantic_phrase(raw_cmd)
        learning.record(command)

        # Auto-learn custom commands
        learn_triggers = ("learn", "remember", "teach", "when i say")
        if any(t in command for t in learn_triggers) and len(command.split()) > 3:
            from utils import auto_learn_command
            response = auto_learn_command(command)
            memory.add_context("user", command)
            memory.add_context("assistant", response)
            save_history(command, response[:80])
            return response

        custom = self._try_custom(command)
        if custom:
            memory.add_context("user", command)
            memory.add_context("assistant", custom)
            save_history(command, custom[:80])
            return custom

        simple = self._try_simple(command)
        if simple:
            memory.add_context("user", command)
            memory.add_context("assistant", simple)
            save_history(command, simple[:80])
            return simple

        memory.add_context("user", command)
        intent = brain.classify_intent(command)

        if intent == "conversation":
            response = brain.converse(command, model=model)
            memory.add_context("assistant", response)
            save_history(command, response[:80])
            return response

        if speak_callback:
            speak_callback("Processing your request.")

        plan_result = planner.generate_plan(command, model=model)
        if "error" in plan_result:
            fallback = brain.converse(command, model=model)
            memory.add_context("assistant", fallback)
            save_history(command, f"Fallback: {fallback[:60]}")
            return fallback

        plan = plan_result["plan"]
        final_response = "Task complete."
        self._last_result_data = {}

        for task in plan:
            agent_name = task.get("agent")
            action = task.get("action")
            params = task.get("params", {}) or {}

            if agent_name == "voice_agent":
                if action == "speak":
                    final_response = params.get("text", final_response)
                continue

            if agent_name == "memory_agent":
                if action == "save_fact":
                    memory.remember_fact(params.get("category", "General"), params.get("content", ""))
                elif action == "set_preference":
                    memory.set_preference(params.get("key", ""), params.get("value", ""))
                continue

            if requires_confirmation(agent_name, action):
                if confirm_callback:
                    prompt = build_confirmation_prompt(agent_name, action, params)
                    if speak_callback:
                        speak_callback(prompt)
                    if not confirm_callback(prompt):
                        final_response = "Action cancelled."
                        break
                else:
                    final_response = build_confirmation_prompt(agent_name, action, params)
                    self._pending_confirmation = task
                    break

            agent = self.agents.get(agent_name)
            if not agent:
                continue

            if speak_callback:
                speak_callback(f"Running {action.replace('_', ' ')}.")

            # Pass previous step data to summarize actions
            if params.get("text") == "{{prev}}" and self._last_result_data.get("text"):
                params["text"] = self._last_result_data["text"]
            if params.get("text") == "{{prev}}" and self._last_result_data.get("summary"):
                params["text"] = self._last_result_data["summary"]

            result = agent.execute(action, params)
            if result.get("data"):
                self._last_result_data.update(result["data"])
            if result.get("message"):
                final_response = result["message"]
            if result.get("data", {}).get("summary"):
                final_response = result["data"]["summary"]
            if result.get("data", {}).get("response"):
                final_response = result["data"]["response"]

        suggestion = learning.suggest_shortcut()
        if suggestion and len(command.split()) > 3:
            final_response += f" {suggestion}"

        memory.add_context("assistant", final_response)
        save_history(command, final_response[:80])
        return final_response

    def _try_custom(self, command):
        for trigger, action in get_custom_commands().items():
            if trigger in command:
                if action["type"] == "speak":
                    return action["value"]
                if action["type"] == "open":
                    r = self.agents["desktop_agent"].execute("open_app", {"app_name": action["value"]})
                    return r.get("message", "Done.")
                if action["type"] == "url":
                    r = self.agents["browser_agent"].execute("open_url", {"url": action["value"]})
                    return r.get("message", "Done.")
        return None

    def _try_simple(self, command):
        from utils import get_time, get_date, system_info, automate_task
        from services.weather_service import get_weather
        from services.news_service import get_news

        # --- WhatsApp & Messaging Protocols ---
        if any(p in command for p in ("send whatsapp message to", "send message to", "whatsapp message to")):
            parts = command.split("to ", 1)[-1]
            if ":" in parts:
                contact, msg = parts.split(":", 1)
            elif "message" in parts:
                contact, msg = parts.split("message", 1)
            else:
                words = parts.split()
                contact, msg = words[0], " ".join(words[1:]) if len(words) > 1 else "Hello"
            r = self.agents["comms_agent"].execute("send_whatsapp", {"contact": contact.strip(), "message": msg.strip()})
            return r.get("message", "Sent WhatsApp message.")

        if any(p in command for p in ("open chat with", "open chat", "chat with")) and any(w in command for w in ("whatsapp", "chat", "person", "open")):
            contact = command.replace("open chat with", "").replace("open chat", "").replace("chat with", "").replace("in whatsapp", "").replace("whatsapp", "").strip()
            if contact:
                r = self.agents["comms_agent"].execute("open_chat", {"contact": contact})
                return r.get("message", f"Opened chat with {contact}.")

        if command.startswith(("send message ", "type message ", "send text ", "type text ", "write message ")):
            text = command.replace("send message ", "", 1).replace("type message ", "", 1).replace("send text ", "", 1).replace("type text ", "", 1).replace("write message ", "", 1).strip()
            r = self.agents["comms_agent"].execute("send_message", {"text": text})
            return r.get("message", f"Sent: {text}")

        if command in ("send message", "send it", "send", "press enter to send", "send message now"):
            r = self.agents["comms_agent"].execute("send_message", {})
            return r.get("message", "Sent message.")

        # --- Mouse Control Protocols ---
        if any(w in command for w in ("move mouse", "move cursor", "mouse up", "mouse down", "mouse left", "mouse right")):
            if "up" in command:
                r = self.agents["desktop_agent"].execute("move_mouse", {"direction": "up", "amount": 150})
            elif "down" in command:
                r = self.agents["desktop_agent"].execute("move_mouse", {"direction": "down", "amount": 150})
            elif "left" in command:
                r = self.agents["desktop_agent"].execute("move_mouse", {"direction": "left", "amount": 150})
            elif "right" in command:
                r = self.agents["desktop_agent"].execute("move_mouse", {"direction": "right", "amount": 150})
            else:
                r = self.agents["desktop_agent"].execute("move_mouse", {"direction": "down", "amount": 150})
            return r.get("message", "Moved mouse.")

        if command in ("click", "left click", "mouse click", "click mouse", "click here"):
            r = self.agents["desktop_agent"].execute("click", {"button": "left"})
            return r.get("message", "Clicked mouse.")

        if command in ("right click", "context menu"):
            r = self.agents["desktop_agent"].execute("click", {"button": "right"})
            return r.get("message", "Right clicked.")

        if command in ("double click", "double click mouse"):
            r = self.agents["desktop_agent"].execute("click", {"button": "double"})
            return r.get("message", "Double clicked.")

        if command in ("scroll down", "scroll up", "page down", "page up"):
            direction = "up" if "up" in command else "down"
            r = self.agents["desktop_agent"].execute("scroll", {"direction": direction})
            return r.get("message", f"Scrolled {direction}.")

        # --- Chrome Profile & Browser Protocols ---
        if "chrome" in command and "profile" in command:
            prof = command.split("profile")[-1].strip()
            r = self.agents["desktop_agent"].execute("open_app", {"app_name": "chrome", "profile": prof})
            return r.get("message", f"Opened Chrome with profile {prof}.")

        if "youtube" in command and any(w in command for w in ("search", "play", "open")):
            query = command.replace("search youtube for", "").replace("search youtube", "").replace("play", "").replace("on youtube", "").replace("open youtube", "").strip()
            r = self.agents["browser_agent"].execute("search", {"query": query, "engine": "youtube"})
            return r.get("message", f"Searched YouTube for {query}.")

        # --- Direct Website Opening Protocols ---
        if any(w in command for w in ("netflix", "prime video", "hotstar", "jio hotstar")):
            import webbrowser
            if "netflix" in command:
                webbrowser.open("https://www.netflix.com")
                return "Opening Netflix in your browser."
            elif "prime" in command:
                webbrowser.open("https://www.primevideo.com")
                return "Opening Prime Video in your browser."
            else:
                webbrowser.open("https://www.hotstar.com")
                return "Opening Hotstar in your browser."

        # --- Time-Based Greeting Protocols ---
        if command in ("hello", "hello metis", "hi", "hi metis", "hey metis", "good morning", "good afternoon", "good evening", "good night", "metis online", "metis", "hello jarvis", "jarvis"):
            from utils import get_time_greeting
            return get_time_greeting("Gopi")

        if (command.startswith("click on ") or command.startswith("click ")) and len(command.split()) > 1:
            target = command.replace("click on ", "").replace("click ", "").strip()
            if target not in ("left", "right", "double", "here", "mouse"):
                res = self.agents["vision_agent"].execute("click_target", {"target": target})
                return res.get("message", f"Clicked on {target}")

        if "time" in command and len(command.split()) <= 4:
            return get_time()
        if ("date" in command or "day is it" in command) and len(command.split()) <= 6:
            return get_date()
        if any(w in command for w in ("system info", "battery", "cpu", "ram status")):
            return system_info()
        if any(w in command for w in ("screenshot", "volume", "mute", "copy", "paste")):
            return automate_task(command)
        if "weather" in command:
            city = command.replace("weather", "").replace("in", "").strip() or None
            _, msg = get_weather(city)
            return msg
        if "news" in command or "headlines" in command:
            headlines, _ = get_news()
            if headlines:
                return "; ".join(headlines[:5])
            return "No news available right now. Check your internet connection."
        if any(w in command for w in ("play", "pause", "skip", "next track", "spotify")):
            if "spotify" in command and "open" in command:
                return self.agents["media_agent"].execute("open_spotify", {})["message"]
            if "next" in command or "skip" in command:
                return self.agents["media_agent"].execute("next_track", {})["message"]
            if "previous" in command or "back" in command:
                return self.agents["media_agent"].execute("previous_track", {})["message"]
            return self.agents["media_agent"].execute("play_pause", {})["message"]
        if "remember my name is" in command or "my name is" in command:
            name = command.split("my name is")[-1].strip().title()
            memory.set_preference("username", name)
            memory.remember_fact("User", f"User's name is {name}")
            return f"Got it. I'll call you {name}."
        if command.startswith("calculate "):
            expr = command.replace("calculate", "", 1).strip()
            return self.agents["math_agent"].execute("calculate", {"expression": expr})["message"]
        if command.startswith("what is ") and any(c in command for c in "0123456789+-*/"):
            expr = command.replace("what is", "", 1).strip()
            return self.agents["math_agent"].execute("calculate", {"expression": expr})["message"]
        if command.startswith(("open ", "launch ", "start ")) and len(command.split()) <= 6:
            app_words = [w for w in command.split()[1:] if w not in ("app", "application")]
            app_target = " ".join(app_words).strip()
            if any(w in app_target for w in ("google", "youtube", "gmail", "github", "website", "http", ".com", ".org")):
                r = self.agents["browser_agent"].execute("open_url", {"url": app_target})
                return r.get("message", "Done.")
            r = self.agents["desktop_agent"].execute("open_app", {"app_name": app_target})
            return r.get("message", f"Opened {app_target}.")
        if command.startswith("search ") or command.startswith("search for "):
            query = command.replace("search for", "", 1).replace("search", "", 1).strip()
            r = self.agents["browser_agent"].execute("search", {"query": query})
            return r.get("message", f"Searched for {query}.")
        return None


processor = CommandProcessor()
