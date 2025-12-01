import json
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from openai import OpenAI

HF_TOKEN = "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"

# ================
#  HF LLM CLIENT
# ================
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN    # <<< 🔴 VERY IMPORTANT
)

# ==========================
#  FUNCTION: GENERATE METADATA
# ==========================
def generate_metadata(letter: str, word: str):
    prompt = f"""
    Generate detailed metadata for the item below.

    Alphabet: {letter}
    Word: {word}

    Return only JSON with these exact fields:
    {{
        "alphabet": "",
        "type": "",
        "category": "",
        "color": "",
        "is_living": "",
        "origin_country": "",
        "description": ""
    }}
    }}"""
    

    response = client.chat.completions.create(
        model="Qwen/Qwen2.5-7B-Instruct", 
        messages=[{"role": "user", "content": prompt}],
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except:
        # If JSON fails, fallback
        print("⚠ Warning: Model returned invalid JSON. Raw:", content)
        return {"alphabet": letter, "description": content}


# =====================
#  SETUP CHROMA CLIENT
# =====================
chroma_client = chromadb.Client(
    Settings(persist_directory="./chroma_ai_store")
)

# Embedding function needed for proper search
embedder = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

collection = chroma_client.get_or_create_collection(
    name="dictionary_ai",
    embedding_function=embedder
)

# ======================
#  READ THE TEXT FILE
# ======================
records = []

print("\n📖 Reading data.txt ...")

with open("datas.txt", "r") as f:
    for line in f:
        if ":" in line:
            letter, word = line.split(":")
            letter = letter.strip()
            word = word.strip()
            records.append((letter, word))

print(f"✔ Loaded {len(records)} records.")


# ============================
#  PROCESS + STORE IN CHROMA
# ============================
ids = []
documents = []
metadatas = []

print("\n⚙ Generating metadata and storing in Chroma...\n")

for i, (letter, word) in enumerate(records):
    print(f"Processing '{word}' ...")

    meta = generate_metadata(letter, word)

    ids.append(str(i))
    documents.append(word)
    metadatas.append(meta)

# Add to collection
collection.add(
    ids=ids,
    documents=documents,
    metadatas=metadatas
)

# Save to disk
# chroma_client.persist()

print("\n🎉 ALL DATA STORED SUCCESSFULLY IN chroma_ai_store/")
print("--------------------------------------------------------")


# ============================
#  TEST QUERY
# ============================
print("\n🔎 Testing semantic search: searching for 'fruit'...\n")

results = collection.query(
    query_texts=["A"],
    # where={'color':'red' },
    n_results=3
)

print(results)
print("\n✅ Done.\n")


