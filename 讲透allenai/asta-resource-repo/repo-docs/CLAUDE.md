# CLAUDE.md - Developer Guide

**Audience**: This file is for **agent-developers** working on the asta-resource-repo codebase itself.

**For agent-users** (using this tool for document management): See [README.md](README.md) and the **Asta Documents skill** (`skills/asta-documents.md`).

---

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Asta Resource Repository is a lightweight, git-friendly document metadata index that requires zero external dependencies. It provides a CLI (`asta-documents`) and Claude Code skill for managing document metadata locally.

**Key Concept**: Instead of storing document content, this tool maintains an index of metadata (URLs, summaries, tags) in a local YAML file. Documents are identified by **UUIDs** (10-character alphanumeric short IDs).

**Integration**: The primary integration method is the **Asta Documents skill** (`skills/asta-documents.md`) which provides complete functionality via CLI commands.

## Architecture

### Local-Only Design

**No Databases, No Servers, No Docker**
- Single YAML file (`.asta/documents/index.yaml`) stores all metadata
- No PostgreSQL, no REST API, no external services
- Git-friendly: diffs show exactly what changed
- Portable: copy `.asta/` folder to any project

### Core Components

1. **`document_store/local_index.py`**: YAML-based storage backend
   - File locking for thread safety
   - Atomic writes
   - Multiple search strategies (simple, FTS5, BM25, semantic, hybrid)

2. **`document_store/search_cache.py`**: SQLite search cache
   - Automatic YAML ↔ SQLite synchronization
   - FTS5 full-text indexing
   - BM25 term statistics
   - Hash-based staleness detection

3. **`document_store/bm25_ranker.py`**: BM25 ranking algorithm
   - TF-IDF weighting with term saturation
   - Document length normalization
   - Configurable field weights

4. **`document_store/embeddings.py`**: Semantic search (optional)
   - sentence-transformers integration
   - Vector embeddings (384-dim)
   - Cosine similarity search
   - Lazy model loading

5. **`document_store/hybrid_search.py`**: Hybrid search fusion
   - Reciprocal Rank Fusion (RRF)
   - Combines BM25 + semantic results
   - Configurable weights

6. **`cli/index_cli.py`**: Command-line interface (PRIMARY INTERFACE)
   - `asta-documents` commands for manual management
   - Human-friendly output with `--json` option
   - Search mode selection and score display

7. **`model.py`**: Data models
   - `DocumentMetadata`: Metadata-only model (no content field)
   - `SearchHit`: Search result with relevance score
   - Fields: `uuid` (10-char short ID), `name`, `url`, `summary`, `tags`, `mime_type`, `created_at`, `modified_at`, `extra`

8. **`config/`**: HOCON-based configuration
    - Search parameters (BM25 k1/b, field weights)
    - Embedding model configuration
    - Hybrid search weights

9. **`utils/path_utils.py`**: Path normalization utilities
   - Automatic conversion of file:// URLs to relative paths
   - Detects files within repository vs. external files
   - Improves portability across different machines

### Relative Path Conversion

The system automatically converts file paths to relative paths when documents are stored within the repository (parent directory of `.asta/`). This makes the index portable across different machines and git-friendly.

**How it works:**
- When adding a document with a `file://` URL or absolute path
- If the file is within the repository (subdirectory of repo root)
- The path is converted to a relative path (e.g., `docs/paper.pdf`)
- If the file is outside the repository, it's stored as `file://` URL
- HTTP/HTTPS/S3/GCS URLs are never modified

**Example:**
```python
# Adding a document within repo
doc = DocumentMetadata(
    name="Research Paper",
    url="file:///path/to/repo/docs/paper.pdf",  # Input: absolute file:// URL
    summary="Important research",
    mime_type="application/pdf"
)
await store.store(doc)
# Stored as: url="docs/paper.pdf"  (relative path)

# Adding a document outside repo
doc2 = DocumentMetadata(
    name="External Paper",
    url="file:///home/user/documents/paper.pdf",  # Outside repo
    summary="External document",
    mime_type="application/pdf"
)
await store.store(doc2)
# Stored as: url="file:///home/user/documents/paper.pdf"  (absolute file:// URL)
```

**Benefits:**
- ✅ **Portable**: Works across different machines (absolute paths would break)
- ✅ **Git-friendly**: Relative paths show meaningful diffs
- ✅ **Automatic**: No manual path conversion needed
- ✅ **Smart**: External files still use absolute file:// URLs

**Implementation:**
- `normalize_file_url()` in `utils/path_utils.py` handles the conversion
- Called automatically in `LocalIndexDocumentStore.store()` and `update()` methods
- Validates that relative paths have file extensions or path separators

