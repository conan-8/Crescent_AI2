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
import chromadb
from database import get_chroma_db

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


def create_snapshot(collection, collection_name: str) -> str:
    """
    Export all documents, embeddings, and metadata from collection to a JSON file.
    Returns the snapshot timestamp string.
    """
    col_dir = _collection_dir(collection_name)
    os.makedirs(col_dir, exist_ok=True)

    result = collection.get(include=["documents", "embeddings", "metadatas"])
    ids = result.get("ids") or []
    documents = result.get("documents") or []
    metadatas = result.get("metadatas") or []
    raw_embeddings = result.get("embeddings") or []
    embeddings = [e.tolist() if hasattr(e, "tolist") else list(e) for e in raw_embeddings]

    timestamp = _timestamp()
    snapshot = {
        "collection": collection_name,
        "created_at": timestamp,
        "document_count": len(ids),
        "ids": ids,
        "documents": documents,
        "metadatas": metadatas,
        "embeddings": embeddings,
    }

    with open(_snapshot_path(collection_name, timestamp), "w") as f:
        json.dump(snapshot, f)

    pruned = prune_snapshots(collection_name)
    print(f"Snapshot created: {timestamp} ({len(ids)} documents). {pruned} old snapshot(s) pruned.")
    return timestamp


def rollback(collection_name: str, snapshot_id: str = None):
    """
    Restore a collection from a snapshot. Uses most recent if snapshot_id is None.
    Exits with code 1 if no snapshots exist or the given snapshot_id is not found.
    """
    snapshots = list_snapshots(collection_name)
    if not snapshots:
        print(f"Error: No snapshots found for collection '{collection_name}'.")
        raise SystemExit(1)

    if snapshot_id:
        match = [s for s in snapshots if s["timestamp"] == snapshot_id]
        if not match:
            available = "\n".join(
                f"  {s['timestamp']}  {s['document_count']} documents" for s in snapshots
            )
            print(f"Error: Snapshot '{snapshot_id}' not found. Available snapshots:\n{available}")
            raise SystemExit(1)
        target = match[0]
    else:
        target = snapshots[0]  # newest first

    with open(target["path"]) as f:
        data = json.load(f)

    chroma_client = chromadb.PersistentClient(path=os.environ.get("CHROMA_DB_PATH"))
    chroma_client.delete_collection(collection_name)
    collection = get_chroma_db(collection_name)

    ids = data["ids"]
    documents = data["documents"]
    metadatas = data["metadatas"]
    embeddings = data["embeddings"]

    batch_size = 100
    for i in range(0, len(ids), batch_size):
        collection.add(
            ids=ids[i:i + batch_size],
            documents=documents[i:i + batch_size],
            metadatas=metadatas[i:i + batch_size],
            embeddings=embeddings[i:i + batch_size],
        )

    print(
        f"Rolled back {collection_name} to snapshot {target['timestamp']} "
        f"({data['document_count']} documents restored)."
    )
