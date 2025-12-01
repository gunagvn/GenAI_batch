from nltk.tokenize import word_tokenize
import nltk

# Download both old and new tokenizers (for compatibility)
nltk.download('punkt')
nltk.download('punkt_tab')

sentence = "Let's learn tokenization in AI!"
tokens = word_tokenize(sentence)
print("Tokens:", tokens)
