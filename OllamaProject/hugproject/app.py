import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from flask import send_from_directory

app = Flask(__name__)
CORS(app)

# Read your Hugging Face access token from environment variable
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    print("⚠️  HF_TOKEN not set. Run 'setx HF_TOKEN your_token_here' in Windows cmd first.")

# Initialize OpenAI client (Hugging Face router)
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)
@app.route("/")
def serve_home():
    return send_from_directory(".", "index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "")

        completion = client.chat.completions.create(
            model="moonshotai/Kimi-K2-Thinking:novita",
            messages=[
                {"role": "system", "content": "You are a creative and helpful storyteller assistant."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.9,
            max_tokens=2000,
        )

        reply = completion.choices[0].message.content
        return jsonify({"ok": True, "reply": reply})

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    app.run(host="0.0.0.0", port=port, debug=True)

