"""
METIS AI Operating System — Configuration
"""
import os
import tempfile

_ROOT = os.path.dirname(os.path.abspath(__file__))
IS_VERCEL = os.environ.get("VERCEL") == "1" or bool(os.environ.get("VERCEL_ENV"))
IS_CLOUD_RUNTIME = IS_VERCEL or os.environ.get("METIS_CLOUD_MODE", "false").lower() == "true"
_RUNTIME_DIR = tempfile.gettempdir() if IS_CLOUD_RUNTIME else _ROOT


def _load_env_file():
    path = os.path.join(_ROOT, ".env")
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key, val = key.strip(), val.strip().strip('"').strip("'")
            if key and val:
                os.environ.setdefault(key, val)


def _load_keys_from_database():
    try:
        from database import get_setting
        groq_key = get_setting("groq_api_key") or get_setting("grok_api_key")
        if groq_key and not os.environ.get("GROQ_API_KEY"):
            os.environ["GROQ_API_KEY"] = groq_key
        mistral_key = get_setting("mistral_api_key")
        if mistral_key and not os.environ.get("MISTRAL_API_KEY"):
            os.environ["MISTRAL_API_KEY"] = mistral_key
    except Exception:
        pass


_load_env_file()

# Identity
USERNAME = os.environ.get("JARVIS_USERNAME", os.environ.get("METIS_USERNAME", "Gopi"))
ASSISTANT_NAME = "Metis"
ASSISTANT_CITY = os.environ.get("JARVIS_CITY", os.environ.get("METIS_CITY", "Mumbai"))

# Wake words
WAKE_WORDS = ["metis", "hello metis", "hey metis"]
WAKE_WORD = "metis"
ALT_WAKE_WORD = "hey metis"
REQUIRE_WAKE_WORD = os.environ.get("REQUIRE_WAKE_WORD", "false").lower() == "true"
USE_PORCUPINE_WAKE_WORD = os.environ.get("USE_PORCUPINE", "false").lower() == "true"
SHOW_DESKTOP_WIDGET = os.environ.get("SHOW_DESKTOP_WIDGET", "true").lower() == "true"

# Voice & Timers
VOICE_RATE = 185
VOICE_VOLUME = 1.0
VOICE_INDEX = 1
LISTEN_TIMEOUT = 4
PHRASE_TIME_LIMIT = 8

# Storage
DATABASE_PATH = os.environ.get(
    "DATABASE_PATH",
    os.path.join(_RUNTIME_DIR, "assistant.db") if IS_CLOUD_RUNTIME else "database/assistant.db",
)
MEMORY_DB_PATH = os.environ.get(
    "MEMORY_DB_PATH",
    os.path.join(_RUNTIME_DIR, "metis_memory.db") if IS_CLOUD_RUNTIME else "metis_memory.db",
)
SCREENSHOTS_DIR = os.path.join(_RUNTIME_DIR, "screenshots") if IS_CLOUD_RUNTIME else "screenshots"
REPORTS_DIR = os.path.join(_RUNTIME_DIR, "reports") if IS_CLOUD_RUNTIME else "reports"
CHARTS_DIR = os.path.join(_RUNTIME_DIR, "charts") if IS_CLOUD_RUNTIME else "charts"

# Browser
DEFAULT_BROWSER = "chrome"
try:
    import playwright  # noqa: F401
    USE_PLAYWRIGHT = os.environ.get("USE_PLAYWRIGHT", "true").lower() != "false"
except ImportError:
    USE_PLAYWRIGHT = False

CHROME_USER_DATA = os.environ.get("CHROME_USER_DATA", "")

# API Keys
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY", "")
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")
PICOVOICE_ACCESS_KEY = os.environ.get("PICOVOICE_ACCESS_KEY", "")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")

GOOGLE_CREDENTIALS_FILE = os.environ.get("GOOGLE_CREDENTIALS_FILE", "credentials.json")
GOOGLE_TOKEN_FILE = os.environ.get("GOOGLE_TOKEN_FILE", "token.json")
GOOGLE_CALENDAR_SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]

GROK_API_KEY = GROQ_API_KEY

for _dir in (SCREENSHOTS_DIR, REPORTS_DIR, CHARTS_DIR, os.path.dirname(DATABASE_PATH)):
    if _dir:
        os.makedirs(_dir, exist_ok=True)

# After database path exists, pull saved keys
_load_keys_from_database()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY", "")
GROK_API_KEY = GROQ_API_KEY
