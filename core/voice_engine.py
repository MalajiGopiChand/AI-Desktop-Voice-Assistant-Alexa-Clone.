import pyttsx3
import speech_recognition as sr
import time
import threading
import queue
from config import WAKE_WORDS, LISTEN_TIMEOUT, PHRASE_TIME_LIMIT


class VoiceEngine:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.microphone = sr.Microphone()
        self.tts_queue = queue.Queue()
        self.interrupt_flag = False
        self.engine_ref = None
        self._worker_thread = threading.Thread(target=self._tts_worker, daemon=True)
        self._worker_thread.start()

    def _tts_worker(self):
        self.engine_ref = pyttsx3.init()
        self.engine_ref.setProperty("rate", 165)
        while True:
            text = self.tts_queue.get()
            if text is None:
                break
            print(f"JARVIS: {text}")
            try:
                self.set_widget_state("speaking")
                self.engine_ref.say(text)
                self.engine_ref.runAndWait()
                self.set_widget_state("idle")
            except Exception as e:
                print(f"TTS Error: {e}")
            self.tts_queue.task_done()

    def set_widget_state(self, state):
        try:
            with open("widget_state.txt", "w", encoding="utf-8") as f:
                f.write(state)
        except OSError:
            pass

    def speak(self, text, block=False):
        if not text:
            return
        self.tts_queue.put(text)
        if block:
            self.tts_queue.join()

    def stop_speaking(self):
        self.interrupt_flag = True
        with self.tts_queue.mutex:
            self.tts_queue.queue.clear()

    def listen(self, timeout=None, phrase_time_limit=None):
        timeout = timeout if timeout is not None else LISTEN_TIMEOUT
        phrase_time_limit = phrase_time_limit if phrase_time_limit is not None else PHRASE_TIME_LIMIT

        self.recognizer.pause_threshold = 0.8  # Wait for full sentence before JARVIS responds (never interrupts user)
        self.recognizer.non_speaking_duration = 0.5

        with self.microphone as source:
            self.set_widget_state("listening")
            print("Listening...", flush=True)
            self.stop_speaking()  # Instantly stop JARVIS speech when listening for user input
            self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
            try:
                audio = self.recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=phrase_time_limit
                )
                self.stop_speaking()
                self.set_widget_state("processing")
                text = self.recognizer.recognize_google(audio).lower().strip()
                print(f"User said: {text}")
                return text
            except sr.WaitTimeoutError:
                self.set_widget_state("idle")
                return ""
            except sr.UnknownValueError:
                self.set_widget_state("idle")
                return ""
            except sr.RequestError as e:
                if any(c in str(e) for c in ("10053", "11001", "aborted")):
                    time.sleep(1)
                else:
                    print(f"Network Error: {e}")
                self.set_widget_state("idle")
                return ""
            except Exception as e:
                print(f"Listen error: {e}")
                self.set_widget_state("idle")
                return ""

    def detect_wake_word(self, text):
        if not text:
            return False, text
        for wake in WAKE_WORDS:
            if wake in text:
                remainder = text.replace(wake, "", 1).strip(" ,.")
                return True, remainder
        return False, text

    def listen_for_confirmation(self, prompt, timeout=8):
        self.speak(prompt)
        response = self.listen(timeout=timeout, phrase_time_limit=5)
        if not response:
            return False
        from core.safety import CONFIRM_WORDS, DENY_WORDS
        if any(w in response for w in DENY_WORDS):
            return False
        return any(w in response for w in CONFIRM_WORDS)


voice_engine = VoiceEngine()
