<!-- source: DeepWiki mcp.deepwiki.com · repo openclaw/openclaw · page 2 Gateway · fetched 2026-10-27 -->

# Gateway

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/cli/daemon.md](docs/cli/daemon.md)
- [docs/cli/dashboard.md](docs/cli/dashboard.md)
- [docs/cli/gateway.md](docs/cli/gateway.md)
- [docs/gateway/configuration.md](docs/gateway/configuration.md)
- [extensions/codex/index.test.ts](extensions/codex/index.test.ts)
- [extensions/codex/index.ts](extensions/codex/index.ts)
- [extensions/codex/src/command-plugins-management.test.ts](extensions/codex/src/command-plugins-management.test.ts)
- [extensions/codex/src/command-plugins-management.ts](extensions/codex/src/command-plugins-management.ts)
- [packages/normalization-core/src/error-coercion.test.ts](packages/normalization-core/src/error-coercion.test.ts)
- [packages/normalization-core/src/error-coercion.ts](packages/normalization-core/src/error-coercion.ts)
- [src/agents/cli-runner/reseed-envelope.test.ts](src/agents/cli-runner/reseed-envelope.test.ts)
- [src/agents/embedded-agent-runner/run/idle-timeout-breaker.test.ts](src/agents/embedded-agent-runner/run/idle-timeout-breaker.test.ts)
- [src/agents/live-model-errors.test.ts](src/agents/live-model-errors.test.ts)
- [src/agents/mcp-connection-resolver.test.ts](src/agents/mcp-connection-resolver.test.ts)
- [src/agents/provider-local-service.env-case.test.ts](src/agents/provider-local-service.env-case.test.ts)
- [src/agents/provider-local-service.shutdown.test.ts](src/agents/provider-local-service.shutdown.test.ts)
- [src/agents/provider-local-service.test.ts](src/agents/provider-local-service.test.ts)
- [src/agents/provider-runtime-lifecycle.ts](src/agents/provider-runtime-lifecycle.ts)
- [src/agents/provider-transport-dispatcher-pool.ts](src/agents/provider-transport-dispatcher-pool.ts)
- [src/cli/daemon-cli/probe.reachability.test.ts](src/cli/daemon-cli/probe.reachability.test.ts)
- [src/cli/daemon-cli/probe.test.ts](src/cli/daemon-cli/probe.test.ts)
- [src/cli/daemon-cli/probe.ts](src/cli/daemon-cli/probe.ts)
- [src/cli/daemon-cli/register-service-commands.test.ts](src/cli/daemon-cli/register-service-commands.test.ts)
- [src/cli/daemon-cli/register-service-commands.ts](src/cli/daemon-cli/register-service-commands.ts)
- [src/cli/daemon-cli/types.ts](src/cli/daemon-cli/types.ts)
- [src/cli/dns-cli.test.ts](src/cli/dns-cli.test.ts)
- [src/cli/dns-cli.ts](src/cli/dns-cli.ts)
- [src/cli/gateway-cli.coverage.test.ts](src/cli/gateway-cli.coverage.test.ts)
- [src/cli/gateway-cli/lifecycle.runtime.ts](src/cli/gateway-cli/lifecycle.runtime.ts)
- [src/cli/gateway-cli/register.option-collisions.test.ts](src/cli/gateway-cli/register.option-collisions.test.ts)
- [src/cli/gateway-cli/register.ts](src/cli/gateway-cli/register.ts)
- [src/cli/gateway-cli/run-loop.test.ts](src/cli/gateway-cli/run-loop.test.ts)
- [src/cli/gateway-cli/run-loop.ts](src/cli/gateway-cli/run-loop.ts)
- [src/cli/gateway-cli/suspend-cli.test.ts](src/cli/gateway-cli/suspend-cli.test.ts)
- [src/cli/gateway-cli/suspend-cli.ts](src/cli/gateway-cli/suspend-cli.ts)
- [src/cli/program/routed-command-definitions.ts](src/cli/program/routed-command-definitions.ts)
- [src/cli/runtime-cleanup.ts](src/cli/runtime-cleanup.ts)
- [src/commands/gateway-health-auth-diagnostic.ts](src/commands/gateway-health-auth-diagnostic.ts)
- [src/commands/gateway-readiness.test.ts](src/commands/gateway-readiness.test.ts)
- [src/commands/gateway-readiness.ts](src/commands/gateway-readiness.ts)
- [src/commands/gateway-status.test.ts](src/commands/gateway-status.test.ts)
- [src/commands/gateway-status.ts](src/commands/gateway-status.ts)
- [src/commands/gateway-status/helpers.ts](src/commands/gateway-status/helpers.ts)
- [src/commands/gateway-status/probe-run.ts](src/commands/gateway-status/probe-run.ts)
- [src/commands/onboard-interactive.test.ts](src/commands/onboard-interactive.test.ts)
- [src/config/runtime-write-application.ts](src/config/runtime-write-application.ts)
- [src/gateway/auth-rate-limit.ts](src/gateway/auth-rate-limit.ts)
- [src/gateway/call.test.ts](src/gateway/call.test.ts)
- [src/gateway/call.ts](src/gateway/call.ts)
- [src/gateway/client.ts](src/gateway/client.ts)
- [src/gateway/config-diff.ts](src/gateway/config-diff.ts)
- [src/gateway/config-reload-plan.ts](src/gateway/config-reload-plan.ts)
- [src/gateway/config-reload.test.ts](src/gateway/config-reload.test.ts)
- [src/gateway/config-reload.ts](src/gateway/config-reload.ts)
- [src/gateway/connection-details.ts](src/gateway/connection-details.ts)
- [src/gateway/control-ui-http-utils.ts](src/gateway/control-ui-http-utils.ts)
- [src/gateway/control-ui-routing.test.ts](src/gateway/control-ui-routing.test.ts)
- [src/gateway/control-ui-routing.ts](src/gateway/control-ui-routing.ts)
- [src/gateway/gateway-http-route-contracts.ts](src/gateway/gateway-http-route-contracts.ts)
- [src/gateway/http-media-range.ts](src/gateway/http-media-range.ts)
- [src/gateway/local-request-context.test.ts](src/gateway/local-request-context.test.ts)
- [src/gateway/local-request-context.ts](src/gateway/local-request-context.ts)
- [src/gateway/probe.test.ts](src/gateway/probe.test.ts)
- [src/gateway/probe.ts](src/gateway/probe.ts)
- [src/gateway/server-close.test.ts](src/gateway/server-close.test.ts)
- [src/gateway/server-close.ts](src/gateway/server-close.ts)
- [src/gateway/server-core-runtime.ts](src/gateway/server-core-runtime.ts)
- [src/gateway/server-cron-lazy.test.ts](src/gateway/server-cron-lazy.test.ts)
- [src/gateway/server-cron-lazy.ts](src/gateway/server-cron-lazy.ts)
- [src/gateway/server-http.openai-compat.test.ts](src/gateway/server-http.openai-compat.test.ts)
- [src/gateway/server-http.probe.test.ts](src/gateway/server-http.probe.test.ts)
- [src/gateway/server-http.ts](src/gateway/server-http.ts)
- [src/gateway/server-kernel-request-runtime.ts](src/gateway/server-kernel-request-runtime.ts)
- [src/gateway/server-kernel.test.ts](src/gateway/server-kernel.test.ts)
- [src/gateway/server-kernel.ts](src/gateway/server-kernel.ts)
- [src/gateway/server-lifecycle.ts](src/gateway/server-lifecycle.ts)
- [src/gateway/server-methods/config-write-flow.ts](src/gateway/server-methods/config-write-flow.ts)
- [src/gateway/server-methods/config.test.ts](src/gateway/server-methods/config.test.ts)
- [src/gateway/server-methods/config.ts](src/gateway/server-methods/config.ts)
- [src/gateway/server-methods/models-auth-status.types.ts](src/gateway/server-methods/models-auth-status.types.ts)
- [src/gateway/server-methods/shared-types.ts](src/gateway/server-methods/shared-types.ts)
- [src/gateway/server-reload-contracts.ts](src/gateway/server-reload-contracts.ts)
- [src/gateway/server-reload-handlers.hot-reload-status.test.ts](src/gateway/server-reload-handlers.hot-reload-status.test.ts)
- [src/gateway/server-reload-handlers.test.ts](src/gateway/server-reload-handlers.test.ts)
- [src/gateway/server-reload-hot.ts](src/gateway/server-reload-hot.ts)
- [src/gateway/server-reload-managed.ts](src/gateway/server-reload-managed.ts)
- [src/gateway/server-request-context.test.ts](src/gateway/server-request-context.test.ts)
- [src/gateway/server-request-context.ts](src/gateway/server-request-context.ts)
- [src/gateway/server-runtime-config.ts](src/gateway/server-runtime-config.ts)
- [src/gateway/server-runtime-state-prepare.ts](src/gateway/server-runtime-state-prepare.ts)
- [src/gateway/server-runtime-state.ts](src/gateway/server-runtime-state.ts)
- [src/gateway/server-start.ts](src/gateway/server-start.ts)
- [src/gateway/server-startup-finish.ts](src/gateway/server-startup-finish.ts)
- [src/gateway/server-startup-post-attach.test.ts](src/gateway/server-startup-post-attach.test.ts)
- [src/gateway/server-startup-post-attach.ts](src/gateway/server-startup-post-attach.ts)
- [src/gateway/server.channels-start-outcomes.test.ts](src/gateway/server.channels-start-outcomes.test.ts)
- [src/gateway/server/public-worker-ingress-context.ts](src/gateway/server/public-worker-ingress-context.ts)
- [src/gateway/server/ws-connection-diagnostics.ts](src/gateway/server/ws-connection-diagnostics.ts)
- [src/gateway/system-ca-warmup.test.ts](src/gateway/system-ca-warmup.test.ts)
- [src/gateway/system-ca-warmup.ts](src/gateway/system-ca-warmup.ts)
- [src/infra/net/pinned-dispatcher-pool.test.ts](src/infra/net/pinned-dispatcher-pool.test.ts)
- [src/infra/net/pinned-dispatcher-pool.ts](src/infra/net/pinned-dispatcher-pool.ts)
- [src/infra/sqlite-user-version.ts](src/infra/sqlite-user-version.ts)
- [src/infra/widearea-dns.boundary.test.ts](src/infra/widearea-dns.boundary.test.ts)
- [src/infra/widearea-dns.test.ts](src/infra/widearea-dns.test.ts)
- [src/infra/widearea-dns.ts](src/infra/widearea-dns.ts)
- [src/plugins/services.replacement.test.ts](src/plugins/services.replacement.test.ts)
- [src/plugins/services.test.ts](src/plugins/services.test.ts)
- [src/plugins/services.ts](src/plugins/services.ts)
- [src/process/child-process-tree.ts](src/process/child-process-tree.ts)

