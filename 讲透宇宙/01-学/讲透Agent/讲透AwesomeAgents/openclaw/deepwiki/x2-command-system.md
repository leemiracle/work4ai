<!-- source: DeepWiki mcp.deepwiki.com · repo openclaw/openclaw · extra page Command System · fetched 2026-10-26 -->

# Command System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/concepts/queue.md](docs/concepts/queue.md)
- [extensions/active-memory/transcript-watch.ts](extensions/active-memory/transcript-watch.ts)
- [extensions/copilot/harness.ts](extensions/copilot/harness.ts)
- [extensions/qa-lab/src/suite-runtime-agent-process.ts](extensions/qa-lab/src/suite-runtime-agent-process.ts)
- [extensions/telegram/src/bot-message-dispatch.preview-hook-safety.test.ts](extensions/telegram/src/bot-message-dispatch.preview-hook-safety.test.ts)
- [packages/ai/src/providers/clean-for-gemini.ts](packages/ai/src/providers/clean-for-gemini.ts)
- [qa/scenarios/memory/active-memory-cold-first-turn-trigger-recall.yaml](qa/scenarios/memory/active-memory-cold-first-turn-trigger-recall.yaml)
- [qa/scenarios/memory/active-memory-preprompt-recall.yaml](qa/scenarios/memory/active-memory-preprompt-recall.yaml)
- [qa/scenarios/scheduling/heartbeat-inbound-metadata.yaml](qa/scenarios/scheduling/heartbeat-inbound-metadata.yaml)
- [src/agents/command/attempt-execution.cli.test.ts](src/agents/command/attempt-execution.cli.test.ts)
- [src/agents/command/attempt-execution.ts](src/agents/command/attempt-execution.ts)
- [src/agents/command/compaction-accounting.ts](src/agents/command/compaction-accounting.ts)
- [src/agents/command/run-embedded-attempt.ts](src/agents/command/run-embedded-attempt.ts)
- [src/agents/delegation-capability.test.ts](src/agents/delegation-capability.test.ts)
- [src/agents/delegation-capability.ts](src/agents/delegation-capability.ts)
- [src/agents/embedded-agent-runner/run.overflow-compaction.loop.test.ts](src/agents/embedded-agent-runner/run.overflow-compaction.loop.test.ts)
- [src/agents/embedded-agent-runner/run.recovery-cancellation.test-support.ts](src/agents/embedded-agent-runner/run.recovery-cancellation.test-support.ts)
- [src/agents/embedded-agent-runner/run/internal-params.ts](src/agents/embedded-agent-runner/run/internal-params.ts)
- [src/agents/embedded-agent-runner/run/params.ts](src/agents/embedded-agent-runner/run/params.ts)
- [src/agents/embedded-agent-runner/run/run-attempt-dispatch.ts](src/agents/embedded-agent-runner/run/run-attempt-dispatch.ts)
- [src/agents/embedded-agent-runner/run/runtime-preparation.ts](src/agents/embedded-agent-runner/run/runtime-preparation.ts)
- [src/agents/embedded-agent-subscribe.handlers.messages.update-commentary.test.ts](src/agents/embedded-agent-subscribe.handlers.messages.update-commentary.test.ts)
- [src/agents/embedded-agent-subscribe.raw-stream.test.ts](src/agents/embedded-agent-subscribe.raw-stream.test.ts)
- [src/agents/embedded-agent-subscribe.raw-stream.ts](src/agents/embedded-agent-subscribe.raw-stream.ts)
- [src/agents/embedded-agent-subscribe.tool-text-diagnostics.ts](src/agents/embedded-agent-subscribe.tool-text-diagnostics.ts)
- [src/agents/harness/user-input-bridge.ts](src/agents/harness/user-input-bridge.ts)
- [src/agents/main-session-recovery/main-session-recovery-admission.ts](src/agents/main-session-recovery/main-session-recovery-admission.ts)
- [src/agents/main-session-recovery/main-session-restart-recovery-runtime.ts](src/agents/main-session-recovery/main-session-restart-recovery-runtime.ts)
- [src/agents/session-placement-admission.test.ts](src/agents/session-placement-admission.test.ts)
- [src/agents/session-placement-admission.ts](src/agents/session-placement-admission.ts)
- [src/agents/subagents/registry/subagent-registry-cleanup.test.ts](src/agents/subagents/registry/subagent-registry-cleanup.test.ts)
- [src/agents/subagents/registry/subagent-registry-cleanup.ts](src/agents/subagents/registry/subagent-registry-cleanup.ts)
- [src/agents/subagents/spawn/acp-spawn-parent-stream.ts](src/agents/subagents/spawn/acp-spawn-parent-stream.ts)
- [src/agents/tools/sessions-tool.self-archive.test.ts](src/agents/tools/sessions-tool.self-archive.test.ts)
- [src/auto-reply/dispatch.delivery-order.test.ts](src/auto-reply/dispatch.delivery-order.test.ts)
- [src/auto-reply/dispatch.ts](src/auto-reply/dispatch.ts)
- [src/auto-reply/model.ts](src/auto-reply/model.ts)
- [src/auto-reply/reply-payload.ts](src/auto-reply/reply-payload.ts)
- [src/auto-reply/reply.directive.parse.test.ts](src/auto-reply/reply.directive.parse.test.ts)
- [src/auto-reply/reply/acp-projector.test.ts](src/auto-reply/reply/acp-projector.test.ts)
- [src/auto-reply/reply/acp-projector.ts](src/auto-reply/reply/acp-projector.ts)
- [src/auto-reply/reply/agent-event-bridge.test.ts](src/auto-reply/reply/agent-event-bridge.test.ts)
- [src/auto-reply/reply/agent-event-bridge.ts](src/auto-reply/reply/agent-event-bridge.ts)
- [src/auto-reply/reply/agent-runner-cli-candidate.ts](src/auto-reply/reply/agent-runner-cli-candidate.ts)
- [src/auto-reply/reply/agent-runner-compaction-accounting.ts](src/auto-reply/reply/agent-runner-compaction-accounting.ts)
- [src/auto-reply/reply/agent-runner-embedded-candidate.ts](src/auto-reply/reply/agent-runner-embedded-candidate.ts)
- [src/auto-reply/reply/agent-runner-execution-cli-admission.test.ts](src/auto-reply/reply/agent-runner-execution-cli-admission.test.ts)
- [src/auto-reply/reply/agent-runner-execution-cli-delegation.test.ts](src/auto-reply/reply/agent-runner-execution-cli-delegation.test.ts)
- [src/auto-reply/reply/agent-runner-execution-cli-sessions.test.ts](src/auto-reply/reply/agent-runner-execution-cli-sessions.test.ts)
- [src/auto-reply/reply/agent-runner-execution-lifecycle.test.ts](src/auto-reply/reply/agent-runner-execution-lifecycle.test.ts)
- [src/auto-reply/reply/agent-runner-execution-message-tools.test.ts](src/auto-reply/reply/agent-runner-execution-message-tools.test.ts)
- [src/auto-reply/reply/agent-runner-fallback-candidate.ts](src/auto-reply/reply/agent-runner-fallback-candidate.ts)
- [src/auto-reply/reply/agent-runner-fallback-cycle.types.ts](src/auto-reply/reply/agent-runner-fallback-cycle.types.ts)
- [src/auto-reply/reply/agent-runner-run-params.ts](src/auto-reply/reply/agent-runner-run-params.ts)
- [src/auto-reply/reply/agent-runner-utils.test.ts](src/auto-reply/reply/agent-runner-utils.test.ts)
- [src/auto-reply/reply/before-deliver.test.ts](src/auto-reply/reply/before-deliver.test.ts)
- [src/auto-reply/reply/directive-handling.parse.ts](src/auto-reply/reply/directive-handling.parse.ts)
- [src/auto-reply/reply/directive-parsing.ts](src/auto-reply/reply/directive-parsing.ts)
- [src/auto-reply/reply/directives.ts](src/auto-reply/reply/directives.ts)
- [src/auto-reply/reply/dispatch-acp-delivery.test.ts](src/auto-reply/reply/dispatch-acp-delivery.test.ts)
- [src/auto-reply/reply/dispatch-acp-delivery.ts](src/auto-reply/reply/dispatch-acp-delivery.ts)
- [src/auto-reply/reply/dispatch-acp-manager.runtime.ts](src/auto-reply/reply/dispatch-acp-manager.runtime.ts)
- [src/auto-reply/reply/dispatch-acp.test.ts](src/auto-reply/reply/dispatch-acp.test.ts)
- [src/auto-reply/reply/dispatch-acp.ts](src/auto-reply/reply/dispatch-acp.ts)
- [src/auto-reply/reply/dispatch-from-config.abort-and-dedupe.test-utils.ts](src/auto-reply/reply/dispatch-from-config.abort-and-dedupe.test-utils.ts)
- [src/auto-reply/reply/dispatch-from-config.acp-privacy.test.ts](src/auto-reply/reply/dispatch-from-config.acp-privacy.test.ts)
- [src/auto-reply/reply/dispatch-from-config.base.test-utils.ts](src/auto-reply/reply/dispatch-from-config.base.test-utils.ts)
- [src/auto-reply/reply/dispatch-from-config.choose-route.ts](src/auto-reply/reply/dispatch-from-config.choose-route.ts)
- [src/auto-reply/reply/dispatch-from-config.delivery-and-tts.test-utils.ts](src/auto-reply/reply/dispatch-from-config.delivery-and-tts.test-utils.ts)
- [src/auto-reply/reply/dispatch-from-config.events.ts](src/auto-reply/reply/dispatch-from-config.events.ts)
- [src/auto-reply/reply/dispatch-from-config.execute.ts](src/auto-reply/reply/dispatch-from-config.execute.ts)
- [src/auto-reply/reply/dispatch-from-config.finalize.ts](src/auto-reply/reply/dispatch-from-config.finalize.ts)
- [src/auto-reply/reply/dispatch-from-config.gather.ts](src/auto-reply/reply/dispatch-from-config.gather.ts)
- [src/auto-reply/reply/dispatch-from-config.hooks-and-send-policy.test-utils.ts](src/auto-reply/reply/dispatch-from-config.hooks-and-send-policy.test-utils.ts)
- [src/auto-reply/reply/dispatch-from-config.lifecycle-and-bindings.test-utils.ts](src/auto-reply/reply/dispatch-from-config.lifecycle-and-bindings.test-utils.ts)
- [src/auto-reply/reply/dispatch-from-config.lifecycle.ts](src/auto-reply/reply/dispatch-from-config.lifecycle.ts)
- [src/auto-reply/reply/dispatch-from-config.prepare-context.ts](src/auto-reply/reply/dispatch-from-config.prepare-context.ts)
- [src/auto-reply/reply/dispatch-from-config.prepare-operation.ts](src/auto-reply/reply/dispatch-from-config.prepare-operation.ts)
- [src/auto-reply/reply/dispatch-from-config.send-policy-routing.test-utils.ts](src/auto-reply/reply/dispatch-from-config.send-policy-routing.test-utils.ts)
- [src/auto-reply/reply/dispatch-from-config.shared.test-harness.ts](src/auto-reply/reply/dispatch-from-config.shared.test-harness.ts)
- [src/auto-reply/reply/dispatch-from-config.stale-recovery.test.ts](src/auto-reply/reply/dispatch-from-config.stale-recovery.test.ts)
- [src/auto-reply/reply/dispatch-from-config.terminal-recovery.test.ts](src/auto-reply/reply/dispatch-from-config.terminal-recovery.test.ts)
- [src/auto-reply/reply/dispatch-from-config.test-harness.ts](src/auto-reply/reply/dispatch-from-config.test-harness.ts)
- [src/auto-reply/reply/dispatch-from-config.transcript.ts](src/auto-reply/reply/dispatch-from-config.transcript.ts)
- [src/auto-reply/reply/dispatch-from-config.types.ts](src/auto-reply/reply/dispatch-from-config.types.ts)
- [src/auto-reply/reply/exec/directive.ts](src/auto-reply/reply/exec/directive.ts)
- [src/auto-reply/reply/get-reply-run-admission.ts](src/auto-reply/reply/get-reply-run-admission.ts)
- [src/auto-reply/reply/get-reply-run-context.ts](src/auto-reply/reply/get-reply-run-context.ts)
- [src/auto-reply/reply/get-reply-run-execute.ts](src/auto-reply/reply/get-reply-run-execute.ts)
- [src/auto-reply/reply/get-reply-run-helpers.ts](src/auto-reply/reply/get-reply-run-helpers.ts)
- [src/auto-reply/reply/get-reply-run.media-only.test.ts](src/auto-reply/reply/get-reply-run.media-only.test.ts)
- [src/auto-reply/reply/get-reply.types.ts](src/auto-reply/reply/get-reply.types.ts)
- [src/auto-reply/reply/queue.collect.test.ts](src/auto-reply/reply/queue.collect.test.ts)
- [src/auto-reply/reply/queue/directive.ts](src/auto-reply/reply/queue/directive.ts)
- [src/auto-reply/reply/queue/drain.identity-guard.test.ts](src/auto-reply/reply/queue/drain.identity-guard.test.ts)
- [src/auto-reply/reply/queue/drain.ts](src/auto-reply/reply/queue/drain.ts)
- [src/auto-reply/reply/queue/types.ts](src/auto-reply/reply/queue/types.ts)
- [src/auto-reply/reply/reply-turn-admission.test.ts](src/auto-reply/reply/reply-turn-admission.test.ts)
- [src/auto-reply/reply/reply-turn-admission.ts](src/auto-reply/reply/reply-turn-admission.ts)
- [src/auto-reply/reply/source-reply-delivery-mode.test.ts](src/auto-reply/reply/source-reply-delivery-mode.test.ts)
- [src/auto-reply/reply/source-reply-delivery-mode.ts](src/auto-reply/reply/source-reply-delivery-mode.ts)
- [src/auto-reply/reply/source-reply-delivery-runtime.ts](src/auto-reply/reply/source-reply-delivery-runtime.ts)
- [src/channels/plugins/acp-stateful-target-driver.test.ts](src/channels/plugins/acp-stateful-target-driver.test.ts)
- [src/channels/plugins/acp-stateful-target-driver.ts](src/channels/plugins/acp-stateful-target-driver.ts)
- [src/channels/turn/dispatch-result.ts](src/channels/turn/dispatch-result.ts)
- [src/channels/turn/execution.ts](src/channels/turn/execution.ts)
- [src/channels/turn/lifecycle.ts](src/channels/turn/lifecycle.ts)
- [src/channels/turn/run-channel-turn.finalize.test.ts](src/channels/turn/run-channel-turn.finalize.test.ts)
- [src/channels/turn/run-channel-turn.pipeline.test.ts](src/channels/turn/run-channel-turn.pipeline.test.ts)
- [src/channels/turn/types.ts](src/channels/turn/types.ts)
- [src/config/sessions/lifecycle.ts](src/config/sessions/lifecycle.ts)
- [src/cron/isolated-agent/run-executor.ts](src/cron/isolated-agent/run-executor.ts)
- [src/gateway/agent-turn/agent-admission-controller.ts](src/gateway/agent-turn/agent-admission-controller.ts)
- [src/gateway/gateway-acp-bind.live.test.ts](src/gateway/gateway-acp-bind.live.test.ts)
- [src/gateway/gateway-concurrent-streams.test.ts](src/gateway/gateway-concurrent-streams.test.ts)
- [src/gateway/server-methods/chat-send-late-followup.test.ts](src/gateway/server-methods/chat-send-late-followup.test.ts)
- [src/gateway/server-methods/chat-send-late-followup.ts](src/gateway/server-methods/chat-send-late-followup.ts)
- [src/gateway/server-methods/chat-send-turn-adoption.ts](src/gateway/server-methods/chat-send-turn-adoption.ts)
- [src/gateway/server-methods/sessions-rewind.storage.test.ts](src/gateway/server-methods/sessions-rewind.storage.test.ts)
- [src/gateway/server-methods/sessions-shared.ts](src/gateway/server-methods/sessions-shared.ts)
- [src/gateway/server.startup-recovery-webchat.test.ts](src/gateway/server.startup-recovery-webchat.test.ts)
- [src/gateway/worker-environments/session-placement-lifecycle.ts](src/gateway/worker-environments/session-placement-lifecycle.ts)
- [src/infra/agent-events.run-listeners.test.ts](src/infra/agent-events.run-listeners.test.ts)
- [src/infra/agent-events.test.ts](src/infra/agent-events.test.ts)
- [src/infra/agent-events.ts](src/infra/agent-events.ts)
- [src/infra/kysely-sync-cache-state.ts](src/infra/kysely-sync-cache-state.ts)
- [src/infra/kysely-sync.test.ts](src/infra/kysely-sync.test.ts)
- [src/infra/kysely-sync.ts](src/infra/kysely-sync.ts)
- [src/plugin-sdk/acp-runtime.ts](src/plugin-sdk/acp-runtime.ts)
- [src/plugin-sdk/acpx.ts](src/plugin-sdk/acpx.ts)
- [src/sessions/session-lifecycle-admission.test.ts](src/sessions/session-lifecycle-admission.test.ts)
- [src/sessions/session-lifecycle-admission.ts](src/sessions/session-lifecycle-admission.ts)
- [src/shared/chat-message-content.ts](src/shared/chat-message-content.ts)
- [src/shared/text-truncate.test.ts](src/shared/text-truncate.test.ts)
- [src/shared/text-truncate.ts](src/shared/text-truncate.ts)

