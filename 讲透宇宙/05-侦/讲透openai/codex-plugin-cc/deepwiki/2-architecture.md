<!-- source: DeepWiki mcp.deepwiki.com · repo openai/codex-plugin-cc · page 2 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [plugins/codex/scripts/codex-companion.mjs](plugins/codex/scripts/codex-companion.mjs)
- [plugins/codex/scripts/lib/app-server.mjs](plugins/codex/scripts/lib/app-server.mjs)

</details>



This page provides a high-level overview of the `codex-plugin-cc` system architecture. The plugin is designed as a layered system that bridges the gap between the Claude Code environment and the OpenAI Codex CLI, providing robust job tracking, shared runtime access, and automated review gates.

## System Overview

The architecture is centered around a companion CLI script that manages all interactions with the Codex ecosystem. Because Claude Code may execute multiple commands or hooks in parallel or sequence, the system uses a **Broker** pattern to ensure stable, multiplexed access to a single Codex `app-server` instance.

### High-Level Component Diagram

This diagram illustrates how the system components interact, moving from the user-facing slash commands to the underlying Codex runtime.

"System Components & Data Flow"
```mermaid
graph TD
    subgraph "Claude_Code_Environment"
        [CC_Session]
        [Hooks_hooks.json]
    end

    subgraph "Codex_Plugin_Layer"
        [codex-companion.mjs_Dispatcher]
        [app-server-broker.mjs_Multiplexer]
        [state.mjs_Persistence]
    end

    subgraph "External_Runtime"
        [Codex_app-server_JSON-RPC]
        [Codex_CLI_Binary]
    end

    [CC_Session] -- "executes" --> [codex-companion.mjs_Dispatcher]
    [Hooks_hooks.json] -- "triggers" --> [codex-companion.mjs_Dispatcher]
    [codex-companion.mjs_Dispatcher] -- "requests" --> [app-server-broker.mjs_Multiplexer]
    [app-server-broker.mjs_Multiplexer] -- "JSON-RPC_over_IPC" --> [Codex_app-server_JSON-RPC]
    [Codex_app-server_JSON-RPC] -- "spawns" --> [Codex_CLI_Binary]
    [codex-companion.mjs_Dispatcher] -- "reads/writes" --> [state.mjs_Persistence]
```
Sources: [plugins/codex/scripts/codex-companion.mjs:1-87](), [plugins/codex/scripts/lib/app-server.mjs:183-196](), [plugins/codex/scripts/session-lifecycle-hook.mjs:1-20]()

---

## Core Subsystems

### 1. Codex Companion Script
The `codex-companion.mjs` script is the central entry point for all plugin operations. It acts as a dispatcher, parsing arguments via `parseCommandInput` [plugins/codex/scripts/codex-companion.mjs:141-149]() and routing them to specific logic for setup, code reviews, or task delegation. It handles both foreground execution (where the user waits for a result) and background execution (where a job ID is returned immediately) by utilizing `runTrackedJob` [plugins/codex/scripts/lib/tracked-jobs.mjs:52-54](). The script also includes utility functions like `outputResult` [plugins/codex/scripts/codex-companion.mjs:91-96]() for formatting output and `normalizeRequestedModel` [plugins/codex/scripts/codex-companion.mjs:103-112]() for handling model aliases.

