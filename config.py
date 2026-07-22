"""
JARVIS AI Operating System — Configuration
"""
import os

_ROOT = os.path.dirname(os.path.abspath(__file__))


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
    if os.environ.get("GROQ_API_KEY"):
        return
    try:
        from database import get_setting
        key = get_setting("groq_api_key") or get_setting("grok_api_key")
        if key:
            os.environ["GROQ_API_KEY"] = key
    except Exception:
        pass


_load_env_file()

# Identity
USERNAME = os.environ.get("JARVIS_USERNAME", "Gopi")
ASSISTANT_NAME = "Jarvis"
ASSISTANT_CITY = os.environ.get("JARVIS_CITY", "Mumbai")

# Wake words
WAKE_WORDS = ["jarvis", "hello jarvis", "hey jarvis"]
REQUIRE_WAKE_WORD = os.environ.get("REQUIRE_WAKE_WORD", "false").lower() == "true"
USE_PORCUPINE_WAKE_WORD = os.environ.get("USE_PORCUPINE", "false").lower() == "true"

# Voice
VOICE_RATE = 165
VOICE_VOLUME = 1.0
VOICE_INDEX = 1
LISTEN_TIMEOUT = 5
PHRASE_TIME_LIMIT = 12

# Storage
DATABASE_PATH = "database/assistant.db"
MEMORY_DB_PATH = "jarvis_memory.db"
SCREENSHOTS_DIR = "screenshots"
REPORTS_DIR = "reports"
CHARTS_DIR = "charts"

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

for _dir in (SCREENSHOTS_DIR, REPORTS_DIR, CHARTS_DIR, "database"):
    os.makedirs(_dir, exist_ok=True)

# After database path exists, pull saved Groq key
_load_keys_from_database()
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROK_API_KEY = GROQ_API_KEY
