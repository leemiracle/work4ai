<!-- source: DeepWiki mcp.deepwiki.com · repo openclaw/openclaw · extra page Exec & Background Processes · fetched 2026-10-27 -->

# Exec & Background Processes

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/cli/nodes.md](docs/cli/nodes.md)
- [docs/concepts/agent-loop.md](docs/concepts/agent-loop.md)
- [docs/gateway/pairing.md](docs/gateway/pairing.md)
- [extensions/codex/src/app-server/dynamic-tool-build-state.ts](extensions/codex/src/app-server/dynamic-tool-build-state.ts)
- [extensions/codex/src/app-server/dynamic-tool-build.test.ts](extensions/codex/src/app-server/dynamic-tool-build.test.ts)
- [extensions/codex/src/app-server/dynamic-tool-build.ts](extensions/codex/src/app-server/dynamic-tool-build.ts)
- [extensions/codex/src/app-server/event-projector-assistant.ts](extensions/codex/src/app-server/event-projector-assistant.ts)
- [extensions/codex/src/app-server/run-attempt-tool-setup.ts](extensions/codex/src/app-server/run-attempt-tool-setup.ts)
- [extensions/codex/src/app-server/shell-dynamic-tools.ts](extensions/codex/src/app-server/shell-dynamic-tools.ts)
- [extensions/codex/src/app-server/side-question.test.ts](extensions/codex/src/app-server/side-question.test.ts)
- [extensions/codex/src/app-server/side-question.ts](extensions/codex/src/app-server/side-question.ts)
- [extensions/copilot/src/attempt-config.ts](extensions/copilot/src/attempt-config.ts)
- [extensions/copilot/src/attempt-execution.ts](extensions/copilot/src/attempt-execution.ts)
- [extensions/copilot/src/attempt.test.ts](extensions/copilot/src/attempt.test.ts)
- [extensions/copilot/src/tool-bridge.test.ts](extensions/copilot/src/tool-bridge.test.ts)
- [extensions/copilot/src/tool-bridge.ts](extensions/copilot/src/tool-bridge.ts)
- [src/agents/bash-tools.exec-host-node-phases.test.ts](src/agents/bash-tools.exec-host-node-phases.test.ts)
- [src/agents/bash-tools.exec-host-node-phases.ts](src/agents/bash-tools.exec-host-node-phases.ts)
- [src/agents/bash-tools.exec-host-node.cancellation.test.ts](src/agents/bash-tools.exec-host-node.cancellation.test.ts)
- [src/agents/cli-runner/mcp-grant-context.test.ts](src/agents/cli-runner/mcp-grant-context.test.ts)
- [src/agents/cli-runner/mcp-grant-context.ts](src/agents/cli-runner/mcp-grant-context.ts)
- [src/agents/node-exec-availability.ts](src/agents/node-exec-availability.ts)
- [src/agents/tools/computer-tool.node-resolution.test.ts](src/agents/tools/computer-tool.node-resolution.test.ts)
- [src/agents/tools/terminal-tool.test.ts](src/agents/tools/terminal-tool.test.ts)
- [src/agents/tools/terminal-tool.ts](src/agents/tools/terminal-tool.ts)
- [src/auto-reply/reply/agent-runner-execution-timing.test.ts](src/auto-reply/reply/agent-runner-execution-timing.test.ts)
- [src/auto-reply/reply/agent-runner-trace.test.ts](src/auto-reply/reply/agent-runner-trace.test.ts)
- [src/auto-reply/reply/agent-runner-trace.ts](src/auto-reply/reply/agent-runner-trace.ts)
- [src/cron/isolated-agent/run.tools-allow.test.ts](src/cron/isolated-agent/run.tools-allow.test.ts)
- [src/gateway/mcp-grant-store.ts](src/gateway/mcp-grant-store.ts)
- [src/gateway/mcp-http.oauth-tools.test.ts](src/gateway/mcp-http.oauth-tools.test.ts)
- [src/gateway/mcp-http.runtime.test.ts](src/gateway/mcp-http.runtime.test.ts)
- [src/gateway/mcp-http.runtime.ts](src/gateway/mcp-http.runtime.ts)
- [src/gateway/mcp-http.test.ts](src/gateway/mcp-http.test.ts)
- [src/gateway/mcp-http.ts](src/gateway/mcp-http.ts)
- [src/gateway/server-active-work.test.ts](src/gateway/server-active-work.test.ts)
- [src/gateway/server-chat-progress-snapshot.ts](src/gateway/server-chat-progress-snapshot.ts)
- [src/gateway/server-chat-state.test.ts](src/gateway/server-chat-state.test.ts)
- [src/gateway/server-chat-state.ts](src/gateway/server-chat-state.ts)
- [src/gateway/server-chat.agent-events.test.ts](src/gateway/server-chat.agent-events.test.ts)
- [src/gateway/server-chat.ts](src/gateway/server-chat.ts)
- [src/gateway/server-runtime-subscriptions.test.ts](src/gateway/server-runtime-subscriptions.test.ts)
- [src/gateway/server-runtime-subscriptions.ts](src/gateway/server-runtime-subscriptions.ts)
- [src/gateway/server.sessions.archive-terminal.test.ts](src/gateway/server.sessions.archive-terminal.test.ts)
- [src/gateway/session-lifecycle-persistence-owner.test.ts](src/gateway/session-lifecycle-persistence-owner.test.ts)
- [src/gateway/session-lifecycle-persistence-owner.ts](src/gateway/session-lifecycle-persistence-owner.ts)
- [src/gateway/session-lifecycle-state.persistence.test.ts](src/gateway/session-lifecycle-state.persistence.test.ts)
- [src/gateway/session-lifecycle-state.test.ts](src/gateway/session-lifecycle-state.test.ts)
- [src/gateway/session-list-order.ts](src/gateway/session-list-order.ts)
- [src/gateway/session-utils-contracts.ts](src/gateway/session-utils-contracts.ts)
- [src/gateway/terminal/session-manager.eviction.test.ts](src/gateway/terminal/session-manager.eviction.test.ts)
- [src/gateway/terminal/session-manager.task-lifecycle.test.ts](src/gateway/terminal/session-manager.task-lifecycle.test.ts)
- [src/gateway/terminal/session-manager.test-helpers.ts](src/gateway/terminal/session-manager.test-helpers.ts)
- [src/gateway/terminal/session-manager.ts](src/gateway/terminal/session-manager.ts)
- [src/gateway/tool-resolution.exclude.test.ts](src/gateway/tool-resolution.exclude.test.ts)
- [src/gateway/tool-resolution.terminal.test.ts](src/gateway/tool-resolution.terminal.test.ts)
- [src/gateway/tool-resolution.ts](src/gateway/tool-resolution.ts)
- [src/plugin-sdk/agent-harness-tool-runtime.ts](src/plugin-sdk/agent-harness-tool-runtime.ts)
- [src/plugins/contracts/plugin-sdk-package-contract-guardrails.test.ts](src/plugins/contracts/plugin-sdk-package-contract-guardrails.test.ts)
- [src/shared/node-match.test.ts](src/shared/node-match.test.ts)
- [src/shared/node-match.ts](src/shared/node-match.ts)
- [src/tasks/task-registry-activity.ts](src/tasks/task-registry-activity.ts)
- [src/tasks/task-registry-lifecycle.ts](src/tasks/task-registry-lifecycle.ts)
- [src/tasks/task-registry.test.ts](src/tasks/task-registry.test.ts)
- [src/tasks/task-status-access.ts](src/tasks/task-status-access.ts)
- [ui/src/components/browser/browser-panel.styles.ts](ui/src/components/browser/browser-panel.styles.ts)
- [ui/src/components/terminal/terminal-session-picker.ts](ui/src/components/terminal/terminal-session-picker.ts)

