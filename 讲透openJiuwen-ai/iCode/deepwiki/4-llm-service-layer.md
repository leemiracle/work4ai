<!-- source: DeepWiki mcp.deepwiki.com · repo openJiuwen-ai/iCode · page 4 LLM Service Layer · fetched 2026-11-02 -->

# LLM Service Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/en/guides/daily-use/sessions.md](docs/en/guides/daily-use/sessions.md)
- [docs/zh-Hans/guides/daily-use/sessions.md](docs/zh-Hans/guides/daily-use/sessions.md)
- [src/chrys/foundation/util/chrys_headers.py](src/chrys/foundation/util/chrys_headers.py)
- [src/chrys/service/llm/chat_completions/client.py](src/chrys/service/llm/chat_completions/client.py)
- [src/chrys/service/llm/observer.py](src/chrys/service/llm/observer.py)
- [src/chrys/service/llm/openai_responses/client.py](src/chrys/service/llm/openai_responses/client.py)
- [src/chrys/service/llm/request_tracking.py](src/chrys/service/llm/request_tracking.py)
- [src/chrys/service/llm/sdk_anthropic.py](src/chrys/service/llm/sdk_anthropic.py)
- [src/chrys/service/llm/sdk_headers.py](src/chrys/service/llm/sdk_headers.py)
- [src/chrys/service/llm/sdk_openai.py](src/chrys/service/llm/sdk_openai.py)
- [src/chrys/service/llm/wire_client.py](src/chrys/service/llm/wire_client.py)
- [tests/foundation/errors/_corpus.py](tests/foundation/errors/_corpus.py)
- [tests/foundation/test_errors.py](tests/foundation/test_errors.py)
- [tests/foundation/test_is_retryable.py](tests/foundation/test_is_retryable.py)
- [tests/integration/engine/test_stateless_store_option.py](tests/integration/engine/test_stateless_store_option.py)
- [tests/kernel/test_wire_retry.py](tests/kernel/test_wire_retry.py)
- [tests/service/agent_middleware/test_tool_operation_stamps.py](tests/service/agent_middleware/test_tool_operation_stamps.py)
- [tests/service/llm/test_client_contracts.py](tests/service/llm/test_client_contracts.py)
- [tests/service/llm/test_clients_factory.py](tests/service/llm/test_clients_factory.py)
- [tests/service/llm/test_request_tracking.py](tests/service/llm/test_request_tracking.py)
- [tests/service/llm/test_route_extension_wire.py](tests/service/llm/test_route_extension_wire.py)

</details>



The LLM Service Layer abstracts model provider interactions by encapsulating wire clients, protocol codecs, streaming mechanisms, and request tracking. It bridges the kernel's abstract chat interface with provider-specific SDKs (`AsyncOpenAI` and `AsyncAnthropic`), managing HTTP headers, error classification, telemetry integration, and per-attempt request tracking.

```mermaid
graph TD
    subgraph NaturalLanguageSpace["Natural Language & Agent Loop"]
        NL1["Agent Turn Execution"] --> NL2["Chat Request Generation"]
    end

    subgraph CodeEntitySpace["Code Entity Space: LLM Service Layer"]
        NL2 --> CF["src/chrys/service/llm/clients.py"]
        CF --> WC["WireClient (src/chrys/service/llm/wire_client.py)"]
        WC --> CC["ChatCompletionsClient (src/chrys/service/llm/chat_completions/client.py)"]
        WC --> RC["ResponsesApiClient (src/chrys/service/llm/openai_responses/client.py)"]
        WC --> AC["AnthropicMessagesClient (src/chrys/service/llm/anthropic_messages/client.py)"]
        WC --> RT["RequestTracking (src/chrys/service/llm/request_tracking.py)"]
        WC --> OBS["WireCallObserver (src/chrys/service/llm/observer.py)"]
    end

    Sources: src/chrys/service/llm/wire_client.py:1-20, src/chrys/service/llm/clients.py:1-30
```

---

## 4.1 Wire Clients and Client Factory

The wire client infrastructure defines a common base class, `WireClient`, which implements the kernel's `_inner_get_response` hook. It handles OpenTelemetry spans, request observation, and dispatches to specific protocol handlers (`_send` and `_open_stream`). The client factory (`create_client`) constructs the production stack, composing the tool loop, chat middleware, and the underlying provider wire client.

For details, see [Wire Clients and Client Factory](#4.1).

Sources: `src/chrys/service/llm/wire_client.py:1-156`, `tests/service/llm/test_client_contracts.py:50-120`

---

## 4.2 Chat Completions and OpenAI Responses Codecs

OpenAI-compatible protocols are serviced by two distinct codecs: the standard Chat Completions API client and the newer Responses API client (`ResponsesApiClient`). These clients handle request building, conversation history encoding, stream assembly via `StreamState`, response decoding, and finish reason mapping. They manage specific provider requirements such as prompt caching keys and stateless options.

For details, see [Chat Completions and OpenAI Responses Codecs](#4.2).

Sources: `src/chrys/service/llm/openai_responses/client.py:1-124`, `tests/service/llm/test_request_tracking.py:44-95`

---

## 4.3 Anthropic Messages Codec

The Anthropic client (`AnthropicMessagesClient`) integrates with `AsyncAnthropic` to support the Anthropic Messages API. It handles streaming responses, thinking/reasoning blocks, citation processing, and conversation history normalization. It also includes repair mechanisms for malformed model outputs and handles specialized stop reasons.

For details, see [Anthropic Messages Codec](#4.3).

Sources: `tests/service/llm/test_request_tracking.py:44-90`, `tests/service/llm/test_route_extension_wire.py:33-42`

---

## 4.4 Request Tracking and Observability

Request tracking ensures every individual HTTP attempt—including SDK retries and redirects—carries a unique correlation identifier via the `Chrys-Request-Attempt-Id` header. The `RequestTracking` class and `build_request_tracking_hooks()` bind attempt IDs to `httpx` request extensions, capturing provider request IDs and logging raw HTTP traffic without altering stream completion semantics.

```mermaid
graph TD
    subgraph NaturalLanguageSpace["Tracing & Observability"]
        T1["Exchange Trace Scope"] --> T2["HTTP Attempt Execution"]
    end

    subgraph CodeEntitySpace["Request Tracking Code Entities"]
        T2 --> RT["RequestTracking (src/chrys/service/llm/request_tracking.py)"]
        RT --> HK["build_request_tracking_hooks() (src/chrys/service/llm/request_tracking.py)"]
        HK --> HD["Chrys-Request-Attempt-Id (src/chrys/foundation/util/chrys_headers.py)"]
        RT --> OBS["WireCallObserver (src/chrys/service/llm/observer.py)"]
        OBS --> EV["EventType.MODEL_REQUEST_PREPARED (src/chrys/foundation/trajectory/event_types.py)"]
    end

    Sources: src/chrys/service/llm/request_tracking.py:37-109, src/chrys/service/llm/observer.py:3-33
```

For details, see [Request Tracking and Observability](#4.4).

Sources: `src/chrys/service/llm/request_tracking.py:1-109`, `src/chrys/service/llm/observer.py:3-56`

---

