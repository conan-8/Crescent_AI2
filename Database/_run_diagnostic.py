"""
Generates db_diagnostic.txt from the live full_database ChromaDB collection.
Run from the Database/ directory: python _run_diagnostic.py
"""
import os
import sys
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db_diagnostic.txt")
COLLECTION = "full_database"

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

total = len(ids)
print(f"Fetched {total} chunks from '{COLLECTION}'")

# ── Per-chunk records ─────────────────────────────────────────────────────────
chunks = []
for chunk_id, doc, meta in zip(ids, documents, metadatas):
    length = len(doc) if doc else 0
    source = (meta or {}).get("source", "UNKNOWN")
    chunks.append({"id": chunk_id, "source": source, "len": length, "doc": doc or ""})

chunks_sorted_by_len = sorted(chunks, key=lambda c: c["len"])

# ── Length distribution ───────────────────────────────────────────────────────
buckets = {"<50": 0, "50-100": 0, "100-200": 0, "200-500": 0, "500+": 0}
for c in chunks:
    l = c["len"]
    if l < 50:       buckets["<50"]     += 1
    elif l < 100:    buckets["50-100"]  += 1
    elif l < 200:    buckets["100-200"] += 1
    elif l < 500:    buckets["200-500"] += 1
    else:            buckets["500+"]    += 1

# ── Per-source summary ────────────────────────────────────────────────────────
by_source = defaultdict(list)
for c in chunks:
    by_source[c["source"]].append(c)

source_rows = []
for url, cs in sorted(by_source.items()):
    avg = sum(x["len"] for x in cs) / len(cs)
    short = sum(1 for x in cs if x["len"] < 100)
    source_rows.append((url, len(cs), avg, short))
source_rows.sort(key=lambda r: r[0])

# ── Build report ──────────────────────────────────────────────────────────────
lines = []
W = 70

def h(text): lines.append("=" * 70); lines.append(text); lines.append("=" * 70)
def s(text): lines.append("─" * 42); lines.append(text); lines.append("─" * 42)

h(f"ChromaDB Diagnostic Report — collection: {COLLECTION}")
lines.append("")
lines.append(f"Total documents (chunks): {total}")
lines.append("")

s("Length Distribution (character count)")
for label, count in buckets.items():
    pct = count / total * 100 if total else 0
    lines.append(f"  {label:>8}  {count:>4}  ({pct:.1f}%)")
lines.append("")

s(f"{min(30, total)} Shortest Documents")
for i, c in enumerate(chunks_sorted_by_len[:30], 1):
    preview = repr(c["doc"][:120])
    lines.append(f"\n#{i:>2}  len={c['len']}  id={c['id']}")
    lines.append(f"     source={c['source']}")
    lines.append(f"     text={preview}")
lines.append("")

s("Per-Source Summary")
header = f"  {'Source URL':<70}  {'Chunks':>6}  {'Avg len':>7}  {'<100 chars':>10}"
lines.append(header)
lines.append(f"  {'-'*70}  {'-'*6}  {'-'*7}  {'-'*10}")
for url, count, avg, short in source_rows:
    lines.append(f"  {url:<70}  {count:>6}  {avg:>7.1f}  {short:>10}")
lines.append("")

# ── Removal recommendations ───────────────────────────────────────────────────
h("REMOVAL RECOMMENDATIONS")
lines.append("")
lines.append(
    "NOTE: Multiple single-chunk pages share identical ~379-char content,\n"
    "strongly suggesting the LLM returned the nav/header template instead\n"
    "of real page content. These are FAILED crawls masquerading as success."
)
lines.append("")

# Category 1: individual garbage chunks < 100 chars
cat1 = [c for c in chunks if c["len"] < 100]
s("CATEGORY 1 — Individual garbage chunks (< 100 chars)")
lines.append("Delete these specific chunk IDs. They are title fragments or nav")
lines.append("artifacts that will poison retrieval by matching unrelated queries.")
lines.append("")
lines.append(f"  {'CHUNK ID':<80}  {'LEN':>4}  REASON")
lines.append(f"  {'-'*80}  {'-'*4}  {'-'*25}")
for c in sorted(cat1, key=lambda x: x["len"]):
    lines.append(f"  {c['id']:<80}  {c['len']:>4}  Short fragment / title only")
lines.append(f"\n  Total: {len(cat1)} chunks")
lines.append("")

# Category 2: off-topic entire sources
off_topic_prefixes = [
    ("https://alumni.crescentschool.org", "Alumni domain — wrong audience"),
    ("https://www.crescentschool.org/careers", "Staff hiring — not for parents/students"),
    ("https://www.crescentschool.org/support-crescent", "Fundraising — not for parents/students"),
    ("https://www.crescentschool.org/News-Detail", "Dated news article — not evergreen"),
    ("https://www.crescentschool.org/page/News-Detail", "Dated news article — not evergreen"),
    ("https://www.crescentschool.org/why-crescent/crescent-blogs", "Blog index — no factual content"),
]

