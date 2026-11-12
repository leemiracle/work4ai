<!-- source: DeepWiki mcp.deepwiki.com · repo pipecat-ai/pipecat · page 1 Overview · fetched 2026-10-27 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/coverage.yaml](.github/workflows/coverage.yaml)
- [.github/workflows/python-compatibility.yaml](.github/workflows/python-compatibility.yaml)
- [.github/workflows/tests.yaml](.github/workflows/tests.yaml)
- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [changelog/6208.added.md](changelog/6208.added.md)
- [env.example](env.example)
- [evals/release/manifest.yaml](evals/release/manifest.yaml)
- [examples/voice/voice-rime-v1.py](examples/voice/voice-rime-v1.py)
- [pyproject.toml](pyproject.toml)
- [src/pipecat/frames/frames.py](src/pipecat/frames/frames.py)
- [src/pipecat/pipeline/task.py](src/pipecat/pipeline/task.py)
- [src/pipecat/processors/aggregators/llm_response.py](src/pipecat/processors/aggregators/llm_response.py)
- [src/pipecat/processors/frame_processor.py](src/pipecat/processors/frame_processor.py)
- [src/pipecat/services/rime/tts_v1.py](src/pipecat/services/rime/tts_v1.py)
- [src/pipecat/transports/base_input.py](src/pipecat/transports/base_input.py)
- [src/pipecat/transports/base_output.py](src/pipecat/transports/base_output.py)
- [src/pipecat/transports/base_transport.py](src/pipecat/transports/base_transport.py)
- [tests/test_rime_v1_tts.py](tests/test_rime_v1_tts.py)
- [uv.lock](uv.lock)

</details>



## Purpose and Scope

This page introduces the Pipecat AI framework, covering its core purpose, architectural philosophy, and key capabilities for building real-time conversational AI agents [README.md:7-10](). It provides a conceptual map of the framework's major components and their relationships, including multi-agent coordination over `WorkerBus`, bundled `Pipecat Flows`, and real-time capabilities [README.md:9-10](), [README.md:41-42](), [CHANGELOG.md:10-145]().

For installation and extras configuration, see Getting Started. For frame-based execution mechanics, see Core Architecture. For AI integrations, see AI Service Integrations. For transports, see Transport Layer.

Sources: [README.md:1-42](), [pyproject.toml:5-13](), [CHANGELOG.md:10-145]()

## What is Pipecat?

Pipecat is an open-source Python framework designed for building real-time voice and multimodal conversational AI agents [README.md:7-10](). It orchestrates interactions between audio/video processing, AI services (LLMs, STT, S2S, TTS), transports, and conversation state management through a composable pipeline architecture [README.md:23-30]().

The framework enables developers to:
- **Build Voice Assistants** – Facilitate natural, low-latency streaming conversations [README.md:15-15]().
- **Create Multi-Agent Systems** – Deploy specialist agents that hand off tasks, fan out in parallel, or coordinate as sidecars over a shared `WorkerBus` [README.md:9-10](), [CHANGELOG.md:14-22]().
- **Manage Structured Conversations** – Utilize `Pipecat Flows` bundled directly in `pipecat-ai` [README.md:41-42]().
- **Deploy Across Diverse Transports** – Interface via WebRTC, WebSockets, telephony, and Media over QUIC (`MOQTransport`) [README.md:27-29](), [pyproject.toml:125-125]().
- **Swap Providers Seamlessly** – Change AI service providers without modifying core application logic through the pluggable `AIService` architecture [README.md:25-25]().

**Core Design Principle**: Pipecat treats all data and control events as typed `Frame` objects flowing through a pipeline of `FrameProcessor` nodes. Every `PipelineWorker` operates as a peer on a shared `WorkerBus` [src/pipecat/processors/frame_processor.py:7-12](), [CHANGELOG.md:14-22]().

Sources: [README.md:7-60](), [pyproject.toml:6-8](), [src/pipecat/processors/frame_processor.py:7-12](), [CHANGELOG.md:10-141]()

## Architecture Philosophy

### Frame-Based Processing Pipeline

Pipecat's runtime architecture is built upon three core abstractions:

