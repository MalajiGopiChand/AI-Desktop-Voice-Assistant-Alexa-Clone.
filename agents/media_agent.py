"""Media control — Spotify, YouTube, HTML5 browser video, system media keys."""
import pyautogui
import ctypes
import os
from agents.base_agent import BaseAgent

pyautogui.FAILSAFE = False

# Windows Virtual Key Codes for System Media Control
VK_MEDIA_NEXT_TRACK = 0xB0  # 176
VK_MEDIA_PREV_TRACK = 0xB1  # 177
VK_MEDIA_STOP = 0xB2        # 178
VK_MEDIA_PLAY_PAUSE = 0xB3  # 179
VK_VOLUME_MUTE = 0xAD       # 173
VK_VOLUME_DOWN = 0xAE       # 174
VK_VOLUME_UP = 0xAF         # 175

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002


def send_hardware_media_key(vk_code):
    """Sends hardware-level Windows media key event system-wide."""
    try:
        if os.name == 'nt':
            ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY, 0)
            ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)
            return True
    except Exception as e:
        print(f"Hardware media key error: {e}")
    return False


class MediaAgent(BaseAgent):
    def __init__(self):
        super().__init__("media_agent")

    def execute(self, action, params):
        try:
            def _play_pause():
                # 1. Try hardware-level Windows media key first
                sent = send_hardware_media_key(VK_MEDIA_PLAY_PAUSE)
                if not sent:
                    try:
                        pyautogui.press("playpause")
                    except Exception:
                        pass
                    try:
                        pyautogui.press("space")
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
                sent = send_hardware_media_key(VK_VOLUME_MUTE)
                if not sent:
                    try:
                        pyautogui.press("m")
                    except Exception:
                        pass

            def _next_track():
                sent = send_hardware_media_key(VK_MEDIA_NEXT_TRACK)
                if not sent:
                    try:
                        pyautogui.press("nexttrack")
                        pyautogui.hotkey("shift", "n")
                    except Exception:
                        pass

            def _previous_track():
                sent = send_hardware_media_key(VK_MEDIA_PREV_TRACK)
                if not sent:
                    try:
                        pyautogui.press("prevtrack")
                    except Exception:
                        pass

            def _auto_click_first_video():
                import time
                time.sleep(2.0)
                try:
                    screen_w, screen_h = pyautogui.size()
                    pyautogui.click(screen_w // 2, int(screen_h * 0.35))
                    time.sleep(0.5)
                    _play_pause()
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
                    _play_pause()
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
                "next_track": _next_track,
                "previous_track": _previous_track,
                "volume_up": lambda: [send_hardware_media_key(VK_VOLUME_UP) for _ in range(3)],
                "volume_down": lambda: [send_hardware_media_key(VK_VOLUME_DOWN) for _ in range(3)],
                "open_spotify": lambda: os.system("start spotify:"),
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
