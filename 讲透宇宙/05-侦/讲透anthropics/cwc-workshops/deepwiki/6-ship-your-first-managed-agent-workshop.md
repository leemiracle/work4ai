<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/cwc-workshops · page 6 Ship Your First Managed Agent Workshop · fetched 2026-10-26 -->

# Ship Your First Managed Agent Workshop

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



The **Ship Your First Managed Agent** workshop is a hands-on introduction to the Claude Managed Agents (CMA) platform. Participants take on the role of a Site Reliability Engineer (SRE) tasked with resolving "Incident-2277." The workshop provides a pre-built Streamlit dashboard that is initially "offline." To restore service, participants must implement seven core functions in `agent.py` that interface with the Managed Agents API to create resources, manage sandboxed environments, and stream agent responses.

By the end of the workshop, the SRE Agent is capable of grepping through a 70,000-line log file within its secure sandbox, executing custom tools to query local metrics, and identifying the specific commit that caused a production regression [README.md:15-15]().

### Core Managed Agents Resources
The workshop centers on the four primary resources of the Managed Agents lifecycle:
1.  **Agent**: The persistent configuration, including the system prompt and model selection.
2.  **Environment**: The sandboxed execution space where files (like logs) are stored and code is executed.
3.  **Session**: A stateful interaction instance that binds an Agent to an Environment.
4.  **Events**: The streaming communication channel for messages, tool calls, and results.

### System Architecture

The following diagram illustrates how the workshop's Python entities map to the Managed Agents infrastructure.

**SRE Agent System Mapping**
```mermaid
graph TD
    subgraph "Local Workspace (Natural Language Space)"
        "Dashboard UI [app.py]" -- "User Query" --> "Agent Orchestrator [agent.py]"
        "Agent Orchestrator [agent.py]" -- "Local Data" --> "Incident Fixtures [data/]"
    end

    subgraph "Claude Managed Agents (Code Entity Space)"
        "Agent Orchestrator [agent.py]" -- "setup_agent()" --> "Agent Resource"
        "Agent Orchestrator [agent.py]" -- "setup_environment()" --> "Environment Resource"
        "Agent Orchestrator [agent.py]" -- "start_session()" --> "Session Resource"
        "Session Resource" -- "stream_reply()" --> "Events Stream"
    end

    subgraph "Sandboxed Execution"
        "Environment Resource" -- "upload_log()" --> "File System [/home/user/]"
        "Events Stream" -- "handle_tool()" --> "Custom Tool Execution"
    end
```
Sources: [README.md:15-15](), [ship-your-first-managed-agent/agent.py:1-100]()

---

### SRE Agent: Implementation Guide
The implementation phase focuses on `agent.py`, where participants fill in the logic for seven specific functions. These functions bridge the local Streamlit application with the remote Anthropic infrastructure. The workshop provides a `provided.py` file containing the necessary system prompts, tool definitions, and infrastructure scaffolding to ensure participants can focus on the API integration.

Key implementation milestones include:
*   **Provisioning**: Creating the `Agent` and `Environment` resources.
*   **Data Ingestion**: Using `upload_log()` to move the 70k-line `app.log` into the agent's sandbox.
*   **Interaction**: Implementing `start_session()` and `stream_reply()` to handle the real-time SRE investigation.
*   **Tooling**: Connecting `handle_tool()` to local data sources like `metrics.json` and `deploys.json`.

For a step-by-step walkthrough of these functions and the `e2e.py` test suite, see **[SRE Agent: Implementation Guide](#6.1)**.

Sources: [README.md:15-15](), [ship-your-first-managed-agent/agent.py:1-100]()

---

### SRE Agent: Dashboard UI and Data Layer
The workshop includes a professional-grade SRE dashboard built with Streamlit. This UI provides the visual context for the incident, displaying metrics, logs, and deployment history that the agent will eventually analyze.

The dashboard architecture consists of:
*   **`app.py` & `ui.py`**: The main entry point and UI component library for the Streamlit application.
*   **Incident Data**: Mock data located in `data/` (e.g., `metrics.json`, `app.log`, `diff.txt`) that simulates a real production environment.
*   **Session Management**: A session picker that allows users to resume previous investigations or start new ones, demonstrating the stateful nature of Managed Agents.

For details on the UI structure and how the mock incident data is organized, see **[SRE Agent: Dashboard UI and Data Layer](#6.2)**.

Sources: [README.md:15-15](), [ship-your-first-managed-agent/agent.py:1-100]()

---

### Workshop Summary Table

| Component | File(s) | Responsibility |
| :--- | :--- | :--- |
| **Agent Logic** | `agent.py` | API integration for Agent, Environment, and Session resources. |
| **Infrastructure** | `provided.py` | System prompts, tool schemas, and client initialization. |
| **Frontend** | `app.py`, `ui.py` | Streamlit dashboard and chat interface. |
| **Incident Data** | `data/` | Log files, metric exports, and git diffs for the SRE task. |
| **Testing** | `e2e.py` | End-to-end validation of the agent's ability to solve the incident. |

Sources: [README.md:15-15](), [ship-your-first-managed-agent/agent.py:1-100]()

---

