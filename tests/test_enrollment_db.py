"""
Unit tests for Database/enrollment_database.py

Uses an in-memory ChromaDB client (EphemeralClient) with a trivial mock
embedding function so that no real API credentials are needed.

get_chroma_client and get_embedding_function are patched at the module level
via patch.object so that every function in enrollment_database.py gets the
same ephemeral client and mock embedding function for the duration of each
test.
"""
import json
import os
import sys
from unittest.mock import patch

import pytest
import chromadb

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Database"))

os.environ.setdefault("GEMINI_API_KEY", "test-key")
os.environ.setdefault("CHROMA_DB_PATH", "/tmp/test-chroma")
os.environ.setdefault("OPENROUTER_API_KEY", "test-key")

import enrollment_database as edb


class _MockEmbeddingFunction:
    """Returns fixed-size vectors so no Gemini API calls are made."""

    def __call__(self, input):
        return [[0.1] * 10 for _ in input]

    def name(self) -> str:
        # ChromaDB validates this against the persisted config on subsequent
        # `get_or_create_collection` calls; "default" bypasses the conflict check.
        return "default"

    def is_legacy(self) -> bool:
        return False


@pytest.fixture
def db(tmp_path):
    """
    Yield the enrollment_database module with get_chroma_client and
    get_embedding_function replaced by isolated equivalents.

    PersistentClient with a per-test tmp_path guarantees full isolation —
    chromadb.EphemeralClient shares in-process state across instances and
    would leak data between tests.
    """
    client = chromadb.PersistentClient(path=str(tmp_path))
    mock_ef = _MockEmbeddingFunction()

    with patch.object(edb, "get_chroma_client", return_value=client), \
         patch.object(edb, "get_embedding_function", return_value=mock_ef):
        yield edb


# ---------------------------------------------------------------------------
# log_enrollment_conversation
# ---------------------------------------------------------------------------

class TestLogEnrollmentConversation:
    def test_returns_uuid_string(self, db):
        iid = db.log_enrollment_conversation("I want to enroll.", "Happy to help!")
        assert isinstance(iid, str)
        assert len(iid) == 36  # standard UUID length

    def test_document_contains_user_and_agent_text(self, db):
        db.log_enrollment_conversation("My question", "My answer")
        coll = db.get_enrollment_conversations_db()
        doc = coll.get()["documents"][0]
        assert "User: My question" in doc
        assert "Agent: My answer" in doc

    def test_metadata_role_is_enrollment_interaction(self, db):
        db.log_enrollment_conversation("q", "a")
        meta = db.get_enrollment_conversations_db().get()["metadatas"][0]
        assert meta["role"] == "enrollment_interaction"

    def test_metadata_includes_timestamp(self, db):
        db.log_enrollment_conversation("q", "a")
        meta = db.get_enrollment_conversations_db().get()["metadatas"][0]
        assert "timestamp" in meta

    def test_session_id_stored_in_metadata(self, db):
        db.log_enrollment_conversation("q", "a", session_id="sess-abc")
        meta = db.get_enrollment_conversations_db().get()["metadatas"][0]
        assert meta["session_id"] == "sess-abc"

    def test_default_session_id_when_omitted(self, db):
        db.log_enrollment_conversation("q", "a")
        meta = db.get_enrollment_conversations_db().get()["metadatas"][0]
        assert meta["session_id"] == "no_session"

    def test_extra_metadata_is_merged(self, db):
        db.log_enrollment_conversation("q", "a", metadata={"custom": "value"})
        meta = db.get_enrollment_conversations_db().get()["metadatas"][0]
        assert meta["custom"] == "value"


# ---------------------------------------------------------------------------
# create_enrollment_session
# ---------------------------------------------------------------------------

