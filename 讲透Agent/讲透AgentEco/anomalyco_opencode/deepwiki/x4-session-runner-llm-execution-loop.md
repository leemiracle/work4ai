<!-- source: DeepWiki mcp.deepwiki.com · repo anomalyco/opencode · extra page Session Runner & LLM Execution Loop · fetched 2026-10-27 -->

# Session Runner & LLM Execution Loop

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/ai/src/provider-error.ts](packages/ai/src/provider-error.ts)
- [packages/ai/src/route/executor.ts](packages/ai/src/route/executor.ts)
- [packages/ai/src/route/transport/websocket.ts](packages/ai/src/route/transport/websocket.ts)
- [packages/ai/src/schema/errors.ts](packages/ai/src/schema/errors.ts)
- [packages/ai/src/schema/messages.ts](packages/ai/src/schema/messages.ts)
- [packages/ai/test/executor.test.ts](packages/ai/test/executor.test.ts)
- [packages/ai/test/provider-error.test.ts](packages/ai/test/provider-error.test.ts)
- [packages/ai/test/provider/image-detail.test.ts](packages/ai/test/provider/image-detail.test.ts)
- [packages/ai/test/schema.test.ts](packages/ai/test/schema.test.ts)
- [packages/ai/test/tool-runtime.test.ts](packages/ai/test/tool-runtime.test.ts)
- [packages/core/src/aisdk.ts](packages/core/src/aisdk.ts)
- [packages/core/src/effect/app-node-platform.ts](packages/core/src/effect/app-node-platform.ts)
- [packages/core/src/effect/websocket-constructor.ts](packages/core/src/effect/websocket-constructor.ts)
- [packages/core/src/generate.ts](packages/core/src/generate.ts)
- [packages/core/src/kv.ts](packages/core/src/kv.ts)
- [packages/core/src/model-retry.ts](packages/core/src/model-retry.ts)
- [packages/core/src/session/compaction.ts](packages/core/src/session/compaction.ts)
- [packages/core/src/session/execution.ts](packages/core/src/session/execution.ts)
- [packages/core/src/session/execution/restart.ts](packages/core/src/session/execution/restart.ts)
- [packages/core/src/session/generate.ts](packages/core/src/session/generate.ts)
- [packages/core/src/session/history.ts](packages/core/src/session/history.ts)
- [packages/core/src/session/model-request.ts](packages/core/src/session/model-request.ts)
- [packages/core/src/session/model-transport.ts](packages/core/src/session/model-transport.ts)
- [packages/core/src/session/run-coordinator.ts](packages/core/src/session/run-coordinator.ts)
- [packages/core/src/session/runner/index.ts](packages/core/src/session/runner/index.ts)
- [packages/core/src/session/runner/llm.ts](packages/core/src/session/runner/llm.ts)
- [packages/core/src/session/runner/model.ts](packages/core/src/session/runner/model.ts)
- [packages/core/src/session/runner/publish-llm-event.ts](packages/core/src/session/runner/publish-llm-event.ts)
- [packages/core/src/session/runner/retry.ts](packages/core/src/session/runner/retry.ts)
- [packages/core/src/session/runner/step.ts](packages/core/src/session/runner/step.ts)
- [packages/core/src/session/runner/to-llm-message.ts](packages/core/src/session/runner/to-llm-message.ts)
- [packages/core/src/session/store.ts](packages/core/src/session/store.ts)
- [packages/core/src/session/subagent-completion.ts](packages/core/src/session/subagent-completion.ts)
- [packages/core/src/session/title.ts](packages/core/src/session/title.ts)
- [packages/core/src/session/to-session-error.ts](packages/core/src/session/to-session-error.ts)
- [packages/core/src/shell.ts](packages/core/src/shell.ts)
- [packages/core/src/tool/plugin/shell.ts](packages/core/src/tool/plugin/shell.ts)
- [packages/core/src/tool/plugin/subagent.ts](packages/core/src/tool/plugin/subagent.ts)
- [packages/core/src/tool/plugin/webfetch.ts](packages/core/src/tool/plugin/webfetch.ts)
- [packages/core/test/aisdk.test.ts](packages/core/test/aisdk.test.ts)
- [packages/core/test/config/command-subagent.test.ts](packages/core/test/config/command-subagent.test.ts)
- [packages/core/test/config/compaction.test.ts](packages/core/test/config/compaction.test.ts)
- [packages/core/test/effect-app-node-platform.test.ts](packages/core/test/effect-app-node-platform.test.ts)
- [packages/core/test/generate.test.ts](packages/core/test/generate.test.ts)
- [packages/core/test/kv.test.ts](packages/core/test/kv.test.ts)
- [packages/core/test/lib/tool.ts](packages/core/test/lib/tool.ts)
- [packages/core/test/session-compact.test.ts](packages/core/test/session-compact.test.ts)
- [packages/core/test/session-compaction.test.ts](packages/core/test/session-compaction.test.ts)
- [packages/core/test/session-error.test.ts](packages/core/test/session-error.test.ts)
- [packages/core/test/session-execution.test.ts](packages/core/test/session-execution.test.ts)
- [packages/core/test/session-generate.test.ts](packages/core/test/session-generate.test.ts)
- [packages/core/test/session-model-request-hooks.test.ts](packages/core/test/session-model-request-hooks.test.ts)
- [packages/core/test/session-model-request.test.ts](packages/core/test/session-model-request.test.ts)
- [packages/core/test/session-model-transport-live.test.ts](packages/core/test/session-model-transport-live.test.ts)
- [packages/core/test/session-model-transport.test.ts](packages/core/test/session-model-transport.test.ts)
- [packages/core/test/session-native-compaction.test.ts](packages/core/test/session-native-compaction.test.ts)
- [packages/core/test/session-run-coordinator.test.ts](packages/core/test/session-run-coordinator.test.ts)
- [packages/core/test/session-runner-message.test.ts](packages/core/test/session-runner-message.test.ts)
- [packages/core/test/session-runner-recorded.test.ts](packages/core/test/session-runner-recorded.test.ts)
- [packages/core/test/session-runner-retry.test.ts](packages/core/test/session-runner-retry.test.ts)
- [packages/core/test/session-runner-tool-events.test.ts](packages/core/test/session-runner-tool-events.test.ts)
- [packages/core/test/session-runner.test.ts](packages/core/test/session-runner.test.ts)
- [packages/core/test/session-step.test.ts](packages/core/test/session-step.test.ts)
- [packages/core/test/session-title.test.ts](packages/core/test/session-title.test.ts)
- [packages/core/test/tool-shell.test.ts](packages/core/test/tool-shell.test.ts)
- [packages/core/test/tool-subagent.test.ts](packages/core/test/tool-subagent.test.ts)
- [packages/plugin/src/effect/storage.ts](packages/plugin/src/effect/storage.ts)
- [packages/protocol/src/groups/shell.ts](packages/protocol/src/groups/shell.ts)
- [packages/schema/src/shell.ts](packages/schema/src/shell.ts)
- [packages/server/src/handlers/shell.ts](packages/server/src/handlers/shell.ts)
- [services/www/src/docs/content/compaction.mdx](services/www/src/docs/content/compaction.mdx)