| Concept | Description | Primary Classes |
|---------|-------------|-----------------|
| **Frame** | Immutable data packets flowing through the pipeline. | `Frame`, `SystemFrame`, `DataFrame`, `ControlFrame` [src/pipecat/frames/frames.py:73-155]() |
| **FrameProcessor** | Composable nodes that process incoming frames asynchronously. | `FrameProcessor`, `FrameProcessorQueue` [src/pipecat/processors/frame_processor.py:74-184]() |
| **PipelineWorker** | Execution lifecycle manager and bus peer (formerly `PipelineTask`). | `PipelineWorker`, `PipelineParams` [src/pipecat/pipeline/task.py:15-28]() |

All media chunks, text tokens, LLM contexts, tool calls, and control signals are subclasses of `Frame` [src/pipecat/frames/frames.py:73-155]().

Title: "Frame Hierarchy and Code Entities"
```mermaid
graph "LR" {
    "NL_Base"["Base Frame"] --> "Entity_Frame"["Frame\nsrc/pipecat/frames/frames.py:74"]
    "Entity_Frame" --> "Entity_Sys"["SystemFrame\nsrc/pipecat/frames/frames.py:122"]
    "Entity_Frame" --> "Entity_Data"["DataFrame\nsrc/pipecat/frames/frames.py:133"]
    "Entity_Frame" --> "Entity_Ctrl"["ControlFrame\nsrc/pipecat/frames/frames.py:145"]
    "Entity_Sys" --> "Entity_Start"["StartFrame\nsrc/pipecat/processors/frame_processor.py:39"]
    "Entity_Sys" --> "Entity_Inter"["InterruptionFrame\nsrc/pipecat/processors/frame_processor.py:38"]
    "Entity_Data" --> "Entity_Audio"["OutputAudioRawFrame\nsrc/pipecat/transports/base_output.py:38"]
    "Entity_Data" --> "Entity_Text"["TextFrame\nsrc/pipecat/processors/aggregators/llm_response.py:15"]
    "Entity_Ctrl" --> "Entity_Config"["FilterControlFrame\nsrc/pipecat/transports/base_output.py:34"]
}
```
Sources: [src/pipecat/frames/frames.py:74-155](), [src/pipecat/processors/frame_processor.py:38-41](), [src/pipecat/processors/aggregators/llm_response.py:15-15](), [src/pipecat/transports/base_output.py:34-38]()

**Frame Priority & Flow Control**: Critical signals (`SystemFrame` instances like `InterruptionFrame` or `StartFrame`) bypass standard data queues via `FrameProcessorQueue`, a specialized `asyncio.PriorityQueue` that processes start frames first, then system frames, followed by data and control frames [src/pipecat/processors/frame_processor.py:131-172]().

Sources: [src/pipecat/frames/frames.py:74-155](), [src/pipecat/processors/frame_processor.py:131-184](), [src/pipecat/pipeline/task.py:15-28]()

### Multi-Worker Framework and Shared Bus

The `pipecat.workers` and `pipecat.pipeline.worker` modules enable distributed multi-agent systems. A `PipelineWorker` acts as a peer on a shared `WorkerBus` [CHANGELOG.md:14-22]().

- **`WorkerBus`**: A pub/sub messaging layer (`AsyncQueueBus`, `RedisBus`, or `PgmqBus`) facilitating inter-worker communication.
- **`UIWorker`**: Drives real-time web client interfaces using the RTVI protocol.
- **State & Resource Sharing**: `PipelineWorker` manages `app_resources` passed to downstream processors and tool execution handlers [src/pipecat/processors/frame_processor.py:74-114]().
- **Strategy Callbacks**: Turn strategies utilize explicit lifecycle callbacks like `handle_user_turn_started` and `handle_user_turn_stopped` [CHANGELOG.md:14-22]().

Sources: [src/pipecat/pipeline/task.py:15-28](), [src/pipecat/processors/frame_processor.py:74-114](), [CHANGELOG.md:14-145]()

### Processor Linking and Frame Flow