class TestCreateEnrollmentSession:
    def test_returns_uuid_string(self, db):
        sid = db.create_enrollment_session()
        assert isinstance(sid, str)
        assert len(sid) == 36

    def test_new_session_has_active_status(self, db):
        sid = db.create_enrollment_session()
        meta = db.get_enrollment_sessions_db().get(ids=[sid])["metadatas"][0]
        assert meta["status"] == "active"

    def test_new_session_has_initial_step(self, db):
        sid = db.create_enrollment_session()
        meta = db.get_enrollment_sessions_db().get(ids=[sid])["metadatas"][0]
        assert meta["step"] == "initial"

    def test_user_identifier_stored(self, db):
        sid = db.create_enrollment_session(user_identifier="parent@example.com")
        meta = db.get_enrollment_sessions_db().get(ids=[sid])["metadatas"][0]
        assert meta["user_identifier"] == "parent@example.com"

    def test_anonymous_used_when_no_identifier(self, db):
        sid = db.create_enrollment_session()
        meta = db.get_enrollment_sessions_db().get(ids=[sid])["metadatas"][0]
        assert meta["user_identifier"] == "anonymous"


# ---------------------------------------------------------------------------
# update_enrollment_session
# ---------------------------------------------------------------------------

class TestUpdateEnrollmentSession:
    def test_update_step(self, db):
        sid = db.create_enrollment_session()
        result = db.update_enrollment_session(sid, step="grade_selection")
        assert result is True
        meta = db.get_enrollment_sessions_db().get(ids=[sid])["metadatas"][0]
        assert meta["step"] == "grade_selection"

    def test_update_status(self, db):
        sid = db.create_enrollment_session()
        db.update_enrollment_session(sid, status="completed")
        meta = db.get_enrollment_sessions_db().get(ids=[sid])["metadatas"][0]
        assert meta["status"] == "completed"

    def test_update_collected_data_stored_as_json(self, db):
        sid = db.create_enrollment_session()
        db.update_enrollment_session(sid, collected_data={"name": "John", "grade": "9"})
        meta = db.get_enrollment_sessions_db().get(ids=[sid])["metadatas"][0]
        stored = json.loads(meta["collected_data"])
        assert stored["name"] == "John"
        assert stored["grade"] == "9"

    def test_nonexistent_session_returns_false(self, db):
        result = db.update_enrollment_session("no-such-id", step="test")
        assert result is False

    def test_updated_at_field_is_present_after_update(self, db):
        sid = db.create_enrollment_session()
        db.update_enrollment_session(sid, step="new_step")
        meta = db.get_session_info(sid)["metadata"]
        assert "updated_at" in meta


# ---------------------------------------------------------------------------
# get_session_info
# ---------------------------------------------------------------------------

class TestGetSessionInfo:
    def test_returns_dict_with_correct_id(self, db):
        sid = db.create_enrollment_session()
        info = db.get_session_info(sid)
        assert info is not None
        assert info["id"] == sid

    def test_returned_dict_has_metadata_and_document_keys(self, db):
        sid = db.create_enrollment_session()
        info = db.get_session_info(sid)
        assert "metadata" in info
        assert "document" in info

    def test_returns_none_for_unknown_session(self, db):
        assert db.get_session_info("nonexistent-id") is None


# ---------------------------------------------------------------------------
# get_active_sessions
# ---------------------------------------------------------------------------

class TestGetActiveSessions:
    def test_new_session_appears_in_active_list(self, db):
        sid = db.create_enrollment_session()
        ids = [s["id"] for s in db.get_active_sessions()]
        assert sid in ids

    def test_completed_session_not_in_active_list(self, db):
        sid = db.create_enrollment_session()
        db.complete_enrollment_session(sid)
        ids = [s["id"] for s in db.get_active_sessions()]
        assert sid not in ids

    def test_abandoned_session_not_in_active_list(self, db):
        sid = db.create_enrollment_session()
        db.abandon_enrollment_session(sid)
        ids = [s["id"] for s in db.get_active_sessions()]
        assert sid not in ids


# ---------------------------------------------------------------------------
# abandon_enrollment_session
# ---------------------------------------------------------------------------

class TestAbandonEnrollmentSession:
    def test_sets_status_to_abandoned(self, db):
        sid = db.create_enrollment_session()
        result = db.abandon_enrollment_session(sid)
        assert result is True
        meta = db.get_enrollment_sessions_db().get(ids=[sid])["metadatas"][0]
        assert meta["status"] == "abandoned"

    def test_reason_stored_in_metadata(self, db):
        sid = db.create_enrollment_session()
        db.abandon_enrollment_session(sid, reason="User left the chat")
        meta = db.get_enrollment_sessions_db().get(ids=[sid])["metadatas"][0]
        assert meta["abandonment_reason"] == "User left the chat"

    def test_nonexistent_session_returns_false(self, db):
        assert db.abandon_enrollment_session("nonexistent-id") is False