</details>



This page provides a detailed technical overview of the execution and background process tools in OpenClaw. It explains the implementation of tool runners, shell execution on host nodes, process registries, session management, and output buffering, with a specific focus on the **Process Registry**, **Node Execution**, and **Tool Resolution** pipelines.

## Overview

OpenClaw’s execution system allows agents to interact with shell environments, model-generated scripts, and local filesystems. The system is split into three primary paradigms:

1.  **Foreground Execution**: Synchronous tool calls where the agent waits for a result before continuing the loop. This is managed by the `runEmbeddedPiAgent` lifecycle [src/gateway/server-chat.ts:16-16]().
2.  **Background Processes**: Long-running tasks, such as terminal sessions or backgrounded shell commands, tracked via the **Process Registry** [src/gateway/server-chat-state.ts:2-3]().
3.  **Node Execution**: Commands dispatched to remote paired devices (macOS, Linux, iOS, Android) via the `node.invoke` RPC [docs/cli/nodes.md:54-57]().

### Key Code Entities

| Component | Code Entity | Source File |
| :--- | :--- | :--- |
| Chat Run Registry | `ChatRunRegistry` | [src/gateway/server-chat-state.ts:160-160]() |
| Agent Event Handler | `createAgentEventHandler` | [src/gateway/server-chat.ts:139-141]() |
| Node Invoke Tool | `invokeNodeSystemRun` | [src/agents/bash-tools.exec-host-node-phases.ts:5-6]() |
| Gateway Tool Resolver | `resolveGatewayScopedTools` | [src/gateway/tool-resolution.ts:69-69]() |
| Task Registry | `TaskRecord` | [src/tasks/task-registry.test.ts:96-96]() |

