import chromadb
from chromadb import EmbeddingFunction, Documents, Embeddings, QueryResult
from google import genai
from google.genai import types

client = genai.Client(api_key="AIzaSyCaJ7me7Ans9STNva8-YrNUHf0dPBj6HfI")

def get_chroma_db(name):
    chroma_client = chromadb.PersistentClient(path=r"C:\crescent_ai_source") # u will have to change this for ur local db or if u have never runned this script before
    collection = chroma_client.get_or_create_collection(name=name)
    return collection

def get_relevant_documents(query, db):
    result = db.query(query_texts = [query], n_results = 1)
    return result['documents'][0]

def make_prompt(query, relevant_passage):
    escaped = relevant_passage.replace("'", "").replace('"', "").replace("\n", " ")
    return f"""
You are a helpful assistant that answers questions using the reference passage below.
Keep it friendly, simple, and complete.

QUESTION: {query}
PASSAGE: {escaped}

ANSWER:
"""

def main():
    db = get_chroma_db("family_handbook_1")
    print("Gemini Q&A Console (type 'exit' to quit)\n")

    while True:
        query = input("Ask a question: ").strip()
        if query.lower() in ["exit", "quit"]:
            print("Cyaaaaa!")
            break

        passage = get_relevant_documents(query, db)
        if len(passage) > 0:
            passage = passage[0]
        else:
            passage = 'no answer'
        prompt = make_prompt(query, passage)

        answer = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        print("\nAnswer:", answer.text.strip(), "\n")

if __name__ == "__main__":
    main()
