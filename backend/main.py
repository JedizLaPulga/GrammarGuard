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
    
    return GrammarResponse(
        original_text=request.text,
        corrected_text=request.text 
    )

if __name__ == "__main__":
    # Run on port 14300 to avoid conflicts
    uvicorn.run(app, host="127.0.0.1", port=14300)
