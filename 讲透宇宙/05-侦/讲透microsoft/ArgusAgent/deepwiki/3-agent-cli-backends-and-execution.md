<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/ArgusAgent · page 3 Agent CLI Backends and Execution · fetched 2026-10-26 -->

# Agent CLI Backends and Execution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [argus_skill/agent_cli/__init__.py](argus_skill/agent_cli/__init__.py)
- [argus_skill/agent_cli/agent_cli_runner.py](argus_skill/agent_cli/agent_cli_runner.py)
- [argus_skill/agent_cli/runner_backend.py](argus_skill/agent_cli/runner_backend.py)

</details>



## Purpose and Scope

This page provides a high-level overview of how Argus drives external coding agent Command Line Interfaces (CLIs)—such as Copilot, Codex, Claude Code, Cursor, Pi, OpenCode, Grok, Qoder, and DSH—through a uniform Python adapter and process-control framework. 

Argus acts as an orchestration harness over these heterogeneous developer agents, standardizing prompt delivery, event consumption, process lifecycle management, sandbox confinement, and resource tracking.

For granular details on specific sub-systems, refer to the child pages:
- [agent_cli Runner Internals](#3.1) — Covers `argus_skill/agent_cli`: runner backend selection, prompt delivery, process control, idle watchdogs, ACP routing, Copilot ACP/home handling, OpenCode recovery, sandbox commands, models registry, and DSH overlays.
- [Adapter Execution Pipeline](#3.2) — Covers `argus_skill/adapters/agent_cli_backend`: admission, context, spawn, finalize, options, results, IO logging, budget monitoring, memory backends, and streaming progress.
- [Tools, Subagents and Resource Ledger](#3.3) — Covers `argus_skill/tools`: subagent pools, team execution, GPU leases/ownership, capability vaults, resource ledgers, Lean checking, Jacobian bridges, PDF chat, and PPT master tools.

Sources: [argus_skill/agent_cli/__init__.py:1-11](), [argus_skill/agent_cli/agent_cli_runner.py:1-118]()

---

## 3.1. Agent CLI Runner Subsystem Overview

The low-level driver package `argus_skill/agent_cli` is responsible for launching and supervising external CLI processes without eager submodule imports [argus_skill/agent_cli/__init__.py:1-11](). At its center is `AgentCliRunner`, which orchestrates execution phases by composing multiple specialized mixin classes [argus_skill/agent_cli/agent_cli_runner.py:93-118]().

Supported backends are enumerated in `RunnerBackend` (`codex`, `claude`, `copilot`, `cursor`, `opencode`, `pi`, `grok`, `qoder`, `dsh`), with `codex` acting as the default [argus_skill/agent_cli/runner_backend.py:9-38](). Certain families, such as `qoder`, share command builders and event schemas with `claude` (`CLAUDE_FAMILY`) [argus_skill/agent_cli/runner_backend.py:48-54]().

```mermaid
graph TD
    NaturalLanguageSpace["Natural Language Space: Agent CLIs"] --> CodeEntitySpace["Code Entity Space: AgentCliRunner"]
    
    subgraph "argus_skill/agent_cli"
        CodeEntitySpace --> AcpRoutingMixin["AcpRoutingMixin: argus_skill/agent_cli/_acp_routing.py"]
        CodeEntitySpace --> RunExecMixin["RunExecMixin: argus_skill/agent_cli/_run_exec.py"]
        CodeEntitySpace --> CommandBuilderMixin["CommandBuilderMixin: argus_skill/agent_cli/_sandbox_commands.py"]
        CodeEntitySpace --> PromptDeliveryMixin["PromptDeliveryMixin: argus_skill/agent_cli/_prompt_delivery.py"]
        CodeEntitySpace --> EventConsumerMixin["EventConsumerMixin: argus_skill/agent_cli/_event_consumers.py"]
        CodeEntitySpace --> OpenCodeRecoveryMixin["OpenCodeRecoveryMixin: argus_skill/agent_cli/_opencode_recovery.py"]
        CodeEntitySpace --> ProcessControlMixin["ProcessControlMixin: argus_skill/agent_cli/_process_control.py"]
    end

    Sources: [argus_skill/agent_cli/agent_cli_runner.py:93-118](), [argus_skill/agent_cli/runner_backend.py:9-38]()
```

For complete implementation details on process isolation, watchdogs, sandbox compilation, and model registries, see [agent_cli Runner Internals](#3.1).

Sources: [argus_skill/agent_cli/__init__.py:1-11](), [argus_skill/agent_cli/agent_cli_runner.py:1-118](), [argus_skill/agent_cli/runner_backend.py:9-38]()

---

## 3.2. Adapter Execution Pipeline Overview

The `argus_skill/adapters/agent_cli_backend` module bridges the high-level application orchestrator with the low-level `AgentCliRunner`. It provides uniform admission criteria, context assembly, process spawning, result finalization, and budget monitoring.

```mermaid
graph TD
    NaturalLanguageSpace["Natural Language Space: Agent Execution Request"] --> CodeEntitySpace["Code Entity Space: RunnerBackend Adapter"]

    subgraph "argus_skill/adapters/agent_cli_backend"
        CodeEntitySpace --> Admission["Admission and Context Assembly"]
        Admission --> Spawn["Process Spawn and IO Logging"]
        Spawn --> BudgetMonitor["Budget Monitoring and Stream Progress"]
        BudgetMonitor --> Finalize["Result Finalization"]
    end

    Sources: [argus_skill/agent_cli/agent_cli_runner.py:53-91]()
```

For details on configuration options, IO capturing, memory backends, and streaming progress callbacks, see [Adapter Execution Pipeline](#3.2).

Sources: [argus_skill/agent_cli/agent_cli_runner.py:53-91]()

---

## 3.3. Tools, Subagents and Resource Ledger Overview

The `argus_skill/tools` package equips coding agents with advanced operational capabilities. It manages a pool of subagents, coordinates team execution, tracks GPU leases and ownership loads, enforces capability vaults, and logs resource expenditures.

For details on Lean proof checking, Jacobian mathematical bridges, PDF chat parsing, and PPT master generation tools, see [Tools, Subagents and Resource Ledger](#3.3).

Sources: [argus_skill/agent_cli/__init__.py:1-11]()

---