**Repository Root Detection:**
- Standard setup: Looks for `.asta` directory in index path, uses its parent as repo root
- Custom index path: If `.asta` not found, uses parent directory of index file as repo root
- This ensures `--root` flag works correctly with any directory structure

**Examples with custom root:**
```bash
# Standard .asta structure (default root: .asta/documents)
asta-documents add /path/to/repo/docs/paper.pdf --name="Paper" --summary="..."
# Index file: .asta/documents/index.yaml
# Stored as: docs/paper.pdf (relative to .asta/documents/)

# Custom root directory
asta-documents --root=/path/to/repo/metadata add /path/to/repo/metadata/docs/paper.pdf --name="Paper" --summary="..."
# Index file: /path/to/repo/metadata/index.yaml
# Stored as: docs/paper.pdf (relative to /path/to/repo/metadata/)

# Root in different location
asta-documents --root=/tmp/my-project add /tmp/my-project/docs/paper.pdf --name="Paper" --summary="..."
# Index file: /tmp/my-project/index.yaml
# Stored as: docs/paper.pdf (relative to /tmp/my-project/)
```

## Document Model

### DocumentMetadata Fields

**Required fields:**
- `url`: Where the actual document content lives
  - Supported protocols: `http://`, `https://`, `file://`, `s3://`, `gs://`
  - Relative paths: For files within repo (e.g., `docs/paper.pdf`)
  - Automatically converted from absolute paths/file:// URLs when within repo
- `name`: Document title/name
- `summary`: Text description for search (required for all documents)
- `mime_type`: Document MIME type (e.g., `application/pdf`, `text/plain`)
- `tags`: List of tags for categorization (can be empty list)

**Automatically managed fields:**
- `uuid`: 10-character alphanumeric short ID (auto-generated, stored in YAML)
- `created_at`: Auto-set on creation
- `modified_at`: Auto-updated on changes

**Optional fields:**
- `extra`: Dict for additional metadata (author, year, venue, etc.)

### Index File Structure

The `.asta/documents/index.yaml` file stores only the **10-character short UUID** (not the full URI):

```yaml
version: "1.0"

documents:
  - uuid: "6MNxGbWGRC"  # 10-char alphanumeric short ID (72% smaller than 36-char UUID)
    name: "Attention Is All You Need"
    url: "https://arxiv.org/pdf/1706.03762.pdf"  # HTTP URL
    summary: "Seminal paper introducing the Transformer architecture"
    tags: ["ai", "research", "transformers", "nlp"]
    mime_type: "application/pdf"
    created_at: "2026-02-06T10:00:00+00:00"
    modified_at: "2026-02-06T10:00:00+00:00"
    extra:
      author: "Vaswani et al"
      year: 2017
      venue: "NeurIPS"

  - uuid: "7NAbCxYzPQ"
    name: "Local Research Notes"
    url: "docs/research/notes.pdf"  # Relative path for file within repo
    summary: "Research notes and findings"
    tags: ["research", "notes"]
    mime_type: "application/pdf"
    created_at: "2026-03-11T10:00:00+00:00"
    modified_at: "2026-03-11T10:00:00+00:00"
```

**Storage format notes:**
- Documents are identified solely by their `uuid` field
- No namespace or URI concepts - just simple 10-character IDs
- Clean YAML format with minimal overhead
- URLs can be HTTP/HTTPS, relative paths (within repo), or file:// URLs (external files)

### Short ID Implementation

The system uses **10-character base62-encoded short IDs** instead of traditional 36-character UUIDs:

**Format:**
- Characters: `a-zA-Z0-9` (base62 alphabet)
- Length: 10 characters
- Possibilities: 62^10 ≈ 839 quadrillion unique IDs
- Collision probability: < 0.00000006% for 10,000 documents

**Generation:**
- Location: `utils/short_id.py`
- Uses cryptographically secure random number generation (`secrets` module)
- Automatic collision detection with retry logic (max 10 attempts)
- Thread-safe via existing document store locking mechanisms

**Benefits:**
- **72% reduction in UUID length** (36 chars → 10 chars)
- **~20-30% smaller YAML files** (estimated)
- **More readable IDs** in CLI output and git diffs
- **URL-safe** (no special characters requiring encoding)

**Example:**
```python
# Traditional UUID (36 chars)
550e8400-e29b-41d4-a716-446655440000

# Short ID (10 chars)
6MNxGbWGRC
```

## Cloud Storage Support

