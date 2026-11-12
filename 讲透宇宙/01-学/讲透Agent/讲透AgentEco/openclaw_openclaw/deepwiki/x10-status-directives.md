<!-- source: DeepWiki mcp.deepwiki.com · repo openclaw/openclaw · extra page Status & Directives · fetched 2026-10-27 -->

# Status & Directives

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.agents/skills/openclaw-update/SKILL.md](.agents/skills/openclaw-update/SKILL.md)
- [.agents/skills/openclaw-update/agents/openai.yaml](.agents/skills/openclaw-update/agents/openai.yaml)
- [.agents/skills/update-team-server/SKILL.md](.agents/skills/update-team-server/SKILL.md)
- [.github/labeler.yml](.github/labeler.yml)
- [CHANGELOG.md](CHANGELOG.md)
- [appcast.xml](appcast.xml)
- [docs/.i18n/glossary.zh-CN.json](docs/.i18n/glossary.zh-CN.json)
- [docs/.i18n/zh-Hans-navigation.json](docs/.i18n/zh-Hans-navigation.json)
- [docs/concepts/memory-architecture.md](docs/concepts/memory-architecture.md)
- [docs/docs.json](docs/docs.json)
- [docs/releases/2026.8.1.md](docs/releases/2026.8.1.md)
- [docs/releases/2026.8.2.md](docs/releases/2026.8.2.md)
- [docs/releases/2026.9.1.md](docs/releases/2026.9.1.md)
- [docs/releases/index.md](docs/releases/index.md)
- [scripts/github/barnacle-auto-response.mjs](scripts/github/barnacle-auto-response.mjs)
- [scripts/run-oxlint-shards.mts](scripts/run-oxlint-shards.mts)
- [scripts/run-oxlint.mts](scripts/run-oxlint.mts)
- [src/agents/internal-runtime-context.test.ts](src/agents/internal-runtime-context.test.ts)
- [src/agents/internal-runtime-context.ts](src/agents/internal-runtime-context.ts)
- [src/auto-reply/tokens.test.ts](src/auto-reply/tokens.test.ts)
- [src/auto-reply/tokens.ts](src/auto-reply/tokens.ts)
- [src/config/sessions/session-accessor.entry.ts](src/config/sessions/session-accessor.entry.ts)
- [src/config/sessions/session-accessor.readonly.test.ts](src/config/sessions/session-accessor.readonly.test.ts)
- [src/config/sessions/session-accessor.sqlite-contract.ts](src/config/sessions/session-accessor.sqlite-contract.ts)
- [src/config/sessions/session-accessor.sqlite-data-version.test.ts](src/config/sessions/session-accessor.sqlite-data-version.test.ts)
- [src/config/sessions/session-accessor.sqlite-entry-cache.ts](src/config/sessions/session-accessor.sqlite-entry-cache.ts)
- [src/config/sessions/session-accessor.sqlite-entry-store.ts](src/config/sessions/session-accessor.sqlite-entry-store.ts)
- [src/config/sessions/session-accessor.sqlite-entry.ts](src/config/sessions/session-accessor.sqlite-entry.ts)
- [src/config/sessions/session-accessor.sqlite-status.ts](src/config/sessions/session-accessor.sqlite-status.ts)
- [src/config/sessions/session-accessor.test.ts](src/config/sessions/session-accessor.test.ts)
- [src/config/sessions/session-accessor.ts](src/config/sessions/session-accessor.ts)
- [src/config/sessions/session-accessor.types.ts](src/config/sessions/session-accessor.types.ts)
- [src/gateway/server-methods/chat-history-handler.test.ts](src/gateway/server-methods/chat-history-handler.test.ts)
- [src/gateway/server-methods/chat-send-admission.ts](src/gateway/server-methods/chat-send-admission.ts)
- [src/gateway/server-methods/chat-send-agent-dispatch.ts](src/gateway/server-methods/chat-send-agent-dispatch.ts)
- [src/gateway/server-methods/chat-send-dispatch-errors.test.ts](src/gateway/server-methods/chat-send-dispatch-errors.test.ts)
- [src/gateway/server-methods/chat-send-dispatch-errors.ts](src/gateway/server-methods/chat-send-dispatch-errors.ts)
- [src/gateway/server-methods/chat-send-external-authority-contract.ts](src/gateway/server-methods/chat-send-external-authority-contract.ts)
- [src/gateway/server-methods/chat-send-external-entry.ts](src/gateway/server-methods/chat-send-external-entry.ts)
- [src/gateway/server-methods/chat-send-handler.ts](src/gateway/server-methods/chat-send-handler.ts)
- [src/gateway/server-methods/chat-send-source-finalization.ts](src/gateway/server-methods/chat-send-source-finalization.ts)
- [src/gateway/server-methods/chat.directive-tags.test.ts](src/gateway/server-methods/chat.directive-tags.test.ts)
- [src/gateway/server.chat.gateway-server-chat.test.ts](src/gateway/server.chat.gateway-server-chat.test.ts)
- [src/gateway/session-utils-store-lookup.ts](src/gateway/session-utils-store-lookup.ts)
- [src/gateway/session-utils.single-row-cache.test.ts](src/gateway/session-utils.single-row-cache.test.ts)
- [src/gateway/tools-invoke-http.cron-regression.test.ts](src/gateway/tools-invoke-http.cron-regression.test.ts)
- [src/infra/restart-handoff.test.ts](src/infra/restart-handoff.test.ts)
- [src/sessions/session-work-admission-handoff.ts](src/sessions/session-work-admission-handoff.ts)
- [test/scripts/barnacle-auto-response.test.ts](test/scripts/barnacle-auto-response.test.ts)
- [test/scripts/docs-sync-publish.test.ts](test/scripts/docs-sync-publish.test.ts)
- [test/scripts/local-check-runtime.test.ts](test/scripts/local-check-runtime.test.ts)
- [test/scripts/run-oxlint.test.ts](test/scripts/run-oxlint.test.ts)

