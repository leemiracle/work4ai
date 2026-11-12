<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/browser-use-pi · page 6 Glossary · fetched 2026-10-30 -->

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/api.md](docs/api.md)
- [src/index.ts](src/index.ts)
- [src/model-stream.ts](src/model-stream.ts)
- [src/prompt.ts](src/prompt.ts)
- [src/runtime.ts](src/runtime.ts)
- [src/server.ts](src/server.ts)
- [src/types.ts](src/types.ts)
- [test/model-stream.test.mjs](test/model-stream.test.mjs)

</details>



This page defines key terms used within the `@browser_use/pi` codebase, providing technical explanations, implementation details, and code pointers to aid understanding for developers.

## Pi Mono
`Pi Mono` refers to the monorepo structure of the underlying agent framework, specifically `@earendil-works/pi-agent-core` and `@earendil-works/pi-ai`. These are external dependencies that provide the core agent logic, model interaction, and tool execution capabilities. `browser-use-pi` builds upon this framework to add browser automation features.

Sources:
* [src/index.ts:4-7]()

## Persistent V8 REPL
The agent executes JavaScript code within a persistent V8 REPL (Read-Eval-Print Loop). This REPL runs in a separate Node.js worker process, managed by the `BrowserRuntime` class. "Persistent" means that top-level `await`, variables, and functions declared in one execution (`cell`) survive across subsequent executions within the same run. This allows the agent to maintain state and build up complex browser interactions. The worker process is isolated from the main agent process, ensuring that browser actions and JavaScript state are managed independently.

Sources:
* [src/runtime.ts:45-46]()
* [src/runtime.ts:78-84]()
* [src/prompt.ts:3-3]()

## Cell
A `cell` refers to a single block of JavaScript code executed by the agent in the persistent V8 REPL. Each `cell` execution is isolated in terms of its timeout and potential for error. If a `cell` times out or the worker process crashes, the JavaScript state within that worker is reset. The `BrowserRuntime.executeCell` method is responsible for sending and managing the execution of these code blocks.

Sources:
* [src/runtime.ts:171-177]()
* [src/prompt.ts:35-35]()

## CellError
`CellError` is a custom error class thrown when a JavaScript `cell` execution fails within the browser worker. It includes the `CellResult` (which contains details about the failure) and a `stateReset` boolean indicating whether the JavaScript state in the worker was reset due to the error. This distinction is important because some errors might not necessitate a full state reset, while others (like worker crashes or timeouts) do.

Sources:
* [src/runtime.ts:34-42]()
* [src/index.ts:36-36]()

## AX tree
The `AX tree` (Accessibility Tree) is a representation of the web page's content and structure, optimized for accessibility tools. The agent is instructed to "Prefer the accessibility tree for discovery" [src/prompt.ts:16-16]. This means the agent should primarily use the AX tree to identify elements and their properties (like `role`, `name`, `value`, `checked`, etc.) rather than relying solely on DOM selectors. This approach makes the agent more robust to changes in page structure and more aligned with how users perceive the page.

Sources:
* [src/prompt.ts:9-9]()
* [src/prompt.ts:16-16]()

## backendNodeId
A `backendNodeId` is a unique identifier assigned by the Chrome DevTools Protocol (CDP) to a DOM node. Unlike frontend Node IDs, `backendNodeId`s are stable across page reloads or navigations as long as the underlying DOM node remains the same. The agent uses `backendNodeId`s for interacting with specific elements, for example, to scroll an element into view (`DOM.scrollIntoViewIfNeeded`) or get its box model (`DOM.getBoxModel`).

Sources:
* [src/prompt.ts:16-19]()
* [src/prompt.ts:22-22]()

## CDP target/session
In the context of Chrome DevTools Protocol (CDP), a `target` represents an inspectable entity, such as a browser tab, a web worker, or an iframe. A `session` is an active connection to a specific `target`, allowing the client (the agent) to send commands and receive events related to that target. The `BrowserRuntime` manages the connection to the browser and its targets. The `targetId` property in `BrowserRuntime` refers to the ID of the primary page target the agent is currently interacting with.

