<!-- source: DeepWiki mcp.deepwiki.com · repo NousResearch/hermes-agent · page 7 Messaging Gateway · fetched 2026-10-30 -->

# Messaging Gateway

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/auxiliary_client.py](agent/auxiliary_client.py)
- [cli-config.yaml.example](cli-config.yaml.example)
- [cli.py](cli.py)
- [gateway/run.py](gateway/run.py)
- [gateway/run_active_work_verb.py](gateway/run_active_work_verb.py)
- [gateway/session.py](gateway/session.py)
- [gateway/slash_commands.py](gateway/slash_commands.py)
- [gateway/status.py](gateway/status.py)
- [hermes_cli/cli_commands_mixin.py](hermes_cli/cli_commands_mixin.py)
- [hermes_cli/commands.py](hermes_cli/commands.py)
- [hermes_cli/config.py](hermes_cli/config.py)
- [hermes_cli/config_defaults.py](hermes_cli/config_defaults.py)
- [hermes_cli/gateway.py](hermes_cli/gateway.py)
- [hermes_cli/gateway_lifecycle_guards.py](hermes_cli/gateway_lifecycle_guards.py)
- [hermes_cli/gateway_profile_lifecycle.py](hermes_cli/gateway_profile_lifecycle.py)
- [hermes_cli/main.py](hermes_cli/main.py)
- [hermes_cli/setup.py](hermes_cli/setup.py)
- [hermes_cli/subcommands/gateway.py](hermes_cli/subcommands/gateway.py)
- [hermes_state.py](hermes_state.py)
- [run_agent.py](run_agent.py)
- [tests/agent/test_auxiliary_client.py](tests/agent/test_auxiliary_client.py)
- [tests/gateway/fixtures/lifecycle_persistence_worker.py](tests/gateway/fixtures/lifecycle_persistence_worker.py)
- [tests/gateway/test_managed_worker_images.py](tests/gateway/test_managed_worker_images.py)
- [tests/gateway/test_multiplex_hot_serve_live.py](tests/gateway/test_multiplex_hot_serve_live.py)
- [tests/gateway/test_mutation_prepare_off_loop.py](tests/gateway/test_mutation_prepare_off_loop.py)
- [tests/gateway/test_retire_settles_waiters.py](tests/gateway/test_retire_settles_waiters.py)
- [tests/gateway/test_session.py](tests/gateway/test_session.py)
- [tests/gateway/test_status.py](tests/gateway/test_status.py)
- [tests/gateway/test_terminal_commit_crash.py](tests/gateway/test_terminal_commit_crash.py)
- [tests/gateway/test_worker_lifecycle_execution.py](tests/gateway/test_worker_lifecycle_execution.py)
- [tests/hermes_cli/test_commands.py](tests/hermes_cli/test_commands.py)
- [tests/hermes_cli/test_gateway.py](tests/hermes_cli/test_gateway.py)
- [tests/hermes_cli/test_gateway_external_supervisor.py](tests/hermes_cli/test_gateway_external_supervisor.py)
- [tests/hermes_cli/test_gateway_foreign_xdg_runtime.py](tests/hermes_cli/test_gateway_foreign_xdg_runtime.py)
- [tests/hermes_cli/test_gateway_host_stop_refusal.py](tests/hermes_cli/test_gateway_host_stop_refusal.py)
- [tests/hermes_cli/test_gateway_lifecycle_guards.py](tests/hermes_cli/test_gateway_lifecycle_guards.py)
- [tests/hermes_cli/test_gateway_linger.py](tests/hermes_cli/test_gateway_linger.py)
- [tests/hermes_cli/test_gateway_multiplex_lifecycle.py](tests/hermes_cli/test_gateway_multiplex_lifecycle.py)
- [tests/hermes_cli/test_gateway_scan_home_identity.py](tests/hermes_cli/test_gateway_scan_home_identity.py)
- [tests/hermes_cli/test_gateway_service.py](tests/hermes_cli/test_gateway_service.py)
- [tests/hermes_cli/test_subcommands_profile_gateway.py](tests/hermes_cli/test_subcommands_profile_gateway.py)
- [tests/test_session_daemon_reaper.py](tests/test_session_daemon_reaper.py)
- [ui-tui/src/__tests__/details.test.ts](ui-tui/src/__tests__/details.test.ts)
- [ui-tui/src/domain/details.ts](ui-tui/src/domain/details.ts)
- [website/docs/getting-started/quickstart.md](website/docs/getting-started/quickstart.md)
- [website/docs/integrations/providers.md](website/docs/integrations/providers.md)
- [website/docs/reference/cli-commands.md](website/docs/reference/cli-commands.md)
- [website/docs/reference/environment-variables.md](website/docs/reference/environment-variables.md)
- [website/docs/reference/slash-commands.md](website/docs/reference/slash-commands.md)
- [website/docs/user-guide/cli.md](website/docs/user-guide/cli.md)
- [website/docs/user-guide/configuration.md](website/docs/user-guide/configuration.md)
- [website/docs/user-guide/features/fallback-providers.md](website/docs/user-guide/features/fallback-providers.md)
- [website/docs/user-guide/messaging/index.md](website/docs/user-guide/messaging/index.md)
- [website/docs/user-guide/tui.md](website/docs/user-guide/tui.md)
- [website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/getting-started/quickstart.md](website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/getting-started/quickstart.md)
- [website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/reference/environment-variables.md](website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/reference/environment-variables.md)
- [website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/user-guide/configuration.md](website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/user-guide/configuration.md)
- [website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/user-guide/features/fallback-providers.md](website/i18n/zh-Hans/docusaurus-plugin-content-docs/current/user-guide/features/fallback-providers.md)

