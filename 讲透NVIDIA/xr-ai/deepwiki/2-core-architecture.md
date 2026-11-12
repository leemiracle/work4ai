<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/xr-ai · page 2 Core Architecture · fetched 2026-10-26 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/source/components/launcher-and-process-model.md](docs/source/components/launcher-and-process-model.md)
- [docs/source/components/server-runtime.md](docs/source/components/server-runtime.md)
- [docs/source/getting_started/credentials.md](docs/source/getting_started/credentials.md)
- [docs/source/guides/adding-a-sample.md](docs/source/guides/adding-a-sample.md)
- [docs/source/guides/adding-cloudxr.md](docs/source/guides/adding-cloudxr.md)
- [docs/source/overview/architecture.md](docs/source/overview/architecture.md)
- [docs/source/reference/agent-sdk-tools.md](docs/source/reference/agent-sdk-tools.md)
- [docs/source/reference/migrations.md](docs/source/reference/migrations.md)
- [docs/source/reference/simple-vlm-example.md](docs/source/reference/simple-vlm-example.md)
- [services/device-io-hub/device_io_hub/__main__.py](services/device-io-hub/device_io_hub/__main__.py)
- [services/device-io-hub/device_io_hub/ipc/_connector.py](services/device-io-hub/device_io_hub/ipc/_connector.py)
- [services/device-io-hub/device_io_hub/ipc/_hub.py](services/device-io-hub/device_io_hub/ipc/_hub.py)
- [services/device-io-hub/device_io_hub/transport/livekit/_room_client.py](services/device-io-hub/device_io_hub/transport/livekit/_room_client.py)
- [services/device-io-hub/device_io_hub/transport/livekit/connector.py](services/device-io-hub/device_io_hub/transport/livekit/connector.py)
- [tests/test_device_io_hub_startup.py](tests/test_device_io_hub_startup.py)
- [tests/test_launcher_stack.py](tests/test_launcher_stack.py)
- [tests/test_participant_events.py](tests/test_participant_events.py)
- [tests/test_vllm_stop.py](tests/test_vllm_stop.py)
- [utils/xr-ai-launcher/xr_ai_launcher/_stack.py](utils/xr-ai-launcher/xr_ai_launcher/_stack.py)

</details>



The XR-AI system is built on a hub-centric media routing model designed to bridge real-time spatial computing with multimodal AI agents. The architecture enforces strict boundaries between media transport, AI inference, and agent logic to ensure scalability across different hardware (from workstations to DGX Spark) and client platforms (Web, iOS, Android, XR headsets).

Sources: [docs/source/overview/architecture.md:8-16]()

## System Topology

The system follows a three-tier architecture where a central hub manages media and connectivity, specialized services handle heavy AI inference, and lightweight agents implement application logic.

### Media Routing and Isolation
The architecture centers on **DeviceIOHub**, which serves as the single point of entry for all clients [docs/source/components/server-runtime.md:8-12](). It manages an internal LiveKit transport and fans media out to agents via a high-performance IPC boundary [docs/source/components/server-runtime.md:8-12]().

*   **Participant Isolation**: The hub enforces a strict isolation contract: media from Participant A is never routed to Participant B [docs/source/components/server-runtime.md:51-60](). The only supported flow is `participant → hub → consumer (agent) → hub → same participant` [docs/source/components/server-runtime.md:57-60]().
*   **Zero-Copy Frames**: Video frames are managed via a shared-memory ring buffer (`ShmRingBuffer`), allowing agents to sample frames on-demand without the overhead of full-frame IPC serialization [docs/source/components/server-runtime.md:91-103]().

Sources: [docs/source/components/server-runtime.md:8-60]()

### Process Model
Applications are composed of multiple processes managed by a central launcher (`xr-ai-launcher`) [docs/source/components/launcher-and-process-model.md:16-18](). Each sample typically includes:
1.  **DeviceIOHub**: Handles WebRTC, TLS, and ZMQ dispatch [docs/source/components/server-runtime.md:8-12]().
2.  **AI Inference Services**: Independent processes for LLM, VLM, STT, and TTS [docs/source/overview/architecture.md:11-13]().
3.  **Agent Worker**: The application logic process using the Agent SDK [docs/source/components/launcher-and-process-model.md:16-18]().

Sources: [docs/source/components/launcher-and-process-model.md:12-18]()

### Data Flow Diagram: Client to Agent

