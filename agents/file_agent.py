"""File intelligence — search, organize, duplicates."""
import os
import shutil
from agents.base_agent import BaseAgent
from services.file_intel import search_files, find_duplicates


class FileAgent(BaseAgent):
    def __init__(self):
        super().__init__("file_agent")

    def execute(self, action, params):
        try:
            handlers = {
                "search_files": self._search,
                "find_duplicates": self._duplicates,
                "organize_folder": self._organize,
                "index_folder": self._index,
            }
            handler = handlers.get(action)
            if not handler:
                return {"success": False, "message": f"Unknown action: {action}", "data": {}}
            return handler(params)
        except Exception as e:
            return {"success": False, "message": str(e), "data": {}}

    def _search(self, params):
        root = params.get("root", "~")
        query = params.get("query", "")
        matches = search_files(root, query, max_results=int(params.get("limit", 15)))
        if not matches:
            return {"success": True, "message": f"No files matching '{query}' found.", "data": {}}
        msg = f"Found {len(matches)} files: " + "; ".join(os.path.basename(m) for m in matches[:5])
        return {"success": True, "message": msg, "data": {"files": matches}}

    def _duplicates(self, params):
        root = params.get("root", "~")
        dups = find_duplicates(root)
        if not dups:
            return {"success": True, "message": "No duplicate files found.", "data": {}}
        msg = f"Found {len(dups)} duplicate pairs."
        return {"success": True, "message": msg, "data": {"duplicates": dups}}

    def _organize(self, params):
        folder = os.path.expanduser(params.get("path", "~/Downloads"))
        categories = {
            "Images": (".png", ".jpg", ".jpeg", ".gif", ".webp"),
            "Documents": (".pdf", ".docx", ".doc", ".txt", ".xlsx", ".pptx"),
            "Videos": (".mp4", ".avi", ".mkv", ".mov"),
            "Audio": (".mp3", ".wav", ".flac"),
            "Archives": (".zip", ".rar", ".7z"),
        }
        moved = 0
        for fname in os.listdir(folder):
            fpath = os.path.join(folder, fname)
            if not os.path.isfile(fpath):
                continue
            ext = os.path.splitext(fname)[1].lower()
            for cat, exts in categories.items():
                if ext in exts:
                    dest_dir = os.path.join(folder, cat)
                    os.makedirs(dest_dir, exist_ok=True)
                    shutil.move(fpath, os.path.join(dest_dir, fname))
                    moved += 1
                    break
        return {"success": True, "message": f"Organized {moved} files in {folder}", "data": {"moved": moved}}

    def _index(self, params):
        folder = os.path.expanduser(params.get("path", "~"))
        count = sum(len(files) for _, _, files in os.walk(folder))
        return {"success": True, "message": f"Indexed {count} files in {folder}", "data": {"count": count}}
