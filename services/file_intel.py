"""File search and indexing utilities."""
import os
from pathlib import Path


def search_files(root, query, max_results=20):
    root = os.path.expanduser(root or "~")
    query = query.lower()
    matches = []
    for dirpath, _, filenames in os.walk(root):
        if any(skip in dirpath for skip in (".git", "node_modules", "__pycache__", "AppData")):
            continue
        for name in filenames:
            if query in name.lower():
                matches.append(os.path.join(dirpath, name))
                if len(matches) >= max_results:
                    return matches
    return matches


def find_duplicates(root, max_files=500):
    import hashlib
    seen = {}
    duplicates = []
    count = 0
    for dirpath, _, filenames in os.walk(os.path.expanduser(root or "~")):
        for name in filenames:
            path = os.path.join(dirpath, name)
            try:
                h = hashlib.md5(open(path, "rb").read(65536)).hexdigest()
                if h in seen:
                    duplicates.append((seen[h], path))
                else:
                    seen[h] = path
            except OSError:
                continue
            count += 1
            if count >= max_files:
                return duplicates
    return duplicates
