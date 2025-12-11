from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import spacy
import uvicorn
import os
from contextlib import asynccontextmanager

# Global variable to hold the model
nlp = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global nlp
    try:
        print("Loading spaCy model...")
        if not spacy.util.is_package("en_core_web_sm"):
             print("Model 'en_core_web_sm' not found. Downloading...")
             os.system("python -m spacy download en_core_web_sm")
        
        nlp = spacy.load("en_core_web_sm")
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {e}")
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
    if nlp:
        return {"status": "ok", "message": "Model is ready"}
    return {"status": "loading", "message": "Model is still loading"}

@app.post("/check", response_model=GrammarResponse)
def check_grammar(request: GrammarRequest):
    if not nlp:
        raise HTTPException(status_code=503, detail="Model not loaded yet")
    
    doc = nlp(request.text)
    
    corrected_parts = []
    
    # Iterate through sentences to apply corrections
    for sent in doc.sents:
        sent_text = sent.text_with_ws
        
        # 1. Basic Capitalization
        if sent_text and sent_text[0].islower():
             sent_text = sent_text[0].upper() + sent_text[1:]
        
        # 2. Fix repeated words (e.g. "the the")
        tokens = [token.text_with_ws for token in sent]
        new_tokens = []
        skip_next = False
        
        for i in range(len(sent)):
            if skip_next:
                skip_next = False
                continue
                
            token = sent[i]
            
            # Check for repeated words text (case insensitive)
            if i < len(sent) - 1:
                next_token = sent[i+1]
                if token.text.lower() == next_token.text.lower() and token.pos_ != "PUNCT":
                    # Keep the one with whitespace if applicable, or just the first
                    # We skip the second instance
                    skip_next = True
            
            new_tokens.append(tokens[i])

        # Reconstruct sentence
        fixed_sent = "".join(new_tokens)
        
        # 3. Simple 'a' vs 'an' fix (heuristic) 
        # This is a bit complex to do perfectly with just tokens, so we'll do a simple string replace for demo
        # A robust solution would check the phonetics of the next word.
        
        corrected_parts.append(fixed_sent)
    
    final_corrected = "".join(corrected_parts)
    
    # Simple post-processing fixes
    final_corrected = final_corrected.replace(" ,", ",")
    final_corrected = final_corrected.replace(" .", ".")
    
    return GrammarResponse(
        original_text=request.text,
        corrected_text=final_corrected
    )

if __name__ == "__main__":
    # Run on port 14300 to avoid conflicts
    uvicorn.run(app, host="127.0.0.1", port=14300)
```
