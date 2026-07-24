"""News — NewsAPI, RSS, or DuckDuckGo news fallback."""
import xml.etree.ElementTree as ET
import requests
from database import get_setting
from config import NEWS_API_KEY

RSS_FEEDS = [
    ("BBC Tech", "https://feeds.bbci.co.uk/news/technology/rss.xml"),
    ("Hacker News", "https://hnrss.org/frontpage"),
]


def get_news_api_key():
    import os
    return os.environ.get("NEWS_API_KEY") or get_setting("news_api_key") or NEWS_API_KEY


def fetch_rss_headlines(limit=5):
    headlines = []
    for source, url in RSS_FEEDS:
        try:
            resp = requests.get(url, timeout=8, headers={"User-Agent": "Metis/1.0"})
            resp.raise_for_status()
            root = ET.fromstring(resp.content)
            count = 0
            for item in root.iter("item"):
                if count >= 2:
                    break
                title = item.find("title")
                if title is not None and title.text:
                    headlines.append(f"[{source}] {title.text.strip()}")
                    count += 1
                if len(headlines) >= limit:
                    return headlines
        except Exception:
            continue
    return headlines


def fetch_ddg_news(query="technology", limit=5):
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.news(query, max_results=limit))
        return [f"{r.get('title', '')} — {r.get('source', '')}" for r in results if r.get("title")]
    except Exception:
        return []


def fetch_newsapi(query="technology", limit=5):
    key = get_news_api_key()
    if not key:
        return None
    url = "https://newsapi.org/v2/top-headlines"
    params = {"q": query, "apiKey": key, "pageSize": limit, "language": "en"}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    articles = resp.json().get("articles", [])
    return [f"{a.get('title', '')} — {a.get('source', {}).get('name', '')}" for a in articles[:limit]]


def get_news(query="technology", limit=5):
    try:
        api_results = fetch_newsapi(query, limit)
        if api_results:
            return api_results, "News from NewsAPI"
    except Exception:
        pass

    headlines = fetch_rss_headlines(limit)
    if headlines:
        return headlines, "Latest headlines from RSS feeds"

    headlines = fetch_ddg_news(query, limit)
    if headlines:
        return headlines, "Latest headlines from web search"

    return [], "No news available. Check your internet connection."
