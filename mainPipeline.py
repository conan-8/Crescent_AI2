from crawl4ai import AsyncWebCrawler
import asyncio
from typing import List, Tuple
import time
from sentence_transformers import SentenceTransformer
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
import re
from supabase import create_client, Client
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Load environment variables
load_dotenv()

class SupabaseVectorDB:
    def __init__(self, url: str, key: str):
        self.supabase: Client = create_client(url, key)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for texts"""
        embeddings = self.model.encode(texts)
        return embeddings.tolist()
    
    def add_texts(self, texts: List[str], urls: List[str], metadatas: List[dict] = None):
        """Add texts to Supabase with embeddings"""
        if not texts:
            return None
            
        if metadatas is None:
            metadatas = [{}] * len(texts)
        
        embeddings = self.embed_texts(texts)
        
        # Prepare data for insertion
        records = []
        for text, url, embedding, metadata in zip(texts, urls, embeddings, metadatas):
            records.append({
                'content': text,
                'url': url,
                'embedding': embedding,
                'metadata': metadata
            })
        
        # Insert into Supabase
        try:
            data, count = self.supabase.table('documents').insert(records).execute()
            print(f"Successfully inserted {len(records)} records")
            return data
        except Exception as e:
            print(f"Error inserting records: {e}")
            return None
    
    def search(self, query: str, top_k: int = 5) -> List[dict]:
        """Search for similar documents using vector similarity"""
        query_embedding = self.model.encode([query]).tolist()[0]
        
        try:
            # Get all records from Supabase
            result = self.supabase.table('documents').select('content, url, metadata, embedding').execute()
            
            if not result.data:
                return []
            
            # Calculate similarity scores
            import numpy as np
            similarities = []
            for record in result.data:
                if record['embedding'] and isinstance(record['embedding'], list):
                    emb = np.array(record['embedding'])
                    query_emb = np.array(query_embedding)
                    
                    # Calculate cosine similarity
                    if np.linalg.norm(emb) > 0 and np.linalg.norm(query_emb) > 0:
                        similarity = np.dot(emb, query_emb) / (np.linalg.norm(emb) * np.linalg.norm(query_emb))
                        similarities.append((record, similarity))
            
            # Sort by similarity and return top_k
            similarities.sort(key=lambda x: x[1], reverse=True)
            top_results = similarities[:top_k]
            
            formatted_results = []
            for record, similarity in top_results:
                formatted_results.append({
                    "text": record['content'],
                    "url": record['url'],
                    "metadata": record['metadata'],
                    "similarity": similarity
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"Search error: {e}")
            return []

class Crawl4AIWrapper:
    def __init__(self, max_pages: int = 100):
        self.max_pages = max_pages
    
    def extract_links_from_html(self, html_content: str, current_url: str) -> List[str]:
        """Extract links from HTML content"""
        # If no content, return empty list
        if not html_content:
            return []
        
        try:
            # Use BeautifulSoup to parse the HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            base_domain = urlparse(current_url).netloc
            
            links = []
            for link in soup.find_all('a', href=True):
                absolute_url = urljoin(current_url, link['href'])
                parsed = urlparse(absolute_url)
                
                # Only include same-domain links that aren't files
                if (parsed.netloc == base_domain and 
                    not any(absolute_url.endswith(ext) for ext in ['.pdf', '.jpg', '.png', '.gif', '.doc', '.docx'])):
                    links.append(absolute_url)
            
            return links
        except Exception as e:
            print(f"Error extracting links from {current_url}: {e}")
            return []

    async def crawl_website(self, base_url: str) -> List[Tuple[str, str]]:
        """Crawl the entire website using Crawl4AI"""
        async with AsyncWebCrawler(verbose=True) as crawler:
            all_texts = []
            visited_urls = set()
            urls_to_visit = [base_url]
            
            pages_crawled = 0
            
            while urls_to_visit and pages_crawled < self.max_pages:
                current_url = urls_to_visit.pop(0)  # BFS approach
                
                if current_url in visited_urls:
                    continue
                
                try:
                    print(f"Crawling: {current_url}")
                    result = await crawler.arun(url=current_url)
                    
                    if result.success and result.markdown and result.markdown.strip():
                        all_texts.append((current_url, result.markdown))
                        visited_urls.add(current_url)
                        
                        # Extract links from the current page's HTML content
                        if result.extracted_content:
                            new_links = self.extract_links_from_html(result.extracted_content, current_url)
                            for link in new_links:
                                if link not in visited_urls and link not in urls_to_visit:
                                    urls_to_visit.append(link)
                        
                        pages_crawled += 1
                        print(f"  Found {len(new_links)} new links to crawl")
                        time.sleep(0.5)  # Be respectful to the server
                    else:
                        print(f"Skipped {current_url} - no content found")
                        
                except Exception as e:
                    print(f"Error crawling {current_url}: {e}")
            
            print(f"Total pages crawled: {len(all_texts)}")
            return all_texts

class ContextAwareChunker:
    def __init__(self, max_chunk_size: int = 512, overlap: int = 50):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str) -> List[str]:
        if not text or not text.strip():
            return []
            
        # Split by paragraphs first
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(paragraph) > self.max_chunk_size:
                # If paragraph is too long, split it
                sub_chunks = self.split_long_paragraph(paragraph)
                chunks.extend(sub_chunks)
            else:
                if len(current_chunk) + len(paragraph) <= self.max_chunk_size:
                    current_chunk += " " + paragraph
                else:
                    if current_chunk.strip():
                        chunks.append(current_chunk.strip())
                    current_chunk = paragraph
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def split_long_paragraph(self, text: str) -> List[str]:
        if not text or not text.strip():
            return []
            
        sentences = re.split(r'[.!?]+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_chunk) + len(sentence) <= self.max_chunk_size:
                current_chunk += " " + sentence
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks

class RAGPipeline:
    def __init__(self, vector_db: SupabaseVectorDB, gemini_api_key: str):
        self.vector_db = vector_db
        self.initialize_llm(gemini_api_key)
        self.define_prompt()
        self.build_rag_chain()
    
    def initialize_llm(self, gemini_api_key: str):
        """Initialize the Gemini LLM"""
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=gemini_api_key,
            temperature=0.1,
            max_output_tokens=1024,
            request_timeout=60
        )
    
    def define_prompt(self):
        """Define custom prompt template for Gemini"""
        template = """
        You are an AI assistant for a school. Use the following pieces of context to answer the question at the end.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        Keep the answer concise and helpful.
        
        Context:
        {context}
        
        Question: {question}
        
        Helpful Answer:"""
        
        self.prompt = PromptTemplate.from_template(template)
    
    def retrieve_and_format_context(self, question: str):
        """Retrieve relevant documents and format them as context"""
        retrieved_docs = self.vector_db.search(question, top_k=5)
        context = "\n\n".join([doc["text"] for doc in retrieved_docs if "text" in doc])
        return context if context.strip() else "No relevant information found in the database."
    
    def build_rag_chain(self):
        """Build the complete RAG chain"""
        def format_rag_input(question: str):
            context = self.retrieve_and_format_context(question)
            return {
                "context": context,
                "question": question
            }
        
        # Create the RAG chain
        self.rag_chain = (
            RunnablePassthrough()  # Pass the question directly
            | format_rag_input     # Format with context and question
            | self.prompt          # Apply the prompt template
            | self.llm             # Call the LLM
            | StrOutputParser()    # Parse the output
        )
    
    def query(self, question: str) -> str:
        """Query the RAG system"""
        return self.rag_chain.invoke(question)

async def main():
    # Configuration
    SCHOOL_URL = "https://www.crescentschool.org/"  # Replace with actual URL
    
    # Supabase configuration
    SUPABASE_URL = os.getenv("SUPABASE_URL")  # Your Supabase project URL
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Your Supabase anon/public key
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Your Gemini API key
    
    if not all([SUPABASE_URL, SUPABASE_KEY, GEMINI_API_KEY]):
        print("Please set the following environment variables:")
        print("SUPABASE_URL, SUPABASE_KEY, GEMINI_API_KEY")
        return
    
    # Initialize Supabase Vector DB
    print("Step 1: Initializing Supabase Vector Database...")
    vector_db = SupabaseVectorDB(SUPABASE_URL, SUPABASE_KEY)
    
    # Step 2: Crawl the website using Crawl4AI
    print("Step 2: Crawling website with Crawl4AI...")
    crawler = Crawl4AIWrapper(max_pages=50)  # Adjust as needed
    crawled_data = await crawler.crawl_website(SCHOOL_URL)
    print(f"Crawled {len(crawled_data)} pages")
    
    # Print some sample URLs that were crawled for verification
    print("\nSample URLs crawled:")
    for i, (url, _) in enumerate(crawled_data[:5]):
        print(f"  {i+1}. {url}")
    
    # Step 3: Chunk the text
    print("Step 3: Chunking text...")
    chunker = ContextAwareChunker(max_chunk_size=512, overlap=50)
    all_texts = []
    all_urls = []
    
    for url, text in crawled_data:
        if text and text.strip():  # Only process if text exists
            chunks = chunker.chunk_text(text)
            for chunk in chunks:
                all_texts.append(chunk)
                all_urls.append(url)
    
    print(f"Created {len(all_texts)} text chunks from {len(crawled_data)} pages")
    
    # Step 4: Add embeddings to Supabase
    print("Step 4: Adding embeddings to Supabase...")
    if all_texts:  # Only add if we have text
        vector_db.add_texts(all_texts, all_urls)
    else:
        print("No text content found to add to database.")
    
    # Step 5: Initialize RAG pipeline with Gemini
    print("Step 5: Building RAG pipeline with Gemini...")
    rag_pipeline = RAGPipeline(vector_db, GEMINI_API_KEY)
    
    # Test the pipeline with a simple query to see what's in the database
    print("\nTesting search functionality...")
    test_search = vector_db.search("admission", top_k=3)
    print(f"Found {len(test_search)} documents related to 'admission'")
    
    # Test the pipeline
    print("\nRAG pipeline is ready!")
    
    # Interactive mode
    print("\nInteractive mode (type 'quit' to exit):")
    while True:
        question = input("\nEnter your question: ")
        if question.lower() == 'quit':
            break
        
        try:
            response = rag_pipeline.query(question)
            print(f"Answer: {response}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())