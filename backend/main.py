from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import spacy
import uvicorn
import os
from contextlib import asynccontextmanager
from spellchecker import SpellChecker
import lemminflect

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
    
    # --- STEP 1: Basic Corrections (Spell Check & Capitalization) ---
    # We do a first pass to fix spelling so the parser has clean text to work with.
    
    doc_initial = nlp(request.text)
    step1_tokens = []
    
    for sent in doc_initial.sents:
        sent_tokens = [t.text_with_ws for t in sent]
        
        # 1. Capitalization Fix
        if sent_tokens:
            first_word_str = sent_tokens[0]
            if first_word_str and first_word_str[0].islower():
                sent_tokens[0] = first_word_str[0].upper() + first_word_str[1:]
        
        # 2. Spell Checker Fix
        for i, token in enumerate(sent):
            if not token.is_alpha: continue
            # Skip capitalized entities (heuristics)
            if token.ent_type_ and not token.text[0].islower(): continue
            
            current_str = sent_tokens[i]
            whitespace = token.whitespace_
            word_part = current_str[:len(current_str) - len(whitespace)] if whitespace else current_str
            
            if word_part.lower() not in spell:
                 correction = spell.correction(word_part)
                 if correction and correction.lower() != word_part.lower():
                     if word_part[0].isupper(): correction = correction.capitalize()
                     sent_tokens[i] = correction + (whitespace if whitespace else "")
        
        step1_tokens.extend(sent_tokens)
        
    text_step1 = "".join(step1_tokens)
    
    # --- STEP 2: Advanced Grammar (Subject-Verb Agreement) & Repeats ---
    # Re-parse the cleaner text to get accurate dependency tree
    doc_step2 = nlp(text_step1)
    corrected_parts = []
    
    for sent in doc_step2.sents:
        # We work with mutable list of token strings from the new doc
        tokens = [t.text_with_ws for t in sent]
        
        # 3. Subject-Verb Agreement (SVA)
        for token in sent:
            if token.pos_ in ["VERB", "AUX"]:
                subjects = [child for child in token.children if child.dep_ == "nsubj"]
                if subjects:
                    subj = subjects[0] # Take the first subject
                    
                    is_plural_subj = False
                    if subj.tag_ in ["NNS", "NNPS"]:
                        is_plural_subj = True
                    elif subj.pos_ == "PRON":
                        lower_subj = subj.text.lower()
                        if lower_subj in ["they", "we", "you"]:
                            is_plural_subj = True
                    
                    # Target Tag Selection
                    target_tag = None
                    
                    # CASE A: "I" (Special)
                    if subj.text.lower() == "i":
                        # If verb is 'be', needs special handling ("am", "was")
                        if token.lemma_ == "be":
                            if token.tag_ == "VBZ" or token.text.lower() in ["is", "are"]:
                                # Force to 'am' (present) or 'was' (past)
                                # This is simplistic, let's assume present tense 'am' if it was 'is/are'
                                # But if it was 'were', maintain past.
                                if token.text.lower() in ["is", "are"]:
                                    # Manually fix specific be-verbs for 'I'
                                    idx = token.i - sent.start
                                    tokens[idx] = "am" + token.whitespace_
                                    continue # Skip standard inflection
                            target_tag = "VBP" # I have, I go
                        else:
                            target_tag = "VBP" # I run

                    # CASE B: Plural (You, We, They, Dogs)
                    elif is_plural_subj:
                         target_tag = "VBP" # They run, You are
                         
                    # CASE C: Singular (He, She, It, Dog)
                    else:
                         target_tag = "VBZ" # She runs, It is
                    
                    # Apply correction if needed
                    if target_tag:
                        # Don't change if already correct
                        if token.tag_ != target_tag:
                            new_verb = token._.inflect(target_tag)
                            if new_verb:
                                idx = token.i - sent.start
                                tokens[idx] = new_verb + token.whitespace_

        # 4. Repeated Word Fix (Simple String Match on the Grammar-Corrected Text)
        final_sent_tokens = []
        skip_next = False
        
        for i in range(len(tokens)):
            if skip_next:
                skip_next = False
                continue
            
            curr_str = tokens[i]
            curr_word = curr_str.strip()
            
            if i < len(tokens) - 1:
                next_str = tokens[i+1]
                next_word = next_str.strip()
                
                if curr_word and curr_word.lower() == next_word.lower():
                     # Only skip if it looks like a word, not punctuation ".."
                     if curr_word[0].isalnum():
                         skip_next = True
            
            final_sent_tokens.append(curr_str)

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