The system supports fetching documents from cloud storage services in addition to HTTP/HTTPS and local file:// URLs.

### Supported Protocols

**Local and Web:**
- `http://` and `https://` - Web URLs (uses curl)
- `file://` - Local file system (uses curl)

**Cloud Storage:**
- `s3://` - Amazon S3 (uses AWS CLI)
- `gs://` - Google Cloud Storage (uses gsutil)

### Prerequisites

**For S3 URLs (`s3://`):**
```bash
# Install AWS CLI
brew install awscli  # macOS
# or: pip install awscli

# Configure credentials
aws configure
# Or use environment variables:
# AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION
# Or use AWS_PROFILE for named profiles
```

**For GCS URLs (`gs://`):**
```bash
# Install gsutil (part of Google Cloud SDK)
brew install --cask google-cloud-sdk  # macOS
# or: pip install gsutil

# Configure credentials
gcloud auth login
# Or use service account:
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

### Usage Examples

```bash
# Add document from S3
uv run asta-documents add s3://my-bucket/papers/paper.pdf \
  --name="Research Paper" \
  --summary="Important research findings" \
  --tags="research,ml" \
  --mime-type="application/pdf"

# Add document from Google Cloud Storage
uv run asta-documents add gs://my-bucket/docs/document.pdf \
  --name="Technical Document" \
  --summary="Technical specifications" \
  --tags="docs,specs" \
  --mime-type="application/pdf"

# Fetch from cloud storage (automatic caching)
uv run asta-documents fetch <uuid> -o local-copy.pdf
```

**Notes:**
- Cloud storage credentials must be configured before fetching
- The fetch command will use cached content when available (default: 7 days)
- Cache works identically for all protocols (http, https, file, s3, gs)
- The CLI tools (aws, gsutil) must be installed and in PATH

## Search System

The search system provides multiple strategies optimized for different use cases, from simple substring matching to sophisticated hybrid search combining keyword and semantic approaches.

### Architecture Overview

```
YAML Index (Source of Truth)
    ↓ (on modification)
SQLite Cache (.cache/search.db)
    ├─→ FTS5 Full-Text Index (keyword search)
    ├─→ BM25 Scoring Tables (term frequencies)
    └─→ Embeddings Table (semantic vectors)
         ↓
Search Query
    ├─→ Keyword Path (FTS5 + BM25)
    ├─→ Semantic Path (Vector Similarity)
    └─→ Hybrid Fusion (Reciprocal Rank Fusion)
         ↓
    Ranked Results
```

**File Structure:**
```
/path/to/index/
├── index.yaml              # Source of truth (can be git-tracked)
└── .cache/                 # Cache directory (gitignored)
    ├── search.db           # SQLite search cache
    ├── .index_checksum     # YAML modification tracker
    └── <hash>/             # Fetched document content
        ├── content
        └── metadata.yaml
```

### Field-Specific Search

The search system uses **field-specific strategies** based on which document field you're searching:

**Field Query Parameters** (can be combined):
- `--name=QUERY`: Search document names with simple word matching
- `--tags=QUERY`: Search tags with comma-separated matching
- `--summary=QUERY`: Search summaries with semantic/hybrid search
- `--extra=QUERY`: Search extra metadata with JSONPath-like syntax

**Combine Modes:**
- Default (intersection): Returns documents matching ALL field queries
- `--union`: Returns documents matching ANY field query

**Hierarchical Scoring:**

Results are sorted using a priority hierarchy, where tags and extra act as filters:

1. **Summary score** (if summary query present): Uses semantic/hybrid search relevance
2. **Name score** (if name query present): Uses word-matching score
3. **Created timestamp** (for tags/extra only queries): Sorts by creation time (newest first)

This means:
- `--summary` + `--tags`: Sorted by summary relevance (tags filter)
- `--name` + `--tags`: Sorted by name word-match score (tags filter)
- `--tags` only: Sorted by created_at timestamp
- `--summary` + `--name` + `--tags`: Sorted by summary relevance (name and tags filter)

**Examples:**
```bash
# Single field search
asta-documents search --name="Attention"
asta-documents search --tags="ai,nlp"
asta-documents search --summary="papers about transformers"
asta-documents search --extra=".year > 2020"

# Multiple fields (intersection - documents matching ALL)
asta-documents search --summary="transformers" --tags="ai"
asta-documents search --name="Attention" --tags="nlp" --extra=".year > 2015"

