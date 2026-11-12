<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nim-anywhere · page 3 Core Architecture · fetched 2026-10-26 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [code/chain_server/chain.py](code/chain_server/chain.py)
- [code/frontend/__init__.py](code/frontend/__init__.py)

</details>



## Purpose and Scope

This document describes the core architectural components and design patterns of NVIDIA NIM Anywhere, focusing on how the system orchestrates RAG (Retrieval-Augmented Generation) pipelines using NVIDIA NIMs and LangChain. This covers the overall system design, component relationships, and data flow patterns.

For detailed information about the RAG chain implementation specifics, see [RAG Chain Implementation](#3.1). For AI Workbench integration details, see [AI Workbench Integration](#3.2). For user interface architecture, see [User Interfaces](#4).

## System Overview

NVIDIA NIM Anywhere is architected as a multi-tier system running within the NVIDIA AI Workbench environment. The system follows a microservices pattern with clear separation between presentation, orchestration, and data layers.

### High-Level Architecture

```mermaid
graph TB
    subgraph "NVIDIA AI Workbench Container Environment"
        subgraph "Presentation Layer"
            ChatFrontend["Chat Frontend<br/>Gradio Application<br/>Port 7070"]
            ControlPanel["Control Panel<br/>Configuration UI<br/>Gradio Application"]
            TutorialApp["Tutorial Application<br/>Streamlit<br/>Port 8501"]
        end
        
        subgraph "Orchestration Layer"
            ChainServer["Chain Server<br/>FastAPI + LangChain<br/>Port 3030<br/>chain.py"]
        end
        
        subgraph "Data Layer"
            Redis["Redis<br/>RedisChatMessageHistory<br/>Port 6379"]
            Milvus["Milvus Vector Store<br/>langchain_milvus.Milvus<br/>Port 19530"]
        end
        
        subgraph "Development Tools"
            JupyterLab["JupyterLab<br/>Data Ingestion<br/>Port 8888"]
            VSCode["VS Code<br/>IDE Integration"]
        end
    end
    
    subgraph "External NVIDIA Services"
        LLM_NIM["LLM NIM<br/>ChatNVIDIA<br/>meta/llama3-8b-instruct"]
        EMB_NIM["Embedding NIM<br/>NVIDIAEmbeddings<br/>nv-embedqa-e5-v5"]
        RERANK_NIM["Reranker NIM<br/>NVIDIARerank<br/>nv-rerankqa-mistral-4b-v3"]
    end
    
    ChatFrontend --> ChainServer
    ControlPanel --> ChainServer
    TutorialApp --> ChainServer
    
    ChainServer --> Redis
    ChainServer --> Milvus
    ChainServer --> LLM_NIM
    ChainServer --> EMB_NIM
    ChainServer --> RERANK_NIM
    
    JupyterLab --> Milvus
```

The architecture separates concerns across distinct layers, with the `ChainServer` serving as the central orchestration point for all RAG operations.

**Sources:** [README.md:1-993](), [code/chain_server/chain.py:1-138]()

## Core Components

### Chain Server (`chain.py`)

The `ChainServer` implements the core RAG logic using LangChain components. It exposes a FastAPI-based REST interface and orchestrates the complete RAG pipeline.

```mermaid
graph TB
    subgraph "Chain Server Components"
        ChainInputs["ChainInputs<br/>BaseModel<br/>question, use_kb, use_reranker"]
        
        subgraph "LangChain Pipeline"
            QuestionParsing["question_parsing<br/>@chain function<br/>Condenses question with history"]
            RetrieveContext["retrieve_context<br/>@chain function<br/>Document retrieval"]
            MyChain["my_chain<br/>RunnableWithMessageHistory<br/>Main processing pipeline"]
        end
        
        subgraph "External Model Integrations"
            ChatNVIDIA["ChatNVIDIA<br/>llm variable<br/>LLM inference"]
            NVIDIAEmbeddings["NVIDIAEmbeddings<br/>embedding_model<br/>Text embeddings"]
            NVIDIARerank["NVIDIARerank<br/>reranker<br/>Document reranking"]
        end
        
        subgraph "Storage Components"
            MilvusStore["Milvus<br/>vector_store<br/>Vector database"]
            RedisHistory["RedisChatMessageHistory<br/>Conversation storage"]
        end
    end
    
    ChainInputs --> QuestionParsing
    ChainInputs --> RetrieveContext
    QuestionParsing --> MyChain
    RetrieveContext --> MyChain
    
    MyChain --> ChatNVIDIA
    RetrieveContext --> NVIDIAEmbeddings
    RetrieveContext --> NVIDIARerank
    RetrieveContext --> MilvusStore
    MyChain --> RedisHistory
```

**Sources:** [code/chain_server/chain.py:17-138]()

### Frontend Applications

The system provides three distinct user interfaces, each implemented as separate Gradio applications:

| Component | Technology | Purpose | Port |
|-----------|------------|---------|------|
| Chat Frontend | Gradio | Primary RAG interaction interface | 7070 |
| Control Panel | Gradio | System configuration and KB management | Variable |
| Tutorial App | Streamlit | Interactive learning environment | 8501 |

**Sources:** [README.md:43-511]()

### Data Management Components

#### Vector Storage (`Milvus`)
The system uses `langchain_milvus.Milvus` as the vector store, configured with the embedding model and collection settings:

```python
vector_store = Milvus(
    embedding_function=embedding_model,
    connection_args={"uri": app_config.milvus.url},
    collection_name=app_config.milvus.collection_name,
    auto_id=True,
)
```

#### Conversation History (`RedisChatMessageHistory`)
Chat sessions are persisted using Redis through LangChain's `RedisChatMessageHistory`:

```python
RedisChatMessageHistory(session_id, url=str(app_config.redis_dsn))
```

**Sources:** [code/chain_server/chain.py:41-46](), [code/chain_server/chain.py:130]()

## RAG Processing Flow

The system implements a sophisticated RAG pipeline with optional reranking and conversation history management.

### Request Processing Pipeline

```mermaid
sequenceDiagram
    participant Client as "Client Application"
    participant ChainServer as "Chain Server<br/>my_chain"
    participant QuestionParsing as "question_parsing<br/>@chain"
    participant RetrieveContext as "retrieve_context<br/>@chain"
    participant Redis as "RedisChatMessageHistory"
    participant Milvus as "Milvus vector_store"
    participant LLM as "ChatNVIDIA llm"
    participant Embeddings as "NVIDIAEmbeddings"
    participant Reranker as "NVIDIARerank reranker"
    
    Client->>ChainServer: "POST /invoke<br/>{question, use_kb, use_reranker, session_id}"
    
    ChainServer->>Redis: "Load conversation history"
    Redis-->>ChainServer: "Historical messages"
    
    par Question Processing
        ChainServer->>QuestionParsing: "Condense with history"
        QuestionParsing->>LLM: "CONDENSE_QUESTION_TEMPLATE"
        LLM-->>QuestionParsing: "Condensed question"
        QuestionParsing-->>ChainServer: "Processed question"
    and Context Retrieval
        alt use_kb == true
            ChainServer->>RetrieveContext: "Retrieve documents"
            RetrieveContext->>Embeddings: "Generate query embedding"
            Embeddings-->>RetrieveContext: "Query vector"
            RetrieveContext->>Milvus: "Vector similarity search"
            Milvus-->>RetrieveContext: "Retrieved documents"
            
            alt use_reranker == true
                RetrieveContext->>Reranker: "Rerank documents"
                Reranker-->>RetrieveContext: "Ranked documents"
            end
            
            RetrieveContext-->>ChainServer: "format_docs(documents)"
        else
            RetrieveContext-->>ChainServer: "Empty context"
        end
    end
    
    ChainServer->>LLM: "CHAT_PROMPT with context + question"
    LLM-->>ChainServer: "Generated response"
    
    ChainServer->>Redis: "Store conversation update"
    ChainServer-->>Client: "Streamed response"
```

**Sources:** [code/chain_server/chain.py:76-113](), [code/chain_server/chain.py:128-134]()

## Configuration Management

The system implements a hierarchical configuration system supporting multiple sources and environment variable overrides.

### Configuration Hierarchy

```mermaid
graph TD
    EnvVars["Environment Variables<br/>APP_* prefixed<br/>Highest priority"]
    CustomConfig["Custom Config File<br/>APP_CONFIG env var<br/>Medium priority"]
    DefaultConfigs["Default Config Locations<br/>./config.yaml, ~/app.yaml, /etc/app.yaml<br/>Lower priority"]
    
    subgraph "Configuration Schema"
        NvidiaAPIKey["nvidia_api_key<br/>NGC authentication"]
        RedisConfig["redis_dsn<br/>Redis connection"]
        LLMConfig["llm_model<br/>{name, url}"]
        EmbeddingConfig["embedding_model<br/>{name, url}"]
        RerankingConfig["reranking_model<br/>{name, url}"]
        MilvusConfig["milvus<br/>{url, collection_name}"]
    end
    
    EnvVars --> NvidiaAPIKey
    CustomConfig --> LLMConfig
    DefaultConfigs --> EmbeddingConfig
    
    NvidiaAPIKey --> ChainServerConfig["Chain Server<br/>app_config"]
    RedisConfig --> ChainServerConfig
    LLMConfig --> ChainServerConfig
    EmbeddingConfig --> ChainServerConfig
    RerankingConfig --> ChainServerConfig
    MilvusConfig --> ChainServerConfig
```

The configuration is loaded through the `app_config` module and used to initialize all NVIDIA AI service connections.

**Sources:** [README.md:560-685](), [code/chain_server/chain.py:32]()

## Service Integration

### NVIDIA AI Services Integration

The system integrates with three categories of NVIDIA AI services through standardized interfaces:

| Service Type | Class | Configuration | Purpose |
|--------------|-------|---------------|---------|
| LLM | `ChatNVIDIA` | `app_config.llm_model` | Text generation and reasoning |
| Embeddings | `NVIDIAEmbeddings` | `app_config.embedding_model` | Text vectorization for retrieval |
| Reranking | `NVIDIARerank` | `app_config.reranking_model` | Document relevance scoring |

### Retrieval Strategy Implementation

The system implements a flexible retrieval strategy with optional reranking:

```python
# Base retriever
retriever = vector_store.as_retriever()

# Enhanced retriever with reranking
reranking_retriever = ContextualCompressionRetriever(
    base_compressor=reranker, 
    base_retriever=retriever
)
```

The `retrieve_context` function dynamically selects between retrieval strategies based on the `use_reranker` parameter.

**Sources:** [code/chain_server/chain.py:35-55](), [code/chain_server/chain.py:76-89]()

### AI Workbench Orchestration

NVIDIA AI Workbench serves as the container orchestration platform, managing:

- **Application Lifecycle**: Automatic startup/shutdown of frontend applications
- **Service Dependencies**: Docker Compose coordination for Redis and Milvus
- **Environment Management**: Configuration injection and secret management
- **Development Integration**: JupyterLab and VS Code integration

The system is designed to scale from development environments to production deployments while maintaining consistent configuration and service integration patterns.

**Sources:** [README.md:127-512]()

---

