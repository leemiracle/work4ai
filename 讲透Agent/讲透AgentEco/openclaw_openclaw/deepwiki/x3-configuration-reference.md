<!-- source: DeepWiki mcp.deepwiki.com · repo openclaw/openclaw · extra page Configuration Reference · fetched 2026-10-27 -->

# Configuration Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/.generated/config-baseline.counts.json](docs/.generated/config-baseline.counts.json)
- [docs/.generated/config-baseline.sha256](docs/.generated/config-baseline.sha256)
- [docs/cli/config.md](docs/cli/config.md)
- [docs/gateway/config-agents.md](docs/gateway/config-agents.md)
- [docs/gateway/config-tools.md](docs/gateway/config-tools.md)
- [docs/gateway/configuration-reference.md](docs/gateway/configuration-reference.md)
- [docs/help/environment.md](docs/help/environment.md)
- [docs/reference/session-management-compaction.md](docs/reference/session-management-compaction.md)
- [docs/security/network-proxy.md](docs/security/network-proxy.md)
- [extensions/qa-lab/src/hook-agent-account-routing.e2e.test.ts](extensions/qa-lab/src/hook-agent-account-routing.e2e.test.ts)
- [extensions/qa-lab/src/live-transports/matrix/substrate/harness.runtime-internals.ts](extensions/qa-lab/src/live-transports/matrix/substrate/harness.runtime-internals.ts)
- [extensions/qa-lab/src/live-transports/matrix/substrate/harness.runtime.test.ts](extensions/qa-lab/src/live-transports/matrix/substrate/harness.runtime.test.ts)
- [src/agents/code-mode.config.test.ts](src/agents/code-mode.config.test.ts)
- [src/cli/config-cli-input.test.ts](src/cli/config-cli-input.test.ts)
- [src/cli/config-cli-input.ts](src/cli/config-cli-input.ts)
- [src/cli/config-cli-path.test.ts](src/cli/config-cli-path.test.ts)
- [src/cli/config-cli-path.ts](src/cli/config-cli-path.ts)
- [src/cli/config-cli-runner.ts](src/cli/config-cli-runner.ts)
- [src/cli/config-cli-validation.ts](src/cli/config-cli-validation.ts)
- [src/cli/config-cli.integration.test-harness.ts](src/cli/config-cli.integration.test-harness.ts)
- [src/cli/config-cli.integration.test.ts](src/cli/config-cli.integration.test.ts)
- [src/cli/config-cli.roster.integration.test.ts](src/cli/config-cli.roster.integration.test.ts)
- [src/cli/config-cli.secrets.integration.test.ts](src/cli/config-cli.secrets.integration.test.ts)
- [src/cli/config-cli.test.ts](src/cli/config-cli.test.ts)
- [src/cli/config-cli.ts](src/cli/config-cli.ts)
- [src/cli/config-model-validation.runtime.test.ts](src/cli/config-model-validation.runtime.test.ts)
- [src/cli/config-model-validation.ts](src/cli/config-model-validation.ts)
- [src/cli/config-set-dryrun.ts](src/cli/config-set-dryrun.ts)
- [src/cli/config-set-input.test.ts](src/cli/config-set-input.test.ts)
- [src/cli/config-set-input.ts](src/cli/config-set-input.ts)
- [src/cli/gateway-cli/pre-bootstrap.ts](src/cli/gateway-cli/pre-bootstrap.ts)
- [src/commands/doctor-startup-migration-refusal.ts](src/commands/doctor-startup-migration-refusal.ts)
- [src/config/__snapshots__/schema.help.quality.test.ts.snap](src/config/__snapshots__/schema.help.quality.test.ts.snap)
- [src/config/bundled-channel-config-metadata.generated.ts](src/config/bundled-channel-config-metadata.generated.ts)
- [src/config/io.read-helpers.ts](src/config/io.read-helpers.ts)
- [src/config/io.write-topology.ts](src/config/io.write-topology.ts)
- [src/config/io.write.ts](src/config/io.write.ts)
- [src/config/legacy.roster.ts](src/config/legacy.roster.ts)
- [src/config/schema.help.agents.ts](src/config/schema.help.agents.ts)
- [src/config/schema.help.automation.ts](src/config/schema.help.automation.ts)
- [src/config/schema.help.core.ts](src/config/schema.help.core.ts)
- [src/config/schema.help.quality.test-fixtures.ts](src/config/schema.help.quality.test-fixtures.ts)
- [src/config/schema.help.runtime.ts](src/config/schema.help.runtime.ts)
- [src/config/schema.hints.test.ts](src/config/schema.hints.test.ts)
- [src/config/schema.hints.ts](src/config/schema.hints.ts)
- [src/config/schema.labels.ts](src/config/schema.labels.ts)
- [src/config/schema.tiers.ts](src/config/schema.tiers.ts)
- [src/config/types.agent-defaults.ts](src/config/types.agent-defaults.ts)
- [src/config/types.base.ts](src/config/types.base.ts)
- [src/config/types.gateway.ts](src/config/types.gateway.ts)
- [src/config/types.openclaw.ts](src/config/types.openclaw.ts)
- [src/config/types.secrets.test.ts](src/config/types.secrets.test.ts)
- [src/config/types.tools.ts](src/config/types.tools.ts)
- [src/config/zod-schema.agent-defaults.test.ts](src/config/zod-schema.agent-defaults.test.ts)
- [src/config/zod-schema.agent-defaults.ts](src/config/zod-schema.agent-defaults.ts)
- [src/config/zod-schema.gateway-auth.test.ts](src/config/zod-schema.gateway-auth.test.ts)
- [src/config/zod-schema.gateway.ts](src/config/zod-schema.gateway.ts)
- [src/config/zod-schema.root-shape.ts](src/config/zod-schema.root-shape.ts)
- [src/daemon/service-managed-env.ts](src/daemon/service-managed-env.ts)
- [src/infra/dotenv-global.ts](src/infra/dotenv-global.ts)
- [src/infra/shell-env.test.ts](src/infra/shell-env.test.ts)
- [src/infra/shell-env.ts](src/infra/shell-env.ts)
- [ui/src/pages/labs/labs-registry.ts](ui/src/pages/labs/labs-registry.ts)

