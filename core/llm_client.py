"""Shared Multi-Provider LLM Client for JARVIS (Groq + Mistral AI)."""
import os
import sys
import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
FAST_GROQ_MODEL = "llama-3.1-8b-instant"

DEFAULT_MISTRAL_MODEL = "mistral-large-latest"
FAST_MISTRAL_MODEL = "mistral-small-latest"

DEFAULT_MODEL = DEFAULT_GROQ_MODEL
FAST_MODEL = FAST_GROQ_MODEL


def get_groq_api_key():
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


def get_mistral_api_key():
    from database import get_setting
    from config import MISTRAL_API_KEY

    key = (
        os.environ.get("MISTRAL_API_KEY")
        or get_setting("mistral_api_key")
        or MISTRAL_API_KEY
    )
    if not key or key in ("YOUR_MISTRAL_API_KEY_HERE", ""):
        return None
    return key


def get_api_key():
    return get_groq_api_key() or get_mistral_api_key()


def get_groq_client():
    from groq import Groq

    api_key = get_groq_api_key()
    if not api_key:
        raise RuntimeError("Groq API key not configured. Set GROQ_API_KEY or add it in Settings.")
    return Groq(api_key=api_key)


def get_mistral_client():
    api_key = get_mistral_api_key()
    if not api_key:
        raise RuntimeError("Mistral API key not configured. Set MISTRAL_API_KEY or add it in Settings.")
    try:
        from mistralai.client import Mistral
        return Mistral(api_key=api_key)
    except Exception:
        return None


def chat_groq(messages, model=DEFAULT_GROQ_MODEL, max_tokens=512, temperature=0.2):
    client = get_groq_client()
    response = client.chat.completions.create(
        messages=messages,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


def chat_mistral(messages, model=DEFAULT_MISTRAL_MODEL, max_tokens=512, temperature=0.2):
    api_key = get_mistral_api_key()
    if not api_key:
        raise RuntimeError("Mistral API key not configured.")

    # Primary: SDK client
    client = get_mistral_client()
    if client:
        try:
            response = client.chat.complete(
                model=model,
                messages=messages,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Mistral SDK call failed, using HTTP API fallback: {e}")

    # Fallback: HTTP REST API
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    res = requests.post(url, headers=headers, json=payload, timeout=30)
    res.raise_for_status()
    data = res.json()
    return data["choices"][0]["message"]["content"].strip()


def chat(messages, model=None, max_tokens=512, temperature=0.2):
    selected_model = model or DEFAULT_MODEL

    # Determine provider by model name
    is_mistral_model = any(m in selected_model.lower() for m in ("mistral", "pixtral", "codestral"))

    if is_mistral_model:
        try:
            return chat_mistral(messages, model=selected_model, max_tokens=max_tokens, temperature=temperature)
        except Exception as e:
            print(f"Mistral LLM Error: {e}, falling back to Groq...")
            if get_groq_api_key():
                return chat_groq(messages, model=DEFAULT_GROQ_MODEL, max_tokens=max_tokens, temperature=temperature)
            return f"Mistral API Error: {e}"

    # Default Groq provider
    try:
        return chat_groq(messages, model=selected_model, max_tokens=max_tokens, temperature=temperature)
    except Exception as e:
        print(f"Groq LLM Error: {e}")
        if get_mistral_api_key():
            try:
                print("Falling back to Mistral AI...")
                return chat_mistral(messages, model=DEFAULT_MISTRAL_MODEL, max_tokens=max_tokens, temperature=temperature)
            except Exception as m_err:
                return f"LLM Error (Groq: {e}, Mistral: {m_err})"
        return str(e)