Natural Language to Code Entity Mapping (Media Path)
```mermaid
graph LR
    subgraph ["Client Space (Remote)"]
        [iOS_App] --> ["wss://host:8080/rtc"]
    end

    subgraph ["DeviceIOHub (Service)"]
        [WebServer] --> [LiveKitConnector]
        [LiveKitConnector] -- "AudioChunk / FRAME_SIGNAL" --> [HubEndpoint]
    end

    subgraph ["Agent Space (Worker Process)"]
        [HubEndpoint] -- "ZMQ PUB/SUB" --> [ProcessorEndpoint]
        [ProcessorEndpoint] --> [AgentRuntime]
        [Agent_Class] --> [AgentRuntime]
    end

    style [iOS_App] stroke-dasharray: 5 5
    style [Agent_Class] stroke-width:4px
```
Sources: [docs/source/components/server-runtime.md:8-12](), [services/device-io-hub/device_io_hub/transport/livekit/connector.py:65-80]()

---

## Major Subsystems

### [Device I/O Hub](#2.1)
The core media server (`services/device-io-hub/`). It manages the `LiveKitConnector` for WebRTC transport, a TLS web server for token generation and proxying, and a ZMQ-based IPC hub (`HubEndpoint` / `ConnectorEndpoint`). It handles shared-memory ring buffers (`ShmRingBuffer`) for zero-copy frame access.
For details, see [Device I/O Hub](#2.1).

Sources: [docs/source/components/server-runtime.md:8-12](), [docs/source/reference/migrations.md:16-23]()

### [Agent SDK](#2.2)
A collection of six Python packages (`xr-ai-hub`, `xr-ai-runtime`, `xr-ai-models`, `xr-ai-tools`, `xr-ai-voice`, `xr-ai-web-events`) used to build agents. It abstracts ZMQ IPC, provides typed model protocols, and includes a Pipecat-based voice pipeline.
For details, see [Agent SDK](#2.2).

Sources: [docs/source/overview/architecture.md:73-74]()

### [Process Orchestration and Launcher](#2.3)
The `xr-ai-launcher` utility provides stack orchestration via `run_stack`, `Process`, and `Parallel` dataclasses, managing launch modes (`own`, `persist`, `reuse`), ready-file protocols, environment sanitization, and credential loading.
For details, see [Process Orchestration and Launcher](#2.3).

Sources: [docs/source/components/launcher-and-process-model.md:6-12](), [utils/xr-ai-launcher/xr_ai_launcher/_stack.py:66-134]()

### [AI Inference Services](#2.4)
Dedicated services for Vision-Language Models (VLM), Large Language Models (LLM), Speech-to-Text (STT), and Text-to-Speech (TTS), managed via `xr-ai-vllm` Docker/pip backends and model profiles.
For details, see [AI Inference Services](#2.4).

Sources: [docs/source/overview/architecture.md:75-76]()

### [XR Capability Services](#2.5)
Typed RPC services providing spatial and visual capabilities, including `video-memory-service`, `openxr-service`, `rag-service`, and `cloudxr-runtime`.
For details, see [XR Capability Services](#2.5).

Sources: [docs/source/overview/architecture.md:76-77]()

---

## IPC and Communication Contract

The system uses a hub-and-spoke model for IPC. The Hub binds two primary ZMQ sockets (`PULL` and `PUB`) to communicate with connectors and processors.

IPC Topology Diagram
```mermaid
graph TD
    subgraph ["Service Layer"]
        [ConnectorEndpoint] -- "ZMQ PUSH (ipc:///tmp/xr_hub_in)" --> [HubEndpoint_PULL]
    end

    subgraph ["Hub Process"]
        [HubEndpoint_PULL] --> [Dispatcher]
        [Dispatcher] --> [HubEndpoint_PUB]
    end

    subgraph ["Agent Layer"]
        [HubEndpoint_PUB] -- "ZMQ SUB (ipc:///tmp/xr_hub_pub)" --> [ProcessorEndpoint]
        [ProcessorEndpoint] -- "return_audio.{pid}" --> [HubEndpoint_PULL]
    end

    [Dispatcher] -- "FRAME_DATA" --> [ShmRingBuffer]
    [ProcessorEndpoint] -- "FRAME_REQUEST" --> [Dispatcher]
```
Sources: [docs/source/components/server-runtime.md:113-130](), [services/device-io-hub/device_io_hub/ipc/_hub.py:103-150]()

### Topic Convention
Messages are routed using a dot-notated topic scheme: `<type>.<participant_id>.<track_or_topic>`.
*   `audio.alice`: All audio from participant Alice.
*   `data.alice.chat`: Data messages on the "chat" channel from Alice.
*   `return_audio.alice`: Audio sent from an agent back to Alice.

Sources: [docs/source/components/server-runtime.md:135-145]()

---

