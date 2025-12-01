import gradio as gr
from transformers import pipeline

# Load an image classification model
classifier = pipeline("image-classification", model="google/vit-base-patch16-224")

def detect_objects(frame):
    # frame is a single webcam frame (image)
    results = classifier(frame)

    # Convert predictions into a readable string
    output = ""
    for r in results[:3]:
        output += f"{r['label']} → {round(r['score']*100, 2)}%\n"
    return output

# Gradio Interface
live = gr.Interface(
    fn=detect_objects,
    inputs=gr.Image(sources="webcam", streaming=True),   # webcam ON
    outputs=gr.Textbox(label="Detected Objects"),
    title="Live Object Detector",
    description="Show any object to your webcam. The AI will identify it."
)

live.launch()
