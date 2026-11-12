<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cosmos · page 8 NIM Microservice Deployment · fetched 2026-10-26 -->

# NIM Microservice Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cookbooks/cosmos3/nim/README.md](cookbooks/cosmos3/nim/README.md)
- [cookbooks/cosmos3/nim/acknowledgements/2.0.0.md](cookbooks/cosmos3/nim/acknowledgements/2.0.0.md)
- [cookbooks/cosmos3/nim/acknowledgements/README.md](cookbooks/cosmos3/nim/acknowledgements/README.md)
- [cookbooks/cosmos3/nim/prerequisites.md](cookbooks/cosmos3/nim/prerequisites.md)
- [cookbooks/cosmos3/nim/release-notes.md](cookbooks/cosmos3/nim/release-notes.md)
- [cookbooks/cosmos3/nim/support-matrix.md](cookbooks/cosmos3/nim/support-matrix.md)

</details>



This page provides a high-level overview of the NVIDIA Cosmos 3 NIM (NVIDIA Inference Microservice) turnkey container offering, `nvcr.io/nim/nvidia/cosmos3`. This container provides a unified runtime for both the Cosmos 3 Generator and Reasoner models. It covers the core functionalities, prerequisites, support matrix, release notes, acknowledgements, and the Python example suite. For detailed deployment instructions, API references, and specific examples, please refer to the linked child pages.

The Cosmos 3 NIM container simplifies the deployment of Cosmos 3 models for world generation and multimodal reasoning. It encapsulates the necessary dependencies and configurations, allowing users to quickly get started with either the Generator or Reasoner runtime. The container is designed to be flexible, supporting various model variants, precisions, and performance profiles, which are automatically selected based on the host GPU capabilities and user preferences.

Sources:
- [cookbooks/cosmos3/nim/README.md:6-12]()

## NIM Deployment and Configuration

The NIM container offers a streamlined approach to deploying Cosmos 3 models. Users can choose between running the Generator for image/video generation, action modeling, and transfer tasks, or the Reasoner for OpenAI-compatible image/video understanding. The deployment process involves selecting the desired runtime (`NIM_MODEL_TYPE`), model variant (`NIM_MODEL_VARIANT`), and optionally a performance profile (`NIM_PERF_PROFILE`) or precision (`NIM_PRECISION`). The NIM automatically selects the best compatible profile for the visible GPUs based on these choices.

