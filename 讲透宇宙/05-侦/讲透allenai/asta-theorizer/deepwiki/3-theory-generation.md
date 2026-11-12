<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/asta-theorizer · page 3 Theory Generation · fetched 2026-10-26 -->

# Theory Generation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This page documents the core theory generation system in Theorizer, explaining how the system transforms a user query (e.g., "build theories about memory architectures for LLM agents") into synthesized scientific theories. It covers the configuration options, the dual-pathway architecture, and the orchestration of the generation process.

For information about the specific generation modes (literature-supported vs parametric), see [Generation Modes](#3.1). For details on the paper processing pipeline used in literature-supported mode, see [Paper Processing Pipeline](#3.3). For using the web interface or API to submit theory requests, see [Web Interface and API](#3.4). For evaluation of generated theories, see [Evaluation Systems](#4).

## Overview of Theory Generation

The Theorizer system generates scientific theories through a configurable pipeline that can operate in four distinct modes, determined by two orthogonal configuration axes:

| Axis | Options | Effect |
|------|---------|--------|
| **Input Type** | `literature-supported` or `parametric` | Whether to extract evidence from papers or use LLM parametric knowledge |
| **Generation Objective** | `accuracy-focused` or `novelty-focused` | Which prompt template to use during synthesis |

Each combination of these axes results in a different generation mode with its own prompt engineering in `TheorizerProcessing.py`. A typical theory generation request takes 30-60 minutes to process, primarily due to external API rate limits rather than computational constraints.

Sources: [README.md:1-587](), [src/TheorizerProcessing.py:227](), [src/TheorizerProcessing.py:688](), [src/TheorizerProcessing.py:1202](), [src/TheorizerProcessing.py:1590]()

## Theory Generation Configuration Space

The system implements a **2×2 factorial design** resulting in four distinct generation conditions:

```mermaid
graph TD
    Query["User Theory Query<br/>'Build theories about X'"]
    
    Query --> Config["Configuration Selection"]
    
    Config --> Axis1["Input Type Axis"]
    Config --> Axis2["Objective Axis"]
    
    Axis1 --> Lit["literature-supported"]
    Axis1 --> Param["parametric"]
    
    Axis2 --> Acc["accuracy-focused"]
    Axis2 --> Nov["novelty-focused"]
    
    Lit --> C1["Mode 1:<br/>Literature + Accuracy"]
    Lit --> C2["Mode 2:<br/>Literature + Novelty"]
    Param --> C3["Mode 3:<br/>Parametric + Accuracy"]
    Param --> C4["Mode 4:<br/>Parametric + Novelty"]
    
    Acc --> C1
    Acc --> C3
    Nov --> C2
    Nov --> C4
    
    C1 --> P1["TheorizerProcessing.py:L227<br/>buildTheoriesFromEvidence_AccuracyFocused()"]
    C2 --> P2["TheorizerProcessing.py:L1202<br/>buildTheoriesFromEvidence_NoveltyFocused()"]
    C3 --> P3["TheorizerProcessing.py:L688<br/>buildTheoriesParametric_AccuracyFocused()"]
    C4 --> P4["TheorizerProcessing.py:L1590<br/>buildTheoriesParametric_NoveltyFocused()"]
    
    P1 --> Output["4-8 Theories<br/>Stored in TheoryStore"]
    P2 --> Output
    P3 --> Output
    P4 --> Output
```

**Configuration Parameters**

Additional parameters available for literature-supported modes:

| Parameter | Purpose | Default/Range |
|-----------|---------|---------------|
| `num_papers` | Maximum papers to retrieve and process | Up to 100 |
| `knowledge_cutoff_year` | Only use papers published before this year | Configurable for temporal testing |
| `knowledge_cutoff_month` | Month component of cutoff | 1-12 |
| `model_extraction` | LLM for per-paper evidence extraction | Inexpensive model recommended |
| `model_generation` | LLM for final theory synthesis | Powerful model recommended |

Sources: [README.md:220-232](), [src/TheorizerProcessing.py:227-1590]()

## System Architecture and Component Roles

The theory generation system consists of three primary components that orchestrate the end-to-end workflow:

```mermaid
graph TB
    subgraph "Entry Points"
        WebUI["TheorizerWebInterface.py<br/>localhost:8080<br/>Flask web interface"]
        API["Programmatic API<br/>localhost:5002<br/>HTTP POST requests"]
    end
    
    subgraph "Orchestration Layer"
        Server["TheorizerServer.py<br/>TheorizerServer class<br/>Request queue management<br/>State persistence"]
    end
    
    subgraph "Processing Layer"
        Processing["TheorizerProcessing.py<br/>TheorizerProcessing class<br/>4 generation methods<br/>Prompt templates"]
        SEQ["SchemaExtractionQueue.py<br/>SchemaExtractionQueue class<br/>Multi-threaded extraction<br/>Per-paper LLM calls"]
    end
    
    subgraph "External Services"
        Asta["Asta Paper Finder<br/>Local subprocess<br/>Paper discovery + download"]
        MOCR["MistralOCRStore.py<br/>PDF to Markdown conversion<br/>Mistral API required"]
        LLMs["LLM Providers<br/>OpenAI, Anthropic<br/>Theory synthesis + extraction"]
    end
    
    subgraph "Data Stores"
        TheoryStore["TheoryStore<br/>JSON dictionary<br/>theories: {}<br/>extraction_schemas: {}<br/>extraction_results: {}"]
        PaperStore["PaperStore<br/>JSON cache<br/>Full-text papers<br/>OCR-converted content"]
    end
    
    WebUI --> Server
    API --> Server
    
    Server --> Processing
    Server --> SEQ
    Server --> Asta
    Server --> MOCR
    
    Processing --> LLMs
    SEQ --> LLMs
    
    Asta --> PaperStore
    MOCR --> PaperStore
    PaperStore --> SEQ
    
    SEQ --> TheoryStore
    Processing --> TheoryStore
    
    Server --> TheoryStore
```

**Component Responsibilities:**

- **TheorizerServer**: Maintains request queue, manages theory generation lifecycle, handles auto-save backups, exposes HTTP endpoints
- **TheorizerProcessing**: Contains four distinct theory generation methods, each with specialized prompts for the 2×2 configuration space
- **SchemaExtractionQueue**: Multi-threaded extraction manager, generates extraction schemas from theory queries, extracts evidence from papers
- **Asta Paper Finder**: External subprocess for paper discovery via Semantic Scholar API and PDF download
- **MistralOCRStore**: Converts downloaded PDFs to Markdown format using Mistral's specialized OCR API

Sources: [src/TheorizerServer.py:1-400](), [src/TheorizerProcessing.py:1-2000](), [src/SchemaExtractionQueue.py:1-500](), [src/MistralOCRStore.py:1-200](), [src/TheorizerWebInterface.py:1-300]()

## Theory Generation Workflow

The complete workflow differs significantly between literature-supported and parametric modes. Below is the unified workflow showing both paths:

```mermaid
graph TB
    Start["Theory Request Submitted<br/>via Web UI or API"]
    
    Start --> Queue["TheorizerServer.addTheoryQuery()<br/>Add to processing queue"]
    
    Queue --> CheckMode{"Input Type?"}
    
    CheckMode -->|"literature-supported"| LitPath["Literature-Supported Path"]
    CheckMode -->|"parametric"| ParamPath["Parametric Path"]
    
    LitPath --> FindPapers["Asta Paper Finder<br/>subprocess call<br/>Query Semantic Scholar<br/>Download up to num_papers PDFs"]
    
    FindPapers --> CheckPapers{"Papers found?"}
    CheckPapers -->|"No"| Error["Error: No papers found"]
    CheckPapers -->|"Yes"| Convert["MistralOCRStore.convertPDFToMarkdown()<br/>OCR conversion for each PDF<br/>Cache in PaperStore"]
    
    Convert --> GenSchema["SchemaExtractionQueue.generateSchema()<br/>LLM call to create extraction schema<br/>Based on theory query<br/>Store in extraction_schemas"]
    
    GenSchema --> Extract["SchemaExtractionQueue.extractFromPaper()<br/>Multi-threaded extraction<br/>Up to 100 LLM calls (one per paper)<br/>Uses inexpensive model_extraction<br/>Store in extraction_results"]
    
    Extract --> Aggregate["TheorizerProcessing.aggregateEvidence()<br/>Combine evidence across papers<br/>Prepare context for synthesis"]
    
    ParamPath --> DirectSynth["Skip paper processing<br/>Use LLM parametric knowledge"]
    
    Aggregate --> CheckObj{"Generation Objective?"}
    DirectSynth --> CheckObj
    
    CheckObj -->|"accuracy-focused (lit)"| AccLit["buildTheoriesFromEvidence_AccuracyFocused()<br/>TheorizerProcessing.py:L227"]
    CheckObj -->|"novelty-focused (lit)"| NovLit["buildTheoriesFromEvidence_NoveltyFocused()<br/>TheorizerProcessing.py:L1202"]
    CheckObj -->|"accuracy-focused (param)"| AccParam["buildTheoriesParametric_AccuracyFocused()<br/>TheorizerProcessing.py:L688"]
    CheckObj -->|"novelty-focused (param)"| NovParam["buildTheoriesParametric_NoveltyFocused()<br/>TheorizerProcessing.py:L1590"]
    
    AccLit --> Synth["LLM Synthesis<br/>Uses powerful model_generation<br/>Generate 4-8 theories"]
    NovLit --> Synth
    AccParam --> Synth
    NovParam --> Synth
    
    Synth --> Store["TheorizerServer.saveTheoryStore()<br/>Persist to TheoryStore JSON<br/>Auto-save backup<br/>theorizer-state-autosave-*.json"]
    
    Store --> Complete["Theory generation complete<br/>Visible in web interface"]
    
    Error --> Complete
```

Sources: [src/TheorizerServer.py:100-250](), [src/TheorizerProcessing.py:227-1590](), [src/SchemaExtractionQueue.py:1-500](), [README.md:196-298]()

## Theory Structure and Output Format

Generated theories are stored in the `TheoryStore` JSON structure with the following schema:

```mermaid
graph LR
    TheoryStore["TheoryStore JSON"]
    
    TheoryStore --> Theories["theories: {}<br/>Dictionary keyed by theory_id"]
    TheoryStore --> Schemas["extraction_schemas: {}<br/>Dictionary keyed by schema_id"]
    TheoryStore --> Results["extraction_results: {}<br/>Dictionary keyed by result_id"]
    
    Theories --> Theory["Single Theory Object"]
    
    Theory --> TID["theory_id: unique identifier"]
    Theory --> TQuery["theory_query: original request"]
    Theory --> TDesc["description: summary"]
    Theory --> TComponents["components: structured theory parts"]
    Theory --> TLaws["laws: list of theory statements"]
    Theory --> TMeta["metadata: generation params<br/>model, objective, input_type"]
    Theory --> TEvidence["evidence_ids: links to extraction_results"]
    
    Schemas --> Schema["Extraction Schema"]
    Schema --> SFields["fields: list of evidence types<br/>to extract from papers"]
    
    Results --> Result["Extraction Result"]
    Result --> RPaper["paper_id: source paper"]
    Result --> RSchema["schema_id: schema used"]
    Result --> RData["extracted_data: evidence instances"]
```

**Example Theory Law Structure:**

Each theory contains 4-8 laws/statements with the following fields:
- `law_id`: Unique identifier within the theory
- `statement`: Natural language formulation of the law
- `variables`: Identified variables and relationships
- `conditions`: Applicability constraints
- `evidence_support`: Links to extraction results that support this law

Sources: [README.md:483-491](), [src/TheoryStore.py:1-300]()

## Processing Timeline and Cost Considerations

Theory generation is a time-intensive and potentially expensive operation:

| Stage | Typical Duration | Cost Driver |
|-------|------------------|-------------|
| Paper Discovery (Asta) | 1-5 minutes | Semantic Scholar API rate limits |
| PDF Download | 2-10 minutes | Network bandwidth, paper availability |
| PDF→Markdown OCR | 5-15 minutes | Mistral API rate limits (up to 100 calls) |
| Schema Generation | 1-2 minutes | Single LLM call |
| Evidence Extraction | 10-30 minutes | Multiple LLM calls (one per paper, up to 100) |
| Theory Synthesis | 2-5 minutes | Single powerful LLM call with large context |
| **Total** | **30-60 minutes** | **Primarily API rate limits** |

**Cost Optimization Strategies:**

The system employs several cost-reduction techniques:

1. **Two-tier model selection**: Inexpensive models for high-volume extraction (`model_extraction`), expensive models only for final synthesis (`model_generation`)
2. **Caching**: `PaperStore` caches OCR-converted papers, `extraction_results` cached for reuse
3. **Configurable limits**: `num_papers` parameter caps maximum papers processed
4. **Rate limit awareness**: Processing time dominated by external API throttling, not local computation

⚠️ **Warning**: A single literature-supported theory query with 100 papers can make 101+ LLM API calls (1 schema generation + 100 extractions + 1 synthesis). Set hard limits on API keys to avoid unexpected costs.

Sources: [README.md:102](), [README.md:198](), [README.md:243]()

## Monitoring and State Management

The `TheorizerServer` provides real-time monitoring of theory generation status:

**Status Endpoint**: The web interface polls `TheorizerServer.getStatus()` to display:
- Current queue position
- Active processing stage
- Completed theories count
- Error states

**Auto-save Behavior**: After each theory completes, the server automatically saves a backup to `theorizer-state-autosave-<timestamp>.json`. However, this is **unreliable** and should not be the primary persistence method.

**Manual Export**: The recommended persistence method is manual export via the web interface "Export" button, which saves both:
- `TheoryStore`: Complete theory data including schemas and extraction results
- `PaperStore`: Cached full-text papers (note: copyright considerations apply)

Sources: [README.md:246-258](), [src/TheorizerServer.py:300-350]()

## Entry Point Summary

**Web Interface** (`TheorizerWebInterface.py`):
- Runs Flask server on `localhost:8080`
- Form-based theory submission
- Real-time status monitoring
- Theory browsing and export

**Programmatic API** (`TheorizerServer.py`):
- HTTP server on `localhost:5002`
- POST to `/submit_theory_query` with JSON payload
- GET `/status` for queue monitoring
- GET `/export` for data extraction

For detailed API usage, see [Web Interface and API](#3.4).

Sources: [README.md:169-192](), [src/TheorizerWebInterface.py:1-300](), [src/TheorizerServer.py:1-400]()

---

