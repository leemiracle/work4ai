<!-- source: DeepWiki mcp.deepwiki.com · repo openclaw/openclaw · extra page Web Search & Fetch · fetched 2026-10-26 -->

# Web Search & Fetch

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/gateway/openai-http-api.md](docs/gateway/openai-http-api.md)
- [docs/gateway/openresponses-http-api.md](docs/gateway/openresponses-http-api.md)
- [docs/nodes/media-understanding.md](docs/nodes/media-understanding.md)
- [docs/tools/code-mode.md](docs/tools/code-mode.md)
- [docs/tools/tool-search.md](docs/tools/tool-search.md)
- [extensions/discord/src/voice/audio.lifecycle.test.ts](extensions/discord/src/voice/audio.lifecycle.test.ts)
- [extensions/discord/src/voice/audio.test.ts](extensions/discord/src/voice/audio.test.ts)
- [extensions/discord/src/voice/audio.ts](extensions/discord/src/voice/audio.ts)
- [extensions/discord/src/voice/capture-state.test.ts](extensions/discord/src/voice/capture-state.test.ts)
- [extensions/discord/src/voice/capture-state.ts](extensions/discord/src/voice/capture-state.ts)
- [extensions/discord/src/voice/voice-session.startup.test.ts](extensions/discord/src/voice/voice-session.startup.test.ts)
- [packages/media-core/src/attachment-classify.test.ts](packages/media-core/src/attachment-classify.test.ts)
- [packages/media-core/src/attachment-classify.ts](packages/media-core/src/attachment-classify.ts)
- [packages/media-core/src/base64.test.ts](packages/media-core/src/base64.test.ts)
- [packages/media-core/src/base64.ts](packages/media-core/src/base64.ts)
- [packages/media-core/src/inbound-path-policy.test.ts](packages/media-core/src/inbound-path-policy.test.ts)
- [packages/media-core/src/mime.test.ts](packages/media-core/src/mime.test.ts)
- [packages/media-core/src/mime.ts](packages/media-core/src/mime.ts)
- [packages/memory-host-sdk/src/host/embedding-chunk-limits.test.ts](packages/memory-host-sdk/src/host/embedding-chunk-limits.test.ts)
- [packages/memory-host-sdk/src/host/embeddings.types.ts](packages/memory-host-sdk/src/host/embeddings.types.ts)
- [src/agents/agent-tools.deferred-followup.ts](src/agents/agent-tools.deferred-followup.ts)
- [src/agents/code-mode-bridge.ts](src/agents/code-mode-bridge.ts)
- [src/agents/code-mode-execution.ts](src/agents/code-mode-execution.ts)
- [src/agents/code-mode-headless.test.ts](src/agents/code-mode-headless.test.ts)
- [src/agents/code-mode-headless.ts](src/agents/code-mode-headless.ts)
- [src/agents/code-mode-json.test.ts](src/agents/code-mode-json.test.ts)
- [src/agents/code-mode-json.ts](src/agents/code-mode-json.ts)
- [src/agents/code-mode-runtime.test.ts](src/agents/code-mode-runtime.test.ts)
- [src/agents/code-mode-runtime.ts](src/agents/code-mode-runtime.ts)
- [src/agents/code-mode-state.ts](src/agents/code-mode-state.ts)
- [src/agents/code-mode-swarm.test.ts](src/agents/code-mode-swarm.test.ts)
- [src/agents/code-mode-worker-lifecycle.test.ts](src/agents/code-mode-worker-lifecycle.test.ts)
- [src/agents/code-mode-worker-types.ts](src/agents/code-mode-worker-types.ts)
- [src/agents/code-mode.agent-loop.test.ts](src/agents/code-mode.agent-loop.test.ts)
- [src/agents/code-mode.bridge.lifecycle.test.ts](src/agents/code-mode.bridge.lifecycle.test.ts)
- [src/agents/code-mode.bridge.test.ts](src/agents/code-mode.bridge.test.ts)
- [src/agents/code-mode.limits.test.ts](src/agents/code-mode.limits.test.ts)
- [src/agents/code-mode.output.test.ts](src/agents/code-mode.output.test.ts)
- [src/agents/code-mode.test-support.ts](src/agents/code-mode.test-support.ts)
- [src/agents/code-mode.test.ts](src/agents/code-mode.test.ts)
- [src/agents/code-mode.ts](src/agents/code-mode.ts)
- [src/agents/code-mode.wait.test.ts](src/agents/code-mode.wait.test.ts)
- [src/agents/code-mode.worker.ts](src/agents/code-mode.worker.ts)
- [src/agents/embedded-agent-runner/run/code-mode-outcome.test.ts](src/agents/embedded-agent-runner/run/code-mode-outcome.test.ts)
- [src/agents/embedded-agent-runner/run/code-mode-outcome.ts](src/agents/embedded-agent-runner/run/code-mode-outcome.ts)
- [src/agents/sessions/tools/limits.test.ts](src/agents/sessions/tools/limits.test.ts)
- [src/agents/sessions/tools/limits.ts](src/agents/sessions/tools/limits.ts)
- [src/agents/tool-search-catalog.ts](src/agents/tool-search-catalog.ts)
- [src/agents/tool-search-code-mode.ts](src/agents/tool-search-code-mode.ts)
- [src/agents/tool-search-config.ts](src/agents/tool-search-config.ts)
- [src/agents/tool-search-runtime.test.ts](src/agents/tool-search-runtime.test.ts)
- [src/agents/tool-search-runtime.ts](src/agents/tool-search-runtime.ts)
- [src/agents/tool-search-types.ts](src/agents/tool-search-types.ts)
- [src/agents/tool-search.stream-errors.test.ts](src/agents/tool-search.stream-errors.test.ts)
- [src/agents/tool-search.test-support.ts](src/agents/tool-search.test-support.ts)
- [src/agents/tool-search.test.ts](src/agents/tool-search.test.ts)
- [src/agents/tool-search.ts](src/agents/tool-search.ts)
- [src/agents/tools/gateway-tool.test.ts](src/agents/tools/gateway-tool.test.ts)
- [src/agents/tools/gateway-tool.ts](src/agents/tools/gateway-tool.ts)
- [src/auto-reply/reply/get-reply-native-slash-fast-path.ts](src/auto-reply/reply/get-reply-native-slash-fast-path.ts)
- [src/auto-reply/reply/get-reply.message-hooks.test.ts](src/auto-reply/reply/get-reply.message-hooks.test.ts)
- [src/auto-reply/reply/get-reply.ts](src/auto-reply/reply/get-reply.ts)
- [src/gateway/agent-prompt.ts](src/gateway/agent-prompt.ts)
- [src/gateway/embeddings-http.test.ts](src/gateway/embeddings-http.test.ts)
- [src/gateway/embeddings-http.ts](src/gateway/embeddings-http.ts)
- [src/gateway/open-responses.schema.ts](src/gateway/open-responses.schema.ts)
- [src/gateway/openai-compat-errors.ts](src/gateway/openai-compat-errors.ts)
- [src/gateway/openai-http.test.ts](src/gateway/openai-http.test.ts)
- [src/gateway/openai-http.ts](src/gateway/openai-http.ts)
- [src/gateway/openresponses-http.server.file-only.test.ts](src/gateway/openresponses-http.server.file-only.test.ts)
- [src/gateway/openresponses-http.test.ts](src/gateway/openresponses-http.test.ts)
- [src/gateway/openresponses-http.ts](src/gateway/openresponses-http.ts)
- [src/gateway/openresponses-parity.test.ts](src/gateway/openresponses-parity.test.ts)
- [src/gateway/openresponses-prompt.ts](src/gateway/openresponses-prompt.ts)
- [src/media-understanding/apply.test.ts](src/media-understanding/apply.test.ts)
- [src/media-understanding/apply.ts](src/media-understanding/apply.ts)
- [src/media-understanding/attachments.cache.test.ts](src/media-understanding/attachments.cache.test.ts)
- [src/media-understanding/attachments.cache.ts](src/media-understanding/attachments.cache.ts)
- [src/media-understanding/file-attachment-outcomes.test.ts](src/media-understanding/file-attachment-outcomes.test.ts)
- [src/media-understanding/file-attachment-outcomes.ts](src/media-understanding/file-attachment-outcomes.ts)
- [src/media-understanding/image-input-normalize.ts](src/media-understanding/image-input-normalize.ts)
- [src/media-understanding/media-understanding-misc.test.ts](src/media-understanding/media-understanding-misc.test.ts)
- [src/media-understanding/runtime.local-input.test.ts](src/media-understanding/runtime.local-input.test.ts)
- [src/media-understanding/runtime.test.ts](src/media-understanding/runtime.test.ts)
- [src/media-understanding/runtime.ts](src/media-understanding/runtime.ts)
- [src/media/input-files.extract.test.ts](src/media/input-files.extract.test.ts)
- [src/media/input-files.fetch-guard.test.ts](src/media/input-files.fetch-guard.test.ts)
- [src/media/input-files.ts](src/media/input-files.ts)
- [src/media/playback-transcode.test-support.ts](src/media/playback-transcode.test-support.ts)
- [src/media/playback-transcode.test.ts](src/media/playback-transcode.test.ts)
- [src/media/playback-transcode.ts](src/media/playback-transcode.ts)
- [test/transcripts-tool.discord-lifecycle.integration.test.ts](test/transcripts-tool.discord-lifecycle.integration.test.ts)

