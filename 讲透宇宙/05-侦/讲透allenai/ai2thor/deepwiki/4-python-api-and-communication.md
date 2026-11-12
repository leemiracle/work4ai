<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/ai2thor · page 4 Python API and Communication · fetched 2026-10-30 -->

# Python API and Communication

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [Dockerfile](Dockerfile)
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



This document covers the Python API layer and communication systems that enable interaction between Python client code and the Unity simulation engine in AI2-THOR. This includes the primary `Controller` class, server communication protocols, build automation, and data exchange mechanisms.

For information about specialized agent types and their controllers, see [Specialized Agent Types](#5). For details about Unity project configuration and scene management, see [Unity Project Configuration](#11) and [Scenes and Environments](#6).

## Architecture Overview

The Python API and communication system forms the bridge between Python client applications and the Unity simulation engine through multiple communication protocols and build management systems.

```mermaid
graph TB
    subgraph "Python Client Layer"
        CTRL["ai2thor.controller.Controller"]
        API_INIT["Initialization Parameters"]
        API_ACTIONS["Action Methods"]
    end
    
    subgraph "Communication Protocols"
        WSGI["ai2thor.wsgi_server.WsgiServer"]
        FIFO["ai2thor.fifo_server.FifoServer"]
        SERVER_BASE["ai2thor.server.Server"]
    end
    
    subgraph "Build & Deployment"
        TASKS["tasks.py"]
        BUILD_PY["ai2thor.build.Build"]
        DOWNLOADER["ai2thor.downloader"]
        PLATFORM["ai2thor.platform"]
    end
    
    subgraph "Unity Engine Layer"
        UNITY_FIFO["FifoServer.cs"]
        UNITY_WSGI["WSGI Endpoint"]
        IMAGE_SYNTH["ImageSynthesis.cs"]
        BUILD_CS["Build.cs"]
    end
    
    subgraph "Data Exchange"
        EVENT["server.Event"]
        METADATA["MetadataWrapper"]
        IMAGES["Image Data"]
        ACTIONS_JSON["JSON Actions"]
    end
    
    CTRL --> WSGI
    CTRL --> FIFO
    WSGI --> SERVER_BASE
    FIFO --> SERVER_BASE
    
    SERVER_BASE --> EVENT
    EVENT --> METADATA
    EVENT --> IMAGES
    
    WSGI --> UNITY_WSGI
    FIFO --> UNITY_FIFO
    
    TASKS --> BUILD_PY
    BUILD_PY --> DOWNLOADER
    BUILD_PY --> PLATFORM
    
    TASKS --> BUILD_CS
    BUILD_CS --> UNITY_WSGI
    BUILD_CS --> UNITY_FIFO
    
    UNITY_FIFO --> IMAGE_SYNTH
    UNITY_WSGI --> IMAGE_SYNTH
    
    CTRL --> ACTIONS_JSON
    ACTIONS_JSON --> UNITY_FIFO
    ACTIONS_JSON --> UNITY_WSGI
```

Sources: [ai2thor/controller.py:1-1000](), [ai2thor/server.py:1-100](), [ai2thor/wsgi_server.py:1-100](), [ai2thor/fifo_server.py:1-100]()

## Controller Class - Main Python API

The `Controller` class in `ai2thor.controller` serves as the primary entry point for all Python interactions with AI2-THOR. It manages initialization, communication protocols, build selection, and action execution.

```mermaid
graph TB
    subgraph "Controller Initialization"
        INIT["Controller.__init__()"]
        BUILD_FIND["find_build()"]
        SERVER_BUILD["_build_server()"]
        START["start()"]
    end
    
    subgraph "Core Controller Methods"
        STEP["step(action)"]
        RESET["reset(scene)"]
        STOP["stop()"]
        INTERACT["interact()"]
    end
    
    subgraph "Build Management"
        BUILD_CLASS["ai2thor.build.Build"]
        BUILD_EDITOR["EditorBuild"]
        BUILD_EXTERNAL["ExternalBuild"]
        DOWNLOAD["download()"]
    end
    
    subgraph "Server Selection"
        WSGI_SERVER["WsgiServer"]
        FIFO_SERVER["FifoServer"]
        SERVER_CLASS["server_class"]
    end
    
    INIT --> BUILD_FIND
    BUILD_FIND --> BUILD_CLASS
    BUILD_FIND --> BUILD_EDITOR
    BUILD_FIND --> BUILD_EXTERNAL
    
    INIT --> SERVER_BUILD
    SERVER_BUILD --> WSGI_SERVER
    SERVER_BUILD --> FIFO_SERVER
    
    BUILD_CLASS --> DOWNLOAD
    
    STEP --> SERVER_CLASS
    RESET --> SERVER_CLASS
    
    INIT --> START
    START --> STEP
```

The `Controller` class handles several key responsibilities:

| Component | Purpose | Key Methods |
|-----------|---------|-------------|
| Initialization | Set up communication and build | `__init__`, `start()` |
| Action Execution | Send actions to Unity | `step()`, `multi_step_physics()` |
| Scene Management | Load and reset scenes | `reset()`, `normalize_scene()` |
| Build Management | Handle Unity builds | `find_build()`, `prune_releases()` |
| Server Communication | Manage protocol selection | `_build_server()`, `server_type_to_class()` |

Sources: [ai2thor/controller.py:372-627](), [ai2thor/controller.py:689-774](), [ai2thor/controller.py:776-796]()

## Communication Protocols

AI2-THOR supports two primary communication protocols between Python and Unity: WSGI (HTTP-based) and FIFO (named pipes). The choice depends on platform compatibility and performance requirements.

### Protocol Architecture

```mermaid
graph LR
    subgraph "Python Side"
        CTRL_SEND["controller.step(action)"]
        CTRL_RECV["controller.receive()"]
    end
    
    subgraph "WSGI Protocol"
        WSGI_SEND["WsgiServer.send()"]
        WSGI_RECV["WsgiServer.receive()"]
        FLASK["Flask App"]
        HTTP_ENDPOINT["/train endpoint"]
    end
    
    subgraph "FIFO Protocol"
        FIFO_SEND["FifoServer.send()"]
        FIFO_RECV["FifoServer.receive()"]
        NAMED_PIPES["Named Pipes"]
        MSGPACK["MessagePack"]
    end
    
    subgraph "Unity Side"
        UNITY_HTTP["HTTP Handler"]
        UNITY_FIFO["FifoServer.cs"]
        AGENT_MGR["AgentManager"]
    end
    
    CTRL_SEND --> WSGI_SEND
    CTRL_SEND --> FIFO_SEND
    
    WSGI_SEND --> FLASK
    FLASK --> HTTP_ENDPOINT
    HTTP_ENDPOINT --> UNITY_HTTP
    
    FIFO_SEND --> NAMED_PIPES
    NAMED_PIPES --> MSGPACK
    MSGPACK --> UNITY_FIFO
    
    UNITY_HTTP --> AGENT_MGR
    UNITY_FIFO --> AGENT_MGR
    
    AGENT_MGR --> UNITY_HTTP
    AGENT_MGR --> UNITY_FIFO
    
    UNITY_HTTP --> HTTP_ENDPOINT
    UNITY_FIFO --> MSGPACK
    
    HTTP_ENDPOINT --> FLASK
    MSGPACK --> NAMED_PIPES
    
    FLASK --> WSGI_RECV
    NAMED_PIPES --> FIFO_RECV
    
    WSGI_RECV --> CTRL_RECV
    FIFO_RECV --> CTRL_RECV
```

### WSGI Server Protocol

The `WsgiServer` uses HTTP communication through Flask endpoints:

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| Flask App | HTTP server | Multi-part form data, JSON responses |
| `/train` endpoint | Action processing | Handles metadata and image data |
| Queue System | Thread-safe communication | Request/response queues |
| BufferedIO | Optimized data transfer | Reduced HTTP overhead |

### FIFO Server Protocol  

The `FifoServer` uses named pipes for lower-latency communication:

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| Named Pipes | Direct OS communication | Lower latency than HTTP |
| MessagePack | Binary serialization | Efficient data encoding |
| Field Types | Structured messages | Typed data fields (RGB, depth, metadata) |
| Signal Handling | Timeout management | Connection timeout detection |

Platform compatibility determines protocol selection:
- **Windows**: WSGI only (FIFO not supported)
- **Linux/macOS**: FIFO preferred, WSGI fallback

Sources: [ai2thor/wsgi_server.py:149-196](), [ai2thor/fifo_server.py:56-124](), [ai2thor/controller.py:512-529](), [unity/Assets/Scripts/FifoServer.cs:8-50]()

## Build System and Deployment

The build system automates Unity compilation, packaging, and deployment across multiple platforms using Python invoke tasks and Unity build scripts.

### Build Pipeline Architecture

```mermaid
graph TB
    subgraph "Development"
        INVOKE["invoke tasks.py"]
        UNITY_EDITOR["Unity Editor"]
        BUILD_CS["Build.cs"]
    end
    
    subgraph "Build Configuration"
        ENV_VARS["Environment Variables"]
        SCENES["Scene Selection"]
        PLATFORMS["Platform Targets"]
        DEFINES["Scripting Defines"]
    end
    
    subgraph "Build Execution"
        LOCAL_BUILD["local_build()"]
        WEBGL_BUILD["webgl_build()"]
        CI_BUILD["ci_build()"]
        BUILD_FUNC["build() function"]
    end
    
    subgraph "Artifact Management"
        ZIP_ARCHIVE["ZIP Archives"]
        S3_UPLOAD["S3 Upload"]
        METADATA["Build Metadata"]
        SHA256["Checksums"]
    end
    
    subgraph "Distribution"
        PUBLIC_S3["PUBLIC_S3_BUCKET"]
        PRIVATE_S3["PRIVATE_S3_BUCKET"]
        PYPI["PyPI Distribution"]
        DOCKER["Docker Images"]
    end
    
    INVOKE --> ENV_VARS
    INVOKE --> LOCAL_BUILD
    INVOKE --> WEBGL_BUILD
    INVOKE --> CI_BUILD
    
    ENV_VARS --> BUILD_CS
    SCENES --> BUILD_CS
    PLATFORMS --> BUILD_CS
    DEFINES --> BUILD_CS
    
    BUILD_CS --> BUILD_FUNC
    BUILD_FUNC --> ZIP_ARCHIVE
    
    ZIP_ARCHIVE --> S3_UPLOAD
    S3_UPLOAD --> PUBLIC_S3
    S3_UPLOAD --> PRIVATE_S3
    
    METADATA --> PUBLIC_S3
    SHA256 --> PUBLIC_S3
    
    INVOKE --> PYPI
    INVOKE --> DOCKER
```

### Key Build Tasks

| Task | Purpose | Key Parameters |
|------|---------|----------------|
| `local_build` | Development builds | `prefix`, `arch`, `scenes` |
| `webgl_build` | Web deployment | `scenes`, `content_addressable` |
| `ci_build` | Continuous integration | `commit_id`, `branch` |
| `build_pip` | Package distribution | `version` validation |

### Build Metadata and Downloads

The `ai2thor.build` module manages build discovery and download:

```mermaid
graph LR
    subgraph "Build Discovery"
        FIND_BUILD["Controller.find_build()"]
        PLATFORMS["Platform Selection"]
        VALIDATION["Platform Validation"]
    end
    
    subgraph "Build Types"
        BUILD_CLASS["Build"]
        EDITOR_BUILD["EditorBuild"]
        EXTERNAL_BUILD["ExternalBuild"]
    end
    
    subgraph "Download System"
        DOWNLOADER["ai2thor.downloader"]
        S3_AUTH["boto_auth()"]
        SHA256_CHECK["SHA256 Verification"]
        EXTRACT["ZIP Extraction"]
    end
    
    FIND_BUILD --> PLATFORMS
    PLATFORMS --> VALIDATION
    VALIDATION --> BUILD_CLASS
    VALIDATION --> EDITOR_BUILD
    VALIDATION --> EXTERNAL_BUILD
    
    BUILD_CLASS --> DOWNLOADER
    DOWNLOADER --> S3_AUTH
    DOWNLOADER --> SHA256_CHECK
    SHA256_CHECK --> EXTRACT
```

Sources: [tasks.py:488-511](), [tasks.py:514-637](), [tasks.py:1074-1200](), [ai2thor/build.py:110-248](), [unity/Assets/Editor/Build.cs:83-128]()

## Unity Integration and Data Exchange

The communication layer handles bidirectional data exchange between Python and Unity, including action commands, scene metadata, and image data.

### Data Flow Architecture

```mermaid
graph TB
    subgraph "Python to Unity"
        ACTION_DICT["Action Dictionary"]
        JSON_ENCODE["JSON Encoding"]
        NUMPY_AWARE["NumpyAwareEncoder"]
        SEND_METHOD["server.send()"]
    end
    
    subgraph "Unity Processing"
        UNITY_RECEIVE["Unity Action Handler"]
        AGENT_EXECUTE["Agent Execution"]
        IMAGE_SYNTHESIS["ImageSynthesis.cs"]
        METADATA_GEN["Metadata Generation"]
    end
    
    subgraph "Unity to Python"
        RESPONSE_DATA["Response Assembly"]
        IMAGE_DATA["Image Data"]
        METADATA_JSON["Metadata JSON"]
        MULTIPART["Multipart Encoding"]
    end
    
    subgraph "Python Reception"
        SERVER_RECEIVE["server.receive()"]
        EVENT_CREATE["Event Creation"]
        LAZY_MASKS["Lazy Segmentation Masks"]
        FINAL_EVENT["Final Event Object"]
    end
    
    ACTION_DICT --> JSON_ENCODE
    JSON_ENCODE --> NUMPY_AWARE
    NUMPY_AWARE --> SEND_METHOD
    
    SEND_METHOD --> UNITY_RECEIVE
    UNITY_RECEIVE --> AGENT_EXECUTE
    AGENT_EXECUTE --> IMAGE_SYNTHESIS
    AGENT_EXECUTE --> METADATA_GEN
    
    IMAGE_SYNTHESIS --> IMAGE_DATA
    METADATA_GEN --> METADATA_JSON
    IMAGE_DATA --> RESPONSE_DATA
    METADATA_JSON --> RESPONSE_DATA
    RESPONSE_DATA --> MULTIPART
    
    MULTIPART --> SERVER_RECEIVE
    SERVER_RECEIVE --> EVENT_CREATE
    EVENT_CREATE --> LAZY_MASKS
    LAZY_MASKS --> FINAL_EVENT
```

### Event Data Structure

The `Event` class wraps all response data from Unity:

| Component | Purpose | Data Types |
|-----------|---------|------------|
| `metadata` | Scene and object information | JSON dict via `MetadataWrapper` |
| `frame` | RGB image data | NumPy array (H×W×3) |
| `depth_frame` | Depth information | NumPy array (H×W) |
| `instance_masks` | Object segmentation | `LazyInstanceSegmentationMasks` |
| `class_masks` | Semantic segmentation | `LazyClassSegmentationMasks` |
| `third_party_*` | Additional camera data | Lists of arrays |

### Image Processing and Synthesis

Unity's `ImageSynthesis` component generates multiple image types:

```mermaid
graph LR
    subgraph "Capture Passes"
        IMG_PASS["_img (RGB)"]
        DEPTH_PASS["_depth"]
        ID_PASS["_id (Instance)"]
        CLASS_PASS["_class (Semantic)"]
        NORMALS_PASS["_normals"]
        FLOW_PASS["_flow (Optical)"]
    end
    
    subgraph "Shader Pipeline"
        UBER_SHADER["UberReplacement"]
        DEPTH_SHADER["DepthShader"]
        FLOW_SHADER["OpticalFlowShader"]
    end
    
    subgraph "Data Processing"
        BUFFER_READ["read_buffer_image()"]
        LAZY_LOADING["Lazy Mask Loading"]
        COLOR_MAPPING["Color ID Mapping"]
    end
    
    IMG_PASS --> BUFFER_READ
    DEPTH_PASS --> DEPTH_SHADER
    ID_PASS --> UBER_SHADER
    CLASS_PASS --> UBER_SHADER
    NORMALS_PASS --> UBER_SHADER
    FLOW_PASS --> FLOW_SHADER
    
    UBER_SHADER --> COLOR_MAPPING
    DEPTH_SHADER --> BUFFER_READ
    FLOW_SHADER --> BUFFER_READ
    
    BUFFER_READ --> LAZY_LOADING
    COLOR_MAPPING --> LAZY_LOADING
```

Sources: [ai2thor/server.py:427-533](), [ai2thor/server.py:59-155](), [unity/Assets/Scripts/ImageSynthesis/ImageSynthesis.cs:20-143](), [unity/Assets/Scripts/ImageSynthesis/ImageSynthesis.cs:235-300]()

## Error Handling and Debugging

The communication system includes comprehensive error handling and debugging capabilities for robust operation.

### Exception Handling

| Exception Type | Trigger | Recovery |
|----------------|---------|----------|
| `UnityCrashException` | Unity process exit | Process restart required |
| `TimeoutError` | Communication timeout | Configurable timeout values |
| `ValueError` | Invalid action parameters | Action validation |
| `ConnectionError` | Server communication failure | Protocol fallback |

### Debugging and Monitoring

The system provides multiple debugging mechanisms:

- **Frame rate monitoring**: Tracks rendering performance
- **Action validation**: Validates parameters before sending
- **Sequence ID tracking**: Ensures message ordering
- **Connection state monitoring**: Detects Unity process health
- **Build validation**: Verifies platform compatibility

Sources: [ai2thor/wsgi_server.py:36-65](), [ai2thor/fifo_server.py:147-200](), [ai2thor/controller.py:414-418](), [ai2thor/exceptions.py:1-10]()

---

