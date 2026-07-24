"""
Metis AI OS — Security, Firewall Protection, & Cryptographic Policy Engine.
Protects API keys, validates incoming requests, and enforces confirmation policies.
"""
import os
import hashlib
import hmac
import time
from database import log_error


class SecurityFirewall:
    def __init__(self):
        self.secret_key = os.environ.get("METIS_SECRET_KEY", "metis_secure_os_key_2026")
        self._blocked_ips = set()

    def generate_token(self, payload_str):
        timestamp = str(int(time.time()))
        message = f"{payload_str}:{timestamp}".encode("utf-8")
        signature = hmac.new(self.secret_key.encode("utf-8"), message, hashlib.sha256).hexdigest()
        return f"{timestamp}:{signature}"

    def validate_request(self, payload_str, token):
        if not token or ":" not in token:
            return False
        try:
            timestamp, signature = token.split(":", 1)
            # Token expiration: 5 minutes
            if abs(time.time() - int(timestamp)) > 300:
                return False
            expected = hmac.new(self.secret_key.encode("utf-8"), f"{payload_str}:{timestamp}".encode("utf-8"), hashlib.sha256).hexdigest()
            return hmac.compare_digest(expected, signature)
        except Exception as e:
            log_error("security.validate_request", str(e))
            return False

    def sanitize_input(self, text):
        if not text:
            return ""
        # Remove shell injection risks & malicious scripts
        forbidden_patterns = ["rm -rf", "format c:", "drop database", "<script>", "</script>"]
        clean = text
        for p in forbidden_patterns:
            if p in clean.lower():
                clean = clean.replace(p, "")
        return clean.strip()

    def requires_confirmation(self, action_name):
        sensitive_actions = [
            "delete_file", "shutdown", "restart", "send_email",
            "send_sms", "make_call", "make_purchase", "wipe_memory"
        ]
        return action_name in sensitive_actions


security_firewall = SecurityFirewall()
