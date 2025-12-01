"""
sqlite_embeddings_search.py
- computes embeddings using sentence-transformers (all-MiniLM-L6-v2)
- stores each document text + embedding as BLOB in SQLite
- performs a semantic search by computing cosine similarity in Python
"""

import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer

# -------------------------
# 1) Documents (your data)
# -------------------------
student_info = """
Alexandra Thompson, a 19-year-old computer science sophomore with a 3.7 GPA,
is a member of the programming and chess clubs who enjoys pizza, swimming, and hiking
in her free time in hopes of working at a tech company after graduating from the University of Washington.
"""

club_info = """
The university chess club provides an outlet for students to come together and enjoy playing
the classic strategy game of chess. Members of all skill levels are welcome, from beginners learning
the rules to experienced tournament players. The club typically meets a few times per week to play casual games,
participate in tournaments, analyze famous chess matches, and improve members' skills.
"""

university_info = """
The University of Washington, founded in 1861 in Seattle, is a public research university
with over 45,000 students across three campuses in Seattle, Tacoma, and Bothell.
As the flagship institution of the six public universities in Washington state,
UW encompasses over 500 buildings and 20 million square feet of space,
including one of the largest library systems in the world.
"""

docs = [
    ("student_info", student_info.strip()),
    ("club_info", club_info.strip()),
    ("university_info", university_info.strip()),
]

# -------------------------
# 2) Create SQLite DB
# -------------------------
# Using a file DB so it persists between runs; change ":memory:" if you want temp DB
conn = sqlite3.connect("kb_embeddings.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    text TEXT,
    embedding BLOB
);
""")
conn.commit()

# -------------------------
# 3) Load embedding model
# -------------------------
print("Loading embedding model (this may take a while)...")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
# model returns numpy arrays of dtype float32

# -------------------------
# 4) Insert docs + embeddings
# -------------------------
def embed_to_blob(vec: np.ndarray) -> bytes:
    """
    Convert a float32 numpy vector into bytes to store as BLOB.
    We'll store raw float32 bytes and on read convert back with np.frombuffer.
    """
    # ensure float32 contiguous
    arr = np.asarray(vec, dtype=np.float32)
    return arr.tobytes()

# Insert (or skip if already present)
for name, text in docs:
    # check if already inserted to avoid duplicates
    cur.execute("SELECT id FROM documents WHERE name = ?", (name,))
    if cur.fetchone():
        print(f"{name} already exists — skipping insertion.")
        continue

    emb = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)  # normalized
    blob = embed_to_blob(emb)
    cur.execute(
        "INSERT INTO documents (name, text, embedding) VALUES (?, ?, ?)",
        (name, text, blob)
    )
    print(f"Inserted {name} (embedding dim {emb.shape})")
conn.commit()

# -------------------------
# 5) Semantic search helper
# -------------------------
def blob_to_vec(blob: bytes) -> np.ndarray:
    # convert raw float32 bytes back to numpy array
    arr = np.frombuffer(blob, dtype=np.float32)
    # ensure normalized (we stored normalized vectors above)
    return arr

def semantic_search(query: str, top_k: int = 3):
    q_emb = model.encode(query, convert_to_numpy=True, normalize_embeddings=True)
    # read all doc embeddings
    cur.execute("SELECT id, name, text, embedding FROM documents")
    rows = cur.fetchall()

    sims = []
    for doc_id, name, text, emb_blob in rows:
        doc_vec = blob_to_vec(emb_blob)
        # cosine similarity since vectors are normalized -> dot product equals cosine
        score = float(np.dot(q_emb, doc_vec))
        sims.append((score, doc_id, name, text))

    # sort by descending similarity
    sims.sort(key=lambda x: x[0], reverse=True)
    return sims[:top_k]

# -------------------------
# 6) Test interactive queries
# -------------------------
if __name__ == "__main__":
    while True:
        q = input("\nEnter query (or 'exit'): ").strip()
        if q.lower() in ("exit", "quit"):
            break
        results = semantic_search(q, top_k=3)
        if not results:
            print("No documents.")
            continue
        print("\nTop results (score, name):")
        for score, doc_id, name, text in results:
            print(f"{score:.4f}  — {name} (id={doc_id})")
            # optionally show excerpt
            snippet = text[:300].replace("\n", " ")
            print("   ", snippet)