</details>



This section documents the implementation and integration of web search and fetch tools within the OpenClaw agent runtime. It covers supported web search providers, the HTTP fetch transport with SSRF (Server-Side Request Forgery) protection, and the integration of **Code Mode** for advanced tool orchestration.

---

## Overview

OpenClaw provides built-in web tools that extend agent capabilities with external web data access:

- **`web_search`**: Executes web queries across multiple providers (Brave, Perplexity, Tavily, xAI Grok, Kimi) offering structured search results or AI-grounded answers. [src/agents/tool-search.ts:49-50]()
- **`web_fetch`**: Fetches raw HTTP content and extracts readable markdown/text. It includes safeguards to prevent SSRF attacks and enforces resource limits. [src/media/input-files.ts:28-39]()

These tools are integrated into the agent's tool surface and can be orchestrated via standard tool calls or the experimental **Code Mode** QuickJS-WASI sandbox. [docs/tools/code-mode.md:33-36]()

Sources:
- [src/agents/tool-search.ts:47-52]()
- [docs/tools/code-mode.md:12-40]()

---

## Web Search Tool Integration

### Supported Providers & Runtime Resolution

OpenClaw supports various web search providers. The system selects the active provider based on available credentials and model capabilities.

| Provider | Implementation Details | Source |
|:---|:---|:---|
| **Brave** | Structured snippets from the Brave Search API. | `web_search` |
| **xAI Grok** | Integrated search via the Grok model provider. | `grok-search` |
| **Perplexity** | LLM-based search with real-time grounding. | `perplexity-search` |
| **Tavily** | AI-optimized search results. | `tavily-search` |
| **Kimi** | Search integration for the Kimi model family. | `kimi-search` |

