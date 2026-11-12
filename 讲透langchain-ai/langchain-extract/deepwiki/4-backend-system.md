<!-- source: DeepWiki mcp.deepwiki.com · repo langchain-ai/langchain-extract · page 4 Backend System · fetched 2026-10-26 -->

# Backend System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/poetry.lock](backend/poetry.lock)
- [backend/pyproject.toml](backend/pyproject.toml)
- [backend/server/main.py](backend/server/main.py)
- [backend/server/models.py](backend/server/models.py)
- [backend/tests/unit_tests/fake/test_fake_chat_model.py](backend/tests/unit_tests/fake/test_fake_chat_model.py)

</details>



The Backend System of LangChain Extract is a FastAPI-based server that provides RESTful APIs for extracting structured information from text and documents using various Language Models (LLMs). It forms the core processing engine of the application, handling extractor definitions, document parsing, and the actual extraction process.

For information about specific extraction functionality, see [Extraction Engine](#4.1). For API endpoint details, see [API Endpoints](#4.2).

## System Architecture

The LangChain Extract backend consists of a FastAPI server exposing several API endpoints, with core services for model integration, document processing, and extraction logic.

```mermaid
graph TD
    subgraph "Backend System"
        FastAPI["FastAPI Server (main.py)"]
        
        subgraph "API Endpoints"
            ExtractorsAPI["/extractors"]
            ExtractAPI["/extract"]
            ExamplesAPI["/examples"]
            SuggestAPI["/suggest"]
            SharedAPI["/shared"]
            ConfigAPI["/configurables"]
            LangServeAPI["/extract_text"]
        end
        
        subgraph "Core Services"
            ModelIntegration["Model Integration (models.py)"]
            ExtractRunnable["extraction_runnable"]
            DocProcessing["Document Processing"]
            ExtractorMgmt["Extractor Management"]
        end
        
        Database[(PostgreSQL)]
    end
    
    Client["Client Applications"] --> FastAPI
    
    FastAPI --> ExtractorsAPI & ExtractAPI & ExamplesAPI & SuggestAPI & SharedAPI & ConfigAPI & LangServeAPI
    
    ExtractorsAPI --> ExtractorMgmt
    ExtractAPI --> ExtractRunnable
    ExtractAPI --> DocProcessing
    ExamplesAPI --> ExtractorMgmt
    SuggestAPI --> ModelIntegration
    LangServeAPI --> ExtractRunnable
    
    ExtractorMgmt --> Database
    ExtractRunnable --> ModelIntegration
```

Sources: [backend/server/main.py:1-83](), [backend/server/models.py:1-87]()

## FastAPI Server

The server is built using FastAPI, defined in `main.py`. It configures middleware, registers API routes, and serves the frontend application when available.

Key components include:
- CORS middleware for cross-origin request handling
- Registration of various API routers
- LangServe integration for the extraction runnable
- Static file serving for the frontend

```python
# FastAPI application configuration
app = FastAPI(
    title="Extraction Powered by LangChain",
    description="An extraction service powered by LangChain.",
    version="0.0.1",
    openapi_tags=[
        {
            "name": "extraction",
            "description": "Operations related to extracting content from text.",
        }
    ],
)
```

The API routes are registered as follows:

```python
# Include API endpoints
app.include_router(extractors.router)
app.include_router(examples.router)
app.include_router(extract.router)
app.include_router(suggest.router)
app.include_router(shared.router)
app.include_router(configurables.router)

# Add LangServe route
add_routes(
    app,
    extraction_runnable.with_types(
        input_type=ExtractRequest, output_type=ExtractResponse
    ),
    path="/extract_text",
    enabled_endpoints=["invoke", "batch"],
)
```

Sources: [backend/server/main.py:6-76]()

## API Endpoints

The backend exposes several API endpoints that handle different aspects of the extraction system:

| Endpoint | Purpose |
|----------|---------|
| `/extractors` | Managing extraction schemas and configurations |
| `/extract` | Performing extraction on text or documents |
| `/examples` | Managing few-shot examples for improving extraction accuracy |
| `/suggest` | Generating schema or extraction suggestions |
| `/shared` | Handling shared extractor links |
| `/configurables` | Exposing system capabilities and configurations |
| `/extract_text` | LangServe route for extraction runnable |

Sources: [backend/server/main.py:52-58](), [backend/server/main.py:60-67]()

## Model Integration

The system integrates with multiple LLM providers through the `models.py` module, which provides a unified interface for accessing different language models. Available models are determined based on API keys present in the environment.

```mermaid
graph TD
    subgraph "Model Registry System"
        SUPPORTED_MODELS["SUPPORTED_MODELS Dictionary"]
        get_model["get_model() Function"]
        get_chunk_size["get_chunk_size() Function"]
        
        subgraph "Environment Detection"
            EnvVars["API Key Environment Variables"]
            ModelConfig["Model Configurations"]
        end
    end
    
    subgraph "LLM Providers"
        OpenAI["OpenAI (gpt-3.5-turbo, gpt-4)"]
        Anthropic["Anthropic (Claude)"]
        Fireworks["Fireworks"]
        Groq["Groq"]
        TogetherAI["Together AI (Mixtral)"]
    end
    
    subgraph "Extraction Components"
        extraction_runnable["extraction_runnable"]
        extract_api["extract API"]
    end
    
    EnvVars -->|"Detected Keys"| SUPPORTED_MODELS
    ModelConfig -->|"Default Settings"| SUPPORTED_MODELS
    
    OpenAI & Anthropic & Fireworks & Groq & TogetherAI -->|"Provider Integration"| SUPPORTED_MODELS
    
    extract_api -->|"Requested Model"| get_model
    SUPPORTED_MODELS -->|"Available Models"| get_model
    get_model -->|"Selected LLM"| extraction_runnable
    extract_api -->|"Model Context Size"| get_chunk_size
```

The model registry dynamically loads models based on environment configuration:

```python
def get_supported_models():
    """Get models according to environment secrets."""
    models = {}
    if "OPENAI_API_KEY" in os.environ:
        models["gpt-3.5-turbo"] = {
            "chat_model": ChatOpenAI(model="gpt-3.5-turbo", temperature=0),
            "description": "GPT-3.5 Turbo",
        }
        if os.environ.get("DISABLE_GPT4", "").lower() != "true":
            models["gpt-4-0125-preview"] = {
                "chat_model": ChatOpenAI(model="gpt-4-0125-preview", temperature=0),
                "description": "GPT-4 0125 Preview",
            }
    # Additional model providers...
```

Sources: [backend/server/models.py:1-87](), [backend/pyproject.toml:15-30]()

## Extraction Process Flow

The following sequence diagram illustrates the data flow during an extraction process:

```mermaid
sequenceDiagram
    participant Client
    participant API as "API Endpoints"
    participant Extractor as "Extractor Manager"
    participant Parser as "Document Parser"
    participant Engine as "Extraction Engine"
    participant LLM as "Language Models"
    participant DB as "PostgreSQL"
    
    Client->>API: POST /extract with text or file
    
    alt Is file upload
        API->>Parser: parse_binary_input(file)
        Parser-->>API: Extracted text content
    end
    
    API->>Extractor: Get extractor config by ID
    Extractor->>DB: Query extractor
    DB-->>Extractor: Extractor definition
    Extractor-->>API: Schema and instructions
    
    alt Extraction mode: entire_document
        API->>Engine: extract_entire_document(text, extractor, model)
        Engine->>Engine: Split text into chunks
        loop For each chunk
            Engine->>LLM: Process with extraction prompt
            LLM-->>Engine: Extraction results
        end
        Engine->>Engine: Deduplicate results
    else Extraction mode: retrieval
        API->>Engine: extract_from_content(text, extractor, model)
        Engine->>Engine: Create vector store from text
        Engine->>LLM: Process with extraction_runnable
        LLM-->>Engine: Extraction results
    end
    
    Engine-->>API: Return structured data
    API-->>Client: JSON response with extracted data
```

Sources: [backend/server/main.py:11-16](), [backend/server/main.py:52-58]()

## Document Processing

The backend includes utilities for parsing different document types before extraction:

- PDF processing using `pdfminer-six`
- HTML processing with `beautifulsoup4` and `lxml`
- Plain text handling

The document processing pipeline handles:
1. File type detection
2. Text extraction appropriate to the file type
3. Preprocessing text for the extraction engine

Sources: [backend/pyproject.toml:21-25]()

## Dependencies and Technologies

The backend relies on several key technologies and libraries:

| Category | Dependencies |
|----------|-------------|
| Core Framework | FastAPI, Uvicorn, Starlette |
| LLM Integration | LangChain, LangServe, OpenAI, Anthropic, Fireworks, Groq |
| Database | PostgreSQL, Alembic, SQLAlchemy |
| Document Processing | pdfminer-six, BeautifulSoup4, lxml |
| Vector Storage | FAISS |
| API Utilities | Pydantic, Python-multipart, jsonschema |

Sources: [backend/pyproject.toml:9-31]()

## Configuration and Deployment

The backend can be configured through environment variables:

| Variable | Purpose |
|----------|---------|
| `CORS_ORIGINS` | Comma-separated list of allowed origins for CORS |
| `OPENAI_API_KEY` | API key for OpenAI integration |
| `ANTHROPIC_API_KEY` | API key for Anthropic integration |
| `FIREWORKS_API_KEY` | API key for Fireworks integration |
| `GROQ_API_KEY` | API key for Groq integration |
| `TOGETHER_API_KEY` | API key for Together AI integration |
| `DISABLE_GPT4` | Flag to disable GPT-4 models even if API key is present |

The system is designed to be deployed using Docker, with containers for the backend, frontend, and PostgreSQL database.

```mermaid
graph TB
    subgraph "LangChain Extract Deployment"
        Frontend["Frontend Container"]
        Backend["Backend Container"]
        Database["PostgreSQL Container"]
    end
    
    User["User"] -->|"HTTP Requests"| Frontend
    Frontend -->|"API Calls"| Backend
    Backend -->|"Data Storage"| Database
    
    subgraph "Backend Container Details"
        FastAPI["FastAPI Server"]
        Uvicorn["Uvicorn Server"]
        LangChain["LangChain Libraries"]
        LLMConnectors["LLM Provider Connectors"]
    end
    
    Backend --- FastAPI
    FastAPI --- Uvicorn
    FastAPI --- LangChain
    LangChain --- LLMConnectors
```

Sources: [backend/server/main.py:35-44](), [backend/server/models.py:10-67](), [backend/pyproject.toml:9-31]()

## Error Handling and Logging

The backend system implements error handling through FastAPI's exception handling mechanisms. Logging is configured to track important system events and potential issues:

```python
logger = logging.getLogger(__name__)
# Later in the code
logger.warning("No UI directory found, serving API only.")
```

Sources: [backend/server/main.py:18](), [backend/server/main.py:76]()

## Testing Infrastructure

The backend includes a comprehensive testing infrastructure with pytest fixtures and utilities. The test suite includes unit tests, integration tests, and tools like `GenericFakeChatModel` for mocking LLM responses during testing.

Sources: [backend/tests/unit_tests/fake/test_fake_chat_model.py:1-39]()

---

