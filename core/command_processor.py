"""
Unified command processor — single pipeline for voice, web UI, and API.
"""
import importlib

from config import IS_CLOUD_RUNTIME
from core.memory import memory
from core.brain import brain
from core.planner import planner
from core.learning import learning
from core.safety import requires_confirmation, build_confirmation_prompt
from database import get_custom_commands, save_history

AGENT_CLASSES = {
    "desktop_agent": ("agents.desktop_agent", "DesktopAgent"),
    "browser_agent": ("agents.browser_agent", "BrowserAgent"),
    "research_agent": ("agents.research_agent", "ResearchAgent"),
    "vision_agent": ("agents.vision_agent", "VisionAgent"),
    "comms_agent": ("agents.comms_agent", "CommsAgent"),
    "coding_agent": ("agents.coding_agent", "CodingAgent"),
    "automation_agent": ("agents.automation_agent", "AutomationAgent"),
    "conversation_agent": ("agents.conversation_agent", "ConversationAgent"),
    "calendar_agent": ("agents.calendar_agent", "CalendarAgent"),
    "office_agent": ("agents.office_agent", "OfficeAgent"),
    "analytics_agent": ("agents.analytics_agent", "AnalyticsAgent"),
    "math_agent": ("agents.math_agent", "MathAgent"),
    "file_agent": ("agents.file_agent", "FileAgent"),
    "media_agent": ("agents.media_agent", "MediaAgent"),
    "info_agent": ("agents.info_agent", "InfoAgent"),
    "mobile_agent": ("agents.mobile_agent", "MobileAgent"),
}

CLOUD_DISABLED_AGENTS = {
    "desktop_agent",
    "vision_agent",
    "comms_agent",
    "automation_agent",
    "media_agent",
}


class UnavailableAgent:
    def __init__(self, name, reason):
        self.name = name
        self.reason = reason

    def execute(self, action, params):
        return {
            "success": False,
            "message": f"{self.name} cannot run '{action}' here. {self.reason}",
            "data": {},
        }


def _load_agent(agent_name):
    if IS_CLOUD_RUNTIME and agent_name in CLOUD_DISABLED_AGENTS:
        return UnavailableAgent(
            agent_name,
            "Desktop automation is available only in the local desktop app, not on Vercel.",
        )

    module_name, class_name = AGENT_CLASSES[agent_name]
    try:
        module = importlib.import_module(module_name)
        return getattr(module, class_name)()
    except Exception as exc:
        return UnavailableAgent(agent_name, f"Import failed: {exc}")


