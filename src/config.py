# src/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# A list of URLs to scrape for the knowledge base
TARGET_URLS = [
    "https://www.crescentschool.org/about/history",
    "https://www.crescentschool.org/about/meet-our-headmaster",
    "https://www.crescentschool.org/about/missionvaluesvision"
]

# --- NEW: Google Model Configuration ---
# The embedding model to use (Google's free model)
EMBEDDING_MODEL = "models/embedding-001"

# The generation model to use (Gemini's free model)
GENERATION_MODEL = "gemini-2.5-flash"

# Your Google API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")