</details>



The Messaging Gateway is a core long-running background service that enables Hermes Agent to connect and interact with multiple messaging platforms concurrently [hermes_cli/gateway.py:1-4](). Serving as a multiplexing communication hub, it manages platform adapters that convert platform-specific protocols and events into a unified model, routes incoming messages to dedicated AI agent instances, and caches session state for efficient conversation persistence [hermes_cli/gateway.py:1-4](). The gateway plays a central role in maintaining high availability, resource efficiency, and seamless multi-platform user interactions.

Sources:
- [hermes_cli/gateway.py:1-4]()

---

## Architecture Overview

The gateway is architected around platform adapters, a core orchestration runner, and session-aware AI agents [hermes_cli/gateway.py:1-4]().

- **Platform Adapters**: These adapters implement platform-specific protocols and message formats, normalizing them into a common event interface consumed by the gateway core [gateway/platforms/base.py:1-6]().
- **GatewayRunner**: The central service controller responsible for lifecycle management of adapters, message routing to per-session AI agents, and enforcing resource policies like agent cache size and idle TTL eviction [gateway/run.py:50-52]().
- **Session-Aware AI Agents**: For each active chat session, a resident `AIAgent` instance is managed [run_agent.py:1-7](). These agents preserve conversation context, interact with LLM backends, and execute tools as needed.

The gateway is triggered from the CLI via the `hermes gateway` subcommand and can run as a foreground process or a system service on Linux (`systemd`) or macOS (`launchd`) [hermes_cli/gateway.py:3-4]().

### System Entity to Code Mapping