Sources: [src/gateway/server-chat-state.ts:160-160](), [src/gateway/server-chat.ts:139-141](), [src/agents/bash-tools.exec-host-node-phases.ts:5-6](), [src/gateway/tool-resolution.ts:69-69](), [src/tasks/task-registry.test.ts:96-96]()

---

## Process Registry & Session Management

The Gateway maintains a `ChatRunRecordStore` to track active execution states, delta buffers for streaming output, and tool event recipients [src/gateway/server-chat-state.ts:126-130]().

### Execution State Flow
```mermaid
graph TD
    ["Gateway Server"] -- "registerChatRun" --> ["ChatRunRegistry"]
    ["ChatRunRegistry"] -- "createChatRunEntry" --> ["ChatRunRecord"]
    ["ChatRunRecord"] -- "registrations" --> ["Queue of Active Runs"]
    ["ChatRunRecord"] -- "buffer" --> ["Streaming Output Buffer"]
    ["ChatRunRecord"] -- "toolRecipient" --> ["Connected UI/Client IDs"]
    ["Agent Event"] -- "projectLiveAssistantBufferedText" --> ["ChatRunRecord.buffer"]
```

**Implementation Details:**
- **Monotonic Sequencing**: Every chat run is stamped with a `registeredSequence` to ensure that abort markers (which also use this sequence) can correctly suppress stale events even if they arrive out of order [src/gateway/server-chat-state.ts:41-46]().
- **Abort Markers**: The `isChatAbortMarkerCurrent` function checks the sequence to determine if a specific run has been cancelled [src/gateway/server-chat-state.ts:63-71]().
- **Output Buffering**: Assistant text and thinking blocks are buffered in `ChatRunAgentTextState` before being projected to the UI [src/gateway/server-chat-state.ts:86-89]().
- **Heartbeat Suppression**: Background "heartbeat" runs (used for maintenance) have their output suppressed from interactive chat surfaces via `shouldHideHeartbeatChatOutput` [src/gateway/server-chat.ts:164-165]().

Sources: [src/gateway/server-chat-state.ts:126-130](), [src/gateway/server-chat-state.ts:41-46](), [src/gateway/server-chat-state.ts:63-71](), [src/gateway/server-chat-state.ts:86-89](), [src/gateway/server-chat.ts:164-165]()

---

## Node Execution (Remote Processes)

OpenClaw can offload execution to paired "Nodes." This is primarily used for running shell commands on a user's local machine or a specific remote server via `system.run` [docs/cli/nodes.md:68-68]().