</details>



### Purpose & Scope
This page details the implementation of the core session execution engine within OpenCode, specifically the `SessionRunnerLLM` service (`packages/core/src/session/runner/llm.ts`). It covers the drain and step event-loop, model-request compilation (`packages/core/src/session/model-request.ts`), classification of provider errors and transient retry logic (`packages/ai/src/provider-error.ts`), error mapping (`packages/core/src/session/to-session-error.ts`), real-time LLM event publishing (`packages/core/src/session/runner/publish-llm-event.ts`), and snapshot integration with git workflows.

---

### Drain & Step Execution Loop (`SessionRunnerLLM`)

The session execution loop is orchestrated by `SessionRunnerLLM`, which consumes items from the session inbox, manages execution steps, drives tool calls, and handles mid-stream interruptions or compactions [packages/core/src/session/runner/llm.ts:54-146]().

When a drain request is triggered via `SessionRunner.drain()`, the service evaluates pending promotable items in the session inbox [packages/core/src/session/runner/llm.ts:54-66](). Once active, it enters an uninterruptible mask loop (`advanceToStep`) that checks location liveness and synchronizes control actions like manual compactions or workspace moves [packages/core/src/session/runner/llm.ts:71-115]().

Diagram: Natural Language Space to Code Entity Space for Drain Execution
```mermaid
graph TD
  "DrainTrigger" --> ["SessionRunner.drain"]
  ["SessionRunner.drain"] --> ["SessionInbox.nextPromotable"]
  ["SessionInbox.nextPromotable"] --> ["Plugin.awaitActivation"]
  ["Plugin.awaitActivation"] --> ["SessionRunner.advanceToStep"]
  ["SessionRunner.advanceToStep"] --> ["LocationLifecycle.isClosed"]
  ["LocationLifecycle.isClosed"] -->|Active| ["SessionInbox.serialized"]
  ["SessionInbox.serialized"] --> ["SessionCompaction.compact"]
  ["SessionInbox.serialized"] --> ["SessionModelRequest.compaction"]
```
*Sources: `packages/core/src/session/runner/llm.ts:54-146`*

If an incomplete stream or interruption occurs, the runner appends continuation markers (such as `CONTINUE_AFTER_INCOMPLETE_STREAM`) to maintain conversational continuity without re-processing completed parts [packages/core/src/session/runner/llm.ts:35-36]().

