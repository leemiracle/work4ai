<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/browser-use-pi · page 2 Public SDK API · fetched 2026-10-30 -->

# Public SDK API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/api.md](docs/api.md)
- [src/index.ts](src/index.ts)
- [src/model-stream.ts](src/model-stream.ts)
- [src/server.ts](src/server.ts)
- [src/types.ts](src/types.ts)
- [test/model-stream.test.mjs](test/model-stream.test.mjs)

</details>



This page provides a high-level overview of the public API surface for the `@browser_use/pi` SDK, focusing on the `BrowserUse` class, its options, and the types of results it returns. It serves as a parent page, linking to more detailed child pages for in-depth explanations of specific functionalities.

The core interaction with the SDK revolves around creating a `BrowserUse` instance, running tasks, following up on previous runs, and finally closing the session.

```javascript
import { BrowserUse, Type } from '@browser_use/pi';

async function main() {
  const agent = await BrowserUse.create({
    model: 'openrouter/openai/gpt-5.6-luna',
    // ... other creation options
  });

  try {
    const result = await agent.run('Read the page title at example.com.', {
      schema: Type.Object({ title: Type.String() }),
      // ... other run options
    });

    if (result.status === 'completed') {
      console.log(result.output.title);
    } else {
      console.error(result.status, result.text);
    }

    // Optionally, follow up on a previous run
    // const followUpResult = await agent.followUp('Summarize the content.', { /* ... */ });

  } finally {
    await agent.close();
  }
}

main();
```
Sources: [docs/api.md:7-21]()

## BrowserUse Class Lifecycle <a name="2.1"></a>

The `BrowserUse` class manages a single browser session, a dedicated workspace, and a JavaScript execution environment. Its lifecycle involves creation, running tasks, potentially following up on previous tasks, executing arbitrary JavaScript, and finally closing the session.

### Creation (`BrowserUse.create`)

The `BrowserUse.create(options)` static method initializes a new browser automation session. This involves setting up the browser environment, configuring the model, and preparing the workspace. Key options at creation time include:
- `model`: Specifies the AI model to use (e.g., `'openai/gpt-5.4'`). [src/types.ts:21]()
- `browser`: Configuration for the browser instance itself. [src/types.ts:22]()
- `workspace`: A persistent output directory for artifacts. [src/types.ts:24]()
- `historyFile`: Path to a file for restoring or saving session history. [src/types.ts:56]()
- `telemetry`: Controls anonymous usage reporting. [src/types.ts:19]()
- `sensitiveData`: Defines named credentials for redaction and policy enforcement. [src/types.ts:17]()
- `allowedDomains` / `prohibitedDomains`: Navigation policy rules. [src/types.ts:16]()
- `tools`: Custom agent tools. [src/types.ts:30]()
- `beforeToolCall` / `afterToolCall`: Hooks for controlling tool execution. [src/types.ts:40-53]()