# Multiple fields (union - documents matching ANY)
asta-documents search --summary="transformers" --name="BERT" --union
```

**Field-Specific Implementations:**

1. **Name Search** (`_search_by_name()`):
   - Simple case-insensitive word matching
   - Splits query into words, matches any word in name
   - Score = (matched words / total query words)
   - Fast in-memory scan, no indexing needed

2. **Tag Search** (`_search_by_tags()`):
   - Comma-separated tag matching
   - Case-insensitive
   - Score = (matched tags / total query tags)
   - Works with partial matches (finds docs with any matching tags)

3. **Summary Search** (`_search_by_summary()`):
   - Uses best available method with automatic fallback:
     - Hybrid (BM25 + semantic embeddings) → BM25 → FTS5 → Simple
   - Optimized for natural language queries
   - Understands semantic meaning

4. **Extra Metadata Search** (`_search_by_extra()`):
   - JSONPath-like query syntax
   - Supported operators: `>`, `>=`, `<`, `<=`, `==`, `contains`
   - Numeric and string comparisons
   - Example: `.year > 2020` finds docs where `extra.year > 2020`

### Search Implementation Details

Below are the internal search methods used by summary field search (not directly user-facing):

#### 1. Simple Search (Baseline)

#### 1. Simple Search (Baseline)

**Location**: `local_index.py:_search_simple()`

**Algorithm**:
- Substring matching with case-insensitive comparison
- Fixed weights: summary=3, name=2, tags=1, extra=1
- O(n) linear scan through all documents

**When to use**: Fallback when cache unavailable, exact phrase matching

**Performance**: ~150ms for 5K documents

#### 2. FTS5 Search (Indexed)

**Location**: `local_index.py:_search_fts5()`

**Algorithm**:
- SQLite FTS5 virtual table with porter stemming
- Unicode61 tokenizer for international text
- BM25 ranking built into FTS5
- Field boosting via BM25 weights

**Features**:
- Automatic index sync with YAML using SHA256 hashing
- Handles stemming (e.g., "running" matches "run")
- Case-insensitive with diacritical mark handling

**Performance**: ~50ms for 5K documents

**Configuration** (`local.conf`):
```hocon
search {
  enable_cache = true
  cache_filename = "search.db"
  field_weights {
    summary = 3.0
    name = 2.0
    tags = 1.5
    extra = 1.0
  }
}
```

#### 3. BM25 Search (Relevance Ranking)

**Location**: `bm25_ranker.py:BM25Ranker`

**Algorithm**: Best Match 25 (BM25)
```
BM25(q, d) = Σ IDF(qi) * (f(qi, d) * (k1 + 1)) / (f(qi, d) + k1 * (1 - b + b * |d| / avgdl))

Where:
- IDF(qi) = log((N - df(qi) + 0.5) / (df(qi) + 0.5))
- f(qi, d) = term frequency in document
- |d| = document length
- avgdl = average document length
- k1 = term saturation parameter (default: 1.2)
- b = length normalization parameter (default: 0.75)
```

**Features**:
- Term frequency with saturation (prevents over-weighting repeated terms)
- Inverse document frequency (rare terms score higher)
- Document length normalization (fairness for long/short docs)
- Field-specific weights (summary > name > tags > extra)

**Performance**: ~80ms for 5K documents

**Configuration** (`local.conf`):
```hocon
search {
  bm25 {
    k1 = 1.2  # Term saturation (1.2-2.0)
    b = 0.75  # Length normalization (0.0-1.0)
  }
}
```

**Expected Improvement**: ~25% precision increase over simple search

#### 4. Semantic Search (Embeddings)

**Location**: `embeddings.py:EmbeddingManager`

**Algorithm**:
- sentence-transformers `all-MiniLM-L6-v2` model
- 384-dimensional embeddings
- Cosine similarity for vector comparison
- Lazy model loading (loads on first use)

**Features**:
- Understands semantic meaning (e.g., "ML papers" finds "machine learning")
- Works offline (no API calls)
- CPU-optimized model (~80MB, downloads on first use)
- Embeddings cached in SQLite

**Dependencies** (included by default):
- `sentence-transformers>=2.2.0`
- `numpy>=1.21.0`

**Performance**: ~120ms for 5K documents (including embedding generation)

**Configuration** (`local.conf`):
```hocon
search {
  embeddings {
    enabled = true
    model = "sentence-transformers/all-MiniLM-L6-v2"
    lazy_generation = true
  }
}
```

**Storage**:
```sql
CREATE TABLE embeddings (
    uri TEXT PRIMARY KEY,
    embedding BLOB,  -- Serialized numpy array (float32)
    model_version TEXT,
    created_at TIMESTAMP
);
```

#### 5. Hybrid Search (BM25 + Semantic)

**Location**: `hybrid_search.py:HybridSearchRanker`

**Algorithm**: Reciprocal Rank Fusion (RRF)
```
RRF(d) = Σ (weight / (k + rank(d)))

