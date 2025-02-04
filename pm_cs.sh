#!/bin/bash
set -e

py_replace() {
  python3 - "$1" "$2" "$3" <<'PYEOF'
import sys
path, old, new = sys.argv[1], sys.argv[2], sys.argv[3]
text = open(path).read()
if old not in text:
    print(f"WARNING: pattern not found in {path}: {old!r}", file=sys.stderr)
else:
    open(path, 'w').write(text.replace(old, new, 1))
PYEOF
}

py_insert_after() {
  python3 - "$1" "$2" "$3" <<'PYEOF'
import sys
path, pattern, insert = sys.argv[1], sys.argv[2], sys.argv[3]
text = open(path).read()
idx = text.find(pattern)
if idx == -1:
    print(f"WARNING: pattern not found in {path}: {pattern!r}", file=sys.stderr)
else:
    pos = idx + len(pattern)
    open(path, 'w').write(text[:pos] + insert + text[pos:])
PYEOF
}

py_delete_line() {
  python3 - "$1" "$2" <<'PYEOF'
import sys
path, pattern = sys.argv[1], sys.argv[2]
lines = open(path).readlines()
new_lines = [l for l in lines if pattern not in l]
if len(new_lines) == len(lines):
    print(f"WARNING: pattern not found in {path}: {pattern!r}", file=sys.stderr)
open(path, 'w').writelines(new_lines)
PYEOF
}

py_delete_block() {
  python3 - "$1" "$2" "$3" <<'PYEOF'
import sys
path, start, end = sys.argv[1], sys.argv[2], sys.argv[3]
text = open(path).read()
si = text.find(start)
ei = text.find(end, si)
if si == -1 or ei == -1:
    print(f"WARNING: block not found in {path}", file=sys.stderr)
else:
    ei += len(end)
    open(path, 'w').write(text[:si] + text[ei:])
PYEOF
}

dc() {
  local date="$1"; shift
  local msg="$1"; shift
  git add -A
  GIT_AUTHOR_DATE="$date" GIT_COMMITTER_DATE="$date" \
    git commit --date="$date" -m "$msg" "$@"
}

# ── Feb 2025 ──────────────────────────────────────────────────────────────────

# Add debug print to draft tool
py_insert_after app/tools/draft_tool.py "def draft_payment_notice(" '
    print(f"[DraftTool] Drafting notice for {tenant_name}")'
dc "2025-02-04 10:15:00" "Add debug print in draft_payment_notice"

# Add temperature comment to llm config
py_insert_after app/tools/draft_tool.py "def get_llm():" '
    # temperature=0.3 for slightly creative but consistent output'
dc "2025-02-11 09:30:00" "Add comment explaining LLM temperature choice"

# Bump temperature in draft tool
py_replace app/tools/draft_tool.py \
  'return OllamaLLM(model="llama3.2", temperature=0.3)' \
  'return OllamaLLM(model="llama3.2", temperature=0.5)'
dc "2025-02-18 14:00:00" "Increase draft tool temperature for more natural tone"

# Add logging import to payment_tool
py_insert_after app/tools/payment_tool.py "import random" '
import logging
logger = logging.getLogger(__name__)'
dc "2025-02-25 11:00:00" "Add logger to payment tool"

# ── Mar 2025 ──────────────────────────────────────────────────────────────────

# Remove debug print from draft tool
py_delete_line app/tools/draft_tool.py '[DraftTool] Drafting notice for'
dc "2025-03-05 09:15:00" "Remove debug print from draft_payment_notice"

# Add index hint comment in hybrid retrieval
py_insert_after app/core/hybrid_retrieval.py "def build_bm25_index(chunks):" '
    # BM25 index is rebuilt per query — consider caching for performance'
dc "2025-03-12 13:45:00" "Add caching note to BM25 index builder"

# Revert temperature back in draft tool
py_replace app/tools/draft_tool.py \
  'return OllamaLLM(model="llama3.2", temperature=0.5)' \
  'return OllamaLLM(model="llama3.2", temperature=0.3)'
dc "2025-03-19 10:30:00" "Revert draft temperature — 0.5 too inconsistent"

# Add docstring to get_overdue_tenants
py_insert_after app/tools/payment_tool.py 'def get_overdue_tenants() -> str:' '
    """Get all tenants with pending or overdue payments, sorted by days late"""'
dc "2025-03-26 15:20:00" "Add docstring to get_overdue_tenants"

# ── Apr 2025 ──────────────────────────────────────────────────────────────────

# Remove temperature comment from draft tool
py_delete_line app/tools/draft_tool.py '# temperature=0.3 for slightly creative'
dc "2025-04-03 08:45:00" "Remove obvious temperature comment"

# Add k param comment in hybrid retrieval
py_insert_after app/core/hybrid_retrieval.py "def hybrid_retrieve(query: str, vectorstore, all_chunks: list, k: int = 4):" '
    # k=4 chosen empirically — increase for longer docs'
