import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from google import genai
from google.genai import types
import os
import sys

# Configuration
API_KEY = "AIzaSyCaJ7me7Ans9STNva8-YrNUHf0dPBj6HfI"
DB_PATH = r"C:\crescent_ai_source"
COLLECTION_NAME = "conversations"
MODEL_NAME = "gemini-2.5-flash"

def get_chroma_collection():
    """Connects to the ChromaDB collection."""
    try:
        google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
            api_key=API_KEY,
            model_name="gemini-embedding-001"
        )
        chroma_client = chromadb.PersistentClient(path=DB_PATH)
        collection = chroma_client.get_collection(name=COLLECTION_NAME, embedding_function=google_ef)
        return collection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def parse_conversations(documents):
    """Parses raw log strings into structured data."""
    parsed_data = []
    for doc in documents:
        try:
            # Expected format: "User: [query]\nAI: [response]"
            parts = doc.split("\nAI: ", 1)
            if len(parts) == 2:
                user_query = parts[0].replace("User: ", "").strip()
                ai_response = parts[1].strip()
                parsed_data.append({"query": user_query, "response": ai_response})
        except Exception:
            continue
    return parsed_data

def analyze_with_gemini(conversations):
    """Sends the conversation data to Gemini for analysis."""
    if not conversations:
        return "No conversations found to analyze."

    # Prepare the data for the prompt
    conversation_text = ""
    for i, conv in enumerate(conversations, 1):
        conversation_text += f"Interaction {i}:\nUser: {conv['query']}\nAI: {conv['response']}\n\n"

    import datetime
    current_date = datetime.datetime.now().strftime("%B %d, %Y")

    prompt = f"""
    You are an expert data analyst for a school chatbot. 
    Analyze the following conversation logs and generate a report.
    
    CURRENT DATE: {current_date}

    DATA:
    {conversation_text}

    YOUR TASK:
    1. **Identify Trends**: What are the top 3-5 most frequent topics or questions asked?
    2. **Unanswered Questions**: Identify questions where the AI failed to provide a helpful answer (e.g., responded with "I don't have that information" or similar).
    3. **Content Gaps**: Based on the unanswered questions, what specific information should be added to the handbook/database?
    4. **Recommendations**: Suggest any improvements for the chatbot's responses or what information needs to be added to the school website in order to produce a satisfying answer to the user's query.

    OUTPUT FORMAT:
    Produce a clean Markdown report. Start the report with the date provided above.
    """

    try:
        client = genai.Client(api_key=API_KEY)
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error during AI analysis: {e}"

def main():
    print("--- Starting Conversation Analysis ---")
    
    # 1. Fetch Data
    collection = get_chroma_collection()
    if not collection:
        return

    print("Fetching conversation logs...")
    all_docs = collection.get()
    documents = all_docs['documents']
    
    if not documents:
        print("No conversations found in the database.")
        return

    print(f"Found {len(documents)} interactions.")

    # 2. Parse Data
    parsed_conversations = parse_conversations(documents)
    
    # 3. Analyze
    print("Analyzing with Gemini...")
    report = analyze_with_gemini(parsed_conversations)

    # 4. Output
    print("\n--- Analysis Report ---\n")
    print(report)
    
    with open("analysis_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("\nReport saved to 'analysis_report.md'")

if __name__ == "__main__":
    main()