</details>



The Command System in OpenClaw provides a unified interface for structured control of agents, sessions, and system configurations. It bridges natural language chat interfaces with structured code execution through textual slash commands, native platform integrations, and internal agent directives.

---

## Overview

OpenClaw's command system is designed to be multi-platform and extensible. It allows users to bypass the LLM execution pipeline for direct system manipulation while providing rich UI elements like choice menus and autocomplete on supported platforms.

- **Unified Registry**: Centralized definitions for all system and plugin commands, managed via a declarative catalog. [src/cli/command-catalog.ts:77-77]()
- **Multi-Runtime Orchestration**: Commands trigger execution across Embedded (Pi Agent), CLI (e.g., `claude-cli`), or ACP (Agent Control Protocol) runtimes. [src/agents/command/attempt-execution.ts:1-3]()
- **Failover & Recovery**: Robust handling of provider failures through a structured failover error system that classifies errors into actionable categories like rate limits or context overflows. [src/agents/command/attempt-execution.ts:44-45]()
- **Status & Directives**: Support for inline directives (e.g., `/think`, `/verbose`, `/reasoning`) that modify model behavior mid-conversation. [src/auto-reply/reply/get-reply-run-execute.ts:134-140]()
- **Admission Control**: A session-based admission system ensures that only one command executes per session at a time, preventing state corruption. [src/sessions/session-lifecycle-admission.ts:13-13]()

