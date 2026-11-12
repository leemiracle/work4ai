<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/ai2thor · page 1 AI2-THOR Overview · fetched 2026-10-30 -->

# AI2-THOR Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [WEBGL.md](WEBGL.md)
- [ai2thor/__init__.py](ai2thor/__init__.py)
- [ai2thor/build.py](ai2thor/build.py)
- [ai2thor/controller.py](ai2thor/controller.py)
- [ai2thor/docker.py](ai2thor/docker.py)
- [ai2thor/downloader.py](ai2thor/downloader.py)
- [ai2thor/fifo_server.py](ai2thor/fifo_server.py)
- [ai2thor/platform.py](ai2thor/platform.py)
- [ai2thor/server.py](ai2thor/server.py)
- [ai2thor/tests/build_controller.py](ai2thor/tests/build_controller.py)
- [ai2thor/tests/constants.py](ai2thor/tests/constants.py)
- [ai2thor/tests/data/arm/new/pickup_object.json](ai2thor/tests/data/arm/new/pickup_object.json)
- [ai2thor/tests/data/image-depth-data256.raw](ai2thor/tests/data/image-depth-data256.raw)
- [ai2thor/tests/data/image-depth-datafloat32.raw](ai2thor/tests/data/image-depth-datafloat32.raw)
- [ai2thor/tests/fifo_client.py](ai2thor/tests/fifo_client.py)
- [ai2thor/tests/test_controller.py](ai2thor/tests/test_controller.py)
- [ai2thor/tests/test_event.py](ai2thor/tests/test_event.py)
- [ai2thor/tests/test_fifo_server.py](ai2thor/tests/test_fifo_server.py)
- [ai2thor/tests/test_server.py](ai2thor/tests/test_server.py)
- [ai2thor/tests/test_unity.py](ai2thor/tests/test_unity.py)
- [ai2thor/wsgi_server.py](ai2thor/wsgi_server.py)
- [doc/static/ReleaseNotes/Cook.png](doc/static/ReleaseNotes/Cook.png)
- [doc/static/ReleaseNotes/Dirty.png](doc/static/ReleaseNotes/Dirty.png)
- [doc/static/ReleaseNotes/Fill.png](doc/static/ReleaseNotes/Fill.png)
- [doc/static/ReleaseNotes/Moveable.png](doc/static/ReleaseNotes/Moveable.png)
- [doc/static/ReleaseNotes/ReleaseNotes_2.4.md](doc/static/ReleaseNotes/ReleaseNotes_2.4.md)
- [doc/static/ReleaseNotes/Slice.png](doc/static/ReleaseNotes/Slice.png)
- [doc/static/ReleaseNotes/UseUp.png](doc/static/ReleaseNotes/UseUp.png)
- [start.sh](start.sh)
- [tasks.py](tasks.py)
- [unity/Assets/Editor/Build.cs](unity/Assets/Editor/Build.cs)
- [unity/Assets/Physics/SimObjsPhysics/RoboTHOR Objects/RoboTHOR_Assets_SmallObjects/Target_SmallObjects/SprayBottle/Materials.meta](unity/Assets/Physics/SimObjsPhysics/RoboTHOR Objects/RoboTHOR_Assets_SmallObjects/Target_SmallObjects/SprayBottle/Materials.meta)
- [unity/Assets/Resources/MagicMirror/Prefab/MirrorMaterial.mat](unity/Assets/Resources/MagicMirror/Prefab/MirrorMaterial.mat)
- [unity/Assets/Scripts/FifoServer.cs](unity/Assets/Scripts/FifoServer.cs)
- [unity/Assets/Scripts/ImageSynthesis/ImageSynthesis.cs](unity/Assets/Scripts/ImageSynthesis/ImageSynthesis.cs)
- [unity/Assets/Scripts/ImageSynthesis/Shaders/Depth.shader](unity/Assets/Scripts/ImageSynthesis/Shaders/Depth.shader)
- [unity/ProjectSettings/GraphicsSettings.asset](unity/ProjectSettings/GraphicsSettings.asset)

</details>



## Purpose and Scope

AI2-THOR is a near photo-realistic interactable framework for embodied AI agents. This document provides an overview of the core system architecture, communication protocols, and key components that enable researchers to create and control AI agents in 3D simulated environments. 

