from rag.search import search_knowledge

query = "What is a nested loop?"

results = search_knowledge(query)

for result in results:
    print("\n--- Result ---")
    print(result)