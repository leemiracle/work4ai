> 来源: [https://deepwiki.com/allenai/ai2thor/4-python-api-and-communication](https://deepwiki.com/allenai/ai2thor/4-python-api-and-communication)
> DeepWiki allenai/ai2thor | Last indexed: 16 September 2025 (24f798

# Python API and Communication

  Relevant source files 
 - [.dockerignore](https://github.com/allenai/ai2thor/blob/24f79883/.dockerignore)
 - [Dockerfile](https://github.com/allenai/ai2thor/blob/24f79883/Dockerfile)
 - [ai2thor/__init__.py](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/__init__.py)
 - [ai2thor/build.py](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/build.py)
 - [ai2thor/controller.py](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/controller.py)
 - [ai2thor/docker.py](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/docker.py)
 - [ai2thor/downloader.py](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/downloader.py)
 - [ai2thor/fifo_server.py](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/fifo_server.py)
 - [ai2thor/platform.py](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/platform.py)
 - [ai2thor/server.py](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/server.py)
 - [ai2thor/tests/build_controller.py](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/tests/build_controller.py)
 - [ai2thor/tests/constants.py](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/tests/constants.py)
 - [ai2thor/tests/data/arm/new/pickup_object.json](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/tests/data/arm/new/pickup_object.json)
 - [ai2thor/tests/data/image-depth-data256.raw](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/tests/data/image-depth-data256.raw)
 - [ai2thor/tests/data/image-depth-datafloat32.raw](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/tests/data/image-depth-datafloat32.raw)
 - [ai2thor/tests/fifo_client.py](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/tests/fifo_client.py)
 - [ai2thor/tests/test_controller.py](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/tests/test_controller.py)
 - [ai2thor/tests/test_event.py](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/tests/test_event.py)
 - [ai2thor/tests/test_fifo_server.py](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/tests/test_fifo_server.py)
 - [ai2thor/tests/test_server.py](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/tests/test_server.py)
 - [ai2thor/tests/test_unity.py](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/tests/test_unity.py)
 - [ai2thor/wsgi_server.py](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/wsgi_server.py)
 - [start.sh](https://github.com/allenai/ai2thor/blob/24f79883/start.sh)
 - [tasks.py](https://github.com/allenai/ai2thor/blob/24f79883/tasks.py)
 - [unity/Assets/Editor/Build.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Editor/Build.cs)
 - [unity/Assets/Physics/SimObjsPhysics/RoboTHOR Objects/RoboTHOR_Assets_SmallObjects/Target_SmallObjects/SprayBottle/Materials.meta](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Physics/SimObjsPhysics/RoboTHOR Objects/RoboTHOR_Assets_SmallObjects/Target_SmallObjects/SprayBottle/Materials.meta)
 - [unity/Assets/Resources/MagicMirror/Prefab/MirrorMaterial.mat](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Resources/MagicMirror/Prefab/MirrorMaterial.mat)
 - [unity/Assets/Scripts/FifoServer.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/FifoServer.cs)
 - [unity/Assets/Scripts/ImageSynthesis/ImageSynthesis.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ImageSynthesis/ImageSynthesis.cs)
 - [unity/Assets/Scripts/ImageSynthesis/Shaders/Depth.shader](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ImageSynthesis/Shaders/Depth.shader)
 - [unity/ProjectSettings/GraphicsSettings.asset](https://github.com/allenai/ai2thor/blob/24f79883/unity/ProjectSettings/GraphicsSettings.asset)
 
  This document covers the Python API layer and communication systems that enable interaction between Python client code and the Unity simulation engine in AI2-THOR. This includes the primary `Controller` class, server communication protocols, build automation, and data exchange mechanisms.

 For information about specialized agent types and their controllers, see [Specialized Agent Types](https://deepwiki.com/allenai/ai2thor/5-specialized-agent-types). For details about Unity project configuration and scene management, see [Unity Project Configuration](https://deepwiki.com/allenai/ai2thor/11-unity-project-configuration) and [Scenes and Environments](https://deepwiki.com/allenai/ai2thor/6-scenes-and-environments).

 
## Architecture Overview

 The Python API and communication system forms the bridge between Python client applications and the Unity simulation engine through multiple communication protocols and build management systems.

 
```

```

 Sources: [ai2thor/controller.py1-1000](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/controller.py#L1-L1000) [ai2thor/server.py1-100](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/server.py#L1-L100) [ai2thor/wsgi_server.py1-100](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/wsgi_server.py#L1-L100) [ai2thor/fifo_server.py1-100](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/fifo_server.py#L1-L100)

 
## Controller Class - Main Python API

 The `Controller` class in `ai2thor.controller` serves as the primary entry point for all Python interactions with AI2-THOR. It manages initialization, communication protocols, build selection, and action execution.

 
```

```

 The `Controller` class handles several key responsibilities:

 
| Component | Purpose | Key Methods |
|---|---|---|
| Initialization | Set up communication and build | __init__, start() |
| Action Execution | Send actions to Unity | step(), multi_step_physics() |
| Scene Management | Load and reset scenes | reset(), normalize_scene() |
| Build Management | Handle Unity builds | find_build(), prune_releases() |
| Server Communication | Manage protocol selection | _build_server(), server_type_to_class() |

 Sources: [ai2thor/controller.py372-627](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/controller.py#L372-L627) [ai2thor/controller.py689-774](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/controller.py#L689-L774) [ai2thor/controller.py776-796](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/controller.py#L776-L796)

 
## Communication Protocols

 AI2-THOR supports two primary communication protocols between Python and Unity: WSGI (HTTP-based) and FIFO (named pipes). The choice depends on platform compatibility and performance requirements.

 
### Protocol Architecture

 
```

```

 
### WSGI Server Protocol

 The `WsgiServer` uses HTTP communication through Flask endpoints:

 
| Component | Purpose | Key Features |
|---|---|---|
| Flask App | HTTP server | Multi-part form data, JSON responses |
| /train endpoint | Action processing | Handles metadata and image data |
| Queue System | Thread-safe communication | Request/response queues |
| BufferedIO | Optimized data transfer | Reduced HTTP overhead |

 
### FIFO Server Protocol

 The `FifoServer` uses named pipes for lower-latency communication:

 
| Component | Purpose | Key Features |
|---|---|---|
| Named Pipes | Direct OS communication | Lower latency than HTTP |
| MessagePack | Binary serialization | Efficient data encoding |
| Field Types | Structured messages | Typed data fields (RGB, depth, metadata) |
| Signal Handling | Timeout management | Connection timeout detection |

 Platform compatibility determines protocol selection:

 
 - **Windows**: WSGI only (FIFO not supported)
 - **Linux/macOS**: FIFO preferred, WSGI fallback
 
 Sources: [ai2thor/wsgi_server.py149-196](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/wsgi_server.py#L149-L196) [ai2thor/fifo_server.py56-124](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/fifo_server.py#L56-L124) [ai2thor/controller.py512-529](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/controller.py#L512-L529) [unity/Assets/Scripts/FifoServer.cs8-50](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/FifoServer.cs#L8-L50)

 
## Build System and Deployment

 The build system automates Unity compilation, packaging, and deployment across multiple platforms using Python invoke tasks and Unity build scripts.

 
### Build Pipeline Architecture

 
```

```

 
### Key Build Tasks

 
| Task | Purpose | Key Parameters |
|---|---|---|
| local_build | Development builds | prefix, arch, scenes |
| webgl_build | Web deployment | scenes, content_addressable |
| ci_build | Continuous integration | commit_id, branch |
| build_pip | Package distribution | version validation |

 
### Build Metadata and Downloads

 The `ai2thor.build` module manages build discovery and download:

 
```

```

 Sources: [tasks.py488-511](https://github.com/allenai/ai2thor/blob/24f79883/tasks.py#L488-L511) [tasks.py514-637](https://github.com/allenai/ai2thor/blob/24f79883/tasks.py#L514-L637) [tasks.py1074-1200](https://github.com/allenai/ai2thor/blob/24f79883/tasks.py#L1074-L1200) [ai2thor/build.py110-248](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/build.py#L110-L248) [unity/Assets/Editor/Build.cs83-128](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Editor/Build.cs#L83-L128)

 
## Unity Integration and Data Exchange

 The communication layer handles bidirectional data exchange between Python and Unity, including action commands, scene metadata, and image data.

 
### Data Flow Architecture

 
```

```

 
### Event Data Structure

 The `Event` class wraps all response data from Unity:

 
| Component | Purpose | Data Types |
|---|---|---|
| metadata | Scene and object information | JSON dict via MetadataWrapper |
| frame | RGB image data | NumPy array (H×W×3) |
| depth_frame | Depth information | NumPy array (H×W) |
| instance_masks | Object segmentation | LazyInstanceSegmentationMasks |
| class_masks | Semantic segmentation | LazyClassSegmentationMasks |
| third_party_* | Additional camera data | Lists of arrays |

 
### Image Processing and Synthesis

 Unity's `ImageSynthesis` component generates multiple image types:

 
```

```

 Sources: [ai2thor/server.py427-533](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/server.py#L427-L533) [ai2thor/server.py59-155](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/server.py#L59-L155) [unity/Assets/Scripts/ImageSynthesis/ImageSynthesis.cs20-143](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ImageSynthesis/ImageSynthesis.cs#L20-L143) [unity/Assets/Scripts/ImageSynthesis/ImageSynthesis.cs235-300](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ImageSynthesis/ImageSynthesis.cs#L235-L300)

 
## Error Handling and Debugging

 The communication system includes comprehensive error handling and debugging capabilities for robust operation.

 
### Exception Handling

 
| Exception Type | Trigger | Recovery |
|---|---|---|
| UnityCrashException | Unity process exit | Process restart required |
| TimeoutError | Communication timeout | Configurable timeout values |
| ValueError | Invalid action parameters | Action validation |
| ConnectionError | Server communication failure | Protocol fallback |

 
### Debugging and Monitoring

 The system provides multiple debugging mechanisms:

 
 - **Frame rate monitoring**: Tracks rendering performance
 - **Action validation**: Validates parameters before sending
 - **Sequence ID tracking**: Ensures message ordering
 - **Connection state monitoring**: Detects Unity process health
 - **Build validation**: Verifies platform compatibility
 
 Sources: [ai2thor/wsgi_server.py36-65](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/wsgi_server.py#L36-L65) [ai2thor/fifo_server.py147-200](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/fifo_server.py#L147-L200) [ai2thor/controller.py414-418](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/controller.py#L414-L418) [ai2thor/exceptions.py1-10](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/exceptions.py#L1-L10)
