<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/workbench-example-agentic-rag · page 8 Notebooks and Examples · fetched 2026-10-26 -->

# Notebooks and Examples

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [code/langgraph_rag_agent_llama3_nvidia_nim.ipynb](code/langgraph_rag_agent_llama3_nvidia_nim.ipynb)

</details>



This document covers the interactive examples and Jupyter notebooks provided within the Agentic RAG system. These materials demonstrate key system capabilities, provide hands-on tutorials for customization, and serve as starting points for development workflows.

The notebooks and examples are designed to complement the three usage modes of the system. For basic setup instructions, see [Getting Started](#2). For detailed component documentation, see [Core Components](#4). For customization guidance, see [Code Customization](#6.1).

## Jupyter Lab Environment

The system includes a fully configured JupyterLab environment accessible at port 8888 within the NVIDIA AI Workbench container. This environment provides an interactive development interface for exploring system components, testing modifications, and running example workflows.

```mermaid
graph TB
    subgraph "NVIDIA AI Workbench Container"
        JupyterLab["JupyterLab Server :8888"]
        
        subgraph "Notebook Categories"
            GettingStarted["Getting Started<br/>Basic Usage Examples"]
            DataIngestion["Data Ingestion<br/>Document Loading & Processing"]
            ModelConfig["Model Configuration<br/>LLM Provider Setup"]
            CustomWorkflows["Custom Workflows<br/>Agent Modification Examples"]
            Troubleshooting["Troubleshooting<br/>Debug & Diagnostics"]
        end
        
        subgraph "System Integration"
            ChatUI["Chat UI :8080"]
            ChromaDB["ChromaDB Vector Store"]
            AgenticWorkflow["LangGraph Workflow"]
        end
    end
    
    subgraph "External Resources"
        NVIDIAEndpoints["NVIDIA API Endpoints"]
        TavilyAPI["Tavily Search API"]
        ProjectData["/project/data<br/>Persistent Storage"]
    end
    
    JupyterLab --> GettingStarted
    JupyterLab --> DataIngestion
    JupyterLab --> ModelConfig
    JupyterLab --> CustomWorkflows
    JupyterLab --> Troubleshooting
    
    DataIngestion --> ChromaDB
    ModelConfig --> NVIDIAEndpoints
    CustomWorkflows --> AgenticWorkflow
    GettingStarted --> ChatUI
    
    ChromaDB --> ProjectData
    AgenticWorkflow --> TavilyAPI
```

The JupyterLab environment provides direct access to all system components and allows for real-time experimentation with the agentic workflow, model configurations, and data processing pipelines.

**Sources:** System architecture diagrams, container port configuration

## Example Categories

### Data Ingestion Examples

Examples demonstrating document loading, processing, and vector database population workflows. These notebooks show how to work with different data sources and file formats supported by the system.

```mermaid
graph LR
    subgraph "Data Sources"
        WebURLs["Web URLs<br/>WebBaseLoader"]
        PDFFiles["PDF Documents<br/>UnstructuredPDFLoader"]
        TextFiles["Text Files<br/>TextLoader"]
        CSVFiles["CSV Data<br/>CSVLoader"]
    end
    
    subgraph "Processing Pipeline"
        TextSplitter["RecursiveCharacterTextSplitter<br/>chunk_size=250"]
        NVEmbeddings["NVIDIA Embeddings<br/>NV-Embed-QA"]
        ChromaCollection["ChromaDB Collection<br/>Persistent Storage"]
    end
    
    subgraph "Example Notebooks"
        BasicIngestion["basic_data_ingestion.ipynb<br/>Simple Document Loading"]
        BatchProcessing["batch_processing.ipynb<br/>Multiple File Handling"]
        CustomLoaders["custom_loaders.ipynb<br/>Advanced Data Sources"]
    end
    
    WebURLs --> TextSplitter
    PDFFiles --> TextSplitter
    TextFiles --> TextSplitter
    CSVFiles --> TextSplitter
    
    TextSplitter --> NVEmbeddings
    NVEmbeddings --> ChromaCollection
    
    BasicIngestion --> TextSplitter
    BatchProcessing --> TextSplitter
    CustomLoaders --> TextSplitter
```

These examples demonstrate the document processing pipeline from raw data sources through embedding generation and vector storage.

**Sources:** Data ingestion architecture, document processing pipeline

### Model Configuration Examples

Notebooks showing how to configure different LLM providers, adjust model parameters, and switch between cloud and self-hosted endpoints.

| Example Type | Purpose | Key Components |
|--------------|---------|----------------|
| NVIDIA API Setup | Configure cloud endpoints | `NVIDIA_API_KEY`, model selection |
| Ollama Integration | Local model deployment | Model pulling, endpoint configuration |
| Custom Prompts | Modify system behavior | Prompt templates, persona configuration |
| Parameter Tuning | Optimize model performance | Temperature, top-p, max tokens |

### Agentic Workflow Customization

Interactive examples for modifying the LangGraph-based agentic workflow, including routing logic, grading functions, and iteration controls.

```mermaid
flowchart TD
    subgraph "Workflow Components"
        Router["router_function<br/>Query Classification"]
        RetrieverGrader["retrieval_grader<br/>Document Relevance"]
        Generator["generate_function<br/>Answer Generation"]
        HallGrader["hallucination_grader<br/>Fact Verification"]
        AnswerGrader["answer_grader<br/>Quality Assessment"]
    end
    
    subgraph "Customization Examples"
        RouterCustom["router_customization.ipynb<br/>Modify Query Routing"]
        GraderTuning["grader_tuning.ipynb<br/>Adjust Evaluation Criteria"]
        WorkflowMod["workflow_modification.ipynb<br/>Add New Agents"]
        IterationControl["iteration_control.ipynb<br/>Recursion Management"]
    end
    
    RouterCustom --> Router
    GraderTuning --> RetrieverGrader
    GraderTuning --> HallGrader
    GraderTuning --> AnswerGrader
    WorkflowMod --> Generator
    IterationControl --> Router
    
    Router --> RetrieverGrader
    RetrieverGrader --> Generator
    Generator --> HallGrader
    HallGrader --> AnswerGrader
```

These notebooks provide hands-on experience with modifying the core agentic logic and understanding how different components interact within the LangGraph framework.

**Sources:** Agentic RAG workflow architecture, LangGraph integration

## Mode-Specific Examples

### Easy Mode Examples

Simple notebooks that demonstrate basic usage without requiring code modifications. These focus on configuration changes and basic customization through parameters.

- **Quick Start Tutorial**: Step-by-step walkthrough of adding documents and asking questions
- **API Key Configuration**: Setting up NVIDIA and Tavily API credentials
- **Basic Document Upload**: Using the chat interface for document ingestion

### Intermediate Mode Examples

Development-focused notebooks for users who want to modify system behavior through code changes.

- **Prompt Engineering**: Customizing system prompts and response templates
- **UI Modifications**: Adjusting the Gradio interface components
- **Model Comparison**: Testing different LLM providers and configurations
- **Custom Grading Functions**: Implementing domain-specific evaluation criteria

### Advanced Mode Examples

Infrastructure and deployment examples for self-hosted setups.

- **Ollama Deployment**: Setting up local model serving with Ollama
- **NVIDIA NIM Integration**: Configuring self-hosted NVIDIA Inference Microservices
- **GPU Optimization**: Performance tuning for specific hardware configurations
- **Container Customization**: Modifying the Docker environment for specific requirements

## Development Workflow Integration

The notebooks integrate with the broader development workflow, providing testing environments for modifications before deploying changes to the main chat interface.

```mermaid
graph TB
    subgraph "Development Cycle"
        Explore["Explore Notebooks<br/>Understand Components"]
        Experiment["Experiment<br/>Test Modifications"]
        Validate["Validate Changes<br/>Check Functionality"]
        Deploy["Deploy to Chat UI<br/>Production Usage"]
    end
    
    subgraph "Notebook Environment"
        JupyterLab["JupyterLab Interface"]
        InteractiveKernel["Python Kernel<br/>Live Code Execution"]
        SystemAccess["Direct System Access<br/>Component Testing"]
    end
    
    subgraph "Chat Application"
        GradioUI["Gradio Chat Interface"]
        AgenticGraph["LangGraph Workflow"]
        VectorDB["ChromaDB Storage"]
    end
    
    Explore --> JupyterLab
    Experiment --> InteractiveKernel
    Validate --> SystemAccess
    Deploy --> GradioUI
    
    SystemAccess --> AgenticGraph
    SystemAccess --> VectorDB
    InteractiveKernel --> AgenticGraph
```

This workflow allows developers to iterate quickly on modifications while maintaining system stability.

**Sources:** Development workflow architecture, JupyterLab integration

## Troubleshooting and Diagnostics

Specialized notebooks for system diagnostics, performance analysis, and common issue resolution.

| Diagnostic Area | Notebook Purpose | Key Metrics |
|-----------------|------------------|-------------|
| Vector Database | ChromaDB health checks | Collection size, embedding quality |
| LLM Connectivity | API endpoint testing | Response times, error rates |
| Agentic Flow | Workflow execution analysis | Routing decisions, iteration counts |
| Memory Usage | Resource monitoring | Container memory, GPU utilization |

These diagnostic tools help identify and resolve common issues encountered during system operation and customization.

**Sources:** System monitoring requirements, container resource management