Sources: [src/cli/command-catalog.ts:77-77](), [src/agents/command/attempt-execution.ts:1-45](), [src/auto-reply/reply/get-reply-run-execute.ts:134-140](), [src/sessions/session-lifecycle-admission.ts:13-13]()

---

## Command Architecture

The system distinguishes between **Core Commands** (built-in system controls), **Plugin Commands** (extended via the plugin SDK), and **Inline Directives** (flags that modify model behavior).

### Command Detection and Execution Path

The command system identifies commands by checking if a message starts with a `/` via `hasControlCommand`. The execution pipeline manages the lifecycle of an agent turn, including session binding, model selection, and delivery.

**Diagram: Agent Turn Execution Lifecycle**
```mermaid
graph TD
    "Start[User Message / Slash Command]" --> "Detect[hasControlCommand]"
    "Detect" --> "Prep[prepareReplyRunContext]"
    "Prep" --> "Admission[executePreparedReplyRun]"
    "Admission" --> "Runtime{Backend Type?}"
    "Runtime" -- "CLI" --> "CliRunner[runCliFallbackCandidate]"
    "Runtime" -- "Embedded" --> "EmbeddedRunner[runEmbeddedFallbackCandidate]"
    "Runtime" -- "ACP" --> "AcpRunner[tryDispatchAcpReplyCore]"
    "CliRunner" --> "Persist[persistCliTurnTranscript]"
    "EmbeddedRunner" --> "Persist[persistSessionTranscriptTurn]"
    "AcpRunner" --> "Persist[persistAcpDispatchTranscript]"

    subgraph "Natural Language Space"
    "Start[User types /reset or /think high]"
    end

    subgraph "Code Entity Space"
    "hasControlCommand[src/auto-reply/reply/get-reply-run.media-only.test.ts:15-15]"
    "prepareReplyRunContext[src/auto-reply/reply/get-reply-run-context.ts:1-5]"
    "executePreparedReplyRun[src/auto-reply/reply/get-reply-run-execute.ts:58-58]"
    "runCliFallbackCandidate[src/auto-reply/reply/agent-runner-cli-candidate.ts:41-41]"
    "runEmbeddedFallbackCandidate[src/auto-reply/reply/agent-runner-embedded-candidate.ts:39-39]"
    "tryDispatchAcpReplyCore[src/auto-reply/reply/dispatch-acp.ts:36-36]"
    "persistSessionTranscriptTurn[src/agents/command/attempt-execution.ts:27-27]"
    "persistAcpDispatchTranscript[src/auto-reply/reply/dispatch-acp.test.ts:150-150]"
    end
```
Sources: [src/auto-reply/reply/get-reply-run-execute.ts:58-85](), [src/auto-reply/reply/agent-runner-cli-candidate.ts:41-50](), [src/auto-reply/reply/agent-runner-embedded-candidate.ts:39-55](), [src/agents/command/attempt-execution.ts:27-30]()

