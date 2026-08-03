"""
Core Engine Module.
"""
import time
import threading
from speech import speak, listen
from commands import process_command
from database import save_history
from config import WAKE_WORD, ALT_WAKE_WORD, USERNAME

def start_assistant():
    """
    The main loop of the assistant running in a background thread.
    """
    speak(f"Hello {USERNAME}, I am your A I Assistant. I am ready.")
    
    while True:
        try:
            text = listen()
            
            if not text:
                continue

            # The user spoke! Interrupt the assistant if it is currently speaking.
            from speech import stop_speaking
            stop_speaking()

            if text in ("exit", "quit", "goodbye", "stop listening", "go dormant"):
                speak("Goodbye! I am ready whenever you need me.")
                save_history(text, "User said goodbye")
                time.sleep(2)
                continue

            from speech import set_widget_state
            set_widget_state("processing")
            response = process_command(text)
            if response:
                speak(response)
            save_history(text, f"Success: {response[:20]}...")
                
        except Exception as e:
            print(f"Assistant encountered an error: {e}")
            save_history("Error", str(e))

def start_assistant_thread():
    """Starts the assistant loop in a daemon thread so it doesn't block Flask."""
    t = threading.Thread(target=start_assistant, daemon=True)
    t.start()
