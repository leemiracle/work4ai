<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/workbench-example-agentic-rag · page 3 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.project/spec.yaml](.project/spec.yaml)
- [README.md](README.md)
- [requirements.txt](requirements.txt)

</details>



## Purpose and Scope

This document provides a comprehensive overview of the Agentic RAG system architecture, including the core components, technology stack, deployment model, and how the various subsystems interact. The system combines retrieval-augmented generation (RAG) with agentic workflows to provide accurate responses while controlling hallucinations through iterative evaluation and web search augmentation.

For detailed information about individual components, see [Core Components](#4). For deployment instructions, see [Getting Started](#2) and [Deployment and Infrastructure](#5). For technical configuration details, see [Technical Reference](#7).

## High-Level System Overview

The Agentic RAG system operates within an NVIDIA AI Workbench container environment, providing multiple interfaces for user interaction and a sophisticated backend processing pipeline.

### System Components Architecture

```mermaid
graph TB
    subgraph "NVIDIA AI Workbench Container"
        subgraph "User Interfaces"
            ChatUI["chatui module<br/>Gradio App :8080"]
            JupyterLab["jupyterlab :8888"]
            TensorBoard["tensorboard :6006"]
        end
        
        subgraph "Agentic Processing Pipeline"
            Router["query_router"]
            RetrieverGrader["retrieval_grader"]
            Generator["generate_answer"]
            HallucinationGrader["hallucination_grader"]
            AnswerGrader["answer_grader"]
            WebSearch["web_search_tool"]
        end
        
        subgraph "Data Layer"
            ChromaDB["ChromaDB Collection<br/>vectorstore"]
            ProjectData["/project/data<br/>Persistent Storage"]
        end
        
        subgraph "LLM Integration"
            NVIDIAEndpoints["langchain_nvidia_ai_endpoints<br/>ChatNVIDIA"]
            Embeddings["NVIDIAEmbeddings<br/>NV-Embed-QA"]
        end
    end
    
    subgraph "External Services"
        TavilyAPI["tavily_python<br/>TavilySearchAPIWrapper"]
        NVIDIACloud["NVIDIA API Endpoints<br/>build.nvidia.com"]
    end
    
    %% User interaction flows
    ChatUI --> Router
    Router --> RetrieverGrader
    Router --> WebSearch
    RetrieverGrader --> ChromaDB
    RetrieverGrader --> Generator
    Generator --> HallucinationGrader
    HallucinationGrader --> AnswerGrader
    WebSearch --> TavilyAPI
    
    %% Data flows
    ChromaDB --> ProjectData
    Generator --> NVIDIAEndpoints
    Embeddings --> NVIDIAEndpoints
    NVIDIAEndpoints --> NVIDIACloud
    TavilyAPI -.->|"Web Results"| Generator
    
    %% Configuration
    ChatUI -.->|"PROXY_PREFIX"| Router
```

**Sources:** [.project/spec.yaml:34-49](), [README.md:3-6](), [requirements.txt:2-8]()

## Technology Stack and Integration Layer

The system leverages a modern Python-based technology stack with specialized AI/ML libraries for document processing, vector storage, and language model integration.

### Technology Integration Architecture

```mermaid
graph TB
    subgraph "Application Layer"
        GradioApp["gradio==4.15.0<br/>Web Interface"]
        JupyterApp["jupyterlab>3.0<br/>Development Environment"]
    end
    
    subgraph "Orchestration and Agent Layer"
        LangGraph["langgraph==0.2.67<br/>Agent Workflow Engine"]
        LangChain["langchain==0.3.15<br/>LLM Abstraction Layer"]
        LangChainCommunity["langchain-community==0.3.15<br/>Tool Integrations"]
    end
    
    subgraph "LLM Provider Integration"
        NVIDIAEndpoints["langchain-nvidia-ai-endpoints==0.3.7<br/>ChatNVIDIA, NVIDIAEmbeddings"]
        OpenAIEndpoints["langchain-openai==0.3.2<br/>ChatOpenAI"]
    end
    
    subgraph "Document Processing Pipeline"
        Unstructured["unstructured[pdf]==0.16.17<br/>Document Loaders"]
        NLTK["nltk==3.8.1<br/>Text Processing"]
        BeautifulSoup["beautifulsoup4==4.12.2<br/>HTML Parsing"]
        LXML["lxml==5.2.2<br/>XML Processing"]
    end
    
    subgraph "Vector Database Layer"
        ChromaIntegration["langchain-chroma==0.2.0<br/>Vector Store Interface"]
        ChromaDB["ChromaDB<br/>Vector Database"]
    end
    
    subgraph "External API Integration"
        TavilySearch["tavily-python==0.3.5<br/>TavilySearchAPIWrapper"]
        FastAPI["fastapi==0.111.0<br/>API Framework"]
        Requests["requests<br/>HTTP Client"]
    end
    
    subgraph "Infrastructure Layer"
        ContainerBase["nvidia/ai-workbench/pytorch:1.0.2<br/>CUDA 12.2, Ubuntu 22.04"]
        ONNXRuntime["onnxruntime==1.18.0<br/>Model Inference"]
    end
    
    %% Integration flows
    GradioApp --> LangGraph
    LangGraph --> LangChain
    LangChain --> NVIDIAEndpoints
    LangChain --> OpenAIEndpoints
    LangChain --> ChromaIntegration
    ChromaIntegration --> ChromaDB
    
    LangChain --> TavilySearch
    Unstructured --> ChromaIntegration
    NLTK --> ChromaIntegration
    BeautifulSoup --> Unstructured
    
    ONNXRuntime --> ContainerBase
    GradioApp --> FastAPI
```

**Sources:** [requirements.txt:1-20](), [.project/spec.yaml:22-28](), [.project/spec.yaml:82-89]()

## Deployment Architecture

The system is deployed as a containerized application within NVIDIA AI Workbench, providing three distinct web applications and supporting multiple deployment modes.

### Container and Application Deployment

```mermaid
graph TB
    subgraph "Host Environment"
        DockerEngine["Docker Engine"]
        NVIDIAWorkbench["NVIDIA AI Workbench"]
    end
    
    subgraph "Container: project-agentic-rag"
        subgraph "Application Services"
            ChatApp["chat app<br/>python3 -m chatui<br/>Port 8080"]
            JupyterService["jupyterlab<br/>jupyter lab --allow-root<br/>Port 8888"]  
            TensorBoardService["tensorboard<br/>tensorboard --logdir<br/>Port 6006"]
        end
        
        subgraph "File System Mounts"
            ProjectMount["/project/<br/>rw mount"]
            TensorBoardLogs["/data/tensorboard/logs/<br/>volume mount"]
        end
        
        subgraph "Environment Configuration"
            APIKeys["NVIDIA_API_KEY<br/>TAVILY_API_KEY"]
            ProxyPrefix["PROXY_PREFIX"]
        end
        
        subgraph "Base Image Components"
            PyTorch["PyTorch 2.1"]
            CUDA["CUDA 12.2"]
            Ubuntu["Ubuntu 22.04"]
            SystemPackages["curl, git, git-lfs, vim"]
        end
    end
    
    subgraph "Storage Backend"
        GitStorage["Git Repository<br/>code/"]
        GitLFS["Git LFS<br/>models/, data/"]
        VolumeStorage["Docker Volume<br/>tensorboard-logs-volume"]
    end
    
    %% Deployment relationships
    NVIDIAWorkbench --> DockerEngine
    DockerEngine --> ChatApp
    DockerEngine --> JupyterService
    DockerEngine --> TensorBoardService
    
    ProjectMount --> GitStorage
    ProjectMount --> GitLFS
    TensorBoardLogs --> VolumeStorage
    
    APIKeys -.->|"Required for"| ChatApp
    ProxyPrefix -.->|"URL routing"| ChatApp
    
    ChatApp --> PyTorch
    PyTorch --> CUDA
    CUDA --> Ubuntu
```

**Sources:** [.project/spec.yaml:34-82](), [.project/spec.yaml:126-139](), [.project/spec.yaml:11-19]()

## Agentic Workflow Processing Architecture

The core agentic processing pipeline implements a graph-based workflow that routes queries, evaluates responses, and iterates for improved accuracy.

### Agent Workflow Graph

```mermaid
graph TD
    QueryInput["User Query Input"]
    
    QueryInput --> QueryRouter["query_router<br/>Route decision"]
    
    QueryRouter -->|"vectorstore"| VectorRetrieval["retrieve_documents<br/>ChromaDB query"]
    QueryRouter -->|"websearch"| WebSearchNode["web_search_tool<br/>TavilySearchAPIWrapper"]
    
    VectorRetrieval --> RetrievalGrader["retrieval_grader<br/>Document relevance check"]
    WebSearchNode --> WebSearchGrader["web_search_grader<br/>Search result relevance"]
    
    RetrievalGrader -->|"relevant"| GenerateAnswer["generate_answer<br/>ChatNVIDIA response"]
    RetrievalGrader -->|"not_relevant"| WebSearchNode
    WebSearchGrader -->|"relevant"| GenerateAnswer
    WebSearchGrader -->|"not_relevant"| GenerateAnswer
    
    GenerateAnswer --> HallucinationGrader["hallucination_grader<br/>Fact-checking against context"]
    
    HallucinationGrader -->|"grounded"| AnswerGrader["answer_grader<br/>Answer quality assessment"]
    HallucinationGrader -->|"hallucination"| GenerateAnswer
    
    AnswerGrader -->|"useful"| FinalAnswer["Final Response"]
    AnswerGrader -->|"not_useful"| IterationCheck["Check recursion_limit"]
    
    IterationCheck -->|"under_limit"| QueryRouter
    IterationCheck -->|"limit_exceeded"| FinalAnswer
    
    %% State management
    QueryRouter -.->|"update"| GraphState["GraphState<br/>question, generation, documents"]
    RetrievalGrader -.->|"update"| GraphState
    GenerateAnswer -.->|"update"| GraphState
    HallucinationGrader -.->|"update"| GraphState
    AnswerGrader -.->|"update"| GraphState
```

**Sources:** [README.md:3-6](), [README.md:74]()

## API and Environment Configuration

The system requires specific environment variables and API keys for operation, with support for multiple LLM providers and external services.

| Component | Configuration | Purpose |
|-----------|---------------|---------|
| `NVIDIA_API_KEY` | Required secret | Access to NVIDIA AI endpoints and embedding models |
| `TAVILY_API_KEY` | Required secret | Web search functionality via Tavily API |
| `PROXY_PREFIX` | Runtime variable | URL path prefix for containerized deployment |
| `ChatNVIDIA` | LLM provider | Primary language model for generation tasks |
| `NVIDIAEmbeddings` | Embedding model | Document vectorization using NV-Embed-QA |
| `TavilySearchAPIWrapper` | Search provider | External web search integration |

**Sources:** [.project/spec.yaml:126-130](), [README.md:32-34](), [requirements.txt:2](), [requirements.txt:8]()

---

