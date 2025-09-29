import os
import json
import time
import logging
from typing import List, Dict, Set, Optional
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
import hashlib
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup
import chromadb
from sentence_transformers import SentenceTransformer
from chromadb.config import Settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crescent_crawler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class CrawledPage:
    """Data class to store crawled page information"""
    url: str
    title: str
    content: str
    chunks: List[str]
    timestamp: datetime
    word_count: int

class CrescentWebsiteCrawler:
    """
    Web crawler specifically for Crescent School website.
    It crawls pages, extracts content, chunks it.
    """
    
    def __init__(self, base_url: str, max_pages: int = 1000):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.max_pages = max_pages
        self.visited_urls: Set[str] = set()
        self.crawled_pages: List[CrawledPage] = []
        
        # Configure session for better performance
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'CrescentSchoolBot 1.0 (Educational Purpose)'
        })
        
        # Define content patterns to focus on (optional, but can help prioritize)
        self.content_keywords = [
            'about', 'admissions', 'curriculum', 'academics', 'faculty', 
            'programs', 'courses', 'student', 'campus', 'news', 'events',
            'contact', 'directory', 'policy', 'handbook', 'calendar',
            'crescent', 'school', 'learning', 'education', 'boys', 'toronto'
        ]
        
        # Define patterns to ignore
        self.ignore_patterns = [
            # File types
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.jpg', '.jpeg', '.png', '.gif', '.svg', '.zip', '.rar', '.mp4',
            # Social media and external links
            'facebook.com', 'twitter.com', 'instagram.com', 'linkedin.com',
            'youtube.com', 'vimeo.com', 'tiktok.com',
            # General non-content patterns
            'social', 'share', 'login', 'register', 'admin', 'wp-admin', 'wp-login',
            'search', 'cart', 'checkout', 'payment', 'newsletter', 'subscribe',
            'donate', 'donation', 'eventbrite', 'ticket', 'booking', 'appointment',
            # Specific to Crescent School (if known to be non-content)
            # Add any specific patterns if needed, e.g., 'alumni-network' if it's mostly links
        ]

    def is_relevant_url(self, url: str) -> bool:
        """Check if URL is relevant for crawling based on domain and patterns."""
        parsed = urlparse(url)
        
        # Check if it's an external link (not on crescentschool.org)
        if parsed.netloc and parsed.netloc != self.domain:
            return False
            
        # Check ignore patterns
        url_lower = url.lower()
        for pattern in self.ignore_patterns:
            if pattern in url_lower:
                return False

        # Basic check: if it's a valid http/https URL and within the domain
        # The content keywords are more for prioritization if needed, 
        # but for completeness, we'll still crawl most pages on the domain.
        # This check ensures it's a standard web page URL.
        if parsed.scheme in ['http', 'https'] and parsed.netloc == self.domain:
             # Ensure it doesn't end with a file extension (common heuristic)
             path = parsed.path.lower()
             if not any(path.endswith(ext) for ext in ['.html', '.htm', ''] + self.ignore_patterns if '.' in ext):
                 # If path has no extension or has .html/.htm, it's likely a page
                 # Or just check if it's not a known file type link
                 return True
             elif any(ext in path for ext in ['.html', '.htm']): # Explicitly html pages
                 return True
             # If path looks like a directory or has no extension, assume page
             elif '.' not in os.path.basename(path) or path.endswith('/'):
                 return True

        # If it passes domain check and doesn't match ignore patterns, crawl it
        return parsed.scheme in ['http', 'https'] and parsed.netloc == self.domain


    def extract_content(self, html: str, url: str) -> str:
        """Extract meaningful text content from HTML, focusing on main content."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Attempt to find main content areas first
        # Common selectors for main content
        main_content_selectors = [
            'main',
            'article',
            '[role="main"]',
            '.main-content',
            '.content',
            '.post-content',
            '#content',
            '.entry-content',
            '.page-content',
            '.primary-content',
            '.site-content',
            '.main-body'
        ]

        content_element = None
        for selector in main_content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                logger.debug(f"Found main content using selector: {selector} on {url}")
                break

        if not content_element:
            # Fallback to the entire body if no main content area found
            content_element = soup.find('body')
            logger.debug(f"Using body as content source for {url}")

        if content_element:
            # Remove unwanted elements within the main content area
            for element in content_element(['script', 'style', 'nav', 'header', 'footer', 
                                          'aside', 'menu', 'form', 'input', 'button', 'img']):
                element.decompose()

            # Remove elements likely to be navigation or ads based on class/id
            for element in content_element.find_all():
                classes = element.get('class', [])
                ids = [element.get('id')] if element.get('id') else []
                combined_attrs = ' '.join(classes + ids).lower()
                if any(bad_attr in combined_attrs for bad_attr in 
                      ['nav', 'menu', 'sidebar', 'advertisement', 'ad-', 'social', 
                       'share', 'cookie', 'popup', 'modal', 'search', 'widget', 'footer']):
                    element.decompose()

            # Extract text content
            text = content_element.get_text(separator=' ', strip=True)
        else:
            # Fallback if no body or main content is found
            text = ""

        # Clean up the text: remove extra whitespace and newlines
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text

    def chunk_text(self, text: str, max_chunk_size: int = 200, overlap: int = 20) -> List[str]:
        """Chunk text into semantically coherent pieces with overlap."""
        if not text:
            return []
        
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()] # Clean up sentences
        if not sentences:
            return []

        chunks = []
        current_chunk = ""
        current_word_count = 0

        for sentence in sentences:
            sentence_word_count = len(sentence.split())
            
            # If adding this sentence exceeds the limit
            if current_word_count + sentence_word_count > max_chunk_size:
                if current_chunk.strip(): # If there's already content in the chunk
                    chunks.append(current_chunk.strip())
                
                # Start a new chunk. If the sentence itself is too long, it might go over,
                # but we handle very long sentences later. For now, try to add it.
                # A better strategy might be to split the long sentence, but for now:
                # Start new chunk with this sentence
                current_chunk = sentence
                current_word_count = sentence_word_count
            else:
                # Add sentence to current chunk
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
                current_word_count += sentence_word_count

        # Add the last chunk if it exists
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # Handle potentially very long chunks (e.g., if a single sentence was > max_chunk_size)
        final_chunks = []
        for chunk in chunks:
            words = chunk.split()
            if len(words) <= max_chunk_size:
                final_chunks.append(chunk)
            else:
                # Split the long chunk into smaller ones
                for i in range(0, len(words), max_chunk_size - overlap):
                    sub_chunk_words = words[i:i + max_chunk_size]
                    final_chunks.append(" ".join(sub_chunk_words))

        # Filter out very short chunks
        final_chunks = [chunk for chunk in final_chunks if len(chunk.split()) >= 10]
        
        return final_chunks


    def crawl_page(self, url: str) -> Optional[CrawledPage]:
        """Crawl a single page and return structured data."""
        try:
            logger.info(f"Crawling: {url}")
            response = self.session.get(url, timeout=15) # Increased timeout
            response.raise_for_status()
            
            # Extract content
            content = self.extract_content(response.text, url)
            
            # Get title
            soup = BeautifulSoup(response.text, 'html.parser')
            title_tag = soup.find('title')
            title = title_tag.text.strip() if title_tag else url.split('/')[-1].replace('-', ' ').replace('_', ' ').title()
            
            # Chunk the content
            chunks = self.chunk_text(content)
            
            page_data = CrawledPage(
                url=url,
                title=title,
                content=content,
                chunks=chunks,
                timestamp=datetime.now(),
                word_count=len(content.split())
            )
            
            logger.info(f"Successfully crawled {url} - {len(chunks)} chunks created")
            return page_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error crawling {url}: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing {url}: {str(e)}")
        return None

    def get_links_from_page(self, url: str) -> List[str]:
        """Extract all internal links from a page."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            links = []
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                
                if self.is_relevant_url(full_url):
                    links.append(full_url)
            
            return list(set(links))  # Remove duplicates
            
        except Exception as e:
            logger.error(f"Error extracting links from {url}: {str(e)}")
            return []

    def crawl_website(self) -> List[CrawledPage]:
        """Main crawling method - performs breadth-first crawl."""
        logger.info(f"Starting crawl of {self.base_url}")
        
        # Start with base URL
        urls_to_crawl = [self.base_url]
        
        while urls_to_crawl and len(self.visited_urls) < self.max_pages:
            current_url = urls_to_crawl.pop(0)
            
            if current_url in self.visited_urls:
                continue
                
            self.visited_urls.add(current_url)
            
            # Crawl the page
            page_data = self.crawl_page(current_url)
            if page_data is not None:
                self.crawled_pages.append(page_data)
            
            # Get links from current page
            new_links = self.get_links_from_page(current_url)
            
            # Add new links to crawl queue if they haven't been visited and we haven't hit the limit
            for link in new_links:
                if link not in self.visited_urls and len(self.visited_urls) < self.max_pages:
                    urls_to_crawl.append(link)
            
            # Be respectful - add delay between requests to the same domain
            time.sleep(1.0) # Increased delay for politeness
        
        logger.info(f"Crawling completed. Total pages crawled: {len(self.crawled_pages)}")
        return self.crawled_pages

