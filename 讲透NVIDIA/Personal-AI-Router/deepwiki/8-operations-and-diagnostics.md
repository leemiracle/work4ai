<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/Personal-AI-Router · page 8 Operations and Diagnostics · fetched 2026-10-26 -->

# Operations and Diagnostics

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [AGENTS.md](AGENTS.md)

</details>



Operating the NVIDIA Personal AI Router (PAIR) involves managing a distributed system of local and remote inference engines. This page provides a high-level overview of the tools and procedures for monitoring system health, collecting diagnostic information for troubleshooting, and validating routing performance.

## System Monitoring and Terminal Access

While the primary interface for PAIR is the Electron desktop application, headless environments (such as remote servers or SSH sessions) require a specialized interface. PAIR provides a terminal-based dashboard that mirrors the desktop application's functionality.

### Terminal Interface (nvpair-tui)
The `nvpair-tui` utility is a terminal user interface built with the Bubble Tea framework. It allows operators to monitor node status, view active workloads, manage engines, and inspect logs without a graphical environment.

*   **Operation**: It functions as a standalone client. Because it spawns its own internal `nvpair-ui-broker`, it **must not** be run simultaneously with the desktop application on the same machine to avoid port and resource conflicts.
*   **Capabilities**: Includes tabs for Errors, Nodes, Proxies, Workloads, Engines, Cluster management, and real-time Log viewing.

For details, see [Terminal Interface (nvpair-tui)](#8.1).

### Natural Language to Code Entity Mapping: TUI Components
The following diagram maps the TUI's visual components to their underlying Go implementations within the `nvpair-tui` service.

```mermaid
graph TD
    subgraph "TUI View (Bubble Tea)"
        "UI_Tabs"["Tabs Controller"]
        "Node_View"["Nodes Tab"]
        "Error_View"["Errors Tab"]
        "Log_View"["Logs Tab"]
    end

    subgraph "Service Entities (services/nvpair-tui/)"
        "TUI_App"["app.go: App Struct"]
        "TUI_Model"["model.go: Model Struct"]
        "TUI_Update"["update.go: Update()"]
    end

    subgraph "Broker Connection"
        "RPC_Client"["jsonrpc.Client"]
    end

    "UI_Tabs" --> "TUI_Model"
    "Node_View" --> "TUI_Update"
    "Error_View" --> "TUI_Update"
    "TUI_Update" --> "RPC_Client"
    "RPC_Client" -- "discovery:get-nodes" --> "nvpair-ui-broker"
```
**Sources:** [AGENTS.md:40-42](), [services/nvpair-tui/README.md]() (implied by TUI structure).

---

## Diagnostics and Log Collection

PAIR generates structured logs in JSONL format to facilitate automated analysis while protecting user privacy.

### Log Collection and Sanitization
The system includes a diagnostic pipeline via `scripts/collect-logs.sh` (Linux/macOS) and `collect-logs.ps1` (Windows). This pipeline automates the gathering of logs from the local node and, optionally, remote cluster nodes.

*   **Sanitization**: The `collectlogs` Go binary automatically redacts sensitive information, including hostnames, IP addresses, and UUIDs, replacing them with consistent tokens (e.g., `NODE-1`). A `token-map.json` is generated locally to allow the administrator to reverse these tokens if necessary, but this map is never included in the shared diagnostic bundle.
*   **Privacy Policy**: The system is designed to **never** log inference prompts, response bodies, or pairing PINs. Only operational metadata (engine status, model names, job IDs) is captured.

For details, see [Log Collection and Sanitization](#8.2).

**Sources:** [AGENTS.md:117-119](), [.gitignore:9-12](), [.gitignore:15-15]().

---

## Traffic Validation and Load Testing

To ensure the router and scheduler are functioning correctly across a cluster, PAIR includes utilities for generating synthetic traffic.

### Inference Demo and Dispatcher
The "Inference Demo" is a built-in feature that generates 60 seconds of synthetic inference traffic to exercise the routing logic and failover mechanisms.

*   **Orchestration**: The Electron main process schedules these requests via `inference-demo.ts` and `inference-demo-schedule.ts`.
*   **Execution**: The `inference-dispatcher` Go binary is used to send the actual HTTP requests. It targets the local proxy ports (e.g., the Ollama or LM Studio compatible ports) rather than the engines directly, ensuring the `nvpair-job-scheduler` is involved in every request.
*   **Privacy**: The dispatcher uses `stdio: ignore` and does not log the content of the synthetic prompts or responses.

For details, see [Inference Demo and Dispatcher](#8.3).

### Natural Language to Code Entity Mapping: Inference Flow
This diagram illustrates how a diagnostic demo request moves from the UI through the dispatcher to the routing logic.

```mermaid
graph LR
    subgraph "Desktop UI"
        "Demo_Button"["InferenceDemoToast.tsx"]
    end

    subgraph "Electron Main"
        "Demo_Sched"["inference-demo-schedule.ts"]
        "Demo_Logic"["inference-demo.ts"]
    end

    subgraph "External Utility"
        "Dispatcher"["inference-dispatcher (Go binary)"]
    end

    subgraph "Routing Layer"
        "Ollama_Proxy"["ollama-proxy: Port 11434"]
        "Scheduler"["nvpair-job-scheduler"]
    end

    "Demo_Button" -- "demo:start" --> "Demo_Sched"
    "Demo_Sched" --> "Demo_Logic"
    "Demo_Logic" -- "spawn" --> "Dispatcher"
    "Dispatcher" -- "HTTP POST /api/generate" --> "Ollama_Proxy"
    "Ollama_Proxy" -- "Select Node" --> "Scheduler"
```
**Sources:** [desktop/src/electron/inference-demo.ts](), [desktop/src/electron/inference-demo-schedule.ts](), [scripts/inference-dispatcher/main.go]().

---

## Summary of Operations Utilities

| Utility | Location | Purpose |
| :--- | :--- | :--- |
| `nvpair-tui` | `services/nvpair-tui/` | Headless monitoring and management. |
| `collect-logs.sh/ps1` | `scripts/` | Automated diagnostic gathering and redaction. |
| `collectlogs` | `scripts/collectlogs/` | The Go engine behind log sanitization. |
| `inference-dispatcher` | `scripts/inference-dispatcher/` | CLI tool for generating test inference traffic. |

**Sources:** [AGENTS.md:15-17](), [AGENTS.md:40-40](), [.gitignore:15-17]().

---

