"""
Unit tests for Database/update_db.py

Tests parse_args, collection helpers, dry-run mode, and the
delete-then-reindex logic.  No real network, database, or LLM
calls are made — all external dependencies are stubbed out.
"""

import os
import sys
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

import pytest

# ------------------------------------------------------------------
# Stub heavy external dependencies before importing update_db so
# that module-level initialisation (LLM clients, DB connections,
# text splitter) does not fail in a test environment.
# ------------------------------------------------------------------

os.environ.setdefault("GEMINI_API_KEY", "test-key")
os.environ.setdefault("CHROMA_DB_PATH", "/tmp/test-chroma")

for _mod in ("database", "crawl4ai", "crawl4ai.extraction_strategy", "dotenv"):
    sys.modules.setdefault(_mod, MagicMock())

# Provide a controlled text-splitter that returns predictable chunks.
_mock_splitter = MagicMock()
_mock_splitter.split_text.return_value = ["chunk_a", "chunk_b"]
_mock_langchain = MagicMock()
_mock_langchain.RecursiveCharacterTextSplitter.return_value = _mock_splitter
sys.modules["langchain_text_splitters"] = _mock_langchain

# Stub snapshot_db so auto-snapshot calls don't touch the filesystem.
_mock_snapshot_db = MagicMock()
sys.modules["snapshot_db"] = _mock_snapshot_db

# Populate the database stub with what update_db actually imports.
sys.modules["database"].get_chroma_db = MagicMock()
sys.modules["database"].ExtractedContent = MagicMock()
sys.modules["database"].EXTRACTION_INSTRUCTION = "test_instruction"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Database"))
import update_db  # noqa: E402  (must come after sys.modules setup)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run_async(coro):
    """Run a coroutine synchronously inside a test."""
    return asyncio.run(coro)


def _make_collection(*, all_metadatas=None, chunk_ids=None):
    """
    Return a mock ChromaDB collection whose .get() behaves correctly for
    both callers inside update_db:

      get_all_urls_with_types  → collection.get(include=[...])
      get_chunk_ids_for_url    → collection.get(where={...}, include=[...])
    """
    col = MagicMock()

    def _get(**kwargs):
        if "where" in kwargs:
            # Called by get_chunk_ids_for_url
            return {"ids": chunk_ids or [], "metadatas": []}
        # Called by get_all_urls_with_types
        return {"ids": [], "metadatas": all_metadatas or []}

    col.get.side_effect = _get
    return col


# ---------------------------------------------------------------------------
# parse_args
# ---------------------------------------------------------------------------

class TestParseArgs:
    def test_no_args_gives_empty_url_list(self):
        args = update_db.parse_args([])
        assert args.urls == []

    def test_single_url_parsed(self):
        args = update_db.parse_args(["https://example.com/page"])
        assert args.urls == ["https://example.com/page"]

    def test_multiple_urls_parsed(self):
        args = update_db.parse_args(["https://a.com", "https://b.com"])
        assert args.urls == ["https://a.com", "https://b.com"]

    def test_dry_run_defaults_to_false(self):
        args = update_db.parse_args([])
        assert args.dry_run is False

    def test_dry_run_flag_sets_true(self):
        args = update_db.parse_args(["--dry-run"])
        assert args.dry_run is True

    def test_default_collection_is_full_database(self):
        args = update_db.parse_args([])
        assert args.collection == "full_database"

    def test_collection_flag_overrides_default(self):
        args = update_db.parse_args(["--collection", "my_col"])
        assert args.collection == "my_col"

    def test_dry_run_combined_with_url(self):
        args = update_db.parse_args(["--dry-run", "https://example.com"])
        assert args.dry_run is True
        assert args.urls == ["https://example.com"]


# ---------------------------------------------------------------------------
# get_all_urls_with_types
# ---------------------------------------------------------------------------