### Node Dispatch Pipeline
```mermaid
graph TD
    ["Agent Tool: exec"] -- "host=node" --> ["resolveNodeExecutionTarget"]
    ["resolveNodeExecutionTarget"] -- "node.list" --> ["Gateway Node Registry"]
    ["Gateway Node Registry"] -- "Filtered Nodes" --> ["Selected Node ID"]
    ["Selected Node ID"] -- "dispatchNodeSystemRun" --> ["node.invoke(system.run)"]
    ["node.invoke"] -- "WebSocket" --> ["Remote OpenClaw Node"]
    ["Remote OpenClaw Node"] -- "Child Process" --> ["OS Shell"]
```

**Key Implementation Details:**
- **Target Resolution**: `resolveNodeExecutionTarget` filters the connected nodes based on capabilities. If multiple nodes support `system.run`, the system requires an explicit `nodeId` to disambiguate [src/agents/bash-tools.exec-host-node-phases.ts:122-146]().
- **Failure Classification**: Errors during remote execution are classified by `invokeNodeSystemRun`. Failures are marked as `retrySafe: true` only if the system can prove the command was never dispatched (e.g., `NOT_CONNECTED` pre-dispatch) [src/agents/bash-tools.exec-host-node-phases.test.ts:53-70]().
- **Outcome Unknown**: If a connection drops *after* dispatch, the outcome is marked as `outcome-unknown`, and the system provides a multiline command followup for the agent to verify state [src/agents/bash-tools.exec-host-node-phases.test.ts:103-119]().

Sources: [docs/cli/nodes.md:68-68](), [src/agents/bash-tools.exec-host-node-phases.ts:122-146](), [src/agents/bash-tools.exec-host-node-phases.test.ts:53-70](), [src/agents/bash-tools.exec-host-node-phases.test.ts:103-119]()

---

## Tool Resolution & Policy

Before an agent can execute a process, the tools must pass through the `resolveGatewayScopedTools` pipeline [src/gateway/tool-resolution.ts:69-69]().

- **Policy Pipeline**: Tools are filtered through `applyToolPolicyPipeline`, which checks global, agent, and profile-level allowlists/denylists [src/gateway/tool-resolution.ts:29-31]().
- **Surface Scoping**: The system distinguishes between `http` (external API) and `loopback` (internal agent loop) surfaces. Dangerous tools are often excluded from the `http` surface by default [src/gateway/tool-resolution.ts:59-61]().
- **Owner-Only Restrictions**: Certain "Ring Zero" tools are restricted to the Gateway owner via `GATEWAY_OWNER_ONLY_CORE_TOOLS` [src/gateway/tool-resolution.ts:60-61]().
- **Codex Dynamic Tools**: For the Codex app-server, tools are dynamically projected based on the session's sandbox policy. If native tool surfaces are disabled, shell tools like `exec` and `process` are explicitly filtered out [extensions/codex/src/app-server/dynamic-tool-build.ts:83-91]().

Sources: [src/gateway/tool-resolution.ts:69-69](), [src/gateway/tool-resolution.ts:29-31](), [src/gateway/tool-resolution.ts:59-61](), [extensions/codex/src/app-server/dynamic-tool-build.ts:83-91]()

---

## Background Task Registry

For long-running automations and cron jobs, OpenClaw uses the `TaskRegistry` [src/tasks/task-registry.test.ts:1-1]().

- **Lifecycle Tracking**: Tasks move through states: `upserted` -> `running` -> `terminal` (success/failure/lost) [src/tasks/task-registry.test.ts:182-190]().
- **Persistence**: Task records are stored in the `OpenClawStateKyselyDatabase` and can be reloaded after a gateway restart [src/tasks/task-registry.test.ts:43-44]().
- **Delivery**: Terminal updates and progress increments are delivered to subscribers (e.g., Discord, Slack, or WebChat) via `maybeDeliverTaskTerminalUpdate` [src/tasks/task-registry.test.ts:70-70]().

Sources: [src/tasks/task-registry.test.ts:1-1](), [src/tasks/task-registry.test.ts:182-190](), [src/tasks/task-registry.test.ts:43-44](), [src/tasks/task-registry.test.ts:70-70]()

---

