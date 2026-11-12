<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/Maya-ACE · page 3 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CMakeLists.txt](CMakeLists.txt)
- [README.md](README.md)

</details>



This document provides a comprehensive overview of Maya-ACE's system architecture, including its core components, data flow patterns, and build system organization. It details how the Maya plugin integrates with NVIDIA's Audio2Face-3D service through gRPC communication and how the various subsystems interact to provide audio-driven facial animation capabilities.

For information about building and testing the system, see [Building and Testing](#4.1). For dependency-specific details, see [Dependency Management](#3.2) and [C++ Libraries](#3.3).

## System Overview

Maya-ACE implements a plugin-based architecture that extends Autodesk Maya with cloud-based facial animation capabilities. The system consists of four primary architectural layers: the Maya integration layer, the core client libraries, the network communication layer, and the external service integration.

### High-Level Component Architecture

```mermaid
graph TB
    subgraph MayaEnvironment["Maya Environment"]
        MayaApp["Autodesk Maya 2024/2025"]
        PluginLoader["maya_aceclient Plugin"]
        AceAnimationPlayer["AceAnimationPlayer Node"]
        BlendShapeNode["Character Blendshapes"]
        MayaTimeline["Maya Timeline"]
    end
    
    subgraph CoreLibraries["Core Client Libraries"]
        AceGrpcCpp["ace_grpc_cpp"]
        AceClient["ace_client"]
        AudioFileLib["AudioFile Processing"]
        ConfigSystem["Configuration Management"]
    end
    
    subgraph NetworkLayer["Network Communication"]
        GrpcClient["gRPC Client"]
        ProtobufSerialization["Protocol Buffer Serialization"]
        ApiAuthentication["NVCF API Authentication"]
    end
    
    subgraph ExternalServices["NVIDIA Cloud Services"]
        Audio2Face3D["Audio2Face-3D Service"]
        NvidiaNIM["NVIDIA NIM Platform"]
        NVCF["NVIDIA Cloud Functions"]
    end
    
    MayaApp --> PluginLoader
    PluginLoader --> AceAnimationPlayer
    AceAnimationPlayer --> BlendShapeNode
    BlendShapeNode --> MayaTimeline
    
    AceAnimationPlayer --> AceClient
    AceClient --> AceGrpcCpp
    AceClient --> AudioFileLib
    AceGrpcCpp --> GrpcClient
    
    GrpcClient --> ProtobufSerialization
    GrpcClient --> ApiAuthentication
    ProtobufSerialization --> Audio2Face3D
    ApiAuthentication --> NVCF
    
    Audio2Face3D --> NvidiaNIM
    NVCF --> NvidiaNIM
```

Sources: [CMakeLists.txt:1-27](), [README.md:1-74]()

## Component Architecture

### Maya Plugin Layer

The Maya plugin layer provides the primary user interface and Maya scene integration through native Maya nodes and UI elements.

```mermaid
graph TD
    subgraph MayaPlugin["maya_aceclient Plugin"]
        PluginEntry["Plugin Entry Point"]
        NodeRegistration["Node Registration"]
        MenuSystem["ACE Menu System"]
    end
    
    subgraph MayaNodes["Maya Node System"]
        AceAnimationPlayerNode["AceAnimationPlayer"]
        NodeAttributes["Node Attributes"]
        AttributeEditor["Attribute Editor UI"]
        ConnectButton["Connect and Send Audio Button"]
    end
    
    subgraph MayaIntegration["Maya Scene Integration"]
        BlendShapeConnections["Blendshape Connections"]
        TimelineIntegration["Timeline Integration"]
        SceneGraph["Maya Scene Graph"]
    end
    
    PluginEntry --> NodeRegistration
    NodeRegistration --> AceAnimationPlayerNode
    PluginEntry --> MenuSystem
    
    AceAnimationPlayerNode --> NodeAttributes
    NodeAttributes --> AttributeEditor
    AttributeEditor --> ConnectButton
    
    AceAnimationPlayerNode --> BlendShapeConnections
    BlendShapeConnections --> TimelineIntegration
    TimelineIntegration --> SceneGraph
```

Sources: [CMakeLists.txt:18](), [README.md:35-37]()

### Core Client Libraries

The core libraries handle audio processing, gRPC communication, and service orchestration.

```mermaid
graph TB
    subgraph AceClientLib["ace_client Library"]
        ClientInterface["Client Interface"]
        AudioProcessor["Audio File Processor"]
        ServiceOrchestrator["Service Orchestrator"]
    end
    
    subgraph AceGrpcLib["ace_grpc_cpp Library"]
        GrpcClientImpl["gRPC Client Implementation"]
        ServiceStubs["Generated Service Stubs"]
        MessageHandlers["Protocol Buffer Handlers"]
    end
    
    subgraph AudioProcessing["Audio Processing"]
        AudioFileReader["AudioFile Reader"]
        FormatConverter["Audio Format Converter"]
        StreamProcessor["Audio Stream Processor"]
    end
    
    ClientInterface --> AudioProcessor
    ClientInterface --> ServiceOrchestrator
    ServiceOrchestrator --> GrpcClientImpl
    
    GrpcClientImpl --> ServiceStubs
    GrpcClientImpl --> MessageHandlers
    
    AudioProcessor --> AudioFileReader
    AudioFileReader --> FormatConverter
    FormatConverter --> StreamProcessor
```

Sources: [CMakeLists.txt:14-16](), [README.md:71]()

## Data Flow Architecture

### Audio-to-Animation Pipeline

The following diagram illustrates how audio data flows through the system to generate facial animation data that drives Maya blendshapes.

```mermaid
sequenceDiagram
    participant User as "Maya User"
    participant AcePlayer as "AceAnimationPlayer"
    participant AudioFile as "AudioFile Library"
    participant AceClient as "ace_client"
    participant GrpcClient as "ace_grpc_cpp"
    participant A2F3D as "Audio2Face-3D Service"
    participant BlendShape as "Maya BlendShape Node"
    
    User->>AcePlayer: "Configure audio file path"
    User->>AcePlayer: "Set API key and function ID"
    User->>AcePlayer: "Click Connect and Send Audio"
    
    AcePlayer->>AudioFile: "Load audio file"
    AudioFile-->>AcePlayer: "Return audio data"
    
    AcePlayer->>AceClient: "Process audio request"
    AceClient->>GrpcClient: "Serialize audio via protobuf"
    GrpcClient->>A2F3D: "Send gRPC request"
    
    A2F3D-->>GrpcClient: "Return animation frames"
    GrpcClient-->>AceClient: "Deserialize response"
    AceClient-->>AcePlayer: "Animation weight data"
    
    AcePlayer->>BlendShape: "Apply animation weights"
    User->>AcePlayer: "Play Maya timeline"
    BlendShape->>User: "Display animated character"
```

Sources: [README.md:22-24](), [CMakeLists.txt:14-16]()

### Network Communication Flow

```mermaid
graph LR
    subgraph ClientSide["Client Side"]
        AudioData["Audio Data"]
        ProtobufEncoder["Protocol Buffer Encoder"]
        GrpcChannel["gRPC Channel"]
        AuthHeaders["NVCF Auth Headers"]
    end
    
    subgraph NetworkTransport["Network Transport"]
        HttpsTransport["HTTPS Transport"]
        LoadBalancer["Service Load Balancer"]
    end
    
    subgraph ServiceSide["Service Side"]
        NvcfGateway["NVCF Gateway"]
        A2F3DService["Audio2Face-3D Service"]
        NimPlatform["NIM Platform Runtime"]
    end
    
    AudioData --> ProtobufEncoder
    ProtobufEncoder --> GrpcChannel
    AuthHeaders --> GrpcChannel
    GrpcChannel --> HttpsTransport
    
    HttpsTransport --> LoadBalancer
    LoadBalancer --> NvcfGateway
    NvcfGateway --> A2F3DService
    A2F3DService --> NimPlatform
```

Sources: [README.md:15-16](), [CMakeLists.txt:16-20]()

## Build and Dependency Architecture

### CMake Build System Organization

The build system uses CMake with modular find packages and a hierarchical source organization.

```mermaid
graph TD
    subgraph BuildSystem["Build System"]
        RootCMake["CMakeLists.txt (root)"]
        CompilerSettings["compiler_settings.cmake"]
        FindModules["cmake/modules/ Find*.cmake"]
        VersionConfig["source/VERSION.md"]
    end
    
    subgraph Dependencies["External Dependencies"]
        PackmanDeps["Packman Dependencies"]
        AbslDep["find_package(Absl)"]
        AudiofileDep["find_package(Audiofile)"]
        GrpcDep["find_package(Grpc)"]
        GtestDep["find_package(Gtest)"]
        MayaDep["find_package(Maya)"]
        OpensslDep["find_package(Openssl)"]
        ProtobufDep["find_package(Protobuf)"]
        PythonDepsDep["find_package(PythonDeps)"]
    end
    
    subgraph SourceTargets["Source Targets"]
        SourceDir["add_subdirectory(source)"]
        TestsDir["add_subdirectory(tests)"]
        OutputPlugin["plugins/mace.mod"]
    end
    
    RootCMake --> CompilerSettings
    RootCMake --> FindModules
    RootCMake --> VersionConfig
    
    FindModules --> AbslDep
    FindModules --> AudiofileDep
    FindModules --> GrpcDep
    FindModules --> GtestDep
    FindModules --> MayaDep
    FindModules --> OpensslDep
    FindModules --> ProtobufDep
    FindModules --> PythonDepsDep
    
    PackmanDeps --> AbslDep
    PackmanDeps --> AudiofileDep
    PackmanDeps --> GrpcDep
    
    RootCMake --> SourceDir
    RootCMake --> TestsDir
    VersionConfig --> OutputPlugin
```

Sources: [CMakeLists.txt:1-27]()

### Dependency Resolution Chain

```mermaid
graph TB
    subgraph PackmanManaged["Packman-Managed Dependencies"]
        GrpcPackman["gRPC Framework"]
        ProtobufPackman["Protocol Buffers"]
        OpensslPackman["OpenSSL"]
        AbslPackman["Abseil C++"]
        ZlibPackman["Zlib"]
        Re2Packman["RE2 Regex"]
        CaresPackman["c-ares DNS"]
        AudioFilePackman["AudioFile Library"]
        GtestPackman["Google Test"]
    end
    
    subgraph SystemDependencies["System Dependencies"]
        MayaDevkit["Maya devkitBase"]
        VisualStudio["Visual Studio 2019+"]
        WindowsSDK["Windows SDK"]
    end
    
    subgraph PythonDependencies["Python Dependencies"]
        GrpcPython["grpcio"]
        GrpcToolsPython["grpcio-tools"]
        NumpyPython["numpy"]
        PyYamlPython["PyYAML"]
    end
    
    GrpcPackman --> ProtobufPackman
    GrpcPackman --> OpensslPackman
    GrpcPackman --> AbslPackman
    GrpcPackman --> ZlibPackman
    GrpcPackman --> Re2Packman
    GrpcPackman --> CaresPackman
    
    MayaDevkit --> VisualStudio
    VisualStudio --> WindowsSDK
    
    GrpcPython --> GrpcToolsPython
    GrpcPython --> NumpyPython
```

Sources: [CMakeLists.txt:13-23]()

---

