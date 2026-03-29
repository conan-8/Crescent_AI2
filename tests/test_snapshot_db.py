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
