<!-- source: DeepWiki mcp.deepwiki.com · repo bytedance/trae-agent · page 9 Glossary · fetched 2026-10-29 -->

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/pre-commit.yml](.github/workflows/pre-commit.yml)
- [.github/workflows/unit-test.yml](.github/workflows/unit-test.yml)
- [Makefile](Makefile)
- [README.md](README.md)
- [evaluation/patch_selection/README.md](evaluation/patch_selection/README.md)
- [tests/tools/test_bash_tool.py](tests/tools/test_bash_tool.py)
- [tests/utils/test_config.py](tests/utils/test_config.py)
- [trae_agent/agent/agent_basics.py](trae_agent/agent/agent_basics.py)
- [trae_agent/agent/trae_agent.py](trae_agent/agent/trae_agent.py)
- [trae_agent/tools/base.py](trae_agent/tools/base.py)
- [trae_agent/tools/bash_tool.py](trae_agent/tools/bash_tool.py)
- [trae_agent/tools/ckg/base.py](trae_agent/tools/ckg/base.py)
- [trae_agent/tools/ckg/ckg_database.py](trae_agent/tools/ckg/ckg_database.py)
- [trae_agent/utils/config.py](trae_agent/utils/config.py)
- [trae_agent/utils/constants.py](trae_agent/utils/constants.py)
- [trae_agent/utils/legacy_config.py](trae_agent/utils/legacy_config.py)
- [trae_agent/utils/trajectory_recorder.py](trae_agent/utils/trajectory_recorder.py)
- [trae_config.yaml.example](trae_config.yaml.example)

</details>



This glossary defines the core concepts, terminology, and technical components specific to the **Trae Agent** codebase. It is intended to help onboarding engineers navigate the system's architecture and implementation details.

## Core Agent Concepts

### TraeAgent
The primary implementation of the software engineering agent. It extends `BaseAgent` and specializes in repository-level tasks such as bug fixing, feature implementation, and code refactoring. It manages the lifecycle of a task, including tool initialization (including MCP), environment setup, and git diff generation.
*   **Implementation:** [trae_agent/agent/trae_agent.py:30-32]()
*   **Key Methods:** `new_task` [trae_agent/agent/trae_agent.py:103-109](), `execute_task` [trae_agent/agent/trae_agent.py:156-158](), `initialise_mcp` [trae_agent/agent/trae_agent.py:65-66]().

### AgentExecution & AgentStep
`AgentExecution` encapsulates the entire lifecycle of a single task, while `AgentStep` represents an individual iteration (turn) within that execution. Each step transitions through various `AgentStepState` values like `THINKING`, `CALLING_TOOL`, and `REFLECTING`.
*   **Implementation:** [trae_agent/agent/agent_basics.py:39-45](), [trae_agent/agent/agent_basics.py:67-73]()
*   **States:** [trae_agent/agent/agent_basics.py:19-26]()

### Trajectory
A detailed record of the agent's actions, LLM interactions, and tool outputs saved during execution. It is used for debugging, auditing, and analysis.
*   **Recorder:** `TrajectoryRecorder` in [trae_agent/utils/trajectory_recorder.py:20-21]()
*   **Data Structure:** [trae_agent/utils/trajectory_recorder.py:39-51]()

---

## Tool System Terminology

### Tool
The base abstract class for all capabilities provided to the agent. Every tool must define its name, description, parameters (using `ToolParameter`), and an `execute` method.
*   **Implementation:** [trae_agent/tools/base.py:74-75]()
*   **Registration:** Tools are typically registered in a `tools_registry` and initialized based on the agent configuration [trae_agent/agent/trae_agent.py:117-119]().

### ToolExecutor
A manager class that handles the mapping and execution of `ToolCall` objects. it normalizes tool names (lowercase, no underscores) to ensure robust matching between LLM output and internal tool instances.
*   **Implementation:** [trae_agent/tools/base.py:182-183]()
*   **Normalization:** [trae_agent/tools/base.py:195-197]()

### MCP (Model Context Protocol)
A protocol that allows Trae Agent to connect to external servers to discover and use additional tools dynamically. This enables extensibility without modifying the core agent code.
*   **Client:** `MCPClient` in [trae_agent/agent/trae_agent.py:19]()
*   **Discovery:** `discover_mcp_tools` [trae_agent/agent/trae_agent.py:72-73]()

### Bash Session
A persistent shell environment maintained by the `BashTool`. Unlike simple subprocess calls, `_BashSession` keeps the shell open across multiple tool calls to preserve environment variables and working directories.
*   **Implementation:** [trae_agent/tools/bash_tool.py:19-20]()
*   **Sentinel:** Uses a unique banner to detect command completion and capture exit codes [trae_agent/tools/bash_tool.py:28-29]().

