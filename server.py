from mcp.server.fastmcp import FastMCP

# 1. Create the Server
# We name it "News Analyst"
mcp = FastMCP("News Analyst")

# 2. Define the Logic
# We move your "main" function here, but we add a "decorator" (@mcp.tool)
# This tells the MCP system: "Hey, this function is a Tool other AIs can use!"
@mcp.tool()
def analyze_hype(news_input: str) -> dict:
    """
    Analyzes text to calculate a hype score (0-100).
    Input: A string of news text.
    Output: A dictionary with score and keywords.
    """
    # SAFETY CHECK: Handle empty input
    if not news_input:
        return {"hype_score": 0, "reason": "No input provided"}

    # LOGIC (Same as before)
    hype_words = ["revolutionary", "breakthrough", "agentic", "transform", "incredible", "boom", "future"]
    
    score = 0
    found_words = []
    text_lower = str(news_input).lower()
    
    for word in hype_words:
        if word in text_lower:
            score += 10
            found_words.append(word)
    
    final_score = min(score, 100)
    
    return {
        "hype_score": final_score,
        "keywords_found": found_words
    }

# 3. Run the Server
if __name__ == "__main__":
    # This command starts the server so it listens for requests
    mcp.run()