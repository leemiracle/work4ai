# Architecture

This page explains the role, data flow, module layout, and key design decisions of Agent Gateway.

## Role

The system uses a split deployment: **Gateway + AgentServer**.

- **Gateway**: the access layer for clients and IM platforms. It handles multi-channel access, request normalization, routing, session binding, cron scheduling, heartbeat, and health checks.
- **AgentServer**: the execution layer. It runs the agent loop, model calls, workspace I/O, tool sandboxing, and file persistence.

The gateway is stateless with respect to agent execution: everything that touches the workspace, model credentials, or the tool sandbox is executed by the AgentServer.

## Data flow

```text
 Web UI / TUI / ACP / IM channels
              │  WebSocket (E2A frames)
              ▼
     Agent Gateway
       ├─ MessageHandler + ChannelManager
       ├─ WebChannel (uvicorn) / TUI route
       ├─ Cron scheduler · heartbeat · health check
       └─ routing / session binding
              │  AgentServer WebSocket (E2A)
              ▼
      jiuwenswarm-agentserver
```

A typical request path:

1. A channel receives the raw message (WebSocket frame, IM platform event, and so on).
2. The gateway normalizes it into unified E2A request fields (`user_id`, `message_id`, `params`, session info, and so on).
3. `MessageHandler` parses commands and routing information; `ChannelManager` keeps channel and session bindings.
4. The `routing` layer sends the request over the single AgentServer WebSocket and demultiplexes responses and stream chunks by request id.
5. The gateway projects the response back to the originating channel (WebSocket events, IM messages, ACP/A2A responses, and so on).

See the [E2A protocol reference](../reference/e2a-protocol.md) for field definitions.

## Modules

| Module | Responsibility |
| --- | --- |
| `app_gateway.py` | Process entry point: startup orchestration, AgentServer connection and retries, channel config application, workspace lock, background task lifecycle |
| `channel_manager/` | Channel registration, lazy loading, and message dispatch; `web/`, `tui/`, `im_platforms/`, `protocol/` (ACP, A2A, SSH, web proxy) |
| `message_handler/` | Message normalization, command parsing, join/exit handling, evolution approval, and related logic |
| `routing/` | AgentServer client, E2A forwarding, route binding, session mapping, and multi-instance routing |
| `cron/` | Cron job store, scheduler, and command acknowledgement; jobs are executed by the AgentServer |
| `heartbeat/`, `health_check/` | Periodic health checks and heartbeat, exposing Gateway / AgentServer state |
| `im_pipeline/` | IM inbound/outbound adapters and media handling |
| `extensions/` | Pluggable capabilities such as extension registration and authentication |
| `embedded/` | Built-in runtime adapters: agent prewarming, attachments, sessions, HarmonyOS, and so on |

## Startup sequence

1. Parse `--dotenv` / environment variables and prepare the workspace (the first start initializes default skills, config, and so on).
2. Read `config.yaml` and parse `channels` and `health_check`.
3. Connect to the AgentServer over WebSocket (retry according to `AGENT_CONNECT_RETRY`).
4. Acquire the workspace singleton lock `.gateway.lock` to prevent multiple gateways on one workspace.
5. Start the cron scheduler, heartbeat and health checks, WebChannel, and the TUI route.
6. Lazily load IM channels and their dependencies for entries present under `channels`.

## Key design decisions

- **One downstream connection + request-id multiplexing**: all clients share one AgentServer WebSocket instead of opening a downstream connection per client; responses and stream chunks are demultiplexed by request id.
- **Lazy channel loading**: only channels present under `channels` are initialized; unconfigured channels pull in no dependencies and hold no connections.
- **Routing state lives in the gateway**: on reconnect or channel switch, the gateway preserves session, project, work mode, and channel bindings.
- **Workspace singleton lock**: held by an OS file lock and released automatically if the process crashes; only one gateway may serve a workspace, which prevents duplicate cron scheduling.
- **Security boundary**: WebSocket Origin checks, `user_id` allow-list, explicit stripping of client-forged auth keys, and credentials forwarded only from authenticated channels.
- **System task protection**: system-owned jobs such as `proactive.tick` cannot be created or edited manually.
- **Execution neutrality**: the gateway never writes into the user's project directory; IM files are persisted by the AgentServer.

## Non-goals

- Running the agent loop or calling models.
- Reading or writing business files in the user's project directory.
- Replacing the AgentServer's permission, tool, or sandbox controls.

---

## Navigation

- [Documentation home](../../README.md)
- [E2A protocol reference](../reference/e2a-protocol.md)
- [CLI and environment](../reference/cli-and-environment.md)
