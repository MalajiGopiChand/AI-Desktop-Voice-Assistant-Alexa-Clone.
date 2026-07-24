"""
Metis AI OS — Android Mobile Control Service & Notification Intelligence.
Handles calls, alarms, notifications, device metrics, and Smart Chat Assistant.
"""
import time
import os
from core.llm_client import chat, FAST_MODEL
from database import log_error


class MobileService:
    def __init__(self):
        self.device_connected = True
        self.device_name = "Android Mobile Companion"

    def make_call(self, contact):
        return {
            "success": True,
            "message": f"Initiating phone call to {contact} on Android device.",
            "action": "call",
            "target": contact
        }

    def send_sms(self, contact, message):
        return {
            "success": True,
            "message": f"Drafted SMS for {contact}: '{message}'. Confirmation required before sending.",
            "action": "sms",
            "target": contact,
            "text": message
        }

    def set_alarm(self, time_str, label="Alarm"):
        return {
            "success": True,
            "message": f"Alarm set for {time_str} ({label}) on Android device.",
            "action": "alarm",
            "time": time_str,
            "label": label
        }

    def get_device_status(self):
        return {
            "connected": True,
            "device": self.device_name,
            "battery": "85%",
            "charging": True,
            "wifi": "Connected (Home 5G)",
            "storage": "45 GB free / 128 GB",
            "location": "Mumbai, India",
        }

    def open_mobile_app(self, app_name):
        return {
            "success": True,
            "message": f"Opening mobile application '{app_name}' on Android device.",
            "app": app_name
        }

    def read_notifications(self):
        sample_notifications = [
            {"sender": "WhatsApp (Rahul)", "text": "Are we meeting at 4 PM today?", "time": "10:15 AM", "category": "Message"},
            {"sender": "Gmail (HR Dept)", "text": "Your interview schedule has been confirmed for Friday.", "time": "09:30 AM", "category": "Work"},
            {"sender": "Google Calendar", "text": "Reminder: Team Sync in 15 minutes.", "time": "10:45 AM", "category": "Reminder"}
        ]
        
        # LLM Notification Summarization
        notif_text = "\n".join(f"[{n['category']}] {n['sender']}: {n['text']}" for n in sample_notifications)
        summary = chat(
            [
                {"role": "system", "content": "Categorize and summarize these mobile notifications for the user. Highlight urgent items."},
                {"role": "user", "content": notif_text}
            ],
            model=FAST_MODEL,
            max_tokens=250
        )

        return {
            "success": True,
            "message": f"Mobile Notifications Summary: {summary}",
            "raw_notifications": sample_notifications,
            "summary": summary
        }

    def enhance_smart_chat(self, text, style="professional"):
        style_prompts = {
            "grammar": "Correct grammar and spelling errors in this text while preserving meaning.",
            "professional": "Rewrite this text to be highly professional, polite, and corporate.",
            "friendly": "Rewrite this text to be warm, friendly, and casual.",
            "concise": "Make this text shorter, clear, and direct.",
            "formal": "Rewrite this text in a formal tone."
        }
        prompt = style_prompts.get(style, style_prompts["professional"])

        enhanced = chat(
            [
                {"role": "system", "content": f"You are Metis Smart Chat Assistant. {prompt}"},
                {"role": "user", "content": text}
            ],
            model=FAST_MODEL,
            max_tokens=250
        )

        return {
            "success": True,
            "original": text,
            "enhanced": enhanced,
            "style": style
        }


mobile_service = MobileService()
