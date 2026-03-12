"""
Unit tests for server.py

Tests spam detection helpers (is_gibberish, cleanup_old_messages, check_spam),
query contextualization, and Flask endpoint behaviour.

The module-level ChromaDB initialisation in server.py is intercepted by
patching chatbot.get_chroma_db before the module is imported.
"""
import os
import sys
import time
from unittest.mock import MagicMock, patch

# Set env vars before any import that transitively loads chatbot.py so that
# the module-level OpenAI client does not raise AuthenticationError.
os.environ.setdefault("OPENROUTER_API_KEY", "test-key")
os.environ.setdefault("GEMINI_API_KEY", "test-key")
os.environ.setdefault("CHROMA_DB_PATH", "/tmp/test-chroma")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

# Patch chatbot.get_chroma_db so the four module-level DB calls in server.py
# return a mock collection instead of hitting real ChromaDB/Gemini APIs.
_mock_collection = MagicMock()
_mock_collection.count.return_value = 0

with patch("chatbot.get_chroma_db", return_value=_mock_collection):
    import server

from server import is_gibberish, cleanup_old_messages, check_spam, spam_tracker


# ---------------------------------------------------------------------------
# Fixture: reset global spam state between tests
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clear_spam_tracker():
    spam_tracker.clear()
    yield
    spam_tracker.clear()


# ---------------------------------------------------------------------------
# is_gibberish
# ---------------------------------------------------------------------------

class TestIsGibberish:
    def test_normal_sentence_is_not_gibberish(self):
        assert is_gibberish("What are the school hours?") is False

    def test_message_10_chars_or_fewer_never_gibberish(self):
        assert is_gibberish("!!!!!!!!!!") is False  # exactly 10 symbols
        assert is_gibberish("a!!!!!!!") is False    # 9 chars

    def test_11_char_mostly_symbols_is_gibberish(self):
        # 1 alphanumeric out of 11 = ~9 % < 50 %
        assert is_gibberish("a!!!!!!!!!!") is True

    def test_exactly_50_percent_alphanumeric_not_gibberish(self):
        # 6 alpha + 6 symbols = 50 %, not *less than* 50 %
        assert is_gibberish("abcdef!!!!!!") is False

    def test_below_50_percent_alphanumeric_is_gibberish(self):
        # 5 alpha + 7 symbols = ~41.7 %
        assert is_gibberish("abcde!!!!!!!") is True

    def test_all_alphanumeric_not_gibberish(self):
        assert is_gibberish("HelloWorld12345") is False

    def test_empty_string_not_gibberish(self):
        assert is_gibberish("") is False

    def test_keyboard_mash_is_gibberish(self):
        assert is_gibberish("!@#$%^&*()_+-=[]{}") is True

    def test_sentence_with_spaces_not_gibberish(self):
        # Spaces are non-alphanumeric but "hello world" is still mostly letters
        assert is_gibberish("hello world") is False


# ---------------------------------------------------------------------------
# cleanup_old_messages
# ---------------------------------------------------------------------------

class TestCleanupOldMessages:
    def test_removes_messages_older_than_window(self):
        fp = "fp1"
        spam_tracker[fp].append((time.time() - 400, "old"))
        cleanup_old_messages(fp)
        assert len(spam_tracker[fp]) == 0

    def test_keeps_messages_within_window(self):
        fp = "fp2"
        spam_tracker[fp].append((time.time() - 100, "recent"))
        cleanup_old_messages(fp)
        assert len(spam_tracker[fp]) == 1

    def test_removes_old_keeps_recent_when_mixed(self):
        fp = "fp3"
        spam_tracker[fp].extend([
            (time.time() - 400, "old"),
            (time.time() - 100, "recent"),
        ])
        cleanup_old_messages(fp)
        assert len(spam_tracker[fp]) == 1
        assert spam_tracker[fp][0][1] == "recent"

    def test_custom_max_age_respected(self):
        fp = "fp4"
        spam_tracker[fp].append((time.time() - 90, "msg"))
        cleanup_old_messages(fp, max_age_seconds=60)
        assert len(spam_tracker[fp]) == 0


# ---------------------------------------------------------------------------
# check_spam
# ---------------------------------------------------------------------------

