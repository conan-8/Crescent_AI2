import sys
import os
import chromadb
from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chatbot import get_chroma_db, get_relevant_documents, make_prompt, client

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

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    # Safety check
    if not db:
        return jsonify({"response": "Error: Database connection failed. Check server console."}), 500

    # Get message from Frontend
    data = request.json
    user_query = data.get('message')

    if not user_query:
        return jsonify({"error": "No message provided"}), 400

    print(f"\n[User Query]: {user_query}")

    try:
        # --- LOGIC COPIED EXACTLY FROM YOUR chatbot.py MAIN() LOOP ---

        # 1. Retrieve Context
        passage = get_relevant_documents(user_query, db)
        
        # 2. Validation (Logic from your script)
        if passage == "No relevant information found." or len(passage) < 10:
            print("No relevant passage found.")
            return jsonify({"response": "I don't have that information in the family handbook."})

        # 3. Construct Prompt
        prompt = make_prompt(user_query, passage)

        # 4. Generate Answer with Gemini
        # Using the same model "gemini-2.5-flash" defined in your script
        answer = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        response_text = answer.text.strip()
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