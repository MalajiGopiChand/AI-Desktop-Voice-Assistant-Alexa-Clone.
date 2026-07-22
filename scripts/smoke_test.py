"""Smoke tests — run without microphone: python scripts/smoke_test.py"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

from database import create_tables
from config import GROQ_API_KEY


def test_imports():
    from core.command_processor import processor
    assert len(processor.agents) == 15
    print("[OK] 15 agents loaded")


def test_simple_commands():
    from core.command_processor import processor
    r = processor.process("what time is it")
    assert r and "time" in r.lower()
    print(f"[OK] time: {r[:60]}")

    r = processor.process("system info")
    assert "cpu" in r.lower() or "ram" in r.lower()
    print(f"[OK] system info: {r[:60]}")


def test_math():
    from core.command_processor import processor
    r = processor.process("calculate 2 + 2")
    assert "4" in r
    print(f"[OK] math: {r}")


def test_news():
    from core.command_processor import processor
    r = processor.process("news headlines")
    assert r
    print(f"[OK] news: {r[:80]}...")


def test_groq():
    if not GROQ_API_KEY:
        print("[SKIP] Groq API key not set — add in Settings or GROQ_API_KEY env")
        return
    from core.command_processor import processor
    r = processor.process("who are you")
    assert r
    print(f"[OK] groq chat: {r[:80]}...")


def main():
    print("JARVIS Smoke Test")
    print("=" * 40)
    create_tables()
    test_imports()
    test_simple_commands()
    test_math()
    test_news()
    test_groq()
    print("=" * 40)
    print("Done.")


if __name__ == "__main__":
    main()
