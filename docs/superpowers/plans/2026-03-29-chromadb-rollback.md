# ChromaDB Collection Rollback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add snapshot and rollback support for individual ChromaDB collections so a bad crawl can be instantly reversed without re-crawling or re-embedding.

**Architecture:** A new `Database/snapshot_db.py` module exports each collection to a timestamped JSON file (ids + documents + metadatas + embeddings). `update_db.py` auto-snapshots before any update run. Rollback deletes and recreates the collection from the snapshot file — no Gemini API call needed.

**Tech Stack:** Python stdlib (`os`, `json`, `argparse`, `datetime`), `chromadb` PersistentClient, pytest with `unittest.mock` and `tmp_path`.

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `Database/snapshot_db.py` | All snapshot/list/prune/rollback logic + CLI |
| Create | `tests/test_snapshot_db.py` | Unit tests for snapshot_db |
| Modify | `Database/update_db.py` | Import snapshot_db; call `create_snapshot` before update loop |
| Modify | `tests/test_update_db.py` | Stub snapshot_db; add auto-snapshot integration test |

---

## Task 1: `prune_snapshots` and `list_snapshots`

These are pure filesystem functions — no ChromaDB needed. Write and test them first so later tasks can rely on them.

**Files:**
- Create: `Database/snapshot_db.py`
- Create: `tests/test_snapshot_db.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_snapshot_db.py`:

```python
"""
Unit tests for Database/snapshot_db.py

All filesystem operations use pytest's tmp_path fixture.
ChromaDB and database imports are stubbed before import.
"""

import os
import sys
import json
from unittest.mock import MagicMock, patch

import pytest

# ------------------------------------------------------------------
# Stub heavy external dependencies before importing snapshot_db.
# ------------------------------------------------------------------

os.environ.setdefault("GEMINI_API_KEY", "test-key")
os.environ.setdefault("CHROMA_DB_PATH", "/tmp/test-chroma")

for _mod in ("database", "chromadb", "dotenv"):
    sys.modules.setdefault(_mod, MagicMock())

sys.modules["database"].get_chroma_db = MagicMock()
sys.modules["chromadb"].PersistentClient = MagicMock()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Database"))
import snapshot_db  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_snap(directory, timestamp, doc_count=10):
    """Write a minimal valid snapshot file to directory."""
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, f"{timestamp}_snap.json")
    data = {
        "collection": "col",
        "created_at": timestamp,
        "document_count": doc_count,
        "ids": [f"id_{i}" for i in range(doc_count)],
        "documents": [f"doc_{i}" for i in range(doc_count)],
        "metadatas": [{"source": "https://x.com"}] * doc_count,
        "embeddings": [[0.1, 0.2]] * doc_count,
    }
    with open(path, "w") as f:
        json.dump(data, f)
    return path


# ---------------------------------------------------------------------------
# list_snapshots
# ---------------------------------------------------------------------------

class TestListSnapshots:
    def test_returns_empty_list_when_directory_missing(self, tmp_path):
        with patch.object(snapshot_db, "SNAPSHOTS_DIR", str(tmp_path)):
            result = snapshot_db.list_snapshots("no_such_collection")
        assert result == []

    def test_returns_empty_list_when_no_snapshot_files(self, tmp_path):
        col_dir = tmp_path / "my_col"
        col_dir.mkdir()
        with patch.object(snapshot_db, "SNAPSHOTS_DIR", str(tmp_path)):
            result = snapshot_db.list_snapshots("my_col")
        assert result == []

    def test_returns_one_snapshot(self, tmp_path):
        col_dir = tmp_path / "my_col"
        _write_snap(str(col_dir), "2026-03-29T14-05-00", doc_count=5)
        with patch.object(snapshot_db, "SNAPSHOTS_DIR", str(tmp_path)):
            result = snapshot_db.list_snapshots("my_col")
        assert len(result) == 1
        assert result[0]["timestamp"] == "2026-03-29T14-05-00"
        assert result[0]["document_count"] == 5

    def test_returns_snapshots_newest_first(self, tmp_path):
        col_dir = tmp_path / "my_col"
        _write_snap(str(col_dir), "2026-03-29T09-00-00")
        _write_snap(str(col_dir), "2026-03-29T14-05-00")
        with patch.object(snapshot_db, "SNAPSHOTS_DIR", str(tmp_path)):
            result = snapshot_db.list_snapshots("my_col")
        assert result[0]["timestamp"] == "2026-03-29T14-05-00"
        assert result[1]["timestamp"] == "2026-03-29T09-00-00"

    def test_each_entry_has_required_keys(self, tmp_path):
        col_dir = tmp_path / "my_col"
        _write_snap(str(col_dir), "2026-03-29T10-00-00")
        with patch.object(snapshot_db, "SNAPSHOTS_DIR", str(tmp_path)):
            result = snapshot_db.list_snapshots("my_col")
        snap = result[0]
        assert "timestamp" in snap
        assert "path" in snap
        assert "document_count" in snap


# ---------------------------------------------------------------------------
# prune_snapshots
# ---------------------------------------------------------------------------

class TestPruneSnapshots:
    def test_returns_zero_when_directory_missing(self, tmp_path):
        with patch.object(snapshot_db, "SNAPSHOTS_DIR", str(tmp_path)):
            count = snapshot_db.prune_snapshots("missing_col", max_keep=5)
        assert count == 0

    def test_returns_zero_when_under_limit(self, tmp_path):
        col_dir = tmp_path / "my_col"
        _write_snap(str(col_dir), "2026-03-29T10-00-00")
        _write_snap(str(col_dir), "2026-03-29T11-00-00")
        with patch.object(snapshot_db, "SNAPSHOTS_DIR", str(tmp_path)):
            count = snapshot_db.prune_snapshots("my_col", max_keep=5)
        assert count == 0

    def test_deletes_oldest_when_over_limit(self, tmp_path):
        col_dir = tmp_path / "my_col"
        timestamps = [
            "2026-03-29T09-00-00",
            "2026-03-29T10-00-00",
            "2026-03-29T11-00-00",
            "2026-03-29T12-00-00",
            "2026-03-29T13-00-00",
            "2026-03-29T14-00-00",  # 6 total, keep 5 → delete oldest
        ]
        for ts in timestamps:
            _write_snap(str(col_dir), ts)
        with patch.object(snapshot_db, "SNAPSHOTS_DIR", str(tmp_path)):
            count = snapshot_db.prune_snapshots("my_col", max_keep=5)
        assert count == 1
        remaining = sorted(os.listdir(str(col_dir)))
        assert "2026-03-29T09-00-00_snap.json" not in remaining

    def test_returns_count_of_deleted_files(self, tmp_path):
        col_dir = tmp_path / "my_col"
        for i in range(8):
            _write_snap(str(col_dir), f"2026-03-29T{i:02d}-00-00")
        with patch.object(snapshot_db, "SNAPSHOTS_DIR", str(tmp_path)):
            count = snapshot_db.prune_snapshots("my_col", max_keep=5)
        assert count == 3

    def test_keeps_newest_files(self, tmp_path):
        col_dir = tmp_path / "my_col"
        timestamps = [f"2026-03-29T{i:02d}-00-00" for i in range(7)]
        for ts in timestamps:
            _write_snap(str(col_dir), ts)
        with patch.object(snapshot_db, "SNAPSHOTS_DIR", str(tmp_path)):
            snapshot_db.prune_snapshots("my_col", max_keep=5)
        remaining = os.listdir(str(col_dir))
        assert "2026-03-29T06-00-00_snap.json" in remaining
        assert "2026-03-29T05-00-00_snap.json" in remaining
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_snapshot_db.py -v
```

Expected: `ModuleNotFoundError` or `ImportError` — `snapshot_db` does not exist yet.

- [ ] **Step 3: Create `Database/snapshot_db.py` with `list_snapshots` and `prune_snapshots`**

