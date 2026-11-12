<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/TensorRT · page 4 Plugin System · fetched 2026-10-26 -->

# Plugin System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitmodules](.gitmodules)
- [CHANGELOG.md](CHANGELOG.md)
- [plugin/CMakeLists.txt](plugin/CMakeLists.txt)
- [plugin/README.md](plugin/README.md)
- [plugin/common/checkMacrosPlugin.cpp](plugin/common/checkMacrosPlugin.cpp)
- [plugin/exports-vfc_plugin.map](plugin/exports-vfc_plugin.map)
- [plugin/multiscaleDeformableAttnPlugin/CMakeLists.txt](plugin/multiscaleDeformableAttnPlugin/CMakeLists.txt)
- [plugin/multiscaleDeformableAttnPlugin/README.md](plugin/multiscaleDeformableAttnPlugin/README.md)
- [plugin/multiscaleDeformableAttnPlugin/multiscaleDeformableAttn.cu](plugin/multiscaleDeformableAttnPlugin/multiscaleDeformableAttn.cu)
- [plugin/multiscaleDeformableAttnPlugin/multiscaleDeformableAttn.h](plugin/multiscaleDeformableAttnPlugin/multiscaleDeformableAttn.h)
- [plugin/multiscaleDeformableAttnPlugin/multiscaleDeformableAttnPlugin.cpp](plugin/multiscaleDeformableAttnPlugin/multiscaleDeformableAttnPlugin.cpp)
- [plugin/multiscaleDeformableAttnPlugin/multiscaleDeformableAttnPlugin.h](plugin/multiscaleDeformableAttnPlugin/multiscaleDeformableAttnPlugin.h)
- [plugin/multiscaleDeformableAttnPlugin/multiscaleDeformableIm2ColCuda.cuh](plugin/multiscaleDeformableAttnPlugin/multiscaleDeformableIm2ColCuda.cuh)
- [scripts/stubify.sh](scripts/stubify.sh)

</details>



TensorRT's Plugin System provides a framework for extending TensorRT with custom layer implementations that are not natively supported. This system enables users to implement specialized operations, accelerate specific network architectures, and integrate domain-specific optimizations while maintaining compatibility with TensorRT's inference engine.

