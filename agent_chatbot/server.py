import sys
import os
import chromadb
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import uuid
import datetime
import hashlib
import time
from collections import defaultdict

# Add Database folder to path BEFORE importing modules from it
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Database"))

from snapshot_db import rollback, list_snapshots
from chatbot import get_chroma_db, get_relevant_documents, make_prompt, client



# --- Client Fingerprinting ---
def get_client_fingerprint():
    """Generate a unique fingerprint for a client based on request headers."""
    ip = request.remote_addr or ''
    user_agent = request.headers.get('User-Agent', '')
    accept_language = request.headers.get('Accept-Language', '')
    accept_encoding = request.headers.get('Accept-Encoding', '')

    fingerprint_data = f"{ip}|{user_agent}|{accept_language}|{accept_encoding}"
    fingerprint_hash = hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]
    return fingerprint_hash

# --- Spam Detection ---
# Store message history per fingerprint: {fingerprint: [(timestamp, message), ...]}
spam_tracker = defaultdict(list)

def cleanup_old_messages(fingerprint, max_age_seconds=300):
    """Remove messages older than max_age_seconds (default 5 minutes)."""
    current_time = time.time()
    spam_tracker[fingerprint] = [
        (ts, msg) for ts, msg in spam_tracker[fingerprint]
        if current_time - ts < max_age_seconds
    ]

def is_gibberish(message):
    """Check if message is gibberish (less than 50% alphanumeric, only for messages > 10 chars)."""
    if len(message) <= 10:
        return False
    alphanumeric_count = sum(1 for c in message if c.isalnum())
    return alphanumeric_count / len(message) < 0.5

def check_spam(fingerprint, message):
    """
    Check if message is spam. Returns (is_spam, spam_type) tuple.
    spam_type: 'duplicate', 'too_fast', 'gibberish', or None
    """
    current_time = time.time()

    # Clean up old entries first
    cleanup_old_messages(fingerprint)

    # Check for gibberish
    if is_gibberish(message):
        return True, 'gibberish'

    # Check for duplicate messages (same message 2+ times within 5 minutes)
    message_lower = message.lower().strip()
    duplicate_count = sum(1 for ts, msg in spam_tracker[fingerprint] if msg.lower().strip() == message_lower)
    if duplicate_count >= 2:
        return True, 'duplicate'

    # Check for rapid-fire messaging (10+ messages within 60 seconds)
    recent_messages = [ts for ts, msg in spam_tracker[fingerprint] if current_time - ts < 60]
    if len(recent_messages) >= 10:
        return True, 'too_fast'

    # Not spam - record this message
    spam_tracker[fingerprint].append((current_time, message))
    return False, None

SPAM_RESPONSES = {
    'duplicate': "Please don't send the same message repeatedly.",
    'too_fast': "You're sending messages too quickly. Please slow down.",
    'gibberish': "Please enter a valid question about Crescent School."
}

app = Flask(__name__)
CORS(app) # Allow your HTML website to talk to this Python script

# Initialize Rate Limiter (uses client fingerprint instead of just IP)
limiter = Limiter(
    get_client_fingerprint,
    app=app,
    default_limits=["200 per day", "100 per hour"],
    storage_uri="memory://",
)

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"response": "You have sent too many messages recently. Please wait a minute before trying again."}), 200

# --- Health Check Endpoint ---
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

# --- END Health Check ---

# --- Static Files Route for Main Page assets ---
@app.route('/Main Page_files/<path:filename>', methods=['GET'])
def serve_main_page_files(filename):
    """Serve static files from Main Page_files folder."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_dir = os.path.join(base_dir, 'frontend')
    files_dir = os.path.join(frontend_dir, 'Main Page_files')
    file_path = os.path.join(files_dir, filename)

    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return "File not found", 404

# --- Also serve chatbot widget files ---
@app.route('/chatbot.css', methods=['GET'])
def serve_chatbot_css():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    css_path = os.path.join(base_dir, 'frontend', 'chatbot.css')
    if os.path.exists(css_path):
        return send_file(css_path)
    return "File not found", 404

@app.route('/chatbot.js', methods=['GET'])
def serve_chatbot_js():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    js_path = os.path.join(base_dir, 'frontend', 'chatbot.js')
    if os.path.exists(js_path):
        return send_file(js_path)
    return "File not found", 404

@app.route('/chatbot_iframe.html', methods=['GET'])
def serve_chatbot_iframe():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    iframe_path = os.path.join(base_dir, 'frontend', 'chatbot_iframe.html')
    if os.path.exists(iframe_path):
        return send_file(iframe_path)
    return "File not found", 404

# --- Homepage Route ---
@app.route('/', methods=['GET'])
def home():
    # Get the path to the frontend directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_dir = os.path.join(base_dir, 'frontend')
    html_file = 'Main Page.html'

    # Use send_from_directory which properly handles MIME types
    if os.path.exists(os.path.join(frontend_dir, html_file)):
        return send_from_directory(frontend_dir, html_file)
    else:
        # Fallback to JSON if HTML not found
        return jsonify({
            "message": "Crescent AI Server is running",
            "endpoints": {
                "health": "/health (GET)",
                "chat": "/chat (POST) - requires JSON body"
            }
        }), 200
    
print("--- Crescent AI Server Starting ---")

# 3. Initialize the Database
try:
    full_database = get_chroma_db("full_database")
    count = full_database.count()
    print(f"Full database loaded successfully. Documents indexed: {count}")

    if count == 0:
        print("Full database is empty — attempting snapshot restore...")
        try:
            snapshots = list_snapshots("full_database")
            if snapshots:
                rollback("full_database")
                full_database = get_chroma_db("full_database")
                restored_count = full_database.count()
                print(f"Restored {restored_count} documents from snapshot.")
            else:
                print("No snapshots available for restore.")
        except SystemExit:
            print("Snapshot restore failed — no snapshots found.")
        except Exception as restore_err:
            print(f"Snapshot restore failed: {restore_err}")

except Exception as e:
    print(f"CRITICAL ERROR loading full database: {e}")
    full_database = None

# Initialize Conversations Database
try:
    conversations_db = get_chroma_db("conversations")
    print("Conversations database loaded successfully.")
except Exception as e:
    print(f"Error loading conversations database: {e}")
    conversations_db = None

# Initialize Full Database Conversations Database
try:
    full_database_conversations = get_chroma_db("full_database_conversations")
    print("Full database conversations loaded successfully.")
except Exception as e:
    print(f"Error loading full database conversations: {e}")
    full_database_conversations = None

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
        completion = client.chat.completions.create(
            model="qwen/qwen3.5-397b-a17b",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            extra_body={"reasoning": {"enabled": False}}
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error contextualizing query: {e}")
        return latest_query

def get_best_link(query, response_text, sources):
    if not sources:
        return None
    if len(sources) == 1:
        return sources[0]
        
    prompt = f"""Given the user query: "{query}"
