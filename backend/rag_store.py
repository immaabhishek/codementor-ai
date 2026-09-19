import json
import os
import re
import numpy as np
from dotenv import load_dotenv
from google import genai

load_dotenv()

KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(__file__), "knowledge_base")
CACHE_FILE = os.path.join(KNOWLEDGE_BASE_DIR, "vector_index.json")


def cosine_similarity(vec_a, vec_b):
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(vec_a, vec_b) / (norm_a * norm_b))


class RAGEngine:
    def __init__(self):
        self.documents = []
        self.vectors = []
        self.initialized = False
        self.client = None

        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            try:
                self.client = genai.Client(api_key=api_key)
            except Exception as e:
                print("RAG Client init error:", e)

    def load_knowledge_base(self):
        self.documents = []

        files = ["dsa_patterns.json", "language_guidelines.json", "bug_antipatterns.json"]
        for fname in files:
            fpath = os.path.join(KNOWLEDGE_BASE_DIR, fname)
            if os.path.exists(fpath):
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        items = json.load(f)
                        self.documents.extend(items)
                except Exception as e:
                    print(f"Error loading {fname}:", e)

        print(f"RAG Engine loaded {len(self.documents)} knowledge base documents.")

    def _get_doc_text(self, doc):
        parts = [
            doc.get("title", ""),
            doc.get("pattern_description", ""),
            " ".join(doc.get("common_triggers", [])),
            doc.get("rule", ""),
            doc.get("recommendation", "")
        ]
        return " ".join([p for p in parts if p]).strip()

    def build_or_load_index(self):
        self.load_knowledge_base()

        # Try loading cached vectors from file
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    cache_data = json.load(f)
                    if len(cache_data.get("documents", [])) == len(self.documents):
                        self.vectors = cache_data.get("vectors", [])
                        self.initialized = True
                        print("Loaded RAG vector index from cache.")
                        return
            except Exception as e:
                print("Cache load failed, re-embedding:", e)

        # Build embeddings using Gemini if available
        if self.client and len(self.documents) > 0:
            embeddings = []
            try:
                for doc in self.documents:
                    text = self._get_doc_text(doc)
                    res = self.client.models.embed_content(
                        model="gemini-embedding-001",
                        contents=text
                    )
                    # Extract embedding vector float array
                    vec = res.embeddings[0].values
                    embeddings.append(vec)

                self.vectors = embeddings
                self.initialized = True

                # Save cache to disk
                with open(CACHE_FILE, "w", encoding="utf-8") as f:
                    json.dump({
                        "documents": self.documents,
                        "vectors": self.vectors
                    }, f)
                print("Successfully generated and cached RAG vector embeddings.")
                return
            except Exception as e:
                print("Gemini embedding build failed (falling back to keyword matching):", e)

        self.initialized = True

    def query_rag(self, query_code: str, language: str = "", top_k: int = 3):
        if not self.initialized:
            self.build_or_load_index()

        if not self.documents:
            return []

        clean_query = query_code.lower()
        query_words = set(re.findall(r"\w+", clean_query))

        # Try Vector Search if embeddings are present
        if self.vectors and self.client:
            try:
                res = self.client.models.embed_content(
                    model="gemini-embedding-001",
                    contents=query_code[:1000]
                )
                q_vec = np.array(res.embeddings[0].values)

                scores = []
                for idx, doc_vec in enumerate(self.vectors):
                    d_vec = np.array(doc_vec)
                    sim = cosine_similarity(q_vec, d_vec)

                    # Boost score if document matches requested programming language
                    doc_lang = self.documents[idx].get("language", "")
                    if doc_lang and language and doc_lang.lower() == language.lower():
                        sim += 0.15

                    scores.append((sim, idx))

                scores.sort(key=lambda x: x[0], reverse=True)
                top_results = []
                for sim, idx in scores[:top_k]:
                    if sim > 0.1:  # Relevance threshold
                        doc_copy = dict(self.documents[idx])
                        doc_copy["relevance_score"] = round(sim, 3)
                        top_results.append(doc_copy)

                if top_results:
                    return top_results
            except Exception as e:
                print("Vector query failed, falling back to lexical search:", e)

        # Lexical / Keyword Matching Fallback
        lexical_scores = []
        for idx, doc in enumerate(self.documents):
            score = 0
            doc_text = self._get_doc_text(doc).lower()
            triggers = [t.lower() for t in doc.get("common_triggers", [])]

            for word in query_words:
                if word in doc_text:
                    score += 1

            for trigger in triggers:
                if trigger in clean_query:
                    score += 3

            doc_lang = doc.get("language", "")
            if doc_lang and language and doc_lang.lower() == language.lower():
                score += 2

            if score > 0:
                lexical_scores.append((score, idx))

        lexical_scores.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, idx in lexical_scores[:top_k]:
            doc_copy = dict(self.documents[idx])
            doc_copy["relevance_score"] = round(float(score), 2)
            results.append(doc_copy)

        return results


rag_engine = RAGEngine()
