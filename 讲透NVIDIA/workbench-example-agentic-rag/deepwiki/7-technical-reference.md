<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/workbench-example-agentic-rag · page 7 Technical Reference · fetched 2026-10-26 -->

# Technical Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.project/configpacks](.project/configpacks)
- [apt.txt](apt.txt)

</details>



## Purpose and Scope

This technical reference provides comprehensive documentation of the system's implementation details, configuration structures, and technical specifications. It serves as a reference for developers and system administrators who need to understand the technical architecture, troubleshoot issues, or maintain the Agentic RAG system.

For user-focused guides and getting started instructions, see [Getting Started](#2). For development and customization guidance, see [Development Guide](#6). For detailed configuration specifications, see [Configuration Reference](#7.1).

## System Implementation Overview

The Agentic RAG system is implemented as a containerized Python application built on NVIDIA AI Workbench. The system combines multiple components through a graph-based workflow orchestration layer.

### Core Technical Architecture

```mermaid
graph TB
    subgraph "Container_Environment" ["Container Environment (nvcr.io/pytorch)"]
        subgraph "Application_Layer" ["Application Layer"]
            gradio_app["gradio_app.py"]
            chat_interface["chat_with_pdf"]
            workflow_graph["agentic_rag_workflow"]
        end
        
        subgraph "Orchestration_Layer" ["Orchestration Layer"]
            langgraph_runtime["LangGraph Runtime"]
            langchain_core["LangChain Core"]
            agent_nodes["Agent Nodes"]
        end
        
        subgraph "Data_Layer" ["Data Layer"]
            chromadb_client["ChromaDB Client"]
            vector_collections["Vector Collections"]
            document_store["Document Store"]
        end
        
        subgraph "Model_Layer" ["Model Integration Layer"]
            nvidia_endpoints["NVIDIA API Endpoints"]
            openai_compatible["OpenAI Compatible APIs"]
            local_inference["Local Inference Engines"]
        end
    end
    
    subgraph "External_Dependencies" ["External Dependencies"]
        tavily_api["Tavily Search API"]
        nvidia_ngc["NVIDIA NGC Registry"]
        gpu_drivers["CUDA/GPU Drivers"]
    end
    
    gradio_app --> chat_interface
    chat_interface --> workflow_graph
    workflow_graph --> langgraph_runtime
    langgraph_runtime --> agent_nodes
    agent_nodes --> chromadb_client
    agent_nodes --> nvidia_endpoints
    agent_nodes --> tavily_api
    chromadb_client --> vector_collections
    vector_collections --> document_store
    
    nvidia_endpoints --> nvidia_ngc
    local_inference --> gpu_drivers
```

**Sources:** [.project/configpacks:1-14](), [apt.txt:1-7]()

### Technical Component Mapping

```mermaid
graph LR
    subgraph "Code_Entities" ["Code Entities"]
        chat_pdf["chat_with_pdf()"]
        create_agent["create_agentic_rag_agent()"]
        router_node["router_node()"]
        retrieval_grader["retrieval_grader()"]
        generate_node["generate()"]
        grade_generation["grade_generation()"]
        web_search["web_search_node()"]
        chroma_client["ChromaClient"]
        embedding_function["NVIDIAEmbeddings"]
    end
    
    subgraph "System_Functions" ["System Functions"]
        query_routing["Query Routing Logic"]
        document_retrieval["Document Retrieval"]
        answer_generation["Answer Generation"]
        hallucination_detection["Hallucination Detection"]
        web_search_integration["Web Search Integration"]
        vector_storage["Vector Storage Management"]
        embedding_processing["Embedding Processing"]
    end
    
    chat_pdf --> query_routing
    create_agent --> query_routing
    router_node --> query_routing
    retrieval_grader --> document_retrieval
    generate_node --> answer_generation
    grade_generation --> hallucination_detection
    web_search --> web_search_integration
    chroma_client --> vector_storage
    embedding_function --> embedding_processing
```

**Sources:** [.project/configpacks:1-14](), [apt.txt:1-7]()

## Container Configuration Structure

The system uses NVIDIA AI Workbench's configpack system for container configuration management. The configuration is modular and declarative.

### Configpack Architecture

| Configpack | Purpose | Technical Function |
|------------|---------|-------------------|
| `*defaults.ContainerUser` | User configuration | Sets container user permissions and environment |
| `*bash.PreBuild` | Pre-build scripts | Executes system preparation commands |
| `*defaults.CA` | Certificate authority | Configures SSL/TLS certificate handling |
| `*cuda.CUDA` | GPU acceleration | Enables CUDA runtime and GPU access |
| `*defaults.EnvVars` | Environment variables | Sets runtime environment configuration |
| `*apt.PackageManager` | System packages | Installs system-level dependencies |
| `*python.PipPackageManager` | Python packages | Manages Python package dependencies |
| `*jupyterlab.JupyterLab` | Jupyter environment | Configures JupyterLab development environment |
| `*vs_code.VSCode` | VS Code integration | Sets up VS Code server for development |
| `*tensorboard.Tensorboard` | Monitoring | Enables TensorBoard for metrics visualization |

**Sources:** [.project/configpacks:1-14]()

## System Dependencies

### Critical System Packages

The system requires specific system-level packages for document processing and OCR capabilities:

| Package | Purpose | Technical Requirement |
|---------|---------|----------------------|
| `poppler-utils` | PDF processing utilities | Required for PDF text extraction and conversion |
| `python3-pil` | Python Imaging Library | Image processing for document analysis |
| `tesseract-ocr` | OCR engine | Text extraction from images and scanned documents |
| `libtesseract-dev` | Tesseract development headers | Required for Python bindings compilation |
| `tesseract-ocr-eng` | English language model | English text recognition capabilities |
| `tesseract-ocr-script-latn` | Latin script model | Latin alphabet character recognition |

**Sources:** [apt.txt:1-7]()

### Package Installation Flow

```mermaid
sequenceDiagram
    participant Container as "Container Build"
    participant APT as "APT Package Manager"
    participant Tesseract as "Tesseract OCR"
    participant Python as "Python Environment"
    
    Container->>APT: "Install system packages"
    APT->>APT: "poppler-utils"
    APT->>APT: "python3-pil"
    APT->>Tesseract: "tesseract-ocr"
    APT->>Tesseract: "libtesseract-dev"
    APT->>Tesseract: "tesseract-ocr-eng"
    APT->>Tesseract: "tesseract-ocr-script-latn"
    Tesseract-->>Python: "OCR capabilities available"
    Python-->>Container: "Document processing ready"
```

**Sources:** [apt.txt:1-7](), [.project/configpacks:8]()

## Runtime Environment Configuration

### Service Port Allocation

The system exposes multiple services on different ports within the container environment:

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Gradio Chat UI | 8080 | HTTP | Primary user interface for chat interactions |
| JupyterLab | 8888 | HTTP | Development and experimentation environment |
| TensorBoard | 6006 | HTTP | Metrics and monitoring dashboard |

### Environment Variable Structure

The system uses environment variables for configuration management, particularly for API keys and service endpoints. Critical environment variables include:

- `NVIDIA_API_KEY`: Authentication for NVIDIA AI endpoints
- `TAVILY_API_KEY`: Authentication for Tavily web search API
- `CHROMA_HOST`: ChromaDB service host configuration
- `CHROMA_PORT`: ChromaDB service port configuration

**Sources:** [.project/configpacks:5]()

## Error Handling and System Utilities

### Configuration Validation

The system implements configuration validation through the configpack system, ensuring all required dependencies and configurations are properly set before runtime.

### Service Health Monitoring

```mermaid
graph TD
    subgraph "Health_Check_Flow" ["Health Check Flow"]
        container_start["Container Start"]
        configpack_validation["Configpack Validation"]
        dependency_check["Dependency Check"]
        service_initialization["Service Initialization"]
        health_status["Health Status"]
    end
    
    container_start --> configpack_validation
    configpack_validation --> dependency_check
    dependency_check --> service_initialization
    service_initialization --> health_status
    
    subgraph "Validation_Points" ["Validation Points"]
        cuda_available["CUDA Available"]
        packages_installed["System Packages"]
        python_deps["Python Dependencies"]
        api_keys["API Key Configuration"]
        ports_available["Port Availability"]
    end
    
    dependency_check --> cuda_available
    dependency_check --> packages_installed
    dependency_check --> python_deps
    dependency_check --> api_keys
    service_initialization --> ports_available
```

**Sources:** [.project/configpacks:1-14]()

## Technical Specifications

### Container Base Image

- **Base Image**: `nvcr.io/nvidia/pytorch`
- **CUDA Version**: 12.2
- **Python Version**: 3.x (as provided by PyTorch container)
- **GPU Support**: NVIDIA GPU with CUDA compatibility

### Memory and Resource Requirements

- **Minimum RAM**: 8GB (recommended 16GB for optimal performance)
- **GPU Memory**: Minimum 4GB VRAM for local inference
- **Storage**: Minimum 10GB for system and dependencies
- **CPU**: Multi-core processor recommended for document processing

**Sources:** [.project/configpacks:4]()

## Integration Specifications

For detailed configuration file documentation, see [Configuration Reference](#7.1). For complete dependency specifications and version requirements, see [System Dependencies](#7.2). For data storage implementation details, see [Data Storage and Management](#7.3).

---

