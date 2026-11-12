<!-- source: DeepWiki mcp.deepwiki.com · repo openai/codex · page 3 Core Agent System (codex-core) · fetched 2026-10-26 -->

# Core Agent System (codex-core)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [codex-rs/app-server/src/bespoke_event_handling.rs](codex-rs/app-server/src/bespoke_event_handling.rs)
- [codex-rs/core/src/codex_delegate.rs](codex-rs/core/src/codex_delegate.rs)
- [codex-rs/core/src/codex_delegate_tests.rs](codex-rs/core/src/codex_delegate_tests.rs)
- [codex-rs/core/src/codex_thread.rs](codex-rs/core/src/codex_thread.rs)
- [codex-rs/core/src/compact.rs](codex-rs/core/src/compact.rs)
- [codex-rs/core/src/compact_remote_v2.rs](codex-rs/core/src/compact_remote_v2.rs)
- [codex-rs/core/src/compact_remote_v2_attempt.rs](codex-rs/core/src/compact_remote_v2_attempt.rs)
- [codex-rs/core/src/compact_tests.rs](codex-rs/core/src/compact_tests.rs)
- [codex-rs/core/src/environment_selection.rs](codex-rs/core/src/environment_selection.rs)
- [codex-rs/core/src/session/environment.rs](codex-rs/core/src/session/environment.rs)
- [codex-rs/core/src/session/handlers.rs](codex-rs/core/src/session/handlers.rs)
- [codex-rs/core/src/session/mod.rs](codex-rs/core/src/session/mod.rs)
- [codex-rs/core/src/session/session.rs](codex-rs/core/src/session/session.rs)
- [codex-rs/core/src/session/tests.rs](codex-rs/core/src/session/tests.rs)
- [codex-rs/core/src/session/tests/guardian_tests.rs](codex-rs/core/src/session/tests/guardian_tests.rs)
- [codex-rs/core/src/session/turn.rs](codex-rs/core/src/session/turn.rs)
- [codex-rs/core/src/session/turn_context.rs](codex-rs/core/src/session/turn_context.rs)
- [codex-rs/core/src/state/mod.rs](codex-rs/core/src/state/mod.rs)
- [codex-rs/core/src/state/turn.rs](codex-rs/core/src/state/turn.rs)
- [codex-rs/core/src/tasks/mod.rs](codex-rs/core/src/tasks/mod.rs)
- [codex-rs/core/src/thread_manager.rs](codex-rs/core/src/thread_manager.rs)
- [codex-rs/core/src/thread_manager_tests.rs](codex-rs/core/src/thread_manager_tests.rs)
- [codex-rs/core/tests/common/test_codex.rs](codex-rs/core/tests/common/test_codex.rs)
- [codex-rs/core/tests/suite/compact.rs](codex-rs/core/tests/suite/compact.rs)
- [codex-rs/core/tests/suite/compact_remote.rs](codex-rs/core/tests/suite/compact_remote.rs)
- [codex-rs/core/tests/suite/mod.rs](codex-rs/core/tests/suite/mod.rs)
- [codex-rs/core/tests/suite/remote_env.rs](codex-rs/core/tests/suite/remote_env.rs)
- [codex-rs/protocol/src/environment.rs](codex-rs/protocol/src/environment.rs)
- [codex-rs/protocol/src/protocol.rs](codex-rs/protocol/src/protocol.rs)

</details>



The Core Agent System is the central orchestration layer of Codex, responsible for managing conversation turns, coordinating model API interactions, and maintaining session state. This document provides a high-level overview of the core engine that drives the Codex AI agent, focusing on the key abstractions, execution patterns, and relationships between subsystems.

