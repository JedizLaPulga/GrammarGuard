from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import spacy
import uvicorn
import os

# Initialize FastAPI app
app = FastAPI(title="GrammarGuard Backend")

# Global variable to hold the model
nlp = None

class GrammarRequest(BaseModel):
    text: str

class GrammarResponse(BaseModel):
    original_text: str
    corrected_text: str
    # We can add more detailed error info later

@app.on_event("startup")
def load_model():
    global nlp
    try:
        print("Loading spaCy model...")
        # Load the small internet-trained model
        # The user needs to download this: python -m spacy download en_core_web_sm
        if not spacy.util.is_package("en_core_web_sm"):
             print("Model 'en_core_web_sm' not found. Downloading...")
             os.system("python -m spacy download en_core_web_sm")
        
        nlp = spacy.load("en_core_web_sm")
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {e}")

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
    
    # Placeholder logic for "correction" 
    # Real grammar correction with spaCy usually requires complex rules 
    # or a specific model. For now, we will just return the analysis.
    # We'll stick to a pass-through response for this step to verify connectivity.
    
    return GrammarResponse(
        original_text=request.text,
        corrected_text=request.text # TODO: Implement actual correction logic
    )

if __name__ == "__main__":
    # We run on localhost 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)
