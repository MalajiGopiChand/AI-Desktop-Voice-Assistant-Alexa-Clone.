"""
Core Engine Module.
This is the brain of the assistant. It continuously runs the main loop,
waits for the wake word, processes commands, and logs history.
"""

import time
from speech import speak, listen
from commands import process_command
from database import save_history
from config import WAKE_WORD, ALT_WAKE_WORD, USERNAME

def start_assistant():
    """
    The main loop of the assistant.
    It greets the user and then listens continuously.
    """
    speak(f"Hello {USERNAME}, I am your A I Assistant. I am ready.")
    
    # Track if we are actively waiting for a command after hearing the wake word
    active_mode = False
    
    while True:
        try:
            # Get text from the microphone
            text = listen()
            
            if not text:
                # If we were in active mode but heard nothing, return to sleep mode
                if active_mode:
                    active_mode = False
                continue

            # Check for exit command first (doesn't require wake word if already active)
            if "exit" in text or "quit" in text or "goodbye" in text:
                response = process_command("exit")
                speak(response)
                save_history(text, "Exited successfully")
                break

            # If we are not in active mode, we only care about the wake word
            if not active_mode:
                if WAKE_WORD in text or ALT_WAKE_WORD in text:
                    active_mode = True
                    speak("Yes?")
                continue
            
            # If we are in active mode, treat the text as a command
            if active_mode:
                # Process the command
                response = process_command(text)
                
                # Speak the response if there is one
                if response:
                    speak(response)
                
                # Log the command to the database
                save_history(text, f"Success: {response[:20]}...")
                
                # After executing one command, go back to waiting for the wake word
                active_mode = False
                
        except KeyboardInterrupt:
            # Handles when the user presses Ctrl+C in the terminal
            print("\nShutting down assistant...")
            break
        except Exception as e:
            print(f"Assistant encountered an error: {e}")
            save_history("Error", str(e))
            # Go back to sleep mode on error
            active_mode = False
