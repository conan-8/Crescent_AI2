# src/processing/text_processor.py

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from typing import List
from src import config

def chunk_text(text: str) -> List[str]:
    """Chunks the given text into smaller pieces."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def create_embeddings(chunks: List[str]) -> List[List[float]]:
    """
    Creates embeddings for a list of text chunks using Google's model.
    """
    embeddings = GoogleGenerativeAIEmbeddings(
        model=config.EMBEDDING_MODEL,
        google_api_key=config.GOOGLE_API_KEY
    )
    # The embed_documents method handles batching
    vector_embeddings = embeddings.embed_documents(chunks)
    return vector_embeddings