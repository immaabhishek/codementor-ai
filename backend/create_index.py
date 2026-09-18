import faiss
import numpy as np
import json

from rag.knowledge_base import load_documents
from rag.chunker import split_text
from rag.embeddings import create_embedding


documents = load_documents()

embeddings = []
metadata = []

for document in documents:
    chunks = split_text(document["content"])

    for chunk in chunks:
        vector = create_embedding(chunk)

        embeddings.append(vector)
        metadata.append({
            "source": document["source"],
            "content": chunk
        })


matrix = np.array(embeddings, dtype="float32")

index = faiss.IndexFlatL2(matrix.shape[1])
index.add(matrix)

faiss.write_index(index, "rag/vector_store.index")

with open("rag/metadata.json", "w", encoding="utf-8") as file:
    json.dump(metadata, file, indent=2)

print("Vector index created!")
print("Total vectors:", index.ntotal)