<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/TensorRT · page 1 TensorRT Overview · fetched 2026-10-26 -->

# TensorRT Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitmodules](.gitmodules)
- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [VERSION](VERSION)
- [docker/build.sh](docker/build.sh)
- [docker/launch.sh](docker/launch.sh)
- [docker/ubuntu-cross-aarch64.Dockerfile](docker/ubuntu-cross-aarch64.Dockerfile)
- [include/NvInferVersion.h](include/NvInferVersion.h)

</details>



This page describes the structure and purpose of the **NVIDIA/TensorRT Open Source Software (OSS)** repository. It covers what the repository contains, how it relates to the closed-source TensorRT GA binary release, the supported platforms, and the API migration requirements coming in TensorRT 11.0.

For installation steps and prerequisites, see [Installation and Setup](#1.1). For the build system in detail, see [Building From Source](#2).

---

## What This Repository Is

The TensorRT OSS repository is a **partial open-source complement** to the TensorRT General Availability (GA) binary release (`libnvinfer.so`). It does not contain the core inference engine. Instead, it contains:

- The **plugin library** (`libnvinfer_plugin.so`) — built-in custom layer implementations
- The **ONNX parser** (`libnvonnxparser.so`) — converts ONNX graphs to `INetworkDefinition`
- The **`trtexec` CLI** — engine building and benchmarking tool
- **C++ and Python samples** — reference implementations
- **Demo applications** — BERT, Stable Diffusion, Tacotron2
- **Developer tools** — ONNX Graph Surgeon, TRT Engine Explorer, TF Quantization Toolkit
- **Python bindings** — wraps the C++ API for Python consumers

The core TensorRT runtime (`IBuilder`, `IRuntime`, `ICudaEngine`, etc.) is **not** part of this repository. It is distributed as a closed-source binary from NVIDIA's developer portal and is a required build dependency.

Sources: [README.md:14-16]()

---

## Repository at a Glance

The following diagram maps top-level directories to their primary roles and output artifacts.

**Repository Component Map**

```mermaid
graph TD
    subgraph "OSS Repository (NVIDIA/TensorRT)"
        include["include/\nNvInfer.h, NvOnnxParser.h,\nNvInferPlugin.h, NvInferVersion.h"]
        plugin["plugin/\nInferPlugin.cpp + plugin implementations"]
        parsers["parsers/onnx\n(git submodule: onnx-tensorrt)"]
        samples["samples/\ntrtexec, C++ samples, Python samples"]
        demo["demo/\nBERT, Diffusion"]
        tools["tools/\nonnx-graphsurgeon, trt-engine-explorer,\ntensorflow-quantization"]
        python["python/\nPython bindings (pyOnnx.cpp, etc.)"]
        docker["docker/\nDockerfiles + build.sh + launch.sh"]
    end

    plugin -->|"builds to"| libnvinfer_plugin["libnvinfer_plugin.so"]
    parsers -->|"builds to"| libnvonnxparser["libnvonnxparser.so"]
    samples -->|"builds to"| trtexec["trtexec binary"]
    python -->|"builds to"| pytrt["tensorrt Python .so"]
```

Sources: [README.md:14-16](), [.gitmodules:9-12]()

---

## Relationship to the TensorRT GA Binary

The OSS components are built **against** the GA release, not independent of it. The GA release provides `libnvinfer.so`, which contains the core builder and runtime. All OSS components link to it.

**OSS vs. GA Dependency Relationship**

```mermaid
flowchart LR
    subgraph "GA Binary Release (closed-source)"
        libnvinfer["libnvinfer.so\nIBuilder, IRuntime, ICudaEngine,\nIExecutionContext, INetworkDefinition"]
    end

    subgraph "TensorRT OSS (this repository)"
        libnvinfer_plugin["libnvinfer_plugin.so\nplugin/InferPlugin.cpp\ninitLibNvInferPlugins()"]
        libnvonnxparser["libnvonnxparser.so\nparsers/onnx\nIParser, IParserRefitter"]
        trtexec["trtexec\nsamples/trtexec/"]
        pytrt["tensorrt Python .so\npython/"]
    end

    libnvinfer -->|"TRT_LIB_DIR link dep"| libnvinfer_plugin
    libnvinfer -->|"TRT_LIB_DIR link dep"| libnvonnxparser
    libnvinfer -->|"TRT_LIB_DIR link dep"| trtexec
    libnvinfer -->|"TRT_LIB_DIR link dep"| pytrt
```

The CMake build requires `TRT_LIB_DIR` to be set to the directory containing the GA libraries. Without them, nothing in the OSS repo can be compiled.

Sources: [README.md:38-82]()

---

## Current Version

| Component | Version |
|-----------|---------|
| TensorRT OSS | `10.15.1.29` |
| `NV_TENSORRT_MAJOR` | `10` |
| `NV_TENSORRT_MINOR` | `15` |
| `NV_TENSORRT_PATCH` | `1` |
| `NV_TENSORRT_BUILD` | `29` |
| Required CUDA | `13.1` or `12.9` |
| cuDNN (optional) | `8.9` |

Version macros are defined in [include/NvInferVersion.h:26-33]().

Sources: [VERSION:1-1](), [include/NvInferVersion.h:26-33]()

---

## Supported Platforms

| Platform | Architecture | Notes |
|----------|-------------|-------|
| Ubuntu 24.04 | x86_64 | Primary Linux target |
| Ubuntu 24.04 | aarch64 | Native build |
| Rocky Linux 8 | x86_64 | RPM-based distributions |
| Jetson (JetPack) | aarch64 | Cross-compiled from x86_64 |
| DriveOS 6.5 / 7 | aarch64 (Linux) | Cross-compiled; QNX also supported |
| DriveOS 6.5 | aarch64 (QNX) | Requires QNX toolchain |
| Windows 10/11 | x86_64 | Native build via MSVC |

Build toolchain files for cross-compilation live in `cmake/toolchains/`. The relevant ones are:

| Toolchain File | Target |
|---|---|
| `cmake_aarch64-native.toolchain` | Native aarch64 Linux build |
| `cmake_aarch64_cross.toolchain` | Cross-compile for Jetson from x86_64 |
| `cmake_aarch64_dos_cross.toolchain` | Cross-compile for DriveOS Linux |
| `cmake_qnx.toolchain` | Cross-compile for QNX |
| `cmake_qnx_safe.toolchain` | Safety-certified QNX builds |

Sources: [README.md:120-310](), [docker/ubuntu-cross-aarch64.Dockerfile:1-100]()

---

## What Each OSS Component Does

### Plugin Library (`plugin/`)

Contains built-in TensorRT plugins shipped as `libnvinfer_plugin.so`. All plugins register themselves when `initLibNvInferPlugins()` is called. Plugins are grouped by application domain:

| Plugin Group | Examples |
|---|---|
| NMS / Detection | `EfficientNMS_TRT`, `BatchedNMS_TRT`, `GenerateDetection_TRT` |
| BERT / NLP | `CustomQKVToContextPluginDynamic`, `CustomEmbLayerNormDynamic`, `CustomSkipLayerNormDynamic` |
| 3D Perception | `VoxelGeneratorPlugin`, `DecodeBbox3DPlugin` |
| Normalization | `InstanceNormalization_TRT`, `GroupNormalizationPlugin` |
| Attention | `DisentangledAttention_TRT`, `MultiscaleDeformableAttnPlugin_TRT` |

For detailed plugin documentation, see [Plugin System](#4).

### ONNX Parser (`parsers/onnx`)

A git submodule pointing to `onnx/onnx-tensorrt`. Provides `IParser` and `IParserRefitter` interfaces declared in `include/NvOnnxParser.h`. Converts ONNX model graphs into `INetworkDefinition` objects consumable by `IBuilder`.

For details, see [Builder and Optimization](#3.2).

### `trtexec` (`samples/trtexec/`)

A command-line utility for building TRT engines from ONNX models and benchmarking inference throughput. It is both a tool and a reference consumer of the OSS sample infrastructure in `samples/common/`.

For shared sample infrastructure details, see [Sample Infrastructure](#5.1).

### Demo Applications (`demo/`)

| Demo | Location | Purpose |
|---|---|---|
| BERT | `demo/BERT/` | NLP inference, INT8 calibration, SQuAD eval |
| Stable Diffusion / Flux | `demo/Diffusion/` | Text-to-image / image-to-image pipelines |

See [Demo Applications](#5) for details.

### Tools (`tools/`)

| Tool | Path | Purpose |
|---|---|---|
| ONNX Graph Surgeon | `tools/onnx-graphsurgeon/` | Programmatic ONNX graph manipulation |
| TRT Engine Explorer | `tools/trt-engine-explorer/` | Engine plan visualization and analysis |
| TF Quantization Toolkit | `tools/tensorflow-quantization/` | QAT for TensorFlow 2 models |

See [ONNX Graph Surgeon](#6) and [Performance and Profiling Tools](#8) for details.

---

## Upcoming Breaking Changes in TensorRT 11.0

TensorRT 11.0 is planned for 2026 Q2. It removes several legacy APIs that have been deprecated over the TRT 10.x series. Affected code in this repository is actively being migrated.

| Removed Feature | Replacement | Tracking in OSS |
|---|---|---|
| `IPluginV2` and all subclasses | `IPluginV3` + `IPluginCreatorV3One` | Plugins progressively migrated since TRT 10.4 |
| Weakly-typed networks | Strongly Typed Networks (`IBuilderConfig`) | New samples added in TRT 10.15 |
| Implicit quantization APIs | Explicit Quantization via QDQ nodes | Parser and sample updates |
| TREX tool | Nsight Deep Learning Designer | `tools/trt-engine-explorer/` will be removed |
| Python 3.9 and older bindings | Python 3.10+ | Already enforced in TRT 10.13.2+ |

### Plugin Migration State (as of TRT 10.15)

The plugin library uses a version number per plugin. Each `IPluginV2`-derived version has been given a corresponding `IPluginV3`-derived successor:

```mermaid
flowchart LR
    subgraph "IPluginV2 (deprecated)"
        qkv_v1["bertQKVToContextPlugin\nversions 1,2,3"]
        emb_v1["embLayerNormPlugin\nversions 2,3"]
        skip_v1["skipLayerNormPlugin\nversions 1-4"]
        inst_v1["InstanceNormalization_TRT\nversions 1,2"]
    end
    subgraph "IPluginV3 (current)"
        qkv_v2["bertQKVToContextPlugin\nversions 4,5,6"]
        emb_v2["embLayerNormPlugin\nversions 4,5"]
        skip_v2["skipLayerNormPlugin\nversions 5-8"]
        inst_v2["InstanceNormalization_TRT\nversion 3"]
    end
    qkv_v1 -->|"migrated"| qkv_v2
    emb_v1 -->|"migrated"| emb_v2
    skip_v1 -->|"migrated"| skip_v2
    inst_v1 -->|"migrated"| inst_v2
```

Sources: [README.md:3-12](), [CHANGELOG.md:1-120]()

---

## Model-to-Inference Flow

The following shows the full path from a training framework to a running TensorRT inference session, with code entities at each step.

**End-to-End Data Flow**

```mermaid
flowchart TD
    fw["PyTorch / TensorFlow / ONNX-native"]
    onnx_model["ONNX Model (.onnx)"]
    gs["onnx-graphsurgeon\ntools/onnx-graphsurgeon/\nGraph, Node, Tensor"]
    parser["IParser (NvOnnxParser.h)\nlibnvonnxparser.so\nparsers/onnx/"]
    network["INetworkDefinition\n(from libnvinfer.so)"]
    plugins_build["initLibNvInferPlugins()\nplugin/InferPlugin.cpp"]
    builder["IBuilder + IBuilderConfig\n(from libnvinfer.so)"]
    engine_file["Serialized Engine\n(.trt / .engine)"]
    runtime["IRuntime::deserializeCudaEngine()\n(from libnvinfer.so)"]
    context["IExecutionContext::enqueueV3()"]

    fw -->|"torch.onnx.export / tf2onnx"| onnx_model
    onnx_model -->|"optional: graph surgery"| gs
    gs --> parser
    onnx_model --> parser
    parser -->|"parse()"| network
    plugins_build -->|"registered at build time"| builder
    network --> builder
    builder -->|"buildSerializedNetwork()"| engine_file
    engine_file --> runtime
    runtime --> context
```

Sources: [README.md:38-82](), [CHANGELOG.md:379-410]()

---