</details>



## Purpose and Scope

This page documents the **status message system** and **inline directives** in OpenClaw. Status messages provide runtime information about the current session, model configuration, token usage, and related parameters. Inline directives such as `/think`, `/verbose`, `/reasoning`, and `/fast` allow users to modify agent behavior dynamically within a chat message. This section covers the implementation of directive persistence, normalization, and the construction of status responses during the agent execution lifecycle, including the advanced usage bar templating system.

---

## Status Messages

Status messages present detailed runtime information for the current session. The system identifies the active runtime—such as the built-in Pi Agent Core or external harnesses—to tailor the status output. Status lines are often contributed by plugins and the core agent runner to provide a comprehensive view of the session state.

### Status Construction Pipeline

The construction of status information gathers data from the active `SessionEntry` [src/gateway/server.chat.gateway-server-chat.test.ts:182-190]() and configuration defaults. Key metadata includes versions, model configurations, and current queue/activation states. The construction logic relies on runtime facts such as the effective agent runtime and the current model identity resolved via `resolveSessionModel` [src/gateway/server-methods/chat-send-agent-dispatch.ts:141-141]().

**Status Construction Flow**

```mermaid
graph TD
    [A]["User/System Request Status"] --> [B]["chat.history Handler"]
    [B] --> [C]["loadSessionEntry"]
    [B] --> [D]["resolveMirroredTranscriptText"]
    [B] --> [E]["projectAssistantDisplayContent"]
    [C] & [D] --> [E]
    [E] --> [F]["Rendered Status/Title Payload"]

    subgraph "Key Functions & Data"
        [C] -- "SessionEntry" --> "src/config/sessions/session-accessor.ts"
        [D] -- "Transcript Text Mirroring" --> "src/config/sessions/transcript-mirror.ts"
        [E] -- "Display Projection" --> "src/shared/assistant-display-content.ts"
    end
```
Sources: [src/gateway/server.chat.gateway-server-chat.test.ts:149-155](), [src/gateway/server-methods/chat.directive-tags.test.ts:49-54](), [src/config/sessions/session-accessor.ts:153-156]().

The system resolves model authentication profiles and overrides per session. During `chat.send`, the Gateway tracks server timing attributes to provide latency breakdowns for different phases of the status construction [src/gateway/server-methods/chat-server-timing.ts:47-51]().

---

## Directives Overview

**Directives** are inline annotations or tags embedded within chat messages to control agent behavior or specify delivery logic. They are processed during the `chat.send` dispatch pipeline [src/gateway/server-methods/chat-send-handler.ts:78-83]().

### Directive Persistence vs Ephemeral Use

The system distinguishes between directives that modify the session state and those that apply to specific messages:

1.  **Session Directives**: Handled by the command interpretation layer, these can persist settings like model choice or agent behavior.
2.  **Message Directives**: Tags like `[[reply_to_current]]` are parsed to route replies or handle specific message injections [src/gateway/server-methods/chat.directive-tags.test.ts:100-100]().

### Directive Normalization

