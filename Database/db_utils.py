"""
db_utils.py — Shared ChromaDB helpers and LLM extraction config.

Imported by: update_db.py, snapshot_db.py, query_chunks.py, create_db.py
"""

import os
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class ExtractedContent(BaseModel):
    relevant_text: str = Field(
        description="The clean text block containing only the content that is special to that specific URL."
    )


EXTRACTION_INSTRUCTION = """
You are a content extraction assistant for a school handbook website. Your job is to extract useful, substantive content from web pages while removing navigation clutter.

## Context
You're processing pages from a school's family handbook. Each page contains important information about policies, procedures, or general school information.

## What to KEEP (Extract)
- Page titles and main headings
- All descriptive paragraphs and explanatory text
- Policy descriptions and guidelines
- Important lists (rules, procedures, requirements)
- Contact information relevant to the page topic
- Any substantive content that helps answer questions about the school

## What to REMOVE (Filter Out)
- Repetitive navigation menus (e.g., "Home | About | Contact | Admissions")
- Footer content that appears on every page
- Social media links and share buttons
- Generic headers like "Quick Links" or "Main Menu"
- Login/Sign-in links
- Search boxes
- Copyright notices and legal disclaimers
- Breadcrumb navigation

## Critical Rules
1. **Err on the side of inclusion**: If you're unsure whether content is important, KEEP IT. Missing important information is worse than including a bit of extra content.

2. **Minimum content threshold**: Your extracted text should be at least 100 characters long. If you find less than that, you're likely being too aggressive with filtering.

3. **Check the URL**: The URL path often indicates the topic (e.g., "/dress-code" means extract dress code information). Make sure you're capturing content related to that topic.

4. **Don't return empty results**: If you can't find specific content matching the URL, extract ALL substantive text from the page instead of returning nothing.

## Output Format
Return ONLY the cleaned, relevant text. Do not add any commentary, metadata, or explanations. Just return the useful content from the page.
"""


def get_chroma_db(name):
    google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
        api_key=os.environ.get("GEMINI_API_KEY"),
        model_name="gemini-embedding-001",
    )
    # Use environment variable or default to ./chroma_db in Database directory
    chroma_path = os.environ.get("CHROMA_DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db"))
    print(f"[ChromaDB] Using database path: {chroma_path}")
    chroma_client = chromadb.PersistentClient(path=chroma_path)
    collection = chroma_client.get_or_create_collection(name=name, embedding_function=google_ef)
    return collection
