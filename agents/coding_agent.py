import os
import subprocess
import tempfile
from agents.base_agent import BaseAgent
from core.llm_client import chat, FAST_MODEL


class CodingAgent(BaseAgent):
    def __init__(self):
        super().__init__("coding_agent")

    def execute(self, action, params):
        try:
            handlers = {
                "generate_code": self._generate_code,
                "explain_code": self._explain_code,
                "fix_code": self._fix_code,
                "run_code": self._run_code,
                "git_status": self._git_status,
            }
            handler = handlers.get(action)
            if not handler:
                return {"success": False, "message": f"Unknown action: {action}", "data": {}}
            return handler(params)
        except Exception as e:
            return {"success": False, "message": str(e), "data": {}}

    def _generate_code(self, params):
        prompt = params.get("prompt", "")
        language = params.get("language", "python")
        code = chat(
            [
                {"role": "system", "content": f"Generate {language} code. Return only code, no markdown."},
                {"role": "user", "content": prompt},
            ],
            model=FAST_MODEL,
            max_tokens=800,
        )
        return {"success": True, "message": "Code generated", "data": {"code": code}}

    def _explain_code(self, params):
        code = params.get("code", "")
        explanation = chat(
            [
                {"role": "system", "content": "Explain this code briefly for voice output."},
                {"role": "user", "content": code[:4000]},
            ],
            model=FAST_MODEL,
            max_tokens=300,
        )
        return {"success": True, "message": explanation, "data": {"explanation": explanation}}

    def _fix_code(self, params):
        code = params.get("code", "")
        error = params.get("error", "")
        fixed = chat(
            [
                {"role": "system", "content": "Fix the code. Return only the corrected code."},
                {"role": "user", "content": f"Error: {error}\n\nCode:\n{code}"},
            ],
            model=FAST_MODEL,
            max_tokens=800,
        )
        return {"success": True, "message": "Code fixed", "data": {"code": fixed}}

    def _run_code(self, params):
        code = params.get("code", "")
        language = params.get("language", "python")
        with tempfile.NamedTemporaryFile(
            suffix=".py" if language == "python" else ".txt", delete=False, mode="w", encoding="utf-8"
        ) as f:
            f.write(code)
            path = f.name
        try:
            if language == "python":
                result = subprocess.run(
                    ["python", path], capture_output=True, text=True, timeout=30
                )
                output = result.stdout or result.stderr
            else:
                output = "Only Python execution is supported locally."
            return {"success": True, "message": output[:500], "data": {"output": output}}
        finally:
            os.unlink(path)

    def _git_status(self, params):
        cwd = params.get("path", os.getcwd())
        result = subprocess.run(
            ["git", "status", "--short"], capture_output=True, text=True, cwd=cwd
        )
        output = result.stdout.strip() or "Working tree clean"
        return {"success": True, "message": output, "data": {"status": output}}