class TestCheckSpam:
    def test_legitimate_message_not_spam(self):
        is_spam, spam_type = check_spam("u1", "What are the school fees?")
        assert is_spam is False
        assert spam_type is None

    def test_gibberish_detected(self):
        is_spam, spam_type = check_spam("u1", "!@#$%^&*()_+-=[]{}!!!")
        assert is_spam is True
        assert spam_type == "gibberish"

    def test_duplicate_detected_on_third_identical_send(self):
        fp = "u_dup"
        msg = "Tell me about tuition"
        check_spam(fp, msg)
        check_spam(fp, msg)
        is_spam, spam_type = check_spam(fp, msg)
        assert is_spam is True
        assert spam_type == "duplicate"

    def test_first_two_identical_messages_not_duplicate(self):
        fp = "u_dup2"
        msg = "Hello school"
        check_spam(fp, msg)
        is_spam, _ = check_spam(fp, msg)
        assert is_spam is False

    def test_duplicate_check_is_case_insensitive(self):
        fp = "u_case"
        check_spam(fp, "Hello school")
        check_spam(fp, "hello school")
        is_spam, spam_type = check_spam(fp, "HELLO SCHOOL")
        assert is_spam is True
        assert spam_type == "duplicate"

    def test_rapid_fire_detected_after_ten_messages(self):
        fp = "u_rapid"
        for i in range(10):
            check_spam(fp, f"unique message {i}")
        is_spam, spam_type = check_spam(fp, "one more")
        assert is_spam is True
        assert spam_type == "too_fast"

    def test_nine_messages_not_rapid_fire(self):
        fp = "u_ok"
        for i in range(9):
            check_spam(fp, f"unique message {i}")
        is_spam, _ = check_spam(fp, "tenth unique message")
        assert is_spam is False

    def test_gibberish_takes_priority_over_duplicate(self):
        fp = "u_gib"
        gibberish = "!@#$%^&*()_+-=[]{}!!!"
        check_spam(fp, gibberish)
        is_spam, spam_type = check_spam(fp, gibberish)
        assert spam_type == "gibberish"

    def test_legitimate_message_is_recorded(self):
        fp = "u_rec"
        check_spam(fp, "Valid question about the school")
        assert len(spam_tracker[fp]) == 1

    def test_gibberish_message_is_not_recorded(self):
        fp = "u_norec"
        check_spam(fp, "!@#$%^&*()_+-=[]{}!!!")
        assert len(spam_tracker[fp]) == 0


# ---------------------------------------------------------------------------
# contextualize_query
# ---------------------------------------------------------------------------

class TestContextualizeQuery:
    def test_returns_original_query_when_no_history(self):
        result = server.contextualize_query([], "What are school hours?")
        assert result == "What are school hours?"

    def test_calls_llm_and_returns_rephrased_query(self, monkeypatch):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "  Rephrased standalone question  "
        monkeypatch.setattr(server.client.chat.completions, "create", lambda **kw: mock_response)
        history = [{"role": "user", "content": "Tell me about fees"}]
        result = server.contextualize_query(history, "What about deadlines?")
        assert result == "Rephrased standalone question"

    def test_returns_original_query_on_llm_exception(self, monkeypatch):
        def raise_error(**kw):
            raise Exception("API error")
        monkeypatch.setattr(server.client.chat.completions, "create", raise_error)
        history = [{"role": "user", "content": "Some context"}]
        result = server.contextualize_query(history, "Follow-up question?")
        assert result == "Follow-up question?"

    def test_only_last_six_history_messages_used(self, monkeypatch):
        captured = {}

        def fake_create(**kw):
            captured["prompt"] = kw["messages"][1]["content"]
            mock_resp = MagicMock()
            mock_resp.choices[0].message.content = "standalone"
            return mock_resp

        monkeypatch.setattr(server.client.chat.completions, "create", fake_create)
        history = [{"role": "user", "content": f"msg {i}"} for i in range(10)]
        server.contextualize_query(history, "latest question")
        assert "msg 0" not in captured["prompt"]
        assert "msg 9" in captured["prompt"]


# ---------------------------------------------------------------------------
# Flask endpoints
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    server.app.config["TESTING"] = True
    # Disable Flask-Limiter so rate-limit responses don't mask spam/logic tests.
    server.app.config["RATELIMIT_ENABLED"] = False
    server.db = _mock_collection
    server.enrollment_db = _mock_collection
    server.conversations_db = _mock_collection
    server.enrollment_conversations_db = _mock_collection
    with server.app.test_client() as c:
        yield c
    server.app.config["RATELIMIT_ENABLED"] = True


class TestChatEndpoint:
    def test_missing_message_returns_400(self, client):
        resp = client.post("/chat", json={})
        assert resp.status_code == 400

    def test_greeting_hello_returns_200_with_school_mention(self, client):
        resp = client.post("/chat", json={"message": "hello"})
        assert resp.status_code == 200
        assert "Crescent School" in resp.get_json()["response"]

    def test_greeting_hi_returns_200(self, client):
        resp = client.post("/chat", json={"message": "hi"})
        assert resp.status_code == 200

    def test_greeting_hey_returns_200(self, client):
        resp = client.post("/chat", json={"message": "hey"})
        assert resp.status_code == 200

    def test_no_db_returns_500(self, client):
        original = server.db
        server.db = None
        resp = client.post("/chat", json={"message": "hello"})
        server.db = original
        assert resp.status_code == 500

    def test_gibberish_message_returns_spam_response(self, client):
        # Use a unique User-Agent so this request gets its own rate-limit bucket,
        # isolated from the fingerprint accumulated by the earlier greeting tests.
        resp = client.post(
            "/chat",
            json={"message": "!@#$%^&*()_+-=[]{}!!!"},
            headers={"User-Agent": "GibberishDetectionTest/1.0"},
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert "valid question" in data["response"].lower()


class TestEnrollmentChatEndpoint:
    def test_missing_message_returns_400(self, client):
        resp = client.post("/enrollment-chat", json={})
        assert resp.status_code == 400

    def test_greeting_returns_enrollment_response(self, client):
        resp = client.post("/enrollment-chat", json={"message": "hello"})
        assert resp.status_code == 200
        assert "Enrollment" in resp.get_json()["response"]

    def test_no_db_returns_500(self, client):
        original = server.enrollment_db
        server.enrollment_db = None
        resp = client.post("/enrollment-chat", json={"message": "hello"})
        server.enrollment_db = original
        assert resp.status_code == 500



