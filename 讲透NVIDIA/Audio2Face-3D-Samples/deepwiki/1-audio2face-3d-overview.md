<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/Audio2Face-3D-Samples · page 1 Audio2Face-3D Overview · fetched 2026-10-26 -->

# Audio2Face-3D Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [quick-start/README.md](quick-start/README.md)

</details>



## Purpose and Scope

This document provides a high-level introduction to NVIDIA's Audio2Face-3D system, its architecture, and the organization of this repository. Audio2Face-3D NIM (NVIDIA Inference Microservice) is a generative AI solution that converts speech audio into facial animations using ARKit Blendshapes, with automatic emotion detection and expression generation.

For detailed information about specific character model configurations, see [Character Models and Stylization](#2). For deployment procedures, see [Deployment and Operations](#5). For client application usage, see [Client Applications and APIs](#4).

Sources: [README.md:1-57](), [quick-start/README.md:1-90]()

## System Architecture

Audio2Face-3D consists of several interconnected components that work together to process audio input and generate facial animation output.

### Core System Components

```mermaid
graph TB
    subgraph "Audio2Face-3D NIM Core"
        A2F_NIM["Audio2Face-3D NIM<br/>Main Inference Service<br/>Port: 52000"]
        A2E_Subsystem["Audio2Emotion Subsystem<br/>Emotion Detection"]
        A2F_Pipeline["Audio2Face Pipeline<br/>Blendshape Generation"]
    end
    
    subgraph "Character Models"
        Claire_Model["Claire Model<br/>claire_stylization_config.yaml"]
        James_Model["James Model<br/>james_stylization_config.yaml"]
        Mark_Model["Mark Model<br/>mark_stylization_config.yaml"]
    end
    
    subgraph "Configuration System"
        Deployment_Config["deployment_config.yaml<br/>Service Configuration"]
        Advanced_Config["advanced_config.yaml<br/>Pipeline Settings"]
        Migration_Tool["convert_configuration_files.py<br/>Version Migration"]
    end
    
    subgraph "Client Applications"
        Micro_Client["a2f_3d.py<br/>Primary Client App"]
        API_Client["nim_a2f_3d_client.py<br/>NVCF API Client"]
        Authoring_Clients["client_local_deploy.py<br/>client_nvcf_deploy.py<br/>Authoring Sample Apps"]
    end
    
    subgraph "Deployment Infrastructure"
        Docker_Compose["docker-compose.yml<br/>Container Orchestration"]
        Observability["Prometheus + Jaeger<br/>Metrics and Tracing"]
        TRT_Cache["a2f-3d-init-data/<br/>TensorRT Model Cache"]
    end
    
    A2F_NIM --> A2E_Subsystem
    A2F_NIM --> A2F_Pipeline
    
    Claire_Model --> A2F_NIM
    James_Model --> A2F_NIM
    Mark_Model --> A2F_NIM
    
    Deployment_Config --> A2F_NIM
    Advanced_Config --> A2F_Pipeline
    Migration_Tool --> Deployment_Config
    Migration_Tool --> Advanced_Config
    Migration_Tool --> Claire_Model
    Migration_Tool --> James_Model
    Migration_Tool --> Mark_Model
    
    Micro_Client -.->|"gRPC"| A2F_NIM
    API_Client -.->|"gRPC + Auth"| A2F_NIM
    Authoring_Clients -.->|"gRPC"| A2F_NIM
    
    Docker_Compose --> A2F_NIM
    Observability --> A2F_NIM
    TRT_Cache --> A2F_NIM
```

Sources: [README.md:29-48](), [quick-start/README.md:19-44]()

## Core Components

### Audio2Face-3D NIM Service

The primary service that processes audio input and generates facial animation output. The service operates on port 52000 by default and provides gRPC endpoints for:

- Health checking and service status
- Audio-to-blendshape inference
- Emotion detection and processing
- Performance monitoring and metrics

The service supports three character models: `claire`, `james`, and `mark`, each with distinct facial characteristics and parameter configurations.

### Character Model System

| Character | Model Version | Configuration File | Key Features |
|-----------|---------------|-------------------|--------------|
| Claire | v2.3 | `claire_stylization_config.yaml` | Balanced emotional expression |
| James | v2.3 | `james_stylization_config.yaml` | Masculine facial characteristics |
| Mark | v2.3 | `mark_stylization_config.yaml` | Distinct personality parameters |

Each character model includes Audio2Emotion (A2E) and Audio2Face (A2F) parameter configurations that control blendshape generation and emotional expression intensity.

### Processing Pipeline

```mermaid
graph LR
    subgraph "Input Processing"
        Audio_Input["Audio Input<br/>16-bit PCM WAV"]
        Emotion_Config["Emotion Configuration<br/>YAML Parameters"]
    end
    
    subgraph "Audio2Face-3D Processing"
        Stream_Handler["gRPC Stream Handler<br/>Bidirectional Processing"]
        A2E_Engine["Audio2Emotion Engine<br/>Emotion Detection"]
        A2F_Engine["Audio2Face Engine<br/>Blendshape Generation"]
        TRT_Models["TensorRT Models<br/>Cached in a2f-3d-init-data/"]
    end
    
    subgraph "Output Generation"
        Blendshapes_Output["ARKit Blendshapes<br/>52 Coefficient Values"]
        Emotion_Output["Emotion Vectors<br/>Detected Emotions"]
        Audio_Output["Processed Audio<br/>out.wav"]
    end
    
    Audio_Input --> Stream_Handler
    Emotion_Config --> Stream_Handler
    Stream_Handler --> A2E_Engine
    Stream_Handler --> A2F_Engine
    A2E_Engine --> TRT_Models
    A2F_Engine --> TRT_Models
    A2E_Engine --> Emotion_Output
    A2F_Engine --> Blendshapes_Output
    Stream_Handler --> Audio_Output
```

Sources: [README.md:5-10](), [quick-start/README.md:41-42](), [quick-start/README.md:50-51]()

## Repository Structure

The repository is organized into functional modules that correspond to different aspects of the Audio2Face-3D system:

### Directory Layout

| Directory | Purpose | Key Files | Wiki Section |
|-----------|---------|-----------|--------------|
| `configs/` | Configuration templates and examples | `deployment_config.yaml`, `advanced_config.yaml`, character configs | [2](#2), [3.2](#3.2) |
| `early_access/` | Early access sample applications | `client_local_deploy.py`, `client_nvcf_deploy.py` | [4.3](#4.3) |
| `example_audio/` | Sample audio files for testing | WAV audio files | [6.2](#6.2) |
| `migration/` | Configuration migration tools | `convert_configuration_files.py` | [3](#3), [3.1](#3.1) |
| `proto/` | gRPC protocol definitions | Proto files and build instructions | [6.1](#6.1) |
| `quick-start/` | Docker deployment files | `docker-compose.yml` | [5.1](#5.1) |
| `scripts/` | Client applications | `a2f_3d.py`, `nim_a2f_3d_client.py` | [4](#4) |

### Configuration Management

The system uses a hierarchical configuration approach:

- **Deployment Configuration**: Service endpoints, authentication, and telemetry settings
- **Advanced Configuration**: Pipeline performance and processing parameters  
- **Stylization Configuration**: Character-specific Audio2Emotion and Audio2Face parameters

Configuration files have evolved from version 1.0 to 1.2, with migration tools provided to upgrade existing configurations.

Sources: [README.md:33-48]()

## Key Technologies and Protocols

### Communication Protocol

Audio2Face-3D uses gRPC for client-server communication, with protocol definitions available in the `nvidia_ace` Python wheel. The service supports:

- Bidirectional streaming for real-time audio processing
- Authentication via API keys for cloud deployments
- Health check endpoints for service monitoring

### Model Execution

The system utilizes TensorRT for optimized model inference:

- Models are compiled to TensorRT format on first startup
- Compiled models are cached in the `a2f-3d-init-data/` directory
- Cache can be invalidated by removing `*.trt` files

### Observability

Integrated monitoring and tracing capabilities:

- Prometheus metrics collection on port 9090
- Jaeger distributed tracing on port 16686
- Configurable telemetry settings in `deployment_config.yaml`

Sources: [quick-start/README.md:50-74](), [README.md:42-43]()

---

