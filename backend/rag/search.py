import faiss
import json
import numpy as np

from rag.embeddings import create_embedding


index = faiss.read_index("rag/vector_store.index")

with open("rag/metadata.json", "r", encoding="utf-8") as file:
    metadata = json.load(file)

def search_knowledge(query, top_k=2):
    top_k = min(top_k, index.ntotal)

    query_vector = create_embedding(query)
    query_vector = np.array([query_vector], dtype="float32")

    distances, indices = index.search(query_vector, top_k)

    results = []

    for idx in indices[0]:
        if idx >= 0:
            results.append(metadata[idx]["content"])

    return results