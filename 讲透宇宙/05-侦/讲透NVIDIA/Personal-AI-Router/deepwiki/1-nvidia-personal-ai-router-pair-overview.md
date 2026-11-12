<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/Personal-AI-Router · page 1 NVIDIA Personal AI Router (PAIR) — Overview · fetched 2026-10-26 -->

# NVIDIA Personal AI Router (PAIR) — Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/ISSUE_TEMPLATE/bug.yml](.github/ISSUE_TEMPLATE/bug.yml)
- [AGENTS.md](AGENTS.md)
- [README.md](README.md)
- [assets/pair-demo.gif](assets/pair-demo.gif)
- [assets/pair-demo.mp4](assets/pair-demo.mp4)

</details>



NVIDIA Personal AI Router (PAIR) is a local inference router designed for a group of compatible computers on the same network. It discovers participating nodes, manages supported inference engines (Ollama and LM Studio), and presents unified Ollama-compatible and OpenAI-compatible proxy endpoints to applications and agents [README.md:11-16]().

PAIR is optimized for concurrent local workloads, such as multi-agent applications, ensuring that prompts and responses remain on the local network when all configured components are local [README.md:18-20]().

> **Note:** PAIR routes independent requests to individual nodes. It does **not** pool GPU memory, shard single models across machines, or split a single in-flight inference request between nodes [README.md:22-24]().

## Key Capabilities

*   **Discovery:** Automatically finds other PAIR nodes on the network using mDNS [AGENTS.md:36-37]().
*   **Engine Management:** Installs and supervises engines like Ollama and LM Studio [README.md:102-105]().
*   **Intelligent Routing:** Directs requests based on model availability and current GPU pressure [README.md:15-16]().
*   **Secure Pairing:** Establishes trust between nodes using EAP-NOOB and a six-digit PIN for mutual TLS (mTLS) communication [AGENTS.md:117-118]().

## System Entities and Vocabulary

The PAIR ecosystem is defined by several core entities that map directly to services and data structures in the codebase:

| Entity | Description | Code Reference |
| :--- | :--- | :--- |
| **Node** | A single computer running PAIR. | `NodeRec` in [services/shared/noderec/noderec.go]() |
| **Cluster** | A group of trusted Nodes paired via PIN. | `nvpair-cluster-manager` in [services/cluster-manager/]() |
| **Engine** | An inference provider (e.g., Ollama, LM Studio). | `Engine` in [services/engine-manager/]() |
| **Model** | An AI model managed by an Engine. | `Model` in [services/engine-manager/]() |
| **Proxy** | The entry point for client API requests. | `ollama-proxy` / `lmstudio-proxy` |
| **Job** | An active inference request being routed. | `nvpair-job-scheduler` in [services/job-scheduler/]() |
| **Broker** | The central supervisor for all Go workers. | `nvpair-ui-broker` in [services/ui-broker/]() |

For a complete list of terms, see [Core Concepts and Vocabulary](#1.2).

## High-Level Architecture

PAIR uses a multi-process architecture where an Electron desktop application acts as a client to a tree of Go-based services [AGENTS.md:27-31]().

### Process Relationship Diagram
This diagram shows how the user-facing application connects to the underlying system entities.

```mermaid
graph TD
    subgraph "Desktop Space (TypeScript/Electron)"
        UI["React Renderer"] -- "window.pairApi" --> MB["ModularSupervisor (Electron Main)"]
    end

    subgraph "Service Space (Go)"
        MB -- "JSON-RPC (stdio)" --> Broker["nvpair-ui-broker"]
        Broker -- "Supervises" --> Scanner["nvpair-node-scanner"]
        Broker -- "Supervises" --> EngineMgr["nvpair-engine-manager"]
        Broker -- "Supervises" --> Proxies["Inference Proxies (Ollama/LM Studio)"]
        Broker -- "Supervises" --> ClusterMgr["nvpair-cluster-manager"]
    end

    Proxies -- "Routes to" --> RemoteNode["Remote PAIR Node (mTLS)"]
    EngineMgr -- "Controls" --> LocalEngine["Local Engine (Ollama/LM Studio)"]

    Sources: [AGENTS.md:35-42](), [desktop/src/electron/index.ts]()
```

### Request Flow Diagram
This diagram bridges the "Natural Language" intent of a user to the specific "Code Entities" that handle the request.

```mermaid
graph LR
    Client["'curl /v1/chat/completions'"] --> Proxy["ollama-proxy (Go)"]
    Proxy --> Scheduler["nvpair-job-scheduler (Go)"]
    
    subgraph "Routing Logic"
        Scheduler -- "Check Capacity" --> NodeList["Discovery Store"]
        NodeList -- "Selects" --> TargetNode["Target NodeID"]
    end

    TargetNode --> Transport["mTLS Client (shared/clustertrust)"]
    Transport --> Remote["Remote Node Port 14321"]

    Sources: [README.md:128-132](), [AGENTS.md:36-37](), [services/shared/clustertrust/]()
```

## Supported Platforms and Engines

PAIR supports a cross-platform environment, allowing different OS types to participate in the same cluster [README.md:40]().

*   **Operating Systems:** Windows 11, Linux (Debian/Ubuntu), macOS [README.md:37]().
*   **Architectures:** x64 and arm64 [README.md:38]().
*   **Engines:** Ollama and LM Studio [README.md:41]().

> **Important:** PAIR manages engines, but the engine's hardware requirements (GPU, VRAM) are independent of PAIR [README.md:43-50]().

## Documentation Map

*   **[Getting Started](#1.1)**: Installation, initial setup, pairing nodes, and running your first inference.
*   **[Core Concepts and Vocabulary](#1.2)**: Deep dive into the terminology and conceptual model of the system.
*   **System Architecture**: Detailed breakdown of the process model, discovery mechanisms, and security boundaries.
*   **Backend Services (Go)**: Technical details on the 13 Go binaries that power the routing engine.
*   **Desktop Application**: Overview of the Electron/React frontend and the service bridge.
*   **Operations and Diagnostics**: How to use `nvpair-tui` for headless nodes and collect sanitized logs.

---
**Sources:**
* [README.md:1-155]()
* [AGENTS.md:1-150]()
* [.github/ISSUE_TEMPLATE/bug.yml:24-38]()

---

