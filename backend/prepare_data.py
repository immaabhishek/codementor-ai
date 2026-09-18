from rag.knowledge_base import load_documents
from rag.chunker import split_text


documents = load_documents()

for document in documents:
    chunks = split_text(document["content"])

    print("Source:", document["source"])
    print("Number of chunks:", len(chunks))
    print("First chunk:", chunks[0])