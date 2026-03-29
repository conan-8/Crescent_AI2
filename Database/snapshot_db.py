"""
snapshot_db.py — Snapshot and rollback support for ChromaDB collections.

Usage:
    python Database/snapshot_db.py --collection full_database
        Take a manual snapshot.

    python Database/snapshot_db.py --list --collection full_database
        List available snapshots (newest first).

    python Database/snapshot_db.py --rollback --collection full_database
        Rollback to the most recent snapshot.

    python Database/snapshot_db.py --rollback --collection full_database --snapshot 2026-03-29T09-12-33
        Rollback to a specific snapshot.
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SNAPSHOTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snapshots")
MAX_SNAPSHOTS = 5


def _collection_dir(collection_name: str) -> str:
    return os.path.join(SNAPSHOTS_DIR, collection_name)


def _snapshot_path(collection_name: str, timestamp: str) -> str:
    # used by create_snapshot (added in the next task)
    return os.path.join(_collection_dir(collection_name), f"{timestamp}_snap.json")


def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H-%M-%S")


def list_snapshots(collection_name: str) -> list:
    """
    Return list of snapshot dicts (newest first).
    Each dict has keys: 'timestamp', 'path', 'document_count'.
    """
    col_dir = _collection_dir(collection_name)
    if not os.path.isdir(col_dir):
        return []
    files = sorted(
        [f for f in os.listdir(col_dir) if f.endswith("_snap.json")],
        reverse=True,
    )
    snapshots = []
    for fname in files:
        path = os.path.join(col_dir, fname)
        try:
            with open(path) as f:
                data = json.load(f)
            snapshots.append({
                "timestamp": data["created_at"],
                "path": path,
                "document_count": data["document_count"],
            })
        except (json.JSONDecodeError, KeyError):
            pass
    return snapshots


def prune_snapshots(collection_name: str, max_keep: int = MAX_SNAPSHOTS) -> int:
    """
    Delete oldest snapshots beyond max_keep. Returns count deleted.
    """
    col_dir = _collection_dir(collection_name)
    if not os.path.isdir(col_dir):
        return 0
    files = sorted(f for f in os.listdir(col_dir) if f.endswith("_snap.json"))
    if max_keep <= 0:
        to_delete = files
    elif len(files) > max_keep:
        to_delete = files[:-max_keep]
    else:
        to_delete = []
    for fname in to_delete:
        os.remove(os.path.join(col_dir, fname))
    return len(to_delete)
