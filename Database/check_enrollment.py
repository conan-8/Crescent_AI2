"""
Enrollment Database Inspection Utility

This script allows you to inspect the enrollment database collections,
view conversations, sessions, and statistics.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enrollment_database import (
    get_enrollment_conversations_db,
    get_enrollment_sessions_db,
    get_enrollment_stats,
    get_all_enrollment_conversations,
    get_active_sessions,
    get_session_conversations
)


def print_separator(title=""):
    """Print a visual separator."""
    if title:
        print(f"\n{'='*20} {title} {'='*20}")
    else:
        print("=" * 50)


def check_enrollment_databases():
    """Check and display enrollment database information."""

    print_separator("ENROLLMENT DATABASE STATUS")

    # Get statistics
    stats = get_enrollment_stats()
    print("\n--- Statistics ---")
    print(f"Total Conversations: {stats['total_conversations']}")
    print(f"Total Sessions: {stats['total_sessions']}")
    print(f"  - Active: {stats['active_sessions']}")
    print(f"  - Completed: {stats['completed_sessions']}")
    print(f"  - Abandoned: {stats['abandoned_sessions']}")

    # Show recent conversations
    print_separator("RECENT CONVERSATIONS")
    conversations = get_all_enrollment_conversations(limit=10)

    if not conversations:
        print("\nNo enrollment conversations found.")
    else:
        print(f"\nShowing {len(conversations)} most recent conversations:\n")
        for conv in conversations:
            print(f"ID: {conv['id']}")
            print(f"Timestamp: {conv['metadata'].get('timestamp', 'N/A')}")
            print(f"Session: {conv['metadata'].get('session_id', 'N/A')}")
            print(f"Content Preview: {conv['content'][:200]}...")
            print("-" * 40)

    # Show active sessions
    print_separator("ACTIVE SESSIONS")
    active_sessions = get_active_sessions()

    if not active_sessions:
        print("\nNo active enrollment sessions found.")
    else:
        print(f"\nFound {len(active_sessions)} active sessions:\n")
        for session in active_sessions:
            print(f"Session ID: {session['id']}")
            print(f"Created: {session['metadata'].get('created_at', 'N/A')}")
            print(f"Current Step: {session['metadata'].get('step', 'N/A')}")
            print(f"User: {session['metadata'].get('user_identifier', 'anonymous')}")

            # Get conversation count for this session
            session_convs = get_session_conversations(session['id'])
            print(f"Conversations: {len(session_convs)}")
            print("-" * 40)

    print_separator()
    print("\nEnrollment database check complete.")


def interactive_mode():
    """Run in interactive mode for detailed inspection."""
    print("\n=== Enrollment Database Inspector ===")
    print("Commands: stats, convs, sessions, session <id>, quit\n")

    while True:
        cmd = input("> ").strip().lower()

        if cmd == "quit" or cmd == "exit":
            print("Goodbye!")
            break

        elif cmd == "stats":
            stats = get_enrollment_stats()
            print(f"\nStatistics: {stats}\n")

        elif cmd == "convs":
            conversations = get_all_enrollment_conversations(limit=20)
            print(f"\nFound {len(conversations)} conversations:")
            for conv in conversations:
                print(f"  [{conv['id'][:8]}...] {conv['metadata'].get('timestamp', 'N/A')}")
            print()

        elif cmd == "sessions":
            sessions_db = get_enrollment_sessions_db()
            all_sessions = sessions_db.get(limit=20)
            if all_sessions['ids']:
                print(f"\nFound {len(all_sessions['ids'])} sessions:")
                for i, sid in enumerate(all_sessions['ids']):
                    meta = all_sessions['metadatas'][i] if all_sessions['metadatas'] else {}
                    print(f"  [{sid[:8]}...] Status: {meta.get('status', 'N/A')}, Step: {meta.get('step', 'N/A')}")
            else:
                print("\nNo sessions found.")
            print()

        elif cmd.startswith("session "):
            session_id = cmd.split(" ", 1)[1]
            convs = get_session_conversations(session_id)
            print(f"\nConversations for session {session_id[:8]}...:")
            for conv in convs:
                print(f"\n{conv['content']}")
                print(f"  [{conv['metadata'].get('timestamp', 'N/A')}]")
            print()

        else:
            print("Unknown command. Try: stats, convs, sessions, session <id>, quit")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-i":
        interactive_mode()
    else:
        check_enrollment_databases()
