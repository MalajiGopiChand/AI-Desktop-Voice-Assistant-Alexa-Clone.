"""
Utilities Module.
This module contains the actual actions the assistant can perform.
"""

import os
import time
import webbrowser
import subprocess
import psutil
import wikipedia
import datetime
import platform

try:
    import pyautogui
    pyautogui.FAILSAFE = False
except Exception:
    pyautogui = None


def _require_desktop_automation():
    if pyautogui is None:
        raise RuntimeError("Desktop automation is unavailable in this cloud environment.")
    return pyautogui

def get_ist_now():
    try:
        import zoneinfo
        tz = zoneinfo.ZoneInfo("Asia/Kolkata")
        return datetime.datetime.now(tz)
    except Exception:
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        ist_offset = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
        return utc_now.astimezone(ist_offset)


def system_info():
    cpu_usage = psutil.cpu_percent(interval=0.2)
    memory_info = psutil.virtual_memory()
    ram_usage = memory_info.percent

    battery = psutil.sensors_battery()
    if battery:
        plugged = "plugged in and charging" if battery.power_plugged else "not plugged in"
        battery_status = f"Battery is at {battery.percent} percent and is {plugged}."
    else:
        battery_status = "Battery information is active."

    return {"cpu_percent": cpu_usage, "ram_percent": ram_usage, "battery_status": battery_status, "text": f"CPU is at {cpu_usage} percent. RAM usage is at {ram_usage} percent. {battery_status}"}


def get_time_greeting(name="Gopi"):
    now = get_ist_now()
    hour = now.hour
    if 5 <= hour < 12:
        period = "Good morning"
    elif 12 <= hour < 17:
        period = "Good afternoon"
    elif 17 <= hour < 22:
        period = "Good evening"
    else:
        period = "Good night"
    return f"{period} Master {name}! Metis is online and ready."


def get_time():
    now = get_ist_now()
    return f"The current time in India (IST) is {now.strftime('%I:%M %p')}."


def get_date():
    now = get_ist_now()
    return f"Today is {now.strftime('%A, %B %d, %Y')} (India Standard Time)."

def open_app(app_name):
    app_name = app_name.lower()
    try:
        if "chrome" in app_name:
            if platform.system() == "Windows":
                # Ensure we pass the whole string so arguments like --profile-directory work
                chrome_cmd = app_name if app_name.startswith("chrome") else "chrome"
                os.system(f"start {chrome_cmd}")
            else:
                webbrowser.open("http://www.google.com")
            return f"Opening {app_name}."
        elif "notepad" in app_name:
            subprocess.Popen("notepad.exe")
            return "Opening Notepad."
        elif "calculator" in app_name or "calc" in app_name:
            subprocess.Popen("calc.exe")
            return "Opening Calculator."
        elif "paint" in app_name:
            subprocess.Popen("mspaint.exe")
            return "Opening Paint."
        elif "task manager" in app_name:
            gui = _require_desktop_automation()
            gui.hotkey('ctrl', 'shift', 'esc')
            return "Opening Task Manager."
        elif "file explorer" in app_name or "my computer" in app_name:
            gui = _require_desktop_automation()
            gui.hotkey('win', 'e')
            return "Opening File Explorer."
        elif "browser" in app_name:
            webbrowser.open("http://www.google.com")
            return "Opening browser."
        elif "whatsapp" in app_name:
            os.system("start whatsapp:")
            return "Opening WhatsApp."
        elif "code" in app_name or "vs code" in app_name:
            os.system("code")
            return "Opening VS Code."
        else:
            # Fallback to searching the start menu using pyautogui
            gui = _require_desktop_automation()
            gui.press('win')
            time.sleep(1.5) # Give start menu time to open
            gui.write(app_name, interval=0.1)
            time.sleep(1.5) # Give search time to find the app
            gui.press('enter')
            return f"Trying to open {app_name} from the start menu."
    except Exception as e:
        print(f"Failed to open app {app_name}: {e}")
        return f"Sorry, I encountered an error trying to open {app_name}."

def web_search(query):
    query = query.lower()
    if "wikipedia" in query:
        search_term = query.replace("search wikipedia for", "").replace("wikipedia", "").replace("search", "").strip()
        try:
            result = wikipedia.summary(search_term, sentences=2)
            return f"According to Wikipedia: {result}"
        except:
            return "I couldn't find a clear Wikipedia page for that."
            
    elif "youtube" in query:
        search_term = query.replace("search youtube for", "").replace("youtube", "").replace("search", "").strip()
        url = f"https://www.youtube.com/results?search_query={search_term}"
        webbrowser.open(url)
        return f"Opening YouTube search results for {search_term}."
    else:
        search_term = query.replace("search for", "").replace("search google for", "").replace("search", "").strip()
        url = f"https://www.google.com/search?q={search_term}"
        webbrowser.open(url)
        return f"Here is what I found on Google for {search_term}."

