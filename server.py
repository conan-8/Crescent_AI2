import sys
import os
import chromadb
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot import get_chroma_db, get_relevant_documents, make_prompt, client
from google.genai import types

app = Flask(__name__)

CORS(app) # Allow your HTML website to talk to this Python script

print("--- Crescent AI Server Starting ---")

# 3. Initialize the Database
# We use the same collection name "family_handbook_1" as your main() function
try:
    db = get_chroma_db("family_handbook_1")
    count = db.count()
    print(f"Database loaded successfully. Documents indexed: {count}")
except Exception as e:
    print(f"CRITICAL ERROR loading database: {e}")
    db = None

# Initialize Conversations Database
try:
    conversations_db = get_chroma_db("conversations")
    print("Conversations database loaded successfully.")
except Exception as e:
    print(f"Error loading conversations database: {e}")
    conversations_db = None

def contextualize_query(history, latest_query):
    if not history:
        return latest_query
    
    history_text = ""
    # Use only the last 3 turns to keep context focused and reduce token usage
    for msg in history[-6:]: 
        role = "User" if msg['role'] == "user" else "AI"
        history_text += f"{role}: {msg['content']}\n"
    
    prompt = f"""
    Given the following conversation history and a follow-up question, rephrase the follow-up question to be a standalone question that includes all necessary context.
    If the follow-up question is already self-contained, return it unchanged.
    
    Chat History:
    {history_text}
    
    Follow-up Question: {latest_query}
    
    Standalone Question:
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.5)
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error contextualizing query: {e}")
        return latest_query

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    # Safety check
    if not db:
        return jsonify({"response": "Error: Database connection failed. Check server console."}), 500

    # Get message from Frontend
    data = request.json
    user_query = data.get('message')
    history = data.get('history', []) # Get history, default to empty list

    if not user_query:
        return jsonify({"error": "No message provided"}), 400

    print(f"\n[User Query]: {user_query}")

    try:
        # --- GREETING HANDLING ---
        greetings = ["hello", "hi", "hey", "how are you", "how are you?"]
        response_text = ""
        
        if user_query.lower().strip() in greetings:
            response_text = "Hello! I am an AI assistant for Crescent School. How can I help you today with information about the school?"
            print(f"[AI Response]: {response_text}")
        else:
            # 0. Contextualize Query (Rewrite if needed)
            search_query = user_query
            if history:
                search_query = contextualize_query(history, user_query)
                print(f"[Rewritten Query]: {search_query}")

            # 1. Retrieve Context using the REWRITTEN query
            passage, metadatas = get_relevant_documents(search_query, db)
            
            # 2. Validation
            if passage == "No relevant information found." or len(passage) < 10:
                response_text = "My purpose is to provide information about Crescent School. Do you have a question about the school that I can assist you with?"
                print(f"[AI Response]: {response_text}")
            else:
                # 3. Construct Prompt (Pass ORIGINAL query to keep flow natural, but use passage from rewritten query)
                prompt = make_prompt(user_query, passage, history)

                # 4. Generate Answer with Gemini
                answer = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(temperature=0.5)
                )
                
                response_text = answer.text.strip()
                
                # Check for standard "no information" responses
                negative_phrases = [
                    "does not contain information",
                    "passage does not mention",
                    "provided passage does not",
                    "i don't have that information",
                    "cannot answer this question"
                ]
                
                if any(phrase in response_text.lower() for phrase in negative_phrases):
                    response_text = "My purpose is to provide information about Crescent School. Do you have a question about the school that I can assist you with?"
                else:
                    # Add source link if available
                    if metadatas:
                        sources = list(set([m.get('source') for m in metadatas if m and m.get('source')]))
                        if sources:
                            response_text += f"\n\nSource: {sources[0]}"

                print(f"[Gemini Answer]: {response_text}")

        # 5. Log Conversation
        if conversations_db:
            try:
                interaction_id = str(uuid.uuid4())
                timestamp = datetime.datetime.now().isoformat()
                log_entry = f"User: {user_query}\nAI: {response_text}"
                conversations_db.add(
                    documents=[log_entry],
                    metadatas=[{"role": "interaction", "timestamp": timestamp}],
                    ids=[interaction_id]
                )
                print(f"Logged interaction {interaction_id} to conversations DB.")
            except Exception as log_error:
                print(f"Error logging conversation: {log_error}")
        
        return jsonify({"response": response_text})

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"response": "I encountered an internal error."}), 500

if __name__ == '__main__':
    print("Server running on http://127.0.0.1:5000")
    print("Keep this window OPEN while using the chatbot!")
    app.run(debug=True, port=5000)