### Admission and State Control

Execution is governed by the `withLocalSessionPlacementTurnSettlement`, which manages session-specific locks. It ensures that foreground tasks take priority and that lifecycle generations are tracked to prevent "stale" execution.

**Diagram: Admission and Context Logic**
```mermaid
graph TD
    "Request[Agent Command]" --> "Admission[withLocalSessionPlacementTurnSettlement]"
    "Admission" --> "Check[resolveAgentLifecycleTerminalBackstop]"
    "Check" --> "Auth[resolveRunAuthProfile]"
    "Auth" --> "Exec[Task Execution]"

    subgraph "Natural Language Space"
    "Request[User types message in Chat UI]"
    end

    subgraph "Code Entity Space"
    "withLocalSessionPlacementTurnSettlement[src/agents/session-placement-admission.ts:1-5]"
    "resolveAgentLifecycleTerminalBackstop[src/auto-reply/reply/agent-lifecycle-terminal.ts:1-5]"
    "resolveRunAuthProfile[src/auto-reply/reply/agent-runner-auth-profile.ts:1-5]"
    end
```
Sources: [src/auto-reply/reply/agent-runner-cli-candidate.ts:74-85](), [src/agents/command/attempt-execution.ts:110-110]()

---

## Command Dispatch and Arguments

