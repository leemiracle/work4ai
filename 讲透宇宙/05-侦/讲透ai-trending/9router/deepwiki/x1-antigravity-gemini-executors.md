<!-- source: DeepWiki mcp.deepwiki.com · repo decolua/9router · extra page Antigravity & Gemini Executors · fetched 2026-10-30 -->

# Antigravity & Gemini Executors

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [open-sse/executors/antigravity.js](open-sse/executors/antigravity.js)
- [open-sse/executors/vertex.js](open-sse/executors/vertex.js)
- [open-sse/providers/registry/gemini.js](open-sse/providers/registry/gemini.js)
- [open-sse/providers/registry/vertex.js](open-sse/providers/registry/vertex.js)
- [open-sse/translator/index.js](open-sse/translator/index.js)
- [open-sse/translator/request/openai-to-gemini.js](open-sse/translator/request/openai-to-gemini.js)
- [open-sse/translator/response/claude-to-openai.js](open-sse/translator/response/claude-to-openai.js)
- [open-sse/translator/response/gemini-to-openai.js](open-sse/translator/response/gemini-to-openai.js)
- [open-sse/translator/response/kiro-to-openai.js](open-sse/translator/response/kiro-to-openai.js)
- [open-sse/translator/response/ollama-to-openai.js](open-sse/translator/response/ollama-to-openai.js)
- [open-sse/translator/response/openai-responses.js](open-sse/translator/response/openai-responses.js)
- [open-sse/translator/response/openai-to-claude.js](open-sse/translator/response/openai-to-claude.js)
- [open-sse/utils/stream.js](open-sse/utils/stream.js)
- [src/sse/services/antigravityQuota.js](src/sse/services/antigravityQuota.js)
- [tests/unit/antigravity-quota-routing.test.js](tests/unit/antigravity-quota-routing.test.js)
- [tests/unit/gemini-4-argon.test.js](tests/unit/gemini-4-argon.test.js)
- [tests/unit/gemini-duplicate-tool-call-ids.test.js](tests/unit/gemini-duplicate-tool-call-ids.test.js)
- [tests/unit/vertex-location.test.js](tests/unit/vertex-location.test.js)

</details>



This page details the `AntigravityExecutor`, `VertexExecutor`, and their roles in handling requests for Google's Antigravity, Gemini, and Vertex AI models within the 9Router system. It covers executor implementations, translation pipelines between OpenAI and Gemini formats, quota routing mechanisms, and transient error/retry hooks.

## Antigravity Executor Implementation

The `AntigravityExecutor` is a specialized subclass of `BaseExecutor` responsible for interfacing with Google's Antigravity API. It handles unique request/response formats, IDE-specific tracing headers, image generation model parameters, and authentication.

The executor initializes with the provider ID `"antigravity"` and configuration from `PROVIDERS.antigravity` [open-sse/executors/antigravity.js:113-116]().

```mermaid
graph TD
    sub532_Client[""Client Request""] -->|"POST /v1/chat/completions"| sub532_Router[""Router Engine""];
    sub532_Router -->|"execute()"| sub532_AntigravityExecutor[""AntigravityExecutor (open-sse/executors/antigravity.js)""];
    sub532_AntigravityExecutor -->|"transformRequest()"| sub532_OpenaiToGemini[""openaiToGeminiBase (open-sse/translator/request/openai-to-gemini.js)""];
    sub532_AntigravityExecutor -->|"buildUrl()"| sub532_ApiEndpoint[""Antigravity /v1internal API""];
    sub532_ApiEndpoint -->|"Response Stream"| sub532_GeminiToOpenAI[""geminiToOpenAIResponse (open-sse/translator/response/gemini-to-openai.js)""];
    sub532_GeminiToOpenAI -->|"OpenAI Chunks"| sub532_Client;
```
**Title: Antigravity Executor Natural Language to Code Entity Flow**
Sources: [open-sse/executors/antigravity.js:113-116](), [open-sse/translator/request/openai-to-gemini.js:76](), [open-sse/translator/response/gemini-to-openai.js:41]()

### Key Methods & Request Transformation

The `transformRequest` method prepares payloads for the Antigravity backend [open-sse/executors/antigravity.js:172]() through several normalization steps:

1.  **Project ID Generation**: Resolves or generates a `projectId` using credentials [open-sse/executors/antigravity.js:173]().
2.  **Image Model Parsing**: Detects image generation models using `isImageModel` and configures aspect ratios via `parseImageConfig` [open-sse/executors/antigravity.js:66-90]().
3.  **IDE Request ID Construction**: Generates an `ideRequestId` via `buildIdeRequestId` matching the pattern `agent/<conversationId>/<timestamp>/<trajectoryId>/<step>` to emulate official Google IDE clients [open-sse/executors/antigravity.js:100-111]().
4.  **Blacklisted Field Stripping**: Strips fields unsupported by Gemini (e.g., `output_config`, `thinking`, `reasoning_effort`, `enable_thinking`) via `stripBlacklisted` [open-sse/executors/antigravity.js:43-56]().
5.  **Tool Name Sanitization**: Cleans function names using `sanitizeFunctionName` to ensure compliance with Gemini's naming restrictions [open-sse/executors/antigravity.js:13-18]().

