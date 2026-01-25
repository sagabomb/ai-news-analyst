import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. Load your key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ Error: GOOGLE_API_KEY not found in .env")
else:
    print(f"🔑 Found API Key. Asking Google for available models...")
    genai.configure(api_key=api_key)

    try:
        # 2. List models that support "generateContent" (Chatting)
        available_models = []
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ AVAILABLE: {m.name}")
                available_models.append(m.name)
        
        if not available_models:
            print("⚠️ No models found. Check if your API Key has the right permissions.")
            
    except Exception as e:
        print(f"❌ Connection Failed: {e}")