"""METIS Orchestrator — voice loop with wake word and multi-agent execution."""
import time
from core.voice_engine import voice_engine
from core.command_processor import processor
from core.memory import memory
from core.wake_word import wake_detector
from config import USERNAME, ASSISTANT_NAME, USE_PORCUPINE_WAKE_WORD


class Orchestrator:
    def __init__(self):
        self.running = True

    def run(self):
        name = memory.get_preference("username", USERNAME)
        mode = "offline Porcupine" if wake_detector.is_offline_available else "voice"
        voice_engine.speak(
            f"{ASSISTANT_NAME} online. Hello {name}. Wake word mode: {mode}. Say Metis to activate."
        )

        while self.running:
            try:
                if USE_PORCUPINE_WAKE_WORD and wake_detector.is_offline_available:
                    if not wake_detector.listen_for_wake_word(timeout=30):
                        continue
                    voice_engine.speak("Yes?")
                    command = voice_engine.listen(timeout=8, phrase_time_limit=12)
                else:
                    text = voice_engine.listen(timeout=5, phrase_time_limit=8)
                    if not text:
                        continue
                    voice_engine.stop_speaking()
                    if any(w in text for w in ("exit", "quit", "shutdown metis", "sleep mode")):
                        voice_engine.speak("Powering down. Goodbye.")
                        break
                    detected, command = wake_detector.check_transcript(text)
                    if not detected:
                        continue
                    if not command:
                        voice_engine.speak("Yes?")
                        command = voice_engine.listen(timeout=8, phrase_time_limit=12)
                        if not command:
                            continue

                if any(w in command for w in ("exit", "quit", "shutdown metis")):
                    voice_engine.speak("Goodbye.")
                    break

                response = processor.process(
                    command,
                    confirm_callback=voice_engine.listen_for_confirmation,
                    speak_callback=None,
                )
                if response:
                    voice_engine.speak(response)


            except Exception as e:
                print(f"Orchestrator error: {e}")
                voice_engine.speak("I encountered an error. Please try again.")

    def stop(self):
        self.running = False


def start_metis():
    Orchestrator().run()


def start_metis_thread():
    import threading
    threading.Thread(target=start_metis, daemon=True).start()


def start_jarvis_thread():
    start_metis_thread()
