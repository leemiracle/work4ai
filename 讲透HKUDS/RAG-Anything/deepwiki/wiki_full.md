# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README_zh.md](README_zh.md)
- [raganything/__init__.py](raganything/__init__.py)

</details>



## Purpose and Scope

This document provides a high-level introduction to RAG-Anything, an all-in-one multimodal Retrieval-Augmented Generation (RAG) framework. It explains the system's core value proposition, architecture, and main components.

For detailed installation instructions, see [Installation](#2.1). For configuration details, see [Configuration](#8). For implementation details of specific subsystems, see [System Architecture](#3), [Document Processing](#4), [Multimodal Content Processing](#5), and [Query System](#7).

Sources: [README.md:1-98]()

## What is RAG-Anything

RAG-Anything is a comprehensive multimodal document processing and retrieval system built on top of [LightRAG](https://github.com/HKUDS/LightRAG). It extends traditional text-only RAG systems to handle heterogeneous content types including text, images, tables, mathematical equations, and structured data within a unified framework.

The system addresses the limitation that modern documents contain diverse multimodal content that text-focused RAG systems cannot effectively process. Unlike conventional approaches requiring multiple specialized tools, RAG-Anything provides seamless processing and querying across all content modalities through a single integrated interface.

**Key Distinguishing Features:**

| Feature | Description |
|---------|-------------|
| **Unified Processing** | Single framework handles PDFs, Office documents, images, and text files |
| **Multimodal Analysis** | Specialized processors for images, tables, equations with context awareness |
| **Knowledge Graph Integration** | Cross-modal entity extraction and relationship mapping |
| **Flexible Parsing** | Multiple parser backends (MinerU, Docling, PaddleOCR) with format-specific optimization |
| **Multi-Mode Querying** | Text queries, multimodal queries, and VLM-enhanced queries |

Sources: [README.md:83-112](), [raganything/__init__.py:8-14]()

## Core Architecture

### Architectural Overview

RAG-Anything implements a three-layer architecture built on top of LightRAG, utilizing a Mixin-based design to separate concerns.

```mermaid
graph TB
    subgraph "raganything Package"
        Init["raganything/__init__.py<br/>RAGAnything<br/>RAGAnythingConfig"]
        Core["raganything/raganything.py<br/>RAGAnything class"]
    end
    
    subgraph "Mixin-Based Functionality"
        ProcMix["raganything/processor.py<br/>ProcessorMixin"]
        QueryMix["raganything/query.py<br/>QueryMixin"]
        BatchMix["raganything/batch.py<br/>BatchMixin"]
    end
    
    subgraph "Document Parsing Subsystem"
        ParserBase["raganything/parser.py<br/>Parser (base class)<br/>parse_document()"]
        MinerUImpl["MineruParser<br/>parse_method: auto/ocr/txt"]
        DoclingImpl["DoclingParser<br/>Office/HTML optimization"]
        PaddleImpl["PaddleOCRParser<br/>OCR-focused"]
    end
    
    subgraph "Multimodal Processing Subsystem"
        ModalBase["raganything/modalprocessors.py<br/>BaseModalProcessor"]
        ImgProc["ImageModalProcessor<br/>vision_model_func"]
        TblProc["TableModalProcessor<br/>modal_caption_func"]
        EqProc["EquationModalProcessor<br/>modal_caption_func"]
        GenProc["GenericModalProcessor<br/>extensible base"]
        CtxExt["ContextExtractor<br/>ContextConfig"]
    end
    
    subgraph "LightRAG Foundation"
        LR["LightRAG instance<br/>working_dir<br/>llm_model_func<br/>embedding_func"]
        Storage["Storage Backends:<br/>text_chunks<br/>chunks_vdb<br/>entities_vdb<br/>relations_vdb<br/>knowledge_graph<br/>doc_status"]
    end
    
    Init --> Core
    Core --> ProcMix
    Core --> QueryMix
    Core --> BatchMix
    
    ProcMix --> ParserBase
    ParserBase --> MinerUImpl
    ParserBase --> DoclingImpl
    ParserBase --> PaddleImpl
    
    ProcMix --> ModalBase
    ModalBase --> ImgProc
    ModalBase --> TblProc
    ModalBase --> EqProc
    ModalBase --> GenProc
    ModalBase --> CtxExt
    
    Core --> LR
    ProcMix --> LR
    QueryMix --> LR
    ModalBase --> LR
    LR --> Storage
```

**Core Classes and Their Roles:**

| Class | File Location | Primary Responsibility |
|-------|--------------|------------------------|
| `RAGAnything` | [raganything/raganything.py:28-29]() | Main orchestrator, inherits from mixins, holds LightRAG instance |
| `RAGAnythingConfig` | [raganything/config.py:12-13]() | Configuration dataclass for all system parameters |
| `ProcessorMixin` | [raganything/processor.py:46-47]() | Document processing methods: `process_document_complete()`, `insert_content_list()` |
| `QueryMixin` | [raganything/query.py:23-24]() | Query methods: `aquery()`, `aquery_with_multimodal()` |
| `BatchMixin` | [raganything/batch.py:84-85]() | Batch processing logic: `process_folder_complete()`, `process_documents_batch()` |
| `Parser` | [raganything/parser.py:53-54]() | Abstract base for document parsers, defines `parse_document()` interface |
| `BaseModalProcessor` | [raganything/modalprocessors.py:102-103]() | Abstract base for multimodal content processors |
| `ContextExtractor` | [raganything/modalprocessors.py:49-50]() | Extracts surrounding text context for multimodal items |

Sources: [raganything/__init__.py:1-68](), [README.md:115-150]()

### Component Interaction Diagram

**System Initialization and Processing Flow:**

```mermaid
sequenceDiagram
    participant User
    participant RAGAnything
    participant ProcessorMixin
    participant Parser
    participant ModalProcessor
    participant LightRAG
    participant Storage

    User->>RAGAnything: process_document_complete(file_path)
    RAGAnything->>ProcessorMixin: delegate to mixin method
    ProcessorMixin->>Parser: parse_document(file_path, parse_method)
    Parser-->>ProcessorMixin: content_list, md_content
    
    ProcessorMixin->>ProcessorMixin: separate_content(content_list)
    ProcessorMixin->>LightRAG: ainsert(text_chunks)
    
    loop For each multimodal item
        ProcessorMixin->>ModalProcessor: process_multimodal_content()
        ModalProcessor->>ModalProcessor: extract_context(page_idx)
        ModalProcessor->>LightRAG: generate description + entities
        ModalProcessor->>Storage: create entity, belongs_to relations
    end
    
    ProcessorMixin->>Storage: update doc_status(multimodal_processed=True)
    ProcessorMixin-->>User: processing complete
```

**Query Processing Flow:**

```mermaid
sequenceDiagram
    participant User
    participant QueryMixin
    participant LightRAG
    participant Storage
    participant VLM

    User->>QueryMixin: aquery(query_text, vlm_enhanced=True)
    QueryMixin->>LightRAG: retrieve context (hybrid/local/global/naive)
    LightRAG->>Storage: fetch entities, chunks, relations
    Storage-->>LightRAG: retrieved context
    
    alt VLM Enhanced Mode
        QueryMixin->>QueryMixin: detect image paths in context
        QueryMixin->>VLM: vision_model_func(query + images)
        VLM-->>QueryMixin: enhanced response
    else Text Only Mode
        QueryMixin->>LightRAG: llm_model_func(query + context)
        LightRAG-->>QueryMixin: text response
    end
    
    QueryMixin-->>User: final response
```

Sources: [raganything/processor.py:214-266](), [raganything/query.py:101-155](), [raganything/modalprocessors.py:155-190]()

### Five-Stage Processing Pipeline

**Pipeline Flow with Code Constructs:**

```mermaid
flowchart TB
    subgraph Stage1["Stage 1: Document Parsing"]
        Input["File Input:<br/>PDF/DOCX/PNG/TXT/etc."]
        ParseSelect{"Parser.parse_document()<br/>(raganything/parser.py)"}
        MinerU["MineruParser<br/>parse_method param:<br/>auto/ocr/txt"]
        Docling["DoclingParser<br/>Office/HTML optimized"]
        Paddle["PaddleOCRParser<br/>OCR-focused"]
        Output1["Output:<br/>content_list: List[Dict]<br/>md_content: str"]
    end
    
    subgraph Stage2["Stage 2: Content Separation"]
        Separate["ProcessorMixin.separate_content()<br/>(raganything/processor.py)"]
        TextPath["text_content: List[str]<br/>→ LightRAG.ainsert()"]
        MMPath["multimodal_items: List[Dict]<br/>→ Modal Processors"]
    end
    
    subgraph Stage3["Stage 3: Multimodal Processing"]
        ImgProc["ImageModalProcessor<br/>.process_multimodal_content()"]
        TblProc["TableModalProcessor<br/>.process_multimodal_content()"]
        EqProc["EquationModalProcessor<br/>.process_multimodal_content()"]
        Context["ContextExtractor<br/>.extract_context(page_idx)"]
    end
    
    subgraph Stage4["Stage 4: Knowledge Graph Index"]
        Entity["Create Modal Entity<br/>entity_name, entity_type"]
        LLMExtract["LLM Entity Extraction<br/>llm_model_func()"]
        Belongs["belongs_to relations<br/>link to source entity"]
        KGStore["Store in LightRAG:<br/>entities_vdb<br/>relations_vdb<br/>knowledge_graph"]
    end
    
    subgraph Stage5["Stage 5: Query & Retrieval"]
        QueryAPI["QueryMixin methods:<br/>aquery()<br/>aquery_with_multimodal()"]
        Retrieve["LightRAG.query()<br/>mode: hybrid/local/global/naive"]
        VLMEnhance["Optional: VLM Enhancement<br/>vision_model_func()"]
        Response["Response with<br/>multimodal context"]
    end
    
    Input --> ParseSelect
    ParseSelect --> MinerU
    ParseSelect --> Docling
    ParseSelect --> Paddle
    MinerU --> Output1
    Docling --> Output1
    Paddle --> Output1
    
    Output1 --> Separate
    Separate --> TextPath
    Separate --> MMPath
    
    MMPath --> ImgProc
    MMPath --> TblProc
    MMPath --> EqProc
    ImgProc --> Context
    TblProc --> Context
    EqProc --> Context
    
    Context --> Entity
    Entity --> LLMExtract
    LLMExtract --> Belongs
    Belongs --> KGStore
    
    KGStore --> QueryAPI
    QueryAPI --> Retrieve
    Retrieve --> VLMEnhance
    VLMEnhance --> Response
```

**Stage Implementation Details:**

| Stage | Entry Point | Key Methods | Output Format |
|-------|-------------|-------------|---------------|
| **1. Parsing** | `Parser.parse_document()` | `MineruParser._parse_with_mineru()`, `DoclingParser._parse_with_docling()` | `content_list: List[Dict]` with keys: `type`, `text`, `img_path`, `table_body`, `latex`, `page_idx` |
| **2. Separation** | `ProcessorMixin.separate_content()` | Internal logic splits by `content['type']` | Text strings for LightRAG, dicts for modal processors |
| **3. Modal Analysis** | `BaseModalProcessor.process_multimodal_content()` | `ContextExtractor.extract_context()`, `vision_model_func()`, `modal_caption_func()` | Enhanced description string, entity metadata dict |
| **4. KG Construction** | LightRAG integration | `LightRAG.ainsert()`, entity extraction, relationship mapping | Entities stored in `entities_vdb`, relations in `relations_vdb` and `knowledge_graph` |
| **5. Query** | `QueryMixin.aquery()` | `LightRAG.query()`, optional VLM enhancement via `vision_model_func()` | String response with citations |

**Parse Cache System:**

Documents are cached to avoid redundant parsing. Cache key generation:
`cache_key = f"{file_path}_{mtime}_{parser_name}_{parse_method}_{config_hash}"`
Cache location: `{working_dir}/parse_cache/{cache_key}.json`

Sources: [raganything/parser.py:53-84](), [raganything/processor.py:423-448](), [raganything/modalprocessors.py:155-190](), [raganything/query.py:101-155](), [README.md:151-246]()

## Configuration and Initialization

### Configuration Architecture

```mermaid
graph TB
    subgraph ConfigSources["Configuration Sources (priority order)"]
        CLI["Command Line Args<br/>(highest priority)"]
        EnvVars["Environment Variables<br/>OPENAI_API_KEY, PARSER, etc."]
        DotEnv[".env File<br/>loads via python-dotenv"]
        Defaults["System Defaults<br/>in RAGAnythingConfig"]
    end
    
    subgraph ConfigClasses["Configuration Classes"]
        RAGConfig["RAGAnythingConfig<br/>(raganything/config.py)<br/>dataclass with:<br/>working_dir<br/>parser: str<br/>parse_method: str<br/>enable_*_processing: bool"]
        CtxConfig["ContextConfig<br/>(raganything/modalprocessors.py)<br/>context_window_pages<br/>context_max_tokens<br/>context_mode"]
    end
    
    subgraph Initialization["RAGAnything Initialization"]
        InitMethod["RAGAnything.__init__()<br/>Accepts:<br/>config: RAGAnythingConfig<br/>lightrag: LightRAG (optional)<br/>llm_model_func<br/>vision_model_func<br/>embedding_func"]
        CreateLR["Creates LightRAG if not provided:<br/>LightRAG(working_dir, llm_model_func, embedding_func)"]
        InitStorage["await initialize_storages()<br/>text_chunks, chunks_vdb,<br/>entities_vdb, relations_vdb,<br/>knowledge_graph, doc_status"]
    end
    
    CLI --> RAGConfig
    EnvVars --> RAGConfig
    DotEnv --> EnvVars
    Defaults --> RAGConfig
    
    RAGConfig --> CtxConfig
    RAGConfig --> InitMethod
    InitMethod --> CreateLR
    CreateLR --> InitStorage
```

**Key Configuration Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `working_dir` | `str` | `"./rag_storage"` | Directory for LightRAG data persistence |
| `parser` | `str` | `"mineru"` | Parser backend: `"mineru"`, `"docling"`, or `"paddleocr"` |
| `parse_method` | `str` | `"auto"` | Parse mode: `"auto"`, `"ocr"`, or `"txt"` (MinerU-specific) |
| `enable_image_processing` | `bool` | `True` | Enable `ImageModalProcessor` |
| `enable_table_processing` | `bool` | `True` | Enable `TableModalProcessor` |
| `enable_equation_processing` | `bool` | `True` | Enable `EquationModalProcessor` |

Sources: [raganything/config.py:12-70](), [raganything/raganything.py:31-90](), [README.md:326-427]()

## Supported Content Types

### Document Format Support Matrix

| Format | Extensions | MinerU | Docling | PaddleOCR | External Dependency |
|--------|-----------|--------|---------|-----------|---------------------|
| **PDF** | `.pdf` | ✓ (primary) | ✓ | ✓ | None |
| **Office** | `.doc`, `.docx`, `.ppt`, `.pptx`, `.xls`, `.xlsx` | ✓ (via conversion) | ✓ (native) | ✓ (via conversion) | LibreOffice |
| **Images** | `.jpg`, `.png` | ✓ | ✓ | ✓ | None |
| **Extended Images** | `.bmp`, `.tiff`, `.gif`, `.webp` | ✓ | ✓ | ✓ | Pillow (`raganything[image]`) |
| **Text** | `.txt`, `.md` | ✓ (via conversion) | ✗ | ✓ (via conversion) | ReportLab (`raganything[text]`) |
| **HTML** | `.html`, `.htm` | ✗ | ✓ (primary) | ✗ | None |

### Multimodal Content Processing

**Content Type Mapping:**

| Content Type | `content_list` Format | Processor Class | Required Fields |
|--------------|----------------------|-----------------|-----------------|
| **Images** | `{"type": "image", "img_path": str}` | `ImageModalProcessor` | `img_path` (absolute path) |
| **Tables** | `{"type": "table", "table_body": str}` | `TableModalProcessor` | `table_body` (markdown) |
| **Equations** | `{"type": "equation", "latex": str}` | `EquationModalProcessor` | `latex` (LaTeX string) |
| **Text** | `{"type": "text", "text": str}` | Direct to LightRAG | `text` content |

Sources: [raganything/parser.py:53-84](), [raganything/modalprocessors.py:202-386](), [README.md:1136-1168]()

## System Extension Points

| Extension Point | Base Class | Required Methods | Use Case |
|----------------|------------|------------------|----------|
| **Custom Modal Processor** | `GenericModalProcessor` | `process_multimodal_content()` | Process domain-specific content types |
| **Custom Parser** | `Parser` | `parse_document()` | Integrate alternative parsing engines |
| **Direct Injection** | N/A | `insert_content_list()` | Use pre-parsed content from external sources |

Sources: [raganything/modalprocessors.py:386-412](), [raganything/parser.py:53-84](), [raganything/processor.py:268-335]()

## Relationship to LightRAG

RAG-Anything extends LightRAG's capabilities while preserving full compatibility. The system can initialize with an existing `LightRAG` instance, share working directories, and leverage LightRAG's knowledge graph and retrieval modes. `RAGAnything` holds a `LightRAG` instance and extends it with document parsing and multimodal analysis through mixins.

Sources: [raganything/raganything.py:92-125](), [README.md:674-799]()

---

# Page: Getting Started

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/pypi-publish.yml](.github/workflows/pypi-publish.yml)
- [README.md](README.md)
- [raganything/enhanced_markdown.py](raganything/enhanced_markdown.py)
- [requirements.txt](requirements.txt)
- [setup.py](setup.py)

</details>



This guide covers the essential steps to install, configure, and run your first RAG-Anything pipeline. You will learn how to set up the environment, initialize the `RAGAnything` class, process your first document, and execute basic queries.

For detailed installation options and troubleshooting, see [Installation](#2.1). For comprehensive configuration reference, see [Environment Configuration](#2.3). For complete end-to-end examples, see [Quick Start Example](#2.2).

---

## Overview

RAG-Anything requires three primary setup phases:

1.  **Installation**: Installing Python packages and external dependencies.
2.  **Configuration**: Setting up API keys and model providers.
3.  **Initialization**: Creating a `RAGAnything` instance with model functions.

Once configured, the typical workflow involves:
*   Processing documents with `process_document_complete()`.
*   Querying the knowledge base with `aquery()` or `aquery_with_multimodal()`.

---

## Prerequisites

Before installing RAG-Anything, ensure you have:

| Requirement | Version | Purpose |
| :--- | :--- | :--- |
| Python | 3.10+ | Core runtime environment [setup.py:105-105]() |
| pip or uv | Latest | Package management [README.md:26-26]() |
| API Key | - | LLM/embedding service access (OpenAI, Ollama, etc.) |

**Optional External Tools:**

| Tool | Required For | Installation Method |
| :--- | :--- | :--- |
| LibreOffice | Office documents (.docx, .xlsx, .pptx) | [Official website](https://www.libreoffice.org) or system package manager [setup.py:65-65]() |
| CUDA Toolkit | GPU acceleration for MinerU | [NVIDIA website](https://developer.nvidia.com/cuda-downloads) |

Sources: [README.md:301-308](), [setup.py:105-105](), [setup.py:65-65]()

---

## Installation Quick Reference

### Installation Architecture

```mermaid
graph TB
    subgraph "Core Installation"
        PIP["pip install raganything"]
        CORE["Core Dependencies<br/>lightrag-hku<br/>mineru[core]<br/>tqdm<br/>huggingface_hub"]
    end
    
    subgraph "Optional Python Dependencies [setup.py extras_require]"
        IMAGE["'image' extra<br/>Pillow>=10.0.0<br/>BMP, TIFF, GIF, WebP"]
        TEXT["'text' extra<br/>reportlab>=4.0.0<br/>TXT, MD files"]
        PADDLE["'paddleocr' extra<br/>paddleocr, pypdfium2<br/>Scanned PDFs"]
        ALL["'all' extra<br/>All optional features"]
    end
    
    subgraph "External Dependencies"
        LIBREOFFICE["LibreOffice<br/>Office document conversion"]
        MINERU_MODELS["MinerU Models<br/>Auto-downloaded on first use"]
    end
    
    subgraph "Verification"
        CHECK_MINERU["mineru --version"]
        CHECK_PARSER["rag.check_parser_installation()"]
    end
    
    PIP --> CORE
    PIP -.optional.-> IMAGE
    PIP -.optional.-> TEXT
    PIP -.optional.-> PADDLE
    PIP -.optional.-> ALL
    
    CORE --> CHECK_MINERU
    CORE --> CHECK_PARSER
    
    LIBREOFFICE -.external.-> CORE
    MINERU_MODELS -.auto-download.-> CORE
```

Sources: [README.md:257-320](), [requirements.txt:1-15](), [setup.py:62-84]()

### Basic Installation Commands

**From PyPI (Recommended):**
```bash
# Minimal installation
pip install raganything

# With optional dependencies for images and scanned PDFs
pip install 'raganything[image,paddleocr]'

# Install everything
pip install 'raganything[all]'
```

**From Source:**
```bash
git clone https://github.com/HKUDS/RAG-Anything.git
cd RAG-Anything
# Using uv for fast dependency resolution
uv sync
```

For detailed installation instructions including troubleshooting, see [Installation](#2.1).

Sources: [README.md:257-320](), [requirements.txt:15-16]()

---

## Configuration Essentials

### Configuration Flow

```mermaid
graph LR
    subgraph "Environment Setup"
        ENV_FILE[".env file"]
        ENV_VARS["Environment Variables<br/>OPENAI_API_KEY<br/>OPENAI_BASE_URL<br/>PARSER<br/>PARSE_METHOD"]
    end
    
    subgraph "RAGAnythingConfig"
        CONFIG["RAGAnythingConfig<br/>working_dir<br/>parser<br/>parse_method<br/>enable_*_processing"]
        CONFIG_DEFAULTS["Default Values<br/>parser='mineru'<br/>parse_method='auto'<br/>enable_image=True"]
    end
    
    subgraph "Model Functions"
        LLM_FUNC["llm_model_func<br/>openai_complete_if_cache"]
        VISION_FUNC["vision_model_func<br/>gpt-4o with images"]
        EMBED_FUNC["embedding_func<br/>EmbeddingFunc wrapper"]
    end
    
    subgraph "RAGAnything Instance"
        RAG_INSTANCE["RAGAnything(config, llm_model_func,<br/>vision_model_func, embedding_func)"]
    end
    
    ENV_FILE --> ENV_VARS
    ENV_VARS -.optional.-> CONFIG
    CONFIG_DEFAULTS --> CONFIG
    
    CONFIG --> RAG_INSTANCE
    LLM_FUNC --> RAG_INSTANCE
    VISION_FUNC --> RAG_INSTANCE
    EMBED_FUNC --> RAG_INSTANCE
```

Sources: [README.md:1037-1052](), [README.md:326-427]()

### Minimal Configuration Example

Initialize `RAGAnything` with minimal configuration using OpenAI-compatible functions:

```python
from raganything import RAGAnything, RAGAnythingConfig
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc

# Create configuration
config = RAGAnythingConfig(
    working_dir="./rag_storage",
    parser="mineru",
    enable_image_processing=True,
    enable_table_processing=True,
    enable_equation_processing=True
)

# Define model functions
def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
    return openai_complete_if_cache(
        "gpt-4o-mini",
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        api_key="your-api-key",
        **kwargs
    )

embedding_func = EmbeddingFunc(
    embedding_dim=3072,
    max_token_size=8192,
    func=lambda texts: openai_embed(
        texts,
        model="text-embedding-3-large",
        api_key="your-api-key"
    )
)

# Initialize RAGAnything orchestrator
rag = RAGAnything(
    config=config,
    llm_model_func=llm_model_func,
    embedding_func=embedding_func
)
```

For complete configuration options and environment variables, see [Environment Configuration](#2.3).

Sources: [README.md:326-427]()

---

## Your First RAG Pipeline

### End-to-End Workflow

```mermaid
graph TB
    subgraph "1. Initialization Phase"
        INIT_CONFIG["RAGAnythingConfig<br/>working_dir='./rag_storage'<br/>parser='mineru'"]
        INIT_FUNCS["Model Functions<br/>llm_model_func<br/>vision_model_func<br/>embedding_func"]
        INIT_RAG["rag = RAGAnything(config, llm_model_func,<br/>vision_model_func, embedding_func)"]
    end
    
    subgraph "2. Document Processing Phase"
        PROCESS_CALL["await rag.process_document_complete(<br/>file_path='document.pdf',<br/>output_dir='./output',<br/>parse_method='auto')"]
        PARSE["Parser Layer<br/>MineruParser / DoclingParser / PaddleOCRParser"]
        PROCESSOR["ProcessorMixin<br/>_process_multimodal_content_batch_type_aware()"]
        STORAGE["LightRAG Storage<br/>Knowledge Graph + Vector DB"]
    end
    
    subgraph "3. Query Phase"
        QUERY_TEXT["Text Query<br/>await rag.aquery(question, mode='hybrid')"]
        QUERY_MM["Multimodal Query<br/>await rag.aquery_with_multimodal(<br/>question, multimodal_content, mode='hybrid')"]
        RETRIEVAL["QueryMixin<br/>Hybrid retrieval from KG + VectorDB"]
        RESPONSE["Generated Response"]
    end
    
    INIT_CONFIG --> INIT_RAG
    INIT_FUNCS --> INIT_RAG
    
    INIT_RAG --> PROCESS_CALL
    PROCESS_CALL --> PARSE
    PARSE --> PROCESSOR
    PROCESSOR --> STORAGE
    
    STORAGE --> QUERY_TEXT
    STORAGE --> QUERY_MM
    QUERY_TEXT --> RETRIEVAL
    QUERY_MM --> RETRIEVAL
    RETRIEVAL --> RESPONSE
```

Sources: [README.md:323-457]()

### Complete Minimal Example

```python
import asyncio
from raganything import RAGAnything, RAGAnythingConfig

async def main():
    # Step 1: Initialize with basic config
    # Note: Model functions would be defined here as shown in previous section
    rag = RAGAnything(config=RAGAnythingConfig(working_dir="./rag_storage"))
    
    # Step 2: Process a document
    # This calls ProcessorMixin.process_document_complete
    await rag.process_document_complete(
        file_path="path/to/document.pdf",
        output_dir="./output"
    )
    
    # Step 3: Query the knowledge base
    # This uses QueryMixin.aquery
    result = await rag.aquery(
        "What are the main findings in the document?",
        mode="hybrid"
    )
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

Sources: [README.md:323-457]()

### Key Method Reference

| Method | Purpose | Source |
| :--- | :--- | :--- |
| `process_document_complete()` | Parse and process a document into the knowledge base | [README.md:428-457]() |
| `aquery()` | Execute a text-based query | [README.md:604-616]() |
| `aquery_with_multimodal()` | Execute a query with images/tables/equations | [README.md:648-672]() |
| `process_folder_complete()` | Batch process multiple documents in a directory | [README.md:577-603]() |

For detailed API documentation, see [RAGAnything Class](#10.1) and [Query Methods API](#10.5).

---

## Query Modes Explained

RAG-Anything supports four query modes inherited from LightRAG:

1.  **`hybrid`**: Default mode. Combines vector similarity with graph relationships for comprehensive retrieval. Recommended for most use cases.
2.  **`local`**: Focuses on specific entities and their immediate neighbors. Best when you know the exact entity you're querying about.
3.  **`global`**: Traverses the entire knowledge graph for high-level understanding. Best for broad, summarization-style questions.
4.  **`naive`**: Simple vector-based search without graph traversal. Fastest but may miss contextual relationships.

Sources: [README.md:604-616]()

---

## Next Steps

Now that you have RAG-Anything running, explore these topics:

### Core Functionality
*   **[Installation](#2.1)**: Detailed installation instructions and troubleshooting.
*   **[Environment Configuration](#2.3)**: Complete environment variable reference and configuration options.
*   **[Quick Start Example](#2.2)**: Comprehensive end-to-end examples.

### Advanced Features
*   **[Multimodal Content Processing](#5)**: Process images, tables, and equations with specialized processors.
*   **[Query System](#7)**: Advanced query modes including VLM-enhanced queries.
*   **[Batch Processing](#4.5)**: Concurrent processing of multiple documents using `BatchMixin`.

### Configuration & Deployment
*   **[Storage Backend Configuration](#8.3)**: Configure PostgreSQL, Neo4j, Milvus, and other backends.
*   **[Model Provider Configuration](#8.4)**: Set up OpenAI, Ollama, Azure, or local models.
*   **[Offline Deployment](#11.1)**: Configure for fully offline operation with local models.

Sources: [README.md:257-672]()

---

# Page: Installation

# Installation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/pypi-publish.yml](.github/workflows/pypi-publish.yml)
- [pyproject.toml](pyproject.toml)
- [raganything/enhanced_markdown.py](raganything/enhanced_markdown.py)
- [requirements.txt](requirements.txt)
- [setup.py](setup.py)

</details>



This page covers the standard installation process for RAG-Anything, including core dependencies, optional feature packages, and external requirements like LibreOffice.

## Installation Overview

RAG-Anything is a modular system that leverages several high-performance backends for document parsing and retrieval. It is built on top of the LightRAG framework and uses MinerU as its primary parsing engine.

```mermaid
flowchart TD
    subgraph "Installation Methods"
        [pip_install] -- "Standard" --> PIP["pip install raganything"]
        [pip_extras] -- "Feature-specific" --> PIP_EXTRAS["pip install raganything[extras]"]
    end
    
    subgraph "Core Dependencies (pyproject.toml)"
        [lightrag-hku]
        [mineru_core]
        [huggingface_hub]
        [tqdm]
    end
    
    subgraph "Optional Dependencies (extras_require)"
        [image_extra] -- "Pillow" --> PILLOW["Image Conversion"]
        [text_extra] -- "reportlab" --> REPORTLAB["TXT/MD to PDF"]
        [paddle_extra] -- "paddleocr" --> PADDLE["Scanned PDF OCR"]
        [md_extra] -- "weasyprint" --> WEASY["Enhanced MD Styling"]
        [office_ext] -- "System" --> LIBRE["LibreOffice (External)"]
    end
    
    PIP --> [lightrag-hku]
    PIP --> [mineru_core]
    PIP_EXTRAS --> [image_extra]
    PIP_EXTRAS --> [paddle_extra]
    PIP_EXTRAS --> [md_extra]
```
**Installation Dependency Mapping**  
Sources: [pyproject.toml:23-51](), [setup.py:62-84](), [requirements.txt:1-7]()

## System Requirements

| Requirement | Version | Source |
|-------------|---------|---------|
| Python | >=3.10 | [pyproject.toml:14]() |
| Operating System | Cross-platform | [pyproject.toml:19]() |
| Build System | setuptools >= 64 | [pyproject.toml:2]() |

**Note**: While [setup.py:105]() mentions `python_requires=">=3.9"`, the `pyproject.toml` specification of `3.10` is the recommended minimum for modern dependency compatibility.

## Basic Installation

### Standard Installation
Install the core package which includes `lightrag-hku` for graph-based RAG and `mineru[core]` for multimodal document parsing.

```bash
pip install raganything
```
Sources: [pyproject.toml:23-28](), [requirements.txt:1-7]()

### Installation with Optional Features
RAG-Anything uses `extras_require` to manage specialized dependencies.

```bash
# For scanned PDF OCR support
pip install raganything[paddleocr]

# For image format conversion (BMP, TIFF, etc.)
pip install raganything[image]

# For enhanced Markdown to PDF styling
pip install raganything[markdown]

# Install everything
pip install raganything[all]
```
Sources: [setup.py:62-84](), [pyproject.toml:30-51]()

## Detailed Dependency Breakdown

### Core Dependencies
These are installed by default and form the backbone of the system:
*   **`lightrag-hku`**: The retrieval engine and knowledge graph framework [pyproject.toml:25]().
*   **`mineru[core]`**: Handles the "Five-Stage Processing Pipeline" for PDF and document parsing [pyproject.toml:26]().
*   **`huggingface_hub`**: Used for downloading model weights and assets [pyproject.toml:24]().

### Optional Packages (Extras)
| Extra | Packages | Purpose |
|-------|----------|---------|
| `image` | `Pillow>=10.0.0` | Format conversion for BMP, TIFF, GIF, and WebP [setup.py:63](). |
| `text` | `reportlab>=4.0.0` | Basic conversion of TXT and MD files to PDF for the parser [setup.py:64](). |
| `paddleocr` | `paddleocr`, `pypdfium2` | Better OCR accuracy for scanned PDFs [setup.py:66-69](). |
| `markdown` | `markdown`, `weasyprint`, `pygments` | High-fidelity Markdown conversion with CSS and syntax highlighting [setup.py:79-83](). |

### External Dependencies
*   **LibreOffice**: Required for processing Microsoft Office formats (DOCX, PPTX, XLSX). RAG-Anything invokes LibreOffice as an external process to convert these files to PDF before parsing [setup.py:65](), [requirements.txt:12]().

## Code Entity to Natural Language Mapping

The following diagram maps installation-related code entities to their functional roles in the setup process.

```mermaid
classDiagram
    class SetupScript["setup.py"] {
        +retrieve_metadata()
        +read_requirements()
        +extras_require
    }
    class ProjectConfig["pyproject.toml"] {
        +dependencies
        +optional-dependencies
    }
    class MarkdownConverter["raganything.enhanced_markdown.py"] {
        +WEASYPRINT_AVAILABLE
        +MARKDOWN_AVAILABLE
        +PANDOC_AVAILABLE
        +_check_backends()
    }

    SetupScript --|> ProjectConfig : "Mirroring configuration"
    MarkdownConverter ..> ProjectConfig : "Checks for [markdown] extras"
```
**Code Entity Space: Installation & Backend Detection**  
Sources: [setup.py:14-84](), [pyproject.toml:23-51](), [raganything/enhanced_markdown.py:21-43]()

## Verification and Backend Detection

RAG-Anything performs runtime checks to determine which features are available based on the installed packages. For example, the `EnhancedMarkdownConverter` class detects backends during initialization.

```python
# raganything/enhanced_markdown.py:92-94
self.available_backends = self._check_backends()
self.logger.info(f"Available backends: {list(self.available_backends.keys())}")
```

You can verify your installation by checking the availability of these backends:

```python
from raganything.enhanced_markdown import EnhancedMarkdownConverter

converter = EnhancedMarkdownConverter()
print(converter.available_backends)
# Output: {'weasyprint': True, 'pandoc': False, 'markdown': True, 'pandoc_system': False}
```
Sources: [raganything/enhanced_markdown.py:96-111]()

## Automated Build Pipeline

The project includes a GitHub Action for automated distribution to PyPI, ensuring that the `install_requires` and `extras_require` are correctly packaged.

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant GH as GitHub Actions
    participant PyPI as PyPI Repository

    Dev->>GH: Create Release
    GH->>GH: Run pypi-publish.yml
    GH->>GH: python -m build
    GH->>PyPI: Upload distributions (dist/)
```
**Deployment Workflow**  
Sources: [.github/workflows/pypi-publish.yml:21-53]()

---

# Page: Quick Start Example

# Quick Start Example

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [examples/raganything_example.py](examples/raganything_example.py)

</details>



This page provides a minimal working example demonstrating end-to-end document processing and querying with RAG-Anything. It covers the essential steps to process a document, insert it into the knowledge base, and perform different types of queries.

**Scope**: This guide assumes you have already completed installation (see [Installation](#2.1)). For detailed configuration options, see [Environment Configuration](#2.3). For comprehensive usage examples, see [Usage Examples](#9).

---

## Overview of the Basic Workflow

The following diagram illustrates the essential steps in a basic RAG-Anything workflow:

```mermaid
flowchart TB
    Setup["1. Setup Configuration<br/>(RAGAnythingConfig)"]
    Functions["2. Define Model Functions<br/>(llm_model_func, vision_model_func, embedding_func)"]
    Init["3. Initialize RAGAnything<br/>(RAGAnything instance)"]
    Process["4. Process Document<br/>(process_document_complete)"]
    Query["5. Query System<br/>(aquery / aquery_with_multimodal)"]
    
    Setup --> Functions
    Functions --> Init
    Init --> Process
    Process --> Query
```

Sources: [README.md:321-456](), [examples/raganything_example.py:89-267]()

---

## Step 1: Create Configuration

Begin by creating a `RAGAnythingConfig` instance to define the system's behavior. This class centralizes all processing parameters.

```python
from raganything import RAGAnything, RAGAnythingConfig

config = RAGAnythingConfig(
    working_dir="./rag_storage",           # Storage directory
    parser="mineru",                        # Parser: mineru, docling, or paddleocr
    parse_method="auto",                    # Parse method: auto, ocr, or txt
    enable_image_processing=True,           # Enable image analysis
    enable_table_processing=True,           # Enable table processing
    enable_equation_processing=True,        # Enable equation processing
)
```

**Configuration Architecture**:

```mermaid
graph LR
    Config["RAGAnythingConfig"]
    
    subgraph "Core Settings"
        WD["working_dir"]
        Parser["parser<br/>(mineru/docling/paddleocr)"]
        ParseMethod["parse_method<br/>(auto/ocr/txt)"]
    end
    
    subgraph "Processing Flags"
        ImgProc["enable_image_processing"]
        TblProc["enable_table_processing"]
        EqProc["enable_equation_processing"]
    end
    
    Config --> WD
    Config --> Parser
    Config --> ParseMethod
    Config --> ImgProc
    Config --> TblProc
    Config --> EqProc
```

Sources: [README.md:336-344](), [examples/raganything_example.py:109-116]()

---

## Step 2: Define Model Functions

RAG-Anything requires three function types: LLM for text generation, vision model for image analysis, and embedding for vector representations.

### LLM Model Function
The `llm_model_func` handles standard text generation tasks and entity extraction [examples/raganything_example.py:123-132]().

```python
from lightrag.llm.openai import openai_complete_if_cache

def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
    return openai_complete_if_cache(
        "gpt-4o-mini",
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        api_key="your-api-key",
        base_url="your-base-url",  # Optional
        **kwargs,
    )
```

### Vision Model Function
The `vision_model_func` is critical for multimodal features. It handles both single-image analysis during document processing and multi-image context analysis during VLM-enhanced queries [examples/raganything_example.py:135-187]().

```python
def vision_model_func(
    prompt, 
    system_prompt=None, 
    history_messages=[], 
    image_data=None, 
    messages=None, 
    **kwargs
):
    # Multimodal VLM format (for VLM-enhanced queries)
    if messages:
        return openai_complete_if_cache(
            "gpt-4o",
            "",
            system_prompt=None,
            history_messages=[],
            messages=messages,
            api_key="your-api-key",
            base_url="your-base-url",
            **kwargs,
        )
    # Single image format (for image processing)
    elif image_data:
        return openai_complete_if_cache(
            "gpt-4o",
            "",
            system_prompt=None,
            history_messages=[],
            messages=[
                {"role": "system", "content": system_prompt} if system_prompt else None,
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                        },
                    ],
                }
            ],
            api_key="your-api-key",
            base_url="your-base-url",
            **kwargs,
        )
    # Pure text fallback
    else:
        return llm_model_func(prompt, system_prompt, history_messages, **kwargs)
```

### Embedding Function
Uses `EmbeddingFunc` to wrap vector generation [examples/raganything_example.py:193-206]().

```python
from lightrag.llm.openai import openai_embed
from lightrag.utils import EmbeddingFunc

embedding_func = EmbeddingFunc(
    embedding_dim=3072,
    max_token_size=8192,
    func=lambda texts: openai_embed(
        texts,
        model="text-embedding-3-large",
        api_key="your-api-key",
        base_url="your-base-url",
    ),
)
```

**Function Injection Architecture**:

```mermaid
graph TB
    RAG["RAGAnything"]
    
    subgraph "Injected Functions"
        LLM["llm_model_func<br/>(Text Generation)"]
        Vision["vision_model_func<br/>(Image Analysis)"]
        Embed["embedding_func<br/>(Vector Embeddings)"]
    end
    
    subgraph "Usage"
        TextProc["Text Processing<br/>& Entity Extraction"]
        ImgProc["Image Processing<br/>(ImageModalProcessor)"]
        VecStore["Vector Storage<br/>(Chunks/Entities/Relations)"]
        Query["Query Processing<br/>(QueryMixin)"]
    end
    
    LLM --> RAG
    Vision --> RAG
    Embed --> RAG
    
    RAG --> TextProc
    RAG --> ImgProc
    RAG --> VecStore
    RAG --> Query
    
    LLM -.used by.-> TextProc
    Vision -.used by.-> ImgProc
    Embed -.used by.-> VecStore
    LLM -.used by.-> Query
    Vision -.used by.-> Query
```

Sources: [README.md:346-418](), [examples/raganything_example.py:119-198]()

---

## Step 3: Initialize RAGAnything

Create the `RAGAnything` instance. This class inherits from `ProcessorMixin`, `QueryMixin`, and `BatchMixin` to provide a unified interface [README.md:93-97]().

```python
import asyncio

rag = RAGAnything(
    config=config,
    llm_model_func=llm_model_func,
    vision_model_func=vision_model_func,
    embedding_func=embedding_func,
)
```

**Initialization Flow**:

```mermaid
graph TB
    Input["RAGAnything Constructor"]
    
    subgraph "Input Parameters"
        Cfg["config: RAGAnythingConfig"]
        LLM["llm_model_func"]
        Vision["vision_model_func"]
        Emb["embedding_func"]
    end
    
    subgraph "Internal Initialization"
        LightRAG["LightRAG Instance<br/>(if not provided)"]
        Storage["Storage Initialization<br/>(text_chunks, vectors, KG)"]
        Mixins["Mixin Integration<br/>(ProcessorMixin, QueryMixin)"]
    end
    
    subgraph "Ready Components"
        Parser["Parser<br/>(MinerU/Docling/PaddleOCR)"]
        Processors["Modal Processors<br/>(Image/Table/Equation)"]
        QuerySys["Query System"]
    end
    
    Cfg --> Input
    LLM --> Input
    Vision --> Input
    Emb --> Input
    
    Input --> LightRAG
    Input --> Storage
    Input --> Mixins
    
    Mixins --> Parser
    Mixins --> Processors
    Mixins --> QuerySys
```

Sources: [README.md:420-426](), [examples/raganything_example.py:200-206]()

---

## Step 4: Process a Document

Use `process_document_complete` to run the five-stage pipeline (parsing, routing, analysis, graph construction, indexing) [README.md:107-111]().

```python
await rag.process_document_complete(
    file_path="path/to/your/document.pdf",
    output_dir="./output",
    parse_method="auto"
)
```

**Document Processing Pipeline**:

```mermaid
flowchart LR
    Input["Document File"]
    
    subgraph "Stage 1: Parsing"
        ParseSelect{"Parser<br/>(mineru/docling/paddleocr)"}
        ContentList["content_list<br/>(List of Dicts)"]
    end
    
    subgraph "Stage 2-3: Processing"
        TextRoute["Text Chunks"]
        MMRoute["Multimodal Content<br/>(images/tables/equations)"]
    end
    
    subgraph "Stage 4-5: Storage"
        TextChunks["text_chunks DB"]
        ChunksVDB["chunks_vdb"]
        EntitiesVDB["entities_vdb"]
        KG["Knowledge Graph"]
    end
    
    Input --> ParseSelect
    ParseSelect --> ContentList
    ContentList --> TextRoute
    ContentList --> MMRoute
    
    TextRoute --> TextChunks
    TextRoute --> ChunksVDB
    MMRoute --> EntitiesVDB
    MMRoute --> KG
    TextRoute --> KG
```

Sources: [README.md:428-433](), [examples/raganything_example.py:208-211]()

---

## Step 5: Query the System

### Pure Text Queries
Standard text queries using `aquery()` [examples/raganything_example.py:214-222]().

```python
result = await rag.aquery(
    "What are the main findings in the document?",
    mode="hybrid"  # Options: hybrid, local, global, naive
)
print(result)
```

### Multimodal Queries
Use `aquery_with_multimodal()` for queries containing explicit new multimodal elements [examples/raganything_example.py:224-261]().

```python
# Query with table data
table_result = await rag.aquery_with_multimodal(
    "Compare these metrics with document content",
    multimodal_content=[{
        "type": "table",
        "table_data": "Method,Accuracy\nRAGAnything,95.2%",
        "table_caption": "Performance comparison"
    }],
    mode="hybrid"
)
```

### VLM-Enhanced Queries
If `vision_model_func` is configured, RAG-Anything automatically detects images in the retrieved context and sends them to the VLM for analysis [README.md:80]().

```mermaid
graph TB
    Query["User Query"]
    
    subgraph "Query Type Selection"
        TextQ["aquery<br/>(Text Query)"]
        MMQ["aquery_with_multimodal<br/>(Explicit MM Content)"]
    end
    
    subgraph "Processing Path"
        Retrieve["Hybrid Retrieval<br/>(Vector + Graph)"]
        VLMCheck{"Images in<br/>Context?"}
        VLMProc["VLM Processing<br/>(vision_model_func)"]
        LLMGen["LLM Generation<br/>(llm_model_func)"]
    end
    
    Query --> TextQ
    Query --> MMQ
    TextQ --> Retrieve
    Retrieve --> VLMCheck
    VLMCheck -->|Yes| VLMProc
    VLMProc --> LLMGen
    VLMCheck -->|No| LLMGen
```

Sources: [README.md:435-453](), [README.md:607-672](), [examples/raganything_example.py:213-261]()

---

## Complete Working Example

A complete, runnable implementation combining the steps above:

```python
import asyncio
from raganything import RAGAnything, RAGAnythingConfig
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc

async def main():
    config = RAGAnythingConfig(
        working_dir="./rag_storage",
        parser="mineru",
        enable_image_processing=True
    )
    
    api_key = "your-api-key"
    
    def llm_model_func(prompt, **kwargs):
        return openai_complete_if_cache("gpt-4o-mini", prompt, api_key=api_key, **kwargs)
    
    def vision_model_func(prompt, image_data=None, messages=None, **kwargs):
        # Implementation logic for single image or VLM messages...
        return openai_complete_if_cache("gpt-4o", prompt, api_key=api_key, messages=messages, **kwargs)
    
    embedding_func = EmbeddingFunc(
        embedding_dim=3072, max_token_size=8192,
        func=lambda texts: openai_embed(texts, model="text-embedding-3-large", api_key=api_key)
    )
    
    rag = RAGAnything(
        config=config,
        llm_model_func=llm_model_func,
        vision_model_func=vision_model_func,
        embedding_func=embedding_func
    )
    
    await rag.process_document_complete(file_path="sample.pdf", output_dir="./out")
    
    print(await rag.aquery("Summarize the charts", mode="hybrid"))

if __name__ == "__main__":
    asyncio.run(main())
```

Sources: [README.md:321-456](), [examples/raganything_example.py:1-331]()

---

# Page: Environment Configuration

# Environment Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [env.example](env.example)
- [examples/lmstudio_integration_example.py](examples/lmstudio_integration_example.py)
- [raganything/config.py](raganything/config.py)

</details>



## Purpose and Scope

This page explains the basic environment configuration required to get RAG-Anything operational. It covers essential API keys, directory paths, and fundamental settings needed for initial system setup, primarily focusing on the interaction between the `.env` file and the `RAGAnythingConfig` class.

For comprehensive configuration options including all environment variables, see [Environment Variables](#8.2). For storage backend configuration details, see [Storage Backend Configuration](#8.3). For model provider configuration, see [Model Provider Configuration](#8.4). For complete `RAGAnythingConfig` parameter reference, see [RAGAnythingConfig](#8.1).

## Configuration Architecture

RAG-Anything uses a three-tier configuration system that combines environment variables, configuration objects, and runtime parameters. The `RAGAnythingConfig` class acts as the central hub for document processing settings, utilizing the `get_env_value` utility to bridge system environment variables to code entities.

### Configuration Data Flow

The following diagram illustrates how configuration flows from raw environment variables into the `RAGAnything` system components.

```mermaid
graph TB
    subgraph "Configuration Sources"
        ENV_FILE[".env File"]
        ENV_VARS["Environment Variables"]
        CLI["Command Line Arguments"]
    end
    
    subgraph "Configuration Loading"
        LOAD_ENV["load_dotenv()<br/>Loads .env into environment"]
        ENV_MODULE["lightrag/utils.py<br/>get_env_value()"]
    end
    
    subgraph "Configuration Objects"
        RAG_CONFIG["RAGAnythingConfig<br/>raganything/config.py"]
        LIGHTRAG_PARAMS["LightRAG Parameters<br/>working_dir, llm_model_func, etc."]
    end
    
    subgraph "Runtime Application"
        RAG_INIT["RAGAnything.__init__()<br/>Applies configuration"]
        PROCESS_DOCS["ProcessorMixin<br/>Uses parser, modal processors"]
        QUERY_SYS["QueryMixin<br/>Uses retrieval settings"]
        STORAGE["Storage Backends<br/>PostgreSQL, Neo4j, etc."]
    end
    
    ENV_FILE --> LOAD_ENV
    ENV_VARS --> ENV_MODULE
    CLI --> RAG_CONFIG
    
    LOAD_ENV --> ENV_MODULE
    ENV_MODULE --> RAG_CONFIG
    ENV_MODULE --> LIGHTRAG_PARAMS
    ENV_MODULE --> STORAGE
    
    RAG_CONFIG --> RAG_INIT
    LIGHTRAG_PARAMS --> RAG_INIT
    
    RAG_INIT --> PROCESS_DOCS
    RAG_INIT --> QUERY_SYS
    RAG_INIT --> STORAGE
```

**Sources:** [env.example:1-212](), [raganything/config.py:1-116]()

## Configuration Sources

### Environment Variables via `.env` File

The primary configuration method uses a `.env` file in the project root. The `env.example` file provides a comprehensive template including server settings, multimodal processing flags, and storage connection strings.

```bash
cp env.example .env
# Edit .env with your settings
```

**Sources:** [env.example:1-212]()

### Programmatic Configuration

Configuration is encapsulated in the `RAGAnythingConfig` dataclass. This class supports environment variable detection for all fields via `get_env_value`.

```python
from raganything.config import RAGAnythingConfig

config = RAGAnythingConfig(
    working_dir="./rag_storage",
    parser="mineru",
    parse_method="auto",
    enable_image_processing=True,
    enable_table_processing=True,
    enable_equation_processing=True
)
```

**Sources:** [raganything/config.py:13-116]()

### Configuration Priority

When the same setting is specified in multiple places, the priority order is:

1. **Runtime Parameters**: Passed directly to methods like `process_document_complete`.
2. **RAGAnythingConfig Object**: The instance passed to the `RAGAnything` constructor.
3. **Environment Variables**: Values retrieved from `.env` or the system shell.
4. **Default Values**: Hardcoded defaults in `RAGAnythingConfig` (e.g., `parser="mineru"`).

**Sources:** [raganything/config.py:18-115]()

## Essential Configuration

### API Keys and Authentication

API keys are required for AI model services and are typically defined in the `.env` file.

| Environment Variable | Purpose | Code Reference |
|---------------------|---------|--------------|
| `LLM_BINDING_API_KEY` | Authentication for LLM | [env.example:122]() |
| `EMBEDDING_BINDING_API_KEY` | Authentication for Embeddings | [env.example:139]() |
| `LIGHTRAG_API_KEY` | Security for the LightRAG Server API | [env.example:27]() |
| `TOKEN_SECRET` | Secret for JWT generation | [env.example:21]() |

### Directory Configuration

These settings define where the system reads inputs and persists data.

| Environment Variable | `RAGAnythingConfig` Field | Default |
|---------------------|---------------------------|---------|
| `WORKING_DIR` | `working_dir` | `./rag_storage` |
| `OUTPUT_DIR` | `parser_output_dir` | `./output` |
| `INPUT_DIR` | N/A (Server level) | `./inputs` |
| `TIKTOKEN_CACHE_DIR` | N/A (Offline mode) | N/A |

**Sources:** [raganything/config.py:18-27](), [env.example:17-38]()

### LLM and Embedding Configuration

The system uses a binding system to interface with various providers.

```mermaid
graph LR
    subgraph "Model Configuration (env.example)"
        LLM_B["LLM_BINDING"]
        LLM_M["LLM_MODEL"]
        LLM_H["LLM_BINDING_HOST"]
        LLM_K["LLM_BINDING_API_KEY"]
    end
    
    subgraph "Internal Functions (lmstudio_integration_example.py)"
        LLM_FUNC["lmstudio_llm_model_func"]
        EMB_FUNC["lmstudio_embedding_async"]
    end
    
    LLM_B --> LLM_FUNC
    LLM_M --> LLM_FUNC
    LLM_H --> LLM_FUNC
    LLM_K --> LLM_FUNC
    
    LLM_FUNC --> RAG_A["RAGAnything Instance"]
    EMB_FUNC --> RAG_A
```

**Example local configuration (LM Studio):**
```bash
LLM_BINDING=lmstudio
LLM_MODEL=openai/gpt-oss-20b
LLM_BINDING_HOST=http://localhost:1234/v1
LLM_BINDING_API_KEY=lm-studio
```

**Sources:** [env.example:117-122](), [examples/lmstudio_integration_example.py:39-43]()

## Parser and Processing Configuration

### Parser Selection and Strategy

The `RAGAnythingConfig` manages which parser backend is used for document extraction.

| Variable | Values | Code Entity |
|----------|--------|-------------|
| `PARSER` | `mineru`, `docling`, `paddleocr` | `RAGAnythingConfig.parser` |
| `PARSE_METHOD` | `auto`, `ocr`, `txt` | `RAGAnythingConfig.parse_method` |

**Backward Compatibility:** The class includes a `__post_init__` hook that maps the legacy `MINERU_PARSE_METHOD` to the new `parse_method` field, issuing a `DeprecationWarning` if the old variable is detected.

**Sources:** [raganything/config.py:23-30](), [raganything/config.py:117-130]()

### Multimodal Processing Flags

Processing of specific document elements can be toggled via boolean flags in `RAGAnythingConfig`:
* `enable_image_processing`: Default `True` ([raganything/config.py:39]())
* `enable_table_processing`: Default `True` ([raganything/config.py:44]())
* `enable_equation_processing`: Default `True` ([raganything/config.py:49]())

### Context Extraction Settings

These settings define how much surrounding text is provided to multimodal processors (like vision models for images).

* `CONTEXT_WINDOW`: Number of adjacent pages/chunks ([raganything/config.py:80]())
* `CONTEXT_MODE`: `'page'` or `'chunk'` ([raganything/config.py:83]())
* `MAX_CONTEXT_TOKENS`: Hard limit on context length ([raganything/config.py:86]())

## Storage Backend Configuration

Storage is configured by selecting specific class names for the LightRAG storage interface.

| Category | Env Variable | Options |
|----------|--------------|---------|
| Key-Value | `LIGHTRAG_KV_STORAGE` | `PGKVStorage`, `MongoKVStorage` |
| Vector | `LIGHTRAG_VECTOR_STORAGE` | `PGVectorStorage`, `MilvusVectorStorage` |
| Status | `LIGHTRAG_DOC_STATUS_STORAGE` | `PGDocStatusStorage` |
| Graph | `LIGHTRAG_GRAPH_STORAGE` | `Neo4JStorage`, `NetworkXStorage` |

**Sources:** [env.example:152-156](), [env.example:167-212]()

## Performance and Concurrency Settings

Concurrency is managed through multiple variables to balance throughput and API rate limits.

* `MAX_ASYNC`: Max concurrent LLM requests (Default: 4) ([env.example:113]())
* `MAX_PARALLEL_INSERT`: Max parallel document insertions (Default: 2) ([env.example:100]())
* `MAX_CONCURRENT_FILES`: Max files processed in batch (Default: 1) ([raganything/config.py:56]())
* `EMBEDDING_FUNC_MAX_ASYNC`: Max concurrent embedding requests (Default: 16) ([env.example:145]())

## Configuration Loading Process

The configuration loading process follows this sequence:

```mermaid
sequenceDiagram
    participant OS as "System Environment / .env"
    participant CFG as "RAGAnythingConfig"
    participant RAG as "RAGAnything Instance"
    
    OS->>CFG: get_env_value("PARSER")
    CFG->>CFG: __post_init__() (Check Deprecations)
    Note over CFG: Holds validated settings
    
    RAG->>CFG: Read working_dir
    RAG->>OS: Read LIGHTRAG_KV_STORAGE
    Note over RAG: _ensure_lightrag_initialized()
```

**Sources:** [raganything/config.py:117-130](), [env.example:152-156]()

---

# Page: System Architecture

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [raganything/raganything.py](raganything/raganything.py)

</details>



## Purpose and Scope

This document describes the overall system architecture of RAG-Anything, including its component organization, class structure, design patterns, and data flow. It explains how the various modules work together to provide an all-in-one multimodal RAG framework built on top of LightRAG.

For detailed information about specific subsystems, see:
- Component-level details: [Component Overview](#3.1)
- Processing pipeline stages: [Five-Stage Processing Pipeline](#3.2)
- LightRAG integration specifics: [LightRAG Integration](#3.3)
- Document processing internals: [Document Processing](#4)
- Multimodal processing details: [Multimodal Content Processing](#5)
- Query system implementation: [Query System](#7)

---

## Architectural Overview

RAG-Anything is architected as a **modular, mixin-based system** that extends LightRAG with multimodal document processing capabilities. The architecture follows a layered design pattern where high-level orchestration is separated from specialized processing logic through composition.

### Core Design Philosophy

The system is designed around these key architectural principles:

1. **Dependency Injection**: Model functions (LLM, VLM, embedding) are injected as callables, allowing flexible backend configuration [raganything/raganything.py:59-66]().
2. **Mixin-Based Composition**: Major functionality areas (query, processing, batch) are separated into mixins [raganything/raganything.py:51]().
3. **Storage Abstraction**: Leverages LightRAG's storage layer for persistence, with added parse caching [raganything/raganything.py:94-98]().
4. **Extensibility**: Modal processors follow a base class pattern for easy extension [raganything/modalprocessors.py:112-114]().
5. **Lazy Initialization**: LightRAG and processors are initialized on first use to support both pre-configured and on-demand setup [raganything/raganything.py:231-233]().

Sources: [README.md:93-113](), [raganything/raganything.py:1-586]()

---

## Core Class Architecture

### RAGAnything Main Class

The `RAGAnything` class serves as the central orchestrator and is defined as a dataclass that composes three mixin classes:

```mermaid
graph TB
    subgraph "RAGAnything Class Structure"
        RA["RAGAnything<br/>raganything.py:51"]
        
        QM["QueryMixin<br/>query.py"]
        PM["ProcessorMixin<br/>processor.py"]
        BM["BatchMixin<br/>batch.py"]
        
        RA -.inherits.-> QM
        RA -.inherits.-> PM
        RA -.inherits.-> BM
    end
    
    subgraph "Core Components"
        LR["lightrag: LightRAG<br/>Field"]
        LLM["llm_model_func: Callable<br/>Field"]
        VLM["vision_model_func: Callable<br/>Field"]
        EMB["embedding_func: Callable<br/>Field"]
        CFG["config: RAGAnythingConfig<br/>Field"]
    end
    
    subgraph "Internal State"
        MP["modal_processors: Dict<br/>Field init=False"]
        CE["context_extractor: ContextExtractor<br/>Field init=False"]
        PC["parse_cache: KVStorage<br/>Field init=False"]
        DP["doc_parser: Parser<br/>Initialized in __post_init__"]
    end
    
    RA --> LR
    RA --> LLM
    RA --> VLM
    RA --> EMB
    RA --> CFG
    RA --> MP
    RA --> CE
    RA --> PC
    RA --> DP
```

**Diagram: RAGAnything Class Composition and Fields**

The `RAGAnything` class uses Python dataclass fields to manage its components:

- **Core Components** (Lines 56-73): Optional fields that can be provided at initialization [raganything/raganything.py:56-73]().
- **Internal State** (Lines 88-103): Fields initialized during `__post_init__` or lazy initialization [raganything/raganything.py:88-103]().
- **Mixins**: Provide method collections for specific functional areas [raganything/raganything.py:51]().

Sources: [raganything/raganything.py:49-106]()

---

### Mixin-Based Method Distribution

Each mixin contributes a specific set of methods to the `RAGAnything` class:

| Mixin Class | File | Primary Responsibilities | Key Methods |
|------------|------|-------------------------|-------------|
| `QueryMixin` | `raganything/query.py` | Query processing and retrieval | `aquery()`, `aquery_with_multimodal()`, `aquery_vlm_enhanced()` |
| `ProcessorMixin` | `raganything/processor.py` | Document parsing and content insertion | `parse_document()`, `process_document_complete()`, `insert_content_list()` |
| `BatchMixin` | `raganything/batch.py` | Concurrent multi-document processing | `process_folder_complete()`, `process_documents_batch()` |

This separation allows each functional area to be developed and tested independently while still being accessible through the unified `RAGAnything` interface.

Sources: [raganything/raganything.py:32-34]()

---

## Component Layer Architecture

The system is organized into distinct layers, each with specific responsibilities:

```mermaid
graph TB
    subgraph "Layer 1: Configuration & Entry Points"
        INIT["__init__.py<br/>Package Exports"]
        CFG_CLASS["RAGAnythingConfig<br/>config.py"]
        ENV["Environment Variables<br/>.env file"]
    end
    
    subgraph "Layer 2: Core Orchestration"
        RA_CLASS["RAGAnything<br/>raganything.py:51<br/>@dataclass"]
        POST_INIT["__post_init__<br/>raganything.py:108"]
        ENSURE["_ensure_lightrag_initialized<br/>raganything.py:231"]
        INIT_PROC["_initialize_processors<br/>raganything.py:177"]
    end
    
    subgraph "Layer 3: Functional Mixins"
        QUERY_M["QueryMixin<br/>query.py"]
        PROC_M["ProcessorMixin<br/>processor.py"]
        BATCH_M["BatchMixin<br/>batch.py"]
    end
    
    subgraph "Layer 4: Parsing Subsystem"
        PARSER_BASE["Parser (ABC)<br/>parser.py"]
        MINERU["MineruParser<br/>parser.py"]
        DOCLING["DoclingParser<br/>parser.py"]
    end
    
    subgraph "Layer 5: Modal Processing"
        BASE_MP["BaseModalProcessor<br/>modalprocessors.py"]
        IMG_MP["ImageModalProcessor<br/>modalprocessors.py"]
        TBL_MP["TableModalProcessor<br/>modalprocessors.py"]
        EQ_MP["EquationModalProcessor<br/>modalprocessors.py"]
        GEN_MP["GenericModalProcessor<br/>modalprocessors.py"]
        CTX_EXT["ContextExtractor<br/>modalprocessors.py"]
    end
    
    subgraph "Layer 6: LightRAG Foundation"
        LR_CLASS["LightRAG<br/>External Framework"]
        KG["Knowledge Graph<br/>Neo4j/AGE"]
        VDB["Vector Database<br/>pgvector/Milvus/Qdrant"]
        KVDB["KV Storage<br/>PostgreSQL/MongoDB"]
    end
    
    INIT --> RA_CLASS
    CFG_CLASS --> RA_CLASS
    ENV --> CFG_CLASS
    
    RA_CLASS --> POST_INIT
    POST_INIT --> ENSURE
    ENSURE --> INIT_PROC
    
    RA_CLASS -.composes.-> QUERY_M
    RA_CLASS -.composes.-> PROC_M
    RA_CLASS -.composes.-> BATCH_M
    
    POST_INIT --> PARSER_BASE
    PARSER_BASE --> MINERU
    PARSER_BASE --> DOCLING
    
    INIT_PROC --> BASE_MP
    BASE_MP --> IMG_MP
    BASE_MP --> TBL_MP
    BASE_MP --> EQ_MP
    BASE_MP --> GEN_MP
    INIT_PROC --> CTX_EXT
    
    ENSURE --> LR_CLASS
    LR_CLASS --> KG
    LR_CLASS --> VDB
    LR_CLASS --> KVDB
```

**Diagram: Layered Component Architecture with Initialization Flow**

### Layer Descriptions

**Layer 1: Configuration & Entry Points**
- `__init__.py` exports `RAGAnything` and `RAGAnythingConfig` classes.
- `RAGAnythingConfig` reads environment variables and provides default values.

**Layer 2: Core Orchestration**
- `RAGAnything` class orchestrates all components through its lifecycle methods.
- `__post_init__` (line 108): Sets up working directory, logger, and parser [raganything/raganything.py:108-142]().
- `_ensure_lightrag_initialized` (line 231): Lazy initialization of LightRAG instance [raganything/raganything.py:231-369]().
- `_initialize_processors` (line 177): Creates modal processors with appropriate model functions [raganything/raganything.py:177-221]().

**Layer 3: Functional Mixins**
- Each mixin provides a focused set of methods for retrieval, processing, and batching.

**Layer 4: Parsing Subsystem**
- Abstract `Parser` base class defines the parsing interface [raganything/parser.py:61]().
- `MineruParser` and `DoclingParser` implement format-specific parsing logic.

**Layer 5: Modal Processing**
- `BaseModalProcessor` defines the processing interface and entity creation logic [raganything/modalprocessors.py:112]().
- Specialized processors (Image, Table, Equation) inherit from `GenericModalProcessor` [raganything/modalprocessors.py:356-430]().

**Layer 6: LightRAG Foundation**
- LightRAG handles knowledge graph construction, vector storage, and retrieval [raganything/raganything.py:27]().

Sources: [raganything/raganything.py:99-221](), [raganything/config.py](), [raganything/modalprocessors.py]()

---

## Initialization and Data Flow

### Initialization Sequence

The system follows a specific initialization sequence to ensure all components are properly configured:

```mermaid
sequenceDiagram
    participant User
    participant RAGAnything
    participant __post_init__
    participant _ensure_lightrag_initialized
    participant LightRAG
    participant _initialize_processors
    participant ModalProcessors
    
    User->>RAGAnything: RAGAnything(config, llm_func, ...)
    RAGAnything->>__post_init__: Execute post-init
    __post_init__->>__post_init__: Set working_dir, logger
    __post_init__->>__post_init__: Create doc_parser (MineruParser/DoclingParser)
    __post_init__->>__post_init__: Register atexit cleanup
    __post_init__-->>User: Return initialized instance
    
    User->>RAGAnything: process_document_complete(file_path)
    RAGAnything->>_ensure_lightrag_initialized: Check/initialize LightRAG
    
    alt LightRAG not provided
        _ensure_lightrag_initialized->>LightRAG: LightRAG(working_dir, llm_func, ...)
        LightRAG->>LightRAG: initialize_storages()
        _ensure_lightrag_initialized->>_ensure_lightrag_initialized: Create parse_cache
    else LightRAG provided
        _ensure_lightrag_initialized->>LightRAG: initialize_storages() if needed
        _ensure_lightrag_initialized->>_ensure_lightrag_initialized: Inherit llm_model_func, embedding_func
    end
    
    _ensure_lightrag_initialized->>_initialize_processors: Initialize modal processors
    _initialize_processors->>_initialize_processors: Create ContextExtractor
    _initialize_processors->>ModalProcessors: Create ImageModalProcessor
    _initialize_processors->>ModalProcessors: Create TableModalProcessor
    _initialize_processors->>ModalProcessors: Create EquationModalProcessor
    _initialize_processors->>ModalProcessors: Create GenericModalProcessor
    _initialize_processors-->>RAGAnything: Processors ready
    
    RAGAnything-->>User: Ready for processing
```

**Diagram: Component Initialization Sequence**

### Key Initialization Steps

1. **`__post_init__` (raganything.py:108-142)**
   - Creates working directory if it doesn't exist [raganything/raganything.py:127-129]().
   - Selects parser based on `config.parser` [raganything/raganything.py:121]().
   - Registers cleanup handler via `atexit` [raganything/raganything.py:124]().

2. **`_ensure_lightrag_initialized` (raganything.py:231-369)**
   - Called lazily on first processing operation.
   - Checks parser installation before proceeding [raganything/raganything.py:234-239]().
   - Initializes parse cache using LightRAG's KV storage [raganything/raganything.py:285-291]().

3. **`_initialize_processors` (raganything.py:177-221)**
   - Creates `ContextExtractor` with tokenizer from LightRAG [raganything/raganything.py:180-184]().
   - Instantiates modal processors based on configuration flags (Image, Table, Equation) [raganything/raganything.py:186-221]().

Sources: [raganything/raganything.py:99-221](), [raganything/raganything.py:231-369]()

---

## Storage Architecture

### Multi-Layer Storage System

RAG-Anything uses a multi-layer storage approach built on top of LightRAG's storage abstractions:

```mermaid
graph TB
    subgraph "RAGAnything Storage Layer"
        PC["parse_cache<br/>KVStorage namespace='parse_cache'"]
    end
    
    subgraph "LightRAG Storage Layers"
        KV["key_string_value_json_storage_cls<br/>KV Store for chunks and metadata"]
        VEC["vector_storage<br/>Vector embeddings"]
        GRAPH["graph_storage<br/>Knowledge graph entities/relations"]
        DOC["doc_status_storage<br/>Document processing status"]
    end
    
    subgraph "Backend Storage Engines"
        PG["PostgreSQL<br/>KV, Vector, Graph"]
        NEO4J["Neo4j<br/>Graph-only"]
        MILVUS["Milvus<br/>Vector-only"]
        QDRANT["Qdrant<br/>Vector-only"]
        MONGO["MongoDB<br/>KV-only"]
    end
    
    PC -.stored in.-> KV
    
    KV --> PG
    VEC --> PG
    VEC --> MILVUS
    VEC --> QDRANT
    GRAPH --> PG
    GRAPH --> NEO4J
    DOC --> PG
    DOC --> MONGO
```

**Diagram: Storage Layer Architecture**

### Parse Cache Implementation

The parse cache is implemented using LightRAG's KV storage system:

- **Namespace**: `"parse_cache"` [raganything/raganything.py:285]().
- **Purpose**: Stores parsed document results to avoid redundant parsing.
- **Initialization**: Created in `_ensure_lightrag_initialized` after LightRAG setup [raganything/raganything.py:285-291]().

Sources: [raganything/raganything.py:285-291](), [raganything/raganything.py:345-351]()

---

## Resource Cleanup

The system implements proper resource cleanup through `atexit` registration and explicit finalization:

- **`atexit` Registration**: The `close` method is registered in `__post_init__` [raganything/raganything.py:124]().
- **`finalize_storages`**: Asynchronously closes all storage backends (LightRAG, parse cache, and status cache) [raganything/raganything.py:371-415]().
- **Async Safety**: The `close` method detects if an event loop is running to safely schedule cleanup [raganything/raganything.py:143-175]().

Sources: [raganything/raganything.py:124](), [raganything/raganything.py:143-175](), [raganything/raganything.py:371-415]()

---

# Page: Component Overview

# Component Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [raganything/__init__.py](raganything/__init__.py)
- [raganything/base.py](raganything/base.py)
- [raganything/raganything.py](raganything/raganything.py)

</details>



This document describes the main architectural components of RAG-Anything and their responsibilities. It provides a technical overview of the system's modular design, focusing on the `RAGAnything` class, mixin architecture, processors, parsers, and storage integration.

---

## Purpose and Scope

This page covers the structural components that make up the RAG-Anything system:

- **Core orchestrator**: The `RAGAnything` class and its initialization pattern.
- **Mixin architecture**: Modular functionality through `QueryMixin`, `ProcessorMixin`, and `BatchMixin`.
- **Configuration system**: `RAGAnythingConfig` and environment-based setup.
- **Parser abstraction**: Document parsing through `MineruParser`, `DoclingParser`, and `PaddleOCRParser`.
- **Modal processors**: Specialized content handlers for images, tables, equations.
- **Storage integration**: LightRAG-based knowledge graph and vector storage.
- **Dependency injection**: Model function binding pattern for LLM, VLM, and Embeddings.

---

## Component Architecture Overview

The following diagram shows the primary components and their relationships using actual class names from the codebase:

**Figure 1: System Component Map**
```mermaid
graph TB
    subgraph "Core_Orchestration_Layer"
        RAGAnything["RAGAnything<br/>(raganything/raganything.py)"]
        RAGAnythingConfig["RAGAnythingConfig<br/>(raganything/config.py)"]
    end
    
    subgraph "Mixin_Functionality"
        QueryMixin["QueryMixin<br/>(raganything/query.py)"]
        ProcessorMixin["ProcessorMixin<br/>(raganything/processor.py)"]
        BatchMixin["BatchMixin<br/>(raganything/batch.py)"]
    end
    
    subgraph "Document_Parsing"
        Parser["Parser (Base Class)"]
        MineruParser["MineruParser"]
        DoclingParser["DoclingParser"]
        PaddleOCRParser["PaddleOCRParser"]
    end
    
    subgraph "Multimodal_Processing"
        BaseModalProcessor["BaseModalProcessor"]
        ImageModalProcessor["ImageModalProcessor"]
        TableModalProcessor["TableModalProcessor"]
        EquationModalProcessor["EquationModalProcessor"]
        GenericModalProcessor["GenericModalProcessor"]
        ContextExtractor["ContextExtractor"]
    end
    
    subgraph "Storage_&_Knowledge_Graph"
        LightRAG["LightRAG Instance"]
        ParseCache["parse_cache<br/>(KV Storage)"]
        DocStatus["doc_status_storage<br/>(KV Storage)"]
    end
    
    subgraph "External_Dependencies"
        llm_model_func["llm_model_func<br/>(User-provided)"]
        vision_model_func["vision_model_func<br/>(User-provided)"]
        embedding_func["embedding_func<br/>(User-provided)"]
    end
    
    RAGAnything -->|inherits| QueryMixin
    RAGAnything -->|inherits| ProcessorMixin
    RAGAnything -->|inherits| BatchMixin
    RAGAnything -->|configured_by| RAGAnythingConfig
    RAGAnything -->|initializes| LightRAG
    RAGAnything -->|creates| ParseCache
    
    RAGAnything -->|selects_via_get_parser| Parser
    Parser -->|implemented_by| MineruParser
    Parser -->|implemented_by| DoclingParser
    Parser -->|implemented_by| PaddleOCRParser
    
    RAGAnything -->|creates| ImageModalProcessor
    RAGAnything -->|creates| TableModalProcessor
    RAGAnything -->|creates| EquationModalProcessor
    RAGAnything -->|creates| GenericModalProcessor
    RAGAnything -->|creates| ContextExtractor
    
    ImageModalProcessor -->|inherits| BaseModalProcessor
    TableModalProcessor -->|inherits| BaseModalProcessor
    EquationModalProcessor -->|inherits| BaseModalProcessor
    GenericModalProcessor -->|inherits| BaseModalProcessor
    
    BaseModalProcessor -->|writes_to| LightRAG
    ProcessorMixin -->|uses| LightRAG
    QueryMixin -->|queries| LightRAG
    
    ImageModalProcessor -->|uses| ContextExtractor
    TableModalProcessor -->|uses| ContextExtractor
    EquationModalProcessor -->|uses| ContextExtractor
    
    RAGAnything -->|injects| llm_model_func
    RAGAnything -->|injects| vision_model_func
    RAGAnything -->|injects| embedding_func
    
    ImageModalProcessor -->|calls| vision_model_func
    TableModalProcessor -->|calls| llm_model_func
    EquationModalProcessor -->|calls| llm_model_func
    
    LightRAG -->|manages| DocStatus
```
**Sources:** [raganything/raganything.py:49-107](), [raganything/__init__.py:1-68](), [raganything/base.py:4-13]()

---

## RAGAnything: Central Orchestrator

The `RAGAnything` class serves as the system's main entry point and orchestrator. It is implemented as a dataclass that inherits functionality from three mixins.

### Class Structure

**Figure 2: RAGAnything Class Inheritance and Members**
```mermaid
classDiagram
    class RAGAnything {
        +LightRAG lightrag
        +Callable llm_model_func
        +Callable vision_model_func
        +Callable embedding_func
        +RAGAnythingConfig config
        +Dict lightrag_kwargs
        +Dict modal_processors
        +ContextExtractor context_extractor
        +Any parse_cache
        +str working_dir
        +Parser doc_parser
        +CallbackManager callback_manager
        
        +__post_init__()
        +close()
        +_ensure_lightrag_initialized()
        +_initialize_processors()
        +finalize_storages()
        +check_parser_installation()
        +get_processor_info()
    }
    
    class QueryMixin {
        +aquery()
        +aquery_with_multimodal()
        +aquery_vlm_enhanced()
    }
    
    class ProcessorMixin {
        +parse_document()
        +process_document_complete()
        +insert_content_list()
    }
    
    class BatchMixin {
        +process_folder_complete()
        +process_documents_batch()
    }
    
    RAGAnything --|> QueryMixin
    RAGAnything --|> ProcessorMixin
    RAGAnything --|> BatchMixin
```

### Key Responsibilities

| Responsibility | Implementation Location | Description |
|---|---|---|
| Configuration management | [raganything/raganything.py:110-112]() | Loads and validates `RAGAnythingConfig` |
| LightRAG lifecycle | [raganything/raganything.py:231-369]() | Initializes or reuses LightRAG instance |
| Parser selection | [raganything/raganything.py:121-121]() | Chooses between `MineruParser`, `DoclingParser`, or `PaddleOCRParser` via `get_parser()` |
| Processor initialization | [raganything/raganything.py:177-221]() | Creates modal processors based on config |
| Resource cleanup | [raganything/raganything.py:124-124](), [raganything/raganything.py:143-172]() | Manages storage finalization via `atexit` and `finalize_storages()` |
| Context extraction setup | [raganything/raganything.py:154-175]() | Configures `ContextExtractor` for processors |

### Initialization Pattern

The initialization follows a lazy pattern where LightRAG and processors are created on first use (e.g., during document processing or querying):

1. **Instantiation**: `__init__` sets up basic configuration and identifies the parser.
2. **Post-Init**: `__post_init__` prepares the working directory and logs the configuration [raganything/raganything.py:108-141]().
3. **Lazy Setup**: Methods like `process_document_complete` call `_ensure_lightrag_initialized()` [raganything/raganything.py:231-245](), which sets up storage backends and modal processors.

**Sources:** [raganything/raganything.py:49-152](), [raganything/raganything.py:231-369]()

---

## Mixin Architecture

RAG-Anything uses a mixin pattern to modularize functionality into three distinct concerns:

### Component Breakdown

| Mixin | File | Primary Methods | Responsibility |
|---|---|---|---|
| `QueryMixin` | `raganything/query.py` | `aquery()`, `aquery_with_multimodal()`, `aquery_vlm_enhanced()` | Query interface to LightRAG with multimodal support and VLM-enhanced retrieval. |
| `ProcessorMixin` | `raganything/processor.py` | `process_document_complete()`, `insert_content_list()`, `parse_document()` | Core document parsing, text insertion, and multimodal content routing. |
| `BatchMixin` | `raganything/batch.py` | `process_folder_complete()`, `process_documents_batch()` | Concurrent processing of multiple documents and folder traversal. |

This design allows:
- **Separation of concerns**: Each mixin handles a distinct aspect of functionality.
- **Shared state access**: All mixins operate on the same `lightrag`, `modal_processors`, and `parse_cache` instances defined in the `RAGAnything` dataclass [raganything/raganything.py:49-107]().
- **Composition**: Functionality is added through multiple inheritance rather than deep hierarchies.

**Sources:** [raganything/raganything.py:49-51](), [raganything/__init__.py:1-68]()

---

## Configuration System

The `RAGAnythingConfig` class provides a centralized configuration interface that can be initialized from environment variables or constructor parameters.

### Key Configuration Fields

| Field | Type | Default | Purpose |
|---|---|---|---|
| `working_dir` | `str` | `"./rag_storage"` | Base directory for all storage [raganything/raganything.py:115-115](). |
| `parser` | `str` | `"mineru"` | Parser selection: `"mineru"`, `"docling"`, or `"paddleocr"` [raganything/raganything.py:134-134](). |
| `parse_method` | `str` | `"auto"` | Parse method: `"auto"`, `"ocr"`, or `"txt"` [raganything/raganything.py:135-135](). |
| `enable_image_processing` | `bool` | `True` | Enable `ImageModalProcessor` [raganything/raganything.py:137-137](). |
| `enable_table_processing` | `bool` | `True` | Enable `TableModalProcessor` [raganything/raganything.py:138-138](). |
| `enable_equation_processing` | `bool` | `True` | Enable `EquationModalProcessor` [raganything/raganything.py:139-139](). |
| `max_concurrent_files` | `int` | `4` | Maximum parallel document processing [raganything/raganything.py:141-141](). |

**Sources:** [raganything/raganything.py:110-141](), [raganything/config.py]()

---

## Document Parsers

RAG-Anything supports multiple document parsers through a unified `Parser` interface.

### Parser Selection Logic

The parser is selected at initialization using the `get_parser()` function based on configuration [raganything/raganything.py:121-121]().

| Parser | Description |
|---|---|
| `MineruParser` | High-fidelity extraction using MinerU, supporting PDF, Office, and images. |
| `DoclingParser` | Structure-aware parsing using Docling, optimized for Office and PDF. |
| `PaddleOCRParser` | OCR-focused parsing using PaddleOCR for images and scanned PDFs. |

### Format Conversion
Both `MineruParser` and `PaddleOCRParser` include automatic format conversion (e.g., Office to PDF via LibreOffice, Text to PDF via ReportLab) to normalize inputs before parsing.

**Sources:** [raganything/raganything.py:121-121](), [raganything/parser.py]()

---

## Modal Processors

Modal processors are specialized components that analyze and create knowledge graph entities from specific content types.

### Processor Initialization

Modal processors are created by `RAGAnything._initialize_processors()` based on configuration flags [raganything/raganything.py:177-221]().

| Processor | Content Types | Model Function | Output |
|---|---|---|---|
| `ImageModalProcessor` | Images (JPG, PNG, etc.) | `vision_model_func` | Visual descriptions and entity nodes. |
| `TableModalProcessor` | Tables (Markdown) | `llm_model_func` | Semantic interpretations and statistics. |
| `EquationModalProcessor` | LaTeX equations | `llm_model_func` | Mathematical concepts and domain mappings. |
| `GenericModalProcessor` | Fallback | `llm_model_func` | Generic entity creation for unknown types. |

### ContextExtractor Integration

All processors use `ContextExtractor` to obtain surrounding content, providing semantic context to the LLM/VLM during multimodal analysis [raganything/raganything.py:154-175]().

**Sources:** [raganything/raganything.py:177-221](), [raganything/raganything.py:38-46]()

---

## Storage and LightRAG Integration

RAG-Anything builds on LightRAG's storage layer and extends it with additional caching.

### Storage Components

1. **LightRAG Instance**: Manages the core knowledge graph, vector databases, and text chunks [raganything/raganything.py:56-57]().
2. **Parse Cache**: A specialized KV storage (namespace: `"parse_cache"`) that caches document parsing results to avoid redundant parsing [raganything/raganything.py:94-95](), [raganything/raganything.py:345-351]().
3. **Doc Status**: Tracks the processing state of documents (e.g., `READY`, `HANDLING`, `PROCESSED`) [raganything/base.py:4-13]().

### Finalization
All storage backends must be properly finalized to persist data and release resources. This is handled by `finalize_storages()` [raganything/raganything.py:371-415](), which is registered via `atexit` [raganything/raganything.py:124-124]().

**Sources:** [raganything/raganything.py:231-415](), [raganything/base.py:4-13]()

---

# Page: Five-Stage Processing Pipeline

# Five-Stage Processing Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README_zh.md](README_zh.md)
- [raganything/processor.py](raganything/processor.py)
- [tests/test_insert_content_list.py](tests/test_insert_content_list.py)

</details>



## Purpose and Scope

This document provides a technical explanation of RAG-Anything's five-stage document processing pipeline. The pipeline transforms raw documents into retrieval-ready knowledge graph structures through sequential stages: document parsing, content understanding, multimodal analysis, knowledge graph indexing, and storage.

For overall architecture context, see [Component Overview](#3.1). For detailed parsing implementation, see [Document Parsers](#4.1). For multimodal processing specifics, see [Modal Processor Architecture](#5.1). For storage configuration, see [Storage Architecture](#6.2).

---

## Pipeline Overview

The five-stage pipeline implements a transformation from unstructured documents to structured, queryable knowledge graphs. Each stage has specific input/output contracts and distinct responsibilities.

```mermaid
flowchart TB
    Input["Document Input<br/>(PDF/Office/Images/Text)"]
    
    Stage1["Stage 1: Document Parsing<br/>Parser Abstraction"]
    Stage2["Stage 2: Content Understanding<br/>ProcessorMixin"]
    Stage3["Stage 3: Multimodal Analysis<br/>Modal Processors"]
    Stage4["Stage 4: Knowledge Graph Index<br/>LightRAG Integration"]
    Stage5["Stage 5: Storage & Indexing<br/>LightRAG Storages"]
    
    Output["Queryable Knowledge<br/>Graph + Vector DBs"]
    
    Input --> Stage1
    Stage1 -->|"content_list + doc_id"| Stage2
    Stage2 -->|"text_content + multimodal_items"| Stage3
    Stage3 -->|"enhanced descriptions + entities"| Stage4
    Stage4 -->|"chunk_results with relations"| Stage5
    Stage5 --> Output
    
    Cache1["Parse Cache<br/>parse_cache storage"]
    Cache2["Doc Status<br/>doc_status storage"]
    
    Stage1 -.-> Cache1
    Stage2 -.-> Cache2
    Stage5 -.-> Cache2
```

**Sources:** [raganything/processor.py:280-456](), [README.md:151-245]()

---

## Stage 1: Document Parsing

Stage 1 converts raw document files into a standardized `content_list` format through parser abstraction. The system supports multiple parser backends (MinerU, Docling, PaddleOCR) with automatic format detection and conversion.

### Parser Selection and Execution

The `parse_document` method in `ProcessorMixin` orchestrates parser selection:

```mermaid
flowchart LR
    FileInput["Document File<br/>(Path object)"]
    CacheCheck{"Check<br/>Parse Cache"}
    ExtDetect["Extension Detection<br/>.pdf/.docx/.jpg etc"]
    
    ParserSelect{"Parser Type"}
    MinerU["MineruParser"]
    Docling["DoclingParser"]
    PaddleOCR["PaddleOCRParser"]
    
    Output["content_list<br/>(List[Dict])"]
    DocID["doc_id<br/>(content-based hash)"]
    
    FileInput --> CacheCheck
    CacheCheck -->|"Cache Hit"| Output
    CacheCheck -->|"Cache Miss"| ExtDetect
    ExtDetect --> ParserSelect
    
    ParserSelect -->|"config.parser=mineru"| MinerU
    ParserSelect -->|"config.parser=docling"| Docling
    ParserSelect -->|"config.parser=paddleocr"| PaddleOCR
    
    MinerU --> Output
    Docling --> Output
    PaddleOCR --> Output
    
    Output --> DocID
```

**Key Implementation Details:**

| Component | Location | Responsibility |
|-----------|----------|----------------|
| `parse_document` | [raganything/processor.py:280-456]() | Main parsing orchestration |
| `_generate_cache_key` | [raganything/processor.py:50-98]() | Cache key generation from file + config |
| `_get_cached_result` | [raganything/processor.py:133-210]() | Cache retrieval with validation |
| `_store_cached_result` | [raganything/processor.py:212-278]() | Cache storage with metadata |
| `get_parser` | [raganything/parser.py:17-17]() | Parser factory method |

### Parse Caching Mechanism

Parse results are cached to avoid redundant processing. The cache key incorporates file path, modification time, parser type, and parse method:

```mermaid
flowchart TD
    FileAttrs["File Attributes<br/>path + mtime"]
    ParserConfig["Parser Config<br/>parser + parse_method + kwargs"]
    
    CacheKey["Cache Key<br/>MD5 hash"]
    
    ValidCheck{"Validation"}
    MTimeCheck["Check mtime match"]
    ConfigCheck["Check config match"]
    
    FileAttrs --> CacheKey
    ParserConfig --> CacheKey
    
    CacheKey --> ValidCheck
    ValidCheck --> MTimeCheck
    ValidCheck --> ConfigCheck
    
    MTimeCheck -->|"Match"| Valid["Use Cached Result"]
    ConfigCheck -->|"Match"| Valid
    
    MTimeCheck -->|"Mismatch"| Invalid["Re-parse Document"]
    ConfigCheck -->|"Mismatch"| Invalid
```

The cache stores both `content_list` and `doc_id`, with version tracking for future compatibility.

**Sources:** [raganything/processor.py:50-278]()

### Content List Format

All parsers produce a standardized `content_list` structure:

| Type | Required Fields | Optional Fields |
|------|----------------|-----------------|
| `text` | `type`, `text`, `page_idx` | - |
| `image` | `type`, `img_path`, `page_idx` | `image_caption`, `image_footnote` |
| `table` | `type`, `table_body`, `page_idx` | `table_caption`, `table_footnote`, `img_path` |
| `equation` | `type`, `text`, `page_idx` | `latex`, `text_format` |
| `generic` | `type`, `content`, `page_idx` | Custom fields |

**Sources:** [README.md:969-977](), [raganything/processor.py:280-456]()

---

## Stage 2: Content Understanding

Stage 2 separates text content from multimodal elements and manages document status tracking. The `ProcessorMixin` class implements the core logic.

### Content Separation

```mermaid
flowchart LR
    ContentList["content_list<br/>from Stage 1"]
    
    Separate["separate_content()<br/>raganything.utils"]
    
    TextContent["text_content<br/>(concatenated string)"]
    MultimodalItems["multimodal_items<br/>(List[Dict])"]
    
    TextRoute["Text Processing<br/>insert_text_content"]
    MMRoute["Multimodal Processing<br/>Modal Processors"]
    
    ContentList --> Separate
    Separate --> TextContent
    Separate --> MultimodalItems
    
    TextContent --> TextRoute
    MultimodalItems --> MMRoute
```

The `separate_content` utility function filters `content_list` items:
- Text items: Extracted and concatenated with page markers
- Multimodal items: Collected for specialized processing

### Document ID Generation

The `_generate_content_based_doc_id` method creates stable identifiers using `compute_mdhash_id`:

```python
# Implementation reference
def _generate_content_based_doc_id(self, content_list: List[Dict[str, Any]]) -> str:
    from lightrag.utils import compute_mdhash_id
    content_str = json.dumps(content_list, sort_keys=True)
    return compute_mdhash_id(content_str, prefix="doc-")
```

This generates deterministic IDs based on document content, enabling deduplication.

**Sources:** [raganything/processor.py:202-214](), [raganything/processor.py:29-29]()

### Document Status Tracking

Stage 2 initializes document status records in the `lightrag.doc_status` storage:

| Field | Type | Purpose |
|-------|------|---------|
| `status` | `DocStatus` enum | Processing state (READY/HANDLING/PROCESSED/FAILED) |
| `chunks_list` | `List[str]` | List of chunk IDs |
| `chunks_count` | `int` | Total chunk count |
| `multimodal_processed` | `bool` | Multimodal completion flag |
| `file_path` | `str` | Source file reference |
| `updated_at` | `str` | Last update timestamp |

**Sources:** [raganything/processor.py:105-160]()

---

## Stage 3: Multimodal Analysis

Stage 3 processes non-textual content through specialized modal processors, generating enhanced descriptions and extracting contextual information.

### Modal Processor Dispatch

```mermaid
flowchart TD
    MultimodalItems["multimodal_items<br/>(from Stage 2)"]
    
    TypeDetect{"Content Type"}
    
    ImageProc["ImageModalProcessor<br/>vision_model_func"]
    TableProc["TableModalProcessor<br/>modal_caption_func"]
    EquationProc["EquationModalProcessor<br/>modal_caption_func"]
    GenericProc["GenericModalProcessor<br/>extensible"]
    
    Context["ContextExtractor<br/>Surrounding content"]
    
    Description["Enhanced Description<br/>(LLM/VLM generated)"]
    EntityInfo["Entity Info<br/>(name, type, summary)"]
    
    MultimodalItems --> TypeDetect
    
    TypeDetect -->|"type=image"| ImageProc
    TypeDetect -->|"type=table"| TableProc
    TypeDetect -->|"type=equation"| EquationProc
    TypeDetect -->|"other"| GenericProc
    
    ImageProc --> Context
    TableProc --> Context
    EquationProc --> Context
    GenericProc --> Context
    
    Context --> Description
    Context --> EntityInfo
```

The `get_processor_for_type` utility function selects the appropriate processor.

### Batch Processing with Concurrency Control

The `_process_multimodal_content_batch_type_aware` method implements parallel description generation:

```mermaid
flowchart TD
    Start["Multimodal Items<br/>(N items)"]
    
    Semaphore["asyncio.Semaphore<br/>(max_parallel_insert)"]
    
    Concurrent["Concurrent Processing<br/>asyncio.gather"]
    
    Task1["Task 1: Item 1<br/>processor.generate_description_only"]
    Task2["Task 2: Item 2<br/>processor.generate_description_only"]
    TaskN["Task N: Item N<br/>processor.generate_description_only"]
    
    Results["multimodal_data_list<br/>(descriptions + entity_info)"]
    
    Start --> Semaphore
    Semaphore --> Concurrent
    
    Concurrent --> Task1
    Concurrent --> Task2
    Concurrent --> TaskN
    
    Task1 --> Results
    Task2 --> Results
    TaskN --> Results
```

Concurrency is controlled by `lightrag.max_parallel_insert` to avoid overwhelming API rate limits.

**Key Methods:**

| Method | Location | Purpose |
|--------|----------|---------|
| `_process_multimodal_content` | [raganything/processor.py:458-549]() | Entry point for multimodal processing |
| `_process_multimodal_content_batch_type_aware` | [raganything/processor.py:706-881]() | Batch processing orchestration |
| `generate_description_only` | Modal processor classes | LLM/VLM description generation |
| `process_multimodal_content` | Modal processor classes | Full processing pipeline |

**Sources:** [raganything/processor.py:458-881]()

---

## Stage 4: Knowledge Graph Index

Stage 4 constructs the knowledge graph by extracting entities and relationships from both text and multimodal content. This stage integrates tightly with LightRAG's `extract_entities` and `merge_nodes_and_edges` operations.

### Entity Extraction Flow

```mermaid
flowchart TD
    LightRAGChunks["LightRAG Chunks<br/>(chunk_id -> chunk_data)"]
    
    ExtractEntities["extract_entities()<br/>lightrag.operate"]
    
    LLMCall["llm_model_func<br/>Entity/Relation Extraction"]
    
    ChunkResults["chunk_results<br/>(List[Tuple[maybe_nodes, maybe_edges]])"]
    
    NodesFormat["maybe_nodes<br/>(Dict[entity_name -> node_data])"]
    EdgesFormat["maybe_edges<br/>(Dict[(src, tgt) -> edge_data])"]
    
    LightRAGChunks --> ExtractEntities
    ExtractEntities --> LLMCall
    LLMCall --> ChunkResults
    
    ChunkResults --> NodesFormat
    ChunkResults --> EdgesFormat
```

**Sources:** [raganything/processor.py:1176-1203]()

### Multimodal Main Entity Storage

Before entity extraction, multimodal main entities (e.g., "Figure 1: System Architecture (image)") are pre-stored in three locations:

```mermaid
flowchart TD
    MultimodalData["multimodal_data_list<br/>(entity_info + descriptions)"]
    
    EntityID["entity_id<br/>compute_mdhash_id(entity_name)"]
    
    KG["chunk_entity_relation_graph<br/>upsert_node()"]
    EntitiesVDB["entities_vdb<br/>upsert()"]
    FullEntities["full_entities<br/>upsert()"]
    
    MultimodalData --> EntityID
    
    EntityID --> KG
    EntityID --> EntitiesVDB
    EntityID --> FullEntities
```

**Sources:** [raganything/processor.py:1023-1174]()

### Belongs-To Relationship Creation

Stage 4 adds hierarchical `belongs_to` relationships linking extracted entities to their parent multimodal entities via `_batch_add_belongs_to_relations_type_aware`.

**Sources:** [raganything/processor.py:1205-1267]()

---

## Stage 5: Storage & Indexing

Stage 5 distributes processed data across multiple storage backends, creating a multi-layered retrieval infrastructure.

### Storage Distribution

```mermaid
flowchart TD
    ChunkResults["chunk_results<br/>(nodes + edges + belongs_to)"]
    
    MergeOp["merge_nodes_and_edges()<br/>lightrag.operate"]
    
    TextChunks["text_chunks<br/>(KV Storage)"]
    ChunksVDB["chunks_vdb<br/>(Vector Storage)"]
    
    KG["chunk_entity_relation_graph<br/>(Graph Storage)"]
    EntitiesVDB["entities_vdb<br/>(Vector Storage)"]
    RelationsVDB["relationships_vdb<br/>(Vector Storage)"]
    
    FullEntities["full_entities<br/>(KV Storage)"]
    FullRelations["full_relations<br/>(KV Storage)"]
    
    DocStatus["doc_status<br/>(KV Storage)"]
    
    ChunkResults --> MergeOp
    
    MergeOp --> TextChunks
    MergeOp --> ChunksVDB
    MergeOp --> KG
    MergeOp --> EntitiesVDB
    MergeOp --> RelationsVDB
    MergeOp --> FullEntities
    MergeOp --> FullRelations
    
    MergeOp --> DocStatus
```

**Sources:** [raganything/processor.py:1269-1302]()

### Document Status Finalization

After all data is stored, the document status is updated with final metadata. The `multimodal_processed` flag is set to `True` using `_set_multimodal_status_record` or direct `doc_status` update.

**Sources:** [raganything/processor.py:171-201](), [raganything/processor.py:1304-1366]()

---

## Pipeline Execution Methods

### process_document_complete

The standard entry point for document processing.

```mermaid
flowchart TD
    Input["process_document_complete()<br/>file_path + config"]
    
    S1["Stage 1: parse_document()"]
    S2["Stage 2: separate_content()"]
    ContextSet["set_content_source_for_context()"]
    S3["Stage 3: insert_text_content()"]
    S4["Stage 4: _process_multimodal_content()"]
    S5["Stage 5: Implicit in LightRAG insert"]
    
    Complete["Document Processing Complete"]
    
    Input --> S1
    S1 --> S2
    S2 --> ContextSet
    ContextSet --> S3
    S3 --> S4
    S4 --> S5
    S5 --> Complete
```

**Location:** [raganything/processor.py:1444-1532]()

### insert_content_list

Alternative entry point for pre-parsed content. It skips Stage 1 and starts from content separation.

**Location:** [raganything/processor.py:1759-1864]()

---

## Error Handling and Recovery

The pipeline implements recovery mechanisms:
- **Parsing Failures:** `MineruExecutionError` is caught and `doc_status` updated to `FAILED` [raganything/processor.py:1645-1678]().
- **Multimodal Fallback:** If batch processing fails, the system falls back to individual processing [raganything/processor.py:540-549]().

**Sources:** [raganything/processor.py:1-1864](), [README.md:1-245]()

---

# Page: LightRAG Integration

# LightRAG Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [env.example](env.example)
- [examples/lmstudio_integration_example.py](examples/lmstudio_integration_example.py)
- [raganything/raganything.py](raganything/raganything.py)

</details>



This document explains how RAG-Anything extends and integrates with the [LightRAG framework](https://github.com/HKUDS/LightRAG), which provides the foundational RAG capabilities including knowledge graph construction, vector storage, and text-based retrieval. 

RAG-Anything builds on LightRAG by adding multimodal document processing capabilities while maintaining full compatibility with LightRAG's storage and query systems. For details on the overall system architecture, see [Component Overview](3.1). For multimodal processing specifics, see [Multimodal Content Processing](5).

---

## LightRAG Foundation

LightRAG provides the core RAG infrastructure that RAG-Anything depends on:

| Component | LightRAG Provides | RAG-Anything Uses For |
|-----------|-------------------|----------------------|
| **Knowledge Graph** | Entity and relationship storage | Storing multimodal entities and `belongs_to` relations |
| **Vector Databases** | Chunks, entities, relationships VDBs | Storing text and multimodal chunk embeddings |
| **Key-Value Storage** | Document status, full entities/relations | Parse caching, multimodal processing tracking |
| **Entity Extraction** | LLM-based entity/relation extraction | Extracting entities from multimodal descriptions |
| **Query System** | Hybrid/local/global/naive query modes | Base query functionality for all query types |
| **Text Chunking** | Token-aware text splitting | Processing text content from documents |

Sources: [raganything/raganything.py:27-28](), [env.example:152-156]()

---

## Integration Architecture

RAG-Anything integrates with LightRAG through two primary patterns: **wrapping** (where RAG-Anything wraps an existing LightRAG instance) and **extension** (where RAG-Anything adds new capabilities on top of LightRAG's foundation).

### RAGAnything Class Integration

**Mixin Inheritance Pattern:**

```mermaid
graph TB
    subgraph "RAGAnything Class"
        RAGAnything["@dataclass<br/>RAGAnything<br/>(raganything.py:51)"]
        
        subgraph "Mixins (Multiple Inheritance)"
            QueryMixin["QueryMixin<br/>(query.py)"]
            ProcessorMixin["ProcessorMixin<br/>(processor.py)"]
            BatchMixin["BatchMixin<br/>(batch.py)"]
        end
        
        RAGAnything -.->|"inherits"| QueryMixin
        RAGAnything -.->|"inherits"| ProcessorMixin
        RAGAnything -.->|"inherits"| BatchMixin
    end
    
    subgraph "Core LightRAG Instance (self.lightrag)"
        LightRAG["LightRAG instance<br/>field: lightrag<br/>(raganything.py:56)"]
        
        subgraph "LightRAG Storage Attributes"
            text_chunks["self.lightrag.text_chunks<br/>(KV storage)"]
            chunks_vdb["self.lightrag.chunks_vdb<br/>(Vector DB)"]
            entities_vdb["self.lightrag.entities_vdb<br/>(Vector DB)"]
            relationships_vdb["self.lightrag.relationships_vdb<br/>(Vector DB)"]
            kg["self.lightrag.chunk_entity_relation_graph<br/>(Graph DB)"]
            doc_status["self.lightrag.doc_status<br/>(KV storage)"]
            full_entities["self.lightrag.full_entities<br/>(KV storage)"]
            full_relations["self.lightrag.full_relations<br/>(KV storage)"]
        end
    end
    
    subgraph "RAG-Anything Extensions"
        vision_model_func["vision_model_func<br/>(raganything.py:62)"]
        modal_processors["modal_processors: Dict<br/>(raganything.py:88)"]
        parse_cache["parse_cache<br/>namespace='parse_cache'<br/>(raganything.py:94)"]
        context_extractor["context_extractor<br/>(raganything.py:91)"]
    end
    
    RAGAnything -->|"self.lightrag"| LightRAG
    
    QueryMixin -->|"calls self.lightrag.aquery"| LightRAG
    ProcessorMixin -->|"uses self.lightrag storage"| LightRAG
    BatchMixin -->|"uses ProcessorMixin"| ProcessorMixin
    
    ProcessorMixin -->|"stores to"| text_chunks
    ProcessorMixin -->|"stores to"| chunks_vdb
    ProcessorMixin -->|"stores to"| entities_vdb
    ProcessorMixin -->|"stores to"| kg
    ProcessorMixin -->|"updates"| doc_status
    ProcessorMixin -->|"stores to"| full_entities
    
    modal_processors -->|"use self.lightrag"| LightRAG
```

**Key Integration Points:**

| Field/Attribute | Type | Purpose | Code Reference |
|----------------|------|---------|----------------|
| `self.lightrag` | `Optional[LightRAG]` | Core LightRAG instance (pre-initialized or created) | [raganything/raganything.py:56-57]() |
| `self.llm_model_func` | `Optional[Callable]` | LLM function (inherited from LightRAG if not provided) | [raganything/raganything.py:59-60]() |
| `self.vision_model_func` | `Optional[Callable]` | VLM function for image analysis (RAG-Anything extension) | [raganything/raganything.py:62-63]() |
| `self.embedding_func` | `Optional[Callable]` | Embedding function (inherited from LightRAG if not provided) | [raganything/raganything.py:65-66]() |
| `self.lightrag_kwargs` | `Dict[str, Any]` | Parameters for LightRAG initialization | [raganything/raganything.py:73-84]() |
| `self.modal_processors` | `Dict[str, Any]` | Multimodal content processors | [raganything/raganything.py:88-89]() |
| `self.parse_cache` | Storage instance | Document parse cache (uses LightRAG's KV storage class) | [raganything/raganything.py:94-95]() |

Sources: [raganything/raganything.py:50-106]()

---

## Initialization Patterns

RAG-Anything supports two initialization patterns for LightRAG integration:

### Pattern 1: Automatic LightRAG Creation

RAG-Anything creates and configures a new LightRAG instance:

```mermaid
graph LR
    INIT["RAGAnything.__post_init__<br/>(raganything.py:108)"]
    ENSURE["_ensure_lightrag_initialized<br/>(raganything.py:231)"]
    CREATE["LightRAG(...)<br/>(raganything.py:340)"]
    INIT_STOR["initialize_storages<br/>(raganything.py:341)"]
    PARSE_CACHE["Initialize parse_cache<br/>(raganything.py:345-351)"]
    PROCS["_initialize_processors<br/>(raganything.py:354)"]
    
    INIT -->|"deferred"| ENSURE
    ENSURE -->|"if lightrag is None"| CREATE
    CREATE --> INIT_STOR
    INIT_STOR --> PARSE_CACHE
    PARSE_CACHE --> PROCS
```

**Key Steps:**
1. Check `self.lightrag is None` ([raganything/raganything.py:247]())
2. Validate `llm_model_func` and `embedding_func` provided ([raganything/raganything.py:307-315]())
3. Create LightRAG with `lightrag_params` merged from defaults and `lightrag_kwargs` ([raganything/raganything.py:320-327]())
4. Initialize storages via `await self.lightrag.initialize_storages()` ([raganything/raganything.py:341]())
5. Create parse cache using `self.lightrag.key_string_value_json_storage_cls` ([raganything/raganything.py:345-351]())
6. Initialize modal processors via `_initialize_processors()` ([raganything/raganything.py:354]())

Sources: [raganything/raganything.py:231-364]()

### Pattern 2: Using Pre-initialized LightRAG

RAG-Anything wraps an existing LightRAG instance:

```mermaid
graph LR
    USER["User provides<br/>lightrag=existing_instance"]
    INIT["RAGAnything.__post_init__<br/>(raganything.py:108)"]
    ENSURE["_ensure_lightrag_initialized<br/>(raganything.py:231)"]
    INHERIT["Inherit model funcs<br/>(raganything.py:250-260)"]
    CHECK["Check storage status<br/>(raganything.py:264-276)"]
    PARSE_CACHE["Initialize parse_cache<br/>(raganything.py:279-291)"]
    PROCS["_initialize_processors<br/>(raganything.py:294-295)"]
    
    USER --> INIT
    INIT -->|"deferred"| ENSURE
    ENSURE -->|"if lightrag is not None"| INHERIT
    INHERIT --> CHECK
    CHECK --> PARSE_CACHE
    PARSE_CACHE --> PROCS
```

**Key Steps:**
1. Check `self.lightrag is not None` ([raganything/raganything.py:247]())
2. Inherit `llm_model_func` if not provided ([raganything/raganything.py:250-254]())
3. Inherit `embedding_func` if not provided ([raganything/raganything.py:256-260]())
4. Initialize storages if not already done ([raganything/raganything.py:264-276]())
5. Create parse cache in LightRAG's workspace ([raganything/raganything.py:279-291]())
6. Initialize processors ([raganything/raganything.py:294-295]())

Sources: [raganything/raganything.py:247-304]()

---

## Storage System Integration

RAG-Anything integrates deeply with LightRAG's multi-layer storage architecture, adding parse caching and multimodal-specific tracking.

### Storage Architecture Mapping

**Storage Access Pattern:**

```mermaid
graph TB
    subgraph "RAGAnything Extension Storage"
        parse_cache["self.parse_cache<br/>(KV storage)<br/>namespace='parse_cache'<br/>created via self.lightrag.key_string_value_json_storage_cls"]
    end
    
    subgraph "LightRAG Storage Instances (via self.lightrag)"
        text_chunks["self.lightrag.text_chunks<br/>(KV storage)<br/>namespace='text_chunks'"]
        chunks_vdb["self.lightrag.chunks_vdb<br/>(Vector DB)<br/>stores chunk embeddings"]
        entities_vdb["self.lightrag.entities_vdb<br/>(Vector DB)<br/>stores entity embeddings"]
        relationships_vdb["self.lightrag.relationships_vdb<br/>(Vector DB)<br/>stores relation embeddings"]
        kg["self.lightrag.chunk_entity_relation_graph<br/>(Graph DB)<br/>stores nodes and edges"]
        doc_status["self.lightrag.doc_status<br/>(KV storage)<br/>namespace='doc_status'"]
        full_entities["self.lightrag.full_entities<br/>(KV storage)<br/>namespace='full_entities'"]
        full_relations["self.lightrag.full_relations<br/>(KV storage)<br/>namespace='full_relations'"]
    end
```

**Storage Namespace Pattern:**

All LightRAG and RAG-Anything storages use namespace-based isolation:

| Storage | Namespace | Accessed Via | Creation |
|---------|-----------|--------------|----------|
| `text_chunks` | `'text_chunks'` | `self.lightrag.text_chunks` | LightRAG initialization |
| `doc_status` | `'doc_status'` | `self.lightrag.doc_status` | LightRAG initialization |
| `full_entities` | `'full_entities'` | `self.lightrag.full_entities` | LightRAG initialization |
| `full_relations` | `'full_relations'` | `self.lightrag.full_relations` | LightRAG initialization |
| `parse_cache` | `'parse_cache'` | `self.parse_cache` | RAG-Anything creates using `self.lightrag.key_string_value_json_storage_cls` |

**Parse Cache Creation:**
[raganything/raganything.py:345-351]()
```python
self.parse_cache = self.lightrag.key_string_value_json_storage_cls(
    namespace="parse_cache",
    workspace=self.lightrag.workspace,
    global_config=self.lightrag.__dict__,
    embedding_func=self.embedding_func,
)
await self.parse_cache.initialize()
```

Sources: [raganything/raganything.py:345-351](), [env.example:152-156]()

---

## Processing Pipeline Integration

RAG-Anything extends LightRAG's text processing pipeline to support multimodal content while maintaining compatibility with LightRAG's entity extraction and knowledge graph construction.

### 7-Stage Multimodal Processing Pipeline

```mermaid
graph TB
    subgraph "Stage 1: Description Generation"
        gen_desc["processor.generate_description_only()"]
    end
    
    subgraph "Stage 2: Chunk Conversion"
        convert["_convert_to_lightrag_chunks_type_aware()"]
        apply_template["_apply_chunk_template()"]
    end
    
    subgraph "Stage 3: Chunk Storage"
        text_chunks_upsert["await self.lightrag.text_chunks.upsert()"]
        chunks_vdb_upsert["await self.lightrag.chunks_vdb.upsert()"]
    end
    
    subgraph "Stage 4: Main Entity Storage"
        kg_node["await self.lightrag.chunk_entity_relation_graph.upsert_node()"]
        ent_vdb["await self.lightrag.entities_vdb.upsert()"]
    end
    
    subgraph "Stage 5: Entity Extraction (Uses LightRAG)"
        lr_extract["from lightrag.operate import extract_entities"]
    end
    
    subgraph "Stage 6: Belongs-To Relations"
        belongs_rel["Add belongs_to relation to modal_entity_name"]
    end
    
    subgraph "Stage 7: Merge to KG (Uses LightRAG)"
        lr_merge["from lightrag.operate import merge_nodes_and_edges"]
    end
    
    gen_desc --> convert
    convert --> apply_template
    apply_template --> text_chunks_upsert
    text_chunks_upsert --> chunks_vdb_upsert
    chunks_vdb_upsert --> kg_node
    kg_node --> ent_vdb
    ent_vdb --> lr_extract
    lr_extract --> belongs_rel
    belongs_rel --> lr_merge
```

Sources: [raganything/raganything.py:50-106](), [env.example:48-51]()

---

## Configuration Inheritance

RAG-Anything allows full control over LightRAG configuration through the `lightrag_kwargs` parameter, which is merged with required defaults during initialization.

**Configuration Flow:**

```mermaid
graph TB
    subgraph "User Input"
        user_kwargs["lightrag_kwargs: Dict[str, Any]"]
    end
    
    subgraph "_ensure_lightrag_initialized()"
        defaults["lightrag_params = {<br/>  'working_dir': self.working_dir,<br/>  'llm_model_func': self.llm_model_func,<br/>  'embedding_func': self.embedding_func<br/>}"]
        merge["lightrag_params.update(self.lightrag_kwargs)"]
        create_lr["self.lightrag = LightRAG(**lightrag_params)"]
    end
    
    user_kwargs --> defaults
    defaults --> merge
    merge --> create_lr
```

**Key Configurable Parameters (via `lightrag_kwargs`):**
- **Storage**: `kv_storage`, `vector_storage`, `graph_storage`, `doc_status_storage` [raganything/raganything.py:76]()
- **Retrieval**: `top_k`, `chunk_top_k`, `cosine_threshold` [raganything/raganything.py:77-78]()
- **Chunking**: `chunk_token_size`, `chunk_overlap_token_size` [raganything/raganything.py:79]()
- **LLM**: `llm_model_name`, `llm_model_max_token_size`, `llm_model_max_async` [raganything/raganything.py:81]()

Sources: [raganything/raganything.py:73-84](), [raganything/raganything.py:318-342]()

---

## Summary

RAG-Anything integrates with LightRAG through:

1. **Wrapping Pattern**: Can wrap existing LightRAG instances or create new ones [raganything/raganything.py:56-57]().
2. **Storage Integration**: Uses all LightRAG storage systems plus a custom `parse_cache` [raganything/raganything.py:94-95]().
3. **Pipeline Extension**: Extends entity extraction and merge operations for multimodal content.
4. **Configuration**: Supports all LightRAG configuration parameters via `lightrag_kwargs` [raganything/raganything.py:73-84]().

This integration allows RAG-Anything to provide multimodal capabilities while maintaining full compatibility with LightRAG's text-based RAG system.

Sources: [raganything/raganything.py:50-106](), [examples/lmstudio_integration_example.py:175-194]()

---

# Page: Document Processing

# Document Processing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [raganything/parser.py](raganything/parser.py)
- [raganything/processor.py](raganything/processor.py)
- [tests/test_insert_content_list.py](tests/test_insert_content_list.py)
- [tests/testparser_kwargs.py](tests/testparser_kwargs.py)

</details>



## Purpose and Scope

This page provides a comprehensive guide to RAG-Anything's document processing system, covering document ingestion, format detection, parsing, and content extraction. The document processing layer is the foundation of the system, with a combined importance score of 81.06 across `parser.py` and `processor.py`, making it the most critical subsystem in the codebase.

**Scope boundaries:**
- For detailed parser implementations and configuration options, see [Document Parsers](#4.1)
- For internal processing pipeline mechanics and LightRAG integration, see [Processing Pipeline Internals](#4.2)
- For the caching mechanism, see [Parse Caching System](#4.3)
- For state management and flags, see [Document Status Tracking](#4.4)
- For batch/concurrent document processing, see [Batch Processing](#4.5)
- For multimodal content analysis (images, tables, equations), see [Multimodal Content Processing](#5)

## Document Processing Architecture

The document processing system follows a two-stage architecture: (1) **Parsing** via `Parser` implementations and (2) **Processing** via `ProcessorMixin` methods. This separation enables flexible parser selection while maintaining a consistent processing interface.

```mermaid
graph TB
    subgraph "Input Layer"
        PDF["PDF Documents"]
        IMG["Images<br/>(JPG, PNG, BMP, TIFF)"]
        OFFICE["Office Files<br/>(DOCX, XLSX, PPTX)"]
        TEXT["Text Files<br/>(TXT, MD)"]
        HTML["HTML Files<br/>(HTML, HTM, XHTML)"]
    end
    
    subgraph "Parser Layer - parser.py"
        PARSER_BASE["Parser<br/>(Base Class)"]
        MINERU["MineruParser"]
        DOCLING["DoclingParser"]
        PADDLE["PaddleOCRParser"]
        
        PARSER_BASE --> MINERU
        PARSER_BASE --> DOCLING
        PARSER_BASE --> PADDLE
    end
    
    subgraph "Format Conversion"
        LIBRE["Parser.convert_office_to_pdf()"]
        REPORTLAB["Parser.convert_text_to_pdf()"]
        PILLOW["PIL Image Conversion"]
    end
    
    subgraph "Processing Layer - processor.py"
        PROC_MIXIN["ProcessorMixin"]
        PARSE_DOC["parse_document()"]
        PROC_COMPLETE["process_document_complete()"]
        INSERT_LIST["insert_content_list()"]
        
        PROC_MIXIN --> PARSE_DOC
        PROC_MIXIN --> PROC_COMPLETE
        PROC_MIXIN --> INSERT_LIST
    end
    
    subgraph "Output"
        CONTENT_LIST["content_list<br/>(List[Dict])"]
        DOC_ID["doc_id<br/>(Content Hash)"]
        SEPARATED["Text + Multimodal Items"]
    end
    
    PDF --> MINERU
    IMG --> MINERU
    IMG --> PILLOW
    
    OFFICE --> LIBRE
    TEXT --> REPORTLAB
    HTML --> DOCLING
    OFFICE --> DOCLING
    
    LIBRE --> MINERU
    REPORTLAB --> MINERU
    PILLOW --> MINERU
    
    MINERU --> CONTENT_LIST
    DOCLING --> CONTENT_LIST
    PADDLE --> CONTENT_LIST
    
    CONTENT_LIST --> PARSE_DOC
    PARSE_DOC --> DOC_ID
    PARSE_DOC --> PROC_COMPLETE
    
    PROC_COMPLETE --> SEPARATED
    INSERT_LIST --> SEPARATED
    
    SEPARATED --> LIGHTRAG["LightRAG Storage"]
```

**Sources:** [raganything/parser.py:68-1373](), [raganything/processor.py:32-453](), [raganything/processor.py:1441-1861]()

## Supported Document Formats

RAG-Anything supports a comprehensive range of document formats through its multi-parser strategy. Format support is defined as class-level constants in the `Parser` base class [raganything/parser.py:76-78]().

| Format Category | Extensions | Primary Parser | Conversion Required |
|----------------|------------|----------------|---------------------|
| **PDF** | `.pdf` | MineruParser / DoclingParser | No |
| **Images** | `.png`, `.jpg`, `.jpeg`, `.bmp`, `.tiff`, `.tif`, `.gif`, `.webp` | MineruParser / PaddleOCRParser | Yes (non-PNG/JPG → PNG for MinerU) |
| **Office Documents** | `.doc`, `.docx`, `.ppt`, `.pptx`, `.xls`, `.xlsx` | DoclingParser (direct)<br/>MineruParser (via PDF) | MineruParser: Yes (LibreOffice → PDF) |
| **Text Files** | `.txt`, `.md` | MineruParser | Yes (ReportLab → PDF) |
| **HTML** | `.html`, `.htm`, `.xhtml` | DoclingParser | No |

**Format Detection:** Extension-based routing occurs in `MineruParser.parse_document()` [raganything/parser.py:1178-1227]() and `DoclingParser.parse_document()` [raganything/parser.py:1332-1373]().

**Sources:** [raganything/parser.py:76-78](), [raganything/parser.py:1271]()

## Parser Selection Strategy

RAG-Anything employs a pluggable parser architecture optimized for different document types. Parser selection is configured via `RAGAnythingConfig.parser` and defaults to `"mineru"`.

**Available Parsers:**
- **MinerU (Default):** Excels at complex layout detection in academic/technical PDFs. Uses the `magic-pdf` command [raganything/parser.py:572-651]().
- **Docling:** Native support for Office and HTML formats without PDF conversion overhead [raganything/parser.py:1262-1276]().
- **PaddleOCR:** Specialized for high-accuracy OCR on images and scanned documents [raganything/parser.py:1416-1430]().

For details, see [Document Parsers](#4.1).

**Sources:** [raganything/parser.py:572-651](), [raganything/parser.py:1262-1276](), [raganything/processor.py:335-342]()

## Format Conversion Pipelines

RAG-Anything includes robust format conversion utilities in the `Parser` base class to normalize unsupported formats into parser-compatible inputs.

### Office and Text Conversion
- **Office to PDF:** Uses LibreOffice headless mode to convert legacy formats [raganything/parser.py:194-282]().
- **Text to PDF:** Uses ReportLab to generate PDFs from `.txt` or `.md` files, supporting multi-encoding detection (UTF-8, GBK, etc.) and international fonts like WenQuanYi [raganything/parser.py:285-520]().

### Image Normalization
Non-standard image formats (BMP, TIFF, etc.) are converted to PNG using Pillow for MinerU compatibility [raganything/parser.py:1011-1064]().

**Sources:** [raganything/parser.py:194-520](), [raganything/parser.py:1011-1064]()

## Content List Structure

The document parsing output is a standardized `content_list` format - a `List[Dict[str, Any]]` where each dictionary represents a content block.

| Type | Key Fields |
|------|------------|
| `text` | `text`, `page_idx` |
| `image` | `img_path` (absolute), `image_caption`, `page_idx` |
| `table` | `table_body` (markdown), `img_path`, `table_caption` |
| `equation` | `text` (LaTeX), `text_format`, `img_path` |

**Sources:** [raganything/parser.py:798-883](), [raganything/processor.py:1756-1788]()

## Processing Workflow

The `ProcessorMixin` class orchestrates the complete document-to-knowledge workflow.

### Parse Document
`parse_document()` handles the initial ingestion [raganything/processor.py:280-453](). It checks the `parse_cache` using a key generated from the file path, mtime, and configuration [raganything/processor.py:50-98](). If no cache exists, it invokes the selected parser and generates a content-based `doc_id` [raganything/processor.py:202-218]().

For details, see [Processing Pipeline Internals](#4.2) and [Parse Caching System](#4.3).

### Complete Processing
`process_document_complete()` is the high-level entry point [raganything/processor.py:1441-1529](). It:
1. Parses the document.
2. Separates text from multimodal items.
3. Inserts text into LightRAG (triggering chunking/indexing).
4. Routes images, tables, and equations to specialized modal processors.

For details, see [Processing Pipeline Internals](#4.2).

**Sources:** [raganything/processor.py:280-453](), [raganything/processor.py:1441-1529]()

## Document Status and Tracking

Processing states are tracked in `doc_status` storage [raganything/processor.py:105-137]().
- **States:** `READY`, `HANDLING`, `PROCESSED`, `FAILED`.
- **Multimodal Flag:** A `multimodal_processed` flag tracks whether non-textual elements (images/tables) have been integrated into the graph [raganything/processor.py:189-200]().

For details, see [Document Status Tracking](#4.4).

**Sources:** [raganything/processor.py:105-200](), [raganything/base.py:18-24]()

## Batch Processing

The `BatchMixin` provides methods for processing folders and document lists concurrently.
- `process_folder_complete()`: Recursively processes directories.
- `BatchParser`: A utility for high-concurrency parsing with dry-run support.

For details, see [Batch Processing](#4.5).

**Sources:** [raganything/batch.py:26-35](), [raganything/batch.py:263-280]()

---

# Page: Document Parsers

# Document Parsers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/test.yaml](.github/workflows/test.yaml)
- [raganything/batch_parser.py](raganything/batch_parser.py)
- [raganything/omml_extractor.py](raganything/omml_extractor.py)
- [raganything/parser.py](raganything/parser.py)
- [tests/test_content_list_alias_handling.py](tests/test_content_list_alias_handling.py)
- [tests/test_custom_parser.py](tests/test_custom_parser.py)
- [tests/test_doc_status_creation.py](tests/test_doc_status_creation.py)
- [tests/test_omml_extractor.py](tests/test_omml_extractor.py)
- [tests/testpaddleocr_parser.py](tests/testpaddleocr_parser.py)
- [tests/testparser_kwargs.py](tests/testparser_kwargs.py)

</details>



This page documents the document parsing subsystem of RAG-Anything, which converts various file formats into a standardized content representation. The parser layer is the first stage of the five-stage processing pipeline and provides a unified interface for extracting content from PDFs, Office documents, images, and text files.

For information about what happens to parsed content after extraction, see [Processing Pipeline Internals](). For details on parse caching mechanisms, see [Parse Caching System]().

## Purpose and Scope

The document parser subsystem provides:

- **Parser Abstraction**: A unified interface (`Parser` base class) for multiple parsing backends.
- **Format Normalization**: Automatic conversion of Office documents and text files to PDF before parsing.
- **Multi-Backend Support**: Three built-in parser implementations (MinerU, Docling, PaddleOCR) and a registry for custom extensions.
- **Equation Enrichment**: Specialized OMML extraction for structured math in DOCX files.
- **Standardized Output**: All parsers produce a consistent `content_list` format for downstream processing.

Sources: [raganything/parser.py:1-66](), [raganything/omml_extractor.py:1-38]()

## Parser Architecture Overview

The parsing subsystem uses a polymorphic design with a central registry for extensibility.

### Class Hierarchy and Registry

```mermaid
classDiagram
    class Parser {
        <<abstract>>
        +OFFICE_FORMATS
        +IMAGE_FORMATS
        +TEXT_FORMATS
        +parse_pdf()
        +parse_image()
        +parse_document()
        +convert_office_to_pdf()
        +convert_text_to_pdf()
        +check_installation()
    }
    
    class MineruParser {
        -_run_mineru_command()
        -_read_output_files()
        +parse_pdf()
    }
    
    class DoclingParser {
        +HTML_FORMATS
        -_get_converter()
        -_run_docling_python()
        +parse_document()
    }
    
    class PaddleOCRParser {
        -_ocr_instances
        -_get_ocr()
        +parse_pdf()
        +parse_image()
    }
    
    class CustomParser {
        <<user defined>>
    }
    
    class Registry {
        <<module level>>
        +_CUSTOM_PARSERS: dict
        +register_parser(name, cls)
        +get_parser(name)
    }
    
    Parser <|-- MineruParser
    Parser <|-- DoclingParser
    Parser <|-- PaddleOCRParser
    Parser <|-- CustomParser
    Registry ..> Parser : manages
```

**Parser Selection Flow**

```mermaid
flowchart TD
    Start["get_parser(parser_type)"]
    
    CheckBuiltin{"Is Built-in?"}
    CheckCustom{"In _CUSTOM_PARSERS?"}
    
    MinerU["MineruParser()"]
    Docling["DoclingParser()"]
    PaddleOCR["PaddleOCRParser()"]
    CustomInst["Custom Class()"]
    Error["ValueError: Unsupported parser"]
    
    Start --> CheckBuiltin
    CheckBuiltin -->|"mineru"| MinerU
    CheckBuiltin -->|"docling"| Docling
    CheckBuiltin -->|"paddleocr"| PaddleOCR
    CheckBuiltin -->|"no"| CheckCustom
    
    CheckCustom -->|"yes"| CustomInst
    CheckCustom -->|"no"| Error
    
    MinerU --> Return["Return Parser instance"]
    Docling --> Return
    PaddleOCR --> Return
    CustomInst --> Return
```

Sources: [raganything/parser.py:49-595](), [raganything/parser.py:2165-2244](), [tests/test_custom_parser.py:17-40]()

## Parser Registry and Custom Parsers

RAG-Anything supports a plugin architecture for document parsers. Developers can register custom parser classes that inherit from the `Parser` base class.

### Key Functions
- `register_parser(name: str, parser_cls: Type[Parser])`: Adds a new parser to the internal `_CUSTOM_PARSERS` dictionary. It enforces that the class is a subclass of `Parser` and prevents overriding built-in names [raganything/parser.py:2180-2212]().
- `unregister_parser(name: str)`: Removes a custom parser from the registry [raganything/parser.py:2215-2231]().
- `list_parsers()`: Returns a dictionary of all available parsers (built-in and custom) [raganything/parser.py:2247-2258]().

### Custom Parser Example
```python
from raganything.parser import Parser, register_parser

class MySpecialParser(Parser):
    def check_installation(self): return True
    def parse_document(self, file_path, **kwargs):
        return [{"type": "text", "text": "Extracted content", "page_idx": 0}]

register_parser("special", MySpecialParser)
```
Sources: [tests/test_custom_parser.py:17-31](), [raganything/parser.py:2180-2212]()

## Supported File Formats

| Format Category | Extensions | MinerU | Docling | PaddleOCR | Notes |
|----------------|------------|--------|---------|-----------|-------|
| **PDF** | `.pdf` | ✅ Native | ✅ Native | ✅ Native | All parsers support PDF |
| **Office** | `.doc`, `.docx`, `.ppt`, `.pptx`, `.xls`, `.xlsx` | ✅ Via LibreOffice | ✅ Native (API) | ✅ Via LibreOffice | MinerU/PaddleOCR convert to PDF first |
| **Images** | `.png`, `.jpeg`, `.jpg` | ✅ Native | ❌ | ✅ Native | Core image formats |
| **Extended Images** | `.bmp`, `.tiff`, `.tif`, `.gif`, `.webp` | ✅ Via Pillow | ❌ | ✅ Native | Requires `raganything[image]` extra |
| **Text** | `.txt`, `.md` | ✅ Via ReportLab | ❌ | ✅ Via ReportLab | Requires `raganything[text]` extra |
| **HTML** | `.html`, `.htm`, `.xhtml` | ❌ | ✅ Native | ❌ | Docling-exclusive |

Sources: [raganything/parser.py:56-59](), [raganything/parser.py:1352](), [raganything/parser.py:76-78]()

## MinerU Parser

`MineruParser` is the default parser, leveraging the MinerU 2.0 CLI. It handles high-fidelity extraction including tables and formulas.

### Windows Path Safety
On Windows, `MineruParser` implements a safety mechanism for paths containing non-ASCII characters. It copies the source file to a temporary ASCII-named file and uses an ASCII output directory to prevent MinerU CLI failures [raganything/parser.py:1010-1065]().

### Backend Support
Supports multiple MinerU backends via the `backend` parameter: `pipeline` (default), `vlm-auto-engine`, `vlm-http-client`, `hybrid-auto-engine`, and `hybrid-http-client` [raganything/parser.py:617-679]().

Sources: [raganything/parser.py:597-1341](), [tests/testparser_kwargs.py:160-192]()

## Docling Parser

`DoclingParser` has been updated to use the **Docling Python API** (`DocumentConverter`) instead of the CLI for better performance and stability.

### Python API Integration
The parser maintains a cached `DocumentConverter` instance via `_get_converter()`. It accepts arbitrary keyword arguments which are forwarded to the converter configuration [raganything/parser.py:1367-1428]().

### Equation Extraction
Docling identifies mathematical formulas and classifies them as `texts` with `label="formula"`. The parser maps these to the standard `equation` block type [raganything/parser.py:1625-1640]().

Sources: [raganything/parser.py:1343-1834](), [tests/testparser_kwargs.py:46-55]()

## PaddleOCR Parser

`PaddleOCRParser` renders PDF pages into images using `pypdfium2` and then performs OCR using the PaddleOCR library.

### Text Line Extraction
The `_extract_text_lines()` method recursively traverses the PaddleOCR result structure (which can be a list of tuples or nested dictionaries) to extract raw text and confidence scores [raganything/parser.py:1884-1968]().

Sources: [raganything/parser.py:1837-2160](), [tests/testpaddleocr_parser.py:95-117]()

## OMML Equation Extractor

For `.docx` files, RAG-Anything includes a specialized `omml_extractor` to recover structured math that might be lost during PDF conversion.

### Implementation Detail
It opens the DOCX as a ZIP archive, reads `word/document.xml`, and recursively converts `<m:oMath>` elements to LaTeX [raganything/omml_extractor.py:111-168]().

### Mapping Logic
The extractor uses a comprehensive mapping for OMML constructs:
- **N-ary Operators**: Maps Unicode codepoints (e.g., `\u2211`) to LaTeX commands (e.g., `\sum`) [raganything/omml_extractor.py:65-79]().
- **Functions**: Recognizes common math functions (sin, cos, log) and wraps others in parentheses [raganything/omml_extractor.py:400-425]().
- **Structures**: Handles fractions (`m:f`), radicals (`m:rad`), and matrices (`m:m`) [raganything/omml_extractor.py:273-350]().

Sources: [raganything/omml_extractor.py:1-450](), [tests/test_omml_extractor.py:63-214]()

## Standardized Output: content_list

All parsers must return a `List[Dict[str, Any]]`.

| Type | Key Fields | Description |
|------|------------|-------------|
| `text` | `text`, `page_idx` | Standard text block. |
| `image` | `img_path`, `image_caption` | Path to extracted image file. |
| `table` | `table_body`, `table_caption` | Markdown or list-of-lists representation. |
| `equation` | `text`, `latex`, `text_format` | Math formula (usually LaTeX). |

### Field Aliases
To maintain backward compatibility with MinerU 1.x and various parser outputs, the system handles aliases like `img_caption` → `image_caption` and `latex` → `text` (when `text_format` is "latex") [raganything/parser.py:603-606](), [tests/test_content_list_alias_handling.py:127-150]().

Sources: [raganything/parser.py:930-957](), [tests/test_content_list_alias_handling.py:87-100]()

---

# Page: Processing Pipeline Internals

# Processing Pipeline Internals

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [raganything/processor.py](raganything/processor.py)
- [tests/test_insert_content_list.py](tests/test_insert_content_list.py)

</details>



This document provides a deep dive into the `ProcessorMixin` class and the document processing workflow in RAG-Anything. It covers the internal mechanisms that transform parsed documents into indexed, queryable knowledge graph entries.

**Scope**: This page focuses on the processing logic after parsing completes and before querying begins. For parser selection and configuration, see [Document Parsers](#4.1). For parse caching mechanisms, see [Parse Caching System](#4.3). For document status tracking details, see [Document Status Tracking](#4.4). For multimodal processor internals, see [Modal Processor Architecture](#5.1).

---

## ProcessorMixin Class Architecture

The `ProcessorMixin` class serves as the central orchestrator for document processing in RAG-Anything. It handles the complete workflow from document parsing through knowledge graph indexing.

### Class Composition and Key Methods

```mermaid
graph TB
    subgraph "Code Entity Space: RAGAnything Composition"
        RAGAnything["class RAGAnything"]
        ProcessorMixin["class ProcessorMixin"]
        QueryMixin["class QueryMixin"]
        BatchMixin["class BatchMixin"]
        
        RAGAnything -->|inherits| ProcessorMixin
        RAGAnything -->|inherits| QueryMixin
        RAGAnything -->|inherits| BatchMixin
    end
    
    subgraph "Code Entity Space: ProcessorMixin Internals"
        ParseDoc["parse_document()"]
        ProcComplete["process_document_complete()"]
        InsertContent["insert_content_list()"]
        ProcMultimodal["_process_multimodal_content_batch_type_aware()"]
        
        ProcessorMixin --> ParseDoc
        ProcessorMixin --> ProcComplete
        ProcessorMixin --> InsertContent
        ProcessorMixin --> ProcMultimodal
    end
    
    subgraph "Code Entity Space: Dependencies"
        DocParser["self.doc_parser (Parser)"]
        LightRAGInst["self.lightrag (LightRAG)"]
        ModalProcs["self.modal_processors (Dict)"]
        ParseCache["self.parse_cache (Storage)"]
        
        ProcessorMixin -.uses.-> DocParser
        ProcessorMixin -.uses.-> LightRAGInst
        ProcessorMixin -.uses.-> ModalProcs
        ProcessorMixin -.uses.-> ParseCache
    end
```

Sources: [raganything/processor.py:32-34](), [raganything/main.py:27-31]()

### Key Attributes

| Attribute | Type | Purpose |
|-----------|------|---------|
| `config` | `RAGAnythingConfig` | Configuration object containing parser settings, paths, and processing options. |
| `lightrag` | `LightRAG` | LightRAG instance for knowledge graph and vector DB operations. |
| `doc_parser` | `Parser` | Parser instance (MinerU/Docling/PaddleOCR) selected by configuration. |
| `modal_processors` | `Dict[str, BaseModalProcessor]` | Registry mapping content types (image, table, equation) to processor instances. |
| `parse_cache` | `Storage` | Cache storage for parsed document results to prevent redundant parsing. |
| `multimodal_status_cache` | `Storage` | Compatibility storage for tracking multimodal processing completion. |

Sources: [raganything/processor.py:32-35](), [raganything/processor.py:163-167](), [raganything/main.py:112-115]()

---

## Core Processing Methods

The `ProcessorMixin` provides three primary entry points for document processing:

### Method Overview

```mermaid
graph LR
    subgraph "Entry Points"
        Entry1["parse_document()"]
        Entry2["process_document_complete()"]
        Entry3["insert_content_list()"]
        Entry4["process_document_complete_lightrag_api()"]
    end
    
    subgraph "Internal Flow"
        Parse["Document Parsing"]
        Separate["Content Separation"]
        TextInsert["Text Insertion"]
        MMProcess["Multimodal Processing"]
    end
    
    Entry1 --> Parse
    Entry2 --> Parse --> Separate --> TextInsert --> MMProcess
    Entry3 --> Separate --> TextInsert --> MMProcess
    Entry4 --> Parse --> Separate --> TextInsert
```

Sources: [raganything/processor.py:280-285](), [raganything/processor.py:1444-1450](), [raganything/processor.py:1534-1540](), [raganything/processor.py:1759-1765]()

### parse_document()

Primary method for parsing documents with caching support. It returns a `(content_list, doc_id)` tuple.

**Workflow**:
1. Generate cache key via `_generate_cache_key()` using MD5 hash of file path, mtime, and configuration [raganything/processor.py:50-98]().
2. Check `parse_cache` for existing results via `_get_cached_result()` [raganything/processor.py:246-261]().
3. On cache miss, identify the parser via `get_parser()` based on the file extension [raganything/processor.py:363-366]().
4. Invoke parser (e.g., `doc_parser.parse_pdf`) [raganything/processor.py:416-419]().
5. Generate content-based `doc_id` via `_generate_content_based_doc_id()` [raganything/processor.py:202-230]().
6. Store result in `parse_cache` via `_store_cached_result()` [raganything/processor.py:263-278]().

### process_document_complete()

End-to-end processing workflow from file to indexed knowledge graph.

**Workflow Stages**:
1. **Parse**: Calls `parse_document()` to get content [raganything/processor.py:1484-1486]().
2. **Separate**: Uses `separate_content()` to split text from multimodal items [raganything/processor.py:1492]().
3. **Insert Text**: Calls `insert_text_content()` which delegates to `lightrag.ainsert` [raganything/processor.py:1504-1515]().
4. **Multimodal**: Calls `_process_multimodal_content()` to handle images, tables, and equations [raganything/processor.py:1517-1522]().

### insert_content_list()

Direct insertion of pre-parsed content without the parsing step. This is the core logic used by `process_document_complete()` after parsing is finished.

**Key Parameters**:
- `content_list`: List of dictionaries containing `type`, `text`/`img_path`, and `page_idx`.
- `file_path`: Source file path for reference.

**Behavior**:
- If text exists, it inserts text first to ensure the base document exists in LightRAG [raganything/processor.py:1807-1818]().
- It then processes multimodal items, linking them to the text entities via `belongs_to` relations [raganything/processor.py:1836-1845]().

Sources: [raganything/processor.py:1759-1864](), [tests/test_insert_content_list.py:131-154]()

---

## Document Processing Workflow

The complete processing workflow consists of seven distinct stages:

```mermaid
flowchart TB
    subgraph Stage1["Stage 1: Document Parsing"]
        FileInput["File Input"] --> CacheCheck{"_generate_cache_key()"}
        CacheCheck -->|Hit| CacheReturn["Return cached content_list"]
        CacheCheck -->|Miss| SelectParser["get_parser()"]
        SelectParser --> InvokeParser["Parser.parse_*()"]
        InvokeParser --> GenDocId["_generate_content_based_doc_id()"]
        GenDocId --> StoreCache["_store_cached_result()"]
    end
    
    subgraph Stage2["Stage 2: Content Separation"]
        ContentList["content_list"] --> SepFunc["separate_content()"]
        SepFunc --> TextOut["text_content (str)"]
        SepFunc --> MMOut["multimodal_items (list)"]
    end
    
    subgraph Stage3["Stage 3: Context Setup"]
        MMOut --> ContextSetup["set_content_source_for_context()"]
        ContextSetup --> ContextReady["ContextExtractor ready"]
    end
    
    subgraph Stage4["Stage 4: Text Insertion"]
        TextOut --> InsertText["insert_text_content()"]
        InsertText --> LightRAGInsert["lightrag.ainsert()"]
        LightRAGInsert --> TextToKG["Text indexed in KG"]
    end
    
    subgraph Stage5["Stage 5: Multimodal Processing"]
        ContextReady --> MMProcess["_process_multimodal_content_batch_type_aware()"]
        MMProcess --> BatchGen["Concurrent generate_description_only()"]
        BatchGen --> ChunkStore["Store multimodal chunks"]
        ChunkStore --> EntityExtractMM["extract_entities()"]
        EntityExtractMM --> BelongsTo["Add 'belongs_to' relations"]
        BelongsTo --> MMToKG["Merge to KG"]
    end
    
    subgraph Stage6["Stage 6: Status Update"]
        MMToKG --> MarkMultimodal["_mark_multimodal_processing_complete()"]
    end
    
    subgraph Stage7["Stage 7: Finalization"]
        MarkMultimodal --> FinalStatus["doc_status = PROCESSED"]
        FinalStatus --> Done["index_done_callback()"]
    end
    
    CacheReturn --> Stage2
    StoreCache --> Stage2
```

Sources: [raganything/processor.py:1444-1532](), [raganything/utils.py:18-54](), [raganything/processor.py:706-881]()

---

## Content Separation Logic

Content separation divides the parsed `content_list` into text and multimodal components using the `separate_content` utility.

### Separation Algorithm

| Input Type | Classification | Logic |
|------------|---------------|-------|
| `{"type": "text", ...}` | Text | Appended to a buffer and joined with `\n\n` [raganything/utils.py:34-36](). |
| `{"type": "image", ...}` | Multimodal | Added to `multimodal_items` list [raganything/utils.py:44-46](). |
| `{"type": "table", ...}` | Multimodal | Added to `multimodal_items` list [raganything/utils.py:44-46](). |
| `{"type": "equation", ...}` | Multimodal | Added to `multimodal_items` list [raganything/utils.py:44-46](). |

**Note**: The logic iterates through the `content_list` once, ensuring all non-text types are treated as multimodal content [raganything/utils.py:29-50]().

---

## Multimodal Content Processing Internals

Multimodal content processing employs a batch processing architecture to optimize throughput via concurrent operations.

### Batch Processing Lifecycle

The method `_process_multimodal_content_batch_type_aware()` handles the heavy lifting:

1.  **Concurrency Control**: Uses an `asyncio.Semaphore` initialized with `lightrag.max_parallel_insert` to limit concurrent LLM/VLM calls [raganything/processor.py:732](), [raganything/processor.py:748]().
2.  **Description Generation**: Iterates through items and calls the specific processor's `generate_description_only()` method concurrently [raganything/processor.py:750-775]().
3.  **Chunk Creation**: For each processed item, it applies a chunk template (e.g., `image_chunk`, `table_chunk`) via `_apply_chunk_template()` [raganything/processor.py:848-870]().
4.  **KG Integration**:
    *   Inserts the multimodal chunk into `text_chunks` storage [raganything/processor.py:1012-1014]().
    *   Extracts entities from the generated description [raganything/processor.py:1176-1203]().
    *   Creates a `belongs_to` relationship between extracted entities and the multimodal item itself (e.g., "Figure 1") [raganything/processor.py:1205-1267]().

Sources: [raganything/processor.py:706-881](), [raganything/processor.py:931-1004](), [raganything/processor.py:1205-1267]()

---

## Document Status Tracking

The `ProcessorMixin` maintains detailed status records in the `doc_status` storage.

### Status Transitions

| State | Trigger | Method |
|-------|---------|--------|
| `READY` | Initial record creation | `_ensure_doc_status_record()` [raganything/processor.py:105-136]() |
| `HANDLING` | Start of text/multimodal processing | `insert_text_content()` [raganything/utils.py:74-83]() |
| `PROCESSED` | All stages finished successfully | `_mark_multimodal_processing_complete()` [raganything/processor.py:1345-1366]() |
| `FAILED` | Exception during processing | `process_document_complete_lightrag_api()` [raganything/processor.py:1651-1666]() |

### Multimodal Completion Flag

Because standard LightRAG status might not track multimodal stages, RAG-Anything uses a `multimodal_processed` flag.
*   Stored within the `doc_status` record if supported [raganything/processor.py:193-194]().
*   Stored in a separate `multimodal_status_cache` for compatibility [raganything/processor.py:171-187]().

Sources: [raganything/processor.py:105-136](), [raganything/processor.py:189-200](), [raganything/base.py:13-17]()

---

## File and ID Management

### File Reference Logic
The method `_get_file_reference()` determines how files are cited in the database.
*   If `config.use_full_path` is `True`, the absolute path is used [raganything/processor.py:45-46]().
*   Otherwise, only the `os.path.basename` is stored [raganything/processor.py:47-48]().

### Content-Based Doc ID
`_generate_content_based_doc_id()` creates a deterministic ID by hashing a "signature" of the document's contents (text blocks, image paths, table bodies). This prevents duplicate indexing of identical content across different file names [raganything/processor.py:202-230]().

Sources: [raganything/processor.py:35-49](), [raganything/processor.py:202-230]()

---

# Page: Parse Caching System

# Parse Caching System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [raganything/processor.py](raganything/processor.py)
- [raganything/raganything.py](raganything/raganything.py)
- [tests/test_insert_content_list.py](tests/test_insert_content_list.py)

</details>



## Purpose and Scope

This document describes RAG-Anything's parse caching system, which optimizes document processing performance by storing and reusing parsing results. The system eliminates redundant document parsing operations by maintaining a cache of previously parsed content lists indexed by file characteristics and parsing configuration.

For information about the document parsing process itself, see [Document Parsers](#4.1). For details on how parsed content is subsequently processed, see [Processing Pipeline Internals](#4.2).

**Sources:** [raganything/processor.py:1-438]()

---

## System Architecture

The parse caching system consists of three core operations managed by the `ProcessorMixin` class: cache key generation, cache retrieval, and cache storage. The cache stores the complete parsed `content_list` and the generated `doc_id` for each successfully parsed document.

```mermaid
graph TB
    subgraph "Parse Request"
        REQ["ProcessorMixin.parse_document()"]
        FILE["File Path + Config"]
    end
    
    subgraph "Cache Key Generation"
        KEYGEN["ProcessorMixin._generate_cache_key()"]
        FILEINFO["File Metadata<br/>mtime, absolute path"]
        PARSECONFIG["Parse Configuration<br/>parser, parse_method, kwargs"]
        MD5["hashlib.md5"]
        CACHEKEY["cache_key"]
    end
    
    subgraph "Cache Lookup"
        LOOKUP["ProcessorMixin._get_cached_result()"]
        PARSECACHE["self.parse_cache<br/>(LightRAG KV Storage)"]
        VALIDATE["Validation<br/>mtime + config check"]
        RESULT["content_list, doc_id"]
    end
    
    subgraph "Parser Execution"
        PARSER["Parser Registry<br/>(Mineru/Docling/Paddle)"]
        CONTENTLIST["content_list"]
        DOCID["ProcessorMixin._generate_content_based_doc_id()"]
    end
    
    subgraph "Cache Storage"
        STORE["ProcessorMixin._store_cached_result()"]
        CACHEDATA["Cache Entry<br/>content_list, doc_id,<br/>mtime, parse_config,<br/>cached_at, cache_version"]
        UPSERT["self.parse_cache.upsert()"]
        PERSIST["index_done_callback()"]
    end
    
    REQ --> FILE
    FILE --> KEYGEN
    KEYGEN --> FILEINFO
    KEYGEN --> PARSECONFIG
    FILEINFO --> MD5
    PARSECONFIG --> MD5
    MD5 --> CACHEKEY
    
    CACHEKEY --> LOOKUP
    LOOKUP --> PARSECACHE
    PARSECACHE --> VALIDATE
    VALIDATE -->|Cache Hit| RESULT
    VALIDATE -->|Cache Miss| PARSER
    
    PARSER --> CONTENTLIST
    CONTENTLIST --> DOCID
    CONTENTLIST --> STORE
    DOCID --> STORE
    
    STORE --> CACHEDATA
    CACHEDATA --> UPSERT
    UPSERT --> PERSIST
    PERSIST --> PARSECACHE
    
    RESULT --> REQ
    CONTENTLIST --> REQ
```

**Diagram: Parse Caching System Architecture**

**Sources:** [raganything/processor.py:32-438](), [raganything/raganything.py:94-95]()

---

## Cache Key Generation

The `_generate_cache_key()` method creates a unique cache identifier by combining file metadata with parsing configuration. The cache key is deterministic: identical files with identical parsing settings always produce the same key.

### Key Components

The cache key incorporates the following elements:

| Component | Purpose | Source |
|-----------|---------|--------|
| `file_path` | Absolute path to the file | `Path.absolute()` [raganything/processor.py:70]() |
| `mtime` | File modification timestamp | `Path.stat().st_mtime` [raganything/processor.py:66]() |
| `parser` | Parser type (mineru/docling) | `self.config.parser` [raganything/processor.py:72]() |
| `parse_method` | Parsing method (auto/ocr/txt) | `self.config.parse_method` or parameter [raganything/processor.py:73]() |
| `kwargs` | Relevant parser parameters | Filtered from `**kwargs` [raganything/processor.py:77-92]() |

### Relevant Parser Parameters

Only parsing-relevant keyword arguments are included in the cache key:

```python
relevant_kwargs = ["lang", "device", "start_page", "end_page", 
                   "formula", "table", "backend", "source"]
```

**Sources:** [raganything/processor.py:77-92]()

### Generation Process

```mermaid
graph LR
    subgraph "Input"
        FILEPATH["file_path: Path"]
        METHOD["parse_method: str"]
        KWARGS["**kwargs"]
    end
    
    subgraph "Metadata Collection"
        MTIME["file_path.stat().st_mtime"]
        ABSPATH["str(file_path.absolute())"]
        PARSER["self.config.parser"]
        PARSEMETHOD["parse_method or<br/>self.config.parse_method"]
    end
    
    subgraph "Configuration Dictionary"
        CONFIGDICT["config_dict = {<br/>file_path: absolute path,<br/>mtime: timestamp,<br/>parser: parser type,<br/>parse_method: method<br/>}"]
        FILTER["Filter relevant_kwargs<br/>from **kwargs"]
        MERGE["config_dict.update(<br/>relevant_kwargs)"]
    end
    
    subgraph "Hash Generation"
        JSONSTR["json.dumps(<br/>config_dict,<br/>sort_keys=True)"]
        MD5HASH["hashlib.md5.hexdigest()"]
        CACHEKEY["cache_key"]
    end
    
    FILEPATH --> MTIME
    FILEPATH --> ABSPATH
    METHOD --> PARSEMETHOD
    
    MTIME --> CONFIGDICT
    ABSPATH --> CONFIGDICT
    PARSER --> CONFIGDICT
    PARSEMETHOD --> CONFIGDICT
    
    KWARGS --> FILTER
    FILTER --> MERGE
    CONFIGDICT --> MERGE
    
    MERGE --> JSONSTR
    JSONSTR --> MD5HASH
    MD5HASH --> CACHEKEY
```

**Diagram: Cache Key Generation Flow**

**Sources:** [raganything/processor.py:50-98]()

---

## Cache Retrieval

The `_get_cached_result()` method attempts to retrieve a previously cached parsing result. It performs validation checks to ensure the cached data is still valid.

### Retrieval Flow

```mermaid
sequenceDiagram
    participant PM as ProcessorMixin
    participant GCR as _get_cached_result()
    participant CACHE as self.parse_cache
    participant FS as File System
    
    PM->>GCR: cache_key, file_path, parse_method, **kwargs
    
    GCR->>GCR: Check parse_cache exists
    alt parse_cache is None
        GCR-->>PM: return None
    end
    
    GCR->>CACHE: get_by_id(cache_key)
    CACHE-->>GCR: cached_data or None
    
    alt cached_data is None
        GCR-->>PM: return None
    end
    
    GCR->>FS: file_path.stat().st_mtime
    FS-->>GCR: current_mtime
    
    GCR->>GCR: Compare current_mtime vs<br/>cached_data["mtime"]
    
    alt mtime mismatch
        GCR->>GCR: Log "Cache invalid - file modified"
        GCR-->>PM: return None
    end
    
    GCR->>GCR: Build current_config<br/>(parser, parse_method, kwargs)
    GCR->>GCR: Compare current_config vs<br/>cached_data["parse_config"]
    
    alt config mismatch
        GCR->>GCR: Log "Cache invalid - config changed"
        GCR-->>PM: return None
    end
    
    GCR->>GCR: Extract content_list, doc_id
    
    alt content_list or doc_id missing
        GCR->>GCR: Log "Cache incomplete"
        GCR-->>PM: return None
    end
    
    GCR->>GCR: Log "Found valid cached result"
    GCR-->>PM: (content_list, doc_id)
```

**Diagram: Cache Retrieval Sequence**

**Sources:** [raganything/processor.py:118-195]()

### Validation Checks

The cache retrieval performs three critical validation steps:

1. **Existence Check**: Verifies cached entry exists for the cache key [raganything/processor.py:137-140]()
2. **Modification Time Check**: Compares current file `mtime` with cached `mtime` [raganything/processor.py:142-149]()
3. **Configuration Check**: Compares current parsing config with cached `parse_config` [raganything/processor.py:151-176]()

If any validation fails, the method returns `None` and triggers a fresh parse.

**Sources:** [raganything/processor.py:137-176]()

---

## Cache Storage

The `_store_cached_result()` method persists parsing results to the cache after successful document parsing.

### Storage Process

```mermaid
graph TB
    subgraph "Input Data"
        CACHEKEY["cache_key"]
        CONTENTLIST["content_list"]
        DOCID["doc_id"]
        FILEPATH["file_path"]
        METHOD["parse_method"]
        KWARGS["**kwargs"]
    end
    
    subgraph "Metadata Collection"
        MTIME["file_path.stat().st_mtime"]
        PARSECONFIG["parse_config = {<br/>parser: self.config.parser,<br/>parse_method: method,<br/>...relevant_kwargs<br/>}"]
        TIMESTAMP["time.time()"]
        VERSION["cache_version: '1.0'"]
    end
    
    subgraph "Cache Entry Construction"
        CACHEDATA["cache_data = {<br/>cache_key: {<br/>  content_list: list,<br/>  doc_id: str,<br/>  mtime: float,<br/>  parse_config: dict,<br/>  cached_at: timestamp,<br/>  cache_version: '1.0'<br/>}<br/>}"]
    end
    
    subgraph "Storage Operations"
        UPSERT["self.parse_cache.upsert(<br/>cache_data)"]
        CALLBACK["self.parse_cache.<br/>index_done_callback()"]
        LOG["Log: Stored parsing result"]
    end
    
    CACHEKEY --> CACHEDATA
    CONTENTLIST --> CACHEDATA
    DOCID --> CACHEDATA
    
    FILEPATH --> MTIME
    METHOD --> PARSECONFIG
    KWARGS --> PARSECONFIG
    MTIME --> CACHEDATA
    PARSECONFIG --> CACHEDATA
    TIMESTAMP --> CACHEDATA
    VERSION --> CACHEDATA
    
    CACHEDATA --> UPSERT
    UPSERT --> CALLBACK
    CALLBACK --> LOG
```

**Diagram: Cache Storage Flow**

**Sources:** [raganything/processor.py:197-263]()

### Cache Entry Structure

Each cache entry contains the following fields:

```python
{
    "cache_key": {
        "content_list": List[Dict[str, Any]],    # Parsed document content
        "doc_id": str,                           # Content-based document ID
        "mtime": float,                          # File modification time
        "parse_config": {                        # Parsing configuration
            "parser": str,                       # "mineru", "docling", "paddle"
            "parse_method": str,                 # "auto", "ocr", or "txt"
            # ...additional relevant kwargs
        },
        "cached_at": float,                      # Cache creation timestamp
        "cache_version": str                     # Cache format version ("1.0")
    }
}
```

**Sources:** [raganything/processor.py:248-257]()

---

## Cache Invalidation Conditions

The cache automatically invalidates under specific conditions to ensure data consistency:

| Condition | Detection Method | Action |
|-----------|------------------|--------|
| **File Modified** | Compare `current_mtime` with `cached_mtime` | Return `None`, trigger fresh parse |
| **Parser Changed** | Compare `self.config.parser` with `cached_config["parser"]` | Return `None`, trigger fresh parse |
| **Parse Method Changed** | Compare current `parse_method` with `cached_config["parse_method"]` | Return `None`, trigger fresh parse |
| **Kwargs Changed** | Compare relevant kwargs with cached kwargs | Return `None`, trigger fresh parse |
| **Missing Cache Entry** | `get_by_id()` returns `None` | Return `None`, trigger fresh parse |
| **Incomplete Cache Data** | Missing `content_list` or `doc_id` | Return `None`, trigger fresh parse |

**Sources:** [raganything/processor.py:142-189]()

---

## Integration with Parse Pipeline

The cache integrates seamlessly into the document parsing workflow in the `parse_document()` method:

```mermaid
sequenceDiagram
    participant USER as User/Caller
    participant PD as ProcessorMixin.parse_document()
    participant GCK as ProcessorMixin._generate_cache_key()
    participant GCR as ProcessorMixin._get_cached_result()
    participant PARSER as Parser Registry
    participant GDID as ProcessorMixin._generate_content_based_doc_id()
    participant SCR as ProcessorMixin._store_cached_result()
    
    USER->>PD: file_path, parse_method, **kwargs
    
    PD->>GCK: file_path, parse_method, **kwargs
    GCK-->>PD: cache_key
    
    PD->>GCR: cache_key, file_path, parse_method, **kwargs
    
    alt Cache Hit
        GCR-->>PD: (content_list, doc_id)
        PD->>PD: Log "Using cached parsing result"
        PD-->>USER: (content_list, doc_id)
    else Cache Miss
        GCR-->>PD: None
        PD->>PD: Log "Cache miss, parsing document"
        
        PD->>PARSER: get_parser().parse_document()
        PARSER-->>PD: content_list
        
        PD->>GDID: content_list
        GDID-->>PD: doc_id
        
        PD->>SCR: cache_key, content_list, doc_id,<br/>file_path, parse_method, **kwargs
        SCR->>SCR: Store in parse_cache
        SCR-->>PD: (stored)
        
        PD-->>USER: (content_list, doc_id)
    end
```

**Diagram: Cache Integration in parse_document()**

**Sources:** [raganything/processor.py:265-438]()

### Implementation Details

The `parse_document()` method checks the cache early in its execution:

1. **Generate cache key** using file path and configuration [raganything/processor.py:301]()
2. **Check cache** by calling `_get_cached_result()` [raganything/processor.py:304-306]()
3. **Return cached result** if valid, with logging [raganything/processor.py:307-314]()
4. **Parse document** if cache miss [raganything/processor.py:319-406]()
5. **Generate doc_id** from content [raganything/processor.py:414]()
6. **Store result** in cache for future use [raganything/processor.py:417-419]()

**Sources:** [raganything/processor.py:301-419]()

---

## Cache Storage Backend

The parse cache uses the `self.parse_cache` storage backend, which must implement the following interface:

### Required Methods

| Method | Purpose | Usage in Cache System |
|--------|---------|----------------------|
| `get_by_id(id)` | Retrieve entry by cache key | Cache lookup in `_get_cached_result()` |
| `upsert(data)` | Insert or update cache entries | Store parsed results in `_store_cached_result()` |
| `index_done_callback()` | Persist changes to disk | Ensure cache durability after storage |

The parse cache is typically a key-value store instantiated in the `RAGAnything` class initialization [raganything/raganything.py:94-95](). The cache backend is separate from LightRAG's primary storage systems and is specifically optimized for storing large content lists.

**Sources:** [raganything/processor.py:133-134, 137, 258, 260](), [raganything/raganything.py:94-95]()

---

## Performance Characteristics

### Cache Hit Benefits

When the cache contains a valid entry:

- **Parsing Time**: Eliminated (0 seconds vs. seconds/minutes)
- **API Calls**: None (no external parser process invocation)
- **I/O Operations**: Minimal (single KV store lookup)
- **Memory**: Efficient (cached content_list loaded directly)

### Cache Miss Overhead

When cache lookup fails:

- **Additional Time**: ~1-5ms for cache key generation and lookup
- **Storage Write**: One `upsert()` operation after parsing
- **Negligible Impact**: Cache operations add <1% to total parse time

### Storage Requirements

Cache storage scales with document corpus:

- **Per Document**: Size of serialized `content_list` + metadata (~1-100 MB typical)
- **Cache Key**: 32 characters (MD5 hash)
- **Metadata**: ~200 bytes per entry

**Sources:** [raganything/processor.py:29-438]()

---

## Implementation Notes

### Error Handling

The cache system is designed to fail gracefully:

```python
try:
    cached_data = await self.parse_cache.get_by_id(cache_key)
    # ...validation logic...
except Exception as e:
    self.logger.warning(f"Error accessing parse cache: {e}")
    return None
```

Any cache access error results in a cache miss, triggering a fresh parse. This ensures the system continues functioning even if the cache backend fails.

**Sources:** [raganything/processor.py:192-194, 262-263]()

### Cache Versioning

The cache includes a `cache_version` field (currently `"1.0"`) to support future format changes. This allows for graceful migration if the cache structure needs to evolve.

**Sources:** [raganything/processor.py:255]()

### Async Operations

All cache operations are asynchronous (`async`/`await`) to prevent blocking during cache I/O:

- `_get_cached_result()` is async [raganything/processor.py:118]()
- `_store_cached_result()` is async [raganything/processor.py:197]()
- Cache backend methods (`get_by_id()`, `upsert()`, `index_done_callback()`) are async [raganything/processor.py:137, 258, 260]()

**Sources:** [raganything/processor.py:118, 197, 137, 258, 260]()

---

## Configuration

The parse cache is initialized when `RAGAnything` is instantiated. The cache backend is typically configured through the working directory structure.

### Cache Location

The parse cache storage location is determined by:

```
{working_dir}/parse_cache/
```

This directory contains the key-value store files for cached parsing results.

### Disabling Cache

To disable parse caching, set `self.parse_cache = None` before calling `parse_document()`. The cache methods check for `None` and skip caching operations:

```python
if not hasattr(self, "parse_cache") or self.parse_cache is None:
    return None  # Skip cache operations
```

**Sources:** [raganything/processor.py:133-134, 217-218]()

---

# Page: Document Status Tracking

# Document Status Tracking

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [raganything/base.py](raganything/base.py)
- [raganything/processor.py](raganything/processor.py)
- [tests/test_insert_content_list.py](tests/test_insert_content_list.py)

</details>



## Purpose and Scope

This document describes RAG-Anything's document status tracking system, which monitors the processing lifecycle of documents from initial parsing through text and multimodal content indexing. The system enables skip logic for already-processed documents, provides visibility into processing failures, and distinguishes between text and multimodal processing completion states using the `doc_status` storage and a specialized `multimodal_processed` flag.

For information about the overall document processing pipeline, see [Document Processing](#4). For details on multimodal content processing specifically, see [Multimodal Content Processing](#5).

**Sources:** [raganything/base.py:1-13](), [raganything/processor.py:1-32]()

---

## DocStatus Enumeration

The `DocStatus` enum defines the lifecycle states a document can occupy during processing. It is implemented as a string-based enumeration in [raganything/base.py:4-12]() to ensure compatibility with JSON serialization for storage backends.

| State | Value | Description |
|-------|-------|-------------|
| `READY` | `"ready"` | Document is queued for processing but not yet started |
| `HANDLING` | `"handling"` | Document is being prepared for processing (initial setup) |
| `PENDING` | `"pending"` | Document is waiting for resources or dependencies |
| `PROCESSING` | `"processing"` | Document is actively being processed |
| `PROCESSED` | `"processed"` | Text processing is complete (multimodal may still be pending) |
| `FAILED` | `"failed"` | Processing encountered an unrecoverable error |

**Sources:** [raganything/base.py:4-12]()

---

## Document Status State Machine

The following diagram illustrates the valid state transitions during document processing within the `ProcessorMixin`.

```mermaid
stateDiagram-v2
    [*] --> READY: _ensure_doc_status_record()
    READY --> HANDLING: _upsert_doc_status()
    HANDLING --> PROCESSING: Text Insertion Starts
    PROCESSING --> PROCESSED: LightRAG ainsert() success
    PROCESSING --> FAILED: Exception caught
    PROCESSED --> PROCESSED: Multimodal Processing
    FAILED --> READY: Retry logic
    
    note right of PROCESSED
        multimodal_processed flag
        tracks non-textual elements
    end note
```

**Sources:** [raganything/base.py:4-12](), [raganything/processor.py:105-160]()

---

## Document Status Data Structure

Document status is stored in LightRAG's `doc_status` key-value storage. RAG-Anything extends the standard LightRAG schema with multimodal tracking fields.

| Field | Type | Description |
|-------|------|-------------|
| `status` | `str` | Current `DocStatus` enum value [raganything/base.py:4-12]() |
| `chunks_list` | `List[str]` | List of chunk IDs (text + multimodal) [raganything/processor.py:125-126]() |
| `multimodal_processed` | `bool` | Flag indicating non-textual element integration [raganything/processor.py:193-194]() |
| `updated_at` | `str` | UTC timestamp of last update [raganything/processor.py:101-103]() |
| `file_path` | `str` | Path reference (absolute or relative) [raganything/processor.py:129]() |

```mermaid
graph LR
    subgraph "doc_status Storage (KV Store)"
        DOC_ID["doc_id (key)"]
        STATUS["status: DocStatus"]
        CHUNKS_LIST["chunks_list: List[str]"]
        MULTIMODAL["multimodal_processed: bool"]
        UPDATED["updated_at: str"]
        FILE_REF["file_path: str"]
    end
    
    DOC_ID --> STATUS
    DOC_ID --> CHUNKS_LIST
    DOC_ID --> MULTIMODAL
    DOC_ID --> UPDATED
    DOC_ID --> FILE_REF
```

**Sources:** [raganything/processor.py:113-137](), [raganything/processor.py:138-160](), [raganything/processor.py:189-200]()

---

## Document Processing Lifecycle

The processing pipeline uses `_ensure_doc_status_record` [raganything/processor.py:105-137]() to initialize records and `_upsert_doc_status` [raganything/processor.py:138-160]() to update them.

```mermaid
sequenceDiagram
    participant P as ProcessorMixin
    participant LS as lightrag.doc_status
    participant MS as multimodal_status_cache
    
    P->>LS: get_by_id(doc_id)
    alt Record missing
        P->>LS: upsert({doc_id: status=READY})
        P->>LS: index_done_callback()
    end
    
    Note over P: Perform Text Insertion
    P->>LS: upsert({doc_id: status=PROCESSED})
    
    Note over P: Perform Multimodal Analysis
    P->>MS: upsert({doc_id: multimodal_processed=True})
    P->>MS: index_done_callback()
```

**Sources:** [raganything/processor.py:105-137](), [raganything/processor.py:138-160](), [raganything/processor.py:171-188]()

---

## Multimodal Status Tracking

RAG-Anything uses a dual-tracking strategy for multimodal content. While text status is tracked in `doc_status`, the `multimodal_processed` flag may be stored in a separate `multimodal_status_cache` for compatibility [raganything/processor.py:161-170]().

### Multimodal Flag Resolution
The method `_get_multimodal_processed_flag` resolves the completion state by checking two locations in order:
1. The `doc_status` dictionary itself [raganything/processor.py:193-194]().
2. The `multimodal_status_cache` (KV namespace) if not found in the primary record [raganything/processor.py:196-198]().

### Implementation Details
*   **Initialization**: `_ensure_doc_status_record` creates a minimal entry with `status=READY` and an empty `chunks_list` [raganything/processor.py:113-132]().
*   **Persistence**: Every update calls `index_done_callback()` to ensure the underlying storage backend flushes changes [raganything/processor.py:135](), [raganything/processor.py:158](), [raganything/processor.py:187]().
*   **Timestamping**: Stable UTC timestamps are generated via `_current_doc_status_timestamp` using `%Y-%m-%dT%H:%M:%S+00:00` format [raganything/processor.py:101-103]().

**Sources:** [raganything/processor.py:101-103](), [raganything/processor.py:161-200]()

---

## Code Entity Reference Map

The following diagram maps internal tracking functions to their storage interactions.

```mermaid
graph TB
    subgraph "ProcessorMixin Entities"
        ENSURE["_ensure_doc_status_record()"]
        UPSERT["_upsert_doc_status()"]
        GET_MM["_get_multimodal_processed_flag()"]
        SET_MM["_set_multimodal_status_record()"]
    end
    
    subgraph "Storage Entities"
        LR_DS["lightrag.doc_status"]
        MM_CACHE["multimodal_status_cache"]
    end
    
    ENSURE -->|get/upsert| LR_DS
    UPSERT -->|upsert| LR_DS
    GET_MM -->|read| LR_DS
    GET_MM -->|read| MM_CACHE
    SET_MM -->|upsert| MM_CACHE
    
    style LR_DS stroke-dasharray: 5 5
    style MM_CACHE stroke-dasharray: 5 5
```

**Sources:** [raganything/processor.py:105-137](), [raganything/processor.py:138-160](), [raganything/processor.py:171-188](), [raganything/processor.py:189-200]()

---

## Status Updates Summary

| Event | Function | Status Result |
|-------|----------|---------------|
| Initial Registration | `_ensure_doc_status_record` | `READY` [raganything/processor.py:111]() |
| Start Processing | `_upsert_doc_status` | `HANDLING` / `PROCESSING` |
| Text Inserted | `lightrag.ainsert` | `PROCESSED` [tests/test_insert_content_list.py:86]() |
| Multimodal Done | `_set_multimodal_status_record` | `multimodal_processed = True` [raganything/processor.py:182]() |
| Failure | Pipeline Exception | `FAILED` [raganything/base.py:12]() |

**Sources:** [raganything/processor.py:111-134](), [raganything/processor.py:179-185](), [tests/test_insert_content_list.py:82-98]()

---

# Page: Batch Processing

# Batch Processing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/batch_processing.md](docs/batch_processing.md)
- [docs/enhanced_markdown.md](docs/enhanced_markdown.md)
- [examples/batch_dry_run_example.py](examples/batch_dry_run_example.py)
- [examples/batch_processing_example.py](examples/batch_processing_example.py)
- [examples/enhanced_markdown_example.py](examples/enhanced_markdown_example.py)
- [raganything/batch.py](raganything/batch.py)
- [raganything/batch_parser.py](raganything/batch_parser.py)
- [raganything/query.py](raganything/query.py)
- [tests/test_custom_parser.py](tests/test_custom_parser.py)

</details>



RAG-Anything provides robust batch processing capabilities through the `BatchMixin` and the specialized `BatchParser` class. These components enable efficient ingestion of large document collections via concurrent processing, progress tracking, and detailed result reporting.

## Overview

Batch processing in RAG-Anything is designed for high throughput and reliability. It abstracts the complexity of managing multiple asynchronous tasks, allowing users to process entire directories or lists of files with a single method call.

Key components include:
- **`BatchMixin`**: A mixin for the `RAGAnything` class providing high-level batch methods [raganything/batch.py:19-21]().
- **`BatchParser`**: A standalone utility for parallel document parsing [raganything/batch_parser.py:53-59]().
- **`BatchProcessingResult`**: A dataclass containing success rates, timing, and error details [raganything/batch_parser.py:21-32]().

## Key Methods

### 1. process_folder_complete
The primary entry point for processing all supported documents within a directory. It handles file discovery, concurrency control via semaphores, and final statistics reporting [raganything/batch.py:34-45]().

### 2. process_documents_batch
A flexible method to process a specific list of file paths. It utilizes `BatchParser` internally to handle the parsing stage in parallel [raganything/batch.py:177-186]().

### 3. process_documents_with_rag_batch
An end-to-end asynchronous method that first parses documents in batch and then sequentially inserts them into the LightRAG knowledge base [raganything/batch.py:255-265]().

## System Architecture

The following diagram bridges the high-level batch request to the internal code entities.

### Batch Processing Architecture

```mermaid
graph TD
    subgraph "Public API (raganything/batch.py)"
        B_MIX["BatchMixin"]
        PFC["process_folder_complete"]
        PDB["process_documents_batch"]
        PDRB["process_documents_with_rag_batch"]
    end

    subgraph "Parallel Engine (raganything/batch_parser.py)"
        BP["BatchParser"]
        PB["process_batch"]
        PBA["process_batch_async"]
        BPR["BatchProcessingResult"]
    end

    subgraph "Concurrency & Execution"
        TPE["ThreadPoolExecutor"]
        SEM["asyncio.Semaphore"]
        TQDM["tqdm (Progress Bar)"]
    end

    B_MIX --> BP
    PFC --> SEM
    PDB --> PB
    PDRB --> PBA
    PB --> TPE
    PBA --> TPE
    PB --> BPR
    PBA --> BPR
    PFC --> TQDM
    PB --> TQDM
```

Sources: [raganything/batch.py:19-21](), [raganything/batch_parser.py:53-59](), [raganything/batch_parser.py:203-210]()

## Concurrency and Resource Control

RAG-Anything manages system resources during batch operations through two primary mechanisms:

1.  **Async Semaphores**: In `process_folder_complete`, an `asyncio.Semaphore` is initialized using `max_workers` (defaulting to `config.max_concurrent_files`) to limit the number of simultaneous `process_document_complete` tasks [raganything/batch.py:106-110]().
2.  **Thread Pools**: The `BatchParser` uses a `ThreadPoolExecutor` to run CPU-bound parsing tasks in parallel, preventing the event loop from blocking [raganything/batch_parser.py:231-235]().

### Data Flow: Batch Parsing to Result

```mermaid
sequenceDiagram
    participant User
    participant RAG as RAGAnything (BatchMixin)
    participant BP as BatchParser
    participant P as Parser (Mineru/Docling)
    
    User->>RAG: process_documents_batch(file_paths)
    RAG->>BP: process_batch(file_paths, output_dir)
    Note over BP: Filter supported extensions
    
    loop Parallel Execution (max_workers)
        BP->>P: parse_document(file_path)
        P-->>BP: content_list
    end
    
    BP-->>RAG: BatchProcessingResult (successful_files, errors)
    RAG-->>User: Summary & Statistics
```

Sources: [raganything/batch.py:177-186](), [raganything/batch_parser.py:203-210](), [raganything/batch_parser.py:158-160]()

## Dry-Run Mode

The `BatchParser` supports a `dry_run` mode. When enabled, the system performs file discovery and extension filtering but skips the actual parsing logic [raganything/batch_parser.py:209-215](). This is useful for verifying which files in a large directory are supported by the selected parser (e.g., Mineru vs. Docling) before committing resources [examples/batch_dry_run_example.py:43-49]().

## Configuration Parameters

Batch processing behavior is governed by both method arguments and `RAGAnythingConfig` defaults.

| Parameter | Source | Description |
| :--- | :--- | :--- |
| `max_workers` | `MAX_CONCURRENT_FILES` | Max parallel tasks for parsing/processing [raganything/batch.py:71-72](). |
| `recursive` | `RECURSIVE_FOLDER_PROCESSING` | Whether to scan subdirectories [raganything/batch.py:68-69](). |
| `file_extensions` | `SUPPORTED_FILE_EXTENSIONS` | List of extensions to include in batch [raganything/batch.py:66-67](). |
| `timeout_per_file` | Constructor | Max seconds allowed for a single file parse [raganything/batch_parser.py:66-68](). |

Sources: [raganything/batch.py:60-72](), [raganything/batch_parser.py:61-68]()

## Implementation Details

### Result Tracking
The `BatchProcessingResult` dataclass tracks:
- `successful_files`: List of paths that completed without error [raganything/batch_parser.py:25]().
- `failed_files`: List of paths that encountered exceptions [raganything/batch_parser.py:26]().
- `errors`: A dictionary mapping file paths to their specific error messages [raganything/batch_parser.py:29]().
- `processing_time`: Total wall-clock time for the batch operation [raganything/batch_parser.py:28]().

### File Discovery
The system uses `pathlib` for robust path handling. `filter_supported_files` automatically identifies files based on the parser's supported formats (Office, Image, Text, and PDF) [raganything/batch_parser.py:110-123](). It handles both explicit file lists and directory scanning [raganything/batch_parser.py:126-152]().

Sources: [raganything/batch_parser.py:21-32](), [raganything/batch_parser.py:110-156]()

---

# Page: Multimodal Content Processing

# Multimodal Content Processing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [raganything/modalprocessors.py](raganything/modalprocessors.py)

</details>



## Purpose and Scope

This document describes the multimodal content processing subsystem in RAG-Anything, which analyzes and transforms non-textual content (images, tables, equations) into structured, searchable knowledge. The system deploys specialized processors for each content modality, extracting semantic information and creating entities in the knowledge graph.

For information about the overall document processing pipeline, see [Document Processing](#4). For details on specific processor implementations, see the following child pages:
- [Modal Processor Architecture](#5.1) — Explain the `BaseModalProcessor` design, inheritance hierarchy, and processing flow.
- [Image Processing](#5.2) — Document `ImageModalProcessor`, vision model integration, and spatial relationship extraction.
- [Table Processing](#5.3) — Document `TableModalProcessor`, table structure analysis, and Markdown rendering.
- [Equation Processing](#5.4) — Document `EquationModalProcessor`, LaTeX formula handling, and OMML conversion.
- [Custom Modal Processors](#5.5) — Guide for creating custom modal processors using `GenericModalProcessor`.
- [Context Extraction](#5.6) — Detailed explanation of `ContextExtractor`, `ContextConfig`, and context-aware processing.

## Overview

The multimodal content processing system handles three primary responsibilities:

1. **Content-Specific Analysis**: Each content type (image, table, equation) receives specialized processing through dedicated modal processors that understand its semantic structure. [raganything/modalprocessors.py:1-10]()
2. **Context-Aware Enhancement**: Processors use `ContextExtractor` to retrieve surrounding textual context, improving description accuracy. [raganything/modalprocessors.py:55-66]()
3. **Knowledge Graph Integration**: Processed content is transformed into knowledge graph entities with `belongs_to` relationships connecting them to extracted textual entities. [raganything/modalprocessors.py:736-770]()

The system operates in two modes:
- **Immediate Mode**: Processes individual items and immediately performs entity/relationship extraction.
- **Batch Mode**: Generates descriptions in stage 1, defers entity extraction to stage 2 for concurrent processing. [raganything/modalprocessors.py:773-792]()

Sources: [raganything/modalprocessors.py:1-30](), [README.md:166-211]()

## System Architecture

### Multimodal Pipeline Overview

The following diagram bridges the Natural Language Space (descriptions/captions) to the Code Entity Space (classes and storage backends).

```mermaid
graph TB
    subgraph "Input Content"
        IMG_IN["Image Content<br/>{img_path, captions}"]
        TBL_IN["Table Content<br/>{table_body, captions}"]
        EQ_IN["Equation Content<br/>{text, latex}"]
    end
    
    subgraph "Context Extraction Layer"
        CE["ContextExtractor"]
        CC["ContextConfig"]
        CE --- CC
    end
    
    subgraph "Modal Processor Layer"
        BASE["BaseModalProcessor"]
        IMG_PROC["ImageModalProcessor"]
        TBL_PROC["TableModalProcessor"]
        EQ_PROC["EquationModalProcessor"]
        
        BASE <|-- IMG_PROC
        BASE <|-- TBL_PROC
        BASE <|-- EQ_PROC
    end
    
    subgraph "AI Services"
        VLM["vision_model_func<br/>(e.g., GPT-4o)"]
        LLM["llm_model_func<br/>(e.g., GPT-4o-mini)"]
    end
    
    subgraph "Storage (Code Entity Space)"
        CHUNK_DB["text_chunks_db"]
        CHUNK_VDB["chunks_vdb"]
        KG_INST["knowledge_graph_inst"]
        ENT_VDB["entities_vdb"]
    end
    
    IMG_IN --> IMG_PROC
    TBL_IN --> TBL_PROC
    EQ_IN --> EQ_PROC
    
    CE --> BASE
    
    IMG_PROC --> VLM
    TBL_PROC --> LLM
    EQ_PROC --> LLM
    
    BASE --> CHUNK_DB
    BASE --> CHUNK_VDB
    BASE --> KG_INST
    BASE --> ENT_VDB
```

Sources: [raganything/modalprocessors.py:360-401](), [raganything/modalprocessors.py:465-545](), [raganything/modalprocessors.py:796-1030]()

## Supported Content Types

| Content Type | Processor Class | AI Service | Primary Analysis |
|-------------|----------------|------------|------------------|
| **Image** | `ImageModalProcessor` | Vision Model (VLM) | Visual semantics, object detection, spatial relationships |
| **Table** | `TableModalProcessor` | Language Model (LLM) | Statistical patterns, data relationships |
| **Equation** | `EquationModalProcessor` | Language Model (LLM) | Mathematical concepts, domain mapping |
| **Generic** | `GenericModalProcessor` | Language Model (LLM) | Extensible framework for custom types |

Sources: [README.md:894-977](), [raganything/modalprocessors.py:824-929]()

## Modal Processor Architecture

All specialized processors inherit from `BaseModalProcessor`, which provides the core lifecycle for multimodal data. For a deep dive into the inheritance and storage dependency injection, see [Modal Processor Architecture](#5.1).

### Entity and Chunk Creation Lifecycle

The lifecycle follows a two-stage process:
1. **Description Generation**: Uses LLM/VLM to create a detailed semantic description.
2. **Entity Creation**: Inserts the description as a chunk and creates a corresponding entity node.

```mermaid
sequenceDiagram
    participant P as ModalProcessor
    participant AI as LLM/VLM Service
    participant KG as knowledge_graph_inst
    participant VDB as entities_vdb / chunks_vdb

    P->>AI: modal_caption_func(prompt)
    AI-->>P: JSON {detailed_description, entity_info}
    P->>P: _create_entity_and_chunk()
    P->>KG: upsert_node(entity_name)
    P->>VDB: upsert(vector_embeddings)
    P->>KG: extract_entities(description)
    P->>KG: upsert_edge(belongs_to)
```

Sources: [raganything/modalprocessors.py:465-545](), [raganything/modalprocessors.py:699-793]()

## Context-Aware Processing

The `ContextExtractor` enhances multimodal content analysis by providing surrounding textual context. This prevents processors from analyzing images or tables in isolation.

- **Modes**: Supports `page` (window around a page index) or `chunk` (window around a sequence index). [raganything/modalprocessors.py:43-44]()
- **Truncation**: Uses token-based truncation via `max_context_tokens` to stay within LLM context limits. [raganything/modalprocessors.py:45]()

For details on how context windows are calculated and filtered, see [Context Extraction](#5.6).

Sources: [raganything/modalprocessors.py:49-358](), [raganything/modalprocessors.py:406-440]()

## Robust JSON Parsing

The system implements a multi-strategy JSON parsing approach in `_robust_json_parse` to handle varied LLM response formats, including those from models with reasoning/thinking tags (e.g., DeepSeek, Qwen). [raganything/modalprocessors.py:547-550]()

Strategies include:
1. **Thinking Tag Removal**: Stripping `<thinking>` or `<thought>` blocks. [raganything/modalprocessors.py:579-589]()
2. **Candidate Extraction**: Using regex and brace-matching to find JSON objects within text. [raganything/modalprocessors.py:591-615]()
3. **Regex Fallback**: Extracting specific fields like `detailed_description` via regex if the JSON is malformed. [raganything/modalprocessors.py:657-688]()

Sources: [raganything/modalprocessors.py:547-698]()

## Integration with LightRAG

Modal processors are initialized within the `RAGAnything` class and utilize the underlying `LightRAG` storage components. [raganything/modalprocessors.py:365-375]()

- **Storage Injection**: Processors receive references to `text_chunks_db`, `entities_vdb`, and `knowledge_graph_inst`. [raganything/modalprocessors.py:488-510]()
- **Relationship Mapping**: The system automatically creates `belongs_to` edges to link multimodal elements to the textual entities mentioned in their descriptions. [raganything/modalprocessors.py:736-770]()

Sources: [raganything/modalprocessors.py:360-794](), [README.md:336-356]()

---

# Page: Modal Processor Architecture

# Modal Processor Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/context_aware_processing.md](docs/context_aware_processing.md)
- [examples/insert_content_list_example.py](examples/insert_content_list_example.py)
- [examples/modalprocessors_example.py](examples/modalprocessors_example.py)
- [raganything/modalprocessors.py](raganything/modalprocessors.py)
- [tests/test_embedding_examples.py](tests/test_embedding_examples.py)

</details>



## Purpose and Scope

This document describes the modal processor architecture that handles specialized analysis of multimodal content types (images, tables, equations, and custom content) in RAG-Anything. Modal processors transform raw multimodal content into enhanced textual descriptions, create knowledge graph entities, and establish relationships through the LightRAG framework.

The architecture is built on a two-stage lifecycle: generating descriptive content via Vision-Language Models (VLMs) or Large Language Models (LLMs), and then persisting that content into the LightRAG knowledge graph and vector storage.

**Sources:** [raganything/modalprocessors.py:1-10]()

## Base Processor Architecture

### Class Hierarchy

The modal processor system uses inheritance to provide shared functionality while allowing content-specific customization. The `BaseModalProcessor` provides the core logic for storage interaction and context management.

```mermaid
classDiagram
    class BaseModalProcessor {
        +LightRAG lightrag
        +modal_caption_func
        +ContextExtractor context_extractor
        +content_source
        +content_format
        +set_content_source(content_source, content_format)
        +generate_description_only(modal_content, item_info, entity_name)
        +process_multimodal_content(modal_content, content_type, file_path, entity_name, item_info, batch_mode)
        #_create_entity_and_chunk(modal_chunk, entity_info, file_path, batch_mode)
        #_process_chunk_for_extraction(chunk_id, entity_name, batch_mode)
        #_get_context_for_item(item_info)
        #_robust_json_parse(response)
    }
    
    class ImageModalProcessor {
        #_encode_image_to_base64(img_path)
        +generate_description_only()
        +process_multimodal_content()
        #_parse_response(response)
    }
    
    class TableModalProcessor {
        +generate_description_only()
        +process_multimodal_content()
        #_parse_table_response(response)
    }
    
    class EquationModalProcessor {
        +generate_description_only()
        +process_multimodal_content()
        #_parse_equation_response(response)
    }
    
    class GenericModalProcessor {
        +generate_description_only()
        +process_multimodal_content()
        #_parse_generic_response(response)
    }
    
    BaseModalProcessor <|-- ImageModalProcessor
    BaseModalProcessor <|-- TableModalProcessor
    BaseModalProcessor <|-- EquationModalProcessor
    BaseModalProcessor <|-- GenericModalProcessor
```

**Sources:** [raganything/modalprocessors.py:360-405](), [raganything/modalprocessors.py:796-812](), [raganything/modalprocessors.py:1032-1048](), [raganything/modalprocessors.py:1226-1241](), [raganything/modalprocessors.py:1410-1425]()

### BaseModalProcessor Initialization and Storage Injection

The `BaseModalProcessor` class serves as the foundation for all specialized processors. During initialization, it establishes connections to LightRAG storage systems and configures context extraction. It uses dependency injection to receive a `LightRAG` instance, from which it extracts storage backends.

```mermaid
graph TB
    Init["BaseModalProcessor.__init__()"] --> LR["lightrag: LightRAG instance"]
    Init --> MCF["modal_caption_func: LLM/VLM function"]
    Init --> CE["context_extractor: ContextExtractor"]
    
    LR --> Storage["Storage Instances"]
    Storage --> TCDB["lightrag.text_chunks"]
    Storage --> CVDB["lightrag.chunks_vdb"]
    Storage --> EVDB["lightrag.entities_vdb"]
    Storage --> RVDB["lightrag.relationships_vdb"]
    Storage --> KG["lightrag.chunk_entity_relation_graph"]
    
    LR --> Funcs["LightRAG Functions"]
    Funcs --> EMB["lightrag.embedding_func"]
    Funcs --> LLM["lightrag.llm_model_func"]
    Funcs --> HKV["lightrag.llm_response_cache"]
    
    CE --> ContextConfig["ContextConfig settings"]
    CE --> CS["content_source tracking"]
```

**Sources:** [raganything/modalprocessors.py:363-398]()

### Storage and Configuration Integration

| Component | Code Reference | Purpose |
|-----------|----------------|---------|
| `text_chunks_db` | `self.lightrag.text_chunks` | Store text chunks with metadata |
| `chunks_vdb` | `self.lightrag.chunks_vdb` | Enable chunk retrieval |
| `entities_vdb` | `self.lightrag.entities_vdb` | Enable entity search |
| `relationships_vdb` | `self.lightrag.relationships_vdb` | Enable relationship search |
| `knowledge_graph_inst` | `self.lightrag.chunk_entity_relation_graph` | Store entity-relationship graph |
| `embedding_func` | `self.lightrag.embedding_func` | Generate embeddings for indexing |
| `llm_model_func` | `self.lightrag.llm_model_func` | Primary LLM for text generation |
| `hashing_kv` | `self.lightrag.llm_response_cache` | Cache LLM responses to reduce costs |

**Sources:** [raganything/modalprocessors.py:380-398]()

## Processing Lifecycle

### Two-Phase Processing Pattern

Modal processors support two distinct processing modes to accommodate both batch and real-time workflows. This is primarily handled via `generate_description_only` and `_create_entity_and_chunk`.

```mermaid
sequenceDiagram
    participant Caller as "ProcessorMixin / BatchMixin"
    participant Processor as "Modal Processor"
    participant VLM as "Vision/Language Model"
    participant Storage as "LightRAG Storage"
    participant Extract as "Entity Extraction Pipeline"
    
    Note over Caller,Extract: Phase 1: Description Generation (Description Stage)
    Caller->>Processor: generate_description_only(modal_content, item_info)
    Processor->>Processor: _get_context_for_item(item_info)
    Processor->>VLM: modal_caption_func(prompt, context)
    VLM-->>Processor: JSON response (description + entity_info)
    Processor-->>Caller: (description, entity_info, modal_chunk)
    
    Note over Caller,Extract: Phase 2: Entity/Chunk Creation (Entity Creation Stage)
    Caller->>Processor: _create_entity_and_chunk(modal_chunk, entity_info)
    Processor->>Storage: Store chunk in text_chunks & chunks_vdb
    Processor->>Storage: Create Entity Node in KG & entities_vdb
    Processor->>Processor: _process_chunk_for_extraction(chunk_id)
    Processor->>Extract: extract_entities(chunk_text)
    Extract-->>Processor: extracted_entities & relationships
    Processor->>Storage: Create 'belongs_to' edges in KG & relationships_vdb
    Processor-->>Caller: (description, entity_data, chunk_results)
```

**Sources:** [raganything/modalprocessors.py:442-463](), [raganything/modalprocessors.py:465-545](), [raganything/modalprocessors.py:699-793]()

### Complete Processing Flow

The `process_multimodal_content()` method orchestrates both phases for immediate processing.

1.  **Context Retrieval**: Calls `_get_context_for_item` to get surrounding text [raganything/modalprocessors.py:423-440]().
2.  **Model Inference**: Calls `modal_caption_func` with a specialized prompt [raganything/modalprocessors.py:961-980]().
3.  **JSON Parsing**: Uses `_robust_json_parse` to extract `detailed_description` and `entity_info` [raganything/modalprocessors.py:547-688]().
4.  **Storage**: Invokes `_create_entity_and_chunk` to persist the data [raganything/modalprocessors.py:465-545]().
5.  **Graph Expansion**: Invokes `_process_chunk_for_extraction` to find relationships between the new modal entity and existing knowledge [raganything/modalprocessors.py:699-793]().

## Context Extraction System

### ContextExtractor Architecture

The `ContextExtractor` provides content-aware analysis by extracting surrounding text from the source document based on a `ContextConfig`.

```mermaid
graph TB
    subgraph "ContextExtractor"
        CE["ContextExtractor"]
        CE --> Config["ContextConfig"]
        CE --> Tokenizer["tokenizer (from LightRAG)"]
        
        Config --> CW["context_window: 1 (default)"]
        Config --> CM["context_mode: 'page' | 'chunk'"]
        Config --> MCT["max_context_tokens: 2000"]
        Config --> IH["include_headers: True"]
        Config --> IC["include_captions: True"]
    end
    
    subgraph "Extraction Logic"
        EC["extract_context()"] --> Format{"Format?"}
        Format -->|minerU| EML["_extract_from_content_list()"]
        Format -->|text_chunks| ETC["_extract_from_text_chunks()"]
        Format -->|text| ETS["_extract_from_text_source()"]
        
        EML --> Mode{"Mode?"}
        Mode -->|page| EPC["_extract_page_context()"]
        Mode -->|chunk| ECC["_extract_chunk_context()"]
        
        EPC --> Trunc["_truncate_context()"]
        ECC --> Trunc
    end
```

**Sources:** [raganything/modalprocessors.py:39-112](), [raganything/modalprocessors.py:120-137](), [raganything/modalprocessors.py:308-357]()

### Context Extraction Modes

| Mode | Logic | Source Dependency |
|------|-------|-------------------|
| `page` | Uses `page_idx` to find items in surrounding pages | `content_list` with `page_idx` keys [raganything/modalprocessors.py:139-177]() |
| `chunk` | Uses the `index` of items in the list to find neighbors | `content_list` with sequential indices [raganything/modalprocessors.py:179-204]() |

## Entity and Chunk Creation

### Belongs-To Relationship Schema

When a modal element (like an image) is processed, the system extracts entities from its description. It then creates a `belongs_to` relationship from those extracted entities back to the modal entity.

*   **Relationship Name**: `belongs_to` [raganything/modalprocessors.py:755]()
*   **Weight**: Defaulted to `10.0` to emphasize the link between content and its container [raganything/modalprocessors.py:758]()
*   **Keywords**: `belongs_to,part_of,contained_in` [raganything/modalprocessors.py:757]()

**Sources:** [raganything/modalprocessors.py:736-770]()

### Chunk Storage Format

Each multimodal item is stored as a chunk in `text_chunks_db` with the following metadata:
*   `content`: The generated description.
*   `file_path`: Source file.
*   `chunk_order_index`: Original position in document.
*   `full_doc_id`: Hash of the document.

**Sources:** [raganything/modalprocessors.py:475-503]()

## Robust JSON Parsing

LLMs often return JSON wrapped in markdown or with trailing commas. The `_robust_json_parse` method uses a progressive strategy to clean the response:
1.  **Candidate Extraction**: Finds all blocks between `{}` [raganything/modalprocessors.py:554-566]().
2.  **Think Tag Removal**: Strips `<think>` blocks used by reasoning models [raganything/modalprocessors.py:568-571]().
3.  **Cleanup**: Replaces smart quotes and removes trailing commas [raganything/modalprocessors.py:581-587]().
4.  **Regex Fallback**: If `json.loads` fails, it uses regex to extract specific fields like `detailed_description` and `entity_name` [raganything/modalprocessors.py:657-688]().

**Sources:** [raganything/modalprocessors.py:547-688]()

---

# Page: Image Processing

# Image Processing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/image_format_test.py](examples/image_format_test.py)
- [examples/office_document_test.py](examples/office_document_test.py)
- [examples/text_format_test.py](examples/text_format_test.py)
- [raganything/modalprocessors.py](raganything/modalprocessors.py)

</details>



## Purpose and Scope

This page documents the image processing subsystem in RAG-Anything, specifically the `ImageModalProcessor` class and its integration with vision language models (VLMs) for analyzing and indexing image content. The system converts visual information into structured knowledge graph entities through vision model analysis and context-aware processing.

The pipeline supports a wide range of image formats including JPG, PNG, BMP, TIFF, GIF, and WebP [examples/image_format_test.py:66-75](). While MinerU natively supports JPG and PNG, RAG-Anything handles conversion for other formats using Pillow [examples/image_format_test.py:93-102]().

For information about the base processor architecture and inheritance structure, see **5.1 Modal Processor Architecture**. For other content types, see **5.3 Table Processing**, **5.4 Equation Processing**, and **5.6 Context Extraction**.

## ImageModalProcessor Architecture

The `ImageModalProcessor` class inherits from `BaseModalProcessor` and specializes in handling image content by integrating vision language models for visual understanding.

**Key Responsibilities:**
- Encode images to base64 format for VLM transmission [raganything/modalprocessors.py:814-823]().
- Generate detailed visual descriptions using vision models [raganything/modalprocessors.py:907-915]().
- Extract context from surrounding document content using `ContextExtractor` [raganything/modalprocessors.py:874-899]().
- Create image entities in the knowledge graph [raganything/modalprocessors.py:965-980]().
- Establish relationships between image entities and extracted concepts [raganything/modalprocessors.py:739-770]().

### Class Hierarchy and Interactions

```mermaid
classDiagram
    class BaseModalProcessor {
        +LightRAG lightrag
        +modal_caption_func
        +ContextExtractor context_extractor
        +set_content_source()
        +_get_context_for_item()
        +_create_entity_and_chunk()
        +_process_chunk_for_extraction()
    }
    
    class ImageModalProcessor {
        +_encode_image_to_base64()
        +generate_description_only()
        +process_multimodal_content()
        +_parse_response()
    }
    
    class ContextExtractor {
        +ContextConfig config
        +extract_context()
        +_extract_from_content_list()
        +_truncate_context()
    }
    
    class LightRAG {
        +text_chunks
        +chunks_vdb
        +entities_vdb
        +knowledge_graph_inst
        +embedding_func
    }
    
    BaseModalProcessor <|-- ImageModalProcessor
    BaseModalProcessor --> ContextExtractor
    BaseModalProcessor --> LightRAG
    ImageModalProcessor --> "vision_model_func"
```

**Sources:** [raganything/modalprocessors.py:796-1030](), [raganything/modalprocessors.py:360-401]()

## Image Encoding and Vision Model Integration

### Base64 Encoding

Images must be encoded to base64 format before transmission to vision models. The `_encode_image_to_base64()` method handles this conversion by reading the file as binary and using the `base64` library [raganything/modalprocessors.py:814-823]().

### Vision Model Function

The `modal_caption_func` (typically provided as `vision_model_func`) must support image data input. The function signature expects:

```python
modal_caption_func(
    prompt: str,
    image_data: str,  # base64 encoded image
    system_prompt: str = None,
    **kwargs
) -> str
```

The vision model receives both the text prompt and the base64-encoded image for multimodal analysis [raganything/modalprocessors.py:907-911]().

**Sources:** [raganything/modalprocessors.py:814-823](), [raganything/modalprocessors.py:907-911]()

## Image Processing Workflow

### Two-Stage Processing

Image processing follows a two-stage pipeline that separates description generation from entity relationship extraction:

```mermaid
flowchart TB
    subgraph Stage1["Stage 1: Description Generation (generate_description_only)"]
        Input["Image Content<br/>{img_path, image_caption, image_footnote}"]
        Validate["Validate Image Path<br/>Path.exists()"]
        GetContext["Extract Context<br/>context_extractor.extract_context()"]
        BuildPrompt["Build Vision Prompt<br/>PROMPTS['vision_prompt']"]
        Encode["Encode Image<br/>_encode_image_to_base64()"]
        CallVLM["Call Vision Model<br/>modal_caption_func()"]
        ParseResp["Parse Response<br/>_parse_response()"]
        Output1["enhanced_caption, entity_info"]
        
        Input --> Validate
        Validate --> GetContext
        GetContext --> BuildPrompt
        BuildPrompt --> Encode
        Encode --> CallVLM
        CallVLM --> ParseResp
        ParseResp --> Output1
    end
    
    subgraph Stage2["Stage 2: Entity & Graph Creation (_create_entity_and_chunk)"]
        BuildChunk["Build Modal Chunk<br/>PROMPTS['image_chunk']"]
        CreateChunk["Create Text Chunk<br/>text_chunks.upsert()"]
        CreateEntity["Create Entity Node<br/>knowledge_graph_inst.upsert_node()"]
        VectorizeEntity["Vectorize Entity<br/>entities_vdb.upsert()"]
        ExtractRels["Extract Relationships<br/>extract_entities()"]
        BelongsTo["Create belongs_to Relations<br/>knowledge_graph_inst.upsert_edge()"]
        Output2["description, entity_info, chunk_results"]
        
        Output1 --> BuildChunk
        BuildChunk --> CreateChunk
        CreateChunk --> CreateEntity
        CreateEntity --> VectorizeEntity
        VectorizeEntity --> ExtractRels
        ExtractRels --> BelongsTo
        BelongsTo --> Output2
    end
    
    Output2 --> Done["Image Indexed in Knowledge Graph"]
```

**Sources:** [raganything/modalprocessors.py:824-928](), [raganything/modalprocessors.py:930-991](), [raganything/modalprocessors.py:465-545]()

### Processing Methods

| Method | Stage | Batch Mode | Purpose |
|--------|-------|------------|---------|
| `generate_description_only()` | 1 | Yes | Generate description without immediate graph insertion [raganything/modalprocessors.py:824-928]() |
| `process_multimodal_content()` | 1+2 | Optional | Complete processing including entity/relation extraction [raganything/modalprocessors.py:930-991]() |

## Image Content Format

### Input Structure

The image content can be provided in multiple formats, supporting both standard and legacy keys [raganything/modalprocessors.py:846-872]():

```python
# Dictionary format (standard)
{
    "img_path": "/absolute/path/to/image.jpg",  # Required
    "image_caption": ["Figure 1: Architecture"],  # Optional
    "image_footnote": ["Source: Author"]  # Optional
}

# Alternative key names (legacy support)
{
    "img_path": "/path/to/image.jpg",
    "img_caption": ["..."], 
    "img_footnote": ["..."]
}
```

**Sources:** [raganything/modalprocessors.py:846-872](), [raganything/modalprocessors.py:949-963]()

### Output Structure

The processor generates two primary outputs:
1. **Enhanced Caption**: Detailed visual description from VLM analysis [raganything/modalprocessors.py:993-1029]().
2. **Entity Info**: Dictionary containing `entity_name` (with "(image)" suffix), `entity_type`, and `summary` [raganything/modalprocessors.py:1009-1017]().

## Prompt Templates and Context-Aware Processing

### Vision Analysis Prompts

The system uses structured JSON prompts to ensure consistent VLM responses. The templates `vision_prompt` and `vision_prompt_with_context` guide the model to output JSON containing `detailed_description` and `entity_info` [raganything/prompt.py:32-89]().

### Context-Aware Analysis

When `item_info` is provided, the processor extracts surrounding content to enrich image analysis [raganything/modalprocessors.py:874-899]().

```mermaid
flowchart LR
    subgraph ContextFlow["Context Extraction Flow"]
        ItemInfo["item_info<br/>{page_idx: 5}"]
        GetContext["_get_context_for_item()"]
        Extractor["ContextExtractor.extract_context()"]
        ContentSource["content_source<br/>(document content_list)"]
        FilterText["Filter text chunks<br/>within context_window"]
        Context["Surrounding text context"]
        
        ItemInfo --> GetContext
        GetContext --> Extractor
        ContentSource --> Extractor
        Extractor --> FilterText
        FilterText --> Context
    end
    
    Context --> BuildPrompt["Build Prompt with Context"]
    BuildPrompt --> VLM["Vision Model Analysis"]
```

**Sources:** [raganything/modalprocessors.py:874-899](), [raganything/modalprocessors.py:417-440](), [raganything/modalprocessors.py:49-358]()

## Entity and Knowledge Graph Integration

### Entity Creation Process

After generating the image description, the processor creates a structured entity in the knowledge graph via `_create_entity_and_chunk` [raganything/modalprocessors.py:465-545]().

```mermaid
flowchart TB
    subgraph EntityCreation["Entity Creation (_create_entity_and_chunk)"]
        ModalChunk["Build Modal Chunk<br/>image_path + captions + description"]
        ChunkID["Generate chunk_id<br/>compute_mdhash_id()"]
        StoreChunk["Store in text_chunks_db<br/>text_chunks.upsert()"]
        VectorChunk["Vectorize Chunk<br/>chunks_vdb.upsert()"]
        
        ModalChunk --> ChunkID
        ChunkID --> StoreChunk
        StoreChunk --> VectorChunk
    end
    
    subgraph NodeCreation["Node Creation"]
        UpsertNode["Create Graph Node<br/>knowledge_graph_inst.upsert_node()"]
        EntityVDB["Vectorize Entity<br/>entities_vdb.upsert()"]
        
        VectorChunk --> UpsertNode
        UpsertNode --> EntityVDB
    end
    
    subgraph RelationExtraction["Relationship Extraction"]
        ExtractEnts["Extract Entities<br/>extract_entities()"]
        CreateBelongsTo["Create belongs_to edges<br/>for each extracted entity"]
        RelVDB["Vectorize Relations<br/>relationships_vdb.upsert()"]
        
        EntityVDB --> ExtractEnts
        ExtractEnts --> CreateBelongsTo
        CreateBelongsTo --> RelVDB
    end
```

**Sources:** [raganything/modalprocessors.py:465-545](), [raganything/modalprocessors.py:699-793]()

### Belongs-To Relationships

The processor automatically creates `belongs_to` relationships linking concepts extracted from the image description back to the image entity itself [raganything/modalprocessors.py:739-770]().

## Error Handling and Fallbacks

### Robust JSON Parsing

The `_parse_response()` method uses six distinct strategies to handle VLM response variations, including stripping thinking tags (e.g., `<think>`), extracting from code blocks, and balancing braces [raganything/modalprocessors.py:547-697]().

### Validation and Error Recovery

If the image path is invalid or the VLM call fails, the system recovers by creating a fallback entity based on the available metadata or a content hash [raganything/modalprocessors.py:918-928](), [raganything/modalprocessors.py:1019-1029]().

**Sources:** [raganything/modalprocessors.py:547-697](), [raganything/modalprocessors.py:918-928](), [raganything/modalprocessors.py:1019-1029]()

---

# Page: Table Processing

# Table Processing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [raganything/modalprocessors.py](raganything/modalprocessors.py)
- [raganything/utils.py](raganything/utils.py)

</details>



## Purpose and Scope

This document describes the table processing capabilities in RAG-Anything, specifically how the `TableModalProcessor` class analyzes tabular data, interprets structured information, and integrates tables into the knowledge graph. For general modal processor architecture, see [Modal Processor Architecture](5.1).

The `TableModalProcessor` specializes in:
- Parsing markdown-formatted tables and list-of-lists data structures.
- Extracting statistical patterns and data trends via LLM-based semantic interpretations.
- Creating table entities with "belongs_to" relationships to extracted entities.
- Context-aware table analysis using surrounding document content.
- Formatting structured data into clean Markdown for LLM consumption.

Sources: [raganything/modalprocessors.py:1032-1223](), [raganything/utils.py:36-61]()

---

## TableModalProcessor Class Overview

The `TableModalProcessor` extends `BaseModalProcessor` to provide specialized handling for tabular content. Unlike image processing which requires vision models, table processing uses standard LLM capabilities to analyze structured data patterns.

### Class Structure and Dependency Flow

The following diagram bridges the Natural Language concepts of "Table Processing" with the specific code entities involved.

```mermaid
graph TD
    subgraph "Natural Language Space"
        Table[Table Content]
        Analysis[Semantic Analysis]
        Storage[Graph Storage]
    end

    subgraph "Code Entity Space"
        TMP["TableModalProcessor (raganything/modalprocessors.py)"]
        BMP["BaseModalProcessor (raganything/modalprocessors.py)"]
        CE["ContextExtractor (raganything/modalprocessors.py)"]
        FTB["format_table_body (raganything/utils.py)"]
        LR["LightRAG (lightrag/lightrag.py)"]
    end

    Table --> TMP
    TMP -- "inherits" --> BMP
    TMP -- "uses" --> FTB
    TMP -- "extracts context via" --> CE
    Analysis -- "generated by" --> TMP
    Storage -- "managed by" --> LR
    TMP -- "stores results in" --> LR
```

Sources: [raganything/modalprocessors.py:1032-1033](), [raganything/modalprocessors.py:360-401](), [raganything/utils.py:36-61]()

---

## Table Content Structure and Utilities

### Input Format and Normalization

Tables processed by `TableModalProcessor` are expected in a dictionary format. RAG-Anything provides utility functions in `raganything/utils.py` to handle variations in parser outputs.

| Field | Source Utility | Description |
|-------|----------------|-------------|
| `table_body` | `get_table_body` | Reads content from `table_body`, `table_data`, or `text` fields. [raganything/utils.py:27-34]() |
| `table_caption` | `normalize_caption_list` | Normalizes strings or lists into a clean list of strings. [raganything/utils.py:16-24]() |
| `table_body` (rendered) | `format_table_body` | Converts strings or list-of-lists into Markdown tables. [raganything/utils.py:36-61]() |

### Markdown Rendering Implementation

The `format_table_body` function ensures the LLM sees structured rows instead of a Python representation:

1. **Strings**: Passed through unchanged. [raganything/utils.py:44-45]()
2. **List-of-Lists**: Rendered as a Markdown table with `|` separators and a `| --- |` header separator. [raganything/utils.py:49-58]()
3. **Other Lists**: Joined by newlines. [raganything/utils.py:59]()

Sources: [raganything/utils.py:16-61](), [raganything/modalprocessors.py:1056-1068]()

---

## Table Processing Workflow

The table processing workflow consists of two main stages: description generation and entity creation.

```mermaid
flowchart TB
    START["Table Content Dictionary"]
    
    UTILS["Normalize Content<br/>get_table_body()<br/>format_table_body()"]
    
    CONTEXT["Extract Context<br/>ContextExtractor.extract_context()"]
    
    LLM_CALL["LLM Analysis<br/>modal_caption_func()"]
    
    PARSE_RESPONSE["Parse JSON Response<br/>_parse_table_response()"]
    
    CREATE_ENTITY["Create Entity & Chunk<br/>_create_entity_and_chunk()"]
    
    BELONGS_TO["Add belongs_to Relationships<br/>to extracted entities"]
    
    STORE["Store in LightRAG<br/>knowledge_graph_inst<br/>entities_vdb"]
    
    START --> UTILS
    UTILS --> CONTEXT
    CONTEXT --> LLM_CALL
    LLM_CALL --> PARSE_RESPONSE
    PARSE_RESPONSE --> CREATE_ENTITY
    CREATE_ENTITY --> BELONGS_TO
    BELONGS_TO --> STORE
```

Sources: [raganything/modalprocessors.py:1125-1186](), [raganything/modalprocessors.py:699-793](), [raganything/utils.py:36-61]()

---

## Context-Aware Analysis

Tables are analyzed with awareness of surrounding document content. The `ContextExtractor` retrieves text from nearby pages or chunks using the `ContextConfig`.

### Prompt Selection Logic

The processor selects between two prompt templates based on context availability:
- **`table_prompt_with_context`**: Used if `context_extractor` is present and returns content. [raganything/modalprocessors.py:1085-1098]()
- **`table_prompt`**: Standard analysis without surrounding text. [raganything/modalprocessors.py:1076-1083]()

The `ContextExtractor` can operate in `page` mode (surrounding pages) or `chunk` mode (surrounding content blocks). [raganything/modalprocessors.py:132-137]()

Sources: [raganything/modalprocessors.py:40-54](), [raganything/modalprocessors.py:1070-1098](), [raganything/prompt.py:101-160]()

---

## Response Parsing and Robustness

### _parse_table_response()

The `_parse_table_response` method uses the `_robust_json_parse` logic from the base class to handle LLM hallucinations or formatting errors.

**Analysis Components Requested:**
- **detailed_description**: Comprehensive analysis of structure, trends, and significance. [raganything/prompt.py:101-160]()
- **entity_info**: A structured object containing `entity_name`, `entity_type` (fixed as "table"), and a concise `summary`. [raganything/modalprocessors.py:1191-1211]()

**Error Handling Strategy:**
If JSON parsing fails after multiple cleaning attempts (fixing quotes, trailing commas, etc.), the processor falls back to a generated entity name based on the MD5 hash of the response. [raganything/modalprocessors.py:1213-1223]()

Sources: [raganything/modalprocessors.py:1187-1223](), [raganything/modalprocessors.py:547-698]()

---

## Knowledge Graph Integration

### Entity and Relationship Creation

After the LLM generates the `detailed_description`, the processor integrates the data into the LightRAG knowledge graph:

1. **Chunk Creation**: A specialized `table_chunk` is created containing the raw Markdown table, captions, footnotes, and the LLM analysis. [raganything/modalprocessors.py:1158-1164]()
2. **Entity Extraction**: The `extract_entities` function is called on the generated description to identify domain-specific entities mentioned within the table analysis. [raganything/modalprocessors.py:736-745]()
3. **Belongs_to Relationships**: For every entity extracted from the table's description, a `belongs_to` relationship is created linking it to the primary Table Entity. [raganything/modalprocessors.py:747-770]()

### Relationship Schema
The `belongs_to` edge uses a high weight (10.0) to signify a strong structural containment relationship. [raganything/modalprocessors.py:756]()

Sources: [raganything/modalprocessors.py:736-770](), [raganything/modalprocessors.py:1166-1173](), [raganything/prompt.py:283-289]()

---

## Batch Processing and Performance

### Stage Flow for Tables

In the `ProcessorMixin` pipeline, tables are handled via `_process_multimodal_content_batch_type_aware`.

- **Stage 4**: Parallel execution of `generate_description_only` for all tables in the document. [raganything/processor.py:646-654]()
- **Stage 5**: Creation of entities and chunks. If `batch_mode=True`, the storage flush and graph merging are deferred to optimize performance. [raganything/modalprocessors.py:773-792]()

### Caching
The system uses `hashing_kv` to cache LLM responses for table analysis. If the same table (based on content hash) is processed again with the same prompt, the cached description is reused. [raganything/modalprocessors.py:389-391]()

Sources: [raganything/modalprocessors.py:773-792](), [raganything/processor.py:646-654]()

---

# Page: Equation Processing

# Equation Processing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [raganything/modalprocessors.py](raganything/modalprocessors.py)
- [raganything/omml_extractor.py](raganything/omml_extractor.py)
- [raganything/utils.py](raganything/utils.py)
- [tests/test_doc_status_creation.py](tests/test_doc_status_creation.py)
- [tests/test_omml_extractor.py](tests/test_omml_extractor.py)

</details>



This page documents the `EquationModalProcessor` implementation, which handles LaTeX mathematical formulas extracted from documents. The processor performs semantic analysis of equations, extracts mathematical meaning, and integrates them into the knowledge graph with proper entity relationships. It also details the specialized OMML-to-LaTeX conversion utility used for DOCX files.

For handling other multimodal content types, see [Image Processing](#5.2) and [Table Processing](#5.3). For the base processor architecture, see [Modal Processor Architecture](#5.1).

---

## Overview

The `EquationModalProcessor` class specializes in processing mathematical equations and formulas. Unlike image and table processors that rely on visual analysis, equation processing focuses on mathematical interpretation and semantic understanding of LaTeX expressions.

**Key capabilities:**
- Parsing LaTeX formula syntax from document content [raganything/modalprocessors.py:1250-1261]()
- LLM-based semantic analysis of mathematical expressions [raganything/modalprocessors.py:1268-1286]()
- Variable definition and operation identification [raganything/prompt.py:163-188]()
- Context-aware interpretation of equations [raganything/modalprocessors.py:1263-1265]()
- Integration with knowledge graph as specialized entities [raganything/modalprocessors.py:1389-1393]()
- Robust error handling for malformed LaTeX [raganything/modalprocessors.py:547-688]()
- OMML-to-LaTeX conversion for DOCX math preservation [raganything/omml_extractor.py:10-28]()

**Sources:** [raganything/modalprocessors.py:8-10](), [raganything/modalprocessors.py:1226-1408](), [raganything/omml_extractor.py:1-38]()

---

## Equation Processor Class Hierarchy

```mermaid
classDiagram
    class BaseModalProcessor {
        +LightRAG lightrag
        +modal_caption_func
        +ContextExtractor context_extractor
        +set_content_source()
        +_get_context_for_item()
        +_create_entity_and_chunk()
        +_robust_json_parse()
    }
    
    class EquationModalProcessor {
        +generate_description_only()
        +process_multimodal_content()
        +_parse_equation_response()
    }
    
    class LightRAG {
        +text_chunks
        +chunks_vdb
        +entities_vdb
        +chunk_entity_relation_graph
        +llm_model_func
        +embedding_func
    }
    
    class ContextExtractor {
        +ContextConfig config
        +extract_context()
        +_extract_page_context()
        +_truncate_context()
    }
    
    BaseModalProcessor --> LightRAG : "uses storage"
    BaseModalProcessor --> ContextExtractor : "extracts context"
    EquationModalProcessor --|> BaseModalProcessor : "extends"
```

**Diagram: EquationModalProcessor Class Structure**

The `EquationModalProcessor` inherits storage access and context extraction capabilities from `BaseModalProcessor`, while implementing equation-specific processing logic.

**Sources:** [raganything/modalprocessors.py:360-401](), [raganything/modalprocessors.py:1226-1228]()

---

## Equation Content Format and Extraction

Equations follow a standard format. The utility `get_equation_text_and_format` handles various alias fields (e.g., `text`, `latex`, `equation`) to ensure compatibility across different parsers.

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Always `"equation"` for equation content |
| `text` | string | LaTeX formula string (highest priority) [raganything/utils.py:72-78]() |
| `latex` | string | Alias for LaTeX content [raganything/utils.py:73-82]() |
| `equation` | string | Fallback alias [raganything/utils.py:74-84]() |
| `text_format` | string | Format identifier (defaults to `"latex"`) [raganything/utils.py:75-82]() |

### OMML-to-LaTeX (DOCX Support)
For DOCX files, equations are stored as Office Math Markup Language (OMML). The `omml_extractor` module converts these to LaTeX to prevent loss during PDF conversion.

**Key Conversion Rules:**
- **Fractions:** `<m:f>` becomes `\frac{num}{den}` [raganything/omml_extractor.py:284-290]().
- **Scripts:** `<m:sSup>` (superscript) and `<m:sSub>` (subscript) [raganything/omml_extractor.py:292-316]().
- **N-ary Operators:** Summation (`\sum`), Integrals (`\int`), etc., are mapped from Unicode codepoints [raganything/omml_extractor.py:62-79]().
- **Matrices:** `<m:m>` converted to `\begin{matrix} ... \end{matrix}` [raganything/omml_extractor.py:392-411]().

**Sources:** [raganything/utils.py:63-89](), [raganything/omml_extractor.py:40-105](), [raganything/omml_extractor.py:270-430]()

---

## Equation Processing Pipeline

```mermaid
flowchart TB
    INPUT["Equation Content<br/>{type, text, text_format, page_idx}"]
    
    PARSE["Parse Content<br/>get_equation_text_and_format()"]
    EXTRACT_TEXT["Extract LaTeX String"]
    EXTRACT_FORMAT["Extract Format"]
    
    CONTEXT_CHECK{"Context<br/>Available?"}
    GET_CONTEXT["Get Context<br/>_get_context_for_item()"]
    
    BUILD_PROMPT_CTX["Build Prompt with Context<br/>equation_prompt_with_context"]
    BUILD_PROMPT["Build Prompt<br/>equation_prompt"]
    
    LLM_CALL["Call LLM<br/>modal_caption_func()"]
    
    PARSE_RESPONSE["Parse Response<br/>_parse_equation_response()"]
    ROBUST_JSON["Robust JSON Parsing<br/>_robust_json_parse()"]
    EXTRACT_FIELDS["Extract Fields<br/>detailed_description<br/>entity_info"]
    
    CREATE_CHUNK["Build Equation Chunk<br/>equation_chunk template"]
    
    CREATE_ENTITY["Create Entity & Chunk<br/>_create_entity_and_chunk()"]
    
    STORE_CHUNK["Store in text_chunks_db<br/>chunks_vdb"]
    CREATE_NODE["Create Knowledge Graph Node<br/>chunk_entity_relation_graph"]
    STORE_ENTITY["Store in entities_vdb"]
    EXTRACT_RELATIONS["Extract Relations<br/>_process_chunk_for_extraction()"]
    
    OUTPUT["Returns:<br/>(description, entity_info, chunk_results)"]
    
    ERROR{"Error?"}
    FALLBACK["Fallback Entity<br/>equation_[hash]"]
    
    INPUT --> PARSE
    PARSE --> EXTRACT_TEXT
    PARSE --> EXTRACT_FORMAT
    
    EXTRACT_TEXT --> CONTEXT_CHECK
    EXTRACT_FORMAT --> CONTEXT_CHECK
    
    CONTEXT_CHECK -->|Yes| GET_CONTEXT
    CONTEXT_CHECK -->|No| BUILD_PROMPT
    GET_CONTEXT --> BUILD_PROMPT_CTX
    
    BUILD_PROMPT_CTX --> LLM_CALL
    BUILD_PROMPT --> LLM_CALL
    
    LLM_CALL --> PARSE_RESPONSE
    PARSE_RESPONSE --> ROBUST_JSON
    ROBUST_JSON --> EXTRACT_FIELDS
    
    EXTRACT_FIELDS --> ERROR
    ERROR -->|No| CREATE_CHUNK
    ERROR -->|Yes| FALLBACK
    
    CREATE_CHUNK --> CREATE_ENTITY
    FALLBACK --> CREATE_ENTITY
    
    CREATE_ENTITY --> STORE_CHUNK
    STORE_CHUNK --> CREATE_NODE
    CREATE_NODE --> STORE_ENTITY
    STORE_ENTITY --> EXTRACT_RELATIONS
    
    EXTRACT_RELATIONS --> OUTPUT
```

**Diagram: Complete Equation Processing Flow**

The pipeline uses `get_equation_text_and_format` [raganything/utils.py:63]() to normalize input before calling the LLM via `modal_caption_func` [raganything/modalprocessors.py:1290]().

**Sources:** [raganything/modalprocessors.py:1313-1369](), [raganything/modalprocessors.py:1229-1311](), [raganything/utils.py:63-89]()

---

## LLM-Based Semantic Analysis

### Prompt Construction

The processor uses specialized prompts to extract mathematical meaning from LaTeX formulas:

**Without Context:**
```python
# Template from PROMPTS["equation_prompt"]
"""Please analyze this mathematical equation and provide a JSON response...

Equation Information:
Equation: {equation_text}
Format: {equation_format}
"""
```

**With Context:**
```python
# Template from PROMPTS["equation_prompt_with_context"]
"""Please analyze this mathematical equation considering the surrounding context...

Context from surrounding content:
{context}

Equation Information:
Equation: {equation_text}
Format: {equation_format}
"""
```

**Sources:** [raganything/prompt.py:162-220](), [raganything/modalprocessors.py:1268-1286]()

---

## Robust JSON Parsing

Mathematical LaTeX contains many special characters (backslashes, braces) that frequently break standard JSON parsing. The processor uses a multi-strategy approach:

1. **Direct Parsing:** Attempts standard `json.loads()`.
2. **Candidate Extraction:** Uses `_extract_all_json_candidates()` to find JSON blocks within model output, stripping thinking tags [raganything/modalprocessors.py:573-616]().
3. **LaTeX Quote Fixing:** Specifically escapes backslashes in LaTeX strings (e.g., `\alpha` becomes `\\alpha`) to prevent JSON errors [raganything/modalprocessors.py:642-655]().
4. **Regex Fallback:** As a last resort, `_extract_fields_with_regex` pulls fields directly using patterns [raganything/modalprocessors.py:657-688]().

**Sources:** [raganything/modalprocessors.py:547-688]()

---

## Entity Creation and Knowledge Graph Integration

### Chunk Creation
The processor builds a formatted text chunk using the `equation_chunk` template [raganything/prompt.py:291-295]():

```python
modal_chunk = PROMPTS["equation_chunk"].format(
    equation_text=equation_text,
    equation_format=equation_format,
    enhanced_caption=enhanced_caption,
)
```

### Storage Operations
The chunk is stored in `chunks_vdb` and the equation is added as a node to the `chunk_entity_relation_graph` [raganything/modalprocessors.py:720-745](). Relationships are then extracted from the enhanced description to link the equation to other concepts in the document [raganything/modalprocessors.py:756-771]().

**Sources:** [raganything/modalprocessors.py:465-545](), [raganything/modalprocessors.py:699-793]()

---

## Two-Phase Processing

### Phase 1: Description Generation
The `generate_description_only()` method performs analysis without entity extraction [raganything/modalprocessors.py:1229-1311](). This is used in batch processing stage 1.

### Phase 2: Complete Processing
The `process_multimodal_content()` method performs full processing, including KG integration and storage [raganything/modalprocessors.py:1313-1369]().

---

## Limitations

1. **OCR Dependency:** Equations in image form must be converted to LaTeX by the parser (e.g., MinerU) before this processor can handle them.
2. **Complex Notation:** Highly specialized mathematical notation may be misinterpreted if the LLM lacks specific domain training.
3. **JSON Sensitivity:** Despite robust parsing, extremely long or nested LaTeX strings can still cause parsing timeouts or failures.

**Sources:** [raganything/modalprocessors.py:1226-1408](), [raganything/omml_extractor.py:24-28]()

---

# Page: Custom Modal Processors

# Custom Modal Processors

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/context_aware_processing.md](docs/context_aware_processing.md)
- [examples/insert_content_list_example.py](examples/insert_content_list_example.py)
- [examples/modalprocessors_example.py](examples/modalprocessors_example.py)
- [raganything/batch_parser.py](raganything/batch_parser.py)
- [raganything/modalprocessors.py](raganything/modalprocessors.py)
- [tests/test_custom_parser.py](tests/test_custom_parser.py)
- [tests/test_embedding_examples.py](tests/test_embedding_examples.py)

</details>



This page provides a comprehensive guide to creating custom modal processors for handling domain-specific or specialized content types beyond the built-in image, table, and equation processors. Custom modal processors enable RAG-Anything to extend its multimodal capabilities to any content type while maintaining consistency with the knowledge graph integration.

For information about the base modal processor architecture and lifecycle, see [Modal Processor Architecture](#5.1). For specific implementations of built-in processors, see [Image Processing](#5.2), [Table Processing](#5.3), and [Equation Processing](#5.4).

---

## Overview

The `GenericModalProcessor` class serves as both a functional processor for generic content types and an extensible base class for creating custom processors. It implements the full modal processor lifecycle while providing customization points for domain-specific analysis logic.

**Key Capabilities:**
- Process arbitrary content types with custom analysis logic.
- Integrate with context extraction for content-aware processing.
- Generate structured entities for knowledge graph integration.
- Support both batch and immediate processing modes.
- Leverage custom LLM prompts for specialized analysis.

Sources: [raganything/modalprocessors.py:9-10](), [raganything/modalprocessors.py:1410-1569]()

---

## GenericModalProcessor Architecture

### System to Code Entity Mapping

The following diagram bridges the conceptual modal processing space with the specific code entities defined in the `raganything/modalprocessors.py` file.

```mermaid
graph TB
    subgraph "BaseModalProcessor (System Foundation)"
        BASE["BaseModalProcessor<br/>(Abstract Base)"]
        BASE_INIT["__init__()<br/>raganything/modalprocessors.py:360-404"]
        BASE_CONTEXT["_get_context_for_item()<br/>raganything/modalprocessors.py:417-440"]
        BASE_ENTITY["_create_entity_and_chunk()<br/>raganything/modalprocessors.py:699-793"]
        BASE_EXTRACT["_process_chunk_for_extraction()<br/>raganything/modalprocessors.py:795-870"]
        BASE_JSON["_robust_json_parse()<br/>raganything/modalprocessors.py:547-698"]
    end
    
    subgraph "GenericModalProcessor (Implementation Base)"
        GENERIC["GenericModalProcessor<br/>raganything/modalprocessors.py:1410-1569"]
        GEN_DESC["generate_description_only()<br/>raganything/modalprocessors.py:1413-1485"]
        GEN_PROCESS["process_multimodal_content()<br/>raganything/modalprocessors.py:1487-1531"]
        GEN_PARSE["_parse_generic_response()<br/>raganything/modalprocessors.py:1533-1569"]
    end
    
    subgraph "Custom Processor Pattern"
        CUSTOM["CustomModalProcessor<br/>(User-defined subclass)"]
        CUSTOM_DESC["generate_description_only()<br/>(Override)"]
        CUSTOM_PROCESS["process_multimodal_content()<br/>(Optional override)"]
    end
    
    BASE --> GENERIC
    GENERIC --> CUSTOM
    
    BASE_INIT --> BASE_CONTEXT
    BASE_CONTEXT --> BASE_ENTITY
    BASE_ENTITY --> BASE_EXTRACT
    BASE_EXTRACT --> BASE_JSON
    
    GEN_DESC --> BASE_CONTEXT
    GEN_DESC --> GEN_PARSE
    GEN_PROCESS --> GEN_DESC
    GEN_PROCESS --> BASE_ENTITY
```

**Inheritance Hierarchy**

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| `BaseModalProcessor` | Abstract base with shared infrastructure | `_create_entity_and_chunk()`, `_get_context_for_item()`, `_robust_json_parse()` |
| `GenericModalProcessor` | Default implementation for any content type | `generate_description_only()`, `process_multimodal_content()` |
| Custom Processors | Domain-specific extensions | Override `generate_description_only()`, optionally override `process_multimodal_content()` |

Sources: [raganything/modalprocessors.py:360-404](), [raganything/modalprocessors.py:1410-1569]()

---

## Extension Points

### Required Method: generate_description_only

This method generates a text description and entity metadata for the content without performing entity/relationship extraction. It is used during batch processing stage 1 and forms the foundation of all modal processing.

**Method Signature:**
```python
async def generate_description_only(
    self,
    modal_content: Any,           # Content to process
    content_type: str,            # Type identifier (e.g., "code", "chart")
    item_info: Dict[str, Any] = None,  # For context extraction (page_idx, index)
    entity_name: str = None       # Optional predefined entity name
) -> Tuple[str, Dict[str, Any]]  # Returns (description, entity_info)
```

**Return Format:**
```python
# entity_info structure
{
    "entity_name": "unique_entity_identifier",
    "entity_type": "content_type",
    "summary": "concise summary (max 100 words)"
}
```

Sources: [raganything/modalprocessors.py:442-463](), [raganything/modalprocessors.py:1413-1485]()

### Optional Method: process_multimodal_content

This method performs full processing including entity creation, chunk storage, and knowledge graph integration. Most custom processors can rely on the base implementation, only overriding `generate_description_only()`.

**Method Signature:**
```python
async def process_multimodal_content(
    self,
    modal_content: Any,
    content_type: str,
    file_path: str = "manual_creation",
    entity_name: str = None,
    item_info: Dict[str, Any] = None,
    batch_mode: bool = False,
    doc_id: str = None,
    chunk_order_index: int = 0
) -> Tuple[str, Dict[str, Any], List]
```

Sources: [raganything/modalprocessors.py:1487-1531]()

---

## Processing Flow Diagram

### Data Flow and Pipeline Integration

This sequence diagram illustrates how a custom processor interacts with the `ContextExtractor` and the underlying `LightRAG` storage systems.

```mermaid
sequenceDiagram
    participant User
    participant Custom as CustomModalProcessor
    participant Base as BaseModalProcessor
    participant Context as ContextExtractor (raganything/modalprocessors.py:55-358)
    participant LLM as modal_caption_func
    participant KG as LightRAG Storage (lightrag/lightrag.py)
    
    User->>Custom: process_multimodal_content(modal_content)
    Custom->>Custom: generate_description_only()
    
    alt Context Enabled
        Custom->>Base: _get_context_for_item(item_info)
        Base->>Context: extract_context(content_source)
        Context-->>Base: context text
        Base-->>Custom: context
    end
    
    Custom->>Custom: Build custom prompt with context
    Custom->>LLM: modal_caption_func(prompt)
    LLM-->>Custom: JSON response
    Custom->>Base: _robust_json_parse(response)
    Base-->>Custom: parsed entity_info
    Custom-->>Custom: (description, entity_info)
    
    Custom->>Custom: Build modal_chunk
    Custom->>Base: _create_entity_and_chunk(modal_chunk, entity_info)
    
    Base->>KG: Store chunk in text_chunks_db
    Base->>KG: Create entity node in knowledge_graph_inst
    Base->>Base: _process_chunk_for_extraction(chunk_id)
    Base->>KG: Extract entities & relationships
    
    Base-->>Custom: (description, entity_info, chunk_results)
    Custom-->>User: Processing complete
```

Sources: [raganything/modalprocessors.py:1487-1531](), [raganything/modalprocessors.py:465-545](), [raganything/modalprocessors.py:699-793]()

---

## Context Integration

Custom processors can leverage the `ContextExtractor` to obtain surrounding content for context-aware analysis. The context extractor supports multiple content formats and extraction modes.

### Using Context in Custom Processors

```python
# Context is automatically available via _get_context_for_item()
context = self._get_context_for_item(item_info)

if context:
    # Use context-aware prompt
    prompt = PROMPTS["custom_prompt_with_context"].format(
        context=context,
        content=modal_content,
        entity_name=entity_name
    )
```

**Context Configuration:**

The `ContextExtractor` is initialized with a `ContextConfig` object that controls extraction behavior:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `context_window` | 1 | Number of pages/chunks before and after |
| `context_mode` | "page" | Extraction mode: "page", "chunk", or "token" |
| `max_context_tokens` | 2000 | Maximum context length |
| `include_headers` | True | Include document section headers |
| `include_captions` | True | Include image/table captions |
| `filter_content_types` | ["text"] | Content types to include in context |

Sources: [raganything/modalprocessors.py:417-440](), [raganything/modalprocessors.py:33-47](), [raganything/modalprocessors.py:49-358](), [docs/context_aware_processing.md:43-54]()

---

## Complete Implementation Example

### Code Snippet Processor Example

This example demonstrates a complete custom processor for analyzing code snippets, extending `GenericModalProcessor`.

```python
from raganything.modalprocessors import GenericModalProcessor
from raganything.prompt import PROMPTS
from typing import Dict, Any, Tuple
from lightrag.utils import logger

class CodeSnippetProcessor(GenericModalProcessor):
    """Processor for analyzing code snippets with language-specific insights"""
    
    async def generate_description_only(
        self,
        modal_content: Any,
        content_type: str,
        item_info: Dict[str, Any] = None,
        entity_name: str = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate code analysis description"""
        try:
            # Parse content
            code_content = modal_content.get("code", "") if isinstance(modal_content, dict) else str(modal_content)
            
            # Extract context
            context = self._get_context_for_item(item_info) if item_info else ""
            
            # Build prompt using existing template logic
            prompt_key = "generic_prompt_with_context" if context else "generic_prompt"
            prompt = PROMPTS[prompt_key].format(
                context=context,
                entity_name=entity_name or "code_snippet",
                content=code_content,
                content_type="code_snippet"
            )
            
            # Call LLM
            response = await self.modal_caption_func(prompt)
            
            # Parse response using base utility
            description, entity_info = self._parse_generic_response(
                response, entity_name, "code_snippet"
            )
            
            return description, entity_info
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return str(modal_content), {"entity_name": entity_name, "entity_type": "code_snippet"}
```

Sources: [raganything/modalprocessors.py:1410-1569](), [examples/modalprocessors_example.py:144-165]()

---

## Best Practices

### 1. Robust JSON Parsing
Always use the inherited `_robust_json_parse()` method [raganything/modalprocessors.py:547-698](). It implements multiple fallback strategies including code block extraction and balanced brace matching to handle LLM outputs that aren't perfectly formatted JSON.

### 2. Batch Mode Support
Custom processors should respect the `batch_mode` flag [raganything/modalprocessors.py:1487-1531](). When `batch_mode` is True, `_create_entity_and_chunk` avoids immediate indexing to improve performance during large document ingestions.

### 3. Error Fallbacks
Implement meaningful fallbacks in `generate_description_only` [raganything/modalprocessors.py:1413-1485](). If the LLM fails or the response is unparseable, return a basic summary of the raw content to prevent the entire pipeline from failing.

Sources: [raganything/modalprocessors.py:547-698](), [raganything/modalprocessors.py:1413-1531]()

---

# Page: Context Extraction

# Context Extraction

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/context_aware_processing.md](docs/context_aware_processing.md)
- [examples/insert_content_list_example.py](examples/insert_content_list_example.py)
- [examples/modalprocessors_example.py](examples/modalprocessors_example.py)
- [raganything/config.py](raganything/config.py)
- [raganything/modalprocessors.py](raganything/modalprocessors.py)
- [tests/test_embedding_examples.py](tests/test_embedding_examples.py)

</details>



## Purpose and Scope

Context extraction is a critical component of RAG-Anything's multimodal processing pipeline that enriches modal content (images, tables, equations) with surrounding textual information. This system enables modal processors to generate more accurate and contextually-aware descriptions by providing LLMs and VLMs with relevant surrounding content from the document.

This page covers the `ContextExtractor` class, `ContextConfig` dataclass, and their integration with modal processors.

**Sources:** [raganything/modalprocessors.py:1-48]()

---

## System Overview

The context extraction system extracts text content surrounding multimodal items to provide additional context when generating descriptions. This context-aware approach significantly improves the quality of generated descriptions and entity relationships.

### Context Extraction in the Processing Pipeline

```mermaid
graph TB
    subgraph "Document Processing"
        Parser["Parser<br/>(MinerU/Docling/PaddleOCR)"]
        ContentList["content_list<br/>(List of content items)"]
    end
    
    subgraph "Context Extraction System"
        ContextConfig["ContextConfig<br/>dataclass"]
        ContextExtractor["ContextExtractor<br/>class"]
        
        ContextConfig -->|"configures"| ContextExtractor
    end
    
    subgraph "Modal Processing"
        BaseModalProcessor["BaseModalProcessor<br/>._get_context_for_item()"]
        ImageProc["ImageModalProcessor<br/>.generate_description_only()"]
        TableProc["TableModalProcessor<br/>.generate_description_only()"]
        EquationProc["EquationModalProcessor<br/>.generate_description_only()"]
    end
    
    subgraph "Context Extraction Flow"
        SetSource["BaseModalProcessor<br/>.set_content_source()"]
        ExtractContext["ContextExtractor<br/>.extract_context()"]
        
        ModeRouter{"context_mode?"}
        PageMode["_extract_page_context()"]
        ChunkMode["_extract_chunk_context()"]
        TokenMode["_truncate_context()"]
    end
    
    subgraph "LLM/VLM Processing"
        PromptBuild["Build prompt with context"]
        LLMCall["modal_caption_func()"]
    end
    
    Parser --> ContentList
    ContentList --> SetSource
    
    ContextConfig --> BaseModalProcessor
    ContextExtractor --> BaseModalProcessor
    
    SetSource --> BaseModalProcessor
    BaseModalProcessor --> ImageProc
    BaseModalProcessor --> TableProc
    BaseModalProcessor --> EquationProc
    
    ImageProc --> ExtractContext
    TableProc --> ExtractContext
    EquationProc --> ExtractContext
    
    ExtractContext --> ModeRouter
    ModeRouter -->|"page"| PageMode
    ModeRouter -->|"chunk"| ChunkMode
    ModeRouter -->|"token limit"| TokenMode
    
    PageMode --> PromptBuild
    ChunkMode --> PromptBuild
    TokenMode --> PromptBuild
    
    PromptBuild --> LLMCall
    
    style ContextExtractor fill:#f9f9f9,stroke:#333,stroke-width:2px
    style BaseModalProcessor fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Sources:** [raganything/modalprocessors.py:49-441](), [docs/context_aware_processing.md:174-189]()

---

## ContextConfig Dataclass

The `ContextConfig` dataclass provides configuration options for context extraction behavior. These settings can be initialized via `RAGAnythingConfig` or passed directly to the extractor.

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `context_window` | `int` | `1` | Number of pages/chunks to include on each side of the target item. |
| `context_mode` | `str` | `"page"` | Extraction mode: `"page"`, `"chunk"`, or `"token"`. |
| `max_context_tokens` | `int` | `2000` | Maximum number of tokens in extracted context. |
| `include_headers` | `bool` | `True` | Whether to include document headers/titles in context. |
| `include_captions` | `bool` | `True` | Whether to include image/table captions in context. |
| `filter_content_types` | `List[str]` | `["text"]` | Content types to include in context extraction. |

**Sources:** [raganything/modalprocessors.py:39-54](), [raganything/config.py:78-107]()

---

## ContextExtractor Class

The `ContextExtractor` class implements context extraction logic with support for multiple content source formats and extraction modes.

### Initialization

The `ContextExtractor` is initialized with a configuration and optional tokenizer:

```python
def __init__(self, config: ContextConfig = None, tokenizer=None):
    """Initialize context extractor
    
    Args:
        config: Context extraction configuration
        tokenizer: Tokenizer for accurate token counting
    """
    self.config = config or ContextConfig()
    self.tokenizer = tokenizer
```

**Sources:** [raganything/modalprocessors.py:58-66]()

### Main Entry Point: `extract_context`

The `extract_context` method serves as a universal interface, automatically detecting the format of the `content_source`.

| Format Hint | Input Type | Internal Method |
|-------------|------------|-----------------|
| `minerU` | `List[Dict]` | `_extract_from_content_list` |
| `text_chunks`| `List[str]` | `_extract_from_text_chunks` |
| `text` | `str` | `_extract_from_text_source` |
| `auto` | Any | Dynamic Detection |

**Sources:** [raganything/modalprocessors.py:68-118]()

---

## Context Extraction Modes

### Page Mode (`context_mode="page"`)

Page mode extracts context based on page boundaries. It uses the `page_idx` field found in MinerU-style content lists.

**Implementation Logic:**
1. Identifies the `current_page` from `current_item_info`. [raganything/modalprocessors.py:151]()
2. Calculates `start_page` and `end_page` using `context_window`. [raganything/modalprocessors.py:154-155]()
3. Iterates through the list, collecting items where `item_type` is in `filter_content_types`. [raganything/modalprocessors.py:163-167]()
4. Prepends `[Page X]` markers to content from pages other than the current one. [raganything/modalprocessors.py:170-172]()

**Sources:** [raganything/modalprocessors.py:139-177]()

### Chunk Mode (`context_mode="chunk"`)

Chunk mode extracts context based on sequential item indices, suitable for pre-chunked data or non-paginated documents.

**Implementation Logic:**
1. Identifies the `current_index` from `current_item_info`. [raganything/modalprocessors.py:191]()
2. Calculates index range `[current_index - window, current_index + window]`. [raganything/modalprocessors.py:194-195]()
3. Collects text from surrounding items, excluding the target item itself. [raganything/modalprocessors.py:198-204]()

**Sources:** [raganything/modalprocessors.py:179-204]()

---

## Text Extraction and Truncation

### `_extract_text_from_item`

This internal method converts various content types into text strings for the context block:
- **Text**: Returns the text. If `include_headers` is True and `text_level > 0`, it adds Markdown header symbols (`#`). [raganything/modalprocessors.py:214-220]()
- **Image**: Returns the caption in brackets `[Image: caption]` if `include_captions` is True. [raganything/modalprocessors.py:222-226]()
- **Table**: Returns the caption in brackets `[Table: caption]` if `include_captions` is True. [raganything/modalprocessors.py:228-232]()

**Sources:** [raganything/modalprocessors.py:206-236]()

### `_truncate_context`

To prevent exceeding LLM context limits, the extractor truncates the final string:
1. **Token-based**: If a tokenizer is provided, it encodes the string and truncates to `max_context_tokens`. [raganything/modalprocessors.py:315-322]()
2. **Smart Boundary Preservation**: It attempts to truncate at the last period (`.`) or newline (`\n`) if they appear within the last 20% of the truncated text to avoid cutting off mid-sentence. [raganything/modalprocessors.py:325-333]()
3. **Character-based**: Fallback to character slicing if no tokenizer is available. [raganything/modalprocessors.py:336-357]()

**Sources:** [raganything/modalprocessors.py:308-357]()

---

## Integration with Modal Processors

The `BaseModalProcessor` class manages the lifecycle of context extraction for specific modal items.

```mermaid
sequenceDiagram
    participant P as ProcessorMixin
    participant BMP as BaseModalProcessor
    participant CE as ContextExtractor
    
    P->>BMP: set_content_source(content_list, "minerU")
    Note over BMP: Stores source for later use
    
    P->>BMP: process_multimodal_content(item, item_info)
    BMP->>BMP: _get_context_for_item(item_info)
    BMP->>CE: extract_context(self.content_source, item_info)
    CE-->>BMP: Returns truncated context string
    
    Note over BMP: Injects context into prompt
    BMP->>LLM: modal_caption_func(prompt_with_context)
```

**Key Integration Points:**
- **Storage**: `BaseModalProcessor` stores the `content_source` and `content_format`. [raganything/modalprocessors.py:406-415]()
- **Retrieval**: The `_get_context_for_item` method calls the `ContextExtractor` using the stored source. [raganything/modalprocessors.py:417-440]()
- **Prompt Injection**: Specialized prompts (e.g., `image_prompt_with_context`) are selected when context is available. [raganything/modalprocessors.py:824-850]()

**Sources:** [raganything/modalprocessors.py:363-440](), [raganything/modalprocessors.py:824-916]()

---

## Configuration via Environment Variables

The context extraction behavior can be controlled globally via `.env` variables, which are mapped to `RAGAnythingConfig`.

| Env Variable | RAGAnythingConfig Field |
|--------------|-------------------------|
| `CONTEXT_WINDOW` | `context_window` |
| `CONTEXT_MODE` | `context_mode` |
| `MAX_CONTEXT_TOKENS` | `max_context_tokens` |
| `INCLUDE_HEADERS` | `include_headers` |
| `INCLUDE_CAPTIONS` | `include_captions` |
| `CONTEXT_FILTER_CONTENT_TYPES` | `context_filter_content_types` |

**Sources:** [raganything/config.py:78-107](), [docs/context_aware_processing.md:56-67]()

---

# Page: Knowledge Graph and Storage

# Knowledge Graph and Storage

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [env.example](env.example)
- [examples/lmstudio_integration_example.py](examples/lmstudio_integration_example.py)
- [raganything/processor.py](raganything/processor.py)
- [tests/test_insert_content_list.py](tests/test_insert_content_list.py)

</details>



## Purpose and Scope

This page documents the knowledge graph construction and storage architecture in RAG-Anything. It covers how entities and relationships are extracted from both text and multimodal content, the dual-layer entity system with `belongs_to` relationships, and the multi-storage backend architecture.

For information about how multimodal content is processed before entering the knowledge graph, see [Multimodal Content Processing](#5). For query-time retrieval from the knowledge graph, see [Query System](#7).

---

## Knowledge Graph Architecture

RAG-Anything constructs a hierarchical knowledge graph that integrates both text-based entities and multimodal entities (images, tables, equations) into a unified structure.

### Dual-Layer Entity System

```mermaid
graph TB
    subgraph "Document Processing"
        Doc["Document content_list"]
        TextContent["Text Content"]
        MMContent["Multimodal Content<br/>(image, table, equation)"]
    end
    
    subgraph "Entity Layer 1: Main Modal Entities"
        ImgEntity["Image Entity<br/>'Figure_Analysis (image)'"]
        TblEntity["Table Entity<br/>'Performance_Table (table)'"]
        EqEntity["Equation Entity<br/>'Einstein_Equation (equation)'"]
    end
    
    subgraph "Entity Layer 2: Extracted Entities"
        TextEntity1["Text Entity<br/>'Neural Networks'"]
        TextEntity2["Text Entity<br/>'Accuracy'"]
        ImgExtracted["Extracted from Image<br/>'ResNet Architecture'"]
        TblExtracted["Extracted from Table<br/>'F1 Score'"]
        EqExtracted["Extracted from Equation<br/>'Mass-Energy Equivalence'"]
    end
    
    subgraph "Knowledge Graph (chunk_entity_relation_graph)"
        KG["NetworkX Graph<br/>Nodes: All Entities<br/>Edges: Relationships"]
    end
    
    Doc --> TextContent
    Doc --> MMContent
    
    TextContent --> TextEntity1
    TextContent --> TextEntity2
    
    MMContent --> ImgEntity
    MMContent --> TblEntity
    MMContent --> EqEntity
    
    ImgEntity -->|"extract_entities"| ImgExtracted
    TblEntity -->|"extract_entities"| TblExtracted
    EqEntity -->|"extract_entities"| EqExtracted
    
    ImgExtracted -.->|"belongs_to (weight=10)"| ImgEntity
    TblExtracted -.->|"belongs_to (weight=10)"| TblEntity
    EqExtracted -.->|"belongs_to (weight=10)"| EqEntity
    
    TextEntity1 --> KG
    TextEntity2 --> KG
    ImgEntity --> KG
    TblEntity --> KG
    EqEntity --> KG
    ImgExtracted --> KG
    TblExtracted --> KG
    EqExtracted --> KG
```

**Sources:** `ProcessorMixin` in [raganything/processor.py:32-33](), multimodal extraction logic in [raganything/processor.py:1205-1267](), and `BaseModalProcessor` logic in [raganything/modalprocessors.py:326-335]().

The system creates two layers of entities:

1. **Main Modal Entities** (Layer 1): Represent entire multimodal objects. These are created directly from parsed content (images, tables, equations) and named with the format: `"{descriptive_name} ({type})"`, e.g., `"Performance_Comparison (table)"`.
2. **Extracted Entities** (Layer 2): Domain-specific entities extracted via LLM analysis from both text chunks and modal content chunks. These are connected to their source modal entities via `"belongs_to"` relationships.

### Entity Creation Flow

```mermaid
flowchart TD
    subgraph "Stage 1: Modal Description Generation"
        MM["Multimodal Item"]
        Processor["Modal Processor<br/>(ImageModalProcessor,<br/>TableModalProcessor,<br/>EquationModalProcessor)"]
        Desc["generate_description_only()"]
        LLM["LLM/VLM Analysis"]
        EntityInfo["entity_info:<br/>{entity_name, entity_type, summary}"]
    end
    
    subgraph "Stage 2: Chunk & Main Entity Creation"
        ChunkTemplate["_apply_chunk_template()<br/>Format with prompt template"]
        ChunkContent["Formatted Chunk Content"]
        ChunkID["compute_mdhash_id()<br/>Generate chunk_id"]
        StoreChunk["Store to text_chunks<br/>& chunks_vdb"]
        MainEntityNode["Create Main Entity Node<br/>in chunk_entity_relation_graph"]
        EntityVDB["Store to entities_vdb"]
        FullEntities["Store to full_entities"]
    end
    
    subgraph "Stage 3: Entity Extraction"
        ExtractCall["extract_entities()<br/>(from LightRAG)"]
        ChunkResults["chunk_results:<br/>List[(maybe_nodes, maybe_edges)]"]
        ExtractedEnts["Extracted Entities<br/>from LLM analysis"]
    end
    
    subgraph "Stage 4: belongs_to Relations"
        BelongsToLogic["_batch_add_belongs_to_relations()"]
        BelongsToEdge["Create Edge:<br/>extracted_entity -> main_modal_entity<br/>weight=10.0, keywords='belongs_to'"]
        RelVDB["Store to relationships_vdb"]
    end
    
    subgraph "Stage 5: Graph Merge"
        MergeCall["merge_nodes_and_edges()"]
        FinalKG["chunk_entity_relation_graph<br/>Updated with all entities & relations"]
    end
    
    MM --> Processor
    Processor --> Desc
    Desc --> LLM
    LLM --> EntityInfo
    
    EntityInfo --> ChunkTemplate
    ChunkTemplate --> ChunkContent
    ChunkContent --> ChunkID
    ChunkID --> StoreChunk
    EntityInfo --> MainEntityNode
    MainEntityNode --> EntityVDB
    MainEntityNode --> FullEntities
    
    StoreChunk --> ExtractCall
    ExtractCall --> ChunkResults
    ChunkResults --> ExtractedEnts
    
    ExtractedEnts --> BelongsToLogic
    MainEntityNode --> BelongsToLogic
    BelongsToLogic --> BelongsToEdge
    BelongsToEdge --> RelVDB
    
    ChunkResults --> MergeCall
    BelongsToEdge --> MergeCall
    MergeCall --> FinalKG
```

**Sources:** `_process_multimodal_content` flow in [raganything/processor.py:706-881](), `_batch_add_belongs_to_relations` in [raganything/processor.py:1205-1267](), and modal processor description logic in [raganything/modalprocessors.py:465-545]().

---

## Entity Types and Naming

### Main Modal Entity Naming Convention

Main modal entities follow a consistent naming pattern that includes both a descriptive name and the content type: `{entity_name} ({entity_type})`. This naming convention is enforced in the modal processor response parsing.

**Sources:** `_parse_response` in [raganything/modalprocessors.py:1011-1013](), `_parse_table_response` in [raganything/modalprocessors.py:1205-1207](), and `_parse_equation_response` in [raganything/modalprocessors.py:1389-1391]().

### Entity Data Structure

Each entity stored in the knowledge graph contains metadata such as `entity_id`, `entity_type`, `description`, `source_id`, and `file_path`.

**Sources:** Entity structure in [raganything/modalprocessors.py:505-513]() and [raganything/processor.py:1084-1092]().

---

## Relationship Types

### Standard Entity Relationships

Standard relationships are extracted by LightRAG's `extract_entities()` function from chunk content. These capture semantic relationships between entities mentioned in the text.

**Sources:** [raganything/processor.py:1176-1203](), [raganything/modalprocessors.py:727-734]().

### belongs_to Relationships

The `"belongs_to"` relationship is unique to RAG-Anything's multimodal processing. It creates hierarchical connections from extracted entities to their source modal entities.

```mermaid
graph LR
    subgraph "Example: Table Processing"
        TblChunk["Table Chunk:<br/>'Performance_Table (table)'<br/>Contains accuracy metrics..."]
        
        ExtEntity1["Extracted Entity:<br/>'F1 Score'"]
        ExtEntity2["Extracted Entity:<br/>'Precision'"]
        ExtEntity3["Extracted Entity:<br/>'Recall'"]
        
        MainEntity["Main Modal Entity:<br/>'Model_Performance_Table (table)'"]
    end
    
    TblChunk -.->|"extract_entities()"| ExtEntity1
    TblChunk -.->|"extract_entities()"| ExtEntity2
    TblChunk -.->|"extract_entities()"| ExtEntity3
    
    ExtEntity1 -->|"belongs_to<br/>weight=10.0"| MainEntity
    ExtEntity2 -->|"belongs_to<br/>weight=10.0"| MainEntity
    ExtEntity3 -->|"belongs_to<br/>weight=10.0"| MainEntity
```

**Sources:** `_batch_add_belongs_to_relations` in [raganything/processor.py:1205-1267]() and [raganything/modalprocessors.py:738-770]().

---

## Storage Architecture

RAG-Anything uses a multi-storage architecture inherited from LightRAG, with distinct storage systems working together.

### Storage System Overview

```mermaid
graph TB
    subgraph "Storage Backends"
        TextChunks["text_chunks<br/>(KV Storage)<br/>Raw chunk content"]
        ChunksVDB["chunks_vdb<br/>(Vector DB)<br/>Chunk embeddings"]
        EntitiesVDB["entities_vdb<br/>(Vector DB)<br/>Entity embeddings"]
        RelationsVDB["relationships_vdb<br/>(Vector DB)<br/>Relation embeddings"]
        KG["chunk_entity_relation_graph<br/>(Graph Storage)<br/>NetworkX or Neo4j/AGE"]
        FullEntities["full_entities<br/>(KV Storage)<br/>Doc-level entity list"]
        FullRelations["full_relations<br/>(KV Storage)<br/>Doc-level relation list"]
        DocStatus["doc_status<br/>(KV Storage)<br/>Processing status"]
        ParseCache["parse_cache<br/>(KV Storage)<br/>Parsed content cache"]
    end
    
    subgraph "Data Types"
        Chunks["Chunks"]
        Entities["Entities"]
        Relations["Relationships"]
        Status["Metadata"]
    end
    
    Chunks --> TextChunks
    Chunks --> ChunksVDB
    
    Entities --> EntitiesVDB
    Entities --> KG
    Entities --> FullEntities
    
    Relations --> RelationsVDB
    Relations --> KG
    Relations --> FullRelations
    
    Status --> DocStatus
    Status --> ParseCache
```

**Sources:** `lightrag` storage access in [raganything/processor.py:1006-1022](), [raganything/processor.py:1099-1101](), and [raganything/modalprocessors.py:380-384]().

### Key Storage Components

- **text_chunks (KV Storage)**: Stores raw chunk content and multimodal flags [raganything/processor.py:911-924]().
- **chunks_vdb / entities_vdb / relationships_vdb**: Vector databases for semantic retrieval [raganything/processor.py:1015](), [raganything/processor.py:1099-1101]().
- **chunk_entity_relation_graph**: Graph storage for entity-relationship structure [raganything/processor.py:1095-1097]().
- **doc_status**: Tracks document processing state, including the `multimodal_processed` flag [raganything/processor.py:138-159](), [raganything/processor.py:189-200]().
- **parse_cache**: Caches parsed document results using a generated `cache_key` [raganything/processor.py:50-98](), [raganything/processor.py:212-278]().

---

## Storage Backend Options

RAG-Anything supports multiple storage backends configured via environment variables or `RAGAnythingConfig`.

| Storage Type | Options |
|--------------|---------|
| **KV Storage** | `JsonKVStorage`, `PGKVStorage`, `MongoDBStorage`, `RedisStorage` |
| **Vector DB** | `NanoVectorDBStorage`, `PGVectorStorage`, `MilvusVectorStorage`, `QdrantVectorStorage` |
| **Graph DB** | `NetworkXStorage`, `Neo4jStorage`, `AGEStorage`, `MongoDBGraphStorage` |

**Sources:** `env.example:152-212]()` and `RAGAnythingConfig` parameters.

For details, see [Storage Architecture](#6.2) and [Storage Backend Configuration](#8.3).

---

# Page: Knowledge Graph Construction

# Knowledge Graph Construction

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [raganything/modalprocessors.py](raganything/modalprocessors.py)
- [raganything/processor.py](raganything/processor.py)
- [tests/test_insert_content_list.py](tests/test_insert_content_list.py)

</details>



This page documents how RAG-Anything transforms multimodal document content into a structured knowledge graph. The system extracts entities from text, images, tables, and equations, establishes cross-modal relationships, and preserves document hierarchy through specialized `belongs_to` connections.

For information about the underlying storage systems and backend options, see [Storage Architecture](#6.2). For details on how multimodal content is processed before graph construction, see [Multimodal Content Processing](#5).

---

## Overview

Knowledge graph construction in RAG-Anything is a multi-stage process that converts processed document content into a queryable graph structure. The system creates two types of entities:

1. **Main Multimodal Entities** - Top-level entities representing images, tables, and equations as distinct knowledge objects (e.g., "Performance Comparison Table (table)").
2. **Sub-Entities** - Entities extracted from the content descriptions via LLM analysis (e.g., concepts, metrics, people mentioned within a table).

These entities are connected through:
- **Standard Relationships** - Semantic connections discovered by the LLM.
- **`belongs_to` Relationships** - Hierarchical links connecting sub-entities to their source multimodal entities.

The resulting graph enables both semantic retrieval (via vector embeddings) and structural traversal (via graph relationships).

---

## Entity Extraction Architecture

The extraction process bridges the gap between raw parsed content and the final graph storage.

### Natural Language Space to Code Entity Space

The following diagram illustrates how natural language elements from documents are mapped to specific code classes and functions within the `raganything` package.

**Entity Extraction Data Flow**
```mermaid
graph TB
    subgraph "Natural Language Space"
        DocContent["Document Content<br/>(Text, Images, Tables)"]
    end

    subgraph "Code Entity Space: ProcessorMixin"
        direction TB
        MainProc["ProcessorMixin<br/>raganything/processor.py"]
        
        subgraph "Main Entity Creation"
            StoreMain["_store_multimodal_main_entities<br/>processor.py:1023-1115"]
            GenID["compute_mdhash_id<br/>lightrag/utils.py"]
        end
        
        subgraph "Sub-Entity Extraction"
            BatchExtract["_batch_extract_entities_lightrag_style<br/>processor.py:1176-1203"]
            LightRAGExtract["extract_entities<br/>lightrag/operate.py"]
        end
    end

    subgraph "Storage Entities"
        KG["chunk_entity_relation_graph<br/>(NetworkX)"]
        VDB["entities_vdb<br/>(Vector DB)"]
    end

    DocContent --> MainProc
    MainProc --> StoreMain
    StoreMain --> GenID
    GenID --> KG
    GenID --> VDB
    
    MainProc --> BatchExtract
    BatchExtract --> LightRAGExtract
    LightRAGExtract --> KG
    LightRAGExtract --> VDB
```
Sources: [raganything/processor.py:1023-1115](), [raganything/processor.py:1176-1203](), [raganything/modalprocessors.py:20-27]()

**Stage 1: Main Entity Creation**
Main multimodal entities are created first to represent the multimodal content items themselves. The process generates an `entity_name` with a type suffix (e.g., `(image)`), an `entity_type`, and a `content` field containing the enhanced description from the modal processor. The ID is generated using `compute_mdhash_id(entity_name, prefix="ent-")`.

**Stage 2: Sub-Entity Extraction**
Sub-entities are extracted from the enhanced descriptions using LightRAG's LLM-based entity extraction. The function `_batch_extract_entities_lightrag_style` iterates through multimodal chunks and uses `extract_entities` to identify concepts, metrics, or people mentioned within the descriptions.

Sources: [raganything/processor.py:1023-1115](), [raganything/processor.py:1176-1203](), [raganything/modalprocessors.py:465-545]()

---

## Relationship Mapping

Relationships define how entities interact within the graph.

**Relationship Mapping Flow**
```mermaid
graph TB
    subgraph "Logic Layer"
        RelLogic["_batch_add_belongs_to_relations_type_aware<br/>processor.py:1205-1274"]
    end

    subgraph "Relationship Types"
        Semantic["Semantic Relationships<br/>(LLM Discovered)"]
        BelongsTo["belongs_to Relationships<br/>(Structural)"]
    end

    subgraph "Code Implementation"
        UpsertEdge["knowledge_graph_inst.upsert_edge<br/>processor.py:1248-1251"]
    end

    RelLogic --> BelongsTo
    RelLogic --> Semantic
    BelongsTo --> UpsertEdge
    Semantic --> UpsertEdge
```

**Belongs_to Relationships**
The `belongs_to` relationship is a special hierarchical link. It is created in `_batch_add_belongs_to_relations_type_aware` to link every sub-entity back to its parent multimodal entity. 
- **Keywords**: `"belongs_to,part_of,contained_in"`
- **Weight**: Defaulted to `10.0` to emphasize structural importance.
- **Description**: Formatted as `"Entity {src} belongs to {tgt}"`.

Sources: [raganything/processor.py:1205-1274](), [raganything/modalprocessors.py:736-770]()

---

## Graph Structure and Schema

Every entity and relationship follows a strict schema to ensure compatibility with retrieval modes.

### Node Schema
| Attribute | Type | Source |
|-----------|------|--------|
| `entity_id` | string | [raganything/processor.py:1085]() |
| `entity_type` | string | [raganything/processor.py:1086]() |
| `description` | string | [raganything/processor.py:1087]() |
| `source_id` | string | [raganything/processor.py:1088]() |
| `file_path` | string | [raganything/processor.py:1089]() |

### Edge Schema
| Attribute | Type | Source |
|-----------|------|--------|
| `keywords` | string | [raganything/processor.py:1243]() |
| `description` | string | [raganything/processor.py:1242]() |
| `weight` | float | [raganything/processor.py:1245]() |
| `source_id` | string | [raganything/processor.py:1244]() |

Sources: [raganything/processor.py:1084-1097](), [raganything/processor.py:1240-1266]()

---

## Multi-Storage Integration

The knowledge graph data is distributed across three storage layers to optimize different retrieval strategies.

| Storage Name | Code Reference | Purpose |
|--------------|----------------|---------|
| `entities_vdb` | [raganything/processor.py:1078]() | Vector search for semantic entity matching. |
| `relationships_vdb` | [raganything/processor.py:1255]() | Vector search for semantic relationship matching. |
| `chunk_entity_relation_graph` | [raganything/processor.py:1095]() | NetworkX graph for structural traversal. |
| `full_entities` | [raganything/processor.py:1104]() | KV Storage mapping document IDs to entity lists. |

Sources: [raganything/processor.py:1078-1115](), [raganything/processor.py:1255-1266]()

---

## Batch Processing Pipeline

The `_process_multimodal_content_batch_type_aware` method in `ProcessorMixin` orchestrates the construction in a pipeline fashion.

1.  **Description Generation**: Uses `generate_description_only` from modal processors.
2.  **Chunking**: `_convert_to_lightrag_chunks_type_aware` transforms descriptions into chunks.
3.  **Entity Insertion**: `_store_multimodal_main_entities` populates the graph and VDB.
4.  **Relationship Linking**: `_batch_add_belongs_to_relations_type_aware` establishes hierarchy.
5.  **Final Merge**: `_batch_merge_lightrag_style` commits all nodes and edges to the persistent graph.

Sources: [raganything/processor.py:706-881](), [raganything/processor.py:1276-1297]()

---

## Context-Aware Entity Extraction

Multimodal entities are extracted with awareness of their surrounding document context using the `ContextExtractor` system. This allows the LLM to understand that a table on page 5 is related to the text on page 4.

**Context Configuration (`ContextConfig`)**
- `context_window`: Number of surrounding items to include.
- `context_mode`: Whether to use `page`, `chunk`, or `token` boundaries.

The `extract_context` method is called during description generation to provide the LLM with the necessary background information to name entities accurately.

Sources: [raganything/modalprocessors.py:33-358](), [raganything/modalprocessors.py:415-440]()

---

# Page: Storage Architecture

# Storage Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [docs/multimodal_rag_failure_modes.md](docs/multimodal_rag_failure_modes.md)
- [env.example](env.example)
- [examples/lmstudio_integration_example.py](examples/lmstudio_integration_example.py)
- [raganything/asset_urls.py](raganything/asset_urls.py)
- [raganything/raganything.py](raganything/raganything.py)
- [tests/test_asset_urls.py](tests/test_asset_urls.py)

</details>



This page documents RAG-Anything's multi-layered storage architecture, which extends LightRAG's storage system with additional multimodal-specific storage components. This architecture enables efficient indexing, retrieval, and caching of both text and multimodal content.

For information about how knowledge graphs are constructed and populated, see [Knowledge Graph Construction](6.1). For query retrieval strategies that leverage these storage systems, see [Query Architecture](7.1).

---

## Overview

RAG-Anything implements a **seven-storage architecture** built on top of LightRAG's foundation. Each storage type serves a specific purpose in the document processing and retrieval pipeline:

| Storage Type | Purpose | Backend Options |
|--------------|---------|-----------------|
| **text_chunks** | Raw text chunk storage with metadata | PostgreSQL, MongoDB, Redis |
| **chunks_vdb** | Vector embeddings for chunk retrieval | PostgreSQL, Milvus, Qdrant |
| **entities_vdb** | Vector embeddings for entity retrieval | PostgreSQL, Milvus, Qdrant |
| **relationships_vdb** | Vector embeddings for relationship retrieval | PostgreSQL, Milvus, Qdrant |
| **chunk_entity_relation_graph** | Knowledge graph structure (nodes + edges) | Neo4j, AGE, NetworkX (in-memory) |
| **doc_status** | Document processing status tracking | PostgreSQL, MongoDB |
| **parse_cache** | Cached document parsing results | PostgreSQL, MongoDB, Redis |

The storage architecture is designed to support **hybrid retrieval** strategies that combine vector similarity search with graph traversal, enabling both semantic and structural queries across multimodal content.

**Sources:** [raganything/raganything.py:51-103](), [env.example:152-212]()

---

## Storage Layer Architecture

The following diagram illustrates how the seven storage components interact within the RAG-Anything system:

```mermaid
graph TB
    subgraph "Document Processing Layer"
        Parser["Document Parser"]
        TextContent["Text Content"]
        MultimodalContent["Multimodal Content<br/>(Images/Tables/Equations)"]
    end
    
    subgraph "LightRAG Storage Layer"
        TextChunks["text_chunks<br/>(Key-Value Storage)"]
        ChunksVDB["chunks_vdb<br/>(Vector Database)"]
        
        EntitiesVDB["entities_vdb<br/>(Vector Database)"]
        RelationsVDB["relationships_vdb<br/>(Vector Database)"]
        
        KnowledgeGraph["chunk_entity_relation_graph<br/>(Graph Storage)"]
        
        FullEntities["full_entities<br/>(Key-Value Storage)"]
        FullRelations["full_relations<br/>(Key-Value Storage)"]
        
        DocStatus["doc_status<br/>(Document Status Storage)"]
    end
    
    subgraph "RAGAnything Extensions"
        ParseCache["parse_cache<br/>(Key-Value Storage)"]
    end
    
    subgraph "Query Layer"
        VectorRetrieval["Vector Retrieval"]
        GraphTraversal["Graph Traversal"]
        HybridFusion["Hybrid Fusion"]
    end
    
    Parser --> ParseCache
    ParseCache --> TextContent
    ParseCache --> MultimodalContent
    
    TextContent --> TextChunks
    TextContent --> ChunksVDB
    TextContent --> DocStatus
    
    MultimodalContent --> TextChunks
    MultimodalContent --> ChunksVDB
    MultimodalContent --> EntitiesVDB
    MultimodalContent --> KnowledgeGraph
    MultimodalContent --> DocStatus
    
    TextChunks --> KnowledgeGraph
    KnowledgeGraph --> EntitiesVDB
    KnowledgeGraph --> RelationsVDB
    KnowledgeGraph --> FullEntities
    KnowledgeGraph --> FullRelations
    
    ChunksVDB --> VectorRetrieval
    EntitiesVDB --> VectorRetrieval
    RelationsVDB --> VectorRetrieval
    
    KnowledgeGraph --> GraphTraversal
    
    VectorRetrieval --> HybridFusion
    GraphTraversal --> HybridFusion
    
    DocStatus --> HybridFusion
```

**Sources:** [raganything/raganything.py:51-103](), [raganything/raganything.py:277-300]()

---

## Storage Types and Data Models

### 1. text_chunks Storage

**Purpose:** Stores raw text content with metadata for all chunks (both text and multimodal).

**Storage Class:** `key_string_value_json_storage_cls` (configurable via `LIGHTRAG_KV_STORAGE`)

**Data Model:**
```python
{
    "chunk-<hash>": {
        "content": str,                    # Raw or templated chunk content
        "tokens": int,                     # Token count
        "full_doc_id": str,                # Document ID (doc-<hash>)
        "chunk_order_index": int,          # Position in document
        "file_path": str,                  # Source file reference
        "llm_cache_list": List[str],       # LLM response cache keys
        
        # Multimodal-specific fields (optional)
        "is_multimodal": bool,             # True for multimodal chunks
        "modal_entity_name": str,          # e.g., "Figure 1 (image)"
        "original_type": str,              # image, table, equation, generic
        "page_idx": int                    # Source page number
    }
}
```

**Usage in Code:**
- Unified storage for text and multimodal chunks.
- Multimodal chunks use specialized templates.
- Metadata tracks chunk position and relationships.

**Sources:** [raganything/raganything.py:71-84](), [env.example:101-103]()

---

### 2. chunks_vdb Storage

**Purpose:** Vector embeddings of chunk content for semantic similarity search.

**Storage Class:** `vector_db_storage_cls` (configurable via `LIGHTRAG_VECTOR_STORAGE`)

**Supported Backends:**
- **PostgreSQL** with pgvector extension (`PGVectorStorage`)
- **Milvus** vector database (`MilvusVectorDBStorge`)
- **Qdrant** vector database (`QdrantVectorDBStorage`)

**Configuration:**
```bash
# env.example
LIGHTRAG_VECTOR_STORAGE=PGVectorStorage  # or MilvusVectorDBStorge, QdrantVectorDBStorage
EMBEDDING_MODEL=bge-m3:latest
EMBEDDING_DIM=1024
```

**Sources:** [raganything/raganything.py:73-84](), [env.example:134-150](), [env.example:199-209]()

---

### 3. entities_vdb and relationships_vdb Storage

**Purpose:** Vector embeddings of extracted entities and relationships for entity-centric retrieval.

**Storage Class:** Same as `chunks_vdb` (shared vector storage backend)

**Key Features:**
- Multimodal main entities (e.g., "TableName (table)") indexed separately.
- Supports `belongs_to` relationships linking content to modal entities.
- Enables entity-centric queries across modalities.

**Sources:** [raganything/raganything.py:73-84](), [env.example:86-89]()

---

### 4. chunk_entity_relation_graph Storage

**Purpose:** Graph database storing nodes (entities) and edges (relationships) for structural queries.

**Storage Class:** `graph_storage_cls` (configurable via `LIGHTRAG_GRAPH_STORAGE`)

**Supported Backends:**
- **Neo4j** graph database (`Neo4JStorage`)
- **Apache AGE** (PostgreSQL extension) (`AGEStorage`)
- **NetworkX** in-memory graph (default for local development)
- **MongoDB** graph storage (`MongoGraphStorage`)

**Configuration:**
```bash
# Neo4j
LIGHTRAG_GRAPH_STORAGE=Neo4JStorage
NEO4J_URI=neo4j+s://xxxxxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD='your_password'

# MongoDB
MONGO_URI=mongodb://root:root@localhost:27017/
MONGO_DATABASE=LightRAG
```

**Sources:** [raganything/raganything.py:73-84](), [env.example:177-181](), [env.example:193-195]()

---

### 5. doc_status Storage

**Purpose:** Tracks document processing status, including multimodal processing completion.

**Storage Class:** `doc_status_storage_cls` (configurable via `LIGHTRAG_DOC_STATUS_STORAGE`)

**Processing States:**

```mermaid
stateDiagram-v2
    [*] --> PROCESSING: parse_document()
    PROCESSING --> PROCESSED: Text content inserted
    PROCESSED --> MultimodalProcessing: _process_multimodal_content()
    MultimodalProcessing --> FullyProcessed: multimodal_processed=True
    FullyProcessed --> [*]
    
    note right of PROCESSED
        status=DocStatus.PROCESSED
        multimodal_processed=False
    end note
    
    note right of FullyProcessed
        status=DocStatus.PROCESSED
        multimodal_processed=True
    end note
```

**Sources:** [raganything/raganything.py:73-84](), [env.example:152-156]()

---

### 6. parse_cache Storage

**Purpose:** Caches document parsing results to avoid redundant parsing operations.

**Storage Class:** `key_string_value_json_storage_cls` (same as text_chunks)

**Usage in Code:**
- Created during initialization with namespace `parse_cache` [raganything/raganything.py:283]().
- Uses the same KV storage class configured for LightRAG [raganything/raganything.py:277-282]().

**Invalidation Strategy:**
- File modification time (`mtime`) changes.
- Parser configuration changes.
- Parse method changes.

**Sources:** [raganything/raganything.py:94-95](), [raganything/raganything.py:277-289]()

---

### 7. Asset URL Mapping

**Purpose:** Maps local filesystem paths to public URLs (S3, CDN) for frontend display.

**Configuration:**
- `RAGANYTHING_PUBLIC_ASSET_BASE_URL`: The root URL of the public storage [raganything/asset_urls.py:77]().
- `RAGANYTHING_PUBLIC_ASSET_STRIP_PREFIX`: The local absolute path prefix to strip from media paths [raganything/asset_urls.py:78]().

**Fields Handled:**
- `img_path` -> `img_path_public_url`
- `table_img_path` -> `table_img_path_public_url`
- `equation_img_path` -> `equation_img_path_public_url`

**Sources:** [raganything/asset_urls.py:23-27](), [raganything/asset_urls.py:65-118](), [env.example:67-70]()

---

## Storage Backend Configuration

### Backend Options Matrix

| Backend | text_chunks | chunks_vdb | entities_vdb | relationships_vdb | graph | doc_status | parse_cache |
|---------|-------------|------------|--------------|-------------------|-------|------------|-------------|
| **PostgreSQL** | ✓ | ✓ | ✓ | ✓ | ✓ (AGE) | ✓ | ✓ |
| **MongoDB** | ✓ | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ |
| **Redis** | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |
| **Neo4j** | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ |
| **Milvus** | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |
| **Qdrant** | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |

**Sources:** [env.example:152-212]()

---

## Storage Initialization and Lifecycle

### Initialization Flow

```mermaid
flowchart TB
    Start["RAGAnything.__post_init__()"]
    
    CheckLightRAG{"lightrag<br/>provided?"}
    
    EnsureInit["_ensure_lightrag_initialized()"]
    
    InheritFuncs["Inherit functions from<br/>lightrag instance"]
    
    CreateLightRAG["Create LightRAG instance<br/>with lightrag_kwargs"]
    
    InitStorages["lightrag.initialize_storages()"]
    
    InitPipeline["initialize_pipeline_status()"]
    
    CreateParseCache["Create parse_cache using<br/>key_string_value_json_storage_cls"]
    
    InitParseCache["parse_cache.initialize()"]
    
    InitProcessors["_initialize_processors()"]
    
    Ready["Ready for Processing"]
    
    Start --> EnsureInit
    EnsureInit --> CheckLightRAG
    
    CheckLightRAG -->|Yes| InheritFuncs
    CheckLightRAG -->|No| CreateLightRAG
    
    InheritFuncs --> InitStorages
    CreateLightRAG --> InitStorages
    
    InitStorages --> InitPipeline
    InitPipeline --> CreateParseCache
    CreateParseCache --> InitParseCache
    InitParseCache --> InitProcessors
    InitProcessors --> Ready
```

**Initialization Code:**
- Main entry point: `_ensure_lightrag_initialized` [raganything/raganything.py:229-311]().
- Parse cache setup: [raganything/raganything.py:277-289]().
- Processor initialization: [raganything/raganything.py:175-218]().

**Sources:** [raganything/raganything.py:229-311]()

---

### Storage Finalization

**Purpose:** Ensures all cached data is persisted and connections are closed properly.

```mermaid
flowchart LR
    Trigger["atexit.register(close)<br/>or Manual Call"]
    
    Close["close()"]
    
    FinalizeStorages["finalize_storages()"]
    
    subgraph "Concurrent Finalization"
        ParseCache["parse_cache.finalize()"]
        LightRAGStorages["lightrag.finalize_storages()"]
    end
    
    Done["Resources Cleaned Up"]
    
    Trigger --> Close
    Close --> FinalizeStorages
    FinalizeStorages --> ParseCache
    FinalizeStorages --> LightRAGStorages
    ParseCache --> Done
    LightRAGStorages --> Done
```

**Finalization Code:**
- `close` method handles various async/sync context scenarios [raganything/raganything.py:143-173]().
- `finalize_storages` gathers cleanup tasks for both `parse_cache` and `lightrag` [raganything/raganything.py:369-413]().

**Sources:** [raganything/raganything.py:143-173](), [raganything/raganything.py:369-413]()

---

## Storage Performance Considerations

### Concurrency Controls

**Batch Processing:**
- `MAX_PARALLEL_INSERT`: Limits concurrent document insertions to the storage backend [env.example:100]().
- `EMBEDDING_FUNC_MAX_ASYNC`: Limits concurrent embedding requests [env.example:145]().

### Cache Optimization

**Parse Cache Benefits:**
- Avoids redundant document parsing (expensive operation).
- Persisted across RAGAnything instances using LightRAG's KV storage backend.

**Tiktoken Cache:**
- `TIKTOKEN_CACHE_DIR`: Used for offline deployment to prevent downloading models from the internet [raganything/raganything.py:23-25](), [env.example:17]().

**Sources:** [raganything/raganything.py:23-25](), [env.example:100-103](), [env.example:145]()

---

# Page: Query System

# Query System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [raganything/batch.py](raganything/batch.py)
- [raganything/query.py](raganything/query.py)

</details>



The Query System is the retrieval and question-answering subsystem of RAG-Anything. It provides three query modes: pure text queries that leverage LightRAG's knowledge graph retrieval, multimodal queries that accept explicit image/table/equation content, and VLM-enhanced queries that automatically detect and process images in retrieved context. All query functionality is implemented through the `QueryMixin` class [raganything/query.py:23](), which integrates with LightRAG's retrieval engine while adding multimodal capabilities.

For document processing and indexing operations, see [Document Processing](#4). For configuration of LLM and vision model providers, see [Model Provider Configuration](#8.4).

## QueryMixin Architecture

The `QueryMixin` class [raganything/query.py:23-24]() provides query functionality that extends LightRAG's base capabilities. It is designed as a mixin to be inherited by the main `RAGAnything` class, providing three distinct query methods:

| Method | Type | Key Capability |
|--------|------|----------------|
| `aquery` | Text | Pure text query via LightRAG [raganything/query.py:102]() |
| `aquery_with_multimodal` | Multimodal | Query with explicit multimodal content [raganything/query.py:195]() |
| `aquery_vlm_enhanced` | VLM-Enhanced | Automatic image processing from retrieved context [raganything/query.py:343]() |

### Query System Component Relationships

```mermaid
graph TB
    User["User Query Request"]
    
    QueryMixin["QueryMixin Class<br/>(raganything/query.py:23)"]
    
    subgraph "Query Methods"
        AQuery["aquery()<br/>(raganything/query.py:102)"]
        AMM["aquery_with_multimodal()<br/>(raganything/query.py:195)"]
        AVLM["aquery_vlm_enhanced()<br/>(raganything/query.py:343)"]
    end
    
    subgraph "Processing Helpers"
        ProcessMM["_process_multimodal_query_content()<br/>(raganything/query.py:412)"]
        ProcessImg["_process_image_paths_for_vlm()<br/>(raganything/query.py:579)"]
        BuildVLM["_build_vlm_messages_with_images()<br/>(raganything/query.py:698)"]
        CallVLM["_call_vlm_with_multimodal_content()<br/>(raganything/query.py:782)"]
        GenCache["_generate_multimodal_cache_key()<br/>(raganything/query.py:26)"]
    end
    
    subgraph "Content Processors"
        GetProc["get_processor_for_type()<br/>(raganything/utils.py:228)"]
        ImgDesc["_describe_image_for_query()<br/>(raganything/query.py:495)"]
        TblDesc["_describe_table_for_query()<br/>(raganything/query.py:526)"]
        EqDesc["_describe_equation_for_query()<br/>(raganything/query.py:543)"]
    end
    
    LightRAGQuery["LightRAG.aquery()<br/>Base Retrieval"]
    LLMFunc["llm_model_func"]
    VisionFunc["vision_model_func"]
    QueryParam["QueryParam<br/>(lightrag)"]
    Cache["llm_response_cache<br/>(lightrag)"]
    
    User --> QueryMixin
    QueryMixin --> AQuery
    QueryMixin --> AMM
    QueryMixin --> AVLM
    
    AQuery --> QueryParam
    AQuery --> LightRAGQuery
    AQuery -.vlm_enhanced=True.-> AVLM
    
    AMM --> GenCache
    AMM --> ProcessMM
    ProcessMM --> GetProc
    ProcessMM --> ImgDesc
    ProcessMM --> TblDesc
    ProcessMM --> EqDesc
    AMM --> AQuery
    AMM --> Cache
    
    AVLM --> QueryParam
    AVLM --> LightRAGQuery
    AVLM --> ProcessImg
    AVLM --> BuildVLM
    AVLM --> CallVLM
    
    ImgDesc --> VisionFunc
    TblDesc --> LLMFunc
    EqDesc --> LLMFunc
    CallVLM --> VisionFunc
    
    LightRAGQuery --> LLMFunc
```

**Sources:** [raganything/query.py:23-859](), [raganything/utils.py:228-249]()

## Text Queries

The `aquery` method [raganything/query.py:102-193]() provides pure text querying by delegating to LightRAG's retrieval engine. It supports all LightRAG query modes and can automatically upgrade to VLM-enhanced mode if a vision model is available [raganything/query.py:128-143]().

### Query Flow

```mermaid
flowchart TD
    Start["aquery(query, mode, **kwargs)"]
    CheckLightRAG{{"lightrag<br/>initialized?<br/>(raganything/query.py:120)"}}
    CheckVLM{{"vlm_enhanced<br/>parameter<br/>(raganything/query.py:126)"}}
    AutoVLM{{"vision_model_func<br/>available?<br/>(raganything/query.py:130)"}}
    UseVLM["Call aquery_vlm_enhanced()<br/>(raganything/query.py:141)"]
    CreateParam["Create QueryParam(mode, **kwargs)<br/>(raganything/query.py:162)"]
    CallLightRAG["await lightrag.aquery(query, param)<br/>(raganything/query.py:169)"]
    Return["Return result"]
    Error["Raise ValueError"]
    
    Start --> CheckLightRAG
    CheckLightRAG -->|No| Error
    CheckLightRAG -->|Yes| CheckVLM
    CheckVLM -->|None| AutoVLM
    CheckVLM -->|True| UseVLM
    CheckVLM -->|False| CreateParam
    AutoVLM -->|Yes| UseVLM
    AutoVLM -->|No| CreateParam
    CreateParam --> CallLightRAG
    CallLightRAG --> Return
    UseVLM --> Return
```

### LightRAG Query Modes

The query mode parameter [raganything/query.py:110]() controls LightRAG's retrieval strategy:

| Mode | Description |
|------|-------------|
| `local` | Local search around specific entities |
| `global` | Global graph traversal |
| `hybrid` | Combines local + global |
| `naive` | Simple vector similarity |
| `mix` | Adaptive mode selection (default) |
| `bypass` | Skip retrieval, direct LLM |

For details, see [Text Queries](#7.2).

**Sources:** [raganything/query.py:102-193]()

## Multimodal Queries

The `aquery_with_multimodal` method [raganything/query.py:195-341]() enables queries that include explicit multimodal content (images, tables, equations). It processes the multimodal content to generate enhanced textual descriptions [raganything/query.py:412-453](), then performs a standard text query with the enriched context.

### Multimodal Query Processing Flow

```mermaid
flowchart TD
    Start["aquery_with_multimodal(query, multimodal_content, mode)"]
    GenKey["Generate cache key<br/>_generate_multimodal_cache_key()<br/>(raganything/query.py:26)"]
    CheckCache{{"Cache hit?<br/>(raganything/query.py:246)"}}
    ProcessContent["Process multimodal content<br/>_process_multimodal_query_content()<br/>(raganything/query.py:412)"]
    
    subgraph ContentLoop["For each content item"]
        GetType["Get content type"]
        GetProc["Get processor<br/>get_processor_for_type()"]
        GenDesc["Generate description"]
    end
    
    BuildQuery["Build enhanced query text"]
    CallAQuery["await aquery(enhanced_query, mode)"]
    SaveCache["Save result to cache<br/>(raganything/query.py:314)"]
    Return["Return result"]
    
    Start --> GenKey
    GenKey --> CheckCache
    CheckCache -->|Hit| Return
    CheckCache -->|Miss| ProcessContent
    ProcessContent --> ContentLoop
    ContentLoop --> BuildQuery
    BuildQuery --> CallAQuery
    CallAQuery --> SaveCache
    SaveCache --> Return
```

### Content Description Generation

The system generates descriptions for each content type [raganything/query.py:465-577]():
1. **Images**: Analyzed via `vision_model_func` [raganything/query.py:495-524]().
2. **Tables**: Structured analysis using `modal_caption_func` [raganything/query.py:526-541]().
3. **Equations**: Formula explanation using `modal_caption_func` [raganything/query.py:543-558]().

For details, see [Multimodal Queries](#7.3).

**Sources:** [raganything/query.py:195-341](), [raganything/query.py:412-577](), [raganything/query.py:26-100]()

## VLM-Enhanced Queries

The `aquery_vlm_enhanced` method [raganything/query.py:343-410]() automatically detects image paths in retrieved context from LightRAG and processes them with the vision model. This enables the system to answer questions about images found within documents without explicit user input of the images.

### VLM Enhancement Architecture

```mermaid
flowchart TD
    Start["aquery_vlm_enhanced(query, mode, system_prompt)"]
    GetPrompt["Get retrieval prompt<br/>only_need_prompt=True<br/>(raganything/query.py:364)"]
    ExtractImages["Extract and validate image paths<br/>_process_image_paths_for_vlm()<br/>(raganything/query.py:579)"]
    
    subgraph Validation["Image Security Validation"]
        CheckExists["File exists?"]
        CheckSafety["In safe directory?<br/>(raganything/query.py:618)"]
        CheckSymlink["Not a symlink?"]
        Encode["encode_image_to_base64()"]
    end
    
    BuildMessages["Build VLM messages<br/>_build_vlm_messages_with_images()<br/>(raganything/query.py:698)"]
    CallVLM["Call vision_model_func<br/>_call_vlm_with_multimodal_content()<br/>(raganything/query.py:782)"]
    Return["Return result"]
    
    Start --> GetPrompt
    GetPrompt --> ExtractImages
    ExtractImages --> Validation
    Validation --> BuildMessages
    BuildMessages --> CallVLM
    CallVLM --> Return
```

For details, see [VLM-Enhanced Queries](#7.4).

**Sources:** [raganything/query.py:343-410](), [raganything/query.py:579-696](), [raganything/query.py:698-813]()

## Query Result Caching

Multimodal queries use MD5-based cache keys generated from normalized query parameters [raganything/query.py:26-100](). The cache is stored in LightRAG's `llm_response_cache` [raganything/query.py:263-338]().

### Cache Normalization
- **File Paths**: Reduced to basenames to ensure portability [raganything/query.py:60]().
- **Large Content**: Strings over 200 characters (like table bodies) are hashed [raganything/query.py:67-69]().
- **Parameters**: Includes `stream`, `top_k`, `temperature`, etc. [raganything/query.py:83-92]().

**Sources:** [raganything/query.py:26-100](), [raganything/query.py:263-338]()

## Synchronous Query Methods

The system provides synchronous wrappers for all async query methods using `always_get_an_event_loop()` [raganything/query.py:816-859]():

- `query()`: Synchronous version of `aquery` [raganything/query.py:816-832]().
- `query_with_multimodal()`: Synchronous version of `aquery_with_multimodal` [raganything/query.py:834-859]().

**Sources:** [raganything/query.py:816-859]()

---

# Page: Query Architecture

# Query Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [raganything/batch.py](raganything/batch.py)
- [raganything/query.py](raganything/query.py)
- [raganything/raganything.py](raganything/raganything.py)

</details>



This document describes the architectural design of RAG-Anything's query system, including the `QueryMixin` class structure, the three distinct query paths (text, VLM-enhanced, and multimodal), and the underlying retrieval modes. For detailed implementation and usage of specific query types, see [7.2 Text Queries](), [7.3 Multimodal Queries](), and [7.4 VLM-Enhanced Queries]().

## Overview

RAG-Anything's query architecture extends the LightRAG framework with sophisticated multimodal query capabilities. The system provides three distinct query paths that serve different use cases while sharing a common retrieval infrastructure. All query functionality is encapsulated in the `QueryMixin` class, which is composed into the main `RAGAnything` class.

Sources: [raganything/query.py:1-24](), [raganything/raganything.py:51-51]()

## QueryMixin Class Structure

The `QueryMixin` class provides the query interface for RAG-Anything and integrates with the LightRAG framework's retrieval system.

Title: QueryMixin Architecture
```mermaid
classDiagram
    class QueryMixin {
        +aquery(query, mode, system_prompt, **kwargs) str
        +aquery_with_multimodal(query, multimodal_content, mode, **kwargs) str
        +aquery_vlm_enhanced(query, mode, system_prompt, **kwargs) str
        +query(query, mode, **kwargs) str
        +query_with_multimodal(query, multimodal_content, mode, **kwargs) str
        -_process_multimodal_query_content(base_query, multimodal_content) str
        -_generate_multimodal_cache_key(query, multimodal_content, mode, **kwargs) str
        -_process_image_paths_for_vlm(prompt) tuple
        -_build_vlm_messages_with_images(enhanced_prompt, user_query, system_prompt) List
        -_call_vlm_with_multimodal_content(messages) str
        -_generate_query_content_description(processor, content, content_type) str
        -_describe_image_for_query(processor, content) str
        -_describe_table_for_query(processor, content) str
        -_describe_equation_for_query(processor, content) str
        -_describe_generic_for_query(processor, content, content_type) str
    }
    
    class RAGAnything {
        +lightrag: LightRAG
        +vision_model_func: callable
        +modal_processors: dict
        +logger: Logger
    }
    
    class LightRAG {
        +aquery(query, param) str
        +llm_model_func: callable
        +llm_response_cache: BaseStorage
    }
    
    class QueryParam {
        +mode: str
        +only_need_context: bool
        +only_need_prompt: bool
        +stream: bool
        +response_type: str
        +top_k: int
    }
    
    RAGAnything --|> QueryMixin : "inherits"
    RAGAnything --> LightRAG : "uses"
    QueryMixin --> LightRAG : "delegates to"
    QueryMixin --> QueryParam : "creates"
```

**Key Components:**

- **Public Query Methods**: Three async methods (`aquery`, `aquery_with_multimodal`, `aquery_vlm_enhanced`) and their synchronous wrappers [raganything/query.py:102-365]().
- **Content Processing**: Private methods for processing multimodal content and generating descriptions [raganything/query.py:367-531]().
- **VLM Integration**: Methods for image path extraction and VLM message formatting [raganything/query.py:533-692]().
- **Caching**: Multimodal query cache key generation and cache management [raganything/query.py:26-100]().

Sources: [raganything/query.py:23-770](), [raganything/raganything.py:51-107]()

## Three Query Paths

The query architecture provides three distinct paths, each optimized for different content types and use cases.

Title: Query Execution Logic
```mermaid
flowchart TD
    UserQuery["User Query"]
    TypeCheck{"Query Type?"}
    
    subgraph TextPath["Text Query Path"]
        TextQuery["aquery()"]
        VLMCheck{"VLM Enhanced?"}
        NormalQuery["LightRAG.aquery()"]
        VLMQuery["aquery_vlm_enhanced()"]
    end
    
    subgraph MultimodalPath["Multimodal Query Path"]
        MMQuery["aquery_with_multimodal()"]
        HasContent{"Has Multimodal Content?"}
        ProcessContent["_process_multimodal_query_content()"]
        GenerateDesc["Generate Descriptions via Modal Processors"]
        EnhancedQuery["Enhanced Query Text"]
        CacheCheck{"Cache Available?"}
        CacheHit["Return Cached Result"]
    end
    
    subgraph VLMPath["VLM Enhanced Path"]
        VLMEnh["aquery_vlm_enhanced()"]
        GetPrompt["LightRAG.aquery() with only_need_prompt=True"]
        ExtractImages["_process_image_paths_for_vlm()"]
        HasImages{"Valid Images Found?"}
        BuildMessages["_build_vlm_messages_with_images()"]
        CallVLM["_call_vlm_with_multimodal_content()"]
        FallbackNormal["Fallback to Normal Query"]
    end
    
    UserQuery --> TypeCheck
    TypeCheck -->|"Text Query"| TextQuery
    TypeCheck -->|"With Multimodal Content"| MMQuery
    TypeCheck -->|"VLM Enhanced"| VLMEnh
    
    TextQuery --> VLMCheck
    VLMCheck -->|"vlm_enhanced=True"| VLMQuery
    VLMCheck -->|"vlm_enhanced=False"| NormalQuery
    
    MMQuery --> HasContent
    HasContent -->|"Yes"| CacheCheck
    HasContent -->|"No"| TextQuery
    CacheCheck -->|"Hit"| CacheHit
    CacheCheck -->|"Miss"| ProcessContent
    ProcessContent --> GenerateDesc
    GenerateDesc --> EnhancedQuery
    EnhancedQuery --> TextQuery
    
    VLMEnh --> GetPrompt
    GetPrompt --> ExtractImages
    ExtractImages --> HasImages
    HasImages -->|"Yes"| BuildMessages
    HasImages -->|"No"| FallbackNormal
    BuildMessages --> CallVLM
    FallbackNormal --> NormalQuery
```

**Path 1: Text Queries (`aquery`)**
Pure text queries that directly leverage LightRAG's retrieval and generation capabilities [raganything/query.py:102-193](). When `vision_model_func` is available, this automatically routes to VLM-enhanced mode unless explicitly disabled [raganything/query.py:125-143]().

**Path 2: Multimodal Queries (`aquery_with_multimodal`)**
Accepts user-provided multimodal content (images, tables, equations) alongside the query text [raganything/query.py:195-302](). The system generates textual descriptions of the provided content and combines them with the query for enhanced retrieval [raganything/query.py:367-434]().

**Path 3: VLM-Enhanced Queries (`aquery_vlm_enhanced`)**
Automatically detects images in the retrieved context and integrates them directly with the VLM for visual understanding [raganything/query.py:303-365](). This path extracts image paths from LightRAG's retrieval results, encodes them as base64, and formats them in VLM-compatible message structures [raganything/query.py:533-692]().

Sources: [raganything/query.py:102-365]()

## Retrieval Modes

RAG-Anything inherits LightRAG's retrieval modes via the `QueryParam` class [raganything/query.py:162-162]().

| Mode | Description | Retrieval Strategy |
|------|-------------|-------------------|
| `hybrid` | Combines vector similarity and graph traversal | Vector DB + Graph DB |
| `local` | Context-focused retrieval using graph relationships | Graph DB (local context) |
| `global` | High-level overview using full knowledge graph | Graph DB (global view) |
| `naive` | Simple vector similarity search | Vector DB only |
| `mix` | Dynamically selects between local and global | Auto-selection |
| `bypass` | Skips retrieval, direct LLM query | No retrieval |

Sources: [raganything/query.py:103-110](), [raganything/query.py:162-162]()

## Multimodal Query Caching

RAG-Anything implements a specialized caching mechanism for multimodal queries to avoid redundant processing of complex content.

Title: Cache Key Generation Logic
```mermaid
flowchart TD
    QueryInput["Multimodal Query Input"]
    GenerateKey["_generate_multimodal_cache_key()"]
    
    subgraph KeyGen["Cache Key Generation Details"]
        NormalizeQuery["Normalize query text"]
        NormalizeContent["Normalize multimodal content"]
        HashPaths["Hash file paths to basename"]
        HashLarge["Hash large content > 200 chars"]
        CombineParams["Add mode and kwargs"]
        MD5Hash["Generate MD5 hash"]
    end
    
    CheckCache{"Cache Available?"}
    CacheHit{"Cache Hit?"}
    ProcessContent["Process multimodal content"]
    SaveCache["Save result to cache"]
    ReturnResult["Return result"]
    
    QueryInput --> GenerateKey
    GenerateKey --> NormalizeQuery
    NormalizeQuery --> NormalizeContent
    NormalizeContent --> HashPaths
    HashPaths --> HashLarge
    HashLarge --> CombineParams
    CombineParams --> MD5Hash
    
    MD5Hash --> CheckCache
    CheckCache -->|"Yes"| CacheHit
    CheckCache -->|"No"| ProcessContent
    CacheHit -->|"Yes"| ReturnResult
    CacheHit -->|"No"| ProcessContent
    ProcessContent --> SaveCache
    SaveCache --> ReturnResult
```

**Cache Key Components [raganything/query.py:26-100]():**
1. **Query Text**: Stripped and normalized.
2. **Mode**: Retrieval mode string.
3. **Multimodal Content**: 
   - File paths reduced to basenames for portability.
   - Large content (table bodies > 200 chars) replaced with MD5 hashes.
4. **Relevant kwargs**: `stream`, `response_type`, `top_k`, `max_tokens`, `temperature`, `system_prompt`.

The cache key is generated using the pattern: `multimodal_query:<md5_hash>`.

Sources: [raganything/query.py:26-100](), [raganything/query.py:217-230]()

## VLM Message Format

When processing VLM-enhanced queries, the system constructs messages in a format compatible with vision-language models.

Title: VLM Message Construction
```mermaid
flowchart LR
    subgraph Input["Input Components"]
        Prompt["Enhanced Prompt with [VLM_IMAGE_N] markers"]
        Images["Base64 Encoded Images"]
        UserQuery["Original User Query"]
        SysPrompt["System Prompt"]
    end
    
    subgraph Processing["_build_vlm_messages_with_images()"]
        Split["Split text at markers"]
        InsertImages["Insert images at marker positions"]
        AddQuestion["Append user question"]
    end
    
    subgraph Output["VLM Message Format"]
        SysMsg["System Message: role: system, content: prompt text"]
        UserMsg["User Message: role: user, content: array of parts"]
        
        subgraph ContentParts["Content Parts Array"]
            TextPart1["text part"]
            ImagePart1["image_url part"]
            TextPartN["user question"]
        end
    end
    
    Prompt --> Split
    Images --> InsertImages
    Split --> InsertImages
    InsertImages --> AddQuestion
    UserQuery --> AddQuestion
    
    AddQuestion --> UserMsg
    SysPrompt --> SysMsg
```

The system splits the prompt based on the `[VLM_IMAGE_N]` regex and intersperses text parts with base64 image objects [raganything/query.py:613-685]().

Sources: [raganything/query.py:609-692](), [raganything/query.py:533-607]()

## Error Handling and Fallbacks

The query system implements graceful degradation:

- **Missing LightRAG**: Raises `ValueError` if `self.lightrag` is `None` [raganything/query.py:120-123]().
- **Missing Vision Model**: If `vlm_enhanced` is requested but `vision_model_func` is absent, it logs a warning and falls back to a normal text query [raganything/query.py:144-149]().
- **VLM Image Validation**: Checks image existence and format before encoding [raganything/query.py:553-568](). If validation fails, it skips that specific image.
- **VLM Prompt Fallback**: If no valid images are extracted from the retrieved context, `aquery_vlm_enhanced` falls back to a standard `lightrag.aquery` call [raganything/query.py:345-351]().

Sources: [raganything/query.py:120-150](), [raganything/query.py:345-351](), [raganything/query.py:553-568]()

---

# Page: Text Queries

# Text Queries

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/raganything_example.py](examples/raganything_example.py)
- [raganything/batch.py](raganything/batch.py)
- [raganything/query.py](raganything/query.py)

</details>



## Purpose and Scope

This page documents the pure text query functionality in RAG-Anything, specifically the `aquery` and `query` methods provided by the `QueryMixin` class. Text queries are the primary mechanism for retrieving information from the knowledge base using natural language questions without explicitly providing multimodal content in the query.

Text queries directly leverage LightRAG's retrieval capabilities and support multiple query modes for different retrieval strategies. When a `vision_model_func` is provided, text queries can automatically upgrade to VLM-enhanced mode to process images found in the retrieved context.

---

## Query Methods Overview

The `QueryMixin` class provides two primary methods for text queries: an asynchronous version (`aquery`) and a synchronous wrapper (`query`).

### Code Entity Space: Query Flow

The following diagram illustrates how the natural language query is handled by the internal methods of the `QueryMixin` class.

```mermaid
graph TB
    UserQuery["User Text Query"]
    QueryMethod{Query Method}
    AQuery["QueryMixin.aquery()"]
    SyncQuery["QueryMixin.query()"]
    VLMCheck{"vlm_enhanced?"}
    VLMQuery["QueryMixin.aquery_vlm_enhanced()"]
    LightRAGQuery["lightrag.aquery()"]
    QueryParam["lightrag.QueryParam"]
    Result["Query Result"]
    
    UserQuery --> QueryMethod
    QueryMethod -->|"Async"| AQuery
    QueryMethod -->|"Sync"| SyncQuery
    SyncQuery -->|"always_get_an_event_loop()"| AQuery
    
    AQuery --> VLMCheck
    VLMCheck -->|"True & self.vision_model_func"| VLMQuery
    VLMCheck -->|"False or None"| QueryParam
    
    QueryParam --> LightRAGQuery
    LightRAGQuery --> Result
    VLMQuery --> Result
```

**Diagram: Text Query Method Flow**

Sources: [raganything/query.py:102-143](), [raganything/query.py:776-792]()

### aquery (Asynchronous)

The `aquery` method is the primary asynchronous text query interface. It manages the logic for determining whether to perform a standard RAG query or an enhanced VLM query.

**Method Signature:**
[raganything/query.py:102-104]()
```python
async def aquery(
    self, query: str, mode: str = "mix", system_prompt: str | None = None, **kwargs
) -> str:
```

**Parameters:**
- `query`: The query text (natural language question).
- `mode`: Query mode determining retrieval strategy (default: `"mix"`).
- `system_prompt`: Optional system prompt for LLM.
- `**kwargs`: Additional query parameters passed to `QueryParam`, including:
  - `vlm_enhanced`: Boolean to explicitly enable/disable VLM enhancement. If `None`, it is auto-detected based on `vision_model_func` availability. [raganything/query.py:126-133]()

**Returns:** Query result as a string.

Sources: [raganything/query.py:102-119]()

### query (Synchronous)

The `query` method is a synchronous wrapper around `aquery` for convenience, using `always_get_an_event_loop` to execute the coroutine. [raganything/query.py:776-792]()

---

## Query Modes

Text queries support multiple retrieval modes defined by the underlying LightRAG system. These modes determine the search strategy within the Knowledge Graph and Vector Databases.

| Mode | Description |
|------|-------------|
| `"local"` | Focuses on specific entities and their direct relationships. |
| `"global"` | Uses high-level community summaries for broad thematic understanding. |
| `"hybrid"` | Combines local and global retrieval strategies. |
| `"naive"` | Simple vector similarity search without graph traversal. |
| `"mix"` | Adaptive strategy that selects appropriate mode based on query. |
| `"bypass"` | Bypasses retrieval and directly uses the LLM. |

Sources: [raganything/query.py:110](), [examples/raganything_example.py:223-241]()

---

## VLM Enhancement Auto-Detection

RAG-Anything intelligently detects if it should use a Vision-Language Model (VLM) to interpret visual elements found in the retrieved context.

### Code Entity Space: Auto-Detection Logic

This diagram shows how the system bridges the "Vision Model" configuration to the "Query Pipeline".

```mermaid
flowchart TB
    Start["QueryMixin.aquery()"]
    CheckParam{"kwargs.pop('vlm_enhanced')"}
    
    ParamNull["vlm_enhanced is None"]
    ParamTrue["vlm_enhanced is True"]
    ParamFalse["vlm_enhanced is False"]
    
    DetectVLM{"hasattr(self, 'vision_model_func')?"}
    
    RunVLM["QueryMixin.aquery_vlm_enhanced()"]
    RunNormal["lightrag.aquery()"]
    
    Start --> CheckParam
    CheckParam --> ParamNull
    CheckParam --> ParamTrue
    CheckParam --> ParamFalse
    
    ParamNull --> DetectVLM
    ParamTrue --> DetectVLM
    ParamFalse --> RunNormal
    
    DetectVLM -->|"Yes"| RunVLM
    DetectVLM -->|"No"| RunNormal
```

**Diagram: VLM Enhancement Decision Flow**

**Behavior:**
1. **Auto-Detection**: If `vlm_enhanced` is not specified, it defaults to `True` if `self.vision_model_func` is present. [raganything/query.py:129-133]()
2. **Explicit Control**: Users can force disable VLM processing even if a model is available by passing `vlm_enhanced=False`. [raganything/query.py:126]()
3. **Fallback**: If VLM enhancement is requested but no `vision_model_func` is found, the system logs a warning and falls back to a normal text query. [raganything/query.py:144-149]()

Sources: [raganything/query.py:125-149]()

---

## Implementation and Data Flow

### Retrieval Pipeline

When a standard text query is executed, the following flow occurs:

1. **LightRAG Initialization**: Verifies `self.lightrag` is not `None`. [raganything/query.py:120-123]()
2. **Callback Dispatch**: Triggers `on_query_start` via the `callback_manager`. [raganything/query.py:151-159]()
3. **Parameter Packaging**: Constructs a `lightrag.QueryParam` object using the provided `mode` and `**kwargs`. [raganything/query.py:162]()
4. **Execution**: Calls `await self.lightrag.aquery()`. [raganything/query.py:169-171]()
5. **Completion**: Triggers `on_query_complete` with duration and result length statistics. [raganything/query.py:183-192]()

### Integration with Callbacks

The `QueryMixin` interacts with the `callback_manager` to provide observability into the query lifecycle.

| Event | Data Provided | Call Site |
|-------|---------------|-----------|
| `on_query_start` | `query`, `mode` | [raganything/query.py:155-159]() |
| `on_query_error` | `query`, `mode`, `error` | [raganything/query.py:173-179]() |
| `on_query_complete` | `query`, `mode`, `duration_seconds`, `result_length` | [raganything/query.py:186-192]() |

Sources: [raganything/query.py:151-193]()

---

## Usage Examples

### Basic Asynchronous Query

```python
# From examples/raganything_example.py
result = await rag.aquery(
    "What are the main findings in the research?",
    mode="hybrid"
)
```
Sources: [examples/raganything_example.py:231-234]()

### Query with Custom Parameters

Users can pass standard LightRAG parameters through `**kwargs` to the `aquery` method.

```python
result = await rag.aquery(
    "Explain the methodology",
    mode="local",
    top_k=5,
    max_tokens=1000,
    temperature=0.2
)
```
Sources: [raganything/query.py:102-113](), [raganything/query.py:162]()

### Forcing VLM Enhancement

If you want to ensure the system attempts to process images found in the retrieved context:

```python
result = await rag.aquery(
    "What is shown in Figure 1?",
    vlm_enhanced=True
)
```
Sources: [raganything/query.py:126-143]()

---

# Page: Multimodal Queries

# Multimodal Queries

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/raganything_example.py](examples/raganything_example.py)
- [raganything/batch.py](raganything/batch.py)
- [raganything/query.py](raganything/query.py)

</details>



## Purpose and Scope

This page describes the multimodal query functionality in RAG-Anything, specifically the `aquery_with_multimodal()` method that enables querying with both text and structured multimodal content such as tables, equations, and images. This functionality allows users to provide specific multimodal content alongside their queries for enhanced context-aware retrieval and generation.

**Scope:**
- Multimodal query execution via `aquery_with_multimodal()`
- Content injection and description generation
- Table, equation, and image query integration
- Query caching mechanism and normalization

**Related Pages:**
- For standard text-based queries, see [7.2 Text Queries]()
- For VLM-enhanced queries with automatic image processing, see [7.4 VLM-Enhanced Queries]()
- For the overall query architecture, see [7.1 Query Architecture]()

Sources: [raganything/query.py:1-24](), [raganything/query.py:195-205]()

---

## Overview

Multimodal queries in RAG-Anything extend standard text queries by allowing users to inject specific multimodal content (tables, equations, images) directly into the query context. Unlike VLM-enhanced queries that automatically process images found in retrieved documents, multimodal queries are designed for scenarios where the user wants to explicitly provide specific content for analysis.

The system processes this content through specialized modal processors to generate rich descriptions, then combines these descriptions with the user's query to create an enhanced query that is executed against the knowledge base.

**Key Characteristics:**
- **Explicit Content Injection**: User provides specific multimodal content to analyze.
- **Type-Aware Processing**: Different content types (table, equation, image) are processed by their respective specialized processors.
- **Query Enhancement**: Multimodal content is transformed into descriptive text that enriches the base query.
- **Caching Support**: Enhanced queries and their results are cached using a normalized hashing strategy.

Sources: [raganything/query.py:195-210](), [raganything/query.py:372-385]()

---

## Query Execution Flow

**Diagram: Multimodal Query Execution Pipeline**
```mermaid
flowchart TD
    UserQuery["User: query + multimodal_content"]
    EntryPoint["QueryMixin.aquery_with_multimodal()"]
    CheckCache["_generate_multimodal_cache_key()<br/>normalize & MD5 hash"]
    CacheHit{"llm_response_cache<br/>.get_by_id()"}
    ReturnCached["Return cached result"]
    
    ProcessContent["_process_multimodal_query_content()"]
    GetProc["get_processor_for_type()<br/>from self.modal_processors"]
    
    ImageProc["_describe_image_for_query()"]
    TableProc["_describe_table_for_query()"]
    EqProc["_describe_equation_for_query()"]
    GenericProc["_describe_generic_for_query()"]
    
    EnhanceQuery["Build enhanced_query:<br/>base + descriptions + suffix"]
    ExecuteQuery["QueryMixin.aquery()<br/>LightRAG query"]
    SaveCache["llm_response_cache.upsert()<br/>+ index_done_callback()"]
    Return["Return result"]
    
    UserQuery --> EntryPoint
    EntryPoint --> CheckCache
    CheckCache --> CacheHit
    CacheHit -->|"Hit"| ReturnCached
    CacheHit -->|"Miss"| ProcessContent
    
    ProcessContent --> GetProc
    GetProc -->|"type == image"| ImageProc
    GetProc -->|"type == table"| TableProc
    GetProc -->|"type == equation"| EqProc
    GetProc -->|"else"| GenericProc
    
    ImageProc --> EnhanceQuery
    TableProc --> EnhanceQuery
    EqProc --> EnhanceQuery
    GenericProc --> EnhanceQuery
    
    EnhanceQuery --> ExecuteQuery
    ExecuteQuery --> SaveCache
    SaveCache --> Return
```

**Query Flow Stages:**

1. **Cache Check**: `_generate_multimodal_cache_key()` [raganything/query.py:26-40]() generates a normalized key and checks `self.lightrag.llm_response_cache` [raganything/query.py:223-233]().
2. **Content Processing**: `_process_multimodal_query_content()` [raganything/query.py:372-423]() routes each multimodal item via `get_processor_for_type()` [raganything/utils.py:228-248]().
3. **Description Generation**: Generates rich textual descriptions using processor-specific methods like `_describe_image_for_query()` [raganything/query.py:455-484]().
4. **Query Enhancement**: Combines descriptions with the user query and `PROMPTS["QUERY_ENHANCEMENT_SUFFIX"]` [raganything/query.py:419-420]().
5. **Query Execution**: Executes the enhanced query using the standard `aquery()` path [raganything/query.py:257]().
6. **Cache Storage**: Saves result to `llm_response_cache` and triggers `index_done_callback()` for persistence [raganything/query.py:288-298]().

Sources: [raganything/query.py:26-100](), [raganything/query.py:217-298](), [raganything/query.py:372-423]()

---

## Content Injection Mechanism

### Query Method Signature

The primary entry point is `QueryMixin.aquery_with_multimodal()` defined in [raganything/query.py:195-205]():

```python
async def aquery_with_multimodal(
    self,
    query: str,
    multimodal_content: List[Dict[str, Any]] = None,
    mode: str = "mix",
    system_prompt: str | None = None,
    **kwargs,
) -> str
```

**Parameters:**
- `query`: Base query text provided by the user.
- `multimodal_content`: List of dictionaries containing `type` and content data.
- `mode`: Query mode (e.g., `"local"`, `"global"`, `"hybrid"`, `"naive"`, `"mix"`, `"bypass"`) [raganything/query.py:199]().
- `**kwargs`: Additional parameters forwarded to `QueryParam` (e.g., `top_k`, `max_tokens`).

**Fallback Behavior**: If `multimodal_content` is `None` or empty, the method automatically delegates to `aquery()` for standard text query processing [raganything/query.py:212-215]().

Sources: [raganything/query.py:195-215]()

---

### Multimodal Content Format

Each item in the `multimodal_content` list must be a dictionary with a `type` field and type-specific fields:

| Content Type | Required Fields | Optional Fields | Processing Method |
|-------------|----------------|-----------------|-------------------|
| `image` | `type`, `img_path` | `image_caption`, `image_footnote` | `_describe_image_for_query()` |
| `table` | `type`, `table_data` | `table_caption` | `_describe_table_for_query()` |
| `equation` | `type`, `latex` | `equation_caption` | `_describe_equation_for_query()` |
| Generic | `type` | Any custom fields | `_describe_generic_for_query()` |

**Content Routing**: The `type` field determines which processor is selected via `get_processor_for_type()` in [raganything/utils.py:228-248](), which maps types to instances in `self.modal_processors`.

Sources: [raganything/query.py:198-204](), [raganything/utils.py:228-248]()

---

## Content Description Generation

### Type-Based Routing

**Diagram: Content Type to Processor Routing**
```mermaid
graph TB
    ContentItem["content_item dict<br/>with 'type' field"]
    ProcessLoop["_process_multimodal_query_content()"]
    GetProc["utils.get_processor_for_type()<br/>self.modal_processors"]
    
    ImgCheck{"type == 'image'"}
    TblCheck{"type == 'table'"}
    EqCheck{"type == 'equation'"}
    
    ImageProc["self.modal_processors['image']<br/>ImageModalProcessor"]
    TableProc["self.modal_processors['table']<br/>TableModalProcessor"]
    EqProc["self.modal_processors['equation']<br/>EquationModalProcessor"]
    GenericProc["self.modal_processors['generic']<br/>GenericModalProcessor"]
    
    GenDesc["_generate_query_content_description()"]
    
    ContentItem --> ProcessLoop
    ProcessLoop --> GetProc
    GetProc --> ImgCheck
    ImgCheck -->|"Yes"| ImageProc
    ImgCheck -->|"No"| TblCheck
    TblCheck -->|"Yes"| TableProc
    TblCheck -->|"No"| EqCheck
    EqCheck -->|"Yes"| EqProc
    EqCheck -->|"No"| GenericProc
    
    ImageProc --> GenDesc
    TableProc --> GenDesc
    EqProc --> GenDesc
    GenericProc --> GenDesc
```

The routing logic iterates through `multimodal_content` and fetches the processor instance [raganything/query.py:389-402](). If a processor is found, it calls `_generate_query_content_description()` [raganything/query.py:404-407]().

Sources: [raganything/query.py:372-423](), [raganything/utils.py:228-248]()

---

### Image Description Generation

The `_describe_image_for_query()` method in [raganything/query.py:455-484]() processes image content:

**Processing Flow:**
1. **Extract Metadata**: Extracts `img_path`, `image_caption`, and `image_footnote` [raganything/query.py:459-461]().
2. **Path Validation**: Checks if the file exists [raganything/query.py:463]().
3. **Base64 Encoding**: Encodes the image via `encode_image_to_base64()` [raganything/query.py:465]().
4. **VLM Analysis**: Calls `processor.modal_caption_func` with `PROMPTS["QUERY_IMAGE_DESCRIPTION"]` and `PROMPTS["QUERY_IMAGE_ANALYST_SYSTEM"]` [raganything/query.py:466-472]().
5. **Metadata Fallback**: If processing fails or image is missing, it constructs a description from available text metadata [raganything/query.py:476-484]().

Sources: [raganything/query.py:455-484](), [raganything/utils.py:281-300]()

---

### Table Description Generation

The `_describe_table_for_query()` method in [raganything/query.py:486-501]() analyzes table content:

**Processing Steps:**
1. **Extract Table Data**: Gets `table_data` (Markdown/CSV) and `table_caption` [raganything/query.py:490-491]().
2. **Build Analysis Prompt**: Formats `PROMPTS["QUERY_TABLE_ANALYSIS"]` with the data [raganything/query.py:493-495]().
3. **LLM Analysis**: Sends to `modal_caption_func()` with `PROMPTS["QUERY_TABLE_ANALYST_SYSTEM"]` [raganything/query.py:497-499]().

Sources: [raganything/query.py:486-501]()

---

### Equation Description Generation

The `_describe_equation_for_query()` method in [raganything/query.py:503-518]() interprets mathematical equations:

**Processing Steps:**
1. **Extract LaTeX**: Gets `latex` formula and `equation_caption` [raganything/query.py:507-508]().
2. **Build Analysis Prompt**: Formats `PROMPTS["QUERY_EQUATION_ANALYSIS"]` [raganything/query.py:510-512]().
3. **LLM Analysis**: Generates interpretation via `modal_caption_func()` using `PROMPTS["QUERY_EQUATION_ANALYST_SYSTEM"]` [raganything/query.py:514-516]().

Sources: [raganything/query.py:503-518]()

---

### Generic Content Description

The `_describe_generic_for_query()` method in [raganything/query.py:520-537]() handles custom content types by serializing the dictionary to a string [raganything/query.py:524]() and prompting the LLM to analyze it based on the `content_type` [raganything/query.py:526-535]().

Sources: [raganything/query.py:520-537]()

---

## Caching System

### Cache Key Generation

**Diagram: Cache Key Generation Process**
```mermaid
graph TD
    Params["query, multimodal_content,<br/>mode, kwargs"]
    Method["_generate_multimodal_cache_key()"]
    
    NormQuery["Normalize query.strip()"]
    NormMode["Include mode"]
    NormContent["Normalize multimodal_content"]
    NormKwargs["Filter relevant kwargs"]
    
    BasenameRule["File paths → basename only"]
    HashRule["Large content → MD5 hash"]
    
    CacheData["cache_data dict"]
    JSON["json.dumps() with sort_keys"]
    MD5["hashlib.md5()"]
    CacheKey["'multimodal_query:' + hash"]
    
    Params --> Method
    Method --> NormQuery
    Method --> NormMode
    Method --> NormContent
    Method --> NormKwargs
    
    NormContent --> BasenameRule
    NormContent --> HashRule
    
    NormQuery --> CacheData
    NormMode --> CacheData
    BasenameRule --> CacheData
    HashRule --> CacheData
    NormKwargs --> CacheData
    
    CacheData --> JSON
    JSON --> MD5
    MD5 --> CacheKey
```

The `_generate_multimodal_cache_key()` method in [raganything/query.py:26-100]() ensures stability:
- **Path Normalization**: Uses `Path(value).name` for file paths to keep keys portable [raganything/query.py:60]().
- **Content Hashing**: Hashes `table_data` or `table_body` if length exceeds 200 characters [raganything/query.py:61-69]().
- **Kwarg Filtering**: Only includes relevant parameters like `top_k` and `temperature` in the hash [raganything/query.py:79-94]().

Sources: [raganything/query.py:26-100]()

---

## Usage Examples

### Example: Multimodal Query with Table and Equation

This example demonstrates how to pass explicit structured data to the query system.

```python
from raganything import RAGAnything

async def run_query(rag: RAGAnything):
    result = await rag.aquery_with_multimodal(
        query="Compare the performance metrics in this table with the theoretical formula.",
        multimodal_content=[
            {
                "type": "table",
                "table_data": "Method,Accuracy\nRAGAnything,95.2%\nBaseline,87.3%",
                "table_caption": "Empirical Results"
            },
            {
                "type": "equation",
                "latex": "Acc = \\frac{TP + TN}{Total}",
                "equation_caption": "Accuracy Definition"
            }
        ],
        mode="hybrid"
    )
    print(result)
```

Sources: [examples/raganything_example.py:228-261]()

---

## Synchronous API

For non-async environments, `QueryMixin` provides a synchronous wrapper `query_with_multimodal()` [raganything/query.py:794-818]():

```python
def query_with_multimodal(self, query: str, multimodal_content: List[Dict[str, Any]] = None, 
                          mode: str = "mix", **kwargs) -> str:
    loop = always_get_an_event_loop()
    return loop.run_until_complete(
        self.aquery_with_multimodal(query, multimodal_content, mode=mode, **kwargs)
    )
```

This uses `lightrag.utils.always_get_an_event_loop` to manage execution [raganything/query.py:815-817]().

Sources: [raganything/query.py:794-818]()

---

# Page: VLM-Enhanced Queries

# VLM-Enhanced Queries

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/multimodal_rag_failure_modes.md](docs/multimodal_rag_failure_modes.md)
- [raganything/asset_urls.py](raganything/asset_urls.py)
- [raganything/batch.py](raganything/batch.py)
- [raganything/query.py](raganything/query.py)
- [tests/test_asset_urls.py](tests/test_asset_urls.py)

</details>



## Purpose and Scope

This page documents the VLM-Enhanced Query feature in RAG-Anything, implemented primarily within the `QueryMixin` class. This capability allows the system to automatically process visual information retrieved during the RAG process by identifying image markers in the context, validating their paths, and reconstructing a multimodal prompt for a Vision-Language Model (VLM).

VLM-Enhanced Queries differ from:
- **Text queries**: which ignore visual markers in retrieved context [raganything/query.py:102-119]().
- **Explicit multimodal queries**: which require the user to provide new images at query time [raganything/query.py:195-202]().

---

## Overview

VLM-Enhanced Queries bridge the gap between structured document ingestion and multimodal reasoning. During ingestion, images are saved to disk and their paths are stored in the knowledge graph. During retrieval, if these paths appear in the context, the system automatically fetches the files, encodes them, and invokes the VLM.

```mermaid
graph TB
    subgraph "QueryMixin.aquery"
        UserQuery["User Query"] --> CheckVLM{"vision_model_func<br/>exists?"}
        CheckVLM -- "Yes" --> VLMEnhanced["aquery_vlm_enhanced()"]
        CheckVLM -- "No" --> NormalQuery["Normal Text Query"]
    end

    subgraph "QueryMixin.aquery_vlm_enhanced"
        VLMEnhanced --> Retrieval["LightRAG Retrieval<br/>(mode=mix/local/etc)"]
        Retrieval --> Context["Retrieved Context String"]
        Context --> Extract["Extract VLM_IMAGE_ markers<br/>(re.findall)"]
        Extract --> Validate["Path Validation<br/>(is_path_safe)"]
        Validate --> Encode["Base64 Encoding<br/>(encode_image_to_base64)"]
        Encode --> VLMCall["vision_model_func<br/>(messages=[...])"]
    end

    style VLMEnhanced fill:#f9f9f9
    style VLMCall fill:#f9f9f9
```
**VLM-Enhanced Query Data Flow**

Sources: [raganything/query.py:102-143](), [raganything/query.py:276-340]()

---

## System Components and Implementation

### The QueryMixin Class
The `QueryMixin` class provides the core logic for routing queries. It checks if `vision_model_func` is available and whether the user has requested `vlm_enhanced` mode [raganything/query.py:126-143]().

### Image Marker Reconstruction
When documents are parsed, images are represented in the text as specific markers. `aquery_vlm_enhanced` uses a regular expression `VLM_IMAGE_([^\s\n]+)` to find these markers in the retrieved text [raganything/query.py:302-303]().

### Path Validation and Security
To prevent arbitrary file access, the system validates extracted paths:
1.  **Safety Check**: The `is_path_safe` utility ensures the image resides within the configured `working_dir` or `parser_output_dir` [raganything/query.py:311-315]().
2.  **Existence Check**: It verifies the file physically exists on the disk before attempting to read it [raganything/query.py:316-318]().

### Base64 Encoding
Images are converted to base64 strings using `encode_image_to_base64` from `raganything.utils` to be compatible with standard VLM API message formats [raganything/query.py:321-322]().

Sources: [raganything/query.py:23-24](), [raganything/query.py:276-340](), [raganything/utils.py:114-129]()

---

## Vision Model Function Architecture

The `vision_model_func` is a flexible interface that handles both ingestion-time captioning and query-time reasoning.

### Invocation Patterns
The system uses the `messages` parameter pattern for VLM-enhanced queries, allowing for a mix of multiple images and retrieved text.

```mermaid
classDiagram
    class RAGAnything {
        +llm_model_func
        +vision_model_func
        +aquery(query, vlm_enhanced)
        +aquery_vlm_enhanced(query)
    }
    class QueryMixin {
        +aquery_vlm_enhanced()
    }
    class VisionModelFunc {
        <<interface>>
        +call(prompt, image_data, messages)
    }
    RAGAnything --|> QueryMixin
    RAGAnything --> VisionModelFunc : executes
```
**Association between Query Logic and Model Execution**

| Parameter | Type | Usage in VLM-Enhanced Query |
| :--- | :--- | :--- |
| `messages` | `List[Dict]` | Contains the full conversation history including base64 images [raganything/query.py:333-340](). |
| `prompt` | `str` | The original user query, often embedded in the last user message [raganything/query.py:330](). |
| `system_prompt` | `str` | Optional instructions for the VLM [raganything/query.py:326](). |

Sources: [raganything/query.py:131-143](), [raganything/query.py:333-340]()

---

## Query Processing Workflow

### Decision Logic
The `aquery` method automatically determines whether to use VLM enhancement based on the presence of `vision_model_func` [raganything/query.py:129-133]().

```mermaid
flowchart TD
    Start["aquery(query)"] --> HasVLM{"hasattr(self, 'vision_model_func')?"}
    HasVLM -- "No" --> TextOnly["Standard Text Query"]
    HasVLM -- "Yes" --> ParamCheck{"vlm_enhanced param?"}
    ParamCheck -- "False" --> TextOnly
    ParamCheck -- "True/None" --> VLME["aquery_vlm_enhanced()"]
    
    VLME --> Retrieve["Retrieve Context via LightRAG"]
    Retrieve --> Scan["Scan for 'VLM_IMAGE_...'"]
    Scan --> Found{"Images Found?"}
    Found -- "No" --> Fallback["Log warning & return text-only"]
    Found -- "Yes" --> Build["Build Multimodal Messages"]
    Build --> Invoke["Invoke VLM"]
```
**Decision Logic for VLM Enhancement**

Sources: [raganything/query.py:126-150](), [raganything/query.py:276-305]()

---

## Configuration and Environment

### Public URL Mapping
While VLM-enhanced queries typically use local paths for processing, the system supports mapping these to public URLs for UI display via `attach_public_media_urls` [raganything/asset_urls.py:65-76](). This is controlled by:
- `RAGANYTHING_PUBLIC_ASSET_BASE_URL` [raganything/asset_urls.py:77]()
- `RAGANYTHING_PUBLIC_ASSET_STRIP_PREFIX` [raganything/asset_urls.py:78]()

### Safe Directories
Path validation in `aquery_vlm_enhanced` relies on the configuration's directory settings to prevent path traversal attacks [raganything/query.py:311-315]().

Sources: [raganything/asset_urls.py:1-12](), [raganything/query.py:311-318]()

---

## Usage Examples

### Enabling VLM-Enhanced Queries
Users simply need to provide a `vision_model_func` during initialization. The system handles the rest during `aquery`.

```python
# The system automatically detects if VLM enhancement is possible
result = await rag.aquery(
    "Explain the diagram on page 5", 
    mode="hybrid"
)
```

### Manual Control
You can explicitly disable the feature even if a VLM is configured.

```python
# Force text-only retrieval even if images are present
result = await rag.aquery(
    "Summarize the text only", 
    vlm_enhanced=False
)
```

Sources: [raganything/query.py:102-116](), [raganything/query.py:126-133]()

---

# Page: Configuration

# Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [env.example](env.example)
- [examples/lmstudio_integration_example.py](examples/lmstudio_integration_example.py)
- [raganything/config.py](raganything/config.py)

</details>



This page provides a comprehensive guide to configuring RAG-Anything, covering configuration sources, the `RAGAnythingConfig` class, environment variables, storage backends, and model providers. Configuration determines system behavior including parser selection, multimodal processing capabilities, context extraction parameters, storage backends, and external service integration.

For installation and setup procedures, see [Installation](#2.1). For environment-specific setup steps, see [Environment Configuration](#2.3). For advanced deployment scenarios, see [Offline Deployment](#11.1).

## Configuration Architecture

RAG-Anything uses a two-tier configuration system: environment variables loaded from `.env` files and programmatic configuration via the `RAGAnythingConfig` class. Environment variables provide deployment-level configuration (API keys, storage credentials, server settings), while `RAGAnythingConfig` provides document processing configuration (parser settings, multimodal processing, context extraction).

**Configuration Architecture Flow**

```mermaid
flowchart TB
    subgraph ConfigSources["Configuration Sources"]
        ENV_FILE[".env File"]
        OS_ENV["OS Environment Variables"]
        CODE_CONFIG["RAGAnythingConfig instance"]
    end
    
    subgraph LoadingProcess["Loading Process"]
        DOTENV["load_dotenv()"]
        ENV_VAL["get_env_value()"]
    end
    
    subgraph RAGInit["RAGAnything Class"]
        direction TB
        CONFIG_INIT["self.config = config or RAGAnythingConfig()"]
        POST_INIT["__post_init__()"]
        LIGHTRAG_KW["self.lightrag_kwargs"]
    end
    
    subgraph ComponentSetup["Component Configuration"]
        PARSER_SELECT["self.parser: Parser"]
        PROCESSOR_INIT["_initialize_processors()"]
        CONTEXT_CONFIG["_create_context_config()"]
        LIGHTRAG_INIT["_ensure_lightrag_initialized()"]
    end
    
    ENV_FILE --> DOTENV
    OS_ENV --> ENV_VAL
    DOTENV --> ENV_VAL
    ENV_VAL --> CONFIG_INIT
    CODE_CONFIG --> CONFIG_INIT
    
    CONFIG_INIT --> POST_INIT
    POST_INIT --> PARSER_SELECT
    POST_INIT --> PROCESSOR_INIT
    POST_INIT --> CONTEXT_CONFIG
    
    LIGHTRAG_KW --> LIGHTRAG_INIT
    ENV_VAL -.influences.-> LIGHTRAG_INIT
```

**Sources:** [raganything/raganything.py:22-135](), [raganything/config.py:1-159](), [env.example:1-212]()

### Configuration Loading Order

The configuration loading follows a specific precedence order:

1.  **Environment variables** are loaded first via `load_dotenv()` with `override=False` at [raganything/raganything.py:25](). This ensures OS-level environment variables take precedence over `.env` file values.
2.  **RAGAnythingConfig initialization** occurs. If no config is provided, a new instance is created at [raganything/raganything.py:102-103]() which reads from environment variables via the `get_env_value()` helper function at [raganything/config.py:9]().
3.  **Component-specific configuration** happens during initialization:
    *   Parser selection at [raganything/raganything.py:112-114]().
    *   Working directory setup at [raganything/raganything.py:106]().
    *   Multimodal processor configuration at [raganything/raganything.py:177-220]().
4.  **LightRAG configuration** merges user-provided `lightrag_kwargs` with defaults at [raganything/raganything.py:320-327]().

**Sources:** [raganything/raganything.py:22-135](), [raganything/config.py:8-159]()

## Configuration Sources

RAG-Anything supports multiple configuration methods that can be combined:

**Configuration Methods and Effects**

```mermaid
graph LR
    subgraph Methods["Configuration Methods"]
        METHOD1["Environment Variables"]
        METHOD2["RAGAnythingConfig Class"]
        METHOD3["lightrag_kwargs Dict"]
        METHOD4["update_config() Method"]
    end
    
    subgraph Instance["RAGAnything Instance"]
        CONFIG_OBJ["self.config: RAGAnythingConfig"]
        LIGHTRAG_KW["self.lightrag_kwargs: Dict"]
        UPDATE_METHOD["update_config()"]
    end
    
    subgraph Effects["System Components"]
        PARSER["self.parser: Parser"]
        MODAL["Modal Processors"]
        CONTEXT["ContextExtractor"]
        STORAGE["Storage Backends"]
    end
    
    METHOD1 --> CONFIG_OBJ
    METHOD2 --> CONFIG_OBJ
    METHOD3 --> LIGHTRAG_KW
    METHOD4 --> UPDATE_METHOD
    
    CONFIG_OBJ --> PARSER
    CONFIG_OBJ --> MODAL
    CONFIG_OBJ --> CONTEXT
    LIGHTRAG_KW --> STORAGE
    UPDATE_METHOD --> CONFIG_OBJ
```

### Environment Variables (.env)

Environment variables are defined in a `.env` file following the template in `env.example`. The file is loaded at [raganything/raganything.py:25]() before any imports, which is critical for `TIKTOKEN_CACHE_DIR` to work in offline environments.

**Key characteristics:**
*   Loaded with `override=False` - OS environment takes precedence.
*   Affects both RAGAnything and LightRAG configuration.
*   Required for service credentials (API keys, database passwords).
*   Optional for RAGAnything-specific settings (defaults provided in `RAGAnythingConfig`).

### RAGAnythingConfig Class

The `RAGAnythingConfig` dataclass (defined at [raganything/config.py:13]()) provides programmatic configuration. When instantiated without parameters, it reads from environment variables. When provided explicitly to `RAGAnything.__init__()`, it overrides environment-based defaults.

**Initialization pattern:**
```python
# Method 1: Use environment variables
config = RAGAnythingConfig()  # Reads from environment via get_env_value

# Method 2: Override programmatically
config = RAGAnythingConfig(
    parser="mineru",
    parse_method="auto",
    enable_image_processing=True
)

rag = RAGAnything(config=config, ...)
```

Referenced at [raganything/raganything.py:67-68]() and initialized at [raganything/raganything.py:102-103]().

### lightrag_kwargs Dictionary

The `lightrag_kwargs` parameter provides direct passthrough to LightRAG initialization. This allows configuring storage backends, chunking parameters, and LightRAG-specific settings without modifying RAGAnything configuration.

**Usage pattern:**
```python
rag = RAGAnything(
    config=my_config,
    lightrag_kwargs={
        "kv_storage": "PGKVStorage",
        "vector_storage": "MilvusVectorStorage",
        "chunk_token_size": 1200,
        "max_parallel_insert": 2
    }
)
```

Documented at [raganything/raganything.py:72-83](), merged at [raganything/raganything.py:320-327]().

**Sources:** [raganything/raganything.py:67-83](), [raganything/raganything.py:222-229](), [env.example:1-212]()

## RAGAnythingConfig Fields

The `RAGAnythingConfig` dataclass contains all document processing configuration. Each field is populated via `get_env_value()` from environment variables or uses the specified default.

### Directory and Parser Configuration

| Field | Type | Default | Environment Variable | Line Reference |
| :--- | :--- | :--- | :--- | :--- |
| `working_dir` | `str` | `"./rag_storage"` | `WORKING_DIR` | [raganything/config.py:18]() |
| `parser_output_dir` | `str` | `"./output"` | `OUTPUT_DIR` | [raganything/config.py:26]() |
| `parser` | `str` | `"mineru"` | `PARSER` | [raganything/config.py:29]() |
| `parse_method` | `str` | `"auto"` | `PARSE_METHOD` | [raganything/config.py:23]() |

**Note:** `MINERU_PARSE_METHOD` is supported for backward compatibility but deprecated in favor of `PARSE_METHOD` at [raganything/config.py:120-130]().

### Multimodal and Batch Processing

| Field | Type | Default | Environment Variable | Line Reference |
| :--- | :--- | :--- | :--- | :--- |
| `enable_image_processing` | `bool` | `True` | `ENABLE_IMAGE_PROCESSING` | [raganything/config.py:39-41]() |
| `enable_table_processing` | `bool` | `True` | `ENABLE_TABLE_PROCESSING` | [raganything/config.py:44-46]() |
| `enable_equation_processing` | `bool` | `True` | `ENABLE_EQUATION_PROCESSING` | [raganything/config.py:49-52]() |
| `max_concurrent_files` | `int` | `1` | `MAX_CONCURRENT_FILES` | [raganything/config.py:56-58]() |
| `supported_file_extensions` | `List[str]` | (Standard extensions) | `SUPPORTED_FILE_EXTENSIONS` | [raganything/config.py:61-71]() |

### Context Extraction Configuration

| Field | Type | Default | Environment Variable | Line Reference |
| :--- | :--- | :--- | :--- | :--- |
| `context_window` | `int` | `1` | `CONTEXT_WINDOW` | [raganything/config.py:80]() |
| `context_mode` | `str` | `"page"` | `CONTEXT_MODE` | [raganything/config.py:83]() |
| `max_context_tokens` | `int` | `2000` | `MAX_CONTEXT_TOKENS` | [raganything/config.py:86-88]() |
| `include_headers` | `bool` | `True` | `INCLUDE_HEADERS` | [raganything/config.py:91]() |
| `include_captions` | `bool` | `True` | `INCLUDE_CAPTIONS` | [raganything/config.py:94-96]() |

**Sources:** [raganything/config.py:13-159](), [env.example:40-66]()

## Environment Variable Reference

For a complete reference, see [Environment Variables](#8.2). Key categories include:

*   **Server Configuration:** `HOST`, `PORT`, `WEBUI_TITLE`, `WEBUI_DESCRIPTION` ([env.example:5-8]()).
*   **Authentication:** `AUTH_ACCOUNTS`, `TOKEN_SECRET`, `LIGHTRAG_API_KEY` ([env.example:20-27]()).
*   **Offline Deployment:** `TIKTOKEN_CACHE_DIR` at [env.example:17]().
*   **Processing Pipeline:** `CHUNK_SIZE`, `CHUNK_OVERLAP_SIZE`, `MAX_PARALLEL_INSERT` ([env.example:100-103]()).
*   **LLM/Embedding:** `LLM_BINDING`, `LLM_MODEL`, `EMBEDDING_BINDING`, `EMBEDDING_MODEL` ([env.example:113-141]()).

## Storage Backend Configuration

RAG-Anything supports multiple storage backends through LightRAG. These are configured via environment variables and passed through `lightrag_kwargs`. For detailed setup, see [Storage Backend Configuration](#8.3).

**Supported Backends:**
*   **PostgreSQL:** All-in-one storage for KV, Vector, Graph, and DocStatus ([env.example:168-173]()).
*   **Neo4j:** Native graph storage ([env.example:178-180]()).
*   **Milvus/Qdrant:** Specialized vector storage ([env.example:200-207]()).
*   **MongoDB:** Document-based storage ([env.example:194-195]()).
*   **Redis:** High-speed KV caching ([env.example:211]()).

## Model Provider Configuration

RAG-Anything supports various model providers for both LLM and embedding tasks. For detailed configuration signatures, see [Model Provider Configuration](#8.4).

**Integration Examples:**
*   **OpenAI:** Standard cloud models ([env.example:113-122]()).
*   **Ollama:** Local model serving ([env.example:136-141]()).
*   **Azure OpenAI:** Enterprise-grade deployments ([env.example:124-125]()).
*   **LM Studio / vLLM:** High-performance local inference ([env.example:129-132](), [examples/lmstudio_integration_example.py:14-21]()).

**Sources:** [env.example:113-211](), [examples/lmstudio_integration_example.py:14-21]()

---

# Page: RAGAnythingConfig

# RAGAnythingConfig

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [raganything/config.py](raganything/config.py)

</details>



## Purpose and Scope

`RAGAnythingConfig` is the centralized configuration class for the RAG-Anything system. It defines all operational parameters for document parsing, multimodal content analysis, batch processing, and context extraction. This class is implemented as a dataclass with built-in environment variable support, serving as the single source of truth for system configuration.

This page documents the configuration parameters, their defaults, and their mapping to environment variables. For information about:
- Overall system architecture and components, see [System Architecture](#3)
- Configuration of storage backends, see [Storage Backend Configuration](#8.3)
- Configuration of AI model providers, see [Model Provider Configuration](#8.4)
- Environment variables reference, see [Environment Variables](#8.2)

## Configuration Architecture

The following diagram illustrates how `RAGAnythingConfig` integrates with the RAG-Anything system components.

### System Configuration Flow
```mermaid
graph TB
    subgraph "Configuration Sources"
        ENV["Environment Variables<br/>(via get_env_value)"]
        CODE["Programmatic Configuration<br/>(RAGAnythingConfig constructor)"]
    end
    
    subgraph "Configuration Object"
        CONFIG["RAGAnythingConfig Instance<br/>raganything/config.py"]
    end
    
    subgraph "RAGAnything System"
        RA["RAGAnything Instance<br/>raganything/raganything.py"]
        PARSER["Parser Registry<br/>(mineru, docling, paddleocr)"]
        PROC["ProcessorMixin<br/>(Document Processing)"]
        MODAL["Modal Processors<br/>(Image/Table/Equation)"]
        BATCH["BatchMixin<br/>(Concurrent Processing)"]
        CTX["ContextExtractor<br/>(Context Extraction)"]
    end
    
    ENV -->|defaults| CONFIG
    CODE -->|initialization| CONFIG
    
    CONFIG -->|self.config| RA
    
    RA -->|config.parser| PARSER
    RA -->|config.parse_method| PROC
    RA -->|config.enable_image_processing| MODAL
    RA -->|config.max_concurrent_files| BATCH
    RA -->|config.context_window| CTX
```

**Sources:** [raganything/config.py:12-116](), [raganything/raganything.py:99-135]()

## Configuration Initialization

`RAGAnythingConfig` is initialized in the `RAGAnything.__post_init__` method. If no configuration object is provided during `RAGAnything` instantiation, a default instance is created which automatically pulls values from the environment.

### Code Entity Space: Configuration Mapping
```mermaid
graph LR
    subgraph "RAGAnything Class"
        POST_INIT["__post_init__"]
        CONFIG_ATTR["self.config"]
    end

    subgraph "RAGAnythingConfig Class"
        FIELD_DIR["working_dir"]
        FIELD_PARSE["parser / parse_method"]
        FIELD_MODAL["enable_*_processing"]
        FIELD_CTX["context_*"]
    end

    POST_INIT -->|checks| CONFIG_ATTR
    POST_INIT -->|creates default| CONFIG_ATTR
    CONFIG_ATTR --> FIELD_DIR
    CONFIG_ATTR --> FIELD_PARSE
    CONFIG_ATTR --> FIELD_MODAL
    CONFIG_ATTR --> FIELD_CTX
```

**Sources:** [raganything/raganything.py:99-110](), [raganything/config.py:12-116]()

## Configuration Parameters

### Directory Configuration
These parameters control file system locations for storage and parsing output.

| Parameter | Type | Default | Env Variable | Description |
|-----------|------|---------|--------------|-------------|
| `working_dir` | `str` | `"./rag_storage"` | `WORKING_DIR` | Directory where RAG storage and cache files are stored. |
| `parser_output_dir` | `str` | `"./output"` | `OUTPUT_DIR` | Default output directory for parsed content. |

**Sources:** [raganything/config.py:18-27]()

### Parser Configuration
Controls document parser selection and extraction behavior.

| Parameter | Type | Default | Env Variable | Description |
|-----------|------|---------|--------------|-------------|
| `parser` | `str` | `"mineru"` | `PARSER` | Parser selection: `'mineru'`, `'docling'`, or `'paddleocr'`. |
| `parse_method` | `str` | `"auto"` | `PARSE_METHOD` | Default parsing method: `'auto'`, `'ocr'`, or `'txt'`. |
| `display_content_stats` | `bool` | `True` | `DISPLAY_CONTENT_STATS` | Whether to display content statistics during parsing. |

**Backward Compatibility:** The configuration supports a legacy variable `MINERU_PARSE_METHOD`. If `PARSE_METHOD` is not set, it will fallback to this value and issue a `DeprecationWarning`.

**Sources:** [raganything/config.py:23-35](), [raganything/config.py:117-158]()

### Multimodal Processing Configuration
Controls the activation of specialized modal processors.

| Parameter | Type | Default | Env Variable | Description |
|-----------|------|---------|--------------|-------------|
| `enable_image_processing` | `bool` | `True` | `ENABLE_IMAGE_PROCESSING` | Enable image content processing via `ImageModalProcessor`. |
| `enable_table_processing` | `bool` | `True` | `ENABLE_TABLE_PROCESSING` | Enable table content processing via `TableModalProcessor`. |
| `enable_equation_processing` | `bool` | `True` | `ENABLE_EQUATION_PROCESSING` | Enable equation content processing via `EquationModalProcessor`. |

**Sources:** [raganything/config.py:39-52]()

### Context Extraction Configuration
Controls how surrounding context is provided to modal processors to improve description accuracy.

| Parameter | Type | Default | Env Variable | Description |
|-----------|------|---------|--------------|-------------|
| `context_window` | `int` | `1` | `CONTEXT_WINDOW` | Number of items before/after current item to include. |
| `context_mode` | `str` | `"page"` | `CONTEXT_MODE` | Context mode: `'page'` (page-based) or `'chunk'` (chunk-based). |
| `max_context_tokens` | `int` | `2000` | `MAX_CONTEXT_TOKENS` | Maximum number of tokens in extracted context. |
| `include_headers` | `bool` | `True` | `INCLUDE_HEADERS` | Whether to include document headers and titles in context. |
| `include_captions` | `bool` | `True` | `INCLUDE_CAPTIONS` | Whether to include image/table captions in context. |
| `context_filter_content_types`| `List[str]`| `["text"]` | `CONTEXT_FILTER_CONTENT_TYPES`| Content types to include in context extraction. |
| `content_format` | `str` | `"minerU"` | `CONTENT_FORMAT` | Default content format for context extraction. |

**Sources:** [raganything/config.py:80-111]()

### Batch Processing Configuration
Controls concurrent processing behavior for folders or multiple documents.

| Parameter | Type | Default | Env Variable | Description |
|-----------|------|---------|--------------|-------------|
| `max_concurrent_files` | `int` | `1` | `MAX_CONCURRENT_FILES` | Maximum number of files to process concurrently. |
| `supported_file_extensions` | `List[str]` | (Standard set) | `SUPPORTED_FILE_EXTENSIONS` | List of supported extensions (e.g., .pdf, .docx, .md). |
| `recursive_folder_processing`| `bool` | `True` | `RECURSIVE_FOLDER_PROCESSING`| Whether to recursively process subfolders. |

**Sources:** [raganything/config.py:56-76]()

### Path Handling Configuration
| Parameter | Type | Default | Env Variable | Description |
|-----------|------|---------|--------------|-------------|
| `use_full_path` | `bool` | `False` | `USE_FULL_PATH` | Whether to use full file path or just basename for file references. |

**Sources:** [raganything/config.py:114-115]()

## Configuration Methods in RAGAnything

The `RAGAnything` class provides several methods to interact with and update this configuration at runtime.

### Dynamic Updates
- `update_config(**kwargs)`: Updates general configuration parameters. [raganything/raganything.py:222-230]()
- `update_context_config(**context_kwargs)`: Specifically updates context extraction parameters and recreates the `ContextExtractor`. [raganything/raganything.py:521-551]()

### Inspection Methods
- `get_config_info()`: Returns a categorized dictionary of the current configuration, including directory, parsing, multimodal, context, and batch settings. [raganything/raganything.py:437-491]()
- `get_processor_info()`: Returns a status report of the system, including initialized modal processors and the current configuration state. [raganything/raganything.py:553-585]()

**Sources:** [raganything/raganything.py:222-585]()

## Complete Configuration Example

```python
from raganything import RAGAnything, RAGAnythingConfig

# Programmatic initialization
config = RAGAnythingConfig(
    parser="docling",
    parse_method="ocr",
    max_concurrent_files=4,
    context_window=2,
    enable_equation_processing=False
)

# Initializing RAGAnything with the custom config
rag = RAGAnything(
    config=config,
    working_dir="./my_knowledge_base" # Overrides config.working_dir if provided
)

# Updating configuration after initialization
rag.update_config(display_content_stats=False)
rag.update_context_config(max_context_tokens=1000)
```

**Sources:** [raganything/config.py:12-116](), [raganything/raganything.py:99-135](), [raganything/raganything.py:222-230]()

---

# Page: Environment Variables

# Environment Variables

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [env.example](env.example)
- [examples/lmstudio_integration_example.py](examples/lmstudio_integration_example.py)
- [raganything/config.py](raganything/config.py)

</details>



This page documents all environment variables supported by RAG-Anything and LightRAG. Environment variables provide a declarative way to configure the system without modifying code, making deployment and configuration management easier across different environments.

**Scope**: This page covers environment variables loaded from `.env` files and system environment. For programmatic Python configuration using `RAGAnythingConfig`, see [RAGAnythingConfig](#8.1). For detailed storage backend connection strings and parameters, see [Storage Backend Configuration](#8.3). For model provider API keys and endpoints, see [Model Provider Configuration](#8.4).

## Environment Variable Loading

RAG-Anything loads environment variables using the following priority (highest to lowest):

1. **System environment variables** - Variables set in your shell or deployment environment.
2. **`.env` file** - Variables defined in a `.env` file in the working directory.
3. **Default values** - Hardcoded defaults in the codebase.

The system uses the `get_env_value` utility from `lightrag.utils` to read variables, which handles automatic type conversion for numeric and boolean values [raganything/config.py:9-10]().

### Data Flow Diagram: Configuration Initialization

The following diagram illustrates how the `RAGAnythingConfig` class [raganything/config.py:13-116]() consumes environment variables during instantiation.

```mermaid
graph TD
    subgraph "Environment Sources"
        ENV_FILE[".env file"]
        SYS_ENV["System Shell Env"]
    end

    subgraph "Loading Utility"
        GET_ENV["lightrag.utils.get_env_value"]
    end

    subgraph "Config Entity: RAGAnythingConfig"
        WD["working_dir"]
        PM["parse_method"]
        PAR["parser"]
        IMG["enable_image_processing"]
        MAX_C["max_concurrent_files"]
        CTX_W["context_window"]
    end

    ENV_FILE --> GET_ENV
    SYS_ENV --> GET_ENV
    GET_ENV --> WD
    GET_ENV --> PM
    GET_ENV --> PAR
    GET_ENV --> IMG
    GET_ENV --> MAX_C
    GET_ENV --> CTX_W
```

**Sources:** [raganything/config.py:13-116](), [env.example:1-40]()

## Configuration Categories

### Logging Configuration

Controls logging behavior and output destinations for the RAG-Anything system.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LOG_LEVEL` | string | `INFO` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `VERBOSE` | boolean | `False` | Enable verbose logging output |
| `LOG_MAX_BYTES` | integer | `10485760` | Maximum size of log files in bytes (10MB default) |
| `LOG_BACKUP_COUNT` | integer | `5` | Number of rotated log files to keep |
| `LOG_DIR` | path | current directory | Directory path for log file storage |

**Sources:** [env.example:75-81]()

### Document Processing Configuration

Controls document parsing, output directories, and parser selection.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `PARSER` | string | `mineru` | Parser selection: `mineru`, `docling`, or `paddleocr` [raganything/config.py:29-30]() |
| `PARSE_METHOD` | string | `auto` | Parse method: `auto`, `ocr`, or `txt` [raganything/config.py:23-24]() |
| `OUTPUT_DIR` | path | `./output` | Output directory for parsed documents [raganything/config.py:26-27]() |
| `DISPLAY_CONTENT_STATS` | boolean | `true` | Display content statistics after parsing [raganything/config.py:32-35]() |
| `INPUT_DIR` | path | `./inputs` | Default input directory for documents [env.example:38]() |
| `WORKING_DIR` | path | `./rag_storage` | Directory for RAG storage and cache [raganything/config.py:18-19]() |

**Deprecation Warning:** The variable `MINERU_PARSE_METHOD` is deprecated. The `RAGAnythingConfig.__post_init__` method [raganything/config.py:117-129]() automatically maps it to `PARSE_METHOD` if the latter is not set, while issuing a `DeprecationWarning`.

**Sources:** [raganything/config.py:16-36](), [raganything/config.py:117-158](), [env.example:35-46]()

### Multimodal Processing Configuration

Enables or disables processing of specific content modalities during the multimodal batch processing stage.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ENABLE_IMAGE_PROCESSING` | boolean | `true` | Enable image content processing and captioning [raganything/config.py:39-42]() |
| `ENABLE_TABLE_PROCESSING` | boolean | `true` | Enable table structure analysis and processing [raganything/config.py:44-47]() |
| `ENABLE_EQUATION_PROCESSING` | boolean | `true` | Enable mathematical equation parsing [raganything/config.py:49-52]() |

**Sources:** [raganything/config.py:37-52](), [env.example:48-51]()

### Batch Processing Configuration

Controls concurrent document processing and file type filtering.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `MAX_CONCURRENT_FILES` | integer | `1` | Maximum number of files to process concurrently [raganything/config.py:56-59]() |
| `SUPPORTED_FILE_EXTENSIONS` | string | (Long list) | Comma-separated list of supported extensions [raganything/config.py:61-71]() |
| `RECURSIVE_FOLDER_PROCESSING` | boolean | `true` | Enable recursive folder traversal [raganything/config.py:73-76]() |

**Sources:** [raganything/config.py:54-77](), [env.example:53-56]()

### Context Extraction Configuration

Controls how contextual text is extracted around multimodal elements for enhanced understanding by the `ContextExtractor`.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `CONTEXT_WINDOW` | integer | `1` | Number of content units before/after modal element [raganything/config.py:80-81]() |
| `CONTEXT_MODE` | string | `page` | Context extraction mode: `page` or `chunk` [raganything/config.py:83-84]() |
| `MAX_CONTEXT_TOKENS` | integer | `2000` | Maximum tokens to extract from context [raganything/config.py:86-89]() |
| `INCLUDE_HEADERS` | boolean | `true` | Include document headers in context [raganything/config.py:91-92]() |
| `INCLUDE_CAPTIONS` | boolean | `true` | Include element captions in context [raganything/config.py:94-97]() |
| `CONTEXT_FILTER_CONTENT_TYPES` | string | `text` | Comma-separated list of content types [raganything/config.py:99-107]() |
| `CONTENT_FORMAT` | string | `minerU` | Default format for extraction [raganything/config.py:109-110]() |

**Sources:** [raganything/config.py:78-111](), [env.example:58-65]()

### RAG Query Configuration

Controls retrieval and response generation behavior during queries.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `HISTORY_TURNS` | integer | `3` | Number of conversation turns to include in history |
| `COSINE_THRESHOLD` | float | `0.2` | Minimum cosine similarity for vector retrieval |
| `TOP_K` | integer | `60` | Number of top results to retrieve |
| `MAX_TOKEN_TEXT_CHUNK` | integer | `4000` | Maximum tokens per text chunk in context |
| `MAX_TOKEN_RELATION_DESC` | integer | `4000` | Maximum tokens for relationship descriptions |
| `MAX_TOKEN_ENTITY_DESC` | integer | `4000` | Maximum tokens for entity descriptions |
| `MAX_GRAPH_NODES` | integer | `1000` | Maximum nodes to retrieve from graph |

**Sources:** [env.example:83-90]()

### LLM and Embedding Configuration

These variables configure the model bindings used for text generation, vision analysis, and vector embeddings.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LLM_BINDING` | string | `openai` | LLM provider: `openai`, `ollama`, `vllm`, `lmstudio`, etc. [env.example:117-118]() |
| `LLM_MODEL` | string | `gpt-4o` | Model name or identifier [env.example:119]() |
| `VISION_MODEL` | string | `gpt-4o` | Model used for image analysis [env.example:120]() |
| `LLM_BINDING_HOST` | url | - | API endpoint URL [env.example:121]() |
| `LLM_BINDING_API_KEY` | string | - | API authentication key [env.example:122]() |
| `MAX_ASYNC` | integer | `4` | Maximum concurrent LLM requests [env.example:113]() |
| `EMBEDDING_BINDING` | string | `ollama` | Embedding provider [env.example:136]() |
| `EMBEDDING_MODEL` | string | `bge-m3:latest` | Embedding model name [env.example:137]() |
| `EMBEDDING_DIM` | integer | `1024` | Vector dimension [env.example:138]() |

**Sources:** [env.example:105-151](), [examples/lmstudio_integration_example.py:39-43]()

## Environment Variable to Code Entity Mapping

This diagram bridges the environment variables to the specific code classes and logic they initialize.

```mermaid
graph LR
    subgraph "Environment Variables"
        VAR_PARSER["PARSER"]
        VAR_MAX_C["MAX_CONCURRENT_FILES"]
        VAR_LLM_B["LLM_BINDING"]
        VAR_V_MOD["VISION_MODEL"]
    end

    subgraph "Code Entity Space"
        RAC["class RAGAnythingConfig"]
        RA["class RAGAnything"]
        BM["mixin BatchMixin"]
        MM_PROC["Multimodal Processors"]
    end

    VAR_PARSER --> RAC
    VAR_MAX_C --> RAC
    RAC --> RA
    
    VAR_MAX_C -.-> BM
    VAR_LLM_B -.-> RA
    VAR_V_MOD -.-> MM_PROC
```

**Sources:** [raganything/config.py:13-31](), [raganything/config.py:56-59](), [env.example:117-120]()

## Storage Backend Selection

Selects storage implementations for different data layers.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `LIGHTRAG_KV_STORAGE` | string | - | Key-value storage class (e.g., `PGKVStorage`) |
| `LIGHTRAG_VECTOR_STORAGE` | string | - | Vector storage class (e.g., `PGVectorStorage`) |
| `LIGHTRAG_DOC_STATUS_STORAGE`| string | - | Document status storage class |
| `LIGHTRAG_GRAPH_STORAGE` | string | - | Graph storage class (e.g., `Neo4JStorage`) |

**Sources:** [env.example:152-156]()

## Offline Deployment Configuration

Enables air-gapped deployment without internet access for model downloads.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `TIKTOKEN_CACHE_DIR` | path | - | Local directory containing cached tiktoken models |

**Sources:** [env.example:13-17]()

## Server Configuration (API Server)

Configuration for the optional LightRAG API server.

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `HOST` | string | `0.0.0.0` | Server bind address |
| `PORT` | integer | `9621` | Server port |
| `AUTH_ACCOUNTS` | string | - | Authentication accounts: `user:pass,user2:pass2` |
| `TOKEN_SECRET` | string | - | JWT token secret |
| `LIGHTRAG_API_KEY` | string | - | API key for server authentication |

**Sources:** [env.example:4-28]()

---

# Page: Storage Backend Configuration

# Storage Backend Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [env.example](env.example)
- [examples/lmstudio_integration_example.py](examples/lmstudio_integration_example.py)
- [reproduce/env.example](reproduce/env.example)
- [reproduce/index.py](reproduce/index.py)
- [reproduce/llm_answer_evaluator.py](reproduce/llm_answer_evaluator.py)

</details>



This page documents the configuration of storage backends in RAG-Anything. The system uses a multi-storage architecture with four distinct storage types, each supporting multiple backend implementations. This page covers storage backend selection, connection parameters, and configuration examples for each supported backend.

For general environment variable configuration, see [Environment Variables](#8.2). For model provider configuration (LLM/embedding services), see [Model Provider Configuration](#8.4).

## Storage Architecture Overview

RAG-Anything inherits LightRAG's multi-storage architecture, which separates data into four specialized storage types. The system utilizes these backends to manage the lifecycle of document processing, from initial parsing to knowledge graph construction and final retrieval.

1. **KV Storage**: Stores text chunks, full-text content, and metadata.
2. **Vector Storage**: Stores vector embeddings for semantic search across entities, relationships, and text chunks.
3. **Graph Storage**: Manages the Knowledge Graph, containing extracted entities and their relational mappings.
4. **Doc Status Storage**: Tracks document processing status (e.g., `READY`, `HANDLING`, `PROCESSED`, `FAILED`) and multimodal processing flags.

### Storage Type and Backend Matrix

```mermaid
graph TB
    subgraph StorageTypes["Four Storage Types"]
        KV["KV Storage<br/>Text chunks and full-text"]
        Vector["Vector Storage<br/>Semantic embeddings"]
        Graph["Graph Storage<br/>Knowledge graph"]
        DocStatus["Doc Status Storage<br/>Processing metadata"]
    end
    
    subgraph Backends["Supported Backends"]
        PG["PostgreSQL<br/>+ pgvector extension"]
        Mongo["MongoDB"]
        Neo4j["Neo4j"]
        Milvus["Milvus"]
        Qdrant["Qdrant"]
        Redis["Redis"]
        AGE["Apache AGE"]
    end
    
    KV -->|"PGKVStorage"| PG
    KV -->|"MongoKVStorage"| Mongo
    KV -->|"RedisKVStorage"| Redis
    
    Vector -->|"PGVectorStorage"| PG
    Vector -->|"MilvusVectorStorage"| Milvus
    Vector -->|"QdrantVectorStorage"| Qdrant
    
    Graph -->|"Neo4JStorage"| Neo4j
    Graph -->|"AGEStorage"| AGE
    Graph -->|"MongoGraphStorage"| Mongo
    
    DocStatus -->|"PGDocStatusStorage"| PG
    DocStatus -->|"MongoDocStatusStorage"| Mongo
```

**Storage Type Support Summary:**

| Storage Type | PostgreSQL | MongoDB | Neo4j | Milvus | Qdrant | Redis | AGE |
|-------------|-----------|---------|-------|--------|--------|-------|-----|
| KV Storage | ✓ | ✓ | - | - | - | ✓ | - |
| Vector Storage | ✓ | - | - | ✓ | ✓ | - | - |
| Graph Storage | - | ✓ | ✓ | - | - | - | ✓ |
| Doc Status Storage | ✓ | ✓ | - | - | - | - | - |

Sources: [env.example:152-156](), [env.example:167-212]()

## Storage Backend Selection

Storage backends are selected via environment variables. If not specified, LightRAG uses default in-memory implementations.

### Environment Variable Mapping

```mermaid
graph LR
    subgraph EnvVars["Environment Variables"]
        KVVAR["LIGHTRAG_KV_STORAGE"]
        VECVAR["LIGHTRAG_VECTOR_STORAGE"]
        GRAPHVAR["LIGHTRAG_GRAPH_STORAGE"]
        DOCVAR["LIGHTRAG_DOC_STATUS_STORAGE"]
    end
    
    subgraph ClassNames["Storage Class Names"]
        PGKV["PGKVStorage"]
        PKVEC["PGVectorStorage"]
        PGDOC["PGDocStatusStorage"]
        NEO4J["Neo4JStorage"]
        MONGO["MongoKVStorage<br/>MongoGraphStorage<br/>MongoDocStatusStorage"]
        MILVUS["MilvusVectorStorage"]
        QDRANT["QdrantVectorStorage"]
        REDIS["RedisKVStorage"]
        AGE["AGEStorage"]
    end
    
    KVVAR --> PGKV
    KVVAR --> MONGO
    KVVAR --> REDIS
    
    VECVAR --> PKVEC
    VECVAR --> MILVUS
    VECVAR --> QDRANT
    
    GRAPHVAR --> NEO4J
    GRAPHVAR --> MONGO
    GRAPHVAR --> AGE
    
    DOCVAR --> PGDOC
    DOCVAR --> MONGO
```

**Configuration Pattern:**

```bash
# Select storage backends by class name in .env
LIGHTRAG_KV_STORAGE=PGKVStorage
LIGHTRAG_VECTOR_STORAGE=PGVectorStorage
LIGHTRAG_DOC_STATUS_STORAGE=PGDocStatusStorage
LIGHTRAG_GRAPH_STORAGE=Neo4JStorage
```

Sources: [env.example:152-156]()

## PostgreSQL Configuration

PostgreSQL supports KV Storage, Vector Storage, and Doc Status Storage. Vector storage requires the `pgvector` extension.

### Configuration Parameters

| Variable | Purpose | Required | Default |
|----------|---------|----------|---------|
| `POSTGRES_HOST` | PostgreSQL server hostname | Yes | `localhost` |
| `POSTGRES_PORT` | PostgreSQL server port | Yes | `5432` |
| `POSTGRES_USER` | Database username | Yes | - |
| `POSTGRES_PASSWORD` | Database password | Yes | - |
| `POSTGRES_DATABASE` | Database name | Yes | - |
| `POSTGRES_MAX_CONNECTIONS` | Connection pool size | No | `12` |

### Example Configuration

```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=your_username
POSTGRES_PASSWORD='your_password'
POSTGRES_DATABASE=your_database
POSTGRES_MAX_CONNECTIONS=12
```

Sources: [env.example:167-173]()

## Neo4j Configuration

Neo4j provides graph storage for the knowledge graph structure. It stores entities and relationships extracted from documents.

### Configuration Parameters

| Variable | Purpose | Required | Default |
|----------|---------|----------|---------|
| `NEO4J_URI` | Neo4j connection URI | Yes | - |
| `NEO4J_USERNAME` | Database username | Yes | `neo4j` |
| `NEO4J_PASSWORD` | Database password | Yes | - |

### Example Configuration

```bash
NEO4J_URI=neo4j+s://xxxxxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD='your_password'
```

Sources: [env.example:177-180]()

## Apache AGE Configuration

Apache AGE (A Graph Extension) provides graph storage using PostgreSQL. It can be configured as an independent instance or embedded.

### Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `AGE_POSTGRES_DB` | AGE database name | Yes |
| `AGE_POSTGRES_USER` | AGE username | Yes |
| `AGE_POSTGRES_PASSWORD` | AGE password | Yes |
| `AGE_POSTGRES_HOST` | AGE server hostname | Yes |
| `AGE_POSTGRES_PORT` | AGE server port | No (Default: 8529) |

Sources: [env.example:182-191]()

## MongoDB Configuration

MongoDB supports KV Storage, Graph Storage, and Doc Status Storage.

### Configuration Parameters

| Variable | Purpose | Required | Default |
|----------|---------|----------|---------|
| `MONGO_URI` | MongoDB connection URI | Yes | - |
| `MONGO_DATABASE` | Database name | No | `LightRAG` |

### Example Configuration

```bash
MONGO_URI=mongodb://root:root@localhost:27017/
MONGO_DATABASE=LightRAG
```

Sources: [env.example:193-197]()

## Milvus Configuration

Milvus provides high-performance vector storage optimized for large-scale semantic search.

### Configuration Parameters

| Variable | Purpose | Required | Default |
|----------|---------|----------|---------|
| `MILVUS_URI` | Milvus server URI | Yes | `http://localhost:19530` |
| `MILVUS_DB_NAME` | Database name | No | `lightrag` |
| `MILVUS_USER` | Username for auth | No | - |
| `MILVUS_PASSWORD` | Password for auth | No | - |
| `MILVUS_TOKEN` | Token for auth | No | - |

Sources: [env.example:199-204]()

## Qdrant Configuration

Qdrant is a vector database used for storing embeddings of chunks, entities, and relationships.

### Configuration Parameters

| Variable | Purpose | Required | Default |
|----------|---------|----------|---------|
| `QDRANT_URL` | Qdrant service URL | Yes | `http://localhost:6333` |
| `QDRANT_API_KEY` | API key for authentication | No | - |

Sources: [env.example:206-208]()

## Redis Configuration

Redis is used for fast Key-Value storage, typically for text chunks.

### Configuration Parameters

| Variable | Purpose | Required | Default |
|----------|---------|----------|---------|
| `REDIS_URI` | Redis connection URI | Yes | `redis://localhost:6379` |

Sources: [env.example:210-211]()

## Implementation and Data Flow

When `RAGAnything` is initialized, it calls `_ensure_lightrag_initialized` which sets up the `LightRAG` instance with the specified storage backends.

```mermaid
sequenceDiagram
    participant App as "RAGAnything Instance"
    participant Config as "RAGAnythingConfig"
    participant Storage as "LightRAG Storage Factory"
    participant DB as "Database Backend (PG/Neo4j/etc)"

    App->>Config: Read storage env vars
    App->>Storage: Initialize storage classes (KV, Vector, Graph, DocStatus)
    Storage->>DB: Establish connection strings
    App->>DB: Create tables/collections/indexes if missing
    Note over App, DB: Data Flow: Document -> Parser -> Storage -> Retrieval
```

### Data Flow during Processing
1. **Parser**: Documents are parsed into a `content_list`.
2. **KV Storage**: Raw text and chunked content are stored.
3. **Doc Status**: The document ID is marked as `HANDLING` then `PROCESSED`.
4. **Graph Storage**: Extracted entities and relationships are inserted.
5. **Vector Storage**: Embeddings generated by the `embedding_func` are stored for the entities, relations, and chunks.

Sources: [examples/lmstudio_integration_example.py:90-97](), [reproduce/index.py:109-116](), [env.example:152-156]()

---

# Page: Model Provider Configuration

# Model Provider Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [docs/vllm_integration.md](docs/vllm_integration.md)
- [env.example](env.example)
- [examples/lmstudio_integration_example.py](examples/lmstudio_integration_example.py)
- [examples/minimax_integration_example.py](examples/minimax_integration_example.py)
- [examples/vllm_integration_example.py](examples/vllm_integration_example.py)
- [tests/test_minimax_integration.py](tests/test_minimax_integration.py)

</details>



## Purpose and Scope

This page documents how to configure different LLM (Large Language Model) and embedding model providers in RAG-Anything. The system supports multiple providers including OpenAI, Ollama, Azure OpenAI, LM Studio, vLLM, and MiniMax for both text generation and embeddings.

For general configuration parameters, see [RAGAnythingConfig](#8.1). For storage backend configuration, see [Storage Backend Configuration](#8.3). For environment variable reference, see [Environment Variables](#8.2).

---

## Provider Architecture Overview

RAG-Anything uses a provider abstraction layer that allows you to configure different AI service providers through environment variables. The configuration flows from environment variables to the `RAGAnything` instance, which then uses these settings to create the appropriate function wrappers.

### Data Flow and System Entities

The following diagram maps the configuration from environment space into the code entity space, specifically showing how `RAGAnything` and `LightRAG` interact with provider functions.

```mermaid
graph TB
    subgraph "Environment Space"
        EnvVars["Environment Variables<br/>LLM_BINDING, LLM_MODEL, etc."]
        EnvFile[".env File"]
    end
    
    subgraph "Code Entity Space: RAG-Anything"
        RAGConfig["RAGAnythingConfig Class"]
        RAGInstance["RAGAnything Instance"]
        
        LLMFunc["llm_model_func<br/>(async callable)"]
        VisionFunc["vision_model_func<br/>(async callable)"]
        EmbedFunc["embedding_func<br/>(lightrag.utils.EmbeddingFunc)"]
    end
    
    subgraph "Code Entity Space: Provider Wrappers"
        OpenAILLM["openai_complete_if_cache"]
        OpenAIEmbed["openai_embed"]
        OllamaLLM["ollama_model_complete"]
    end
    
    subgraph "External Model Providers"
        OpenAISvc["OpenAI API"]
        OllamaSvc["Ollama Server"]
        vLLMSvc["vLLM Server"]
        MiniMaxSvc["MiniMax API"]
    end
    
    EnvFile --> EnvVars
    EnvVars --> RAGConfig
    RAGConfig --> RAGInstance
    
    RAGInstance --> LLMFunc
    RAGInstance --> VisionFunc
    RAGInstance --> EmbedFunc
    
    LLMFunc -. "uses" .-> OpenAILLM
    LLMFunc -. "uses" .-> OllamaLLM
    
    OpenAILLM --> OpenAISvc
    OpenAILLM --> vLLMSvc
    OpenAILLM --> MiniMaxSvc
    OpenAIEmbed --> OpenAISvc
    OllamaLLM --> OllamaSvc
```

**Sources:** [env.example:105-145](), [examples/lmstudio_integration_example.py:45-73](), [examples/vllm_integration_example.py:59-93]()

---

## Supported Provider Types

RAG-Anything supports the following provider types through the `LLM_BINDING` and `EMBEDDING_BINDING` environment variables:

| Provider Type | Value | LLM Support | Embedding Support | Description |
|---------------|-------|-------------|-------------------|-------------|
| OpenAI | `openai` | ✅ | ✅ | Official OpenAI API |
| Ollama | `ollama` | ✅ | ✅ | Local model server |
| Azure OpenAI | `azure_openai` | ✅ | ✅ | Microsoft Azure OpenAI Service |
| LM Studio | `lmstudio` | ✅ | ✅ | Local OpenAI-compatible server |
| vLLM | `vllm` | ✅ | ✅ | High-throughput production server |
| MiniMax | `minimax` | ✅ | ❌ | High-quality cloud LLM (OpenAI-compatible) |

**Sources:** [env.example:117-118](), [env.example:129-130](), [examples/minimax_integration_example.py:1-34]()

---

## LLM Configuration

### Common LLM Parameters

These parameters apply to all LLM providers:

| Environment Variable | Purpose | Default | Valid Values |
|---------------------|---------|---------|--------------|
| `LLM_BINDING` | Provider type | `openai` | `openai`, `ollama`, `azure_openai`, `lmstudio`, `vllm` |
| `LLM_MODEL` | Model identifier | `gpt-4o` | Provider-specific model names |
| `LLM_BINDING_HOST` | API endpoint URL | `https://api.openai.com/v1` | Full URL with protocol |
| `LLM_BINDING_API_KEY` | Authentication key | - | Provider API key or token |
| `TIMEOUT` | Request timeout in seconds | `240` | Integer or `None` |
| `TEMPERATURE` | Generation temperature | `0` | `0.0` to `2.0` |
| `MAX_TOKENS` | Context window size | `32768` | Integer (e.g., 32768) |
| `MAX_ASYNC` | Max concurrent LLM requests | `4` | Integer |

**Sources:** [env.example:105-116]()

### Provider-Specific Details

#### vLLM (Production High-Throughput)
vLLM is the recommended backend for high-throughput production RAG. It exposes an OpenAI-compatible API and supports continuous batching and PagedAttention.

*   **Setup:** Use `vllm serve <model_name>` to start the server.
*   **Configuration:** Set `LLM_BINDING=vllm` and point `LLM_BINDING_HOST` to the vLLM endpoint (default `:8000/v1`).

**Sources:** [docs/vllm_integration.md:1-18](), [examples/vllm_integration_example.py:51-56]()

#### MiniMax (Cloud LLM)
MiniMax is integrated using its OpenAI-compatible endpoint.
*   **Constraint:** MiniMax requires temperature to be in the range `(0.0, 1.0]`. RAG-Anything's integration examples handle this via `_normalize_minimax_temperature`.
*   **Embeddings:** MiniMax does not provide an embedding model; you must use a separate provider (e.g., OpenAI or Ollama) for embeddings.

**Sources:** [examples/minimax_integration_example.py:77-86](), [examples/minimax_integration_example.py:114-126]()

#### LM Studio (Local Offline)
Ideal for local development and testing offline models.
*   **Configuration:** Set `LLM_BINDING=lmstudio` and `LLM_BINDING_HOST=http://localhost:1234/v1`.

**Sources:** [examples/lmstudio_integration_example.py:14-22]()

---

## Embedding Configuration

### Parameters

| Environment Variable | Purpose | Default | Valid Values |
|---------------------|---------|---------|--------------|
| `EMBEDDING_BINDING` | Provider type | `ollama` | `openai`, `ollama`, `vllm`, `lmstudio` |
| `EMBEDDING_MODEL` | Model identifier | `bge-m3:latest` | e.g., `text-embedding-3-large` |
| `EMBEDDING_DIM` | Vector dimension | `1024` | 1024, 1536, 3072, etc. |
| `EMBEDDING_BINDING_HOST` | API endpoint URL | `http://localhost:11434` | Full URL |
| `EMBEDDING_BATCH_NUM` | Chunks per request | `32` | Integer |

**Sources:** [env.example:134-143]()

---

## Implementation and Function Binding

RAG-Anything initializes model functions during instantiation. If no functions are provided to the `RAGAnything` constructor, it generates them based on environment variables.

### LLM and Embedding Function Mapping

This diagram illustrates the association between the `RAGAnything` initialization logic and the specific provider functions.

```mermaid
graph LR
    subgraph "Initialization Logic"
        Init["RAGAnything.__init__"]
        Config["RAGAnythingConfig"]
    end

    subgraph "Provider Functions (lightrag.llm)"
        OAI_Comp["openai_complete_if_cache"]
        OAI_Embed["openai_embed"]
    end

    subgraph "Custom Integration Wrappers"
        vLLM_Func["vllm_llm_model_func"]
        MiniMax_Func["minimax_llm_model_func"]
        LMS_Func["lmstudio_llm_model_func"]
    end

    Init -->| "Reads LLM_BINDING" | Config
    Config -->| "if vllm" | vLLM_Func
    Config -->| "if minimax" | MiniMax_Func
    
    vLLM_Func --> OAI_Comp
    MiniMax_Func --> OAI_Comp
    LMS_Func --> OAI_Comp
```

**Sources:** [examples/lmstudio_integration_example.py:45-60](), [examples/minimax_integration_example.py:89-111](), [examples/vllm_integration_example.py:59-77]()

### Manual Binding Example (LM Studio)
Users can manually bind functions if they need custom logic or are not using environment variables.

```python
from raganything import RAGAnything, RAGAnythingConfig
from lightrag.llm.openai import openai_complete_if_cache

async def custom_llm_func(prompt, system_prompt=None, history_messages=None, **kwargs):
    return await openai_complete_if_cache(
        model="your-model",
        prompt=prompt,
        system_prompt=system_prompt,
        base_url="http://localhost:1234/v1",
        api_key="lm-studio",
        **kwargs
    )

rag = RAGAnything(
    config=RAGAnythingConfig(working_dir="./storage"),
    llm_model_func=custom_llm_func
)
```

**Sources:** [examples/lmstudio_integration_example.py:45-60](), [examples/lmstudio_integration_example.py:180-184]()

---

## Summary of Configuration Variables

| Category | Variables |
|----------|-----------|
| **OpenAI** | `LLM_BINDING=openai`, `LLM_MODEL`, `LLM_BINDING_API_KEY` |
| **Azure** | `LLM_BINDING=azure_openai`, `AZURE_OPENAI_DEPLOYMENT`, `AZURE_OPENAI_API_VERSION` |
| **Ollama** | `LLM_BINDING=ollama`, `LLM_MODEL`, `LLM_BINDING_HOST` |
| **vLLM** | `LLM_BINDING=vllm`, `LLM_MODEL`, `LLM_BINDING_HOST`, `LLM_BINDING_API_KEY` |
| **MiniMax** | `MINIMAX_API_KEY`, `MINIMAX_LLM_MODEL`, `MINIMAX_BASE_URL` |

**Sources:** [env.example:112-132](), [examples/minimax_integration_example.py:53-55]()

---

# Page: Usage Examples

# Usage Examples

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [examples/raganything_example.py](examples/raganything_example.py)

</details>



## Purpose and Scope

This page provides an overview of common usage patterns and practical examples for RAG-Anything. It demonstrates the core workflows for processing documents, querying content, and integrating with various components.

For detailed examples of specific scenarios, see:
- **Basic single document processing**: [Basic Document Processing](#9.1) — Step-by-step example of processing a single document with `process_document_complete`, including parser selection and output directory configuration.
- **Processing multiple documents**: [Batch Processing](#9.2) — Example of processing multiple documents with `process_folder_complete`, `BatchParser` dry-run mode, and configuring `max_workers` and concurrency.
- **Using pre-parsed content**: [Direct Content List Insertion](#9.3) — Example of inserting pre-parsed content using `insert_content_list`, including the content list schema and supported content types.
- **Different query approaches**: [Query Examples](#9.4) — Examples of different query types (text, multimodal, VLM-enhanced) with code snippets showing mode selection and `multimodal_content` structure.
- **Offline deployment**: [Local LLM Integration](#9.5) — Complete example of integrating with LM Studio, Ollama, and vLLM for offline deployment, including function wrappers and compatibility patches.
- **Using existing LightRAG instances**: [Loading Existing LightRAG Instances](#9.6) — Example of initializing `RAGAnything` with a pre-configured LightRAG instance to add multimodal capabilities to a previously text-only index.
- **Format-specific processing**: [Format-Specific Processing Examples](#9.7) — Examples of processing different file formats (PDF, Office documents, images, text files, Markdown) including enhanced Markdown-to-PDF conversion.

For configuration details, see [Configuration](#8). For understanding the processing pipeline, see [Five-Stage Processing Pipeline](#3.2).

## Common Usage Patterns

RAG-Anything supports three primary usage patterns, each suited to different scenarios:

```mermaid
graph TB
    subgraph Pattern1["Pattern 1: End-to-End Processing"]
        Doc1["Document File<br/>(PDF/Office/Image)"]
        Process1["process_document_complete()"]
        Query1["aquery() / query()"]
        Result1["Response"]
        
        Doc1 --> Process1
        Process1 --> Query1
        Query1 --> Result1
    end
    
    subgraph Pattern2["Pattern 2: Pre-Parsed Content"]
        ContentList["content_list<br/>(List of Dicts)"]
        Insert["insert_content_list()"]
        Query2["aquery() / query()"]
        Result2["Response"]
        
        ContentList --> Insert
        Insert --> Query2
        Query2 --> Result2
    end
    
    subgraph Pattern3["Pattern 3: Existing LightRAG"]
        ExistingRAG["Existing LightRAG<br/>Instance"]
        InitRAG["RAGAnything(lightrag=...)"]
        Process3["process_document_complete()"]
        Query3["aquery() / query()"]
        Result3["Response"]
        
        ExistingRAG --> InitRAG
        InitRAG --> Process3
        Process3 --> Query3
        Query3 --> Result3
    end
```

**Sources:** [README.md:249-966](), [examples/raganything_example.py:1-331]()

## Core Initialization Pattern

All usage examples follow a common initialization pattern involving three key components: configuration, model functions, and `RAGAnything` instantiation.

### Standard Initialization Code Structure

```mermaid
flowchart LR
    subgraph Config["Configuration"]
        RAGConfig["RAGAnythingConfig"]
        WorkDir["working_dir"]
        Parser["parser selection"]
        Modes["enable_*_processing"]
        
        RAGConfig --> WorkDir
        RAGConfig --> Parser
        RAGConfig --> Modes
    end
    
    subgraph Functions["Model Functions"]
        LLM["llm_model_func"]
        Vision["vision_model_func"]
        Embed["embedding_func"]
        
        APIKey["api_key"]
        BaseURL["base_url"]
        
        APIKey --> LLM
        APIKey --> Vision
        APIKey --> Embed
        BaseURL --> LLM
        BaseURL --> Vision
        BaseURL --> Embed
    end
    
    subgraph Init["RAGAnything Initialization"]
        RAGInstance["RAGAnything(...)"]
        
        RAGConfig --> RAGInstance
        LLM --> RAGInstance
        Vision --> RAGInstance
        Embed --> RAGInstance
    end
    
    Init --> Ready["Ready for Operations"]
```

**Sources:** [README.md:326-427](), [examples/raganything_example.py:108-206]()

### Configuration Setup

The `RAGAnythingConfig` class centralizes all configuration parameters:

```python
# From examples/raganything_example.py:108-116
config = RAGAnythingConfig(
    working_dir="./rag_storage",
    parser="mineru",  # or "docling", "paddleocr"
    parse_method="auto",  # or "ocr", "txt"
    enable_image_processing=True,
    enable_table_processing=True,
    enable_equation_processing=True,
)
```

**Key Parameters:**
- `working_dir`: Directory for LightRAG storage (text_chunks, vector DBs, knowledge graph) [examples/raganything_example.py:111]()
- `parser`: Parser backend selection - `mineru`, `docling`, or `paddleocr` [examples/raganything_example.py:112]()
- `parse_method`: Parsing approach - `auto` (intelligent selection), `ocr` (OCR-focused), or `txt` (text extraction) [examples/raganything_example.py:113]()
- `enable_*_processing`: Boolean flags for each multimodal content type [examples/raganything_example.py:114-116]()

**Sources:** [README.md:336-344](), [examples/raganything_example.py:108-116]()

### Model Function Definitions

Three model functions must be provided: LLM, vision, and embedding functions.

#### LLM Model Function

```python
# From examples/raganything_example.py:123-132
def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
    return openai_complete_if_cache(
        llm_model,
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        api_key=api_key,
        base_url=base_url,
        **kwargs,
    )
```

This function handles text generation for entity extraction, relationship mapping, and query response generation.

**Sources:** [examples/raganything_example.py:123-132]()

#### Vision Model Function

```python
# From examples/raganything_example.py:135-187
def vision_model_func(
    prompt,
    system_prompt=None,
    history_messages=[],
    image_data=None,
    messages=None,
    **kwargs,
):
    # If messages format is provided (for multimodal VLM enhanced query), use it directly
    if messages:
        return openai_complete_if_cache(vision_model, "", messages=messages, ...)
    # Traditional single image format for ImageModalProcessor
    elif image_data:
        return openai_complete_if_cache(
            vision_model,
            "",
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                ]}
            ],
            ...
        )
    # Pure text format
    else:
        return llm_model_func(prompt, system_prompt, history_messages, **kwargs)
```

This function supports three modes:
1. **Messages format**: Used by VLM-enhanced queries with multiple images [examples/raganything_example.py:144-154]()
2. **Single image format**: Used by `ImageModalProcessor` for image captioning [examples/raganything_example.py:156-184]()
3. **Text fallback**: Used when no image data is provided [examples/raganything_example.py:186-187]()

**Sources:** [examples/raganything_example.py:131-183](), [README.md:359-406]()

#### Embedding Function

```python
# From examples/raganything_example.py:193-203
embedding_func = EmbeddingFunc(
    embedding_dim=embedding_dim,
    max_token_size=8192,
    func=partial(
        openai_embed.func,
        model=embedding_model,
        api_key=api_key,
        base_url=base_url,
    ),
)
```

The embedding function generates vector representations for semantic search. The `embedding_dim` must match the model's output dimension.

**Sources:** [examples/raganything_example.py:190-203](), [README.md:408-418]()

### RAGAnything Instantiation

```python
# From examples/raganything_example.py:206-211
rag = RAGAnything(
    config=config,
    llm_model_func=llm_model_func,
    vision_model_func=vision_model_func,
    embedding_func=embedding_func,
)
```

This creates a `RAGAnything` instance that internally initializes LightRAG and the modal processing subsystem.

**Sources:** [examples/raganything_example.py:206-211]()

## Document Processing Workflow

```mermaid
graph TB
    subgraph Input["Input Stage"]
        FilePath["file_path"]
        OutputDir["output_dir"]
        ParseMethod["parse_method"]
        Parser["parser selection"]
    end
    
    subgraph Process["process_document_complete()"]
        CheckStatus["Check doc_status"]
        CheckCache["Check parse_cache"]
        ParserStep["Parser.parse()"]
        ContentList["content_list"]
        ProcessMM["ProcessorMixin"]
        ModalProc["Modal Processors"]
        TextProc["Text Processing"]
    end
    
    subgraph Storage["Storage Stage"]
        TextChunks["text_chunks DB"]
        ChunksVDB["chunks_vdb"]
        EntitiesVDB["entities_vdb"]
        RelationsVDB["relations_vdb"]
        KG["knowledge_graph"]
    end
    
    FilePath --> CheckStatus
    OutputDir --> ParserStep
    ParseMethod --> ParserStep
    Parser --> ParserStep
    
    CheckStatus -->|"not processed"| CheckCache
    CheckCache -->|"miss"| ParserStep
    CheckCache -->|"hit"| ContentList
    ParserStep --> ContentList
    
    ContentList --> ProcessMM
    ProcessMM -->|"multimodal content"| ModalProc
    ProcessMM -->|"text content"| TextProc
    
    ModalProc --> TextChunks
    ModalProc --> KG
    TextProc --> TextChunks
    TextProc --> KG
```

**Sources:** [README.md:428-433]()

### Basic Processing Example

```python
# From README.md:428-433
await rag.process_document_complete(
    file_path="path/to/your/document.pdf",
    output_dir="./output",
    parse_method="auto"
)
```

The `process_document_complete()` method performs the full five-stage pipeline:

1. **Document Parsing**: Calls the configured parser to extract `content_list`.
2. **Content Separation**: Separates text from multimodal content.
3. **Multimodal Processing**: Routes images/tables/equations to modal processors.
4. **Entity Extraction**: Extracts entities and relationships via LLM.
5. **Storage**: Writes to all storage backends.

**Sources:** [README.md:428-433]()

## Query Patterns

RAG-Anything supports three distinct query patterns, each suited to different use cases:

```mermaid
graph LR
    subgraph Queries["Query Types"]
        TextQuery["aquery()<br/>Pure Text Query"]
        VLMQuery["aquery()<br/>VLM-Enhanced Query"]
        MMQuery["aquery_with_multimodal()<br/>Multimodal Query"]
    end
    
    subgraph Processing["Query Processing"]
        TextQuery --> Retrieve1["LightRAG Retrieval"]
        VLMQuery --> ImageDetect["Detect Images in Context"]
        ImageDetect --> VLMProcess["VLM Analysis"]
        VLMProcess --> Retrieve2["LightRAG Retrieval"]
        MMQuery --> MMProcess["Process MM Content"]
        MMProcess --> Retrieve3["LightRAG Retrieval"]
    end
    
    subgraph Response["Response Generation"]
        Retrieve1 --> LLMGen1["llm_model_func"]
        Retrieve2 --> VLMGen["vision_model_func"]
        Retrieve3 --> LLMGen2["llm_model_func"]
    end
```

**Sources:** [README.md:602-671](), [examples/raganything_example.py:213-260]()

### Pure Text Queries

```python
# From examples/raganything_example.py:222-225
result = await rag.aquery(query, mode="hybrid")
```

Pure text queries use LightRAG's retrieval without additional processing. Supported modes include `hybrid`, `local`, `global`, and `naive` [examples/raganything_example.py:222-225]().

**Sources:** [examples/raganything_example.py:216-225](), [README.md:607-616]()

### VLM-Enhanced Queries

```python
# From README.md:619-645
vlm_result = await rag.aquery(
    "Analyze the charts and figures in the document",
    mode="hybrid"
)
```

When `vision_model_func` is provided, the system automatically detects image markers (e.g., `VLM_IMAGE_`) in retrieved context and integrates them into the VLM prompt [README.md:619-645]().

**Sources:** [README.md:619-645]()

### Multimodal Queries

```python
# From examples/raganything_example.py:231-244
multimodal_result = await rag.aquery_with_multimodal(
    "Compare this performance data with any similar results mentioned in the document",
    multimodal_content=[
        {
            "type": "table",
            "table_data": """Method,Accuracy,Processing_Time
                        RAGAnything,95.2%,120ms
                        Traditional_RAG,87.3%,180ms""",
            "table_caption": "Performance comparison results",
        }
    ],
    mode="hybrid",
)
```

This pattern allows querying with explicit multimodal content (tables, equations, images) provided by the user [examples/raganything_example.py:231-244]().

**Sources:** [examples/raganything_example.py:228-260](), [README.md:648-671]()

## Example Execution Flow

The following sequence diagram illustrates the document processing and querying flow:

```mermaid
sequenceDiagram
    participant User
    participant Main
    participant RAGAnything
    participant Parser
    participant ProcessorMixin
    participant ModalProcessors
    participant LightRAG
    
    User->>Main: Run with file_path
    Main->>RAGAnything: process_document_complete()
    RAGAnything->>ProcessorMixin: parse_document()
    ProcessorMixin->>Parser: parse(file_path)
    Parser-->>ProcessorMixin: content_list
    ProcessorMixin->>ModalProcessors: process_multimodal_content()
    ModalProcessors->>LightRAG: Insert entities/relationships
    ProcessorMixin->>LightRAG: insert(text_content)
    
    Main->>RAGAnything: aquery(text_query)
    RAGAnything->>LightRAG: query()
    LightRAG-->>Main: Response
```

**Sources:** [examples/raganything_example.py:89-267]()

## Code Organization for Examples

RAG-Anything provides several example scripts in the `examples/` directory:

| Example File | Purpose | API Key Required |
|-------------|---------|------------------|
| `raganything_example.py` | End-to-end processing with queries [examples/raganything_example.py:1-10]() | Yes |
| `modalprocessors_example.py` | Direct multimodal processing [README.md:1034]() | Yes |
| `office_document_test.py` | Office format parsing test [README.md:1015]() | No |
| `image_format_test.py` | Image format parsing test [README.md:1020]() | No |
| `text_format_test.py` | Text format parsing test [README.md:1025]() | No |

**Sources:** [README.md:1000-1034](), [examples/raganything_example.py:1-10]()

---

# Page: Basic Document Processing

# Basic Document Processing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/image_format_test.py](examples/image_format_test.py)
- [examples/office_document_test.py](examples/office_document_test.py)
- [examples/raganything_example.py](examples/raganything_example.py)
- [examples/text_format_test.py](examples/text_format_test.py)

</details>



## Purpose

This page provides a step-by-step example of processing a single document with RAG-Anything. The example covers initialization, document processing with `process_document_complete()`, and basic querying with `aquery()`. 

RAG-Anything extends the standard RAG pipeline by incorporating multimodal analysis (images, tables, equations) into the knowledge graph construction process.

---

## Processing Pipeline Overview

Document processing transforms raw files into a queryable knowledge graph through five stages. The `ProcessorMixin` class coordinates the flow from raw file to indexed content.

### Code Entity Flow

The following diagram maps the high-level stages to the specific code entities responsible for the transformation.

```mermaid
graph TD
    subgraph "Natural Language Space (Input)"
        FILE["Raw Document<br/>(PDF, DOCX, Image)"]
    end

    subgraph "Code Entity Space (Processing)"
        RAG["RAGAnything Class<br/>raganything/main.py"]
        PROC["process_document_complete()<br/>raganything/processor.py"]
        PARSE["parse_document()<br/>raganything/parser.py"]
        CLIST["content_list<br/>(List[Dict])"]
        INSERT["insert_content_list()<br/>raganything/processor.py"]
        MODAL["Modal Processors<br/>(ImageModalProcessor, etc.)<br/>raganything/modalprocessors.py"]
    end

    subgraph "Storage Space (Output)"
        LRAG["LightRAG.insert()<br/>lightrag/lightrag.py"]
        VDB["Vector DB<br/>(entities_vdb, chunks_vdb)"]
        KG["Knowledge Graph<br/>(graph_chunk_entity_relation.graphml)"]
    end

    FILE --> RAG
    RAG --> PROC
    PROC --> PARSE
    PARSE --> CLIST
    CLIST --> INSERT
    INSERT --> MODAL
    MODAL --> LRAG
    LRAG --> VDB
    LRAG --> KG
```

**Sources:** [raganything/processor.py:150-250](), [raganything/parser.py:1-50](), [examples/raganything_example.py:90-117]()

---

## Step-by-Step Implementation

### 1. Import and Configuration
First, initialize the configuration and model functions. RAG-Anything relies on `RAGAnythingConfig` to define the environment and parser settings.

```python
from raganything import RAGAnything, RAGAnythingConfig
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc

config = RAGAnythingConfig(
    working_dir="./rag_storage",
    parser="mineru",         # Options: mineru, docling, paddleocr
    parse_method="auto",     # Options: auto, ocr, txt
    enable_image_processing=True,
    enable_table_processing=True,
    enable_equation_processing=True,
)
```

**Sources:** [examples/raganything_example.py:109-117](), [raganything/config.py:1-40]()

### 2. Define Model Functions
RAG-Anything requires three core functions: `llm_model_func` for text, `vision_model_func` for multimodal analysis, and `embedding_func` for vectorization.

```python
# LLM Function for entity extraction
def llm_model_func(prompt, **kwargs):
    return openai_complete_if_cache("gpt-4o-mini", prompt, api_key="sk-...", **kwargs)

# Vision Function for describing images/tables
def vision_model_func(prompt, image_data=None, messages=None, **kwargs):
    if messages: # VLM-enhanced query format
        return openai_complete_if_cache("gpt-4o", "", messages=messages, **kwargs)
    return openai_complete_if_cache("gpt-4o", prompt, image_data=image_data, **kwargs)

# Embedding Function
embedding_func = EmbeddingFunc(
    embedding_dim=3072,
    func=lambda texts: openai_embed(texts, model="text-embedding-3-large", api_key="sk-...")
)
```

**Sources:** [examples/raganything_example.py:123-198](), [README.md:346-418]()

### 3. Initialize and Process
Initialize the `RAGAnything` instance and call `process_document_complete`. This method handles the entire lifecycle: parsing, content separation, multimodal description generation, and knowledge graph insertion.

```python
rag = RAGAnything(
    config=config,
    llm_model_func=llm_model_func,
    vision_model_func=vision_model_func,
    embedding_func=embedding_func
)

# Complete pipeline execution
await rag.process_document_complete(
    file_path="manual.pdf",
    output_dir="./output_files"
)
```

**Sources:** [raganything/processor.py:150-170](), [examples/raganything_example.py:201-211]()

---

## Parameter Reference

### process_document_complete()
Defined in `ProcessorMixin`, this is the primary entry point for single document ingestion.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `file_path` | `str` | Required | Path to the document (PDF, DOCX, Image, TXT, MD). |
| `output_dir` | `str` | `None` | Directory for parser artifacts (JSON, images, MD). |
| `parse_method` | `str` | `None` | Overrides config `parse_method` ("auto", "ocr", "txt"). |
| `parser` | `str` | `None` | Overrides config `parser` ("mineru", "docling", "paddleocr"). |
| `display_stats` | `bool` | `True` | Logs the count of text blocks, images, and tables found. |

**Sources:** [raganything/processor.py:150-168]()

### Supported File Formats
RAG-Anything supports a wide range of formats through its parser backends:
*   **MinerU/Docling:** PDF, DOCX, PPTX, XLSX. [examples/office_document_test.py:60-64]()
*   **Images:** JPG, PNG, BMP, TIFF, WebP. [examples/image_format_test.py:66-75]()
*   **Text:** TXT, MD. [examples/text_format_test.py:49-50]()

---

## Internal Data Flow

The following diagram illustrates how the `ProcessorMixin` coordinates data between the `Parser` and the `ModalProcessors`.

```mermaid
sequenceDiagram
    participant User
    participant RAG as RAGAnything (ProcessorMixin)
    participant P as Parser (Mineru/Docling)
    participant M as ModalProcessors (Image/Table/Eq)
    participant L as LightRAG

    User->>RAG: process_document_complete(file)
    RAG->>P: parse_document(file)
    P-->>RAG: content_list (JSON-like structure)
    
    RAG->>RAG: _separate_content(content_list)
    Note over RAG: Splits into Text, Images, Tables, Equations
    
    RAG->>M: _process_multimodal_content_batch_type_aware()
    M->>M: generate_description_only() (via VLM)
    M-->>RAG: Descriptions & Relationships
    
    RAG->>L: insert(combined_text_and_descriptions)
    L-->>RAG: Indexing Complete
    RAG-->>User: Done
```

**Sources:** [raganything/processor.py:170-240](), [raganything/processor.py:348-380](), [raganything/modalprocessors.py:100-150]()

---

## Next Steps

*   **Batch Processing:** To process entire directories, see [9.2 Batch Processing](9.2).
*   **Pre-parsed Content:** If you already have JSON content, use `insert_content_list()`. See [9.3 Direct Content List Insertion](9.3).
*   **Querying:** Learn about the different retrieval modes in [7.1 Query Architecture](7.1).

---

# Page: Batch Processing

# Batch Processing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/batch_processing.md](docs/batch_processing.md)
- [docs/enhanced_markdown.md](docs/enhanced_markdown.md)
- [examples/batch_dry_run_example.py](examples/batch_dry_run_example.py)
- [examples/batch_processing_example.py](examples/batch_processing_example.py)
- [examples/enhanced_markdown_example.py](examples/enhanced_markdown_example.py)
- [raganything/batch.py](raganything/batch.py)
- [raganything/query.py](raganything/query.py)

</details>



This page describes the batch processing capabilities of RAG-Anything, which allow for the efficient processing of multiple documents in parallel. It covers high-level integration via `BatchMixin`, the specialized `BatchParser` for dry-run and standalone parsing, and concurrency controls.

## Overview

The batch processing system is designed to improve throughput for large document collections. It provides parallel processing using thread pools or asyncio tasks, progress tracking with `tqdm`, and robust error isolation.

### Key Features
- **Parallel Processing**: Concurrent file handling via `max_workers` [raganything/batch.py:70-71]().
- **Progress Tracking**: Real-time feedback using `tqdm` progress bars [docs/batch_processing.md:12]().
- **Dry Run Mode**: Preview supported files without executing heavy parsing logic [raganything/batch_parser.py:228-232]().
- **Recursive Discovery**: Optional subdirectory traversal [raganything/batch.py:87-91]().

## System Architecture

The batch processing logic is distributed across `BatchMixin` (for RAG integration) and `BatchParser` (for raw parsing).

### Batch Processing Entity Space

```mermaid
graph TB
    subgraph "Batch Control Space"
        RAG["RAGAnything"]
        BMIX["BatchMixin"]
        BPARSER["BatchParser"]
    end

    subgraph "Execution Space"
        SEMAPHORE["asyncio.Semaphore"]
        WORKERS["ThreadPoolExecutor"]
        TASK["process_single_file"]
    end

    subgraph "Result Space"
        BPR["BatchProcessingResult"]
        STATS["Processing Statistics"]
    end

    RAG -- "inherits" --> BMIX
    BMIX -- "calls" --> BPARSER
    BMIX -- "manages" --> SEMAPHORE
    BPARSER -- "uses" --> WORKERS
    SEMAPHORE -- "limits" --> TASK
    BPARSER -- "returns" --> BPR
    BPR -- "generates" --> STATS
```
Sources: [raganything/batch.py:19-20](), [raganything/batch_parser.py:18-20](), [raganything/batch.py:106-110]()

## BatchParser and Dry-Run Mode

The `BatchParser` class is a standalone utility for processing files without necessarily involving the full RAG knowledge graph. It is particularly useful for pre-flight checks using `dry_run=True`.

### Dry-Run Example
A dry run allows you to verify which files in a directory are supported by the selected parser backend (e.g., Mineru, Docling) without consuming API credits or CPU time.

```python
from raganything.batch_parser import BatchParser

batch_parser = BatchParser(parser_type="mineru", show_progress=False)
result = batch_parser.process_batch(
    file_paths=["./docs"],
    output_dir="./output",
    recursive=True,
    dry_run=True
)

print(f"Files to be processed: {len(result.successful_files)}")
```
Sources: [examples/batch_dry_run_example.py:43-49](), [raganything/batch_parser.py:228-232]()

### BatchProcessingResult Schema
Every batch operation returns a `BatchProcessingResult` object containing detailed execution metadata.

| Field | Type | Description |
|-------|------|-------------|
| `successful_files` | `List[str]` | Paths of files successfully handled [raganything/batch_parser.py:26]() |
| `failed_files` | `List[str]` | Paths of files that encountered errors [raganything/batch_parser.py:27]() |
| `errors` | `Dict[str, str]` | Mapping of file paths to error messages [raganything/batch_parser.py:30]() |
| `processing_time` | `float` | Total duration in seconds [raganything/batch_parser.py:29]() |
| `dry_run` | `bool` | Whether the run was a simulation [raganything/batch_parser.py:32]() |

Sources: [raganything/batch_parser.py:24-33]()

## RAG Integration: process_folder_complete

The `process_folder_complete` method in `BatchMixin` is the primary entry point for batch-indexing folders into the RAG system.

### Data Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant RAG as RAGAnything (BatchMixin)
    participant Sem as asyncio.Semaphore
    participant Proc as ProcessorMixin
    participant LR as LightRAG

    User->>RAG: process_folder_complete(folder_path, max_workers=4)
    RAG->>RAG: Discover files via glob/rglob
    Note over RAG: Create tasks for each file
    
    loop For each file
        RAG->>Sem: acquire()
        RAG->>Proc: process_document_complete(file_path)
        Proc->>LR: insert_text_content()
        Proc->>Proc: _process_multimodal_content_batch()
        RAG->>Sem: release()
    end
    
    RAG-->>User: Display Statistics (Success/Fail)
```
Sources: [raganything/batch.py:34-45](), [raganything/batch.py:106-117](), [raganything/batch.py:118-136]()

### Concurrency Configuration
Concurrency is managed at two levels:
1.  **File-Level Concurrency**: `max_workers` controls how many documents are parsed simultaneously using `asyncio.Semaphore` [raganything/batch.py:106-110]().
2.  **Global Defaults**: If not specified, the system uses `config.max_concurrent_files` [raganything/batch.py:71]().

```python
# Configure via RAGAnythingConfig
config = RAGAnythingConfig(
    max_concurrent_files=4,
    recursive_folder_processing=True
)

# Or override in the method call
await rag.process_folder_complete(
    folder_path="./data",
    max_workers=8
)
```
Sources: [raganything/batch.py:70-71](), [docs/batch_processing.md:147]()

## Error Handling and Isolation

The batch system implements "soft-failure" logic. An error in one document (e.g., a corrupted PDF or vision model timeout) does not terminate the entire batch.

1.  **Per-file Try-Except**: Each file task is wrapped in a try-except block [raganything/batch.py:117-140]().
2.  **Exception Gathering**: Results are collected via `asyncio.gather(return_exceptions=True)`, allowing the system to aggregate errors without crashing [raganything/batch.py:148]().
3.  **Reporting**: Final statistics log the specific file path and the error message for every failure [raganything/batch.py:168-171]().

Sources: [raganything/batch.py:138-140](), [raganything/batch.py:148](), [raganything/batch.py:168-171]()

## Performance Considerations

- **Memory Usage**: Each worker thread/task consumes memory for the parser backend (e.g., Docling or MinerU models). High `max_workers` values on systems with low RAM may lead to OOM (Out of Memory) errors [docs/batch_processing.md:209-213]().
- **I/O Bound vs CPU Bound**: Parsing is often CPU/GPU bound (for OCR/Vision), while network-based parsers are I/O bound. Adjust `max_workers` based on your specific parser and hardware [docs/batch_processing.md:214-218]().
- **Recommended Settings**: 
    - Small files: 6-8 workers.
    - Large/Complex files: 2-3 workers [docs/batch_processing.md:220-222]().

---

# Page: Direct Content List Insertion

# Direct Content List Insertion

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/context_aware_processing.md](docs/context_aware_processing.md)
- [examples/insert_content_list_example.py](examples/insert_content_list_example.py)
- [examples/modalprocessors_example.py](examples/modalprocessors_example.py)
- [raganything/processor.py](raganything/processor.py)
- [tests/test_embedding_examples.py](tests/test_embedding_examples.py)
- [tests/test_insert_content_list.py](tests/test_insert_content_list.py)

</details>



This page documents the direct content list insertion feature, which allows users to insert pre-parsed content into RAGAnything without going through the document parsing stage. For full document processing workflows that include parsing, see [Basic Document Processing](#9.1). For details about batch processing multiple documents, see [Batch Processing](#9.2).

## Purpose and Scope

The `insert_content_list` method provides a way to bypass the document parsing phase and directly insert structured content into the RAG system. This is particularly useful when:

- Content has already been parsed by external tools (non-MinerU/Docling parsers)
- Content is programmatically generated rather than extracted from documents
- Parsing results have been cached and need to be reused
- Multiple content sources need to be integrated into a single knowledge base

The method accepts a standardized content list format and processes it through the same multimodal content pipeline as regular document processing, ensuring consistent knowledge graph construction and storage.

## Content List Format Specification

The `content_list` parameter accepts a list of dictionaries, where each dictionary represents a content block. The format is standardized across all content types:

### Supported Content Types

| Content Type | Required Fields | Optional Fields | Notes |
|--------------|----------------|-----------------|-------|
| **text** | `type`, `text`, `page_idx` | - | Plain text content |
| **image** | `type`, `img_path`, `page_idx` | `image_caption`, `image_footnote` | `img_path` must be absolute |
| **table** | `type`, `table_body`, `page_idx` | `table_caption`, `table_footnote` | `table_body` in markdown format |
| **equation** | `type`, `latex`, `page_idx` | `text` | LaTeX formula representation |
| **generic** | `type`, `content`, `page_idx` | Custom fields | Extensible for custom types |

### Format Examples

```python
# Text content
{
    "type": "text",
    "text": "This is the introduction section.",
    "page_idx": 0
}

# Image content
{
    "type": "image",
    "img_path": "/absolute/path/to/figure.jpg",  # Must be absolute path
    "image_caption": ["Figure 1: System Architecture"],
    "image_footnote": ["Source: Authors' design"],
    "page_idx": 1
}

# Table content
{
    "type": "table",
    "table_body": "| Method | Accuracy |\n|--------|----------|\n| Ours | 95.2% |",
    "table_caption": ["Table 1: Results"],
    "table_footnote": ["Test dataset"],
    "page_idx": 2
}

# Equation content
{
    "type": "equation",
    "latex": "P(d|q) = \\frac{P(q|d) \\cdot P(d)}{P(q)}",
    "text": "Document relevance probability",
    "page_idx": 3
}
```

**Sources:** [examples/insert_content_list_example.py:104-172](), [raganything/processor.py:1769-1786]()

## Processing Workflow

The following diagram illustrates the complete processing flow for direct content list insertion:

```mermaid
flowchart TB
    Input["User provides content_list<br/>+ file_path"]
    
    subgraph InsertMethod["ProcessorMixin.insert_content_list Method"]
        ValidateInit["_ensure_lightrag_initialized()"]
        GenDocID["_generate_content_based_doc_id()"]
        DisplayStats{"display_stats<br/>enabled?"}
        StatsLog["Log content statistics"]
        SeparateContent["separate_content()<br/>Split text & multimodal"]
    end
    
    subgraph ContextSetup["Context Configuration"]
        SetContext["set_content_source_for_context()<br/>Enable context extraction"]
    end
    
    subgraph TextProcessing["Text Content Processing"]
        CheckText{"text_content<br/>not empty?"}
        GetFileRef["_get_file_reference()"]
        InsertText["insert_text_content()<br/>to LightRAG"]
    end
    
    subgraph MultimodalProcessing["Multimodal Content Processing"]
        CheckMM{"multimodal_items<br/>not empty?"}
        ProcessMM["_process_multimodal_content()<br/>Process images, tables, equations"]
        MarkComplete["_mark_multimodal_processing_complete()"]
    end
    
    Complete["Content insertion complete"]
    
    Input --> ValidateInit
    ValidateInit --> GenDocID
    GenDocID --> DisplayStats
    DisplayStats -->|Yes| StatsLog
    DisplayStats -->|No| SeparateContent
    StatsLog --> SeparateContent
    
    SeparateContent --> SetContext
    SetContext --> CheckText
    
    CheckText -->|Yes| GetFileRef
    CheckText -->|No| CheckMM
    GetFileRef --> InsertText
    InsertText --> CheckMM
    
    CheckMM -->|Yes| ProcessMM
    CheckMM -->|No| MarkComplete
    ProcessMM --> MarkComplete
    
    MarkComplete --> Complete
```

**Sources:** [raganything/processor.py:1759-1864](), [tests/test_insert_content_list.py:131-155]()

### Key Processing Steps

#### 1. Initialization and Validation

The method begins by ensuring LightRAG is initialized via `_ensure_lightrag_initialized()` and preparing the processing environment by reading the `display_stats` configuration from `self.config.display_content_stats`.

**Sources:** [raganything/processor.py:1793-1798](), [tests/test_insert_content_list.py:116-117]()

#### 2. Document ID Generation

If no `doc_id` is provided, the system generates a content-based ID using `_generate_content_based_doc_id`, which creates a hash from the content's key elements (text, image paths, table bodies, and equations).

```mermaid
flowchart LR
    ContentList["content_list"]
    
    subgraph IDGeneration["ProcessorMixin._generate_content_based_doc_id"]
        Signature["Create content signature<br/>(concatenate all items)"]
        Hash["compute_mdhash_id()<br/>prefix='doc-'"]
    end
    
    DocID["doc_id"]
    
    ContentList --> Signature
    Signature --> Hash
    Hash --> DocID
```

**Sources:** [raganything/processor.py:202-239](), [raganything/processor.py:1805-1806]()

#### 3. Content Separation

The `separate_content` utility function splits the content list into text and multimodal components. Text items are concatenated with page markers, while images, tables, and equations are collected into a separate list.

**Sources:** [raganything/processor.py:1826](), [tests/test_insert_content_list.py:131-155]()

#### 4. Context Configuration for Multimodal Processing

If multimodal items exist, the system calls `set_content_source_for_context(content_list, "mineru")` to enable context-aware processing. This allows modal processors to look up surrounding text during description generation.

**Sources:** [raganything/processor.py:1829-1835](), [docs/context_aware_processing.md:102-114]()

#### 5. Text Content Insertion

Text content is inserted through `insert_text_content`, which calls `self.lightrag.ainsert`. This triggers LightRAG's standard pipeline for chunking, embedding, and entity extraction.

**Sources:** [raganything/processor.py:1838-1848](), [tests/test_insert_content_list.py:141-145]()

#### 6. Multimodal Content Processing

Multimodal items are processed through `_process_multimodal_content`, which manages the batch lifecycle of modal processors.

```mermaid
flowchart TB
    MMItems["multimodal_items"]
    
    subgraph MMProcess["ProcessorMixin._process_multimodal_content"]
        BatchProcess["_process_multimodal_content_batch_type_aware()"]
        
        subgraph BatchStages["Processing Lifecycle"]
            Stage1["ImageModalProcessor<br/>TableModalProcessor<br/>EquationModalProcessor"]
            Stage2["Generate Descriptions"]
            Stage3["Create KG Entities"]
            Stage4["Add belongs_to relations"]
        end
        
        MarkComplete["_mark_multimodal_processing_complete()"]
    end
    
    MMItems --> BatchProcess
    BatchProcess --> Stage1
    Stage1 --> Stage2
    Stage2 --> Stage3
    Stage3 --> Stage4
    Stage4 --> MarkComplete
```

**Sources:** [raganything/processor.py:1854-1855](), [raganything/processor.py:706-882](), [examples/modalprocessors_example.py:85-165]()

## Method Signature and Parameters

The `insert_content_list` method is defined in the `ProcessorMixin` class:

```python
async def insert_content_list(
    self,
    content_list: List[Dict[str, Any]],
    file_path: str = "unknown_document",
    split_by_character: str | None = None,
    split_by_character_only: bool = False,
    doc_id: str | None = None,
    display_stats: bool = None,
)
```

### Parameter Details

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `content_list` | `List[Dict[str, Any]]` | Required | Pre-parsed content items in standardized format |
| `file_path` | `str` | `"unknown_document"` | Reference file path/name for citation purposes |
| `split_by_character` | `str \| None` | `None` | Optional character to split text content by |
| `split_by_character_only` | `bool` | `False` | If True, split only by specified character |
| `doc_id` | `str \| None` | `None` | Optional custom document ID (auto-generated if not provided) |
| `display_stats` | `bool \| None` | `None` | Display content statistics (uses config default if None) |

**Sources:** [raganything/processor.py:1759-1767]()

## Complete Usage Example

The following example demonstrates how to initialize `RAGAnything` and use `insert_content_list` with various content types.

```python
import asyncio
from raganything import RAGAnything, RAGAnythingConfig
from examples.insert_content_list_example import create_sample_content_list

async def main():
    config = RAGAnythingConfig(working_dir="./rag_storage")
    rag = RAGAnything(config=config)
    
    # Create sample content list (text, image, table, equation)
    content_list = create_sample_content_list()
    
    # Direct insertion
    await rag.insert_content_list(
        content_list=content_list,
        file_path="/path/to/source_doc.pdf",
        display_stats=True
    )

if __name__ == "__main__":
    asyncio.run(main())
```

**Sources:** [examples/insert_content_list_example.py:93-172](), [examples/insert_content_list_example.py:221-250]()

## Important Considerations

### Image Path Requirements

**Critical:** The `img_path` field in image content items **must be an absolute path**. The `ImageModalProcessor` uses this path to load the image for captioning and base64 encoding.

**Sources:** [examples/insert_content_list_example.py:114](), [raganything/processor.py:1774-1775]()

### Page Index Field

The `page_idx` field represents the page number where content appears (0-based). This is vital for the `ContextExtractor` to locate surrounding text when `context_mode="page"` is used.

**Sources:** [docs/context_aware_processing.md:162-167](), [raganything/processor.py:1781]()

### Document Status Tracking

The system tracks the completion of multimodal processing separately from text insertion. After text is inserted via `ainsert`, the system marks `multimodal_processed=True` in the `doc_status` record (or `multimodal_status_cache` for compatibility) only after all modal processors have finished.

**Sources:** [raganything/processor.py:161-200](), [tests/test_insert_content_list.py:146-154]()

### Use Cases

- **External Parser Integration**: Use content from specialized OCR engines.
- **Programmatic Content**: Insert data derived from databases or web scraping.
- **Performance**: Bypass expensive PDF parsing when JSON results are already available.

**Sources:** [examples/insert_content_list_example.py:5-11](), [examples/modalprocessors_example.py:4-5]()

---

# Page: Query Examples

# Query Examples

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/raganything_example.py](examples/raganything_example.py)
- [raganything/batch.py](raganything/batch.py)
- [raganything/query.py](raganything/query.py)

</details>



This page demonstrates practical examples of the three query types supported by RAG-Anything: pure text queries, multimodal queries, and VLM-enhanced queries. Each query type is designed for different use cases and provides specific capabilities for interacting with processed documents.

For information about the query system architecture and retrieval mechanisms, see [Query Architecture](#7.1). For API reference documentation of query methods, see [Query Methods API](#10.5). For details about the underlying query processing implementation, see [Text Queries](#7.2), [Multimodal Queries](#7.3), and [VLM-Enhanced Queries](#7.4).

---

## Query Type Overview

RAG-Anything provides three distinct query methods that correspond to different information needs. The `QueryMixin` class handles the logic for mode selection and multimodal content transformation.

| Query Type | Method | Primary Use Case | Key Capability |
|------------|--------|------------------|----------------|
| Pure Text | `aquery()` | Knowledge base search | Retrieves and synthesizes text-based information |
| Multimodal | `aquery_with_multimodal()` | Analyzing user-provided content | Compares external content with document knowledge |
| VLM-Enhanced | `aquery()` with `vlm_enhanced=True` | Visual content analysis | Directly analyzes images within retrieved context |

### Query Type Decision Flow

```mermaid
graph TB
    subgraph QueryTypes["Query Type Decision Flow"]
        UserQuery["User Query Intent"]
        
        NeedExternalContent{"Providing external<br/>content?"}
        HasImages{"Document contains<br/>images to analyze?"}
        BasicKnowledge["Basic knowledge<br/>retrieval?"]
        
        TextQuery["aquery()<br/>Pure Text Query"]
        MultimodalQuery["aquery_with_multimodal()<br/>Multimodal Query"]
        VLMQuery["aquery(vlm_enhanced=True)<br/>VLM-Enhanced Query"]
    end
    
    UserQuery --> NeedExternalContent
    NeedExternalContent -->|"Yes: table,<br/>equation, etc"| MultimodalQuery
    NeedExternalContent -->|No| HasImages
    
    HasImages -->|"Yes: need visual<br/>understanding"| VLMQuery
    HasImages -->|No| BasicKnowledge
    
    BasicKnowledge --> TextQuery
```

**Sources:** [raganything/query.py:102-143](), [raganything/query.py:195-202](), [examples/raganything_example.py:213-260]()

---

## Pure Text Queries

Pure text queries use the `aquery()` method to perform standard knowledge base retrieval. This method acts as a wrapper around `lightrag.aquery` while adding logging, callback dispatching, and automatic VLM detection.

### Query Modes

```mermaid
graph LR
    subgraph QueryModes["aquery() Retrieval Modes"]
        HYBRID["hybrid<br/>Vector + Graph<br/>(Recommended)"]
        LOCAL["local<br/>Local Context<br/>Search"]
        GLOBAL["global<br/>Full Knowledge<br/>Base"]
        NAIVE["naive<br/>Simple Vector<br/>Search"]
    end
    
    HYBRID -->|"Best for"| HybridUse["Balanced retrieval<br/>combining semantic<br/>& structural"]
    LOCAL -->|"Best for"| LocalUse["Finding related<br/>context around<br/>entities"]
    GLOBAL -->|"Best for"| GlobalUse["Broad topic<br/>summarization"]
    NAIVE -->|"Best for"| NaiveUse["Quick semantic<br/>similarity only"]
```

**Sources:** [raganything/query.py:110-110](), [raganything/query.py:162-162]()

### Basic Text Query Example

```python
import asyncio
from raganything import RAGAnything, RAGAnythingConfig

async def text_query_example():
    # Initialize RAGAnything
    config = RAGAnythingConfig(working_dir="./rag_storage")
    rag = RAGAnything(config=config)
    
    # Basic text query with hybrid mode (recommended)
    # This calls QueryMixin.aquery()
    result = await rag.aquery(
        "What are the main findings shown in the figures and tables?",
        mode="hybrid"
    )
    print(f"Answer: {result}")

asyncio.run(text_query_example())
```

**Sources:** [raganything/query.py:102-119](), [examples/raganything_example.py:217-225]()

---

## Multimodal Queries

Multimodal queries use the `aquery_with_multimodal()` method to analyze user-provided content. The system generates a cache key using `_generate_multimodal_cache_key` to ensure stability even with large table or image data.

### Multimodal Query Sequence

```mermaid
sequenceDiagram
    participant User
    participant QueryMixin
    participant ModalProcessor
    participant LightRAG
    
    User->>QueryMixin: aquery_with_multimodal(query, content)
    QueryMixin->>QueryMixin: _generate_multimodal_cache_key()
    
    loop For each item in content
        QueryMixin->>ModalProcessor: generate_description_only(item)
        ModalProcessor-->>QueryMixin: text_description
    end
    
    QueryMixin->>LightRAG: aquery(query + descriptions)
    LightRAG-->>User: Final Result
```

**Sources:** [raganything/query.py:26-40](), [raganything/query.py:233-247]()

### Table and Equation Examples

```python
# Query with table data
table_result = await rag.aquery_with_multimodal(
    "Compare this performance data with document results",
    multimodal_content=[
        {
            "type": "table",
            "table_data": "Method,Acc\nRAG,95%",
            "table_caption": "External results"
        }
    ],
    mode="hybrid"
)

# Query with equation content
equation_result = await rag.aquery_with_multimodal(
    "Explain this formula",
    multimodal_content=[
        {
            "type": "equation",
            "latex": "E = mc^2",
            "equation_caption": "Mass-energy equivalence"
        }
    ],
    mode="hybrid"
)
```

**Sources:** [raganything/query.py:195-210](), [examples/raganything_example.py:228-260]()

---

## VLM-Enhanced Queries

VLM-enhanced queries are triggered automatically in `aquery()` if `vision_model_func` is available. The system performs standard retrieval, then scans the context for image markers.

### VLM Retrieval Logic

The system uses `aquery_vlm_enhanced` to bridge retrieved text chunks and visual models.

```mermaid
graph TD
    subgraph VLM_Logic["QueryMixin.aquery_vlm_enhanced"]
        RAG_Call["lightrag.aquery(only_need_context=True)"]
        Find_Paths["_extract_image_paths_from_context()"]
        Validate["_validate_and_filter_paths()"]
        Encode["encode_image_to_base64()"]
        VLM_Call["vision_model_func(messages=[text+images])"]
    end
    
    RAG_Call --> Find_Paths
    Find_Paths --> Validate
    Validate --> Encode
    Encode --> VLM_Call
```

**Sources:** [raganything/query.py:284-338](), [raganything/query.py:343-380]()

### Manual VLM Control

```python
# Force enable VLM enhancement even if not auto-detected
vlm_enabled = await rag.aquery(
    "What do the images show in this document?",
    mode="hybrid",
    vlm_enhanced=True
)

# Force disable VLM enhancement to save tokens
vlm_disabled = await rag.aquery(
    "Summarize the text only",
    mode="hybrid",
    vlm_enhanced=False
)
```

**Sources:** [raganything/query.py:126-143]()

---

## Complete Usage Example

This example demonstrates the standard implementation of `vision_model_func` required for VLM-enhanced queries.

```python
def vision_model_func(prompt, image_data=None, messages=None, **kwargs):
    # VLM enhanced queries pass a list of messages containing base64 images
    if messages:
        return openai_complete_if_cache(
            "gpt-4o",
            "",
            messages=messages,
            api_key=API_KEY
        )
    # Standard multimodal processing passes raw image_data
    elif image_data:
        return openai_complete_if_cache(
            "gpt-4o",
            prompt,
            image_data=image_data,
            api_key=API_KEY
        )
    return llm_model_func(prompt, **kwargs)

# Initialize with vision support
rag = RAGAnything(
    config=config,
    llm_model_func=llm_model_func,
    vision_model_func=vision_model_func
)
```

**Sources:** [examples/raganything_example.py:135-187](), [raganything/query.py:408-435]()

---

## Best Practices

1. **Cache Key Stability**: When performing multimodal queries, use consistent keys in `multimodal_content`. `_generate_multimodal_cache_key` uses the file basename and MD5 hashes of large tables to maintain cache hits across different environments. [raganything/query.py:54-72]()
2. **Safe Paths**: VLM enhancement only processes images from directories specified in `config.parser_output_dir` or the document's parent directory to prevent unauthorized file access. [raganything/query.py:353-370]()
3. **Mode Selection**:
   - Use `hybrid` for most general queries.
   - Use `naive` when you only need semantic similarity without graph relationships.
   - Use `bypass` if you want to query the LLM directly without retrieval context. [raganything/query.py:110-110]()

**Sources:** [raganything/query.py:42-100](), [raganything/query.py:343-380]()

---

# Page: Local LLM Integration

# Local LLM Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [docs/vllm_integration.md](docs/vllm_integration.md)
- [env.example](env.example)
- [examples/lmstudio_integration_example.py](examples/lmstudio_integration_example.py)
- [examples/ollama_integration_example.py](examples/ollama_integration_example.py)
- [examples/vllm_integration_example.py](examples/vllm_integration_example.py)
- [reproduce/query.py](reproduce/query.py)

</details>



This page documents the integration of RAG-Anything with local Large Language Model (LLM) services, specifically **LM Studio**, **Ollama**, and **vLLM**. Local LLM integration enables fully offline document processing and querying without external API dependencies, providing production-grade performance on local hardware.

**Supported Local Services:**
- **Ollama**: Lightweight local inference server (`http://localhost:11434`) using a native embedding API [examples/ollama_integration_example.py:73-84]().
- **LM Studio**: Desktop application with OpenAI-compatible API (`http://localhost:1234/v1`) [examples/lmstudio_integration_example.py:8-22]().
- **vLLM**: High-throughput inference engine with continuous batching and PagedAttention, ideal for multi-GPU production environments [docs/vllm_integration.md:5-18]().

Sources: [env.example:112-132](), [examples/lmstudio_integration_example.py:1-22](), [docs/vllm_integration.md:1-18]()

## Configuration Architecture

Local LLM integration requires three independent function bindings: text generation (LLM), embedding generation, and optionally vision model. Each binding is configured through environment variables in the `.env` file or passed directly during class initialization.

**Binding Configuration Pattern**

```mermaid
graph TB
    subgraph "Environment Variables (.env)"
        LLM_BIND["LLM_BINDING"]
        LLM_MODEL["LLM_MODEL"]
        LLM_HOST["LLM_BINDING_HOST"]
        LLM_KEY["LLM_BINDING_API_KEY"]
        
        EMB_BIND["EMBEDDING_BINDING"]
        EMB_MODEL["EMBEDDING_MODEL"]
        EMB_DIM["EMBEDDING_DIM"]
        EMB_HOST["EMBEDDING_BINDING_HOST"]
        EMB_KEY["EMBEDDING_BINDING_API_KEY"]
    end
    
    subgraph "RAGAnything Initialization"
        INIT["RAGAnything.__init__()"]
        LLM_FUNC["llm_model_func parameter"]
        EMB_FUNC["embedding_func parameter"]
    end
    
    subgraph "LightRAG Integration Layer"
        OAI_COMPLETE["lightrag.llm.openai.openai_complete_if_cache"]
        OAI_EMBED["lightrag.llm.openai.openai_embed"]
    end
    
    subgraph "Local Services"
        OLLAMA["Ollama Server\n:11434"]
        LMSTUDIO["LM Studio Server\n:1234/v1"]
        VLLM["vLLM Server\n:8000/v1"]
    end
    
    LLM_BIND --> LLM_FUNC
    LLM_MODEL --> LLM_FUNC
    LLM_HOST --> LLM_FUNC
    LLM_KEY --> LLM_FUNC
    
    EMB_BIND --> EMB_FUNC
    EMB_MODEL --> EMB_FUNC
    EMB_DIM --> EMB_FUNC
    EMB_HOST --> EMB_FUNC
    EMB_KEY --> EMB_FUNC
    
    LLM_FUNC --> INIT
    EMB_FUNC --> INIT
    
    LLM_FUNC --> OAI_COMPLETE
    EMB_FUNC --> OAI_EMBED
    
    OAI_COMPLETE --> OLLAMA
    OAI_COMPLETE --> LMSTUDIO
    OAI_COMPLETE --> VLLM
    OAI_EMBED --> OLLAMA
    OAI_EMBED --> LMSTUDIO
    OAI_EMBED --> VLLM
```

Sources: [env.example:105-147](), [examples/lmstudio_integration_example.py:39-42](), [docs/vllm_integration.md:52-69]()

## Environment Variables Reference

### LLM Configuration (Text Generation)

| Variable | Purpose | Ollama Example | vLLM Example |
|----------|---------|----------------|-------------------|
| `LLM_BINDING` | Service type | `ollama` | `vllm` |
| `LLM_MODEL` | Model identifier | `llama3.2` | `Qwen/Qwen2.5-72B-Instruct` |
| `LLM_BINDING_HOST` | API endpoint | `http://localhost:11434/v1` | `http://localhost:8000/v1` |
| `LLM_BINDING_API_KEY` | API key | `ollama` | `token-abc123` |
| `MAX_ASYNC` | Concurrent requests | `4` | `16` (Higher for vLLM) |
| `MAX_TOKENS` | Context window | `32768` | `32768` |

### Embedding Configuration (Vector Generation)

| Variable | Purpose | Ollama Example | vLLM Example |
|----------|---------|----------------|-------------------|
| `EMBEDDING_BINDING` | Service type | `ollama` | `vllm` |
| `EMBEDDING_MODEL` | Model identifier | `nomic-embed-text` | `BAAI/bge-m3` |
| `EMBEDDING_DIM` | Vector dimensions | `768` | `1024` |
| `EMBEDDING_BINDING_HOST` | API endpoint | `http://localhost:11434` | `http://localhost:8001/v1` |

### Caching and Optimization

| Variable | Purpose | Recommended Value |
|----------|---------|-------------------|
| `ENABLE_LLM_CACHE` | Cache LLM responses | `true` |
| `TIKTOKEN_CACHE_DIR` | Offline tokenizer cache | `./tiktoken_cache` |

Sources: [env.example:105-147](), [examples/ollama_integration_example.py:44-52](), [docs/vllm_integration.md:78-90]()

## Function Integration Architecture

RAG-Anything requires custom callable functions for initialization that implement the LightRAG function interfaces. These functions route requests to local services via `openai_complete_if_cache` or native client libraries.

**Function Call Flow**

```mermaid
graph TB
    subgraph "raganything.py"
        RA_INIT["RAGAnything.__init__(llm_model_func, embedding_func)"]
        RA_QUERY["RAGAnything.aquery()"]
        RA_INSERT["RAGAnything.insert_content_list()"]
    end
    
    subgraph "Custom Integration Functions"
        LLM_FUNC["ollama_llm_model_func()"]
        EMB_FUNC["ollama_embedding_async()"]
        EMB_FACTORY["_make_embedding_func() -> EmbeddingFunc"]
    end
    
    subgraph "lightrag.llm.openai"
        OAI_COMPLETE["openai_complete_if_cache()"]
        OAI_EMBED["openai_embed()"]
    end
    
    subgraph "Clients"
        OLLAMA_CLIENT["ollama.AsyncClient"]
        OAI_CLIENT["openai.AsyncOpenAI"]
    end
    
    RA_INIT --> LLM_FUNC
    RA_INIT --> EMB_FACTORY
    EMB_FACTORY --> EMB_FUNC
    
    RA_QUERY --> LLM_FUNC
    RA_INSERT --> EMB_FUNC
    
    LLM_FUNC --> OAI_COMPLETE
    EMB_FUNC --> OLLAMA_CLIENT
    OAI_COMPLETE --> OAI_CLIENT
```

Sources: [examples/ollama_integration_example.py:55-84](), [examples/vllm_integration_example.py:59-93]()

## Implementation Patterns

### Ollama Implementation (Native API)

Ollama uses a different embedding API (`/api/embed`) compared to the standard OpenAI-compatible endpoint. RAG-Anything integrates this using the `ollama` Python library [examples/ollama_integration_example.py:7-10]().

**Embedding Function:**
[examples/ollama_integration_example.py:73-84]()
```python
async def ollama_embedding_async(texts: List[str]) -> List[List[float]]:
    import ollama
    client = ollama.AsyncClient(host=OLLAMA_HOST)
    response = await client.embed(model=OLLAMA_EMBEDDING_MODEL, input=texts)
    return response.embeddings
```

### vLLM Implementation (High-Throughput)

vLLM provides an OpenAI-compatible API server with continuous batching [docs/vllm_integration.md:8-9](). It is recommended to run separate vLLM instances for LLM and Embedding tasks on different ports [docs/vllm_integration.md:45-50]().

**LLM Function:**
[examples/vllm_integration_example.py:59-77]()
```python
async def vllm_llm_model_func(prompt, system_prompt=None, history_messages=None, **kwargs):
    return await openai_complete_if_cache(
        model=VLLM_MODEL_NAME,
        prompt=prompt,
        system_prompt=system_prompt,
        history_messages=history_messages or [],
        base_url=VLLM_BASE_URL,
        api_key=VLLM_API_KEY,
        **kwargs,
    )
```

### LM Studio Implementation (OpenAI-Compatible)

LM Studio acts as a standard OpenAI-compatible server. The implementation leverages `openai_complete_if_cache` and `openai_embed` helpers [examples/lmstudio_integration_example.py:45-74]().

**Embedding Wrapper:**
[examples/lmstudio_integration_example.py:167-173]()
```python
def embedding_func_factory(self):
    return EmbeddingFunc(
        embedding_dim=768,
        max_token_size=8192,
        func=lmstudio_embedding_async,
    )
```

## Initialization Process

**Complete Setup Sequence**

```mermaid
sequenceDiagram
    participant User
    participant Integration as "VLLMRAGIntegration"
    participant VLLM as "vLLM Server (:8000)"
    participant RAGAnything
    
    rect rgb(240, 240, 240)
    note right of User: Phase 1: Connection Testing
    User->>Integration: test_connection()
    Integration->>VLLM: GET /v1/models
    VLLM-->>Integration: Available models
    Integration-->>User: Connected successfully
    end
    
    rect rgb(240, 240, 240)
    note right of User: Phase 2: RAG Initialization
    User->>Integration: initialize_rag()
    Integration->>RAGAnything: RAGAnything(llm_model_func, embedding_func)
    RAGAnything-->>Integration: Instance ready
    Integration-->>User: RAG-Anything initialized
    end
    
    rect rgb(240, 240, 240)
    note right of User: Phase 3: Operations
    User->>Integration: process_document(file_path)
    Integration->>RAGAnything: process_document_complete()
    RAGAnything->>VLLM: Batch inference requests
    VLLM-->>RAGAnything: Embeddings/Summaries
    RAGAnything-->>User: Document processed
    end
```

Sources: [examples/vllm_integration_example.py:124-155](), [examples/vllm_integration_example.py:202-219]()

### Step-by-Step Setup

#### 1. Start Local Server

**vLLM Example:**
```bash
# Chat Model
vllm serve Qwen/Qwen2.5-72B-Instruct --tensor-parallel-size 4 --port 8000
# Embedding Model
vllm serve BAAI/bge-m3 --task embedding --port 8001
```

#### 2. Configure Environment

**vLLM Configuration:**
```bash
LLM_BINDING=vllm
LLM_BINDING_HOST=http://localhost:8000/v1
EMBEDDING_BINDING=vllm
EMBEDDING_BINDING_HOST=http://localhost:8001/v1
EMBEDDING_DIM=1024
```

#### 3. Initialize RAGAnything

[examples/vllm_integration_example.py:202-219]() demonstrates initialization with the custom functions:

```python
self.rag = RAGAnything(
    config=self.config,
    llm_model_func=vllm_llm_model_func,
    embedding_func=self.embedding_func_factory(),
)
```

**Local LLM Configuration Recommendations:**

| Setting | Recommended Value | Reason |
|---------|------------------|--------|
| `enable_image_processing` | `False` | Local vision models are resource-heavy |
| `MAX_ASYNC` | `16` (vLLM) / `4` (Ollama) | vLLM handles high concurrency efficiently |
| `TIKTOKEN_CACHE_DIR` | `./tiktoken_cache` | Prevents internet access during tokenization |

Sources: [env.example:13-17](), [docs/vllm_integration.md:153-156](), [examples/vllm_integration_example.py:112-119]()

## Usage Examples

### High-Throughput Processing (vLLM)

[examples/vllm_integration_example.py:221-238]() shows processing with a high-throughput backend:

```python
await rag.process_document_complete(
    file_path="large_doc.pdf",
    output_dir="./output_vllm",
    display_stats=True
)
```

### Local Querying (Ollama)

[examples/ollama_integration_example.py:212-226]() demonstrates querying a locally hosted model:

```python
# Query using local Llama 3.2
result = await rag.aquery(
    "What are the main findings?",
    mode="hybrid"
)
```

### Compatibility Fixes

When integrating with older LightRAG versions, a "noop" patch is often applied to prevent schema errors in the document status storage [examples/lmstudio_integration_example.py:188-191]():

```python
async def _noop_mark_multimodal(doc_id: str):
    return None

self.rag._mark_multimodal_processing_complete = _noop_mark_multimodal
```

Sources: [examples/lmstudio_integration_example.py:188-191](), [examples/vllm_integration_example.py:221-238]()

---

# Page: Loading Existing LightRAG Instances

# Loading Existing LightRAG Instances

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/raganything_example.py](examples/raganything_example.py)
- [raganything/raganything.py](raganything/raganything.py)

</details>



This page demonstrates how to initialize `RAGAnything` with a pre-configured `LightRAG` instance, enabling multimodal capabilities on existing knowledge bases. This pattern allows extending existing RAG systems with image, table, and equation processing without rebuilding the entire knowledge graph.

For creating new RAGAnything instances from scratch, see [Basic Document Processing](9.1). For storage backend configuration, see [Storage Backend Configuration](8.3).

---

## Purpose and Use Cases

`RAGAnything` supports two initialization patterns:

1. **Self-Managed LightRAG**: RAGAnything creates and manages its own LightRAG instance internally [raganything/raganything.py:304-367]().
2. **Pre-Initialized LightRAG**: RAGAnything wraps an existing LightRAG instance, inheriting its configuration and storage handles [raganything/raganything.py:55-57]().

The pre-initialized pattern is useful when:
- You have an existing LightRAG knowledge base with processed documents.
- You want to add multimodal processing capabilities to legacy systems.
- You need fine-grained control over LightRAG's storage backends (e.g., custom Neo4j or Milvus setups) [raganything/raganything.py:73-84]().
- You're integrating RAGAnything into an existing RAG pipeline.

Sources: [raganything/raganything.py:55-84](), [raganything/raganything.py:245-302]()

---

## Initialization Patterns

### Pattern Comparison

| Aspect | Self-Managed | Pre-Initialized |
|--------|--------------|-----------------|
| **LightRAG Creation** | Automatic during `_ensure_lightrag_initialized` | Manual, passed to `__init__` |
| **Configuration Control** | Via `lightrag_kwargs` | Direct LightRAG params |
| **Storage Management** | Automatic | Manual initialization recommended |
| **Function Inheritance** | Required at init | Inherited from LightRAG |
| **Use Case** | New deployments | Existing systems / Custom Backends |

### Self-Managed Initialization

```python
rag = RAGAnything(
    config=RAGAnythingConfig(working_dir="./rag_storage"),
    llm_model_func=llm_func,        # Required
    embedding_func=embed_func,       # Required
    vision_model_func=vision_func,   # Optional
    lightrag_kwargs={                # Optional LightRAG params
        "top_k": 60,
        "chunk_token_size": 1200
    }
)
```

### Pre-Initialized Pattern

```python
# Create LightRAG instance first
lightrag = LightRAG(
    working_dir="./existing_storage",
    llm_model_func=llm_func,
    embedding_func=embed_func
)
await lightrag.initialize_storages()

# Wrap with RAGAnything
rag = RAGAnything(
    lightrag=lightrag,              # Pass existing instance
    vision_model_func=vision_func   # Add vision capabilities
    # llm_model_func and embedding_func inherited from lightrag
)
```

Sources: [raganything/raganything.py:54-83](), [raganything/raganything.py:247-258]()

---

## Initialization Flow

### RAGAnything Initialization State Machine

```mermaid
stateDiagram-v2
    [*] --> CheckLightRAG: "__post_init__()"
    
    CheckLightRAG --> ValidateParser: "Check if lightrag provided"
    
    ValidateParser --> PreInitialized: "lightrag != None"
    ValidateParser --> SelfManaged: "lightrag == None"
    
    SelfManaged --> ValidateFunctions: "Require llm_model_func\nand embedding_func"
    ValidateFunctions --> CreateLightRAG: "Functions valid"
    ValidateFunctions --> Error: "Missing functions"
    
    CreateLightRAG --> InitStorages: "LightRAG(**lightrag_kwargs)"
    
    PreInitialized --> InheritFunctions: "Check existing functions"
    InheritFunctions --> CheckStorageStatus: "Inherit llm_model_func\nand embedding_func"
    
    CheckStorageStatus --> InitStorages: "Storages not initialized"
    CheckStorageStatus --> InitParseCache: "Storages already initialized"
    
    InitStorages --> InitPipelineStatus: "await initialize_storages()"
    InitPipelineStatus --> InitParseCache: "await initialize_pipeline_status()"
    
    InitParseCache --> InitProcessors: "Create parse_cache storage"
    InitProcessors --> Ready: "Create modal processors"
    
    Ready --> [*]
    Error --> [*]
```

### Code Flow in `_ensure_lightrag_initialized`

The `_ensure_lightrag_initialized` method [raganything/raganything.py:229-230]() handles the logic of bridging an existing `LightRAG` instance into the `RAGAnything` ecosystem.

```mermaid
graph TB
    Start["_ensure_lightrag_initialized()"]
    
    CheckParser["Check parser installation<br/>verify_parser_installation_once()"]
    
    CheckLightRAG{"self.lightrag<br/>is not None?"}
    
    subgraph PreInitPath["Pre-Initialized Path"]
        InheritLLM["Inherit llm_model_func<br/>from lightrag.llm_model_func"]
        InheritEmbed["Inherit embedding_func<br/>from lightrag.embedding_func"]
        CheckStatus{"Storage status<br/>== INITIALIZED?"}
        InitExisting["await lightrag.initialize_storages()<br/>await initialize_pipeline_status()"]
        InitCache1["Create parse_cache storage<br/>using lightrag.key_string_value_json_storage_cls"]
        InitProc1["_initialize_processors()"]
    end
    
    subgraph SelfManagedPath["Self-Managed Path"]
        ValidateLLM{"llm_model_func<br/>provided?"}
        ValidateEmbed{"embedding_func<br/>provided?"}
        BuildParams["Build lightrag_params<br/>Merge lightrag_kwargs"]
        CreateLR["self.lightrag = LightRAG(**params)"]
        InitNew["await lightrag.initialize_storages()<br/>await initialize_pipeline_status()"]
        InitCache2["Create parse_cache storage"]
        InitProc2["_initialize_processors()"]
    end
    
    Success["Return {'success': True}"]
    ErrorNode["Return {'success': False, 'error': msg}"]
    
    Start --> CheckParser
    CheckParser --> CheckLightRAG
    
    CheckLightRAG -->|Yes| InheritLLM
    InheritLLM --> InheritEmbed
    InheritEmbed --> CheckStatus
    CheckStatus -->|No| InitExisting
    CheckStatus -->|Yes| InitCache1
    InitExisting --> InitCache1
    InitCache1 --> InitProc1
    InitProc1 --> Success
    
    CheckLightRAG -->|No| ValidateLLM
    ValidateLLM -->|No| ErrorNode
    ValidateLLM -->|Yes| ValidateEmbed
    ValidateEmbed -->|No| ErrorNode
    ValidateEmbed -->|Yes| BuildParams
    BuildParams --> CreateLR
    CreateLR --> InitNew
    InitNew --> InitCache2
    InitCache2 --> InitProc2
    InitProc2 --> Success
```

Sources: [raganything/raganything.py:229-367]()

---

## Storage Initialization Requirements

When passing a pre-initialized `LightRAG` instance, `RAGAnything` performs these initialization steps:

### Storage Status Check

The system checks if `LightRAG` storages are initialized using the `_storages_status` attribute [raganything/raganything.py:261-264]():

```python
if not hasattr(self.lightrag, "_storages_status") or self.lightrag._storages_status.name != "INITIALIZED":
    await self.lightrag.initialize_storages()
    from lightrag.kg.shared_storage import initialize_pipeline_status
    await initialize_pipeline_status()
```

### Parse Cache Creation

`RAGAnything` creates its own parse cache storage using LightRAG's storage class to ensure consistency across the backend [raganything/raganything.py:284-290]():

```python
self.parse_cache = self.lightrag.key_string_value_json_storage_cls(
    namespace="parse_cache",
    workspace=self.lightrag.working_dir,
    global_config=self.lightrag.__dict__,
    embedding_func=self.embedding_func
)
await self.parse_cache.initialize()
```

### Storage Hierarchy

```mermaid
graph TB
    subgraph LightRAG_Storages["LightRAG Storages"]
        TextChunks["text_chunks<br/>(KV Storage)"]
        ChunksVDB["chunks_vdb<br/>(Vector Storage)"]
        EntitiesVDB["entities_vdb<br/>(Vector Storage)"]
        RelationsVDB["relations_vdb<br/>(Vector Storage)"]
        GraphDB["graph_storage<br/>(Graph Storage)"]
        DocStatus["doc_status<br/>(Doc Status Storage)"]
    end
    
    subgraph RAGAnything_Storages["RAGAnything Extensions"]
        ParseCache["parse_cache<br/>(KV Storage)<br/>namespace='parse_cache'"]
    end
    
    LightRAGInit["LightRAG Instance<br/>Pre-initialized"]
    RAGAnythingInit["RAGAnything Wrapper"]
    
    LightRAGInit --> TextChunks
    LightRAGInit --> ChunksVDB
    LightRAGInit --> EntitiesVDB
    LightRAGInit --> RelationsVDB
    LightRAGInit --> GraphDB
    LightRAGInit --> DocStatus
    
    RAGAnythingInit --> LightRAGInit
    RAGAnythingInit --> ParseCache
    
    ParseCache -.uses same storage class.-> TextChunks
```

Sources: [raganything/raganything.py:261-294](), [raganything/raganything.py:342-349]()

---

## Function Inheritance

### Inherited Functions from LightRAG

When `lightrag` is pre-provided, `RAGAnything` inherits these functions if not explicitly provided in the `RAGAnything` constructor [raganything/raganything.py:247-258]():

| Function | Inheritance Logic | Usage |
|----------|-------------------|-------|
| `llm_model_func` | `lightrag.llm_model_func` | Text generation, entity extraction |
| `embedding_func` | `lightrag.embedding_func` | Vector embeddings |
| `vision_model_func` | Not inherited (must provide) | Image analysis, VLM queries |

### Inheritance Code Flow

```mermaid
graph LR
    subgraph Input["Input Parameters"]
        ProvidedLR["lightrag<br/>(LightRAG instance)"]
        ProvidedLLM["llm_model_func<br/>(optional)"]
        ProvidedEmbed["embedding_func<br/>(optional)"]
        ProvidedVision["vision_model_func<br/>(optional)"]
    end
    
    subgraph Check["Inheritance Check"]
        CheckLLM{"self.llm_model_func<br/>is None?"}
        CheckEmbed{"self.embedding_func<br/>is None?"}
    end
    
    subgraph Result["Final Configuration"]
        FinalLLM["self.llm_model_func"]
        FinalEmbed["self.embedding_func"]
        FinalVision["self.vision_model_func"]
    end
    
    ProvidedLR --> CheckLLM
    ProvidedLLM --> CheckLLM
    
    CheckLLM -->|Yes| InheritLLM["Inherit from<br/>lightrag.llm_model_func"]
    CheckLLM -->|No| UseLLM["Use provided<br/>llm_model_func"]
    
    InheritLLM --> FinalLLM
    UseLLM --> FinalLLM
    
    ProvidedLR --> CheckEmbed
    ProvidedEmbed --> CheckEmbed
    
    CheckEmbed -->|Yes| InheritEmbed["Inherit from<br/>lightrag.embedding_func"]
    CheckEmbed -->|No| UseEmbed["Use provided<br/>embedding_func"]
    
    InheritEmbed --> FinalEmbed
    UseEmbed --> FinalEmbed
    
    ProvidedVision --> FinalVision
```

Sources: [raganything/raganything.py:247-258]()

---

## Complete Example

### Full Working Implementation

This example demonstrates how to define the vision function and wrap an existing instance.

```python
import asyncio
import os
from raganything import RAGAnything, RAGAnythingConfig
from lightrag import LightRAG
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.kg.shared_storage import initialize_pipeline_status
from lightrag.utils import EmbeddingFunc

async def load_existing_lightrag():
    # Configuration
    api_key = os.getenv("OPENAI_API_KEY")
    lightrag_working_dir = "./existing_lightrag_storage"
    
    # Step 1: Create/Load LightRAG instance
    lightrag_instance = LightRAG(
        working_dir=lightrag_working_dir,
        llm_model_func=lambda prompt, **kwargs: 
            openai_complete_if_cache("gpt-4o-mini", prompt, api_key=api_key, **kwargs),
        embedding_func=EmbeddingFunc(
            embedding_dim=3072,
            max_token_size=8192,
            func=lambda texts: openai_embed(texts, model="text-embedding-3-large", api_key=api_key)
        )
    )
    
    # Step 2: Initialize LightRAG storages
    await lightrag_instance.initialize_storages()
    await initialize_pipeline_status()
    
    # Step 3: Define vision model function (not inherited)
    def vision_model_func(prompt, system_prompt=None, history_messages=[], 
                         image_data=None, messages=None, **kwargs):
        if messages:
            return openai_complete_if_cache("gpt-4o", "", messages=messages, api_key=api_key, **kwargs)
        elif image_data:
            return openai_complete_if_cache(
                "gpt-4o", "", 
                messages=[{"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                ]}], api_key=api_key, **kwargs
            )
        return lightrag_instance.llm_model_func(prompt, **kwargs)
    
    # Step 4: Initialize RAGAnything with existing LightRAG
    rag = RAGAnything(
        lightrag=lightrag_instance,
        vision_model_func=vision_model_func
    )
    
    # Step 5: Query existing knowledge base
    result = await rag.aquery("Summarize the document contents", mode="hybrid")
    print("Query result:", result)
    
    await rag.finalize_storages()

if __name__ == "__main__":
    asyncio.run(load_existing_lightrag())
```

Sources: [examples/raganything_example.py:90-188](), [raganything/raganything.py:55-84]()

---

## Important Considerations

### Storage Compatibility
The pre-initialized `LightRAG` instance must use compatible storage backends. RAGAnything creates an additional `parse_cache` namespace in the same KV storage [raganything/raganything.py:284-294]().

### Configuration Precedence
When using pre-initialized LightRAG:
- **Working Directory**: Inherited from `lightrag.working_dir` [raganything/raganything.py:115]().
- **LLM Functions**: Inherited from `lightrag.llm_model_func` if not provided [raganything/raganything.py:247-252]().
- **RAGAnything Config**: Applied to multimodal processing (e.g., `enable_image_processing`) [raganything/raganything.py:369-373]().

### Cleanup
Always call `finalize_storages()` or ensure `close()` is triggered via `atexit` to persist the `parse_cache` and close database connections [raganything/raganything.py:124](), [raganything/raganything.py:143-172]().

Sources: [raganything/raganything.py:115-172](), [raganything/raganything.py:245-302]()

---

# Page: Format-Specific Processing Examples

# Format-Specific Processing Examples

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/enhanced_markdown.md](docs/enhanced_markdown.md)
- [examples/batch_processing_example.py](examples/batch_processing_example.py)
- [examples/enhanced_markdown_example.py](examples/enhanced_markdown_example.py)
- [examples/image_format_test.py](examples/image_format_test.py)
- [examples/office_document_test.py](examples/office_document_test.py)
- [examples/text_format_test.py](examples/text_format_test.py)
- [raganything/enhanced_markdown.py](raganything/enhanced_markdown.py)
- [requirements.txt](requirements.txt)

</details>



This page provides practical examples of processing different document formats with RAG-Anything. Each format type has specific requirements, parser support, and processing considerations. These examples demonstrate how to handle PDF files, Office documents, images, text files, and enhanced Markdown-to-PDF conversion.

---

## Format Support Overview

RAG-Anything supports multiple parsers, each with different format capabilities. The system often uses internal conversion pipelines to normalize non-PDF formats for parsers like MinerU.

| Format Type | File Extensions | MineruParser | DoclingParser | PaddleOCRParser | Requires External Tool |
|-------------|----------------|--------------|---------------|-----------------|----------------------|
| **PDF** | `.pdf` | ✅ | ✅ | ✅ | - |
| **Office Documents** | `.doc`, `.docx`, `.ppt`, `.pptx`, `.xls`, `.xlsx` | ✅ (via conversion) | ✅ (native) | ✅ (via conversion) | LibreOffice |
| **Images** | `.png`, `.jpg`, `.jpeg` | ✅ (native) | ❌ | ✅ (native) | - |
| **Images (Extended)** | `.bmp`, `.tiff`, `.gif`, `.webp` | ✅ (via conversion) | ❌ | ✅ (native) | Pillow |
| **Text Files** | `.txt`, `.md` | ✅ (via conversion) | ❌ | ✅ (via conversion) | ReportLab |
| **HTML** | `.html`, `.htm`, `.xhtml` | ❌ | ✅ | ❌ | - |

**Sources:** [raganything/parser.py:56-59](), [requirements.txt:4-16](), [examples/office_document_test.py:60-64](), [examples/image_format_test.py:66-75]()

---

## Format-to-Code Mapping

The following diagram bridges the natural language document formats to the specific code entities responsible for their processing and conversion.

**Document Format Routing and Backend Entities**

```mermaid
graph TD
    subgraph "Natural Language Space"
        DocX["Word Document (.docx)"]
        Images["Extended Images (.webp, .tiff)"]
        MD["Markdown Files (.md)"]
    end

    subgraph "Code Entity Space"
        subgraph "Conversion Utilities"
            LibO["convert_office_to_pdf()"]
            Pil["PIL.Image conversion"]
            RL["convert_text_to_pdf()"]
            EMC["EnhancedMarkdownConverter"]
        end

        subgraph "Parsers"
            MP["MineruParser"]
            DP["DoclingParser"]
            PP["PaddleOCRParser"]
        end

        subgraph "Pipeline"
            Proc["ProcessorMixin.parse_document()"]
        end
    end

    DocX -->|"If parser='mineru'"| LibO
    DocX -->|"If parser='docling'"| DP
    Images --> Pil
    MD --> RL
    MD --> EMC
    
    LibO --> MP
    Pil --> MP
    RL --> MP
    EMC --> Proc
    
    MP --> Proc
    DP --> Proc
    PP --> Proc
```

**Sources:** [raganything/parser.py:1188-1224](), [raganything/parser.py:1091-1144](), [raganything/enhanced_markdown.py:72-80](), [examples/image_format_test.py:94-100]()

---

## Image Processing Examples

### Extended Image Format Handling
While standard formats like PNG/JPG are handled natively, extended formats (BMP, TIFF, GIF, WebP) are converted to PNG using Pillow before being passed to the OCR engine.

```python
# Example from examples/image_format_test.py
async def test_image_format_parsing(file_path: str):
    rag = RAGAnything()
    
    # Files like .webp or .bmp are automatically detected and converted
    content_list, md_content = await rag.parse_document(
        file_path=file_path,
        parse_method="ocr", # Images default to OCR
        display_stats=True
    )
    
    # Extracted metadata includes image captions and OCR text blocks
    for item in content_list:
        if item.get("type") == "image":
            print(f"Image Path: {item.get('img_path')}")
```

**Sources:** [examples/image_format_test.py:55-116](), [examples/image_format_test.py:142-154]()

---

## Office Document Processing

Office documents require LibreOffice installed on the system path. The `MineruParser` converts these to PDF, while `DoclingParser` can handle them natively.

### Word and PowerPoint Conversion
The system checks for `libreoffice` or `soffice` commands to perform the conversion.

```python
# Verification logic from examples/office_document_test.py
def check_libreoffice():
    import subprocess
    for cmd in ["libreoffice", "soffice"]:
        try:
            subprocess.run([cmd, "--version"], capture_output=True)
            return True
        except: continue
    return False
```

**Sources:** [examples/office_document_test.py:23-46](), [examples/office_document_test.py:75-81]()

---

## Enhanced Markdown-to-PDF Conversion

RAG-Anything provides an `EnhancedMarkdownConverter` that offers superior formatting compared to basic text-to-PDF utilities. It supports multiple backends like **WeasyPrint** and **Pandoc**.

### Implementation Architecture

```mermaid
graph TB
    subgraph "Input Processing"
        MD_Input["Markdown Content"]
        MD_Config["MarkdownConfig<br/>(page_size, margin, font_size)"]
    end

    subgraph "EnhancedMarkdownConverter"
        Ext["Markdown Extensions<br/>(tables, fenced_code, toc)"]
        CSS["_get_default_css()"]
        HTML["HTML Generation"]
    end

    subgraph "Backends"
        WP["WeasyPrint<br/>(Recommended)"]
        PAN["Pandoc<br/>(Complex Docs)"]
        RLB["ReportLab<br/>(Fallback)"]
    end

    MD_Input --> Ext
    MD_Config --> CSS
    Ext --> HTML
    CSS --> HTML
    
    HTML -->|"method='weasyprint'"| WP
    HTML -->|"method='pandoc'"| PAN
    HTML --> RLB
    
    WP --> PDF_Out["Professional PDF"]
    PAN --> PDF_Out
```

**Sources:** [raganything/enhanced_markdown.py:46-70](), [raganything/enhanced_markdown.py:72-111](), [raganything/enhanced_markdown.py:235-265]()

### Using the Enhanced Converter

The enhanced converter allows for custom CSS and professional typography (e.g., A4 page size, 1in margins).

```python
from raganything.enhanced_markdown import EnhancedMarkdownConverter, MarkdownConfig

config = MarkdownConfig(
    page_size="A4",
    include_toc=True,
    syntax_highlighting=True,
    custom_css="body { font-family: 'Georgia', serif; }"
)

converter = EnhancedMarkdownConverter(config)
success = converter.convert_markdown_to_pdf(
    markdown_content="# My Document\nContent here...",
    output_path="professional_output.pdf",
    method="weasyprint"
)
```

**Sources:** [raganything/enhanced_markdown.py:46-70](), [examples/enhanced_markdown_example.py:97-117](), [docs/enhanced_markdown.md:90-137]()

---

## Text and Markdown Processing

For basic text processing without the enhanced converter, the system uses `ReportLab` to wrap raw text into a PDF container.

```python
# Example from examples/text_format_test.py
async def test_text_parsing(file_path: str):
    # Requires ReportLab for .txt and .md to PDF conversion
    rag = RAGAnything()
    content_list, md_content = await rag.parse_document(
        file_path=file_path,
        parse_method="auto"
    )
    print(f"Extracted {len(content_list)} blocks from text file.")
```

**Sources:** [examples/text_format_test.py:38-84](), [requirements.txt:10-15]()

---

## Format-Specific Configuration Summary

| Format | Key Config / Dependency | Primary Code Entity |
|--------|-------------------------|---------------------|
| **PDF** | `mineru[core]` | `MineruParser` [raganything/parser.py:49]() |
| **DOCX** | `LibreOffice` | `convert_office_to_pdf` [raganything/parser.py:1188]() |
| **MD** | `weasyprint`, `markdown` | `EnhancedMarkdownConverter` [raganything/enhanced_markdown.py:72]() |
| **WEBP** | `Pillow` | `PIL.Image` conversion [examples/image_format_test.py:23]() |
| **TXT** | `reportlab` | `convert_text_to_pdf` [raganything/parser.py:230]() |

**Sources:** [requirements.txt:1-16](), [raganything/enhanced_markdown.py:21-43](), [examples/office_document_test.py:8-12]()

---

# Page: API Reference

# API Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [raganything/__init__.py](raganything/__init__.py)
- [raganything/raganything.py](raganything/raganything.py)

</details>



This page provides an overview of the RAG-Anything API structure and serves as a navigation guide to detailed API documentation in subsections. The API is organized into major component categories, each documented in detail in the following pages:

- **[RAGAnything Class](#10.1)** - Main orchestrator class and entry point.
- **[Configuration Classes](#10.2)** - API reference for `RAGAnythingConfig` and `ContextConfig`.
- **[Modal Processors API](#10.3)** - API reference for `BaseModalProcessor`, `ImageModalProcessor`, and others.
- **[Parser API](#10.4)** - API reference for `Parser` base class and backend implementations.
- **[Query Methods API](#10.5)** - API reference for `QueryMixin` methods and VLM-enhanced retrieval.
- **[Utilities API](#10.6)** - Helper functions for table formatting, equation extraction, and asset URLs.
- **[ProcessorMixin API](#10.7)** - Core document processing pipeline methods.
- **[BatchMixin API](#10.8)** - Batch and folder processing API.

---

## API Architecture

The RAG-Anything API follows a layered architecture with clear separation of concerns. The diagram below shows the main API components and their relationships, using actual class names and file locations.

**Diagram: API Layer Architecture with Code Entities**

```mermaid
graph TB
    subgraph "Entry Point"
        RAGAnything["RAGAnything<br/>[raganything/raganything.py]"]
    end
    
    subgraph "Configuration Layer"
        RAGAnythingConfig["RAGAnythingConfig<br/>[raganything/config.py]"]
        ContextConfig["ContextConfig<br/>[raganything/config.py]"]
    end
    
    subgraph "Processing Mixins"
        ProcessorMixin["ProcessorMixin<br/>[raganything/processor.py]"]
        QueryMixin["QueryMixin<br/>[raganything/query.py]"]
        BatchMixin["BatchMixin<br/>[raganything/batch.py]"]
    end
    
    subgraph "Modal Processing"
        BaseModalProcessor["BaseModalProcessor<br/>[raganything/modalprocessors.py]"]
        ImageModalProcessor["ImageModalProcessor<br/>[modalprocessors.py]"]
        TableModalProcessor["TableModalProcessor<br/>[modalprocessors.py]"]
        EquationModalProcessor["EquationModalProcessor<br/>[modalprocessors.py]"]
        GenericModalProcessor["GenericModalProcessor<br/>[modalprocessors.py]"]
        ContextExtractor["ContextExtractor<br/>[modalprocessors.py]"]
    end
    
    subgraph "Parsing Layer"
        Parser["Parser<br/>[raganything/parser.py]"]
        MineruParser["MineruParser<br/>[parser.py]"]
        DoclingParser["DoclingParser<br/>[parser.py]"]
        PaddleOCRParser["PaddleOCRParser<br/>[parser.py]"]
    end
    
    subgraph "Storage Integration"
        LightRAG["LightRAG<br/>[External Framework]"]
    end
    
    RAGAnything --> RAGAnythingConfig
    RAGAnything --> ProcessorMixin
    RAGAnything --> QueryMixin
    RAGAnything --> BatchMixin
    RAGAnything --> LightRAG
    
    ProcessorMixin --> Parser
    ProcessorMixin --> BaseModalProcessor
    
    BaseModalProcessor --> ImageModalProcessor
    BaseModalProcessor --> TableModalProcessor
    BaseModalProcessor --> EquationModalProcessor
    BaseModalProcessor --> GenericModalProcessor
    
    BaseModalProcessor --> ContextExtractor
    ContextExtractor --> ContextConfig
    
    Parser --> MineruParser
    Parser --> DoclingParser
    Parser --> PaddleOCRParser
    
    QueryMixin --> LightRAG
```

**Sources:** [raganything/raganything.py:50-51](), [raganything/__init__.py:1-60](), [raganything/processor.py:1-50]()

---

## Core API Interfaces

RAG-Anything exposes primary interfaces for different integration scenarios. For details on these methods, see [ProcessorMixin API](#10.7) and [Query Methods API](#10.5).

### Primary Interfaces

| Interface | File Location | Purpose | Entry Methods |
|-----------|---------------|---------|---------------|
| **Document Processing** | `raganything/processor.py` | Ingest and process documents | `process_document_complete()`, `insert_content_list()` |
| **Batch Processing** | `raganything/batch.py` | Folder and batch operations | `process_folder_complete()`, `process_documents_batch()` |
| **Query Interface** | `raganything/query.py` | Search and retrieve information | `aquery()`, `aquery_with_multimodal()` |
| **Modal Processing** | `raganything/modalprocessors.py` | Process specific content types | `ImageModalProcessor`, `TableModalProcessor` |

### Method Naming Conventions

| Pattern | Meaning | Example |
|---------|---------|---------|
| `a*` prefix | Async coroutine | `aquery()` [raganything/query.py:101]() |
| `*_complete` suffix | End-to-end pipeline | `process_document_complete()` [raganything/processor.py:213]() |
| `*_batch` suffix | Batch processing | `process_documents_batch()` [raganything/batch.py:84]() |

---

## Type System and Data Structures

The API uses consistent type definitions across all components. For a complete field-by-field reference, see [Configuration Classes](#10.2).

### Core Data Types

| Type Name | Python Type | Description | Example Value |
|-----------|-------------|-------------|---------------|
| `content_list` | `list[dict]` | Parsed document content | `[{"type": "text", "text": "...", "page_idx": 0}]` |
| `doc_id` | `str` | Content-based SHA256 hash | `"a3f2c8e4b6d9..."` |
| `modal_content` | `dict` | Modality-specific data | `{"img_path": "/path/img.jpg", "image_caption": ["..."]}` |

### Content List Structure

The `content_list` is the fundamental data structure produced by `Parser` implementations. Each element must contain `type` and `page_idx` fields.

**Diagram: Content List Schema with Types**

```mermaid
graph LR
    content_list["content_list<br/>list[dict]"]
    
    subgraph "Text Content"
        text_item["type: 'text'<br/>text: str<br/>page_idx: int"]
    end
    
    subgraph "Image Content"
        image_item["type: 'image'<br/>img_path: str<br/>image_caption: list[str]<br/>page_idx: int"]
    end
    
    subgraph "Table Content"
        table_item["type: 'table'<br/>table_body: str<br/>table_caption: list[str]<br/>page_idx: int"]
    end
    
    subgraph "Equation Content"
        equation_item["type: 'equation'<br/>latex: str<br/>text: str<br/>page_idx: int"]
    end
    
    content_list --> text_item
    content_list --> image_item
    content_list --> table_item
    content_list --> equation_item
```

**Sources:** [raganything/processor.py:260-350](), [raganything/modalprocessors.py:237-250]()

---

## Model Function Contracts

RAG-Anything requires three types of model functions with specific signatures. For implementation examples, see [Model Provider Configuration](#8.4).

### Required Function Signatures

**Diagram: Model Function Interfaces and Call Patterns**

```mermaid
graph TB
    subgraph "Function Interfaces"
        LLM_FUNC["llm_model_func<br/>Text generation"]
        VISION_FUNC["vision_model_func<br/>Image analysis"]
        EMBED_FUNC["embedding_func<br/>Vector generation"]
    end
    
    subgraph "Call Contexts"
        TEXT_GEN["Text Generation<br/>Entity extraction"]
        IMAGE_CAP["Image Captioning<br/>Visual understanding"]
        VLM_QUERY["VLM Enhanced Query<br/>Multimodal messages"]
    end
    
    subgraph "Parameters"
        LLM_PARAMS["prompt: str<br/>system_prompt: str<br/>history_messages: list"]
        VISION_PARAMS["prompt: str<br/>image_data: str (base64)<br/>messages: list (optional)"]
        EMBED_PARAMS["texts: list[str]<br/>Returns: list[list[float]]"]
    end
    
    LLM_FUNC --> TEXT_GEN
    VISION_FUNC --> IMAGE_CAP
    VISION_FUNC --> VLM_QUERY
    EMBED_FUNC --> VECTOR_GEN
    
    TEXT_GEN --> LLM_PARAMS
    IMAGE_CAP --> VISION_PARAMS
    VLM_QUERY --> VISION_PARAMS
    VECTOR_GEN --> EMBED_PARAMS
```

### LLM Model Function
Used by `ProcessorMixin` for entity extraction and `TableModalProcessor` for analysis.
```python
def llm_model_func(prompt: str, system_prompt: str = None, history_messages: list = [], **kwargs) -> str
```
**Sources:** [raganything/raganything.py:59-60](), [raganything/modalprocessors.py:534-540]()

### Vision Model Function
Used by `ImageModalProcessor` for captioning and `QueryMixin` for VLM-enhanced queries.
```python
def vision_model_func(prompt: str, system_prompt: str = None, image_data: str = None, messages: list = None, **kwargs) -> str
```
**Sources:** [raganything/raganything.py:62-63](), [raganything/query.py:246-260]()

---

## Error Handling and Status Tracking

RAG-Anything tracks the state of document processing in `doc_status_storage`. For details on the caching mechanism, see [Parse Caching System](#4.3).

| State | Meaning |
|-------|---------|
| `READY` | Document recognized, processing not started. |
| `HANDLING` | Document currently being parsed or indexed. |
| `PROCESSED` | Document successfully indexed in Knowledge Graph. |
| `FAILED` | Processing terminated due to error. |

**Sources:** [raganything/processor.py:220-240](), [raganything/raganything.py:97-98]()

---

# Page: RAGAnything Class

# RAGAnything Class

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [raganything/__init__.py](raganything/__init__.py)
- [raganything/raganything.py](raganything/raganything.py)

</details>



**Purpose**: This page documents the `RAGAnything` class, which serves as the central orchestrator and entry point for the RAG-Anything system. It coordinates document parsing, multimodal content processing, knowledge graph construction, and query execution.

**Scope**: This page covers the class structure, initialization patterns, core components, and lifecycle management. For detailed API documentation of specific methods, see:
- Processing methods: [ProcessorMixin API](#10.7)
- Query methods: [Query Methods API](#10.5)
- Batch processing methods: [BatchMixin API](#10.8)

**Related Pages**: For configuration details, see [RAGAnythingConfig](#8.1). For architectural context, see [Component Overview](#3.1).

---

## Class Structure

The `RAGAnything` class is implemented as a Python dataclass that inherits functionality from three mixins, providing a modular architecture for different operational concerns.

**Class Definition Structure**

```mermaid
classDiagram
    class RAGAnything {
        +LightRAG lightrag
        +Callable llm_model_func
        +Callable vision_model_func
        +Callable embedding_func
        +RAGAnythingConfig config
        +Dict lightrag_kwargs
        +Dict modal_processors
        +ContextExtractor context_extractor
        +Any parse_cache
        +bool _parser_installation_checked
        +__post_init__()
        +close()
        +_ensure_lightrag_initialized()
        +finalize_storages()
        +update_config()
        +get_config_info()
        +get_processor_info()
    }
    
    class QueryMixin {
        +aquery()
        +query()
        +aquery_with_multimodal()
        +query_with_multimodal()
        +aquery_vlm_enhanced()
    }
    
    class ProcessorMixin {
        +parse_document()
        +process_document_complete()
        +insert_content_list()
        +get_document_status()
        +update_document_status()
    }
    
    class BatchMixin {
        +process_folder_complete()
        +process_documents_batch()
        +process_documents_with_rag_batch()
    }
    
    class LightRAG {
        +working_dir
        +llm_model_func
        +embedding_func
        +initialize_storages()
        +finalize_storages()
    }
    
    class RAGAnythingConfig {
        +working_dir
        +parser
        +parse_method
        +enable_image_processing
        +enable_table_processing
        +enable_equation_processing
    }
    
    RAGAnything --|> QueryMixin : inherits
    RAGAnything --|> ProcessorMixin : inherits
    RAGAnything --|> BatchMixin : inherits
    RAGAnything --> LightRAG : uses
    RAGAnything --> RAGAnythingConfig : configured by
```

**Sources**: [raganything/raganything.py:50-586]()

---

## Core Components and Fields

The `RAGAnything` class manages several key components through its fields:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `lightrag` | `Optional[LightRAG]` | `None` | Optional pre-initialized LightRAG instance. If not provided, will be created during initialization. [raganything/raganything.py:56-57]() |
| `llm_model_func` | `Optional[Callable]` | `None` | LLM model function for text analysis. Required if `lightrag` is not provided. [raganything/raganything.py:59-60]() |
| `vision_model_func` | `Optional[Callable]` | `None` | Vision model function for image analysis. Optional, but required for image processing. [raganything/raganything.py:62-63]() |
| `embedding_func` | `Optional[Callable]` | `None` | Embedding function for text vectorization. Required if `lightrag` is not provided. [raganything/raganything.py:65-66]() |
| `config` | `Optional[RAGAnythingConfig]` | `None` | Configuration object. If not provided, created from environment variables. [raganything/raganything.py:68-69]() |
| `lightrag_kwargs` | `Dict[str, Any]` | `{}` | Additional keyword arguments for LightRAG initialization. [raganything/raganything.py:73-84]() |
| `modal_processors` | `Dict[str, Any]` | `{}` (auto-initialized) | Dictionary mapping content types to modal processors. [raganything/raganything.py:88-89]() |
| `context_extractor` | `Optional[ContextExtractor]` | `None` (auto-initialized) | Context extractor for providing surrounding content. [raganything/raganything.py:91-92]() |
| `parse_cache` | `Optional[Any]` | `None` (auto-initialized) | Parse result cache storage using LightRAG KV storage. [raganything/raganything.py:94-95]() |
| `callback_manager` | `CallbackManager` | `CallbackManager()` | Manager for processing hooks and observability. [raganything/raganything.py:100-103]() |

**Additional Attributes Set During Initialization:**
- `working_dir` (str): Set from `config.working_dir` [raganything/raganything.py:115-115]()
- `logger` (Logger): Uses LightRAG's logger instance [raganything/raganything.py:118-118]()
- `doc_parser` (Parser): Initialized via `get_parser(self.config.parser)` [raganything/raganything.py:121-121]()

**Sources**: [raganything/raganything.py:49-106]()

---

## Initialization Patterns

The `RAGAnything` class supports multiple initialization patterns to accommodate different use cases.

**Component Initialization Flow**

```mermaid
flowchart TD
    START["RAGAnything.__init__()"] --> POST_INIT["__post_init__()"]
    
    POST_INIT --> CONFIG_CHECK{"config<br/>provided?"}
    CONFIG_CHECK -->|No| CREATE_CONFIG["Create RAGAnythingConfig<br/>from environment"]
    CONFIG_CHECK -->|Yes| USE_CONFIG["Use provided config"]
    CREATE_CONFIG --> SETUP_PARSER
    USE_CONFIG --> SETUP_PARSER
    
    SETUP_PARSER["Setup doc_parser<br/>get_parser(config.parser)"] --> REG_CLEANUP["Register atexit cleanup<br/>atexit.register(close)"]
    
    REG_CLEANUP --> CREATE_DIR["Create working_dir<br/>if not exists"]
    
    CREATE_DIR --> LOG_CONFIG["Log configuration info"]
    
    LOG_CONFIG --> FIRST_USE["First method call<br/>(parse, query, etc.)"]
    
    FIRST_USE --> ENSURE_INIT["_ensure_lightrag_initialized()"]
    
    ENSURE_INIT --> CHECK_PARSER{"Parser<br/>installed?"}
    CHECK_PARSER -->|No| PARSER_ERROR["Return error:<br/>'Parser not installed'"]
    CHECK_PARSER -->|Yes| LIGHTRAG_CHECK{"lightrag<br/>provided?"}
    
    LIGHTRAG_CHECK -->|Yes| INHERIT["Inherit model functions<br/>from LightRAG"]
    LIGHTRAG_CHECK -->|No| VALIDATE["Validate required<br/>functions provided"]
    
    INHERIT --> INIT_STORAGE["Initialize LightRAG storages<br/>initialize_storages()"]
    VALIDATE --> CREATE_LIGHTRAG["Create new LightRAG<br/>with llm_model_func,<br/>embedding_func,<br/>lightrag_kwargs"]
    
    CREATE_LIGHTRAG --> INIT_STORAGE
    
    INIT_STORAGE --> INIT_CACHE["Initialize parse_cache<br/>key_string_value_json_storage"]
    
    INIT_CACHE --> INIT_PROCESSORS["_initialize_processors()"]
    
    INIT_PROCESSORS --> CREATE_CONTEXT["Create ContextExtractor<br/>with tokenizer from LightRAG"]
    
    CREATE_CONTEXT --> CREATE_MODAL["Create modal processors:<br/>ImageModalProcessor,<br/>TableModalProcessor,<br/>EquationModalProcessor,<br/>GenericModalProcessor"]
    
    CREATE_MODAL --> READY["System Ready"]
    
    PARSER_ERROR --> END["End with error"]
    READY --> END["End successfully"]
```

**Sources**: [raganything/raganything.py:108-142](), [raganything/raganything.py:177-221](), [raganything/raganything.py:231-369]()

### Pattern 1: Full Initialization (Recommended)

When you have all model functions and want RAGAnything to create the LightRAG instance:

```python
from raganything import RAGAnything, RAGAnythingConfig

config = RAGAnythingConfig(
    working_dir="./rag_storage",
    parser="mineru",
    enable_image_processing=True
)

rag = RAGAnything(
    config=config,
    llm_model_func=your_llm_function,
    vision_model_func=your_vision_function,
    embedding_func=your_embedding_function
)
```

**Sources**: [raganything/raganything.py:50-84]()

### Pattern 2: Pre-Initialized LightRAG

When you have an existing LightRAG instance and want to add multimodal capabilities:

```python
from lightrag import LightRAG
from raganything import RAGAnything

lightrag_instance = LightRAG(working_dir="./existing_rag")
# ... model funcs set on lightrag_instance ...

rag = RAGAnything(
    lightrag=lightrag_instance,
    vision_model_func=your_vision_function
)
```

**Sources**: [raganything/raganything.py:255-263]()

---

## Component Coordination

The `RAGAnything` class orchestrates the interaction between multiple subsystems:

**Component Communication Diagram**

```mermaid
graph TB
    subgraph "RAGAnything Instance"
        CONFIG["config:<br/>RAGAnythingConfig"]
        DOC_PARSER["doc_parser:<br/>Parser (e.g. MineruParser)"]
        LIGHTRAG_INST["lightrag:<br/>LightRAG"]
        PARSE_CACHE["parse_cache:<br/>KVStorage&lt;parse_cache&gt;"]
        CONTEXT_EXT["context_extractor:<br/>ContextExtractor"]
        
        subgraph "modal_processors Dict"
            IMG_PROC["'image':<br/>ImageModalProcessor"]
            TBL_PROC["'table':<br/>TableModalProcessor"]
            EQ_PROC["'equation':<br/>EquationModalProcessor"]
            GEN_PROC["'generic':<br/>GenericModalProcessor"]
        end
    end
    
    subgraph "Mixin Methods"
        PROCESSOR_MIXIN["ProcessorMixin:<br/>parse_document()<br/>process_document_complete()"]
        QUERY_MIXIN["QueryMixin:<br/>aquery()<br/>aquery_with_multimodal()"]
        BATCH_MIXIN["BatchMixin:<br/>process_folder_complete()"]
    end
    
    CONFIG --> DOC_PARSER
    PROCESSOR_MIXIN --> DOC_PARSER
    PROCESSOR_MIXIN --> PARSE_CACHE
    PROCESSOR_MIXIN --> LIGHTRAG_INST
    
    PROCESSOR_MIXIN --> IMG_PROC
    PROCESSOR_MIXIN --> TBL_PROC
    PROCESSOR_MIXIN --> EQ_PROC
    
    CONTEXT_EXT --> IMG_PROC
    CONTEXT_EXT --> TBL_PROC
    
    IMG_PROC --> LIGHTRAG_INST
    TBL_PROC --> LIGHTRAG_INST
    
    QUERY_MIXIN --> LIGHTRAG_INST
    BATCH_MIXIN --> PROCESSOR_MIXIN
```

**Sources**: [raganything/raganything.py:177-221](), [raganything/raganything.py:493-519]()

---

## Key Methods

### Initialization and Setup

#### `__post_init__()`
Called automatically after dataclass initialization. Sets up the working directory, logger, document parser, and registers cleanup handlers via `atexit.register(self.close)`. [raganything/raganything.py:108-142]()

#### `_ensure_lightrag_initialized()`
Ensures LightRAG instance and storages are initialized before any processing or query operations. This method handles deferred initialization, creates the `parse_cache` and `multimodal_status_cache`, and triggers `_initialize_processors()`. [raganything/raganything.py:231-369]()

#### `_initialize_processors()`
Creates modal processor instances based on configuration flags (e.g., `ImageModalProcessor` if `config.enable_image_processing` is True). [raganything/raganything.py:177-221]()

### Configuration Management

#### `update_config(**kwargs)`
Updates configuration with new values at runtime by applying `setattr` to the internal `config` object. [raganything/raganything.py:222-229]()

#### `update_context_config(**context_kwargs)`
Updates context extraction configuration (like `context_window` or `max_context_tokens`) and recreates the `context_extractor` for all modal processors. [raganything/raganything.py:521-551]()

#### `set_content_source_for_context(content_source, content_format="auto")`
Sets the source content (full document or list of chunks) for context extraction in all modal processors. [raganything/raganything.py:493-519]()

### Information Retrieval

#### `get_config_info()`
Returns a comprehensive dictionary of current configuration settings, including directory paths, parsing methods, and multimodal flags. [raganything/raganything.py:437-491]()

#### `get_processor_info()`
Returns information about initialized processors and their capabilities, including model function availability and parser installation status. [raganything/raganything.py:553-585]()

### Parser Verification

#### `check_parser_installation()`
Checks if the configured parser is properly installed. [raganything/raganything.py:417-424]()

#### `verify_parser_installation_once()`
Verifies parser installation once and caches the result to avoid redundant checks. Raises `RuntimeError` if the parser is missing. [raganything/raganything.py:426-435]()

---

## Lifecycle Management

### Automatic Cleanup
The `close()` method is registered with `atexit` to ensure cleanup on program exit. [raganything/raganything.py:124-124]()

The `close()` method handles three scenarios:
1. Inside a running async context (e.g., FastAPI shutdown) -> schedules `finalize_storages`. [raganything/raganything.py:160-161]()
2. No event loop in thread -> creates one with `asyncio.run(self.finalize_storages())`. [raganything/raganything.py:172-172]()
3. Event loop exists but is closed -> cleans up and runs a fresh loop. [raganything/raganything.py:166-172]()

### `finalize_storages()`
Finalizes all storage components concurrently, including `parse_cache`, `multimodal_status_cache`, and the underlying `lightrag` storages. [raganything/raganything.py:371-415]()

**Sources**: [raganything/raganything.py:143-176](), [raganything/raganything.py:371-415]()

---

# Page: Configuration Classes

# Configuration Classes

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [raganything/config.py](raganything/config.py)
- [raganything/modalprocessors.py](raganything/modalprocessors.py)

</details>



This page provides comprehensive API reference documentation for the configuration classes used in RAG-Anything. These classes define the configurable parameters for document processing, multimodal content handling, and context extraction.

For information about configuring storage backends and model providers, see [Storage Backend Configuration](#8.3) and [Model Provider Configuration](#8.4). For environment variable reference, see [Environment Variables](#8.2).

## Overview

RAG-Anything uses two primary configuration classes:

- **`RAGAnythingConfig`**: Main configuration class that controls global settings for parsing, processing, and batch operations.
- **`ContextConfig`**: Specialized configuration for context extraction behavior in modal processors.

Both classes are implemented as Python dataclasses with built-in support for environment variable overrides, providing flexibility for different deployment scenarios.

---

## Configuration Class Hierarchy

```mermaid
graph TB
    subgraph "Configuration Layer"
        EnvVars["Environment Variables<br/>.env file or shell"]
        RAGConfig["RAGAnythingConfig<br/>raganything/config.py"]
        ContextConfig["ContextConfig<br/>raganything/modalprocessors.py"]
    end
    
    subgraph "System Components"
        RAGAnything["RAGAnything<br/>Core System"]
        ContextExtractor["ContextExtractor<br/>Context Extraction"]
        ModalProcessors["BaseModalProcessor<br/>+ Subclasses"]
    end
    
    EnvVars --> RAGConfig
    EnvVars --> ContextConfig
    
    RAGConfig --> RAGAnything
    RAGConfig --> ContextConfig
    ContextConfig --> ContextExtractor
    ContextExtractor --> ModalProcessors
    
    RAGAnything --> ModalProcessors
```

**Sources:** [raganything/config.py:12-153](), [raganything/modalprocessors.py:33-47]()

---

## RAGAnythingConfig

The `RAGAnythingConfig` class is the primary configuration object for RAG-Anything, controlling document parsing, multimodal processing, batch operations, and context extraction.

### Class Definition

```python
@dataclass
class RAGAnythingConfig:
    """Configuration class for RAGAnything with environment variable support"""
```

**Location:** [raganything/config.py:12-14]()

### Configuration Categories

The configuration parameters are organized into seven logical categories:

```mermaid
graph LR
    RAGConfig["RAGAnythingConfig"]
    
    Directory["Directory Configuration<br/>working_dir"]
    Parser["Parser Configuration<br/>parse_method, parser_output_dir<br/>parser, display_content_stats"]
    Multimodal["Multimodal Processing<br/>enable_image_processing<br/>enable_table_processing<br/>enable_equation_processing"]
    Batch["Batch Processing<br/>max_concurrent_files<br/>supported_file_extensions<br/>recursive_folder_processing"]
    Context["Context Extraction<br/>context_window, context_mode<br/>max_context_tokens, etc."]
    Path["Path Handling<br/>use_full_path"]
    
    RAGConfig --> Directory
    RAGConfig --> Parser
    RAGConfig --> Multimodal
    RAGConfig --> Batch
    RAGConfig --> Context
    RAGConfig --> Path
```

**Sources:** [raganything/config.py:15-110]()

---

### Directory Configuration

| Field | Type | Default | Environment Variable | Description |
|-------|------|---------|---------------------|-------------|
| `working_dir` | `str` | `"./rag_storage"` | `WORKING_DIR` | Directory where RAG storage and cache files are stored |

**Source:** [raganything/config.py:18-19]()

---

### Parser Configuration

| Field | Type | Default | Environment Variable | Description |
|-------|------|---------|---------------------|-------------|
| `parse_method` | `str` | `"auto"` | `PARSE_METHOD` | Default parsing method: `"auto"`, `"ocr"`, or `"txt"` |
| `parser_output_dir` | `str` | `"./output"` | `OUTPUT_DIR` | Default output directory for parsed content |
| `parser` | `str` | `"mineru"` | `PARSER` | Parser backend: `"mineru"`, `"docling"`, or `"paddleocr"` |
| `display_content_stats` | `bool` | `True` | `DISPLAY_CONTENT_STATS` | Whether to display content statistics during parsing |

**Notes:**
- `parse_method` controls how the selected parser processes documents.
- `parser` selects which backend parser implementation to use.
- Legacy environment variable `MINERU_PARSE_METHOD` is supported but deprecated [raganything/config.py:120-129]().

**Source:** [raganything/config.py:21-35]()

---

### Multimodal Processing Configuration

| Field | Type | Default | Environment Variable | Description |
|-------|------|---------|---------------------|-------------|
| `enable_image_processing` | `bool` | `True` | `ENABLE_IMAGE_PROCESSING` | Enable image content processing |
| `enable_table_processing` | `bool` | `True` | `ENABLE_TABLE_PROCESSING` | Enable table content processing |
| `enable_equation_processing` | `bool` | `True` | `ENABLE_EQUATION_PROCESSING` | Enable equation content processing |

**Notes:**
- These flags control whether modal processors are invoked during document processing.
- Disabling processing for specific modalities improves performance when those content types are not needed.

**Source:** [raganything/config.py:37-52]()

---

### Batch Processing Configuration

| Field | Type | Default | Environment Variable | Description |
|-------|------|---------|---------------------|-------------|
| `max_concurrent_files` | `int` | `1` | `MAX_CONCURRENT_FILES` | Maximum number of files to process concurrently |
| `supported_file_extensions` | `List[str]` | (see below) | `SUPPORTED_FILE_EXTENSIONS` | List of supported file extensions |
| `recursive_folder_processing` | `bool` | `True` | `RECURSIVE_FOLDER_PROCESSING` | Whether to recursively process subfolders in batch mode |

**Default Supported Extensions:**
`.pdf, .jpg, .jpeg, .png, .bmp, .tiff, .tif, .gif, .webp, .doc, .docx, .ppt, .pptx, .xls, .xlsx, .txt, .md` [raganything/config.py:65-69]()

**Source:** [raganything/config.py:54-73]()

---

### Context Extraction Configuration

These parameters control how surrounding content is extracted and included during multimodal content processing.

| Field | Type | Default | Environment Variable | Description |
|-------|------|---------|---------------------|-------------|
| `context_window` | `int` | `1` | `CONTEXT_WINDOW` | Number of pages/chunks to include before and after current item |
| `context_mode` | `str` | `"page"` | `CONTEXT_MODE` | Context extraction mode: `"page"` or `"chunk"` |
| `max_context_tokens` | `int` | `2000` | `MAX_CONTEXT_TOKENS` | Maximum number of tokens in extracted context |
| `include_headers` | `bool` | `True` | `INCLUDE_HEADERS` | Whether to include document headers and titles |
| `include_captions` | `bool` | `True` | `INCLUDE_CAPTIONS` | Whether to include image/table captions |
| `context_filter_content_types` | `List[str]` | `["text"]` | `CONTEXT_FILTER_CONTENT_TYPES` | Content types to include (comma-separated) |
| `content_format` | `str` | `"minerU"` | `CONTENT_FORMAT` | Default content format for context extraction |

**Source:** [raganything/config.py:75-110]()

---

### Path Handling Configuration

| Field | Type | Default | Environment Variable | Description |
|-------|------|---------|---------------------|-------------|
| `use_full_path` | `bool` | `False` | `USE_FULL_PATH` | Whether to use full file path (`True`) or just basename (`False`) |

**Source:** [raganything/config.py:113-115]()

---

### Backward Compatibility

The class includes support for legacy environment variables via `__post_init__` and deprecated property accessors.

```mermaid
graph LR
    Legacy["MINERU_PARSE_METHOD<br/>(deprecated)"]
    Current["PARSE_METHOD"]
    Field["parse_method"]
    
    Legacy -.fallback.-> Field
    Current --> Field
    
    Property["mineru_parse_method<br/>(deprecated property)"]
    Property -.alias.-> Field
```

**Source:** [raganything/config.py:117-159]()

---

## ContextConfig

The `ContextConfig` class provides fine-grained control over context extraction behavior for modal processors. It is used by the `ContextExtractor` class.

### Class Definition

```python
@dataclass
class ContextConfig:
    """Configuration for context extraction"""
```

**Location:** [raganything/modalprocessors.py:39-41]()

### Configuration Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `context_window` | `int` | `1` | Window size for context extraction |
| `context_mode` | `str` | `"page"` | Extraction mode: `"page"`, `"chunk"`, or `"token"` |
| `max_context_tokens` | `int` | `2000` | Maximum tokens to include in extracted context |
| `include_headers` | `bool` | `True` | Whether to include headers/titles |
| `include_captions` | `bool` | `True` | Whether to include image/table captions |
| `filter_content_types` | `List[str]` | `["text"]` | Content types to include in context |

**Source:** [raganything/modalprocessors.py:43-52]()

---

### Context Extraction Modes

```mermaid
graph TB
    ContextConfig["ContextConfig<br/>context_mode"]
    
    PageMode["page mode<br/>±N pages from current"]
    ChunkMode["chunk mode<br/>±N chunks from current"]
    TokenMode["token mode<br/>up to max_context_tokens"]
    
    ContextConfig --> PageMode
    ContextConfig --> ChunkMode
    ContextConfig --> TokenMode
    
    PageExtract["_extract_page_context<br/>raganything/modalprocessors.py"]
    ChunkExtract["_extract_chunk_context<br/>raganything/modalprocessors.py"]
    Truncate["_truncate_context<br/>raganything/modalprocessors.py"]
    
    PageMode --> PageExtract
    ChunkMode --> ChunkExtract
    PageExtract --> Truncate
    ChunkExtract --> Truncate
    TokenMode --> Truncate
```

**Sources:** [raganything/modalprocessors.py:132-204]()

---

## Usage in System Components

### Configuration Flow Through System

```mermaid
graph TB
    subgraph "Initialization"
        EnvFile[".env File"]
        RAGConfigInit["RAGAnythingConfig()<br/>raganything/config.py"]
    end
    
    subgraph "Core System"
        RAGAnything["RAGAnything.__init__<br/>config: RAGAnythingConfig"]
        ContextConfigCreate["Create ContextConfig<br/>from config fields"]
        ContextExtractorInit["ContextExtractor<br/>raganything/modalprocessors.py"]
    end
    
    subgraph "Modal Processing"
        BaseModalInit["BaseModalProcessor.__init__"]
        ImageProc["ImageModalProcessor"]
        TableProc["TableModalProcessor"]
        EquationProc["EquationModalProcessor"]
    end
    
    EnvFile --> RAGConfigInit
    RAGConfigInit --> RAGAnything
    RAGAnything --> ContextConfigCreate
    ContextConfigCreate --> ContextExtractorInit
    ContextExtractorInit --> BaseModalInit
    BaseModalInit --> ImageProc
    BaseModalInit --> TableProc
    BaseModalInit --> EquationProc
```

**Sources:** [raganything/config.py:12-153](), [raganything/modalprocessors.py:58-66]()

---

### Environment Variable Loading

The configuration system uses `lightrag.utils.get_env_value` for environment variable support with type coercion.

```mermaid
graph TB
    EnvSource["Environment Variable<br/>(e.g., CONTEXT_WINDOW=2)"]
    GetEnvValue["get_env_value<br/>lightrag/utils.py"]
    DefaultValue["Default Value<br/>(1)"]
    TypeCoercion["Type Coercion<br/>(int)"]
    FieldValue["context_window: int = 2"]
    
    EnvSource --> GetEnvValue
    DefaultValue -.fallback.-> GetEnvValue
    GetEnvValue --> TypeCoercion
    TypeCoercion --> FieldValue
```

**Sources:** [raganything/config.py:9-107]()

---

## Related Pages

- **[Environment Variables](#8.2)**: Complete environment variable reference.
- **[Context Extraction](#5.6)**: Detailed explanation of the context extraction system.
- **[RAGAnything Class](#10.1)**: Main class that uses these configuration objects.

**Sources:** [raganything/config.py:1-159](), [raganything/modalprocessors.py:33-52]()

---

# Page: Modal Processors API

# Modal Processors API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [raganything/modalprocessors.py](raganything/modalprocessors.py)

</details>



## Purpose and Scope

This page provides comprehensive API documentation for the modal processor classes in RAG-Anything. Modal processors are responsible for analyzing and processing multimodal content types (images, tables, equations, and custom content) and integrating them into the knowledge graph.

For architectural overview and design patterns of modal processors, see [Modal Processor Architecture](#5.1). For implementation details of specific processors, see [Image Processing](#5.2), [Table Processing](#5.3), [Equation Processing](#5.4), and [Custom Modal Processors](#5.5). For context extraction concepts, see [Context Extraction](#5.6).

This page documents:
- Class constructors and initialization parameters
- Public methods with signatures, parameters, and return types
- Configuration classes and data structures
- Internal utility methods
- Usage patterns and integration points

---

## Class Hierarchy

```mermaid
classDiagram
    class BaseModalProcessor {
        +LightRAG lightrag
        +modal_caption_func
        +ContextExtractor context_extractor
        +content_source
        +content_format
        +set_content_source(content_source, content_format)
        +generate_description_only(modal_content, content_type, item_info, entity_name)*
        +process_multimodal_content(modal_content, content_type, file_path, entity_name, item_info, batch_mode, doc_id, chunk_order_index)*
        -_get_context_for_item(item_info)
        -_create_entity_and_chunk(modal_chunk, entity_info, file_path, batch_mode, doc_id, chunk_order_index)
        -_process_chunk_for_extraction(chunk_id, modal_entity_name, batch_mode)
        -_robust_json_parse(response)
    }
    
    class ImageModalProcessor {
        -_encode_image_to_base64(image_path)
        +generate_description_only(modal_content, content_type, item_info, entity_name)
        +process_multimodal_content(modal_content, content_type, file_path, entity_name, item_info, batch_mode, doc_id, chunk_order_index)
        -_parse_response(response, entity_name)
    }
    
    class TableModalProcessor {
        +generate_description_only(modal_content, content_type, item_info, entity_name)
        +process_multimodal_content(modal_content, content_type, file_path, entity_name, item_info, batch_mode, doc_id, chunk_order_index)
        -_parse_table_response(response, entity_name)
    }
    
    class EquationModalProcessor {
        +generate_description_only(modal_content, content_type, item_info, entity_name)
        +process_multimodal_content(modal_content, content_type, file_path, entity_name, item_info, batch_mode, doc_id, chunk_order_index)
        -_parse_equation_response(response, entity_name)
    }
    
    class GenericModalProcessor {
        +generate_description_only(modal_content, content_type, item_info, entity_name)
        +process_multimodal_content(modal_content, content_type, file_path, entity_name, item_info, batch_mode, doc_id, chunk_order_index)
        -_parse_generic_response(response, entity_name, content_type)
    }
    
    class ContextExtractor {
        +ContextConfig config
        +tokenizer
        +extract_context(content_source, current_item_info, content_format)
        -_extract_from_content_list(content_list, current_item_info)
        -_extract_page_context(content_list, current_item_info)
        -_extract_chunk_context(content_list, current_item_info)
        -_truncate_context(context)
    }
    
    class ContextConfig {
        +int context_window
        +str context_mode
        +int max_context_tokens
        +bool include_headers
        +bool include_captions
        +List filter_content_types
    }
    
    BaseModalProcessor <|-- ImageModalProcessor
    BaseModalProcessor <|-- TableModalProcessor
    BaseModalProcessor <|-- EquationModalProcessor
    BaseModalProcessor <|-- GenericModalProcessor
    BaseModalProcessor o-- ContextExtractor
    ContextExtractor o-- ContextConfig
```

**Sources:** [raganything/modalprocessors.py:39-1570]()

---

## Configuration Classes

### ContextConfig

`ContextConfig` is a dataclass that controls context extraction behavior for multimodal content processing.

**Class Definition:** [raganything/modalprocessors.py:39-53]()

#### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `context_window` | `int` | `1` | Number of pages/chunks before and after current item to include |
| `context_mode` | `str` | `"page"` | Context extraction mode: `"page"`, `"chunk"`, or `"token"` |
| `max_context_tokens` | `int` | `2000` | Maximum number of tokens in extracted context |
| `include_headers` | `bool` | `True` | Whether to include document headers/titles in context |
| `include_captions` | `bool` | `True` | Whether to include image/table captions in context |
| `filter_content_types` | `List[str]` | `["text"]` | Content types to include (e.g., `["text"]`, `["text", "image"]`) |

#### Example Usage

```python
from raganything.modalprocessors import ContextConfig

# Default configuration
config = ContextConfig()

# Custom configuration for wider context
config = ContextConfig(
    context_window=2,
    context_mode="page",
    max_context_tokens=4000,
    include_headers=True,
    include_captions=True,
    filter_content_types=["text", "image"]
)
```

**Sources:** [raganything/modalprocessors.py:39-53]()

---

## ContextExtractor Class

The `ContextExtractor` class extracts surrounding context for multimodal content to enable context-aware processing.

**Class Definition:** [raganything/modalprocessors.py:55-358]()

### Constructor

```python
def __init__(self, config: ContextConfig = None, tokenizer=None)
```

**Parameters:**
- `config` (`ContextConfig`, optional): Configuration for context extraction. If `None`, uses default `ContextConfig()`.
- `tokenizer` (optional): Tokenizer instance for accurate token counting. If `None`, falls back to character-based truncation.

**Sources:** [raganything/modalprocessors.py:58-66]()

### Methods

#### extract_context()

```python
def extract_context(
    self,
    content_source: Any,
    current_item_info: Dict[str, Any],
    content_format: str = "auto"
) -> str
```

Extract context for the current item from a content source.

**Parameters:**
- `content_source` (`Any`): Source content in various formats (list, dict, or string)
- `current_item_info` (`Dict[str, Any]`): Information about the current item:
  - `page_idx` (`int`): Page index for page-based extraction
  - `index` (`int`): Chunk index for chunk-based extraction
- `content_format` (`str`): Format hint: `"auto"`, `"minerU"`, `"text_chunks"`, or `"text"`

**Returns:**
- `str`: Extracted and truncated context text

**Sources:** [raganything/modalprocessors.py:68-118]()

#### Internal Methods

| Method | Purpose | Line Reference |
|--------|---------|----------------|
| `_extract_from_content_list()` | Extract from MinerU-style content list | [raganything/modalprocessors.py:120-137]() |
| `_extract_page_context()` | Extract context based on page boundaries | [raganything/modalprocessors.py:139-177]() |
| `_extract_chunk_context()` | Extract context based on chunk boundaries | [raganything/modalprocessors.py:179-210]() |
| `_extract_text_from_item()` | Extract text from a content item | [raganything/modalprocessors.py:212-242]() |
| `_extract_from_dict_source()` | Extract from dictionary source | [raganything/modalprocessors.py:244-269]() |
| `_extract_from_text_source()` | Extract from plain text | [raganything/modalprocessors.py:271-283]() |
| `_extract_from_text_chunks()` | Extract from text chunk list | [raganything/modalprocessors.py:285-312]() |
| `_truncate_context()` | Truncate to max token limit | [raganything/modalprocessors.py:314-357]() |

**Sources:** [raganything/modalprocessors.py:120-357]()

---

## BaseModalProcessor Class

`BaseModalProcessor` is the abstract base class for all modal processors, providing common infrastructure for multimodal content processing.

**Class Definition:** [raganything/modalprocessors.py:360-794]()

### Constructor

```python
def __init__(
    self,
    lightrag: LightRAG,
    modal_caption_func,
    context_extractor: ContextExtractor = None
)
```

**Parameters:**
- `lightrag` (`LightRAG`): LightRAG instance providing storage and model functions
- `modal_caption_func` (callable): Async function for generating descriptions. Signature:
  ```python
  async def modal_caption_func(
      prompt: str,
      image_data: str = None,
      system_prompt: str = None
  ) -> str
  ```
- `context_extractor` (`ContextExtractor`, optional): Context extractor instance. If `None`, creates default instance.

**Initialized Attributes:**
- `self.lightrag`: LightRAG instance reference
- `self.modal_caption_func`: Caption generation function
- `self.text_chunks_db`: Text chunks storage from LightRAG
- `self.chunks_vdb`: Chunk vector database from LightRAG
- `self.entities_vdb`: Entity vector database from LightRAG
- `self.relationships_vdb`: Relationship vector database from LightRAG
- `self.knowledge_graph_inst`: Knowledge graph storage from LightRAG
- `self.embedding_func`: Embedding function from LightRAG
- `self.llm_model_func`: LLM function from LightRAG
- `self.global_config`: LightRAG configuration dictionary
- `self.hashing_kv`: LLM response cache from LightRAG
- `self.tokenizer`: Tokenizer from LightRAG
- `self.context_extractor`: Context extractor instance
- `self.content_source`: Content source for context extraction (initially `None`)
- `self.content_format`: Content format hint (initially `"auto"`)

**Sources:** [raganything/modalprocessors.py:363-404]()

### Public Methods

#### set_content_source()

```python
def set_content_source(self, content_source: Any, content_format: str = "auto")
```

Set the content source for context extraction in batch processing.

**Parameters:**
- `content_source` (`Any`): Full document content for context extraction
- `content_format` (`str`): Format hint: `"auto"`, `"minerU"`, `"text_chunks"`, or `"text"`

**Usage:**
```python
processor.set_content_source(parsed_content, content_format="minerU")
```

**Sources:** [raganything/modalprocessors.py:406-415]()

#### generate_description_only()

```python
async def generate_description_only(
    self,
    modal_content,
    content_type: str,
    item_info: Dict[str, Any] = None,
    entity_name: str = None
) -> Tuple[str, Dict[str, Any]]
```

Generate text description and entity info without entity/relation extraction. Used in batch processing stage 1.

**Parameters:**
- `modal_content`: Modal content to process (format varies by processor type)
- `content_type` (`str`): Type of content: `"image"`, `"table"`, `"equation"`, or custom type
- `item_info` (`Dict[str, Any]`, optional): Item information for context extraction:
  - `page_idx` (`int`): Page index
  - `index` (`int`): Chunk index
- `entity_name` (`str`, optional): Predefined entity name. If `None`, generated from content.

**Returns:**
- `Tuple[str, Dict[str, Any]]`:
  - `description` (`str`): Generated detailed description
  - `entity_info` (`dict`): Entity information with keys:
    - `entity_name` (`str`): Entity identifier
    - `entity_type` (`str`): Entity type
    - `summary` (`str`): Concise summary (max 100 words)

**Note:** This is an abstract method that must be implemented by subclasses.

**Sources:** [raganything/modalprocessors.py:442-463]()

#### process_multimodal_content()

```python
async def process_multimodal_content(
    self,
    modal_content,
    content_type: str,
    file_path: str = "manual_creation",
    entity_name: str = None,
    item_info: Dict[str, Any] = None,
    batch_mode: bool = False,
    doc_id: str = None,
    chunk_order_index: int = 0
) -> Tuple[str, Dict[str, Any], List]
```

Complete processing of multimodal content including description generation, entity creation, and knowledge graph insertion.

**Parameters:**
- `modal_content`: Modal content to process (format varies by processor type)
- `content_type` (`str`): Type of content
- `file_path` (`str`): Source file path for tracking
- `entity_name` (`str`, optional): Predefined entity name
- `item_info` (`Dict[str, Any]`, optional): Item information for context extraction
- `batch_mode` (`bool`): If `True`, skips immediate merge operation for batch processing
- `doc_id` (`str`, optional): Document ID for chunk tracking
- `chunk_order_index` (`int`): Chunk position in document

**Returns:**
- `Tuple[str, Dict[str, Any], List]`:
  - `description` (`str`): Generated description
  - `entity_info` (`dict`): Entity information
  - `chunk_results` (`list`): Extraction results as list of `(nodes, edges)` tuples

**Note:** This is an abstract method that must be implemented by subclasses.

**Sources:** Implementation varies by subclass (see specialized processors below)

### Protected Methods

#### _get_context_for_item()

```python
def _get_context_for_item(self, item_info: Dict[str, Any]) -> str
```

Get context for the current processing item using the configured context extractor.

**Parameters:**
- `item_info` (`Dict[str, Any]`): Item information with `page_idx` or `index`

**Returns:**
- `str`: Extracted context text

**Sources:** [raganything/modalprocessors.py:417-440]()

#### _create_entity_and_chunk()

```python
async def _create_entity_and_chunk(
    self,
    modal_chunk: str,
    entity_info: Dict[str, Any],
    file_path: str,
    batch_mode: bool = False,
    doc_id: str = None,
    chunk_order_index: int = 0
) -> Tuple[str, Dict[str, Any], List]
```

Create text chunk, entity node, and extract relationships.

**Parameters:**
- `modal_chunk` (`str`): Complete formatted content for the chunk
- `entity_info` (`Dict[str, Any]`): Entity information dictionary
- `file_path` (`str`): Source file path
- `batch_mode` (`bool`): Batch processing flag
- `doc_id` (`str`): Document ID
- `chunk_order_index` (`int`): Chunk position

**Returns:**
- `Tuple[str, Dict[str, Any], List]`: Description, entity info, and chunk results

**Operations Performed:**
1. Generates chunk ID using `compute_mdhash_id()` [raganything/modalprocessors.py:476]()
2. Creates chunk data with tokens, content, and metadata [raganything/modalprocessors.py:478-498]()
3. Inserts chunk into `text_chunks_db` and `chunks_vdb` [raganything/modalprocessors.py:500-505]()
4. Creates entity node in knowledge graph [raganything/modalprocessors.py:507-521]()
5. Inserts entity into `entities_vdb` [raganything/modalprocessors.py:523-532]()
6. Calls `_process_chunk_for_extraction()` for entity/relationship extraction [raganything/modalprocessors.py:534]()
7. If not batch mode, calls `merge_nodes_and_edges()` [raganything/modalprocessors.py:538-542]()

**Sources:** [raganything/modalprocessors.py:465-545]()

#### _process_chunk_for_extraction()

```python
async def _process_chunk_for_extraction(
    self,
    chunk_id: str,
    modal_entity_name: str,
    batch_mode: bool = False
) -> List[Tuple[Dict, Dict]]
```

Extract entities and relationships from chunk content.

**Parameters:**
- `chunk_id` (`str`): Chunk identifier
- `modal_entity_name` (`str`): Main modal entity name
- `batch_mode` (`bool`): Batch processing flag

**Returns:**
- `List[Tuple[Dict, Dict]]`: List of `(nodes, edges)` extraction results

**Operations Performed:**
1. Retrieves chunk data from `text_chunks_db` [raganything/modalprocessors.py:708-713]()
2. Creates chunk vector database entry [raganything/modalprocessors.py:715-726]()
3. Calls `extract_entities()` for NER and relation extraction [raganything/modalprocessors.py:728-734]()
4. Creates "belongs_to" relationships between extracted entities and modal entity [raganything/modalprocessors.py:745-774]()
5. Inserts relationships into `relationships_vdb` [raganything/modalprocessors.py:759-766]()
6. If not batch mode, calls `merge_nodes_and_edges()` and `_insert_done()` [raganything/modalprocessors.py:776-791]()

**Sources:** [raganything/modalprocessors.py:699-793]()

#### _robust_json_parse()

```python
def _robust_json_parse(self, response: str) -> dict
```

Parse JSON from LLM response with multiple fallback strategies.

**Parameters:**
- `response` (`str`): Raw LLM response text

**Returns:**
- `dict`: Parsed JSON object

**Strategies Applied (in order):**
1. Direct JSON parsing from all candidates [raganything/modalprocessors.py:603-611]()
2. Basic cleanup (smart quotes, trailing commas) [raganything/modalprocessors.py:613-623]()
3. Progressive quote fixing for LaTeX and escape sequences [raganything/modalprocessors.py:625-635]()
4. Regex field extraction as last resort [raganything/modalprocessors.py:637-697]()

**Handles:**
- JSON in code blocks (` ```json ... ``` `)
- Thinking/reasoning tags (`` tags)
- `<thinking>...</thinking>` tags

This ensures clean JSON extraction even from models that output reasoning chains.

**Sources:** [raganything/modalprocessors.py:579-697]()

### Entity Fallback Creation

All processors implement fallback entity creation when processing fails:

```python
fallback_entity = {
    "entity_name": entity_name or f"{content_type}_{compute_mdhash_id(str(modal_content))}",
    "entity_type": content_type,
    "summary": f"{content_type} content: {str(modal_content)[:100]}"
}
```

This ensures processing continues even with LLM failures.

**Sources:** [raganything/modalprocessors.py:984-990](), [raganything/modalprocessors.py:1177-1183](), [raganything/modalprocessors.py:1361-1367](), [raganything/modalprocessors.py:1523-1529]()

---

## Return Value Specifications

### Entity Information Dictionary

All `generate_description_only()` methods return entity information in this format:

```python
{
    "entity_name": str,      # Unique identifier with type suffix, e.g., "Figure 1 (image)"
    "entity_type": str,      # Content type: "image", "table", "equation", or custom
    "summary": str          # Concise summary, max 100 words
}
```

### Chunk Results Format

The `process_multimodal_content()` method returns chunk results as:

```python
List[Tuple[Dict[str, Dict], Dict[Tuple[str, str], List[Dict]]]]
```

Where each tuple contains:
- `nodes` (`Dict[str, Dict]`): Extracted entity nodes, keyed by entity name
- `edges` (`Dict[Tuple[str, str], List[Dict]]`): Extracted relationships, keyed by `(source, target)` tuple

**Sources:** [raganything/modalprocessors.py:699-793]()

---

## Integration with LightRAG Functions

Modal processors use these LightRAG utility functions:

| Function | Module | Purpose | Line Reference |
|----------|--------|---------|----------------|
| `compute_mdhash_id()` | `lightrag.utils` | Generate hash-based IDs | [raganything/modalprocessors.py:476]() |
| `extract_entities()` | `lightrag.operate` | NER and relation extraction | [raganything/modalprocessors.py:728-734]() |
| `merge_nodes_and_edges()` | `lightrag.operate` | Merge entities into KG | [raganything/modalprocessors.py:776-788]() |
| `get_namespace_data()` | `lightrag.kg.shared_storage` | Get pipeline status | [raganything/modalprocessors.py:721]() |
| `get_pipeline_status_lock()` | `lightrag.kg.shared_storage` | Get status lock | [raganything/modalprocessors.py:722]() |

**Sources:** [raganything/modalprocessors.py:20-27]()

---

# Page: Parser API

# Parser API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [raganything/__init__.py](raganything/__init__.py)
- [raganything/parser.py](raganything/parser.py)
- [tests/testparser_kwargs.py](tests/testparser_kwargs.py)

</details>



This page provides API reference documentation for the document parsing subsystem in RAG-Anything. The parser layer is responsible for converting documents from various formats (PDF, images, Office documents, HTML, text files) into structured content lists that can be processed by the multimodal analysis pipeline.

For the high-level processing pipeline that uses these parsers, see [Document Parsers](#4.1). For configuration of parser selection, see [RAGAnythingConfig](#8.1).

---

## Parser Class Hierarchy

The following diagram shows the inheritance structure and key methods of the parser subsystem, including the factory registry system.

```mermaid
classDiagram
    class Parser {
        <<abstract>>
        +OFFICE_FORMATS: Set~str~
        +IMAGE_FORMATS: Set~str~
        +TEXT_FORMATS: Set~str~
        +logger: Logger
        +convert_office_to_pdf(doc_path, output_dir)$ Path
        +convert_text_to_pdf(text_path, output_dir)$ Path
        +parse_pdf(pdf_path, output_dir, method, lang)*
        +parse_image(image_path, output_dir, lang)*
        +parse_document(file_path, method, output_dir, lang)*
        +check_installation()* bool
    }
    
    class MineruParser {
        +parse_pdf(pdf_path, output_dir, method, lang) List~Dict~
        +parse_image(image_path, output_dir, lang) List~Dict~
        +parse_office_doc(doc_path, output_dir, lang) List~Dict~
        +parse_text_file(text_path, output_dir, lang) List~Dict~
        +parse_document(file_path, method, output_dir, lang) List~Dict~
        +check_installation() bool
        -_run_mineru_command(input_path, output_dir, method, lang, backend, ...)$
        -_read_output_files(output_dir, file_stem, method)$ Tuple
    }
    
    class DoclingParser {
        +HTML_FORMATS: Set~str~
        +parse_pdf(pdf_path, output_dir, method, lang) List~Dict~
        +parse_office_doc(doc_path, output_dir, lang) List~Dict~
        +parse_html(html_path, output_dir, lang) List~Dict~
        +parse_document(file_path, method, output_dir, lang) List~Dict~
        +check_installation() bool
        -_get_converter(kwargs) DocumentConverter
        -_run_docling_python(input_path, output_dir, file_stem, ...)$
    }

    class PaddleOCRParser {
        +parse_pdf(pdf_path, output_dir, method, lang) List~Dict~
        +parse_image(image_path, output_dir, lang) List~Dict~
        +check_installation() bool
    }
    
    class MineruExecutionError {
        +return_code: int
        +error_msg: str
    }
    
    Parser <|-- MineruParser
    Parser <|-- DoclingParser
    Parser <|-- PaddleOCRParser
    MineruParser ..> MineruExecutionError : raises
```

**Sources:** [raganything/parser.py:68-170](), [raganything/parser.py:612-1327](), [raganything/parser.py:1329-1784](), [raganything/parser.py:1786-1934](), [raganything/parser.py:57-66]()

---

## Registry and Factory Functions

RAG-Anything uses a global registry to manage parser implementations. This allows for easy extension and dynamic selection of parsing backends.

### Code-to-Entity Mapping: Parser Registry

```mermaid
flowchart LR
    subgraph "Natural Language Space"
        REG["Parser Registry"]
        FACT["Parser Factory"]
    end

    subgraph "Code Entity Space"
        MAP["_PARSER_REGISTRY : Dict[str, Type[Parser]]"]
        REG_FUNC["register_parser(name, parser_cls)"]
        GET_FUNC["get_parser(name)"]
        LIST_FUNC["list_parsers()"]
    end

    REG --- MAP
    REG_FUNC -.-> MAP
    FACT --- GET_FUNC
    GET_FUNC -.-> MAP
    LIST_FUNC -.-> MAP
```

**Sources:** [raganything/parser.py:2020-2070]()

### Function Reference

| Function | Description |
|----------|-------------|
| `register_parser(name, parser_cls)` | Registers a new parser class under a string name. [raganything/parser.py:2020-2035]() |
| `unregister_parser(name)` | Removes a parser from the registry. [raganything/parser.py:2037-2046]() |
| `get_parser(name)` | Factory function that returns an instance of the requested parser. Defaults to `MineruParser` if name is unknown. [raganything/parser.py:2058-2070]() |
| `list_parsers()` | Returns a list of all registered parser names. [raganything/parser.py:2048-2051]() |

---

## Parse Output Format

The following diagram shows the data flow from documents through parsers to structured content lists:

```mermaid
flowchart LR
    subgraph "Input Documents"
        PDF["PDF<br/>.pdf"]
        IMG["Images<br/>.png .jpg .bmp .tiff .gif .webp"]
        OFFICE["Office Docs<br/>.doc .docx .ppt .pptx .xls .xlsx"]
        TEXT["Text Files<br/>.txt .md"]
        HTML["HTML<br/>.html .htm .xhtml"]
    end
    
    subgraph "Parser Layer"
        MINERU["MineruParser<br/>parse_document()"]
        DOCLING["DoclingParser<br/>parse_document()"]
        PADDLE["PaddleOCRParser<br/>parse_document()"]
        
        CONVERT_OFFICE["convert_office_to_pdf()<br/>via LibreOffice"]
        CONVERT_TEXT["convert_text_to_pdf()<br/>via ReportLab"]
    end
    
    subgraph "Parser Output"
        CONTENT_LIST["List[Dict[str, Any]]<br/>content_list"]
    end
    
    subgraph "Content Block Types"
        TEXT_BLOCK["type: 'text'<br/>text: str<br/>page_idx: int"]
        IMAGE_BLOCK["type: 'image'<br/>img_path: str<br/>image_caption: str<br/>image_footnote: str<br/>page_idx: int"]
        TABLE_BLOCK["type: 'table'<br/>table_body: List<br/>table_caption: str<br/>table_footnote: str<br/>page_idx: int"]
        EQUATION_BLOCK["type: 'equation'<br/>equation_img_path: str<br/>text: str<br/>text_format: str<br/>page_idx: int"]
    end
    
    PDF --> MINERU
    IMG --> MINERU
    OFFICE --> CONVERT_OFFICE
    CONVERT_OFFICE --> MINERU
    TEXT --> CONVERT_TEXT
    CONVERT_TEXT --> MINERU
    
    PDF --> DOCLING
    OFFICE --> DOCLING
    HTML --> DOCLING
    
    PDF --> PADDLE
    IMG --> PADDLE
    
    MINERU --> CONTENT_LIST
    DOCLING --> CONTENT_LIST
    PADDLE --> CONTENT_LIST
    
    CONTENT_LIST --> TEXT_BLOCK
    CONTENT_LIST --> IMAGE_BLOCK
    CONTENT_LIST --> TABLE_BLOCK
    CONTENT_LIST --> EQUATION_BLOCK
```

**Sources:** [raganything/parser.py:1239-1294](), [raganything/parser.py:1410-1451](), [raganything/parser.py:1865-1906]()

---

## Parser Base Class

The `Parser` class provides an abstract interface for document parsing utilities.

**Location:** [raganything/parser.py:68-610]()

### Class Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `OFFICE_FORMATS` | `Set[str]` | Supported Office file extensions: `.doc`, `.docx`, `.ppt`, `.pptx`, `.xls`, `.xlsx` |
| `IMAGE_FORMATS` | `Set[str]` | Supported image extensions: `.png`, `.jpeg`, `.jpg`, `.bmp`, `.tiff`, `.tif`, `.gif`, `.webp` |
| `TEXT_FORMATS` | `Set[str]` | Supported text extensions: `.txt`, `.md` |
| `logger` | `logging.Logger` | Class-level logger instance |

**Sources:** [raganything/parser.py:76-81]()

### Constructor

```python
def __init__(self) -> None
```

Initializes the base parser. Called by subclass constructors.

**Sources:** [raganything/parser.py:167-169]()

### Static Conversion Methods

#### convert_office_to_pdf

```python
@classmethod
def convert_office_to_pdf(
    cls, 
    doc_path: Union[str, Path], 
    output_dir: Optional[str] = None
) -> Path
```

Converts Office documents to PDF format using LibreOffice command-line tools.

**Sources:** [raganything/parser.py:193-331]()

#### convert_text_to_pdf

```python
@classmethod
def convert_text_to_pdf(
    cls, 
    text_path: Union[str, Path], 
    output_dir: Optional[str] = None
) -> Path
```

Converts text files to PDF format using ReportLab with markdown support.

**Sources:** [raganything/parser.py:333-568]()

---

## MineruParser Class

The `MineruParser` class implements document parsing using the MinerU 2.0 command-line tool.

**Location:** [raganything/parser.py:612-1327]()

### MinerU Command Execution Flow

```mermaid
flowchart TD
    START["parse_document()"] --> RUN_MINERU["_run_mineru_command()"]
    RUN_MINERU --> BUILD_CMD["Build mineru CLI command"]
    BUILD_CMD --> SPAWN["subprocess.Popen()"]
    SPAWN --> THREADS["Start reader threads for stdout/stderr"]
    THREADS --> POLL["Poll process and log output"]
    POLL --> WAIT["Wait for completion"]
    WAIT -->|"returncode != 0"| ERROR["Raise MineruExecutionError"]
    WAIT -->|"returncode == 0"| READ["_read_output_files()"]
    READ --> RETURN["Return List[Dict[str, Any]]"]
```

**Sources:** [raganything/parser.py:631-831](), [raganything/parser.py:833-922]()

### Public Methods

#### parse_pdf

```python
def parse_pdf(
    self,
    pdf_path: Union[str, Path],
    output_dir: Optional[str] = None,
    method: str = "auto",
    lang: Optional[str] = None,
    **kwargs,
) -> List[Dict[str, Any]]
```
**Sources:** [raganything/parser.py:924-1022]()

---

## DoclingParser Class

The `DoclingParser` class implements document parsing using the Docling Python API.

**Location:** [raganything/parser.py:1329-1784]()

### Implementation Details
DoclingParser now uses the `DocumentConverter` Python API rather than a subprocess CLI call. It maintains a converter cache to improve performance.

- `_get_converter(**kwargs)`: Retrieves or initializes a `DocumentConverter` with specified options. [raganything/parser.py:1453-1502]()
- `_run_docling_python(...)`: Performs the actual conversion and exports to JSON/Markdown. [raganything/parser.py:1504-1563]()

---

## PaddleOCRParser Class

The `PaddleOCRParser` provides a lightweight OCR-based parsing alternative using the PaddleOCR library.

**Location:** [raganything/parser.py:1786-1934]()

### Capabilities
- **OCR for Images/PDFs**: Uses `PaddleOCR` to detect and recognize text. [raganything/parser.py:1820-1863]()
- **Text-only Output**: Currently returns a list of text blocks; does not extract images or tables separately. [raganything/parser.py:1865-1906]()

---

## Content Block Formats

### Text Block
```python
{
    "type": "text",
    "text": str,
    "page_idx": int,
}
```
**Sources:** [raganything/parser.py:1658-1672]()

### Image Block
```python
{
    "type": "image",
    "img_path": str,
    "image_caption": str,
    "image_footnote": str,
    "page_idx": int,
}
```
**Sources:** [raganything/parser.py:1673-1696]()

### Table Block
```python
{
    "type": "table",
    "img_path": str,
    "table_caption": str,
    "table_footnote": str,
    "table_body": List[List[str]],
    "page_idx": int,
}
```
**Sources:** [raganything/parser.py:1697-1713]()

---

## Parser Selection Guidelines

| Use Case | Recommended Parser | Reason |
|----------|-------------------|---------|
| PDF (complex layout) | `mineru` | Superior structure and formula extraction. |
| Office / HTML | `docling` | Native Python API support for structured docs. |
| Quick OCR / Light | `paddleocr` | Lower resource usage for simple text extraction. |

**Sources:** [raganything/parser.py:2053-2070]()

---

# Page: Query Methods API

# Query Methods API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [raganything/batch.py](raganything/batch.py)
- [raganything/query.py](raganything/query.py)

</details>



This page documents the public API methods of the `QueryMixin` class, which provides text and multimodal query capabilities for RAG-Anything. These methods enable querying the knowledge graph constructed from processed documents using various retrieval strategies.

For information about query architecture and retrieval strategies, see [Query Architecture](#7.1). For practical query examples, see [Query Examples](#9.4).

**Sources:** [raganything/query.py:1-770]()

---

## QueryMixin Class Overview

The `QueryMixin` class provides all query functionality as a mixin to the main `RAGAnything` class. It offers three distinct query interfaces, each available in both synchronous and asynchronous versions:

1. **Pure Text Query** - Standard text-based retrieval via `aquery()` / `query()`
2. **Multimodal Query** - Query with accompanying multimodal content via `aquery_with_multimodal()` / `query_with_multimodal()`
3. **VLM Enhanced Query** - Automatic image detection and VLM processing via `aquery_vlm_enhanced()`

All query methods integrate with LightRAG's retrieval engine and support multiple query modes.

**Sources:** [raganything/query.py:22-23]()

---

## Query Method Hierarchy

```mermaid
graph TB
    QueryMixin["QueryMixin Class"]
    
    subgraph "Async Methods"
        aquery["aquery()"]
        aquery_multimodal["aquery_with_multimodal()"]
        aquery_vlm["aquery_vlm_enhanced()"]
    end
    
    subgraph "Sync Methods"
        query["query()"]
        query_multimodal["query_with_multimodal()"]
    end
    
    subgraph "LightRAG Integration"
        lightrag_query["lightrag.aquery()"]
    end
    
    subgraph "Helper Methods"
        process_multimodal["_process_multimodal_query_content()"]
        process_images["_process_image_paths_for_vlm()"]
        build_vlm_msg["_build_vlm_messages_with_images()"]
        cache_key["_generate_multimodal_cache_key()"]
    end
    
    QueryMixin --> aquery
    QueryMixin --> aquery_multimodal
    QueryMixin --> aquery_vlm
    QueryMixin --> query
    QueryMixin --> query_multimodal
    
    query --> aquery
    query_multimodal --> aquery_multimodal
    
    aquery --> aquery_vlm
    aquery --> lightrag_query
    
    aquery_multimodal --> process_multimodal
    aquery_multimodal --> cache_key
    aquery_multimodal --> aquery
    
    aquery_vlm --> process_images
    aquery_vlm --> build_vlm_msg
    aquery_vlm --> lightrag_query
```

**Sources:** [raganything/query.py:102-770]()

---

## Public Query Methods

### aquery() - Asynchronous Text Query

Pure text query method that directly interfaces with LightRAG's query functionality. Automatically enables VLM enhancement when `vision_model_func` is available.

**Signature:**
```python
async def aquery(
    self,
    query: str,
    mode: str = "mix",
    system_prompt: str | None = None,
    **kwargs
) -> str
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | Required | Query text to search for |
| `mode` | `str` | `"mix"` | Retrieval mode (see Query Modes section) |
| `system_prompt` | `str \| None` | `None` | Optional system prompt to include |
| `vlm_enhanced` | `bool` | Auto-detected | Enable VLM enhancement for image processing |
| `**kwargs` | | | Additional parameters passed to `QueryParam` |

**Returns:** `str` - Query result generated by the LLM

**Behavior:**

1. Validates that LightRAG instance exists [raganything/query.py:120-124]().
2. Auto-detects VLM enhancement capability based on `vision_model_func` availability [raganything/query.py:129-133]().
3. If VLM enhancement is enabled, delegates to `aquery_vlm_enhanced()` [raganything/query.py:136-143]().
4. Otherwise, creates a `QueryParam` and calls `lightrag.aquery()` [raganything/query.py:162-171]().

**Example:**
```python
# Basic text query
result = await rag.aquery("What is machine learning?")

# Query with specific mode
result = await rag.aquery("Explain the algorithm", mode="local")

# Disable VLM enhancement explicitly
result = await rag.aquery("Describe the results", vlm_enhanced=False)
```

**Sources:** [raganything/query.py:102-193]()

---

### query() - Synchronous Text Query

Synchronous wrapper around `aquery()`. Uses `always_get_an_event_loop()` to handle async execution.

**Signature:**
```python
def query(
    self,
    query: str,
    mode: str = "mix",
    **kwargs
) -> str
```

**Parameters:** Same as `aquery()` except `system_prompt` is passed via `**kwargs`.

**Returns:** `str` - Query result

**Example:**
```python
# Synchronous query
result = rag.query("What is deep learning?", mode="hybrid")
```

**Sources:** [raganything/query.py:727-743]()

---

### aquery_with_multimodal() - Asynchronous Multimodal Query

Query method that accepts multimodal content (images, tables, equations) alongside the text query. Processes multimodal content to generate enhanced context before querying.

**Signature:**
```python
async def aquery_with_multimodal(
    self,
    query: str,
    multimodal_content: List[Dict[str, Any]] = None,
    mode: str = "mix",
    system_prompt: str | None = None,
    **kwargs,
) -> str
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | Required | Base query text |
| `multimodal_content` | `List[Dict[str, Any]]` | `None` | List of multimodal content items |
| `mode` | `str` | `"mix"` | Retrieval mode |
| `system_prompt` | `str \| None` | `None` | Optional system prompt |
| `**kwargs` | | | Additional query parameters |

**Multimodal Content Format:**

Each item in `multimodal_content` is a dictionary with content type and type-specific fields:

**Image Content:**
```python
{
    "type": "image",
    "img_path": "./path/to/image.jpg",  # Required
    "image_caption": ["Caption text"],   # Optional
    "img_footnote": ["Footnote"]        # Optional
}
```

**Table Content:**
```python
{
    "type": "table",
    "table_data": "Name,Age\nAlice,25",  # Required (CSV or markdown)
    "table_caption": "User data table"   # Optional
}
```

**Equation Content:**
```python
{
    "type": "equation",
    "latex": "E = mc^2",              # Required
    "equation_caption": "Mass-energy"  # Optional
}
```

**Returns:** `str` - Query result incorporating multimodal analysis

**Processing Flow:**

```mermaid
flowchart TD
    start["aquery_with_multimodal() called"]
    check_content{"multimodal_content<br/>provided?"}
    check_cache{"Cache enabled<br/>and hit?"}
    process["_process_multimodal_query_content()"]
    enhance["Generate enhanced query"]
    query["Call aquery() with enhanced query"]
    cache_save["Save to cache"]
    return_result["Return result"]
    fallback["Fallback to aquery()"]
    
    start --> check_content
    check_content -->|No| fallback
    check_content -->|Yes| check_cache
    check_cache -->|Yes| return_result
    check_cache -->|No| process
    process --> enhance
    enhance --> query
    query --> cache_save
    cache_save --> return_result
    fallback --> return_result
```

**Caching Strategy:**

The method implements intelligent caching for multimodal queries [raganything/query.py:214-230]():
- Cache key generated via `_generate_multimodal_cache_key()` [raganything/query.py:26-100]().
- Image paths normalized to basenames for portability [raganything/query.py:54-60]().
- Large content (>200 chars) hashed instead of stored directly [raganything/query.py:62-69]().
- Cache checked before processing, saved after successful query [raganything/query.py:284-288]().

**Example:**
```python
# Query with image
result = await rag.aquery_with_multimodal(
    "What does this diagram show?",
    multimodal_content=[{
        "type": "image",
        "img_path": "./diagram.png"
    }]
)
```

**Sources:** [raganything/query.py:195-301]()

---

### query_with_multimodal() - Synchronous Multimodal Query

Synchronous wrapper around `aquery_with_multimodal()`.

**Signature:**
```python
def query_with_multimodal(
    self,
    query: str,
    multimodal_content: List[Dict[str, Any]] = None,
    mode: str = "mix",
    **kwargs
) -> str
```

**Parameters:** Same as `aquery_with_multimodal()`.

**Returns:** `str` - Query result

**Sources:** [raganything/query.py:745-769]()

---

### aquery_vlm_enhanced() - VLM Enhanced Query

Specialized query method that automatically detects image paths in retrieved context and replaces them with base64-encoded images for VLM (Vision-Language Model) processing. This enables the LLM to "see" images referenced in the retrieved knowledge.

**Signature:**
```python
async def aquery_vlm_enhanced(
    self,
    query: str,
    mode: str = "mix",
    system_prompt: str | None = None,
    **kwargs
) -> str
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | Required | User query text |
| `mode` | `str` | `"mix"` | Underlying LightRAG retrieval mode |
| `system_prompt` | `str \| None` | `None` | Optional system prompt |
| `**kwargs` | | | Additional query parameters |

**Requirements:**
- `vision_model_func` must be provided during RAGAnything initialization [raganything/query.py:319-323]().
- Image files must exist at referenced paths and pass validation [raganything/query.py:573-581]().

**Returns:** `str` - VLM-generated query result

**Processing Pipeline:**

```mermaid
flowchart TD
    start["aquery_vlm_enhanced() called"]
    validate{"vision_model_func<br/>available?"}
    get_prompt["Get retrieval prompt<br/>(only_need_prompt=True)"]
    find_images["_process_image_paths_for_vlm()"]
    check_images{"Images found?"}
    build_msg["_build_vlm_messages_with_images()"]
    call_vlm["_call_vlm_with_multimodal_content()"]
    fallback["Fallback to<br/>normal query"]
    return_result["Return VLM result"]
    
    start --> validate
    validate -->|No| error["Raise ValueError"]
    validate -->|Yes| get_prompt
    get_prompt --> find_images
    find_images --> check_images
    check_images -->|No| fallback
    check_images -->|Yes| build_msg
    build_msg --> call_vlm
    call_vlm --> return_result
    fallback --> return_result
```

**Image Path Detection:**

The method uses regex pattern matching to find image paths in the retrieved context [raganything/query.py:539-541]():
```
Image Path:\s*([^\r\n]*?\.(?:jpg|jpeg|png|gif|bmp|webp|tiff|tif))
```

Images are validated using `validate_image_file()` and encoded to base64 using `encode_image_to_base64()` [raganything/query.py:573-586]().

**VLM Message Format:**

Messages are constructed in OpenAI-compatible multimodal format with interleaved text and images [raganything/query.py:609-691]().

**Sources:** [raganything/query.py:303-364]()

---

## Query Modes

All query methods support the following retrieval modes via the `mode` parameter:

| Mode | Description | Use Case |
|------|-------------|----------|
| `"local"` | Context-based search using vector similarity | Finding specific facts or details |
| `"global"` | Knowledge-based search using graph traversal | Understanding overall themes and concepts |
| `"hybrid"` | Combines vector similarity and graph traversal | Balanced retrieval for complex queries |
| `"naive"` | Simple vector similarity search | Fast retrieval without graph enhancement |
| `"mix"` | **Default.** Automatically selects best mode | General purpose queries |
| `"bypass"` | Direct LLM call without retrieval | Testing or LLM-only responses |

These modes are passed to LightRAG's `QueryParam` [raganything/query.py:162]().

**Sources:** [raganything/query.py:110,199,311]()

---

## Internal Helper Methods

### Multimodal Content Processing

**`_process_multimodal_query_content()`** [raganything/query.py:366-417]()
Processes multimodal content items to generate enhanced query text by routing each item to the appropriate processor.

**`_generate_query_content_description()`** [raganything/query.py:419-447]()
Dispatches content to type-specific description generators based on the `type` field.

**Type-Specific Describers:**
- `_describe_image_for_query()` [raganything/query.py:449-478]()
- `_describe_table_for_query()` [raganything/query.py:480-495]()
- `_describe_equation_for_query()` [raganything/query.py:497-512]()
- `_describe_generic_for_query()` [raganything/query.py:514-531]()

### VLM Image Processing

**`_process_image_paths_for_vlm()`** [raganything/query.py:533-607]()
Extracts image paths from prompt text, validates files, and encodes them to base64.

**`_build_vlm_messages_with_images()`** [raganything/query.py:609-691]()
Constructs the final multimodal message list for the VLM provider.

**`_call_vlm_with_multimodal_content()`** [raganything/query.py:693-724]()
Invokes `vision_model_func` with the constructed multimodal messages.

### Caching

**`_generate_multimodal_cache_key()`** [raganything/query.py:26-100]()
Generates a unique MD5 hash for a multimodal query based on the text, mode, and normalized content descriptions.

**Sources:** [raganything/query.py:26-724]()

---

# Page: Utilities API

# Utilities API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/multimodal_rag_failure_modes.md](docs/multimodal_rag_failure_modes.md)
- [raganything/asset_urls.py](raganything/asset_urls.py)
- [raganything/omml_extractor.py](raganything/omml_extractor.py)
- [raganything/utils.py](raganything/utils.py)
- [tests/test_asset_urls.py](tests/test_asset_urls.py)
- [tests/test_doc_status_creation.py](tests/test_doc_status_creation.py)
- [tests/test_omml_extractor.py](tests/test_omml_extractor.py)

</details>



## Purpose and Scope

This page documents the utility functions and helper modules within RAG-Anything. These utilities provide core functionality for content normalization, table formatting, OMML equation extraction, and public asset URL mapping.

For information about the main RAGAnything class that uses these utilities, see [RAGAnything Class](10.1). For details on document processing workflows that orchestrate these utilities, see [ProcessorMixin API](10.7).

---

## Utility Module Overview

The codebase contains three primary utility modules:

| Module | Purpose | Key Functions |
|--------|---------|---------------|
| `raganything.utils` | General content processing and normalization. | `normalize_caption_list`, `format_table_body`, `separate_content` |
| `raganything.asset_urls` | Mapping local paths to public URLs (S3/CDN). | `attach_public_media_urls`, `public_url_for_local_path` |
| `raganything.omml_extractor` | Extracting and converting Word (OMML) equations. | `extract_omml_equations`, `omml_to_latex` |

**Sources:** [raganything/utils.py:1-5](), [raganything/asset_urls.py:1-12](), [raganything/omml_extractor.py:1-38]()

---

## Content Normalization and Formatting (`utils.py`)

### `normalize_caption_list`
Ensures that captions and footnotes (which may arrive as `None`, `str`, or `list`) are converted into a consistent `List[str]`.
[raganything/utils.py:16-24]()

### `format_table_body`
Serializes table content for LLM consumption. It converts "list-of-lists" (common in non-MinerU parsers) into a Markdown table format with headers and separators.
[raganything/utils.py:36-60]()

### `get_equation_text_and_format`
Resolves equation content by checking multiple alias fields (`text`, `latex`, `equation`) to ensure compatibility across different parser backends (MinerU, Docling, PaddleOCR).
[raganything/utils.py:63-88]()

### `separate_content`
Separates text content from multimodal content (images, tables, equations) in a parsed document's content list. It also enriches multimodal items with `_section_path` and `_neighbor_text` for context.
[raganything/utils.py:172-214]()

```mermaid
graph TD
    subgraph "Natural Language Space"
        Doc["Document Content"]
        Captions["Captions & Footnotes"]
        TableData["Raw Table Data"]
    end

    subgraph "Code Entity Space (raganything/utils.py)"
        norm["normalize_caption_list()"]
        fmt_table["format_table_body()"]
        sep["separate_content()"]
        
        Doc --> sep
        Captions --> norm
        TableData --> fmt_table
    end

    sep -->|"text"| text_out["text_parts"]
    sep -->|"multimodal"| mm_out["multimodal_items"]
    norm --> clean_list["List[str]"]
    fmt_table --> md_table["Markdown String"]
```
**Sources:** [raganything/utils.py:16-214]()

---

## Public Asset URL Mapping (`asset_urls.py`)

This module implements the environment-variable contract for systems where ingestion occurs on a server but the UI/retrieval runs elsewhere. It allows local filesystem paths to be mapped to public HTTPS/S3 URLs.

### Environment Variables
- `RAGANYTHING_PUBLIC_ASSET_BASE_URL`: The prefix for the public URL (e.g., `https://cdn.example.com/assets`).
- `RAGANYTHING_PUBLIC_ASSET_STRIP_PREFIX`: The local absolute path to strip from the beginning of the file path.

### `attach_public_media_urls`
Mutates a content item dictionary by adding `*_public_url` fields for any detected media paths (`img_path`, `table_img_path`, `equation_img_path`).
[raganything/asset_urls.py:65-118]()

```mermaid
sequenceDiagram
    participant P as Processor (MinerU)
    participant A as asset_urls.py
    participant E as Env Variables

    P->>A: attach_public_media_urls(item)
    A->>E: Get BASE_URL & STRIP_PREFIX
    alt Both Vars Set
        A->>A: public_url_for_local_path()
        A->>P: Mutate item: add img_path_public_url
    else Missing Vars
        A->>A: Log Warning (Once)
    end
```
**Sources:** [raganything/asset_urls.py:42-118]()

---

## OMML Equation Extraction (`omml_extractor.py`)

This module provides a zero-dependency, pure-stdlib utility to extract mathematical formulas from `.docx` files. It parses the `word/document.xml` archive directly.

### `extract_omml_equations`
Opens a DOCX as a ZIP archive and locates every `<m:oMath>` or `<m:oMathPara>` element in document order.
[raganything/omml_extractor.py:111-147]()

### `omml_to_latex`
A recursive transformer that converts OMML XML constructs into searchable LaTeX strings.
- **Handled Constructs**: Fractions (`m:f`), Sub/Superscripts (`m:sSub`, `m:sSup`), Radicals (`m:rad`), N-ary operators (Summation, Integral), Matrices (`m:m`), and Delimiters (`m:d`).
- **Fallback**: If a construct is unhandled, it falls back to concatenated text content to ensure RAG recall.
[raganything/omml_extractor.py:203-345]()

### `enrich_content_list_with_docx_equations`
Merges extracted equations into an existing `content_list` produced by standard parsers. It uses a fuzzy matching strategy (ignoring whitespace/case) to insert LaTeX formulas where placeholders were left by the PDF conversion process.
[raganything/omml_extractor.py:348-422]()

```mermaid
graph LR
    subgraph "DOCX Archive"
        XML["word/document.xml"]
    end

    subgraph "omml_extractor.py"
        ext["extract_omml_equations()"]
        trans["omml_to_latex()"]
        enrich["enrich_content_list_with_docx_equations()"]
    end

    XML --> ext
    ext --> trans
    trans --> enrich
    enrich --> final["Enriched Content List"]
```
**Sources:** [raganything/omml_extractor.py:111-422]()

---

## Implementation Details

### Table Serialization Logic
The `format_table_body` function implements a robust fallback mechanism:
1. **String**: Returned as-is.
2. **List of Lists**: Rendered as a Markdown table.
3. **List of Objects**: Rendered as newline-joined strings.
4. **Empty List**: Returns empty string.
[raganything/utils.py:44-60]()

### Section Path Reconstruction
The `extract_section_path_from_content_list` utility walks backward through the `content_list` to reconstruct a hierarchical path (e.g., `Introduction > Method > Results`) based on `text_level` markers. This provides spatial context to multimodal elements.
[raganything/utils.py:91-134]()

### OMML N-ary Operators
The extractor maps Unicode math symbols to LaTeX commands for common operators:
- `\u2211` → `\sum`
- `\u222b` → `\int`
- `\u220f` → `\prod`
[raganything/omml_extractor.py:65-79]()

**Sources:** [raganything/utils.py:44-134](), [raganything/omml_extractor.py:65-79]()

---

# Page: ProcessorMixin API

# ProcessorMixin API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [raganything/processor.py](raganything/processor.py)
- [tests/test_insert_content_list.py](tests/test_insert_content_list.py)

</details>



## Purpose and Scope

This document provides comprehensive API documentation for the `ProcessorMixin` class, which contains all document processing functionality in RAG-Anything. The ProcessorMixin implements the core document ingestion pipeline including parsing, caching, text content insertion, multimodal content processing, and document status tracking.

For information about:
- Parser implementations and supported formats, see [Parser API](#10.4)
- Multimodal content processors, see [Modal Processors API](#10.3)
- Batch processing methods, see [BatchMixin API](#10.8)
- Query functionality, see [Query Methods API](#10.5)

Sources: [raganything/processor.py:1-30]()

---

## ProcessorMixin Class Overview

The `ProcessorMixin` class is defined in [raganything/processor.py:32-33]() and provides document processing capabilities as a mixin that is composed into the main `RAGAnything` class. It orchestrates a multi-stage processing pipeline that handles both text and multimodal content.

### System Architecture and Data Flow

The following diagram bridges the Natural Language processing requirements to the Code Entity Space, showing how `ProcessorMixin` methods interact with storage and internal utilities.

```mermaid
graph TB
    subgraph "ProcessorMixin Public API"
        process_document_complete["process_document_complete()"]
        insert_content_list["insert_content_list()"]
        parse_document["parse_document()"]
    end
    
    subgraph "Internal Processing Logic"
        separate_content["separate_content()"]
        insert_text_content["insert_text_content()"]
        _process_multimodal_content_batch_type_aware["_process_multimodal_content_batch_type_aware()"]
        _generate_cache_key["_generate_cache_key()"]
    end
    
    subgraph "Storage & Status Management"
        lightrag_doc_status["lightrag.doc_status"]
        multimodal_status_cache["multimodal_status_cache"]
        parse_cache["parse_cache"]
    end
    
    process_document_complete --> parse_document
    parse_document --> _generate_cache_key
    _generate_cache_key --> parse_cache
    
    process_document_complete --> separate_content
    separate_content --> insert_text_content
    separate_content --> _process_multimodal_content_batch_type_aware
    
    insert_content_list --> _process_multimodal_content_batch_type_aware
    
    _process_multimodal_content_batch_type_aware --> multimodal_status_cache
    insert_text_content --> lightrag_doc_status
```

Sources: [raganything/processor.py:32-202](), [raganything/processor.py:1441-1861]()

---

## Core Processing Methods

### process_document_complete()

Complete document processing workflow that parses a file and integrates both text and multimodal content into the knowledge graph.

**Signature:**
[raganything/processor.py:1441-1453]()
```python
async def process_document_complete(
    self,
    file_path: str,
    output_dir: str = None,
    parse_method: str = None,
    display_stats: bool = None,
    split_by_character: str | None = None,
    split_by_character_only: bool = False,
    doc_id: str | None = None,
    file_name: str | None = None,
    **kwargs,
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `file_path` | `str` | Path to the file to process (required) |
| `output_dir` | `str` | Parser output directory (defaults to `config.parser_output_dir`) |
| `parse_method` | `str` | Parse method: `"auto"`, `"ocr"`, or `"txt"` (defaults to `config.parse_method`) |
| `display_stats` | `bool` | Display content statistics (defaults to `config.display_content_stats`) |
| `split_by_character` | `str \| None` | Character to split text by (e.g., `"\n\n"`) |
| `split_by_character_only` | `bool` | If True, split only by specified character |
| `doc_id` | `str \| None` | Document ID (auto-generated from content if not provided) |
| `file_name` | `str \| None` | File name for citation (defaults to basename or full path based on `config.use_full_path`) |
| `**kwargs` | | Additional parser parameters: `lang`, `device`, `start_page`, `end_page`, `formula`, `table`, `backend`, `source` |

**Behavior:**
1. Calls `parse_document` to get `content_list` and `doc_id` [raganything/processor.py:1477-1483]().
2. Separates content into text and multimodal items using `separate_content` [raganything/processor.py:1492]().
3. Inserts text content using `insert_text_content` (or `insert_text_content_with_multimodal_content` if enabled) [raganything/processor.py:1502-1510]().
4. Processes multimodal items via `_process_multimodal_content` [raganything/processor.py:1512-1517]().
5. Updates document status to `PROCESSED` and sets the `multimodal_processed` flag [raganything/processor.py:1523-1528]().

Sources: [raganything/processor.py:1441-1529]()

---

### process_document_complete_lightrag_api()

A specialized version of the complete processing workflow designed to be compatible with LightRAG API expectations. It ensures the `doc_status` is updated correctly within the LightRAG ecosystem.

**Behavior:**
- Wraps `process_document_complete` but focuses on providing the `doc_id` and ensuring `doc_status` records exist [raganything/processor.py:1531-1582]().
- Uses `_ensure_doc_status_record` to prevent missing status entries in the LightRAG backend [raganything/processor.py:1561-1563]().

Sources: [raganything/processor.py:1531-1582]()

---

### insert_content_list()

Insert pre-parsed content list directly without document parsing. This method bypasses the parsing stage and allows integration with external parsers or pre-processed content.

**Signature:**
[raganything/processor.py:1756-1765]()
```python
async def insert_content_list(
    self,
    content_list: List[Dict[str, Any]],
    file_path: str = "unknown_document",
    split_by_character: str | None = None,
    split_by_character_only: bool = False,
    doc_id: str | None = None,
    display_stats: bool = None,
)
```

**Content List Schema:**
Items must be dictionaries with a `type` field. Supported types:
- `text`: Requires `text` field [raganything/processor.py:1796]().
- `image`: Requires `img_path` [raganything/processor.py:1806]().
- `table`: Requires `table_body` [raganything/processor.py:1810]().
- `equation`: Requires `latex` or `text` [raganything/processor.py:1814]().

**Status Management:**
If text is present, it uses `ainsert` which marks the document as `PROCESSED` [tests/test_insert_content_list.py:141-148](). If only multimodal content is present, it manually transitions status from `READY` to `HANDLING` [tests/test_insert_content_list.py:196-217]().

Sources: [raganything/processor.py:1756-1861](), [tests/test_insert_content_list.py:131-217]()

---

### parse_document()

Parse document with automatic caching support. This method handles parser selection via the `get_parser` factory and manages the `parse_cache`.

**Logic Flow:**
1. Generates a cache key using `_generate_cache_key` [raganything/processor.py:293]().
2. Checks `parse_cache` for existing results [raganything/processor.py:295-305]().
3. If not cached, selects a parser (e.g., `MineruParser`) and executes parsing [raganything/processor.py:343-417]().
4. Generates a `doc_id` using `_generate_content_based_doc_id` [raganything/processor.py:431]().
5. Stores the result in `parse_cache` [raganything/processor.py:434-445]().

Sources: [raganything/processor.py:280-453]()

---

### _process_multimodal_content_batch_type_aware()

The core internal engine for handling multimodal elements (images, tables, equations) in a batch-aware manner.

**Implementation Details:**
- **Concurrency Control:** Uses `asyncio.Semaphore` limited by `config.max_parallel_insert` to bound LLM/VLM calls [raganything/processor.py:716-721]().
- **Type Routing:** For each item, it calls `get_processor_for_type` to retrieve the specialized processor (e.g., `ImageModalProcessor`) [raganything/processor.py:723-724]().
- **Two-Stage Processing:**
    1. **Description Generation:** Generates text descriptions for all items concurrently [raganything/processor.py:726-751]().
    2. **LightRAG Integration:** Converts descriptions to LightRAG chunks, extracts entities, and merges them into the knowledge graph [raganything/processor.py:756-879]().

```mermaid
graph TD
    subgraph "Batch Type-Aware Flow"
        input["multimodal_items list"]
        semaphore["asyncio.Semaphore"]
        
        input --> loop["For each item"]
        loop --> get_proc["get_processor_for_type()"]
        get_proc --> limit["Acquire Semaphore"]
        limit --> gen_desc["processor.generate_description_only()"]
        gen_desc --> collect["Collect descriptions"]
        
        collect --> convert["_convert_to_lightrag_chunks_type_aware()"]
        convert --> extract["_batch_extract_entities_lightrag_style_type_aware()"]
        extract --> merge["_batch_merge_lightrag_style_type_aware()"]
    end
```

Sources: [raganything/processor.py:703-879]()

---

## Internal Helper Methods

### _generate_cache_key()
Generates a unique MD5 hash based on:
- Absolute file path [raganything/processor.py:70]().
- File modification time (`st_mtime`) [raganything/processor.py:66-71]().
- Parser and `parse_method` [raganything/processor.py:72-73]().
- Specific parser parameters like `lang`, `device`, `pages` [raganything/processor.py:77-92]().

### _upsert_doc_status()
Safely updates the `lightrag.doc_status` record. It first ensures a record exists via `_ensure_doc_status_record` and then merges updates while updating the `updated_at` timestamp [raganything/processor.py:138-159]().

### _set_multimodal_status_record()
Persists the completion state of multimodal processing in the `multimodal_status_cache` namespace. This is crucial for tracking documents that have finished text indexing but are still undergoing VLM analysis [raganything/processor.py:171-188]().

Sources: [raganything/processor.py:50-188]()

---

# Page: BatchMixin API

# BatchMixin API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [raganything/batch.py](raganything/batch.py)
- [raganything/batch_parser.py](raganything/batch_parser.py)
- [raganything/query.py](raganything/query.py)
- [tests/test_custom_parser.py](tests/test_custom_parser.py)

</details>



This document provides the complete API reference for the `BatchMixin` class and the supporting `BatchParser` class. These components provide batch and concurrent document processing capabilities to RAGAnything, enabling processing of multiple files, entire folders, and integrated batch parsing with RAG insertion.

For usage examples of batch processing, see [Batch Processing](#9.2). For the single-document processing API, see [ProcessorMixin API](#10.7).

---

## Overview

The `BatchMixin` class is composed into the `RAGAnything` class to provide batch processing functionality. It supports:

- **Concurrent file processing** with configurable worker pools and semaphore-based concurrency control.
- **Folder traversal** with optional recursive processing.
- **Format filtering** based on supported file extensions.
- **Progress tracking** and statistics reporting via `tqdm`.
- **Two processing modes**: parse-only batch processing and integrated RAG batch processing.
- **Synchronous and asynchronous APIs** for both workflows.

Sources: [raganything/batch.py:1-25](), [raganything/batch_parser.py:1-16]()

---

## Batch Processing Architecture

The system uses a delegation pattern where high-level batch requests are routed through `BatchMixin` to the `BatchParser` for the parsing phase, and back to `ProcessorMixin` for the RAG integration phase.

### Natural Language Space to Code Entity Space Mapping

```mermaid
graph TD
    subgraph "Natural Language Concepts"
        Folder["Folder Processing"]
        Concurrent["Parallel Workers"]
        Result["Processing Summary"]
        Filtering["File Filtering"]
    end

    subgraph "Code Entity Space (raganything/batch.py)"
        BatchMixin["BatchMixin (Class)"]
        PF_Complete["process_folder_complete (Method)"]
        PD_Batch["process_documents_batch (Method)"]
        PD_RAG["process_documents_with_rag_batch (Method)"]
    end

    subgraph "Code Entity Space (raganything/batch_parser.py)"
        BatchParser["BatchParser (Class)"]
        BP_Result["BatchProcessingResult (Dataclass)"]
        BP_Batch["process_batch (Method)"]
    end

    Folder --> PF_Complete
    Concurrent --> BatchParser
    Result --> BP_Result
    Filtering --> PD_Batch

    PF_Complete -.->|"Uses"| BatchMixin
    PD_Batch -->|"Delegates to"| BP_Batch
    PD_RAG -->|"Phase 1"| BP_Batch
    PD_RAG -->|"Phase 2"| ProcessorMixin["ProcessorMixin.process_document_complete"]
```
Sources: [raganything/batch.py:19-34](), [raganything/batch.py:177-185](), [raganything/batch_parser.py:22-59]()

---

## BatchParser and BatchProcessingResult

The `BatchParser` is a standalone utility class that handles the low-level concurrency of document parsing.

### BatchProcessingResult (Dataclass)

This class stores the outcome of a batch operation.

| Attribute | Type | Description |
|-----------|------|-------------|
| `successful_files` | `List[str]` | List of paths for successfully parsed files. |
| `failed_files` | `List[str]` | List of paths for files that encountered errors. |
| `total_files` | `int` | Count of all files attempted. |
| `processing_time` | `float` | Total duration of the batch in seconds. |
| `errors` | `Dict[str, str]` | Map of `file_path -> error_message`. |
| `output_dir` | `str` | Root directory where results were stored. |
| `dry_run` | `bool` | Whether the operation was a dry run. |

Sources: [raganything/batch_parser.py:22-31]()

### BatchParser Class

```python
class BatchParser:
    def __init__(
        self,
        parser_type: str = "mineru",
        max_workers: int = 4,
        show_progress: bool = True,
        timeout_per_file: int = 300,
        skip_installation_check: bool = False,
    )
```

**Key Methods:**
- `filter_supported_files(file_paths, recursive)`: Filters a list of paths to only include those matching the parser's supported extensions [raganything/batch_parser.py:110-156]().
- `process_batch(file_paths, output_dir, ...)`: Executes parallel parsing using a `ThreadPoolExecutor` [raganything/batch_parser.py:203-230]().

---

## BatchMixin Method Reference

### process_folder_complete

```python
async def process_folder_complete(
    self,
    folder_path: str,
    output_dir: str = None,
    parse_method: str = None,
    display_stats: bool = None,
    file_extensions: Optional[List[str]] = None,
    recursive: bool = None,
    max_workers: int = None,
    **kwargs
)
```

The original RAG-integrated batch method. It crawls a directory and calls `process_document_complete` for every matching file concurrently using an `asyncio.Semaphore`.

**Implementation Logic:**
1. **File Discovery**: Uses `Path.glob` or `Path.rglob` based on the `recursive` flag [raganything/batch.py:85-91]().
2. **Concurrency**: Creates an `asyncio.Semaphore(max_workers)` to limit active tasks [raganything/batch.py:106-110]().
3. **Execution**: Wraps each file in a `process_single_file` task and gathers them via `asyncio.gather` [raganything/batch.py:143-148]().

Sources: [raganything/batch.py:34-172]()

### process_documents_batch

```python
def process_documents_batch(
    self,
    file_paths: List[str],
    output_dir: Optional[str] = None,
    parse_method: Optional[str] = None,
    max_workers: Optional[int] = None,
    recursive: Optional[bool] = None,
    show_progress: bool = True,
    **kwargs,
) -> BatchProcessingResult
```

A synchronous wrapper that delegates parsing to `BatchParser`. It does **not** insert data into the Knowledge Graph; it only produces parsed files (Markdown/JSON) in the `output_dir`.

Sources: [raganything/batch.py:177-224]()

### process_documents_with_rag_batch

```python
async def process_documents_with_rag_batch(
    self,
    file_paths: List[str],
    output_dir: Optional[str] = None,
    parse_method: Optional[str] = None,
    max_workers: Optional[int] = None,
    recursive: Optional[bool] = None,
    show_progress: bool = True,
    **kwargs,
) -> Dict[str, Any]
```

The modern integrated workflow. It executes in two distinct phases:
1. **Phase 1 (Parsing)**: Calls `process_documents_batch_async` to generate all parsed content [raganything/batch.py:357-365]().
2. **Phase 2 (Indexing)**: Iterates through the `successful_files` from Phase 1 and calls `process_document_complete` to insert them into LightRAG [raganything/batch.py:378-385]().

Sources: [raganything/batch.py:302-405]()

---

## Concurrency and Data Flow

The following diagram illustrates how `BatchMixin` manages the flow of data from raw files to the RAG index.

```mermaid
sequenceDiagram
    participant User
    participant BM as BatchMixin
    participant BP as BatchParser
    participant PM as ProcessorMixin
    participant LR as LightRAG

    User->>BM: process_documents_with_rag_batch(files)
    BM->>BP: process_batch(files)
    Note over BP: Parallel Parsing (ThreadPool)
    BP-->>BM: BatchProcessingResult (successful_files)
    
    loop for file in successful_files
        BM->>PM: process_document_complete(file)
        PM->>LR: insert_content_list(parsed_data)
        Note over LR: KG Construction & Vector Indexing
        LR-->>PM: Done
        PM-->>BM: Success/Fail
    end
    
    BM-->>User: Combined Result Dict
```
Sources: [raganything/batch.py:357-405](), [raganything/batch_parser.py:203-230]()

---

## Utility Methods

### filter_supported_files
Filters a list of input paths (files or directories) and returns only those supported by the current parser backend (e.g., MinerU or Docling).
Sources: [raganything/batch.py:283-300](), [raganything/batch_parser.py:110-156]()

### get_supported_file_extensions
Queries the active parser to determine which file suffixes it can handle.
Sources: [raganything/batch.py:278-281](), [raganything/batch_parser.py:101-108]()

---

# Page: Advanced Topics

# Advanced Topics

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/linting.yaml](.github/workflows/linting.yaml)
- [docs/offline_setup.md](docs/offline_setup.md)
- [raganything/__init__.py](raganything/__init__.py)
- [scripts/create_tiktoken_cache.py](scripts/create_tiktoken_cache.py)

</details>



This section covers advanced usage patterns, customization techniques, and deployment strategies for RAG-Anything. These topics are intended for users who need to extend the system's capabilities, optimize performance, or deploy in specialized environments.

**Scope**: This page provides an architectural overview of extension points and advanced patterns. For detailed implementation guides, see:
- [Offline Deployment](#11.1) — Guide for deploying RAG-Anything with local models and no internet connectivity.
- [Performance Optimization](#11.2) — Tips for optimizing processing speed, memory usage, and query performance.
- [Custom Modal Processor Development](#11.3) — In-depth guide for developing custom modal processors for new content types.
- [Parser Extension](#11.4) — Guide for creating custom parser implementations using the parser registry.
- [Resilience and Error Handling](#11.5) — Documentation on retries, circuit breakers, and fault tolerance.
- [Callbacks and Observability](#11.6) — Monitoring the document processing lifecycle with hooks and metrics.
- [Prompt Management and Localization](#11.7) — Managing multilingual prompt templates and localization.

---

## Extension Point Architecture

RAG-Anything provides three primary extension points for customization: **parsers**, **modal processors**, and **context extractors**. Understanding these extension points is essential for advanced customization.

### System Extension Map

```mermaid
graph TB
    subgraph "Extension Point 1: Parser Layer"
        ParserBase["Parser<br/>(Base Class)<br/>raganything/parser.py"]
        MineruParser["MineruParser<br/>raganything/parser.py"]
        DoclingParser["DoclingParser<br/>raganything/parser.py"]
        PaddleOCRParser["PaddleOCRParser<br/>raganything/parser.py"]
        CustomParser["YourCustomParser<br/>(Extend Parser)"]
        
        ParserBase -.inherits.-> MineruParser
        ParserBase -.inherits.-> DoclingParser
        ParserBase -.inherits.-> PaddleOCRParser
        ParserBase -.inherits.-> CustomParser
    end
    
    subgraph "Extension Point 2: Modal Processor Layer"
        BaseModalProc["BaseModalProcessor<br/>raganything/modalprocessors.py"]
        ImageProc["ImageModalProcessor<br/>raganything/modalprocessors.py"]
        TableProc["TableModalProcessor<br/>raganything/modalprocessors.py"]
        EquationProc["EquationModalProcessor<br/>raganything/modalprocessors.py"]
        GenericProc["GenericModalProcessor<br/>raganything/modalprocessors.py"]
        CustomProc["YourCustomProcessor<br/>(Extend BaseModalProcessor)"]
        
        BaseModalProc -.inherits.-> ImageProc
        BaseModalProc -.inherits.-> TableProc
        BaseModalProc -.inherits.-> EquationProc
        BaseModalProc -.inherits.-> GenericProc
        BaseModalProc -.inherits.-> CustomProc
    end
    
    subgraph "Extension Point 3: Context Layer"
        ContextConfig["ContextConfig<br/>raganything/modalprocessors.py"]
        ContextExtractor["ContextExtractor<br/>raganything/modalprocessors.py"]
        CustomContext["Custom Context Strategy"]
        
        ContextConfig --> ContextExtractor
        ContextExtractor -.customize.-> CustomContext
    end
    
    subgraph "Core Integration"
        RAGAnything["RAGAnything<br/>(Core Orchestrator)"]
        LightRAG["LightRAG<br/>(Foundation)"]
    end
    
    ParserBase --> RAGAnything
    BaseModalProc --> RAGAnything
    ContextExtractor --> BaseModalProc
    RAGAnything --> LightRAG
```

**Sources**: [raganything/parser.py:49-1720](), [raganything/modalprocessors.py:33-1570]()

---

## Resilience and Observability

To ensure reliability in production environments, RAG-Anything includes optional modules for resilience (retries, circuit breakers) and observability (callbacks).

### Resilience Utilities
The system provides `retry`, `async_retry`, and `CircuitBreaker` patterns to handle transient failures in LLM APIs or network-bound operations. These are feature-gated and available if the resilience module is present.

### Callback System
The `ProcessingCallback` and `CallbackManager` allow developers to hook into the document processing lifecycle. This is useful for progress tracking, logging, or custom metrics collection.

```mermaid
graph LR
    subgraph "Observability Flow"
        Proc["ProcessorMixin"]
        CBManager["CallbackManager<br/>raganything/callbacks.py"]
        MetricsCB["MetricsCallback"]
        CustomCB["YourCustomCallback"]

        Proc -- "on_process_start" --> CBManager
        Proc -- "on_parse_end" --> CBManager
        Proc -- "on_multimodal_end" --> CBManager
        CBManager --> MetricsCB
        CBManager --> CustomCB
    end
```

**Sources**: [raganything/__init__.py:21-44](), [raganything/__init__.py:81-98]()

---

## Offline and Performance Strategies

### Offline Deployment
RAG-Anything can run in air-gapped environments. A critical step is handling the `tiktoken` network dependency by pre-caching models using `scripts/create_tiktoken_cache.py` and setting the `TIKTOKEN_CACHE_DIR` environment variable. For details, see [Offline Deployment](#11.1).

### Performance Tuning
Optimization targets include concurrency control (e.g., `MAX_ASYNC`), batch processing in `BatchMixin`, and caching mechanisms for both parsing and multimodal analysis. For details, see [Performance Optimization](#11.2).

### Resource Consumption Hierarchy

```mermaid
graph TD
    subgraph "Cost Centers"
        Parsing["Document Parsing<br/>(CPU/Memory Intensive)"]
        VLM["VLM/LLM Inference<br/>(Token/API Cost)"]
        Embedding["Embedding Generation<br/>(GPU/Inference)"]
        Graph["Graph Construction<br/>(I/O Intensive)"]
    end

    Parsing --- VLM
    VLM --- Embedding
    Embedding --- Graph

    style Parsing stroke-width:4px
    style VLM stroke-width:4px
```

**Sources**: [docs/offline_setup.md:1-79](), [scripts/create_tiktoken_cache.py:1-18]()

---

## Prompt Management and Localization

The `prompt_manager` provides a centralized way to handle multilingual prompts and template overrides. Users can switch between languages (e.g., English and Chinese) or register entirely new prompt sets without modifying core logic.

| Function | Purpose |
|----------|---------|
| `set_prompt_language` | Sets the global prompt language for the session. |
| `register_prompt_language` | Adds a new language mapping to the system. |
| `reset_prompts` | Reverts prompts to their default state. |

**Sources**: [raganything/__init__.py:48-58](), [raganything/__init__.py:100-109]()

---

## Next Steps

For detailed implementation guides on specific advanced topics:

- **Deploying without internet**: [Offline Deployment](#11.1)
- **Speeding up processing and queries**: [Performance Optimization](#11.2)
- **Creating custom content processors**: [Custom Modal Processor Development](#11.3)
- **Adding support for new file formats**: [Parser Extension](#11.4)
- **Implementing retries and error handling**: [Resilience and Error Handling](#11.5)
- **Monitoring with callbacks**: [Callbacks and Observability](#11.6)
- **Customizing prompt templates**: [Prompt Management and Localization](#11.7)

---

# Page: Offline Deployment

# Offline Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/linting.yaml](.github/workflows/linting.yaml)
- [.gitignore](.gitignore)
- [docs/offline_setup.md](docs/offline_setup.md)
- [env.example](env.example)
- [examples/lmstudio_integration_example.py](examples/lmstudio_integration_example.py)
- [scripts/create_tiktoken_cache.py](scripts/create_tiktoken_cache.py)

</details>



This document explains how to deploy and run RAG-Anything in air-gapped or network-restricted environments where internet access is unavailable. The primary challenge involves the `tiktoken` library's default behavior of downloading tokenizer models from OpenAI's servers on first use. This page covers the necessary steps to pre-cache these models and configure the system for fully offline operation.

For general configuration of RAG-Anything, see [RAGAnythingConfig](). For model provider setup, see [Model Provider Configuration]().

## Network Dependency Problem

RAG-Anything relies on the LightRAG framework, which uses OpenAI's `tiktoken` library for text tokenization. By default, `tiktoken` attempts to download tokenizer model files from `openaipublic.blob.core.windows.net` on its first use [docs/offline_setup.md:5-9](). In offline environments, this network call fails, preventing the LightRAG instance from initializing [docs/offline_setup.md:9-15]().

### Dependency Chain

The following diagram illustrates the relationship between code entities and the external network dependency.

**Tokenizer Dependency Graph**
```mermaid
graph TD
    RAGAnything["class RAGAnything (raganything/rag_anything.py)"]
    LightRAG["class LightRAG (lightrag/lightrag.py)"]
    tiktoken["tiktoken Library"]
    OpenAI["openaipublic.blob.core.windows.net"]
    
    RAGAnything --> |"initializes"| LightRAG
    LightRAG --> |"imports and uses"| tiktoken
    tiktoken --> |"downloads models from"| OpenAI
    
    OpenAI -.-> |"FAILS in offline env"| tiktoken
```

**Sources:** [docs/offline_setup.md:5-18](), [env.example:13-17]()

### Error Manifestation

When the network download fails, you will encounter an error similar to:

```
Failed to initialize LightRAG instance: HTTPSConnectionPool(host='openaipublic.blob.core.windows.net', port=443): 
Max retries exceeded with url: /encodings/o200k_base
```

This failure occurs during initialization, even though RAG-Anything itself does not directly import or call `tiktoken`. The dependency is indirect through the underlying library [docs/offline_setup.md:11-17]().

## Solution Overview

The solution involves creating a local cache of `tiktoken` models in an environment with internet access, then configuring the offline environment to use this cache instead of attempting network downloads. This is achieved through the `TIKTOKEN_CACHE_DIR` environment variable [docs/offline_setup.md:19-24]().

**Offline Workflow Architecture**
```mermaid
graph LR
    subgraph "Online Environment"
        Script["scripts/create_tiktoken_cache.py"]
        Cache["./tiktoken_cache/"]
        Internet["Internet"]
        
        Script --> |"tiktoken.get_encoding()"| Internet
        Script --> |"writes to"| Cache
    end
    
    subgraph "Offline Environment"
        ENV[".env file<br/>TIKTOKEN_CACHE_DIR=./tiktoken_cache"]
        tiktoken_offline["tiktoken library"]
        Cache_Copy["./tiktoken_cache/"]
        
        ENV --> |"os.environ['TIKTOKEN_CACHE_DIR']"| tiktoken_offline
        tiktoken_offline --> |"reads from"| Cache_Copy
    end
    
    Cache -.-> |"manual transfer"| Cache_Copy
```

**Sources:** [docs/offline_setup.md:19-24](), [scripts/create_tiktoken_cache.py:1-18]()

## Setting Up Offline Deployment

### Step 1: Create the Tiktoken Cache

In an environment **with internet access**, run the provided cache creation script:

```bash
uv run scripts/create_tiktoken_cache.py
```

This script performs the following operations:

| Operation | Description | Code Reference |
|-----------|-------------|----------------|
| Set cache directory | Defines `./tiktoken_cache` as the cache location | [scripts/create_tiktoken_cache.py:5-7]() |
| Create directory | Creates the cache directory if it doesn't exist | [scripts/create_tiktoken_cache.py:10-11]() |
| Download models | Downloads `cl100k_base` encoding (used by GPT-3.5/4) | [scripts/create_tiktoken_cache.py:14]() |
| Store locally | Saves model files to the cache directory | [scripts/create_tiktoken_cache.py:5-11]() |

**Sources:** [docs/offline_setup.md:26-34](), [scripts/create_tiktoken_cache.py:1-18]()

### Step 2: Transfer Cache to Offline Environment

Copy the entire `tiktoken_cache` directory from the online environment to your offline deployment environment. The directory structure should be preserved [docs/offline_setup.md:27-34]():

```
project_root/
├── tiktoken_cache/
│   └── [model files downloaded by script]
├── .env
└── [other project files]
```

**Sources:** [docs/offline_setup.md:27-34](), [.gitignore:69]()

### Step 3: Configure Environment Variable

Add the following line to your `.env` file in the offline environment:

```bash
TIKTOKEN_CACHE_DIR=./tiktoken_cache
```

This environment variable instructs `tiktoken` to read model files from the specified local directory instead of attempting network downloads [env.example:17]().

**Sources:** [docs/offline_setup.md:36-40](), [env.example:13-17]()

### Step 4: Ensure Proper Load Order

**Critical:** The `.env` file must be loaded **before** the code imports `tiktoken` (which happens inside LightRAG). This ensures the `TIKTOKEN_CACHE_DIR` environment variable is active when the library initializes [docs/offline_setup.md:42-43]().

**Initialization Sequence**
```mermaid
sequenceDiagram
    participant App as "Application Code"
    participant Dotenv as "dotenv.load_dotenv()"
    participant ENV as "os.environ"
    participant LR as "from lightrag import LightRAG"
    participant TT as "tiktoken library"
    
    App->>Dotenv: load_dotenv(dotenv_path=".env")
    Dotenv->>ENV: Set TIKTOKEN_CACHE_DIR
    
    Note over App,TT: Environment is now prepared for offline use
    
    App->>LR: Import LightRAG
    LR->>TT: Import tiktoken
    TT->>ENV: Check TIKTOKEN_CACHE_DIR
    TT->>TT: Load local files from directory
```

**Sources:** [docs/offline_setup.md:42-65]()

The initialization code should follow this pattern:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables FIRST - before any imports that use tiktoken
load_dotenv(dotenv_path=".env", override=False)

# Now import LightRAG (which will import tiktoken with the correct env var set)
from lightrag import LightRAG
```

**Sources:** [docs/offline_setup.md:44-64]()

## Testing Offline Setup

Follow these steps to verify your offline deployment is configured correctly [docs/offline_setup.md:67-78]():

1.  **Create a `tiktoken_cache` directory:** Run `scripts/create_tiktoken_cache.py` to populate the directory.
2.  **Set the variable:** Add `TIKTOKEN_CACHE_DIR=./tiktoken_cache` to your `.env` file.
3.  **Disconnect from the internet:** Disable network interfaces or use airplane mode.
4.  **Run the application:** Execute an example, such as `uv run examples/raganything_example.py requirements.txt`.

If the application initializes without an `HTTPSConnectionPool` error, the offline setup is successful.

**Sources:** [docs/offline_setup.md:67-78]()

## Tiktoken Models Cached

The `create_tiktoken_cache.py` script specifically targets the following:

| Encoding Name | Used By | Code Reference |
|---------------|---------|----------------|
| `cl100k_base` | GPT-3.5-Turbo, GPT-4, text-embedding-3-* | [scripts/create_tiktoken_cache.py:14]() |

Additional encodings like `p50k_base` (GPT-3, Codex) are commented out in the script but can be enabled if required by your specific local models [scripts/create_tiktoken_cache.py:15]().

**Sources:** [scripts/create_tiktoken_cache.py:14-15]()

## Local Model Integration

For a truly offline deployment, you must also use local LLM and Embedding providers. RAG-Anything supports several local backends:

*   **Ollama:** Configure via `EMBEDDING_BINDING=ollama` and `LLM_BINDING=ollama` [env.example:136-141]().
*   **LM Studio:** Use the OpenAI-compatible API provided by LM Studio [examples/lmstudio_integration_example.py:14-21]().
*   **vLLM:** Recommended for high-throughput production inference [env.example:127-132]().

Example `.env` for local LM Studio integration:
```bash
LLM_BINDING=lmstudio
LLM_MODEL=openai/gpt-oss-20b
LLM_BINDING_HOST=http://localhost:1234/v1
EMBEDDING_BINDING=lmstudio
EMBEDDING_MODEL=text-embedding-nomic-embed-text-v1.5
EMBEDDING_BINDING_HOST=http://localhost:1234/v1
TIKTOKEN_CACHE_DIR=./tiktoken_cache
```

**Sources:** [examples/lmstudio_integration_example.py:12-22](), [env.example:127-141]()

---

# Page: Performance Optimization

# Performance Optimization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [env.example](env.example)
- [examples/lmstudio_integration_example.py](examples/lmstudio_integration_example.py)
- [raganything/parser.py](raganything/parser.py)
- [raganything/processor.py](raganything/processor.py)
- [tests/test_insert_content_list.py](tests/test_insert_content_list.py)
- [tests/testparser_kwargs.py](tests/testparser_kwargs.py)

</details>



This document covers performance optimization techniques and configuration options for RAG-Anything. It explains caching strategies, batch processing, concurrency controls, and memory management that can significantly improve processing speed and resource utilization.

For configuration details, see **8. Configuration**. For storage backend optimization, see **8.3. Storage Backend Configuration**. For offline deployment optimization, see **11.1. Offline Deployment**.

---

## Overview of Performance Optimization Areas

RAG-Anything provides multiple optimization mechanisms across its five-stage processing pipeline. The main performance-critical areas are:

1.  **Parse Caching**: Avoid redundant document parsing through intelligent caching.
2.  **Batch Processing**: Process multimodal content in parallel batches instead of sequentially.
3.  **Concurrency Controls**: Configure parallelism for LLM calls, embeddings, and document processing.
4.  **LLM Call Optimization**: Cache responses and control API request concurrency.
5.  **Context Extraction**: Optimize context window size and token limits.
6.  **Memory Management**: Efficient handling of large documents and multimodal content.

### Performance Pipeline Architecture

The following diagram maps high-level optimization concepts to the specific code entities and variables that implement them.

```mermaid
graph TB
    subgraph "Stage 1: Document Parsing"
        ParseCache["parse_cache storage<br/>(KV Namespace)"]
        CacheKey["_generate_cache_key()<br/>[processor.py:50]"]
        Parser["Parser.parse_pdf()<br/>[parser.py:648]"]
        
        CacheKey -->|cache hit| ParseCache
        CacheKey -->|cache miss| Parser
        Parser --> ParseCache
    end
    
    subgraph "Stage 2-3: Content Processing"
        Separate["separate_content()<br/>[utils.py]"]
        TextInsert["ainsert()<br/>[LightRAG]"]
        BatchProc["_process_multimodal_content_batch_type_aware()<br/>[processor.py:706]"]
        Semaphore["asyncio.Semaphore<br/>(max_parallel_insert)"]
        
        Separate --> TextInsert
        Separate --> BatchProc
        Semaphore --> BatchProc
    end
    
    subgraph "Stage 4: Entity Extraction"
        LLMCache["llm_response_cache<br/>(KV Namespace)"]
        BatchExtract["_batch_extract_entities_lightrag_style_type_aware()<br/>[processor.py:1016]"]
        MaxAsync["MAX_ASYNC Control<br/>[env.example:113]"]
        
        LLMCache --> BatchExtract
        MaxAsync --> BatchExtract
    end
    
    subgraph "Stage 5: Storage & Indexing"
        BatchMerge["_batch_merge_lightrag_style_type_aware()<br/>[processor.py:1174]"]
        VectorBatch["EMBEDDING_BATCH_NUM<br/>[env.example:143]"]
        StorageOpt["Storage Backend<br/>(PostgreSQL/Neo4j/Milvus)"]
        
        BatchMerge --> VectorBatch
        VectorBatch --> StorageOpt
    end
    
    ParseCache -.cached results.-> Separate
    BatchProc --> BatchExtract
    BatchExtract --> BatchMerge
```

**Sources:** [raganything/processor.py:50-50](), [raganything/processor.py:706-706](), [raganything/processor.py:1016-1016](), [raganything/processor.py:1174-1174](), [raganything/parser.py:648-648](), [env.example:113-143]()

---

## Parse Caching System

The parse caching system prevents redundant parsing of documents by storing and reusing results in the `parse_cache` storage.

### Cache Key Generation

The `_generate_cache_key` method in `ProcessorMixin` creates a unique MD5 hash based on the file's state and the parser's configuration [raganything/processor.py:50-98]().

| Component | Purpose | Implementation |
| :--- | :--- | :--- |
| `file_path` | Unique file identifier | Absolute path string [raganything/processor.py:70-70]() |
| `mtime` | Detect file changes | `file_path.stat().st_mtime` [raganything/processor.py:66-66]() |
| `parser` | Parser backend | `self.config.parser` (mineru, docling, etc.) [raganything/processor.py:72-72]() |
| `parse_method` | Processing mode | `config.parse_method` (auto, ocr, txt) [raganything/processor.py:73-73]() |
| `relevant_kwargs` | Parser parameters | `lang`, `device`, `pages`, `formula`, `table` [raganything/processor.py:77-92]() |

### Docling Converter Cache
For the `DoclingParser`, RAG-Anything optimizes performance by caching the `DocumentConverter` instance. This avoids the heavy overhead of re-initializing the Docling model pipeline for every document [raganything/parser.py:1015-1044]().

```mermaid
flowchart TD
    Input["File Path + Config"]
    GenKey["_generate_cache_key()"]
    CheckCache{"Cache Hit?"}
    
    Input --> GenKey
    GenKey --> CheckCache
    CheckCache -->|Yes| Return["Return cached content_list"]
    CheckCache -->|No| RunParser["Parser.parse_document()"]
    
    subgraph Docling_Optimization["Docling Internal Cache"]
        RunParser --> GetConv["_get_converter()"]
        GetConv --> ConvExists{"Converter in<br/>_converter_cache?"}
        ConvExists -->|Yes| UseExisting["Use cached DocumentConverter"]
        ConvExists -->|No| InitNew["Initialize & cache<br/>DocumentConverter"]
    end
    
    RunParser --> Store["Store in parse_cache"]
```

**Sources:** [raganything/processor.py:50-98](), [raganything/parser.py:1015-1044]()

---

## Batch Processing Optimization

RAG-Anything implements `_process_multimodal_content_batch_type_aware` to maximize parallelism and minimize LLM API call overhead [raganything/processor.py:706-881]().

### Concurrency Control via Semaphores
The system uses an `asyncio.Semaphore` to limit concurrent multimodal processing tasks. The limit is derived from `max_parallel_insert` (defaulting to 2) [raganything/processor.py:732-732]().

### Optimization Comparison: Individual vs. Batch

| Metric | Individual Processing | Batch Processing |
| :--- | :--- | :--- |
| **LLM Description Calls** | Sequential or Uncontrolled | Controlled via `Semaphore` [raganything/processor.py:743-746]() |
| **Entity Extraction** | 1 Call per Item | 1 Batch Call for all items [raganything/processor.py:844-846]() |
| **Storage Ops** | Multiple per Item | Single Batch Upsert [raganything/processor.py:829-834]() |
| **KG Merging** | Separate operations | `_batch_merge_lightrag_style_type_aware` [raganything/processor.py:863-865]() |

**Sources:** [raganything/processor.py:706-881](), [raganything/processor.py:732-732](), [raganything/processor.py:743-746](), [raganything/processor.py:844-846](), [raganything/processor.py:863-865]()

---

## Concurrency Controls

Multiple environment variables and config fields control the system's parallel execution capabilities.

### Key Performance Variables

| Variable | Default | Purpose | File Pointer |
| :--- | :--- | :--- | :--- |
| `MAX_ASYNC` | 4 | Max concurrent LLM requests. | [env.example:113]() |
| `MAX_PARALLEL_INSERT` | 2 | Concurrent document processing tasks. | [env.example:100]() |
| `EMBEDDING_FUNC_MAX_ASYNC` | 16 | Concurrent embedding API calls. | [env.example:145]() |
| `EMBEDDING_BATCH_NUM` | 32 | Chunks per embedding request. | [env.example:143]() |
| `MAX_CONCURRENT_FILES` | 1 | Parallel files in `process_folder_complete`. | [env.example:54]() |

### Optimization Guidelines

1.  **For High-Throughput APIs (OpenAI/Azure)**: Increase `MAX_ASYNC` to 10-20 and `EMBEDDING_FUNC_MAX_ASYNC` to 32.
2.  **For Local Models (Ollama/LM Studio)**: Keep `MAX_ASYNC` low (1-4) to avoid GPU OOM or context contention. Set `EMBEDDING_BATCH_NUM` to 32+ to benefit from batch processing [examples/lmstudio_integration_example.py:167-173]().
3.  **Memory Constraints**: If processing large PDFs with many images, keep `MAX_PARALLEL_INSERT` at 1 or 2 to limit memory spikes during VLM description generation.

**Sources:** [env.example:54-145](), [examples/lmstudio_integration_example.py:167-173]()

---

## Context Extraction Optimization

The `ContextExtractor` determines how much surrounding text is sent to the VLM for describing images, tables, or equations.

### Token and Window Tuning
The `ContextConfig` class allows tuning the context window to balance description accuracy with token cost [raganything/config.py:76-105]().

*   **`context_mode`**: `page` (default) extracts surrounding pages; `chunk` extracts surrounding text chunks [raganything/config.py:81-81]().
*   **`context_window`**: Number of units (pages/chunks) to include before/after the item [raganything/config.py:79-79]().
*   **`max_context_tokens`**: Hard limit (default 2000) to prevent oversized LLM payloads [raganything/config.py:83-83]().

```mermaid
graph LR
    subgraph "Token Space"
        T1["Input Tokens"]
        T2["Output Tokens"]
    end
    
    subgraph "Code Entity Space"
        CE["ContextExtractor.extract_context()"]
        CC["ContextConfig"]
        MAX["MAX_CONTEXT_TOKENS"]
    end
    
    T1 --> CE
    CC --> CE
    MAX --> CE
    CE --> T2
```

**Sources:** [raganything/config.py:76-105](), [env.example:58-63]()

---

## Storage and Query Performance

### Vector DB Batching
When inserting text chunks, the system batches them according to `EMBEDDING_BATCH_NUM`. This is critical for remote embedding services where network latency per request is high [env.example:143]().

### Query Retrieval Tuning
Query performance is primarily affected by retrieval depth:
*   **`TOP_K`**: Number of text chunks retrieved (default 60) [env.example:86]().
*   **`MAX_GRAPH_NODES`**: Maximum nodes returned from graph retrieval (default 1000) [env.example:73]().
*   **`COSINE_THRESHOLD`**: Similarity filter; higher values (e.g., 0.3) speed up processing by ignoring low-relevance chunks [env.example:85]().

### LLM Response Caching
`ENABLE_LLM_CACHE` (default true) ensures that identical entity extraction prompts or summary requests do not hit the LLM twice, drastically speeding up the indexing of similar documents [env.example:106-107]().

**Sources:** [env.example:73-143]()

---

# Page: Custom Modal Processor Development

# Custom Modal Processor Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/context_aware_processing.md](docs/context_aware_processing.md)
- [examples/insert_content_list_example.py](examples/insert_content_list_example.py)
- [examples/modalprocessors_example.py](examples/modalprocessors_example.py)
- [raganything/modalprocessors.py](raganything/modalprocessors.py)
- [tests/test_embedding_examples.py](tests/test_embedding_examples.py)

</details>



This page provides an in-depth guide for developing custom modal processors to handle new content types in RAG-Anything. Custom modal processors enable the system to process, analyze, and index specialized content formats beyond the built-in image, table, and equation processors.

For an overview of the modal processor architecture and built-in processors, see [Modal Processor Architecture](#5.1). For specific implementations of existing processors, see [Image Processing](#5.2), [Table Processing](#5.3), and [Equation Processing](#5.4). For API reference, see [Modal Processors API](#10.3).

---

## Architecture Overview

The modal processor system follows a class-based inheritance pattern where all processors extend `BaseModalProcessor` and implement specific content handling logic.

### Class Hierarchy

```mermaid
graph TB
    Base["BaseModalProcessor<br/>(raganything/modalprocessors.py:360-794)"]
    
    Image["ImageModalProcessor<br/>(796-1030)"]
    Table["TableModalProcessor<br/>(1032-1223)"]
    Equation["EquationModalProcessor<br/>(1226-1407)"]
    Generic["GenericModalProcessor<br/>(1410-1569)"]
    Custom["CustomModalProcessor<br/>(Your Implementation)"]
    
    Base --> Image
    Base --> Table
    Base --> Equation
    Base --> Generic
    Base --> Custom
    
    subgraph "Core Components"
        Context["ContextExtractor<br/>(49-358)"]
        LightRAG["LightRAG Instance"]
        Storage["Storage Backends<br/>(text_chunks_db, chunks_vdb,<br/>entities_vdb, relationships_vdb,<br/>knowledge_graph_inst)"]
    end
    
    Base --> Context
    Base --> LightRAG
    Base --> Storage
```

**Sources:** [raganything/modalprocessors.py:360-794](), [raganything/modalprocessors.py:49-358]()

---

## BaseModalProcessor Components

### Required Dependencies

Every `BaseModalProcessor` instance receives and manages several core components:

| Component | Type | Purpose |
|-----------|------|---------|
| `lightrag` | `LightRAG` | Core RAG system instance |
| `modal_caption_func` | Callable | LLM/VLM function for content analysis |
| `context_extractor` | `ContextExtractor` | Extracts surrounding document context |
| `text_chunks_db` | Storage | Text chunk storage backend |
| `chunks_vdb` | VectorStorage | Vector database for chunks |
| `entities_vdb` | VectorStorage | Vector database for entities |
| `relationships_vdb` | VectorStorage | Vector database for relationships |
| `knowledge_graph_inst` | GraphStorage | Knowledge graph storage |
| `embedding_func` | Callable | Embedding generation function |
| `llm_model_func` | Callable | LLM function for extraction |
| `tokenizer` | Tokenizer | Token counting and encoding |

**Sources:** [raganything/modalprocessors.py:363-401]()

### Initialization Pattern

```mermaid
flowchart LR
    Init["__init__()"]
    SetRefs["Set Storage References<br/>(text_chunks_db, chunks_vdb,<br/>entities_vdb, etc.)"]
    SetFuncs["Set Function References<br/>(embedding_func,<br/>llm_model_func, etc.)"]
    InitContext["Initialize ContextExtractor<br/>with tokenizer"]
    SetSource["Initialize content_source<br/>and content_format"]
    
    Init --> SetRefs
    SetRefs --> SetFuncs
    SetFuncs --> InitContext
    InitContext --> SetSource
```

**Sources:** [raganything/modalprocessors.py:363-404]()

---

## Required Methods

Custom modal processors must implement two primary methods:

### 1. generate_description_only()

Generates text descriptions and entity information without performing entity extraction. Used in batch processing Stage 1.

**Signature:**
```python
async def generate_description_only(
    self,
    modal_content: Any,
    content_type: str,
    item_info: Dict[str, Any] = None,
    entity_name: str = None,
) -> Tuple[str, Dict[str, Any]]:
```

**Returns:**
- `Tuple[str, Dict[str, Any]]`: (enhanced_description, entity_info)

**entity_info Structure:**
```python
{
    "entity_name": str,  # Unique identifier for the entity
    "entity_type": str,  # Content type classification
    "summary": str       # Concise summary (max 100 words)
}
```

**Sources:** [raganything/modalprocessors.py:442-463]()

### 2. process_multimodal_content()

Complete processing pipeline including description generation, entity creation, chunk storage, and knowledge graph integration.

**Signature:**
```python
async def process_multimodal_content(
    self,
    modal_content: Any,
    content_type: str,
    file_path: str = "manual_creation",
    entity_name: str = None,
    item_info: Dict[str, Any] = None,
    batch_mode: bool = False,
    doc_id: str = None,
    chunk_order_index: int = 0,
) -> Tuple[str, Dict[str, Any]]:
```

**Returns:**
- `Tuple[str, Dict[str, Any], List]`: (description, entity_info, chunk_results)

**Sources:** [raganything/modalprocessors.py:930-991]() (ImageModalProcessor example)

---

## Development Workflow

### Step 1: Define Content Structure

Identify the structure of your custom content type and define how it will be represented.

**Example Content Structure:**
```python
# Audio content example
audio_content = {
    "audio_path": "/path/to/audio.mp3",
    "duration": 120.5,
    "transcript": "...",
    "speakers": ["Speaker A", "Speaker B"],
    "audio_caption": ["Interview recording"],
}
```

### Step 2: Create Processor Class

```mermaid
flowchart TB
    Start["Define Custom Processor Class"]
    Inherit["Inherit from BaseModalProcessor"]
    InitMethod["Implement __init__()<br/>Call super().__init__()"]
    GenDesc["Implement generate_description_only()"]
    Process["Implement process_multimodal_content()"]
    Parse["Implement _parse_response()"]
    Done["Custom Processor Complete"]
    
    Start --> Inherit
    Inherit --> InitMethod
    InitMethod --> GenDesc
    GenDesc --> Process
    Process --> Parse
    Parse --> Done
```

**Sources:** [raganything/modalprocessors.py:360-401](), [raganything/modalprocessors.py:796-812]()

### Step 3: Implement generate_description_only()

This method handles content analysis and description generation.

**Implementation Pattern:**

```mermaid
flowchart TB
    Input["Parse modal_content<br/>Extract fields"]
    Validate["Validate required fields<br/>Check file existence"]
    Context["Extract context using<br/>_get_context_for_item()"]
    Prompt["Build analysis prompt<br/>from PROMPTS template"]
    LLM["Call modal_caption_func()<br/>with prompt and system_prompt"]
    Parse["Parse JSON response<br/>using _robust_json_parse()"]
    Return["Return (description, entity_info)"]
    Error["Handle exceptions<br/>Return fallback entity"]
    
    Input --> Validate
    Validate --> Context
    Context --> Prompt
    Prompt --> LLM
    LLM --> Parse
    Parse --> Return
    Validate -->|Error| Error
    LLM -->|Error| Error
    Parse -->|Error| Error
    Error --> Return
```

**Key Components:**

1. **Content Parsing:**
```python
# Handle both string and dict formats
if isinstance(modal_content, str):
    try:
        content_data = json.loads(modal_content)
    except json.JSONDecodeError:
        content_data = {"field": modal_content}
else:
    content_data = modal_content
```

2. **Context Extraction:**
```python
# Extract context for current item
context = ""
if item_info:
    context = self._get_context_for_item(item_info)
```

3. **Prompt Construction:**
```python
# Build analysis prompt with or without context
if context:
    prompt = PROMPTS.get(
        "custom_prompt_with_context", PROMPTS["custom_prompt"]
    ).format(
        context=context,
        entity_name=entity_name or "descriptive name",
        **content_fields
    )
else:
    prompt = PROMPTS["custom_prompt"].format(
        entity_name=entity_name or "descriptive name",
        **content_fields
    )
```

4. **LLM Invocation:**
```python
# Call analysis function
response = await self.modal_caption_func(
    prompt,
    system_prompt=PROMPTS["CUSTOM_ANALYSIS_SYSTEM"],
)
```

5. **Response Parsing:**
```python
# Parse response using robust parser
enhanced_description, entity_info = self._parse_custom_response(
    response, entity_name
)
```

**Sources:** [raganything/modalprocessors.py:824-928]() (ImageModalProcessor example), [raganything/modalprocessors.py:1035-1123]() (TableModalProcessor example)

### Step 4: Implement process_multimodal_content()

This method orchestrates the complete processing pipeline.

**Processing Pipeline:**

```mermaid
flowchart TB
    Call["process_multimodal_content() called"]
    GenDesc["Call generate_description_only()<br/>Get (description, entity_info)"]
    Parse["Parse modal_content<br/>Extract all fields"]
    Build["Build modal_chunk text<br/>using PROMPTS template"]
    Create["Call _create_entity_and_chunk()<br/>Store in all backends"]
    Extract["_process_chunk_for_extraction()<br/>Extract entities & relationships"]
    BelongsTo["Create belongs_to relationships<br/>Link extracted entities to modal entity"]
    Return["Return (description, entity_info, chunk_results)"]
    
    Call --> GenDesc
    GenDesc --> Parse
    Parse --> Build
    Build --> Create
    Create --> Extract
    Extract --> BelongsTo
    BelongsTo --> Return
```

**Implementation Template:**
```python
async def process_multimodal_content(
    self,
    modal_content,
    content_type: str,
    file_path: str = "manual_creation",
    entity_name: str = None,
    item_info: Dict[str, Any] = None,
    batch_mode: bool = False,
    doc_id: str = None,
    chunk_order_index: int = 0,
) -> Tuple[str, Dict[str, Any]]:
    try:
        # Step 1: Generate description and entity info
        enhanced_description, entity_info = await self.generate_description_only(
            modal_content, content_type, item_info, entity_name
        )
        
        # Step 2: Parse content for building complete chunk
        if isinstance(modal_content, str):
            try:
                content_data = json.loads(modal_content)
            except json.JSONDecodeError:
                content_data = {"content": modal_content}
        else:
            content_data = modal_content
        
        # Extract fields from content_data
        field1 = content_data.get("field1", "")
        field2 = content_data.get("field2", "")
        
        # Step 3: Build complete content chunk
        modal_chunk = PROMPTS["custom_chunk"].format(
            field1=field1,
            field2=field2,
            enhanced_description=enhanced_description,
        )
        
        # Step 4: Create entity and chunk (handles storage)
        return await self._create_entity_and_chunk(
            modal_chunk,
            entity_info,
            file_path,
            batch_mode,
            doc_id,
            chunk_order_index,
        )
        
    except Exception as e:
        logger.error(f"Error processing {content_type} content: {e}")
        # Return fallback entity
        fallback_entity = {
            "entity_name": entity_name or f"{content_type}_{compute_mdhash_id(str(modal_content))}",
            "entity_type": content_type,
            "summary": f"{content_type} content: {str(modal_content)[:100]}",
        }
        return str(modal_content), fallback_entity
```

**Sources:** [raganything/modalprocessors.py:930-991]() (ImageModalProcessor), [raganything/modalprocessors.py:1125-1185]() (TableModalProcessor)

### Step 5: Implement Response Parsing

Create a method to parse LLM responses with robust error handling.

**Parsing Method Pattern:**

```mermaid
flowchart TB
    Input["_parse_custom_response(response, entity_name)"]
    Robust["Call _robust_json_parse(response)<br/>Handles malformed JSON"]
    Extract["Extract required fields:<br/>detailed_description, entity_info"]
    Validate["Validate field presence:<br/>entity_name, entity_type, summary"]
    Format["Format entity_name:<br/>Add (entity_type) suffix"]
    Override["Override with provided entity_name<br/>if specified"]
    Return["Return (description, entity_info)"]
    Error["Catch exceptions<br/>Return fallback entity"]
    
    Input --> Robust
    Robust --> Extract
    Extract --> Validate
    Validate --> Format
    Format --> Override
    Override --> Return
    Extract -->|Error| Error
    Validate -->|Error| Error
    Error --> Return
```

**Implementation:**
```python
def _parse_custom_response(
    self, response: str, entity_name: str = None
) -> Tuple[str, Dict[str, Any]]:
    """Parse custom content analysis response"""
    try:
        # Use inherited robust JSON parser
        response_data = self._robust_json_parse(response)
        
        # Extract required fields
        description = response_data.get("detailed_description", "")
        entity_data = response_data.get("entity_info", {})
        
        # Validate presence
        if not description or not entity_data:
            raise ValueError("Missing required fields in response")
        
        if not all(
            key in entity_data for key in ["entity_name", "entity_type", "summary"]
        ):
            raise ValueError("Missing required fields in entity_info")
        
        # Format entity name with type
        entity_data["entity_name"] = (
            entity_data["entity_name"] + f" ({entity_data['entity_type']})"
        )
        
        # Override with provided name if specified
        if entity_name:
            entity_data["entity_name"] = entity_name
        
        return description, entity_data
        
    except (json.JSONDecodeError, AttributeError, ValueError) as e:
        logger.error(f"Error parsing custom content response: {e}")
        logger.debug(f"Raw response: {response}")
        
        # Return fallback entity
        fallback_entity = {
            "entity_name": entity_name or f"custom_{compute_mdhash_id(response)}",
            "entity_type": "custom",
            "summary": response[:100] + "..." if len(response) > 100 else response,
        }
        return response, fallback_entity
```

**Sources:** [raganything/modalprocessors.py:993-1029]() (ImageModalProcessor), [raganything/modalprocessors.py:547-698]() (BaseModalProcessor robust parsing)

---

## Prompt Templates

Custom processors require prompt templates defined in `PROMPTS` dictionary.

### Required Prompt Types

| Prompt Key | Purpose | Context Support |
|------------|---------|-----------------|
| `custom_prompt` | Basic analysis prompt | No |
| `custom_prompt_with_context` | Context-aware analysis prompt | Yes |
| `CUSTOM_ANALYSIS_SYSTEM` | System prompt for LLM | N/A |
| `custom_chunk` | Chunk formatting template | N/A |

### Prompt Structure

**Basic Prompt Template:**
```python
PROMPTS["custom_prompt"] = """Please analyze this {content_type} content and provide a JSON response with the following structure:

{{
    "detailed_description": "A comprehensive analysis of the content including:
    - Content structure and organization
    - Key information and elements
    - Relationships between components
    - Context and significance
    - Relevant details for knowledge retrieval",
    "entity_info": {{
        "entity_name": "{entity_name}",
        "entity_type": "{content_type}",
        "summary": "concise summary (max 100 words)"
    }}
}}

Content Information:
{content_fields}

Focus on extracting meaningful information for knowledge retrieval."""
```

**Context-Aware Prompt Template:**
```python
PROMPTS["custom_prompt_with_context"] = """Please analyze this {content_type} content considering the surrounding context, and provide a JSON response:

{{
    "detailed_description": "Comprehensive analysis including:
    - Content structure and key elements
    - Relationships to surrounding context
    - How this content supports the broader discussion
    - Relevant details for knowledge retrieval",
    "entity_info": {{
        "entity_name": "{entity_name}",
        "entity_type": "{content_type}",
        "summary": "concise summary including context relationship (max 100 words)"
    }}
}}

Context from surrounding content:
{context}

Content Information:
{content_fields}"""
```

**System Prompt:**
```python
PROMPTS["CUSTOM_ANALYSIS_SYSTEM"] = (
    "You are an expert {content_type} analyst. Provide detailed, accurate analysis."
)
```

**Chunk Template:**
```python
PROMPTS["custom_chunk"] = """{content_type} Content Analysis:
Field1: {field1}
Field2: {field2}

Analysis: {enhanced_description}"""
```

**Sources:** [raganything/prompt.py:1-354]()

---

## Context Integration

Custom processors inherit context extraction capabilities from `BaseModalProcessor`.

### Context Extraction Flow

```mermaid
flowchart TB
    Set["set_content_source()<br/>Store content_source and format"]
    Get["_get_context_for_item(item_info)<br/>Called during processing"]
    Extract["context_extractor.extract_context()<br/>Extract surrounding content"]
    Mode{Context Mode?}
    Page["Page-based extraction<br/>(±N pages)"]
    Chunk["Chunk-based extraction<br/>(±N chunks)"]
    Token["Token-limited extraction<br/>(max tokens)"]
    Truncate["Truncate to max_context_tokens<br/>Preserve sentence boundaries"]
    Return["Return context string"]
    
    Set --> Get
    Get --> Extract
    Extract --> Mode
    Mode -->|page| Page
    Mode -->|chunk| Chunk
    Mode -->|token| Token
    Page --> Truncate
    Chunk --> Truncate
    Token --> Truncate
    Truncate --> Return
```

### Using Context in Processors

**Setting Content Source:**
```python
# Before processing, set the content source
processor.set_content_source(
    content_source=content_list,  # Full document content
    content_format="minerU"        # Format hint
)
```

**Extracting Context:**
```python
# Inside generate_description_only()
context = ""
if item_info:
    context = self._get_context_for_item(item_info)
```

**item_info Structure:**
```python
item_info = {
    "page_idx": 5,        # Current page index
    "index": 10,          # Current item index
    # Additional fields as needed
}
```

**Sources:** [raganything/modalprocessors.py:406-440](), [raganything/modalprocessors.py:49-358]()

---

## Storage Integration

The `_create_entity_and_chunk()` method handles all storage operations.

### Storage Pipeline

```mermaid
flowchart TB
    Input["_create_entity_and_chunk()<br/>modal_chunk, entity_info, file_path"]
    
    subgraph "Chunk Storage"
        GenID["Generate chunk_id<br/>using compute_mdhash_id()"]
        Count["Count tokens<br/>using tokenizer"]
        ChunkData["Build chunk_data dict<br/>with tokens, content, file_path"]
        StoreChunk["Store in text_chunks_db"]
        StoreVec["Store in chunks_vdb"]
    end
    
    subgraph "Entity Storage"
        NodeData["Build node_data dict<br/>with entity info"]
        StoreNode["Store in knowledge_graph_inst"]
        EntData["Build entity_vdb_data"]
        StoreEnt["Store in entities_vdb"]
    end
    
    subgraph "Relation Extraction"
        Extract["_process_chunk_for_extraction()<br/>Extract entities & relationships"]
        BelongsTo["Create belongs_to edges<br/>Link to modal entity"]
        StoreRel["Store in relationships_vdb"]
    end
    
    Return["Return (description, entity_info, chunk_results)"]
    
    Input --> GenID
    GenID --> Count
    Count --> ChunkData
    ChunkData --> StoreChunk
    StoreChunk --> StoreVec
    StoreVec --> NodeData
    NodeData --> StoreNode
    StoreNode --> EntData
    EntData --> StoreEnt
    StoreEnt --> Extract
    Extract --> BelongsTo
    BelongsTo --> StoreRel
    StoreRel --> Return
```

**Storage Targets:**

| Storage | Purpose | Data Format |
|---------|---------|-------------|
| `text_chunks_db` | Text chunk metadata | `{chunk_id: {tokens, content, chunk_order_index, full_doc_id, file_path}}` |
| `chunks_vdb` | Vector embeddings for chunks | `{chunk_id: {content, full_doc_id, tokens, chunk_order_index, file_path}}` |
| `knowledge_graph_inst` | Graph nodes | `{entity_id, entity_type, description, source_id, file_path, created_at}` |
| `entities_vdb` | Vector embeddings for entities | `{entity_id: {entity_name, entity_type, content, source_id, file_path}}` |
| `relationships_vdb` | Vector embeddings for relationships | `{relation_id: {src_id, tgt_id, keywords, content, source_id, file_path}}` |

**Sources:** [raganything/modalprocessors.py:465-545](), [raganything/modalprocessors.py:699-793]()

---

## Complete Example: AudioModalProcessor

Here is a complete example implementing a custom processor for audio content.

### Class Definition

```python
class AudioModalProcessor(BaseModalProcessor):
    """Processor specialized for audio content"""
    
    async def generate_description_only(
        self,
        modal_content,
        content_type: str,
        item_info: Dict[str, Any] = None,
        entity_name: str = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """Generate audio description and entity info"""
        try:
            # Parse audio content
            if isinstance(modal_content, str):
                try:
                    content_data = json.loads(modal_content)
                except json.JSONDecodeError:
                    content_data = {"transcript": modal_content}
            else:
                content_data = modal_content
            
            # Extract audio fields
            audio_path = content_data.get("audio_path", "")
            duration = content_data.get("duration", 0)
            transcript = content_data.get("transcript", "")
            speakers = content_data.get("speakers", [])
            audio_caption = content_data.get("audio_caption", [])
            
            # Validate required fields
            if not transcript:
                raise ValueError(
                    f"No transcript provided in modal_content: {modal_content}"
                )
            
            # Extract context
            context = ""
            if item_info:
                context = self._get_context_for_item(item_info)
            
            # Build analysis prompt
            if context:
                audio_prompt = PROMPTS.get(
                    "audio_prompt_with_context", PROMPTS["audio_prompt"]
                ).format(
                    context=context,
                    entity_name=entity_name or "descriptive name for this audio",
                    audio_path=audio_path,
                    duration=duration,
                    transcript=transcript,
                    speakers=", ".join(speakers) if speakers else "Unknown",
                    audio_caption=", ".join(audio_caption) if audio_caption else "None",
                )
            else:
                audio_prompt = PROMPTS["audio_prompt"].format(
                    entity_name=entity_name or "descriptive name for this audio",
                    audio_path=audio_path,
                    duration=duration,
                    transcript=transcript,
                    speakers=", ".join(speakers) if speakers else "Unknown",
                    audio_caption=", ".join(audio_caption) if audio_caption else "None",
                )
            
            # Call LLM for audio analysis
            response = await self.modal_caption_func(
                audio_prompt,
                system_prompt=PROMPTS["AUDIO_ANALYSIS_SYSTEM"],
            )
            
            # Parse response
            enhanced_description, entity_info = self._parse_audio_response(
                response, entity_name
            )
            
            return enhanced_description, entity_info
            
        except Exception as e:
            logger.error(f"Error generating audio description: {e}")
            # Fallback entity
            fallback_entity = {
                "entity_name": entity_name or f"audio_{compute_mdhash_id(str(modal_content))}",
                "entity_type": "audio",
                "summary": f"Audio content: {str(modal_content)[:100]}",
            }
            return str(modal_content), fallback_entity
    
    async def process_multimodal_content(
        self,
        modal_content,
        content_type: str,
        file_path: str = "manual_creation",
        entity_name: str = None,
        item_info: Dict[str, Any] = None,
        batch_mode: bool = False,
        doc_id: str = None,
        chunk_order_index: int = 0,
    ) -> Tuple[str, Dict[str, Any]]:
        """Process audio content with context support"""
        try:
            # Generate description and entity info
            enhanced_description, entity_info = await self.generate_description_only(
                modal_content, content_type, item_info, entity_name
            )
            
            # Parse content for building complete chunk
            if isinstance(modal_content, str):
                try:
                    content_data = json.loads(modal_content)
                except json.JSONDecodeError:
                    content_data = {"transcript": modal_content}
            else:
                content_data = modal_content
            
            audio_path = content_data.get("audio_path", "")
            duration = content_data.get("duration", 0)
            transcript = content_data.get("transcript", "")
            speakers = content_data.get("speakers", [])
            audio_caption = content_data.get("audio_caption", [])
            
            # Build complete audio content
            modal_chunk = PROMPTS["audio_chunk"].format(
                audio_path=audio_path,
                duration=duration,
                transcript=transcript,
                speakers=", ".join(speakers) if speakers else "Unknown",
                audio_caption=", ".join(audio_caption) if audio_caption else "None",
                enhanced_description=enhanced_description,
            )
            
            return await self._create_entity_and_chunk(
                modal_chunk,
                entity_info,
                file_path,
                batch_mode,
                doc_id,
                chunk_order_index,
            )
            
        except Exception as e:
            logger.error(f"Error processing audio content: {e}")
            # Fallback entity
            fallback_entity = {
                "entity_name": entity_name or f"audio_{compute_mdhash_id(str(modal_content))}",
                "entity_type": "audio",
                "summary": f"Audio content: {str(modal_content)[:100]}",
            }
            return str(modal_content), fallback_entity
    
    def _parse_audio_response(
        self, response: str, entity_name: str = None
    ) -> Tuple[str, Dict[str, Any]]:
        """Parse audio analysis response"""
        try:
            response_data = self._robust_json_parse(response)
            
            description = response_data.get("detailed_description", "")
            entity_data = response_data.get("entity_info", {})
            
            if not description or not entity_data:
                raise ValueError("Missing required fields in response")
            
            if not all(
                key in entity_data for key in ["entity_name", "entity_type", "summary"]
            ):
                raise ValueError("Missing required fields in entity_info")
            
            entity_data["entity_name"] = (
                entity_data["entity_name"] + f" ({entity_data['entity_type']})"
            )
            if entity_name:
                entity_data["entity_name"] = entity_name
            
            return description, entity_data
            
        except (json.JSONDecodeError, AttributeError, ValueError) as e:
            logger.error(f"Error parsing audio analysis response: {e}")
            logger.debug(f"Raw response: {response}")
            fallback_entity = {
                "entity_name": entity_name or f"audio_{compute_mdhash_id(response)}",
                "entity_type": "audio",
                "summary": response[:100] + "..." if len(response) > 100 else response,
            }
            return response, fallback_entity
```

### Prompt Templates

```python
# Add to raganything/prompt.py

PROMPTS["AUDIO_ANALYSIS_SYSTEM"] = (
    "You are an expert audio content analyst. Provide detailed, accurate transcription analysis."
)

PROMPTS["audio_prompt"] = """Please analyze this audio content and provide a JSON response:

{{
    "detailed_description": "A comprehensive analysis of the audio including:
    - Main topics and themes discussed
    - Key points and conclusions
    - Speaker contributions and perspectives
    - Tone and communication style
    - Context and significance of the discussion
    - Important quotes or statements",
    "entity_info": {{
        "entity_name": "{entity_name}",
        "entity_type": "audio",
        "summary": "concise summary of audio content (max 100 words)"
    }}
}}

Audio Information:
Path: {audio_path}
Duration: {duration} seconds
Speakers: {speakers}
Caption: {audio_caption}

Transcript:
{transcript}"""

PROMPTS["audio_prompt_with_context"] = """Please analyze this audio content considering the surrounding context:

{{
    "detailed_description": "Comprehensive analysis including:
    - Main topics and themes discussed
    - Key points and their relationship to surrounding content
    - Speaker contributions and perspectives
    - How this audio relates to the broader discussion
    - Important quotes or statements
    - Context connections",
    "entity_info": {{
        "entity_name": "{entity_name}",
        "entity_type": "audio",
        "summary": "concise summary including context relationship (max 100 words)"
    }}
}}

Context from surrounding content:
{context}

Audio Information:
Path: {audio_path}
Duration: {duration} seconds
Speakers: {speakers}
Caption: {audio_caption}

Transcript:
{transcript}"""

PROMPTS["audio_chunk"] = """Audio Content Analysis:
Path: {audio_path}
Duration: {duration} seconds
Speakers: {speakers}
Caption: {audio_caption}

Transcript:
{transcript}

Analysis: {enhanced_description}"""
```

**Sources:** Based on patterns from [raganything/modalprocessors.py:796-1030](), [raganything/modalprocessors.py:1032-1223](), [raganything/prompt.py:1-354]()

---

## Integration with RAGAnything

### Registration Pattern

Custom processors are typically instantiated and used within `ProcessorMixin` methods.

```mermaid
flowchart TB
    Init["RAGAnything Initialization"]
    Create["Create modal processor instances<br/>(ImageModalProcessor, TableModalProcessor, etc.)"]
    Custom["Instantiate custom processor<br/>AudioModalProcessor(lightrag, modal_caption_func)"]
    Map["Map content types to processors<br/>in processor_map"]
    Process["process_content_list() called"]
    Route["Route content by type<br/>to appropriate processor"]
    Custom2["Custom processor handles<br/>custom content type"]
    
    Init --> Create
    Create --> Custom
    Custom --> Map
    Map --> Process
    Process --> Route
    Route --> Custom2
```

**Example Integration:**
```python
# In RAGAnything or ProcessorMixin initialization
self.audio_processor = AudioModalProcessor(
    lightrag=self.lightrag,
    modal_caption_func=self.llm_model_func,  # or vision_model_func
    context_extractor=self.context_extractor,
)

# Map content type to processor
self.processor_map = {
    "image": self.image_processor,
    "table": self.table_processor,
    "equation": self.equation_processor,
    "audio": self.audio_processor,  # Custom processor
    # ... other processors
}

# During processing
content_type = item.get("type")
processor = self.processor_map.get(content_type)
if processor:
    result = await processor.process_multimodal_content(
        modal_content=item,
        content_type=content_type,
        file_path=file_path,
        item_info={"page_idx": item.get("page_idx"), "index": idx},
    )
```

**Sources:** Based on patterns from [raganything/modalprocessors.py:360-401]()

---

## Best Practices

### Error Handling

1. **Wrap all operations in try-except blocks**
2. **Always provide fallback entities** for graceful degradation
3. **Log errors with detailed context** for debugging
4. **Validate input data** before processing

```python
try:
    # Processing logic
    result = await self.process_content(...)
except FileNotFoundError as e:
    logger.error(f"File not found: {e}")
    return self._create_fallback_entity()
except json.JSONDecodeError as e:
    logger.error(f"JSON parsing failed: {e}")
    return self._create_fallback_entity()
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    return self._create_fallback_entity()
```

### Prompt Design

1. **Request structured JSON output** with clear field definitions
2. **Provide specific instructions** for analysis
3. **Include context when available** for better understanding
4. **Use consistent field names** across all prompts
5. **Specify entity_name format** requirements

### Performance Optimization

1. **Use batch_mode flag** to defer expensive operations
2. **Cache LLM responses** using built-in `hashing_kv`
3. **Minimize redundant context extraction**
4. **Validate required fields early** before calling LLM

### Content Validation

1. **Check for required fields** before processing
2. **Validate file paths** if handling external resources
3. **Handle both string and dict inputs** consistently
4. **Provide meaningful error messages**

**Sources:** [raganything/modalprocessors.py:547-698]() (robust parsing strategies), [raganything/modalprocessors.py:824-928]() (error handling patterns)

---

## Testing Custom Processors

### Unit Test Structure

```python
import pytest
from raganything.modalprocessors import BaseModalProcessor
from your_module import AudioModalProcessor

@pytest.fixture
async def audio_processor(lightrag_instance, mock_llm_func):
    """Create audio processor instance for testing"""
    processor = AudioModalProcessor(
        lightrag=lightrag_instance,
        modal_caption_func=mock_llm_func,
    )
    return processor

@pytest.mark.asyncio
async def test_generate_description_only(audio_processor):
    """Test description generation"""
    modal_content = {
        "audio_path": "/path/to/test.mp3",
        "duration": 60.0,
        "transcript": "Test transcript content",
        "speakers": ["Speaker A"],
    }
    
    description, entity_info = await audio_processor.generate_description_only(
        modal_content=modal_content,
        content_type="audio",
    )
    
    assert description is not None
    assert entity_info["entity_type"] == "audio"
    assert "entity_name" in entity_info
    assert "summary" in entity_info

@pytest.mark.asyncio
async def test_process_multimodal_content(audio_processor):
    """Test complete processing pipeline"""
    modal_content = {
        "audio_path": "/path/to/test.mp3",
        "transcript": "Test transcript",
    }
    
    result = await audio_processor.process_multimodal_content(
        modal_content=modal_content,
        content_type="audio",
        file_path="test.pdf",
    )
    
    description, entity_info, chunk_results = result
    assert description is not None
    assert entity_info is not None
    assert chunk_results is not None

@pytest.mark.asyncio
async def test_error_handling(audio_processor):
    """Test error handling with invalid input"""
    modal_content = {}  # Missing required fields
    
    description, entity_info = await audio_processor.generate_description_only(
        modal_content=modal_content,
        content_type="audio",
    )
    
    # Should return fallback entity
    assert "audio_" in entity_info["entity_name"]
    assert entity_info["entity_type"] == "audio"
```

### Integration Test

```python
@pytest.mark.asyncio
async def test_end_to_end_processing(rag_instance):
    """Test custom processor in complete RAG pipeline"""
    # Add audio content to document
    content_list = [
        {
            "type": "text",
            "text": "Introduction to the interview",
            "page_idx": 0,
        },
        {
            "type": "audio",
            "audio_path": "/path/to/interview.mp3",
            "transcript": "Full interview transcript...",
            "duration": 1800.0,
            "speakers": ["Interviewer", "Expert"],
            "page_idx": 0,
        },
    ]
    
    # Process document
    await rag_instance.insert_content_list(
        content_list=content_list,
        file_path="interview_document.pdf",
    )
    
    # Query should retrieve audio content
    result = await rag_instance.aquery(
        "What did the expert say about the topic?"
    )
    
    assert result is not None
    assert "audio" in result.lower() or "interview" in result.lower()
```

**Sources:** Based on testing patterns for modal processors

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| JSON parsing fails | Malformed LLM response | Use `_robust_json_parse()` inherited method |
| Context not extracted | `content_source` not set | Call `set_content_source()` before processing |
| Entity not stored | Missing required fields | Validate `entity_info` has all required keys |
| Relationships not created | `batch_mode=True` | Ensure merge is called after batch processing |
| Token count incorrect | Wrong tokenizer | Use `self.tokenizer` from BaseModalProcessor |

### Debugging Tips

1. **Enable debug logging:**
```python
import logging
logging.getLogger("raganything").setLevel(logging.DEBUG)
```

2. **Inspect LLM responses:**
```python
logger.debug(f"Raw LLM response: {response}")
```

3. **Verify storage operations:**
```python
# Check if entity was stored
entity_data = await self.knowledge_graph_inst.get_node(entity_name)
logger.debug(f"Stored entity: {entity_data}")
```

4. **Test prompt templates:**
```python
# Print formatted prompt before calling LLM
logger.debug(f"Prompt: {prompt}")
```

**Sources:** [raganything/modalprocessors.py:547-698]() (robust parsing strategies)

---

## Summary

Custom modal processor development follows a structured pattern:

1. **Inherit from `BaseModalProcessor`** to access storage, LLM functions, and context extraction
2. **Implement `generate_description_only()`** for content analysis and entity creation
3. **Implement `process_multimodal_content()`** for complete processing pipeline
4. **Create parsing methods** using `_robust_json_parse()` for error handling
5. **Define prompt templates** with and without context support
6. **Integrate context extraction** using `_get_context_for_item()`
7. **Leverage `_create_entity_and_chunk()`** for automatic storage handling
8. **Test thoroughly** with unit and integration tests

The architecture provides flexibility for handling any content type while maintaining consistency with the RAG-Anything processing pipeline.

**Sources:** [raganything/modalprocessors.py:360-1569](), [raganything/prompt.py:1-354]()

---

# Page: Parser Extension

# Parser Extension

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [raganything/batch_parser.py](raganything/batch_parser.py)
- [raganything/parser.py](raganything/parser.py)
- [tests/test_custom_parser.py](tests/test_custom_parser.py)
- [tests/testparser_kwargs.py](tests/testparser_kwargs.py)

</details>



This guide provides comprehensive documentation for creating custom parser implementations in RAG-Anything. It covers the `Parser` base class interface, the standardized output format specifications, and the plugin registry system for integrating new backends.

For information about using the existing parsers, see [Document Parsers](#4.1). For the broader document processing pipeline, see [Processing Pipeline Internals](#4.2).

---

## Purpose and Scope

RAG-Anything's parser subsystem is designed to be extensible. While the system ships with three parser implementations (`MineruParser`, `DoclingParser`, `PaddleOCRParser`), you can create custom parsers to integrate new document processing backends, specialized OCR engines, or proprietary parsing solutions.

The system utilizes a central registry (`_CUSTOM_PARSERS`) to manage third-party implementations, allowing them to be used via the standard `get_parser` factory without modifying core library code [raganything/parser.py:2238-2240]().

---

## Parser Architecture Overview

The following diagram bridges the **Natural Language Space** (Concepts) to the **Code Entity Space** (Classes and Functions).

### System Component Association
```mermaid
graph TB
    subgraph "Natural Language Space"
        Concept[Custom Parser Implementation]
        RegFlow[Registration Workflow]
        Factory[Parser Factory]
    end

    subgraph "Code Entity Space"
        BaseClass["class Parser<br/>(raganything/parser.py:68)"]
        Registry["_CUSTOM_PARSERS<br/>(raganything/parser.py:2238)"]
        RegFunc["register_parser()<br/>(raganything/parser.py:2243)"]
        GetFunc["get_parser()<br/>(raganything/parser.py:2294)"]
        ListFunc["list_parsers()<br/>(raganything/parser.py:2281)"]
    end

    Concept -. implements .-> BaseClass
    RegFlow -. calls .-> RegFunc
    RegFunc -. populates .-> Registry
    Factory -. calls .-> GetFunc
    GetFunc -. lookups .-> Registry

    style BaseClass fill:#f9f9f9,stroke:#333,stroke-width:2px
    style Registry fill:#f9f9f9,stroke:#333,stroke-width:2px
```
**Sources:** [raganything/parser.py:68-2310](), [raganything/parser.py:2238-2294]()

### Parser Inheritance and Data Flow
```mermaid
graph TB
    subgraph "Parser Abstraction Layer"
        BaseParser["Parser<br/>(Base Class)<br/>raganything/parser.py:68"]
        
        subgraph "Abstract Methods (Must Implement)"
            ParsePDF["parse_pdf()"]
            ParseImage["parse_image()"]
            ParseDoc["parse_document()"]
            CheckInstall["check_installation()"]
        end
        
        subgraph "Helper Methods (Inherited)"
            ConvertOffice["convert_office_to_pdf()"]
            ConvertText["convert_text_to_pdf()"]
            UniqueDir["_unique_output_dir()"]
        end
    end
    
    subgraph "Concrete Implementations"
        MineruImpl["MineruParser<br/>raganything/parser.py:616"]
        DoclingImpl["DoclingParser<br/>raganything/parser.py:1362"]
        PaddleImpl["PaddleOCRParser<br/>raganything/parser.py:1856"]
        CustomImpl["CustomParser<br/>(User Implementation)"]
    end
    
    subgraph "Factory & Registration"
        GetParser["get_parser()"]
        Register["register_parser()"]
    end
    
    BaseParser --> ParsePDF
    BaseParser --> ParseImage
    BaseParser --> ParseDoc
    BaseParser --> CheckInstall
    
    BaseParser -.inherits.-> MineruImpl
    BaseParser -.inherits.-> DoclingImpl
    BaseParser -.inherits.-> PaddleImpl
    BaseParser -.inherits.-> CustomImpl
    
    Register --> CustomImpl
    GetParser --> CustomImpl
    
    style BaseParser fill:#f9f9f9,stroke:#333,stroke-width:3px
    style CustomImpl fill:#fff,stroke:#333,stroke-width:2px
```
**Sources:** [raganything/parser.py:68-1856](), [raganything/parser.py:2243-2294]()

---

## Base Parser Class Interface

The `Parser` base class defines the contract for all implementations. It provides common functionality and requires subclasses to implement four primary methods.

### Required Abstract Methods

| Method | Purpose | Return Type |
|--------|---------|-------------|
| `parse_pdf()` | Parse PDF documents | `List[Dict[str, Any]]` |
| `parse_image()` | Parse image files | `List[Dict[str, Any]]` |
| `parse_document()` | Main routing method for any supported file | `List[Dict[str, Any]]` |
| `check_installation()` | Verify parser dependencies are available | `bool` |

### Class Attributes
The `Parser` class defines file format constants used for routing:
- `OFFICE_FORMATS`: `{".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx"}` [raganything/parser.py:76]()
- `IMAGE_FORMATS`: `{".png", ".jpeg", ".jpg", ".bmp", ".tiff", ".tif", ".gif", ".webp"}` [raganything/parser.py:77]()
- `TEXT_FORMATS`: `{".txt", ".md"}` [raganything/parser.py:78]()

**Sources:** [raganything/parser.py:68-82]()

---

## Standardized Output Format

All parsers must return a `List[Dict[str, Any]]`. The system recognizes four content types:

### 1. Text Block
```python
{
    "type": "text",
    "text": "Extracted text content...",
    "page_idx": 0
}
```
**Sources:** [raganything/parser.py:1647-1661]()

### 2. Image Block
```python
{
    "type": "image",
    "img_path": "/abs/path/to/image.png", # Must be absolute
    "image_caption": ["Caption text"], 
    "image_footnote": ["Footnote text"],
    "page_idx": 0
}
```
*Note: For backward compatibility, include `img_caption` and `img_footnote` as aliases.* [raganything/parser.py:935-948]()

### 3. Table Block
```python
{
    "type": "table",
    "table_body": "| Col1 | Col2 |\n|---|---|", # Markdown or List
    "table_caption": ["Table Title"],
    "page_idx": 0
}
```
**Sources:** [raganything/parser.py:1686-1702]()

### 4. Equation Block
```python
{
    "type": "equation",
    "latex": "E=mc^2",
    "text": "Energy equals mass times c squared",
    "text_format": "latex", # "latex", "mathml", or "unknown"
    "page_idx": 0
}
```
**Sources:** [raganything/parser.py:1647-1655]()

---

## The Parser Registry System

RAG-Anything uses an **in-process registry** for custom parsers. This is primarily intended for Python usage where the application imports a parser and registers it before calling RAG-Anything APIs [raganything/parser.py:9-13]().

### Key Functions

| Function | Description |
|----------|-------------|
| `register_parser(name, parser_cls)` | Registers a new parser class under a unique name. Rejects built-in names like `mineru`. [raganything/parser.py:2243]() |
| `unregister_parser(name)` | Removes a custom parser from the registry. [raganything/parser.py:2268]() |
| `list_parsers()` | Returns a dictionary of all available (built-in + custom) parsers. [raganything/parser.py:2281]() |
| `get_parser(parser_type)` | Factory function that retrieves an instance of the requested parser. [raganything/parser.py:2294]() |

### Implementation Example

```python
from raganything.parser import Parser, register_parser

class MySpecialParser(Parser):
    def check_installation(self) -> bool:
        return True
    
    def parse_document(self, file_path, output_dir="./output", **kwargs):
        return [{"type": "text", "text": "Parsed by MySpecialParser", "page_idx": 0}]
    
    def parse_pdf(self, pdf_path, **kwargs):
        return self.parse_document(pdf_path, **kwargs)

# Registering the parser
register_parser("special", MySpecialParser)

# Usage via factory
from raganything.parser import get_parser
parser = get_parser("special")
```
**Sources:** [tests/test_custom_parser.py:17-30](), [raganything/parser.py:2243-2266]()

---

## Helper Utilities

The `Parser` base class provides inherited methods to simplify implementation:

- **`_unique_output_dir(base_dir, file_path)`**: Generates a collision-resistant directory by hashing the absolute file path. [raganything/parser.py:172-191]()
- **`convert_office_to_pdf(doc_path, output_dir)`**: Uses LibreOffice to convert `.docx`, `.pptx`, etc., to PDF. [raganything/parser.py:194-332]()
- **`convert_text_to_pdf(text_path, output_dir)`**: Converts `.txt` or `.md` to PDF using ReportLab with full markdown support. [raganything/parser.py:334-569]()
- **`_is_url(path)`**: Utility to check if a string is a valid URL. [raganything/parser.py:83-90]()
- **`_download_file(url)`**: Downloads a remote file to a temporary local path for processing. [raganything/parser.py:92-166]()

**Sources:** [raganything/parser.py:172-569]()

---

## Best Practices

1.  **Case Insensitivity**: The registry handles names case-insensitively and strips whitespace [raganything/parser.py:2253-2254]().
2.  **Subclass Validation**: `register_parser` strictly enforces that the provided class is a subclass of `Parser` [raganything/parser.py:2256-2257]().
3.  **Absolute Paths**: Always ensure `img_path` in returned content blocks is an absolute path to prevent processing failures in downstream modal processors [raganything/parser.py:935-948]().
4.  **CLI Discovery**: The standalone CLI (`python -m raganything.parser`) does **not** perform automatic plugin discovery. Custom parsers must be registered in the current process (e.g., via `sitecustomize` or a wrapper script) [raganything/parser.py:14-17]().

**Sources:** [raganything/parser.py:9-17](), [raganything/parser.py:2253-2260]()

---

# Page: Resilience and Error Handling

# Resilience and Error Handling

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [raganything/__init__.py](raganything/__init__.py)
- [raganything/resilience.py](raganything/resilience.py)
- [tests/test_resilience.py](tests/test_resilience.py)

</details>



The RAG-Anything framework incorporates a dedicated resilience layer to handle the inherent instability of distributed systems, specifically focusing on LLM API calls, embedding requests, and network-dependent document parsing [raganything/resilience.py:1-9](). This subsystem prevents the processing pipeline from stalling due to transient failures like rate limits or intermittent network drops [raganything/resilience.py:7-9]().

## Resilience Mechanisms

The system implements three primary patterns for fault tolerance:
1.  **Retry Decorators**: Automatic re-execution of failed operations with backoff logic.
2.  **Circuit Breaker**: Preventing system overload by "tripping" when a service is consistently failing.
3.  **Exponential Backoff with Jitter**: Spreading out retry attempts to avoid "thundering herd" problems [raganything/resilience.py:70-71]().

### Resilience Component Mapping
The following diagram maps the logical resilience concepts to their implementation entities in the codebase.

**Resilience Logic to Code Entity Mapping**
```mermaid
graph TD
    subgraph "Natural Language Space"
        A["Retry Logic"]
        B["Fault Tolerance"]
        C["Service Protection"]
    end

    subgraph "Code Entity Space"
        A --> D["@retry (sync)"]
        A --> E["@async_retry (async)"]
        B --> F["_DEFAULT_RETRYABLE"]
        C --> G["CircuitBreaker Class"]
    end

    D["raganything.resilience.retry"]
    E["raganything.resilience.async_retry"]
    F["raganything.resilience._DEFAULT_RETRYABLE"]
    G["raganything.resilience.CircuitBreaker"]
```
Sources: [raganything/resilience.py:59-67](), [raganything/resilience.py:146-154](), [raganything/resilience.py:29-32](), [raganything/resilience.py:216-220]()

## Retry Logic and Backoff

RAG-Anything provides two primary decorators: `retry` for synchronous functions and `async_retry` for asynchronous operations [raganything/resilience.py:59-177](). Both use a configurable exponential backoff strategy.

### Configuration Parameters
The decorators accept several parameters to tune behavior:
*   `max_attempts`: Total attempts including the initial call (default: 3) [raganything/resilience.py:60]().
*   `base_delay`: Initial sleep time in seconds (default: 1.0) [raganything/resilience.py:61]().
*   `max_delay`: Upper bound for delay (default: 60.0) [raganything/resilience.py:62]().
*   `exponential_base`: Multiplier for the delay after each failure (default: 2.0) [raganything/resilience.py:63]().
*   `jitter`: Adds 0-50% random noise to the delay to prevent synchronized retries [raganything/resilience.py:124-127]().

### Retryable Exception Types
The system defines a default set of exceptions (`_DEFAULT_RETRYABLE`) that are considered transient and safe to retry [raganything/resilience.py:29-56]():

| Category | Exception Types |
| :--- | :--- |
| **Standard Python** | `ConnectionError`, `TimeoutError` |
| **HTTPX** | `ConnectError`, `ReadTimeout`, `WriteTimeout`, `PoolTimeout` |
| **OpenAI API** | `APIConnectionError`, `APITimeoutError`, `RateLimitError`, `InternalServerError` |

Local programming errors (e.g., `TypeError`, `ValueError`) and filesystem errors (e.g., `FileNotFoundError`) are explicitly excluded from default retries to prevent infinite loops on non-recoverable errors [raganything/resilience.py:26-28]().

Sources: [raganything/resilience.py:29-56](), [raganything/resilience.py:59-92](), [tests/test_resilience.py:198-213]()

## Circuit Breaker Pattern

The `CircuitBreaker` class protects downstream services (like a local LLM server or a vector database) from being overwhelmed when they are struggling [raganything/resilience.py:216-220]().

### State Machine Flow
The circuit breaker operates in three states:
1.  **CLOSED**: Normal operation. Requests pass through. Failures are tracked [tests/test_resilience.py:217-225]().
2.  **OPEN**: Threshold reached. All calls fail immediately with `CircuitBreakerOpen` without attempting the underlying function [tests/test_resilience.py:227-241]().
3.  **HALF-OPEN**: After a `reset_timeout`, the system allows a single "proportional" call to test if the service has recovered [tests/test_resilience.py:243-255]().

**Circuit Breaker Lifecycle**
```mermaid
stateDiagram-v2
    [*] --> CLOSED
    CLOSED --> OPEN : "failure_count >= failure_threshold"
    OPEN --> HALF_OPEN : "time > reset_timeout"
    HALF_OPEN --> CLOSED : "Success"
    HALF_OPEN --> OPEN : "Failure"
```
Sources: [raganything/resilience.py:216-260](), [tests/test_resilience.py:216-255]()

## Implementation Example: Wrapping LLM Calls

The following diagram illustrates how the resilience layer wraps an LLM call to provide fault tolerance during document processing.

**LLM Call Fault Tolerance Flow**
```mermaid
sequenceDiagram
    participant P as ProcessorMixin
    participant R as async_retry
    participant LLM as LLM Provider (OpenAI/Ollama)

    P->>R: "Call generate_description_only()"
    activate R
    R->>LLM: "Request (Attempt 1)"
    LLM-->>R: "RateLimitError"
    Note over R: "Calculate delay: base_delay * 2^0 + jitter"
    R->>R: "asyncio.sleep(delay)"
    R->>LLM: "Request (Attempt 2)"
    LLM-->>R: "Success"
    R-->>P: "Return result"
    deactivate R
```

### Usage in Code
Developers can apply these protections by decorating sensitive functions:

```python
# Example of wrapping a sync call
@retry(max_attempts=5, retryable_exceptions=[ConnectionError])
def fetch_data():
    ...

# Example of wrapping an async LLM call
@async_retry(max_attempts=3, on_retry=my_callback)
async def call_vision_model(image_data):
    ...
```

Sources: [raganything/resilience.py:89-91](), [raganything/resilience.py:173-176](), [tests/test_resilience.py:100-106]()

---

# Page: Callbacks and Observability

# Callbacks and Observability

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [raganything/__init__.py](raganything/__init__.py)
- [raganything/callbacks.py](raganything/callbacks.py)
- [tests/test_callbacks.py](tests/test_callbacks.py)

</details>



The RAG-Anything system includes a comprehensive callback and event system designed for monitoring, logging, and metrics collection across the document processing lifecycle. This system provides a lightweight publish-subscribe mechanism that hooks into every major stage, from initial parsing to final query execution.

### Overview of the Callback System

The observability framework is built around three primary components:
1.  **`ProcessingEvent`**: An immutable data structure representing a specific occurrence in the pipeline.
2.  **`ProcessingCallback`**: An abstract base class that defines hook methods for various lifecycle events.
3.  **`CallbackManager`**: A registry and dispatcher that manages multiple callbacks and ensures event delivery.

Sources: [raganything/callbacks.py:4-21](), [raganything/callbacks.py:35-46]()

---

### Data Structures and Core Classes

#### ProcessingEvent
The `ProcessingEvent` captures the state of the system at a specific point in time. It includes fields for the event type, timestamp, document identifiers, and performance metrics like `duration_seconds`.

| Field | Type | Description |
| :--- | :--- | :--- |
| `event_type` | `str` | The name of the hook (e.g., `on_parse_start`). |
| `timestamp` | `float` | Epoch time when the event was created. |
| `file_path` | `Optional[str]` | Path to the document being processed. |
| `stage` | `Optional[str]` | The pipeline stage (parsing, insertion, etc.). |
| `duration_seconds` | `Optional[float]` | Time taken for the stage to complete. |
| `error` | `Optional[str]` | Error message if the stage failed. |

Sources: [raganything/callbacks.py:35-58]()

#### CallbackManager
The `CallbackManager` acts as the central hub for observability. It maintains a list of registered callbacks and dispatches events to them. It includes a thread-safe mechanism for event logging that can be enabled for debugging.

*   **`register(callback)`**: Adds a `ProcessingCallback` instance to the manager [raganything/callbacks.py:257-263]().
*   **`dispatch(event_type, **kwargs)`**: Triggers the corresponding method on all registered callbacks. It automatically handles errors within callbacks to prevent them from crashing the main processing pipeline [raganything/callbacks.py:276-312]().
*   **`enable_event_log(enabled)`**: When enabled, the manager stores a history of `ProcessingEvent` objects in an internal list [raganything/callbacks.py:314-316]().

Sources: [raganything/callbacks.py:238-316]()

---

### The Processing Lifecycle Hooks

The `ProcessingCallback` class provides a set of `on_*` methods that can be overridden. By default, these methods are empty and silently ignored if not implemented.

#### Lifecycle Diagram: Code Entity Flow
This diagram maps the natural language processing stages to the specific hook methods defined in `raganything/callbacks.py`.

Title: Document Processing Callback Lifecycle
```mermaid
graph TD
    subgraph "Natural Language Space"
        Start["Start Processing"]
        Parse["Parsing Document"]
        Insert["Inserting Text"]
        Multi["Multimodal Processing"]
        Query["Querying Index"]
        End["Finish"]
    end

    subgraph "Code Entity Space: ProcessingCallback"
        on_batch_start["on_batch_start()"]
        on_parse_start["on_parse_start()"]
        on_parse_complete["on_parse_complete()"]
        on_text_insert_start["on_text_insert_start()"]
        on_text_insert_complete["on_text_insert_complete()"]
        on_multimodal_start["on_multimodal_start()"]
        on_multimodal_item["on_multimodal_item_complete()"]
        on_multimodal_complete["on_multimodal_complete()"]
        on_document_complete["on_document_complete()"]
        on_query_start["on_query_start()"]
        on_query_complete["on_query_complete()"]
    end

    Start --> on_batch_start
    on_batch_start --> on_parse_start
    on_parse_start --> on_parse_complete
    on_parse_complete --> on_text_insert_start
    on_text_insert_start --> on_text_insert_complete
    on_text_insert_complete --> on_multimodal_start
    on_multimodal_start --> on_multimodal_item
    on_multimodal_item --> on_multimodal_complete
    on_multimodal_complete --> on_document_complete
    Query --> on_query_start
    on_query_start --> on_query_complete
    on_document_complete --> End
```
Sources: [raganything/callbacks.py:61-181](), [tests/test_callbacks.py:12-61]()

---

### Built-in Metrics Collection

RAG-Anything provides a `MetricsCallback` that aggregates data across multiple documents and queries. This is useful for generating performance reports or monitoring system health.

#### Tracked Metrics
The `MetricsCallback` maintains a `metrics` dictionary containing:
*   **Document Stats**: `documents_processed`, `documents_failed` [raganything/callbacks.py:198-199]().
*   **Content Stats**: `total_content_blocks`, `total_multimodal_items` [raganything/callbacks.py:200-201]().
*   **Latency Stats**: `total_parse_time`, `total_insert_time`, `total_multimodal_time`, `total_query_time` [raganything/callbacks.py:202-206]().
*   **Error Tracking**: A list of error descriptions and stages [raganything/callbacks.py:207]().

#### Summary Generation
The `summary()` method provides a human-readable string of the collected metrics, including averages (e.g., average parse time per document) [raganything/callbacks.py:231-235]().

Sources: [raganything/callbacks.py:183-235](), [tests/test_callbacks.py:148-181]()

---

### Integration with RAGAnything

The `CallbackManager` is initialized within the `RAGAnything` class. Users can register their own callbacks via the `callback_manager` attribute.

#### Implementation Diagram: Dispatcher Logic
This diagram shows how the `CallbackManager` mediates between the `ProcessorMixin` (which triggers events) and the `ProcessingCallback` implementations.

Title: Callback Dispatcher Interaction
```mermaid
sequenceDiagram
    participant P as ProcessorMixin
    participant CM as CallbackManager
    participant CB as ProcessingCallback (e.g. MetricsCallback)

    P->>CM: dispatch("on_parse_start", file_path="doc.pdf")
    CM->>CM: Create ProcessingEvent
    CM->>CB: on_parse_start(file_path="doc.pdf")
    Note over CB: Update metrics / Log event
    
    P->>P: _parse_document()
    
    P->>CM: dispatch("on_parse_complete", duration_seconds=1.2)
    CM->>CB: on_parse_complete(duration_seconds=1.2)
```
Sources: [raganything/callbacks.py:276-312](), [raganything/__init__.py:34-40](), [tests/test_callbacks.py:184-195]()

### Error Handling in Callbacks
To ensure that observability does not impact system reliability, the `CallbackManager` wraps every call to a callback method in a `try-except` block. If a callback raises an exception, it is caught, logged, and processing continues uninterrupted [raganything/callbacks.py:302-307]().

Sources: [raganything/callbacks.py:302-312](), [tests/test_callbacks.py:95-103]()

---

# Page: Prompt Management and Localization

# Prompt Management and Localization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [raganything/__init__.py](raganything/__init__.py)
- [raganything/prompt.py](raganything/prompt.py)
- [raganything/prompt_manager.py](raganything/prompt_manager.py)
- [raganything/prompts_zh.py](raganything/prompts_zh.py)
- [tests/test_prompt_language.py](tests/test_prompt_language.py)

</details>



RAG-Anything provides a robust localization framework for managing LLM and VLM prompt templates. This system allows the engine to adapt its multimodal analysis—covering images, tables, and equations—to different target languages at runtime. The architecture supports built-in Chinese templates, atomic language switching, and a registry for custom language extensions.

### Overview of Prompt Management

The prompt management system is centered around the `prompt_manager` module, which controls the global state of prompt templates used across all modal processors [raganything/prompt_manager.py:1-16](). It ensures that even when the language is switched, the system remains thread-safe and provides fallback mechanisms to English for any missing translations [raganything/prompt_manager.py:84-90]().

The following diagram illustrates the relationship between the localization functions and the underlying data structures.

**Prompt Management Architecture**
```mermaid
graph TD
    subgraph "Natural Language Space"
        User["User/Developer"] -- "set_prompt_language('zh')" --> SetLang["set_prompt_language"]
        User -- "register_prompt_language('fr', dict)" --> RegLang["register_prompt_language"]
    end

    subgraph "Code Entity Space"
        SetLang --> PM["prompt_manager.py"]
        RegLang --> PM
        PM -- "atomically updates" --> PR["PromptRegistry (PROMPTS)"]
        
        subgraph "Storage"
            EL["_ENGLISH_PROMPTS"]
            PL["_PROMPT_LANGUAGES"]
            ZH["prompts_zh.py"]
        end

        PM -- "fallback/diff" --> EL
        PM -- "lazy load" --> ZH
        PM -- "store/retrieve" --> PL
    end

    PR -- "used by" --> ModalProcessors["Modal Processors (Image, Table, etc.)"]
```
Sources: [raganything/prompt_manager.py:24-40](), [raganything/prompt.py:65-82](), [raganything/prompts_zh.py:1-14]()

---

### Key Components and Classes

#### PromptRegistry
The `PromptRegistry` class serves as a stable container for prompt templates. It implements a "snapshot swapping" pattern where readers (modal processors) maintain a reference to the registry object, but the underlying data can be replaced in a single atomic step using the `swap` method [raganything/prompt.py:13-25]().

| Method | Description |
| :--- | :--- |
| `swap(prompts)` | Atomically replaces the active prompt dictionary with a new set [raganything/prompt.py:23-25](). |
| `snapshot()` | Returns a copy of the currently active prompt set [raganything/prompt.py:27-29](). |
| `__getitem__(key)` | Standard dictionary-like access to specific templates [raganything/prompt.py:31-32](). |

Sources: [raganything/prompt.py:13-62]()

#### Prompt Manager Functions
The `prompt_manager` module provides the public API for controlling localization.

*   **`set_prompt_language(language: str)`**: Switches the active templates. It performs a "lazy load" for built-in languages like Chinese (`zh`) if they haven't been initialized yet [raganything/prompt_manager.py:84-114]().
*   **`register_prompt_language(language_code: str, prompts: dict)`**: Allows developers to add support for new languages by providing a dictionary of templates [raganything/prompt_manager.py:64-82]().
*   **`reset_prompts()`**: Reverts all templates back to the original English defaults [raganything/prompt_manager.py:139-146]().
*   **`get_prompt_language()`**: Returns the ISO 639-1 code of the current language [raganything/prompt_manager.py:134-136]().

Sources: [raganything/prompt_manager.py:64-156]()

---

### Data Flow for Language Switching

When `set_prompt_language` is called, the system follows a specific resolution logic to ensure stability and completeness:

1.  **Normalization**: The language code is stripped and lower-cased [raganything/prompt_manager.py:100]().
2.  **Loading**: If the language is `zh`, it imports `PROMPTS_ZH` from `raganything.prompts_zh` [raganything/prompt_manager.py:57-60]().
3.  **Resolution**: A new dictionary is constructed. For every key in the default English set, the system checks if a translation exists in the target language. If not, it falls back to the English version [raganything/prompt_manager.py:120-125]().
4.  **Atomic Swap**: The `_PROMPTS_LOCK` (a `threading.RLock`) is acquired, and `PROMPTS.swap()` is called to update the global registry without interrupting concurrent readers [raganything/prompt_manager.py:127-129]().

**Language Switch Sequence**
```mermaid
sequenceDiagram
    participant App as "Application Code"
    participant PM as "prompt_manager.py"
    participant ZH as "prompts_zh.py"
    participant PR as "PROMPTS (PromptRegistry)"

    App->>PM: set_prompt_language("zh")
    PM->>PM: _normalize_language_code()
    PM->>ZH: _lazy_load_language()
    ZH-->>PM: return PROMPTS_ZH
    PM->>PM: Resolve keys (ZH + EN Fallback)
    PM->>PR: swap(resolved_dict)
    Note over PR: Atomic update under _PROMPTS_LOCK
    PM-->>App: Success
```
Sources: [raganything/prompt_manager.py:43-61](), [raganything/prompt_manager.py:115-131](), [raganything/prompt.py:23-25]()

---

### Chinese Prompt Templates (`prompts_zh.py`)

The system includes a full suite of Chinese templates to support native-language multimodal RAG. These templates cover:

*   **System Prompts**: Specialized personas for image, table, and equation analysis (e.g., `IMAGE_ANALYSIS_SYSTEM` defined as "你是一位专业的图像分析专家") [raganything/prompts_zh.py:17-27]().
*   **Analysis Prompts**: Detailed instructions for VLMs to extract structured JSON from visual elements, including `vision_prompt`, `table_prompt`, and `equation_prompt` [raganything/prompts_zh.py:30-218]().
*   **Chunk Templates**: Formatting templates used to create text chunks for the vector database (e.g., `image_chunk`, `table_chunk`) [raganything/prompts_zh.py:271-298]().
*   **Query Prompts**: Instructions for the query system to describe images or tables provided in a multimodal query [raganything/prompts_zh.py:301-318]().

Sources: [raganything/prompts_zh.py:1-318]()

---

### Implementation Details and Usage

#### Adding a New Language
To add a custom language (e.g., French), use the `register_prompt_language` function. You only need to provide the keys you wish to override; others will remain in English.

```python
from raganything.prompt_manager import register_prompt_language, set_prompt_language

french_prompts = {
    "IMAGE_ANALYSIS_SYSTEM": "Vous êtes un expert en analyse d'images."
}
register_prompt_language("fr", french_prompts)
set_prompt_language("fr")
```
Sources: [raganything/prompt_manager.py:64-82](), [tests/test_prompt_language.py:70-74]()

#### Verification and Thread Safety
The system uses a `threading.RLock` to ensure that even if multiple threads attempt to switch languages or read prompts simultaneously, the `PROMPTS` registry never enters an inconsistent state [raganything/prompt_manager.py:40](), [raganything/prompt_manager.py:127-129]().

Testing utilities confirm that:
1.  Switching to a language and back to English restores original values [tests/test_prompt_language.py:32-39]().
2.  Unknown languages raise a `ValueError` [tests/test_prompt_language.py:41-43]().
3.  The Chinese template set is verified to contain all keys present in the English set [tests/test_prompt_language.py:49-56]().

Sources: [raganything/prompt_manager.py:108-113](), [tests/test_prompt_language.py:24-67]()

---

# Page: Troubleshooting

# Troubleshooting

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/multimodal_rag_failure_modes.md](docs/multimodal_rag_failure_modes.md)
- [raganything/asset_urls.py](raganything/asset_urls.py)
- [raganything/parser.py](raganything/parser.py)
- [tests/test_asset_urls.py](tests/test_asset_urls.py)
- [tests/testparser_kwargs.py](tests/testparser_kwargs.py)

</details>



This page provides an overview of common issues encountered when using RAG-Anything and guidance for diagnosing and resolving them. The troubleshooting process is organized into three main categories: parser installation issues, document processing errors, and query/storage problems.

For detailed troubleshooting of specific issues, see:
- **Parser Installation Issues**: See [Parser Installation Issues](#12.1)
- **Processing Errors**: See [Processing Errors](#12.2)
- **Query and Storage Issues**: See [Query and Storage Issues](#12.3)

For initial setup guidance, see [Installation](#2.1) and [Environment Configuration](#2.3).

---

## Error Propagation Architecture

Understanding where errors originate in the system helps diagnose problems efficiently. The following diagram shows the major error sources and their propagation paths through the RAG-Anything pipeline.

```mermaid
graph TD
    subgraph "User Input Layer"
        DOC_INPUT["file_path parameter"]
        CONFIG_INPUT["RAGAnythingConfig object"]
        ENV_INPUT[".env file variables"]
    end
    
    subgraph "Validation Layer - parser.py"
        FILE_CHECK["Path.exists() check"]
        EXT_CHECK["Extension validation<br/>OFFICE_FORMATS / IMAGE_FORMATS / TEXT_FORMATS"]
        CONFIG_CHECK["config.parser validation<br/>get_parser()"]
    end
    
    subgraph "Parser Layer - parser.py"
        GET_PARSER["get_parser(parser_type)<br/>line 2165"]
        MINERU_PARSER["MineruParser()<br/>line 597"]
        DOCLING_PARSER["DoclingParser()<br/>line 1343"]
        PADDLEOCR_PARSER["PaddleOCRParser()<br/>line 1837"]
        
        FORMAT_CONVERT["Format conversion methods"]
        CONVERT_OFFICE["convert_office_to_pdf()<br/>line 194"]
        CONVERT_TEXT["convert_text_to_pdf()<br/>line 334"]
        CONVERT_IMAGE["PIL Image.open() + convert<br/>line 1109"]
    end
    
    subgraph "External Dependencies"
        MINERU_CMD["mineru CLI subprocess<br/>subprocess.Popen()"]
        DOCLING_API["Docling Python API<br/>DocumentConverter"]
        LIBREOFFICE["soffice / libreoffice<br/>subprocess.run()"]
        PIL_LIB["from PIL import Image<br/>Image.open()"]
        REPORTLAB["from reportlab.platypus<br/>SimpleDocTemplate"]
        PADDLEOCR_LIB["from paddleocr import PaddleOCR"]
        PYPDFIUM["import pypdfium2 as pdfium"]
    end
    
    subgraph "Error Types"
        FILE_ERR["FileNotFoundError"]
        VALUE_ERR["ValueError"]
        RUNTIME_ERR["RuntimeError"]
        MINERU_ERR["MineruExecutionError<br/>line 57"]
        IMPORT_ERR["ImportError"]
    end
    
    DOC_INPUT --> FILE_CHECK
    CONFIG_INPUT --> CONFIG_CHECK
    
    FILE_CHECK -->|"not exists"| FILE_ERR
    FILE_CHECK -->|"exists"| EXT_CHECK
    
    EXT_CHECK -->|"valid"| GET_PARSER
    EXT_CHECK -->|"invalid"| VALUE_ERR
    
    CONFIG_CHECK -->|"invalid"| VALUE_ERR
    CONFIG_CHECK -->|"valid"| GET_PARSER
    
    GET_PARSER --> MINERU_PARSER
    GET_PARSER --> DOCLING_PARSER
    GET_PARSER --> PADDLEOCR_PARSER
    
    MINERU_PARSER --> FORMAT_CONVERT
    DOCLING_PARSER --> FORMAT_CONVERT
    PADDLEOCR_PARSER --> FORMAT_CONVERT
    
    FORMAT_CONVERT --> CONVERT_OFFICE
    FORMAT_CONVERT --> CONVERT_TEXT
    FORMAT_CONVERT --> CONVERT_IMAGE
    
    CONVERT_OFFICE --> LIBREOFFICE
    CONVERT_TEXT --> REPORTLAB
    CONVERT_IMAGE --> PIL_LIB
    
    MINERU_PARSER --> MINERU_CMD
    DOCLING_PARSER --> DOCLING_API
    PADDLEOCR_PARSER --> PADDLEOCR_LIB
    PADDLEOCR_PARSER --> PYPDFIUM
    
    LIBREOFFICE -->|"command not found"| RUNTIME_ERR
    REPORTLAB -->|"not installed"| IMPORT_ERR
    PIL_LIB -->|"not installed"| RUNTIME_ERR
    PADDLEOCR_LIB -->|"not installed"| IMPORT_ERR
    PYPDFIUM -->|"not installed"| IMPORT_ERR
    
    MINERU_CMD -->|"exit code != 0"| MINERU_ERR
```

**Sources:** [raganything/parser.py:57-66](), [raganything/parser.py:194-228](), [raganything/parser.py:334-568](), [raganything/parser.py:597-615](), [raganything/parser.py:1343-1356](), [raganything/parser.py:1837-1847](), [raganything/parser.py:2165-2176]()

---

## Common Error Categories

The system encounters errors in three primary areas, each with distinct diagnostic approaches.

| Error Category | Typical Symptoms | Primary Source Code | Detailed Guide |
|---------------|------------------|---------------------|----------------|
| **Parser Installation** | `FileNotFoundError` for `mineru`, subprocess failures, Docling API missing | `get_parser()` [raganything/parser.py:2165-2176](), `check_installation()` [raganything/parser.py:1309-1340, 1803-1834]() | [Parser Installation Issues](#12.1) |
| **Format Dependencies** | `ImportError` for PIL/Pillow/ReportLab/PaddleOCR, LibreOffice conversion failures | `convert_office_to_pdf()` [raganything/parser.py:194-331](), `convert_text_to_pdf()` [raganything/parser.py:334-568]() | [Parser Installation Issues](#12.1) |
| **Processing Errors** | `MineruExecutionError` [raganything/parser.py:57-66](), empty `content_list`, invalid JSON output | `_run_mineru_command()` [raganything/parser.py:617-845](), `_read_output_files()` [raganything/parser.py:847-962]() | [Processing Errors](#12.2) |
| **Multimodal Failure** | OCR corruption, table structure loss, image-caption misalignment | `docs/multimodal_rag_failure_modes.md` [docs/multimodal_rag_failure_modes.md:1-85]() | [Processing Errors](#12.2) |
| **Asset URL Issues** | Images not loading in UI, path mismatch | `attach_public_media_urls()` [raganything/asset_urls.py:65-118]() | [Query and Storage Issues](#12.3) |
| **Storage Errors** | Connection timeouts, database initialization failures | LightRAG storage backends | [Query and Storage Issues](#12.3) |

**Sources:** [raganything/parser.py:57-66](), [raganything/parser.py:617-845](), [raganything/asset_urls.py:65-118](), [docs/multimodal_rag_failure_modes.md:9-72]()

---

## Diagnostic Workflow

Use this decision tree to quickly identify the appropriate troubleshooting section for your issue.

```mermaid
graph TD
    START["Encountering Error"]
    
    PHASE{"Which phase<br/>is failing?"}
    
    INSTALL_CHECK["Installation/<br/>Setup Phase"]
    PROCESS_CHECK["Document<br/>Processing Phase"]
    QUERY_CHECK["Query/<br/>Retrieval Phase"]
    
    INSTALL_TYPE{"Error type?"}
    PROCESS_TYPE{"Error type?"}
    QUERY_TYPE{"Error type?"}
    
    CMD_NOT_FOUND["Command not found:<br/>mineru/soffice"]
    DEP_MISSING["Missing dependency:<br/>PIL/ReportLab/Docling"]
    
    PARSE_FAIL["Parser execution<br/>failed"]
    CONVERT_FAIL["Format conversion<br/>failed"]
    OCR_CORRUPT["OCR/Layout<br/>corruption"]
    
    EMPTY_RESULT["Empty query<br/>results"]
    IMG_NOT_LOAD["Images not loading<br/>in UI"]
    
    GOTO_121["See 12.1:<br/>Parser Installation"]
    GOTO_122["See 12.2:<br/>Processing Errors"]
    GOTO_123["See 12.3:<br/>Query/Storage Issues"]
    
    START --> PHASE
    
    PHASE -->|Setup| INSTALL_CHECK
    PHASE -->|Processing| PROCESS_CHECK
    PHASE -->|Querying| QUERY_CHECK
    
    INSTALL_CHECK --> INSTALL_TYPE
    PROCESS_CHECK --> PROCESS_TYPE
    QUERY_CHECK --> QUERY_TYPE
    
    INSTALL_TYPE --> CMD_NOT_FOUND
    INSTALL_TYPE --> DEP_MISSING
    
    PROCESS_TYPE --> PARSE_FAIL
    PROCESS_TYPE --> CONVERT_FAIL
    PROCESS_TYPE --> OCR_CORRUPT
    
    QUERY_TYPE --> EMPTY_RESULT
    QUERY_TYPE --> IMG_NOT_LOAD
    
    CMD_NOT_FOUND --> GOTO_121
    DEP_MISSING --> GOTO_121
    
    PARSE_FAIL --> GOTO_122
    CONVERT_FAIL --> GOTO_122
    OCR_CORRUPT --> GOTO_122
    
    EMPTY_RESULT --> GOTO_123
    IMG_NOT_LOAD --> GOTO_123
```

**Sources:** [docs/multimodal_rag_failure_modes.md:1-85](), [raganything/parser.py:617-845]()

---

## Quick Diagnostic Commands

### Check Parser Installation

```python
from raganything.parser import get_parser

# Check MinerU installation
mineru_parser = get_parser("mineru")
if mineru_parser.check_installation():
    print("✅ MinerU installed properly")

# Check Docling installation (Python API check)
docling_parser = get_parser("docling")
if docling_parser.check_installation():
    print("✅ Docling installed properly")
```

The `check_installation()` method verifies parser availability:
- `MineruParser.check_installation()` [raganything/parser.py:1309-1340]() runs `mineru --version`.
- `DoclingParser.check_installation()` [raganything/parser.py:1803-1834]() checks for the `docling` package.

**Sources:** [raganything/parser.py:1309-1340](), [raganything/parser.py:1803-1834]()

### Verify Public Asset Mapping

If images are missing in your UI, verify the environment variables for asset URL mapping:

```python
import os
base = os.environ.get("RAGANYTHING_PUBLIC_ASSET_BASE_URL")
strip = os.environ.get("RAGANYTHING_PUBLIC_ASSET_STRIP_PREFIX")
print(f"Base URL: {base}, Strip Prefix: {strip}")
```

If only one is set, the system logs a warning and skips attachment [raganything/asset_urls.py:83-100]().

**Sources:** [raganything/asset_urls.py:77-100]()

---

## Subprocess Execution Monitoring (MinerU)

MinerU runs as a subprocess with real-time logging. Errors are captured via `stdout_queue` and `stderr_queue` [raganything/parser.py:745-746]().

```mermaid
graph LR
    subgraph "Main Thread"
        MAIN["_run_mineru_command()<br/>line 617"]
        POPEN["subprocess.Popen(cmd)<br/>line 742"]
        RETURN_CHECK["if return_code != 0<br/>line 824"]
    end
    
    subgraph "Worker Threads"
        THREAD_OUT["stdout_thread<br/>line 749"]
        THREAD_ERR["stderr_thread<br/>line 752"]
    end
    
    subgraph "Logging Output"
        LOG_INFO["logger.info('[MinerU] ...')<br/>line 769"]
        LOG_WARN["logger.warning('[MinerU] ...')<br/>line 779"]
        LOG_ERROR["logger.error('[MinerU] ...')<br/>line 781"]
    end
    
    MAIN --> POPEN
    POPEN --> THREAD_OUT
    POPEN --> THREAD_ERR
    THREAD_OUT --> LOG_INFO
    THREAD_ERR --> LOG_WARN
    THREAD_ERR --> LOG_ERROR
    LOG_ERROR --> RETURN_CHECK
    RETURN_CHECK -->|"Error"| RAISE["raise MineruExecutionError"]
```

**Sources:** [raganything/parser.py:731-826]()

---

## Next Steps

1. **[Parser Installation Issues](#12.1)** - Solutions for LibreOffice, MinerU, and dependency conflicts.
2. **[Processing Errors](#12.2)** - Debugging OCR corruption, table loss, and `MineruExecutionError`.
3. **[Query and Storage Issues](#12.3)** - Fixing VLM path validation, retrieval bias, and public URL mapping.

**Sources:** [docs/multimodal_rag_failure_modes.md:1-85](), [raganything/asset_urls.py:1-118]()

---

# Page: Parser Installation Issues

# Parser Installation Issues

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/pypi-publish.yml](.github/workflows/pypi-publish.yml)
- [raganything/parser.py](raganything/parser.py)
- [setup.py](setup.py)
- [tests/testparser_kwargs.py](tests/testparser_kwargs.py)

</details>



## Purpose and Scope

This page documents common installation problems with the document parsing subsystem and their solutions. RAG-Anything supports multiple parser backends—**MinerU**, **Docling**, and **PaddleOCR**—each with distinct dependencies. This page covers installation verification, dependency resolution, and troubleshooting for all supported parsers.

For general parser functionality and usage, see [Document Parsers](#4.1). For processing errors that occur after successful installation, see [Processing Errors](#12.2).

---

## Parser Dependencies Overview

RAG-Anything's parsing subsystem requires different dependencies depending on which parser and file formats you need to support. The `setup.py` file defines specific `extras_require` groups to simplify this process.

### Dependency Categories

| Category | Components | Required By | Installation Method |
|----------|-----------|-------------|-------------------|
| **Core Parser** | `mineru[core]` | `MineruParser` | `pip install mineru[core]` |
| **Core Parser** | `docling` | `DoclingParser` | `pip install docling` |
| **OCR Parser** | `paddleocr`, `pypdfium2` | `PaddleOCRParser` | `pip install raganything[paddleocr]` |
| **Office Conversion**| LibreOffice | All parsers for Office files | System package manager |
| **Image Conversion** | `Pillow` | `MineruParser` for exotic images | `pip install raganything[image]` |
| **Text Conversion**  | `reportlab` | All parsers for TXT/MD | `pip install raganything[text]` |
| **Markdown Support** | `weasyprint`, `markdown` | Enhanced MD conversion | `pip install raganything[markdown]` |

**Sources:** [raganything/parser.py:68-82](), [setup.py:61-84]()

---

## Dependency Installation Flow

The following diagram maps the relationship between system requirements and the Python classes that utilize them.

```mermaid
flowchart TB
    subgraph "Natural Language Space"
        OFFICE["Office Documents (.docx, .pptx)"]
        SCANNED["Scanned PDFs / Images"]
        TEXT_FILES["Plain Text / Markdown"]
    end

    subgraph "Code Entity Space"
        LIBRE["LibreOffice (External)"]
        PADDLE["paddleocr (Python Lib)"]
        REPLAB["reportlab (Python Lib)"]
        
        PARSER_BASE["Parser (Base Class)"]
        MINERU_P["MineruParser"]
        DOCLING_P["DoclingParser"]
        PADDLE_P["PaddleOCRParser"]
    end

    OFFICE -- "Requires" --> LIBRE
    LIBRE -- "Used by" --> PARSER_BASE
    
    SCANNED -- "Processed by" --> PADDLE_P
    PADDLE_P -- "Depends on" --> PADDLE
    
    TEXT_FILES -- "Requires PDF conversion" --> REPLAB
    REPLAB -- "Used in" --> PARSER_BASE
    
    MINERU_P -- "Inherits" --> PARSER_BASE
    DOCLING_P -- "Inherits" --> PARSER_BASE
    PADDLE_P -- "Inherits" --> PARSER_BASE
```

**Sources:** [raganything/parser.py:68-82](), [raganything/parser.py:193-207](), [raganything/parser.py:1262-1270](), [raganything/parser.py:1743-1750]()

---

## MinerU Installation Issues

### Error: `mineru command not found`

**Symptom:** When attempting to parse a document, you receive:
`RuntimeError: mineru command not found. Please ensure MinerU 2.0 is properly installed.`

**Location:** Raised by `MineruParser._run_mineru_command` [raganything/parser.py:784-788]().

**Cause:** The `mineru` CLI tool is not available in the system PATH. Note that MinerU 2.0 no longer includes LibreOffice document conversion; Office files must be converted to PDF first [raganything/parser.py:19-22]().

**Solutions:**
1. **Install MinerU:** `pip install -U 'mineru[core]'`
2. **Verify installation:** 
   ```python
   from raganything.parser import MineruParser
   assert MineruParser().check_installation()
   ```

### MinerU Execution Errors

**Error Class:** `MineruExecutionError` [raganything/parser.py:57-65]()

This exception is raised when the subprocess call to the `mineru` CLI returns a non-zero exit code.
- **return_code:** The exit code from the process.
- **error_msg:** The captured stderr output.

**Sources:** [raganything/parser.py:57-65](), [raganything/parser.py:771-793]()

---

## Docling Installation Issues

### API-Based Integration

Unlike previous versions, `DoclingParser` now utilizes the Docling Python API (`DocumentConverter`) rather than the CLI [tests/testparser_kwargs.py:8-14]().

**Error:** `ImportError: Docling is not installed.`
**Location:** Raised during `_get_converter` [raganything/parser.py:1455-1465]().

**Solution:**
```bash
pip install docling
```

**Kwarg Handling:**
The `DoclingParser` accepts an `env` dictionary for backward compatibility but ignores it in the Python-API path [tests/testparser_kwargs.py:86-91](). However, it performs strict type checking: `env` must be a dictionary with string keys and values [tests/testparser_kwargs.py:131-158]().

**Sources:** [raganything/parser.py:1455-1465](), [tests/testparser_kwargs.py:86-106]()

---

## PaddleOCR Installation Issues

**Symptom:** `PaddleOCRParser` fails to initialize or process files.

**Required Extras:**
```bash
pip install "raganything[paddleocr]"
```
This installs `paddleocr` and `pypdfium2` [setup.py:66-69]().

**Common Issues:**
- **CUDA/GPU Conflicts:** PaddleOCR often requires specific versions of `paddlepaddle-gpu`. If OCR is slow, ensure the correct Paddle backend is installed for your hardware.
- **Memory Errors:** Scanned PDF processing via `PaddleOCRParser` is memory-intensive as it renders pages to images before OCR.

**Sources:** [setup.py:66-69](), [raganything/parser.py:1743-1750]()

---

## LibreOffice Requirement

LibreOffice is mandatory for processing Office formats (`.doc`, `.docx`, `.ppt`, `.pptx`, `.xls`, `.xlsx`) [raganything/parser.py:76]().

### Detection Logic

The `Parser.convert_office_to_pdf` method attempts to locate `libreoffice` or `soffice` in the system path [raganything/parser.py:193-240]().

```mermaid
graph TD
    A["Call convert_office_to_pdf()"] --> B{"Check Platform"}
    B -- "Windows" --> C["Search for soffice.exe in default paths"]
    B -- "Linux/macOS" --> D["Check 'libreoffice' or 'soffice' in PATH"]
    C --> E{"Found?"}
    D --> E
    E -- "No" --> F["Raise RuntimeError: LibreOffice not found"]
    E -- "Yes" --> G["Execute conversion command"]
```

**Sources:** [raganything/parser.py:193-240](), [raganything/parser.py:108-160]()

---

## Skip Installation Check

In some environments (e.g., restricted containers), the standard `check_installation()` might fail even if the parser is functional. 

While the codebase performs these checks during initialization of `MineruParser` [raganything/parser.py:1228-1259]() and `DoclingParser` [raganything/parser.py:1709-1740](), users can bypass or handle these by catching the `RuntimeError` if they are certain the environment is configured correctly.

---

## Summary of Optional Dependencies (`setup.py`)

| Extra Name | Packages | Purpose |
|------------|----------|---------|
| `image` | `Pillow` | Conversion for BMP, TIFF, GIF, WebP [setup.py:63]() |
| `text` | `reportlab` | TXT/MD to PDF conversion [setup.py:64]() |
| `paddleocr` | `paddleocr`, `pypdfium2` | Scanned PDF parsing [setup.py:66-69]() |
| `markdown` | `markdown`, `weasyprint`, `pygments` | Enhanced MD to PDF [setup.py:79-83]() |
| `all` | All above | Full multimodal support [setup.py:70-78]() |

**Sources:** [setup.py:61-84]()

---

# Page: Processing Errors

# Processing Errors

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/multimodal_rag_failure_modes.md](docs/multimodal_rag_failure_modes.md)
- [raganything/asset_urls.py](raganything/asset_urls.py)
- [raganything/processor.py](raganything/processor.py)
- [tests/test_asset_urls.py](tests/test_asset_urls.py)
- [tests/test_insert_content_list.py](tests/test_insert_content_list.py)

</details>



## Purpose and Scope

This page covers errors that occur during document processing, multimodal content analysis, and content extraction in RAG-Anything. It focuses on debugging parsing failures, multimodal processor errors, and recovery strategies. This includes handling OCR corruption, table structure loss, and image-caption misalignment.

The processing pipeline involves three main stages where errors can occur:
1. **Document Parsing** - Converting files to structured content lists.
2. **Content Extraction** - Separating and routing multimodal items.
3. **Multimodal Processing** - Generating descriptions and extracting entities via Vision Language Models (VLMs).

---

## Error Classification System

```mermaid
graph TD
    subgraph "Error Sources"
        PARSE_ERR["Parser Errors<br/>(parser.py)"]
        PROC_ERR["Processing Errors<br/>(processor.py)"]
        MODAL_ERR["Modal Processor Errors<br/>(modalprocessors.py)"]
    end
    
    subgraph "Parser Error Types"
        MINERU_ERR["MineruExecutionError<br/>parser.py:38-46"]
        CONV_ERR["Format Conversion Errors<br/>parser.py:187-196"]
        FILE_ERR["File Access Errors<br/>parser.py:108,989,1063"]
        VAL_ERR["Validation Errors<br/>parser.py:211-216"]
    end
    
    subgraph "Processing Error Types"
        EMPTY_ERR["Empty Content Error<br/>processor.py:428-430"]
        CACHE_ERR["Cache Validation Error<br/>processor.py:160-162"]
        PARSE_FAIL["Parsing Method Failure<br/>processor.py:416-423"]
        MM_PROC_ERR["Multimodal Processing Error<br/>processor.py:540-546"]
    end
    
    subgraph "Modal Processor Error Types"
        JSON_ERR["JSON Parsing Error<br/>modalprocessors.py"]
        IMG_ERR["Image Processing Error<br/>modalprocessors.py"]
        VLM_ERR["VLM Call Failure<br/>modalprocessors.py"]
        FALLBACK["Fallback Entity Creation<br/>modalprocessors.py"]
    end
    
    PARSE_ERR --> MINERU_ERR
    PARSE_ERR --> CONV_ERR
    PARSE_ERR --> FILE_ERR
    PARSE_ERR --> VAL_ERR
    
    PROC_ERR --> EMPTY_ERR
    PROC_ERR --> CACHE_ERR
    PROC_ERR --> PARSE_FAIL
    PROC_ERR --> MM_PROC_ERR
    
    MODAL_ERR --> JSON_ERR
    MODAL_ERR --> IMG_ERR
    MODAL_ERR --> VLM_ERR
    MODAL_ERR --> FALLBACK
```

**Error Classification Hierarchy**

Sources: [raganything/parser.py:38-46](), [raganything/processor.py:416-430]()

---

## Common Multimodal Failure Modes

Real-world documents are often noisy. Below are specific symptoms and their corresponding code-level checks.

### 1. OCR Corruption and Layout Loss
**Symptoms:** Answers quote nonsense, wrong numbers, or mixed columns. OCR confuses ligatures or watermarks.
- **Check:** Inspect the `content_list` produced by `parse_document` [raganything/processor.py:311-457](). Eyeball the `text` blocks in the `*_content_list.json` in the parser output directory.
- **Solution:** Try a different `parse_method` (e.g., forcing `ocr` vs `auto`) or switch the `parser` backend (e.g., `docling` vs `mineru`) [raganything/processor.py:69-74]().

### 2. Table Structure Loss
**Symptoms:** Merged cells, tables rendered as plain text lines, or incorrect row order.
- **Check:** Look for `type: table` blocks in the content list [raganything/utils.py:19-27](). Check if `table_body` or structure fields contain plausible Markdown/HTML.
- **Solution:** Use `TableModalProcessor` to regenerate descriptions from the table image if the structured text is corrupted [raganything/modalprocessors.py:1026-1133]().

### 3. Image-Caption Misalignment
**Symptoms:** Captions match the wrong figure, or images appear in the wrong order.
- **Check:** Validate `img_path` and `caption_list` consistency in `_process_multimodal_content_batch_type_aware` [raganything/processor.py:706-882]().
- **Note:** For DOCX files, equations can be dropped during PDF conversion. Use the OMML helper to recover equations directly from the source [raganything/processor.py:24-27]().

### 4. Public Asset URL Issues
**Symptoms:** Indexed images or tables fail to load in the UI because they reference local filesystem paths.
- **Check:** Verify `RAGANYTHING_PUBLIC_ASSET_BASE_URL` and `RAGANYTHING_PUBLIC_ASSET_STRIP_PREFIX` are set [raganything/asset_urls.py:77-80]().
- **Implementation:** The `attach_public_media_urls` function maps local paths to public URLs for `img_path`, `table_img_path`, and `equation_img_path` [raganything/asset_urls.py:23-27]().

---

## Parser-Level Errors

### MinerU Execution Errors
The `MineruExecutionError` captures failures from the MinerU command-line interface.

```mermaid
flowchart TD
    START["parse_document() called<br/>processor.py:280-457"]
    
    RUN_CMD["_run_mineru_command()<br/>parser.py:617-846"]
    
    EXEC_CHECK{Return Code<br/>== 0?}
    
    ERROR_LOG["Error Lines<br/>Captured"]
    
    RAISE_ERR["Raise MineruExecutionError<br/>parser.py:38-46"]
    
    CATCH_ERR["Catch in parse_document<br/>processor.py:416-418"]
    
    RERAISE["Re-raise to Caller"]
    
    SUCCESS["Parse Successful<br/>Return content_list"]
    
    START --> RUN_CMD
    RUN_CMD --> EXEC_CHECK
    
    EXEC_CHECK -->|No| ERROR_LOG
    ERROR_LOG --> RAISE_ERR
    RAISE_ERR --> CATCH_ERR
    CATCH_ERR --> RERAISE
    
    EXEC_CHECK -->|Yes| SUCCESS
```

**MinerU Execution Error Flow**

| Field | Description |
|-------|-------------|
| `return_code` | Subprocess exit code (e.g., 127 if command not found) [raganything/parser.py:38-46](). |
| `error_msg` | Captured stderr lines (e.g., "CUDA error") [raganything/parser.py:762-792](). |

Sources: [raganything/parser.py:38-46](), [raganything/processor.py:416-423]()

---

## Multimodal Processing Failures

The system uses a two-tier recovery strategy for multimodal content analysis.

```mermaid
graph TD
    START["_process_multimodal_content<br/>processor.py:458-550"]
    
    BATCH["_process_multimodal_content_batch_type_aware<br/>processor.py:706-882"]
    
    BATCH_ERR{Batch<br/>Error?}
    
    FALLBACK["_process_multimodal_content_individual<br/>processor.py:551-705"]
    
    MARK_COMPLETE["_mark_multimodal_processing_complete<br/>processor.py:531,549"]
    
    START --> BATCH
    BATCH --> BATCH_ERR
    BATCH_ERR -->|Yes| FALLBACK
    BATCH_ERR -->|No| MARK_COMPLETE
    FALLBACK --> MARK_COMPLETE
```

**Multimodal Recovery Logic**

### Batch vs. Individual Processing
- **Batch Processing:** Uses `_process_multimodal_content_batch_type_aware` to handle multiple items (images, tables) concurrently to reduce LLM overhead [raganything/processor.py:706-882]().
- **Fallback:** If the batch fails (due to rate limits or context window issues), the system catches the exception and triggers `_process_multimodal_content_individual` to process items one by one [raganything/processor.py:538-546]().

### JSON Parsing Robustness
VLMs often return malformed JSON or wrap it in Markdown tags. `BaseModalProcessor` implements `_robust_json_parse` which:
1. Strips `<thinking>` tags (e.g., from DeepSeek-R1) [raganything/modalprocessors.py:580-589]().
2. Fixes common JSON syntax errors like trailing commas [raganything/modalprocessors.py:628-640]().
3. Uses regex field extraction as a final resort [raganything/modalprocessors.py:657-688]().

Sources: [raganything/processor.py:522-546](), [raganything/modalprocessors.py:547-688]()

---

## Cache Validation Errors

The `ParseCache` prevents redundant parsing but can cause issues if the file or configuration changes.

```mermaid
sequenceDiagram
    participant PC as parse_document
    participant GC as _get_cached_result
    participant Cache as parse_cache
    
    PC->>PC: Generate cache_key<br/>processor.py:316
    PC->>GC: _get_cached_result(cache_key)
    GC->>Cache: get_by_id(cache_key)
    
    alt Cache Hit
        Cache-->>GC: cached_data
        GC->>GC: Check mtime<br/>processor.py:157-162
        alt mtime matches
            GC-->>PC: (content_list, doc_id)
        else mtime changed
            GC-->>PC: None (Invalidate)
        end
    else Cache Miss
        Cache-->>GC: None
    end
```

**Cache Invalidation Triggers:**
- **File Modification:** `current_mtime` from `file_path.stat().st_mtime` must match the cached value [raganything/processor.py:157-162]().
- **Config Change:** Changes in `parser`, `parse_method`, or language settings generate a different `cache_key` [raganything/processor.py:69-98]().

Sources: [raganything/processor.py:133-211](), [raganything/processor.py:65-98]()

---

## Debugging and Manual Recovery

### Manual Recovery Actions
1. **Clear Parse Cache:** If parsing results are corrupted, manually delete the `parse_cache` directory in the `working_dir` to force a re-parse.
2. **Reprocess Failed Docs:** Check `doc_status` for entries where `status == DocStatus.FAILED` [raganything/base.py:16](). Re-run `process_document_complete` for these files [raganything/processor.py:280-457]().
3. **Verify Asset URLs:** If images don't load, use `public_url_for_local_path` to test your environment variable mapping manually [raganything/asset_urls.py:42-62]().

### Logging Points
- **Parser Logs:** Subprocess output is logged with the `[MinerU]` prefix in real-time [raganything/parser.py:709-747]().
- **Multimodal Progress:** Logged at 10% intervals during batch processing [raganything/processor.py:781-790]().

Sources: [raganything/parser.py:709-815](), [raganything/processor.py:781-790](), [raganything/asset_urls.py:42-62]()

---

# Page: Query and Storage Issues

# Query and Storage Issues

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/linting.yaml](.github/workflows/linting.yaml)
- [docs/multimodal_rag_failure_modes.md](docs/multimodal_rag_failure_modes.md)
- [docs/offline_setup.md](docs/offline_setup.md)
- [raganything/asset_urls.py](raganything/asset_urls.py)
- [raganything/batch.py](raganything/batch.py)
- [raganything/query.py](raganything/query.py)
- [scripts/create_tiktoken_cache.py](scripts/create_tiktoken_cache.py)
- [tests/test_asset_urls.py](tests/test_asset_urls.py)

</details>



This page provides technical troubleshooting guidance for query failures and storage backend problems in RAG-Anything. It covers solutions for retrieval bias, VLM path validation, tiktoken network dependencies in offline environments, and database connection issues.

---

## 1. Query System Architecture and Error Points

The query system is implemented via the `QueryMixin` class, which bridges the gap between multimodal content and the underlying `LightRAG` retrieval engine.

### Diagram: Query Execution Flow and System Names
This diagram associates system names with the code entities responsible for query execution and image handling.

```mermaid
graph TB
    subgraph "QueryMixin (raganything/query.py)"
        aquery["aquery()<br/>[raganything/query.py:102-193]"]
        aquery_vlm["aquery_vlm_enhanced()<br/>[raganything/query.py:303-364]"]
        vlm_msg_build["_build_vlm_messages_from_context()<br/>[raganything/query.py:533-607]"]
    end
    
    subgraph "External Models"
        llm_func["llm_model_func<br/>(Text Generation)"]
        vision_func["vision_model_func<br/>(VLM Processing)"]
    end
    
    subgraph "Storage Entities"
        lightrag_inst["self.lightrag<br/>(LightRAG Instance)"]
        chunks_vdb["chunks_vdb<br/>(Vector Storage)"]
        llm_cache["llm_response_cache<br/>(KV Cache)"]
    end

    subgraph "Utilities (raganything/utils.py)"
        validate_img["validate_image_file()"]
        encode_img["encode_image_to_base64()"]
    end

    aquery -->|Auto-detect VLM| aquery_vlm
    aquery_vlm --> vlm_msg_build
    vlm_msg_build --> validate_img
    vlm_msg_build --> encode_img
    aquery_vlm --> vision_func
    aquery --> lightrag_inst
    lightrag_inst --> chunks_vdb
    lightrag_inst --> llm_cache
    lightrag_inst --> llm_func
```

**Sources:**
- [raganything/query.py:102-193]()
- [raganything/query.py:303-364]()
- [raganything/query.py:533-607]()

---

## 2. Retrieval and Query Issues

### 2.1 Retrieval Bias Toward Text
**Symptoms:** The system answers using surrounding text but ignores figures or tables that contain the actual answer.

**Technical Cause:** 
- Multimodal stages may not have run, leaving the knowledge graph without enriched descriptions.
- The `ENABLE_IMAGE_PROCESSING` or `ENABLE_TABLE_PROCESSING` flags were false during ingestion [docs/multimodal_rag_failure_modes.md:42-51]().

**Resolution:**
- Verify multimodal flags in `.env` [docs/multimodal_rag_failure_modes.md:49]().
- Use a "probe question" that can *only* be answered by visual data to verify if descriptions are indexed [docs/multimodal_rag_failure_modes.md:48]().

### 2.2 VLM Path Validation and Image Errors
**Symptoms:** VLM-enhanced queries fail to load images or show "No valid images found".

**Implementation Detail:**
The `aquery_vlm_enhanced` method extracts paths from retrieved context using a specific regex: `Image Path:\s*([^\r\n]*?\.(?:jpg|jpeg|png|gif|bmp|webp|tiff|tif))` [raganything/query.py:551-552]().

**Common Failures:**
- **Regex Mismatch:** If the parser changed the "Image Path:" prefix, the extractor fails [raganything/query.py:556-557]().
- **Validation Failure:** `validate_image_file` is called for every path. If the file is missing or permissions are restricted, the image is skipped [raganything/query.py:571-577]().
- **Encoding Failure:** Large or corrupt images may fail during `encode_image_to_base64` [raganything/query.py:582]().

**Sources:**
- [raganything/query.py:551-582]()
- [docs/multimodal_rag_failure_modes.md:42-51]()

---

## 3. Storage and Network Issues

### 3.1 Tiktoken Network Failures (Offline Mode)
**Symptoms:** `LightRAG` fails to initialize with a `ConnectionError` to `openaipublic.blob.core.windows.net` [docs/offline_setup.md:14-15]().

**Cause:** 
The `tiktoken` library, used by `LightRAG`, attempts to download tokenizer models (like `o200k_base`) on the first run [docs/offline_setup.md:7-9]().

**Solution:**
1. Run the cache creation script in an online environment: `uv run scripts/create_tiktoken_cache.py` [scripts/create_tiktoken_cache.py:1-18]().
2. Set the `TIKTOKEN_CACHE_DIR` environment variable to point to this directory *before* `LightRAG` is imported [docs/offline_setup.md:21-23]().
3. Ensure `.env` is loaded before any imports that trigger `tiktoken` [docs/offline_setup.md:57-61]().

### 3.2 Public Asset URL Mapping
**Symptoms:** UI/Frontend cannot display images because they are stored as local absolute paths (e.g., `/home/user/rag/data/...`) [docs/multimodal_rag_failure_modes.md:66-67]().

**Implementation:**
The `attach_public_media_urls` utility maps local paths to public URLs using `RAGANYTHING_PUBLIC_ASSET_BASE_URL` and `RAGANYTHING_PUBLIC_ASSET_STRIP_PREFIX` [raganything/asset_urls.py:77-78]().

**Code Logic:**
- It iterates over `MEDIA_PATH_FIELDS` (`img_path`, `table_img_path`, etc.) [raganything/asset_urls.py:23-27]().
- It strips the prefix and appends the remainder to the base URL [raganything/asset_urls.py:42-62]().
- Currently, this is only wired into the **MinerU** parser path [raganything/asset_urls.py:8-12]().

**Sources:**
- [docs/offline_setup.md:1-79]()
- [scripts/create_tiktoken_cache.py:1-18]()
- [raganything/asset_urls.py:1-118]()

---

## 4. Database Connection Issues

### Diagram: Storage Backend Code Entities
This diagram maps the environment configuration to the internal storage classes and backend services.

```mermaid
graph LR
    subgraph "Configuration (.env)"
        kv_env["LIGHTRAG_KV_STORAGE"]
        vdb_env["LIGHTRAG_VECTOR_STORAGE"]
        graph_env["LIGHTRAG_GRAPH_STORAGE"]
    end

    subgraph "Storage Classes"
        pg_kv["PGKVStorage"]
        pg_vdb["PGVectorStorage"]
        mongo_kv["MongoKVStorage"]
        milvus_vdb["MilvusVectorStorage"]
        neo4j_graph["Neo4JStorage"]
    end

    subgraph "Backend Services"
        postgres[("PostgreSQL")]
        mongodb[("MongoDB")]
        milvus[("Milvus")]
        neo4j[("Neo4j")]
    end

    kv_env -->|Selects| pg_kv
    kv_env -->|Selects| mongo_kv
    vdb_env -->|Selects| pg_vdb
    vdb_env -->|Selects| milvus_vdb
    graph_env -->|Selects| neo4j_graph

    pg_kv --> postgres
    pg_vdb --> postgres
    mongo_kv --> mongodb
    milvus_vdb --> milvus
    neo4j_graph --> neo4j
```

### Common Backend Errors

| Backend | Common Error | Resolution |
| :--- | :--- | :--- |
| **PostgreSQL** | `Connection refused` | Check `POSTGRES_HOST` and `POSTGRES_PORT`. Ensure the service is running. |
| **Neo4j** | `AuthError` | Verify `NEO4J_USERNAME` and `NEO4J_PASSWORD`. Ensure URI uses `neo4j://` or `bolt://`. |
| **Milvus** | `Collection not found` | Ensure `MILVUS_URI` is correct. Collections are usually created automatically on first insert. |
| **MongoDB** | `ServerSelectionTimeout` | Verify `MONGO_URI`. Check if the database requires specific auth mechanisms in the connection string. |

**Sources:**
- [raganything/batch.py:73-77]() (Initialization checks)
- [docs/multimodal_rag_failure_modes.md:53-61]() (Resource/Hangs)

---

# Page: Glossary

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [raganything/base.py](raganything/base.py)
- [raganything/batch.py](raganything/batch.py)
- [raganything/config.py](raganything/config.py)
- [raganything/modalprocessors.py](raganything/modalprocessors.py)
- [raganything/parser.py](raganything/parser.py)
- [raganything/processor.py](raganything/processor.py)
- [raganything/query.py](raganything/query.py)
- [tests/test_insert_content_list.py](tests/test_insert_content_list.py)
- [tests/testparser_kwargs.py](tests/testparser_kwargs.py)

</details>



This page provides technical definitions for codebase-specific terms, domain concepts, and architectural components within the RAG-Anything framework. It serves as a reference for engineers to understand how natural language concepts map to specific code entities and implementation logic.

## 1. Core RAG Concepts

### Hybrid Retrieval
A retrieval strategy that combines multiple search modalities. In RAG-Anything, this typically refers to the `mix` mode in `QueryMixin.aquery`, which leverages both vector-based similarity and Knowledge Graph-based relationship traversal [raganything/query.py:102-119]().

### Knowledge Graph (KG)
The structural representation of entities and relationships extracted from documents. RAG-Anything extends standard text-based KGs by inserting multimodal entities (images, tables, equations) as nodes and creating `belongs_to` relationships between these elements and their parent documents or surrounding text chunks [raganything/processor.py:202-212]().

### Retrieval Modes
RAG-Anything supports several query modes inherited and extended from LightRAG [raganything/query.py:110-110]():
*   **Naive**: Basic vector retrieval.
*   **Local**: Context-focused retrieval around specific entities.
*   **Global**: High-level summary retrieval across the entire corpus.
*   **Hybrid/Mix**: Combines multiple strategies for balanced results.
*   **Bypass**: Direct LLM call without retrieval.

**Sources:** [raganything/query.py:102-119](), [raganything/processor.py:202-212]()

---

## 2. Document Processing & Storage

### DocStatus
An enumeration defining the lifecycle of a document within the system [raganything/base.py:4-12]().
*   `READY`: Initial state.
*   `HANDLING`: Currently being parsed or processed.
*   `PROCESSED`: Successfully indexed into both text and multimodal storages.
*   `FAILED`: Error encountered during processing.

### Parse Cache
A mechanism to avoid redundant parsing of the same file. The cache key is generated using a hash of the absolute file path, modification time (`mtime`), and the specific parser configuration used [raganything/processor.py:50-98]().

### Working Directory (`working_dir`)
The root directory for all persistent storage, including the Knowledge Graph, vector databases, and the `doc_status` KV store [raganything/config.py:18-19]().

### Logic-to-Code Mapping: Document Lifecycle
The following diagram bridges the conceptual "Document State" to the internal classes and status flags used in the code.

**Title: Document Processing State Flow**
```mermaid
graph TD
    subgraph "Natural Language Space"
        A["New Document"]
        B["Parsing Content"]
        C["Indexing Text"]
        D["Analyzing Images/Tables"]
        E["Ready for Query"]
    end

    subgraph "Code Entity Space"
        A -->|".process_document_complete()"| B
        B -->|"DocStatus.HANDLING"| C
        C -->|"lightrag.ainsert()"| D
        D -->|"_process_multimodal_content()"| E
        E -->|"multimodal_processed: True"| F["doc_status Storage"]
    end

    style B stroke-width:2px
    style E stroke-width:2px
```
**Sources:** [raganything/processor.py:105-160](), [raganything/base.py:4-12](), [raganything/processor.py:202-212]()

---

## 3. Multimodal Terms

### Modal Processor
Specialized classes inheriting from `BaseModalProcessor` (or using `GenericModalProcessor`) that handle specific content types. They typically follow a two-stage lifecycle: generating a textual description for indexing and creating graph entities for retrieval [raganything/modalprocessors.py:5-10]().

### Context Window
The range of surrounding content (measured in pages or chunks) provided to a VLM or LLM when processing a multimodal element to ensure the model understands the surrounding narrative [raganything/modalprocessors.py:40-48]().

### VLM-Enhanced Query
A query mode where the system automatically detects image markers in retrieved text context, retrieves the original images from disk, encodes them as base64, and passes them to a Vision Language Model (VLM) for multimodal reasoning [raganything/query.py:125-143]().

### Logic-to-Code Mapping: Multimodal Retrieval
This diagram shows how a user's query is enriched with visual data before hitting the LLM.

**Title: VLM-Enhanced Retrieval Pipeline**
```mermaid
graph LR
    subgraph "Natural Language Space"
        Q["User Query"]
        R["Retrieved Context"]
        I["Visual Analysis"]
    end

    subgraph "Code Entity Space"
        Q -->|"aquery(vlm_enhanced=True)"| QM["QueryMixin"]
        QM -->|"lightrag.aquery()"| R
        R -->|"re.findall(VLM_IMAGE_MARKER)"| VE["aquery_vlm_enhanced"]
        VE -->|"encode_image_to_base64()"| I
        I -->|"vision_model_func()"| Final["Final Answer"]
    end
```
**Sources:** [raganything/query.py:125-150](), [raganything/utils.py:18-20]()

---

## 4. Parser Terminology

### Parser Registry
A factory system that maps parser names (e.g., "mineru", "docling") to their respective implementation classes. This allows for runtime selection of parsing backends [raganything/parser.py:5-17]().

### OCR (Optical Character Recognition)
Used when `parse_method` is set to `ocr`. This forces the parser to treat the document as an image and extract text via visual recognition, rather than extracting embedded text metadata [raganything/config.py:23-24]().

### OMML Extractor
A specialized utility for extracting Office Math Markup Language (OMML) from `.docx` files and converting it to LaTeX format for indexing and querying [raganything/processor.py:24-25]().

---

## 5. Configuration Abbreviations

| Abbreviation | Full Name / Meaning | Code Pointer |
| :--- | :--- | :--- |
| `VDB` | Vector Database (entities, relationships, or chunks) | [raganything/config.py:18-19]() |
| `mtime` | Modification Time (used for cache invalidation) | [raganything/processor.py:66-66]() |
| `VLM` | Vision Language Model | [raganything/query.py:113-115]() |
| `KV` | Key-Value Storage (used for status tracking) | [raganything/processor.py:161-170]() |
| `OMML` | Office Math Markup Language | [raganything/processor.py:24-25]() |

**Sources:** [raganything/config.py:13-116](), [raganything/processor.py:50-98](), [raganything/query.py:125-150]()