### Tool Search & Cataloging
For agents with extensive toolsets, OpenClaw utilizes a **Tool Search** mechanism. This system moves web tools into a searchable catalog rather than exposing their full schemas in every prompt. The `ToolSearchRuntime` handles lexical indexing and scoring of tool metadata. [src/agents/tool-search-runtime.ts:67-77]()

Title: Tool Search and Catalog Flow
```mermaid
flowchart TD
    "Tools"["normalizeAgentRuntimeTools()"] --> "Catalog"["applyToolSearchCatalog()"]
    "Catalog" -->|Check| "Config"["resolveToolSearchConfig()"]
    "Config" -->|If Enabled| "Registry"["registerHeadlessToolSearchCatalog()"]
    "Registry" -->|Index| "SearchRuntime"["ToolSearchRuntime"]
    "SearchRuntime" -->|Score| "Lexical"["scoreLexical()"]
```

Sources:
- [src/agents/tool-search.ts:33-52]()
- [src/agents/tool-search-runtime.ts:60-77]()

---

## Code Mode Orchestration

**Code Mode** is an experimental feature where the model writes JavaScript or TypeScript programs to search, describe, and call tools. [docs/tools/code-mode.md:12-16]()

### Guest Bridge & QuickJS Sandbox
In Code Mode, tools are exposed as async globals inside a QuickJS-WASI worker. [docs/tools/code-mode.md:62-64]() The `runCodeModeExec` function manages the lifecycle of these executions, including snapshots and state parking for long-running tool calls. [src/agents/code-mode-execution.ts:61-73]()

