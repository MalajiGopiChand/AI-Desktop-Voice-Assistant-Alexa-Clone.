import json
import time
import pyautogui
from agents.base_agent import BaseAgent
from agents.desktop_agent import DesktopAgent
from agents.browser_agent import BrowserAgent
from core.llm_client import chat, FAST_MODEL

pyautogui.FAILSAFE = False


class AutomationAgent(BaseAgent):
    def __init__(self):
        super().__init__("automation_agent")
        self._desktop = DesktopAgent()
        self._browser = BrowserAgent()

    def execute(self, action, params):
        try:
            if action == "run_workflow":
                return self._run_workflow(params)
            if action == "parse_and_run":
                return self._parse_and_run(params)
            return {"success": False, "message": f"Unknown action: {action}", "data": {}}
        except Exception as e:
            return {"success": False, "message": str(e), "data": {}}

    def _run_workflow(self, params):
        steps = params.get("steps", [])
        for step in steps:
            agent = step.get("agent")
            act = step.get("action")
            p = step.get("params", {})
            if agent == "desktop_agent":
                self._desktop.execute(act, p)
            elif agent == "browser_agent":
                self._browser.execute(act, p)
            time.sleep(float(step.get("delay", 0.5)))
        return {"success": True, "message": "Workflow completed", "data": {}}

    def _parse_and_run(self, params):
        command = params.get("command", "")
        system = """Convert the command into a JSON array of UI automation steps.
Valid: {"action":"open_app","value":"chrome"}, {"action":"wait","value":2},
{"action":"type","value":"text"}, {"action":"press","value":"enter"},
{"action":"open_url","value":"url"}, {"action":"search","value":"query"}
Reply with raw JSON only."""

        raw = chat(
            [{"role": "system", "content": system}, {"role": "user", "content": command}],
            model=FAST_MODEL,
            max_tokens=400,
            temperature=0.1,
        )
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        steps = json.loads(raw.strip())

        for step in steps:
            act = step.get("action")
            val = step.get("value")
            if act == "open_app":
                self._desktop.execute("open_app", {"app_name": val})
            elif act == "open_url":
                self._browser.execute("open_url", {"url": val})
            elif act == "search":
                self._browser.execute("search", {"query": val})
            elif act == "type":
                pyautogui.write(str(val), interval=0.04)
            elif act == "press":
                pyautogui.press(str(val))
            elif act == "wait":
                time.sleep(float(val))

        return {"success": True, "message": "Automation sequence executed", "data": {}}
