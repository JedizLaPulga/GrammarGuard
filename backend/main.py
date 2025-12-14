from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import spacy
import uvicorn
import os
from contextlib import asynccontextmanager
from spellchecker import SpellChecker

# Global variables to hold the models
nlp = None
spell = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global nlp, spell
    try:
        print("Loading spaCy model...")
        if not spacy.util.is_package("en_core_web_sm"):
             print("Model 'en_core_web_sm' not found. Downloading...")
             os.system("python -m spacy download en_core_web_sm")
        
        nlp = spacy.load("en_core_web_sm")
        print("spaCy model loaded successfully!")
        
        print("Loading spell checker...")
        spell = SpellChecker()
        print("Spell checker loaded successfully!")
        
    except Exception as e:
        print(f"Error loading models: {e}")
    yield

# Initialize FastAPI app
app = FastAPI(title="GrammarGuard Backend", lifespan=lifespan)

class GrammarRequest(BaseModel):
    text: str

class GrammarResponse(BaseModel):
    original_text: str
    corrected_text: str

@app.get("/health")
def health_check():
    if nlp and spell:
        return {"status": "ok", "message": "Models are ready"}
    return {"status": "loading", "message": "Models are still loading"}

@app.post("/check", response_model=GrammarResponse)
def check_grammar(request: GrammarRequest):
    if not nlp or not spell:
        raise HTTPException(status_code=503, detail="Models not loaded yet")
    
    doc = nlp(request.text)
    
    corrected_parts = []
    
    for sent in doc.sents:
        # Get all tokens as a list of strings (preserving whitespace)
        tokens = [t.text_with_ws for t in sent]
        
        # 1. Capitalization Fix
        # Check the first token of the sentence
        if tokens:
            first_word_str = tokens[0]
            # tokens[0] is string like "hello "
            # Check if it starts with lower case letter
            if first_word_str and first_word_str[0].islower():
                # Capitalize first char
                tokens[0] = first_word_str[0].upper() + first_word_str[1:]
        
        # 2. Spell Checker Fix
        for i, token in enumerate(sent):
            # Skip non-alpha characters and entities (like names)
            if not token.is_alpha or token.ent_type_:
                continue
                
            # extracting the word part from the potentially modified token string
            # (Note: Capitalization fix might have modified tokens[0])
            current_str = tokens[i]
            
            # We assume the whitespace is at the end.
            # token.whitespace_ gives the original whitespace.
            # Let's trust that we only modified the text part so far.
            whitespace = token.whitespace_
            word_part = current_str[:len(current_str) - len(whitespace)] if whitespace else current_str
            
            # Check correction
            # unknown() takes a list
            if word_part.lower() not in spell:
                 correction = spell.correction(word_part)
                 if correction and correction.lower() != word_part.lower():
                     # Preserve original capitalization style if simple title case
                     if word_part[0].isupper():
                         correction = correction.capitalize()
                     
                     # Update token
                     tokens[i] = correction + whitespace

        # 3. Repeated Word Fix
        # We will rebuild the list of valid tokens using the UPDATED tokens list
        final_sent_tokens = []
        skip_next = False
        
        for i in range(len(sent)):
            if skip_next:
                skip_next = False
                continue
            
            current_str = tokens[i]
            # For comparison, we grab the word part again (strip ws)
            current_word_clean = current_str.strip()
            
            if i < len(sent) - 1:
                next_str = tokens[i+1]
                next_word_clean = next_str.strip()
                
                # Check if words match (case insensitive) and original POS was not PUNCT
                # We use sent[i].pos_ because checking punctuation on corrected text is tricky without re-parsing,
                # and punctuation shouldn't have changed during spell check/capitalization ideally.
                if (current_word_clean.lower() == next_word_clean.lower() 
                    and sent[i].pos_ != "PUNCT"):
                    
                    # Found duplicate. 
                    skip_next = True
            
            final_sent_tokens.append(current_str)
            
        corrected_parts.append("".join(final_sent_tokens))

    final_corrected = "".join(corrected_parts)
    
    # Simple post-processing fixes
    final_corrected = final_corrected.replace(" ,", ",")
    final_corrected = final_corrected.replace(" .", ".")
    
    return GrammarResponse(
        original_text=request.text,
        corrected_text=final_corrected
    )

if __name__ == "__main__":
    # We run on localhost 14300
    uvicorn.run(app, host="127.0.0.1", port=14300)
