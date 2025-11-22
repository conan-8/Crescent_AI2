import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from google import genai
from google.genai import types

client = genai.Client(api_key="AIzaSyCaJ7me7Ans9STNva8-YrNUHf0dPBj6HfI")

def get_chroma_db(name):
    # ADD THIS: Same embedding function as your crawl script
    google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
        api_key="AIzaSyCaJ7me7Ans9STNva8-YrNUHf0dPBj6HfI",
        model_name="gemini-embedding-001",
    )
    
    chroma_client = chromadb.PersistentClient(path=r"C:\crescent_ai_source")
    collection = chroma_client.get_or_create_collection(
        name=name, 
        embedding_function=google_ef  # ADD THIS
    )
    return collection

def print_passages(passages):
    print("\n--- Retrieved Passages ---")
    for i, p in enumerate(passages, 1):
        print(f"Passage {i}:\n{p.strip()}\n")
    print("--------------------------\n")

def get_relevant_documents(query, db):
    try:
        result = db.query(query_texts=[query], n_results=3)
        if result['documents'] and len(result['documents'][0]) > 0:
            passages = result['documents'][0]
            print_passages(passages)
            return "\n\n".join(passages)
        return "No relevant information found."
    except Exception as e:
        print(f"Error querying database: {e}")
        return "Error retrieving documents."

def make_prompt(query, relevant_passage):
    escaped = relevant_passage.replace("'", "").replace('"', "").replace("\n", " ")
    return f"""
You are a helpful assistant that answers questions using the reference passage below.
Please keep your response short, concise, and accurate

QUESTION: {query}
PASSAGE: {escaped}

ANSWER:
"""

def main():
    db = get_chroma_db("family_handbook_1")
    
    # DIAGNOSTIC CODE
    print(f"Database loaded with {db.count()} documents")
    
    # Check what's actually in the database
    peek = db.peek(limit=2)
    print(f"\nFirst document preview: {peek['documents'][0][:200] if peek['documents'] else 'EMPTY'}")
    
    # Try a simple get instead of query
    print("\nTesting basic retrieval...")
    all_docs = db.get(limit=2)
    print(f"Can retrieve documents: {len(all_docs['documents'])} docs found")
    
    print("\nGemini Q&A Console (type 'exit' to quit)\n")

    while True:
        query = input("Ask a question: ").strip()
        if query.lower() in ["exit", "quit"]:
            print("Cyaaaaa!")
            break

        # Add debugging to see what query returns
        print(f"\nSearching for: '{query}'...")
        
        try:
            result = db.query(query_texts=[query], n_results=3)
            print(f"Query returned {len(result['documents'][0])} results")
            
            if result['documents'][0]:
                print(f"First result preview: {result['documents'][0][0][:200]}")
        except Exception as e:
            print(f"Query error: {e}")
            continue

        passage = get_relevant_documents(query, db)
        print(f"\nPassage length: {len(passage)} characters")
        
        if passage == "No relevant information found." or len(passage) < 10:
            print("No relevant passage found, skipping generation.")
            continue
            
        prompt = make_prompt(query, passage)

        try:
            answer = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            print("\nAnswer:", answer.text.strip(), "\n")
        except Exception as e:
            print(f"\nError: {e}\n")

if __name__ == "__main__":
    main()
