import chromadb
from chromadb import EmbeddingFunction, Documents, Embeddings
import chromadb.utils.embedding_functions as embedding_functions
import asyncio
import crawl4ai
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, LLMExtractionStrategy, LLMConfig
from google import genai
from google.genai import types
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field
import json
import os
from dotenv import load_dotenv

load_dotenv()

urls = [
    "https://www.crescentschool.org/how-to-apply",
    "https://www.crescentschool.org/how-to-apply/visit-crescent",
    "https://www.crescentschool.org/how-to-apply/application-process",
    "https://www.crescentschool.org/how-to-apply/admission-dates-and-events",
    "https://www.crescentschool.org/how-to-apply/tuition-and-fees",
    "https://www.crescentschool.org/page/how-to-apply/financial-assistance",
    "https://www.crescentschool.org/how-to-apply/enrolment-team",
    "https://www.crescentschool.org/how-to-apply/faqs",
    "https://www.crescentschool.org/how-to-apply/answers-from-the-enrolment-office",
    "https://www.crescentschool.org/how-to-apply/apply-now"
]

class ExtractedContent(BaseModel):
     relevant_text: str = Field(description="The clean text block containing only the content that is special to that specific URL.")
     
EXTRACTION_INSTRUCTION = """
You are a content extraction assistant for a school handbook website. Your job is to extract useful, substantive content from web pages while removing navigation clutter.

## Context
You're processing pages from a school's family handbook. Each page contains important information about policies, procedures, or general school information.

## What to KEEP (Extract)
- Page titles and main headings
- All descriptive paragraphs and explanatory text
- Policy descriptions and guidelines
- Important lists (rules, procedures, requirements)
- Contact information relevant to the page topic
- Any substantive content that helps answer questions about the school

## What to REMOVE (Filter Out)
- Repetitive navigation menus (e.g., "Home | About | Contact | Admissions")
- Footer content that appears on every page
- Social media links and share buttons
- Generic headers like "Quick Links" or "Main Menu"
- Login/Sign-in links
- Search boxes
- Copyright notices and legal disclaimers
- Breadcrumb navigation

## Critical Rules
1. **Err on the side of inclusion**: If you're unsure whether content is important, KEEP IT. Missing important information is worse than including a bit of extra content.

2. **Minimum content threshold**: Your extracted text should be at least 100 characters long. If you find less than that, you're likely being too aggressive with filtering.

3. **Check the URL**: The URL path often indicates the topic (e.g., "/dress-code" means extract dress code information). Make sure you're capturing content related to that topic.

4. **Don't return empty results**: If you can't find specific content matching the URL, extract ALL substantive text from the page instead of returning nothing.

## Output Format
Return ONLY the cleaned, relevant text. Do not add any commentary, metadata, or explanations. Just return the useful content from the page.
"""

def get_chroma_db(name):
        google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
            api_key=os.environ.get("GEMINI_API_KEY"),
            model_name="gemini-embedding-001"
        )
        chroma_client = chromadb.PersistentClient(path=os.environ.get("CHROMA_DB_PATH"))
        collection = chroma_client.get_or_create_collection(name=name, embedding_function=google_ef)
        return collection

async def crawlinfo(db):
    print("Starting crawl (Optimized: No LLM Extraction)...")
    
    # Simple run config - no LLM strategy needed, crawl4ai defaults to smart markdown
    run_conf = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS
    )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=100,
        length_function=len
    )

    doc_list = []
    id_list = []
    metadata_list = []

    async with AsyncWebCrawler() as crawler:
        for i, url in enumerate(urls):
            print(f"\n[Crawling {i+1}/{len(urls)}] {url}")
            
            # Basic crawl - crawl4ai automatically converts to markdown
            result = await crawler.arun(url, config=run_conf)
            
            if result.success:
                # Use the raw markdown content directly
                # crawl4ai usually does a good job cleaning up navs/footers in markdown mode
                content = result.markdown
                
                if not content:
                    print(f"[WARN] No content found for {url}")
                    continue
                    
                print(f"[OK] Content length: {len(content)} chars")

                # Split the text
                chunks = text_splitter.split_text(content)
                print(f"     Split into {len(chunks)} chunks.")
                
                for j, chunk in enumerate(chunks):
                    doc_list.append(chunk)
                    chunk_id = f"{url}_chunk_{j}"
                    id_list.append(chunk_id)
                    metadata_list.append({"source": url})

            else:
                print(f"[ERROR] Crawl failed for {url}: {result.error_message}")
            
            # Much shorter wait time needed since we aren't calling the LLM
            await asyncio.sleep(2)

    # Add to ChromaDB
    if doc_list:
        print(f"\nCrawl complete. Adding {len(doc_list)} chunks to ChromaDB...")
        # Note: This is where the Gemini Embedding API is called.
        # It's much cheaper/faster than the generation API, but still has limits.
        # If this fails, we might need to batch it or wait between adds.
        
        # Batching adds to be safe
        batch_size = 20
        total_batches = (len(doc_list) + batch_size - 1) // batch_size
        
        for i in range(0, len(doc_list), batch_size):
            batch_ids = id_list[i:i+batch_size]
            batch_docs = doc_list[i:i+batch_size]
            batch_meta = metadata_list[i:i+batch_size]
            
            print(f"  Adding batch {i//batch_size + 1}/{total_batches}...")
            db.add(ids=batch_ids, documents=batch_docs, metadatas=batch_meta)
            # Small sleep to be nice to the embedding API
            await asyncio.sleep(1)
            
        print("Done.")
    else:
        print("No documents found.")

def main():
        # Using a new collection name for enrollment info
        db = get_chroma_db("enrollment_info")
        asyncio.run(crawlinfo(db))
        print(f"Total documents in enrollment_info: {db.count()}")

if __name__ == "__main__":
        main()
