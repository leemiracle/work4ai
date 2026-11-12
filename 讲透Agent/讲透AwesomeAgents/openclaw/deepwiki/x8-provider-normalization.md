<!-- source: DeepWiki mcp.deepwiki.com · repo openclaw/openclaw · extra page Provider Normalization · fetched 2026-10-26 -->

# Provider Normalization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/concepts/models.md](docs/concepts/models.md)
- [extensions/venice/pricing-api.ts](extensions/venice/pricing-api.ts)
- [packages/model-catalog-core/src/model-catalog-pricing.test.ts](packages/model-catalog-core/src/model-catalog-pricing.test.ts)
- [packages/model-catalog-core/src/model-catalog-pricing.ts](packages/model-catalog-core/src/model-catalog-pricing.ts)
- [scripts/publish-model-catalog.mts](scripts/publish-model-catalog.mts)
- [src/agents/agent-auth-credential-modes.ts](src/agents/agent-auth-credential-modes.ts)
- [src/agents/agent-auth-credentials.ts](src/agents/agent-auth-credentials.ts)
- [src/agents/embedded-agent-runner/model.static-catalog.prepared.test.ts](src/agents/embedded-agent-runner/model.static-catalog.prepared.test.ts)
- [src/agents/embedded-agent-runner/run.overflow-compaction.misc-owners.test.ts](src/agents/embedded-agent-runner/run.overflow-compaction.misc-owners.test.ts)
- [src/agents/embedded-agent-runner/run/auth-profile-success.ts](src/agents/embedded-agent-runner/run/auth-profile-success.ts)
- [src/agents/harness/runtime-plugin-load-plan.ts](src/agents/harness/runtime-plugin-load-plan.ts)
- [src/agents/harness/runtime-plugin.test.ts](src/agents/harness/runtime-plugin.test.ts)
- [src/agents/harness/runtime-plugin.ts](src/agents/harness/runtime-plugin.ts)
- [src/agents/model-auth-availability.test.ts](src/agents/model-auth-availability.test.ts)
- [src/agents/model-auth-availability.ts](src/agents/model-auth-availability.ts)
- [src/agents/model-catalog-browse.test.ts](src/agents/model-catalog-browse.test.ts)
- [src/agents/model-catalog-browse.ts](src/agents/model-catalog-browse.ts)
- [src/agents/prepared-model-catalog-worker.integration.test.ts](src/agents/prepared-model-catalog-worker.integration.test.ts)
- [src/agents/prepared-model-catalog-worker.test.ts](src/agents/prepared-model-catalog-worker.test.ts)
- [src/agents/prepared-model-catalog-worker.ts](src/agents/prepared-model-catalog-worker.ts)
- [src/agents/prepared-model-catalog.worker.ts](src/agents/prepared-model-catalog.worker.ts)
- [src/agents/prepared-model-runtime-auth.ts](src/agents/prepared-model-runtime-auth.ts)
- [src/agents/prepared-model-runtime-config-stamp.test.ts](src/agents/prepared-model-runtime-config-stamp.test.ts)
- [src/agents/prepared-model-runtime-generation-scope.ts](src/agents/prepared-model-runtime-generation-scope.ts)
- [src/agents/prepared-model-runtime-lease.ts](src/agents/prepared-model-runtime-lease.ts)
- [src/agents/prepared-model-runtime.build.ts](src/agents/prepared-model-runtime.build.ts)
- [src/agents/prepared-model-runtime.catalog-contract.ts](src/agents/prepared-model-runtime.catalog-contract.ts)
- [src/agents/prepared-model-runtime.catalog-owner.test.ts](src/agents/prepared-model-runtime.catalog-owner.test.ts)
- [src/agents/prepared-model-runtime.configured-catalog.ts](src/agents/prepared-model-runtime.configured-catalog.ts)
- [src/agents/prepared-model-runtime.configured-completion.ts](src/agents/prepared-model-runtime.configured-completion.ts)
- [src/agents/prepared-model-runtime.configured.ts](src/agents/prepared-model-runtime.configured.ts)
- [src/agents/prepared-model-runtime.facts.ts](src/agents/prepared-model-runtime.facts.ts)
- [src/agents/prepared-model-runtime.full-catalog.ts](src/agents/prepared-model-runtime.full-catalog.ts)
- [src/agents/prepared-model-runtime.inbound-registry.test.ts](src/agents/prepared-model-runtime.inbound-registry.test.ts)
- [src/agents/prepared-model-runtime.inbound-registry.ts](src/agents/prepared-model-runtime.inbound-registry.ts)
- [src/agents/prepared-model-runtime.lifecycle.test.ts](src/agents/prepared-model-runtime.lifecycle.test.ts)
- [src/agents/prepared-model-runtime.owner-selection.test.ts](src/agents/prepared-model-runtime.owner-selection.test.ts)
- [src/agents/prepared-model-runtime.owner.ts](src/agents/prepared-model-runtime.owner.ts)
- [src/agents/prepared-model-runtime.plugin-context.test.ts](src/agents/prepared-model-runtime.plugin-context.test.ts)
- [src/agents/prepared-model-runtime.plugin-context.ts](src/agents/prepared-model-runtime.plugin-context.ts)
- [src/agents/prepared-model-runtime.plugin-generation.ts](src/agents/prepared-model-runtime.plugin-generation.ts)
- [src/agents/prepared-model-runtime.reload-auth.test.ts](src/agents/prepared-model-runtime.reload-auth.test.ts)
- [src/agents/prepared-model-runtime.scoped-catalog.ts](src/agents/prepared-model-runtime.scoped-catalog.ts)
- [src/agents/prepared-model-runtime.scoped-refresh.test.ts](src/agents/prepared-model-runtime.scoped-refresh.test.ts)
- [src/agents/prepared-model-runtime.startup-static.test.ts](src/agents/prepared-model-runtime.startup-static.test.ts)
- [src/agents/prepared-model-runtime.test-harness.ts](src/agents/prepared-model-runtime.test-harness.ts)
- [src/agents/prepared-model-runtime.test.ts](src/agents/prepared-model-runtime.test.ts)
- [src/agents/prepared-model-runtime.ts](src/agents/prepared-model-runtime.ts)
- [src/agents/prepared-model-runtime.types.ts](src/agents/prepared-model-runtime.types.ts)
- [src/agents/provider-auth-aliases.test.ts](src/agents/provider-auth-aliases.test.ts)
- [src/agents/runtime-plugins.memory-corpus.integration.test.ts](src/agents/runtime-plugins.memory-corpus.integration.test.ts)
- [src/agents/runtime-plugins.test.ts](src/agents/runtime-plugins.test.ts)
- [src/agents/runtime-plugins.ts](src/agents/runtime-plugins.ts)
- [src/agents/sessions/model-registry.test.ts](src/agents/sessions/model-registry.test.ts)
- [src/agents/sessions/model-registry.ts](src/agents/sessions/model-registry.ts)
- [src/agents/sessions/resolve-config-value.ts](src/agents/sessions/resolve-config-value.ts)
- [src/auto-reply/reply/get-reply-run.prepared-metadata.test.ts](src/auto-reply/reply/get-reply-run.prepared-metadata.test.ts)
- [src/auto-reply/reply/get-reply-run.ts](src/auto-reply/reply/get-reply-run.ts)
- [src/auto-reply/reply/queue.drain-restart.test.ts](src/auto-reply/reply/queue.drain-restart.test.ts)
- [src/gateway/server-chat-metadata-lifecycle.integration.test.ts](src/gateway/server-chat-metadata-lifecycle.integration.test.ts)
- [src/gateway/server-methods/models-list-auth-resolver.ts](src/gateway/server-methods/models-list-auth-resolver.ts)
- [src/gateway/server-methods/models-list-result.cli-runtime-availability.test.ts](src/gateway/server-methods/models-list-result.cli-runtime-availability.test.ts)
- [src/gateway/server-methods/models-list-result.configured-static.test.ts](src/gateway/server-methods/models-list-result.configured-static.test.ts)
- [src/gateway/server-methods/models-list-result.openai-routes.test-support.ts](src/gateway/server-methods/models-list-result.openai-routes.test-support.ts)
- [src/gateway/server-methods/models-list-result.openai-routes.test.ts](src/gateway/server-methods/models-list-result.openai-routes.test.ts)
- [src/gateway/server-methods/models-list-result.provider-outcomes.test.ts](src/gateway/server-methods/models-list-result.provider-outcomes.test.ts)
- [src/gateway/server-methods/models-list-result.ts](src/gateway/server-methods/models-list-result.ts)
- [src/gateway/server-methods/models.test.ts](src/gateway/server-methods/models.test.ts)
- [src/gateway/server-model-catalog-auth.ts](src/gateway/server-model-catalog-auth.ts)
- [src/gateway/server-model-catalog.test.ts](src/gateway/server-model-catalog.test.ts)
- [src/gateway/server-model-catalog.ts](src/gateway/server-model-catalog.ts)
- [src/gateway/server-model-catalog.types.ts](src/gateway/server-model-catalog.types.ts)
- [src/gateway/server.sessions.agent-model-catalog.test.ts](src/gateway/server.sessions.agent-model-catalog.test.ts)
- [src/infra/approval-native-route-coordinator.ts](src/infra/approval-native-route-coordinator.ts)
- [src/plugins/current-plugin-metadata-snapshot.test.ts](src/plugins/current-plugin-metadata-snapshot.test.ts)
- [src/plugins/gateway-startup-plugin-metadata.ts](src/plugins/gateway-startup-plugin-metadata.ts)
- [src/plugins/memory-state.test.ts](src/plugins/memory-state.test.ts)
- [src/plugins/memory-state.ts](src/plugins/memory-state.ts)
- [src/plugins/plugin-metadata-snapshot.types.ts](src/plugins/plugin-metadata-snapshot.types.ts)
- [src/plugins/provider-runtime.usage-harness.test.ts](src/plugins/provider-runtime.usage-harness.test.ts)
- [src/plugins/runtime/generation-scope.ts](src/plugins/runtime/generation-scope.ts)
- [test/scripts/publish-model-catalog.test.ts](test/scripts/publish-model-catalog.test.ts)

