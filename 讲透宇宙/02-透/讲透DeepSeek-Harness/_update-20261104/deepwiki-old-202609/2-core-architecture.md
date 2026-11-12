> 来源: [https://deepwiki.com/deepseek-ai/deepseek-harness/2-core-architecture](https://deepwiki.com/deepseek-ai/deepseek-harness/2-core-architecture)
> DeepWiki deepseek-ai/deepseek-harness

# Core Architecture

  Relevant source files 
 - [.agents/notes/implemented/bug-fix/2026-07-20-config-hot-reload-resilience.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.agents/notes/implemented/bug-fix/2026-07-20-config-hot-reload-resilience.i18n.yaml)
 - [.agents/notes/implemented/bug-fix/2026-07-20-config-hot-reload-resilience.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.agents/notes/implemented/bug-fix/2026-07-20-config-hot-reload-resilience.md?plain=1)
 - [.agents/notes/implemented/bug-fix/2026-07-20-config-hot-reload-resilience.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/.agents/notes/implemented/bug-fix/2026-07-20-config-hot-reload-resilience.zh.md?plain=1)
 - [apps/cli/package.json](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/apps/cli/package.json)
 - [apps/cli/tsconfig.json](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/apps/cli/tsconfig.json)
 - [apps/web/tests/plan-control-row.e2e.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/apps/web/tests/plan-control-row.e2e.ts)
 - [apps/web/tests/scaffold.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/apps/web/tests/scaffold.ts)
 - [apps/web/tsconfig.json](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/apps/web/tsconfig.json)
 - [docs/architecture.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/architecture.i18n.yaml)
 - [docs/architecture.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/architecture.md?plain=1)
 - [docs/architecture.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/architecture.zh.md?plain=1)
 - [docs/capability-seams.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/capability-seams.md?plain=1)
 - [docs/config-catalog.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/config-catalog.i18n.yaml)
 - [docs/config-catalog.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/config-catalog.md?plain=1)
 - [docs/config-catalog.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/config-catalog.zh.md?plain=1)
 - [docs/event-producer-consumer.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/event-producer-consumer.i18n.yaml)
 - [docs/event-producer-consumer.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/event-producer-consumer.md?plain=1)
 - [docs/event-producer-consumer.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/event-producer-consumer.zh.md?plain=1)
 - [docs/module-graph.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/module-graph.i18n.yaml)
 - [docs/module-graph.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/module-graph.md?plain=1)
 - [docs/module-graph.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/module-graph.zh.md?plain=1)
 - [knip.json](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/knip.json)
 - [packages/core/agent-loop/README.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/README.md?plain=1)
 - [packages/core/agent-loop/src/agent.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/src/agent.ts)
 - [packages/core/agent-loop/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/src/index.ts)
 - [packages/core/agent-loop/tests/agent.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/tests/agent.spec.ts)
 - [packages/core/agent-loop/tests/cancel.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/tests/cancel.spec.ts)
 - [packages/core/agent-loop/tests/config-session-id.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/tests/config-session-id.spec.ts)
 - [packages/core/agent-loop/tests/contract-regressions.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/tests/contract-regressions.spec.ts)
 - [packages/core/agent-loop/tests/coverage-edges.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/tests/coverage-edges.spec.ts)
 - [packages/core/agent-loop/tests/interception.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/tests/interception.spec.ts)
 - [packages/core/agent-loop/tests/loop.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/tests/loop.spec.ts)
 - [packages/core/agent-loop/tests/resume.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/tests/resume.spec.ts)
 - [packages/core/agent/README.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent/README.md?plain=1)
 - [packages/core/agent/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent/src/index.ts)
 - [packages/core/agent/src/types.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent/src/types.ts)
 - [packages/core/agent/tests/agent.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent/tests/agent.spec.ts)
 - [packages/extensions/tool-cordis/src/api-catalog.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/extensions/tool-cordis/src/api-catalog.ts)
 - [pnpm-lock.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/pnpm-lock.yaml)
 - [scripts/gen-cordis-catalog.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/scripts/gen-cordis-catalog.ts)
 - [scripts/gen-doc-graphs.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/scripts/gen-doc-graphs.ts)
 - [scripts/type-equiv.manifest.json](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/scripts/type-equiv.manifest.json)
 - [scripts/verify-package-readme-model-experience.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/scripts/verify-package-readme-model-experience.ts)
 - [tsconfig.base.json](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/tsconfig.base.json)
 - [tsconfig.host.json](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/tsconfig.host.json)
 - [tsconfig.json](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/tsconfig.json)
 - [vendor/README.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/vendor/README.md?plain=1)
 - [vendor/cordis/src/context.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/vendor/cordis/src/context.ts)
 - [vendor/cordis/src/events.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/vendor/cordis/src/events.ts)
 - [vendor/cordis/src/fiber.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/vendor/cordis/src/fiber.ts)
 - [vendor/cordis/src/logger.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/vendor/cordis/src/logger.ts)
 - [vendor/cordis/src/reflect.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/vendor/cordis/src/reflect.ts)
 - [vendor/cordis/src/registry.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/vendor/cordis/src/registry.ts)
 - [vendor/cordis/src/service.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/vendor/cordis/src/service.ts)
 - [vendor/hmr/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/vendor/hmr/src/index.ts)
 - [vendor/include/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/vendor/include/src/index.ts)
 - [vendor/loader/src/config/entry.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/vendor/loader/src/config/entry.ts)
 - [vendor/loader/src/config/group.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/vendor/loader/src/config/group.ts)
 - [vendor/loader/src/config/isolate.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/vendor/loader/src/config/isolate.ts)
 - [vendor/loader/src/config/tree.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/vendor/loader/src/config/tree.ts)
 - [vendor/loader/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/vendor/loader/src/index.ts)
 - [vendor/loader/src/internal.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/vendor/loader/src/internal.ts)
 - [vendor/logger-console/src/browser.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/vendor/logger-console/src/browser.ts)
 - [vendor/logger-console/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/vendor/logger-console/src/index.ts)
 
  DeepSeek Harness (dsh) is built on a modular, plugin-first architecture using the **Cordis** framework. Every functional component—from the LLM adapters and tool registries to the session logs and the agent loop itself—is a plugin that contributes services and effects to a shared context [docs/architecture.md9-14](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/architecture.md?plain=1#L9-L14)

 
## The Cordis Plugin Framework

 DSH leverages a vendored version of the **Cordis** framework to manage its lifecycle. Plugins are the fundamental unit of composition; they provide **Services** (accessible via `ctx.serviceName`), listen to **Events**, and manage reversible side effects [docs/architecture.md9-14](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/architecture.md?plain=1#L9-L14)

 
 - **Service Injection:** Plugins declare dependencies using the `inject` property. The runtime ensures that a plugin only starts once its required services are available [docs/config-catalog.md10](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/config-catalog.md?plain=1#L10-L10)
 - **Context Declaration Merging:** TypeScript interfaces are merged to provide type-safe access to services on the `Context` object (e.g., `ctx.llm`, `ctx.agents`) [tsconfig.host.json2-4](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/tsconfig.host.json#L2-L4)
 - **Disposable Effects:** When a plugin is unloaded, all its registrations (tools, events, services) are automatically cleaned up [docs/architecture.md13-14](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/architecture.md?plain=1#L13-L14)
 
 For details, see [Cordis Framework & Vendored Dependencies](https://deepwiki.com/deepseek-ai/deepseek-harness/2.1-cordis-framework-and-vendored-dependencies).

 
## Plugin Composition: Profiles & Bundles

 A running instance of `dsh` is assembled from ordered layers of configuration and code [docs/architecture.md17](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/architecture.md?plain=1#L17-L17)

 
| Entity | Description |
|---|---|
| Profile | A named composition (e.g., web, headless) that defines which bundles to stack and provides user-level patches docs/architecture.md19-21 |
| Bundle | A distribution of Cordis config rows (e.g., dsh-base) that provides a baseline set of features docs/architecture.md21-23 |
| Patch | A YAML-based override (cordis.patch.yml) that can modify any configuration row in the tree by its ID docs/architecture.md27-28 |

 The final configuration tree can be inspected using the `dsh --profile web --dump-config` command [docs/architecture.md31-35](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/architecture.md?plain=1#L31-L35)

 For details, see [Plugin Composition: Profiles, Bundles & Configuration](https://deepwiki.com/deepseek-ai/deepseek-harness/2.2-plugin-composition:-profiles-bundles-and-configuration).

 
## Event Bus & Capability Seams

 Communication between subsystems is handled via a central event bus and well-defined "capability seams."

 
### The Event Bus

 DSH uses three primary event domains to facilitate decoupled communication [docs/architecture.md64-71](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/architecture.md?plain=1#L64-L71):

 
 - **Session Events:** Durable facts appended to the log and broadcast through `session/event`. Use one when the fact must survive a reload [docs/architecture.md68](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/architecture.md?plain=1#L68-L68)
 - **Agent Events:** Live lifecycle hooks for the agent loop (e.g., `agent/pre-step`, `agent/request`) [docs/architecture.md69](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/architecture.md?plain=1#L69-L69)
 - **Capability Events:** Policy and adapter attachments for specific seams (e.g., `fs/*`, `tools/*`) [docs/architecture.md70](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/architecture.md?plain=1#L70-L70)
 
 
### Capability Seams

 A **seam** is a swappable interface that allows the system to change behavior by swapping a provider without changing the consumer [docs/config-catalog.md6-8](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/config-catalog.md?plain=1#L6-L8) For example, the `ctx.llm` seam allows swapping between DeepSeek and Pi.ai adapters [docs/architecture.md61](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/architecture.md?plain=1#L61-L61)

 
### System Component Map

 The following diagram maps high-level system concepts to their specific code entities and service keys.

 **Architecture Component Map**

 
```

```

 Sources: [docs/architecture.md53-62](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/architecture.md?plain=1#L53-L62) [packages/core/agent-loop/src/agent.ts1-20](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/src/agent.ts#L1-L20) [docs/module-graph.md21-41](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/module-graph.md?plain=1#L21-L41) [docs/event-producer-consumer.md8-23](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/event-producer-consumer.md?plain=1#L8-L23)

 For details, see [Event Bus & Capability Seams](https://deepwiki.com/deepseek-ai/deepseek-harness/2.3-event-bus-and-capability-seams).

 
## Turn Flow and Execution

 The **Agent Loop** orchestrates the interaction between the LLM and the execution environment through **Turns** and **Steps** [docs/architecture.md75-77](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/architecture.md?plain=1#L75-L77)

 
 - **Turn:** A complete interaction cycle that opens on user input and closes when no further model actions are owed [docs/architecture.md76](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/architecture.md?plain=1#L76-L76)
 - **Step:** A single model request followed by the execution of any resulting tool calls [docs/architecture.md76](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/architecture.md?plain=1#L76-L76)
 
 **Step Execution Pipeline**

 
```

```

 Sources: [docs/architecture.md78-93](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/architecture.md?plain=1#L78-L93) [docs/event-producer-consumer.md18-20](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/event-producer-consumer.md?plain=1#L18-L20)

 
## Subsystem Navigation

 
 - **[Cordis Framework & Vendored Dependencies](https://deepwiki.com/deepseek-ai/deepseek-harness/2.1-cordis-framework-and-vendored-dependencies):** Lifecycle, service injection, and modifications to the upstream framework.
 - **[Plugin Composition: Profiles, Bundles & Configuration](https://deepwiki.com/deepseek-ai/deepseek-harness/2.2-plugin-composition:-profiles-bundles-and-configuration):** How the system is assembled and patched.
 - **[Event Bus & Capability Seams](https://deepwiki.com/deepseek-ai/deepseek-harness/2.3-event-bus-and-capability-seams):** Detailed map of event flows and swappable capability interfaces.
