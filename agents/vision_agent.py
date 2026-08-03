import os
import glob
import time
import platform
import subprocess
from agents.base_agent import BaseAgent
from core.llm_client import chat, FAST_MODEL

try:
    import pyautogui
    pyautogui.FAILSAFE = False
except Exception:
    pyautogui = None

try:
    from PIL import Image
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

# Directory where captures are saved (root of project)
_CAPTURE_DIR = os.path.dirname(os.path.abspath(__file__))
_CAPTURE_DIR = os.path.join(_CAPTURE_DIR, "..")   # one level up → project root


def _cleanup_old_captures(keep_last=3):
    """Delete old vision_capture_*.png files, keeping only the N most recent."""
    try:
        root = os.path.dirname(os.path.abspath(__file__))
        root = os.path.normpath(os.path.join(root, ".."))
        pattern = os.path.join(root, "vision_capture_*.png")
        files = sorted(glob.glob(pattern))
        for old in files[:-keep_last]:
            try:
                os.remove(old)
            except Exception:
                pass
    except Exception:
        pass


class VisionAgent(BaseAgent):
    def __init__(self):
        super().__init__("vision_agent")

    def execute(self, action, params):
        try:
            handlers = {
                "screenshot":       self._screenshot,
                "read_screen":      self._read_screen,
                "ocr_region":       self._ocr_region,
                "describe_screen":  self._describe_screen,
                "click_target":     self._click_target,
            }
            handler = handlers.get(action)
            if not handler:
                return {"success": False, "message": f"Unknown action: {action}", "data": {}}
            return handler(params)
        except Exception as e:
            return {"success": False, "message": str(e), "data": {}}

    def _capture(self):
        """Take a screenshot, save to project root, clean up old ones."""
        root = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
        path = os.path.join(root, f"vision_capture_{int(time.time())}.png")
        saved = False

        if pyautogui:
            try:
                pyautogui.screenshot(path)
                saved = os.path.exists(path) and os.path.getsize(path) > 0
            except Exception:
                saved = False

        if not saved:
            try:
                from PIL import ImageGrab
                shot = ImageGrab.grab()
                shot.save(path)
                saved = os.path.exists(path) and os.path.getsize(path) > 0
            except Exception:
                saved = False

        if not saved and platform.system() == "Windows":
            try:
                ps = (
                    f'[Reflection.Assembly]::LoadWithPartialName("System.Drawing"); '
                    f'[Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms"); '
                    f'$b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds; '
                    f'$bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height; '
                    f'$g = [System.Drawing.Graphics]::FromImage($bmp); '
                    f'$g.CopyFromScreen($b.Location, [System.Drawing.Point]::Empty, $b.Size); '
                    f'$bmp.Save("{path}")'
                )
                subprocess.run(["powershell", "-Command", ps], capture_output=True)
            except Exception:
                pass

        _cleanup_old_captures(keep_last=3)
        return path

    def _ocr(self, image_path):
        """Run OCR on saved screenshot with active window title fallback."""
        text = ""
        if PIL_AVAILABLE:
            try:
                import pytesseract
                img = Image.open(image_path)
                try:
                    text = pytesseract.image_to_string(img)
                finally:
                    img.close()
                text = text.strip()
            except Exception as e:
                print(f"OCR notice: {e}")

        if not text and platform.system() == "Windows":
            try:
                import ctypes
                user32 = ctypes.windll.user32
                hwnd = user32.GetForegroundWindow()
                length = user32.GetWindowTextLengthW(hwnd)
                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buf, length + 1)
                win_title = buf.value.strip()
                if win_title:
                    text = f"Active Screen: {win_title}. Application running on desktop."
            except Exception:
                pass

        return text

    def find_and_click_element(self, target_name):
        """Find target text on screen via OCR and click it; fallback to centre."""
        target_name = (target_name or "").lower().strip()
        path = self._capture()

        # Try OCR-based location
        if PIL_AVAILABLE:
            try:
                import pytesseract
                img = Image.open(path)
                try:
                    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
                finally:
                    img.close()          # ← fix: always close

                n_boxes = len(data.get("text", []))
                for i in range(n_boxes):
                    word = (data["text"][i] or "").lower().strip()
                    if not word or len(word) < 2:
                        continue
                    if target_name in word or word in target_name:
                        x = data["left"][i] + data["width"][i] // 2
                        y = data["top"][i] + data["height"][i] // 2
                        if pyautogui:
                            pyautogui.moveTo(x, y, duration=0.25)
                            pyautogui.click(x, y)
                        return {
                            "success": True,
                            "message": f"Located '{word}' on screen and clicked ({x}, {y}).",
                            "data": {"x": x, "y": y, "target": word},
                        }
            except Exception as e:
                print(f"OCR Target search notice: {e}")

        # Fallback: click centre of screen
        if pyautogui:
            sw, sh = pyautogui.size()
            cx, cy = sw // 2, sh // 2
            pyautogui.moveTo(cx, cy, duration=0.25)
            pyautogui.click(cx, cy)
            return {
                "success": True,
                "message": f"Could not locate '{target_name}' via OCR. Clicked screen centre.",
                "data": {"x": cx, "y": cy},
            }
        return {"success": False, "message": "pyautogui not available.", "data": {}}

    def _click_target(self, params):
        target = params.get("target", params.get("element", params.get("name", "")))
        return self.find_and_click_element(target)

    def _screenshot(self, params):
        path = self._capture()
        return {"success": True, "message": f"Screenshot saved to {path}", "data": {"path": path}}

    def _read_screen(self, params):
        path = self._capture()
        text = self._ocr(path)
        if text:
            summary = chat(
                [
                    {"role": "system", "content": "Summarize visible screen text briefly for the user."},
                    {"role": "user",   "content": text[:5000]},
                ],
                model=FAST_MODEL,
                max_tokens=200,
            )
            return {"success": True, "message": summary, "data": {"text": text, "summary": summary}}

        if platform.system() == "Windows":
            try:
                import ctypes
                user32 = ctypes.windll.user32
                hwnd = user32.GetForegroundWindow()
                length = user32.GetWindowTextLengthW(hwnd)
                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buf, length + 1)
                title = buf.value.strip()
                if title:
                    msg = f"Current screen active window: '{title}'. Screenshot captured to {os.path.basename(path)}."
                    return {"success": True, "message": msg, "data": {"path": path, "window_title": title}}
            except Exception:
                pass

        return {"success": True, "message": f"Screen screenshot captured to {os.path.basename(path)}.", "data": {"path": path}}

    def _ocr_region(self, params):
        path = self._capture()
        text = self._ocr(path)
        return {"success": True, "message": text or "No text detected", "data": {"text": text}}

    def _describe_screen(self, params):
        path = self._capture()
        text = self._ocr(path)
        if text:
            desc = chat(
                [
                    {"role": "system", "content": "Describe what the user is likely looking at based on OCR text."},
                    {"role": "user",   "content": text[:4000]},
                ],
                model=FAST_MODEL,
                max_tokens=200,
            )
            return {"success": True, "message": desc, "data": {"description": desc}}
        return {"success": True, "message": "Screen captured — no readable text found.", "data": {"path": path}}
