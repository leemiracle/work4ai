<!-- source: DeepWiki mcp.deepwiki.com · repo anomalyco/opencode · extra page Compaction & Context Management · fetched 2026-10-27 -->

# Compaction & Context Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/core/src/codemode/catalog.ts](packages/core/src/codemode/catalog.ts)
- [packages/core/src/codemode/instructions.ts](packages/core/src/codemode/instructions.ts)
- [packages/core/src/codemode/tool.ts](packages/core/src/codemode/tool.ts)
- [packages/core/src/codemode/web.ts](packages/core/src/codemode/web.ts)
- [packages/core/src/session/compaction.ts](packages/core/src/session/compaction.ts)
- [packages/core/src/session/context.ts](packages/core/src/session/context.ts)
- [packages/core/src/session/history.ts](packages/core/src/session/history.ts)
- [packages/core/src/session/model-request.ts](packages/core/src/session/model-request.ts)
- [packages/core/src/session/runner/llm.ts](packages/core/src/session/runner/llm.ts)
- [packages/core/src/session/runner/publish-llm-event.ts](packages/core/src/session/runner/publish-llm-event.ts)
- [packages/core/src/session/runner/step.ts](packages/core/src/session/runner/step.ts)
- [packages/core/src/session/runner/to-llm-message.ts](packages/core/src/session/runner/to-llm-message.ts)
- [packages/core/src/session/store.ts](packages/core/src/session/store.ts)
- [packages/core/src/session/title.ts](packages/core/src/session/title.ts)
- [packages/core/test/codemode.test.ts](packages/core/test/codemode.test.ts)
- [packages/core/test/codemode/catalog.test.ts](packages/core/test/codemode/catalog.test.ts)
- [packages/core/test/codemode/instructions.test.ts](packages/core/test/codemode/instructions.test.ts)
- [packages/core/test/config/compaction.test.ts](packages/core/test/config/compaction.test.ts)
- [packages/core/test/session-compact.test.ts](packages/core/test/session-compact.test.ts)
- [packages/core/test/session-compaction.test.ts](packages/core/test/session-compaction.test.ts)
- [packages/core/test/session-model-request-hooks.test.ts](packages/core/test/session-model-request-hooks.test.ts)
- [packages/core/test/session-model-request.test.ts](packages/core/test/session-model-request.test.ts)
- [packages/core/test/session-native-compaction.test.ts](packages/core/test/session-native-compaction.test.ts)
- [packages/core/test/session-runner-message.test.ts](packages/core/test/session-runner-message.test.ts)
- [packages/core/test/session-runner-recorded.test.ts](packages/core/test/session-runner-recorded.test.ts)
- [packages/core/test/session-runner-tool-events.test.ts](packages/core/test/session-runner-tool-events.test.ts)
- [packages/core/test/session-runner.test.ts](packages/core/test/session-runner.test.ts)
- [packages/core/test/session-step.test.ts](packages/core/test/session-step.test.ts)
- [packages/core/test/session-title.test.ts](packages/core/test/session-title.test.ts)
- [packages/core/test/tool-execute.test.ts](packages/core/test/tool-execute.test.ts)
- [services/www/src/docs/content/compaction.mdx](services/www/src/docs/content/compaction.mdx)

</details>



## Purpose & Scope
This page details OpenCode's context management, compaction architecture, and token lifecycle mechanisms implemented in `packages/core`. It covers the `SessionCompaction` service, context assembly via `SessionModelRequest`, runtime overflow recovery loops in `SessionRunnerLLM`, instruction discovery (such as `AGENTS.md` parsing), and dynamic token budgeting.

---

## 1. Summary vs. Native Compaction
OpenCode supports two distinct modes of context reduction to handle long-running sessions that approach model context windows: **Summary Compaction** (local structural abstraction) and **Native Compaction** (provider-handled state caching/compaction).

The compaction engine is managed by `SessionCompaction.Service`, which evaluates triggers (`auto`, `overflow`, or `manual`) and produces an outcome status (`skipped`, `completed`, or `failed`) [packages/core/src/session/compaction.ts:53-67]().