For detailed information about specific agent types and their capabilities, see [Specialized Agent Types](#5). For scene management and procedural generation, see [Scenes and Environments](#6). For object interaction systems, see [Object Interaction System](#7).

## High-Level System Architecture

AI2-THOR operates as a client-server architecture where Python clients communicate with a Unity simulation backend through multiple communication protocols.

```mermaid
graph TB
    subgraph "Python Client Layer"
        Controller["ai2thor.controller.Controller"]
        BuildSystem["Build System (tasks.py)"]
        Platform["Platform Management"]
    end
    
    subgraph "Communication Layer"
        FifoServer["ai2thor.fifo_server.FifoServer"]
        WsgiServer["ai2thor.wsgi_server.WsgiServer"]
        WebGL["WebGL Interface"]
    end
    
    subgraph "Unity Simulation Backend"
        AgentManager["AgentManager.cs"]
        ImageSynth["ImageSynthesis.cs"]
        FifoServerCS["FifoServer.cs"]
        BuildCS["Build.cs"]
    end
    
    subgraph "Scene & Content"
        Scenes["FloorPlan Scenes"]
        SimObjects["SimObjPhysics Objects"]
        ProceduralGen["Procedural Generation"]
    end
    
    Controller --> FifoServer
    Controller --> WsgiServer
    BuildSystem --> BuildCS
    Platform --> Controller
    
    FifoServer --> FifoServerCS
    WsgiServer --> AgentManager
    WebGL --> AgentManager
    
    AgentManager --> ImageSynth
    AgentManager --> Scenes
    AgentManager --> SimObjects
    
    ProceduralGen --> Scenes
```

**Sources:** [ai2thor/controller.py:1-50](), [tasks.py:1-100](), [unity/Assets/Scripts/AgentManager.cs](), [unity/Assets/Scripts/ImageSynthesis/ImageSynthesis.cs:1-50]()

## Core Python Controller

The `Controller` class serves as the primary entry point for interacting with AI2-THOR simulations. It manages the lifecycle of Unity processes, handles build downloads, and provides the main API for sending actions and receiving observations.

```mermaid
graph LR
    Controller["Controller.__init__()"]
    BuildManager["Build Management"]
    ServerFactory["Server Factory"]
    EventLoop["Step/Receive Loop"]
    
    Controller --> BuildManager
    Controller --> ServerFactory
    Controller --> EventLoop
    
    subgraph "Build Management"
        FindBuild["find_build()"]
        DownloadBuild["Build.download()"]
        ValidatePlatform["Platform.validate()"]
    end
    
    subgraph "Server Types"
        FifoChoice["FifoServer"]
        WsgiChoice["WsgiServer"]
    end
    
    subgraph "Action Processing"
        StepMethod["step()"]
        ResetMethod["reset()"]
        ReceiveEvent["receive Event"]
    end
    
    BuildManager --> FindBuild
    BuildManager --> DownloadBuild
    BuildManager --> ValidatePlatform
    
    ServerFactory --> FifoChoice
    ServerFactory --> WsgiChoice
    
    EventLoop --> StepMethod
    EventLoop --> ResetMethod
    EventLoop --> ReceiveEvent
```

The controller initialization process involves several key phases:

| Phase | Components | Key Classes |
|-------|------------|-------------|
| Platform Detection | `ai2thor.platform` | `Linux64`, `OSXIntel64`, `CloudRendering` |
| Build Management | `ai2thor.build` | `Build`, `EditorBuild`, `ExternalBuild` |
| Server Selection | Communication protocols | `FifoServer`, `WsgiServer` |
| Unity Process | Process management | `subprocess.Popen` |

**Sources:** [ai2thor/controller.py:372-627](), [ai2thor/build.py:110-248](), [ai2thor/platform.py:1-236]()

## Communication Architecture

AI2-THOR supports multiple communication protocols between the Python client and Unity backend, each optimized for different use cases.

```mermaid
graph TB
    subgraph "Python Client"
        ControllerAPI["Controller.step()"]
        ActionDict["action: dict"]
    end
    
    subgraph "Communication Protocols"
        FifoProtocol["FIFO Named Pipes"]
        WsgiProtocol["HTTP/WSGI"]
        WebGLProtocol["WebGL/JavaScript"]
    end
    
    subgraph "Message Serialization"
        MsgPack["MessagePack (FIFO)"]
        JSON["JSON (WSGI/WebGL)"]
        MultipartForm["Multipart Form Data"]
    end
    
    subgraph "Unity Backend"
        FifoServerCS["FifoServer.cs"]
        AgentManagerCS["AgentManager.cs"]
        ActionDispatcher["ActionDispatcher"]
    end
    
    subgraph "Response Data"
        Metadata["Event Metadata"]
        ImageData["RGB/Depth/Segmentation"]
        ObjectStates["Object States"]
    end
    
    ControllerAPI --> ActionDict
    ActionDict --> FifoProtocol
    ActionDict --> WsgiProtocol
    
    FifoProtocol --> MsgPack
    WsgiProtocol --> JSON
    WsgiProtocol --> MultipartForm
    
    MsgPack --> FifoServerCS
    JSON --> AgentManagerCS
    MultipartForm --> AgentManagerCS
    
    FifoServerCS --> ActionDispatcher
    AgentManagerCS --> ActionDispatcher
    
    ActionDispatcher --> Metadata
    ActionDispatcher --> ImageData
    ActionDispatcher --> ObjectStates
```

### FIFO Server Communication

The FIFO server uses named pipes for high-performance local communication:

```mermaid
graph LR
    subgraph "Python FIFO Client"
        FifoClient["FifoServer.__init__()"]
        SendAction["_send_message()"]
        ReceiveResp["_recv_message()"]
    end
    
    subgraph "Message Structure"
        Header["FieldType + Length"]
        Body["MessagePack Data"]
        EOM["END_OF_MESSAGE"]
    end
    
    subgraph "Unity FIFO Server"
        UnityFifo["FifoServer.cs"]
        FieldTypes["FieldType Enum"]
        ImageData["Image Data Streams"]
    end
    
    FifoClient --> SendAction
    SendAction --> Header
    Header --> Body
    Body --> EOM
    
    EOM --> UnityFifo
    UnityFifo --> FieldTypes
    FieldTypes --> ImageData
    
    ImageData --> ReceiveResp
    ReceiveResp --> FifoClient
```

**Sources:** [ai2thor/fifo_server.py:56-318](), [unity/Assets/Scripts/FifoServer.cs:1-50](), [ai2thor/fifo_server.py:26-46]()

## Build and Deployment System

The build system manages Unity compilation, asset bundling, and distribution across multiple platforms.

```mermaid
graph TB
    subgraph "Build Orchestration"
        TasksPy["tasks.py"]
        InvokeTasks["Invoke Tasks"]
        BuildCommand["inv local-build"]
    end
    
    subgraph "Unity Build Process"
        BuildCS["Build.cs"]
        UnityEditor["Unity Editor API"]
        BuildPipeline["BuildPipeline.BuildPlayer()"]
    end
    
    subgraph "Platform Targets"
        OSX["OSXIntel64"]
        Linux["Linux64"]
        Windows["StandaloneWindows64"]
        WebGLBuild["WebGL"]
        CloudRender["CloudRendering"]
    end
    
    subgraph "Distribution"
        S3Upload["S3 Upload"]
        PipPackage["PyPI Package"]
        Downloader["ai2thor.downloader"]
    end
    
    TasksPy --> InvokeTasks
    InvokeTasks --> BuildCommand
    BuildCommand --> BuildCS
    
    BuildCS --> UnityEditor
    UnityEditor --> BuildPipeline
    
    BuildPipeline --> OSX
    BuildPipeline --> Linux
    BuildPipeline --> Windows
    BuildPipeline --> WebGLBuild
    BuildPipeline --> CloudRender
    
    OSX --> S3Upload
    Linux --> S3Upload
    S3Upload --> PipPackage
    PipPackage --> Downloader
```

The build system supports environment-driven configuration:

| Environment Variable | Purpose | Code Reference |
|---------------------|---------|----------------|
| `BUILD_SCENES` | Scene selection | [unity/Assets/Editor/Build.cs:190-204]() |
| `INCLUDE_PRIVATE_SCENES` | Private content | [unity/Assets/Editor/Build.cs:224-227]() |
| `BUILD_SCRIPTS_ONLY` | Development builds | [unity/Assets/Editor/Build.cs:219-222]() |
| `UNITY_BUILD_NAME` | Output naming | [unity/Assets/Editor/Build.cs:43-46]() |

**Sources:** [tasks.py:193-250](), [unity/Assets/Editor/Build.cs:83-128](), [ai2thor/build.py:110-248]()

## Event and Observation System

AI2-THOR's observation system provides rich sensory data through the `Event` class, which encapsulates all simulation state and sensor outputs.

```mermaid
graph TB
    subgraph "Event Creation"
        ServerReceive["Server.receive()"]
        CreateEvent["create_event()"]
        MetadataWrapper["MetadataWrapper"]
    end
    
    subgraph "Event Components"
        EventClass["ai2thor.server.Event"]
        Metadata["metadata: dict"]
        Frame["frame: np.ndarray"]
        DepthFrame["depth_frame: np.ndarray"]
        SegFrames["segmentation_frames"]
    end
    
    subgraph "Image Processing"
        ImageSynth["ImageSynthesis.cs"]
        DepthShader["Depth.shader"]
        SegmentationShader["UberReplacement"]
        InstanceMasks["LazyInstanceSegmentationMasks"]
    end
    
    subgraph "Object Detection"
        BoundingBoxes["LazyInstanceDetections2D"]
        ClassDetections["LazyClassDetections2D"]
        VisibilityMasks["Visibility Processing"]
    end
    
    ServerReceive --> CreateEvent
    CreateEvent --> MetadataWrapper
    MetadataWrapper --> EventClass
    
    EventClass --> Metadata
    EventClass --> Frame
    EventClass --> DepthFrame
    EventClass --> SegFrames
    
    ImageSynth --> Frame
    DepthShader --> DepthFrame
    SegmentationShader --> SegFrames
    SegFrames --> InstanceMasks
    
    InstanceMasks --> BoundingBoxes
    InstanceMasks --> ClassDetections
    BoundingBoxes --> VisibilityMasks
```

**Sources:** [ai2thor/server.py:427-522](), [unity/Assets/Scripts/ImageSynthesis/ImageSynthesis.cs:20-143](), [ai2thor/server.py:59-331]()

## Platform and Dependencies

AI2-THOR adapts to different operating systems and hardware configurations through its platform abstraction layer.

```mermaid
graph LR
    subgraph "Platform Detection"
        PlatformSystem["platform.system()"]
        RequestObj["Request(system, width, height)"]
    end
    
    subgraph "Platform Classes"
        Linux64["Linux64.validate()"]
        OSXIntel64["OSXIntel64.validate()"]
        CloudRendering["CloudRendering.validate()"]
        Windows["StandaloneWindows64"]
    end
    
    subgraph "Validation Checks"
        XDisplayCheck["X11 Display Validation"]
        VulkanCheck["Vulkan Driver Check"]
        GLXExtension["GLX Extension Check"]
    end
    
    subgraph "Environment Setup"
        LaunchEnv["Platform.launch_env()"]
        DisplayEnv["DISPLAY variable"]
        ExecutablePath["executable_path()"]
    end
    
    PlatformSystem --> RequestObj
    RequestObj --> Linux64
    RequestObj --> OSXIntel64
    RequestObj --> CloudRendering
    
    Linux64 --> XDisplayCheck
    Linux64 --> GLXExtension
    CloudRendering --> VulkanCheck
    
    XDisplayCheck --> LaunchEnv
    VulkanCheck --> LaunchEnv
    LaunchEnv --> DisplayEnv
    LaunchEnv --> ExecutablePath
```

**Sources:** [ai2thor/platform.py:214-227](), [ai2thor/platform.py:150-160](), [ai2thor/platform.py:185-202]()

## Summary

AI2-THOR provides a comprehensive framework for embodied AI research through:

- **Unified Python API**: The `Controller` class abstracts platform differences and communication protocols
- **Multi-protocol Communication**: FIFO pipes for performance, WSGI for compatibility, WebGL for web deployment  
- **Automated Build System**: Cross-platform Unity builds with automated distribution
- **Rich Observation Space**: RGB, depth, segmentation, and structured metadata
- **Platform Flexibility**: Support for Linux, macOS, Windows, and cloud rendering

The system is designed for both local development and large-scale distributed training, with extensive testing and validation frameworks to ensure reliability across different hardware configurations.

**Sources:** [README.md:1-312](), [ai2thor/__init__.py:1-8](), [ai2thor/controller.py:1-100]()

---

