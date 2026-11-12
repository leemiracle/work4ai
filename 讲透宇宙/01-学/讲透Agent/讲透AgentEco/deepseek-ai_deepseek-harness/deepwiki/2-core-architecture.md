<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/deepseek-harness · page 2 Core Architecture · fetched 2026-10-27 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/architecture.i18n.yaml](docs/architecture.i18n.yaml)
- [docs/architecture.md](docs/architecture.md)
- [docs/architecture.zh.md](docs/architecture.zh.md)
- [docs/capability-seams.i18n.yaml](docs/capability-seams.i18n.yaml)
- [docs/capability-seams.md](docs/capability-seams.md)
- [docs/capability-seams.zh.md](docs/capability-seams.zh.md)
- [packages/core/agent-loop/README.i18n.yaml](packages/core/agent-loop/README.i18n.yaml)
- [packages/core/agent-loop/README.md](packages/core/agent-loop/README.md)
- [packages/core/agent-loop/README.zh.md](packages/core/agent-loop/README.zh.md)
- [packages/core/agent-loop/src/agent.ts](packages/core/agent-loop/src/agent.ts)
- [packages/core/agent-loop/tests/cancel.spec.ts](packages/core/agent-loop/tests/cancel.spec.ts)
- [packages/core/agent-loop/tests/contract-regressions.spec.ts](packages/core/agent-loop/tests/contract-regressions.spec.ts)
- [packages/core/agent-loop/tests/coverage-edges.spec.ts](packages/core/agent-loop/tests/coverage-edges.spec.ts)
- [packages/core/agent-loop/tests/interception.spec.ts](packages/core/agent-loop/tests/interception.spec.ts)
- [packages/core/agent-loop/tests/loop.spec.ts](packages/core/agent-loop/tests/loop.spec.ts)
- [packages/core/agent/README.i18n.yaml](packages/core/agent/README.i18n.yaml)
- [packages/core/agent/README.md](packages/core/agent/README.md)
- [packages/core/agent/README.zh.md](packages/core/agent/README.zh.md)
- [packages/core/agent/src/types.ts](packages/core/agent/src/types.ts)
- [scripts/gen-doc-graphs.ts](scripts/gen-doc-graphs.ts)

</details>



This page provides an overview of the core architectural foundations of DeepSeek Harness (`dsh`), powered by the **Cordis** plugin framework. Every functional subsystem—from model adapters and tool registries to session logging and the core agent loop—is implemented as a modular plugin contributing services, typed events, and reversible effects to a shared context [docs/architecture.md:9-11](). 