For details, see [BrowserUse Class Lifecycle](#2.1).

### Running Tasks (`run`, `followUp`, `execute`)

- `agent.run(task, options)`: Initiates a new task. It resets the agent's context, meaning it starts fresh without memory of previous interactions.
- `agent.followUp(task, options)`: Continues a previous task, retaining the agent's context and conversation history. This is useful for iterative refinement or multi-step workflows.
- `agent.execute(code, options)`: Allows direct execution of JavaScript code within the browser's context. [src/server.ts:195-196]()

Both `run` and `followUp` accept `RunOptions` which include:
- `schema`: A TypeBox schema for validating the expected output. [docs/api.md:13]()
- `maxSteps`: Maximum number of agent turns. [src/types.ts:63]()
- `timeoutMs`: Overall task timeout. [src/types.ts:64]()
- `maxCostUsd`: A soft cap on the estimated cost of model interactions. [src/types.ts:66]()
- `compaction`: Controls automatic context summarization. [src/types.ts:68]()
- `signal`: An `AbortSignal` for external cancellation. [src/types.ts:70]()

### Closing (`close`)

`agent.close()`: Releases all resources associated with the `BrowserUse` instance, including the browser process and temporary files. It's crucial to call this method to prevent resource leaks.

### RunResult

The `run` and `followUp` methods return a `RunResult` object, which provides comprehensive information about the task's outcome.
```typescript
export type RunResult<T = string> = RunMetrics &
  (
    | { status: 'completed'; output: T; text: string }
    | {
        status: StopReason;
        output?: never;
        text: string;
        error?: string;
        partial?: { path?: string; value: unknown };
      }
  );
```
Sources: [src/types.ts:97-107]()

A `RunResult` includes:
- `status`: Indicates the outcome (e.g., `'completed'`, `'timeout'`, `'error'`). [src/types.ts:99-102]()
- `output`: The validated result if `status` is `'completed'` and a `schema` was provided. [src/types.ts:99]()
- `text`: The raw text output from the agent. [src/types.ts:99]()
- `partial`: Contains the latest published JSON value and its file path if the run was interrupted before completion. [src/types.ts:105]()
- `RunMetrics`: Provides performance and resource usage details, such as `steps`, `durationMs`, `usage`, `model`, and `workspace`. [src/types.ts:79-96]()

For details, see [BrowserUse Class Lifecycle](#2.1).

### Diagram: BrowserUse Class Lifecycle

```mermaid
graph TD
    subgraph "BrowserUse Class Lifecycle"
        A[BrowserUse.create(BrowserUseOptions)] --> B{BrowserUse Instance};
        B -- "New Task" --> C[agent.run(task, RunOptions)];
        B -- "Continue Task" --> D[agent.followUp(task, RunOptions)];
        B -- "Direct JS Execution" --> E[agent.execute(code, options)];
        C --> F{RunResult};
        D --> F;
        E --> G{CellResult};
        F -- "Status: 'completed'" --> H[Output: T];
        F -- "Status: 'error' / 'timeout' / etc." --> I[Partial Output / Error];
        B -- "When done" --> J[agent.close()];
        J --> K[Resources Released];
    end

    subgraph "RunOptions"
        RO1[schema: TSchema]
        RO2[maxSteps: number]
        RO3[timeoutMs: number]
        RO4[maxCostUsd: number]
        RO5[compaction: boolean]
        RO6[signal: AbortSignal]
    end

    subgraph "BrowserUseOptions"
        BO1[model: string]
        BO2[browser: BrowserOptions]
        BO3[workspace: string]
        BO4[historyFile: string]
        BO5[telemetry: boolean]
        BO6[sensitiveData: SensitiveData]
        BO7[allowedDomains/prohibitedDomains]
        BO8[tools: AgentTool[]]
        BO9[beforeToolCall/afterToolCall]
    end

    RO1 --- C; RO2 --- C; RO3 --- C; RO4 --- C; RO5 --- C; RO6 --- C;
    RO1 --- D; RO2 --- D; RO3 --- D; RO4 --- D; RO5 --- D; RO6 --- D;

    BO1 --- A; BO2 --- A; BO3 --- A; BO4 --- A; BO5 --- A; BO6 --- A; BO7 --- A; BO8 --- A; BO9 --- A;
```
Sources: [src/index.ts:42-43](), [src/index.ts:69-167](), [src/types.ts:16-61](), [src/types.ts:62-76](), [src/types.ts:97-107]()

## Events, Control and Streaming <a name="2.2"></a>

The SDK provides mechanisms for observing the agent's progress, controlling its execution, and handling partial results.

### Event Streaming (`events()`, `onEvent`, `observe`)

The `agent.events()` method returns an asynchronous iterator that yields `SessionEvent` objects, providing a real-time stream of the agent's activities. This allows for detailed monitoring and logging of the agent's thought process, tool calls, and browser interactions.
- `onEvent`: An awaited callback for processing events, applying backpressure. [src/types.ts:75]()
- `observe`: A best-effort, non-blocking callback for observations, which may coalesce under load. [src/types.ts:71]()

### Run Control (`RunControl`)

During a run, the `RunControl` object (accessible internally) allows for dynamic interaction with the agent. While not directly exposed as a public API for `BrowserUse` instances, it underpins functionalities like:
- **Pause/Resume**: Temporarily halt and restart agent execution.
- **Steer**: Inject new instructions or modify the agent's path.
- **Cancel**: Abort the current run. This can also be achieved via the `signal` in `RunOptions`.

### Checkpoints and Partial Findings

The agent can publish partial findings using `checkpoint('findings.json', findings, { partial: true })` [docs/api.md:89](). If a run is interrupted (e.g., by a timeout or cancellation), the `RunResult` may contain a `partial` field with the latest published JSON value and its file path. This allows for recovery and inspection of work done before termination.

### Run Journals

The `historyFile` option in `BrowserUseOptions` allows for saving and restoring the agent's conversation history, effectively creating a "run journal." This enables persistent sessions and the ability to pick up where a previous session left off.

For details, see [Events, Control and Streaming](#2.2).

### Diagram: Event Flow and Control

```mermaid
graph TD
    subgraph "Agent Execution"
        A[agent.run() / agent.followUp()] --> B{Agent Loop};
        B -- "Tool Call / Thinking" --> C[Generate SessionEvent];
        C --> D[EventStream (agent.events())];
        C --> E[onEvent Callback];
        C --> F[observe Callback];
    end

    subgraph "External Control"
        G[AbortSignal (RunOptions.signal)] --> B;
        H[RunControl (Internal)] --> B;
        H -- "Pause" --> B;
        H -- "Resume" --> B;
        H -- "Steer" --> B;
        H -- "Cancel" --> B;
    end

    subgraph "Partial Results"
        B -- "Agent publishes findings" --> I[checkpoint()];
        I --> J[Partial Data in RunResult.partial];
    end

    D -- "Async Iterator" --> K[External Event Consumer];
    E -- "Awaited" --> L[Application Logic];
    F -- "Best-effort" --> M[Telemetry / Monitoring];
```
Sources: [src/index.ts:52](), [src/index.ts:23](), [src/types.ts:70-75](), [docs/api.md:52-53](), [docs/api.md:89-90]()

## Sessions, History and Recording <a name="2.3"></a>

The SDK provides features for managing session state, persisting interaction history, and recording browser activity.

### Session Persistence and History (`historyFile`)

The `historyFile` option in `BrowserUseOptions` allows the agent to save its conversation history and browser state to a specified file. When `BrowserUse.create` is called with a `historyFile`, it attempts to load a previously saved session. This enables long-running tasks or resuming work across different invocations of the SDK. The `loadHistory` and `saveHistory` functions [src/index.ts:17-22]() manage this persistence.

### Video Recording (`recording`)

The `recording` option in `BrowserUseOptions` enables video recording of the browser session. This can be configured with `RecordingOptions` [src/types.ts:12]() to control aspects like `intervalMs` (frame capture interval) and `maxFrames`. The `Recorder` class [src/index.ts:14]() handles the actual recording process. The path to the recorded video is included in the `RunMetrics` as `recordingPath`. [src/types.ts:93]()

For details, see [Sessions, History and Recording](#2.3).

## Python Client and stdio Bridge <a name="2.4"></a>

The `@browser_use/pi` SDK can be integrated with Python applications through a dedicated client and a versioned stdio bridge.

### Python Client (`browser_use_next`)

A Python client library, `browser_use_next`, provides an asynchronous interface to interact with the `BrowserUse` SDK. This client abstracts away the underlying communication protocol, allowing Python developers to use the browser automation capabilities seamlessly.

### Pydantic Schema Handling

The Python client supports Pydantic schemas for defining the expected input and output types of tasks. This enables strong typing and validation of data exchanged between the Python application and the TypeScript agent.

### Python-defined Tools

Python applications can define custom tools that the agent can invoke. These tools are registered with the `BrowserUse` instance during creation and are executed in the Python environment, with results communicated back to the agent via the stdio bridge. The `invokePython` function [src/server.ts:31-65]() handles the communication for these tools.

### `src/server.ts` (bu-pi-server)

The `src/server.ts` file implements a private, versioned stdio bridge. This server acts as an intermediary, receiving commands from the Python client via standard input and sending responses and events via standard output. It handles the serialization and deserialization of data, as well as the invocation of `BrowserUse` methods. The `dispatch` function [src/server.ts:93-196]() is the core of this bridge, routing incoming requests to the appropriate `BrowserUse` methods.

### `scripts/build-python.mjs` Packaging

The `scripts/build-python.mjs` script is responsible for packaging the necessary components for the Python client, including the `bu-pi-server` executable, ensuring that the Python client can correctly set up and communicate with the Node.js-based agent.

For details, see [Python Client and stdio Bridge](#2.4).
Sources: [src/server.ts:1-196]()

---

