import sqlite3
import numpy as np

# ------------------------------
# CREATE SQLITE IN-MEMORY DB
# ------------------------------
conn = sqlite3.connect(":memory:")

conn.execute("""
CREATE TABLE books_vectors (
    id        INTEGER PRIMARY KEY,
    title     TEXT NOT NULL,
    embedding BLOB NOT NULL
);
""")

# Helper to create fake vector embeddings
def make_vec(value: float) -> bytes:
    return np.array([value] * 384, dtype=np.float32).tobytes()

# Insert sample book vectors
conn.executemany(
    "INSERT INTO books_vectors (id, title, embedding) VALUES (?, ?, ?)",
    [
        (1, "Book 1: Intro to AI",       make_vec(0.10)),
        (2, "Book 2: Cooking with Love", make_vec(0.80)),
        (3, "Book 3: Machine Learning",  make_vec(0.14)),
    ],
)
conn.commit()

# ------------------------------
# FAKE TEXT EMBEDDING FUNCTION
# ------------------------------
def fake_text_embedding(text: str) -> np.ndarray:
    """Return a query vector (close to book 1 + 3)."""
    return np.array([0.15] * 384, dtype=np.float32)

query_text = input("Enter your search text: ")
query_emb = fake_text_embedding(query_text)

# ------------------------------
# PURE PYTHON VECTOR SEARCH
# ------------------------------
def cosine_similarity(a, b):
    """Compute cosine similarity between two vectors."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Load all vectors from SQLite
cur = conn.execute("SELECT id, title, embedding FROM books_vectors")
rows = cur.fetchall()

results = []

for row in rows:
    book_id, title, blob = row
    vec = np.frombuffer(blob, dtype=np.float32)

    score = cosine_similarity(query_emb, vec)
    results.append((score, book_id, title))

# Sort by highest cosine similarity
results.sort(reverse=True)

# Top-2 matches
top_k = results[:2]

print("\nTop-2 similar books:")
for score, book_id, title in top_k:
    print(f"{book_id}: {title} (similarity={score:.4f})")