</details>



The Gateway is the central control plane for OpenClaw, responsible for managing WebSocket connections, dispatching RPC methods, coordinating messaging channels, orchestrating agent runs, and maintaining system state. It runs as a single multiplexed process serving protocol clients (CLI, native apps, Control UI) and channel providers simultaneously. [src/gateway/server-runtime-state-prepare.ts:68-84]()

For details on specific Gateway subsystems, see:
- **[WebSocket Protocol & RPC](#2.1)** — Document the Gateway protocol v3, including `ConnectFrame`, `RequestFrame`, `ResponseFrame`, and `EventFrame`. Cover `TypeBox` as the schema source of truth and the steering queue for active-run message delivery. [packages/gateway-protocol/src/schema/frames.ts:9-13]()
- **[Authentication & Authorization](#2.2)** — Explain Gateway authentication modes (token/password/none), scope-based authorization (`READ`/`WRITE`/`ADMIN`/`PAIRING`/`APPROVALS`), and rate limiting. [src/gateway/server-methods/shared-types.ts:91-96](), [src/gateway/server-runtime-state-prepare.ts:46-55]()
- **[Configuration System](#2.3)** — Overview of `openclaw.json`, `models.json`, `auth-profiles.json`, configuration loading, Zod schema validation, and migrations. [src/gateway/server-runtime-state-prepare.ts:6-7](), [docs/gateway/configuration.md:10-22]()
- **[Session & State Management](#2.4)** — Document session scoping (per-channel-peer/shared/global), session storage in JSONL files, state directory organization, and session lifecycle. [src/gateway/server-startup-post-attach.ts:29-29](), [src/gateway/server-runtime-state-prepare.ts:16-17]()
- **[Multi-Agent Routing](#2.5)** — Explain agent bindings, how channels route to specific agents, isolated workspaces, and agent-specific auth profiles. [src/gateway/server-core-runtime.ts:2-6]()
- **[Service Lifecycle & Diagnostics](#2.6)** — Cover Gateway daemon management (launchd/systemd), health checks, `status` command, and `doctor` command for diagnostics and auto-repair. [src/gateway/server-startup-post-attach.ts:38-42](), [src/gateway/server-core-runtime.ts:32-36]()
- **[Control UI & WebChat](#2.7)** — Document the browser-based Control UI served by the Gateway, including the chat interface, settings panels, and session management views. [src/gateway/server-http.ts:25-36]()
- **[HTTP APIs](#2.8)** — Document the Gateway's HTTP surfaces: OpenAI-compatible endpoints, `/tools/invoke`, and the MCP bridge (`openclaw mcp serve`). [src/gateway/server-http.ts:113-120]()
- **[Client SDK](#2.9)** — Document the `@openclaw/sdk` TypeScript client package for programmatic access to the Gateway via `GatewayClientTransport`. [src/gateway/server-methods/shared-types.ts:77-89]()
- **[Terminal UI (TUI)](#2.10)** — Document the terminal-based chat interface (`openclaw tui` / `openclaw chat`), including Gateway-backed mode and session navigation. [src/gateway/server-methods/shared-types.ts:60-61]()

---

## Gateway Role in the System

The Gateway acts as the single source of truth for:
- **Protocol connections**: WebSocket clients connect to the Gateway for RPC and events using a versioned protocol. [src/gateway/call.ts:18-21](), [src/gateway/server-http.ts:133-145]()
- **Agent orchestration**: The Gateway invokes agent runs and tracks their lifecycle across restarts, handling recovery for orphaned sessions via `markStartupOrphanedMainSessionsForRecovery`. [src/gateway/server-startup-post-attach.ts:66-72]()
- **Transcript Management**: Manages session history and lifecycle persistence via session state events. [src/gateway/server-startup-post-attach.ts:29-29]()
- **Sidecar Coordination**: Orchestrates background tasks like cron, maintenance, and health monitoring. [src/gateway/server-core-runtime.ts:158-160](), [src/gateway/server-lifecycle.ts:21-23]()

### Gateway Architecture Overview

```mermaid
graph TB
    subgraph "Protocol Clients [packages/gateway-protocol]"
        [GatewayClient] --> [ConnectFrame]
        [GatewayClient] --> [RequestFrame]
    end
    
    subgraph "Gateway Kernel [src/gateway/server-runtime-state-prepare.ts]"
        [prepareGatewayKernelState] --> [GatewayMethodRegistry]
        [GatewayMethodRegistry] --> [GatewayRequestContext]
    end
    
    subgraph "Logic & Services [src/gateway/]"
        [GatewayRequestContext] --> [ChannelManager]
        [GatewayRequestContext] --> [GatewayCronServiceContract]
        [GatewayRequestContext] --> [GatewayInstanceRuntime]
    end
    
    subgraph "Recovery & Lifecycle [src/gateway/server-startup-post-attach.ts]"
        [GatewayInstanceRuntime] --> [GatewayRecoveryRuntime]
        [GatewayRecoveryRuntime] --> [markStartupOrphanedMainSessionsForRecovery]
    end
```

Sources: [src/gateway/server-methods/shared-types.ts:79-89](), [src/gateway/server-runtime-state-prepare.ts:68-84](), [src/gateway/server-startup-post-attach.ts:40-42]()

---

## Core Responsibilities

### 1. WebSocket Protocol & RPC Dispatch
The Gateway implements a versioned WebSocket protocol. It projects agent events into chat/session subscriber streams for live UI updates. [src/gateway/server-http.ts:1-2](), [src/gateway/server-lifecycle.ts:96-102]()

- **Client Transport**: The `GatewayClient` manages the binding of HTTP and WebSocket listeners. [src/gateway/call.ts:59-65]()
- **Method Resolution**: Methods are registered via `createGatewayMethodRegistry` and classified by scope (e.g., `ADMIN_SCOPE`, `WRITE_SCOPE`) to ensure least-privilege access. [src/gateway/server-core-runtime.ts:14-22](), [src/gateway/call.ts:90-96]()
- **Event Fanout**: The Gateway broadcasts events (e.g., `health`, `presence`) to connected clients based on session interest. [src/gateway/server-core-runtime.ts:32-37]()

Sources: [src/gateway/server-core-runtime.ts:14-22](), [src/gateway/server-lifecycle.ts:96-102](), [src/gateway/call.ts:59-65]()

### 2. Channel and Account Management
The Gateway manages the lifecycle of messaging channels (Telegram, Discord, etc.) and their specific accounts. [src/gateway/server-core-runtime.ts:2-6]()

- **Lifecycle Management**: The `channelManager` (from `createChannelManager`) starts, stops, and restarts plugin channel account runtimes. [src/gateway/server-lifecycle.ts:67-67](), [src/gateway/server-reload-handlers.ts:9]()
- **Account Snapshots**: Maintains `ChannelRuntimeSnapshot` state, including connectivity status and diagnostic errors. [src/gateway/server-methods/shared-types.ts:42-46]()
- **Thaw & Restart**: Handles graceful restarts of running channel accounts via `restartRunningChannelAccounts`. [src/gateway/server-core-runtime.ts:11-11]()

Sources: [src/gateway/server-core-runtime.ts:2-11](), [src/gateway/server-lifecycle.ts:67-67]()

### 3. Service Lifecycle & Maintenance
The Gateway coordinates sidecar services and manages its own maintenance lifecycle through work admission and startup tasks. [src/gateway/server-startup-post-attach.ts:1-2]()

- **Startup Sidecars**: Manages the transition from startup to a "ready" state, initializing model prewarming (`scheduleGatewayHandlerPrewarm`) and update checks. [src/gateway/server-startup-post-attach.ts:45-52]()
- **Work Admission**: Critical operations are protected by `GatewayWorkAdmission` (e.g., `tryBeginGatewayRootWorkAdmission`) to prevent race conditions during restarts or draining. [src/gateway/server-startup-post-attach.ts:25-28](), [src/gateway/server-reload-handlers.ts:9]()
- **Cron Coordination**: Manages scheduled tasks through `GatewayCronServiceContract` and reconciliation loops. [src/gateway/server-lifecycle.ts:21-22]()

Sources: [src/gateway/server-startup-post-attach.ts:1-170](), [src/gateway/server-reload-handlers.ts:9]()

---

## Gateway Boundaries and Safety

The Gateway enforces security and stability through several layers:
- **Credential Protection**: Plugin runtime claims and secrets are isolated via `GatewayPluginRuntimeClaim`. [src/gateway/server-plugin-runtime-generation.ts:27-29]()
- **Restart Sentinel**: Detects and handles orphaned sessions using a persistent sentinel file (`hasRestartSentinel`). [src/gateway/server-startup-post-attach.ts:11-15]()
- **Rate Limiting**: Throttles authentication attempts via `AuthRateLimiter` to protect against brute force, including specific loopback exemptions for non-browser clients. [src/gateway/server-runtime-state-prepare.ts:46-55]()

```mermaid
graph LR
    subgraph "Untrusted Space"
        [External_Client] -- "WebSocket / HTTP" --> [createGatewayHttpServer]
    end
    
    subgraph "Gateway Guard [src/gateway/server-runtime-state-prepare.ts]"
        [createGatewayHttpServer] --> [AuthRateLimiter]
        [AuthRateLimiter] --> [GatewayMethodRegistry]
    end
    
    subgraph "Trusted Runtime"
        [GatewayMethodRegistry] --> [ChannelManager]
        [GatewayMethodRegistry] --> [PluginRegistry]
    end
```

Sources: [src/gateway/server-runtime-state-prepare.ts:46-55](), [src/gateway/server-http.ts:150-154](), [src/gateway/server-core-runtime.ts:14-22]()

---

## Summary

The Gateway is the orchestration layer for OpenClaw. It:
- Implements the WebSocket protocol for all clients. [src/gateway/call.ts:59-65]()
- Manages the lifecycle of messaging channels and accounts. [src/gateway/server-core-runtime.ts:2-11]()
- Handles chat history, session state, and restart recovery. [src/gateway/server-startup-post-attach.ts:66-72]()
- Coordinates agent runs and schedules sidecar services like maintenance and health monitors. [src/gateway/server-lifecycle.ts:21-23]()

For operational details, see [Service Lifecycle & Diagnostics](#2.6).

---

