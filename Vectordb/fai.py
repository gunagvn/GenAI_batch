import numpy as np
import faiss

# 1. Suppose these are 5 product embeddings (dimension d = 4)
# In a real system, you would compute these using an embedding model.
d = 4  # vector dimension
vectors = np.array([
    [0.9,  0.1,  0.0,  0.0],  # "Red apple"
    [0.85, 0.15, 0.0,  0.0],  # "Green apple"
    [0.1,  0.9,  0.0,  0.0],  # "Banana fruit"
    [0.0,  0.1,  0.9,  0.1],  # "Fresh orange"
    [0.88, 0.12, 0.1,  0.0],  # "Apple juice"
], dtype='float32')

print("vectors.shape =", vectors.shape)  # (5, 4)

# 2. Create an HNSW index using L2 distance
M = 32  # HNSW parameter: number of neighbors per node in the graph
index = faiss.IndexHNSWFlat(d, M)  # index = faiss.IndexHNSWFlat(d, M=32)

# Optional: tune construction and search parameters
index.hnsw.efConstruction = 40  # trade-off: build time vs quality
index.hnsw.efSearch = 50        # trade-off: query latency vs recall

# 3. Add vectors to the index
index.add(vectors)   # Now the index holds 5 vectors
print("Index total vectors:", index.ntotal)  # should be 5

# 4. Build a query vector for "Apple drink"
# Again, in practice this is an embedding from your model.
query = np.array([[0.88, 0.15, 0.9, 0.0]], dtype='float32')  # shape (1, 4)

# 5. Perform a search: find top-3 nearest neighbors
k = 3
D, I = index.search(query, k)  # D: distances, I: indices in 'vectors'

print("Nearest distances:", D)
print("Nearest indices:", I)