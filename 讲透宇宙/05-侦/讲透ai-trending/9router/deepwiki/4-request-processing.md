<!-- source: DeepWiki mcp.deepwiki.com · repo decolua/9router · page 4 Request Processing · fetched 2026-10-30 -->

# Request Processing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [images/fusion-combo-ui.png](images/fusion-combo-ui.png)
- [open-sse/handlers/chatCore.js](open-sse/handlers/chatCore.js)
- [open-sse/services/combo.js](open-sse/services/combo.js)
- [open-sse/translator/concerns/modality.js](open-sse/translator/concerns/modality.js)
- [src/sse/handlers/chat.js](src/sse/handlers/chat.js)
- [src/sse/services/auth.js](src/sse/services/auth.js)
- [tests/unit/combo-fusion.test.js](tests/unit/combo-fusion.test.js)
- [tests/unit/fetch-success-clears-account.test.js](tests/unit/fetch-success-clears-account.test.js)
- [tests/unit/hermes-vision-detection.test.js](tests/unit/hermes-vision-detection.test.js)

</details>



This page documents how 9Router processes incoming AI chat and embeddings requests from ingress through provider execution to response delivery. It serves as a high-level overview of the request lifecycle, authentication, account selection, format translation, streaming response processing, and usage tracking.

For deep technical details, refer to the child pages:
- [Chat Request Flow](#4.1) — Trace a chat request from ingress through provider selection and execution.
- [Streaming & SSE Processing](#4.2) — Explain SSE handling, stream-to-JSON conversion, usage extraction.
- [Format Translation Pipeline](#4.3) — Detail request/response translation modules, concerns, state management.
- [Usage Tracking & Analytics](#4.4) — Token counting, cost calculation, request detail logging.
- [Token Savers (RTK, Headroom, Caveman, Ponytail, PXPipe)](#4.5) — Document the open-sse/rtk pipeline and compression/prompt-modifier subsystems.

---

## 4.1 Chat Request Flow

Requests enter 9Router via ingress endpoints like `/v1/chat/completions` handled by `handleChat()` in `src/sse/handlers/chat.js` [src/sse/handlers/chat.js:35-35](). The system validates API keys, resolves model aliases or combo chains, and delegates the payload to `handleChatCore()` located in `open-sse/handlers/chatCore.js` [open-sse/handlers/chatCore.js:63-63](). 

During execution, `getProviderCredentials()` in `src/sse/services/auth.js` selects an available account while respecting rate limits, model locks, and provider-specific quotas [src/sse/services/auth.js:28-28](). If a transient error occurs, `checkFallbackError()` in `open-sse/services/accountFallback.js` determines whether to trigger an account fallback [open-sse/services/accountFallback.js:23-23]().

Diagram: Request Routing and Execution Lifecycle (Code Entity Space)
```mermaid
graph TD
    Client[""Client Request Ingress""] --> HandleChat[""src/sse/handlers/chat.js:handleChat()""]
    HandleChat --> Auth[""src/sse/services/auth.js:getProviderCredentials()""]
    Auth --> ChatCore[""open-sse/handlers/chatCore.js:handleChatCore()""]
    ChatCore --> Translator[""open-sse/translator/index.js:translateRequest()""]
    Translator --> Executor[""open-sse/executors/index.js:getExecutor()""]
    Executor --> Upstream[""Upstream AI Provider""]
```

For details, see [Chat Request Flow](#4.1).

Sources:
- [src/sse/handlers/chat.js:35-153]()
- [open-sse/handlers/chatCore.js:63-110]()
- [src/sse/services/auth.js:28-102]()
- [open-sse/services/accountFallback.js:23-47]()

---

## 4.2 Streaming & SSE Processing

Server-Sent Events (SSE) and streaming responses are managed via stream controllers and handlers. When an upstream provider returns a streaming response, `createStreamController()` in `open-sse/utils/streamHandler.js` handles chunk parsing, event dispatching, and stream-to-JSON conversion [open-sse/utils/streamHandler.js:6-6](). 

Depending on whether the source and target formats match, the system operates in either translation or passthrough mode, extracting token usage metrics on-the-fly. For details, see [Streaming & SSE Processing](#4.2).

Sources:
- [open-sse/handlers/chatCore.js:21-21]()
- [open-sse/utils/streamHandler.js:6-6]()

---

## 4.3 Format Translation Pipeline

9Router translates requests and responses between disparate provider schemas (such as OpenAI, Claude, Gemini, and OpenAI Responses API formats). The core transformation logic resides in `open-sse/translator/index.js`, where `translateRequest()` maps input payloads to the target provider's expected schema [open-sse/handlers/chatCore.js:2-2](). 

Concerns such as reasoning block extraction via `extractThinking()`, modality stripping via `stripUnsupportedModalities()`, and prompt prefetching are handled as modular pipeline steps [open-sse/handlers/chatCore.js:3-32](). For details, see [Format Translation Pipeline](#4.3).

Sources:
- [open-sse/handlers/chatCore.js:2-35]()
- [open-sse/translator/index.js:1-50]()

---

## 4.4 Usage Tracking & Analytics

As requests are processed and completed, usage data is recorded for monitoring and cost calculation. The system tracks pending requests via `trackPendingRequest()` and persists completed request logs and detailed metrics through `appendRequestLog()` and `saveRequestDetail()` in `src/lib/usageDb.js` [src/lib/usageDb.js:7](). 

Aggregated metrics and real-time statistics are emitted to the web dashboard via event emitters and queryable logs. For details, see [Usage Tracking & Analytics](#4.4).

Sources:
- [open-sse/handlers/chatCore.js:15-21]()
- [src/lib/usageDb.js:7]()

---

## 4.5 Token Savers (RTK, Headroom, Caveman, Ponytail, PXPipe)

To optimize token usage, latency, and costs, requests can pass through an optional token-saving pipeline prior to upstream translation. This includes real-time tokenization compression via `compressMessages()` (`open-sse/rtk/index.js`), remote compression proxies via `compressWithHeadroom()` (`open-sse/rtk/headroom.js`), and prompt modifiers like `injectCaveman()` and `injectPonytail()` [open-sse/handlers/chatCore.js:25-29]().

Diagram: Token Saver Execution Pipeline (Code Entity Space)
```mermaid
graph TD
    Incoming[""Incoming Messages Body""] --> RTK[""open-sse/rtk/index.js:compressMessages()""]
    RTK --> Headroom[""open-sse/rtk/headroom.js:compressWithHeadroom()""]
    Headroom --> Caveman[""open-sse/rtk/caveman.js:injectCaveman()""]
    Caveman --> Ponytail[""open-sse/rtk/ponytail.js:injectPonytail()""]
    Ponytail --> PXPipe[""open-sse/rtk/pxpipe.js:compressWithPxpipe()""]
    PXPipe --> Translated[""Translated Outbound Payload""]
```

For details, see [Token Savers (RTK, Headroom, Caveman, Ponytail, PXPipe)](#4.5).

Sources:
- [open-sse/handlers/chatCore.js:25-29]()
- [open-sse/rtk/index.js:1-30]()
- [open-sse/rtk/headroom.js:1-25]()

---

