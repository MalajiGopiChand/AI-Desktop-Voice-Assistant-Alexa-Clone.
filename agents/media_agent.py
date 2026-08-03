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
                    pyautogui.press("playpause")
                except Exception:
                    pass
                try:
                    pyautogui.press("k")
                except Exception:
                    pass


            def _seek_forward():
                try:
                    pyautogui.press("l")
                    pyautogui.press("right")
                except Exception:
                    pass

            def _seek_backward():
                try:
                    pyautogui.press("j")
                    pyautogui.press("left")
                except Exception:
                    pass

            def _fullscreen():
                try:
                    pyautogui.press("f")
                except Exception:
                    pass

            def _mute():
                try:
                    pyautogui.press("m")
                except Exception:
                    pass

            def _auto_click_first_video():
                import time
                time.sleep(2.0)
                try:
                    screen_w, screen_h = pyautogui.size()
                    pyautogui.click(screen_w // 2, int(screen_h * 0.35))
                    time.sleep(0.5)
                    pyautogui.press("k")
                except Exception:
                    pass

            def _play_ordinal_video(params):
                import time
                try:
                    idx = int(params.get("index", 1))
                    screen_w, screen_h = pyautogui.size()
                    y_ratios = {1: 0.35, 2: 0.50, 3: 0.65, 4: 0.80, 5: 0.90}
                    y_pos = int(screen_h * y_ratios.get(idx, 0.35))
                    x_pos = screen_w // 2
                    pyautogui.click(x_pos, y_pos)
                    time.sleep(0.5)
                    pyautogui.press("k")
                except Exception:
                    pass

            actions = {
                "play_pause": _play_pause,
                "pause_video": _play_pause,
                "play_video": _play_pause,
                "stop_video": _play_pause,
                "seek_forward": _seek_forward,
                "seek_backward": _seek_backward,
                "fullscreen": _fullscreen,
                "mute_video": _mute,
                "auto_play_video": _auto_click_first_video,
                "play_ordinal_video": lambda: _play_ordinal_video(params),
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
