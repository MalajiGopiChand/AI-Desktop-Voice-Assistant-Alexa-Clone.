import os
import time
import urllib.parse
import webbrowser
import pyautogui
from agents.base_agent import BaseAgent
from core.llm_client import chat, FAST_MODEL

pyautogui.FAILSAFE = False


class CommsAgent(BaseAgent):
    def __init__(self):
        super().__init__("comms_agent")

    def execute(self, action, params):
        try:
            handlers = {
                "open_email": self._open_email,
                "compose_email": self._compose_email,
                "send_email": self._send_email,
                "open_whatsapp": self._open_whatsapp,
                "send_whatsapp": self._send_whatsapp,
                "read_whatsapp": self._read_whatsapp,
                "read_chats": self._read_chats,
                "answer_email": self._answer_email,
                "explain_popup": self._explain_popup,
                "open_chat": self._open_chat,
                "type_message": self._type_message,
                "send_message": self._send_message,
            }
            handler = handlers.get(action)
            if not handler:
                return {"success": False, "message": f"Unknown action: {action}", "data": {}}
            return handler(params)
        except Exception as e:
            return {"success": False, "message": str(e), "data": {}}

    def _open_chat(self, params):
        contact = params.get("contact", "")
        os.system("start whatsapp:")
        time.sleep(2)
        pyautogui.hotkey("ctrl", "f")
        time.sleep(0.5)
        try:
            import pyperclip
            pyperclip.copy(contact)
            pyautogui.hotkey("ctrl", "v")
        except Exception:
            pyautogui.write(contact, interval=0.05)
        time.sleep(1)
        pyautogui.press("enter")
        time.sleep(0.5)
        return {"success": True, "message": f"Opened chat with {contact}", "data": {}}

    def _type_message(self, params):
        text = params.get("text", "")
        try:
            import pyperclip
            pyperclip.copy(text)
            pyautogui.hotkey("ctrl", "v")
        except Exception:
            pyautogui.write(text, interval=0.03)
        return {"success": True, "message": f"Typed: {text}", "data": {}}

    def _send_message(self, params):
        text = params.get("text", "")
        if text:
            try:
                import pyperclip
                pyperclip.copy(text)
                pyautogui.hotkey("ctrl", "v")
                time.sleep(0.3)
            except Exception:
                pyautogui.write(text, interval=0.03)
        pyautogui.press("enter")
        time.sleep(0.2)
        return {"success": True, "message": "Sent message", "data": {}}

    def _open_email(self, params):
        webbrowser.open("https://mail.google.com/mail/u/0/#inbox")
        return {"success": True, "message": "Opened Gmail inbox", "data": {}}

    def _compose_email(self, params):
        to = params.get("to", "")
        subject = params.get("subject", "")
        body = params.get("body", "")
        mailto = f"mailto:{to}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
        webbrowser.open(mailto)
        return {"success": True, "message": f"Composed email to {to}", "data": {}}

    def _send_email(self, params):
        return self._compose_email(params)

    def _open_whatsapp(self, params):
        os.system("start whatsapp:")
        time.sleep(2)
        return {"success": True, "message": "Opened WhatsApp", "data": {}}

    def _send_whatsapp(self, params):
        contact = params.get("contact", "")
        message = params.get("message", "")
        os.system("start whatsapp:")
        time.sleep(2.5)
        pyautogui.hotkey("ctrl", "f")
        time.sleep(0.5)
        try:
            import pyperclip
            pyperclip.copy(contact)
            pyautogui.hotkey("ctrl", "v")
        except Exception:
            pyautogui.write(contact, interval=0.05)
        time.sleep(1)
        pyautogui.press("enter")
        time.sleep(0.6)
        if message:
            try:
                import pyperclip
                pyperclip.copy(message)
                pyautogui.hotkey("ctrl", "v")
            except Exception:
                pyautogui.write(message, interval=0.03)
            time.sleep(0.3)
            pyautogui.press("enter")
        return {"success": True, "message": f"Sent message to {contact}", "data": {}}

    def _read_whatsapp(self, params):
        return self._read_chats(params)

    def _read_chats(self, params):
        from agents.vision_agent import VisionAgent
        v = VisionAgent()
        res = v._read_screen({})
        text = res.get("data", {}).get("text", "")

        if text:
            summary = chat(
                [
                    {"role": "system", "content": "Extract and summarize recent chat messages visible on screen."},
                    {"role": "user", "content": text[:4000]},
                ],
                model=FAST_MODEL,
                max_tokens=250,
            )
            return {"success": True, "message": f"Chat Summary: {summary}", "data": {"text": text, "summary": summary}}
        return {"success": True, "message": "Opened active chat window. Please ensure chat window is visible on screen.", "data": {}}

    def _answer_email(self, params):
        from agents.vision_agent import VisionAgent
        v = VisionAgent()
        res = v._read_screen({})
        text = res.get("data", {}).get("text", "")

        reply_intent = params.get("reply", "Confirm receipt and thank them.")

        if text:
            reply_text = chat(
                [
                    {"role": "system", "content": f"Write a professional email reply based on visible email text. User instruction: {reply_intent}"},
                    {"role": "user", "content": text[:4000]},
                ],
                model=FAST_MODEL,
                max_tokens=300,
            )

            # Auto-type reply into current text area
            try:
                import pyperclip
                pyperclip.copy(reply_text)
                pyautogui.hotkey("ctrl", "v")
            except Exception:
                pyautogui.write(reply_text[:100], interval=0.03)

            return {"success": True, "message": f"Drafted email reply: {reply_text[:120]}...", "data": {"reply": reply_text}}
        return {"success": False, "message": "Could not read open email text on screen.", "data": {}}

    def _explain_popup(self, params):
        from agents.vision_agent import VisionAgent
        v = VisionAgent()
        res = v._read_screen({})
        text = res.get("data", {}).get("text", "")

        if text:
            explanation = chat(
                [
                    {"role": "system", "content": "Explain what the system alert / popup window on screen says and what action is needed."},
                    {"role": "user", "content": text[:4000]},
                ],
                model=FAST_MODEL,
                max_tokens=250,
            )
            return {"success": True, "message": f"Popup Alert Explanation: {explanation}", "data": {"explanation": explanation}}
        return {"success": True, "message": "No active popup dialog text detected on screen.", "data": {}}
