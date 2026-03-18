import google.generativeai as genai
import wikipedia
import time
from config import GEMINI_API_KEY

# Configure the API
genai.configure(api_key=GEMINI_API_KEY)

# 🔄 List of models to try in order (Fallback Strategy)
# We prioritize the newest "Flash" models, then fall back to stable aliases.
MODEL_PRIORITY_LIST = [
    "gemini-2.5-flash",          # Newest High Quality
    "gemini-flash-latest",       # Google's Managed Stable Alias (Recommended)
    "gemini-2.0-flash-lite",     # Lightweight/Fast
    "gemini-pro-latest",         # Standard Pro Model
    "gemini-2.0-flash-exp",      # Experimental
]

def get_wiki_summary(topic):
    """Optional: Fetches real facts."""
    try:
        search_results = wikipedia.search(topic)
        if search_results:
            return wikipedia.summary(search_results[0], sentences=5)
    except:
        return None
    return None

def generate_script(topic):
    print(f"✨ Generating script for '{topic}'...")

    # 1. Fetch Context
    context = get_wiki_summary(topic)
    
    # 2. Build Prompt
    if context:
        base_prompt = (
            f"You are a professional YouTube video creator. Write a voiceover script about '{topic}'. "
            f"Use these real facts: {context}. "
        )
    else:
        base_prompt = f"You are a professional YouTube video creator. Write a factual, engaging voiceover script about '{topic}'. "

    final_prompt = (
        f"{base_prompt}\n"
        "Strict Requirements:\n"
        "1. Total length: Approx 180 words (for a 1-minute video).\n"
        "2. Structure: Hook -> 3 Interesting Facts -> Conclusion.\n"
        "3. Do NOT include scene descriptions. Only write what the voice says.\n"
        "4. Tone: Energetic and educational."
    )

    # 3. 🔄 TRY MODELS ONE BY ONE
    for model_name in MODEL_PRIORITY_LIST:
        try:
            print(f"🔄 Attempting with model: {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(final_prompt)
            
            script = response.text.strip()
            
            # Clean up
            script = script.replace("**", "").replace("##", "").replace("*", "")
            
            print(f"✅ Success with {model_name}!")
            return script

        except Exception as e:
            # If it's a Quota error (429), we print and move to the next model
            if "429" in str(e) or "Quota" in str(e):
                print(f"⚠️ Quota/Limit hit on {model_name}. Switching...")
            else:
                print(f"❌ Error on {model_name}: {e}")
            
            time.sleep(1) # Short pause before trying next model

    # 4. FINAL FALLBACK (If Google blocks everything)
    print("🚨 All AI Models Failed. Using Wiki Backup.")
    return (
        f"Welcome to our video about {topic}. "
        f"{context if context else 'This is a fascinating topic that many people enjoy.'} "
        "It has changed the way we live. "
        "Thanks for watching and don't forget to subscribe."
    )