```mermaid
graph TD
    subgraph "Messaging Gateway"
        GR["GatewayRunner (gateway/run.py)"]
        GSC["GatewaySlashCommandsMixin (gateway/slash_commands.py)"]
        GSCN["GatewayStreamConsumer (gateway/stream_consumer.py)"]
        GSP["SessionPersistenceMixin (gateway/session_persistence.py)"]
        GSR["SessionRecoveryMixin (gateway/session_recovery.py)"]
        GSLC["SessionLifecycleMixin (gateway/session_lifecycle.py)"]
        GST["SessionTranscriptMixin (gateway/session_transcript.py)"]
        GSG["SessionGatewayMixin (hermes_state_gateway.py)"]
        GSL["GatewayAdapterLifecycleMixin (gateway/run_adapters.py)"]
        GSS["GatewayStartupMixin (gateway/run_startup.py)"]
        GSD["GatewayShutdownMixin (gateway/run_shutdown.py)"]
        GSN["GatewayNotificationsMixin (gateway/run_notifications.py)"]
    end

    subgraph "Platform Adapters"
        BC["BasePlatformAdapter (gateway/platforms/base.py)"]
        TG["TelegramAdapter (plugins/platforms/telegram/adapter.py)"]
        DC["DiscordAdapter (plugins/platforms/discord/adapter.py)"]
        SL["SlackAdapter (plugins/platforms/slack/adapter.py)"]
        WA["WhatsAppAdapter (plugins/platforms/whatsapp/adapter.py)"]
        MX["MatrixAdapter (plugins/platforms/matrix/adapter.py)"]
        FS["FeishuAdapter (plugins/platforms/feishu/adapter.py)"]
        SG["SignalAdapter (plugins/platforms/signal/adapter.py)"]
        PH["PhotonAdapter (plugins/platforms/photon/adapter.py)"]
        BZ["BuzzAdapter (plugins/platforms/buzz/adapter.py)"]
        WH["WebhookAdapter (plugins/platforms/webhook/adapter.py)"]
        API["APIAdapter (plugins/platforms/api/adapter.py)"]
        A2A["A2AAdapter (plugins/platforms/a2a/adapter.py)"]
        RL["RelayConnector (plugins/platforms/relay/adapter.py)"]
    end

    subgraph "Core Agent"
        AA["AIAgent (run_agent.py)"]
    end

    subgraph "Configuration & State"
        GCFG["GatewayConfig (gateway/config.py)"]
        SS["SessionStore (gateway/session.py)"]
        SD["SessionDB (hermes_state.py)"]
        CFG["Config (hermes_cli/config.py)"]
        DL["DeliveryLedger (gateway/delivery_ledger.py)"]
        RTS["_RuntimeStatusWriter (gateway/status.py)"]
    end

    subgraph "CLI & UI"
        GW_CLI["GatewayCliCommand (hermes_cli/subcommands/gateway.py)"]
        CLI_MAIN["hermes_cli.main"]
        WEB_GW["_probe_gateway_health (hermes_cli/web_server_gateway.py)"]
    end

    CLI_MAIN -- "hermes gateway run" --> GR
    GR -- "Manages" --> BC
    BC <|-- TG
    BC <|-- DC
    BC <|-- SL
    BC <|-- WA
    BC <|-- MX
    BC <|-- FS
    BC <|-- SG
    BC <|-- PH
    BC <|-- BZ
    BC <|-- WH
    BC <|-- API
    BC <|-- A2A
    BC <|-- RL

    GR -- "Routes messages to" --> AA
    AA -- "Persists state via" --> SD
    GR -- "Uses" --> SS
    SS -- "Backed by" --> SD
    GR -- "Loads config from" --> GCFG
    GCFG -- "Derived from" --> CFG

    GR -- "Handles slash commands via" --> GSC
    GR -- "Delivers streams via" --> GSCN

    SS -- "Mixins" --> GSP
    SS -- "Mixins" --> GSR
    SS -- "Mixins" --> GSLC
    SS -- "Mixins" --> GST
    SD -- "Mixins" --> GSG

    GR -- "Adapter lifecycle" --> GSL
    GR -- "Startup logic" --> GSS
    GR -- "Shutdown logic" --> GSD
    GR -- "Notifications" --> GSN
    GR -- "Writes runtime status via" --> RTS
    GR -- "Manages message delivery via" --> DL

    GW_CLI -- "Interacts with" --> GR
    WEB_GW -- "Probes" --> GR
```

