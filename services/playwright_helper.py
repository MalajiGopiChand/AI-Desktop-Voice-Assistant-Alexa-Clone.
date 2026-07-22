"""Playwright browser automation — optional; falls back if not installed."""
import threading

_lock = threading.Lock()
_instance = None


class PlaywrightHelper:
    def __init__(self):
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
        self._error = None

    @classmethod
    def get(cls):
        global _instance
        with _lock:
            if _instance is None:
                _instance = cls()
            return _instance

    def _ensure(self):
        if self._page:
            return self._page
        if self._error:
            raise RuntimeError(self._error)
        try:
            from playwright.sync_api import sync_playwright
            from config import CHROME_USER_DATA

            self._playwright = sync_playwright().start()
            if CHROME_USER_DATA:
                self._context = self._playwright.chromium.launch_persistent_context(
                    CHROME_USER_DATA, headless=False
                )
                self._page = (
                    self._context.pages[0] if self._context.pages else self._context.new_page()
                )
            else:
                self._browser = self._playwright.chromium.launch(headless=False)
                self._context = self._browser.new_context()
                self._page = self._context.new_page()
            return self._page
        except Exception as e:
            self._error = str(e)
            raise RuntimeError(
                f"Playwright unavailable: {e}. Run: pip install playwright && playwright install chromium"
            ) from e

    def navigate(self, url):
        page = self._ensure()
        if not url.startswith("http"):
            url = "https://" + url
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        return page.title()

    def search_google(self, query):
        page = self._ensure()
        page.goto("https://www.google.com", wait_until="domcontentloaded")
        page.fill('textarea[name="q"], input[name="q"]', query)
        page.keyboard.press("Enter")
        page.wait_for_load_state("domcontentloaded")
        return page.title()

    def click_first_result(self):
        page = self._ensure()
        link = page.locator("#search a h3").first
        if link.count() > 0:
            link.click()
            page.wait_for_load_state("domcontentloaded")
            return page.url
        return None

    def get_page_text(self, max_chars=5000):
        page = self._ensure()
        text = page.inner_text("body")
        return " ".join(text.split())[:max_chars]

    def fill_and_submit(self, selector, value, submit_selector=None):
        page = self._ensure()
        page.fill(selector, value)
        if submit_selector:
            page.click(submit_selector)
        else:
            page.keyboard.press("Enter")

    def screenshot(self, path):
        page = self._ensure()
        page.screenshot(path=path)
        return path

    def close(self):
        try:
            if self._context:
                self._context.close()
            if self._browser:
                self._browser.close()
            if self._playwright:
                self._playwright.stop()
        except Exception:
            pass
        self._page = None
