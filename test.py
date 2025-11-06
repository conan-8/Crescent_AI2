import chromadb
chroma_client = chromadb.PersistentClient(path="C:\crescent_ai_source")

collection = chroma_client.get_collection(name="family_handbook")


results = collection.query(
    query_texts=["skibidi toielty"],
    n_results=2 
)
print(results)


