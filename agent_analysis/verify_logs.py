import os
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
import time
from dotenv import load_dotenv

load_dotenv()

def verify_logs():
    try:
        google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
            api_key=os.environ.get("GEMINI_API_KEY"),
            model_name="gemini-embedding-001"
        )
        
        chroma_client = chromadb.PersistentClient(path=os.environ.get("CHROMA_DB_PATH"))
        collection = chroma_client.get_collection(name="full_database_conversations", embedding_function=google_ef)
        
        count = collection.count()
        print(f"Total conversations logged: {count}")
        
        # Get all documents to find the latest one (not efficient for large DBs but fine for verification)
        all_docs = collection.get()
        if all_docs['ids']:
            last_index = -1
            print("\nMost recent log entry:")
            print(all_docs['documents'][last_index])
            print(all_docs['metadatas'][last_index])
            return True
        else:
            print("No conversations found in the database.")
            return False
            
    except Exception as e:
        print(f"Error verifying logs: {e}")
        return False

if __name__ == "__main__":
    verify_logs()