This page covers the overall plugin architecture, interfaces, registration mechanisms, and build system. For specific plugin implementations, see [BERT and NLP Plugins](#4.3), [Detection and NMS Plugins](#4.4), [3D Perception Plugins](#4.5), and [Normalization Plugins](#4.6). For creating custom plugins, see [Creating Custom Plugins](#4.2).

## Architecture Overview

TensorRT's plugin system consists of several key components that work together to enable custom layer functionality:

```mermaid
graph TD
    subgraph "TensorRT Core"
        BUILDER["IBuilder<br/>Network Definition"]
        ENGINE["ICudaEngine<br/>Inference Runtime"]
        REGISTRY["IPluginRegistry<br/>Global Plugin Manager"]
    end
    
    subgraph "Plugin Interfaces"
        IPLUGINV2["IPluginV2<br/>Legacy Interface"]
        IPLUGINV2EXT["IPluginV2Ext<br/>Extended Interface"]
        IPLUGINV2DYN["IPluginV2DynamicExt<br/>Dynamic Shape Support"]
        IPLUGINV3["IPluginV3<br/>Latest Interface"]
    end
    
    subgraph "Plugin Libraries"
        TENSORRT_PLUGINS["tensorrt_plugins.so<br/>Main Plugin Library"]
        TENSORRT_VC_PLUGINS["tensorrt_vc_plugins.so<br/>Version Compatibility"]
    end
    
    subgraph "Plugin Registration"
        INIT_FUNC["initLibNvInferPlugins()"]
        CREATOR_REGISTRY["PluginCreatorRegistry<br/>Singleton Manager"]
        CREATORS["Plugin Creators<br/>Factory Classes"]
    end
    
    subgraph "Build System"
        MAIN_CMAKE["plugin/CMakeLists.txt"]
        PLUGIN_OBJECTS["trt_plugins<br/>Object Library"]
    end
    
    INIT_FUNC --> CREATOR_REGISTRY
    CREATOR_REGISTRY --> REGISTRY
    CREATORS --> IPLUGINV2
    CREATORS --> IPLUGINV2EXT  
    CREATORS --> IPLUGINV2DYN
    CREATORS --> IPLUGINV3
    
    REGISTRY --> BUILDER
    BUILDER --> ENGINE
    
    MAIN_CMAKE --> PLUGIN_OBJECTS
    PLUGIN_OBJECTS --> TENSORRT_PLUGINS
    PLUGIN_OBJECTS --> TENSORRT_VC_PLUGINS
    
    TENSORRT_PLUGINS --> INIT_FUNC
```

Sources: [plugin/CMakeLists.txt:1-280](), [plugin/api/inferPlugin.cpp:86-174](), [plugin/README.md:1-68]()

## Plugin Interfaces and Versioning

TensorRT provides multiple plugin interfaces to accommodate different use cases and maintain backward compatibility:

| Interface | Version | Dynamic Shapes | Use Case |
|-----------|---------|----------------|----------|
| `IPluginV2` | Legacy | No | Simple static plugins |
| `IPluginV2Ext` | Extended | No | Enhanced static plugins |
| `IPluginV2DynamicExt` | Dynamic | Yes | Dynamic shape support |
| `IPluginV3` | Latest | Yes | Modern interface with capabilities |

The `IPluginV3` interface introduces a capability-based system where plugins implement specific capability interfaces:

```mermaid
graph TD
    IPLUGINV3["IPluginV3<br/>Base Interface"]
    
    subgraph "Capability Interfaces"
        CORE["IPluginV3OneCore<br/>Core Functionality"]
        BUILD["IPluginV3OneBuild<br/>Build-time Operations"]  
        RUNTIME["IPluginV3OneRuntime<br/>Runtime Execution"]
    end
    
    IPLUGINV3 --> CORE
    IPLUGINV3 --> BUILD
    IPLUGINV3 --> RUNTIME
    
    subgraph "Plugin Implementation Example"
        INSTANCENORM["InstanceNormalizationV3Plugin"]
        GET_CAPABILITY["getCapabilityInterface(type)"]
    end
    
    INSTANCENORM --> GET_CAPABILITY
    GET_CAPABILITY --> CORE
    GET_CAPABILITY --> BUILD
    GET_CAPABILITY --> RUNTIME
```

Sources: [plugin/instanceNormalizationPlugin/instanceNormalizationPlugin.cu:94-114](), [plugin/leakyReluPlugin/lReluPlugin.h:31-73]()

## Registration and Initialization System

The plugin registration system ensures plugins are properly initialized and available to TensorRT engines:

```mermaid
graph TD
    subgraph "Application Layer"
        APP["User Application"]
        INIT_CALL["initLibNvInferPlugins(logger, namespace)"]
    end
    
    subgraph "Registration Infrastructure"
        CREATOR_REGISTRY["PluginCreatorRegistry<br/>Singleton Instance"]
        ADD_PLUGIN["addPluginCreator<T>(logger, namespace)"]
        REGISTRY_LIST["mRegistryList<br/>std::unordered_set<string>"]
        REGISTRY_STACK["mRegistry<br/>std::stack<unique_ptr>"]
    end
    
    subgraph "TensorRT Core"
        PLUGIN_REGISTRY["IPluginRegistry::registerCreator()"]
        GET_PLUGIN_REGISTRY["getPluginRegistry()"]
    end
    
    subgraph "Plugin Creators"
        LRELU_CREATOR["LReluPluginCreator"]
        INSTANCENORM_CREATOR["InstanceNormalizationV3PluginCreator"]
        BATCHEDNMS_CREATOR["BatchedNMSPluginCreator"]
        OTHER_CREATORS["... 50+ Plugin Creators"]
    end
    
    APP --> INIT_CALL
    INIT_CALL --> CREATOR_REGISTRY
    CREATOR_REGISTRY --> ADD_PLUGIN
    
    ADD_PLUGIN --> LRELU_CREATOR
    ADD_PLUGIN --> INSTANCENORM_CREATOR  
    ADD_PLUGIN --> BATCHEDNMS_CREATOR
    ADD_PLUGIN --> OTHER_CREATORS
    
    ADD_PLUGIN --> REGISTRY_LIST
    ADD_PLUGIN --> REGISTRY_STACK
    ADD_PLUGIN --> GET_PLUGIN_REGISTRY
    GET_PLUGIN_REGISTRY --> PLUGIN_REGISTRY
```

The registration process follows this sequence:

1. **Library Loading**: Application loads `tensorrt_plugins.so`
2. **Initialization Call**: Application calls `initLibNvInferPlugins(logger, namespace)`
3. **Creator Registration**: Each plugin creator is registered through `PluginCreatorRegistry::addPluginCreator<T>()`
4. **Duplicate Prevention**: The registry checks `mRegistryList` to prevent duplicate registrations
5. **TensorRT Integration**: Successfully registered creators are added to TensorRT's `IPluginRegistry`

Sources: [plugin/api/inferPlugin.cpp:86-174](), [plugin/api/inferPlugin.cpp:181-235]()

## Build System Architecture

The plugin build system is designed to support multiple library configurations and cross-platform compilation:

```mermaid
graph TD
    subgraph "Build Configuration"
        MAIN_CMAKE["plugin/CMakeLists.txt"]
        NEW_FLOW["TRT_BUILD_ENABLE_NEW_PLUGIN_FLOW"]
        BERT_OPTION["TRT_BUILD_INCLUDE_BERT_QKV_PLUGIN"]
    end
    
    subgraph "Object Libraries"
        TRT_PLUGINS["trt_plugins<br/>OBJECT Library"]
        TRT_VC_PLUGINS["trt_vc_plugins<br/>OBJECT Library"]
    end
    
    subgraph "Plugin Source Management"
        PLUGIN_NAMES["TRT_PLUGIN_NAMES<br/>List of 40+ Plugins"]
        ADD_PLUGIN_SOURCE["add_plugin_source()"]
        ADD_VC_PLUGIN_SOURCE["add_vc_plugin_source()"]
    end
    
    subgraph "Final Libraries"
        SHARED_LIB["tensorrt_plugins<br/>SHARED -> nvinfer_plugin.so"]
        STATIC_LIB["tensorrt_plugins_static<br/>STATIC"]
        INTERNAL_LIB["tensorrt_plugins_internal<br/>SHARED with symbols"]
        VC_SHARED["tensorrt_vc_plugins<br/>SHARED -> nvinfer_vc_plugin.so"]
        VC_STATIC["tensorrt_vc_plugins_static<br/>STATIC"]
    end
    
    subgraph "Individual Plugin Directories"
        SUBDIRS["add_subdirectory() for each plugin"]
        PLUGIN_CMAKE["Each plugin's CMakeLists.txt"]
    end
    
    MAIN_CMAKE --> NEW_FLOW
    MAIN_CMAKE --> BERT_OPTION
    MAIN_CMAKE --> TRT_PLUGINS
    MAIN_CMAKE --> TRT_VC_PLUGINS
    
    PLUGIN_NAMES --> SUBDIRS
    SUBDIRS --> PLUGIN_CMAKE
    PLUGIN_CMAKE --> ADD_PLUGIN_SOURCE
    PLUGIN_CMAKE --> ADD_VC_PLUGIN_SOURCE
    
    ADD_PLUGIN_SOURCE --> TRT_PLUGINS
    ADD_VC_PLUGIN_SOURCE --> TRT_VC_PLUGINS
    
    TRT_PLUGINS --> SHARED_LIB
    TRT_PLUGINS --> STATIC_LIB
    TRT_PLUGINS --> INTERNAL_LIB
    TRT_VC_PLUGINS --> VC_SHARED
    TRT_VC_PLUGINS --> VC_STATIC
```

The build system supports several key features:

- **Object Library Pattern**: Uses `OBJECT` libraries to compile sources once and link multiple times
- **Symbol Management**: Different export maps control symbol visibility for each library variant
- **Architecture Support**: Configures CUDA architectures via `CMAKE_CUDA_ARCHITECTURES`
- **Version Compatibility**: Separate VC (Version Compatibility) libraries for minimal plugin subsets

Key build artifacts include:
- `libnvinfer_plugin.so`: Main plugin library for production use
- `libnvinfer_plugin_internal.so`: Development library with exposed symbols
- `libnvinfer_vc_plugin.so`: Version compatibility library

Sources: [plugin/CMakeLists.txt:20-280](), [plugin/CMakeLists.txt:36-93]()

## Plugin Categories

The TensorRT OSS plugin library contains over 40 different plugins organized into functional categories:

| Category | Example Plugins | Purpose |
|----------|----------------|---------|
| **BERT/NLP** | `bertQKVToContextPlugin`, `embLayerNormPlugin`, `skipLayerNormPlugin` | Transformer model acceleration |
| **Detection** | `batchedNMSPlugin`, `efficientNMSPlugin`, `generateDetectionPlugin` | Object detection pipelines |
| **3D Perception** | `pillarScatterPlugin`, `voxelGeneratorPlugin`, `decodeBbox3DPlugin` | Point cloud and 3D object detection |
| **Normalization** | `instanceNormalizationPlugin`, `groupNormalizationPlugin` | Various normalization layers |
| **Spatial Operations** | `cropAndResizePlugin`, `roiAlignPlugin`, `proposalPlugin` | Spatial feature manipulation |
| **Utility** | `flattenConcat`, `splitPlugin`, `reorgPlugin` | General tensor operations |

Many plugins have multiple versions to maintain backward compatibility:

```mermaid
graph LR
    subgraph "Plugin Evolution Example"
        V1["InstanceNormalization_TRT v1<br/>DEPRECATED"]
        V2["InstanceNormalization_TRT v2<br/>DEPRECATED"] 
        V3["InstanceNormalization_TRT v3<br/>CURRENT"]
    end
    
    subgraph "Interface Migration"
        IPLV2["IPluginV2"]
        IPLV2EXT["IPluginV2Ext"]
        IPLV3["IPluginV3"]
    end
    
    V1 --> IPLV2
    V2 --> IPLV2EXT
    V3 --> IPLV3
    
    V1 --> V2
    V2 --> V3
```

Sources: [plugin/README.md:4-68](), [plugin/CMakeLists.txt:36-84]()

## Plugin Lifecycle

Understanding the plugin lifecycle is crucial for both plugin developers and users:

1. **Registration**: Plugins are registered during library initialization via `initLibNvInferPlugins()`
2. **Creation**: Plugin instances are created by their respective creators during network building
3. **Configuration**: Plugins are configured with input/output tensor information
4. **Context Attachment**: Runtime plugins are attached to execution contexts via `attachToContext()`
5. **Execution**: Plugin kernels are launched during inference via `enqueue()`
6. **Cleanup**: Plugin resources are released when engines are destroyed

The plugin system provides thread-safe registration and manages plugin lifetimes automatically through RAII patterns and smart pointers.

Sources: [plugin/api/inferPlugin.cpp:86-174](), [plugin/instanceNormalizationPlugin/instanceNormalizationPlugin.cu:554-559]()

---

