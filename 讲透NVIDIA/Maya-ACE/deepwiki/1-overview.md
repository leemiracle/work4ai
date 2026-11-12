<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/Maya-ACE · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [LICENSE.txt](LICENSE.txt)
- [README.md](README.md)

</details>



## Purpose and Scope

This document provides a comprehensive overview of Maya-ACE, covering its architecture, core components, and integration patterns. Maya-ACE serves as a reference implementation for integrating NVIDIA's Audio2Face-3D service with Autodesk Maya through a native plugin architecture.

For step-by-step setup instructions, see [Getting Started](#2). For detailed build procedures, see [Building and Testing](#4.1). For technical specifications on supported audio formats, see [Audio Specifications](#5.1).

## What is Maya-ACE

Maya-ACE is a reference client implementation that enables Maya users to access NVIDIA's ACE Audio2Face-3D service for generating high-quality, audio-driven facial animations. The system consists of a Maya plugin (`maya_aceclient`), gRPC-based service communication, and integration with Maya's native blendshape animation system.

The core workflow involves sending audio data to NVIDIA's cloud-based Audio2Face-3D service and receiving facial animation data that drives character blendshapes in real-time or batch processing modes.

**Sources:** [README.md:3-16](), [README.md:43-50]()

## System Architecture Overview

Maya-ACE implements a plugin-based architecture that extends Maya's functionality while maintaining clean separation between presentation, business logic, and external service integration.

### High-Level Component Architecture

```mermaid
graph TB
    subgraph "Maya Environment"
        MAYA["Autodesk Maya 2024/2025"]
        PLUGIN["maya_aceclient Plugin"]
        PLAYER["AceAnimationPlayer Node"]
        BLENDSHAPE["Maya Blendshape Nodes"]
    end
    
    subgraph "Maya-ACE Core Libraries"
        GRPC_CLIENT["gRPC Client Libraries"]
        AUDIO_PROC["AudioFile Processing"]
        CONFIG["Configuration System"]
    end
    
    subgraph "NVIDIA Cloud Services"
        ACE_SERVICE["Audio2Face-3D Service"]
        NVCF["NVIDIA Cloud Functions"]
        NIM["NVIDIA NIM Platform"]
    end
    
    subgraph "Build Infrastructure"
        CMAKE["CMake Build System"]
        PACKMAN["Packman Dependencies"]
        PYTHON_DEPS["Python Dependencies"]
    end
    
    MAYA --> PLUGIN
    PLUGIN --> PLAYER
    PLUGIN --> GRPC_CLIENT
    PLUGIN --> AUDIO_PROC
    PLAYER --> BLENDSHAPE
    
    GRPC_CLIENT --> ACE_SERVICE
    ACE_SERVICE --> NVCF
    NVCF --> NIM
    
    CMAKE --> PLUGIN
    PACKMAN --> CMAKE
    PYTHON_DEPS --> CMAKE
```

This architecture demonstrates the plugin's role as a bridge between Maya's native systems and NVIDIA's cloud-based AI services, using industry-standard gRPC communication protocols.

**Sources:** [README.md:7-16](), [README.md:20-42]()

## Core Components and Integration Points

### Maya Plugin Integration

The `maya_aceclient` plugin integrates with Maya through several key mechanisms:

| Component | Purpose | Maya Integration |
|-----------|---------|------------------|
| `AceAnimationPlayer` | Core animation node | Extends Maya's DG node system |
| gRPC Client | Service communication | Handles external API calls |
| AudioFile Library | Audio processing | Loads and processes audio data |
| Blendshape Connectors | Animation output | Connects to Maya blendshape nodes |

### Service Communication Flow

```mermaid
sequenceDiagram
    participant User
    participant Maya
    participant Plugin as "maya_aceclient"
    participant AudioLib as "AudioFile Library"
    participant gRPC as "gRPC Client"
    participant ACE as "Audio2Face-3D Service"
    participant Blendshape as "Maya Blendshapes"
    
    User->>Maya: "Load maya_aceclient plugin"
    User->>Maya: "Create AceAnimationPlayer node"
    User->>Plugin: "Configure audio file and API key"
    Plugin->>AudioLib: "Load and process audio"
    User->>Plugin: "Click Connect and Send Audio"
    Plugin->>gRPC: "Serialize audio data (Protocol Buffers)"
    gRPC->>ACE: "Send audio via gRPC call"
    ACE-->>gRPC: "Return facial animation data"
    gRPC-->>Plugin: "Deserialize animation frames"
    Plugin->>Blendshape: "Apply animation weights"
    User->>Maya: "Play timeline"
    Blendshape->>Maya: "Display animated character"
```

This sequence illustrates the end-to-end data flow from audio input to character animation, highlighting the plugin's role in orchestrating communication between Maya and NVIDIA's services.

**Sources:** [README.md:22-28](), [README.md:35-38]()

## Development and Deployment Model

### Build System Architecture

Maya-ACE uses a comprehensive build system that manages both C++ and Python dependencies:

```mermaid
graph LR
    subgraph "Development Environment"
        VS["Visual Studio 2019+"]
        PYTHON["Python 3"]
        MAYA_INSTALL["Maya 2024/2025"]
        VSWHERE["vswhere.exe"]
    end
    
    subgraph "Build Process"
        FETCH["fetch_deps.bat"]
        BUILD["build.bat"]
        CMAKE_GEN["CMake Generation"]
        NINJA_BUILD["Ninja Compilation"]
    end
    
    subgraph "Dependencies"
        PACKMAN_DEPS["Packman (C++ libs)"]
        PIP_DEPS["pip (Python libs)"]
        MAYA_SDK["Maya devkitBase"]
    end
    
    subgraph "Output Artifacts"
        PLUGIN_OUT["maya_aceclient.mll"]
        MOD_FILE["mace.mod"]
        TESTS_OUT["Test Executables"]
    end
    
    VS --> BUILD
    PYTHON --> BUILD
    MAYA_INSTALL --> BUILD
    
    BUILD --> FETCH
    FETCH --> CMAKE_GEN
    PACKMAN_DEPS --> CMAKE_GEN
    PIP_DEPS --> CMAKE_GEN
    MAYA_SDK --> CMAKE_GEN
    CMAKE_GEN --> NINJA_BUILD
    
    NINJA_BUILD --> PLUGIN_OUT
    NINJA_BUILD --> MOD_FILE
    NINJA_BUILD --> TESTS_OUT
```

The build system emphasizes reproducibility and cross-platform compatibility while managing complex dependency relationships between Maya SDK, gRPC libraries, and audio processing components.

**Sources:** [README.md:68-71]()

### Licensing and Contribution Model

Maya-ACE operates under an MIT license with a maintainer-led development model. The project encourages forking and adaptation while maintaining centralized development by NVIDIA's team.

| Aspect | Details |
|--------|---------|
| License | MIT License with NVIDIA copyright |
| Contribution Model | Maintainer-led, forks encouraged |
| External Contributions | Not currently accepting direct PRs |
| Support | NVIDIA Enterprise Support for customers |

**Sources:** [LICENSE.txt:1-22](), [CONTRIBUTING.md:1-18](), [README.md:47-50]()

## Integration with NVIDIA Ecosystem

Maya-ACE serves as an entry point into NVIDIA's broader digital human technology ecosystem, providing pathways to more advanced platforms:

- **NVIDIA NIM Platform**: Cloud-based AI inference services
- **Kairos Unreal Engine Integration**: Real-time rendering and interaction
- **Tokkio SDK**: Interactive avatar virtual assistant development
- **ACE Suite**: Comprehensive digital human development tools

This positioning makes Maya-ACE both a standalone tool and a stepping stone for more complex digital human applications.

**Sources:** [README.md:30-34](), [README.md:43-50]()

---

