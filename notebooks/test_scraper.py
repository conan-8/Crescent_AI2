# notebooks/test_scraper.py
import sys
import os

# This allows the script to find your src modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_ingestion.scraper import scrape_website
from src.config import TARGET_URLS

# Test with the first URL in your config
test_url = TARGET_URLS[0]

print(f"--- Testing scraper on {test_url} ---")
content = scrape_website(test_url)

if content:
    print("--- Scraper Test: SUCCESS ---")
    print("Scraped Content (first 500 chars):")
    print(content[:500] + "...")
else:
    print("--- Scraper Test: FAILED ---")
    print("No content was returned.")