```mermaid
graph TD
    "SessionRunnerLLM" -->|"Overflow or Limit Exceeded"| "SessionCompaction.Service"
    "SessionCompaction.Service" -->|"Manual /compact"| "TriggerDecision"
    "TriggerDecision" -->|"Summary Mode"| "BuildPrompt"
    "TriggerDecision" -->|"Native Mode"| "ProviderContextState"
    "BuildPrompt" --> "LLMClient.stream"
    "LLMClient.stream" --> "StructuredCheckpoint"
    "StructuredCheckpoint" --> "SessionStore"
```
*Sources: [packages/core/src/session/runner/llm.ts:112-145](), [packages/core/src/session/compaction.ts:53-80]()*

### Summary Compaction Format
When executing summary compaction, the system enforces a strict Markdown template that separates state into explicit blocks: Objective, Requirements, Decisions, Work State (Completed, Active, Blocked), Next Move, Relevant Files, and Important Context [packages/core/src/session/compaction.ts:104-135](). 

Rules enforced during summary generation require terse, single-line bullets, exact path preservation, and the omission of transient tool outputs [packages/core/src/session/compaction.ts:137-143]().

---

## 2. Context Assembly & Instructions Discovery
Before an LLM request is dispatched, the session context assembler compiles system prompts, available tool inventories, discovered instructions (`AGENTS.md`), and historical message transcripts [packages/core/src/session/model-request.ts:100-120]().

### Instruction Discovery
Instruction files like `AGENTS.md` are dynamically discovered when tools (such as the `read` tool) traverse project paths. The filesystem walk searches upward from the target path toward the session root, loading matching files as durable synthetic instructions into the session database [packages/core/test/session-runner.test.ts:70-76]().

```mermaid
graph TD
    "ReadTool" -->|"File Read Success"| "FSUtilUp"
    "FSUtilUp" -->|"Finds AGENTS.md"| "InstructionsDiscovery"
    "InstructionsDiscovery" --> "SessionInboxTable"
    "SessionContext.select" --> "InstructionDiscovery"
    "InstructionDiscovery" --> "SessionModelRequest"
    "SessionModelRequest" --> "LLMRequest"
```
*Sources: [packages/core/test/session-runner.test.ts:70-76](), [packages/core/src/session/model-request.ts:100-120](), [packages/core/src/session/context.ts]()*

---

## 3. Token Budgeting & Output Limits
To prevent hitting maximum context limits mid-generation, `SessionModelRequest` dynamically computes output token limits based on model limits, measured input tokens, and estimated text expansions [packages/core/src/session/model-request.ts:88-98]().

The output headroom formula accounts for an estimation error margin (`ESTIMATE_ERROR = 0.15`) over raw character lengths [packages/core/src/session/model-request.ts:54-57](). If the catalog provides no limit, it falls back to `OUTPUT_TOKEN_FALLBACK` (32,000 tokens), capped by `OUTPUT_TOKEN_MAX` (256,000 tokens) and floored by `OUTPUT_TOKEN_MIN` (1,024 tokens) [packages/core/src/session/model-request.ts:49-57]().

---

## 4. Overflow Shrinking & Recovery Loop
When a model rejects a prompt due to context length overflow (`isContextOverflowFailure`), the execution pipeline initiates an overflow recovery shrinkage sequence defined by `SHRINK_STEPS` [packages/core/src/session/compaction.ts:94-95]().

```mermaid
graph TD
    "SessionRunnerLLM" --> "SessionModelRequest"
    "SessionModelRequest" --> "LLMClient.stream"
    "LLMClient.stream" -->|"ContextOverflowFailure"| "SessionCompaction.compact"
    "SessionCompaction.compact" -->|"Shrink step: 0.7, 0.5, 0.35"| "RetryRequest"
    "RetryRequest" --> "SessionRunnerRetry"
```
*Sources: [packages/core/src/session/runner/llm.ts:54-146](), [packages/core/src/session/compaction.ts:94-97](), [packages/core/src/session/runner/retry.ts]() *

---

