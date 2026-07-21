"""
Speech Module.
This module handles all audio input (listening) and output (speaking).
It uses SpeechRecognition to understand microphone input and pyttsx3 to speak text.
"""

import speech_recognition as sr
import pyttsx3
import threading
from config import VOICE_RATE, VOICE_VOLUME, VOICE_INDEX, LISTEN_TIMEOUT, PHRASE_TIME_LIMIT

# Initialize the text-to-speech engine
# pyttsx3 works offline and uses the system's built-in voices.
engine = pyttsx3.init()

def setup_voice():
    """
    Configures the voice engine settings based on config.py.
    """
    engine.setProperty('rate', VOICE_RATE)
    engine.setProperty('volume', VOICE_VOLUME)
    
    # Get available voices and set to the configured index (usually 1 is female, 0 is male)
    voices = engine.getProperty('voices')
    if len(voices) > VOICE_INDEX:
        engine.setProperty('voice', voices[VOICE_INDEX].id)

# Apply settings immediately
setup_voice()

def _speak_sync(text):
    """
    Synchronous speaking function. 
    This blocks the program until it finishes speaking.
    We usually call this inside a thread so it doesn't freeze the assistant.
    """
    engine.say(text)
    engine.runAndWait()

def speak(text):
    """
    Speaks the given text out loud.
    Runs on a separate thread so that the assistant doesn't freeze
    and can do other things while speaking.
    
    Args:
        text (str): The text to be spoken.
    """
    print(f"Assistant: {text}")
    # Create a new thread targeting the synchronous speak function
    thread = threading.Thread(target=_speak_sync, args=(text,))
    thread.daemon = True  # Allows the thread to close when the main program closes
    thread.start()

def listen():
    """
    Listens to the microphone and converts speech to text.
    
    Returns:
        str: The recognized text in lowercase, or an empty string if nothing was heard/understood.
    """
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("Listening...")
        
        # Adjust for ambient noise to improve recognition accuracy
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            # Listen to the user with a timeout so it doesn't hang forever
            audio = recognizer.listen(source, timeout=LISTEN_TIMEOUT, phrase_time_limit=PHRASE_TIME_LIMIT)
            print("Processing...")
            
            # Use Google's free online speech recognition
            query = recognizer.recognize_google(audio)
            print(f"User said: {query}")
            return query.lower()
            
        except sr.WaitTimeoutError:
            # Reached LISTEN_TIMEOUT without hearing anything
            return ""
        except sr.UnknownValueError:
            # Heard something, but couldn't understand the words
            print("Sorry, I didn't catch that.")
            return ""
        except sr.RequestError as e:
            # Internet issue or Google API error
            print(f"Could not request results; check your internet connection. Error: {e}")
            speak("I am having trouble connecting to the internet.")
            return ""
        except Exception as e:
            # Catch any other unexpected errors
            print(f"Error during listening: {e}")
            return ""
