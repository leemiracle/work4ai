<!-- source: DeepWiki mcp.deepwiki.com · repo flepied/second-brain-agent · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [pyproject.toml](pyproject.toml)

</details>



## Purpose and Scope

This page provides a high-level introduction to the Second Brain AI Agent system, its architecture, core capabilities, and technology stack. It is intended for developers and technical users who need to understand how the system works as a whole before diving into specific subsystems.

For detailed information about specific components, see:
- Data processing pipeline details: [Data Processing Pipeline](#2)
- Agent intelligence and RAG implementation: [Agent and Intelligence Layer](#3)
- User interfaces: [User Interfaces](#4)
- Deployment and infrastructure: [Infrastructure and Deployment](#5)
- Development setup: [Development Environment](#6)

## System Purpose

The Second Brain AI Agent is a **Personal Knowledge Management (PKM) system** that automatically indexes and enables semantic search over markdown notes and embedded content. Inspired by Tiago Forte's Second Brain methodology, it transforms unstructured personal knowledge into a queryable AI-powered system.

### Core Capabilities

| Capability | Description | Implementation |
|------------|-------------|----------------|
| **Automated Indexing** | Monitors markdown files and extracts content from embedded links (PDFs, YouTube videos, web pages, audio files) | `transform_md.py`, `monitor.sh` |
| **Semantic Search** | Vector-based similarity search using embeddings | `ChromaDB`, `similarity.py` |
| **RAG-based Q&A** | Question answering using Retrieval-Augmented Generation with OpenAI LLMs | `lib.py:Agent`, `qa.py` |
| **Intent Classification** | Routes queries to specialized processing chains based on intent (summary, activity report, lookup) | `extractors.py` |
| **Multi-Interface Access** | Web UI, MCP protocol server, and CLI tools | `second_brain_agent.py`, `mcp_server.py`, CLI scripts |
| **Continuous Processing** | Automatic reprocessing of changed files via filesystem monitoring | `monitor.sh`, systemd services |

Sources: [README.md:5-36](), [README.md:40-73]()

## System Architecture

The system follows a **three-layer architecture**: data ingestion, storage, and query interfaces, with an AI orchestration layer coordinating intelligent query processing.

```mermaid
graph TB
    subgraph Input["Input Layer"]
        MD["Markdown Files<br/>(SRCDIR)"]
        USER["User Queries"]
    end
    
    subgraph Processing["Processing Layer"]
        TRANSFORM_MD["transform_md.py<br/>Content Extraction"]
        TRANSFORM_TXT["transform_txt.py<br/>Chunking & Embedding"]
        MONITOR["monitor.sh<br/>inotifywait"]
    end
    
    subgraph Storage["Storage Layer"]
        JSON["JSON Files<br/>(DSTDIR/Text)"]
        CHUNKS["Chunk Files<br/>(DSTDIR/Chunk)"]
        CHECKSUMS["checksums.json<br/>ChecksumStore"]
        CHROMADB["ChromaDB<br/>Vector Database<br/>Port 8000"]
    end
    
    subgraph Intelligence["Intelligence Layer"]
        AGENT["Agent class<br/>(lib.py)"]
        EXTRACTORS["extractors.py<br/>Intent Classification"]
        VECTORSTORE["get_vectorstore()<br/>(lib.py)"]
    end
    
    subgraph Interfaces["Interface Layer"]
        STREAMLIT["second_brain_agent.py<br/>Streamlit Web UI<br/>Port 8502"]
        MCP["mcp_server.py<br/>FastMCP Server"]
        CLI_SIM["similarity.py<br/>Vector Search"]
        CLI_QA["qa.py<br/>Q&A"]
    end
    
    MD -->|"Monitored by"| MONITOR
    MONITOR -->|"Triggers"| TRANSFORM_MD
    TRANSFORM_MD -->|"Writes"| JSON
    TRANSFORM_MD -->|"Updates"| CHECKSUMS
    JSON -->|"Processed by"| TRANSFORM_TXT
    TRANSFORM_TXT -->|"Writes"| CHUNKS
    TRANSFORM_TXT -->|"Stores vectors"| CHROMADB
    
    USER -->|"Queries"| STREAMLIT
    USER -->|"Queries"| MCP
    USER -->|"Queries"| CLI_SIM
    USER -->|"Queries"| CLI_QA
    
    STREAMLIT -->|"Uses"| AGENT
    CLI_QA -->|"Uses"| AGENT
    CLI_SIM -->|"Direct access"| VECTORSTORE
    MCP -->|"Direct access"| VECTORSTORE
    
    AGENT -->|"Classifies intent"| EXTRACTORS
    AGENT -->|"Retrieves context"| VECTORSTORE
    VECTORSTORE -->|"Queries"| CHROMADB
```

**Architecture Analysis**: The system separates data ingestion from query processing, with `ChromaDB` serving as the central knowledge repository. The `Agent` class in `lib.py` acts as the orchestrator for intelligent queries, while simpler tools can bypass it for direct vector database access.

Sources: [README.md:40-52](), Diagram 1 from context

## Data Flow Pipeline

The system implements a **two-stage pipeline** that decouples content extraction from vectorization:

```mermaid
graph LR
    subgraph Sources["Content Sources"]
        MD_FILES["Markdown Files"]
        YOUTUBE["YouTube Videos"]
        PDFS["PDF Documents"]
        URLS["Web Pages"]
        AUDIO["MP3 Audio"]
    end
    
    subgraph Stage1["Stage 1: Content Extraction<br/>transform_md.py"]
        MD_PARSER["Markdown parsing"]
        YT_TRANS["YouTube transcription<br/>youtube-transcript-api"]
        PDF_EXTRACT["PDF extraction<br/>PyMuPDF"]
        URL_EXTRACT["Web page extraction<br/>Unstructured"]
        AUDIO_TRANS["Audio transcription<br/>AssemblyAI"]
        HIST_SPLIT["History file splitter<br/>Date-based"]
    end
    
    subgraph Intermediate["Intermediate Storage"]
        JSON_FILES["JSON files<br/>DSTDIR/Text/<br/>metadata + text"]
        CHECKSUM_STORE["ChecksumStore<br/>MD5 hashing"]
    end
    
    subgraph Stage2["Stage 2: Chunking & Embedding<br/>transform_txt.py"]
        VALIDATOR["JSON validation<br/>datetime_decoder"]
        SPLITTER["TokenTextSplitter<br/>CHUNK_SIZE=1000<br/>OVERLAP=50"]
        META_ENRICH["Metadata enrichment<br/>source, referer, part"]
    end
    
    subgraph Output["Output"]
        CHUNK_FILES["Chunk files<br/>DSTDIR/Chunk/<br/>basename-NNNN.txt"]
        EMBEDDINGS["Vector embeddings<br/>all-MiniLM-L6-v2"]
        DB["ChromaDB"]
    end
    
    MD_FILES -->|"Parse"| MD_PARSER
    MD_FILES -->|"Links"| YOUTUBE
    MD_FILES -->|"Links"| PDFS
    MD_FILES -->|"Links"| URLS
    MD_FILES -->|"Links"| AUDIO
    
    MD_PARSER -->|"Write"| JSON_FILES
    YOUTUBE -->|"Transcribe"| YT_TRANS
    PDFS -->|"Extract"| PDF_EXTRACT
    URLS -->|"Extract"| URL_EXTRACT
    AUDIO -->|"Transcribe"| AUDIO_TRANS
    MD_PARSER -->|"If history"| HIST_SPLIT
    
    YT_TRANS -->|"Write"| JSON_FILES
    PDF_EXTRACT -->|"Write"| JSON_FILES
    URL_EXTRACT -->|"Write"| JSON_FILES
    AUDIO_TRANS -->|"Write"| JSON_FILES
    HIST_SPLIT -->|"Write multiple"| JSON_FILES
    
    JSON_FILES -->|"Track changes"| CHECKSUM_STORE
    JSON_FILES -->|"Read"| VALIDATOR
    VALIDATOR -->|"Split"| SPLITTER
    SPLITTER -->|"Enrich"| META_ENRICH
    
    META_ENRICH -->|"Write"| CHUNK_FILES
    META_ENRICH -->|"Generate"| EMBEDDINGS
    EMBEDDINGS -->|"Store"| DB
    META_ENRICH -->|"Store metadata"| DB
```

**Pipeline Design**: The two-stage design allows content extraction to be independent of vectorization. `ChecksumStore` provides incremental processing by tracking file changes via MD5 hashing, ensuring only modified content is reprocessed.

Sources: [README.md:40-52](), [README.md:47-49](), Diagram 2 from context

## Query Processing Architecture

The system implements **intent-based query routing** where different query types follow optimized processing paths:

### Query Types and Processing Chains

| Intent Type | Detection Method | Processing Chain | Key Functions |
|-------------|------------------|------------------|---------------|
| **Regular Question** | Default classification | Step-back prompting → Vector retrieval → LLM generation | `extractors.py:rephrase_sentence()`, `lib.py:Agent.question()` |
| **Activity Report** | Time period or domain keywords | Period extraction → Document filtering → Filtered retrieval → LLM | `extractors.py:get_period()`, `extractors.py:get_docs()` |
| **Summary Request** | "summarize" keyword | Retrieve all chunks → LLM summarization | `lib.py:Agent.question()` |
| **PDF/URL Lookup** | URL pattern detection | Direct document extraction | `extractors.py:get_url()` |

### Intent Classification Flow

```mermaid
graph TD
    QUERY["User Query"]
    CLASSIFY["extractors.py<br/>classify_intent()"]
    
    REGULAR["Regular Question"]
    ACTIVITY["Activity Report"]
    SUMMARY["Summary Request"]
    LOOKUP["PDF/URL Lookup"]
    
    STEPBACK["extractors.py<br/>rephrase_sentence()<br/>Step-back prompting"]
    PERIOD["extractors.py<br/>get_period()<br/>Time extraction"]
    DOCS["extractors.py<br/>get_docs()<br/>Domain extraction"]
    URL["extractors.py<br/>get_url()<br/>URL extraction"]
    
    VDB["get_vectorstore()<br/>ChromaDB access"]
    FILTER["Metadata filtering<br/>period + domain"]
    
    LLM["OpenAI LLM<br/>Answer generation"]
    
    QUERY --> CLASSIFY
    CLASSIFY -->|"Default"| REGULAR
    CLASSIFY -->|"Time/domain keywords"| ACTIVITY
    CLASSIFY -->|"'summarize' keyword"| SUMMARY
    CLASSIFY -->|"URL pattern"| LOOKUP
    
    REGULAR --> STEPBACK
    STEPBACK --> VDB
    
    ACTIVITY --> PERIOD
    ACTIVITY --> DOCS
    PERIOD --> FILTER
    DOCS --> FILTER
    FILTER --> VDB
    
    SUMMARY --> VDB
    LOOKUP --> URL
    
    VDB --> LLM
    URL --> LLM
    LLM --> QUERY
```

**Intent Routing**: The `Agent` class in `lib.py` delegates intent classification to `extractors.py`, which uses LLM-based parsing to extract time periods, domains, and query types. This enables specialized retrieval strategies for different question types.

Sources: [README.md:53-73](), Diagram 3 from context

## Key Features

### Multi-Source Content Ingestion

The system supports diverse content types through specialized extractors:

- **YouTube videos**: Transcript API with Whisper fallback ([transform_md.py]())
- **PDF documents**: PyMuPDF-based extraction ([transform_md.py]())
- **Web pages**: Unstructured library for HTML parsing ([transform_md.py]())
- **Audio files**: AssemblyAI transcription service ([transform_md.py]())
- **History files**: Date-based segmentation for journal entries ([transform_md.py]())

### Domain-Based Organization

The system implements a **domain metadata system** for document classification:

1. Domain extraction: Removes numbers and keywords (`At`, `Journal`, `Project`, `Notes`, `History`) from filenames
2. Example: `WorkoutHistory202412.md` → domain: `Workout`
3. Organization document: `SecondBrainOrganization.md` (configurable via `SBA_ORG_DOC`) maps domains to categories
4. Used for filtered retrieval in activity reports

Sources: [README.md:68-72]()

### MCP Protocol Server

The `mcp_server.py` implements a **FastMCP server** providing programmatic access:

| Tool | Function | Parameters |
|------|----------|------------|
| `search_documents` | Semantic search with metadata filtering | `query`, `filter_metadata`, `n_results` |
| `get_document_count` | Returns total document count | None |
| `get_domains` | Lists available domains | None |
| `get_recent_documents` | Retrieves recently accessed documents | `n_results` |

The MCP server enables integration with external applications without requiring the full Agent reasoning layer.

Sources: [README.md:74-124]()

## Technology Stack

### Core Dependencies

The system is built on the **LangChain framework** with specialized integrations:

| Category | Technology | Purpose |
|----------|------------|---------|
| **RAG Framework** | `langchain`, `langchain-core` | Orchestration and chain management |
| **Vector Database** | `chromadb` (v0.4+) | Embedding storage and similarity search |
| **LLM Provider** | `openai`, `langchain-openai` | GPT models for answer generation |
| **Embeddings** | `sentence-transformers`, `langchain-huggingface` | Text vectorization (all-MiniLM-L6-v2) |
| **Document Loaders** | `langchain-community`, `pymupdf`, `unstructured` | Multi-format content extraction |
| **Web UI** | `streamlit`, `altair` | Interactive query interface |
| **MCP Server** | `fastmcp`, `pydantic` | Programmatic API |
| **Audio/Video** | `youtube-transcript-api`, `yt-dlp`, `pydub`, `assemblyai` | Multimedia transcription |

### Dependency Management

The project uses **Poetry** for dependency management:
- Main dependencies: [pyproject.toml:17-46]()
- Test dependencies: [pyproject.toml:48-54]()
- Python version requirement: `>=3.10,<3.12`

Sources: [pyproject.toml:1-70](), [README.md:38-39](), Diagram 5 from context

## Runtime Infrastructure

The system runs as a set of coordinated services:

### Background Services (systemd)

| Service | Script | Purpose | Dependencies |
|---------|--------|---------|--------------|
| `sba-md.service` | `transform_md.py` via `monitor.sh` | Content extraction from markdown files | `inotify-tools` |
| `sba-txt.service` | `transform_txt.py` via `monitor.sh` | Chunking and embedding generation | `ChromaDB` container |

### Database Container

ChromaDB runs in a Docker container:
- Configuration: `compose.yaml`
- Port: 8000
- Persistent storage: Volumes defined in compose configuration
- Version: Synchronized with `poetry.lock` via `Makefile`

Sources: [README.md:159-172](), Diagram 4 from context

## System Requirements

### Installation Prerequisites

- **Python**: 3.10 or 3.11 (not 3.12)
- **Package Manager**: Poetry
- **System Tools**: `inotify-tools` for file monitoring
- **Container Runtime**: Docker or Podman (for ChromaDB)
- **Operating System**: Tested on Fedora Linux 42 and Ubuntu latest

### API Keys Required

The system requires API keys configured in `.env`:
- `OPENAI_API_KEY`: For GPT models
- `HUGGINGFACEHUB_API_TOKEN`: For embeddings
- `ASSEMBLYAI_API_KEY`: For audio transcription (optional)

For configuration details, see [Configuration Management](#5.3).

Sources: [README.md:126-157](), [pyproject.toml:18]()

## Getting Started

### Basic Usage Flow

1. **Setup**: Install dependencies, configure `.env`, start ChromaDB container
2. **Ingestion**: Point `SRCDIR` to markdown notes directory, start systemd services
3. **Query**: Use web UI (`streamlit run second_brain_agent.py`), CLI tools (`similarity.py`, `qa.py`), or MCP server

### Example Commands

```bash
# Similarity search
./similarity.py "What is LangChain?" type=notes

# Question answering
./qa.py "What did I work on last week?"

# Launch web UI
streamlit run second_brain_agent.py

# Start MCP server
poetry run python mcp_server.py
```

Sources: [README.md:174-198]()

---

