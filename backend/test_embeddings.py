from rag.embeddings import create_embedding

text = "What is a nested loop?"

embedding = create_embedding(text)

print("Embedding created!")
print("Number of values:", len(embedding))
print("First 5 values:", embedding[:5])