Sources:
* [src/runtime.ts:55-55]()
* [src/runtime.ts:63-63]()
* [src/runtime.ts:113-113]()
* [src/prompt.ts:13-14]()

## Observation target
The term "observation target" is not explicitly defined as a distinct entity in the provided code. However, the `observe` option in `RunOptions` [src/types.ts:71-71]() suggests a mechanism for external systems to receive `AgentEvent`s. This implies that any component or system configured to receive these events acts as an "observation target," consuming real-time updates about the agent's progress and actions.

Sources:
* [src/types.ts:71-71]()

## Compaction
`Compaction` is the process of summarizing older context in the agent's conversation history to stay within the model's context window limits. When `compaction: true` is set in `RunOptions` [src/types.ts:68-68](), the agent will automatically use the Pi framework's summarization capabilities to reduce the size of the message history. This is a soft boundary; if compaction fails or times out, the original context is retained, and the run might terminate due to `context_limit`.

Sources:
* [src/types.ts:36-36]()
* [src/types.ts:68-68]()
* [docs/api.md:46-46]()
* [test/model-stream.test.mjs:131-153]()

## Checkpoint/partial findings
A `checkpoint` is a mechanism for the agent to save its progress and intermediate results. The `checkpoint(filename, value, {partial:true})` helper [src/prompt.ts:30-30]() allows the agent to atomically save JSON data and publish it as a "partial result" to the caller. These partial findings are available even if the run terminates prematurely (e.g., due to timeout or worker loss) and do not need to satisfy the final schema. They are crucial for recovery and providing continuous feedback.

Sources:
* [src/prompt.ts:30-30]()
* [src/types.ts:105-105]()
* [docs/api.md:86-95]()

## Run journal
The "run journal" refers to the comprehensive logging of all model observations and agent actions during a run. This journal is saved to the workspace, allowing for post-mortem analysis and debugging. The agent is instructed to "read files instead of repeating completed actions" [src/prompt.ts:33-33] from this journal, implying it can be used for recovery or to understand past behavior.

Sources:
* [src/prompt.ts:33-33]()

## Stop reasons
`Stop reasons` are enumerated statuses indicating why an agent run terminated. These include `max_steps`, `timeout`, `cancelled`, `cost_limit`, `context_limit`, `incomplete`, and `error`. The `RunResult` type [src/types.ts:97-107]() explicitly defines these reasons, providing clarity on the outcome of an agent's execution.

Sources:
* [src/types.ts:77-78]()
* [src/types.ts:97-107]()
* [docs/api.md:45-45]()

## RunControl
`RunControl` is a class that provides mechanisms for external control over an active agent run. It allows for pausing, resuming, steering, and canceling the agent's execution. This is implemented using an `AbortController` and associated signals to manage the lifecycle of the agent's operations.

Sources:
* [src/index.ts:15-15]()
* [src/index.ts:51-51]()

## Observer
An `Observer` is a function provided via the `observe` option in `RunOptions` [src/types.ts:71-71](). It receives `AgentEvent`s in a best-effort, non-blocking manner. Unlike `onEvent`, which applies backpressure, `observe` may coalesce events under heavy load, making it suitable for monitoring or telemetry where occasional dropped events are acceptable.

Sources:
* [src/types.ts:71-71]()
* [docs/api.md:53-53]()

## Workspace
The `workspace` is a persistent directory on the filesystem where the agent stores all its artifacts, including run journals, screenshots, downloaded files, and checkpoints. It defaults to a new OS temporary directory but can be specified via `BrowserUseOptions.workspace` [src/types.ts:24-24](). This directory is crucial for debugging, auditing, and recovering from failures.

Sources:
* [src/index.ts:64-64]()
* [src/index.ts:137-139]()
* [src/types.ts:24-24]()
* [docs/api.md:31-31]()

## Artifact
An `artifact` is a file created by the agent within its `workspace` using the `artifact(filename, textOrBytes)` helper [src/prompt.ts:29-29](). This helper ensures the file is exclusive and returns its path. Artifacts can include any data the agent deems important to save, such as extracted data, logs, or intermediate results.

