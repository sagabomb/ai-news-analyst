import json

def main(news_input: str) -> dict:
    # SAFETY CHECK: If input is empty/None, return 0 immediately
    if not news_input:
        return {"hype_score": 0}

    # 1. Define Hype Keywords
    hype_words = ["revolutionary", "breakthrough", "agentic", "transform", "incredible", "boom", "future"]
    
    # 2. Calculate Score
    score = 0
    # Force input to string just in case
    text_lower = str(news_input).lower()
    
    for word in hype_words:
        if word in text_lower:
            score += 10
    
    # 3. Cap score at 100
    final_score = min(score, 100)
    
    # 4. Return result
    return {
        "hype_score": final_score
    }

# Test block
if __name__ == "__main__":
    print(json.dumps(main("This is a revolutionary agentic boom"), indent=2))