The system parses inline directives into payload fields. During the execution of an agent turn, the system extracts metadata such as verbose levels and thinking levels. The `ReplyPayload` carries metadata that informs the client of the directive's effect [src/gateway/server-methods/chat.directive-tags.test.ts:25-25](). For detached dispatches, the logic handles the handoff to the agent runtime with specific context fields [src/gateway/server-methods/chat-send-agent-dispatch.ts:37-39]().

**Directive Types and Effects**

| Directive | Description | Implementation Source |
|:---|:---|:---|
| `/think` | Adjusts the reasoning level (e.g., `low`, `medium`, `high`) | [src/gateway/server-methods/chat.directive-tags.test.ts:127-127]() |
| `/verbose` | Controls the verbosity of the agent's internal logs | [src/gateway/server-methods/chat-send-agent-dispatch.ts:17-17]() |
| `NO_REPLY` | Suppresses the assistant's response for a specific turn | [src/gateway/server.chat.gateway-server-chat.test.ts:119-119]() |

### Response Sanitization

Before a reply is delivered, the system ensures internal routing tags are handled. The `finalizeChatSendDispatchedReplies` function handles the final payload delivery, including logic for broadcasting the final state to the client [src/gateway/server-methods/chat-send-agent-dispatch.ts:41-41]().

Sources: [src/gateway/server-methods/chat-send-agent-dispatch.ts:40-45](), [src/gateway/server.chat.gateway-server-chat.test.ts:117-127](), [src/gateway/server-methods/chat.directive-tags.test.ts:100-105]().

---

## Inbound Metadata and Context

Directives are often accompanied by inbound metadata that informs the agent of its environment. This metadata is validated and normalized before being injected into the system prompt.

### Metadata Normalization
The `prepareAndAdmitChatSend` function assembles the execution context from the incoming WebSocket request [src/gateway/server-methods/chat-send-handler.ts:79-83](). This includes resolving the `sessionKey` and `agentId` which are then registered in the `agent-run-registry` [src/gateway/server-methods/chat-send-agent-dispatch.ts:133-144]().

**Metadata Flow**

```mermaid
graph TD
    [A]["Inbound User Message"] --> [B]["handleChatSend"]
    [B] --> [C]["prepareAndAdmitChatSend"]
    [C] --> [D]["startChatDispatch"]
    [D] --> [E]["dispatchInboundMessageWithProjectedDispatcher"]
    [E] --> [F]["Finalized Runtime Context"]

    subgraph "Code Entities"
        [B] -- "src/gateway/server-methods/chat-send-handler.ts" --> [C]
        [C] -- "src/gateway/server-methods/chat-send-setup.ts" --> [D]
        [D] -- "src/gateway/server-methods/chat-send-agent-dispatch.ts" --> [E]
    end
```
Sources: [src/gateway/server-methods/chat-send-handler.ts:79-83](), [src/gateway/server-methods/chat-send-agent-dispatch.ts:10-12](), [src/gateway/server-methods/chat-send-agent-dispatch.ts:103-122]().

---

## Diagrams Bridging Natural Language & Code Entities

### 1. Directive Processing Map

```mermaid
graph LR
    subgraph "Natural Language Space"
        [UserMsg]["User message with directives: '/think high'"]
    end

    subgraph "Code Entity Space"
        [UserMsg] --> [Handler]["src/gateway/server-methods/chat-send-handler.ts::handleChatSend"]
        [Handler] --> [Dispatch]["src/gateway/server-methods/chat-send-agent-dispatch.ts::startChatDispatch"]
        [Dispatch] --> [Projector]["src/auto-reply/dispatch.ts::dispatchInboundMessageWithProjectedDispatcher"]
    end
```

Sources: [src/gateway/server-methods/chat-send-handler.ts:79-83](), [src/gateway/server-methods/chat-send-agent-dispatch.ts:103-122]().

### 2. Status & Runtime Resolution

```mermaid
graph TD
    subgraph "Natural Language Space"
        [StatusReq]["Client requests session history and status"]
    end

    subgraph "Code Entity Space"
        [StatusReq] --> [RPC]["src/gateway/server.chat.gateway-server-chat.test.ts::chat.history"]
        [RPC] --> [Accessor]["src/config/sessions/session-accessor.ts::loadSessionEntry"]
        [Accessor] --> [DB]["src/config/sessions/session-accessor.sqlite-entry.ts::loadExactSessionEntry"]
    end
```

Sources: [src/gateway/server.chat.gateway-server-chat.test.ts:149-153](), [src/config/sessions/session-accessor.ts:153-156]().

---

