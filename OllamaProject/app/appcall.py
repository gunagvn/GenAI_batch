import requests
import json

# Ollama API endpoint (local host)
url = "http://localhost:11434/api/generate"

# Prepare request payload
payload = {
    "model": "phi3",
    "prompt": "Explain Artificial Intelligence in 3 short lines."
}

# Make POST request
response = requests.post(url, json=payload, stream=True)

# Stream and print response
for line in response.iter_lines():
    if line:
        data = json.loads(line)
        print(data.get("response", ""), end="")