</details>



This page describes the `normalizeProviders` pipeline, the discovery of implicit providers (such as Google Vertex ADC, GitHub Copilot, and Ollama), and the synchronization of normalized model configurations. Provider normalization ensures that model provider definitions from various sources—configuration files, environment variables, and plugins—are transformed into a canonical format used by the Agent Runtime.

---

## Normalization Pipeline Overview

The normalization process occurs in two primary stages: explicit normalization of configured providers and discovery of implicit providers based on the environment and authentication profiles. This pipeline is critical for the execution pipeline to resolve specific model capabilities and transport settings.

### Provider Discovery and Sync Flow
The following diagram illustrates the flow from configuration sources through the normalization logic to the final `models.json` artifact and runtime transports.

```mermaid
graph TB
    subgraph "Natural_Language_Space"["Natural Language Space"]
        "User_Configuration"["User Configuration"]
        "Environment_Discovery"["Environment Discovery"]
        "Plugin_Extensions"["Plugin Extensions"]
    end

    subgraph "Code_Entity_Space"["Code Entity Space"]
        "OpenClawConfig"["OpenClawConfig"]
        "resolveModelsListView"["resolveModelsListView()"]
        "normalizeProviderId"["normalizeProviderId()"]
        "buildPublicModelProjection"["buildPublicModelProjection()"]
        "loadGatewayModelCatalogSnapshot"["loadGatewayModelCatalogSnapshot()"]
        "buildGuardedModelFetch"["buildGuardedModelFetch()"]
    end

    "User_Configuration" -- "models.providers" --> "OpenClawConfig"
    "OpenClawConfig" -- "explicit config" --> "normalizeProviderId"
    "Environment_Discovery" -- "process.env" --> "resolveModelsListView"
    "Plugin_Extensions" -- "manifest discovery" --> "loadGatewayModelCatalogSnapshot"
    "normalizeProviderId" -- "registry sync" --> "Models_JSON"["models.json"]
    "loadGatewayModelCatalogSnapshot" -- "snapshot projection" --> "buildPublicModelProjection"
    "buildPublicModelProjection" -- "transport wrapping" --> "buildGuardedModelFetch"
```
**Sources:** [src/gateway/server-methods/models-list-result.ts:94-114](), [src/gateway/server-methods/models-list-result.ts:83-86](), [src/gateway/server-methods/models-list-result.ts:2-2](), [src/gateway/server-methods/models-list-result.ts:61-64]()

