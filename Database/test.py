import os
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from dotenv import load_dotenv

load_dotenv()

google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
    api_key=os.environ.get("GEMINI_API_KEY"),
    model_name="gemini-embedding-001",
    task_type="RETRIEVAL_DOCUMENT"
)

chroma_client = chromadb.PersistentClient(path=os.environ.get("CHROMA_DB_PATH"))
collection = chroma_client.get_or_create_collection(name="full_database", embedding_function=google_ef)

print(f"Collection count: {collection.count()}")
print(f"Collection peek: {collection.peek()}")