For deep technical details on each subsystem, refer to the child pages:
- [Cordis Framework & Vendored Dependencies](#2.1) — Deep dive into the vendored Cordis framework: plugin lifecycle, service injection, Context declaration merging, fiber disposal, and local modifications to upstream source.
- [Plugin Composition: Profiles, Bundles & Configuration](#2.2) — How a running dsh instance is assembled from ordered patch layers. Covers profiles, bundles, cordis.yml, the config catalog, and dump-config.
- [Event Bus & Capability Seams](#2.3) — Explains the event-driven communication model: session/event, agent/pre-step, llm/stream waterfalls, and the capability seam pattern. Covers the event producer-consumer map.

---

## 2.1 Cordis Framework & Vendored Dependencies

At the core of DeepSeek Harness's extensibility lies the **Cordis** plugin framework [docs/architecture.md:9-14](). Cordis enables `dsh` to be composed entirely from plugins, each contributing typed services, typed events, and reversible side effects so that unloading a plugin cleanly removes all traces of its state and registrations [docs/architecture.md:9-14]().

Plugins declare their required dependencies and exports, leveraging TypeScript declaration merging to compose a rich, typed `Context` object representing the full runtime environment [packages/core/agent/src/types.ts:17-26](). There is no privileged monolithic core; subsystems like the model adapter, tool registry, session log, and agent loop are fully replaceable via configuration [docs/architecture.md:9-11]().

For an in-depth deep dive into Cordis lifecycle, service injection, Context declaration merging, and local vendored modifications, see [Cordis Framework & Vendored Dependencies](#2.1).

Sources: [docs/architecture.md:9-14](), [packages/core/agent/src/types.ts:17-26]()

---

## 2.2 Plugin Composition: Profiles, Bundles & Configuration

A running instance of `dsh` is assembled at startup by layering ordered patch sets into a coherent plugin tree [docs/architecture.md:15-42]():
- **Profiles** are named compositions (e.g., `web`, `headless`, `sdk`, `sdk-minimal`, `acp`) stored within the Harness home directory [docs/architecture.md:17-18]().
- **Bundles** are the distribution units of configuration rows and their corresponding code modules [docs/architecture.md:19-21]().
- **Patches** (`cordis.patch.yml`) are YAML overlays that selectively replace or insert config rows identified by ID [docs/architecture.md:25-27]().

The boot composition order applies empty configuration first, then each bundle in the profile's order, followed by the profile patch, the home patch, and finally any CLI `--patch` overlay [docs/architecture.md:25-27](). To inspect the effective plugin tree and configuration for a profile:

```bash
dsh --profile web --dump-config
```

For detailed mechanics of profiles, bundles, patching, and the generated configuration catalog, see [Plugin Composition: Profiles, Bundles & Configuration](#2.2).

Sources: [docs/architecture.md:15-42]()

---

## 2.3 Event Bus & Capability Seams

`dsh` uses a typed, centralized event bus combined with a **capability seam** pattern to organize runtime communication and enable swappable extensions [docs/architecture.md:71-76]().
- **Session Events** are durable facts appended to the append-only session log and broadcast on `session/event` [docs/architecture.md:71-72]().
- **Agent Events** (`agent/*`) convey live agent runtime information, including inbox state, step transitions, ongoing request status, and tool executions [docs/architecture.md:73-74]().
- **Capability Seams** abstract core subsystems (e.g., `ctx.llm`, `ctx.tools`, `ctx.fs`) behind service interfaces allowing multiple interchangeable implementations to coexist [docs/architecture.md:75-76]().

For complete details on the event model, waterfall semantics, and the event producer-consumer mappings, see [Event Bus & Capability Seams](#2.3).

Sources: [docs/architecture.md:71-76]()

---

## Subsystem Architecture & Code Mapping

This diagram bridges key system concepts in natural language to precise code artifacts and service names in the monorepo.

### Core Architecture Component Map
```mermaid
graph TD
    subgraph "Cordis_Context"
        direction LR
        svc_llm[""ctx.llm: LlmRuntime (packages/llm/llm)""]
        svc_agents[""ctx.agents: AgentRegistry (packages/core/agent)""]
        svc_tools[""ctx.tools: ToolRuntime (packages/core/tools)""]
        svc_sessions[""ctx.sessions: SessionStore (packages/core/session)""]
    end

    subgraph "Core_Packages"
        pkg_agent_loop[""packages/core/agent-loop""]
        pkg_llm[""packages/llm/llm""]
        pkg_tools[""packages/core/tools""]
        pkg_session[""packages/core/session""]
    end

    pkg_agent_loop --> svc_agents
    pkg_llm --> svc_llm
    pkg_tools --> svc_tools
    pkg_session --> svc_sessions

    svc_agents -- "drives agent instances" --> ReactLoopAgent[""ReactLoopAgent (packages/core/agent-loop/src/agent.ts)""]
    svc_llm -- "manages LLM adapters" --> LlmAdapter[""LlmAdapter (packages/llm/llm/src/types.ts)""]
    svc_tools -- "executes registered tools" --> Tool[""Tool (packages/core/tools/src/types.ts)""]
```
Sources: [docs/architecture.md:59-71](), [packages/core/agent-loop/src/agent.ts:98-138]()

---

## Turn Flow and Execution Pipeline

The core agent driver in `dsh-agent-loop` (`ReactLoopAgent`) manages interaction as a flow of turns composed of ordered steps [docs/architecture.md:86-118](), [packages/core/agent-loop/src/agent.ts:120-170]().

### Step Execution Pipeline Illustration
```mermaid
sequenceDiagram
    participant AL as "ReactLoopAgent"
    participant EV as "EventBus (ctx.emit / ctx.waterfall)"
    participant LLM as "LlmRuntime (ctx.llm)"
    participant TR as "ToolRuntime (packages/core/tools)"

    Note over AL,TR: "Turn starts on inbox claim"
    AL->>EV: "agent/pre-step (waterfall)"
    AL->>LLM: "agent/request -> prepareCall()"
    LLM-->>AL: "agent/assistant-stream (chunked token events)"
    AL->>EV: "tools/pre-execute (waterfall)"
    AL->>TR: "executeToolCalls()"
    TR-->>AL: "tool/result"
    AL->>EV: "tools/post-execute (waterfall)"
    Note over AL,TR: "Step ends; check for followup or next step"
```
Sources: [docs/architecture.md:86-118](), [packages/core/agent-loop/src/agent.ts:154-170](), [packages/core/agent-loop/src/tool-calls.ts:1-25]()

---

## Subsystem Navigation

Further exploration of each core component is available in these linked child pages:
- [Cordis Framework & Vendored Dependencies](#2.1) — Plugin lifecycle, service injection, Context declaration merging, and vendored source.
- [Plugin Composition: Profiles, Bundles & Configuration](#2.2) — Profiles, bundles, patch layering, and the configuration catalog.
- [Event Bus & Capability Seams](#2.3) — Event taxonomy, waterfall semantics, and capability seam pattern.

Sources: [docs/architecture.md:1-77](), [packages/core/agent-loop/src/agent.ts:1-171](), [packages/core/agent/src/types.ts:1-88]()

---