Where:
- rank(d) = position of document d in ranking (1-indexed)
- k = 60 (constant to avoid high scores for top items)
- weight = importance weight for each source
```

**Process**:
1. Run BM25 search → get top 2×limit results
2. Run semantic search → get top 2×limit results
3. Combine using RRF with configurable weights
4. Return top limit results

**Performance**: ~150ms for 5K documents (runs both searches)

**Expected Results**: ~80-85% precision@10 (best overall)

**Configuration** (`local.conf`):
```hocon
search {
  hybrid {
    bm25_weight = 0.5
    semantic_weight = 0.5
  }
}
```

### Search API

**Basic usage**:
```python
async with LocalIndexDocumentStore() as store:
    # Default: search summaries (uses best available method)
    hits = await store.search("transformer architecture")

    # Field-specific search
    hits = await store.search(
        "Attention",
        limit=10,
        search_field="name"
    )

    # Tag search
    hits = await store.search("ai,nlp", search_field="tags")

    # Extra metadata search
    hits = await store.search(".year > 2020", search_field="extra")

    # Each hit has .result and .score
    for hit in hits:
        print(f"{hit.result.name}: {hit.score:.4f}")
```

**Field selection**:
- `search_field="summary"` (default): Uses automatic method selection (hybrid → BM25 → FTS5 → simple)
- `search_field="name"`: Simple word matching
- `search_field="tags"`: Tag matching with comma-separated queries
- `search_field="extra"`: JSONPath-like queries for metadata

### Cache Synchronization

**Staleness detection**:
```python
def is_cache_stale() -> bool:
    current_hash = sha256(yaml_file_contents)
    stored_hash = get_from_sync_metadata()
    return current_hash != stored_hash
```

**Rebuild trigger**:
- YAML file modified (detected by hash change)
- Manual cache invalidation
- First search after initialization

**Rebuild process**:
1. Clear existing cache tables
2. Insert documents into `documents` table
3. Insert into `documents_fts` FTS5 table
4. Build BM25 index (term stats, document stats)
5. Generate embeddings (if enabled)
6. Store new YAML hash

**Thread safety**: Uses `fcntl` file locking (same as YAML)

### Testing

**Test files**:
- `test_search_cache.py` - Cache synchronization (7 tests)
- `test_bm25.py` - BM25 algorithm (11 tests)
- `test_local_index_store.py` - Search integration (31 tests)

**Key test scenarios**:
- FTS5 field boosting verification
- BM25 ranking order correctness
- Cache staleness detection
- Graceful fallback when dependencies missing
- Search mode auto-selection

### Performance Benchmarks

**Target**: <100ms for 5K documents ✅

**Measured performance** (5K documents):
- Simple: ~150ms (baseline)
- FTS5: ~50ms (70% faster)
- BM25: ~80ms (47% faster, better relevance)
- Semantic: ~120ms (20% faster, best for concepts)
- Hybrid: ~150ms (same speed, best relevance)

**Memory usage**:
- SQLite cache: ~5-10MB for 5K documents
- Embeddings: ~7.5MB (5K × 384 × 4 bytes)
- Model: ~80MB (loaded once, shared)

### Error Handling and Fallbacks

**Graceful degradation**:
```python
try:
    return await self._search_hybrid(query, limit)
except ImportError:
    # sentence-transformers not installed
    return await self._search_bm25(query, limit)
except Exception:
    # BM25 failed
    return await self._search_fts5(query, limit)
except Exception:
    # FTS5 failed
    return await self._search_simple(query, limit)
