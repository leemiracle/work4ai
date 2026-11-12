# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude/skills/worktree/SKILL.md](.claude/skills/worktree/SKILL.md)
- [CLAUDE.md](CLAUDE.md)
- [README.md](README.md)
- [backend/internal/api/grpc/runner_adapter_mcp.go](backend/internal/api/grpc/runner_adapter_mcp.go)
- [backend/internal/api/grpc/runner_adapter_mcp_ticket.go](backend/internal/api/grpc/runner_adapter_mcp_ticket.go)
- [backend/internal/service/ticket/ticket_query.go](backend/internal/service/ticket/ticket_query.go)
- [backend/internal/service/ticket/ticket_query_test.go](backend/internal/service/ticket/ticket_query_test.go)
- [deploy/dev/.gitignore](deploy/dev/.gitignore)
- [deploy/dev/backend.Dockerfile](deploy/dev/backend.Dockerfile)
- [deploy/dev/docker-compose.yml](deploy/dev/docker-compose.yml)
- [deploy/dev/init-seed.sh](deploy/dev/init-seed.sh)
- [deploy/dev/nginx/conf.d/default.conf](deploy/dev/nginx/conf.d/default.conf)
- [deploy/dev/nginx/nginx.conf](deploy/dev/nginx/nginx.conf)
- [deploy/dev/runner-entrypoint.sh](deploy/dev/runner-entrypoint.sh)
- [deploy/dev/runner.Dockerfile](deploy/dev/runner.Dockerfile)
- [deploy/dev/seed/seed.sql](deploy/dev/seed/seed.sql)
- [deploy/dev/traefik/dynamic/grpc.yml](deploy/dev/traefik/dynamic/grpc.yml)
- [deploy/dev/web.Dockerfile](deploy/dev/web.Dockerfile)
- [docs/images/architecture.svg](docs/images/architecture.svg)
- [runner/internal/mcp/grpc_client.go](runner/internal/mcp/grpc_client.go)
- [runner/internal/mcp/http_server.go](runner/internal/mcp/http_server.go)
- [runner/internal/mcp/http_tools_format_integration_test.go](runner/internal/mcp/http_tools_format_integration_test.go)
- [runner/internal/mcp/http_tools_ticket.go](runner/internal/mcp/http_tools_ticket.go)
- [runner/internal/mcp/tools/types_client.go](runner/internal/mcp/tools/types_client.go)
- [runner/internal/mcp/tools/types_entity.go](runner/internal/mcp/tools/types_entity.go)
- [web/src/components/landing/PricingSection.tsx](web/src/components/landing/PricingSection.tsx)
- [web/src/components/ui/block-editor.tsx](web/src/components/ui/block-editor.tsx)
- [web/src/lib/api/base.ts](web/src/lib/api/base.ts)
- [web/src/messages/de/landing.json](web/src/messages/de/landing.json)
- [web/src/messages/en/landing.json](web/src/messages/en/landing.json)
- [web/src/messages/es/landing.json](web/src/messages/es/landing.json)
- [web/src/messages/fr/landing.json](web/src/messages/fr/landing.json)
- [web/src/messages/ja/landing.json](web/src/messages/ja/landing.json)
- [web/src/messages/ko/landing.json](web/src/messages/ko/landing.json)
- [web/src/messages/pt/landing.json](web/src/messages/pt/landing.json)
- [web/src/messages/zh/landing.json](web/src/messages/zh/landing.json)

</details>



This page introduces AgentsMesh: what the platform does, its five main components, the BYOK model, and the self-hosted execution model. For how the components communicate at the protocol level, see [Architecture](#1.1). For definitions of domain terms such as Pod, Channel, Binding, and Sandbox, see [Core Concepts](#1.2).

---

## What is AgentsMesh?

AgentsMesh is a platform for running and coordinating terminal-based AI coding agents (Claude Code, Codex CLI, Gemini CLI, Aider, and others) at team scale. Rather than running agents one at a time on a developer's local machine, it provides:

- **AgentPods** — Isolated execution environments each with a PTY terminal, a Git worktree sandbox, and a browser-accessible terminal view
- **Multi-agent collaboration** — Agents communicate via Channels, observe and control peer terminals via Bindings, and can spawn new Pods autonomously using MCP tools
- **Ticket management** — Kanban board with agent-to-ticket binding and MR/PR webhook integration
- **Self-hosted Runners** — All code execution stays on user infrastructure; the platform only orchestrates lifecycle commands

---

## BYOK (Bring Your Own Key)

AgentsMesh does not proxy AI API calls. Users supply their own provider API keys — `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, etc. — directly to the Runner process environment. The platform orchestrates agents but never handles AI inference traffic. There are no per-token usage caps imposed by the platform; AI costs appear on the user's own provider account.

Keys are passed to Pods through the runner's sandbox environment. The full set of supported key variables is in [deploy/dev/docker-compose.yml:279-288]().

---

## Self-Hosted Execution Model

The Runner (`runner/`) is a Go daemon deployed on user-controlled infrastructure — a laptop, VM, or Kubernetes cluster. It connects **outbound** to the Backend over gRPC with mTLS. The Backend never receives file contents or raw agent output; it only issues lifecycle commands (`create_pod`, `terminate_pod`, `terminal_input`) and receives heartbeats and status updates over the bidirectional gRPC stream.

Terminal I/O is handled by a separate **Relay** (`relay/`) component that provides WebSocket pub/sub between browsers and runners. This separation keeps the Backend stateless with respect to terminal data and allows the Relay to scale independently. This is explicit in the docker-compose comment: *"Separates control flow (Backend) from data flow (Relay) for scalability"* ([deploy/dev/docker-compose.yml:321-323]()).

---

## Key Components

| Component | Directory | Language / Framework | Primary Role |
|-----------|-----------|---------------------|-------------|
| **Backend** | `backend/` | Go, Gin, GORM | REST API, gRPC server, auth, pod lifecycle, billing, event bus |
| **Web** | `web/` | Next.js (App Router), TypeScript | Browser UI: terminal workspace, kanban, mesh topology, channels |
| **Web-Admin** | `web-admin/` | Next.js, TypeScript | Internal admin console: users, orgs, runners, audit logs |
| **Runner** | `runner/` | Go | Self-hosted daemon; connects to Backend (gRPC+mTLS) and Relay (WebSocket), manages Pod PTY lifecycle |
| **Relay** | `relay/` | Go | WebSocket pub/sub relay for terminal I/O between browser and runner |
| **Proto** | `proto/` | Protocol Buffers | Shared gRPC message definitions for Backend ↔ Runner stream |

Sources: [README.md:108-114](), [CLAUDE.md:7-12]()

---

**Component and Key Code Entity Map**

```mermaid
graph TB
    subgraph "Browser"
        WEBUI["web/ (Next.js)"]
        TERMPOOL["TerminalConnectionPool"]
    end
    subgraph "backend/"
        GINREST["Gin REST Router :8080"]
        GRPCADAPT["GRPCRunnerAdapter :9443"]
        CONNMGR["RunnerConnectionManager"]
        PGREDIS[("PostgreSQL / Redis / MinIO")]
    end
    subgraph "relay/"
        CHANMGR["ChannelManager"]
        TERMCHAN["TerminalChannel"]
    end
    subgraph "runner/ (user infrastructure)"
        RPCCLIENT["RPCClient (grpc_connection.go)"]
        RUNNERMAIN["Runner (runner.go)"]
        MCPHTTP["HTTPServer (mcp/http_server.go)"]
    end

    WEBUI -->|"REST /api"| GINREST
    WEBUI -->|"WebSocket /api/ws"| GINREST
    TERMPOOL -->|"WebSocket /relay"| CHANMGR
    GINREST --- PGREDIS
    GRPCADAPT <-->|"gRPC + mTLS"| RPCCLIENT
    CONNMGR --> GRPCADAPT
    RPCCLIENT --> RUNNERMAIN
    RUNNERMAIN --> MCPHTTP
    RUNNERMAIN -->|"WebSocket"| CHANMGR
    CHANMGR --> TERMCHAN
    TERMCHAN -->|"broadcast"| TERMPOOL
```

Sources: [README.md:100-114](), [CLAUDE.md:137-171](), [deploy/dev/docker-compose.yml:110-383]()

---

**Control Plane vs Data Plane Flow**

```mermaid
sequenceDiagram
    participant Browser as "Browser (TerminalConnectionPool)"
    participant Relay as "relay/ ChannelManager"
    participant Runner as "runner/ pty_forwarder.go"
    participant Backend as "backend/ GRPCRunnerAdapter"

    Note over Backend,Runner: Control Plane — gRPC + mTLS :9443
    Backend->>Runner: create_pod (via RunnerConnectionManager)
    Runner->>Backend: heartbeat / status updates

    Note over Browser,Runner: Data Plane — WebSocket via Relay
    Runner->>Relay: WebSocket connect (publisher role)
    Browser->>Relay: WebSocket connect (subscriber role)
    Runner->>Relay: publish terminal output bytes
    Relay->>Browser: broadcast to subscribers
    Browser->>Relay: terminal input message
    Relay->>Runner: deliver input to PTY
```

Sources: [README.md:102-103](), [CLAUDE.md:159-170](), [deploy/dev/docker-compose.yml:321-382]()

---

## Supported Agents

Any terminal-based process can run as an agent. The platform provides first-class configuration support for:

| Agent | Provider |
|-------|---------|
| Claude Code | Anthropic |
| Codex CLI | OpenAI |
| Gemini CLI | Google |
| Aider | Open Source |
| OpenCode | Open Source |
| Custom | Any terminal-based process |

The Runner injects API keys from its own environment into each Pod's sandbox. Agents authenticate with provider APIs directly; the platform only controls the PTY lifecycle.

Sources: [README.md:186-195]()

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | Go 1.24+, Gin, GORM |
| Database | PostgreSQL 16, Redis 7 |
| Object Storage | MinIO (S3-compatible) |
| Frontend | Next.js (App Router), TypeScript, Tailwind CSS |
| Runner ↔ Backend | gRPC bidirectional streaming, Protocol Buffers, mTLS certificates |
| Runner ↔ Relay | WebSocket |
| Browser ↔ Relay | WebSocket |
| Browser ↔ Backend | REST (Gin), WebSocket (real-time entity events) |
| Runner Authentication | mTLS client certificates issued by Backend PKI |
| Web Authentication | JWT |
| Reverse Proxy | Traefik |

Sources: [README.md:196-208](), [CLAUDE.md:1-15]()

---

## Project Layout

```
AgentsMesh/
├── backend/
│   ├── cmd/server/            # Entry point
│   ├── internal/
│   │   ├── api/rest/          # Gin REST handlers
│   │   ├── api/grpc/          # GRPCRunnerAdapter, GRPCServer
│   │   ├── domain/            # Domain models (agentpod, ticket, channel, runner, ...)
│   │   ├── service/           # Business logic layer
│   │   └── infra/             # DB and cache connections
│   └── migrations/            # golang-migrate SQL files
├── web/src/
│   ├── app/                   # Next.js App Router pages
│   ├── components/            # React components (terminal, kanban, mesh)
│   ├── stores/                # Zustand stores (pod, runner, channel, workspace)
│   └── lib/                   # API clients, URL resolution
├── web-admin/src/             # Admin console (Next.js, basePath: /admin)
├── runner/internal/
│   ├── runner/                # Runner, Pod, PodBuilder, pty_forwarder.go
│   ├── client/                # RPCClient (grpc_connection.go, grpc_registration.go)
│   ├── mcp/                   # HTTPServer, GRPCCollaborationClient
│   ├── terminal/              # PTY management (creack/pty on Unix, ConPTY on Windows)
│   └── workspace/             # Git worktree management
├── relay/                     # ChannelManager, TerminalChannel
├── proto/                     # .proto definitions (runner/v1)
└── deploy/
    ├── dev/                   # Docker Compose dev stack (dev.sh)
    └── selfhost/              # On-premise deployment files
```

Sources: [README.md:210-224](), [CLAUDE.md:174-271]()

---

## Quick Start

```bash
git clone https://github.com/AgentsMesh/AgentsMesh.git
cd AgentsMesh/deploy/dev
./dev.sh
```

`dev.sh` generates a port-isolated `.env` (supporting multiple Git worktrees simultaneously), starts PostgreSQL, Redis, MinIO, Gitea, Backend, Runner, Relay, and Traefik via Docker Compose, runs database migrations, seeds test data, and starts the Next.js frontend locally with Turbopack. See [Development Environment](#7) and [Docker Compose Services](#7.1) for a complete walkthrough.

| Service | Default URL |
|---------|------------|
| Web Console | http://localhost:3000 |
| API (via Traefik) | http://localhost:80/api |
| Traefik Dashboard | http://localhost:8080 |
| Adminer (DB UI) | http://localhost:8081 |
| MinIO Console | http://localhost:9001 |

| Account | Email | Password |
|---------|-------|---------|
| User | `dev@agentsmesh.local` | `devpass123` |
| Admin | `admin@agentsmesh.local` | `adminpass123` |

Sources: [README.md:118-143](), [deploy/dev/docker-compose.yml:1-50](), [deploy/dev/seed/seed.sql:30-65]()

---

# Page: Architecture

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude/skills/gh-merge/SKILL.md](.claude/skills/gh-merge/SKILL.md)
- [.claude/skills/worktree/SKILL.md](.claude/skills/worktree/SKILL.md)
- [CLAUDE.md](CLAUDE.md)
- [README.md](README.md)
- [backend/cmd/server/eventbus_relay.go](backend/cmd/server/eventbus_relay.go)
- [backend/cmd/server/main.go](backend/cmd/server/main.go)
- [backend/internal/api/grpc/command_sender_adapter.go](backend/internal/api/grpc/command_sender_adapter.go)
- [backend/internal/api/grpc/runner_adapter_mcp.go](backend/internal/api/grpc/runner_adapter_mcp.go)
- [backend/internal/api/grpc/runner_adapter_mcp_ticket.go](backend/internal/api/grpc/runner_adapter_mcp_ticket.go)
- [backend/internal/api/grpc/runner_adapter_send.go](backend/internal/api/grpc/runner_adapter_send.go)
- [backend/internal/api/grpc/runner_adapter_send_extra_test.go](backend/internal/api/grpc/runner_adapter_send_extra_test.go)
- [backend/internal/api/grpc/runner_adapter_test.go](backend/internal/api/grpc/runner_adapter_test.go)
- [backend/internal/api/rest/v1/pod_terminal_connect.go](backend/internal/api/rest/v1/pod_terminal_connect.go)
- [backend/internal/service/runner/command_sender.go](backend/internal/service/runner/command_sender.go)
- [backend/internal/service/runner/command_sender_test.go](backend/internal/service/runner/command_sender_test.go)
- [backend/internal/service/runner/connection_manager.go](backend/internal/service/runner/connection_manager.go)
- [backend/internal/service/runner/test_helper_test.go](backend/internal/service/runner/test_helper_test.go)
- [backend/internal/service/ticket/ticket_query.go](backend/internal/service/ticket/ticket_query.go)
- [backend/internal/service/ticket/ticket_query_test.go](backend/internal/service/ticket/ticket_query_test.go)
- [deploy/dev/.gitignore](deploy/dev/.gitignore)
- [deploy/dev/backend.Dockerfile](deploy/dev/backend.Dockerfile)
- [deploy/dev/docker-compose.yml](deploy/dev/docker-compose.yml)
- [deploy/dev/init-seed.sh](deploy/dev/init-seed.sh)
- [deploy/dev/nginx/conf.d/default.conf](deploy/dev/nginx/conf.d/default.conf)
- [deploy/dev/nginx/nginx.conf](deploy/dev/nginx/nginx.conf)
- [deploy/dev/runner-entrypoint.sh](deploy/dev/runner-entrypoint.sh)
- [deploy/dev/runner.Dockerfile](deploy/dev/runner.Dockerfile)
- [deploy/dev/seed/seed.sql](deploy/dev/seed/seed.sql)
- [deploy/dev/traefik/dynamic/grpc.yml](deploy/dev/traefik/dynamic/grpc.yml)
- [deploy/dev/web.Dockerfile](deploy/dev/web.Dockerfile)
- [docs/images/architecture.svg](docs/images/architecture.svg)
- [proto/gen/go/runner/v1/runner.pb.go](proto/gen/go/runner/v1/runner.pb.go)
- [proto/runner/v1/runner.proto](proto/runner/v1/runner.proto)
- [runner/internal/client/grpc_handler.go](runner/internal/client/grpc_handler.go)
- [runner/internal/client/interface.go](runner/internal/client/interface.go)
- [runner/internal/client/protocol.go](runner/internal/client/protocol.go)
- [runner/internal/mcp/grpc_client.go](runner/internal/mcp/grpc_client.go)
- [runner/internal/mcp/http_server.go](runner/internal/mcp/http_server.go)
- [runner/internal/mcp/http_tools_format_integration_test.go](runner/internal/mcp/http_tools_format_integration_test.go)
- [runner/internal/mcp/http_tools_ticket.go](runner/internal/mcp/http_tools_ticket.go)
- [runner/internal/mcp/tools/types_client.go](runner/internal/mcp/tools/types_client.go)
- [runner/internal/mcp/tools/types_entity.go](runner/internal/mcp/tools/types_entity.go)
- [runner/internal/relay/client_token_test.go](runner/internal/relay/client_token_test.go)
- [runner/internal/runner/message_handler.go](runner/internal/runner/message_handler.go)
- [runner/internal/runner/message_handler_pod_create_test.go](runner/internal/runner/message_handler_pod_create_test.go)
- [runner/internal/runner/message_handler_relay.go](runner/internal/runner/message_handler_relay.go)
- [web/src/components/ui/block-editor.tsx](web/src/components/ui/block-editor.tsx)
- [web/src/lib/api/base.ts](web/src/lib/api/base.ts)

</details>



This page describes the system-level architecture of AgentsMesh: how the four main services (Backend, Runner, Relay, Web) are decomposed, which protocols connect them, and how data flows through the system at runtime. For definitions of domain concepts (Pod, Channel, Ticket, Binding), see [Core Concepts](#1.2). For deployment-specific topology, see [Deployment](#8).

---

## Control Plane vs. Data Plane

AgentsMesh separates two distinct communication concerns:

| Plane | Purpose | Protocol | Transport |
|---|---|---|---|
| **Control Plane** | Orchestration commands, lifecycle events, MCP RPC | gRPC bidirectional stream | mTLS (port 9443) |
| **Data Plane** | Terminal I/O (PTY bytes) | WebSocket pub/sub | Relay cluster (port 80/path `/relay`) |
| **API Plane** | User-facing REST, real-time entity events | HTTP + WebSocket | HTTP (port 80/path `/api`) |

This split ensures that raw terminal output—which is high-frequency binary data—never passes through the Backend, keeping Backend stateless with respect to terminal content.

> Terminal output is **exclusively** streamed via Relay. The comment in [runner/internal/client/protocol.go:16-17]() states: `MsgTypeTerminalOutput removed - terminal output is exclusively streamed via Relay`.

---

## Component Topology

**Component overview and their relationships:**

```mermaid
graph TD
    subgraph "User-Facing"
        Browser["Browser"]
        Web["Web (Next.js)"]
        WebAdmin["Web-Admin (Next.js)"]
    end

    subgraph "SaaS / On-Prem Hosted"
        Traefik["Traefik (reverse proxy)"]
        Backend["Backend\ncmd/server/main.go"]
        Relay["Relay\nport :8090"]
    end

    subgraph "Self-Hosted (User Infrastructure)"
        Runner["Runner\nGo daemon"]
        PTY["PTY / AI Agent Process"]
        MCPServer["MCP HTTPServer\n127.0.0.1:{port}"]
    end

    Web --> |"REST /api"| Traefik
    Web --> |"WebSocket events"| Traefik
    WebAdmin --> |"REST /admin"| Traefik
    Browser --> |"WebSocket /relay"| Traefik
    Traefik --> |"HTTP"| Backend
    Traefik --> |"WS strip /relay"| Relay
    Traefik --> |"TLS passthrough :9443"| Backend
    Backend --> |"gRPC + mTLS\nbidirectional stream"| Runner
    Runner --> |"WebSocket publisher"| Relay
    Runner --> PTY
    MCPServer --> |"McpRequest over gRPC stream"| Backend
    PTY --> |"HTTP MCP calls"| MCPServer
```

Sources: [README.md:100-114](), [CLAUDE.md:138-171](), [deploy/dev/docker-compose.yml:384-400]()

---

## Control Plane: gRPC + mTLS

### Protocol Definition

The control channel is defined in [proto/runner/v1/runner.proto]() as a single bidirectional streaming RPC:

```
service RunnerService {
  rpc Connect(stream RunnerMessage) returns (stream ServerMessage);
}
```

All backend-to-runner commands and runner-to-backend events travel over this one persistent stream.

**Runner → Backend (`RunnerMessage` payload types):**

| Message | Purpose |
|---|---|
| `InitializeRequest` | Runner identification on connect |
| `InitializedConfirm` | Reports detected agent types/versions |
| `HeartbeatData` | Pod statuses, relay connection states |
| `PodCreatedEvent` | Pod is live; reports PID and sandbox path |
| `PodTerminatedEvent` | Pod process exited |
| `AgentStatusEvent` | Agent state change: `executing`, `waiting`, `idle` |
| `PodInitProgressEvent` | Progress during clone/prepare phases |
| `RequestRelayTokenEvent` | Runner requests a new relay JWT |
| `SandboxesStatusEvent` | Response to `QuerySandboxesCommand` |
| `McpRequest` | MCP tool call forwarded to backend services |
| `PongEvent` | Downstream heartbeat reply |
| `OSCNotificationEvent` | Desktop notification from terminal (OSC 777/9) |
| `OSCTitleEvent` | Terminal tab title change (OSC 0/2) |

**Backend → Runner (`ServerMessage` payload types):**

| Message | Purpose |
|---|---|
| `CreatePodCommand` | Create isolated PTY sandbox with config |
| `TerminatePodCommand` | Stop a pod |
| `TerminalInputCommand` | Keyboard input for programmatic use |
| `TerminalResizeCommand` | Resize PTY dimensions |
| `TerminalRedrawCommand` | Force terminal state refresh |
| `SubscribeTerminalCommand` | Instruct runner to connect to Relay |
| `UnsubscribeTerminalCommand` | Instruct runner to disconnect from Relay |
| `QuerySandboxesCommand` | Query sandbox filesystem state |
| `McpResponse` | Response to a `McpRequest` |
| `PingCommand` | Downstream liveness probe |
| `CreateAutopilotCommand` | Start an Autopilot controller |
| `AutopilotControlCommand` | Pause/resume/stop Autopilot |

Sources: [proto/runner/v1/runner.proto:1-586]()

### Backend-Side Control Plane Components

**Control plane component relationships on the backend:**

```mermaid
graph LR
    GRPCServer["grpcserver.Server\napi/grpc/server.go"] --> RunnerConnMgr["RunnerConnectionManager\nservice/runner/connection_manager.go"]
    GRPCServer --> RunnerAdapter["GRPCRunnerAdapter\napi/grpc/runner_adapter_*.go"]
    RunnerAdapter --> RunnerConnMgr
    CmdSender["GRPCCommandSender\napi/grpc/command_sender_adapter.go"] --> RunnerAdapter
    PodCoordinator["PodCoordinator\nservice/agentpod/"] --> CmdSender
    TerminalRouter["TerminalRouter\nservice/runner/"] --> CmdSender
    RunnerConnMgr --> GRPCConn["grpcConnectionShard\nconnection_manager.go"]
```

- **`RunnerConnectionManager`** ([backend/internal/service/runner/connection_manager.go]()): Stores live gRPC stream handles in 256 shards to reduce lock contention. Fires event callbacks (`onHeartbeat`, `onPodCreated`, etc.) when runner messages arrive.
- **`GRPCRunnerAdapter`** ([backend/internal/api/grpc/runner_adapter_send.go]()): Knows how to wrap commands into `ServerMessage` protos and deliver them via `RunnerConnectionManager.GetConnection(runnerID)`.
- **`GRPCCommandSender`** ([backend/internal/api/grpc/command_sender_adapter.go]()): Thin adapter that implements the `runner.RunnerCommandSender` interface so `PodCoordinator` and `TerminalRouter` can call gRPC without depending on the `grpc` package directly.

### Runner-Side Control Plane Components

**Control plane components on the runner side:**

```mermaid
graph LR
    GRPCConn["GRPCConnection\nclient/grpc_connection.go"] --> |"readLoop"| Handler["GRPCConnection.handleServerMessage\nclient/grpc_handler.go"]
    Handler --> |"OnCreatePod\nOnTerminatePod\nOnTerminalInput\nOnSubscribeTerminal..."| MsgHandler["RunnerMessageHandler\nrunner/message_handler.go"]
    MsgHandler --> PodStore["PodStore\nrunner/pod_store.go"]
    MsgHandler --> RelayHandler["message_handler_relay.go\nOnSubscribeTerminal"]
    GRPCConn --> RPCClient["RPCClient\nclient/rpc_client.go"]
    RPCClient --> |"McpRequest/McpResponse"| GRPCConn
```

- **`GRPCConnection`** (`runner/internal/client/`): Manages the bidirectional stream, reconnection with backoff, heartbeat ticker, and a write queue. Dispatches incoming messages in `handleServerMessage`.
- **`RunnerMessageHandler`** ([runner/internal/runner/message_handler.go]()): Implements `client.MessageHandler`. Routes each incoming command to pod lifecycle operations (build, start, stop terminal, relay subscribe/unsubscribe).
- **`RPCClient`**: Handles `McpRequest`/`McpResponse` correlation over the gRPC stream using UUID request IDs.

The `client.MessageHandler` interface ([runner/internal/client/protocol.go:107-138]()) defines the contract between the stream layer and the pod operations layer.

---

## Data Plane: WebSocket Terminal Streaming

### Relay Architecture

The Relay is a lightweight WebSocket pub/sub server. Each pod maps to a **channel** identified by its `pod_key`. The Runner is the **publisher** and browsers are **subscribers**.

**Terminal streaming sequence:**

```mermaid
sequenceDiagram
    participant Browser
    participant Backend
    participant Relay
    participant Runner
    participant PTY

    Browser->>Backend: "POST /api/v1/pods/{key}/terminal/connect"
    Note over Backend: "TerminalConnectHandler\npicks relay from relay.Manager\ngenerates JWT via relay.TokenGenerator"
    Backend->>Runner: "gRPC: SubscribeTerminalCommand\n(relay_url, runner_token, pod_key)"
    Runner->>Relay: "WebSocket connect as publisher\n(pod_key channel)"
    Browser->>Relay: "WebSocket connect as subscriber\n(JWT auth)"
    PTY-->>Runner: "PTY output bytes"
    Runner-->>Relay: "WebSocket: output frame"
    Relay-->>Browser: "WebSocket: output frame"
    Browser->>Relay: "WebSocket: input / resize"
    Relay->>Runner: "WebSocket: input / resize"
    Runner->>PTY: "write to PTY stdin"
```

Sources: [backend/internal/api/rest/v1/pod_terminal_connect.go](), [runner/internal/runner/message_handler_relay.go:19-100](), [deploy/dev/docker-compose.yml:321-382]()

### Runner Relay Client

When `OnSubscribeTerminal` fires ([runner/internal/runner/message_handler_relay.go:19-99]()), the runner:

1. Creates `relay.NewClient` with the provided relay URL and JWT token.
2. Sets a **fallback public relay URL** for local runners that cannot resolve Docker-internal hostnames (e.g. `ws://relay:8090` vs `ws://host:port/relay`).
3. Registers handlers:
   - `SetInputHandler` → writes to `pod.Terminal`
   - `SetResizeHandler` → resizes PTY
   - `SetImagePasteHandler` → writes image to clipboard backend, injects Ctrl+V
   - `SetTokenExpiredHandler` → sends `RequestRelayTokenEvent` over gRPC to get a fresh JWT
   - `SetReconnectHandler` → re-attaches relay output and sends terminal snapshot
4. Calls `pod.Aggregator.SetRelayOutput` to route PTY bytes to the relay connection.

On reconnect, the runner sends a **terminal snapshot** (full virtual terminal screen state) so late subscribers immediately see current output.

### Relay Token Refresh

When the runner's relay JWT expires mid-session, the flow uses `RequestRelayTokenEvent` over the gRPC control stream ([backend/cmd/server/eventbus_relay.go]()). The backend generates a new token and re-sends `SubscribeTerminalCommand` with it.

---

## MCP over gRPC

AI agents (Claude Code, etc.) communicate with AgentsMesh collaboration features via the **Model Context Protocol (MCP)**. Rather than opening a separate HTTP connection from the runner to the backend, MCP calls are multiplexed over the existing gRPC bidirectional stream.

**MCP call path:**

```mermaid
sequenceDiagram
    participant Agent as "AI Agent Process (Claude Code)"
    participant MCPServer as "mcp.HTTPServer\n(127.0.0.1:{port})"
    participant GRPCClient as "GRPCCollaborationClient\nmcp/grpc_client.go"
    participant RPCClient as "client.RPCClient"
    participant GRPCStream as "GRPCConnection stream"
    participant BackendAdapter as "GRPCRunnerAdapter\napi/grpc/runner_adapter_mcp.go"
    participant Services as "Backend Service Layer"

    Agent->>MCPServer: "HTTP POST /mcp\n{method, args}"
    MCPServer->>GRPCClient: "tool handler(args)"
    GRPCClient->>RPCClient: "Call(ctx, podKey, method, params)"
    RPCClient->>GRPCStream: "RunnerMessage{McpRequest{request_id, pod_key, method, payload}}"
    GRPCStream->>BackendAdapter: "handleMcpRequest"
    BackendAdapter->>Services: "dispatch to service layer\n(channel, binding, ticket, pod...)"
    Services-->>BackendAdapter: "result"
    BackendAdapter-->>GRPCStream: "ServerMessage{McpResponse{request_id, payload}}"
    GRPCStream-->>RPCClient: "HandleResponse(resp)"
    RPCClient-->>GRPCClient: "[]byte response"
    GRPCClient-->>MCPServer: "unmarshalled result"
    MCPServer-->>Agent: "HTTP 200 JSON"
```

Sources: [runner/internal/mcp/http_server.go](), [runner/internal/mcp/grpc_client.go](), [backend/internal/api/grpc/runner_adapter_mcp.go]()

The MCP tool categories exposed by `mcp.HTTPServer.registerTools()` ([runner/internal/mcp/http_server.go:222-262]()):

| Category | Tools |
|---|---|
| Terminal | `observe_terminal`, `send_terminal_text`, `send_terminal_key`, `get_pod_status` |
| Discovery | `list_available_pods`, `list_runners`, `list_repositories` |
| Binding | `request_binding`, `accept_binding`, `reject_binding`, `unbind_pod`, `get_bindings`, `get_bound_pods` |
| Channel | `search_channels`, `create_channel`, `get_channel`, `send_message`, `get_messages`, `get_channel_document`, `update_channel_document` |
| Ticket | `search_tickets`, `get_ticket`, `create_ticket`, `update_ticket`, `post_comment` |
| Pod | `create_pod` |

Each pod registers with the MCP server via `HTTPServer.RegisterPod`, which creates a `GRPCCollaborationClient` for that pod's `pod_key`, scoping all tool calls to the correct organization context.

---

## Real-Time Events: EventBus → WebSocket Hub

Backend entity changes (pod state, tickets, channels) are broadcast to connected web clients via a WebSocket hub. The flow is:

```
Service layer → EventBus → Hub → WebSocket → Web (RealtimeProvider)
```

- Services call `SetEventBus` / `SetEventPublisher` during startup ([backend/cmd/server/main.go:63-67]()).
- `EventBus.StartRedisSubscriber` enables fan-out across multiple backend instances ([backend/cmd/server/main.go:70-73]()).
- The `Hub` converts events to JSON frames and sends them to subscribed WebSocket connections.
- On the frontend, `RealtimeProvider` dispatches events to Zustand stores (see [Real-time State Management](#5.5)).

---

## PKI and mTLS

Runners authenticate to the backend using **mutual TLS**. The backend operates a Certificate Authority (CA). During runner registration:

1. Runner generates a key pair and sends a CSR.
2. Backend issues a signed certificate (configurable validity, default 365 days via `PKI_VALIDITY_DAYS`).
3. Runner stores the certificate locally and presents it on every gRPC connect.
4. The gRPC server enforces client certificate validation on port 9443.

If `PKI_CA_CERT_FILE` and `PKI_CA_KEY_FILE` are not set, the gRPC server does not start and a `NoOpCommandSender` is used instead ([backend/cmd/server/main.go:134-158]()). For full PKI details, see [PKI and mTLS](#2.8).

---

## Network Ports and Endpoints

| Service | Internal Address | External (via Traefik) | Protocol |
|---|---|---|---|
| Backend REST | `:8080` | `{domain}/api`, `{domain}/health` | HTTP |
| Backend gRPC | `:9090` | `{domain}:9443` (TLS passthrough) | gRPC+mTLS |
| Relay | `:8090` | `{domain}/relay` (prefix stripped) | WebSocket |
| Runner MCP | `127.0.0.1:{dynamic}` | Not exposed externally | HTTP (loopback) |
| PostgreSQL | `:5432` | Not exposed | TCP |
| Redis | `:6379` | Not exposed | TCP |
| MinIO | `:9000` | Not exposed (presigned URLs) | HTTP |

Sources: [deploy/dev/docker-compose.yml:109-400](), [CLAUDE.md:34-48]()

The `PRIMARY_DOMAIN` and `USE_HTTPS` environment variables are the single source of truth for URL construction. All components (Backend, Relay, Web, Web-Admin) derive their public URLs from these two values. For the full configuration model, see [Configuration](#2.7).

---

## Pod Creation Data Flow

**End-to-end pod creation sequence:**

```mermaid
sequenceDiagram
    participant Web
    participant Backend
    participant RunnerConnMgr as "RunnerConnectionManager"
    participant GRPCCmdSender as "GRPCCommandSender"
    participant Runner
    participant PTY

    Web->>Backend: "POST /api/v1/pods\n(runner_id, agent_type, repo, prompt)"
    Note over Backend: "PodOrchestrator.CreatePod\nbuild CreatePodCommand proto"
    Backend->>GRPCCmdSender: "SendCreatePod(runnerID, CreatePodCommand)"
    GRPCCmdSender->>RunnerConnMgr: "GetConnection(runnerID)"
    RunnerConnMgr-->>GRPCCmdSender: "grpcConnectionShard"
    GRPCCmdSender->>Runner: "gRPC: ServerMessage{CreatePodCommand}"
    Note over Runner: "RunnerMessageHandler.OnCreatePod\nPodBuilder: clone git, create sandbox\nstart PTY process"
    Runner->>PTY: "fork AI agent process"
    Runner->>Backend: "gRPC: RunnerMessage{PodCreatedEvent}\n(pod_key, pid, sandbox_path, branch)"
    Note over Backend: "RunnerConnectionManager.onPodCreated callback\npersist pod status to DB\nfire event on EventBus"
    Backend-->>Web: "WebSocket event: pod.created"
```

Sources: [backend/cmd/server/main.go:98-110](), [runner/internal/runner/message_handler.go:32-157](), [backend/internal/api/grpc/command_sender_adapter.go]()

---

# Page: Core Concepts

# Core Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [backend/internal/api/grpc/runner_adapter_mcp.go](backend/internal/api/grpc/runner_adapter_mcp.go)
- [backend/internal/api/grpc/runner_adapter_mcp_ticket.go](backend/internal/api/grpc/runner_adapter_mcp_ticket.go)
- [backend/internal/service/mesh/service.go](backend/internal/service/mesh/service.go)
- [backend/internal/service/ticket/ticket_query.go](backend/internal/service/ticket/ticket_query.go)
- [backend/internal/service/ticket/ticket_query_test.go](backend/internal/service/ticket/ticket_query_test.go)
- [docs/images/architecture.svg](docs/images/architecture.svg)
- [runner/internal/mcp/grpc_client.go](runner/internal/mcp/grpc_client.go)
- [runner/internal/mcp/http_server.go](runner/internal/mcp/http_server.go)
- [runner/internal/mcp/http_tools_format_integration_test.go](runner/internal/mcp/http_tools_format_integration_test.go)
- [runner/internal/mcp/http_tools_ticket.go](runner/internal/mcp/http_tools_ticket.go)
- [runner/internal/mcp/tools/types_client.go](runner/internal/mcp/tools/types_client.go)
- [runner/internal/mcp/tools/types_entity.go](runner/internal/mcp/tools/types_entity.go)
- [web/src/components/landing/PricingSection.tsx](web/src/components/landing/PricingSection.tsx)
- [web/src/lib/api/pod.ts](web/src/lib/api/pod.ts)
- [web/src/messages/de/app.json](web/src/messages/de/app.json)
- [web/src/messages/de/landing.json](web/src/messages/de/landing.json)
- [web/src/messages/en/app.json](web/src/messages/en/app.json)
- [web/src/messages/en/landing.json](web/src/messages/en/landing.json)
- [web/src/messages/es/app.json](web/src/messages/es/app.json)
- [web/src/messages/es/landing.json](web/src/messages/es/landing.json)
- [web/src/messages/fr/app.json](web/src/messages/fr/app.json)
- [web/src/messages/fr/landing.json](web/src/messages/fr/landing.json)
- [web/src/messages/ja/app.json](web/src/messages/ja/app.json)
- [web/src/messages/ja/landing.json](web/src/messages/ja/landing.json)
- [web/src/messages/ko/app.json](web/src/messages/ko/app.json)
- [web/src/messages/ko/landing.json](web/src/messages/ko/landing.json)
- [web/src/messages/pt/app.json](web/src/messages/pt/app.json)
- [web/src/messages/pt/landing.json](web/src/messages/pt/landing.json)
- [web/src/messages/zh/app.json](web/src/messages/zh/app.json)
- [web/src/messages/zh/landing.json](web/src/messages/zh/landing.json)

</details>



This page defines the primary terminology used throughout the AgentsMesh codebase and documentation. Understanding these concepts is necessary before reading any of the component-specific pages. For system architecture and how components communicate, see [Architecture](#1.1). For deployment-specific configuration, see [Configuration](#2.7).

---

## Concept Overview

AgentsMesh organizes work around three layers: **infrastructure** (Runners, Relay), **execution** (Pods, Sandboxes, Workspaces), and **collaboration** (Channels, Bindings, MCP, Tickets).

**Concept map: terms to code entities**

```mermaid
graph TD
    subgraph "Infrastructure Layer"
        Runner["Runner\n(runner/ binary)"]
        Relay["Relay\n(relay/ service)"]
        Backend["Backend\n(backend/ service)"]
    end

    subgraph "Execution Layer"
        Pod["Pod / AgentPod\n(PodData in web/src/lib/api/pod.ts)"]
        Sandbox["Sandbox\n(sandbox_path on PodData)"]
        Workspace["Workspace\n(Git worktree on Runner host)"]
    end

    subgraph "Collaboration Layer"
        Channel["Channel\n(tools.Channel)"]
        Binding["Binding\n(tools.Binding)"]
        MCP["MCP Server\n(mcp.HTTPServer)"]
        Ticket["Ticket\n(ticketDomain.Ticket)"]
    end

    Runner -->|"hosts"| Pod
    Pod -->|"runs in"| Sandbox
    Pod -->|"uses"| Workspace
    Pod -->|"registered with"| MCP
    MCP -->|"exposes"| Channel
    MCP -->|"exposes"| Binding
    MCP -->|"exposes"| Ticket
    Runner -->|"gRPC+mTLS"| Backend
    Runner -->|"WebSocket"| Relay
    Relay -->|"WebSocket"| Browser["Browser / Web Client"]
```

Sources: [runner/internal/mcp/http_server.go:36-57](), [web/src/lib/api/pod.ts:4-45](), [README.md:108-114]()

---

## Infrastructure Concepts

### Runner

The Runner is a self-hosted Go daemon (binary: `agentsmesh-runner`) installed on user-controlled infrastructure. It is the **only component that directly executes AI agents**. Code never passes through AgentsMesh cloud servers.

Key responsibilities:
- Maintains a persistent bidirectional gRPC stream to the Backend (authenticated with mTLS client certificates).
- Connects to the Relay cluster over WebSocket to stream terminal I/O.
- Manages Pod lifecycle: spawning PTY processes, streaming output, handling resize.
- Hosts a local MCP HTTP server (`mcp.HTTPServer`) that AI agents call to use collaboration tools.

For installation and registration details, see [Installation and Registration](#3.1). For the gRPC client internals, see [gRPC Client](#3.3).

### Relay

The Relay is a stateless WebSocket intermediary. It decouples terminal I/O from the Backend control plane. The Runner publishes terminal output to the Relay; browser clients subscribe.

The Relay manages **TerminalChannels** identified by `pod_key`. Multiple browser tabs can subscribe to the same channel. For channel/session management details, see [Channel and Session Management](#4.1).

### Backend

The Backend is the central Go API server. It holds authoritative state in PostgreSQL and Redis. It does not run AI agents itself; instead, it dispatches commands to Runners via gRPC and forwards MCP method calls back through the open stream.

---

## Execution Concepts

### Pod (AgentPod)

A **Pod** (also called **AgentPod**) is the primary unit of work in AgentsMesh. It represents a single running AI agent session on a specific Runner.

Each Pod has:
- A unique `pod_key` (string identifier used across all services).
- A `status` field tracking its lifecycle state.
- An associated `agent_type` (e.g., Claude Code, Codex CLI).
- An optional `repository` and `branch_name` for Git worktree isolation.
- An optional `ticket` association.
- An optional `sandbox_path` pointing to the working directory on the Runner host.

**Pod status lifecycle**

```mermaid
stateDiagram-v2
    [*] --> initializing : "create pod"
    initializing --> running : "Runner reports ready"
    running --> paused : "user pause"
    running --> disconnected : "Runner disconnects"
    running --> terminated : "user terminate"
    running --> completed : "agent exits 0"
    running --> error : "agent exits non-zero"
    disconnected --> running : "Runner reconnects"
    disconnected --> orphaned : "timeout"
    paused --> running : "user resume"
    terminated --> [*]
    completed --> [*]
    error --> [*]
    orphaned --> [*]
    failed --> [*]
```

Sources: [web/src/lib/api/pod.ts:7-7](), [web/src/messages/en/app.json:20-31]()

The `PodData` interface in `web/src/lib/api/pod.ts` is the canonical frontend representation. The equivalent backend domain object lives in `backend/internal/domain/`.

| Field | Type | Description |
|---|---|---|
| `pod_key` | string | Unique identifier, used as routing key in Relay and MCP |
| `status` | enum | Lifecycle state (see diagram above) |
| `agent_status` | string | Fine-grained agent state (`idle`, `executing`, `waiting`) |
| `sandbox_path` | string | Absolute path to working directory on Runner host |
| `branch_name` | string | Git branch for this pod's worktree |
| `runner` | object | The Runner hosting this pod |
| `agent_type` | object | The AI agent type (slug, name) |
| `ticket` | object | Optional linked ticket |

### Sandbox

The **Sandbox** is the isolated filesystem directory on the Runner host where a Pod operates. Its path is stored as `sandbox_path` on `PodData`. Each Pod gets its own directory, preventing filesystem collisions between concurrent agents.

The sandbox contains the Git worktree checked out for the Pod's branch. When a Pod terminates, the sandbox may be retained for session resumption (see `source_pod_key` and `resume_agent_session` in [web/src/lib/api/pod.ts:62-83]()).

### Workspace

A **Workspace** refers to the Git worktree created for a Pod inside its sandbox. When a Pod is created with a `repository_id` or `repository_url`, the Runner clones a bare repository and creates a named worktree on the Pod's branch. This gives each Pod an independent view of the codebase with no shared index files.

For implementation details on worktree creation and Git authentication, see [Workspace and Git Management](#3.7).

---

## Collaboration Concepts

### AgentsMesh (the feature)

**AgentsMesh** (lowercase "mesh" in code) refers specifically to the multi-agent collaboration feature set, as distinct from the product name. It encompasses the topology of running pods, their bindings, and the channels they communicate through. The web frontend exposes this as the **Mesh** page (`mesh` namespace in i18n files).

### MCP (Model Context Protocol)

**MCP** in this codebase refers to the HTTP server (`mcp.HTTPServer`) that runs locally on each Runner. AI agents (e.g., Claude Code) call this server to use collaboration tools. The server listens on `localhost:<port>/mcp` and implements a JSON-RPC style protocol.

**MCP tool categories and their implementations**

```mermaid
graph LR
    Agent["AI Agent\n(Claude Code, etc.)"] -->|"HTTP POST /mcp"| MCPServer["mcp.HTTPServer\n(runner/internal/mcp/http_server.go)"]

    MCPServer --> TermTools["Terminal Tools\nobserve_terminal\nsend_terminal_text\nsend_terminal_key\nget_pod_status"]
    MCPServer --> DiscoveryTools["Discovery Tools\nlist_available_pods\nlist_runners\nlist_repositories"]
    MCPServer --> BindingTools["Binding Tools\nrequest_binding\naccept_binding\nreject_binding\nunbind_pod\nget_bindings"]
    MCPServer --> ChannelTools["Channel Tools\nsearch_channels\ncreate_channel\nsend_message\nget_messages\nget_document\nupdate_document"]
    MCPServer --> TicketTools["Ticket Tools\nsearch_tickets\nget_ticket\ncreate_ticket\nupdate_ticket\npost_comment"]
    MCPServer --> PodTools["Pod Tools\ncreate_pod"]

    MCPServer -->|"serializes to gRPC"| GRPCClient["GRPCCollaborationClient\n(mcp/grpc_client.go)"]
    GRPCClient -->|"McpRequest over\nbidirectional stream"| BackendAdapter["GRPCRunnerAdapter\n(backend/internal/api/grpc/)"]
```

Sources: [runner/internal/mcp/http_server.go:222-262](), [runner/internal/mcp/grpc_client.go:16-27](), [backend/internal/api/grpc/runner_adapter_mcp.go]()

Each MCP tool call from the AI agent travels from the local HTTP server → `GRPCCollaborationClient.call()` → `RPCClient.Call()` → gRPC stream → Backend's `GRPCRunnerAdapter` → the relevant backend service. The result returns the same path. This design avoids the Runner needing direct HTTP access to the Backend for MCP operations.

For full MCP server documentation, see [MCP Server](#3.6). For the backend MCP handler, see [MCP and Mesh Service](#2.4).

### Binding

A **Binding** is a directional relationship between two Pods that grants one Pod permission to observe or control another's terminal. Bindings are negotiated: the initiating pod requests a binding, and the target pod (or its agent) accepts or rejects it.

```mermaid
sequenceDiagram
    participant PodA as "Pod A (initiator)"
    participant Backend as "Backend"
    participant PodB as "Pod B (target)"

    PodA->>Backend: "request_binding(target=PodB, scopes=[terminal_read])"
    Backend->>PodB: "notify: binding request from PodA"
    PodB->>Backend: "accept_binding(binding_id)"
    Backend->>PodA: "binding.status = active"
    PodA->>Backend: "observe_terminal(pod_key=PodB)"
    Backend->>PodA: "terminal output"
```

The `tools.Binding` struct ([runner/internal/mcp/tools/types_entity.go]()) has these key fields:

| Field | Description |
|---|---|
| `ID` | Numeric binding ID |
| `InitiatorPod` | `pod_key` of the requesting pod |
| `TargetPod` | `pod_key` of the target pod |
| `Status` | `pending`, `active`, `rejected`, `terminated` |
| `GrantedScopes` | List of `BindingScope` values (e.g., `terminal_read`, `terminal_write`) |

**Binding scopes** control what the initiator may do: read-only observation (`terminal_read`) vs. full control (`terminal_write`).

### Channel

A **Channel** is a named, persistent messaging space that multiple Pods can join. Channels support:
- **Messages**: Text messages with `@mentions` of pods or users.
- **Document**: A single shared markdown/text document per channel that any pod can read or update (`get_document`, `update_document`).
- **Members**: Tracked list of pods currently in the channel.

`tools.Channel` has fields: `ID`, `Name`, `Description`, `MemberCount`, optional `RepositoryID`, optional `TicketSlug` (for channels scoped to a specific ticket).

Channels serve as the coordination space in multi-agent workflows: one agent broadcasts a result to a channel; other agents poll `get_messages` to act on it.

For the web UI of channels, see [Channels and Chat](#5.4).

---

## Project Management Concepts

### Ticket

A **Ticket** is a task or issue in the integrated project management system. Tickets use a `slug` format of `<ORG_PREFIX>-<NUMBER>` (e.g., `AM-123`) as their primary human-readable identifier throughout the API and MCP tools.

**Ticket fields:**

| Field | Values / Type | Description |
|---|---|---|
| `slug` | `AM-123` | Human-readable unique ID |
| `status` | `backlog`, `todo`, `in_progress`, `in_review`, `done` | Kanban column |
| `priority` | `urgent`, `high`, `medium`, `low`, `none` | |
| `parent_ticket_slug` | string (optional) | Parent for sub-ticket hierarchies |
| `content` | string (BlockNote JSON) | Rich text description; converted to plain text for MCP |

Agents interact with tickets through MCP tools (`search_tickets`, `get_ticket`, `create_ticket`, `update_ticket`, `post_comment`). The backend converts BlockNote JSON content to plain text before sending it to agents, with line-range pagination controlled by `content_offset` and `content_limit` parameters. See `enrichTicketForMCP` in [backend/internal/api/grpc/runner_adapter_mcp_ticket.go:35-87]().

Tickets can be linked to Pods: when a Pod is created with a `ticket_slug`, the ticket's content becomes the agent's initial context. For the ticket service, see [Ticket Service](#2.5). For the web UI, see [Ticket Management](#5.2).

---

## Organizational Concepts

### Organization and Tenant

All resources (Runners, Pods, Tickets, Channels, Repositories) belong to an **Organization**. The organization is identified by its `slug` (e.g., `my-org`). REST API routes are prefixed with `/api/orgs/:org_slug/` to enforce row-level isolation.

The tenant context (`middleware.TenantContext`) is attached to every authenticated request and carries `OrganizationID`, `UserID`, and `UserRole`.

---

## Concept Relationships

The following diagram shows how the primary runtime entities relate to each other during normal operation.

**Runtime entity relationships**

```mermaid
erDiagram
    ORGANIZATION ||--o{ RUNNER : "registers"
    ORGANIZATION ||--o{ TICKET : "owns"
    ORGANIZATION ||--o{ CHANNEL : "owns"
    ORGANIZATION ||--o{ REPOSITORY : "configures"

    RUNNER ||--o{ POD : "hosts"

    POD }o--|| RUNNER : "runs on"
    POD }o--o| TICKET : "linked to"
    POD }o--o| REPOSITORY : "uses"
    POD ||--o| WORKSPACE : "has"
    POD ||--o| SANDBOX : "has"

    POD ||--o{ BINDING : "initiates"
    POD ||--o{ BINDING : "receives"

    POD }o--o{ CHANNEL : "joins"
    CHANNEL ||--o{ CHANNEL_MESSAGE : "contains"
    CHANNEL ||--o| CHANNEL_DOCUMENT : "has"
```

Sources: [web/src/lib/api/pod.ts:4-45](), [runner/internal/mcp/tools/types_entity.go](), [runner/internal/mcp/grpc_client.go:134-212]()

---

## Quick Reference

| Term | Code Symbol | Where Defined |
|---|---|---|
| Pod / AgentPod | `PodData`, `pod_key` | `web/src/lib/api/pod.ts` |
| Runner | `agentsmesh-runner` binary | `runner/` |
| Relay | Relay service | `relay/` |
| Sandbox | `sandbox_path` on `PodData` | `web/src/lib/api/pod.ts:13` |
| Workspace | Git worktree | `runner/internal/workspace/` |
| MCP Server | `mcp.HTTPServer` | `runner/internal/mcp/http_server.go` |
| MCP Collaboration Client | `GRPCCollaborationClient` | `runner/internal/mcp/grpc_client.go` |
| Binding | `tools.Binding` | `runner/internal/mcp/tools/types_entity.go` |
| Channel | `tools.Channel` | `runner/internal/mcp/tools/types_entity.go` |
| Ticket | `ticketDomain.Ticket` | `backend/internal/domain/ticket/` |
| Ticket slug | `AM-123` format | `backend/internal/api/grpc/runner_adapter_mcp_ticket.go` |
| Tenant context | `middleware.TenantContext` | `backend/internal/middleware/` |

---

# Page: Backend

# Backend

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude/skills/worktree/SKILL.md](.claude/skills/worktree/SKILL.md)
- [CLAUDE.md](CLAUDE.md)
- [backend/cmd/server/eventbus_relay.go](backend/cmd/server/eventbus_relay.go)
- [backend/cmd/server/main.go](backend/cmd/server/main.go)
- [backend/internal/api/grpc/command_sender_adapter.go](backend/internal/api/grpc/command_sender_adapter.go)
- [backend/internal/api/grpc/runner_adapter_send.go](backend/internal/api/grpc/runner_adapter_send.go)
- [backend/internal/api/grpc/runner_adapter_send_extra_test.go](backend/internal/api/grpc/runner_adapter_send_extra_test.go)
- [backend/internal/api/rest/internal/relay_registration.go](backend/internal/api/rest/internal/relay_registration.go)
- [backend/internal/api/rest/internal/relay_registration_test.go](backend/internal/api/rest/internal/relay_registration_test.go)
- [backend/internal/api/rest/v1/pod_terminal_connect.go](backend/internal/api/rest/v1/pod_terminal_connect.go)
- [backend/internal/config/config.go](backend/internal/config/config.go)
- [backend/internal/config/config_relay.go](backend/internal/config/config_relay.go)
- [backend/internal/service/relay/dns_service.go](backend/internal/service/relay/dns_service.go)
- [backend/internal/service/relay/dns_service_mock_test.go](backend/internal/service/relay/dns_service_mock_test.go)
- [backend/internal/service/relay/dns_service_sanitize_test.go](backend/internal/service/relay/dns_service_sanitize_test.go)
- [backend/internal/service/runner/command_sender.go](backend/internal/service/runner/command_sender.go)
- [backend/internal/service/runner/command_sender_test.go](backend/internal/service/runner/command_sender_test.go)
- [backend/internal/service/runner/test_helper_test.go](backend/internal/service/runner/test_helper_test.go)
- [backend/migrations/000033_move_preparation_script_to_repository.down.sql](backend/migrations/000033_move_preparation_script_to_repository.down.sql)
- [backend/migrations/000033_move_preparation_script_to_repository.up.sql](backend/migrations/000033_move_preparation_script_to_repository.up.sql)
- [deploy/dev/.gitignore](deploy/dev/.gitignore)
- [deploy/dev/backend.Dockerfile](deploy/dev/backend.Dockerfile)
- [deploy/dev/docker-compose.yml](deploy/dev/docker-compose.yml)
- [deploy/dev/init-seed.sh](deploy/dev/init-seed.sh)
- [deploy/dev/nginx/conf.d/default.conf](deploy/dev/nginx/conf.d/default.conf)
- [deploy/dev/nginx/nginx.conf](deploy/dev/nginx/nginx.conf)
- [deploy/dev/runner-entrypoint.sh](deploy/dev/runner-entrypoint.sh)
- [deploy/dev/runner.Dockerfile](deploy/dev/runner.Dockerfile)
- [deploy/dev/seed/seed.sql](deploy/dev/seed/seed.sql)
- [deploy/dev/traefik/dynamic/grpc.yml](deploy/dev/traefik/dynamic/grpc.yml)
- [deploy/dev/web.Dockerfile](deploy/dev/web.Dockerfile)
- [docs/images/logo.svg](docs/images/logo.svg)
- [proto/gen/go/runner/v1/runner.pb.go](proto/gen/go/runner/v1/runner.pb.go)
- [proto/runner/v1/runner.proto](proto/runner/v1/runner.proto)
- [relay/.env.example](relay/.env.example)
- [relay/internal/config/config.go](relay/internal/config/config.go)
- [relay/internal/config/config_test.go](relay/internal/config/config_test.go)
- [runner/internal/client/grpc_handler.go](runner/internal/client/grpc_handler.go)
- [runner/internal/client/protocol.go](runner/internal/client/protocol.go)
- [runner/internal/runner/message_handler_relay.go](runner/internal/runner/message_handler_relay.go)
- [web-admin/.env.example](web-admin/.env.example)
- [web/src/components/ui/block-editor.tsx](web/src/components/ui/block-editor.tsx)
- [web/src/lib/api/base.ts](web/src/lib/api/base.ts)

</details>



This page covers the Go backend server: its role in the overall platform, how it initializes, and the major subsystems it coordinates. For detailed coverage of individual subsystems, see the child pages: [REST API Routes](#2.1), [gRPC API and Runner Communication](#2.2), [Runner Connection Manager](#2.3), [MCP and Mesh Service](#2.4), [Ticket Service](#2.5), [Billing and Subscriptions](#2.6), [Configuration](#2.7), [PKI and mTLS](#2.8), [Object Storage](#2.9), and [Real-time Events and WebSocket](#2.10).

---

## Role

The backend is the **control plane** of AgentsMesh. It is a Go server (Gin + GORM) that:

- Authenticates users and organizations (JWT, OAuth)
- Manages all domain entities: Users, Orgs, Repos, Pods, Tickets, Channels, Runners, Bindings, Loops, etc.
- Issues mTLS certificates to Runners via a built-in PKI
- Maintains persistent bidirectional gRPC streams with each connected Runner
- Dispatches pod lifecycle commands (`create_pod`, `terminate_pod`) and terminal control commands to Runners over gRPC
- Coordinates terminal streaming by instructing Runners to connect to Relay (WebSocket intermediary)
- Broadcasts real-time entity change events to browsers via WebSocket (`Hub` + `EventBus`)
- Manages billing subscriptions and marketplace extensions

The backend does **not** execute agent code directly; that is the responsibility of the [Runner](#3).

Sources: [backend/cmd/server/main.go:1-50](), [CLAUDE.md:135-170]()

---

## Process Entry Point

The server entry point is `backend/cmd/server/main.go`. The `main()` function orchestrates the full initialization sequence in a fixed order.

**Initialization Sequence**

```mermaid
flowchart TD
  A["config.Load()"] --> B["logger.New()"]
  B --> C["database.New()"]
  C --> D["initializeInfrastructure()"]
  D --> E["initializeServices()"]
  E --> F["setupEventBusHub()"]
  F --> G["ticket/pod EventBus publishers"]
  G --> H["eventBus.StartRedisSubscriber()"]
  H --> I["initializeRunnerComponents()"]
  I --> J["relay.NewManager() + relay.NewTokenGenerator()"]
  J --> K["initializeRelayServices()"]
  K --> L["agent.NewCompositeProvider / ConfigBuilder"]
  L --> M["agentpod.NewPodOrchestrator()"]
  M --> N["instance.NewOrgAwarenessService()"]
  N --> O["loop.NewLoopOrchestrator / LoopScheduler"]
  O --> P["initializePKIAndGRPC()"]
  P --> Q["runner.NewVersionChecker()"]
  Q --> R["rest.NewRouter()"]
  R --> S["startHTTPServer()"]
  S --> T["waitForShutdown()"]
```

Sources: [backend/cmd/server/main.go:26-240]()

---

## Subsystem Map

The following diagram maps the major subsystems to their Go packages and the `Services` struct fields that wire them together.

**Backend subsystem to code entity map**

```mermaid
graph TD
  subgraph "REST Layer"
    RestRouter["rest.NewRouter()"]
    V1Handlers["internal/api/rest/v1"]
  end

  subgraph "gRPC Layer"
    GRPCServer["grpcserver.Server"]
    GRPCRunnerAdapter["GRPCRunnerAdapter"]
    GRPCCommandSender["GRPCCommandSender"]
  end

  subgraph "Domain Services"
    PodOrchestrator["agentpod.PodOrchestrator"]
    PodCoordinator["PodCoordinator"]
    TerminalRouter["TerminalRouter"]
    RunnerConnMgr["RunnerConnectionManager"]
    TicketSvc["ticket.Service"]
    ChannelSvc["channel.Service"]
    BillingSvc["billing.Service"]
    MeshSvc["mesh.Service"]
    LoopOrchestrator["loop.LoopOrchestrator"]
  end

  subgraph "Infrastructure"
    DB["database.New() (PostgreSQL)"]
    Redis["redisClient"]
    EventBus["EventBus"]
    Hub["WebSocket Hub"]
    PKI["infra/pki.Service"]
    Storage["S3Storage"]
  end

  subgraph "Relay Coordination"
    RelayManager["relay.Manager"]
    RelayTokenGen["relay.TokenGenerator"]
    RelayDNS["relay.DNSService"]
    ACME["acme.Manager"]
  end

  RestRouter --> V1Handlers
  V1Handlers --> PodOrchestrator
  V1Handlers --> TicketSvc
  V1Handlers --> ChannelSvc
  V1Handlers --> RelayManager

  GRPCServer --> GRPCRunnerAdapter
  GRPCRunnerAdapter --> RunnerConnMgr
  GRPCCommandSender --> GRPCRunnerAdapter

  PodCoordinator --> GRPCCommandSender
  TerminalRouter --> GRPCCommandSender

  PodOrchestrator --> PodCoordinator
  PodOrchestrator --> BillingSvc
  PodOrchestrator --> TicketSvc

  LoopOrchestrator --> PodOrchestrator

  EventBus --> Hub
  EventBus --> Redis

  PKI --> GRPCServer
```

Sources: [backend/cmd/server/main.go:95-215](), [backend/internal/api/grpc/command_sender_adapter.go:1-87](), [backend/internal/service/runner/command_sender.go:1-53]()

---

## Key Structs and Packages

| Struct / Type | Package | Role |
|---|---|---|
| `Config` | `internal/config` | All environment-based config; loaded once at startup |
| `GRPCRunnerAdapter` | `internal/api/grpc` | Sends commands to Runners over gRPC streams |
| `GRPCCommandSender` | `internal/api/grpc` | Adapts `GRPCRunnerAdapter` to `RunnerCommandSender` interface |
| `RunnerConnectionManager` | `internal/service/runner` | Sharded storage of active Runner gRPC streams |
| `PodOrchestrator` | `internal/service/agentpod` | Unified pod creation for REST and MCP paths |
| `PodCoordinator` | `internal/service/agentpod` | Sends pod/terminal commands; routes through `GRPCCommandSender` |
| `TerminalRouter` | `internal/service/runner` | Routes terminal I/O commands to the correct Runner |
| `relay.Manager` | `internal/service/relay` | Tracks registered Relay instances; selects one per pod |
| `relay.TokenGenerator` | `internal/service/relay` | Issues JWT tokens for Runner↔Relay authentication |
| `OrgAwarenessService` | `internal/service/instance` | Tracks which orgs each backend instance serves |
| `LoopOrchestrator` | `internal/service/loop` | Drives automated agent loop scheduling |
| `EventBus` | `internal/infra` | In-process pub/sub; synced across instances via Redis |
| `Hub` | (WebSocket) | Pushes events to connected browser clients |
| `pki.Service` | `internal/infra/pki` | Issues/renews mTLS certificates for Runners |

Sources: [backend/cmd/server/main.go:166-215](), [backend/internal/api/grpc/command_sender_adapter.go:1-87](), [backend/internal/service/runner/command_sender.go:1-53]()

---

## Infrastructure Dependencies

The backend requires three external dependencies at startup:

| Dependency | Default Address | Used For |
|---|---|---|
| PostgreSQL | `DB_HOST:5432` | All persistent domain data (GORM) |
| Redis | `REDIS_HOST:6379` | EventBus cross-instance sync, heartbeat batching, version check cache |
| MinIO (S3) | `STORAGE_ENDPOINT` | File uploads, presigned URLs, skill packages |

Redis is optional: if `REDIS_URL` and `REDIS_HOST` are not set, the EventBus operates in single-instance mode and the `VersionChecker` is disabled. The backend will still start.

Sources: [backend/cmd/server/main.go:48-72](), [backend/internal/config/config.go:62-82]()

---

## Network Ports

| Port | Protocol | Purpose |
|---|---|---|
| `:8080` | HTTP | REST API and WebSocket (Hub) |
| `:9090` | gRPC + mTLS | Runner bidirectional stream (configurable via `GRPC_ADDRESS`) |
| `9443` | TCP (TLS passthrough) | Traefik passthrough to gRPC port in dev |

In development, Traefik exposes port `9443` externally, passing TLS connections through to the backend's gRPC listener on `:9090`. The backend terminates TLS using server certs derived from the PKI CA.

Sources: [backend/internal/config/config.go:194-199](), [deploy/dev/docker-compose.yml:392-397]()

---

## `Services` Container

All initialized services are collected into `v1.Services` and passed to `rest.NewRouter()`. This struct is the single wiring point — handlers reach any service through it.

**Services struct wiring (abridged)**

```mermaid
graph LR
  ServicesStruct["v1.Services"]

  ServicesStruct --> Auth["Auth"]
  ServicesStruct --> Runner["Runner"]
  ServicesStruct --> RunnerConnMgr["RunnerConnMgr"]
  ServicesStruct --> PodCoordinator["PodCoordinator"]
  ServicesStruct --> TerminalRouter["TerminalRouter"]
  ServicesStruct --> PodOrchestrator["PodOrchestrator"]
  ServicesStruct --> Ticket["Ticket"]
  ServicesStruct --> Channel["Channel"]
  ServicesStruct --> Binding["Binding"]
  ServicesStruct --> Mesh["Mesh"]
  ServicesStruct --> Billing["Billing"]
  ServicesStruct --> Hub["Hub"]
  ServicesStruct --> EventBus["EventBus"]
  ServicesStruct --> GRPCRunnerHandler["GRPCRunnerHandler"]
  ServicesStruct --> RelayManager["RelayManager"]
  ServicesStruct --> RelayTokenGenerator["RelayTokenGenerator"]
  ServicesStruct --> VersionChecker["VersionChecker"]
  ServicesStruct --> LoopOrchestrator["LoopOrchestrator"]
```

Sources: [backend/cmd/server/main.go:167-215]()

---

## gRPC and mTLS Conditional Initialization

gRPC is only enabled when `PKI_CA_CERT_FILE` and `PKI_CA_KEY_FILE` are both set. If they are absent, the backend logs a warning and skips gRPC setup; no Runners can connect, but the REST API still serves.

When enabled, `initializePKIAndGRPC()` sets up:
1. `pki.Service` — CA-backed certificate issuance for Runners
2. `grpcserver.Server` — listens on `GRPC_ADDRESS`, requires client mTLS certs
3. `GRPCRunnerAdapter` — routes inbound Runner messages and exposes outbound send methods
4. `GRPCCommandSender` — adapts the adapter to the `RunnerCommandSender` interface used by `PodCoordinator` and `TerminalRouter`

```mermaid
flowchart LR
  subgraph "PKI/gRPC Conditional Block"
    PKI["pki.Service\n(CA cert/key)"] --> GRPCSrv["grpcserver.Server\n(mTLS listener)"]
    GRPCSrv --> Adapter["GRPCRunnerAdapter"]
    Adapter --> Sender["GRPCCommandSender"]
    Sender --> PodCoord["PodCoordinator.SetCommandSender()"]
    Sender --> TermRouter["TerminalRouter.SetCommandSender()"]
  end
```

Sources: [backend/cmd/server/main.go:130-158](), [backend/internal/api/grpc/command_sender_adapter.go:1-87]()

---

## Relay Token Refresh Flow

When a Runner's relay JWT expires mid-session, the Runner sends a `RequestRelayTokenEvent` over the gRPC stream. The backend handles this via `setupRelayTokenRefreshCallback()`:

1. Look up the pod by `pod_key` in the database
2. Verify the requesting Runner owns the pod
3. Generate a new JWT using `relay.TokenGenerator`
4. Send a fresh `SubscribeTerminalCommand` back to the Runner over gRPC

This is wired at startup via `runnerConnMgr.SetRequestRelayTokenCallback(...)` in `backend/cmd/server/eventbus_relay.go`.

Sources: [backend/cmd/server/eventbus_relay.go:1-104](), [backend/internal/api/rest/v1/pod_terminal_connect.go:100-128]()

---

## Graceful Shutdown

`waitForShutdown()` (called at the end of `main()`) listens for OS signals and then stops in order:

1. HTTP server
2. gRPC server
3. EventBus (Redis subscriber)
4. HeartbeatBatcher
5. SubscriptionScheduler
6. LoopScheduler
7. OrgAwarenessService
8. Database connection
9. Redis client

Sources: [backend/cmd/server/main.go:238-239]()

---

## Configuration Overview

All URLs in the backend are derived from two environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `PRIMARY_DOMAIN` | `localhost:10000` | Base domain for all derived URLs (OAuth callbacks, webhook endpoints, relay public URL) |
| `USE_HTTPS` | `false` | Switches all derived URLs between `http`/`https` and `ws`/`wss` |

This pattern is shared across Backend, Relay, Web, and Web-Admin. Individual per-URL overrides are also supported for backward compatibility. For full details see [Configuration](#2.7).

Sources: [backend/internal/config/config.go:29-53]()

---

# Page: REST API Routes

# REST API Routes

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/cmd/server/eventbus_relay.go](backend/cmd/server/eventbus_relay.go)
- [backend/cmd/server/main.go](backend/cmd/server/main.go)
- [backend/internal/api/grpc/command_sender_adapter.go](backend/internal/api/grpc/command_sender_adapter.go)
- [backend/internal/api/grpc/runner_adapter_send.go](backend/internal/api/grpc/runner_adapter_send.go)
- [backend/internal/api/grpc/runner_adapter_send_extra_test.go](backend/internal/api/grpc/runner_adapter_send_extra_test.go)
- [backend/internal/api/rest/router.go](backend/internal/api/rest/router.go)
- [backend/internal/api/rest/v1/pod_terminal_connect.go](backend/internal/api/rest/v1/pod_terminal_connect.go)
- [backend/internal/api/rest/v1/routes.go](backend/internal/api/rest/v1/routes.go)
- [backend/internal/service/runner/command_sender.go](backend/internal/service/runner/command_sender.go)
- [backend/internal/service/runner/command_sender_test.go](backend/internal/service/runner/command_sender_test.go)
- [backend/internal/service/runner/test_helper_test.go](backend/internal/service/runner/test_helper_test.go)
- [proto/gen/go/runner/v1/runner.pb.go](proto/gen/go/runner/v1/runner.pb.go)
- [proto/runner/v1/runner.proto](proto/runner/v1/runner.proto)
- [runner/internal/client/grpc_handler.go](runner/internal/client/grpc_handler.go)
- [runner/internal/client/protocol.go](runner/internal/client/protocol.go)
- [runner/internal/runner/message_handler_relay.go](runner/internal/runner/message_handler_relay.go)
- [web/src/app/(dashboard)/[org]/settings/page.tsx](web/src/app/(dashboard)/[org]/settings/page.tsx)
- [web/src/components/ide/sidebar/SettingsSidebarContent.tsx](web/src/components/ide/sidebar/SettingsSidebarContent.tsx)
- [web/src/components/settings/ThemeSettings.tsx](web/src/components/settings/ThemeSettings.tsx)
- [web/src/components/settings/index.ts](web/src/components/settings/index.ts)
- [web/src/components/tickets/shared/CommentInput.tsx](web/src/components/tickets/shared/CommentInput.tsx)
- [web/src/components/tickets/shared/CommentsList.tsx](web/src/components/tickets/shared/CommentsList.tsx)
- [web/src/lib/api/index.ts](web/src/lib/api/index.ts)

</details>



This page documents the structure of the AgentsMesh backend HTTP API: how the Gin router is constructed, how route groups are organized, what middleware each group applies, and the specific endpoints within each resource category.

For the gRPC API used for bidirectional backend-to-runner communication, see [gRPC API and Runner Communication](#2.2). For the WebSocket event stream, see [Real-time Events and WebSocket](#2.10). For the Admin Console's own API client, see [Web Admin](#6).

---

## Router Construction

The entry point is `NewRouter` in [backend/internal/api/rest/router.go:23-197](). It receives the application configuration (`*config.Config`), a fully populated `*v1.Services` container, the database handle, and a logger. It returns a configured `*gin.Engine`.

The function performs the following in order:
1. Sets Gin to release mode unless `cfg.Server.Debug` is true.
2. Installs a logger and panic-recovery middleware with structured logging.
3. Configures CORS using `cfg.Server.CORSAllowedOrigins`. Allowed headers include `Authorization`, `X-Organization-Slug`, and `X-API-Key`.
4. Registers health check routes at the root.
5. Builds the `/api/v1` route group and registers all sub-groups.
6. Conditionally registers the Admin Console and Internal Relay API at the root-level router.

The `v1.Services` struct (assembled in [backend/cmd/server/main.go:167-215]()) is the single dependency container passed to all route registration functions.

Sources: [backend/internal/api/rest/router.go:23-197](), [backend/cmd/server/main.go:167-215]()

---

## Route Group Overview

**Route Group and Middleware Hierarchy**

```mermaid
graph TD
    GE["GinEngine r"] --> H["GET /health, GET /health/ready"]
    GE --> V1["apiV1: Group('/api/v1')"]

    V1 --> AUTH_H["AuthHandler: /auth/*"]
    V1 --> CFG_H["RegisterPublicConfigRoutes: /config"]
    V1 --> GRPC_H["RegisterGRPCRunnerRoutes (runner CLI registration)"]
    V1 --> WH_H["WebhookRouter: /webhooks/*"]
    V1 --> INV_H["InvitationHandler: token-based /invitations/*"]

    V1 --> PROT["protected: Use(AuthMiddleware(JWT))"]
    PROT --> USR_H["RegisterUserRoutes: /users/*"]
    PROT --> ORG_H["RegisterOrganizationRoutes: /orgs/*"]
    PROT --> SUP_H["SupportTicketHandler: /support-tickets/*"]
    PROT --> ORGS["orgScoped: Use(TenantMiddleware) /orgs/:slug/*"]

    ORGS --> SCOPE_H["RegisterOrgScopedRoutes"]
    ORGS --> WS_H["EventsHandler: GET /ws/events"]

    V1 --> EXT["extScoped: Use(APIKeyAuthMiddleware) /ext/orgs/:slug/*"]
    EXT --> EXTROUTES_H["RegisterExtRoutes"]

    GE --> ADMIN_H["admin.RegisterRoutes (if Admin.IsEnabled())"]
    GE --> INT_H["RegisterRelayRoutes: /api/internal/relays/*"]
```

Sources: [backend/internal/api/rest/router.go:52-196]()

---

## Route Group Details

### Health Endpoints

These require no authentication and are used for load balancer and readiness checks.

| Method | Path | Response |
|--------|------|----------|
| `GET` | `/health` | `{"status":"ok","service":"agentsmesh-api"}` |
| `GET` | `/health/ready` | `{"status":"ready"}` |

Sources: [backend/internal/api/rest/router.go:53-64]()

---

### Public Routes (`/api/v1`, no auth)

| Prefix | Handler | Auth Mechanism | Purpose |
|--------|---------|---------------|---------|
| `/api/v1/auth/*` | `AuthHandler` | None | Login, register, password reset, token refresh |
| `/api/v1/config` | `RegisterPublicConfigRoutes` | None | Deployment info for frontend (billing features, plan type) |
| `/api/v1/runners/*` | `RegisterGRPCRunnerRoutes` | mTLS (runner cert) | Runner CLI registration and certificate issuance |
| `/api/v1/webhooks/*` | `WebhookRouter` | Token in payload | Incoming webhooks from Git providers, billing providers |
| `/api/v1/invitations/*` | `InvitationHandler` | Invite token in URL | Token-based invitation acceptance |

The `RegisterGRPCRunnerRoutes` function is also called again inside the org-scoped runner group via `RegisterOrgGRPCRunnerRoutes` for certificate management operations scoped to an organization.

Sources: [backend/internal/api/rest/router.go:79-116]()

---

### Protected Routes (JWT required)

`AuthMiddleware(cfg.JWT.Secret)` is applied to the `protected` group. Routes in this group require a valid Bearer JWT in the `Authorization` header.

| Prefix | Handler | Purpose |
|--------|---------|---------|
| `/api/v1/users/*` | `RegisterUserRoutes` | Current user profile, preferences, credential profiles, agent config |
| `/api/v1/orgs/*` | `RegisterOrganizationRoutes` | List orgs, create org, get org by slug |
| `/api/v1/support-tickets/*` | `SupportTicketHandler` | User-level support ticket submission |

Sources: [backend/internal/api/rest/router.go:118-155]()

---

### Org-Scoped Routes (`/api/v1/orgs/:slug/*`)

These routes additionally require `TenantMiddleware`, which resolves the `:slug` path parameter to an organization record and injects it into the Gin context. All handlers within this group operate on resources belonging to that organization.

**Org-Scoped Route Dispatcher**

```mermaid
graph TD
    ROSR["RegisterOrgScopedRoutes()"] --> RA["registerAgentRoutes: AgentHandler /agents/*"]
    ROSR --> RR["registerRepositoryRoutes: RepositoryHandler /repositories/*"]
    ROSR --> RRU["registerRunnerRoutes: RunnerHandler /runners/*"]
    ROSR --> RP["registerPodRoutes: PodHandler /pods/* + TerminalConnectHandler + AutopilotControllerHandler"]
    ROSR --> RC["registerChannelRoutes: ChannelHandler /channels/*"]
    ROSR --> RT["registerTicketRoutes: TicketHandler + MeshHandler /tickets/* /labels/* /mesh/*"]
    ROSR --> RB["registerBillingRoutes: RegisterBillingHandlers /billing/*"]
    ROSR --> RBI["registerBindingRoutes: BindingHandler /bindings/*"]
    ROSR --> RM["registerMessageRoutes: MessageHandler /messages/*"]
    ROSR --> RI["registerInvitationRoutes: InvitationHandler.RegisterOrgRoutes"]
    ROSR --> RF["registerFileRoutes: FileHandler /files/*"]
    ROSR --> RAK["registerAPIKeyManagementRoutes"]
    ROSR --> RE["registerExtensionRoutes: ExtensionHandler /skill-registries/* /market/*"]
    ROSR --> RL["registerLoopRoutes: LoopHandler /loops/*"]
```

All paths below are relative to `/api/v1/orgs/:slug`.

Sources: [backend/internal/api/rest/v1/routes.go:44-89]()

#### Agents

| Method | Path | Handler Method |
|--------|------|----------------|
| `GET` | `/agents/types` | `AgentHandler.ListAgentTypes` |
| `GET` | `/agents/types/:agent_type_id` | `AgentHandler.GetAgentType` |
| `POST` | `/agents/custom` | `AgentHandler.CreateCustomAgent` |
| `PUT` | `/agents/custom/:id` | `AgentHandler.UpdateCustomAgent` |
| `DELETE` | `/agents/custom/:id` | `AgentHandler.DeleteCustomAgent` |
| `GET` | `/agents/:agent_type_id/config-schema` | `AgentHandler.GetAgentTypeConfigSchema` |

Sources: [backend/internal/api/rest/v1/routes.go:91-102]()

#### Repositories

| Method | Path | Handler Method |
|--------|------|----------------|
| `GET` | `/repositories` | `ListRepositories` |
| `POST` | `/repositories` | `CreateRepository` |
| `GET` | `/repositories/:id` | `GetRepository` |
| `PUT` | `/repositories/:id` | `UpdateRepository` |
| `DELETE` | `/repositories/:id` | `DeleteRepository` |
| `GET` | `/repositories/:id/branches` | `ListBranches` |
| `POST` | `/repositories/:id/sync-branches` | `SyncBranches` |
| `POST` | `/repositories/:id/webhook` | `RegisterRepositoryWebhook` |
| `DELETE` | `/repositories/:id/webhook` | `DeleteRepositoryWebhook` |
| `GET` | `/repositories/:id/webhook/status` | `GetRepositoryWebhookStatus` |
| `GET` | `/repositories/:id/webhook/secret` | `GetRepositoryWebhookSecret` |
| `POST` | `/repositories/:id/webhook/configured` | `MarkRepositoryWebhookConfigured` |
| `GET` | `/repositories/:id/merge-requests` | `ListRepositoryMergeRequests` |

Sources: [backend/internal/api/rest/v1/routes.go:104-126]()

#### Runners

| Method | Path | Handler Method |
|--------|------|----------------|
| `GET` | `/runners` | `RunnerHandler.ListRunners` |
| `GET` | `/runners/available` | `RunnerHandler.ListAvailableRunners` |
| `GET` | `/runners/:id` | `RunnerHandler.GetRunner` |
| `PUT` | `/runners/:id` | `RunnerHandler.UpdateRunner` |
| `DELETE` | `/runners/:id` | `RunnerHandler.DeleteRunner` |
| `GET` | `/runners/:id/pods` | `RunnerHandler.ListRunnerPods` |
| `POST` | `/runners/:id/sandboxes/query` | `RunnerHandler.QuerySandboxes` |

Additionally, `RegisterOrgGRPCRunnerRoutes` is called on the `/runners` group to attach certificate management endpoints used during runner registration and renewal.

Sources: [backend/internal/api/rest/v1/routes.go:128-160]()

#### Pods

The pod group includes CRUD, terminal relay connection, and autopilot controller sub-routes.

| Method | Path | Handler Method | Notes |
|--------|------|----------------|-------|
| `GET` | `/pods` | `PodHandler.ListPods` | |
| `POST` | `/pods` | `PodHandler.CreatePod` | |
| `GET` | `/pods/:key` | `PodHandler.GetPod` | |
| `POST` | `/pods/:key/terminate` | `PodHandler.TerminatePod` | |
| `GET` | `/pods/:key/connect` | `PodHandler.GetConnectionInfo` | |
| `POST` | `/pods/:key/send-prompt` | `PodHandler.SendPrompt` | |
| `GET` | `/pods/:key/terminal/observe` | `PodHandler.ObserveTerminal` | Legacy observe |
| `POST` | `/pods/:key/terminal/input` | `PodHandler.SendTerminalInput` | |
| `POST` | `/pods/:key/terminal/resize` | `PodHandler.ResizeTerminal` | |
| `GET` | `/pods/:key/terminal/connect` | `TerminalConnectHandler.GetTerminalConnection` | Returns Relay URL + JWT |

The `GET /pods/:key/terminal/connect` endpoint is the entry point for the Relay-based terminal architecture. It selects a healthy relay, issues a JWT for both the browser and the runner, sends a `SubscribeTerminal` gRPC command to the runner, and returns the relay URL and browser token. The client then opens a WebSocket directly to the relay service. See [Relay](#4) for details.

Autopilot controller routes are registered by `RegisterAutopilotControllerRoutes` on the same parent group.

Sources: [backend/internal/api/rest/v1/routes.go:162-205](), [backend/internal/api/rest/v1/pod_terminal_connect.go:53-150]()

#### Channels

| Method | Path | Handler Method |
|--------|------|----------------|
| `GET` | `/channels` | `ListChannels` |
| `POST` | `/channels` | `CreateChannel` |
| `GET` | `/channels/:id` | `GetChannel` |
| `PUT` | `/channels/:id` | `UpdateChannel` |
| `POST` | `/channels/:id/archive` | `ArchiveChannel` |
| `POST` | `/channels/:id/unarchive` | `UnarchiveChannel` |
| `GET` | `/channels/:id/messages` | `ListMessages` |
| `POST` | `/channels/:id/messages` | `SendMessage` |
| `GET` | `/channels/:id/document` | `GetDocument` |
| `PUT` | `/channels/:id/document` | `UpdateDocument` |
| `GET` | `/channels/:id/pods` | `ListChannelPods` |
| `POST` | `/channels/:id/pods` | `JoinPod` |
| `DELETE` | `/channels/:id/pods/:pod_key` | `LeavePod` |

Sources: [backend/internal/api/rest/v1/routes.go:208-226]()

#### Tickets, Labels, and Mesh

Tickets are managed by `TicketHandler`; pod-related ticket operations use `MeshHandler`.

| Method | Path | Handler Method |
|--------|------|----------------|
| `GET` | `/tickets` | `TicketHandler.ListTickets` |
| `POST` | `/tickets` | `TicketHandler.CreateTicket` |
| `GET` | `/tickets/active` | `TicketHandler.GetActiveTickets` |
| `GET` | `/tickets/board` | `TicketHandler.GetBoard` |
| `POST` | `/tickets/batch-pods` | `MeshHandler.BatchGetTicketPods` |
| `GET` | `/tickets/:ticket_slug` | `TicketHandler.GetTicket` |
| `PUT` | `/tickets/:ticket_slug` | `TicketHandler.UpdateTicket` |
| `DELETE` | `/tickets/:ticket_slug` | `TicketHandler.DeleteTicket` |
| `PATCH` | `/tickets/:ticket_slug/status` | `TicketHandler.UpdateTicketStatus` |
| `POST` | `/tickets/:ticket_slug/assignees` | `TicketHandler.AddAssignee` |
| `DELETE` | `/tickets/:ticket_slug/assignees/:user_id` | `TicketHandler.RemoveAssignee` |
| `POST` | `/tickets/:ticket_slug/labels` | `TicketHandler.AddLabel` |
| `DELETE` | `/tickets/:ticket_slug/labels/:label_id` | `TicketHandler.RemoveLabel` |
| `GET` | `/tickets/:ticket_slug/merge-requests` | `TicketHandler.ListMergeRequests` |
| `GET` | `/tickets/:ticket_slug/sub-tickets` | `TicketHandler.GetSubTickets` |
| `GET` | `/tickets/:ticket_slug/relations` | `TicketHandler.ListRelations` |
| `POST` | `/tickets/:ticket_slug/relations` | `TicketHandler.CreateRelation` |
| `DELETE` | `/tickets/:ticket_slug/relations/:relation_id` | `TicketHandler.DeleteRelation` |
| `GET` | `/tickets/:ticket_slug/commits` | `TicketHandler.ListCommits` |
| `POST` | `/tickets/:ticket_slug/commits` | `TicketHandler.LinkCommit` |
| `DELETE` | `/tickets/:ticket_slug/commits/:commit_id` | `TicketHandler.UnlinkCommit` |
| `GET` | `/tickets/:ticket_slug/comments` | `TicketHandler.ListComments` |
| `POST` | `/tickets/:ticket_slug/comments` | `TicketHandler.CreateComment` |
| `PUT` | `/tickets/:ticket_slug/comments/:id` | `TicketHandler.UpdateComment` |
| `DELETE` | `/tickets/:ticket_slug/comments/:id` | `TicketHandler.DeleteComment` |
| `GET` | `/tickets/:ticket_slug/pods` | `MeshHandler.GetTicketPods` |
| `POST` | `/tickets/:ticket_slug/pods` | `MeshHandler.CreatePodForTicket` |
| `GET` | `/labels` | `TicketHandler.ListLabels` |
| `POST` | `/labels` | `TicketHandler.CreateLabel` |
| `PUT` | `/labels/:id` | `TicketHandler.UpdateLabel` |
| `DELETE` | `/labels/:id` | `TicketHandler.DeleteLabel` |
| `GET` | `/mesh/topology` | `MeshHandler.GetTopology` |

Sources: [backend/internal/api/rest/v1/routes.go:228-274]()

#### Bindings

| Method | Path | Handler Method |
|--------|------|----------------|
| `POST` | `/bindings` | `BindingHandler.RequestBinding` |
| `GET` | `/bindings` | `BindingHandler.ListBindings` |
| `POST` | `/bindings/accept` | `BindingHandler.AcceptBinding` |
| `POST` | `/bindings/reject` | `BindingHandler.RejectBinding` |
| `POST` | `/bindings/unbind` | `BindingHandler.Unbind` |
| `GET` | `/bindings/pending` | `BindingHandler.GetPendingBindings` |
| `GET` | `/bindings/pods` | `BindingHandler.GetBoundPods` |
| `GET` | `/bindings/check/:target_pod` | `BindingHandler.CheckBinding` |
| `POST` | `/bindings/:id/scopes` | `BindingHandler.RequestScopes` |
| `POST` | `/bindings/:id/scopes/approve` | `BindingHandler.ApproveScopes` |

Sources: [backend/internal/api/rest/v1/routes.go:284-299]()

#### Messages

| Method | Path | Handler Method |
|--------|------|----------------|
| `POST` | `/messages` | `MessageHandler.SendMessage` |
| `GET` | `/messages` | `MessageHandler.GetMessages` |
| `GET` | `/messages/unread-count` | `MessageHandler.GetUnreadCount` |
| `GET` | `/messages/sent` | `MessageHandler.GetSentMessages` |
| `POST` | `/messages/mark-read` | `MessageHandler.MarkRead` |
| `POST` | `/messages/mark-all-read` | `MessageHandler.MarkAllRead` |
| `GET` | `/messages/conversation/:correlation_id` | `MessageHandler.GetConversation` |
| `GET` | `/messages/dlq` | `MessageHandler.GetDeadLetters` |
| `POST` | `/messages/dlq/:id/replay` | `MessageHandler.ReplayDeadLetter` |
| `GET` | `/messages/:id` | `MessageHandler.GetMessage` |

Sources: [backend/internal/api/rest/v1/routes.go:301-318]()

#### Files

| Method | Path | Handler Method |
|--------|------|----------------|
| `POST` | `/files/upload` | `FileHandler.UploadFile` |
| `DELETE` | `/files/:id` | `FileHandler.DeleteFile` |

Sources: [backend/internal/api/rest/v1/routes.go:327-338]()

#### Extensions (Skills and MCP Servers)

| Method | Path | Handler Method |
|--------|------|----------------|
| `GET` | `/skill-registries` | `ExtensionHandler.ListSkillRegistries` |
| `POST` | `/skill-registries` | `ExtensionHandler.CreateSkillRegistry` |
| `POST` | `/skill-registries/:id/sync` | `ExtensionHandler.SyncSkillRegistry` |
| `DELETE` | `/skill-registries/:id` | `ExtensionHandler.DeleteSkillRegistry` |
| `PUT` | `/skill-registries/:id/toggle` | `ExtensionHandler.TogglePlatformRegistry` |
| `GET` | `/skill-registry-overrides` | `ExtensionHandler.ListSkillRegistryOverrides` |
| `GET` | `/market/skills` | `ExtensionHandler.ListMarketSkills` |
| `GET` | `/market/mcp-servers` | `ExtensionHandler.ListMarketMcpServers` |
| `GET` | `/repositories/:id/skills` | `ExtensionHandler.ListRepoSkills` |
| `POST` | `/repositories/:id/skills/install-from-market` | `ExtensionHandler.InstallSkillFromMarket` |
| `POST` | `/repositories/:id/skills/install-from-github` | `ExtensionHandler.InstallSkillFromGitHub` |
| `POST` | `/repositories/:id/skills/install-from-upload` | `ExtensionHandler.InstallSkillFromUpload` |
| `PUT` | `/repositories/:id/skills/:installId` | `ExtensionHandler.UpdateSkill` |
| `DELETE` | `/repositories/:id/skills/:installId` | `ExtensionHandler.UninstallSkill` |
| `GET` | `/repositories/:id/mcp-servers` | `ExtensionHandler.ListRepoMcpServers` |
| `POST` | `/repositories/:id/mcp-servers/install-from-market` | `ExtensionHandler.InstallMcpFromMarket` |
| `POST` | `/repositories/:id/mcp-servers/install-custom` | `ExtensionHandler.InstallCustomMcpServer` |
| `PUT` | `/repositories/:id/mcp-servers/:installId` | `ExtensionHandler.UpdateMcpServer` |
| `DELETE` | `/repositories/:id/mcp-servers/:installId` | `ExtensionHandler.UninstallMcpServer` |

Sources: [backend/internal/api/rest/v1/routes.go:341-391]()

#### Loops

| Method | Path | Handler Method |
|--------|------|----------------|
| `GET` | `/loops` | `LoopHandler.ListLoops` |
| `POST` | `/loops` | `LoopHandler.CreateLoop` |
| `GET` | `/loops/:loop_slug` | `LoopHandler.GetLoop` |
| `PUT` | `/loops/:loop_slug` | `LoopHandler.UpdateLoop` |
| `DELETE` | `/loops/:loop_slug` | `LoopHandler.DeleteLoop` |
| `POST` | `/loops/:loop_slug/enable` | `LoopHandler.EnableLoop` |
| `POST` | `/loops/:loop_slug/disable` | `LoopHandler.DisableLoop` |
| `POST` | `/loops/:loop_slug/trigger` | `LoopHandler.TriggerLoop` |
| `GET` | `/loops/:loop_slug/runs` | `LoopHandler.ListRuns` |
| `GET` | `/loops/:loop_slug/runs/:run_id` | `LoopHandler.GetRun` |
| `POST` | `/loops/:loop_slug/runs/:run_id/cancel` | `LoopHandler.CancelRun` |

Sources: [backend/internal/api/rest/v1/routes.go:393-412]()

#### WebSocket Events

| Method | Path | Handler |
|--------|------|---------|
| `GET` | `/ws/events` | `ws.EventsHandler.HandleEvents` |

This endpoint upgrades to WebSocket and streams real-time events to the connected browser client through the `Hub`. See [Real-time Events and WebSocket](#2.10) for details.

Sources: [backend/internal/api/rest/router.go:144-152]()

---

### External API (`/api/v1/ext/orgs/:slug/*`)

Routes registered by `RegisterExtRoutes` are accessed via `X-API-Key` header authentication. `APIKeyAuthMiddleware` validates the key against the `APIKeyAdapter` service and resolves the organization from `:slug`. This path is intended for third-party service integrations. The route group is only instantiated if `svc.APIKeyAdapter != nil`.

Sources: [backend/internal/api/rest/router.go:162-169]()

---

### Admin Console Routes

`admin.RegisterRoutes` is called on the root Gin engine (not under `/api/v1`) when `cfg.Admin.IsEnabled()` returns true. It receives a minimal `admin.Services` struct containing `Auth`, `Admin`, `Billing`, `RelayManager`, `ExtensionRepo`, `MarketplaceWorker`, and `SupportTicket`. The admin console uses its own authentication mechanism separate from the user JWT flow. See [Web Admin](#6) for the frontend counterpart.

Sources: [backend/internal/api/rest/router.go:171-184]()

---

### Internal Relay API (`/api/internal/relays/*`)

`internal.RegisterRelayRoutes` is mounted at `/api/internal/relays` on the root Gin engine. It is protected by `InternalAPISecret` (a shared secret from `cfg.Server.InternalAPISecret`), not by JWT. This API is called exclusively by the Relay service to:

- Register/unregister relay instances with the backend
- Report heartbeat, CPU, and memory metrics
- Notify the backend of session close events
- Obtain ACME (Let's Encrypt) wildcard certificates for relay subdomains

This group is only registered when `svc.RelayManager != nil`.

Sources: [backend/internal/api/rest/router.go:186-194]()

---

## Middleware Summary

| Middleware | Location | Applied To |
|-----------|----------|-----------|
| `gin.Logger()` | All routes | Request logging |
| `gin.CustomRecovery` | All routes | Panic recovery with structured logging |
| `cors.New(corsConfig)` | All routes | CORS headers |
| `middleware.AuthMiddleware(JWT)` | `protected` group | JWT Bearer token validation |
| `middleware.TenantMiddleware(svc.Org)` | `orgScoped` group | Org slug resolution, injects tenant into context |
| `middleware.APIKeyAuthMiddleware(svc.APIKeyAdapter, svc.Org)` | `extScoped` group | API key validation + org resolution |
| `InternalAPISecret` (header check) | `internal` relay routes | Shared-secret validation for relay-to-backend calls |

`TenantMiddleware` reads the `:slug` URL parameter, looks up the organization, and stores it in the Gin context so all downstream handlers can call `middleware.GetTenant(c)` to retrieve the `OrganizationID` and `OrganizationSlug`.

Sources: [backend/internal/api/rest/router.go:119-155](), [backend/internal/api/rest/router.go:163-168]()

---

# Page: gRPC API and Runner Communication

# gRPC API and Runner Communication

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude/skills/gh-merge/SKILL.md](.claude/skills/gh-merge/SKILL.md)
- [backend/cmd/server/eventbus_relay.go](backend/cmd/server/eventbus_relay.go)
- [backend/cmd/server/main.go](backend/cmd/server/main.go)
- [backend/internal/api/grpc/command_sender_adapter.go](backend/internal/api/grpc/command_sender_adapter.go)
- [backend/internal/api/grpc/runner_adapter_send.go](backend/internal/api/grpc/runner_adapter_send.go)
- [backend/internal/api/grpc/runner_adapter_send_extra_test.go](backend/internal/api/grpc/runner_adapter_send_extra_test.go)
- [backend/internal/api/grpc/runner_adapter_test.go](backend/internal/api/grpc/runner_adapter_test.go)
- [backend/internal/api/rest/v1/pod_terminal_connect.go](backend/internal/api/rest/v1/pod_terminal_connect.go)
- [backend/internal/service/runner/command_sender.go](backend/internal/service/runner/command_sender.go)
- [backend/internal/service/runner/command_sender_test.go](backend/internal/service/runner/command_sender_test.go)
- [backend/internal/service/runner/connection_manager.go](backend/internal/service/runner/connection_manager.go)
- [backend/internal/service/runner/test_helper_test.go](backend/internal/service/runner/test_helper_test.go)
- [proto/gen/go/runner/v1/runner.pb.go](proto/gen/go/runner/v1/runner.pb.go)
- [proto/runner/v1/runner.proto](proto/runner/v1/runner.proto)
- [runner/cmd/runner/cmd_reactivate.go](runner/cmd/runner/cmd_reactivate.go)
- [runner/cmd/runner/cmd_register.go](runner/cmd/runner/cmd_register.go)
- [runner/cmd/runner/cmd_run.go](runner/cmd/runner/cmd_run.go)
- [runner/cmd/runner/main.go](runner/cmd/runner/main.go)
- [runner/cmd/runner/register.go](runner/cmd/runner/register.go)
- [runner/cmd/runner/service.go](runner/cmd/runner/service.go)
- [runner/cmd/runner/update.go](runner/cmd/runner/update.go)
- [runner/cmd/runner/webconsole.go](runner/cmd/runner/webconsole.go)
- [runner/internal/client/grpc_connection.go](runner/internal/client/grpc_connection.go)
- [runner/internal/client/grpc_handler.go](runner/internal/client/grpc_handler.go)
- [runner/internal/client/interface.go](runner/internal/client/interface.go)
- [runner/internal/client/protocol.go](runner/internal/client/protocol.go)
- [runner/internal/relay/client_token_test.go](runner/internal/relay/client_token_test.go)
- [runner/internal/runner/message_handler.go](runner/internal/runner/message_handler.go)
- [runner/internal/runner/message_handler_pod_create_test.go](runner/internal/runner/message_handler_pod_create_test.go)
- [runner/internal/runner/message_handler_relay.go](runner/internal/runner/message_handler_relay.go)
- [runner/internal/runner/runner.go](runner/internal/runner/runner.go)

</details>



This page covers the bidirectional gRPC stream that connects runners to the backend, the Protobuf message definitions that define the protocol, and the code components on both sides that produce and consume those messages.

For the backend data structures that store runner connection state, see [Runner Connection Manager](#2.3). For the MCP handler that uses this channel to dispatch agent commands, see [MCP and Mesh Service](#2.4). For the runner-side daemon that hosts the `GRPCConnection`, see [Runner - gRPC Client](#3.3).

---

## Protocol Overview

All runner-to-backend communication uses a single long-lived bidirectional gRPC stream defined in `RunnerService.Connect`. Both sides multiplex many logical message types over this one stream. There is no REST or WebSocket fallback — mTLS gRPC is mandatory.

**Service definition** ([proto/runner/v1/runner.proto:8-13]()):

```
service RunnerService {
  rpc Connect(stream RunnerMessage) returns (stream ServerMessage);
}
```

The runner passes `x-org-slug` as gRPC metadata. The backend's nginx/proxy injects `x-client-cert-cn` (node ID) and `x-client-cert-serial` from the mTLS client certificate. See [PKI and mTLS](#2.8) for how certificates are issued and validated.

Sources: [proto/runner/v1/runner.proto:1-13](), [runner/internal/client/grpc_connection.go:24-26]()

---

## Protobuf Message Types

Each direction uses a single envelope message with a `oneof payload` field.

### Runner → Backend (`RunnerMessage`)

| Field name | Proto field # | Purpose |
|---|---|---|
| `initialize` | 1 | Sent first; carries `RunnerInfo` (version, node_id, mcp_port, OS/arch) |
| `initialized` | 2 | Confirms handshake; lists available agent slugs and versions |
| `heartbeat` | 3 | Periodic pod list + relay connection status |
| `pod_created` | 4 | Pod started successfully; carries PID, sandbox path, branch |
| `pod_terminated` | 5 | Pod exited; carries exit code and error message |
| `terminal_output` | 6 | Raw PTY bytes (no Base64 encoding) |
| `agent_status` | 7 | Agent state change: `executing`, `waiting`, or `idle` |
| `pty_resized` | 8 | Acknowledges a resize after it is applied |
| `error` | 9 | Structured error with `code`, `message`, and detail map |
| `pod_init_progress` | 10 | Phase/progress updates during pod startup (cloning, etc.) |
| `request_relay_token` | 11 | Requests a new relay JWT when existing token has expired |
| `sandboxes_status` | 12 | Response to `QuerySandboxesCommand` |
| `osc_notification` | 13 | Desktop notification from OSC 777/9 terminal sequences |
| `osc_title` | 14 | Window title change from OSC 0/2 sequences |
| `autopilot_status` | 16 | Autopilot phase/circuit-breaker state update |
| `autopilot_iteration` | 17 | Per-iteration summary |
| `autopilot_created` | 18 | Autopilot started |
| `autopilot_terminated` | 19 | Autopilot ended with reason |
| `autopilot_thinking` | 20 | Control agent decision details |
| `mcp_request` | 21 | MCP tool call tunnelled over the stream (see [MCP and Mesh Service](#2.4)) |
| `pong` | 22 | Response to a backend `PingCommand` |

### Backend → Runner (`ServerMessage`)

| Field name | Proto field # | Purpose |
|---|---|---|
| `initialize_result` | 1 | Response to `initialize`; carries server version and agent type list |
| `create_pod` | 2 | Instructs runner to create a pod |
| `terminate_pod` | 3 | Instructs runner to stop a pod |
| `terminal_input` | 4 | Keystroke/data bytes to write to PTY |
| `terminal_resize` | 5 | Change PTY dimensions |
| `send_prompt` | 6 | Reserved prompt injection |
| `terminal_redraw` | 7 | Trigger a SIGWINCH-style redraw without resizing |
| `subscribe_terminal` | 8 | Tells runner to connect to a Relay channel |
| `unsubscribe_terminal` | 9 | Tells runner to disconnect from Relay |
| `query_sandboxes` | 10 | Request sandbox filesystem status for given pod keys |
| `create_autopilot` | 11 | Start an Autopilot controller |
| `autopilot_control` | 12 | Pause/resume/stop/approve/takeover/handback |
| `mcp_response` | 13 | Reply to an `mcp_request` |
| `ping` | 14 | Downstream liveness probe; runner must reply with `pong` |

Sources: [proto/runner/v1/runner.proto:15-175](), [proto/gen/go/runner/v1/runner.pb.go:25-420]()

---

## Stream Lifecycle

**Diagram: Stream initialization handshake**

```mermaid
sequenceDiagram
    participant R as "Runner (GRPCConnection)"
    participant B as "Backend (GRPCRunnerAdapter)"
    R->>B: "Connect() [mTLS, x-org-slug metadata]"
    R->>B: "RunnerMessage{initialize: {protocol_version, RunnerInfo}}"
    B->>R: "ServerMessage{initialize_result: {agent_types, features}}"
    R->>B: "RunnerMessage{initialized: {available_agents, agent_versions}}"
    Note over B: "Marks runner online; starts heartbeat window"
    loop "every 30s"
        R->>B: "RunnerMessage{heartbeat: {pods, relay_connections, agent_versions}}"
    end
```

Sources: [runner/internal/client/grpc_connection.go:116-148](), [runner/internal/client/grpc_handler.go:98-107](), [backend/internal/service/runner/connection_manager.go:72-90]()

### Initialization Timeout

After `Connect()` the backend expects an `initialize` message within `DefaultInitTimeout` (30 seconds). If it does not arrive, the connection is closed and `onInitFailed` is invoked. This is tracked in `RunnerConnectionManager.StartInitTimeoutChecker`.

The current protocol version constant is `GRPCProtocolVersion = 2` ([runner/internal/client/grpc_connection.go:25]()).

---

## Backend-Side Components

**Diagram: Backend gRPC component relationships**

```mermaid
graph TD
    grpcServer["grpcserver.Server"]
    adapter["GRPCRunnerAdapter\n(backend/internal/api/grpc)"]
    sender["GRPCCommandSender\n(backend/internal/api/grpc)"]
    connMgr["RunnerConnectionManager\n(backend/internal/service/runner)"]
    conn["GRPCConnection\n(backend/internal/service/runner)"]
    stream["RunnerStream interface"]
    podCoord["PodCoordinator"]
    termRouter["TerminalRouter"]

    grpcServer --> adapter
    adapter --> connMgr
    adapter --> sender
    sender --> adapter
    connMgr --> conn
    conn --> stream
    podCoord --> sender
    termRouter --> sender
    sender -.->|"implements RunnerCommandSender"| podCoord
```

Sources: [backend/internal/api/grpc/command_sender_adapter.go:1-87](), [backend/internal/api/grpc/runner_adapter_send.go:1-50](), [backend/internal/service/runner/connection_manager.go:27-65](), [backend/cmd/server/main.go:131-158]()

### `GRPCRunnerAdapter`

Located in `backend/internal/api/grpc`. It is the gRPC service implementation; its `Connect` method is the stream entrypoint. It:

- Accepts the incoming stream, reads `x-client-cert-cn` from metadata to identify the runner.
- Calls `RunnerConnectionManager.AddConnection` to register the stream.
- Reads incoming `RunnerMessage`s in a loop and dispatches them to registered callbacks on `RunnerConnectionManager`.
- Provides `Send*` methods that construct `ServerMessage` values and write them to the appropriate `GRPCConnection.SendMessage`.

### `GRPCCommandSender`

`GRPCCommandSender` ([backend/internal/api/grpc/command_sender_adapter.go]()) is a thin adapter that implements `runner.RunnerCommandSender` by delegating each `Send*` call to the corresponding method on `GRPCRunnerAdapter`. This allows `PodCoordinator` and `TerminalRouter` to send commands without depending on the gRPC package.

### `RunnerCommandSender` interface

Defined in `backend/internal/service/runner/command_sender.go`. Implemented by `GRPCCommandSender` and the no-op fallback `NoOpCommandSender` (used when PKI is not configured).

| Method | Corresponding `ServerMessage` |
|---|---|
| `SendCreatePod` | `create_pod` |
| `SendTerminatePod` | `terminate_pod` |
| `SendTerminalInput` | `terminal_input` |
| `SendTerminalResize` | `terminal_resize` |
| `SendTerminalRedraw` | `terminal_redraw` |
| `SendPrompt` | `send_prompt` |
| `SendSubscribeTerminal` | `subscribe_terminal` |
| `SendUnsubscribeTerminal` | `unsubscribe_terminal` |
| `SendCreateAutopilot` | `create_autopilot` |
| `SendAutopilotControl` | `autopilot_control` |

Sources: [backend/internal/service/runner/command_sender.go:17-53](), [backend/internal/api/grpc/runner_adapter_send.go]()

---

## Runner-Side Components

**Diagram: Runner-side gRPC components**

```mermaid
graph TD
    runner["runner.Runner"]
    conn["client.GRPCConnection\n(runner/internal/client)"]
    handler["RunnerMessageHandler\n(runner/internal/runner)"]
    iface["client.MessageHandler interface"]
    connIface["client.Connection interface"]
    podStore["PodStore (InMemoryPodStore)"]
    rpcClient["RPCClient"]
    agentProbe["AgentProbe"]

    runner --> conn
    runner --> handler
    handler --> podStore
    handler --> conn
    conn -->|"calls"| handler
    conn --> rpcClient
    conn --> agentProbe
    handler -.->|"implements"| iface
    conn -.->|"implements"| connIface
```

Sources: [runner/internal/runner/runner.go:57-149](), [runner/internal/client/grpc_connection.go:29-106](), [runner/internal/client/interface.go:99-117]()

### `GRPCConnection`

The runner-side connection class. It:

- Dials the backend with mTLS using `advancedtls` credentials that support hot-reload of certificate files.
- Opens the `Connect` bidirectional stream.
- Runs `readLoop` (reads `ServerMessage`s) and `writeLoop` (drains send channels) as goroutines.
- Exposes two priority-tiered send channels:
  - `controlCh` (buffer 100): heartbeat, pod lifecycle events, OSC events. High priority.
  - `terminalCh` (buffer 1000): `agent_status` and terminal output. Low priority, rate-limited at 50 KB/s by default.
- Calls `connectionLoop` for automatic reconnection with exponential backoff (5 s to 5 min).
- Contains an `RPCClient` for the MCP request/response pattern.

Key configuration:

| Field | Default | Purpose |
|---|---|---|
| `heartbeatInterval` | 30 s | How often to send `HeartbeatData` |
| `initTimeout` | 30 s | Time to wait for `initialize_result` |
| `certRenewalDays` | 30 | Days before expiry to begin renewal |
| `certUrgentDays` | 7 | Days before expiry to force reconnect |
| `terminalRateLimit` | 50 KB/s | Bytes/s for the `terminalCh` rate limiter |

Sources: [runner/internal/client/grpc_connection.go:29-148]()

### `client.Connection` Interface

Composed of four sub-interfaces ([runner/internal/client/interface.go]()):

- `ConnectionLifecycle` — `Connect`, `Start`, `Stop`, `SetHandler`
- `ConnectionSender` — all `Send*` methods
- `ConnectionMonitor` — queue length/capacity/usage metrics
- `ConnectionConfig` — `GetOrgSlug` / `SetOrgSlug`

`GRPCConnection` is the only production implementation.

### `RunnerMessageHandler`

`RunnerMessageHandler` ([runner/internal/runner/message_handler.go]()) implements `client.MessageHandler`. It is wired to `GRPCConnection.SetHandler` and receives decoded commands. Key methods:

| Method | Triggered by | What it does |
|---|---|---|
| `OnCreatePod` | `create_pod` | Runs `PodBuilder`, starts PTY, registers with MCP server, sends `pod_created` |
| `OnTerminatePod` | `terminate_pod` | Stops PTY and relay client, sends `pod_terminated` |
| `OnTerminalInput` | `terminal_input` | Writes bytes to PTY |
| `OnTerminalResize` | `terminal_resize` | Resizes PTY and virtual terminal |
| `OnTerminalRedraw` | `terminal_redraw` | Invokes the +1/-1 resize trick |
| `OnSubscribeTerminal` | `subscribe_terminal` | Creates and connects a relay `Client` |
| `OnUnsubscribeTerminal` | `unsubscribe_terminal` | Disconnects the relay client |
| `OnQuerySandboxes` | `query_sandboxes` | Inspects sandbox directories, sends `sandboxes_status` |
| `OnCreateAutopilot` | `create_autopilot` | Starts an `AutopilotController` |
| `OnAutopilotControl` | `autopilot_control` | Routes pause/resume/stop actions to the controller |

Sources: [runner/internal/runner/message_handler.go:14-335](), [runner/internal/client/protocol.go:107-138]()

---

## Message Dispatch on the Runner

`handleServerMessage` in `grpc_handler.go` is the switch statement that decodes each incoming `ServerMessage`:

- **Heavy operations** (`create_pod`, `subscribe_terminal`, `create_autopilot`) are dispatched with `go` to avoid blocking the read loop.
- **Lightweight operations** (`terminate_pod`, `terminal_input`, `terminal_resize`, `terminal_redraw`, `query_sandboxes`, `autopilot_control`, `mcp_response`, `ping`) are handled synchronously to preserve ordering.

**Diagram: Incoming message dispatch**

```mermaid
flowchart TD
    recv["stream.Recv()"]
    switch["handleServerMessage"]
    
    recv --> switch

    switch -->|"create_pod\nsubscribe_terminal\ncreate_autopilot"| goroutine["go handler (async)"]
    switch -->|"terminate_pod\nterminal_input\nterminal_resize\nterminal_redraw\nautopilot_control\nquery_sandboxes"| sync["handler (sync)"]
    switch -->|"mcp_response"| rpc["RPCClient.HandleResponse"]
    switch -->|"ping"| pong["sendControl(pong)"]
    switch -->|"initialize_result"| initCh["initResultCh <- result"]

    goroutine --> msgHandler["MessageHandler interface"]
    sync --> msgHandler
```

Sources: [runner/internal/client/grpc_handler.go:43-96]()

---

## MCP over gRPC

Rather than an extra HTTP channel, the runner tunnels MCP tool calls through the existing gRPC stream using `McpRequest` (runner→backend) and `McpResponse` (backend→runner) messages.

- `McpRequest` carries a `request_id`, `pod_key`, `method` name, and a JSON `payload`.
- `McpResponse` carries the matching `request_id`, `success` flag, JSON `payload`, and optional `McpError`.
- The `RPCClient` inside `GRPCConnection` maps pending requests by `request_id` and unblocks callers when `HandleResponse` is called.

See [MCP and Mesh Service](#2.4) for the full handler logic on the backend side.

Sources: [proto/runner/v1/runner.proto:547-571](), [runner/internal/client/grpc_handler.go:282-290](), [runner/internal/runner/runner.go:174-178]()

---

## Relay Token Refresh Flow

When a relay connection fails due to token expiry, the runner sends `request_relay_token`. The backend callback in `setupRelayTokenRefreshCallback` ([backend/cmd/server/eventbus_relay.go:17-]()) verifies pod ownership, generates a new JWT, and replies with a fresh `subscribe_terminal` command.

```mermaid
sequenceDiagram
    participant RC as "relay.Client (runner)"
    participant GC as "GRPCConnection (runner)"
    participant B as "Backend"
    RC->>GC: "token expired callback"
    GC->>B: "RunnerMessage{request_relay_token}"
    B->>B: "tokenGenerator.GenerateToken"
    B->>GC: "ServerMessage{subscribe_terminal (new token)}"
    GC->>RC: "UpdateToken / reconnect"
```

Sources: [runner/internal/runner/message_handler_relay.go:159-170](), [backend/cmd/server/eventbus_relay.go:17-100]()

---

## Fatal Error Handling

`isFatalStreamError` ([runner/internal/client/grpc_connection.go:297-321]()) inspects gRPC status codes to determine whether reconnection should stop permanently:

| gRPC Code | Condition | User message |
|---|---|---|
| `Unauthenticated` | `"runner not found"` | Runner deleted; re-register required |
| `Unauthenticated` | other | Authentication failed; re-register |
| `PermissionDenied` | `"runner is disabled"` | Admin must re-enable runner |

Any other error is considered transient and triggers the reconnect backoff loop.

Sources: [runner/internal/client/grpc_connection.go:297-321]()

---

# Page: Runner Connection Manager

# Runner Connection Manager

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude/skills/gh-merge/SKILL.md](.claude/skills/gh-merge/SKILL.md)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [backend/internal/api/grpc/runner_adapter_test.go](backend/internal/api/grpc/runner_adapter_test.go)
- [backend/internal/service/runner/connection_manager.go](backend/internal/service/runner/connection_manager.go)
- [backend/internal/service/runner/version_checker.go](backend/internal/service/runner/version_checker.go)
- [backend/internal/service/runner/version_checker_test.go](backend/internal/service/runner/version_checker_test.go)
- [docs/rfc/RFC-003-runner-release-pipeline.md](docs/rfc/RFC-003-runner-release-pipeline.md)
- [runner/build/scripts/sign-darwin.sh](runner/build/scripts/sign-darwin.sh)
- [runner/internal/client/interface.go](runner/internal/client/interface.go)
- [runner/internal/relay/client_token_test.go](runner/internal/relay/client_token_test.go)
- [runner/internal/runner/message_handler.go](runner/internal/runner/message_handler.go)
- [runner/internal/runner/message_handler_pod_create_test.go](runner/internal/runner/message_handler_pod_create_test.go)
- [runner/internal/updater/updater.go](runner/internal/updater/updater.go)
- [runner/internal/updater/updater_test.go](runner/internal/updater/updater_test.go)

</details>



This page documents the backend `RunnerConnectionManager`: how active runner gRPC connections are stored, retrieved, and tracked on the backend side. It covers the sharding architecture, the `GRPCConnection` abstraction, heartbeat tracking, and the initialization timeout mechanism.

For the gRPC protocol and message types that flow over these connections, see [gRPC API and Runner Communication](#2.2). For the runner-side gRPC client that initiates connections, see [gRPC Client](#3.3). For how the connection manager is used to dispatch pod and terminal commands, see [MCP and Mesh Service](#2.4).

---

## Overview

When a runner establishes a gRPC bidirectional stream with the backend, the backend wraps that stream in a `GRPCConnection` and stores it in the `RunnerConnectionManager`. The manager is the single source of truth for which runners are currently online. All backend subsystems that need to send commands to a runner look up the connection through this manager.

**Key design properties:**

| Property | Value |
|---|---|
| Shard count | 256 |
| Default ping interval | 30 seconds |
| Default init timeout | 30 seconds |
| Init timeout check interval | 10 seconds |
| Connection count tracking | Lock-free `atomic.Int64` |

Sources: [backend/internal/service/runner/connection_manager.go:13-89]()

---

## Sharded Storage Architecture

The manager partitions connections across 256 independent `grpcConnectionShard` structs, each with its own `sync.RWMutex`. The shard for a given runner is selected by:

```
shard index = runnerID % 256
```

This design reduces lock contention to roughly 1/256th compared to a single global lock, keeping performance predictable even at 100,000+ simultaneous runner connections.

**Sharded connection storage**

```mermaid
graph TD
    CM["RunnerConnectionManager"]
    CM --> S0["shards[0]\ngrpcConnectionShard\nsync.RWMutex\nmap[int64]*GRPCConnection"]
    CM --> S1["shards[1]\ngrpcConnectionShard\nsync.RWMutex\nmap[int64]*GRPCConnection"]
    CM --> SDOT["..."]
    CM --> S255["shards[255]\ngrpcConnectionShard\nsync.RWMutex\nmap[int64]*GRPCConnection"]
    CM --> CC["connCount\natomic.Int64"]

    S0 --> C1["GRPCConnection\nrunnerID=0\nnodeID\norgSlug\nRunnerStream"]
    S0 --> C2["GRPCConnection\nrunnerID=256\n..."]
    S1 --> C3["GRPCConnection\nrunnerID=1\n..."]
```

Sources: [backend/internal/service/runner/connection_manager.go:13-95]()

---

## GRPCConnection Abstraction

Each active runner is represented by a `GRPCConnection` on the backend side. It is created by `NewGRPCConnection` inside `AddConnection` and wraps the live gRPC bidirectional stream.

**Key fields and methods inferred from usage:**

| Symbol | Purpose |
|---|---|
| `ConnectedAt` | Timestamp when the connection was added; used to detect initialization timeouts |
| `IsInitialized()` | Returns whether the runner has completed its initialization handshake |
| `UpdateLastPing()` | Records the time of the latest heartbeat |
| `Close()` | Closes the underlying stream and releases resources |

The `RunnerStream` interface that `GRPCConnection` wraps is implemented by the gRPC server-side stream and exposes three methods: `Send(*runnerv1.ServerMessage)`, `Recv() (*runnerv1.RunnerMessage, error)`, and `Context() context.Context`.

Sources: [backend/internal/service/runner/connection_manager.go:100-148](), [backend/internal/api/grpc/runner_adapter_test.go:121-145]()

---

## Connection Lifecycle

**Connection lifecycle state machine**

```mermaid
stateDiagram-v2
    [*] --> "Connected (uninitialized)": "AddConnection(runnerID, nodeID, orgSlug, stream)"
    "Connected (uninitialized)" --> "Connected (initialized)": "onInitialized callback fires"
    "Connected (uninitialized)" --> "Disconnected": "init timeout (30s)\nonInitFailed callback fires"
    "Connected (initialized)" --> "Disconnected": "RemoveConnection(runnerID)\nonDisconnect callback fires"
    "Disconnected" --> [*]
```

**`AddConnection`** acquires a write lock on the appropriate shard, closes any pre-existing connection for the same runner ID, creates a new `GRPCConnection`, and increments `connCount`.

**`RemoveConnection`** acquires a write lock, deletes the entry, decrements `connCount`, calls `conn.Close()`, and then invokes the `onDisconnect` callback outside the lock.

**`GetConnection`** and **`IsConnected`** acquire a read lock and are safe for concurrent use.

Sources: [backend/internal/service/runner/connection_manager.go:99-163]()

---

## Heartbeat Tracking

The manager does not maintain its own timer per connection. Instead, callers invoke `UpdateHeartbeat(runnerID int64)` when a heartbeat message arrives from the runner over the gRPC stream. This calls `conn.UpdateLastPing()` on the corresponding `GRPCConnection`.

```mermaid
sequenceDiagram
    participant "Runner (remote)" as R
    participant "gRPC stream" as S
    participant "GRPCRunnerAdapter" as A
    participant "RunnerConnectionManager.UpdateHeartbeat" as H
    participant "GRPCConnection.UpdateLastPing" as C

    R->>S: "HeartbeatData message"
    S->>A: "onHeartbeat callback"
    A->>H: "UpdateHeartbeat(runnerID)"
    H->>C: "conn.UpdateLastPing()"
```

The `pingInterval` field (30 seconds default) is stored on the manager but the actual sending of server-side pings is handled by the gRPC adapter layer, not directly by `RunnerConnectionManager`.

Sources: [backend/internal/service/runner/connection_manager.go:165-170]()

---

## Initialization Timeout

After a runner establishes its gRPC stream, the backend expects it to complete an initialization handshake within 30 seconds (`DefaultInitTimeout`). A background goroutine checks for stalled connections every 10 seconds.

**Initialization timeout flow**

```mermaid
flowchart TD
    A["StartInitTimeoutChecker()"] --> B["go initTimeoutLoop()"]
    B --> T["time.NewTicker(10s)"]
    T --> C["checkInitTimeouts()"]
    C --> D["iterate all 256 shards (RLock)"]
    D --> E{"conn.IsInitialized() == false\nAND\nnow - conn.ConnectedAt > initTimeout"}
    E -- "yes" --> F["collect timedOutRunners"]
    E -- "no" --> G["skip"]
    F --> H["onInitFailed(runnerID, reason)"]
    H --> I["RemoveConnection(runnerID)"]
    I --> T
    G --> T
```

The `initTimeoutStop` channel is closed by `RunnerConnectionManager.Close()` via a `sync.Once` guard, which causes the background goroutine to exit cleanly.

Sources: [backend/internal/service/runner/connection_manager.go:210-259]()

---

## Event Callbacks

`RunnerConnectionManager` stores a set of function-typed fields that the owning `GRPCRunnerAdapter` registers to handle runner-originated events. Callbacks receive Proto types directly, avoiding JSON serialization overhead.

| Callback field | Trigger |
|---|---|
| `onHeartbeat` | Runner sent a heartbeat |
| `onPodCreated` | Runner reported a pod started |
| `onPodTerminated` | Runner reported a pod exited |
| `onAgentStatus` | Agent status changed (executing / waiting / idle) |
| `onPtyResized` | Terminal was resized |
| `onPodInitProgress` | Pod initialization phase update |
| `onRequestRelayToken` | Runner needs a fresh relay token |
| `onDisconnect` | Runner gRPC stream closed |
| `onInitialized` | Runner completed handshake |
| `onInitFailed` | Runner timed out before completing handshake |
| `onSandboxesStatus` | Response to a sandbox status query |
| `onOSCNotification` | OSC 777 / OSC 9 terminal notification |
| `onOSCTitle` | OSC 0/2 title change event |
| `onPodError` | Pod encountered an error |
| `onAutopilotStatus` | Autopilot controller status |
| `onAutopilotIteration` | Autopilot iteration event |
| `onAutopilotCreated` | Autopilot session created |
| `onAutopilotTerminated` | Autopilot session ended |
| `onAutopilotThinking` | Autopilot thinking event |

Sources: [backend/internal/service/runner/connection_manager.go:42-64]()

---

## Integration with GRPCRunnerAdapter

`GRPCRunnerAdapter` (in `backend/internal/api/grpc/`) holds a reference to `RunnerConnectionManager` as `adapter.connManager`. Sending any command to a runner follows the same pattern:

1. Call `connMgr.GetConnection(runnerID)` to look up the `GRPCConnection`.
2. If the result is `nil`, return an error containing `"not connected"`.
3. Otherwise, call the appropriate send method on the connection.

**Command dispatch path**

```mermaid
flowchart LR
    Caller["GRPCRunnerAdapter\n(e.g. SendCreatePod)"]
    CM["RunnerConnectionManager\n.GetConnection(runnerID)"]
    GC["GRPCConnection\n.Send(ServerMessage)"]
    Stream["RunnerStream\n(gRPC server stream)"]
    Runner["Runner process\n(remote)"]

    Caller --> CM
    CM -- "GRPCConnection or nil" --> Caller
    Caller --> GC
    GC --> Stream
    Stream --> Runner
```

Sources: [backend/internal/api/grpc/runner_adapter_test.go:27-118](), [backend/internal/service/runner/connection_manager.go:99-163]()

---

## Manager Construction and Teardown

`NewRunnerConnectionManager(logger)` initializes all 256 shards and sets default intervals. It does not start any background goroutines; the caller must explicitly call `StartInitTimeoutChecker()` after construction.

`Close()` signals the timeout goroutine to stop, then iterates every shard under a write lock to close all connections and reset the maps.

```mermaid
sequenceDiagram
    participant "Caller (Backend init)" as B
    participant "RunnerConnectionManager" as M
    participant "initTimeoutLoop goroutine" as L

    B->>M: "NewRunnerConnectionManager(logger)"
    Note over M: "256 shards allocated, no goroutines started"
    B->>M: "StartInitTimeoutChecker()"
    M->>L: "go initTimeoutLoop()"
    Note over L: "runs until initTimeoutStop is closed"
    B->>M: "Close()"
    M->>L: "close(initTimeoutStop)"
    L-->>M: "goroutine exits"
    Note over M: "all GRPCConnection.Close() called"
```

Sources: [backend/internal/service/runner/connection_manager.go:72-208]()

---

# Page: MCP and Mesh Service

# MCP and Mesh Service

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [backend/internal/api/grpc/runner_adapter_mcp.go](backend/internal/api/grpc/runner_adapter_mcp.go)
- [backend/internal/api/grpc/runner_adapter_mcp_ticket.go](backend/internal/api/grpc/runner_adapter_mcp_ticket.go)
- [backend/internal/service/mesh/service.go](backend/internal/service/mesh/service.go)
- [backend/internal/service/ticket/ticket_query.go](backend/internal/service/ticket/ticket_query.go)
- [backend/internal/service/ticket/ticket_query_test.go](backend/internal/service/ticket/ticket_query_test.go)
- [docs/images/architecture.svg](docs/images/architecture.svg)
- [runner/internal/mcp/grpc_client.go](runner/internal/mcp/grpc_client.go)
- [runner/internal/mcp/http_server.go](runner/internal/mcp/http_server.go)
- [runner/internal/mcp/http_tools_format_integration_test.go](runner/internal/mcp/http_tools_format_integration_test.go)
- [runner/internal/mcp/http_tools_ticket.go](runner/internal/mcp/http_tools_ticket.go)
- [runner/internal/mcp/tools/types_client.go](runner/internal/mcp/tools/types_client.go)
- [runner/internal/mcp/tools/types_entity.go](runner/internal/mcp/tools/types_entity.go)
- [web/src/lib/api/pod.ts](web/src/lib/api/pod.ts)
- [web/src/messages/de/app.json](web/src/messages/de/app.json)
- [web/src/messages/en/app.json](web/src/messages/en/app.json)
- [web/src/messages/es/app.json](web/src/messages/es/app.json)
- [web/src/messages/fr/app.json](web/src/messages/fr/app.json)
- [web/src/messages/ja/app.json](web/src/messages/ja/app.json)
- [web/src/messages/ko/app.json](web/src/messages/ko/app.json)
- [web/src/messages/pt/app.json](web/src/messages/pt/app.json)
- [web/src/messages/zh/app.json](web/src/messages/zh/app.json)

</details>



This page covers the Multi-Agent Collaboration Protocol (MCP) integration in AgentsMesh: how AI agents running inside pods use MCP tools to collaborate, the two-sided architecture (runner-side HTTP server and backend-side gRPC handler), and the backend mesh topology service that aggregates pods, channels, and bindings into a queryable graph.

For the gRPC stream that carries MCP messages between runner and backend, see [2.2](). For the runner connection manager that tracks active connections, see [2.3](). For the runner-side implementation of the MCP HTTP server and tool definitions, see [3.6](). For the web frontend's mesh topology visualization, see [5.3]().

---

## Overview

MCP is the mechanism by which AI agents (Claude Code, Codex CLI, etc.) interact with the AgentsMesh collaboration layer — discovering other pods, binding to them, messaging through channels, managing tickets, and spawning new pods. The protocol is surfaced to agents as a standard HTTP MCP endpoint on the runner, backed by the existing gRPC bidirectional stream to the backend.

**MCP Call Path (high-level)**

```mermaid
sequenceDiagram
    participant A as "Agent (Claude Code)"
    participant H as "HTTPServer (runner/mcp)"
    participant G as "GRPCCollaborationClient"
    participant B as "GRPCRunnerAdapter (backend)"
    participant S as "Backend Services"

    A->>H: "POST /mcp (JSON-RPC)"
    H->>H: "Route to MCPTool.Handler"
    H->>G: "client.CallMethod(ctx, args)"
    G->>B: "McpRequest{method, pod_key, payload} via gRPC stream"
    B->>B: "authenticatePod → TenantContext"
    B->>B: "dispatchMcpMethod"
    B->>S: "ticketService / channelService / bindingService / ..."
    S-->>B: "result"
    B-->>G: "McpResponse{result_json}"
    G-->>H: "unmarshaled result"
    H-->>A: "MCP JSON response"
```

Sources: [runner/internal/mcp/http_server.go:1-263](), [runner/internal/mcp/grpc_client.go:1-62](), [backend/internal/api/grpc/runner_adapter_mcp.go:1-90]()

---

## Runner-Side MCP Server

### `HTTPServer`

`HTTPServer` in `runner/internal/mcp/http_server.go` is the local HTTP server that serves the `/mcp` endpoint to agents. It is bound to `127.0.0.1:<port>` and is never exposed externally.

**Key fields:**

| Field | Type | Role |
|---|---|---|
| `rpcClient` | `*client.RPCClient` | Used by `GRPCCollaborationClient` to forward calls to backend |
| `pods` | `map[string]*PodInfo` | Pod registry indexed by `pod_key` |
| `tools` | `[]*MCPTool` | All registered collaboration tools |
| `statusProvider` | `PodStatusProvider` | Interface for querying local pod status |
| `terminalProvider` | `LocalTerminalProvider` | Interface for direct local terminal I/O |

**Lifecycle:**
- Created with `NewHTTPServer(rpcClient, port)`, which calls `registerTools()` immediately.
- Started with `Start()`, which registers `/mcp`, `/health`, and `/pods` routes, then launches the HTTP listener in a goroutine via `safego.Go`.
- Stopped gracefully with `Stop()` (5-second shutdown timeout).

**Pod registration:**
When a pod starts, `RegisterPod(podKey, orgSlug, ticketID, projectID, agentType)` is called. This creates a `PodInfo` entry that includes a `GRPCCollaborationClient` bound to that `pod_key`. When the pod terminates, `UnregisterPod(podKey)` removes it.

**MCP config generation:**
`GenerateMCPConfig(podKey)` produces the JSON snippet written into the agent's config directory. It instructs the agent to call the local `/mcp` endpoint using `curl`, passing `X-Pod-Key` as a header for pod identity.

Sources: [runner/internal/mcp/http_server.go:36-219]()

---

### `GRPCCollaborationClient`

`GRPCCollaborationClient` in `runner/internal/mcp/grpc_client.go` implements the `tools.CollaborationClient` interface using the runner's existing gRPC bidirectional stream, rather than making direct HTTP calls to the backend.

The central method is `call()`:

```
GRPCCollaborationClient.call(ctx, method, params, &result)
  → rpc.Call(ctx, podKey, method, params)   // serializes to JSON, sends McpRequest
  → json.Unmarshal(respBytes, &result)
```

Every public method (`ObserveTerminal`, `RequestBinding`, `SendMessage`, etc.) delegates to `call()` with the appropriate method string and param map.

**Interface breakdown:**

```mermaid
classDiagram
    class CollaborationClient {
        <<interface>>
        +GetPodKey() string
    }
    class TerminalClient {
        <<interface>>
        +ObserveTerminal()
        +SendTerminalText()
        +SendTerminalKey()
    }
    class DiscoveryClient {
        <<interface>>
        +ListAvailablePods()
        +ListRunners()
        +ListRepositories()
    }
    class BindingClient {
        <<interface>>
        +RequestBinding()
        +AcceptBinding()
        +RejectBinding()
        +UnbindPod()
        +GetBindings()
        +GetBoundPods()
    }
    class ChannelClient {
        <<interface>>
        +SearchChannels()
        +CreateChannel()
        +GetChannel()
        +SendMessage()
        +GetMessages()
        +GetDocument()
        +UpdateDocument()
    }
    class TicketClient {
        <<interface>>
        +SearchTickets()
        +GetTicket()
        +CreateTicket()
        +UpdateTicket()
        +PostComment()
    }
    class PodClient {
        <<interface>>
        +CreatePod()
    }
    class GRPCCollaborationClient {
        -rpc RPCClient
        -podKey string
        +call()
    }
    CollaborationClient <|-- TerminalClient
    CollaborationClient <|-- DiscoveryClient
    CollaborationClient <|-- BindingClient
    CollaborationClient <|-- ChannelClient
    CollaborationClient <|-- TicketClient
    CollaborationClient <|-- PodClient
    GRPCCollaborationClient ..|> CollaborationClient
```

Sources: [runner/internal/mcp/tools/types_client.go:1-68](), [runner/internal/mcp/grpc_client.go:1-491]()

---

## Backend-Side MCP Handler

### `GRPCRunnerAdapter` — MCP Dispatch

When the backend's gRPC stream receives a `McpRequest` message, it calls `handleMcpRequest()` in `backend/internal/api/grpc/runner_adapter_mcp.go`.

**`handleMcpRequest` steps:**

1. Calls `authenticatePod(ctx, req.PodKey, conn.OrgSlug)` — looks up the pod and organization, verifies the pod belongs to the runner's org, and returns a `TenantContext` with `OrganizationID`, `UserID` (pod creator), and `UserRole: "pod"`.
2. Injects the `TenantContext` into the request context via `middleware.SetTenant`.
3. Calls `dispatchMcpMethod(ctx, tc, req)` — routes on `req.Method` to one of the handler functions listed below.
4. Serializes the result and sends a `McpResponse` back over the stream with `sendMcpResponse`.
5. On error, sends a `McpResponse` with error code via `sendMcpError`.

**Method dispatch table:**

| Method String | Backend Handler | Service Used |
|---|---|---|
| `observe_terminal` | `mcpObserveTerminal` | Pod / runner connection manager |
| `send_terminal_text` | `mcpSendTerminalText` | Pod / runner connection manager |
| `send_terminal_key` | `mcpSendTerminalKey` | Pod / runner connection manager |
| `list_available_pods` | `mcpListAvailablePods` | `podService` |
| `list_runners` | `mcpListRunners` | `runnerService` |
| `list_repositories` | `mcpListRepositories` | `repositoryService` |
| `request_binding` | `mcpRequestBinding` | `bindingService` |
| `accept_binding` | `mcpAcceptBinding` | `bindingService` |
| `reject_binding` | `mcpRejectBinding` | `bindingService` |
| `unbind_pod` | `mcpUnbindPod` | `bindingService` |
| `get_bindings` | `mcpGetBindings` | `bindingService` |
| `get_bound_pods` | `mcpGetBoundPods` | `bindingService` |
| `search_channels` | `mcpSearchChannels` | `channelService` |
| `create_channel` | `mcpCreateChannel` | `channelService` |
| `get_channel` | `mcpGetChannel` | `channelService` |
| `send_message` | `mcpSendMessage` | `channelService` |
| `get_messages` | `mcpGetMessages` | `channelService` |
| `get_document` | `mcpGetDocument` | `channelService` |
| `update_document` | `mcpUpdateDocument` | `channelService` |
| `search_tickets` | `mcpSearchTickets` | `ticketService` |
| `get_ticket` | `mcpGetTicket` | `ticketService` |
| `create_ticket` | `mcpCreateTicket` | `ticketService` |
| `update_ticket` | `mcpUpdateTicket` | `ticketService` |
| `post_comment` | `mcpPostComment` | `ticketService` |
| `create_pod` | `mcpCreatePod` | `podOrchestrator` |

Sources: [backend/internal/api/grpc/runner_adapter_mcp.go:17-90](), [backend/internal/api/grpc/runner_adapter_mcp_ticket.go:1-400]()

---

### Pod Creation via MCP (`mcpCreatePod`)

`mcpCreatePod` in `backend/internal/api/grpc/runner_adapter_mcp_ticket.go` handles the `create_pod` method. It delegates entirely to `a.podOrchestrator.CreatePod()` using an `agentpod.OrchestrateCreatePodRequest`.

**Request fields of note:**

| Field | Type | Description |
|---|---|---|
| `runner_id` | `int64` | Required; target runner |
| `agent_type_id` | `*int64` | Built-in agent type |
| `ticket_slug` | `*string` | Associates pod with a ticket |
| `source_pod_key` | `string` | Enables resume mode from a prior pod |
| `resume_agent_session` | `*bool` | Whether to restore agent session state |
| `credential_profile_id` | `*int64` | `0` = RunnerHost mode; `nil` = user default; `>0` = specific profile |
| `config_overrides` | `map[string]interface{}` | Agent config overrides |

On success, the response contains `pod_key` and `status`. An optional `warning` field may carry non-fatal messages.

Error codes are mapped from `agentpod` sentinel errors via `mapOrchestratorErrorToMCP`:

| Error | MCP Code |
|---|---|
| `ErrMissingRunnerID` | 400 |
| `ErrSourcePodNotTerminated` | 400 |
| `ErrSourcePodAccessDenied` | 403 |
| `ErrSourcePodNotFound` | 404 |
| `ErrSandboxAlreadyResumed` | 409 |
| `ErrConfigBuildFailed` | 500 |

Sources: [backend/internal/api/grpc/runner_adapter_mcp_ticket.go:311-400]()

---

### Ticket MCP Handlers

Ticket methods are implemented in `backend/internal/api/grpc/runner_adapter_mcp_ticket.go`. All of them operate through `ticketService` after extracting `OrganizationID` from the `TenantContext`.

**`enrichTicketForMCP`** is a helper that augments a `ticketDomain.Ticket` before returning it to the runner:

- Resolves `ParentTicketID` → `ParentTicketSlug` (a human-readable slug like `AM-123`)
- Converts BlockNote JSON content to plain text via `blocknote.ToPlainText`
- Applies line-range pagination: `content_offset` (0-based) and `content_limit` (default 200) allow agents to read large ticket bodies in chunks
- Returns an `mcpTicketResponse` wrapper carrying `ContentTotalLines`, `ContentOffset`, `ContentLimit`

This pagination is intentional for LLM context window management — agents should call `get_ticket` repeatedly with increasing `content_offset` when `ContentOffset + ContentLimit < ContentTotalLines`.

Sources: [backend/internal/api/grpc/runner_adapter_mcp_ticket.go:17-87]()

---

## Registered MCP Tools (Runner Side)

`HTTPServer.registerTools()` populates `s.tools` at startup. Each `MCPTool` has a `Name`, `Description`, `InputSchema` (JSON Schema), and a `Handler` function.

**Tool categories:**

```mermaid
graph TD
    Root["registerTools()"] --> T["Terminal Tools"]
    Root --> D["Discovery Tools"]
    Root --> Bind["Binding Tools"]
    Root --> Ch["Channel Tools"]
    Root --> Tk["Ticket Tools"]
    Root --> P["Pod Tools"]

    T --> t1["observe_terminal"]
    T --> t2["send_terminal_text"]
    T --> t3["send_terminal_key"]
    T --> t4["get_pod_status"]

    D --> d1["list_available_pods"]
    D --> d2["list_runners"]
    D --> d3["list_repositories"]

    Bind --> b1["bind_pod"]
    Bind --> b2["accept_binding"]
    Bind --> b3["reject_binding"]
    Bind --> b4["unbind_pod"]
    Bind --> b5["get_bindings"]
    Bind --> b6["get_bound_pods"]

    Ch --> c1["search_channels"]
    Ch --> c2["create_channel"]
    Ch --> c3["get_channel"]
    Ch --> c4["send_channel_message"]
    Ch --> c5["get_channel_messages"]
    Ch --> c6["get_channel_document"]
    Ch --> c7["update_channel_document"]

    Tk --> tk1["search_tickets"]
    Tk --> tk2["get_ticket"]
    Tk --> tk3["create_ticket"]
    Tk --> tk4["update_ticket"]
    Tk --> tk5["post_comment"]

    P --> p1["create_pod"]
```

**`get_pod_status`** is unique in that it is served locally by the runner using `statusProvider.GetPodStatus()` — it does not travel over gRPC to the backend. This allows an agent to query the execution state (`executing` / `waiting` / `idle`) of a sibling pod on the same runner without a round-trip.

Sources: [runner/internal/mcp/http_server.go:222-262](), [runner/internal/mcp/http_tools_ticket.go:1-277]()

---

## Mesh Topology Service

`mesh.Service` in `backend/internal/service/mesh/service.go` assembles the full agent collaboration graph for an organization. It is used by the REST API (not MCP) and by the web frontend's topology visualization.

**Dependencies:**

| Field | Type |
|---|---|
| `db` | `*gorm.DB` |
| `podService` | `*agentpod.PodService` |
| `channelService` | `*channel.Service` |
| `bindingService` | `*binding.Service` |

**`GetTopology(ctx, orgID)`** returns a `*mesh.MeshTopology`:

1. Fetches up to 100 pods for the organization via `podService.ListPods`.
2. Filters to only active pods (those satisfying `pod.IsActive()`).
3. Converts active pods to `mesh.MeshNode` records.
4. For each active pod, fetches active bindings via `bindingService.GetBindingsForPod`. Deduplicates using a `seenBindings` map (since each binding appears from both initiator and target perspectives).
5. Converts active bindings to `mesh.MeshEdge` records.
6. Fetches channels for the organization.
7. Returns a `MeshTopology` struct containing all three.

**`MeshTopology` domain model:**

```mermaid
classDiagram
    class MeshTopology {
        +Nodes []MeshNode
        +Edges []MeshEdge
        +Channels []ChannelSummary
    }
    class MeshNode {
        +PodKey string
        +Status string
        +AgentType string
        +RunnerID int64
        +TicketSlug string
        +CreatedByUsername string
    }
    class MeshEdge {
        +ID int64
        +Source string
        +Target string
        +GrantedScopes []string
        +PendingScopes []string
        +Status string
    }
    class ChannelSummary {
        +ID int64
        +Name string
        +MemberCount int
        +IsArchived bool
        +TicketSlug string
    }
    MeshTopology o-- MeshNode
    MeshTopology o-- MeshEdge
    MeshTopology o-- ChannelSummary
```

Sources: [backend/internal/service/mesh/service.go:1-127]()

---

## Channel and Binding Management

Channels and bindings are the two primary collaboration primitives surfaced through MCP.

### Channels

A `Channel` (domain type in `runner/internal/mcp/tools/types_entity.go`) represents a named communication space for agents. Key fields:

| Field | Purpose |
|---|---|
| `ID` | Integer channel identifier |
| `Name` | Human-readable name |
| `TicketSlug` | Optional association with a ticket (e.g., `AM-42`) |
| `Document` | Shared mutable document for the channel (agents may read/write via `get_document` / `update_document`) |
| `MemberCount` | Number of pods currently in the channel |
| `IsArchived` | Soft-deletion flag |
| `CreatedByPod` | `pod_key` of the creating agent |

### Bindings

A `Binding` models a directed collaboration link between two pods. Key fields:

| Field | Purpose |
|---|---|
| `InitiatorPod` | `pod_key` of the pod that requested the binding |
| `TargetPod` | `pod_key` of the pod being bound to |
| `Status` | `pending` → `active` or `rejected` |
| `GrantedScopes` | Capabilities the target granted (e.g., `terminal_read`) |
| `PendingScopes` | Capabilities requested but not yet accepted |

**Binding lifecycle (MCP perspective):**

```mermaid
stateDiagram-v2
    [*] --> "pending": "request_binding"
    "pending" --> "active": "accept_binding"
    "pending" --> "rejected": "reject_binding"
    "active" --> [*]: "unbind_pod"
    "rejected" --> [*]
```

The initiating agent calls `request_binding` with a `target_pod` and list of `scopes`. The target agent polls `get_bindings` (filtering by `status=pending`) to discover incoming requests, then calls `accept_binding` or `reject_binding`. Once active, the initiator may use `observe_terminal` / `send_terminal_text` on the target pod, subject to the granted scopes.

Sources: [runner/internal/mcp/tools/types_entity.go:1-120](), [runner/internal/mcp/grpc_client.go:134-212]()

---

## End-to-End Architecture Diagram

The following diagram maps the key code entities to their roles in the MCP and Mesh pipeline.

```mermaid
graph LR
    subgraph "Runner Process"
        Agent["Agent (Claude Code)"]
        MCPHTTP["HTTPServer\n/mcp endpoint"]
        PodReg["PodInfo registry\npods map[string]*PodInfo"]
        GCC["GRPCCollaborationClient\ncall(method, params)"]
        RPC["RPCClient\nrpc.Call()"]
    end

    subgraph "gRPC Stream"
        MSG["McpRequest / McpResponse\n(proto)"]
    end

    subgraph "Backend grpc package"
        GRA["GRPCRunnerAdapter\nhandleMcpRequest()"]
        AUTH["authenticatePod()\nTenantContext"]
        DISP["dispatchMcpMethod()"]
    end

    subgraph "Backend Services"
        POD["PodService\n/ PodOrchestrator"]
        BIND["binding.Service"]
        CHAN["channel.Service"]
        TICK["ticket.Service"]
        MESH["mesh.Service\nGetTopology()"]
    end

    Agent -->|"HTTP POST /mcp"| MCPHTTP
    MCPHTTP -->|"lookup pod"| PodReg
    MCPHTTP -->|"CollaborationClient"| GCC
    GCC -->|"rpc.Call"| RPC
    RPC -->|"McpRequest"| MSG
    MSG --> GRA
    GRA --> AUTH
    GRA --> DISP
    DISP --> POD
    DISP --> BIND
    DISP --> CHAN
    DISP --> TICK
    CHAN -.->|"feeds"| MESH
    BIND -.->|"feeds"| MESH
    POD -.->|"feeds"| MESH
```

Sources: [runner/internal/mcp/http_server.go:36-90](), [runner/internal/mcp/grpc_client.go:14-62](), [backend/internal/api/grpc/runner_adapter_mcp.go:17-90](), [backend/internal/service/mesh/service.go:22-44]()

---

# Page: Ticket Service

# Ticket Service

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [backend/internal/api/grpc/runner_adapter_mcp.go](backend/internal/api/grpc/runner_adapter_mcp.go)
- [backend/internal/api/grpc/runner_adapter_mcp_ticket.go](backend/internal/api/grpc/runner_adapter_mcp_ticket.go)
- [backend/internal/service/ticket/ticket_query.go](backend/internal/service/ticket/ticket_query.go)
- [backend/internal/service/ticket/ticket_query_test.go](backend/internal/service/ticket/ticket_query_test.go)
- [docs/images/architecture.svg](docs/images/architecture.svg)
- [runner/internal/mcp/grpc_client.go](runner/internal/mcp/grpc_client.go)
- [runner/internal/mcp/http_server.go](runner/internal/mcp/http_server.go)
- [runner/internal/mcp/http_tools_format_integration_test.go](runner/internal/mcp/http_tools_format_integration_test.go)
- [runner/internal/mcp/http_tools_ticket.go](runner/internal/mcp/http_tools_ticket.go)
- [runner/internal/mcp/tools/types_client.go](runner/internal/mcp/tools/types_client.go)
- [runner/internal/mcp/tools/types_entity.go](runner/internal/mcp/tools/types_entity.go)
- [web/src/app/(dashboard)/[org]/tickets/components/BoardViewLayout.tsx](web/src/app/(dashboard)/[org]/tickets/components/BoardViewLayout.tsx)
- [web/src/app/(dashboard)/[org]/tickets/components/ListViewLayout.tsx](web/src/app/(dashboard)/[org]/tickets/components/ListViewLayout.tsx)
- [web/src/app/(dashboard)/[org]/tickets/page.tsx](web/src/app/(dashboard)/[org]/tickets/page.tsx)
- [web/src/components/tickets/KanbanBoard.tsx](web/src/components/tickets/KanbanBoard.tsx)
- [web/src/components/tickets/TicketDetail.tsx](web/src/components/tickets/TicketDetail.tsx)
- [web/src/components/tickets/TicketDetailPane.tsx](web/src/components/tickets/TicketDetailPane.tsx)
- [web/src/components/tickets/TicketDetailSidebar.tsx](web/src/components/tickets/TicketDetailSidebar.tsx)
- [web/src/components/tickets/__tests__/TicketDetail.test.tsx](web/src/components/tickets/__tests__/TicketDetail.test.tsx)
- [web/src/lib/api/ticket.ts](web/src/lib/api/ticket.ts)
- [web/src/stores/ticket.ts](web/src/stores/ticket.ts)

</details>



This page documents the backend ticket service, the REST API it exposes, the MCP interface for AI agents, and the frontend state management layer. The ticket system is the project management subsystem of AgentsMesh — it tracks work items and integrates with pods so that agents can be launched against specific tasks.

For the **frontend UI components** (Kanban board, ticket list, ticket detail page), see [5.2](#5.2). For how tickets relate to the broader MCP and mesh system, see [2.4](#2.4).

---

## Data Model

A ticket belongs to a single organization and carries a human-readable `slug` (e.g. `AM-42`). Slug uniqueness is enforced per-organization, not globally — two organizations may each have a ticket with slug `TICKET-1`.

**Ticket fields** ([web/src/lib/api/ticket.ts:7-32]()):

| Field | Type | Notes |
|---|---|---|
| `id` | `number` | Primary key |
| `number` | `number` | Sequential counter per org |
| `slug` | `string` | Human-readable ID, e.g. `AM-42` |
| `title` | `string` | |
| `content` | `string?` | BlockNote JSON (rich text) |
| `status` | `TicketStatus` | See below |
| `priority` | `TicketPriority` | See below |
| `severity` | `string?` | Optional severity label |
| `estimate` | `number?` | Story point estimate |
| `due_date` | `string?` | ISO date |
| `reporter` | `User?` | Populated on fetch |
| `assignees` | `TicketAssignee[]?` | Join table with user |
| `labels` | `Label[]?` | Color-tagged labels |
| `repository_id` | `number?` | Associated git repository |
| `parent_ticket` | `{ id, slug, title }?` | Parent for sub-tickets |

**Status values** (`TicketStatus`): `backlog`, `todo`, `in_progress`, `in_review`, `done`

**Priority values** (`TicketPriority`): `none`, `low`, `medium`, `high`, `urgent`

Sources: [web/src/lib/api/ticket.ts:4-32](), [runner/internal/mcp/tools/types_entity.go:98-114]()

---

## Backend Service Layer

The core service lives in `backend/internal/service/ticket/`. The `Service` struct wraps a GORM database handle and exposes query and mutation functions.

**Ticket query diagram:**

```mermaid
flowchart TD
    A["GetTicketByIDOrSlug(ctx, orgID, idOrSlug)"] --> B{"Is slug\nmatch found?"}
    B -- "Yes" --> C["GetTicketBySlug(ctx, orgID, slug)"]
    B -- "No" --> D{"Is input\nnumeric?"}
    D -- "Yes" --> E["GetTicket(ctx, numericID)"]
    E --> F{"orgID\nmatches?"}
    F -- "Yes" --> G["Return ticket"]
    F -- "No" --> H["ErrTicketNotFound"]
    D -- "No" --> H
    C --> G
```

**`GetTicket`** ([backend/internal/service/ticket/ticket_query.go:11-22]())
Fetches by primary key. Eager-loads `Assignees.User`, `Labels`, `MergeRequests`, `SubTickets`.

**`GetTicketBySlug`** ([backend/internal/service/ticket/ticket_query.go:25-38]())
Looks up by `(organization_id, slug)`. Returns `ErrTicketNotFound` if not found.

**`GetTicketByIDOrSlug`** ([backend/internal/service/ticket/ticket_query.go:43-64]())
Tries slug first; falls back to numeric primary-key lookup only if the input string is a pure integer. The numeric path validates org ownership before returning. This is the primary lookup path used by MCP handlers.

**`ListTickets`** ([backend/internal/service/ticket/ticket_query.go:67-112]())
Accepts a `ListTicketsFilter` struct with the following optional fields:

| Filter field | SQL clause |
|---|---|
| `RepositoryID` | `repository_id = ?` |
| `Status` | `status = ?` |
| `Priority` | `priority = ?` |
| `ReporterID` | `reporter_id = ?` |
| `ParentTicketID` | `parent_ticket_id = ?` |
| `Query` | `title ILIKE %q%` or `slug ILIKE %q%` |
| `AssigneeID` | JOIN `ticket_assignees` |
| `LabelIDs` | JOIN `ticket_labels` |

Results are ordered by `created_at DESC`. Returns `([]*ticket.Ticket, totalCount int64, error)`.

Sources: [backend/internal/service/ticket/ticket_query.go:1-112](), [backend/internal/service/ticket/ticket_query_test.go:1-137]()

---

## REST API Endpoints

All ticket routes are scoped to an organization. The `orgPath()` helper in the frontend ([web/src/lib/api/ticket.ts:1]()) prefixes requests with `/api/orgs/{orgSlug}`.

**Ticket resource diagram:**

```mermaid
flowchart LR
    subgraph "Ticket Core"
        LIST["GET /tickets"]
        GET["GET /tickets/:slug"]
        CREATE["POST /tickets"]
        UPDATE["PUT /tickets/:slug"]
        DELETE["DELETE /tickets/:slug"]
        STATUS["PATCH /tickets/:slug/status"]
        ACTIVE["GET /tickets/active"]
        BOARD["GET /tickets/board"]
    end

    subgraph "Relations"
        SUBS["GET /tickets/:slug/sub-tickets"]
        RELS_LIST["GET /tickets/:slug/relations"]
        RELS_CREATE["POST /tickets/:slug/relations"]
        RELS_DELETE["DELETE /tickets/:slug/relations/:id"]
    end

    subgraph "Commits"
        COMMITS_LIST["GET /tickets/:slug/commits"]
        COMMITS_LINK["POST /tickets/:slug/commits"]
        COMMITS_UNLINK["DELETE /tickets/:slug/commits/:id"]
    end

    subgraph "People"
        ASSIGNEE_ADD["POST /tickets/:slug/assignees"]
        ASSIGNEE_REMOVE["DELETE /tickets/:slug/assignees/:userId"]
        LABEL_ADD["POST /tickets/:slug/labels"]
        LABEL_REMOVE["DELETE /tickets/:slug/labels/:id"]
    end

    subgraph "Pods"
        PODS_GET["GET /tickets/:slug/pods"]
        PODS_CREATE["POST /tickets/:slug/pods"]
        PODS_BATCH["POST /tickets/batch-pods"]
    end

    subgraph "Comments"
        COMMENTS_LIST["GET /tickets/:slug/comments"]
        COMMENTS_CREATE["POST /tickets/:slug/comments"]
        COMMENTS_UPDATE["PUT /tickets/:slug/comments/:id"]
        COMMENTS_DELETE["DELETE /tickets/:slug/comments/:id"]
    end
```

Sources: [web/src/lib/api/ticket.ts:76-400]()

### Key endpoint notes

- **`GET /tickets`** accepts query params: `status`, `priority`, `assignee_id`, `repository_id`, `query`, `limit`, `offset`. Returns `{ tickets: TicketData[], total: number }`.
- **`PATCH /tickets/:slug/status`** is a lightweight status-only update. The frontend `updateTicketStatus` store action calls this with an optimistic local update and rolls back on failure ([web/src/stores/ticket.ts:181-202]()).
- **`GET /tickets/board`** returns `{ board: { columns: BoardColumn[] } }` grouped by status.
- **`GET /tickets/active`** returns tickets with `in_progress` or `in_review` status.
- **`POST /tickets/batch-pods`** accepts `{ ticket_ids: number[] }` and returns a map of ticket IDs to pod summaries — used to populate pod indicators on the Kanban board efficiently.
- **`POST /tickets/:slug/pods`** creates a new AgentPod bound to that ticket. The body mirrors the pod creation params (runner_id, initial_prompt, model, permission_mode).
- Comment `content` supports `parent_id` for threaded replies and `mentions` for user references.

Sources: [web/src/lib/api/ticket.ts:76-400]()

---

## Frontend State: `useTicketStore`

The Zustand store at `web/src/stores/ticket.ts` is the single source of state for all ticket data on the frontend.

**Store architecture diagram:**

```mermaid
flowchart TD
    subgraph "useTicketStore [web/src/stores/ticket.ts]"
        STATE["State\n---\ntickets: Ticket[]\ncurrentTicket: Ticket|null\nselectedTicketSlug: string|null\nlabels: Label[]\nfilters: TicketFilters\nuiFilters: TicketUIFilters\nviewMode: board|list\nloading: boolean\nerror: string|null\ntotalCount: number"]

        subgraph "Actions"
            FT["fetchTickets(filters?)"]
            FTK["fetchTicket(slug)"]
            CT["createTicket(data)"]
            UT["updateTicket(slug, data)"]
            DT["deleteTicket(slug)"]
            UTS["updateTicketStatus(slug, status)"]
        end

        subgraph "UI Filter Actions"
            TS["toggleStatus(status)"]
            TP["togglePriority(priority)"]
            CF["clearUIFilters()"]
            SVM["setViewMode(mode)"]
        end
    end

    subgraph "Derived"
        UFT["useFilteredTickets()\n[selector hook]"]
    end

    STATE --> UFT
    FT --> STATE
    FTK --> STATE
    CT --> STATE
    UT --> STATE
    DT --> STATE
    UTS --> STATE

    TS --> STATE
    TP --> STATE
```

**`useFilteredTickets`** ([web/src/stores/ticket.ts:303-322]()) is a selector hook that derives a filtered ticket list from `tickets`, `filters.search`, `uiFilters.selectedStatuses`, and `uiFilters.selectedPriorities` using `useMemo`. It is the single source used by both the list view and board view to avoid duplication.

**Optimistic updates**: `updateTicketStatus` applies the status change locally before calling the API, and rolls back `tickets` and `currentTicket` if the request fails ([web/src/stores/ticket.ts:181-202]()).

**`currentTicket` vs `tickets`**: `currentTicket` is set by `fetchTicket(slug)` and used by `TicketDetail`. The `tickets` array is populated by `fetchTickets()` and used by list/board views. `updateTicket` and `updateTicketStatus` update both simultaneously.

Sources: [web/src/stores/ticket.ts:1-355]()

---

## MCP Integration (AI Agent Access)

AI agents running inside pods can read and modify tickets through the MCP protocol. The backend `GRPCRunnerAdapter` handles these requests.

**MCP ticket flow:**

```mermaid
sequenceDiagram
    participant A as "Agent (Claude Code)"
    participant H as "HTTPServer\n[runner/internal/mcp/http_server.go]"
    participant G as "GRPCCollaborationClient\n[runner/internal/mcp/grpc_client.go]"
    participant R as "RPCClient\n[runner/internal/client]"
    participant B as "GRPCRunnerAdapter\n[backend/internal/api/grpc]"
    participant S as "ticket.Service\n[backend/internal/service/ticket]"

    A->>H: "POST /mcp {method: get_ticket, ticket_slug: AM-42}"
    H->>G: "GetTicket(ctx, slug, offset, limit)"
    G->>R: "Call(ctx, podKey, get_ticket, params)"
    R->>B: "McpRequest{method: get_ticket, payload}"
    B->>B: "authenticatePod(podKey, orgSlug)"
    B->>S: "GetTicketByIDOrSlug(ctx, orgID, slug)"
    S-->>B: "*ticket.Ticket"
    B->>B: "enrichTicketForMCP(ctx, orgID, ticket, pagination)"
    B-->>R: "McpResponse{ticket}"
    R-->>G: "[]byte JSON"
    G-->>H: "*tools.Ticket"
    H-->>A: "MCP text response"
```

### MCP Ticket Methods

Defined in `backend/internal/api/grpc/runner_adapter_mcp_ticket.go` and dispatched from `dispatchMcpMethod` ([backend/internal/api/grpc/runner_adapter_mcp.go:125-136]()):

| MCP method | Handler | Description |
|---|---|---|
| `search_tickets` | `mcpSearchTickets` | Filter by status, priority, assignee, parent, query, with pagination |
| `get_ticket` | `mcpGetTicket` | Fetch single ticket by slug, with content line-range pagination |
| `create_ticket` | `mcpCreateTicket` | Create ticket with title, content, priority, optional parent slug |
| `update_ticket` | `mcpUpdateTicket` | Update title, content, status, or priority |
| `post_comment` | `mcpPostComment` | Post a comment, optionally replying to a parent comment |

### Content Pagination

Ticket content is stored as BlockNote JSON. The `enrichTicketForMCP` function ([backend/internal/api/grpc/runner_adapter_mcp_ticket.go:35-87]()) converts it to plain text and supports line-range slicing:

- Converts `BlockNote JSON → plain text` via `blocknote.ToPlainText()`
- Splits on `\n` to get individual lines
- Applies `content_offset` (0-based start line, default 0) and `content_limit` (line count, default 200)
- Returns `ContentTotalLines`, `ContentOffset`, `ContentLimit` alongside the sliced text

This allows agents to read large ticket descriptions incrementally.

### Runner-side MCP Tools

The runner's MCP HTTP server registers these tools in `runner/internal/mcp/http_tools_ticket.go`. The tool definitions are returned to agents in the MCP `tools/list` response:

| Tool | Required params | Optional params |
|---|---|---|
| `search_tickets` | — | `repository_id`, `status`, `priority`, `assignee_id`, `parent_ticket_slug`, `query`, `limit`, `page` |
| `get_ticket` | `ticket_slug` | `content_offset`, `content_limit` |
| `create_ticket` | `title` | `repository_id`, `content`, `priority`, `parent_ticket_slug` |
| `update_ticket` | `ticket_slug` | `title`, `content`, `status`, `priority` |
| `post_comment` | `ticket_slug`, `content` | `parent_id` |

The runner-side handler calls through `GRPCCollaborationClient` which serializes to JSON and sends a `McpRequest` gRPC message to the backend ([runner/internal/mcp/grpc_client.go:350-468]()).

Sources: [backend/internal/api/grpc/runner_adapter_mcp_ticket.go:1-307](), [runner/internal/mcp/http_tools_ticket.go:1-277](), [runner/internal/mcp/grpc_client.go:347-468](), [runner/internal/mcp/tools/types_client.go:43-50]()

---

## Pod Integration

Tickets connect to pods in two ways:

1. **From the sidebar**: `TicketDetailSidebar` fetches pods via `ticketApi.getPods(slug)` ([web/src/components/tickets/TicketDetailSidebar.tsx:218-228]()). The `SidebarPodSection` component separates pods into active (`running`, `initializing`) and inactive. Clicking "Execute" opens `CreatePodModal` with the ticket pre-populated as context.

2. **From the Kanban board**: When a ticket is dragged from `backlog` or `todo` to `in_progress`, `KanbanBoard` fires `onCreatePodRequest` ([web/src/components/tickets/KanbanBoard.tsx:305-311]()), which causes the parent `TicketsPage` to open `CreatePodModal` ([web/src/app/(dashboard)/[org]/tickets/page.tsx:52-54]()).

3. **Via MCP**: The `create_pod` MCP tool (handled by `mcpCreatePod` in `runner_adapter_mcp_ticket.go`) accepts an optional `ticket_slug` parameter. When provided, the created pod is bound to that ticket in the database.

**Pod status indicators** on sidebar entries are color-coded by `pod.status`:
- `running` — green animated pulse
- `initializing` — yellow animated pulse  
- `failed` — red
- other — muted gray

Sources: [web/src/components/tickets/TicketDetailSidebar.tsx:202-334](), [web/src/components/tickets/KanbanBoard.tsx:282-315](), [web/src/app/(dashboard)/[org]/tickets/page.tsx:39-120](), [backend/internal/api/grpc/runner_adapter_mcp_ticket.go:312-374]()

---

## Ticket Comments

Comments support threading via `parent_id` and user `@mentions`.

**Data shape** ([web/src/lib/api/ticket.ts:56-67]()):

```
TicketComment {
  id, ticket_id, user_id
  content: string
  parent_id?: number       // for threaded replies
  mentions?: [{ user_id, username }]
  created_at, updated_at
  user?: User
  replies?: TicketComment[]
}
```

The frontend `useTicketExtraData` hook (referenced in `TicketDetail`) loads comments, sub-tickets, relations, and commits as a group once the ticket is available. Comments are paginated with `limit`/`offset`.

Sources: [web/src/lib/api/ticket.ts:56-67](), [web/src/components/tickets/TicketDetail.tsx:41]()

---

## Labels

Labels are organization-scoped and optionally tied to a repository. They are managed via `/api/orgs/{slug}/labels` endpoints. Each label has a `name` and a CSS hex `color` string.

**Ticket ↔ label association** uses a join table: `POST /tickets/:slug/labels` with `{ label_id }` and `DELETE /tickets/:slug/labels/:id` to add/remove.

The `ticketApi.listLabels(repositoryId?)` endpoint returns all labels for the organization, optionally filtered by repository ([web/src/lib/api/ticket.ts:256-261]()).

Sources: [web/src/lib/api/ticket.ts:255-302]()

---

# Page: Billing and Subscriptions

# Billing and Subscriptions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/internal/api/rest/v1/admin/subscriptions.go](backend/internal/api/rest/v1/admin/subscriptions.go)
- [backend/internal/api/rest/v1/invitations.go](backend/internal/api/rest/v1/invitations.go)
- [backend/internal/api/rest/v1/pods.go](backend/internal/api/rest/v1/pods.go)
- [backend/internal/api/rest/v1/repositories.go](backend/internal/api/rest/v1/repositories.go)
- [backend/internal/domain/organization/organization.go](backend/internal/domain/organization/organization.go)
- [backend/internal/service/billing/service.go](backend/internal/service/billing/service.go)
- [backend/internal/service/billing/subscription.go](backend/internal/service/billing/subscription.go)
- [backend/internal/service/organization/interface.go](backend/internal/service/organization/interface.go)
- [backend/internal/service/organization/service.go](backend/internal/service/organization/service.go)
- [backend/migrations/000053_fix_missing_subscriptions.down.sql](backend/migrations/000053_fix_missing_subscriptions.down.sql)
- [backend/migrations/000053_fix_missing_subscriptions.up.sql](backend/migrations/000053_fix_missing_subscriptions.up.sql)
- [web-admin/src/app/(dashboard)/organizations/[id]/_components/subscription-section.tsx](web-admin/src/app/(dashboard)/organizations/[id]/_components/subscription-section.tsx)

</details>



This page covers the backend billing service: subscription lifecycle management, plan definitions, seat tracking, payment provider integration (Stripe, LemonSqueezy), and the admin API used to manage subscriptions. It also describes how subscriptions are created automatically when an organization is provisioned.

For the web admin UI that consumes this API, see [Web Admin](#6). For organization creation and membership management, see the Organization Service section of [Backend](#2).

---

## Overview

Every organization in AgentsMesh has exactly one `Subscription` record. The subscription controls:

- Which **plan** the organization is on (feature limits, quotas)
- The current **status** (trialing, active, frozen, canceled)
- The **billing cycle** (monthly or yearly)
- The number of **seats** purchased
- Optional **custom quota overrides** that supersede plan defaults

Subscriptions are created automatically during organization provisioning with a 30-day trial period. Admins can manage subscriptions directly via the internal admin REST API without touching payment providers.

---

## Domain Model

The core types live in `backend/internal/domain/billing/`.

### `Subscription` fields

| Field | Type | Description |
|---|---|---|
| `OrganizationID` | `int64` | FK to `organizations` |
| `PlanID` | `int64` | FK to `subscription_plans` |
| `Status` | `string` | `trialing`, `active`, `frozen`, `canceled`, `expired` |
| `BillingCycle` | `string` | `monthly` or `yearly` |
| `CurrentPeriodStart` | `time.Time` | Start of active billing period |
| `CurrentPeriodEnd` | `time.Time` | End of active billing period |
| `SeatCount` | `int` | Purchased seat count |
| `AutoRenew` | `bool` | Auto-renewal flag |
| `CancelAtPeriodEnd` | `bool` | Scheduled cancellation at period end |
| `DowngradeToPlan` | `*string` | Pending downgrade target (takes effect at period end) |
| `NextBillingCycle` | `*string` | Cycle change queued for next renewal |
| `CustomQuotas` | `JSONB` | Per-resource limit overrides |
| `FrozenAt` | `*time.Time` | When the subscription was frozen |
| `CanceledAt` | `*time.Time` | When the subscription was canceled |
| `StripeSubscriptionID` | `*string` | Stripe subscription ID |
| `LemonSqueezySubscriptionID` | `*string` | LemonSqueezy subscription ID |
| `AlipayAgreementNo` | `*string` | Alipay agreement number |
| `WeChatContractID` | `*string` | WeChat Pay contract ID |
| `PaymentProvider` | `*string` | Denormalized provider label |

### `SubscriptionPlan` fields

| Field | Type | Description |
|---|---|---|
| `Name` | `string` | Identifier (e.g. `"based"`) |
| `DisplayName` | `string` | Human-readable label |
| `PricePerSeatMonthly` | `float64` | Monthly seat price |
| `PricePerSeatYearly` | `float64` | Yearly seat price |
| `IncludedPodMinutes` | `int` | Pod compute minutes per period |
| `MaxUsers` | `int` | Max members (`-1` = unlimited) |
| `MaxRunners` | `int` | Max connected runners |
| `MaxConcurrentPods` | `int` | Max pods running simultaneously |
| `MaxRepositories` | `int` | Max repositories |
| `Features` | `JSONB` | Feature flags for the plan |
| `IsActive` | `bool` | Whether new subscriptions can use this plan |

### Status constants

Defined in `backend/internal/domain/billing/` and used throughout:

```
SubscriptionStatusTrialing  = "trialing"
SubscriptionStatusActive    = "active"
SubscriptionStatusFrozen    = "frozen"
SubscriptionStatusCanceled  = "canceled"
SubscriptionStatusExpired   = "expired"

BillingCycleMonthly = "monthly"
BillingCycleYearly  = "yearly"

PlanBased         = "based"
DefaultTrialDays  = 30
```

Sources: [backend/internal/service/billing/service.go:1-128](), [backend/internal/service/billing/subscription.go:1-50]()

---

## Service Layer

**Billing service struct** (`billing.Service`) is in [backend/internal/service/billing/service.go]().

### Constructors

| Constructor | Use case |
|---|---|
| `NewService(db, stripeKey)` | Testing; minimal payment setup |
| `NewServiceWithConfig(db, appConfig)` | Production; initializes all providers via `payment.Factory` |

`NewServiceWithConfig` reads `appConfig.Payment` to configure:
- Stripe (`cfg.StripeEnabled()` → sets `stripe.Key` and `stripeClient`)
- LemonSqueezy (via `payment.NewFactoryWithDB`)
- Alipay / WeChat (via `payment.Factory`)

[backend/internal/service/billing/service.go:61-85]()

### Payment provider abstraction

The `StripeClient` interface allows mock injection for testing via `SetStripeClient`. The `payment.Factory` (returned by `GetPaymentFactory`) wraps the LemonSqueezy, Alipay, and WeChat providers behind a common `SubscriptionProvider` interface, accessed internally via `getSubscriptionProvider()`.

The `paymentConfig.DeploymentType` field drives currency selection: `"cn"` deployment uses `CurrencyCNY`; otherwise `CurrencyUSD`.

[backend/internal/service/billing/subscription.go:274-308]()

---

## Subscription Lifecycle

**State machine diagram:**

```mermaid
stateDiagram-v2
    [*] --> "trialing": "CreateTrialSubscription"
    "trialing" --> "active": "AdminRenew / UpgradePlan"
    "trialing" --> "frozen": "FreezeSubscription"
    "trialing" --> "canceled": "AdminCancelSubscription"
    "active" --> "frozen": "FreezeSubscription"
    "active" --> "canceled": "AdminCancelSubscription"
    "active" --> "active": "AdminRenew / AdminUpdatePlan"
    "frozen" --> "active": "UnfreezeSubscription"
    "frozen" --> "canceled": "AdminCancelSubscription"
    "canceled" --> "active": "AdminRenew (reactivates)"
    "active" --> "expired": "period_end passed (no renewal)"
```

Sources: [backend/internal/service/billing/subscription.go:62-236]()

### Key service operations

| Method | Description |
|---|---|
| `GetSubscription(ctx, orgID)` | Fetches subscription with `Plan` preloaded |
| `CreateSubscription(ctx, orgID, planName)` | Creates a 1-month active subscription |
| `CreateTrialSubscription(ctx, orgID, planName, trialDays)` | Creates a trial subscription (uses own DB conn) |
| `CreateTrialSubscriptionTx(ctx, tx, orgID, planName, trialDays)` | Same, but within a caller-supplied `*gorm.DB` transaction |
| `AdminCreateSubscription(ctx, orgID, planName, months)` | Admin-only; errors if subscription already exists |
| `AdminUpdatePlan(ctx, orgID, planName)` | Immediate plan change; clears any pending downgrade |
| `AdminRenew(ctx, orgID, months)` | Extends period; reactivates frozen/canceled status |
| `AdminCancelSubscription(ctx, orgID)` | Sets `status=canceled`; does not call payment APIs |
| `UpgradePlan(ctx, orgID, planName)` | Upgrades via provider API if `LemonSqueezySubscriptionID` is set |
| `UpdateSubscription(ctx, orgID, planName)` | Routes to upgrade or scheduled-downgrade logic |
| `FreezeSubscription(ctx, orgID)` | Sets `status=frozen`, records `frozen_at` |
| `UnfreezeSubscription(ctx, orgID, cycle)` | Sets `status=active` |
| `AdminSetSeatCount(ctx, orgID, count)` | Directly sets `seat_count` |
| `SetNextBillingCycle(ctx, orgID, cycle)` | Queues a cycle change for next renewal |
| `SetAutoRenew(ctx, orgID, bool)` | Updates `auto_renew` flag |
| `SetCustomQuota(ctx, orgID, resource, limit)` | Sets a per-resource override in `custom_quotas` JSONB |
| `GetSeatUsage(ctx, orgID)` | Returns `SeatUsage{TotalSeats, UsedSeats, AvailableSeats}` |
| `ListPlans(ctx)` | Returns all active `SubscriptionPlan` records |
| `GetPlan(ctx, planName)` | Fetches plan by name |
| `GetPlanByID(ctx, id)` | Fetches plan by ID |
| `GetPlanPriceByID(ctx, planID, currency)` | Fetches price + LemonSqueezy variant IDs for the plan |

Sources: [backend/internal/service/billing/subscription.go:1-400]()

---

## Organization Integration

When `organization.Service.Create` runs, it opens a database transaction that:

1. Inserts the `Organization` row
2. Inserts the `OrganizationMember` (owner)
3. Calls `billingService.CreateTrialSubscriptionTx` (within the same transaction)

Using the `Tx` variant is essential: the billing service uses its own `*gorm.DB` connection, which cannot see uncommitted rows created by the caller's transaction. Without this, the foreign-key constraint `subscriptions.organization_id_fkey` would fail.

[backend/internal/service/organization/service.go:70-96]()

The `Organization` struct also carries two denormalized fields — `SubscriptionPlan` and `SubscriptionStatus` — that are kept in sync whenever the billing service updates the canonical `subscriptions` row. This allows fast reads of subscription state without a join.

[backend/internal/domain/organization/organization.go:24-27]()

**Organization creation flow diagram:**

```mermaid
sequenceDiagram
    participant "orgSvc.Create" as "orgSvc.Create"
    participant "gorm.Transaction" as "gorm.Transaction"
    participant "billingSvc.CreateTrialSubscriptionTx" as "billingSvc.CreateTrialSubscriptionTx"
    participant "DB" as "PostgreSQL"

    "orgSvc.Create" ->> "gorm.Transaction": "BEGIN"
    "gorm.Transaction" ->> "DB": "INSERT organizations"
    "gorm.Transaction" ->> "DB": "INSERT organization_members (owner)"
    "gorm.Transaction" ->> "billingSvc.CreateTrialSubscriptionTx": "orgID, planName=based, trialDays=30"
    "billingSvc.CreateTrialSubscriptionTx" ->> "DB": "SELECT subscription_plans WHERE name=based"
    "billingSvc.CreateTrialSubscriptionTx" ->> "DB": "INSERT subscriptions (status=trialing, period=30d)"
    "gorm.Transaction" ->> "DB": "COMMIT"
```

Sources: [backend/internal/service/organization/service.go:53-103](), [backend/internal/service/billing/subscription.go:56-91]()

---

## Upgrade and Downgrade Logic

The `UpdateSubscription` method distinguishes upgrade vs. downgrade by comparing `PricePerSeatMonthly`:

- **Downgrade** (`newPlan.Price < currentPlan.Price`): Sets `downgrade_to_plan` field; takes effect at period end. Blocked if current `seat_count` exceeds `newPlan.MaxUsers`.
- **Upgrade** (`newPlan.Price > currentPlan.Price`): Immediate. If either plan is free (`price == 0`), the DB is updated directly. For paid-to-paid upgrades via LemonSqueezy, `UpgradePlan` calls `provider.UpdateSubscriptionPlan` with the correct variant ID before updating the local DB.

`UpgradePlan` selects the LemonSqueezy variant ID by matching the subscription's current `BillingCycle` against `PlanPrice.LemonSqueezyVariantIDMonthly` or `PlanPrice.LemonSqueezyVariantIDYearly`.

[backend/internal/service/billing/subscription.go:238-334]()

---

## Organization Synchronization

Several operations synchronize the denormalized `subscription_plan` and `subscription_status` columns in the `organizations` table:

| Method | Synced fields |
|---|---|
| `AdminCreateSubscription` | `subscription_plan`, `subscription_status` |
| `AdminUpdatePlan` | `subscription_plan` |
| `AdminRenew` | `subscription_status` |
| `AdminCancelSubscription` | `subscription_status` |
| `UpgradePlan` | `subscription_plan` |
| `UpdateSubscription` (free plan) | via `syncOrganizationSubscription` |

These use raw `UPDATE` calls to `organizations` (`Table("organizations").Where("id=?").Updates(...)`) executed after the main subscriptions table update.

Sources: [backend/internal/service/billing/subscription.go:128-138](), [backend/internal/service/billing/subscription.go:166-174]()

---

## Admin REST API

The `SubscriptionHandler` in [backend/internal/api/rest/v1/admin/subscriptions.go]() registers routes under `/organizations/:id/subscription` via `RegisterRoutes`.

**Route map:**

```mermaid
graph LR
    base["/organizations/:id/subscription"]
    base --> getR["GET / → GetSubscription"]
    base --> getPlans["GET /plans → ListPlans"]
    base --> create["POST /create → AdminCreateSubscription"]
    base --> putPlan["PUT /plan → AdminUpdatePlan"]
    base --> putSeats["PUT /seats → AdminUpdateSeats"]
    base --> putCycle["PUT /cycle → AdminUpdateCycle"]
    base --> freeze["POST /freeze → Freeze"]
    base --> unfreeze["POST /unfreeze → Unfreeze"]
    base --> cancel["POST /cancel → Cancel"]
    base --> renew["POST /renew → AdminRenew"]
    base --> autorenew["PUT /auto-renew → SetAutoRenew"]
    base --> quotas["PUT /quotas → SetCustomQuota"]
```

Sources: [backend/internal/api/rest/v1/admin/subscriptions.go:31-47]()

### `subscriptionResponse` shape

The response helper `subscriptionResponse` serializes both the subscription and the current `SeatUsage`. Key fields:

```
id, organization_id, plan_id, status, billing_cycle,
current_period_start, current_period_end, auto_renew,
seat_count, cancel_at_period_end, custom_quotas,
payment_provider, payment_method,
has_stripe, has_alipay, has_wechat, has_lemonsqueezy,
canceled_at, frozen_at, downgrade_to_plan, next_billing_cycle,
plan { id, name, display_name, price_per_seat_monthly, ... },
seat_usage { total_seats, used_seats, available_seats }
```

[backend/internal/api/rest/v1/admin/subscriptions.go:417-474]()

### All operations are audit-logged

Every handler calls `h.logAction(c, action, TargetTypeSubscription, orgID, oldSub, newSub)` before returning, which delegates to `LogAdminAction`. This stores before/after snapshots in the admin audit log.

[backend/internal/api/rest/v1/admin/subscriptions.go:407-408]()

---

## Custom Quotas

Custom quotas are stored as a JSONB map on `Subscription.CustomQuotas`. They override plan-level limits for individual resources. Supported resources:

| Resource key | Plan field overridden |
|---|---|
| `users` | `MaxUsers` |
| `runners` | `MaxRunners` |
| `concurrent_pods` | `MaxConcurrentPods` |
| `repositories` | `MaxRepositories` |
| `pod_minutes` | `IncludedPodMinutes` |

A value of `-1` means unlimited. Set via `SetCustomQuota(ctx, orgID, resource, limit)`.

Sources: [web-admin/src/app/(dashboard)/organizations/[id]/_components/subscription-section.tsx:43-43](), [backend/internal/api/rest/v1/admin/subscriptions.go:372-404]()

---

## Data Migration: Missing Subscriptions

Migration `000053` backfills `subscriptions` rows for any organizations that were created before the billing service was wired into the organization service. It inserts a 30-day trialing subscription on the `based` plan for every organization that lacks one.

[backend/migrations/000053_fix_missing_subscriptions.up.sql:1-21]()

The corresponding down migration is a no-op to avoid re-introducing the data inconsistency.

---

## Component Diagram

```mermaid
graph TD
    subgraph "REST Layer"
        SubscriptionHandler["SubscriptionHandler\n(admin/subscriptions.go)"]
    end

    subgraph "Service Layer"
        BillingService["billing.Service\n(service/billing/)"]
        OrgService["organization.Service\n(service/organization/)"]
        PaymentFactory["payment.Factory\n(service/payment/)"]
        StripeClient["StripeClient\n(interface)"]
    end

    subgraph "Domain"
        Subscription["billing.Subscription"]
        SubscriptionPlan["billing.SubscriptionPlan"]
        Organization["organization.Organization\n(SubscriptionPlan+Status fields)"]
    end

    subgraph "External"
        Stripe["Stripe API"]
        LemonSqueezy["LemonSqueezy API"]
    end

    SubscriptionHandler --> BillingService
    OrgService --> BillingService
    BillingService --> Subscription
    BillingService --> SubscriptionPlan
    BillingService --> Organization
    BillingService --> PaymentFactory
    BillingService --> StripeClient
    PaymentFactory --> LemonSqueezy
    StripeClient --> Stripe
```

Sources: [backend/internal/service/billing/service.go:32-100](), [backend/internal/service/organization/service.go:20-43](), [backend/internal/api/rest/v1/admin/subscriptions.go:16-28]()

---

# Page: Configuration

# Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/internal/api/rest/internal/relay_registration.go](backend/internal/api/rest/internal/relay_registration.go)
- [backend/internal/api/rest/internal/relay_registration_test.go](backend/internal/api/rest/internal/relay_registration_test.go)
- [backend/internal/config/config.go](backend/internal/config/config.go)
- [backend/internal/config/config_relay.go](backend/internal/config/config_relay.go)
- [backend/internal/service/relay/dns_service.go](backend/internal/service/relay/dns_service.go)
- [backend/internal/service/relay/dns_service_mock_test.go](backend/internal/service/relay/dns_service_mock_test.go)
- [backend/internal/service/relay/dns_service_sanitize_test.go](backend/internal/service/relay/dns_service_sanitize_test.go)
- [backend/migrations/000033_move_preparation_script_to_repository.down.sql](backend/migrations/000033_move_preparation_script_to_repository.down.sql)
- [backend/migrations/000033_move_preparation_script_to_repository.up.sql](backend/migrations/000033_move_preparation_script_to_repository.up.sql)
- [docs/images/logo.svg](docs/images/logo.svg)
- [relay/.env.example](relay/.env.example)
- [relay/internal/config/config.go](relay/internal/config/config.go)
- [relay/internal/config/config_test.go](relay/internal/config/config_test.go)
- [web-admin/.env.example](web-admin/.env.example)
- [web-admin/next.config.ts](web-admin/next.config.ts)
- [web-admin/src/lib/api/base.ts](web-admin/src/lib/api/base.ts)
- [web/next.config.ts](web/next.config.ts)
- [web/src/lib/env.ts](web/src/lib/env.ts)

</details>



This page covers the backend configuration system: how the backend and relay services load their settings from environment variables, and how the web frontends derive service URLs. The central design principle is a **unified domain pattern** — all services share `PRIMARY_DOMAIN` and `USE_HTTPS` as a single source of truth for URL derivation.

For frontend URL resolution logic in detail, see [Environment and API Configuration](#5.6). For relay session and heartbeat settings that affect runtime behavior, see [Backend Registration and Heartbeat](#4.2).

---

## The Unified Domain Pattern

All four services (Backend, Relay, Web, Web-Admin) share the same two root variables:

| Variable | Type | Example |
|---|---|---|
| `PRIMARY_DOMAIN` | string | `agentsmesh.ai`, `localhost:10000` |
| `USE_HTTPS` | bool | `true` / `false` |

Every service-specific URL (API base URL, WebSocket URL, relay public URL) is derived from these two values. Explicit per-URL environment variables take priority when set, allowing overrides for non-standard deployments.

**Unified Domain Derivation**

```mermaid
flowchart TD
    PD["PRIMARY_DOMAIN env var"]
    UH["USE_HTTPS env var"]
    
    PD --> BackendLoad["backend/internal/config/config.go\nLoad()"]
    UH --> BackendLoad
    BackendLoad --> BC["Config.PrimaryDomain\nConfig.UseHTTPS"]
    
    PD --> RelayLoad["relay/internal/config/config.go\nLoad()"]
    UH --> RelayLoad
    RelayLoad --> RC["Config.PrimaryDomain\nConfig.UseHTTPS"]
    RC --> RelayURL["Config.Relay.URL\nws(s)://domain/relay"]
    
    PD --> NextConfigWeb["web/next.config.ts\nenv block"]
    UH --> NextConfigWeb
    NextConfigWeb --> NPUB_WEB["NEXT_PUBLIC_PRIMARY_DOMAIN\nNEXT_PUBLIC_USE_HTTPS"]
    NPUB_WEB --> EnvTS["web/src/lib/env.ts\ngetApiBaseUrl()\ngetWsBaseUrl()"]
    
    PD --> NextConfigAdmin["web-admin/next.config.ts\nenv block"]
    UH --> NextConfigAdmin
    NextConfigAdmin --> NPUB_ADMIN["NEXT_PUBLIC_PRIMARY_DOMAIN\nNEXT_PUBLIC_USE_HTTPS"]
    NPUB_ADMIN --> AdminBase["web-admin/src/lib/api/base.ts\ngetApiUrl()"]
```

Sources: [backend/internal/config/config.go:29-32](), [relay/internal/config/config.go:30-36](), [web/next.config.ts:27-33](), [web-admin/next.config.ts:11-17]()

---

## Backend Configuration

### `Config` Struct

The top-level `Config` struct is defined in [backend/internal/config/config.go:11-32]() and contains named sub-structs for each subsystem, plus the two unified domain fields at the root level.

```mermaid
classDiagram
    class Config {
        +PrimaryDomain string
        +UseHTTPS bool
        +Server ServerConfig
        +Database DatabaseConfig
        +Redis RedisConfig
        +JWT JWTConfig
        +OAuth OAuthConfig
        +Webhook WebhookConfig
        +Log LogConfig
        +Email EmailConfig
        +Storage StorageConfig
        +Payment PaymentConfig
        +PKI PKIConfig
        +GRPC GRPCConfig
        +Admin AdminConfig
        +Relay RelayConfig
        +Runner RunnerConfig
        +Marketplace MarketplaceConfig
    }
    class ServerConfig {
        +Address string
        +Debug bool
        +CORSAllowedOrigins []string
        +InternalAPISecret string
    }
    class DatabaseConfig {
        +Host string
        +Port int
        +User string
        +Password string
        +DBName string
        +SSLMode string
        +ReplicaDSNs []string
    }
    class RedisConfig {
        +URL string
        +Host string
        +Port int
        +Password string
        +DB int
    }
    class GRPCConfig {
        +Address string
        +Endpoint string
    }
    class PKIConfig {
        +CACertFile string
        +CAKeyFile string
        +ServerCertFile string
        +ServerKeyFile string
        +ValidityDays int
    }
    class RelayConfig {
        +BaseDomain string
        +DNS DNSConfig
        +ACME ACMEConfig
    }
    class MarketplaceConfig {
        +SyncInterval Duration
        +RegistryEnabled bool
        +RegistryURL string
    }
    Config --> ServerConfig
    Config --> DatabaseConfig
    Config --> RedisConfig
    Config --> GRPCConfig
    Config --> PKIConfig
    Config --> RelayConfig
    Config --> MarketplaceConfig
```

Sources: [backend/internal/config/config.go:11-32](), [backend/internal/config/config_relay.go:4-41]()

### `Load()` Function

`Load()` [backend/internal/config/config.go:49-234]() constructs the full `Config` by calling environment-variable helper functions. There is no config file; all values come from the process environment.

**Helper functions:**

| Function | Signature | Purpose |
|---|---|---|
| `getEnv` | `(key, default string) string` | Returns env var or default |
| `getEnvInt` | `(key string, default int) int` | Parses integer env var |
| `getEnvBool` | `(key string, default bool) bool` | Parses bool env var (`ParseBool`) |
| `getEnvDuration` | `(key string, default Duration) Duration` | Parses Go duration string |
| `getEnvList` | `(key string, default []string) []string` | Parses comma-separated list |

Sources: [backend/internal/config/config.go:240-296]()

### Backend Environment Variables Reference

| Environment Variable | Config Field | Default | Notes |
|---|---|---|---|
| `PRIMARY_DOMAIN` | `Config.PrimaryDomain` | `localhost:10000` | Shared with all services |
| `USE_HTTPS` | `Config.UseHTTPS` | `false` | Shared with all services |
| `SERVER_ADDRESS` | `Server.Address` | `:8080` | HTTP listen address |
| `DEBUG` | `Server.Debug` | `false` | |
| `CORS_ALLOWED_ORIGINS` | `Server.CORSAllowedOrigins` | `["*"]` | Comma-separated |
| `INTERNAL_API_SECRET` | `Server.InternalAPISecret` | `change-me-internal-secret` | Must change in production |
| `DB_HOST` | `Database.Host` | `localhost` | |
| `DB_PORT` | `Database.Port` | `5432` | |
| `DB_USER` | `Database.User` | `agentsmesh` | |
| `DB_PASSWORD` | `Database.Password` | _(empty)_ | |
| `DB_NAME` | `Database.DBName` | `agentsmesh` | |
| `DB_SSLMODE` | `Database.SSLMode` | `disable` | |
| `DB_REPLICA_DSNS` | `Database.ReplicaDSNs` | _(nil)_ | Comma-separated DSNs |
| `REDIS_URL` | `Redis.URL` | _(empty)_ | Full Redis URL |
| `REDIS_HOST` | `Redis.Host` | `localhost` | |
| `REDIS_PORT` | `Redis.Port` | `6379` | |
| `REDIS_PASSWORD` | `Redis.Password` | _(empty)_ | |
| `JWT_SECRET` | `JWT.Secret` | `change-me-in-production` | Must change in production |
| `JWT_EXPIRATION_HOURS` | `JWT.ExpirationHours` | `24` | |
| `GRPC_ADDRESS` | `GRPC.Address` | `:9090` | gRPC listen address |
| `GRPC_PUBLIC_ENDPOINT` | `GRPC.Endpoint` | _(empty)_ | Endpoint advertised to runners |
| `PKI_CA_CERT_FILE` | `PKI.CACertFile` | _(empty)_ | See [PKI and mTLS](#2.8) |
| `PKI_CA_KEY_FILE` | `PKI.CAKeyFile` | _(empty)_ | |
| `PKI_SERVER_CERT_FILE` | `PKI.ServerCertFile` | _(empty)_ | |
| `PKI_SERVER_KEY_FILE` | `PKI.ServerKeyFile` | _(empty)_ | |
| `PKI_VALIDITY_DAYS` | `PKI.ValidityDays` | `365` | |
| `ADMIN_ENABLED` | `Admin.Enabled` | `true` | |
| `DEPLOYMENT_TYPE` | `Payment.DeploymentType` | `global` | `"global"` or `"cn"` |
| `PAYMENT_MOCK` | `Payment.MockEnabled` | `false` | |
| `STRIPE_SECRET_KEY` | `Payment.Stripe.SecretKey` | _(empty)_ | |
| `LEMONSQUEEZY_API_KEY` | `Payment.LemonSqueezy.APIKey` | _(empty)_ | |
| `STORAGE_ENDPOINT` | `Storage.Endpoint` | _(empty)_ | S3-compatible endpoint |
| `STORAGE_BUCKET` | `Storage.Bucket` | `agentsmesh` | |
| `STORAGE_ACCESS_KEY` | `Storage.AccessKey` | _(empty)_ | |
| `STORAGE_SECRET_KEY` | `Storage.SecretKey` | _(empty)_ | |
| `EMAIL_PROVIDER` | `Email.Provider` | `console` | `"console"` or `"resend"` |
| `RESEND_API_KEY` | `Email.ResendKey` | _(empty)_ | |
| `LOG_LEVEL` | `Log.Level` | `info` | |
| `LOG_FORMAT` | `Log.Format` | `text` | |
| `MARKETPLACE_SYNC_INTERVAL` | `Marketplace.SyncInterval` | `1h` | Go duration string |
| `MCP_REGISTRY_ENABLED` | `Marketplace.RegistryEnabled` | `true` | |
| `MCP_REGISTRY_URL` | `Marketplace.RegistryURL` | `https://registry.modelcontextprotocol.io` | |

Sources: [backend/internal/config/config.go:49-234]()

### Relay Management Configuration (Backend-side)

The backend's `RelayConfig` [backend/internal/config/config_relay.go:4-41]() configures how the backend manages relay DNS records and TLS certificates — distinct from the relay service's own configuration.

`RelayConfig.IsEnabled()` returns `true` only when both `BaseDomain` and `DNS.Provider` are non-empty.

| Environment Variable | Config Field | Purpose |
|---|---|---|
| `RELAY_BASE_DOMAIN` | `Relay.BaseDomain` | Base for relay subdomains (e.g., `relay.agentsmesh.cn`) |
| `DNS_PROVIDER` | `Relay.DNS.Provider` | `"cloudflare"` or `"aliyun"` |
| `CLOUDFLARE_API_TOKEN` | `Relay.DNS.CloudflareAPIToken` | Cloudflare DNS token |
| `CLOUDFLARE_ZONE_ID` | `Relay.DNS.CloudflareZoneID` | Cloudflare zone ID |
| `ALIYUN_ACCESS_KEY_ID` | `Relay.DNS.AliyunAccessKeyID` | Aliyun DNS access key |
| `ALIYUN_ACCESS_KEY_SECRET` | `Relay.DNS.AliyunAccessKeySecret` | Aliyun DNS secret |
| `ACME_ENABLED` | `Relay.ACME.Enabled` | Enable Let's Encrypt management |
| `ACME_EMAIL` | `Relay.ACME.Email` | Let's Encrypt registration email |
| `ACME_DIRECTORY_URL` | `Relay.ACME.DirectoryURL` | ACME directory (empty = production LE) |
| `ACME_STORAGE_DIR` | `Relay.ACME.StorageDir` | Certificate storage path |
| `ACME_STAGING` | `Relay.ACME.Staging` | Use LE staging environment |

Sources: [backend/internal/config/config_relay.go:1-50](), [backend/internal/config/config.go:215-233]()

---

## Relay Service Configuration

The relay service uses [Viper](https://github.com/spf13/viper) for configuration, defined in [relay/internal/config/config.go:14-36]().

### `Config` Struct (Relay)

```mermaid
classDiagram
    class Config {
        +PrimaryDomain string
        +UseHTTPS bool
        +Server ServerConfig
        +JWT JWTConfig
        +Backend BackendConfig
        +Session SessionConfig
        +Relay RelayConfig
    }
    class ServerConfig {
        +Host string
        +Port int
        +ReadTimeout Duration
        +WriteTimeout Duration
        +TLS TLSConfig
    }
    class TLSConfig {
        +Enabled bool
        +CertFile string
        +KeyFile string
    }
    class BackendConfig {
        +URL string
        +InternalAPISecret string
        +HeartbeatInterval Duration
    }
    class SessionConfig {
        +KeepAliveDuration Duration
        +MaxBrowsersPerPod int
        +RunnerReconnectTimeout Duration
        +BrowserReconnectTimeout Duration
        +PendingConnectionTimeout Duration
        +OutputBufferSize int
        +OutputBufferCount int
    }
    class RelayConfig_relay {
        +ID string
        +Name string
        +URL string
        +InternalURL string
        +Region string
        +Capacity int
        +AutoIP bool
    }
    Config --> ServerConfig
    Config --> BackendConfig
    Config --> SessionConfig
    Config --> RelayConfig_relay
    ServerConfig --> TLSConfig
```

Sources: [relay/internal/config/config.go:14-87]()

### Relay URL Derivation

The relay's `Load()` function [relay/internal/config/config.go:90-221]() derives `Relay.URL` automatically when `RELAY_URL` is not explicitly set:

**Relay URL derivation logic**

```mermaid
flowchart TD
    A["RELAY_URL set?"] -- "yes" --> B["Use RELAY_URL as-is"]
    A -- "no" --> C["PRIMARY_DOMAIN set?"]
    C -- "yes" --> D["USE_HTTPS == true?"]
    D -- "yes" --> E["wss://PRIMARY_DOMAIN/relay"]
    D -- "no" --> F["ws://PRIMARY_DOMAIN/relay"]
    C -- "no" --> G["Server.TLS.Enabled?"]
    G -- "yes" --> H["wss://localhost:PORT"]
    G -- "no" --> I["ws://localhost:PORT"]
```

Sources: [relay/internal/config/config.go:198-215]()

### Relay Environment Variables Reference

The relay uses Viper with `RELAY_` prefix auto-mapping, plus explicit mappings for unprefixed variable names. Both `FOO` and `RELAY_FOO` are accepted for most settings.

| Environment Variable | Config Field | Default | Notes |
|---|---|---|---|
| `PRIMARY_DOMAIN` | `PrimaryDomain` | _(empty)_ | Shared unified domain |
| `USE_HTTPS` | `UseHTTPS` | `false` | Shared unified domain |
| `JWT_SECRET` | `JWT.Secret` | _(required)_ | Must match backend |
| `JWT_ISSUER` | `JWT.Issuer` | `agentsmesh-relay` | |
| `INTERNAL_API_SECRET` | `Backend.InternalAPISecret` | _(required)_ | Must match backend |
| `SERVER_HOST` | `Server.Host` | `0.0.0.0` | |
| `SERVER_PORT` | `Server.Port` | `8090` | |
| `TLS_ENABLED` | `Server.TLS.Enabled` | `false` | |
| `TLS_CERT_FILE` | `Server.TLS.CertFile` | _(empty)_ | |
| `TLS_KEY_FILE` | `Server.TLS.KeyFile` | _(empty)_ | |
| `BACKEND_URL` | `Backend.URL` | `http://backend:8080` | |
| `HEARTBEAT_INTERVAL` | `Backend.HeartbeatInterval` | `10s` | |
| `KEEP_ALIVE_DURATION` | `Session.KeepAliveDuration` | `30s` | |
| `MAX_BROWSERS_PER_POD` | `Session.MaxBrowsersPerPod` | `10` | |
| `RUNNER_RECONNECT_TIMEOUT` | `Session.RunnerReconnectTimeout` | `30s` | |
| `BROWSER_RECONNECT_TIMEOUT` | `Session.BrowserReconnectTimeout` | `30s` | |
| `PENDING_CONNECTION_TIMEOUT` | `Session.PendingConnectionTimeout` | `60s` | |
| `OUTPUT_BUFFER_SIZE` | `Session.OutputBufferSize` | `262144` (256 KB) | Bytes |
| `OUTPUT_BUFFER_COUNT` | `Session.OutputBufferCount` | `200` | Messages |
| `RELAY_ID` | `Relay.ID` | `relay-<hostname>` | Auto-generated if empty |
| `RELAY_NAME` | `Relay.Name` | _(empty)_ | Used for DNS sub-domain |
| `RELAY_URL` | `Relay.URL` | _derived_ | Derived from `PRIMARY_DOMAIN` |
| `RELAY_INTERNAL_URL` | `Relay.InternalURL` | _(empty)_ | Docker-internal URL for runners |
| `RELAY_REGION` | `Relay.Region` | `default` | |
| `RELAY_CAPACITY` | `Relay.Capacity` | `1000` | Max concurrent sessions |
| `RELAY_AUTO_IP` | `Relay.AutoIP` | `false` | Auto-detect public IP |

Sources: [relay/internal/config/config.go:90-165](), [relay/.env.example:1-58]()

The relay config also supports a YAML file at `./config.yaml` or `/etc/relay/config.yaml`, read via Viper's `ReadInConfig` [relay/internal/config/config.go:167-176]().

---

## Frontend Configuration

Both `web` and `web-admin` follow the same pattern. `PRIMARY_DOMAIN` and `USE_HTTPS` are mapped at build time to `NEXT_PUBLIC_` variables, but using placeholder strings (`__PRIMARY_DOMAIN__`, `__USE_HTTPS__`) so the Docker entrypoint can perform runtime string substitution in the built output.

**Next.js build-time env injection**

```mermaid
flowchart LR
    PD["PRIMARY_DOMAIN\n(server-side env)"]
    UH["USE_HTTPS\n(server-side env)"]
    
    PD --> NCC["next.config.ts\nenv block"]
    UH --> NCC
    NCC --> NPD["NEXT_PUBLIC_PRIMARY_DOMAIN\n= value or __PRIMARY_DOMAIN__"]
    NCC --> NUH["NEXT_PUBLIC_USE_HTTPS\n= value or __USE_HTTPS__"]
    
    NPD --> GAPB["getApiBaseUrl()\nweb/src/lib/env.ts"]
    NUH --> GAPB
    NPD --> GWSB["getWsBaseUrl()\nweb/src/lib/env.ts"]
    NUH --> GWSB
    NPD --> GOAB["getOAuthBaseUrl()\nweb/src/lib/env.ts"]
```

Sources: [web/next.config.ts:27-33](), [web-admin/next.config.ts:11-17](), [web/src/lib/env.ts:46-80]()

The `getPrimaryDomain()` helper [web/src/lib/env.ts:46-50]() filters out unreplaced placeholders by checking if the value starts with `__`, treating them as absent.

### Frontend URL Resolution Priority

Each exported function in `web/src/lib/env.ts` applies the same resolution order:

| Priority | Condition | Result |
|---|---|---|
| 1 | `NEXT_PUBLIC_API_URL=""` | Returns `""` (relative path; proxied by Next.js rewrites in dev) |
| 2 | `NEXT_PUBLIC_API_URL` is set | Returns that value |
| 3 | Running in browser (`window` defined) | Returns `window.location.origin` |
| 4 | `PRIMARY_DOMAIN` set (SSR) | Derives `http(s)://PRIMARY_DOMAIN` |
| 5 | Fallback | `http://localhost:10000` |

For WebSocket URLs (`getWsBaseUrl()`), the same order applies with `ws`/`wss` protocols. Note: when `NEXT_PUBLIC_API_URL=""` (local dev mode), `getWsBaseUrl()` cannot use `window.location` (which points at the Next.js dev server) and instead falls back to `PRIMARY_DOMAIN` derivation.

Sources: [web/src/lib/env.ts:92-177]()

### Frontend Environment Variables

| Variable | Used by | Purpose |
|---|---|---|
| `PRIMARY_DOMAIN` | `web`, `web-admin` | Mapped to `NEXT_PUBLIC_PRIMARY_DOMAIN` at build time |
| `USE_HTTPS` | `web`, `web-admin` | Mapped to `NEXT_PUBLIC_USE_HTTPS` at build time |
| `NEXT_PUBLIC_API_URL` | `web` | Explicit API base URL override |
| `NEXT_PUBLIC_WS_URL` | `web` | Explicit WebSocket URL override |
| `NEXT_PUBLIC_OAUTH_URL` | `web` | Explicit OAuth redirect URL override |
| `API_PROXY_TARGET` | `web` (dev only) | Backend URL for Next.js rewrite proxy |
| `ALLOWED_DEV_ORIGINS` | `web` | Comma-separated allowed dev origins |

Sources: [web/src/lib/env.ts:1-36](), [web/next.config.ts:8-58](), [web-admin/.env.example:1-28]()

---

## Deployment Scenarios

| Scenario | `PRIMARY_DOMAIN` | `USE_HTTPS` | Notes |
|---|---|---|---|
| Local dev (`dev.sh`) | not set | `false` | `NEXT_PUBLIC_API_URL=""` enables Next.js proxy |
| On-premise (IP-based) | not set | `false` | Frontend uses `window.location.origin` automatically |
| SaaS production | `agentsmesh.ai` | `true` | All services derive HTTPS/WSS URLs |
| Self-hosted with domain | `example.com` | `true` | Same as SaaS pattern |
| Self-hosted local port | `192.168.1.10:10000` | `false` | Port included in domain string |

Sources: [web/src/lib/env.ts:1-36](), [relay/.env.example:1-15](), [web-admin/.env.example:1-15]()

---

# Page: PKI and mTLS

# PKI and mTLS

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/cmd/server/grpc_init.go](backend/cmd/server/grpc_init.go)
- [backend/cmd/server/grpc_init_test.go](backend/cmd/server/grpc_init_test.go)
- [backend/internal/infra/pki/service.go](backend/internal/infra/pki/service.go)
- [backend/internal/infra/pki/service_server.go](backend/internal/infra/pki/service_server.go)
- [backend/internal/infra/pki/service_test.go](backend/internal/infra/pki/service_test.go)
- [runner/internal/client/grpc_connection_options.go](runner/internal/client/grpc_connection_options.go)
- [runner/internal/client/grpc_tls.go](runner/internal/client/grpc_tls.go)

</details>



This page covers the public key infrastructure (PKI) used to authenticate runners to the backend, and how mutual TLS (mTLS) is enforced on the gRPC control-plane connection. For how the gRPC connection itself is managed on the runner side, see [3.3](#3.3). For how the gRPC server handles incoming runner streams, see [2.2](#2.2) and [2.3](#2.3). For the REST API endpoints that expose certificate issuance and renewal, see [2.1](#2.1).

---

## Overview

AgentsMesh uses a private CA (Certificate Authority) to issue certificates exclusively to registered runners. Every runner authenticates to the gRPC server by presenting its client certificate during the TLS handshake. The server validates the certificate chain and cross-checks the serial number against the database before accepting the connection. This replaces bearer-token auth for the long-lived gRPC stream.

**Key responsibilities of the PKI subsystem:**

| Responsibility | Component |
|---|---|
| CA loading and certificate issuance | `pki.Service` (backend) |
| Server TLS certificate provisioning | `pki.Service.generateServerCert` |
| gRPC server mTLS enforcement | `grpcserver.Server` |
| Runner client TLS with hot-reload | `GRPCConnection.createAdvancedTLSCredentials` |
| Certificate renewal (REST-triggered) | `GRPCRunnerHandler` + `RenewCertificate` |
| Revocation checking | `runner.Service.IsCertificateRevoked` |

---

## PKI Service (`pki.Service`)

The `pki.Service` struct in [backend/internal/infra/pki/service.go]() is the central authority on the backend. It is constructed once at startup by `initializePKIAndGRPC` in [backend/cmd/server/grpc_init.go]().

### Data model

```
pki.Service
├── caCert       *x509.Certificate
├── caKey        crypto.PrivateKey
├── caCertPEM    []byte            ← sent to runners on registration
├── serverCert   tls.Certificate   ← used by gRPC server
├── certPool     *x509.CertPool    ← validates runner client certs
└── validityDays int               ← default 365
```

Sources: [backend/internal/infra/pki/service.go:16-23]()

### Configuration (`pki.Config`)

| Field | Type | Purpose |
|---|---|---|
| `CACertFile` | `string` | Path to PEM-encoded CA certificate |
| `CAKeyFile` | `string` | Path to PEM-encoded CA private key |
| `ServerCertFile` | `string` | Optional: path to pre-existing server cert |
| `ServerKeyFile` | `string` | Optional: path to pre-existing server key |
| `ValidityDays` | `int` | Runner cert validity (default: 365) |
| `ServerCertSANs` | `[]string` | Extra DNS SANs for the auto-generated server cert |

Sources: [backend/internal/infra/pki/service.go:26-33]()

### Initialization

`NewService` in [backend/internal/infra/pki/service.go:46-95]() performs the following steps on startup:

1. Read and parse `CACertFile` + `CAKeyFile` via `parseCA`.
2. Build `certPool` from the parsed CA cert (used as the client auth root).
3. Apply default `validityDays = 365` if not set.
4. Call `loadOrGenerateServerCert` — load from `ServerCertFile`/`ServerKeyFile` if they exist, otherwise generate in-memory via `generateServerCert`.

`parseCA` in [backend/internal/infra/pki/service.go:98-133]() accepts PKCS#8, EC, and RSA private key formats for the CA key.

---

## Certificate Issuance

### Runner certificates

`IssueRunnerCertificate(nodeID, orgSlug string)` issues a short-lived client certificate for a runner. The resulting `CertificateInfo` struct is returned to the caller (the REST handler) which writes it to disk on the runner.

**Certificate attributes:**

| X.509 Field | Value |
|---|---|
| `CommonName` | `nodeID` |
| `Organization` | `[orgSlug]` |
| `OrganizationalUnit` | `["runners"]` |
| `ExtKeyUsage` | `ClientAuth` |
| `KeyUsage` | `DigitalSignature` |
| `NotAfter` | `now + validityDays` |

The `SerialNumber` from `CertificateInfo` is stored in the database on the runner record (`CertSerialNumber` column), enabling revocation checks later.

```
CertificateInfo {
    CertPEM      []byte
    KeyPEM       []byte
    SerialNumber string
    Fingerprint  string
    IssuedAt     time.Time
    ExpiresAt    time.Time
}
```

Sources: [backend/internal/infra/pki/service.go:36-43](), [backend/internal/infra/pki/service_test.go:117-152]()

### Certificate validation

`ValidateCertificate(certPEM []byte)` is called during the gRPC handshake. It:

1. Decodes the PEM block.
2. Verifies the certificate chain against `certPool` (the private CA).
3. Returns `(nodeID, orgSlug, serialNumber, error)` extracted from the cert's Subject fields.

A certificate signed by any other CA will fail step 2 with `"certificate verification failed"`.

Sources: [backend/internal/infra/pki/service_test.go:172-241]()

---

## Server Certificate

The gRPC server presents a certificate to the connecting runner. This is either loaded from disk (`ServerCertFile`/`ServerKeyFile`) or generated in-memory by `generateServerCert` in [backend/internal/infra/pki/service_server.go:34-91]().

### Default SANs

The auto-generated server certificate always includes these DNS SANs:

- `localhost`
- `backend`
- `agentmesh-backend`

### Derived SANs

`deriveServerCertSANs(cfg)` in [backend/cmd/server/grpc_init.go:234-259]() appends additional SANs derived from the runtime config:

- Hostname extracted from `cfg.PrimaryDomain` (port stripped)
- Hostname extracted from `cfg.GRPC.Endpoint` URL

Duplicates are deduplicated. Examples:

| Config | Derived SANs |
|---|---|
| `PrimaryDomain="agentsmesh.cn"`, `GRPC.Endpoint="grpcs://api.agentsmesh.cn:9443"` | `agentsmesh.cn`, `api.agentsmesh.cn` |
| `PrimaryDomain="localhost:10000"` | `localhost` (already default) |
| `GRPC.Endpoint="grpcs://grpc.example.com:9443"` | `grpc.example.com` |

> **Note:** The runner's TLS credential layer deliberately skips hostname verification (see [Runner TLS](#runner-side-tls) below), so the server cert SANs do not need to exactly match the dial target. SANs are derived anyway for environments where standard TLS verification is desired.

Sources: [backend/cmd/server/grpc_init.go:227-259](), [backend/internal/infra/pki/service_server.go:34-91](), [backend/internal/infra/pki/service_test.go:268-365]()

---

## PKI Initialization Flow

**Diagram: PKI and gRPC server initialization**

```mermaid
sequenceDiagram
    participant main as "main()"
    participant init as "initializePKIAndGRPC()"
    participant pki as "pki.NewService()"
    participant sans as "deriveServerCertSANs()"
    participant grpc as "grpcserver.NewServer()"
    participant handler as "v1.NewGRPCRunnerHandler()"

    main->>init: "cfg, runnerSvc, orgSvc, ..."
    init->>sans: "cfg"
    sans-->>init: "[]string{domain, grpcHost}"
    init->>pki: "Config{CACertFile, CAKeyFile, ServerCertSANs, ...}"
    pki-->>init: "*pki.Service or error"
    init->>handler: "runnerSvc, pkiService, cfg"
    handler-->>init: "*GRPCRunnerHandler"
    init->>grpc: "ServerDependencies{PKIService, ConnManager, ...}"
    grpc-->>init: "*grpcserver.Server"
    init->>grpc: ".Start()"
```

Sources: [backend/cmd/server/grpc_init.go:22-107]()

---

## mTLS Enforcement on the gRPC Server

The gRPC server is configured with `tls.RequireAndVerifyClientCert` mode. When a runner connects:

1. The runner presents its client certificate (CN=nodeID, O=orgSlug).
2. The gRPC layer verifies the chain against `pki.Service.CACertPool()`.
3. The server-side handler extracts `nodeID` and `orgSlug` from the cert via `ValidateCertificate`.
4. `runner.Service.IsCertificateRevoked(ctx, serialNumber)` is called — if revoked, the stream is rejected.
5. The runner record is fetched from the database by `nodeID` + `orgID` to confirm the runner is enabled.

**Diagram: mTLS handshake and runner identity resolution**

```mermaid
sequenceDiagram
    participant runner as "GRPCConnection (runner)"
    participant grpcsrv as "grpcserver.Server"
    participant pki as "pki.Service"
    participant runnersvc as "runner.Service"
    participant db as "Database"

    runner->>grpcsrv: "TLS ClientHello + client cert"
    grpcsrv->>pki: "ValidateCertificate(certPEM)"
    pki-->>grpcsrv: "nodeID, orgSlug, serialNumber"
    grpcsrv->>runnersvc: "IsCertificateRevoked(serialNumber)"
    runnersvc->>db: "SELECT revoked WHERE serial=..."
    db-->>runnersvc: "false"
    runnersvc-->>grpcsrv: "false"
    grpcsrv->>runnersvc: "GetByNodeIDAndOrgID(nodeID, orgID)"
    runnersvc-->>grpcsrv: "RunnerInfo{IsEnabled: true}"
    grpcsrv-->>runner: "stream accepted"
```

Sources: [backend/cmd/server/grpc_init.go:109-165](), [backend/internal/infra/pki/service.go:135-154]()

---

## Runner-Side TLS

The runner manages its own certificate files on disk. These are loaded and presented to the server on each connection. The relevant code lives in [runner/internal/client/grpc_tls.go]().

### Certificate files

The `GRPCConnection` struct references three file paths:

| Field | Content |
|---|---|
| `certFile` | Runner client certificate (PEM) |
| `keyFile` | Runner client private key (PEM) |
| `caFile` | Backend CA certificate (PEM) |

### Three-tier TLS credential fallback

`createAdvancedTLSCredentials()` is called when establishing the gRPC connection. It attempts three strategies in order:

**Diagram: TLS credential provider selection**

```mermaid
flowchart TD
    start["createAdvancedTLSCredentials()"]
    idprov["pemfile.NewProvider(CertFile, KeyFile)\n refresh=1h"]
    rootprov["pemfile.NewProvider(RootFile=caFile)\n refresh=24h"]
    advanced["advancedtls.NewClientCreds()\nIdentityProvider + RootProvider"]
    staticca["createStaticCACredentials()\nos.ReadFile(caFile) -> x509.CertPool"]
    fallback["createFallbackTLSCredentials()\ntls.LoadX509KeyPair + manual VerifyConnection"]
    err1{"error?"}
    err2{"error?"}

    start --> idprov
    idprov --> err1
    err1 -- "yes" --> fallback
    err1 -- "no" --> rootprov
    rootprov --> err2
    err2 -- "yes" --> staticca
    err2 -- "no" --> advanced
```

Sources: [runner/internal/client/grpc_tls.go:26-73](), [runner/internal/client/grpc_tls.go:77-106](), [runner/internal/client/grpc_tls.go:114-156]()

### Verification mode: chain-only, no hostname check

All three strategies set `VerificationType: advancedtls.CertVerification` (or equivalent) instead of the default `VerificationType: CertAndHostVerification`. This is intentional:

- The server certificate SANs may not include the public-facing hostname (e.g., `api.agentsmesh.cn`).
- SNI is set to the dial target hostname so Traefik can route gRPC traffic correctly.
- The private CA ensures only our own server certificates are trusted — the hostname check is redundant in this trust model.

The fallback path (`createFallbackTLSCredentials`) uses `InsecureSkipVerify: true` combined with a manual `VerifyConnection` callback that performs the chain verification without hostname matching.

Sources: [runner/internal/client/grpc_tls.go:22-73](), [runner/internal/client/grpc_tls.go:108-156]()

### Certificate hot-reloading

When the primary path succeeds, both `pemfile.Provider` instances are stored as `identityProvider` and `rootProvider` on the `GRPCConnection` struct. The `advancedtls` library polls these providers on a timer:

| Provider | File(s) | Refresh interval |
|---|---|---|
| `identityProvider` | `certFile`, `keyFile` | 1 hour |
| `rootProvider` | `caFile` | 24 hours |

When a renewed certificate is written to `certFile`, the running gRPC connection picks it up on the next provider refresh without reconnecting.

Sources: [runner/internal/client/grpc_tls.go:28-47]()

---

## Certificate Renewal

### Renewal loop

`certRenewalChecker(ctx, done)` runs as a background goroutine within the runner. It ticks on `certRenewalCheckInterval` and calls `checkCertificateExpiry()`.

`checkCertificateExpiry` computes days until expiry via `getCertDaysUntilExpiry`:

| Condition | Action |
|---|---|
| `daysUntilExpiry <= certRenewalDays` | Call `renewCertificate()` (REST API) |
| `daysUntilExpiry <= certUrgentDays` | Call `triggerReconnect()` (force reconnect) |

Sources: [runner/internal/client/grpc_tls.go:158-200]()

### Renewal via REST API

`renewCertificate()` calls `RenewCertificate(ctx, RenewalRequest{...})` which posts to the backend REST endpoint handled by `v1.GRPCRunnerHandler`. The `RenewalRequest` carries `ServerURL`, `CertFile`, `KeyFile`, `CAFile`.

On success, the new cert and key PEM are written to `certFile` and `keyFile`. Because `advancedtls` hot-reloads on a 1-hour cycle, no reconnect is required unless the cert is already in the urgent window.

```
RenewalRequest {
    ServerURL string
    CertFile  string
    KeyFile   string
    CAFile    string
}
```

Sources: [runner/internal/client/grpc_tls.go:267-298]()

### Configurable thresholds

These thresholds are set via `GRPCConnectionOption` functions at construction time:

| Option | Field | Meaning |
|---|---|---|
| `WithGRPCCertRenewalDays(n)` | `certRenewalDays` | Days before expiry to trigger REST renewal |
| `WithGRPCCertUrgentDays(n)` | `certUrgentDays` | Days before expiry to force reconnection |
| `WithGRPCServerURL(url)` | `serverURL` | Backend REST base URL for renewal calls |

Sources: [runner/internal/client/grpc_connection_options.go:53-65]()

---

## End-to-End Certificate Lifecycle

**Diagram: Full certificate lifecycle from registration to renewal**

```mermaid
sequenceDiagram
    participant runner as "runner CLI"
    participant rest as "v1.GRPCRunnerHandler (REST)"
    participant pkisvc as "pki.Service"
    participant disk as "runner cert files"
    participant grpcsrv as "grpcserver.Server (mTLS)"
    participant renewal as "certRenewalChecker"

    note over runner,disk: "Registration"
    runner->>rest: "POST /register (token)"
    rest->>pkisvc: "IssueRunnerCertificate(nodeID, orgSlug)"
    pkisvc-->>rest: "CertificateInfo{CertPEM, KeyPEM, SerialNumber}"
    rest-->>runner: "cert + key + CA cert"
    runner->>disk: "write certFile, keyFile, caFile"

    note over runner,grpcsrv: "Connection"
    runner->>grpcsrv: "Dial + createAdvancedTLSCredentials()"
    grpcsrv->>pkisvc: "ValidateCertificate(clientCert)"
    pkisvc-->>grpcsrv: "nodeID, orgSlug, serial"
    grpcsrv-->>runner: "stream open"

    note over renewal,disk: "Renewal (background)"
    renewal->>disk: "getCertDaysUntilExpiry()"
    disk-->>renewal: "N days"
    renewal->>rest: "RenewCertificate(RenewalRequest)"
    rest->>pkisvc: "IssueRunnerCertificate(nodeID, orgSlug)"
    pkisvc-->>rest: "new CertificateInfo"
    rest-->>renewal: "new cert + key"
    renewal->>disk: "write certFile, keyFile"
    note over disk,grpcsrv: "advancedtls reloads cert on next 1h tick"
```

Sources: [runner/internal/client/grpc_tls.go](), [backend/cmd/server/grpc_init.go](), [backend/internal/infra/pki/service.go]()

---

## Configuration Reference

Backend PKI config fields come from the `cfg.PKI` struct (see [2.7](#2.7) for the full config system). The relevant keys are:

| Config field | Environment variable pattern | Default |
|---|---|---|
| `PKI.CACertFile` | `PKI_CA_CERT_FILE` | Required |
| `PKI.CAKeyFile` | `PKI_CA_KEY_FILE` | Required |
| `PKI.ServerCertFile` | `PKI_SERVER_CERT_FILE` | Optional (auto-generated) |
| `PKI.ServerKeyFile` | `PKI_SERVER_KEY_FILE` | Optional (auto-generated) |
| `PKI.ValidityDays` | `PKI_VALIDITY_DAYS` | `365` |

Runner-side cert file paths are written at registration time by the installer/register command (see [3.1](#3.1)) and are referenced by the `GRPCConnection` using the `certFile`, `keyFile`, and `caFile` fields.

Sources: [backend/internal/infra/pki/service.go:26-33](), [backend/cmd/server/grpc_init.go:34-50]()

---

# Page: Object Storage

# Object Storage

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/internal/infra/storage/s3.go](backend/internal/infra/storage/s3.go)
- [ci/build-onpremise.sh](ci/build-onpremise.sh)
- [ci/pack-onpremise.sh](ci/pack-onpremise.sh)
- [deploy/dev/runner-ssh/README.md](deploy/dev/runner-ssh/README.md)
- [deploy/onpremise/README.md](deploy/onpremise/README.md)
- [deploy/onpremise/docker-compose.yml](deploy/onpremise/docker-compose.yml)
- [deploy/onpremise/scripts/generate-certs.sh](deploy/onpremise/scripts/generate-certs.sh)
- [deploy/onpremise/scripts/install.sh](deploy/onpremise/scripts/install.sh)
- [deploy/onpremise/scripts/load-images.sh](deploy/onpremise/scripts/load-images.sh)
- [deploy/onpremise/seed/onpremise-seed.sql](deploy/onpremise/seed/onpremise-seed.sql)
- [e2e/README.md](e2e/README.md)

</details>



This page documents the S3-compatible object storage layer used by the AgentsMesh backend. It covers the `S3Storage` implementation, configuration fields, upload/download operations, URL generation strategy, and MinIO integration for on-premise and local development deployments.

For deployment-level MinIO setup in the on-premise Docker Compose stack, see [On-Premise Deployment](#8.3). For the backend configuration system that loads the storage environment variables, see [Configuration](#2.7).

---

## Overview

The backend uses a single `S3Storage` type in `backend/internal/infra/storage/s3.go` to interact with any S3-compatible object store. The implementation uses the AWS SDK v2 (`aws-sdk-go-v2`) and is compatible with:

- **AWS S3** — standard use, no endpoint override
- **MinIO** — path-style URLs, used in local dev and on-premise
- **Aliyun OSS** — virtual-hosted-style URLs; checksum calculation is disabled for OSS compatibility

**Sources:** [backend/internal/infra/storage/s3.go:1-14]()

---

## Data Structures

### `S3Config`

Holds all parameters needed to construct an `S3Storage` instance.

| Field | Type | Description |
|---|---|---|
| `Endpoint` | `string` | Internal S3 endpoint host (e.g. `minio:9000`). Empty for AWS. |
| `PublicEndpoint` | `string` | Browser-accessible endpoint host, if different from `Endpoint` (e.g. `192.168.1.100:9000`). |
| `Region` | `string` | AWS region or equivalent (e.g. `us-east-1`). |
| `Bucket` | `string` | Bucket name for all object operations. |
| `AccessKey` | `string` | Access key ID for authentication. |
| `SecretKey` | `string` | Secret access key for authentication. |
| `UseSSL` | `bool` | Whether to use HTTPS for the endpoint URL. |
| `UsePathStyle` | `bool` | Use path-style URLs (`http://host/bucket/key`) instead of virtual-hosted style (`http://bucket.host/key`). Required for MinIO. |

**Sources:** [backend/internal/infra/storage/s3.go:17-26]()

### `S3Storage`

The runtime storage client. Constructed by `NewS3Storage`.

| Field | Description |
|---|---|
| `client` | `*s3.Client` — the AWS SDK S3 client for all object operations. |
| `presign` | `*s3.PresignClient` — dedicated client for generating presigned URLs. |
| `bucket` | The configured bucket name. |
| `endpoint` | Full internal endpoint URL (scheme + host). |
| `publicEndpoint` | Full public endpoint URL (scheme + host). |
| `publicEndpointHost` | Public endpoint host only (no scheme), used for URL construction. |
| `useSSL` | Whether HTTPS is used. |
| `usePathStyle` | Whether path-style URLs are used. |

**Sources:** [backend/internal/infra/storage/s3.go:28-38]()

---

## Construction

**`NewS3Storage(cfg S3Config) (*S3Storage, error)`**

[backend/internal/infra/storage/s3.go:41-108]()

The constructor performs the following steps:

1. **Builds the endpoint URL** by prepending the appropriate scheme (`http` or `https`) to `cfg.Endpoint` if set.
2. **Registers a custom endpoint resolver** via `aws.EndpointResolverWithOptionsFunc`. When `cfg.Endpoint` is non-empty, it routes all S3 SDK calls to the custom endpoint.
3. **Loads AWS SDK config** with static credentials (`credentials.NewStaticCredentialsProvider`) and the custom resolver.
4. **Creates the `s3.Client`** with `UsePathStyle` and `RequestChecksumCalculationWhenRequired`. The checksum option is set to `aws.RequestChecksumCalculationWhenRequired` to disable the `aws-chunked` transfer encoding that Aliyun OSS does not support.
5. **Constructs public endpoint fields** from `cfg.PublicEndpoint` if it differs from the internal endpoint.

**Initialization flow diagram:**

```mermaid
flowchart TD
    A["NewS3Storage(cfg S3Config)"]
    B["Build endpointURL\n(scheme + cfg.Endpoint)"]
    C["aws.EndpointResolverWithOptionsFunc\n(custom resolver)"]
    D["config.LoadDefaultConfig\n(region, static credentials, resolver)"]
    E["s3.NewFromConfig\n(UsePathStyle, RequestChecksumCalculation)"]
    F["s3.NewPresignClient(client)"]
    G["Build publicEndpointURL\n(cfg.PublicEndpoint)"]
    H["Return *S3Storage"]

    A --> B --> C --> D --> E --> F --> G --> H
```

**Sources:** [backend/internal/infra/storage/s3.go:41-108]()

---

## Operations

### Upload

**`(s *S3Storage) Upload(ctx, key, reader, size, contentType) (*FileInfo, error)`**

[backend/internal/infra/storage/s3.go:111-143]()

Reads the entire body into memory via `io.ReadAll` before calling `s3.PutObject`. This bypasses chunked encoding, which is required for Aliyun OSS compatibility. Returns a `FileInfo` struct containing the object key, size, content type, and ETag from the response.

> **Note:** The full body is buffered in memory before upload. This limits practical single-file size. The `STORAGE_MAX_FILE_SIZE` environment variable is enforced at the API layer, not in this function.

### Delete

**`(s *S3Storage) Delete(ctx, key) error`**

[backend/internal/infra/storage/s3.go:146-155]()

Calls `s3.DeleteObject` on the configured bucket with the given key.

### Exists

**`(s *S3Storage) Exists(ctx, key) (bool, error)`**

[backend/internal/infra/storage/s3.go:204-215]()

Uses `s3.HeadObject` to check for object presence. Returns `false` (without error) if the object is absent — the AWS SDK v2 does not expose a typed not-found error, so the error is checked implicitly.

### EnsureBucket

**`(s *S3Storage) EnsureBucket(ctx) error`**

[backend/internal/infra/storage/s3.go:218-236]()

Issues a `HeadBucket` call. If the bucket does not exist, it calls `CreateBucket`. Used during backend initialization to ensure the configured bucket is ready.

---

## URL Generation

URL generation is the most complex part of `S3Storage` because the internal endpoint (used for SDK operations) may differ from the public endpoint (used to serve browsers or runners).

### `GetURL` — Public URL

**`(s *S3Storage) GetURL(ctx, key, expiry) (string, error)`**

[backend/internal/infra/storage/s3.go:160-186]()

**Decision logic:**

```mermaid
flowchart TD
    A["GetURL(key, expiry)"]
    B{"publicEndpoint != endpoint\nAND both non-empty?"}
    C{"usePathStyle?"}
    D["Return path-style public URL\nhttp://publicEndpointHost/bucket/key\n(MinIO style)"]
    E["Return virtual-hosted public URL\nhttp://bucket.publicEndpointHost/key\n(Aliyun OSS style)"]
    F["PresignGetObject\n(internal endpoint)\nReturn presigned URL"]

    A --> B
    B -- "Yes (public bucket)" --> C
    C -- "Yes" --> D
    C -- "No" --> E
    B -- "No (private bucket)" --> F
```

When `publicEndpoint` is set and differs from `endpoint`, the file is assumed to be on a publicly accessible bucket and a plain URL is returned (no signing). When the endpoints are the same (or `publicEndpoint` is empty), a presigned URL is generated using `s3.PresignClient.PresignGetObject`.

**Sources:** [backend/internal/infra/storage/s3.go:157-186]()

### `GetInternalURL` — Service-to-Service URL

**`(s *S3Storage) GetInternalURL(ctx, key, expiry) (string, error)`**

[backend/internal/infra/storage/s3.go:191-201]()

Always generates a presigned URL using the internal endpoint, bypassing `publicEndpoint`. This is intended for service-to-service downloads — for example, a Runner downloading a skill package from within the Docker network where the public endpoint is not routable.

**Comparison of URL methods:**

| Method | Uses Public Endpoint? | Presigned? | Intended Consumer |
|---|---|---|---|
| `GetURL` | Yes (if set and different) | Conditionally | Browser clients |
| `GetInternalURL` | Never | Always | Runner / backend-to-backend |

**Sources:** [backend/internal/infra/storage/s3.go:191-201]()

---

## Configuration via Environment Variables

The backend reads storage configuration from environment variables and maps them to `S3Config`. From the on-premise Docker Compose definition:

[deploy/onpremise/docker-compose.yml:131-141]()

| Environment Variable | Maps to `S3Config` field | Example Value |
|---|---|---|
| `STORAGE_ENDPOINT` | `Endpoint` | `minio:9000` |
| `STORAGE_PUBLIC_ENDPOINT` | `PublicEndpoint` | `192.168.1.100:9000` |
| `STORAGE_REGION` | `Region` | `us-east-1` |
| `STORAGE_BUCKET` | `Bucket` | `agentsmesh` |
| `STORAGE_ACCESS_KEY` | `AccessKey` | `minioadmin` |
| `STORAGE_SECRET_KEY` | `SecretKey` | `<generated>` |
| `STORAGE_USE_SSL` | `UseSSL` | `false` |
| `STORAGE_USE_PATH_STYLE` | `UsePathStyle` | `true` |
| `STORAGE_MAX_FILE_SIZE` | _(API layer only)_ | `10` (MB) |
| `STORAGE_ALLOWED_TYPES` | _(API layer only)_ | `image/jpeg,image/png,...` |

**Sources:** [deploy/onpremise/docker-compose.yml:129-141]()

---

## MinIO Integration

MinIO is the default object store for both the local development environment and on-premise deployments. It exposes an S3-compatible API and requires two specific settings:

- `UsePathStyle = true` — MinIO does not support virtual-hosted-style bucket URLs.
- `PublicEndpoint` set to a browser-accessible address — the internal Docker hostname (e.g. `minio:9000`) is not reachable from browsers or runners outside the Docker network.

**Endpoint split example (on-premise):**

```mermaid
flowchart LR
    subgraph "Docker Network"
        BE["backend container"]
        MN["minio:9000\n(STORAGE_ENDPOINT)"]
        BE -- "SDK operations\n(Upload, Delete, HeadObject)" --> MN
    end
    subgraph "External"
        BR["Browser / Runner"]
    end
    BE -- "GetURL returns plain URL\nhttp://192.168.1.100:9000/agentsmesh/key\n(STORAGE_PUBLIC_ENDPOINT)" --> BR
    BR -- "Direct HTTP fetch" --> MN
```

The MinIO management console is available at port `9001` in the on-premise stack and at `http://{SERVER_IP}:9001` after installation.

**Sources:** [deploy/onpremise/docker-compose.yml:57-73](), [backend/internal/infra/storage/s3.go:160-186]()

---

## Code Entity Map

```mermaid
flowchart TD
    subgraph "backend/internal/infra/storage/s3.go"
        SC["S3Config\n(config struct)"]
        SS["S3Storage\n(client struct)"]
        NS["NewS3Storage()\n(constructor)"]
        UP["Upload()\n(PutObject)"]
        DL["Delete()\n(DeleteObject)"]
        GU["GetURL()\n(public or presigned)"]
        GI["GetInternalURL()\n(always presigned)"]
        EX["Exists()\n(HeadObject)"]
        EB["EnsureBucket()\n(HeadBucket / CreateBucket)"]
    end
    subgraph "AWS SDK v2"
        S3C["s3.Client"]
        PSC["s3.PresignClient"]
        CR["credentials.NewStaticCredentialsProvider"]
        ER["aws.EndpointResolverWithOptionsFunc"]
    end

    SC --> NS
    NS --> SS
    NS --> S3C
    NS --> PSC
    NS --> CR
    NS --> ER
    SS --> UP
    SS --> DL
    SS --> GU
    SS --> GI
    SS --> EX
    SS --> EB
    UP --> S3C
    DL --> S3C
    EX --> S3C
    EB --> S3C
    GU --> PSC
    GI --> PSC
```

**Sources:** [backend/internal/infra/storage/s3.go:1-236]()

---

# Page: Real-time Events and WebSocket

# Real-time Events and WebSocket

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/cmd/server/eventbus_relay.go](backend/cmd/server/eventbus_relay.go)
- [backend/cmd/server/eventbus_setup.go](backend/cmd/server/eventbus_setup.go)
- [backend/cmd/server/main.go](backend/cmd/server/main.go)
- [backend/internal/api/grpc/command_sender_adapter.go](backend/internal/api/grpc/command_sender_adapter.go)
- [backend/internal/api/grpc/runner_adapter_send.go](backend/internal/api/grpc/runner_adapter_send.go)
- [backend/internal/api/grpc/runner_adapter_send_extra_test.go](backend/internal/api/grpc/runner_adapter_send_extra_test.go)
- [backend/internal/api/rest/v1/pod_terminal_connect.go](backend/internal/api/rest/v1/pod_terminal_connect.go)
- [backend/internal/service/runner/command_sender.go](backend/internal/service/runner/command_sender.go)
- [backend/internal/service/runner/command_sender_test.go](backend/internal/service/runner/command_sender_test.go)
- [backend/internal/service/runner/test_helper_test.go](backend/internal/service/runner/test_helper_test.go)
- [proto/gen/go/runner/v1/runner.pb.go](proto/gen/go/runner/v1/runner.pb.go)
- [proto/runner/v1/runner.proto](proto/runner/v1/runner.proto)
- [runner/internal/client/grpc_handler.go](runner/internal/client/grpc_handler.go)
- [runner/internal/client/protocol.go](runner/internal/client/protocol.go)
- [runner/internal/runner/message_handler_relay.go](runner/internal/runner/message_handler_relay.go)
- [web/src/components/ide/sidebar/WorkspaceSidebarContent.tsx](web/src/components/ide/sidebar/WorkspaceSidebarContent.tsx)
- [web/src/components/pwa/PushNotificationManager.tsx](web/src/components/pwa/PushNotificationManager.tsx)
- [web/src/hooks/usePodStatus.ts](web/src/hooks/usePodStatus.ts)
- [web/src/providers/RealtimeProvider.tsx](web/src/providers/RealtimeProvider.tsx)
- [web/src/stores/__tests__/pod.test.ts](web/src/stores/__tests__/pod.test.ts)
- [web/src/stores/__tests__/terminalConnection.test.ts](web/src/stores/__tests__/terminalConnection.test.ts)
- [web/src/stores/__tests__/workspace.test.ts](web/src/stores/__tests__/workspace.test.ts)
- [web/src/stores/channel.ts](web/src/stores/channel.ts)
- [web/src/stores/pod.ts](web/src/stores/pod.ts)
- [web/src/stores/runner.ts](web/src/stores/runner.ts)

</details>



This page covers the backend event bus, the WebSocket hub that delivers events to browser clients, and the frontend infrastructure that receives and dispatches those events to Zustand stores. It does **not** cover terminal streaming via the Relay service (see [4. Relay]()); that is a separate WebSocket channel dedicated to binary PTY data. For the Zustand stores themselves and how they expose state to React components, see [5.5 Real-time State Management]().

---

## Overview

AgentsMesh uses a two-layer real-time system:

1. **Backend `EventBus`** – an internal publish/subscribe bus where services emit typed events (`pod:created`, `runner:online`, `ticket:updated`, etc.).
2. **WebSocket `Hub`** – consumes EventBus events and delivers them over persistent WebSocket connections to authenticated browser sessions, scoped to an organization or individual user.

The frontend `RealtimeProvider` receives those messages, parses them into typed events, and calls the appropriate Zustand store actions to keep UI state current without full page refreshes.

---

## Backend Event Pipeline

### Initialization Sequence

The relevant wiring in `backend/cmd/server/main.go` happens in this order:

1. Infrastructure is initialized, returning a `Hub`, `EventBus`, and optional Redis client.
2. `setupEventBusHub(eventBus, hub)` connects the two — EventBus subscribers route messages into Hub broadcasts.
3. Service-level publishers are created and injected:
   - `ticket.NewEventBusPublisher(eventBus, ...)` → attached via `services.ticket.SetEventPublisher(...)`
   - `agentpod.NewEventBusPublisher(eventBus, ...)` → attached via `services.pod.SetEventPublisher(...)`
   - `services.channel.SetEventBus(eventBus)`
   - `terminalRouter.SetEventBus(eventBus)`
4. If Redis is configured, `eventBus.StartRedisSubscriber(context.Background())` starts cross-instance synchronization.

[backend/cmd/server/main.go:56-88]()

---

### EventBus

The `EventBus` (`backend/internal/infra/eventbus`) is an in-process pub/sub that supports category-based subscriptions. Each event carries:

| Field | Description |
|---|---|
| `Type` | String event type, e.g. `"pod:created"` |
| `OrganizationID` | Determines which org's clients receive the event |
| `TargetUserID` | Optional; set for user-targeted notifications |
| `TargetUserIDs` | Optional slice for multi-user delivery |
| Data payload | Type-specific struct serialized to JSON |

Event categories:

| Category constant | Routing | Example types |
|---|---|---|
| `CategoryEntity` | Broadcast to entire organization | `pod:*`, `runner:*`, `ticket:*`, `channel:*`, `autopilot:*`, `loop_run:*` |
| `CategoryNotification` | Sent to specific user(s) | `terminal:notification`, `task:completed` |
| `CategorySystem` | Broadcast to entire organization | System-level state changes |

---

### WebSocket Hub

The `Hub` (`backend/internal/infra/websocket`) maintains client connections indexed by organization and user. The `setupEventBusHub` function wires all three categories:

[backend/cmd/server/eventbus_setup.go:59-111]()

**Routing logic:**

- `CategoryEntity` → `hub.BroadcastToOrg(event.OrganizationID, data)`
- `CategoryNotification` → `hub.SendToUser(*event.TargetUserID, data)` (also iterates `event.TargetUserIDs`)
- `CategorySystem` → `hub.BroadcastToOrg(event.OrganizationID, data)`

All data is first marshaled to JSON before being handed to the hub.

---

**Event pipeline diagram**

```mermaid
flowchart TD
    subgraph "Services"
        TS["ticket.EventBusPublisher"]
        PS["agentpod.EventBusPublisher"]
        CS["channel.Service (SetEventBus)"]
        TR["terminalRouter (SetEventBus)"]
    end

    subgraph "backend/internal/infra/eventbus"
        EB["EventBus"]
        CAT_E["CategoryEntity subscribers"]
        CAT_N["CategoryNotification subscribers"]
        CAT_S["CategorySystem subscribers"]
    end

    subgraph "backend/internal/infra/websocket"
        HUB["Hub"]
        BROAD["BroadcastToOrg(orgID, data)"]
        USR["SendToUser(userID, data)"]
    end

    subgraph "Redis (optional)"
        RDS["Redis pub/sub\nStartRedisSubscriber"]
    end

    subgraph "Browser"
        WS["WebSocket client\nuseRealtimeConnection"]
    end

    TS -->|"Publish(event)"| EB
    PS -->|"Publish(event)"| EB
    CS -->|"Publish(event)"| EB
    TR -->|"Publish(event)"| EB

    EB --> CAT_E
    EB --> CAT_N
    EB --> CAT_S
    RDS <-->|"cross-instance sync"| EB

    CAT_E --> BROAD
    CAT_S --> BROAD
    CAT_N --> USR

    BROAD --> HUB
    USR --> HUB
    HUB -->|"JSON over WebSocket"| WS
```

Sources: [backend/cmd/server/eventbus_setup.go:59-111](), [backend/cmd/server/main.go:56-88]()

---

### Redis Multi-Instance Sync

When `redisClient != nil`, `eventBus.StartRedisSubscriber(context.Background())` is called. This allows multiple backend instances (e.g., in a horizontally scaled deployment) to relay events to one another via Redis pub/sub. A backend instance that receives a gRPC event from a runner publishes it to both its local EventBus and Redis; other instances consume from Redis and inject the event into their own EventBus, which then delivers it to their connected WebSocket clients.

[backend/cmd/server/main.go:69-72]()

---

### Event Publishers by Service

| Publisher / Setter | Service | Event types emitted |
|---|---|---|
| `ticket.NewEventBusPublisher` | Ticket service | `ticket:created`, `ticket:updated`, `ticket:status_changed`, `ticket:moved`, `ticket:deleted` |
| `agentpod.NewEventBusPublisher` | Pod service | `pod:created`, `pod:status_changed`, `pod:terminated`, `pod:title_changed`, `pod:init_progress`, `pod:agent_status_changed` |
| `channel.Service.SetEventBus` | Channel service | `channel:message` |
| `terminalRouter.SetEventBus` | Terminal router | `terminal:notification`, `task:completed`, `runner:online`, `runner:offline`, `runner:updated`, `autopilot:*`, `loop_run:*`, MR/pipeline events |

Sources: [backend/cmd/server/main.go:63-68](), [backend/cmd/server/eventbus_setup.go:59-111]()

---

## Frontend Real-time Infrastructure

### Connection Layer

The frontend uses two hooks from `web/src/hooks/useRealtimeEvents`:

- `useRealtimeConnection()` – establishes and maintains the WebSocket connection, returns `{ connectionState, reconnect }`.
- `useAllEventsSubscription(handler, deps)` – registers a callback for all incoming events.

`ConnectionState` is one of `"connecting"`, `"connected"`, `"disconnected"`, `"reconnecting"`.

---

### RealtimeProvider

`RealtimeProvider` (`web/src/providers/RealtimeProvider.tsx`) is the single component responsible for:

1. Holding the WebSocket connection state.
2. Receiving all events and routing them to the correct Zustand store action.
3. Triggering full store refreshes on reconnection.

It is placed at the dashboard layout level, after authentication is established, and exposes `connectionState` and `reconnect` via `RealtimeContext`.

Key design decision: all Zustand stores are accessed via `getState()` (not reactive hooks) inside `handleEvent`. This prevents `RealtimeProvider` itself from re-rendering on every store change, which would cause cascading UI re-renders (e.g., native `<select>` elements closing unexpectedly).

[web/src/providers/RealtimeProvider.tsx:59-63]()

---

### Event Routing in handleEvent

The `handleEvent` callback in `RealtimeProvider` dispatches by `event.type`:

**Pod events diagram**

```mermaid
flowchart LR
    subgraph "RealtimeProvider handleEvent"
        E1["pod:created"]
        E2["pod:status_changed"]
        E3["pod:agent_status_changed"]
        E4["pod:terminated"]
        E5["pod:title_changed"]
        E6["pod:init_progress"]
    end

    subgraph "usePodStore"
        A1["fetchPod(pod_key)"]
        A2["updatePodStatus(podKey, status, ...)"]
        A3["updateAgentStatus(podKey, agentStatus)"]
        A4["updatePodStatus(podKey, 'terminated')"]
        A5["updatePodTitle(podKey, title)"]
        A6["updatePodInitProgress(podKey, phase, progress, message)"]
    end

    subgraph "useMeshStore"
        M1["fetchTopology()"]
    end

    E1 --> A1
    E1 --> M1
    E2 --> A2
    E2 --> M1
    E3 --> A3
    E4 --> A4
    E4 --> M1
    E5 --> A5
    E6 --> A6
```

[web/src/providers/RealtimeProvider.tsx:70-138]()

---

**Full event-to-store routing table**

| Event type(s) | Store action called |
|---|---|
| `pod:created` | `usePodStore.fetchPod(pod_key)`, `useMeshStore.fetchTopology()` |
| `pod:status_changed` | `usePodStore.updatePodStatus(...)` or `fetchPod` if not in store; `fetchTopology()` |
| `pod:agent_status_changed` | `usePodStore.updateAgentStatus(pod_key, agent_status)` |
| `pod:terminated` | `usePodStore.updatePodStatus(pod_key, "terminated")`; `fetchTopology()` |
| `pod:title_changed` | `usePodStore.updatePodTitle(pod_key, title)` |
| `pod:init_progress` | `usePodStore.updatePodInitProgress(pod_key, phase, progress, message)` |
| `runner:online`, `runner:offline`, `runner:updated` | `useRunnerStore.updateRunnerStatus(runner_id, status)` |
| `ticket:created`, `ticket:updated`, `ticket:status_changed`, `ticket:moved`, `ticket:deleted` | `useTicketStore.fetchTickets()` |
| `channel:message` | `useChannelStore.addMessage(message)` (only if `currentChannel.id` matches) |
| `terminal:notification` | `onTerminalNotification(data)` callback prop |
| `task:completed` | `onTaskCompleted(data)` callback prop |
| `autopilot:status_changed` | `useAutopilotStore.updateAutopilotControllerStatus(...)` |
| `autopilot:iteration` | `useAutopilotStore.addIteration(key, {...})` |
| `autopilot:created` | `useAutopilotStore.fetchAutopilotControllers()` |
| `autopilot:terminated` | `useAutopilotStore.removeAutopilotController(key)` |
| `autopilot:thinking` | `useAutopilotStore.updateThinking(key, data)` |
| `mr:created`, `mr:updated`, `mr:merged`, `mr:closed` | `useTicketStore.fetchTickets()` and/or `usePodStore.fetchPods()` |
| `pipeline:updated` | `useTicketStore.fetchTickets()` and/or `usePodStore.fetchPods()` |
| `loop_run:started`, `loop_run:completed`, `loop_run:failed` | Debounced (500 ms): `useLoopStore.fetchLoops()` + `fetchLoop()` + `fetchRuns()` |
| `loop_run:warning` | `toast.warning(...)` via sonner |

[web/src/providers/RealtimeProvider.tsx:66-330]()

---

### Reconnection Behavior

When `connectionState` transitions to `"connected"`, `RealtimeProvider` triggers a full refresh of all affected stores:

```
usePodStore.fetchSidebarPods(currentSidebarFilter)
useRunnerStore.fetchRunners()
useTicketStore.fetchTickets()
useMeshStore.fetchTopology()
useAutopilotStore.fetchAutopilotControllers()
useLoopStore.fetchLoops()
```

This ensures any events missed during a disconnection are recovered via REST.

[web/src/providers/RealtimeProvider.tsx:344-356]()

---

### Loop Event Debouncing

`loop_run:started/completed/failed` events are debounced with a 500 ms coalescing window via a `loopDebounceRef` (`useRef`). This prevents multiple rapid loop completions from triggering redundant API calls. The timer is cleared on component unmount.

[web/src/providers/RealtimeProvider.tsx:55-57](), [web/src/providers/RealtimeProvider.tsx:290-310]()

---

### Staleness Protection in usePodStore

`usePodStore` implements timestamp-based staleness guards to prevent stale REST API responses from overwriting newer WebSocket-applied state:

- `podTimestamps: Record<string, number>` tracks the last-known update time per pod key.
- `shouldUpdate(podTimestamps, podKey, timestamp)` — returns `false` if the incoming timestamp is older than the recorded one.
- `upsertPod(state, podKey, merger, timestamp)` — the single write path; all mutations go through this to enforce the guard and deduplicate.
- In-flight deduplication: `fetchPodInflight: Map<string, Promise<void>>` prevents multiple concurrent `fetchPod` calls for the same key (e.g., rapid WebSocket events).

[web/src/stores/pod.ts:73-142]()

---

### Code Entity Map

```mermaid
flowchart TD
    subgraph "backend/cmd/server"
        SETUP["setupEventBusHub()"]
        MAIN["main.go initializeInfrastructure()"]
    end

    subgraph "backend/internal/infra/eventbus"
        EB2["EventBus\n.SubscribeCategory()\n.Publish()\n.StartRedisSubscriber()"]
        EVT["Event struct\n{Type, OrganizationID,\nTargetUserID, Data}"]
        CAT["CategoryEntity\nCategoryNotification\nCategorySystem"]
    end

    subgraph "backend/internal/infra/websocket"
        HUB2["Hub\n.BroadcastToOrg()\n.SendToUser()\n.GetUserClientCount()"]
    end

    subgraph "backend/internal/service/..."
        PUB1["ticket.EventBusPublisher\nNewEventBusPublisher()"]
        PUB2["agentpod.EventBusPublisher\nNewEventBusPublisher()"]
        PUB3["channel.Service\n.SetEventBus()"]
        PUB4["terminalRouter\n.SetEventBus()"]
    end

    subgraph "web/src/providers"
        RP["RealtimeProvider\nhandleEvent()\nuseRealtimeConnection()\nuseAllEventsSubscription()"]
    end

    subgraph "web/src/stores"
        PST["usePodStore\nupsertPod()\nupdatePodStatus()\nfetchPod()"]
        RST["useRunnerStore\nupdateRunnerStatus()"]
        TST["useTicketStore\nfetchTickets()"]
        CST["useChannelStore\naddMessage()"]
        AST["useAutopilotStore"]
        LST["useLoopStore"]
    end

    MAIN --> EB2
    MAIN --> HUB2
    MAIN --> SETUP
    SETUP --> EB2
    SETUP --> HUB2
    PUB1 --> EB2
    PUB2 --> EB2
    PUB3 --> EB2
    PUB4 --> EB2
    HUB2 -->|"JSON WebSocket"| RP
    RP --> PST
    RP --> RST
    RP --> TST
    RP --> CST
    RP --> AST
    RP --> LST
```

Sources: [backend/cmd/server/eventbus_setup.go:59-111](), [backend/cmd/server/main.go:56-88](), [web/src/providers/RealtimeProvider.tsx:47-368](), [web/src/stores/pod.ts:73-142]()

---

# Page: Runner

# Runner

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [runner/.goreleaser.yml](runner/.goreleaser.yml)
- [runner/README.md](runner/README.md)
- [runner/cmd/runner/cmd_reactivate.go](runner/cmd/runner/cmd_reactivate.go)
- [runner/cmd/runner/cmd_register.go](runner/cmd/runner/cmd_register.go)
- [runner/cmd/runner/cmd_run.go](runner/cmd/runner/cmd_run.go)
- [runner/cmd/runner/main.go](runner/cmd/runner/main.go)
- [runner/cmd/runner/register.go](runner/cmd/runner/register.go)
- [runner/cmd/runner/service.go](runner/cmd/runner/service.go)
- [runner/cmd/runner/update.go](runner/cmd/runner/update.go)
- [runner/cmd/runner/webconsole.go](runner/cmd/runner/webconsole.go)
- [runner/internal/client/grpc_connection.go](runner/internal/client/grpc_connection.go)
- [runner/internal/config/config.go](runner/internal/config/config.go)
- [runner/internal/config/config_defaults_test.go](runner/internal/config/config_defaults_test.go)
- [runner/internal/runner/runner.go](runner/internal/runner/runner.go)
- [web/public/install.ps1](web/public/install.ps1)
- [web/public/install.sh](web/public/install.sh)
- [web/src/app/docs/runners/setup/page.tsx](web/src/app/docs/runners/setup/page.tsx)

</details>



This page covers the Runner daemon: its role, internal structure, configuration, distribution, and startup lifecycle. The Runner is the component users install on their own machines to execute AI agent tasks.

For gRPC communication protocol details, see the [gRPC Client](#3.3) page. For Pod and terminal management, see [Pod and Terminal Management](#3.4). For installation steps and the registration flow, see [Installation and Registration](#3.1). For the full CLI reference, see [CLI Reference](#3.2).

---

## Purpose

The Runner (`agentsmesh-runner`) is a long-running daemon process that:

- Registers with the AgentsMesh backend using mTLS certificates
- Maintains a persistent bidirectional gRPC stream to the backend
- Receives commands to create and manage **Pods** (isolated terminal sessions)
- Streams terminal I/O back to the browser via the Relay WebSocket service
- Exposes a local MCP HTTP server for AI agent tool integration
- Manages Git workspaces for ticket-based development workflows

The Runner embodies the BYOK (Bring Your Own Keys) and self-hosted execution model: AI agent tasks execute on infrastructure the user controls, not on AgentsMesh servers.

Sources: [runner/README.md:1-10](), [runner/internal/runner/runner.go:1-55]()

---

## System Context

**Runner in the AgentsMesh Architecture**

```mermaid
graph TD
    Browser["Browser (Web Frontend)"]
    Backend["Backend (Go server)"]
    Relay["Relay (WebSocket)"]
    Runner["Runner (agentsmesh-runner)"]
    Agent["AI Agent Process (e.g. claude-code)"]
    Git["Git Repository"]

    Browser -- "REST / WebSocket" --> Backend
    Browser -- "WebSocket (terminal stream)" --> Relay
    Backend -- "gRPC/mTLS (bidirectional stream)" --> Runner
    Runner -- "WebSocket (publisher)" --> Relay
    Runner -- "spawns PTY" --> Agent
    Runner -- "git clone / worktree" --> Git
```

Sources: [runner/internal/runner/runner.go:57-149](), [runner/internal/client/grpc_connection.go:1-50]()

---

## Repository Layout

The Runner lives entirely under `runner/` within the monorepo.

| Path | Description |
|------|-------------|
| `runner/cmd/runner/` | CLI entry point and command handlers |
| `runner/internal/runner/` | Core `Runner` struct and lifecycle |
| `runner/internal/client/` | gRPC connection (`GRPCConnection`) |
| `runner/internal/config/` | `Config` struct and loading logic |
| `runner/internal/mcp/` | MCP HTTP server and manager |
| `runner/internal/workspace/` | Git workspace and worktree management |
| `runner/internal/lifecycle/` | Supervisor-compatible service wrappers |
| `runner/internal/autopilot/` | `AutopilotController` for automated pod runs |
| `runner/internal/updater/` | Self-update logic |
| `runner/internal/monitor/` | Agent process monitor |
| `runner/.goreleaser.yml` | Release build configuration |

Sources: [runner/cmd/runner/main.go:1-78](), [runner/internal/runner/runner.go:1-20]()

---

## CLI Commands

The binary entry point is `runner/cmd/runner/main.go`. Command dispatch is a simple `switch` over `os.Args[1]`.

[runner/cmd/runner/main.go:14-44]()

| Invocation | Handler Function | Source File |
|---|---|---|
| `login` / `register` | `runRegister()` | `cmd_register.go` |
| `run` / `start` | `runRunner()` | `cmd_run.go` |
| `service` | `runService()` | `service.go` |
| `webconsole` / `console` | `runWebConsole()` | `webconsole.go` |
| `reactivate` | `runReactivate()` | `cmd_reactivate.go` |
| `update-endpoint` | `runUpdateEndpoint()` | _(in repo)_ |
| `update` | `runUpdate()` | `update.go` |
| `version` | inline `fmt.Printf` | `main.go` |

Sources: [runner/cmd/runner/main.go:20-44]()

---

## Configuration

Configuration is stored at `~/.agentsmesh/config.yaml` (created during registration) and loaded by `config.Load()` using [Viper](https://github.com/spf13/viper). Environment variables with the `AGENTSMESH_` prefix override file values.

[runner/internal/config/config.go:12-79]()

**`Config` struct — key fields**

| Field | `mapstructure` key | Default | Description |
|---|---|---|---|
| `ServerURL` | `server_url` | `https://agentsmesh.ai` | Backend HTTP URL for REST calls |
| `NodeID` | `node_id` | hostname | Runner's unique identifier |
| `OrgSlug` | `org_slug` | _(set at registration)_ | Organization scope |
| `GRPCEndpoint` | `grpc_endpoint` | _(set at registration)_ | gRPC server address (`host:port`) |
| `CertFile` | `cert_file` | _(set at registration)_ | Path to mTLS client certificate |
| `KeyFile` | `key_file` | _(set at registration)_ | Path to private key |
| `CAFile` | `ca_file` | _(set at registration)_ | Path to CA certificate |
| `MaxConcurrentPods` | `max_concurrent_pods` | `5` | Pod capacity limit |
| `WorkspaceRoot` | `workspace_root` | `/workspace` | Root directory for git worktrees |
| `MCPPort` | `mcp_port` | `19000` | Local MCP HTTP server port |
| `LogLevel` | `log_level` | `info` | Logging verbosity |
| `AutoUpdate` | `auto_update` | enabled, 24h, stable | Self-update settings |

Sources: [runner/internal/config/config.go:12-100](), [runner/cmd/runner/register.go:219-234]()

---

## Core `Runner` Struct

`runner.Runner` (in `runner/internal/runner/runner.go`) is the central coordinator. It is created by `runner.New()` and started by `runner.Run()`.

**`Runner` struct and its dependencies**

```mermaid
classDiagram
    class Runner {
        +cfg Config
        +conn Connection
        +workspace Manager
        +podStore PodStore
        +messageHandler RunnerMessageHandler
        +mcpManager mcp.Manager
        +mcpServer mcp.HTTPServer
        +agentMonitor monitor.Monitor
        +autopilots map AutopilotController
        +New(cfg) Runner
        +Run(ctx) error
        +CanAcceptPod() bool
        +GetActivePodCount() int
        +IsDraining() bool
    }
    class GRPCConnection {
        +endpoint string
        +certFile string
        +keyFile string
        +caFile string
        +controlCh chan RunnerMessage
        +terminalCh chan RunnerMessage
        +Connect() error
        +Start()
        +Stop()
    }
    class RunnerMessageHandler {
        +OnCreatePod()
        +OnTerminatePod()
        +OnTerminalInput()
    }
    class InMemoryPodStore {
        +All() Pod
        +Count() int
        +Delete(key)
    }
    class mcp_HTTPServer["mcp.HTTPServer"] {
        +port int
        +Serve(ctx)
    }
    class workspace_Manager["workspace.Manager"] {
        +workspaceRoot string
        +CloneRepo()
        +CreateWorktree()
    }

    Runner --> GRPCConnection : conn
    Runner --> RunnerMessageHandler : messageHandler
    Runner --> InMemoryPodStore : podStore
    Runner --> mcp_HTTPServer : mcpServer
    Runner --> workspace_Manager : workspace
    GRPCConnection --> RunnerMessageHandler : handler
```

Sources: [runner/internal/runner/runner.go:23-54](), [runner/internal/client/grpc_connection.go:29-106]()

---

## Startup Sequence

`runner.New()` validates configuration and constructs all components. `runner.Run()` builds the suture Supervisor tree and blocks until the context is cancelled.

**`runner.Run()` — Supervisor tree**

```mermaid
graph TD
    Run["runner.Run(ctx)"]
    Supervisor["suture.Supervisor (name: runner)"]
    CS["lifecycle.ConnectionService\n(wraps GRPCConnection)"]
    MS["lifecycle.MCPServerService\n(wraps mcp.HTTPServer)"]
    MoS["lifecycle.MonitorService\n(wraps monitor.Monitor)"]
    WD["lifecycle.WatchdogService\n(interval: 15s)"]
    Con["lifecycle.ConsoleService\n(web console, port 19080)"]

    Run --> Supervisor
    Supervisor --> CS
    Supervisor --> MS
    Supervisor --> MoS
    Supervisor --> WD
    Supervisor --> Con
```

[runner/internal/runner/runner.go:197-249]()

On shutdown (`ctx` cancelled), `Run()` calls `stopAllPods()`, which stops all `AutopilotController` instances and then all active Pods.

**`runner.New()` initialization steps**

```mermaid
sequenceDiagram
    participant CLI as "cmd_run.go: runRunner()"
    participant New as "runner.New(cfg)"
    participant GC as "GRPCConnection"
    participant WS as "workspace.NewManager()"
    participant MCP as "mcp.NewHTTPServer()"

    CLI->>New: runner.New(cfg)
    New->>New: "cfg.LoadGRPCConfig() — load cert paths"
    New->>WS: "workspace.NewManager(root, gitConfigPath)"
    New->>GC: "client.NewGRPCConnection(endpoint, nodeID, ...)"
    New->>GC: "grpcConn.GetCertificateExpiryInfo()"
    New->>New: "clipboard.Detect()"
    New->>New: "NewInMemoryPodStore()"
    New->>New: "NewRunnerMessageHandler(r, podStore, grpcConn)"
    New->>MCP: "mcp.NewHTTPServer(rpcClient, mcpPort)"
    New->>New: "monitor.NewMonitor(5s)"
    New-->>CLI: "*Runner"
```

Sources: [runner/internal/runner/runner.go:57-149](), [runner/cmd/runner/cmd_run.go:136-201]()

---

## Registration Flow

Registration runs once (or when re-registering). It contacts the backend REST API, receives mTLS certificates, and writes them to `~/.agentsmesh/certs/`. Configuration is written to `~/.agentsmesh/config.yaml`.

Two modes are supported:

| Mode | Function | Notes |
|---|---|---|
| Token-based | `registerWithGRPCToken()` | Suitable for CI/CD and headless servers |
| Interactive | `registerInteractive()` | Opens browser for OAuth-style login |

[runner/cmd/runner/register.go:29-81]()

After registration, `saveGRPCConfig()` writes the `savedGRPCConfig` YAML struct to disk, including `cert_file`, `key_file`, `ca_file`, and `grpc_endpoint`.

[runner/cmd/runner/register.go:151-207]()

If a previous registration exists for a different organization, `backupExistingConfig()` renames the old config and certs directory before overwriting.

Sources: [runner/cmd/runner/register.go:1-235](), [runner/cmd/runner/cmd_register.go:14-95]()

---

## gRPC Connection

`GRPCConnection` (in `runner/internal/client/grpc_connection.go`) manages the mTLS connection to the backend gRPC server. It uses `advancedtls` credentials for certificate hot-reloading without reconnection.

Key fields:

| Field | Type | Purpose |
|---|---|---|
| `controlCh` | `chan *RunnerMessage` (buf 100) | High-priority: heartbeats, pod events |
| `terminalCh` | `chan *RunnerMessage` (buf 1000) | Low-priority: terminal output |
| `terminalRateLimiter` | `rate.Limiter` | Default 50 KB/s cap on terminal output |
| `reconnectStrategy` | `*ReconnectStrategy` | Exponential backoff (5s–5min) |
| `initTimeout` | `time.Duration` | 30s timeout for initialization handshake |
| `certRenewalDays` | `int` | Renew cert 30 days before expiry |

Fatal, non-retryable errors (e.g., `codes.Unauthenticated` with "runner not found", `codes.PermissionDenied` with "runner is disabled") are detected by `isFatalStreamError()` and stop reconnection attempts.

[runner/internal/client/grpc_connection.go:29-106](), [runner/internal/client/grpc_connection.go:297-321]()

For full gRPC client behavior including reconnection loops, heartbeat, and message routing, see [gRPC Client](#3.3).

---

## Web Console

When running via `agentsmesh-runner run`, a local HTTP status console starts automatically on port `19080` (constant `DefaultConsolePort`).

The `webconsole` CLI command (`webconsole.go`) checks whether the console is reachable at `http://127.0.0.1:19080/api/status` and then opens the URL in the system browser using `open` (macOS), `xdg-open` (Linux), or `rundll32` (Windows).

[runner/cmd/runner/webconsole.go:15-62]()

---

## System Service

The `service` subcommand wraps the runner as a platform-native daemon using `github.com/kardianos/service`.

```
agentsmesh-runner service install   # registers with OS init system
agentsmesh-runner service start
agentsmesh-runner service stop
agentsmesh-runner service restart
agentsmesh-runner service status
agentsmesh-runner service uninstall
```

The `install` sub-action reads a config file path (`--config`, defaults to `~/.agentsmesh/config.yaml`) and delegates to `svc.Install()` in `runner/internal/service/`.

[runner/cmd/runner/service.go:14-149]()

---

## Certificate Lifecycle

| Event | Behavior |
|---|---|
| Registration | Backend issues cert, stored at `~/.agentsmesh/certs/` |
| Startup | `GetCertificateExpiryInfo()` checks cert validity; exits if expired |
| Near expiry (≤30 days) | Warning logged; background renewal triggered |
| Near expiry (≤7 days) | `certUrgentDays`: forces reconnection after renewal |
| Expired | `runner.New()` returns error; user must run `agentsmesh-runner reactivate` |
| Reactivation | `reactivateRunner()` exchanges a token for new certs via REST API |

[runner/internal/runner/runner.go:107-122](), [runner/internal/client/grpc_connection.go:87-92](), [runner/cmd/runner/cmd_reactivate.go:14-71]()

For the backend PKI side, see [PKI and mTLS](#2.8).

---

## Self-Update

The `update` command uses `runner/internal/updater/`. On invocation it:

1. Calls `u.CheckForUpdate(ctx)` — queries GitHub Releases API
2. Calls `u.CreateBackup()` — copies current binary
3. Calls `u.Download(ctx, version, progress)` — downloads new binary
4. Calls `u.Apply(tmpPath)` — atomically replaces binary
5. On failure, calls `u.Rollback()` — restores backup

[runner/cmd/runner/update.go:137-173]()

For the backend-side version polling, see [Auto-Update](#3.8).

---

## Distribution

Releases are produced by GoReleaser ([runner/.goreleaser.yml]()). The release targets are:

| OS | Architectures | Formats |
|---|---|---|
| Linux | amd64, arm64 | tar.gz, `.deb`, `.rpm`, `.apk` |
| macOS | amd64, arm64, universal | tar.gz |
| Windows | amd64, arm64 | `.zip` |

The Homebrew formula in `AgentsMesh/BrewCask` is updated automatically on each release.

**Install methods**

```
# macOS / Linux
curl -fsSL https://agentsmesh.ai/install.sh | sh

# Windows PowerShell
irm https://agentsmesh.ai/install.ps1 | iex

# Homebrew
brew tap agentsmesh/tap https://github.com/AgentsMesh/BrewCask
brew install agentsmesh/tap/agentsmesh-runner
```

`install.sh` detects the platform, fetches the latest GitHub release tag, downloads the matching archive, extracts it to `~/.local/bin`, and prints PATH configuration hints if needed.

[web/public/install.sh:123-210](), [runner/.goreleaser.yml:15-68]()

For the CI/CD pipeline that produces these artifacts, see [Release Process](#8.2).

---

# Page: Installation and Registration

# Installation and Registration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [runner/.goreleaser.yml](runner/.goreleaser.yml)
- [runner/README.md](runner/README.md)
- [runner/cmd/runner/cmd_reactivate.go](runner/cmd/runner/cmd_reactivate.go)
- [runner/cmd/runner/cmd_register.go](runner/cmd/runner/cmd_register.go)
- [runner/cmd/runner/cmd_run.go](runner/cmd/runner/cmd_run.go)
- [runner/cmd/runner/main.go](runner/cmd/runner/main.go)
- [runner/cmd/runner/register.go](runner/cmd/runner/register.go)
- [runner/cmd/runner/service.go](runner/cmd/runner/service.go)
- [runner/cmd/runner/update.go](runner/cmd/runner/update.go)
- [runner/cmd/runner/webconsole.go](runner/cmd/runner/webconsole.go)
- [runner/internal/client/grpc_connection.go](runner/internal/client/grpc_connection.go)
- [runner/internal/config/config.go](runner/internal/config/config.go)
- [runner/internal/config/config_defaults_test.go](runner/internal/config/config_defaults_test.go)
- [runner/internal/runner/runner.go](runner/internal/runner/runner.go)
- [web/public/install.ps1](web/public/install.ps1)
- [web/public/install.sh](web/public/install.sh)
- [web/src/app/docs/runners/setup/page.tsx](web/src/app/docs/runners/setup/page.tsx)

</details>



This page covers how to install the `agentsmesh-runner` binary and register it with an AgentsMesh server. It documents the installation scripts, the `register` command, both token-based and interactive registration flows, the configuration and certificate files written to disk, and the `reactivate` command for certificate renewal.

For details on what the runner does once it is running, see the Runner overview (page [3]()). For the full CLI command reference, see [3.2](). For the gRPC connection lifecycle that begins after registration, see [3.3]().

---

## Installation

The runner binary is released as `agentsmesh-runner` via GitHub Releases under `AgentsMesh/AgentsMesh`. GoReleaser produces archives for Linux, macOS (universal), and Windows, plus `.deb`, `.rpm`, and `.apk` packages for Linux. See [runner/.goreleaser.yml]() for the full build matrix.

### Installation methods

| Method | Command |
|---|---|
| macOS / Linux (one-line) | `curl -fsSL https://agentsmesh.ai/install.sh \| sh` |
| Windows (PowerShell) | `irm https://agentsmesh.ai/install.ps1 \| iex` |
| macOS (Homebrew) | `brew tap agentsmesh/tap https://github.com/AgentsMesh/BrewCask` then `brew install agentsmesh/tap/agentsmesh-runner` |
| Linux packages | `.deb`, `.rpm`, `.apk` from GitHub Releases |
| Direct download | Tarball / zip from GitHub Releases |

### install.sh (macOS and Linux)

The script at [web/public/install.sh]() performs the following steps:

1. **Platform detection** — calls `uname -s` and `uname -m`; maps to `darwin_all`, `linux_amd64`, or `linux_arm64`.
2. **Homebrew suggestion** — on macOS with Homebrew present, offers the tap alternative before continuing.
3. **Install directory selection** — uses `$INSTALL_DIR` env var if set; otherwise defaults to `~/.local/bin`.
4. **Version fetch** — queries `https://api.github.com/repos/AgentsMesh/AgentsMesh/releases/latest` for the tag name.
5. **Download and extract** — fetches the `.tar.gz` archive to a temp directory and extracts it.
6. **Binary install** — moves `agentsmesh-runner` to `$INSTALL_DIR` and sets `chmod +x`.
7. **PATH hint** — if `$INSTALL_DIR` is not in `$PATH`, prints shell-specific instructions for `zsh`, `bash`, or `fish`.

The function sequence is:

**Diagram: install.sh execution flow**

```mermaid
flowchart TD
    A["main()"] --> B["detect_platform()"]
    B --> C["check_homebrew()"]
    C --> D["detect_install_dir()"]
    D --> E["get_latest_version()"]
    E --> F["install()"]
    F --> G["verify()"]
    G --> H["ensure_path()"]
    H --> I["print_next_steps()"]
```

Sources: [web/public/install.sh:270-292]()

### install.ps1 (Windows)

The script at [web/public/install.ps1]() mirrors the shell script logic. Key functions:

| Function | Purpose |
|---|---|
| `Get-Platform` | Returns `windows_amd64` or `windows_arm64` |
| `Get-LatestVersion` | Calls GitHub API with `Invoke-RestMethod` |
| `Get-InstallDir` | Prefers `%USERPROFILE%\.local\bin`; falls back to `%LOCALAPPDATA%\Programs\agentsmesh` |
| `Install-Runner` | Downloads `.zip`, extracts, moves `agentsmesh-runner.exe` |
| `Add-ToPath` | Adds the install directory to the user-scope `PATH` environment variable |
| `Test-Scoop` | Detects Scoop and offers it as an alternative |

Sources: [web/public/install.ps1:1-227]()

### Homebrew

GoReleaser is configured to push formula updates to the `AgentsMesh/BrewCask` repository after each release. The formula installs the macOS universal binary (`darwin_all`). See [runner/.goreleaser.yml:221-252]() for the `brews` block.

---

## Registration

Registration must be completed before running `agentsmesh-runner run`. It exchanges credentials with the server and writes a config file plus mTLS certificates to `~/.agentsmesh/`.

There are two registration modes:

| Mode | Trigger | Use case |
|---|---|---|
| Token-based | `--token <token>` flag | Automated / CI / headless deployment |
| Interactive (login) | No `--token` flag | Developer workstations (opens browser) |

**Diagram: Registration command routing and key functions**

```mermaid
flowchart TD
    CLI["main() in cmd/runner/main.go"] -->|"login / register"| R["runRegister() cmd_register.go"]
    R --> CHK["checkExistingRegistration()"]
    CHK -->|"org_slug found"| WARN["Prompt or --force"]
    CHK -->|"no existing config"| DECIDE
    WARN --> DECIDE
    DECIDE -->|"--token present"| TOK["registerWithGRPCToken()"]
    DECIDE -->|"no token"| INT["registerInteractive()"]
    TOK --> RTOKEN["client.RegisterWithToken()"]
    INT --> RINT["client.InteractiveRegister()"]
    RTOKEN --> SAVE["saveGRPCConfig()"]
    RINT --> SAVE
    SAVE --> CERTS["cfg.SaveCertificates()"]
    SAVE --> YAML["write ~/.agentsmesh/config.yaml"]
```

Sources: [runner/cmd/runner/cmd_register.go](), [runner/cmd/runner/register.go]()

### Token-based registration

```
agentsmesh-runner register --server https://agentsmesh.ai --token <YOUR_TOKEN>
```

The `runRegister` function in [runner/cmd/runner/cmd_register.go:14-95]() parses flags and, when `--token` is set, calls `registerWithGRPCToken` in [runner/cmd/runner/register.go:59-81](). This calls `client.RegisterWithToken` with a `TokenRegistrationRequest` containing the `ServerURL`, `Token`, and `NodeID`.

### Interactive (login) registration

```
agentsmesh-runner register
agentsmesh-runner register --headless        # SSH / remote: print URL, don't open browser
agentsmesh-runner register --server https://self-hosted.example.com
```

When no `--token` is given, `registerInteractive` in [runner/cmd/runner/register.go:31-56]() is called. It generates a random 32-byte hex `machineKey` (via `generateMachineKey`) and calls `client.InteractiveRegister` with an `InteractiveRegistrationRequest`. This flow is Tailscale-style: the server returns a URL for the user to authorize in a browser.

### Overwriting an existing registration

`checkExistingRegistration` in [runner/cmd/runner/cmd_register.go:99-120]() reads `~/.agentsmesh/config.yaml` and returns the existing `org_slug`. If a registration already exists and neither `--force` nor `--token` is set, the user is prompted for confirmation (`[y/N]`). When overwriting, `backupExistingConfig` in [runner/cmd/runner/register.go:112-149]() backs up the current config and certs directory:

- Config backed up to `~/.agentsmesh/config.<org-slug>.yaml.bak`
- Certs backed up to `~/.agentsmesh/certs.<org-slug>.bak/`

---

## Files Written by Registration

After a successful registration, `saveGRPCConfig` in [runner/cmd/runner/register.go:152-207]() writes the following:

### `~/.agentsmesh/config.yaml`

The `savedGRPCConfig` struct ([runner/cmd/runner/register.go:220-234]()) defines all fields written:

| Field | Type | Example / Default |
|---|---|---|
| `server_url` | string | `https://agentsmesh.ai` |
| `node_id` | string | hostname |
| `org_slug` | string | Set by server |
| `grpc_endpoint` | string | `grpc.agentsmesh.ai:9443` |
| `cert_file` | string | `~/.agentsmesh/certs/client.crt` |
| `key_file` | string | `~/.agentsmesh/certs/client.key` |
| `ca_file` | string | `~/.agentsmesh/certs/ca.crt` |
| `max_concurrent_pods` | int | `5` |
| `workspace_root` | string | `/tmp/agentsmesh-workspace` |
| `default_agent` | string | `claude-code` |
| `default_shell` | string | `$SHELL` or `/bin/sh` |
| `health_check_port` | int | `9090` |
| `log_level` | string | `info` |

### `~/.agentsmesh/certs/`

Three PEM files are saved by `cfg.SaveCertificates`:

| File | Content |
|---|---|
| `client.crt` | Client certificate issued by the server CA |
| `client.key` | Client private key |
| `ca.crt` | Server CA certificate (used to verify the gRPC server) |

These three paths are referenced at runtime by `GRPCConnection` in [runner/internal/client/grpc_connection.go:37-39]() to establish mTLS.

**Diagram: Files written to disk and their runtime consumers**

```mermaid
flowchart LR
    REG["saveGRPCConfig()\nregister.go"] -->|"yaml.Marshal"| CFG["~/.agentsmesh/config.yaml\n(savedGRPCConfig struct)"]
    REG -->|"cfg.SaveCertificates()"| CERTS["~/.agentsmesh/certs/\nclient.crt  client.key  ca.crt"]

    CFG -->|"config.Load()"| CFGSTRUCT["Config struct\nconfig/config.go"]
    CERTS -->|"certFile keyFile caFile"| GRPC["GRPCConnection\nclient/grpc_connection.go"]
    CFGSTRUCT -->|"CertFile KeyFile CAFile GRPCEndpoint"| GRPC
    GRPC -->|"createAdvancedTLSCredentials()"| MTLS["mTLS dial\ngrpc.Dial()"]
```

Sources: [runner/cmd/runner/register.go:152-207](), [runner/internal/client/grpc_connection.go:29-106](), [runner/internal/config/config.go:12-79]()

---

## Configuration Loading

`config.Load(configFile)` in [runner/internal/config/config.go:103-165]() uses Viper to merge values from three sources, in ascending priority order:

1. Hard-coded defaults (e.g., `max_concurrent_pods=5`, `mcp_port=19000`)
2. The config file at `~/.agentsmesh/config.yaml`
3. Environment variables with prefix `AGENTSMESH_` (e.g., `AGENTSMESH_SERVER_URL`)

The `Config` struct in [runner/internal/config/config.go:12-79]() is the canonical in-memory representation used throughout the runner.

### Environment variable overrides

| Env var | Config field |
|---|---|
| `AGENTSMESH_SERVER_URL` | `server_url` |
| `AGENTSMESH_NODE_ID` | `node_id` |
| `AGENTSMESH_MAX_CONCURRENT_PODS` | `max_concurrent_pods` |
| `AGENTSMESH_WORKSPACE_ROOT` | `workspace_root` |
| `AGENTSMESH_MCP_PORT` | `mcp_port` |
| `AGENTSMESH_LOG_LEVEL` | `log_level` |

Sources: [runner/internal/config/config.go:103-165]()

---

## Starting the Runner

After registration:

```
agentsmesh-runner run
```

`runRunner` in [runner/cmd/runner/cmd_run.go:26-131]() loads `~/.agentsmesh/config.yaml`, calls `cfg.LoadGRPCConfig()` to verify the certificates are present and parseable, validates the config, and calls `startRunner`. `startRunner` creates a `runner.New(cfg)` instance, which internally creates a `GRPCConnection` from the cert paths. See [3.3]() for the connection lifecycle.

If the config file does not exist, the runner prints:

```
Error: Runner not registered. Please run 'agentsmesh-runner register' first.
```

### System service

The runner can be installed as a system service using the `service` subcommand ([runner/cmd/runner/service.go]()):

```
sudo agentsmesh-runner service install
sudo agentsmesh-runner service start
agentsmesh-runner service status
```

`runService` delegates to `svc.Install`, `svc.Start`, `svc.Stop`, etc. from the `internal/service` package using the `github.com/kardianos/service` library. The Linux package installs a systemd unit at `/etc/systemd/system/agentsmesh-runner.service`.

---

## Certificate Reactivation

Certificates have a finite lifetime. If a certificate expires, the runner will refuse to start with:

```
certificate has expired on <date>. Please reactivate the runner using:
  agentsmesh-runner reactivate --token <token>
```

This check is performed in `runner.New()` via `grpcConn.GetCertificateExpiryInfo()` in [runner/internal/runner/runner.go:108-121]().

The `reactivate` command in [runner/cmd/runner/cmd_reactivate.go]() accepts a `--token` flag (required) and an optional `--server` override. It calls `reactivateRunner` in [runner/cmd/runner/register.go:84-110](), which:

1. Calls `client.Reactivate` with a `ReactivationRequest`.
2. Loads the existing `Config` to get the certificate file paths.
3. Calls `cfg.SaveCertificates` to overwrite the three PEM files with the new ones.

The reactivation token is generated from the web UI under the runner management page.

**Diagram: Registration and reactivation flows end-to-end**

```mermaid
sequenceDiagram
    participant User
    participant CLI as "agentsmesh-runner CLI\ncmd/runner/main.go"
    participant Reg as "register.go"
    participant Client as "client package"
    participant Server as "AgentsMesh Backend"
    participant Disk as "~/.agentsmesh/"

    User->>CLI: register --token TOKEN
    CLI->>Reg: runRegister()
    Reg->>Reg: checkExistingRegistration()
    Reg->>Client: RegisterWithToken(TokenRegistrationRequest)
    Client->>Server: POST /api/runner/register
    Server-->>Client: OrgSlug, Certificate, PrivateKey, CACertificate, GRPCEndpoint
    Client-->>Reg: RegistrationResult
    Reg->>Reg: saveGRPCConfig()
    Reg->>Disk: config.yaml
    Reg->>Disk: certs/client.crt, client.key, ca.crt

    User->>CLI: run
    CLI->>Disk: config.Load()
    CLI->>Client: NewGRPCConnection(certFile, keyFile, caFile)
    Client->>Server: gRPC mTLS Connect

    Note over User,Server: Certificate expires
    User->>CLI: reactivate --token TOKEN
    CLI->>Reg: reactivateRunner()
    Reg->>Client: Reactivate(ReactivationRequest)
    Client->>Server: POST /api/runner/reactivate
    Server-->>Client: New Certificate, PrivateKey, CACertificate
    Reg->>Disk: overwrite certs/client.crt, client.key, ca.crt
```

Sources: [runner/cmd/runner/cmd_register.go](), [runner/cmd/runner/register.go](), [runner/cmd/runner/cmd_reactivate.go](), [runner/internal/runner/runner.go:108-121]()

---

# Page: CLI Reference

# CLI Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [runner/.goreleaser.yml](runner/.goreleaser.yml)
- [runner/README.md](runner/README.md)
- [runner/cmd/runner/cmd_reactivate.go](runner/cmd/runner/cmd_reactivate.go)
- [runner/cmd/runner/cmd_register.go](runner/cmd/runner/cmd_register.go)
- [runner/cmd/runner/cmd_run.go](runner/cmd/runner/cmd_run.go)
- [runner/cmd/runner/main.go](runner/cmd/runner/main.go)
- [runner/cmd/runner/register.go](runner/cmd/runner/register.go)
- [runner/cmd/runner/service.go](runner/cmd/runner/service.go)
- [runner/cmd/runner/update.go](runner/cmd/runner/update.go)
- [runner/cmd/runner/webconsole.go](runner/cmd/runner/webconsole.go)
- [runner/internal/client/grpc_connection.go](runner/internal/client/grpc_connection.go)
- [runner/internal/config/config.go](runner/internal/config/config.go)
- [runner/internal/config/config_defaults_test.go](runner/internal/config/config_defaults_test.go)
- [runner/internal/runner/runner.go](runner/internal/runner/runner.go)
- [web/public/install.ps1](web/public/install.ps1)
- [web/public/install.sh](web/public/install.sh)
- [web/src/app/docs/runners/setup/page.tsx](web/src/app/docs/runners/setup/page.tsx)

</details>



This page documents every subcommand and flag exposed by the `agentsmesh-runner` binary. It covers the command dispatcher in `runner/cmd/runner/main.go`, and the implementation files for each subcommand.

For background on how the runner connects to the backend after registration, see [gRPC Client](#3.3). For the installation steps that precede most commands, see [Installation and Registration](#3.1). For auto-update internals, see [Auto-Update](#3.8).

---

## Binary Overview

The binary is named `agentsmesh-runner`. Its entry point is `main()` in [runner/cmd/runner/main.go:14-44](). Two build-time variables are injected by GoReleaser via `-ldflags`:

| Variable | Purpose |
|---|---|
| `version` | Semantic version string (e.g. `v1.2.3`) |
| `buildTime` | RFC3339 build timestamp |

**Command Dispatch Diagram**

```mermaid
flowchart TD
    argv["os.Args[1]"]

    argv -->|"login / register"| runRegister["runRegister() — cmd_register.go"]
    argv -->|"run / start"| runRunner["runRunner() — cmd_run.go"]
    argv -->|"service"| runService["runService() — service.go"]
    argv -->|"webconsole / console"| runWebConsole["runWebConsole() — webconsole.go"]
    argv -->|"reactivate"| runReactivate["runReactivate() — cmd_reactivate.go"]
    argv -->|"update-endpoint"| runUpdateEndpoint["runUpdateEndpoint()"]
    argv -->|"update"| runUpdate["runUpdate() — update.go"]
    argv -->|"version / -v / --version"| version["print version + buildTime"]
    argv -->|"help / -h / --help"| printUsage["printUsage()"]
    argv -->|"unknown"| exitError["print error + printUsage()"]
```

Sources: [runner/cmd/runner/main.go:14-44]()

---

## `register` (alias: `login`)

Registers the runner with an AgentsMesh server. On success it writes `~/.agentsmesh/config.yaml` and stores mTLS certificates under `~/.agentsmesh/certs/`.

### Flags

| Flag | Type | Default | Description |
|---|---|---|---|
| `--server` | string | `https://agentsmesh.ai` | AgentsMesh server URL |
| `--token` | string | _(empty)_ | Registration token; if omitted, interactive browser flow is used |
| `--node-id` | string | hostname | Identifier for this runner instance |
| `--headless` | bool | `false` | Skip opening the browser; print the auth URL only (SSH-friendly) |
| `--force` | bool | `false` | Overwrite an existing registration without prompting |

### Registration Flows

```mermaid
flowchart TD
    start["runRegister()"]
    start --> checkExisting["checkExistingRegistration()\nreads ~/.agentsmesh/config.yaml"]
    checkExisting -->|"org_slug found + not --force"| prompt["prompt user y/N"]
    checkExisting -->|"no existing config"| flowDecision
    prompt -->|"yes"| flowDecision
    prompt -->|"no"| exit["exit 0"]

    flowDecision{{"--token provided?"}}
    flowDecision -->|"yes"| tokenFlow["registerWithGRPCToken()\nclient.RegisterWithToken()"]
    flowDecision -->|"no"| interactiveFlow["registerInteractive()\nclient.InteractiveRegister()"]

    tokenFlow --> saveConfig["saveGRPCConfig()\nwrites config.yaml + certs/"]
    interactiveFlow --> saveConfig
```

### Files Written After Registration

`saveGRPCConfig()` in [runner/cmd/runner/register.go:152-207]() writes the following YAML structure to `~/.agentsmesh/config.yaml`:

```yaml
server_url: <SERVER_URL>
node_id: <NODE_ID>
org_slug: <ORG_SLUG>
grpc_endpoint: <GRPC_ENDPOINT>
cert_file: ~/.agentsmesh/certs/client.crt
key_file:  ~/.agentsmesh/certs/client.key
ca_file:   ~/.agentsmesh/certs/ca.crt
max_concurrent_pods: 5
workspace_root: /tmp/agentsmesh-workspace
default_agent: claude-code
default_shell: /bin/bash    # or $SHELL
health_check_port: 9090
log_level: info
```

If an existing `config.yaml` is found, `backupExistingConfig()` renames it to `config.<org-slug>.yaml.bak` and moves the `certs/` directory to `certs.<org-slug>.bak/`.

Sources: [runner/cmd/runner/cmd_register.go:14-95](), [runner/cmd/runner/register.go:29-207]()

---

## `run` (alias: `start`)

Starts the runner process in the foreground. The runner must be registered first.

### Flags

| Flag | Type | Default | Description |
|---|---|---|---|
| `--config` | string | `~/.agentsmesh/config.yaml` | Path to config file |
| `--log-level` | string | _(from config)_ | Override log level: `debug`, `info`, `warn`, `error` |
| `--logpty` | bool | `false` | Write raw PTY output to log files (debugging) |
| `--logpty-dir` | string | `$TMPDIR/agentsmesh/pty-logs` | Directory for PTY logs |

### Startup Sequence

```mermaid
sequenceDiagram
    participant CLI as "runRunner()"
    participant Config as "config.Load()"
    participant Logger as "logger.Init()"
    participant PID as "pidfile"
    participant Runner as "runner.New()"
    participant Console as "console.New()"
    participant Supervisor as "suture.Supervisor"

    CLI->>Config: Load config file
    CLI->>Logger: Init with log config
    Config->>CLI: *Config
    CLI->>PID: CleanupStaleProcess()
    CLI->>PID: Write()
    CLI->>Runner: New(cfg)
    Runner->>Runner: LoadGRPCConfig() — load certs
    Runner->>Runner: NewGRPCConnection()
    Runner->>Runner: GetCertificateExpiryInfo()
    CLI->>Console: New(cfg, port=19080, version)
    CLI->>Supervisor: Serve(ctx) — blocks
    Supervisor-->>CLI: ctx cancelled / error
    CLI->>PID: Remove()
```

The runner exits with code `1` on fatal errors. Graceful shutdown is triggered by `SIGINT` or `SIGTERM`.

Sources: [runner/cmd/runner/cmd_run.go:26-202](), [runner/internal/runner/runner.go:57-149]()

### Config File Resolution

The `Config` struct in [runner/internal/config/config.go:12-79]() is populated by [Viper](https://github.com/spf13/viper). The environment variable prefix is `AGENTSMESH_`, so `AGENTSMESH_SERVER_URL` overrides `server_url`.

| Config Key | Default | Env Variable |
|---|---|---|
| `server_url` | `https://agentsmesh.ai` | `AGENTSMESH_SERVER_URL` |
| `max_concurrent_pods` | `5` | `AGENTSMESH_MAX_CONCURRENT_PODS` |
| `workspace_root` | `/workspace` | `AGENTSMESH_WORKSPACE_ROOT` |
| `mcp_port` | `19000` | `AGENTSMESH_MCP_PORT` |
| `health_check_port` | `9090` | `AGENTSMESH_HEALTH_CHECK_PORT` |
| `log_level` | `info` | `AGENTSMESH_LOG_LEVEL` |
| `default_agent` | `claude-code` | `AGENTSMESH_DEFAULT_AGENT` |
| `auto_update.enabled` | `true` | — |
| `auto_update.channel` | `stable` | — |
| `auto_update.check_interval` | `24h` | — |

Sources: [runner/internal/config/config.go:102-165]()

---

## `service`

Installs and manages the runner as an OS system service. Uses [kardianos/service](https://github.com/kardianos/service) under the hood.

### Usage

```
agentsmesh-runner service <action> [options]
```

### Actions

| Action | Description |
|---|---|
| `install` | Register and enable the runner as a system service |
| `uninstall` | Remove the system service registration |
| `start` | Start the service |
| `stop` | Stop the service |
| `restart` | Restart the service |
| `status` | Print `Running`, `Stopped`, or `Unknown` |

### `service install` Flags

| Flag | Type | Default | Description |
|---|---|---|---|
| `--config` | string | `~/.agentsmesh/config.yaml` | Path to config file used by the service |

The config file must exist before running `service install`. The Linux package (`.deb`/`.rpm`) ships a pre-built systemd unit file at `/etc/systemd/system/agentsmesh-runner.service` (see [runner/.goreleaser.yml:82-116]()).

Sources: [runner/cmd/runner/service.go:14-149]()

---

## `webconsole` (alias: `console`)

Opens the local web console in the default browser. The console is hosted by the runner process itself when `run` is active.

### Flags

| Flag | Type | Default | Description |
|---|---|---|---|
| `--port` | int | `19080` | Port the console is listening on |

The command performs an HTTP `GET /api/status` check before opening the browser. If the runner is not running, it exits with an error.

### Browser Launch

`openBrowser()` in [runner/cmd/runner/webconsole.go:65-80]() uses platform-specific commands:

| Platform | Command |
|---|---|
| macOS | `open <url>` |
| Linux | `xdg-open <url>` |
| Windows | `rundll32 url.dll,FileProtocolHandler <url>` |

The console URL is always `http://127.0.0.1:<port>`.

Sources: [runner/cmd/runner/webconsole.go:14-80]()

---

## `reactivate`

Refreshes mTLS certificates for a runner whose certificate has expired. This is needed when a runner has been offline for an extended period.

### Flags

| Flag | Type | Default | Description |
|---|---|---|---|
| `--token` | string | _(required)_ | Reactivation token from the web UI |
| `--server` | string | _(from config)_ | Server URL; falls back to `server_url` in `config.yaml` |

### Flow

```mermaid
sequenceDiagram
    participant CLI as "runReactivate()"
    participant Config as "config.Load()"
    participant Client as "client.Reactivate()"
    participant Disk as "cfg.SaveCertificates()"

    CLI->>Config: load ~/.agentsmesh/config.yaml
    Config->>CLI: cfg.ServerURL
    CLI->>Client: ReactivationRequest{ServerURL, Token}
    Client-->>CLI: new Certificate, PrivateKey, CACertificate
    CLI->>Disk: overwrite ~/.agentsmesh/certs/
```

The reactivation token is generated from the web UI's Runner management page. Timeout is 30 seconds.

Sources: [runner/cmd/runner/cmd_reactivate.go:14-71](), [runner/cmd/runner/register.go:83-110]()

---

## `update`

Checks for and installs a new version of `agentsmesh-runner` from GitHub Releases. Internally uses the `updater` package (see [Auto-Update](#3.8)).

### Flags

| Flag | Shorthand | Type | Default | Description |
|---|---|---|---|---|
| `--check` | `-c` | bool | `false` | Only check; do not download or install |
| `--yes` | `-y` | bool | `false` | Skip the confirmation prompt |
| `--version` | `-v` | string | _(latest)_ | Install a specific version (e.g. `v1.2.3`) |
| `--force` | `-f` | bool | `false` | Skip waiting for active pods to finish |
| `--pre` | — | bool | `false` | Include prerelease versions in the update check |

### Update Flow

```mermaid
flowchart TD
    start["runUpdate()"]
    start --> check["u.CheckForUpdate(ctx)"]
    check --> hasUpdate{{"HasUpdate?"}}
    hasUpdate -->|"no"| done["print 'already up to date'"]
    hasUpdate -->|"yes"| checkOnly{"--check flag?"}
    checkOnly -->|"yes"| printNotes["print release notes + exit"]
    checkOnly -->|"no"| confirm{"--yes flag?"}
    confirm -->|"no"| prompt["confirmUpdate() — y/N prompt"]
    confirm -->|"yes"| backup
    prompt -->|"yes"| backup["u.CreateBackup()"]
    prompt -->|"no"| cancelled["print 'cancelled'"]
    backup --> download["u.Download(ctx, version, progress)"]
    download --> apply["u.Apply(tmpPath)"]
    apply -->|"success"| restart["print 'restart required'"]
    apply -->|"failure"| rollback["u.Rollback()"]
```

Sources: [runner/cmd/runner/update.go:14-228]()

---

## `update-endpoint`

Updates the stored gRPC endpoint in `~/.agentsmesh/config.yaml` without performing a full re-registration. This is used when the server's gRPC address changes. The implementation delegates to `runUpdateEndpoint()` in the main package.

---

## `version`

Prints the version string and build time then exits.

```
AgentsMesh Runner v1.2.3 (built 2024-01-15T10:00:00Z)
```

Aliases: `-v`, `--version`.

Sources: [runner/cmd/runner/main.go:35-37]()

---

## Command-to-File Map

```mermaid
flowchart LR
    main["main.go\nmain()"]

    main --> cr["cmd_register.go\nrunRegister()"]
    main --> crun["cmd_run.go\nrunRunner()"]
    main --> svc["service.go\nrunService()"]
    main --> wc["webconsole.go\nrunWebConsole()"]
    main --> react["cmd_reactivate.go\nrunReactivate()"]
    main --> upd["update.go\nrunUpdate()"]
    main --> reg["register.go\nsaveGRPCConfig()\nregisterInteractive()\nregisterWithGRPCToken()\nreactivateRunner()"]

    cr --> reg
    react --> reg
    crun --> cfgpkg["config/config.go\nconfig.Load()"]
    cr --> cfgpkg
```

Sources: [runner/cmd/runner/main.go:1-78](), [runner/cmd/runner/cmd_register.go:1-120](), [runner/cmd/runner/cmd_run.go:1-202](), [runner/cmd/runner/service.go:1-149](), [runner/cmd/runner/webconsole.go:1-80](), [runner/cmd/runner/cmd_reactivate.go:1-71](), [runner/cmd/runner/update.go:1-228](), [runner/cmd/runner/register.go:1-234]()

---

# Page: gRPC Client

# gRPC Client

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/cmd/server/grpc_init.go](backend/cmd/server/grpc_init.go)
- [backend/cmd/server/grpc_init_test.go](backend/cmd/server/grpc_init_test.go)
- [backend/internal/infra/pki/service.go](backend/internal/infra/pki/service.go)
- [backend/internal/infra/pki/service_server.go](backend/internal/infra/pki/service_server.go)
- [backend/internal/infra/pki/service_test.go](backend/internal/infra/pki/service_test.go)
- [runner/cmd/runner/cmd_reactivate.go](runner/cmd/runner/cmd_reactivate.go)
- [runner/cmd/runner/cmd_register.go](runner/cmd/runner/cmd_register.go)
- [runner/cmd/runner/cmd_run.go](runner/cmd/runner/cmd_run.go)
- [runner/cmd/runner/main.go](runner/cmd/runner/main.go)
- [runner/cmd/runner/register.go](runner/cmd/runner/register.go)
- [runner/cmd/runner/service.go](runner/cmd/runner/service.go)
- [runner/cmd/runner/update.go](runner/cmd/runner/update.go)
- [runner/cmd/runner/webconsole.go](runner/cmd/runner/webconsole.go)
- [runner/internal/client/grpc_connection.go](runner/internal/client/grpc_connection.go)
- [runner/internal/client/grpc_connection_options.go](runner/internal/client/grpc_connection_options.go)
- [runner/internal/client/grpc_tls.go](runner/internal/client/grpc_tls.go)
- [runner/internal/runner/runner.go](runner/internal/runner/runner.go)

</details>



This page documents the runner-side gRPC client: how it establishes an mTLS connection to the backend, manages the bidirectional streaming protocol, routes messages, handles reconnection, and integrates with the suture supervisor tree.

For the backend counterpart that receives connections from runners, see [Runner Connection Manager](#2.3). For the gRPC proto definitions and message types, see [gRPC API and Runner Communication](#2.2). For PKI and certificate issuance, see [PKI and mTLS](#2.8).

---

## Overview

The runner communicates with the backend exclusively over a long-lived gRPC bidirectional stream secured with mutual TLS (mTLS). The central implementation lives in `runner/internal/client/`, with the top-level struct being `GRPCConnection` ([runner/internal/client/grpc_connection.go:29-106]()).

`GRPCConnection` is responsible for:

- Dialing the backend with mTLS credentials
- Opening and maintaining a bidirectional stream (`RunnerService.Connect`)
- Priority-based message sending (control vs. terminal output)
- Reconnection with exponential backoff
- Periodic heartbeat
- Background certificate renewal

---

## Component Map

**Supervisor tree and key types involved in the gRPC client:**

```mermaid
graph TD
  sutureTop["suture.Supervisor (\"runner\")"]
  connSvc["lifecycle.ConnectionService"]
  grpcConn["client.GRPCConnection"]
  handler["runner.RunnerMessageHandler"]
  rpcClient["client.RPCClient"]
  agentProbe["client.AgentProbe"]
  reconnect["client.ReconnectStrategy"]
  tlsCreds["advancedtls credentials"]
  identProvider["pemfile.Provider (identity)"]
  rootProvider["pemfile.Provider (root CA)"]

  sutureTop --> connSvc
  connSvc --> grpcConn
  grpcConn --> handler
  grpcConn --> rpcClient
  grpcConn --> agentProbe
  grpcConn --> reconnect
  grpcConn --> tlsCreds
  tlsCreds --> identProvider
  tlsCreds --> rootProvider
```

Sources: [runner/internal/client/grpc_connection.go:29-106](), [runner/internal/runner/runner.go:197-250]()

---

## GRPCConnection Struct

`GRPCConnection` ([runner/internal/client/grpc_connection.go:29-106]()) aggregates all connection state. The most important fields by role:

| Field group | Fields | Purpose |
|---|---|---|
| Identity | `endpoint`, `nodeID`, `orgSlug` | Target server address and runner identity |
| mTLS cert paths | `certFile`, `keyFile`, `caFile` | File paths for hot-reload cert providers |
| gRPC components | `conn`, `client`, `stream` | Raw connection, service client, active stream |
| Cert providers | `identityProvider`, `rootProvider` | `pemfile.Provider` instances; closed on reconnect to prevent goroutine leaks |
| Messaging | `handler` | `MessageHandler` interface; set to `RunnerMessageHandler` at startup |
| Priority channels | `controlCh` (buf 100), `terminalCh` (buf 1000) | Separate send queues; control messages always win |
| Lifecycle | `stopCh`, `stopOnce`, `reconnectCh` | Shutdown and reconnect signalling |
| Rate limiter | `terminalRateLimiter`, `terminalRateLimit` | Token-bucket limiting terminal output (default 50 KB/s) |
| Cert renewal | `certRenewalCheckInterval`, `certRenewalDays`, `certUrgentDays` | Background cert expiry checker |
| Reconnection | `reconnectStrategy` | `ReconnectStrategy` with configurable base/max delays |
| Stuck detection | `lastSendTime` (atomic) | Watchdog reads this to detect a frozen write loop |
| MCP RPC | `rpcClient` | `RPCClient` for request-response multiplexing over the stream |
| Agent probe | `agentProbe` | `AgentProbe` for detecting available agent binaries |
| Fatal error | `fatalErr`, `fatalErrMu` | Stops reconnection on unrecoverable errors |

Sources: [runner/internal/client/grpc_connection.go:29-106]()

---

## Connection Lifecycle

### Initialization

`GRPCConnection` is constructed in `runner.New()` ([runner/internal/runner/runner.go:97-105]()) using `NewGRPCConnection`, then started by the suture supervisor via `lifecycle.ConnectionService`.

Defaults set by `NewGRPCConnection` ([runner/internal/client/grpc_connection.go:109-148]()):

| Parameter | Default |
|---|---|
| `heartbeatInterval` | 30 s |
| `initTimeout` | 30 s |
| `reconnectStrategy` | base 5 s, max 5 min |
| `certRenewalCheckInterval` | 24 h |
| `certRenewalDays` | 30 days |
| `certUrgentDays` | 7 days |
| `terminalRateLimit` | 50 KB/s |

### Start / Stop

```
GRPCConnection.Start()  →  safego.Go("grpc-connection-loop", c.connectionLoop)
GRPCConnection.Stop()   →  closes stopCh, closes conn, closes cert providers
```

`Start` ([runner/internal/client/grpc_connection.go:248-251]()) spawns `connectionLoop` in a managed goroutine. `Stop` ([runner/internal/client/grpc_connection.go:254-275]()) is idempotent via `sync.Once`.

### Connection loop (connectionLoop / runConnection)

The logic is in `grpc_connection_loop.go` (referenced at [runner/internal/client/grpc_connection.go:277]()):

```mermaid
flowchart TD
  start["connectionLoop start"]
  checkFatal["getFatalError() == nil?"]
  connect["Connect() — dial + advancedtls"]
  stream["open BidiStream"]
  init["send Initialize message\nwait initResultCh (30s timeout)"]
  loops["start readLoop + writeLoop\n+ heartbeatLoop + certRenewalChecker"]
  wait["wait: stopCh | reconnectCh | stream error"]
  fatalCheck["isFatalStreamError(err)?"]
  setFatal["setFatalError — stop retrying"]
  backoff["ReconnectStrategy.Wait()"]
  stopped["return (stopped)"]

  start --> checkFatal
  checkFatal -- "yes" --> connect
  checkFatal -- "no" --> stopped
  connect -- "error" --> backoff
  connect -- "ok" --> stream
  stream --> init
  init --> loops
  loops --> wait
  wait -- "stopCh" --> stopped
  wait -- "stream error" --> fatalCheck
  fatalCheck -- "yes (Unauthenticated/PermissionDenied)" --> setFatal
  setFatal --> stopped
  fatalCheck -- "no" --> backoff
  backoff --> checkFatal
```

Sources: [runner/internal/client/grpc_connection.go:248-277](), [runner/internal/client/grpc_connection.go:282-321]()

---

## mTLS and Certificate Hot-Reload

`Connect()` calls `createAdvancedTLSCredentials()` ([runner/internal/client/grpc_tls.go:26-73]()) which uses `google.golang.org/grpc/security/advancedtls` with `pemfile.Provider` instances:

| Provider | Watches | Refresh interval |
|---|---|---|
| `identityProvider` | `certFile`, `keyFile` | 1 hour |
| `rootProvider` | `caFile` | 24 hours |

The providers automatically reload files when they change, so certificate renewal does not require a reconnect in the normal case. Providers are explicitly closed on every reconnect to prevent goroutine leaks ([runner/internal/client/grpc_connection.go:186-203]()).

**Fallback chain** when providers fail to initialize:

```
pemfile providers (advancedtls) → static CA pool (advancedtls) → standard tls.Config with VerifyConnection
```

The TLS policy uses `advancedtls.CertVerification` (chain-only, no hostname check) so that SNI remains the dial target hostname for correct Traefik/proxy routing even when the server cert SANs differ from the public hostname ([runner/internal/client/grpc_tls.go:63-66]()).

Sources: [runner/internal/client/grpc_tls.go:26-73](), [runner/internal/client/grpc_tls.go:110-156]()

---

## Message Priority and Write Loop

Two buffered channels separate message classes:

```
controlCh  (buf 100)  ← heartbeat, pod_created, pod_terminated, OSC events
terminalCh (buf 1000) ← agent_status (terminal output via Relay)
```

The write loop always drains `controlCh` first via a `select` with priority, then falls through to `terminalCh`. Terminal output is also subject to the token-bucket rate limiter (`terminalRateLimiter`) to avoid saturating slow upstream connections ([runner/internal/client/grpc_connection.go:73-85]()).

`lastSendTime` is updated atomically on each successful send. The Watchdog service reads `LastActivityTime()` ([runner/internal/client/grpc_connection.go:325-331]()) to detect a stuck write loop and trigger reconnection.

Sources: [runner/internal/client/grpc_connection.go:73-85](), [runner/internal/client/grpc_connection.go:325-331]()

---

## Heartbeat

A dedicated heartbeat goroutine sends a `RunnerMessage` of heartbeat type every `heartbeatInterval` (default 30 s) to the `controlCh`. This keeps the gRPC stream alive through NAT devices and load balancers, and also allows the backend to track runner liveness. The keepalive parameters passed to `grpc.Dial` mirror this: ping every 30 s, timeout 10 s ([runner/internal/client/grpc_connection.go:220-225]()).

---

## Certificate Renewal

`certRenewalChecker` ([runner/internal/client/grpc_tls.go:159-175]()) runs on a background goroutine alongside the active stream:

1. Every `certRenewalCheckInterval` (24 h), it calls `checkCertificateExpiry`.
2. If days until expiry ≤ `certRenewalDays` (30), it calls `renewCertificate()`.
3. `renewCertificate` POSTs to the backend REST API (`serverURL`) and overwrites `certFile`/`keyFile` on disk.
4. `advancedtls` picks up the new files at the next provider refresh (within 1 h) — no reconnect needed.
5. If days until expiry ≤ `certUrgentDays` (7), it also calls `triggerReconnect()` to force a fresh TLS handshake with the new certificate immediately.

Sources: [runner/internal/client/grpc_tls.go:158-308]()

---

## Fatal Error Handling

`isFatalStreamError` ([runner/internal/client/grpc_connection.go:297-321]()) inspects gRPC status codes returned by the stream:

| gRPC code | Condition | Action |
|---|---|---|
| `Unauthenticated` | "runner not found" | Fatal — print re-register instructions |
| `Unauthenticated` | other auth failures | Fatal — print re-register instructions |
| `PermissionDenied` | "runner is disabled" | Fatal — print admin contact instructions |
| Anything else | — | Retryable — wait and reconnect |

When an error is marked fatal, `setFatalError` stores it and `connectionLoop` exits permanently without further retries.

Sources: [runner/internal/client/grpc_connection.go:282-321]()

---

## Functional Options

`GRPCConnection` is configured through the `GRPCConnectionOption` functional option pattern ([runner/internal/client/grpc_connection_options.go]()):

| Option | Sets |
|---|---|
| `WithGRPCHeartbeatInterval(d)` | `heartbeatInterval` |
| `WithGRPCInitTimeout(d)` | `initTimeout` |
| `WithGRPCRunnerVersion(v)` | `runnerVersion` (sent on init) |
| `WithGRPCMCPPort(p)` | `mcpPort` (sent on init) |
| `WithGRPCTerminalRateLimit(n)` | `terminalRateLimit` bytes/s |
| `WithGRPCServerURL(url)` | `serverURL` for cert renewal REST calls |
| `WithGRPCCertRenewalDays(n)` | `certRenewalDays` |
| `WithGRPCCertUrgentDays(n)` | `certUrgentDays` |
| `WithGRPCEndpointChanged(fn)` | `onEndpointChanged` callback for auto-discovery |

The `onEndpointChanged` callback is wired to `config.UpdateGRPCEndpointInFile` in `runner.New()` so that when the backend advertises a new gRPC endpoint (e.g., after a migration), the runner persists it to `config.yaml` for use after restart ([runner/internal/runner/runner.go:88-95]()).

Sources: [runner/internal/client/grpc_connection_options.go](), [runner/internal/runner/runner.go:84-105]()

---

## Endpoint Parsing

`parseGRPCEndpoint` ([runner/internal/client/grpc_connection.go:343-375]()) normalises the endpoint before dialing:

| Input format | Resolved to |
|---|---|
| `grpcs://host:port` | `host:port` |
| `grpc://host:port` | `host:port` |
| `host:port` | `host:port` (passthrough) |

This lets the config file use `grpcs://` URIs for clarity while passing bare `host:port` to `grpc.Dial`.

Sources: [runner/internal/client/grpc_connection.go:338-375]()

---

## Suture Integration

The `GRPCConnection` implements the `Connection` interface ([runner/internal/client/grpc_connection.go:334]()), which in turn satisfies `suture.Service` via `lifecycle.ConnectionService`. The supervisor in `runner.Run` ([runner/internal/runner/runner.go:209-244]()) adds it as a supervised service:

```mermaid
graph LR
  sutureSpec["suture.Spec\nFailureThreshold=5\nFailureDecay=60s\nFailureBackoff=5s"]
  supervisor["suture.New(\"runner\", spec)"]
  connSvc["lifecycle.ConnectionService\n(wraps GRPCConnection)"]
  mcpSvc["lifecycle.MCPServerService"]
  monSvc["lifecycle.MonitorService"]
  watchdog["lifecycle.WatchdogService\n(reads LastActivityTime)"]
  consoleSvc["lifecycle.ConsoleService"]

  supervisor -->|"Add"| connSvc
  supervisor -->|"Add"| mcpSvc
  supervisor -->|"Add"| monSvc
  supervisor -->|"Add"| watchdog
  supervisor -->|"Add"| consoleSvc
```

If `ConnectionService` exits unexpectedly, suture restarts it subject to `FailureThreshold` (5 failures before backing off). The Watchdog polls `GRPCConnection.LastActivityTime()` on its own interval (15 s) and can signal reconnection if the write loop appears stuck.

Sources: [runner/internal/runner/runner.go:208-244]()

---

# Page: Pod and Terminal Management

# Pod and Terminal Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude/skills/gh-merge/SKILL.md](.claude/skills/gh-merge/SKILL.md)
- [backend/internal/api/grpc/runner_adapter_test.go](backend/internal/api/grpc/runner_adapter_test.go)
- [backend/internal/service/runner/connection_manager.go](backend/internal/service/runner/connection_manager.go)
- [runner/go.mod](runner/go.mod)
- [runner/go.sum](runner/go.sum)
- [runner/internal/client/interface.go](runner/internal/client/interface.go)
- [runner/internal/relay/client_token_test.go](runner/internal/relay/client_token_test.go)
- [runner/internal/runner/message_handler.go](runner/internal/runner/message_handler.go)
- [runner/internal/runner/message_handler_pod_create_test.go](runner/internal/runner/message_handler_pod_create_test.go)
- [runner/internal/runner/pod.go](runner/internal/runner/pod.go)
- [runner/internal/terminal/terminal.go](runner/internal/terminal/terminal.go)
- [runner/internal/terminal/terminal_io.go](runner/internal/terminal/terminal_io.go)
- [runner/internal/terminal/terminal_pty.go](runner/internal/terminal/terminal_pty.go)
- [runner/internal/terminal/terminal_pty_unix.go](runner/internal/terminal/terminal_pty_unix.go)
- [runner/internal/terminal/terminal_pty_windows.go](runner/internal/terminal/terminal_pty_windows.go)
- [runner/internal/terminal/terminal_resize.go](runner/internal/terminal/terminal_resize.go)
- [runner/internal/terminal/terminal_struct_test.go](runner/internal/terminal/terminal_struct_test.go)

</details>



This page documents the `Pod` struct, the `Terminal` abstraction, and the platform-specific PTY implementations in the runner. It covers how a pod is created and destroyed, how the PTY process is launched and managed, and how backpressure is applied when output consumers fall behind.

For how the runner receives commands from the backend that trigger pod creation, see the gRPC client documentation at [3.3](). For how the runner connects to the Relay service to stream terminal output to the browser, see [3.5](). For workspace and git setup that happens during pod build, see [3.7]().

---

## The Pod Struct

A `Pod` is the central data object representing one active terminal session on the runner. It is defined in [runner/internal/runner/pod.go:17-49]().

| Field | Type | Purpose |
|-------|------|---------|
| `PodKey` | `string` | Unique key assigned by the backend |
| `Terminal` | `*terminal.Terminal` | The PTY process wrapper |
| `VirtualTerminal` | `*vt.VirtualTerminal` | In-memory VT100 screen for state detection |
| `Aggregator` | `*aggregator.SmartAggregator` | Adaptive frame-rate output batching |
| `RelayClient` | `relay.RelayClient` | WebSocket client for Relay connection |
| `Clipboard` | `clipboard.Backend` | Image paste support |
| `SandboxPath` | `string` | Filesystem path to the pod's workspace |
| `Branch` | `string` | Git branch for worktree-based pods |
| `Status` | `string` | One of `initializing`, `running`, `stopped`, `failed` |
| `stateDetector` | `*ManagedStateDetector` | Multi-signal agent state detector |
| `PTYLogger` | `*aggregator.PTYLogger` | Optional PTY output logger |
| `tokenRefreshCh` | `chan string` | Used for relay token refresh handoff |
| `ptyErrorMsg` | `string` | Stores fatal PTY error for the exit handler |

Status transitions are protected by `statusMu` (an `sync.RWMutex`). The `RelayClient` field is accessed via `SetRelayClient`/`GetRelayClient` which acquire `relayMu`.

**Pod status constants** [runner/internal/runner/pod.go:51-57]():

```
PodStatusInitializing → PodStatusRunning → PodStatusStopped
                                         ↘ PodStatusFailed
```

Sources: [runner/internal/runner/pod.go:17-57]()

---

## Pod Lifecycle

Pods are created and destroyed by `RunnerMessageHandler` in [runner/internal/runner/message_handler.go](). The handler itself holds a reference to a `PodStore` and a `client.Connection`.

**Pod creation lifecycle** — `OnCreatePod` [runner/internal/runner/message_handler.go:32-158]():

**Pod creation and destruction flow**

```mermaid
sequenceDiagram
    participant "Backend" as backend
    participant "RunnerMessageHandler" as handler
    participant "PodStore" as store
    participant "PodBuilder" as builder
    participant "Terminal" as terminal
    participant "MCPServer" as mcp

    backend->>handler: "OnCreatePod(CreatePodCommand)"
    handler->>store: "Put(podKey, placeholder {status: initializing})"
    handler->>builder: "NewPodBuilderFromRunner().WithCommand().Build(ctx)"
    Note over builder: "git clone, workspace setup, env prep"
    builder-->>handler: "Pod{Terminal, SandboxPath, Branch, ...}"
    handler->>store: "Check if pod still exists (TerminatePod race)"
    handler->>terminal: "SetExitHandler()"
    handler->>terminal: "SetPTYErrorHandler()"
    handler->>store: "Put(podKey, fullyBuiltPod)"
    handler->>terminal: "Start()"
    handler->>store: "SetStatus(running)"
    handler->>mcp: "RegisterPod(podKey)"
    handler->>backend: "SendPodCreated(podKey, pid, sandboxPath, branch)"
```

**Pod termination** — `OnTerminatePod` [runner/internal/runner/message_handler.go:161-192]():

1. Removes pod from `PodStore` with `Delete`.
2. Closes `PTYLogger` if active.
3. Calls `pod.StopStateDetector()`.
4. Calls `pod.Aggregator.Stop()`.
5. Calls `pod.Terminal.Stop()` — graceful shutdown with a 5-second SIGTERM window.
6. Unregisters from `MCPServer` and `agentMonitor`.
7. Sends `pod_terminated` event to backend.

Sources: [runner/internal/runner/message_handler.go:32-192](), [runner/internal/runner/pod.go:17-57]()

---

## PodStore

`PodStore` is the in-memory map of active pods on the runner. It is an interface defined alongside `RunnerMessageHandler` and implemented by `InMemoryPodStore`. Key operations:

| Method | Description |
|--------|-------------|
| `Put(key, pod)` | Insert or replace a pod |
| `Get(key)` | Retrieve a pod by key |
| `Delete(key)` | Remove and return a pod |
| `All()` | Return all current pods |

Sources: [runner/internal/runner/message_handler.go:1-30]()

---

## The Terminal Abstraction

`Terminal` in [runner/internal/terminal/terminal.go]() wraps a platform-specific PTY process. It is intentionally unaware of gRPC or relay details; it only knows how to start, stop, read, write, and resize a PTY.

**Key fields** [runner/internal/terminal/terminal.go:35-68]():

| Field | Purpose |
|-------|---------|
| `proc` | `ptyProcess` — platform-specific handle |
| `onOutput` | Callback fired when PTY produces output |
| `onExit` | Callback fired when the process exits |
| `onPTYError` | Callback for fatal read errors (e.g. disk full) |
| `readPaused` / `resumeCh` | Backpressure control state |
| `doneCh` | Closed by `waitExit` goroutine on process exit |
| `ptyCloseOnce` | Ensures PTY fd is closed exactly once |

**Terminal struct and its platform backend**

```mermaid
classDiagram
    class "terminal.Terminal" {
        +command string
        +proc ptyProcess
        +onOutput func([]byte)
        +onExit func(int)
        +onPTYError func(error)
        +readPaused bool
        +resumeCh chan struct
        +doneCh chan struct
        +Start() error
        +Stop()
        +Write(data) error
        +Resize(cols, rows) error
        +Redraw() error
        +PauseRead()
        +ResumeRead()
        +PID() int
    }
    class "ptyProcess" {
        <<interface>>
        +Read(p) (n, err)
        +Write(data) (n, err)
        +Close() error
        +Resize(cols, rows) error
        +GetSize() (cols, rows, err)
        +Pid() int
        +SetReadDeadline(t) error
        +Wait() (exitCode, err)
        +Kill() error
        +GracefulStop() error
    }
    class "unixPTY" {
        +cmd exec.Cmd
        +ptyFile os.File
        +GracefulStop() SIGTERM
    }
    class "windowsPTY" {
        +cpty conpty.ConPty
        +readCh chan readResult
        +closedCh chan struct
        +GracefulStop() Ctrl+C
    }
    "terminal.Terminal" --> "ptyProcess"
    "ptyProcess" <|.. "unixPTY"
    "ptyProcess" <|.. "windowsPTY"
```

Sources: [runner/internal/terminal/terminal.go:35-68](), [runner/internal/terminal/terminal_pty.go](), [runner/internal/terminal/terminal_pty_unix.go](), [runner/internal/terminal/terminal_pty_windows.go]()

---

## Platform-Specific PTY Implementations

The `ptyProcess` interface defined in [runner/internal/terminal/terminal_pty.go]() has two implementations, selected at compile time by build tags.

### Unix — `unixPTY`

File: [runner/internal/terminal/terminal_pty_unix.go]()

Uses `github.com/creack/pty`. The `startPTY` function calls `pty.StartWithSize(cmd, winSize)`, which forks the child process inside a PTY master/slave pair. The returned `*os.File` is the PTY master.

- `Resize` calls `pty.Setsize(ptyFile, &pty.Winsize{...})`.
- `GracefulStop` sends `syscall.SIGTERM` to the process.
- `Kill` calls `process.Kill()`.
- `Wait` calls `cmd.Wait()` and unwraps `*exec.ExitError` for exit code.

### Windows — `windowsPTY`

File: [runner/internal/terminal/terminal_pty_windows.go]()

Uses `github.com/UserExistsError/conpty` which wraps the Windows ConPTY API. Because ConPTY's `Read` is blocking without deadline support, `windowsPTY` spawns a `backgroundReader` goroutine that feeds a `readCh` channel. The `Read` method then selects on `readCh`, a deadline timer, and `closedCh`.

- `GracefulStop` writes byte `0x03` (Ctrl+C) to the PTY.
- `Kill` calls `Close()`, which terminates the ConPTY session.
- Read deadlines are implemented via a `deadlineMu`-protected `readDeadline` field.

| Feature | Unix (`unixPTY`) | Windows (`windowsPTY`) |
|---------|-------------------|------------------------|
| Library | `creack/pty` | `UserExistsError/conpty` |
| Graceful stop | SIGTERM | Ctrl+C byte (0x03) |
| Read deadline | Native (`os.File.SetReadDeadline`) | Emulated via goroutine + channel |
| Size query | `pty.GetsizeFull` | Stored `cols`/`rows` fields |

Sources: [runner/internal/terminal/terminal_pty_unix.go](), [runner/internal/terminal/terminal_pty_windows.go]()

---

## PTY Lifecycle: Start, Stop, Resize

### Start

`Terminal.Start()` [runner/internal/terminal/terminal.go:131-160]():

1. Calls `startPTY(command, args, workDir, env, cols, rows)` — platform dispatch.
2. Assigns the returned `ptyProcess` to `t.proc`.
3. Spawns two goroutines via `safego.Go`:
   - `"pty-read"` → `readOutput()`
   - `"pty-wait"` → `waitExit()`

### Stop

`Terminal.Stop()` [runner/internal/terminal/terminal.go:167-211]():

1. Sets `t.closed = true` under `t.mu`.
2. Calls `proc.GracefulStop()` (SIGTERM / Ctrl+C).
3. Waits on `t.doneCh` for up to `gracefulStopTimeout` (5 seconds).
4. If timeout expires, calls `proc.Kill()` and waits 1 more second.
5. Calls `closePTY()` via `sync.Once` to close the PTY file descriptor.

This two-phase shutdown ensures AI agents (Claude Code, Aider, etc.) have time to release git locks and save state before being forcibly killed.

### Resize

`Terminal.Resize(cols, rows)` [runner/internal/terminal/terminal_resize.go:13-24]() delegates directly to `t.proc.Resize(cols, rows)`.

`Terminal.Redraw()` [runner/internal/terminal/terminal_resize.go:30-58]() triggers a redraw by briefly expanding the terminal width by 1 column, waiting 50ms, then restoring. This handles programs that ignore `SIGWINCH` when idle.

Sources: [runner/internal/terminal/terminal.go:131-211](), [runner/internal/terminal/terminal_resize.go:13-58]()

---

## Output Backpressure

The `readOutput` loop in [runner/internal/terminal/terminal_io.go:14-146]() implements ttyd-style flow control. When the consumer (e.g. the relay WebSocket or gRPC send queue) cannot keep up, it calls `PauseRead()`, which sets `t.readPaused = true`. The read loop detects this flag and blocks on `resumeCh`.

**Backpressure flow**

```mermaid
flowchart TD
    A["readOutput goroutine"] --> B{"t.readPaused?"}
    B -- "yes" --> C["block on resumeCh or 100ms timeout"]
    C --> D{"terminal closed?"}
    D -- "yes" --> E["return"]
    D -- "no" --> B
    B -- "no" --> F["proc.SetReadDeadline(+100ms)"]
    F --> G["proc.Read(buf)"]
    G -- "timeout (os.IsTimeout)" --> B
    G -- "io.EOF" --> H["break (normal exit)"]
    G -- "other error" --> I["call onPTYError(err)\nproc.Kill()"]
    G -- "n > 0" --> J["copy data\ncall onOutput(data)"]
    J --> B
```

- `PauseRead()` / `ResumeRead()` are public methods on `Terminal` [runner/internal/terminal/terminal_resize.go:64-92]().
- `ResumeRead()` sends a non-blocking signal on `resumeCh` (buffered channel of size 1).
- Reads use a 100ms deadline instead of blocking indefinitely, so the pause check runs periodically even during idle periods.

### PTY Error Handling

If `readOutput` encounters a non-timeout, non-EOF error (e.g., disk full), it:
1. Calls `onPTYError(err)` — set by `pod.Terminal.SetPTYErrorHandler(...)` in `OnCreatePod`.
2. Kills the process to trigger a clean `waitExit` path.
3. The exit handler then picks up the error message stored in `pod.ptyErrorMsg` via `SetPTYError`/`GetPTYError` [runner/internal/runner/pod.go:60-71]() and includes it in the `pod_terminated` event sent to the backend.

Sources: [runner/internal/terminal/terminal_io.go:14-146](), [runner/internal/terminal/terminal_resize.go:64-99](), [runner/internal/runner/pod.go:60-71]()

---

## Message Handler Integration

`RunnerMessageHandler` in [runner/internal/runner/message_handler.go]() bridges incoming gRPC commands to pod and terminal operations. It implements `client.MessageHandler`.

**Message handler dispatch**

```mermaid
flowchart LR
    grpc["gRPC Stream\n(ServerMessage)"] --> mh["RunnerMessageHandler"]
    mh --> ocp["OnCreatePod()\n→ PodBuilder.Build()\n→ Terminal.Start()"]
    mh --> otp["OnTerminatePod()\n→ Terminal.Stop()"]
    mh --> oti["OnTerminalInput()\n→ Terminal.Write()"]
    mh --> otr["OnTerminalResize()\n→ Terminal.Resize()\n→ VirtualTerminal.Resize()"]
    mh --> otrd["OnTerminalRedraw()\n→ Terminal.Redraw()"]
    mh --> olp["OnListPods()\n→ PodStore.All()"]
    mh --> oqs["OnQuerySandboxes()\n→ Runner.GetSandboxStatus()"]
```

Key details:

- **`OnTerminalResize`** [runner/internal/runner/message_handler.go:275-293]() also resizes `pod.VirtualTerminal` if present, and sends a `pty_resized` event back to the backend.
- **`OnListPods`** [runner/internal/runner/message_handler.go:195-212]() reads agent status from the state detector for each pod.
- **`OnListRelayConnections`** [runner/internal/runner/message_handler.go:236-253]() iterates pods and returns relay URL, connection status, and connect time for each.

### Agent State Bridging

After a pod starts, `OnCreatePod` subscribes to `pod.VirtualTerminal` state change events [runner/internal/runner/message_handler.go:125-152](). When the state detector transitions between `StateExecuting`, `StateWaiting`, and `StateNotRunning`, the handler maps these to backend strings (`"executing"`, `"waiting"`, `"idle"`) and calls `conn.SendAgentStatus`. A `sync.Mutex` deduplicates consecutive identical statuses.

Sources: [runner/internal/runner/message_handler.go:255-332](), [runner/internal/runner/message_handler.go:125-152]()

---

## Environment Setup in `New()`

When `terminal.New(opts)` is called [runner/internal/terminal/terminal.go:71-128](), it builds the process environment by:

1. Starting from `os.Environ()` of the runner process.
2. Removing `CLAUDECODE` to prevent nested-session detection.
3. Forcing `TERM=xterm-256color` and `COLORTERM=truecolor`.
4. Applying user-provided `opts.Env` entries last (highest priority).

Default terminal size is 80×24 if `opts.Cols` or `opts.Rows` are zero.

Sources: [runner/internal/terminal/terminal.go:71-128]()

---

## Relationship Between Components

**How Pod, Terminal, and the message handler fit together**

```mermaid
flowchart TD
    backend["Backend\n(gRPC ServerMessage)"] --> handler["RunnerMessageHandler\n(message_handler.go)"]
    handler --> podstore["PodStore\n(InMemoryPodStore)"]
    handler --> podbuilder["PodBuilder\n(pod_builder.go)"]
    podbuilder --> pod["Pod\n(pod.go)"]
    pod --> term["terminal.Terminal\n(terminal.go)"]
    pod --> vt["vt.VirtualTerminal"]
    pod --> agg["aggregator.SmartAggregator"]
    pod --> relay["relay.RelayClient\n(relay/client.go)"]
    pod --> detector["ManagedStateDetector\n(state_detector.go)"]
    term --> ptyproc["ptyProcess interface\n(terminal_pty.go)"]
    ptyproc --> unix["unixPTY\n(terminal_pty_unix.go)\ncreack/pty"]
    ptyproc --> win["windowsPTY\n(terminal_pty_windows.go)\nconpty"]
    term --> readloop["readOutput goroutine\n(terminal_io.go)"]
    term --> waitloop["waitExit goroutine\n(terminal_io.go)"]
    readloop --> agg
    agg --> relay
    agg --> grpcsend["conn.SendTerminalOutput\n(via gRPC)"]
```

Sources: [runner/internal/runner/pod.go](), [runner/internal/terminal/terminal.go](), [runner/internal/terminal/terminal_pty.go](), [runner/internal/runner/message_handler.go]()

---

# Page: Relay Client

# Relay Client

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/troubleshooting/relay-client-stop-timeout.md](docs/troubleshooting/relay-client-stop-timeout.md)
- [runner/internal/relay/client.go](runner/internal/relay/client.go)
- [runner/internal/relay/client_connection.go](runner/internal/relay/client_connection.go)
- [runner/internal/relay/client_loops.go](runner/internal/relay/client_loops.go)
- [runner/internal/relay/client_reconnect.go](runner/internal/relay/client_reconnect.go)
- [runner/internal/relay/client_test.go](runner/internal/relay/client_test.go)
- [runner/internal/relay/interface.go](runner/internal/relay/interface.go)
- [runner/internal/relay/mock_client.go](runner/internal/relay/mock_client.go)
- [runner/internal/runner/message_handler_relay_test.go](runner/internal/runner/message_handler_relay_test.go)

</details>



This page documents the runner-side WebSocket relay client: how it connects to the Relay service, manages message dispatch, handles reconnection, and shuts down cleanly. For the server-side counterpart that manages subscriber sessions, see [Channel and Session Management](#4.1). For how the runner receives the `SubscribeTerminal` command that triggers relay client creation, see [gRPC Client](#3.3).

---

## Purpose

When a browser user opens a terminal, the backend instructs the runner (via gRPC) to connect to the Relay service over WebSocket. The relay client (`runner/internal/relay/`) owns that WebSocket connection for the lifetime of the terminal session. It:

- Forwards terminal output from the PTY to the Relay (and thus to browsers)
- Dispatches inbound input, resize, and image-paste events from browsers to the PTY
- Automatically reconnects with exponential backoff on unexpected disconnection
- Refreshes the JWT token when the relay rejects the connection with a 401/403

---

## Package Layout

| File | Responsibility |
|---|---|
| `client.go` | `Client` struct definition, constants, constructor, handler setters |
| `client_connection.go` | `Connect`, `Start`, `Stop`, `IsConnected` |
| `client_loops.go` | `readLoop`, `writeLoop`, `handleMessage` |
| `client_reconnect.go` | `reconnectLoop` with exponential backoff and token refresh |
| `interface.go` | `RelayClient` interface definition |
| `mock_client.go` | `MockClient` for unit testing |

Sources: [runner/internal/relay/client.go:1-10](), [runner/internal/relay/interface.go:1-37]()

---

## RelayClient Interface

All consumers interact through the `RelayClient` interface defined in [runner/internal/relay/interface.go:9-33](). This allows dependency injection and makes `MockClient` a drop-in replacement in tests.

**RelayClient interface — method groups**

| Group | Methods |
|---|---|
| Lifecycle | `Connect() error`, `Start() bool`, `Stop()`, `IsConnected() bool` |
| Configuration | `GetRelayURL() string`, `GetConnectedAt() int64`, `UpdateToken(string)`, `SetFallbackURL(string)` |
| Handler registration | `SetInputHandler`, `SetResizeHandler`, `SetCloseHandler`, `SetImagePasteHandler`, `SetReconnectHandler`, `SetTokenExpiredHandler` |
| Data transmission | `SendOutput([]byte) error`, `SendSnapshot(*vt.TerminalSnapshot) error` |

Sources: [runner/internal/relay/interface.go:9-33]()

---

## Client Struct

The `Client` struct in [runner/internal/relay/client.go:39-73]() groups its fields into four logical areas:

**Client struct — field groups diagram**

```mermaid
classDiagram
    class Client {
        <<runner/internal/relay/client.go>>
        +relayURL string
        +fallbackURL string
        +podKey string
        +token string
        +conn websocket.Conn
        +connMu sync.RWMutex
        +onInput InputHandler
        +onResize ResizeHandler
        +onClose CloseHandler
        +onImagePaste ImagePasteHandler
        +onReconnect func
        +onTokenExpired func
        +connected atomic.Bool
        +connectedAt atomic.Int64
        +reconnecting atomic.Bool
        +stopped atomic.Bool
        +stopCh chan struct
        +connDoneCh chan struct
        +stopOnce sync.Once
        +sendCh chan bytes
        +wg sync.WaitGroup
        +wgMu sync.Mutex
        +reconnectMu sync.Mutex
    }
```

Sources: [runner/internal/relay/client.go:39-73]()

### Constants

[runner/internal/relay/client.go:13-23]() defines the key tuning constants:

| Constant | Value | Purpose |
|---|---|---|
| `writeWait` | 10 s | Deadline for each WebSocket write |
| `pongWait` | 60 s | Time to wait for a pong before treating connection as dead |
| `pingPeriod` | 54 s | `(pongWait * 9) / 10` — how often to send pings |
| `maxMessageSize` | 4 MB | Read limit, accommodates image-paste payloads |
| `maxReconnectDelay` | 30 s | Cap on exponential backoff |
| `initialBackoff` | 500 ms | Starting delay before first reconnect attempt |

---

## Connection Lifecycle

**Connection lifecycle state diagram**

```mermaid
stateDiagram-v2
    [*] --> "Disconnected": "NewClient()"
    "Disconnected" --> "Connected": "Connect() succeeds"
    "Disconnected" --> "Disconnected": "Connect() fails (fallback tried)"
    "Connected" --> "Running": "Start() — readLoop + writeLoop launched"
    "Running" --> "Reconnecting": "readLoop: unexpected error"
    "Reconnecting" --> "Running": "reconnectLoop: connect OK"
    "Reconnecting" --> "Stopped": "reconnectLoop: max attempts or Stop()"
    "Running" --> "Stopped": "Stop() called"
    "Stopped" --> [*]
```

Sources: [runner/internal/relay/client_connection.go:1-172](), [runner/internal/relay/client_reconnect.go:24-179]()

### `NewClient`

[runner/internal/relay/client.go:77-100]() constructs the client with a buffered `sendCh` of 256 entries and creates a background context with cancel. The `podKey` is embedded in structured log fields for easy filtering.

### `Connect`

[runner/internal/relay/client_connection.go:16-41]() orchestrates connection:

1. Acquires `reconnectMu` to prevent concurrent dials.
2. Calls `connectInternal()` which builds the WebSocket URL, converts `http`/`https` schemes to `ws`/`wss`, appends `/runner/terminal`, sets `?token=<jwt>`, and dials using `gorilla/websocket`.
3. If the primary URL fails and `fallbackURL` is set, the primary URL is permanently replaced with the fallback URL and `connectInternal()` is retried.
4. On success, sets `connected = true` and records `connectedAt` as Unix milliseconds.

The token is passed as a query parameter, not a header, so it never appears in connection logs (the log omits the query string).

### `Start`

[runner/internal/relay/client_connection.go:102-118]() launches `readLoop` and `writeLoop` as goroutines (via `safego.Go`). The `wgMu` lock is held around the `stopped` check and `wg.Add(2)` call — this ensures the check and the increment are atomic with respect to `Stop()`.

### `Stop`

[runner/internal/relay/client_connection.go:121-166]() is idempotent via `sync.Once`:

1. Acquires `wgMu`, sets `stopped = true`, releases `wgMu`. After this point no new `wg.Add()` calls can occur.
2. Sets `connected = false`, closes `stopCh`, calls `cancel()`.
3. Closes the underlying `websocket.Conn` to unblock `readLoop` immediately.
4. Waits on `wg.Wait()` with a 5-second timeout.
5. Nils out `conn`.

---

## Read and Write Loops

**Read/write loop interaction diagram**

```mermaid
sequenceDiagram
    participant "Relay Server" as RS
    participant "readLoop" as RL
    participant "handleMessage" as HM
    participant "writeLoop" as WL
    participant "sendCh" as SC

    loop "every message"
        RS->>RL: "WebSocket BinaryMessage"
        RL->>HM: "handleMessage(data)"
        HM->>HM: "DecodeMessage → dispatch to handler"
    end

    loop "every 54s (pingPeriod)"
        WL->>RS: "PingMessage"
        RS->>RL: "PongMessage (pong handler resets deadline)"
    end

    note over WL,SC: "SendOutput / SendSnapshot enqueue to sendCh"
    WL->>RS: "BinaryMessage from sendCh"

    note over RL: "readLoop exits → closes connDoneCh"
    RL-->>WL: "connDoneCh closed → writeLoop exits"
```

Sources: [runner/internal/relay/client_loops.go:1-128]()

### `readLoop`

[runner/internal/relay/client_loops.go:9-78]() reads messages in a tight loop. On exit (whether clean or error), its `defer` block:

1. Calls `wg.Done()` **first** — before any callbacks — so `Stop()` is not blocked waiting for slow callbacks.
2. Closes `connDoneCh` to signal `writeLoop`.
3. Checks `stopCh`: if closed, calls `onClose` and returns without reconnecting; otherwise starts `reconnectLoop` (guarded by `reconnecting.Swap(true)` to prevent concurrent attempts).

### `writeLoop`

[runner/internal/relay/client_loops.go:80-128]() selects on three channels:

| Channel | Action |
|---|---|
| `stopCh` | Exit immediately |
| `connDoneCh` | Exit (read side is gone) |
| `sendCh` | Write binary message to WebSocket |
| `ticker.C` | Send `PingMessage` |

Each write sets a `writeWait` deadline before the call.

---

## Message Handling

`handleMessage` in [runner/internal/relay/client_loops.go:130-177]() decodes the binary framing and dispatches by message type:

| `MsgType` | Direction | Handler |
|---|---|---|
| `MsgTypeInput` | Relay → Runner | `onInput(payload)` — keystroke data to PTY |
| `MsgTypeResize` | Relay → Runner | `onResize(cols, rows)` — terminal resize |
| `MsgTypePing` | Relay → Runner | `SendPong()` |
| `MsgTypePong` | Relay → Runner | No-op (keepalive acknowledged) |
| `MsgTypeImagePaste` | Relay → Runner | `onImagePaste(mimeType, data)` |
| `MsgTypeControl` | Relay → Runner | Ignored (logged at debug) |

### Image Paste Payload Format

The `MsgTypeImagePaste` payload uses a length-prefixed MIME type:

```
[mime_len: 1 byte][mime: mime_len bytes][image data: remaining bytes]
```

`DecodeImagePaste` extracts both fields. If the payload is too short, the message is silently dropped rather than panicking.

Sources: [runner/internal/relay/client_loops.go:130-177](), [runner/internal/relay/client_test.go:196-224]()

---

## Reconnection Logic

**Exponential backoff reconnect flow**

```mermaid
flowchart TD
    A["readLoop exits unexpectedly"] --> B{"reconnecting.Swap(true)?"}
    B -- "false (already reconnecting)" --> Z["skip"]
    B -- "true (acquired)" --> C["close old conn, wait for writeLoop"]
    C --> D{"stopCh closed?"}
    D -- "yes" --> E["call onClose, return"]
    D -- "no" --> F["wait backoff (initialBackoff=500ms)"]
    F --> G["connectInternal()"]
    G -- "error" --> H{"isHandshakeError AND onTokenExpired set?"}
    H -- "yes, first time" --> I["call onTokenExpired() → get newToken"]
    I --> J["UpdateToken(newToken), retry immediately"]
    J --> G
    H -- "no / already tried" --> K["backoff = min(backoff*2, 30s) + jitter"]
    K --> L{"attempt <= 10?"}
    L -- "yes" --> F
    L -- "no" --> M["call onClose, give up"]
    G -- "success" --> N["wgMu.Lock — check stopped"]
    N -- "stopped" --> O["close new conn, call onClose, return"]
    N -- "not stopped" --> P["connected=true, wg.Add(2), start readLoop+writeLoop"]
    P --> Q["call onReconnect()"]
```

Sources: [runner/internal/relay/client_reconnect.go:24-179]()

### Backoff Parameters

- **Initial**: 500 ms
- **Formula**: `min(backoff * 2, 30s)` then ±20% jitter via `rand.Float64()*0.4 - 0.2`
- **Max attempts**: 10; on exhaustion `onClose` is called and the client gives up

### Token Refresh

When `connectInternal` returns a "bad handshake", "401", or "403" error, `isHandshakeError` [runner/internal/relay/client_reconnect.go:13-21]() returns true. The reconnect loop then calls `onTokenExpired()` once (guarded by `tokenRefreshAttempted`). This callback is set by the message handler to request a new relay token from the backend via gRPC. If a new token is returned, `UpdateToken` is called and the connection is retried immediately without incrementing backoff.

---

## Shutdown Race Condition Fix

A documented race condition between `Stop()` and `reconnectLoop()` was fixed. The root cause and solution are recorded in [docs/troubleshooting/relay-client-stop-timeout.md:1-158]().

**Race condition: before fix**

```mermaid
sequenceDiagram
    participant "Stop()" as S
    participant "reconnectLoop()" as R
    participant "WaitGroup wg" as WG

    S->>WG: "wg.Wait() — begins waiting"
    R->>R: "connectInternal() succeeds"
    R->>WG: "wg.Add(2) — increments after Stop started!"
    R->>R: "launch readLoop + writeLoop"
    S->>S: "waits 5s, times out"
```

**Fix summary**

| Mechanism | Role |
|---|---|
| `stopped atomic.Bool` | Permanent stop flag; set to `true` once by `Stop()` |
| `wgMu sync.Mutex` | Guards `wg.Add()` calls; makes "check stopped → add" atomic |
| `Stop()` acquires `wgMu` before setting `stopped=true` | Guarantees no new `wg.Add()` after this point |
| `Start()` and `reconnectLoop()` acquire `wgMu` before `wg.Add(2)` | Cannot race with `Stop()` |
| `readLoop` defer calls `wg.Done()` first | Unblocks `Stop()` before any slow callbacks run |

Tests covering this fix: `TestStopDuringReconnect`, `TestConcurrentStopAndReconnect`, `TestStartAfterStop`, `TestStopIdempotent` in [runner/internal/relay/client_test.go:447-641]().

---

## Multi-Client (Shared Relay) Behaviour

When a second browser window (or mobile client) opens the same terminal, the backend sends another `SubscribeTerminal` command with a fresh token but the same relay URL. The message handler checks:

1. Is there an existing `RelayClient` on the pod? → Yes
2. Is it connected? → Yes
3. Is the relay URL the same? → Yes

In this case `Stop()` is **not** called. Only `UpdateToken` is called on the existing client. This prevents interrupting ongoing sessions when multiple viewers connect.

The condition for creating a new connection: existing client is `nil`, not connected, or pointing at a different relay URL.

Sources: [runner/internal/runner/message_handler_relay_test.go:37-87](), [runner/internal/runner/message_handler_relay_test.go:252-333]()

---

## MockClient

[runner/internal/relay/mock_client.go:9-196]() provides `MockClient`, a thread-safe implementation of `RelayClient` for unit testing. It records calls in exported fields:

| Field | Tracks |
|---|---|
| `ConnectCalled bool` | Whether `Connect()` was invoked |
| `StartCalled bool` | Whether `Start()` was invoked |
| `StopCalled bool` | Whether `Stop()` was invoked |
| `UpdateTokenCalls []string` | All tokens passed to `UpdateToken` |
| `ConnectError error` | Configurable error to return from `Connect` |

Helper methods `SetConnected`, `SetConnectedAt`, `GetToken`, and `Reset` support test setup and assertion.

Sources: [runner/internal/relay/mock_client.go:9-196]()

---

# Page: MCP Server

# MCP Server

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [backend/internal/api/grpc/runner_adapter_mcp.go](backend/internal/api/grpc/runner_adapter_mcp.go)
- [backend/internal/api/grpc/runner_adapter_mcp_ticket.go](backend/internal/api/grpc/runner_adapter_mcp_ticket.go)
- [backend/internal/service/ticket/ticket_query.go](backend/internal/service/ticket/ticket_query.go)
- [backend/internal/service/ticket/ticket_query_test.go](backend/internal/service/ticket/ticket_query_test.go)
- [docs/images/architecture.svg](docs/images/architecture.svg)
- [runner/internal/mcp/grpc_client.go](runner/internal/mcp/grpc_client.go)
- [runner/internal/mcp/http_server.go](runner/internal/mcp/http_server.go)
- [runner/internal/mcp/http_tools_format_integration_test.go](runner/internal/mcp/http_tools_format_integration_test.go)
- [runner/internal/mcp/http_tools_ticket.go](runner/internal/mcp/http_tools_ticket.go)
- [runner/internal/mcp/tools/types_client.go](runner/internal/mcp/tools/types_client.go)
- [runner/internal/mcp/tools/types_entity.go](runner/internal/mcp/tools/types_entity.go)

</details>



This page covers the runner-side MCP (Model Context Protocol) HTTP server: how it is structured, how pods are registered, how AI agents discover and call tools, and how each tool category invokes the backend. The document covers code in `runner/internal/mcp/`.

For the backend's counterpart that receives and processes these tool calls over gRPC, see [MCP and Mesh Service (2.4)](#2.4). For how bindings and channels are managed at the backend domain level, see [MCP and Mesh Service (2.4)](#2.4). For the gRPC connection over which tool calls travel, see [gRPC Client (3.3)](#3.3).

---

## Overview

When the runner creates an AgentPod it starts a local HTTP server (`HTTPServer`) that speaks the Model Context Protocol. AI agents such as Claude Code connect to this server to access collaboration tools: observing other terminals, managing pod bindings, sending channel messages, searching tickets, and spawning new pods. Tool invocations arriving at the HTTP server are forwarded as `McpRequest` messages over the existing gRPC bidirectional stream to the backend, which executes the business logic and returns a result.

The entire server is scoped to `127.0.0.1` and is therefore only reachable by processes running on the same machine as the runner.

---

## HTTP Server

`HTTPServer` in [runner/internal/mcp/http_server.go:36-46]() is the central struct. It owns:

| Field | Type | Purpose |
|---|---|---|
| `rpcClient` | `*client.RPCClient` | Sends `McpRequest` messages to the backend over gRPC |
| `port` | `int` | Localhost port (set at construction time) |
| `pods` | `map[string]*PodInfo` | Registry of active pods indexed by pod key |
| `tools` | `[]*MCPTool` | Registered tool definitions (populated once at startup) |
| `statusProvider` | `PodStatusProvider` | Optional interface to query local pod agent status |
| `terminalProvider` | `LocalTerminalProvider` | Optional interface for direct local terminal access |

The server listens on three routes:

| Route | Handler | Purpose |
|---|---|---|
| `POST /mcp` | `handleMCP` | Main JSON-RPC 2.0 dispatch endpoint |
| `GET /health` | `handleHealth` | Health probe |
| `GET /pods` | `handlePods` | Debug – list registered pods |

`NewHTTPServer` in [runner/internal/mcp/http_server.go:72-87]() creates the struct and calls `registerTools()` immediately. Tools are registered once and never change at runtime.

`Start()` in [runner/internal/mcp/http_server.go:90-118]() wraps `http.Server.ListenAndServe` in a `safego.Go` goroutine. `Stop()` issues a graceful shutdown with a 5-second deadline.

Sources: [runner/internal/mcp/http_server.go:36-137]()

---

## Pod Registration

Pods must be registered before the AI agent running inside them can call any tool. The lifecycle is:

**Registration** – `RegisterPod()` in [runner/internal/mcp/http_server.go:140-155]() stores a `PodInfo` entry and creates a `GRPCCollaborationClient` bound to the pod's key. All subsequent tool calls for that pod use this client.

**Unregistration** – `UnregisterPod()` in [runner/internal/mcp/http_server.go:158-163]() removes the entry when a pod terminates.

`PodInfo` [runner/internal/mcp/http_server.go:49-57]() holds:

| Field | Description |
|---|---|
| `PodKey` | Unique identifier for the pod |
| `OrgSlug` | Organization slug for authorization context |
| `TicketID` / `ProjectID` | Optional associations |
| `AgentType` | String identifier of the AI agent |
| `Client` | `CollaborationClient` – the gRPC-backed tool implementation |

**Tool request authentication** – when `handleMCP` receives a request, it reads the `X-Pod-Key` HTTP header and looks up the corresponding `PodInfo`. Requests referencing an unregistered pod are rejected immediately.

Sources: [runner/internal/mcp/http_server.go:49-57](), [runner/internal/mcp/http_server.go:140-173]()

---

## MCP Configuration for Claude Code

`GenerateMCPConfig()` in [runner/internal/mcp/http_server.go:204-219]() produces the JSON configuration block that the runner injects into the agent's environment. The configuration instructs Claude Code to use `curl` as a stdio transport:

```json
{
  "mcpServers": {
    "agentsmesh-collaboration": {
      "command": "curl",
      "args": [
        "-X", "POST",
        "-H", "Content-Type: application/json",
        "-H", "X-Pod-Key: <pod-key>",
        "http://localhost:<port>/mcp",
        "-d", "@-"
      ]
    }
  }
}
```

Claude Code pipes JSON-RPC 2.0 messages through `stdin` into `curl`, which forwards them to the local HTTP server. The `X-Pod-Key` header is baked into the config, so the server knows which pod is calling.

Sources: [runner/internal/mcp/http_server.go:204-219]()

---

## Request Flow

**Title: MCP Tool Call – from AI Agent to Backend and Back**

```mermaid
sequenceDiagram
    participant Agent as "AI Agent (Claude Code)"
    participant HTTP as "HTTPServer.handleMCP()"
    participant Tool as "MCPTool.Handler"
    participant GRPC as "GRPCCollaborationClient.call()"
    participant RPC as "RPCClient.Call()"
    participant BE as "GRPCRunnerAdapter.handleMcpRequest()"

    Agent->>HTTP: "POST /mcp  X-Pod-Key: <key>  JSON-RPC 2.0 tools/call"
    HTTP->>HTTP: "lookup PodInfo by X-Pod-Key"
    HTTP->>Tool: "dispatch by tool name"
    Tool->>GRPC: "method call e.g. SearchTickets()"
    GRPC->>RPC: "Call(ctx, podKey, method, params)"
    RPC->>BE: "McpRequest{method, payload} over gRPC stream"
    BE->>BE: "authenticatePod() + dispatchMcpMethod()"
    BE-->>RPC: "McpResponse{payload}"
    RPC-->>GRPC: "[]byte"
    GRPC-->>Tool: "unmarshaled struct"
    Tool-->>HTTP: "formatted text"
    HTTP-->>Agent: "JSON-RPC result {content:[{type:text}]}"
```

Sources: [runner/internal/mcp/http_server.go:1-220](), [runner/internal/mcp/grpc_client.go:35-62](), [backend/internal/api/grpc/runner_adapter_mcp.go:17-44]()

---

## Tool Architecture

**Title: HTTPServer, CollaborationClient, and Tool Interfaces**

```mermaid
graph TD
    HS["HTTPServer\n(http_server.go)"]
    PI["PodInfo"]
    MT["MCPTool\n{Name, Description, InputSchema, Handler}"]
    CC["CollaborationClient\n(tools/types_client.go)"]
    GCC["GRPCCollaborationClient\n(grpc_client.go)"]
    TC["TerminalClient"]
    DC["DiscoveryClient"]
    BC["BindingClient"]
    CHC["ChannelClient"]
    TKC["TicketClient"]
    PC["PodClient"]
    PSP["PodStatusProvider"]
    LTP["LocalTerminalProvider"]

    HS --> |"holds []"| MT
    HS --> |"holds map[podKey]"| PI
    PI --> |"Client field"| GCC
    GCC --> |"implements"| CC
    CC --> |"embeds"| TC
    CC --> |"embeds"| DC
    CC --> |"embeds"| BC
    CC --> |"embeds"| CHC
    CC --> |"embeds"| TKC
    CC --> |"embeds"| PC
    HS --> |"SetStatusProvider()"| PSP
    HS --> |"SetTerminalProvider()"| LTP
```

Sources: [runner/internal/mcp/http_server.go:36-68](), [runner/internal/mcp/tools/types_client.go:1-68](), [runner/internal/mcp/grpc_client.go:16-27]()

---

## Registered Tools

All tools are registered in `registerTools()` in [runner/internal/mcp/http_server.go:222-262](). Each `MCPTool` carries a JSON Schema (`InputSchema`) and a `MCPToolHandler` closure.

### Terminal Tools

| Tool Name | Method | Description |
|---|---|---|
| `observe_terminal` | `createObserveTerminalTool` | Read scrollback and screen from another pod's PTY |
| `send_terminal_text` | `createSendTerminalTextTool` | Send text input to another pod's terminal |
| `send_terminal_key` | `createSendTerminalKeyTool` | Send special key sequences (e.g. Enter, Ctrl-C) |
| `get_pod_status` | `createGetPodStatusTool` | Query agent status (executing/waiting/idle) from `PodStatusProvider` |

`observe_terminal` accepts `pod_key`, `lines`, `raw`, and `include_screen` parameters. `send_terminal_key` accepts a `keys` array of named key identifiers.

`get_pod_status` is special: it does not go through the gRPC stream. If the target pod key matches a pod running on the same runner, it queries `statusProvider.GetPodStatus()` directly. For remote pods it falls back to the backend call.

### Discovery Tools

| Tool Name | Description | Returns |
|---|---|---|
| `list_available_pods` | All pods in the organization available for collaboration | Markdown table of pod keys, statuses, creators |
| `list_runners` | Runners and their available agent types | Text summary with pod counts and agent list |
| `list_repositories` | Git repositories configured in the organization | Markdown table of IDs, names, providers |

### Binding Tools

Pod bindings grant one pod permission to interact with another. All binding operations require a prior binding relationship.

| Tool Name | Required Args | Description |
|---|---|---|
| `bind_pod` | `target_pod`, `scopes` | Request a binding from this pod to another |
| `accept_binding` | `binding_id` | Accept an incoming binding request |
| `reject_binding` | `binding_id`, `reason` | Reject an incoming binding request |
| `unbind_pod` | `target_pod` | Remove an existing binding |
| `get_bindings` | `status` (optional) | List bindings for this pod |
| `get_bound_pods` | — | List pod keys that are currently bound to this pod |

`scopes` is an array of `BindingScope` strings (e.g. `terminal:read`).

Sources: [runner/internal/mcp/http_server.go:222-262](), [runner/internal/mcp/tools/types_client.go:23-30](), [runner/internal/mcp/tools/types_entity.go:4-13]()

### Channel Tools

Channels are named communication spaces that can be associated with a repository or ticket.

| Tool Name | Required Args | Description |
|---|---|---|
| `search_channels` | — | Search by name, repository, ticket, or archived state |
| `create_channel` | `name` | Create a new channel |
| `get_channel` | `channel_id` | Fetch channel metadata |
| `send_channel_message` | `channel_id`, `content` | Post a message; supports `mentions` and `reply_to` |
| `get_channel_messages` | `channel_id` | Retrieve messages with optional time filters and mention filter |
| `get_channel_document` | `channel_id` | Read the channel's shared document |
| `update_channel_document` | `channel_id`, `document` | Replace the shared document |

Sources: [runner/internal/mcp/http_server.go:244-251](), [runner/internal/mcp/tools/types_entity.go:72-96]()

### Ticket Tools

Ticket tool definitions are in [runner/internal/mcp/http_tools_ticket.go]().

| Tool Name | Required Args | Description |
|---|---|---|
| `search_tickets` | — | Filter by status, priority, assignee, parent ticket, query string |
| `get_ticket` | `ticket_slug` | Retrieve a single ticket; supports `content_offset`/`content_limit` for paginated reading of long descriptions |
| `create_ticket` | `title` | Create a ticket; optional repository, content, priority, parent slug |
| `update_ticket` | `ticket_slug` | Update title, content, status, or priority |
| `post_comment` | `ticket_slug`, `content` | Add a comment; optional `parent_id` for threading |

`ticket_slug` is the human-readable identifier format (e.g. `AM-123`). The backend resolves slugs to internal IDs — see `GetTicketByIDOrSlug` in [backend/internal/service/ticket/ticket_query.go:43-64]().

Ticket content (stored as BlockNote JSON on the backend) is converted to plain text by the backend before being returned. The `content_offset` and `content_limit` parameters allow line-range pagination for large ticket bodies.

Sources: [runner/internal/mcp/http_tools_ticket.go:1-277](), [backend/internal/api/grpc/runner_adapter_mcp_ticket.go:35-87]()

### Pod Tools

| Tool Name | Required Args | Description |
|---|---|---|
| `create_pod` | `runner_id`, `agent_type_id` | Spawn a new AgentPod; accepts repository, ticket, branch, permission mode, credential profile, and config overrides |

`create_pod` delegates to `PodOrchestrator.CreatePod()` on the backend. On success it returns the new `pod_key` and initial `status`. See [backend/internal/api/grpc/runner_adapter_mcp_ticket.go:312-374]() for the full parameter set.

Sources: [runner/internal/mcp/http_server.go:259-261](), [backend/internal/api/grpc/runner_adapter_mcp_ticket.go:312-400]()

---

## GRPCCollaborationClient

`GRPCCollaborationClient` in [runner/internal/mcp/grpc_client.go:16-27]() is the concrete implementation of `CollaborationClient`. It holds a reference to `*client.RPCClient` and the current `podKey`.

Every method calls the private `call()` helper in [runner/internal/mcp/grpc_client.go:35-62](), which:

1. Marshals the parameters to JSON.
2. Invokes `RPCClient.Call(ctx, podKey, method, params)` — this sends a `McpRequest` protobuf message over the gRPC bidirectional stream and blocks until a `McpResponse` is received.
3. Unmarshals the response bytes into the expected result type.

The gRPC stream itself is managed by the runner's `RPCClient` (see [gRPC Client (3.3)](#3.3)). `GRPCCollaborationClient` does not manage connectivity; it only serializes domain calls into wire messages.

Sources: [runner/internal/mcp/grpc_client.go:1-491]()

---

## Backend-Side Dispatch

When a `McpRequest` arrives at the backend over the gRPC stream, `GRPCRunnerAdapter.handleMcpRequest()` in [backend/internal/api/grpc/runner_adapter_mcp.go:17-44]() handles it:

1. **Authentication** – `authenticatePod()` [backend/internal/api/grpc/runner_adapter_mcp.go:62-90]() verifies the pod key exists and belongs to the runner's organization. It constructs a `TenantContext` with the pod's creator as the acting user.
2. **Dispatch** – `dispatchMcpMethod()` [backend/internal/api/grpc/runner_adapter_mcp.go:93-160]() routes by method string to the appropriate handler (e.g. `mcpSearchTickets`, `mcpCreatePod`).
3. **Response** – `sendMcpResponse()` serializes the result and writes a `McpResponse` message back through the gRPC connection.

**Title: Backend MCP Dispatch – Method to Handler Mapping**

```mermaid
graph LR
    REQ["McpRequest\n{method, podKey, payload}"]
    AUTH["authenticatePod()\n→ TenantContext"]
    DISP["dispatchMcpMethod()"]

    CH["Channel handlers\nsearch_channels\ncreate_channel\nget_channel\nsend_message\nget_messages\nget_document\nupdate_document"]
    BN["Binding handlers\nrequest_binding\naccept_binding\nreject_binding\nunbind_pod\nget_bindings\nget_bound_pods"]
    TK["Ticket handlers\nsearch_tickets\nget_ticket\ncreate_ticket\nupdate_ticket\npost_comment"]
    TR["Terminal handlers\nobserve_terminal\nsend_terminal_text\nsend_terminal_key"]
    DS["Discovery handlers\nlist_available_pods\nlist_runners\nlist_repositories"]
    PD["Pod handler\ncreate_pod\n→ PodOrchestrator.CreatePod()"]

    REQ --> AUTH
    AUTH --> DISP
    DISP --> CH
    DISP --> BN
    DISP --> TK
    DISP --> TR
    DISP --> DS
    DISP --> PD
```

Sources: [backend/internal/api/grpc/runner_adapter_mcp.go:17-226](), [backend/internal/api/grpc/runner_adapter_mcp_ticket.go:92-400]()

---

## Local Providers

Two optional interfaces allow the MCP server to bypass the backend gRPC round-trip when interacting with pods on the same runner.

### PodStatusProvider

Defined in [runner/internal/mcp/http_server.go:17-21]():

```
GetPodStatus(podKey string) (agentStatus string, podStatus string, shellPid int, found bool)
```

Set via `SetStatusProvider()`. Used by the `get_pod_status` tool to report whether the agent is currently `executing`, `waiting`, or `idle` without incurring a network call.

### LocalTerminalProvider

Defined in [runner/internal/mcp/http_server.go:24-33]():

```
GetTerminalOutput(podKey string, lines int) (string, error)
SendTerminalText(podKey string, text string) error
SendTerminalKey(podKey string, keys []string) error
```

Set via `SetTerminalProvider()`. When set, an AutopilotController can interact with co-located pods directly through in-process function calls rather than through the backend's terminal relay path.

Sources: [runner/internal/mcp/http_server.go:17-33](), [runner/internal/mcp/http_server.go:176-189]()

---

## Tool Response Format

Tool handlers return their results as human-readable text rather than raw JSON. The MCP response wraps the text in a `content` array of `{type: "text", text: "..."}` blocks (standard MCP tool result format). This is intentional: AI models consume the text directly, so Markdown tables and key-value summaries are more token-efficient than JSON structures.

Examples from integration tests in [runner/internal/mcp/http_tools_format_integration_test.go]():

| Tool | Format |
|---|---|
| `list_available_pods` | Markdown table: Pod Key, Status, Creator, Ticket |
| `list_runners` | Multi-line text: Runner #N, Node, Status, Pods: X/Y, agent list |
| `get_ticket` | Key-value: `Ticket: AM-123 - Title`, `Status: in_progress \| Priority: high` |
| `get_channel_messages` | Prefixed lines: `[timestamp] pod-key: content` |
| `get_bound_pods` | Comma-separated: `Bound pods: pod-x, pod-y` |
| `send_terminal_text` | Plain: `Text sent successfully` |

Sources: [runner/internal/mcp/http_tools_format_integration_test.go:240-492]()

---

# Page: Workspace and Git Management

# Workspace and Git Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitlab-ci.yml](.gitlab-ci.yml)
- [ci/backend.Dockerfile](ci/backend.Dockerfile)
- [ci/relay.Dockerfile](ci/relay.Dockerfile)
- [ci/runner.Dockerfile](ci/runner.Dockerfile)
- [ci/web-admin.Dockerfile](ci/web-admin.Dockerfile)
- [ci/web.Dockerfile](ci/web.Dockerfile)
- [runner/internal/workspace/repo_auth.go](runner/internal/workspace/repo_auth.go)
- [runner/internal/workspace/workspace.go](runner/internal/workspace/workspace.go)
- [runner/internal/workspace/workspace_utils.go](runner/internal/workspace/workspace_utils.go)
- [web/src/lib/terminalScheduler.ts](web/src/lib/terminalScheduler.ts)
- [web/vitest.config.ts](web/vitest.config.ts)

</details>



This page covers the workspace management subsystem in the Runner, located in `runner/internal/workspace/`. It describes how the runner clones repositories as bare Git repos, creates worktrees for individual pods, handles authentication (token and SSH), probes repository access, and provides utility functions for workspace directory management.

For how workspaces are referenced from the pod and terminal abstraction layer, see [Pod and Terminal Management](#3.4). For how MCP tools expose workspace operations to AI agents, see [MCP Server](#3.6).

---

## Overview

Each pod that works on a repository needs an isolated checkout. The workspace package implements this using Git's **bare repository + worktree** model:

1. A bare clone of the upstream repository is maintained as a shared cache.
2. Per-pod working directories are created as Git worktrees from that bare clone.
3. Authentication credentials (HTTPS token or SSH key) are applied at clone/fetch time without storing them permanently in the repository configuration.

**Directory layout on disk:**

```
{workspace_root}/
  repos/
    {repo-name}/          ← bare clone (shared cache)
      HEAD
      config
      refs/
      ...
  sandboxes/
    {podKey}/
      worktree/           ← git worktree checkout for this pod
  temp/
    {podKey}/             ← ephemeral working space (no git)
```

Sources: [runner/internal/workspace/workspace.go:1-70](), [runner/internal/workspace/workspace_utils.go:74-113]()

---

## Core Types

**`Manager`** is the central struct for the workspace subsystem.

| Field | Type | Purpose |
|---|---|---|
| `root` | `string` | Absolute path of the workspace root directory |
| `gitConfigPath` | `string` | Optional path to a supplemental git config file applied to each worktree |
| `mu` | `sync.Mutex` | Guards directory listing operations |

**`WorktreeOptions`** carries per-operation authentication and URL parameters.

| Field | Type | Purpose |
|---|---|---|
| `GitToken` | `string` | Personal access token or OAuth token for HTTPS authentication |
| `SSHKeyPath` | `string` | Filesystem path to the SSH private key |
| `HttpCloneURL` | `string` | HTTPS remote URL |
| `SshCloneURL` | `string` | SSH remote URL (e.g., `git@github.com:org/repo.git`) |

`WorktreeOption` is the functional-options type. The available constructors are `WithGitToken`, `WithSSHKeyPath`, `WithHttpCloneURL`, and `WithSshCloneURL`.

Sources: [runner/internal/workspace/workspace.go:12-70]()

---

## Module Structure

**Workspace package: `runner/internal/workspace`**

```mermaid
graph TD
    workspace_go["workspace.go\nManager · WorktreeOptions\nNewManager"]
    repo_auth_go["repo_auth.go\nensureRepository\nensureRepositoryWithAuth\ncloneBareRepository\nprobeRepositoryAccess\napplyGitConfig"]
    workspace_utils_go["workspace_utils.go\nprepareAuthURL\nsetGitAuthEnv\nsetProbeEnv\nTempWorkspace\nListWorktrees\nextractRepoName"]

    workspace_go -->|"used by"| repo_auth_go
    workspace_go -->|"used by"| workspace_utils_go
    repo_auth_go -->|"calls"| workspace_utils_go
```

Sources: [runner/internal/workspace/workspace.go:1-70](), [runner/internal/workspace/repo_auth.go:1-221](), [runner/internal/workspace/workspace_utils.go:1-137]()

---

## Repository Lifecycle

### `ensureRepository` and `ensureRepositoryWithAuth`

`ensureRepository` is the unauthenticated entry point; it delegates to `ensureRepositoryWithAuth` with `nil` options.

`ensureRepositoryWithAuth` determines whether a bare repository already exists at the given path by checking for a `HEAD` file directly inside the directory (the bare-repo marker). Its logic follows three branches:

```mermaid
flowchart TD
    A["ensureRepositoryWithAuth(ctx, repoURL, path, opts)"] --> B{"HEAD file\nexists at path?"}
    B -- "Yes" --> C["Update remote URL\ngit remote set-url origin"]
    C --> D["git fetch --all"]
    D --> E{"fetch\nsucceeded?"}
    E -- "Yes" --> Z["return nil"]
    E -- "No" --> F["os.RemoveAll(path)"]
    F --> G["cloneBareRepository"]
    B -- "No" --> H{"path exists\nas directory?"}
    H -- "Yes (invalid)" --> I["os.RemoveAll(path)"]
    I --> G
    H -- "No" --> G
    G --> Z
```

Sources: [runner/internal/workspace/repo_auth.go:16-60]()

### `cloneBareRepository`

This function performs the actual `git clone --bare` and then configures the repository for worktree use.

Steps:
1. Create the parent directory with `os.MkdirAll`.
2. Call `prepareAuthURL` to embed the token into the HTTPS URL if applicable.
3. Run `git clone --bare <url> <path>`.
4. On failure, remove any partial clone artifacts with `os.RemoveAll`.
5. Set the fetch refspec: `git config remote.origin.fetch +refs/heads/*:refs/remotes/origin/*`  
   This allows worktrees to reference branches as `origin/<branch>`.
6. Run `git fetch --all` to populate the `origin/*` refs.

Sources: [runner/internal/workspace/repo_auth.go:63-97]()

---

## Authentication

### Token-based HTTPS

`prepareAuthURL` embeds the token into the HTTPS URL using the `x-access-token` username convention:

```
https://x-access-token:<token>@host/path
```

This format is accepted by GitHub, GitLab, Azure DevOps, and Bitbucket without any platform-specific logic.

Sources: [runner/internal/workspace/workspace_utils.go:12-30]()

### SSH Key

`setGitAuthEnv` constructs a `GIT_SSH_COMMAND` environment variable that points to the provided key file:

```
GIT_SSH_COMMAND=ssh -i <keypath> -o StrictHostKeyChecking=no -o BatchMode=yes
```

`BatchMode=yes` ensures SSH never prompts for a passphrase; the runner is a daemon and cannot accept interactive input. `StrictHostKeyChecking=no` avoids blocking on unknown hosts.

### Probe-specific environment

`setProbeEnv` is a stricter variant of `setGitAuthEnv` used during access probing. Even when no `SSHKeyPath` is provided, it injects:

```
GIT_SSH_COMMAND=ssh -o StrictHostKeyChecking=no -o BatchMode=yes -o ConnectTimeout=30
```

The `ConnectTimeout=30` is added to prevent the probe from blocking indefinitely.

Both `setGitAuthEnv` and `setProbeEnv` always append `GIT_TERMINAL_PROMPT=0` and `GIT_ASKPASS=` to suppress any credential helper prompts.

Sources: [runner/internal/workspace/workspace_utils.go:32-71]()

---

## Repository Access Probing

`probeRepositoryAccess` is called before committing to a clone to verify that at least one access method actually works. It runs `git ls-remote --exit-code <url> HEAD` with a 60-second timeout per candidate.

**Candidate URL selection logic:**

```mermaid
flowchart TD
    A["probeRepositoryAccess(ctx, httpURL, sshURL, opts)"] --> B{"GitToken set\n+ httpURL available?"}
    B -- "Yes" --> C["Append: HTTP+token candidate"]
    B -- "No" --> D
    C --> D{"SSHKeyPath set\n+ sshURL available?"}
    D -- "Yes" --> E["Append: SSH+key candidate"]
    D -- "No" --> F
    E --> F{"Any candidates\nadded?"}
    F -- "No" --> G["Fall back: try sshURL then httpURL\nwith local config only"]
    F -- "Yes" --> H["Probe each candidate\nin order"]
    G --> H
    H --> I{"git ls-remote\nsucceeded?"}
    I -- "Yes" --> J["Return accessible URL"]
    I -- "No, more candidates" --> H
    I -- "No, none left" --> K["Return error with all failure details"]
```

The fallback path (no credential-matched candidates) handles `runner_local` mode where the runner relies on the user's local SSH agent or git credential helper.

Sources: [runner/internal/workspace/repo_auth.go:99-176]()

---

## Custom Git Configuration

`applyGitConfig` applies a supplemental git configuration file to a worktree. This is used to inject organization-specific settings (e.g., user name/email, signing keys) without modifying the shared bare repository.

Steps:
1. Read the file at `m.gitConfigPath`.
2. Run `git rev-parse --git-dir` inside the worktree to locate the actual `.git` directory (in a worktree, `.git` is a file, not a directory; this command resolves the real path).
3. Write the contents to `<gitdir>/config.local`.
4. Set `include.path = config.local` in the worktree's local config via `git config --local`.

Sources: [runner/internal/workspace/repo_auth.go:178-221]()

---

## Utility Functions

| Function | Location | Description |
|---|---|---|
| `TempWorkspace(podKey)` | `workspace_utils.go:74` | Returns `{root}/temp/{podKey}`, creating it with `os.MkdirAll` |
| `GetWorkspaceRoot()` | `workspace_utils.go:81` | Returns the configured `root` string |
| `ListWorktrees()` | `workspace_utils.go:86` | Scans `sandboxes/*/worktree` and returns paths that exist on disk |
| `extractRepoName(repoURL)` | `workspace_utils.go:116` | Normalizes SSH and HTTPS URLs to a `owner-repo` string for directory naming |

`ListWorktrees` acquires the `Manager` mutex before scanning to prevent races with concurrent worktree creation or deletion. It returns `nil` (not an error) if the `sandboxes/` directory does not yet exist.

`extractRepoName` handles both SSH (`git@github.com:user/repo.git`) and HTTPS (`https://github.com/user/repo.git`) URL formats, stripping the `.git` suffix and joining the owner and repo name with a hyphen.

Sources: [runner/internal/workspace/workspace_utils.go:73-137]()

---

## Data Flow: Pod Workspace Setup

The following diagram traces a complete workspace setup sequence, from receiving a pod command to having a ready worktree, showing which functions are called at each step.

```mermaid
sequenceDiagram
    participant "Pod Handler" as pod
    participant "Manager" as mgr
    participant "probeRepositoryAccess" as probe
    participant "ensureRepositoryWithAuth" as ensure
    participant "cloneBareRepository" as clone
    participant "applyGitConfig" as applyconf
    participant "git (subprocess)" as git

    pod->>mgr: "WorktreeOptions{GitToken, SSHKeyPath, HttpCloneURL, SshCloneURL}"
    mgr->>probe: "probe(ctx, httpURL, sshURL, opts)"
    probe->>git: "git ls-remote --exit-code <url> HEAD"
    git-->>probe: "success / failure"
    probe-->>mgr: "accessible URL"
    mgr->>ensure: "ensureRepositoryWithAuth(ctx, url, bareRepoPath, opts)"
    ensure->>git: "check HEAD file exists"
    alt "bare repo present"
        ensure->>git: "git remote set-url origin <authURL>"
        ensure->>git: "git fetch --all"
    else "no bare repo"
        ensure->>clone: "cloneBareRepository(ctx, url, bareRepoPath, opts)"
        clone->>git: "git clone --bare <authURL> <path>"
        clone->>git: "git config remote.origin.fetch +refs/heads/*:refs/remotes/origin/*"
        clone->>git: "git fetch --all"
    end
    mgr->>git: "git worktree add <worktreePath> origin/<branch>"
    mgr->>applyconf: "applyGitConfig(ctx, worktreePath)"
    applyconf->>git: "git rev-parse --git-dir"
    applyconf->>git: "git config --local include.path config.local"
```

Sources: [runner/internal/workspace/repo_auth.go:16-221](), [runner/internal/workspace/workspace_utils.go:32-71]()

---

## `NewManager` Initialization

`NewManager(root, gitConfigPath string)` creates the workspace root directory with `os.MkdirAll` if it does not exist and returns a `*Manager`. It logs the root path via the runner's structured logger (`logger.Runner()`).

The `gitConfigPath` argument may be an empty string, in which case `applyGitConfig` is a no-op (guarded by the `m.gitConfigPath == ""` early return at [runner/internal/workspace/repo_auth.go:183]()).

Sources: [runner/internal/workspace/workspace.go:58-70]()

---

# Page: Auto-Update

# Auto-Update

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/release.yml](.github/workflows/release.yml)
- [backend/internal/service/runner/version_checker.go](backend/internal/service/runner/version_checker.go)
- [backend/internal/service/runner/version_checker_test.go](backend/internal/service/runner/version_checker_test.go)
- [docs/rfc/RFC-003-runner-release-pipeline.md](docs/rfc/RFC-003-runner-release-pipeline.md)
- [runner/build/scripts/sign-darwin.sh](runner/build/scripts/sign-darwin.sh)
- [runner/internal/updater/updater.go](runner/internal/updater/updater.go)
- [runner/internal/updater/updater_test.go](runner/internal/updater/updater_test.go)

</details>



This page covers the runner's self-update mechanism and the backend service that tracks the latest available version. The runner updater (`runner/internal/updater`) handles checking, downloading, applying, and rolling back binary updates. The backend `VersionChecker` (`backend/internal/service/runner`) independently polls GitHub Releases and caches the result in Redis for use by the REST API.

For how the runner is built and released as a binary artifact, see the Release Process page ([8.2](#8.2)). For runner CLI commands including the `update` subcommand, see CLI Reference ([3.2](#3.2)).

---

## System Overview

The auto-update system has two independent components that both talk to the GitHub Releases API for `AgentsMesh/AgentsMesh`:

**Auto-Update Architecture**

```mermaid
flowchart TD
    GH["GitHub Releases API\n(AgentsMesh/AgentsMesh)"]

    subgraph "Runner Process"
        U["Updater\nupdater.go"]
        RD["GitHubReleaseDetector\n(ReleaseDetector interface)"]
        EXE["Current Executable\n(on disk)"]
        BAK["Backup File\n(.bak)"]
        U -- "CheckForUpdate / Download" --> RD
        RD -- "HTTP GET latest release" --> GH
        U -- "Apply (atomicReplace)" --> EXE
        U -- "CreateBackup / Rollback" --> BAK
    end

    subgraph "Backend Process"
        VC["VersionChecker\nversion_checker.go"]
        RC["Redis Cache\nrunner:latest_version"]
        API["REST API\nGET /runner/version"]
        VC -- "checkGitHubRelease (1h interval)" --> GH
        VC -- "Set/Get (1h TTL)" --> RC
        API -- "GetLatestVersion" --> RC
    end
```

Sources: [runner/internal/updater/updater.go:1-50](), [backend/internal/service/runner/version_checker.go:1-60]()

---

## Runner-Side: `updater` Package

### Key Types

| Type | File | Role |
|---|---|---|
| `Updater` | `updater.go` | Entry point for all update operations |
| `UpdateInfo` | `updater.go` | Describes an available update |
| `ReleaseDetector` | (interface) | Abstracts GitHub release discovery and download |
| `ReleaseInfo` | (interface impl) | Payload returned by `ReleaseDetector` |

**`UpdateInfo`** fields [runner/internal/updater/updater.go:24-32]():

| Field | Type | Description |
|---|---|---|
| `CurrentVersion` | `string` | Normalized version of the running binary |
| `LatestVersion` | `string` | Version string from GitHub release tag |
| `ReleaseNotes` | `string` | Release body text |
| `PublishedAt` | `time.Time` | GitHub release publication timestamp |
| `HasUpdate` | `bool` | `true` if `LatestVersion > CurrentVersion` |
| `AssetURL` | `string` | Direct download URL for the matching archive |
| `AssetName` | `string` | Archive filename (e.g., `agentsmesh-runner_1.2.0_linux_amd64.tar.gz`) |

### `Updater` Construction

`New` in [runner/internal/updater/updater.go:67-79]() accepts a version string and variadic `Option` functions:

| Option | Effect |
|---|---|
| `WithPrerelease(bool)` | Allow or block prerelease version updates |
| `WithReleaseDetector(ReleaseDetector)` | Inject a custom detector (used in tests) |
| `WithExecPathFunc(func() (string, error))` | Override executable path resolution (used in tests) |

Version normalization is done immediately on construction via the private `normalizeVersion` function [runner/internal/updater/updater.go:82-91](): empty strings and `"dev"` become `"v0.0.0-dev"`, and missing `v` prefixes are added.

### Update Operation Flow

**Runner Update Sequence**

```mermaid
sequenceDiagram
    participant C as "Caller (CLI)"
    participant U as "Updater"
    participant D as "ReleaseDetector"
    participant GH as "GitHub API"
    participant FS as "Filesystem"

    C->>U: "CheckForUpdate(ctx)"
    U->>D: "DetectLatest(ctx)"
    D->>GH: "GET /repos/AgentsMesh/AgentsMesh/releases/latest"
    GH-->>D: "ReleaseInfo{Version, AssetURL, ...}"
    D-->>U: "ReleaseInfo, found=true"
    U-->>C: "UpdateInfo{HasUpdate: true, LatestVersion: ...}"

    C->>U: "Download(ctx, version, progress)"
    U->>D: "DetectVersion(ctx, version)"
    D->>GH: "find release by tag"
    GH-->>D: "ReleaseInfo"
    U->>D: "DownloadTo(ctx, release, tmpPath)"
    D->>FS: "write to /tmp/runner-update-*"
    FS-->>U: "tmpPath"
    U-->>C: "tmpPath"

    C->>U: "Apply(tmpPath)"
    U->>FS: "atomicReplace(tmpPath, execPath)"
    FS-->>U: "ok"
    U-->>C: "nil"
```

Sources: [runner/internal/updater/updater.go:108-232]()

The convenience method `UpdateNow` [runner/internal/updater/updater.go:211-232]() combines all three steps. `UpdateToVersion` [runner/internal/updater/updater.go:235-249]() skips the check and goes directly to `Download` + `Apply` for a named version.

### `Apply` and Atomic Replacement

`Apply` [runner/internal/updater/updater.go:197-208]() resolves the running executable path via `execPathFunc` (defaults to `os.Executable`), then calls `atomicReplace(tmpPath, execPath)`. The `atomicReplace` function is platform-specific and not defined in `updater.go` itself — it handles the constraint that Windows cannot overwrite a running binary (requires a different strategy than a POSIX `rename` syscall).

On non-Windows systems, the downloaded archive is `chmod`-ed to `0755` after extraction [runner/internal/updater/updater.go:186-191]().

### Backup and Rollback

`CreateBackup` [runner/internal/updater/updater.go:276-289]() copies the current executable to `<execPath>.bak` using `copyFile`.

`Rollback` [runner/internal/updater/updater.go:257-273]() reads `<execPath>.bak` and calls `atomicReplace(backupPath, execPath)`. If no backup file exists, it returns an explicit error. The rollback does not restart the process; that is left to the caller.

### Prerelease Filtering

In `CheckForUpdate` [runner/internal/updater/updater.go:143-145](), if `allowPrerelease` is `false` (the default) and the latest release has a non-empty semver prerelease segment, `HasUpdate` is forced to `false` even if the semver ordinal is higher.

---

## Backend-Side: `VersionChecker`

The `VersionChecker` [backend/internal/service/runner/version_checker.go:32-38]() runs as a background goroutine in the backend process. Its sole purpose is to keep a Redis key up to date with the latest published runner version, so that the REST API can return this value cheaply without calling GitHub on every request.

### Construction and Lifecycle

`NewVersionChecker(redisClient *redis.Client)` [backend/internal/service/runner/version_checker.go:42-55]() returns `nil` if `redisClient` is nil. All methods check for nil receiver and degrade silently — the feature is opt-in and requires a Redis connection.

`Start(ctx context.Context)` [backend/internal/service/runner/version_checker.go:58-88]() launches two goroutines:

1. An **immediate first check** to populate the cache on startup.
2. A **ticker goroutine** that calls `checkGitHubRelease` every `defaultCheckInterval` (1 hour).

**Backend VersionChecker Component Map**

```mermaid
flowchart LR
    subgraph "version_checker.go"
        NC["NewVersionChecker(redisClient)"]
        ST["Start(ctx)\n→ goroutine ticker"]
        GLV["GetLatestVersion(ctx)\n→ redis GET"]
        CGR["checkGitHubRelease(ctx)\n→ HTTP + redis SET"]
        NV["NormalizeVersion(string)\n→ strip v prefix"]
    end

    RK["Redis key:\nrunner:latest_version\nTTL: 1h"]
    GHAPI["GitHub API\nhttps://api.github.com/repos/\nAgentsMesh/AgentsMesh/releases/latest"]

    NC --> ST
    ST -- "every 1h" --> CGR
    CGR -- "parse" --> NV
    CGR -- "SET" --> RK
    GLV -- "GET" --> RK
    CGR -- "HTTP GET" --> GHAPI
```

Sources: [backend/internal/service/runner/version_checker.go:1-157]()

### Redis Caching

| Constant | Value |
|---|---|
| `redisKeyLatestVersion` | `"runner:latest_version"` |
| `defaultCheckInterval` | `1 * time.Hour` |
| `redisCacheTTL` | `1 * time.Hour` |

`GetLatestVersion` [backend/internal/service/runner/version_checker.go:92-103]() is a synchronous read from Redis. Cache misses and Redis errors are treated identically: an empty string is returned and the error is suppressed. This prevents any Redis instability from surfacing to callers.

### GitHub API Request

`checkGitHubRelease` [backend/internal/service/runner/version_checker.go:112-151]() sends:

```
GET https://api.github.com/repos/AgentsMesh/AgentsMesh/releases/latest
Accept: application/vnd.github+json
User-Agent: AgentsMesh-Backend
```

The response is decoded into `githubRelease` [backend/internal/service/runner/version_checker.go:106-109]():

```go
type githubRelease struct {
    TagName string `json:"tag_name"`
    Draft   bool   `json:"draft"`
}
```

The `Draft` field is parsed but not currently used to filter results. A non-200 HTTP response, a JSON decode error, or an empty `tag_name` all result in a logged warning (not a fatal error).

### `NormalizeVersion`

The backend `NormalizeVersion` [backend/internal/service/runner/version_checker.go:155-157]() strips the `v` prefix and trims whitespace:

- `"v1.2.3"` → `"1.2.3"`
- `"1.2.3"` → `"1.2.3"`
- `"  v0.1.0-beta.1  "` → `"0.1.0-beta.1"`

The runner-side `normalizeVersion` does the opposite — it ensures the `v` prefix is present for semver comparison via `Masterminds/semver`.

---

## Version String Conventions

The two components use opposite normalization conventions:

| Component | Convention | Example input | Example output |
|---|---|---|---|
| `backend/NormalizeVersion` | Strip `v` prefix | `v1.2.3` | `1.2.3` |
| `runner/normalizeVersion` | Add `v` prefix | `1.2.3` | `v1.2.3` |

The runner uses `github.com/Masterminds/semver/v3` for comparison [runner/internal/updater/updater.go:14](), which requires the `v` prefix. The backend stores the version without prefix in Redis for use in JSON API responses.

---

## Interaction with the Release Pipeline

Runner binaries are published to GitHub Releases at `AgentsMesh/AgentsMesh` via GoReleaser in the GitHub Actions workflow [.github/workflows/release.yml:82-119](). Release assets follow the naming pattern:

```
agentsmesh-runner_<version>_<os>_<arch>.tar.gz   (Linux, macOS)
agentsmesh-runner_<version>_<os>_<arch>.zip       (Windows)
```

The `ReleaseDetector` implementation in the runner (`NewGitHubReleaseDetector`) selects the correct asset from the release by matching `runtime.GOOS` and `runtime.GOARCH` against the asset filename.

Sources: [.github/workflows/release.yml:77-119](), [runner/internal/updater/updater.go:8-10]()

---

# Page: Relay

# Relay

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [relay/internal/backend/client.go](relay/internal/backend/client.go)
- [relay/internal/backend/client_test.go](relay/internal/backend/client_test.go)
- [relay/internal/channel/channel_manager_test.go](relay/internal/channel/channel_manager_test.go)
- [relay/internal/channel/helpers_test.go](relay/internal/channel/helpers_test.go)
- [relay/internal/channel/terminal_channel.go](relay/internal/channel/terminal_channel.go)
- [relay/internal/channel/terminal_channel_test.go](relay/internal/channel/terminal_channel_test.go)
- [relay/internal/server/handler_test.go](relay/internal/server/handler_test.go)
- [relay/internal/server/server.go](relay/internal/server/server.go)
- [relay/internal/server/server_test.go](relay/internal/server/server_test.go)

</details>



This page covers the Relay service: its role as a WebSocket intermediary, its internal structure, the publisher/subscriber channel model, and its lifecycle with the backend. For channel and session management internals see [Channel and Session Management](#4.1). For the backend registration and heartbeat protocol see [Backend Registration and Heartbeat](#4.2). For the runner-side WebSocket client that connects to the Relay, see [Relay Client](#3.5). For the web frontend's terminal connection pool that connects as a subscriber, see [Terminal Workspace](#5.1).

---

## Purpose

The Relay is an independent Go service that proxies terminal I/O between runners and browsers over WebSocket. It decouples the runner (which produces terminal output) from one or more browser sessions (which observe and optionally control the terminal). The backend does not carry any terminal data; it only coordinates which relay serves which pod.

The Relay:

- Accepts a single **publisher** WebSocket connection per pod from a runner
- Accepts multiple **subscriber** WebSocket connections per pod from browsers
- Forwards all publisher output to all subscribers (broadcast)
- Forwards subscriber input to the publisher (with input control enforcement)
- Registers itself with the backend on startup and sends periodic heartbeats
- Notifies the backend when all subscribers leave a channel

---

## High-Level Data Flow

**Relay data flow between runner, browser, and backend**

```mermaid
sequenceDiagram
    participant "Runner" as runner
    participant "Relay /runner/terminal" as relayrun
    participant "Relay /browser/terminal" as relaybrow
    participant "Browser" as browser
    participant "Backend /api/internal/relays/*" as backend

    runner->>relayrun: "WebSocket connect (JWT token, pod_key)"
    relayrun->>relayrun: "SetPublisher → forwardPublisherToSubscribers goroutine"
    browser->>relaybrow: "WebSocket connect (JWT token, pod_key)"
    relaybrow->>relaybrow: "AddSubscriber → forwardSubscriberToPublisher goroutine"
    runner-->>relaybrow: "Output messages → Broadcast to all subscribers"
    browser-->>relayrun: "Input/Resize/ImagePaste → forwarded to publisher"
    browser->>relaybrow: "Control request → grant/deny response"
    relayrun->>backend: "NotifySessionClosed (when last subscriber leaves)"
```

Sources: [relay/internal/server/server.go:139-143](), [relay/internal/channel/terminal_channel.go:364-458]()

---

## Service Structure

**Server package component map**

```mermaid
graph TD
    main["main.go"] --> Server["server.Server"]
    Server --> ChannelManager["channel.ChannelManager"]
    Server --> BackendClient["backend.Client"]
    Server --> Handler["server.Handler"]
    Handler --> ChannelManager
    Handler --> TokenValidator["auth.TokenValidator"]
    ChannelManager --> TerminalChannel["channel.TerminalChannel (per pod)"]
    TerminalChannel --> Publisher["Publisher (*websocket.Conn)"]
    TerminalChannel --> Subscribers["Subscribers map[string]*Subscriber"]
    BackendClient --> BackendHTTP["Backend REST /api/internal/relays/*"]
```

Sources: [relay/internal/server/server.go:19-30](), [relay/internal/server/server.go:33-90]()

### Key Types

| Type | Package | Role |
|---|---|---|
| `Server` | `server` | Top-level service; owns `ChannelManager`, `backend.Client`, `Handler`, and the `http.Server` |
| `Handler` | `server` | HTTP request handlers for WebSocket endpoints and health/stats |
| `ChannelManager` | `channel` | Manages all `TerminalChannel` instances; routes publisher/subscriber connections |
| `TerminalChannel` | `channel` | Per-pod bidirectional relay channel; enforces input control and output buffering |
| `Subscriber` | `channel` | Wraps a single browser WebSocket connection with a serialized write mutex |
| `Client` | `backend` | HTTP client for backend registration, heartbeat, and session-close notifications |
| `TokenValidator` | `auth` | Validates JWT tokens on incoming WebSocket upgrades |

Sources: [relay/internal/server/server.go:19-30](), [relay/internal/channel/terminal_channel.go:41-122](), [relay/internal/backend/client.go:19-51]()

---

## HTTP Endpoints

The Relay exposes four HTTP endpoints registered in `Server.Start`:

| Route | Handler | Description |
|---|---|---|
| `GET /runner/terminal` | `Handler.HandleRunnerWS` | Runner connects as publisher; JWT validated, pod key extracted |
| `GET /browser/terminal` | `Handler.HandleBrowserWS` | Browser connects as subscriber; JWT validated, subscriber limit checked |
| `GET /health` | `Handler.HandleHealth` | Returns `{"status":"ok"}` |
| `GET /stats` | `Handler.HandleStats` | Returns active channel counts, subscriber counts, pending connections |

Authentication on both WebSocket endpoints requires a JWT token supplied as the `token` query parameter. The token encodes the pod key. Missing or invalid tokens receive `HTTP 401`. Empty pod keys receive `HTTP 400`.

Sources: [relay/internal/server/server.go:139-143](), [relay/internal/server/handler_test.go:49-66]()

---

## Publisher / Subscriber Model

Each pod that has an active terminal session is represented by one `TerminalChannel` identified by its `PodKey`. The channel follows a producer-consumer / observer pattern:

- **Publisher** (runner): one connection per channel. Sends `Output` and `Snapshot` messages. Receives `Input`, `Resize`, and `ImagePaste` messages from the controlling subscriber.
- **Subscriber** (browser): up to `MaxSubscribersPerPod` connections per channel. Receives all publisher output via broadcast. May request input control.

**TerminalChannel state machine**

```mermaid
stateDiagram-v2
    [*] --> "Pending": "publisher or subscriber connects first"
    "Pending" --> "Active": "both publisher and ≥1 subscriber connected"
    "Active" --> "PublisherDisconnected": "runner WebSocket closes"
    "PublisherDisconnected" --> "Active": "runner reconnects within PublisherReconnectTimeout"
    "PublisherDisconnected" --> "Closed": "PublisherReconnectTimeout exceeded"
    "Active" --> "KeepAlive": "last subscriber disconnects"
    "KeepAlive" --> "Active": "subscriber reconnects within KeepAliveDuration"
    "KeepAlive" --> "Closed": "KeepAliveDuration exceeded → onAllSubscribersGone callback"
    "Closed" --> [*]
```

Sources: [relay/internal/channel/terminal_channel.go:144-176](), [relay/internal/channel/terminal_channel.go:237-274](), [relay/internal/channel/terminal_channel.go:461-496]()

### Input Control

At most one subscriber can hold input control at a time. The `controllerID` field in `TerminalChannel` tracks the current controller. Subscribers negotiate control by sending `MsgTypeControl` messages with actions `request`, `release`, or `query`. When no controller is set, any subscriber may send input.

| Action | Outcome |
|---|---|
| `request` | Granted if `controllerID` is empty; denied otherwise |
| `release` | Clears `controllerID` if sender is the current controller |
| `query` | Returns current `controllerID` as a `status` response |

`Input` and `ImagePaste` messages from a non-controlling subscriber are silently dropped by `CanInput`.

Sources: [relay/internal/channel/terminal_channel.go:499-573](), [relay/internal/channel/terminal_channel.go:407-458]()

### Output Buffering

`TerminalChannel` maintains a ring buffer of recent `Output` messages (`outputBuffer`, bounded by `OutputBufferCount` and `OutputBufferSize`). When a new subscriber connects, the buffer is replayed to that subscriber so it sees recent terminal output. When a `Snapshot` message arrives from the publisher, the buffer is cleared because the snapshot supersedes all prior output.

Sources: [relay/internal/channel/terminal_channel.go:104-107](), [relay/internal/channel/terminal_channel.go:316-362](), [relay/internal/channel/terminal_channel.go:392-404]()

---

## Message Forwarding

Two goroutines are started per connection:

**`forwardPublisherToSubscribers`** — started by `SetPublisher`. Reads from the publisher `*websocket.Conn` in a loop. Each message is buffered (if `Output`) and broadcast to all subscribers via `Broadcast`. If the read fails, `handlePublisherDisconnect` is called.

**`forwardSubscriberToPublisher`** — started by `AddSubscriber`. Reads from the subscriber `*websocket.Conn` in a loop. Dispatches messages:

- `MsgTypeControl` → `handleControlRequest` (handled locally, not forwarded)
- `MsgTypePing` → `EncodePong` sent back (handled locally)
- `MsgTypeInput`, `MsgTypeImagePaste` → forwarded to publisher via `writeToPublisher` if `CanInput` passes
- All other types → forwarded to publisher

`Broadcast` uses a snapshot-then-write pattern: subscribers are copied under a read lock, then writes happen without holding the lock. This prevents a slow subscriber from blocking `Stats()` and the heartbeat goroutine.

Sources: [relay/internal/channel/terminal_channel.go:364-405](), [relay/internal/channel/terminal_channel.go:407-459](), [relay/internal/channel/terminal_channel.go:283-314]()

---

## Configuration

Configuration is loaded into `config.Config` at startup. Key sections:

| Config Section | Fields | Purpose |
|---|---|---|
| `Server` | `Host`, `Port`, `ReadTimeout`, `WriteTimeout`, `TLS.Enabled`, `TLS.CertFile`, `TLS.KeyFile` | HTTP listener settings |
| `JWT` | `Secret`, `Issuer` | Token validation for WebSocket upgrades |
| `Backend` | `URL`, `InternalAPISecret`, `HeartbeatInterval` | Backend connection parameters |
| `Session` | `KeepAliveDuration`, `MaxBrowsersPerPod`, `RunnerReconnectTimeout`, `BrowserReconnectTimeout`, `PendingConnectionTimeout`, `OutputBufferSize`, `OutputBufferCount` | Channel lifecycle parameters |
| `Relay` | `ID`, `Name`, `URL`, `InternalURL`, `Region`, `Capacity`, `AutoIP` | Relay identity parameters sent to backend |

Sources: [relay/internal/server/server.go:33-90](), [relay/internal/server/server_test.go:32-62]()

### TLS

When `Server.TLS.Enabled` is true, the server uses `tls.Config.GetCertificate` for dynamic certificate loading. On each TLS handshake, it first checks whether `backend.Client` has a certificate received from the backend (via ACME), then falls back to files configured in `TLS.CertFile`/`TLS.KeyFile`. This allows certificate rotation via heartbeat without a server restart.

Sources: [relay/internal/server/server.go:156-202]()

---

## Startup and Shutdown Sequence

**`Server.Start` lifecycle**

```mermaid
sequenceDiagram
    participant "main.go" as main
    participant "Server.Start" as start
    participant "backend.Client.Register" as register
    participant "backend.Client.StartHeartbeat" as hb
    participant "http.Server" as http

    main->>start: "Start(ctx)"
    start->>register: "registerWithRetry (exponential backoff, max 2min)"
    register-->>start: "registered"
    start->>hb: "go runHeartbeat(ctx) (auto-restart on panic)"
    start->>http: "ListenAndServe / ListenAndServeTLS"
    note over start: "blocks on ctx.Done() or errCh"
    main->>start: "cancel() (signal handler in main.go)"
    start->>start: "gracefulShutdown"
    start->>register: "Unregister"
    start->>start: "acceptingConnections = false"
    start->>start: "wait for ActiveChannels == 0 (max 30s)"
    start->>http: "http.Server.Shutdown"
```

`registerWithRetry` retries with exponential backoff (1s → 30s cap) for up to 2 minutes. This tolerates the relay starting before the backend HTTP server is fully initialized.

The heartbeat goroutine is wrapped in `runHeartbeat`, which restarts it after a 5-second delay if it exits unexpectedly (e.g., recovered panic).

Sources: [relay/internal/server/server.go:92-285]()

---

## Backend Communication

The `backend.Client` communicates with the backend over plain HTTP using the `X-Internal-Secret` header for authentication. It calls three internal endpoints:

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/internal/relays/register` | POST | Register relay on startup; receives optional TLS cert and DNS-assigned URL |
| `/api/internal/relays/heartbeat` | POST | Periodic liveness ping; sends connection count, CPU/memory usage, round-trip latency; may receive TLS cert |
| `/api/internal/relays/session-closed` | POST | Notified when all subscribers leave a pod's channel |
| `/api/internal/relays/unregister` | POST | Sent during graceful shutdown |

The `SendHeartbeat` call measures round-trip latency and stores it in `lastLatencyMs` for inclusion in the next heartbeat. If the backend returns `HTTP 404` on a heartbeat, the client marks itself as unregistered and immediately attempts re-registration.

Sources: [relay/internal/backend/client.go:165-246](), [relay/internal/backend/client.go:293-411](), [relay/internal/backend/client.go:420-455]()

### Auto-IP Detection

When `AutoIP` is true and `RelayName` is set, `Register` calls `detectPublicIP` before sending the registration request. It queries three external services (`api.ipify.org`, `ifconfig.me/ip`, `icanhazip.com`) in sequence and uses the first successful result. If all fail, registration proceeds without an IP (a warning is logged).

Sources: [relay/internal/backend/client.go:248-284]()

---

# Page: Channel and Session Management

# Channel and Session Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [relay/internal/backend/client.go](relay/internal/backend/client.go)
- [relay/internal/backend/client_test.go](relay/internal/backend/client_test.go)
- [relay/internal/channel/channel_manager_test.go](relay/internal/channel/channel_manager_test.go)
- [relay/internal/channel/helpers_test.go](relay/internal/channel/helpers_test.go)
- [relay/internal/channel/terminal_channel.go](relay/internal/channel/terminal_channel.go)
- [relay/internal/channel/terminal_channel_test.go](relay/internal/channel/terminal_channel_test.go)
- [relay/internal/server/handler_test.go](relay/internal/server/handler_test.go)
- [relay/internal/server/server.go](relay/internal/server/server.go)
- [relay/internal/server/server_test.go](relay/internal/server/server_test.go)

</details>



This page documents the channel and session management layer of the Relay service: the `TerminalChannel` and `ChannelManager` types, their internal state, and the rules governing publisher and subscriber lifecycles. For an overview of the Relay service itself and how it fits into the broader architecture, see [4](). For backend registration and heartbeat behavior, see [4.2]().

---

## Purpose

The Relay sits between browser clients and runners. Its core job is to multiplex a single runner WebSocket (the **publisher**) out to one or more browser WebSockets (the **subscribers**) for a given pod, while handling disconnections, buffering recent output, and arbitrating input control. The channel layer is entirely in the `relay/internal/channel` package.

---

## Core Types

### `TerminalChannel`

`TerminalChannel` [relay/internal/channel/terminal_channel.go:80-122]() is the central struct. One instance exists per active pod. It is identified by `PodKey` (the pod key, not a session ID).

| Field | Type | Purpose |
|---|---|---|
| `PodKey` | `string` | Unique channel identifier (pod key) |
| `publisher` | `*websocket.Conn` | The runner's WebSocket connection (at most one) |
| `publisherMu` | `sync.RWMutex` | Guards `publisher` and `publisherDisconnected` |
| `publisherWriteMu` | `sync.Mutex` | Serializes writes to publisher |
| `subscribers` | `map[string]*Subscriber` | Map of browser WebSocket connections |
| `subscribersMu` | `sync.RWMutex` | Guards subscriber map |
| `controllerID` | `string` | Subscriber with exclusive input rights (empty = any) |
| `controllerMu` | `sync.RWMutex` | Guards `controllerID` |
| `outputBuffer` | `[][]byte` | Ring buffer of recent `Output` messages |
| `outputBufferBytes` | `int` | Total byte count of buffer contents |
| `publisherDisconnected` | `bool` | True while publisher is temporarily absent |
| `keepAliveTimer` | `*time.Timer` | Fires when all subscribers have been absent for `KeepAliveDuration` |
| `publisherReconnectTimer` | `*time.Timer` | Fires if publisher does not reconnect within `PublisherReconnectTimeout` |
| `onAllSubscribersGone` | `func(podKey string)` | Callback when keep-alive expires |
| `onChannelClosed` | `func(podKey string)` | Callback on `Close()` |

Sources: [relay/internal/channel/terminal_channel.go:80-122]()

### `Subscriber`

`Subscriber` [relay/internal/channel/terminal_channel.go:41-53]() wraps a single browser WebSocket connection. Because `gorilla/websocket` does not support concurrent writes, each `Subscriber` has its own `writeMu` mutex.

```
type Subscriber struct {
    ID      string
    Conn    *websocket.Conn
    writeMu sync.Mutex
}
```

Sources: [relay/internal/channel/terminal_channel.go:41-53]()

### `ChannelConfig`

`ChannelConfig` [relay/internal/channel/terminal_channel.go:55-62]() holds per-channel tuning parameters.

| Field | Default | Meaning |
|---|---|---|
| `KeepAliveDuration` | 30s | Time to keep channel alive after all subscribers leave |
| `PublisherReconnectTimeout` | 30s | Time to wait for publisher to reconnect before closing |
| `SubscriberReconnectTimeout` | 30s | Reserved for future subscriber reconnect logic |
| `OutputBufferSize` | 256 KB | Max total byte size of the output ring buffer |
| `OutputBufferCount` | 200 | Max message count in the output ring buffer |

Sources: [relay/internal/channel/terminal_channel.go:55-73]()

---

## Data Flow

**Channel data flow: publisher-to-subscriber and subscriber-to-publisher**

```mermaid
flowchart LR
    Runner["Runner\n(publisher)"]
    BrowserA["Browser A\n(subscriber s1)"]
    BrowserB["Browser B\n(subscriber s2)"]

    subgraph TerminalChannel["TerminalChannel (PodKey)"]
        fwdPubSub["forwardPublisherToSubscribers()"]
        outputBuf["outputBuffer\n(ring buffer)"]
        fwdSubPub1["forwardSubscriberToPublisher(s1)"]
        fwdSubPub2["forwardSubscriberToPublisher(s2)"]
        ctrl["controllerID"]
    end

    Runner -->|"Output/Snapshot\nWebSocket binary"| fwdPubSub
    fwdPubSub -->|"bufferOutput()\nif MsgTypeOutput"| outputBuf
    fwdPubSub -->|"clearOutputBuffer()\nif MsgTypeSnapshot"| outputBuf
    fwdPubSub -->|"Broadcast()"| BrowserA
    fwdPubSub -->|"Broadcast()"| BrowserB

    BrowserA -->|"Input/ImagePaste/Control/Ping"| fwdSubPub1
    BrowserB -->|"Input/ImagePaste/Control/Ping"| fwdSubPub2

    fwdSubPub1 -->|"CanInput() check"| ctrl
    fwdSubPub2 -->|"CanInput() check"| ctrl
    fwdSubPub1 -->|"writeToPublisher()"| Runner
    fwdSubPub2 -->|"writeToPublisher()"| Runner
```

Sources: [relay/internal/channel/terminal_channel.go:364-458]()

---

## Message Types

The relay protocol (`relay/internal/protocol` package) defines the message types that flow across WebSocket connections. The channel layer uses these to decide how to route each message.

| Message Type | Direction | Handling |
|---|---|---|
| `MsgTypeOutput` | Publisher → Subscribers | Broadcast + buffered in `outputBuffer` |
| `MsgTypeSnapshot` | Publisher → Subscribers | Broadcast + `clearOutputBuffer()` |
| `MsgTypeInput` | Subscriber → Publisher | Forwarded only if `CanInput()` is true |
| `MsgTypeImagePaste` | Subscriber → Publisher | Forwarded only if `CanInput()` is true |
| `MsgTypeControl` | Subscriber → Channel | Handled by `handleControlRequest()`, not forwarded |
| `MsgTypePing` | Subscriber → Channel | Replied to locally with `MsgTypePong`, not forwarded |
| `MsgTypeRunnerDisconnected` | Channel → Subscribers | Sent on publisher disconnect |
| `MsgTypeRunnerReconnected` | Channel → Subscribers | Sent on publisher reconnect |

Sources: [relay/internal/channel/terminal_channel.go:391-458]()

---

## Publisher Lifecycle

**Publisher (runner) lifecycle state machine**

```mermaid
stateDiagram-v2
    [*] --> "Pending": "HandlePublisherConnect()\nno active channel"
    "Pending" --> "Active": "matching subscriber arrives\nSetPublisher() called"
    [*] --> "Active": "HandlePublisherConnect()\nchannel already exists"
    "Active" --> "Disconnected": "ReadMessage() error\nhandlePublisherDisconnect()"
    "Disconnected" --> "Active": "SetPublisher() before timeout\nbroadcasts RunnerReconnected"
    "Disconnected" --> "Closed": "publisherReconnectTimer fires\nClose() called"
    "Active" --> "Closed": "Close() called"
    "Closed" --> [*]
```

Sources: [relay/internal/channel/terminal_channel.go:144-176](), [relay/internal/channel/terminal_channel.go:461-496]()

**`SetPublisher(conn *websocket.Conn)`** [relay/internal/channel/terminal_channel.go:144-176]():

1. Acquires `publisherMu`. Stores `conn`. Clears `publisherDisconnected`. Cancels any existing `publisherReconnectTimer`.
2. If an old connection exists, closes it so its `forwardPublisherToSubscribers` goroutine exits cleanly via a `ReadMessage` error.
3. If reconnecting (`wasDisconnected == true`), broadcasts `protocol.EncodeRunnerReconnected()` to all subscribers.
4. Spawns a new `forwardPublisherToSubscribers()` goroutine bound to the new connection.

**`handlePublisherDisconnect(disconnectedConn)`** [relay/internal/channel/terminal_channel.go:461-496]():

- Performs an **identity check**: if `c.publisher != disconnectedConn`, the publisher was already replaced by `SetPublisher`, so this call is a no-op.
- Otherwise: sets `publisher = nil`, `publisherDisconnected = true`, starts `publisherReconnectTimer`.
- After releasing `publisherMu`, broadcasts `protocol.EncodeRunnerDisconnected()`.

Sources: [relay/internal/channel/terminal_channel.go:144-176](), [relay/internal/channel/terminal_channel.go:461-496]()

---

## Subscriber Lifecycle

**`AddSubscriber(subscriberID string, conn *websocket.Conn)`** [relay/internal/channel/terminal_channel.go:193-234]():

1. Adds the `Subscriber` to the `subscribers` map.
2. Cancels any pending `keepAliveTimer`.
3. Sends all buffered `Output` messages from `outputBuffer` to the new subscriber. This allows a late-joining browser to see recent terminal output.
4. If the publisher is currently disconnected (`publisherDisconnected == true`), immediately sends `protocol.EncodeRunnerDisconnected()` to the new subscriber so it shows the correct state.
5. Spawns a `forwardSubscriberToPublisher(subscriberID)` goroutine.

**`RemoveSubscriber(subscriberID string)`** [relay/internal/channel/terminal_channel.go:237-274]():

1. Closes and removes the subscriber connection.
2. Releases `controllerID` if this subscriber held it.
3. If no subscribers remain, starts `keepAliveTimer`. When it fires, `onAllSubscribersGone(podKey)` is called (which in turn calls `backendClient.NotifySessionClosed()`).

Sources: [relay/internal/channel/terminal_channel.go:193-274]()

---

## Broadcast and Write Safety

`Broadcast(data []byte)` [relay/internal/channel/terminal_channel.go:287-314]() uses a **snapshot-then-write** pattern to avoid holding the subscriber lock during I/O:

1. Take a read lock on `subscribersMu` and copy subscriber pointers into a local slice.
2. Release the lock.
3. Write to each subscriber via `Subscriber.WriteMessage()`, which holds the per-subscriber `writeMu`.
4. Collect failed subscriber IDs and call `RemoveSubscriber` for each.

This prevents a slow or dead subscriber connection from blocking `Stats()`, `SubscriberCount()`, or the heartbeat callback.

The `writeWait` constant (`5 * time.Second`) is applied as a write deadline to every WebSocket write [relay/internal/channel/terminal_channel.go:13-21]().

Sources: [relay/internal/channel/terminal_channel.go:13-21](), [relay/internal/channel/terminal_channel.go:287-314]()

---

## Input Control

At most one subscriber holds input control at a time. The `controllerID` field tracks which subscriber (identified by its ID string) is the current controller. An empty `controllerID` means any subscriber may send input.

**Control request/response protocol:**

| Action sent | Condition | Response action |
|---|---|---|
| `request` | No current controller | `granted`, `Controller = subscriberID` |
| `request` | Another subscriber controls | `denied`, `Controller = existing controllerID` |
| `release` | Sender is controller | `released`, `Controller = ""` |
| `query` | Any | `status`, `Controller = current controllerID` |

`handleControlRequest` [relay/internal/channel/terminal_channel.go:499-540]() processes these entirely within the relay — control messages are never forwarded to the publisher.

`CanInput(subscriberID)` [relay/internal/channel/terminal_channel.go:543-549]() returns `true` if `controllerID == ""` or `controllerID == subscriberID`. Input and image-paste messages from subscribers who cannot input are silently discarded.

Sources: [relay/internal/channel/terminal_channel.go:499-573]()

---

## Output Buffer

The output buffer is a ring buffer that lets newly connected subscribers receive recent terminal output they missed.

**Eviction policy** (`bufferOutput` [relay/internal/channel/terminal_channel.go:317-339]()):

- If `len(outputBuffer) >= OutputBufferCount` **or** `outputBufferBytes + len(data) > OutputBufferSize`, the oldest message is evicted (FIFO).
- A single message larger than `OutputBufferSize` is not buffered at all.
- Copies of data are stored (not references) to avoid data races.

**Snapshot handling** [relay/internal/channel/terminal_channel.go:399-402]():

When a `MsgTypeSnapshot` arrives from the publisher, `clearOutputBuffer()` is called immediately. A snapshot encodes the full current terminal state, so all prior incremental output messages become redundant. New subscribers will receive the snapshot rather than stale incremental messages.

Sources: [relay/internal/channel/terminal_channel.go:317-362](), [relay/internal/channel/terminal_channel.go:391-404]()

---

## ChannelManager

`ChannelManager` coordinates multiple `TerminalChannel` instances and handles the race between a publisher and subscribers connecting in any order.

**`ChannelManagerConfig`** (from `server.go` [relay/internal/server/server.go:72-80]()):

| Config Field | Session Config Source | Purpose |
|---|---|---|
| `KeepAliveDuration` | `cfg.Session.KeepAliveDuration` | Passed to each `TerminalChannel` |
| `MaxSubscribersPerPod` | `cfg.Session.MaxBrowsersPerPod` | Upper limit on subscribers per channel |
| `PublisherReconnectTimeout` | `cfg.Session.RunnerReconnectTimeout` | Passed to each `TerminalChannel` |
| `SubscriberReconnectTimeout` | `cfg.Session.BrowserReconnectTimeout` | Passed to each `TerminalChannel` |
| `PendingConnectionTimeout` | `cfg.Session.PendingConnectionTimeout` | Max wait time for pending connections |
| `OutputBufferSize` | `cfg.Session.OutputBufferSize` | Passed to each `TerminalChannel` |
| `OutputBufferCount` | `cfg.Session.OutputBufferCount` | Passed to each `TerminalChannel` |

Sources: [relay/internal/server/server.go:72-81]()

### Pending Connection Matching

When a publisher or subscriber arrives for a pod key, the channel may not yet exist:

**Channel and ChannelManager connection states**

```mermaid
flowchart TD
    PubConnect["HandlePublisherConnect(podKey, conn)"]
    SubConnect["HandleSubscriberConnect(podKey, id, conn)"]

    PubConnect --> ExistsPub{"Channel\nexists?"}
    ExistsPub -->|"yes"| SetPublisher["ch.SetPublisher(conn)\n(reconnect or replace)"]
    ExistsPub -->|"no"| PendingSub{"Pending\nsubscriber\nfor podKey?"}
    PendingSub -->|"yes"| CreateChanPub["Create TerminalChannel\nSetPublisher()\nAddSubscriber()"]
    PendingSub -->|"no"| StorePendingPub["Store as\npendingPublisher"]

    SubConnect --> ExistsSub{"Channel\nexists?"}
    ExistsSub -->|"yes"| CheckMax{"Subscriber\ncount < Max?"}
    CheckMax -->|"yes"| AddSub["ch.AddSubscriber(id, conn)"]
    CheckMax -->|"no"| MaxErr["Return *MaxSubscribersError\nclose with ClosePolicyViolation"]
    ExistsSub -->|"no"| PendingPub{"Pending\npublisher\nfor podKey?"}
    PendingPub -->|"yes"| CreateChanSub["Create TerminalChannel\nSetPublisher()\nAddSubscriber()"]
    PendingPub -->|"no"| StorePendingSub["Store as\npendingSubscriber"]
```

Sources: [relay/internal/channel/channel_manager_test.go:82-128](), [relay/internal/server/handler_test.go:177-236]()

### `MaxSubscribersError`

When a subscriber attempts to join a channel that has already reached `MaxSubscribersPerPod`, `HandleSubscriberConnect` returns a `*MaxSubscribersError`. The HTTP handler sends a WebSocket close frame with code `ClosePolicyViolation` (1008) before returning.

Sources: [relay/internal/channel/channel_manager_test.go:200-227](), [relay/internal/server/handler_test.go:177-236]()

### `ChannelStats`

`Stats()` returns a `ChannelStats` struct used by the heartbeat to report connection counts to the backend.

| Field | Meaning |
|---|---|
| `ActiveChannels` | Channels with an active publisher and at least one subscriber |
| `TotalSubscribers` | Sum of subscriber counts across all active channels |
| `PendingPublishers` | Publishers waiting for a matching subscriber |
| `PendingSubscribers` | Subscribers waiting for a matching publisher |

Sources: [relay/internal/channel/channel_manager_test.go:269-311](), [relay/internal/server/server.go:220-224]()

---

## Channel Closed Lifecycle

**Channel closure events and callbacks**

```mermaid
sequenceDiagram
    participant Sub as "Subscriber (browser)"
    participant TC as "TerminalChannel"
    participant Mgr as "ChannelManager"
    participant BE as "backendClient"

    Sub->>TC: "disconnect"
    TC->>TC: "RemoveSubscriber()\nstart keepAliveTimer"
    Note over TC: "keepAliveDuration elapses\nno new subscriber"
    TC->>Mgr: "onAllSubscribersGone(podKey)"
    Mgr->>BE: "NotifySessionClosed(podKey, \"\")"

    Note over TC: "OR: publisherReconnectTimer fires"
    TC->>TC: "Close()"
    TC->>Mgr: "onChannelClosed(podKey)"
    Mgr->>Mgr: "delete channels[podKey]"
```

`Close()` [relay/internal/channel/terminal_channel.go:576-618]() is idempotent — a `closed` boolean checked under `closedMu` ensures the close logic runs at most once. On close:

1. Stops `keepAliveTimer` and `publisherReconnectTimer`.
2. Closes the publisher connection.
3. Closes all subscriber connections.
4. Empties the subscriber map.
5. Calls `onChannelClosed(podKey)`.

Sources: [relay/internal/channel/terminal_channel.go:576-618]()

---

## HTTP Endpoints and Handler Integration

The HTTP layer in `relay/internal/server/handler.go` upgrades WebSocket connections and hands them to the `ChannelManager`.

| Route | Handler | Calls |
|---|---|---|
| `/runner/terminal` | `HandleRunnerWS` | `channelManager.HandlePublisherConnect(podKey, conn)` |
| `/browser/terminal` | `HandleBrowserWS` | `channelManager.HandleSubscriberConnect(podKey, subscriberID, conn)` |
| `/health` | `HandleHealth` | Returns `{"status":"ok"}` |
| `/stats` | `HandleStats` | Returns `channelManager.Stats()` as JSON |

Token validation (JWT) is performed before upgrade. Missing or invalid tokens return HTTP 401. An empty `podKey` claim returns 400. The WebSocket upgrader uses 64 KB read and write buffers and allows all origins.

Sources: [relay/internal/server/server.go:139-143](), [relay/internal/server/handler_test.go:49-67](), [relay/internal/server/handler_test.go:97-118]()

---

## Graceful Shutdown

`gracefulShutdown` in `server.go` [relay/internal/server/server.go:243-285]() follows this sequence:

1. Calls `backendClient.Unregister()` (5 s timeout) to notify the backend.
2. Sets `acceptingConnections = false`.
3. Polls `channelManager.Stats().ActiveChannels` every second for up to 30 seconds, waiting for all channels to close naturally.
4. Calls `httpServer.Shutdown()` (10 s timeout).

The heartbeat goroutine (`runHeartbeat`) is wrapped in a restart loop: if it exits unexpectedly (e.g., panic recovery inside `StartHeartbeat`), it is restarted after a 5-second delay, unless the context is cancelled.

Sources: [relay/internal/server/server.go:214-285]()

---

# Page: Backend Registration and Heartbeat

# Backend Registration and Heartbeat

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/internal/api/rest/internal/relay_registration.go](backend/internal/api/rest/internal/relay_registration.go)
- [backend/internal/api/rest/internal/relay_registration_test.go](backend/internal/api/rest/internal/relay_registration_test.go)
- [backend/internal/config/config.go](backend/internal/config/config.go)
- [backend/internal/config/config_relay.go](backend/internal/config/config_relay.go)
- [backend/internal/service/relay/dns_service.go](backend/internal/service/relay/dns_service.go)
- [backend/internal/service/relay/dns_service_mock_test.go](backend/internal/service/relay/dns_service_mock_test.go)
- [backend/internal/service/relay/dns_service_sanitize_test.go](backend/internal/service/relay/dns_service_sanitize_test.go)
- [backend/migrations/000033_move_preparation_script_to_repository.down.sql](backend/migrations/000033_move_preparation_script_to_repository.down.sql)
- [backend/migrations/000033_move_preparation_script_to_repository.up.sql](backend/migrations/000033_move_preparation_script_to_repository.up.sql)
- [docs/images/logo.svg](docs/images/logo.svg)
- [relay/.env.example](relay/.env.example)
- [relay/internal/backend/client.go](relay/internal/backend/client.go)
- [relay/internal/backend/client_test.go](relay/internal/backend/client_test.go)
- [relay/internal/channel/channel_manager_test.go](relay/internal/channel/channel_manager_test.go)
- [relay/internal/channel/helpers_test.go](relay/internal/channel/helpers_test.go)
- [relay/internal/channel/terminal_channel.go](relay/internal/channel/terminal_channel.go)
- [relay/internal/channel/terminal_channel_test.go](relay/internal/channel/terminal_channel_test.go)
- [relay/internal/config/config.go](relay/internal/config/config.go)
- [relay/internal/config/config_test.go](relay/internal/config/config_test.go)
- [relay/internal/server/handler_test.go](relay/internal/server/handler_test.go)
- [relay/internal/server/server.go](relay/internal/server/server.go)
- [relay/internal/server/server_test.go](relay/internal/server/server_test.go)
- [web-admin/.env.example](web-admin/.env.example)

</details>



## Purpose and Scope

This page documents the relay's backend client: how a Relay instance registers itself with the Backend at startup, how it maintains a periodic heartbeat, how TLS certificates are provisioned and renewed, and how session-close events and graceful unregistration work.

This page covers the relay-side code in `relay/internal/backend/` and the corresponding backend-side handler in `backend/internal/api/rest/internal/`. For the relay's WebSocket channel model (publisher/subscriber), see [4.1](#4.1). For the backend's relay management service and DNS infrastructure, see the backend REST API documentation in [2.1](#2.1). For relay configuration loading, see [2.7](#2.7).

---

## Overview

When the relay process starts, it must introduce itself to the backend before accepting any WebSocket connections. The `Client` struct in [relay/internal/backend/client.go:19-51]() is the single component responsible for all relay-to-backend HTTP communication. The relay `Server` in [relay/internal/server/server.go:19-30]() owns exactly one `Client` instance and calls its methods during startup, operation, and shutdown.

**Lifecycle diagram: Relay ↔ Backend communication**

```mermaid
sequenceDiagram
    participant R as "relay/server.Server"
    participant C as "backend.Client"
    participant B as "Backend HTTP /api/internal/relays/*"

    R->>C: "registerWithRetry(ctx)"
    loop "exponential backoff (max 2 min)"
        C->>B: "POST /register"
        B-->>C: "{status, url, tls_cert, tls_key, dns_created}"
        note over C: "stores TLS cert, updates relayURL if DNS created"
    end
    R->>C: "StartHeartbeat(ctx, interval, getConnections)"
    loop "every HeartbeatInterval"
        C->>B: "POST /heartbeat {connections, cpu, memory, latency_ms, need_cert}"
        B-->>C: "{status, tls_cert?, tls_key?}"
        note over C: "measures RTT, updates cert if returned"
    end
    note over R: "subscriber leaves channel"
    R->>C: "NotifySessionClosed(ctx, podKey, sessionID)"
    C->>B: "POST /session-closed"
    note over R: "context cancelled (SIGTERM)"
    R->>C: "Unregister(ctx, reason)"
    C->>B: "POST /unregister"
```

Sources: [relay/internal/backend/client.go:165-455](), [relay/internal/server/server.go:95-240]()

---

## Client Construction

Two constructors are available:

| Constructor | Use case |
|---|---|
| `NewClient(...)` | Simple construction with positional args |
| `NewClientWithConfig(cfg ClientConfig)` | Full configuration including auto-IP and cert file paths |

`NewClientWithConfig` additionally attempts to load any existing TLS certificate from disk at construction time, enabling certificate persistence across process restarts.

```
ClientConfig {
  BaseURL           string  // http://backend:8080
  InternalAPISecret string  // used as X-Internal-Secret header
  RelayID           string
  RelayName         string  // optional, enables DNS auto-registration
  RelayURL          string  // public WebSocket URL
  RelayInternalURL  string  // URL used by runners inside Docker network
  RelayRegion       string
  RelayCapacity     int
  AutoIP            bool    // call detectPublicIP() before Register
  CertFile          string  // path to persist cert PEM
  KeyFile           string  // path to persist key PEM
}
```

Sources: [relay/internal/backend/client.go:53-113]()

---

## Registration

`Register(ctx context.Context) error` [relay/internal/backend/client.go:165-246]() performs the following steps:

1. **Auto-IP detection** — If `autoIP` is true and `relayName` is set and `relayIP` is empty, `detectPublicIP` queries three external services sequentially (`api.ipify.org`, `ifconfig.me/ip`, `icanhazip.com`) and uses the first valid response.

2. **HTTP POST** to `/api/internal/relays/register` with the `RegisterRequest` body and an `X-Internal-Secret` header for authentication.

3. **Response handling**:
   - If `DNSCreated` is true and a URL is returned, the in-memory `relayURL` is updated to the DNS-generated address.
   - If `TLSCert` and `TLSKey` are non-empty (ACME provisioning), the cert is stored in memory and optionally written to `certFile`/`keyFile` for persistence.

4. Sets `c.registered = true`.

**Registration request and response structures:**

```
RegisterRequest {
  relay_id     string
  relay_name   string   // optional (DNS auto-registration)
  ip           string   // optional (auto-detected or blank)
  url          string   // public WebSocket URL
  internal_url string
  region       string
  capacity     int
}

RegisterResponse {
  status       string
  url          string   // populated if DNS record was created
  internal_url string
  dns_created  bool
  tls_cert     string   // PEM cert chain (if ACME enabled on backend)
  tls_key      string   // PEM private key
  tls_expiry   string   // RFC3339
}
```

Sources: [relay/internal/backend/client.go:115-246]()

### Retry Logic

The `Server` does not call `Register` directly. It calls `registerWithRetry` [relay/internal/server/server.go:93-125](), which retries with exponential backoff (starting at 1 second, capping at 30 seconds) for up to 2 minutes. This handles the Docker Compose startup ordering problem where the relay container starts before the backend HTTP server is ready.

Sources: [relay/internal/server/server.go:93-125]()

---

## Backend-Side Registration Handler

On the backend, the `RelayHandler.Register` method [backend/internal/api/rest/internal/relay_registration.go:16-117]() handles `POST /api/internal/relays/register`:

1. If `relay_name` and `ip` are provided and the `DNSService` is enabled, it creates a DNS A record mapping the generated subdomain to the relay's public IP. The final URL in the relay record replaces only the host component of the relay-reported URL (scheme and port are preserved).
2. Calls `h.relayManager.Register(info)` to add the relay to the in-memory relay registry.
3. If an `acmeManager` is configured, fetches the current TLS certificate and includes it in the response.

**DNS domain generation** is handled by `DNSService.GenerateRelayDomain` [backend/internal/service/relay/dns_service.go:57-63]():
```
"us-east-1" → "us-east-1.relay.agentsmesh.cn"  (given BaseDomain = "relay.agentsmesh.cn")
```

Sources: [backend/internal/api/rest/internal/relay_registration.go:16-117](), [backend/internal/service/relay/dns_service.go:57-63]()

---

## Heartbeat

### SendHeartbeat

`SendHeartbeat(ctx context.Context, connections int) error` [relay/internal/backend/client.go:293-376]():

1. Guards against calling before registration (`registered == false` → error).
2. Reads Go runtime memory stats (`runtime.MemStats`) for `MemoryUsage = Alloc/Sys * 100`. CPU usage is currently always `0` (placeholder).
3. Sets `NeedCert = true` if no TLS cert is held in memory.
4. POSTs `HeartbeatRequest` to `/api/internal/relays/heartbeat`.
5. Measures round-trip latency and stores it in `lastLatencyMs` for inclusion in the next heartbeat.
6. If the backend returns HTTP 404, clears `registered` to trigger re-registration.
7. If the response includes a TLS cert, stores it in memory and on disk.

**Heartbeat structures:**

| Field | Type | Notes |
|---|---|---|
| `relay_id` | string | Identity |
| `connections` | int | Active channels count |
| `cpu_usage` | float64 | Always 0 (not yet implemented) |
| `memory_usage` | float64 | Go heap alloc / sys ratio |
| `latency_ms` | int | Previous heartbeat RTT |
| `need_cert` | bool | True if no TLS cert held |

Sources: [relay/internal/backend/client.go:139-157](), [relay/internal/backend/client.go:293-376]()

### StartHeartbeat Loop

`StartHeartbeat(ctx context.Context, interval time.Duration, getConnections func() int)` [relay/internal/backend/client.go:457-507]() runs in a goroutine:

- Fires on `time.Ticker` at the configured interval (default: 10 seconds, from `BackendConfig.HeartbeatInterval`).
- Calls `getConnections()` in a separate goroutine with a 5-second timeout to prevent deadlock propagation from a blocked `ChannelManager.Stats()` call.
- On heartbeat failure, immediately calls `Register` to re-register if the relay became unknown to the backend.
- Recovers from panics and logs them without crashing.

The `Server.runHeartbeat` wrapper [relay/internal/server/server.go:214-240]() restarts `StartHeartbeat` if it exits unexpectedly (e.g., after a recovered panic), with a 5-second delay between restarts.

The `getConnections` callback supplied by the server is:

```go
func() int {
    stats := s.channelManager.Stats()
    return stats.ActiveChannels
}
```

Sources: [relay/internal/backend/client.go:457-507](), [relay/internal/server/server.go:214-240]()

---

## TLS Certificate Management

The relay supports receiving TLS certificates provisioned by the backend via ACME (Let's Encrypt). This avoids running a separate certificate manager inside each relay instance.

**Certificate data flow:**

```mermaid
flowchart TD
    subgraph "relay/internal/backend/client.go"
        REG["Register()"]
        HB["SendHeartbeat()"]
        MEM["tlsCert / tlsKey fields"]
        FILES["saveCertificateFiles()"]
        LOAD["loadCertificateFiles()"]
    end

    subgraph "relay/internal/server/server.go"
        TLS["tls.Config.GetCertificate callback"]
    end

    subgraph "disk"
        CERTFILE["cfg.Server.TLS.CertFile"]
        KEYFILE["cfg.Server.TLS.KeyFile"]
    end

    REG -->|"TLSCert in RegisterResponse"| MEM
    HB -->|"TLSCert in HeartbeatResponse"| MEM
    MEM --> FILES
    FILES --> CERTFILE
    FILES --> KEYFILE
    LOAD -->|"at NewClientWithConfig"| MEM
    CERTFILE --> LOAD
    KEYFILE --> LOAD
    MEM -->|"HasTLSCertificate() / GetTLSCertificate()"| TLS
    CERTFILE -->|"fallback"| TLS
```

Sources: [relay/internal/backend/client.go:517-577](), [relay/internal/server/server.go:155-194]()

Key accessor methods on `Client`:

| Method | Purpose |
|---|---|
| `HasTLSCertificate()` | Returns true if both cert and key are non-empty |
| `GetTLSCertificate()` | Returns `(cert string, key string)` |
| `GetTLSExpiry()` | Returns expiry as RFC3339 string |

The server's `GetCertificate` callback [relay/internal/server/server.go:161-185]() first tries the in-memory certificate from `backendClient`, then falls back to loading from `TLS.CertFile`/`TLS.KeyFile` on disk. The certificate update (via heartbeat) therefore takes effect on the next TLS handshake without a server restart.

---

## Session Close Notification

When all browser subscribers disconnect from a channel and the keep-alive timer expires, the `Server` calls `NotifySessionClosed` [relay/internal/backend/client.go:379-411]().

This is wired via the `onAllSubscribersGone` closure in `server.New` [relay/internal/server/server.go:58-68]():

```go
onAllSubscribersGone := func(podKey string) {
    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()
    s.backendClient.NotifySessionClosed(ctx, podKey, "")
}
```

The notification POSTs `SessionClosedRequest` to `/api/internal/relays/session-closed`. Failures are logged but do not affect channel state.

Sources: [relay/internal/backend/client.go:379-411](), [relay/internal/server/server.go:58-68]()

---

## Graceful Unregistration

`Unregister(ctx context.Context, reason string) error` [relay/internal/backend/client.go:419-455]() is called by `gracefulShutdown` [relay/internal/server/server.go:242-285]() when the relay's context is cancelled (typically a SIGTERM forwarded by the process manager).

The shutdown sequence is:

```mermaid
sequenceDiagram
    participant CTX as "ctx.Done()"
    participant S as "server.gracefulShutdown()"
    participant C as "backend.Client"
    participant B as "Backend /unregister"
    participant CM as "ChannelManager"
    participant HTTP as "http.Server"

    CTX->>S: "cancelled"
    S->>C: "Unregister(5s timeout, reason)"
    C->>B: "POST /unregister {relay_id, reason}"
    B-->>C: "200 OK"
    S->>S: "acceptingConnections.Store(false)"
    loop "up to 30s, 1s poll"
        S->>CM: "Stats().ActiveChannels"
        CM-->>S: "count"
    end
    S->>HTTP: "Shutdown(10s timeout)"
```

After `Unregister` succeeds, `c.registered` is set to `false`. The unregister call is idempotent on the backend side: if the relay ID is not found, the handler returns `200 OK` with `status: not_found`.

Sources: [relay/internal/backend/client.go:419-455](), [relay/internal/server/server.go:242-285](), [backend/internal/api/rest/internal/relay_registration.go:119-150]()

---

## Configuration Reference

The relay-side configuration used by the client is loaded from environment variables via `relay/internal/config/config.go`. The relevant fields are:

| Config field | Env var | Default | Description |
|---|---|---|---|
| `Backend.URL` | `BACKEND_URL` | `http://backend:8080` | Base URL for all internal API calls |
| `Backend.InternalAPISecret` | `INTERNAL_API_SECRET` | — (required) | Value of `X-Internal-Secret` header |
| `Backend.HeartbeatInterval` | `HEARTBEAT_INTERVAL` | `10s` | Ticker interval for `StartHeartbeat` |
| `Relay.ID` | `RELAY_ID` | auto-generated from hostname | Sent in every request as `relay_id` |
| `Relay.Name` | `RELAY_NAME` | `""` | Enables DNS auto-registration |
| `Relay.AutoIP` | `RELAY_AUTO_IP` | `false` | Auto-detect public IP before registration |
| `Relay.URL` | `RELAY_URL` | derived from `PRIMARY_DOMAIN` | Sent as `url` in registration |
| `Relay.InternalURL` | `RELAY_INTERNAL_URL` | `""` | Docker-internal URL for runners |
| `Relay.Region` | `RELAY_REGION` | `default` | Geo-region tag |
| `Relay.Capacity` | `RELAY_CAPACITY` | `1000` | Max connections declared to backend |
| `Server.TLS.CertFile` | `TLS_CERT_FILE` | `""` | Path for cert persistence |
| `Server.TLS.KeyFile` | `TLS_KEY_FILE` | `""` | Path for key persistence |

Sources: [relay/internal/config/config.go:89-221]()

---

# Page: Web Frontend

# Web Frontend

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude/skills/worktree/SKILL.md](.claude/skills/worktree/SKILL.md)
- [CLAUDE.md](CLAUDE.md)
- [deploy/dev/.gitignore](deploy/dev/.gitignore)
- [deploy/dev/backend.Dockerfile](deploy/dev/backend.Dockerfile)
- [deploy/dev/docker-compose.yml](deploy/dev/docker-compose.yml)
- [deploy/dev/init-seed.sh](deploy/dev/init-seed.sh)
- [deploy/dev/nginx/conf.d/default.conf](deploy/dev/nginx/conf.d/default.conf)
- [deploy/dev/nginx/nginx.conf](deploy/dev/nginx/nginx.conf)
- [deploy/dev/runner-entrypoint.sh](deploy/dev/runner-entrypoint.sh)
- [deploy/dev/runner.Dockerfile](deploy/dev/runner.Dockerfile)
- [deploy/dev/seed/seed.sql](deploy/dev/seed/seed.sql)
- [deploy/dev/traefik/dynamic/grpc.yml](deploy/dev/traefik/dynamic/grpc.yml)
- [deploy/dev/web.Dockerfile](deploy/dev/web.Dockerfile)
- [web/package.json](web/package.json)
- [web/pnpm-lock.yaml](web/pnpm-lock.yaml)
- [web/src/app/globals.css](web/src/app/globals.css)
- [web/src/components/mesh/MessageList.tsx](web/src/components/mesh/MessageList.tsx)
- [web/src/components/mobile/MobileShell.tsx](web/src/components/mobile/MobileShell.tsx)
- [web/src/components/ui/block-editor.tsx](web/src/components/ui/block-editor.tsx)
- [web/src/components/ui/markdown.tsx](web/src/components/ui/markdown.tsx)
- [web/src/lib/api/base.ts](web/src/lib/api/base.ts)
- [web/src/providers/PostHogProvider.tsx](web/src/providers/PostHogProvider.tsx)

</details>



This page documents the Next.js web application located in the `web/` directory. It covers the tech stack, directory structure, core libraries, API communication layer, theming system, analytics integration, and how the major UI surfaces connect. For specifics on individual subsystems, see:

- [Terminal Workspace](#5.1) — `TerminalConnectionPool`, `useTerminal`, xterm.js integration
- [Ticket Management](#5.2) — Kanban board, `useTicketStore`, `ticketApi`
- [AgentsMesh Network View](#5.3) — `IDEShell`, `MeshPage`, `WorkspaceManager`
- [Channels and Chat](#5.4) — `ChannelChatPanel`, `channelApi`, pod mentions
- [Real-time State Management](#5.5) — Zustand stores, `RealtimeProvider`
- [Environment and API Configuration](#5.6) — URL resolution, `getApiBaseUrl`, Next.js rewrites

---

## Purpose and Scope

The web frontend is the primary user interface for AgentsMesh. It runs as a Next.js 16 application (App Router) and provides:

- Authentication and organization management
- Terminal workspace for interacting with AI agent pods
- Kanban ticket tracking
- AgentsMesh topology visualization
- Channel-based multi-agent chat
- Real-time event handling over WebSocket

The frontend communicates with the Go backend over REST and WebSocket. It does **not** communicate directly with the Runner or Relay — those connections are brokered through the backend and Relay service respectively.

---

## Tech Stack

| Category | Library | Version |
|---|---|---|
| Framework | `next` | 16.1.1 |
| UI Runtime | `react`, `react-dom` | 19.2.3 |
| Language | TypeScript | ^5 |
| Styling | `tailwindcss` | ^4.2.1 |
| State | `zustand` | ^5.0.9 |
| Data Fetching | `@tanstack/react-query` | ^5.90.16 |
| Terminal | `@xterm/xterm` | ^6.0.0 |
| Graph/Flow | `@xyflow/react` | ^12.10.0 |
| Rich Text | `@blocknote/core`, `@blocknote/react`, `@blocknote/mantine` | ^0.46.0 |
| Drag & Drop | `@dnd-kit/core`, `@dnd-kit/sortable` | ^6.3.1, ^10.0.0 |
| UI Primitives | `@radix-ui/*` | various |
| Icons | `lucide-react` | ^0.562.0 |
| Animation | `framer-motion` | ^12.26.2 |
| Markdown | `react-markdown`, `remark-gfm` | ^10.1.0, ^4.0.1 |
| Virtualization | `@tanstack/react-virtual` | ^3.13.18 |
| i18n | `next-intl` | ^4.7.0 |
| Themes | `next-themes` | ^0.4.6 |
| Toasts | `sonner` | ^2.0.7 |
| Command Palette | `cmdk` | ^1.1.1 |
| Analytics | `posthog-js` | ^1.347.2 |
| Charts | `recharts` | ^3.6.0 |
| Resizable Panels | `react-resizable-panels` | ^4.3.3 |
| Testing | `vitest`, `@testing-library/react` | ^4.0.16, ^16.3.1 |

Sources: [web/package.json:1-83]()

---

## Application Structure

**Directory layout for `web/src/`:**

```
web/src/
├── app/                    # Next.js App Router pages
│   ├── (auth)/             # Login, register routes
│   ├── (dashboard)/        # Main application routes
│   └── api/                # Next.js API routes
├── components/
│   ├── ui/                 # Shared primitives (Button, Markdown, BlockEditor, etc.)
│   ├── mesh/               # AgentsMesh network view components
│   ├── mobile/             # Mobile-specific shell and navigation
│   └── ...                 # Feature-specific component directories
├── lib/
│   ├── api/                # API client modules
│   │   └── base.ts         # ApiError, request(), orgPath()
│   └── env.ts              # getApiBaseUrl() and URL resolution
├── stores/                 # Zustand stores
├── hooks/                  # Custom React hooks
├── messages/               # next-intl translation files
└── providers/              # React context providers
```

Sources: [CLAUDE.md:212-224]()

---

## Component and System Map

The following diagram maps the major UI surfaces to their corresponding code entities.

**Diagram: Frontend component hierarchy**

```mermaid
graph TD
  AppRouter["app/ (Next.js App Router)"]
  AuthGroup["(auth)/ group"]
  DashboardGroup["(dashboard)/ group"]

  AppRouter --> AuthGroup
  AppRouter --> DashboardGroup

  DashboardGroup --> IDEShell["IDEShell (components/mesh)"]
  DashboardGroup --> MobileShell["MobileShell (components/mobile)"]
  DashboardGroup --> TicketsPage["TicketsPage (components/tickets)"]

  IDEShell --> MeshPage["MeshPage - @xyflow/react topology"]
  IDEShell --> TerminalWorkspace["TerminalPane + useTerminal"]
  IDEShell --> BottomPanel["BottomPanel - ChannelChatPanel"]

  MobileShell --> MobileHeader["MobileHeader"]
  MobileShell --> MobileTabBar["MobileTabBar"]
  MobileShell --> MobileDrawer["MobileDrawer"]

  TerminalWorkspace --> TerminalConnectionPool["TerminalConnectionPool (WebSocket)"]
  TerminalWorkspace --> XtermJS["@xterm/xterm Terminal"]
```

Sources: [web/src/components/mobile/MobileShell.tsx:1-74](), [web/src/components/mesh/MessageList.tsx:1-50](), [CLAUDE.md:212-224]()

---

## API Communication Layer

All HTTP requests go through the `request<T>()` function in [web/src/lib/api/base.ts:94-162](). This function:

1. Reads the current JWT from `useAuthStore`
2. Attaches `Authorization: Bearer <token>` to every request
3. On a `401` response, attempts a token refresh via `handleTokenRefresh()`
4. Retries the original request with the new token
5. If refresh fails, calls `logout()` and redirects to `/login`

The refresh logic is deduplicated: concurrent requests that hit a `401` share a single refresh `Promise` to avoid issuing multiple `/api/v1/auth/refresh` calls.

**Key exports from `base.ts`:**

| Export | Purpose |
|---|---|
| `ApiError` | Typed error class with `.status`, `.code`, `.serverMessage` |
| `request<T>(endpoint, options)` | Authenticated fetch with token refresh |
| `publicRequest<T>(endpoint)` | Unauthenticated GET |
| `orgPath(path)` | Prepends `/api/v1/orgs/:slug` to `path` using current org from store |
| `handleTokenRefresh()` | Deduplication wrapper for token refresh |

**Diagram: request() flow**

```mermaid
sequenceDiagram
  participant C as "Component"
  participant R as "request<T>()"
  participant A as "useAuthStore"
  participant B as "Backend REST API"

  C->>R: "call request(endpoint)"
  R->>A: "getState().token"
  R->>B: "fetch with Authorization header"
  alt "200 OK"
    B-->>R: "response body"
    R-->>C: "parsed JSON"
  else "401 Unauthorized"
    R->>R: "handleTokenRefresh()"
    R->>B: "POST /api/v1/auth/refresh"
    B-->>R: "new token"
    R->>A: "setTokens(token, refresh_token)"
    R->>B: "retry original request"
    B-->>R: "response body"
    R-->>C: "parsed JSON"
  else "refresh fails"
    R->>A: "logout()"
    R-->>C: "redirect to /login"
  end
```

Sources: [web/src/lib/api/base.ts:1-193]()

---

## State Management

State is managed exclusively with Zustand stores in `web/src/stores/`. Each store corresponds to a domain:

| Store | File | Primary State |
|---|---|---|
| `useAuthStore` | `stores/auth.ts` | `user`, `token`, `refreshToken`, `currentOrg` |
| `usePodStore` | `stores/pod.ts` | Pod list, active pod |
| `useRunnerStore` | `stores/runner.ts` | Runner list and status |
| `useChannelStore` | `stores/channel.ts` | Channel messages and membership |
| `useWorkspaceStore` | `stores/workspace.ts` | Workspace and worktree state |
| `useIDEStore` | `stores/ide.ts` | IDE activity panel state, `_hasHydrated` |

Real-time updates arrive via WebSocket through `RealtimeProvider` and are dispatched into these stores. See [Real-time State Management](#5.5) for details.

Sources: [web/src/components/mobile/MobileShell.tsx:10-11](), [web/src/providers/PostHogProvider.tsx:7-8](), [CLAUDE.md:212-224]()

---

## Theming

The application supports four themes, defined as CSS variable sets in [web/src/app/globals.css:1-289]():

| Theme Class | Description |
|---|---|
| `:root` (default) | Light theme |
| `.dark` | Dark theme |
| `.solarized-light` | Solarized Light |
| `.solarized-dark` | Solarized Dark |

Each theme defines two groups of variables:

- **UI variables**: `--background`, `--foreground`, `--primary`, `--secondary`, `--muted`, `--border`, etc.
- **Terminal variables**: `--terminal-bg`, `--terminal-bg-secondary`, `--terminal-text`, `--terminal-border`, etc. (kept dark across all themes for readability)

The `@theme inline` block in the CSS maps these variables to Tailwind utility classes (e.g. `bg-background`, `text-primary`), making them available throughout the component tree.

Theme switching is handled by `next-themes`. Components that need to read the current theme directly (e.g. `BlockEditor`) use a `MutationObserver` on `document.documentElement.classList` to detect changes — see [web/src/components/ui/block-editor.tsx:31-58]().

Sources: [web/src/app/globals.css:1-289](), [web/src/components/ui/block-editor.tsx:31-58]()

---

## Key Shared UI Components

### `Markdown`

Located at [web/src/components/ui/markdown.tsx:87-113](), this component wraps `react-markdown` with:

- GitHub Flavored Markdown via `remark-gfm`
- Optional `compact` mode (smaller prose sizing)
- Optional `highlightMentions` — scans text nodes for `@word` patterns and wraps them in styled `<span>` elements

### `BlockEditor` / `BlockViewer`

Located at [web/src/components/ui/block-editor.tsx:105-176](), these components wrap `@blocknote/react`:

- `BlockEditor` — editable rich text with image upload via `/api/v1/orgs/:slug/files/upload`
- `BlockViewer` — read-only view of a BlockNote document (JSON string format)
- Both components detect the active theme automatically

### Mobile Layout

`MobileShell` ([web/src/components/mobile/MobileShell.tsx:35-74]()) provides the responsive mobile layout:

- `MobileHeader` — top bar with hamburger menu
- `MobileTabBar` — bottom navigation with 5 tabs
- `MobileDrawer` — left-side navigation overlay
- `MobileSidebar` — right-side content panel
- `MobileMoreMenu` — overflow actions

Rendering is gated on `useIDEStore._hasHydrated` to prevent flash of unhydrated content.

Sources: [web/src/components/ui/markdown.tsx:1-113](), [web/src/components/ui/block-editor.tsx:1-179](), [web/src/components/mobile/MobileShell.tsx:1-74]()

---

## Providers

**Diagram: Provider wrapping order and responsibilities**

```mermaid
graph TD
  Root["app/layout.tsx (Root)"]
  Root --> PostHogProvider["PostHogProvider (posthog-js)"]
  PostHogProvider --> ThemeProvider["ThemeProvider (next-themes)"]
  ThemeProvider --> QueryProvider["QueryClientProvider (@tanstack/react-query)"]
  QueryProvider --> RealtimeProvider["RealtimeProvider (WebSocket events)"]
  RealtimeProvider --> Page["Page Content"]

  PostHogProvider --> PostHogPageView["PostHogPageView (route change capture)"]
  PostHogProvider --> PostHogIdentify["PostHogIdentify (user + org group)"]
```

**`PostHogProvider`** ([web/src/providers/PostHogProvider.tsx:79-89]()):
- Initializes PostHog with `advanced_disable_decide: true` to avoid polling `/flags` and `/config`
- `PostHogPageView` captures a `$pageview` event on every route change
- `PostHogIdentify` calls `ph.identify()` when `useAuthStore.user` changes, and `ph.group("organization", ...)` when `currentOrg` changes

Sources: [web/src/providers/PostHogProvider.tsx:1-89]()

---

## Main User Flows

```mermaid
flowchart LR
  Login["Login / Register\n(auth)/ routes"] --> OrgSelect["Select Organization\nuseAuthStore.currentOrg"]
  OrgSelect --> IDE["IDEShell\n(dashboard)/"]
  IDE --> Mesh["MeshPage\n@xyflow/react nodes"]
  IDE --> Terminal["TerminalPane\nuseTerminal + @xterm/xterm"]
  IDE --> Tickets["TicketsPage\nKanbanBoard"]
  IDE --> Channel["ChannelChatPanel\nchannelApi"]
  Terminal --> WS["TerminalConnectionPool\nWebSocket to Relay"]
  Mesh --> PodCreate["CreatePodModal\nPOST /api/v1/orgs/:slug/pods"]
  Tickets --> TicketDetail["TicketDetail\nBlockEditor + Markdown"]
```

| Flow | Entry Point | Key API |
|---|---|---|
| Authentication | `(auth)/login` | `POST /api/v1/auth/login` |
| Create pod | `CreatePodModal` | `POST /api/v1/orgs/:slug/pods` |
| Terminal session | `TerminalConnectionPool` | WebSocket via Relay |
| Ticket CRUD | `TicketsPage` / `TicketDetail` | `/api/v1/orgs/:slug/tickets` |
| Channel messaging | `ChannelChatPanel` | `/api/v1/orgs/:slug/channels` |
| Mesh topology | `MeshPage` | `/api/v1/orgs/:slug/mesh` |

Sources: [CLAUDE.md:135-171](), [web/src/lib/api/base.ts:164-172]()

---

## Development

The frontend runs locally (not in Docker) via Next.js with Turbopack:

```bash
cd web
pnpm install
pnpm dev          # starts on http://localhost:3000
```

API calls are proxied through Traefik to the backend (port configured in `deploy/dev/.env` as `HTTP_PORT`). In development, Next.js rewrites or the browser directly addresses `localhost:<HTTP_PORT>/api`. See [Environment and API Configuration](#5.6) for the full URL resolution logic.

Tests use Vitest and Testing Library:

```bash
pnpm test         # watch mode
pnpm test:run     # single run
pnpm test:coverage
```

Sources: [CLAUDE.md:76-86](), [web/package.json:5-14](), [deploy/dev/docker-compose.yml:245-247]()

---

# Page: Terminal Workspace

# Terminal Workspace

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [web/src/app/(dashboard)/[org]/mesh/page.tsx](web/src/app/(dashboard)/[org]/mesh/page.tsx)
- [web/src/app/(dashboard)/[org]/workspace/page.tsx](web/src/app/(dashboard)/[org]/workspace/page.tsx)
- [web/src/components/ide/CreatePodModal.tsx](web/src/components/ide/CreatePodModal.tsx)
- [web/src/components/ide/IDEShell.tsx](web/src/components/ide/IDEShell.tsx)
- [web/src/components/ide/SideBar.tsx](web/src/components/ide/SideBar.tsx)
- [web/src/components/ide/sidebar/MeshSidebarContent.tsx](web/src/components/ide/sidebar/MeshSidebarContent.tsx)
- [web/src/components/ide/sidebar/RunnersSidebarContent.tsx](web/src/components/ide/sidebar/RunnersSidebarContent.tsx)
- [web/src/components/mobile/MobileHeader.tsx](web/src/components/mobile/MobileHeader.tsx)
- [web/src/components/mobile/MobileSidebar.tsx](web/src/components/mobile/MobileSidebar.tsx)
- [web/src/components/settings/organization/RunnersSettings.tsx](web/src/components/settings/organization/RunnersSettings.tsx)
- [web/src/components/tickets/TicketPodPanel.tsx](web/src/components/tickets/TicketPodPanel.tsx)
- [web/src/components/workspace/TerminalPane.tsx](web/src/components/workspace/TerminalPane.tsx)
- [web/src/components/workspace/TerminalSwiper.tsx](web/src/components/workspace/TerminalSwiper.tsx)
- [web/src/components/workspace/TerminalTabs.tsx](web/src/components/workspace/TerminalTabs.tsx)
- [web/src/components/workspace/TerminalToolbar.tsx](web/src/components/workspace/TerminalToolbar.tsx)
- [web/src/components/workspace/WorkspaceManager.tsx](web/src/components/workspace/WorkspaceManager.tsx)
- [web/src/hooks/useTerminal.ts](web/src/hooks/useTerminal.ts)
- [web/src/stores/terminalConnection.ts](web/src/stores/terminalConnection.ts)
- [web/src/stores/workspace.ts](web/src/stores/workspace.ts)

</details>



This page documents the browser-side terminal workspace: how WebSocket connections to the Relay are managed, how xterm.js terminals are initialized and sized, and how multiple terminal panes are arranged in desktop and mobile layouts.

For information about the Relay service that the browser connects to, see [4](). For information about the runner-side PTY management, see [3.4](). For the AgentsMesh Network view that also embeds terminal access, see [5.3]().

---

## Overview

The terminal workspace has three layers:

1. **Connection layer** — `TerminalConnectionPool` in `web/src/stores/terminalConnection.ts` manages WebSocket connections to the Relay, implements the binary protocol, and allows multiple UI components to share a single connection per pod.
2. **Terminal layer** — `useTerminal` hook in `web/src/hooks/useTerminal.ts` creates an xterm.js instance, attaches addons, and wires the connection pool to the terminal display.
3. **Layout layer** — `WorkspaceManager` in `web/src/components/workspace/WorkspaceManager.tsx` renders desktop or mobile layouts (`TerminalTabs`+`TerminalGrid` or `TerminalSwiper`+`TerminalToolbar`), driven by `useWorkspaceStore`.

**Data flow:**
- Browser ↔ Relay (WebSocket, binary protocol) — terminal I/O
- Browser → Backend (REST `podApi.getTerminalConnection`) — obtain Relay URL and token
- Backend → Runner (gRPC) — control commands (resize, etc.) are forwarded via Relay

---

## TerminalConnectionPool

`TerminalConnectionPool` (a singleton exported as `terminalPool` from [web/src/stores/terminalConnection.ts:106-653]()) is the central connection manager.

### Connection Pooling Model

Connections are keyed by `podKey`. Multiple React components subscribe to the same connection using a stable `subscriptionId`. When the last subscriber leaves, the connection stays open for 30 seconds before being torn down (configurable via `disconnectDelay`).

**TerminalConnectionPool architecture diagram**

```mermaid
flowchart TD
    subgraph "TerminalConnectionPool (singleton: terminalPool)"
        CM["connections: Map[podKey, TerminalConnection]"]
        SL["statusListeners: Map[podKey, Set[StatusListener]]"]
        RI["resizeDebounceTimers: Map[podKey, timer]"]
        LI["lastInputs: Map[podKey, {data, time}]"]
    end

    subgraph "TerminalConnection"
        WS["ws: WebSocket"]
        SUB["subscribers: Map[subscriptionId, callback]"]
        STATUS["status: connecting|connected|disconnected|error"]
        RD["runnerDisconnected: boolean"]
        PR["pendingResize: {rows, cols}"]
    end

    CM -->|"per podKey"| TerminalConnection
    podApi["podApi.getTerminalConnection(podKey)"] -->|"relay_url + token"| CM

    useTerminal["useTerminal hook"] -->|"subscribe(podKey, subscriptionId, cb)"| CM
    TerminalTabs["TerminalTabs"] -->|"onStatusChange(podKey, listener)"| SL
```

Sources: [web/src/stores/terminalConnection.ts:106-170]()

### Binary Protocol (MsgType)

All WebSocket messages are prefixed with a 1-byte type code. The `MsgType` enum mirrors `relay/internal/protocol/message.go`.

| Constant | Value | Direction | Purpose |
|---|---|---|---|
| `Snapshot` | `0x01` | Relay → Browser | Full terminal state snapshot (JSON, includes `serialized_content`) |
| `Output` | `0x02` | Relay → Browser | Raw PTY output bytes |
| `Input` | `0x03` | Browser → Relay | Keyboard/paste input |
| `Resize` | `0x04` | Browser → Relay | Terminal resize (4 bytes: `cols uint16 BE`, `rows uint16 BE`) |
| `Ping` | `0x05` | Either | Keepalive ping |
| `Pong` | `0x06` | Either | Keepalive pong |
| `Control` | `0x07` | Relay → Browser | JSON control messages (e.g., `pty_resized`) |
| `RunnerDisconnected` | `0x08` | Relay → Browser | Runner disconnected notification |
| `RunnerReconnected` | `0x09` | Relay → Browser | Runner reconnected notification |
| `ImagePaste` | `0x0a` | Browser → Relay | Image paste (mime-type length byte + mime-type + image data) |

Sources: [web/src/stores/terminalConnection.ts:17-28]()

`encodeMessage(msgType, payload)` prepends the type byte. `decodeMessage(data)` strips it. See [web/src/stores/terminalConnection.ts:67-88]().

### subscribe() and Connection Lifecycle

**Connection lifecycle diagram**

```mermaid
sequenceDiagram
    participant C as "Component"
    participant P as "terminalPool"
    participant API as "podApi.getTerminalConnection"
    participant WS as "WebSocket (Relay)"

    C->>P: "subscribe(podKey, subscriptionId, onMessage)"
    alt "connection exists, same subscriptionId"
        P-->>C: "update callback (idempotent)"
    else "connection exists, new subscriptionId"
        P->>P: "disconnect(podKey) — force reconnect for buffer replay"
        P->>API: "getTerminalConnection(podKey)"
        API-->>P: "{relay_url, token}"
        P->>WS: "new WebSocket(relay_url/browser/terminal?token=...)"
        P-->>C: "ConnectionHandle {send, unsubscribe}"
    else "no connection"
        P->>API: "getTerminalConnection(podKey)"
        API-->>P: "{relay_url, token}"
        P->>WS: "new WebSocket(...)"
        P-->>C: "ConnectionHandle {send, unsubscribe}"
    end

    WS-->>P: "onopen → status=connected"
    WS-->>P: "onmessage → handleRelayMessage → dispatch to subscribers"
    WS-->>P: "onclose → scheduleReconnect"

    C->>P: "unsubscribe(podKey, subscriptionId)"
    P->>P: "schedule disconnect after 30s if no subscribers remain"
```

Sources: [web/src/stores/terminalConnection.ts:180-237](), [web/src/stores/terminalConnection.ts:524-539]()

### Reconnection

On `onclose` or `onerror`, `scheduleReconnect` applies exponential backoff with ±20% jitter up to 30 seconds, retrying up to `maxReconnectAttempts` (5). On reconnect, all existing subscribers are preserved and re-attached to the new WebSocket. See [web/src/stores/terminalConnection.ts:584-633]().

### Input Deduplication

For multi-character inputs (e.g., IME composed strings), if the same string is sent within 50 ms, the second send is dropped. This prevents duplicate input on mobile with network latency. Single characters bypass deduplication. See [web/src/stores/terminalConnection.ts:414-432]().

### Resize Debouncing

`sendResize` debounces by 150 ms. `forceResize` bypasses debounce. If the WebSocket is still `CONNECTING`, the resize is queued as `pendingResize` and sent on `onopen`. See [web/src/stores/terminalConnection.ts:451-510]().

### Status Change Events

`onStatusChange(podKey, listener)` registers a listener that fires immediately with the current `RelayStatusInfo` and on every subsequent change. Components use this to reactively update connection status UI. See [web/src/stores/terminalConnection.ts:132-153]().

---

## useTerminal Hook

`useTerminal` in [web/src/hooks/useTerminal.ts]() creates and manages an xterm.js terminal bound to a DOM element. It is the main integration point between the connection pool and the rendered terminal.

### Signature

```
useTerminal(podKey: string, fontSize: number, isPodReady: boolean, isActive: boolean): UseTerminalResult
```

Returns `{ terminalRef, xtermRef, fitAddonRef, connectionStatus, isRunnerDisconnected, syncSize }`.

### Initialization sequence

**useTerminal initialization diagram**

```mermaid
flowchart TD
    A["isPodReady = true AND terminalRef.current set"] --> B["new XTerm({cursorBlink, fontFamily, theme: TERMINAL_THEME})"]
    B --> C["loadAddon: FitAddon, WebLinksAddon, SearchAddon"]
    C --> D["term.open(terminalRef.current)"]
    D --> E["requestAnimationFrame → safeFit(fitAddon) → initialDims"]
    E --> F["new TerminalWriteScheduler → scheduler.attach(term)"]
    F --> G["terminalPool.subscribe(podKey, subscriptionId, handleMessage)"]
    G --> H["terminalPool.forceResize(podKey, initialDims.cols, initialDims.rows)"]
    H --> I["terminalPool.onStatusChange → setConnectionStatus, setIsRunnerDisconnected"]
    I --> J["term.onData → connectionRef.current.send(data)"]
    J --> K["term.onResize → terminalPool.sendResize"]
    K --> L["new ResizeObserver → safeFit → debouncedSizeSync"]
    L --> M["terminalRegistry.register(podKey, term)"]
```

Sources: [web/src/hooks/useTerminal.ts:136-399]()

### Key design decisions

| Decision | Implementation |
|---|---|
| Stable `subscriptionId` | `"terminal-${podKey}"` — prevents WebSocket teardown on React StrictMode remount |
| AbortController | Prevents a late-resolving `subscribe()` from storing a stale handle if the effect cleaned up first |
| `TerminalWriteScheduler` | Batches `xterm.write()` calls into animation frames, reducing call rate from thousands/s to ~60/s |
| `safeFit` | Checks `proposeDimensions()` before calling `fitAddon.fit()` to guard against zero-size containers |
| `debouncedSizeSync` vs `forceImmediateSizeSync` | Resize events use debounce (100ms); pane activation and initial connect use force-immediate |
| IME composition guard | `compositionstart`/`compositionend` listeners set `isComposing`; `onData` skips if composing |
| Image paste | Intercepts `ClipboardEvent` on terminal container for `image/*` MIME types, sends via `terminalPool.sendImage` |
| Page visibility | On `visibilitychange → visible`, re-fits and debounced-syncs size |
| Font size changes | Handled in a separate `useEffect` with `fontSize` dep; does not recreate the terminal |

Sources: [web/src/hooks/useTerminal.ts:192-231](), [web/src/hooks/useTerminal.ts:233-290](), [web/src/hooks/useTerminal.ts:291-325](), [web/src/hooks/useTerminal.ts:404-471]()

### Terminal Theme

`TERMINAL_THEME` in [web/src/hooks/useTerminal.ts:29-51]() sets a VS Code dark-compatible colour scheme (background `#1e1e1e`, foreground `#d4d4d4`, selection `#264f78`).

---

## TerminalPane Component

`TerminalPane` in [web/src/components/workspace/TerminalPane.tsx]() is the top-level UI component for a single terminal session. It composes `useTerminal`, pod status tracking, and autopilot overlays.

### Props

| Prop | Type | Description |
|---|---|---|
| `paneId` | `string` | Unique workspace pane identifier |
| `podKey` | `string` | Pod key, passed to `useTerminal` and `terminalPool` |
| `isActive` | `boolean` | Whether this pane is the focused pane |
| `onClose` | `() => void` | Callback when user closes the pane |
| `showHeader` | `boolean` | Show/hide `TerminalPaneHeader` (default: true) |

### Render logic

```mermaid
flowchart TD
    A["TerminalPane render"] --> B{"wasEverReady (sticky flag)"}
    B -->|false| C{"podError?"}
    C -->|yes| D["TerminalErrorState"]
    C -->|no| E["TerminalLoadingState (with initProgress bar)"]
    B -->|true| F["showTerminal = true"]
    F --> G{"autopilotController?"}
    G -->|yes| H["TakeoverBanner + CircuitBreakerAlert + AutopilotStatusBar"]
    G -->|no| I["(none)"]
    H --> J["RelayStatusOverlay (floating)"]
    I --> J
    J --> K["div ref=terminalRef (xterm renders here)"]
```

The "sticky ready" flag (`wasEverReady`) is important: once the terminal was ever visible, transient pod status regressions do not unmount it. See [web/src/components/workspace/TerminalPane.tsx:88-92]().

`RelayStatusOverlay` shows a floating banner when `connectionStatus !== 'connected'` or `isRunnerDisconnected === true`.

Sources: [web/src/components/workspace/TerminalPane.tsx:130-215]()

---

## useWorkspaceStore

`useWorkspaceStore` in [web/src/stores/workspace.ts:90-233]() is a persisted Zustand store managing pane layout state.

### State shape

| Field | Type | Description |
|---|---|---|
| `panes` | `TerminalPane[]` | Ordered list of open panes |
| `activePane` | `string \| null` | `paneId` of the focused pane |
| `gridLayout` | `GridLayout` | Desktop grid: `{ type: "1x1"|"1x2"|"2x1"|"2x2"|"custom", rows, cols }` |
| `mobileActiveIndex` | `number` | Index of the visible pane on mobile |
| `terminalFontSize` | `number` | Font size in pixels (clamped 10–24, default 14) |

### Key actions

| Action | Behaviour |
|---|---|
| `addPane(podKey)` | Adds pane or activates existing pane for `podKey`; returns `paneId` |
| `removePane(paneId)` | Removes pane; adjusts `activePane` and `mobileActiveIndex` |
| `setActivePane(paneId)` | Sets active pane and syncs `mobileActiveIndex` |
| `setGridLayout(layout)` | Changes grid layout |
| `setTerminalFontSize(size)` | Clamps and sets font size |

Persistence key is `"agentsmesh-workspace"` (localStorage via `zustand/persist`). Version 2 migration removes obsolete `title` and `isActive` fields from persisted panes. See [web/src/stores/workspace.ts:200-232]().

### TerminalRegistry

`TerminalRegistry` in [web/src/stores/workspace.ts:12-35]() is a simple `Map<podKey, XTerm>` for cross-component access to xterm instances. `useTerminal` registers on mount and unregisters on cleanup. `TerminalToolbar` uses it via `terminalRegistry.scrollToBottom(podKey)`.

Sources: [web/src/stores/workspace.ts:1-35]()

---

## Workspace Layout

`WorkspaceManager` in [web/src/components/workspace/WorkspaceManager.tsx]() selects desktop or mobile layout based on `useBreakpoint().isMobile`.

### Layout selection diagram

```mermaid
flowchart LR
    WM["WorkspaceManager"] --> BP{"isMobile"}
    BP -->|false| DK["Desktop layout"]
    BP -->|true| MB["Mobile layout"]

    DK --> TT["TerminalTabs (tab bar + layout switcher)"]
    DK --> TG["TerminalGrid (renders TerminalPane per pane)"]

    MB --> TS["TerminalSwiper (swipe between panes)"]
    MB --> TB["TerminalToolbar (floating keyboard toolbar)"]
```

Sources: [web/src/components/workspace/WorkspaceManager.tsx:91-128]()

### Desktop: TerminalTabs

`TerminalTabs` in [web/src/components/workspace/TerminalTabs.tsx]() renders:
- One tab per pane with a reactive `ConnectionDot` (green/yellow/red/gray) driven by `terminalPool.onStatusChange`.
- A `+` button to open the pod selector modal.
- Layout controls: 1×1, 1×2 (columns), 2×1 (rows), 2×2 grid, and fullscreen toggle.

`ConnectionDot` subscribes to `terminalPool.onStatusChange` in a `useEffect`, which fires immediately with current status. See [web/src/components/workspace/TerminalTabs.tsx:163-181]().

### Mobile: TerminalSwiper

`TerminalSwiper` in [web/src/components/workspace/TerminalSwiper.tsx]() renders one `TerminalPane` at a time and supports horizontal swipe to switch between panes using `@use-gesture/react`'s `useDrag`. It uses `axis: "lock"` mode to avoid conflicting with vertical terminal scrolling. If horizontal drag > 50px or velocity > 0.5, it advances/retreats the index. See [web/src/components/workspace/TerminalSwiper.tsx:32-83]().

### Mobile: TerminalToolbar

`TerminalToolbar` in [web/src/components/workspace/TerminalToolbar.tsx]() is a floating keyboard toolbar with two rows of keys. It sends raw escape sequences directly via `terminalPool.send`. It supports toggleable `CTRL` and `ALT` modifier states (Blink Shell–style: modifiers are consumed on the next key press and reset). Special keys include ESC, Ctrl+C/D/Z, arrow keys, HOME/END, PgUp/PgDn, TAB, and common symbols.

---

## Component Dependency Map

**Component and store dependency diagram**

```mermaid
flowchart TD
    WP["workspace/page.tsx"] --> WM["WorkspaceManager"]
    WM --> TT["TerminalTabs"]
    WM --> TG["TerminalGrid"]
    WM --> TS["TerminalSwiper"]
    WM --> TB["TerminalToolbar"]
    WM --> useWorkspaceStore["useWorkspaceStore"]

    TT --> useWorkspaceStore
    TT --> terminalPool["terminalPool (TerminalConnectionPool)"]
    TG --> TP["TerminalPane"]
    TS --> TP
    TB --> terminalPool
    TB --> terminalRegistry["terminalRegistry (TerminalRegistry)"]

    TP --> useTerminal["useTerminal hook"]
    TP --> usePodStatus["usePodStatus hook"]
    TP --> useWorkspaceStore
    TP --> useAutopilotStore["useAutopilotStore"]

    useTerminal --> terminalPool
    useTerminal --> terminalRegistry
    useTerminal --> XTerm["XTerm + FitAddon + WebLinksAddon + SearchAddon"]
    useTerminal --> TerminalWriteScheduler["TerminalWriteScheduler"]

    terminalPool --> podApi["podApi.getTerminalConnection"]
    terminalPool --> WebSocket["WebSocket → Relay /browser/terminal"]
```

Sources: [web/src/components/workspace/WorkspaceManager.tsx](), [web/src/components/workspace/TerminalPane.tsx](), [web/src/hooks/useTerminal.ts](), [web/src/stores/terminalConnection.ts](), [web/src/stores/workspace.ts]()

---

## Workspace Page

`WorkspacePage` in [web/src/app/(dashboard)/[org]/workspace/page.tsx]() is the Next.js route component for the `/[org]/workspace` path. It:

1. Waits for `useWorkspaceStore._hasHydrated` before rendering.
2. Handles the `?pod=xxx` query parameter: if a pod key is present and not already open, calls `addPane(podKey)` and replaces the URL to prevent re-opening on refresh.
3. Shows an empty state with a **Create Pod** button when `panes.length === 0`.
4. Renders `WorkspaceManager` when panes exist.

Sources: [web/src/app/(dashboard)/[org]/workspace/page.tsx]()

---

## Opening a Terminal from Other Views

Pods can be opened in the workspace terminal from other parts of the application:

| Source | Mechanism |
|---|---|
| `TicketPodPanel` | Calls `addPane(pod.pod_key)` then `router.push(".../workspace")` on "Connect" click |
| `IDEShell` / `MobileSidebar` | After pod creation via `CreatePodModal`, calls `addPane(pod.pod_key)` |
| `MeshSidebarContent` | "Open terminal" button calls `addPane(podKey)` then navigates to workspace |
| Query param `?pod=` | `WorkspacePage` reads `searchParams.get("pod")` and calls `addPane` |

Sources: [web/src/components/tickets/TicketPodPanel.tsx:181-185](), [web/src/components/ide/IDEShell.tsx:99-109](), [web/src/components/ide/sidebar/MeshSidebarContent.tsx:106-110](), [web/src/app/(dashboard)/[org]/workspace/page.tsx:25-47]()

---

# Page: Ticket Management

# Ticket Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [web/src/app/(dashboard)/[org]/tickets/components/BoardViewLayout.tsx](web/src/app/(dashboard)/[org]/tickets/components/BoardViewLayout.tsx)
- [web/src/app/(dashboard)/[org]/tickets/components/ListViewLayout.tsx](web/src/app/(dashboard)/[org]/tickets/components/ListViewLayout.tsx)
- [web/src/app/(dashboard)/[org]/tickets/page.tsx](web/src/app/(dashboard)/[org]/tickets/page.tsx)
- [web/src/components/billing/CancelSubscriptionDialog.tsx](web/src/components/billing/CancelSubscriptionDialog.tsx)
- [web/src/components/settings/organization/__tests__/APIKeysSettings.test.tsx](web/src/components/settings/organization/__tests__/APIKeysSettings.test.tsx)
- [web/src/components/tickets/KanbanBoard.tsx](web/src/components/tickets/KanbanBoard.tsx)
- [web/src/components/tickets/TicketCreateDialog.tsx](web/src/components/tickets/TicketCreateDialog.tsx)
- [web/src/components/tickets/TicketDetail.tsx](web/src/components/tickets/TicketDetail.tsx)
- [web/src/components/tickets/TicketDetailPane.tsx](web/src/components/tickets/TicketDetailPane.tsx)
- [web/src/components/tickets/TicketDetailSidebar.tsx](web/src/components/tickets/TicketDetailSidebar.tsx)
- [web/src/components/tickets/__tests__/TicketCard.test.tsx](web/src/components/tickets/__tests__/TicketCard.test.tsx)
- [web/src/components/tickets/__tests__/TicketCreateDialog.test.tsx](web/src/components/tickets/__tests__/TicketCreateDialog.test.tsx)
- [web/src/components/tickets/__tests__/TicketDetail.test.tsx](web/src/components/tickets/__tests__/TicketDetail.test.tsx)
- [web/src/components/tickets/index.ts](web/src/components/tickets/index.ts)
- [web/src/components/ui/__tests__/responsive-dialog.test.tsx](web/src/components/ui/__tests__/responsive-dialog.test.tsx)
- [web/src/components/ui/responsive-dialog.tsx](web/src/components/ui/responsive-dialog.tsx)
- [web/src/components/workspace/TerminalStateViews.tsx](web/src/components/workspace/TerminalStateViews.tsx)
- [web/src/components/workspace/__tests__/TerminalStateViews.test.tsx](web/src/components/workspace/__tests__/TerminalStateViews.test.tsx)
- [web/src/lib/api/ticket.ts](web/src/lib/api/ticket.ts)
- [web/src/stores/__tests__/ticket.test.ts](web/src/stores/__tests__/ticket.test.ts)
- [web/src/stores/ticket.ts](web/src/stores/ticket.ts)

</details>



This page documents the ticket management UI in the web frontend: the data model, Zustand store, REST API client, page layout, board and list views, ticket detail view, creation dialog, and keyboard navigation. Ticket management concerns everything under the `/(dashboard)/[org]/tickets` route.

For backend ticket persistence and querying, see [2.5](). For real-time ticket updates delivered via WebSocket, see [5.5](). For pod creation that can be triggered from a ticket, see [5.3]().

---

## Data Model

Ticket data types are defined in [web/src/lib/api/ticket.ts]() and re-exported from [web/src/stores/ticket.ts]().

| Type | Values | Notes |
|------|--------|-------|
| `TicketStatus` | `backlog`, `todo`, `in_progress`, `in_review`, `done` | Maps directly to backend enum |
| `TicketPriority` | `none`, `low`, `medium`, `high`, `urgent` | Controls sort/display order |

The core shape is `TicketData` [web/src/lib/api/ticket.ts:7-32]():

| Field | Type | Description |
|-------|------|-------------|
| `id` | `number` | Internal DB id |
| `number` | `number` | Sequential per-org number |
| `slug` | `string` | Human-readable id, e.g. `PROJ-42` |
| `title` | `string` | Short title |
| `content` | `string?` | Rich text body (block editor JSON) |
| `status` | `TicketStatus` | Current workflow state |
| `priority` | `TicketPriority` | Urgency level |
| `due_date` | `string?` | ISO date string |
| `assignees` | `Array<{user_id, user}>?` | Organization members assigned |
| `labels` | `Array<{id, name, color}>?` | Color-tagged categories |
| `repository_id` | `number?` | Linked git repository |
| `parent_ticket` | `{id, slug, title}?` | Parent if this is a sub-ticket |

The store's `Ticket` interface extends `TicketData` with an optional `child_tickets` field for nested sub-tickets.

---

## `useTicketStore` — Zustand Store

**Source:** [web/src/stores/ticket.ts]()

All ticket state is managed by a single Zustand store created with `create<TicketState>`. Components use individual selectors (`useTicketStore(state => state.X)`) to avoid unnecessary re-renders from unrelated state changes.

**State Model:**

```
TicketState
├── tickets: Ticket[]            -- flat list loaded by fetchTickets()
├── currentTicket: Ticket|null   -- loaded by fetchTicket(slug)
├── selectedTicketSlug: string|null  -- lightweight selection (no fetch)
├── labels: Label[]
├── filters: TicketFilters       -- server-side filter params
├── uiFilters: TicketUIFilters   -- client-side multi-select (status, priority)
├── viewMode: "list" | "board"
├── loading: boolean
├── error: string|null
└── totalCount: number
```

**Key actions:**

| Action | Description |
|--------|-------------|
| `fetchTickets(filters?)` | Calls `ticketApi.list()`, merges with existing filters |
| `fetchTicket(slug)` | Calls `ticketApi.get(slug)`, sets `currentTicket` |
| `createTicket(data)` | Calls `ticketApi.create()`, prepends to `tickets` |
| `updateTicket(slug, data)` | Calls `ticketApi.update()`, patches in-place |
| `updateTicketStatus(slug, status)` | Optimistic update → `ticketApi.updateStatus()`, rollback on failure |
| `deleteTicket(slug)` | Calls `ticketApi.delete()`, removes from `tickets` |
| `toggleStatus(status)` | Toggles `uiFilters.selectedStatuses` (multi-select) |
| `togglePriority(priority)` | Toggles `uiFilters.selectedPriorities` |
| `clearUIFilters()` | Resets both UI filter arrays |
| `setViewMode(mode)` | Switches between `"list"` and `"board"` |

**`useFilteredTickets` selector** [web/src/stores/ticket.ts:303-322]():

A derived selector hook that applies UI filters (search text, selected statuses, selected priorities) client-side via `useMemo`. This is the single source of truth for what tickets are displayed — used by both list and board views.

**Status/priority display helpers:**

- `getStatusInfo(status: TicketStatus)` — returns `{label, color, bgColor}`
- `getPriorityInfo(priority: TicketPriority)` — returns `{label, color, icon}`

Sources: [web/src/stores/ticket.ts]()

---

## `ticketApi` — REST API Client

**Source:** [web/src/lib/api/ticket.ts:76-400]()

All calls go through `request()` with `orgPath("/tickets")` as the base path. The `orgPath` helper prefixes the current organization slug from the auth context.

**Architecture diagram — `ticketApi` methods to backend endpoints:**

```mermaid
graph LR
  subgraph "ticketApi (web/src/lib/api/ticket.ts)"
    L["list(filters)"]
    G["get(slug)"]
    C["create(data)"]
    U["update(slug,data)"]
    D["delete(slug)"]
    US["updateStatus(slug,status)"]
    GST["getSubTickets(slug)"]
    GR["listRelations(slug)"]
    GC["listComments(slug)"]
    GP["getPods(slug)"]
    CP["createPod(slug,data)"]
    BA["batchGetPods(ids)"]
  end

  subgraph "Backend REST"
    E1["GET /tickets"]
    E2["GET /tickets/:slug"]
    E3["POST /tickets"]
    E4["PUT /tickets/:slug"]
    E5["DELETE /tickets/:slug"]
    E6["PATCH /tickets/:slug/status"]
    E7["GET /tickets/:slug/sub-tickets"]
    E8["GET /tickets/:slug/relations"]
    E9["GET /tickets/:slug/comments"]
    E10["GET /tickets/:slug/pods"]
    E11["POST /tickets/:slug/pods"]
    E12["POST /tickets/batch-pods"]
  end

  L --> E1
  G --> E2
  C --> E3
  U --> E4
  D --> E5
  US --> E6
  GST --> E7
  GR --> E8
  GC --> E9
  GP --> E10
  CP --> E11
  BA --> E12
```

Sources: [web/src/lib/api/ticket.ts]()

---

## `TicketsPage` — Route Entry Point

**Source:** [web/src/app/(dashboard)/[org]/tickets/page.tsx]()

This is the `"use client"` Next.js page component rendered at `/:org/tickets`. It orchestrates:

1. Fetching tickets via `fetchTickets()` on mount (with local loading state separate from store's shared `loading`)
2. Reading the filtered ticket list from `useFilteredTickets()`
3. Dispatching to either `ListViewLayout` or `BoardViewLayout` based on `viewMode`
4. Rendering `TicketKeyboardHandler` for J/K keyboard navigation
5. Managing the `CreatePodModal` that auto-opens when a ticket is dragged to `in_progress` on the board

**Data flow:**

```mermaid
flowchart TD
  P["TicketsPage"] --> F["fetchTickets() on mount"]
  F --> S["useTicketStore.tickets"]
  S --> FT["useFilteredTickets()"]
  FT --> VM{"viewMode"}
  VM -- "list" --> LV["ListViewLayout"]
  VM -- "board" --> BV["BoardViewLayout → KanbanBoard"]
  P --> KH["TicketKeyboardHandler"]
  BV -- "drag to in_progress" --> CPM["CreatePodModal"]
```

Sources: [web/src/app/(dashboard)/[org]/tickets/page.tsx]()

---

## Views

### List View

**Source:** [web/src/app/(dashboard)/[org]/tickets/components/ListViewLayout.tsx]()

`ListViewLayout` checks `tickets.length` against `VIRTUALIZATION_THRESHOLD = 50`. Below the threshold it renders `TicketListView`; above it renders `VirtualizedTicketList` (a windowed list) to handle large datasets efficiently.

Clicking a ticket navigates directly to `/:org/tickets/:slug` (no split pane).

### Board View — `KanbanBoard`

**Source:** [web/src/components/tickets/KanbanBoard.tsx]()

Renders a horizontal scroll of five `DroppableColumn` components, one per `TicketStatus`. Uses `@dnd-kit/core` for drag-and-drop.

**Column configuration:**

| Status | Color bar |
|--------|-----------|
| `backlog` | Gray |
| `todo` | Blue |
| `in_progress` | Yellow |
| `in_review` | Purple |
| `done` | Green |

**DnD architecture:**

```mermaid
graph TD
  subgraph "KanbanBoard"
    DC["DndContext (sensors: Mouse, Touch, Keyboard)"]
    DO["DragOverlay"]
  end
  DC --> COL1["DroppableColumn (backlog)"]
  DC --> COL2["DroppableColumn (todo)"]
  DC --> COL3["DroppableColumn (in_progress)"]
  DC --> COL4["DroppableColumn (in_review)"]
  DC --> COL5["DroppableColumn (done)"]
  COL1 --> SC1["SortableContext → SortableTicket[]"]
  DC -- "onDragEnd" --> OSC["onStatusChange(slug, newStatus)"]
  DC -- "in_progress drag from backlog/todo" --> CPR["onCreatePodRequest(ticket)"]
```

- `SortableTicket` wraps `TicketCard` with `useSortable` from `@dnd-kit/sortable`.
- Collision detection uses a custom strategy: pointer-within columns takes priority, falling back to rect-intersection against ticket cards which then resolves to the card's owning column.
- When a ticket is dragged from `backlog` or `todo` into `in_progress`, `onCreatePodRequest` fires — this triggers `CreatePodModal` in `TicketsPage`.
- `useTicketPrefetch` is called `onMouseEnter` for each card to prefetch ticket data before the user navigates.

Sources: [web/src/components/tickets/KanbanBoard.tsx](), [web/src/app/(dashboard)/[org]/tickets/components/BoardViewLayout.tsx]()

---

## `TicketDetail` — Full Page Detail View

**Source:** [web/src/components/tickets/TicketDetail.tsx]()

Rendered at `/:org/tickets/:slug`. Fetches the ticket via `fetchTicket(slug)` and uses individual store selectors to avoid re-renders from unrelated store changes (e.g., a WebSocket event calling `fetchTickets()` would not re-render the detail view).

**Layout:** Two-column on desktop (`flex-row`), stacked on mobile (`flex-col`).

- **Left column (main content):**
  - `InlineEditableText` — click-to-edit title, saves on blur with `updateTicket(slug, {title})`
  - `LabelsList` — colored label chips
  - `BlockEditor` (lazy-loaded) — rich text body, debounced auto-save at 800ms via `contentSaveTimerRef`
  - `SubTicketsList`, `RelationsList`, `CommitsList` — linked entities
  - `CommentsList` — hidden on mobile (shown in sidebar slot instead)

- **Right column (`TicketDetailSidebar`):**
  - Pod execution panel (`SidebarPodSection`)
  - Properties panel: status, priority, due date, assignees, timestamps
  - Delete button with `ConfirmDialog`

**State management pattern:**

`TicketDetail` uses a local `loadedSlug` state (rather than the store's shared `loading` flag) to determine initial loading. This prevents the skeleton from re-appearing when unrelated WebSocket events trigger `fetchTickets()`.

```mermaid
sequenceDiagram
  participant Browser
  participant TicketDetail
  participant useTicketStore
  participant ticketApi
  participant Backend

  Browser->>TicketDetail: render(slug)
  TicketDetail->>useTicketStore: fetchTicket(slug)
  useTicketStore->>ticketApi: get(slug)
  ticketApi->>Backend: GET /tickets/:slug
  Backend-->>ticketApi: {ticket}
  ticketApi-->>useTicketStore: ticket
  useTicketStore-->>TicketDetail: currentTicket updated
  TicketDetail->>Browser: render title + BlockEditor

  Browser->>TicketDetail: user edits content
  TicketDetail->>TicketDetail: debounce 800ms
  TicketDetail->>useTicketStore: updateTicket(slug, {content})
  useTicketStore->>ticketApi: update(slug, {content})
  ticketApi->>Backend: PUT /tickets/:slug
```

Sources: [web/src/components/tickets/TicketDetail.tsx]()

---

## `TicketDetailSidebar` — Properties and Pod Panel

**Source:** [web/src/components/tickets/TicketDetailSidebar.tsx]()

The sidebar has two main sections:

### `SidebarPodSection`

Calls `ticketApi.getPods(ticketSlug)` on mount. Displays pods in two groups:

- **Active pods** — status `running` or `initializing` — shown with a pulsing indicator dot and hover actions (connect terminal, open in new tab)
- **Inactive/previous pods** — collapsed inside a `<details>` element

| Pod Status | Dot style |
|-----------|-----------|
| `running` | Green, animated pulse |
| `initializing` | Yellow, animated pulse |
| `failed` | Red, static |
| Other | Gray, static |

Clicking "Execute" opens `CreatePodModal` with `ticketContext` pre-filled. The "Connect" action calls `addPane(podKey)` from `useWorkspaceStore` then navigates to `/:org/workspace`.

### Properties Panel

Inline property rows using `StatusSelect` and `PrioritySelect` dropdowns. Changes call back to `TicketDetail`'s `handleStatusChange` / `handlePriorityChange`, which dispatch to the store.

Sources: [web/src/components/tickets/TicketDetailSidebar.tsx]()

---

## `TicketDetailPane` — Inline Side Panel

**Source:** [web/src/components/tickets/TicketDetailPane.tsx]()

A lighter-weight ticket view used in the mesh/IDE shell (see [5.3]()) where clicking a ticket opens a panel rather than navigating away. It:

- First checks `useTicketStore.tickets` for a cached ticket (for instant display)
- Falls back to `ticketApi.get(slug)` if not cached
- Skips the API fetch if the ticket is absent from the store (e.g., deleted)
- Uses `BlockViewer` (read-only) instead of `BlockEditor`
- Supports inline title editing, status/priority selects, and repository reassignment
- Embeds `TicketPodPanel`
- Has a footer link to navigate to the full detail page

Sources: [web/src/components/tickets/TicketDetailPane.tsx]()

---

## `TicketCreateDialog` — Creation Form

**Source:** [web/src/components/tickets/TicketCreateDialog.tsx]()

A `ResponsiveDialog` (modal on desktop, bottom drawer on mobile via `vaul`) with these fields:

| Field | Component | Default |
|-------|-----------|---------|
| Title | `<Input>` (required) | — |
| Priority | `<Select>` | `medium` |
| Assignees | Custom dropdown with checkboxes | none |
| Content | `BlockEditor` (lazy-loaded) | — |

**Form state** is held in a local `form: FormData` object. On submit, it calls `ticketApi.create()` directly (not through the store action) and invokes the `onCreated(id, slug)` callback.

When `parentTicketSlug` is provided, the dialog title changes to "Create Sub-ticket" and `parentSlug` is passed to `ticketApi.create()`.

**Mobile vs desktop rendering** is controlled by `useBreakpoint()`. On mobile, the `BlockEditor` uses a shorter `min-h-[100px]`; on desktop it uses `min-h-[150px]`. The footer reverses button order on mobile via `flex-col-reverse`.

Sources: [web/src/components/tickets/TicketCreateDialog.tsx]()

---

## Keyboard Navigation — `TicketKeyboardHandler`

**Source:** [web/src/components/tickets/index.ts:14]() (exported from `TicketKeyboardHandler.tsx`)

`TicketsPage` renders `TicketKeyboardHandler` as a sibling to the view layout. It handles global `keydown` events when `enabled` is true:

| Key | Action |
|-----|--------|
| `j` / `ArrowDown` | Move selection to next ticket |
| `k` / `ArrowUp` | Move selection to previous ticket |
| `Enter` | Navigate to selected ticket's detail page (`onOpenDetail`) |
| `Escape` | Clear selection (`onCloseDetail`) |

`keyboardSelectedSlug` is kept in `TicketsPage` local state (not the store). It controls a highlight style on the focused ticket card but does not perform navigation on its own — only `Enter` navigates.

---

## `useTicketExtraData` Hook

**Source:** [web/src/components/tickets/index.ts:28]() (from `hooks.ts`)

A shared hook used by both `TicketDetail` and `TicketDetailPane`. When `enabled` is true (i.e., the ticket is loaded), it fetches in parallel:

- `ticketApi.getSubTickets(slug)` → `subTickets`
- `ticketApi.listRelations(slug)` → `relations`
- `ticketApi.listCommits(slug)` → `commits`
- `ticketApi.listComments(slug)` → `comments`

Also exposes `addComment`, `updateComment`, `deleteComment` handlers.

---

## Component Map

```mermaid
graph TD
  subgraph "Route: /:org/tickets"
    TP["TicketsPage\n(page.tsx)"]
    KH["TicketKeyboardHandler"]
    LVL["ListViewLayout"]
    BVL["BoardViewLayout"]
    KB["KanbanBoard"]
    CPM["CreatePodModal"]
  end

  subgraph "Route: /:org/tickets/:slug"
    TD["TicketDetail\n(TicketDetail.tsx)"]
    TDS["TicketDetailSidebar\n(TicketDetailSidebar.tsx)"]
    SPS["SidebarPodSection"]
    BE["BlockEditor (lazy)"]
    IL["InlineEditableText"]
    CD["ConfirmDialog"]
  end

  subgraph "Shared Panels"
    TDP["TicketDetailPane\n(TicketDetailPane.tsx)"]
    TCD["TicketCreateDialog\n(TicketCreateDialog.tsx)"]
  end

  subgraph "State"
    UTS["useTicketStore\n(stores/ticket.ts)"]
    UFT["useFilteredTickets()"]
  end

  subgraph "API"
    TA["ticketApi\n(lib/api/ticket.ts)"]
  end

  TP --> KH
  TP --> LVL
  TP --> BVL
  BVL --> KB
  TP --> CPM
  TP --> UTS
  UFT --> TP

  TD --> TDS
  TD --> SPS
  TD --> BE
  TD --> IL
  TD --> CD
  TD --> UTS

  TDS --> SPS
  SPS --> TA

  UTS --> TA
  TDP --> TA
  TCD --> TA
```

Sources: [web/src/components/tickets/index.ts](), [web/src/app/(dashboard)/[org]/tickets/page.tsx](), [web/src/components/tickets/TicketDetail.tsx](), [web/src/components/tickets/TicketDetailSidebar.tsx](), [web/src/components/tickets/TicketDetailPane.tsx](), [web/src/components/tickets/TicketCreateDialog.tsx](), [web/src/stores/ticket.ts](), [web/src/lib/api/ticket.ts]()

---

# Page: AgentsMesh Network View

# AgentsMesh Network View

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/internal/service/mesh/service.go](backend/internal/service/mesh/service.go)
- [web/src/app/(dashboard)/[org]/mesh/page.tsx](web/src/app/(dashboard)/[org]/mesh/page.tsx)
- [web/src/components/ide/CreatePodModal.tsx](web/src/components/ide/CreatePodModal.tsx)
- [web/src/components/ide/IDEShell.tsx](web/src/components/ide/IDEShell.tsx)
- [web/src/components/ide/SideBar.tsx](web/src/components/ide/SideBar.tsx)
- [web/src/components/ide/sidebar/MeshSidebarContent.tsx](web/src/components/ide/sidebar/MeshSidebarContent.tsx)
- [web/src/components/ide/sidebar/RunnersSidebarContent.tsx](web/src/components/ide/sidebar/RunnersSidebarContent.tsx)
- [web/src/components/settings/organization/RunnersSettings.tsx](web/src/components/settings/organization/RunnersSettings.tsx)
- [web/src/components/tickets/TicketPodPanel.tsx](web/src/components/tickets/TicketPodPanel.tsx)
- [web/src/components/workspace/TerminalTabs.tsx](web/src/components/workspace/TerminalTabs.tsx)
- [web/src/components/workspace/WorkspaceManager.tsx](web/src/components/workspace/WorkspaceManager.tsx)
- [web/src/lib/api/pod.ts](web/src/lib/api/pod.ts)
- [web/src/messages/de/app.json](web/src/messages/de/app.json)
- [web/src/messages/en/app.json](web/src/messages/en/app.json)
- [web/src/messages/es/app.json](web/src/messages/es/app.json)
- [web/src/messages/fr/app.json](web/src/messages/fr/app.json)
- [web/src/messages/ja/app.json](web/src/messages/ja/app.json)
- [web/src/messages/ko/app.json](web/src/messages/ko/app.json)
- [web/src/messages/pt/app.json](web/src/messages/pt/app.json)
- [web/src/messages/zh/app.json](web/src/messages/zh/app.json)

</details>



This page covers the desktop IDE shell (`IDEShell`) and the AgentsMesh network topology page (`MeshPage`). It documents the persistent IDE layout structure, the topology visualization for multi-agent networks, pod creation modals, and the terminal workspace management components.

For the channel chat system that appears as a slide-out panel on the Mesh page, see [Channels and Chat](#5.4). For the Zustand stores and real-time event dispatch that power mesh and workspace state, see [Real-time State Management](#5.5). For terminal connection details (xterm.js, WebSocket, binary protocol), see [Terminal Workspace](#5.1).

---

## IDEShell

`IDEShell` is the outer desktop layout wrapper used by all authenticated pages. It lives at [web/src/components/ide/IDEShell.tsx]() and renders a persistent three-panel structure.

**IDEShell Desktop Layout**

```mermaid
graph TD
  IDEShell["IDEShell\nIDEShell.tsx"]
  ActivityBar["ActivityBar\nActivityBar.tsx\n(48px fixed)"]
  SideBar["SideBar\nSideBar.tsx\n(resizable 200-400px)"]
  MainArea["main\n(flex-1, overflow-auto)"]
  BottomPanel["BottomPanel\nBottomPanel.tsx\n(workspace activity only)"]
  CommandPalette["CommandPalette\nCommandPalette.tsx"]
  CreatePodModal["CreatePodModal\nCreatePodModal.tsx"]
  AddRunnerModal["AddRunnerModal\nmodals/AddRunnerModal.tsx"]
  ImportRepositoryModal["ImportRepositoryModal\nmodals/ImportRepositoryModal.tsx"]

  IDEShell --> ActivityBar
  IDEShell --> SideBar
  IDEShell --> MainArea
  MainArea --> BottomPanel
  IDEShell --> CommandPalette
  IDEShell --> CreatePodModal
  IDEShell --> AddRunnerModal
  IDEShell --> ImportRepositoryModal
```

Sources: [web/src/components/ide/IDEShell.tsx:32-43](), [web/src/components/ide/IDEShell.tsx:138-189]()

The layout comment inside `IDEShell` describes the geometry:

```
┌──────────┬──────────────┬─────────────────────────────────┐
│ Activity │  Side Bar    │       Main Content Area         │
│   Bar    │  (resizable) │                                 │
│  (48px)  │              ├─────────────────────────────────┤
│          │              │  Bottom Panel (workspace only)  │
└──────────┴──────────────┴─────────────────────────────────┘
```

`BottomPanel` is rendered only when `activeActivity === "workspace"` [web/src/components/ide/IDEShell.tsx:159]().

### Activity Types and Sidebar Dispatch

`getSidebarContent(activity, callbacks)` [web/src/components/ide/IDEShell.tsx:51-73]() maps the active activity to a sidebar component. The active activity is read from `useIDEStore`.

| `ActivityType` | Sidebar Component |
|---|---|
| `"workspace"` | `WorkspaceSidebarContent` |
| `"tickets"` | `TicketsSidebarContent` |
| `"mesh"` | `MeshSidebarContent` |
| `"repositories"` | `RepositoriesSidebarContent` |
| `"runners"` | `RunnersSidebarContent` |
| `"settings"` | `SettingsSidebarContent` |
| `"loops"` | `LoopsSidebarContent` |

### Global Modals

`IDEShell` owns three application-level modals triggered by callbacks passed to sidebar content components:

| Modal | Triggering callback | Wired into |
|---|---|---|
| `CreatePodModal` | `onCreatePod` | `WorkspaceSidebarContent` |
| `AddRunnerModal` | `onAddRunner` | `RunnersSidebarContent` |
| `ImportRepositoryModal` | `onImportRepo` | `RepositoriesSidebarContent` |

On successful pod creation, `handlePodCreated` [web/src/components/ide/IDEShell.tsx:99-109]() calls `addPane(pod.pod_key)` from `useWorkspaceStore` and `fetchPods()` from `usePodStore` before navigating to the workspace.

### SideBar Resize

`SideBar` [web/src/components/ide/SideBar.tsx]() reads and writes `sidebarWidth` from `useIDEStore`. The resize handle is a 1px-wide `div` on the right edge. On `mousedown` it sets `isResizing = true` and document-level `mousemove` / `mouseup` handlers clamp the new width to `[200, 400]` px [web/src/components/ide/SideBar.tsx:52-73]().

The `SideBar` header contains an organization dropdown that calls `router.push` to the equivalent page in the selected org [web/src/components/ide/SideBar.tsx:111-118]().

---

## MeshPage

`MeshPage` [web/src/app/(dashboard)/[org]/mesh/page.tsx]() is served at `/{org}/mesh`. It renders the multi-agent topology visualization and manages the channel chat overlay.

**MeshPage Component Structure**

```mermaid
graph TD
  MeshPage["MeshPage\n/[org]/mesh/page.tsx"]
  Header["Header div\n(stats + Refresh button)"]
  ErrorBanner["Error Banner\n(conditional on error state)"]
  MeshTopologyComp["MeshTopology\nimport from @/components/mesh"]
  PollingIndicator["Polling indicator\n(loading and topology non-null)"]
  Legend["Legend bar\n(node colors + binding line styles)"]
  ChatPanel["ChannelChatPanel\nimport from @/components/mesh\n(desktop, w-520px slide-out)"]
  MobileChat["MobileChannelChat\nimport from @/components/mesh\n(mobile, full-screen overlay)"]

  MeshPage --> Header
  MeshPage --> ErrorBanner
  MeshPage --> MeshTopologyComp
  MeshPage --> PollingIndicator
  MeshPage --> Legend
  MeshPage --> ChatPanel
  MeshPage --> MobileChat
```

Sources: [web/src/app/(dashboard)/[org]/mesh/page.tsx:57-205]()

### Header Statistics

The header computes three stats from `useMeshStore.topology`:

| Display | Computation |
|---|---|
| Active pods | `topology.nodes.filter(n => n.status === "running" \|\| n.status === "initializing").length` |
| Channel count | `topology.channels.filter(c => !c.is_archived).length` |
| Binding count | `topology.edges.length` |

Both are memoized with `useMemo` [web/src/app/(dashboard)/[org]/mesh/page.tsx:30-40]().

### Chat Panel Behavior

When `selectedChannel` is non-null, the chat panel is shown. The layout differs by breakpoint (from `useBreakpoint`):

- **Desktop**: A fixed 520px-wide `div` positioned `absolute top-0 right-0 h-full` slides in using `translate-x-0` / `translate-x-full` CSS transitions [web/src/app/(dashboard)/[org]/mesh/page.tsx:178-195]().
- **Mobile**: `MobileChannelChat` is rendered as a full-screen overlay.

Pressing `Escape` on desktop calls `selectChannel(null)` [web/src/app/(dashboard)/[org]/mesh/page.tsx:48-55]().

### Legend

| Color / Style | Meaning |
|---|---|
| Green square | Running |
| Yellow square | Initializing |
| Gray square | Terminated |
| Red square | Failed |
| Blue square | Channel |
| Solid green line | Active binding |
| Dashed yellow line | Pending binding |

---

## Mesh Sidebar

`MeshSidebarContent` [web/src/components/ide/sidebar/MeshSidebarContent.tsx]() renders inside `SideBar` when the `"mesh"` activity is active. It provides a searchable list view of the same topology shown on `MeshPage`.

**MeshSidebarContent Structure**

```mermaid
graph TD
  MeshSidebarContent["MeshSidebarContent\nide/sidebar/MeshSidebarContent.tsx"]
  SearchInput["Search Input\n(filters channels and nodes by name/pod_key/model)"]
  RefreshBtn["Refresh Button\n(calls fetchTopology)"]
  NetStats["Network Stats grid\n(activeNodes, totalChannels, totalBindings)"]
  MeshChannelsList["MeshChannelsList\nMeshChannelsList.tsx\n(collapsible)"]
  MeshNodesList["MeshNodesList\nMeshNodesList.tsx\n(collapsible)"]
  MeshSelectedDetails["MeshSelectedDetails\nMeshSelectedDetails.tsx\n(selected node or channel)"]

  MeshSidebarContent --> SearchInput
  MeshSidebarContent --> RefreshBtn
  MeshSidebarContent --> NetStats
  MeshSidebarContent --> MeshChannelsList
  MeshSidebarContent --> MeshNodesList
  MeshSidebarContent --> MeshSelectedDetails
```

Sources: [web/src/components/ide/sidebar/MeshSidebarContent.tsx:133-215]()

### Filtering Logic

Both `filteredChannels` and `filteredNodes` are computed with `useMemo` to avoid creating new array references on every render [web/src/components/ide/sidebar/MeshSidebarContent.tsx:64-85]():

- **Channels**: matches `searchQuery` against `channel.name`.
- **Nodes**: matches `searchQuery` against `node.pod_key` and `node.model`.

### Node and Channel Interaction

| User action | Effect |
|---|---|
| Click a node | `selectNode(node.pod_key)` → updates `MeshSelectedDetails` |
| Click a channel | `selectChannel(channel.id)` → updates `MeshSelectedDetails` and triggers chat on `MeshPage` |
| Click "Open Terminal" on a node | `addPane(podKey)` + `router.push("/{org}/workspace")` |

---

## Topology Data Model

The topology is assembled by `mesh.Service.GetTopology` [backend/internal/service/mesh/service.go:46-147]() and returned as `mesh.MeshTopology`.

**MeshTopology Data Model**

```mermaid
graph TD
  MeshTopology["mesh.MeshTopology\nservice/mesh/service.go"]
  MeshNode["mesh.MeshNode\nPodKey string\nStatus string\nAgentStatus string\nModel string\nTitle string\nRunnerID int64\nRunnerNodeID string\nTicketID ptr int64\nTicketSlug ptr string\nStartedAt ptr time.Time"]
  MeshEdge["mesh.MeshEdge\nID int64\nSource string\nTarget string\nGrantedScopes []string\nPendingScopes []string\nStatus string"]
  ChannelInfo["mesh.ChannelInfo\nID int64\nName string\nDescription string\nPodKeys []string\nMessageCount int\nIsArchived bool"]
  RunnerInfo["mesh.RunnerInfo\nID int64\nNodeID string\nStatus string\nMaxConcurrentPods int\nCurrentPods int"]

  MeshTopology --> MeshNode
  MeshTopology --> MeshEdge
  MeshTopology --> ChannelInfo
  MeshTopology --> RunnerInfo
```

Sources: [backend/internal/service/mesh/service.go:46-147](), [backend/internal/service/mesh/service.go:149-177]()

### Backend Assembly Steps

`GetTopology` builds the topology in four stages:

| Step | Source | Filter |
|---|---|---|
| Nodes | `podService.ListPods` (limit 100) | `pod.IsActive()` |
| Edges | `bindingService.GetBindingsForPod` for each active pod | `BindingStatusActive`, deduplicated by `binding.ID` |
| Channels | `channelService.ListChannels` (limit 50) | `IncludeArchived: false`; `PodKeys` from `channel_pods` table |
| Runners | DB query on `runner` table | `organization_id = orgID AND is_enabled = true` |

`podToNode` [backend/internal/service/mesh/service.go:150-177]() maps an `agentpod.Pod` to `mesh.MeshNode`, populating `RunnerNodeID`/`RunnerStatus` from `pod.Runner` and `TicketSlug`/`TicketTitle` from `pod.Ticket` when those associations are preloaded.

---

## useMeshStore

`useMeshStore` (from `@/stores/mesh`) is the Zustand store that holds all client-side mesh state. Both `MeshPage` and `MeshSidebarContent` subscribe to it independently using granular selectors to avoid unnecessary re-renders.

| Field | Type | Description |
|---|---|---|
| `topology` | `MeshTopology \| null` | Full topology from last `fetchTopology` call |
| `loading` | `boolean` | True while a fetch is in flight |
| `error` | `string \| null` | Error message from last failed fetch |
| `selectedNode` | `string \| null` | `pod_key` of the currently selected node |
| `selectedChannel` | `number \| null` | `id` of the currently selected channel |

Key actions:

| Action | Effect |
|---|---|
| `fetchTopology()` | GETs topology from backend, sets `topology` |
| `selectNode(podKey)` | Sets `selectedNode` |
| `selectChannel(id \| null)` | Sets `selectedChannel`; `null` dismisses chat panel |
| `clearError()` | Clears `error` |

Both `MeshPage` [web/src/app/(dashboard)/[org]/mesh/page.tsx:26-28]() and `MeshSidebarContent` [web/src/components/ide/sidebar/MeshSidebarContent.tsx:47-51]() call `fetchTopology()` on mount. Subsequent real-time updates arrive via `RealtimeProvider` (see [Real-time State Management](#5.5)).

---

## CreatePodModal

`CreatePodModal` [web/src/components/ide/CreatePodModal.tsx]() is a modal dialog that wraps the shared `CreatePodForm` component. It is used in two contexts:

1. **Global workspace context** — triggered by the "New Pod" button in `WorkspaceSidebarContent` via `IDEShell`.
2. **Ticket context** — triggered from `TicketPodPanel` with an explicit `ticketContext` prop.

### Props

| Prop | Type | Description |
|---|---|---|
| `open` | `boolean` | Controls visibility |
| `onClose` | `() => void` | Called on cancel or after creation |
| `onCreated` | `(pod?: PodData) => void` | Called after successful creation |
| `ticketContext?` | `TicketContext` | Scopes the form to a ticket |

### Ticket Context Behavior

When `ticketContext` is supplied, `formConfig` is built with [web/src/components/ide/CreatePodModal.tsx:30-46]():

- `scenario: "ticket"` 
- A `promptGenerator` that produces: `"Work on ticket {slug}: {title}\n\n{description}"`

This prompt is pre-filled into the "Initial Prompt" field of `CreatePodForm`.

Focus is managed with `useFocusTrap`, which traps keyboard navigation inside the modal while `open` is true.

---

## WorkspaceManager and TerminalTabs

`WorkspaceManager` [web/src/components/workspace/WorkspaceManager.tsx]() renders the terminal workspace inside `IDEShell`'s main content area when `activeActivity === "workspace"`.

**WorkspaceManager Component Structure**

```mermaid
graph TD
  WorkspaceManager["WorkspaceManager\nWorkspaceManager.tsx"]
  TerminalTabs["TerminalTabs\nTerminalTabs.tsx\n(desktop only)"]
  TerminalGrid["TerminalGrid\nTerminalGrid.tsx\n(desktop only)"]
  TerminalSwiper["TerminalSwiper\nTerminalSwiper.tsx\n(mobile only)"]
  TerminalToolbar["TerminalToolbar\nTerminalToolbar.tsx\n(mobile only)"]
  PodSelectorModal["PodSelectorModal\n(inline component)\n(shown when + is clicked)"]

  WorkspaceManager --> TerminalTabs
  WorkspaceManager --> TerminalGrid
  WorkspaceManager --> TerminalSwiper
  WorkspaceManager --> TerminalToolbar
  WorkspaceManager --> PodSelectorModal
```

Sources: [web/src/components/workspace/WorkspaceManager.tsx:92-130]()

`PodSelectorModal` lists all pods where `status === "running"` and `pod_key` is not already in `useWorkspaceStore.panes`. Selecting one calls `addPane(podKey)`.

### TerminalTabs

`TerminalTabs` [web/src/components/workspace/TerminalTabs.tsx]() renders the tab bar and layout controls. Each tab corresponds to one pane in `useWorkspaceStore.panes`.

**Tab sub-components:**

| Component | Source | Description |
|---|---|---|
| `ConnectionDot` | `terminalPool.onStatusChange(podKey, cb)` | Colored dot showing WebSocket connection state |
| `TabPaneTitle` | `usePodStore` (find by `pod_key`) | Human-readable pod name via `getPodDisplayName` |

`ConnectionDot` maps pool status to CSS classes [web/src/components/workspace/TerminalTabs.tsx:163-181]():

| Pool status | CSS |
|---|---|
| `"connected"` | `bg-green-500` |
| `"connecting"` | `bg-yellow-500 animate-pulse` |
| `"error"` | `bg-red-500` |
| _(other)_ | `bg-gray-500` |

**Layout controls** update `useWorkspaceStore.gridLayout`:

| Button | `gridLayout.type` | Icon |
|---|---|---|
| Single view | `"1x1"` | `Square` |
| Two columns | `"1x2"` | `Columns` |
| Two rows | `"2x1"` | `Rows` |
| 2×2 grid | `"2x2"` | `Grid2X2` |

Fullscreen toggle uses `document.documentElement.requestFullscreen()` / `document.exitFullscreen()`, with a `fullscreenchange` listener that keeps `isFullscreen` state in sync [web/src/components/workspace/WorkspaceManager.tsx:61-81]().

---

## TicketPodPanel

`TicketPodPanel` [web/src/components/tickets/TicketPodPanel.tsx]() appears in the ticket detail view and lists all pods associated with a ticket. It fetches data with `ticketApi.getPods(ticketSlug)`.

Active pods (status `"running"` or `"initializing"`) are shown at the top. Inactive pods are hidden under a `<details>` element labelled with the count [web/src/components/tickets/TicketPodPanel.tsx:143-155]().

Each active pod row (`PodItem`) offers two actions [web/src/components/tickets/TicketPodPanel.tsx:181-197]():

| Action | Effect |
|---|---|
| **Connect** | `useWorkspaceStore.addPane(pod.pod_key)` + navigate to `/{org}/workspace` |
| **Open in new tab** | `window.open("/{org}/workspace?pod={pod_key}", "_blank")` |

`TicketPodPanel` also renders `CreatePodModal` with a `ticketContext` built from `ticketId`, `ticketSlug`, `ticketTitle`, and `repositoryId` [web/src/components/tickets/TicketPodPanel.tsx:95-109]().

---

## Cross-Component Data Flow

**Topology data flow: backend to UI**

```mermaid
sequenceDiagram
  participant Backend as "mesh.Service.GetTopology\nservice/mesh/service.go"
  participant Store as "useMeshStore\n@/stores/mesh"
  participant MeshPage as "MeshPage\n/[org]/mesh/page.tsx"
  participant Sidebar as "MeshSidebarContent\nide/sidebar/MeshSidebarContent.tsx"
  participant Topology as "MeshTopology\n@/components/mesh"
  participant Chat as "ChannelChatPanel\n@/components/mesh"

  MeshPage->>Store: "fetchTopology() on mount"
  Sidebar->>Store: "fetchTopology() on mount"
  Store->>Backend: "GET /api/v1/orgs/{org}/mesh/topology"
  Backend-->>Store: "MeshTopology {nodes, edges, channels, runners}"
  Store-->>MeshPage: "topology, loading, error"
  Store-->>Sidebar: "topology, selectedNode, selectedChannel"
  MeshPage->>Topology: "renders topology canvas"
  Sidebar->>Topology: "(parallel list view)"
  MeshPage->>Chat: "selectedChannel triggers slide-out"
```

Sources: [web/src/app/(dashboard)/[org]/mesh/page.tsx:26-28](), [web/src/components/ide/sidebar/MeshSidebarContent.tsx:47-51](), [backend/internal/service/mesh/service.go:46-147]()

---

# Page: Channels and Chat

# Channels and Chat

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [web/src/components/ide/BottomPanel.tsx](web/src/components/ide/BottomPanel.tsx)
- [web/src/components/ide/BottomPanel/ChannelDetailView.tsx](web/src/components/ide/BottomPanel/ChannelDetailView.tsx)
- [web/src/components/ide/BottomPanel/types.ts](web/src/components/ide/BottomPanel/types.ts)
- [web/src/components/mesh/ChannelChatPanel.tsx](web/src/components/mesh/ChannelChatPanel.tsx)
- [web/src/components/mesh/ChannelHeader.tsx](web/src/components/mesh/ChannelHeader.tsx)
- [web/src/components/mesh/ChannelPodManager.tsx](web/src/components/mesh/ChannelPodManager.tsx)
- [web/src/components/mesh/MobileChannelChat.tsx](web/src/components/mesh/MobileChannelChat.tsx)
- [web/src/lib/api/channel.ts](web/src/lib/api/channel.ts)

</details>



This page documents the channel chat UI system in the web frontend: how channels are listed and navigated, the chat panel components, pod membership management, the `channelApi` client, and the message-sending flow including `@mention` forwarding to pod terminals. For the backend channel and binding model, see [2.4](). For the Zustand `channelStore` and real-time event updates, see [5.5](). For the AgentsMesh network topology view that hosts the desktop chat panel, see [5.3]().

---

## Overview

Channels are multi-party communication threads that can include both human users and AI pods. The chat system surfaces in two contexts:

| Context | Component | Use case |
|---|---|---|
| IDE bottom panel (desktop) | `BottomPanel` → `ChannelsTabContent` | Embedded chat within the IDE layout |
| Mesh sidebar / full page (desktop) | `ChannelChatPanel` | Standalone channel chat in the mesh view |
| Mobile full-screen | `MobileChannelChat` | Full-viewport overlay on small screens |

When a user sends a message that `@mentions` a pod, the message is posted to the channel **and** the prompt is forwarded directly to that pod's terminal via `podApi.sendPrompt`.

---

## BottomPanel and the Channels Tab

`BottomPanel` ([web/src/components/ide/BottomPanel.tsx:44-382]()) is the resizable panel at the bottom of the IDE layout. It hosts five tabs, each rendered as a discrete content component:

| Tab ID | Icon | Content component |
|---|---|---|
| `channels` | `MessageSquare` | `ChannelsTabContent` |
| `activity` | `Activity` | `ActivityTabContent` |
| `autopilot` | `Bot` | `AutopilotPanelContent` |
| `delivery` | `GitPullRequest` | `DeliveryTabContent` |
| `info` | `Info` | `InfoTabContent` |

The set of available tabs is defined in `TAB_IDS` ([web/src/components/ide/BottomPanel.tsx:42]()).

**Tab and panel state** is managed by `useIDEStore`: `bottomPanelOpen`, `bottomPanelHeight`, `bottomPanelTab`, and their setters. The panel supports mouse-drag resizing, clamped between 100 px and 60% of window height ([web/src/components/ide/BottomPanel.tsx:153-177]()).

**Channel state** for the bottom panel is held locally (`selectedChannelId`) and in `useChannelStore` (`currentChannel`, `messages`, `messagesLoading`). When `selectedChannelId` is set, `fetchChannel` and `fetchMessages` are triggered ([web/src/components/ide/BottomPanel.tsx:83-94]()).

**Channels shown** in the tab are derived from the mesh topology, not fetched independently:

```
podChannels = topology.channels.filter(c => c.pod_keys.includes(selectedPodKey))
```

[web/src/components/ide/BottomPanel.tsx:119-122]()

Sources: [web/src/components/ide/BottomPanel.tsx:1-385]()

---

## Component Hierarchy

**BottomPanel channels tab flow:**

```mermaid
flowchart TD
  BP["BottomPanel"] --> CT["ChannelsTabContent"]
  CT -->|"selectedChannelId == null"| CL["ChannelListView\n(channel list)"]
  CT -->|"selectedChannelId != null"| CDV["ChannelDetailView"]
  CDV --> CH["ChannelHeader"]
  CDV --> CD["ChannelDocument"]
  CDV --> ML["MessageList"]
  CDV --> MI["MessageInput"]
  CH --> CPM["ChannelPodManager"]
```

**Standalone mesh / mobile chat flow:**

```mermaid
flowchart TD
  MeshPage["MeshPage"] --> CCP["ChannelChatPanel"]
  MobileView["MobileView"] --> MCC["MobileChannelChat"]
  CCP --> CH2["ChannelHeader"]
  CCP --> CD2["ChannelDocument"]
  CCP --> ML2["MessageList"]
  CCP --> MI2["MessageInput"]
  CH2 --> CPM2["ChannelPodManager"]
  MCC --> CPM3["ChannelPodManager"]
  MCC --> ML3["MessageList"]
  MCC --> MI3["MessageInput"]
```

Sources: [web/src/components/ide/BottomPanel.tsx:336-353](), [web/src/components/ide/BottomPanel/ChannelDetailView.tsx:1-105](), [web/src/components/mesh/ChannelChatPanel.tsx:1-167](), [web/src/components/mesh/MobileChannelChat.tsx:1-205]()

---

## ChannelChatPanel

`ChannelChatPanel` ([web/src/components/mesh/ChannelChatPanel.tsx]()) is the desktop chat panel used in the mesh view. It accepts `channelId` and `onClose` props.

**Lifecycle:**
- On mount (or `channelId` change): calls `fetchChannel(channelId)` and `fetchMessages(channelId)`.
- On unmount: calls `setCurrentChannel(null)` to clear shared store state.

**Data sources:**
- `useChannelStore` — `currentChannel`, `messages`, `messagesLoading`, `sendMessage`
- `useMeshStore` — `topology` (for pod count on the channel)

**Pod count** is resolved by looking up the channel in `topology.channels` first, falling back to `currentChannel.pods.length` ([web/src/components/mesh/ChannelChatPanel.tsx:45-46]()).

**Message transformation:** Raw `ChannelMessage` objects from the store are mapped to a `TransformedMessage` shape before being passed to `MessageList`. This resolves `sender_pod_info` and `sender_user` (GORM JSON tag names) into typed `pod` and `user` fields ([web/src/components/mesh/ChannelChatPanel.tsx:92-114]()).

**Pagination:** `fetchMessages(channelId, 50, messages.length)` fetches older messages when the user scrolls up. The `hasMore` flag is `messages.length >= 50 && messages.length % 50 === 0` ([web/src/components/mesh/ChannelChatPanel.tsx:81-83](), [web/src/components/mesh/ChannelChatPanel.tsx:150-154]()).

Sources: [web/src/components/mesh/ChannelChatPanel.tsx:1-167]()

---

## MobileChannelChat

`MobileChannelChat` ([web/src/components/mesh/MobileChannelChat.tsx]()) is a fixed-position full-screen overlay (`fixed inset-0 z-50`) for mobile viewports. Its logic mirrors `ChannelChatPanel` exactly, with layout differences:

- Uses `ArrowLeft` back button in the header instead of a close `X`.
- Displays `ChannelDocument` inline when present.
- Loading state uses a skeleton placeholder header ([web/src/components/mesh/MobileChannelChat.tsx:122-136]()).

Sources: [web/src/components/mesh/MobileChannelChat.tsx:1-205]()

---

## Message Sending with Pod Mentions

Both `ChannelChatPanel` and `MobileChannelChat` (and `BottomPanel`) share the same `handleSendMessage` logic. The flow is:

**Message send + pod mention forwarding:**

```mermaid
sequenceDiagram
  participant "User" as User
  participant "MessageInput" as MI
  participant "channelStore.sendMessage" as SM
  participant "channelApi.sendMessage" as API
  participant "podApi.sendPrompt" as PP

  User->>MI: "Types message with @podKey"
  MI->>SM: "sendMessage(channelId, content)"
  SM->>API: "POST /channels/:id/messages"
  MI->>MI: "extractPromptFromMention(content, mentionedPods)"
  MI->>MI: "buildChannelPrompt(rawPrompt, channelName)"
  MI->>PP: "sendPrompt(pod.podKey, prompt) [per mentioned pod]"
  PP-->>MI: "resolved / rejected (allSettled)"
```

Key functions involved:

| Function | File | Role |
|---|---|---|
| `extractPromptFromMention` | `web/src/components/mesh/MessageInput.tsx` | Strips mention syntax, extracts raw prompt text |
| `buildChannelPrompt` | `web/src/components/mesh/MessageInput.tsx` | Wraps raw prompt with channel context metadata |
| `sendMessage` | `useChannelStore` | Posts the message to the backend channel |
| `podApi.sendPrompt` | `web/src/lib/api/pod.ts` | Sends the prompt to a specific pod's terminal |

`Promise.allSettled` is used so a failure to forward to one pod does not block the others ([web/src/components/mesh/ChannelChatPanel.tsx:68-71]()).

Sources: [web/src/components/mesh/ChannelChatPanel.tsx:58-78](), [web/src/components/mesh/MobileChannelChat.tsx:63-83](), [web/src/components/ide/BottomPanel.tsx:192-213]()

---

## ChannelPodManager

`ChannelPodManager` ([web/src/components/mesh/ChannelPodManager.tsx]()) is a `Popover` that manages which pods belong to a channel. It appears in both `ChannelHeader` and `MobileChannelChat`.

**Two display modes:**
- `compact=false` (default): shows a `Bot + count` pill button
- `compact=true`: shows a minimal `Bot + count` inline button (used in the bottom panel header)

**On popover open**, it loads two datasets concurrently ([web/src/components/mesh/ChannelPodManager.tsx:51-66]()):
1. `channelApi.getPods(channelId)` — pods currently joined to the channel
2. `usePodStore.fetchPods({ status: "running" })` — all running pods in the org

**Available pods** = running or initializing pods not already joined ([web/src/components/mesh/ChannelPodManager.tsx:70-75]()).

**Actions:**
- `handleJoin(podKey)` → `channelApi.joinPod(channelId, podKey)` → refreshes pod list → calls `onPodsChanged()`
- `handleLeave(podKey)` → `channelApi.leavePod(channelId, podKey)` → refreshes pod list → calls `onPodsChanged()`

The `onPodsChanged` callback propagates up to trigger `fetchTopology()` so the mesh graph updates to reflect new pod-channel edges.

Sources: [web/src/components/mesh/ChannelPodManager.tsx:1-255]()

---

## ChannelHeader

`ChannelHeader` ([web/src/components/mesh/ChannelHeader.tsx]()) renders the top bar of a chat panel.

| Prop | Purpose |
|---|---|
| `name` | Channel name (displayed as `#name`) |
| `description` | Optional subtitle |
| `podCount` | Shown in the `ChannelPodManager` trigger |
| `channelId` | Passed to `ChannelPodManager` |
| `compact` | `true` for bottom panel embedding |
| `onPodsChanged` | Forwarded to `ChannelPodManager` |

Sources: [web/src/components/mesh/ChannelHeader.tsx:1-121]()

---

## ChannelDocument

`ChannelDocument` is rendered when `currentChannel.document` is non-empty ([web/src/components/mesh/ChannelChatPanel.tsx:144-146]()). It displays a collapsible markdown preview of the channel's document field. This field is a free-form markdown string stored on the channel record.

Sources: [web/src/components/mesh/ChannelChatPanel.tsx:144-146](), [web/src/components/mesh/MobileChannelChat.tsx:183-185](), [web/src/components/ide/BottomPanel/ChannelDetailView.tsx:79-81]()

---

## channelApi

`channelApi` ([web/src/lib/api/channel.ts]()) is the REST client for all channel operations. All routes are scoped to the current organization via `orgPath("/channels")`.

```mermaid
flowchart LR
  subgraph "channelApi (web/src/lib/api/channel.ts)"
    list["list(filters?)"]
    get["get(id)"]
    create["create(data)"]
    update["update(id, data)"]
    archive["archive(id)"]
    unarchive["unarchive(id)"]
    getMessages["getMessages(id, limit?, offset?)"]
    sendMessage["sendMessage(id, content, podKey?, messageType?)"]
    getPods["getPods(id)"]
    joinPod["joinPod(id, podKey)"]
    leavePod["leavePod(id, podKey)"]
  end
```

**Endpoint mapping:**

| Method | HTTP | Path |
|---|---|---|
| `list` | `GET` | `/org/:slug/channels?...` |
| `get` | `GET` | `/org/:slug/channels/:id` |
| `create` | `POST` | `/org/:slug/channels` |
| `update` | `PUT` | `/org/:slug/channels/:id` |
| `archive` | `POST` | `/org/:slug/channels/:id/archive` |
| `unarchive` | `POST` | `/org/:slug/channels/:id/unarchive` |
| `getMessages` | `GET` | `/org/:slug/channels/:id/messages?limit&offset` |
| `sendMessage` | `POST` | `/org/:slug/channels/:id/messages` |
| `getPods` | `GET` | `/org/:slug/channels/:id/pods` |
| `joinPod` | `POST` | `/org/:slug/channels/:id/pods` |
| `leavePod` | `DELETE` | `/org/:slug/channels/:id/pods/:podKey` |

**Core data types** defined in this file:

- `ChannelData` — channel record with `id`, `name`, `description`, `document`, optional `repository_id`, `ticket_id`, `ticket_slug`, `is_archived`
- `ChannelMessage` — message record with `sender_pod_info` and `sender_user` (GORM JSON tag names)

Sources: [web/src/lib/api/channel.ts:1-137]()

---

## BottomPanel/types.ts — Shared Type Contracts

[web/src/components/ide/BottomPanel/types.ts]() defines the shared TypeScript interfaces for all bottom panel tab content components:

| Type | Purpose |
|---|---|
| `TabContentProps` | Base props: `selectedPodKey`, `t` |
| `ChannelsTabContentProps` | Extends base with channel list and chat props |
| `ActivityTabContentProps` | Extends base with binding edge props |
| `TransformedMessage` | Normalized message shape consumed by `MessageList` |

`TransformedMessage` maps the raw `ChannelMessage` (with `sender_pod_info` / `sender_user`) into a cleaner `pod` / `user` shape with camelCase keys ([web/src/components/ide/BottomPanel/types.ts:49-65]()).

Sources: [web/src/components/ide/BottomPanel/types.ts:1-66]()

---

## Data Flow Summary

**Reading channel messages:**

```mermaid
sequenceDiagram
  participant "BottomPanel / ChannelChatPanel" as CP
  participant "useChannelStore" as CS
  participant "channelApi" as API
  participant "Backend REST" as BE

  CP->>CS: "fetchChannel(channelId)"
  CS->>API: "channelApi.get(id)"
  API->>BE: "GET /channels/:id"
  BE-->>CS: "ChannelData"
  CS-->>CP: "currentChannel updated"

  CP->>CS: "fetchMessages(channelId)"
  CS->>API: "channelApi.getMessages(id, limit, offset)"
  API->>BE: "GET /channels/:id/messages"
  BE-->>CS: "ChannelMessage[]"
  CS-->>CP: "messages updated"
```

Real-time message updates (new messages arriving over WebSocket) are handled by `RealtimeProvider` dispatching into `useChannelStore` — see [5.5]() for that layer.

Sources: [web/src/components/mesh/ChannelChatPanel.tsx:33-42](), [web/src/components/ide/BottomPanel.tsx:83-94](), [web/src/lib/api/channel.ts:97-110]()

---

# Page: Real-time State Management

# Real-time State Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/cmd/server/eventbus_setup.go](backend/cmd/server/eventbus_setup.go)
- [web/src/components/ide/sidebar/WorkspaceSidebarContent.tsx](web/src/components/ide/sidebar/WorkspaceSidebarContent.tsx)
- [web/src/components/pwa/PushNotificationManager.tsx](web/src/components/pwa/PushNotificationManager.tsx)
- [web/src/hooks/usePodStatus.ts](web/src/hooks/usePodStatus.ts)
- [web/src/providers/RealtimeProvider.tsx](web/src/providers/RealtimeProvider.tsx)
- [web/src/stores/__tests__/pod.test.ts](web/src/stores/__tests__/pod.test.ts)
- [web/src/stores/__tests__/terminalConnection.test.ts](web/src/stores/__tests__/terminalConnection.test.ts)
- [web/src/stores/__tests__/workspace.test.ts](web/src/stores/__tests__/workspace.test.ts)
- [web/src/stores/channel.ts](web/src/stores/channel.ts)
- [web/src/stores/pod.ts](web/src/stores/pod.ts)
- [web/src/stores/runner.ts](web/src/stores/runner.ts)

</details>



This page documents the client-side state management architecture of the AgentsMesh web frontend: how Zustand stores maintain application state, how `RealtimeProvider` ingests backend WebSocket events and dispatches them to the correct stores, and the design decisions that prevent stale data and rendering issues.

This page focuses on frontend state. For the backend event bus and WebSocket hub that produce these events, see [Real-time Events and WebSocket (2.10)](#2.10). For terminal WebSocket connections (a separate binary protocol not covered here), see [Terminal Workspace (5.1)](#5.1).

---

## Architecture Overview

The system has two complementary update paths. Components can trigger explicit API fetches, but status changes that originate on the backend (runner going offline, pod status changing, channel message arriving) arrive via a single persistent WebSocket managed by `RealtimeProvider`.

**Event flow: backend → frontend state**

```mermaid
flowchart TD
    subgraph "Backend"
        EB["eventbus.EventBus"]
        Hub["websocket.Hub"]
        EB -->|"BroadcastToOrg / SendToUser"| Hub
    end

    subgraph "Frontend (Next.js)"
        WS["WebSocket\n/ws"]
        RP["RealtimeProvider\n(web/src/providers/RealtimeProvider.tsx)"]
        Hub -->|"JSON event"| WS
        WS -->|"useRealtimeConnection"| RP

        RP -->|"pod:*"| PodStore["usePodStore\n(web/src/stores/pod.ts)"]
        RP -->|"runner:*"| RunnerStore["useRunnerStore\n(web/src/stores/runner.ts)"]
        RP -->|"ticket:*"| TicketStore["useTicketStore\n(web/src/stores/ticket.ts)"]
        RP -->|"channel:message"| ChannelStore["useChannelStore\n(web/src/stores/channel.ts)"]
        RP -->|"autopilot:*"| AutopilotStore["useAutopilotStore\n(web/src/stores/autopilot.ts)"]
        RP -->|"loop_run:*"| LoopStore["useLoopStore\n(web/src/stores/loop.ts)"]
        RP -->|"mr:* / pipeline:*"| TicketStore
        RP -->|"pod:* / pod:terminated"| MeshStore["useMeshStore\n(web/src/stores/mesh.ts)"]
    end

    subgraph "UI Components"
        Sidebar["WorkspaceSidebarContent"]
        Chat["ChannelChatPanel"]
        Other["Ticket / Mesh / Autopilot pages"]

        PodStore --> Sidebar
        RunnerStore --> Sidebar
        ChannelStore --> Chat
    end
```

Sources: [web/src/providers/RealtimeProvider.tsx:1-368](), [backend/cmd/server/eventbus_setup.go:59-111]()

---

## RealtimeProvider

`RealtimeProvider` is a React context provider placed at the authenticated dashboard layout level. It owns the WebSocket lifecycle and contains a single `handleEvent` dispatch function that routes every incoming event to the appropriate store action.

### Key design: `getState()` instead of reactive store subscriptions

```mermaid
flowchart LR
    subgraph "Wrong approach (causes flicker)"
        A["RealtimeProvider\nsubscribes to store via hook"] -->|"re-renders on every event"| B["Re-render cascade\nnative selects close\nUI flickers"]
    end

    subgraph "Actual approach"
        C["RealtimeProvider\naccesses stores via\n.getState() only"] -->|"no subscriptions\nno re-renders"| D["Stores update\nonly relevant\ncomponents re-render"]
    end
```

All store mutations in `handleEvent` use `useXxxStore.getState().action(...)` rather than hooks, ensuring `RealtimeProvider` itself never re-renders due to store changes. The context value it exposes (`connectionState`, `reconnect`) is separately memoized via `useMemo`.

Sources: [web/src/providers/RealtimeProvider.tsx:59-63](), [web/src/providers/RealtimeProvider.tsx:357-361]()

### Event Routing Table

| Event type(s) | Store action called |
|---|---|
| `pod:created` | `usePodStore.getState().fetchPod(pod_key)` + `useMeshStore.getState().fetchTopology()` |
| `pod:status_changed` | `updatePodStatus(...)` or `fetchPod(...)` if pod missing; also `fetchTopology()` |
| `pod:agent_status_changed` | `updateAgentStatus(pod_key, agent_status)` |
| `pod:terminated` | `updatePodStatus(pod_key, "terminated")` + `fetchTopology()` |
| `pod:title_changed` | `updatePodTitle(pod_key, title)` |
| `pod:init_progress` | `updatePodInitProgress(pod_key, phase, progress, message)` |
| `runner:online` / `runner:offline` / `runner:updated` | `updateRunnerStatus(runner_id, status)` |
| `ticket:created` / `ticket:updated` / `ticket:status_changed` / `ticket:moved` / `ticket:deleted` | `useTicketStore.getState().fetchTickets()` |
| `channel:message` | `useChannelStore.getState().addMessage(...)` (only if matching `currentChannel`) |
| `terminal:notification` | `onTerminalNotification` callback prop |
| `task:completed` | `onTaskCompleted` callback prop |
| `autopilot:status_changed` | `updateAutopilotControllerStatus(...)` |
| `autopilot:iteration` | `addIteration(key, iterationData)` |
| `autopilot:created` | `fetchAutopilotControllers()` |
| `autopilot:terminated` | `removeAutopilotController(key)` |
| `autopilot:thinking` | `updateThinking(key, data)` |
| `mr:created` / `mr:updated` / `mr:merged` / `mr:closed` | `fetchTickets()` and/or `fetchPods()` based on which IDs are set |
| `pipeline:updated` | `fetchTickets()` and/or `fetchPods()` |
| `loop_run:started` / `loop_run:completed` / `loop_run:failed` | `fetchLoops()`, `fetchLoop()`, `fetchRuns()` — debounced 500ms |
| `loop_run:warning` | `toast.warning(...)` via sonner |

Sources: [web/src/providers/RealtimeProvider.tsx:67-325]()

### Reconnection Recovery

When `connectionState` transitions to `"connected"`, `RealtimeProvider` refreshes all primary stores to recover any events missed during the disconnect window:

```
usePodStore.getState().fetchSidebarPods(currentSidebarFilter)
useRunnerStore.getState().fetchRunners()
useTicketStore.getState().fetchTickets()
useMeshStore.getState().fetchTopology()
useAutopilotStore.getState().fetchAutopilotControllers()
useLoopStore.getState().fetchLoops()
```

Sources: [web/src/providers/RealtimeProvider.tsx:344-355]()

---

## Pod Store (`usePodStore`)

The pod store is the most complex store due to the need to reconcile real-time WebSocket events with paginated API responses.

**File:** [web/src/stores/pod.ts]()

### State Shape

| Field | Type | Purpose |
|---|---|---|
| `pods` | `Pod[]` | All pods currently loaded |
| `currentPod` | `Pod \| null` | The pod selected in detail views |
| `loading` | `boolean` | Sidebar loading spinner (owned by `fetchSidebarPods`) |
| `error` | `string \| null` | Last error message |
| `initProgress` | `Record<string, PodInitProgress>` | Phase/progress/message per pod during initialization |
| `podTimestamps` | `Record<string, number>` | Timestamp of last known mutation per pod (staleness guard) |
| `podTotal` | `number` | Total pod count from API (for pagination) |
| `podHasMore` | `boolean` | Whether more pages are available |
| `loadingMore` | `boolean` | Spinner for "load more" button |
| `currentSidebarFilter` | `string` | Active filter tab (`"running"`, `"completed"`, `"all"`) |

### `SIDEBAR_STATUS_MAP`

Maps filter tab names to the comma-separated status strings sent to the API:

```
running   → "running,initializing"
completed → "terminated,failed,paused,completed,error,orphaned"
all       → ""  (no filter)
```

Sources: [web/src/stores/pod.ts:9-13]()

### `upsertPod` — Unified Write Path

All pod mutations go through the internal `upsertPod` function [web/src/stores/pod.ts:110-142](). It:

1. Checks `shouldUpdate` — skips the write if `timestamp < podTimestamps[podKey]` (stale event).
2. Finds the pod by `pod_key` in the current array.
3. Calls the `merger` callback with the existing pod (or `undefined` for new ones).
4. Produces an updated `pods` array and syncs `currentPod` if it matches.
5. Records the new timestamp.

```mermaid
flowchart TD
    Call["upsertPod(state, podKey, merger, timestamp)"]
    Call --> Guard{"shouldUpdate?\ntimestamp >= existing"}
    Guard -->|"No (stale)"| Skip["return null\n(no state change)"]
    Guard -->|"Yes"| Find["find pod in state.pods\nby pod_key"]
    Find --> Merge["merger(existing | undefined)"]
    Merge -->|"returns undefined"| Skip2["return null\n(partial update on missing pod)"]
    Merge -->|"returns Pod"| Produce["produce new pods array\nupdate currentPod if matches\nrecordTimestamp"]
    Produce --> Return["return Partial<PodState>"]
```

Sources: [web/src/stores/pod.ts:77-142]()

### In-flight Request Deduplication

The module-level `fetchPodInflight` map [web/src/stores/pod.ts:70]() prevents redundant API calls when multiple WebSocket events arrive for the same pod before the first response returns. Subsequent calls for the same `pod_key` reuse the existing `Promise<void>`.

### Merge Strategy During API Fetches

`fetchSidebarPods` and `fetchPods` both capture `fetchStartTs = Date.now()` before the API call. After the response arrives, pods whose `podTimestamps[pod_key] > fetchStartTs` are preserved from local state (a WebSocket event updated them while the request was in flight).

Sources: [web/src/stores/pod.ts:156-259]()

### Store Actions

| Action | Description |
|---|---|
| `fetchPods(filters?)` | Full list fetch. Does **not** set `loading` (fire-and-forget). |
| `fetchSidebarPods(statusFilter)` | Paged fetch for sidebar. Sets `loading`. Resets to page 1. |
| `loadMorePods()` | Appends next page, deduplicating against real-time additions. |
| `fetchPod(podKey)` | Single pod fetch (background, no `loading` flag). Deduplicates in-flight requests. |
| `createPod(data)` | Creates pod via API, prepends to `pods`, sets `currentPod`. |
| `terminatePod(podKey)` | Terminates via API; treats 404 as already terminated. Updates local state. |
| `setCurrentPod(pod)` | Sets `currentPod` directly. |
| `updatePodStatus(...)` | Targeted status update from WebSocket. Clears error fields when leaving error state. |
| `updateAgentStatus(...)` | Updates only `agent_status` field. |
| `updatePodTitle(...)` | Updates only `title` field. |
| `updatePodInitProgress(...)` | Updates `initProgress[podKey]`. |
| `clearInitProgress(podKey)` | Removes progress entry for a pod. |
| `clearError()` | Clears `error`. |

Sources: [web/src/stores/pod.ts:144-413]()

---

## Runner Store (`useRunnerStore`)

**File:** [web/src/stores/runner.ts]()

Simpler than the pod store. The key real-time action is `updateRunnerStatus`:

- Updates `status` on the matching runner in both `runners` and `availableRunners`.
- Removes the runner from `availableRunners` if the new status is anything other than `"online"`.
- Syncs `currentRunner` if it matches.

### State Shape

| Field | Type | Purpose |
|---|---|---|
| `runners` | `Runner[]` | All runners for the organization |
| `availableRunners` | `Runner[]` | Online runners eligible to host new pods |
| `currentRunner` | `Runner \| null` | Runner shown in detail view |
| `tokens` | `GRPCRegistrationToken[]` | Registration tokens for this org |
| `loading` | `boolean` | Loading flag for `fetchRunners` |
| `error` | `string \| null` | Last error |

Helper functions exported alongside the store:

- `getRunnerStatusInfo(status)` — Returns label, text color, and dot color for display.
- `canAcceptPods(runner)` — Returns `true` if `status === "online"` and `current_pods < max_concurrent_pods`.
- `formatHostInfo(hostInfo)` — Formats OS, arch, CPU, and RAM into a display string.

Sources: [web/src/stores/runner.ts:34-204]()

---

## Channel Store (`useChannelStore`)

**File:** [web/src/stores/channel.ts]()

### State Shape

| Field | Type | Purpose |
|---|---|---|
| `channels` | `Channel[]` | All channels for the org |
| `currentChannel` | `Channel \| null` | Currently viewed channel |
| `messages` | `ChannelMessage[]` | Messages for `currentChannel` |
| `loading` | `boolean` | List loading |
| `channelLoading` | `boolean` | Single channel fetch loading |
| `messagesLoading` | `boolean` | Message fetch loading |
| `error` | `string \| null` | Last error |

### Real-time Integration

`addMessage` is called by `RealtimeProvider` on `channel:message` events, but only when the event's `channel_id` matches `currentChannel.id`. Messages are deduplicated by `id` to handle the race between the WebSocket event and the REST response from `sendMessage`:

```
addMessage: (message) =>
  set((state) => ({
    messages: state.messages.some((m) => m.id === message.id)
      ? state.messages
      : [...state.messages, message],
  }))
```

Sources: [web/src/stores/channel.ts:261-267](), [web/src/providers/RealtimeProvider.tsx:167-185]()

---

## Workspace Store (`useWorkspaceStore`)

**File:** `web/src/stores/workspace.ts` (exercised by [web/src/stores/__tests__/workspace.test.ts]())

Manages the multi-pane terminal workspace layout. Persisted to `localStorage` via Zustand's `persist` middleware.

### State Shape

| Field | Type | Purpose |
|---|---|---|
| `panes` | `Pane[]` | Open terminal panes (each tied to a `podKey`) |
| `activePane` | `string \| null` | ID of the focused pane |
| `gridLayout` | `{ type, rows, cols }` | Current grid configuration |
| `mobileActiveIndex` | `number` | Active pane index on mobile (always synced with `activePane`) |
| `terminalFontSize` | `number` | Font size (clamped 10–24) |
| `_hasHydrated` | `boolean` | Whether `persist` has hydrated from localStorage |

### Key Actions

| Action | Behavior |
|---|---|
| `addPane(podKey)` | If pod already open, focuses that pane; otherwise creates new one and assigns grid position. Returns pane ID. |
| `removePane(id)` | Removes pane, selects next/first remaining pane as active. |
| `clearAllPanes()` | Removes all panes, resets active and `mobileActiveIndex`. |
| `setActivePane(id)` | Sets active pane, syncs `mobileActiveIndex`. |
| `setMobileActiveIndex(i)` | Sets index, syncs `activePane`. Guards against out-of-range values. |
| `setGridLayout(layout)` | Updates grid configuration. |
| `updatePanePosition(id, pos)` | Updates `gridPosition` for drag-and-drop layout. |
| `setTerminalFontSize(size)` | Clamps to [10, 24] before storing. |
| `getPaneByPodKey(podKey)` | Lookup helper returning `Pane \| undefined`. |
| `setHasHydrated(v)` | Called by `persist` after localStorage hydration. |

The workspace store is **not** connected to `RealtimeProvider`. It changes only when the user opens or closes terminal panes.

Sources: [web/src/stores/__tests__/workspace.test.ts:1-441](), [web/src/components/ide/sidebar/WorkspaceSidebarContent.tsx:44-45]()

---

## Store Relationship Diagram

This diagram maps the concrete store files and actions to the components and hooks that consume them.

```mermaid
flowchart TD
    subgraph "Stores"
        PS["usePodStore\nweb/src/stores/pod.ts\n\nupdatePodStatus\nupdateAgentStatus\nupdatePodTitle\nupdatePodInitProgress\nfetchPod\nfetchSidebarPods\nloadMorePods\ncreate/terminatePod"]
        RS["useRunnerStore\nweb/src/stores/runner.ts\n\nupdateRunnerStatus\nfetchRunners\nfetchAvailableRunners"]
        CS["useChannelStore\nweb/src/stores/channel.ts\n\naddMessage\nfetchMessages\nsendMessage"]
        WS["useWorkspaceStore\nweb/src/stores/workspace.ts\n\naddPane\nremovePane\nsetActivePane"]
    end

    subgraph "Providers and Hooks"
        RP["RealtimeProvider\nweb/src/providers/RealtimeProvider.tsx"]
        UPS["usePodStatus\nweb/src/hooks/usePodStatus.ts"]
    end

    subgraph "Components"
        WSC["WorkspaceSidebarContent\nweb/src/components/ide/sidebar/\nWorkspaceSidebarContent.tsx"]
        CCP["ChannelChatPanel"]
        Other["Mesh / Ticket / Autopilot pages"]
    end

    RP -->|"getState() calls"| PS
    RP -->|"getState() calls"| RS
    RP -->|"getState() calls"| CS

    PS -->|"pods, loading, fetchSidebarPods\nloadMorePods, terminatePod"| WSC
    RS -->|"runners, loading, fetchRunners"| WSC
    WS -->|"addPane, panes"| WSC

    UPS -->|"reads pods[]\nfor pod_key"| PS
    UPS --> WSC

    CS -->|"currentChannel, messages\naddMessage"| CCP
```

Sources: [web/src/providers/RealtimeProvider.tsx:1-368](), [web/src/stores/pod.ts:1-413](), [web/src/stores/runner.ts:1-165](), [web/src/stores/channel.ts:1-272](), [web/src/components/ide/sidebar/WorkspaceSidebarContent.tsx:1-273]()

---

## `usePodStatus` Hook

**File:** [web/src/hooks/usePodStatus.ts]()

A convenience hook for tracking a specific pod's readiness within a component. It:

1. Selects the pod from `usePodStore` using a granular selector `state.pods.find(p => p.pod_key === podKey)` — minimizes re-renders to only when that specific pod changes.
2. Calls `fetchPod(podKey)` once on mount if the pod isn't already in the store.
3. Retries up to `MAX_FETCH_RETRIES = 3` on transient failures, stopping permanently on a 404.
4. Live store data (from WebSocket events) always overrides a fetch error, so a transient network failure won't permanently shadow a pod that later becomes available via real-time updates.

Returns `{ podStatus, isPodReady, podError }`.

Terminal states mapped to `podError`:

| Status | `podError` value |
|---|---|
| `"failed"` | `"Pod failed"` |
| `"terminated"` | `"Pod terminated"` |
| `"orphaned"` | `"Pod orphaned - Runner connection lost"` |
| `"error"` | `storePod.error_message \|\| "Pod error"` |
| all others | `null` |

Sources: [web/src/hooks/usePodStatus.ts:1-82]()

---

## Loop Run Event Debouncing

Loop run events (`loop_run:started`, `loop_run:completed`, `loop_run:failed`) can fire rapidly in bursts. `RealtimeProvider` coalesces them with a 500ms debounce using a `loopDebounceRef` ref rather than a module-level timer, ensuring the timer is cleaned up when the component unmounts.

```mermaid
sequenceDiagram
    participant B as "Backend"
    participant R as "RealtimeProvider"
    participant L as "useLoopStore"

    B->>R: "loop_run:completed (run 1)"
    R->>R: "clearTimeout, setTimeout(500ms)"
    B->>R: "loop_run:completed (run 2)"
    R->>R: "clearTimeout, setTimeout(500ms)"
    B->>R: "loop_run:completed (run 3)"
    R->>R: "clearTimeout, setTimeout(500ms)"
    Note over R: "500ms passes"
    R->>L: "fetchLoops()"
    R->>L: "fetchLoop(slug) + fetchRuns(slug)"
```

Sources: [web/src/providers/RealtimeProvider.tsx:55-57](), [web/src/providers/RealtimeProvider.tsx:290-310](), [web/src/providers/RealtimeProvider.tsx:335-342]()

---

# Page: Environment and API Configuration

# Environment and API Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [web-admin/next.config.ts](web-admin/next.config.ts)
- [web-admin/src/lib/api/base.ts](web-admin/src/lib/api/base.ts)
- [web/next.config.ts](web/next.config.ts)
- [web/src/lib/env.ts](web/src/lib/env.ts)

</details>



This page documents how the web frontend (`web/`) and web admin (`web-admin/`) resolve API endpoint URLs at runtime. It covers the environment variable hierarchy, deployment-scenario handling, Next.js rewrite proxying for local development, and the `ApiClient` abstraction used in the admin panel.

For backend configuration (environment variables consumed by the Go server), see [Backend Configuration](#2.7). For the web admin application itself, see [Web Admin](#6).

---

## Overview

Both `web` and `web-admin` must connect to the same backend API, but the correct base URL differs across deployment scenarios: SaaS production, on-premise IP-only access, and local development. Rather than hardcoding a URL, the applications apply a resolution hierarchy at runtime and expose a small set of helper functions from `web/src/lib/env.ts`.

---

## URL Resolution Hierarchy

All URL resolver functions (`getApiBaseUrl`, `getWsBaseUrl`, `getOAuthBaseUrl`) follow the same four-step priority order:

**Resolution order (highest to lowest priority)**

```mermaid
flowchart TD
    A["Call getApiBaseUrl / getWsBaseUrl / getOAuthBaseUrl"]
    B["NEXT_PUBLIC_API_URL explicitly set?"]
    C["Return explicit env var value\n(empty string = relative path)"]
    D["window available (browser)?"]
    E["Return window.location.origin"]
    F["NEXT_PUBLIC_PRIMARY_DOMAIN set\n(not a placeholder)?"]
    G["Derive URL from PRIMARY_DOMAIN + USE_HTTPS"]
    H["Return localhost fallback\n(http://localhost:10000)"]

    A --> B
    B -- "yes" --> C
    B -- "no" --> D
    D -- "yes" --> E
    D -- "no (SSR)" --> F
    F -- "yes" --> G
    F -- "no" --> H
```

Sources: [web/src/lib/env.ts:92-114]()

> **Note on `NEXT_PUBLIC_API_URL=""`**: An empty string is a valid, intentional value meaning "use relative paths via Next.js rewrites". The resolver returns `""` immediately on this check. This is distinct from the variable being absent.

---

## Environment Variables Reference

| Variable | Scope | Purpose |
|---|---|---|
| `PRIMARY_DOMAIN` | Server-only (build/run) | Canonical domain, e.g. `agentsmesh.cn`. Mapped to `NEXT_PUBLIC_PRIMARY_DOMAIN` via `next.config.ts`. |
| `USE_HTTPS` | Server-only (build/run) | `"true"` / `"false"`. Mapped to `NEXT_PUBLIC_USE_HTTPS`. |
| `NEXT_PUBLIC_PRIMARY_DOMAIN` | Client-accessible | Exposed by Next.js from `PRIMARY_DOMAIN`. Placeholder `__PRIMARY_DOMAIN__` replaced by `docker-entrypoint.sh` at container start. |
| `NEXT_PUBLIC_USE_HTTPS` | Client-accessible | Exposed by Next.js from `USE_HTTPS`. Placeholder `__USE_HTTPS__` replaced at runtime. |
| `NEXT_PUBLIC_API_URL` | Client-accessible | Overrides all derivation logic. Set to `""` in local dev (enables proxy mode). |
| `NEXT_PUBLIC_WS_URL` | Client-accessible | Explicit WebSocket URL. Falls back to converting `NEXT_PUBLIC_API_URL` scheme (`http→ws`). |
| `NEXT_PUBLIC_OAUTH_URL` | Client-accessible | Explicit OAuth redirect base URL. Required when OAuth callback differs from the API URL. |
| `API_PROXY_TARGET` | Server-only (dev) | Written by `dev.sh` to `.env.local`. Used by Next.js rewrites to forward `/api/*` to the local backend. |
| `ALLOWED_DEV_ORIGINS` | Server-only (build) | Comma-separated list of origins allowed during Next.js development server. |

Sources: [web/src/lib/env.ts:1-36](), [web/next.config.ts:27-33](), [web-admin/next.config.ts:11-17]()

---

## Placeholder Substitution Mechanism

`PRIMARY_DOMAIN` and `USE_HTTPS` are **server-side** variables. If they were inlined at build time into client bundles, the Docker image would be permanently bound to specific values baked during the CI build.

To avoid this, `next.config.ts` emits placeholder strings when the variables are not set at build time:

[web/next.config.ts:27-33]()

At container startup, `docker-entrypoint.sh` replaces `__PRIMARY_DOMAIN__` and `__USE_HTTPS__` in the built JavaScript with the actual values from the container's environment. The helper `getPrimaryDomain()` and `isHttpsEnabled()` guard against un-replaced placeholders by checking for the `__` prefix:

[web/src/lib/env.ts:46-60]()

---

## Exported URL Functions

All functions are exported from `web/src/lib/env.ts`.

### `getApiBaseUrl()`

Returns the base URL for REST API calls (e.g., `fetch("/api/v1/...")`).

- In local dev (proxy mode): returns `""` so that `fetch("/api/v1/...")` uses relative paths that Next.js rewrites forward to the backend.
- In the browser (production/on-premise): returns `window.location.origin`.
- SSR: derives from `PRIMARY_DOMAIN`.

[web/src/lib/env.ts:92-114]()

### `getWsBaseUrl()`

Returns the base URL for WebSocket connections (must be an absolute URL; WebSocket cannot go through Next.js rewrites).

Special case: when `NEXT_PUBLIC_API_URL=""` (local dev proxy mode), REST is proxied but WebSocket is not. In this case the function falls back to `PRIMARY_DOMAIN`-derived `ws://` or `wss://`, not `window.location.origin`, because `window.location` would incorrectly point to the Next.js dev server port rather than the backend.

[web/src/lib/env.ts:145-177]()

### `getOAuthBaseUrl()`

Returns the base URL for OAuth redirect links. Because OAuth involves browser-level redirects directly to the backend (not proxied), this always returns an absolute URL.

[web/src/lib/env.ts:120-139]()

### `getServerUrl()` and `getServerUrlSSR()`

Used specifically for runner registration instructions displayed to the user (not for internal API calls).

- `getServerUrl()`: browser-only, returns `window.location.origin`. Using it in SSR causes a hydration mismatch.
- `getServerUrlSSR()`: safe for SSR; returns `NEXT_PUBLIC_API_URL` or the hardcoded default `https://agentsmesh.ai`.

[web/src/lib/env.ts:188-215]()

---

## Deployment Scenarios

```mermaid
flowchart LR
    subgraph "SaaS Production"
        S1["PRIMARY_DOMAIN=agentsmesh.cn\nUSE_HTTPS=true"]
        S2["NEXT_PUBLIC_PRIMARY_DOMAIN=agentsmesh.cn\nNEXT_PUBLIC_USE_HTTPS=true"]
        S3["API → https://agentsmesh.cn\nWS → wss://agentsmesh.cn"]
        S1 --> S2 --> S3
    end

    subgraph "Local Development (dev.sh)"
        L1["NEXT_PUBLIC_API_URL=''\nAPI_PROXY_TARGET=http://localhost:10000"]
        L2["Next.js rewrites\n/api/* → localhost:10000/api/*"]
        L3["WS → derived from PRIMARY_DOMAIN\nor ws://localhost:10000"]
        L1 --> L2
        L1 --> L3
    end

    subgraph "On-Premise / IP Access"
        O1["No env vars configured"]
        O2["Browser: window.location.origin\n(e.g. http://192.168.1.100:3000)"]
        O3["API → http://192.168.1.100:3000\nWS → ws://192.168.1.100:3000"]
        O1 --> O2 --> O3
    end
```

Sources: [web/src/lib/env.ts:1-36](), [web/next.config.ts:38-58]()

---

## Next.js Rewrite Proxy (Local Development)

When `NODE_ENV=development` and `API_PROXY_TARGET` is set (written to `.env.local` by `dev.sh`), `next.config.ts` installs rewrites that forward API traffic to the local backend:

[web/next.config.ts:38-58]()

| Incoming path | Forwarded to |
|---|---|
| `/api/:path*` | `${API_PROXY_TARGET}/api/:path*` |
| `/health` | `${API_PROXY_TARGET}/health` |

This allows the frontend to make calls to `/api/v1/...` without CORS issues during development. The rewrite is only active when both `NODE_ENV=development` and `API_PROXY_TARGET` are present.

The `web-admin` app uses a similar pattern but derives its proxy target from `PRIMARY_DOMAIN` rather than a dedicated `API_PROXY_TARGET` variable:

[web-admin/next.config.ts:20-34]()

Sources: [web/next.config.ts:38-58](), [web-admin/next.config.ts:20-34]()

---

## `ApiClient` (web-admin)

The web admin panel uses a class-based `ApiClient` in `web-admin/src/lib/api/base.ts`. The web frontend uses individual `fetch` wrappers in each API module; `ApiClient` centralizes this for the admin panel.

**`ApiClient` structure and wiring**

```mermaid
classDiagram
    class ApiClient {
        -baseUrl: string
        +get(endpoint, params)
        +post(endpoint, data)
        +put(endpoint, data)
        +patch(endpoint, data)
        +delete(endpoint, data)
        +postFormData(endpoint, formData)
        -request(endpoint, options)
    }

    class "getApiUrl()" {
        <<function>>
        "NEXT_PUBLIC_API_URL || window.location.origin"
        "|| PRIMARY_DOMAIN-derived || localhost:10000"
    }

    class apiClient {
        <<singleton>>
        "baseUrl = API_URL + /api/v1/admin"
    }

    ApiClient --> "getApiUrl()" : "constructed with"
    apiClient --> ApiClient : "instance of"
```

The `request` private method on `ApiClient`:
- Injects `Authorization: Bearer <token>` from `getAuthToken()` on every request.
- Calls `useAuthStore.getState().logout()` and throws on a `401` response, expiring the session.
- Throws a typed `ApiError` (`{ error: string, status: number }`) on any other non-OK response.

The exported singleton `apiClient` is instantiated with the base path `/api/v1/admin`:

[web-admin/src/lib/api/base.ts:33](), [web-admin/src/lib/api/base.ts:167]()

The `getApiUrl()` function inside `web-admin/src/lib/api/base.ts` mirrors the logic of `getApiBaseUrl()` from `web/src/lib/env.ts` but is a local implementation without the proxy-mode (`""`) handling, since the admin panel always uses an absolute URL.

[web-admin/src/lib/api/base.ts:7-31]()

Sources: [web-admin/src/lib/api/base.ts:1-167]()

---

## Function-to-Deployment-Scenario Matrix

| Function | Local Dev (`API_URL=""`) | Browser (on-premise) | SSR / Build-time |
|---|---|---|---|
| `getApiBaseUrl()` | `""` (relative path) | `window.location.origin` | `PRIMARY_DOMAIN`-derived or `localhost:10000` |
| `getWsBaseUrl()` | `PRIMARY_DOMAIN`-derived or `ws://localhost:10000` | `ws(s)://window.location.host` | `PRIMARY_DOMAIN`-derived or `ws://localhost:10000` |
| `getOAuthBaseUrl()` | `""` → `window.location.origin` | `window.location.origin` | `PRIMARY_DOMAIN`-derived or `localhost:10000` |
| `getServerUrl()` | `window.location.origin` | `window.location.origin` | ⚠️ Not safe for SSR (use `getServerUrlSSR()`) |
| `getServerUrlSSR()` | `NEXT_PUBLIC_API_URL` or `https://agentsmesh.ai` | (same) | `NEXT_PUBLIC_API_URL` or `https://agentsmesh.ai` |

Sources: [web/src/lib/env.ts:92-216]()

---

# Page: Web Admin

# Web Admin

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/internal/api/rest/v1/admin/subscriptions.go](backend/internal/api/rest/v1/admin/subscriptions.go)
- [backend/internal/api/rest/v1/invitations.go](backend/internal/api/rest/v1/invitations.go)
- [backend/internal/api/rest/v1/pods.go](backend/internal/api/rest/v1/pods.go)
- [backend/internal/api/rest/v1/repositories.go](backend/internal/api/rest/v1/repositories.go)
- [backend/internal/domain/organization/organization.go](backend/internal/domain/organization/organization.go)
- [backend/internal/service/billing/service.go](backend/internal/service/billing/service.go)
- [backend/internal/service/billing/subscription.go](backend/internal/service/billing/subscription.go)
- [backend/internal/service/organization/interface.go](backend/internal/service/organization/interface.go)
- [backend/internal/service/organization/service.go](backend/internal/service/organization/service.go)
- [backend/migrations/000053_fix_missing_subscriptions.down.sql](backend/migrations/000053_fix_missing_subscriptions.down.sql)
- [backend/migrations/000053_fix_missing_subscriptions.up.sql](backend/migrations/000053_fix_missing_subscriptions.up.sql)
- [web-admin/next.config.ts](web-admin/next.config.ts)
- [web-admin/src/app/(dashboard)/organizations/[id]/_components/subscription-section.tsx](web-admin/src/app/(dashboard)/organizations/[id]/_components/subscription-section.tsx)
- [web-admin/src/lib/api/base.ts](web-admin/src/lib/api/base.ts)
- [web/next.config.ts](web/next.config.ts)
- [web/src/lib/env.ts](web/src/lib/env.ts)

</details>



The Web Admin (`web-admin/`) is a standalone Next.js application that serves as an internal operator console for the AgentsMesh platform. It is separate from the main user-facing frontend (see [Web Frontend](#5)) and is intended for platform administrators — not end users. Its primary responsibilities are organization administration and subscription lifecycle management.

---

## Application Structure

The web-admin is a Next.js application built with `output: "standalone"`. It uses a dashboard layout with routes under `src/app/(dashboard)/`. The application authenticates via a bearer token stored in a Zustand store (`useAuthStore`) and communicates with the backend exclusively through the `/api/v1/admin` route group (see [REST API Routes](#2.1) for backend route registration).

**Application layout — key files:**

| Path | Purpose |
|---|---|
| `web-admin/next.config.ts` | Next.js configuration, domain env mapping, API proxying |
| `web-admin/src/lib/api/base.ts` | `ApiClient` class and URL resolution |
| `web-admin/src/lib/api/admin.ts` | Domain-specific API functions (typed wrappers) |
| `web-admin/src/stores/auth.ts` | Auth state and token management |
| `web-admin/src/app/(dashboard)/organizations/[id]/` | Per-organization admin views |

Sources: [web-admin/next.config.ts:1-51](), [web-admin/src/lib/api/base.ts:1-167]()

---

## API Client

The `ApiClient` class in `web-admin/src/lib/api/base.ts` is the single HTTP abstraction used by all admin API functions. It is instantiated once and exported as `apiClient`.

**Instantiation:**
```
export const apiClient = new ApiClient(`${API_URL}/api/v1/admin`);
```

The base URL is resolved at module load time by `getApiUrl()` [web-admin/src/lib/api/base.ts:7-31]().

### URL Resolution

The `getApiUrl()` function resolves the backend base URL using the following priority:

```mermaid
flowchart TD
    A["getApiUrl()"] --> B{"NEXT_PUBLIC_API_URL set?"}
    B -->|"Yes"| C["Use NEXT_PUBLIC_API_URL"]
    B -->|"No"| D{"Browser environment?"}
    D -->|"Yes"| E["Use window.location.origin"]
    D -->|"No (SSR)"| F{"PRIMARY_DOMAIN set?"}
    F -->|"Yes"| G["Derive from PRIMARY_DOMAIN + USE_HTTPS"]
    F -->|"No"| H["http://localhost:10000"]
```

Sources: [web-admin/src/lib/api/base.ts:7-31]()

### Authentication

All requests from `ApiClient` attach a `Bearer` token header using `getAuthToken()`. On a `401` response, the client calls `useAuthStore.getState().logout()` to clear the session.

[web-admin/src/lib/api/base.ts:55-88]()

### Available Methods

| Method | Signature |
|---|---|
| `get` | `get<T>(endpoint, params?)` |
| `post` | `post<T>(endpoint, data?)` |
| `put` | `put<T>(endpoint, data?)` |
| `patch` | `patch<T>(endpoint, data?)` |
| `delete` | `delete<T>(endpoint, data?)` |
| `postFormData` | `postFormData<T>(endpoint, formData)` |

Sources: [web-admin/src/lib/api/base.ts:91-165]()

---

## Environment and Domain Configuration

The `web-admin/next.config.ts` mirrors the pattern used by the main web frontend (see [Environment and API Configuration](#5.6)). It maps backend-level variables to `NEXT_PUBLIC_*` counterparts at build time, using runtime-replaceable placeholders for Docker deployments.

**Variable mapping (build time):**

| Source Variable | NEXT_PUBLIC Variable | Default Placeholder |
|---|---|---|
| `PRIMARY_DOMAIN` | `NEXT_PUBLIC_PRIMARY_DOMAIN` | `__PRIMARY_DOMAIN__` |
| `USE_HTTPS` | `NEXT_PUBLIC_USE_HTTPS` | `__USE_HTTPS__` |

Placeholders are replaced at container startup by `docker-entrypoint.sh`. This avoids Next.js build-time constant folding that would hard-code environment values into the bundle.

The `next.config.ts` also registers an API rewrite rule that proxies `/api/*` to the backend:

```mermaid
flowchart LR
    B["Browser"] -->|"/api/:path*"| W["web-admin Next.js"]
    W -->|"rewrite → backendUrl/api/:path*"| BE["Backend"]
```

Sources: [web-admin/next.config.ts:1-51]()

---

## Subscription Management UI

The `SubscriptionSection` component [web-admin/src/app/(dashboard)/organizations/[id]/_components/subscription-section.tsx]() is the primary admin interface for managing an organization's subscription. It is rendered on the per-organization detail page.

### Component Decomposition

**Subscription management component tree:**

```mermaid
flowchart TD
    SS["SubscriptionSection"] --> PSP["PlanStatusPanel"]
    SS --> BDP["BillingDetailsPanel"]
    SS --> SP["SeatsPanel"]
    SS --> AP["ActionsPanel"]
    SS --> CQP["CustomQuotasPanel"]
    SS --> NSP["NoSubscriptionPanel"]
    NSP -->|"when no subscription exists"| CS["createSubscription()"]
    PSP --> UP["updateSubscriptionPlan()"]
    BDP --> UC["updateSubscriptionCycle()"]
    BDP --> AR["setSubscriptionAutoRenew()"]
    SP --> US["updateSubscriptionSeats()"]
    AP --> F["freezeSubscription()"]
    AP --> UF["unfreezeSubscription()"]
    AP --> CA["cancelSubscription()"]
    AP --> R["renewSubscription()"]
    CQP --> SQ["setSubscriptionQuota()"]
```

Sources: [web-admin/src/app/(dashboard)/organizations/[id]/_components/subscription-section.tsx:72-358]()

### Sub-panels

| Component | Function |
|---|---|
| `PlanStatusPanel` | Displays plan name and status badge; provides an inline `<Select>` to change plan immediately |
| `BillingDetailsPanel` | Shows billing cycle, auto-renew toggle, and current period dates |
| `SeatsPanel` | Renders a seat usage progress bar and an input to set a new seat count |
| `ActionsPanel` | Provides Freeze/Unfreeze, Cancel, and Renew (with month count input) controls |
| `CustomQuotasPanel` | Displays per-resource quota overrides vs. plan defaults; allows setting new override values |
| `NoSubscriptionPanel` | Shown when `GET /subscription` returns 404; provides a form to create a new subscription |

The `CustomQuotasPanel` supports overrides for these resources, defined as `QUOTA_RESOURCES` [web-admin/src/app/(dashboard)/organizations/[id]/_components/subscription-section.tsx:43]():

- `users`
- `runners`
- `concurrent_pods`
- `repositories`
- `pod_minutes`

A limit value of `-1` represents unlimited.

---

## Backend Admin API

The web-admin calls backend endpoints under `/api/v1/admin`. The subscription-related routes are registered by `SubscriptionHandler` [backend/internal/api/rest/v1/admin/subscriptions.go:31-47]().

**Admin subscription API — route map:**

```mermaid
flowchart LR
    subgraph "SubscriptionHandler"
        direction TB
        G["GET  /organizations/:id/subscription"] --> GS["GetSubscription()"]
        GP["GET  /organizations/:id/subscription/plans"] --> LP["ListPlans()"]
        PC["POST /organizations/:id/subscription/create"] --> AC["AdminCreateSubscription()"]
        PU["PUT  /organizations/:id/subscription/plan"] --> UP["AdminUpdatePlan()"]
        SU["PUT  /organizations/:id/subscription/seats"] --> US["AdminUpdateSeats()"]
        CU["PUT  /organizations/:id/subscription/cycle"] --> UC["AdminUpdateCycle()"]
        PF["POST /organizations/:id/subscription/freeze"] --> FZ["Freeze()"]
        UF["POST /organizations/:id/subscription/unfreeze"] --> UN["Unfreeze()"]
        CA["POST /organizations/:id/subscription/cancel"] --> CX["Cancel()"]
        RN["POST /organizations/:id/subscription/renew"] --> RE["AdminRenew()"]
        AR["PUT  /organizations/:id/subscription/auto-renew"] --> SA["SetAutoRenew()"]
        QO["PUT  /organizations/:id/subscription/quotas"] --> SQ["SetCustomQuota()"]
    end
```

Sources: [backend/internal/api/rest/v1/admin/subscriptions.go:31-47]()

### Key Backend Behaviours

- **`AdminUpdatePlan`**: Directly changes the plan in the database without checking payment constraints. Syncs the redundant `subscription_plan` field in the `organizations` table. [backend/internal/api/rest/v1/admin/subscriptions.go:132-167]()
- **`AdminRenew`**: Extends the period from `current_period_end` or `now`, whichever is later. Reactivates canceled or frozen subscriptions. [backend/internal/service/billing/subscription.go:179-213]()
- **`AdminCancelSubscription`**: Marks the subscription as canceled without calling any external payment provider API (Stripe, LemonSqueezy, etc.). [backend/internal/service/billing/subscription.go:217-236]()
- **`AdminCreateSubscription`**: Creates a new `active` subscription for organizations missing a record. Fails with `ErrSubscriptionAlreadyExists` if one already exists. [backend/internal/service/billing/subscription.go:95-138]()
- **`SetCustomQuota`**: Persists a per-resource limit override in the `custom_quotas` JSON field of the subscription record, independent of the plan's default limits.

All mutating handlers call `logAction()` which delegates to `LogAdminAction()` to write audit records via `adminservice.Service`. [backend/internal/api/rest/v1/admin/subscriptions.go:407-409]()

### Subscription Response Shape

The `subscriptionResponse()` helper [backend/internal/api/rest/v1/admin/subscriptions.go:418-474]() assembles the JSON response body. Key fields:

| Field | Type | Description |
|---|---|---|
| `status` | string | `active`, `trialing`, `frozen`, `canceled`, `expired` |
| `billing_cycle` | string | `monthly` or `yearly` |
| `current_period_start` / `current_period_end` | timestamp | Current billing period |
| `seat_count` | int | Allocated seats |
| `seat_usage` | object | `used_seats`, `total_seats`, `available_seats` |
| `custom_quotas` | object | Per-resource limit overrides (null if none set) |
| `has_stripe` / `has_alipay` / `has_wechat` / `has_lemonsqueezy` | bool | Payment provider presence flags |
| `downgrade_to_plan` | string? | Pending plan downgrade scheduled at period end |
| `plan` | object | Full plan details including limits |

---

## Relationship to Backend Billing Service

The web-admin does not contact the billing service directly — all interactions go through the backend's admin REST API. The admin API handlers hold references to both `adminservice.Service` and `billingservice.Service`.

```mermaid
flowchart LR
    WA["web-admin\nApiClient"] -->|"HTTP /api/v1/admin"| SH["SubscriptionHandler\n(backend/internal/api/rest/v1/admin)"]
    SH --> BS["billingservice.Service\n(backend/internal/service/billing)"]
    SH --> AS["adminservice.Service\n(backend/internal/service/admin)"]
    BS --> DB[("PostgreSQL\nsubscriptions table")]
    AS --> AuditDB[("PostgreSQL\nadmin_audit_logs table")]
```

Sources: [backend/internal/api/rest/v1/admin/subscriptions.go:17-28](), [backend/internal/service/billing/subscription.go:1-50]()

For background on how subscriptions are modeled and what plan-level constraints exist, see [Billing and Subscriptions](#2.6).

---

# Page: Development Environment

# Development Environment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude/skills/worktree/SKILL.md](.claude/skills/worktree/SKILL.md)
- [CLAUDE.md](CLAUDE.md)
- [deploy/dev/.gitignore](deploy/dev/.gitignore)
- [deploy/dev/backend.Dockerfile](deploy/dev/backend.Dockerfile)
- [deploy/dev/dev.sh](deploy/dev/dev.sh)
- [deploy/dev/docker-compose.yml](deploy/dev/docker-compose.yml)
- [deploy/dev/gitea/init-gitea.sh](deploy/dev/gitea/init-gitea.sh)
- [deploy/dev/init-seed.sh](deploy/dev/init-seed.sh)
- [deploy/dev/nginx/conf.d/default.conf](deploy/dev/nginx/conf.d/default.conf)
- [deploy/dev/nginx/nginx.conf](deploy/dev/nginx/nginx.conf)
- [deploy/dev/runner-entrypoint.sh](deploy/dev/runner-entrypoint.sh)
- [deploy/dev/runner-ssh/id_ed25519.pub](deploy/dev/runner-ssh/id_ed25519.pub)
- [deploy/dev/runner.Dockerfile](deploy/dev/runner.Dockerfile)
- [deploy/dev/seed/seed.sql](deploy/dev/seed/seed.sql)
- [deploy/dev/traefik/dynamic/grpc.yml](deploy/dev/traefik/dynamic/grpc.yml)
- [deploy/dev/web.Dockerfile](deploy/dev/web.Dockerfile)
- [relay/.air.toml](relay/.air.toml)
- [runner/.gitignore](runner/.gitignore)
- [runner/internal/config/config_grpc_test.go](runner/internal/config/config_grpc_test.go)
- [runner/internal/envpath/envpath_test.go](runner/internal/envpath/envpath_test.go)
- [web/src/components/ui/block-editor.tsx](web/src/components/ui/block-editor.tsx)
- [web/src/lib/api/base.ts](web/src/lib/api/base.ts)

</details>



This page covers the local development environment setup for AgentsMesh: the `dev.sh` one-click script, how it configures and starts all services, worktree port isolation, seed data, and common workflows.

For details on each individual Docker Compose service (images, volumes, health checks), see [Docker Compose Services](#7.1). For the local runner binary build process and Gitea initialization, see [Local Runner and Gitea Setup](#7.2).

---

## Overview

The development environment lives entirely under `deploy/dev/`. The entry point is a single script, `deploy/dev/dev.sh`, which handles all first-time setup and idempotent restarts. It starts Docker backend services while the web frontend runs on the host for faster Turbopack iteration.

**Key design decisions:**
- Multiple git worktrees can run simultaneously with isolated port ranges.
- The frontend (`web/`) runs locally via `pnpm dev --turbopack`, not in Docker.
- All URLs (API, WebSocket, OAuth callbacks) derive from a single `PRIMARY_DOMAIN` variable.
- Hot reload is enabled for backend, runner, and relay via [Air](https://github.com/air-verse/air).

---

## Prerequisites

| Tool | Minimum Version | Purpose |
|------|----------------|---------|
| Docker Desktop | 4.x | All backend services |
| `pnpm` | 8.x | Frontend dependency management |
| `git` | 2.x | Worktree support |
| `openssl` | 3.x | Dev SSL cert generation |
| `ssh-keygen` | bundled with OpenSSH | Gitea deploy key generation |

---

## Quick Start

```bash
cd deploy/dev
./dev.sh               # First-time setup and start
./dev.sh --clean       # Stop all services and remove volumes
./dev.sh --reset-runners  # Kill stale runner processes and restart containers
```

After `./dev.sh` completes, the environment is ready:

| Service | Address | Notes |
|---------|---------|-------|
| Frontend | `http://localhost:<WEB_PORT>` | Next.js, Turbopack, local process |
| API | `http://localhost:<HTTP_PORT>/api` | Via Traefik |
| Relay (WebSocket) | `ws://localhost:<HTTP_PORT>/relay` | Via Traefik |
| gRPC (mTLS) | `grpcs://localhost:<GRPC_PORT>` | TLS passthrough via Traefik |
| Gitea | `http://localhost:<GITEA_HTTP_PORT>` | `gitea-admin` / `gitea-admin-123` |
| Traefik Dashboard | `http://localhost:<TRAEFIK_DASHBOARD_PORT>` | |
| Adminer | `http://localhost:<ADMINER_PORT>` | |
| MinIO Console | `http://localhost:<MINIO_CONSOLE_PORT>` | |

Test accounts (seeded automatically):
- **User**: `dev@agentsmesh.local` / `devpass123`
- **Admin**: `admin@agentsmesh.local` / `adminpass123`

Sources: [deploy/dev/dev.sh:626-655](), [CLAUDE.md:33-48]()

---

## Initialization Flow

The `main()` function in `dev.sh` runs the following steps in order:

**`dev.sh` Initialization Sequence**

```mermaid
flowchart TD
    A["main()"] --> B["generate_ssl_certs()"]
    B --> C["generate_ai_cli_configs()"]
    C --> D["generate_env()"]
    D --> E["generate_traefik_config()"]
    E --> F["generate_web_env()"]
    F --> G["docker compose up -d --build"]
    G --> H["wait_for_service(postgres)"]
    H --> I["run_migrations()"]
    I --> J["init_seed(pg_container)"]
    J --> K["generate_runner_ssh_key()"]
    K --> L["init_gitea()"]
    L --> M["setup_gitea_ssh_config()"]
    M --> N["chown /workspace (runner container)"]
    N --> O["start_frontend()"]
    O --> P["build_runner_local()"]
    P --> Q["show_result()"]

    B -->|"ssl/ca.crt already exists"| skip1["skip"]
    D -->|".env matches current project"| skip2["preserve existing ports"]
    J -->|"dev@agentsmesh.local exists"| skip3["skip"]
    P -->|"source hash unchanged"| skip4["skip build"]
```

Sources: [deploy/dev/dev.sh:804-893]()

---

### Step Details

#### Step 1–2: SSL Certs and AI CLI Configs

`generate_ssl_certs()` calls `generate-dev-certs.sh` to produce a CA keypair at `deploy/dev/ssl/ca.crt` and `ca.key`. These are used for mTLS between the backend and runners.

`generate_ai_cli_configs()` writes pre-configured settings for Claude Code (`settings.json`), OpenAI Codex (`config.toml`), and Gemini CLI (`settings.json`) to `deploy/dev/ai-cli-configs/`. These are copied into the runner container image by [deploy/dev/runner.Dockerfile:98-100]().

Sources: [deploy/dev/dev.sh:72-127]()

#### Step 3: `.env` Generation and Port Allocation

`generate_env()` computes a port offset from the current worktree name. Ports are spaced 50 apart per worktree, giving a range that supports up to 500 concurrent worktrees.

```
HTTP_PORT   = 10000 + offset * 50
GRPC_PORT   = 10001 + offset * 50
POSTGRES_PORT = 10002 + offset * 50
...
GITEA_SSH_PORT = 10010 + offset * 50
```

The `main` worktree always gets offset `0` (ports starting at `10000`). Other worktrees get a deterministic offset from an MD5 hash of the branch name.

If `.env` already exists for the current `COMPOSE_PROJECT_NAME`, `generate_env()` preserves the existing ports to keep runner configurations stable.

Sources: [deploy/dev/dev.sh:42-244]()

**Port Allocation Scheme**

```mermaid
flowchart LR
    subgraph "Worktree: main (offset=0)"
        H0["HTTP_PORT=10000"]
        G0["GRPC_PORT=10001"]
        P0["POSTGRES_PORT=10002"]
        R0["REDIS_PORT=10003"]
        W0["WEB_PORT=10007"]
    end
    subgraph "Worktree: feature-xyz (offset=N)"
        HN["HTTP_PORT=10000+N*50"]
        GN["GRPC_PORT=10001+N*50"]
        PN["POSTGRES_PORT=10002+N*50"]
        RN["REDIS_PORT=10003+N*50"]
        WN["WEB_PORT=10007+N*50"]
    end
```

Sources: [deploy/dev/dev.sh:185-220]()

#### Step 4–5: Traefik and Web `.env.local`

`generate_traefik_config()` writes `deploy/dev/traefik/traefik.yml` with the Docker Compose project name embedded so Traefik only discovers containers from the current worktree's project. This prevents cross-worktree routing conflicts.

`generate_web_env()` writes `web/.env.local` with:
- `PRIMARY_DOMAIN=localhost:<HTTP_PORT>`
- `NEXT_PUBLIC_WS_URL=ws://127.0.0.1:<HTTP_PORT>` (direct; Next.js rewrites don't support WebSocket proxy)
- `API_PROXY_TARGET=http://127.0.0.1:<HTTP_PORT>` (server-side proxy target)

Sources: [deploy/dev/dev.sh:129-283]()

#### Step 6–8: Docker Services, Migrations, and Seed Data

`docker compose up -d --build` starts all services defined in `docker-compose.yml`. The backend container image includes `golang-migrate`, and `run_migrations()` executes it inside the running container:

```bash
docker exec <backend_container> migrate \
  -path /app/migrations \
  -database "postgres://agentsmesh:agentsmesh_dev@postgres:5432/agentsmesh?sslmode=disable" \
  up
```

`init_seed()` checks whether `dev@agentsmesh.local` already exists before applying `deploy/dev/seed/seed.sql`.

Sources: [deploy/dev/dev.sh:301-409](), [deploy/dev/seed/seed.sql:1-289]()

#### Steps 9–9.6: Gitea, SSH Keys

`generate_runner_ssh_key()` creates an ed25519 keypair at `deploy/dev/runner-ssh/id_ed25519` if absent. The private key is gitignored.

`init_gitea()` calls `deploy/dev/gitea/init-gitea.sh`, which:
1. Creates the `gitea-admin` user via the Gitea CLI.
2. Creates the `dev-org` organization.
3. Creates and seeds `demo-webapp` and `demo-api` repositories from `deploy/dev/gitea/repos/`.
4. Registers the runner's public key as a deploy key on both repos.

`setup_gitea_ssh_config()` injects a `Host gitea` block into `~/.ssh/config`, mapping `gitea` → `127.0.0.1:<GITEA_SSH_PORT>`. This lets local runners clone `git@gitea:org/repo.git` URLs from outside Docker. The block is managed (removed and rewritten on each run) to stay in sync with port changes.

Sources: [deploy/dev/dev.sh:437-497](), [deploy/dev/gitea/init-gitea.sh:1-244]()

#### Step 10–11.5: Frontend and Runner Binary

`start_frontend()` runs `pnpm dev --turbopack --port <WEB_PORT>` in the background, logging to `deploy/dev/web.log`. It detects stale Next.js lock files and clears the Turbopack cache before restarting.

`build_runner_local()` compiles the runner binary for `darwin/arm64` inside a Docker container (using `golang:1.25-alpine`) so no local Go installation is required. The output is installed to `~/.local/bin/agentsmesh-runner`. A source hash (based on `git rev-parse HEAD:runner HEAD:proto` plus uncommitted diffs) is cached in `runner/.local-build-hash`; the build is skipped when source is unchanged.

Sources: [deploy/dev/dev.sh:658-802]()

---

## Docker Service Architecture

**Docker Compose Network Topology**

```mermaid
flowchart TB
    Browser["Browser"]
    LocalFrontend["Next.js\n(local host process)\nWEB_PORT"]
    LocalRunner["agentsmesh-runner\n(local binary)\n~/.local/bin/"]

    subgraph "Docker Network: agentsmesh-<worktree>_default"
        Traefik["traefik\nHTTP_PORT -> :80\nGRPC_PORT -> :9443\nDASHBOARD_PORT -> :8080"]
        Backend["backend\n:8080\nAir hot reload"]
        Runner["runner\n:9090\nAir hot reload"]
        Relay["relay\n:8090\nAir hot reload"]
        Postgres["postgres\n:5432"]
        Redis["redis\n:6379"]
        MinIO["minio\n:9000 (API)\n:9001 (Console)"]
        Gitea["gitea\n:3000 (HTTP)\n:22 (SSH)"]
        Adminer["adminer\n:8080"]
    end

    Browser -->|"HTTP /api"| Traefik
    Browser -->|"ws /relay"| Traefik
    LocalFrontend -->|"API_PROXY_TARGET (server-side)"| Traefik
    LocalFrontend -->|"NEXT_PUBLIC_WS_URL (direct WS)"| Traefik
    LocalRunner -->|"grpcs GRPC_PORT"| Traefik

    Traefik -->|"/api PathPrefix"| Backend
    Traefik -->|"/relay PathPrefix + strip"| Relay
    Traefik -->|"TCP TLS passthrough :9443"| Backend

    Backend --> Postgres
    Backend --> Redis
    Backend --> MinIO
    Backend -->|"internal HTTP"| Relay

    Runner -->|"gRPC mTLS traefik:9443"| Traefik
    Runner -->|"SSH git@gitea"| Gitea
    Runner -->|"REST http://backend:8080"| Backend
```

Sources: [deploy/dev/docker-compose.yml:1-420](), [deploy/dev/traefik/dynamic/grpc.yml:1-20]()

---

## Seed Data

The seed script `deploy/dev/seed/seed.sql` is idempotent (uses `WHERE NOT EXISTS`). It creates:

| Entity | Value |
|--------|-------|
| User | `dev@agentsmesh.local` / `devpass123` |
| Admin | `admin@agentsmesh.local` / `adminpass123` |
| Organization | `dev-org` (slug), Pro plan, active |
| Runner | node_id `dev-runner`, org `dev-org` |
| Runner token | `dev-runner-token` (pre-hashed bcrypt) |
| Tickets | `DEV-1`, `DEV-2` |
| Git provider | Local Gitea at `http://gitea:3000` |
| Repositories | `dev-org/demo-webapp`, `dev-org/demo-api` |

The runner Docker container's `runner-entrypoint.sh` generates its own mTLS client cert from the CA at startup and writes a `config.yaml` to `/home/runner/.agentsmesh/config.yaml`. The cert CN matches the `node_id` (`dev-runner`) and the org (`dev-org`).

Sources: [deploy/dev/seed/seed.sql:1-289](), [deploy/dev/runner-entrypoint.sh:255-301]()

---

## Hot Reload

All three Go services use [Air](https://github.com/air-verse/air) for automatic rebuild on file changes. Source code directories are bind-mounted into the containers.

| Service | Config | Watch scope |
|---------|--------|-------------|
| Backend | `backend/.air.toml` | `backend/` |
| Runner | `runner/.air.toml` | `runner/` |
| Relay | `relay/.air.toml` | `relay/` |

The relay Air config sets `kill_delay = "5s"` to ensure the old process releases port `8090` before the new binary attempts to bind it.

The frontend uses Next.js Turbopack fast refresh running on the host. If a stale `.next/dev/lock` file is detected, `start_frontend()` clears both the lock and the Turbopack cache before restarting.

Sources: [relay/.air.toml:1-52](), [deploy/dev/dev.sh:657-729](), [deploy/dev/docker-compose.yml:215-224]()

---

## Common Workflows

### Viewing Logs

```bash
# Frontend
tail -f deploy/dev/web.log

# Backend (in deploy/dev directory)
docker compose logs -f backend

# Runner
docker compose logs -f runner

# All services
docker compose logs -f
```

### Running Database Migrations

Migrations are run automatically by `dev.sh`. To run manually inside the backend container:

```bash
docker exec <COMPOSE_PROJECT_NAME>-backend-1 migrate \
  -path /app/migrations \
  -database "postgres://agentsmesh:agentsmesh_dev@postgres:5432/agentsmesh?sslmode=disable" \
  up
```

To create a new migration file (requires `golang-migrate` installed locally):

```bash
brew install golang-migrate
migrate create -ext sql -dir backend/migrations -seq add_new_feature
```

### Using a Local Runner Binary

After `dev.sh` builds and installs the runner to `~/.local/bin/agentsmesh-runner`, register and start it:

```bash
agentsmesh-runner register \
  --server http://localhost:<HTTP_PORT> \
  --token <TOKEN>

agentsmesh-runner run
```

The `--reset-runners` flag in `dev.sh` stops stale local runner processes and restarts the Docker runner and relay containers:

```bash
./dev.sh --reset-runners
```

### Working with Multiple Worktrees

Each git worktree gets an isolated `COMPOSE_PROJECT_NAME` (`agentsmesh-<worktree-name>`) and a unique port range. Worktrees can run simultaneously without conflicts.

```bash
# Create a worktree
git worktree add -b feature/my-feature ../AgentsMesh-Worktrees/feature-my-feature origin/main
cd ../AgentsMesh-Worktrees/feature-my-feature

# Start its own environment
cd deploy/dev && ./dev.sh
```

The `.env` file stores the computed port offset. If `.env` already exists for the project name, existing ports are preserved on subsequent `dev.sh` runs.

Sources: [deploy/dev/dev.sh:42-68](), [deploy/dev/dev.sh:171-245](), [deploy/dev/dev.sh:499-594](), [.claude/skills/worktree/SKILL.md:1-118]()

### Full Teardown

```bash
cd deploy/dev
./dev.sh --clean
```

This stops all containers, removes volumes, and deletes `.env`. Note that this also removes all database data, MinIO data, and Gitea data. Re-running `./dev.sh` will re-initialize everything from scratch.

Sources: [deploy/dev/dev.sh:596-623]()

---

## Environment Variables Reference

The generated `deploy/dev/.env` and `web/.env.local` share a unified domain configuration pattern. All service URLs are derived from two variables:

| Variable | Dev Default | Description |
|----------|-------------|-------------|
| `PRIMARY_DOMAIN` | `localhost:<HTTP_PORT>` | Base domain for all URLs |
| `USE_HTTPS` | `false` | Protocol scheme (`http` vs `https`) |
| `HTTP_PORT` | `10000` (main) | Traefik HTTP listener host port |
| `GRPC_PORT` | `10001` (main) | Traefik gRPC passthrough host port |
| `POSTGRES_PASSWORD` | `agentsmesh_dev` | Shared between backend and init scripts |
| `JWT_SECRET` | `dev-jwt-secret-...` | Must match between backend and relay |
| `INTERNAL_API_SECRET` | `dev-internal-secret` | Used by relay to call backend internal API |
| `ANTHROPIC_AUTH_TOKEN` | *(empty)* | Optional: fill in to use Claude Code |

The `COMPOSE_PROJECT_NAME` variable (set to `agentsmesh-<worktree>`) is the isolation key for all Docker resources: containers, networks, and volumes all receive this prefix.

Sources: [deploy/dev/dev.sh:195-243](), [deploy/dev/dev.sh:254-283](), [deploy/dev/docker-compose.yml:120-215]()

---

# Page: Docker Compose Services

# Docker Compose Services

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude/skills/worktree/SKILL.md](.claude/skills/worktree/SKILL.md)
- [CLAUDE.md](CLAUDE.md)
- [deploy/dev/.gitignore](deploy/dev/.gitignore)
- [deploy/dev/backend.Dockerfile](deploy/dev/backend.Dockerfile)
- [deploy/dev/dev.sh](deploy/dev/dev.sh)
- [deploy/dev/docker-compose.yml](deploy/dev/docker-compose.yml)
- [deploy/dev/gitea/init-gitea.sh](deploy/dev/gitea/init-gitea.sh)
- [deploy/dev/init-seed.sh](deploy/dev/init-seed.sh)
- [deploy/dev/nginx/conf.d/default.conf](deploy/dev/nginx/conf.d/default.conf)
- [deploy/dev/nginx/nginx.conf](deploy/dev/nginx/nginx.conf)
- [deploy/dev/runner-entrypoint.sh](deploy/dev/runner-entrypoint.sh)
- [deploy/dev/runner-ssh/id_ed25519.pub](deploy/dev/runner-ssh/id_ed25519.pub)
- [deploy/dev/runner.Dockerfile](deploy/dev/runner.Dockerfile)
- [deploy/dev/seed/seed.sql](deploy/dev/seed/seed.sql)
- [deploy/dev/traefik/dynamic/grpc.yml](deploy/dev/traefik/dynamic/grpc.yml)
- [deploy/dev/web.Dockerfile](deploy/dev/web.Dockerfile)
- [relay/.air.toml](relay/.air.toml)
- [runner/.gitignore](runner/.gitignore)
- [runner/internal/config/config_grpc_test.go](runner/internal/config/config_grpc_test.go)
- [runner/internal/envpath/envpath_test.go](runner/internal/envpath/envpath_test.go)
- [web/src/components/ui/block-editor.tsx](web/src/components/ui/block-editor.tsx)
- [web/src/lib/api/base.ts](web/src/lib/api/base.ts)

</details>



This page documents the individual services defined in `deploy/dev/docker-compose.yml` — the Docker Compose file used by the local development environment. It covers each service's image or Dockerfile, exposed ports, environment variables, volumes, health checks, and inter-service dependencies.

For the overall dev workflow (running `dev.sh`, database migrations, seed data, and local runner setup), see [Development Environment](#7). For Gitea initialization and SSH deploy key setup, see [Local Runner and Gitea Setup](#7.2).

---

## Service Map

**Docker Compose service dependency and routing diagram:**

```mermaid
graph TD
    subgraph "External Access"
        Browser["Browser / Runner Client"]
    end

    subgraph "Entry Points (Traefik)"
        T_web["traefik :80 (HTTP)"]
        T_grpc["traefik :9443 (gRPC mTLS)"]
        T_dash["traefik :8080 (Dashboard)"]
    end

    subgraph "Application Services"
        backend["backend :8080"]
        relay["relay :8090"]
        runner["runner"]
    end

    subgraph "Infrastructure"
        postgres["postgres :5432"]
        redis["redis :6379"]
        minio["minio :9000/:9001"]
        gitea["gitea :3000/:22"]
    end

    subgraph "Dev Tools"
        adminer["adminer :8080"]
    end

    Browser --> T_web
    Browser --> T_grpc
    T_web -->|"PathPrefix /api"| backend
    T_web -->|"PathPrefix /relay"| relay
    T_grpc -->|"TCP TLS passthrough"| backend
    backend --> postgres
    backend --> redis
    backend --> minio
    runner -->|"gRPC mTLS via traefik"| T_grpc
    runner -->|"REST health check"| backend
    relay -->|"HTTP registration"| backend
    adminer --> postgres
    runner -->|"SSH git clone"| gitea
```

Sources: [deploy/dev/docker-compose.yml:1-420](), [deploy/dev/traefik/dynamic/grpc.yml:1-20]()

---

## Services

### postgres

| Property | Value |
|----------|-------|
| Image | `postgres:16-alpine` |
| Host Port | `${POSTGRES_PORT:-5432}` → container `5432` |
| Database | `agentsmesh` |
| User | `agentsmesh` |
| Password | `${POSTGRES_PASSWORD:-agentsmesh_dev}` |
| Volume | `postgres_data:/var/lib/postgresql/data` |

The primary relational database. All backend domain models (users, organizations, runners, pods, tickets, channels) are persisted here.

**Health check:** `pg_isready -U agentsmesh` — interval 10s, retries 5. Both `backend` and `runner` declare `condition: service_healthy` dependencies that block on this check.

Sources: [deploy/dev/docker-compose.yml:18-33]()

---

### redis

| Property | Value |
|----------|-------|
| Image | `redis:7-alpine` |
| Host Port | `${REDIS_PORT:-6379}` → container `6379` |
| Persistence | AOF via `--appendonly yes` |
| Volume | `redis_data:/data` |

Used by the backend for caching, session storage, and the event bus (pub/sub). The backend connects using `REDIS_URL=redis://redis:6379`.

**Health check:** `redis-cli ping` — interval 10s, retries 5.

Sources: [deploy/dev/docker-compose.yml:36-48]()

---

### minio

| Property | Value |
|----------|-------|
| Image | `minio/minio:latest` |
| API Host Port | `${MINIO_API_PORT:-9000}` → container `9000` |
| Console Host Port | `${MINIO_CONSOLE_PORT:-9001}` → container `9001` |
| Credentials | `${MINIO_ROOT_USER:-minioadmin}` / `${MINIO_ROOT_PASSWORD:-minioadmin}` |
| Volume | `minio_data:/data` |

S3-compatible object storage. The backend is configured with:

```
STORAGE_ENDPOINT=minio:9000          # internal Docker hostname
STORAGE_PUBLIC_ENDPOINT=localhost:${MINIO_API_PORT}  # for presigned URL generation
STORAGE_BUCKET=agentsmesh
STORAGE_USE_PATH_STYLE=true
```

**Health check:** `mc ready local` — interval 10s, retries 5.

Sources: [deploy/dev/docker-compose.yml:51-68](), [deploy/dev/docker-compose.yml:169-179]()

---

### gitea

| Property | Value |
|----------|-------|
| Image | `gitea/gitea:1.22` |
| HTTP Host Port | `${GITEA_HTTP_PORT:-3001}` → container `3000` |
| SSH Host Port | `${GITEA_SSH_PORT:-2222}` → container `22` |
| Database | SQLite (embedded) |
| Volume | `gitea_data:/data` |

A lightweight self-hosted Git server used by the local development environment so the runner can clone and push to repositories without requiring external access.

Key configuration:
- `GITEA__security__INSTALL_LOCK=true` — skips first-run wizard.
- `GITEA__server__ROOT_URL=http://gitea:3000/` — internal Docker DNS name.
- `GITEA__service__DISABLE_REGISTRATION=true` — users are created by the init script only.

After Gitea starts, `dev.sh` calls `deploy/dev/gitea/init-gitea.sh` to create the `gitea-admin` user, the `dev-org` organization, the `demo-webapp` and `demo-api` repos, and registers the runner's SSH deploy key.

**Health check:** `curl -f http://localhost:3000/api/v1/version` — interval 10s, start_period 30s, retries 10.

Sources: [deploy/dev/docker-compose.yml:69-98](), [deploy/dev/gitea/init-gitea.sh:1-245]()

---

### adminer

| Property | Value |
|----------|-------|
| Image | `adminer:latest` |
| Host Port | `${ADMINER_PORT:-8081}` → container `8080` |
| Depends On | `postgres` |

A database management web UI. Access at `http://localhost:${ADMINER_PORT}`. No health check is defined. It does not expose any application-critical path.

Sources: [deploy/dev/docker-compose.yml:100-107]()

---

### backend

The Go API server, rebuilt on source changes using [Air](https://github.com/air-verse/air).

| Property | Value |
|----------|-------|
| Dockerfile | `deploy/dev/backend.Dockerfile` |
| Internal port | `8080` (not exposed directly; routed via Traefik) |
| gRPC port | `9090` (internal only; routed via Traefik TLS passthrough) |
| Depends On | `postgres` (healthy), `redis` (healthy) |

**Build context:** `deploy/dev/backend.Dockerfile` installs `air` and `golang-migrate`, then downloads Go modules. Source code at `../../backend` is bind-mounted for hot reload.

**Key environment variables:**

| Variable | Value in Dev |
|----------|-------------|
| `PRIMARY_DOMAIN` | `localhost:${HTTP_PORT}` |
| `USE_HTTPS` | `false` |
| `DB_HOST` | `postgres` |
| `REDIS_URL` | `redis://redis:6379` |
| `STORAGE_ENDPOINT` | `minio:9000` |
| `PKI_CA_CERT_FILE` | `/app/ssl/ca.crt` |
| `PKI_CA_KEY_FILE` | `/app/ssl/ca.key` |
| `GRPC_ADDRESS` | `:9090` |
| `GRPC_PUBLIC_ENDPOINT` | `grpcs://127.0.0.1:${GRPC_PORT}` |
| `SERVER_ADDRESS` | `:8080` |
| `EMAIL_PROVIDER` | `console` (prints to stdout) |

**Volumes:**

| Host Path | Container Path | Purpose |
|-----------|----------------|---------|
| `../../backend` | `/app` | Source code (hot reload) |
| `../../proto` | `/proto` | Shared proto module |
| `go-mod-cache` | `/go/pkg/mod` | Go module cache |
| `go-build-cache` | `/root/.cache/go-build` | Go build cache |
| `../../backend/logs` | `/app/logs` | Log files |
| `./ssl` | `/app/ssl:ro` | CA cert/key for PKI |

**Traefik routing labels:**

```
PathPrefix(`/api`) || PathPrefix(`/health`) → backend:8080
```

Router name is prefixed with `${COMPOSE_PROJECT_NAME}` to prevent conflicts between simultaneously running worktrees.

**Health check:** `wget --spider http://localhost:8080/health` — interval 30s, start_period 30s.

Sources: [deploy/dev/docker-compose.yml:109-244](), [deploy/dev/backend.Dockerfile:1-30]()

---

### runner

The Runner daemon, run as UID/GID `1000:1000` (non-root) for compatibility with AI CLI tools such as Claude Code.

| Property | Value |
|----------|-------|
| Dockerfile | `deploy/dev/runner.Dockerfile` |
| User | `1000:1000` (user `runner`) |
| Depends On | `backend` (healthy) |

**Build:** `deploy/dev/runner.Dockerfile` installs `air`, AI CLI tools (`claude`, `codex`, `gemini`, `opencode`), creates the `runner` user, and pre-downloads Go modules. Source at `../../runner` is bind-mounted.

**Startup:** The `entrypoint` field points to `deploy/dev/runner-entrypoint.sh` (mounted read-only). This script:
1. Polls `${BACKEND_URL}/health` until the backend is ready.
2. Generates a client TLS certificate signed by the CA in `/app/ssl/` (ECDSA P-256, CN=`dev-runner`, O=`dev-org`).
3. Initializes AI CLI config files (Claude, Codex, Gemini).
4. Writes `~/.agentsmesh/config.yaml` with gRPC endpoint and cert paths.
5. Launches `air` for hot-reload of the runner binary.

**Key environment variables:**

| Variable | Value |
|----------|-------|
| `BACKEND_URL` | `http://backend:8080` |
| `GRPC_ENDPOINT` | `traefik:9443` |
| `RUNNER_NODE_ID` | `dev-runner` |
| `RUNNER_ORG_SLUG` | `dev-org` |
| `MAX_CONCURRENT_PODS` | `10` |
| `WORKSPACE` | `/workspace` |

**Volumes:**

| Mount | Container Path | Purpose |
|-------|----------------|---------|
| `../../runner` | `/app` | Source code (hot reload) |
| `./ssl` | `/app/ssl:ro` | CA cert for signing runner cert |
| `runner_workspace` | `/workspace` | Pod sandbox workspaces |
| `runner_config` | `/home/runner/.agentsmesh` | Persisted runner config & certs |
| `runner_claude_config` | `/home/runner/.claude` | Claude Code config |
| `runner_codex_config` | `/home/runner/.codex` | OpenAI Codex config |
| `runner_gemini_config` | `/home/runner/.gemini` | Gemini CLI config |
| `./runner-ssh` | `/home/runner/.ssh:ro` | SSH deploy key for Git |
| `runner-go-mod-cache` | `/go/pkg/mod` | Go module cache |
| `runner-go-build-cache` | `/home/runner/.cache/go-build` | Go build cache |

Sources: [deploy/dev/docker-compose.yml:249-320](), [deploy/dev/runner.Dockerfile:1-127](), [deploy/dev/runner-entrypoint.sh:1-344]()

---

### relay

The WebSocket relay service that forwards terminal data between browsers and runners.

| Property | Value |
|----------|-------|
| Dockerfile | `deploy/dev/relay.Dockerfile` |
| Internal port | `8090` (not exposed directly; routed via Traefik) |
| Depends On | `backend` (healthy) |

**Key environment variables:**

| Variable | Value |
|----------|-------|
| `SERVER_ADDRESS` | `:8090` |
| `JWT_SECRET` | `${JWT_SECRET}` (must match backend) |
| `BACKEND_URL` | `http://backend:8080` |
| `INTERNAL_API_SECRET` | `${INTERNAL_API_SECRET}` |
| `RELAY_ID` | `dev-relay-1` |
| `RELAY_INTERNAL_URL` | `ws://relay:8090` |
| `PRIMARY_DOMAIN` | `${PRIMARY_DOMAIN}` |

`RELAY_INTERNAL_URL` is the Docker-internal address that runners use to connect directly. The public WebSocket URL (`ws(s)://{PRIMARY_DOMAIN}/relay`) is derived from `PRIMARY_DOMAIN` and is the address used by browsers.

**Traefik routing labels:**

```
PathPrefix(`/relay`) → strip /relay prefix → relay:8090
```

A `stripprefix` middleware removes the `/relay` path prefix before forwarding to the relay container.

**Volumes:** Source code, proto module, and Go caches — same pattern as backend and runner.

**Health check:** `wget --spider http://localhost:8090/health` — interval 30s, start_period 10s.

Sources: [deploy/dev/docker-compose.yml:321-383]()

---

### traefik

The unified HTTP/gRPC entry point for the development environment.

| Property | Value |
|----------|-------|
| Image | `traefik:v3.2` |
| HTTP Host Port | `${HTTP_PORT:-80}` → container `80` |
| gRPC Host Port | `${GRPC_PORT:-9443}` → container `9443` |
| Dashboard Host Port | `${TRAEFIK_DASHBOARD_PORT:-8080}` → container `8080` |
| Depends On | `backend` |

**Configuration files** (bind-mounted read-only):
- `./traefik/traefik.yml` — static config (generated by `dev.sh`'s `generate_traefik_config`). Defines entry points `web` (`:80`) and `grpc` (`:9443`), enables the Docker provider with constraints scoped to `COMPOSE_PROJECT_NAME`.
- `./traefik/dynamic/grpc.yml` — dynamic config for gRPC TLS passthrough.

**gRPC TLS passthrough:** The `grpc` entry point uses a TCP router with `HostSNI("*")` and `tls.passthrough: true`. This forwards the raw TLS stream to `backend:9090` without Traefik terminating TLS. The backend performs mTLS verification itself.

**Routing diagram:**

```mermaid
flowchart LR
    subgraph "Host Ports"
        P80["${HTTP_PORT}:80"]
        P9443["${GRPC_PORT}:9443"]
        P8080["${TRAEFIK_DASHBOARD_PORT}:8080"]
    end

    subgraph "Traefik Entrypoints"
        EP_web["entrypoint: web (:80)"]
        EP_grpc["entrypoint: grpc (:9443)"]
        EP_dash["entrypoint: api (:8080)"]
    end

    subgraph "HTTP Routers (dynamic labels)"
        R_api["router: ${COMPOSE_PROJECT_NAME}-api\nPathPrefix /api || /health"]
        R_relay["router: ${COMPOSE_PROJECT_NAME}-relay\nPathPrefix /relay"]
    end

    subgraph "TCP Router (grpc.yml)"
        R_grpc["router: grpc-mtls\nHostSNI(*) TLS passthrough"]
    end

    subgraph "Backends"
        SVC_backend["backend:8080"]
        SVC_relay["relay:8090"]
        SVC_grpc["backend:9090"]
    end

    P80 --> EP_web
    P9443 --> EP_grpc
    P8080 --> EP_dash
    EP_web --> R_api --> SVC_backend
    EP_web --> R_relay -->|"strip /relay"| SVC_relay
    EP_grpc --> R_grpc --> SVC_grpc
```

Sources: [deploy/dev/docker-compose.yml:384-400](), [deploy/dev/traefik/dynamic/grpc.yml:1-20](), [deploy/dev/dev.sh:136-168]()

---

## Volumes

All named volumes are declared at the bottom of `docker-compose.yml`.

| Volume | Used By | Purpose |
|--------|---------|---------|
| `postgres_data` | `postgres` | PostgreSQL data files |
| `redis_data` | `redis` | Redis AOF persistence |
| `minio_data` | `minio` | Object storage data |
| `gitea_data` | `gitea` | Gitea repos, config, SQLite DB |
| `go-mod-cache` | `backend` | Go module cache |
| `go-build-cache` | `backend` | Go build artifact cache |
| `runner-go-mod-cache` | `runner` | Runner Go module cache |
| `runner-go-build-cache` | `runner` | Runner build artifact cache |
| `runner_workspace` | `runner` | Pod sandbox working directories |
| `runner_config` | `runner` | `~/.agentsmesh` — config + mTLS certs |
| `runner_claude_config` | `runner` | `~/.claude` — Claude Code session |
| `runner_codex_config` | `runner` | `~/.codex` — Codex CLI config |
| `runner_gemini_config` | `runner` | `~/.gemini` — Gemini CLI config |
| `relay-go-mod-cache` | `relay` | Relay Go module cache |
| `relay-go-build-cache` | `relay` | Relay build artifact cache |

Sources: [deploy/dev/docker-compose.yml:402-420]()

---

## Port Allocation

`dev.sh` assigns each worktree a unique `PORT_OFFSET` value (0–500) derived from a hash of the git worktree name. Ports are calculated as:

```
HTTP_PORT  = 10000 + offset * 50
GRPC_PORT  = 10001 + offset * 50
POSTGRES   = 10002 + offset * 50
REDIS      = 10003 + offset * 50
MINIO_API  = 10004 + offset * 50
MINIO_CON  = 10005 + offset * 50
ADMINER    = 10006 + offset * 50
WEB_PORT   = 10007 + offset * 50
TRAEFIK    = 10008 + offset * 50
GITEA_HTTP = 10009 + offset * 50
GITEA_SSH  = 10010 + offset * 50
```

The `main` branch always uses offset 0, giving it the base port values. A secondary worktree gets a deterministic but non-conflicting set of ports, allowing multiple worktrees to run in parallel on the same machine.

The `COMPOSE_PROJECT_NAME` is set to `agentsmesh-${worktree_name}`, which namespaces all containers, volumes, networks, and Traefik router names.

Sources: [deploy/dev/dev.sh:54-69](), [deploy/dev/dev.sh:185-244]()

---

## Hot Reload

Both `backend` and `runner` (and `relay`) use [Air](https://github.com/air-verse/air) for hot reload in development:

- **backend:** `CMD ["air", "-c", ".air.toml"]` — watches `../../backend`, rebuilds `./cmd/server` on `.go` changes.
- **runner:** entrypoint script calls `exec air -c .air.toml` if `air` is on PATH.
- **relay:** Air config at `relay/.air.toml` builds `./cmd/relay` with a `kill_delay = "5s"` to allow the old process to release port `8090` before the new binary starts.

The web frontend (`web` and `web-admin`) intentionally runs **outside Docker** for better Turbopack performance. `dev.sh` starts the local Next.js process directly. See [Development Environment](#7) for details.

Sources: [deploy/dev/backend.Dockerfile:28-30](), [deploy/dev/runner-entrypoint.sh:315-327](), [relay/.air.toml:1-50]()

---

# Page: Local Runner and Gitea Setup

# Local Runner and Gitea Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deploy/dev/dev.sh](deploy/dev/dev.sh)
- [deploy/dev/gitea/init-gitea.sh](deploy/dev/gitea/init-gitea.sh)
- [deploy/dev/runner-ssh/id_ed25519.pub](deploy/dev/runner-ssh/id_ed25519.pub)
- [relay/.air.toml](relay/.air.toml)
- [runner/.gitignore](runner/.gitignore)
- [runner/.goreleaser.yml](runner/.goreleaser.yml)
- [runner/README.md](runner/README.md)
- [runner/internal/config/config.go](runner/internal/config/config.go)
- [runner/internal/config/config_defaults_test.go](runner/internal/config/config_defaults_test.go)
- [runner/internal/config/config_grpc_test.go](runner/internal/config/config_grpc_test.go)
- [runner/internal/envpath/envpath_test.go](runner/internal/envpath/envpath_test.go)
- [web/public/install.ps1](web/public/install.ps1)
- [web/public/install.sh](web/public/install.sh)
- [web/src/app/docs/runners/setup/page.tsx](web/src/app/docs/runners/setup/page.tsx)

</details>



This page covers the developer-side workflows that `dev.sh` orchestrates beyond the Docker Compose services: building the runner binary from source, assigning worktree-isolated port ranges, initializing Gitea with seed repositories and SSH deploy keys, and registering a local runner process against the development backend. For the Docker Compose service definitions themselves, see [7.1](#7.1). For general runner installation and registration in production, see [3.1](#3.1).

---

## Local Runner Binary Build

The `build_runner_local` function in [deploy/dev/dev.sh:735-802]() compiles the runner from local source using a Docker container running `golang:1.25-alpine`. **No local Go toolchain is required.**

### Build Mechanics

- **Source hash detection** — A hash is computed from the git tree SHAs of `runner/` and `proto/` plus any uncommitted diff. If the hash matches `.local-build-hash` and the binary exists, the build is skipped.
- **Docker volume reuse** — The same Go module cache and build cache volumes used by the Docker Compose `runner` service (`runner-go-mod-cache`, `runner-go-build-cache`) are reused, so repeated builds are fast.
- **Output path** — The binary is installed to `~/.local/bin/agentsmesh-runner`. If that directory is absent from `$PATH`, `dev.sh` prints a warning with the required export line.
- **Target platform** — The build targets `GOOS=darwin GOARCH=arm64` (the developer's host). Cross-compilation targets for CI are handled by GoReleaser (see [8.2](#8.2)).

**Diagram: build_runner_local data flow**

```mermaid
flowchart TD
    A["dev.sh\nbuild_runner_local()"] --> B["Compute source_hash\n(git tree SHA + diff)"]
    B --> C{"Hash matches\n.local-build-hash?"}
    C -- "yes + binary exists" --> D["Skip build"]
    C -- "no" --> E["docker run golang:1.25-alpine\ngo build ./cmd/runner"]
    E --> F["runner/bin/agentsmesh-runner"]
    F --> G["~/.local/bin/agentsmesh-runner"]
    G --> H["Write hash to\n.local-build-hash"]
    E -- "uses" --> I["Docker volume\nrunner-go-mod-cache"]
    E -- "uses" --> J["Docker volume\nrunner-go-build-cache"]
```

Sources: [deploy/dev/dev.sh:735-802](), [runner/.gitignore:1-2]()

---

## Port Allocation by Worktree

To allow multiple git worktrees to run simultaneously without port conflicts, `dev.sh` assigns each worktree a deterministic port offset.

### Algorithm

1. **`get_worktree_name()`** ([deploy/dev/dev.sh:42-52]()) — reads `git rev-parse --git-dir`. If the path contains `.git/worktrees/<name>`, it extracts `<name>`; otherwise it uses the current branch name. Non-alphanumeric characters are replaced with `-` and lowercased.

2. **`calculate_port_offset()`** ([deploy/dev/dev.sh:55-69]()) — for `main` or `master`, offset is `0`. For any other name, a 6-character hex MD5 prefix is taken and reduced to the range `1–500` via modulo, giving a step of 50 ports per worktree.

3. **Port formula** — All service ports follow `BASE + (offset × 50)`, where `BASE` is the service's base port:

| Service | Base port | Env var |
|---|---|---|
| Traefik HTTP | 10000 | `HTTP_PORT` |
| Traefik gRPC | 10001 | `GRPC_PORT` |
| PostgreSQL | 10002 | `POSTGRES_PORT` |
| Redis | 10003 | `REDIS_PORT` |
| MinIO API | 10004 | `MINIO_API_PORT` |
| MinIO Console | 10005 | `MINIO_CONSOLE_PORT` |
| Adminer | 10006 | `ADMINER_PORT` |
| Web (Next.js) | 10007 | `WEB_PORT` |
| Traefik Dashboard | 10008 | `TRAEFIK_DASHBOARD_PORT` |
| Gitea HTTP | 10009 | `GITEA_HTTP_PORT` |
| Gitea SSH | 10010 | `GITEA_SSH_PORT` |

For example, a worktree named `feature-auth` with MD5 prefix `a3f1b2` gets `offset = (0xa3f1b2 % 500) + 1 = 179`, so its HTTP port is `10000 + 179 × 50 = 18950`.

The computed values are written to `deploy/dev/.env` by `generate_env()` ([deploy/dev/dev.sh:171-245]()) and are idempotent — if `.env` already exists for the current project name, ports are preserved to keep runner configs stable.

Sources: [deploy/dev/dev.sh:42-69](), [deploy/dev/dev.sh:171-245]()

---

## Gitea Initialization

Gitea is a self-hosted Git service running as a Docker container. The `init_gitea()` function in [deploy/dev/dev.sh:413-435]() waits for Gitea's HTTP API to become reachable, then delegates to [deploy/dev/gitea/init-gitea.sh]().

### Initialization Steps

**Diagram: init-gitea.sh execution sequence**

```mermaid
sequenceDiagram
    participant devsh as "dev.sh\ninit_gitea()"
    participant script as "init-gitea.sh"
    participant giteaAPI as "Gitea API\nlocalhost:GITEA_HTTP_PORT"
    participant docker as "docker exec\ngitea container"

    devsh->>script: "call with container name + port"
    script->>giteaAPI: "GET /api/v1/version (health poll)"
    giteaAPI-->>script: "200 OK"
    script->>docker: "gitea admin user create\n(ADMIN_USER=gitea-admin)"
    script->>giteaAPI: "POST /api/v1/orgs\n{username: dev-org}"
    script->>giteaAPI: "POST /api/v1/orgs/dev-org/repos\n{name: demo-webapp}"
    script->>script: "git init + push seed code\nvia HTTP basic auth"
    script->>giteaAPI: "POST /api/v1/orgs/dev-org/repos\n{name: demo-api}"
    script->>script: "git init + push seed code"
    script->>giteaAPI: "POST /repos/dev-org/demo-webapp/keys\n{title: runner-deploy-key}"
    script->>giteaAPI: "POST /repos/dev-org/demo-api/keys\n{title: runner-deploy-key}"
```

Sources: [deploy/dev/dev.sh:413-435](), [deploy/dev/gitea/init-gitea.sh:1-243]()

### Admin Credentials

| Resource | Value |
|---|---|
| Admin user | `gitea-admin` |
| Admin password | `gitea-admin-123` |
| Organization | `dev-org` |
| Seed repos | `dev-org/demo-webapp`, `dev-org/demo-api` |

### Deploy Key Registration

The `add_deploy_key()` function ([deploy/dev/gitea/init-gitea.sh:146-211]()) handles key rotation: it compares the fingerprint of the currently registered key (title `runner-deploy-key`) against the local public key (`deploy/dev/runner-ssh/id_ed25519.pub`). If they differ, the stale key is deleted before the new one is registered. This ensures that re-generated SSH keys (e.g., on a new machine) are automatically propagated without manual cleanup.

Sources: [deploy/dev/gitea/init-gitea.sh:146-211]()

---

## Runner SSH Key and Host Configuration

### Generating the SSH Keypair

`generate_runner_ssh_key()` ([deploy/dev/dev.sh:440-454]()) creates an ed25519 keypair at `deploy/dev/runner-ssh/id_ed25519` if it does not exist. The private key is excluded from version control via `.gitignore`; only `id_ed25519.pub` is committed ([deploy/dev/runner-ssh/id_ed25519.pub:1-1]()). The key comment is `agentsmesh-dev-runner@local`.

### SSH Config for Host-Side Runners

Inside Docker, the hostname `gitea` resolves via Docker's internal DNS. A local runner process running on the host has no such resolution. `setup_gitea_ssh_config()` ([deploy/dev/dev.sh:462-497]()) writes a managed block to `~/.ssh/config` that maps the `gitea` hostname to `127.0.0.1` on the worktree-specific `GITEA_SSH_PORT`:

```
# BEGIN AgentsMesh dev gitea
Host gitea
    HostName 127.0.0.1
    Port <GITEA_SSH_PORT>
    IdentityFile <repo>/deploy/dev/runner-ssh/id_ed25519
    IdentitiesOnly yes
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
# END AgentsMesh dev gitea
```

The function is idempotent: it removes any existing `BEGIN AgentsMesh dev gitea … END` block before writing, so it can be re-run safely after a port change.

With this in place, any `git@gitea:dev-org/demo-webapp.git` clone URL issued from the host resolves correctly.

**Diagram: SSH resolution paths for Docker vs. host runners**

```mermaid
flowchart LR
    subgraph "Docker Network"
        DockerRunner["runner container\ngit@gitea:..."] -->|"Docker DNS" | GiteaContainer["gitea container\nGITEA_SSH_PORT"]
    end
    subgraph "Host"
        LocalRunner["agentsmesh-runner\ngit@gitea:..."] -->|"~/.ssh/config\nHost gitea → 127.0.0.1:GITEA_SSH_PORT"| GiteaContainer
    end
    GiteaContainer -->|"validates" | DeployKey["runner-deploy-key\nid_ed25519.pub"]
```

Sources: [deploy/dev/dev.sh:440-497](), [deploy/dev/runner-ssh/id_ed25519.pub:1-1]()

---

## Registering and Running a Local Runner

After `dev.sh` completes, a locally built binary is available at `~/.local/bin/agentsmesh-runner`. To register and connect it to the local backend:

```bash
# Obtain a token from the dev UI: Settings → Runners → Create Token
agentsmesh-runner register \
  --server http://localhost:<HTTP_PORT> \
  --token <TOKEN>

# Start the runner (foreground)
agentsmesh-runner run
```

The `register` command writes `~/.agentsmesh/config.yaml` with the `server_url`, `grpc_endpoint` (`grpcs://127.0.0.1:<GRPC_PORT>`), and mTLS certificate paths. `dev.sh` displays the exact `HTTP_PORT` in the startup summary printed by `show_result()` ([deploy/dev/dev.sh:626-655]()).

The runner configuration file structure is defined by `Config` in [runner/internal/config/config.go:12-79](). Key fields relevant to local development:

| Field | Source | Local dev value |
|---|---|---|
| `server_url` | `register` flag | `http://localhost:<HTTP_PORT>` |
| `grpc_endpoint` | assigned during `register` | `grpcs://127.0.0.1:<GRPC_PORT>` |
| `cert_file` / `key_file` / `ca_file` | written by `register` | `~/.agentsmesh/certs/` |
| `workspace_root` | default | `/workspace` |
| `mcp_port` | default | `19000` |

Sources: [deploy/dev/dev.sh:626-655](), [runner/internal/config/config.go:12-79]()

---

## Resetting Runners

The `reset_runners()` function ([deploy/dev/dev.sh:501-594]()) provides a clean-slate recovery when runners are in a bad state:

1. Kills any `agentsmesh-runner` process on the host via `pkill`.
2. Releases ports `19000` (MCP server), `19080` (web console), and `9090` (health check) if occupied.
3. Starts Docker Desktop if not running.
4. Force-recreates the Docker `runner` and `relay` containers.
5. Patches `~/.agentsmesh/config.yaml` if `grpc_endpoint` does not match the current `GRPC_PORT` from `.env`.

Invoke it with:

```bash
./dev.sh --reset-runners
```

Sources: [deploy/dev/dev.sh:501-594]()

---

## Full dev.sh Initialization Sequence

The following diagram maps each step in `main()` to the function it calls, showing where the local runner and Gitea work fits in the overall startup flow.

**Diagram: dev.sh main() step → function mapping**

```mermaid
flowchart TD
    S1["Step 1\ngenerate_ssl_certs()"] --> S2["Step 2\ngenerate_ai_cli_configs()"]
    S2 --> S3["Step 3\ngenerate_env()"]
    S3 --> S4["Step 4\ngenerate_traefik_config()"]
    S4 --> S5["Step 5\ngenerate_web_env()"]
    S5 --> S6["Step 6\ndocker compose up"]
    S6 --> S7["Step 7\nwait PostgreSQL"]
    S7 --> S8["Step 8\nrun_migrations()"]
    S8 --> S9["Step 9\ninit_seed()"]
    S9 --> S95["Step 9.5\ngenerate_runner_ssh_key()\ninit_gitea()"]
    S95 --> S96["Step 9.6\nsetup_gitea_ssh_config()"]
    S96 --> S10["Step 10\nfix workspace permissions"]
    S10 --> S11["Step 11\nstart_frontend()"]
    S11 --> S115["Step 11.5\nbuild_runner_local()"]
    S115 --> S12["show_result()"]

    style S95 fill:#f0f0f0
    style S96 fill:#f0f0f0
    style S115 fill:#f0f0f0
```

> Steps 9.5, 9.6, and 11.5 are the Gitea and local runner steps documented on this page.

Sources: [deploy/dev/dev.sh:804-896]()

---

# Page: Deployment

# Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitlab-ci.yml](.gitlab-ci.yml)
- [backend/internal/infra/storage/s3.go](backend/internal/infra/storage/s3.go)
- [ci/backend.Dockerfile](ci/backend.Dockerfile)
- [ci/build-onpremise.sh](ci/build-onpremise.sh)
- [ci/pack-onpremise.sh](ci/pack-onpremise.sh)
- [ci/relay.Dockerfile](ci/relay.Dockerfile)
- [ci/runner.Dockerfile](ci/runner.Dockerfile)
- [ci/web-admin.Dockerfile](ci/web-admin.Dockerfile)
- [ci/web.Dockerfile](ci/web.Dockerfile)
- [deploy/dev/runner-ssh/README.md](deploy/dev/runner-ssh/README.md)
- [deploy/onpremise/README.md](deploy/onpremise/README.md)
- [deploy/onpremise/docker-compose.yml](deploy/onpremise/docker-compose.yml)
- [deploy/onpremise/scripts/generate-certs.sh](deploy/onpremise/scripts/generate-certs.sh)
- [deploy/onpremise/scripts/install.sh](deploy/onpremise/scripts/install.sh)
- [deploy/onpremise/scripts/load-images.sh](deploy/onpremise/scripts/load-images.sh)
- [deploy/onpremise/seed/onpremise-seed.sql](deploy/onpremise/seed/onpremise-seed.sql)
- [e2e/README.md](e2e/README.md)
- [runner/internal/workspace/repo_auth.go](runner/internal/workspace/repo_auth.go)
- [runner/internal/workspace/workspace.go](runner/internal/workspace/workspace.go)
- [runner/internal/workspace/workspace_utils.go](runner/internal/workspace/workspace_utils.go)
- [web/src/lib/terminalScheduler.ts](web/src/lib/terminalScheduler.ts)
- [web/vitest.config.ts](web/vitest.config.ts)

</details>



This page provides an overview of the three deployment models used by AgentsMesh: the hosted SaaS CI/CD pipeline, the public runner binary release process, and on-premise self-hosted installation. For local development setup, see [Development Environment](#7).

---

## Deployment Models

AgentsMesh is designed to support two distinct operator roles:

| Model | Who runs the infrastructure | Components deployed | Details |
|---|---|---|---|
| **SaaS (hosted)** | AgentsMesh team | Backend, Web, Web-Admin, Relay | [CI/CD Pipeline](#8.1), [Release Process](#8.2) |
| **On-Premise** | Customer team | All services (self-hosted) | [On-Premise Deployment](#8.3) |
| **Runner (BYOK)** | End user (agent host machine) | Runner binary only | [Installation and Registration](#3.1) |

In all deployment models, the Runner binary runs on the **user's own machine**. Only the control plane services (Backend, Web, Relay) vary between SaaS and on-premise.

---

## Service Components and Build Artifacts

Each service in the system has a corresponding Dockerfile and produced artifact.

**Service-to-Dockerfile mapping:**

| Service | Dockerfile | Image name | Port |
|---|---|---|---|
| Backend (Go) | `ci/backend.Dockerfile` | `agentsmesh/backend` | 8080 (HTTP), 9090 (gRPC) |
| Web Frontend (Next.js) | `ci/web.Dockerfile` | `agentsmesh/web` | 3000 |
| Web Admin (Next.js) | `ci/web-admin.Dockerfile` | `agentsmesh/web-admin` | 3001 |
| Relay (Go) | `ci/relay.Dockerfile` | `agentsmesh/relay` | 8090 |
| Runner (Go) | `ci/runner.Dockerfile` | `agentsmesh/runner` | — |

The runner binary is also distributed as a standalone binary via GitHub Releases and Homebrew; the Docker image is used for containerized or dev environments only.

Sources: [ci/backend.Dockerfile:1-67](), [ci/web.Dockerfile:1-94](), [ci/web-admin.Dockerfile:1-86](), [ci/runner.Dockerfile:1-72](), [ci/relay.Dockerfile:1-45]()

---

## Build Pipeline Overview

**Diagram: Pipeline stages and service images**

```mermaid
flowchart TD
    MR["Merge Request"] --> T["test stage"]
    MAIN["main branch push"] --> B["build stage"]
    TAG["git tag push"] --> RL["release stage"]

    T --> TB["test-backend"]
    T --> TW["test-web"]
    T --> TWA["test-web-admin"]
    T --> TR["test-runner"]
    T --> TRL["test-relay"]

    T --> VBB["verify-build-backend"]
    T --> VBW["verify-build-web"]
    T --> VBWA["verify-build-web-admin"]
    T --> VBR["verify-build-runner"]
    T --> VBRL["verify-build-relay"]

    B --> BBK["build-backend\nagentsmesh/backend:SHA"]
    B --> BW["build-web\nagentsmesh/web:SHA"]
    B --> BWA["build-web-admin\nagentsmesh/web-admin:SHA"]
    B --> BRN["build-runner\nagentsmesh/runner:SHA"]
    B --> BRL["build-relay\nagentsmesh/relay:SHA"]

    BBK --> DCN["deploy:cn-prod:backend"]
    BW --> DCW["deploy:cn-prod:web"]
    BWA --> DCWA["deploy:cn-prod:web-admin"]
    BRL --> DCRL["deploy:cn-prod:cn-relay-01"]
    DCN --> MCN["migrate:cn-prod"]

    BBK --> DUS["deploy:uswest-prod:backend"]
    BW --> DUW["deploy:uswest-prod:web"]
    BWA --> DUWA["deploy:uswest-prod:web-admin"]
    BRL --> DURL["deploy:uswest-prod:uswest-relay-01"]
    DUS --> MUS["migrate:uswest-prod"]

    RL --> GR["GoReleaser\nRunner binary"]
    RL --> HB["Homebrew tap update"]
```

Sources: [.gitlab-ci.yml:1-701]()

---

## SaaS Production Environments

The hosted SaaS deployment runs on two independent environments:

| Environment | GitLab env name | Primary URL | Notes |
|---|---|---|---|
| China | `cn-production` | `https://agentsmesh.cn` | Deploys to `aliyun-s001` |
| US West | `uswest-production` | `https://agentsmesh.ai` | Deploys to `aliyun-us-west-001` |

Each environment also has one or more relay nodes deployed separately:

| Relay node | Environment | URL |
|---|---|---|
| `cn-relay-01` | cn-production | `01.relay.agentsmesh.cn:8443` |
| `uswest-relay-01` | uswest-production | `01.relay.agentsmesh.ai:8443` |
| `uswest-relay-beijing-02` | uswest-production | `beijing-02.relay.agentsmesh.ai:8443` |

Deployments are triggered automatically on every push to `main` when relevant files change. Each deploy job SSH-executes a `deploy.sh` script on the target host. Database migrations run automatically after backend deployment when files under `backend/migrations/` change.

For complete pipeline details, see [CI/CD Pipeline](#8.1).

Sources: [.gitlab-ci.yml:415-701]()

---

## Runner Binary Distribution

The runner binary is released as a standalone executable targeting multiple OS/architecture combinations. It is distributed through:

- **GitHub Releases** — via GoReleaser, triggered on git tags
- **Homebrew tap** — automatically updated as part of the release pipeline
- **Windows installer** — bundled in the release artifacts
- **Install script** — `curl -fsSL https://agentsmesh.ai/install.sh | sh`

The runner does not require the hosted backend to be accessible during install; it only connects outbound during `register` and `run`. For details on the release pipeline configuration, see [Release Process](#8.2).

---

## On-Premise Deployment

On-premise deployment uses a Docker Compose stack that mirrors the production services, replacing external dependencies with locally managed containers.

**Diagram: On-premise docker-compose service topology**

```mermaid
flowchart TD
    Browser["Browser"] --> Traefik["traefik\nport 80 HTTP"]
    Runner["agentsmesh-runner\n(user machine)"] --> Traefik
    Runner --> TraefikGRPC["traefik\nport 9443 gRPC+mTLS"]

    Traefik --> Web["web\nport 3000"]
    Traefik --> Backend["backend\nport 8080"]
    Traefik --> Relay["relay\nport 8090"]
    TraefikGRPC --> Backend

    WebAdmin["web-admin\nport 3001"] --> Browser

    Backend --> Postgres["postgres\nport 5432"]
    Backend --> Redis["redis\nport 6379"]
    Backend --> MinIO["minio\nport 9000"]

    subgraph "SSL volume"
        SSL["ssl/ca.crt\nssl/ca.key\nssl/server.crt\nssl/server.key"]
    end

    Backend --> SSL
    TraefikGRPC --> SSL
```

Sources: [deploy/onpremise/docker-compose.yml:1-289]()

**On-premise installation steps:**

| Step | Tool | Description |
|---|---|---|
| 1 | `install.sh --ip <SERVER_IP>` | Main entry point; runs all steps below |
| 2 | `load-images.sh` | Loads pre-exported `.tar` images into Docker |
| 3 | `generate-certs.sh` | Generates CA + server TLS certs (ECDSA P-256) |
| 4 | `docker compose up -d` | Starts all services |
| 5 | `migrate` (in backend container) | Applies database schema migrations |
| 6 | `onpremise-seed.sql` | Creates admin user, default org, and runner token |

Sources: [deploy/onpremise/scripts/install.sh:1-324](), [deploy/onpremise/scripts/generate-certs.sh:1-96](), [deploy/onpremise/seed/onpremise-seed.sql:1-127]()

**Key configuration variables** set in the generated `.env`:

| Variable | Description |
|---|---|
| `SERVER_IP` | IP address for all service URLs |
| `DB_PASSWORD` | PostgreSQL password (randomly generated) |
| `JWT_SECRET` | Shared JWT signing secret |
| `INTERNAL_API_SECRET` | Backend-to-relay authentication |
| `MINIO_ROOT_PASSWORD` | MinIO admin password |
| `GRPC_PORT` | Port for runner gRPC connections (default: `9443`) |

The web and web-admin containers use a `docker-entrypoint.sh` pattern where `PRIMARY_DOMAIN` and `USE_HTTPS` are injected at container start time by replacing placeholder strings embedded during the Next.js build (`__PRIMARY_DOMAIN__`, `__USE_HTTPS__`).

For the complete on-premise setup guide, see [On-Premise Deployment](#8.3).

Sources: [ci/web.Dockerfile:35-36](), [ci/web-admin.Dockerfile:32-33](), [deploy/onpremise/docker-compose.yml:88-160]()

---

## Air-Gapped Packaging

For environments without internet access, the `ci/build-onpremise.sh` and `ci/pack-onpremise.sh` scripts produce a self-contained tarball:

```
agentsmesh-onpremise-{VERSION}.tar.gz
├── docker-compose.yml
├── .env.template
├── traefik/
├── ssl/           (generated by install.sh)
├── seed/
│   └── onpremise-seed.sql
├── images/
│   ├── backend.tar
│   ├── web.tar
│   ├── web-admin.tar
│   ├── relay.tar
│   ├── postgres.tar
│   ├── redis.tar
│   ├── minio.tar
│   └── traefik.tar
└── scripts/
    ├── install.sh
    ├── load-images.sh
    └── generate-certs.sh
```

The `load-images.sh` script loads each `.tar` into the local Docker daemon using `docker load`, making the installation fully offline after the tarball is transferred.

Sources: [ci/build-onpremise.sh:1-138](), [ci/pack-onpremise.sh:1-94](), [deploy/onpremise/scripts/load-images.sh:1-72](), [deploy/onpremise/README.md:83-114]()

---

# Page: CI/CD Pipeline

# CI/CD Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitlab-ci.yml](.gitlab-ci.yml)
- [ci/backend.Dockerfile](ci/backend.Dockerfile)
- [ci/relay.Dockerfile](ci/relay.Dockerfile)
- [ci/runner.Dockerfile](ci/runner.Dockerfile)
- [ci/web-admin.Dockerfile](ci/web-admin.Dockerfile)
- [ci/web.Dockerfile](ci/web.Dockerfile)
- [runner/internal/workspace/repo_auth.go](runner/internal/workspace/repo_auth.go)
- [runner/internal/workspace/workspace.go](runner/internal/workspace/workspace.go)
- [runner/internal/workspace/workspace_utils.go](runner/internal/workspace/workspace_utils.go)
- [web/src/lib/terminalScheduler.ts](web/src/lib/terminalScheduler.ts)
- [web/vitest.config.ts](web/vitest.config.ts)

</details>



This page documents the GitLab CI/CD pipeline that builds, tests, and deploys the SaaS-hosted AgentsMesh services. It covers pipeline stages, job trigger rules, Dockerfile structure for each service, and multi-region deployment topology. For the runner binary release process (GitHub Actions, GoReleaser, code signing), see [8.2](#8.2). For on-premise deployment, see [8.3](#8.3).

---

## Overview

The pipeline is defined in [.gitlab-ci.yml:1-702]() and consists of five ordered stages:

| Stage | Purpose |
|---|---|
| `test` | Run unit tests and verify Docker builds on merge requests |
| `build` | Build and push Docker images on `main` branch commits |
| `package` | *(Reserved for future use / runner release packaging)* |
| `release` | *(Triggered by tags via included runner pipeline)* |
| `deploy` | Deploy images to production environments via SSH |

A secondary pipeline for the runner binary is included conditionally:

```yaml
include:
  - local: 'runner/.gitlab-ci.yml'
    rules:
      - if: $CI_COMMIT_TAG
```

[.gitlab-ci.yml:1-5]()

This means `runner/.gitlab-ci.yml` only activates on tagged commits. The main pipeline handles service deployments on every push to `main`.

---

## Global Variables

[.gitlab-ci.yml:7-22]()

| Variable | Value | Purpose |
|---|---|---|
| `REGISTRY` | `registry.corp.agentsmesh.ai` | Internal container registry |
| `BACKEND_IMAGE` | `${REGISTRY}/agentsmesh/backend` | Backend image name |
| `WEB_IMAGE` | `${REGISTRY}/agentsmesh/web` | Web frontend image name |
| `WEB_ADMIN_IMAGE` | `${REGISTRY}/agentsmesh/web-admin` | Admin panel image name |
| `RUNNER_IMAGE` | `${REGISTRY}/agentsmesh/runner` | Runner daemon image name |
| `RELAY_IMAGE` | `${REGISTRY}/agentsmesh/relay` | Relay service image name |
| `VERSION` | `${CI_COMMIT_TAG:-dev}` | Defaults to `dev` unless on a tag |
| `GO_VERSION` | `1.25` | Go toolchain version used in all Go builds |
| `GOPROXY` | `https://goproxy.cn,...,direct` | China-region Go module proxy |
| `NPM_REGISTRY` | `https://repo.huaweicloud.com/...` | China-region npm mirror |
| `REGISTRY_PREFIX` | `${REGISTRY}/library/` | Internal Docker Hub mirror prefix |

`REGISTRY_PREFIX` is passed as a `--build-arg` to every `docker build` call, allowing Dockerfiles to pull base images (e.g., `golang`, `node`, `alpine`) from the internal mirror rather than Docker Hub, avoiding rate-limit timeouts in CI.

Sources: [.gitlab-ci.yml:7-22]()

---

## Pipeline Trigger Rules

Jobs in this pipeline use GitLab's `rules` keyword for precise activation. There are two primary patterns:

**Pattern A — MR-only** (runs on merge request events, changes to specific paths):
```yaml
rules:
  - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    changes:
      - backend/**/*
  - if: $CI_PIPELINE_SOURCE == "web"
```

**Pattern B — Main branch** (runs on pushes to `main`, same path filtering):
```yaml
rules:
  - if: $CI_COMMIT_BRANCH == "main"
    changes:
      - backend/**/*
      - proto/**/*
      - ci/backend.Dockerfile
  - if: $CI_PIPELINE_SOURCE == "web"
```

The `$CI_PIPELINE_SOURCE == "web"` condition allows manually triggering any job from the GitLab UI regardless of changed files.

Sources: [.gitlab-ci.yml:74-79](), [.gitlab-ci.yml:319-325]()

---

## Test Stage

The test stage runs two categories of jobs: **unit tests** and **build verification**.

### Unit Test Jobs

**Pipeline overview — Test stage:**

```mermaid
graph LR
  MR["Merge Request"]

  MR --> TB["test-backend"]
  MR --> TW["test-web"]
  MR --> TWA["test-web-admin"]
  MR --> TR["test-runner"]
  MR --> TRL["test-relay"]

  TB --> |"JUnit + Cobertura"| A1["backend/report.xml\nbackend/coverage.xml"]
  TW --> |"JUnit + Cobertura"| A2["web/report.xml\nweb/coverage/cobertura-coverage.xml"]
  TR --> |"JUnit + Cobertura"| A3["runner/report.xml\nrunner/coverage.xml"]
  TRL --> |"JUnit + Cobertura"| A4["relay/report.xml\nrelay/coverage.xml"]
```

| Job | Image | Working Dir | Test Command |
|---|---|---|---|
| `test-backend` | `golang:${GO_VERSION}` | `backend/` | `gotestsum --junitfile report.xml -- -race -coverprofile=coverage.out ./...` |
| `test-web` | `node:20-alpine` | `web/` | `pnpm lint && pnpm test:run --coverage` |
| `test-web-admin` | `node:20-alpine` | `web-admin/` | `pnpm lint && pnpm build` |
| `test-runner` | `golang:${GO_VERSION}` | `runner/` | `gotestsum --junitfile report.xml -- -race -coverprofile=coverage.out ./...` |
| `test-relay` | `golang:${GO_VERSION}` | `relay/` | `gotestsum --junitfile report.xml -- -race -coverprofile=coverage.out ./...` |

- `test-backend` spins up `postgres:16-alpine` and `redis:7-alpine` as CI services, with `DATABASE_URL` and `REDIS_URL` injected as environment variables.
- Go tests run with the `-race` flag and atomic coverage mode.
- Coverage results are exported in Cobertura format for GitLab's coverage visualization.
- Web tests use Vitest configured in [web/vitest.config.ts:1-34](), with `jsdom` environment, `v8` coverage provider, and JUnit reporter.

Sources: [.gitlab-ci.yml:34-198](), [web/vitest.config.ts:1-34]()

### Build Verification Jobs

These jobs run only on merge requests and perform a full Docker build without pushing to the registry. They catch Dockerfile or source compilation errors before code is merged.

| Job | Dockerfile | Changed Paths Watched |
|---|---|---|
| `verify-build-backend` | `ci/backend.Dockerfile` | `backend/**/*`, `proto/**/*`, `ci/backend.Dockerfile` |
| `verify-build-web` | `ci/web.Dockerfile` | `web/**/*`, `ci/web.Dockerfile` |
| `verify-build-web-admin` | `ci/web-admin.Dockerfile` | `web-admin/**/*`, `ci/web-admin.Dockerfile` |
| `verify-build-runner` | `ci/runner.Dockerfile` | `runner/**/*`, `proto/**/*`, `ci/runner.Dockerfile` |
| `verify-build-relay` | `ci/relay.Dockerfile` | `relay/**/*`, `ci/relay.Dockerfile` |

Sources: [.gitlab-ci.yml:200-298]()

---

## Build Stage

Build jobs run only on pushes to the `main` branch. Each job produces two tags:

- `${IMAGE}:${CI_COMMIT_SHORT_SHA}` — immutable, pinned to a specific commit
- `${IMAGE}:latest` — floating tag, always points to the most recent main build

Both tags are pushed to the internal registry at `registry.corp.agentsmesh.ai`.

**Diagram — Build stage image outputs:**

```mermaid
graph LR
  main["main branch push"]

  main --> BB["build-backend\nci/backend.Dockerfile"]
  main --> BW["build-web\nci/web.Dockerfile"]
  main --> BWA["build-web-admin\nci/web-admin.Dockerfile"]
  main --> BR["build-runner\nci/runner.Dockerfile"]
  main --> BRL["build-relay\nci/relay.Dockerfile"]

  BB --> |":SHA + :latest"| REG1["agentsmesh/backend"]
  BW --> |":SHA + :latest"| REG2["agentsmesh/web"]
  BWA --> |":SHA + :latest"| REG3["agentsmesh/web-admin"]
  BR --> |":SHA + :latest"| REG4["agentsmesh/runner"]
  BRL --> |":SHA + :latest"| REG5["agentsmesh/relay"]
```

The `backend` and `runner` builds require the `proto/` directory to be in the build context because their `go.mod` files reference it via a `replace` directive. Both Dockerfiles are therefore built from the project root with `-f ci/<service>.Dockerfile`.

Sources: [.gitlab-ci.yml:300-413](), [ci/backend.Dockerfile:15-18](), [ci/runner.Dockerfile:15-19]()

---

## Dockerfiles

All service Dockerfiles follow a multi-stage build pattern to minimize final image size.

### `ci/backend.Dockerfile`

[ci/backend.Dockerfile:1-67]()

| Stage | Base Image | Purpose |
|---|---|---|
| `builder` | `golang:${GO_VERSION}` | Compile the `server` binary with `CGO_ENABLED=0` |
| final | `alpine:3.19` | Runtime image with `ca-certificates`, `tzdata`, `curl`, `git`, and `migrate` |

Notable details:
- The `golang-migrate` binary is installed in the final image so database migrations can be run manually against the container.
- `proto/` is copied before `backend/go.mod` to satisfy the local module replace directive.
- A `/data/acme` directory is created for ACME (Let's Encrypt) certificate storage.
- The binary runs as a non-root `app` user (UID 1000).

### `ci/web.Dockerfile`

[ci/web.Dockerfile:1-94]()

| Stage | Base Image | Purpose |
|---|---|---|
| `deps` | `node:20-alpine` | Install npm/pnpm dependencies |
| `builder` | `node:20-alpine` | Run `pnpm build`, produce Next.js standalone output |
| `runner` | `node:20-alpine` | Serve `server.js` via `docker-entrypoint.sh` |

Key pattern: `NEXT_PUBLIC_PRIMARY_DOMAIN` and `NEXT_PUBLIC_USE_HTTPS` are baked into the build as placeholder strings (`__PRIMARY_DOMAIN__` and `__USE_HTTPS__`). The `docker-entrypoint.sh` script performs a string substitution at container start time, enabling runtime configuration without rebuilding the image. See [5.6](#5.6) for how the frontend resolves these at runtime.

### `ci/web-admin.Dockerfile`

[ci/web-admin.Dockerfile:1-86]()

Same three-stage pattern as `web.Dockerfile`. Runs on port `3001` instead of `3000`. Accepts `NPM_REGISTRY` as a `--build-arg` to point pnpm at the Huawei Cloud npm mirror during CI builds.

### `ci/runner.Dockerfile`

[ci/runner.Dockerfile:1-71]()

| Stage | Base Image | Purpose |
|---|---|---|
| `builder` | `golang:${GO_VERSION}` | Compile the `runner` binary with `CGO_ENABLED=0 -tags nocgo` |
| final | `alpine:3.19` | Runtime with `git`, `openssh-client`, `bash`, `curl` |

The `nocgo` build tag disables CGO-dependent code paths (e.g., PTY on Linux). Git and SSH are included because the runner clones repositories and manages worktrees. The working directory is `/workspace`.

### `ci/relay.Dockerfile`

[ci/relay.Dockerfile:1-45]()

The simplest Dockerfile: golang builder produces the `relay` binary, copied into a minimal `alpine:3.19` image with only `ca-certificates` and `tzdata`. Exposes port `8090`.

---

## Deploy Stage

Deployments are triggered automatically on `main` branch pushes (after successful builds) or manually via the GitLab UI. Deployments use SSH to reach production servers and run a `deploy.sh` script on each host.

**Diagram — Deploy stage topology:**

```mermaid
graph TD
  BUILD["Build Stage\n:SHA image in registry"]

  BUILD --> |"needs: build-backend"| CNB["deploy:cn-prod:backend\nssh aliyun-s001\n./deploy.sh cn-prod --service backend"]
  BUILD --> |"needs: build-web"| CNW["deploy:cn-prod:web\nssh aliyun-s001\n./deploy.sh cn-prod --service web"]
  BUILD --> |"needs: build-web-admin"| CNWA["deploy:cn-prod:web-admin\nssh aliyun-s001\n./deploy.sh cn-prod --service web-admin"]
  BUILD --> |"needs: build-relay"| CNR["deploy:cn-prod:cn-relay-01\nssh aliyun-cn-relay-01"]

  BUILD --> |"needs: build-backend"| USB["deploy:uswest-prod:backend\nssh aliyun-us-west-001\n./deploy.sh uswest-prod --service backend"]
  BUILD --> |"needs: build-web"| USW["deploy:uswest-prod:web\nssh aliyun-us-west-001\n./deploy.sh uswest-prod --service web"]
  BUILD --> |"needs: build-web-admin"| USWA["deploy:uswest-prod:web-admin\nssh aliyun-us-west-001\n./deploy.sh uswest-prod --service web-admin"]
  BUILD --> |"needs: build-relay"| USR1["deploy:uswest-prod:uswest-relay-01\nssh aliyun-us-west-relay-001"]
  BUILD --> |"needs: build-relay"| USR2["deploy:uswest-prod:uswest-relay-beijing-02\nssh aliyun-agentsmesh-us-relay-beijing-002"]

  CNB --> |"needs: deploy:cn-prod:backend"| CMG["migrate:cn-prod\n./migrate.sh cn-prod"]
  USB --> |"needs: deploy:uswest-prod:backend"| UMG["migrate:uswest-prod\n./migrate.sh uswest-prod"]
```

Sources: [.gitlab-ci.yml:415-701]()

### Production Environments

| Environment Name | URL | Primary Host |
|---|---|---|
| `cn-production` | `https://agentsmesh.cn` | `aliyun-s001` |
| `uswest-production` | `https://agentsmesh.ai` | `aliyun-us-west-001` |

### Relay Nodes

| Job Name | Host | Environment | URL |
|---|---|---|---|
| `deploy:cn-prod:cn-relay-01` | `aliyun-cn-relay-01` | `cn-production` | `https://01.relay.agentsmesh.cn:8443` |
| `deploy:uswest-prod:uswest-relay-01` | `aliyun-us-west-relay-001` | `uswest-production` | `https://01.relay.agentsmesh.ai:8443` |
| `deploy:uswest-prod:uswest-relay-beijing-02` | `aliyun-agentsmesh-us-relay-beijing-002` | `uswest-production` | `https://beijing-02.relay.agentsmesh.ai:8443` |

`uswest-relay-beijing-02` is described in the pipeline as a "Beijing accelerator for US West" — a relay node physically located in Beijing that serves users connecting to the US West backend.

### Deploy Script Invocation

Each service deployment follows this pattern on the remote host:

```
cd /opt/agentsmesh && git pull origin main
./deploy.sh <env> --service <service> --version <DEPLOY_VERSION>
```

`DEPLOY_VERSION` defaults to `${CI_COMMIT_SHORT_SHA}`. It can be overridden when triggering the pipeline manually (via `$CI_PIPELINE_SOURCE == "web"`) to perform a rollback to any previously built SHA.

Relay deployments use a slightly different invocation:

```
cd /opt/agentsmesh/relay && ./deploy.sh <relay-name> --pull
```

Sources: [.gitlab-ci.yml:434-438](), [.gitlab-ci.yml:508-510](), [.gitlab-ci.yml:639-641]()

---

## Database Migrations

Migration jobs run in the `deploy` stage and are gated on the corresponding backend deploy job completing successfully. They only activate when files under `backend/migrations/**/*` change.

| Job | Depends On | Host |
|---|---|---|
| `migrate:cn-prod` | `deploy:cn-prod:backend` | `aliyun-s001` |
| `migrate:uswest-prod` | `deploy:uswest-prod:backend` | `aliyun-us-west-001` |

Invocation on host:

```
./migrate.sh <env> --direction up [--steps N]
```

The `MIGRATE_DIRECTION` variable defaults to `up`. `MIGRATE_STEPS` is empty by default (runs all pending migrations). Both can be overridden for manual rollbacks via the GitLab web UI. Migrations run **after** the backend is deployed so the new binary is already in place.

The `migrate` binary is installed in the backend Docker image ([ci/backend.Dockerfile:35-38]()) but the migration job itself runs the `migrate.sh` script on the host rather than inside the container, keeping migration control out-of-band from the server process.

Sources: [.gitlab-ci.yml:521-546](), [.gitlab-ci.yml:673-701](), [ci/backend.Dockerfile:35-38]()

---

## Full Pipeline Flow

**End-to-end pipeline — Merge Request vs Main Branch:**

```mermaid
sequenceDiagram
  participant DEV as "Developer"
  participant MR as "Merge Request Pipeline"
  participant MAIN as "Main Branch Pipeline"
  participant REG as "registry.corp.agentsmesh.ai"
  participant PROD as "Production Hosts"

  DEV->>MR: "Open MR"
  MR->>MR: "test-backend / test-web / test-runner / test-relay"
  MR->>MR: "verify-build-{backend,web,web-admin,runner,relay}"
  Note over MR: "No image push on MR"

  DEV->>MAIN: "Merge to main"
  MAIN->>MAIN: "build-{backend,web,web-admin,runner,relay}"
  MAIN->>REG: "Push :SHA and :latest tags"
  MAIN->>PROD: "deploy:cn-prod:* via SSH"
  MAIN->>PROD: "deploy:uswest-prod:* via SSH"
  MAIN->>PROD: "migrate:cn-prod (if migrations changed)"
  MAIN->>PROD: "migrate:uswest-prod (if migrations changed)"
```

Sources: [.gitlab-ci.yml:1-702]()

---

# Page: Release Process

# Release Process

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/release.yml](.github/workflows/release.yml)
- [.gitlab-ci.yml](.gitlab-ci.yml)
- [backend/internal/service/runner/version_checker.go](backend/internal/service/runner/version_checker.go)
- [backend/internal/service/runner/version_checker_test.go](backend/internal/service/runner/version_checker_test.go)
- [ci/backend.Dockerfile](ci/backend.Dockerfile)
- [ci/relay.Dockerfile](ci/relay.Dockerfile)
- [ci/runner.Dockerfile](ci/runner.Dockerfile)
- [ci/web-admin.Dockerfile](ci/web-admin.Dockerfile)
- [ci/web.Dockerfile](ci/web.Dockerfile)
- [docs/rfc/RFC-003-runner-release-pipeline.md](docs/rfc/RFC-003-runner-release-pipeline.md)
- [runner/.goreleaser.yml](runner/.goreleaser.yml)
- [runner/README.md](runner/README.md)
- [runner/build/scripts/sign-darwin.sh](runner/build/scripts/sign-darwin.sh)
- [runner/internal/config/config.go](runner/internal/config/config.go)
- [runner/internal/config/config_defaults_test.go](runner/internal/config/config_defaults_test.go)
- [runner/internal/updater/updater.go](runner/internal/updater/updater.go)
- [runner/internal/updater/updater_test.go](runner/internal/updater/updater_test.go)
- [runner/internal/workspace/repo_auth.go](runner/internal/workspace/repo_auth.go)
- [runner/internal/workspace/workspace.go](runner/internal/workspace/workspace.go)
- [runner/internal/workspace/workspace_utils.go](runner/internal/workspace/workspace_utils.go)
- [web/public/install.ps1](web/public/install.ps1)
- [web/public/install.sh](web/public/install.sh)
- [web/src/app/docs/runners/setup/page.tsx](web/src/app/docs/runners/setup/page.tsx)
- [web/src/lib/terminalScheduler.ts](web/src/lib/terminalScheduler.ts)
- [web/vitest.config.ts](web/vitest.config.ts)

</details>



This page documents the public release pipeline for AgentsMesh: how Docker images are built and pushed to Docker Hub, how the runner binary is compiled and distributed via GitHub Releases, how macOS code signing works, and how the Homebrew formula is kept up to date.

For the internal GitLab CI/CD pipeline that builds and deploys the SaaS services to production servers, see [8.1](). For how runners self-update after a release lands, see [3.8]().

---

## Overview

AgentsMesh has two parallel release pipelines:

| Pipeline | Platform | Trigger | Output |
|---|---|---|---|
| GitHub Actions (`.github/workflows/release.yml`) | Public | Push to `main` or `v*` tag | Docker Hub images; GitHub Release with runner binaries |
| GitLab CI (`.gitlab-ci.yml`) | Internal | Push to `main` or `v*` tag | Internal registry images; production deployments |

This page focuses on the **GitHub Actions** pipeline, which produces all public-facing artifacts.

Sources: [.github/workflows/release.yml:1-120](), [.gitlab-ci.yml:1-10]()

---

## Pipeline Trigger and Job Structure

**Release pipeline flow**

```mermaid
flowchart TD
    push_main["push to main"] --> build_images["build-images (matrix)"]
    push_tag["push v* tag"] --> build_images
    push_tag --> release["release (GoReleaser)"]
    build_images --> |"needs: build-images"| release

    build_images --> backend_img["agentsmesh/backend:sha / :semver"]
    build_images --> web_img["agentsmesh/web:sha / :semver"]
    build_images --> web_admin_img["agentsmesh/web-admin:sha / :semver"]
    build_images --> relay_img["agentsmesh/relay:sha / :semver"]

    release --> github_release["GitHub Release vX.Y.Z"]
    release --> brew_tap["AgentsMesh/BrewCask Formula update"]
```

Sources: [.github/workflows/release.yml:13-120]()

The `release` job has the conditional `if: startsWith(github.ref, 'refs/tags/v')`, so it only runs on version tags. The `build-images` job runs on every push to `main` and on every version tag.

---

## Docker Image Builds

### Service Matrix

The `build-images` job uses a matrix strategy to build four services in parallel:

| Service | Dockerfile | Build Context |
|---|---|---|
| `backend` | `ci/backend.Dockerfile` | `.` (repo root) |
| `web` | `ci/web.Dockerfile` | `./web` |
| `web-admin` | `ci/web-admin.Dockerfile` | `./web-admin` |
| `relay` | `ci/relay.Dockerfile` | `.` (repo root) |

Sources: [.github/workflows/release.yml:21-76]()

### Image Tags

The `docker/metadata-action` generates tags based on the event:

| Event | Tags Applied |
|---|---|
| Push to `main` | `sha-<short_sha>` |
| Push of `v1.2.3` tag | `1.2.3`, `1.2` |

Images are pushed to Docker Hub under the `agentsmesh` namespace (e.g., `agentsmesh/backend:1.2.3`). Both `linux/amd64` and `linux/arm64` platforms are built using Docker Buildx.

### Dockerfile Internals

All service Dockerfiles follow a multi-stage build pattern:

- **Backend** ([ci/backend.Dockerfile:1-67]()): `golang` builder → `alpine` final. Installs `golang-migrate` for running database migrations. Build context must be the project root so the `proto/` directory is accessible.
- **Web** ([ci/web.Dockerfile:1-94]()): `node:20-alpine` deps stage → builder stage → runner stage. Uses placeholder env vars (`__PRIMARY_DOMAIN__`, `__USE_HTTPS__`) replaced at container start by `docker-entrypoint.sh`.
- **Web-Admin** ([ci/web-admin.Dockerfile:1-87]()): Same pattern as web, runs on port `3001`.
- **Relay** ([ci/relay.Dockerfile:1-45]()): `golang` builder → `alpine` final.
- **Runner** ([ci/runner.Dockerfile:1-72]()): `golang` builder → `alpine` final. Includes `git`, `openssh-client`, and `bash` for workspace operations.

`GOPROXY` and `NPM_REGISTRY` are passed as build arguments for region-specific mirror overrides.

Sources: [ci/backend.Dockerfile:1-10](), [ci/web.Dockerfile:32-48](), [ci/runner.Dockerfile:26-26]()

---

## Runner Binary Release (GoReleaser)

The `release` job installs `rcodesign` for macOS signing, then runs GoReleaser from the `runner/` subdirectory using the config at `runner/.goreleaser.yml`.

**GoReleaser artifact pipeline**

```mermaid
flowchart LR
    src["runner/cmd/runner"] --> cli_build["runner-cli build\n(CGO_ENABLED=0)"]

    cli_build --> darwin_amd64["darwin/amd64"]
    cli_build --> darwin_arm64["darwin/arm64"]
    cli_build --> linux_amd64["linux/amd64"]
    cli_build --> linux_arm64["linux/arm64"]
    cli_build --> windows_amd64["windows/amd64"]
    cli_build --> windows_arm64["windows/arm64"]

    darwin_amd64 --> sign_hook["sign-darwin.sh\n(rcodesign)"]
    darwin_arm64 --> sign_hook

    darwin_amd64 --> universal_binary["runner-universal\n(lipo merge)"]
    darwin_arm64 --> universal_binary

    universal_binary --> darwin_all_archive["cli-archive-darwin-universal\nagentsmesh-runner_VER_darwin_all.tar.gz"]

    darwin_amd64 --> cli_archive["cli-archive (.tar.gz / .zip)"]
    darwin_arm64 --> cli_archive
    linux_amd64 --> cli_archive
    linux_arm64 --> cli_archive
    windows_amd64 --> cli_archive
    windows_arm64 --> cli_archive

    linux_amd64 --> nfpm["runner-deb-rpm\n(.deb / .rpm / .apk)"]

    cli_archive --> github_release["GitHub Release\nAgentsMesh/AgentsMesh"]
    darwin_all_archive --> github_release
    nfpm --> github_release
    github_release --> checksum["checksums.txt (sha256)"]

    github_release --> brew_tap["AgentsMesh/BrewCask\nFormula/agentsmesh-runner.rb"]
```

Sources: [runner/.goreleaser.yml:1-272](), [.github/workflows/release.yml:82-120]()

### Build Configuration

Defined in [runner/.goreleaser.yml:15-37]():

- **Binary name**: `agentsmesh-runner`
- **Entry point**: `./cmd/runner`
- **CGO**: disabled (`CGO_ENABLED=0`) — no system dependencies
- **ldflags**: inject `main.version` and `main.buildTime` at build time
- **`replace: false`** on `universal_binaries` preserves individual architecture archives alongside the universal one

### Release Artifacts

| File Pattern | Description |
|---|---|
| `agentsmesh-runner_X.Y.Z_darwin_all.tar.gz` | macOS Universal (amd64 + arm64) |
| `agentsmesh-runner_X.Y.Z_darwin_amd64.tar.gz` | macOS Intel |
| `agentsmesh-runner_X.Y.Z_darwin_arm64.tar.gz` | macOS Apple Silicon |
| `agentsmesh-runner_X.Y.Z_linux_amd64.tar.gz` | Linux x86-64 |
| `agentsmesh-runner_X.Y.Z_linux_arm64.tar.gz` | Linux ARM64 |
| `agentsmesh-runner_X.Y.Z_linux_amd64.deb` | Debian/Ubuntu package |
| `agentsmesh-runner_X.Y.Z_linux_amd64.rpm` | RHEL/Fedora package |
| `agentsmesh-runner_X.Y.Z_linux_amd64.apk` | Alpine package |
| `agentsmesh-runner_X.Y.Z_windows_amd64.zip` | Windows x86-64 |
| `agentsmesh-runner_X.Y.Z_windows_arm64.zip` | Windows ARM64 |
| `checksums.txt` | SHA256 checksums for all artifacts |

Sources: [runner/.goreleaser.yml:39-57](), [docs/rfc/RFC-003-runner-release-pipeline.md:291-305]()

### Linux Package Contents

The `nfpm` section ([runner/.goreleaser.yml:70-115]()) specifies what goes into the `.deb`, `.rpm`, and `.apk` packages:

| Path | Source | Type |
|---|---|---|
| `/usr/local/bin/agentsmesh-runner` | binary | executable |
| `/etc/systemd/system/agentsmesh-runner.service` | `build/linux/runner.service` | config |
| `/etc/agentsmesh/` | (dir) | directory (mode 0755) |

Post-install script: `runner/build/linux/postinst.sh`  
Pre-remove script: `runner/build/linux/prerm.sh`

---

## macOS Code Signing

### Signing Script

[runner/build/scripts/sign-darwin.sh:1-27]() is called as a GoReleaser `post` build hook for every `darwin` target binary ([runner/.goreleaser.yml:33-37]()):

```
post:
  - cmd: sh -c '[ "{{ .Os }}" = "darwin" ] && ./build/scripts/sign-darwin.sh "{{ .Path }}" || true'
```

The script:
1. Decodes `MACOS_CERTIFICATE` (base64-encoded `.p12` file) to a temp file
2. Calls `rcodesign sign` with the p12, password, `runtime` code signature flag, and entitlements from `build/darwin/entitlements.plist`
3. Exits silently (`exit 0`) if `MACOS_CERTIFICATE` is not set, allowing unsigned local builds

### Required GitHub Secrets

| Secret | Purpose |
|---|---|
| `MACOS_CERTIFICATE` | Base64-encoded Developer ID `.p12` certificate |
| `MACOS_CERTIFICATE_PASSWORD` | Password for the `.p12` file |
| `HOMEBREW_TAP_TOKEN` | GitHub token with write access to `AgentsMesh/BrewCask` |
| `GITHUB_TOKEN` | Standard Actions token for creating the GitHub Release |

Sources: [runner/build/scripts/sign-darwin.sh:1-27](), [.github/workflows/release.yml:100-119]()

---

## Homebrew Tap Update

GoReleaser automatically commits an updated formula to `AgentsMesh/BrewCask` after a successful release ([runner/.goreleaser.yml:220-252]()):

- **Repository**: `AgentsMesh/BrewCask`
- **Formula file**: `Formula/agentsmesh-runner.rb`
- **Commit author**: `AgentsMesh Bot <bot@agentsmesh.ai>`
- **Install block**: `bin.install "agentsmesh-runner"`
- **Covers**: `cli-archive` (per-arch tarballs) and `cli-archive-darwin-universal` (universal binary)

The formula includes `test`, `caveats`, and a `description` block. Users install via:

```bash
brew tap agentsmesh/tap https://github.com/AgentsMesh/BrewCask
brew install agentsmesh/tap/agentsmesh-runner
```

Sources: [runner/.goreleaser.yml:219-252](), [runner/README.md:32-38]()

---

## Release Changelog

GoReleaser generates the changelog automatically from git commit history ([runner/.goreleaser.yml:140-163]()), grouped by conventional commit prefix:

| Group | Regexp | Order |
|---|---|---|
| New Features | `feat(...)` | 0 |
| Bug Fixes | `fix(...)` | 1 |
| Performance | `perf(...)` | 2 |
| Other | (all remaining) | 999 |

Commits prefixed with `docs:`, `test:`, `chore:`, `ci:`, and merge commits are excluded from the changelog.

Pre-releases are auto-detected from the tag: a tag like `v1.0.0-beta.1` sets `prerelease: auto` in the GitHub Release.

Sources: [runner/.goreleaser.yml:140-173]()

---

## Post-Release: Version Distribution

After a release is published to GitHub, two systems consume the new version information.

**Version information flow after a release**

```mermaid
flowchart LR
    github_api["GitHub API\nreleases/latest"] --> |"polls every 1h"| VersionChecker["VersionChecker\nbackend/internal/service/runner/version_checker.go"]
    VersionChecker --> |"SET runner:latest_version"| redis["Redis\nTTL: 1h"]
    redis --> |"GET runner:latest_version"| rest_api["REST API\n(runner version endpoint)"]

    github_api --> |"on startup / every 24h"| GitHubReleaseDetector["GitHubReleaseDetector\nrunner/internal/updater/"]
    GitHubReleaseDetector --> Updater["Updater\nupdater.go"]
    Updater --> |"CheckForUpdate"| semver_cmp["semver comparison\ncurrent vs latest"]
    semver_cmp --> |"HasUpdate=true"| Download["Updater.Download()"]
    Download --> Apply["Updater.Apply()\natomicReplace()"]
    Apply --> |"restart"| runner_process["Runner Process"]

    runner_process --> |"backup before update"| CreateBackup["Updater.CreateBackup()\nexecPath + .bak"]
    CreateBackup --> |"on failure"| Rollback["Updater.Rollback()"]
```

Sources: [backend/internal/service/runner/version_checker.go:1-157](), [runner/internal/updater/updater.go:1-254]()

### Backend `VersionChecker`

`VersionChecker` ([backend/internal/service/runner/version_checker.go:33-38]()) runs as a background goroutine in the backend process:

- Polls `https://api.github.com/repos/AgentsMesh/AgentsMesh/releases/latest` every `1h`
- Stores the normalized version string (e.g., `1.2.3`) under Redis key `runner:latest_version` with a 1-hour TTL
- `NormalizeVersion` strips the `v` prefix from the GitHub tag name
- Returns `""` gracefully on Redis unavailability (silently degrades)

### Runner `Updater`

`Updater` ([runner/internal/updater/updater.go:35-79]()) implements the self-update logic:

| Method | Purpose |
|---|---|
| `CheckForUpdate(ctx)` | Calls `GitHubReleaseDetector.DetectLatest`, compares semver |
| `Download(ctx, version, progress)` | Downloads asset to a temp file |
| `Apply(tmpPath)` | Atomically replaces the current executable (`atomicReplace`) |
| `UpdateNow(ctx, progress)` | Convenience wrapper: check → download → apply |
| `UpdateToVersion(ctx, version, progress)` | Updates to a specific version |
| `CreateBackup()` | Copies `execPath` to `execPath + ".bak"` |
| `Rollback()` | Restores from `.bak` file |

The `allowPrerelease` field (controlled by `AutoUpdateConfig.Channel` = `"stable"` or `"beta"`) gates whether pre-release tags are considered as available updates.

Sources: [runner/internal/updater/updater.go:23-33](), [runner/internal/config/config.go:82-100]()

---

## Installation Scripts

Two shell scripts are served from `web/public/` and used by the one-line install commands:

**`install.sh`** ([web/public/install.sh:1-292]()) — macOS and Linux:
- Calls the GitHub API to get the latest release tag
- Detects OS/arch; uses `darwin_all` (universal binary) for macOS
- Downloads `agentsmesh-runner_{VERSION}_{PLATFORM}.tar.gz` from GitHub Releases
- Installs to `~/.local/bin` by default (no `sudo` required)
- Prints PATH configuration hint if install dir is not in `$PATH`

**`install.ps1`** ([web/public/install.ps1:1-227]()) — Windows:
- Downloads `agentsmesh-runner_{VERSION}_{PLATFORM}.zip` from GitHub Releases
- Installs to `$LOCALAPPDATA\Programs\agentsmesh` by default
- Adds the install directory to the user `PATH` environment variable automatically

---

## Creating a Release

To publish a new runner release:

```bash
# 1. Ensure code is merged to main
git checkout main && git pull origin main

# 2. Create and push a version tag
git tag -a v1.2.3 -m "Release v1.2.3"
git push origin v1.2.3
```

Pushing the tag triggers the GitHub Actions `release.yml` workflow, which:
1. Runs `build-images` for all four Docker services
2. Runs `release` (GoReleaser) for the runner binary
3. Signs macOS binaries, creates the universal binary
4. Publishes the GitHub Release with all artifacts and changelog
5. Pushes an updated Homebrew formula to `AgentsMesh/BrewCask`

To re-release the same tag (after a fix):

```bash
git tag -d v1.2.3
git push origin :refs/tags/v1.2.3
git tag -a v1.2.3 -m "Release v1.2.3 (revised)"
git push origin v1.2.3
```

Sources: [runner/README.md:132-148](), [docs/rfc/RFC-003-runner-release-pipeline.md:263-289]()

---

# Page: On-Premise Deployment

# On-Premise Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/internal/api/rest/internal/relay_registration.go](backend/internal/api/rest/internal/relay_registration.go)
- [backend/internal/api/rest/internal/relay_registration_test.go](backend/internal/api/rest/internal/relay_registration_test.go)
- [backend/internal/config/config.go](backend/internal/config/config.go)
- [backend/internal/config/config_relay.go](backend/internal/config/config_relay.go)
- [backend/internal/infra/storage/s3.go](backend/internal/infra/storage/s3.go)
- [backend/internal/service/relay/dns_service.go](backend/internal/service/relay/dns_service.go)
- [backend/internal/service/relay/dns_service_mock_test.go](backend/internal/service/relay/dns_service_mock_test.go)
- [backend/internal/service/relay/dns_service_sanitize_test.go](backend/internal/service/relay/dns_service_sanitize_test.go)
- [backend/migrations/000033_move_preparation_script_to_repository.down.sql](backend/migrations/000033_move_preparation_script_to_repository.down.sql)
- [backend/migrations/000033_move_preparation_script_to_repository.up.sql](backend/migrations/000033_move_preparation_script_to_repository.up.sql)
- [ci/build-onpremise.sh](ci/build-onpremise.sh)
- [ci/pack-onpremise.sh](ci/pack-onpremise.sh)
- [deploy/dev/runner-ssh/README.md](deploy/dev/runner-ssh/README.md)
- [deploy/onpremise/README.md](deploy/onpremise/README.md)
- [deploy/onpremise/docker-compose.yml](deploy/onpremise/docker-compose.yml)
- [deploy/onpremise/scripts/generate-certs.sh](deploy/onpremise/scripts/generate-certs.sh)
- [deploy/onpremise/scripts/install.sh](deploy/onpremise/scripts/install.sh)
- [deploy/onpremise/scripts/load-images.sh](deploy/onpremise/scripts/load-images.sh)
- [deploy/onpremise/seed/onpremise-seed.sql](deploy/onpremise/seed/onpremise-seed.sql)
- [docs/images/logo.svg](docs/images/logo.svg)
- [e2e/README.md](e2e/README.md)
- [relay/.env.example](relay/.env.example)
- [relay/internal/config/config.go](relay/internal/config/config.go)
- [relay/internal/config/config_test.go](relay/internal/config/config_test.go)
- [web-admin/.env.example](web-admin/.env.example)

</details>



This page documents the self-hosted, on-premise deployment of AgentsMesh. It covers the installer script, Docker Compose service topology, SSL certificate generation, seed data initialization, MinIO configuration, and runner registration. On-premise deployment is designed to work on a bare IP address with no domain name required, making it suitable for private networks and air-gapped environments.

For information about the SaaS CI/CD pipeline, see [8.1](#8.1). For the public GitHub runner release process, see [8.2](#8.2). For general backend configuration reference (environment variables), see [2.7](#2.7).

---

## Overview

The on-premise package bundles all AgentsMesh services as pre-built Docker images alongside a set of helper scripts. A single command (`install.sh --ip <SERVER_IP>`) handles the full setup: image loading, secret generation, SSL certificate creation, service startup, database migration, and seed data import.

All services are fronted by a Traefik reverse proxy. The web frontend and API are accessed over HTTP on the server IP, while gRPC mTLS runner connections use a separate port (default `9443`).

**Deployment package location:** `deploy/onpremise/`

---

## Service Topology

**Docker Compose service graph for on-premise deployment**

```mermaid
graph TD
  Internet["External: Browser / Runner"]
  Traefik["traefik\n:80 (HTTP)\n:9443 (gRPC+mTLS)"]
  Web["web\n(Next.js frontend)\n:3000"]
  WebAdmin["web-admin\n(Admin console)\n:3001"]
  Backend["backend\n(Go API + gRPC)\n:8080 / :9090"]
  Relay["relay\n(WebSocket terminal)\n:8090"]
  Postgres["postgres\n:5432"]
  Redis["redis\n:6379"]
  Minio["minio\n:9000 (API)\n:9001 (Console)"]

  Internet --> Traefik
  Traefik --> Web
  Traefik --> WebAdmin
  Traefik --> Backend
  Traefik --> Relay
  Backend --> Postgres
  Backend --> Redis
  Backend --> Minio
  Web --> Backend
  WebAdmin --> Backend
  Relay --> Backend
```

Sources: [deploy/onpremise/docker-compose.yml:1-283]()

---

## Prerequisites

| Requirement | Minimum |
|---|---|
| Docker | 20.10+ |
| Docker Compose | V2 |
| RAM | 4 GB |
| Disk | 20 GB |

The installer requires `openssl` to be present on the host for certificate generation.

---

## Deployment Package Structure

```
deploy/onpremise/
├── docker-compose.yml          # Defines all 8 services
├── .env.template               # Environment variable template
├── .env                        # Generated by install.sh
├── traefik/
│   ├── traefik.yml             # Static Traefik configuration
│   └── dynamic/
│       └── grpc.yml            # gRPC + mTLS routing rules
├── ssl/                        # Created by generate-certs.sh
│   ├── ca.crt / ca.key
│   └── server.crt / server.key
├── seed/
│   └── onpremise-seed.sql      # Initial admin user, org, and runner token
├── images/                     # Pre-exported .tar files (for air-gapped install)
└── scripts/
    ├── install.sh              # Full one-command installer
    ├── load-images.sh          # Loads .tar files into Docker
    └── generate-certs.sh       # Generates SSL certificates
```

Sources: [deploy/onpremise/README.md:83-113]()

---

## Installation

### Option 1: install.sh (Recommended)

[deploy/onpremise/scripts/install.sh]() runs 7 sequential steps:

**install.sh step sequence**

```mermaid
flowchart LR
  S0["Step 0\n--clean (optional)\ndocker compose down -v"]
  S1["Step 1\nCheck Docker\ndocker info"]
  S2["Step 2\nLoad images\nload-images.sh"]
  S3["Step 3\nGenerate secrets\nWrite .env"]
  S4["Step 4\nGenerate SSL certs\ngenerate-certs.sh"]
  S5["Step 5\nStart services\ndocker compose up -d"]
  S6["Step 6\nRun migrations\nmigrate up"]
  S7["Step 7\nImport seed data\nonpremise-seed.sql"]

  S0 --> S1 --> S2 --> S3 --> S4 --> S5 --> S6 --> S7
```

**Basic usage:**

```bash
./scripts/install.sh --ip 192.168.1.100
```

**Available flags:**

| Flag | Default | Description |
|---|---|---|
| `--ip` | *(required)* | Server IP address |
| `--http-port` | `80` | HTTP port for Traefik |
| `--grpc-port` | `9443` | gRPC + mTLS port |
| `--version` | `v1.0.0` | Docker image version tag |
| `--skip-load` | `false` | Skip loading images (use existing) |
| `--clean` | `false` | Tear down existing deployment first |

Sources: [deploy/onpremise/scripts/install.sh:1-324]()

### Option 2: Manual Installation

```bash
# 1. Load images (for air-gapped environments)
./scripts/load-images.sh

# 2. Generate SSL certificates for the server IP
./scripts/generate-certs.sh 192.168.1.100

# 3. Create and populate .env
cp .env.template .env

# 4. Start all services
docker compose up -d

# 5. Run database migrations
docker compose exec -T backend migrate \
  -path /app/migrations \
  -database "postgres://agentsmesh:<DB_PASSWORD>@postgres:5432/agentsmesh?sslmode=disable" up

# 6. Import seed data
docker compose exec -T postgres psql -U agentsmesh -d agentsmesh \
  < seed/onpremise-seed.sql
```

Sources: [deploy/onpremise/README.md:28-50]()

---

## Environment Configuration

`install.sh` generates the `.env` file from detected values and random secrets. On subsequent runs (upgrades), existing secrets are preserved by sourcing the existing `.env`.

**Generated `.env` variables:**

| Variable | Example Value | Description |
|---|---|---|
| `SERVER_IP` | `192.168.1.100` | Server IP (used as `PRIMARY_DOMAIN`) |
| `HTTP_PORT` | `80` | Traefik HTTP port |
| `GRPC_PORT` | `9443` | Traefik gRPC/mTLS port |
| `DB_PASSWORD` | *(random 32-char)* | PostgreSQL password |
| `JWT_SECRET` | *(random 32-char)* | JWT signing secret |
| `INTERNAL_API_SECRET` | *(random 32-char)* | Internal service auth secret |
| `MINIO_ROOT_PASSWORD` | *(random 32-char)* | MinIO root password |
| `DEPLOYMENT_TYPE` | `onpremise` | Disables cloud billing integrations |
| `EMAIL_PROVIDER` | `console` | Logs emails to stdout instead of sending |

The backend reads these via its `Load()` function in [backend/internal/config/config.go:49-233]().

### IP-Based Access (No Domain Required)

The key difference from a cloud deployment is how `PRIMARY_DOMAIN` is set. In on-premise mode:

- **Backend:** `PRIMARY_DOMAIN=` (empty — uses relative paths, auto-detects from browser)
- **Web:** `PRIMARY_DOMAIN=${SERVER_IP}` (e.g., `192.168.1.100`)
- **Web-Admin:** `PRIMARY_DOMAIN=${SERVER_IP}`
- **Relay:** `PRIMARY_DOMAIN=${SERVER_IP}` → generates `ws://192.168.1.100/relay`
- `USE_HTTPS=false` everywhere

This means no DNS registration, no Let's Encrypt, and no Cloudflare/Aliyun DNS configuration is needed.

Sources: [deploy/onpremise/docker-compose.yml:88-96](), [deploy/onpremise/docker-compose.yml:183-191](), [deploy/onpremise/docker-compose.yml:244-252]()

---

## SSL Certificate Generation

On-premise uses self-signed certificates for **gRPC mTLS** between the Backend and Runners. No HTTPS is used for the web frontend by default.

`generate-certs.sh` creates a two-tier PKI:

**Certificate generation flow**

```mermaid
flowchart TD
  CA_KEY["ca.key\nopenssl ecparam -name prime256v1"]
  CA_CERT["ca.crt\nself-signed, 3650 days\nCN=AgentsMesh OnPremise CA"]
  SERVER_KEY["server.key\nopenssl ecparam -name prime256v1"]
  SERVER_CSR["server.csr\nCN=agentsmesh-backend"]
  EXT["server_ext.cnf\nSAN: localhost, backend, traefik, *.local\nIP: 127.0.0.1, ::1, SERVER_IP"]
  SERVER_CERT["server.crt\nsigned by CA, 365 days"]

  CA_KEY --> CA_CERT
  SERVER_KEY --> SERVER_CSR
  SERVER_CSR --> SERVER_CERT
  CA_CERT --> SERVER_CERT
  EXT --> SERVER_CERT
```

The server certificate's Subject Alternative Names (SANs) include the server IP (`IP.3 = ${SERVER_IP}`), which is required for the Runner to validate the certificate when connecting via the server IP address.

The CA and server certificates are mounted read-only into the backend container at `/app/ssl/`. The backend PKI service reads them via:
- `PKI_CA_CERT_FILE=/app/ssl/ca.crt`
- `PKI_CA_KEY_FILE=/app/ssl/ca.key`
- `PKI_SERVER_CERT_FILE` / `PKI_SERVER_KEY_FILE` (from `PKIConfig` in [backend/internal/config/config.go:186-192]())

Sources: [deploy/onpremise/scripts/generate-certs.sh:1-96](), [deploy/onpremise/docker-compose.yml:148-165]()

---

## Docker Services

**Service configuration summary**

```mermaid
graph TD
  subgraph "Infrastructure"
    PG["postgres:16-alpine\nVolume: postgres_data\nPort: 5432"]
    RD["redis:7-alpine\nVolume: redis_data\nPort: 6379"]
    MN["minio/minio:latest\nVolume: minio_data\nPorts: 9000, 9001"]
  end

  subgraph "Application"
    BE["agentsmesh/backend\nPorts: 8080 (REST), 9090 (gRPC)\npull_policy: never"]
    WB["agentsmesh/web\nPort: 3000\npull_policy: never"]
    WA["agentsmesh/web-admin\nPort: 3001\npull_policy: never"]
    RL["agentsmesh/relay\nPort: 8090\npull_policy: never"]
  end

  subgraph "Ingress"
    TK["traefik:v3.2\nPorts: 80 (HTTP), 9443 (gRPC)"]
  end

  BE --> PG
  BE --> RD
  BE --> MN
  WB --> BE
  WA --> BE
  RL --> BE
  TK --> BE
  TK --> WB
  TK --> WA
  TK --> RL
```

`pull_policy: never` is used for all AgentsMesh application images because they are loaded from `.tar` files during air-gapped deployment, not pulled from a registry.

Sources: [deploy/onpremise/docker-compose.yml:78-82](), [deploy/onpremise/docker-compose.yml:178-181](), [deploy/onpremise/docker-compose.yml:200-202](), [deploy/onpremise/docker-compose.yml:224-226]()

### MinIO (Object Storage)

MinIO provides S3-compatible storage for file uploads. The backend's `S3Storage` client ([backend/internal/infra/storage/s3.go:29-108]()) requires path-style URL mode for MinIO:

| Backend Env Var | On-Premise Value | Notes |
|---|---|---|
| `STORAGE_ENDPOINT` | `minio:9000` | Internal Docker network address |
| `STORAGE_PUBLIC_ENDPOINT` | `${SERVER_IP}:${MINIO_API_PORT}` | Public URL for browser file access |
| `STORAGE_USE_SSL` | `false` | No TLS inside Docker network |
| `STORAGE_USE_PATH_STYLE` | `true` | Required for MinIO; sets `UsePathStyle` on `s3.Options` |
| `STORAGE_BUCKET` | `agentsmesh` | Auto-created on startup |
| `STORAGE_ACCESS_KEY` | `minioadmin` | MinIO root user |
| `STORAGE_SECRET_KEY` | `${MINIO_ROOT_PASSWORD}` | MinIO root password |

When `STORAGE_PUBLIC_ENDPOINT` differs from `STORAGE_ENDPOINT`, the backend's `GetURL()` method ([backend/internal/infra/storage/s3.go:160-186]()) returns a direct public URL (not pre-signed), using path-style format: `http://<SERVER_IP>:9000/agentsmesh/<key>`.

Sources: [deploy/onpremise/docker-compose.yml:57-73](), [deploy/onpremise/docker-compose.yml:129-140]()

---

## Seed Data

[deploy/onpremise/seed/onpremise-seed.sql]() runs as an idempotent PL/pgSQL block that creates the initial state:

**Seed data entities**

| Entity | Details |
|---|---|
| **Admin User** | `admin@localhost.local` / `Admin@123` (bcrypt, cost=10), `is_system_admin=true` |
| **Organization** | slug=`default`, name=`Default Organization`, `subscription_plan=onpremise` |
| **Subscription** | `plan_id=4` (Enterprise/OnPremise), `seat_count=9999`, active for 365 days |
| **Runner Token** | `onpremise-runner-token` (stored as bcrypt hash), unlimited uses, in `runner_grpc_registration_tokens` |

All inserts use `WHERE NOT EXISTS` guards, making the seed script safe to re-run.

> ⚠️ **Change the admin password immediately after first login.**

Sources: [deploy/onpremise/seed/onpremise-seed.sql:1-127]()

---

## Access URLs

After installation completes:

| Service | URL | Description |
|---|---|---|
| Frontend | `http://<SERVER_IP>` | Main user interface |
| Admin Console | `http://<SERVER_IP>:3001` | Internal admin console |
| MinIO Console | `http://<SERVER_IP>:9001` | Object storage management |

Sources: [deploy/onpremise/scripts/install.sh:304-308]()

---

## Runner Registration

Runners run on separate machines and connect back to the backend over gRPC mTLS. The `onpremise-runner-token` created by the seed SQL is used for initial registration.

```bash
# Install the runner binary (requires internet access)
curl -fsSL https://agentsmesh.ai/install.sh | sh

# Register against the on-premise backend
agentsmesh-runner register \
  --server http://192.168.1.100 \
  --token onpremise-runner-token

# Start the runner
agentsmesh-runner run
```

The Runner's gRPC connection goes through Traefik on port `9443` (configurable with `--grpc-port`). The backend returns the gRPC public endpoint via `GRPC_PUBLIC_ENDPOINT=grpc://${SERVER_IP}:${GRPC_PORT:-9443}` in the registration response.

**Required firewall ports:**

| Port | Protocol | Purpose |
|---|---|---|
| `80` | TCP | HTTP (Frontend, API via Traefik) |
| `9443` | TCP | gRPC + mTLS (Runner connections) |
| `9001` | TCP | MinIO Console (optional, admin only) |

For full runner registration and lifecycle details, see [3.1](#3.1).

Sources: [deploy/onpremise/README.md:68-82](), [deploy/onpremise/docker-compose.yml:152-154]()

---

## Air-Gapped Deployment

For environments with no internet access, the build and packaging process exports all Docker images as `.tar` files.

**Build and pack workflow**

```mermaid
flowchart LR
  B["ci/build-onpremise.sh VERSION\nBuilds 4 app images\nPulls 4 base images\nExports all to images/*.tar"]
  P["ci/pack-onpremise.sh VERSION\nCopies deploy/onpremise/*\nCopies images/*.tar\nCreates agentsmesh-onpremise-VERSION.tar.gz"]
  I["install.sh --ip IP\nload-images.sh loads *.tar\ndocker load -i for each file"]

  B --> P --> I
```

`ci/build-onpremise.sh` ([ci/build-onpremise.sh:1-139]()) builds the application images (`backend`, `web`, `web-admin`, `relay`) and pulls base images (`postgres:16-alpine`, `redis:7-alpine`, `minio/minio:latest`, `traefik:v3.2`).

`ci/pack-onpremise.sh` ([ci/pack-onpremise.sh:1-94]()) assembles the deployment archive: `agentsmesh-onpremise-{VERSION}.tar.gz`.

`load-images.sh` ([deploy/onpremise/scripts/load-images.sh:1-72]()) iterates over all `.tar` files in the `images/` directory and calls `docker load -i` on each.

---

## Common Operations

```bash
# Check service status
docker compose ps

# Tail all service logs
docker compose logs -f

# Tail a specific service
docker compose logs -f backend

# Restart a service after config changes
docker compose restart backend

# Stop all services (preserve data)
docker compose down

# Stop all services and delete all volumes
docker compose down -v

# Reapply config changes
docker compose up -d
```

Sources: [deploy/onpremise/README.md:117-138]()

---

## Data Backup and Restore

### Database

```bash
# Backup
docker compose exec postgres pg_dump -U agentsmesh agentsmesh > backup.sql

# Restore
docker compose exec -T postgres psql -U agentsmesh -d agentsmesh < backup.sql
```

### Full Volume Backup

```bash
docker compose down

docker run --rm \
  -v agentsmesh_postgres_data:/data \
  -v $(pwd):/backup alpine \
  tar czf /backup/postgres_backup.tar.gz -C /data .

docker run --rm \
  -v agentsmesh_minio_data:/data \
  -v $(pwd):/backup alpine \
  tar czf /backup/minio_backup.tar.gz -C /data .

docker compose up -d
```

Sources: [deploy/onpremise/README.md:142-167]()

---

## Version Upgrades

```bash
# 1. Backup data (see above)

# 2. Load new version images
./scripts/load-images.sh

# 3. Recreate containers with new images
docker compose up -d

# 4. Run any new migrations
docker compose exec backend migrate \
  -path /app/migrations \
  -database "postgres://agentsmesh:${DB_PASSWORD}@postgres:5432/agentsmesh?sslmode=disable" up
```

Existing secrets in `.env` are preserved across upgrades because `install.sh` sources the current `.env` before writing a new one ([deploy/onpremise/scripts/install.sh:175-190]()).

---

## Troubleshooting

### Services fail to start

```bash
docker info                          # Verify Docker daemon is running
docker compose logs --tail=100       # Inspect startup errors
netstat -tlnp | grep -E ':(80|9443|5432|6379|9000)\s'  # Check port conflicts
```

### Database connection failures

```bash
docker compose exec postgres pg_isready -U agentsmesh
docker compose logs postgres
```

### Runner cannot connect

1. Confirm ports `80` and `9443` are open in the firewall.
2. Verify the server SSL certificate includes the server IP in its SANs. The certificate is valid for 1 year — regenerate with `generate-certs.sh` before it expires.
3. Check backend gRPC logs: `docker compose logs backend | grep -i grpc`

Sources: [deploy/onpremise/README.md:169-207]()

---

## Security Notes

| Concern | Recommendation |
|---|---|
| Default admin password | Change immediately after first login |
| Firewall | Expose only ports `80` and `9443` externally |
| SSL certificates | Valid for 1 year; renew with `generate-certs.sh` before expiry |
| Secrets in `.env` | Keep `.env` out of version control |
| Data backups | Schedule regular backups of `postgres_data` and `minio_data` volumes |