import chromadb

# Initialize Chroma client (local mode)
chroma_client = chromadb.Client()

# Create a collection
collection = chroma_client.create_collection(name="fruit_collection")

# Step 1: Build dictionary of 100 items (50 A-words, 50 B-words)
data = {}

for i in range(1, 51):
    word = f"apple_{i}"
    data[word] = {
        "color": "red",
        "category": "fruit",
        "biological_name": "Malus domestica",
        "taste": "sweet",
        "index": i
    }

for i in range(1, 51):
    word = f"banana_{i}"
    data[word] = {
        "color": "yellow",
        "category": "fruit",
        "biological_name": "Musa",
        "taste": "sweet",
        "index": i
    }

# Step 2: Add to Chroma collection
for key, meta in data.items():
    collection.add(
        documents=[key],   # the text to embed
        metadatas=[meta],  # metadata dictionary
        ids=[key]          # unique ID
    )

print("✅ Added 100 fruits with metadata to ChromaDB")

# Step 3: Query example
query = "yellow fruit"
results = collection.query(
    query_texts=[query],
    n_results=5  # number of similar items to return
)

print("\n🔍 Query Results for:", query)
for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
    print(f"- {doc}: {meta}")
