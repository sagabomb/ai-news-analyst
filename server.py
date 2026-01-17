from fastapi import FastAPI
from pydantic import BaseModel

# 1. Create the App
# Note: The variable is named 'app', not 'mcp'
app = FastAPI()

# 2. Define the Input Format
# We tell the server to expect a JSON like {"text": "some news"}
class Input(BaseModel):
    text: str

# 3. Define the Route
# This creates a web link at http://.../analyze
@app.post("/analyze")
def analyze_hype(data: Input):
    # LOGIC (Same as before)
    hype_words = ["revolutionary", "breakthrough", "agentic", "transform", "incredible", "boom", "future"]
    
    score = 0
    text_lower = data.text.lower()
    
    for word in hype_words:
        if word in text_lower:
            score += 10
            
    final_score = min(score, 100)
    
    return {
        "hype_score": final_score,
        "status": "Processed by Local FastAPI"
    }