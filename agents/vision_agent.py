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
            "message": "Screenshot taken. Install pytesseract for OCR text extraction.",
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
        return {"success": True, "message": "I captured the screen but could not read text.", "data": {"path": path}}
