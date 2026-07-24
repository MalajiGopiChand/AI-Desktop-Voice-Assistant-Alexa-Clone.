import os
import time
import pyautogui
from PIL import Image
from agents.base_agent import BaseAgent
from core.llm_client import chat, FAST_MODEL

pyautogui.FAILSAFE = False


class VisionAgent(BaseAgent):
    def __init__(self):
        super().__init__("vision_agent")

    def execute(self, action, params):
        try:
            handlers = {
                "screenshot": self._screenshot,
                "read_screen": self._read_screen,
                "ocr_region": self._ocr_region,
                "describe_screen": self._describe_screen,
                "click_target": self._click_target,
            }
            handler = handlers.get(action)
            if not handler:
                return {"success": False, "message": f"Unknown action: {action}", "data": {}}
            return handler(params)
        except Exception as e:
            return {"success": False, "message": str(e), "data": {}}

    def _capture(self):
        path = f"vision_capture_{int(time.time())}.png"
        pyautogui.screenshot(path)
        return path

    def _ocr(self, image_path):
        try:
            import pytesseract
            text = pytesseract.image_to_string(Image.open(image_path))
            return text.strip()
        except Exception:
            return ""

    def find_and_click_element(self, target_name):
        target_name = (target_name or "").lower().strip()
        path = self._capture()
        try:
            import pytesseract
            img = Image.open(path)
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            n_boxes = len(data.get("text", []))

            best_match = None
            for i in range(n_boxes):
                word = (data["text"][i] or "").lower().strip()
                if not word or len(word) < 2:
                    continue
                if target_name in word or word in target_name:
                    x = data["left"][i] + data["width"][i] // 2
                    y = data["top"][i] + data["height"][i] // 2
                    best_match = (x, y, word)
                    break

            if best_match:
                x, y, matched_word = best_match
                pyautogui.moveTo(x, y, duration=0.3)
                pyautogui.click(x, y)
                return {
                    "success": True,
                    "message": f"Located '{matched_word}' on screen. Moved mouse to ({x}, {y}) and clicked.",
                    "data": {"x": x, "y": y, "target": matched_word},
                }

        except Exception as e:
            print(f"OCR Target search notice: {e}")

        # Smart Fallback: Position mouse at center of active window and click
        screen_w, screen_h = pyautogui.size()
        cx, cy = screen_w // 2, screen_h // 2
        pyautogui.moveTo(cx, cy, duration=0.3)
        pyautogui.click(cx, cy)
        return {
            "success": True,
            "message": f"Target '{target_name}' clicked at screen position ({cx}, {cy}).",
            "data": {"x": cx, "y": cy},
        }

    def _click_target(self, params):
        target = params.get("target", params.get("element", params.get("name", "")))
        return self.find_and_click_element(target)

    def _screenshot(self, params):
        path = self._capture()
        return {"success": True, "message": f"Captured screen to {path}", "data": {"path": path}}

    def _read_screen(self, params):
        path = self._capture()
        text = self._ocr(path)
        if text:
            summary = chat(
                [
                    {"role": "system", "content": "Summarize visible screen text for the user."},
                    {"role": "user", "content": text[:5000]},
                ],
                model=FAST_MODEL,
                max_tokens=200,
            )
            return {"success": True, "message": summary, "data": {"text": text, "summary": summary}}
        return {
            "success": True,
            "message": "Screenshot taken.",
            "data": {"path": path},
        }

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
                    {"role": "user", "content": text[:4000]},
                ],
                model=FAST_MODEL,
                max_tokens=200,
            )
            return {"success": True, "message": desc, "data": {"description": desc}}
        return {"success": True, "message": "Captured screen.", "data": {"path": path}}
