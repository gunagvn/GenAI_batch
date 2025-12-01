import streamlit as st
from transformers import pipeline
from PIL import Image

classifier = pipeline("image-classification")

st.title("Image Classification")

file = st.file_uploader("Upload an image", type=["jpg","jpeg","png"])

if file:
    img = Image.open(file)
    st.image(img, use_column_width=True)

    st.write("🔍 Classifying...")
    results = classifier(img)

    for r in results:
        st.write(f"**{r['label']}** → {r['score']:.2f}")
