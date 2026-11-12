<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/ACV · page 2 Self-Managing Systems · fetched 2026-10-26 -->

# Self-Managing Systems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [self_managing_systems/microservice/README.md](self_managing_systems/microservice/README.md)
- [self_managing_systems/microservice/paper_artifact_arXiv_2407_14402/README.md](self_managing_systems/microservice/paper_artifact_arXiv_2407_14402/README.md)

</details>



## Purpose and Scope

This document covers the Self-Managing Systems workstream, which represents the primary research domain within the Autonomic Computing Vision (ACV) repository. This workstream focuses on developing LLM-based agents for microservice self-management in distributed systems, particularly within Kubernetes environments. The system implements the four key properties of autonomic computing: self-configuration, self-optimization, self-healing, and self-protection.

The Self-Managing Systems workstream includes two main implementations: a research Paper Artifact for experimental validation and AutoKube as a general-purpose tool. For information about the secondary research domain focused on image retrieval, see [OSrCIR System](#3).

Sources: [README.md:13-25](), [self_managing_systems/microservice/README.md:1-7]()

## System Architecture Overview

The Self-Managing Systems workstream implements a multi-agent architecture where LLM-powered agents manage microservices autonomously. The system operates through two primary implementations that share core architectural principles.

### High-Level Architecture

```mermaid
graph TB
    subgraph "Self-Managing Systems Workstream"
        PA["Paper Artifact<br/>arXiv 2407.14402"]
        AK["AutoKube<br/>General Tool"]
    end
    
    subgraph "Core Agent System"
        CM["ClusterManager"]
        SM["ServiceMaintainer"]
        IE["Intent Execution<br/>main.py"]
    end
    
    subgraph "LLM Integration Layer"
        OPENAI["OpenAI Backend"]
        AZURE["AzureOpenAI Backend"] 
        OTHER["Other Backend"]
        CONFIG["conf/secret.yaml"]
    end
    
    subgraph "Infrastructure Layer"
        K8S["Kubernetes Cluster"]
        SOCKSHOP["Sock Shop Demo"]
        SOCIAL["Social Network Benchmark"]
        RABBIT["RabbitMQ Message Broker"]
        PROM["Prometheus Monitoring"]
    end
    
    subgraph "Experience System"
        EXP["Experience Banks"]
        JSONL["JSONL Storage"]
        FILTER["Experience Filtering"]
    end
    
    PA --> CM
    PA --> SM
    AK --> CM
    AK --> SM
    
    CM --> IE
    SM --> IE
    
    CM --> OPENAI
    SM --> AZURE
    IE --> OTHER
    CONFIG --> OPENAI
    CONFIG --> AZURE
    CONFIG --> OTHER
    
    CM --> K8S
    SM --> K8S
    K8S --> SOCKSHOP
    K8S --> SOCIAL
    K8S --> RABBIT
    K8S --> PROM
    
    CM --> EXP
    SM --> EXP
    EXP --> JSONL
    EXP --> FILTER
```

Sources: [README.md:17-24](), [self_managing_systems/microservice/README.md:5-7](), [self_managing_systems/microservice/paper_artifact_arXiv_2407_14402/README.md:47-76]()

### Code-to-System Mapping

```mermaid
graph LR
    subgraph "Python Modules"
        ELL12["src.empirical_low_level_L1_2"]
        ELL345["src.empirical_low_level_L3_4_5"]
        EHL12["src.empirical_high_level_L1_2"]
        EHL345["src.empirical_high_level_L3_4_5"]
        WM1["src.working_mechanism_1"]
        WM2["src.working_mechanism_2"]
    end
    
    subgraph "Configuration Files"
        SECRET["conf/secret.yaml"]
        TEMPLATE["conf/secret_template.yaml"]
        REQUIREMENTS["requirements.txt"]
    end
    
    subgraph "Script Directory"
        CHECK["scripts/check_prerequisites.sh"]
        SETUP["scripts/setup.sh"]
        CREATE["scripts/create_project.sh"]
        REMOVE["scripts/remove_project.sh"]
    end
    
    subgraph "Data and Results"
        DATASET["data/dataset/"]
        RESULTS["results/*.md"]
        LOGS["logs/"]
    end
    
    ELL12 --> SECRET
    ELL345 --> SECRET
    EHL12 --> SECRET
    EHL345 --> SECRET
    WM1 --> SECRET
    WM2 --> SECRET
    
    SECRET --> TEMPLATE
    
    CREATE --> SETUP
    REMOVE --> CHECK
    
    ELL12 --> RESULTS
    WM1 --> LOGS
    WM2 --> DATASET
```

Sources: [self_managing_systems/microservice/paper_artifact_arXiv_2407_14402/README.md:78-161]()

## Paper Artifact Implementation

The Paper Artifact implements the experimental framework described in arXiv paper 2407.14402, providing empirical validation of LLM-based agents for microservice self-management. This implementation focuses on the Sock Shop microservice demo environment.

### Experimental Framework

The Paper Artifact includes multiple experimental modules that test different autonomic levels (L1-L5) and agent architectures:

| Module | Purpose | Agent Level | Test Cases |
|--------|---------|-------------|------------|
| `src.empirical_low_level_L1_2` | Basic autonomic tasks | Low-level | metric_collection, restart |
| `src.empirical_low_level_L3_4_5` | Advanced autonomic tasks | Low-level | pod_failure scenarios |
| `src.empirical_high_level_L1_2` | Group management tasks | High-level | Multi-component optimization |
| `src.empirical_high_level_L3_4_5` | Complex group scenarios | High-level | Coordinated failure handling |

### Working Mechanisms

The system implements two primary working mechanisms:

```mermaid
graph TD
    subgraph "Working Mechanism 1"
        WM1_TASK["Task: Report CPU usage"]
        WM1_COMP["Component: catalogue"]
        WM1_AGENT["Single Agent<br/>ServiceMaintainer"]
        WM1_ACTION["Direct kubectl commands"]
    end
    
    subgraph "Working Mechanism 2"
        WM2_TASK["Task: Reduce P99 latency"]
        WM2_COMP["Components: catalogue,front-end"]
        WM2_AGENTS["Multi-Agent<br/>ClusterManager + ServiceMaintainer"]
        WM2_COORD["Coordinated optimization"]
    end
    
    WM1_TASK --> WM1_COMP
    WM1_COMP --> WM1_AGENT
    WM1_AGENT --> WM1_ACTION
    
    WM2_TASK --> WM2_COMP
    WM2_COMP --> WM2_AGENTS
    WM2_AGENTS --> WM2_COORD
```

Sources: [self_managing_systems/microservice/paper_artifact_arXiv_2407_14402/README.md:127-156]()

### LLM Configuration

The Paper Artifact supports multiple LLM backends through a unified configuration system in `conf/secret.yaml`:

```mermaid
graph LR
    subgraph "LLM Backend Configuration"
        ST["conf/secret_template.yaml"]
        SC["conf/secret.yaml"]
        
        subgraph "Backend Types"
            OAI["OpenAI<br/>gpt-4"]
            AOAI["AzureOpenAI<br/>azure deployment"]
            OTHER["Other<br/>local API"]
        end
    end
    
    ST --> SC
    SC --> OAI
    SC --> AOAI
    SC --> OTHER
    
    subgraph "Agent Components"
        CM_PA["ClusterManager"]
        SM_PA["ServiceMaintainer"]
    end
    
    OAI --> CM_PA
    AOAI --> SM_PA
    OTHER --> CM_PA
```

Sources: [self_managing_systems/microservice/paper_artifact_arXiv_2407_14402/README.md:47-76]()

## AutoKube System

AutoKube represents the general-purpose tool implementation of the Self-Managing Systems architecture, designed to simplify microservice management in Kubernetes through LLM-powered agents. While the Paper Artifact focuses on experimental validation, AutoKube aims for practical deployment scenarios.

### Tool Architecture

AutoKube builds upon the research work from the Paper Artifact but extends it for broader applicability beyond the experimental Sock Shop environment. The system maintains the core agent architecture while providing enhanced Dev and Ops workflow integration.

```mermaid
graph TB
    subgraph "AutoKube General Tool"
        CLI["AutoKube CLI Interface"]
        DEV["Dev Workflow Support"]
        OPS["Ops Workflow Support"]
    end
    
    subgraph "Shared Agent Core"
        CORE_CM["ClusterManager Agent"]
        CORE_SM["ServiceMaintainer Agent"]
        INTENT["Intent Processing"]
    end
    
    subgraph "Enhanced Features"
        MULTI_ENV["Multi-Environment Support"]
        PROD_READY["Production Readiness"]
        EXT_INT["Extended Integrations"]
    end
    
    CLI --> DEV
    CLI --> OPS
    DEV --> CORE_CM
    OPS --> CORE_SM
    CORE_CM --> INTENT
    CORE_SM --> INTENT
    
    CORE_CM --> MULTI_ENV
    CORE_SM --> PROD_READY
    INTENT --> EXT_INT
```

Sources: [README.md:10](), [self_managing_systems/microservice/README.md:6]()

## Agent Architecture

The core agent system implements a hierarchical architecture with specialized agents for different management scopes. The `ClusterManager` handles cluster-level operations while `ServiceMaintainer` instances manage individual services.

### Agent Component Relationships

```mermaid
graph TD
    subgraph "Agent Hierarchy"
        CM["ClusterManager<br/>Cluster-level decisions"]
        SM1["ServiceMaintainer<br/>catalogue service"]
        SM2["ServiceMaintainer<br/>front-end service"]
        SM3["ServiceMaintainer<br/>orders service"]
    end
    
    subgraph "Intent Processing"
        IE["Intent Execution<br/>main.py entry point"]
        DECOMP["Component Decomposition"]
        COORD["Agent Coordination"]
    end
    
    subgraph "Experience Management"
        EB["Experience Banks"]
        FILTER["Experience Filtering"]
        STORAGE["JSONL Storage"]
    end
    
    subgraph "LLM Integration"
        PROMPT["Prompt Templates"]
        CHAT["Chat Log Processing"]
        DECISION["Decision Making"]
    end
    
    IE --> DECOMP
    DECOMP --> CM
    DECOMP --> SM1
    DECOMP --> SM2
    DECOMP --> SM3
    
    CM --> COORD
    SM1 --> COORD
    SM2 --> COORD
    SM3 --> COORD
    
    CM --> EB
    SM1 --> EB
    EB --> FILTER
    FILTER --> STORAGE
    
    CM --> PROMPT
    SM1 --> CHAT
    PROMPT --> DECISION
    CHAT --> DECISION
```

Sources: [self_managing_systems/microservice/paper_artifact_arXiv_2407_14402/README.md:78-86](), [self_managing_systems/microservice/paper_artifact_arXiv_2407_14402/README.md:139-155]()

### Agent Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant MainPy as "main.py"
    participant ClusterMgr as "ClusterManager"
    participant ServiceMaint as "ServiceMaintainer"
    participant LLM as "LLM Backend"
    participant K8s as "Kubernetes API"
    participant ExpBank as "Experience Bank"
    
    User->>MainPy: "Execute intent with components"
    MainPy->>MainPy: "Decompose components list"
    MainPy->>ClusterMgr: "Initialize cluster manager"
    MainPy->>ServiceMaint: "Initialize service maintainers"
    
    ClusterMgr->>LLM: "Request cluster-level decisions"
    ServiceMaint->>LLM: "Request service-level actions"
    
    LLM->>ClusterMgr: "Return management strategy"
    LLM->>ServiceMaint: "Return action commands"
    
    ClusterMgr->>K8s: "Execute cluster operations"
    ServiceMaint->>K8s: "Execute service operations"
    
    K8s->>ClusterMgr: "Return operation results"
    K8s->>ServiceMaint: "Return action results"
    
    ClusterMgr->>ExpBank: "Store successful experiences"
    ServiceMaint->>ExpBank: "Store service experiences"
    
    ExpBank->>ExpBank: "Filter and index experiences"
```

Sources: [self_managing_systems/microservice/paper_artifact_arXiv_2407_14402/README.md:78-86]()

## Development and Deployment

The Self-Managing Systems workstream provides comprehensive scripts and workflows for setting up development and experimental environments.

### Environment Setup Workflow

```mermaid
graph TD
    subgraph "Prerequisites Check"
        LINUX["Linux System Environment"]
        DOCKER["Docker Installation"]
        RABBIT["RabbitMQ Installation"]
        CHECK_SCRIPT["scripts/check_prerequisites.sh"]
    end
    
    subgraph "Installation Process"
        CLONE["git clone microsoft/ACV"]
        CONDA["conda create -n acv_llm"]
        PIP["pip install -r requirements.txt"]
        AZURE_ID["pip install azure-identity-broker"]
        SETUP_SCRIPT["scripts/setup.sh"]
    end
    
    subgraph "Configuration"
        SECRET_TEMPLATE["conf/secret_template.yaml"]
        SECRET_CONFIG["conf/secret.yaml"]
        LLM_BACKEND["Configure LLM backend"]
    end
    
    subgraph "Project Management"
        CREATE_PROJ["scripts/create_project.sh"]
        REMOVE_PROJ["scripts/remove_project.sh"]
        ENVIRONMENT["Sock Shop deployment"]
    end
    
    LINUX --> CHECK_SCRIPT
    DOCKER --> CHECK_SCRIPT
    RABBIT --> CHECK_SCRIPT
    CHECK_SCRIPT --> CLONE
    
    CLONE --> CONDA
    CONDA --> PIP
    PIP --> AZURE_ID
    AZURE_ID --> SETUP_SCRIPT
    
    SETUP_SCRIPT --> SECRET_TEMPLATE
    SECRET_TEMPLATE --> SECRET_CONFIG
    SECRET_CONFIG --> LLM_BACKEND
    
    LLM_BACKEND --> CREATE_PROJ
    CREATE_PROJ --> ENVIRONMENT
    ENVIRONMENT --> REMOVE_PROJ
```

Sources: [self_managing_systems/microservice/paper_artifact_arXiv_2407_14402/README.md:22-45](), [self_managing_systems/microservice/paper_artifact_arXiv_2407_14402/README.md:131-161]()

### Experimental Execution Patterns

The system supports various execution patterns for different experimental scenarios:

| Execution Pattern | Command Example | Purpose |
|------------------|-----------------|---------|
| Quick Trial | `python -m src.empirical_low_level_L1_2 --instance metric_collection_1` | Basic functionality test |
| Low-level L1-L2 | `python -m src.empirical_low_level_L1_2 --instance restart` | Simple autonomic tasks |
| Low-level L3-L5 | `python -m src.empirical_low_level_L3_4_5 --instance pod_failure` | Advanced failure handling |
| High-level L1-L2 | `python -m src.empirical_high_level_L1_2 --task 'Reduce P99 latency'` | Multi-component optimization |
| Working Mechanism 1 | `python -m src.working_mechanism_1 --task 'Report CPU usage'` | Single-agent operations |
| Working Mechanism 2 | `python -m src.working_mechanism_2 --task 'Reduce latency'` | Multi-agent coordination |

Sources: [self_managing_systems/microservice/paper_artifact_arXiv_2407_14402/README.md:78-156]()

---

