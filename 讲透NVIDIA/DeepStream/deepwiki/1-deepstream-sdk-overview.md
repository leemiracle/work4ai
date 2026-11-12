<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/DeepStream · page 1 DeepStream SDK Overview · fetched 2026-10-26 -->

# DeepStream SDK Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/ISSUE_TEMPLATE/bug_report.md](.github/ISSUE_TEMPLATE/bug_report.md)
- [.gitignore](.gitignore)
- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [THIRD_PARTY_LICENSES.txt](THIRD_PARTY_LICENSES.txt)
- [build/BUILD.md](build/BUILD.md)
- [build/build.sh](build/build.sh)
- [includes/.gitkeep](includes/.gitkeep)
- [scripts/print_env.sh](scripts/print_env.sh)
- [src/.gitkeep](src/.gitkeep)
- [src/README.md](src/README.md)
- [src/apps/.gitkeep](src/apps/.gitkeep)
- [src/apps/reference_apps/deepstream-tracker-3d-multi-view/README.md](src/apps/reference_apps/deepstream-tracker-3d-multi-view/README.md)
- [src/apps/reference_apps/deepstream-tracker-3d-multi-view/docs/manual-setup.md](src/apps/reference_apps/deepstream-tracker-3d-multi-view/docs/manual-setup.md)
- [src/apps/reference_apps/deepstream-tracker-3d-multi-view/scripts/setup_prerequisites.sh](src/apps/reference_apps/deepstream-tracker-3d-multi-view/scripts/setup_prerequisites.sh)
- [src/apps/sample_apps/README.md](src/apps/sample_apps/README.md)
- [src/apps/sample_apps/deepstream-infer-tensor-meta-test/README](src/apps/sample_apps/deepstream-infer-tensor-meta-test/README)
- [src/gst-plugins/.gitkeep](src/gst-plugins/.gitkeep)
- [src/gst-plugins/README.md](src/gst-plugins/README.md)
- [src/service-maker/.gitkeep](src/service-maker/.gitkeep)
- [src/utils/.gitkeep](src/utils/.gitkeep)
- [src/utils/README.md](src/utils/README.md)
- [src/utils/nvds_msgapi/amqp_protocol_adaptor/Makefile](src/utils/nvds_msgapi/amqp_protocol_adaptor/Makefile)
- [src/utils/nvds_msgapi/kafka_protocol_adaptor/Makefile](src/utils/nvds_msgapi/kafka_protocol_adaptor/Makefile)
- [src/utils/nvds_msgapi/mqtt_protocol_adaptor/Makefile](src/utils/nvds_msgapi/mqtt_protocol_adaptor/Makefile)
- [src/utils/nvds_msgapi/redis_protocol_adaptor/Makefile](src/utils/nvds_msgapi/redis_protocol_adaptor/Makefile)
- [tools/.gitkeep](tools/.gitkeep)

</details>



