import os
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
from dotenv import load_dotenv

load_dotenv()

# Enrollment URLs (Starting Point)
urls = [
    "https://www.crescentschool.org/how-to-apply"
]

MAX_DEPTH = 2
ALLOWED_DOMAIN = "crescentschool.org"


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
    print("Starting crawl (LLM-based)...")
    llm_conf = LLMConfig(provider="openrouter/qwen/qwen3.5-397b-a17b", api_token=os.environ.get("OPENROUTER_API_KEY"))

    extraction_strategy = LLMExtractionStrategy(
        llm_config=llm_conf,
        schema=ExtractedContent.model_json_schema(),
        instruction=EXTRACTION_INSTRUCTION,
        extraction_type="schema"
    )

    run_conf = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=extraction_strategy
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
        queue = [{"url": u, "depth": 0} for u in urls]
        visited = set()

        while queue:
            current = queue.pop(0)
            url = current["url"]
            depth = current["depth"]

            if url in visited: continue
            visited.add(url)
            
            print(f"\n[Crawling Depth {depth} | Queue: {len(queue)}] {url}")
            
            result = await crawler.arun(url, config=run_conf)
            
            if result.success and result.extracted_content:
                # Add discovered internal links to queue
                if depth < MAX_DEPTH and hasattr(result, 'links') and isinstance(result.links, dict):
                    internal_links = result.links.get('internal', [])
                    for link_obj in internal_links:
                        next_url = link_obj.get('href')
                        if next_url and ALLOWED_DOMAIN in next_url:
                            # Clean URL (remove fragments)
                            clean_url = next_url.split('#')[0]
                            # Only add if it's not already in visited or queue to save space
                            if clean_url not in visited and not any(q['url'] == clean_url for q in queue):
                                queue.append({"url": clean_url, "depth": depth + 1})

                try:
                    # The result is a JSON string
                    data = json.loads(result.extracted_content)
                    extracted_text = None
                    
                    # Handle potential list or dict response
                    if isinstance(data, list) and data:
                        extracted_text = data[0].get("relevant_text")
                    elif isinstance(data, dict):
                        extracted_text = data.get("relevant_text")

                    if not extracted_text:
                        print(f"[WARN] LLM returned no 'relevant_text' for {url}")
                        continue

                    # Split the extracted text
                    chunks = text_splitter.split_text(extracted_text)
                    print(f"[OK] Extracted and split into {len(chunks)} chunks.")
                    
                    for j, chunk in enumerate(chunks):
                        doc_list.append(chunk)
                        chunk_id = f"{url}_chunk_{j}"
                        id_list.append(chunk_id)
                        metadata_list.append({"source": url})

                except json.JSONDecodeError:
                    print(f"[ERROR] Failed to parse LLM output for {url}")
                except Exception as e:
                    print(f"[ERROR] processing {url}: {e}")
            else:
                print(f"[ERROR] Crawl failed for {url}: {result.error_message}")

    # Add all chunks to ChromaDB
    if doc_list:
        print(f"\nCrawl complete. Adding {len(doc_list)} total document chunks to ChromaDB...")
        db.add(
            ids=id_list,
            documents=doc_list,
            metadatas=metadata_list
        )
        print("Done.")
    else:
        print("No successful documents to add.")

def main():
        # Using the enrollment_info collection
        db = get_chroma_db("test")
        asyncio.run(crawlinfo(db))
        print(f"Total documents in enrollment_info: {db.count()}")

if __name__ == "__main__":
        main()
