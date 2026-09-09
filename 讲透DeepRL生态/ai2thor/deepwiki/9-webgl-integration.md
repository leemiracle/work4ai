> 来源: [https://deepwiki.com/allenai/ai2thor/9-webgl-integration](https://deepwiki.com/allenai/ai2thor/9-webgl-integration)
> DeepWiki allenai/ai2thor | Last indexed: 16 September 2025 (24f798

# WebGL Integration

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

 The WebGL Integration system enables AI2-THOR to run in web browsers through Unity's WebGL build target. This system provides the infrastructure for creating browser-based interfaces for AI2-THOR simulations, enabling applications such as crowdsourcing tasks, web-based data collection, and accessible simulation environments without requiring local Unity installations.

 For information about general build processes and deployment infrastructure, see [Build System and Deployment](https://deepwiki.com/allenai/ai2thor/4.2-build-system-and-deployment). For Unity project configuration details, see [Unity Project Configuration](https://deepwiki.com/allenai/ai2thor/11-unity-project-configuration).

 
## WebGL Build System Overview

 The WebGL integration consists of several interconnected components that handle building, deploying, and running AI2-THOR in web browsers:

 
```

```

 **Sources:** [tasks.py514-636](https://github.com/allenai/ai2thor/blob/24f79883/tasks.py#L514-L636) [unity/Assets/Editor/Build.cs59-70](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Editor/Build.cs#L59-L70) [ai2thor/build.py24](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/build.py#L24-L24)

 
## Build Process and Task Automation

 The WebGL build process is orchestrated through the `webgl_build` invoke task, which handles scene selection, Unity compilation, and metadata generation:

 
```

```

 The task supports several configuration options:

 
| Parameter | Description | Default |
|---|---|---|
| scenes | Comma-separated scene list | All scenes |
| room_ranges | Range-based scene selection | None |
| prefix | Build name prefix | "local" |
| content_addressable | Hash-based file naming | False |
| crowdsource_build | Enable crowdsource defines | False |

 **Sources:** [tasks.py514-636](https://github.com/allenai/ai2thor/blob/24f79883/tasks.py#L514-L636) [tasks.py572-579](https://github.com/allenai/ai2thor/blob/24f79883/tasks.py#L572-L579)

 
## Unity WebGL Build Configuration

 The Unity build system handles WebGL-specific compilation requirements through the `Build.cs` script:

 
```

```

 The WebGL build requires specific scripting defines to disable native encoders that are incompatible with WebGL:

 
 - `USIM_USE_BUILTIN_JPG_ENCODER`
 - `USIM_USE_BUILTIN_PNG_ENCODER`
 
 **Sources:** [unity/Assets/Editor/Build.cs59-70](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Editor/Build.cs#L59-L70)

 
## Content Types and File Handling

 The WebGL system manages various file types with appropriate MIME types for web delivery:

 
| Extension | Content Type | Purpose |
|---|---|---|
| .js | application/javascript | Unity loader scripts |
| .wasm | application/wasm | WebAssembly binary |
| .data | application/octet-stream | Unity data files |
| .unityweb | application/octet-stream | Unity web resources |
| .html | text/html | Web page templates |
| .json | application/json | Scene metadata |

 **Sources:** [tasks.py41-54](https://github.com/allenai/ai2thor/blob/24f79883/tasks.py#L41-L54)

 
## Scene Metadata Generation

 The build process generates structured metadata for WebGL builds, organizing scenes by room types:

 
```

```

 **Sources:** [tasks.py589-635](https://github.com/allenai/ai2thor/blob/24f79883/tasks.py#L589-L635)

 
## JavaScript-Unity Communication Interface

 The WebGL integration provides a bidirectional communication interface between JavaScript and Unity:

 
```

```

 
### Communication Methods

 
| Direction | Method | Purpose |
|---|---|---|
| JS → Unity | SendMessage('FPSController', 'Step', jsonAction) | Execute actions |
| JS → Unity | SetController(controllerType) | Set input controller |
| Unity → JS | onUnityMetadata(metadataString) | Return action results |
| Unity → JS | onGameLoaded() | Signal initialization complete |

 **Sources:** [WEBGL.md49-87](https://github.com/allenai/ai2thor/blob/24f79883/WEBGL.md?plain=1#L49-L87) [WEBGL.md94-102](https://github.com/allenai/ai2thor/blob/24f79883/WEBGL.md?plain=1#L94-L102)

 
## Content Addressable Assets

 For production deployments, the system supports content-addressable file naming to enable efficient caching:

 
```

```

 **Sources:** [tasks.py622-632](https://github.com/allenai/ai2thor/blob/24f79883/tasks.py#L622-L632) [tasks.py535-547](https://github.com/allenai/ai2thor/blob/24f79883/tasks.py#L535-L547)

 
## Distribution and Deployment

 WebGL builds are distributed through S3 with appropriate content types and access controls:

 
| Component | S3 Bucket | Access |
|---|---|---|
| Public WebGL Builds | PUBLIC_WEBGL_S3_BUCKET | Public Read |
| Build Assets | File-specific content types | Optimized delivery |

 **Sources:** [ai2thor/build.py24](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/build.py#L24-L24) [tasks.py41-54](https://github.com/allenai/ai2thor/blob/24f79883/tasks.py#L41-L54)

 
## WebGL Templates and Customization

 The system supports custom WebGL templates for specialized interfaces:

 
```

```

 Templates are located in `unity/Assets/WebGLTemplates/` and can be selected through Unity's build settings for different use cases.

 **Sources:** [WEBGL.md28-45](https://github.com/allenai/ai2thor/blob/24f79883/WEBGL.md?plain=1#L28-L45) [WEBGL.md89-103](https://github.com/allenai/ai2thor/blob/24f79883/WEBGL.md?plain=1#L89-L103)
