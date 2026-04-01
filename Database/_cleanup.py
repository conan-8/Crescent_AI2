"""
_cleanup.py — Delete Category 1 and Category 3 chunks from full_database.

Category 1: individual chunks shorter than 100 chars (garbage fragments)
Category 3: all chunks from /page/... URLs where the canonical (non-/page/) exists
            + trailing-slash homepage duplicate

Run: python _cleanup.py [--dry-run]
"""
import os
import sys
import argparse
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

COLLECTION = "full_database"
DRY_RUN = "--dry-run" in sys.argv

google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
    api_key=os.environ.get("GEMINI_API_KEY"),
    model_name="gemini-embedding-001",
)
chroma_client = chromadb.PersistentClient(path=os.environ.get("CHROMA_DB_PATH"))
collection = chroma_client.get_or_create_collection(name=COLLECTION, embedding_function=google_ef)

result = collection.get(include=["documents", "metadatas"])
ids       = result.get("ids", [])
documents = result.get("documents", [])
metadatas = result.get("metadatas", [])

print(f"Current chunk count: {len(ids)}")

# Build lookup structures
by_source = defaultdict(list)
for chunk_id, doc, meta in zip(ids, documents, metadatas):
    length = len(doc) if doc else 0
    source = (meta or {}).get("source", "UNKNOWN")
    by_source[source].append({"id": chunk_id, "len": length})

all_sources = set(by_source.keys())

# ── Category 1: chunks shorter than 100 chars ────────────────────────────────
cat1_ids = []
for chunk_id, doc in zip(ids, documents):
    if len(doc if doc else "") < 100:
        cat1_ids.append(chunk_id)

print(f"\nCategory 1 — garbage chunks (<100 chars): {len(cat1_ids)} to delete")
for cid in cat1_ids:
    print(f"  DELETE chunk: {cid}")

# ── Category 3: /page/ duplicates + trailing-slash homepage ──────────────────
cat3_sources = []

for source in all_sources:
    if "/page/" in source:
        canonical = source.replace("/page/", "/", 1)
        if canonical in all_sources:
            cat3_sources.append(source)

# Trailing-slash homepage duplicate
trailing = "https://www.crescentschool.org/"
canonical_home = "https://www.crescentschool.org"
if trailing in all_sources and canonical_home in all_sources:
    cat3_sources.append(trailing)

cat3_ids = []
for source in cat3_sources:
    source_ids = [c["id"] for c in by_source[source]]
    cat3_ids.extend(source_ids)
    print(f"\nCategory 3 — duplicate source: {source}")
    print(f"  Deleting {len(source_ids)} chunk(s) -> canonical: {source.replace('/page/', '/', 1)}")

print(f"\nCategory 3 total chunks to delete: {len(cat3_ids)}")

# ── Deduplicate across categories ─────────────────────────────────────────────
all_to_delete = list(set(cat1_ids + cat3_ids))
print(f"\nTotal unique chunks to delete: {len(all_to_delete)}")
print(f"Remaining after cleanup: {len(ids) - len(all_to_delete)}")

# ── Execute ───────────────────────────────────────────────────────────────────
if DRY_RUN:
    print("\n[DRY RUN] No changes made.")
else:
    if all_to_delete:
        collection.delete(ids=all_to_delete)
        final_count = collection.count()
        print(f"\nDone. Collection now has {final_count} chunks.")
    else:
        print("\nNothing to delete.")