Sources:
* [src/prompt.ts:29-29]()

## Reconnect
The `reconnect()` helper [src/prompt.ts:31-31]() allows the agent to reset its CDP connection while preserving the Node.js bindings and files in the worker. This is useful in scenarios where the browser state might be corrupted or the CDP connection is lost, enabling the agent to re-establish communication and reacquire tab handles without losing its JavaScript context.

Sources:
* [src/prompt.ts:31-31]()

## Findings mode
"Findings mode" is a concept mentioned in the evaluation harness [docs/api.md:5]() but not explicitly defined in the provided code. It likely refers to a mode of operation or reporting where the primary focus is on collecting and presenting the "findings" or results of the agent's task, especially in the context of QA or research. This would involve emphasizing partial findings and checkpoints.

Sources:
* [docs/api.md:5]()

## Faux provider
A `faux provider` is a mock implementation of a model provider, used primarily for testing purposes. It allows tests to simulate model responses without making actual API calls to external LLM services. The `@earendil-works/pi-ai` library provides utilities like `fauxProvider()` and `createAssistantMessageEventStream` for this purpose.

Sources:
* [test/model-stream.test.mjs:9-12]()

## bu-pi-server bridge
The `bu-pi-server bridge` refers to the `src/server.ts` module, which implements a private, versioned stdio protocol. This bridge facilitates communication between the `browser-use-pi` Node.js agent and external clients, particularly the Python client. It handles method dispatch, tool calls, and event streaming over standard input/output, enabling cross-language interaction.

```mermaid
graph TD
    A[Python Client] -- "stdio (JSON protocol)" --> B[bu-pi-server (src/server.ts)]
    B -- "BrowserUse.create/run/followUp" --> C[BrowserUse (src/index.ts)]
    C -- "CDP Commands" --> D[Browser Runtime (src/runtime.ts)]
    D -- "Browser Actions" --> E[Chrome Browser]
    C -- "Model API Calls" --> F[LLM Provider]
    B -- "Events" --> A
    B -- "Tool Call Requests" --> A
    A -- "Tool Call Results" --> B
```
**Diagram: bu-pi-server Bridge Architecture**

Sources:
* [src/server.ts:1-2]()
* [src/server.ts:114-115]()
* [src/server.ts:143-158]()

## sensitiveData/redaction
`sensitiveData` is an option in `BrowserUseOptions` [src/types.ts:16-16]() that allows users to provide named credentials or other sensitive values. These values are then automatically included in the `redact` list [src/index.ts:77-79](). `redaction` is the process of replacing sensitive information (specified in the `redact` array) with placeholders in logs, events, and saved text to prevent accidental exposure. It does not redact screenshots.

Sources:
* [src/types.ts:16-16]()
* [src/types.ts:47-47]()
* [src/index.ts:9-9]()
* [src/index.ts:77-79]()
* [docs/api.md:37-37]()

## Telemetry
`Telemetry` refers to the anonymous usage data collected by `browser-use-pi`. This includes run counters, SDK version, OS, Node version, browser mode, stop status, steps, duration, token counts, and estimated cost. It explicitly excludes sensitive information like user IDs, model IDs, tasks, URLs, page content, paths, credentials, or raw errors. Telemetry is opt-out and can be disabled via `telemetry: false` in options, `DO_NOT_TRACK=1`, or `ANONYMIZED_TELEMETRY=false` environment variables.

```mermaid
graph TD
    A[BrowserUse.create] --> B{Telemetry Enabled?}
    B -- Yes --> C[Telemetry (src/telemetry.ts)]
    C -- "Report Run Data" --> D[PostHog (EU Project)]
    D -- "Anonymous Counters" --> E[Analytics Dashboard]
    B -- No --> F[No Telemetry Sent]
```
**Diagram: Telemetry Data Flow**

Sources:
* [src/types.ts:19-19]()
* [src/index.ts:10-10]()
* [src/index.ts:66-66]()
* [docs/api.md:97-100]()