For detailed instructions on `docker run` invocations, environment variable configurations, Helm chart deployment, operational monitoring, bringing your own checkpoints, and using the `uv`/`pyproject` tooling for examples, see [NIM Deployment and Configuration](#8.1).

Sources:
- [cookbooks/cosmos3/nim/README.md:21-69]()

## NIM API Reference and Examples

The NIM exposes a standardized HTTP API for interacting with the deployed models. The Generator runtime primarily uses the `POST /v1/infer` endpoint for various generation and action tasks, while the Reasoner runtime uses `POST /v1/chat/completions` for chat-based reasoning and optionally the Responses API. The API supports base64 encoded video and JSON responses.

The Cosmos 3 NIM distribution includes a suite of Python examples demonstrating how to interact with the API for different tasks, such as text-to-image (`t2i.py`), text-to-video (`t2v.py`), image-to-video (`i2v.py`), video-to-video (`v2v.py`), transfer (`transfer.py`), action modeling (`action.py`), and reasoning (`reasoner.py`). These examples showcase the generation, reasoning, transfer, and action capabilities of the Cosmos 3 models.

For a comprehensive reference of the NIM HTTP API, including request and response formats, and detailed usage of the bundled example scripts, see [NIM API Reference and Examples](#8.2).

Sources:
- [cookbooks/cosmos3/nim/README.md:73-85]()
- [cookbooks/cosmos3/nim/README.md:113-121]()

## Prerequisites and Support Matrix

Before deploying the Cosmos 3 NIM, it is crucial to verify that the host system meets the necessary hardware and software prerequisites. This includes checking GPU compute capability, GPU count, per-device VRAM, and host RAM. The NIM supports various GPU architectures and topologies, with specific requirements for Generator and Reasoner runtimes across different precisions (BF16, FP8, NVFP4).

The support matrix provides detailed compatibility information, mapping model variants to required GPU compute capability, VRAM, and system memory. It also outlines the automatic precision behavior for each model and runtime. For unified-memory systems like DGX Spark and Jetson AGX Thor, specific considerations for shared memory thresholds are documented.

For a complete list of hardware requirements, instructions on inspecting unified-memory capacity, and detailed support matrix tables, see [Prerequisites for the Cosmos3 Certified NIM](prerequisites.md) and [Cosmos3 Certified NIM support matrix](support-matrix.md).

Sources:
- [cookbooks/cosmos3/nim/prerequisites.md:1-37]()
- [cookbooks/cosmos3/nim/support-matrix.md:1-125]()

## Release Notes and Acknowledgements

The Cosmos 3 NIM is a unified container image that combines both Generator and Reasoner runtimes. The initial release provides a comprehensive solution for deploying Cosmos 3 models.

The NIM container includes various open-source components, and their respective licenses and acknowledgements are provided. Users can find detailed license information within the running container at `/v1/license`, as well as in specific files like `/opt/nim/LICENSE`, `/opt/nim/MODEL_LICENSE`, and `/opt/nim/NOTICE`.

For the latest updates, new features, and bug fixes, refer to the [Cosmos3 Certified NIM release notes](release-notes.md). For a complete list of acknowledgements and license information for the container image `nvcr.io/nim/nvidia/cosmos3:2.0.0`, see [Cosmos3 NIM acknowledgements](acknowledgements/2.0.0.md) and [Cosmos3 NIM acknowledgements](acknowledgements/README.md).

Sources:
- [cookbooks/cosmos3/nim/release-notes.md:1-17]()
- [cookbooks/cosmos3/nim/acknowledgements/2.0.0.md:1-22]()
- [cookbooks/cosmos3/nim/acknowledgements/README.md:1-6]()

## NIM Runtime Architecture

The Cosmos 3 NIM container provides a unified runtime for both Generator and Reasoner models. While the container image `nvcr.io/nim/nvidia/cosmos3:2.0.0` includes both runtimes, each container instance runs only one at a time, determined by configuration at launch.

```mermaid
graph TD
    subgraph "NIM Container (nvcr.io/nim/nvidia/cosmos3:2.0.0)"
        A[NIM_MODEL_TYPE="generator"] --> B{Generator Runtime}
        A --> C{Reasoner Runtime}
        B -- "POST /v1/infer" --> D[Generation Tasks]
        B --> E[Action Tasks]
        B --> F[Transfer Tasks]
        C -- "POST /v1/chat/completions" --> G[Reasoning Tasks]
        C -- "Responses API" --> H[Structured Responses]
    end

    subgraph "Configuration"
        NIM_MODEL_TYPE["NIM_MODEL_TYPE (generator/reasoner)"]
        NIM_MODEL_VARIANT["NIM_MODEL_VARIANT (nano/super/nano-droid/super-t2i/etc.)"]
        NIM_PERF_PROFILE["NIM_PERF_PROFILE (latency/throughput)"]
        NIM_PRECISION["NIM_PRECISION (FP8/BF16/NVFP4)"]
    end

    NIM_MODEL_TYPE --> A
    NIM_MODEL_VARIANT --> B
    NIM_MODEL_VARIANT --> C
    NIM_PERF_PROFILE --> B
    NIM_PRECISION --> B
    NIM_PRECISION --> C

    D -- "t2i.py, t2v.py, i2v.py, v2v.py" --> "examples/outputs/"
    E -- "action.py" --> "examples/outputs/"
    F -- "transfer.py" --> "examples/outputs/"
    G -- "reasoner.py" --> "examples/outputs/"
    H -- "reasoner_responses.py" --> "examples/outputs/"

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#bbf,stroke:#333,stroke-width:2px
    style C fill:#bbf,stroke:#333,stroke-width:2px
    style D fill:#ccf,stroke:#333,stroke-width:1px
    style E fill:#ccf,stroke:#333,stroke-width:1px
    style F fill:#ccf,stroke:#333,stroke-width:1px
    style G fill:#ccf,stroke:#333,stroke-width:1px
    style H fill:#ccf,stroke:#333,stroke-width:1px
```
**Diagram: NIM Runtime Selection and Task Flow**

Sources:
- [cookbooks/cosmos3/nim/README.md:6-12]()
- [cookbooks/cosmos3/nim/README.md:21-69]()
- [cookbooks/cosmos3/nim/README.md:73-85]()
- [cookbooks/cosmos3/nim/README.md:113-121]()

## Model Variants and Capabilities

The NIM supports various Cosmos 3 model variants, each optimized for specific tasks or performance characteristics. These variants are selected using the `NIM_MODEL_VARIANT` environment variable.

| Variant | Supported Use | Automatic Precision Behavior |
|---|---|---|
| `nano` | General-purpose generation and compatible Generator tasks | Prefer FP8 when compatible; otherwise fall back |
| `nano-droid` | DROID policy with an action-only response; BF16 only | BF16 only |
| `super` | General-purpose generation and compatible Generator tasks | Prefer FP8 when compatible; otherwise fall back |
| `super-t2i` | Full-step T2I only | Prefer FP8 when compatible; otherwise fall back |
| `super-t2i-4step` | Four-step text-to-image only | Prefer FP8 when compatible; otherwise fall back |
| `super-i2v` | Full-step I2V only | Prefer FP8 when compatible; otherwise fall back |
| `super-i2v-4step` | Four-step image-to-video only | Prefer FP8 when compatible; otherwise fall back |
| `nano` (Reasoner) | Image/video reasoning | Prefer BF16 on compute capability 8.0 through 8.8, FP8 on 8.9 through 9.x, and NVFP4 on 10.0 or newer when compatible |
| `super` (Reasoner) | Image/video reasoning | Prefer BF16 on compute capability 8.0 through 8.8, FP8 on 8.9 through 9.x, and NVFP4 on 10.0 or newer when compatible |

Sources:
- [cookbooks/cosmos3/nim/README.md:41-52]()
- [cookbooks/cosmos3/nim/support-matrix.md:25-33]()

## Example Workflow

The `cookbooks/cosmos3/nim` directory contains Python examples that demonstrate how to interact with the NIM. These examples utilize the `uv` dependency manager for environment setup.

```mermaid
graph TD
    A[Start NIM Container] --> B{Check NIM_MODEL_TYPE}
    B -- "generator" --> C[Generator Runtime Active]
    B -- "reasoner" --> D[Reasoner Runtime Active]

    C --> E[Run Generator Example: examples/t2i.py]
    D --> F[Run Reasoner Example: examples/reasoner.py --case image_caption]

    E -- "POST /v1/infer" --> G[NIM Generator API]
    F -- "POST /v1/chat/completions" --> H[NIM Reasoner API]

    G --> I[Generated Media (JPEG/MP4)]
    H --> J[Reasoning Output (Text/JSON)]

    I --> K["examples/outputs/"]
    J --> K

    subgraph "Client Tooling"
        L["cd cookbooks/cosmos3/nim"]
        M["export NIM_URL=${NIM_URL:-http://localhost:8000}"]
        N["curl -fsS '$NIM_URL/v1/health/ready'"]
        O["curl -fsS '$NIM_URL/v1/metadata'"]
        P["uv run python examples/t2i.py"]
        Q["uv run python examples/reasoner.py --case image_caption"]
    end

    L --> M --> N --> O
    O --> P
    O --> Q
    P --> E
    Q --> F
```
**Diagram: NIM Example Workflow**

Sources:
- [cookbooks/cosmos3/nim/README.md:99-121]()

---