And the following response generated:
"{response_text}"

Which of these source links is the MOST relevant to the response?
Links:
{chr(10).join([f"- {s}" for s in sources])}

Please output ONLY the single best URL from the list above, nothing else."""
    
    try:
        completion = client.chat.completions.create(
            model="qwen/qwen3.5-397b-a17b",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that selects the best link. Output only the URL itself."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            extra_body={"reasoning": {"enabled": False}}
        )
        best_link = completion.choices[0].message.content.strip()
        # Verify the returned link is actually in our sources
        for s in sources:
            if s in best_link:
                return s
        return sources[0] # Fallback if LLM failed
    except Exception as e:
        print(f"Error determining best link: {e}")
        return sources[0]


@app.route('/chat', methods=['POST'])
@limiter.limit("20 per minute")
def chat_endpoint():
    # Safety check
    if not full_database:
        return jsonify({"response": "Error: Enrollment database connection failed. Check server console."}), 500

    # Get message from Frontend
    data = request.json
    user_query = data.get('message')
    history = data.get('history', [])
    language = data.get('language', 'English')

    if not user_query:
        return jsonify({"error": "No message provided"}), 400

    print(f"\n[Enrollment User Query]: {user_query}")

    # --- Spam Detection ---
    fingerprint = get_client_fingerprint()
    is_spam, spam_type = check_spam(fingerprint, user_query)
    if is_spam:
        print(f"[Spam Detected]: {spam_type} from {fingerprint}")
        return jsonify({"response": SPAM_RESPONSES[spam_type]}), 200

    try:
        # --- GREETING HANDLING ---
        greetings = ["hello", "hi", "hey", "how are you", "how are you?"]
        response_text = ""
        
        if user_query.lower().strip() in greetings:
            response_text = "Hello! I am the Crescent School AI Assistant, how can I help you?"
            print(f"[AI Response]: {response_text}")
        else:
            # 0. Contextualize Query
            search_query = user_query
            if history:
                search_query = contextualize_query(history, user_query)
                print(f"[Rewritten Query]: {search_query}")

            # 1. Retrieve Context
            passage, metadatas = get_relevant_documents(search_query, full_database)
            
            # 2. Validation
            if passage == "No relevant information found.":
                response_text = "I specialize in information relevant to Crescent School. Do you have a question about the school that I can assist you with?"
                print(f"[AI Response]: {response_text}")
            else:
                # 3. Construct Prompt (Specialized for enrollment agent)
                prompt = make_prompt(user_query, passage, history, language)
                # Maybe modify prompt slightly for enrollment context if needed, 
                # but standard make_prompt works if passage is good.

                # 4. Generate Answer with OpenRouter
                completion = client.chat.completions.create(
                    model="qwen/qwen3.5-397b-a17b",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    extra_body={"reasoning": {"enabled": False}}
                )
                
                response_text = completion.choices[0].message.content.strip()
                
                # Check for standard "no information" responses
                negative_phrases = [
                    "does not contain information",
                    "passage does not mention",
                    "provided passage does not",
                    "i don't have that information",
                    "cannot answer this question"
                ]
                
                if any(phrase in response_text.lower() for phrase in negative_phrases):
                     response_text = "I specialize in information relevant to Crescent School. Do you have a question about the school that I can assist you with?"
                else:
                    # Add source link
                    if metadatas:
                        sources = list(set([m.get('source') for m in metadatas if m and m.get('source')]))
                        if sources:
                            best_link = get_best_link(user_query, response_text, sources)
                            if best_link:
                                response_text += f"\n\nSource: {best_link}"
                print(f"[Enrollment Answer]: {response_text}")

        # 5. Log Conversation
        if full_database_conversations:
            try:
                interaction_id = str(uuid.uuid4())
                timestamp = datetime.datetime.now().isoformat()
                log_entry = f"User: {user_query}\nAI: {response_text}"
                full_database_conversations.add(
                    documents=[log_entry],
                    metadatas=[{"role": "interaction", "timestamp": timestamp}],
                    ids=[interaction_id]
                )
            except Exception as log_error:
                print(f"Error logging enrollment conversation: {log_error}")

        
        return jsonify({"response": response_text})

    except Exception as e:
        print(f"Error processing enrollment request: {e}")
        return jsonify({"response": "I encountered an internal error."}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"Server running on port {port}")
    # Host must be 0.0.0.0 for Render to detect the open port
    app.run(host='0.0.0.0', port=port)
