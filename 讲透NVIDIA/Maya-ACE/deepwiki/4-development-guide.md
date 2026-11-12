<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/Maya-ACE · page 4 Development Guide · fetched 2026-10-26 -->

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/bestpractices.md](docs/bestpractices.md)
- [docs/buildandtest.md](docs/buildandtest.md)

</details>



This document provides a comprehensive guide for developers working with or extending Maya-ACE. It covers the development environment setup, core workflows, key code components, and testing strategies needed to effectively develop and maintain the Maya-ACE plugin system.

This guide focuses on the development aspects of Maya-ACE. For detailed build instructions and testing procedures, see [Building and Testing](#4.1). For recommended workflows and animation techniques, see [Best Practices](#4.2). For code formatting and style guidelines, see [Code Standards](#4.3).

## Development Environment Overview

Maya-ACE requires a comprehensive development environment that includes Maya SDK integration, C++ build tools, Python environment, and external service connectivity. The development setup supports both the Maya plugin development and the underlying ACE client library development.

### Development Environment Architecture

```mermaid
graph TB
    subgraph "Development Tools"
        VS["Visual Studio 2019+"]
        PYTHON["Python 3"]
        VSWHERE["vswhere.exe"]
        MAYAINSTALL["Maya 2024/2025 Installation"]
    end
    
    subgraph "Environment Variables"
        MAYA_LOCATION["MAYA_LOCATION"]
        PATH_ENV["PATH Environment"]
    end
    
    subgraph "Dependencies Location"
        DEVKIT["deps/devkitBase/"]
        PACKMAN_DEPS["Packman Dependencies"]
        PIP_DEPS["Python pip packages"]
    end
    
    subgraph "Build Scripts"
        FETCH_DEPS["fetch_deps.bat"]
        BUILD_BAT["build.bat"]
        CMAKE_SYSTEM["CMake Build System"]
    end
    
    subgraph "Output Directories"
        BUILD_DIR["_build/windows-x86_64/release/"]
        DEBUG_DIR["_build/windows-x86_64/debug/"]
    end
    
    VS --> BUILD_BAT
    PYTHON --> BUILD_BAT  
    MAYA_LOCATION --> MAYAINSTALL
    PATH_ENV --> VS
    PATH_ENV --> PYTHON
    
    BUILD_BAT --> FETCH_DEPS
    FETCH_DEPS --> DEVKIT
    FETCH_DEPS --> PACKMAN_DEPS
    FETCH_DEPS --> PIP_DEPS
    
    CMAKE_SYSTEM --> BUILD_DIR
    CMAKE_SYSTEM --> DEBUG_DIR
```

Sources: [docs/buildandtest.md:5-30]()

## Core Development Workflows

The Maya-ACE development process follows several key workflows depending on the type of development work being performed. Understanding these workflows is essential for efficient development.

### Primary Development Workflow

```mermaid
sequenceDiagram
    participant Dev as "Developer"
    participant Env as "Development Environment"
    participant Build as "Build System"
    participant Maya as "Maya Instance"
    participant Tests as "Test Suite"
    participant ACE as "ACE Service"
    
    Dev->>Env: "Set MAYA_LOCATION environment"
    Dev->>Build: "fetch_deps.bat"
    Build->>Env: "Download Packman dependencies"
    Build->>Env: "Install pip packages"
    
    Dev->>Build: "build.bat mace"
    Build->>Build: "CMake generation"
    Build->>Build: "Ninja compilation"
    Build->>Env: "Generate maya_aceclient.mll"
    
    Dev->>Tests: "test_maya.bat"
    Tests->>Maya: "Launch mayapy with plugin"
    Tests->>Tests: "Run unit tests"
    
    Dev->>Maya: "run_maya.bat"
    Maya->>Env: "Load plugin for testing"
    
    Dev->>ACE: "run_mock_server.bat"
    ACE->>Tests: "Provide mock ACE service"
```

Sources: [docs/buildandtest.md:33-81]()

## Key Code Components

Maya-ACE consists of several key code components that developers need to understand. These components work together to provide the complete plugin functionality within Maya's architecture.

### Core Component Architecture

```mermaid
graph TB
    subgraph "Maya Plugin Layer"
        MAYA_PLUGIN["maya_aceclient Plugin (.mll)"]
        ACE_ANIMATION_PLAYER["AceAnimationPlayer Node"]
        MAYA_COMMANDS["Maya MEL/Python Commands"]
    end
    
    subgraph "ACE Client Library"
        ACE_CLIENT["ACE Client Library (Static)"]
        GRPC_CPP["ace_grpc_cpp Library"]
        AUDIO_PROCESSOR["Audio File Processor"]
    end
    
    subgraph "Build Artifacts"
        SOURCE_DIR["source/ directory"]
        TESTS_DIR["tests/ directory"]
        CMAKE_FILES["CMakeLists.txt files"]
    end
    
    subgraph "Generated Files"
        GRPC_GENERATED["gRPC Generated C++ Files"]
        PROTOBUF_FILES["Protocol Buffer Definitions"]
        MOD_FILE["mace.mod Module File"]
    end
    
    subgraph "Test Infrastructure"
        MAYA_TESTS["Maya Plugin Tests"]
        CLIENT_TESTS["ACE Client Tests"]
        MOCK_SERVER["Mock ACE Server"]
    end
    
    MAYA_PLUGIN --> ACE_ANIMATION_PLAYER
    MAYA_PLUGIN --> MAYA_COMMANDS
    ACE_ANIMATION_PLAYER --> ACE_CLIENT
    ACE_CLIENT --> GRPC_CPP
    ACE_CLIENT --> AUDIO_PROCESSOR
    
    SOURCE_DIR --> MAYA_PLUGIN
    SOURCE_DIR --> ACE_CLIENT
    CMAKE_FILES --> MAYA_PLUGIN
    CMAKE_FILES --> ACE_CLIENT
    
    GRPC_GENERATED --> GRPC_CPP
    PROTOBUF_FILES --> GRPC_GENERATED
    
    TESTS_DIR --> MAYA_TESTS
    TESTS_DIR --> CLIENT_TESTS
    MOCK_SERVER --> CLIENT_TESTS
```

Sources: [docs/buildandtest.md:31-97]()

## Testing Strategy

Maya-ACE implements a comprehensive testing strategy that covers both the Maya plugin functionality and the underlying ACE client library. The testing approach supports both unit testing and integration testing with mock services.

### Testing Component Flow

```mermaid
graph LR
    subgraph "Test Execution Scripts"
        TEST_MAYA["test_maya.bat"]
        TEST_CLIENT["test_aceclient.bat"]
        RUN_MOCK["run_mock_server.bat"]
    end
    
    subgraph "Test Environments"
        MAYAPY["mayapy Environment"]
        PYTHON_ENV["Python Test Environment"]
        MOCK_ACE["Mock ACE Server"]
    end
    
    subgraph "Test Suites"
        MAYA_UNIT_TESTS["Maya Plugin Unit Tests"]
        CLIENT_UNIT_TESTS["ACE Client Unit Tests"]
        INTEGRATION_TESTS["Integration Tests"]
    end
    
    subgraph "Test Dependencies"
        BUILT_PLUGIN["Built maya_aceclient.mll"]
        BUILT_CLIENT["Built ACE Client Library"]
        PIP_PACKAGES["Python Test Packages"]
    end
    
    TEST_MAYA --> MAYAPY
    TEST_CLIENT --> PYTHON_ENV
    RUN_MOCK --> MOCK_ACE
    
    MAYAPY --> MAYA_UNIT_TESTS
    PYTHON_ENV --> CLIENT_UNIT_TESTS
    MOCK_ACE --> INTEGRATION_TESTS
    
    MAYA_UNIT_TESTS --> BUILT_PLUGIN
    CLIENT_UNIT_TESTS --> BUILT_CLIENT
    INTEGRATION_TESTS --> PIP_PACKAGES
```

Sources: [docs/buildandtest.md:44-81](), [docs/buildandtest.md:87-97]()

## Development Workflow Implementation

The iterative development workflow for Maya-ACE follows a parameter-tuning approach that requires multiple iterations to achieve optimal results. This workflow is central to how developers and users interact with the system.

### Parameter Tuning and Animation Workflow

```mermaid
sequenceDiagram
    participant Dev as "Developer/User"
    participant UI as "Maya UI"
    participant Player as "AceAnimationPlayer"
    participant Service as "ACE Service"
    participant Blendshape as "Character Blendshapes"
    participant Timeline as "Maya Timeline"
    
    loop "Iterative Parameter Tuning"
        Dev->>Player: "Adjust Parameters"
        Dev->>UI: "Click Connect and Send Audio"
        UI->>Player: "Trigger animation update"
        Player->>Service: "Send audio with parameters"
        Service-->>Player: "Return facial animation data"
        Player->>Blendshape: "Apply animation weights"
        Dev->>Timeline: "Play scene and check animation"
        
        alt "Satisfied with result"
            Dev->>UI: "Bake Simulation"
            UI->>Blendshape: "Freeze animation keyframes"
            Dev->>UI: "Save scene"
        else "Need adjustments"
            Note over Dev: "Return to parameter adjustment"
        end
    end
```

Sources: [docs/bestpractices.md:3-14]()

## Blendshape Connection System

Maya-ACE implements a sophisticated blendshape connection system that supports both complete ARKit blendshape sets and partial/custom blendshape configurations. This system is crucial for developers working with different character rigs.

### Blendshape Matching and Connection Process

| Component | Function | ARKit Compliance |
|-----------|----------|------------------|
| `AceAnimationPlayer` | Manages 52 blendshape outputs | Full ARKit BlendShape Locations |
| `Output Weights` | Dynamic blendshape name updates | Case-insensitive matching |
| `Connect existing Animation Player` | Name-based connection system | Partial set support |
| `Blendshape Node` | Target Maya blendshape deformers | User-defined naming |

The connection process follows these rules:
- Blendshape names must correspond to ARKit face locations
- Names are matched case-insensitively  
- Partial blendshape sets are supported through name-based matching
- The `AceAnimationPlayer` automatically updates its output weights based on received animations

Sources: [docs/bestpractices.md:33-54]()

## Quick Start for Developers

For developers new to Maya-ACE, follow this sequence to get started:

1. **Environment Setup**: Install Visual Studio 2019+, Python 3, and Maya 2024/2025
2. **Maya SDK**: Download and place Maya devkitBase in `deps/devkitBase/`
3. **Environment Variables**: Set `MAYA_LOCATION` to Maya installation directory
4. **Dependencies**: Run `fetch_deps.bat` to download all required dependencies
5. **Build**: Execute `build.bat mace` to compile the plugin
6. **Test**: Run `test_maya.bat` to verify the build works correctly
7. **Development**: Use `run_maya.bat` to launch Maya with the plugin loaded

For detailed instructions on each step, see [Building and Testing](#4.1).

For recommended development workflows and animation optimization techniques, see [Best Practices](#4.2).

For code formatting standards and development environment configuration, see [Code Standards](#4.3).

## Related Resources

- **Architecture Overview**: For system architecture details, see [Architecture](#3)
- **Build System Details**: For CMake configuration and build scripts, see [Build System](#3.1)  
- **Dependency Management**: For Packman and pip dependency details, see [Dependency Management](#3.2)
- **Audio Specifications**: For technical audio requirements, see [Audio Specifications](#5.1)
- **Sample Projects**: For example implementations, see [Sample Projects](#5.2)

Sources: [docs/buildandtest.md:1-97](), [docs/bestpractices.md:1-54]()

---