```python
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
import argparse
import chromadb
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SNAPSHOTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snapshots")
MAX_SNAPSHOTS = 5


def _collection_dir(collection_name: str) -> str:
    return os.path.join(SNAPSHOTS_DIR, collection_name)


def _snapshot_path(collection_name: str, timestamp: str) -> str:
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
    to_delete = files[:-max_keep] if len(files) > max_keep else []
    for fname in to_delete:
        os.remove(os.path.join(col_dir, fname))
    return len(to_delete)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_snapshot_db.py::TestListSnapshots tests/test_snapshot_db.py::TestPruneSnapshots -v
```

Expected: All 13 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add Database/snapshot_db.py tests/test_snapshot_db.py
git commit -m "feat: add snapshot_db with list_snapshots and prune_snapshots"
```

---

## Task 2: `create_snapshot`

**Files:**
- Modify: `Database/snapshot_db.py`
- Modify: `tests/test_snapshot_db.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_snapshot_db.py`:

```python
# ---------------------------------------------------------------------------
# create_snapshot
# ---------------------------------------------------------------------------

class TestCreateSnapshot:
    def _make_collection(self, ids, documents, metadatas, embeddings):
        col = MagicMock()
        col.get.return_value = {
            "ids": ids,
            "documents": documents,
            "metadatas": metadatas,
            "embeddings": embeddings,
        }
        return col

    def test_creates_collection_directory(self, tmp_path):
        col = self._make_collection(["id0"], ["doc0"], [{"source": "x"}], [[0.1]])
        with patch.object(snapshot_db, "SNAPSHOTS_DIR", str(tmp_path)):
            snapshot_db.create_snapshot(col, "new_col")
        assert os.path.isdir(str(tmp_path / "new_col"))

    def test_writes_json_file(self, tmp_path):
        col = self._make_collection(["id0"], ["doc0"], [{"source": "x"}], [[0.1]])
        with patch.object(snapshot_db, "SNAPSHOTS_DIR", str(tmp_path)):
            ts = snapshot_db.create_snapshot(col, "my_col")
        snap_file = tmp_path / "my_col" / f"{ts}_snap.json"
        assert snap_file.exists()

    def test_snapshot_contains_correct_fields(self, tmp_path):
        ids = ["id0", "id1"]
        docs = ["doc0", "doc1"]
        metas = [{"source": "https://a.com"}, {"source": "https://b.com"}]
        embeds = [[0.1, 0.2], [0.3, 0.4]]
        col = self._make_collection(ids, docs, metas, embeds)
        with patch.object(snapshot_db, "SNAPSHOTS_DIR", str(tmp_path)):
            ts = snapshot_db.create_snapshot(col, "my_col")
        with open(str(tmp_path / "my_col" / f"{ts}_snap.json")) as f:
            data = json.load(f)
        assert data["collection"] == "my_col"
        assert data["document_count"] == 2
        assert data["ids"] == ids
        assert data["documents"] == docs
        assert data["metadatas"] == metas
        assert data["embeddings"] == embeds

    def test_returns_timestamp_string(self, tmp_path):
        col = self._make_collection([], [], [], [])
        with patch.object(snapshot_db, "SNAPSHOTS_DIR", str(tmp_path)):
            ts = snapshot_db.create_snapshot(col, "my_col")
        assert isinstance(ts, str)
        assert len(ts) > 0

    def test_calls_collection_get_with_correct_includes(self, tmp_path):
        col = self._make_collection([], [], [], [])
        with patch.object(snapshot_db, "SNAPSHOTS_DIR", str(tmp_path)):
            snapshot_db.create_snapshot(col, "my_col")
        col.get.assert_called_once_with(
            include=["documents", "embeddings", "metadatas"]
        )

    def test_prunes_after_writing(self, tmp_path):
        col_dir = tmp_path / "my_col"
        for i in range(5):
            _write_snap(str(col_dir), f"2026-03-28T{i:02d}-00-00")
        col = self._make_collection(["id0"], ["doc0"], [{"source": "x"}], [[0.1]])
        with patch.object(snapshot_db, "SNAPSHOTS_DIR", str(tmp_path)):
            snapshot_db.create_snapshot(col, "my_col")
        # 5 existing + 1 new = 6; prune to 5 → 1 deleted
        remaining = [f for f in os.listdir(str(col_dir)) if f.endswith("_snap.json")]
        assert len(remaining) == 5

    def test_empty_collection_snapshot_has_zero_count(self, tmp_path):
        col = self._make_collection([], [], [], [])
        with patch.object(snapshot_db, "SNAPSHOTS_DIR", str(tmp_path)):
            ts = snapshot_db.create_snapshot(col, "my_col")
        with open(str(tmp_path / "my_col" / f"{ts}_snap.json")) as f:
            data = json.load(f)
        assert data["document_count"] == 0

    def test_numpy_like_embeddings_serialized_as_lists(self, tmp_path):
        """Embeddings from ChromaDB may be numpy arrays; they must be JSON-serializable."""
        class FakeArray:
            def __init__(self, vals):
                self._vals = vals
            def tolist(self):
                return self._vals

        col = self._make_collection(
            ["id0"], ["doc0"], [{"source": "x"}],
            [FakeArray([0.1, 0.2])]
        )
        with patch.object(snapshot_db, "SNAPSHOTS_DIR", str(tmp_path)):
            ts = snapshot_db.create_snapshot(col, "my_col")
        with open(str(tmp_path / "my_col" / f"{ts}_snap.json")) as f:
            data = json.load(f)
        assert data["embeddings"] == [[0.1, 0.2]]
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_snapshot_db.py::TestCreateSnapshot -v
```

Expected: `AttributeError: module 'snapshot_db' has no attribute 'create_snapshot'`

- [ ] **Step 3: Add `create_snapshot` to `Database/snapshot_db.py`**

Add this function after `prune_snapshots`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_snapshot_db.py::TestCreateSnapshot -v
```

