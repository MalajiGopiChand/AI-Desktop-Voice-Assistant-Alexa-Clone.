"""
Speech Module for Metis AI.
Supports both local desktop hardware TTS/STT and cloud server web fallbacks (Vercel).
"""

import threading
import queue
import time
from config import VOICE_RATE, VOICE_VOLUME, LISTEN_TIMEOUT, PHRASE_TIME_LIMIT
from database import get_setting

# Safe optional imports for cloud compatibility (Vercel)
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False

try:
    import pyttsx3
    TTS_AVAILABLE = True
except Exception:
    TTS_AVAILABLE = False


def set_widget_state(state, text=""):
    try:
        with open("widget_state.txt", "w", encoding="utf-8") as f:
            f.write(state)
        if text:
            with open("widget_text.txt", "w", encoding="utf-8") as f:
                f.write(text)
    except Exception:
        pass


tts_queue = queue.Queue()
interrupt_flag = False
engine_ref = None


def get_available_voices():
    """Returns a list of available system voices."""
    if not TTS_AVAILABLE:
        return [{"id": 0, "name": "Web Browser Voice Engine (Cloud)"}]
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        return [{"id": i, "name": v.name} for i, v in enumerate(voices)]
    except Exception:
        return [{"id": 0, "name": "Standard Engine"}]


def _tts_worker():
    """Dedicated background thread for pyttsx3."""
    global engine_ref
    if not TTS_AVAILABLE:
        while True:
            text = tts_queue.get()
            if text is None:
                break
            print(f"Assistant (Cloud Mode): {text}")
            tts_queue.task_done()
        return

    try:
        engine_ref = pyttsx3.init()
        engine_ref.setProperty('rate', VOICE_RATE)
        engine_ref.setProperty('volume', VOICE_VOLUME)
    except Exception as e:
        print(f"TTS Init notice: {e}")
        engine_ref = None

    while True:
        text = tts_queue.get()
        if text is None:
            break

        print(f"Assistant: {text}")
        if engine_ref:
            try:
                set_widget_state("speaking")
                engine_ref.say(text)
                engine_ref.runAndWait()
                set_widget_state("idle")
            except Exception as e:
                print(f"TTS Error: {e}")
        tts_queue.task_done()


worker_thread = threading.Thread(target=_tts_worker, daemon=True)
worker_thread.start()


def speak(text):
    if not text:
        return
    set_widget_state("speaking", text)
    tts_queue.put(text)


def stop_speaking():
    global interrupt_flag
    interrupt_flag = True
    with tts_queue.mutex:
        tts_queue.queue.clear()


def listen():
    if not SR_AVAILABLE:
        print("Speech Recognition engine disabled on Cloud/Vercel. Use Web UI input.")
        time.sleep(1)
        return ""

    try:
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
                set_widget_state("idle")
                return ""
            except Exception as e:
                set_widget_state("idle")
                return ""
    except Exception:
        # PortAudio / Microphone missing on server environment
        time.sleep(1)
        return ""
