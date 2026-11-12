<!-- source: DeepWiki mcp.deepwiki.com · repo decolua/9router · extra page Kiro / CodeWhisperer Executor · fetched 2026-10-30 -->

# Kiro / CodeWhisperer Executor

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [open-sse/config/kiroConstants.js](open-sse/config/kiroConstants.js)
- [open-sse/executors/kiro.js](open-sse/executors/kiro.js)
- [open-sse/providers/registry/kiro.js](open-sse/providers/registry/kiro.js)
- [open-sse/translator/concerns/kiroConversation.js](open-sse/translator/concerns/kiroConversation.js)
- [open-sse/translator/request/claude-to-kiro.js](open-sse/translator/request/claude-to-kiro.js)
- [open-sse/translator/request/openai-to-kiro.js](open-sse/translator/request/openai-to-kiro.js)
- [open-sse/translator/response/kiro-to-claude.js](open-sse/translator/response/kiro-to-claude.js)
- [open-sse/utils/kiroSessionReplay.js](open-sse/utils/kiroSessionReplay.js)
- [tests/translator/agent-client-fixes.test.js](tests/translator/agent-client-fixes.test.js)
- [tests/translator/claude-kiro-direct.test.js](tests/translator/claude-kiro-direct.test.js)
- [tests/translator/kiro-tool-name-roundtrip.test.js](tests/translator/kiro-tool-name-roundtrip.test.js)
- [tests/unit/capabilities-opus-context.test.js](tests/unit/capabilities-opus-context.test.js)
- [tests/unit/kiro-api-key-endpoint-routing.test.js](tests/unit/kiro-api-key-endpoint-routing.test.js)
- [tests/unit/kiro-claude-opus-5-5.test.js](tests/unit/kiro-claude-opus-5-5.test.js)
- [tests/unit/kiro-minimal-wire-payload.test.js](tests/unit/kiro-minimal-wire-payload.test.js)
- [tests/unit/kiro-model-slots.test.js](tests/unit/kiro-model-slots.test.js)
- [tests/unit/kiro-tool-result-placeholder.test.js](tests/unit/kiro-tool-result-placeholder.test.js)
- [tests/unit/openai-to-kiro.test.js](tests/unit/openai-to-kiro.test.js)
- [tests/unit/thinking-levels-kiro.test.js](tests/unit/thinking-levels-kiro.test.js)

</details>



This page provides a detailed technical overview of the Kiro / CodeWhisperer executor within 9Router (`open-sse/executors/kiro.js`). It covers the translation mechanisms for converting OpenAI and Claude API requests into Kiro's native format, conversation state and canonicalization (`kiroConversation.js`), AWS EventStream binary parsing, the integrity gate and repair loop, session replay, and authentication / profile ARN configuration constants.

## Kiro Request Translation

9Router supports direct translation of both OpenAI (`openai-to-kiro.js`) and Claude (`claude-to-kiro.js`) API requests into Kiro/AWS CodeWhisperer `GenerateAssistantResponse` payloads [open-sse/translator/request/openai-to-kiro.js](), [open-sse/translator/request/claude-to-kiro.js]().

### OpenAI to Kiro Translation

The `openaiToKiroRequest` function in `open-sse/translator/request/openai-to-kiro.js` converts OpenAI Chat Completions requests into Kiro format. The message parsing relies on `convertMessages`, which normalizes roles, merges consecutive same-role turns, handles image payloads, and transforms tool calls and results [open-sse/translator/request/openai-to-kiro.js:43-90]().

* **Role Normalization**: OpenAI `system` and `tool` roles are normalized to `user` roles in Kiro history [open-sse/translator/request/openai-to-kiro.js:96-100]().
* **Content Merging**: Consecutive messages sharing a role are merged to satisfy Kiro's strict alternating turn requirements [open-sse/translator/request/openai-to-kiro.js:102-106]().
* **Image Handling**: Base64 data URIs from `image_url` blocks are mapped to Kiro's `userInputMessage.images` format (`{ format, source: { bytes } }`), while HTTP/HTTPS image URLs fall back to text placeholders [open-sse/translator/request/openai-to-kiro.js:118-128]().
* **Tool Call/Result Handling**: OpenAI `tool_calls` map to Kiro `toolUses`, and tool result messages map to `userInputMessageContext.toolResults` [open-sse/translator/request/openai-to-kiro.js:141-154]().