class TextEmbedder:
    """Handles text embedding using sentence transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        if not texts:
            return []
        
        # Batch processing for efficiency
        embeddings = self.model.encode(texts, show_progress_bar=True)
        return embeddings.tolist()

class VectorDatabase:
    """Manages vector storage and indexing using ChromaDB."""
    
    def __init__(self, collection_name: str = "crescent_school_kb"):
        self.client = chromadb.PersistentClient(path="./chroma_data")
        
        # Create or get collection
        try:
            # Try to get existing collection first
            self.collection = self.client.get_collection(name=collection_name)
            logger.info(f"Loaded existing collection: {collection_name}")
        except:
            # If it doesn't exist, create it
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}  # Use cosine similarity
            )
            logger.info(f"Created new collection: {collection_name}")
        
    def add_texts_with_metadata(self, texts: List[str], metadatas: List[Dict], ids: List[str]):
        """Add texts, their metadata, and IDs to the vector database."""
        if not texts:
            logger.warning("No texts provided to add to vector database.")
            return
            
        logger.info(f"Generating embeddings for {len(texts)} text chunks...")
        embedder = TextEmbedder()
        embeddings = embedder.embed_texts(texts)
        
        logger.info(f"Adding {len(texts)} items to vector database...")
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=texts, # Store the raw text chunk
            metadatas=metadatas, # Store metadata like URL, title, chunk index
            ids=ids # Store unique IDs
        )
        
        logger.info(f"Successfully added {len(texts)} texts to vector database collection '{self.collection.name}'")

class CrescentKnowledgeBaseBuilder:
    """Main class that orchestrates crawling, chunking, and vectorizing."""
    
    def __init__(self, base_url: str = "https://www.crescentschool.org/", max_pages: int = 1000):
        self.crawler = CrescentWebsiteCrawler(base_url, max_pages)
        self.vector_db = VectorDatabase(collection_name="crescent_school_kb")
        
    def build_knowledge_base(self):
        """Complete process: crawl, extract, chunk, embed, and index."""
        logger.info("--- Starting Crescent School Knowledge Base Build ---")
        
        # Step 1: Crawl the website
        crawled_pages = self.crawler.crawl_website()
        
        if not crawled_pages:
            logger.warning("No pages were successfully crawled. Exiting.")
            return

        # Step 2: Prepare data for vector database
        all_texts = []
        all_metadatas = []
        all_ids = []
        
        total_chunks = 0
        for page in crawled_pages:
            for i, chunk in enumerate(page.chunks):
                # Create unique ID for each chunk using URL and chunk index
                chunk_id = hashlib.md5(f"{page.url}_chunk_{i}".encode()).hexdigest()
                
                metadata = {
                    'url': page.url,
                    'title': page.title,
                    'chunk_index': i,
                    'word_count': len(chunk.split()),
                    'crawl_timestamp': page.timestamp.isoformat(),
                    'source_page_total_chunks': len(page.chunks)
                }
                
                all_texts.append(chunk)
                all_metadatas.append(metadata)
                all_ids.append(chunk_id)
                total_chunks += 1
        
        logger.info(f"Prepared {total_chunks} chunks from {len(crawled_pages)} pages for vectorization.")

        # Step 3: Add all prepared data to vector database
        if all_texts:
            self.vector_db.add_texts_with_metadata(all_texts, all_metadatas, all_ids)
        else:
            logger.warning("No text chunks were prepared for vectorization.")
        
        logger.info("--- Knowledge Base Build Completed ---")
        logger.info(f"Indexed {total_chunks} chunks from {len(crawled_pages)} pages.")
        
        # Save crawl report
        self._save_crawl_report(crawled_pages, total_chunks)
        
        return total_chunks, len(crawled_pages)
    
    def _save_crawl_report(self, pages: List[CrawledPage], total_chunks: int):
        """Save a report of the crawling process."""
        report = {
            'total_pages_crawled': len(pages),
            'total_chunks_indexed': total_chunks,
            'crawled_urls': [page.url for page in pages],
            'processing_timestamp': datetime.now().isoformat(),
            'stats': {
                'avg_chunks_per_page': total_chunks / len(pages) if pages else 0,
                'avg_words_per_chunk': sum(len(page.content.split()) for page in pages) / total_chunks if total_chunks > 0 else 0,
                'total_words_crawled': sum(page.word_count for page in pages)
            }
        }
        
        with open('crescent_crawl_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info("Crawl report saved to crescent_crawl_report.json")

def main():
    """Main execution function."""
    # Configuration for Crescent School
    SCHOOL_URL = "https://www.crescentschool.org/"
    MAX_PAGES = 1000 # Adjust based on the size of the site
    
    # Initialize and run the knowledge base builder
    kb_builder = CrescentKnowledgeBaseBuilder(SCHOOL_URL, MAX_PAGES)
    
    try:
        total_chunks, total_pages = kb_builder.build_knowledge_base()
        logger.info(f"Knowledge Base Build Successful!")
        logger.info(f" - Pages Crawled: {total_pages}")
        logger.info(f" - Chunks Indexed: {total_chunks}")
        
    except KeyboardInterrupt:
        logger.info("Crawling interrupted by user.")
    except Exception as e:
        logger.error(f"An error occurred during the build process: {str(e)}")
        logger.exception("Full traceback:") # Log the full stack trace

if __name__ == "__main__":
    main()