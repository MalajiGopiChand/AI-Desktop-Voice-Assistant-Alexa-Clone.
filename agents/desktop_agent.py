import os
import time
import platform
import subprocess
from agents.base_agent import BaseAgent

try:
    import pyautogui
    pyautogui.FAILSAFE = False
except Exception:
    pyautogui = None

APP_MAP = {
    "chrome": "chrome",
    "google chrome": "chrome",
    "browser": "chrome",
    "notepad": "notepad",
    "note pad": "notepad",
    "calculator": "calc",
    "calc": "calc",
    "paint": "mspaint",
    "vscode": "code",
    "vs code": "code",
    "visual studio code": "code",
    "spotify": "spotify",
    "discord": "discord",
    "telegram": "telegram",
    "whatsapp": "whatsapp:",
    "whats app": "whatsapp:",
    "what app": "whatsapp:",
    "watsapp": "whatsapp:",
    "wtsapp": "whatsapp:",
    "file explorer": "explorer",
    "explorer": "explorer",
    "cmd": "cmd",
    "command prompt": "cmd",
    "task manager": "taskmgr",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "copilot": "ms-copilot:",
    "co pilot": "ms-copilot:",
    "ko pilot": "ms-copilot:",
}


class DesktopAgent(BaseAgent):
    def __init__(self):
        super().__init__("desktop_agent")

    def execute(self, action, params):
        try:
            handlers = {
                "open_app": self._open_app,
                "type": self._type,
                "press": self._press,
                "hotkey": self._hotkey,
                "wait": self._wait,
                "screenshot": self._screenshot,
                "switch_window": self._switch_window,
                "close_window": self._close_window,
                "open_folder": self._open_folder,
                "move_file": self._move_file,
                "rename_file": self._rename_file,
                "delete_file": self._delete_file,
                "shutdown": self._shutdown,
                "restart": self._restart,
                "lock": self._lock,
                "sleep": self._sleep,
                "click": self._click,
                "click_target": self._click_target,
                "move_mouse": self._move_mouse,
                "scroll": self._scroll,
            }
            handler = handlers.get(action)
            if not handler:
                return {"success": False, "message": f"Unknown action: {action}", "data": {}}
            return handler(params)
        except Exception as e:
            return {"success": False, "message": str(e), "data": {}}

    def _click(self, params):
        button = params.get("button", "left")
        if button == "right":
            pyautogui.rightClick()
        elif button == "double":
            pyautogui.doubleClick()
        else:
            pyautogui.click()
        return {"success": True, "message": f"Executed {button} click", "data": {}}

    def _click_target(self, params):
        target = params.get("target", params.get("name", params.get("element", "")))
        from agents.vision_agent import VisionAgent
        v = VisionAgent()
        return v.find_and_click_element(target)

    def _move_mouse(self, params):
        direction = params.get("direction", "down").lower()
        amount = int(params.get("amount", 150))
        x, y = 0, 0
        if "up" in direction:
            y = -amount
        elif "down" in direction:
            y = amount
        elif "left" in direction:
            x = -amount
        elif "right" in direction:
            x = amount
        pyautogui.moveRel(x, y, duration=0.2)
        return {"success": True, "message": f"Moved mouse {direction} by {amount}px", "data": {}}

    def _scroll(self, params):
        direction = params.get("direction", "down").lower()
        clicks = -500 if "down" in direction else 500
        pyautogui.scroll(clicks)
        return {"success": True, "message": f"Scrolled {direction}", "data": {}}

    def _get_chrome_exe(self):
        candidates = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        ]
        return next((c for c in candidates if os.path.exists(c)), "chrome")

    def _open_app(self, params):
        raw_app = params.get("app_name", "").lower().strip()
        from core.learning import learning
        app_name = learning.resolve_semantic_phrase(raw_app)
        profile = params.get("profile", "")

        if "chrome" in app_name:
            exe = self._get_chrome_exe()
            if profile:
                cmd = f'"{exe}" --profile-directory="{profile}"'
            else:
                cmd = f'"{exe}"'
            subprocess.Popen(cmd, shell=True)
            msg = f"Opened Chrome with profile {profile}" if profile else "Opened Chrome"
            return {"success": True, "message": msg, "data": {}}

        for key, launch in APP_MAP.items():
            if key in app_name or app_name in key:
                if platform.system() == "Windows":
                    if launch.endswith(":"):
                        os.system(f"start {launch}")
                    elif launch == "explorer":
                        pyautogui.hotkey("win", "e")
                    else:
                        subprocess.Popen(f"start {launch}", shell=True)
                return {"success": True, "message": f"Opened {app_name}", "data": {}}

        pyautogui.press("win")
        time.sleep(0.6)
        pyautogui.write(app_name, interval=0.05)
        time.sleep(0.6)
        pyautogui.press("enter")
        return {"success": True, "message": f"Opening {app_name} from Start menu", "data": {}}

    def _type(self, params):
        text = params.get("text", "")
        pyautogui.write(text, interval=0.04)
        return {"success": True, "message": "Typed text", "data": {}}

    def _press(self, params):
        key = params.get("key", "")
        pyautogui.press(key)
        return {"success": True, "message": f"Pressed {key}", "data": {}}

    def _hotkey(self, params):
        keys = params.get("keys", [])
        pyautogui.hotkey(*keys)
        return {"success": True, "message": f"Pressed {'+'.join(keys)}", "data": {}}

    def _wait(self, params):
        seconds = float(params.get("seconds", 1))
        time.sleep(seconds)
        return {"success": True, "message": f"Waited {seconds}s", "data": {}}

    def _screenshot(self, params):
        shot = pyautogui.screenshot()
        path = params.get("path") or f"screenshot_{int(time.time())}.png"
        shot.save(path)
        return {"success": True, "message": f"Screenshot saved to {path}", "data": {"path": path}}

    def _switch_window(self, params):
        pyautogui.hotkey("alt", "tab")
        time.sleep(0.3)
        return {"success": True, "message": "Switched window", "data": {}}

    def _close_window(self, params):
        pyautogui.hotkey("alt", "f4")
        return {"success": True, "message": "Closed active window", "data": {}}

    def _open_folder(self, params):
        path = params.get("path", os.path.expanduser("~"))
        if platform.system() == "Windows":
            os.startfile(path)
        return {"success": True, "message": f"Opened folder {path}", "data": {}}

    def _move_file(self, params):
        src = params.get("source")
        dst = params.get("destination")
        os.replace(src, dst)
        return {"success": True, "message": f"Moved {src} to {dst}", "data": {}}

    def _rename_file(self, params):
        src = params.get("path")
        new_name = params.get("new_name")
        dst = os.path.join(os.path.dirname(src), new_name)
        os.rename(src, dst)
        return {"success": True, "message": f"Renamed to {new_name}", "data": {}}

    def _delete_file(self, params):
        path = params.get("path")
        if os.path.isdir(path):
            import shutil
            shutil.rmtree(path)
        else:
            os.remove(path)
        return {"success": True, "message": f"Deleted {path}", "data": {}}

    def _shutdown(self, params):
        os.system("shutdown /s /t 5")
        return {"success": True, "message": "Shutting down in 5 seconds", "data": {}}

    def _restart(self, params):
        os.system("shutdown /r /t 5")
        return {"success": True, "message": "Restarting in 5 seconds", "data": {}}

    def _lock(self, params):
        os.system("rundll32.exe user32.dll,LockWorkStation")
        return {"success": True, "message": "Locked workstation", "data": {}}

    def _sleep(self, params):
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return {"success": True, "message": "Entering sleep mode", "data": {}}