Title: Code Mode Execution and Bridge Dispatch
```mermaid
flowchart TD
    "Model"["Model Output"] -->|Exec Tool| "Exec"["runCodeModeExec()"]
    "Exec" -->|Start| "Worker"["runCodeModeWorker()"]
    "Worker" -->|Call Tool| "Bridge"["runBridgeRequest()"]
    "Bridge" -->|Dispatch| "Host"["bridgeDispatch.operations"]
    "Host" -->|Result| "State"["settleCodeModeResult()"]
```

### State Management
Code Mode runs are tracked in the `activeRuns` map. [src/agents/code-mode-state.ts:69-69]() If a tool call is pending, the run can be "parked" as a `Snapshot` and resumed later via the `wait` tool. [src/agents/code-mode-state.ts:42-61](), [docs/tools/code-mode.md:79-83]()

Sources:
- [docs/tools/code-mode.md:25-40]()
- [src/agents/code-mode-execution.ts:108-122]()
- [src/agents/code-mode-state.ts:42-61]()

---

## Web Fetch & SSRF Protection

The `web_fetch` implementation relies on `fetchWithSsrFGuard` to ensure secure retrieval of web content. [src/gateway/openresponses-http.test.ts:45-58]()

### SSRF Guarding
The fetch system enforces strict boundaries on network requests:
- **Hostname Allowlist**: Configurable via `normalizeInputHostnameAllowlist`. [src/gateway/openai-http.ts:76-76]()
- **Private Network Blocking**: Prevents access to internal IP ranges (SSRF protection).
- **Resource Limits**: Enforces `maxBytes`, `timeoutMs`, and `maxRedirects` for all inbound media and web fetches. [src/media/input-files.ts:28-39]()

### Media Understanding Integration
Fetched web content, especially images and audio, is processed through the media understanding pipeline. [src/media-understanding/apply.ts:36-36]() This includes HEIC to JPEG conversion and audio transcription via providers like Groq or Deepgram. [src/media-understanding/apply.test.ts:82-101]()

Title: Media Understanding and Fetch Pipeline
```mermaid
flowchart TD
    "Input"["InputImageSource"] -->|Fetch| "Guard"["fetchWithSsrFGuard()"]
    "Guard" -->|Process| "Media"["applyMediaUnderstanding()"]
    "Media" -->|Probe| "Probe"["probePlaybackMediaFileDescriptor()"]
    "Probe" -->|Transcode| "FFmpeg"["runFfmpeg()"]
```

Sources:
- [src/media/input-files.ts:28-39]()
- [src/gateway/openresponses-http.ts:76-76]()
- [src/media-understanding/apply.test.ts:82-101]()

---

## HTTP API Integration

Web search and fetch capabilities are exposed through OpenAI-compatible endpoints.

### OpenResponses & OpenAI HTTP
- **`/v1/chat/completions`**: Translates OpenAI chat requests into agent runs, including tool definitions. [src/gateway/openai-http.ts:1-2]()
- **`/v1/responses`**: Implements the OpenResponses spec, allowing for rich tool output items. [src/gateway/openresponses-http.ts:4-7]()

The `resolveOpenAiChatCompletionsLimits` function ensures that incoming requests with large payloads (like base64 images) are bounded to prevent Gateway memory exhaustion. [src/gateway/openai-http.ts:146-163]()

Sources:
- [src/gateway/openai-http.ts:107-124]()
- [src/gateway/openresponses-http.ts:78-84]()

---