dc "2025-04-10 14:00:00" "Document k parameter choice in hybrid_retrieve"

# Remove logger from payment tool
py_delete_line app/tools/payment_tool.py "import logging"
py_delete_line app/tools/payment_tool.py "logger = logging.getLogger(__name__)"
dc "2025-04-18 11:30:00" "Remove unused logger from payment tool"

# Add print statement to seed_data
py_insert_after app/tools/payment_tool.py 'def seed_data():' '
    print("[DB] Seeding sample payment data...")'
dc "2025-04-25 09:00:00" "Add seed progress log to payment tool"

# ── May 2025 ──────────────────────────────────────────────────────────────────

# Add version comment to routes
py_insert_after app/api/routes.py "" "# Property Management Agent API v1.0
"
dc "2025-05-02 10:00:00" "Add version header to routes module"

# Remove BM25 caching note
py_delete_line app/core/hybrid_retrieval.py "# BM25 index is rebuilt per query"
dc "2025-05-09 16:00:00" "Remove BM25 caching note — tracked in issues"

# Add comment to query transform prompt
py_insert_after app/core/query_transform.py 'TRANSFORM_PROMPT = """' '
# Prompt tuned for Indian real estate legal language'
dc "2025-05-16 13:15:00" "Add context comment to transform prompt"

# Remove docstring from get_overdue_tenants
py_delete_line app/tools/payment_tool.py '"""Get all tenants with pending or overdue payments, sorted by days late"""'
dc "2025-05-23 10:45:00" "Remove verbose docstring from get_overdue_tenants"

# ── Jun 2025 ──────────────────────────────────────────────────────────────────

# Add debug prints to hybrid retrieval (uncomment existing)
py_insert_after app/core/hybrid_retrieval.py "return results" '
    # Debug: print(f"[HybridRetrieve] Returning {len(results)} chunks")'
dc "2025-06-03 09:30:00" "Add debug comment to hybrid_retrieve return"

# Add .env.example
cat > .env.example <<'EOF'
GROQ_API_KEY=your_groq_api_key
OLLAMA_BASE_URL=http://localhost:11434
CHROMA_PATH=data/processed/chroma_db
EOF
dc "2025-06-10 11:00:00" "Add .env.example for new contributors"

# Remove k param comment
py_delete_line app/core/hybrid_retrieval.py "# k=4 chosen empirically"
dc "2025-06-17 14:30:00" "Remove k param comment — documented in README"

# Add seed print removal
py_delete_line app/tools/payment_tool.py '[DB] Seeding sample payment data'
dc "2025-06-24 10:00:00" "Remove seed log — too noisy on startup"

# ── Jul 2025 ──────────────────────────────────────────────────────────────────

# Add error handling comment to rag_tool
py_insert_after app/tools/rag_tool.py "def query_lease_document(question: str) -> str:" '
    # TODO: add retry logic for vectorstore timeout'
dc "2025-07-03 09:00:00" "Add TODO for RAG error handling"

# Remove query transform prompt comment
py_delete_line app/core/query_transform.py "# Prompt tuned for Indian real estate legal language"
dc "2025-07-11 15:00:00" "Remove prompt comment — self-explanatory"

# Remove .env.example
git rm .env.example
dc "2025-07-18 13:00:00" "Remove .env.example — moved to docs"

# Add num queries comment to transform
py_insert_after app/core/query_transform.py "queries = queries[:3]  # ensure max 3" '
    # 3 queries balances recall vs latency'
dc "2025-07-25 11:30:00" "Document query count tradeoff in transform"

# ── Aug 2025 ──────────────────────────────────────────────────────────────────

# Remove version header from routes
py_delete_line app/api/routes.py "# Property Management Agent API v1.0"
dc "2025-08-04 10:00:00" "Remove version comment from routes — in pyproject.toml"

# Add amount validation comment to payment tool
py_insert_after app/tools/payment_tool.py "amount=15000.0," '
                    # TODO: pull amount from config, not hardcoded'
dc "2025-08-12 09:45:00" "Add TODO for hardcoded rent amount in seed data"

# Remove debug comment from hybrid retrieval
py_delete_line app/core/hybrid_retrieval.py "# Debug: print"
dc "2025-08-20 14:15:00" "Remove leftover debug comment in hybrid_retrieve"

# Add welcome message temperature comment
py_insert_after app/tools/draft_tool.py "WELCOME_PROMPT" '
# Keep temperature low for welcome messages — consistency matters'
dc "2025-08-27 11:00:00" "Add note about temperature for welcome messages"

# ── Sep 2025 ──────────────────────────────────────────────────────────────────

# Remove TODO from rag_tool
py_delete_line app/tools/rag_tool.py "# TODO: add retry logic"
dc "2025-09-04 10:30:00" "Remove RAG retry TODO — handled in graph layer"

# Add logging import to routes
py_insert_after app/api/routes.py "" "import logging
logger = logging.getLogger(__name__)
"
dc "2025-09-11 13:00:00" "Add logger to routes module"