---

## Configuration & LLM Space

### ModelProvider & ModelConfig
`ModelProvider` stores credentials and endpoint information (API key, base URL) for LLM services. `ModelConfig` defines model-specific hyperparameters like temperature, max tokens, and tool-calling support.
*   **Implementation:** [trae_agent/utils/config.py:17-21](), [trae_agent/utils/config.py:30-33]()

### Lakeview
A feature that provides short, concise summarization of agent steps. It uses a separate LLM call (configured via `LakeviewConfig`) to condense complex trajectories into human-readable summaries.
*   **Configuration:** [trae_agent/utils/config.py:185-192]()
*   **Usage:** [trae_agent/agent/trae_agent.py:56-57]()

---

## Data Flow Diagrams

### From Task to Execution
The following diagram illustrates how natural language input is transformed into code entities and executed.

**Task Initialization Flow**
```mermaid
graph TD
    "User Instruction" -- "trae-cli run" --> CLI["trae_cli/main.py"]
    CLI -- "Load Config" --> Config["trae_agent/utils/config.py:Config"]
    Config -- "Init" --> Agent["trae_agent/agent/trae_agent.py:TraeAgent"]
    Agent -- "new_task()" --> Prompt["trae_agent/prompt/agent_prompt.py:TRAE_AGENT_SYSTEM_PROMPT"]
    Agent -- "discover_mcp_tools()" --> MCP["trae_agent/utils/mcp_client.py:MCPClient"]
    Agent -- "execute_task()" --> Loop["Agent Loop"]
    Loop -- "LLM Interaction" --> LLM["trae_agent/utils/llm_clients/"]
    Loop -- "record_agent_step()" --> Rec["trae_agent/utils/trajectory_recorder.py:TrajectoryRecorder"]
```
**Sources:** [trae_agent/agent/trae_agent.py:65-170](), [trae_agent/utils/config.py:194-204](), [trae_agent/utils/trajectory_recorder.py:77-128]()

### Tool Execution Logic
This diagram bridges the "Tool Call" received from an LLM to the specific implementation in the codebase.

**Tool Dispatch Mechanism**
```mermaid
graph LR
    "LLM Response" -- "contains" --> TC["trae_agent/tools/base.py:ToolCall"]
    TC -- "name & arguments" --> Exec["trae_agent/tools/base.py:ToolExecutor"]
    Exec -- "_normalize_name()" --> Map["_tool_map"]
    Map -- "matches" --> ToolImpl["trae_agent/tools/base.py:Tool"]
    
    subgraph Implementations
        ToolImpl -.-> Bash["trae_agent/tools/bash_tool.py:BashTool"]
        ToolImpl -.-> Edit["trae_agent/tools/text_editor.py"]
        ToolImpl -.-> MCPT["trae_agent/agent/trae_agent.py:mcp_tools"]
    end
    
    ToolImpl -- "execute()" --> Res["trae_agent/tools/base.py:ToolExecResult"]
    Res -- "wrap" --> Final["trae_agent/tools/base.py:ToolResult"]
```
**Sources:** [trae_agent/tools/base.py:182-225](), [trae_agent/agent/trae_agent.py:21-27](), [trae_agent/tools/bash_tool.py:162-170]()

---

## Glossary Table

| Term | Definition | Code Pointer |
| :--- | :--- | :--- |
| **must_patch** | A flag indicating if the agent is required to produce a git patch file upon completion. | [trae_agent/agent/trae_agent.py:50]() |
| **Trajectory** | The JSON file containing the full history of an agent's run. | [trae_agent/utils/trajectory_recorder.py:33]() |
| **Sequential Thinking** | A specialized tool that allows the agent to break down complex problems into steps. | [trae_agent/agent/trae_agent.py:23]() |
| **Base URL** | The endpoint used for LLM API calls, allowing for proxies or local providers like Ollama. | [trae_agent/utils/config.py:25]() |
| **Sentinel** | A specific string used in the `BashTool` to mark the end of a command's output in a stream. | [trae_agent/tools/bash_tool.py:28]() |
| **Project Path** | The local directory where the agent executes its software engineering tasks. | [trae_agent/agent/trae_agent.py:48]() |

**Sources:** [trae_agent/agent/trae_agent.py:21-51](), [trae_agent/utils/trajectory_recorder.py:33](), [trae_agent/utils/config.py:25](), [trae_agent/tools/bash_tool.py:28]()