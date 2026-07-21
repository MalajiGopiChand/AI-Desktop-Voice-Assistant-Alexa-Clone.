"""
Utilities Module.
This module contains the actual actions the assistant can perform.
Things like opening apps, checking system status, and web searches happen here.
"""

import os
import time
import webbrowser
import subprocess
import psutil
import pyautogui
import wikipedia
import datetime
from config import DEFAULT_BROWSER

def system_info():
    """
    Gathers system information like CPU, RAM, and Battery.
    Returns a string meant to be spoken by the assistant.
    """
    # CPU usage percentage
    cpu_usage = psutil.cpu_percent(interval=0.5)
    
    # RAM usage percentage
    memory_info = psutil.virtual_memory()
    ram_usage = memory_info.percent
    
    # Battery information (if available, e.g., on a laptop)
    battery = psutil.sensors_battery()
    battery_status = ""
    if battery:
        plugged = "plugged in and charging" if battery.power_plugged else "not plugged in"
        battery_status = f"Battery is at {battery.percent} percent and is {plugged}."
    else:
        battery_status = "Battery information is not available."

    return f"CPU is at {cpu_usage} percent. RAM usage is at {ram_usage} percent. {battery_status}"

def get_time():
    """Returns the current time in a spoken format."""
    now = datetime.datetime.now()
    return f"The current time is {now.strftime('%I:%M %p')}."

def get_date():
    """Returns the current date in a spoken format."""
    now = datetime.datetime.now()
    return f"Today is {now.strftime('%B %d, %Y')}."

def open_app(app_name):
    """
    Tries to open a known application.
    This uses basic Windows commands or known paths.
    """
    app_name = app_name.lower()
    
    try:
        if "notepad" in app_name:
            subprocess.Popen("notepad.exe")
            return "Opening Notepad."
        elif "calculator" in app_name or "calc" in app_name:
            subprocess.Popen("calc.exe")
            return "Opening Calculator."
        elif "paint" in app_name:
            subprocess.Popen("mspaint.exe")
            return "Opening Paint."
        elif "task manager" in app_name:
            # Task manager shortcut
            pyautogui.hotkey('ctrl', 'shift', 'esc')
            return "Opening Task Manager."
        elif "file explorer" in app_name or "my computer" in app_name:
            # Windows key + E opens Explorer
            pyautogui.hotkey('win', 'e')
            return "Opening File Explorer."
        elif "browser" in app_name or "chrome" in app_name:
            # Tries to open the default browser or Chrome if requested
            webbrowser.open("http://www.google.com")
            return "Opening browser."
        elif "code" in app_name or "vs code" in app_name:
            # Assumes VS Code is in the system PATH
            os.system("code")
            return "Opening VS Code."
        else:
            # Fallback: search Windows using the start menu
            pyautogui.press('win')
            time.sleep(0.5)
            pyautogui.write(app_name)
            time.sleep(0.5)
            pyautogui.press('enter')
            return f"Trying to open {app_name} from the start menu."
    except Exception as e:
        print(f"Failed to open app {app_name}: {e}")
        return f"Sorry, I encountered an error trying to open {app_name}."

def web_search(query):
    """
    Performs a web search based on the query.
    Can search Wikipedia, YouTube, or Google.
    """
    query = query.lower()
    
    if "wikipedia" in query:
        # Extract the search term (remove "search wikipedia for")
        search_term = query.replace("search wikipedia for", "").replace("wikipedia", "").replace("search", "").strip()
        try:
            # Get a summary of the topic (limit to 2 sentences)
            result = wikipedia.summary(search_term, sentences=2)
            return f"According to Wikipedia: {result}"
        except wikipedia.exceptions.DisambiguationError:
            return "There are too many results for that topic. Please be more specific."
        except wikipedia.exceptions.PageError:
            return "I couldn't find a Wikipedia page for that."
            
    elif "youtube" in query:
        search_term = query.replace("search youtube for", "").replace("youtube", "").replace("search", "").strip()
        url = f"https://www.youtube.com/results?search_query={search_term}"
        webbrowser.open(url)
        return f"Opening YouTube search results for {search_term}."
        
    else:
        # Default Google search
        search_term = query.replace("search for", "").replace("search google for", "").replace("search", "").strip()
        url = f"https://www.google.com/search?q={search_term}"
        webbrowser.open(url)
        return f"Here is what I found on Google for {search_term}."

def open_website(url_name):
    """Opens common websites directly."""
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
            
    # If not in the list, just append .com
    target = url_name.replace("open ", "").strip()
    # Remove any spaces in target
    target = target.replace(" ", "")
    webbrowser.open(f"https://www.{target}.com")
    return f"Opening {target} dot com."

def automate_task(task):
    """
    Performs simple desktop automation using pyautogui.
    """
    task = task.lower()
    
    try:
        if "screenshot" in task:
            # Capture the screen and save it
            screenshot = pyautogui.screenshot()
            file_name = f"screenshot_{int(time.time())}.png"
            screenshot.save(file_name)
            return f"Screenshot saved as {file_name}."
            
        elif "volume up" in task or "increase volume" in task:
            for _ in range(5):
                pyautogui.press('volumeup')
            return "Volume increased."
            
        elif "volume down" in task or "decrease volume" in task:
            for _ in range(5):
                pyautogui.press('volumedown')
            return "Volume decreased."
            
        elif "mute" in task:
            pyautogui.press('volumemute')
            return "Muted system volume."
            
        elif "copy" in task:
            pyautogui.hotkey('ctrl', 'c')
            return "Copied to clipboard."
            
        elif "paste" in task:
            pyautogui.hotkey('ctrl', 'v')
            return "Pasted from clipboard."
            
        elif "select all" in task:
            pyautogui.hotkey('ctrl', 'a')
            return "Selected all text."
            
        elif "type" in task:
            # Example: "type hello world"
            text_to_type = task.replace("type", "", 1).strip()
            pyautogui.write(text_to_type, interval=0.05)
            return f"Typed: {text_to_type}"
            
        elif "press enter" in task or "hit enter" in task:
            pyautogui.press('enter')
            return "Pressed Enter."
            
        elif "press escape" in task:
            pyautogui.press('esc')
            return "Pressed Escape."
            
        else:
            return "I don't know how to automate that task yet."
            
    except Exception as e:
        print(f"Automation error: {e}")
        return "An error occurred during automation."

def system_power(action):
    """
    Handles system shutdown, restart, lock, and sleep.
    """
    action = action.lower()
    
    try:
        if "shutdown" in action or "shut down" in action:
            # /s = shutdown, /t 1 = time 1 second
            os.system("shutdown /s /t 1")
            return "Shutting down the computer."
        elif "restart" in action:
            # /r = restart
            os.system("shutdown /r /t 1")
            return "Restarting the computer."
        elif "lock" in action:
            # Windows lock command
            os.system("rundll32.exe user32.dll,LockWorkStation")
            return "Locking the computer."
        elif "sleep" in action:
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return "Putting the computer to sleep."
    except Exception as e:
        print(f"Power command error: {e}")
        return "Failed to execute power command."
