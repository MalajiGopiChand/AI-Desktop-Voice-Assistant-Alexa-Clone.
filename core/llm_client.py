"""Shared Groq LLM client for all JARVIS modules."""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DEFAULT_MODEL = "llama-3.3-70b-versatile"
FAST_MODEL = "llama-3.1-8b-instant"


def get_api_key():
    from database import get_setting
    from config import GROQ_API_KEY

    key = (
        os.environ.get("GROQ_API_KEY")
        or get_setting("groq_api_key")
        or get_setting("grok_api_key")
        or GROQ_API_KEY
    )
    if not key or key in ("YOUR_GROQ_API_KEY_HERE", ""):
        return None
    return key


def get_groq_client():
    from groq import Groq

    api_key = get_api_key()
    if not api_key:
        raise RuntimeError("Groq API key not configured. Set GROQ_API_KEY or add it in Settings.")
    return Groq(api_key=api_key)


def chat(messages, model=DEFAULT_MODEL, max_tokens=512, temperature=0.2):
    try:
        client = get_groq_client()
    except RuntimeError as e:
        return str(e)
    response = client.chat.completions.create(
        messages=messages,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()
