<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/scholarphi · page 4 Data Processing Pipeline · fetched 2026-10-26 -->

# Data Processing Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [data-processing/.dockerignore](data-processing/.dockerignore)
- [data-processing/Dockerfile](data-processing/Dockerfile)
- [data-processing/common/file_utils.py](data-processing/common/file_utils.py)
- [data-processing/common/types.py](data-processing/common/types.py)
- [data-processing/config.ini](data-processing/config.ini)
- [data-processing/requirements.txt](data-processing/requirements.txt)
- [data-processing/scripts/run_pipeline.py](data-processing/scripts/run_pipeline.py)

</details>



## Purpose and Scope

The Data Processing Pipeline is a Python-based system that processes academic papers from arXiv to extract structured entities such as mathematical symbols, equations, citations, and definitions. The pipeline converts LaTeX source documents into annotated data that powers the Scholar Reader's augmented PDF viewing experience.

This document provides an overview of the pipeline architecture, data flow, and orchestration mechanisms. For detailed information about specific components, see:
- Pipeline orchestration and command structure: [Pipeline Architecture and Orchestration](#4.1)
- Document parsing and mathematical notation handling: [LaTeX and MathML Parsing](#4.2)  
- Entity detection algorithms: [Entity Extraction Systems](#4.3)
- ML models for definition detection: [Machine Learning and NLP Models](#4.4)
- Visual entity localization methods: [Entity Localization and Visualization](#4.5)
- Docker environment and dependencies: [Environment and Dependencies](#4.6)

## Pipeline Architecture Overview

The data processing pipeline transforms academic papers through multiple stages, from raw LaTeX sources to structured entities with precise location data.

```mermaid
graph TB
    subgraph "Input Sources"
        ARXIV["arXiv.org"]
        S3_SOURCES["S3 arXiv Sources"]
        RECENT_IDS["FetchNewArxivIds"]
    end
    
    subgraph "Pipeline Orchestration"
        RUN_PIPELINE["run_pipeline.py"]
        COMMAND_LIST["CommandList"]
        TEX_PREP["TEX_PREPARATION_COMMANDS"]
        ENTITY_CMDS["ENTITY_COMMANDS"]
    end
    
    subgraph "Processing Stages"
        FETCH_SOURCES["FetchArxivSources"]
        PARSE_TEX["LaTeX/TeX Parsing"]
        EXTRACT_ENTITIES["Entity Extractors"]
        LOCATE_ENTITIES["LocateEntitiesCommand"]
        DB_UPLOAD["DatabaseUploadCommand"]
    end
    
    subgraph "Data Storage"
        CSV_FILES["CSV Entity Files"]
        POSTGRES_DB["PostgreSQL Database"]
        S3_RESULTS["S3 Results Storage"]
    end
    
    ARXIV --> FETCH_SOURCES
    S3_SOURCES --> FETCH_SOURCES
    RECENT_IDS --> RUN_PIPELINE
    
    RUN_PIPELINE --> COMMAND_LIST
    COMMAND_LIST --> TEX_PREP
    COMMAND_LIST --> ENTITY_CMDS
    
    TEX_PREP --> FETCH_SOURCES
    TEX_PREP --> PARSE_TEX
    ENTITY_CMDS --> EXTRACT_ENTITIES
    ENTITY_CMDS --> LOCATE_ENTITIES
    ENTITY_CMDS --> DB_UPLOAD
    
    FETCH_SOURCES --> PARSE_TEX
    PARSE_TEX --> EXTRACT_ENTITIES
    EXTRACT_ENTITIES --> CSV_FILES
    CSV_FILES --> LOCATE_ENTITIES
    LOCATE_ENTITIES --> DB_UPLOAD
    DB_UPLOAD --> POSTGRES_DB
    
    RUN_PIPELINE --> S3_RESULTS
```

Sources: [data-processing/scripts/run_pipeline.py:31-36](), [data-processing/scripts/run_pipeline.py:104]()

## Entity Processing Data Flow

The pipeline processes different types of entities through specialized extraction and localization workflows.

```mermaid
graph LR
    subgraph "Entity Types"
        CITATIONS["Citations"]
        SYMBOLS["Symbols"] 
        EQUATIONS["Equations"]
        DEFINITIONS["Definitions"]
        SENTENCES["Sentences"]
    end
    
    subgraph "Extraction Phase"
        TEX_SOURCES["TeX Sources"]
        CITATION_EXT["Citation Extractor"]
        SYMBOL_EXT["Symbol Extractor"]
        EQUATION_EXT["Equation Extractor"]
        DEF_EXT["Definition Extractor"]
        SENT_EXT["Sentence Extractor"]
    end
    
    subgraph "Serialization"
        SERIALIZABLE_ENT["SerializableEntity"]
        CSV_STORAGE["CSV Files"]
        LOAD_FUNCTIONS["load_symbols()<br/>load_equations()<br/>load_tokens()"]
    end
    
    subgraph "Localization"
        COLORIZE_TEX["TeX Colorization"]
        COMPILE_TEX["TeX Compilation"]
        RASTER_PDF["PDF Rasterization"]
        BBOX_DETECT["BoundingBox Detection"]
    end
    
    TEX_SOURCES --> CITATION_EXT
    TEX_SOURCES --> SYMBOL_EXT
    TEX_SOURCES --> EQUATION_EXT
    TEX_SOURCES --> DEF_EXT
    TEX_SOURCES --> SENT_EXT
    
    CITATION_EXT --> CITATIONS
    SYMBOL_EXT --> SYMBOLS
    EQUATION_EXT --> EQUATIONS
    DEF_EXT --> DEFINITIONS
    SENT_EXT --> SENTENCES
    
    CITATIONS --> SERIALIZABLE_ENT
    SYMBOLS --> SERIALIZABLE_ENT
    EQUATIONS --> SERIALIZABLE_ENT
    DEFINITIONS --> SERIALIZABLE_ENT
    SENTENCES --> SERIALIZABLE_ENT
    
    SERIALIZABLE_ENT --> CSV_STORAGE
    CSV_STORAGE --> LOAD_FUNCTIONS
    LOAD_FUNCTIONS --> COLORIZE_TEX
    
    COLORIZE_TEX --> COMPILE_TEX
    COMPILE_TEX --> RASTER_PDF
    RASTER_PDF --> BBOX_DETECT
```

Sources: [data-processing/common/types.py:138-182](), [data-processing/common/file_utils.py:330-446]()

## Core Entity Data Structures

The pipeline defines specific data classes for different entity types, each inheriting from `SerializableEntity` to enable CSV storage and retrieval.

| Entity Type | Core Class | Key Attributes | File Storage |
|-------------|------------|----------------|--------------|
| Equations | `Equation` | `i`, `content_tex`, `katex_compatible_tex` | `detected-equations/entities.csv` |
| Symbols | `SerializableSymbol` | `mathml`, `type_`, `is_definition` | `detected-symbols/entities.csv` |
| Tokens | `SerializableToken` | `text`, `type_`, `relative_start` | `detected-equation-tokens/entities.csv` |
| Citations | Various | Citation key, reference data | `citations/entities.csv` |
| Definitions | `Term` | `text`, `definitions`, `sources` | `definitions/entities.csv` |

Sources: [data-processing/common/types.py:191-241](), [data-processing/common/file_utils.py:330-355]()

## Pipeline Command Structure

The `run_pipeline.py` script orchestrates processing through a sequence of commands, each implementing the command pattern with standardized argument parsing.

```mermaid
graph TD
    subgraph "Command Execution Flow"
        ARGS_PARSER["ArgumentParser"]
        PIPELINE_ARGS["pipeline_args"]
        COMMAND_CLASSES["CommandClasses"]
        RUN_COMMANDS["run_commands_for_arxiv_ids()"]
    end
    
    subgraph "Command Types"
        FETCH_CMD["FetchArxivSources"]
        TEX_CMD["TeX Processing Commands"]
        EXTRACT_CMD["Entity Extraction Commands"]
        LOCATE_CMD["LocateEntitiesCommand"]
        UPLOAD_CMD["DatabaseUploadCommand"]
        STORE_CMD["StoreResults<br/>StorePipelineLog"]
    end
    
    subgraph "Command Filtering"
        ENTITY_FILTER["--entities filter"]
        COMMAND_FILTER["--commands filter"] 
        START_END["--start/--end range"]
        EXTRACTION_ONLY["--extraction-only"]
    end
    
    ARGS_PARSER --> PIPELINE_ARGS
    PIPELINE_ARGS --> COMMAND_CLASSES
    COMMAND_CLASSES --> RUN_COMMANDS
    
    RUN_COMMANDS --> FETCH_CMD
    RUN_COMMANDS --> TEX_CMD
    RUN_COMMANDS --> EXTRACT_CMD
    RUN_COMMANDS --> LOCATE_CMD
    RUN_COMMANDS --> UPLOAD_CMD
    RUN_COMMANDS --> STORE_CMD
    
    ENTITY_FILTER --> COMMAND_CLASSES
    COMMAND_FILTER --> COMMAND_CLASSES
    START_END --> COMMAND_CLASSES
    EXTRACTION_ONLY --> COMMAND_CLASSES
```

Sources: [data-processing/scripts/run_pipeline.py:44-99](), [data-processing/scripts/run_pipeline.py:401-453]()

## Configuration and Environment

The pipeline requires a comprehensive environment including LaTeX, Perl, Python ML libraries, and database connectivity.

### Key Dependencies

- **LaTeX Processing**: TeXLive 2020, AutoTeX via Perl 5.22.4
- **ML/NLP**: spaCy, SciSpacy, transformers, pytorch-crf 
- **Database**: PostgreSQL via peewee ORM
- **Image Processing**: OpenCV, ImageMagick, GhostScript
- **Cloud Storage**: AWS CLI for S3 integration

### Configuration Structure

```mermaid
graph LR
    subgraph "config.ini Sections"
        TEX_CONFIG["[tex]<br/>texlive_path<br/>texlive_bin_path"]
        RASTER_CONFIG["[rasterers]<br/>pdf/ps commands"]
        PERL_CONFIG["[perl]<br/>binary path"]
        DB_CONFIG["[input-db]<br/>[output-db]<br/>credentials"]
        DIGEST_CONFIG["[digest]<br/>email settings"]
    end
    
    subgraph "Environment Variables"
        PYTHONPATH["PYTHONPATH=/data-processing"]
        DB_VARS["READER_DB_*<br/>environment variables"]
    end
    
    subgraph "Docker Environment"
        UBUNTU_BASE["ubuntu:bionic"]
        DEPENDENCIES["Multi-stage installation"]
        RUNTIME_ENV["Production container"]
    end
    
    TEX_CONFIG --> DEPENDENCIES
    RASTER_CONFIG --> DEPENDENCIES  
    PERL_CONFIG --> DEPENDENCIES
    DB_CONFIG --> DB_VARS
    DIGEST_CONFIG --> DEPENDENCIES
    
    PYTHONPATH --> RUNTIME_ENV
    DB_VARS --> RUNTIME_ENV
    DEPENDENCIES --> RUNTIME_ENV
```

Sources: [data-processing/config.ini:10-66](), [data-processing/Dockerfile:1-80](), [data-processing/requirements.txt:1-35]()

## Processing Modes and Execution

The pipeline supports flexible execution modes for different use cases, from development to production batch processing.

### Execution Modes

| Mode | Flag | Description | Use Case |
|------|------|-------------|----------|
| Batch Processing | Default | Process all papers together | Production runs |
| One-at-a-time | `--one-paper-at-a-time` | Process papers sequentially | Memory-constrained environments |
| Extraction Only | `--extraction-only` | Skip localization and database upload | Entity extraction testing |
| Dry Run | `--dry-run` | Skip database writes | Testing and validation |

### Input Sources

The pipeline can process papers from multiple sources:

- **Recent Papers**: `--days N` fetches recent arXiv submissions via `FetchNewArxivIds`
- **Specific Papers**: `--arxiv-ids` or `--arxiv-ids-file` for targeted processing  
- **S3 Job Specs**: `--s3-job-spec` for cloud-orchestrated batch jobs
- **Source Location**: `--source arxiv|s3` determines download location

Sources: [data-processing/scripts/run_pipeline.py:164-244](), [data-processing/scripts/run_pipeline.py:466-489]()

## Output and Results Storage

The pipeline generates structured outputs at multiple stages, with configurable storage options for different deployment scenarios.

### Data Output Structure

```mermaid
graph TB
    subgraph "Local File System"
        ENTITY_CSV["Entity CSV Files<br/>entities.csv"]
        LOCATION_CSV["Location CSV Files<br/>entity_locations.csv"] 
        COMPILATION["Compilation Results<br/>compilation_results/"]
        LOGS["Pipeline Logs<br/>pipeline-*.log"]
    end
    
    subgraph "Database Upload"
        ENTITIES_TABLE["Entities Table"]
        BBOX_TABLE["BoundingBox Table"]
        PAPERS_TABLE["Papers Table"]
        VERSION_CONTROL["Data Versioning"]
    end
    
    subgraph "S3 Storage"
        RESULTS_BUCKET["S3 Results Bucket"]
        LOGS_BUCKET["S3 Logs Bucket"]
        DIGEST_EMAIL["Email Digest"]
    end
    
    ENTITY_CSV --> ENTITIES_TABLE
    LOCATION_CSV --> BBOX_TABLE
    COMPILATION --> PAPERS_TABLE
    
    ENTITIES_TABLE --> VERSION_CONTROL
    BBOX_TABLE --> VERSION_CONTROL
    PAPERS_TABLE --> VERSION_CONTROL
    
    LOGS --> RESULTS_BUCKET
    ENTITY_CSV --> RESULTS_BUCKET
    LOCATION_CSV --> RESULTS_BUCKET
    
    LOGS --> LOGS_BUCKET
    RESULTS_BUCKET --> DIGEST_EMAIL
    LOGS_BUCKET --> DIGEST_EMAIL
```

Sources: [data-processing/scripts/run_pipeline.py:250-275](), [data-processing/scripts/run_pipeline.py:491-506](), [data-processing/common/file_utils.py:82-146]()

---

