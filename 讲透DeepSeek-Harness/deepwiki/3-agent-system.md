> 来源: [https://deepwiki.com/deepseek-ai/deepseek-harness/3-agent-system](https://deepwiki.com/deepseek-ai/deepseek-harness/3-agent-system)
> DeepWiki deepseek-ai/deepseek-harness

# Agent System

  Relevant source files 
 - [docs/architecture.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/architecture.i18n.yaml)
 - [docs/architecture.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/architecture.md?plain=1)
 - [docs/architecture.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/architecture.zh.md?plain=1)
 - [docs/persistence-catalog.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/persistence-catalog.i18n.yaml)
 - [docs/persistence-catalog.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/persistence-catalog.md?plain=1)
 - [docs/persistence-catalog.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/persistence-catalog.zh.md?plain=1)
 - [docs/tool-catalog.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/tool-catalog.i18n.yaml)
 - [docs/tool-catalog.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/tool-catalog.md?plain=1)
 - [docs/tool-catalog.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/tool-catalog.zh.md?plain=1)
 - [packages/core/agent-loop/README.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/README.md?plain=1)
 - [packages/core/agent-loop/src/agent.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/src/agent.ts)
 - [packages/core/agent-loop/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/src/index.ts)
 - [packages/core/agent-loop/src/tool-calls.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/src/tool-calls.ts)
 - [packages/core/agent-loop/tests/agent.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/tests/agent.spec.ts)
 - [packages/core/agent-loop/tests/cancel.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/tests/cancel.spec.ts)
 - [packages/core/agent-loop/tests/config-session-id.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/tests/config-session-id.spec.ts)
 - [packages/core/agent-loop/tests/contract-regressions.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/tests/contract-regressions.spec.ts)
 - [packages/core/agent-loop/tests/coverage-edges.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/tests/coverage-edges.spec.ts)
 - [packages/core/agent-loop/tests/interception.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/tests/interception.spec.ts)
 - [packages/core/agent-loop/tests/loop.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/tests/loop.spec.ts)
 - [packages/core/agent-loop/tests/resume.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/tests/resume.spec.ts)
 - [packages/core/agent-loop/tests/tool-calls.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/tests/tool-calls.spec.ts)
 - [packages/core/agent-tool-presentation/README.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-tool-presentation/README.i18n.yaml)
 - [packages/core/agent-tool-presentation/README.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-tool-presentation/README.md?plain=1)
 - [packages/core/agent-tool-presentation/README.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-tool-presentation/README.zh.md?plain=1)
 - [packages/core/agent/README.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent/README.md?plain=1)
 - [packages/core/agent/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent/src/index.ts)
 - [packages/core/agent/src/types.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent/src/types.ts)
 - [packages/core/agent/tests/agent.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent/tests/agent.spec.ts)
 - [packages/core/session/README.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/session/README.i18n.yaml)
 - [packages/core/session/README.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/session/README.md?plain=1)
 - [packages/core/session/README.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/session/README.zh.md?plain=1)
 - [packages/core/session/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/session/src/index.ts)
 - [packages/core/session/src/surface.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/session/src/surface.ts)
 - [packages/core/session/src/types.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/session/src/types.ts)
 - [packages/core/session/tests/session.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/session/tests/session.spec.ts)
 - [packages/core/session/tests/surface.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/session/tests/surface.spec.ts)
 - [packages/core/tools/README.i18n.yaml](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/tools/README.i18n.yaml)
 - [packages/core/tools/README.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/tools/README.md?plain=1)
 - [packages/core/tools/README.zh.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/tools/README.zh.md?plain=1)
 - [packages/core/tools/src/index.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/tools/src/index.ts)
 - [packages/core/tools/src/py-types.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/tools/src/py-types.ts)
 - [packages/core/tools/src/ts-types.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/tools/src/ts-types.ts)
 - [packages/core/tools/tests/execution-mode.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/tools/tests/execution-mode.spec.ts)
 - [packages/core/tools/tests/gen-tool-catalog.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/tools/tests/gen-tool-catalog.spec.ts)
 - [packages/core/tools/tests/py-types.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/tools/tests/py-types.spec.ts)
 - [packages/core/tools/tests/tools.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/tools/tests/tools.spec.ts)
 - [packages/core/tools/tests/ts-types.spec.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/tools/tests/ts-types.spec.ts)
 - [scripts/gen-tool-catalog.ts](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/scripts/gen-tool-catalog.ts)
 - [snapshots/session/both-mode-turn/system-prompt.expected.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/snapshots/session/both-mode-turn/system-prompt.expected.md?plain=1)
 - [snapshots/session/cordis-inspect-jsdoc/system-prompt.expected.md](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/snapshots/session/cordis-inspect-jsdoc/system-prompt.expected.md?plain=1)
 
  The Agent System is the core orchestration layer of DeepSeek Harness. It manages the lifecycle of autonomous agents, their interaction with LLMs, and the execution of tools. The system is built on a plugin-based architecture using the **Cordis** framework, where the agent loop itself is a replaceable service.

 
## Architectural Overview

 Agents in `dsh` are driven by a turn-based state machine. A **Turn** represents a complete cycle of work, starting from a user input and ending when no further actions are required. Each turn consists of one or more **Steps**, where a step is defined as a single LLM request followed by the execution of any resulting tool calls [docs/architecture.md75-82](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/architecture.md?plain=1#L75-L82)

 
### Core Components

 
| Service | Context Key | Responsibility |
|---|---|---|
| AgentRegistry | ctx.agents | Tracks live agents and carries the initiating initiator scope packages/core/agent/README.md9-11 |
| AgentLoop | ctx.agentLoop | The concrete implementation of the agent driver and factory packages/core/agent-loop/README.md9-10 |
| ReactLoopAgent | N/A | The default internal implementation of the Agent interface packages/core/agent-loop/src/agent.ts69-76 |

 
### Entity Mapping: Natural Language to Code

 The following diagram maps high-level agent concepts to their corresponding classes and service keys in the codebase.

 Agent System Entity Map

 
```

```

 Sources: [packages/core/agent-loop/src/agent.ts69-104](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/src/agent.ts#L69-L104) [packages/core/agent/README.md9-15](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent/README.md?plain=1#L9-L15) [packages/core/agent-loop/README.md44-45](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/README.md?plain=1#L44-L45)

 
## Agent Lifecycle & The Loop

 The `AgentLoop` service (provided by `dsh-agent-loop`) manages the creation and resumption of agents. Agents are identified by a `SessionId`, which is shared with their durable session log [packages/core/agent-loop/README.md17-19](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/README.md?plain=1#L17-L19)

 The loop follows a `React` pattern managed by `ReactLoopAgent`:

 
 - **Claim**: Claim input from the `Inbox` [packages/core/agent-loop/src/agent.ts120-125](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/src/agent.ts#L120-L125)
 - **Assemble**: Gather system prompts and tool schemas via `assembleContextFor` [packages/core/agent/src/index.ts100](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent/src/index.ts#L100-L100)
 - **Request**: Call the LLM via `ctx.llm` using `agent/request` [docs/architecture.md86](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/architecture.md?plain=1#L86-L86)
 - **Execute**: Run tools via `ctx.tools` [docs/architecture.md87](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/architecture.md?plain=1#L87-L87)
 - **Repeat**: If tools owe another request, start a new step [docs/architecture.md89](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/architecture.md?plain=1#L89-L89)
 
 For a deep dive into the state machine, cancellation, and turn boundaries, see **[Agent Loop & Lifecycle](https://deepwiki.com/deepseek-ai/deepseek-harness/3.1-agent-loop-and-lifecycle)**.

 Sources: [docs/architecture.md75-93](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/architecture.md?plain=1#L75-L93) [packages/core/agent-loop/src/agent.ts120-125](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/src/agent.ts#L120-L125) [packages/core/agent-loop/README.md13-26](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/README.md?plain=1#L13-L26)

 
## Tool Registry & Execution

 Capabilities are exposed to agents as tools. The `ToolRuntime` service (`ctx.tools`) manages a scoped registry where tools can be registered globally or for specific agents [packages/core/tools/src/index.ts137-140](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/tools/src/index.ts#L137-L140) The execution pipeline is guarded by a waterfall of events: `tools/pre-execute`, `tools/execute`, and `tools/post-execute` [packages/core/tools/src/index.ts152-164](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/tools/src/index.ts#L152-L164)

 For details on tool registration, parallel execution, and "Code Mode," see **[Tool Registry & Execution Pipeline (#3.2)]**.

 Sources: [packages/core/tools/src/index.ts137-164](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/tools/src/index.ts#L137-L164) [packages/core/tools/README.md10-12](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/tools/README.md?plain=1#L10-L12)

 
## Session Log & Persistence

 Every action taken by an agent is recorded in an append-only `SessionEvent` log. This log is the "source of truth" for the agent's interaction history; the model's history is projected from this log using `deriveMessages()` [packages/core/session/src/index.ts19-20](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/session/src/index.ts#L19-L20) This ensures that any agent state can be reconstructed for resumption or forking [packages/core/session/src/index.ts17-18](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/session/src/index.ts#L17-L18)

 For information on the event schema, lineage, and persistence backends (JSONL/SQLite), see **[Session Log & Persistence (#3.3)]**.

 Sources: [packages/core/session/src/index.ts19-20](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/session/src/index.ts#L19-L20) [packages/core/session/src/index.ts17-18](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/session/src/index.ts#L17-L18) [docs/persistence-catalog.md10](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/persistence-catalog.md?plain=1#L10-L10)

 
## Subagent Orchestration

 Agents can delegate tasks to subagents. This is handled via a capability seam (`ctx.subagents`), allowing for various implementations—from in-process child agents to out-of-process agents communicating via the **Agent Client Protocol (ACP)** [docs/tool-catalog.md19](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/tool-catalog.md?plain=1#L19-L19) Runtime ownership is tracked via `ctx.agents.isOwnedBy()` [packages/core/agent/README.md32](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent/README.md?plain=1#L32-L32)

 For orchestration policies and delegation mechanisms, see **[Subagent Orchestration (#3.4)]**.

 Sources: [packages/core/agent/README.md32](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent/README.md?plain=1#L32-L32) [docs/tool-catalog.md19](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/tool-catalog.md?plain=1#L19-L19)

 
## LLM Adapters

 The agent loop is decoupled from specific LLM providers through the `LlmRuntime` (`ctx.llm`). Adapters translate the internal `Message` and `StreamChunk` vocabulary into provider-specific formats [packages/core/agent-loop/src/agent.ts19-27](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/src/agent.ts#L19-L27)

 For details on streaming, block assembly, and adapter registration, see **[LLM Adapters & Streaming (#3.5)]**.

 Sources: [packages/core/agent-loop/src/agent.ts19-27](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/src/agent.ts#L19-L27) [docs/architecture.md61](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/architecture.md?plain=1#L61-L61)

 
## Service Interactions

 The following diagram illustrates how the `AgentLoop` orchestrates various services during a single step.

 Agent Step Orchestration

 
```

```

 Sources: [docs/architecture.md75-93](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/docs/architecture.md?plain=1#L75-L93) [packages/core/agent-loop/src/agent.ts18-37](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/src/agent.ts#L18-L37) [packages/core/agent-loop/src/tool-calls.ts36](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/agent-loop/src/tool-calls.ts#L36-L36) [packages/core/session/src/index.ts19-20](https://github.com/deepseek-ai/deepseek-harness/blob/cd5ef814/packages/core/session/src/index.ts#L19-L20)
