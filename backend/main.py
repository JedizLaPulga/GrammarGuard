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
    
    for sent in doc.sents:
        # Get all tokens as a list of strings (preserving whitespace)
        tokens = [t.text_with_ws for t in sent]
        
        # 1. Capitalization Fix
        # Check the first token of the sentence
        if tokens:
            first_word = tokens[0]
            # capitalization might affect just the text part, need to be careful with whitespace
            if first_word and first_word[0].islower():
                tokens[0] = first_word[0].upper() + first_word[1:]
        
        # 2. Repeated Word Fix
        # We will rebuild the list of valid tokens
        final_sent_tokens = []
        skip_next = False
        
        for i in range(len(sent)):
            if skip_next:
                skip_next = False
                continue
            
            # Use the 'tokens' list which might have the capitalized first word
            current_str = tokens[i]
            
            # For comparison logic, we look at the underlying spaCy token
            current_token_obj = sent[i]
            
            if i < len(sent) - 1:
                next_token_obj = sent[i+1]
                
                # Check if words match (case insensitive) and are not punctuation
                if (current_token_obj.text.lower() == next_token_obj.text.lower() 
                    and current_token_obj.pos_ != "PUNCT"):
                    
                    # Found duplicate. 
                    # Generally, we keep the FIRST one (which might have space) and skip the second.
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
