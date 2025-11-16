import chromadb
import chromadb.utils.embedding_functions as embedding_functions

google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
    api_key="AIzaSyCaJ7me7Ans9STNva8-YrNUHf0dPBj6HfI",
    model_name="gemini-embedding-001",
    task_type="RETRIEVAL_DOCUMENT"
)

chroma_client = chromadb.PersistentClient(path=r"C:\crescent_ai_source")
collection = chroma_client.get_or_create_collection(name="family_handbook_1", embedding_function=google_ef)

print(f"Collection count: {collection.count()}")
print(f"Collection peek: {collection.peek()}")