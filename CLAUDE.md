# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt   # adds pytest

# Run the Flask chat server (port 5000 by default)
cd agent_chatbot && python server.py

# Run the analysis agent (reads DB logs, writes a markdown report, emails it)
cd agent_analysis && python analysis_agent.py

# Rebuild the ChromaDB vector database from scratch
python Database/database.py

# Refresh specific URLs in the DB (or all if none given)
python Database/update_db.py [URL ...]
python Database/update_db.py --dry-run
python Database/update_db.py --collection full_database URL

# Run all tests
pytest tests/

# Run a single test file or test
pytest tests/test_chatbot.py
pytest tests/test_server.py::TestChatEndpoint::test_missing_message_returns_400
```

## Environment Variables (`.env` in repo root)

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY` | Gemini embeddings (`gemini-embedding-001`) and LLM extraction during crawling |
| `OPENROUTER_API_KEY` | Qwen model (`qwen/qwen3.5-397b-a17b`) for chat responses and analysis |
| `CHROMA_DB_PATH` | Absolute path to the ChromaDB persistent storage directory |
| `SENDER_EMAIL` / `SENDER_PASSWORD` / `RECIPIENT_EMAIL` | Email credentials for automated report delivery |
| `SMTP_SERVER` / `SMTP_PORT` | SMTP config (defaults: `smtp.gmail.com`, `587`) |

## Architecture

### Request flow

```
Browser iframe  →  enrollment_chatbot.js  →  Flask /chat or /enrollment-chat
                                          →  get_relevant_documents (ChromaDB)
                                          →  make_prompt (constructs system prompt)
                                          →  Qwen via OpenRouter (generates answer)
                                          →  logs to full_database_conversations
```

### Key architectural facts

**Both chatbot iframes share one JS file.** `chatbot_iframe.html` and `enrollment_chatbot_iframe.html` are nearly identical HTML shells; both load `enrollment_chatbot.js`. The only server-side distinction is the endpoint (`/chat` vs `/enrollment-chat`) and the greeting response text.

**ChromaDB collections in use by the server** (`agent_chatbot/server.py`):
- `full_database` — the main knowledge base queried on every non-greeting request
- `conversations` — logs `/chat` interactions
- `full_database_conversations` — logs `/enrollment-chat` interactions; also the source for the analysis agent

**Chunk metadata convention:**
- Handbook pages: `{"source": url}` — crawled with LLM extraction (Gemini Flash)
- Enrollment pages: `{"source": url, "type": "enrollment"}` — crawled with `fit_markdown` (no LLM cost)

`update_db.py` uses the presence/absence of `"type": "enrollment"` in metadata to decide which crawler to invoke when refreshing a URL.

**`make_prompt` in `agent_chatbot/chatbot.py`** is the single function that builds the entire system prompt. It accepts `query`, `relevant_passage`, `history=[]`, and `language="English"`. The language instruction is injected just before the `ANSWER:` label so the model always responds in the user-selected language regardless of what language the user typed in.

**Language selector** is in both iframe headers. The selected value is sent as `"language"` in every API request JSON body and passed through `server.py → make_prompt`. Welcome screen text translates immediately on change via `updateWelcomeText()` in `enrollment_chatbot.js`, which holds translations for all 7 supported languages.

**Rate limiting + spam detection** in `server.py` runs before any LLM call:
1. Flask-Limiter (20 req/min) keyed on a SHA-256 client fingerprint (IP + User-Agent + Accept headers)
2. Custom `spam_tracker` catches gibberish (<50% alphanumeric), duplicate messages (same message ≥3× in 5 min), and rapid-fire (≥10 messages in 60 s)

### Analysis agent (`agent_analysis/`)

`analysis_agent.py` fetches all documents from `full_database_conversations`, parses `"User: ...\nAI: ..."` log format, sends the batch to Qwen for trend analysis, and writes a dated markdown report to `agent_analysis/analysis_reports/`. `email_report.py` then emails the report as an attachment.

### Database build scripts (`Database/`)

- `database.py` — defines the two crawlers (`crawlinfo` for handbook pages using Gemini LLM extraction, `crawl_enrollment` for enrollment pages using `fit_markdown`) and `get_chroma_db`. Import from here rather than duplicating.
- `update_db.py` — imports from `database.py`; used for incremental refreshes of existing URLs without a full rebuild.
- Other scripts (`clear.py`, `check_metadata.py`, etc.) are one-off maintenance utilities.

## Testing

Tests live in `tests/` and use pytest with `unittest.mock`. The pattern for each test module:

1. Set dummy env vars (`OPENROUTER_API_KEY`, `GEMINI_API_KEY`, `CHROMA_DB_PATH`) before importing the module under test.
2. Patch `chatbot.get_chroma_db` (or stub `sys.modules["database"]`) so module-level DB initialisation doesn't hit real ChromaDB.
3. Test pure functions directly; mock LLM calls with `MagicMock` / `AsyncMock`.

`test_update_db.py` uses `sys.modules` pre-import stubbing for `database`, `crawl4ai`, `langchain_text_splitters`, and `dotenv` because those are heavy imports with side effects.
