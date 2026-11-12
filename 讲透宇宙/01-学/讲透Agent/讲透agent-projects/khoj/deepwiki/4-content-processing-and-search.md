<!-- source: DeepWiki mcp.deepwiki.com · repo khoj-ai/khoj · page 4 Content Processing and Search · fetched 2026-10-29 -->

# Content Processing and Search

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/khoj/processor/content/markdown/markdown_to_entries.py](src/khoj/processor/content/markdown/markdown_to_entries.py)
- [src/khoj/processor/content/org_mode/org_to_entries.py](src/khoj/processor/content/org_mode/org_to_entries.py)
- [src/khoj/processor/content/org_mode/orgnode.py](src/khoj/processor/content/org_mode/orgnode.py)
- [src/khoj/processor/content/plaintext/plaintext_to_entries.py](src/khoj/processor/content/plaintext/plaintext_to_entries.py)
- [src/khoj/processor/content/text_to_entries.py](src/khoj/processor/content/text_to_entries.py)
- [src/khoj/processor/embeddings.py](src/khoj/processor/embeddings.py)
- [src/khoj/search_type/text_search.py](src/khoj/search_type/text_search.py)
- [tests/conftest.py](tests/conftest.py)
- [tests/helpers.py](tests/helpers.py)
- [tests/test_client.py](tests/test_client.py)
- [tests/test_helpers.py](tests/test_helpers.py)
- [tests/test_markdown_to_entries.py](tests/test_markdown_to_entries.py)
- [tests/test_org_to_entries.py](tests/test_org_to_entries.py)
- [tests/test_orgnode.py](tests/test_orgnode.py)
- [tests/test_pdf_to_entries.py](tests/test_pdf_to_entries.py)
- [tests/test_plaintext_to_entries.py](tests/test_plaintext_to_entries.py)
- [tests/test_text_search.py](tests/test_text_search.py)

</details>



This document covers Khoj's content processing pipeline and semantic search capabilities. It explains how diverse document types are parsed, indexed, and made searchable through vector embeddings and similarity matching. For information about the chat and conversation system that leverages this search functionality, see [Conversation and AI System](#3).

## Architecture Overview

The content processing and search system follows a multi-stage pipeline that transforms raw documents into searchable vector embeddings, then provides semantic search capabilities across the indexed content.

```mermaid
graph TD
    subgraph "Content Sources"
        [LocalFiles] --> [FSSync]
        [GitHub] --> [GithubToEntries]
        [Notion] --> [NotionToEntries]
    end
    
    subgraph "File Collection"
        [FSSync] -- "collect_files()" --> [ConfigDB]
        [ConfigDB] -- "LocalMarkdownConfig" --> [MarkdownProc]
    end
    
    subgraph "Content Processors"
        [MarkdownProc] -- "MarkdownToEntries.process()" --> [TextToEntries]
        [OrgProc] -- "OrgToEntries.process()" --> [TextToEntries]
        [PlaintextProc] -- "PlaintextToEntries.process()" --> [TextToEntries]
    end
    
    subgraph "Text Processing"
        [TextToEntries] -- "split_entries_by_max_tokens()" --> [Chunking]
        [Chunking] -- "RecursiveCharacterTextSplitter" --> [Embeddings]
    end
    
    subgraph "Search Engine"
        [Embeddings] -- "EmbeddingsModel.embed_documents()" --> [VectorDB]
        [VectorDB] -- "Entry.embeddings (pgvector)" --> [SearchAPI]
        [SearchAPI] -- "text_search.query()" --> [Results]
    end
```

Sources: [src/khoj/processor/content/text_to_entries.py:27-35](), [src/khoj/search_type/text_search.py:99-138](), [src/khoj/processor/content/markdown/markdown_to_entries.py:21-50]()

## Content Processing Pipeline

