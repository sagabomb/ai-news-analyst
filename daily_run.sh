#!/bin/bash

# 1. Go to the correct folder (REPLACE THIS PATH!)
cd /Users/allen/Desktop/ai-news-analyst

# 2. Activate the Virtual Environment
# (This ensures we use the Python that has Tavily/Gemini installed)
source venv/bin/activate

# 3. Ensure log folder exists (Safety Check)
mkdir -p logs

# 4. Run Sentinel and pipe output to the logs folder
echo "--- Starting Run: $(date) ---" >> logs/sentinel.log
python sentinel.py >> logs/sentinel.log 2>&1
echo "--- Finished Run ---" >> logs/sentinel.log