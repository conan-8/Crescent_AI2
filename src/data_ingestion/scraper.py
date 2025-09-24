# src/data_ingestion/scraper.py

import requests
from bs4 import BeautifulSoup

def scrape_website(url: str) -> str:
    """
    Scrapes the text content from a single webpage.

    Args:
        url: The URL of the webpage to scrape.

    Returns:
        The cleaned text content of the page, or an empty string if scraping fails.
    """
    print(f"Scraping {url}...")
    try:
        # --- ADD THIS HEADER ---
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # --- UPDATE THIS LINE ---
        response = requests.get(url, headers=headers, timeout=10)
        
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        # Find the main content of the page. This is a common tag,
        # but you might need to inspect your target websites to find
        # the right tag or class (e.g., 'article', 'div#content').
        main_content = soup.find('main')

        if main_content:
            text = main_content.get_text(separator='\n', strip=True)
            return text
        else:
            # Fallback to using the whole body if 'main' isn't found
            return soup.body.get_text(separator='\n', strip=True)

    except requests.RequestException as e:
        print(f"Error scraping {url}: {e}")
        return ""