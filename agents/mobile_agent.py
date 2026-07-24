from agents.base_agent import BaseAgent
from services.mobile_service import mobile_service


class MobileAgent(BaseAgent):
    def __init__(self):
        super().__init__("mobile_agent")

    def execute(self, action, params):
        try:
            handlers = {
                "make_call": self._make_call,
                "send_sms": self._send_sms,
                "set_alarm": self._set_alarm,
                "read_notifications": self._read_notifications,
                "device_status": self._device_status,
                "open_app": self._open_app,
                "enhance_chat": self._enhance_chat,
            }
            handler = handlers.get(action)
            if not handler:
                return {"success": False, "message": f"Unknown mobile action: {action}", "data": {}}
            return handler(params)
        except Exception as e:
            return {"success": False, "message": str(e), "data": {}}

    def _make_call(self, params):
        contact = params.get("contact", params.get("number", "Contact"))
        res = mobile_service.make_call(contact)
        return {"success": True, "message": res["message"], "data": res}

    def _send_sms(self, params):
        contact = params.get("contact", "")
        message = params.get("message", "")
        res = mobile_service.send_sms(contact, message)
        return {"success": True, "message": res["message"], "data": res}

    def _set_alarm(self, params):
        time_str = params.get("time", "07:00 AM")
        label = params.get("label", "Alarm")
        res = mobile_service.set_alarm(time_str, label)
        return {"success": True, "message": res["message"], "data": res}

    def _read_notifications(self, params):
        res = mobile_service.read_notifications()
        return {"success": True, "message": res["message"], "data": res}

    def _device_status(self, params):
        res = mobile_service.get_device_status()
        msg = f"Android Device Status: Battery {res['battery']}, Wi-Fi: {res['wifi']}, Storage: {res['storage']}"
        return {"success": True, "message": msg, "data": res}

    def _open_app(self, params):
        app_name = params.get("app_name", "")
        res = mobile_service.open_mobile_app(app_name)
        return {"success": True, "message": res["message"], "data": res}

    def _enhance_chat(self, params):
        text = params.get("text", "")
        style = params.get("style", "professional")
        res = mobile_service.enhance_smart_chat(text, style)
        return {"success": True, "message": res["enhanced"], "data": res}
