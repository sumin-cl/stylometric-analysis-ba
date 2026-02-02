import spacy
spacy.load('en_core_web_sm')

def test_spacy_load():
    nlp = spacy.load('en_core_web_sm')
    doc = nlp("This is a test sentence.")
    assert len(doc) == 6  # "This", "is", "a", "test", "sentence", "."
    return "Spacy model loaded and test passed."

print(test_spacy_load())