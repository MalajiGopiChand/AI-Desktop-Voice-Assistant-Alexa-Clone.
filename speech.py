"""
Speech Module.
Handles audio input (listening) and output (speaking).
Fixed threading: Uses a queue and a background worker for pyttsx3 to avoid crashes.
"""

import speech_recognition as sr
import pyttsx3
import threading
import queue
import time
from config import VOICE_RATE, VOICE_VOLUME, LISTEN_TIMEOUT, PHRASE_TIME_LIMIT
from database import get_setting

def set_widget_state(state):
    try:
        with open("widget_state.txt", "w") as f:
            f.write(state)
    except:
        pass

# We use a Queue to pass text to the TTS engine safely.
tts_queue = queue.Queue()
interrupt_flag = False
engine_ref = None

def onWord(name, location, length):
    global interrupt_flag, engine_ref
    if interrupt_flag and engine_ref:
        engine_ref.stop()
        interrupt_flag = False

def get_available_voices():
    """Returns a list of available system voices."""
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    return [{"id": i, "name": v.name} for i, v in enumerate(voices)]

def _tts_worker():
    """
    Dedicated background thread for pyttsx3.
    """
    global engine_ref
    engine_ref = pyttsx3.init()
    engine_ref.connect('word', onWord)
    
    # Configure fixed properties
    engine_ref.setProperty('rate', VOICE_RATE)
    engine_ref.setProperty('volume', VOICE_VOLUME)
        
    while True:
        text = tts_queue.get()
        if text is None:
            break
            
        v_idx = int(get_setting("voice_index", 1))
        voices = engine_ref.getProperty('voices')
        if len(voices) > v_idx:
            engine_ref.setProperty('voice', voices[v_idx].id)
            
        print(f"Assistant: {text}")
        try:
            set_widget_state("speaking")
            engine_ref.say(text)
            engine_ref.runAndWait()
            set_widget_state("idle")
        except Exception as e:
            print(f"TTS Error: {e}")
        tts_queue.task_done()

# Start the TTS worker thread immediately
worker_thread = threading.Thread(target=_tts_worker, daemon=True)
worker_thread.start()

def speak(text):
    """
    Speaks the given text out loud.
    Adds text to the queue to be processed by the worker thread.
    """
    tts_queue.put(text)

def stop_speaking():
    """Stops current speech and clears the queue."""
    global interrupt_flag
    interrupt_flag = True
    with tts_queue.mutex:
        tts_queue.queue.clear()

def listen():
    """
    Listens to the microphone and converts speech to text.
    Handles internet connection errors gracefully.
    """
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("Listening...", flush=True)
        set_widget_state("listening")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            audio = recognizer.listen(source, timeout=LISTEN_TIMEOUT, phrase_time_limit=PHRASE_TIME_LIMIT)
            print("Processing...")
            query = recognizer.recognize_google(audio)
            print(f"User said: {query}")
            return query.lower()
            
        except sr.WaitTimeoutError:
            set_widget_state("idle")
            return ""
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
            set_widget_state("idle")
            return ""
        except sr.RequestError as e:
            # Handle [WinError 10053] and connection issues quietly
            if "10053" in str(e) or "11001" in str(e) or "getaddrinfo" in str(e) or "aborted" in str(e):
                print("Connection lost or aborted. Retrying quietly...")
                time.sleep(1)
            else:
                print(f"Internet Error: {e}")
            return ""
        except Exception as e:
            if "10053" in str(e) or "aborted" in str(e):
                time.sleep(1)
            else:
                print(f"Error during listening: {e}")
            return ""
