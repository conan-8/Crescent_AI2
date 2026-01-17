"""
Enrollment Agent Database Module

This module provides a separate conversation database for the enrollment agent,
allowing it to store and retrieve enrollment-specific conversations independently
from the main chatbot's conversation logs.

Collections:
- enrollment_conversations: Stores all enrollment agent interactions
- enrollment_sessions: Stores enrollment session metadata and progress
"""

import os
import uuid
import datetime
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from dotenv import load_dotenv

load_dotenv()


def get_embedding_function():
    """Get the Google Generative AI embedding function."""
    return embedding_functions.GoogleGenerativeAiEmbeddingFunction(
        api_key=os.environ.get("GEMINI_API_KEY"),
        model_name="gemini-embedding-001"
    )


def get_chroma_client():
    """Get the ChromaDB persistent client."""
    return chromadb.PersistentClient(path=os.environ.get("CHROMA_DB_PATH"))


def get_enrollment_conversations_db():
    """
    Get or create the enrollment conversations collection.

    This collection stores all user-agent interactions for the enrollment agent,
    separate from the main chatbot conversations.

    Returns:
        chromadb.Collection: The enrollment conversations collection
    """
    google_ef = get_embedding_function()
    chroma_client = get_chroma_client()
    collection = chroma_client.get_or_create_collection(
        name="enrollment_conversations",
        embedding_function=google_ef
    )
    return collection


def get_enrollment_sessions_db():
    """
    Get or create the enrollment sessions collection.

    This collection stores enrollment session metadata, including:
    - Session ID and status
    - User information collected during enrollment
    - Progress through enrollment steps

    Returns:
        chromadb.Collection: The enrollment sessions collection
    """
    google_ef = get_embedding_function()
    chroma_client = get_chroma_client()
    collection = chroma_client.get_or_create_collection(
        name="enrollment_sessions",
        embedding_function=google_ef
    )
    return collection


def log_enrollment_conversation(user_message, agent_response, session_id=None, metadata=None):
    """
    Log an enrollment conversation interaction.

    Args:
        user_message (str): The user's message
        agent_response (str): The enrollment agent's response
        session_id (str, optional): Session ID for grouping related conversations
        metadata (dict, optional): Additional metadata to store

    Returns:
        str: The interaction ID
    """
    db = get_enrollment_conversations_db()

    interaction_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().isoformat()

    log_entry = f"User: {user_message}\nAgent: {agent_response}"

    # Build metadata
    doc_metadata = {
        "role": "enrollment_interaction",
        "timestamp": timestamp,
        "session_id": session_id or "no_session"
    }

    # Merge additional metadata if provided
    if metadata:
        doc_metadata.update(metadata)

    db.add(
        documents=[log_entry],
        metadatas=[doc_metadata],
        ids=[interaction_id]
    )

    return interaction_id


def create_enrollment_session(user_identifier=None):
    """
    Create a new enrollment session.

    Args:
        user_identifier (str, optional): Optional user identifier (email, name, etc.)

    Returns:
        str: The session ID
    """
    db = get_enrollment_sessions_db()

    session_id = str(uuid.uuid4())
    timestamp = datetime.datetime.now().isoformat()

    session_data = f"Enrollment session started at {timestamp}"

    metadata = {
        "status": "active",
        "created_at": timestamp,
        "updated_at": timestamp,
        "step": "initial",
        "user_identifier": user_identifier or "anonymous"
    }

    db.add(
        documents=[session_data],
        metadatas=[metadata],
        ids=[session_id]
    )

    return session_id


