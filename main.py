"""
JARVIS AI Operating System — Entry Point
"""
import sys
import subprocess
import os

# Ensure project root is cwd
ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

from database import create_tables
from core.orchestrator import start_jarvis_thread
import app


def main():
    print("=" * 50)
    print("  JARVIS AI Operating System")
    print("  Voice + Vision + Multi-Agent Desktop AI")
    print("=" * 50)

    create_tables()

    from config import GROQ_API_KEY
    if not GROQ_API_KEY:
        print("\nWARNING: GROQ_API_KEY not set.")
        print("  Set env var GROQ_API_KEY or add key in http://localhost:5000 -> Settings\n")

    start_jarvis_thread()

    from config import SHOW_DESKTOP_WIDGET
    if SHOW_DESKTOP_WIDGET:
        try:
            subprocess.Popen([sys.executable, "widget.py"], cwd=ROOT)
        except Exception as e:
            print(f"Widget skipped: {e}")

    try:
        app.start_flask()
    except KeyboardInterrupt:
        print("\nShutting down JARVIS...")
    finally:
        sys.exit(0)


if __name__ == "__main__":
    main()