Commands can be dispatched via the Gateway RPC or directly via the CLI. The system supports complex argument parsing for session selection, model overrides, and delivery options.

### Argument Parsing and Options
The `AgentFallbackCandidateCommonParams` and `RunEmbeddedAgentInternalParams` define the structured input for the execution system. [src/auto-reply/reply/agent-runner-fallback-cycle.types.ts:1-5](), [src/agents/embedded-agent-runner/run/internal-params.ts:5-6]()

| Option | Description |
| :--- | :--- |
| `thinkLevel` | Sets the reasoning intensity (e.g., `high`, `medium`). [src/auto-reply/reply/agent-runner-embedded-candidate.ts:65-65]() |
| `fastMode` | Enables faster, potentially less accurate execution. [src/auto-reply/reply/agent-runner-embedded-candidate.ts:64-64]() |
| `authProfileId` | Explicitly selects a credential profile for the run. [src/auto-reply/reply/agent-runner-embedded-candidate.ts:93-94]() |
| `sourceReplyDeliveryMode` | Controls how the agent replies (e.g., `automatic` or `message_tool_only`). [src/agents/command/attempt-execution.cli.test.ts:62-62]() |

### ACP Dispatch
The Agent Control Protocol (ACP) allows for sub-agent orchestration. The `tryDispatchAcpReplyCore` function manages sending turns to specialized agents and projecting their events back to the main session. [src/auto-reply/reply/dispatch-acp.ts:36-36]()

