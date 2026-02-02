import spacy
import pandas as pd

# 1. Test spaCy loading
try:
    nlp = spacy.load("en_core_web_sm")
    print("✅ spaCy Model loaded successfully.")
except Exception as e:
    print(f"❌ Error loading spaCy: {e}")

# 2. simple processing
text = "LLMs are changing the landscape of linguistics."
doc = nlp(text)
print(f"Analysis: {[token.pos_ for token in doc]}")

# 3. Test pandas
df = pd.DataFrame({"Test": [1, 2, 3]})
print("✅ Pandas is working.")