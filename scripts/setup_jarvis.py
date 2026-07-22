"""First-run setup helper."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)


def main():
    from database import create_tables, get_setting
    from config import GROQ_API_KEY

    create_tables()
    print("JARVIS Setup Check")
    print("-" * 40)

    key = GROQ_API_KEY or get_setting("groq_api_key") or get_setting("grok_api_key")
    print(f"Groq API key: {'OK' if key else 'MISSING (required)'}")

    try:
        import playwright  # noqa: F401
        print("Playwright: OK")
    except ImportError:
        print("Playwright: not installed (pip install playwright)")

    try:
        import groq  # noqa: F401
        print("Groq SDK: OK")
    except ImportError:
        print("Groq SDK: MISSING (pip install groq)")

    if not key:
        print("\nTo fix Groq:")
        print("  1. Get key: https://console.groq.com")
        print("  2. Run: python scripts/save_api_key.py gsk_YOUR_KEY")
        print("  Or add to .env: GROQ_API_KEY=gsk_...")
    else:
        print("\nRun: python main.py")
        print("Web UI: http://localhost:5000")


if __name__ == "__main__":
    main()