Expected: All 8 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add Database/snapshot_db.py tests/test_snapshot_db.py
git commit -m "feat: add create_snapshot to snapshot_db"
```

---

## Task 3: `rollback`

**Files:**
- Modify: `Database/snapshot_db.py`
- Modify: `tests/test_snapshot_db.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_snapshot_db.py`:

```python
# ---------------------------------------------------------------------------
# rollback
# ---------------------------------------------------------------------------

class TestRollback:
    def test_exits_with_error_when_no_snapshots(self, tmp_path):
        with patch.object(snapshot_db, "SNAPSHOTS_DIR", str(tmp_path)):
            with pytest.raises(SystemExit) as exc:
                snapshot_db.rollback("empty_col")
        assert exc.value.code == 1

    def test_exits_with_error_when_snapshot_id_not_found(self, tmp_path):
        col_dir = tmp_path / "my_col"
        _write_snap(str(col_dir), "2026-03-29T10-00-00")
        with patch.object(snapshot_db, "SNAPSHOTS_DIR", str(tmp_path)):
            with pytest.raises(SystemExit) as exc:
                snapshot_db.rollback("my_col", snapshot_id="9999-01-01T00-00-00")
        assert exc.value.code == 1

    def test_deletes_existing_collection(self, tmp_path):
        col_dir = tmp_path / "my_col"
        _write_snap(str(col_dir), "2026-03-29T10-00-00", doc_count=2)
        mock_client = MagicMock()
        mock_new_col = MagicMock()
        with patch.object(snapshot_db, "SNAPSHOTS_DIR", str(tmp_path)), \
             patch.object(snapshot_db.chromadb, "PersistentClient", return_value=mock_client), \
             patch.object(snapshot_db, "get_chroma_db", return_value=mock_new_col):
            snapshot_db.rollback("my_col")
        mock_client.delete_collection.assert_called_once_with("my_col")

    def test_recreates_collection_via_get_chroma_db(self, tmp_path):
        col_dir = tmp_path / "my_col"
        _write_snap(str(col_dir), "2026-03-29T10-00-00", doc_count=2)
        mock_client = MagicMock()
        mock_new_col = MagicMock()
        with patch.object(snapshot_db, "SNAPSHOTS_DIR", str(tmp_path)), \
             patch.object(snapshot_db.chromadb, "PersistentClient", return_value=mock_client), \
             patch.object(snapshot_db, "get_chroma_db", return_value=mock_new_col) as mock_get:
            snapshot_db.rollback("my_col")
        mock_get.assert_called_once_with("my_col")

    def test_restores_documents_to_new_collection(self, tmp_path):
        col_dir = tmp_path / "my_col"
        _write_snap(str(col_dir), "2026-03-29T10-00-00", doc_count=2)
        mock_client = MagicMock()
        mock_new_col = MagicMock()
        with patch.object(snapshot_db, "SNAPSHOTS_DIR", str(tmp_path)), \
             patch.object(snapshot_db.chromadb, "PersistentClient", return_value=mock_client), \
             patch.object(snapshot_db, "get_chroma_db", return_value=mock_new_col):
            snapshot_db.rollback("my_col")
        mock_new_col.add.assert_called()
        call_kwargs = mock_new_col.add.call_args_list[0][1]
        assert "ids" in call_kwargs
        assert "documents" in call_kwargs
        assert "metadatas" in call_kwargs
        assert "embeddings" in call_kwargs

    def test_uses_most_recent_snapshot_by_default(self, tmp_path):
        col_dir = tmp_path / "my_col"
        _write_snap(str(col_dir), "2026-03-29T09-00-00", doc_count=10)
        _write_snap(str(col_dir), "2026-03-29T14-00-00", doc_count=20)
        mock_client = MagicMock()
        mock_new_col = MagicMock()
        with patch.object(snapshot_db, "SNAPSHOTS_DIR", str(tmp_path)), \
             patch.object(snapshot_db.chromadb, "PersistentClient", return_value=mock_client), \
             patch.object(snapshot_db, "get_chroma_db", return_value=mock_new_col):
            snapshot_db.rollback("my_col")
        # The most recent snapshot has doc_count=20, so add is called with 20 ids
        all_ids = []
        for call in mock_new_col.add.call_args_list:
            all_ids.extend(call[1]["ids"])
        assert len(all_ids) == 20

    def test_uses_specified_snapshot_id(self, tmp_path):
        col_dir = tmp_path / "my_col"
        _write_snap(str(col_dir), "2026-03-29T09-00-00", doc_count=10)
        _write_snap(str(col_dir), "2026-03-29T14-00-00", doc_count=20)
        mock_client = MagicMock()
        mock_new_col = MagicMock()
        with patch.object(snapshot_db, "SNAPSHOTS_DIR", str(tmp_path)), \
             patch.object(snapshot_db.chromadb, "PersistentClient", return_value=mock_client), \
             patch.object(snapshot_db, "get_chroma_db", return_value=mock_new_col):
            snapshot_db.rollback("my_col", snapshot_id="2026-03-29T09-00-00")
        all_ids = []
        for call in mock_new_col.add.call_args_list:
            all_ids.extend(call[1]["ids"])
        assert len(all_ids) == 10

    def test_add_called_in_batches_of_100(self, tmp_path):
        col_dir = tmp_path / "my_col"
        _write_snap(str(col_dir), "2026-03-29T10-00-00", doc_count=250)
        mock_client = MagicMock()
        mock_new_col = MagicMock()
        with patch.object(snapshot_db, "SNAPSHOTS_DIR", str(tmp_path)), \
             patch.object(snapshot_db.chromadb, "PersistentClient", return_value=mock_client), \
             patch.object(snapshot_db, "get_chroma_db", return_value=mock_new_col):
            snapshot_db.rollback("my_col")
        # 250 docs → 3 batches (100, 100, 50)
        assert mock_new_col.add.call_count == 3
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_snapshot_db.py::TestRollback -v
```

Expected: `AttributeError: module 'snapshot_db' has no attribute 'rollback'`

- [ ] **Step 3: Add `rollback` to `Database/snapshot_db.py`**

Add this import at the top of the file (after `from dotenv import load_dotenv`):

```python
from database import get_chroma_db
```

Add this function after `create_snapshot`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_snapshot_db.py::TestRollback -v
```

