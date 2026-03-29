# ChromaDB Collection Rollback — Design Spec

**Date:** 2026-03-29
**Status:** Approved

---

## Overview

Add snapshot and rollback support for individual ChromaDB collections. When a crawl produces bad data, the operator can instantly restore a collection to its last known-good state without re-crawling or re-embedding anything.

---

## Architecture & File Layout

A new module `Database/snapshot_db.py` handles all snapshot/rollback logic. It is self-contained and imported by `update_db.py` to trigger automatic snapshots before any destructive update.

```
Database/
  snapshot_db.py        ← new: snapshot, rollback, list, prune logic
  update_db.py          ← modified: auto-snapshot before any update run
snapshots/
  full_database/
    2026-03-29T14-05-00_snap.json
    2026-03-29T09-12-33_snap.json
    ...                 ← up to 5 kept, oldest pruned automatically
  enrollment_info/
    ...
```

Snapshots live in `Database/snapshots/<collection-name>/`. The path is a constant in `snapshot_db.py`.

---

## Snapshot Format

Each snapshot is a single JSON file named by timestamp: `YYYY-MM-DDTHH-MM-SS_snap.json`.

```json
{
  "collection": "full_database",
  "created_at": "2026-03-29T14:05:00",
  "document_count": 87,
  "ids": ["url_chunk_0", "url_chunk_1"],
  "documents": ["chunk text...", "..."],
  "metadatas": [{"source": "https://..."}, {"source": "https://..."}],
  "embeddings": [[0.12, -0.34, ...], [...]]
}
```

Embeddings are stored so that rollback is instant — no Gemini API call is needed to restore.

---

## CLI Interface

`snapshot_db.py` is both importable (for `update_db.py` integration) and runnable as a CLI script.

```bash
# Take a manual snapshot of a collection
python Database/snapshot_db.py --collection full_database

# List available snapshots for a collection
python Database/snapshot_db.py --list --collection full_database

# Rollback to most recent snapshot
python Database/snapshot_db.py --rollback --collection full_database

# Rollback to a specific snapshot by timestamp ID
python Database/snapshot_db.py --rollback --collection full_database --snapshot 2026-03-29T09-12-33
```

`update_db.py` calls `create_snapshot(collection)` silently before processing any URLs — same logic as the manual command, same 5-snapshot cap enforced automatically.

`--list` output format (one line per snapshot, newest first):
```
2026-03-29T14-05-00  87 documents
2026-03-29T09-12-33  85 documents
```
The timestamp shown is the value to pass to `--snapshot`.

---

## Rollback Behavior

When `--rollback` is executed:

1. Load the target snapshot JSON (most recent, or the one specified by `--snapshot`)
2. Delete the entire existing collection via `client.delete_collection(name)`
3. Recreate the collection using `get_chroma_db(name)` (same embedding function)
4. Re-add all ids, documents, metadatas, and embeddings from the snapshot in batches of 100
5. Print confirmation: `Rolled back full_database to snapshot 2026-03-29T09-12-33 (87 documents restored).`

Delete + recreate (step 2–3) is preferred over diffing to guarantee the collection exactly matches the snapshot with no leftover stale chunks.

If no snapshots exist for the collection, the script exits with a clear error message.

---

## Snapshot Retention

- Maximum 5 snapshots per collection.
- After every new snapshot is written, the oldest file(s) beyond the cap are deleted automatically.
- Retention is enforced in `create_snapshot()` so both manual and auto-snapshots obey the same limit.

---

## Components

| Component | Responsibility |
|---|---|
| `snapshot_db.py` | `create_snapshot()`, `list_snapshots()`, `rollback()`, `prune_snapshots()`, CLI entry point |
| `update_db.py` | Calls `create_snapshot(collection)` before the update loop |
| `Database/snapshots/` | Snapshot storage directory (one subdirectory per collection) |

---

## Error Handling

- Snapshot directory missing → created automatically on first use.
- Collection is empty → snapshot is still written (with `document_count: 0`).
- No snapshots found on rollback → exit with non-zero status and clear message.
- Invalid `--snapshot` ID → exit with clear message listing available snapshots.
- Partial rollback failure (e.g. add fails mid-batch) → collection may be in incomplete state; the snapshot file is untouched so the operator can retry.