Sources: `packages/core/src/session/runner/llm.ts:35-146`

---

### Model-Request Construction (`SessionModelRequest`)

Before dispatching prompts to model providers, OpenCode compiles session histories, system instructions, and tool definitions into a normalized `LLMRequest` object using `SessionModelRequest` (`packages/core/src/session/model-request.ts`).

The core transcript builder (`baseTranscript`) aggregates system prompts from agent specifications, injected instruction files, and initial session metadata, then maps historical messages via `toLLMMessages` [packages/core/src/session/model-request.ts:100-120]().

Diagram: Natural Language Space to Code Entity Space for Model Request Building
```mermaid
graph TD
  "TranscriptAssembly" --> ["SessionModelRequest"]
  ["SessionModelRequest"] --> ["baseTranscript"]
  ["baseTranscript"] --> ["Agent.Info"]
  ["baseTranscript"] --> ["InstructionBuiltIns"]
  ["baseTranscript"] --> ["toLLMMessages"]
  ["toLLMMessages"] --> ["LLMRequest"]
```
*Sources: `packages/core/src/session/model-request.ts:100-120`, `packages/core/src/session/runner/to-llm-message.ts:1-50`*

Token limits and output budgets are dynamically computed using `outputLimit`, which evaluates model context caps, measured/estimated prompt tokens, and reserves room for final responses and summaries [packages/core/src/session/model-request.ts:88-98](). Media assets (images, audio, PDFs) are validated against model capability definitions and stripped or removed if unsupported [packages/core/src/session/model-request.ts:132-147]().

Sources: `packages/core/src/session/model-request.ts:60-154`

---

### Retries, Error Mapping, and Provider Failures

When interacting with LLM providers, failures can occur due to rate limiting, context overflows, or provider internal errors. OpenCode classifies these errors to determine whether a request can be safely retried.

The function `isRetryable` evaluates whether an `AIError` is eligible for repetition based on reason tags, headers (`x-should-retry`), and delivery statuses [packages/ai/src/provider-error.ts:81-116]().

Context overflows are detected via regex pattern matchers that inspect error messages for threshold breaches (e.g., `isContextOverflow`), triggering automatic or manual compaction flows [packages/ai/src/provider-error.ts:66-75](). Raw errors are mapped into standardized session error structures via `toSessionError` [packages/core/src/session/to-session-error.ts:1-40]().

Sources: `packages/ai/src/provider-error.ts:66-116`, `packages/core/src/session/to-session-error.ts:1-50`

---

### LLM Event Publishing (`createLLMEventPublisher`)

During step execution, streaming responses and tool invocations emit fine-grained events via `createLLMEventPublisher` (`packages/core/src/session/runner/publish-llm-event.ts`). 

The publisher maintains thread-safe synchronization between concurrent provider output processing and tool execution fibers. Two concurrency invariants govern this design:
1. **Synchronous State Marking**: State updates (such as `tool.settled` or `stepStarted`) must be marked synchronously before any `await` or `yield` to preserve atomicity under cooperative scheduling [packages/core/src/session/runner/publish-llm-event.ts:67-78]().
2. **Event Sequencing**: Cross-source ordering relies on per-source monotonic sequences rather than global locks [packages/core/src/session/runner/publish-llm-event.ts:75-77]().

Diagram: Natural Language Space to Code Entity Space for Event Publishing
```mermaid
graph TD
  "StreamOutput" --> ["LLMStream"]
  ["LLMStream"] --> ["createLLMEventPublisher"]
  ["createLLMEventPublisher"] -->|SessionEvent.Step.Started| ["Bus.Service"]
  ["createLLMEventPublisher"] -->|SessionEvent.Step.Streamed| ["Bus.Service"]
  ["createLLMEventPublisher"] -->|Tool Execution| ["Tool.Snapshot.execute"]
  ["Tool.Snapshot.execute"] --> ["SessionMessage"]
```
*Sources: `packages/core/src/session/runner/publish-llm-event.ts:79-124`*

Delta text chunks are batched at regular intervals (defaulting to `100ms`) to minimize database write contention and UI re-render thrashing [packages/core/src/session/runner/publish-llm-event.ts:80-156]().

Sources: `packages/core/src/session/runner/publish-llm-event.ts:1-156`

---

### Snapshots and Git Integration

To maintain project integrity across execution steps, the session runner integrates with the `Snapshot` service and local Git repositories (`packages/core/src/snapshot.ts`).

Before a step initiates, pending snapshots are captured asynchronously, allowing file-system modifications to be tracked and correlated with assistant turns [packages/core/src/session/runner/publish-llm-event.ts:23-27](). Working tree diffs, branch resolutions, and commit statuses are managed through git utility hooks, ensuring changes applied by tools can be audited or reverted.

Sources: `packages/core/src/snapshot.ts:1-50`

---