# ---------------------------------------------------------------------------
# complete_enrollment_session
# ---------------------------------------------------------------------------

class TestCompleteEnrollmentSession:
    def test_sets_status_to_completed(self, db):
        sid = db.create_enrollment_session()
        result = db.complete_enrollment_session(sid)
        assert result is True
        meta = db.get_enrollment_sessions_db().get(ids=[sid])["metadatas"][0]
        assert meta["status"] == "completed"

    def test_sets_step_to_completed(self, db):
        sid = db.create_enrollment_session()
        db.complete_enrollment_session(sid)
        meta = db.get_enrollment_sessions_db().get(ids=[sid])["metadatas"][0]
        assert meta["step"] == "completed"

    def test_final_data_stored_as_json(self, db):
        sid = db.create_enrollment_session()
        db.complete_enrollment_session(sid, final_data={"student": "John"})
        meta = db.get_enrollment_sessions_db().get(ids=[sid])["metadatas"][0]
        stored = json.loads(meta["collected_data"])
        assert stored["student"] == "John"


# ---------------------------------------------------------------------------
# get_enrollment_stats
# ---------------------------------------------------------------------------

class TestGetEnrollmentStats:
    def test_initial_counts_all_zero(self, db):
        stats = db.get_enrollment_stats()
        assert stats["total_conversations"] == 0
        assert stats["total_sessions"] == 0
        assert stats["active_sessions"] == 0
        assert stats["completed_sessions"] == 0
        assert stats["abandoned_sessions"] == 0

    def test_counts_active_sessions(self, db):
        db.create_enrollment_session()
        db.create_enrollment_session()
        assert db.get_enrollment_stats()["active_sessions"] == 2

    def test_counts_completed_sessions(self, db):
        sid = db.create_enrollment_session()
        db.complete_enrollment_session(sid)
        stats = db.get_enrollment_stats()
        assert stats["completed_sessions"] == 1
        assert stats["active_sessions"] == 0

    def test_counts_abandoned_sessions(self, db):
        sid = db.create_enrollment_session()
        db.abandon_enrollment_session(sid)
        assert db.get_enrollment_stats()["abandoned_sessions"] == 1

    def test_counts_conversations(self, db):
        db.log_enrollment_conversation("q1", "a1")
        db.log_enrollment_conversation("q2", "a2")
        assert db.get_enrollment_stats()["total_conversations"] == 2


# ---------------------------------------------------------------------------
# get_session_conversations
# ---------------------------------------------------------------------------

class TestGetSessionConversations:
    def test_returns_conversations_for_session(self, db):
        sid = db.create_enrollment_session()
        db.log_enrollment_conversation("Hello", "Hi", session_id=sid)
        db.log_enrollment_conversation("Question", "Answer", session_id=sid)
        assert len(db.get_session_conversations(sid)) == 2

    def test_does_not_include_other_sessions_conversations(self, db):
        sid_a = db.create_enrollment_session()
        sid_b = db.create_enrollment_session()
        db.log_enrollment_conversation("Q for A", "Ans A", session_id=sid_a)
        db.log_enrollment_conversation("Q for B", "Ans B", session_id=sid_b)
        convos = db.get_session_conversations(sid_a)
        assert len(convos) == 1
        assert "Q for A" in convos[0]["content"]

    def test_returns_empty_list_for_session_with_no_conversations(self, db):
        sid = db.create_enrollment_session()
        assert db.get_session_conversations(sid) == []

    def test_conversations_sorted_by_timestamp(self, db):
        sid = db.create_enrollment_session()
        db.log_enrollment_conversation("First message", "Answer", session_id=sid)
        db.log_enrollment_conversation("Second message", "Answer", session_id=sid)
        convos = db.get_session_conversations(sid)
        assert "First message" in convos[0]["content"]
        assert "Second message" in convos[1]["content"]
