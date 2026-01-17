"""
Enrollment Database Clear Utility

This script clears all enrollment data from the database.
WARNING: This operation is destructive and cannot be undone.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from enrollment_database import clear_enrollment_data, get_enrollment_stats


def main():
    """Clear enrollment database with confirmation."""

    print("=== Enrollment Database Clear Utility ===\n")

    # Show current stats
    stats = get_enrollment_stats()
    print("Current enrollment database contents:")
    print(f"  - Conversations: {stats['total_conversations']}")
    print(f"  - Sessions: {stats['total_sessions']}")
    print()

    if stats['total_conversations'] == 0 and stats['total_sessions'] == 0:
        print("Database is already empty. Nothing to clear.")
        return

    # Confirmation
    print("WARNING: This will permanently delete all enrollment data!")
    confirm = input("Type 'DELETE' to confirm: ").strip()

    if confirm != "DELETE":
        print("Operation cancelled.")
        return

    # Clear data
    print("\nClearing enrollment data...")
    success = clear_enrollment_data()

    if success:
        print("Enrollment data cleared successfully.")

        # Verify
        new_stats = get_enrollment_stats()
        print(f"\nVerification - Conversations: {new_stats['total_conversations']}, Sessions: {new_stats['total_sessions']}")
    else:
        print("Error clearing enrollment data.")


if __name__ == "__main__":
    main()
