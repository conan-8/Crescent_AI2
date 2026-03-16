import os
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from dotenv import load_dotenv

load_dotenv()

def check_metadata():
    try:
        google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
            api_key=os.environ.get("GEMINI_API_KEY"),
            model_name="gemini-embedding-001",
        )
        
        chroma_client = chromadb.PersistentClient(path=os.environ.get("CHROMA_DB_PATH"))
        collection = chroma_client.get_collection(
            name="family_handbook_1", 
            embedding_function=google_ef
        )
        
        peek = collection.peek(limit=1)
        if peek['metadatas'] and len(peek['metadatas']) > 0:
            print("Metadata found:", peek['metadatas'][0])
        else:
            print("No metadata found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_metadata()