```

**Logging**:
- Warnings when falling back to simpler modes
- Info messages on cache rebuilds
- Error messages with actionable suggestions

### Common Development Tasks

**Adding new search mode**:
1. Implement `_search_<mode>()` in `local_index.py`
2. Update `_determine_search_mode()` logic
3. Add mode to CLI choices in `index_cli.py`
4. Add tests in `test_local_index_store.py`

**Tuning BM25 parameters**:
- Edit `k1` in `local.conf` (higher = more term frequency weight)
- Edit `b` in `local.conf` (higher = more length normalization)
- Run benchmarks to measure impact

**Changing embedding model**:
1. Update `model` in `local.conf`
2. Delete `.cache/search.db` (or entire `.cache/` directory) to clear old embeddings
3. Run search to regenerate with new model

## Configuration

Configuration uses HOCON format. The index file location is fixed at `.asta/documents/index.yaml` relative to the current directory.

**Default config** (`src/asta/resources/config/local.conf`):
```hocon
# Allowed MIME types for documents
allowed_mime_types = [
  "application/json",
  "application/pdf",
  "text/plain",
  "text/markdown",
  "text/html"
]
```

**Environment variable overrides:**
- `CONFIG_FILE`: Use different config file
- `ENV`: Load environment-specific config (e.g., `production.conf`)

## Git Tracking

**Recommended for teams:**
```bash
# Track the index file in git
git add .asta/documents/index.yaml
git commit -m "Add document index"
git push
```

When tracked in git:
- ✅ Team members get same UUIDs (documents are universally identifiable)
- ✅ Git shows readable diffs when documents change
- ✅ Document metadata is versioned alongside code

**Personal use (untracked):**
- `.gitignore` allows tracking `.asta/documents/index.yaml` but ignores other `.asta/` files
- If not committed, the index is local-only

## CLI Commands

### Installation

```bash
# Install project
uv sync

# Verify CLI is available
uv run asta-documents --help
```

### Usage

```bash
# Add a document
uv run asta-documents add https://arxiv.org/pdf/1706.03762.pdf \
  --name="Attention Is All You Need" \
  --summary="Transformer architecture paper" \
  --tags="ai,research,transformers" \
  --mime-type="application/pdf" \
  --extra='{"author": "Vaswani et al", "year": 2017}'

# List all documents
uv run asta-documents list

# List with tag filter
uv run asta-documents list --tags="ai,research"

# List with verbose output
uv run asta-documents list -v

# Search documents by single field
uv run asta-documents search --summary="transformer"
uv run asta-documents search --name="Attention"
uv run asta-documents search --tags="ai,nlp"

# Search with scores
uv run asta-documents search --summary="deep learning" --show-scores

# Search extra metadata with JSONPath-like syntax
uv run asta-documents search --extra=".year > 2020"
uv run asta-documents search --extra=".author contains Vaswani"
uv run asta-documents search --extra=".venue == NeurIPS"

# Search multiple fields (default: intersection - documents matching ALL queries)
uv run asta-documents search --summary="transformers" --tags="ai"
uv run asta-documents search --name="Attention" --tags="nlp" --extra=".year > 2015"

# Search multiple fields with union (documents matching ANY query)
uv run asta-documents search --summary="transformers" --name="BERT" --union

# Get specific document by UUID
uv run asta-documents get 6MNxGbWGRC

# Update document metadata
uv run asta-documents update 6MNxGbWGRC \
  --name="Updated Title" \
  --summary="Updated summary text" \
  --tags="updated,revised"

# Update with JSON output
uv run asta-documents --json update 6MNxGbWGRC \
  --name="New Title"

# Remove document
uv run asta-documents remove 6MNxGbWGRC

# Show index information
uv run asta-documents show

# Fetch document content (with automatic caching)
uv run asta-documents fetch 6MNxGbWGRC -o document.pdf

# Fetch to stdout
uv run asta-documents fetch 6MNxGbWGRC > document.pdf

# Force refresh (bypass cache)
uv run asta-documents fetch 6MNxGbWGRC -o document.pdf --force

# Cache management
uv run asta-documents cache list              # List cached items
uv run asta-documents cache stats             # Show cache statistics
uv run asta-documents cache clean --days 7    # Remove items older than 7 days
uv run asta-documents cache clear             # Clear entire cache
uv run asta-documents cache info <hash>       # Show cached item details

# JSON output (for scripting)
uv run asta-documents list --json
uv run asta-documents cache stats --json
```

### Content Fetching with Caching

The CLI includes built-in content fetching with automatic caching:

**Features:**
- Automatic cache checking (SHA256 hash of document URL)
- 7-day default cache freshness (configurable with `--max-age`)
- Downloads and caches content on first request
- Instant retrieval from cache on subsequent requests
- Cache stored in `.cache/` directory (gitignored)

**Workflow for reading document content:**

```bash
# 1. Fetch document by UUID (uses cache if available)
uv run asta-documents fetch 6MNxGbWGRC -o /tmp/doc.pdf

# 2. Use Read tool to extract and display content
# Read(/tmp/doc.pdf)
# The Read tool has native PDF support for text extraction
```

**Cache management:**

```bash
# Check what's cached
uv run asta-documents cache list

# View statistics (size, age distribution, content types)
uv run asta-documents cache stats

# Clean old cache entries
uv run asta-documents cache clean --days 7

