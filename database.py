import chromadb
from chromadb import EmbeddingFunction, Documents, Embeddings
import chromadb.utils.embedding_functions as embedding_functions
import asyncio
import crawl4ai
from crawl4ai import *
from google import genai
from google.genai import types
from langchain_text_splitters import RecursiveCharacterTextSplitter

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
    run_conf = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        stream=False
    )
    
    # 1. Initialize a text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        # Set a reasonable chunk size and overlap
        chunk_size=3000, 
        chunk_overlap=100,
        length_function=len
    )

    results = []
    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun_many(urls, config=run_conf)
    
    print("Crawl complete. Splitting and processing results...")

    # Create lists to hold your data
    doc_list = []
    id_list = []
    metadata_list = [] # We'll add metadata to track our source
    
    for res in results:
        if res.success and res.markdown and res.markdown.raw_markdown:
            print(f"[OK] Processing: {res.url}")
            
            # 2. Split the markdown text into chunks
            chunks = text_splitter.split_text(res.markdown.raw_markdown)
            
            # 3. Add each chunk as a separate document
            for i, chunk in enumerate(chunks):
                doc_list.append(chunk)
                
                # Create a unique ID for each chunk
                chunk_id = f"{res.url}_chunk_{i}"
                id_list.append(chunk_id)
                
                # Store the original URL in the metadata
                metadata_list.append({"source": res.url})
                
        else:
            print(f"[ERROR] {res.url} => {res.error_message}")

    # Now, add everything to ChromaDB in a single batch
    if doc_list:
        print(f"\nAdding {len(doc_list)} document chunks to ChromaDB...")
        db.add(
            ids=id_list,
            documents=doc_list,
            metadatas=metadata_list # Add the metadata
        )
        print("Done.")
    else:
        print("No successful documents to add.")

def main():
        db = get_chroma_db("family_handbook_1")
        asyncio.run(crawlinfo(db))

if __name__ == "__main__":
        main()
                



