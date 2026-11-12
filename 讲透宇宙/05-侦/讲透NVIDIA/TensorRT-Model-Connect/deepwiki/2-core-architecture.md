<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/TensorRT-Model-Connect · page 2 Core Architecture · fetched 2026-10-26 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CMakeLists.txt](CMakeLists.txt)
- [examples/trtmc_benchmark_worker.cpp](examples/trtmc_benchmark_worker.cpp)
- [include/trtmc/pipeline.h](include/trtmc/pipeline.h)
- [src/cli/args.cpp](src/cli/args.cpp)
- [src/cli/args.h](src/cli/args.h)
- [src/cli/main.cpp](src/cli/main.cpp)
- [src/runtime/backend/backend_loader.cpp](src/runtime/backend/backend_loader.cpp)
- [src/runtime/backend/backend_loader.h](src/runtime/backend/backend_loader.h)
- [src/runtime/backend/rtx_backend.cpp](src/runtime/backend/rtx_backend.cpp)
- [src/runtime/backend/trt_backend.cpp](src/runtime/backend/trt_backend.cpp)
- [src/runtime/backend/trt_logger.cpp](src/runtime/backend/trt_logger.cpp)
- [src/runtime/backend/trt_logger.h](src/runtime/backend/trt_logger.h)
- [src/runtime/backend/trt_version.cpp](src/runtime/backend/trt_version.cpp)
- [src/runtime/backend/trt_version.h](src/runtime/backend/trt_version.h)
- [src/runtime/core/cuda_common.cpp](src/runtime/core/cuda_common.cpp)
- [src/runtime/core/cuda_common.h](src/runtime/core/cuda_common.h)
- [src/runtime/core/trt_common.cpp](src/runtime/core/trt_common.cpp)
- [src/runtime/core/trt_common.h](src/runtime/core/trt_common.h)
- [src/runtime/models/dinov3/pipeline.cpp](src/runtime/models/dinov3/pipeline.cpp)
- [src/runtime/models/dinov3/pipeline.h](src/runtime/models/dinov3/pipeline.h)
- [src/runtime/providers/optimized_runtime_factory.h](src/runtime/providers/optimized_runtime_factory.h)
- [src/runtime/providers/optimized_runtime_host.cpp](src/runtime/providers/optimized_runtime_host.cpp)
- [src/runtime/registry/pipeline_factory.cpp](src/runtime/registry/pipeline_factory.cpp)
- [src/utils/data_dir.cpp](src/utils/data_dir.cpp)
- [src/utils/data_dir.h](src/utils/data_dir.h)
- [src/utils/json_helpers.cpp](src/utils/json_helpers.cpp)
- [src/utils/json_helpers.h](src/utils/json_helpers.h)
- [tests/cpp/fakes/fake_optimized_runtime_provider.cpp](tests/cpp/fakes/fake_optimized_runtime_provider.cpp)
- [tests/cpp/models/dinov3/test_dinov3_pipeline.cpp](tests/cpp/models/dinov3/test_dinov3_pipeline.cpp)
- [tests/cpp/test_backend_loader.cpp](tests/cpp/test_backend_loader.cpp)
- [tests/cpp/test_cli_args.cpp](tests/cpp/test_cli_args.cpp)
- [tests/cpp/test_data_dir.cpp](tests/cpp/test_data_dir.cpp)
- [tests/cpp/test_json_helpers.cpp](tests/cpp/test_json_helpers.cpp)
- [tests/cpp/test_pipeline_api.cpp](tests/cpp/test_pipeline_api.cpp)
- [tests/cpp/test_trt_logger.cpp](tests/cpp/test_trt_logger.cpp)
- [tests/e2e/models/qwen/edge_llm_adapter/test_runtime_contract.py](tests/e2e/models/qwen/edge_llm_adapter/test_runtime_contract.py)

</details>



TensorRT-Model-Connect (TRTMC) provides a streamlined build-to-runtime pipeline for deploying optimized AI models. This page offers a high-level overview of the core architectural components, focusing on the `.bundle` artifact as the central boundary between the build and runtime phases, and the two primary bundle shapes: native and optimized.