### CLI Command System
The CLI uses a declarative catalog to define command paths. For automated tasks, the system supports a `COMMAND_STYLE_CRON_PREFIX` to detect shell-like commands in cron jobs. [src/cron/isolated-agent/run-executor.ts:130-131]()

---

## Status and Directives

The command system provides visibility into the agent's current state and allows for mid-conversation behavioral adjustments.

### Inline Directives
Directives are tags embedded in messages or passed as options that modify the behavior of the next agent turn:
- **Thinking Level**: `/think` level adjustments resolved via `resolveCandidateThinkingLevel`. [src/auto-reply/reply/agent-runner-fallback-candidate.ts:9-9]()
- **Verbosity**: `/verbose` levels for detailed output (e.g., `full` vs `minimal`). [src/auto-reply/reply/agent-runner-cli-candidate.ts:98-98]()
- **Reasoning**: `/reasoning` tags handled via `isReasoningTagProvider`. [src/auto-reply/reply/get-reply-run-execute.ts:30-30]()
- **Reset Commands**: Triggered when `isBareSessionReset` is detected, allowing for session clearing. [src/auto-reply/reply/get-reply-run-execute.ts:104-104]()

### Usage Tracking
Every command execution tracks token usage and costs. The system uses `CompactionAccountingFact` to track context usage and triggers compaction when limits are reached. [src/auto-reply/reply/agent-runner-embedded-candidate.ts:51-54]()

