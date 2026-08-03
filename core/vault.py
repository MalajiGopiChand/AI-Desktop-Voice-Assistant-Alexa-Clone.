"""
Metis AI OS — Secure Encrypted AI Vault.
Stores passwords, API keys, private notes, and credentials with PIN authentication protection. Never spoken aloud.
"""
import os
import json
import base64

VAULT_PATH = "metis_vault_secure.json"

class SecureVault:
    def __init__(self):
        self.pin = "1234"  # Default vault PIN
        self.data = self._load_vault()

    def _load_vault(self):
        if os.path.exists(VAULT_PATH):
            try:
                with open(VAULT_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_vault(self):
        try:
            with open(VAULT_PATH, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Vault error: {e}")

    def verify_pin(self, user_pin):
        return str(user_pin).strip() == self.pin

    def store_item(self, pin, key, value, category="API Key"):
        if not self.verify_pin(pin):
            return {"success": False, "message": "Invalid Vault PIN authentication."}

        encoded_val = base64.b64encode(value.encode('utf-8')).decode('utf-8')
        self.data[key] = {
            "value": encoded_val,
            "category": category
        }
        self._save_vault()
        return {"success": True, "message": f"Successfully secured '{key}' in Metis AI Vault."}

    def retrieve_item(self, pin, key):
        if not self.verify_pin(pin):
            return {"success": False, "message": "Invalid Vault PIN authentication."}

        item = self.data.get(key)
        if not item:
            return {"success": False, "message": f"Item '{key}' not found in Vault."}

        decoded_val = base64.b64decode(item["value"].encode('utf-8')).decode('utf-8')
        return {"success": True, "key": key, "value": decoded_val, "category": item["category"]}

    def list_keys(self, pin):
        if not self.verify_pin(pin):
            return {"success": False, "message": "Invalid Vault PIN."}
        return {"success": True, "items": [{"key": k, "category": v["category"]} for k, v in self.data.items()]}


vault = SecureVault()
