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

# Search document summaries
asta-documents search "query"

# Search by specific field
asta-documents search "title words" --name
asta-documents search "ai,nlp" --tags
asta-documents search ".year > 2020" --extra

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

## Fetch Document Content

The index stores metadata only. The content of a document is retrievable via its URL. The `fetch` command retrieves the content and caches it locally for future use.

**Fetch to file (with automatic caching):**
```bash
asta-documents fetch <uuid> -o /tmp/document.pdf
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
asta-documents search "transformers" --tags
```

### Workflow 2: Search and Fetch

```bash
# Search for relevant documents
asta-documents search "transformer architecture" --show-scores

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
RESULTS=$(asta-documents search "query" --json)

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

Asta uses different search strategies optimized for each document field:

**--name** (Name search):
- Simple case-insensitive word matching
- Splits query into words, matches any word in name
- Score = (matched words / total query words)
- Fast, no indexing needed
- Example: `asta-documents search "Attention" --name`

**--tags** (Tag search):
- Comma-separated tag matching
- Case-insensitive
- Score = (matched tags / total query tags)
- Finds documents with any matching tags
- Example: `asta-documents search "ai,nlp" --tags`

**--summary** (Summary search, default):
- Uses best available method automatically:
  - Hybrid (BM25 + semantic embeddings) → best quality
  - BM25 (keyword relevance ranking) → fast indexed
  - FTS5 (full-text search) → fallback
  - Simple (substring matching) → always available
- Optimized for natural language queries
- Understands semantic meaning
- Example: `asta-documents search "papers about transformers"`

**--extra** (Extra metadata search):
- JSONPath-like query syntax
- Supported operators: `>`, `>=`, `<`, `<=`, `==`, `contains`
- Numeric and string comparisons
- Examples:
  - `asta-documents search ".year > 2020" --extra`
  - `asta-documents search ".author contains Smith" --extra`
  - `asta-documents search ".venue == NeurIPS" --extra`

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
  - `asta-documents search "keyword" --name`
  - `asta-documents search "tag" --tags`
- Check if documents exist: `asta-documents list`

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
