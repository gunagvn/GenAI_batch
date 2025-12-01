import chromadb
from chromadb.utils import embedding_functions

# Connect to Chroma
client = chromadb.Client()

embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = client.get_or_create_collection(
    name="books",
    embedding_function=embedding_function
)

# Add data only if empty
if collection.count() == 0:
    collection.add(
        documents=[
            "A detective solves crimes in London.",
            "A romance about two lovers in Paris.",
            "A sci-fi adventure on Mars.",
            "A fantasy tale with dragons and wizards.",
            "A historical novel set in ancient Egypt."
        ],
        ids=["book1", "book2", "book3", "book4", "book5"]
    )

# Take user input
query = input("Enter a keyword or phrase: ")

# Query collection
results = collection.query(query_texts=[query], n_results=5)

docs = results["documents"][0]
distances = results["distances"][0]  # smaller = better

# Convert to similarity percentages
max_d = max(distances)
min_d = min(distances)
similarities = [100 - ((d - min_d) / (max_d - min_d + 1e-9)) * 100 for d in distances]

# Convert similarity → token temperature scale (inverse relationship)
# Higher similarity → lower temperature (more confident)
temperatures = [round((1 - (s / 100)) * 1.0, 2) for s in similarities]  # range 0.0–1.0

# Combine and sort results
combined = sorted(zip(docs, similarities, temperatures), key=lambda x: x[1], reverse=True)

# Print formatted results
print("\n📚 Most Related Books with Token-like Temperatures:\n")
for i, (doc, sim, temp) in enumerate(combined, start=1):
    print(f"{i}. {doc} — {sim:.2f}% (temperature={temp:.2f})")
