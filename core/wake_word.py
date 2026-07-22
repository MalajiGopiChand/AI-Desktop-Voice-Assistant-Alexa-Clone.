"""Optional offline wake word via Picovoice Porcupine."""
from config import USE_PORCUPINE_WAKE_WORD, PICOVOICE_ACCESS_KEY, WAKE_WORDS


class WakeWordDetector:
    def __init__(self):
        self._porcupine = None
        self._audio = None
        self._available = False
        if USE_PORCUPINE_WAKE_WORD:
            self._init_porcupine()

    def _init_porcupine(self):
        try:
            import pvporcupine
            import pyaudio
            from database import get_setting
            import os

            key = (
                os.environ.get("PICOVOICE_ACCESS_KEY")
                or get_setting("picovoice_access_key")
                or PICOVOICE_ACCESS_KEY
            )
            if not key:
                return

            self._porcupine = pvporcupine.create(
                access_key=key,
                keywords=["jarvis"],
            )
            self._audio = pyaudio.PyAudio()
            self._available = True
        except Exception as e:
            print(f"Porcupine wake word unavailable: {e}")

    @property
    def is_offline_available(self):
        return self._available

    def listen_for_wake_word(self, timeout=30):
        """Returns True if wake word detected. Falls back to False if Porcupine unavailable."""
        if not self._available:
            return False

        import pyaudio
        import struct

        stream = self._audio.open(
            rate=self._porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self._porcupine.frame_length,
        )
        try:
            for _ in range(int(timeout * self._porcupine.sample_rate / self._porcupine.frame_length)):
                pcm = stream.read(self._porcupine.frame_length, exception_on_overflow=False)
                pcm = struct.unpack_from("h" * self._porcupine.frame_length, pcm)
                if self._porcupine.process(pcm) >= 0:
                    return True
        finally:
            stream.stop_stream()
            stream.close()
        return False

    def check_transcript(self, text):
        """STT-based wake word check."""
        if not text:
            return False, text
        from config import REQUIRE_WAKE_WORD
        for wake in WAKE_WORDS:
            if wake in text:
                remainder = text.replace(wake, "", 1).strip(" ,.")
                return True, remainder or text
        if not REQUIRE_WAKE_WORD:
            return True, text
        return False, text


wake_detector = WakeWordDetector()
