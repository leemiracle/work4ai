<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-go · page 19 Glossary · fetched 2026-10-26 -->

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.release-please-manifest.json](.release-please-manifest.json)
- [.stats.yml](.stats.yml)
- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [aliases.go](aliases.go)
- [internal/encoding/json/time.go](internal/encoding/json/time.go)
- [internal/requestconfig/requestconfig.go](internal/requestconfig/requestconfig.go)
- [internal/version.go](internal/version.go)
- [option/requestoption.go](option/requestoption.go)
- [packages/param/encoder.go](packages/param/encoder.go)
- [packages/param/encoder_test.go](packages/param/encoder_test.go)
- [packages/param/option.go](packages/param/option.go)
- [packages/param/param.go](packages/param/param.go)
- [packages/ssestream/ssestream.go](packages/ssestream/ssestream.go)
- [responses/aliases.go](responses/aliases.go)
- [responses/response.go](responses/response.go)
- [shared/shared.go](shared/shared.go)

</details>



This glossary defines codebase-specific terms, abbreviations, and domain concepts used throughout the `openai-go` SDK.

## Purpose and Scope
The `openai-go` SDK is a programmatically generated library based on the OpenAI REST API specification. This glossary serves to bridge the gap between high-level OpenAI product concepts and their specific implementation details within the Go type system, especially regarding the newer **Responses API** and the underlying **Request Execution Pipeline**.

---

## Core SDK Terminology

### Request Configuration & Options
The SDK uses a functional options pattern to configure clients and individual requests.

*   **`RequestOption`**: An interface representing a configuration function that modifies a `RequestConfig` object. These are defined in [internal/requestconfig/requestconfig.go:81-83]() and aliased for public use in [option/requestoption.go:25-25]().
*   **`RequestConfig`**: An internal struct that holds the state for a single HTTP request, including headers, timeout, retries, and the body reader [internal/requestconfig/requestconfig.go:210-234]().
*   **`Middleware`**: A function type that intercepts HTTP requests and responses. Middlewares can be chained to implement logging, custom auth, or telemetry [option/requestoption.go:85-85]().

### Data Structures & Marshaling
*   **`param.Opt[T]`**: A wrapper used for optional fields in request parameters. It allows the SDK to distinguish between a field that is explicitly set to a zero value and a field that is omitted from the JSON payload.
*   **`Union Types`**: Types representing a field that can hold one of several different structures (e.g., `ResponseNewParamsInputUnion`). These are typically implemented using helper structs with fields like `Of[Type]` [responses/response.go:68-68]().
*   **`ExtraFields`**: A map found on many structs that captures unknown properties returned by the API, ensuring forward compatibility when the API adds new fields [responses/response.go:1210-1210]().

---

## Domain Specific Terms

### Responses API (Modern)
The **Responses API** is the primary interface for interacting with models, succeeding the legacy Assistants API.

*   **`Response`**: The primary entity representing a model's execution. It is stateful and can be retrieved, cancelled, or deleted [responses/response.go:92-145]().
*   **`PreviousResponseID`**: A field used to chain responses together, maintaining conversation context without manually managing message history [README.md:98-98]().
*   **`InputItem`**: A discrete piece of content provided to a Response, such as text, images, or tool outputs [responses/response.go:35-35]().

### Streaming
*   **`ssestream.Stream`**: A generic wrapper for Server-Sent Events (SSE). It handles the parsing of the `text/event-stream` format and provides an iterator interface via `Next()` and `Current()` [packages/ssestream/ssestream.go:137-143]().
*   **`[DONE]` Marker**: A specific string sent by the OpenAI API to signify the end of a stream. The `ssestream` package handles this to stop iteration [packages/ssestream/ssestream.go:181-185]().

---

## Conceptual Mapping: Natural Language to Code

The following diagrams illustrate how high-level concepts map to specific entities within the `openai-go` codebase.

### Diagram 1: Request Execution Lifecycle
This diagram maps the process of making an API call to the internal functions and types responsible for each step.

```mermaid
graph TD
    "User Code" -- "Calls client.Responses.New()" --> RService["responses.ResponseService.New"]
    RService -- "Prepares Body" --> ReqConfig["requestconfig.NewRequestConfig"]
    ReqConfig -- "Applies" --> Opts["option.RequestOption"]
    ReqConfig -- "Serializes" --> Marshaler["apijson.Marshal / apiform.Marshaler"]
    ReqConfig -- "Executes" --> Exec["requestconfig.ExecuteNewRequest"]
    Exec -- "Retries/Backoff" --> Backoff["internal/requestconfig/requestconfig.go"]
    Exec -- "Dispatches" --> HTTP["http.Client.Do"]

    subgraph "Code Entity Space"
    RService
    ReqConfig
    Opts
    Marshaler
    Exec
    end
```
**Sources:** [responses/response.go:61-66](), [internal/requestconfig/requestconfig.go:91-198](), [option/requestoption.go:20-25]()

### Diagram 2: Response API & Streaming Flow
This diagram maps the "Natural Language" concept of a streaming chat conversation to the specific Go types that handle the data flow.

```mermaid
graph LR
    subgraph "Natural Language Space"
    "Prompt" --> "Streaming Response"
    "Streaming Response" --> "Event Processing"
    "Event Processing" --> "Final Output"
    end

    subgraph "Code Entity Space"
    "Prompt" -.-> Param["responses.ResponseNewParams"]
    "Streaming Response" -.-> NewStream["responses.ResponseService.NewStreaming"]
    NewStream -.-> SStream["ssestream.Stream[ResponseStreamEventUnion]"]
    SStream -.-> Decoder["ssestream.eventStreamDecoder"]
    "Event Processing" -.-> Next["ssestream.Stream.Next()"]
    Next -.-> Union["responses.ResponseStreamEventUnion"]
    "Final Output" -.-> Output["responses.Response.OutputText()"]
    end
```
**Sources:** [responses/response.go:79-89](), [packages/ssestream/ssestream.go:171-228](), [README.md:168-183]()

---

## Technical Jargon & Abbreviations

| Term | Definition | Code Pointer |
| :--- | :--- | :--- |
| **SSE** | Server-Sent Events. The protocol used for real-time streaming of model tokens and events. | [packages/ssestream/ssestream.go:65-65]() |
| **ZDR** | Zero-Data Retention. Refers to specific compliance and compaction modes in the Responses API. | [responses/response.go:151-152]() |
| **Functional Option** | A pattern where functions (e.g., `WithAPIKey`) are passed to a constructor to configure an object. | [option/requestoption.go:20-22]() |
| **Delta** | A partial update in a stream, typically containing just the new characters/tokens generated. | [README.md:177-177]() |
| **Tool Call** | An instruction from the model to execute a specific function or use a plugin (e.g., Web Search). | [responses/response.go:220-222]() |

**Sources:** [packages/ssestream/ssestream.go:1-20](), [responses/response.go:147-158](), [option/requestoption.go:1-44](), [README.md:1-185]()