def update_enrollment_session(session_id, step=None, status=None, collected_data=None):
    """
    Update an enrollment session's metadata.

    Args:
        session_id (str): The session ID to update
        step (str, optional): Current enrollment step
        status (str, optional): Session status (active, completed, abandoned)
        collected_data (dict, optional): Data collected during enrollment

    Returns:
        bool: True if update successful, False otherwise
    """
    db = get_enrollment_sessions_db()

    try:
        # Get existing session
        existing = db.get(ids=[session_id])

        if not existing['ids']:
            print(f"Session {session_id} not found")
            return False

        current_metadata = existing['metadatas'][0] if existing['metadatas'] else {}
        current_document = existing['documents'][0] if existing['documents'] else ""

        # Update metadata
        timestamp = datetime.datetime.now().isoformat()
        current_metadata['updated_at'] = timestamp

        if step:
            current_metadata['step'] = step
        if status:
            current_metadata['status'] = status
        if collected_data:
            # Store collected data as JSON string in metadata
            import json
            current_metadata['collected_data'] = json.dumps(collected_data)

        # Update the session
        db.update(
            ids=[session_id],
            metadatas=[current_metadata],
            documents=[current_document + f"\nUpdated at {timestamp}"]
        )

        return True

    except Exception as e:
        print(f"Error updating session {session_id}: {e}")
        return False


def get_session_conversations(session_id):
    """
    Get all conversations for a specific enrollment session.

    Args:
        session_id (str): The session ID

    Returns:
        list: List of conversation documents with metadata
    """
    db = get_enrollment_conversations_db()

    try:
        results = db.get(
            where={"session_id": session_id}
        )

        conversations = []
        if results['documents']:
            for i, doc in enumerate(results['documents']):
                conversations.append({
                    'id': results['ids'][i],
                    'content': doc,
                    'metadata': results['metadatas'][i] if results['metadatas'] else {}
                })

        # Sort by timestamp
        conversations.sort(key=lambda x: x['metadata'].get('timestamp', ''))

        return conversations

    except Exception as e:
        print(f"Error retrieving conversations for session {session_id}: {e}")
        return []


def get_all_enrollment_conversations(limit=100):
    """
    Get all enrollment conversations.

    Args:
        limit (int): Maximum number of conversations to retrieve

    Returns:
        list: List of all conversation documents with metadata
    """
    db = get_enrollment_conversations_db()

    try:
        results = db.get(limit=limit)

        conversations = []
        if results['documents']:
            for i, doc in enumerate(results['documents']):
                conversations.append({
                    'id': results['ids'][i],
                    'content': doc,
                    'metadata': results['metadatas'][i] if results['metadatas'] else {}
                })

        return conversations

    except Exception as e:
        print(f"Error retrieving enrollment conversations: {e}")
        return []


def get_session_info(session_id):
    """
    Get information about an enrollment session.

    Args:
        session_id (str): The session ID

    Returns:
        dict: Session information including metadata, or None if not found
    """
    db = get_enrollment_sessions_db()

    try:
        results = db.get(ids=[session_id])

        if results['ids']:
            return {
                'id': results['ids'][0],
                'document': results['documents'][0] if results['documents'] else '',
                'metadata': results['metadatas'][0] if results['metadatas'] else {}
            }

        return None

    except Exception as e:
        print(f"Error retrieving session {session_id}: {e}")
        return None


def get_active_sessions():
    """
    Get all active enrollment sessions.

    Returns:
        list: List of active session information
    """
    db = get_enrollment_sessions_db()

    try:
        results = db.get(
            where={"status": "active"}
        )

        sessions = []
        if results['ids']:
            for i, session_id in enumerate(results['ids']):
                sessions.append({
                    'id': session_id,
                    'document': results['documents'][i] if results['documents'] else '',
                    'metadata': results['metadatas'][i] if results['metadatas'] else {}
                })

        return sessions

    except Exception as e:
        print(f"Error retrieving active sessions: {e}")
        return []


def complete_enrollment_session(session_id, final_data=None):
    """
    Mark an enrollment session as completed.

    Args:
        session_id (str): The session ID
        final_data (dict, optional): Final enrollment data to store

    Returns:
        bool: True if successful, False otherwise
    """
    return update_enrollment_session(
        session_id=session_id,
        status="completed",
        step="completed",
        collected_data=final_data
    )