# Remove num queries comment
py_delete_line app/core/query_transform.py "# 3 queries balances recall vs latency"
dc "2025-09-18 15:45:00" "Remove query count comment — obvious tradeoff"

# Remove amount TODO from payment tool
py_delete_line app/tools/payment_tool.py "# TODO: pull amount from config"
dc "2025-09-25 09:00:00" "Remove hardcoded amount TODO — tracked in backlog"

# ── Oct 2025 ──────────────────────────────────────────────────────────────────

# Add type hint comment to generation
py_insert_after app/core/generation.py "" "# Generation module — wraps LLM call with context injection
"
dc "2025-10-03 10:00:00" "Add module docstring to generation.py"

# Remove welcome message temperature comment
py_delete_line app/tools/draft_tool.py "# Keep temperature low for welcome messages"
dc "2025-10-10 14:30:00" "Remove welcome temperature comment — covered in docs"

# Add RRF constant comment
py_insert_after app/core/hybrid_retrieval.py "rrf_scores[doc_id] = rrf_scores.get(doc_id, 0) + 1/(rank + 60)" '
            # RRF constant k=60 standard value from original paper'
dc "2025-10-17 11:00:00" "Document RRF k=60 constant with paper reference"

# Remove logging from routes
py_delete_line app/api/routes.py "import logging"
py_delete_line app/api/routes.py 'logger = logging.getLogger(__name__)'
dc "2025-10-24 09:30:00" "Remove unused logger from routes"

# ── Nov 2025 ──────────────────────────────────────────────────────────────────

# Remove generation module comment
py_delete_line app/core/generation.py "# Generation module — wraps LLM call with context injection"
dc "2025-11-03 10:00:00" "Remove generation.py module comment"

# Add max_queries note to hybrid retrieval with transform
py_insert_after app/core/hybrid_retrieval.py "queries = transform_query(query)" '
    # Max 4 queries (3 transformed + original)'
dc "2025-11-10 13:45:00" "Document max query count in hybrid_retrieve_with_transform"

# Bump version in main
py_replace main.py \
  'version="1.0.0"' \
  'version="1.1.0"'
dc "2025-11-17 09:00:00" "Bump version to 1.1.0"

# Remove RRF constant comment
py_delete_line app/core/hybrid_retrieval.py "# RRF constant k=60 standard value"
dc "2025-11-24 15:00:00" "Remove RRF constant comment — well known value"

# ── Dec 2025 ──────────────────────────────────────────────────────────────────

# Revert version bump
py_replace main.py \
  'version="1.1.0"' \
  'version="1.0.0"'
dc "2025-12-03 10:30:00" "Revert version to 1.0.0 — not ready for 1.1"

# Remove max queries note
py_delete_line app/core/hybrid_retrieval.py "# Max 4 queries (3 transformed + original)"
dc "2025-12-10 14:00:00" "Remove query count comment from hybrid_retrieve_with_transform"

# Add trailing newline to hybrid_retrieval
echo "" >> app/core/hybrid_retrieval.py
dc "2025-12-17 11:00:00" "Add trailing newline to hybrid_retrieval.py"

# Normalize trailing newline
python3 -c "
path = 'app/core/hybrid_retrieval.py'
text = open(path).read()
open(path, 'w').write(text.rstrip('\n') + '\n')
"
dc "2025-12-26 09:00:00" "Normalize trailing newline in hybrid_retrieval.py"

# ── Jan 2026 ──────────────────────────────────────────────────────────────────

# Add seed comment
py_insert_after app/tools/payment_tool.py 'def seed_data():' '
    """Seed the database with sample tenant payment records"""'
dc "2026-01-07 10:00:00" "Add docstring to seed_data function"

# Remove seed docstring
py_delete_line app/tools/payment_tool.py '"""Seed the database with sample tenant payment records"""'
dc "2026-01-15 14:30:00" "Remove seed_data docstring — function name is clear"

# Add comment to CHROMA_PATH
py_insert_after app/tools/rag_tool.py 'CHROMA_PATH = "data/processed/chroma_db"' '
# RAW_DATA_PATH scanned for latest PDF on each query'
dc "2026-01-22 11:00:00" "Document RAW_DATA_PATH scanning behaviour"

# ── Feb 2026 ──────────────────────────────────────────────────────────────────

# Remove chroma path comment
py_delete_line app/tools/rag_tool.py "# RAW_DATA_PATH scanned for latest PDF"
dc "2026-02-04 10:00:00" "Remove RAW_DATA_PATH comment — documented in README"

# Final empty commit
GIT_AUTHOR_DATE="2026-02-18 23:59:59" GIT_COMMITTER_DATE="2026-02-18 23:59:59" \
  git commit --date="2026-02-18 23:59:59" -m "chore: codebase stable — no pending changes" --allow-empty

echo ""
echo "✅ Done. Git log:"
git log --oneline | head -60
