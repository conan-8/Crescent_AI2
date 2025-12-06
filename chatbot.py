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
            metadatas = result['metadatas'][0] if 'metadatas' in result else []
            print_passages(passages)
            return "\n\n".join(passages), metadatas
        return "No relevant information found.", []
    except Exception as e:
        print(f"Error querying database: {e}")
        return "Error retrieving documents.", []

def make_prompt(query, relevant_passage, history=[]):
    escaped = relevant_passage.replace("'", "").replace('"', "").replace("\n", " ")
    
    history_text = ""
    if history:
        history_text = "HISTORY:\n"
        for msg in history:
            role = "User" if msg['role'] == "user" else "AI"
            history_text += f"{role}: {msg['content']}\n"
        history_text += "\n"

    return f"""
You are a helpful assistant that answers questions using the reference passage below.
Please keep your response short, concise, and accurate.
Use the conversation history to understand context if needed.

{history_text}
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

        # --- GREETING HANDLING ---
        greetings = ["hello", "hi", "hey", "how are you", "how are you?"]
        if query.lower().strip() in greetings:
            print("\nAnswer: Hello! I am an AI assistant for Crescent School. How can I help you today with information about the school?\n")
            continue
        
        try:
            result = db.query(query_texts=[query], n_results=3)
            print(f"Query returned {len(result['documents'][0])} results")
            
            if result['documents'][0]:
                print(f"First result preview: {result['documents'][0][0][:200]}")
        except Exception as e:
            print(f"Query error: {e}")
            continue

        passage, metadatas = get_relevant_documents(query, db)
        print(f"\nPassage length: {len(passage)} characters")
        
        if passage == "No relevant information found." or len(passage) < 10:
            print("My purpose is to provide information about Crescent School. Do you have a question about the school that I can assist you with?")
            continue
            
        prompt = make_prompt(query, passage)

        try:
            answer = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            response_text = answer.text.strip()
            
            # Check for standard "no information" responses from Gemini
            negative_phrases = [
                "does not contain information",
                "passage does not mention",
                "provided passage does not",
                "i don't have that information"
            ]
            
            if any(phrase in response_text.lower() for phrase in negative_phrases):
                response_text = "My purpose is to provide information about Crescent School. Do you have a question about the school that I can assist you with?"
            else:
                # Add source link if available
                if metadatas:
                    sources = list(set([m.get('source') for m in metadatas if m and m.get('source')]))
                    if sources:
                        response_text += f"\n\nSource: {sources[0]}"

            print("\nAnswer:", response_text, "\n")
        except Exception as e:
            print(f"\nError: {e}\n")

if __name__ == "__main__":
    main()
