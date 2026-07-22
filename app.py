from flask import Flask, render_template, request, jsonify
from database import get_history, add_custom_command, save_history, set_setting, get_setting
from core.command_processor import processor
from core.voice_engine import voice_engine
from speech import speak, get_available_voices
import os

app = Flask(__name__)

os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/history", methods=["GET"])
def history():
    return jsonify(get_history(limit=30))


@app.route("/api/command", methods=["POST"])
def handle_command():
    data = request.json or {}
    command_text = (data.get("command") or "").strip()
    if not command_text:
        return jsonify({"status": "error", "message": "No command provided"})

    lower = command_text.lower()
    for wake in ("jarvis", "hey jarvis", "hello jarvis"):
        if lower.startswith(wake):
            lower = lower.replace(wake, "", 1).strip(" ,.")
            break

    def web_confirm(prompt):
        # Web UI auto-approves compose actions; destructive ops need explicit confirm flag
        return bool(data.get("confirm", False))

    response = processor.process(
        lower,
        confirm_callback=web_confirm,
        speak_callback=speak,
    )

    if response:
        speak(response)

    return jsonify({"response": response, "status": "success"})


@app.route("/api/train", methods=["POST"])
def train_command():
    data = request.json or {}
    trigger = data.get("trigger")
    action_value = data.get("action_value")
    action_type = data.get("action_type", data.get("action", "speak"))

    if trigger and action_value:
        add_custom_command(trigger, action_type, action_value)
        return jsonify({"status": "success", "message": f"Trained: '{trigger}'"})
    return jsonify({"status": "error", "message": "Invalid training data"})


@app.route("/api/voices", methods=["GET"])
def list_voices():
    voices = get_available_voices()
    current = get_setting("voice_index", 1)
    return jsonify({"voices": voices, "current": int(current)})


@app.route("/api/settings/voice", methods=["POST"])
def update_voice():
    data = request.json or {}
    voice_index = data.get("voice_index")
    if voice_index is not None:
        set_setting("voice_index", voice_index)
        speak("Voice updated.")
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})


@app.route("/api/settings/grok", methods=["GET", "POST"])
def manage_groq_key():
    from config import GROQ_API_KEY

    if request.method == "POST":
        data = request.json or {}
        api_key = data.get("api_key")
        if api_key:
            set_setting("groq_api_key", api_key)
            set_setting("grok_api_key", api_key)  # legacy
            return jsonify({"status": "success"})
        return jsonify({"status": "error", "message": "No key provided"})

    key = get_setting("groq_api_key") or get_setting("grok_api_key") or GROQ_API_KEY
    display = f"{key[:8]}...{key[-4:]}" if key and len(key) > 12 else ""
    has_key = bool(key)
    return jsonify({"api_key_masked": display, "has_key": has_key})


@app.route("/api/settings/keys", methods=["GET", "POST"])
def manage_api_keys():
    keys = ["openweather_api_key", "news_api_key", "picovoice_access_key", "user_city"]
    if request.method == "POST":
        data = request.json or {}
        for k in keys:
            if k in data and data[k]:
                set_setting(k, data[k])
        return jsonify({"status": "success"})

    result = {}
    for k in keys:
        val = get_setting(k, "")
        if "key" in k and val and len(val) > 12:
            result[k] = f"{val[:6]}...{val[-4:]}"
        else:
            result[k] = val
    result["calendar_configured"] = os.path.exists("token.json")
    result["agents"] = list(processor.agents.keys())
    from core.learning import learning
    result["frequent_commands"] = learning.get_frequent_commands(5)
    return jsonify(result)


@app.route("/api/agents", methods=["GET"])
def list_agents():
    return jsonify({"agents": list(processor.agents.keys())})


@app.route("/api/status", methods=["GET"])
def system_status():
    from utils import system_info
    from core.wake_word import wake_detector
    return jsonify({
        "status": "online",
        "info": system_info(),
        "agents": len(processor.agents),
        "porcupine": wake_detector.is_offline_available,
    })


def start_flask():
    print("JARVIS Web Dashboard: http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)


if __name__ == "__main__":
    start_flask()