Sources: [src/auto-reply/reply/agent-runner-fallback-candidate.ts:9-9](), [src/auto-reply/reply/agent-runner-cli-candidate.ts:98-98](), [src/auto-reply/reply/agent-runner-embedded-candidate.ts:51-54]()

---

## Implementation Reference

### Key Functions and Classes

| Entity | Description | Location |
| :--- | :--- | :--- |
| `runAgentAttempt` | Orchestrates one agent attempt across embedded, CLI, and ACP runtimes. | [src/agents/command/attempt-execution.ts:53-53]() |
| `executePreparedReplyRun` | The entry point for executing a turn after context has been gathered. | [src/auto-reply/reply/get-reply-run-execute.ts:58-58]() |
| `runEmbeddedFallbackCandidate` | Executes a turn using the internal Pi Agent runtime. | [src/auto-reply/reply/agent-runner-embedded-candidate.ts:39-39]() |
| `runCliFallbackCandidate` | Executes a turn using an external CLI backend (e.g., `claude-cli`). | [src/auto-reply/reply/agent-runner-cli-candidate.ts:41-41]() |
| `tryDispatchAcpReplyCore` | Dispatches a turn to an ACP-compatible agent. | [src/auto-reply/reply/dispatch-acp.ts:36-36]() |
| `dispatchEmbeddedRunAttempt` | Low-level dispatch for embedded runs with specific lifecycle controls. | [src/agents/embedded-agent-runner/run/run-attempt-dispatch.ts:124-124]() |
| `kickFollowupDrainIfIdle` | Restarts the queue drain for follow-up runs. | [src/auto-reply/reply/queue/drain.ts:129-129]() |

Sources: [src/agents/command/attempt-execution.ts:53-53](), [src/auto-reply/reply/get-reply-run-execute.ts:58-58](), [src/auto-reply/reply/agent-runner-embedded-candidate.ts:39-39](), [src/auto-reply/reply/agent-runner-cli-candidate.ts:41-41](), [src/auto-reply/reply/dispatch-acp.ts:36-36](), [src/agents/embedded-agent-runner/run/run-attempt-dispatch.ts:124-124](), [src/auto-reply/reply/queue/drain.ts:129-129]()

---