---

## Stage 1: Explicit Provider Normalization

Normalization ensures that manually entered settings in `openclaw.json` are sanitized and compatible with the underlying AI libraries. This is handled by functions that resolve provider IDs and apply manifest-defined normalization rules.

### Key Normalization Steps
1.  **Provider ID Normalization**: `normalizeProviderId` transforms raw provider names into canonical slugs for routing and credential lookup [src/gateway/server-methods/models-list-result.ts:2-2]().
2.  **Public Projection**: `buildPublicModelProjection` strips internal runtime facts (base URLs, costs) and projects models onto the public protocol shape `ModelChoice` [src/gateway/server-methods/models-list-result.ts:61-64]().
3.  **Inventory Merging**: `resolveProviderConfigInventoryEntries` reconciles authored configuration with canonical plugin catalogs, ensuring configured overrides take precedence while maintaining metadata consistency [src/gateway/server-methods/models-list-result.ts:116-156]().
4.  **Thinking Policy Materialization**: `prepareModelCatalogThinkingPolicies` applies metadata-driven reasoning configurations to the projected catalog, mapping provider capabilities to agent-accessible levels [src/agents/prepared-model-runtime.build.ts:164-168]().

**Sources:** [src/gateway/server-methods/models-list-result.ts:2-156](), [src/agents/prepared-model-runtime.build.ts:159-170]()