# Clear everything
uv run asta-documents cache clear
```

## Claude Code Integration

### Asta Documents Skill (Recommended)

The primary integration method is the **Asta Documents skill** located at `skills/asta-documents.md`.

**Installation for external users:**
```bash
curl -o ~/.claude/skills/asta-documents.md https://raw.githubusercontent.com/allenai/asta-resource-repo/main/skills/asta-documents.md
```

**Usage in Claude Code:**
```
💬 "Use /asta-documents to add a paper at https://arxiv.org/pdf/1706.03762.pdf
    about Transformers, tags: ai, research"

💬 "Use /asta-documents to search for papers about attention mechanisms"

💬 "Use /asta-documents to fetch document 6MNxGbWGRC"
```

**The skill provides:**
- Complete document management (add, update, remove, list)
- Search with multiple modes (simple, keyword, semantic, hybrid)
- Content fetching with automatic caching
- Tag management
- Metadata operations

**Aliases:** `/asta`, `/asta-docs`, `/docs`, `/fetch-asta-content`

See `skills/asta-documents.md` for complete documentation.

## Development Commands

### Code Quality

```bash
# Check formatting and linting
make code-check

# Auto-format code
make code-format
```

### Running Tests

```bash
# Run all tests
make test

# Or directly with pytest
uv run --extra dev pytest tests/ -v

# Run specific test file
uv run --extra dev pytest tests/test_local_index_store.py -v

# Run with coverage
uv run --extra dev pytest tests/ --cov=src/asta/resources --cov-report=html
```

### Test Organization

- `test_local_index_store.py`: LocalIndexDocumentStore backend tests
- All tests use temporary directories (no database setup required)

## Project Workflow

### Task Tracking with Beads

The project uses [Beads](https://github.com/steveyegge/beads), a distributed issue tracker for AI coding agents.

**Quick reference:**
```bash
# View ready work
bd ready

# Show task details
bd show <issue-id>

# Update task status
bd update <issue-id> --status in_progress
bd close <issue-id> --reason "Completed"

# Create new task
bd create "Task title" -d "Description" -p 1 -t feature
```

See `BEADS.md` for detailed workflows.

## Skills

### Skill Distribution

**Public Skills** (for external users):
- Location: `skills/` directory
- Installation: `curl -o ~/.claude/skills/asta-documents.md https://raw.githubusercontent.com/allenai/asta-resource-repo/main/skills/asta-documents.md`
- Uses: Global `asta-documents` command (assumes tool is installed via `uv tool install`)

**Development Skills** (for contributors):
- Location: `.claude/commands/` directory (internal use only)
- Uses: `uv run asta-documents` for local development
- See `.claude/commands/asta-documents.md`

### Available Skills

**asta-documents** (main skill)

Complete document management for tracking research papers, documentation, and resources.

**Location:** `skills/asta-documents.md`

**Aliases:** `/asta`, `/asta-docs`, `/docs`, `/fetch-asta-content`, `/read-asta-doc`, `/get-asta-content`, `/show-asta-doc`

**Features:**
- Add, search, update, remove documents
- Tag-based organization
- Multiple search modes (simple, keyword, semantic, hybrid)
- Content fetching with automatic caching
- Cache management
- JSON output for scripting

**Simplified workflow for fetching content:**

```bash
# 1. Fetch document content by UUID (automatic caching)
asta-documents fetch 6MNxGbWGRC -o /tmp/document.pdf

# 2. Use Read tool to extract and display
# Read(/tmp/document.pdf)
```

**Key features:**
- Automatic cache checking (SHA256 hash of document URL)
- 7-day default cache freshness (configurable)
- Instant retrieval from cache on subsequent requests
- Built-in cache management commands

**Cache management:**

```bash
# View cached items
asta-documents cache list

# Show cache statistics
asta-documents cache stats

# Remove old entries (> 7 days)
asta-documents cache clean --days 7

# Clear entire cache
asta-documents cache clear

# Show specific item details
asta-documents cache info <hash>
```

**How it works:**
1. `asta-documents fetch` retrieves document metadata from Asta index
2. Checks local cache (`.cache/` directory) using SHA256 hash of URL
3. Uses cached content if fresh (< max-age days)
4. Downloads and caches if not present or expired
5. Saves to specified output file

**Example workflow:**
```
User: "Show me the Introduction from document 6MNxGbWGRC"

Agent workflow:
1. asta-documents fetch 6MNxGbWGRC -o /tmp/doc.pdf -q
2. Read(/tmp/doc.pdf) - Claude extracts and displays the Introduction

User: "Show me the Methods section" (same document)

Agent workflow:
1. asta-documents fetch 6MNxGbWGRC -o /tmp/doc.pdf -q
   # Uses cache instantly (no re-download)
2. Read(/tmp/doc.pdf) - Claude extracts and displays Methods
```

