import wikipedia
from duckduckgo_search import DDGS
from agents.base_agent import BaseAgent
from core.llm_client import chat, FAST_MODEL


class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__("research_agent")

    def execute(self, action, params):
        try:
            handlers = {
                "search_web": self._search_web,
                "search_wikipedia": self._search_wikipedia,
                "summarize": self._summarize,
                "ask_llm": self._ask_llm,
                "compare": self._compare,
            }
            handler = handlers.get(action)
            if not handler:
                return {"success": False, "message": f"Unknown action: {action}", "data": {}}
            return handler(params)
        except Exception as e:
            return {"success": False, "message": str(e), "data": {}}

    def _search_web(self, params):
        query = params.get("query", "")
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        snippets = [f"{r.get('title', '')}: {r.get('body', '')}" for r in results]
        summary = self._summarize({"text": "\n".join(snippets)})
        return {
            "success": True,
            "message": summary["data"].get("summary", "Search complete"),
            "data": {"results": results, "summary": summary["data"].get("summary")},
        }

    def _search_wikipedia(self, params):
        query = params.get("query", "")
        try:
            summary = wikipedia.summary(query, sentences=3)
            return {"success": True, "message": summary, "data": {"summary": summary}}
        except Exception:
            return {"success": False, "message": "No Wikipedia article found", "data": {}}

    def _summarize(self, params):
        text = params.get("text", "")
        if not text:
            return {"success": False, "message": "No text to summarize", "data": {}}
        summary = chat(
            [
                {"role": "system", "content": "Summarize the following text concisely for voice output."},
                {"role": "user", "content": text[:6000]},
            ],
            model=FAST_MODEL,
            max_tokens=250,
        )
        return {"success": True, "message": summary, "data": {"summary": summary}}

    def _ask_llm(self, params):
        prompt = params.get("prompt", "")
        response = chat(
            [
                {"role": "system", "content": "You are Metis research assistant. Be accurate and concise."},
                {"role": "user", "content": prompt},
            ],
            model=FAST_MODEL,
            max_tokens=400,
        )
        return {"success": True, "message": response, "data": {"response": response}}

    def _compare(self, params):
        topic_a = params.get("a", "")
        topic_b = params.get("b", "")
        response = chat(
            [
                {"role": "system", "content": "Compare the two topics briefly for a voice assistant."},
                {"role": "user", "content": f"Compare {topic_a} vs {topic_b}"},
            ],
            model=FAST_MODEL,
            max_tokens=350,
        )
        return {"success": True, "message": response, "data": {"response": response}}
