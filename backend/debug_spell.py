from spellchecker import SpellChecker
import spacy

def format_token_debug(token):
    return f"Text: '{token.text}', Alpha: {token.is_alpha}, Ent: '{token.ent_type_}'"

def debug_spell():
    print("Initializing...")
    nlp = spacy.load("en_core_web_sm")
    spell = SpellChecker()
    
    text = "the qick brown fox jumps over the the lazy dog."
    doc = nlp(text)
    
    print(f"\nAnalyzing text: '{text}'")
    
    for sent in doc.sents:
        for token in sent:
            print(f"\nToken: {format_token_debug(token)}")
            
            word = token.text
            if word.lower() not in spell:
                print(f"  '{word}' is UNKNOWN.")
                correction = spell.correction(word)
                print(f"  Correction: '{correction}'")
            else:
                print(f"  '{word}' is KNOWN.")

if __name__ == "__main__":
    debug_spell()
