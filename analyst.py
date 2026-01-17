import json

def main(news_input: str) -> dict:
    # 1. Define Hype Keywords
    hype_words = ["revolutionary", "breakthrough", "agentic", "transform", "incredible", "boom", "future"]
    
    # 2. Calculate Score
    score = 0
    found_words = []
    
    # +10 points for every hype word found
    text_lower = news_input.lower()
    for word in hype_words:
        if word in text_lower:
            score += 10
            found_words.append(word)
    
    # 3. Cap score at 100
    final_score = min(score, 100)
    
    # 4. Return JSON structure
    result = {
        "hype_score": final_score,
        "keywords_found": found_words,
        "analysis": f"Score: {final_score}/100. Keywords: {', '.join(found_words)}"
    }
    
    return result

# Simple test block (Runs only on your Mac, not in Dify)
if __name__ == "__main__":
    sample_text = "This new agentic AI is a revolutionary breakthrough for the future."
    print(json.dumps(main(sample_text), indent=2))