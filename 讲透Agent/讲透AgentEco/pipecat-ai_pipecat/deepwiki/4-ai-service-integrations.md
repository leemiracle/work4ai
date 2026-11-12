<!-- source: DeepWiki mcp.deepwiki.com · repo pipecat-ai/pipecat · page 4 AI Service Integrations · fetched 2026-10-27 -->

# AI Service Integrations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [AGENTS.md](AGENTS.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [src/pipecat/evals/conversation.py](src/pipecat/evals/conversation.py)
- [src/pipecat/evals/conversation_observer.py](src/pipecat/evals/conversation_observer.py)
- [src/pipecat/services/anthropic/llm.py](src/pipecat/services/anthropic/llm.py)
- [src/pipecat/services/aws/llm.py](src/pipecat/services/aws/llm.py)
- [src/pipecat/services/google/llm.py](src/pipecat/services/google/llm.py)
- [src/pipecat/services/grok/realtime/events.py](src/pipecat/services/grok/realtime/events.py)
- [src/pipecat/services/grok/realtime/llm.py](src/pipecat/services/grok/realtime/llm.py)
- [src/pipecat/services/llm_service.py](src/pipecat/services/llm_service.py)
- [src/pipecat/services/openai/base_llm.py](src/pipecat/services/openai/base_llm.py)
- [src/pipecat/services/openai/realtime/events.py](src/pipecat/services/openai/realtime/events.py)
- [src/pipecat/services/openai/responses/llm.py](src/pipecat/services/openai/responses/llm.py)
- [src/pipecat/services/settings.py](src/pipecat/services/settings.py)
- [src/pipecat/transports/daily/utils.py](src/pipecat/transports/daily/utils.py)
- [tests/test_anthropic_thinking_defaults.py](tests/test_anthropic_thinking_defaults.py)
- [tests/test_evals_conversation.py](tests/test_evals_conversation.py)
- [tests/test_evals_conversation_observer.py](tests/test_evals_conversation_observer.py)
- [tests/test_openai_responses_http.py](tests/test_openai_responses_http.py)
- [tests/test_openai_responses_websocket.py](tests/test_openai_responses_websocket.py)
- [tests/test_run_inference.py](tests/test_run_inference.py)
- [tests/test_settings.py](tests/test_settings.py)

</details>



This page provides an architectural overview of Pipecat's AI service integration layer: the common base classes, the settings system for runtime updates, and the landscape of 60+ supported service integrations. It serves as a high-level map to the subsystems described in the child pages.