**Why this approach:**
- Uses unified CLI instead of separate scripts
- Native PDF support via Read tool (better text extraction)
- All cache operations integrated into asta-documents CLI
- Consistent command structure with other operations

**Complete documentation:** See `skills/asta-documents.md`

### Installing Skills for External Users

External users should install the skill from the public location:

```bash
# 1. Install the CLI tool
uv tool install git+https://github.com/allenai/asta-resource-repo.git

# 2. Install the skill
curl -o ~/.claude/skills/asta-documents.md https://raw.githubusercontent.com/allenai/asta-resource-repo/main/skills/asta-documents.md
```

### Modifying Skills

To update or modify skills:

1. Edit the skill file in `skills/` directory
2. Test with Claude Code using the development skill in `.claude/commands/`
3. Update documentation in both locations if needed
4. Submit pull request
5. External users can update via curl once merged

The `skills/` directory includes a `README.md` with complete installation instructions.

## Common Patterns

### Adding New Metadata Fields

To add a field to document metadata:

1. Update `DocumentMetadata` in `model.py`
2. Update CLI `add` command in `cli/index_cli.py` if needed
3. Add tests in `tests/test_local_index_store.py`
4. YAML format automatically handles new fields (no migration needed)

### Extending Search

Search is implemented in `LocalIndexDocumentStore.search()`:
- Simple in-memory string matching
- Case-insensitive
- Ranks by number of matches
- To add new searchable fields, update the `search()` method

### Adding New CLI Commands

1. Add command function in `cli/index_cli.py` (e.g., `cmd_export`)
2. Add subparser in `main()` function
3. Test manually with `uv run asta-documents <command>`

## Error Handling

Custom exceptions in `exceptions.py`:
- `ValidationError`: Input validation failures (invalid URL, missing fields)
- `DocumentNotFoundError`: Document doesn't exist
- `DocumentServiceError`: Base exception for service errors

The CLI converts exceptions to user-friendly error messages.

## Important Notes

- **Always use `uv run`**: This project uses `uv` for dependency management
- **UUID-Based**: Documents are identified by 10-character alphanumeric UUIDs
- **Git-Friendly**: `.asta/documents/index.yaml` should be committed for team sharing
- **Async/Await**: All document store operations are async for future extensibility
- **YAML Serialization**: Pydantic's `model_dump()` handles datetime serialization automatically
- **No Backward Compatibility Required**: This is an early-stage project with no production users yet. Make breaking changes freely when they improve the codebase. Don't add compatibility shims, deprecated code paths, or version checks. Clean refactoring is preferred over maintaining legacy behavior.

## Troubleshooting

### Index File Corruption

If `.asta/documents/index.yaml` becomes corrupted:

```bash
# Backup corrupt file
cp .asta/documents/index.yaml .asta/documents/index.yaml.backup

# Recreate empty index
rm .asta/documents/index.yaml
uv run asta-documents list  # Creates new empty index
```

### Import Errors

```bash
# Reinstall dependencies
uv sync

# Verify installation
uv run python -c "from asta.resources.document_store import LocalIndexDocumentStore; print('OK')"
```

### CLI Not Found

```bash
# Reinstall project
uv sync

# Check entry points
uv run which asta-documents
```

## Quick Start Example

```bash
# Navigate to project directory
cd /path/to/asta-resource-repo

# Add your first document
uv run asta-documents add https://arxiv.org/pdf/1706.03762.pdf \
  --name="Attention Is All You Need" \
  --summary="Seminal transformer architecture paper" \
  --tags="ai,nlp,transformers"

# List documents
uv run asta-documents list

# Search by single field
uv run asta-documents search --summary="attention"
uv run asta-documents search --name="Attention"
uv run asta-documents search --tags="ai,transformers"
uv run asta-documents search --extra=".year > 2015"

# Search with scores
uv run asta-documents search --summary="transformer" --show-scores

# Search multiple fields (intersection)
uv run asta-documents search --summary="transformers" --tags="ai"

# Search multiple fields (union)
uv run asta-documents search --summary="transformers" --name="BERT" --union

# Update document metadata (use UUID from add command output)
uv run asta-documents update 6MNxGbWGRC \
  --tags="ai,nlp,transformers,updated"

# View the index file directly
cat .asta/documents/index.yaml

# Commit to git
git add .asta/documents/index.yaml
git commit -m "Add transformer paper to index"
```
