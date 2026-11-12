<!-- source: DeepWiki mcp.deepwiki.com · repo K-Dense-AI/claude-scientific-skills · page 6 Research Workflows and Tools · fetched 2026-10-26 -->

# Research Workflows and Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [scientific-skills/open-notebook/SKILL.md](scientific-skills/open-notebook/SKILL.md)
- [scientific-skills/open-notebook/references/api_reference.md](scientific-skills/open-notebook/references/api_reference.md)
- [scientific-skills/open-notebook/references/architecture.md](scientific-skills/open-notebook/references/architecture.md)
- [scientific-skills/open-notebook/references/configuration.md](scientific-skills/open-notebook/references/configuration.md)
- [scientific-skills/open-notebook/references/examples.md](scientific-skills/open-notebook/references/examples.md)
- [scientific-skills/open-notebook/scripts/chat_interaction.py](scientific-skills/open-notebook/scripts/chat_interaction.py)
- [scientific-skills/open-notebook/scripts/notebook_management.py](scientific-skills/open-notebook/scripts/notebook_management.py)
- [scientific-skills/open-notebook/scripts/source_ingestion.py](scientific-skills/open-notebook/scripts/source_ingestion.py)
- [scientific-skills/open-notebook/scripts/test_open_notebook_skill.py](scientific-skills/open-notebook/scripts/test_open_notebook_skill.py)
- [scientific-skills/parallel-web/SKILL.md](scientific-skills/parallel-web/SKILL.md)
- [scientific-skills/parallel-web/references/api_reference.md](scientific-skills/parallel-web/references/api_reference.md)
- [scientific-skills/parallel-web/references/deep_research_guide.md](scientific-skills/parallel-web/references/deep_research_guide.md)
- [scientific-skills/parallel-web/references/extraction_patterns.md](scientific-skills/parallel-web/references/extraction_patterns.md)
- [scientific-skills/parallel-web/references/search_best_practices.md](scientific-skills/parallel-web/references/search_best_practices.md)
- [scientific-skills/parallel-web/references/workflow_recipes.md](scientific-skills/parallel-web/references/workflow_recipes.md)
- [scientific-skills/parallel-web/scripts/parallel_web.py](scientific-skills/parallel-web/scripts/parallel_web.py)
- [scientific-skills/research-lookup/README.md](scientific-skills/research-lookup/README.md)
- [scientific-skills/research-lookup/SKILL.md](scientific-skills/research-lookup/SKILL.md)
- [scientific-skills/research-lookup/examples.py](scientific-skills/research-lookup/examples.py)
- [scientific-skills/research-lookup/lookup.py](scientific-skills/research-lookup/lookup.py)

</details>



## Purpose and Scope

This page provides an overview of the research workflow tools in the Claude Scientific Skills system, covering three primary skills for gathering, organizing, and analyzing research information. These tools enable end-to-end research workflows from initial web searches through document organization to AI-powered analysis.

**Covered in this page:**
- `research-lookup` skill: Intelligent research queries with automatic backend routing
- `parallel-web` skill: Web search, deep research, and URL content extraction
- `open-notebook` skill: Self-hosted research organization and analysis platform

