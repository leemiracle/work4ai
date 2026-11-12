<!-- source: DeepWiki mcp.deepwiki.com · repo OpenDCAI/Paper2Any · page 2 Getting Started · fetched 2026-11-02 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [dataflow_agent/toolkits/p2vtool/1_merge.bash](dataflow_agent/toolkits/p2vtool/1_merge.bash)
- [deploy/app_config.sh](deploy/app_config.sh)
- [docs/contributing.md](docs/contributing.md)
- [docs/guides/index.md](docs/guides/index.md)
- [docs/guides/open_source_deployment.md](docs/guides/open_source_deployment.md)
- [docs/index.md](docs/index.md)
- [docs/installation.md](docs/installation.md)
- [docs/quickstart.md](docs/quickstart.md)
- [fastapi_app/__init__.py](fastapi_app/__init__.py)
- [fastapi_app/interprocess_lock.py](fastapi_app/interprocess_lock.py)
- [mkdocs.yml](mkdocs.yml)
- [requirements-base.txt](requirements-base.txt)
- [requirements-paper.txt](requirements-paper.txt)
- [tests/test_paper2ppt_generate_route.py](tests/test_paper2ppt_generate_route.py)

</details>



This guide walks you through setting up Paper2Any and running your first workflow. Paper2Any is a multimodal document processing system that converts academic papers into figures, presentations, videos, and more. It can be deployed in several configurations ranging from a minimal local setup to a full production system with GPU-accelerated model services.

**Quick Navigation:**
- [Installation](#2.1) — Detailed installation instructions including Python dependencies, Node.js setup, and system packages (LibreOffice, Inkscape).
- [Configuration](#2.2) — Explain the four configuration file types, API key setup, model selection, and optional Supabase configuration.
- [Quick Start](#2.3) — Walk through running the application locally using deployment scripts and executing first workflows.

---

## Prerequisites

Paper2Any requires Python 3.11 and several system-level dependencies for document processing, vector graphics rendering, and AI model integration.

**Core Requirements:**

| Component | Recommended Version | Required For |
|-----------|---------------------|--------------|
| Python | 3.11 | Backend Runtime & Model Services [docs/installation.md:33]() |
| Node.js | 20 | Frontend Web UI [docs/installation.md:34]() |
| OS | Linux (Ubuntu/Debian) | Primary support (WSL2 for Windows) [docs/installation.md:36]() |

**System Packages (Linux):**
The following packages are essential for the document conversion pipeline:
- `inkscape`: Vector graphics processing [requirements-paper.txt:14]()
- `libreoffice`: PPT/PDF conversions [docs/installation.md:49]()
- `tectonic`: TeX engine for scientific rendering [requirements-paper.txt:11]()
- `poppler-utils`: PDF manipulation [docs/installation.md:50]()
- `ffmpeg`: Video compositing for Paper2Video [dataflow_agent/toolkits/p2vtool/1_merge.bash:39-43]()

**Sources:** [docs/installation.md:12-65](), [requirements-paper.txt:10-15]()

---

## Deployment Architectures

Paper2Any supports three primary deployment routes depending on your hardware resources and use case. For a deep dive into these routes, see [Quick Start](#2.3).

### 1. Minimal Setup (Local Development)
This route focuses on the frontend and backend logic, relying on external LLM APIs (OpenAI, Gemini, etc.) for heavy lifting.

```mermaid
graph TD
    subgraph "Local_Machine"
        [Browser] -->|"Port 3000"| [Vite_Frontend]
        [Vite_Frontend] -->|"API Proxy"| [FastAPI_Backend]
        [FastAPI_Backend] --> [DataFlow_Agent_Engine]
        [DataFlow_Agent_Engine] --> [External_LLM_APIs]
    end
    [FastAPI_Backend] -.->|"Storage"| [Local_Outputs_Dir]
```

**Sources:** [docs/index.md:57-80](), [docs/quickstart.md:10-88]()

### 2. Full Local Setup (GPU Accelerated)
This configuration adds local model servers (MinerU, SAM3, OCR) to handle PDF parsing and image segmentation locally, reducing reliance on external multimodal APIs.

```mermaid
graph TB
    subgraph "Application_Tier"
        [FastAPI_Backend]
    end

    subgraph "Model_Service_Tier"
        [FastAPI_Backend] --> [MinerU_Server]
        [FastAPI_Backend] --> [SAM3_Server]
        [FastAPI_Backend] --> [PaddleOCR_Server]
    end

    [MinerU_Server] --- [GPU_Resources]
    [SAM3_Server] --- [GPU_Resources]
    
    [FastAPI_Backend] --> [InterProcessLock]
    [InterProcessLock] --> [Outputs_Locks_Dir]
```

**Key Entities:**
- `MinerU_Server`: High-fidelity PDF parsing [docs/index.md:107]()
- `SAM3_Server`: Segment Anything Model for diagram extraction [deploy/app_config.sh:27]()
- `AsyncInterProcessSemaphore`: Manages concurrent access to GPU resources across uvicorn workers [fastapi_app/interprocess_lock.py:23-24]()

**Sources:** [deploy/app_config.sh:24-31](), [fastapi_app/interprocess_lock.py:12-16](), [docs/quickstart.md:101-109]()

---

## Configuration Overview

The system behavior is governed by four primary configuration locations. For details on variable mapping, see [Configuration](#2.2).

| Config File | Scope | Key Variables |
|-------------|-------|---------------|
| `fastapi_app/.env` | Backend Logic | `BACKEND_API_KEY`, `DF_API_KEY`, `APP_BILLING_MODE` |
| `frontend-workflow/.env` | Web UI | `VITE_API_KEY`, `VITE_API_BASE_URL` |
| `deploy/profiles/*.env` | Model Servers | `SAM3_SERVER_URLS`, `APP_PORT` |
| `logs/model_servers.env` | Shared Runtime | GPU allocation and server ports |

**Sources:** [docs/index.md:62](), [docs/quickstart.md:41-65](), [deploy/app_config.sh:9-31]()

---

## Application Startup

To get the system running quickly, follow the "Shortest Path" using the provided deployment scripts.

1.  **Environment Preparation:** Create a Conda environment and install dependencies from `requirements-paper.txt` [docs/quickstart.md:23-29]().
2.  **Frontend Setup:** Install Node modules in `frontend-workflow/` [docs/quickstart.md:31-39]().
3.  **Configuration:** Copy `.env.example` templates and set your `DF_API_KEY` (LLM provider key) [docs/quickstart.md:41-58]().
4.  **Execution:**
    *   Start Backend: `bash deploy/start.sh` [docs/quickstart.md:75-77]()
    *   Start Frontend: `bash deploy/start_frontend.sh` [docs/quickstart.md:81-83]()

For a detailed walkthrough of these steps and troubleshooting, see [Quick Start](#2.3).

**Sources:** [docs/quickstart.md:10-88](), [deploy/app_config.sh:1-25]()

---

## Next Steps

Once the application is running, you can explore the various workflows:

*   **Document Conversion:** Use the UI to run `Paper2PPT` or `Paper2Figure` tasks.
*   **Knowledge Base:** Upload PDFs to the KB system for RAG-based Q&A and podcast generation.
*   **CLI Usage:** For batch processing, refer to the CLI tools documented in [Quick Start](#2.3).

For developers looking to extend the system, refer to the [Development Guide](#11) to learn about the `DataFlow-Agent` framework and how to register new `wf_*.py` workflows [docs/contributing.md:67-87]().

**Sources:** [docs/index.md:25-43](), [docs/contributing.md:54-65]()

---

