"""
Command Router Module.
This module takes the text heard by the assistant, figures out what it means,
and calls the right function in utils.py.
"""

from utils import (
    system_info, get_time, get_date, open_app, web_search, 
    open_website, automate_task, system_power
)

def process_command(command):
    """
    Parses the command and routes to the correct action.
    Returns the response string that the assistant should speak.
    """
    command = command.lower()

    if not command:
        return ""

    # 1. System Info and Time
    if "time" in command:
        return get_time()
    elif "date" in command or "day" in command:
        return get_date()
    elif "system info" in command or "status" in command or "battery" in command:
        return system_info()

    # 2. Web Search and Websites
    elif "search" in command:
        return web_search(command)
    elif "open website" in command or ("open" in command and ".com" in command):
        return open_website(command)
    elif "open google" in command or "open youtube" in command or "open gmail" in command or "open chatgpt" in command:
        return open_website(command)

    # 3. Open Apps
    elif "open" in command:
        # e.g., "open notepad", extract "notepad"
        app_name = command.replace("open", "").strip()
        return open_app(app_name)

    # 4. Desktop Automation
    elif any(word in command for word in ["screenshot", "volume", "mute", "copy", "paste", "select all", "type", "press"]):
        return automate_task(command)

    # 5. System Power
    elif any(word in command for word in ["shutdown", "restart", "lock", "sleep", "shut down"]):
        return system_power(command)

    # 6. Basic Conversation
    elif "hello" in command or "hi" in command:
        return "Hello! How can I help you today?"
    elif "how are you" in command:
        return "I am functioning perfectly. Thank you for asking!"
    elif "your name" in command or "who are you" in command:
        from config import ASSISTANT_NAME
        return f"I am {ASSISTANT_NAME}, your AI Desktop Assistant."
    elif "bye" in command or "exit" in command or "quit" in command or "stop" in command:
        return "Goodbye! Have a great day."

    # Unknown Command
    else:
        return "I am sorry, I do not understand that command yet."
