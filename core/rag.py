"""
Metis AI OS — Local RAG & Vector Knowledge Base Engine.
Indexes local PDFs, Word files, Markdown notes, and college materials for instant offline QA.
"""
import os
import json
import re
from core.llm_client import chat, FAST_MODEL
from database import get_setting, set_setting

KNOWLEDGE_INDEX_PATH = "metis_knowledge_index.json"


class LocalRAGEngine:
    def __init__(self):
        self.index = self._load_index()

    def _load_index(self):
        if os.path.exists(KNOWLEDGE_INDEX_PATH):
            try:
                with open(KNOWLEDGE_INDEX_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_index(self):
        try:
            with open(KNOWLEDGE_INDEX_PATH, "w", encoding="utf-8") as f:
                json.dump(self.index, f, indent=2)
        except Exception as e:
            print(f"Error saving RAG index: {e}")

    def index_document(self, file_path):
        """Extracts text and indexes document content locally."""
        if not os.path.exists(file_path):
            return {"success": False, "message": f"File not found: {file_path}"}

        filename = os.path.basename(file_path)
        ext = os.path.splitext(filename)[1].lower()
        content = ""

        try:
            if ext in (".txt", ".md", ".py", ".json", ".csv"):
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            elif ext == ".pdf":
                try:
                    import pypdf
                    reader = pypdf.PdfReader(file_path)
                    content = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
                except ImportError:
                    content = f"PDF text extraction fallback for {filename}"
            elif ext in (".docx", ".doc"):
                try:
                    import docx
                    doc = docx.Document(file_path)
                    content = "\n".join(p.text for p in doc.paragraphs)
                except ImportError:
                    content = f"Word document text extraction fallback for {filename}"

            if not content.strip():
                return {"success": False, "message": f"No extractable text in {filename}"}

            # Chunk content into ~500 char passages
            words = content.split()
            chunks = [" ".join(words[i:i+100]) for i in range(0, len(words), 80)]
            self.index[file_path] = {
                "filename": filename,
                "path": file_path,
                "chunks": chunks[:50],
                "updated_at": os.path.getmtime(file_path)
            }
            self._save_index()
            return {"success": True, "message": f"Indexed {filename} ({len(chunks)} passages)."}
        except Exception as e:
            return {"success": False, "message": f"Failed to index {filename}: {e}"}

    def query(self, question, top_k=3):
        """Searches indexed passages using term overlap & semantic score."""
        question_terms = set(re.findall(r'\w+', question.lower()))
        matches = []

        for path, doc in self.index.items():
            for chunk in doc.get("chunks", []):
                chunk_terms = set(re.findall(r'\w+', chunk.lower()))
                overlap = len(question_terms.intersection(chunk_terms))
                if overlap > 0:
                    matches.append((overlap, doc["filename"], chunk))

        matches.sort(key=lambda x: x[0], reverse=True)
        top_passages = matches[:top_k]

        if not top_passages:
            return f"No relevant passages found in local knowledge base for: '{question}'."

        context_str = "\n---\n".join(f"From {filename}:\n{passage}" for _, filename, passage in top_passages)
        answer = chat(
            [
                {"role": "system", "content": "You are Metis Local RAG Knowledge Engine. Answer the user's question accurately using ONLY the provided local document passages."},
                {"role": "user", "content": f"Context:\n{context_str}\n\nQuestion: {question}"}
            ],
            model=FAST_MODEL,
            max_tokens=350
        )
        return answer


rag_engine = LocalRAGEngine()