class CommandProcessor:
    def __init__(self):
        self.agents = {name: _load_agent(name) for name in AGENT_CLASSES}
        self._last_result_data = {}
        self._pending_confirmation = None

    def process(self, command, confirm_callback=None, speak_callback=None, model=None):
        raw_cmd = (command or "").strip().lower()
        if not raw_cmd:
            return ""

        command = learning.resolve_semantic_phrase(raw_cmd)
        learning.record(command)

        # Immediate Stop Talking / Quiet Interrupt Handlers
        stop_triggers = ("stop talking", "stop speaking", "be quiet", "shut up", "quiet", "stop speech", "silence")
        if command in stop_triggers or any(t in command for t in ("stop talking", "stop speaking", "be quiet", "shut up")):
            from speech import stop_speaking
            stop_speaking()
            return "Stopped speaking."

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
            if isinstance(custom, dict):
                custom = custom.get("text") or custom.get("message") or str(custom)
            memory.add_context("user", command)
            memory.add_context("assistant", custom)
            save_history(command, custom[:80])
            return custom

        simple = self._try_simple(command)
        if simple:
            if isinstance(simple, dict):
                simple = simple.get("text") or simple.get("message") or str(simple)
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

        # --- Window & Navigation Commands ---
        if any(w in command for w in ("minimize", "minimize window", "minimize app", "minimise")):
            r = self.agents["desktop_agent"].execute("minimize_window", {})
            return r.get("message", "Minimized active window.")

        if any(w in command for w in ("reload", "refresh", "reload page", "refresh page")):
            r = self.agents["desktop_agent"].execute("reload_page", {})
            return r.get("message", "Reloaded page.")

        # --- Chrome Profile & Browser Protocols ---
        if "chrome" in command and "profile" in command:
            prof = command.split("profile")[-1].strip()
            r = self.agents["desktop_agent"].execute("open_app", {"app_name": "chrome", "profile": prof})
            return r.get("message", f"Opened Chrome with profile {prof}.")

        # --- YouTube Video & Song Name Auto-Play Handler ---
        if command.startswith("play ") or "play song" in command or "play video" in command or "on youtube" in command or "youtube" in command:
            query = (
                command.replace("search youtube for", "")
                .replace("search youtube", "")
                .replace("play song", "")
                .replace("play video", "")
                .replace("play on youtube", "")
                .replace("play", "")
                .replace("on youtube", "")
                .replace("on yt", "")
                .strip()
            )
            if query and query not in ("pause", "resume", "media", "music", "next", "previous", "track"):
                r = self.agents["browser_agent"].execute("search", {"query": query, "engine": "youtube"})
                import threading
                threading.Thread(target=lambda: self.agents["media_agent"].execute("auto_play_video", {}), daemon=True).start()
                return f"Playing '{query}' on YouTube."
            if "youtube" in command:
                r = self.agents["browser_agent"].execute("search", {"query": query or "trending videos", "engine": "youtube"})
                return r.get("message", "Opened YouTube.")

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

        # Mobile Android Controls
        if command.startswith("call ") or command.startswith("make call "):
            contact = command.replace("make call ", "").replace("call ", "").strip()
            r = self.agents["mobile_agent"].execute("make_call", {"contact": contact})
            return r.get("message", f"Calling {contact}")
        if "set alarm" in command or "alarm for" in command:
            r = self.agents["mobile_agent"].execute("set_alarm", {"time": command})
            return r.get("message", "Alarm set.")
        if "read notifications" in command or "mobile notifications" in command:
            r = self.agents["mobile_agent"].execute("read_notifications", {})
            return r.get("message", "Notifications summarized.")
        if "mobile status" in command or "phone status" in command:
            r = self.agents["mobile_agent"].execute("device_status", {})
            return r.get("message", "Device status retrieved.")

        # --- Ordinal YouTube Video Clicker (1st, 2nd, 3rd, 4th video) ---
        ordinal_map = {
            "first": 1, "1st": 1, "one": 1,
            "second": 2, "2nd": 2, "two": 2,
            "third": 3, "3rd": 3, "three": 3,
            "fourth": 4, "4th": 4, "four": 4,
            "fifth": 5, "5th": 5, "five": 5,
        }
        if any(w in command for w in ("video", "song", "result")) and any(o in command for o in ("first", "1st", "second", "2nd", "third", "3rd", "fourth", "4th", "fifth", "5th")):
            for word, idx in ordinal_map.items():
                if word in command:
                    r = self.agents["media_agent"].execute("play_ordinal_video", {"index": idx})
                    return f"Playing video number {idx} on screen."

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
            info = system_info()
            if isinstance(info, dict):
                return info.get("text", f"CPU: {info.get('cpu_percent')}%, RAM: {info.get('ram_percent')}%. {info.get('battery_status')}")
            return info
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
        if any(w in command for w in ("play video", "pause video", "stop video", "resume video", "fullscreen", "full screen", "seek forward", "seek back", "fast forward", "rewind")):
            if "fullscreen" in command or "full screen" in command:
                return self.agents["media_agent"].execute("fullscreen", {})["message"]
            if "forward" in command or "next" in command:
                return self.agents["media_agent"].execute("seek_forward", {})["message"]
            if "rewind" in command or "back" in command:
                return self.agents["media_agent"].execute("seek_backward", {})["message"]
            return self.agents["media_agent"].execute("play_pause", {})["message"]

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

    def process_structured(self, command, model=None, device_context=None):
        """Returns structured dict with target ('mobile'/'desktop'), agent, action, params, and spoken_reply."""
        raw_cmd = (command or "").strip().lower()
        if not raw_cmd:
            return {"status": "error", "message": "Empty command"}

        # Mobile control direct intent mapping
        if raw_cmd.startswith(("call ", "make call ", "dial ")):
            contact = raw_cmd.replace("make call ", "").replace("call ", "").replace("dial ", "").strip()
            return {
                "status": "success",
                "target": "mobile",
                "agent": "DeviceControlAgent",
                "action": "make_call",
                "params": {"contact": contact},
                "spoken_reply": f"Calling {contact}.",
                "confirmation_required": True
            }

        if any(p in raw_cmd for p in ("whatsapp message", "send whatsapp", "send whatsapp message")):
            parts = raw_cmd.split("to ", 1)[-1] if "to " in raw_cmd else raw_cmd
            contact = parts.split()[0] if parts else "Contact"
            msg = raw_cmd.split("message", 1)[-1].strip(" :") if "message" in raw_cmd else "Hello"
            return {
                "status": "success",
                "target": "mobile",
                "agent": "CommsAgent",
                "action": "send_whatsapp",
                "params": {"contact": contact, "message": msg},
                "spoken_reply": f"Drafting WhatsApp message to {contact}: {msg}",
                "confirmation_required": True
            }

        if any(p in raw_cmd for p in ("send sms", "send text", "text message")):
            parts = raw_cmd.split("to ", 1)[-1] if "to " in raw_cmd else raw_cmd
            contact = parts.split()[0] if parts else "Contact"
            msg = raw_cmd.split("text", 1)[-1].strip(" :") if "text" in raw_cmd else "Hello"
            return {
                "status": "success",
                "target": "mobile",
                "agent": "CommsAgent",
                "action": "send_sms",
                "params": {"contact": contact, "message": msg},
                "spoken_reply": f"Sending SMS to {contact}.",
                "confirmation_required": True
            }

        if "set alarm" in raw_cmd or "alarm for" in raw_cmd:
            return {
                "status": "success",
                "target": "mobile",
                "agent": "DeviceControlAgent",
                "action": "set_alarm",
                "params": {"time": raw_cmd},
                "spoken_reply": "Setting alarm on your phone.",
                "confirmation_required": False
            }

        if any(w in raw_cmd for w in ("flashlight", "torch")):
            toggle = "off" if "off" in raw_cmd else "on"
            return {
                "status": "success",
                "target": "mobile",
                "agent": "DeviceControlAgent",
                "action": "toggle_flashlight",
                "params": {"state": toggle},
                "spoken_reply": f"Turning flashlight {toggle}.",
                "confirmation_required": False
            }

        if "read notifications" in raw_cmd or "summarize notifications" in raw_cmd:
            return {
                "status": "success",
                "target": "mobile",
                "agent": "NotificationAgent",
                "action": "read_notifications",
                "params": {},
                "spoken_reply": "Summarizing your recent notifications.",
                "confirmation_required": False
            }

        if any(w in raw_cmd for w in ("play video", "pause video", "play pause", "pause", "resume video", "stop video", "play music", "pause music")):
            r = self.agents["media_agent"].execute("play_pause", {})
            reply = r.get("message", "Toggled media playback.")
            return {
                "status": "success",
                "target": "desktop",
                "agent": "MediaAgent",
                "action": "play_pause",
                "params": {},
                "spoken_reply": reply,
                "response": reply,
                "confirmation_required": False
            }

        # Fallback to standard process pipeline

        text_response = self.process(command, model=model)
        return {
            "status": "success",
            "target": "general",
            "agent": "ResearchAgent",
            "action": "speak",
            "params": {"text": text_response},
            "spoken_reply": text_response[:290] if text_response else "Request complete.",
            "response": text_response,
            "confirmation_required": False
        }


processor = CommandProcessor()

