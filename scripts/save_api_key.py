"""Save API keys to local database (not committed to git)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from database import create_tables, set_setting


def main():
    create_tables()
    groq = os.environ.get("GROQ_API_KEY", "").strip()
    if not groq and len(sys.argv) > 1:
        groq = sys.argv[1].strip()
    if not groq:
        print("Usage: set GROQ_API_KEY=gsk_... then python scripts/save_api_key.py")
        print("   or: python scripts/save_api_key.py gsk_your_key_here")
        sys.exit(1)
    set_setting("groq_api_key", groq)
    set_setting("grok_api_key", groq)
    print("Groq API key saved to database. Restart JARVIS: python main.py")


if __name__ == "__main__":
    main()
