# Crescent AI

A comprehensive AI ecosystem for Crescent School, featuring multiple intelligent agents, an integration-ready frontend component, and a centralized vector database.

## Architecture & Project Structure

The project has been refactored into modular directories:

- **`/agent_chatbot`**: Contains Agent 1, the primary Chatbot Agent. 
  - `server.py`: Flask application that hosts the backend API for chat.
  - `chatbot.py`: Core logic for Agent 1. Handles prompt formatting and queries the ChromaDB full database.
- **`/agent_analysis`**: Contains Agent 2, the Analysis Agent.
  - `analysis_agent.py`: Parses logged conversations, queries an LLM to identify trends, unanswered questions, and generates insights.
  - `verify_logs.py`: Utility to verify if conversation logs have been saved properly in the database.
- **`/frontend`**: UI files and chat widget integrations.
  - `chatbot_iframe.html`: Embeddable iframe shell loading `chatbot.js` and `chatbot.css`.
  - `Main Page.html`: Demo page showing the widget on site.
- **`/Database`**: Scripts for scraping, embedding, and database management.
  - Contains scripts to crawl the Crescent website (`create_db.py`, `database.py`) and save embeddings into ChromaDB for both standard queries and enrollment-specific tasks.
- **`/tests`**: Comprehensive PyTest unit tests for agents and the database.
- **`/experiments`**: Miscellaneous testing files for crawling and gemini functionality.

## How to Run

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt # For running tests
   ```

2. **Environment Variables**:
   Create a `.env` file in the root structure containing APIs and paths:
   ```env
   GEMINI_API_KEY=your_gemini_key
   OPENROUTER_API_KEY=your_openrouter_key
   CHROMA_DB_PATH=C:\path\to\your\database
   ```

3. **Start the Database Build (If Needed)**:
   You may need to run `database.py` in the Database folder to crawl site info and build the local embeddings via ChromaDB.

4. **Run the Chatbot Server (Agent 1)**:
   ```bash
   cd agent_chatbot
   python server.py
   ```
   *The Flask API will run on `http://127.0.0.1:5000` by default. Include the widget iframe on your page to talk to it.*

5. **Run the Analytics Agent (Agent 2)**:
   ```bash
   cd agent_analysis
   python analysis_agent.py
   ```
   *This reads recent interactions and writes an intelligence report automatically.*

6. **Run Tests**:
   ```bash
   pytest tests/
   ```

## Integrations

- OpenRouter API (Accessing Qwen endpoints)
- Google Gemini Embeddings (`gemini-embedding-001`)
- Crawl4AI to scrape subdomains and web pages for data preprocessing/indexing.