---

## Stage 2: Implicit Provider Discovery

Implicit discovery allows OpenClaw to support providers available via the environment, active authentication profiles, or specialized SDK harnesses.

### Discovery Logic
The system uses a combination of environment variable checks and plugin-specific resolution to auto-register providers.

| Discovery Mechanism | Implementation |
| :--- | :--- |
| **Plugin Discovery** | Plugins declare `modelCatalog.discovery` modes as `runtime` or `refreshable` to trigger dynamic probing [src/gateway/server-methods/models-list-result.ts:98-106](). |
| **Auth Fact Discovery** | `discoverAuthStorageFacts` probes `agentDir` and environment for usable credentials, including inherited and ambient sources [src/agents/prepared-model-runtime.facts.ts:108-119](). |
| **External CLI Sync** | `listExternalCliSyncProviderIds` identifies providers that require synchronization with local CLI tools (e.g., `gcloud`, `aws`) [src/agents/prepared-model-catalog.worker.ts:23-23](). |
| **Synthetic Auth** | `resolveRuntimeSyntheticAuthProviderRefs` resolves virtual providers that proxy authentication to other backends [src/agents/prepared-model-runtime.facts.ts:22-22](). |

### Worker-Based Discovery
To prevent blocking the main Gateway event loop during potentially slow network probes, discovery is offloaded to a worker thread via `createPreparedModelCatalogWorker` [src/agents/prepared-model-runtime.build.ts:15-17](). This worker:
1. Restores config resolution facts [src/agents/prepared-model-catalog.worker.ts:92-98]().
2. Overlays external auth profiles [src/agents/prepared-model-catalog.worker.ts:79-85]().
3. Executes `prepareWorkspaceBuildGroup` to generate a fresh catalog snapshot [src/agents/prepared-model-catalog.worker.ts:123-130]().

