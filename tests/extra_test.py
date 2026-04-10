import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src import Document, EmbeddingStore, _mock_embed

from src import Document, EmbeddingStore, _mock_embed

store = EmbeddingStore(collection_name="manual_test", embedding_fn=_mock_embed)

docs = [
    Document("doc1", "Python programming tutorial", {"department": "engineering", "lang": "en"}),
    Document("doc2", "Marketing strategy guide", {"department": "marketing", "lang": "en"}),
    Document("doc3", "Kỹ thuật lập trình Python", {"department": "engineering", "lang": "vi"}),
]

store.add_documents(docs)

print("Size before delete:", store.get_collection_size())

# 1) Test search_with_filter()
results = store.search_with_filter(
    "programming",
    top_k=5,
    metadata_filter={"department": "engineering"}
)

print("\nFiltered search results:")
for r in results:
    print(r)

# 2) Test delete_document()
deleted = store.delete_document("doc1")
print("\nDeleted doc1:", deleted)
print("Size after delete:", store.get_collection_size())

# Optional: verify it is gone
results_after = store.search("Python", top_k=10)
print("\nSearch after delete:")
for r in results_after:
    print(r)