**For detailed usage of specific tools, see:**
- Research lookup and web search patterns: [6.1](#6.1)
- Open Notebook platform features: [6.2](#6.2)
- AI reasoning and analysis tools: [6.3](#6.3)

---

## Tool Ecosystem Overview

The research workflow tools provide three complementary capabilities that work together to support scientific research:

| Tool | Primary Use Case | Backend | Key Capability |
|------|-----------------|---------|----------------|
| `research-lookup` | Academic paper searches | Parallel Chat API + Perplexity sonar-pro-search | Auto-routes to optimal backend based on query type |
| `parallel-web` | General web research | Parallel Chat API + Extract API | Synthesized reports with citations from multiple sources |
| `open-notebook` | Research organization | Self-hosted FastAPI + SurrealDB | Document ingestion, AI chat, podcast generation |

### Diagram: Research Tool Architecture

```mermaid
graph TB
    subgraph "User Query Layer"
        UserQuery["User Query:<br/>Natural Language"]
    end
    
    subgraph "Research Lookup (research-lookup skill)"
        ResearchLookupRouter["ResearchLookup Class<br/>scripts/research_lookup.py"]
        AcademicRouter["Academic Query Detection<br/>_assess_query_complexity()"]
        ParallelBackend["Parallel Chat API<br/>core model"]
        PerplexityBackend["Perplexity API<br/>sonar-pro-search"]
    end
    
    subgraph "Parallel Web (parallel-web skill)"
        ParallelChat["ParallelChat Class<br/>scripts/parallel_web.py"]
        ParallelSearch["ParallelSearch Class<br/>web search via Chat API"]
        ParallelDeepResearch["ParallelDeepResearch Class<br/>core model research"]
        ParallelExtract["ParallelExtract Class<br/>Extract API for URLs"]
    end
    
    subgraph "Open Notebook (open-notebook skill)"
        NotebookAPI["FastAPI REST API<br/>api/main.py"]
        NotebookRouters["20 Route Modules<br/>api/routers/*"]
        SurrealDB["SurrealDB<br/>RocksDB backend"]
        LangChainIntegration["LangChain + Esperanto<br/>16+ AI providers"]
    end
    
    UserQuery --> ResearchLookupRouter
    UserQuery --> ParallelChat
    UserQuery --> NotebookAPI
    
    ResearchLookupRouter --> AcademicRouter
    AcademicRouter -->|"Academic keywords"| PerplexityBackend
    AcademicRouter -->|"General research"| ParallelBackend
    
    ParallelChat --> ParallelSearch
    ParallelChat --> ParallelDeepResearch
    ParallelChat --> ParallelExtract
    
    NotebookAPI --> NotebookRouters
    NotebookRouters --> SurrealDB
    NotebookRouters --> LangChainIntegration
    
    style ResearchLookupRouter fill:#e1f5ff
    style ParallelChat fill:#fef3c7
    style NotebookAPI fill:#dcfce7
```

**Sources:**
- [scientific-skills/research-lookup/SKILL.md:1-414]()
- [scientific-skills/parallel-web/SKILL.md:1-315]()
- [scientific-skills/open-notebook/SKILL.md:1-290]()
- [scientific-skills/research-lookup/lookup.py:1-188]()
- [scientific-skills/parallel-web/scripts/parallel_web.py:1-569]()

---

## Research Lookup: Intelligent Backend Routing

The `research-lookup` skill automatically routes queries to the optimal backend based on query content analysis. This routing is implemented in the `ResearchLookup` class.

### Routing Logic Implementation

The automatic routing system analyzes queries for academic keywords and routes accordingly:

```mermaid
graph TB
    Query["User Query Input"]
    
    RoutingDecision{"Query contains<br/>academic keywords?"}
    
    AcademicKeywords["Academic Keywords:<br/>• find papers<br/>• DOI, journal, peer-reviewed<br/>• systematic review<br/>• meta-analysis<br/>• cite, citation, pubmed<br/>• arxiv, preprint"]
    
    PerplexityRoute["Route to Perplexity<br/>sonar-pro-search model<br/>via OpenRouter"]
    
    ParallelRoute["Route to Parallel<br/>Chat API core model<br/>Default backend"]
    
    PerplexityResponse["Academic Search Results:<br/>• Paper citations with DOIs<br/>• Venue tier indicators<br/>• Citation counts<br/>• Scholarly database focus"]
    
    ParallelResponse["General Research Report:<br/>• Multi-source synthesis<br/>• Inline citations with URLs<br/>• Comprehensive analysis<br/>• Structured markdown"]
    
    Query --> RoutingDecision
    RoutingDecision -->|"Yes"| AcademicKeywords
    RoutingDecision -->|"No"| ParallelRoute
    AcademicKeywords --> PerplexityRoute
    
    PerplexityRoute --> PerplexityResponse
    ParallelRoute --> ParallelResponse
```

**Sources:**
- [scientific-skills/research-lookup/SKILL.md:49-97]()
- [scientific-skills/research-lookup/scripts/research_lookup.py:1-end]()
- [scientific-skills/research-lookup/lookup.py:14-188]()

### Backend Capabilities Comparison

| Feature | Parallel Chat API (core) | Perplexity sonar-pro-search |
|---------|--------------------------|----------------------------|
| **Latency** | 60s-5min | 5-15s |
| **Use Case** | Comprehensive multi-source research | Academic paper search |
| **Output Format** | Markdown report with inline citations | Summary with 5-8 paper citations |
| **Citation Style** | Web source URLs | DOI, journal, authors, year |
| **Database Priority** | Authoritative web sources | Scholarly databases (PubMed, arXiv) |
| **Cost** | $0.025 per 1000 tokens | Via OpenRouter rates |

**Sources:**
- [scientific-skills/research-lookup/SKILL.md:196-222]()
- [scientific-skills/parallel-web/references/api_reference.md:189-228]()

### Code Entity Mapping

The routing implementation maps to these code constructs:

| Functionality | Code Location | Class/Function |
|---------------|---------------|----------------|
| Main lookup interface | `research-lookup/lookup.py` | `main()` function |
| Backend routing | `research-lookup/scripts/research_lookup.py` | `ResearchLookup.lookup()` |
| Academic keyword detection | `research-lookup/SKILL.md:64-73` | Documented in routing logic |
| Parallel API client | `parallel-web/scripts/parallel_web.py:53-163` | `ParallelChat` class |
| Perplexity integration | Via OpenRouter SDK | OpenRouter API client |

**Sources:**
- [scientific-skills/research-lookup/lookup.py:149-188]()
- [scientific-skills/research-lookup/SKILL.md:49-97]()
- [scientific-skills/parallel-web/scripts/parallel_web.py:53-163]()

---

## Parallel Web Systems: Multi-Purpose Research API

The `parallel-web` skill provides three complementary capabilities through the Parallel Web Systems APIs:

### Core Classes Architecture

```mermaid
graph LR
    subgraph "Python Client Classes (parallel_web.py)"
        ParallelChat["ParallelChat<br/>Base Chat API client<br/>lines 53-163"]
        ParallelSearch["ParallelSearch<br/>Web search wrapper<br/>lines 165-222"]
        ParallelDeepResearch["ParallelDeepResearch<br/>Research report generator<br/>lines 300-365"]
        ParallelExtract["ParallelExtract<br/>URL content extraction<br/>lines 224-298"]
    end
    
    subgraph "External APIs"
        ChatAPI["Parallel Chat API<br/>https://api.parallel.ai<br/>OpenAI-compatible"]
        ExtractAPI["Parallel Extract API<br/>Beta endpoint<br/>URL content extraction"]
    end
    
    ParallelSearch --> ParallelChat
    ParallelDeepResearch --> ParallelChat
    ParallelChat --> ChatAPI
    ParallelExtract --> ExtractAPI
    
    style ParallelChat fill:#e1f5ff
    style ParallelSearch fill:#fef3c7
    style ParallelDeepResearch fill:#dcfce7
    style ParallelExtract fill:#f3e8ff
```

**Sources:**
- [scientific-skills/parallel-web/scripts/parallel_web.py:53-365]()
- [scientific-skills/parallel-web/SKILL.md:46-120]()
- [scientific-skills/parallel-web/references/api_reference.md:1-245]()

### Model Selection Matrix

The Chat API supports two research models with different latency/depth tradeoffs:

| Model | Latency | Token Cost | Best For | CLI Usage |
|-------|---------|------------|----------|-----------|
| `base` | 15-100s | $10/1000 | Standard web searches, quick lookups | `--model base` |
| `core` | 60s-5min | $25/1000 | Complex multi-source research, comprehensive reports | `--model core` (default for research) |

**Command-line interface mapping:**

```bash
# ParallelSearch with base model (default)
python scripts/parallel_web.py search "query" --model base -o output.md

# ParallelDeepResearch with core model (default)
python scripts/parallel_web.py research "query" --model core -o output.md

# ParallelExtract for verification
python scripts/parallel_web.py extract "url" --objective "focus" -o output.md
```

**Sources:**
- [scientific-skills/parallel-web/SKILL.md:122-134]()
- [scientific-skills/parallel-web/scripts/parallel_web.py:467-565]()
- [scientific-skills/parallel-web/references/api_reference.md:189-202]()

### Extract API vs Chat API Usage

The Extract API should only be used for specific URL verification, not general research:

| Scenario | Use Tool | Rationale |
|----------|----------|-----------|
| "Find papers on topic X" | `parallel_web.py search` or `research_lookup.py` | Need to discover URLs |
| "Verify citation at URL Y" | `parallel_web.py extract` | Known URL to verify |
| "Research company Z" | `parallel_web.py research` | Need synthesis from multiple sources |
| "Get DOI metadata" | `parallel_web.py extract` | Known DOI URL |
| "Market analysis of industry W" | `parallel_web.py research --model core` | Comprehensive multi-source research |

**Sources:**
- [scientific-skills/parallel-web/SKILL.md:17-44]()
- [scientific-skills/parallel-web/references/extraction_patterns.md:20-33]()

---

## Open Notebook: Self-Hosted Research Platform

Open Notebook provides a complete research organization platform as an alternative to Google NotebookLM, with full REST API access and multi-provider AI support.

### System Architecture

```mermaid
graph TB
    subgraph "Docker Compose Stack"
        Frontend["Next.js Frontend<br/>Port 8502<br/>React UI"]
        Backend["FastAPI Backend<br/>Port 5055<br/>api/main.py"]
        Database["SurrealDB<br/>Port 8000<br/>RocksDB storage"]
    end
    
    subgraph "FastAPI Route Modules (api/routers/)"
        NotebooksRouter["/api/notebooks<br/>CRUD + associations"]
        SourcesRouter["/api/sources<br/>Ingestion + processing"]
        NotesRouter["/api/notes<br/>Human + AI notes"]
        ChatRouter["/api/chat<br/>Sessions + execution"]
        SearchRouter["/api/search<br/>Vector + text search"]
        PodcastsRouter["/api/podcasts<br/>Generation + audio"]
        TransformationsRouter["/api/transformations<br/>Custom pipelines"]
        ModelsRouter["/api/models<br/>Provider config"]
        CredentialsRouter["/api/credentials<br/>API key management"]
    end
    
    subgraph "AI Integration (open_notebook/)"
        LangChainGraphs["LangGraph State Machines<br/>graphs/chat_graph.py"]
        EsperantoLib["Esperanto Multi-Provider<br/>ai/esperanto_integration.py"]
        PodcastPipeline["Podcast Generator<br/>podcasts/generator.py"]
    end
    
    Frontend --> Backend
    Backend --> NotebooksRouter
    Backend --> SourcesRouter
    Backend --> NotesRouter
    Backend --> ChatRouter
    Backend --> SearchRouter
    Backend --> PodcastsRouter
    Backend --> TransformationsRouter
    Backend --> ModelsRouter
    Backend --> CredentialsRouter
    
    NotebooksRouter --> Database
    SourcesRouter --> Database
    NotesRouter --> Database
    ChatRouter --> Database
    SearchRouter --> Database
    
    ChatRouter --> LangChainGraphs
    PodcastsRouter --> PodcastPipeline
    LangChainGraphs --> EsperantoLib
    PodcastPipeline --> EsperantoLib
    
    style Backend fill:#e1f5ff
    style Database fill:#fef3c7
    style EsperantoLib fill:#dcfce7
```

**Sources:**
- [scientific-skills/open-notebook/references/architecture.md:1-164]()
- [scientific-skills/open-notebook/SKILL.md:271-287]()
- [scientific-skills/open-notebook/references/api_reference.md:1-716]()

### Core REST API Endpoints

The Open Notebook REST API exposes 20 route modules. Key endpoints:

| Route Group | Base Path | Primary Operations | Code Location |
|-------------|-----------|-------------------|---------------|
| Notebooks | `/api/notebooks` | List, create, update, delete notebooks | `api/routers/notebooks.py` |
| Sources | `/api/sources` | Upload files, ingest URLs, process content | `api/routers/sources.py` |
| Notes | `/api/notes` | Create human/AI notes, manage associations | `api/routers/notes.py` |
| Chat | `/api/chat/sessions` | Create sessions, execute messages with context | `api/routers/chat.py` |
| Search | `/api/search` | Vector/text search, AI-powered Q&A | `api/routers/search.py` |
| Podcasts | `/api/podcasts` | Generate multi-speaker podcasts, download audio | `api/routers/podcasts.py` |
| Models | `/api/models` | Discover, register, assign default models | `api/routers/models.py` |
| Credentials | `/api/credentials` | Manage encrypted API keys per provider | `api/routers/credentials.py` |

**Sources:**
- [scientific-skills/open-notebook/references/api_reference.md:15-716]()
- [scientific-skills/open-notebook/SKILL.md:256-268]()
- [scientific-skills/open-notebook/references/architecture.md:30-51]()

### Source Processing Pipeline

Open Notebook ingests diverse content types through an asynchronous processing pipeline:

```mermaid
graph LR
    Upload["Source Upload<br/>POST /api/sources"]
    
    CreateRecord["Create Source Record<br/>status: pending"]
    
    ProcessingQueue["Background Processing Queue<br/>process_async=true"]
    
    subgraph "Content Extraction"
        PDFExtract["PDF Text Extraction"]
        WebScrape["Web URL Scraping"]
        AudioTranscribe["Audio Transcription<br/>STT model"]
        VideoTranscribe["Video Transcription<br/>STT model"]
        DocxParse["Office Document Parsing"]
    end
    
    EmbedGenerate["Generate Embeddings<br/>Embedding model"]
    
    IndexSearch["Index for Search<br/>SurrealDB full-text + vector"]
    
    StatusComplete["Update Status<br/>status: completed"]
    
    Upload --> CreateRecord
    CreateRecord --> ProcessingQueue
    
    ProcessingQueue --> PDFExtract
    ProcessingQueue --> WebScrape
    ProcessingQueue --> AudioTranscribe
    ProcessingQueue --> VideoTranscribe
    ProcessingQueue --> DocxParse
    
    PDFExtract --> EmbedGenerate
    WebScrape --> EmbedGenerate
    AudioTranscribe --> EmbedGenerate
    VideoTranscribe --> EmbedGenerate
    DocxParse --> EmbedGenerate
    
    EmbedGenerate --> IndexSearch
    IndexSearch --> StatusComplete
```

**Sources:**
- [scientific-skills/open-notebook/scripts/source_ingestion.py:1-161]()
- [scientific-skills/open-notebook/references/api_reference.md:103-199]()
- [scientific-skills/open-notebook/references/architecture.md:82-96]()

### Multi-Provider AI Configuration

Open Notebook supports 16+ AI providers through the Esperanto library. Configuration workflow:

```mermaid
sequenceDiagram
    participant User
    participant CredAPI as "/api/credentials"
    participant ModelsAPI as "/api/models"
    participant EsperantoLib as "Esperanto Library"
    participant Provider as "AI Provider API"
    
    User->>CredAPI: POST /api/credentials<br/>{provider, api_key}
    CredAPI->>CredAPI: Encrypt API key
    CredAPI-->>User: {credential_id}
    
    User->>CredAPI: POST /credentials/{id}/test
    CredAPI->>Provider: Test connection
    Provider-->>CredAPI: Success
    CredAPI-->>User: {success: true}
    
    User->>CredAPI: POST /credentials/{id}/discover
    CredAPI->>EsperantoLib: Enumerate models
    EsperantoLib->>Provider: List available models
    Provider-->>EsperantoLib: Model metadata
    EsperantoLib-->>CredAPI: Discovered models
    CredAPI-->>User: {models: [...]}
    
    User->>CredAPI: POST /credentials/{id}/register-models<br/>{model_ids: [...]}
    CredAPI->>ModelsAPI: Create model records
    ModelsAPI-->>User: Models registered
    
    User->>ModelsAPI: POST /api/models/auto-assign
    ModelsAPI->>ModelsAPI: Assign default models<br/>for 7 service slots
    ModelsAPI-->>User: Defaults assigned
```

**Sources:**
- [scientific-skills/open-notebook/SKILL.md:87-140]()
- [scientific-skills/open-notebook/references/configuration.md:98-140]()
- [scientific-skills/open-notebook/references/api_reference.md:609-716]()

---

## Workflow Integration Patterns

### Pattern 1: Research → Save → Organize

Standard workflow for gathering and organizing research materials:

```mermaid
graph TB
    Start["Research Query"]
    
    Lookup["research_lookup.py<br/>Auto-routes to optimal backend"]
    
    SaveSources["MANDATORY: Save to sources/<br/>-o sources/research_YYYYMMDD_*.md"]
    
    CheckExisting["Check sources/ for<br/>existing results before<br/>new API calls"]
    
    IngestNotebook["Upload to Open Notebook<br/>POST /api/sources<br/>{file or url}"]
    
    ProcessContent["Background Processing<br/>Extraction + Embeddings"]
    
    SearchChat["Chat with Documents<br/>POST /api/chat/execute"]
    
    Start --> CheckExisting
    CheckExisting -->|"Not found"| Lookup
    CheckExisting -->|"Found"| IngestNotebook
    Lookup --> SaveSources
    SaveSources --> IngestNotebook
    IngestNotebook --> ProcessContent
    ProcessContent --> SearchChat
    
    style SaveSources fill:#ff6b6b
```

**Key requirement:** All research results MUST be saved to `sources/` folder with timestamp:

```bash
# research-lookup saves
python research_lookup.py "query" -o sources/research_20250217_143000_topic.md

# parallel-web saves  
python scripts/parallel_web.py search "query" -o sources/search_20250217_143000_topic.md
python scripts/parallel_web.py research "query" -o sources/research_20250217_143000_topic.md
```

**Sources:**
- [scientific-skills/research-lookup/SKILL.md:241-328]()
- [scientific-skills/parallel-web/SKILL.md:190-248]()
- [scientific-skills/open-notebook/scripts/source_ingestion.py:1-161]()

### Pattern 2: Multi-Tool Research Pipeline

Combining tools for comprehensive research workflows:

```mermaid
graph TB
    Literature["Literature Review Phase"]
    
    AcademicSearch["research-lookup<br/>Academic paper searches<br/>Routes to Perplexity"]
    
    WebContext["parallel-web search<br/>Industry context<br/>base model"]
    
    DeepResearch["parallel-web research<br/>Comprehensive analysis<br/>core model"]
    
    SaveAll["Save all to sources/<br/>with citations preserved"]
    
    CreateNotebook["Open Notebook<br/>Create notebook<br/>POST /api/notebooks"]
    
    IngestSources["Upload saved results<br/>POST /api/sources<br/>process_async=true"]
    
    WaitProcessing["Poll status<br/>GET /api/sources/{id}/status"]
    
    ChatAnalysis["Context-aware chat<br/>POST /api/chat/execute<br/>include_sources=true"]
    
    GeneratePodcast["Generate podcast<br/>POST /api/podcasts/generate<br/>1-4 speakers"]
    
    Literature --> AcademicSearch
    Literature --> WebContext
    Literature --> DeepResearch
    
    AcademicSearch --> SaveAll
    WebContext --> SaveAll
    DeepResearch --> SaveAll
    
    SaveAll --> CreateNotebook
    CreateNotebook --> IngestSources
    IngestSources --> WaitProcessing
    WaitProcessing --> ChatAnalysis
    ChatAnalysis --> GeneratePodcast
    
    style SaveAll fill:#ff6b6b
```

**Sources:**
- [scientific-skills/parallel-web/references/workflow_recipes.md:1-457]()
- [scientific-skills/open-notebook/references/examples.md:1-291]()
- [scientific-skills/research-lookup/SKILL.md:329-414]()

### Pattern 3: URL Verification and Citation Management

Workflow for verifying and extracting citation metadata:

```mermaid
graph LR
    FindPaper["Search for Paper<br/>parallel_web.py search<br/>or research_lookup.py"]
    
    ExtractURL["Get URL/DOI<br/>from search results"]
    
    VerifyContent["Verify Content<br/>parallel_web.py extract<br/>--objective 'citation metadata'"]
    
    SaveVerified["Save to sources/<br/>extract_YYYYMMDD_*.md"]
    
    StructuredData["Extract Structured Data<br/>Authors, Title, Journal,<br/>Year, Volume, Pages, DOI"]
    
    FindPaper --> ExtractURL
    ExtractURL --> VerifyContent
    VerifyContent --> SaveVerified
    SaveVerified --> StructuredData
```

**Example command sequence:**

```bash
# Step 1: Find papers
python research_lookup.py "Find papers on transformer attention NeurIPS 2024" \
  -o sources/papers_20250217_transformers.md

# Step 2: Extract from specific DOI
python scripts/parallel_web.py extract "https://doi.org/10.48550/arXiv.1706.03762" \
  --objective "Complete citation: authors, title, venue, year, DOI" \
  -o sources/extract_20250217_attention_paper.md
```

**Sources:**
- [scientific-skills/parallel-web/references/workflow_recipes.md:74-113]()
- [scientific-skills/parallel-web/references/extraction_patterns.md:249-291]()

---

## Mandatory File Saving Requirements

All research tools enforce mandatory saving of results to the `sources/` folder for reproducibility and context window recovery:

### Saving Rules by Tool

| Tool | `-o` Flag Requirement | Filename Pattern | Preserved Data |
|------|-----------------------|------------------|----------------|
| `research_lookup.py` | MANDATORY | `research_YYYYMMDD_HHMMSS_<topic>.md` | Response text + Sources list + Additional References with DOIs |
| `parallel_web.py search` | MANDATORY | `search_YYYYMMDD_HHMMSS_<topic>.md` | Synthesized summary + source citations |
| `parallel_web.py research` | MANDATORY | `research_YYYYMMDD_HHMMSS_<topic>.md` | Full markdown report + citation objects |
| `parallel_web.py extract` | MANDATORY | `extract_YYYYMMDD_HHMMSS_<source>.md` | Extracted content + metadata |

### Citation Preservation Formats

Each tool preserves citations in structured formats:

**research-lookup output:**
```markdown
# Research Results

[Response text with inline citations]

## Sources (N):
1. [Title] (Date)
   URL

## Additional References (N):
1. DOI: 10.xxxx/xxxxx → URL
```

**parallel-web output:**
```markdown
# Research Report

[Synthesized content]

========================================== SOURCES ==========================================
  [1] Title
      URL
```

**JSON format (maximum citation metadata):**
```json
{
  "success": true,
  "response": "...",
  "citations": [
    {
      "type": "doi",
      "doi": "10.xxxx/xxxxx",
      "url": "https://...",
      "title": "..."
    }
  ]
}
```

**Sources:**
- [scientific-skills/research-lookup/SKILL.md:241-328]()
- [scientific-skills/parallel-web/SKILL.md:190-248]()

---

## Environment Configuration

Required environment variables for each tool:

| Tool | Variable | Purpose | Source |
|------|----------|---------|--------|
| `research-lookup` | `PARALLEL_API_KEY` | Primary backend (Parallel Chat API) | https://platform.parallel.ai |
| `research-lookup` | `OPENROUTER_API_KEY` | Academic search (Perplexity via OpenRouter) | https://openrouter.ai |
| `parallel-web` | `PARALLEL_API_KEY` | Search + research (Parallel Chat API) | https://platform.parallel.ai |
| `open-notebook` | `OPEN_NOTEBOOK_ENCRYPTION_KEY` | Required for credential encryption | User-generated secure key |
| `open-notebook` | `SURREAL_URL` | SurrealDB connection | `ws://surrealdb:8000/rpc` (Docker default) |

**Sources:**
- [scientific-skills/research-lookup/SKILL.md:196-204]()
- [scientific-skills/parallel-web/SKILL.md:272-283]()
- [scientific-skills/open-notebook/references/configuration.md:60-96]()

---

## Performance and Cost Characteristics

| Operation | Tool | Typical Latency | Approx. Cost | Use Case |
|-----------|------|----------------|--------------|----------|
| Academic paper search | `research_lookup.py` (Perplexity) | 5-15s | $0.01-0.05 | Finding scholarly papers with DOIs |
| General web search | `parallel_web.py search` (base) | 15-100s | $0.01/1K tokens | Quick fact lookups, current events |
| Deep research report | `parallel_web.py research` (core) | 60s-5min | $0.025/1K tokens | Comprehensive multi-source analysis |
| URL content extraction | `parallel_web.py extract` | 1-20s | $0.001/URL | Citation verification |
| Source ingestion | Open Notebook | 5-60s | Depends on AI provider | PDF/video processing + embeddings |
| Chat with documents | Open Notebook | 5-30s | Depends on AI provider | Context-aware Q&A |
| Podcast generation | Open Notebook | 5-30min | Depends on TTS provider | Multi-speaker audio from research |

**Sources:**
- [scientific-skills/research-lookup/README.md:50-56]()
- [scientific-skills/parallel-web/references/workflow_recipes.md:438-449]()
- [scientific-skills/parallel-web/references/api_reference.md:173-185]()

---