The TRTMC workflow begins with model definition and configuration, proceeds through a build process that generates a `.bundle` file, and culminates in the loading and execution of this bundle by the TRTMC runtime. Each of these stages involves distinct components and processes, which are detailed in linked child pages.

## Build Pipeline: From Checkpoint to .bundle

The build pipeline is responsible for taking a source model (typically a Hugging Face checkpoint) and transforming it into an optimized `.bundle` artifact. This process involves several key steps: resolving the model, selecting an appropriate "family plugin" for model-specific optimizations, routing to either a native or optimized builder, compiling TensorRT engines, and finally packaging everything into the `.bundle` file.

The `trtmc build` CLI command [src/cli/main.cpp:9-9]() or the `tensorrt_model_connect.build()` Python API orchestrates this process. Model configurations are managed through `ModelConfig` objects, and the `FamilyPlugin` protocol defines how different model architectures integrate into the build system. The choice between native and optimized builders depends on the desired level of optimization and the target deployment environment.

For a detailed explanation of how models are resolved, plugins are selected, and TensorRT engines are compiled, see [Build Pipeline: From Checkpoint to .bundle](#2.1).

Sources:
- [src/cli/main.cpp:9-9]()

## Bundle Format and Runtime Lifecycle

The `.bundle` file is the self-contained artifact produced by the build pipeline. It encapsulates all necessary components for model inference, including TensorRT engines, configuration data, and any required assets. TRTMC supports two main "bundle shapes":

1.  **Native Bundles**: These bundles contain TensorRT engines and rely on the TRTMC C++ runtime to load and execute them directly. They are typically used for maximum performance and control.
2.  **Optimized Bundles**: These bundles leverage external optimized runtimes (e.g., TVM, ONNX Runtime) for execution. They might contain intermediate representations or specialized engine formats tailored for these runtimes.

The `PipelineFactory` is responsible for loading a `.bundle` file. It first inspects the bundle's header to determine its `runtime_strategy` [src/runtime/registry/pipeline_factory.cpp:125-125]() and then dispatches to the appropriate loading mechanism. This involves loading necessary Dynamic Shared Objects (DSOs) for model-specific logic and backend runtimes, and constructing a `PipelineContext` to manage the inference lifecycle.

For an in-depth look at the `.bundle` file structure, the loading process, and the differences between native and optimized load paths, see [Bundle Format and Runtime Lifecycle](#2.2).

Sources:
- [src/runtime/registry/pipeline_factory.cpp:125-125]()

## C++ Public API (IPipeline and CLI)

TRTMC provides both a command-line interface (CLI) and a C++ public API for interacting with models.

The `trtmc` CLI [src/cli/main.cpp:6-30]() offers a range of commands for common tasks such as `build`, `run`, `transcribe`, `generate-video`, `classify`, `segment`, `embed`, `rerank`, `solve`, `inspect`, and `version`. These commands provide a convenient way to interact with TRTMC models without writing custom code. The CLI arguments are parsed by `trtmc::cli::parse_args` [src/cli/args.cpp:127-127]().

The C++ `IPipeline` API [include/trtmc/pipeline.h:8-12]() is the programmatic interface for integrating TRTMC models into C++ applications. It defines methods like `generate`, `transcribe`, `generate_image`, `embed`, etc., allowing developers to load bundles and perform inference directly within their C++ code. An example of a concrete pipeline implementation is `Dinov3ImageFeaturePipeline` [src/runtime/models/dinov3/pipeline.h:20-21](), which implements `IPipeline` and `IImageFeatureExtractor`.

For a comprehensive guide to the `trtmc` CLI commands and the C++ `IPipeline` API, including usage examples and available functionalities, see [C++ Public API (IPipeline and CLI)](#2.3).

Sources:
- [src/cli/main.cpp:6-30]()
- [src/cli/args.cpp:127-127]()
- [include/trtmc/pipeline.h:8-12]()
- [src/runtime/models/dinov3/pipeline.h:20-21]()

## Build System: CMake, DSO Boundaries, and Packaging

The TRTMC build system is primarily managed by CMake [CMakeLists.txt:4-5](). It handles the compilation of C++ components, the generation of Dynamic Shared Objects (DSOs), and the packaging of the final release artifacts.

A key aspect of the build system is the scanning of `MODEL.toml` descriptors. These files define model-specific metadata and are used to generate model plugin registrations, allowing the TRTMC runtime to discover and load model-specific logic.

The native link boundary defines the separation between `trtmc_core`, model DSOs, and backend DSOs. This modular design allows for flexible integration of different models and TensorRT versions. For instance, `libtrtmc_backend_trt.so` [src/runtime/backend/trt_backend.cpp:6-6]() provides the standard TensorRT backend, while `libtrtmc_backend_rtx.so` [src/runtime/backend/rtx_backend.cpp:6-6]() provides the TensorRT-RTX backend.

Python packaging is handled via `pyproject.toml` and `conanfile.py`, which define the dependencies and build steps for the Python wheel. The release wheel build process ensures that all necessary components are correctly packaged for distribution.

For a detailed breakdown of the CMake build process, DSO boundaries, and the Python packaging mechanisms, see [Build System: CMake, DSO Boundaries, and Packaging](#2.4).

Sources:
- [CMakeLists.txt:4-5]()
- [src/runtime/backend/trt_backend.cpp:6-6]()
- [src/runtime/backend/rtx_backend.cpp:6-6]()

## Architectural Overview

The following diagram illustrates the high-level architecture of TensorRT-Model-Connect, showing the relationship between the build and runtime components and the central role of the `.bundle` artifact.

```mermaid
graph TD
    subgraph "Build Time"
        A[Hugging Face Checkpoint] --> B(ModelConfig)
        B --> C{FamilyPlugin Selection}
        C --> D{Native Builder}
        C --> E{Optimized Builder}
        D --> F[Compile TensorRT Engines]
        E --> F
        F --> G[.bundle Artifact]
    end

    subgraph "Run Time"
        G --> H(PipelineFactory.load())
        H --> I{runtime_strategy}
        I --> J[Load Model DSOs]
        I --> K[Load Backend DSOs]
        J --> L(PipelineContext)
        K --> L
        L --> M[IPipeline API / trtmc CLI]
    end

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bbf,stroke:#333,stroke-width:2px
    style D fill:#bbf,stroke:#333,stroke-width:2px
    style E fill:#bbf,stroke:#333,stroke-width:2px
    style F fill:#bbf,stroke:#333,stroke-width:2px
    style G fill:#f9f,stroke:#333,stroke-width:2px
    style H fill:#bbf,stroke:#333,stroke-width:2px
    style I fill:#bbf,stroke:#333,stroke-width:2px
    style J fill:#bbf,stroke:#333,stroke-width:2px
    style K fill:#bbf,stroke:#333,stroke-width:2px
    style L fill:#bbf,stroke:#333,stroke-width:2px
    style M fill:#f9f,stroke:#333,stroke-width:2px
```
Sources:
- [src/cli/main.cpp]()
- [src/runtime/registry/pipeline_factory.cpp]()
- [include/trtmc/pipeline.h]()

## Code Entity Map: CLI to C++ API

This diagram illustrates how the `trtmc` CLI commands map to the underlying C++ `IPipeline` API and its implementations.

```mermaid
graph TD
    subgraph "trtmc CLI (src/cli/main.cpp)"
        CLI_BUILD["trtmc build"] --> Cpp_BUILD_LOGIC[Build Logic]
        CLI_RUN["trtmc run"] --> Cpp_LOAD_PIPELINE[trtmc::load()]
        CLI_TRANSCRIBE["trtmc transcribe"] --> Cpp_LOAD_PIPELINE
        CLI_GENERATE_VIDEO["trtmc generate-video"] --> Cpp_LOAD_PIPELINE
        CLI_CLASSIFY["trtmc classify"] --> Cpp_LOAD_PIPELINE
        CLI_EXTRACT_FEATURES["trtmc extract-features"] --> Cpp_LOAD_PIPELINE
        CLI_DETECT["trtmc detect"] --> Cpp_LOAD_PIPELINE
        CLI_INSPECT["trtmc inspect"] --> Cpp_INSPECT_BUNDLE[trtmc::InspectBundle()]
        CLI_VERSION["trtmc version"] --> Cpp_VERSION_INFO[Version Info]
    end

    subgraph "C++ API (include/trtmc/pipeline.h)"
        Cpp_LOAD_PIPELINE --> IPipeline_LOAD[trtmc::load(bundle_path, LoadOptions)]
        IPipeline_LOAD --> IPipeline_INTERFACE[IPipeline*]
        IPipeline_INTERFACE --> IPipeline_GENERATE[generate()]
        IPipeline_INTERFACE --> IPipeline_TRANSCRIBE[transcribe()]
        IPipeline_INTERFACE --> IPipeline_GENERATE_IMAGE[generate_image()]
        IPipeline_INTERFACE --> IPipeline_EMBED[embed()]
        IPipeline_INTERFACE --> IPipeline_EXTRACT_IMAGE_FEATURES[IImageFeatureExtractor::extract_image_features()]
    end

    subgraph "C++ Implementations"
        IPipeline_GENERATE --> ConcretePipeline_GENERATE[e.g., TextGenerationPipeline::generate()]
        IPipeline_TRANSCRIBE --> ConcretePipeline_TRANSCRIBE[e.g., WhisperPipeline::transcribe()]
        IPipeline_EXTRACT_IMAGE_FEATURES --> Dinov3Pipeline_EXTRACT[Dinov3ImageFeaturePipeline::extract_image_features()]
        Dinov3Pipeline_EXTRACT --> TrtModule_FORWARD[TrtModule::forward()]
    end

    style CLI_BUILD fill:#f9f,stroke:#333,stroke-width:2px
    style CLI_RUN fill:#f9f,stroke:#333,stroke-width:2px
    style CLI_TRANSCRIBE fill:#f9f,stroke:#333,stroke-width:2px
    style CLI_GENERATE_VIDEO fill:#f9f,stroke:#333,stroke-width:2px
    style CLI_CLASSIFY fill:#f9f,stroke:#333,stroke-width:2px
    style CLI_EXTRACT_FEATURES fill:#f9f,stroke:#333,stroke-width:2px
    style CLI_DETECT fill:#f9f,stroke:#333,stroke-width:2px
    style CLI_INSPECT fill:#f9f,stroke:#333,stroke-width:2px
    style CLI_VERSION fill:#f9f,stroke:#333,stroke-width:2px

    style Cpp_BUILD_LOGIC fill:#bbf,stroke:#333,stroke-width:2px
    style Cpp_LOAD_PIPELINE fill:#bbf,stroke:#333,stroke-width:2px
    style Cpp_INSPECT_BUNDLE fill:#bbf,stroke:#333,stroke-width:2px
    style Cpp_VERSION_INFO fill:#bbf,stroke:#333,stroke-width:2px

    style IPipeline_LOAD fill:#bbf,stroke:#333,stroke-width:2px
    style IPipeline_INTERFACE fill:#bbf,stroke:#333,stroke-width:2px
    style IPipeline_GENERATE fill:#bbf,stroke:#333,stroke-width:2px
    style IPipeline_TRANSCRIBE fill:#bbf,stroke:#333,stroke-width:2px
    style IPipeline_GENERATE_IMAGE fill:#bbf,stroke:#333,stroke-width:2px
    style IPipeline_EMBED fill:#bbf,stroke:#333,stroke-width:2px
    style IPipeline_EXTRACT_IMAGE_FEATURES fill:#bbf,stroke:#333,stroke-width:2px

    style ConcretePipeline_GENERATE fill:#bbf,stroke:#333,stroke-width:2px
    style ConcretePipeline_TRANSCRIBE fill:#bbf,stroke:#333,stroke-width:2px
    style Dinov3Pipeline_EXTRACT fill:#bbf,stroke:#333,stroke-width:2px
    style TrtModule_FORWARD fill:#bbf,stroke:#333,stroke-width:2px
```
Sources:
- [src/cli/main.cpp]()
- [src/cli/args.cpp]()
- [include/trtmc/pipeline.h]()
- [src/runtime/models/dinov3/pipeline.h]()
- [src/runtime/models/dinov3/pipeline.cpp]()

---

