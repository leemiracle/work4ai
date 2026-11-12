<!-- source: DeepWiki mcp.deepwiki.com · repo crewAIInc/crewAI · page 8 CLI and Project Tooling · fetched 2026-11-09 -->

# CLI and Project Tooling

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/edge/ar/concepts/cli.mdx](docs/edge/ar/concepts/cli.mdx)

</details>



This page provides an overview of the `crewai` command-line interface, project scaffolding, and dependency management tooling. For detailed documentation on specific subsystems, refer to the child pages: [CLI Tools and Templates](#8.1), [Checkpointing and Flow Recovery](#8.2), and [Dependency Management with UV](#8.3).

## CLI Tools and Templates

The `crewai` CLI is the primary entry point for developers. It handles project initialization, execution, and lifecycle management. The CLI is packaged separately in the monorepo to maintain a lightweight footprint for the core library.

### Key Commands
The CLI provides a suite of commands to manage the development lifecycle:
- `crewai create`: Scaffolds a new project. It supports two main types: `crew` (agent-centric) and `flow` (event-driven). By default, it creates a JSON-first structure with `crew.jsonc` and `agents/*.jsonc`, but the `--classic` flag can be used for the legacy YAML/Python structure [docs/edge/ar/concepts/cli.mdx:37-55]().
- `crewai run`: The recommended way to execute projects. It automatically detects whether the project is a Crew or a Flow by inspecting the `pyproject.toml` file [docs/edge/ar/concepts/cli.mdx:133-146]().
- `crewai train` & `crewai test`: Used for iterative improvement. Training runs the crew for multiple iterations to save agent performance data, while testing evaluates results against a model like `gpt-4o-mini` [docs/edge/ar/concepts/cli.mdx:77-132]().
- `crewai chat`: Initiates an interactive session where a "chat LLM" (configured via `chat_llm`) prompts the user for necessary inputs before execution [docs/edge/ar/concepts/cli.mdx:148-183]().
- `crewai deploy`: Handles deployment to the CrewAI Agent Management Platform (AMP), including `create`, `push`, and `status` subcommands [docs/edge/ar/concepts/cli.mdx:185-224]().

For details, see [CLI Tools and Templates](#8.1).

**Sources:** [docs/edge/ar/concepts/cli.mdx:17-224]()

### CLI Execution Flow

The following diagram illustrates how CLI commands map to internal framework components and the state management system.

**CLI Execution Flow**
```mermaid
graph TD
    subgraph "Natural Language Space (User Commands)"
        "cmd_run"["crewai run"]
        "cmd_create"["crewai create"]
        "cmd_chat"["crewai chat"]
    end

    subgraph "Code Entity Space (Framework)"
        "CLI_Package"["lib/cli/"]
        "Flow_Class"["crewai.flow.flow.Flow"]
        "Crew_Class"["crewai.crew.Crew"]
        "State_Store"["crewai.state.state_persistence.SQLiteStorage"]
        "UV_Lock"["uv.lock"]
    end

    "cmd_run" --> "CLI_Package"
    "cmd_create" --> "CLI_Package"
    "CLI_Package" -- "Instantiates" --> "Flow_Class"
    "CLI_Package" -- "Instantiates" --> "Crew_Class"
    "Flow_Class" -- "Checkpoints to" --> "State_Store"
    "CLI_Package" -- "Ensures Env via" --> "UV_Lock"
```
**Sources:** [docs/edge/ar/concepts/cli.mdx:37-146]()

## Checkpointing and Flow Recovery

For long-running or complex orchestrations, CrewAI provides a checkpointing system. This is particularly critical for **Flows**, where execution might span multiple Crews or involve human-in-the-loop steps.

### Persistence Mechanism
The system utilizes a SQLite-based persistence layer located in `lib/crewai/src/crewai/state/`. This allows the framework to save the state of a Flow at specific intervals or after specific method executions.
- **`checkpoint_config`**: Defines the storage backend and frequency of saves.
- **`checkpoint_listener`**: Monitors flow events to trigger state persistence.

### Flow Resumption
If a flow is interrupted (e.g., due to a crash or a `HumanFeedbackPending` exception), the CLI and framework can use the saved checkpoints to resume from the last known good state. This is often managed via a Checkpoint TUI (Terminal User Interface) that allows developers to select which state to restore.

For details, see [Checkpointing and Flow Recovery](#8.2).

**Sources:** [docs/edge/ar/concepts/cli.mdx:17-146]()

## Dependency Management with UV

CrewAI standardizes on `uv` for high-performance dependency resolution and virtual environment management.

### The UV Integration
The CLI wraps `uv` commands to ensure that the environment is always synchronized with the `uv.lock` file.
- **Workspace Sources**: In the monorepo, `uv` manages internal package relationships using workspace sources, ensuring local changes are reflected immediately.
- **`crewai install`**: Internally runs `uv sync`, which installs all dependencies and ensures the `uv.lock` file is up to date.
- **`crewai uv add`**: A convenience wrapper for adding new dependencies to a project while handling authentication for the tools repository.

For details, see [Dependency Management with UV](#8.3).

**Sources:** [docs/edge/ar/concepts/cli.mdx:17-224]()

### Project Configuration Mapping

The CLI uses configuration files to bridge high-level intent to specific code instances.

**Configuration to Code Mapping**
```mermaid
graph LR
    subgraph "Configuration Files"
        "Agents_JSONC"["agents/researcher.jsonc"]
        "Crew_JSONC"["crew.jsonc"]
        "PyProject"["pyproject.toml"]
    end

    subgraph "Code Entities"
        "Agent_Factory"["crewai.agent.Agent"]
        "Task_Factory"["crewai.task.Task"]
        "Dep_Manager"["uv sync"]
    end

    "Agents_JSONC" -- "Defines attributes for" --> "Agent_Factory"
    "Crew_JSONC" -- "Defines tasks for" --> "Task_Factory"
    "PyProject" -- "Configures" --> "Dep_Manager"
```
**Sources:** [docs/edge/ar/concepts/cli.mdx:37-183]()

---