Each content type has a specialized processor that inherits from `TextToEntries` and implements the document-specific parsing logic. For deep technical details on specific format processors, hash-based change detection, and batch indexing, see [Content Indexing Pipeline](#4.1).

```mermaid
graph TD
    subgraph "Base Class: TextToEntries"
        [TextToEntries] -- "update_embeddings()" --> [EntryAdapters]
    end
    
    subgraph "Subclasses"
        [MarkdownToEntries] -- "inherits" --> [TextToEntries]
        [OrgToEntries] -- "inherits" --> [TextToEntries]
        [PlaintextToEntries] -- "inherits" --> [TextToEntries]
    end

    subgraph "Logic Flow"
        [process] -- "calls" --> [extract_entries]
        [extract_entries] -- "calls" --> [split_entries_by_max_tokens]
        [split_entries_by_max_tokens] -- "calls" --> [update_embeddings]
    end
```

Sources: [src/khoj/processor/content/text_to_entries.py:27-35](), [src/khoj/processor/content/markdown/markdown_to_entries.py:16-18](), [src/khoj/processor/content/org_mode/org_to_entries.py:17-19]()

## Text Processing and Entry Chunking

Raw file content is processed into structured `Entry` objects that are then chunked to fit within model token limits.

### Entry Structure
Each processed document becomes one or more `Entry` objects (defined in `src/khoj/utils/rawconfig.py`) with fields including `raw`, `compiled`, `heading`, `file`, `uri`, and `corpus_id` [src/khoj/processor/content/text_to_entries.py:130-138]().

### Token-Based Chunking
The `split_entries_by_max_tokens()` method uses `RecursiveCharacterTextSplitter` from LangChain to break large entries into smaller chunks [src/khoj/processor/content/text_to_entries.py:61-80]().
- **Chunk Size**: Default is 256 tokens [src/khoj/processor/content/text_to_entries.py:62]().
- **Separators**: Paragraphs, newlines, sentences, and words [src/khoj/processor/content/text_to_entries.py:74]().
- **Context Preservation**: Prepends the heading to chunks (after the first) to maintain search context [src/khoj/processor/content/text_to_entries.py:112-117]().

Sources: [src/khoj/processor/content/text_to_entries.py:61-140]()

## Search Engine

The search engine provides semantic search capabilities using vector embeddings and optional cross-encoder reranking. For details on vector similarity with `pgvector`, search filters, and API endpoints, see [Search Engine](#4.2).

### Search Process Flow
1. **Query Encoding**: The raw string is encoded into a vector using `EmbeddingsModel.embed_query()` [src/khoj/processor/embeddings.py:53-58]().
2. **Vector Retrieval**: `EntryAdapters.search_with_embeddings()` performs a similarity search in the database [src/khoj/search_type/text_search.py:127-135]().
3. **Reranking**: If a cross-encoder is configured, results are reranked using `CrossEncoderModel.predict()` for higher precision [src/khoj/processor/embeddings.py:135-146]().

### Search Types
The system maps search types to database entry types via `search_type_to_embeddings_type` [src/khoj/search_type/text_search.py:24-32]():
- `Org`, `Markdown`, `Plaintext`, `Pdf`, `Github`, `Notion`, and `All`.

Sources: [src/khoj/search_type/text_search.py:99-138](), [src/khoj/processor/embeddings.py:29-147]()

## Entry Management and Database Storage

The `update_embeddings()` method handles the complete lifecycle of entries in the database [src/khoj/processor/content/text_to_entries.py:142-153]().

### Lifecycle Management
- **Change Detection**: Uses MD5 hashes of entry content to identify new or modified entries [src/khoj/processor/content/text_to_entries.py:36-37]().
- **Batch Processing**: Database operations are batched to optimize performance [src/khoj/processor/content/text_to_entries.py:21]().
- **Model Integration**: Uses `EmbeddingsModel` (Bi-Encoder) to generate vectors for storage in the `Entry` model's `embeddings` field [src/khoj/processor/embeddings.py:94-114]().

Sources: [src/khoj/processor/content/text_to_entries.py:142-265](), [src/khoj/processor/embeddings.py:29-114]()

---