cat2_rows = []
for url, cs in by_source.items():
    for prefix, reason in off_topic_prefixes:
        if url.startswith(prefix):
            cat2_rows.append((url, len(cs), reason))
            break
cat2_rows.sort()
cat2_total = sum(r[1] for r in cat2_rows)

s("CATEGORY 2 — Off-topic entire sources (DELETE all chunks for these URLs)")
lines.append("These pages are irrelevant to the chatbot's purpose of answering")
lines.append("prospective student/parent questions.")
lines.append("")
lines.append(f"  {'SOURCE URL':<70}  {'CHUNKS':>6}  REASON")
lines.append(f"  {'-'*70}  {'-'*6}  {'-'*40}")
for url, count, reason in cat2_rows:
    lines.append(f"  {url:<70}  {count:>6}  {reason}")
lines.append(f"\n  Total: {cat2_total} chunks to remove")
lines.append("")

# Category 3: /page/ duplicate URLs
page_dupes = []
for url, cs in by_source.items():
    if "/page/" in url:
        canonical = url.replace("/page/", "/", 1)
        if canonical in by_source:
            page_dupes.append((url, len(cs), canonical))
# Also trailing slash dupe
trailing = "https://www.crescentschool.org/"
if trailing in by_source and "https://www.crescentschool.org" in by_source:
    page_dupes.append((trailing, len(by_source[trailing]), "https://www.crescentschool.org"))
page_dupes.sort()
cat3_total = sum(r[1] for r in page_dupes)

s("CATEGORY 3 — Duplicate /page/ prefix URLs (DELETE one copy of each pair)")
lines.append("The spider crawled both /foo and /page/foo for the same content.")
lines.append("Keep the canonical URL (without /page/), delete the /page/ duplicate.")
lines.append("")
lines.append(f"  {'DUPLICATE (delete)':<70}  {'CHUNKS':>6}  CANONICAL (keep)")
lines.append(f"  {'-'*70}  {'-'*6}  {'-'*50}")
for dupe, count, canonical in page_dupes:
    lines.append(f"  {dupe:<70}  {count:>6}  {canonical}")
lines.append(f"\n  Total: {cat3_total} chunks to remove")
lines.append("")

# Category 4: failed crawls (single chunk, ~379 chars) that are high-value
IMPORTANT_PATHS = [
    "/how-to-apply/",
    "/academics/",
    "/why-crescent/",
    "/about/",
    "/character-in-action/",
]
FINGERPRINT_LEN = (350, 410)  # 379 ± tolerance

cat4 = []
for url, cs in by_source.items():
    if len(cs) == 1:
        avg_len = cs[0]["len"]
        if FINGERPRINT_LEN[0] <= avg_len <= FINGERPRINT_LEN[1]:
            priority = "HIGH" if any(p in url for p in ["/how-to-apply/", "/academics/upper-school", "/academics/middle-school", "/academics/lower-school"]) else "MEDIUM" if "/academics/" in url else "LOW"
            cat4.append((priority, url))
cat4.sort(key=lambda x: ({"HIGH": 0, "MEDIUM": 1, "LOW": 2}[x[0]], x[1]))

s("CATEGORY 4 — Failed crawls needing re-crawl (DO NOT DELETE — refresh instead)")
lines.append("Single-chunk pages at ~379 chars: LLM returned nav template, not content.")
lines.append("Re-crawl with CSS selector or fallback strategy.")
lines.append("")
lines.append(f"  {'PRIORITY':<8}  SOURCE URL")
lines.append(f"  {'-'*8}  {'-'*70}")
for priority, url in cat4:
    lines.append(f"  {priority:<8}  {url}")
lines.append("")

# Summary
cat1_ids_not_in_cat2 = [c for c in cat1 if not any(c["source"].startswith(p) for p, _ in off_topic_prefixes)]
unique_cat1 = len(cat1_ids_not_in_cat2)

s("REMOVAL SUMMARY")
lines.append(f"  Category 1 — Garbage chunks (individual deletes)  : {len(cat1):>4} chunks")
lines.append(f"  Category 2 — Off-topic entire sources             : {cat2_total:>4} chunks")
lines.append(f"  Category 3 — Duplicate /page/ URLs                : {cat3_total:>4} chunks")
lines.append(f"  (overlap between categories deducted automatically at delete time)")
lines.append(f"  ──────────────────────────────────────────────────────────────────")
lines.append(f"  Current total chunks                              : {total:>4}")
lines.append(f"  Category 4 — Failed crawls needing re-crawl      : {len(cat4):>4} URLs (not deleted)")

output = "\n".join(lines)
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(output)

print(f"\nDiagnostic written to {OUTPUT_PATH}")
print(f"Total chunks: {total}")
print(f"Cat1 (garbage): {len(cat1)}, Cat2 (off-topic): {cat2_total}, Cat3 (dupes): {cat3_total}, Cat4 (re-crawl needed): {len(cat4)}")