For context on where services sit in a running pipeline, see [Core Architecture](#3). For transport services (WebRTC, telephony, MoQ), see [Transport Layer](#5).

Detailed coverage by category:
- [Service Architecture and Adapters](#4.1) — Explain `AIService` base class, Settings system, `BaseLLMAdapter` pattern, runtime configuration via update frames, settings delta pattern, `WebsocketService` reconnection, `ServiceMetadataFrame`, and OTel GenAI convention updates.
- [Large Language Models](#4.2) — Document `LLMService` base class, function calling, standard LLM integrations (OpenAI, Anthropic, Google, AWS Bedrock, Groq, Mistral, Cerebras, SambaNova, Ollama, DeepSeek, Baseten, Crusoe, etc.), and the OpenAI Responses API with reasoning support.
- [Text-to-Speech Services](#4.3) — Cover `TTSService` base class, text aggregation modes, WebSocket vs HTTP services, word timestamp support, and TTS provider implementations.
- [Speech-to-Text Services](#4.4) — Document `STTService` base class, audio processing, TTFB/TTFS metrics, keepalive mechanisms, VAD force turn endpoint, and STT provider implementations including Deepgram Flux and SageMaker variants.
- [Speech-to-Speech Services](#4.5) — Overview of real-time speech-to-speech services using WebSocket-based bidirectional streaming. Links to child pages for each major provider. Covers `realtime_service_mode`, `RealtimeServiceMetadataFrame`, and audio token usage.
- [Vision and Image Services](#4.6) — Document vision model integrations (Moondream, Google Image, OpenAI Image, FAL, Azure Image), image processing, and multimodal context handling.

---

## Module Organization

All service base classes live under `src/pipecat/services/`. Provider implementations are organized under `src/pipecat/services/<provider>/`. Adapters (format converters between universal context and provider APIs) live under `src/pipecat/adapters/`.

| Module | Base Class | Role |
|--------|-----------|------|
| `pipecat.services.ai_service` | `AIService` | Root base; lifecycle + settings management |
| `pipecat.services.llm_service` | `LLMService` | LLM text inference + function calling [src/pipecat/services/llm_service.py:65-65]() |
| `pipecat.services.websocket_service` | `WebsocketService` | Base for WebSocket services with reconnection [src/pipecat/services/llm_service.py:67-67]() |
| `pipecat.services.settings` | `ServiceSettings` | Typed configuration store and delta updates [src/pipecat/services/settings.py:68-68]() |

Sources: [src/pipecat/services/llm_service.py:65-65](), [src/pipecat/services/llm_service.py:67-67](), [src/pipecat/services/settings.py:68-68]()

---

## Service Type Hierarchy

`AIService` extends `FrameProcessor` and provides a shared lifecycle and runtime-updatable settings via `_update_settings()` [src/pipecat/services/llm_service.py:65-65](). Every service instance manages its state through a `ServiceSettings` object [src/pipecat/services/settings.py:68-75]().

The settings infrastructure uses a **Store mode** (full current state) and **Delta mode** (sparse updates carried by frames) pattern [src/pipecat/services/settings.py:13-23](). `ServiceSettings` fields default to `NOT_GIVEN` to facilitate sparse updates [src/pipecat/services/settings.py:53-57](). When a service starts, `validate_complete()` is called to ensure the Store mode object has no `NOT_GIVEN` values [src/pipecat/services/settings.py:32-32]().

For details on the adapter pattern and runtime configuration, see [Service Architecture and Adapters](#4.1).

**Diagram: Service Architecture and Natural Language to Code Entity Space**

```mermaid
flowchart TD
    subgraph "NaturalLanguageSpace" ["Natural Language Concept Space"]
        NL_SVC[""AI Service Lifecycle & Runtime Settings""]
        NL_SOCK[""WebSocket Reconnection & Resilience""]
        NL_SET[""Typed Configuration & Delta Updates""]
    end

    subgraph "CodeEntitySpace" ["Code Entity Space"]
        CE_AI[""AIService (src/pipecat/services/ai_service.py)""]
        CE_WS[""WebsocketService (src/pipecat/services/websocket_service.py)""]
        CE_SET[""ServiceSettings (src/pipecat/services/settings.py)""]
    end

    NL_SVC --> CE_AI
    NL_SOCK --> CE_WS
    NL_SET --> CE_SET
```

Sources: [src/pipecat/services/llm_service.py:65-65](), [src/pipecat/services/settings.py:68-75](), [src/pipecat/services/settings.py:13-23](), [src/pipecat/services/settings.py:53-57](), [src/pipecat/services/settings.py:32-32]()

---

## The Adapter System

Each LLM provider uses a different API format. Pipecat uses a per-provider adapter to perform just-in-time translation from a universal `LLMContext` into provider-specific invocation parameters [src/pipecat/services/llm_service.py:30-32]().

The `BaseLLMAdapter` handles:
- Extracting provider-specific parameters.
- Converting standardized tool schemas (`ToolsSchema`).
- Resolving conflicts between `system_instruction` settings and context messages.

Specific adapters like `GeminiLLMAdapter` [src/pipecat/services/google/llm.py:27-27](), `AWSBedrockLLMAdapter`, `AnthropicLLMAdapter`, and `OpenAILLMAdapter` apply provider-specific constraints, such as role conversion (e.g., converting "developer" to "user" for services lacking `supports_developer_role` [src/pipecat/services/openai/base_llm.py:87-94]()).

**Diagram: LLM Service Ecosystem (Natural Language to Code Entity Space)**

```mermaid
flowchart TD
    subgraph "NaturalLanguageSpace" ["Natural Language Concept Space"]
        NL_LLM[""Large Language Model Integration""]
        NL_ADAPT[""Universal Context to Provider Translation""]
    end

    subgraph "CodeEntitySpace" ["Code Entity Space"]
        CE_LLM[""LLMService (src/pipecat/services/llm_service.py)""]
        CE_ADAPT[""BaseLLMAdapter (src/pipecat/adapters/base_llm_adapter.py)""]
        CE_OPENAI[""BaseOpenAILLMService (src/pipecat/services/openai/base_llm.py)""]
        CE_GOOGLE[""GoogleLLMService (src/pipecat/services/google/llm.py)""]
    end

    NL_LLM --> CE_LLM
    NL_LLM --> CE_OPENAI
    NL_LLM --> CE_GOOGLE
    NL_ADAPT --> CE_ADAPT
```

Sources: [src/pipecat/services/llm_service.py:30-32](), [src/pipecat/services/google/llm.py:27-27](), [src/pipecat/services/openai/base_llm.py:87-94]()

---

## WebSocket Service and Reconnection

Many AI services (STT, TTS, and Speech-to-Speech) communicate over WebSockets. Pipecat provides a `WebsocketService` base class that implements robust reconnection logic [src/pipecat/services/llm_service.py:67-67]().

- **Automatic Reconnection**: Uses exponential backoff [src/pipecat/services/llm_service.py:67-67]().
- **Send Retry**: `send_with_retry()` attempts to re-establish a connection if a send fails [src/pipecat/services/llm_service.py:67-67]().
- **Quick Failure Detection**: Detects rapid failure cycles to avoid infinite loops [src/pipecat/services/llm_service.py:67-67]().
- **Non-Fatal Errors**: Reconnection failures emit non-fatal `ErrorFrame` objects, allowing the pipeline to potentially recover or switch services [src/pipecat/services/llm_service.py:67-67]().

Sources: [src/pipecat/services/llm_service.py:67-67]()

---

## Supported Provider Landscape

### Large Language Models
Pipecat supports 30+ LLM providers. For complete details, see [Large Language Models](#4.2).
- **OpenAI**: Standard Chat Completions via `BaseOpenAILLMService` [src/pipecat/services/openai/base_llm.py:89-96]() and reasoning support via `OpenAIResponsesLLMService`.
- **Google Gemini**: Support for Gemini models via `GoogleLLMService` [src/pipecat/services/google/llm.py:161-166]().
- **Anthropic**: Claude models supporting extended thinking and prompt caching via `AnthropicLLMService`.
- **AWS Bedrock**: Amazon Nova and Anthropic Claude models via `AWSBedrockLLMService` [src/pipecat/services/aws/llm.py:87-93]().
- **xAI Grok**: Realtime LLM service.

### Speech and Vision
- **Text-to-Speech**: Managed via `TTSService` implementations supporting WebSocket and HTTP endpoints (ElevenLabs, Cartesia, Azure, Sarvam, Rime, Inworld). For details, see [Text-to-Speech Services](#4.3).
- **Speech-to-Text**: Managed via `STTService` implementations providing audio transcription and metrics (Deepgram, Azure, OpenAI Whisper, Google STT). For details, see [Speech-to-Text Services](#4.4).
- **Speech-to-Speech**: Real-time bidirectional WebSocket streaming via providers like OpenAI Realtime, Gemini Live, AWS Nova Sonic, and Ultravox. For details, see [Speech-to-Speech Services](#4.5).
- **Vision and Image**: Multimodal context handling across model integrations (Moondream, Google Image, OpenAI Image, FAL, Azure Image). For details, see [Vision and Image Services](#4.6).

Sources: [src/pipecat/services/openai/base_llm.py:89-96](), [src/pipecat/services/google/llm.py:161-166](), [src/pipecat/services/aws/llm.py:87-93]()

---

