import re

text = "Hello!!!  This   is   an Example...   "
print("Original Text:", text)

# Step 1: Clean extra punctuation and spaces
clean_text = re.sub(r'[!?.]+', '.', text)
clean_text = re.sub(r'\s+', ' ', clean_text).strip()
clean_text = clean_text.lower()

print("Cleaned Text:", clean_text)