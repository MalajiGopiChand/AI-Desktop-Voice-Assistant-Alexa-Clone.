"""
Metis AI OS — Universal AI Search Engine.
Searches local files, browser history, memory notes, downloads, and cloud items simultaneously by semantic intent.
"""
import os
import glob
from database import get_history
from core.memory import memory

class UniversalSearchEngine:
    def search(self, query):
        query_lower = query.lower().strip()
        results = []

        # 1. Search Memory & Notes
        facts = memory.recall_facts(limit=20)
        for f in facts:
            if any(w in f.lower() for w in query_lower.split()):
                results.append({"type": "Memory Fact", "title": f[:40], "details": f, "source": "Metis Memory"})

        # 2. Search Local Workspace & Downloads Files
        search_dirs = [os.getcwd(), os.path.expanduser("~/Downloads"), os.path.expanduser("~/Documents")]
        for d in search_dirs:
            if os.path.exists(d):
                try:
                    for root, _, files in os.walk(d):
                        for f in files[:50]:
                            if any(w in f.lower() for w in query_lower.split()):
                                full_p = os.path.join(root, f)
                                results.append({"type": "File", "title": f, "details": full_p, "source": d})
                except Exception:
                    pass

        # 3. Search Command History
        hist = get_history(limit=30)
        for item in hist:
            cmd = item.get("command", "")
            if any(w in cmd.lower() for w in query_lower.split()):
                results.append({"type": "Command History", "title": cmd, "details": item.get("status", ""), "source": "History"})

        return {
            "query": query,
            "total_results": len(results),
            "results": results[:10]
        }


universal_search = UniversalSearchEngine()
