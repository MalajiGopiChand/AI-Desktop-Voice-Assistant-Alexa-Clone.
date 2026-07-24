from flask import Flask, render_template, request, jsonify
from database import get_history, add_custom_command, save_history, set_setting, get_setting
from core.command_processor import processor
from speech import speak, get_available_voices
from core.llm_client import get_groq_api_key, get_mistral_api_key
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
    model = (data.get("model") or "").strip() or None

    if not command_text:
        return jsonify({"status": "error", "message": "No command provided"})

    lower = command_text.lower()
    for wake in ("metis", "hey metis", "hello metis"):
        if lower.startswith(wake):
            lower = lower.replace(wake, "", 1).strip(" ,.")
            break

    def web_confirm(prompt):
        return bool(data.get("confirm", False))

    response = processor.process(
        lower,
        confirm_callback=web_confirm,
        speak_callback=speak,
        model=model,
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


@app.route("/api/models", methods=["GET"])
def list_models():
    models = [
        {"id": "llama-3.3-70b-versatile", "name": "Llama 3.3 70B (Groq)", "provider": "Groq", "active": bool(get_groq_api_key())},
        {"id": "llama-3.1-8b-instant", "name": "Llama 3.1 8B Fast (Groq)", "provider": "Groq", "active": bool(get_groq_api_key())},
        {"id": "mistral-large-latest", "name": "Mistral Large (Mistral AI)", "provider": "Mistral AI", "active": bool(get_mistral_api_key())},
        {"id": "mistral-small-latest", "name": "Mistral Small (Mistral AI)", "provider": "Mistral AI", "active": bool(get_mistral_api_key())},
    ]
    return jsonify({"models": models})


@app.route("/api/settings/llm", methods=["GET", "POST"])
def manage_llm_keys():
    from config import GROQ_API_KEY, MISTRAL_API_KEY

    if request.method == "POST":
        data = request.json or {}
        if "groq_api_key" in data and data["groq_api_key"]:
            set_setting("groq_api_key", data["groq_api_key"])
            set_setting("grok_api_key", data["groq_api_key"])
            os.environ["GROQ_API_KEY"] = data["groq_api_key"]
        if "mistral_api_key" in data and data["mistral_api_key"]:
            set_setting("mistral_api_key", data["mistral_api_key"])
            os.environ["MISTRAL_API_KEY"] = data["mistral_api_key"]
        return jsonify({"status": "success"})

    groq = get_groq_api_key() or ""
    mistral = get_mistral_api_key() or ""

    mask = lambda k: f"{k[:8]}...{k[-4:]}" if len(k) > 12 else ""
    return jsonify({
        "groq_key_masked": mask(groq),
        "has_groq": bool(groq),
        "mistral_key_masked": mask(mistral),
        "has_mistral": bool(mistral),
    })


@app.route("/api/settings/grok", methods=["GET", "POST"])
def manage_groq_key():
    return manage_llm_keys()


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
        "groq_active": bool(get_groq_api_key()),
        "mistral_active": bool(get_mistral_api_key()),
    })


def start_flask():
    print("METIS Web Dashboard: http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)


if __name__ == "__main__":
    start_flask()
