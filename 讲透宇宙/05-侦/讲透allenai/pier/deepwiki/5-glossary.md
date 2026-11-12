<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/pier · page 5 Glossary · fetched 2026-10-26 -->

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [pier/cli.py](pier/cli.py)
- [pier/harbor_bridge.py](pier/harbor_bridge.py)
- [pier/trajectory.py](pier/trajectory.py)

</details>



## Purpose and Scope

This glossary defines core terminology used across `pier` and its underlying `Harbor` engine. It provides technical definitions, data structures, behavioral patterns, and exact code pointers for key concepts such as workspaces, session configuration files, Harbor identifiers, execution modes, trial directories, reward extraction, skill bundles, and capture mechanisms.

Sources:
- `pier/cli.py:1-2165`
- `pier/harbor_bridge.py:1-1304`
- `pier/trajectory.py:1-100`

---

## Core Entities and Data Structures

### Workspace and `.pier/` Directory
A **workspace** is a local directory containing the source files being modified by a coding agent or user. Every active workspace contains a hidden `.pier/` directory managed by `pier` [pier/cli.py:38](). The `.pier/` directory holds session state, trial artifacts, and temporary metadata required to interface with the container runtime or host execution environment.

Sources:
- `pier/cli.py:38-73`
- `README.md:1-154`

### `session.json`
`session.json` is the per-workspace state file stored at `<workspace>/.pier/session.json` [pier/cli.py:54-55](). It serializes configuration parameters including the active agent name, container status, environment variables, base image reference, task reference, and Harbor session mapping. It is read via `_load_session()` [pier/cli.py:65-73]() and written via `_save_session()` [pier/cli.py:58-63]().

Sources:
- `pier/cli.py:54-73`

### Harbor Session ID
The **Harbor session ID** is a unique identifier generated for a container or host execution run. It determines the underlying Docker Compose project name via `get_compose_project()` [pier/harbor_bridge.py:45-51](), which lowercases the session identifier and replaces dots with dashes. The primary container name is derived as `{project}-main-1` [pier/harbor_bridge.py:54-61]().

Sources:
- `pier/harbor_bridge.py:45-82`

### Trial Directory and Trajectory
A **trial directory** is a structured output folder (typically stored under `.pier/trials/`) containing the results of a verification run or an explicit capture action. A **trajectory** captures the sequence of agent interactions, tool outputs, costs, and execution metadata. It is assembled by `assemble_trial()` [pier/trajectory.py:29-99](), writing out `result.json`, `config.json`, and reward metrics.

Sources:
- `pier/trajectory.py:1-100`
- `README.md:105-125`

---

## Execution Modes and Components

### Task-Free Mode
**Task-free mode** is an operational mode where `pier start` is invoked without a Harbor benchmark task reference (e.g., using `--image` on an arbitrary directory) [README.md:18-20,132-134](). In this mode, no task definition or `task.toml` is present; the workspace relies purely on the base Docker image and manual or semi-automated agent invocation.

Sources:
- `README.md:18-35,132-135`

### Verifier and Reward
The **verifier** is the testing subsystem (typically wrapping Harbor's verification runner and scripts like `test.sh`) that evaluates the correctness of the workspace implementation [README.md:61-65,88-89](). The **reward** is the numerical or structured score returned by the verifier (e.g., `{"reward": 1.0}`), stored in `verifier/reward.json` [pier/trajectory.py:48,96-99]().

Sources:
- `pier/harbor_bridge.py:1-21`
- `pier/trajectory.py:1-100`
- `README.md:59-72`

### Skill Bundle and Skills Compose
A **skill bundle** is a collection of instructions and tools (`SKILL.md` and related assets) that can be injected into a coding agent. `pier skills compose` merges multiple skill bundles into a single composite directory for agent consumption [README.md:14-16,11-17]().

Sources:
- `pier/cli.py:1-17`
- `README.md:14-34`

### Compose Override
A **compose override** is a dynamically generated Docker Compose configuration file (written by `_write_mounts_compose()` [pier/harbor_bridge.py:179-202]()) that patches Harbor's default container settings. It injects a `tmpfs` mount over `.pier/` to hide pier session data from the container, configures workspace bind mounts, and maps requested ports [pier/harbor_bridge.py:179-202]().

Sources:
- `pier/harbor_bridge.py:179-202`

### Tee Capture
**Tee capture** refers to stream interception (using tools like `script(1)` or pipe redirection) to capture agent stdout, stderr, and user inputs into log files for trajectory analysis and post-run extraction.

Sources:
- `README.md:1-154`

---

## Architectural Mapping Diagrams

### Diagram 1: Workspace State and Session Management
This diagram maps natural language workspace concepts to the internal Python functions and file entities in `pier/cli.py`.

```mermaid
graph TD
    A["NaturalLanguageWorkspace"] --> B["WorkspaceDirectory"]
    B --> C["HiddenPierFolder[\".pier/\"]"]
    C --> D["SessionConfigFile[\"session.json\"]"]
    
    subgraph CodeEntitySpace
        D --> E["_load_session()"]
        D --> F["_save_session()"]
        B --> G["_find_workspace_from_cwd()"]
        H["_all_workspaces()"] --> I["_index_load()"]
    end

    A -.->|Managed by| E
    A -.->|Managed by| F
```

Sources:
- `pier/cli.py:38-144`

### Diagram 2: Trial Assembly and Trajectory Flow
This diagram illustrates how raw execution artifacts are converted into a standardized Harbor trial structure via `trajectory.py` and `harbor_bridge.py`.

```mermaid
graph TD
    A["ExecutionRun[\"pier verify\"]"] --> B["RawContainerOutputs"]
    B --> C["VerifierReward[\"reward.json\"]"]
    B --> D["AgentLogsAndArtifacts"]
    
    subgraph CodeEntitySpace
        C --> E["assemble_trial()"]
        D --> E
        E --> F["build_trial_result_json()"]
        E --> G["write_trial_config_json()"]
        F --> H["TrialResultOutput[\"result.json\"]"]
        G --> I["TrialConfigOutput[\"config.json\"]"]
    end
```

Sources:
- `pier/trajectory.py:29-100`
- `pier/harbor_bridge.py:1-21`