Expected: All 8 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add Database/snapshot_db.py tests/test_snapshot_db.py
git commit -m "feat: add rollback to snapshot_db"
```

---

## Task 4: CLI (`parse_args` + `main`)

**Files:**
- Modify: `Database/snapshot_db.py`
- Modify: `tests/test_snapshot_db.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_snapshot_db.py`:

```python
# ---------------------------------------------------------------------------
# parse_args
# ---------------------------------------------------------------------------

class TestParseArgs:
    def test_collection_is_required(self):
        with pytest.raises(SystemExit):
            snapshot_db.parse_args([])

    def test_collection_flag_sets_name(self):
        args = snapshot_db.parse_args(["--collection", "full_database"])
        assert args.collection == "full_database"

    def test_default_no_list_no_rollback(self):
        args = snapshot_db.parse_args(["--collection", "full_database"])
        assert args.list is False
        assert args.rollback is False

    def test_list_flag(self):
        args = snapshot_db.parse_args(["--collection", "full_database", "--list"])
        assert args.list is True

    def test_rollback_flag(self):
        args = snapshot_db.parse_args(["--collection", "full_database", "--rollback"])
        assert args.rollback is True

    def test_snapshot_flag(self):
        args = snapshot_db.parse_args([
            "--collection", "full_database",
            "--rollback",
            "--snapshot", "2026-03-29T10-00-00",
        ])
        assert args.snapshot == "2026-03-29T10-00-00"

    def test_snapshot_defaults_to_none(self):
        args = snapshot_db.parse_args(["--collection", "full_database", "--rollback"])
        assert args.snapshot is None

    def test_list_and_rollback_are_mutually_exclusive(self):
        with pytest.raises(SystemExit):
            snapshot_db.parse_args(["--collection", "full_database", "--list", "--rollback"])
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_snapshot_db.py::TestParseArgs -v
```

Expected: `AttributeError: module 'snapshot_db' has no attribute 'parse_args'`

- [ ] **Step 3: Add `parse_args` and `main` to `Database/snapshot_db.py`**

Add at the end of the file (after `rollback`):

```python
def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Snapshot and rollback ChromaDB collections."
    )
    parser.add_argument(
        "--collection", required=True, metavar="NAME", help="Collection name."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--list", action="store_true", help="List available snapshots.")
    group.add_argument("--rollback", action="store_true", help="Rollback to a snapshot.")
    parser.add_argument(
        "--snapshot",
        metavar="TIMESTAMP",
        default=None,
        help="Snapshot timestamp to rollback to (use with --rollback). Defaults to most recent.",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    if args.list:
        snaps = list_snapshots(args.collection)
        if not snaps:
            print(f"No snapshots found for collection '{args.collection}'.")
        for s in snaps:
            print(f"{s['timestamp']}  {s['document_count']} documents")
    elif args.rollback:
        rollback(args.collection, snapshot_id=args.snapshot)
    else:
        collection = get_chroma_db(args.collection)
        create_snapshot(collection, args.collection)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_snapshot_db.py::TestParseArgs -v
```

Expected: All 8 tests PASS.

- [ ] **Step 5: Run full test suite for snapshot_db**

```bash
pytest tests/test_snapshot_db.py -v
```

Expected: All tests PASS.

- [ ] **Step 6: Commit**

```bash
git add Database/snapshot_db.py tests/test_snapshot_db.py
git commit -m "feat: add CLI (parse_args + main) to snapshot_db"
```

---

## Task 5: Auto-snapshot integration in `update_db.py`

**Files:**
- Modify: `Database/update_db.py`
- Modify: `tests/test_update_db.py`

- [ ] **Step 1: Write failing test**

Open `tests/test_update_db.py`. Add `snapshot_db` to the stub block (immediately after the existing `sys.modules.setdefault` loop):

```python
# Stub snapshot_db so auto-snapshot calls don't touch the filesystem.
_mock_snapshot_db = MagicMock()
sys.modules["snapshot_db"] = _mock_snapshot_db
```

Then append this test class at the end of the file:

```python
# ---------------------------------------------------------------------------
# auto-snapshot integration
# ---------------------------------------------------------------------------

class TestAutoSnapshot:
    def test_create_snapshot_called_before_update(self):
        """update_db.run() must call snapshot_db.create_snapshot once, before any update."""
        col = _make_collection(
            all_metadatas=[{"source": "https://a.com", "type": "enrollment"}],
            chunk_ids=[],
        )
        args = update_db.parse_args(["https://a.com", "--collection", "full_database"])

        with patch.object(update_db, "get_chroma_db", return_value=col), \
             patch.object(update_db, "update_url", AsyncMock(return_value=(0, 0))), \
             patch.object(update_db.snapshot_db, "create_snapshot") as mock_snap:
            asyncio.run(update_db.run(args))

        mock_snap.assert_called_once_with(col, "full_database")

    def test_create_snapshot_not_called_on_dry_run(self):
        col = _make_collection(
            all_metadatas=[{"source": "https://a.com", "type": "enrollment"}],
            chunk_ids=[],
        )
        args = update_db.parse_args(["--dry-run", "--collection", "full_database"])

        with patch.object(update_db, "get_chroma_db", return_value=col), \
             patch.object(update_db, "update_url", AsyncMock(return_value=(0, 0))), \
             patch.object(update_db.snapshot_db, "create_snapshot") as mock_snap:
            asyncio.run(update_db.run(args))

        mock_snap.assert_not_called()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_update_db.py::TestAutoSnapshot -v
```

Expected: `AttributeError: module 'update_db' has no attribute 'snapshot_db'`

- [ ] **Step 3: Modify `Database/update_db.py`**

Add the import after the existing imports (after `from dotenv import load_dotenv`):

```python
import snapshot_db
```

In the `run` coroutine, add the auto-snapshot call right after `collection = get_chroma_db(args.collection)` and before the `if args.urls:` block:

```python
async def run(args):
    collection = get_chroma_db(args.collection)

    if not args.dry_run:
        snapshot_db.create_snapshot(collection, args.collection)

    if args.urls:
        ...  # rest of function unchanged
```

The full modified `run` function:

```python
async def run(args):
    collection = get_chroma_db(args.collection)

    if not args.dry_run:
        snapshot_db.create_snapshot(collection, args.collection)

    if args.urls:
        stored = get_all_urls_with_types(collection)
        url_types = {url: stored.get(url, "enrollment") for url in args.urls}
    else:
        url_types = get_all_urls_with_types(collection)
        if not url_types:
            print("No URLs found in the collection. Nothing to update.")
            return

    target_urls = list(url_types.keys())
    action = "preview" if args.dry_run else "update"
    print(f"\nURLs to {action}: {len(target_urls)}")
    for url in target_urls:
        print(f"  {url}  [{url_types[url]}]")
    print()

    total_removed = 0
    total_added = 0

    for url in target_urls:
        print(f"Processing: {url}")
        removed, added = await update_url(
            collection, url, url_types[url], dry_run=args.dry_run
        )
        total_removed += removed
        total_added += added

    print("\n" + "=" * 60)
    if args.dry_run:
        print("DRY-RUN SUMMARY  (no changes made)")
        print(f"  URLs that would be refreshed    : {len(target_urls)}")
        print(f"  Chunks that would be removed    : {total_removed}")
    else:
        print("UPDATE SUMMARY")
        print(f"  URLs updated    : {len(target_urls)}")
        print(f"  Chunks removed  : {total_removed}")
        print(f"  Chunks added    : {total_added}")
    print("=" * 60)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_update_db.py::TestAutoSnapshot -v
```

Expected: Both tests PASS.

- [ ] **Step 5: Run full test suite**

```bash
pytest tests/ -v
```

Expected: All tests PASS.

- [ ] **Step 6: Commit**

```bash
git add Database/update_db.py tests/test_update_db.py
git commit -m "feat: auto-snapshot in update_db before any update run"
```

---

## Final Verification

- [ ] **Smoke test the full suite one more time**

```bash
pytest tests/ -v
```

Expected: All tests PASS, no warnings about missing stubs.

- [ ] **Verify the CLI is accessible**

```bash
python Database/snapshot_db.py --help
```

Expected output includes `--collection`, `--list`, `--rollback`, `--snapshot`.
