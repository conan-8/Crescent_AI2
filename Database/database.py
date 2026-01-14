import os
import chromadb
from chromadb import EmbeddingFunction, Documents, Embeddings
import chromadb.utils.embedding_functions as embedding_functions
import asyncio
import crawl4ai
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, LLMExtractionStrategy, LLMConfig
from crawl4ai.extraction_strategy import CosineStrategy
from google import genai
from google.genai import types
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field
import json



urls = ["https://www.crescentschool.org/family-handbook/upper-school",
        "https://www.crescentschool.org/family-handbook/upper-school/attendance-and-punctuality",
        "https://www.crescentschool.org/family-handbook/upper-school/mentor-program",
        "https://www.crescentschool.org/family-handbook/upper-school/academics"
        "https://www.crescentschool.org/family-handbook/upper-school/academic-integrity",
        "https://www.crescentschool.org/family-handbook/upper-school/promotion-from-grade-to-grade"
        # "https://www.crescentschool.org/family-handbook/policies/code-of-conduct",
        # "https://www.crescentschool.org/family-handbook/policies/code-of-sportsmanship",
        # "https://www.crescentschool.org/family-handbook/policies/generative-artificial-intelligence-ai",
        # "https://www.crescentschool.org/family-handbook/policies/laptop-use-policy",
        # "https://www.crescentschool.org/family-handbook/policies/parent-concern-policy",
        # "https://www.crescentschool.org/family-handbook/policies/video-conferencing"
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

## Example
URL: https://www.crescentschool.org/family-handbook/general-information/dress-code

Good extraction:
"Dress Code
Students are expected to dress appropriately for a learning environment. The following guidelines apply:
- Shirts must have sleeves
- Closed-toe shoes are required
- No offensive language or imagery on clothing
For questions about dress code, contact the main office."

Bad extraction (too aggressive):
"Dress Code"

Bad extraction (empty):
""
"""

def get_chroma_db(name):
        google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
            api_key=os.environ.get("GEMINI_API_KEY"),
            model_name="gemini-embedding-001"
        )
        chroma_client = chromadb.PersistentClient(path=os.environ.get("CHROMA_DB_PATH")) # u will have to change this for ur local db or if u have never runned this script before
        collection = chroma_client.get_or_create_collection(name=name, embedding_function=google_ef)
        return collection

async def crawlinfo(db):
    print("Starting crawl...")
    llm_conf = LLMConfig(provider="gemini/gemini-2.5-flash", api_token="AIzaSyCaJ7me7Ans9STNva8-YrNUHf0dPBj6HfI")

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
        # 4. Loop one-by-one to respect rate limits
        for i, url in enumerate(urls):
            print(f"\n[Crawling {i+1}/{len(urls)}] {url}")
            
            # Use arun (singular)
            result = await crawler.arun(url, config=run_conf)
            
            if result.success and result.extracted_content:
                try:
                    # The result is a JSON string, e.g., '{"relevant_text": "..."}'
                    data = json.loads(result.extracted_content)
                    extracted_text = None
                    
                    # --- START FIX ---
                    # Check if the result is a list
                    if isinstance(data, list) and data:
                        # If it's a list, get the 'relevant_text' from the *first item*
                        extracted_text = data[0].get("relevant_text")
                    elif isinstance(data, dict):
                        # If it's a dictionary, get it directly
                        extracted_text = data.get("relevant_text")
                    # --- END FIX ---

                    if not extracted_text:
                        print(f"[WARN] LLM returned no 'relevant_text' for {url}")
                        continue

                    # 5. Split the *extracted* text
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
            
            # 6. WAIT! This is critical for the free-tier rate limit.
            # 10 requests/min = 1 request every 6 seconds.
            if i < len(urls) - 1: # Don't wait after the last one
                print("Waiting 10 seconds for 'generate_content' rate limit...")
                await asyncio.sleep(10)

    # 7. Add all chunks to ChromaDB in a single batch
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

# Enrollment URLs for LLM-free crawling
enrollment_urls = [
    "https://www.crescentschool.org/admissions",
    "https://www.crescentschool.org/admissions/how-to-apply",
    "https://www.crescentschool.org/admissions/tuition-and-fees",
    "https://www.crescentschool.org/admissions/open-house",
    "https://www.crescentschool.org/admissions/faqs"
]


async def crawl_enrollment(db):
    """
    Crawl enrollment pages using LLM-free CosineStrategy.
    This is faster and cheaper than LLM-based extraction.
    """
    print("Starting enrollment crawl (LLM-free)...")

    # CosineStrategy for semantic content extraction without LLM
    extraction_strategy = CosineStrategy(
        semantic_filter="enrollment admission tuition application fees apply school",
        word_count_threshold=50,  # Filter out very short chunks
        sim_threshold=0.3,        # Similarity threshold for clustering
        top_k=10,                 # Get top 10 relevant clusters per page
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Configure crawler with content cleaning (no nav/footer)
    run_conf = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=extraction_strategy,
        excluded_tags=["nav", "footer", "header", "aside", "script", "style"],
        remove_overlay_elements=True
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
        for i, url in enumerate(enrollment_urls):
            print(f"\n[Crawling {i+1}/{len(enrollment_urls)}] {url}")

            result = await crawler.arun(url, config=run_conf)

            if result.success:
                # CosineStrategy returns extracted content as JSON string
                extracted_text = ""

                if result.extracted_content:
                    try:
                        # Parse the JSON result from CosineStrategy
                        data = json.loads(result.extracted_content)

                        # CosineStrategy returns a list of clusters
                        if isinstance(data, list):
                            # Combine all cluster content
                            text_parts = []
                            for cluster in data:
                                if isinstance(cluster, dict):
                                    # Get the content from each cluster
                                    content = cluster.get("content", "") or cluster.get("text", "")
                                    if content:
                                        text_parts.append(content)
                                elif isinstance(cluster, str):
                                    text_parts.append(cluster)
                            extracted_text = "\n\n".join(text_parts)
                        elif isinstance(data, dict):
                            extracted_text = data.get("content", "") or data.get("text", "") or str(data)
                        else:
                            extracted_text = str(data)
                    except json.JSONDecodeError:
                        # If not valid JSON, use the raw extracted content
                        extracted_text = result.extracted_content

                # Fallback to markdown if no extracted content
                if not extracted_text and result.markdown:
                    extracted_text = result.markdown

                if extracted_text and len(extracted_text.strip()) > 50:
                    # Split the extracted text into chunks
                    chunks = text_splitter.split_text(extracted_text)
                    print(f"[OK] Extracted and split into {len(chunks)} chunks.")

                    for j, chunk in enumerate(chunks):
                        doc_list.append(chunk)
                        chunk_id = f"enrollment_{url}_chunk_{j}"
                        id_list.append(chunk_id)
                        metadata_list.append({"source": url, "type": "enrollment"})
                else:
                    print(f"[WARN] No substantial content extracted for {url}")
            else:
                print(f"[ERROR] Crawl failed for {url}: {result.error_message}")

    # Add all chunks to ChromaDB in a single batch
    if doc_list:
        print(f"\nEnrollment crawl complete. Adding {len(doc_list)} total document chunks to ChromaDB...")
        db.add(
            ids=id_list,
            documents=doc_list,
            metadatas=metadata_list
        )
        print("Done.")
    else:
        print("No successful documents to add for enrollment.")


def main():
    # Build handbook database (existing LLM-based crawling)
    handbook_db = get_chroma_db("family_handbook_1")

    # Build enrollment database (new LLM-free crawling)
    enrollment_db = get_chroma_db("enrollment_info")

    # Run both crawlers
    print("=" * 60)
    print("BUILDING FAMILY HANDBOOK DATABASE (LLM-based)")
    print("=" * 60)
    asyncio.run(crawlinfo(handbook_db))
    print(f"\nHandbook database document count: {handbook_db.count()}")

    print("\n" + "=" * 60)
    print("BUILDING ENROLLMENT DATABASE (LLM-free)")
    print("=" * 60)
    asyncio.run(crawl_enrollment(enrollment_db))
    print(f"\nEnrollment database document count: {enrollment_db.count()}")

if __name__ == "__main__":
        main()
                



