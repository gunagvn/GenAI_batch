import requests

API_URL = "http://localhost:11434/api/chat"

payload = {
    "model": "llama3",
    "messages": [
        {"role": "user", "content": "Explain RAG in 3 bullet points."}
    ]
}

response = requests.post(API_URL, json=payload)
print(response.json())