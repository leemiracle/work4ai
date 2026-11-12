<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/ACE · extra page Colang 2.0 Sample Bot · fetched 2026-10-26 -->

# Colang 2.0 Sample Bot

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [microservices/ace_agent/4.0/deploy/ucs_apps/speech_bot/colang2_sample_bot/README.md](microservices/ace_agent/4.0/deploy/ucs_apps/speech_bot/colang2_sample_bot/README.md)

</details>



## Purpose and Scope

The Colang 2.0 Sample Bot demonstrates advanced conversational AI capabilities using NVIDIA's latest Colang 2.0 runtime within the ACE Agent framework. This sample application showcases multimodal interaction management, guardrailing mechanisms, and speech-enabled conversations through an event-driven architecture.

This documentation covers the speech-enabled bot implementation, deployment configuration, and integration patterns. For other sample bot implementations, see [Chat Bots](#5.1). For general ACE Agent microservices architecture, see [ACE Agent Framework](#3).

## Architecture Overview

The Colang 2.0 Sample Bot operates as a UCS (Unified Cloud Services) application that integrates multiple ACE Agent microservices to deliver speech-enabled conversational experiences.

### System Architecture

```mermaid
graph TB
    subgraph "Client Interfaces"
        grpcClient["gRPC Speech Client"]
        eventClient["Event Client"]
    end
    
    subgraph "ACE Agent Services"
        chatController["chat-controller<br/>Speech Pipeline Orchestration"]
        chatEngine["chat-engine<br/>Colang 2.0 Runtime"]
        nlpServer["nlp-server<br/>GPU Accelerated Processing"]
    end
    
    subgraph "Speech Processing"
        rivaASR["Riva ASR<br/>Speech-to-Text"]
        rivaTTS["Riva TTS<br/>Text-to-Speech"]
        audio2face["Audio2Face<br/>Facial Animation"]
    end
    
    subgraph "External Services"
        openaiAPI["OpenAI API<br/>gpt-3.5-turbo-instruct"]
        redisEvents["Redis<br/>Event Streaming"]
    end
    
    subgraph "Bot Configuration"
        colangFlows["Colang 2.0 Flows<br/>Conversation Logic"]
        appYaml["app.yaml<br/>UCS Configuration"]
        appParams["app-params.yaml<br/>Deployment Parameters"]
    end
    
    grpcClient --> chatController
    eventClient --> redisEvents
    
    chatController --> rivaASR
    chatController --> rivaTTS
    chatController --> audio2face
    chatController --> chatEngine
    
    chatEngine --> nlpServer
    chatEngine --> openaiAPI
    chatEngine --> redisEvents
    chatEngine --> colangFlows
    
    appYaml --> chatEngine
    appParams --> chatEngine
```

Sources: [microservices/ace_agent/4.0/deploy/ucs_apps/speech_bot/colang2_sample_bot/README.md:1-63]()

### Colang 2.0 Runtime Components

```mermaid
graph LR
    subgraph "Colang 2.0 Runtime"
        flowEngine["Flow Engine<br/>Hierarchical Flow Management"]
        actionExecutor["Action Executor<br/>Parallel Action Support"]
        eventBus["Event Bus<br/>UMIM Actions/Events"]
        guardrails["Guardrails<br/>Profanity & Content Filtering"]
    end
    
    subgraph "Conversation Features"
        chitChat["Chit-Chat<br/>General Conversation"]
        nvidiaQA["NVIDIA Q&A<br/>Company Information"]
        dateTime["Date/Time Queries<br/>Recent Information Integration"]
        profanityFilter["Profanity Handling<br/>Content Moderation"]
    end
    
    subgraph "External Integrations"
        llmModel["OpenAI Model<br/>gpt-3.5-turbo-instruct"]
        knowledgeBase["Knowledge Sources<br/>NVIDIA Information"]
    end
    
    flowEngine --> actionExecutor
    actionExecutor --> eventBus
    eventBus --> guardrails
    
    guardrails --> chitChat
    guardrails --> nvidiaQA
    guardrails --> dateTime
    guardrails --> profanityFilter
    
    chitChat --> llmModel
    nvidiaQA --> knowledgeBase
    dateTime --> llmModel
```

Sources: [microservices/ace_agent/4.0/deploy/ucs_apps/speech_bot/colang2_sample_bot/README.md:4-8]()

## Colang 2.0 Features

### Core Capabilities

Colang 2.0 represents a significant evolution from Colang 1.0, introducing multimodal interaction support at its foundation. The runtime provides several advanced features:

| Feature | Description | Use Case |
|---------|-------------|----------|
| **Parallel Actions** | Execute multiple conversation flows simultaneously | Handle interruptions and multi-threaded dialogues |
| **Hierarchical Flows** | Nested conversation structures with parent-child relationships | Complex conversation management |
| **UMIM Actions/Events** | Unified Multimodal Interaction Model support | Cross-modal event handling |
| **Guardrailing** | Built-in content filtering and conversation boundaries | Profanity detection and topic constraints |
| **Multimodal Core** | Native support for text, speech, and gesture inputs | Speech-enabled conversational AI |

### Conversation Management

The bot demonstrates practical implementations of Colang 2.0's conversation management capabilities:

- **Chit-Chat Experience**: General conversation handling using LLM-based responses
- **Domain-Specific Q&A**: NVIDIA-focused question answering with specialized knowledge
- **Content Filtering**: Automatic profanity detection and response moderation
- **Temporal Awareness**: Integration of current date/time information for relevant responses

Sources: [microservices/ace_agent/4.0/deploy/ucs_apps/speech_bot/colang2_sample_bot/README.md:4-8]()

## Deployment Configuration

### UCS Application Structure

The Colang 2.0 Sample Bot is packaged as a UCS application with the following configuration files:

```mermaid
graph TB
    subgraph "UCS Configuration"
        appYaml["app.yaml<br/>Application Definition"]
        appParams["app-params.yaml<br/>Deployment Parameters"]
    end
    
    subgraph "Generated Artifacts"
        helmChart["ucf-app-speech-bot-4.0.0/<br/>Generated Helm Chart"]
        k8sManifests["Kubernetes Manifests<br/>Service Definitions"]
    end
    
    subgraph "Kubernetes Resources"
        pods["ACE Agent Pods<br/>Microservice Containers"]
        secrets["Kubernetes Secrets<br/>API Keys & Credentials"]
        pvc["Persistent Volume Claims<br/>Model Storage"]
    end
    
    appYaml --> helmChart
    appParams --> helmChart
    
    helmChart --> k8sManifests
    k8sManifests --> pods
    k8sManifests --> secrets
    k8sManifests --> pvc
```

Sources: [microservices/ace_agent/4.0/deploy/ucs_apps/speech_bot/colang2_sample_bot/README.md:40-48]()

### Prerequisites and Dependencies

The deployment requires several prerequisite configurations:

| Requirement | Purpose | Configuration Command |
|-------------|---------|----------------------|
| **NGC Docker Registry Secret** | Access to NVIDIA container images | `kubectl create secret docker-registry ngc-docker-reg-secret` |
| **NGC API Key Secret** | Download models and resources from NGC | `kubectl create secret generic ngc-api-key-secret` |
| **OpenAI API Key Secret** | Access to OpenAI gpt-3.5-turbo-instruct model | `kubectl create secret generic openai-key-secret` |
| **Local Path Provisioner** | Persistent volume storage for models | `microk8s kubectl apply -f local-path-storage.yaml` |

### Build and Deployment Process

The deployment follows a standard UCS application lifecycle:

1. **Configuration Setup**: Environment variables and Kubernetes secrets
2. **Helm Chart Generation**: `ucf_app_builder_cli app build app.yaml app-params.yaml`
3. **Application Deployment**: `helm install ace-agent ucf-app-speech-bot-4.0.0/`
4. **Pod Readiness Verification**: `watch kubectl get pods`
5. **Client Interaction**: gRPC or event-based client connections

Sources: [microservices/ace_agent/4.0/deploy/ucs_apps/speech_bot/colang2_sample_bot/README.md:23-56]()

## Client Interaction Patterns

### Supported Client Interfaces

The Colang 2.0 Sample Bot supports two primary interaction patterns:

```mermaid
graph TB
    subgraph "Speech Interactions"
        speechClient["gRPC Server Sample Client"]
        speechPipeline["Speech Processing Pipeline"]
        audioInput["Audio Input Stream"]
        audioOutput["Audio Output Stream"]
    end
    
    subgraph "Text Interactions"
        eventClient["Event Sample Client"]
        eventInterface["ACE Agent Event Interface"]
        textInput["Text Messages"]
        textOutput["Text Responses"]
    end
    
    subgraph "Bot Processing"
        colangRuntime["Colang 2.0 Runtime"]
        chatEngine["Chat Engine"]
        eventBus["Redis Event Streaming"]
    end
    
    audioInput --> speechClient
    speechClient --> speechPipeline
    speechPipeline --> chatEngine
    chatEngine --> colangRuntime
    colangRuntime --> speechPipeline
    speechPipeline --> audioOutput
    
    textInput --> eventClient
    eventClient --> eventInterface
    eventInterface --> eventBus
    eventBus --> chatEngine
    chatEngine --> colangRuntime
    colangRuntime --> eventBus
    eventBus --> textOutput
```

Sources: [microservices/ace_agent/4.0/deploy/ucs_apps/speech_bot/colang2_sample_bot/README.md:55-56]()

### Event-Based Architecture

The bot leverages the ACE Agent event interface for asynchronous, event-driven interactions. This architecture supports:

- **Real-time Conversation Flow**: Immediate response to user inputs
- **Parallel Processing**: Multiple conversation threads and background tasks
- **State Management**: Persistent conversation context across interactions
- **Multimodal Coordination**: Synchronization between speech, text, and gesture inputs

Sources: [microservices/ace_agent/4.0/deploy/ucs_apps/speech_bot/colang2_sample_bot/README.md:8]()

## Integration with ACE Agent Services

### Service Dependencies

The Colang 2.0 Sample Bot integrates with multiple ACE Agent microservices:

| Service | Role | Integration Point |
|---------|------|-------------------|
| **chat-controller** | Speech pipeline orchestration | gRPC endpoint for audio processing |
| **chat-engine** | Colang 2.0 runtime hosting | HTTP API for conversation management |
| **nlp-server** | GPU-accelerated language processing | Internal service calls for NLP tasks |
| **Redis** | Event streaming and state management | Event bus for asynchronous communication |

### Model and Resource Management

The bot requires access to several external models and resources:

- **OpenAI gpt-3.5-turbo-instruct**: Primary language model for conversation generation
- **Riva ASR/TTS Models**: Speech processing models from NGC catalog  
- **NVIDIA Knowledge Base**: Specialized information for NVIDIA-related queries
- **Guardrail Models**: Content filtering and moderation capabilities

Sources: [microservices/ace_agent/4.0/deploy/ucs_apps/speech_bot/colang2_sample_bot/README.md:33-39]()

---

