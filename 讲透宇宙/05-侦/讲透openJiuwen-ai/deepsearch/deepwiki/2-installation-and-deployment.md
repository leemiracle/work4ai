<!-- source: DeepWiki mcp.deepwiki.com · repo openJiuwen-ai/deepsearch · page 2 Installation and Deployment · fetched 2026-11-02 -->

# Installation and Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [deepsearch/docs/en/2.Installation Guide/DeepSearch Full Edition/README.md](deepsearch/docs/en/2.Installation Guide/DeepSearch Full Edition/README.md)

</details>



This page provides a high-level overview of the deployment strategies for the DeepSearch system. DeepSearch can be deployed either as a comprehensive product suite (Full Edition) or as a standalone backend service (SDK Only). The installation process supports multiple operating systems (Linux, Windows, and macOS) through both containerized (Docker) and manual methods.

## Deployment Options

DeepSearch is architected to be flexible, allowing users to choose between a user-facing interface or a pure API-driven backend.

| Option | Components Included | Primary Use Case |
| :--- | :--- | :--- |
| **DeepSearch Full Edition** | Studio (Web UI) + DeepSearch SDK | End-to-end research product with visual management and knowledge base UI. |
| **DeepSearch SDK Only** | DeepSearch SDK (FastAPI Backend) | Integration into existing applications via API or for headless agentic workflows. |

Sources: [deepsearch/docs/en/2.Installation Guide/DeepSearch Full Edition/README.md:1-9]()

### System Connectivity Bridge
When deploying the Full Edition, the **Studio** component acts as a client to the **DeepSearch SDK**. The connection between these two services is established through specific environment variables that must be aligned in their respective `.env` files.

*   **Studio Configuration**: Uses `DEEPSEARCH_AGENT_HOST` and `DEEPSEARCH_AGENT_PORT` to locate the backend.
*   **SDK Configuration**: Uses `HOST` and `BACKEND_PORT` to define its listening interface.

Sources: [deepsearch/docs/en/2.Installation Guide/DeepSearch Full Edition/README.md:23-26]()

## Deployment Architecture

The following diagram illustrates how the system components interact across different deployment scenarios, bridging the user-facing "Studio" to the internal "SDK" logic.

**DeepSearch Component Interaction**
```mermaid
graph TD
    subgraph "Natural Language Space (User Interface)"
        ["Studio Web UI"] -- "HTTP/SSE" --> ["Studio Backend"]
    end

    subgraph "Code Entity Space (DeepSearch SDK)"
        ["Studio Backend"] -- "DEEPSEARCH_AGENT_HOST:PORT" --> ["FastAPI Server (server/main.py)"]
        ["FastAPI Server (server/main.py)"] --> ["DeepSearch Run API (deepsearch_run.py)"]
        ["DeepSearch Run API (deepsearch_run.py)"] --> ["Workflow Runner (algorithm/workflow.py)"]
    end

    subgraph "Data & Persistence"
        ["FastAPI Server (server/main.py)"] --> ["SQLAlchemy DB (MySQL/SQLite)"]
        ["DeepSearch Run API (deepsearch_run.py)"] --> ["Redis Checkpointer"]
    end
```
Sources: [deepsearch/docs/en/2.Installation Guide/DeepSearch Full Edition/README.md:1-6](), [deepsearch/server/main.py:1-50](), [deepsearch/server/deepsearch_run.py:1-20]()

## Installation Paths

### 1. DeepSearch Full Edition Installation
This is the recommended path for most users. It includes the **Studio** (Web UI and backend management) and the **DeepSearch SDK**. 

*   **Docker Deployment**: The simplest method, using `docker-compose` to orchestrate the Studio, SDK, and required databases (MySQL/Redis).
*   **Manual Installation**: Requires manual setup of Python environments for both repositories and configuring the bridge environment variables.

For detailed, OS-specific instructions, see [DeepSearch Full Edition Installation](#2.1).

Sources: [deepsearch/docs/en/2.Installation Guide/DeepSearch Full Edition/README.md:11-38]()

### 2. DeepSearch SDK Standalone Installation
This path is intended for developers who want to use DeepSearch as an engine within their own infrastructure. This installs only the backend service defined in the `deepsearch` repository.

*   **API Access**: Once deployed, the SDK exposes endpoints via FastAPI (e.g., `/api/deepsearch/run`).
*   **Configuration**: Requires setting up `.env` for LLM providers, search engines (e.g., Bing/Serper), and vector databases if knowledge base features are needed.

For details on standalone backend setup, see [DeepSearch SDK Standalone Installation](#2.2).

Sources: [deepsearch/docs/en/2.Installation Guide/DeepSearch Full Edition/README.md:23-25]()

## OS Support Matrix

The installation guides cover three primary operating systems for both Docker and Manual methods:

| Operating System | Docker Support | Manual Support |
| :--- | :---: | :---: |
| **Linux** (Ubuntu/CentOS) | Supported | Supported |
| **Windows** (WSL2 recommended) | Supported | Supported |
| **macOS** (Intel/Apple Silicon) | Supported | Supported |

Sources: [deepsearch/docs/en/2.Installation Guide/DeepSearch Full Edition/README.md:13-17]()

---

