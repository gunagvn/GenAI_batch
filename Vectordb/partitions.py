import math
from typing import List, Dict, Any, Optional


class VectorCollection:
    """
    A simple in-memory vector collection with NAMED partitions.

    partitions = {
        partition_name (str): {
            vector_id (str): {
                "vector": [...],
                "metadata": {...}
            }
        }
    }
    """

    def __init__(
        self,
        name: str,
        dim: int,
        partition_names: Optional[List[str]] = None,
        default_num_partitions: int = 2
    ):
        self.name = name
        self.dim = dim

        # If user provides custom partition names → use them
        if partition_names:
            self.partition_names = partition_names
        else:
            # Generate generic default partition names
            self.partition_names = [f"partition_{i}" for i in range(default_num_partitions)]

        # Partition structure: name → vector-store
        self.partitions: Dict[str, Dict[str, Dict[str, Any]]] = {
            pname: {} for pname in self.partition_names
        }

    # --------------------------------------------------
    # Helper Methods
    # --------------------------------------------------

    def _validate_vector(self, vector: List[float]) -> None:
        """Ensure vector has correct dimension."""
        if len(vector) != self.dim:
            raise ValueError(
                f"Vector dimension mismatch. Expected {self.dim}, got {len(vector)}"
            )

    def _choose_partition_automatically(self, vector_id: str) -> str:
        """Hash-based partition selection."""
        idx = hash(vector_id) % len(self.partition_names)
        return self.partition_names[idx]

    # --------------------------------------------------
    # Core Operations
    # --------------------------------------------------

    def upsert_vector(
        self,
        vector_id: str,
        vector: List[float],
        metadata: Dict[str, Any],
        partition_name: Optional[str] = None
    ):
        """
        UPSERT a vector:

        - If vector_id already exists → update in its current partition.
        - Else:
            * If partition_name is provided → insert there.
            * If not provided → auto-select partition.

        """
        self._validate_vector(vector)

        # 1. Check if vector ID already exists → update
        for p_name, store in self.partitions.items():
            if vector_id in store:
                store[vector_id]["vector"] = vector
                store[vector_id]["metadata"] = metadata
                print(f"[UPSERT] Updated '{vector_id}' in partition '{p_name}'")
                return

        # 2. Insert into a partition
        if partition_name:
            if partition_name not in self.partitions:
                raise ValueError(
                    f"Partition '{partition_name}' does not exist. "
                    f"Available: {list(self.partitions.keys())}"
                )
            target_partition = partition_name
        else:
            target_partition = self._choose_partition_automatically(vector_id)

        self.partitions[target_partition][vector_id] = {
            "vector": vector,
            "metadata": metadata
        }
        print(f"[UPSERT] Inserted '{vector_id}' into '{target_partition}'")

    def get_vector(self, vector_id: str):
        """Return (partition_name, record) or (None, None)."""
        for p_name, store in self.partitions.items():
            if vector_id in store:
                return p_name, store[vector_id]
        return None, None

    def get_partition(self, partition_name: str):
        """Return raw dictionary of a partition."""
        if partition_name not in self.partitions:
            raise ValueError(
                f"Partition '{partition_name}' does not exist. "
                f"Available: {list(self.partitions.keys())}"
            )
        return self.partitions[partition_name]

    def print_collection_summary(self):
        """Show number of vectors per partition."""
        print(f"\n=== Collection Summary: '{self.name}' ===")
        total = 0
        for p_name, store in self.partitions.items():
            count = len(store)
            total += count
            print(f"  {p_name}: {count} vectors")
        print(f"  TOTAL: {total} vectors\n")

    def search_in_partition(
        self,
        partition_name: str,
        query_vector: List[float],
        top_k: int = 3
    ):
        """Brute-force L2 search inside one partition."""
        self._validate_vector(query_vector)

        if partition_name not in self.partitions:
            raise ValueError(
                f"Partition '{partition_name}' does not exist. "
                f"Available: {list(self.partitions.keys())}"
            )

        store = self.partitions[partition_name]
        results = []

        for vec_id, record in store.items():
            dist = math.dist(query_vector, record["vector"])
            results.append((vec_id, dist))

        results.sort(key=lambda x: x[1])
        return results[:top_k]


# -------------------------------------------------------------
# DEMO (Ready to run)
# -------------------------------------------------------------
if __name__ == "__main__":

    # Create collection with named partitions
    collection = VectorCollection(
        name="products",
        dim=4,
        partition_names=["fruits", "juices", "others"]
    )

    # Insert vectors
    collection.upsert_vector(
        vector_id="p1",
        vector=[0.9, 0.1, 0.0, 0.0],
        metadata={"name": "Red apple"},
        partition_name="fruits"
    )

    collection.upsert_vector(
        vector_id="p2",
        vector=[0.85, 0.15, 0.0, 0.0],
        metadata={"name": "Green apple"},
        partition_name="fruits"
    )

    collection.upsert_vector(
        vector_id="p3",
        vector=[0.0, 0.1, 0.9, 0.1],
        metadata={"name": "Orange juice"},
        partition_name="juices"
    )

    collection.upsert_vector(
        vector_id="p4",
        vector=[0.1, 0.9, 0.0, 0.0],
        metadata={"name": "Banana"}  # auto-placed partition
    )

    # Summary
    collection.print_collection_summary()

    # Check contents of fruits partition
    fruits = collection.get_partition("fruits")
    print("Contents of 'fruits' partition:")
    for vid, rec in fruits.items():
        print(f"  {vid}: {rec['metadata']['name']}")

    print()

    # Query search example
    query = [0.88, 0.12, 0.0, 0.0]  # similar to apple
    results = collection.search_in_partition("fruits", query, top_k=2)

    print("Top-2 nearest neighbors in 'fruits':")
    for vid, dist in results:
        _, rec = collection.get_vector(vid)
        print(f"  {vid}: {rec['metadata']['name']} (dist={dist:.4f})")
