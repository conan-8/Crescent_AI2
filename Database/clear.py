import chromadb

# Connect to your existing database
chroma_client = chromadb.PersistentClient(path=r"C:\crescent_ai_source")

# Delete the old collection
try:
    chroma_client.delete_collection(name="enrollment_info")
    print("✓ Successfully deleted 'enrollment_info' collection")
except Exception as e:
    print(f"Error deleting collection: {e}")

# Verify it's gone
collections = chroma_client.list_collections()
print(f"\nRemaining collections: {[c.name for c in collections]}")

print("\nYou can now run your database.py script with the new extraction prompt!")