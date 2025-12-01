import chromadb
chroma_client = chromadb.Client()

collection = chroma_client.create_collection(name="fruit_simple")

for key, value in data.items():
    collection.add(
        documents=[value],
        ids=[key]
    )

print("✅ Added 100 documents without metadata")

# Query example
query = "apple"
results = collection.query(
    query_texts=[query],
    n_results=5
)

print("\n🔍 Query Results:")
for doc in results["documents"][0]:
    print("-", doc)