class TestGetAllUrlsWithTypes:
    def test_extracts_urls_and_types(self):
        col = _make_collection(all_metadatas=[
            {"source": "https://a.com", "type": "enrollment"},
            {"source": "https://b.com"},
        ])
        result = update_db.get_all_urls_with_types(col)
        assert result == {"https://a.com": "enrollment", "https://b.com": "handbook"}

    def test_missing_type_defaults_to_handbook(self):
        col = _make_collection(all_metadatas=[{"source": "https://x.com"}])
        result = update_db.get_all_urls_with_types(col)
        assert result["https://x.com"] == "handbook"

    def test_duplicate_urls_deduplicated(self):
        col = _make_collection(all_metadatas=[
            {"source": "https://a.com", "type": "enrollment"},
            {"source": "https://a.com", "type": "enrollment"},
            {"source": "https://a.com", "type": "enrollment"},
        ])
        result = update_db.get_all_urls_with_types(col)
        assert len(result) == 1
        assert "https://a.com" in result

    def test_empty_collection_returns_empty_dict(self):
        col = _make_collection(all_metadatas=[])
        assert update_db.get_all_urls_with_types(col) == {}

    def test_none_metadata_entries_skipped(self):
        col = _make_collection(all_metadatas=[None, {"source": "https://a.com"}])
        result = update_db.get_all_urls_with_types(col)
        assert list(result.keys()) == ["https://a.com"]

    def test_multiple_urls_all_returned(self):
        col = _make_collection(all_metadatas=[
            {"source": "https://a.com", "type": "enrollment"},
            {"source": "https://b.com"},
            {"source": "https://c.com", "type": "enrollment"},
        ])
        result = update_db.get_all_urls_with_types(col)
        assert set(result.keys()) == {"https://a.com", "https://b.com", "https://c.com"}


# ---------------------------------------------------------------------------
# get_chunk_ids_for_url
# ---------------------------------------------------------------------------

class TestGetChunkIdsForUrl:
    def test_returns_ids_for_url(self):
        col = _make_collection(chunk_ids=["id1", "id2"])
        ids = update_db.get_chunk_ids_for_url(col, "https://a.com")
        assert ids == ["id1", "id2"]

    def test_passes_correct_where_filter_to_collection(self):
        col = _make_collection(chunk_ids=[])
        update_db.get_chunk_ids_for_url(col, "https://a.com")
        col.get.assert_called_once_with(
            where={"source": "https://a.com"}, include=["metadatas"]
        )

    def test_returns_empty_list_when_no_chunks_exist(self):
        col = _make_collection(chunk_ids=[])
        ids = update_db.get_chunk_ids_for_url(col, "https://a.com")
        assert ids == []


# ---------------------------------------------------------------------------
# delete_chunks_for_url
# ---------------------------------------------------------------------------

class TestDeleteChunksForUrl:
    def test_calls_delete_with_correct_ids(self):
        col = _make_collection(chunk_ids=["id1", "id2", "id3"])
        update_db.delete_chunks_for_url(col, "https://a.com")
        col.delete.assert_called_once_with(ids=["id1", "id2", "id3"])

    def test_returns_count_of_deleted_chunks(self):
        col = _make_collection(chunk_ids=["id1", "id2"])
        count = update_db.delete_chunks_for_url(col, "https://a.com")
        assert count == 2

    def test_no_chunks_skips_delete_call(self):
        col = _make_collection(chunk_ids=[])
        update_db.delete_chunks_for_url(col, "https://a.com")
        col.delete.assert_not_called()

    def test_no_chunks_returns_zero(self):
        col = _make_collection(chunk_ids=[])
        count = update_db.delete_chunks_for_url(col, "https://a.com")
        assert count == 0


# ---------------------------------------------------------------------------
# update_url — dry-run mode
# ---------------------------------------------------------------------------

class TestUpdateUrlDryRun:
    def test_does_not_call_delete(self):
        col = _make_collection(chunk_ids=["id1", "id2"])
        run_async(update_db.update_url(col, "https://a.com", "enrollment", dry_run=True))
        col.delete.assert_not_called()

    def test_does_not_call_add(self):
        col = _make_collection(chunk_ids=["id1"])
        run_async(update_db.update_url(col, "https://a.com", "enrollment", dry_run=True))
        col.add.assert_not_called()

    def test_returns_existing_count_as_removed(self):
        col = _make_collection(chunk_ids=["id1", "id2", "id3"])
        removed, _ = run_async(
            update_db.update_url(col, "https://a.com", "handbook", dry_run=True)
        )
        assert removed == 3

    def test_returns_zero_added(self):
        col = _make_collection(chunk_ids=["id1", "id2"])
        _, added = run_async(
            update_db.update_url(col, "https://a.com", "enrollment", dry_run=True)
        )
        assert added == 0

    def test_zero_existing_chunks_dry_run(self):
        col = _make_collection(chunk_ids=[])
        removed, added = run_async(
            update_db.update_url(col, "https://a.com", "handbook", dry_run=True)
        )
        assert removed == 0
        assert added == 0


