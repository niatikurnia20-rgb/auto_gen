import os

from dotenv import load_dotenv

# Load variables from .env file (for local development)
load_dotenv()

# API Keys (Fetched safely from system)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print("Kunci Gemini yang benar-benar terbaca adalah:", GEMINI_API_KEY)
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
HF_API_KEY = os.getenv("HF_API_KEY")  # Optional if you still use it
LMNT_API_KEY = os.getenv("LMNT_API_KEY")
LMNT_VOICE = os.getenv("LMNT_VOICE") or os.getenv("LMNT_VOICE_ID")
LMNT_LANGUAGE = os.getenv("LMNT_LANGUAGE", "id")

# Config
OUTPUT_FOLDER = "static/videos"
TEMP_FOLDER = "temp"

# Create folders if they don't exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)

# Safety Check
if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY is missing! Check your .env file.")
if not PEXELS_API_KEY:
    print("WARNING: PEXELS_API_KEY is missing! Check your .env file.")
if not LMNT_API_KEY:
    print("WARNING: LMNT_API_KEY is missing! Check your .env file.")
