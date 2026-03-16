"""
Unit tests for analysis_agent.py

parse_conversations is pure string logic with no external dependencies, so it
is tested directly. analyze_with_openrouter is tested for its empty-input
short-circuit only; real LLM calls are not made.
"""
import os
import sys

os.environ.setdefault("OPENROUTER_API_KEY", "test-key")
os.environ.setdefault("GEMINI_API_KEY", "test-key")
os.environ.setdefault("CHROMA_DB_PATH", "/tmp/test-chroma")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "agent_analysis"))

import pytest
import analysis_agent
from analysis_agent import parse_conversations


# ---------------------------------------------------------------------------
# parse_conversations
# ---------------------------------------------------------------------------

class TestParseConversations:
    def test_parses_standard_format(self):
        docs = ["User: What are the fees?\nAI: Tuition is $20,000 per year."]
        result = parse_conversations(docs)
        assert len(result) == 1
        assert result[0]["query"] == "What are the fees?"
        assert result[0]["response"] == "Tuition is $20,000 per year."

    def test_parses_multiple_documents(self):
        docs = [
            "User: Question one?\nAI: Answer one.",
            "User: Question two?\nAI: Answer two.",
        ]
        result = parse_conversations(docs)
        assert len(result) == 2
        assert result[0]["query"] == "Question one?"
        assert result[1]["query"] == "Question two?"

    def test_skips_documents_without_ai_separator(self):
        docs = [
            "This has no AI separator at all",
            "User: Valid question?\nAI: Valid answer.",
        ]
        result = parse_conversations(docs)
        assert len(result) == 1
        assert result[0]["query"] == "Valid question?"

    def test_empty_list_returns_empty_list(self):
        assert parse_conversations([]) == []

    def test_all_malformed_documents_returns_empty_list(self):
        docs = ["no separator", "also no separator here"]
        assert parse_conversations(docs) == []

    def test_strips_whitespace_from_query_and_response(self):
        docs = ["User:   padded query   \nAI:   padded response   "]
        result = parse_conversations(docs)
        assert result[0]["query"] == "padded query"
        assert result[0]["response"] == "padded response"

    def test_multiline_ai_response_is_preserved(self):
        # Only the first "\nAI: " is used as the split point, so newlines
        # within the AI response are kept intact.
        docs = ["User: Tell me about admissions.\nAI: Step 1.\nStep 2.\nStep 3."]
        result = parse_conversations(docs)
        assert "Step 1." in result[0]["response"]
        assert "Step 2." in result[0]["response"]

    def test_each_entry_has_query_and_response_keys(self):
        docs = ["User: question?\nAI: answer."]
        result = parse_conversations(docs)
        assert "query" in result[0]
        assert "response" in result[0]

    def test_user_prefix_stripped_from_query(self):
        docs = ["User: My question\nAI: My answer"]
        result = parse_conversations(docs)
        assert not result[0]["query"].startswith("User:")

    def test_document_with_only_whitespace_after_split_is_handled(self):
        # The AI part is empty — should still parse without crashing
        docs = ["User: question\nAI: "]
        result = parse_conversations(docs)
        assert len(result) == 1
        assert result[0]["response"] == ""


# ---------------------------------------------------------------------------
# analyze_with_openrouter — empty-input guard
# ---------------------------------------------------------------------------

class TestAnalyzeWithOpenRouter:
    def test_empty_conversations_returns_no_conversations_message(self):
        result = analysis_agent.analyze_with_openrouter([])
        assert result == "No conversations found to analyze."