#### Natural Language to Code Entity: Request Translation Pipeline

```mermaid
graph TD
    subgraph "Natural Language Space"
        NL_REQ[""Client Chat Request (OpenAI/Claude)""] --> NL_TRANS[""Request Translation & Normalization""]
        NL_TRANS --> NL_CANON[""Conversation State Canonicalization""]
    end

    subgraph "Code Entity Space"
        NL_REQ --> O2K[""openaiToKiroRequest(model, body, stream, credentials)""]
        O2K --> C2K[""claudeToKiroRequest(model, body, stream, credentials)""]
        O2K --> CONV_MSG[""convertMessages(messages, model)""]
        C2K --> CONV_CLAUDE[""convertClaudeMessagesToKiro(messages, model)""]
        CONV_MSG & CONV_CLAUDE --> CANON[""canonicalizeKiroConversation(history, currentMessage, modelId)""]
        CANON --> REPLAY[""applyKiroSessionReplay(conversationState, credentials)""]
        REPLAY --> INTENT[""resolveKiroModelIntent(model)""]
        INTENT --> OVERRIDE[""applyKiroThinkingOverride(body, override)""]
        OVERRIDE --> FIELDS[""buildKiroAdditionalModelRequestFieldsForModel(body, model)""]
    end
```
Sources:
- [open-sse/translator/request/openai-to-kiro.js]()
- [open-sse/translator/request/openai-to-kiro.js:43-90]()
- [open-sse/translator/request/openai-to-kiro.js:96-100]()
- [open-sse/translator/request/openai-to-kiro.js:102-106]()
- [open-sse/translator/request/openai-to-kiro.js:118-128]()
- [open-sse/translator/request/openai-to-kiro.js:141-154]()
- [open-sse/translator/request/claude-to-kiro.js]()

### Claude to Kiro Translation

The `claude-to-kiro.js` module implements a direct translation pipeline from Anthropic Messages API requests to Kiro payloads, avoiding any intermediary OpenAI format pivot [open-sse/translator/request/claude-to-kiro.js:1-17].

* **Role Alternation**: `convertClaudeMessagesToKiro` aggregates consecutive user or assistant messages [open-sse/translator/request/claude-to-kiro.js:45-84]().
* **Tool Results and Tool Uses**: Claude `tool_result` blocks are transformed into Kiro `toolResults`, and `tool_use` blocks populate `assistantResponseMessage.toolUses` [open-sse/translator/request/claude-to-kiro.js:98-143]().
* **Orphan Protection**: If a `tool_result` references an unknown `tool_use_id`, it is gracefully folded into user text to prevent upstream 400 validation failures [tests/translator/claude-kiro-direct.test.js:58-71]().

Sources:
- [open-sse/translator/request/claude-to-kiro.js]()
- [open-sse/translator/request/claude-to-kiro.js:1-17]
- [open-sse/translator/request/claude-to-kiro.js:45-84]
- [open-sse/translator/request/claude-to-kiro.js:98-143]
- [tests/translator/claude-kiro-direct.test.js:58-71]

## Conversation State (`conversationState`) & Canonicalization

Kiro requires structured conversation payloads containing `conversationId`, `history`, and `currentMessage`. The shared canonicalizer in `open-sse/translator/concerns/kiroConversation.js` enforces structural rules [open-sse/translator/concerns/kiroConversation.js:158-190]():

* **Turn Validation**: Eliminates malformed turns where user and assistant presence conflict.
* **Placeholder Management**: Inserts `KIRO_EMPTY_USER_PLACEHOLDER` (`"continue"`) or `KIRO_TOOL_RESULTS_PLACEHOLDER` (`"Tool results provided."`) when user turns lack text content, preventing model rejection [open-sse/translator/concerns/kiroConversation.js:15-21]().
* **Tool Spec Normalization**: `normalizeKiroToolSpecs` cleans tool names against `KIRO_TOOL_NAME_MAX_LENGTH` (64 characters) and strips unsupported schema attributes like `additionalProperties` [open-sse/translator/concerns/kiroConversation.js:92-123]().

Sources:
- [open-sse/translator/concerns/kiroConversation.js:15-21]()
- [open-sse/translator/concerns/kiroConversation.js:92-123]()
- [open-sse/translator/concerns/kiroConversation.js:158-190]()

## AWS EventStream Processing

