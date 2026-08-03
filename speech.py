"""
Speech Module for Metis AI.
Supports both local desktop hardware TTS/STT and cloud server web fallbacks.
Fixes: Too-many-open-files via listen lock, exponential backoff, gc.collect.
"""

import gc
import threading
import queue
import time

from config import VOICE_RATE, VOICE_VOLUME, LISTEN_TIMEOUT, PHRASE_TIME_LIMIT
from database import get_setting

# ── Optional imports ──────────────────────────────────────────────────────────
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


# ── Widget state helpers ───────────────────────────────────────────────────────
def set_widget_state(state, text=""):
    try:
        with open("widget_state.txt", "w", encoding="utf-8") as f:
            f.write(state)
        if text:
            with open("widget_text.txt", "w", encoding="utf-8") as f:
                f.write(text)
    except Exception:
        pass


# ── TTS engine ────────────────────────────────────────────────────────────────
tts_queue   = queue.Queue()
interrupt_flag = False
engine_ref  = None


def get_available_voices():
    """Returns a list of available system voices."""
    if not TTS_AVAILABLE:
        return [{"id": 0, "name": "Web Browser Voice Engine (Cloud)"}]
    try:
        try:
            import pythoncom
            pythoncom.CoInitialize()
        except Exception:
            pass
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
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
        try:
            import pythoncom
            pythoncom.CoInitialize()
        except Exception:
            pass
        engine_ref = pyttsx3.init()
        engine_ref.setProperty("rate", VOICE_RATE)
        engine_ref.setProperty("volume", VOICE_VOLUME)
        # Force Female Voice
        try:
            voices = engine_ref.getProperty("voices")
            female_id = None
            for v in voices:
                vn = (v.name or "").lower()
                if any(n in vn for n in ["zira", "hazel", "female", "susan", "eva", "catherine", "helena"]):
                    female_id = v.id
                    break
            if female_id:
                engine_ref.setProperty("voice", female_id)
            elif voices and len(voices) > 1:
                engine_ref.setProperty("voice", voices[1].id)
        except Exception:
            pass
    except Exception as e:
        print(f"TTS Init notice: {e}")
        engine_ref = None

    while True:
        text = tts_queue.get()
        if text is None:
            break
        print(f"Metis: {text}")
        if engine_ref:
            try:
                set_widget_state("speaking", text)
                engine_ref.say(text)
                engine_ref.runAndWait()
                set_widget_state("idle")
            except Exception as e:
                print(f"TTS Error: {e}")
                set_widget_state("idle")
                try:
                    engine_ref.endLoop()
                except Exception:
                    pass
                try:
                    engine_ref = pyttsx3.init()
                    engine_ref.setProperty("rate", VOICE_RATE)
                    engine_ref.setProperty("volume", VOICE_VOLUME)
                except Exception:
                    pass
        tts_queue.task_done()


worker_thread = threading.Thread(target=_tts_worker, daemon=True)
worker_thread.start()


def speak(text):
    if not text:
        return
    set_widget_state("speaking", text)
    tts_queue.put(text)


def stop_speaking():
    global interrupt_flag, engine_ref
    interrupt_flag = True
    with tts_queue.mutex:
        tts_queue.queue.clear()
    if engine_ref:
        try:
            engine_ref.stop()
        except Exception:
            pass
    set_widget_state("idle")


# ── STT engine ────────────────────────────────────────────────────────────────
# Single shared recognizer to avoid resource re-creation on every call
if SR_AVAILABLE:
    _recognizer = sr.Recognizer()
    _recognizer.energy_threshold        = 280
    _recognizer.dynamic_energy_threshold = True
    _recognizer.pause_threshold         = 0.5
    _recognizer.phrase_threshold        = 0.1
    _recognizer.non_speaking_duration   = 0.3
else:
    _recognizer = None

# Mutex: only ONE listen() allowed at a time (prevents file-descriptor explosion)
_listen_lock   = threading.Lock()
_error_backoff = 0.5   # starts at 0.5 s, doubles on repeated network errors


def listen():
    """Capture one utterance from the microphone and return the transcription."""
    global _error_backoff

    if not SR_AVAILABLE or not _recognizer:
        print("Speech Recognition disabled. Use Web UI input.")
        time.sleep(1)
        return ""

    # Non-blocking lock: if another listen() is already running, skip this cycle
    if not _listen_lock.acquire(blocking=False):
        return ""

    try:
        with sr.Microphone() as source:
            print("Listening...", flush=True)
            set_widget_state("listening")

            try:
                audio = _recognizer.listen(
                    source,
                    timeout=LISTEN_TIMEOUT,
                    phrase_time_limit=PHRASE_TIME_LIMIT,
                )
            except sr.WaitTimeoutError:
                set_widget_state("idle")
                return ""

            try:
                print("Processing...", flush=True)
                query = _recognizer.recognize_google(audio)
                print(f"User said: {query}")
                _error_backoff = 0.5          # reset on success
                set_widget_state("idle")
                return query.lower()

            except sr.UnknownValueError:
                set_widget_state("idle")
                return ""

            except sr.RequestError as req_err:
                err_str = str(req_err).lower()
                set_widget_state("idle")

                if "too many open files" in err_str or "temporarily unavailable" in err_str:
                    print(f"Network resource error — backing off {_error_backoff:.1f}s: {req_err}")
                    time.sleep(_error_backoff)
                    _error_backoff = min(_error_backoff * 2, 8.0)  # cap at 8 s
                    gc.collect()           # release stale file descriptors
                else:
                    print(f"Speech API error: {req_err}")
                    time.sleep(0.5)
                return ""

            except Exception:
                set_widget_state("idle")
                return ""

    except Exception as mic_err:
        set_widget_state("idle")
        print(f"Microphone error: {mic_err}")
        time.sleep(1)
        return ""

    finally:
        _listen_lock.release()
        gc.collect()     # always free audio buffer memory