# ---------------------------------------------------------------------------
# update_url — live mode (delete-then-reindex)
# ---------------------------------------------------------------------------

class TestUpdateUrlLive:
    def test_deletes_existing_chunks(self):
        col = _make_collection(chunk_ids=["old1", "old2"])
        with patch.object(update_db, "crawl_url_markdown", AsyncMock(return_value=([], [], []))):
            run_async(update_db.update_url(col, "https://a.com", "enrollment"))
        col.delete.assert_called_once_with(ids=["old1", "old2"])

    def test_uses_markdown_crawler_for_enrollment_type(self):
        col = _make_collection(chunk_ids=[])
        mock_crawl = AsyncMock(return_value=([], [], []))
        with patch.object(update_db, "crawl_url_markdown", mock_crawl):
            run_async(update_db.update_url(col, "https://a.com/enroll", "enrollment"))
        mock_crawl.assert_awaited_once_with("https://a.com/enroll")

    def test_uses_llm_crawler_for_handbook_type(self):
        col = _make_collection(chunk_ids=[])
        mock_crawl = AsyncMock(return_value=([], [], []))
        with patch.object(update_db, "crawl_url_llm", mock_crawl):
            run_async(update_db.update_url(col, "https://a.com/handbook", "handbook"))
        mock_crawl.assert_awaited_once_with("https://a.com/handbook")

    def test_adds_new_chunks_to_collection(self):
        col = _make_collection(chunk_ids=[])
        docs = ["chunk_a", "chunk_b"]
        ids = ["new_id_0", "new_id_1"]
        metas = [{"source": "https://a.com", "type": "enrollment"}] * 2
        with patch.object(update_db, "crawl_url_markdown", AsyncMock(return_value=(docs, ids, metas))):
            run_async(update_db.update_url(col, "https://a.com", "enrollment"))
        col.add.assert_called_once_with(ids=ids, documents=docs, metadatas=metas)

    def test_returns_correct_removed_and_added_counts(self):
        col = _make_collection(chunk_ids=["old1", "old2"])
        docs = ["c1", "c2", "c3"]
        ids = ["n1", "n2", "n3"]
        metas = [{}] * 3
        with patch.object(update_db, "crawl_url_markdown", AsyncMock(return_value=(docs, ids, metas))):
            removed, added = run_async(
                update_db.update_url(col, "https://a.com", "enrollment")
            )
        assert removed == 2
        assert added == 3

    def test_no_new_chunks_skips_add(self):
        col = _make_collection(chunk_ids=["id1"])
        with patch.object(update_db, "crawl_url_llm", AsyncMock(return_value=([], [], []))):
            run_async(update_db.update_url(col, "https://a.com", "handbook"))
        col.add.assert_not_called()

    def test_no_existing_chunks_skips_delete(self):
        col = _make_collection(chunk_ids=[])
        with patch.object(update_db, "crawl_url_llm", AsyncMock(return_value=([], [], []))):
            run_async(update_db.update_url(col, "https://a.com", "handbook"))
        col.delete.assert_not_called()

    def test_delete_happens_before_add(self):
        """Verify the delete-then-add ordering via call_args_list on the collection."""
        call_order = []
        col = _make_collection(chunk_ids=["old1"])
        col.delete.side_effect = lambda **kw: call_order.append("delete")
        col.add.side_effect = lambda **kw: call_order.append("add")

        docs = ["new_chunk"]
        with patch.object(
            update_db, "crawl_url_markdown",
            AsyncMock(return_value=(docs, ["new_id"], [{"source": "https://a.com"}]))
        ):
            run_async(update_db.update_url(col, "https://a.com", "enrollment"))

        assert call_order == ["delete", "add"]


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