For details, see [Codex Companion Script](#2.1).

Sources: [plugins/codex/scripts/codex-companion.mjs:75-87](), [plugins/codex/scripts/codex-companion.mjs:215-230](), [plugins/codex/scripts/codex-companion.mjs:91-96](), [plugins/codex/scripts/codex-companion.mjs:103-112]()

### 2. App-Server Client & Broker
To avoid the overhead of repeatedly spawning the Codex CLI and to maintain session state (like conversation history), the plugin uses a broker mechanism. `AppServerClientBase` [plugins/codex/scripts/lib/app-server.mjs:57-181]() provides the foundation for JSON-RPC communication. The system supports direct spawning via `SpawnedCodexAppServerClient` [plugins/codex/scripts/lib/app-server.mjs:183-230]() or connecting to a persistent multiplexer. This ensures that only one "turn" is active at a time, preventing race conditions in the Codex runtime via `interruptAppServerTurn` [plugins/codex/scripts/lib/codex.mjs:18-18](). The client also defines default information and capabilities for the plugin, such as `DEFAULT_CLIENT_INFO` [plugins/codex/scripts/lib/app-server.mjs:26-30]() and `DEFAULT_CAPABILITIES` [plugins/codex/scripts/lib/app-server.mjs:33-42]().

For details, see [App-Server Client & Broker](#2.2).

"Natural Language to Code Entity: Broker & Protocol"
```mermaid
graph LR
    subgraph "Natural_Language_Space"
        [REQ_Run_a_review]
        [INT_Stop_current_task]
    end

    subgraph "Code_Entity_Space"
        [codex-companion.mjs]
        [AppServerClientBase]
        [interruptAppServerTurn]
        [request]
    end

    [REQ_Run_a_review] --> [codex-companion.mjs]
    [codex-companion.mjs] -- "request()" --> [request]
    [request] -- "JSON-RPC" --> [AppServerClientBase]
    [INT_Stop_current_task] --> [codex-companion.mjs]
    [codex-companion.mjs] -- "interruptAppServerTurn()" --> [interruptAppServerTurn]
```
Sources: [plugins/codex/scripts/lib/app-server.mjs:86-98](), [plugins/codex/scripts/codex-companion.mjs:10-23](), [plugins/codex/scripts/lib/app-server.mjs:26-30](), [plugins/codex/scripts/lib/app-server.mjs:33-42]()

### 3. Job Tracking & State Management
The system includes a persistence layer in `state.mjs` and `tracked-jobs.mjs`. Every significant action is assigned a `jobId` generated by `generateJobId` [plugins/codex/scripts/lib/state.mjs:30-30](). The state of these jobs, including logs, progress, and final results, is stored in a local state directory. This allows users to query `/codex:status` via `buildStatusSnapshot` [plugins/codex/scripts/lib/job-control.mjs:213-213]() or retrieve results later with `/codex:result` using `resolveResultJob` [plugins/codex/scripts/lib/job-control.mjs:42-42](). The `tracked-jobs.mjs` module also provides functions like `createJobLogFile` [plugins/codex/scripts/lib/tracked-jobs.mjs:47-47]() and `createJobProgressUpdater` [plugins/codex/scripts/lib/tracked-jobs.mjs:48-48]() for managing job output.

For details, see [Job Tracking & State Management](#2.3).

"Natural Language to Code Entity: Job Lifecycle"
```mermaid
graph TD
    subgraph "Natural_Language_Space"
        [START_Start_background_task]
        [POLL_Is_it_done_yet]
    end

    subgraph "Code_Entity_Space"
        [runTrackedJob]
        [upsertJob]
        [resolveStateFile]
        [writeJobFile]
        [buildStatusSnapshot]
    end

    [START_Start_background_task] --> [runTrackedJob]
    [runTrackedJob] --> [upsertJob]
    [upsertJob] --> [resolveStateFile]
    [resolveStateFile] --> [writeJobFile]
    [POLL_Is_it_done_yet] --> [buildStatusSnapshot]
    [buildStatusSnapshot] -- "reads" --> [writeJobFile]
```
Sources: [plugins/codex/scripts/lib/state.mjs:48-48](), [plugins/codex/scripts/lib/tracked-jobs.mjs:52-54](), [plugins/codex/scripts/lib/job-control.mjs:213-223](), [plugins/codex/scripts/lib/tracked-jobs.mjs:47-48]()

### 4. Claude Code Hook Integration
The plugin integrates with Claude Code's lifecycle via hooks.
- **SessionStart**: Triggers `session-lifecycle-hook.mjs` to prepare the Codex runtime and set environment variables like `SESSION_ID_ENV` [plugins/codex/scripts/session-lifecycle-hook.mjs:77-81]().
- **SessionEnd**: Triggers `session-lifecycle-hook.mjs` to clean up resources, including calling `teardownBrokerSession` [plugins/codex/scripts/session-lifecycle-hook.mjs:105-112]() and `cleanupSessionJobs` [plugins/codex/scripts/session-lifecycle-hook.mjs:42-75]().
- **Stop**: Can trigger a "Review Gate" which prevents Claude from exiting if there are unreviewed changes.

For details, see [Claude Code Hook Integration](#2.4).

Sources: [plugins/codex/scripts/session-lifecycle-hook.mjs:77-114](), [plugins/codex/scripts/lib/broker-lifecycle.mjs:14-15]()

---

## Component Relationship Table

| Component | Responsibility | Primary Files |
| :--- | :--- | :--- |
| **Dispatcher** | CLI argument parsing and subcommand delegation. | `codex-companion.mjs` [plugins/codex/scripts/codex-companion.mjs:1-9]() |
| **Broker** | Lifecycle management for the shared Codex `app-server`. | `lib/broker-lifecycle.mjs` [plugins/codex/scripts/lib/broker-lifecycle.mjs:1-15]() |
| **Client** | JSON-RPC communication protocol implementation. | `lib/app-server.mjs` [plugins/codex/scripts/lib/app-server.mjs:57-69]() |
| **State** | Persistence of job metadata and logs. | `lib/state.mjs` [plugins/codex/scripts/lib/state.mjs:1-36](), `lib/tracked-jobs.mjs` [plugins/codex/scripts/lib/tracked-jobs.mjs:1-13]() |
| **Control** | Logic for querying and enriching job status. | `lib/job-control.mjs` [plugins/codex/scripts/lib/job-control.mjs:1-13]() |

Sources: [plugins/codex/scripts/codex-companion.mjs:1-65](), [plugins/codex/scripts/lib/app-server.mjs:57-70](), [plugins/codex/scripts/lib/state.mjs:1-36](), [plugins/codex/scripts/lib/tracked-jobs.mjs:1-13](), [plugins/codex/scripts/lib/job-control.mjs:1-13]()

---

