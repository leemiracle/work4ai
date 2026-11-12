<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/xr-ai · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [AGENTS.md](AGENTS.md)
- [DEPENDENCIES.md](DEPENDENCIES.md)
- [README.md](README.md)
- [docs/source/_snippets/agent-setup-prompt.txt](docs/source/_snippets/agent-setup-prompt.txt)
- [docs/source/components/launcher-and-process-model.md](docs/source/components/launcher-and-process-model.md)
- [docs/source/getting_started/credentials.md](docs/source/getting_started/credentials.md)
- [docs/source/getting_started/index.md](docs/source/getting_started/index.md)
- [docs/source/getting_started/skills.md](docs/source/getting_started/skills.md)
- [docs/source/guides/adding-a-sample.md](docs/source/guides/adding-a-sample.md)
- [docs/source/guides/adding-cloudxr.md](docs/source/guides/adding-cloudxr.md)
- [docs/source/guides/spdx-headers.md](docs/source/guides/spdx-headers.md)
- [docs/source/index.md](docs/source/index.md)
- [docs/source/overview/architecture.md](docs/source/overview/architecture.md)
- [docs/source/reference/agent-sdk-tools.md](docs/source/reference/agent-sdk-tools.md)
- [docs/source/reference/simple-vlm-example.md](docs/source/reference/simple-vlm-example.md)
- [skills/getting-started/SKILL.md](skills/getting-started/SKILL.md)
- [skills/gh-manage-xr-ai-reviews/SKILL.md](skills/gh-manage-xr-ai-reviews/SKILL.md)
- [skills/gh-manage-xr-ai-reviews/agents/openai.yaml](skills/gh-manage-xr-ai-reviews/agents/openai.yaml)
- [skills/gh-review-xr-ai/SKILL.md](skills/gh-review-xr-ai/SKILL.md)
- [skills/gh-review-xr-ai/agents/openai.yaml](skills/gh-review-xr-ai/agents/openai.yaml)
- [tests/pyproject.toml](tests/pyproject.toml)
- [tests/test_launcher_stack.py](tests/test_launcher_stack.py)
- [tests/test_vllm_stop.py](tests/test_vllm_stop.py)
- [utils/xr-ai-launcher/xr_ai_launcher/_stack.py](utils/xr-ai-launcher/xr_ai_launcher/_stack.py)

</details>



XR-AI is an open-source developer stack for building agentic AI systems within the CloudXR ecosystem [README.md:8-9](). It enables the creation of multimodal agents that can see, hear, reason over live physical context, and respond in real-time across Web, iOS/visionOS, and XR headset platforms [README.md:8-14]().

The repository provides an end-to-end foundation for spatial computing, integrating media routing, participant isolation, and GPU-accelerated AI services [README.md:11-14]().

## Three-Tier Architecture

The project follows a modular three-tier architecture designed to separate transport, rendering, and AI logic, allowing each layer to evolve independently [README.md:11-14](), [docs/source/overview/architecture.md:37-38]().

```mermaid
graph TD
    subgraph "Agent SDK Tier"
        ["xr-ai-hub"] --> ["xr-ai-runtime"]
        ["xr-ai-runtime"] --> ["xr-ai-models"]
        ["xr-ai-runtime"] --> ["xr-ai-tools"]
        ["xr-ai-runtime"] --> ["xr-ai-voice"]
    end

    subgraph "Services Tier"
        ["device-io-hub"] --> ["vllm-server"]
        ["device-io-hub"] --> ["video-memory-service"]
    end

    subgraph "Utilities Tier"
        ["xr-ai-launcher"] --> ["xr-ai-logging"]
    end

    style ["xr-ai-hub"] stroke-dasharray: 5 5
    style ["device-io-hub"] stroke-dasharray: 5 5
    style ["xr-ai-launcher"] stroke-dasharray: 5 5
```
Sources: [README.md:60-72](), [docs/source/overview/architecture.md:20-47]()

### 1. Agent SDK (`agent-sdk/`)
The SDK is the primary interface for building agent logic. It is modularized to minimize dependency bloat, with the core IPC layer (`xr-ai-hub`) depending only on `pyzmq` and `msgpack` [AGENTS.md:35](), [DEPENDENCIES.md:108-116]().
- **xr-ai-hub**: The agent-facing IPC boundary using `ProcessorEndpoint` [agent-sdk/xr-ai-hub/](), [AGENTS.md:35-37]()
- **xr-ai-runtime**: Manages `Agent` registration and typed participant-scoped message fan-out [agent-sdk/xr-ai-runtime/](), [AGENTS.md:53-56]()
- **xr-ai-models**: Provides typed protocols and factory functions (e.g., `make_llm`, `make_vlm`) for interacting with AI services [agent-sdk/xr-ai-models/](), [AGENTS.md:42-47]()
- **xr-ai-tools**: A framework for native tools (e.g., `MarkerTrackingTool`) that agents can execute via model tool-calling loops [agent-sdk/xr-ai-tools/](), [AGENTS.md:51-52]()
- **xr-ai-voice**: A Pipecat-based pipeline for voice-enabled agents, handling VAD, STT, and streaming TTS [agent-sdk/xr-ai-voice/]()
- **xr-ai-web-events**: A telemetry viewer for monitoring agent events in a browser [agent-sdk/xr-ai-web-events/]()