</details>



This document provides a comprehensive technical reference for all configuration keys available in `~/.openclaw/openclaw.json`. It covers types, defaults, validation rules, and subsystem effects.

OpenClaw uses a centralized configuration system built on **JSON5** and **Zod**, providing strict type safety while allowing comments and trailing commas in the configuration file [docs/gateway/configuration-reference.md:10-12]().

## Configuration Architecture

The configuration system is organized into a hierarchical structure that separates infrastructure, runtime, and agent-specific settings.

### Top-Level Organization

Title: "OpenClaw Configuration Subsystems"
```mermaid
graph TB
    subgraph Root["Root OpenClawConfig [src/config/types.openclaw.ts]"]
        [ConfigObject]["OpenClawConfig Object"]
    end
    
    subgraph Infrastructure["Core Infrastructure"]
        [Meta]["meta: Version & History"]
        [Env]["env: Shell & Var Injection"]
        [Logging]["logging: Severity & Redaction"]
        [Diagnostics]["diagnostics: OTEL & Tracing"]
        [Update]["update: Auto-update Channels"]
    end
    
    subgraph GatewayIdentity["Gateway & Identity"]
        [Gateway]["gateway: Port, Bind, Mode"]
        [Auth]["auth: Auth Profiles"]
        [Models]["models: Provider Catalog"]
    end
    
    subgraph AgentRuntime["Agent & Tool Runtime"]
        [Agents]["agents: Workspace & Defaults"]
        [Tools]["tools: Policy & Security"]
        [Memory]["memory: Vector & QMD Knobs"]
        [Session]["session: Lifecycle & Maintenance"]
        [CloudWorkers]["cloudWorkers: Ephemeral Runtimes"]
    end
    
    subgraph Messaging["Messaging & Protocol"]
        [Channels]["channels: Platform Config"]
        [Commands]["commands: Slash Commands"]
    end
    
    subgraph Automation["Automation & ACP"]
        [Cron]["cron: Scheduled Jobs"]
        [ACP]["acp: Agent Control Protocol"]
        [MCP]["mcp: Model Context Protocol"]
    end
    
    [ConfigObject] --> Infrastructure
    [ConfigObject] --> GatewayIdentity
    [ConfigObject] --> AgentRuntime
    [ConfigObject] --> Messaging
    [ConfigObject] --> Automation
```
**Sources:** [src/config/schema.labels.ts:8-135](), [docs/gateway/configuration-reference.md:34-140]()

