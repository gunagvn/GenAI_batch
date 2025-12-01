import chromadb
from chromadb.utils import embedding_functions

# Connection (from Section 1)
client = chromadb.Client()
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
collection = client.get_or_create_collection(  # Use get_or_create to avoid errors if run multiple times
    name="Books",
    embedding_function=embedding_function
)
collection = client.create_collection(name="books", embedding_function=embedding_function)
collection.add(
    documents=[
        "A detective solves crimes in London.",
        "A romance about two lovers in Paris.",
        "A sci-fi adventure on Mars.",
        "A fantasy tale with dragons and wizards.",
        "A historical novel set in ancient Egypt.",
    ],
    ids=["book1", "book2", "book3","book4", "book5"]
)

# Query
results = collection.query(query_texts=["harry potter"], n_results=1)
print(results)  