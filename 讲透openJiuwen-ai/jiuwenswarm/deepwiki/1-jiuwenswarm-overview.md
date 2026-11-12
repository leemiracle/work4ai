<!-- source: DeepWiki mcp.deepwiki.com · repo openJiuwen-ai/jiuwenswarm · page 1 JiuwenSwarm Overview · fetched 2026-11-02 -->

# JiuwenSwarm Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README_CN.md](README_CN.md)
- [docs/en/InstallGuide.md](docs/en/InstallGuide.md)
- [docs/en/Page-Overview.md](docs/en/Page-Overview.md)
- [docs/en/Quickstart_tui.md](docs/en/Quickstart_tui.md)
- [docs/en/README.md](docs/en/README.md)
- [docs/en/SUMMARY.md](docs/en/SUMMARY.md)
- [docs/en/install.md](docs/en/install.md)
- [docs/zh/Quickstart_tui.md](docs/zh/Quickstart_tui.md)
- [docs/zh/README.md](docs/zh/README.md)
- [docs/zh/SUMMARY.md](docs/zh/SUMMARY.md)
- [jiuwenswarm/common/config.py](jiuwenswarm/common/config.py)
- [pyproject.toml](pyproject.toml)
- [tests/unit_tests/test_app_web_handlers.py](tests/unit_tests/test_app_web_handlers.py)
- [tests/unit_tests/test_config.py](tests/unit_tests/test_config.py)
- [uv.lock](uv.lock)

</details>



**JiuwenSwarm** is an intelligent multi-agent framework built in Python, designed to act as a self-hosted AI butler [README.md:3-15](). It leverages a "swarm" architecture where multiple intelligent agents collaborate to execute complex tasks, ranging from general assistance to autonomous coding and multi-agent team coordination [README.md:15-17]().

The system is designed for high data sovereignty, supporting self-hosted deployment and integration with diverse platforms such as **Huawei Cloud MaaS**, **Xiaoyi Open Platform**, and various Instant Messaging (IM) channels [README.md:19-22]().

## System Architecture

JiuwenSwarm utilizes a split-process architecture to separate concerns between agent intelligence and communication management. The system is primarily composed of the **AgentServer** and the **Gateway** [pyproject.toml:72-73]().

*   **AgentServer**: The core execution engine where the LLM logic, tool orchestration, and agent modes (Agent, Code, Team) reside. It is launched via `jiuwenswarm-agentserver` [pyproject.toml:72]().
*   **Gateway**: The communication hub that routes messages between external channels (Web, TUI, IM platforms) and the AgentServer using the **E2A (External-to-Agent)** protocol. It is launched via `jiuwenswarm-gateway` [pyproject.toml:73]().

### High-Level Process Interaction
The following diagram illustrates how user requests move from "Natural Language Space" (Channels) into "Code Entity Space" (Internal Services).

**Diagram: System Entry and Routing**
```mermaid
graph TD
    subgraph "Natural Language Space (Channels)"
        [Web_UI] --> [app_web.py]
        [IM_Platforms] --> [channel_manager]
        [TUI_Frontend] --> [app_acp.py]
    end

    subgraph "Gateway Process (app_gateway.py)"
        [app_web.py] -- "E2A Protocol" --> [MessageHandler]
        [channel_manager] --> [MessageHandler]
        [app_acp.py] --> [MessageHandler]
        [MessageHandler] --> [SessionMap]
    end

    subgraph "AgentServer Process (app_agentserver.py)"
        [SessionMap] -- "WebSocket" --> [AgentWebSocketServer]
        [AgentWebSocketServer] --> [JiuWenClaw]
        [JiuWenClaw] --> [ModeHarness]
    end
```
**Sources:** [pyproject.toml:70-82](), [jiuwenswarm/common/config.py:106-112]()

## Key Capabilities

### 1. Multi-Mode Operation
JiuwenSwarm operates in specialized modes tailored for different task types:
*   **Agent Mode**: General-purpose assistance using ReAct loops.
*   **Code Mode**: Specialized for software development, utilizing specialized rails like `CodingMemoryRail` and `ProjectMemoryRail`.
*   **Team Mode**: Orchestrates multiple agents with leader/teammate hierarchies for complex project execution, supporting distributed deployments [pyproject.toml:49-53]().

### 2. Autonomous Evolution
The system features a **Skill Self-Evolution** mechanism. When users provide feedback or errors occur, the system can automatically refine its underlying skills based on feedback [README.md:31-34]().

### 3. Memory & Context
JiuwenSwarm employs a multi-layered memory system including:
*   **Short-term Project Memory**: Contextual information derived from local workspace files.
*   **Long-term Memory (LTM)**: Persistent storage using `chromadb`, `pgvector`, or `sqlite-vec` [pyproject.toml:16-39]().
*   **Forbidden Memory**: A security filter that prevents the storage of sensitive patterns.

### 4. Communication Channels
The framework supports a wide array of interfaces:
*   **Web**: A FastAPI-based web server [pyproject.toml:74]().
*   **TUI**: A terminal-based interface for developer workflows, launched via `jiuwenswarm-tui` [pyproject.toml:78]().
*   **IM Channels**: Native support for **Feishu/Lark**, **WeCom**, **Telegram**, **Discord**, and **DingTalk** [pyproject.toml:26-29]().

**Diagram: Memory Subsystem Integration**
```mermaid
graph LR
    subgraph "Code Entity Space"
        [JiuWenClaw] --> [Rails_System]
        [Rails_System] --> [CodingMemoryRail]
        [Rails_System] --> [ContextProcessorRail]
    end

    subgraph "Storage & Providers"
        [CodingMemoryRail] --> [sqlite_vec]
        [ContextProcessorRail] --> [MemoryIndexManager]
        [MemoryIndexManager] --> [chromadb]
        [MemoryIndexManager] --> [pgvector]
    end
```
**Sources:** [pyproject.toml:16-39](), [jiuwenswarm/common/config.py:106-112]()

## Configuration and Setup

JiuwenSwarm is managed via environment variables and YAML configuration:
1.  **Config Management**: The `jiuwenswarm.common.config` module handles loading and resolving environment variables within the configuration [jiuwenswarm/common/config.py:35-76]().
2.  **Initialization**: The `jiuwenswarm-init` command sets up the workspace, resources, and `.env.template` [pyproject.toml:76]().
3.  **Startup**: The `jiuwenswarm-start` command launches the necessary services [pyproject.toml:75]().

For detailed instructions on setting up your environment, see **[Getting Started](#1.1)**.
For a complete breakdown of configuration options, see **[Configuration Reference](#1.2)**.

## Documentation Map

*   **[Getting Started](#1.1)**: Installation via `pip` or source, and initial workspace setup using `jiuwenswarm-init`.
*   **[Configuration Reference](#1.2)**: Detailed guide to `config.yaml`, environment variables, and model provider settings.
*   **Core Architecture**: (Section 2) Deep dive into the Gateway, AgentServer, and E2A protocol.
*   **Agent Modes**: (Section 3) Details on Code, Team, and Plan modes.
*   **Memory & Skills**: (Sections 4 & 5) Exploration of the indexing system and skill evolution.

**Sources:** [README.md:103-137](), [docs/en/SUMMARY.md:1-41]()

---