## Schema Validation System

OpenClaw employs a strict validation pipeline. Configuration is validated against a base schema defined in `OpenClawSchemaShape`. The system ensures cross-field integrity, such as ensuring `bindings` refer to valid agent IDs defined in `agents.entries` [src/cli/config-cli.ts:130-140]().

### Zod Schema Pipeline

The configuration loading process handles filesystem state and persistence. During runtime initialization, the system merges defaults and validates cross-field constraints. The `buildRuntimeConfigSchemaFromRegistry` function aggregates these definitions into a live JSON Schema for the Control UI [src/cli/config-cli.ts:137-140]().

Title: "Configuration Loading and Validation Flow"
```mermaid
graph LR
    subgraph Sources["Input Sources"]
        [JSON5]["openclaw.json [JSON5]"]
        [ENV]["Process Env [env.vars]"]
    end
    
    subgraph Logic["Logic [src/config/runtime-schema.ts]"]
        [Zod]["Zod Validation Pipeline"]
        [CoreSchema]["buildRuntimeConfigSchemaFromRegistry"]
    end
    
    subgraph Validation["Subsystem Schemas"]
        [AgentSchema]["AgentDefaultsSchema"]
        [CloudSchema]["CloudWorkerSchema"]
    end
    
    subgraph Output["Output"]
        [Config]["OpenClawConfig Object"]
    end
    
    [JSON5] --> [Zod]
    [ENV] --> [Zod]
    [Zod] --> [CoreSchema]
    [CoreSchema] --> [AgentSchema]
    [CoreSchema] --> [CloudSchema]
    [AgentSchema] --> [Config]
    [CloudSchema] --> [Config]
```
**Sources:** [src/cli/config-cli.ts:130-140](), [src/config/runtime-schema.ts:47]()

### Field Metadata and UI Hints

The system maps internal configuration paths to human-readable labels and help text.

| Metadata Entity | Code Reference | Purpose |
| :--- | :--- | :--- |
| `FIELD_HELP` | [src/config/schema.help.runtime.ts:1-10]() | Aggregated mapping of config paths to descriptive help strings. |
| `FIELD_LABELS` | [src/config/schema.labels.ts:8-130]() | Mapping of config paths to human-readable labels in the Control UI. |
| `BundledChannelConfigMetadata` | [src/config/bundled-channel-config-metadata.generated.ts:3-15]() | Type definition for auto-generated channel configuration metadata. |

## Subsystem Reference

### Agent Defaults & Workspace

The `agents.defaults` section defines the baseline behavior for all agents unless overridden in `agents.entries` [src/config/schema.labels.ts:96-100]().

| Key | Type | Default | Effect |
| :--- | :--- | :--- | :--- |
| `agents.defaults.workspace` | `string` | `~/.openclaw/workspace` | Base directory for agent files [docs/gateway/config-agents.md:32-34](). |
| `agents.defaults.contextInjection` | `enum` | `"always"` | Controls injection of bootstrap files (`always`, `continuation-skip`, `never`) [docs/gateway/config-agents.md:125-130](). |
| `agents.defaults.bootstrapMaxChars` | `number` | `20000` | Max characters per workspace bootstrap file [docs/gateway/config-agents.md:141-143](). |
| `agents.defaults.fastModeDefault` | `boolean` | `false` | Default setting for fast-mode inference [src/config/schema.labels.ts:90-90](). |
| `agents.defaults.cwd` | `string` | `undefined` | Optional working directory for agent reply runs [docs/gateway/config-agents.md:44-48](). |

**Sources:** [docs/gateway/config-agents.md:30-176](), [src/config/schema.labels.ts:76-113]()

### Session & Maintenance

The `session.maintenance` section controls automatic cleanup of SQLite session and transcript rows [docs/reference/session-management-compaction.md:43-46]().