Title: "Pipeline Execution Model and Component Relationships"
```mermaid
graph "TD" {
    "Worker"["PipelineWorker\nsrc/pipecat/pipeline/task.py:20"]
    "Processor"["FrameProcessor\nsrc/pipecat/processors/frame_processor.py:74"]
    "Queue"["FrameProcessorQueue\nsrc/pipecat/processors/frame_processor.py:131"]
    "InputT"["BaseInputTransport\nsrc/pipecat/transports/base_input.py:38"]
    "OutputT"["BaseOutputTransport\nsrc/pipecat/transports/base_output.py:66"]
    
    "Worker" -->|"runs"| "Processor"
    "Processor" -->|"enqueues via"| "Queue"
    "InputT" -->|"pushes downstream"| "Processor"
    "Processor" -->|"pushes downstream"| "OutputT"
}
```
Sources: [src/pipecat/processors/frame_processor.py:74-184](), [src/pipecat/pipeline/task.py:15-28](), [src/pipecat/transports/base_input.py:38-45](), [src/pipecat/transports/base_output.py:66-72]()

Each `FrameProcessor` operates asynchronously, accepting frames via `process_frame()` and pushing results downstream or upstream using `push_frame()` [src/pipecat/processors/frame_processor.py:74-184]().

Sources: [src/pipecat/processors/frame_processor.py:74-184](), [src/pipecat/pipeline/task.py:15-28](), [src/pipecat/transports/base_input.py:38-45](), [src/pipecat/transports/base_output.py:66-72]()

## Key Capabilities

### AI Service Integrations & Pluggable Architecture

Pipecat integrates over 60 AI providers through unified service base classes [README.md:89-137]().

| Service Category | Base Class | Notable Integrations |
|------------------|------------|----------------------|
| LLMs | `LLMService` | OpenAI, Anthropic, Google, AWS Bedrock, Groq, Mistral [pyproject.toml:70-155]() |
| Text-to-Speech | `TTSService` | Cartesia, ElevenLabs, Deepgram, Smallest [pyproject.toml:78-146]() |
| Speech-to-Text | `STTService` | Deepgram, Whisper, AssemblyAI, Speechmatics [pyproject.toml:71-153]() |
| Speech-to-Speech | Realtime Services | OpenAI Realtime, Google Gemini Live, AWS Nova Sonic [pyproject.toml:74-154]() |

**Plugin Ecosystem**: Dependencies are organized via `pyproject.toml` extras, enabling modular installations per service provider [pyproject.toml:68-155](). Environment variables, as shown in `env.example`, are used to configure API keys and other service-specific settings [env.example:1-247]().

Sources: [README.md:89-137](), [pyproject.toml:68-155](), [env.example:1-247]()

### Transport Layer Abstraction & Real-Time Transports

Transports inherit from `BaseTransport`, splitting into `BaseInputTransport` and `BaseOutputTransport` to handle bidirectional media streams [src/pipecat/transports/base_input.py:38-45](), [src/pipecat/transports/base_output.py:66-72]().

- **`MOQTransport`**: Media over QUIC provides low-latency streaming and transport control [pyproject.toml:125-125](). It supports client-mode reconnect with backoff and sends `session-ending` markers [CHANGELOG.md:47-58]().
- **`DailyTransport`**: Integrates Daily.co WebRTC sessions and media streaming [pyproject.toml:83-83]().
- **Media Senders**: `BaseOutputTransport` manages distinct `MediaSender` instances per destination track, handling audio chunking and media streaming [src/pipecat/transports/base_output.py:97-195]().

Sources: [src/pipecat/transports/base_input.py:38-76](), [src/pipecat/transports/base_output.py:66-195](), [pyproject.toml:83-125](), [CHANGELOG.md:47-58]()

### Real-Time Conversational Features & Turn Management

- **Audio Token Tracking**: Tracks `input_audio_tokens` and `output_audio_tokens` for multimodal and realtime LLM calls [CHANGELOG.md:71-91]().
- **Turn Strategies**: Specialized turn detectors and aggregators manage user interruptions, VAD states, and conversational transitions [src/pipecat/transports/base_input.py:39-44]().
- **Interruptible Frames**: The `interruptible` field on `Frame` objects (default `True`) allows fine-grained control over whether a frame can be dropped during an interruption, with `UninterruptibleFrame` subclasses defaulting to `False` [src/pipecat/frames/frames.py:104-116](), [CHANGELOG.md:67-72]().

Sources: [src/pipecat/transports/base_input.py:38-44](), [CHANGELOG.md:67-91](), [src/pipecat/frames/frames.py:104-116]()

---

