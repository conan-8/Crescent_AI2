import sys
import os

# This adds the project root to the Python path, allowing imports from src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_ingestion.scraper import scrape_website
from src.processing.text_processor import chunk_text, create_embeddings
from src.vector_store.database_manager import ChromaManager
from src.config import TARGET_URLS

def main():
    """
    Main function to build the entire knowledge base.
    1. Scrapes websites.
    2. Chunks the text.
    3. Creates embeddings.
    4. Stores them in ChromaDB.
    """
    print("--- Starting Knowledge Base build process ---")
    
    # 1. Scrape all target websites
    all_text = ""
    for url in TARGET_URLS:
        scraped_content = scrape_website(url)
        if scraped_content:
            all_text += scraped_content + "\n\n"
    
    if not all_text:
        print("No content was scraped. Exiting.")
        return

    # 2. Chunk the text
    print("Chunking text...")
    chunks = chunk_text(all_text)
    
    # 3. Create embeddings for the chunks
    print("Creating embeddings...")
    embeddings = create_embeddings(chunks)
    
    # 4. Store in ChromaDB
    db_manager = ChromaManager()
    db_manager.add_documents(chunks, embeddings)
    
    print("--- Knowledge Base build process COMPLETE ---")

if __name__ == "__main__":
    main()

