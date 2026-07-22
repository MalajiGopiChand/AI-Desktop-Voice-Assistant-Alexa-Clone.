import urllib.parse
import webbrowser
import requests
from bs4 import BeautifulSoup
from agents.base_agent import BaseAgent
from config import USE_PLAYWRIGHT


class BrowserAgent(BaseAgent):
    def __init__(self):
        super().__init__("browser_agent")

    def execute(self, action, params):
        try:
            handlers = {
                "open_url": self._open_url,
                "search": self._search,
                "read_page": self._read_page,
                "open_with_profile": self._open_with_profile,
                "automate_search": self._automate_search,
                "automate_navigate": self._automate_navigate,
                "automate_read": self._automate_read,
                "automate_fill_form": self._automate_fill_form,
                "extract_text": self._read_page,
            }
            handler = handlers.get(action)
            if not handler:
                return {"success": False, "message": f"Unknown action: {action}", "data": {}}
            return handler(params)
        except Exception as e:
            return {"success": False, "message": str(e), "data": {}}

    def _pw(self):
        from services.playwright_helper import PlaywrightHelper
        return PlaywrightHelper.get()

    def _open_url(self, params):
        url = params.get("url", "")
        if USE_PLAYWRIGHT:
            try:
                title = self._pw().navigate(url)
                return {"success": True, "message": f"Opened {title}", "data": {"url": url}}
            except Exception:
                pass
        if not url.startswith("http"):
            url = "https://" + url
        webbrowser.open(url)
        return {"success": True, "message": f"Opened {url}", "data": {"url": url}}

    def _search(self, params):
        query = params.get("query", "")
        if USE_PLAYWRIGHT:
            try:
                title = self._pw().search_google(query)
                return {"success": True, "message": f"Searched: {title}", "data": {"query": query}}
            except Exception:
                pass
        engine = params.get("engine", "google")
        if engine == "youtube":
            url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        else:
            url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        webbrowser.open(url)
        return {"success": True, "message": f"Searched for {query}", "data": {"query": query}}

    def _automate_search(self, params):
        query = params.get("query", "")
        pw = self._pw()
        pw.search_google(query)
        url = pw.click_first_result()
        msg = f"Searched {query} and opened {url}" if url else f"Searched for {query}"
        return {"success": True, "message": msg, "data": {"url": url}}

    def _automate_navigate(self, params):
        url = params.get("url", "")
        title = self._pw().navigate(url)
        return {"success": True, "message": f"Navigated to {title}", "data": {"url": url}}

    def _automate_read(self, params):
        text = self._pw().get_page_text()
        from core.llm_client import chat, FAST_MODEL
        summary = chat(
            [{"role": "system", "content": "Summarize this web page for voice output."},
             {"role": "user", "content": text[:5000]}],
            model=FAST_MODEL, max_tokens=250,
        )
        return {"success": True, "message": summary, "data": {"text": text, "summary": summary}}

    def _automate_fill_form(self, params):
        selector = params.get("selector", "input")
        value = params.get("value", "")
        self._pw().fill_and_submit(selector, value, params.get("submit_selector"))
        return {"success": True, "message": "Form filled", "data": {}}

    def _open_with_profile(self, params):
        import os
        profile = params.get("profile", "Default")
        url = params.get("url", "")
        cmd = f'start chrome --profile-directory="{profile}"'
        if url:
            cmd += f' "{url}"'
        os.system(cmd)
        return {"success": True, "message": f"Opened Chrome profile {profile}", "data": {}}

    def _read_page(self, params):
        url = params.get("url", "")
        if USE_PLAYWRIGHT and not url:
            return self._automate_read(params)
        if not url.startswith("http"):
            url = "https://" + url
        headers = {"User-Agent": "Mozilla/5.0 (JARVIS Bot)"}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = " ".join(soup.get_text(separator=" ").split())[:4000]
        return {"success": True, "message": "Page read", "data": {"text": text, "url": url}}
