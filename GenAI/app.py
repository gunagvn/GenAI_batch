from flask import Flask, render_template, request, jsonify
from transformers import pipeline

# Initialize Flask app
app = Flask(__name__)

# Load the GPT-2 text generation pipeline
gen = pipeline("text-generation", model="gpt2")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    # Get the topic from the frontend
    data = request.get_json()
    topic = data.get('topic', '')

    # Generate text using GPT-2
    result = gen(
        f"Write a short text about {topic}:",
        max_new_tokens=200,
        do_sample=True,
        top_p=0.9,
        temperature=0.8
    )[0]['generated_text']

    # Return JSON response
    return jsonify({'generated_text': result})

if __name__ == '__main__':
    app.run(debug=True)