Sources: [README.md:63](), [AGENTS.md:35-56](), [DEPENDENCIES.md:108-144]()

### 2. Services (`services/`)
Services provide the heavy-lifting capabilities for the stack, running as independent processes managed by the launcher [README.md:67](), [docs/source/overview/architecture.md:8-13]().
- **device-io-hub**: The central routing service handling transport connections, participant isolation, and media distribution [services/device-io-hub/](), [docs/source/overview/architecture.md:51-54]()
- **AI Inference Services**: Dockerized vLLM-backed servers for Vision-Language Models (VLM) and Large Language Models (LLM) [README.md:65](), [docs/source/overview/architecture.md:43-46]()
- **Capability Services**: Specialized RPC services like `video-memory-service` for frame history and `rag-service` for retrieval [tests/pyproject.toml:33-34](), [docs/source/overview/architecture.md:43-46]()

Sources: [README.md:67](), [docs/source/overview/architecture.md:8-16]()

### 3. Utilities (`utils/`)
Shared infrastructure used across the repository for process management, logging, and diagnostics [README.md:68]().
- **xr-ai-launcher**: A `stdlib`-only process manager that orchestrates the startup of the hub, workers, and model servers using the `--ready-file` protocol [utils/xr-ai-launcher/](), [AGENTS.md:90-94](), [docs/source/components/launcher-and-process-model.md:65-73]()
- **xr-ai-logging**: A unified logging sink based on `loguru` [utils/xr-ai-logging/](), [tests/test_launcher_stack.py:59-62]()

Sources: [README.md:68](), [utils/xr-ai-launcher/xr_ai_launcher/_stack.py:1-33](), [docs/source/components/launcher-and-process-model.md:65-81]()

## Natural Language to Code Entity Mapping

The following diagrams illustrate how high-level system concepts map to specific code entities and communication protocols across the architecture tiers.

**Agent-Hub Communication Flow**
```mermaid
graph LR
    subgraph "Client Space"
        ["StreamSession"] --> ["LiveKitBackend"]
    end

    subgraph "Service Space (device-io-hub)"
        ["LiveKitConnector"] -- "ZMQ PUSH/PULL" --> ["HubEndpoint"]
        ["HubEndpoint"] -- "ZMQ PUB/SUB" --> ["ProcessorEndpoint"]
    end

    subgraph "Agent SDK Space"
        ["ProcessorEndpoint"] --> ["AgentRuntime"]
        ["AgentRuntime"] --> ["AgentClass"]
    end

    style ["StreamSession"] stroke-dasharray: 5 5
    style ["AgentClass"] stroke-dasharray: 5 5
```
Sources: [README.md:11-14](), [docs/source/overview/architecture.md:28-47](), [AGENTS.md:33-40]()

**Multimodal Tool Execution Architecture**
```mermaid
graph TD
    subgraph "Agent Logic"
        ["Agent"] --> ["ToolSet"]
        ["ToolSet"] --> ["run_tool_loop"]
    end

    subgraph "Tools (xr-ai-tools)"
        ["run_tool_loop"] --> ["CurrentFrameTool"]
        ["run_tool_loop"] --> ["MarkerTrackingTool"]
    end

    subgraph "AI Services (xr-ai-models)"
        ["CurrentFrameTool"] -- "VLMService.request" --> ["vllm_backend"]
        ["Agent"] -- "LLMService.request" --> ["llama_nemotron_llm_server"]
    end

    style ["vllm_backend"] stroke-width:2px
    style ["llama_nemotron_llm_server"] stroke-width:2px
```
Sources: [AGENTS.md:51-54](), [DEPENDENCIES.md:119-144]()

## Getting Started

<a id="1.1"></a>

For new developers, XR AI provides step-by-step setup guides covering hardware and software requirements, installing `uv`, running model servers, launching `simple-vlm-example` and `xr-render-demo`, and connecting a client [README.md:18-31](), [docs/source/index.md:50-55]().

For details, see [Getting Started](#1.1) in the official documentation or child pages [README.md:20-25]().

Sources: [README.md:18-31](), [docs/source/index.md:50-55]()

## Repository Layout and Conventions

<a id="1.2"></a>

The repository top-level directory structure (`agent-sdk/`, `services/`, `model-server-samples/`, `utils/`, `agent-samples/`, `client-samples/`, `tests/`, `docs/`, `skills/`) organizes code by tier [README.md:58-72](), [AGENTS.md:15-29](). Coding conventions enforce strict SPDX header requirements [docs/source/guides/spdx-headers.md:8-18](), ruff linting, and Developer Certificate of Origin (DCO) sign-offs. Reusable agent playbooks are maintained under `skills/` [skills/getting-started/SKILL.md:1-20]().

For details, see [Repository Layout and Conventions](#1.2) and `AGENTS.md` [README.md:73-74](), [AGENTS.md:6-10]().

Sources: [README.md:58-74](), [AGENTS.md:6-29](), [docs/source/guides/spdx-headers.md:8-18]()

---

This wiki is divided into major sections corresponding to these architectural layers and workflows. For a complete list of terms and definitions, refer to the [Glossary](#6).

Sources: [README.md:18-31](), [docs/source/index.md:83-92]()

---

