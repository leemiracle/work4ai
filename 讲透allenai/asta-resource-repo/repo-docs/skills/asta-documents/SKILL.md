---
name: asta-documents
description: Local document metadata index for scientific documents
---

# Asta Documents Management

Use this skill when the user asks to store a document "in Asta" or retrieve "from Asta". Use it when the
user references an "Asta document" or anything with an `asta://` URI.

This skill provides complete document management functionality for tracking research papers, documentation, and resources using the `asta-documents` CLI.

**What it does:** Track document metadata (URLs, summaries, tags) in a local index. Think of it as a smart bookmark manager with powerful search capabilities.

## Installation

### 1. Install the CLI Tool

```bash
# Install globally using uv
uv tool install git+https://github.com/allenai/asta-resource-repo.git
```

**Prerequisites:** Python 3.10+ and [uv package manager](https://docs.astral.sh/uv/)

Verify installation with `asta-documents --help`

## Quick Command Reference

Add `--json` flag to any command for machine-readable output.

```bash
# List documents
asta-documents list
asta-documents list --tags="ai,research"

# Search documents (by field)
asta-documents search --summary="query"
asta-documents search --name="title words"
asta-documents search --tags="ai,nlp"
asta-documents search --extra=".year > 2020"

# Multi-field search (intersection - matches ALL)
asta-documents search --summary="transformers" --tags="ai"

# Multi-field search (union - matches ANY)
asta-documents search --summary="transformers" --name="BERT" --union

# Add document
asta-documents add <url> --name="Title" --summary="Description" --tags="tag1,tag2" --extra='{"author": "Smith et al", "year": 2024, "venue": "NeurIPS"}'

# Get document metadata
asta-documents get <uuid>

# Update document
asta-documents update <uuid> --name="New Title" --tags="new,tags"

# Fetch document content
asta-documents fetch <uuid> -o /tmp/document.pdf

# Manage tags
asta-documents add-tags <uuid> --tags="new,tags"
asta-documents remove-tags <uuid> --tags="old,tags"

# Cache management
asta-documents cache list
asta-documents cache stats
asta-documents cache clean --days 7

# Summary information (document counts)
asta-documents show
```
Always use the command line interface for all operations to ensure proper index management and caching.
Avoid direct read/write operations on the index file.

## Working with Remote Indexes (asta:// URLs)

Asta documents can reference remote indexes using the `asta://` URL scheme. This allows sharing document collections hosted on the web.

**URL Format:**
```
asta://{url-encoded-index-url}/{uuid}
```

Where:
- `{url-encoded-index-url}` is the URL-encoded URL to the remote `index.yaml` file
- `{uuid}` is the 10-character document identifier

**Example:**
```
# Actual index URL: https://example.com/research/index.yaml
# Asta URL: asta://https%3A%2F%2Fexample.com%2Fresearch%2Findex.yaml/6MNxGbWGRC
```

**Workflow:**

When you encounter an `asta://` URL, follow these steps:

1. **Parse the URL** to extract the encoded index URL and document UUID
2. **URL-decode** the index URL
3. **Download the remote index** to a local temporary file
4. **Access documents** using the `--root` parameter

**Example:**

```bash
# Given an asta:// URL
ASTA_URL="asta://https%3A%2F%2Fexample.com%2Fresearch%2Findex.yaml/6MNxGbWGRC"

# 1. Parse the URL components (extract encoded index URL and UUID)
ENCODED_INDEX_URL=$(echo "$ASTA_URL" | sed 's|^asta://||' | sed 's|/[^/]*$||')
UUID=$(echo "$ASTA_URL" | sed 's|.*/||')

# 2. URL-decode the index URL
INDEX_URL=$(python3 -c "import urllib.parse; print(urllib.parse.unquote('$ENCODED_INDEX_URL'))")

# 3. Download the remote index
mkdir -p /tmp/asta-remote
curl -s -o /tmp/asta-remote/index.yaml "$INDEX_URL"

# 4. Get document metadata using --root
asta-documents get "$UUID" --root /tmp/asta-remote

# 5. Fetch document content
asta-documents fetch "$UUID" --root /tmp/asta-remote -o /tmp/document.pdf
```

**Common Operations with Remote Indexes:**

```bash
# After downloading and decoding the index URL (see examples above)
# Assume TEMP_INDEX points to the downloaded index file

# Search remote index
asta-documents search --summary="query" --root "$TEMP_ROOT"

# List all documents in remote index
asta-documents list --root "$TEMP_ROOT"

# Get metadata for specific document
asta-documents get "$UUID" --root "$TEMP_ROOT"

# Search and fetch from remote index
asta-documents search --summary="transformers" --root "$TEMP_ROOT" --show-scores
asta-documents fetch "$UUID" --root "$TEMP_ROOT" -o result.pdf
```

**Important Notes:**

- The `--root` parameter works with all read commands (list, search, get, fetch)
- The root directory must contain an `index.yaml` file
- Remote indexes accessed this way are read-only (no add/update/remove operations)
- Downloaded indexes can be cached locally to avoid repeated downloads
- The index URL portion is URL-encoded and must be decoded before use
- The decoded URL supports: http://, https://, file://, s3://, gs://
- Always validate the index file exists and is valid YAML before using it

**Complete Example Workflow:**

```bash
# User provides: asta://https%3A%2F%2Fai.example.org%2Fpapers%2Findex.yaml/AbC123XyZ9

# Step 1: Extract components
ASTA_URL="asta://https%3A%2F%2Fai.example.org%2Fpapers%2Findex.yaml/AbC123XyZ9"
ENCODED_INDEX_URL=$(echo "$ASTA_URL" | sed 's|^asta://||' | sed 's|/[^/]*$||')
UUID=$(echo "$ASTA_URL" | sed 's|.*/||')

# Step 2: URL-decode the index URL
INDEX_URL=$(python3 -c "import urllib.parse; print(urllib.parse.unquote('$ENCODED_INDEX_URL'))")
# Result: https://ai.example.org/papers/index.yaml

# Step 3: Download index to temp location
TEMP_ROOT="/tmp/asta-remote-$(date +%s)"
mkdir -p "$TEMP_ROOT"
curl -s -o "$TEMP_ROOT/index.yaml" "$INDEX_URL"

# Step 4: Verify download succeeded
if [ ! -f "$TEMP_ROOT/index.yaml" ]; then
    echo "Failed to download index from $INDEX_URL"
    exit 1
fi

# Step 5: Access the document
asta-documents get "$UUID" --root "$TEMP_ROOT"
asta-documents fetch "$UUID" --root "$TEMP_ROOT" -o /tmp/paper.pdf

# Step 6: Read the content
# Read(/tmp/paper.pdf)
```

## Fetch Document Content

The index stores metadata only. The content of a document is retrievable via its URL. The `fetch` command retrieves the content and caches it locally for future use.

**Fetch to file (with automatic caching):**
```bash
asta-documents fetch <uuid> -o /tmp/document.pdf
```

### Supported URL Protocols

The system supports multiple protocols for document URLs:

**Local and Web:**
- `http://` and `https://` - Web URLs (uses curl)
- `file://` - Local file system (uses curl)

**Cloud Storage:**
- `s3://` - Amazon S3 (requires AWS CLI)
- `gs://` - Google Cloud Storage (requires gsutil)

**Cloud Storage Setup:**

For S3:
```bash
# Install AWS CLI
brew install awscli  # macOS
pip install awscli   # or via pip

# Configure credentials
aws configure
# Or use: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_PROFILE
```

For GCS:
```bash
# Install Google Cloud SDK
brew install --cask google-cloud-sdk  # macOS

# Authenticate
gcloud auth login
# Or use: GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

**Examples:**
```bash
# Add document from S3
asta-documents add s3://my-bucket/papers/research.pdf \
  --name="Research Paper" \
  --summary="ML research findings" \
  --tags="ml,research"

# Add document from GCS
asta-documents add gs://my-bucket/docs/spec.pdf \
  --name="Technical Spec" \
  --summary="System specifications" \
  --tags="docs"

# Fetch works the same for all protocols
asta-documents fetch <uuid> -o local-copy.pdf
```

### Cache Management

**List cached items:**
```bash
asta-documents cache list
```

**Show cache statistics:**
```bash
asta-documents cache stats
```

**Clean old cache entries:**
```bash
# Remove items older than N days
asta-documents cache clean --days 14
```

**Clear entire cache:**
```bash
asta-documents cache clear
asta-documents cache clear -y  # Skip confirmation
```

**Show specific item details:**
```bash
asta-documents cache info <hash>
```

## Common Workflows

### Workflow 1: Add and Organize Papers

```bash
# Add research paper
asta-documents add https://arxiv.org/pdf/1706.03762.pdf \
  --name="Attention Is All You Need" \
  --summary="Seminal paper introducing Transformer architecture" \
  --tags="ai,research,nlp,transformers" \
  --mime-type="application/pdf" \
  --extra='{"author": "Vaswani et al", "year": 2017, "venue": "NeurIPS"}'

# Search papers by tag
asta-documents search --tags="transformers"
```

### Workflow 2: Search and Fetch

```bash
# Search for relevant documents
asta-documents search --summary="transformer architecture" --show-scores

# Get metadata for top result (using UUID from search results)
asta-documents get 6MNxGbWGRC

# Fetch content
asta-documents fetch 6MNxGbWGRC -o /tmp/paper.pdf -q

# Read with PDF support
# Read(/tmp/paper.pdf)
```

### Workflow 3: Search with JSON Processing

```bash
# Search and extract UUIDs
RESULTS=$(asta-documents search --summary="query" --json)

# Get first UUID (example with Python)
UUID=$(echo "$RESULTS" | python3 -c "import sys,json; results=json.load(sys.stdin); print(results[0]['result']['uuid'] if results else '')")

# Fetch that document
asta-documents fetch "$UUID" -o result.pdf
```

### Workflow 4: Bulk Tag Management

```bash
# List documents with old tag
DOCS=$(asta-documents list --tags="old-tag" --json)

# For each, remove old tag and add new
for uuid in $(echo "$DOCS" | python3 -c "import sys,json; print('\\n'.join([d['uuid'] for d in json.load(sys.stdin)]))"); do
    asta-documents remove-tags "$uuid" --tags="old-tag"
    asta-documents add-tags "$uuid" --tags="new-tag"
done
```

### Workflow 5: Update Multiple Fields

```bash
# Get current metadata (using UUID)
asta-documents get 6MNxGbWGRC

# Update multiple fields
asta-documents update 6MNxGbWGRC \
  --name="Updated Title" \
  --summary="Updated summary with more details" \
  --tags="updated,revised,2025"
```

### Workflow 6: Cache Maintenance

```bash
# Check cache usage
asta-documents cache stats

# List what's cached
asta-documents cache list

# Remove old entries if cache is large
asta-documents cache clean --days 7

# Verify cache reduction
asta-documents cache stats
```

## Field-Specific Search

Asta uses different search strategies optimized for each document field. You can search single fields or combine multiple fields with intersection/union modes.

### Single Field Search

**--summary** (Summary search):
- Uses best available method automatically:
  - Hybrid (BM25 + semantic embeddings) → best quality
  - BM25 (keyword relevance ranking) → fast indexed
  - FTS5 (full-text search) → fallback
  - Simple (substring matching) → always available
- Optimized for natural language queries
- Understands semantic meaning
- Produces relevance scores for ranking
- Example: `asta-documents search --summary="papers about transformers"`

**--name** (Name search):
- Simple case-insensitive word matching
- Splits query into words, matches any word in name
- Score = (matched words / total query words)
- Fast, no indexing needed
- Produces match scores for ranking
- Example: `asta-documents search --name="Attention"`

**--tags** (Tag search):
- Comma-separated tag matching
- Case-insensitive
- Acts as a filter (no meaningful relevance scores)
- Finds documents with any matching tags
- Example: `asta-documents search --tags="ai,nlp"`

**--extra** (Extra metadata search):
- JSONPath-like query syntax
- Supported operators: `>`, `>=`, `<`, `<=`, `==`, `contains`
- Numeric and string comparisons
- Acts as a filter (no meaningful relevance scores)
- Examples:
  - `asta-documents search --extra=".year > 2020"`
  - `asta-documents search --extra=".author contains Smith"`
  - `asta-documents search --extra=".venue == NeurIPS"`

### Multi-Field Search

Combine multiple field queries to create powerful filtered searches:

**Intersection mode (default)**:
- Returns documents matching ALL specified field queries
- Example: `asta-documents search --summary="transformers" --tags="ai"`
- Only returns documents where summary contains "transformers" AND tags include "ai"

**Union mode (`--union` flag)**:
- Returns documents matching ANY specified field query
- Example: `asta-documents search --summary="transformers" --name="BERT" --union`
- Returns documents where summary contains "transformers" OR name contains "BERT"

**Hierarchical Scoring**:

Results are sorted using a priority hierarchy where tags/extra act as filters:

1. **Summary score** (highest priority) - if `--summary` present
   - Uses semantic/hybrid search relevance
   - Best for natural language queries

2. **Name score** (medium priority) - if `--name` present
   - Uses word-matching score
   - Used when no summary query

3. **Created timestamp** (lowest priority) - if only `--tags` or `--extra`
   - Sorts by creation time (newest first)
   - Only used when no summary/name queries

**Examples**:
```bash
# Summary + tags: Sorted by summary relevance (tags filter)
asta-documents search --summary="machine learning" --tags="ai"

# Name + tags: Sorted by name word-match (tags filter)
asta-documents search --name="Python" --tags="programming"

# Tags only: Sorted by creation timestamp
asta-documents search --tags="research"

# Three fields: Summary ranks, name and extra filter
asta-documents search --summary="transformers" --name="Attention" --extra=".year > 2015"
```

## Output Formats

**Human-readable (default):**
- Formatted tables and lists
- Color-coded (if terminal supports)
- Progress messages

**JSON (`--json` flag):**
- Machine-readable
- All fields included
- For scripting and integration

**Verbose (`-v` flag for list):**
- Shows all metadata fields
- Includes extra metadata
- Full URIs and timestamps

## Best Practices

1. **Use descriptive summaries**: They're indexed for search
2. **Tag consistently**: Establish a tagging scheme
3. **Use extra metadata**: Store author, year, venue for papers
4. **Let fetch handle caching**: Don't manually check cache
5. **Use JSON for scripting**: More reliable than parsing text
6. **Use quiet mode in scripts**: `-q` suppresses progress messages

## Troubleshooting

**"asta-documents: command not found"**
- Verify installation: `uv tool list | grep asta`
- Add to PATH: `export PATH="$HOME/.local/bin:$PATH"`
- Reinstall: `uv tool install --reinstall git+https://github.com/allenai/asta-resource-repo.git`

**"Document not found"**
- Verify URI: `asta-documents list --json | grep <partial-uri>`
- Check namespace: URIs are namespace-specific
- Ensure there is an index file at `.asta/documents/index.yaml`

**"Fetch failed"**
- Check URL is accessible: `curl -I <url>`
- Try force refresh: `--force`
- Check network connection

**"Search returns no results"**
- Try simpler query terms
- Search by name or tags for exact matching:
  - `asta-documents search --name="keyword"`
  - `asta-documents search --tags="tag"`
- Check if documents exist: `asta-documents list`
- Try union mode if using multiple fields: `--union`

**"Cache is large"**
- Check size: `asta-documents cache stats`
- Clean old entries: `asta-documents cache clean --days 7`
- Clear if needed: `asta-documents cache clear -y`

## Updating

**Update the CLI tool:**
```bash
uv tool install --reinstall git+https://github.com/allenai/asta-resource-repo.git
```

**Update the skill:**
```bash
curl -o ~/.claude/skills/asta-documents.md https://raw.githubusercontent.com/allenai/asta-resource-repo/main/skills/asta-documents.md
```

## Links

- **Repository**: https://github.com/allenai/asta-resource-repo
- **Documentation**: https://github.com/allenai/asta-resource-repo/blob/main/README.md
- **Issues**: https://github.com/allenai/asta-resource-repo/issues
