import gradio as gr

def greet(name, is_morning,is_afternoon,is_evening):
    if is_morning:
        return f"Good morning, {name}!"
    elif is_afternoon:
        return f"Good afternoon, {name}!"
    elif is_evening:    
        return f"Good evening, {name}!"
    else:
        return f"Hello, {name}!"
    
demo = gr.Interface(
    fn=greet,
    inputs=[
        gr.Textbox(label="Your name"),
        gr.Checkbox(label="Is it morning?"),
        gr.Checkbox(label="Is it afternoon?"),
        gr.Checkbox(label="Is it evening?")
    ],
    outputs=gr.Textbox(label="Greeting"),
    title="Greeting App"
)

if __name__ == "__main__":
    demo.launch()