**Sources:** [src/agents/prepared-model-runtime.facts.ts:107-154](), [src/agents/prepared-model-catalog.worker.ts:89-145](), [src/gateway/server-methods/models-list-result.ts:89-114]()

---

## Prepared Model Runtime (PMR) Synchronization

OpenClaw uses a "Prepared Model Runtime" (PMR) to synchronize normalized provider data across different agent runs and the Gateway.

### PMR Lifecycle
1.  **Preparation**: `prepareModelRuntimeOwner` initializes the identity and environment fingerprint for a specific agent/workspace pair [src/agents/prepared-model-runtime.owner.ts:76-91]().
2.  **Building**: `runSerializedPreparedModelRuntimeTask` ensures that catalog builds for the same `agentDir` are serialized to prevent race conditions and excessive memory growth [src/agents/prepared-model-runtime.build.ts:84-116]().
3.  **Publication**: `publishPreparedModelRuntimeSnapshot` stamps the snapshot with the current config and attaches it to the owner for future resolution [src/agents/prepared-model-runtime.owner.ts:50-61]().
4.  **Inbound Registry**: `loadPreparedInboundPluginRegistry` manages the lifecycle of plugin registries, ensuring they match the manifest generation of the prepared snapshot [src/agents/prepared-model-runtime.inbound-registry.ts:60-99]().

### Models.json Synchronization
The `ensureOpenClawModelsJson` function (mocked in tests) synchronizes the normalized provider catalog to a local `models.json` file. This allows the system to maintain a persistent cache of discovered models that survives restarts while respecting workspace-specific overrides [src/agents/prepared-model-runtime.startup-static.test.ts:52-57]().

**Sources:** [src/agents/prepared-model-runtime.owner.ts:42-177](), [src/agents/prepared-model-runtime.build.ts:84-116](), [src/agents/prepared-model-runtime.inbound-registry.ts:60-121]()

---

## Code Entity Mapping

The following diagram bridges the high-level normalization concepts to the specific code entities implementing them.

```mermaid
graph LR
    subgraph "Input_Sources"["Input Sources"]
        "OpenClawConfig"["OpenClawConfig"]
        "AuthProfileStore"["AuthProfileStore"]
        "PluginMetadata"["PluginMetadataSnapshot"]
    end

    subgraph "Normalization_Engine"["Normalization Engine"]
        "normalizeProviderId"["normalizeProviderId()"]
        "prepareAgentFacts"["prepareAgentFacts()"]
        "loadPreparedInboundPluginRegistry"["loadPreparedInboundPluginRegistry()"]
        "createPreparedModelCatalogWorker"["createPreparedModelCatalogWorker()"]
    end

    subgraph "Canonical_Output"["Canonical Output"]
        "PreparedSnapshot"["PreparedModelRuntimeSnapshot"]
        "ModelsJSON"["models.json"]
        "ModelCatalog"["ModelCatalogSnapshot"]
    end

    "OpenClawConfig" --> "normalizeProviderId"
    "AuthProfileStore" --> "prepareAgentFacts"
    "PluginMetadata" --> "loadPreparedInboundPluginRegistry"
    "prepareAgentFacts" --> "createPreparedModelCatalogWorker"
    "createPreparedModelCatalogWorker" --> "ModelCatalog"
    "ModelCatalog" --> "PreparedSnapshot"
    "PreparedSnapshot" --> "ModelsJSON"
```
**Sources:** [src/gateway/server-methods/models-list-result.ts:2-2](), [src/agents/prepared-model-runtime.facts.ts:99-105](), [src/agents/prepared-model-runtime.inbound-registry.ts:60-64](), [src/agents/prepared-model-runtime.build.ts:14-17]()

---