| Key | Type | Default | Effect |
| :--- | :--- | :--- | :--- |
| `session.maintenance.mode` | `enum` | `"enforce"` | Operation mode: `"enforce"` (mutate) or `"warn"` (report only) [docs/reference/session-management-compaction.md:49-49](). |
| `session.maintenance.pruneAfter` | `duration` | `"30d"` | Cutoff age for stale session entries [docs/reference/session-management-compaction.md:50-50](). |
| `session.maintenance.maxDiskBytes` | `bytes` | `10gb` | Per-agent disk budget for sessions [docs/reference/session-management-compaction.md:54-54](). |
| `session.maintenance.highWaterBytes` | `bytes` | 80% | Target usage after cleanup [docs/reference/session-management-compaction.md:55-55](). |

**Sources:** [docs/reference/session-management-compaction.md:43-66]()

### Model Context Protocol (MCP)

Configuration for MCP servers managed by the Gateway [docs/gateway/configuration-reference.md:112-114]().

| Key | Type | Default | Effect |
| :--- | :--- | :--- | :--- |
| `mcp.servers.<name>.command` | `string` | `undefined` | Stdio transport command [docs/gateway/configuration-reference.md:124-124](). |
| `mcp.servers.<name>.url` | `string` | `undefined` | Remote endpoint URL for HTTP-based MCP [docs/gateway/configuration-reference.md:128-128](). |
| `mcp.servers.<name>.transport` | `enum` | `undefined` | Remote protocol: `"streamable-http"` or `"sse"` [docs/gateway/configuration-reference.md:129-129](). |
| `mcp.servers.<name>.auth` | `enum` | `"shared"` | Identity mode: `"shared"` or `"per-requester"` [docs/gateway/configuration-reference.md:136-138](). |

**Sources:** [docs/gateway/configuration-reference.md:112-140]()

### Messaging & Channels

OpenClaw supports multi-platform messaging via a normalized channel architecture. Per-channel config keys live under `channels.*` [docs/gateway/configuration-reference.md:34-36]().

Title: "Channel Configuration to Code Mapping"
```mermaid
graph TD
    subgraph Config["openclaw.json"]
        [ChanCfg]["channels.* [src/config/bundled-channel-config-metadata.generated.ts]"]
    end
    
    subgraph Metadata["Metadata [src/config/bundled-channel-config-metadata.generated.ts]"]
        [DiscordMeta]["Discord: token, accounts[]"]
        [SlackMeta]["Slack: appToken, botToken"]
        [TelegramMeta]["Telegram: botToken"]
    end
    
    subgraph Logic["CLI Runtime [src/cli/config-cli.test.ts]"]
        [SecretReg]["secretTargetRegistryEntries"]
        [Contract]["loadChannelSecretContractApi"]
    end
    
    [ChanCfg] --> [DiscordMeta]
    [ChanCfg] --> [SlackMeta]
    [ChanCfg] --> [TelegramMeta]
    [DiscordMeta] --> [Contract]
    [SlackMeta] --> [Contract]
    [Contract] --> [SecretReg]
```
**Sources:** [src/config/bundled-channel-config-metadata.generated.ts:1-17](), [src/cli/config-cli.test.ts:50-92]()

### Tools & Policy

The `tools.*` section configures global and per-agent tool access [docs/gateway/config-tools.md:11-13]().

| Key | Type | Default | Effect |
| :--- | :--- | :--- | :--- |
| `tools.profile` | `enum` | `undefined` | Base allowlist: `minimal`, `coding`, `messaging`, `full` [docs/gateway/config-tools.md:17-28](). |
| `worktreeRoot` | `string` | `<state>/worktrees` | Global root for managed worktree checkouts [docs/gateway/configuration-reference.md:53-55](). |

**Sources:** [docs/gateway/config-tools.md:15-50](), [docs/gateway/configuration-reference.md:53-63]()

### Infrastructure & Environment

| Key | Type | Default | Effect |
| :--- | :--- | :--- | :--- |
| `env.shellEnv.enabled` | `boolean` | `false` | Import secrets from login shell [src/config/schema.labels.ts:18-19](). |
| `env.vars` | `object` | `{}` | Inline environment variable overrides [src/config/schema.labels.ts:21-21](). |
| `logging.level` | `enum` | `undefined` | Primary log level threshold [src/config/schema.labels.ts:45-45](). |
| `diagnostics.otel.enabled` | `boolean` | `false` | Enables OpenTelemetry tracing [src/config/schema.labels.ts:60-60](). |

**Sources:** [src/config/schema.labels.ts:12-75]()

---

