<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/ACE · page 1 NVIDIA ACE Overview · fetched 2026-10-26 -->

# NVIDIA ACE Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [README.md](README.md)

</details>



## Purpose and Scope

This document provides a comprehensive overview of the NVIDIA ACE repository, which contains a suite of technologies for building digital humans and conversational AI agents using generative AI. The material covers the core digital human microservices (NIMs), the ACE Agent framework architecture, deployment patterns, and sample applications.

For detailed information about specific microservices implementations, see [Core Digital Human Technologies](#2). For comprehensive documentation of the ACE Agent framework components, see [ACE Agent Framework](#3). For deployment strategies and infrastructure setup, see [Deployment & Infrastructure](#4).

Sources: [README.md:1-95]()

## NVIDIA ACE Platform Architecture

NVIDIA ACE is structured as a comprehensive platform combining digital human technologies with conversational AI capabilities. The platform consists of two primary architectural layers: the Digital Human Microservices layer for speech, animation, and rendering, and the ACE Agent Framework layer for conversational AI orchestration.

### Digital Human Technology Stack

```mermaid
graph TD
    subgraph "NVIDIA ACE Platform"
        subgraph "Digital Human Microservices (NIMs)"
            ASR["riva-speech-api<br/>Automatic Speech Recognition"]
            TTS["riva-speech-api<br/>Text-to-Speech"]
            NMT["riva-speech-api<br/>Neural Machine Translation"]
            A2F["audio2face-microservice<br/>Facial Animation Pipeline"]
            AnimGraph["animation-graph-microservice<br/>Animation Controller"]
            RTXRender["omniverse-renderer-microservice<br/>RTX Pixel Streaming"]
            LivePortrait["live-portrait-microservice<br/>2D Picture Animation"]
        end
        
        subgraph "ACE Agent Framework v4.0"
            ChatController["chat-controller<br/>gRPC Pipeline Orchestrator"]
            ChatEngine["chat-engine<br/>HTTP Conversation Manager"]
            NLPServer["nlp-server<br/>GPU Language Processing"]
            PluginServer["plugin-server<br/>External API Gateway"]
            WebApp["web-app<br/>Frontend Interface"]
        end
    end
    
    subgraph "External Dependencies"
        OpenAI["OpenAI API<br/>GPT Models"]
        NGC["NVIDIA GPU Cloud<br/>Model Repository"]
        Redis["redis<br/>Event Streaming"]
    end
    
    %% Service Interactions
    ChatController --> ASR
    ChatController --> TTS
    ChatController --> A2F
    ChatEngine --> NLPServer
    ChatEngine --> PluginServer
    ChatEngine --> OpenAI
    NLPServer --> NGC
    PluginServer --> Redis
    
    %% Client Access Patterns
    ChatController -.-> ChatEngine
    WebApp --> ChatEngine
```

The platform provides state-of-the-art AI models with real-time performance, commercially safe training data, and flexible deployment options supporting public/private cloud, Windows PC, or hybrid configurations.

Sources: [README.md:4-49](), [README.md:32-46]()

## Core Technology Components

NVIDIA ACE integrates multiple specialized microservices, each designed for specific aspects of digital human creation and interaction:

| Technology | Service Name | Description | Deployment Support |
|------------|--------------|-------------|-------------------|
| Riva ASR | `riva-speech-api` | Speech → Text conversion | Cloud, Windows (Coming Soon) |
| Riva TTS | `riva-speech-api` | Text → Speech synthesis | Cloud, Windows (Coming Soon) |
| Riva NMT | `riva-speech-api` | Multi-language text translation | Cloud Only |
| Audio2Face | `audio2face-microservice` | Audio → Facial blendshapes | Cloud, Windows (Coming Soon) |
| AnimGraph | `animation-graph-microservice` | Animation state management | Cloud Only |
| RTX Renderer | `omniverse-renderer-microservice` | Omniverse-based pixel streaming | Cloud Only |
| ACE Agent | `ace-agent` | Conversational AI with RAG | Cloud Only |
| Live Portrait | `live-portrait-microservice` | 2D facial animation | Cloud Only |

Sources: [README.md:15-30]()

## ACE Agent Framework Architecture

The ACE Agent Framework provides a microservices-based architecture for building scalable conversational AI applications. The framework consists of five core services that work together to handle speech processing, natural language understanding, and business logic integration.

### Core Services Architecture

```mermaid
graph TB
    subgraph "Client Interfaces"
        gRPCClient["speech_client.py<br/>gRPC Audio Streaming"]
        HTTPClient["chat_client.py<br/>HTTP Text Interface"]
        EventClient["event_client.py<br/>Textual TUI"]
        WebInterface["web-app service<br/>Browser Frontend"]
    end
    
    subgraph "ACE Agent Microservices"
        ChatController["chat-controller<br/>chat_controller_service.py"]
        ChatEngine["chat-engine<br/>chat_engine_service.py"]
        NLPServer["nlp-server<br/>nlp_service.py"]
        PluginServer["plugin-server<br/>plugin_service.py"]
        WebApp["web-app<br/>app.py Flask Service"]
    end
    
    subgraph "Configuration & State"
        RedisStreams["redis<br/>Event Streaming & State"]
        ConfigFiles["bot_config.yaml<br/>Bot Definitions"]
        ModelRepo["models/<br/>Local Model Storage"]
    end
    
    subgraph "External APIs"
        OpenAIAPI["OpenAI API<br/>GPT-4 Integration"]
        NVIDIAAPI["NVIDIA API Catalog<br/>Model Inference"]
        YahooAPI["Yahoo Finance API<br/>Stock Data"]
    end
    
    %% Client to Service Connections
    gRPCClient --> ChatController
    HTTPClient --> ChatEngine
    EventClient --> RedisStreams
    WebInterface --> WebApp
    
    %% Inter-service Communication
    ChatController --> ChatEngine
    ChatEngine --> NLPServer
    ChatEngine --> PluginServer
    ChatEngine --> RedisStreams
    
    %% External Service Integration
    ChatEngine --> OpenAIAPI
    NLPServer --> NVIDIAAPI
    PluginServer --> YahooAPI
    
    %% Configuration Access
    ChatEngine --> ConfigFiles
    PluginServer --> ConfigFiles
    NLPServer --> ModelRepo
```

Each microservice operates independently with well-defined interfaces, enabling horizontal scaling and independent deployment cycles. The `chat-controller` orchestrates speech processing pipelines, while the `chat-engine` handles conversational logic and integrates with external AI services.

Sources: [README.md:25](), [README.md:75]()

## Deployment Ecosystem

NVIDIA ACE supports multiple deployment patterns designed for different use cases and infrastructure requirements. The repository provides both containerized local development environments and production-ready Kubernetes deployments through the NVIDIA UCS (Unified Cloud Services) platform.

### Deployment Architecture Overview

```mermaid
graph TB
    subgraph "Development Environment"
        GitRepo["ACE Repository<br/>git + git-lfs"]
        DockerCompose["docker-compose.yml<br/>Local Development"]
        EnvFiles[".env files<br/>API Key Configuration"]
    end
    
    subgraph "Container Registry & Models"
        NGCRegistry["nvcr.io<br/>NVIDIA GPU Cloud Registry"]
        NGCCatalog["NGC Model Catalog<br/>Pre-trained Models"]
        ModelCache["Local Model Cache<br/>Downloaded NIMs"]
    end
    
    subgraph "Production Deployment"
        subgraph "UCS Platform"
            UCSTools["ucs_tools<br/>Kubernetes Generator"]
            HelmCharts["Generated Helm Charts<br/>K8s Deployment Manifests"]
            K8sCluster["Kubernetes Cluster<br/>Container Orchestration"]
        end
        
        subgraph "Sample Applications"
            FoodBotDeploy["food-ordering-bot<br/>UCS Application"]
            StockBotDeploy["stock-bot<br/>UCS Application"]
            RAGBotDeploy["rag-bot<br/>UCS Application"]
            SpeechBotDeploy["colang2-sample-bot<br/>Speech-enabled Bot"]
        end
    end
    
    subgraph "External Infrastructure"
        TerraformIaC["terraform/<br/>Infrastructure as Code"]
        CloudProviders["AWS/GCP/Azure<br/>Cloud Infrastructure"]
    end
    
    %% Deployment Flow
    GitRepo --> DockerCompose
    DockerCompose --> NGCRegistry
    NGCRegistry --> ModelCache
    
    UCSTools --> HelmCharts
    HelmCharts --> K8sCluster
    K8sCluster --> FoodBotDeploy
    K8sCluster --> StockBotDeploy
    K8sCluster --> RAGBotDeploy
    K8sCluster --> SpeechBotDeploy
    
    TerraformIaC --> CloudProviders
    CloudProviders --> K8sCluster
    
    NGCCatalog --> ModelCache
```

The deployment ecosystem leverages NVIDIA's container registry (`nvcr.io`) for microservice distribution and supports both Docker Compose for local development and Kubernetes for production scalability. UCS tools generate Helm charts for streamlined Kubernetes deployments.

Sources: [README.md:8-13](), [README.md:70]()

## Sample Applications Overview

The repository includes multiple sample applications demonstrating different ACE capabilities, from text-based conversational bots to speech-enabled multimodal interactions. These samples serve as reference implementations for common digital human use cases.

### Application Architecture Patterns

```mermaid
graph LR
    subgraph "Text-Based Bots"
        FoodBot["food-ordering-bot<br/>Menu Management & Cart"]
        StockBot["stock-bot<br/>Yahoo Finance Integration"]
        RAGBot["rag-bot<br/>Document Q&A Pipeline"]
    end
    
    subgraph "Speech-Enabled Bots"
        Colang2Bot["colang2-sample-bot<br/>Multimodal Interactions"]
        SpeechDemo["Speech Processing Demo<br/>ASR/TTS Pipeline"]
    end
    
    subgraph "Reference Workflows"
        GamingFlow["Gaming Workflow<br/>Audio2Face + Unreal Engine"]
        CustomerServiceFlow["Tokkio Workflow<br/>Customer Service Kiosk"]
        Text2GestureFlow["Text-to-Gesture<br/>A2X + Animation Graph"]
    end
    
    subgraph "ACE Agent Framework"
        CoreServices["chat-engine + nlp-server<br/>plugin-server + chat-controller"]
    end
    
    %% Application Dependencies
    FoodBot --> CoreServices
    StockBot --> CoreServices
    RAGBot --> CoreServices
    Colang2Bot --> CoreServices
    SpeechDemo --> CoreServices
    
    %% Workflow Integration
    GamingFlow --> CoreServices
    CustomerServiceFlow --> CoreServices
    Text2GestureFlow --> CoreServices
```

Each sample application demonstrates specific integration patterns with external APIs, different conversation management approaches using Colang/NeMo Guardrails, and various deployment configurations suitable for different production scenarios.

Sources: [README.md:51-62](), [README.md:81-88]()

## Key Benefits and Capabilities

NVIDIA ACE provides three primary advantages for digital human development:

- **State-of-the-Art Models and Microservices**: Pre-trained NVIDIA models deliver industry-leading quality with real-time performance optimization
- **Safe and Consistent Results**: AI models trained on commercially safe, responsibly licensed data with fine-tuning and guardrails for appropriate responses
- **Flexible Deployment Options**: Support for inference across public/private cloud, Windows PC, or hybrid configurations

The platform enables developers to build custom digital human solutions from scratch or leverage domain-specific workflows for gaming NPCs, customer service assistants, and real-time communication avatars.

Sources: [README.md:32-62]()

---

