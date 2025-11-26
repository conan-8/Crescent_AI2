import chromadb
import chromadb.utils.embedding_functions as embedding_functions
import time

def verify_logs():
    try:
        google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
            api_key="AIzaSyCaJ7me7Ans9STNva8-YrNUHf0dPBj6HfI",
            model_name="gemini-embedding-001"
        )
        
        chroma_client = chromadb.PersistentClient(path=r"C:\crescent_ai_source")
        collection = chroma_client.get_collection(name="conversations", embedding_function=google_ef)
        
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
