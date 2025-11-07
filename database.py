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


client = genai.Client(api_key="AIzaSyCaJ7me7Ans9STNva8-YrNUHf0dPBj6HfI")

urls = ["https://www.crescentschool.org/family-handbook",
        "https://www.crescentschool.org/family-handbook/general-information",
        "https://www.crescentschool.org/family-handbook/general-information/a-message-from-our-headmaster",
        "https://www.crescentschool.org/family-handbook/general-information/mission-and-values",
        "https://www.crescentschool.org/family-handbook/general-information/campus-access",
        "https://www.crescentschool.org/family-handbook/general-information/transportation-and-parking",
        "https://www.crescentschool.org/family-handbook/general-information/food-services",
        "https://www.crescentschool.org/family-handbook/general-information/school-communication",
        "https://www.crescentschool.org/family-handbook/general-information/dress-code",
        "https://www.crescentschool.org/family-handbook/general-information/student-property",
        "https://www.crescentschool.org/family-handbook/general-information/house-system",
        "https://www.crescentschool.org/family-handbook/general-information/prefect-system",
        "https://www.crescentschool.org/family-handbook/general-information/school-constitution"
]

class ExtractedContent(BaseModel):
     relevant_text: str = Field(description="The clean text block containing only the content that is special to that specific URL.")
     
EXTRACTION_INSTRUCTION = """
You are an intelligent content extraction assistant. Your task is to analyze a webpage's URL and its corresponding raw text, find relevant chunks of text and return them

## Your Goal
Filter the raw text to keep *only* the descriptive content section that is specifically identified by the page's URL.

## Instructions
1.  **Analyze the URL:** Look at the last part of the URL's path (the "slug"). This tells you the page's specific topic.
    * *Example:* For `https://www.crescentschool.org/family-handbook/general-information`, the key topic is "general-information".
2.  **Scan the Raw Text:** Search the provided raw text for the heading and descriptive paragraph(s) that semantically match this key topic. The heading in the text (e.g., "General Information" or "Family Handbook: General Information") will be the one most closely related to the URL's key topic.
3.  **Extract & Filter:**
    * **KEEP:** The matching heading(s) and the descriptive paragraph(s) directly associated with them.
    * **EXCLUDE:** You must aggressively filter out all other non-relevant information. This includes:
        * All other content sections and their descriptions (e.g., "About Us," "Academics," "Careers," etc.).
        * All navigation menus, sitemaps, and bulleted link lists.
        * Headers, footers, and sidebars.
        * Login links, social media icons, and search bars.
4. If you can't find anything related to the end sequence of the provided url, return everything excluding any links or non-relevant info

Your final output must be a clean text block containing the content that you returned
"""

def get_chroma_db(name):
        google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key="AIzaSyCaJ7me7Ans9STNva8-YrNUHf0dPBj6HfI",
                                                                            model_name="gemini-embedding-001",
                                                                            task_type="RETRIEVAL_DOCUMENT"
                                                                            )
        chroma_client = chromadb.PersistentClient(path=r"C:\crescent_ai_source") # u will have to change this for ur local db or if u have never runned this script before
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
        chunk_size=2000, 
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
                print("Waiting 7 seconds for 'generate_content' rate limit...")
                await asyncio.sleep(7)

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

def main():
        db = get_chroma_db("family_handbook_1")
        asyncio.run(crawlinfo(db))

if __name__ == "__main__":
        main()
                