Kiro upstream responses arrive via AWS EventStream (`application/vnd.amazon.eventstream`), which is a binary framing protocol [open-sse/providers/registry/kiro.js:31](). The `KiroExecutor` (`open-sse/executors/kiro.js`) decodes this binary stream into standard Server-Sent Events [open-sse/executors/kiro.js:1-15].

* **Event Frame Parsing**: Uses `parseEventFrame` and `crc32` validation to verify frame integrity (`open-sse/utils/awsEventStream.js`) [open-sse/executors/kiro.js:14]().
* **Recognized Event Types**: Filters events via `KIRO_EVENT_TYPES` including `assistantResponseEvent`, `reasoningContentEvent`, `codeEvent`, `toolUseEvent`, and `messageStopEvent` [open-sse/executors/kiro.js:21-32]().

#### Natural Language to Code Entity: Execution and Stream Processing

```mermaid
graph TD
    subgraph "Natural Language Space"
        NL_EXEC[""Upstream AWS Streaming Execution""] --> NL_PARSE[""Binary Frame Decoding & CRC Check""]
        NL_PARSE --> NL_INTEGRITY[""Integrity Gate & Retry Evaluation""]
    end

    subgraph "Code Entity Space"
        NL_EXEC --> EXEC[""KiroExecutor.execute(connection, body, signal)""]
        EXEC --> TIMEOUT[""readWithTimeout(reader, signal, timeoutMs, message)""]
        TIMEOUT --> FRAME[""parseEventFrame(chunk)""]
        FRAME --> CRC[""crc32(headerAndPayloadBytes)""]
        CRC --> TYPES[""KIRO_EVENT_TYPES.has(eventType)""]
        TYPES --> REPAIR[""appendRepairInstruction(body, kind)""]
    end
```
Sources:
- [open-sse/executors/kiro.js]()
- [open-sse/executors/kiro.js:1-15]()
- [open-sse/executors/kiro.js:14]()
- [open-sse/executors/kiro.js:21-32]()
- [open-sse/executors/kiro.js:73-90]()

## Integrity Gate & Repair Subsystem

The Kiro executor incorporates an integrity gate that monitors response completion and tool wrapper formatting. If a tool call wrapper is malformed or a response terminates prematurely with ellipsis or incomplete action clauses, the executor triggers an automated retry loop [open-sse/executors/kiro.js:35-50]().

* **Repair Instructions**: `appendRepairInstruction` injects targeted prompts into the user turn (`REPAIR_INSTRUCTIONS` such as `tool`, `ellipsis`, or `short_final`) to guide the model toward correct completion [open-sse/executors/kiro.js:122-131]().

Sources:
- [open-sse/executors/kiro.js:35-50]()
- [open-sse/executors/kiro.js:122-131]()

## Session Replay & Session Management

Kiro maintains context continuity via `applyKiroSessionReplay` (`open-sse/utils/kiroSessionReplay.js`), which injects frozen initial message turns when session identifiers are present in request headers [tests/translator/claude-kiro-direct.test.js:19-37](). Session identities and continuation tokens are resolved via `resolveSessionIdentity` and `resolveContinuationId` [open-sse/translator/request/openai-to-kiro.js:9]().

Sources:
- [open-sse/translator/request/openai-to-kiro.js:9]()
- [open-sse/utils/kiroSessionReplay.js]()
- [tests/translator/claude-kiro-direct.test.js:19-37]()

## Authentication, Profile ARNs & Constants

Kiro configuration constants (`open-sse/config/kiroConstants.js`) and registry settings (`open-sse/providers/registry/kiro.js`) define target endpoints and profile mapping rules.

* **Profile ARNs**: `KIRO_DEFAULT_PROFILE_ARNS` and `resolveDefaultProfileArn(authMethod)` resolve default profile ARNs (us-east-1) for Builder ID, social sign-ins (Google/GitHub), and IAM Identity Center [open-sse/config/kiroConstants.js:33-45]().
* **Model Intents & Thinking Overrides**: `resolveKiroModelIntent` strips suffixes like `-agentic` or `-thinking` and applies thinking budgets or native effort configurations (`applyKiroThinkingOverride`, `resolveKiroThinkingBudget`) [open-sse/config/kiroConstants.js:53-80]().

Sources:
- [open-sse/config/kiroConstants.js:33-45]()
- [open-sse/config/kiroConstants.js:53-80]()
- [open-sse/providers/registry/kiro.js]()

---