The `buildUrl` method conditionally appends `streamGenerateContent?alt=sse` or `generateContent` depending on whether streaming is enabled and whether the model is an image generator [open-sse/executors/antigravity.js:153-160](). The `buildHeaders` method applies authorization Bearer tokens and required user agents [open-sse/executors/antigravity.js:164-170]().

Sources: [open-sse/executors/antigravity.js:1-175]()

## Gemini Request & Response Translation Pipeline

Translating requests and responses between OpenAI and Gemini formats involves dedicated core utility modules in the translation pipeline.

```mermaid
graph TD
    sub532_Req[""OpenAI Request Body""] --> sub532_Translator[""openaiToGeminiBase (open-sse/translator/request/openai-to-gemini.js)""];
    sub532_Translator --> sub532_Uniquifier[""createToolCallIdUniquifier (open-sse/translator/request/openai-to-gemini.js)""];
    sub532_Uniquifier --> sub532_GeminiPayload[""Gemini Contents & Generation Config""];
    
    sub532_Resp[""Gemini SSE Chunk""] --> sub532_GeminiParser[""geminiToOpenAIResponse (open-sse/translator/response/gemini-to-openai.js)""];
    sub532_GeminiParser --> sub532_Signatures[""storeGeminiThoughtSignature (open-sse/services/thoughtSignatureStore.js)""];
    sub532_Signatures --> sub532_OpenAIChunks[""OpenAI SSE Chunks""];
```
**Title: Gemini Translation Pipeline Code Entities**
Sources: [open-sse/translator/request/openai-to-gemini.js:57-76](), [open-sse/translator/response/gemini-to-openai.js:9-41]()

### Request Translation (`openaiToGeminiBase`)

The `openaiToGeminiBase` function converts OpenAI chat completion structures into Gemini-compatible payloads [open-sse/translator/request/openai-to-gemini.js:76](). Key operations include:
*   Extracting sampling parameters (`temperature`, `top_p`, `top_k`) when permitted by model capabilities [open-sse/translator/request/openai-to-gemini.js:85-95]().
*   Converting system messages into `systemInstruction` objects and user/assistant turns into Gemini `contents` parts [open-sse/translator/request/openai-to-gemini.js:140-190]().
*   Using `createToolCallIdUniquifier` to guarantee that function call IDs remain unique across long agent histories, preventing upstream `400 INVALID_ARGUMENT` rejections [open-sse/translator/request/openai-to-gemini.js:57-74]().

### Response Translation (`geminiToOpenAIResponse`)

The `geminiToOpenAIResponse` function processes inbound Gemini or Antigravity streaming chunks and maps them to OpenAI chat completion deltas [open-sse/translator/response/gemini-to-openai.js:41](). 
*   It handles thought signatures using `storeGeminiThoughtSignature` to preserve thinking states for subsequent tool execution turns [open-sse/translator/response/gemini-to-openai.js:9-26]().
*   It transforms Gemini `functionCall` structures into OpenAI `tool_calls` via `emitFunctionCall` [open-sse/translator/response/gemini-to-openai.js:17-38]().

Sources: [open-sse/translator/request/openai-to-gemini.js:1-531](), [open-sse/translator/response/gemini-to-openai.js:1-163]()

## Vertex AI Executor (`VertexExecutor`)

The `VertexExecutor` manages Google Cloud Vertex AI integrations, distinguishing between Gemini models via regional/global endpoints and partner models (such as Llama or Mistral) via global OpenAI-compatible endpoints [open-sse/executors/vertex.js:62-84]().

*   **Authentication & Token Minting**: Supports Service Account (SA) JSON parsing (`parseVertexSaJson`), Application Default Credentials (ADC) user credentials (`parseVertexAdcJson`), and explicit bearer tokens [open-sse/executors/vertex.js:14-30, 68-70]().
*   **Project Resolution**: Automatically probes endpoints to resolve missing `project_id` values from raw API keys or ADC metadata [open-sse/executors/vertex.js:36-50, 163-164]().
*   **Location Routing**: Adheres to configured regions or defaults global-only models (e.g., Gemini Argon) to global infrastructure [open-sse/executors/vertex.js:95-98]().

Sources: [open-sse/executors/vertex.js:1-185](), [tests/unit/vertex-location.test.js:1-70]()

## Retry Hooks & Quota Error Handling

The `AntigravityExecutor` implements `parseError` to inspect failed API responses and extract precise quota reset timings [open-sse/executors/antigravity.js:119]().

1.  **Quota Reset Parsing**: Evaluates HTTP `429` and `409` responses, parsing `quotaResetTimeStamp` or `retryDelay` from error details to determine exact backoff windows [open-sse/executors/antigravity.js:120-147]().
2.  **Transient Error Patterns**: Matches error bodies against `ANTIGRAVITY_TRANSIENT_ERROR_PATTERNS` (detecting high traffic, agent termination errors, capacity warnings, or timeouts) [open-sse/executors/antigravity.js:25-33]().
3.  **Transient Status Codes**: Evaluates standard server error statuses (`ANTIGRAVITY_TRANSIENT_STATUSES`) including `500`, `502`, `503`, and `504` to trigger automatic provider-level failovers [open-sse/executors/antigravity.js:35-40]().

Sources: [open-sse/executors/antigravity.js:20-56](), [open-sse/executors/antigravity.js:119-151]()

---