For details on user interfaces interacting with this system, see [User Interfaces](#4). For information on tool execution and approval workflows, see [Tool System](#5). For configuration and permissions management, see [Sandbox and Approval Policies](#2.4).

## Architecture Overview

The Core Agent System implements a **Submission Queue (SQ) / Event Queue (EQ)** asynchronous communication pattern between frontends and the agent, as defined in the protocol crate [codex-rs/protocol/src/protocol.rs:1-4]().

Users issue requests such as prompts or approvals by submitting operations (`Op`) to the `CodexThread` interface. The agent processes these via internal `Session` objects and emits events (`EventMsg`) back to the thread, which streams them to the UI.

```mermaid
graph TB
    subgraph "Natural Language Space (Client)"
        UI["User Interface"] -->|submit(Op)| CodexThread["CodexThread"]
    end

    subgraph "Code Entity Space (codex-core)"
        CodexThread -->|"submission channel"| Session["Session"]
        ThreadManager["ThreadManager"] -->|spawn()| Session
        Session -->|"control messages"| AgentControl["AgentControl"]
    end

    subgraph "Model Communication"
        Session -->|"request"| ModelClientSession["ModelClientSession"]
        ModelClientSession -->|"response stream"| ModelAPI["Model API (OpenAI, LM Studio, Ollama)"]
    end

    ModelAPI -->|"ResponseEvent"| Session
    Session -->|"event channel"| CodexThread
    CodexThread -->|rx_event| UI

    style CodexThread stroke-dasharray: 5 5
    style Session stroke-width: 2px
```

This diagram highlights the core flow: user commands enter through `CodexThread` as ops, sessions execute turns interacting with model clients, and events stream back for UI consumption.

**Sources:**  
[codex-rs/protocol/src/protocol.rs:1-4](),  
[codex-rs/core/src/session/mod.rs:59-60](),  
[codex-rs/core/src/codex_thread.rs:1-164](),  
[codex-rs/core/src/thread_manager.rs:1-167]()

### Key Components Overview

| Component               | Role                                                                                | Location (lines)                     |
|-------------------------|-------------------------------------------------------------------------------------|------------------------------------|
| `Op`                    | Submission queue entries for user actions (prompts, approvals, interrupts).         | [codex-rs/protocol/src/protocol.rs:2325-2350]() |
| `EventMsg`              | Event queue entries for agent notifications (text, tool start/stop, errors).        | [codex-rs/protocol/src/protocol.rs:2075-2120]() |
| `Session`               | Core orchestrator managing turns, state, tools, and task lifecycle.                 | [codex-rs/core/src/session/session.rs:60-101]()|
| `TurnContext`           | Per-turn data such as environment, model settings, and permissions.                 | [codex-rs/core/src/session/turn_context.rs:67-77]() |
| `SessionTask`           | Trait for async tasks performing session work (Regular turn, Review, Compaction).   | [codex-rs/core/src/tasks/mod.rs:181-196]()    |
| `ThreadManager`         | Oversees threads, handling thread lifecycle, forks, and sub-agent sessions.         | [codex-rs/core/src/thread_manager.rs:1-167]()  |
| `AgentControl`          | Support for multi-agent coordination and inter-agent messaging.                     | [codex-rs/core/src/agent/api.rs:1-10]()      |
| `SharedModelProvider`    | Handles communication with language model providers via streaming APIs.            | [codex-rs/core/src/session/session.rs:105]()     |

**Sources:**  
[codex-rs/core/src/session/session.rs:60-101](),  
[codex-rs/core/src/tasks/mod.rs:181-196](),  
[codex-rs/core/src/thread_manager.rs:1-167](),  
[codex-rs/core/src/session/turn_context.rs:67-77](),  
[codex-rs/core/src/agent/api.rs:1-10](),  
[codex-rs/core/src/session/session.rs:105]()

## Session Lifecycle

At the heart of Codex execution is the `Session` entity, representing a single agent's stateful context tied to a conversation thread. The session manages one active task at a time, such as processing user input or running a review.

```mermaid
stateDiagram-v2
    [*] --> ThreadManager_Start_Thread: "ThreadManager::start_thread()"
    ThreadManager_Start_Thread --> Session_Spawn: "Session::spawn()"
    Session_Spawn --> Session_Idle: "Begin session loop"
    Session_Idle --> Session_Receive_User_Op: "Op::UserInput received"
    Session_Receive_User_Op --> Session_Run_Task: "SessionTask::run()"
    Session_Run_Task --> ToolExec: "ToolRouter::call()"
    ToolExec --> Session_Run_Task: "DynamicToolResponse"
    Session_Run_Task --> Session_Idle: "TurnCompleteEvent / TaskFinished"
    Session_Idle --> Session_Terminated: "Cancelled (CancellationToken)"
    Session_Terminated --> [*]
```

- The `ThreadManager` starts or resumes threads, which wrap a `Session` [codex-rs/core/src/thread_manager.rs:32-34]().
- The `Session` listens on a submission queue and drives turn execution tasks implementing the `SessionTask` trait [codex-rs/core/src/session/session.rs:94]().
- Each `SessionTask` instance ties to a turn or workflow (regular chat turn, compaction, review).
- During turns, `Session` routes tool calls via `ToolRouter`, handles model streaming, and emits events.
- The session serializes state changes and observes cancellation tokens allowing user interrupts.

This lifecycle ensures resource-efficient serialization of agent work and responsiveness to user requests [codex-rs/core/src/session/session.rs:60-101]().

### Multi-Agent Coordination

Codex supports multi-agent setups where a main agent may spawn specialized sub-agents (e.g., review, guardian). Key facets include:

- **Multi-Agent Versions:** Codex supports versioned multi-agent protocols (e.g., `MultiAgentVersion::V2`) that influence agent interactions, interruption signals, and turn rendering [codex-rs/protocol/src/protocol.rs:150-151]().
- **Inter-Agent Communication:** Agents communicate via structured messages (`InterAgentCommunication`) mediated by `AgentControl`, enabling messages and requests to cross agent boundaries [codex-rs/protocol/src/protocol.rs:147-148]().
- **Thread Graph Persistence:** The `codex_agent_graph_store` crate maintains parent/child thread relationships to archive session lineage and enable UI navigation and debugging [codex-rs/core/src/thread_manager.rs:40-41]().

These multi-agent constructs enable advanced workflows, such as background checks and layered review processes, enhancing Codex’s safety and extensibility.

**Sources:**  
[codex-rs/protocol/src/protocol.rs:150-151](),  
[codex-rs/protocol/src/protocol.rs:147-148](),  
[codex-rs/core/src/thread_manager.rs:40-41]()

## Model Client and API Communication

The Core Agent System communicates with language models via the `SharedModelProvider` abstraction, managing streaming request/responses with retry logic and local model provider integrations.

- The `Session`'s `provider` field holds the `SharedModelProvider` [codex-rs/core/src/session/session.rs:105]() for configuration.
- The `SharedModelsManager` handles model discovery, caching, TTL-based refresh, and metadata overrides to reflect dynamic configuration [codex-rs/core/src/session/mod.rs:98-99]().
- Model clients connect to different backends like OpenAI, LM Studio or Ollama via pluggable session clients with either HTTP or websocket transports [codex-rs/core/src/codex_thread.rs:1-164]().
- Specialized support covers delta events for reasoning content and section breaks, supporting structured and interactive assistant outputs.

This layered client abstraction supports modular addition of new model providers and transport mechanisms.

**Sources:**  
[codex-rs/core/src/session/session.rs:105](),  
[codex-rs/core/src/session/mod.rs:98-99](),  
[codex-rs/core/src/codex_thread.rs:1-164]()

## Turn Execution and Prompt Construction

The agent executes turns asynchronously, transforming user input into model calls and processing streamed outputs.

### Turn Execution Flow

1.  **Turn Context Setup:** Each turn initializes a `TurnContext` instance capturing the model, environments, developer and enforcement instructions, and permissions [codex-rs/core/src/session/turn_context.rs:67-77]().
2.  **Hooks Execution:** Pre-turn and pre-tool-use hooks run in the hooks engine to support telemetry, input validation, or modifications.
3.  **Auto-Compaction:** Token budget limits trigger inline compaction tasks to reduce history token count before sending prompts [codex-rs/core/src/compact.rs:118-152]().
4.  **Tool Routing & Execution:** If the model output requests tool operations, `ToolRouter` dispatches to appropriate handlers asynchronously [codex-rs/core/src/session/turn.rs:57]().

### State Tracking and Persistence

- The session state is incrementally updated via streaming event flow, providing fine-grained turn progress.
- Events propagate through `ResponseEvent → EventMsg` translation layers, synchronizing with the session for persistence and UI updates [codex-rs/app-server/src/bespoke_event_handling.rs:104]().
- Rollout persistence logs full turn event histories for recovery and replay [codex-rs/core/src/codex_thread.rs:22]().
- Token usage per turn is tracked for budgeting and analytics [codex-rs/core/src/tasks/mod.rs:55]().

These layers enable responsive, interruptible turn execution while safeguarding token budgets and state integrity.

**Sources:**  
[codex-rs/core/src/session/turn_context.rs:67-77](),  
[codex-rs/core/src/compact.rs:118-152](),  
[codex-rs/core/src/session/turn.rs:57](),  
[codex-rs/app-server/src/bespoke_event_handling.rs:104](),  
[codex-rs/core/src/codex_thread.rs:22](),  
[codex-rs/core/src/tasks/mod.rs:55]()

## Core Subsystems and Related Documentation

The Core Agent System spans multiple specialized subsystems. These are documented in dedicated child pages, linked below:

-   **[Codex Interface and Session Lifecycle](#3.1)**: Describes the `CodexThread` API implementing submission and event processing loops, session spawn/resume/fork semantics, and thread lifecycle management.
-   **[Model Client and API Communication](#3.2)**: Details the `ModelClient` abstraction, differences between session-scoped and turn-scoped clients, websocket vs HTTP transports, retry strategies, and integrations with LM Studio/Ollama providers.
-   **[Turn Execution and Prompt Construction](#3.3)**: Covers `TurnContext` lifecycle, prompt construction with cached prefixes, override patterns, authentication headers, and the `prompts` crate which provides template systems for compact, review, goals, permissions, and realtime prompts.
-   **[Event Processing and State Management](#3.4)**: Explains the translation of `ResponseEvent` stream items into agent `EventMsg`s, event emission, and how session state is synchronized and persisted.
-   **[Conversation History Management](#3.5)**: Details the `ContextManager`, storage and normalization of `ResponseItem`s, token estimation, and the history lifecycle. Includes child pages for compaction and rollout persistence.
-   **[Thread Management and Multi-Agent](#3.6)**: Describes the `ThreadManager`, handling primary and sub-agent threads (review, guardian, custom), thread switching, `ThreadEventStore` usage, and use of the `agent-graph-store` crate to persist thread topology.
-   **[Session Tasks and Turn State](#3.7)**: Documents the `SessionTask` trait, asynchronous task lifecycles including spawn and abort operations, and token usage tracking within `TurnState`.
-   **[Models Manager](#3.8)**: Covers model discovery, remote fetch, caching with TTL, and `ModelInfo` resolution including overrides. Explains the `models-manager` crate and collaboration mode presets.
-   **[Memories System](#3.9)**: Describes the multi-phase conversation memory extraction and consolidation system, storage, and memory injection at startup. Covers `memories/write`, `memories/read`, and the read-only `memories/mcp` server crates.
-   **[Realtime Conversation](#3.10)**: Details realtime interaction APIs (WebSocket, WebRTC) for low-latency audio and text, session lifecycle management, protocol versions, and native macOS WebRTC support through the `realtime-webrtc` crate.
-   **[Hooks System](#3.11)**: Documents the Claude-style hooks engine, supporting hook event types like `PreToolUse`, `PostToolUse`, session start/stop, and prompt submit. Explains `HooksConfig`, event discovery, dispatch pipeline, and abort semantics.
-   **[Network Proxy](#3.12)**: Explains the sandboxed network proxy enforcing HTTP/SOCKS5 policies, allow/deny configuration, read-only limited mode, MITM capability, and integration with permission profiles. Also covers the `codex-responses-api-proxy` binary for injecting privileged API keys.
-   **[Goal Extension and State Runtime](#3.13)**: Documents the goal tracking framework with objectives, token budgets, status management for threads, and the `codex-state` crate’s SQLite-backed runtime managing goals, logs, memories, jobs, and remote control enrollment.

---

This page is intended to provide engineers with a high-level understanding of the core agent engine foundation. For deep technical detail, please refer to each subsystem’s dedicated child page.

**Sources:**  
[codex-rs/protocol/src/protocol.rs:1-155](),  
[codex-rs/core/src/session/session.rs:60-101](),  
[codex-rs/core/src/tasks/mod.rs:181-196](),  
[codex-rs/core/src/session/turn_context.rs:67-77](),  
[codex-rs/core/src/thread_manager.rs:1-167](),  
[codex-rs/core/src/codex_thread.rs:1-164](),
[codex-rs/core/src/session/mod.rs:1-155](),
[codex-rs/core/src/session/turn.rs:1-151]()

---