The [NVIDIA DeepStream SDK](https://developer.nvidia.com/deepstream-sdk) is a high-performance streaming analytics toolkit for AI-based video and image understanding [README.md:3-3](). It provides a GStreamer-based framework to build multi-stream, multi-model inference pipelines on NVIDIA GPUs, supporting both discrete GPUs (dGPU) and Jetson platforms [README.md:3-5]().

DeepStream 9.1 integrates hardware-accelerated video decoding/encoding, TensorRT-based inference, multi-object tracking, and message-broker connectivity into a unified architecture for real-time video analytics [README.md:5-5]().

## System Architecture

DeepStream applications are built on top of the GStreamer multimedia framework. The repository provides a collection of specialized plugins and utility libraries that interface with NVIDIA's compute stack (CUDA, TensorRT, and Video Codec SDK).

### Component Stack
The SDK is organized into several functional layers:

*   **GStreamer Plugins**: Core building blocks for inference (`nvinfer`), muxing (`nvstreammux`), and visualization (`nvdsosd`) [src/README.md:60-62]().
*   **Utility Libraries**: Low-level libraries for metadata management, messaging protocols, and sensor fusion [src/README.md:72-76]().
*   **Service Maker SDK**: A declarative C++/Python SDK that simplifies pipeline construction [src/README.md:48-52]().
*   **Reference Applications**: End-to-end examples for complex use cases like 3D tracking and LiDAR fusion [src/README.md:34-38]().

### Code-to-System Mapping
The following diagram illustrates how repository entities map to the runtime system architecture.

**System Entity to Code Path Mapping**
```mermaid
graph TD
    subgraph "GStreamer Space"
        GstPlugin["Gst-Plugins"]
        GstUtils["Gst-Utilities"]
    end

    subgraph "NVIDIA Compute Space"
        TRT["TensorRT Inference"]
        CUDA["CUDA Processing"]
    end

    subgraph "Application Space"
        AppBin["Reference Apps"]
        SM["Service Maker SDK"]
    end

    %% Mapping relationships
    GstPlugin -->|"src/gst-plugins/"| [src/README.md:14-14]
    GstUtils -->|"src/gst-utils/"| [src/README.md:64-70]
    AppBin -->|"src/apps/"| [src/README.md:28-46]
    SM -->|"src/service-maker/"| [src/README.md:48-57]
    
    %% Functional links
    GstPlugin --> TRT
    AppBin --> GstPlugin
    SM --> GstPlugin
```
Sources: [README.md:13-19](), [src/README.md:26-77]()

## Key Capabilities

*   **Inference Integration**: Supports TensorRT via `nvinfer` and Triton Inference Server via `nvinferserver` [src/README.md:96-96]().
*   **3D Sensing**: Advanced support for LiDAR and multi-camera 3D tracking (MV3DT) [src/apps/reference_apps/deepstream-tracker-3d-multi-view/README.md:18-24]().
*   **Cloud Connectivity**: Protocol adaptors for Kafka, MQTT, AMQP, and Redis [src/utils/nvds_msgapi/kafka_protocol_adaptor/Makefile:25-26](), [src/utils/nvds_msgapi/redis_protocol_adaptor/Makefile:22-23]().
*   **Observability**: Integrated OpenTelemetry (OTEL) and Prometheus metrics for pipeline monitoring [README.md:27-27]().
*   **Vision-Language Models**: Native VLM support (e.g., Cosmos Reason 2) via the `vLLM` plugin [CHANGELOG.md:6-6]().

## Supported Platforms

DeepStream 9.1 supports three primary architectural targets:

| Platform | Architecture | OS / Requirements |
| :--- | :--- | :--- |
| **x86 dGPU** | `x86_64` | Ubuntu 24.04, CUDA 13.2, TensorRT 10.16.x [README.md:68-68]() |
| **Jetson** | `aarch64` | JetPack 7.2 GA, CUDA 13.2, TensorRT 10.16.x [README.md:69-69]() |
| **SBSA / DGX Spark** | `aarch64` | Bare-metal not supported; run via SBSA Docker container [README.md:70-70]() |

Sources: [README.md:64-71](), [build/BUILD.md:26-30]()

## Repository Organization

The repository is structured to separate core logic, application templates, and developer tooling.

**Repository Structure Overview**
```mermaid
graph TD
    Root["/ (Repo Root)"]
    Root --> BuildDir["build/ (Build Scripts)"]
    Root --> SrcDir["src/ (Core Source Code)"]
    Root --> ToolsDir["tools/ (Dev Utilities)"]
    Root --> SkillsDir["skills/ (AI Agent Skills)"]

    SrcDir --> Apps["apps/ (Sample/Ref Apps)"]
    SrcDir --> Plugins["gst-plugins/ (GStreamer)"]
    SrcDir --> Utils["utils/ (Shared Libs)"]
    SrcDir --> SM["service-maker/ (SDK)"]

    BuildDir --> BuildSH["build.sh"]
    
    %% Precise Code Entities
    BuildSH -->|"Orchestrates"| [build/build.sh:17-18]
    Apps -->|"Contains"| [src/README.md:28-46]
    SkillsDir -->|"Contains"| [README.md:29-39]
```
Sources: [README.md:13-39](), [src/README.md:26-77]()

## Detailed Documentation Sections

For deeper technical details, please refer to the following child pages:

*   **[Getting Started & Build System](#1.1)**: Guide to building from source using `build/build.sh`, platform detection, and the install/uninstall lifecycle.
*   **[Docker Containers & Host Provisioning](#1.2)**: Instructions for building Docker images and using Ansible for host setup.
*   **[Open-Source Dependencies](#1.3)**: Details on the libraries compiled by `install_opensource_deps.sh`, including OpenTelemetry and Triton Client.

For runtime usage, the primary entry point is the `deepstream-app` reference application [README.md:79-83]().

Sources: [README.md:52-62](), [build/BUILD.md:161-170]()

---

