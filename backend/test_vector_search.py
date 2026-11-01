
from app.services.vector_store import add_chunks, search_chunks


chunks = [
    {
        "chunk_id": 1,
        "page_number": 1,
        "text": "The client must pay invoices within fifteen calendar days.",
    },
    {
        "chunk_id": 2,
        "page_number": 2,
        "text": "Either party may terminate the agreement after written notice.",
    },
    {
        "chunk_id": 3,
        "page_number": 3,
        "text": "The provider must protect confidential information.",
    },
]

count = add_chunks(chunks)
print(f"Indexed chunks: {count}")

results = search_chunks("When does the customer need to pay?", top_k=2)

for result in results:
    print(f"\nPage: {result['page_number']}")
    print(f"Text: {result['text']}")
    print(f"Similarity: {result['similarity_score']:.4f}")

assert results, "Expected at least one search result"
assert results[0]["chunk_id"] == 1, "Payment clause should rank first"

print("\nSemantic search test passed!")