def open_website(url_name):
    websites = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "gmail": "https://mail.google.com",
        "chatgpt": "https://chat.openai.com",
        "github": "https://github.com"
    }
    for key, url in websites.items():
        if key in url_name.lower():
            webbrowser.open(url)
            return f"Opening {key}."
            
    target = url_name.replace("open ", "").strip().replace(" ", "")
    webbrowser.open(f"https://www.{target}.com")
    return f"Opening {target} dot com."

def automate_task(task):
    task = task.lower()
    try:
        gui = _require_desktop_automation()
        if "screenshot" in task:
            screenshot = gui.screenshot()
            file_name = f"screenshot_{int(time.time())}.png"
            screenshot.save(file_name)
            return f"Screenshot saved."
        elif "volume up" in task or "increase volume" in task:
            for _ in range(5): gui.press('volumeup')
            return "Volume increased."
        elif "volume down" in task or "decrease volume" in task:
            for _ in range(5): gui.press('volumedown')
            return "Volume decreased."
        elif "mute" in task:
            gui.press('volumemute')
            return "Muted system volume."
        elif "copy" in task:
            gui.hotkey('ctrl', 'c')
            return "Copied to clipboard."
        elif "paste" in task:
            gui.hotkey('ctrl', 'v')
            return "Pasted from clipboard."
        elif "select all" in task:
            gui.hotkey('ctrl', 'a')
            return "Selected all text."
        elif "play" in task or "pause" in task:
            import keyboard
            keyboard.send('play/pause media')
            return "Toggled play/pause."
        elif "skip" in task or "next" in task:
            import keyboard
            keyboard.send('next track')
            return "Skipped to next track."
        elif "previous" in task or "back" in task:
            import keyboard
            keyboard.send('previous track')
            return "Went to previous track."
        elif "type" in task:
            import keyboard
            text_to_type = task.replace("type", "", 1).strip()
            keyboard.write(text_to_type, delay=0.05)
            return f"Typed: {text_to_type}"
        elif "press enter" in task or "hit enter" in task:
            gui.press('enter')
            return "Pressed Enter."
        elif "press escape" in task:
            gui.press('esc')
            return "Pressed Escape."
        else:
            return "I don't know how to automate that task yet."
    except Exception as e:
        print(f"Automation error: {e}")
        return "An error occurred during automation."

def system_power(action):
    action = action.lower()
    try:
        if "shutdown" in action or "shut down" in action:
            os.system("shutdown /s /t 1")
            return "Shutting down the computer."
        elif "restart" in action:
            os.system("shutdown /r /t 1")
            return "Restarting the computer."
        elif "lock" in action:
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return "Locking the computer."
        elif "sleep" in action:
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return "Putting the computer to sleep."
    except Exception as e:
        print(f"Power command error: {e}")
        return "Failed to execute power command."

def ask_ai(prompt):
    """Uses Groq LLM via shared client."""
    try:
        from core.brain import brain
        return brain.converse(prompt)
    except Exception as e:
        print(f"AI Error: {e}")
        return "I am unable to connect to the AI service. Please configure your Groq API key."

def execute_complex_automation(command):
    """Delegate multi-step UI automation to the automation agent."""
    try:
        from agents.automation_agent import AutomationAgent
        agent = AutomationAgent()
        result = agent.execute("parse_and_run", {"command": command})
        return result.get("message", "Automation finished.")
    except Exception as e:
        print(f"Automation Parser Error: {e}")
        return "An error occurred while executing the complex automation."


def auto_learn_command(command):
    """Parse natural language training and save as custom command."""
    try:
        from core.llm_client import chat, FAST_MODEL
        from database import add_custom_command
        import json

        system_prompt = """Extract trigger phrase and action from the user's training instruction.
Valid action_types: "open", "url", "speak".
Reply ONLY JSON: {"trigger": "...", "action_type": "...", "action_value": "..."}"""

        raw = chat(
            [{"role": "system", "content": system_prompt}, {"role": "user", "content": command}],
            model=FAST_MODEL,
            max_tokens=150,
            temperature=0.1,
        )
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw.strip())
        trigger = data.get("trigger", "").lower().strip()
        action_type = data.get("action_type")
        action_value = data.get("action_value")
        if trigger and action_type and action_value:
            if add_custom_command(trigger, action_type, action_value):
                return f"Got it! When you say '{trigger}', I will {action_type} {action_value}."
            return "Failed to save the command."
        return "I couldn't understand what you wanted me to learn."
    except Exception as e:
        print(f"Auto-learn Error: {e}")
        return "Please configure your Groq API key in Settings, then try again."
