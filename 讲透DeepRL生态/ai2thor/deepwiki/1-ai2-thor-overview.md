> 来源: [https://deepwiki.com/allenai/ai2thor/1-ai2-thor-overview](https://deepwiki.com/allenai/ai2thor/1-ai2-thor-overview)
> DeepWiki allenai/ai2thor | Last indexed: 16 September 2025 (24f798

# AI2-THOR Overview

  Relevant source files 
 - [.dockerignore](https://github.com/allenai/ai2thor/blob/24f79883/.dockerignore)
 - [Dockerfile](https://github.com/allenai/ai2thor/blob/24f79883/Dockerfile)
 - [README.md](https://github.com/allenai/ai2thor/blob/24f79883/README.md?plain=1)
 - [WEBGL.md](https://github.com/allenai/ai2thor/blob/24f79883/WEBGL.md?plain=1)
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
 - [doc/static/ReleaseNotes/Cook.png](https://github.com/allenai/ai2thor/blob/24f79883/doc/static/ReleaseNotes/Cook.png)
 - [doc/static/ReleaseNotes/Dirty.png](https://github.com/allenai/ai2thor/blob/24f79883/doc/static/ReleaseNotes/Dirty.png)
 - [doc/static/ReleaseNotes/Fill.png](https://github.com/allenai/ai2thor/blob/24f79883/doc/static/ReleaseNotes/Fill.png)
 - [doc/static/ReleaseNotes/Moveable.png](https://github.com/allenai/ai2thor/blob/24f79883/doc/static/ReleaseNotes/Moveable.png)
 - [doc/static/ReleaseNotes/ReleaseNotes_2.4.md](https://github.com/allenai/ai2thor/blob/24f79883/doc/static/ReleaseNotes/ReleaseNotes_2.4.md?plain=1)
 - [doc/static/ReleaseNotes/Slice.png](https://github.com/allenai/ai2thor/blob/24f79883/doc/static/ReleaseNotes/Slice.png)
 - [doc/static/ReleaseNotes/UseUp.png](https://github.com/allenai/ai2thor/blob/24f79883/doc/static/ReleaseNotes/UseUp.png)
 - [start.sh](https://github.com/allenai/ai2thor/blob/24f79883/start.sh)
 - [tasks.py](https://github.com/allenai/ai2thor/blob/24f79883/tasks.py)
 - [unity/Assets/Editor/Build.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Editor/Build.cs)
 - [unity/Assets/Physics/SimObjsPhysics/RoboTHOR Objects/RoboTHOR_Assets_SmallObjects/Target_SmallObjects/SprayBottle/Materials.meta](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Physics/SimObjsPhysics/RoboTHOR Objects/RoboTHOR_Assets_SmallObjects/Target_SmallObjects/SprayBottle/Materials.meta)
 - [unity/Assets/Resources/MagicMirror/Prefab/MirrorMaterial.mat](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Resources/MagicMirror/Prefab/MirrorMaterial.mat)
 - [unity/Assets/Scripts/FifoServer.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/FifoServer.cs)
 - [unity/Assets/Scripts/ImageSynthesis/ImageSynthesis.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ImageSynthesis/ImageSynthesis.cs)
 - [unity/Assets/Scripts/ImageSynthesis/Shaders/Depth.shader](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ImageSynthesis/Shaders/Depth.shader)
 - [unity/ProjectSettings/GraphicsSettings.asset](https://github.com/allenai/ai2thor/blob/24f79883/unity/ProjectSettings/GraphicsSettings.asset)
 
  
## Purpose and Scope

 AI2-THOR is a near photo-realistic interactable framework for embodied AI agents. This document provides an overview of the core system architecture, communication protocols, and key components that enable researchers to create and control AI agents in 3D simulated environments.

 For detailed information about specific agent types and their capabilities, see [Specialized Agent Types](https://deepwiki.com/allenai/ai2thor/5-specialized-agent-types). For scene management and procedural generation, see [Scenes and Environments](https://deepwiki.com/allenai/ai2thor/6-scenes-and-environments). For object interaction systems, see [Object Interaction System](https://deepwiki.com/allenai/ai2thor/7-object-interaction-system).

 
## High-Level System Architecture

 AI2-THOR operates as a client-server architecture where Python clients communicate with a Unity simulation backend through multiple communication protocols.

 
```

```

 **Sources:** [ai2thor/controller.py1-50](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/controller.py#L1-L50) [tasks.py1-100](https://github.com/allenai/ai2thor/blob/24f79883/tasks.py#L1-L100) [unity/Assets/Scripts/AgentManager.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/AgentManager.cs) [unity/Assets/Scripts/ImageSynthesis/ImageSynthesis.cs1-50](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ImageSynthesis/ImageSynthesis.cs#L1-L50)

 
## Core Python Controller

 The `Controller` class serves as the primary entry point for interacting with AI2-THOR simulations. It manages the lifecycle of Unity processes, handles build downloads, and provides the main API for sending actions and receiving observations.

 
```

```

 The controller initialization process involves several key phases:

 
| Phase | Components | Key Classes |
|---|---|---|
| Platform Detection | ai2thor.platform | Linux64, OSXIntel64, CloudRendering |
| Build Management | ai2thor.build | Build, EditorBuild, ExternalBuild |
| Server Selection | Communication protocols | FifoServer, WsgiServer |
| Unity Process | Process management | subprocess.Popen |

 **Sources:** [ai2thor/controller.py372-627](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/controller.py#L372-L627) [ai2thor/build.py110-248](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/build.py#L110-L248) [ai2thor/platform.py1-236](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/platform.py#L1-L236)

 
## Communication Architecture

 AI2-THOR supports multiple communication protocols between the Python client and Unity backend, each optimized for different use cases.

 
```

```

 
### FIFO Server Communication

 The FIFO server uses named pipes for high-performance local communication:

 
```

```

 **Sources:** [ai2thor/fifo_server.py56-318](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/fifo_server.py#L56-L318) [unity/Assets/Scripts/FifoServer.cs1-50](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/FifoServer.cs#L1-L50) [ai2thor/fifo_server.py26-46](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/fifo_server.py#L26-L46)

 
## Build and Deployment System

 The build system manages Unity compilation, asset bundling, and distribution across multiple platforms.

 
```

```

 The build system supports environment-driven configuration:

 
| Environment Variable | Purpose | Code Reference |
|---|---|---|
| BUILD_SCENES | Scene selection | unity/Assets/Editor/Build.cs190-204 |
| INCLUDE_PRIVATE_SCENES | Private content | unity/Assets/Editor/Build.cs224-227 |
| BUILD_SCRIPTS_ONLY | Development builds | unity/Assets/Editor/Build.cs219-222 |
| UNITY_BUILD_NAME | Output naming | unity/Assets/Editor/Build.cs43-46 |

 **Sources:** [tasks.py193-250](https://github.com/allenai/ai2thor/blob/24f79883/tasks.py#L193-L250) [unity/Assets/Editor/Build.cs83-128](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Editor/Build.cs#L83-L128) [ai2thor/build.py110-248](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/build.py#L110-L248)

 
## Event and Observation System

 AI2-THOR's observation system provides rich sensory data through the `Event` class, which encapsulates all simulation state and sensor outputs.

 
```

```

 **Sources:** [ai2thor/server.py427-522](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/server.py#L427-L522) [unity/Assets/Scripts/ImageSynthesis/ImageSynthesis.cs20-143](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ImageSynthesis/ImageSynthesis.cs#L20-L143) [ai2thor/server.py59-331](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/server.py#L59-L331)

 
## Platform and Dependencies

 AI2-THOR adapts to different operating systems and hardware configurations through its platform abstraction layer.

 
```

```

 **Sources:** [ai2thor/platform.py214-227](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/platform.py#L214-L227) [ai2thor/platform.py150-160](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/platform.py#L150-L160) [ai2thor/platform.py185-202](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/platform.py#L185-L202)

 
## Summary

 AI2-THOR provides a comprehensive framework for embodied AI research through:

 
 - **Unified Python API**: The `Controller` class abstracts platform differences and communication protocols
 - **Multi-protocol Communication**: FIFO pipes for performance, WSGI for compatibility, WebGL for web deployment
 - **Automated Build System**: Cross-platform Unity builds with automated distribution
 - **Rich Observation Space**: RGB, depth, segmentation, and structured metadata
 - **Platform Flexibility**: Support for Linux, macOS, Windows, and cloud rendering
 
 The system is designed for both local development and large-scale distributed training, with extensive testing and validation frameworks to ensure reliability across different hardware configurations.

 **Sources:** [README.md1-312](https://github.com/allenai/ai2thor/blob/24f79883/README.md?plain=1#L1-L312) [ai2thor/__init__.py1-8](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/__init__.py#L1-L8) [ai2thor/controller.py1-100](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/controller.py#L1-L100)