def abandon_enrollment_session(session_id, reason=None):
    """
    Mark an enrollment session as abandoned.

    Args:
        session_id (str): The session ID
        reason (str, optional): Reason for abandonment

    Returns:
        bool: True if successful, False otherwise
    """
    db = get_enrollment_sessions_db()

    try:
        existing = db.get(ids=[session_id])

        if not existing['ids']:
            return False

        current_metadata = existing['metadatas'][0] if existing['metadatas'] else {}
        current_metadata['status'] = 'abandoned'
        current_metadata['updated_at'] = datetime.datetime.now().isoformat()

        if reason:
            current_metadata['abandonment_reason'] = reason

        db.update(
            ids=[session_id],
            metadatas=[current_metadata]
        )

        return True

    except Exception as e:
        print(f"Error abandoning session {session_id}: {e}")
        return False


def get_enrollment_stats():
    """
    Get statistics about enrollment conversations and sessions.

    Returns:
        dict: Statistics including counts and status breakdown
    """
    conversations_db = get_enrollment_conversations_db()
    sessions_db = get_enrollment_sessions_db()

    stats = {
        'total_conversations': 0,
        'total_sessions': 0,
        'active_sessions': 0,
        'completed_sessions': 0,
        'abandoned_sessions': 0
    }

    try:
        stats['total_conversations'] = conversations_db.count()
        stats['total_sessions'] = sessions_db.count()

        # Count by status
        active = sessions_db.get(where={"status": "active"})
        stats['active_sessions'] = len(active['ids']) if active['ids'] else 0

        completed = sessions_db.get(where={"status": "completed"})
        stats['completed_sessions'] = len(completed['ids']) if completed['ids'] else 0

        abandoned = sessions_db.get(where={"status": "abandoned"})
        stats['abandoned_sessions'] = len(abandoned['ids']) if abandoned['ids'] else 0

    except Exception as e:
        print(f"Error getting enrollment stats: {e}")

    return stats


def clear_enrollment_data():
    """
    Clear all enrollment data (conversations and sessions).

    WARNING: This is destructive and cannot be undone.

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        chroma_client = get_chroma_client()

        # Delete collections if they exist
        try:
            chroma_client.delete_collection("enrollment_conversations")
            print("Deleted enrollment_conversations collection")
        except Exception:
            pass

        try:
            chroma_client.delete_collection("enrollment_sessions")
            print("Deleted enrollment_sessions collection")
        except Exception:
            pass

        return True

    except Exception as e:
        print(f"Error clearing enrollment data: {e}")
        return False


# Main function for testing
def main():
    """Test the enrollment database functionality."""
    print("=== Enrollment Database Test ===\n")

    # Get stats
    stats = get_enrollment_stats()
    print(f"Current stats: {stats}\n")

    # Create a test session
    print("Creating test enrollment session...")
    session_id = create_enrollment_session(user_identifier="test@example.com")
    print(f"Created session: {session_id}\n")

    # Log a conversation
    print("Logging test conversation...")
    interaction_id = log_enrollment_conversation(
        user_message="I want to enroll my child",
        agent_response="I'd be happy to help you with the enrollment process. What grade will your child be entering?",
        session_id=session_id,
        metadata={"step": "grade_selection"}
    )
    print(f"Logged interaction: {interaction_id}\n")

    # Update session
    print("Updating session progress...")
    update_enrollment_session(
        session_id=session_id,
        step="grade_selection",
        collected_data={"inquiry_type": "new_student"}
    )

    # Get session info
    print("Retrieving session info...")
    session_info = get_session_info(session_id)
    print(f"Session info: {session_info}\n")

    # Get session conversations
    print("Retrieving session conversations...")
    conversations = get_session_conversations(session_id)
    print(f"Found {len(conversations)} conversations\n")

    # Get updated stats
    stats = get_enrollment_stats()
    print(f"Updated stats: {stats}\n")

    print("=== Test Complete ===")


if __name__ == "__main__":
    main()