Sources:
- [hermes_cli/gateway.py:1-4]()
- [gateway/platforms/base.py:1-6]()
- [gateway/run.py:50-52]()
- [run_agent.py:1-7]()
- [hermes_cli/gateway.py:3-4]()
- [gateway/slash_commands.py:1-14]()
- [gateway/session.py:1-22]()
- [hermes_state.py:1-74]()
- [gateway/config.py:1-15]()
- [gateway/run_adapters.py:70-72]()
- [gateway/run_startup.py:63-65]()
- [gateway/run_shutdown.py:172-173]()
- [gateway/run_notifications.py:125-127]()
- [gateway/delivery_ledger.py:1-11]()
- [gateway/status.py:56-75]()
- [hermes_cli/web_server_gateway.py:39-45]()

---

## Gateway Architecture

The gateway’s core is the `GatewayRunner` class defined in `gateway/run.py`, which orchestrates the lifecycle of all configured platform adapters, manages session-based routing of messages, and coordinates instance caching of per-session AI agents [gateway/run.py:3-4](). The `GatewayRunner` is composed of several mixins, including `GatewayStartupMixin` [gateway/run_startup.py:63-65](), `GatewayAdapterLifecycleMixin` [gateway/run_adapters.py:70-72](), `GatewayShutdownMixin` [gateway/run_shutdown.py:172-173](), and `GatewayNotificationsMixin` [gateway/run_notifications.py:125-127]().

- **Lifecycle Management**: The `GatewayRunner` starts, monitors, and stops platform adapters gracefully through its `run_*` submodules. It handles signals like `SIGTERM` for graceful shutdown and manages reconnect logic for platforms [gateway/run_shutdown.py:47-67](). The `GatewayAdapterLifecycleMixin` handles the connection and disconnection of adapters, including error recovery and a reconnect watcher [gateway/run_adapters.py:70-72]().
- **Message Routing**: Incoming messages are routed to the appropriate `AIAgent` instance based on session keys derived from platform and chat identifiers [gateway/session.py:63-67]().
- **Session Caching & Expiry**: The gateway maintains a bounded LRU cache (`_AGENT_CACHE_MAX_SIZE`) of live `AIAgent` instances to reduce startup latency [gateway/run.py:50-52](). Agents idle longer than `_AGENT_CACHE_IDLE_TTL_SECS` are evicted to save memory [gateway/run.py:50-52]().
- **Service Management**: The `GatewayRunner` integrates with a cron scheduler for background tasks and ensures proper service health and supervision [hermes_cli/config_defaults.py:86-93](). The `hermes gateway` CLI command provides subcommands like `run`, `start`, `stop`, `restart`, and `status` for managing the gateway service [hermes_cli/gateway.py:3-4]().
- **Profile Multiplexing**: Supports serving multiple Hermes profiles simultaneously, with allowlists to control access [gateway/config.py:46-88]().

