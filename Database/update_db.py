"""
update_db.py — Refresh ChromaDB entries for specified URLs (or all stored URLs).

Usage:
    python update_db.py
        Refreshes every URL currently stored in the collection.

    python update_db.py URL [URL ...]
        Refreshes only the given URL(s).

    python update_db.py --dry-run
        Prints what would change without touching the database.

    python update_db.py --collection my_collection
        Targets a specific ChromaDB collection (default: full_database).
"""

import os
import sys
import argparse
import asyncio
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import get_chroma_db, ExtractedContent, EXTRACTION_INSTRUCTION
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, LLMExtractionStrategy, LLMConfig
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

DEFAULT_COLLECTION = "full_database"

_TEXT_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    length_function=len,
)


# ---------------------------------------------------------------------------
# Collection helpers
# ---------------------------------------------------------------------------

def get_all_urls_with_types(collection):
    """
    Return {url: type_str} for every unique source URL in the collection.
    type_str is "enrollment" for enrollment pages or "handbook" for all others.
    """
    result = collection.get(include=["metadatas"])
    url_types = {}
    for meta in (result.get("metadatas") or []):
        if meta and "source" in meta:
            url = meta["source"]
            if url not in url_types:
                url_types[url] = meta.get("type", "handbook")
    return url_types


def get_chunk_ids_for_url(collection, url):
    """Return all chunk IDs whose source metadata matches url."""
    result = collection.get(where={"source": url}, include=["metadatas"])
    return result.get("ids", [])


def delete_chunks_for_url(collection, url):
    """
    Delete all chunks where source == url.
    Returns the number of chunks removed.
    """
    ids = get_chunk_ids_for_url(collection, url)
    if ids:
        collection.delete(ids=ids)
    return len(ids)


# ---------------------------------------------------------------------------
# Crawlers
# ---------------------------------------------------------------------------

async def crawl_url_markdown(url):
    """
    Crawl url using fit_markdown — the same strategy used for enrollment pages.
    Returns (doc_list, id_list, metadata_list).
    """
    run_conf = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url, config=run_conf)

    if not result.success:
        print(f"  [ERROR] Crawl failed for {url}: {getattr(result, 'error_message', '')}")
        return [], [], []

    content = result.markdown.fit_markdown or result.markdown
    if not content:
        print(f"  [WARN] No content for {url}")
        return [], [], []

    chunks = _TEXT_SPLITTER.split_text(content)
    ids = [f"enrollment_{url}_chunk_{j}" for j in range(len(chunks))]
    metadatas = [{"source": url, "type": "enrollment"} for _ in chunks]
    return chunks, ids, metadatas


async def crawl_url_llm(url):
    """
    Crawl url using LLM extraction — the same strategy used for handbook pages.
    Returns (doc_list, id_list, metadata_list).
    """
    llm_conf = LLMConfig(
        provider="gemini/gemini-2.5-flash",
        api_token=os.environ.get("GEMINI_API_KEY"),
    )
    extraction_strategy = LLMExtractionStrategy(
        llm_config=llm_conf,
        schema=ExtractedContent.model_json_schema(),
        instruction=EXTRACTION_INSTRUCTION,
        extraction_type="schema",
    )
    run_conf = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=extraction_strategy,
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url, config=run_conf)

    if not result.success or not result.extracted_content:
        print(f"  [ERROR] Crawl failed for {url}: {getattr(result, 'error_message', '')}")
        return [], [], []

    try:
        data = json.loads(result.extracted_content)
        if isinstance(data, list) and data:
            extracted_text = data[0].get("relevant_text")
        elif isinstance(data, dict):
            extracted_text = data.get("relevant_text")
        else:
            extracted_text = None
    except json.JSONDecodeError:
        print(f"  [ERROR] Failed to parse LLM output for {url}")
        return [], [], []

    if not extracted_text:
        print(f"  [WARN] LLM returned no text for {url}")
        return [], [], []

    chunks = _TEXT_SPLITTER.split_text(extracted_text)
    ids = [f"{url}_chunk_{j}" for j in range(len(chunks))]
    metadatas = [{"source": url} for _ in chunks]
    return chunks, ids, metadatas


# ---------------------------------------------------------------------------
# Core update logic
# ---------------------------------------------------------------------------

async def update_url(collection, url, url_type, dry_run=False):
    """
    Delete existing chunks for url, re-crawl, and re-index.
    Returns (chunks_removed, chunks_added).
    In dry_run mode no changes are made; chunks_added is always 0.
    """
    existing_ids = get_chunk_ids_for_url(collection, url)
    chunks_removed = len(existing_ids)

    if dry_run:
        print(f"  [DRY-RUN] {url}  [{url_type}]  —  would remove {chunks_removed} chunk(s)")
        return chunks_removed, 0

    if existing_ids:
        collection.delete(ids=existing_ids)
        print(f"  Removed {chunks_removed} old chunk(s)")

    if url_type == "enrollment":
        doc_list, id_list, metadata_list = await crawl_url_markdown(url)
    else:
        doc_list, id_list, metadata_list = await crawl_url_llm(url)

    chunks_added = len(doc_list)
    if doc_list:
        collection.add(ids=id_list, documents=doc_list, metadatas=metadata_list)
        print(f"  Added {chunks_added} new chunk(s)")
    else:
        print(f"  [WARN] No chunks produced for {url}")

    return chunks_removed, chunks_added


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description=(
            "Refresh ChromaDB entries for specified URLs (or all stored URLs). "
            "Omit URLs to refresh every URL currently in the collection."
        )
    )
    parser.add_argument(
        "urls",
        nargs="*",
        metavar="URL",
        help="URLs to refresh. Omit to refresh all URLs in the collection.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be updated without making any changes.",
    )
    parser.add_argument(
        "--collection",
        default=DEFAULT_COLLECTION,
        metavar="NAME",
        help=f"ChromaDB collection to use (default: {DEFAULT_COLLECTION}).",
    )
    return parser.parse_args(argv)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def run(args):
    collection = get_chroma_db(args.collection)

    if args.urls:
        # Specific URLs supplied — look up their stored types so we use the
        # right crawler. Default to "enrollment" (markdown) for unknown URLs.
        stored = get_all_urls_with_types(collection)
        url_types = {url: stored.get(url, "enrollment") for url in args.urls}
    else:
        url_types = get_all_urls_with_types(collection)
        if not url_types:
            print("No URLs found in the collection. Nothing to update.")
            return

    target_urls = list(url_types.keys())
    action = "preview" if args.dry_run else "update"
    print(f"\nURLs to {action}: {len(target_urls)}")
    for url in target_urls:
        print(f"  {url}  [{url_types[url]}]")
    print()

    total_removed = 0
    total_added = 0

    for url in target_urls:
        print(f"Processing: {url}")
        removed, added = await update_url(
            collection, url, url_types[url], dry_run=args.dry_run
        )
        total_removed += removed
        total_added += added

    print("\n" + "=" * 60)
    if args.dry_run:
        print("DRY-RUN SUMMARY  (no changes made)")
        print(f"  URLs that would be refreshed    : {len(target_urls)}")
        print(f"  Chunks that would be removed    : {total_removed}")
    else:
        print("UPDATE SUMMARY")
        print(f"  URLs updated    : {len(target_urls)}")
        print(f"  Chunks removed  : {total_removed}")
        print(f"  Chunks added    : {total_added}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run(parse_args()))
