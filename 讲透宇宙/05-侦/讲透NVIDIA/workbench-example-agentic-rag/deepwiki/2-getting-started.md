<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/workbench-example-agentic-rag · page 2 Getting Started · fetched 2026-10-26 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This document provides a comprehensive guide to setting up and using the Agentic RAG system based on your technical requirements and expertise level. It covers three distinct usage modes, from immediate deployment to full infrastructure customization.

For detailed information about the system architecture and components, see [System Architecture](#3). For development and customization guidance, see [Development Guide](#6).

## Purpose and Scope

The Getting Started guide covers three primary usage modes:

- **Easy Mode**: Immediate deployment using NVIDIA AI Workbench with cloud endpoints
- **Intermediate Mode**: Code customization and application modification
- **Advanced Mode**: Self-hosted GPU infrastructure setup

This document focuses on initial setup and deployment decisions. For detailed configuration options, see [Configuration Reference](#7.1). For GPU compatibility and self-hosting details, see [GPU Compatibility and Self-Hosting](#6.2).

## System Overview and Mode Selection

The Agentic RAG system provides three distinct pathways based on your technical requirements and infrastructure preferences:

### Usage Mode Decision Matrix

| Mode | Time Investment | Technical Expertise | Infrastructure | Customization Level |
|------|-----------------|-------------------|----------------|-------------------|
| Easy | < 5 minutes | Minimal | Cloud endpoints | Pre-configured |
| Intermediate | Hours to days | Python/Git familiar | Cloud + local dev | Code modification |
| Advanced | Days to weeks | DevOps/GPU admin | Self-hosted GPUs | Full control |

### Mode-Specific Requirements and Outcomes

```mermaid
graph TB
    subgraph "Prerequisites"
        WB["NVIDIA AI Workbench"]
        Internet["Internet Connection"]
        APIKeys["API Keys"]
    end
    
    subgraph "Easy Mode"
        EasyPreq["Workbench + API Keys"]
        EasySteps["1. Clone repo<br/>2. Configure keys<br/>3. Open chat<br/>4. Add documents<br/>5. Ask questions"]
        EasyOutcome["Ready-to-use chat interface<br/>Cloud-powered inference"]
    end
    
    subgraph "Intermediate Mode"
        InterPreq["Easy Mode + Git/Python"]
        InterSteps["1. Fork repository<br/>2. Add VS Code<br/>3. Create branch<br/>4. Modify code<br/>5. Test changes"]
        InterOutcome["Customized application<br/>Modified prompts/UI<br/>Parameter tuning"]
    end
    
    subgraph "Advanced Mode"
        AdvPreq["Linux + GPU + Docker"]
        AdvSteps["1. Setup GPU host<br/>2. Deploy Ollama/NIM<br/>3. Configure endpoints<br/>4. Test inference"]
        AdvOutcome["Self-hosted infrastructure<br/>Full model control<br/>No cloud dependencies"]
    end
    
    WB --> EasyPreq
    Internet --> EasyPreq
    APIKeys --> EasyPreq
    
    EasyPreq --> EasySteps
    EasySteps --> EasyOutcome
    
    EasyOutcome --> InterPreq
    InterPreq --> InterSteps
    InterSteps --> InterOutcome
    
    InterOutcome --> AdvPreq
    AdvPreq --> AdvSteps
    AdvSteps --> AdvOutcome
```

Sources: [README.md:19-23](), [README.md:31-37](), [README.md:73-103]()

## Prerequisites

All usage modes require these foundational components:

### Core Requirements

1. **NVIDIA AI Workbench**: Download and install from the [official documentation](https://docs.nvidia.com/ai-workbench/user-guide/latest/installation/overview.html)
2. **Internet Connection**: Required for document embedding via NVIDIA endpoints
3. **API Keys**: Two API keys are needed for full functionality

### Required API Keys

| API Key | Purpose | Generation Link | Usage |
|---------|---------|-----------------|-------|
| `NVIDIA_API_KEY` | LLM inference and embeddings | [NGC API Keys](https://org.ngc.nvidia.com/setup/api-keys) | Cloud model access |
| `TAVILY_API_KEY` | Web search capabilities | [Tavily API](https://tavily.com) | Agentic web search |

### Environment Configuration

The system uses environment variables configured through NVIDIA AI Workbench's [variable management system](https://docs.nvidia.com/ai-workbench/user-guide/latest/environment/variables.html#basic-usage-for-environment-variables).

Sources: [README.md:24-29](), [README.md:32-34]()

## Application Architecture and Entry Points

Understanding the system's structure helps in choosing the appropriate mode and customization approach:

### System Entry Points and Code Mapping

```mermaid
graph LR
    subgraph "User Interfaces"
        ChatUI["gradio_app.py<br/>Chat Interface :8080"]
        JupyterLab["JupyterLab :8888"]
    end
    
    subgraph "Core Application Logic"
        MainApp["chatui/main.py<br/>Application Entry"]
        AgentGraph["agent.py<br/>LangGraph Workflow"]
        RouterNode["router_node<br/>Query Routing"]
        RetrievalNode["retrieval_grader_node<br/>Document Evaluation"]
        GeneratorNode["generator_node<br/>Answer Generation"]
    end
    
    subgraph "Data Management"
        VectorDB["chromadb_collection<br/>Vector Storage"]
        DocumentLoader["document_loaders<br/>PDF/Web Processing"]
        ContextManager["context_manager<br/>Document Context"]
    end
    
    subgraph "Model Integration"
        NVIDIAEndpoints["nvidia_ai_endpoints<br/>Cloud Models"]
        LocalModels["local_model_config<br/>Self-hosted Setup"]
        EmbeddingModel["NV-Embed-QA<br/>Text Embeddings"]
    end
    
    ChatUI --> MainApp
    MainApp --> AgentGraph
    AgentGraph --> RouterNode
    AgentGraph --> RetrievalNode
    AgentGraph --> GeneratorNode
    
    RetrievalNode --> VectorDB
    VectorDB --> DocumentLoader
    DocumentLoader --> ContextManager
    
    GeneratorNode --> NVIDIAEndpoints
    GeneratorNode --> LocalModels
    VectorDB --> EmbeddingModel
```

Sources: [README.md:1-16](), [code/chatui/](), [code/agent.py]()

## Mode-Specific Getting Started Paths

### Quick Mode Assessment

Use this decision tree to select your optimal starting path:

```mermaid
flowchart TD
    Start["Ready to Get Started?"]
    Start --> Q1{"Want immediate results<br/>without code changes?"}
    
    Q1 -->|Yes| Q2{"Have NVIDIA AI Workbench<br/>installed?"}
    Q1 -->|No| Q3{"Want to modify prompts,<br/>UI, or behavior?"}
    
    Q2 -->|Yes| EasyMode["Easy Mode<br/>Quick Start"]
    Q2 -->|No| InstallWB["Install AI Workbench<br/>then Easy Mode"]
    
    Q3 -->|Yes| Q4{"Comfortable with<br/>Python and Git?"}
    Q3 -->|No| EasyFirst["Start with Easy Mode<br/>then upgrade to Intermediate"]
    
    Q4 -->|Yes| InterMode["Intermediate Mode<br/>Code Customization"]
    Q4 -->|No| LearnFirst["Learn Python/Git basics<br/>then Intermediate Mode"]
    
    Q5{"Want self-hosted GPU<br/>infrastructure?"}
    InterMode --> Q5
    Q5 -->|Yes| AdvMode["Advanced Mode<br/>Self-Hosted Setup"]
    Q5 -->|No| StayInter["Continue with<br/>Intermediate Mode"]
    
    EasyMode --> EasySteps["Go to Easy Mode Guide"]
    InterMode --> InterSteps["Go to Intermediate Mode Guide"]
    AdvMode --> AdvSteps["Go to Advanced Mode Guide"]
```

Sources: [README.md:19-23](), [README.md:76-89](), [README.md:97-103]()

### Easy Mode Overview

For users who want immediate functionality with minimal setup:

**Target Users**: Business users, researchers, quick prototyping
**Time Investment**: < 5 minutes after Workbench installation
**Technical Skills**: Basic computer usage

**Process Summary**:
1. Clone repository in AI Workbench
2. Configure API keys when prompted
3. Open chat interface via "Open Chat" button
4. Add documents through Document tab
5. Start querying the system

For complete Easy Mode instructions, see [Easy Mode - Quick Start](#2.1).

### Intermediate Mode Overview

For developers who want to customize the application:

**Target Users**: Python developers, ML engineers, prompt engineers
**Time Investment**: Hours to days
**Technical Skills**: Python, Git, basic LLM concepts

**Process Summary**:
1. Fork the repository to your GitHub account
2. Add VS Code to the Workbench project
3. Create experimental branches for safe development
4. Modify prompts, parameters, and UI components
5. Test and iterate on changes

For complete Intermediate Mode instructions, see [Intermediate Mode - Code Customization](#2.2).

### Advanced Mode Overview

For users requiring self-hosted infrastructure:

**Target Users**: DevOps engineers, organizations with data privacy requirements
**Time Investment**: Days to weeks
**Technical Skills**: Linux administration, Docker, GPU management

**Process Summary**:
1. Set up Linux host with NVIDIA GPU and Docker
2. Deploy Ollama or NVIDIA NIM containers
3. Configure application to use self-hosted endpoints
4. Optimize models and infrastructure for performance

For complete Advanced Mode instructions, see [Advanced Mode - Self-Hosted Infrastructure](#2.3).

Sources: [README.md:31-66](), [README.md:73-89](), [README.md:96-103]()

## Next Steps

Based on your selected mode:

- **Easy Mode**: Proceed to [Easy Mode - Quick Start](#2.1) for step-by-step instructions
- **Intermediate Mode**: Start with [Intermediate Mode - Code Customization](#2.2) for development setup
- **Advanced Mode**: Begin with [Advanced Mode - Self-Hosted Infrastructure](#2.3) for infrastructure planning

For technical reference and troubleshooting, see [Technical Reference](#7).

Sources: [README.md:39-107]()

---

