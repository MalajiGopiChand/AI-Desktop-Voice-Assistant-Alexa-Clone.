"""Media control — Spotify, YouTube, HTML5 browser video, system media keys."""
import pyautogui
from agents.base_agent import BaseAgent

pyautogui.FAILSAFE = False


class MediaAgent(BaseAgent):
    def __init__(self):
        super().__init__("media_agent")

    def execute(self, action, params):
        try:
            import keyboard

            def _play_pause():
                try:
                    keyboard.send("play/pause media")
                except Exception:
                    pass
                pyautogui.press("playpause")
                pyautogui.press("k")

            def _seek_forward():
                pyautogui.press("l")
                pyautogui.press("right")

            def _seek_backward():
                pyautogui.press("j")
                pyautogui.press("left")

            def _fullscreen():
                pyautogui.press("f")

            def _mute():
                pyautogui.press("m")
                pyautogui.press("volumemute")

            actions = {
                "play_pause": _play_pause,
                "pause_video": _play_pause,
                "play_video": _play_pause,
                "stop_video": _play_pause,
                "seek_forward": _seek_forward,
                "seek_backward": _seek_backward,
                "fullscreen": _fullscreen,
                "mute_video": _mute,
                "next_track": lambda: [pyautogui.press("nexttrack"), pyautogui.hotkey("shift", "n")],
                "previous_track": lambda: pyautogui.press("prevtrack"),
                "volume_up": lambda: [pyautogui.press("volumeup") for _ in range(3)],
                "volume_down": lambda: [pyautogui.press("volumedown") for _ in range(3)],
                "open_spotify": lambda: __import__("os").system("start spotify:"),
            }
            fn = actions.get(action)
            if not fn:
                return {"success": False, "message": f"Unknown action: {action}", "data": {}}
            fn()
            labels = {
                "play_pause": "Toggled video play/pause",
                "pause_video": "Paused video playback",
                "play_video": "Resumed video playback",
                "stop_video": "Stopped video playback",
                "seek_forward": "Fast forwarded video",
                "seek_backward": "Rewound video",
                "fullscreen": "Toggled full screen",
                "mute_video": "Toggled mute",
                "next_track": "Skipped to next track/video",
                "previous_track": "Previous track/video",
                "volume_up": "Volume increased",
                "volume_down": "Volume decreased",
                "open_spotify": "Opened Spotify",
            }
            return {"success": True, "message": labels.get(action, "Done"), "data": {}}
        except Exception as e:
            return {"success": False, "message": str(e), "data": {}}