For detailed technical design and session expiry mechanisms, see [Gateway Architecture](#7.1).

Sources:
- [gateway/run.py:3-4]()
- [gateway/run_startup.py:63-65]()
- [gateway/run_adapters.py:70-72]()
- [gateway/run_shutdown.py:172-173]()
- [gateway/run_notifications.py:125-127]()
- [gateway/run_shutdown.py:47-67]()
- [gateway/session.py:63-67]()
- [gateway/run.py:50-52]()
- [hermes_cli/config_defaults.py:86-93]()
- [hermes_cli/gateway.py:3-4]()
- [gateway/config.py:46-88]()

---

## Platform Adapters

Each messaging platform is supported via a dedicated adapter class inheriting from `BasePlatformAdapter` in `gateway/platforms/base.py` [gateway/platforms/base.py:1-19]().

- **Unified Interface**: The `BasePlatformAdapter` defines methods for sending text, audio, and media content, while handling platform-specific metadata like `thread_id` or `reply_to_message_id` [gateway/platforms/base.py:101-127]().
- **Stream Consumer Delivery**: Adapters are responsible for delivering messages from their respective platforms to the gateway's stream consumer, which then processes them for the AI agent [gateway/platforms/base.py:1-19]().
- **Media Handling**: The adapters distinguish between standard audio and platform voice notes (e.g., transcoding to Ogg/Opus for Telegram voice bubbles) [gateway/platforms/base.py:51-72]().
- **Cross-Platform Coverage**: The codebase includes implementations for a wide array of platforms, such as Telegram, Discord, Slack, WhatsApp, Matrix, Feishu, Signal, Photon, Buzz, webhooks, an API server, A2A, and a relay connector [hermes_cli/web_server_gateway.py:67-75]().

For the complete adapter contract and specific implementations, refer to [Platform Adapters](#7.2).

Sources:
- [gateway/platforms/base.py:1-19]()
- [gateway/platforms/base.py:51-72]()
- [gateway/platforms/base.py:101-127]()
- [hermes_cli/web_server_gateway.py:67-75]()

---

## Session and Media Management

The gateway manages how conversational state and rich media are delivered to users across channels:

- **Session Storage**: Conversation history and metadata are persisted in an SQLite `SessionDB` [hermes_state.py:1-7](). The `SessionSource` dataclass captures the origin of each message, including platform, chat ID, user ID, and thread ID [gateway/session.py:63-99]().
- **Media Caching**: The gateway handles caching and routing of media content, ensuring it's delivered efficiently and in the correct format for each platform [gateway/platforms/base.py:39-48]().
- **Delivery Ledger**: A delivery ledger (`gateway/delivery_ledger.py`) tracks message status and ensures reliable delivery across potentially unreliable messaging platforms, handling redelivery policies, flood control, and retry mechanisms [gateway/delivery_ledger.py:1-11]().
- **Interrupt Handling**: The gateway supports interrupting ongoing agent turns, allowing users to regain control or redirect the conversation [agent/interrupt_compat.py:39-40]().
- **Message Formatting**: Messages are formatted appropriately for each platform, including handling of markdown, rich text, and attachments.

For thorough discussion of session lifecycle and media handling, see [Session and Media Management](#7.3).

Sources:
- [hermes_state.py:1-7]()
- [gateway/session.py:63-99]()
- [gateway/platforms/base.py:39-48]()
- [gateway/delivery_ledger.py:1-11]()
- [agent/interrupt_compat.py:39-40]()

---

## Security and Pairing

Security is central to protecting user data and system integrity across gateway channels:

- **Allowlist Filtering**: The gateway can be configured with allowlists to restrict which users or channels can interact with the agent [gateway/config.py:46-88]().
- **Authz Mixin**: An authorization mixin (`AuthzMixin`) provides a framework for implementing fine-grained access control policies.
- **Channel Directory**: A channel directory helps manage and discover authorized communication channels.
- **DM Pairing System**: A secure pairing system ensures direct messages are routed to the correct authorized agent profile, preventing impersonation and unauthorized access.
- **Gateway Security Model**: The overall security model emphasizes least privilege, secret redaction from logs, and process isolation [hermes_cli/config.py:140-149]().

Detailed security design and pairing mechanisms are described in [Security and Pairing](#7.4).

Sources:
- [gateway/config.py:46-88]()
- [hermes_cli/config.py:140-149]()

---

## Hosted Rooms and Group Chat

The gateway provides a gateway-hosted Bot Mode rooms subsystem designed for multi-agent or collaborative room environments. This subsystem allows the agent to participate in and manage group conversations across various platforms.

- **Durable Room Identity**: Each hosted room maintains a durable identity, ensuring consistent state and history across sessions.
- **Append-Only Event Log**: Conversations within hosted rooms are recorded in an append-only event log, providing an immutable record of interactions.
- **Replicas**: The system supports replicas for high availability and fault tolerance.
- **Peer HTTP**: Peer-to-peer HTTP communication facilitates coordination between different instances of the discussion driver.
- **Discussion Driver**: A discussion driver orchestrates the flow of conversation within hosted rooms, managing turns and agent interactions.
- **Execution/Policy Checkpoints**: The system enforces execution and policy checkpoints, allowing for controlled progression and adherence to predefined rules.

For detailed design and implementation of hosted rooms, see [Hosted Rooms and Group Chat](#7.5).

Sources:
- [hermes_cli/gateway.py:1-4]()

---

