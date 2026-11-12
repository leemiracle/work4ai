# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [Dockerfile](Dockerfile)
- [README-ja_JP.md](README-ja_JP.md)
- [README-ko_KR.md](README-ko_KR.md)
- [README-zh_CN.md](README-zh_CN.md)
- [README.md](README.md)
- [docker-compose.yml](docker-compose.yml)
- [docs/CNAME](docs/CNAME)
- [docs/docs/contribute.md](docs/docs/contribute.md)
- [gpt_researcher/agent.py](gpt_researcher/agent.py)
- [gpt_researcher/skills/browser.py](gpt_researcher/skills/browser.py)
- [gpt_researcher/skills/researcher.py](gpt_researcher/skills/researcher.py)
- [requirements.txt](requirements.txt)

</details>



## Purpose and Scope

This document provides a high-level overview of the GPT Researcher system architecture, core components, and capabilities. GPT Researcher is an autonomous research agent designed for both web and local research on any given task, producing detailed, factual, and unbiased research reports with citations [README.md:23-27](). Inspired by the [Plan-and-Solve](https://arxiv.org/abs/2305.04091) and [RAG](https://arxiv.org/abs/2005.11401) papers, it addresses misinformation and speed through parallelized agent work [README.md:27-28]().

This overview covers the fundamental architecture and component relationships. For detailed information about specific subsystems, refer to the subsequent pages in this wiki.

**Sources:** [README.md:23-30](), [gpt_researcher/agent.py:1-5]()

## System Architecture

GPT Researcher utilizes a "planner" and "execution" agent pattern [README.md:54-56](). The system is highly modular, supporting 25+ LLM providers, multiple search retrievers, and various document formats [README.md:76-84]().

### High-Level Component Architecture

The following diagram bridges the high-level system concepts with the specific classes and files found in the codebase.

```mermaid
graph TB
    subgraph "EntryPoints"
        Main["main.py<br/>(FastAPI/Uvicorn)"]
        PIP["gpt_researcher<br/>(PIP Package)"]
        Claude["Claude Skill<br/>(npx skills)"]
    end
    
    subgraph "OrchestrationLayer"
        GPTR["class GPTResearcher<br/>gpt_researcher/agent.py"]
        Config["class Config<br/>gpt_researcher/config.py"]
    end
    
    subgraph "ExecutionSkills"
        RC["class ResearchConductor<br/>gpt_researcher/skills/researcher.py"]
        BM["class BrowserManager<br/>gpt_researcher/skills/browser.py"]
        RG["class ReportGenerator<br/>gpt_researcher/skills/writer.py"]
        CM["class ContextManager<br/>gpt_researcher/skills/context_manager.py"]
        IG["class ImageGenerator<br/>gpt_researcher/skills/image_generator.py"]
        DS["class DeepResearchSkill<br/>gpt_researcher/skills/deep_research.py"]
    end
    
    subgraph "DataRetrieval"
        Retriever["get_retrievers()<br/>gpt_researcher/actions/retrievers.py"]
        DocLoader["class DocumentLoader<br/>gpt_researcher/document/document.py"]
        VS["class VectorStoreWrapper<br/>gpt_researcher/vector_store.py"]
    end
    
    subgraph "Intelligence"
        LLM["class GenericLLMProvider<br/>gpt_researcher/llm_provider.py"]
        Mem["class Memory<br/>gpt_researcher/memory.py"]
        Prompts["get_prompt_family()<br/>gpt_researcher/prompts.py"]
    end

    Main --> GPTR
    PIP --> GPTR
    Claude --> GPTR
    
    GPTR --> Config
    GPTR --> RC
    GPTR --> BM
    GPTR --> RG
    GPTR --> CM
    GPTR --> IG
    GPTR --> DS
    
    RC --> Retriever
    RC --> DocLoader
    CM --> VS
    
    GPTR --> LLM
    GPTR --> Mem
    GPTR --> Prompts
```

**Sources:** [README.md:54-68](), [gpt_researcher/agent.py:36-83](), [gpt_researcher/skills/researcher.py:21-47](), [gpt_researcher/agent.py:24-30]()

## Core Components

The system consists of several key classes and modules that manage the research lifecycle:

| Component | Code Entity | Primary Responsibility |
|-----------|-----------|------------------------|
| **Main Agent** | `GPTResearcher` [gpt_researcher/agent.py:36]() | Orchestrates the entire research process, manages state, and tracks costs [gpt_researcher/agent.py:43-50](). |
| **Research Planner** | `ResearchConductor` [gpt_researcher/skills/researcher.py:21]() | Handles query planning, sub-query generation, and retriever coordination [gpt_researcher/skills/researcher.py:24-32](). |
| **Browser Engine** | `BrowserManager` [gpt_researcher/skills/browser.py:14]() | Manages parallel URL scraping and image selection using a `WorkerPool` [gpt_researcher/skills/browser.py:17-35](). |
| **Context Processor** | `ContextManager` [gpt_researcher/skills/context_manager.py:25]() | Filters and compresses gathered information to fit LLM context windows. |
| **Report Writer** | `ReportGenerator` [gpt_researcher/skills/writer.py:30]() | Synthesizes findings into the final document (Markdown, PDF, or DOCX). |
| **Config System** | `Config` [gpt_researcher/agent.py:140]() | Loads environment variables and settings for LLMs, retrievers, and scrapers. |
| **LLM Interface** | `GenericLLMProvider` [gpt_researcher/agent.py:21]() | Provides a unified interface for multiple LLM providers (OpenAI, Anthropic, etc.). |

### Internal Data Flow Diagram

This diagram traces the flow of a research query through the internal function calls and data structures.

```mermaid
sequenceDiagram
    participant U as User/API
    participant A as "class GPTResearcher"
    participant RC as "class ResearchConductor"
    participant BM as "class BrowserManager"
    participant LLM as "class GenericLLMProvider"
    participant RG as "class ReportGenerator"

    U->>A: conduct_research()
    activate A
    A->>RC: plan_research(query)
    RC->>LLM: plan_research_outline()
    LLM-->>RC: List[sub_queries]
    
    loop For each sub-query
        RC->>RC: get_search_results()
        RC->>BM: browse_urls(urls)
        BM->>BM: scrape_urls()
        BM-->>A: add_research_sources(content)
    end
    
    A-->>U: Research Complete
    deactivate A
    
    U->>A: write_report()
    activate A
    A->>RG: write_report()
    RG->>LLM: create_chat_completion()
    LLM-->>RG: Final Report Content
    RG-->>A: Report (MD/PDF/DOCX)
    A-->>U: Final Report
    deactivate A
```

**Sources:** [gpt_researcher/agent.py:138-168](), [gpt_researcher/skills/researcher.py:89-160](), [gpt_researcher/skills/browser.py:37-84](), [gpt_researcher/skills/researcher.py:75-87]()

## Research Workflow

The standard research pipeline follows these steps:

1.  **Task Initialization**: A task-specific agent is created based on the research query [README.md:63]().
2.  **Query Decomposition**: The `ResearchConductor` generates a set of questions that collectively form an objective opinion on the task [README.md:64]().
3.  **Information Gathering**: A crawler agent (via `BrowserManager`) gathers information for each question from online or local resources [README.md:65]().
4.  **Source Tracking**: Each resource is summarized and its source is tracked [README.md:66]().
5.  **Aggregation**: Findings are filtered and aggregated into a final research report exceeding 2,000 words if configured [README.md:67-79]().

**Sources:** [README.md:62-68](), [gpt_researcher/skills/researcher.py:89-160]()

## Key Capabilities

*   **Multi-Source Research**: Aggregates over 20 sources per research task to ensure objective conclusions [README.md:80]().
*   **Hybrid Data Support**: Conducts research using both web search and local documents (PDF, DOCX, CSV, etc.) [README.md:76](), [requirements.txt:31-36]().
*   **Advanced UI Options**: Provides both a lightweight Vanilla JS frontend and a production-ready NextJS + Tailwind interface [README.md:81](), [docker-compose.yml:26-45]().
*   **Visual Enhancements**: Includes smart image scraping and AI-generated inline images using Google Gemini [README.md:77-78](), [docker-compose.yml:13-16]().
*   **Parallel Execution**: Utilizes a `WorkerPool` for parallelized web scraping to increase speed and stability [gpt_researcher/skills/browser.py:32-35]().
*   **MCP Support**: Integrates with the Model Context Protocol (MCP) to access specialized tools and data sources [gpt_researcher/agent.py:113-135]().

**Sources:** [README.md:74-85](), [gpt_researcher/skills/browser.py:32-35](), [gpt_researcher/agent.py:113-136](), [requirements.txt:60-61]()

## Deployment and Operations

GPT Researcher can be deployed in several environments:
*   **Local Python**: Installed via `pip` or by cloning the repository [README.md:94-135]().
*   **Docker**: Multi-stage builds for the backend and NextJS frontend are provided [Dockerfile:1-65](), [docker-compose.yml:1-78]().
*   **Claude Skill**: Can be installed as a tool for Claude to extend its research capabilities [README.md:44-52]().

**Sources:** [README.md:94-135](), [Dockerfile:1-65](), [docker-compose.yml:1-25]()

---

# Page: Getting Started

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.cursorignore](.cursorignore)
- [README-ja_JP.md](README-ja_JP.md)
- [README-ko_KR.md](README-ko_KR.md)
- [README-zh_CN.md](README-zh_CN.md)
- [README.md](README.md)
- [docs/CNAME](docs/CNAME)
- [docs/docs/contribute.md](docs/docs/contribute.md)
- [docs/docs/examples/custom_prompt.py](docs/docs/examples/custom_prompt.py)
- [docs/docs/examples/examples.md](docs/docs/examples/examples.md)
- [docs/docs/examples/hybrid_research.md](docs/docs/examples/hybrid_research.md)
- [docs/docs/examples/pip-run.ipynb](docs/docs/examples/pip-run.ipynb)
- [docs/docs/examples/sample_report.py](docs/docs/examples/sample_report.py)
- [docs/docs/examples/sample_sources_only.py](docs/docs/examples/sample_sources_only.py)
- [docs/docs/gpt-researcher/getting-started/getting-started.md](docs/docs/gpt-researcher/getting-started/getting-started.md)
- [docs/docs/gpt-researcher/getting-started/introduction.md](docs/docs/gpt-researcher/getting-started/introduction.md)
- [docs/docs/gpt-researcher/gptr/pip-package.md](docs/docs/gpt-researcher/gptr/pip-package.md)

</details>



This page provides an overview of installing GPT Researcher and running your first research task. It covers prerequisites, installation paths, basic configuration, and initial verification. Detailed information is provided in the child pages:

- **[Installation Methods](#2.1)** - Detailed setup instructions for pip, Docker, git clone, and Claude skills.
- **[Quick Start Examples](#2.2)** - Copy-paste code examples for common use cases including hybrid research.
- **[Configuration Setup](#2.3)** - API keys, environment variables, and model provider tuning.

For system architecture details, see [Core Architecture](#3). For multi-agent capabilities, see [Multi-Agent Framework](#4.4).

---

## Prerequisites and System Requirements

Before installing GPT Researcher, ensure your system meets the following requirements:

| Requirement | Specification | Notes |
|------------|---------------|-------|
| **Python Version** | 3.11 or higher | Required for core async features [README.md:98](), [docs/docs/gpt-researcher/getting-started/getting-started.md:3]() |
| **Operating System** | Linux, macOS, Windows | Cross-platform support [README.md:98-111]() |
| **API Keys** | OpenAI, Tavily (recommended) | Essential for LLM and Search capabilities [README.md:106-111](), [docs/docs/gpt-researcher/getting-started/getting-started.md:12-30]() |
| **Environment** | Virtual Env / Poetry | Recommended for dependency isolation [docs/docs/gpt-researcher/getting-started/getting-started.md:48-99]() |

The system is optimized for **OpenAI GPT** models and the **Tavily Search API**, though it supports over 25+ LLM providers and various retrievers.

**Sources:** [README.md:98](), [README.md:106-111](), [docs/docs/gpt-researcher/getting-started/getting-started.md:3-30]()

---

## Installation Overview

GPT Researcher offers four primary installation methods to suit different development workflows:

### Installation Paths and Components

```mermaid
graph TB
    Start["Installation Method"]
    
    Start --> PIP["pip install gpt-researcher"]
    Start --> Git["git clone + pip install -r requirements.txt"]
    Start --> Docker["docker-compose up --build"]
    Start --> Claude["npx skills add gpt-researcher"]
    
    PIP --> PIPComponents["gpt_researcher package<br/>'GPTResearcher' class<br/>Library usage"]
    Git --> GitComponents["Full source code<br/>'main.py' FastAPI server<br/>'frontend/' directory"]
    Docker --> DockerComponents["'gpt-researcher' service (8000)<br/>'gptr-nextjs' service (3000)<br/>Isolated environment"]
    Claude --> ClaudeComponents["'.claude/skills/'<br/>Claude Code integration<br/>Deep Research Skill"]
    
    PIPComponents --> Config["Set ENV Variables<br/>'OPENAI_API_KEY'<br/>'TAVILY_API_KEY'"]
    GitComponents --> Config
    DockerComponents --> EnvFile["'.env' file<br/>Auto-loaded by Compose"]
    ClaudeComponents --> Config
    
    Config --> FirstTask["researcher = GPTResearcher(query=...)<br/>await researcher.conduct_research()<br/>await researcher.write_report()"]
    EnvFile --> FirstTask
```

**Installation Method Comparison**

| Method | Best For | Components | Entry Point |
|--------|----------|------------|-------------|
| **PIP Package** | Integration into existing apps | `gpt_researcher` module | `from gpt_researcher import GPTResearcher` [README.md:145]() |
| **Git Clone** | Development and Customization | Full Repo + FastAPI | `python -m uvicorn main:app` [README.md:130](), [docs/docs/gpt-researcher/getting-started/getting-started.md:104-105]() |
| **Docker** | Production-ready deployments | Containerized App + UI | `docker-compose up` [README-ko_KR.md:167]() |
| **Claude Skill** | Claude Desktop/CLI users | Skill-based research | `npx skills add ...` [README.md:49]() |

For detailed installation instructions, see [Installation Methods](#2.1).

**Sources:** [README.md:44-50](), [README.md:96-141](), [docs/docs/gpt-researcher/getting-started/getting-started.md:1-105](), [README-ko_KR.md:158-175]()

---

## Quick Configuration Setup

After installation, you must provide API keys. GPT Researcher uses a hierarchical configuration system that prioritizes environment variables.

### Minimal Configuration

The minimum required configuration for the default setup:

```bash
export OPENAI_API_KEY={Your OpenAI API Key}
export TAVILY_API_KEY={Your Tavily API Key}
```

For custom OpenAI-compatible APIs (e.g., local models or alternative providers), set the base URL:

```bash
export OPENAI_BASE_URL={Your custom API base URL}
```

### Configuration Architecture

```mermaid
graph LR
    subgraph "Input Sources"
        Env[".env / Export"]
        File["config.json"]
    end
    
    subgraph "Code Entity Space"
        ConfigClass["'Config' class<br/>gpt_researcher/config/config.py"]
        GPTResearcher["'GPTResearcher' agent<br/>gpt_researcher/agent.py"]
    end
    
    Env --> ConfigClass
    File --> ConfigClass
    ConfigClass --> GPTResearcher
    
    subgraph "Provider Logic"
        LLM["'GenericLLMProvider'<br/>gpt_researcher/llm_provider/"]
        Search["'get_retriever()'<br/>gpt_researcher/retrievers/"]
    end
    
    GPTResearcher --> LLM
    GPTResearcher --> Search
```

The `Config` class loads these variables to initialize the `GPTResearcher` agent. For detailed parameter reference, see [Configuration Setup](#2.3).

**Sources:** [README.md:106-124](), [docs/docs/gpt-researcher/getting-started/getting-started.md:12-30](), [README-zh_CN.md:119-120]()

---

## Running Your First Research Task

The execution method depends on your chosen interface.

### Approach 1: Python API (Library)

Use the `GPTResearcher` class to conduct research programmatically:

```python
from gpt_researcher import GPTResearcher
import asyncio

async def main():
    query = "why is Nvidia stock going up?"
    # Initialize with query and report type
    researcher = GPTResearcher(query=query, report_type="research_report")
    # Step 1: Conduct research (Scraping & Context gathering)
    await researcher.conduct_research()
    # Step 2: Write report (Synthesis & Generation)
    report = await researcher.write_report()
    print(report)

if __name__ == "__main__":
    asyncio.run(main())
```

### Approach 2: FastAPI Web Interface

If you cloned the repository, you can run the built-in web server:

```bash
python -m uvicorn main:app --reload
```

Visit `http://localhost:8000` to access the research dashboard [README.md:133]().

### Research Pipeline Flow

```mermaid
sequenceDiagram
    participant U as User
    participant G as GPTResearcher [gpt_researcher/agent.py]
    participant C as ResearchConductor [gpt_researcher/skills/research_conductor.py]
    participant R as ReportGenerator [gpt_researcher/skills/report_generator.py]
    
    U->>G: Initialize(query, report_type)
    G->>C: conduct_research()
    Note over C: 1. Plan Research (Planner)<br/>2. Scrape Sources (Execution)<br/>3. Summarize & Aggregate
    C-->>G: Aggregated Context
    G->>R: write_report()
    Note over R: 1. Apply Prompt Templates<br/>2. LLM Synthesis (GPT-4o)<br/>3. Format Markdown
    R-->>G: Markdown Report
    G-->>U: Final Document
```

For more examples including **Hybrid Research** (Web + Local Docs), see [Quick Start Examples](#2.2).

**Sources:** [README.md:142-154](), [docs/docs/examples/examples.md:4-30](), [docs/docs/examples/hybrid_research.md:62-78](), [docs/docs/gpt-researcher/gptr/pip-package.md:32-63]()

---

## Repository Structure

Key directories for developers:

- `gpt_researcher/`: Core logic including `agent.py` (the main orchestrator) and `config/`. [README.md:145]()
- `multi_agents/`: LangGraph-based collaborative agent system (ChiefEditor, Researcher, etc.). [README-zh_CN.md:137]()
- `frontend/`: UI implementations (NextJS and Vanilla JS). [README.md:81]()
- `docs/`: Documentation and example scripts. [README.md:88]()

**Sources:** [README.md:81-88](), [README-zh_CN.md:137](), [README-ko_KR.md:178-185]()

---

## Next Steps

1. **[Installation Methods](#2.1)**: Set up virtual environments or Docker volumes.
2. **[Quick Start Examples](#2.2)**: Learn how to research local PDFs or use custom prompts.
3. **[Configuration Setup](#2.3)**: Switch from OpenAI to Anthropic, Groq, or local Ollama models.

---

# Page: Installation Methods

# Installation Methods

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [Dockerfile](Dockerfile)
- [docker-compose.yml](docker-compose.yml)
- [docs/docs/examples/custom_prompt.py](docs/docs/examples/custom_prompt.py)
- [docs/docs/examples/examples.md](docs/docs/examples/examples.md)
- [docs/docs/examples/pip-run.ipynb](docs/docs/examples/pip-run.ipynb)
- [docs/docs/examples/sample_report.py](docs/docs/examples/sample_report.py)
- [docs/docs/examples/sample_sources_only.py](docs/docs/examples/sample_sources_only.py)
- [docs/docs/gpt-researcher/context/azure-storage.md](docs/docs/gpt-researcher/context/azure-storage.md)
- [docs/docs/gpt-researcher/context/local-docs.md](docs/docs/gpt-researcher/context/local-docs.md)
- [docs/docs/gpt-researcher/getting-started/getting-started-with-docker.md](docs/docs/gpt-researcher/getting-started/getting-started-with-docker.md)
- [docs/docs/gpt-researcher/getting-started/introduction.md](docs/docs/gpt-researcher/getting-started/introduction.md)
- [docs/docs/gpt-researcher/gptr/ai-development.md](docs/docs/gpt-researcher/gptr/ai-development.md)
- [docs/docs/gpt-researcher/gptr/claude-skill.md](docs/docs/gpt-researcher/gptr/claude-skill.md)
- [docs/docs/gpt-researcher/gptr/image_generation.md](docs/docs/gpt-researcher/gptr/image_generation.md)
- [docs/docs/gpt-researcher/gptr/pip-package.md](docs/docs/gpt-researcher/gptr/pip-package.md)
- [docs/sidebars.js](docs/sidebars.js)
- [gpt_researcher/document/document.py](gpt_researcher/document/document.py)
- [pyproject.toml](pyproject.toml)
- [requirements.txt](requirements.txt)
- [setup.py](setup.py)

</details>



This page documents the four primary installation methods for GPT Researcher: pip package installation for Python integration, Docker deployment for containerized environments, git clone for development, and Claude skill installation for AI-assisted usage. Each method serves different use cases and comes with specific prerequisites and configuration steps.

For configuration of environment variables and API keys after installation, see [Configuration Setup](). For quick start usage examples, see [Quick Start Examples]().

---

## Prerequisites

All installation methods require the following prerequisites:

| Requirement | Minimum Version | Notes |
|------------|----------------|-------|
| **Python** | 3.11 | Required for LangChain v1 compatibility [requirements.txt:2](), [setup.py:44](), [pyproject.toml:10]() |
| **pip** | Latest | Python package installer |
| **API Keys** | - | At minimum: `OPENAI_API_KEY` and `TAVILY_API_KEY` [docker-compose.yml:7-9]() |

Optional but recommended:

| Tool | Purpose |
|------|---------|
| **Docker** | For containerized deployment [docs/docs/gpt-researcher/getting-started/getting-started-with-docker.md:3]() |
| **Node.js/npm** | For Claude skill installation or frontend development [docs/docs/gpt-researcher/gptr/claude-skill.md:14]() |
| **Poetry** | Alternative Python dependency manager [pyproject.toml:1]() |

**Sources:** [requirements.txt:1-3](), [setup.py:44](), [pyproject.toml:10](), [docs/docs/gpt-researcher/getting-started/getting-started-with-docker.md:3-5](), [docs/docs/gpt-researcher/gptr/claude-skill.md:14-15]()

---

## Installation Decision Flow

```mermaid
flowchart TD
    Start["Need to install<br/>GPT Researcher"] --> UseCase{What's your use case?}
    
    UseCase -->|"Integrate into<br/>existing Python app"| PIP["pip Package<br/>Installation"]
    UseCase -->|"Production deployment<br/>with frontend"| Docker["Docker<br/>Deployment"]
    UseCase -->|"Development or<br/>customization"| Clone["Git Clone<br/>Setup"]
    UseCase -->|"Use with<br/>Claude AI"| Skill["Claude Skill<br/>Installation"]
    
    PIP --> PIPSteps["1. pip install gpt-researcher<br/>2. Set API keys<br/>3. Import and use"]
    Docker --> DockerSteps["1. Install Docker<br/>2. Clone repo for docker-compose<br/>3. Configure .env<br/>4. docker-compose up"]
    Clone --> CloneSteps["1. git clone<br/>2. Install dependencies<br/>3. Configure .env<br/>4. Run server"]
    Skill --> SkillSteps["1. npx skills add<br/>2. Use in Claude"]
    
    PIPSteps --> Verify["Verify Installation"]
    DockerSteps --> Verify
    CloneSteps --> Verify
    SkillSteps --> VerifySkill["Verify in Claude"]
    
    Verify --> Done["Ready to Research"]
    VerifySkill --> Done
```

**Sources:** [docs/docs/gpt-researcher/getting-started/getting-started-with-docker.md:1-29](), [docs/docs/gpt-researcher/gptr/claude-skill.md:9-17](), [setup.py:22-45]()

---

## Method 1: pip Package Installation

The pip package installation is the simplest method for integrating GPT Researcher into existing Python applications or Jupyter notebooks.

### Installation Steps

**Step 1: Install the package**

```bash
pip install gpt-researcher
```

This installs version `0.14.7` (current latest) and all required dependencies defined in `setup.py` [setup.py:3-45]().

**Step 2: Set environment variables**

```bash
export OPENAI_API_KEY={Your OpenAI API Key}
export TAVILY_API_KEY={Your Tavily API Key}
```

**Step 3: Verify installation**

```python
from gpt_researcher import GPTResearcher
import asyncio

async def test_install():
    # Initialize the researcher agent
    researcher = GPTResearcher(query="test query")
    print(f"GPT Researcher initialized successfully")

asyncio.run(test_install())
```

### Package Contents

The pip package includes the core research engine but excludes certain heavy web dependencies like `fastapi` and `uvicorn` during the standard build to remain lightweight [setup.py:5-14]().

| Component | Description |
|-----------|-------------|
| `gpt_researcher` | Core research engine package [setup.py:26]() |
| `gpt_researcher.agent` | Main `GPTResearcher` orchestrator class |
| `gpt_researcher.document` | `DocumentLoader` for local files (PDF, docx, etc.) [gpt_researcher/document/document.py:16]() |
| `gpt_researcher.config` | `Config` management system |

**Sources:** [setup.py:3-45](), [requirements.txt:1-68](), [pyproject.toml:1-248](), [gpt_researcher/document/document.py:16-19]()

---

## Method 2: Docker Deployment

Docker deployment provides a containerized environment with both backend API and frontend applications pre-configured.

### Docker Architecture

```mermaid
graph TB
    subgraph "Docker_Compose_Services"
        GPTRService["gpt-researcher<br/>Backend Service<br/>Port: 8000<br/>Image: gptresearcher/gpt-researcher"]
        NextJSService["gptr-nextjs<br/>Frontend Service<br/>Port: 3000<br/>Image: gptresearcher/gptr-nextjs"]
        TestService["gpt-researcher-tests<br/>Test Service<br/>Profile: test"]
    end
    
    subgraph "Volumes"
        MyDocs["./my-docs<br/>Local Documents"]
        Outputs["./outputs<br/>Generated Reports"]
        Logs["./logs<br/>Application Logs"]
    end
    
    subgraph "Environment_Variables"
        EnvFile[".env File<br/>OPENAI_API_KEY<br/>TAVILY_API_KEY<br/>GOOGLE_API_KEY<br/>IMAGE_GENERATION_*"]
    end
    
    EnvFile --> GPTRService
    EnvFile --> NextJSService
    
    MyDocs --> GPTRService
    Outputs --> GPTRService
    Outputs --> NextJSService
    Logs --> GPTRService
    
    GPTRService -- "WebSocket/REST" --> NextJSService
```

**Sources:** [docker-compose.yml:1-78](), [Dockerfile:1-65]()

### Installation Steps

**Step 1: Clone repository for docker-compose**

```bash
git clone https://github.com/assafelovic/gpt-researcher.git
cd gpt-researcher
```

**Step 2: Configure environment file**

Copy the example environment file and edit it [docs/docs/gpt-researcher/getting-started/getting-started-with-docker.md:10]():

```bash
cp .env.example .env
```

**Step 3: Start services**

```bash
docker-compose up --build
```

This starts two services by default [docker-compose.yml:1-45]():
- **Backend API**: http://localhost:8000 (FastAPI server defined in `main:app` [Dockerfile:64]())
- **Frontend UI**: http://localhost:3000 (Next.js application [docker-compose.yml:45]())

### Multi-Stage Dockerfile Implementation

The `Dockerfile` uses a three-stage build process to optimize image size and security.

```mermaid
flowchart LR
    Stage1["Stage 1: install-browser<br/>Base: python:3.12-slim-bookworm<br/>Action: Install Chromium & Firefox"]
    Stage2["Stage 2: gpt-researcher-install<br/>Action: pip install requirements.txt"]
    Stage3["Stage 3: gpt-researcher<br/>Action: Create non-root user<br/>CMD: uvicorn main:app"]
    
    Stage1 --> Stage2
    Stage2 --> Stage3
```

**Key configuration in Dockerfile:**

- **Base image**: `python:3.12-slim-bookworm` [Dockerfile:3]()
- **Browser support**: Installs Chromium, Chromedriver, and Firefox-ESR for scraping [Dockerfile:6-21]()
- **Non-root user**: Runs as user `gpt-researcher` for security [Dockerfile:53-59]()
- **Default command**: `uvicorn main:app --host 0.0.0.0 --port 8000` [Dockerfile:64]()

**Sources:** [docker-compose.yml:1-78](), [Dockerfile:1-65](), [docs/docs/gpt-researcher/getting-started/getting-started-with-docker.md:1-29]()

---

## Method 3: Git Clone Setup

Git clone installation provides full repository access for development, customization, or running the complete application stack.

### Installation Steps

**Step 1: Clone the repository**

```bash
git clone https://github.com/assafelovic/gpt-researcher.git
cd gpt-researcher
```

**Step 2: Install dependencies**

The repository supports multiple dependency managers:

#### Option A: pip (Standard)
```bash
pip install -r requirements.txt
```

#### Option B: Poetry (Development)
```bash
poetry install
poetry shell
```

**Step 3: Run the FastAPI server**

```bash
python -m uvicorn main:app --reload
```

The server starts on http://localhost:8000.

### Dependency Management Details

| File | Purpose | Key Package Groups |
|------|---------|-------------------|
| `requirements.txt` | Direct dependencies | FastAPI, LangChain, LLM Providers, Retrievers [requirements.txt:5-30]() |
| `pyproject.toml` | Poetry configuration | Full dependency tree with versions [pyproject.toml:9-214]() |
| `setup.py` | pip package build | Metadata for PyPI distribution [setup.py:22-46]() |

**Sources:** [requirements.txt:1-68](), [pyproject.toml:1-248](), [setup.py:1-48]()

---

## Method 4: Claude Skill Installation

GPT Researcher can be installed as a Claude Skill, enabling Claude AI to leverage deep research capabilities within conversations and development workflows.

### Installation Steps

**Step 1: Install the skill**

```bash
npx skills add assafelovic/gpt-researcher
```

This installs the skill from the [GPT Researcher GitHub repository](https://github.com/assafelovic/gpt-researcher) [docs/docs/gpt-researcher/gptr/claude-skill.md:14-17]().

### Skill Structure

The skill is defined in the `.claude/` directory of the repository and provides Claude with context about the system architecture [docs/docs/gpt-researcher/gptr/claude-skill.md:42-61]().

| Component | Purpose |
|-----------|---------|
| `SKILL.md` | Main skill file providing core context |
| `references/architecture.md` | System architecture details |
| `references/api-reference.md` | REST and WebSocket API documentation |
| `references/config-reference.md` | Configuration reference |

**Sources:** [docs/docs/gpt-researcher/gptr/claude-skill.md:1-67]()

---

## Inline Image Generation Setup

GPT Researcher supports contextually relevant illustrations embedded directly within research reports using Google's Gemini models [docs/docs/gpt-researcher/gptr/image_generation.md:8]().

### Configuration
To enable this feature, set the following environment variables [docs/docs/gpt-researcher/gptr/image_generation.md:23-35]():

```bash
IMAGE_GENERATION_ENABLED=true
GOOGLE_API_KEY=your_google_api_key_here
IMAGE_GENERATION_MODEL=models/gemini-2.5-flash-image
IMAGE_GENERATION_MAX_IMAGES=3
```

### Data Flow for Image Generation

```mermaid
sequenceDiagram
    participant R as GPTResearcher
    participant P as Image_Planner
    participant G as Google_Gemini
    participant S as Storage_outputs_images

    R->>P: Analyze research context
    P->>G: Generate image concepts
    G-->>P: Concept identified
    P->>G: Generate image X of Y
    G-->>S: Save img_{hash}.png
    S-->>R: Return markdown link
    R->>R: Embed inline in report
```

**Sources:** [docs/docs/gpt-researcher/gptr/image_generation.md:6-170](), [docker-compose.yml:12-16]()

---

## Installation Comparison

| Aspect | pip Package | Docker | Git Clone | Claude Skill |
|--------|-------------|--------|-----------|--------------|
| **Setup Time** | < 1 minute | 5-10 minutes | 5 minutes | < 1 minute |
| **Use Case** | Python integration | Production deployment | Development | AI assistance |
| **Frontend** | ❌ | ✅ | ✅ | N/A |
| **Multi-Agent** | ❌ | ✅ | ✅ | N/A |
| **Customization** | Limited | Limited | Full | N/A |

**Sources:** [setup.py:5-14](), [docker-compose.yml:1-78](), [docs/docs/gpt-researcher/gptr/claude-skill.md:1-67]()

---

# Page: Quick Start Examples

# Quick Start Examples

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.cursorignore](.cursorignore)
- [cli.py](cli.py)
- [docs/blog/2024-09-7-hybrid-research/gptr-hybrid.png](docs/blog/2024-09-7-hybrid-research/gptr-hybrid.png)
- [docs/blog/2024-09-7-hybrid-research/index.md](docs/blog/2024-09-7-hybrid-research/index.md)
- [docs/docs/examples/custom_prompt.py](docs/docs/examples/custom_prompt.py)
- [docs/docs/examples/detailed_report.md](docs/docs/examples/detailed_report.md)
- [docs/docs/examples/examples.md](docs/docs/examples/examples.md)
- [docs/docs/examples/hybrid_research.md](docs/docs/examples/hybrid_research.md)
- [docs/docs/examples/pip-run.ipynb](docs/docs/examples/pip-run.ipynb)
- [docs/docs/examples/sample_report.py](docs/docs/examples/sample_report.py)
- [docs/docs/examples/sample_sources_only.py](docs/docs/examples/sample_sources_only.py)
- [docs/docs/gpt-researcher/getting-started/cli.md](docs/docs/gpt-researcher/getting-started/cli.md)
- [docs/docs/gpt-researcher/getting-started/getting-started.md](docs/docs/gpt-researcher/getting-started/getting-started.md)
- [docs/docs/gpt-researcher/getting-started/introduction.md](docs/docs/gpt-researcher/getting-started/introduction.md)
- [docs/docs/gpt-researcher/gptr/pip-package.md](docs/docs/gpt-researcher/gptr/pip-package.md)

</details>



## Purpose and Scope

This page provides practical, executable code examples for using GPT Researcher after installation. Examples progress from basic pip package usage to advanced configurations including FastAPI server deployment, CLI usage, and hybrid research modes. For installation instructions, see [Installation Methods](#2.1). For detailed configuration of API keys and environment variables, see [Configuration Setup](#2.3).

---

## Basic PIP Package Usage

### Minimal Research Example

The simplest way to use GPT Researcher is via the pip package with a basic query:

```python
from gpt_researcher import GPTResearcher
import asyncio

async def main():
    # Query
    query = "What happened in the latest burning man floods?"

    # Report Type
    report_type = "research_report"

    # Initialize the researcher
    researcher = GPTResearcher(query=query, report_type=report_type)
    
    # Conduct research on the given query
    await researcher.conduct_research()
    
    # Write the report
    report = await researcher.write_report()
    
    return report

if __name__ == "__main__":
    asyncio.run(main())
```

This example instantiates the `GPTResearcher` class [gpt_researcher/researcher.py]() and executes the core two-phase research workflow: `conduct_research()` for information gathering and `write_report()` for synthesis.

**Sources:** [docs/docs/examples/examples.md:4-30](), [docs/docs/gpt-researcher/gptr/pip-package.md:32-63]()

---

### Research Flow: Natural Language to Code Entities

The following diagram maps the high-level research intent to the specific classes and methods executed within the `gpt-researcher` package.

```mermaid
graph TD
    User["User Query<br/>'What is GPT Researcher?'"] --> GPTResearcher["GPTResearcher(query, report_type)"]
    
    subgraph "Execution Phase"
        GPTResearcher --> conduct_research["conduct_research()"]
        conduct_research --> ResearchConductor["ResearchConductor.conduct_research()"]
        ResearchConductor --> Context["self.context<br/>(Aggregated Research Data)"]
    end
    
    subgraph "Synthesis Phase"
        Context --> write_report["write_report(custom_prompt)"]
        write_report --> ReportGenerator["ReportGenerator.write_report()"]
        ReportGenerator --> FinalReport["Markdown Report Output"]
    end
    
    subgraph "Metadata Accessors"
        GPTResearcher --> get_costs["get_costs()"]
        GPTResearcher --> get_sources["get_research_sources()"]
        GPTResearcher --> get_images["get_research_images()"]
    end
```

**Sources:** [docs/docs/gpt-researcher/gptr/pip-package.md:36-47](), [docs/docs/examples/sample_report.py:9-22](), [docs/docs/gpt-researcher/getting-started/introduction.md:23-38]()

---

### Customizing Report Formatting

You can use `custom_prompt` to override the default generation logic and enforce specific formatting or constraints.

```python
from gpt_researcher import GPTResearcher
import asyncio

async def main():
    query = "What are the latest advancements in renewable energy?"
    researcher = GPTResearcher(query=query, report_type="research_report")
    
    await researcher.conduct_research()
    
    # Generate a short, concise report using custom_prompt
    custom_prompt = "Provide a concise summary in 2 paragraphs without citations."
    short_report = await researcher.write_report(custom_prompt=custom_prompt)
    
    # Generate a bullet-point format report
    bullet_prompt = "List the top 5 advancements as bullet points with brief explanations."
    bullet_report = await researcher.write_report(custom_prompt=bullet_prompt)
    
    return short_report, bullet_report

if __name__ == "__main__":
    asyncio.run(main())
```

**Sources:** [docs/docs/examples/examples.md:40-74](), [docs/docs/examples/sample_report.py:35-40](), [docs/docs/examples/custom_prompt.py:42-54]()

---

## Command Line Interface (CLI)

GPT Researcher includes a CLI tool (`cli.py`) for running research directly from the terminal. It handles argument parsing, asynchronous execution, and automatic file naming using an LLM-generated title.

### Basic CLI Syntax
```bash
python cli.py "What are the main causes of climate change?" --report_type research_report
```

### Advanced CLI Example
Generate a detailed, analytical report and restrict the search to specific domains:
```bash
python cli.py "Impact of AI on job markets" \
  --report_type detailed_report \
  --tone analytical \
  --query_domains "techcrunch.com,nytimes.com"
```

**CLI Arguments:**

| Argument | Description | Default |
|----------|-------------|---------|
| `query` | The research question (positional). | Required |
| `--report_type` | `research_report`, `detailed_report`, `resource_report`, etc. | Required |
| `--tone` | `objective`, `formal`, `analytical`, `persuasive`, etc. | `objective` |
| `--query_domains` | Comma-separated list of domains to search. | `""` |
| `--report_source` | `web`, `local`, `hybrid`, `azure`, `static`. | `web` |
| `--no-pdf` | Skip PDF generation. | `False` |

**Sources:** [cli.py:31-135](), [docs/docs/gpt-researcher/getting-started/cli.md:21-54]()

---

## Hybrid Research (Web + Local Docs)

Hybrid research allows the agent to combine real-time web data with your own local documents (PDF, Text, Docx, etc.) to ground findings in internal context. The system uses `load_local_documents` to process files and `RecursiveCharacterTextSplitter` for chunking.

```python
from gpt_researcher import GPTResearcher
import asyncio

async def run_hybrid_research():
    query = "How does our product roadmap compare to industry trends?"
    
    # report_source="hybrid" triggers the combination logic
    researcher = GPTResearcher(
        query=query, 
        report_type="research_report", 
        report_source="hybrid"
    )
    
    await researcher.conduct_research()
    report = await researcher.write_report()
    print(report)

if __name__ == "__main__":
    asyncio.run(run_hybrid_research())
```

**Hybrid Architecture:**

```mermaid
graph LR
    Query["User Query"] --> Planner["Planner Agent"]
    Planner --> Plan["Research Plan"]
    
    Plan --> WebSearch["Web Search<br/>(Tavily/Google)"]
    Plan --> LocalDocs["Local Documents<br/>(PDF/Docx/CSV)"]
    
    subgraph "Processing Engine"
        LocalDocs --> Load["load_local_documents()"]
        Load --> Split["RecursiveCharacterTextSplitter"]
        Split --> VectorStore["Chroma/VectorStore"]
    end
    
    WebSearch --> Retrieval["Retrieval & Summarization"]
    VectorStore --> Retrieval
    
    Retrieval --> ReportGenerator["ReportGenerator"]
    ReportGenerator --> FinalReport["Hybrid Research Report"]
```

**Sources:** [docs/docs/examples/hybrid_research.md:62-78](), [docs/blog/2024-09-7-hybrid-research/index.md:48-52](), [docs/blog/2024-09-7-hybrid-research/index.md:72-105]()

---

## Web Integration Examples

### FastAPI Server Implementation

GPT Researcher can be wrapped in a FastAPI endpoint to serve as a backend for web or mobile applications. The server is typically started using `uvicorn main:app`.

```python
from fastapi import FastAPI
from gpt_researcher import GPTResearcher
import asyncio

app = FastAPI()

@app.get("/report/{report_type}")
async def get_report(query: str, report_type: str) -> dict:
    researcher = GPTResearcher(query, report_type)
    await researcher.conduct_research()
    report = await researcher.write_report()
    
    return {
        "report": report,
        "costs": researcher.get_costs(),
        "sources": researcher.get_source_urls()
    }

# Run with: uvicorn main:app --reload
```

**Sources:** [docs/docs/gpt-researcher/gptr/pip-package.md:92-120](), [docs/docs/gpt-researcher/getting-started/getting-started.md:42-46](), [docs/docs/gpt-researcher/getting-started/getting-started.md:103-106]()

---

## Detailed Reports (STORM-inspired)

For complex topics requiring 2000+ words, use the `DetailedReport` class. It breaks the query into subtopics and researches each iteratively to avoid redundancy.

```python
import asyncio
from backend.report_type import DetailedReport
from gpt_researcher.utils.enum import Tone

async def run_detailed():
    detailed_report = DetailedReport(
        query="The future of artificial intelligence in healthcare",
        report_type="research_report",
        report_source="web_search",
        tone=Tone.FORMAL
    )

    report = await detailed_report.run()
    print(report)

if __name__ == "__main__":
    asyncio.run(run_detailed())
```

**Sources:** [docs/docs/examples/detailed_report.md:17-42](), [docs/docs/examples/detailed_report.md:48-78]()

---

## Summary of Research Outputs

When running a research task, the following metadata is accessible via the `GPTResearcher` instance:

| Method | Output Description |
|--------|--------------------|
| `get_costs()` | The total cost of the research task in USD based on token consumption. |
| `get_source_urls()` | A list of all unique URLs visited during research. |
| `get_research_context()` | The raw aggregated text chunks used to write the report. |
| `get_research_images()` | A list of image URLs found or generated during the process. |
| `get_research_sources()` | A list of source objects containing titles, content, and metadata. |

**Sources:** [docs/docs/gpt-researcher/gptr/pip-package.md:172-203](), [docs/docs/examples/sample_report.py:16-20](), [docs/docs/examples/pip-run.ipynb:55-61]()

---

# Page: Configuration Setup

# Configuration Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [docs/docs/gpt-researcher/getting-started/how-to-choose.md](docs/docs/gpt-researcher/getting-started/how-to-choose.md)
- [docs/docs/gpt-researcher/gptr/config.md](docs/docs/gpt-researcher/gptr/config.md)
- [gpt_researcher/actions/query_processing.py](gpt_researcher/actions/query_processing.py)
- [gpt_researcher/actions/retriever.py](gpt_researcher/actions/retriever.py)
- [gpt_researcher/config/variables/base.py](gpt_researcher/config/variables/base.py)
- [gpt_researcher/config/variables/default.py](gpt_researcher/config/variables/default.py)
- [gpt_researcher/retrievers/__init__.py](gpt_researcher/retrievers/__init__.py)
- [gpt_researcher/retrievers/openalex/__init__.py](gpt_researcher/retrievers/openalex/__init__.py)
- [gpt_researcher/retrievers/openalex/openalex.py](gpt_researcher/retrievers/openalex/openalex.py)
- [gpt_researcher/retrievers/utils.py](gpt_researcher/retrievers/utils.py)
- [gpt_researcher/retrievers/xquik/__init__.py](gpt_researcher/retrievers/xquik/__init__.py)
- [gpt_researcher/retrievers/xquik/xquik.py](gpt_researcher/retrievers/xquik/xquik.py)
- [multi_agents_ag2/README.md](multi_agents_ag2/README.md)
- [multi_agents_ag2/__init__.py](multi_agents_ag2/__init__.py)
- [multi_agents_ag2/agents/__init__.py](multi_agents_ag2/agents/__init__.py)
- [multi_agents_ag2/agents/editor.py](multi_agents_ag2/agents/editor.py)
- [multi_agents_ag2/agents/orchestrator.py](multi_agents_ag2/agents/orchestrator.py)
- [multi_agents_ag2/main.py](multi_agents_ag2/main.py)

</details>



This page covers the initial configuration steps required to get GPT Researcher operational after installation. For comprehensive configuration parameter documentation, see [Configuration Parameters Reference](#5.2). For the underlying configuration architecture, see [Config Class Architecture](#5.1). For a complete list of environment variables, see [Environment Variables Reference](#5.3).

---

## Purpose and Scope

Configuration setup involves three essential tasks:

1.  **Setting required API keys** for LLM and search providers.
2.  **Configuring environment variables** for basic operational parameters.
3.  **Understanding configuration precedence** between environment variables, JSON files, and defaults.

This is a prerequisite for running GPT Researcher in any deployment mode (CLI, Docker, or web interface).

---

## Configuration Architecture Overview

GPT Researcher uses a three-tier configuration hierarchy where settings cascade from environment variables through JSON configuration files to hard-coded defaults.

### Configuration Loading Flow

```mermaid
graph TB
    subgraph "Configuration_Sources"
        ENV["Environment Variables<br/>.env file or export"]
        JSON["config.json<br/>Optional JSON file"]
        DEFAULT["DEFAULT_CONFIG<br/>gpt_researcher/config/variables/default.py"]
    end
    
    subgraph "Configuration_Loading"
        Config["Config Class<br/>gpt_researcher/config/config.py"]
    end
    
    subgraph "Application_Layer"
        GPTResearcher["GPTResearcher Agent<br/>gpt_researcher/agent.py"]
        MultiAgent["Multi-Agent System<br/>multi_agents_ag2/main.py"]
        Backend["FastAPI Backend<br/>backend/server/server.py"]
    end
    
    ENV -->|Highest Priority| Config
    JSON -->|Overrides Defaults| Config
    DEFAULT -->|Lowest Priority| Config
    
    Config --> GPTResearcher
    Config --> MultiAgent
    Config --> Backend
```

**Sources:** [gpt_researcher/config/variables/default.py:3-54](), [.env.example:1-45](), [docs/docs/gpt-researcher/gptr/config.md:16-38](), [multi_agents_ag2/main.py:12-34]()

---

## Required API Keys

GPT Researcher requires two API keys for basic operation:

| API Key | Provider | Purpose | Acquisition |
| :--- | :--- | :--- | :--- |
| `OPENAI_API_KEY` | OpenAI | LLM operations (`FAST_LLM`, `SMART_LLM`, `STRATEGIC_LLM`) | [platform.openai.com](https://platform.openai.com) |
| `TAVILY_API_KEY` | Tavily | Web search and retrieval (Default) | [app.tavily.com](https://app.tavily.com) |

### Setting API Keys via Environment Variables

**Option 1: .env File (Recommended)**
Create a `.env` file in the project root based on the example provided in the codebase.
```bash
# .env
OPENAI_API_KEY=sk-...
TAVILY_API_KEY=tvly-...
```

**Option 2: Direct Export (Linux/macOS)**
```bash
export OPENAI_API_KEY=sk-...
export TAVILY_API_KEY=tvly-...
```

**Sources:** [.env.example:1-2](), [docs/docs/gpt-researcher/gptr/config.md:8-11](), [gpt_researcher/config/variables/default.py:4-9]()

---

## Essential vs Optional Configuration

The system maps natural language configuration needs to specific code entities within the `BaseConfig` typed dictionary.

### Configuration Categories and Code Entities

```mermaid
graph LR
    subgraph "Essential_Configuration"
        OPENAI["OPENAI_API_KEY<br/>LLM provider"]
        TAVILY["TAVILY_API_KEY<br/>Search provider"]
    end
    
    subgraph "Scraper_&_Performance"
        SCRAPER["SCRAPER<br/>'bs' (BeautifulSoup)"]
        WORKERS["MAX_SCRAPER_WORKERS<br/>Default: 15"]
        DELAY["SCRAPER_RATE_LIMIT_DELAY<br/>Default: 0.0"]
    end
    
    subgraph "Deep_Research_&_Logic"
        BREADTH["DEEP_RESEARCH_BREADTH<br/>Default: 3"]
        DEPTH["DEEP_RESEARCH_DEPTH<br/>Default: 2"]
        REASONING["REASONING_EFFORT<br/>'medium'"]
    end
    
    subgraph "Retrieval_&_Sources"
        RETRIEVER["RETRIEVER<br/>'tavily'"]
        DOC_PATH["DOC_PATH<br/>'./my-docs'"]
        MCP["MCP_SERVERS<br/>[]"]
    end
    
    OPENAI --> System["GPT Researcher System"]
    TAVILY --> System
    SCRAPER --> System
    WORKERS --> System
    DELAY --> System
    BREADTH --> System
    DEPTH --> System
    REASONING --> System
    RETRIEVER --> System
    DOC_PATH --> System
    MCP --> System
```

**Sources:** [gpt_researcher/config/variables/base.py:5-51](), [gpt_researcher/config/variables/default.py:3-54](), [.env.example:7-37]()

---

## Environment Variables Reference

### Core & LLM Configuration
| Variable | Default | Description |
| :--- | :--- | :--- |
| `RETRIEVER` | `tavily` | Web search engine. Options: `duckduckgo`, `bing`, `google`, `serper`, `arxiv`, `mcp`, etc. |
| `FAST_LLM` | `openai:gpt-4o-mini` | Model for fast tasks like summaries. |
| `SMART_LLM` | `openai:gpt-4.1` | Model for report generation. |
| `STRATEGIC_LLM` | `openai:o4-mini` | Model for research planning. |
| `TEMPERATURE` | `0.4` | LLM sampling temperature. |

### Scraper & Performance
| Variable | Default | Description |
| :--- | :--- | :--- |
| `MAX_SCRAPER_WORKERS` | `15` | Max concurrent browser instances. |
| `SCRAPER_RATE_LIMIT_DELAY` | `0.0` | Seconds between requests (0 = no limit). |
| `COMPRESSION_THRESHOLD` | `8000` | Skip embedding-based compression for content smaller than this (in chars). |

### Deep Research & Advanced Settings
| Variable | Default | Description |
| :--- | :--- | :--- |
| `DEEP_RESEARCH_BREADTH` | `3` | Parallel paths to explore in deep research. |
| `DEEP_RESEARCH_DEPTH` | `2` | Sequential search iterations in deep research. |
| `REASONING_EFFORT` | `medium` | Effort level for strategic models (o1/o3). |
| `IMAGE_GENERATION_ENABLED` | `False` | Master switch for inline image generation. |

**Sources:** [gpt_researcher/config/variables/default.py:3-54](), [.env.example:7-37](), [docs/docs/gpt-researcher/gptr/config.md:53-103](), [gpt_researcher/actions/retriever.py:35-103]()

---

## Configuration File Setup (Optional)

For complex setups or version-controlled configurations, use a `config.json` file.

### Creating a config.json
The JSON keys must match the attributes in `BaseConfig` defined in `gpt_researcher/config/variables/base.py`.

```json
{
  "RETRIEVER": "tavily",
  "EMBEDDING": "openai:text-embedding-3-small",
  "FAST_LLM": "openai:gpt-4o-mini",
  "SMART_LLM": "openai:gpt-4.1",
  "STRATEGIC_LLM": "openai:o4-mini",
  "MAX_ITERATIONS": 3,
  "DOC_PATH": "./my-docs",
  "IMAGE_GENERATION_ENABLED": true
}
```

### Applying the Configuration
**Via CLI:**
```bash
python gpt_researcher/main.py --config_path my_config.json
```

**Via Python API:**
```python
from gpt_researcher import GPTResearcher

researcher = GPTResearcher(
    query="How does quantum computing affect cybersecurity?",
    config_path="./my_config.json"
)
```

**Sources:** [docs/docs/gpt-researcher/gptr/config.md:16-44](), [gpt_researcher/config/variables/base.py:5-51]()

---

## Configuration Hierarchy and Precedence

The configuration system resolves parameters using the following priority (highest to lowest):

1.  **Environment Variables**: Set via shell `export` or `.env` file.
2.  **JSON Configuration**: Passed via the `config_path` parameter.
3.  **Default Configuration**: Defined in `gpt_researcher/config/variables/default.py`.

### Precedence Resolution Logic

```mermaid
graph TB
    subgraph "Priority_1:_Environment"
        ENV_RET["RETRIEVER=bing"]
    end
    
    subgraph "Priority_2:_config.json"
        JSON_RET["RETRIEVER: google"]
        JSON_ITER["MAX_ITERATIONS: 5"]
    end
    
    subgraph "Priority_3:_default.py"
        DEF_RET["RETRIEVER: tavily"]
        DEF_ITER["MAX_ITERATIONS: 3"]
        DEF_LANG["LANGUAGE: english"]
    end
    
    subgraph "Resulting_Config"
        RES_RET["RETRIEVER: bing (from ENV)"]
        RES_ITER["MAX_ITERATIONS: 5 (from JSON)"]
        RES_LANG["LANGUAGE: english (from DEFAULT)"]
    end
    
    ENV_RET -.->|Overrides| JSON_RET
    JSON_RET -.->|Overrides| DEF_RET
    JSON_ITER -.->|Overrides| DEF_ITER
    
    ENV_RET --> RES_RET
    JSON_ITER --> RES_ITER
    DEF_LANG --> RES_LANG
```

**Sources:** [gpt_researcher/config/variables/default.py:3-54](), [docs/docs/gpt-researcher/gptr/config.md:1-49]()

---

## Multi-Agent Configuration

When using the multi-agent system (e.g., via `ChiefEditorAgent`), the configuration can also be influenced by a `task.json` file.

*   The `ChiefEditorAgent` reads `task.json` to define the research query and model.
*   It specifically looks for the `STRATEGIC_LLM` environment variable to override the model specified in `task.json`.

**Sources:** [multi_agents_ag2/main.py:15-34](), [multi_agents_ag2/agents/orchestrator.py:43-53]()

---

## Observability & Debugging

For production deployments, it is recommended to enable LangSmith tracing for enhanced observability of agent workflows.

### LangChain Tracing Setup
Add these to your `.env` file:
```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT="gpt-researcher"
```

**Sources:** [.env.example:39-45]()

---

## Verification Steps

After setting up your configuration, verify the implementation:

1.  **Check Scraper Workers**: Ensure `MAX_SCRAPER_WORKERS` aligns with your provider's limits (e.g., Firecrawl Free allows 2 concurrent browsers) [.env.example:11-17]().
2.  **Validate Doc Path**: If `REPORT_SOURCE` is set to `doc`, ensure the directory at `DOC_PATH` exists and contains supported files [.env.example:3-4](), [gpt_researcher/config/variables/default.py:30]().
3.  **Strategic Model Check**: If using `o1` or `o3` for `STRATEGIC_LLM`, the system automatically handles `reasoning_effort` and retries if token limits cause failures [gpt_researcher/actions/query_processing.py:72-108](), [gpt_researcher/config/variables/default.py:9]().

**Sources:** [.env.example:1-45](), [gpt_researcher/config/variables/default.py:3-54](), [gpt_researcher/actions/query_processing.py:72-108]()

---

# Page: Core Architecture

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README-ja_JP.md](README-ja_JP.md)
- [README-ko_KR.md](README-ko_KR.md)
- [README-zh_CN.md](README-zh_CN.md)
- [README.md](README.md)
- [docs/CNAME](docs/CNAME)
- [docs/docs/contribute.md](docs/docs/contribute.md)
- [gpt_researcher/agent.py](gpt_researcher/agent.py)
- [gpt_researcher/skills/browser.py](gpt_researcher/skills/browser.py)
- [gpt_researcher/skills/researcher.py](gpt_researcher/skills/researcher.py)

</details>



## Purpose and Scope

This document describes the core architectural components of GPT Researcher and how they interact to orchestrate research workflows. It covers the central classes (`GPTResearcher`, `ResearchConductor`, `Config`), the skill-based architecture, and the data flow through the research pipeline.

For detailed information about specific components:
- Individual GPTResearcher class methods: see [GPTResearcher Agent Class](#3.1)
- Research workflow details: see [ResearchConductor and Workflow](#3.2)
- Skill manager implementations: see [Skill Managers and Components](#3.3)
- Prompt generation and model support: see [Prompt Management System](#3.4)

---

## System Component Overview

The GPT Researcher architecture consists of a central orchestrator (`GPTResearcher` class) that delegates specialized tasks to skill managers. Each skill manager is responsible for a specific aspect of the research process.

### Core Component Hierarchy

```mermaid
graph TB
    User["User/API Client"]
    
    subgraph "Main Orchestrator"
        GPTResearcher["GPTResearcher<br/>(gpt_researcher/agent.py:36)"]
        Config["Config<br/>(gpt_researcher/config.py:20)"]
    end
    
    subgraph "Skill Managers"
        ResearchConductor["ResearchConductor<br/>(gpt_researcher/skills/researcher.py:21)"]
        ReportGenerator["ReportGenerator<br/>(gpt_researcher/skills/writer.py:30)"]
        ContextManager["ContextManager<br/>(gpt_researcher/skills/context_manager.py:25)"]
        BrowserManager["BrowserManager<br/>(gpt_researcher/skills/browser.py:14)"]
        SourceCurator["SourceCurator<br/>(gpt_researcher/skills/curator.py:27)"]
        DeepResearchSkill["DeepResearchSkill<br/>(gpt_researcher/skills/deep_research.py:27)"]
    end
    
    subgraph "Utility Modules"
        LLMUtils["create_chat_completion<br/>(gpt_researcher/utils/llm.py:32)"]
        PromptFamily["get_prompt_family<br/>(gpt_researcher/prompts.py:23)"]
        Memory["Memory<br/>(gpt_researcher/memory.py:22)"]
        GenericLLM["GenericLLMProvider<br/>(gpt_researcher/llm_provider.py:21)"]
    end
    
    subgraph "Data Sources"
        Retrievers["get_retrievers<br/>(gpt_researcher/actions/agent_creator.py:16)"]
        Scrapers["scrape_urls<br/>(gpt_researcher/actions/web_scraping.py:10)"]
        VectorStore["VectorStoreWrapper<br/>(gpt_researcher/vector_store.py:33)"]
    end
    
    User -->|"__init__(query, ...)"| GPTResearcher
    User -->|"conduct_research()"| GPTResearcher
    User -->|"write_report()"| GPTResearcher
    
    GPTResearcher -->|"Loads"| Config
    GPTResearcher -->|"Instantiates"| ResearchConductor
    GPTResearcher -->|"Instantiates"| ReportGenerator
    GPTResearcher -->|"Instantiates"| ContextManager
    GPTResearcher -->|"Instantiates"| BrowserManager
    GPTResearcher -->|"Instantiates"| SourceCurator
    
    ResearchConductor -->|"Uses"| Retrievers
    ResearchConductor -->|"Uses"| BrowserManager
    ResearchConductor -->|"Uses"| ContextManager
    
    ReportGenerator -->|"Uses"| LLMUtils
    ReportGenerator -->|"Uses"| PromptFamily
    
    ContextManager -->|"Uses"| Memory
    BrowserManager -->|"Uses"| Scrapers
    
    LLMUtils -->|"get_llm()"| GenericLLM
```

**Purpose**: This diagram shows the class-level architecture. `GPTResearcher` acts as a facade, instantiating and coordinating specialized skill managers that handle everything from web browsing to final report writing.

**Sources**: [gpt_researcher/agent.py:36-83](), [gpt_researcher/skills/researcher.py:21-47](), [gpt_researcher/skills/browser.py:14-35]()

---

## GPTResearcher: The Central Orchestrator

The `GPTResearcher` class serves as the main entry point for all research operations. It maintains research state, coordinates skill managers, and exposes the primary API.

### Initialization and State

The `GPTResearcher.__init__()` method [gpt_researcher/agent.py:52-136]() accepts extensive configuration parameters including the research query, report type (defined in `ReportType` enum [gpt_researcher/utils/enum.py:17]()), and source preferences (defined in `ReportSource` enum [gpt_researcher/utils/enum.py:17]()).

### State Management

The class maintains several critical state variables to track research progress:

```python
# Core state (gpt_researcher/agent.py:138-167)
self.query: str                    # Research query
self.context: list                 # Accumulated research context
self.visited_urls: set             # Deduplicate sources
self.research_sources: list        # Scraped content with metadata
self.research_images: list         # Selected images
self.research_costs: float         # Accumulated API costs
self.agent: str                    # Agent type (e.g., "Business Analyst")
self.role: str                     # Agent role prompt
```

### Skill Manager Instantiation

During initialization, `GPTResearcher` instantiates its skill managers [gpt_researcher/agent.py:24-30]():

```python
self.research_conductor = ResearchConductor(self)
self.report_generator = ReportGenerator(self)
self.context_manager = ContextManager(self)
self.scraper_manager = BrowserManager(self)
self.source_curator = SourceCurator(self)
self.image_generator = ImageGenerator(self)
self.deep_research_skill = DeepResearchSkill(self)
```

Each manager receives a reference to the parent `GPTResearcher` instance, allowing them to access configuration, shared state, and other managers.

**Sources**: [gpt_researcher/agent.py:24-30](), [gpt_researcher/agent.py:138-167](), [gpt_researcher/utils/enum.py:17-17]()

---

## Configuration System

The `Config` class [gpt_researcher/config.py:20]() manages settings with a hierarchy: environment variables override file-based configurations, which override defaults.

### LLM Tier Strategy

GPT Researcher utilizes a three-tier LLM strategy to balance cost and performance:

*   **FAST_LLM**: Used for quick summarization and extraction tasks.
*   **SMART_LLM**: Used for complex analysis and final report generation.
*   **STRATEGIC_LLM**: Used for high-level research planning and query decomposition.

The system supports specialized parameters like `mcp_strategy` to handle Model Context Protocol integration during research [gpt_researcher/agent.py:132-135]().

**Sources**: [gpt_researcher/agent.py:140-142](), [gpt_researcher/agent.py:132-135]()

---

## Research Workflow and Data Flow

The research process follows a structured pipeline managed by the `ResearchConductor` [gpt_researcher/skills/researcher.py:89]().

### Research Execution Pipeline

```mermaid
graph TD
    Start["conduct_research()<br/>(gpt_researcher/skills/researcher.py:89)"]
    
    ChooseAgent["choose_agent()<br/>(gpt_researcher/actions/agent_creator.py:102)"]
    
    Plan["plan_research()<br/>(gpt_researcher/skills/researcher.py:48)"]
    
    WebSearch["_get_context_by_web_search()<br/>(gpt_researcher/skills/researcher.py:243)"]
    
    Scrape["BrowserManager.browse_urls()<br/>(gpt_researcher/skills/browser.py:37)"]
    
    Context["ContextManager.get_similar_content()<br/>(gpt_researcher/skills/context_manager.py:58)"]
    
    Start --> ChooseAgent
    ChooseAgent --> Plan
    Plan --> WebSearch
    WebSearch --> Scrape
    Scrape --> Context
```

**Purpose**: This diagram bridges the Natural Language task to Code Entities by showing the sequence of method calls across different skill managers during a standard research run.

### Parallel Sub-Query Processing

To ensure comprehensive coverage, the `ResearchConductor` decomposes the main query into multiple sub-queries using `plan_research_outline` [gpt_researcher/skills/researcher.py:75-85](). These queries are then processed to gather context from various sources including web search, local documents, or hybrid sources [gpt_researcher/skills/researcher.py:135-161]().

**Sources**: [gpt_researcher/skills/researcher.py:48-87](), [gpt_researcher/skills/researcher.py:135-161]()

---

## Skill Manager Components

The architecture delegates logic to specialized "Skills":

*   **ResearchConductor**: Manages query planning, retriever selection, and the overall research loop [gpt_researcher/skills/researcher.py:21]().
*   **BrowserManager**: Handles parallel web scraping using a `WorkerPool` and selects relevant images from scraped pages [gpt_researcher/skills/browser.py:14-35]().
*   **ContextManager**: Performs context management and retrieval from accumulated research data [gpt_researcher/skills/context_manager.py:25]().
*   **ReportGenerator**: Orchestrates the writing of the final report [gpt_researcher/skills/writer.py:30]().
*   **SourceCurator**: Handles the curation and validation of research sources [gpt_researcher/skills/curator.py:27]().
*   **DeepResearchSkill**: Manages recursive deep research tasks [gpt_researcher/skills/deep_research.py:27]().

**Sources**: [gpt_researcher/agent.py:24-30](), [gpt_researcher/skills/browser.py:32-35]()

---

## Prompt Management System

The system uses a prompt family hierarchy to support different model families and task-specific requirements.

### Prompt Generation Flow

```mermaid
graph LR
    Agent["GPTResearcher"]
    GetFamily["get_prompt_family()<br/>(gpt_researcher/prompts.py:23)"]
    
    subgraph "Prompt Hierarchy"
        Base["PromptFamily<br/>(gpt_researcher/prompts.py:39)"]
    end
    
    Writer["ReportGenerator"]
    
    Agent --> GetFamily
    GetFamily --> Base
    Writer -->|"Uses prompts via"| Base
```

The `get_prompt_family` function [gpt_researcher/prompts.py:23]() determines the appropriate prompt set based on the configured model or family name, ensuring compatibility across different LLM providers.

**Sources**: [gpt_researcher/prompts.py:23-36](), [gpt_researcher/agent.py:168-169]()

---

# Page: GPTResearcher Agent Class

# GPTResearcher Agent Class

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [gpt_researcher/agent.py](gpt_researcher/agent.py)
- [gpt_researcher/config/config.py](gpt_researcher/config/config.py)
- [gpt_researcher/llm_provider/__init__.py](gpt_researcher/llm_provider/__init__.py)
- [gpt_researcher/skills/browser.py](gpt_researcher/skills/browser.py)
- [gpt_researcher/skills/researcher.py](gpt_researcher/skills/researcher.py)
- [gpt_researcher/utils/llm.py](gpt_researcher/utils/llm.py)

</details>



## Purpose and Scope

This page documents the `GPTResearcher` class, the central orchestrator and entry point for all research operations in the GPT Researcher system. The class encapsulates the complete research lifecycle from initialization through query execution to report generation. It acts as a facade that coordinates various specialized "skills" such as browsing, context management, and report writing.

The `GPTResearcher` class is defined in [gpt_researcher/agent.py:36-720]() and serves as the main API for both programmatic usage (via the pip package) and backend integration (via the FastAPI server).

---

## Class Overview and Architecture

The `GPTResearcher` class implements a **composition-based architecture**. Instead of handling all logic internally, it instantiates and delegates to specialized skill classes that manage distinct aspects of the research pipeline.

### Class Definition and Composition Pattern

```mermaid
classDiagram
    class GPTResearcher["GPTResearcher (gpt_researcher/agent.py)"] {
        +str query
        +str report_type
        +Config cfg
        +list context
        +float research_costs
        +set visited_urls
        +list research_sources
        +list research_images
        +ResearchConductor research_conductor
        +ReportGenerator report_generator
        +ContextManager context_manager
        +BrowserManager scraper_manager
        +SourceCurator source_curator
        +DeepResearchSkill deep_researcher
        +ImageGenerator image_generator
        +Memory memory
        +conduct_research()
        +write_report()
        +write_introduction()
        +write_report_conclusion()
        +quick_search()
        +get_subtopics()
        +add_costs()
    }
    
    class ResearchConductor["ResearchConductor (gpt_researcher/skills/researcher.py)"] {
        +GPTResearcher researcher
        +plan_research()
        +conduct_research()
    }
    
    class ReportGenerator["ReportGenerator (gpt_researcher/skills/writer.py)"] {
        +GPTResearcher researcher
        +write_report()
        +write_report_conclusion()
        +write_introduction()
    }
    
    class ContextManager["ContextManager (gpt_researcher/skills/context_manager.py)"] {
        +GPTResearcher researcher
        +get_similar_content_by_query()
        +get_similar_content_by_query_with_vectorstore()
    }
    
    class BrowserManager["BrowserManager (gpt_researcher/skills/browser.py)"] {
        +GPTResearcher researcher
        +WorkerPool worker_pool
        +browse_urls()
        +select_top_images()
    }
    
    class SourceCurator["SourceCurator (gpt_researcher/skills/curator.py)"] {
        +GPTResearcher researcher
        +curate_sources()
    }
    
    class Config["Config (gpt_researcher/config/config.py)"] {
        +str smart_llm_model
        +str fast_llm_model
        +str strategic_llm_model
        +list retrievers
    }
    
    class Memory["Memory (gpt_researcher/memory/__init__.py)"] {
        +get_embeddings()
    }
    
    GPTResearcher *-- ResearchConductor
    GPTResearcher *-- ReportGenerator
    GPTResearcher *-- ContextManager
    GPTResearcher *-- BrowserManager
    GPTResearcher *-- SourceCurator
    GPTResearcher *-- Config
    GPTResearcher *-- Memory
```

**Sources:** [gpt_researcher/agent.py:36-195](), [gpt_researcher/skills/researcher.py:21-47](), [gpt_researcher/skills/writer.py:20-47](), [gpt_researcher/skills/context_manager.py:18-35](), [gpt_researcher/skills/browser.py:14-35](), [gpt_researcher/skills/curator.py:15-31](), [gpt_researcher/config/config.py:19-61]()

---

## Initialization Parameters

The `GPTResearcher` constructor accepts a comprehensive set of parameters defined in [gpt_researcher/agent.py:52-136](). These parameters allow fine-grained control over the research behavior.

### Core Research Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | Required | The research question or topic to investigate. |
| `report_type` | `str` | `"research_report"` | Type of report: `research_report`, `detailed_report`, `subtopic_report`, `deep`. |
| `report_source` | `str` | `"web"` | Data source: `web`, `local`, `hybrid`, `azure`, `langchain_documents`, `langchain_vectorstore`. |
| `tone` | `Tone` | `Tone.Objective` | Writing tone (e.g., Analytical, Formal). |
| `verbose` | `bool` | `True` | Whether to output progress logs. |

**Sources:** [gpt_researcher/agent.py:52-83](), [gpt_researcher/utils/enum.py:6-27]()

### Source and Retrieval Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `source_urls` | `list[str]` | `None` | Specific URLs to use as sources (bypasses search). |
| `document_urls` | `list[str]` | `None` | URLs for online document loading. |
| `query_domains` | `list[str]` | `None` | Restrict web search to specific domains. |
| `vector_store` | `Any` | `None` | Pre-existing vector store for retrieval via `VectorStoreWrapper`. |
| `mcp_configs` | `list[dict]` | `None` | Configurations for Model Context Protocol servers. |
| `mcp_strategy` | `str` | `"fast"` | MCP execution strategy: `fast`, `deep`, or `disabled`. |

**Sources:** [gpt_researcher/agent.py:59-65](), [gpt_researcher/agent.py:79-82](), [gpt_researcher/agent.py:153]()

---

## Initialization Flow

The initialization process sets up the configuration, identifies the appropriate prompt family, and instantiates all skill managers.

### Initialization Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant GPTResearcher["GPTResearcher (gpt_researcher/agent.py)"]
    participant Config["Config (gpt_researcher/config/config.py)"]
    participant PromptFamily["PromptFamily (gpt_researcher/prompts/__init__.py)"]
    participant Memory["Memory (gpt_researcher/memory/__init__.py)"]
    participant SkillManagers["Skill Managers (gpt_researcher/skills/*)"]
    
    User->>GPTResearcher: __init__(query, report_type, ...)
    GPTResearcher->>Config: Config(config_path)
    Config->>Config: _set_llm_attributes()
    Config-->>GPTResearcher: cfg instance
    
    GPTResearcher->>GPTResearcher: Process MCP and Retrievers
    
    GPTResearcher->>PromptFamily: get_prompt_family(prompt_family, cfg)
    PromptFamily-->>GPTResearcher: prompt_family instance
    
    GPTResearcher->>Memory: Memory(embedding_provider, embedding_model)
    Memory-->>GPTResearcher: memory instance
    
    GPTResearcher->>SkillManagers: Initialize Skill Classes
    Note over SkillManagers: ResearchConductor, ReportGenerator,<br/>ContextManager, BrowserManager,<br/>SourceCurator, ImageGenerator
    
    GPTResearcher-->>User: Initialized agent
```

**Sources:** [gpt_researcher/agent.py:137-197](), [gpt_researcher/config/config.py:34-61](), [gpt_researcher/config/config.py:91-96]()

---

## Primary Research Methods

The core research workflow is orchestrated through two primary methods: `conduct_research()` and `write_report()`.

### conduct_research() Method

This method is the main entry point for the information-gathering phase. It determines the agent's persona and triggers the search and scraping process.

```python
async def conduct_research(self):
    """Runs the GPT Researcher to conduct research"""
```

**Key Operations:**
1. **Persona Selection**: If `agent` and `role` are not provided, it calls `choose_agent()` to generate a persona based on the query [gpt_researcher/agent.py:358-365]().
2. **Workflow Delegation**: It delegates the actual research logic to `research_conductor.conduct_research()` [gpt_researcher/agent.py:372]().
3. **Deep Research**: If `report_type` is `"deep"`, it triggers the `deep_researcher.run()` logic [gpt_researcher/agent.py:346-355]().
4. **Image Generation**: If configured, it triggers `image_generator.plan_and_generate_images()` after context gathering [gpt_researcher/agent.py:385-391]().

**Sources:** [gpt_researcher/agent.py:328-395](), [gpt_researcher/skills/researcher.py:89-160]()

### write_report() Method

This method synthesizes the gathered context into a structured report.

```python
async def write_report(self, existing_headers=[], relevant_written_contents=[], ext_context=None, custom_prompt=""):
    """Write the research report based on gathered context"""
```

**Key Operations:**
1. **Context Preparation**: Uses either the internal `self.context` or provided `ext_context` [gpt_researcher/agent.py:465]().
2. **Skill Delegation**: Calls `report_generator.write_report()` with parameters like tone, query, and context [gpt_researcher/agent.py:481]().
3. **Subtopic Handling**: If generating a `subtopic_report`, it passes the main topic and existing headers to ensure continuity [gpt_researcher/agent.py:471-477]().

**Sources:** [gpt_researcher/agent.py:445-485](), [gpt_researcher/skills/writer.py:49-123]()

---

## State and Data Management

The `GPTResearcher` class maintains several internal lists and sets to track the state of the research process.

| Attribute | Type | Purpose |
|-----------|------|---------|
| `context` | `list` | Stores the synthesized/compressed context used for writing. |
| `visited_urls` | `set` | Tracks URLs already scraped to prevent redundant work [gpt_researcher/agent.py:160](). |
| `research_sources` | `list[dict]` | Stores the raw scraped content, titles, and images [gpt_researcher/agent.py:150](). |
| `research_costs` | `float` | Tracks the total API cost of the current session [gpt_researcher/agent.py:164](). |
| `research_images` | `list` | Stores URLs of images selected during scraping [gpt_researcher/agent.py:151](). |

**Sources:** [gpt_researcher/agent.py:149-166]()

### Cost Tracking

Costs are tracked using the `add_costs(cost)` method, which is passed as a callback to LLM utility functions [gpt_researcher/agent.py:703-720](). The utility `create_chat_completion` calculates costs via `calculate_llm_cost` and updates the agent through this callback [gpt_researcher/utils/llm.py:134-144]().

---

## Utility Methods

The class provides several helper methods for post-processing and metadata retrieval.

| Method | Purpose | Source |
|--------|---------|--------|
| `quick_search()` | Performs a fast search and optional summary without the full agent cycle. | [gpt_researcher/agent.py:512-544]() |
| `get_subtopics()` | Generates a list of subtopics for the main query using `construct_subtopics`. | [gpt_researcher/agent.py:546-563]() |
| `add_references()` | Appends a bibliography/references section to the report. | [gpt_researcher/agent.py:626-636]() |
| `extract_sections()` | Parses a markdown report into individual sections. | [gpt_researcher/agent.py:648-658]() |

**Sources:** [gpt_researcher/utils/llm.py:152-193]()

---

## MCP and Strategy Resolution

The agent handles Model Context Protocol (MCP) by resolving a strategy (`fast`, `deep`, or `disabled`) during initialization [gpt_researcher/agent.py:213-277]().

- **Fast Strategy**: MCP is run once with the original query to gather initial context [gpt_researcher/agent.py:228]().
- **Deep Strategy**: MCP is triggered for every sub-query generated during the research planning phase [gpt_researcher/agent.py:230]().
- **Disabled**: MCP retrievers are ignored.

**Sources:** [gpt_researcher/agent.py:213-307]()

---

# Page: ResearchConductor and Workflow

# ResearchConductor and Workflow

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/gpt-researcher/gptr/config.md](docs/docs/gpt-researcher/gptr/config.md)
- [gpt_researcher/actions/agent_creator.py](gpt_researcher/actions/agent_creator.py)
- [gpt_researcher/actions/query_processing.py](gpt_researcher/actions/query_processing.py)
- [gpt_researcher/actions/utils.py](gpt_researcher/actions/utils.py)
- [gpt_researcher/agent.py](gpt_researcher/agent.py)
- [gpt_researcher/config/variables/base.py](gpt_researcher/config/variables/base.py)
- [gpt_researcher/config/variables/default.py](gpt_researcher/config/variables/default.py)
- [gpt_researcher/skills/browser.py](gpt_researcher/skills/browser.py)
- [gpt_researcher/skills/curator.py](gpt_researcher/skills/curator.py)
- [gpt_researcher/skills/researcher.py](gpt_researcher/skills/researcher.py)
- [gpt_researcher/utils/costs.py](gpt_researcher/utils/costs.py)
- [gpt_researcher/utils/tools.py](gpt_researcher/utils/tools.py)
- [tests/test_costs.py](tests/test_costs.py)
- [tests/test_llm_usage_tracking.py](tests/test_llm_usage_tracking.py)

</details>



## Purpose and Scope

This document explains the `ResearchConductor` class and the research workflow it orchestrates within GPT Researcher. The `ResearchConductor` is a specialized skill manager responsible for coordinating the multi-stage research process, including query planning, sub-query generation, parallel data gathering from multiple sources, and context aggregation.

It acts as the operational engine for the `GPTResearcher` agent, translating a high-level research goal into a series of executable technical steps across web retrievers, local documents, and Model Context Protocol (MCP) servers.

**Sources:** [gpt_researcher/skills/researcher.py:1-32](), [gpt_researcher/agent.py:29-30]()

## ResearchConductor in the Architecture

The `ResearchConductor` is instantiated during the initialization of the `GPTResearcher` class. It maintains a reference to its parent researcher instance to access shared configuration, memory, and WebSocket communication channels.

### Code Entity Association

The following diagram bridges the high-level research concepts to the specific classes and methods implemented in the codebase.

```mermaid
graph TB
    GPTResearcher["class GPTResearcher<br/>(gpt_researcher/agent.py)"]
    
    subgraph "Skill Managers (gpt_researcher/skills/)"
        ResearchConductor["class ResearchConductor<br/>(researcher.py)"]
        BrowserManager["class BrowserManager<br/>(browser.py)"]
        ContextManager["class ContextManager<br/>(context_manager.py)"]
        SourceCurator["class SourceCurator<br/>(curator.py)"]
        ReportGenerator["class ReportGenerator<br/>(writer.py)"]
    end
    
    subgraph "Core Actions (gpt_researcher/actions/)"
        Plan["plan_research_outline()<br/>(query_processing.py)"]
        Search["get_search_results()<br/>(query_processing.py)"]
        Scrape["scrape_urls()<br/>(web_scraping.py)"]
    end
    
    GPTResearcher -->|"self.research_conductor ="| ResearchConductor
    GPTResearcher -->|"calls conduct_research()"| ResearchConductor
    
    ResearchConductor -->|"calls"| Plan
    ResearchConductor -->|"calls"| Search
    ResearchConductor -->|"calls"| BrowserManager
    
    BrowserManager -->|"calls"| Scrape
    ResearchConductor -->|"calls"| ContextManager
    ResearchConductor -->|"calls"| SourceCurator
```

**Sources:** [gpt_researcher/agent.py:182-190](), [gpt_researcher/skills/researcher.py:34-46]()

## Core Workflow Stages

The `ResearchConductor.conduct_research()` method is the primary entry point for the research execution logic. It follows a structured pipeline:

1.  **Initialization**: Clears `visited_urls`, resets `research_data`, and logs active retrievers [gpt_researcher/skills/researcher.py:91-102]().
2.  **Agent Selection**: If not predefined, it calls `choose_agent()` to assign a persona and role based on the query [gpt_researcher/skills/researcher.py:119-127]().
3.  **Source Routing**: Determines the research path based on `self.researcher.report_source` (e.g., "web", "local", "hybrid") [gpt_researcher/skills/researcher.py:135-191]().
4.  **Context Gathering**: Executes the selected retrieval strategy (Web Search, Local Document Loading, or Vector Store Querying).
5.  **Curation (Optional)**: If `cfg.curate_sources` is enabled, it uses the `SourceCurator` to rank and filter results [gpt_researcher/skills/researcher.py:195-207]().

### Detailed Research Flow

```mermaid
flowchart TD
    Start["conduct_research()"] --> Agent{"Agent & Role<br/>Set?"}
    Agent -- "No" --> Choose["choose_agent()"]
    Agent -- "Yes" --> Source{"report_source?"}
    Choose --> Source
    
    Source -- "web" --> Web["_get_context_by_web_search()"]
    Source -- "local" --> Local["DocumentLoader.load()"]
    Source -- "hybrid" --> Hybrid["Local Docs + Web Search"]
    Source -- "vectorstore" --> VS["_get_context_by_vectorstore()"]
    
    Local --> Web
    Hybrid --> Web
    
    Web --> CurateCheck{"cfg.curate_sources?"}
    VS --> CurateCheck
    
    CurateCheck -- "Yes" --> Curator["SourceCurator.curate_sources()"]
    CurateCheck -- "No" --> Final["Set researcher.context"]
    Curator --> Final
```

**Sources:** [gpt_researcher/skills/researcher.py:89-211]()

## Query Planning and Decomposition

Before searching, the system decomposes the main query into sub-queries to ensure breadth. This is handled by `plan_research()`.

1.  **Initial Search**: Calls `get_search_results()` with the original query to get baseline context [gpt_researcher/skills/researcher.py:62]().
2.  **Outline Generation**: Calls `plan_research_outline()`, which uses the `STRATEGIC_LLM` to generate a list of focused sub-queries [gpt_researcher/skills/researcher.py:75-85]().
3.  **MCP Optimization**: If only an `MCPRetriever` is used, sub-query generation is skipped to prevent redundant iterations [gpt_researcher/actions/query_processing.py:145-153]().

**Sources:** [gpt_researcher/skills/researcher.py:48-87](), [gpt_researcher/actions/query_processing.py:112-169]()

## Web Search and Sub-Query Processing

The method `_get_context_by_web_search()` manages parallel execution across multiple retrievers and sub-queries.

### MCP Execution Strategies

The system implements specific logic for Model Context Protocol (MCP) servers via the `mcp_strategy` configuration [gpt_researcher/config/variables/default.py:44]().

| Strategy | Behavior | Implementation |
| :--- | :--- | :--- |
| **fast** | Runs MCP once with the original query; caches results for all sub-queries. | `_mcp_results_cache` [gpt_researcher/skills/researcher.py:44]() |
| **deep** | Runs MCP research for every generated sub-query. | `_execute_mcp_research_for_queries()` [gpt_researcher/skills/researcher.py:393]() |
| **disabled** | Skips MCP retrievers entirely. | `_get_mcp_strategy()` check [gpt_researcher/skills/researcher.py:283]() |

### Parallel Execution Diagram

```mermaid
sequenceDiagram
    participant RC as ResearchConductor
    participant WP as WorkerPool
    participant BM as BrowserManager
    participant CM as ContextManager

    RC->>RC: plan_research() -> sub_queries[]
    
    par For each sub_query
        RC->>RC: _process_sub_query(sub_query)
        RC->>RC: _execute_mcp_research() (if deep)
        RC->>BM: browse_urls(retriever_results)
        BM->>WP: Parallel Scrape
        WP-->>BM: raw_content[]
        BM-->>RC: scraped_data[]
        RC->>CM: get_similar_content_by_query()
        CM-->>RC: compressed_context
    end
    
    RC->>RC: aggregate all compressed_context
```

**Sources:** [gpt_researcher/skills/researcher.py:348-365](), [gpt_researcher/skills/researcher.py:449-578](), [gpt_researcher/skills/browser.py:32-35]()

## Key Implementation Details

### Browser and Scraper Integration
The `BrowserManager` utilizes a `WorkerPool` to parallelize the scraping of URLs discovered by retrievers. It also handles image selection via `select_top_images`, filtering by image hash to avoid duplicates [gpt_researcher/skills/browser.py:32-35](), [gpt_researcher/skills/browser.py:86-115]().

### Context Compression
The `ContextManager` uses specialized compressors to reduce raw scraped text into relevant snippets. It performs similarity searches to select the top results based on embeddings generated for the query and document chunks.

### Source Curation
If `CURATE_SOURCES` is `True` [gpt_researcher/config/variables/default.py:14](), the `SourceCurator` performs an LLM-based evaluation of all gathered sources. It uses the `SMART_LLM` to rank sources by credibility and relevance, returning a structured JSON list of verified references [gpt_researcher/skills/curator.py:58-85]().

## Configuration Summary

The behavior of the `ResearchConductor` is governed by the following key variables in `BaseConfig`:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `RETRIEVER` | `"tavily"` | Primary web search provider [gpt_researcher/config/variables/default.py:4]() |
| `MAX_SEARCH_RESULTS_PER_QUERY` | `5` | Results per sub-query [gpt_researcher/config/variables/default.py:18]() |
| `MAX_SCRAPER_WORKERS` | `15` | Concurrency for web scraping [gpt_researcher/config/variables/default.py:25]() |
| `MCP_STRATEGY` | `"fast"` | Execution mode for MCP servers [gpt_researcher/config/variables/default.py:44]() |
| `CURATE_SOURCES` | `False` | Whether to run the SourceCurator skill [gpt_researcher/config/variables/default.py:14]() |

**Sources:** [gpt_researcher/config/variables/default.py:1-54](), [gpt_researcher/config/variables/base.py:5-51]()

---

# Page: Skill Managers and Components

# Skill Managers and Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/report_type/deep_research/example.py](backend/report_type/deep_research/example.py)
- [frontend/nextjs/styles/markdown.css](frontend/nextjs/styles/markdown.css)
- [gpt_researcher/actions/report_generation.py](gpt_researcher/actions/report_generation.py)
- [gpt_researcher/llm_provider/image/__init__.py](gpt_researcher/llm_provider/image/__init__.py)
- [gpt_researcher/llm_provider/image/image_generator.py](gpt_researcher/llm_provider/image/image_generator.py)
- [gpt_researcher/llm_provider/image/modelslab_image_generator.py](gpt_researcher/llm_provider/image/modelslab_image_generator.py)
- [gpt_researcher/skills/__init__.py](gpt_researcher/skills/__init__.py)
- [gpt_researcher/skills/context_manager.py](gpt_researcher/skills/context_manager.py)
- [gpt_researcher/skills/deep_research.py](gpt_researcher/skills/deep_research.py)
- [gpt_researcher/skills/image_generator.py](gpt_researcher/skills/image_generator.py)
- [gpt_researcher/skills/writer.py](gpt_researcher/skills/writer.py)
- [gpt_researcher/utils/rate_limiter.py](gpt_researcher/utils/rate_limiter.py)
- [gpt_researcher/utils/workers.py](gpt_researcher/utils/workers.py)
- [tests/test_deep_research_parsing.py](tests/test_deep_research_parsing.py)

</details>



This document describes the specialized skill manager components that `GPTResearcher` orchestrates to conduct research operations. Each skill manager encapsulates specific functionality—data acquisition, content generation, context management, web scraping, source evaluation, and image generation. For the main orchestration workflow, see [ResearchConductor and Workflow]().

## Skill Manager Architecture

GPTResearcher implements a **component-based architecture** where specialized skill managers handle distinct aspects of the research pipeline. All skill managers are instantiated during `GPTResearcher.__init__` and maintain a reference to their parent researcher instance.

### Component Initialization Pattern

[gpt_researcher/agent.py:182-193]()

```python
# All managers receive the researcher instance for shared state access
self.research_conductor: ResearchConductor = ResearchConductor(self)
self.report_generator: ReportGenerator = ReportGenerator(self)
self.context_manager: ContextManager = ContextManager(self)
self.scraper_manager: BrowserManager = BrowserManager(self)
self.source_curator: SourceCurator = SourceCurator(self)
self.deep_researcher: Optional[DeepResearchSkill] = None
if report_type == ReportType.DeepResearch.value:
    self.deep_researcher = DeepResearchSkill(self)
self.image_generator: Optional[ImageGenerator] = ImageGenerator(self)
```

Each skill manager follows the **strategy pattern**, encapsulating complex operations while maintaining access to shared researcher state (config, memory, websocket, costs).

**Sources:** [gpt_researcher/agent.py:182-193](), [gpt_researcher/agent.py:27-30]()

---

## Skill Manager Component Diagram

```mermaid
graph TB
    subgraph GPTResearcher["GPTResearcher (agent.py)"]
        MainAgent["Main Agent Instance<br/>- query<br/>- context<br/>- cfg: Config<br/>- memory: Memory<br/>- visited_urls: set"]
    end
    
    subgraph SkillManagers["Skill Manager Components"]
        ResearchConductor["ResearchConductor<br/>(skills/researcher.py)<br/>Data Acquisition"]
        ReportGenerator["ReportGenerator<br/>(skills/writer.py)<br/>Content Generation"]
        ContextManager["ContextManager<br/>(skills/context_manager.py)<br/>Context Compression"]
        BrowserManager["BrowserManager<br/>(skills/browser.py)<br/>Web Scraping"]
        SourceCurator["SourceCurator<br/>(skills/curator.py)<br/>Source Ranking"]
        ImageGenerator["ImageGenerator<br/>(skills/image_generator.py)<br/>Image Generation"]
        DeepResearchSkill["DeepResearchSkill<br/>(skills/deep_research.py)<br/>Iterative Research"]
    end
    
    subgraph SupportComponents["Support Components"]
        ImageProvider["ImageGeneratorProvider<br/>(llm_provider/image/image_generator.py)"]
        WorkerPool["WorkerPool<br/>(utils/workers.py)"]
        GlobalLimiter["GlobalRateLimiter<br/>(utils/rate_limiter.py)"]
        Compressors["ContextCompressor<br/>VectorstoreCompressor<br/>WrittenContentCompressor"]
    end
    
    MainAgent -->|"instantiates"| ResearchConductor
    MainAgent -->|"instantiates"| ReportGenerator
    MainAgent -->|"instantiates"| ContextManager
    MainAgent -->|"instantiates"| BrowserManager
    MainAgent -->|"instantiates"| SourceCurator
    MainAgent -->|"instantiates"| ImageGenerator
    MainAgent -->|"instantiates"| DeepResearchSkill
    
    ResearchConductor -->|"uses"| BrowserManager
    ResearchConductor -->|"uses"| ContextManager
    ResearchConductor -->|"uses"| SourceCurator
    
    BrowserManager -->|"uses"| WorkerPool
    WorkerPool -->|"throttles via"| GlobalLimiter
    
    ContextManager -->|"uses"| Compressors
    
    ImageGenerator -->|"uses"| ImageProvider
    
    ReportGenerator -->|"calls"| ImageGenerator
```

**Sources:** [gpt_researcher/agent.py:182-193](), [gpt_researcher/skills/context_manager.py:18-35](), [gpt_researcher/utils/workers.py:9-34](), [gpt_researcher/utils/rate_limiter.py:13-37](), [gpt_researcher/skills/image_generator.py:33-46]()

---

## ResearchConductor

**Purpose:** Orchestrates the data acquisition phase including query planning, retrieval execution, MCP integration, and context gathering.

**Location:** [gpt_researcher/skills/researcher.py:21-46]()

### Core Responsibilities

| Responsibility | Methods | Description |
|---------------|---------|-------------|
| Query Planning | `plan_research()` | Generates sub-queries from main query using `plan_research_outline` [gpt_researcher/skills/researcher.py:48-87]() |
| Research Execution | `conduct_research()` | Main entry point coordinating all research operations [gpt_researcher/skills/researcher.py:89-211]() |
| URL Scraping | `_get_context_by_urls()` | Processes specific source URLs via `scraper_manager` [gpt_researcher/skills/researcher.py:213-241]() |
| Web Search | `_get_context_by_web_search()` | Executes multi-retriever web search with MCP integration [gpt_researcher/skills/researcher.py:243-264]() |
| MCP Optimization | `_execute_mcp_research()` | Handles Model Context Protocol retriever strategy [gpt_researcher/skills/researcher.py:367-447]() |
| Sub-Query Processing | `_process_sub_query()` | Parallel processing of decomposed queries [gpt_researcher/skills/researcher.py:449-578]() |

**Sources:** [gpt_researcher/skills/researcher.py:89-211](), [gpt_researcher/skills/researcher.py:243-264]()

---

## DeepResearchSkill

**Purpose:** Implements the recursive, tree-like research mode which explores topics with configurable depth and breadth.

**Location:** [gpt_researcher/skills/deep_research.py:7-35]()

### Implementation Details
The `DeepResearchSkill` uses specialized parsing logic to handle JSON responses from reasoning models (like `o3-mini`). It manages its own `visited_urls` and `learnings` state to avoid redundancy during deep exploration.

| Function | Role |
|----------|------|
| `parse_search_queries_response` | Extracts `query` and `researchGoal` from LLM JSON or text blocks [gpt_researcher/skills/deep_research.py:77-116]() |
| `parse_research_results_response` | Extracts `learnings`, `followUpQuestions`, and `citations` from search results [gpt_researcher/skills/deep_research.py:143-201]() |
| `_extract_json_payloads` | Utility to find JSON blocks within messy LLM output using regex [gpt_researcher/skills/deep_research.py:48-60]() |

**Sources:** [gpt_researcher/skills/deep_research.py:7-116](), [backend/report_type/deep_research/example.py:32-53]()

---

## ReportGenerator

**Purpose:** Handles all report writing operations including introductions, conclusions, and final report compilation.

**Location:** [gpt_researcher/skills/writer.py:20-48]()

### Core Responsibilities

| Responsibility | Methods | Description |
|---------------|---------|-------------|
| Report Writing | `write_report()` | Main report generation with image embedding [gpt_researcher/skills/writer.py:49-123]() |
| Introduction | `write_introduction()` | Generate introduction section via `write_report_introduction` [gpt_researcher/skills/writer.py:164-193]() |
| Conclusion | `write_report_conclusion()` | Generate conclusion section via `write_conclusion` [gpt_researcher/skills/writer.py:125-162]() |
| Subtopic Generation | `get_subtopics()` | Extract subtopics for detailed reports [gpt_researcher/skills/writer.py:195-212]() |

**Sources:** [gpt_researcher/skills/writer.py:49-123](), [gpt_researcher/actions/report_generation.py:12-60]()

---

## ContextManager

**Purpose:** Manages context retrieval, compression, and similarity matching for research queries using embeddings and vector operations.

**Location:** [gpt_researcher/skills/context_manager.py:18-35]()

### Core Responsibilities

| Responsibility | Methods | Description |
|---------------|---------|-------------|
| Query-Based Retrieval | `get_similar_content_by_query()` | Find similar content from scraped pages using `ContextCompressor` [gpt_researcher/skills/context_manager.py:37-63]() |
| Vectorstore Retrieval | `get_similar_content_by_query_with_vectorstore()` | Query vector stores using `VectorstoreCompressor` [gpt_researcher/skills/context_manager.py:65-86]() |
| Written Content Matching | `get_similar_written_contents_by_draft_section_titles()` | Find relevant previously written content via `WrittenContentCompressor` [gpt_researcher/skills/context_manager.py:88-118]() |

**Sources:** [gpt_researcher/skills/context_manager.py:37-118](), [gpt_researcher/context/compression.py:11-15]()

---

## BrowserManager and WorkerPool

**Purpose:** Handles web scraping and content extraction from URLs using a throttled parallel worker pool.

### BrowserManager
**Location:** [gpt_researcher/skills/browser.py:14-35]()
- **`browse_urls()`**: Initiates parallel scraping of multiple URLs [gpt_researcher/skills/browser.py:37-84]().
- **`select_top_images()`**: Deduplicates and ranks images found during scraping [gpt_researcher/skills/browser.py:86-115]().

### WorkerPool and Rate Limiting
**Location:** [gpt_researcher/utils/workers.py:8-28]()
The `WorkerPool` uses an `asyncio.Semaphore` to limit concurrency and a `GlobalRateLimiter` to enforce delays across all instances.
- **`throttle()`**: An async context manager that waits for both a semaphore slot and the global rate limiter [gpt_researcher/utils/workers.py:35-50]().
- **`GlobalRateLimiter`**: A singleton that ensures `rate_limit_delay` is respected globally (e.g., for Firecrawl limits) [gpt_researcher/utils/rate_limiter.py:13-37]().

**Sources:** [gpt_researcher/utils/workers.py:35-50](), [gpt_researcher/utils/rate_limiter.py:60-80](), [gpt_researcher/skills/browser.py:37-84]()

---

## ImageGenerator

**Purpose:** Generates contextually relevant AI images for research reports.

**Location:** [gpt_researcher/skills/image_generator.py:20-46]()

### Image Generation Workflow

```mermaid
graph LR
    Context["Research Context"] --> Plan["plan_and_generate_images()"]
    Plan --> Concepts["_plan_image_concepts()<br/>(Identify 2-3 visual themes)"]
    Concepts --> ParallelGen["asyncio.gather()<br/>(Generate via Provider)"]
    ParallelGen --> Embed["process_image_placeholders()<br/>(Insert into Markdown)"]
```

- **`plan_and_generate_images()`**: Analyzes context to identify visualization opportunities before report writing [gpt_researcher/skills/image_generator.py:77-180]().
- **`process_image_placeholders()`**: Scans the final report for `[IMAGE: ...]` tags and replaces them with actual image Markdown [gpt_researcher/skills/image_generator.py:104-176]().

**Sources:** [gpt_researcher/skills/image_generator.py:77-180](), [gpt_researcher/skills/image_generator.py:104-176]()

---

## SourceCurator

**Purpose:** Evaluates and ranks research sources based on relevance and credibility using LLM-based assessment.

**Location:** [gpt_researcher/skills/curator.py:15-31]()

- **`curate_sources()`**: Filters and ranks scraped data to ensure only high-quality information enters the final context [gpt_researcher/skills/curator.py:33-96]().

**Sources:** [gpt_researcher/skills/curator.py:33-96]()

---

# Page: Prompt Management System

# Prompt Management System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.python-version](.python-version)
- [gpt_researcher/config/config.py](gpt_researcher/config/config.py)
- [gpt_researcher/llm_provider/__init__.py](gpt_researcher/llm_provider/__init__.py)
- [gpt_researcher/prompts.py](gpt_researcher/prompts.py)
- [gpt_researcher/utils/enum.py](gpt_researcher/utils/enum.py)
- [gpt_researcher/utils/llm.py](gpt_researcher/utils/llm.py)
- [tests/test_quick_search.py](tests/test_quick_search.py)

</details>



The Prompt Management System provides a flexible, extensible architecture for generating and managing prompts used throughout the research pipeline. This system abstracts prompt formatting away from business logic, enabling model-specific customizations (such as Granite support) while maintaining a consistent interface across all research operations.

---

## System Architecture

The prompt management system uses a class-based hierarchy where a base `PromptFamily` class defines the standard interface, and derived classes can override specific prompt generation methods to accommodate model-specific requirements.

### PromptFamily Class Hierarchy

The following diagram illustrates how `PromptFamily` is integrated into the core agent and its skills.

**Prompt Management Integration**
```mermaid
graph TB
    subgraph "Configuration Layer"
        Config["Config"]
        EnvVar["PROMPT_FAMILY<br/>Environment Variable"]
    end
    
    subgraph "Prompt Selection"
        GetPromptFamily["get_prompt_family()"]
        PromptFamilyEnum["PromptFamilyEnum"]
    end
    
    subgraph "PromptFamily Classes"
        BaseFamily["PromptFamily"]
        GraniteFamily["Granite-Specific Families"]
    end
    
    subgraph "Core Agent & Utilities"
        GPTResearcher["GPTResearcher"]
        LLMUtils["gpt_researcher/utils/llm.py"]
    end
    
    subgraph "Prompt Methods"
        SearchQueries["generate_search_queries_prompt"]
        ReportPrompt["generate_report_prompt"]
        MCPPrompts["generate_mcp_research_prompt"]
        SubtopicsPrompt["generate_subtopics_prompt"]
    end
    
    EnvVar --> Config
    Config --> GetPromptFamily
    PromptFamilyEnum --> GetPromptFamily
    
    GetPromptFamily --> BaseFamily
    
    BaseFamily --> GPTResearcher
    LLMUtils --> SubtopicsPrompt
    
    GPTResearcher --> SearchQueries
    GPTResearcher --> ReportPrompt
    GPTResearcher --> MCPPrompts
```
**Sources:** [gpt_researcher/prompts.py:14-23](), [gpt_researcher/utils/enum.py:94-101](), [gpt_researcher/config/config.py:19-75](), [gpt_researcher/utils/llm.py:152-178]()

---

## PromptFamily Base Class

The `PromptFamily` class serves as the foundation for all prompt generation. It is initialized with a `Config` instance and provides methods broken down into two functional groups.

### Initialization and Flow

The prompt family is instantiated and used to drive research logic. The system parses the desired prompt family from the configuration or environment variables.

**Initialization Data Flow**
```mermaid
graph LR
    subgraph "Initialization Source"
        CfgFamily["cfg.prompt_family"]
        EnvFamily["PROMPT_FAMILY"]
    end
    
    subgraph "Agent & Utility Setup"
        AgentInit["GPTResearcher"]
        LLMUtilCall["construct_subtopics"]
    end
    
    subgraph "Execution"
        PromptGen["PromptFamily.generate_subtopics_prompt()"]
    end
    
    CfgFamily --> AgentInit
    EnvFamily --> LLMUtilCall
    LLMUtilCall --> PromptGen
```
**Sources:** [gpt_researcher/prompts.py:14-36](), [gpt_researcher/utils/llm.py:152-178](), [gpt_researcher/config/config.py:71-75]()

### Method Categories

The `PromptFamily` class [gpt_researcher/prompts.py:14-29]() organizes methods into:

1.  **Prompt Generators**: Standardized formats correlated with the `ReportType` enum (e.g., `generate_report_prompt`).
2.  **Prompt Methods**: Situation-specific methods with unique signatures (e.g., `generate_mcp_tool_selection_prompt`).

---

## Prompt Generation Categories

### Research Planning & MCP Prompts

These prompts orchestrate query decomposition and the Model Context Protocol (MCP) integration.

*   **`generate_mcp_tool_selection_prompt`**: Generates a prompt for LLM-based tool selection, returning JSON with relevance scores [gpt_researcher/prompts.py:40-83]().
*   **`generate_mcp_research_prompt`**: Instructs the LLM on how to execute research using the selected tools [gpt_researcher/prompts.py:86-118]().
*   **`construct_subtopics` utility**: Uses `prompt_family.generate_subtopics_prompt()` to create a research plan based on the task and available data [gpt_researcher/utils/llm.py:152-178]().

**Sources:** [gpt_researcher/prompts.py:40-118](), [gpt_researcher/utils/llm.py:152-178]()

### Image Generation Prompts

The prompt family includes logic to identify and describe visual needs for reports:

1.  **`generate_image_analysis_prompt`**: Analyzes report sections to determine which benefit most from visuals (diagrams, flowcharts, etc.) [gpt_researcher/prompts.py:122-175]().
2.  **`generate_image_prompt_enhancement`**: Refines a base prompt with report context to ensure high-quality, professional illustrations [gpt_researcher/prompts.py:178-192]().

**Sources:** [gpt_researcher/prompts.py:122-192]()

---

## Model-Specific Support (Granite, etc.)

The system identifies model-specific needs through the `PromptFamily` enum and the `prompt_family` configuration string.

### Granite Support
The system includes specific support for the IBM Granite model family:
*   `Granite` (General)
*   `Granite3`, `Granite3.1`, `Granite3.2`, `Granite3.3`

These are defined in the `PromptFamily` enum [gpt_researcher/utils/enum.py:94-101](). When a Granite family is selected, the system can override base prompts to match the specific instruction-following nuances of these models.

### Integration with LLM Utilities
The `create_chat_completion` utility [gpt_researcher/utils/llm.py:41-146]() and `construct_subtopics` [gpt_researcher/utils/llm.py:152-178]() utilize these prompts. `construct_subtopics` specifically takes a `prompt_family` argument (defaulting to the base `PromptFamily` class) to structure the hierarchical research plan [gpt_researcher/utils/llm.py:157]().

**Sources:** [gpt_researcher/utils/enum.py:94-101](), [gpt_researcher/utils/llm.py:41-178]()

---

## Extension Guide

To add a new prompt family (e.g., for a new model provider):

1.  **Define the Enum**: Add the new family name to `PromptFamily` in `gpt_researcher/utils/enum.py` [gpt_researcher/utils/enum.py:94-101]().
2.  **Subclass PromptFamily**: Create a new class in `gpt_researcher/prompts.py` inheriting from `PromptFamily` [gpt_researcher/prompts.py:14-29]().
3.  **Override Methods**: Implement specific logic for prompts that require model-specific formatting (e.g., custom delimiters or instruction styles).
4.  **Configuration**: Set the `PROMPT_FAMILY` environment variable to your new enum value to trigger the logic in the `Config` class [gpt_researcher/config/config.py:71-75]().

**Sources:** [gpt_researcher/prompts.py:14-29](), [gpt_researcher/utils/enum.py:94-101](), [gpt_researcher/config/config.py:71-75]()

---

# Page: Research Modes

# Research Modes

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README-ja_JP.md](README-ja_JP.md)
- [README-ko_KR.md](README-ko_KR.md)
- [README-zh_CN.md](README-zh_CN.md)
- [README.md](README.md)
- [backend/report_type/basic_report/basic_report.py](backend/report_type/basic_report/basic_report.py)
- [backend/report_type/detailed_report/detailed_report.py](backend/report_type/detailed_report/detailed_report.py)
- [backend/server/multi_agent_runner.py](backend/server/multi_agent_runner.py)
- [backend/server/server_utils.py](backend/server/server_utils.py)
- [backend/server/websocket_manager.py](backend/server/websocket_manager.py)
- [docs/CNAME](docs/CNAME)
- [docs/docs/contribute.md](docs/docs/contribute.md)
- [docs/docs/gpt-researcher/getting-started/how-to-choose.md](docs/docs/gpt-researcher/getting-started/how-to-choose.md)
- [frontend/index.html](frontend/index.html)
- [frontend/scripts.js](frontend/scripts.js)
- [frontend/styles.css](frontend/styles.css)
- [multi_agents_ag2/README.md](multi_agents_ag2/README.md)
- [multi_agents_ag2/__init__.py](multi_agents_ag2/__init__.py)
- [multi_agents_ag2/agents/__init__.py](multi_agents_ag2/agents/__init__.py)
- [multi_agents_ag2/agents/editor.py](multi_agents_ag2/agents/editor.py)
- [multi_agents_ag2/agents/orchestrator.py](multi_agents_ag2/agents/orchestrator.py)
- [multi_agents_ag2/main.py](multi_agents_ag2/main.py)
- [tests/test_websocket_manager.py](tests/test_websocket_manager.py)

</details>



GPT Researcher provides several distinct research modes, each optimized for different use cases, depth requirements, and output formats. This page provides a high-level overview of the available modes, their characteristics, and guidance on when to use each.

## Overview of Research Modes

The system supports four primary research approaches, ranging from fast summaries to hierarchical deep dives and multi-agent collaborative workflows.

| Mode | Report Type | Primary Use Case | Execution Time | Output Length |
|------|-------------|------------------|----------------|---------------|
| **Standard** | `research_report` | General-purpose research on focused topics | ~2 min | ~1,200 words |
| **Detailed** | `detailed_report` | Hierarchical exploration of subtopics | ~5 min | ~3,000+ words |
| **Deep** | `deep` | Tree-like recursive exploration with reasoning | ~5-10 min | 4,000+ words |
| **Multi-Agent** | `multi_agents` | High-quality reports with peer review | ~10-15 min | 5-10 pages |

Sources: [frontend/index.html:171-174](), [backend/report_type/detailed_report/detailed_report.py:50-51](), [backend/server/websocket_manager.py:134-164]()

## Research Mode Architecture

The following diagram illustrates how the system routes a user query to different execution engines based on the selected `report_type`.

### System Routing Logic
```mermaid
graph TD
    subgraph "User Interface"
        UI["Frontend / API Call"]
    end

    subgraph "Orchestration Layer"
        WSM["WebSocketManager<br/>backend/server/websocket_manager.py"]
        RA["run_agent()<br/>backend/server/websocket_manager.py"]
    end

    subgraph "Execution Engines"
        BR["BasicReport<br/>backend/report_type/basic_report/basic_report.py"]
        DR["DetailedReport<br/>backend/report_type/detailed_report/detailed_report.py"]
        GR["GPTResearcher<br/>gpt_researcher/agent.py"]
        MAR["run_multi_agent_task<br/>backend/server/multi_agent_runner.py"]
    end

    UI -->|"POST / WebSocket"| WSM
    WSM --> RA
    RA -->|"research_report"| BR
    RA -->|"detailed_report"| DR
    RA -->|"multi_agents"| MAR
    
    BR --> GR
    DR -->|"Subtopic instances"| GR
```
Sources: [backend/server/websocket_manager.py:106-180](), [backend/report_type/detailed_report/detailed_report.py:67-124](), [backend/report_type/basic_report/basic_report.py:41-60](), [backend/server/server_utils.py:126-173]()

## Research Workflow Comparison

The internal logic of each mode differs in how it handles query decomposition and context gathering.

### Logic Flow by Mode
```mermaid
graph LR
    subgraph "Standard Mode"
        S1["Query"] --> S2["Plan Outline"]
        S2 --> S3["Search & Scrape"]
        S3 --> S4["Write Report"]
    end
    
    subgraph "Detailed Mode"
        D1["Query"] --> D2["Initial Research"]
        D2 --> D3["Identify Subtopics"]
        D3 --> D4["Recursive Research<br/>per Subtopic"]
        D4 --> D5["Stitch Report"]
    end
    
    subgraph "Deep Mode"
        DP1["Query"] --> DP2["Recursive Tree<br/>Exploration"]
        DP2 --> DP3["Breadth x Depth"]
        DP3 --> DP4["Aggregate Context"]
    end
```
Sources: [backend/report_type/detailed_report/detailed_report.py:84-91](), [backend/report_type/basic_report/basic_report.py:72-75](), [README.md:62-67]()

---

## Mode Details

### 4.1 Standard Research Mode
The default mode for quick and focused research. It performs a single pass of parallel web searching based on generated sub-queries to provide a concise yet comprehensive summary.
* **Core Entity:** `BasicReport` in [backend/report_type/basic_report/basic_report.py:9-25]()
* **Workflow:** Calls `conduct_research` and `write_report` on a single `GPTResearcher` instance [backend/report_type/basic_report/basic_report.py:72-75]().
* For details, see [Standard Research Mode](#4.1).

### 4.2 Detailed Report Mode
A hierarchical approach that first performs broad research to identify key subtopics, then initializes separate `GPTResearcher` instances for each subtopic to ensure maximum depth.
* **Core Entity:** `DetailedReport` in [backend/report_type/detailed_report/detailed_report.py:10-28]()
* **Workflow:** Executes `_initial_research`, calls `_get_all_subtopics`, and then runs `_generate_subtopic_reports` to process each section [backend/report_type/detailed_report/detailed_report.py:84-91]().
* For details, see [Detailed Report Mode](#4.2).

### 4.3 Deep Research Mode
Designed for complex topics requiring tree-like recursive exploration. It is inspired by "Plan-and-Solve" methodologies to address speed and reliability through parallelized work.
* **Core Entity:** `GPTResearcher` (with deep configuration) in [gpt_researcher/agent.py]()
* **Workflow:** Utilizes parallel execution agents to gather information for objective conclusions [README.md:54-60]().
* For details, see [Deep Research Mode](#4.3).

### 4.4 Multi-Agent Framework
A sophisticated framework where specialized agents collaborate. It leverages LangGraph or AG2 to manage stateful interactions between planning, execution, and publishing agents.
* **Core Entity:** `run_multi_agent_task` in [backend/server/multi_agent_runner.py]() (referenced in [backend/server/websocket_manager.py:135-141]())
* **Workflow:** A state-machine driven process that includes planning, research, review, and publication stages [README.md:54-60]().
* For details, see [Multi-Agent Framework](#4.4).

---

## Configuration & Routing

Modes are programmatically selected in the backend based on the `report_type` string received via the API or WebSocket.

```python
# Routing logic in backend/server/websocket_manager.py:134-176
if report_type == "multi_agents":
    report = await run_multi_agent_task(...)
elif report_type == ReportType.DetailedReport.value:
    researcher = DetailedReport(...)
    report = await researcher.run()
else:
    researcher = BasicReport(...)
    report = await researcher.run()
```

Sources: [backend/server/websocket_manager.py:134-176](), [backend/report_type/detailed_report/detailed_report.py:47-67](), [backend/report_type/basic_report/basic_report.py:41-60]()

---

# Page: Standard Research Mode

# Standard Research Mode

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/report_type/basic_report/basic_report.py](backend/report_type/basic_report/basic_report.py)
- [backend/report_type/detailed_report/detailed_report.py](backend/report_type/detailed_report/detailed_report.py)
- [backend/server/multi_agent_runner.py](backend/server/multi_agent_runner.py)
- [backend/server/server_utils.py](backend/server/server_utils.py)
- [backend/server/websocket_manager.py](backend/server/websocket_manager.py)
- [docs/docs/gpt-researcher/gptr/config.md](docs/docs/gpt-researcher/gptr/config.md)
- [frontend/index.html](frontend/index.html)
- [frontend/scripts.js](frontend/scripts.js)
- [frontend/styles.css](frontend/styles.css)
- [gpt_researcher/actions/query_processing.py](gpt_researcher/actions/query_processing.py)
- [gpt_researcher/config/variables/base.py](gpt_researcher/config/variables/base.py)
- [gpt_researcher/config/variables/default.py](gpt_researcher/config/variables/default.py)
- [tests/test_websocket_manager.py](tests/test_websocket_manager.py)

</details>



## Purpose and Scope

Standard Research Mode is the default research operation mode in GPT Researcher, designed for generating comprehensive research reports in approximately 2 minutes. This mode executes a single-pass research workflow that produces reports of 1,000-2,000 words with proper citations and structured analysis.

This document covers the `research_report` report type workflow, component interactions, and configuration. For in-depth multi-level research, see [Detailed Report Mode](4.2). For recursive tree-based exploration, see [Deep Research Mode](4.3). For multi-agent collaborative research, see [Multi-Agent Framework](4.4).

---

## Workflow Overview

Standard Research Mode executes a linear pipeline from query to report. The process involves agent selection, research planning, parallel data acquisition, context compression, optional source curation, and report generation.

### End-to-End Flow Diagram

```mermaid
graph TB
    UserQuery["User Query Input"]
    Init["GPTResearcher.__init__<br/>report_type='research_report'"]
    ConductResearch["GPTResearcher.conduct_research()"]
    ChooseAgent["choose_agent()<br/>Select agent & role"]
    PlanResearch["ResearchConductor.plan_research()<br/>Generate sub-queries"]
    ParallelProcessing["asyncio.gather()<br/>Parallel sub-query execution"]
    
    subgraph SubQueryProcessing["Per Sub-Query: _process_sub_query()"]
        SearchWeb["get_search_results()<br/>Retriever: Tavily/DuckDuckGo/etc"]
        ScrapeURLs["BrowserManager.browse_urls()<br/>scrape_urls() + WorkerPool"]
        CompressContext["ContextManager.get_similar_content_by_query()<br/>ContextCompressor with embeddings"]
    end
    
    CurateCheck{"cfg.curate_sources<br/>enabled?"}
    CurateSource["SourceCurator.curate_sources()<br/>LLM-based ranking"]
    WriteReport["GPTResearcher.write_report()<br/>ReportGenerator.write_report()"]
    GenerateReport["generate_report()<br/>Smart LLM synthesis"]
    OutputReport["Markdown Report<br/>with citations & references"]
    
    UserQuery --> Init
    Init --> ConductResearch
    ConductResearch --> ChooseAgent
    ChooseAgent --> PlanResearch
    PlanResearch --> ParallelProcessing
    ParallelProcessing --> SearchWeb
    SearchWeb --> ScrapeURLs
    ScrapeURLs --> CompressContext
    CompressContext --> CurateCheck
    CurateCheck -->|Yes| CurateSource
    CurateCheck -->|No| WriteReport
    CurateSource --> WriteReport
    WriteReport --> GenerateReport
    GenerateReport --> OutputReport
```

**Sources:** `[gpt_researcher/agent.py:52-136]()`, `[gpt_researcher/skills/researcher.py:89-169]()`, `[gpt_researcher/skills/browser.py:37-84]()`, `[gpt_researcher/skills/context_manager.py:37-63]()`

---

## Core Components

### GPTResearcher Class

The `GPTResearcher` class in `[gpt_researcher/agent.py:36-168]()` serves as the main orchestrator for standard research mode. It manages configuration via the `Config` class, coordinates skill managers, and tracks research state.

#### Initialization Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | Required | The research question or topic |
| `report_type` | `str` | `"research_report"` | Report type identifier (from `ReportType` enum) |
| `report_source` | `str` | `"web"` | Data source: web, local, hybrid, etc. |
| `tone` | `Tone` | `Tone.Objective` | Writing style for report |
| `verbose` | `bool` | `True` | Enable detailed logging |
| `max_subtopics` | `int` | `5` | Maximum sub-queries to generate |
| `websocket` | `WebSocket` | `None` | WebSocket for streaming progress updates |

**Sources:** `[gpt_researcher/agent.py:52-136]()`, `[gpt_researcher/utils/enum.py:6-45]()`

#### Core Methods

```mermaid
graph LR
    ConductResearch["GPTResearcher.conduct_research()<br/>Orchestrates research pipeline"]
    WriteReport["GPTResearcher.write_report()<br/>Generates markdown report"]
    GetCosts["GPTResearcher.get_costs()<br/>Returns total research costs"]
    AddCosts["GPTResearcher.add_costs()<br/>Accumulates LLM costs"]
    
    ConductResearch -->|"self.context"| WriteReport
    WriteReport -->|"str"| Output["Generated Markdown Report"]
    AddCosts -->|"Updates"| ConductResearch
    ConductResearch -->|"Final total"| GetCosts
```

**Sources:** `[gpt_researcher/agent.py:328-395]()`, `[gpt_researcher/agent.py:445-485]()`, `[gpt_researcher/agent.py:687-719]()`

---

### ResearchConductor

The `ResearchConductor` class manages the research execution pipeline, including query planning, parallel processing, and context gathering.

#### Research Planning

The conductor generates sub-queries to decompose the main question into researchable components using `plan_research_outline` in `[gpt_researcher/actions/query_processing.py:112-169]()`.

```mermaid
graph TB
    MainQuery["Main Query"]
    InitSearch["get_search_results()<br/>First retriever call"]
    SearchResults["Search results<br/>for context"]
    LLMPlanning["plan_research_outline()<br/>Generates sub-queries"]
    StrategicLLM["strategic_llm_model<br/>(e.g. o4-mini)"]
    SubQueries["Sub-Query List<br/>(List[str])"]
    
    MainQuery --> InitSearch
    InitSearch --> SearchResults
    SearchResults --> LLMPlanning
    LLMPlanning --> StrategicLLM
    StrategicLLM --> SubQueries
```

**Sources:** `[gpt_researcher/skills/researcher.py:48-87]()`, `[gpt_researcher/actions/query_processing.py:112-169]()`, `[gpt_researcher/config/variables/default.py:9-12]()`

#### Parallel Sub-Query Processing

Each sub-query executes independently using `asyncio.gather` for concurrent processing within `_get_context_by_web_search`.

| Step | Component | Function/Method | Description |
|------|-----------|-----------------|-------------|
| 1 | Search | `get_search_results()` | Retrieve URLs from configured retrievers |
| 2 | Scrape | `BrowserManager.browse_urls()` | Call `scrape_urls()` via WorkerPool |
| 3 | Compress | `ContextManager.get_similar_content_by_query()` | Uses `ContextCompressor` with embeddings |

**Sources:** `[gpt_researcher/skills/researcher.py:266-365]()`, `[gpt_researcher/skills/browser.py:37-84]()`, `[gpt_researcher/skills/context_manager.py:37-63]()`

---

### ContextManager

The `ContextManager` class handles content retrieval and compression, ensuring only relevant information reaches the report generator.

#### Context Compression Pipeline

```mermaid
graph TB
    ScrapedDocs["Scraped Documents<br/>(list of pages)"]
    InitCompressor["ContextCompressor.__init__<br/>(documents, embeddings)"]
    AsyncGetContext["async_get_context()<br/>(query, max_results=10)"]
    
    subgraph CompressionSteps["ContextCompressor Processing"]
        TextSplitter["RecursiveCharacterTextSplitter"]
        SimilarityFilter["Embeddings Similarity Check<br/>(threshold=0.42)"]
    end
    
    CompressedContext["Compressed Context String"]
    
    ScrapedDocs --> InitCompressor
    InitCompressor --> AsyncGetContext
    AsyncGetContext --> TextSplitter
    TextSplitter --> SimilarityFilter
    SimilarityFilter --> CompressedContext
```

**Sources:** `[gpt_researcher/skills/context_manager.py:37-63]()`, `[gpt_researcher/config/variables/default.py:6]()`

---

### SourceCurator

The `SourceCurator` class provides optional LLM-based source ranking that evaluates credibility and relevance when `cfg.curate_sources=True`.

#### Curation Process

```mermaid
graph TB
    RawSources["Raw Source Context"]
    CurateCall["SourceCurator.curate_sources()<br/>(source_data, max_results=10)"]
    LLMEval["create_chat_completion()<br/>model=smart_llm_model"]
    RankedSources["Curated Sources List<br/>(JSON format)"]
    
    RawSources --> CurateCall
    CurateCall --> LLMEval
    LLMEval --> RankedSources
```

**Sources:** `[gpt_researcher/skills/curator.py:33-96]()`, `[gpt_researcher/config/variables/default.py:14]()`

---

## Report Generation

### ReportGenerator Workflow

The `ReportGenerator` class transforms research context into a formatted markdown report using the Smart LLM tier.

#### Report Writing Process

```mermaid
graph TB
    WriteReportCall["GPTResearcher.write_report()"]
    ReportGenInit["ReportGenerator.write_report()"]
    SendImages["stream_output('images')"]
    CallGenerate["generate_report()<br/>(Smart LLM synthesis)"]
    FinalReport["Markdown Report"]
    
    WriteReportCall --> ReportGenInit
    ReportGenInit --> SendImages
    SendImages --> CallGenerate
    CallGenerate --> FinalReport
```

**Sources:** `[gpt_researcher/skills/writer.py:49-123]()`, `[gpt_researcher/actions/report_generation.py:209-250]()`

---

## Configuration Parameters

Standard research mode respects key configuration parameters from the `DEFAULT_CONFIG` in `[gpt_researcher/config/variables/default.py:3-54]()`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `RETRIEVER` | `"tavily"` | Web search engine used for retrieving sources |
| `FAST_LLM` | `"openai:gpt-4o-mini"` | Model for fast operations like summaries |
| `SMART_LLM` | `"openai:gpt-4.1"` | Model for report generation and reasoning |
| `STRATEGIC_LLM` | `"openai:o4-mini"` | Model for generating research plans |
| `MAX_ITERATIONS` | `3` | Max iterations for query expansion |
| `MAX_SCRAPER_WORKERS`| `15` | Max concurrent scraper workers |
| `CURATE_SOURCES` | `False` | Whether to add LLM-based source curation |

**Sources:** `[gpt_researcher/config/variables/default.py:3-54]()`, `[docs/docs/gpt-researcher/gptr/config.md:51-86]()`

---

## Error Handling and Edge Cases

### Common Issues

**No Search Results:**
- If no results are found from the retriever, the system logs the issue and returns an empty list `[gpt_researcher/actions/query_processing.py:12-35]()`.
- Research continues with available context or the original query.

**Failed Scraping:**
- Individual URL failures in scraping are caught and logged without halting the entire process `[gpt_researcher/actions/web_scraping.py:33-40]()`.
- `WorkerPool` manages concurrent tasks and rate limits to prevent blockages `[gpt_researcher/skills/browser.py:32-35]()`.

**LLM Response Parsing:**
- `json_repair.loads()` is used to handle malformed JSON responses from strategic models during sub-query generation `[gpt_researcher/actions/query_processing.py:110]()`.

**Sources:** `[gpt_researcher/actions/web_scraping.py:33-40]()`, `[gpt_researcher/actions/query_processing.py:110]()`, `[gpt_researcher/skills/browser.py:32-35]()`

---

# Page: Detailed Report Mode

# Detailed Report Mode

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/report_type/basic_report/basic_report.py](backend/report_type/basic_report/basic_report.py)
- [backend/report_type/detailed_report/detailed_report.py](backend/report_type/detailed_report/detailed_report.py)
- [backend/server/multi_agent_runner.py](backend/server/multi_agent_runner.py)
- [backend/server/server_utils.py](backend/server/server_utils.py)
- [backend/server/websocket_manager.py](backend/server/websocket_manager.py)
- [cli.py](cli.py)
- [docs/blog/2024-09-7-hybrid-research/gptr-hybrid.png](docs/blog/2024-09-7-hybrid-research/gptr-hybrid.png)
- [docs/blog/2024-09-7-hybrid-research/index.md](docs/blog/2024-09-7-hybrid-research/index.md)
- [docs/docs/examples/detailed_report.md](docs/docs/examples/detailed_report.md)
- [docs/docs/gpt-researcher/getting-started/cli.md](docs/docs/gpt-researcher/getting-started/cli.md)
- [frontend/index.html](frontend/index.html)
- [frontend/scripts.js](frontend/scripts.js)
- [frontend/styles.css](frontend/styles.css)
- [tests/test_websocket_manager.py](tests/test_websocket_manager.py)

</details>



## Purpose and Scope

This document describes the **Detailed Report Mode** in GPT Researcher, which produces in-depth, hierarchically-structured research reports by breaking down the main query into subtopics and researching each independently. This mode generates longer, more comprehensive reports (typically 5+ minutes of research time) compared to the standard single-pass research.

For information about:
- Single-pass research without subtopic decomposition, see [Standard Research Mode](#4.1)
- Recursive tree-like exploration with configurable depth, see [Deep Research Mode](#4.3)
- Multi-agent collaborative research with specialized roles, see [Multi-Agent Framework](#4.4)

Sources: [backend/report_type/detailed_report/detailed_report.py:10-91](), [frontend/index.html:171-172]()

## Overview

Detailed Report Mode extends the standard research workflow by introducing a hierarchical two-phase approach:

1. **Phase 1**: Conduct initial broad research on the main query and generate subtopics.
2. **Phase 2**: For each subtopic, conduct independent deep-dive research with context awareness.

The mode maintains global state across all subtopic research tasks to avoid duplication and ensure coherent narrative flow. The final report includes an introduction, table of contents, subtopic sections, and conclusion with references.

**Key characteristics:**
- Report type identifier: `"detailed_report"` (used in API calls and configuration).
- Average completion time: ~5 minutes.
- Typical output length: 2,000+ words across multiple sections.
- Subtopic count: Dynamically determined by LLM analysis (typically 3-6 subtopics).

Sources: [backend/report_type/detailed_report/detailed_report.py:84-91](), [frontend/index.html:172]()

## Architecture Overview

### Detailed Report Workflow

```mermaid
flowchart TD
    Start[/"User Query: Detailed Report Request"/] --> Init["DetailedReport.__init__()<br/>[backend/report_type/detailed_report/detailed_report.py:11]"]
    Init --> Run["DetailedReport.run()<br/>[backend/report_type/detailed_report/detailed_report.py:84]"]
    
    Run --> InitResearch["_initial_research()<br/>Conduct broad research<br/>Populate global_context"]
    InitResearch --> GetSubtopics["_get_all_subtopics()<br/>gpt_researcher.get_subtopics()<br/>Generate 3-6 subtopics"]
    
    GetSubtopics --> WriteIntro["gpt_researcher.write_introduction()<br/>Generate report introduction"]
    WriteIntro --> GenSubReports["_generate_subtopic_reports()<br/>Process all subtopics"]
    
    GenSubReports --> Loop{For each<br/>subtopic}
    Loop --> SubReport["_get_subtopic_report()<br/>Create GPTResearcher instance<br/>with report_type='subtopic_report'"]
    
    SubReport --> SubConduct["subtopic_assistant.conduct_research()<br/>Research specific subtopic"]
    SubConduct --> GetDraft["subtopic_assistant.get_draft_section_titles()<br/>Extract planned sections"]
    
    GetDraft --> FindSimilar["subtopic_assistant.get_similar_written_contents<br/>_by_draft_section_titles()<br/>Find overlapping content"]
    FindSimilar --> WriteSubReport["subtopic_assistant.write_report()<br/>existing_headers=existing_headers<br/>relevant_written_contents=relevant_contents"]
    
    WriteSubReport --> UpdateGlobal["Update Global State:<br/>- global_written_sections<br/>- global_context<br/>- global_urls<br/>- existing_headers"]
    UpdateGlobal --> Loop
    
    Loop -->|All subtopics done| Construct["_construct_detailed_report()<br/>Assemble final report"]
    Construct --> FinalReport[/"Final Report String"/]
```

Sources: [backend/report_type/detailed_report/detailed_report.py:84-91](), [backend/report_type/detailed_report/detailed_report.py:138-175]()

## Class Structure and Responsibilities

### DetailedReport Class

The `DetailedReport` class (defined in `backend/report_type/detailed_report/detailed_report.py`) orchestrates the hierarchical research process.

```mermaid
classDiagram
    class DetailedReport {
        +str query
        +str report_type
        +str report_source
        +List[str] source_urls
        +List[str] document_urls
        +List[str] query_domains
        +str config_path
        +Any tone
        +WebSocket websocket
        +Dict headers
        +str research_id
        
        +GPTResearcher gpt_researcher
        +List[Dict] existing_headers
        +List[str] global_context
        +List[str] global_written_sections
        +Set[str] global_urls
        
        +__init__()
        +run() str
        -_generate_research_id() str
        -_initial_research() None
        -_get_all_subtopics() List[Dict]
        -_generate_subtopic_reports() tuple
        -_get_subtopic_report() Dict[str, str]
        -_construct_detailed_report() str
    }
    
    class GPTResearcher {
        <<gpt_researcher/gpt_researcher.py>>
        +conduct_research()
        +get_subtopics()
        +write_introduction()
        +get_draft_section_titles()
        +get_similar_written_contents_by_draft_section_titles()
        +write_report()
        +extract_headers()
        +extract_sections()
    }
    
    DetailedReport --> GPTResearcher : creates main instance
    DetailedReport --> GPTResearcher : creates per subtopic
```

**State Management Fields:**

| Field | Type | Purpose |
|-------|------|---------|
| `existing_headers` | `List[Dict]` | Tracks section headers from all completed subtopics to avoid duplication. [backend/report_type/detailed_report/detailed_report.py:72]() |
| `global_context` | `List[str]` | Accumulated context snippets from all subtopic research. [backend/report_type/detailed_report/detailed_report.py:73]() |
| `global_written_sections` | `List[str]` | Full text of all written sections for similarity checking. [backend/report_type/detailed_report/detailed_report.py:74]() |
| `global_urls` | `Set[str]` | All URLs visited across main + subtopic research to avoid re-scraping. [backend/report_type/detailed_report/detailed_report.py:75]() |
| `research_id` | `str` | Unique identifier: `"detailed_{timestamp}_{query_hash}"`. [backend/report_type/detailed_report/detailed_report.py:44]() |

Sources: [backend/report_type/detailed_report/detailed_report.py:10-76]()

## Detailed Workflow

### Phase 1: Initial Research and Subtopic Generation

In this phase, the main `GPTResearcher` instance performs a broad sweep to understand the landscape of the query and identify key areas for deeper investigation.

1. **Broad Research**: `conduct_research()` is called on the main query to populate `global_context`. [backend/report_type/detailed_report/detailed_report.py:94-95]()
2. **Subtopic Identification**: `get_subtopics()` analyzes the context to propose specific research tasks. [backend/report_type/detailed_report/detailed_report.py:99]()
3. **Intro Writing**: The main researcher writes the report introduction. [backend/report_type/detailed_report/detailed_report.py:87]()

Sources: [backend/report_type/detailed_report/detailed_report.py:85-87](), [backend/report_type/detailed_report/detailed_report.py:93-108]()

### Phase 2: Subtopic Research with Deduplication

For each identified subtopic, a new `GPTResearcher` instance is spawned with `report_type="subtopic_report"`. [backend/report_type/detailed_report/detailed_report.py:143]()

**Deduplication Mechanisms:**

1. **Header Tracking**: `existing_headers` is passed to each subtopic writer to ensure the LLM does not repeat section titles already used. [backend/report_type/detailed_report/detailed_report.py:172]()
2. **Content Similarity Check**: Before writing, `get_similar_written_contents_by_draft_section_titles()` uses embeddings to find overlapping content in `global_written_sections`. [backend/report_type/detailed_report/detailed_report.py:177-178]()
3. **URL Deduplication**: The `visited_urls` set is shared and updated globally to prevent redundant scraping of the same source. [backend/report_type/detailed_report/detailed_report.py:149]()

Sources: [backend/report_type/detailed_report/detailed_report.py:138-190]()

### Phase 3: Report Assembly

The final report is constructed by concatenating the introduction and all generated subtopic reports. [backend/report_type/detailed_report/detailed_report.py:90]()

```python
async def _construct_detailed_report(self, introduction: str, report_body: str) -> str:
    # Aggregates components into a single markdown string
    report = f"{introduction}\n\n{report_body}"
    return report
```

Sources: [backend/report_type/detailed_report/detailed_report.py:192-194]()

## Integration with Backend

### WebSocket Communication Flow

The `WebSocketManager` in `backend/server/websocket_manager.py` handles the incoming "start" command and routes it to the `DetailedReport` class if the report type matches.

```mermaid
sequenceDiagram
    participant Client as Frontend/Client
    participant WS as WebSocketManager
    participant RUN as run_agent()
    participant DR as DetailedReport
    participant LH as CustomLogsHandler
    
    Client->>WS: WebSocket: "start {json_data}"
    WS->>WS: handle_start_command() [backend/server/server_utils.py:126]
    
    WS->>LH: Create CustomLogsHandler [backend/server/server_utils.py:148]
    WS->>WS: start_streaming() [backend/server/websocket_manager.py:101]
    
    WS->>RUN: run_agent(report_type="detailed_report") [backend/server/websocket_manager.py:108]
    
    RUN->>DR: Create DetailedReport instance [backend/server/websocket_manager.py:145]
    RUN->>DR: report = await researcher.run() [backend/server/websocket_manager.py:160]
    
    DR-->>RUN: Final report string
    RUN-->>WS: report
    
    WS->>WS: generate_report_files(report) [backend/server/server_utils.py:175]
    WS->>Client: Send file paths via WebSocket [backend/server/server_utils.py:178]
```

Sources: [backend/server/websocket_manager.py:101-160](), [backend/server/server_utils.py:126-179]()

## Configuration Parameters

The `DetailedReport` class constructor accepts parameters that define the research scope and constraints.

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | `str` | The main research topic. |
| `report_type` | `str` | Must be `"detailed_report"`. |
| `max_search_results` | `int` | Overrides `max_search_results_per_query` in the researcher config. [backend/report_type/detailed_report/detailed_report.py:71]() |
| `mcp_configs` | `list` | Configurations for Model Context Protocol servers. [backend/report_type/detailed_report/detailed_report.py:62]() |
| `mcp_strategy` | `str` | Strategy for MCP usage (e.g., "fast", "deep"). [backend/report_type/detailed_report/detailed_report.py:64]() |
| `complement_source_urls`| `bool` | If True, allows the researcher to find more URLs beyond provided ones. [backend/report_type/detailed_report/detailed_report.py:24]() |

Sources: [backend/report_type/detailed_report/detailed_report.py:10-71]()

## Performance Considerations

**Research ID Generation**: Each report generates a unique `research_id` to track the task through logs and file generation.

```python
def _generate_research_id(self, query: str) -> str:
    """Generate a unique research ID from query and timestamp."""
    timestamp = str(int(time.time()))
    query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
    return f"detailed_{timestamp}_{query_hash}"
```

Sources: [backend/report_type/detailed_report/detailed_report.py:78-82]()

**Resource Usage**: Because Detailed Report Mode spawns multiple `GPTResearcher` instances (one for initial research and one for each subtopic), it is more resource-intensive than the standard mode. Each subtopic researcher inherits the global configuration, including MCP settings and search result limits. [backend/report_type/detailed_report/detailed_report.py:140-162]()

Sources: [backend/report_type/detailed_report/detailed_report.py:138-162]()

---

# Page: Deep Research Mode

# Deep Research Mode

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/report_type/deep_research/README.md](backend/report_type/deep_research/README.md)
- [backend/report_type/deep_research/__init__.py](backend/report_type/deep_research/__init__.py)
- [backend/report_type/deep_research/example.py](backend/report_type/deep_research/example.py)
- [backend/report_type/deep_research/main.py](backend/report_type/deep_research/main.py)
- [docs/blog/2025-02-26-deep-research/index.md](docs/blog/2025-02-26-deep-research/index.md)
- [docs/docs/gpt-researcher/gptr/deep_research.md](docs/docs/gpt-researcher/gptr/deep_research.md)
- [gpt_researcher/skills/deep_research.py](gpt_researcher/skills/deep_research.py)
- [gpt_researcher/utils/rate_limiter.py](gpt_researcher/utils/rate_limiter.py)
- [gpt_researcher/utils/workers.py](gpt_researcher/utils/workers.py)
- [tests/test_deep_research_parsing.py](tests/test_deep_research_parsing.py)

</details>



## Purpose and Scope

Deep Research Mode in GPT Researcher is an advanced recursive research workflow that explores topics with hierarchical depth. It employs a tree-like exploration pattern to investigate subtopics systematically while maintaining comprehensive context across research branches. This mode is specifically optimized for complex research tasks that require uncovering hidden connections and following citation trails across multiple levels of depth.

For standard single-pass research, see [Standard Research Mode](#4.1). For structured multi-subtopic reports, see [Detailed Report Mode](#4.2). For collaborative agent-based research, see [Multi-Agent Framework](#4.4).

## Overview

Deep Research Mode is designed for tasks requiring more than a surface-level summary. Unlike standard research that performs a single pass of query generation and web search, Deep Research recursively branches into subtopics, creating a tree of research that builds from foundational to advanced insights.

**Key Characteristics:**
- **Report Type Identifier**: `"deep"` [gpt_researcher/skills/deep_research.py:214]()
- **Execution Time**: Approximately 5 minutes per research task [docs/docs/gpt-researcher/gptr/deep_research.md:5]()
- **Estimated Cost**: ~$0.40 per research using strategic reasoning models like `o3-mini` [docs/docs/gpt-researcher/gptr/deep_research.md:5]()
- **Output**: Comprehensive reports with hierarchical synthesis of findings, recommended for ~2000 words [docs/docs/gpt-researcher/gptr/deep_research.md:55]()

Sources: [gpt_researcher/skills/deep_research.py:214](), [docs/docs/gpt-researcher/gptr/deep_research.md:1-17](), [backend/report_type/deep_research/README.md:1-15]()

## Architecture and Components

### Component Overview

```mermaid
graph TB
    subgraph "GPTResearcher_Core"
        Agent["GPTResearcher<br/>(gpt_researcher/agent.py)"]
        Config["Config<br/>(gpt_researcher/config/config.py)"]
    end
    
    subgraph "Deep_Research_Execution"
        DeepSkill["DeepResearchSkill<br/>(gpt_researcher/skills/deep_research.py)"]
        Progress["ResearchProgress<br/>(gpt_researcher/skills/deep_research.py:230-240)"]
    end
    
    subgraph "Recursive_Logic"
        GenQueries["generate_search_queries<br/>(line 277-317)"]
        GenPlan["generate_research_plan<br/>(line 319-366)"]
        ProcessRes["process_research_results<br/>(line 368-412)"]
    end
    
    subgraph "Infrastructure"
        WorkerPool["WorkerPool<br/>(gpt_researcher/utils/workers.py)"]
        RateLimiter["GlobalRateLimiter<br/>(gpt_researcher/utils/rate_limiter.py)"]
    end
    
    Agent -->|"report_type='deep'"| DeepSkill
    DeepSkill --> Progress
    DeepSkill --> GenQueries
    DeepSkill --> GenPlan
    DeepSkill --> ProcessRes
    DeepSkill --> WorkerPool
    WorkerPool --> RateLimiter
```

Sources: [gpt_researcher/skills/deep_research.py:214-260](), [gpt_researcher/utils/workers.py:8-34](), [gpt_researcher/utils/rate_limiter.py:13-28]()

### Initialization and Invocation

Deep Research Mode is activated when the `report_type` parameter is set to `"deep"`. The `DeepResearchSkill` class is initialized with parameters from the researcher's configuration.

```python
# Initialization in gpt_researcher/skills/deep_research.py:214-228
class DeepResearchSkill:
    def __init__(self, researcher):
        self.researcher = researcher
        self.breadth = getattr(researcher.cfg, "deep_research_breadth", 4)
        self.depth = getattr(researcher.cfg, "deep_research_depth", 2)
        self.concurrency_limit = getattr(researcher.cfg, "deep_research_concurrency", 2)
```

The system uses `DeepResearchSkill` to manage the recursive state, including `visited_urls`, `learnings`, and `research_sources`.

Sources: [gpt_researcher/skills/deep_research.py:214-228](), [docs/docs/gpt-researcher/gptr/deep_research.md:34]()

## Configuration Parameters

Deep Research behavior is governed by breadth, depth, and concurrency settings.

| Parameter | Default | Description |
|-----------|---------|-------------|
| `deep_research_breadth` | 4 | Number of parallel search queries generated at each level to explore different aspects. |
| `deep_research_depth` | 2 | How many levels deep the recursion follows leads and uncovering connections. |
| `deep_research_concurrency` | 2 | Maximum number of concurrent research operations to prevent API exhaustion. |

Sources: [gpt_researcher/skills/deep_research.py:218-220](), [docs/docs/gpt-researcher/gptr/deep_research.md:50-54]()

## Tree-Like Exploration Mechanism

### Recursive Research Strategy

Deep Research employs a tree-like exploration pattern where each node generates new questions that become branches for further investigation.

1.  **Initial Plan**: The system calls `generate_research_plan` to create targeted questions based on the original query and initial web results [gpt_researcher/skills/deep_research.py:319-366]().
2.  **Query Generation**: For each question, `generate_search_queries` produces specific SERP queries [gpt_researcher/skills/deep_research.py:277-317]().
3.  **Recursive Deepening**: The `run_deep_research` method follows these branches, extracting "learnings" and citations at each step [gpt_researcher/skills/deep_research.py:414-500]().
4.  **Context Management**: To prevent context window overflow, the system maintains a safety margin of approximately 25,000 words [gpt_researcher/skills/deep_research.py:18]().

### Progress Tracking

The `ResearchProgress` class tracks the state of the tree across both dimensions.

```python
class ResearchProgress:
    def __init__(self, total_depth: int, total_breadth: int):
        self.current_depth = total_depth
        self.total_depth = total_depth
        self.current_breadth = total_breadth
        self.total_breadth = total_breadth
        self.current_query: Optional[str] = None
        self.total_queries = 0
        self.completed_queries = 0
```

Sources: [gpt_researcher/skills/deep_research.py:230-240](), [backend/report_type/deep_research/example.py:22-30]()

## Resource Management and Rate Limiting

Because Deep Research initiates many parallel requests, it uses a sophisticated throttling system.

### Global Rate Limiter

The `GlobalRateLimiter` is a singleton that ensures `rate_limit_delay` is enforced across the entire application, even if multiple `GPTResearcher` instances are running in Deep Research Mode.

```mermaid
sequenceDiagram
    participant WP as WorkerPool (gpt_researcher/utils/workers.py)
    participant RL as GlobalRateLimiter (gpt_researcher/utils/rate_limiter.py)
    participant API as Search_API
    
    WP->>RL: throttle.wait_if_needed()
    Note over RL: Acquire Async Lock
    RL->>RL: Check time_since_last
    alt delay needed
        RL->>RL: asyncio.sleep()
    end
    RL->>WP: yield (Proceed)
    WP->>API: get_search_results()
    Note over RL: Update last_request_time
```

Sources: [gpt_researcher/utils/rate_limiter.py:13-80](), [gpt_researcher/utils/workers.py:8-51]()

## Integration with Reasoning Models

Deep Research is designed to work with high-reasoning models (e.g., `o3-mini`). The system explicitly sets `reasoning_effort` to `High` for critical planning and analysis tasks:

- **Plan Generation**: Uses `ReasoningEfforts.High.value` to analyze initial search results and generate targeted questions [gpt_researcher/skills/deep_research.py:359]().
- **Result Processing**: Uses `ReasoningEfforts.High.value` to extract key learnings and citations from raw context [gpt_researcher/skills/deep_research.py:405]().

Sources: [gpt_researcher/skills/deep_research.py:359, 405](), [backend/report_type/deep_research/example.py:82, 148]()

## Usage Example

To trigger Deep Research Mode, set the `report_type` to `"deep"` during initialization.

```python
from gpt_researcher import GPTResearcher
import asyncio

async def main():
    researcher = GPTResearcher(
        query="Latest developments in quantum computing",
        report_type="deep",
    )

    # Conducts the recursive tree search
    research_data = await researcher.conduct_research()

    # Synthesizes findings from all branches into a report
    report = await researcher.write_report()
    print(report)

if __name__ == "__main__":
    asyncio.run(main())
```

Sources: [docs/docs/gpt-researcher/gptr/deep_research.md:25-45](), [backend/report_type/deep_research/main.py:6-33]()

---

**Related Pages:**
- For standard configuration, see [Configuration Setup](#2.3)
- For details on the orchestrator, see [GPTResearcher Agent Class](#3.1)
- For the underlying scraping logic, see [Web Scraping System](#7.2)

---

# Page: Multi-Agent Framework

# Multi-Agent Framework

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/__init__.py](backend/__init__.py)
- [backend/utils.py](backend/utils.py)
- [langgraph.json](langgraph.json)
- [multi_agents/README.md](multi_agents/README.md)
- [multi_agents/agent.py](multi_agents/agent.py)
- [multi_agents/agents/human.py](multi_agents/agents/human.py)
- [multi_agents/agents/orchestrator.py](multi_agents/agents/orchestrator.py)
- [multi_agents/agents/plan_review.py](multi_agents/agents/plan_review.py)
- [multi_agents/agents/utils/file_formats.py](multi_agents/agents/utils/file_formats.py)
- [multi_agents/langgraph.json](multi_agents/langgraph.json)
- [multi_agents/main.py](multi_agents/main.py)
- [multi_agents/memory/research.py](multi_agents/memory/research.py)
- [multi_agents/requirements.txt](multi_agents/requirements.txt)
- [multi_agents/task.json](multi_agents/task.json)
- [tests/test_multi_agents_plan_revisions.py](tests/test_multi_agents_plan_revisions.py)

</details>



The Multi-Agent Framework provides a sophisticated LangGraph-based orchestration system for conducting in-depth research using specialized AI agents. This framework represents the most advanced research mode in GPT Researcher, leveraging multiple specialized agents that collaborate to produce comprehensive research reports. It is inspired by the STORM paper and implements a collaborative workflow where agents have distinct responsibilities and interact through defined state transitions [multi_agents/README.md:1-9]().

## Architecture Overview

The multi-agent system orchestrates eight specialized agents using LangGraph to conduct research from planning through publication [multi_agents/README.md:15-24]().

### Multi-Agent System Architecture

```mermaid
graph TB
    subgraph "Entry_Point"
        main["multi_agents/main.py"]
        task_config["multi_agents/task.json"]
    end
    
    subgraph "Orchestration_Layer"
        chief["ChiefEditorAgent"]
        research_state["ResearchState"]
        draft_state["DraftState"]
    end
    
    subgraph "Planning_and_Management"
        editor["EditorAgent"]
        human["HumanAgent"]
    end
    
    subgraph "Research_Execution"
        researcher["ResearchAgent"]
        gpt_researcher["GPTResearcher"]
    end
    
    subgraph "Quality_Control"
        reviewer["ReviewerAgent"] 
        reviser["ReviserAgent"]
    end
    
    subgraph "Content_Generation"
        writer["WriterAgent"]
        publisher["PublisherAgent"]
    end
    
    main --> chief
    task_config --> chief
    chief --> research_state
    chief --> editor
    editor --> researcher
    researcher --> gpt_researcher
    researcher --> draft_state
    draft_state --> reviewer
    reviewer --> reviser
    reviser --> draft_state
    editor --> writer
    writer --> publisher
    human -.-> chief
    
    style chief stroke-width:2px
    style researcher stroke-dasharray: 5 5
```
Sources: [multi_agents/main.py:1-62](), [multi_agents/memory/research.py:1-22](), [multi_agents/agents/orchestrator.py:23-54]()

## Agent Roles and Responsibilities

### ChiefEditorAgent
The master orchestrator that coordinates the entire research process using LangGraph [multi_agents/agents/orchestrator.py:23-24](). It initializes the research team, defines the `StateGraph`, and manages agent interactions by calling `run_research_task()` [multi_agents/agents/orchestrator.py:104-127]().

### ResearchAgent 
Integrates with the core `GPTResearcher` class to conduct both initial research and in-depth subtopic research [multi_agents/README.md:42-45]().
- `run_initial_research()`: Conducts broad research on the main query to provide context for the planning phase [multi_agents/agents/orchestrator.py:60]().
- `run_depth_research()`: Performs detailed research on specific subtopics identified in the research plan.

### EditorAgent
Responsible for research planning and parallel execution management [multi_agents/README.md:20]().
- `plan_research()`: Plans the report outline and structure based on the initial research [multi_agents/README.md:43]().
- `run_parallel_research()`: Orchestrates parallel research tasks where multiple subtopics are researched simultaneously [multi_agents/agents/orchestrator.py:62]().

### ReviewerAgent and ReviserAgent
Implement a quality control loop to ensure drafts meet specified guidelines [multi_agents/README.md:46-47]().
- `ReviewerAgent`: Validates the correctness of the research results given a set of criteria [multi_agents/README.md:21]().
- `ReviserAgent`: Revises the research results based on the feedback from the reviewer until satisfactory [multi_agents/README.md:22]().

### HumanAgent
The human-in-the-loop component that oversees the process and provides feedback on the research plan [multi_agents/README.md:17]().
- `review_plan()`: Prompts the user for feedback via WebSockets or console input [multi_agents/agents/human.py:10-45]().
- It tracks `plan_revision_count` to ensure the workflow respects the `max_plan_revisions` limit [multi_agents/agents/human.py:50-59]().

Sources: [multi_agents/agents/human.py:4-60](), [multi_agents/agents/orchestrator.py:47-54](), [multi_agents/README.md:15-24]()

## Workflow Execution

### Research Process Flow

```mermaid
flowchart TD
    start["ChiefEditorAgent.run_research_task()"] --> initial["ResearchAgent.run_initial_research()"]
    initial --> plan["EditorAgent.plan_research()"]
    plan --> human_node["HumanAgent.review_plan()"]
    
    human_node --> route_choice{"route_human_feedback"}
    route_choice -->|"revise"| plan
    route_choice -->|"accept"| parallel["EditorAgent.run_parallel_research()"]
    
    subgraph "Parallel_Research_Loop"
        parallel --> research_tasks["ResearchAgent.run_depth_research()"]
        research_tasks --> review_cycle["Reviewer & Reviser Loop"]
    end
    
    review_cycle --> writer["WriterAgent.run()"]
    writer --> publisher["PublisherAgent.run()"]
    publisher --> output["Multi-format Reports"]
```
Sources: [multi_agents/agents/orchestrator.py:56-90](), [multi_agents/agents/human.py:10-60](), [multi_agents/README.md:40-49]()

### State Transitions
The workflow is defined by a `StateGraph` in `ChiefEditorAgent` [multi_agents/agents/orchestrator.py:57]().
1. **Entry Point**: Starts at the `browser` node (Initial Research) [multi_agents/agents/orchestrator.py:77]().
2. **Planning**: Moves from `browser` to `planner` [multi_agents/agents/orchestrator.py:73]().
3. **Human Feedback**: Moves from `planner` to `human` [multi_agents/agents/orchestrator.py:74]().
4. **Conditional Routing**: Uses `_route_human_feedback` to either go back to `planner` for revisions or proceed to `researcher` [multi_agents/agents/orchestrator.py:81-85]().
5. **Finalization**: Proceeds through `writer` and `publisher` to `END` [multi_agents/agents/orchestrator.py:75-78]().

## State Management

The system uses `ResearchState` to track the overall project progress [multi_agents/memory/research.py:5-20]().

| Field | Type | Description |
|-------|------|-------------|
| `task` | dict | The original task configuration from `task.json` |
| `initial_research` | str | Raw data from the initial broad search |
| `sections` | List[str] | The list of subtopics/sections to be researched |
| `research_data` | List[dict] | Accumulated research findings for each section |
| `human_feedback` | str | Feedback provided by the human user |
| `report` | str | The final compiled research report |

Sources: [multi_agents/memory/research.py:5-20]()

## Configuration System

### Task Configuration
The system is configured via `multi_agents/task.json` [multi_agents/main.py:21-24]().

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Main research question [multi_agents/task.json:2]() |
| `model` | string | LLM model (e.g., "gpt-4o") [multi_agents/task.json:12]() |
| `max_sections` | int | Max subtopics to research [multi_agents/task.json:3]() |
| `max_plan_revisions` | int | Max human-requested plan revisions [multi_agents/task.json:4]() |
| `include_human_feedback` | bool | Toggle human-in-the-loop [multi_agents/task.json:10]() |
| `publish_formats` | object | Enabled output formats (pdf, docx, markdown) [multi_agents/task.json:5-9]() |
| `guidelines` | array | Quality requirements for the report [multi_agents/task.json:13-17]() |

### Model Override
The system supports model override through environment variables. If `STRATEGIC_LLM` is defined, it extracts the model name and overrides the `model` specified in `task.json` [multi_agents/main.py:29-37]().

## Output Generation

The `PublisherAgent` uses utility functions to generate the final documents in the `outputs/` directory [multi_agents/agents/orchestrator.py:39-45]().

- **Markdown**: Generated via `write_text_to_md` [multi_agents/agents/utils/file_formats.py:24-37]().
- **PDF**: Generated using `md2pdf` with custom CSS [multi_agents/agents/utils/file_formats.py:40-69]().
- **DOCX**: Generated by converting Markdown to HTML, then using `HtmlToDocx` [multi_agents/agents/utils/file_formats.py:72-104]().

Sources: [multi_agents/agents/utils/file_formats.py:1-105](), [backend/utils.py:1-130]()

---

# Page: Configuration System

# Configuration System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/gpt-researcher/gptr/config.md](docs/docs/gpt-researcher/gptr/config.md)
- [gpt_researcher/actions/query_processing.py](gpt_researcher/actions/query_processing.py)
- [gpt_researcher/config/config.py](gpt_researcher/config/config.py)
- [gpt_researcher/config/variables/base.py](gpt_researcher/config/variables/base.py)
- [gpt_researcher/config/variables/default.py](gpt_researcher/config/variables/default.py)
- [gpt_researcher/llm_provider/__init__.py](gpt_researcher/llm_provider/__init__.py)
- [gpt_researcher/utils/llm.py](gpt_researcher/utils/llm.py)

</details>



## Purpose and Scope

The Configuration System provides centralized management of all settings for GPT Researcher. This includes LLM providers and models, embedding configurations, retriever settings, document paths, and operational parameters. The system implements a three-tier configuration hierarchy that merges defaults, JSON configuration files, and environment variables to provide flexible deployment options.

For information about specific LLM provider integration and the three-tier LLM strategy (FAST_LLM, SMART_LLM, STRATEGIC_LLM), see [LLM Integration](#6). For details on embedding providers and the Memory system, see [Embeddings and Memory System](#6.5). For a complete reference of all configuration parameters and environment variables, see [Configuration Parameters Reference](#5.2) and [Environment Variables Reference](#5.3).

## Configuration Architecture Overview

The configuration system uses a hierarchical priority system where environment variables override JSON configuration files, which in turn override default values.

### Configuration Entity Mapping
The following diagram bridges the natural language configuration concepts to the specific code entities that implement them.

```mermaid
graph TB
    subgraph "Configuration Sources (Priority Order)"
        EnvVars["Environment Variables<br/>(Highest Priority)"]
        ConfigJSON["config.json Files<br/>(Custom Configurations)"]
        DefaultConfig["DEFAULT_CONFIG<br/>(gpt_researcher/config/variables/default.py)"]
    end
    
    subgraph "Config Class (gpt_researcher/config/config.py)"
        LoadConfig["Config.load_config()<br/>Merge sources"]
        SetAttributes["_set_attributes()<br/>Apply env overrides"]
        SetEmbedding["_set_embedding_attributes()<br/>Parse EMBEDDING"]
        SetLLM["_set_llm_attributes()<br/>Parse LLM Tiers"]
        HandleDeprecated["_handle_deprecated_attributes()<br/>Migration warnings"]
        SetDocPath["_set_doc_path()<br/>Validate filesystem"]
    end
    
    subgraph "Parsing Logic"
        ParseLLM["Config.parse_llm()<br/>provider:model → tuple"]
        ParseEmbedding["Config.parse_embedding()<br/>provider:model → tuple"]
        ParseRetrievers["Config.parse_retrievers()<br/>comma-separated → list"]
        ParseReasoning["Config.parse_reasoning_effort()<br/>low/medium/high → str"]
        ValidateDoc["Config.validate_doc_path()<br/>mkdir if needed"]
        ConvertEnv["Config.convert_env_value()<br/>Type coercion via BaseConfig"]
    end
    
    subgraph "Internal State (Config instance attributes)"
        FastLLMAttrs["fast_llm_provider<br/>fast_llm_model"]
        SmartLLMAttrs["smart_llm_provider<br/>smart_llm_model"]
        StrategicLLMAttrs["strategic_llm_provider<br/>strategic_llm_model"]
        EmbeddingAttrs["embedding_provider<br/>embedding_model"]
        RetrieversAttr["retrievers: List[str]"]
        DocPathAttr["doc_path: str"]
        ReasoningAttr["reasoning_effort: str"]
    end
    
    EnvVars --> LoadConfig
    ConfigJSON --> LoadConfig
    DefaultConfig --> LoadConfig
    
    LoadConfig --> SetAttributes
    SetAttributes --> SetEmbedding
    SetEmbedding --> SetLLM
    SetLLM --> HandleDeprecated
    HandleDeprecated --> SetDocPath
    
    SetLLM --> ParseLLM
    SetEmbedding --> ParseEmbedding
    SetAttributes --> ParseRetrievers
    SetLLM --> ParseReasoning
    SetDocPath --> ValidateDoc
    SetAttributes --> ConvertEnv
    
    ParseLLM --> FastLLMAttrs
    ParseLLM --> SmartLLMAttrs
    ParseLLM --> StrategicLLMAttrs
    ParseEmbedding --> EmbeddingAttrs
    ParseRetrievers --> RetrieversAttr
    ValidateDoc --> DocPathAttr
    ParseReasoning --> ReasoningAttr
```

Sources: [gpt_researcher/config/config.py:19-155](), [gpt_researcher/config/variables/default.py:3-55](), [gpt_researcher/config/variables/base.py:5-52]()

## The Config Class

The `Config` class ([gpt_researcher/config/config.py:19-155]()) serves as the central configuration manager. It is initialized with an optional `config_path` parameter and performs the following initialization sequence:

1. **Load configuration** - Merges defaults, JSON files, and environment variables [gpt_researcher/config/config.py:44]().
2. **Set base attributes** - Applies environment variable overrides [gpt_researcher/config/config.py:45]().
3. **Parse embedding configuration** - Extracts provider and model from `EMBEDDING` string [gpt_researcher/config/config.py:46]().
4. **Parse LLM configurations** - Extracts provider and model for all three LLM tiers [gpt_researcher/config/config.py:47]().
5. **Handle deprecated attributes** - Issues warnings and performs migrations [gpt_researcher/config/config.py:48]().
6. **Validate document paths** - Ensures filesystem directories exist [gpt_researcher/config/config.py:49-50]().

### Key Initialization Flow

```mermaid
sequenceDiagram
    participant User
    participant ConfigInit as "Config.__init__()"
    participant LoadConfig as "Config.load_config()"
    participant SetAttrs as "Config._set_attributes()"
    participant ParseMethods as "parse_llm/parse_embedding/etc"
    
    User->>ConfigInit: Config(config_path)
    ConfigInit->>LoadConfig: load_config(config_path)
    LoadConfig->>LoadConfig: Read JSON file if exists
    LoadConfig->>LoadConfig: Merge with DEFAULT_CONFIG
    LoadConfig-->>ConfigInit: merged config dict
    
    ConfigInit->>SetAttrs: _set_attributes(config)
    SetAttrs->>SetAttrs: For each config key in BaseConfig
    SetAttrs->>SetAttrs: Check os.getenv(key)
    SetAttrs->>SetAttrs: convert_env_value() using Type Hints
    SetAttrs->>SetAttrs: setattr(self, key.lower(), value)
    
    ConfigInit->>ParseMethods: _set_embedding_attributes()
    ParseMethods->>ParseMethods: parse_embedding(self.embedding)
    ParseMethods-->>ConfigInit: embedding_provider, embedding_model
    
    ConfigInit->>ParseMethods: _set_llm_attributes()
    ParseMethods->>ParseMethods: parse_llm(self.fast_llm)
    ParseMethods->>ParseMethods: parse_llm(self.smart_llm)
    ParseMethods->>ParseMethods: parse_llm(self.strategic_llm)
    ParseMethods-->>ConfigInit: llm providers and models
    
    ConfigInit->>ConfigInit: _handle_deprecated_attributes()
    ConfigInit->>ConfigInit: _set_doc_path()
```

Sources: [gpt_researcher/config/config.py:34-61](), [gpt_researcher/config/config.py:62-84]()

### Key Attributes

The `Config` class exposes the following key attributes after initialization:

| Attribute | Type | Description |
|-----------|------|-------------|
| `config_path` | `str \| None` | Path to the JSON configuration file [gpt_researcher/config/config.py:40]() |
| `llm_kwargs` | `Dict[str, Any]` | Additional keyword arguments for LLM calls [gpt_researcher/config/config.py:41]() |
| `embedding_kwargs` | `Dict[str, Any]` | Additional keyword arguments for embeddings [gpt_researcher/config/config.py:42]() |
| `fast_llm_provider` | `str` | Provider for fast/cheap LLM operations [gpt_researcher/config/config.py:93]() |
| `fast_llm_model` | `str` | Model name for fast operations [gpt_researcher/config/config.py:93]() |
| `smart_llm_provider` | `str` | Provider for complex reasoning tasks [gpt_researcher/config/config.py:94]() |
| `smart_llm_model` | `str` | Model name for main research [gpt_researcher/config/config.py:94]() |
| `strategic_llm_provider` | `str` | Provider for high-level coordination [gpt_researcher/config/config.py:95]() |
| `strategic_llm_model` | `str` | Model name for multi-agent orchestration [gpt_researcher/config/config.py:95]() |
| `embedding_provider` | `str` | Provider for embeddings [gpt_researcher/config/config.py:87]() |
| `embedding_model` | `str` | Model name for embeddings [gpt_researcher/config/config.py:87]() |
| `retrievers` | `List[str]` | List of enabled retriever names [gpt_researcher/config/config.py:80]() |
| `doc_path` | `str` | Path to local documents directory [gpt_researcher/config/config.py:148]() |
| `mcp_servers` | `List[dict]` | MCP server configurations [gpt_researcher/config/config.py:53]() |
| `reasoning_effort` | `str` | Reasoning effort level (low/medium/high) [gpt_researcher/config/config.py:96]() |

Sources: [gpt_researcher/config/config.py:25-61](), [gpt_researcher/config/config.py:85-96]()

## Configuration Sources and Priority

### Three-Tier Priority System

The system follows a strict hierarchy for resolving configuration values:
1. **Environment Variables**: Highest priority. Checked in `_set_attributes` [gpt_researcher/config/config.py:72-75]().
2. **JSON Config Files**: Loaded via `load_config` [gpt_researcher/config/config.py:157-177]().
3. **DEFAULT_CONFIG**: Fallback values defined in `gpt_researcher/config/variables/default.py` [gpt_researcher/config/variables/default.py:3-55]().

### Loading Configuration Files

The `load_config()` class method ([gpt_researcher/config/config.py:157-177]()) implements the configuration loading logic:

1. Checks for `config_path` parameter or `CONFIG_PATH` environment variable [gpt_researcher/config/config.py:159]().
2. If no path specified, returns `DEFAULT_CONFIG` [gpt_researcher/config/config.py:161]().
3. If path specified but file doesn't exist, warns and returns `DEFAULT_CONFIG` [gpt_researcher/config/config.py:164-171]().
4. If file exists, loads JSON and merges with `DEFAULT_CONFIG` [gpt_researcher/config/config.py:173-177]().

Sources: [gpt_researcher/config/config.py:157-177]()

## Parsing and Validation Methods

### LLM Configuration Parsing

The `parse_llm()` static method ([gpt_researcher/config/config.py:203-221]()) parses LLM configuration strings in the format `provider:model`. It validates the provider against `_SUPPORTED_PROVIDERS` [gpt_researcher/config/config.py:214]().

**Example configurations:**
- `FAST_LLM=openai:gpt-4o-mini`
- `SMART_LLM=anthropic:claude-3-5-sonnet-20241022`

### Retriever Parsing and Validation

The `parse_retrievers()` method ([gpt_researcher/config/config.py:188-201]()) validates retriever names against available implementations retrieved via `get_all_retriever_names()` [gpt_researcher/config/config.py:193]().

### Environment Variable Type Conversion

The `convert_env_value()` static method ([gpt_researcher/config/config.py:256-288]()) handles type coercion from environment variable strings to the appropriate Python types based on `BaseConfig` type hints [gpt_researcher/config/config.py:74]().

| Type Hint | Conversion Logic |
|-----------|-----------------|
| `bool` | `"true"/"1"/"yes"/"on"` → `True` [gpt_researcher/config/config.py:263-264]() |
| `int` | `int(env_value)` [gpt_researcher/config/config.py:274-275]() |
| `float` | `float(env_value)` [gpt_researcher/config/config.py:277-278]() |
| `List` / `dict` | `json.loads(env_value)` [gpt_researcher/config/config.py:280-281]() |

Sources: [gpt_researcher/config/config.py:256-288]()

## LLM and Embedding Configuration

### Three-Tier LLM Configuration

The configuration system separates LLM usage into three tiers: `fast_llm`, `smart_llm`, and `strategic_llm`. These are used by `create_chat_completion` in `gpt_researcher/utils/llm.py` to determine which model to invoke for specific tasks like sub-query generation [gpt_researcher/actions/query_processing.py:72-81]().

### Usage in LLM Creation

The parsed configuration attributes are used to initialize LLM providers. For example, when constructing subtopics:

```python
# gpt_researcher/utils/llm.py:184-194
provider_kwargs = {'model': config.smart_llm_model}

if config.llm_kwargs:
    provider_kwargs.update(config.llm_kwargs)

if config.smart_llm_model in SUPPORT_REASONING_EFFORT_MODELS:
    provider_kwargs['reasoning_effort'] = ReasoningEfforts.High.value
else:
    provider_kwargs['temperature'] = config.temperature
    provider_kwargs['max_tokens'] = config.smart_token_limit

provider = get_llm(config.smart_llm_provider, **provider_kwargs)
```

Sources: [gpt_researcher/utils/llm.py:184-194](), [gpt_researcher/actions/query_processing.py:72-81]()

## MCP (Model Context Protocol) Configuration

MCP configuration is handled through `mcp_servers` and `mcp_allowed_root_paths` [gpt_researcher/config/config.py:53-54](). The system uses `get_mcp_server_config()` to retrieve specific server settings by name [gpt_researcher/config/config.py:295-312]().

## Deprecated Attributes and Migration

The system maintains backward compatibility for legacy variables like `LLM_PROVIDER`, `FAST_LLM_MODEL`, and `EMBEDDING_PROVIDER` in `_handle_deprecated_attributes()` [gpt_researcher/config/config.py:98-145](). It issues a `FutureWarning` when these are detected [gpt_researcher/config/config.py:101-105]().

Sources: [gpt_researcher/config/config.py:98-145]()

---

# Page: Config Class Architecture

# Config Class Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/gpt-researcher/llms/running-with-ollama.md](docs/docs/gpt-researcher/llms/running-with-ollama.md)
- [gpt_researcher/config/__init__.py](gpt_researcher/config/__init__.py)
- [gpt_researcher/config/config.py](gpt_researcher/config/config.py)
- [gpt_researcher/config/variables/__init__.py](gpt_researcher/config/variables/__init__.py)
- [gpt_researcher/llm_provider/__init__.py](gpt_researcher/llm_provider/__init__.py)
- [gpt_researcher/utils/llm.py](gpt_researcher/utils/llm.py)
- [multi_agents/agents/utils/llms.py](multi_agents/agents/utils/llms.py)

</details>



## Purpose and Scope

This document explains the architecture of the `Config` class, which serves as the central configuration management system for GPT Researcher. The `Config` class is responsible for loading, parsing, validating, and providing access to all configuration parameters from multiple sources including default values, JSON configuration files, and environment variables [gpt_researcher/config/config.py:1-6]().

For information about individual configuration parameters and their meanings, see [Configuration Parameters Reference](5.2). For details about environment variable usage, see [Environment Variables Reference](5.3). For information about how LLM providers use configuration, see [LLM Provider Architecture](6.1).

---

## BaseConfig Schema Definition

### BaseConfig TypedDict Structure

The `BaseConfig` TypedDict defines the complete schema for all configuration parameters. It serves as the type contract that ensures type safety throughout the configuration system [gpt_researcher/config/variables/base.py:5-51]().

**Key Schema Categories:**

| Category | Parameters | Type Examples |
|----------|-----------|---------------|
| **LLM Configuration** | `FAST_LLM`, `SMART_LLM`, `STRATEGIC_LLM` | `str` (format: `provider:model`) |
| **Token Limits** | `FAST_TOKEN_LIMIT`, `SMART_TOKEN_LIMIT`, `STRATEGIC_TOKEN_LIMIT` | `int` |
| **Retriever Settings** | `RETRIEVER`, `MAX_SEARCH_RESULTS_PER_QUERY` | `str`, `int` |
| **Embedding Configuration** | `EMBEDDING`, `SIMILARITY_THRESHOLD` | `str`, `float` |
| **Research Parameters** | `MAX_ITERATIONS`, `MAX_SUBTOPICS`, `TOTAL_WORDS` | `int` |
| **Scraping Configuration** | `SCRAPER`, `MAX_SCRAPER_WORKERS`, `SCRAPER_RATE_LIMIT_DELAY` | `str`, `int`, `float` |
| **Deep Research** | `DEEP_RESEARCH_BREADTH`, `DEEP_RESEARCH_DEPTH`, `DEEP_RESEARCH_CONCURRENCY` | `int` |
| **MCP Integration** | `MCP_SERVERS`, `MCP_AUTO_TOOL_SELECTION`, `MCP_STRATEGY`, `MCP_ALLOWED_ROOT_PATHS` | `List[Dict]`, `bool`, `str`, `List[str]` |
| **Image Generation** | `IMAGE_GENERATION_MODEL`, `IMAGE_GENERATION_MAX_IMAGES`, `IMAGE_GENERATION_ENABLED`, `IMAGE_GENERATION_STYLE` | `Union[str, None]`, `int`, `bool`, `str` |
| **Additional Settings** | `LANGUAGE`, `REPORT_FORMAT`, `AGENT_ROLE`, `TEMPERATURE`, `REASONING_EFFORT` | `str`, `float` |

**Complete Schema Location:** [gpt_researcher/config/variables/base.py:5-51]()

**Notable Type Patterns:**
- `Union[str, None]`: Optional string fields like `AGENT_ROLE`, `REPORT_SOURCE`, `IMAGE_GENERATION_MODEL` [gpt_researcher/config/variables/base.py:26-47]()
- `List[Dict[str, Any]]`: Complex structured data like `MCP_SERVERS` [gpt_researcher/config/variables/base.py:40]()
- `dict`: Flexible dictionaries like `LLM_KWARGS`, `EMBEDDING_KWARGS` [gpt_researcher/config/variables/base.py:34-35]()

**Sources:** [gpt_researcher/config/variables/base.py:1-51]()

---

## DEFAULT_CONFIG Values

The `DEFAULT_CONFIG` dictionary provides baseline values for all configuration parameters:

```mermaid
graph LR
    subgraph "LLM_Defaults"
        ["FAST_LLM: openai:gpt-4o-mini (3000 tokens)"]
        ["SMART_LLM: openai:gpt-4.1 (6000 tokens)"]
        ["STRATEGIC_LLM: openai:o4-mini (4000 tokens)"]
    end
    
    subgraph "Retriever_Defaults"
        ["RETRIEVER: tavily"]
        ["MAX_SEARCH_RESULTS_PER_QUERY: 5"]
    end
    
    subgraph "Embedding_Defaults"
        ["EMBEDDING: openai:text-embedding-3-small"]
        ["SIMILARITY_THRESHOLD: 0.42"]
    end
    
    subgraph "Deep_Research_Defaults"
        ["DEEP_RESEARCH_BREADTH: 3"]
        ["DEEP_RESEARCH_DEPTH: 2"]
        ["DEEP_RESEARCH_CONCURRENCY: 4"]
    end
    
    subgraph "MCP_Defaults"
        ["MCP_SERVERS: []"]
        ["MCP_STRATEGY: fast"]
        ["MCP_AUTO_TOOL_SELECTION: True"]
    end
```

**Key Default Values:**
- **LLMs:** `gpt-4o-mini` for fast operations, `gpt-4.1` for smart operations, `o4-mini` for strategic planning [gpt_researcher/config/variables/default.py:7-9]()
- **Token Limits:** 3000 (fast), 6000 (smart), 4000 (strategic) [gpt_researcher/config/variables/default.py:10-12]()
- **Retriever:** `tavily` (default search engine) [gpt_researcher/config/variables/default.py:4]()
- **Embedding:** `openai:text-embedding-3-small` with 0.42 similarity threshold [gpt_researcher/config/variables/default.py:5-6]()
- **Scraping:** `bs` (BeautifulSoup), 15 max workers, 0.0 rate limit delay [gpt_researcher/config/variables/default.py:24-26]()
- **Report Source:** `web` (can be changed to `local`, `hybrid`, or `azure`) [gpt_researcher/config/variables/default.py:29]()
- **Document Path:** `./my-docs` for local document research [gpt_researcher/config/variables/default.py:30]()
- **Reasoning Effort:** `medium` (for reasoning models) [gpt_researcher/config/variables/default.py:45]()
- **MCP Strategy:** `fast` execution strategy [gpt_researcher/config/variables/default.py:44]()
- **Image Generation:** Disabled by default, uses `models/gemini-2.5-flash-image` when enabled [gpt_researcher/config/variables/default.py:50-53]()

**Sources:** [gpt_researcher/config/variables/default.py:1-54]()

---

## Configuration Hierarchy and Precedence

The `Config` class implements a three-tier loading hierarchy where each subsequent source can override values from the previous one:

```mermaid
graph TD
    ["Start: Config.__init__(config_path)"] --> ["load_config(config_path)"]
    ["load_config(config_path)"] --> ["DEFAULT_CONFIG (variables/default.py)"]
    ["load_config(config_path)"] --> ["Custom JSON Config (if config_path provided)"]
    ["DEFAULT_CONFIG (variables/default.py)"] --> ["Merged Config Dictionary"]
    ["Custom JSON Config (if config_path provided)"] --> ["Merged Config Dictionary"]
    ["Merged Config Dictionary"] --> ["_set_attributes()"]
    ["Environment Variables (os.getenv)"] --> ["_set_attributes()"]
    ["_set_attributes()"] --> ["Final Config Object"]
```

**Sources:** [gpt_researcher/config/config.py:34-51](), [gpt_researcher/config/config.py:157-176]()

### Configuration Loading Flow

The configuration loading process follows this sequence:

| Order | Source | Method | Precedence | Notes |
|-------|--------|--------|------------|-------|
| 1 | Default Config | `DEFAULT_CONFIG` dictionary | Lowest | Always loaded as base [gpt_researcher/config/config.py:161]() |
| 2 | JSON Config File | `load_config(config_path)` | Medium | Optional, merged with defaults [gpt_researcher/config/config.py:173]() |
| 3 | Environment Variables | `os.getenv(key)` in `_set_attributes()` | Highest | Always checked, overrides all [gpt_researcher/config/config.py:72-75]() |

The `load_config()` class method [gpt_researcher/config/config.py:157-176]() handles the file loading logic:

1. If `config_path` is `None`, returns `DEFAULT_CONFIG` [gpt_researcher/config/config.py:161]()
2. Checks if the file exists; if not, warns and returns `DEFAULT_CONFIG` [gpt_researcher/config/config.py:164-171]()
3. Loads the JSON file and merges it with `DEFAULT_CONFIG` to ensure all keys are present [gpt_researcher/config/config.py:173]()
4. Returns the merged configuration dictionary [gpt_researcher/config/config.py:176]()

**Sources:** [gpt_researcher/config/config.py:157-176]()

---

## Config Class Structure

### Class Overview and Key Components

```mermaid
graph TB
    subgraph "Config_Class_Entities"
        ["Config.__init__(config_path)"]
        ["Config.CONFIG_DIR"]
        ["Config.llm_kwargs"]
        ["Config.embedding_kwargs"]
        ["Config.mcp_servers"]
        ["Config.mcp_allowed_root_paths"]
    end
    
    subgraph "Initialization_Methods"
        ["Config._set_attributes(config)"]
        ["Config._set_embedding_attributes()"]
        ["Config._set_llm_attributes()"]
        ["Config._handle_deprecated_attributes()"]
        ["Config._set_doc_path(config)"]
    end
    
    subgraph "Parsing_Methods"
        ["Config.parse_llm(llm_str)"]
        ["Config.parse_embedding(embedding_str)"]
        ["Config.parse_retrievers(retriever_str)"]
        ["Config.parse_reasoning_effort(str)"]
        ["Config.convert_env_value(key, value, type)"]
    end
    
    ["Config.__init__(config_path)"] --> ["Config._set_attributes(config)"]
    ["Config.__init__(config_path)"] --> ["Config._set_embedding_attributes()"]
    ["Config.__init__(config_path)"] --> ["Config._set_llm_attributes()"]
    ["Config.__init__(config_path)"] --> ["Config._handle_deprecated_attributes()"]
    ["Config.__init__(config_path)"] --> ["Config._set_doc_path(config)"]
    
    ["Config._set_attributes(config)"] --> ["Config.convert_env_value(key, value, type)"]
    ["Config._set_attributes(config)"] --> ["Config.parse_retrievers(retriever_str)"]
    ["Config._set_embedding_attributes()"] --> ["Config.parse_embedding(embedding_str)"]
    ["Config._set_llm_attributes()"] --> ["Config.parse_llm(llm_str)"]
    ["Config._set_llm_attributes()"] --> ["Config.parse_reasoning_effort(str)"]
```

**Sources:** [gpt_researcher/config/config.py:19-61](), [gpt_researcher/config/config.py:62-155]()

### Key Attributes

The `Config` class maintains several categories of attributes:

**Instance Attributes:**
- `config_path`: Path to the custom configuration file [gpt_researcher/config/config.py:40]()
- `llm_kwargs`: Dictionary for additional LLM provider arguments [gpt_researcher/config/config.py:41]()
- `embedding_kwargs`: Dictionary for additional embedding provider arguments [gpt_researcher/config/config.py:42]()
- `mcp_servers`: List of MCP server configurations [gpt_researcher/config/config.py:53]()
- `mcp_allowed_root_paths`: Allowed root paths for MCP servers [gpt_researcher/config/config.py:54]()

**Dynamic Attributes (set via `_set_attributes()`):**
All configuration parameters from the loaded config dictionary are converted to lowercase attribute names [gpt_researcher/config/config.py:75](). For example:
- `FAST_LLM` → `self.fast_llm`
- `MAX_ITERATIONS` → `self.max_iterations`
- `REASONING_EFFORT` → `self.reasoning_effort`

**Parsed Attributes (set via parsing methods):**
- `fast_llm_provider`, `fast_llm_model`: Parsed from `fast_llm` string [gpt_researcher/config/config.py:93]()
- `smart_llm_provider`, `smart_llm_model`: Parsed from `smart_llm` string [gpt_researcher/config/config.py:94]()
- `strategic_llm_provider`, `strategic_llm_model`: Parsed from `strategic_llm` string [gpt_researcher/config/config.py:95]()
- `embedding_provider`, `embedding_model`: Parsed from `embedding` string [gpt_researcher/config/config.py:87-89]()
- `retrievers`: List of retriever names parsed from comma-separated string [gpt_researcher/config/config.py:78-83]()
- `reasoning_effort`: Parsed and validated reasoning effort level [gpt_researcher/config/config.py:96]()

**MCP Configuration Attributes:**
The MCP-related attributes are initialized after the main configuration loading [gpt_researcher/config/config.py:53-60]().

**Sources:** [gpt_researcher/config/config.py:34-61](), [gpt_researcher/config/config.py:91-96]()

---

## Parsing and Type Conversion System

### Provider String Parsing

The `Config` class uses a standardized format for specifying providers and models: `provider:model`. This format is parsed by static methods that validate the provider against supported lists.

```mermaid
graph LR
    subgraph "LLM_Parsing"
        ["'openai:gpt-4o-mini'"] --> ["Config.parse_llm()"]
        ["Config.parse_llm()"] --> ["fast_llm_provider: 'openai'"]
        ["Config.parse_llm()"] --> ["fast_llm_model: 'gpt-4o-mini'"]
    end
    
    subgraph "Embedding_Parsing"
        ["'openai:text-embedding-3-large'"] --> ["Config.parse_embedding()"]
        ["Config.parse_embedding()"] --> ["embedding_provider: 'openai'"]
        ["Config.parse_embedding()"] --> ["embedding_model: 'text-embedding-3-large'"]
    end
    
    subgraph "Retriever_Parsing"
        ["'tavily,google'"] --> ["Config.parse_retrievers()"]
        ["Config.parse_retrievers()"] --> ["retrievers: ['tavily', 'google']"]
    end
```

**Sources:** [gpt_researcher/config/config.py:202-249](), [gpt_researcher/config/config.py:187-200]()

### LLM Parsing Implementation

The `parse_llm()` static method [gpt_researcher/config/config.py:202-220]() implements the following logic:

1. Returns `(None, None)` if input is `None` [gpt_researcher/config/config.py:204]()
2. Splits the string on `:` to separate provider and model [gpt_researcher/config/config.py:206]()
3. Validates the provider against `_SUPPORTED_PROVIDERS` from `gpt_researcher.llm_provider.generic.base` [gpt_researcher/config/config.py:214]()
4. Raises `ValueError` with helpful message if format is incorrect or provider is unsupported [gpt_researcher/config/config.py:217]()

Example usage in the codebase:
```python
self.fast_llm_provider, self.fast_llm_model = self.parse_llm(self.fast_llm)
```

**Sources:** [gpt_researcher/config/config.py:202-220]()

### Environment Variable Type Conversion

The `convert_env_value()` static method [gpt_researcher/config/config.py:255-287]() provides robust type conversion for environment variables using Python's type hints:

| Type Hint | Conversion Logic | Example |
|-----------|-----------------|---------|
| `bool` | Checks if value is in `("true", "1", "yes", "on")` (case-insensitive) [gpt_researcher/config/config.py:265]() | `"true"` → `True` |
| `int` | Uses `int()` constructor [gpt_researcher/config/config.py:268]() | `"42"` → `42` |
| `float` | Uses `float()` constructor [gpt_researcher/config/config.py:270]() | `"3.14"` → `3.14` |
| `str` or `Any` | Returns value as-is [gpt_researcher/config/config.py:272]() | `"text"` → `"text"` |
| `list` or `List` | Parses JSON [gpt_researcher/config/config.py:275]() | `'["a","b"]'` → `["a", "b"]` |
| `dict` | Parses JSON [gpt_researcher/config/config.py:278]() | `'{"key":"value"}'` → `{"key": "value"}` |
| `Union` types | Tries each type in order, returns first successful conversion [gpt_researcher/config/config.py:281-287]() | `Union[str, None]` |

**Sources:** [gpt_researcher/config/config.py:255-287]()

---

## Attribute Setting and Initialization Sequence

### Initialization Method Flow

```mermaid
graph TD
    ["Config.__init__(config_path)"] --> ["config_to_use = load_config(config_path)"]
    ["config_to_use = load_config(config_path)"] --> ["_set_attributes(config_to_use)"]
    ["_set_attributes(config_to_use)"] --> ["_set_embedding_attributes()"]
    ["_set_embedding_attributes()"] --> ["_set_llm_attributes()"]
    ["_set_llm_attributes()"] --> ["_handle_deprecated_attributes()"]
    ["_handle_deprecated_attributes()"] --> ["Check report_source != 'web'"]
    ["Check report_source != 'web'"] -->|Yes| ["_set_doc_path(config_to_use)"]
    ["Check report_source != 'web'"] -->|No| ["Initialize MCP attributes"]
    ["_set_doc_path(config_to_use)"] --> ["Initialize MCP attributes"]
```

**Sources:** [gpt_researcher/config/config.py:34-61]()

### _set_attributes() Method

The `_set_attributes()` method [gpt_researcher/config/config.py:62-83]() is the core of the configuration loading system:

**Algorithm:**
1. Iterate through all key-value pairs in the config dictionary [gpt_researcher/config/config.py:71]()
2. For each key, check if an environment variable exists with that name [gpt_researcher/config/config.py:72]()
3. If environment variable exists, convert it to the appropriate type using `convert_env_value()` and `BaseConfig` annotations [gpt_researcher/config/config.py:74]()
4. Set the attribute on the `Config` instance using `setattr(self, key.lower(), value)` [gpt_researcher/config/config.py:75]()
5. Special handling for `RETRIEVER`: 
   - Gets value from environment or config with default `"tavily"` [gpt_researcher/config/config.py:78]()
   - Parses into list using `parse_retrievers()` [gpt_researcher/config/config.py:80]()

**Sources:** [gpt_researcher/config/config.py:62-83]()

### LLM Attributes Configuration

The `_set_llm_attributes()` method [gpt_researcher/config/config.py:91-96]() parses all three LLM types:

```python
self.fast_llm_provider, self.fast_llm_model = self.parse_llm(self.fast_llm)
self.smart_llm_provider, self.smart_llm_model = self.parse_llm(self.smart_llm)
self.strategic_llm_provider, self.strategic_llm_model = self.parse_llm(self.strategic_llm)
self.reasoning_effort = self.parse_reasoning_effort(os.getenv("REASONING_EFFORT"))
```

**Sources:** [gpt_researcher/config/config.py:91-96]()

---

## Deprecation Handling System

### Deprecated Attributes Management

The `_handle_deprecated_attributes()` method [gpt_researcher/config/config.py:98-145]() manages backward compatibility:

**EMBEDDING_PROVIDER Deprecation:**
- Issues `FutureWarning` if `EMBEDDING_PROVIDER` environment variable is set [gpt_researcher/config/config.py:101]()
- Maps old provider values to appropriate embedding models [gpt_researcher/config/config.py:110-126]()

| Old Provider | New Embedding Model |
|--------------|-------------------|
| `ollama` | Value from `OLLAMA_EMBEDDING_MODEL` [gpt_researcher/config/config.py:112]() |
| `custom` | `"custom"` (or value from `OPENAI_EMBEDDING_MODEL`) [gpt_researcher/config/config.py:114]() |
| `openai` | `"text-embedding-3-large"` [gpt_researcher/config/config.py:116]() |
| `azure_openai` | `"text-embedding-3-large"` [gpt_researcher/config/config.py:118]() |
| `huggingface` | `"sentence-transformers/all-MiniLM-L6-v2"` [gpt_researcher/config/config.py:120]() |
| `google_genai` | `"text-embedding-004"` [gpt_researcher/config/config.py:124]() |

**LLM Configuration Deprecation:**
- `LLM_PROVIDER`, `FAST_LLM_MODEL`, and `SMART_LLM_MODEL` are deprecated in favor of `FAST_LLM` and `SMART_LLM` [gpt_researcher/config/config.py:128-131]()
- Issues warnings and maps values to new attributes [gpt_researcher/config/config.py:132-145]()

**Sources:** [gpt_researcher/config/config.py:98-145]()

---

## Integration with System Components

### Config Usage in LLM Operations

```mermaid
graph TB
    subgraph "Config_Data"
        ["Config.fast_llm_provider"]
        ["Config.smart_llm_model"]
        ["Config.llm_kwargs"]
        ["Config.reasoning_effort"]
    end
    
    subgraph "LLM_Utilities"
        ["create_chat_completion()"]
        ["get_llm(llm_provider, **kwargs)"]
        ["construct_subtopics()"]
    end
    
    subgraph "Configuration_Application"
        ["Check SUPPORT_REASONING_EFFORT_MODELS"]
        ["Check NO_SUPPORT_TEMPERATURE_MODELS"]
        ["Apply llm_kwargs"]
    end
    
    ["Config_Data"] --> ["create_chat_completion()"]
    ["Config_Data"] --> ["construct_subtopics()"]
    
    ["create_chat_completion()"] --> ["Configuration_Application"]
    ["construct_subtopics()"] --> ["Configuration_Application"]
    
    ["Configuration_Application"] --> ["get_llm(llm_provider, **kwargs)"]
```

**Sources:** [gpt_researcher/utils/llm.py:41-112](), [gpt_researcher/utils/llm.py:152-193]()

### Configuration Application in create_chat_completion

The `create_chat_completion()` function [gpt_researcher/utils/llm.py:41-135]() demonstrates how the `Config` class integrates with LLM operations:

1. Creates `provider_kwargs` dictionary with model from parameters [gpt_researcher/utils/llm.py:84]()
2. Updates with `llm_kwargs` if provided [gpt_researcher/utils/llm.py:87]()
3. Checks if model is in `SUPPORT_REASONING_EFFORT_MODELS` [gpt_researcher/utils/llm.py:89]()
4. Conditionally sets `reasoning_effort` [gpt_researcher/utils/llm.py:90]()
5. Checks if model is in `NO_SUPPORT_TEMPERATURE_MODELS` [gpt_researcher/utils/llm.py:92-97]()

**Sources:** [gpt_researcher/utils/llm.py:78-91]()

---

## Validation and Utility Methods

### Document Path Validation

The `validate_doc_path()` method [gpt_researcher/config/config.py:251-253]() ensures the document directory exists:

```python
def validate_doc_path(self):
    """Ensure that the folder exists at the doc path"""
    os.makedirs(self.doc_path, exist_ok=True)
```

This is called during initialization when `report_source` is not `'web'` [gpt_researcher/config/config.py:49-50]().

**Sources:** [gpt_researcher/config/config.py:147-154](), [gpt_researcher/config/config.py:251-253]()

### MCP Server Configuration Retrieval

The `get_mcp_server_config()` method [gpt_researcher/config/config.py:294-310]() provides access to MCP server configurations by name, iterating through the `mcp_servers` list to find a match [gpt_researcher/config/config.py:302-308]().

**Sources:** [gpt_researcher/config/config.py:294-310]()

### Verbose Mode Configuration

The `set_verbose()` method [gpt_researcher/config/config.py:290-292]() provides runtime control over logging verbosity by updating the `llm_kwargs` dictionary [gpt_researcher/config/config.py:292]().

**Sources:** [gpt_researcher/config/config.py:290-292]()

### Configuration Discovery

The `list_available_configs()` classmethod [gpt_researcher/config/config.py:178-185]() allows discovery of available configurations by scanning the `CONFIG_DIR` for `.json` files [gpt_researcher/config/config.py:183]().

**Sources:** [gpt_researcher/config/config.py:178-185]()

---

## Summary

The `Config` class implements a sophisticated configuration management system with the following key characteristics:

1. **Three-Tier Hierarchy:** Defaults → JSON File → Environment Variables [gpt_researcher/config/config.py:44-51]().
2. **Type-Safe Conversion:** Automatic type conversion using Python type hints [gpt_researcher/config/config.py:255-287]().
3. **Provider String Parsing:** Standardized `provider:model` format for LLMs and embeddings [gpt_researcher/config/config.py:202-220]().
4. **Validation:** Runtime validation for retrievers and providers [gpt_researcher/config/config.py:187-200]().
5. **Deprecation Management:** Backward compatibility for old configuration formats [gpt_researcher/config/config.py:98-145]().
6. **Integration Points:** Direct usage in LLM utilities and throughout the research pipeline [gpt_researcher/utils/llm.py:27-135]().

---

# Page: Configuration Parameters Reference

# Configuration Parameters Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/gpt-researcher/gptr/config.md](docs/docs/gpt-researcher/gptr/config.md)
- [gpt_researcher/actions/query_processing.py](gpt_researcher/actions/query_processing.py)
- [gpt_researcher/config/variables/base.py](gpt_researcher/config/variables/base.py)
- [gpt_researcher/config/variables/default.py](gpt_researcher/config/variables/default.py)

</details>



## Purpose and Scope

This document provides a complete reference of all configuration parameters defined in `DEFAULT_CONFIG`. Each parameter is documented with its type, default value, valid options, and purpose. For information about how configuration is loaded and processed, see [Config Class Architecture](#5.1). For environment variable names and formats, see [Environment Variables Reference](#5.3).

The configuration system is defined in three key files:
- [gpt_researcher/config/variables/default.py:3-55]() - Default values
- [gpt_researcher/config/variables/base.py:5-52]() - Type definitions
- [gpt_researcher/config/config.py:11-278]() - Loading and validation logic

## Configuration Architecture Overview

The configuration system aggregates defaults, environment variables, and optional JSON files into a unified `Config` object used by the `GPTResearcher` agent.

```mermaid
graph TB
    subgraph "Configuration Sources"
        DefaultConfig["DEFAULT_CONFIG<br/>(default.py:3-55)"]
        EnvVars["Environment Variables<br/>(e.g., FAST_LLM, RETRIEVER)"]
        ConfigFile["Custom Config JSON<br/>(optional)"]
    end
    
    subgraph "Type System"
        BaseConfig["BaseConfig TypedDict<br/>(base.py:5-52)"]
        TypeAnnotations["Type Annotations:<br/>str, int, float, bool,<br/>Union, List, Dict"]
    end
    
    subgraph "Loading Process"
        LoadConfig["Config.load_config()<br/>(config.py:124-143)"]
        SetAttrs["Config._set_attributes()<br/>(config.py:40-53)"]
        ConvertTypes["Config.convert_env_value()<br/>(config.py:223-254)"]
    end
    
    subgraph "Parsing & Validation"
        ParseLLM["Config.parse_llm()<br/>(config.py:170-187)"]
        ParseEmbed["Config.parse_embedding()<br/>(config.py:199-216)"]
        ParseRetrievers["Config.parse_retrievers()<br/>(config.py:154-167)"]
        ValidateDocPath["Config.validate_doc_path()<br/>(config.py:218-220)"]
    end
    
    subgraph "Config Instance"
        ConfigAttrs["Config Attributes:<br/>fast_llm_provider,<br/>fast_llm_model,<br/>retrievers, etc."]
    end
    
    DefaultConfig --> LoadConfig
    ConfigFile --> LoadConfig
    LoadConfig --> SetAttrs
    EnvVars --> SetAttrs
    BaseConfig --> ConvertTypes
    SetAttrs --> ConvertTypes
    ConvertTypes --> ConfigAttrs
    
    ConfigAttrs --> ParseLLM
    ConfigAttrs --> ParseEmbed
    ConfigAttrs --> ParseRetrievers
    ConfigAttrs --> ValidateDocPath
    
    ParseLLM --> ConfigAttrs
    ParseEmbed --> ConfigAttrs
    ParseRetrievers --> ConfigAttrs
```

**Sources:** [gpt_researcher/config/config.py:11-278](), [gpt_researcher/config/variables/default.py:3-55](), [gpt_researcher/config/variables/base.py:5-52]()

## Configuration Parameter Categories

The parameters are logically grouped to control different stages of the research pipeline.

```mermaid
graph LR
    subgraph "LLM Configuration"
        FAST_LLM["FAST_LLM<br/>SMART_LLM<br/>STRATEGIC_LLM"]
        TokenLimits["FAST_TOKEN_LIMIT<br/>SMART_TOKEN_LIMIT<br/>STRATEGIC_TOKEN_LIMIT"]
        TEMPERATURE["TEMPERATURE<br/>REASONING_EFFORT"]
        LLM_KWARGS["LLM_KWARGS"]
    end
    
    subgraph "Retriever Configuration"
        RETRIEVER["RETRIEVER"]
        MAX_SEARCH["MAX_SEARCH_RESULTS_PER_QUERY"]
        REPORT_SOURCE["REPORT_SOURCE<br/>DOC_PATH"]
    end
    
    subgraph "Embedding Configuration"
        EMBEDDING["EMBEDDING"]
        SIMILARITY["SIMILARITY_THRESHOLD"]
        EMBEDDING_KWARGS2["EMBEDDING_KWARGS"]
        MEMORY["MEMORY_BACKEND"]
    end
    
    subgraph "Research Behavior"
        MAX_ITERATIONS["MAX_ITERATIONS"]
        MAX_SUBTOPICS["MAX_SUBTOPICS"]
        CURATE["CURATE_SOURCES"]
        AGENT_ROLE["AGENT_ROLE"]
    end
    
    subgraph "Scraping Configuration"
        SCRAPER["SCRAPER"]
        MAX_WORKERS["MAX_SCRAPER_WORKERS"]
        RATE_LIMIT["SCRAPER_RATE_LIMIT_DELAY"]
        BROWSE_CHUNK["BROWSE_CHUNK_MAX_LENGTH"]
        USER_AGENT["USER_AGENT"]
    end
    
    subgraph "Output Configuration"
        TOTAL_WORDS["TOTAL_WORDS"]
        REPORT_FORMAT["REPORT_FORMAT"]
        LANGUAGE["LANGUAGE"]
        SUMMARY_LIMIT["SUMMARY_TOKEN_LIMIT"]
        PROMPT_FAMILY["PROMPT_FAMILY"]
        IMAGE_GEN["IMAGE_GENERATION_ENABLED<br/>IMAGE_GENERATION_MODEL"]
    end
    
    subgraph "Deep Research"
        DEEP_BREADTH["DEEP_RESEARCH_BREADTH"]
        DEEP_DEPTH["DEEP_RESEARCH_DEPTH"]
        DEEP_CONCUR["DEEP_RESEARCH_CONCURRENCY"]
    end
    
    subgraph "MCP Configuration"
        MCP_SERVERS["MCP_SERVERS"]
        MCP_STRATEGY["MCP_STRATEGY"]
        MCP_AUTO["MCP_AUTO_TOOL_SELECTION"]
        MCP_PATHS["MCP_ALLOWED_ROOT_PATHS"]
    end
```

**Sources:** [gpt_researcher/config/variables/default.py:3-55](), [gpt_researcher/config/variables/base.py:5-52]()

## LLM Configuration Parameters

### FAST_LLM
**Type:** `str` | **Default:** `"openai:gpt-4o-mini"` | **Format:** `"<provider>:<model>"`
Model used for fast operations like summaries and quick analyses. Optimized for speed and cost-efficiency.
**Sources:** [gpt_researcher/config/variables/default.py:7]()

### SMART_LLM
**Type:** `str` | **Default:** `"openai:gpt-4.1"` | **Format:** `"<provider>:<model>"`
Model used for complex analysis, generating research reports, and reasoning tasks. Should support long responses (2000+ words).
**Sources:** [gpt_researcher/config/variables/default.py:8]()

### STRATEGIC_LLM
**Type:** `str` | **Default:** `"openai:o4-mini"` | **Format:** `"<provider>:<model>"`
Model used for strategic operations like research planning and query decomposition. The `generate_sub_queries` function uses this model to plan the research outline [gpt_researcher/actions/query_processing.py:73-81]().
**Sources:** [gpt_researcher/config/variables/default.py:9](), [gpt_researcher/actions/query_processing.py:72-81]()

### FAST_TOKEN_LIMIT
**Type:** `int` | **Default:** `3000`
Maximum token limit for `FAST_LLM` responses.
**Sources:** [gpt_researcher/config/variables/default.py:10]()

### SMART_TOKEN_LIMIT
**Type:** `int` | **Default:** `6000`
Maximum token limit for `SMART_LLM` responses. Used as a fallback in `generate_sub_queries` if the strategic LLM fails [gpt_researcher/actions/query_processing.py:103]().
**Sources:** [gpt_researcher/config/variables/default.py:11](), [gpt_researcher/actions/query_processing.py:99-108]()

### STRATEGIC_TOKEN_LIMIT
**Type:** `int` | **Default:** `4000`
Maximum token limit for `STRATEGIC_LLM` responses. Used during retry logic in `generate_sub_queries` [gpt_researcher/actions/query_processing.py:89]().
**Sources:** [gpt_researcher/config/variables/default.py:12](), [gpt_researcher/actions/query_processing.py:83-97]()

### TEMPERATURE
**Type:** `float` | **Default:** `0.4` | **Range:** `0.0 - 1.0`
Sampling temperature for LLM responses. Higher values increase randomness.
**Sources:** [gpt_researcher/config/variables/default.py:16]()

### REASONING_EFFORT
**Type:** `str` | **Default:** `"medium"` | **Valid Values:** `"low"`, `"medium"`, `"high"`
Reasoning effort level for models supporting it. Used in `create_chat_completion` calls [gpt_researcher/actions/query_processing.py:78]().
**Sources:** [gpt_researcher/config/variables/default.py:45](), [gpt_researcher/actions/query_processing.py:72-81]()

### LLM_KWARGS
**Type:** `dict` | **Default:** `{}`
Additional keyword arguments passed to the LLM provider class.
**Sources:** [gpt_researcher/config/variables/default.py:32]()

## Retriever Configuration Parameters

### RETRIEVER
**Type:** `str` | **Default:** `"tavily"`
Web search engine(s) used for retrieving sources. Options: `tavily`, `duckduckgo`, `google`, `bing`, `searchapi`, `serper`, `searx`, `arxiv`.
**Sources:** [gpt_researcher/config/variables/default.py:4](), [docs/docs/gpt-researcher/gptr/config.md:53]()

### MAX_SEARCH_RESULTS_PER_QUERY
**Type:** `int` | **Default:** `5`
Maximum number of search results to retrieve per query.
**Sources:** [gpt_researcher/config/variables/default.py:18]()

### REPORT_SOURCE
**Type:** `str` | **Default:** `"web"`
Source mode for research data. Options: `web`, `local`, `hybrid`, `azure`, `langchain_documents`, `langchain_vectorstore`.
**Sources:** [gpt_researcher/config/variables/default.py:29]()

### DOC_PATH
**Type:** `str` | **Default:** `"./my-docs"`
Path to read and research local documents.
**Sources:** [gpt_researcher/config/variables/default.py:30]()

## Embedding Configuration Parameters

### EMBEDDING
**Type:** `str` | **Default:** `"openai:text-embedding-3-small"`
Embedding model used for similarity search.
**Sources:** [gpt_researcher/config/variables/default.py:5]()

### SIMILARITY_THRESHOLD
**Type:** `float` | **Default:** `0.42`
Threshold for similarity comparison when processing documents.
**Sources:** [gpt_researcher/config/variables/default.py:6]()

### MEMORY_BACKEND
**Type:** `str` | **Default:** `"local"`
Backend used for memory operations.
**Sources:** [gpt_researcher/config/variables/default.py:19]()

### EMBEDDING_KWARGS
**Type:** `dict` | **Default:** `{}`
Additional keyword arguments for the embedding provider.
**Sources:** [gpt_researcher/config/variables/default.py:33]()

## Scraping Configuration Parameters

### SCRAPER
**Type:** `str` | **Default:** `"bs"`
Web scraper to use (e.g., `bs` for BeautifulSoup, `newspaper`).
**Sources:** [gpt_researcher/config/variables/default.py:24]()

### MAX_SCRAPER_WORKERS
**Type:** `int` | **Default:** `15`
Maximum concurrent scraper workers per research.
**Sources:** [gpt_researcher/config/variables/default.py:25]()

### SCRAPER_RATE_LIMIT_DELAY
**Type:** `float` | **Default:** `0.0`
Minimum seconds between scraper requests to handle rate limiting.
**Sources:** [gpt_researcher/config/variables/default.py:26]()

### BROWSE_CHUNK_MAX_LENGTH
**Type:** `int` | **Default:** `8192`
Maximum length of text chunks to browse in web sources.
**Sources:** [gpt_researcher/config/variables/default.py:13]()

## Deep Research Configuration Parameters

Deep research mode performs recursive, tree-like exploration of topics.

```mermaid
graph TB
    RootQuery["Root Query<br/>(Depth 0)"]
    
    subgraph "DEEP_RESEARCH_BREADTH = 3"
        Sub1["Subtopic 1<br/>(Depth 1)"]
        Sub2["Subtopic 2<br/>(Depth 1)"]
        Sub3["Subtopic 3<br/>(Depth 1)"]
    end
    
    subgraph "DEEP_RESEARCH_DEPTH = 2"
        Sub11["Sub-subtopic 1.1<br/>(Depth 2)"]
        Sub12["Sub-subtopic 1.2<br/>(Depth 2)"]
        Sub13["Sub-subtopic 1.3<br/>(Depth 2)"]
    end
    
    ConcurrencyControl["DEEP_RESEARCH_CONCURRENCY = 4<br/>Max 4 parallel operations"]
    
    RootQuery --> Sub1
    RootQuery --> Sub2
    RootQuery --> Sub3
    
    Sub1 --> Sub11
    Sub1 --> Sub12
    Sub1 --> Sub13
    
    Sub1 -.->|"Concurrent"| ConcurrencyControl
    Sub2 -.->|"Concurrent"| ConcurrencyControl
    Sub3 -.->|"Concurrent"| ConcurrencyControl
```

### DEEP_RESEARCH_BREADTH
**Type:** `int` | **Default:** `3`
Number of parallel paths to explore.
**Sources:** [gpt_researcher/config/variables/default.py:36]()

### DEEP_RESEARCH_DEPTH
**Type:** `int` | **Default:** `2`
Number of sequential searches to perform.
**Sources:** [gpt_researcher/config/variables/default.py:37]()

### DEEP_RESEARCH_CONCURRENCY
**Type:** `int` | **Default:** `4`
Maximum concurrent operations in deep research mode.
**Sources:** [gpt_researcher/config/variables/default.py:38]()

## MCP Configuration Parameters

Model Context Protocol (MCP) enables access to specialized data sources.

### MCP_SERVERS
**Type:** `List[Dict[str, Any]]` | **Default:** `[]`
Predefined MCP server configurations.
**Sources:** [gpt_researcher/config/variables/default.py:41]()

### MCP_STRATEGY
**Type:** `str` | **Default:** `"fast"` | **Valid Values:** `"fast"`, `"deep"`, `"disabled"`
Strategy for MCP execution.
**Sources:** [gpt_researcher/config/variables/default.py:44]()

### MCP_AUTO_TOOL_SELECTION
**Type:** `bool` | **Default:** `True`
Automatic selection of the best tool for a query.
**Sources:** [gpt_researcher/config/variables/default.py:42]()

### MCP_ALLOWED_ROOT_PATHS
**Type:** `List[str]` | **Default:** `[]`
Allowed root paths for local file access.
**Sources:** [gpt_researcher/config/variables/default.py:43]()

## Image Generation Parameters

GPT Researcher can generate inline images for reports.

### IMAGE_GENERATION_ENABLED
**Type:** `bool` | **Default:** `False`
Master switch for inline image generation.
**Sources:** [gpt_researcher/config/variables/default.py:52]()

### IMAGE_GENERATION_MODEL
**Type:** `str` | **Default:** `"models/gemini-2.5-flash-image"`
Model used for image generation.
**Sources:** [gpt_researcher/config/variables/default.py:50]()

### IMAGE_GENERATION_MAX_IMAGES
**Type:** `int` | **Default:** `3`
Maximum images to generate per report.
**Sources:** [gpt_researcher/config/variables/default.py:51]()

### IMAGE_GENERATION_STYLE
**Type:** `str` | **Default:** `"dark"` | **Valid Values:** `"dark"`, `"light"`, `"auto"`
Image style preference.
**Sources:** [gpt_researcher/config/variables/default.py:53]()

## Miscellaneous Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `MAX_ITERATIONS` | `int` | `3` | Max iterations for query expansion. [default.py:22]() |
| `MAX_SUBTOPICS` | `int` | `3` | Max subtopics to consider. [default.py:27]() |
| `CURATE_SOURCES` | `bool` | `False` | Whether to curate sources via LLM. [default.py:14]() |
| `LANGUAGE` | `str` | `"english"` | Target language for the report. [default.py:28]() |
| `REPORT_FORMAT` | `str` | `"APA"` | Preferred report format (APA, MLA, etc.). [default.py:21]() |
| `TOTAL_WORDS` | `int` | `1200` | Target word count for processing. [default.py:20]() |
| `PROMPT_FAMILY` | `str` | `"default"` | The family of prompts to use. [default.py:31]() |
| `VERBOSE` | `bool` | `False` | Enable detailed logging. [default.py:34]() |

**Sources:** [gpt_researcher/config/variables/default.py:14-34]()

---

# Page: Environment Variables Reference

# Environment Variables Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [docs/docs/gpt-researcher/gptr/config.md](docs/docs/gpt-researcher/gptr/config.md)
- [gpt_researcher/actions/query_processing.py](gpt_researcher/actions/query_processing.py)
- [gpt_researcher/actions/retriever.py](gpt_researcher/actions/retriever.py)
- [gpt_researcher/config/variables/base.py](gpt_researcher/config/variables/base.py)
- [gpt_researcher/config/variables/default.py](gpt_researcher/config/variables/default.py)
- [gpt_researcher/retrievers/__init__.py](gpt_researcher/retrievers/__init__.py)
- [gpt_researcher/retrievers/openalex/__init__.py](gpt_researcher/retrievers/openalex/__init__.py)
- [gpt_researcher/retrievers/openalex/openalex.py](gpt_researcher/retrievers/openalex/openalex.py)
- [gpt_researcher/retrievers/utils.py](gpt_researcher/retrievers/utils.py)
- [gpt_researcher/retrievers/xquik/__init__.py](gpt_researcher/retrievers/xquik/__init__.py)
- [gpt_researcher/retrievers/xquik/xquik.py](gpt_researcher/retrievers/xquik/xquik.py)

</details>



This page provides a comprehensive reference for all environment variables supported by GPT Researcher. Environment variables are the primary mechanism for configuring API keys, LLM providers, retrievers, and operational settings without modifying code.

For information about the Config class implementation and how environment variables are parsed, see [Config Class Architecture](). For a complete reference of all configuration parameters (including those only available in config files), see [Configuration Parameters Reference]().

## Configuration Priority

GPT Researcher uses a three-tier configuration system where environment variables take highest priority:

```mermaid
graph LR
    Env["Environment Variables<br/>(Highest Priority)"]
    JSON["Custom config.json Files<br/>(Medium Priority)"]
    Default["DEFAULT_CONFIG<br/>(Fallback)"]
    
    Env --> Merged["Final Configuration"]
    JSON --> Merged
    Default --> Merged
    
    Merged --> ConfigClass["Config Instance"]
```

**Configuration Priority Hierarchy**

Sources: [gpt_researcher/config/config.py:157-177]() (Note: Reference based on general architecture logic in `Config` initialization).

## Environment Variable Processing

Environment variables are read and type-converted by the `Config` class during initialization. The system maps environment strings to the `BaseConfig` TypedDict.

```mermaid
graph TB
    Start["Config.__init__()"] --> LoadConfig["load_config()"]
    LoadConfig --> SetAttrs["_set_attributes()"]
    
    SetAttrs --> Loop["For each config key in BaseConfig"]
    Loop --> GetEnv["os.getenv(key)"]
    GetEnv --> Check{Env var exists?}
    
    Check -->|Yes| Convert["convert_env_value()<br/>Type conversion"]
    Check -->|No| UseDefault["Use DEFAULT_CONFIG value"]
    
    Convert --> SetAttr["setattr(self, key.lower(), value)"]
    UseDefault --> SetAttr
    
    SetAttr --> ParseLLM["_set_llm_attributes()<br/>Parse provider:model strings"]
    ParseLLM --> ParseEmbed["_set_embedding_attributes()"]
```

**Environment Variable Processing Flow**

Sources: [gpt_researcher/config/variables/base.py:5-51](), [gpt_researcher/config/variables/default.py:3-55]()

## Required API Keys

These environment variables must be set for basic operation depending on your chosen provider:

| Variable | Type | Description | Required | Example |
|----------|------|-------------|----------|---------|
| `OPENAI_API_KEY` | string | OpenAI API key for GPT models | Yes (if using OpenAI) | `sk-proj-...` |
| `TAVILY_API_KEY` | string | Tavily Search API key for web research | Yes (if using Tavily) | `tvly-...` |
| `XQUIK_API_KEY` | string | X/Twitter Search API key | Yes (if using Xquik) | `xq-...` |
| `GOOGLE_API_KEY` | string | Required for Gemini image generation | Optional | `AIza...` |

Sources: [.env.example:1-3](), [gpt_researcher/retrievers/xquik/xquik.py:30-35](), [docs/docs/gpt-researcher/gptr/config.md:8-11]()

## LLM Configuration

### Provider and Model Selection

GPT Researcher uses a three-tier LLM system. Each variable follows the `provider:model_name` format.

| Variable | Type | Description | Default | Example |
|----------|------|-------------|---------|---------|
| `FAST_LLM` | string | Fast LLM for quick tasks (summaries) | `openai:gpt-4o-mini` | `openai:gpt-4o-mini` |
| `SMART_LLM` | string | Smart LLM for report generation | `openai:gpt-4.1` | `anthropic:claude-3-5-sonnet` |
| `STRATEGIC_LLM` | string | Strategic LLM for research planning | `openai:o4-mini` | `openai:o1-preview` |
| `EMBEDDING` | string | Embedding model for vector operations | `openai:text-embedding-3-small`| `ollama:mxbai-embed-large` |

Sources: [gpt_researcher/config/variables/default.py:5-12](), [docs/docs/gpt-researcher/gptr/config.md:56-58]()

### Token Limits and Performance

| Variable | Type | Description | Default | Recommended for Claude/GPT-5 |
|----------|------|-------------|---------|------------------------------|
| `FAST_TOKEN_LIMIT` | int | Max output tokens for Fast LLM | `3000` | `8000` |
| `SMART_TOKEN_LIMIT` | int | Max output tokens for Smart LLM | `6000` | `16000` - `32000` |
| `STRATEGIC_TOKEN_LIMIT`| int | Max output tokens for Strategic LLM| `4000` | `16000` |

Sources: [gpt_researcher/config/variables/default.py:10-12](), [.env.example:56-64](), [docs/docs/gpt-researcher/gptr/config.md:71-81]()

## Retriever and Scraper Configuration

### Web Search Providers
Set `RETRIEVER` to one of the supported keys.

| Variable | Type | Description | Default | Supported Options |
|----------|------|-------------|---------|-------------------|
| `RETRIEVER` | string | Primary web search engine | `tavily` | `google`, `bing`, `duckduckgo`, `serper`, `arxiv`, `exa`, `xquik`, `openalex`, `mcp` |

Sources: [gpt_researcher/actions/retriever.py:35-103](), [gpt_researcher/retrievers/utils.py:62-80]()

### Scraping Control
Controls how GPT Researcher extracts content from discovered URLs.

| Variable | Type | Description | Default | Example |
|----------|------|-------------|---------|---------|
| `SCRAPER` | string | Web scraper implementation | `bs` | `bs`, `newspaper`, `firecrawl` |
| `MAX_SCRAPER_WORKERS` | int | Max concurrent scraper workers | `15` | `5` (for Firecrawl Hobby) |
| `SCRAPER_RATE_LIMIT_DELAY`| float | Seconds between scraper requests | `0.0` | `2.0` (for 30 req/min) |

Sources: [gpt_researcher/config/variables/default.py:24-26](), [.env.example:12-30]()

## Research Depth and Breadth

These variables control the complexity of the research pipeline.

| Variable | Type | Description | Default |
|----------|------|-------------|---------|
| `MAX_ITERATIONS` | int | Max iterations for query expansion | `3` |
| `MAX_SUBTOPICS` | int | Max subtopics for detailed reports | `3` |
| `DEEP_RESEARCH_BREADTH` | int | Parallel paths in deep research | `3` |
| `DEEP_RESEARCH_DEPTH` | int | Sequential iterations in deep research | `2` |
| `DEEP_RESEARCH_CONCURRENCY`| int | Concurrency for deep research tasks | `4` |

Sources: [gpt_researcher/config/variables/default.py:22-38](), [docs/docs/gpt-researcher/gptr/config.md:91-103]()

## Context and Source Management

| Variable | Type | Description | Default |
|----------|------|-------------|---------|
| `REPORT_SOURCE` | string | Source for data: `web`, `local`, `hybrid` | `web` |
| `DOC_PATH` | string | Directory for local document research | `./my-docs` |
| `CURATE_SOURCES` | bool | Enable LLM-based source ranking/validation | `False` |
| `SIMILARITY_THRESHOLD` | float | Minimum similarity for context chunks | `0.42` |
| `COMPRESSION_THRESHOLD` | int | Char count below which compression is skipped | `8000` |

**Context Processing Logic:**

```mermaid
graph TB
    Scraped["Scraped Content"] --> Threshold{"Length < COMPRESSION_THRESHOLD?"}
    Threshold -->|Yes| Raw["Use Raw Content (Fast Path)"]
    Threshold -->|No| Vector["Vector Store Compression"]
    
    Vector --> Split["Split into BROWSE_CHUNK_MAX_LENGTH"]
    Split --> Filter["Filter by SIMILARITY_THRESHOLD"]
    Filter --> Final["Final Context for LLM"]
    Raw --> Final
```

Sources: [gpt_researcher/config/variables/default.py:6-30](), [.env.example:34-38]()

## Image Generation

GPT Researcher supports generating relevant inline images using Google Gemini or ModelsLab.

| Variable | Type | Description | Default | Options |
|----------|------|-------------|---------|---------|
| `IMAGE_GENERATION_ENABLED` | bool | Master switch for inline images | `False` | `True`, `False` |
| `IMAGE_GENERATION_PROVIDER`| string | Image generation service | `google` | `google`, `modelslab` |
| `IMAGE_GENERATION_MODEL` | string | Model used for generation | `models/gemini-2.5-flash-image` | See Gemini/Imagen models |
| `IMAGE_GENERATION_STYLE` | string | Visual style of images | `dark` | `dark`, `light`, `auto` |
| `IMAGE_GENERATION_MAX_IMAGES`| int | Max images to include per report | `3` | Integer |

Sources: [gpt_researcher/config/variables/default.py:47-54]()

## Model Context Protocol (MCP)

Settings for integrating with MCP servers to access local files or specialized tools.

| Variable | Type | Description | Default |
|----------|------|-------------|---------|
| `MCP_STRATEGY` | string | Execution strategy: `fast`, `deep`, `disabled` | `fast` |
| `MCP_SERVERS` | list | JSON list of MCP server configurations | `[]` |
| `MCP_AUTO_TOOL_SELECTION` | bool | LLM automatically selects best MCP tool | `True` |
| `MCP_ALLOWED_ROOT_PATHS` | list | Allowed paths for local file access | `[]` |

**MCP Sub-query Logic:**
When using `MCPRetriever`, the system may skip sub-query generation to prevent redundant search iterations if MCP is the sole provider.

```python
# gpt_researcher/actions/query_processing.py:145-153
if retriever_names and ("mcp" in retriever_names or "MCPRetriever" in retriever_names):
    mcp_only = (len(retriever_names) == 1 ...)
    if mcp_only:
        return [query] # Skip sub-query generation
```

Sources: [gpt_researcher/config/variables/default.py:40-44](), [gpt_researcher/actions/query_processing.py:143-154]()

## Observability (LangSmith)

Enable LangChain tracing for debugging and performance monitoring.

| Variable | Type | Description | Default |
|----------|------|-------------|---------|
| `LANGCHAIN_TRACING_V2` | bool | Enable LangSmith tracing | `False` |
| `LANGCHAIN_API_KEY` | string | LangSmith API Key | None |
| `LANGCHAIN_PROJECT` | string | Project name for tracing | `gpt-researcher` |

Sources: [.env.example:40-46]()

## Type Conversion Rules

The `Config` class converts environment variable strings into the following Python types based on the `BaseConfig` schema:

| Target Type | Conversion Rule | Example |
|-------------|-----------------|---------|
| `bool` | Case-insensitive: `true`, `1`, `yes` → `True`; else `False` | `CURATE_SOURCES=true` |
| `int` | Standard integer conversion | `TOTAL_WORDS=1200` |
| `float` | Standard float conversion | `TEMPERATURE=0.4` |
| `list` | Parsed as a JSON-formatted list | `MCP_SERVERS='["server1"]'` |
| `dict` | Parsed as a JSON-formatted dictionary | `LLM_KWARGS='{"ctx": 4096}'` |

Sources: [gpt_researcher/config/variables/base.py:5-51](), [gpt_researcher/config/variables/default.py:3-55]()

---

# Page: LLM Integration

# LLM Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/gpt-researcher/llms/llms.md](docs/docs/gpt-researcher/llms/llms.md)
- [docs/docs/gpt-researcher/llms/supported-llms.md](docs/docs/gpt-researcher/llms/supported-llms.md)
- [gpt_researcher/config/config.py](gpt_researcher/config/config.py)
- [gpt_researcher/llm_provider/__init__.py](gpt_researcher/llm_provider/__init__.py)
- [gpt_researcher/llm_provider/generic/base.py](gpt_researcher/llm_provider/generic/base.py)
- [gpt_researcher/memory/embeddings.py](gpt_researcher/memory/embeddings.py)
- [gpt_researcher/utils/llm.py](gpt_researcher/utils/llm.py)

</details>



## Purpose and Scope

This document explains how Large Language Models (LLMs) are integrated and abstracted in GPT Researcher. It covers the provider architecture, the three-tier LLM strategy, supported providers, and model-specific handling. For detailed configuration parameters and environment variables, see [Configuration System](#5). For embeddings and the Memory system, see [Embeddings and Memory System](#6.5).

## Provider Abstraction Architecture

GPT Researcher uses a unified abstraction layer to support over 35 LLM providers through the `GenericLLMProvider` class [gpt_researcher/llm_provider/generic/base.py:13-39](). This design allows seamless switching between providers without modifying application code.

### GenericLLMProvider Class

The `GenericLLMProvider` class wraps LangChain's chat model implementations and provides a consistent interface for all supported providers.

```mermaid
graph TB
    subgraph "Application Layer"
        GPTResearcher["GPTResearcher Class"]
        MultiAgent["Multi-Agent System"]
        ReportGenerator["ReportGenerator"]
        LLMUtils["gpt_researcher/utils/llm.py"]
    end
    
    subgraph "Abstraction Layer"
        GenericLLMProvider["GenericLLMProvider<br/>gpt_researcher/llm_provider/generic/base.py"]
        from_provider["from_provider() classmethod<br/>Dynamic provider loading"]
        get_chat_response["get_chat_response()<br/>Unified invocation"]
        ChatLogger["ChatLogger<br/>Async logging utility"]
    end
    
    subgraph "LangChain Integration"
        ChatOpenAI["langchain_openai.ChatOpenAI"]
        ChatAnthropic["langchain_anthropic.ChatAnthropic"]
        AzureChatOpenAI["langchain_openai.AzureChatOpenAI"]
        ChatOllama["langchain_ollama.ChatOllama"]
        ChatGroq["langchain_groq.ChatGroq"]
        Others["30+ other providers"]
    end
    
    subgraph "Provider APIs"
        OpenAI["OpenAI API"]
        Anthropic["Anthropic API"]
        Azure["Azure OpenAI"]
        OllamaLocal["Ollama Local"]
        Groq["Groq API"]
        MoreAPIs["Other APIs"]
    end
    
    GPTResearcher --> LLMUtils
    LLMUtils --> GenericLLMProvider
    MultiAgent --> GenericLLMProvider
    ReportGenerator --> GenericLLMProvider
    
    GenericLLMProvider --> from_provider
    GenericLLMProvider --> get_chat_response
    GenericLLMProvider --> ChatLogger
    
    from_provider --> ChatOpenAI
    from_provider --> ChatAnthropic
    from_provider --> AzureChatOpenAI
    from_provider --> ChatOllama
    from_provider --> ChatGroq
    from_provider --> Others
    
    ChatOpenAI --> OpenAI
    ChatAnthropic --> Anthropic
    AzureChatOpenAI --> Azure
    ChatOllama --> OllamaLocal
    ChatGroq --> Groq
    Others --> MoreAPIs
```

**Sources:** [gpt_researcher/llm_provider/generic/base.py:92-122](), [gpt_researcher/utils/llm.py:27-38]()

### Dynamic Provider Loading

The `from_provider()` classmethod dynamically loads the appropriate LangChain provider based on the provider string. It includes automatic dependency validation using the `_check_pkg()` helper function [gpt_researcher/llm_provider/generic/base.py:122-310]().

**Key Implementation Details:**

- **Provider Detection**: Uses an `if/elif` chain to route to the correct LangChain implementation, supporting a wide range from `openai` to `minimax` [gpt_researcher/llm_provider/generic/base.py:123-308]().
- **Lazy Import**: Only imports provider-specific packages (e.g., `langchain_openai`, `langchain_anthropic`) when needed to keep the footprint small [gpt_researcher/llm_provider/generic/base.py:125-135]().
- **Metadata Capture**: The class captures `usage_metadata` and `response_metadata` from LLM responses to track token usage and costs [gpt_researcher/llm_provider/generic/base.py:105-119]().
- **Custom Configuration**: Passes provider-specific kwargs (like `openai_api_base` or `azure_deployment`) to constructors [gpt_researcher/llm_provider/generic/base.py:128-143]().

```mermaid
graph LR
    Start["from_provider(provider, **kwargs)"]
    Match["Match provider string"]
    CheckPkg["_check_pkg()<br/>Verify/install dependency"]
    Import["Import LangChain module"]
    Instantiate["Instantiate Chat model"]
    Return["Return GenericLLMProvider<br/>instance"]
    
    Start --> Match
    Match --> CheckPkg
    CheckPkg --> Import
    Import --> Instantiate
    Instantiate --> Return
```

**Sources:** [gpt_researcher/llm_provider/generic/base.py:122-310](), [gpt_researcher/llm_provider/generic/base.py:98-119]()

### Response Generation Utilities

The system provides high-level utilities in `gpt_researcher/utils/llm.py` to manage LLM interactions, including cost estimation and retry logic.

| Function | Purpose | Return Type |
|--------|---------|-------------|
| `get_llm()` | Factory function to get a `GenericLLMProvider` instance [gpt_researcher/utils/llm.py:27-38]() | `GenericLLMProvider` |
| `create_chat_completion()` | Orchestrates chat calls with exponential backoff retries (up to 10 attempts), cost tracking, and token limit validation [gpt_researcher/utils/llm.py:41-146]() | `str` |
| `construct_subtopics()` | Specialized function using `PydanticOutputParser` for structured research planning [gpt_researcher/utils/llm.py:152-199]() | `list` |

**Sources:** [gpt_researcher/utils/llm.py:1-200]()

## Three-Tier LLM Strategy

GPT Researcher employs a three-tier LLM strategy to optimize for both cost and performance. These are initialized in the `Config` class [gpt_researcher/config/config.py:91-96]().

```mermaid
graph TB
    subgraph "LLM Tier Configuration"
        ConfigClass["Config Class<br/>gpt_researcher/config/config.py"]
        FAST_LLM["FAST_LLM<br/>gpt-4o-mini"]
        SMART_LLM["SMART_LLM<br/>gpt-4o"]
        STRATEGIC_LLM["STRATEGIC_LLM<br/>o1-preview"]
    end
    
    subgraph "Tier Usage"
        FastTasks["Fast Tasks<br/>- Sub-query generation<br/>- Basic summaries"]
        SmartTasks["Smart Tasks<br/>- Research planning<br/>- Content synthesis"]
        StrategicTasks["Strategic Tasks<br/>- Multi-agent coordination<br/>- Complex reasoning"]
    end
    
    subgraph "Example Models"
        FastModels["gpt-4o-mini<br/>claude-3-haiku"]
        SmartModels["gpt-4o<br/>claude-3.5-sonnet"]
        StrategicModels["o1-preview<br/>o3-mini"]
    end
    
    FAST_LLM --> ConfigClass
    SMART_LLM --> ConfigClass
    STRATEGIC_LLM --> ConfigClass
    
    ConfigClass --> FastTasks
    ConfigClass --> SmartTasks
    ConfigClass --> StrategicTasks
    
    FastTasks -.-> FastModels
    SmartTasks -.-> SmartModels
    StrategicTasks -.-> StrategicModels
```

### Tier Definitions

- **FAST_LLM**: Used for lightweight operations where speed and low cost are critical. Defaults to `openai:gpt-4o-mini` [gpt_researcher/config/variables/default.py]().
- **SMART_LLM**: The primary workhorse for high-quality research tasks and report generation. Defaults to `openai:gpt-4o` [gpt_researcher/config/variables/default.py]().
- **STRATEGIC_LLM**: Reserved for complex coordination and reasoning-heavy tasks. Defaults to `openai:o1-preview` [gpt_researcher/config/variables/default.py]().

**Sources:** [gpt_researcher/config/config.py:91-96](), [docs/docs/gpt-researcher/llms/llms.md:23-36]()

## Supported Providers

GPT Researcher supports over 35 providers. The internal `_SUPPORTED_PROVIDERS` set tracks valid integration targets [gpt_researcher/llm_provider/generic/base.py:13-39]().

### Provider Categories

| Category | Providers |
|----------|-----------|
| **Major Cloud** | `openai`, `anthropic`, `google_genai`, `google_vertexai`, `cohere` |
| **Enterprise** | `azure_openai`, `bedrock` (AWS), `dashscope` (Alibaba) |
| **High-Speed/Inference** | `groq`, `together`, `fireworks`, `mistralai`, `deepseek`, `vllm_openai` |
| **Local/Custom** | `ollama`, `huggingface`, `custom` |
| **Aggregators** | `litellm`, `openrouter`, `aimlapi`, `netmind` |

**Sources:** [gpt_researcher/llm_provider/generic/base.py:13-39](), [docs/docs/gpt-researcher/llms/supported-llms.md:5-26]()

## Model-Specific Handling

Certain models require special handling due to API constraints or unique features, managed in `gpt_researcher/llm_provider/generic/base.py`.

### Temperature Restrictions

Models that do not support the `temperature` parameter (primarily reasoning models like `o1` and `deepseek-reasoner`) are tracked in `NO_SUPPORT_TEMPERATURE_MODELS` [gpt_researcher/llm_provider/generic/base.py:41-57](). When using these models, the `create_chat_completion` utility automatically sets `temperature` and `max_tokens` to `None` to prevent API errors [gpt_researcher/utils/llm.py:92-97]().

### Reasoning Effort Parameters

OpenAI reasoning models (like `o3-mini`) support a `reasoning_effort` parameter [gpt_researcher/llm_provider/generic/base.py:59-66](). The system defines an Enum `ReasoningEfforts` (High, Medium, Low) and applies the configured effort level during chat completion [gpt_researcher/llm_provider/generic/base.py:68-71](), [gpt_researcher/utils/llm.py:89-90]().

## Embeddings and Memory System

The `Memory` class in `gpt_researcher/memory/embeddings.py` handles vector embeddings for document similarity and retrieval [gpt_researcher/memory/embeddings.py:56-71]().

- **Supported Providers**: Includes 20+ providers such as `openai`, `azure_openai`, `cohere`, `voyageai`, and local `ollama` [gpt_researcher/memory/embeddings.py:32-53]().
- **Default Model**: Defaults to `text-embedding-3-small` for OpenAI [gpt_researcher/memory/embeddings.py:28-30]().
- **Lazy Loading**: Provider-specific LangChain embedding classes are imported only when the specific provider is initialized to avoid unnecessary dependency overhead [gpt_researcher/memory/embeddings.py:87-195]().

**Sources:** [gpt_researcher/memory/embeddings.py:1-200](), [gpt_researcher/config/config.py:85-89]()

## Child Pages
- [LLM Provider Architecture](#6.1)
- [Supported Providers and Models](#6.2)
- [Three-Tier LLM Strategy](#6.3)
- [Model-Specific Handling](#6.4)
- [Embeddings and Memory System](#6.5)

---

# Page: LLM Provider Architecture

# LLM Provider Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/gpt-researcher/llms/llms.md](docs/docs/gpt-researcher/llms/llms.md)
- [docs/docs/gpt-researcher/llms/supported-llms.md](docs/docs/gpt-researcher/llms/supported-llms.md)
- [gpt_researcher/config/config.py](gpt_researcher/config/config.py)
- [gpt_researcher/llm_provider/__init__.py](gpt_researcher/llm_provider/__init__.py)
- [gpt_researcher/llm_provider/generic/base.py](gpt_researcher/llm_provider/generic/base.py)
- [gpt_researcher/memory/embeddings.py](gpt_researcher/memory/embeddings.py)
- [gpt_researcher/utils/llm.py](gpt_researcher/utils/llm.py)

</details>



## Purpose and Scope

This document explains the LLM provider abstraction layer in GPT Researcher, which provides a unified interface for interacting with over 35 different language model providers. The architecture is built around the `GenericLLMProvider` class, which abstracts provider-specific implementations using LangChain's chat model interfaces. This enables the system to switch between providers (OpenAI, Anthropic, local Ollama models, etc.) dynamically based on configuration without requiring changes to the core application logic.

For configuration details about specific providers and API keys, see [Configuration Parameters Reference](). For information about the three-tier LLM strategy (FAST_LLM, SMART_LLM, STRATEGIC_LLM), see [Three-Tier LLM Strategy](). For embedding providers, see [Embeddings and Memory System]().

---

## Architecture Overview

The LLM provider architecture utilizes a factory pattern to instantiate the appropriate LangChain chat model based on the requested provider string. It features dynamic package loading to minimize initial dependency overhead and a centralized utility for managing model-specific parameters like temperature and reasoning effort.

### System-to-Code Mapping: Provider Workflow
The following diagram bridges the high-level request for an LLM to the specific code entities involved in the lifecycle of a chat completion.

```mermaid
graph TB
    subgraph "Natural Language & Request Space"
        UserReq["User Research Request"]
        LLMConfig["LLM Configuration<br/>(FAST_LLM, SMART_LLM)"]
    end

    subgraph "Code Entity Space: gpt_researcher/utils/llm.py"
        create_chat_completion["create_chat_completion()<br/>Line 41"]
        get_llm_util["get_llm()<br/>Line 27"]
    end
    
    subgraph "Code Entity Space: gpt_researcher/llm_provider/generic/base.py"
        GenericLLMProvider["class GenericLLMProvider<br/>Line 92"]
        from_provider["GenericLLMProvider.from_provider()<br/>Line 122"]
        get_chat_response["GenericLLMProvider.get_chat_response()<br/>Line 275"]
        _check_pkg["_check_pkg()<br/>Line 316"]
    end

    UserReq --> create_chat_completion
    LLMConfig --> create_chat_completion
    create_chat_completion --> get_llm_util
    get_llm_util --> from_provider
    from_provider --> _check_pkg
    from_provider --> GenericLLMProvider
    create_chat_completion --> get_chat_response
```
**Sources:** [gpt_researcher/utils/llm.py:27-146](), [gpt_researcher/llm_provider/generic/base.py:92-314]()

---

## GenericLLMProvider Class

The `GenericLLMProvider` class is the central entity for all LLM interactions. It wraps the underlying LangChain `BaseChatModel` and provides standardized methods for both streaming and non-streaming responses, while also tracking usage metadata for cost calculations.

### Class Structure and Metadata Flow

```mermaid
classDiagram
    class GenericLLMProvider {
        +llm: BaseChatModel
        +chat_logger: ChatLogger
        +last_usage_metadata: dict
        +last_response_metadata: dict
        +__init__(llm, chat_log, verbose)
        +from_provider(provider, chat_log, verbose, **kwargs)$
        +get_chat_response(messages, stream, websocket, **kwargs)
        -_capture_response_metadata(message)
    }
    
    class ChatLogger {
        +fname: str
        -_lock: asyncio.Lock
        +log_request(messages, response)
    }
    
    GenericLLMProvider --> ChatLogger : logs to
    GenericLLMProvider --> BaseChatModel : wraps
```

### Key Implementation Details

| Component | Role | File Reference |
|-----------|------|----------------|
| `from_provider` | Static factory that maps provider strings to LangChain classes. | [gpt_researcher/llm_provider/generic/base.py:122-272]() |
| `get_chat_response` | Orchestrates the call to the LLM, handling both streaming and logging. | [gpt_researcher/llm_provider/generic/base.py:275-288]() |
| `_capture_response_metadata` | Extracts token usage and provider-specific metadata from the LLM response. | [gpt_researcher/llm_provider/generic/base.py:105-120]() |
| `ChatLogger` | Async utility to write requests, responses, and stack traces to JSONL. | [gpt_researcher/llm_provider/generic/base.py:74-90]() |

**Sources:** [gpt_researcher/llm_provider/generic/base.py:74-288]()

---

## Dynamic Package Loading

To maintain a lightweight core, GPT Researcher does not include all provider-specific LangChain packages in its base dependencies. Instead, it uses `_check_pkg` to install them on-demand via `subprocess`.

### Package Installation Flow
This diagram shows how the system ensures the environment has the necessary code entities (LangChain adapters) at runtime.

```mermaid
sequenceDiagram
    participant from_provider as "GenericLLMProvider.from_provider()"
    participant check_pkg as "_check_pkg()"
    participant importlib as "importlib.util"
    participant pip as "pip install"
    
    from_provider->>check_pkg: _check_pkg("langchain_anthropic")
    check_pkg->>importlib: find_spec("langchain_anthropic")
    
    alt Package Not Found
        importlib-->>check_pkg: None
        check_pkg->>pip: subprocess.check_call(["pip", "install", "-U", "langchain-anthropic"])
        pip-->>check_pkg: 0 (Success)
    end
    
    check_pkg-->>from_provider: Package available
    from_provider->>from_provider: from langchain_anthropic import ChatAnthropic
```
**Sources:** [gpt_researcher/llm_provider/generic/base.py:316-335]()

---

## Supported Providers

The system supports a wide array of providers, managed via the `_SUPPORTED_PROVIDERS` set.

| Category | Supported Provider Keys |
|----------|-------------------------|
| **Major Cloud** | `openai`, `anthropic`, `google_genai`, `google_vertexai`, `cohere` |
| **Enterprise** | `azure_openai`, `bedrock` (AWS) |
| **Inference APIs** | `groq`, `together`, `fireworks`, `mistralai`, `deepseek`, `xai`, `openrouter`, `litellm`, `aimlapi` |
| **Local/Self-hosted** | `ollama`, `vllm_openai`, `huggingface` |
| **Specialized** | `dashscope`, `gigachat`, `netmind`, `forge`, `avian`, `minimax` |

**Sources:** [gpt_researcher/llm_provider/generic/base.py:13-39](), [docs/docs/gpt-researcher/llms/supported-llms.md:5-26]()

---

## Model-Specific Parameter Handling

The architecture includes logic in `gpt_researcher/utils/llm.py` to handle idiosyncratic behaviors of specific models, particularly regarding temperature and reasoning effort.

### 1. Temperature Restrictions
Certain models (mostly reasoning models) do not support the `temperature` or `max_tokens` parameters. The system uses the `NO_SUPPORT_TEMPERATURE_MODELS` list to nullify these parameters before calling the provider.
* **Affected Models:** `o1-mini`, `o3-mini`, `gpt-5`, `deepseek/deepseek-reasoner`.
* **Reference:** [gpt_researcher/llm_provider/generic/base.py:41-57](), [gpt_researcher/utils/llm.py:92-97]()

### 2. Reasoning Effort
For OpenAI's reasoning models, the system can pass a `reasoning_effort` parameter (`low`, `medium`, `high`). This is enabled for models in the `SUPPORT_REASONING_EFFORT_MODELS` list.
* **Affected Models:** `o3-mini`, `o3`, `o4-mini`.
* **Reference:** [gpt_researcher/llm_provider/generic/base.py:59-66](), [gpt_researcher/utils/llm.py:89-90]()

---

## Embedding Providers Integration

The `Memory` class in `gpt_researcher/memory/embeddings.py` handles the vectorization of research data. It mirrors the LLM provider architecture with a similar `match` statement for provider selection.

### Embedding Implementation Comparison

| Feature | LLM Provider (`GenericLLMProvider`) | Embedding Provider (`Memory`) |
|---------|------------------------------------|-------------------------------|
| **Provider List** | `_SUPPORTED_PROVIDERS` [gpt_researcher/llm_provider/generic/base.py:13]() | `_SUPPORTED_PROVIDERS` [gpt_researcher/memory/embeddings.py:32]() |
| **Custom Base URL** | Supports `OPENAI_BASE_URL` [gpt_researcher/llm_provider/generic/base.py:128]() | Supports `OPENAI_BASE_URL` [gpt_researcher/memory/embeddings.py:104]() |
| **Initialization** | `from_provider` factory method | `__init__` match statement |
| **Base Class** | `BaseChatModel` | `Embeddings` |

**Sources:** [gpt_researcher/memory/embeddings.py:56-187](), [gpt_researcher/llm_provider/generic/base.py:122-272]()

---

## Summary Table: Provider to Package Mapping

| Provider Key | Package Required | LangChain Class |
|--------------|------------------|-----------------|
| `openai` | `langchain-openai` | `ChatOpenAI` |
| `anthropic` | `langchain-anthropic` | `ChatAnthropic` |
| `azure_openai` | `langchain-openai` | `AzureChatOpenAI` |
| `ollama` | `langchain-ollama` | `ChatOllama` |
| `groq` | `langchain-groq` | `ChatGroq` |
| `bedrock` | `langchain-aws` | `ChatBedrock` |
| `google_genai` | `langchain-google-genai` | `ChatGoogleGenerativeAI` |

**Sources:** [gpt_researcher/llm_provider/generic/base.py:122-265]()

---

# Page: Supported Providers and Models

# Supported Providers and Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/gpt-researcher/llms/llms.md](docs/docs/gpt-researcher/llms/llms.md)
- [docs/docs/gpt-researcher/llms/running-with-azure.md](docs/docs/gpt-researcher/llms/running-with-azure.md)
- [docs/docs/gpt-researcher/llms/running-with-ollama.md](docs/docs/gpt-researcher/llms/running-with-ollama.md)
- [docs/docs/gpt-researcher/llms/supported-llms.md](docs/docs/gpt-researcher/llms/supported-llms.md)
- [gpt_researcher/config/__init__.py](gpt_researcher/config/__init__.py)
- [gpt_researcher/config/variables/__init__.py](gpt_researcher/config/variables/__init__.py)
- [gpt_researcher/llm_provider/generic/base.py](gpt_researcher/llm_provider/generic/base.py)
- [gpt_researcher/memory/embeddings.py](gpt_researcher/memory/embeddings.py)
- [multi_agents/agents/utils/llms.py](multi_agents/agents/utils/llms.py)

</details>



This page provides a complete reference of all LLM and embedding providers supported by GPT Researcher, including setup instructions, API key requirements, and configuration examples for each provider. For information about the architecture that enables this multi-provider support, see [LLM Provider Architecture](#6.1). For details on how GPT Researcher uses different model tiers (FAST/SMART/STRATEGIC), see [Three-Tier LLM Strategy](#6.3).

## Provider Support Overview

GPT Researcher supports **25+ LLM providers** and **19+ embedding providers** through a unified abstraction layer built on LangChain. The system uses a factory pattern with automatic dependency management, allowing you to switch between providers by simply changing environment variables without modifying code.

### Provider Factory Architecture

```mermaid
graph TB
    EnvVars["Environment Variables<br/>FAST_LLM=provider:model<br/>SMART_LLM=provider:model<br/>STRATEGIC_LLM=provider:model<br/>EMBEDDING=provider:model"]
    
    Config["Config.parse_llm()<br/>Config.parse_embedding()<br/>gpt_researcher/config/config.py"]
    
    EnvVars --> Config
    
    subgraph "LLM Provider Factory - GenericLLMProvider"
        Factory["GenericLLMProvider.from_provider()<br/>base.py:122"]
        ValidateProvider["Validate against<br/>_SUPPORTED_PROVIDERS<br/>base.py:13-39"]
        CheckPkg["_check_pkg()<br/>base.py:298<br/>Auto-install if missing"]
        Instantiate["Instantiate LangChain<br/>Chat Model<br/>base.py:124-253"]
        
        Config -->|"provider, model, kwargs"| Factory
        Factory --> ValidateProvider
        ValidateProvider --> CheckPkg
        CheckPkg --> Instantiate
    end
    
    subgraph "Embedding Provider Factory - Memory"
        EmbedFactory["Memory.__init__()<br/>embeddings.py:72"]
        EmbedMatch["match embedding_provider<br/>Python match statement<br/>embeddings.py:86-192"]
        EmbedInstantiate["Instantiate LangChain<br/>Embeddings"]
        
        Config -->|"provider, model, kwargs"| EmbedFactory
        EmbedFactory --> EmbedMatch
        EmbedMatch --> EmbedInstantiate
    end
    
    subgraph "Supported LLM Providers"
        OpenAI["openai<br/>ChatOpenAI<br/>base.py:124-131"]
        Anthropic["anthropic<br/>ChatAnthropic<br/>base.py:132-136"]
        Azure["azure_openai<br/>AzureChatOpenAI<br/>base.py:137-145"]
        Ollama["ollama<br/>ChatOllama<br/>base.py:167-171"]
        Groq["groq<br/>ChatGroq<br/>base.py:195-199"]
        Others["bedrock, cohere, dashscope<br/>deepseek, fireworks, gigachat<br/>google_genai, google_vertexai<br/>huggingface, litellm, mistralai<br/>netmind, openrouter, together<br/>vllm_openai, xai, aimlapi, forge, avian, minimax"]
    end
    
    subgraph "Supported Embedding Providers"
        OAIEmbed["openai<br/>OpenAIEmbeddings<br/>embeddings.py:100-107"]
        AzureEmbed["azure_openai<br/>AzureOpenAIEmbeddings<br/>embeddings.py:108-120"]
        OllamaEmbed["ollama<br/>OllamaEmbeddings<br/>embeddings.py:145-151"]
        HFEmbed["huggingface<br/>HuggingFaceEmbeddings<br/>embeddings.py:166-169"]
        OthersEmbed["bedrock, cohere, custom<br/>dashscope, fireworks, gigachat<br/>google_genai, google_vertexai<br/>mistralai, netmind, nomic<br/>together, voyageai, aimlapi, openrouter, minimax"]
    end
    
    Instantiate --> OpenAI
    Instantiate --> Anthropic
    Instantiate --> Azure
    Instantiate --> Ollama
    Instantiate --> Groq
    Instantiate --> Others
    
    EmbedInstantiate --> OAIEmbed
    EmbedInstantiate --> AzureEmbed
    EmbedInstantiate --> OllamaEmbed
    EmbedInstantiate --> HFEmbed
    EmbedInstantiate --> OthersEmbed
```

**Sources:** [gpt_researcher/llm_provider/generic/base.py:13-39](), [gpt_researcher/llm_provider/generic/base.py:122-253](), [gpt_researcher/llm_provider/generic/base.py:298-316](), [gpt_researcher/memory/embeddings.py:32-53](), [gpt_researcher/memory/embeddings.py:72-203]()

## LLM Providers Reference

GPT Researcher supports a wide array of LLM providers via the `GenericLLMProvider` factory class. The following table provides a reference of supported providers:

| Provider | Configuration Key | LangChain Package | API Key Env Var | Base URL Override |
|----------|------------------|-------------------|-----------------|-------------------|
| OpenAI | `openai` | `langchain_openai` | `OPENAI_API_KEY` | `OPENAI_BASE_URL` |
| Anthropic | `anthropic` | `langchain_anthropic` | `ANTHROPIC_API_KEY` | N/A |
| Azure OpenAI | `azure_openai` | `langchain_openai` | `AZURE_OPENAI_API_KEY` | `AZURE_OPENAI_ENDPOINT` |
| Cohere | `cohere` | `langchain_cohere` | `COHERE_API_KEY` | N/A |
| Google Vertex AI | `google_vertexai` | `langchain_google_vertexai` | (GCP credentials) | N/A |
| Google GenAI | `google_genai` | `langchain_google_genai` | `GOOGLE_API_KEY` | N/A |
| Fireworks | `fireworks` | `langchain_fireworks` | `FIREWORKS_API_KEY` | N/A |
| Ollama | `ollama` | `langchain_ollama` | N/A | `OLLAMA_BASE_URL` |
| Together AI | `together` | `langchain_together` | `TOGETHER_API_KEY` | N/A |
| Mistral AI | `mistralai` | `langchain_mistralai` | `MISTRAL_API_KEY` | `MISTRAL_BASE_URL` |
| HuggingFace | `huggingface` | `langchain_huggingface` | `HUGGINGFACE_API_KEY` | N/A |
| Groq | `groq` | `langchain_groq` | `GROQ_API_KEY` | N/A |
| AWS Bedrock | `bedrock` | `langchain_aws` | (AWS credentials) | N/A |
| Dashscope | `dashscope` | `langchain_openai` | `DASHSCOPE_API_KEY` | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| xAI | `xai` | `langchain_xai` | `XAI_API_KEY` | N/A |
| DeepSeek | `deepseek` | `langchain_openai` | `DEEPSEEK_API_KEY` | `https://api.deepseek.com/v1` |
| LiteLLM | `litellm` | `langchain_community` | (varies) | N/A |
| GigaChat | `gigachat` | `langchain_gigachat` | `GIGACHAT_CREDENTIALS` | N/A |
| OpenRouter | `openrouter` | `langchain_openai` | `OPENROUTER_API_KEY` | `https://openrouter.ai/api/v1` |
| vLLM OpenAI | `vllm_openai` | `langchain_openai` | `VLLM_OPENAI_API_KEY` | `VLLM_OPENAI_API_BASE` |
| AI/ML API | `aimlapi` | `langchain_openai` | `AIMLAPI_API_KEY` | `https://api.aimlapi.com` |
| NetMind | `netmind` | `langchain_netmind` | `NETMIND_API_KEY` | N/A |
| Forge | `forge` | (custom) | (varies) | N/A |
| Avian | `avian` | (custom) | (varies) | N/A |
| Minimax | `minimax` | `langchain_openai` | `MINIMAX_API_KEY` | `https://api.minimax.chat/v1` |

**Sources:** [gpt_researcher/llm_provider/generic/base.py:13-39](), [gpt_researcher/llm_provider/generic/base.py:122-253](), [docs/docs/gpt-researcher/llms/llms.md:1-185](), [docs/docs/gpt-researcher/llms/supported-llms.md:3-27]()

## Embedding Providers Reference

GPT Researcher supports 19 embedding providers via the `Memory` class for vector similarity search and context retrieval:

| Provider | Configuration Key | API Key Env Var | Base URL Override |
|----------|------------------|-----------------|-------------------|
| OpenAI | `openai` | `OPENAI_API_KEY` | `OPENAI_BASE_URL` |
| Azure OpenAI | `azure_openai` | `AZURE_OPENAI_API_KEY` | `AZURE_OPENAI_ENDPOINT` |
| Cohere | `cohere` | `COHERE_API_KEY` | N/A |
| GigaChat | `gigachat` | `GIGACHAT_CREDENTIALS` | N/A |
| Google Vertex AI | `google_vertexai` | (GCP credentials) | N/A |
| Google GenAI | `google_genai` | `GOOGLE_API_KEY` | N/A |
| Fireworks | `fireworks` | `FIREWORKS_API_KEY` | N/A |
| Ollama | `ollama` | N/A | `OLLAMA_BASE_URL` |
| Together AI | `together` | `TOGETHER_API_KEY` | N/A |
| Mistral AI | `mistralai` | `MISTRAL_API_KEY` | N/A |
| HuggingFace | `huggingface` | N/A | N/A |
| Nomic | `nomic` | `NOMIC_API_KEY` | N/A |
| Voyage AI | `voyageai` | `VOYAGE_API_KEY` | N/A |
| Dashscope | `dashscope` | `DASHSCOPE_API_KEY` | N/A |
| AWS Bedrock | `bedrock` | (AWS credentials) | N/A |
| AI/ML API | `aimlapi` | `AIMLAPI_API_KEY` | `AIMLAPI_BASE_URL` |
| NetMind | `netmind` | `NETMIND_API_KEY` | N/A |
| OpenRouter | `openrouter` | `OPENROUTER_API_KEY` | N/A |
| Minimax | `minimax` | `MINIMAX_API_KEY` | N/A |
| Custom | `custom` | `OPENAI_API_KEY` | `OPENAI_BASE_URL` |

**Sources:** [gpt_researcher/memory/embeddings.py:32-53](), [gpt_researcher/memory/embeddings.py:72-203]()

## Configuration Format

All providers are configured using the `provider:model` format in environment variables:

```bash
# LLM Configuration
FAST_LLM=provider:model_name
SMART_LLM=provider:model_name
STRATEGIC_LLM=provider:model_name

# Embedding Configuration
EMBEDDING=provider:model_name
```

### Configuration Parsing Flow

```mermaid
graph TB
    EnvVar["Environment Variable<br/>FAST_LLM='openai:gpt-4o'"]
    
    Parse["Config.parse_llm()<br/>Split on ':'"]
    
    Provider["provider = 'openai'"]
    Model["model = 'gpt-4o'"]
    
    Validate["if provider not in<br/>_SUPPORTED_PROVIDERS<br/>base.py:250-252"]
    
    Factory["GenericLLMProvider.from_provider()<br/>base.py:122"]
    
    CheckPackage["_check_pkg('langchain_openai')<br/>base.py:298"]
    
    InstallDecision{Package<br/>installed?}
    
    Install["subprocess.check_call()<br/>pip install -U langchain-openai<br/>base.py:306"]
    
    ImportModule["from langchain_openai<br/>import ChatOpenAI<br/>base.py:125"]
    
    Instantiate["ChatOpenAI(model='gpt-4o')<br/>base.py:131"]
    
    EnvVar --> Parse
    Parse --> Provider
    Parse --> Model
    Provider --> Validate
    Model --> Validate
    Validate --> Factory
    Factory --> CheckPackage
    CheckPackage --> InstallDecision
    InstallDecision -->|No| Install
    InstallDecision -->|Yes| ImportModule
    Install --> ImportModule
    ImportModule --> Instantiate
```

**Sources:** [gpt_researcher/llm_provider/generic/base.py:122-131](), [gpt_researcher/llm_provider/generic/base.py:250-252](), [gpt_researcher/llm_provider/generic/base.py:298-316]()

## Provider-Specific Setup Instructions

### OpenAI

OpenAI is the default and recommended provider.

**Configuration:**
```bash
OPENAI_API_KEY=your_openai_api_key
FAST_LLM=openai:gpt-5-mini
SMART_LLM=openai:gpt-5
STRATEGIC_LLM=openai:o4-mini
EMBEDDING=openai:text-embedding-3-small
```

**Custom OpenAI-Compatible APIs:**
Use custom servers (e.g., llama.cpp) by setting the base URL:
```bash
OPENAI_BASE_URL=http://localhost:1234/v1
OPENAI_API_KEY=dummy_key
FAST_LLM=openai:your_custom_model
EMBEDDING=custom:your_embedding_model
```

**Sources:** [gpt_researcher/llm_provider/generic/base.py:124-131](), [gpt_researcher/memory/embeddings.py:87-106](), [docs/docs/gpt-researcher/llms/llms.md:17-59]()

### Azure OpenAI

Azure OpenAI provides enterprise-grade deployment.

**Configuration:**
```bash
AZURE_OPENAI_API_KEY=your_azure_key
AZURE_OPENAI_ENDPOINT=https://your-endpoint.openai.azure.com/
OPENAI_API_VERSION=2024-05-01-preview
FAST_LLM=azure_openai:gpt-4o-mini
SMART_LLM=azure_openai:gpt-4o
EMBEDDING=azure_openai:text-embedding-3-large
```

**Implementation Details:**
- Uses `AzureChatOpenAI` from `langchain_openai` [gpt_researcher/llm_provider/generic/base.py:137-145]().
- Deployment name is mapped from the `model` parameter [gpt_researcher/llm_provider/generic/base.py:143]().

**Sources:** [gpt_researcher/llm_provider/generic/base.py:137-145](), [gpt_researcher/memory/embeddings.py:108-120](), [docs/docs/gpt-researcher/llms/llms.md:62-97](), [docs/docs/gpt-researcher/llms/running-with-azure.md:10-24]()

### Ollama

Ollama enables running open-source models locally.

**Configuration:**
```bash
OLLAMA_BASE_URL=http://localhost:11434
FAST_LLM=ollama:llama3
EMBEDDING=ollama:nomic-embed-text
```

**Granite Models:**
For IBM Granite models, set the prompt family:
```bash
FAST_LLM=ollama:granite3.3:8b
PROMPT_FAMILY=granite
```

**Sources:** [gpt_researcher/llm_provider/generic/base.py:167-171](), [gpt_researcher/memory/embeddings.py:145-151](), [docs/docs/gpt-researcher/llms/llms.md:101-128](), [docs/docs/gpt-researcher/llms/running-with-ollama.md:25-36]()

### Groq

GroqCloud provides high-speed AI inference.

**Configuration:**
```bash
GROQ_API_KEY=your_groq_key
FAST_LLM=groq:Mixtral-8x7b-32768
```

**Sources:** [gpt_researcher/llm_provider/generic/base.py:195-199](), [docs/docs/gpt-researcher/llms/llms.md:130-162]()

### DeepSeek

DeepSeek provides cost-effective reasoning models.

**Configuration:**
```bash
DEEPSEEK_API_KEY=your_deepseek_key
FAST_LLM=deepseek:deepseek-chat
STRATEGIC_LLM=deepseek:deepseek-reasoner
```

**Note:** `deepseek-reasoner` is included in `NO_SUPPORT_TEMPERATURE_MODELS` [gpt_researcher/llm_provider/generic/base.py:41]().

**Sources:** [gpt_researcher/llm_provider/generic/base.py:41](), [gpt_researcher/llm_provider/generic/base.py:192-199](), [docs/docs/gpt-researcher/llms/llms.md:321-327]()

## Model-Specific Parameter Handling

GPT Researcher includes logic to handle specific constraints of modern models, such as reasoning models that do not support temperature or require reasoning effort parameters.

### Temperature Restrictions
Models that do not support the `temperature` parameter are listed in `NO_SUPPORT_TEMPERATURE_MODELS`. This includes:
- DeepSeek Reasoner [gpt_researcher/llm_provider/generic/base.py:41]()
- OpenAI o1 and o3 families [gpt_researcher/llm_provider/generic/base.py:42-52]()
- Future GPT-5 models [gpt_researcher/llm_provider/generic/base.py:54-55]()

### Reasoning Effort
Models that support the `reasoning_effort` parameter (High, Medium, Low) are listed in `SUPPORT_REASONING_EFFORT_MODELS` [gpt_researcher/llm_provider/generic/base.py:58-65](). This currently includes the OpenAI `o3` and `o4` families.

**Sources:** [gpt_researcher/llm_provider/generic/base.py:40-70]()

## Automatic Dependency Management

GPT Researcher automatically installs required LangChain packages when you first use a provider via the `_check_pkg()` function [gpt_researcher/llm_provider/generic/base.py:298-316]():

1.  Checks if the package is installed using `importlib.util.find_spec()`.
2.  If missing, converts the provider name to a kebab-case package name (e.g., `langchain_openai` -> `langchain-openai`).
3.  Executes `pip install -U {package_name}`.
4.  Attempts to import the module again.

**Sources:** [gpt_researcher/llm_provider/generic/base.py:298-316]()

## Provider Validation

All provider keys are validated against the `_SUPPORTED_PROVIDERS` set before instantiation [gpt_researcher/llm_provider/generic/base.py:13-39]():

```python
_SUPPORTED_PROVIDERS = {
    "openai",
    "anthropic",
    "azure_openai",
    "cohere",
    "google_vertexai",
    "google_genai",
    "fireworks",
    "ollama",
    "together",
    "mistralai",
    "huggingface",
    "groq",
    "bedrock",
    "dashscope",
    "xai",
    "deepseek",
    "litellm",
    "gigachat",
    "openrouter",
    "vllm_openai",
    "aimlapi",
    "netmind",
    "forge",
    "avian",
    "minimax",
}
```

If an unsupported provider is specified, a `ValueError` is raised [gpt_researcher/llm_provider/generic/base.py:250-252]().

**Sources:** [gpt_researcher/llm_provider/generic/base.py:13-39](), [gpt_researcher/llm_provider/generic/base.py:250-252]()

---

# Page: Three-Tier LLM Strategy

# Three-Tier LLM Strategy

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/gpt-researcher/gptr/config.md](docs/docs/gpt-researcher/gptr/config.md)
- [gpt_researcher/actions/query_processing.py](gpt_researcher/actions/query_processing.py)
- [gpt_researcher/config/config.py](gpt_researcher/config/config.py)
- [gpt_researcher/config/variables/base.py](gpt_researcher/config/variables/base.py)
- [gpt_researcher/config/variables/default.py](gpt_researcher/config/variables/default.py)
- [gpt_researcher/llm_provider/__init__.py](gpt_researcher/llm_provider/__init__.py)
- [gpt_researcher/utils/llm.py](gpt_researcher/utils/llm.py)

</details>



## Purpose and Scope

This document explains GPT Researcher's three-tier LLM architecture: `FAST_LLM`, `SMART_LLM`, and `STRATEGIC_LLM`. These tiers optimize the research pipeline by matching LLM capabilities to specific task requirements, balancing cost, speed, and output quality across different research operations.

The system relies on the `Config` class to manage these tiers and the `create_chat_completion` utility to execute them.

---

## Tier Overview

GPT Researcher employs three distinct LLM tiers, each optimized for specific cognitive tasks within the research workflow:

| Tier | Default Model | Token Limit | Primary Use Cases | Cost Profile |
|------|---------------|-------------|-------------------|--------------|
| `FAST_LLM` | `openai:gpt-4o-mini` | 3000 | Summaries, context extraction, introductions | Low |
| `SMART_LLM` | `openai:gpt-4.1` | 6000 | Report writing, complex analysis, subtopic construction | Medium |
| `STRATEGIC_LLM` | `openai:o4-mini` | 4000 | Research planning, query decomposition, reasoning | High |

**Architecture Principle**: Route tasks to the most cost-effective tier capable of producing acceptable results. Strategic models excel at planning but are expensive; fast models handle volume operations efficiently.

Sources: [gpt_researcher/config/variables/default.py:7-12](), [gpt_researcher/config/config.py:93-95]()

---

## Configuration Architecture

### Configuration Loading and Parsing Flow

The `Config` class initializes these tiers by parsing strings in the `provider:model` format. Environment variables take precedence over the `DEFAULT_CONFIG` dictionary.

```mermaid
graph TB
    subgraph "Configuration Sources"
        Env["Environment Variables<br/>(os.getenv)"]
        JsonFile["config.json<br/>(Optional config_path)"]
        Defaults["DEFAULT_CONFIG<br/>default.py"]
    end
    
    subgraph "Config Class Initialization"
        Init["Config.__init__()<br/>config.py:34"]
        SetAttr["_set_attributes()<br/>config.py:62"]
        SetLLM["_set_llm_attributes()<br/>config.py:91"]
        ParseLLM["parse_llm(llm_string)<br/>config.py:221"]
        
        Env --> SetAttr
        JsonFile --> SetAttr
        Defaults --> SetAttr
        SetAttr --> SetLLM
        SetLLM --> ParseLLM
    end
    
    subgraph "Parsed Code Entities"
        ParseLLM --> Fast["self.fast_llm_provider<br/>self.fast_llm_model"]
        ParseLLM --> Smart["self.smart_llm_provider<br/>self.smart_llm_model"]
        ParseLLM --> Strategic["self.strategic_llm_provider<br/>self.strategic_llm_model"]
    end
```

Sources: [gpt_researcher/config/config.py:34-97](), [gpt_researcher/config/variables/default.py:3-12](), [gpt_researcher/config/config.py:221-235]()

---

## Tier Usage in Research Pipeline

### Operational Mapping with Code References

The research pipeline routes specific functions to different tiers based on the complexity of the reasoning required.

```mermaid
graph TD
    subgraph "STRATEGIC_LLM Operations"
        Plan["plan_research_outline()<br/>query_processing.py:112"]
        GenSub["generate_sub_queries()<br/>query_processing.py:37"]
    end

    subgraph "SMART_LLM Operations"
        Subtopics["construct_subtopics()<br/>llm.py:152"]
        Curation["SourceCurator.curate_sources()<br/>curator.py"]
        Writing["Report writing (Main Body)"]
    end

    subgraph "FAST_LLM Operations"
        Summaries["Context summarization"]
        Intro["write_introduction()<br/>writer.py"]
        Conclusion["write_report_conclusion()<br/>writer.py"]
    end

    Plan --> GenSub
    GenSub -->|"Uses Strategic"| StrategicCall["create_chat_completion<br/>(model=cfg.strategic_llm_model)"]
    Subtopics -->|"Uses Smart"| SmartCall["create_chat_completion<br/>(model=cfg.smart_llm_model)"]
    Conclusion -->|"Uses Fast"| FastCall["create_chat_completion<br/>(model=cfg.fast_llm_model)"]
```

### Strategic LLM with Reasoning Models

The `STRATEGIC_LLM` tier often utilizes reasoning models (like OpenAI's o-series). These models require specific handling for `reasoning_effort` and often do not support `temperature`.

- **Reasoning Effort**: Configured via `REASONING_EFFORT` environment variable (default: "medium"). [gpt_researcher/config/variables/default.py:45]()
- **Model Support**: The system checks if a model is in `SUPPORT_REASONING_EFFORT_MODELS` before applying the parameter. [gpt_researcher/utils/llm.py:89-90]()

Sources: [gpt_researcher/utils/llm.py:41-98](), [gpt_researcher/actions/query_processing.py:72-81](), [gpt_researcher/utils/llm.py:152-195]()

---

## Fallback Strategy for Strategic LLM

The `generate_sub_queries` function implements a robust fallback mechanism to ensure the research process continues even if high-end reasoning models fail or hit rate limits.

```mermaid
graph TB
    Start["generate_sub_queries()"]
    
    Try1["Attempt 1: Strategic LLM<br/>(No max_tokens, reasoning_effort)"]
    Try1 -->|Success| Return[Return Sub-queries]
    Try1 -->|Failure| Log1["logger.warning"]
    
    Log1 --> Try2["Attempt 2: Strategic LLM<br/>(With STRATEGIC_TOKEN_LIMIT)"]
    Try2 -->|Success| Return
    Try2 -->|Failure| Log2["logger.warning"]
    
    Log2 --> Try3["Attempt 3: Smart LLM Fallback<br/>(cfg.smart_llm_model)"]
    Try3 -->|Success| Return
    Try3 -->|Failure| Error["Raise RuntimeError"]
```

**Implementation Detail**: 
- The first attempt uses `max_tokens=None` and `reasoning_effort=ReasoningEfforts.Medium.value` to allow reasoning models full expression. [gpt_researcher/actions/query_processing.py:72-81]()
- The second attempt adds `max_tokens=cfg.strategic_token_limit` to handle models that require explicit limits. [gpt_researcher/actions/query_processing.py:86-94]()
- The final fallback switches to the `smart_llm_model` and its associated token limits to ensure task completion. [gpt_researcher/actions/query_processing.py:99-108]()

Sources: [gpt_researcher/actions/query_processing.py:71-110]()

---

## Model Capability Detection

The `create_chat_completion` function in `gpt_researcher/utils/llm.py` dynamically adjusts parameters based on the selected tier's model capabilities:

1.  **Temperature**: If a model is in `NO_SUPPORT_TEMPERATURE_MODELS`, the `temperature` parameter is set to `None`. [gpt_researcher/utils/llm.py:92-97]()
2.  **Reasoning Effort**: If a model is in `SUPPORT_REASONING_EFFORT_MODELS`, the `reasoning_effort` level is passed to the provider. [gpt_researcher/utils/llm.py:89-90]()
3.  **Token Limits**: Different tiers use `FAST_TOKEN_LIMIT`, `SMART_TOKEN_LIMIT`, or `STRATEGIC_TOKEN_LIMIT` accordingly. The system enforces a hard limit of 200,000 tokens as a sanity guard. [gpt_researcher/utils/llm.py:75-81]()

### Tier Comparison Table

| Feature | FAST_LLM | SMART_LLM | STRATEGIC_LLM |
| :--- | :--- | :--- | :--- |
| **Default Model** | `gpt-4o-mini` | `gpt-4.1` | `o4-mini` |
| **Token Limit** | 3000 | 6000 | 4000 |
| **Temperature** | 0.4 (Default) | 0.4 (Default) | N/A (for o-series) |
| **Reasoning Effort** | N/A | N/A | Supported (Medium) |
| **Main Function** | `write_report_conclusion` | `construct_subtopics` | `generate_sub_queries` |

Sources: [gpt_researcher/utils/llm.py:41-98](), [gpt_researcher/config/variables/default.py:3-55](), [gpt_researcher/actions/query_processing.py:72-108]()

---

# Page: Model-Specific Handling

# Model-Specific Handling

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/gpt-researcher/llms/llms.md](docs/docs/gpt-researcher/llms/llms.md)
- [docs/docs/gpt-researcher/llms/supported-llms.md](docs/docs/gpt-researcher/llms/supported-llms.md)
- [gpt_researcher/config/config.py](gpt_researcher/config/config.py)
- [gpt_researcher/llm_provider/__init__.py](gpt_researcher/llm_provider/__init__.py)
- [gpt_researcher/llm_provider/generic/base.py](gpt_researcher/llm_provider/generic/base.py)
- [gpt_researcher/memory/embeddings.py](gpt_researcher/memory/embeddings.py)
- [gpt_researcher/utils/llm.py](gpt_researcher/utils/llm.py)

</details>



## Purpose and Scope

This document details how GPT Researcher dynamically adjusts LLM invocation parameters based on model-specific capabilities. Different LLM models support different features: some models do not accept temperature parameters, while others support specialized reasoning effort controls. The system automatically detects and adapts to these differences to prevent API errors and optimize model behavior.

For general LLM provider configuration, see **6.1 LLM Provider Architecture**. For the three-tier LLM strategy (FAST/SMART/STRATEGIC), see **6.3 Three-Tier LLM Strategy**. For the complete list of supported providers, see **6.2 Supported Providers and Models**.

## Overview

GPT Researcher maintains two critical lists in `gpt_researcher/llm_provider/generic/base.py` that define model capabilities:

- **`NO_SUPPORT_TEMPERATURE_MODELS`**: Models that enforce default temperature only and reject temperature parameters [gpt_researcher/llm_provider/generic/base.py:41-57]().
- **`SUPPORT_REASONING_EFFORT_MODELS`**: Models that support reasoning effort levels for enhanced problem-solving [gpt_researcher/llm_provider/generic/base.py:59-66]().

The system inspects the model name before LLM invocation and removes or adds parameters accordingly, ensuring API calls succeed regardless of which model is configured.

**Sources:** [gpt_researcher/llm_provider/generic/base.py:41-66]()

## Model Capability Detection Architecture

The following diagram illustrates how the system transitions from configuration strings to specific model parameter adjustments.

### Model Parameter Flow
```mermaid
graph TB
    subgraph "NaturalLanguage_ConfigSpace"
        EnvVars["Environment Variables<br/>FAST_LLM: 'openai:o3-mini'"]
        ConfigClass["Config Class<br/>gpt_researcher/config/config.py"]
    end
    
    subgraph "CodeEntitySpace_GenericLLMProvider"
        Factory["GenericLLMProvider.from_provider()"]
        ModelLists["Model Capability Lists<br/>NO_SUPPORT_TEMPERATURE_MODELS<br/>SUPPORT_REASONING_EFFORT_MODELS"]
        
        subgraph "Logic: gpt_researcher/utils/llm.py"
            CheckCap["create_chat_completion()<br/>Check model name against lists"]
            AdjustKwargs["Adjust provider_kwargs dictionary"]
            ReasoningEnum["ReasoningEfforts Enum"]
        end
    end
    
    subgraph "LLMInvocation"
        LangChain["GenericLLMProvider Instance"]
        Invoke["provider.get_chat_response()"]
    end
    
    EnvVars --> ConfigClass
    ConfigClass --> Factory
    Factory --> CheckCap
    ModelLists --> CheckCap
    CheckCap --> AdjustKwargs
    ReasoningEnum -.-> AdjustKwargs
    AdjustKwargs --> LangChain
    LangChain --> Invoke
```

**Sources:** [gpt_researcher/llm_provider/generic/base.py:41-71](), [gpt_researcher/utils/llm.py:41-104](), [gpt_researcher/config/config.py:91-97]()

## Temperature Parameter Handling

### Models Without Temperature Support

The `NO_SUPPORT_TEMPERATURE_MODELS` list identifies models that enforce default temperature settings and will reject API calls that include a `temperature` parameter. This is common in "Reasoning" or "Thought" models.

| Model Pattern | Family | Notes |
|--------------|---------|-------|
| `deepseek/deepseek-reasoner` | DeepSeek | Reasoning-optimized model [gpt_researcher/llm_provider/generic/base.py:42]() |
| `o1-mini`, `o1-mini-2024-09-12` | OpenAI o1 | First-gen reasoning models [gpt_researcher/llm_provider/generic/base.py:43-44]() |
| `o1`, `o1-2024-12-17` | OpenAI o1 | Standard reasoning model [gpt_researcher/llm_provider/generic/base.py:45-46]() |
| `o3-mini`, `o3-mini-2025-01-31` | OpenAI o3 | Compact reasoning model [gpt_researcher/llm_provider/generic/base.py:47-48]() |
| `o1-preview` | OpenAI o1 | Preview version [gpt_researcher/llm_provider/generic/base.py:49]() |
| `o3`, `o3-2025-04-16` | OpenAI o3 | Advanced reasoning model [gpt_researcher/llm_provider/generic/base.py:50-51]() |
| `o4-mini`, `o4-mini-2025-04-16` | OpenAI o4 | Next-gen compact model [gpt_researcher/llm_provider/generic/base.py:52-53]() |
| `gpt-5`, `gpt-5-mini` | OpenAI GPT-5 | Future model family [gpt_researcher/llm_provider/generic/base.py:55-56]() |

**Sources:** [gpt_researcher/llm_provider/generic/base.py:41-57]()

### Implementation Pattern

When `create_chat_completion` prepares to invoke an LLM, it checks if the model name matches any entry in `NO_SUPPORT_TEMPERATURE_MODELS`. If a match is found, the `temperature` and `max_tokens` parameters are set to `None` in the `provider_kwargs` dictionary [gpt_researcher/utils/llm.py:92-97](). This prevents `invalid_request_error` from the provider API.

**Sources:** [gpt_researcher/utils/llm.py:92-97](), [gpt_researcher/llm_provider/generic/base.py:41-57]()

## Reasoning Effort Parameter Handling

### Models With Reasoning Effort Support

The `SUPPORT_REASONING_EFFORT_MODELS` list identifies OpenAI's o-series models that accept a `reasoning_effort` parameter to control the depth of internal "thought" processing:

| Model | Identifier | Reasoning Capability |
|-------|-----------|---------------------|
| o3-mini | `o3-mini`, `o3-mini-2025-01-31` | Compact reasoning with configurable effort [gpt_researcher/llm_provider/generic/base.py:60-61]() |
| o3 | `o3`, `o3-2025-04-16` | Full reasoning with configurable effort [gpt_researcher/llm_provider/generic/base.py:62-63]() |
| o4-mini | `o4-mini`, `o4-mini-2025-04-16` | Next-gen compact with configurable effort [gpt_researcher/llm_provider/generic/base.py:64-65]() |

**Sources:** [gpt_researcher/llm_provider/generic/base.py:59-66]()

### ReasoningEfforts Enum

The `ReasoningEfforts` enum defines the allowed levels for reasoning models:

```python
class ReasoningEfforts(Enum):
    High = "high"
    Medium = "medium"
    Low = "low"
```

**Sources:** [gpt_researcher/llm_provider/generic/base.py:68-71]()

## GenericLLMProvider Integration

The `GenericLLMProvider` acts as the central bridge between the research agents and the various LLM APIs, handling model-specific quirks during instantiation.

### LLM Invocation Lifecycle
```mermaid
graph LR
    subgraph "GenericLLMProvider_base.py:92"
        Init["__init__(llm, chat_log, verbose)"]
        FromProv["from_provider(provider, **kwargs)"]
    end
    
    subgraph "LogicFlow_llm.py"
        CreateChat["create_chat_completion()"]
        Check["Check Model Lists"]
        Filter["Filter/Add Params<br/>(temperature, reasoning_effort)"]
    end
    
    subgraph "Providers_base.py:122-215"
        OpenAI["ChatOpenAI"]
        Anthropic["ChatAnthropic"]
        Azure["AzureChatOpenAI"]
        Ollama["ChatOllama"]
    end
    
    CreateChat --> Check
    Check --> Filter
    Filter --> FromProv
    FromProv --> Init
    Init --> OpenAI
    Init --> Azure
    OpenAI --> Call["provider.get_chat_response()"]
    Azure --> Call
```

**Sources:** [gpt_researcher/llm_provider/generic/base.py:92-215](), [gpt_researcher/utils/llm.py:41-104]()

## Model Name Matching Logic

The system performs exact string matching against the model lists. Model names are matched as they appear in the configuration after parsing:

### Exact Match Examples

| Configuration | Parsed Model Name | Match Result |
|--------------|------------------|--------------|
| `STRATEGIC_LLM=openai:o3-mini` | `o3-mini` | Matches both lists (no temp, reasoning support) |
| `STRATEGIC_LLM=openai:deepseek/deepseek-reasoner` | `deepseek/deepseek-reasoner` | Matches NO_SUPPORT_TEMPERATURE [gpt_researcher/llm_provider/generic/base.py:42]() |
| `FAST_LLM=openai:gpt-4o` | `gpt-4o` | No match, standard parameters apply |

### Special Cases

- **Azure OpenAI**: In Azure, the `azure_deployment` is often mapped to the model name. The `GenericLLMProvider.from_provider` method ensures that if `model` is provided in kwargs, it is also set as the `azure_deployment` [gpt_researcher/llm_provider/generic/base.py:141-145]().
- **Ollama Granite**: GPT Researcher supports custom prompt formatting for the Granite family via the `PROMPT_FAMILY=granite` environment variable [docs/docs/gpt-researcher/llms/llms.md:123-134]().
- **Custom OpenAI Base URL**: If `OPENAI_BASE_URL` is set, the system automatically injects it as `openai_api_base` for OpenAI providers [gpt_researcher/utils/llm.py:99-102]().

**Sources:** [gpt_researcher/llm_provider/generic/base.py:41-57](), [gpt_researcher/llm_provider/generic/base.py:141-145](), [docs/docs/gpt-researcher/llms/llms.md:123-134](), [gpt_researcher/utils/llm.py:99-102]()

## Configuration Examples

### Using Reasoning Models

For strategic tasks with `o3-mini`, the system automatically strips temperature and injects the reasoning effort level:

```python
# gpt_researcher/utils/llm.py:89-90
if model in SUPPORT_REASONING_EFFORT_MODELS:
    provider_kwargs['reasoning_effort'] = reasoning_effort
```

### Using Ollama with Granite

To use the IBM Granite family with specialized prompt formatting:

```env
OLLAMA_BASE_URL=http://localhost:11434
FAST_LLM=ollama:granite3.3:2b
SMART_LLM=ollama:granite3.3:8b
PROMPT_FAMILY=granite
```

**Sources:** [gpt_researcher/utils/llm.py:89-90](), [docs/docs/gpt-researcher/llms/llms.md:123-134]()

## Common Error Prevention

The model-specific handling prevents these common API errors:

| Error | Cause | Solution |
|-------|-------|----------|
| `invalid_request_error: temperature not supported` | Passing temperature to o-series models | Model name in `NO_SUPPORT_TEMPERATURE_MODELS` [gpt_researcher/llm_provider/generic/base.py:41-57]() |
| `invalid_request_error: unknown parameter reasoning_effort` | Passing reasoning_effort to standard models | Only added for models in `SUPPORT_REASONING_EFFORT_MODELS` [gpt_researcher/llm_provider/generic/base.py:59-66]() |
| `max_tokens exceeds limit` | User setting tokens > 200k in env vars | Sanity guard in `create_chat_completion` [gpt_researcher/utils/llm.py:75-81]() |

**Sources:** [gpt_researcher/llm_provider/generic/base.py:41-66](), [gpt_researcher/utils/llm.py:75-81]()

---

# Page: Embeddings and Memory System

# Embeddings and Memory System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/gpt-researcher/llms/llms.md](docs/docs/gpt-researcher/llms/llms.md)
- [docs/docs/gpt-researcher/llms/supported-llms.md](docs/docs/gpt-researcher/llms/supported-llms.md)
- [gpt_researcher/__init__.py](gpt_researcher/__init__.py)
- [gpt_researcher/actions/__init__.py](gpt_researcher/actions/__init__.py)
- [gpt_researcher/context/__init__.py](gpt_researcher/context/__init__.py)
- [gpt_researcher/context/compression.py](gpt_researcher/context/compression.py)
- [gpt_researcher/context/retriever.py](gpt_researcher/context/retriever.py)
- [gpt_researcher/llm_provider/generic/base.py](gpt_researcher/llm_provider/generic/base.py)
- [gpt_researcher/memory/embeddings.py](gpt_researcher/memory/embeddings.py)
- [gpt_researcher/vector_store/__init__.py](gpt_researcher/vector_store/__init__.py)
- [gpt_researcher/vector_store/vector_store.py](gpt_researcher/vector_store/vector_store.py)

</details>



This document covers the embedding generation infrastructure in GPT Researcher, including the `Memory` class, supported embedding providers, configuration mechanisms, and integration with context compression. For LLM provider architecture, see [6.1](). For context compression implementation details, see [9.3](). For vector store integration, see [7.6]().

## Purpose and Scope

The embeddings and memory system provides a unified interface for generating document embeddings across 19+ providers, enabling semantic similarity search, context compression, and retrieval-augmented generation (RAG). The system abstracts provider-specific implementations while maintaining consistent configuration patterns and lazy dependency loading.

---

## Memory Class Architecture

The `Memory` class [gpt_researcher/memory/embeddings.py:56-202]() serves as the central factory for embedding generation, implementing a match-case pattern to instantiate provider-specific LangChain embedding classes.

### Class Structure

```
Memory.__init__(embedding_provider: str, model: str, **embedding_kwargs)
├── Match embedding_provider
│   ├── case "openai" → OpenAIEmbeddings
│   ├── case "azure_openai" → AzureOpenAIEmbeddings
│   ├── case "cohere" → CohereEmbeddings
│   ├── case "google_vertexai" → VertexAIEmbeddings
│   ├── case "google_genai" → GoogleGenerativeAIEmbeddings
│   ├── case "ollama" → OllamaEmbeddings
│   └── ... (19+ total providers)
└── self._embeddings ← Configured embedding instance
```

The class provides a public method `get_embeddings()` [gpt_researcher/memory/embeddings.py:196-202]() that returns the configured LangChain embeddings instance for downstream use.

**Diagram: Memory Class Provider Instantiation**

```mermaid
graph TB
    subgraph "Memory Class Factory"
        MemoryInit["Memory.__init__()<br/>gpt_researcher/memory/embeddings.py"]
        MatchCase["match embedding_provider"]
        EmbeddingsAttr["self._embeddings"]
        GetMethod["get_embeddings()"]
    end
    
    subgraph "Provider Cases"
        OpenAI["case 'openai'<br/>langchain_openai.OpenAIEmbeddings"]
        AzureOpenAI["case 'azure_openai'<br/>langchain_openai.AzureOpenAIEmbeddings"]
        Cohere["case 'cohere'<br/>langchain_cohere.CohereEmbeddings"]
        GoogleVertex["case 'google_vertexai'<br/>langchain_google_vertexai.VertexAIEmbeddings"]
        GoogleGenAI["case 'google_genai'<br/>langchain_google_genai.GoogleGenerativeAIEmbeddings"]
        Ollama["case 'ollama'<br/>langchain_ollama.OllamaEmbeddings"]
        Huggingface["case 'huggingface'<br/>langchain_huggingface.HuggingFaceEmbeddings"]
        Nomic["case 'nomic'<br/>langchain_nomic.NomicEmbeddings"]
        Voyageai["case 'voyageai'<br/>langchain_voyageai.VoyageAIEmbeddings"]
        Dashscope["case 'dashscope'<br/>langchain_community.embeddings.DashScopeEmbeddings"]
        Bedrock["case 'bedrock'<br/>langchain_aws.embeddings.BedrockEmbeddings"]
        Custom["case 'custom'<br/>OpenAIEmbeddings<br/>custom base_url"]
        Other["... 7 more providers"]
    end
    
    subgraph "Downstream Usage"
        ContextCompressor["ContextCompressor<br/>gpt_researcher/context/compression.py"]
        VectorStore["VectorStoreWrapper<br/>gpt_researcher/vector_store/vector_store.py"]
        EmbeddingsFilter["langchain.EmbeddingsFilter"]
    end
    
    MemoryInit --> MatchCase
    MatchCase --> OpenAI
    MatchCase --> AzureOpenAI
    MatchCase --> Cohere
    MatchCase --> GoogleVertex
    MatchCase --> GoogleGenAI
    MatchCase --> Ollama
    MatchCase --> Huggingface
    MatchCase --> Nomic
    MatchCase --> Voyageai
    MatchCase --> Dashscope
    MatchCase --> Bedrock
    MatchCase --> Custom
    MatchCase --> Other
    
    OpenAI --> EmbeddingsAttr
    AzureOpenAI --> EmbeddingsAttr
    Cohere --> EmbeddingsAttr
    GoogleVertex --> EmbeddingsAttr
    GoogleGenAI --> EmbeddingsAttr
    Ollama --> EmbeddingsAttr
    Huggingface --> EmbeddingsAttr
    Nomic --> EmbeddingsAttr
    Voyageai --> EmbeddingsAttr
    Dashscope --> EmbeddingsAttr
    Bedrock --> EmbeddingsAttr
    Custom --> EmbeddingsAttr
    Other --> EmbeddingsAttr
    
    EmbeddingsAttr --> GetMethod
    GetMethod --> ContextCompressor
    GetMethod --> VectorStore
    GetMethod --> EmbeddingsFilter
```

Sources: [gpt_researcher/memory/embeddings.py:56-202](), [gpt_researcher/context/compression.py:98-120](), [gpt_researcher/vector_store/vector_store.py:10-15]()

---

## Supported Embedding Providers

The system supports 20+ embedding providers defined in `_SUPPORTED_PROVIDERS` [gpt_researcher/memory/embeddings.py:32-53]():

| Provider | Case Name | LangChain Class | Environment Variables |
|----------|-----------|-----------------|----------------------|
| OpenAI | `openai` | `OpenAIEmbeddings` | `OPENAI_API_KEY`, `OPENAI_BASE_URL` (optional) |
| Azure OpenAI | `azure_openai` | `AzureOpenAIEmbeddings` | `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_VERSION` |
| Cohere | `cohere` | `CohereEmbeddings` | `COHERE_API_KEY` |
| GigaChat | `gigachat` | `GigaChatEmbeddings` | `GIGACHAT_API_KEY` |
| Google Vertex AI | `google_vertexai` | `VertexAIEmbeddings` | GCP credentials |
| Google Generative AI | `google_genai` | `GoogleGenerativeAIEmbeddings` | `GOOGLE_API_KEY` |
| Fireworks | `fireworks` | `FireworksEmbeddings` | `FIREWORKS_API_KEY` |
| Ollama | `ollama` | `OllamaEmbeddings` | `OLLAMA_BASE_URL` |
| Together AI | `together` | `TogetherEmbeddings` | `TOGETHER_API_KEY` |
| NetMind | `netmind` | `NetmindEmbeddings` | `NETMIND_API_KEY` |
| Mistral AI | `mistralai` | `MistralAIEmbeddings` | `MISTRAL_API_KEY` |
| HuggingFace | `huggingface` | `HuggingFaceEmbeddings` | `HUGGINGFACE_API_KEY` |
| Nomic | `nomic` | `NomicEmbeddings` | `NOMIC_API_KEY` |
| Voyage AI | `voyageai` | `VoyageAIEmbeddings` | `VOYAGE_API_KEY` |
| DashScope | `dashscope` | `DashScopeEmbeddings` | `DASHSCOPE_API_KEY` |
| AWS Bedrock | `bedrock` | `BedrockEmbeddings` | AWS credentials |
| AIML API | `aimlapi` | `OpenAIEmbeddings` | `AIMLAPI_API_KEY`, `AIMLAPI_BASE_URL` |
| OpenRouter | `openrouter` | `OpenAIEmbeddings` | `OPENROUTER_API_KEY` |
| Custom | `custom` | `OpenAIEmbeddings` | `OPENAI_API_KEY`, `OPENAI_BASE_URL` |
| MiniMax | `minimax` | `OpenAIEmbeddings` | `MINIMAX_API_KEY`, `MINIMAX_BASE_URL` |

### Provider-Specific Implementation Examples

**OpenAI** [gpt_researcher/memory/embeddings.py:100-107]():
```python
case "openai":
    from langchain_openai import OpenAIEmbeddings

    # Support custom OpenAI-compatible APIs via OPENAI_BASE_URL
    if "openai_api_base" not in embedding_kwargs and os.environ.get("OPENAI_BASE_URL"):
        embedding_kwargs["openai_api_base"] = os.environ["OPENAI_BASE_URL"]

    _embeddings = OpenAIEmbeddings(model=model, **embedding_kwargs)
```

**Azure OpenAI** [gpt_researcher/memory/embeddings.py:108-120]():
```python
case "azure_openai":
    from langchain_openai import AzureOpenAIEmbeddings

    _embeddings = AzureOpenAIEmbeddings(
        model=model,
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        openai_api_key=os.environ["AZURE_OPENAI_API_KEY"],
        openai_api_version=os.environ.get(
            "AZURE_OPENAI_API_VERSION",
            os.environ.get("OPENAI_API_VERSION"),
        ),
        **embedding_kwargs,
    )
```

Sources: [gpt_researcher/memory/embeddings.py:32-53](), [gpt_researcher/memory/embeddings.py:86-192]()

---

## Integration with Context Compression

The embedding system is central to the context compression pipeline, which reduces the token count of retrieved web pages to fit LLM context windows while preserving relevance.

### ContextCompressor Class

The `ContextCompressor` [gpt_researcher/context/compression.py:85-179]() uses embeddings to filter document chunks based on their semantic similarity to the research query.

**Optimization Strategy**: To improve performance, the compressor calculates the total character count of the input documents. If the total size is below the `COMPRESSION_THRESHOLD` (default: 8000 characters) and the document count is low, it skips the expensive embedding-based pipeline and returns the documents directly [gpt_researcher/context/compression.py:158-171]().

**Diagram: Context Compression Logic Flow**

```mermaid
graph TD
    Start["async_get_context(query)<br/>gpt_researcher/context/compression.py"]
    CheckSize["Calculate total_chars<br/>Check COMPRESSION_THRESHOLD"]
    
    FastPath["Fast Path: No Compression<br/>Return documents directly"]
    StandardPath["Standard Path: Contextual Compression"]
    
    BuildRetriever["__get_contextual_retriever()<br/>gpt_researcher/context/compression.py"]
    Splitter["RecursiveCharacterTextSplitter<br/>chunk_size=1000, overlap=100"]
    RelevanceFilter["EmbeddingsFilter<br/>uses self.embeddings"]
    Pipeline["DocumentCompressorPipeline"]
    
    Invoke["Invoke Pipeline via SearchAPIRetriever"]
    
    CheckSize -- "total_chars < threshold" --> FastPath
    CheckSize -- "total_chars >= threshold" --> StandardPath
    
    StandardPath --> BuildRetriever
    BuildRetriever --> Splitter
    Splitter --> RelevanceFilter
    RelevanceFilter --> Pipeline
    Pipeline --> Invoke
    Invoke --> End["Return Formatted Context"]
    FastPath --> End
```

### WrittenContentCompressor Class

The `WrittenContentCompressor` [gpt_researcher/context/compression.py:181-235]() is specialized for multi-agent workflows where the system needs to retrieve relevant sections from previously written report content. It uses the `SectionRetriever` [gpt_researcher/context/retriever.py:37-67]() as its base retriever.

Sources: [gpt_researcher/context/compression.py:85-235](), [gpt_researcher/context/retriever.py:13-67]()

---

## Vector Store Integration

### VectorStoreWrapper Class

The `VectorStoreWrapper` [gpt_researcher/vector_store/vector_store.py:10-43]() provides a bridge between GPT Researcher's internal document formats and LangChain's vector store interfaces.

| Function | Code Entity | Description |
|----------|-------------|-------------|
| Loading | `load(documents)` | Converts researcher dicts to LangChain `Document` objects and adds them to the store. |
| Conversion | `_create_langchain_documents()` | Maps `raw_content` and `url` from researcher data to LangChain metadata. |
| Splitting | `_split_documents()` | Uses `RecursiveCharacterTextSplitter` with 1000 chunk size and 200 overlap. |
| Search | `asimilarity_search()` | Asynchronous similarity search against the underlying vector store. |

**Diagram: Code Entity Data Flow (Documents to Vector Store)**

```mermaid
graph LR
    subgraph "GPT Researcher Space"
        InputDocs["List[Dict[str, str]]<br/>(raw_content, url)"]
    end

    subgraph "VectorStoreWrapper Entity"
        CreateDocs["_create_langchain_documents()"]
        SplitDocs["_split_documents()"]
        VSLoad["load()"]
    end

    subgraph "LangChain / Vector Store Space"
        LCDocs["List[langchain_core.documents.Document]"]
        VS["langchain_community.vectorstores.VectorStore"]
    end

    InputDocs --> VSLoad
    VSLoad --> CreateDocs
    CreateDocs --> LCDocs
    LCDocs --> SplitDocs
    SplitDocs --> VS
```

Sources: [gpt_researcher/vector_store/vector_store.py:10-43]()

---

## Configuration and Environment Variables

The embedding system is configured primarily via the `EMBEDDING` environment variable.

| Variable | Example | Description |
|----------|---------|-------------|
| `EMBEDDING` | `openai:text-embedding-3-small` | Primary config in `<provider>:<model>` format. |
| `SIMILARITY_THRESHOLD` | `0.35` | Minimum similarity score for context compression [gpt_researcher/context/compression.py:119](). |
| `COMPRESSION_THRESHOLD` | `8000` | Character count below which compression is skipped [gpt_researcher/context/compression.py:159](). |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | Default model if provider is OpenAI [gpt_researcher/memory/embeddings.py:28-30](). |
| `MAX_CONTENT_CHARS` | `50000` | Maximum characters of raw content to embed per document [gpt_researcher/context/retriever.py:13](). |

### Usage Examples

**Azure OpenAI Setup** [docs/docs/gpt-researcher/llms/llms.md:92-103]():
```env
AZURE_OPENAI_API_KEY=[Your Key]
AZURE_OPENAI_ENDPOINT=https://{your-endpoint}.openai.azure.com/
OPENAI_API_VERSION=2024-05-01-preview
EMBEDDING=azure_openai:text-embedding-3-large
```

**Ollama Local Setup** [docs/docs/gpt-researcher/llms/llms.md:113-118]():
```env
OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING=ollama:nomic-embed-text
```

Sources: [gpt_researcher/memory/embeddings.py:28-30](), [gpt_researcher/context/compression.py:119-159](), [docs/docs/gpt-researcher/llms/llms.md:1-120](), [gpt_researcher/context/retriever.py:13]()

---

# Page: Data Sources and Retrieval

# Data Sources and Retrieval

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [gpt_researcher/actions/retriever.py](gpt_researcher/actions/retriever.py)
- [gpt_researcher/retrievers/__init__.py](gpt_researcher/retrievers/__init__.py)
- [gpt_researcher/retrievers/bing/__init__.py](gpt_researcher/retrievers/bing/__init__.py)
- [gpt_researcher/retrievers/bing/bing.py](gpt_researcher/retrievers/bing/bing.py)
- [gpt_researcher/retrievers/google/google.py](gpt_researcher/retrievers/google/google.py)
- [gpt_researcher/retrievers/openalex/__init__.py](gpt_researcher/retrievers/openalex/__init__.py)
- [gpt_researcher/retrievers/openalex/openalex.py](gpt_researcher/retrievers/openalex/openalex.py)
- [gpt_researcher/retrievers/searchapi/searchapi.py](gpt_researcher/retrievers/searchapi/searchapi.py)
- [gpt_researcher/retrievers/searx/searx.py](gpt_researcher/retrievers/searx/searx.py)
- [gpt_researcher/retrievers/serpapi/serpapi.py](gpt_researcher/retrievers/serpapi/serpapi.py)
- [gpt_researcher/retrievers/serper/serper.py](gpt_researcher/retrievers/serper/serper.py)
- [gpt_researcher/retrievers/tavily/tavily_search.py](gpt_researcher/retrievers/tavily/tavily_search.py)
- [gpt_researcher/retrievers/utils.py](gpt_researcher/retrievers/utils.py)
- [gpt_researcher/retrievers/xquik/__init__.py](gpt_researcher/retrievers/xquik/__init__.py)
- [gpt_researcher/retrievers/xquik/xquik.py](gpt_researcher/retrievers/xquik/xquik.py)

</details>



## Purpose and Scope

This document provides an overview of GPT Researcher's data source and retrieval architecture. It covers how the system acquires information from multiple sources including web search engines, local documents, cloud storage, and specialized data providers. The document explains the orchestration layer that routes research queries to appropriate data sources and consolidates results into usable research context.

For detailed implementation specifics of each subsystem, see:
- Web search retriever implementations: [Retriever System](#7.1)
- Parallel web scraping mechanics: [Web Scraping System](#7.2)
- File format parsers and document loaders: [Document Loading System](#7.3)
- Azure Blob Storage integration: [Cloud Storage Integration](#7.4)
- Model Context Protocol for specialized data: [Model Context Protocol (MCP)](#7.5)
- Semantic search and embeddings: [Vector Store Integration](#7.6)
- Source mode configuration reference: [Report Source Modes](#7.7)
- Filtering results by specific domains: [Domain Filtering](#7.8)

## Data Source Architecture

GPT Researcher implements a flexible multi-source data acquisition architecture orchestrated by the `ResearchConductor` class. Data flows from various sources through a unified pipeline that handles scraping, compression, and context assembly.

### Source Type Enumeration

The system defines several distinct source modes via the `ReportSource` enum, allowing the agent to target specific data environments:

| Source Mode | Description | Primary Use Case |
|------------|-------------|------------------|
| `ReportSource.Web` | Web search + scraping | Internet research with search engines |
| `ReportSource.Local` | Local file system documents | Research on proprietary documents (PDF, DOCX, etc.) |
| `ReportSource.Azure` | Azure Blob Storage documents | Cloud-hosted document research |
| `ReportSource.Hybrid` | Local + Web combined | Complement local docs with web data |
| `ReportSource.LangChainDocuments` | Pre-loaded LangChain Document objects | Integration with existing LangChain pipelines |
| `ReportSource.LangChainVectorStore` | Vector store similarity search | Research on pre-embedded document collections |

**Sources:** [gpt_researcher/utils/enum.py:30-51](), [gpt_researcher/agent.py:141]()

### Research Conductor Overview

The `ResearchConductor` class serves as the orchestration layer for all data acquisition, managing the transition from planning to context gathering.

**ResearchConductor Data Flow Diagram**
```mermaid
graph TB
    subgraph "ResearchConductor Orchestration"
        [ResearchConductor] --> [conduct_research]
        [ResearchConductor] --> [plan_research]
    end
    
    subgraph "Source Routing Methods"
        [conduct_research] --> [_get_context_by_urls]
        [conduct_research] --> [_get_context_by_web_search]
        [conduct_research] --> [_get_context_by_vectorstore]
    end
    
    subgraph "Data Sources"
        [_get_context_by_urls] --> [Source_URLs]
        [_get_context_by_web_search] --> [Web_Search_Retrievers]
        [_get_context_by_web_search] --> [Local_Documents]
        [_get_context_by_web_search] --> [Azure_Blob_Storage]
        [_get_context_by_web_search] --> [MCP_Tools]
        [_get_context_by_vectorstore] --> [VectorStoreWrapper]
    end
    
    subgraph "Processing Pipeline"
        [Source_URLs] --> [BrowserManager.browse_urls]
        [Web_Search_Retrievers] --> [BrowserManager.browse_urls]
        [BrowserManager.browse_urls] --> [ContextManager.get_similar_content_by_query]
        [ContextManager.get_similar_content_by_query] --> [SourceCurator.curate_sources]
    end
    
    [SourceCurator.curate_sources] --> FinalContext["Final Research Context"]
```

**Sources:** [gpt_researcher/skills/researcher.py:21-211]()

## Source Selection and Routing

The research workflow begins with source selection based on the `report_source` parameter passed to `GPTResearcher.__init__()`.

**Source Routing Logic**
```mermaid
graph LR
    [GPTResearcher.__init__] --> CheckSource{"report_source value?"}
    
    CheckSource -->|"source_urls provided"| [_get_context_by_urls]
    CheckSource -->|"Web"| [_get_context_by_web_search]
    CheckSource -->|"Local"| [DocumentLoader]
    CheckSource -->|"Azure"| [AzureDocumentLoader]
    CheckSource -->|"Hybrid"| HybridPath["Local + Web Combined"]
    CheckSource -->|"LangChainDocuments"| [LangChainDocumentLoader]
    CheckSource -->|"LangChainVectorStore"| [_get_context_by_vectorstore]
    
    [_get_context_by_urls] --> Context["Research Context"]
    [_get_context_by_web_search] --> Context
    [DocumentLoader] --> Context
    [AzureDocumentLoader] --> Context
    HybridPath --> Context
    [LangChainDocumentLoader] --> Context
    [_get_context_by_vectorstore] --> Context
```

**Sources:** [gpt_researcher/agent.py:51-82](), [gpt_researcher/skills/researcher.py:134-211]()

## Web Search and Retriever System

GPT Researcher supports 17+ search providers through a unified retriever interface. The `get_retrievers()` factory function instantiates retriever classes based on configuration.

### Retriever Factory Pattern

The system determines which search providers to use by checking headers, the `Config` object, or falling back to `TavilySearch` as the default.

**Retriever Resolution Diagram**
```mermaid
graph TB
    subgraph "Configuration Inputs"
        [Headers_retrievers]
        [Config_retrievers]
        [Default_Fallback]
    end
    
    [get_retrievers] --> [get_retriever]
    
    [Headers_retrievers] --> [get_retrievers]
    [Config_retrievers] --> [get_retrievers]
    [Default_Fallback] --> [get_retrievers]
    
    subgraph "Retriever Implementations"
        [get_retriever] --> [TavilySearch]
        [get_retriever] --> [GoogleSearch]
        [get_retriever] --> [BingSearch]
        [get_retriever] --> [Duckduckgo]
        [get_retriever] --> [ArxivSearch]
        [get_retriever] --> [XquikSearch]
        [get_retriever] --> [OpenAlexSearch]
        [get_retriever] --> [MCPRetriever]
    end
```

**Sources:** [gpt_researcher/actions/retriever.py:8-156](), [gpt_researcher/retrievers/__init__.py:1-37]()

### Supported Retrievers

The system currently supports the following retrievers, mapping names to classes in `gpt_researcher/actions/retriever.py`:

*   **General Search:** `tavily`, `google`, `duckduckgo`, `bing`, `searx`, `bocha`, `xquik` (X/Twitter)
*   **Academic/Medical:** `arxiv`, `semantic_scholar`, `pubmed_central`, `openalex`
*   **AI/Neural Search:** `exa`
*   **API Aggregators:** `serper`, `serpapi`, `searchapi`
*   **Protocol Based:** `mcp` (Model Context Protocol)

**Sources:** [gpt_researcher/actions/retriever.py:33-103](), [gpt_researcher/retrievers/utils.py:62-80]()

### Domain Filtering

Users can restrict web search results to specific domains (e.g., `wikipedia.org`). This is primarily implemented by modifying the search query with `site:` operators or using provider-specific parameters.

*   **Google:** Constructs queries like `(site:example.com) query` [gpt_researcher/retrievers/google/google.py:61-63]().
*   **Tavily:** Passes `include_domains` directly to the API [gpt_researcher/retrievers/tavily/tavily_search.py:113]().
*   **Serper:** Appends `-site:excluded.com` or `site:included.com` to the query string [gpt_researcher/retrievers/serper/serper.py:78-86]().

**Sources:** [gpt_researcher/retrievers/google/google.py:59-67](), [gpt_researcher/retrievers/tavily/tavily_search.py:100-115](), [gpt_researcher/retrievers/serper/serper.py:74-91]()

## Web Scraping Pipeline

Once search results are obtained, the `BrowserManager` orchestrates parallel web scraping to extract full page content. Performance is controlled by environment variables like `MAX_SCRAPER_WORKERS` and `SCRAPER_RATE_LIMIT_DELAY`.

**Sources:** [.env.example:12-30](), [gpt_researcher/skills/browser.py:14-116]()

## Document Loading System

GPT Researcher can ingest local files and remote documents using the `DocumentLoader` class.

*   **Local Docs:** Set the `DOC_PATH` environment variable and use `report_source="local"` [.env.example:4]().
*   **Hybrid Mode:** Combines these local documents with real-time web search results.
*   **Cloud Integration:** Integration with Azure Blob Storage allows fetching blobs from containers using the `AZURE_CONNECTION_STRING`.

**Sources:** [gpt_researcher/skills/researcher.py:154-189]()

## Model Context Protocol (MCP) Integration

MCP allows GPT Researcher to interact with external tools and data servers during the research process.

*   **Strategies:** Supports `fast` (single execution) and `deep` (per sub-query) strategies.
*   **Retriever:** The `MCPRetriever` handles communication with MCP servers to fetch context [gpt_researcher/retrievers/mcp.py]().

**Sources:** [gpt_researcher/retrievers/mcp.py](), [gpt_researcher/skills/researcher.py:279-327]()

## Vector Store Integration

The `VectorStoreWrapper` enables semantic similarity search over pre-embedded document collections. This is used when `report_source` is set to `langchain_vectorstore`.

**Sources:** [gpt_researcher/agent.py:63-64](), [gpt_researcher/skills/researcher.py:233-264]()

---

# Page: Retriever System

# Retriever System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [gpt_researcher/actions/retriever.py](gpt_researcher/actions/retriever.py)
- [gpt_researcher/retrievers/__init__.py](gpt_researcher/retrievers/__init__.py)
- [gpt_researcher/retrievers/arxiv/__init__.py](gpt_researcher/retrievers/arxiv/__init__.py)
- [gpt_researcher/retrievers/arxiv/arxiv.py](gpt_researcher/retrievers/arxiv/arxiv.py)
- [gpt_researcher/retrievers/bing/__init__.py](gpt_researcher/retrievers/bing/__init__.py)
- [gpt_researcher/retrievers/bing/bing.py](gpt_researcher/retrievers/bing/bing.py)
- [gpt_researcher/retrievers/bocha/__init__.py](gpt_researcher/retrievers/bocha/__init__.py)
- [gpt_researcher/retrievers/bocha/bocha.py](gpt_researcher/retrievers/bocha/bocha.py)
- [gpt_researcher/retrievers/duckduckgo/duckduckgo.py](gpt_researcher/retrievers/duckduckgo/duckduckgo.py)
- [gpt_researcher/retrievers/exa/__init__.py](gpt_researcher/retrievers/exa/__init__.py)
- [gpt_researcher/retrievers/exa/exa.py](gpt_researcher/retrievers/exa/exa.py)
- [gpt_researcher/retrievers/google/google.py](gpt_researcher/retrievers/google/google.py)
- [gpt_researcher/retrievers/openalex/__init__.py](gpt_researcher/retrievers/openalex/__init__.py)
- [gpt_researcher/retrievers/openalex/openalex.py](gpt_researcher/retrievers/openalex/openalex.py)
- [gpt_researcher/retrievers/pubmed_central/__init__.py](gpt_researcher/retrievers/pubmed_central/__init__.py)
- [gpt_researcher/retrievers/pubmed_central/pubmed_central.py](gpt_researcher/retrievers/pubmed_central/pubmed_central.py)
- [gpt_researcher/retrievers/searchapi/searchapi.py](gpt_researcher/retrievers/searchapi/searchapi.py)
- [gpt_researcher/retrievers/searx/searx.py](gpt_researcher/retrievers/searx/searx.py)
- [gpt_researcher/retrievers/semantic_scholar/__init__.py](gpt_researcher/retrievers/semantic_scholar/__init__.py)
- [gpt_researcher/retrievers/semantic_scholar/semantic_scholar.py](gpt_researcher/retrievers/semantic_scholar/semantic_scholar.py)
- [gpt_researcher/retrievers/serpapi/serpapi.py](gpt_researcher/retrievers/serpapi/serpapi.py)
- [gpt_researcher/retrievers/serper/serper.py](gpt_researcher/retrievers/serper/serper.py)
- [gpt_researcher/retrievers/tavily/tavily_search.py](gpt_researcher/retrievers/tavily/tavily_search.py)
- [gpt_researcher/retrievers/utils.py](gpt_researcher/retrievers/utils.py)
- [gpt_researcher/retrievers/xquik/__init__.py](gpt_researcher/retrievers/xquik/__init__.py)
- [gpt_researcher/retrievers/xquik/xquik.py](gpt_researcher/retrievers/xquik/xquik.py)

</details>



## Purpose and Scope

The Retriever System provides a pluggable architecture for integrating multiple search engines and data sources into GPT Researcher's research workflow. This system abstracts web search operations behind a unified interface, enabling GPT Researcher to query information from over 15 different search providers including Tavily, Google, DuckDuckGo, arXiv, and specialized academic databases.

For information about the overall research workflow orchestration, see [ResearchConductor and Workflow](). For MCP-specific retrieval strategies, see [Model Context Protocol (MCP)](). For general configuration of retrievers, see [Configuration Setup]().

---

## Architecture Overview

The retriever system implements a factory pattern with three primary responsibilities:

1.  **Retriever Discovery**: Maps retriever names to implementation classes.
2.  **Configuration Resolution**: Determines which retrievers to activate based on multiple configuration sources (headers, config files, or environment variables).
3.  **Instantiation**: Creates retriever instances with standardized parameters (`query`, `query_domains`).

### Data Flow: Natural Language to Code Entity Space

The following diagram bridges the user's intent (Natural Language) to the specific code entities responsible for retrieval.

```mermaid
graph TD
    subgraph "Natural Language Space"
        UserIntent["'Search for AI news using Google and Arxiv'"]
    end

    subgraph "Code Entity Space: gpt_researcher/actions/retriever.py"
        GetRetrievers["get_retrievers(headers, cfg)"]
        GetRetriever["get_retriever(retriever_name)"]
        DefaultRetriever["get_default_retriever()"]
    end

    subgraph "Code Entity Space: gpt_researcher/retrievers/"
        TavilySearch["class TavilySearch"]
        GoogleSearch["class GoogleSearch"]
        ArxivSearch["class ArxivSearch"]
        Duckduckgo["class Duckduckgo"]
        PubMed["class PubMedCentralSearch"]
        XquikSearch["class XquikSearch"]
    end

    UserIntent -->|"Configures 'retrievers' string"| GetRetrievers
    GetRetrievers -->|"Iterates and calls"| GetRetriever
    GetRetriever -->|"Matches 'google'"| GoogleSearch
    GetRetriever -->|"Matches 'arxiv'"| ArxivSearch
    GetRetriever -->|"Matches 'xquik'"| XquikSearch
    GetRetriever -->|"Fallback if invalid"| DefaultRetriever
    DefaultRetriever -->|"Returns"| TavilySearch
```

**Sources**: [gpt_researcher/actions/retriever.py:8-103](), [gpt_researcher/actions/retriever.py:109-146](), [gpt_researcher/retrievers/__init__.py:1-37]()

---

## Retriever Factory Pattern

### get_retriever() Mapping

The `get_retriever()` function serves as the central registry. It uses a Python `match` statement to return the uninstantiated class reference for a given string identifier.

| Identifier | Implementation Class | File Path |
| :--- | :--- | :--- |
| `tavily` | `TavilySearch` | [gpt_researcher/retrievers/tavily/tavily_search.py:14-15]() |
| `google` | `GoogleSearch` | [gpt_researcher/retrievers/google/google.py:9-10]() |
| `duckduckgo` | `Duckduckgo` | [gpt_researcher/retrievers/duckduckgo/duckduckgo.py:5-6]() |
| `bing` | `BingSearch` | [gpt_researcher/retrievers/bing/bing.py:10-11]() |
| `serper` | `SerperSearch` | [gpt_researcher/retrievers/serper/serper.py:9-10]() |
| `searx` | `SearxSearch` | [gpt_researcher/retrievers/searx/searx.py:8-9]() |
| `pubmed_central`| `PubMedCentralSearch` | [gpt_researcher/retrievers/pubmed_central/pubmed_central.py:7-8]() |
| `mcp` | `MCPRetriever` | [gpt_researcher/retrievers/__init__.py:14-14]() |
| `xquik` | `XquikSearch` | [gpt_researcher/retrievers/xquik/xquik.py:9-10]() |
| `bocha` | `BoChaSearch` | [gpt_researcher/retrievers/bocha/bocha.py:9-10]() |

**Sources**: [gpt_researcher/actions/retriever.py:35-103](), [gpt_researcher/retrievers/__init__.py:1-37]()

### Resolution Logic in get_retrievers()

The system resolves which retrievers to use by checking sources in a specific hierarchy of precedence:

1.  **Request Headers**: `headers.get("retrievers")` (comma-separated) or `headers.get("retriever")`.
2.  **Config Object**: `cfg.retrievers` (list or string) or `cfg.retriever`.
3.  **Default**: `get_default_retriever()`, which returns `TavilySearch`.

**Sources**: [gpt_researcher/actions/retriever.py:121-140](), [gpt_researcher/actions/retriever.py:149-156]()

---

## Retriever Implementation Details

### Standardized Search Interface

Most retrievers follow a constructor pattern accepting `query` and `query_domains`. The primary execution method is `search(max_results)`.

```mermaid
classDiagram
    class BaseRetriever {
        <<interface>>
        +__init__(query, query_domains)
        +search(max_results) List[Dict]
    }
    class TavilySearch {
        +api_key: str
        +topic: str
        +search(max_results)
    }
    class GoogleSearch {
        +api_key: str
        +cx_key: str
        +search(max_results)
    }
    class SerperSearch {
        +country: str
        +language: str
        +time_range: str
        +search(max_results)
    }
    class PubMedCentralSearch {
        +db_type: str
        +search(max_results)
    }

    BaseRetriever <|-- TavilySearch
    BaseRetriever <|-- GoogleSearch
    BaseRetriever <|-- SerperSearch
    BaseRetriever <|-- PubMedCentralSearch
```

**Sources**: [gpt_researcher/retrievers/tavily/tavily_search.py:14-19](), [gpt_researcher/retrievers/google/google.py:9-13](), [gpt_researcher/retrievers/serper/serper.py:9-13](), [gpt_researcher/retrievers/pubmed_central/pubmed_central.py:7-12]()

### Provider-Specific Features

#### 1. Tavily Search
The default provider. It supports advanced filtering like `search_depth` ("basic" or "advanced") and `topic` ("general" or "news").
*   **Authentication**: `TAVILY_API_KEY` environment variable or `tavily_api_key` in headers.
*   **Domain Filtering**: Supports `include_domains` and `exclude_domains`.

**Sources**: [gpt_researcher/retrievers/tavily/tavily_search.py:45-54](), [gpt_researcher/retrievers/tavily/tavily_search.py:57-88]()

#### 2. Google Search (Custom Search API)
Uses the official Google Custom Search JSON API.
*   **Authentication**: Requires both `GOOGLE_API_KEY` and `GOOGLE_CX_KEY`.
*   **Logic**: Automatically filters out YouTube results to focus on text-based content.

**Sources**: [gpt_researcher/retrievers/google/google.py:22-51](), [gpt_researcher/retrievers/google/google.py:86-89]()

#### 3. Google Serper
A high-performance wrapper for Google Search results with extended parameters.
*   **Filters**: Supports `SERPER_REGION`, `SERPER_LANGUAGE`, and `SERPER_TIME_RANGE` (e.g., `qdr:w` for past week).
*   **Exclusions**: Can globally exclude sites via `SERPER_EXCLUDE_SITES`.

**Sources**: [gpt_researcher/retrievers/serper/serper.py:26-29](), [gpt_researcher/retrievers/serper/serper.py:94-101]()

#### 4. PubMed Central
Specialized for medical and biological research.
*   **Two-Step Process**: First calls `esearch.fcgi` to get article IDs, then `efetch.fcgi` to retrieve full XML text.
*   **Parsing**: Uses `xml.etree.ElementTree` to extract Title, Abstract, and Body content.

**Sources**: [gpt_researcher/retrievers/pubmed_central/pubmed_central.py:13-14](), [gpt_researcher/retrievers/pubmed_central/pubmed_central.py:42-71](), [gpt_researcher/retrievers/pubmed_central/pubmed_central.py:73-125]()

#### 5. Bing Search
General internet search using the Microsoft Bing API.
*   **Authentication**: `BING_API_KEY` environment variable.
*   **Filtering**: Normalizes results by skipping `youtube.com` links.

**Sources**: [gpt_researcher/retrievers/bing/bing.py:32-37](), [gpt_researcher/retrievers/bing/bing.py:84-87]()

---

## Utility Functions

### Package Validation
The `check_pkg` utility ensures that optional dependencies (like `ddgs` for DuckDuckGo) are installed before attempting to instantiate the retriever. It raises an `ImportError` with installation instructions if the package is missing.

**Sources**: [gpt_researcher/retrievers/utils.py:44-59](), [gpt_researcher/retrievers/duckduckgo/duckduckgo.py:10-12]()

### Discovery
`get_all_retriever_names()` dynamically inspects the `gpt_researcher/retrievers/` directory to identify available providers, excluding internal Python directories like `__pycache__`.

**Sources**: [gpt_researcher/retrievers/utils.py:82-103]()

### Output Streaming
The `stream_output` function facilitates real-time communication of retrieval progress to the client via WebSockets.

**Sources**: [gpt_researcher/retrievers/utils.py:14-42]()

---

# Page: Web Scraping System

# Web Scraping System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/gpt-researcher/getting-started/linux-deployment.md](docs/docs/gpt-researcher/getting-started/linux-deployment.md)
- [docs/docs/gpt-researcher/gptr/automated-tests.md](docs/docs/gpt-researcher/gptr/automated-tests.md)
- [docs/docs/gpt-researcher/gptr/example.md](docs/docs/gpt-researcher/gptr/example.md)
- [docs/docs/gpt-researcher/gptr/scraping.md](docs/docs/gpt-researcher/gptr/scraping.md)
- [docs/docs/gpt-researcher/gptr/troubleshooting.md](docs/docs/gpt-researcher/gptr/troubleshooting.md)
- [gpt_researcher/actions/web_scraping.py](gpt_researcher/actions/web_scraping.py)
- [gpt_researcher/scraper/__init__.py](gpt_researcher/scraper/__init__.py)
- [gpt_researcher/scraper/beautiful_soup/beautiful_soup.py](gpt_researcher/scraper/beautiful_soup/beautiful_soup.py)
- [gpt_researcher/scraper/browser/__init__.py](gpt_researcher/scraper/browser/__init__.py)
- [gpt_researcher/scraper/browser/browser.py](gpt_researcher/scraper/browser/browser.py)
- [gpt_researcher/scraper/browser/js/overlay.js](gpt_researcher/scraper/browser/js/overlay.js)
- [gpt_researcher/scraper/browser/nodriver_scraper.py](gpt_researcher/scraper/browser/nodriver_scraper.py)
- [gpt_researcher/scraper/browser/processing/__init__.py](gpt_researcher/scraper/browser/processing/__init__.py)
- [gpt_researcher/scraper/browser/processing/html.py](gpt_researcher/scraper/browser/processing/html.py)
- [gpt_researcher/scraper/browser/processing/scrape_skills.py](gpt_researcher/scraper/browser/processing/scrape_skills.py)
- [gpt_researcher/scraper/scraper.py](gpt_researcher/scraper/scraper.py)
- [gpt_researcher/scraper/tavily_extract/__init__.py](gpt_researcher/scraper/tavily_extract/__init__.py)
- [gpt_researcher/scraper/tavily_extract/tavily_extract.py](gpt_researcher/scraper/tavily_extract/tavily_extract.py)
- [gpt_researcher/scraper/utils.py](gpt_researcher/scraper/utils.py)
- [gpt_researcher/scraper/web_base_loader/web_base_loader.py](gpt_researcher/scraper/web_base_loader/web_base_loader.py)
- [gpt_researcher/utils/logger.py](gpt_researcher/utils/logger.py)

</details>



## Purpose and Scope

The Web Scraping System is responsible for fetching and extracting content from URLs during the research process. This system supports multiple scraping backends, ranging from static HTML parsing to dynamic browser rendering and professional-grade extraction APIs. It utilizes a `WorkerPool` for parallel URL processing and includes intelligent image extraction and deduplication mechanisms.

## Architecture Overview

The web scraping system is built around three core components that work together to efficiently scrape content from multiple URLs in parallel:

```mermaid
graph TB
    subgraph "Research Workflow"
        Conductor["ResearchConductor"]
        URLs["List of URLs"]
    end
    
    subgraph "Parallel Processing Layer"
        WorkerPool["WorkerPool (gpt_researcher/utils/workers.py)"]
        Throttle["worker_pool.throttle()"]
    end
    
    subgraph "Scraping Orchestration"
        ScraperClass["Scraper Class (gpt_researcher/scraper/scraper.py)"]
        extract_data["extract_data_from_url()"]
        get_scraper["get_scraper()"]
    end
    
    subgraph "Scraping Backends"
        BS["BeautifulSoupScraper"]
        ND["NoDriverScraper"]
        Browser["BrowserScraper (Selenium)"]
        Tavily["TavilyExtract"]
        Fire["FireCrawl"]
        PDF["PyMuPDFScraper"]
    end
    
    subgraph "Content Extraction"
        Utils["gpt_researcher/scraper/utils.py"]
        Clean["clean_soup()"]
        Text["get_text_from_soup()"]
        Images["get_relevant_images()"]
    end
    
    Conductor --> URLs
    URLs --> ScraperClass
    
    ScraperClass --> extract_data
    extract_data --> Throttle
    Throttle --> WorkerPool
    extract_data --> get_scraper
    
    get_scraper --> BS
    get_scraper --> ND
    get_scraper --> Browser
    get_scraper --> Tavily
    get_scraper --> Fire
    get_scraper --> PDF
    
    BS --> Utils
    ND --> Utils
    Browser --> Utils
    
    Utils --> Clean
    Utils --> Text
    Utils --> Images
```

**Sources:** [gpt_researcher/scraper/scraper.py:30-195](), [gpt_researcher/scraper/utils.py:1-133](), [gpt_researcher/actions/web_scraping.py:12-42]()

## Scraper Implementation

The `Scraper` class [gpt_researcher/scraper/scraper.py:30]() is the central coordinator for individual URL extraction. It is typically invoked via the `scrape_urls` action [gpt_researcher/actions/web_scraping.py:12-42]().

### URL Deduplication and Throttling
Upon initialization, the `Scraper` removes duplicate URLs to avoid redundant network requests by creating a dictionary from keys to preserve order while ensuring uniqueness [gpt_researcher/scraper/scraper.py:42](). During execution, it uses `self.worker_pool.throttle()` to ensure that concurrent requests stay within the configured limits of the `WorkerPool` [gpt_researcher/scraper/scraper.py:112]().

### Scraper Selection Logic
The `get_scraper` method [gpt_researcher/scraper/scraper.py:171]() determines the appropriate backend based on the URL suffix or domain:
- **PDFs**: `PyMuPDFScraper` [gpt_researcher/scraper/scraper.py:189]()
- **Arxiv**: `ArxivScraper` [gpt_researcher/scraper/scraper.py:190]()
- **Default**: Selected via the `self.scraper` attribute, which is passed from the configuration (defaults to `bs` for BeautifulSoup) [gpt_researcher/scraper/scraper.py:191]().

**Sources:** [gpt_researcher/scraper/scraper.py:41-195](), [gpt_researcher/actions/web_scraping.py:34-35]()

## Scraping Backends

The system provides a modular set of scrapers that all follow a similar interface, returning a tuple of `(content, image_urls, title)`.

### BeautifulSoup (Static)
The `BeautifulSoupScraper` [gpt_researcher/scraper/beautiful_soup/beautiful_soup.py:6]() is the lightweight default. It fetches the page via `self.session.get`, parses it with `lxml`, cleans the HTML using `clean_soup`, and extracts text and images [gpt_researcher/scraper/beautiful_soup/beautiful_soup.py:24-38]().

### NoDriver (Dynamic)
The `NoDriverScraper` [gpt_researcher/scraper/browser/nodriver_scraper.py:16]() provides high-performance dynamic scraping using the `zendriver` package [gpt_researcher/scraper/browser/nodriver_scraper.py:141]().
- **Load Balancing**: It manages a pool of browser instances (`max_browsers = 5`), routing requests to the browser with the lowest `processing_count` [gpt_researcher/scraper/browser/nodriver_scraper.py:18-21](), [gpt_researcher/scraper/browser/nodriver_scraper.py:163]().
- **Rate Limiting**: Implements `rate_limit_for_domain` using `asyncio.Semaphore` per domain to prevent aggressive hitting of single hosts [gpt_researcher/scraper/browser/nodriver_scraper.py:108-122]().
- **Interaction**: Automatically scrolls pages using `scroll_page_to_bottom` to trigger lazy-loading of content [gpt_researcher/scraper/browser/nodriver_scraper.py:59-80]().

### BrowserScraper (Selenium)
The `BrowserScraper` [gpt_researcher/scraper/browser/browser.py:24]() uses Selenium for full browser emulation. It supports Chrome, Firefox, and Safari [gpt_researcher/scraper/browser/browser.py:86-90](), handles cookie persistence via pickle files [gpt_researcher/scraper/browser/browser.py:121-130](), and can run in headless mode [gpt_researcher/scraper/browser/browser.py:94]().

### Production APIs (Tavily & FireCrawl)
For high-scale use cases, the system supports `TavilyExtract` and `FireCrawl` [gpt_researcher/scraper/scraper.py:49-52](). These require external API keys and handle anti-bot measures automatically [docs/docs/gpt-researcher/gptr/scraping.md:84-134]().

**Sources:** [gpt_researcher/scraper/browser/nodriver_scraper.py:16-173](), [gpt_researcher/scraper/browser/browser.py:24-119](), [gpt_researcher/scraper/beautiful_soup/beautiful_soup.py:6-42](), [docs/docs/gpt-researcher/gptr/scraping.md:7-35]()

## Content Extraction and Cleaning

Extraction utilities are centralized in `gpt_researcher/scraper/utils.py` to ensure consistency across different scraping backends.

```mermaid
graph LR
    RawHTML["Raw HTML"]
    CleanSoup["clean_soup() (gpt_researcher/scraper/utils.py)"]
    GetText["get_text_from_soup() (gpt_researcher/scraper/utils.py)"]
    GetImages["get_relevant_images() (gpt_researcher/scraper/utils.py)"]
    
    RawHTML --> CleanSoup
    CleanSoup -->|"Remove script/style/nav/footer"| GetText
    CleanSoup -->|"Score img tags"| GetImages
```

- **Cleaning**: `clean_soup` removes `script`, `style`, `footer`, `header`, `nav`, `menu`, `sidebar`, and `svg` tags [gpt_researcher/scraper/utils.py:95-109](). It also decomposes elements with disallowed classes [gpt_researcher/scraper/utils.py:111-123]().
- **Text Extraction**: `get_text_from_soup` uses `soup.get_text`, strips whitespace, and normalizes multiple spaces into a single space [gpt_researcher/scraper/utils.py:128-133]().
- **Image Scoring**: `get_relevant_images` scores images based on class names (e.g., "header", "featured", "hero" get 4 points) and dimensions parsed via `parse_dimension` [gpt_researcher/scraper/utils.py:16-52]().

**Sources:** [gpt_researcher/scraper/utils.py:16-133]()

## Image Selection and Deduplication

Images are processed to ensure only high-quality, unique visual content is returned to the researcher.

1. **Deduplication**: The system uses `get_image_hash` [gpt_researcher/scraper/utils.py:73]() which calculates an MD5 hash based on the image filename and essential query parameters [gpt_researcher/scraper/utils.py:89]().
2. **Ranking**: Images are extracted and stored with their calculated scores [gpt_researcher/scraper/utils.py:47](). The `get_relevant_images` function sorts them and returns the top 10 candidates per page [gpt_researcher/scraper/utils.py:49-52]().

**Sources:** [gpt_researcher/scraper/utils.py:16-52](), [gpt_researcher/scraper/utils.py:73-92]()

## Configuration Parameters

The behavior of the scraping system is controlled via the `Config` class and environment variables.

| Parameter | Environment Variable | Default | Description |
|-----------|---------------------|---------|-------------|
| `scraper` | `SCRAPER` | `"bs"` | Backend selection: `bs`, `browser`, `nodriver`, `tavily_extract`, `firecrawl` |
| `max_scraper_workers` | `MAX_SCRAPER_WORKERS` | `8` | Maximum concurrent scraping tasks in the `WorkerPool` |
| `scraper_rate_limit_delay` | `SCRAPER_RATE_LIMIT_DELAY` | `0.1` | Throttle delay between worker tasks |

**Sources:** [docs/docs/gpt-researcher/gptr/scraping.md:7-35](), [gpt_researcher/scraper/browser/nodriver_scraper.py:18-19](), [gpt_researcher/actions/web_scraping.py:12-35]()

---

# Page: Document Loading System

# Document Loading System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/gpt-researcher/gptr/ai-development.md](docs/docs/gpt-researcher/gptr/ai-development.md)
- [docs/docs/gpt-researcher/gptr/image_generation.md](docs/docs/gpt-researcher/gptr/image_generation.md)
- [gpt_researcher/document/__init__.py](gpt_researcher/document/__init__.py)
- [gpt_researcher/document/document.py](gpt_researcher/document/document.py)
- [gpt_researcher/document/langchain_document.py](gpt_researcher/document/langchain_document.py)
- [gpt_researcher/scraper/arxiv/__init__.py](gpt_researcher/scraper/arxiv/__init__.py)
- [gpt_researcher/scraper/arxiv/arxiv.py](gpt_researcher/scraper/arxiv/arxiv.py)
- [gpt_researcher/scraper/beautiful_soup/__init__.py](gpt_researcher/scraper/beautiful_soup/__init__.py)
- [gpt_researcher/scraper/pymupdf/__init__.py](gpt_researcher/scraper/pymupdf/__init__.py)
- [gpt_researcher/scraper/pymupdf/pymupdf.py](gpt_researcher/scraper/pymupdf/pymupdf.py)
- [gpt_researcher/scraper/web_base_loader/__init__.py](gpt_researcher/scraper/web_base_loader/__init__.py)
- [pyproject.toml](pyproject.toml)
- [setup.py](setup.py)

</details>



The Document Loading System enables GPT Researcher to process local files as research sources. This system is responsible for reading various document formats from the filesystem and transforming them into a standardized structure that can be consumed by the research pipeline. For cloud-based document storage, see [7.4 Cloud Storage Integration](). For configuring document sources in research tasks, see [7.7 Report Source Modes]().

## DocumentLoader Class Architecture

The `DocumentLoader` class [gpt_researcher/document/document.py:16-16]() is the central component of the document loading system, providing a unified interface for loading multiple document formats asynchronously. It leverages the LangChain ecosystem to handle diverse file types.

### Class Diagram: DocumentLoader and LangChain Integration

```mermaid
classDiagram
    class DocumentLoader {
        +path Union[str, List[str]]
        +__init__(path)
        +load() list
        -_load_document(file_path, file_extension) list
    }
    
    class PyMuPDFLoader {
        +load() list
    }
    
    class TextLoader {
        +load() list
    }
    
    class UnstructuredWordDocumentLoader {
        +load() list
    }
    
    class UnstructuredPowerPointLoader {
        +load() list
    }
    
    class UnstructuredCSVLoader {
        +__init__(mode)
        +load() list
    }
    
    class UnstructuredExcelLoader {
        +__init__(mode)
        +load() list
    }
    
    class UnstructuredMarkdownLoader {
        +load() list
    }
    
    class BSHTMLLoader {
        +load() list
    }
    
    DocumentLoader ..> PyMuPDFLoader : "instantiates"
    DocumentLoader ..> TextLoader : "instantiates"
    DocumentLoader ..> UnstructuredWordDocumentLoader : "instantiates"
    DocumentLoader ..> UnstructuredPowerPointLoader : "instantiates"
    DocumentLoader ..> UnstructuredCSVLoader : "instantiates"
    DocumentLoader ..> UnstructuredExcelLoader : "instantiates"
    DocumentLoader ..> UnstructuredMarkdownLoader : "instantiates"
    DocumentLoader ..> BSHTMLLoader : "instantiates"
```

**Sources:** [gpt_researcher/document/document.py:16-93]()

### Constructor Parameters

The `DocumentLoader` accepts flexible path inputs [gpt_researcher/document/document.py:18-19]():

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | `str` | Directory path to recursively load all documents |
| `path` | `List[str]` | List of specific file paths to load |
| `path` | `os.PathLike` | Path-like object for directory traversal |

**Sources:** [gpt_researcher/document/document.py:18-19]()

### Output Format

The `load()` method returns a list of document dictionaries with a standardized structure used throughout the research context [gpt_researcher/document/document.py:53-56]():

```python
{
    "raw_content": str,  # Extracted text content from the file
    "url": str          # Original filename (basename) used as a source reference
}
```

**Sources:** [gpt_researcher/document/document.py:53-56]()

## Supported File Formats

The system supports 11+ file extensions through 8 primary LangChain loaders [gpt_researcher/document/document.py:66-78]():

| File Extension | LangChain Loader Class | Implementation Detail |
|----------------|------------------------|-----------------------|
| `.pdf` | `PyMuPDFLoader` | High-performance PDF parsing [gpt_researcher/document/document.py:67-67]() |
| `.txt` | `TextLoader` | Standard UTF-8 text loading [gpt_researcher/document/document.py:68-68]() |
| `.doc`, `.docx`| `UnstructuredWordDocumentLoader` | Handles legacy and modern Word formats [gpt_researcher/document/document.py:69-70]() |
| `.pptx` | `UnstructuredPowerPointLoader` | Extracts text from slides [gpt_researcher/document/document.py:71-71]() |
| `.csv` | `UnstructuredCSVLoader` | Uses `mode="elements"` for granular parsing [gpt_researcher/document/document.py:72-72]() |
| `.xls`, `.xlsx`| `UnstructuredExcelLoader` | Uses `mode="elements"` for spreadsheet data [gpt_researcher/document/document.py:73-74]() |
| `.md` | `UnstructuredMarkdownLoader` | Parses markdown syntax [gpt_researcher/document/document.py:75-75]() |
| `.html`, `.htm`| `BSHTMLLoader` | Uses BeautifulSoup4 for HTML cleaning [gpt_researcher/document/document.py:76-77]() |

**Sources:** [gpt_researcher/document/document.py:66-78](), [pyproject.toml:13-36]()

## Loading Process and Workflow

The document loading process follows an asynchronous pattern to efficiently handle multiple files concurrently.

### Sequence Diagram: Document Loading Flow

```mermaid
sequenceDiagram
    participant App as "GPTResearcher Agent"
    participant DL as "DocumentLoader"
    participant OS as "os/asyncio"
    participant LC as "LangChain Loaders"
    
    App->>DL: load()
    
    alt Path is List
        loop Each file_path
            DL->>OS: os.path.isfile(file_path)
            DL->>DL: _load_document(path, ext)
        end
    else Path is Directory
        DL->>OS: os.walk(path)
        loop Each file in walk
            DL->>DL: _load_document(path, ext)
        end
    end
    
    DL->>OS: asyncio.gather(*tasks)
    
    loop Concurrent Loading
        OS->>LC: loader.load()
        LC-->>OS: List[Document]
    end
    
    OS-->>DL: results
    
    loop Processing Results
        DL->>DL: Filter empty page_content
        DL->>DL: Map to {"raw_content", "url"}
    end
    
    DL-->>App: List[Dict]
```

**Sources:** [gpt_researcher/document/document.py:21-61]()

### Loading Algorithm

1.  **Path Resolution**: The system checks if `self.path` is a list or a directory string [gpt_researcher/document/document.py:23-40]().
2.  **Extension Normalization**: Extensions are stripped of dots and converted to lowercase for dictionary lookup [gpt_researcher/document/document.py:27-28]().
3.  **Task Aggregation**: Each valid file creates a coroutine via `_load_document()` [gpt_researcher/document/document.py:29-37]().
4.  **Asynchronous Execution**: `asyncio.gather` triggers all loaders in parallel [gpt_researcher/document/document.py:50-50]().
5.  **Metadata Extraction**: The system extracts the `source` metadata field to populate the `url` key [gpt_researcher/document/document.py:55-55]().

**Sources:** [gpt_researcher/document/document.py:21-61]()

## Specialized Scrapers

Beyond the general `DocumentLoader`, the system includes specialized scrapers for specific document-heavy sources.

### ArxivScraper
Located in `gpt_researcher/scraper/arxiv/arxiv.py`, this component uses `ArxivRetriever` to fetch academic papers. It extracts the title, published date, and authors to provide context for APA-style formatting [gpt_researcher/scraper/arxiv/arxiv.py:4-28]().

### PyMuPDFScraper
Located in `gpt_researcher/scraper/pymupdf/pymupdf.py`, this scraper handles both local and remote PDF URLs. It uses a `tempfile.NamedTemporaryFile` to download remote PDFs before parsing them with `PyMuPDFLoader` [gpt_researcher/scraper/pymupdf/pymupdf.py:43-63]().

**Sources:** [gpt_researcher/scraper/arxiv/arxiv.py:4-28](), [gpt_researcher/scraper/pymupdf/pymupdf.py:8-81]()

## LangChain Integration Variants

The system provides multiple ways to interface with LangChain documents:

1.  **DocumentLoader**: The primary filesystem loader [gpt_researcher/document/document.py:16-16]().
2.  **OnlineDocumentLoader**: Handles remote document URLs [gpt_researcher/document/__init__.py:2-2]().
3.  **LangChainDocumentLoader**: A wrapper that converts existing `langchain_core.documents.Document` objects into the internal dictionary format [gpt_researcher/document/langchain_document.py:10-24]().

**Sources:** [gpt_researcher/document/langchain_document.py:10-24](), [gpt_researcher/document/__init__.py:1-5]()

## Dependency Requirements

Document processing relies on several external libraries defined in the core requirements:

| Library | Version | Purpose |
|---------|---------|---------|
| `pymupdf` | `>=1.26.0` | PDF parsing [pyproject.toml:169-169]() |
| `python-docx` | `^1.1.0` | Word document parsing [pyproject.toml:36-36]() |
| `unstructured`| `>=0.17.2` | Complex format parsing (PPTX, CSV, XLS) [pyproject.toml:201-201]() |
| `beautifulsoup4`| `>=4.12.2`| HTML parsing and cleaning [pyproject.toml:13-13]() |

**Sources:** [pyproject.toml:13-201]()

## Error Handling

The system implements nested error handling to ensure that a single corrupt file does not crash the entire loading process:

- **Loader Selection**: If an extension is unsupported, `loader_dict.get()` returns `None`, and the file is skipped [gpt_researcher/document/document.py:80-81]().
- **Inner Load Failure**: Each `loader.load()` call is wrapped in a try-except block to catch parsing errors [gpt_researcher/document/document.py:82-87]().
- **Final Validation**: If no documents are successfully loaded after all tasks finish, a `ValueError` is raised [gpt_researcher/document/document.py:58-59]().

**Sources:** [gpt_researcher/document/document.py:58-92]()

---

# Page: Cloud Storage Integration

# Cloud Storage Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [docs/docs/gpt-researcher/context/azure-storage.md](docs/docs/gpt-researcher/context/azure-storage.md)
- [docs/docs/gpt-researcher/context/local-docs.md](docs/docs/gpt-researcher/context/local-docs.md)
- [docs/docs/gpt-researcher/getting-started/getting-started-with-docker.md](docs/docs/gpt-researcher/getting-started/getting-started-with-docker.md)
- [docs/docs/gpt-researcher/gptr/claude-skill.md](docs/docs/gpt-researcher/gptr/claude-skill.md)
- [docs/sidebars.js](docs/sidebars.js)
- [gpt_researcher/actions/retriever.py](gpt_researcher/actions/retriever.py)
- [gpt_researcher/retrievers/__init__.py](gpt_researcher/retrievers/__init__.py)
- [gpt_researcher/retrievers/openalex/__init__.py](gpt_researcher/retrievers/openalex/__init__.py)
- [gpt_researcher/retrievers/openalex/openalex.py](gpt_researcher/retrievers/openalex/openalex.py)
- [gpt_researcher/retrievers/utils.py](gpt_researcher/retrievers/utils.py)
- [gpt_researcher/retrievers/xquik/__init__.py](gpt_researcher/retrievers/xquik/__init__.py)
- [gpt_researcher/retrievers/xquik/xquik.py](gpt_researcher/retrievers/xquik/xquik.py)

</details>



## Purpose and Scope

This document describes the Azure Blob Storage integration as a cloud-based document source for GPT Researcher. Azure storage provides an alternative to local file storage when documents need to be accessed from cloud infrastructure, enabling distributed deployments and centralized document management. This integration allows the research agent to treat a cloud container as its primary knowledge base for report generation.

Sources: [docs/docs/gpt-researcher/context/azure-storage.md:1-4]()

---

## Configuration Requirements

Azure Blob Storage integration requires specific environment variables and an additional Python dependency to interact with the Azure SDK.

### Environment Variables

To enable the connection, the following variables must be defined in the `.env` file at the repository root:

| Variable | Purpose | Example |
|----------|---------|---------|
| `AZURE_CONNECTION_STRING` | The full connection string for the Azure Storage account. | `DefaultEndpointsProtocol=https;AccountName=...` |
| `AZURE_CONTAINER_NAME` | The specific blob container where research documents are stored. | `research-docs` |

Sources: [docs/docs/gpt-researcher/context/azure-storage.md:5-10](), [.env.example:1-4]()

### Dependency Installation

The `azure-storage-blob` package is required and should be added to your environment:

```bash
pip install azure-storage-blob
```

Sources: [docs/docs/gpt-researcher/context/azure-storage.md:12-16]()

---

## Code Entity Space: Integration Architecture

The following diagram bridges the natural language concept of "Cloud Storage" to the specific code entities and parameters used in the `gpt-researcher` codebase.

### Entity Mapping: Request to Storage Client
```mermaid
graph TD
    subgraph "Code Entity Space"
        GPTR["GPTResearcher Class<br/>gpt_researcher/agent.py"]
        Config["Config Manager<br/>gpt_researcher/config/config.py"]
        AzureClient["Azure BlobServiceClient<br/>(External SDK)"]
    end

    subgraph "Natural Language Space"
        Input["User Request<br/>'report_source=azure'"]
        Env["Environment Variables<br/>AZURE_CONNECTION_STRING"]
    end

    Input -->|"Passed to __init__"| GPTR
    Env -->|"Parsed by"| Config
    Config -->|"Provides credentials to"| GPTR
    GPTR -->|"Instantiates"| AzureClient
    AzureClient -->|"Fetches from"| Container["Azure Container"]
```

**Implementation Detail**: When `report_source` is set to `"azure"`, the system bypasses standard web retrievers (like `TavilySearch` or `GoogleSearch`) and instead routes the data acquisition logic to the Azure storage account defined in the configuration.

Sources: [docs/docs/gpt-researcher/context/azure-storage.md:18-26](), [gpt_researcher/actions/retriever.py:149-156](), [gpt_researcher/retrievers/__init__.py:1-17]()

---

## Data Flow and Retrieval Workflow

The retrieval process transforms raw blobs into structured context for the LLM.

### Document Processing Pipeline
```mermaid
sequenceDiagram
    participant User
    participant GPTR as GPTResearcher
    participant Azure as Azure Blob Storage
    participant Loader as DocumentLoader
    participant Context as ContextManager

    User->>GPTR: conduct_research(report_source="azure")
    GPTR->>Azure: List Blobs in AZURE_CONTAINER_NAME
    Azure-->>GPTR: List of file references
    
    loop For each blob
        GPTR->>Azure: Download blob bytes
        Azure-->>GPTR: Raw data
        GPTR->>Loader: load_document(data, extension)
        Loader-->>GPTR: Extracted Text
    end

    GPTR->>Context: feed_context(extracted_texts)
    Context->>Context: Summarize & Rank
    GPTR->>User: Final Research Report
```

**Key Functions**:
- **`GPTResearcher.__init__`**: Captures the `report_source="azure"` parameter which determines the data retrieval strategy.
- **`DocumentLoader`**: Processes the downloaded bytes. It supports PDF, plain text, CSV, Excel, Markdown, PowerPoint, and Word documents.

Sources: [docs/docs/gpt-researcher/context/azure-storage.md:18-26](), [docs/docs/gpt-researcher/context/local-docs.md:5-6]()

---

## Usage Patterns

### Python API Integration
To trigger the cloud storage workflow programmatically, instantiate the researcher with the `azure` source:

```python
from gpt_researcher import GPTResearcher

# Initialize with azure source
researcher = GPTResearcher(
    query="Analysis of internal project documents",
    report_type="research_report",
    report_source="azure"
)

# Conduct research (downloads from Azure)
await researcher.conduct_research()
# Write report based on cloud context
report = await researcher.write_report()
```

Sources: [docs/docs/gpt-researcher/context/azure-storage.md:20-26]()

### Frontend Configuration
In the NextJS or Vanilla JS frontends, the Azure integration is exposed via the "Report Source" dropdown.

1. **NextJS**: Users select "Azure" in the Settings Modal, which sends a WebSocket payload with `report_source: "azure"`.
2. **Vanilla JS**: The relevant input field or dropdown updates the JSON payload sent to the `/ws` endpoint.

Sources: [docs/docs/gpt-researcher/context/local-docs.md:14-15]()

---

## Comparison of Document Sources

The system distinguishes between local, vector, and cloud sources through the `report_source` parameter.

| Parameter Value | Data Source | Key Config | Primary Use Case |
|-----------------|-------------|------------|------------------|
| `local` | Local Filesystem | `DOC_PATH` | Researching local PDFs/Docs |
| `azure` | Azure Blob Storage | `AZURE_CONNECTION_STRING` | Enterprise cloud document silos |
| `langchain_vectorstore` | Vector Database | `vector_store` object | Querying existing embeddings |
| `web` | Search Engines | `RETRIEVER` | Public internet research |

**Note**: When using `report_source="azure"`, the system specifically targets the container documents. This differs from `langchain_vectorstore` which expects a pre-populated database that implements similarity searches.

Sources: [docs/docs/gpt-researcher/context/azure-storage.md:18-26](), [docs/docs/gpt-researcher/context/local-docs.md:7-15](), [.env.example:4-4]()

---

## Supported File Formats

The Azure integration leverages the same `DocumentLoader` logic as local documents, supporting:
- **PDF**: Portable Document Format
- **Text**: `.txt`, `.md`
- **Structured**: `.csv`, `.xlsx` (Excel)
- **Office**: `.docx` (Word), `.pptx` (PowerPoint)

Sources: [docs/docs/gpt-researcher/context/local-docs.md:5-6]()

---

# Page: Model Context Protocol (MCP)

# Model Context Protocol (MCP)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/gpt-researcher/mcp-server/advanced-usage.md](docs/docs/gpt-researcher/mcp-server/advanced-usage.md)
- [docs/docs/gpt-researcher/mcp-server/claude-integration.md](docs/docs/gpt-researcher/mcp-server/claude-integration.md)
- [docs/docs/gpt-researcher/mcp-server/getting-started.md](docs/docs/gpt-researcher/mcp-server/getting-started.md)
- [docs/docs/gpt-researcher/retrievers/mcp-configs.mdx](docs/docs/gpt-researcher/retrievers/mcp-configs.mdx)
- [docs/docs/gpt-researcher/search-engines/search-engines.md](docs/docs/gpt-researcher/search-engines/search-engines.md)
- [gpt_researcher/mcp/README.md](gpt_researcher/mcp/README.md)
- [gpt_researcher/mcp/__init__.py](gpt_researcher/mcp/__init__.py)
- [gpt_researcher/mcp/client.py](gpt_researcher/mcp/client.py)
- [gpt_researcher/mcp/research.py](gpt_researcher/mcp/research.py)
- [gpt_researcher/mcp/streaming.py](gpt_researcher/mcp/streaming.py)
- [gpt_researcher/mcp/tool_selector.py](gpt_researcher/mcp/tool_selector.py)
- [gpt_researcher/retrievers/mcp/__init__.py](gpt_researcher/retrievers/mcp/__init__.py)
- [gpt_researcher/retrievers/mcp/retriever.py](gpt_researcher/retrievers/mcp/retriever.py)
- [mcp-server/README.md](mcp-server/README.md)
- [tests/test_mcp.py](tests/test_mcp.py)

</details>



## Purpose and Scope

This document describes GPT Researcher's integration with the Model Context Protocol (MCP), which enables research from specialized data sources beyond web search. MCP allows the system to connect to GitHub repositories, local filesystems, databases, and custom APIs through a standardized protocol. [docs/docs/gpt-researcher/retrievers/mcp-configs.mdx:1-3]()

GPT Researcher implements an intelligent two-stage MCP approach that automatically selects the best tools and generates contextual research, powered by LangChain's MCP adapters for seamless integration. [docs/docs/gpt-researcher/retrievers/mcp-configs.mdx:3-12]()

## Overview

MCP integration enables GPT Researcher to query specialized data sources that traditional web retrievers cannot access. The system treats MCP as a retriever alongside web search engines, but with unique characteristics:

- **Two-stage intelligent approach**: LLM analyzes queries and available MCP servers to select the most relevant tools, then executes research with dynamically generated arguments. [docs/docs/gpt-researcher/retrievers/mcp-configs.mdx:7-12]()
- **Configurable execution strategy**: Supports pure MCP or hybrid retrieval patterns. [docs/docs/gpt-researcher/retrievers/mcp-configs.mdx:43-56]()
- **Hybrid retrieval patterns**: Combines MCP results with web search (e.g., `RETRIEVER=tavily,mcp`) for comprehensive coverage. [docs/docs/gpt-researcher/retrievers/mcp-configs.mdx:48-56]()

Sources: [docs/docs/gpt-researcher/retrievers/mcp-configs.mdx:1-12](), [gpt_researcher/retrievers/mcp/retriever.py:27-42]()

## Configuration System

### MCP Configuration Parameters

MCP integration is primarily configured through the `GPTResearcher` constructor or environment variables:

| Parameter | Type | Description |
|-----------|------|-------------|
| `mcp_configs` | `List[Dict]` | List of MCP server configurations (command, args, env, etc.). [gpt_researcher/mcp/client.py:29-36]() |
| `RETRIEVER` | `str` | Env var; include `mcp` to enable. Example: `tavily,mcp`. [docs/docs/gpt-researcher/retrievers/mcp-configs.mdx:41-46]() |

### MCP Server Configuration Format

Each MCP server configuration accepts the following fields:

```python
{
    "name": "github",           # Identifier for the MCP server
    "command": "npx",          # Command to start the server (stdio)
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {"GITHUB_TOKEN": "..."}, # Environment variables for the server
    "connection_url": "...",   # URL for remote connections (WebSocket/HTTP)
    "connection_type": "stdio" # auto-detected: stdio, websocket, or http
}
```

**Local servers** require `name`, `command`, and `args`. **Remote servers** require `name` and `connection_url`. [docs/docs/gpt-researcher/retrievers/mcp-configs.mdx:86-100]()

Sources: [docs/docs/gpt-researcher/retrievers/mcp-configs.mdx:84-100](), [gpt_researcher/mcp/client.py:40-103]()

## Core Architecture and Data Flow

The MCP integration is modularized into several key classes within the `gpt_researcher.mcp` and `gpt_researcher.retrievers.mcp` modules.

### Component Association

```mermaid
graph TD
    subgraph "Natural Language Space"
        UserQuery["User Research Query"]
        SubQuery["Decomposed Sub-Query"]
    end

    subgraph "Code Entity Space (MCP Implementation)"
        Researcher["GPTResearcher Class"]
        Retriever["MCPRetriever Class"]
        ClientMgr["MCPClientManager"]
        Selector["MCPToolSelector"]
        Skill["MCPResearchSkill"]
        Adapter["MultiServerMCPClient (LangChain)"]
    end

    UserQuery --> Researcher
    Researcher --> Retriever
    Retriever --> ClientMgr
    Retriever --> Selector
    Retriever --> Skill
    
    Selector -->|"calls"| LLM_Select["_call_llm_for_tool_selection"]
    Skill -->|"calls"| LLM_Research["conduct_research_with_tools"]
    ClientMgr -->|"initializes"| Adapter
```

Sources: [gpt_researcher/retrievers/mcp/retriever.py:27-79](), [gpt_researcher/mcp/client.py:19-27](), [gpt_researcher/mcp/tool_selector.py:14-22](), [gpt_researcher/mcp/research.py:13-21]()

### Two-Stage Intelligent Research Flow

GPT Researcher does not simply dump all MCP tools into the context. It follows a structured execution pipeline:

```mermaid
sequenceDiagram
    participant R as "MCPRetriever"
    participant S as "MCPToolSelector"
    participant SK as "MCPResearchSkill"
    participant C as "MCPClientManager"
    participant M as "MultiServerMCPClient"

    R->>C: "get_or_create_client()"
    C->>M: "Initialize with mcp_configs"
    R->>C: "get_all_tools()"
    C->>M: "get_tools()"
    M-->>R: "List of available tools"
    
    Note over R,S: "Stage 1: Tool Selection"
    R->>S: "select_relevant_tools(query, all_tools)"
    S->>S: "generate_mcp_tool_selection_prompt()"
    S-->>R: "Selected Tools (max 3)"
    
    Note over R,SK: "Stage 2: Contextual Research"
    R->>SK: "conduct_research_with_tools(query, selected_tools)"
    SK->>SK: "bind_tools(selected_tools) to LLM"
    SK->>M: "ainvoke(tool_args)"
    M-->>SK: "Raw Data"
    SK->>SK: "_process_tool_result()"
    SK-->>R: "Formatted Search Results"
```

Sources: [gpt_researcher/retrievers/mcp/retriever.py:116-170](), [gpt_researcher/mcp/tool_selector.py:35-46](), [gpt_researcher/mcp/research.py:34-44](), [gpt_researcher/mcp/client.py:155-179]()

## Implementation Details

### MCPClientManager
This class manages the lifecycle of MCP connections. It converts GPT Researcher's configuration dictionaries into the format expected by `langchain-mcp-adapters`. [gpt_researcher/mcp/client.py:19-27]()
- **`convert_configs_to_langchain_format`**: Auto-detects transport types (WebSocket vs. stdio) based on `connection_url`. [gpt_researcher/mcp/client.py:40-103]()
- **`get_or_create_client`**: Ensures a singleton-like `MultiServerMCPClient` instance per research task using an `asyncio.Lock`. [gpt_researcher/mcp/client.py:105-137]()

### MCPToolSelector
Uses the `STRATEGIC_LLM` to analyze tool descriptions and select the most relevant ones for a specific query. [gpt_researcher/mcp/tool_selector.py:149-158]()
- **Fallback Mechanism**: If the LLM fails to return valid JSON or tools, `_fallback_tool_selection` uses pattern matching (e.g., searching for "search", "fetch", "query" in tool names). [gpt_researcher/mcp/tool_selector.py:163-178]()

### MCPResearchSkill
The primary execution engine for MCP tools. [gpt_researcher/mcp/research.py:13-21]()
- **`conduct_research_with_tools`**: Binds selected tools to the LLM using `llm.bind_tools()`. It handles the execution of tool calls generated by the LLM and processes their output. [gpt_researcher/mcp/research.py:34-82]()
- **`_process_tool_result`**: Normalizes diverse MCP tool outputs into a standard format (`title`, `href`, `body`) compatible with GPT Researcher's internal context management. [gpt_researcher/mcp/research.py:158-167]()

Sources: [gpt_researcher/mcp/client.py:19-137](), [gpt_researcher/mcp/tool_selector.py:14-178](), [gpt_researcher/mcp/research.py:13-167]()

## Example Servers and Use Cases

### GitHub Integration
Ideal for technical documentation and code research.
```python
mcp_configs=[{
    "name": "github",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_TOKEN")}
}]
```
Sources: [docs/docs/gpt-researcher/retrievers/mcp-configs.mdx:132-153](), [tests/test_mcp.py:53-64]()

### Hybrid Web Research (Tavily MCP)
Combines the raw speed of web search with the structured extraction of MCP.
```python
os.environ["RETRIEVER"] = "tavily,mcp"
mcp_configs=[{
    "name": "tavily",
    "command": "npx",
    "args": ["-y", "tavily-mcp@0.1.2"],
    "env": {"TAVILY_API_KEY": os.getenv("TAVILY_API_KEY")}
}]
```
Sources: [docs/docs/gpt-researcher/retrievers/mcp-configs.mdx:103-130](), [tests/test_mcp.py:40-51]()

## Claude Desktop Integration

GPT Researcher can also act as an MCP server for other clients like Claude Desktop. This allows Claude to use GPT Researcher as a "tool" for deep research. [docs/docs/gpt-researcher/mcp-server/claude-integration.md:5-7]()

**Configuration in `claude_desktop_config.json`:**
```json
{
  "mcpServers": {
    "gpt-researcher": {
      "command": "/path/to/python",
      "args": ["/path/to/gptr-mcp/server.py"]
    }
  }
}
```
Sources: [docs/docs/gpt-researcher/mcp-server/claude-integration.md:52-65](), [mcp-server/README.md:7-19]()

## Troubleshooting

1. **Missing Dependencies**: Ensure `langchain-mcp-adapters` is installed. The system logs a warning if it's missing. [gpt_researcher/retrievers/mcp/__init__.py:11-26]()
2. **Connection Errors**: For `stdio` servers, verify the absolute path to the command (e.g., `python` vs `/usr/bin/python3`). [docs/docs/gpt-researcher/mcp-server/claude-integration.md:110-114]()
3. **Empty Results**: If the LLM makes tool calls but no context is gathered, check `MCPResearchSkill._process_tool_result` logs to see if the tool output format is recognized. [gpt_researcher/mcp/research.py:130-135]()

Sources: [gpt_researcher/retrievers/mcp/retriever.py:127-131](), [gpt_researcher/mcp/client.py:116-118]()

---

# Page: Vector Store Integration

# Vector Store Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/requirements.txt](backend/requirements.txt)
- [docs/docs/examples/examples.ipynb](docs/docs/examples/examples.ipynb)
- [docs/docs/gpt-researcher/context/data-ingestion.md](docs/docs/gpt-researcher/context/data-ingestion.md)
- [docs/docs/gpt-researcher/context/vector-stores.md](docs/docs/gpt-researcher/context/vector-stores.md)
- [gpt_researcher/__init__.py](gpt_researcher/__init__.py)
- [gpt_researcher/actions/__init__.py](gpt_researcher/actions/__init__.py)
- [gpt_researcher/context/__init__.py](gpt_researcher/context/__init__.py)
- [gpt_researcher/context/compression.py](gpt_researcher/context/compression.py)
- [gpt_researcher/context/retriever.py](gpt_researcher/context/retriever.py)
- [gpt_researcher/vector_store/__init__.py](gpt_researcher/vector_store/__init__.py)
- [gpt_researcher/vector_store/vector_store.py](gpt_researcher/vector_store/vector_store.py)
- [tests/docs/doc.pdf](tests/docs/doc.pdf)
- [tests/vector-store.py](tests/vector-store.py)

</details>



## Purpose and Scope

This document describes how GPT Researcher integrates with LangChain vector stores for document retrieval and storage. Vector stores enable GPT Researcher to query existing knowledge bases or persist scraped web content for future research tasks. This page covers the `VectorStoreWrapper` abstraction, the `VectorstoreCompressor` retrieval system, data ingestion patterns, and supported vector store implementations.

For information about other data sources, see:
- Local document loading: [7.3]()
- Web scraping: [7.2]()
- Cloud storage: [7.4]()
- Report source modes: [7.7]()

---

## Architecture Overview

GPT Researcher integrates with LangChain vector stores through the `VectorStoreWrapper` class, supporting two modes: querying existing vector stores for research (read mode) and persisting scraped content (write mode).

### Vector Store Integration Architecture

```mermaid
graph TB
    subgraph "GPTResearcher_Initialization"
        Init["GPTResearcher.__init__()<br/>vector_store parameter"]
        WrapInit["self.vector_store =<br/>VectorStoreWrapper(vector_store)"]
    end
    
    subgraph "Read_Mode_report_source_langchain_vectorstore"
        RConductor["ResearchConductor<br/>conduct_research()"]
        GetVS["_get_context_by_vectorstore()"]
        CMgr["ContextManager<br/>get_similar_content_by_query_with_vectorstore()"]
        VSComp["VectorstoreCompressor<br/>async_get_context()"]
    end
    
    subgraph "Write_Mode_report_source_web_plus_vector_store"
        RConductorW["ResearchConductor<br/>conduct_research()"]
        Scrape["_get_context_by_web_search()"]
        Load["vector_store.load(document_data)"]
    end
    
    subgraph "VectorStoreWrapper_Entity"
        LoadMethod["load(documents)<br/>Convert + chunk + add"]
        SearchMethod["asimilarity_search(query, k, filter)"]
        CreateLC["_create_langchain_documents()"]
        Split["_split_documents()<br/>RecursiveCharacterTextSplitter"]
    end
    
    subgraph "LangChain_VectorStore_Entity"
        AddDocs["add_documents(documents)"]
        ASearch["asimilarity_search(query, k, filter)"]
    end
    
    Init --> WrapInit
    
    RConductor --> GetVS
    GetVS --> CMgr
    CMgr --> VSComp
    VSComp --> SearchMethod
    
    RConductorW --> Scrape
    Scrape --> Load
    Load --> LoadMethod
    LoadMethod --> CreateLC
    CreateLC --> Split
    Split --> AddDocs
    
    SearchMethod --> ASearch
```

**Sources:** [gpt_researcher/agent.py:152](), [gpt_researcher/vector_store/vector_store.py:10-44](), [gpt_researcher/context/compression.py:36-82]()

### Code Flow for Both Modes

| Mode | Trigger | Code Path | Key Methods |
|------|---------|-----------|-------------|
| **Read** | `report_source="langchain_vectorstore"` | `ResearchConductor._get_context_by_vectorstore()` → `ContextManager.get_similar_content_by_query_with_vectorstore()` → `VectorstoreCompressor.async_get_context()` → `VectorStoreWrapper.asimilarity_search()` | [gpt_researcher/context/compression.py:71-82](), [gpt_researcher/vector_store/vector_store.py:40-43]() |
| **Write** | `report_source="web"` + `vector_store` | `ResearchConductor._get_context_by_web_search()` → `vector_store.load(document_data)` → `VectorStoreWrapper.load()` → `_create_langchain_documents()` → `_split_documents()` | [gpt_researcher/vector_store/vector_store.py:17-24]() |

**Sources:** [gpt_researcher/agent.py:51-152](), [gpt_researcher/vector_store/vector_store.py:10-44]()

---

## VectorStoreWrapper Class

The `VectorStoreWrapper` class provides an adapter layer between GPT Researcher's document format and LangChain's vector store interface. It handles document conversion, chunking, and similarity search operations.

### Class Structure

**Location:** [gpt_researcher/vector_store/vector_store.py:10-44]()

```mermaid
classDiagram
    class VectorStoreWrapper {
        +VectorStore vector_store
        +__init__(vector_store)
        +load(documents)
        +asimilarity_search(query, k, filter)
        -_create_langchain_documents(data)
        -_split_documents(documents, chunk_size, chunk_overlap)
    }
    
    class VectorStore {
        <<LangChain Interface>>
        +add_documents(documents)
        +asimilarity_search(query, k, filter)
    }
    
    class Document {
        <<LangChain>>
        +str page_content
        +dict metadata
    }
    
    VectorStoreWrapper --> VectorStore
    VectorStoreWrapper --> Document
```

### Key Methods

| Method | Signature | Implementation |
|--------|-----------|----------------|
| `__init__(vector_store)` | Initialize with LangChain `VectorStore` | Stores reference to `self.vector_store` [gpt_researcher/vector_store/vector_store.py:14-15]() |
| `load(documents)` | `documents: List[Dict[str, str]]` | Calls `_create_langchain_documents()` → `_split_documents()` → `vector_store.add_documents()` [gpt_researcher/vector_store/vector_store.py:17-24]() |
| `asimilarity_search(query, k, filter)` | `query: str, k: int, filter: Optional[dict]` → `List[Document]` | Async wrapper for `vector_store.asimilarity_search()` [gpt_researcher/vector_store/vector_store.py:40-43]() |
| `_create_langchain_documents(data)` | `data: List[Dict]` → `List[Document]` | Maps `{url, raw_content}` → `Document(page_content, metadata={"source": url})` [gpt_researcher/vector_store/vector_store.py:26-28]() |
| `_split_documents(documents)` | `documents: List[Document]` → `List[Document]` | Uses `RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)` [gpt_researcher/vector_store/vector_store.py:30-38]() |

**Sources:** [gpt_researcher/vector_store/vector_store.py:14-43]()

### Document Conversion Pipeline

```mermaid
graph LR
    Input["GPT_Researcher_Doc<br/>{url, raw_content}"]
    CreateLC["_create_langchain_documents()"]
    LCDoc["Document(page_content=item['raw_content'],<br/>metadata={'source': item['url']})"]
    SplitMethod["_split_documents()"]
    Splitter["RecursiveCharacterTextSplitter<br/>chunk_size=1000<br/>chunk_overlap=200"]
    Chunks["List[Document] chunks"]
    AddDocs["vector_store.add_documents(chunks)"]
    
    Input --> CreateLC
    CreateLC --> LCDoc
    LCDoc --> SplitMethod
    SplitMethod --> Splitter
    Splitter --> Chunks
    Chunks --> AddDocs
```

**Implementation:**
- `_create_langchain_documents()`: [gpt_researcher/vector_store/vector_store.py:26-28]() - List comprehension creating `Document` objects.
- `_split_documents()`: [gpt_researcher/vector_store/vector_store.py:30-38]() - Instantiates `RecursiveCharacterTextSplitter` with fixed parameters.
- `load()` orchestration: [gpt_researcher/vector_store/vector_store.py:17-24]()

**Sources:** [gpt_researcher/vector_store/vector_store.py:17-38]()

---

## VectorstoreCompressor for Context Retrieval

The `VectorstoreCompressor` class retrieves relevant context from vector stores using similarity search. It is used when `report_source="langchain_vectorstore"` is specified.

### Class Structure

**Location:** [gpt_researcher/context/compression.py:36-82]()

| Attribute | Type | Description |
|-----------|------|-------------|
| `vector_store` | `VectorStoreWrapper` | Wrapped LangChain vector store [gpt_researcher/context/compression.py:65]() |
| `max_results` | `int` | Maximum documents to return (default: 7) [gpt_researcher/context/compression.py:66]() |
| `filter` | `Optional[dict]` | Optional metadata filter [gpt_researcher/context/compression.py:67]() |
| `prompt_family` | `PromptFamily` | Format output for LLM consumption [gpt_researcher/context/compression.py:69]() |

### Retrieval Flow

```mermaid
sequenceDiagram
    participant RC as ResearchConductor<br/>_get_context_by_vectorstore()
    participant CM as ContextManager<br/>get_similar_content_by_query_with_vectorstore()
    participant VSC as VectorstoreCompressor<br/>async_get_context()
    participant VSW as VectorStoreWrapper<br/>asimilarity_search()
    participant VS as LangChain_VectorStore
    
    RC->>CM: query, filter
    CM->>VSC: query, max_results=8
    VSC->>VSW: query, k=max_results, filter
    VSW->>VS: asimilarity_search(query, k, filter)
    VS-->>VSW: List[Document]
    VSW-->>VSC: List[Document]
    VSC->>VSC: prompt_family.pretty_print_docs(results)
    VSC-->>CM: Formatted string
    CM-->>RC: Context string
```

**Implementation:**
- `VectorstoreCompressor.async_get_context()`: [gpt_researcher/context/compression.py:71-82]() - Calls `vector_store.asimilarity_search()` and formats results.
- `ContextManager.get_similar_content_by_query_with_vectorstore()`: [gpt_researcher/skills/context_manager.py:65-86]() - Instantiates `VectorstoreCompressor` with `max_results=8`.

**Sources:** [gpt_researcher/context/compression.py:36-82](), [gpt_researcher/skills/context_manager.py:65-86]()

---

## Using Vector Stores with GPTResearcher

### Pattern 1: Querying Existing Vector Stores

Set `report_source="langchain_vectorstore"` to trigger the read mode code path.

**Initialization:** [gpt_researcher/agent.py:152]()

```python
# GPTResearcher.__init__ wraps the vector store
self.vector_store = VectorStoreWrapper(vector_store) if vector_store else None
```

**Example:** [docs/docs/gpt-researcher/context/vector-stores.md:12-86]()

```python
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from gpt_researcher import GPTResearcher

# Pre-populated FAISS vector store
vector_store = FAISS.from_documents(documents, OpenAIEmbeddings())

# Read mode: query the vector store
researcher = GPTResearcher(
    query="Summarize key findings",
    report_source="langchain_vectorstore",  # Triggers _get_context_by_vectorstore()
    vector_store=vector_store,  # Wrapped in VectorStoreWrapper
)

await researcher.conduct_research()
report = await researcher.write_report()
```

**Sources:** [gpt_researcher/agent.py:152](), [docs/docs/gpt-researcher/context/vector-stores.md:12-86]()

### Pattern 2: Storing Scraped Data

Set `report_source="web"` (or `"local"`, `"hybrid"`, `"azure"`) with a `vector_store` parameter to trigger write mode.

**Example:** [docs/docs/gpt-researcher/context/vector-stores.md:126-156]()

```python
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from gpt_researcher import GPTResearcher

# Empty vector store for write mode
vector_store = InMemoryVectorStore(embedding=OpenAIEmbeddings())

# Write mode: persist scraped content
researcher = GPTResearcher(
    query="The best LLM",
    report_source="web",  # Triggers _get_context_by_web_search()
    vector_store=vector_store,  # Data written via load()
)

await researcher.conduct_research()
# Scraped content now stored via vector_store.load()

# Query the populated store
related_contexts = await vector_store.asimilarity_search("GPT-4", k=5)
```

**Sources:** [docs/docs/gpt-researcher/context/vector-stores.md:126-156]()

### Report Source Behavior Matrix

| `report_source` | `vector_store` Parameter | Code Path | Behavior |
|-----------------|--------------------------|-----------|----------|
| `"langchain_vectorstore"` | Required | `_get_context_by_vectorstore()` | **Read**: Queries via `VectorstoreCompressor` [docs/docs/gpt-researcher/context/vector-stores.md:9-10]() |
| `"web"` | Optional | `_get_context_by_web_search()` + `load()` | **Write**: Stores scraped content if `vector_store` provided [docs/docs/gpt-researcher/context/vector-stores.md:128-129]() |

**Sources:** [docs/docs/gpt-researcher/context/vector-stores.md:9-129]()

---

## Supported Vector Store Types

GPT Researcher works with any LangChain vector store that implements the `asimilarity_search` method [docs/docs/gpt-researcher/context/vector-stores.md:7-8]().

### FAISS (Facebook AI Similarity Search)

**In-memory vector store** for fast similarity search.

```python
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

vector_store = FAISS.from_documents(documents, OpenAIEmbeddings())
```

**Source:** [docs/docs/gpt-researcher/context/vector-stores.md:11-86]()

### PGVector (PostgreSQL)

**Persistent vector store** backed by PostgreSQL with pgvector extension.

```python
from langchain_postgres.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings

CONNECTION_STRING = 'postgresql://user:pass@localhost:5432/db'

vector_store = PGVector.from_existing_index(
    use_jsonb=True,
    embedding=OpenAIEmbeddings(),
    collection_name='my_collection',
    connection=CONNECTION_STRING,
    async_mode=True,
)
```

**Source:** [docs/docs/gpt-researcher/context/vector-stores.md:89-125]()

### InMemoryVectorStore

**Lightweight in-memory store** used for testing and temporary storage.

```python
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings

vector_store = InMemoryVectorStore(embedding=OpenAIEmbeddings())
```

**Source:** [tests/vector-store.py:8]()

---

## Data Ingestion Patterns

For large-scale or custom data ingestion, GPT Researcher supports standalone data ingestion processes that populate vector stores before research execution.

### Three-Step Ingestion Process

```mermaid
graph TB
    subgraph "Step_1_Create_LangChain_Documents"
        RawData["Raw Data Files/APIs/DB"]
        CreateDoc["Document(page_content=text,<br/>metadata={'source': url, 'title': title})"]
        LCDocs["List[Document]"]
    end
    
    subgraph "Step_2_Chunk_and_Insert"
        Splitter["RecursiveCharacterTextSplitter<br/>split_text() or split_documents()"]
        Chunks["Document chunks"]
        AddDocs["vector_store.add_documents(chunks,<br/>ids=[...])"]
    end
    
    subgraph "Step_3_Query_with_GPTResearcher"
        InitR["GPTResearcher(report_source=<br/>'langchain_vectorstore',<br/>vector_store=vs)"]
        ConductR["conduct_research()<br/>_get_context_by_vectorstore()"]
        WriteR["write_report()"]
    end
    
    RawData --> CreateDoc
    CreateDoc --> LCDocs
    LCDocs --> Splitter
    Splitter --> Chunks
    Chunks --> AddDocs
    AddDocs -.->|Pre-populated| InitR
    InitR --> ConductR
    ConductR --> WriteR
```

**Sources:** [docs/docs/gpt-researcher/context/data-ingestion.md:16-27]()

### Step 1: Create LangChain Documents

**Required metadata fields for GPT Researcher:**
- `source`: URL or file path (used in citations).
- `title`: Document title.

**Example transformation:** [docs/docs/gpt-researcher/context/data-ingestion.md:46-91]()

```python
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=30)
documents = []

for file_content in source_data:
    chunks = splitter.split_text(file_content)
    
    for chunk in chunks:
        metadata = {
            "id": f"{timestamp}_{uuid4()}",
            "source": file_path,
            "title": file_name,
            "extension": file_extension
        }
        document = Document(page_content=chunk, metadata=metadata)
        documents.append(document)
```

**Sources:** [docs/docs/gpt-researcher/context/data-ingestion.md:46-91]()

### Step 2: Insert into Vector Store

Batch insert documents to avoid rate limits: [docs/docs/gpt-researcher/context/data-ingestion.md:95-125]()

```python
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings

vector_store = PGVector(
    embeddings=OpenAIEmbeddings(),
    collection_name="my_docs",
    connection=connection_string,
    use_jsonb=True
)

# Insert in batches of 100 to avoid rate limits
for i in range(0, len(documents), 100):
    chunk = documents[i:i+100]
    vector_store.add_documents(
        chunk, 
        ids=[doc.metadata["id"] for doc in chunk]
    )
```

**Source:** [docs/docs/gpt-researcher/context/data-ingestion.md:95-125]()

---

## Configuration and Best Practices

### Similarity Threshold Configuration

The `ContextCompressor` class supports a similarity threshold environment variable for filtering raw documents:

```bash
SIMILARITY_THRESHOLD=0.35  # Default value
```

**Usage:** [gpt_researcher/context/compression.py:119]() - `self.similarity_threshold = os.environ.get("SIMILARITY_THRESHOLD", 0.35)`

**Sources:** [gpt_researcher/context/compression.py:119]()

### Best Practices

| Practice | Rationale |
|----------|-----------|
| **Include `source` and `title` metadata** | Required for citations and display in reports [docs/docs/gpt-researcher/context/data-ingestion.md:42]() |
| **Use async-compatible vector stores** | GPT Researcher uses `asimilarity_search` asynchronously [gpt_researcher/vector_store/vector_store.py:40-43]() |
| **Batch document insertion** | Avoid rate limits on embedding APIs [docs/docs/gpt-researcher/context/data-ingestion.md:120-125]() |
| **Set `report_source="langchain_vectorstore"`** | Essential for querying pre-populated stores without contamination [docs/docs/gpt-researcher/context/vector-stores.md:9-10]() |

**Sources:** [docs/docs/gpt-researcher/context/data-ingestion.md:1-154](), [docs/docs/gpt-researcher/context/vector-stores.md:1-156]()

---

# Page: Report Source Modes

# Report Source Modes

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/requirements.txt](backend/requirements.txt)
- [docs/docs/examples/examples.ipynb](docs/docs/examples/examples.ipynb)
- [docs/docs/gpt-researcher/context/azure-storage.md](docs/docs/gpt-researcher/context/azure-storage.md)
- [docs/docs/gpt-researcher/context/data-ingestion.md](docs/docs/gpt-researcher/context/data-ingestion.md)
- [docs/docs/gpt-researcher/context/local-docs.md](docs/docs/gpt-researcher/context/local-docs.md)
- [docs/docs/gpt-researcher/context/vector-stores.md](docs/docs/gpt-researcher/context/vector-stores.md)
- [docs/docs/gpt-researcher/getting-started/getting-started-with-docker.md](docs/docs/gpt-researcher/getting-started/getting-started-with-docker.md)
- [docs/docs/gpt-researcher/gptr/claude-skill.md](docs/docs/gpt-researcher/gptr/claude-skill.md)
- [docs/docs/gpt-researcher/gptr/config.md](docs/docs/gpt-researcher/gptr/config.md)
- [docs/sidebars.js](docs/sidebars.js)
- [gpt_researcher/actions/query_processing.py](gpt_researcher/actions/query_processing.py)
- [gpt_researcher/config/variables/base.py](gpt_researcher/config/variables/base.py)
- [gpt_researcher/config/variables/default.py](gpt_researcher/config/variables/default.py)
- [tests/docs/doc.pdf](tests/docs/doc.pdf)
- [tests/vector-store.py](tests/vector-store.py)

</details>



## Purpose and Scope

This document describes the `REPORT_SOURCE` configuration parameter in GPT Researcher, which determines the data origin for the research agent. The system supports six distinct source modes: web search, local documents, hybrid (web + local), Azure Blob Storage, LangChain documents, and LangChain vector stores. This parameter dictates how the `ResearchConductor` gathers context and whether it triggers external search queries or internal document processing.

## Available Report Source Modes

The system defaults to `web` research, but can be configured to use local or cloud-based document stores.

| Mode | Configuration Value | Data Source | Use Case |
|------|---------------------|-------------|----------|
| **Web** | `"web"` | Web search APIs (Tavily, Google, etc.) | Default mode for real-time online research. |
| **Local** | `"local"` | Local file system documents | Research from private/proprietary documents in `DOC_PATH`. |
| **Hybrid** | `"hybrid"` | Local documents + Web search | Combine internal knowledge with real-time external data. |
| **Azure** | `"azure"` | Azure Blob Storage containers | Enterprise document storage integration. |
| **LangChain Documents** | `"langchain_documents"` | Pre-loaded LangChain `Document` objects | Custom document preprocessing or external ingestion pipelines. |
| **LangChain VectorStore** | `"langchain_vectorstore"` | Existing LangChain vector store | Research directly from pre-indexed document collections. |

Sources: [gpt_researcher/config/variables/default.py:29-30](), [gpt_researcher/config/variables/base.py:31-32](), [docs/docs/gpt-researcher/gptr/config.md:96-97]()

## Report Source Flow Architecture

The following diagram bridges the **Natural Language Space** (User Intent) to the **Code Entity Space** (Classes and Variables).

```mermaid
graph TB
    subgraph "Natural Language Space"
        UserIntent["User wants to research 'Local Documents'"]
    end

    subgraph "Code Entity Space"
        direction TB
        ConfigClass["Config Class<br/>gpt_researcher/config/config.py"]
        AgentClass["GPTResearcher Class<br/>gpt_researcher/agent.py"]
        DefaultVars["DEFAULT_CONFIG<br/>gpt_researcher/config/variables/default.py"]
        
        DocLoader["DocumentLoader<br/>gpt_researcher/utils/doc_loader.py"]
        VectorStore["VectorStoreWrapper<br/>gpt_researcher/utils/vector_store.py"]
        QueryProc["query_processing.py<br/>gpt_researcher/actions/query_processing.py"]
    end

    UserIntent -->|Sets report_source='local'| AgentClass
    AgentClass -->|Initializes| ConfigClass
    ConfigClass -->|Loads Defaults| DefaultVars
    
    AgentClass -->|Calls conduct_research()| SourceSwitch{"REPORT_SOURCE?"}
    
    SourceSwitch -->|'web'| QueryProc
    SourceSwitch -->|'local'| DocLoader
    SourceSwitch -->|'langchain_vectorstore'| VectorStore
    
    QueryProc -->|get_search_results| WebAPI["Search Retrievers"]
```

Sources: [gpt_researcher/config/variables/default.py:29-30](), [gpt_researcher/config/variables/base.py:31-32](), [gpt_researcher/actions/query_processing.py:12-35]()

## Configuration Methods

### Constructor Parameter
When instantiating the `GPTResearcher` class, the `report_source` argument explicitly defines the research origin.

```python
from gpt_researcher import GPTResearcher

researcher = GPTResearcher(
    query="How does the stubbornness of the Collison brothers differ from mere obstinacy?",
    report_source="langchain_vectorstore",
    vector_store=my_faiss_index  # Required for vectorstore mode
)
```

Sources: [docs/docs/gpt-researcher/context/vector-stores.md:75-81](), [docs/docs/gpt-researcher/context/local-docs.md:13-15]()

### Configuration Files and Environment
The `REPORT_SOURCE` can be set globally in a `config.json` file or via environment variables.

```json
{
  "REPORT_SOURCE": "local",
  "DOC_PATH": "./my-docs"
}
```

Sources: [gpt_researcher/config/variables/default.py:29-30](), [docs/docs/gpt-researcher/gptr/config.md:19-37]()

## Detailed Mode Implementations

### Web Mode (`"web"`)
The default mode. It uses the `RETRIEVER` (e.g., `tavily`, `duckduckgo`) to find information online.
- **Sub-query Generation**: Generates multiple search queries via `generate_sub_queries` to ensure breadth [gpt_researcher/actions/query_processing.py:37-62]().
- **Data Flow**: `get_search_results` calls the retriever's `.search()` method [gpt_researcher/actions/query_processing.py:12-35]().

### Local Mode (`"local"`)
Uses documents stored on the local filesystem.
- **Path**: Configured via `DOC_PATH` (defaults to `./my-docs`) [gpt_researcher/config/variables/default.py:30]().
- **Formats**: Supports PDF, TXT, CSV, Excel, MD, PPTX, and DOCX [docs/docs/gpt-researcher/context/local-docs.md:5-6]().

### LangChain VectorStore Mode (`"langchain_vectorstore"`)
Integrates with pre-populated vector databases.
- **Requirement**: Must provide a `vector_store` object that implements `asimilarity_search` [docs/docs/gpt-researcher/context/vector-stores.md:6-7]().
- **Optimization**: Setting `report_source="langchain_vectorstore"` prevents the agent from attempting to scrape additional web data, which avoids "contaminating" the existing vector database [docs/docs/gpt-researcher/context/vector-stores.md:9-10]().

## Data Ingestion Flow

The following diagram illustrates the transformation of raw sources into the research context used by the LLM.

```mermaid
graph LR
    subgraph "Raw Sources"
        R_Web["Web URLs"]
        R_Files["Local Files (.pdf, .docx)"]
        R_Azure["Azure Blobs"]
    end

    subgraph "Processing (Code Entities)"
        direction TB
        P_Scraper["Scraper (bs/newspaper)<br/>gpt_researcher/scraper"]
        P_Loader["DocumentLoader<br/>gpt_researcher/utils/doc_loader.py"]
        P_Splitter["RecursiveCharacterTextSplitter<br/>langchain_text_splitters"]
    end

    subgraph "Storage/Context"
        V_Store["LangChain VectorStore<br/>(FAISS, PGVector, etc.)"]
        C_Manager["ContextManager"]
    end

    R_Web --> P_Scraper
    R_Files --> P_Loader
    R_Azure --> P_Loader
    
    P_Scraper --> P_Splitter
    P_Loader --> P_Splitter
    P_Splitter --> V_Store
    V_Store --> C_Manager
```

Sources: [docs/docs/gpt-researcher/context/data-ingestion.md:15-28](), [docs/docs/gpt-researcher/context/vector-stores.md:61-65](), [gpt_researcher/config/variables/default.py:24-25]()

## Precedence and Defaults
The configuration system follows a strict hierarchy to resolve the active `REPORT_SOURCE`:
1. **Direct Argument**: Passed to `GPTResearcher(report_source=...)`.
2. **Custom Config**: Values in `config.json` provided via `--config_path` [docs/docs/gpt-researcher/gptr/config.md:41-44]().
3. **Environment Variables**: System-level `REPORT_SOURCE` [docs/docs/gpt-researcher/context/local-docs.md:9-11]().
4. **Hardcoded Default**: `"web"` as defined in `default.py` [gpt_researcher/config/variables/default.py:29]().

Sources: [gpt_researcher/config/variables/default.py:29-30](), [docs/docs/gpt-researcher/gptr/config.md:16-18]()

---

# Page: Domain Filtering

# Domain Filtering

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/gpt-researcher/context/filtering-by-domain.md](docs/docs/gpt-researcher/context/filtering-by-domain.md)
- [docs/docs/gpt-researcher/frontend/embed-script.md](docs/docs/gpt-researcher/frontend/embed-script.md)
- [docs/docs/gpt-researcher/gptr/querying-the-backend.md](docs/docs/gpt-researcher/gptr/querying-the-backend.md)
- [frontend/nextjs/public/embed.js](frontend/nextjs/public/embed.js)
- [frontend/nextjs/src/utils/imageTransformPlugin.js](frontend/nextjs/src/utils/imageTransformPlugin.js)

</details>



## Purpose and Scope

This document explains the domain filtering feature in GPT Researcher, which allows users to restrict web search results to specific domains. Domain filtering helps focus research on trusted or specialized sources, improving result quality and relevance.

For information about configuring search retrievers generally, see [Retriever System](#7.1). For details on report source modes, see [Report Source Modes](#7.7). For web scraping implementation details, see [Web Scraping System](#7.2).

---

## Overview

Domain filtering restricts web search results to user-specified domains during the research process. This feature is currently supported for **Tavily** and **Google Search** retrievers. When enabled, the research system will only retrieve and scrape content from the specified domains, ensuring focused and domain-specific research outcomes.

**Key Characteristics:**
- Supported retrievers: Tavily, Google Search [docs/docs/gpt-researcher/context/filtering-by-domain.md:3-5]()
- Available across all interfaces: pip package, NextJS frontend, Vanilla JS frontend, URL parameters [docs/docs/gpt-researcher/context/filtering-by-domain.md:22-62]()
- Accepts single or multiple domains
- Filters applied before web scraping begins

Sources: [docs/docs/gpt-researcher/context/filtering-by-domain.md:1-5]()

---

## Retriever Configuration Requirements

Domain filtering requires proper retriever configuration. The system supports two primary retrievers with domain filtering capabilities.

### Tavily Retriever Setup

To use domain filtering with Tavily, configure the following environment variables:

```bash
RETRIEVER=tavily
TAVILY_API_KEY=your_tavily_api_key
```

### Google Search Retriever Setup

To use domain filtering with Google Search, configure these environment variables:

```bash
RETRIEVER=google
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CX_KEY=your_google_custom_search_engine_id
```

**Note:** The `RETRIEVER` environment variable determines which search provider handles domain filtering. The domains parameter is passed through to the configured retriever during search operations.

Sources: [docs/docs/gpt-researcher/context/filtering-by-domain.md:7-20]()

---

## Domain Filtering Across Interfaces

The domain filtering feature is accessible through multiple interfaces, each with its own syntax and configuration method.

### Domain Filtering Flow Diagram

```mermaid
flowchart TD
    User["User Input<br/>(Query + Domains)"]
    
    User --> Interface{Interface Type?}
    
    Interface -->|Pip Package| PipCode["GPTResearcher Constructor<br/>domains=['forbes.com', 'techcrunch.com']"]
    Interface -->|NextJS Frontend| NextJSUI["Settings Modal<br/>Domain Input Field"]
    Interface -->|Vanilla JS| VanillaUI["Domain Input Field<br/>in Main Form"]
    Interface -->|URL Parameter| URLParam["?domains=wired.com,forbes.com"]
    
    PipCode --> BackendAPI["FastAPI Backend<br/>/ws WebSocket Endpoint"]
    NextJSUI --> BackendAPI
    VanillaUI --> BackendAPI
    URLParam --> NextJSUI
    
    BackendAPI --> ResearcherInit["GPTResearcher.__init__()<br/>domains parameter"]
    
    ResearcherInit --> RetrieverCheck{Retriever Type?}
    
    RetrieverCheck -->|Tavily| TavilySearch["TavilySearch.search()<br/>include_domains param"]
    RetrieverCheck -->|Google| GoogleSearch["GoogleSearch.search()<br/>domain filtering"]
    RetrieverCheck -->|Other| NoFilter["No Domain Filtering<br/>Standard Search"]
    
    TavilySearch --> FilteredResults["Filtered Search Results"]
    GoogleSearch --> FilteredResults
    NoFilter --> AllResults["All Search Results"]
    
    FilteredResults --> Scraper["BrowserManager<br/>URL Scraping"]
    AllResults --> Scraper
    
    Scraper --> Context["Context Collection"]
    Context --> Report["Report Generation"]
```

Sources: [docs/docs/gpt-researcher/context/filtering-by-domain.md:22-62]()

---

## Pip Package Implementation

When using GPT Researcher as a pip package, domain filtering is configured through the `domains` parameter in the `GPTResearcher` constructor.

### Basic Usage

```python
from gpt_researcher import GPTResearcher

report = GPTResearcher(
    query="Latest AI Startups",
    report_type="research_report",
    report_source="web",
    domains=["forbes.com", "techcrunch.com"]
)
```

### Parameter Specification

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | `str` | Yes | Research query |
| `report_type` | `str` | Yes | Type of report to generate |
| `report_source` | `str` | Yes | Must be `"web"` for domain filtering [docs/docs/gpt-researcher/context/filtering-by-domain.md:30-31]() |
| `domains` | `List[str]` | No | List of domains to filter by [docs/docs/gpt-researcher/context/filtering-by-domain.md:31-32]() |

**Important:** The `report_source` must be set to `"web"` for domain filtering to apply. Other report sources (local, azure, hybrid) retrieve content from non-web sources where domain filtering is not applicable. [docs/docs/gpt-researcher/context/filtering-by-domain.md:30-31]()

Sources: [docs/docs/gpt-researcher/context/filtering-by-domain.md:22-33]()

---

## NextJS Frontend Implementation

The NextJS frontend provides a graphical interface for domain filtering through the Settings Modal.

### Settings Modal Configuration

Users access domain filtering through the Settings Modal UI component:

1. Open the Settings Modal
2. Locate the "Domain Filtering" section
3. Enter comma-separated domain names (e.g., `forbes.com, techcrunch.com`) [docs/docs/gpt-researcher/context/filtering-by-domain.md:37-39]()
4. Settings persist in localStorage for subsequent research sessions

### Frontend State Management

The NextJS frontend stores domain configuration in the browser's localStorage, ensuring persistence across sessions. When initiating research, the frontend passes the domains array to the backend via WebSocket message.

**WebSocket Message Structure:**
```javascript
{
  task: "research query",
  report_type: "research_report",
  report_source: "web",
  domains: ["forbes.com", "techcrunch.com"],
  // ... other parameters
}
```

Sources: [docs/docs/gpt-researcher/context/filtering-by-domain.md:35-39](), [docs/docs/gpt-researcher/gptr/querying-the-backend.md:64-71]()

---

## Vanilla JS Frontend Implementation

The Vanilla JS frontend provides domain filtering through a dedicated input field in the main research form.

### Input Field Configuration

Users enter domains directly in the research form:
- Input field accepts comma-separated domain list [docs/docs/gpt-researcher/context/filtering-by-domain.md:43-45]()
- Domains are included in the WebSocket payload when research starts
- No persistence between sessions (unlike NextJS frontend)

### Form Submission Flow

When the user submits the research form, the Vanilla JS frontend constructs a WebSocket message containing the domains array and sends it to the FastAPI backend at `ws://localhost:8000/ws`. [docs/docs/gpt-researcher/gptr/querying-the-backend.md:22-25]()

Sources: [docs/docs/gpt-researcher/context/filtering-by-domain.md:41-45](), [docs/docs/gpt-researcher/gptr/querying-the-backend.md:58-89]()

---

## URL Parameter Filtering

Domain filtering can be pre-configured via URL query parameters, enabling shareable research configurations and proof-of-concept demonstrations.

### URL Parameter Syntax

**Single Domain:**
```
https://app.gptr.dev/?domains=wikipedia.org
```

**Multiple Domains (comma-separated):**
```
https://app.gptr.dev/?domains=wired.com,forbes.com,wikipedia.org
```

### Use Cases

1. **Proof of Concept Demonstrations:** Share URLs with stakeholders showcasing domain-specific research [docs/docs/gpt-researcher/context/filtering-by-domain.md:49-51]()
2. **Bookmarked Configurations:** Create bookmarks for frequently-used domain sets
3. **Embedded Applications:** Configure domain filters in embedded instances

### URL Processing Flow

```mermaid
flowchart LR
    URL["URL with ?domains=<br/>wired.com,forbes.com"]
    
    URL --> Parser["NextJS URL Parameter Parser"]
    Parser --> LocalStorage["Store in localStorage"]
    LocalStorage --> SettingsModal["Populate Settings Modal"]
    SettingsModal --> Research["Initiate Research with Domains"]
```

**Note:** The URL parameter feature is implemented in the NextJS frontend. When the application loads with a `domains` query parameter, it automatically populates the domain filter settings. [docs/docs/gpt-researcher/context/filtering-by-domain.md:55-61]()

Sources: [docs/docs/gpt-researcher/context/filtering-by-domain.md:47-62]()

---

## Technical Implementation Details

### Backend Processing Architecture

```mermaid
flowchart TD
    WSMessage["WebSocket Message<br/>{domains: ['forbes.com']}"]
    
    WSMessage --> Handler["handle_websocket_communication()<br/>backend/server.py"]
    
    Handler --> ExtractParams["Extract domains parameter<br/>from message payload"]
    
    ExtractParams --> CreateResearcher["GPTResearcher.__init__()<br/>gpt_researcher/agent.py"]
    
    CreateResearcher --> StoreConfig["Store domains in<br/>researcher.domains attribute"]
    
    StoreConfig --> PlanStage["Research Planning<br/>Generate Sub-queries"]
    
    PlanStage --> SubQuery["For each sub-query"]
    
    SubQuery --> RetrieverCall["Call retriever.search()<br/>Pass domains parameter"]
    
    RetrieverCall --> RetrieverType{Retriever?}
    
    RetrieverType -->|Tavily| TavilyAPI["TavilySearch.search()<br/>include_domains=domains"]
    RetrieverType -->|Google| GoogleAPI["GoogleSearch.search()<br/>Apply domain filter"]
    RetrieverType -->|Other| IgnoreDomains["Ignore domains parameter"]
    
    TavilyAPI --> FilteredURLs["Filtered URL List"]
    GoogleAPI --> FilteredURLs
    IgnoreDomains --> AllURLs["All URLs"]
    
    FilteredURLs --> BrowserManager["BrowserManager.browse()<br/>Scrape filtered URLs"]
    AllURLs --> BrowserManager
    
    BrowserManager --> Context["Aggregated Context"]
```

Sources: [docs/docs/gpt-researcher/context/filtering-by-domain.md:1-62](), [docs/docs/gpt-researcher/gptr/querying-the-backend.md:31-45]()

### Data Flow Through Interfaces

The following table summarizes how domains flow from each interface to the backend:

| Interface | Input Method | Storage | Transport | Backend Receiver |
|-----------|--------------|---------|-----------|------------------|
| Pip Package | Constructor parameter | Python variable | Direct method call | `GPTResearcher.__init__()` |
| NextJS Frontend | Settings Modal | localStorage | WebSocket JSON | `handle_websocket_communication()` |
| Vanilla JS Frontend | Input field | None | WebSocket JSON | `handle_websocket_communication()` |
| URL Parameter | Query string | Parsed to localStorage | WebSocket JSON (via NextJS) | `handle_websocket_communication()` |

Sources: [docs/docs/gpt-researcher/context/filtering-by-domain.md:22-62]()

---

## Embed Script Compatibility

The embed script (`embed.js`) supports domain filtering through the host application's URL parameters. When embedding GPT Researcher in external applications, domains can be passed via query parameters.

### Embed Script URL Construction

The embed script constructs an iframe URL that can include domain parameters by checking `GPTR_API_URL` in `localStorage`. [frontend/nextjs/public/embed.js:4-15]()

```javascript
// From frontend/nextjs/public/embed.js
const iframe = document.createElement("iframe");
iframe.src = "https://gptr.app" + (parentApiUrl ? "?GPTR_API_URL=" + parentApiUrl : "");
```

The iframe loads the NextJS frontend with the specified domains, which are then processed through the standard URL parameter flow. [docs/docs/gpt-researcher/frontend/embed-script.md:8-9]()

Sources: [frontend/nextjs/public/embed.js:1-15](), [docs/docs/gpt-researcher/frontend/embed-script.md:1-28]()

---

## Domain Format Specifications

### Domain String Format

Domains must be specified as bare hostnames without protocol or path:

**Valid Formats:**
- `forbes.com`
- `techcrunch.com`
- `en.wikipedia.org`

**Invalid Formats:**
- `https://forbes.com` (includes protocol)
- `forbes.com/tech` (includes path)
- `www.forbes.com` (www prefix may work but is unnecessary)

### Multiple Domain Separator

When passing multiple domains:
- **Array format (Python):** `["forbes.com", "techcrunch.com"]` [docs/docs/gpt-researcher/context/filtering-by-domain.md:31-32]()
- **Comma-separated (URL/Frontend):** `forbes.com,techcrunch.com` [docs/docs/gpt-researcher/context/filtering-by-domain.md:59-60]()

Sources: [docs/docs/gpt-researcher/context/filtering-by-domain.md:22-62]()

---

## Limitations and Extensibility

### Current Limitations

1. **Retriever Support:** Domain filtering only works with Tavily and Google Search retrievers [docs/docs/gpt-researcher/context/filtering-by-domain.md:3-5]()
2. **Report Source Restriction:** Only applicable when `report_source="web"` [docs/docs/gpt-researcher/context/filtering-by-domain.md:30-31]()
3. **No Wildcard Support:** Subdomain wildcards (e.g., `*.wikipedia.org`) are not supported

### Future Extensibility

The documentation explicitly welcomes contributions to add domain filtering support to additional retrievers. [docs/docs/gpt-researcher/context/filtering-by-domain.md:5-6]() To add domain filtering to a new retriever:

1. Implement domain parameter handling in the retriever's `search()` method
2. Apply domain filter to search API calls or post-process results
3. Document the new capability in retriever configuration

Sources: [docs/docs/gpt-researcher/context/filtering-by-domain.md:5-6]()

---

## Configuration Summary

### Environment Variables Required

| Variable | Required For | Description |
|----------|--------------|-------------|
| `RETRIEVER` | All | Set to `tavily` or `google` [docs/docs/gpt-researcher/context/filtering-by-domain.md:9-17]() |
| `TAVILY_API_KEY` | Tavily | API key for Tavily search [docs/docs/gpt-researcher/context/filtering-by-domain.md:11-12]() |
| `GOOGLE_API_KEY` | Google | API key for Google Custom Search [docs/docs/gpt-researcher/context/filtering-by-domain.md:18-19]() |
| `GOOGLE_CX_KEY` | Google | Google Custom Search Engine ID [docs/docs/gpt-researcher/context/filtering-by-domain.md:19-20]() |

### Interface-Specific Configuration

**Pip Package:**
- Pass `domains` list to `GPTResearcher()` constructor [docs/docs/gpt-researcher/context/filtering-by-domain.md:27-32]()
- Requires `report_source="web"`

**NextJS Frontend:**
- Configure via Settings Modal [docs/docs/gpt-researcher/context/filtering-by-domain.md:37-39]()
- Persists in browser localStorage
- Can be pre-set via URL parameters [docs/docs/gpt-researcher/context/filtering-by-domain.md:55-61]()

**Vanilla JS Frontend:**
- Enter domains in input field [docs/docs/gpt-researcher/context/filtering-by-domain.md:43-45]()
- No persistence between sessions

**Embedded Applications:**
- Pass domains via iframe URL parameters
- Inherits NextJS frontend behavior [frontend/nextjs/public/embed.js:15-16]()

Sources: [docs/docs/gpt-researcher/context/filtering-by-domain.md:7-62]()

---

# Page: User Interfaces

# User Interfaces

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/report_type/basic_report/basic_report.py](backend/report_type/basic_report/basic_report.py)
- [backend/report_type/detailed_report/detailed_report.py](backend/report_type/detailed_report/detailed_report.py)
- [backend/server/multi_agent_runner.py](backend/server/multi_agent_runner.py)
- [backend/server/server_utils.py](backend/server/server_utils.py)
- [backend/server/websocket_manager.py](backend/server/websocket_manager.py)
- [frontend/index.html](frontend/index.html)
- [frontend/nextjs/app/page.tsx](frontend/nextjs/app/page.tsx)
- [frontend/nextjs/components/Footer.tsx](frontend/nextjs/components/Footer.tsx)
- [frontend/nextjs/components/Header.tsx](frontend/nextjs/components/Header.tsx)
- [frontend/nextjs/components/Hero.tsx](frontend/nextjs/components/Hero.tsx)
- [frontend/nextjs/components/ResearchBlocks/elements/InputArea.tsx](frontend/nextjs/components/ResearchBlocks/elements/InputArea.tsx)
- [frontend/nextjs/components/ResearchSidebar.tsx](frontend/nextjs/components/ResearchSidebar.tsx)
- [frontend/scripts.js](frontend/scripts.js)
- [frontend/styles.css](frontend/styles.css)
- [tests/test_websocket_manager.py](tests/test_websocket_manager.py)

</details>



This page provides an overview of all user interface options available for interacting with GPT Researcher. It covers the backend API layer that serves these interfaces, the communication protocols used, and the relationship between different interface types.

For detailed documentation on specific interfaces, see:
- FastAPI backend and WebSocket protocol: [FastAPI Backend and WebSocket API](#8.1)
- Production web interface: [NextJS Production Frontend](#8.2)
- Lightweight web interface: [Vanilla JS Lightweight Frontend](#8.3)
- Integration into other applications: [Embed Script Integration](#8.4)
- Frontend state persistence: [Frontend State and History Management](#8.5)
- Streaming data processing: [Frontend Data Processing](#8.6)

## Available Interface Options

GPT Researcher provides four primary user interface options, all powered by a common FastAPI backend:

| Interface Type | Port | Technology Stack | Use Case |
|---------------|------|------------------|----------|
| **Vanilla JS Frontend** | 8000 | HTML/CSS/JS | Lightweight deployment, simple integration, minimal dependencies |
| **NextJS Frontend** | 3000 | React/NextJS/Tailwind | Production deployments, advanced features (drag-n-drop docs, GUI config) |
| **Embed Script** | N/A | JS Widget | Integration into existing web applications via iframe |
| **Direct API Access** | 8000 | WebSocket/REST | Programmatic access, custom frontends, mobile apps |

All interfaces communicate with the same FastAPI backend server running on port 8000, which orchestrates research tasks and streams results in real-time.

Sources: [frontend/index.html:1-13](), [frontend/nextjs/app/page.tsx:28-66]()

## System Architecture Overview

The following diagram illustrates the complete user interface architecture and how different interfaces connect to the backend:

### Interface Connectivity Diagram
```mermaid
graph TB
    subgraph "Client Applications"
        DesktopBrowser["Desktop Browser"]
        MobileBrowser["Mobile Browser"]
    end
    
    subgraph "Frontend Layer"
        VanillaJS["Vanilla JS Frontend<br/>frontend/index.html<br/>frontend/scripts.js"]
        NextJS["Next.js Frontend<br/>nextjs/app/page.tsx"]
    end
    
    subgraph "Communication Layer"
        WebSocket["WebSocket Protocol<br/>ws://host:8000/ws"]
        REST["REST API<br/>/api/chat"]
    end
    
    subgraph "Backend API - Port 8000"
        WSManager["WebSocketManager<br/>backend/server/websocket_manager.py"]
        WSComm["handle_websocket_communication<br/>backend/server/server_utils.py"]
        LogsHandler["CustomLogsHandler<br/>backend/server/server_utils.py"]
    end
    
    subgraph "Research Execution"
        BasicReport["BasicReport<br/>basic_report.py"]
        DetailedReport["DetailedReport<br/>detailed_report.py"]
        MultiAgent["run_multi_agent_task<br/>multi_agent_runner.py"]
    end
    
    DesktopBrowser --> VanillaJS
    DesktopBrowser --> NextJS
    MobileBrowser --> NextJS
    
    VanillaJS -.->|WebSocket| WebSocket
    NextJS -.->|WebSocket| WebSocket
    NextJS -.->|Mobile: REST| REST
    
    WebSocket --> WSManager
    REST --> WSComm
    
    WSManager --> WSComm
    WSComm --> LogsHandler
    
    WSComm --> BasicReport
    WSComm --> DetailedReport
    WSComm --> MultiAgent
    
    LogsHandler -.->|Stream JSON| WebSocket
```

Sources: [backend/server/websocket_manager.py:21-60](), [backend/server/server_utils.py:33-80](), [frontend/nextjs/app/page.tsx:109-118]()

## Backend API Layer

The FastAPI backend serves as the unified entry point for all user interfaces. It provides two main interaction patterns:

### WebSocket Communication

WebSocket connections enable real-time bidirectional communication for streaming research progress. The `WebSocketManager` class manages connection lifecycle:

- **Connection Management**: The `connect()` and `disconnect()` methods in [backend/server/websocket_manager.py:53-100]() handle lifecycle.
- **Message Queuing**: Each connection has an associated `asyncio.Queue` for reliable message delivery [backend/server/websocket_manager.py:28]().
- **Sender Tasks**: Background tasks continuously send queued messages to clients [backend/server/websocket_manager.py:30-51]().

### REST Endpoints

REST endpoints provide stateless request-response interactions, particularly for mobile clients or chat functionality:
- **Chat API**: The NextJS frontend utilizes `/api/chat` for mobile interactions when WebSocket is unavailable [frontend/nextjs/app/page.tsx:167-176]().
- **File Uploads**: Handled via `DocumentLoader` for processing local research materials [backend/server/server_utils.py:10]().

Sources: [backend/server/websocket_manager.py:21-114](), [frontend/nextjs/app/page.tsx:164-180]()

## Real-Time Data Streaming

The `CustomLogsHandler` class in [backend/server/server_utils.py:33-80]() serves dual purposes:
1. **Real-time streaming**: Sends JSON messages to the WebSocket client via `send_json` [backend/server/server_utils.py:56-60]().
2. **Persistent logging**: Writes structured logs to `outputs/task_*.json` files [backend/server/server_utils.py:38-44]().

### Research Streaming Sequence
```mermaid
sequenceDiagram
    participant Client as "Frontend (scripts.js / page.tsx)"
    participant WS as "WebSocketManager"
    participant Handler as "CustomLogsHandler"
    participant Agent as "GPTResearcher"
    
    Client->>WS: "start {task, report_type...}"
    WS->>Handler: Initialize(websocket, task)
    WS->>Agent: conduct_research()
    
    loop Progress Events
        Agent->>Handler: send_json({type: 'logs', content: '...'})
        Handler->>Client: websocket.send_json(data)
    end
    
    Agent->>Handler: send_json({type: 'report', content: '...'})
    Handler->>Client: Final Report
```

Sources: [backend/server/server_utils.py:56-80](), [backend/server/websocket_manager.py:116-160]()

## Frontend Message Processing

Frontends consume streaming messages through several processing stages:

### State and History Management
The NextJS frontend uses a `ResearchHistoryContext` to manage local persistence [frontend/nextjs/app/page.tsx:6](). It stores research IDs and associated data to allow users to revisit previous reports via the `ResearchSidebar` [frontend/nextjs/components/ResearchSidebar.tsx:7-23]().

The Vanilla JS frontend tracks history in `conversationHistory` and persists it via cookies or `localStorage` [frontend/scripts.js:4-6]().

### Platform Differentiation
The NextJS frontend implements platform-specific strategies:
- **Desktop**: Primarily uses `useWebSocket` for interactive research [frontend/nextjs/app/page.tsx:109-118]().
- **Mobile**: Detects mobile state via `window.innerWidth < 768` and falls back to RESTful chat calls for better reliability [frontend/nextjs/app/page.tsx:83-96]().

Sources: [frontend/nextjs/app/page.tsx:109-118](), [frontend/nextjs/components/ResearchSidebar.tsx:16-23](), [frontend/scripts.js:82-104]()

## Component Communication Patterns

The following diagram maps user interactions to backend processes:

### User Interaction Flow
```mermaid
graph TB
    subgraph "User Actions"
        A1["Submit Research Form"]
        A2["Chat with Report"]
        A3["View History"]
    end
    
    subgraph "Frontend Components"
        B1["InputArea.tsx"]
        B2["ChatBox (NextJS)"]
        B3["ResearchSidebar.tsx"]
    end
    
    subgraph "Backend Logic"
        C1["handle_start_command"]
        C2["handle_chat_command"]
        C3["generate_report_files"]
    end
    
    A1 --> B1
    A2 --> B2
    A3 --> B3
    
    B1 -.->|WS 'start'| C1
    B2 -.->|WS 'chat'| C2
    B3 -.->|File Access| C3
    
    C1 --> D1["BasicReport / DetailedReport"]
    C2 --> D2["ChatAgentWithMemory"]
```

Sources: [backend/server/server_utils.py:126-141](), [backend/server/server_utils.py:187-210](), [frontend/nextjs/components/ResearchBlocks/elements/InputArea.tsx:100-108]()

## Configuration UI

The frontends expose key configuration options that map directly to the `GPTResearcher` and `Config` classes:

| Configuration | UI Element | Maps to Parameter |
|--------------|-----------|-------------------|
| **Report Type** | `<select id="report_type">` | `report_type` in `DetailedReport` [backend/report_type/detailed_report/detailed_report.py:30]() |
| **Tone** | `<select name="tone">` | `tone` in `BasicReport` [backend/report_type/basic_report/basic_report.py:18]() |
| **Report Source** | `chatBoxSettings.report_source` | `report_source` [frontend/nextjs/app/page.tsx:40]() |
| **Max Search Results** | `max_search_results` | `cfg.max_search_results_per_query` [backend/report_type/basic_report/basic_report.py:64]() |

Sources: [frontend/nextjs/app/page.tsx:36-48](), [backend/report_type/basic_report/basic_report.py:10-25](), [backend/report_type/detailed_report/detailed_report.py:10-41]()

## Error Handling and Recovery

The frontend implements automatic reconnection with exponential backoff to handle network instability. In `scripts.js`, `reconnectAttempts` and `maxReconnectAttempts` manage this process [frontend/scripts.js:21-23]().

On the backend, `WebSocketManager` ensures that if a connection is lost, sender tasks are cancelled and queues are cleaned up to prevent memory leaks [backend/server/websocket_manager.py:66-99]().

Sources: [frontend/scripts.js:21-23](), [backend/server/websocket_manager.py:66-99]()

---

# Page: FastAPI Backend and WebSocket API

# FastAPI Backend and WebSocket API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/chat/chat.py](backend/chat/chat.py)
- [backend/report_type/basic_report/basic_report.py](backend/report_type/basic_report/basic_report.py)
- [backend/report_type/detailed_report/detailed_report.py](backend/report_type/detailed_report/detailed_report.py)
- [backend/run_server.py](backend/run_server.py)
- [backend/server/agent_discovery.py](backend/server/agent_discovery.py)
- [backend/server/app.py](backend/server/app.py)
- [backend/server/multi_agent_runner.py](backend/server/multi_agent_runner.py)
- [backend/server/report_store.py](backend/server/report_store.py)
- [backend/server/server_utils.py](backend/server/server_utils.py)
- [backend/server/websocket_manager.py](backend/server/websocket_manager.py)
- [frontend/index.html](frontend/index.html)
- [frontend/scripts.js](frontend/scripts.js)
- [frontend/styles.css](frontend/styles.css)
- [main.py](main.py)
- [tests/test_agent_discovery.py](tests/test_agent_discovery.py)
- [tests/test_websocket_manager.py](tests/test_websocket_manager.py)

</details>



## Purpose and Scope

This document covers the FastAPI backend server that powers GPT Researcher, including its WebSocket-based real-time communication protocol, REST API endpoints, and streaming log infrastructure. The backend serves as the primary interface between frontend clients and the core research engine.

For information about the core research orchestration logic, see [GPTResearcher Agent Class](#3.1). For frontend-specific data processing and state management, see [Frontend State and History Management](#8.5) and [Frontend Data Processing](#8.6). For deployment configurations, see [Server Configuration and Entry Points](#11.2).

## Server Architecture Overview

The backend is structured around a central FastAPI application that manages both synchronous REST endpoints and asynchronous WebSocket connections for long-running research tasks.

Title: GPT Researcher Backend Architecture
```mermaid
graph TB
    runServer["run_server.py<br/>Uvicorn Entry Point"]
    fastAPIApp["backend.server.app<br/>FastAPI Application"]
    wsManager["WebSocketManager<br/>Connection Pool"]
    serverUtils["server_utils Module<br/>Message Handlers"]
    logsHandler["CustomLogsHandler<br/>Streaming Logs to JSON"]
    reportStore["ReportStore<br/>JSON Persistence"]
    
    subgraph "WebSocket Endpoints"
        wsEndpoint["/ws<br/>WebSocket Connection"]
    end
    
    subgraph "REST Endpoints"
        serveFrontend["/ (GET)<br/>serve_frontend()"]
        getReports["/api/reports (GET)<br/>get_all_reports()"]
        postReport["/api/reports (POST)<br/>create_or_update_report()"]
        uploadEndpoint["/api/upload (POST)<br/>handle_file_upload()"]
    end
    
    subgraph "Message Handlers"
        startHandler["handle_start_command()<br/>Research Initiation"]
        chatHandler["handle_chat_command()<br/>Chat Processing"]
        feedbackHandler["handle_human_feedback()<br/>Multi-Agent Feedback"]
    end
    
    subgraph "Report Execution"
        basicReport["BasicReport<br/>Single-Pass Research"]
        detailedReport["DetailedReport<br/>Subtopic Research"]
        multiAgent["run_multi_agent_task()<br/>LangGraph Workflow"]
    end
    
    runServer -->|"uvicorn.run(app)"| fastAPIApp
    fastAPIApp --> wsEndpoint
    fastAPIApp --> serveFrontend
    fastAPIApp --> getReports
    fastAPIApp --> postReport
    fastAPIApp --> uploadEndpoint
    
    getReports --> reportStore
    postReport --> reportStore
    
    wsEndpoint -->|"manager.connect()"| wsManager
    wsManager -->|"handle_websocket_communication()"| serverUtils
    
    serverUtils --> startHandler
    serverUtils --> chatHandler
    serverUtils --> feedbackHandler
    
    startHandler -->|"manager.start_streaming()"| wsManager
    wsManager -->|"run_agent()"| basicReport
    wsManager -->|"run_agent()"| detailedReport
    wsManager -->|"run_agent()"| multiAgent
    
    basicReport -.->|"stream logs"| logsHandler
    detailedReport -.->|"stream logs"| logsHandler
    multiAgent -.->|"stream logs"| logsHandler
    
    logsHandler -->|"send_json()"| wsEndpoint
```
Sources: [backend/run_server.py:1-27](), [backend/server/app.py:97-210](), [backend/server/websocket_manager.py:21-114](), [backend/server/server_utils.py:126-252]()

## FastAPI Server Startup

The server is initialized and started through [backend/run_server.py:1-27](). The entry point performs the following setup:

| Component | Configuration | Location |
|-----------|--------------|----------|
| **ASGI Server** | Uvicorn | [backend/run_server.py:21-27]() |
| **App Instance** | `server.app:app` | [backend/run_server.py:22]() |
| **Host/Port** | `0.0.0.0:8000` | [backend/run_server.py:23-24]() |
| **Static Files** | `/site` (frontend), `/static` (assets), `/outputs` (reports) | [backend/server/app.py:74-87]() |
| **CORS** | Configurable via `CORS_ALLOW_ORIGINS` | [backend/server/app.py:99-120]() |

The application uses a `lifespan` context manager to ensure the `outputs` directory exists and to log startup/shutdown events [backend/server/app.py:71-92]().

Sources: [backend/run_server.py:1-27](), [backend/server/app.py:71-133]()

## WebSocket Manager

The `WebSocketManager` class [backend/server/websocket_manager.py:21-114]() manages WebSocket connection lifecycle and message queuing.

### Connection Management

```python
# Key attributes initialized in __init__
self.active_connections: List[WebSocket] = []
self.sender_tasks: Dict[WebSocket, asyncio.Task] = {}
self.message_queues: Dict[WebSocket, asyncio.Queue] = {}
```

| Method | Purpose | Key Operations |
|--------|---------|----------------|
| `connect(websocket)` | Establish WebSocket connection | Accept connection, create message queue, start sender task [backend/server/websocket_manager.py:53-61]() |
| `disconnect(websocket)` | Clean up connection | Cancel sender task, close websocket, remove from active connections [backend/server/websocket_manager.py:66-100]() |
| `start_sender(websocket)` | Background message sender | Continuously read from queue and send to client [backend/server/websocket_manager.py:30-51]() |
| `start_streaming(...)` | Initiate research workflow | Call `run_agent()` with research parameters [backend/server/websocket_manager.py:101-114]() |

Sources: [backend/server/websocket_manager.py:21-114]()

## WebSocket Communication Protocol

Communication follows a command-based protocol where the client sends string-prefixed JSON payloads, and the server responds with typed JSON messages.

Title: WebSocket Communication Sequence
```mermaid
sequenceDiagram
    participant Client as "WebSocket Client<br/>(Browser/App)"
    participant WS as "/ws Endpoint"
    participant Handler as "handle_websocket_communication()"
    participant StartCmd as "handle_start_command()"
    participant LogsHandler as "CustomLogsHandler"
    participant Agent as "run_agent()"
    
    Client->>WS: Connect to ws://host/ws
    WS->>Handler: websocket.accept()
    Handler-->>Client: Connection established
    
    loop Message Loop
        Client->>Handler: receive_text()
        
        alt Command: "start {json_data}"
            Handler->>StartCmd: Parse and execute
            StartCmd->>LogsHandler: Create logs handler
            StartCmd->>Agent: manager.start_streaming()
            Agent-->>LogsHandler: Stream research events
            loop During Research
                LogsHandler-->>Client: send_json(event)
            end
            Agent-->>Client: send_json(file_paths)
        else Command: "chat {json_data}"
            Handler->>chatHandler: handle_chat_command()
            chatHandler-->>Client: send_json(response)
        else Command: "human_feedback {json_data}"
            Handler->>feedbackHandler: handle_human_feedback()
        else Command: "ping"
            Handler-->>Client: "pong"
        end
    end
```
Sources: [backend/server/server_utils.py:126-180](), [backend/server/server_utils.py:325-395]()

## Message Handling Pipeline

The core message routing logic is implemented in `handle_websocket_communication()` [backend/server/server_utils.py:325-395]().

### Command Detection and Routing

Commands are identified by their string prefix:

| Command Prefix | Handler Function | Purpose |
|----------------|------------------|---------|
| `"start"` | `handle_start_command()` | Initiate research task [backend/server/server_utils.py:126]() |
| `"chat"` | `handle_chat_command()` | Process chat messages [backend/server/server_utils.py:187]() |
| `"human_feedback"` | `handle_human_feedback()` | Handle multi-agent feedback [backend/server/server_utils.py:181]() |
| `"ping"` | Inline handler | Health check response [backend/server/websocket_manager.py:43-44]() |

Sources: [backend/server/server_utils.py:126-252](), [backend/server/server_utils.py:325-395]()

## CustomLogsHandler - Streaming Research Progress

The `CustomLogsHandler` class [backend/server/server_utils.py:33-80]() captures and streams research events in real-time to both WebSocket clients and JSON log files.

### Initialization

```python
def __init__(self, websocket, task: str):
    self.logs = []
    self.websocket = websocket
    sanitized_filename = sanitize_filename(f"task_{int(time.time())}_{task}")
    self.log_file = os.path.join("outputs", f"{sanitized_filename}.json")
    # ...
```
Each handler creates a unique log file in the `outputs/` directory to store events and final research content [backend/server/server_utils.py:38-54]().

### Streaming Events

The `send_json()` method [backend/server/server_utils.py:56-79]() performs dual-writing:
1. **WebSocket Stream**: Immediately sends data to connected client via `websocket.send_json(data)` [backend/server/server_utils.py:60]().
2. **JSON File**: Updates the local log file with events or content updates [backend/server/server_utils.py:63-79]().

Sources: [backend/server/server_utils.py:33-80]()

## WebSocket Message Types

Messages sent from server to client during research execution use a standardized JSON format:

| Type | Content | Metadata/Output | Purpose |
|------|---------|-----------------|---------|
| `logs` | Event name | Event description | Research progress updates [backend/server/websocket_manager.py:127-131]() |
| `path` | N/A | `{pdf, docx, md, json}` | Generated report file locations [backend/server/server_utils.py:175-178]() |
| `report` | N/A | Markdown chunks | Streaming report content |
| `chat` | Response text | `{role: "assistant"}` | Chat interaction responses [backend/server/server_utils.py:203-207]() |

Sources: [backend/server/server_utils.py:126-179](), [backend/server/websocket_manager.py:127-131]()

## Start Command Handler

The `handle_start_command()` function [backend/server/server_utils.py:126-179]() processes research initiation requests.

### Execution Flow

1. **Extraction**: Parses JSON payload using `extract_command_data()` [backend/server/server_utils.py:141]().
2. **Log Initialization**: Creates a `CustomLogsHandler` and sends the initial query [backend/server/server_utils.py:148-155]().
3. **Research Execution**: Calls `manager.start_streaming()` which triggers the underlying research agent [backend/server/server_utils.py:159-173]().
4. **File Generation**: Converts the final report to PDF and DOCX formats [backend/server/server_utils.py:175]().
5. **Completion**: Sends the relative file paths back to the client [backend/server/server_utils.py:178]().

Sources: [backend/server/server_utils.py:126-179]()

## Chat Command Handler

The `handle_chat_command()` function [backend/server/server_utils.py:187-252]() processes conversational queries about completed research reports.

### Chat Flow

1. **Context Loading**: Extracts the existing report and conversation history from the payload [backend/server/server_utils.py:194-196]().
2. **Agent Initialization**: Instantiates `ChatAgentWithMemory` with the report context [backend/chat/chat.py:55-80]().
3. **Processing**: Calls `chat_agent.chat(messages, websocket)` which supports tool calling for web searches [backend/chat/chat.py:187-210]().
4. **Streaming**: The agent streams the response and search metadata directly to the WebSocket [backend/chat/chat.py:204-210]().

Sources: [backend/server/server_utils.py:187-252](), [backend/chat/chat.py:55-210]()

## run_agent() - Research Orchestration

The `run_agent()` function [backend/server/websocket_manager.py:116-184]() serves as the bridge between the WebSocket interface and the core research logic.

Title: Agent Execution Logic
```mermaid
graph TD
    runAgent["run_agent()"] --> logsHandler["CustomLogsHandler"]
    logsHandler --> checkMCP{MCP Enabled?}
    
    checkMCP -->|Yes| logMCP["Log MCP Strategy & Configs"]
    checkMCP -->|No| checkType{Report Type?}
    
    logMCP --> checkType
    
    checkType -->|multi_agents| multiAgent["run_multi_agent_task()"]
    checkType -->|detailed_report| detailedReport["DetailedReport.run()"]
    checkType -->|other| basicReport["BasicReport.run()"]
    
    multiAgent --> finalize["Return Report"]
    detailedReport --> finalize
    basicReport --> finalize
```
Sources: [backend/server/websocket_manager.py:116-184]()

## REST API Endpoints

The FastAPI backend exposes several REST endpoints for history management and file operations:

| Endpoint | Method | Purpose | Handler |
|----------|--------|---------|---------|
| `/api/reports` | GET | Retrieve list of past research tasks | `get_all_reports()` [backend/server/app.py:183-187]() |
| `/api/reports` | POST | Save or update a research report | `create_or_update_report()` [backend/server/app.py:198-207]() |
| `/api/upload` | POST | Upload documents for local research | `handle_file_upload()` [backend/server/server_utils.py:293-302]() |
| `/report/{id}` | GET | Serve generated DOCX report | `read_report()` [backend/server/app.py:174-179]() |

Sources: [backend/server/app.py:174-207](), [backend/server/server_utils.py:293-302]()

## Client Integration Example (Vanilla JS)

The Vanilla JS frontend [frontend/index.html:1-152]() demonstrates how to interact with the WebSocket API.

### Connection and Command Dispatch
```javascript
// From frontend/scripts.js
const socket = new WebSocket(`ws://${window.location.host}/ws`);

const startResearch = () => {
  const data = {
    task: document.getElementById('task').value,
    report_type: document.getElementById('report_type').value,
    report_source: "web",
    tone: "Objective"
  };
  socket.send("start " + JSON.stringify(data));
};

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'logs') {
    // Update UI with data.output
  }
};
```
Sources: [frontend/index.html:154-179](), [frontend/scripts.js:25-79]()

---

# Page: NextJS Production Frontend

# NextJS Production Frontend

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/gpt-researcher/frontend/nextjs-frontend.md](docs/docs/gpt-researcher/frontend/nextjs-frontend.md)
- [docs/docs/gpt-researcher/frontend/vanilla-js-frontend.md](docs/docs/gpt-researcher/frontend/vanilla-js-frontend.md)
- [frontend/nextjs/.dockerignore](frontend/nextjs/.dockerignore)
- [frontend/nextjs/.eslintrc.json](frontend/nextjs/.eslintrc.json)
- [frontend/nextjs/.example.env](frontend/nextjs/.example.env)
- [frontend/nextjs/.gitignore](frontend/nextjs/.gitignore)
- [frontend/nextjs/.prettierrc](frontend/nextjs/.prettierrc)
- [frontend/nextjs/Dockerfile](frontend/nextjs/Dockerfile)
- [frontend/nextjs/Dockerfile.dev](frontend/nextjs/Dockerfile.dev)
- [frontend/nextjs/README.md](frontend/nextjs/README.md)
- [frontend/nextjs/actions/apiActions.ts](frontend/nextjs/actions/apiActions.ts)
- [frontend/nextjs/app/page.tsx](frontend/nextjs/app/page.tsx)
- [frontend/nextjs/components/Footer.tsx](frontend/nextjs/components/Footer.tsx)
- [frontend/nextjs/components/Header.tsx](frontend/nextjs/components/Header.tsx)
- [frontend/nextjs/components/Hero.tsx](frontend/nextjs/components/Hero.tsx)
- [frontend/nextjs/components/ResearchBlocks/elements/InputArea.tsx](frontend/nextjs/components/ResearchBlocks/elements/InputArea.tsx)
- [frontend/nextjs/components/ResearchSidebar.tsx](frontend/nextjs/components/ResearchSidebar.tsx)
- [frontend/nextjs/helpers/getHost.ts](frontend/nextjs/helpers/getHost.ts)
- [frontend/nextjs/hooks/useAnalytics.ts](frontend/nextjs/hooks/useAnalytics.ts)
- [frontend/nextjs/package.json](frontend/nextjs/package.json)
- [frontend/nextjs/rollup.config.js](frontend/nextjs/rollup.config.js)
- [frontend/nextjs/src/GPTResearcher.tsx](frontend/nextjs/src/GPTResearcher.tsx)
- [frontend/nextjs/src/index.ts](frontend/nextjs/src/index.ts)
- [frontend/nextjs/tsconfig.json](frontend/nextjs/tsconfig.json)
- [frontend/nextjs/tsconfig.lib.json](frontend/nextjs/tsconfig.lib.json)
- [frontend/nextjs/utils/consolidateBlocks.ts](frontend/nextjs/utils/consolidateBlocks.ts)
- [frontend/nextjs/utils/dataProcessing.ts](frontend/nextjs/utils/dataProcessing.ts)

</details>



## Purpose and Scope

This document describes the NextJS production frontend for GPT Researcher, located in [frontend/nextjs/](). This is the primary user interface for interacting with the GPT Researcher system, providing a modern, feature-rich React application with TypeScript and Tailwind CSS.

The NextJS frontend offers advanced features including drag-and-drop document upload, GUI-based configuration, research history management, and both desktop and mobile optimized experiences. It communicates with the FastAPI backend via WebSockets for real-time streaming and REST APIs for chat and mobile fallback.

Sources: [frontend/nextjs/package.json:1-13](), [frontend/nextjs/README.md:1-20](), [docs/docs/gpt-researcher/frontend/nextjs-frontend.md:11-20]()

## Architecture Overview

### Technology Stack

The NextJS frontend is built with:
- **Next.js 14**: React framework with server-side rendering [frontend/nextjs/package.json:35-35]()
- **TypeScript**: Type-safe development [frontend/nextjs/package.json:83-83]()
- **Tailwind CSS**: Utility-first CSS framework [frontend/nextjs/package.json:82-82]()
- **Framer Motion**: Animation library for smooth transitions [frontend/nextjs/package.json:33-33]()
- **WebSocket API**: Real-time communication with backend [frontend/nextjs/hooks/useWebSocket.ts:1-12]()
- **Zod**: Schema validation for data structures [frontend/nextjs/package.json:47-47]()
- **Rollup**: Used for bundling the frontend as a library [frontend/nextjs/rollup.config.js:19-32]()

### Component Hierarchy

```mermaid
graph TB
    page["page.tsx (Main Orchestrator)"]
    
    page --> Hero["Hero.tsx (Landing Input)"]
    page --> Header["Header.tsx (Top Bar)"]
    page --> Footer["Footer.tsx (Settings/Links)"]
    page --> ResearchSidebar["ResearchSidebar.tsx (History)"]
    page --> ResearchPageLayout["ResearchPageLayout (Desktop)"]
    page --> MobileHomeScreen["MobileHomeScreen (Mobile Landing)"]
    
    Hero --> InputArea["InputArea.tsx (Text Input)"]
    Footer --> Modal["Modal (Settings UI)"]
    Modal --> ChatBox["ChatBox.tsx (Config Form)"]
    ChatBox --> ResearchForm["ResearchForm.tsx (Options)"]
    
    page -.->|State| useWebSocket["useWebSocket hook"]
    page -.->|Context| ResearchHistoryContext["ResearchHistoryContext"]
```
Sources: [frontend/nextjs/app/page.tsx:15-27](), [frontend/nextjs/components/Settings/Modal.tsx:3-6](), [frontend/nextjs/components/Task/ResearchForm.tsx:1-8]()

## Main Page Component

### State Management

The `Home` component in [frontend/nextjs/app/page.tsx:28-28]() manages the application state. Key state variables include:

| State Variable | Type | Purpose |
|----------------|------|---------|
| `promptValue` | `string` | Current research query input [frontend/nextjs/app/page.tsx:30-30]() |
| `answer` | `string` | Accumulated research report content [frontend/nextjs/app/page.tsx:33-33]() |
| `loading` | `boolean` | Research in progress indicator [frontend/nextjs/app/page.tsx:34-34]() |
| `chatBoxSettings` | `ChatBoxSettings` | Configuration for report type, source, and tone [frontend/nextjs/app/page.tsx:36-36]() |
| `orderedData` | `Data[]` | Streamed research logs and steps [frontend/nextjs/app/page.tsx:68-68]() |
| `isMobile` | `boolean` | Responsive layout toggle [frontend/nextjs/app/page.tsx:76-76]() |

### ChatBoxSettings Configuration

The `chatBoxSettings` object controls the research behavior sent to the backend [frontend/nextjs/app/page.tsx:38-48]():

```typescript
const defaultSettings = {
  report_type: "research_report",
  report_source: "web",
  tone: "Objective",
  domains: [],
  defaultReportType: "research_report",
  layoutType: 'copilot',
  mcp_enabled: false,
  mcp_configs: [],
  mcp_strategy: "fast",
};
```
These settings are persisted in `localStorage` under the key `chatBoxSettings` [frontend/nextjs/app/page.tsx:52-52]().

Sources: [frontend/nextjs/app/page.tsx:36-66](), [frontend/nextjs/components/Task/ResearchForm.tsx:111-148]()

## Communication Architecture

### WebSocket Implementation

The `useWebSocket` hook manages the connection to the FastAPI backend [frontend/nextjs/hooks/useWebSocket.ts:5-11]().

**Connection Logic**:
- Generates the URI using `getHost()` [frontend/nextjs/hooks/useWebSocket.ts:60-63]().
- Sends a `start` command containing the task and settings as a JSON string [frontend/nextjs/hooks/useWebSocket.ts:92-94]().
- Implements a 30-second heartbeat (ping/pong) to keep the connection alive [frontend/nextjs/hooks/useWebSocket.ts:38-42]().

**Message Handling**:
- `type: 'report'`: Appends content to the `answer` state [frontend/nextjs/hooks/useWebSocket.ts:120-121]().
- `type: 'report_complete'`: Replaces the answer with the final version including images [frontend/nextjs/hooks/useWebSocket.ts:122-125]().
- `type: 'human_feedback'`: Triggers the feedback modal [frontend/nextjs/hooks/useWebSocket.ts:113-115]().

Sources: [frontend/nextjs/hooks/useWebSocket.ts:45-150](), [frontend/nextjs/helpers/getHost.ts:5-27]()

### API Host Resolution

The `getHost` helper determines the backend URL based on a priority system [frontend/nextjs/helpers/getHost.ts:8-25]():
1. `localStorage` key `GPTR_API_URL` [frontend/nextjs/helpers/getHost.ts:8-8]()
2. URL Query Parameter `GPTR_API_URL` [frontend/nextjs/helpers/getHost.ts:11-11]()
3. Environment variable `NEXT_PUBLIC_GPTR_API_URL` [frontend/nextjs/helpers/getHost.ts:17-18]()
4. Environment variable `REACT_APP_GPTR_API_URL` [frontend/nextjs/helpers/getHost.ts:19-20]()
5. Default to `http://localhost:8000` (development) or `https://${host}` (production) [frontend/nextjs/helpers/getHost.ts:24-25]()

Sources: [frontend/nextjs/helpers/getHost.ts:5-27]()

## Key Components

### Hero and InputArea

The `Hero` component provides an immersive entry point with an animated particle background [frontend/nextjs/components/Hero.tsx:24-56](). It wraps the `InputArea` component.

`InputArea` [frontend/nextjs/components/ResearchBlocks/elements/InputArea.tsx:28-36]() features:
- **Auto-height adjustment**: Uses a `debounce` function to resize the textarea based on content [frontend/nextjs/components/ResearchBlocks/elements/InputArea.tsx:54-57]().
- **Submission**: Handles `Enter` key (without Shift) to trigger `handleSubmit` [frontend/nextjs/components/ResearchBlocks/elements/InputArea.tsx:65-79]().
- **Visuals**: Glassmorphism effects with teal/cyan gradients [frontend/nextjs/components/ResearchBlocks/elements/InputArea.tsx:87-111]().

Sources: [frontend/nextjs/components/Hero.tsx:106-121](), [frontend/nextjs/components/ResearchBlocks/elements/InputArea.tsx:16-26]()

### Settings Modal and ResearchForm

The `Modal` component [frontend/nextjs/components/Settings/Modal.tsx:17-17]() provides the interface for advanced configuration.

`ResearchForm` [frontend/nextjs/components/Task/ResearchForm.tsx:21-25]() allows users to toggle:
- **Report Type**: Options include `research_report`, `deep`, `multi_agents`, and `detailed_report` [frontend/nextjs/components/Task/ResearchForm.tsx:122-130]().
- **Source**: Choice between `web`, `local` (documents), or `hybrid` [frontend/nextjs/components/Task/ResearchForm.tsx:144-147]().
- **Domain Filtering**: Users can specify allowed domains for web searches [frontend/nextjs/components/Task/ResearchForm.tsx:167-175]().
- **MCP**: Toggle for Model Context Protocol servers [frontend/nextjs/components/Task/ResearchForm.tsx:158-162]().

Sources: [frontend/nextjs/components/Settings/Modal.tsx:55-63](), [frontend/nextjs/components/Task/ResearchForm.tsx:106-176]()

### ResearchSidebar (History Management)

The sidebar displays a list of past research sessions [frontend/nextjs/components/ResearchSidebar.tsx:16-23]().

```mermaid
graph LR
    subgraph "History Flow"
        LS["localStorage: 'research-history'"]
        Ctx["ResearchHistoryContext"]
        Sidebar["ResearchSidebar"]
    end
    
    LS -->|Load| Ctx
    Ctx -->|history array| Sidebar
    Sidebar -->|onSelectResearch| page["Update page state"]
    Sidebar -->|onDeleteResearch| Ctx -->|Update| LS
```

It uses `formatDistanceToNow` from `date-fns` to show relative timestamps for history items [frontend/nextjs/components/ResearchSidebar.tsx:44-54]().

Sources: [frontend/nextjs/components/ResearchSidebar.tsx:73-100](), [frontend/nextjs/app/page.tsx:98-106]()

## Data Processing Pipeline

Before rendering, the raw stream of messages from the WebSocket is processed to improve readability.

```mermaid
graph TD
    WS["WebSocket Raw Message"] --> Parse["JSON.parse()"]
    Parse --> Accumulate["orderedData Array"]
    Accumulate --> Preprocess["preprocessOrderedData()"]
    Preprocess --> Group["Group logs into Accordions"]
    Group --> Render["ResearchResults Component"]
```

The `preprocessOrderedData` utility in [frontend/nextjs/utils/dataProcessing.ts:4-4]() groups sequential "logs" (agent steps) into expandable accordion blocks while keeping the final "report" and "chat" types distinct. It also consolidates source and image blocks [frontend/nextjs/utils/dataProcessing.ts:127-127]().

Sources: [frontend/nextjs/app/page.tsx:225-240](), [frontend/nextjs/utils/dataProcessing.ts:4-129](), [frontend/nextjs/hooks/useWebSocket.ts:102-133]()

## Deployment and Environment

### Environment Variables

The frontend relies on the following environment variables:
- `NEXT_PUBLIC_GPTR_API_URL`: The base URL for the FastAPI backend [frontend/nextjs/helpers/getHost.ts:17-18]().
- `NEXT_PUBLIC_GA_MEASUREMENT_ID`: Google Analytics ID for tracking [frontend/nextjs/docs/docs/gpt-researcher/frontend/nextjs-frontend.md:98-98]().

### Build Scripts

Defined in [frontend/nextjs/package.json:15-23]():
- `npm run dev`: Starts the Next.js development server.
- `npm run build`: Creates an optimized production build.
- `npm run start`: Runs the production server.
- `npm run build:lib`: Uses Rollup to bundle the frontend as a library (CommonJS and ESM) for embedding [frontend/nextjs/rollup.config.js:21-32]().

Sources: [frontend/nextjs/package.json:15-23](), [frontend/nextjs/helpers/getHost.ts:1-27](), [frontend/nextjs/rollup.config.js:1-84]()

---

# Page: Vanilla JS Lightweight Frontend

# Vanilla JS Lightweight Frontend

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/report_type/basic_report/basic_report.py](backend/report_type/basic_report/basic_report.py)
- [backend/report_type/detailed_report/detailed_report.py](backend/report_type/detailed_report/detailed_report.py)
- [backend/server/multi_agent_runner.py](backend/server/multi_agent_runner.py)
- [backend/server/server_utils.py](backend/server/server_utils.py)
- [backend/server/websocket_manager.py](backend/server/websocket_manager.py)
- [docs/docs/gpt-researcher/frontend/nextjs-frontend.md](docs/docs/gpt-researcher/frontend/nextjs-frontend.md)
- [docs/docs/gpt-researcher/frontend/vanilla-js-frontend.md](docs/docs/gpt-researcher/frontend/vanilla-js-frontend.md)
- [frontend/index.html](frontend/index.html)
- [frontend/nextjs/utils/consolidateBlocks.ts](frontend/nextjs/utils/consolidateBlocks.ts)
- [frontend/nextjs/utils/dataProcessing.ts](frontend/nextjs/utils/dataProcessing.ts)
- [frontend/scripts.js](frontend/scripts.js)
- [frontend/styles.css](frontend/styles.css)
- [tests/test_websocket_manager.py](tests/test_websocket_manager.py)

</details>



## Purpose and Scope

The Vanilla JS Lightweight Frontend is a static HTML/CSS/JavaScript interface for GPT Researcher that provides a simple, dependency-free alternative to the NextJS production frontend. It is served directly by the FastAPI backend (typically on port 8000) and communicates via WebSocket for real-time research streaming.

This frontend is designed for developers who prefer a minimal footprint without a Node.js build process. It supports core features including multi-type report generation, Model Context Protocol (MCP) configuration, domain filtering, and research history persistence.

**Sources:** [frontend/index.html:1-15](), [frontend/scripts.js:1-12](), [docs/docs/gpt-researcher/frontend/vanilla-js-frontend.md:1-25]()

## Architecture Overview

The vanilla JS frontend is a self-contained client application consisting of static files served by FastAPI's static file mounting. Unlike the NextJS frontend, it does not require a separate server process.

### System Component Interaction
The following diagram illustrates how the Vanilla JS entities interact with the FastAPI backend entities.

```mermaid
graph TB
    subgraph "Client Browser (Vanilla JS Space)"
        Index["index.html"]
        Styles["styles.css"]
        Scripts["scripts.js (GPTResearcher IIFE)"]
        WSClient["WebSocket Client"]
    end
    
    subgraph "FastAPI Backend (Python Space)"
        Static["StaticFiles Mount ('/site')"]
        WSManager["WebSocketManager Class"]
        SrvUtils["server_utils.py Functions"]
        LogsHandler["CustomLogsHandler Class"]
    end
    
    subgraph "Research Logic"
        Basic["BasicReport Class"]
        Detailed["DetailedReport Class"]
    end
    
    Index --> Static
    Scripts --> WSClient
    WSClient <==>|"ws://host/ws"| WSManager
    WSManager --> LogsHandler
    LogsHandler --> Basic
    LogsHandler --> Detailed
    WSManager --> SrvUtils
```

**Sources:** [frontend/index.html:14-15](), [backend/server/websocket_manager.py:19-27](), [backend/server/server_utils.py:33-81]()

## UI Components and Implementation

### Research Configuration Form
The main interface is driven by `form#researchForm` [frontend/index.html:154](). It captures parameters that are mapped to the `GPTResearcher` backend class via a JSON payload.

| UI Element | Code ID | Backend Parameter |
|:---|:---|:---|
| Task Input | `textarea#task` | `query` |
| Report Type | `select#report_type` | `report_type` |
| Tone | `select#tone` | `tone` |
| Source | `select#report_source` | `report_source` |
| Domains | `input#query_domains` | `query_domains` |
| Max Search Results | `input#max_search_results` | `max_search_results` |

**Sources:** [frontend/index.html:154-220](), [backend/server/server_utils.py:126-141](), [backend/report_type/detailed_report/detailed_report.py:27-28]()

### WebSocket Status Panel
A dedicated monitoring panel [frontend/index.html:88-134]() provides technical insights into the connection state. It is managed by `initWebSocketPanel` in the frontend and `WebSocketManager` in the backend.

```mermaid
graph LR
    UI["websocketPanel"] --- State["scripts.js State"]
    State --- Socket["WebSocket.readyState"]
    
    subgraph "Monitored Metrics"
        M1["connectionStatus"]
        M2["messagesReceived"]
        M3["connectionDuration"]
        M4["lastActivity"]
    end
    
    Socket --> M1
    State --> M2
    State --> M3
    State --> M4
```

**Sources:** [frontend/index.html:88-134](), [frontend/scripts.js:61-62](), [backend/server/websocket_manager.py:21-65]()

## Data Flow and WebSocket Protocol

### The "Start" Command
When a user submits the form, `GPTResearcher.startResearch()` is invoked via an event listener [frontend/scripts.js:38-42](). It constructs a string command prefixed with `start ` followed by a JSON string.

The backend receives this in `handle_start_command` [backend/server/server_utils.py:126](), which extracts data using `extract_command_data` and initiates streaming via `manager.start_streaming` [backend/server/server_utils.py:159-173]().

**Sources:** [frontend/scripts.js:38-42](), [backend/server/server_utils.py:126-173](), [backend/server/websocket_manager.py:101-114]()

### Streaming Response Handling
The backend streams updates using `CustomLogsHandler.send_json` [backend/server/server_utils.py:56](). This class handles real-time WebSocket transmission and persists logs to the `outputs/` directory [backend/server/server_utils.py:38-44]().

| Message Type | Frontend Action | Code Reference |
|:---|:---|:---|
| `logs` | Displays research progress/events | [backend/server/server_utils.py:67-72]() |
| `chat` | Handles AI assistant responses | [backend/server/server_utils.py:187-210]() |
| `path` | Provides download links for generated files | [backend/server/server_utils.py:175-178]() |

**Sources:** [backend/server/server_utils.py:56-80](), [backend/server/server_utils.py:187-210]()

## State and History Management

The frontend maintains a `conversationHistory` array [frontend/scripts.js:4]() that persists across sessions using browser cookies with a fallback to `localStorage` [frontend/scripts.js:82-104]().

### History Persistence Logic
1. **Loading:** `loadConversationHistory()` is called during `init()` [frontend/scripts.js:30](). It populates the history panel sidebar [frontend/index.html:82]().
2. **Filtering:** `filterHistoryEntries` allows users to search through past research tasks [frontend/scripts.js:145]().
3. **Storage Status:** `checkCookieStatus` provides debugging information regarding the storage backend (Cookies vs LocalStorage) [frontend/scripts.js:190]().

**Sources:** [frontend/scripts.js:4-30](), [frontend/scripts.js:82-104](), [frontend/scripts.js:145-190]()

## MCP (Model Context Protocol) Integration

The frontend includes a specialized section for MCP configuration. It allows users to enable MCP and provide a JSON configuration for servers.

### MCP Configuration Flow
1. **Initialization:** `initMCPSection()` is called during startup [frontend/scripts.js:64]().
2. **Execution:** If `mcp_enabled` is true, the `run_agent` function in the backend logs the initialization and passes the `mcp_configs` and `mcp_strategy` to the `DetailedReport` or `BasicReport` classes [backend/server/websocket_manager.py:125-131]().
3. **Propagation:** For detailed reports, MCP settings are propagated to subtopic researchers to ensure consistent context retrieval [backend/report_type/detailed_report/detailed_report.py:155-157]().

**Sources:** [frontend/scripts.js:64](), [backend/server/websocket_manager.py:125-158](), [backend/report_type/detailed_report/detailed_report.py:155-157]()

## Key JavaScript Functions

| Function | Role | Source |
|:---|:---|:---|
| `init()` | Bootstraps event listeners, history, and WebSocket monitoring. | [frontend/scripts.js:25-79]() |
| `checkCookiesEnabled()` | Determines if browser cookies are available for history storage. | [frontend/scripts.js:82-104]() |
| `initHistoryPanel()` | Sets up sidebar toggles, search, and export/import actions. | [frontend/scripts.js:107-197]() |
| `updateState(state)` | Manages UI visibility and transitions. | [frontend/scripts.js:69]() |

**Sources:** [frontend/scripts.js:25-197]()

---

# Page: Embed Script Integration

# Embed Script Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/gpt-researcher/context/filtering-by-domain.md](docs/docs/gpt-researcher/context/filtering-by-domain.md)
- [docs/docs/gpt-researcher/frontend/embed-script.md](docs/docs/gpt-researcher/frontend/embed-script.md)
- [docs/docs/gpt-researcher/gptr/querying-the-backend.md](docs/docs/gpt-researcher/gptr/querying-the-backend.md)
- [docs/npm/Readme.md](docs/npm/Readme.md)
- [docs/npm/index.js](docs/npm/index.js)
- [docs/npm/package.json](docs/npm/package.json)
- [frontend/nextjs/public/embed.js](frontend/nextjs/public/embed.js)
- [frontend/nextjs/src/utils/imageTransformPlugin.js](frontend/nextjs/src/utils/imageTransformPlugin.js)

</details>



## Purpose and Scope

This document describes the `embed.js` script that enables integration of the GPT Researcher NextJS frontend into external web applications. The script provides a simple JavaScript API for embedding the full-featured research interface via an iframe, allowing third-party applications to leverage GPT Researcher's capabilities without implementing their own UI.

For information about the embedded NextJS frontend itself, see [NextJS Production Frontend](#8.2). For details on backend communication protocols, see [FastAPI Backend and WebSocket API](#8.1). For frontend state management within the embedded application, see [Frontend State and History Management](#8.5).

---

## Architecture Overview

The embed script uses an **iframe-based embedding strategy** to isolate the GPT Researcher frontend while providing a clean integration API for host applications.

**System Entity Mapping: Embed Architecture**

```mermaid
graph TB
    subgraph "Host Application Space"
        HostApp["Host Application<br/>(Third-party Website)"]
        EmbedScript["embed.js Script<br/>window.GPTResearcher API"]
        Container["div#gpt-researcher-container<br/>(DOM Container)"]
        LocalStorage["localStorage<br/>GPTR_API_URL"]
    end

    subgraph "Code Entity Space"
        Iframe["HTMLIFrameElement<br/>src: https://gptr.app"]
        NextJSApp["NextJS Frontend<br/>(Embedded Application)"]
        Backend["FastAPI Backend<br/>(main.py / uvicorn)"]
        WebSocket["WebSocket Connection<br/>/ws"]
    end
    
    HostApp -->|"1. Includes script tag"| EmbedScript
    EmbedScript -->|"2. Reads API URL"| LocalStorage
    EmbedScript -->|"3. document.createElement"| Container
    Container -->|"4. appendChild"| Iframe
    Iframe -->|"5. Loads"| NextJSApp
    HostApp -->|"6. setItem()"| LocalStorage
    NextJSApp -->|"7. Establish"| WebSocket
    WebSocket -->|"8. Communicates with"| Backend
```

**Sources:** [frontend/nextjs/public/embed.js:1-68](), [docs/docs/gpt-researcher/frontend/embed-script.md:1-28]()

The architecture separates concerns:
- **Host Application**: The third-party website integrating GPT Researcher.
- **Embed Script**: The integration layer providing the JavaScript API.
- **Iframe Isolation**: Sandboxed environment for the NextJS frontend.
- **Backend Configuration**: Flexible API endpoint selection via `localStorage` or URL parameters.

---

## Global API Object

The embed script exposes a global `window.GPTResearcher` object with two primary methods.

### GPTResearcher.init()

Creates the embedding infrastructure automatically when the script loads.

**Execution Logic: init() Method**

```mermaid
flowchart TD
    Start["init() Called"] --> ReadLS["localStorage.getItem('GPTR_API_URL')"]
    ReadLS --> CreateContainer["Create div#gpt-researcher-container<br/>Width: 100%, Height: 100vh"]
    CreateContainer --> CreateIframe["Create iframe element<br/>src: https://gptr.app + ?GPTR_API_URL=..."]
    CreateIframe --> ApplyStyles["Inject CSS style contentText<br/>(Hide scrollbars)"]
    ApplyStyles --> InsertDOM["parentNode.insertBefore(container, currentScript)"]
    InsertDOM --> AddListeners["window.addEventListener('resize')"]
    AddListeners --> End["Iframe loads NextJS app"]
```

**Sources:** [frontend/nextjs/public/embed.js:3-54]()

**Implementation Details:**

| Step | Action | Code Reference |
|------|--------|----------------|
| 1 | Read API URL from `localStorage` | [frontend/nextjs/public/embed.js:4]() |
| 2 | Create container div with ID `gpt-researcher-container` | [frontend/nextjs/public/embed.js:7-11]() |
| 3 | Create iframe with source `https://gptr.app` | [frontend/nextjs/public/embed.js:14-19]() |
| 4 | Append query parameter if `parentApiUrl` exists | [frontend/nextjs/public/embed.js:15]() |
| 5 | Inject CSS to hide scrollbars via `document.head.appendChild` | [frontend/nextjs/public/embed.js:22-39]() |
| 6 | Insert container into DOM before the script tag | [frontend/nextjs/public/embed.js:42-43]() |
| 7 | Attach `resize` and `load` event handlers to maintain height | [frontend/nextjs/public/embed.js:45-53]() |

### GPTResearcher.configure()

Allows runtime configuration of the embedded interface dimensions.

```javascript
GPTResearcher.configure({ height: 600 })
```

**Current Configuration Options:**

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `height` | number | Height of iframe in pixels | `100vh` (full viewport) |

**Sources:** [frontend/nextjs/public/embed.js:56-64]()

The `configure()` method queries the DOM for the iframe within `#gpt-researcher-container` and applies the specified height. This allows host applications to dynamically adjust the embedded interface dimensions after initialization.

---

## Integration Workflow

The following sequence diagram illustrates the initialization and data flow from the host application to the research backend.

```mermaid
sequenceDiagram
    participant Host as Host Application
    participant LS as localStorage
    participant Script as embed.js
    participant DOM as Document
    participant Iframe as Iframe
    participant NextJS as NextJS Frontend
    participant Backend as FastAPI Backend
    
    Host->>LS: setItem("GPTR_API_URL", "http://localhost:8000")
    Host->>DOM: Add <script src="embed.js">
    DOM->>Script: Load and execute IIFE
    Script->>LS: getItem("GPTR_API_URL")
    LS-->>Script: "http://localhost:8000"
    Script->>DOM: Create #gpt-researcher-container
    Script->>DOM: Inject CSS styles
    Script->>Iframe: Create with src="https://gptr.app?GPTR_API_URL=..."
    Script->>DOM: Insert container before script tag
    Iframe->>NextJS: Load application
    NextJS->>NextJS: Parse GPTR_API_URL from URL params
    NextJS->>Backend: Connect via WebSocket /ws
    Backend-->>NextJS: Stream research logs/results
    NextJS-->>Host: Display in iframe
```

**Sources:** [frontend/nextjs/public/embed.js:1-68](), [docs/docs/gpt-researcher/frontend/embed-script.md:1-28]()

---

## Backend Configuration

The embed script supports two methods for specifying the FastAPI backend URL.

### Method 1: localStorage (Recommended)

Set the `GPTR_API_URL` key before loading the embed script. This is the standard way to point the embedded frontend at a custom GPTR API Server.

```html
<script>localStorage.setItem("GPTR_API_URL", "http://localhost:8000");</script>
<script src="https://app.gptr.dev/embed.js"></script>
```

**Sources:** [docs/docs/gpt-researcher/frontend/embed-script.md:8-10]()

### Method 2: Default Hosted Backend

If `GPTR_API_URL` is not set in `localStorage`, the script defaults to the hosted environment at `https://gptr.app`.

**Sources:** [frontend/nextjs/public/embed.js:4-15]()

The API URL is passed to the embedded NextJS application as a query parameter: `?GPTR_API_URL=<url>`. The NextJS frontend reads this parameter to establish its communication channels.

---

## Domain Filtering Integration

When embedding GPT Researcher, users can also pass domain filters via URL parameters. This allows for tailored research agents restricted to specific sources.

| Parameter | Example | Effect |
|-----------|---------|--------|
| `domains` | `wikipedia.org` | Filters search results to a single domain |
| `domains` | `wired.com,forbes.com` | Filters search results to multiple domains |

**Sources:** [docs/docs/gpt-researcher/context/filtering-by-domain.md:47-62]()

---

## DOM Structure and Styling

The embed script creates a specific hierarchy to ensure the research interface occupies the intended space without interfering with the host's layout.

### Container and Iframe Properties

| Element | Property | Value | Purpose |
|---------|----------|-------|---------|
| **Container** | `id` | `gpt-researcher-container` | Target for CSS and JS manipulation |
| | `width` | `100%` | Occupy full width of parent |
| | `height` | `100vh` | Default to full viewport height |
| | `overflow` | `hidden` | Prevent container scrollbars |
| **Iframe** | `src` | `https://gptr.app...` | Target application URL |
| | `border` | `none` | Seamless integration |
| | `height` | `100%` | Fill the container |

**Sources:** [frontend/nextjs/public/embed.js:7-20]()

### Scrollbar Suppression

The script injects a `<style>` block into the `document.head` to ensure that scrollbars are hidden across all major browsers (Chrome, Safari, Firefox, IE, Edge) for both the container and the iframe.

**Sources:** [frontend/nextjs/public/embed.js:22-39]()

---

## Minimal Integration Example

A complete, valid HTML document demonstrating the integration:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GPT Researcher Embed Demo</title>
</head>
<body style="margin: 0; padding: 0;">
    <!-- Set backend URL and load the script -->
    <script>localStorage.setItem("GPTR_API_URL", "http://localhost:8000");</script>
    <script src="https://app.gptr.dev/embed.js"></script>
</body>
</html>
```

**Sources:** [docs/docs/gpt-researcher/frontend/embed-script.md:14-28]()

---

## Responsive Behavior

The script includes lifecycle event listeners to maintain the iframe's responsiveness:

1.  **Resize Listener**: Listens for `window.addEventListener("resize")` to reset `iframe.style.height` to `100%`. [frontend/nextjs/public/embed.js:46-48]()
2.  **Load Listener**: Ensures height is set correctly immediately after the iframe content finishes loading. [frontend/nextjs/public/embed.js:51-53]()

---

## Asset Management

When embedding the application, internal image paths are automatically transformed to point to the hosted domain (`https://gptr.app`) using a dedicated plugin `imageTransformPlugin` to ensure assets resolve correctly regardless of where the app is embedded.

**Sources:** [frontend/nextjs/src/utils/imageTransformPlugin.js:2-16]()

---

# Page: Frontend State and History Management

# Frontend State and History Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [frontend/nextjs/app/page.tsx](frontend/nextjs/app/page.tsx)
- [frontend/nextjs/components/Footer.tsx](frontend/nextjs/components/Footer.tsx)
- [frontend/nextjs/components/Header.tsx](frontend/nextjs/components/Header.tsx)
- [frontend/nextjs/components/Hero.tsx](frontend/nextjs/components/Hero.tsx)
- [frontend/nextjs/components/ResearchBlocks/AccessReport.tsx](frontend/nextjs/components/ResearchBlocks/AccessReport.tsx)
- [frontend/nextjs/components/ResearchBlocks/elements/InputArea.tsx](frontend/nextjs/components/ResearchBlocks/elements/InputArea.tsx)
- [frontend/nextjs/components/ResearchSidebar.tsx](frontend/nextjs/components/ResearchSidebar.tsx)
- [frontend/nextjs/components/Settings/ChatBox.tsx](frontend/nextjs/components/Settings/ChatBox.tsx)
- [frontend/nextjs/components/Settings/MCPSelector.tsx](frontend/nextjs/components/Settings/MCPSelector.tsx)
- [frontend/nextjs/components/Task/DomainFilter.tsx](frontend/nextjs/components/Task/DomainFilter.tsx)
- [frontend/nextjs/components/Task/ResearchForm.tsx](frontend/nextjs/components/Task/ResearchForm.tsx)
- [frontend/nextjs/hooks/useWebSocket.ts](frontend/nextjs/hooks/useWebSocket.ts)
- [frontend/nextjs/types/data.ts](frontend/nextjs/types/data.ts)

</details>



## Purpose and Scope

This document explains how the GPT Researcher frontends (primarily the Next.js production interface) manage research state and history persistence. It covers the state management architecture, storage mechanisms (`localStorage`), CRUD operations on research history, and the UI components that interact with saved research.

For information about how research data is processed and streamed from the backend, see [Frontend Data Processing](#8.6). For details about the backend WebSocket communication protocol, see [FastAPI Backend and WebSocket API](#8.1).

---

## State Management Architecture

The Next.js frontend utilizes a combination of React's `useState` hooks for ephemeral session state and a specialized `ResearchHistoryContext` for persistent history management [frontend/nextjs/app/page.tsx:28-106]().

### Next.js State Management Architecture

The architecture centralizes history logic in a context provider, allowing components like the `ResearchSidebar` and the main `Home` page to stay synchronized.

```mermaid
graph TB
    subgraph "React Component Tree"
        PageTSX["page.tsx (Home)"]
        ResearchSidebar["ResearchSidebar.tsx"]
        Hero["Hero.tsx"]
        ResearchForm["ResearchForm.tsx"]
    end
    
    subgraph "State Management Layer"
        HistoryContext["ResearchHistoryContext"]
        LocalState["useState Hooks"]
    end
    
    subgraph "Persistence Layer"
        LocalStorage["localStorage (researchHistory)"]
        ChatSettings["localStorage (chatBoxSettings)"]
        DomainFilters["localStorage (domainFilters)"]
    end
    
    subgraph "State Objects"
        HistoryArray["history: ResearchHistoryItem[]"]
        CurrentResearch["currentResearchId: string"]
        OrderedData["orderedData: Data[]"]
        SettingsObj["chatBoxSettings: ChatBoxSettings"]
    end
    
    PageTSX --> LocalState
    PageTSX --> HistoryContext
    ResearchSidebar --> HistoryContext
    ResearchForm --> SettingsObj
    
    LocalState --> CurrentResearch
    LocalState --> OrderedData
    LocalState --> SettingsObj
    
    HistoryContext --> HistoryArray
    HistoryContext --> LocalStorage
    
    ChatSettings -.->|initializes| SettingsObj
    DomainFilters -.->|initializes| ResearchForm
```

**Sources:** [frontend/nextjs/app/page.tsx:28-106](), [frontend/nextjs/components/ResearchSidebar.tsx:7-23](), [frontend/nextjs/components/Task/ResearchForm.tsx:33-47]()

---

## Research History Data Structures

### ResearchHistoryItem Interface

The frontend uses TypeScript interfaces to define the structure of research history items. This structure includes the original question, the generated report, and the full sequence of logs and sources received during the session.

```typescript
// Defined in types/data.ts
export interface ResearchHistoryItem {
  id: string;              // Unique identifier (UUID or timestamp)
  question: string;        // User's research query
  answer: string;          // Generated research report
  timestamp: number;       // Creation/update timestamp
  orderedData: Data[];     // Structured research data (logs, sources, etc.)
  chatMessages?: ChatMessage[];  // Associated chat history
}
```

The `orderedData` array stores objects of type `Data`, which are processed via `preprocessOrderedData` [frontend/nextjs/utils/dataProcessing.ts:11-129]() to group related information like sources and images.

**Sources:** [frontend/nextjs/types/data.ts:64-71](), [frontend/nextjs/app/page.tsx:10-11]()

---

## Storage Mechanisms

### localStorage Usage

The Next.js frontend uses `localStorage` for persisting research history, user configuration settings, and API variables.

1.  **Research History**: Managed via `useResearchHistoryContext`, which provides methods to `saveResearch`, `updateResearch`, and `deleteResearch` [frontend/nextjs/app/page.tsx:98-106]().
2.  **Settings Persistence**: The `chatBoxSettings` state (report type, source, tone, MCP settings) is initialized by reading `chatBoxSettings` from `localStorage` [frontend/nextjs/app/page.tsx:36-66]().
3.  **Domain Filtering**: Selected domains are stored in `domainFilters` and synced between the `ResearchForm` and `localStorage` [frontend/nextjs/components/Task/ResearchForm.tsx:33-47]().
4.  **API Configuration**: The `useWebSocket` hook retrieves `apiVariables` from `localStorage` to configure the connection [frontend/nextjs/hooks/useWebSocket.ts:55-56]().

```mermaid
graph LR
    subgraph "Storage Keys"
        H["'researchHistory'"]
        S["'chatBoxSettings'"]
        D["'domainFilters'"]
        A["'apiVariables'"]
    end

    subgraph "Consumer Components"
        HC["ResearchHistoryContext"]
        Home["Home (page.tsx)"]
        RF["ResearchForm"]
        WS["useWebSocket Hook"]
    end

    HC <-->|CRUD| H
    Home -.->|Read on Mount| S
    RF <-->|Sync| D
    WS -.->|Read| A
```

**Sources:** [frontend/nextjs/app/page.tsx:52-64](), [frontend/nextjs/components/Task/ResearchForm.tsx:33-47](), [frontend/nextjs/hooks/useWebSocket.ts:55-56]()

---

## CRUD Operations on Research History

### Context-Based CRUD

The `Home` component interacts with history through hooks provided by the `ResearchHistoryContext` [frontend/nextjs/app/page.tsx:98-106]().

| Operation | Trigger | Code Reference |
| :--- | :--- | :--- |
| **Create** | Starting a new research task via `handleDisplayResult` | [frontend/nextjs/app/page.tsx:100]() |
| **Read** | `ResearchSidebar` mapping over `history` array | [frontend/nextjs/components/ResearchSidebar.tsx:17-23]() |
| **Update** | Adding chat messages or receiving new research data | [frontend/nextjs/app/page.tsx:101-106]() |
| **Delete** | Clicking the delete icon in `ResearchSidebar` | [frontend/nextjs/components/ResearchSidebar.tsx:11-20]() |

**Sources:** [frontend/nextjs/app/page.tsx:98-106](), [frontend/nextjs/components/ResearchSidebar.tsx:7-23]()

---

## History UI Components

### ResearchSidebar Component

The `ResearchSidebar` component is the primary interface for history management. It provides a sliding panel (managed by `framer-motion`) that lists previous research items [frontend/nextjs/components/ResearchSidebar.tsx:90-100]().

*   **Selection**: Clicking a history item triggers `onSelectResearch`, which loads the research data into the main view [frontend/nextjs/components/ResearchSidebar.tsx:18-19]().
*   **Deletion**: Each item has a delete action that calls `onDeleteResearch` [frontend/nextjs/components/ResearchSidebar.tsx:20-21]().
*   **Formatting**: Timestamps are formatted using `formatDistanceToNow` for human-readability [frontend/nextjs/components/ResearchSidebar.tsx:44-54]().
*   **Interactivity**: It handles "click outside" events to automatically close the sidebar [frontend/nextjs/components/ResearchSidebar.tsx:28-41]().

**Sources:** [frontend/nextjs/components/ResearchSidebar.tsx:1-155]()

---

## Chat and Settings State

### Settings Management

User preferences for research (e.g., `report_type`, `tone`, `mcp_enabled`) are stored in a `chatBoxSettings` object [frontend/nextjs/app/page.tsx:36-48](). 

*   **URL Parameter Integration**: The `Footer` component checks for `domains` in the URL query parameters and syncs them to `localStorage` as `domainFilters` [frontend/nextjs/components/Footer.tsx:14-24]().
*   **Form Control**: The `ResearchForm` component updates settings via `onFormChange`, `onToneChange`, and `onMCPChange` [frontend/nextjs/components/Task/ResearchForm.tsx:61-91]().
*   **MCP Configuration**: The `MCPSelector` manages complex JSON configurations for Model Context Protocol servers, validating them before updating state [frontend/nextjs/components/Settings/MCPSelector.tsx:52-92]().

### Chat History Persistence

Chat messages are treated as a sub-resource of a research session.
*   **User Messages**: Immediately added to `orderedData` for UI feedback and persisted via `addChatMessage` [frontend/nextjs/app/page.tsx:146-161]().
*   **AI Responses**: On mobile, responses are fetched via `/api/chat` and subsequently saved to history using `addChatMessage` [frontend/nextjs/app/page.tsx:164-190]().

**Sources:** [frontend/nextjs/app/page.tsx:36-66](), [frontend/nextjs/components/Task/ResearchForm.tsx:61-91](), [frontend/nextjs/components/Settings/MCPSelector.tsx:52-92]()

---

## State Reset and Cleanup

To start a "New Research" session, the frontend provides a mechanism to clear current session state without deleting history.

*   **Header Actions**: The `Header` component provides a "New Research" button that triggers `onNewResearch` [frontend/nextjs/components/Header.tsx:9-52]().
*   **State Clearing**: This typically resets `orderedData`, `answer`, `currentResearchId`, and `promptValue` to their default empty states in `page.tsx` [frontend/nextjs/app/page.tsx:28-75]().
*   **WebSocket Cleanup**: The `useWebSocket` hook includes a cleanup effect to close the socket and clear heartbeat intervals on unmount [frontend/nextjs/hooks/useWebSocket.ts:16-29]().

**Sources:** [frontend/nextjs/app/page.tsx:28-75](), [frontend/nextjs/components/Header.tsx:1-61](), [frontend/nextjs/hooks/useWebSocket.ts:16-29]()

---

# Page: Frontend Data Processing

# Frontend Data Processing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/gpt-researcher/frontend/nextjs-frontend.md](docs/docs/gpt-researcher/frontend/nextjs-frontend.md)
- [docs/docs/gpt-researcher/frontend/vanilla-js-frontend.md](docs/docs/gpt-researcher/frontend/vanilla-js-frontend.md)
- [frontend/nextjs/components/Images/ImageModal.tsx](frontend/nextjs/components/Images/ImageModal.tsx)
- [frontend/nextjs/components/Images/ImagesAlbum.tsx](frontend/nextjs/components/Images/ImagesAlbum.tsx)
- [frontend/nextjs/components/ResearchBlocks/AccessReport.tsx](frontend/nextjs/components/ResearchBlocks/AccessReport.tsx)
- [frontend/nextjs/components/ResearchBlocks/ImageSection.tsx](frontend/nextjs/components/ResearchBlocks/ImageSection.tsx)
- [frontend/nextjs/components/ResearchBlocks/LogsSection.tsx](frontend/nextjs/components/ResearchBlocks/LogsSection.tsx)
- [frontend/nextjs/components/ResearchBlocks/Question.tsx](frontend/nextjs/components/ResearchBlocks/Question.tsx)
- [frontend/nextjs/components/ResearchBlocks/Sources.tsx](frontend/nextjs/components/ResearchBlocks/Sources.tsx)
- [frontend/nextjs/components/ResearchBlocks/elements/SourceCard.tsx](frontend/nextjs/components/ResearchBlocks/elements/SourceCard.tsx)
- [frontend/nextjs/components/ResearchBlocks/elements/SubQuestions.tsx](frontend/nextjs/components/ResearchBlocks/elements/SubQuestions.tsx)
- [frontend/nextjs/components/ResearchResults.tsx](frontend/nextjs/components/ResearchResults.tsx)
- [frontend/nextjs/components/Settings/ChatBox.tsx](frontend/nextjs/components/Settings/ChatBox.tsx)
- [frontend/nextjs/components/Settings/MCPSelector.tsx](frontend/nextjs/components/Settings/MCPSelector.tsx)
- [frontend/nextjs/components/Task/DomainFilter.tsx](frontend/nextjs/components/Task/DomainFilter.tsx)
- [frontend/nextjs/components/Task/ResearchForm.tsx](frontend/nextjs/components/Task/ResearchForm.tsx)
- [frontend/nextjs/hooks/useWebSocket.ts](frontend/nextjs/hooks/useWebSocket.ts)
- [frontend/nextjs/types/data.ts](frontend/nextjs/types/data.ts)
- [frontend/nextjs/utils/consolidateBlocks.ts](frontend/nextjs/utils/consolidateBlocks.ts)
- [frontend/nextjs/utils/dataProcessing.ts](frontend/nextjs/utils/dataProcessing.ts)

</details>



This document covers the frontend data processing utilities that transform raw WebSocket stream data from the backend into structured, displayable content. These utilities handle grouping related data items, deduplicating sources and images, and organizing content into logical blocks for rendering.

## Purpose and Scope

The frontend receives a continuous stream of JSON objects from the backend via WebSocket connections. Each message has a `type` and `content` field, along with optional `output` and `metadata` fields [frontend/nextjs/hooks/useWebSocket.ts:109-118](). These raw messages must be:

1.  **Grouped** into logical blocks (e.g., all report chunks into a single report block).
2.  **Deduplicated** to prevent showing the same source URL or image multiple times.
3.  **Ordered** correctly to maintain the research narrative flow.
4.  **Consolidated** to present a clean, organized UI.

The primary processing functions are:
*   `preprocessOrderedData` - Main orchestrator that groups and orders data [frontend/nextjs/utils/dataProcessing.ts:4-129]().
*   `consolidateSourceAndImageBlocks` - Deduplicates and consolidates sources/images [frontend/nextjs/utils/consolidateBlocks.ts:1-35]().

Sources: [frontend/nextjs/utils/dataProcessing.ts:4-129](), [frontend/nextjs/utils/consolidateBlocks.ts:1-35](), [frontend/nextjs/hooks/useWebSocket.ts:102-133]()

## Data Flow Architecture

The following diagram illustrates how raw WebSocket data is transformed into UI components.

### Data Processing Pipeline
```mermaid
graph TB
    subgraph "Natural Language Space"
        UserQuery["User Research Query"]
        StreamText["Streaming Report Text"]
        LogText["'Searching for AI trends...'"]
    end

    subgraph "Code Entity Space"
        WS["WebSocket Message<br/>{type, content, output}"]
        OrderedData["orderedData State<br/>Data[] array"]
        PreProcess["preprocessOrderedData()"]
        Consolidate["consolidateSourceAndImageBlocks()"]
        GroupedData["Grouped Data Objects<br/>(reportBlock, sourceBlock)"]
        UI["React Components<br/>(Report.tsx, Sources.tsx)"]
    end

    UserQuery -.-> WS
    StreamText -.-> WS
    LogText -.-> WS
    
    WS --> OrderedData
    OrderedData --> PreProcess
    PreProcess --> Consolidate
    Consolidate --> GroupedData
    GroupedData --> UI
```
Sources: [frontend/nextjs/utils/dataProcessing.ts:4-129](), [frontend/nextjs/components/ResearchResults.tsx:33-85](), [frontend/nextjs/hooks/useWebSocket.ts:102-133]()

## preprocessOrderedData Function

The `preprocessOrderedData` function is the primary utility that transforms a flat array of data items into a structured representation [frontend/nextjs/utils/dataProcessing.ts:4-129]().

### Processing Logic Flow
```mermaid
graph TD
    Start["Input: data: Data[]"]
    Loop["Iterate each item"]
    
    TypeCheck{"Check item.type<br/>/ item.content"}
    
    Question["type === 'question'"] --> PushQ["Push {type: 'question'}"]
    
    Report["type === 'report'"] --> AggReport["Append output to<br/>currentReportGroup.content"]
    
    Complete["type === 'report_complete'"] --> OverwriteReport["Replace content with<br/>final output (with images)"]
    
    SourceURL["content === 'added_source_url'"] --> DedupeSource["Add to currentSourceGroup<br/>if URL not in seenUrls Set"]
    
    Subqueries["content === 'subqueries'"] --> SetIdx["Push item & track<br/>lastSubqueriesIndex"]
    
    Other["Default / Logs"] --> Accordion["If sources encountered,<br/>add to accordionBlock"]
    
    Consolidate["consolidateSourceAndImageBlocks()"]
    
    Start --> Loop
    Loop --> TypeCheck
    TypeCheck --> Question
    TypeCheck --> Report
    TypeCheck --> Complete
    TypeCheck --> SourceURL
    TypeCheck --> Subqueries
    TypeCheck --> Other
    
    PushQ --> Loop
    AggReport --> Loop
    OverwriteReport --> Loop
    DedupeSource --> Loop
    SetIdx --> Loop
    Accordion --> Loop
    
    Loop -->|Done| Consolidate
    Consolidate --> End["Return groupedData"]
```

### Key Implementation Details

*   **Report Aggregation**: Streaming chunks of type `report` are concatenated into a `reportBlock` [frontend/nextjs/utils/dataProcessing.ts:21-26](). When `report_complete` is received, the entire content is replaced to ensure the final version (often containing embedded images) is displayed [frontend/nextjs/utils/dataProcessing.ts:27-34]().
*   **Source Handling**: Individual URLs received via `added_source_url` are parsed to extract hostnames (e.g., removing `www.`) and stored in a `sourceBlock` [frontend/nextjs/utils/dataProcessing.ts:72-88]().
*   **Subquery Ordering**: The function tracks `lastSubqueriesIndex` to ensure that `sourceBlock` elements are inserted immediately after the research subqueries in the UI flow [frontend/nextjs/utils/dataProcessing.ts:64-69]().
*   **Human Feedback**: While not part of the grouping logic, the frontend handles feedback requests by monitoring `data.type === 'human_feedback'`, which triggers UI state changes for user input [frontend/nextjs/hooks/useWebSocket.ts:113-116]().

Sources: [frontend/nextjs/utils/dataProcessing.ts:15-125](), [frontend/nextjs/hooks/useWebSocket.ts:111-129]()

## consolidateSourceAndImageBlocks

After initial grouping, `consolidateSourceAndImageBlocks` performs a final pass to merge multiple disparate blocks of the same type into single, unified UI elements [frontend/nextjs/utils/consolidateBlocks.ts:1-35]().

### Consolidation Rules
1.  **Source Consolidation**: Extracts all `sourceBlock` items, flattens them, and performs a final deduplication by URL [frontend/nextjs/utils/consolidateBlocks.ts:3-11]().
2.  **Image Consolidation**: Collects all `imagesBlock` metadata (image URLs) into a single array for the gallery view [frontend/nextjs/utils/consolidateBlocks.ts:14-19]().
3.  **Re-assembly**: Removes all original small blocks and appends the unified `consolidatedSourceBlock` and `consolidatedImageBlock` to the end of the data array [frontend/nextjs/utils/consolidateBlocks.ts:21-34]().

Sources: [frontend/nextjs/utils/consolidateBlocks.ts:1-35]()

## Component Rendering

The processed data is rendered by the `ResearchResults` component, which maps the internal block types to specific React components [frontend/nextjs/components/ResearchResults.tsx:23-87]().

| Block Type | Component | Description |
| :--- | :--- | :--- |
| `question` | `Question` | Displays the original research task [frontend/nextjs/components/ResearchBlocks/Question.tsx:8-28](). |
| `sourceBlock` | `Sources` | Renders a grid of `SourceCard` elements with hostnames and links [frontend/nextjs/components/ResearchBlocks/Sources.tsx:5-79](). |
| `reportBlock` | `Report` | Renders the Markdown report using `markdown.css` styles [frontend/nextjs/components/ResearchBlocks/Report.tsx:3-4](). |
| `imagesBlock` | `ImageSection` | Displays the `ImagesAlbum` of generated or retrieved images [frontend/nextjs/components/ResearchBlocks/ImageSection.tsx:9-23](). |
| `path` | `AccessReport` | Provides download links for PDF, DocX, and JSON logs [frontend/nextjs/components/ResearchBlocks/AccessReport.tsx:17-107](). |

### Report Path Sanitization
The `AccessReport` component includes logic to sanitize paths received from the backend, ensuring they are correctly prefixed with `outputs/` and formatted as valid URLs relative to the host [frontend/nextjs/components/ResearchBlocks/AccessReport.tsx:20-40]().

### Styling and Markdown
The frontend uses a specialized `markdown.css` file to style the generated reports. It includes specific styling for:
*   **Tables**: Dark background with teal borders.
*   **Images**: Auto-scaled with shadow and border radius [frontend/nextjs/components/ResearchBlocks/ImageSection.tsx:11-21]().
*   **Logs**: A dedicated `LogsSection` provides a real-time view of agent activity, automatically scrolling to the bottom as new logs arrive [frontend/nextjs/components/ResearchBlocks/LogsSection.tsx:16-42]().

Sources: [frontend/nextjs/components/ResearchResults.tsx:33-85](), [frontend/nextjs/components/ResearchBlocks/AccessReport.tsx:20-40](), [frontend/nextjs/components/ResearchBlocks/LogsSection.tsx:16-42]()

---

# Page: Research Pipeline Internals

# Research Pipeline Internals

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/gpt-researcher/gptr/config.md](docs/docs/gpt-researcher/gptr/config.md)
- [gpt_researcher/actions/query_processing.py](gpt_researcher/actions/query_processing.py)
- [gpt_researcher/agent.py](gpt_researcher/agent.py)
- [gpt_researcher/config/variables/base.py](gpt_researcher/config/variables/base.py)
- [gpt_researcher/config/variables/default.py](gpt_researcher/config/variables/default.py)
- [gpt_researcher/skills/browser.py](gpt_researcher/skills/browser.py)
- [gpt_researcher/skills/researcher.py](gpt_researcher/skills/researcher.py)

</details>



This document describes the internal mechanisms of the GPT Researcher pipeline that transforms a user query into a comprehensive research report. It covers the technical implementation details of query decomposition, parallel data acquisition, context processing, source evaluation, and report synthesis.

For high-level workflow orchestration by the `ResearchConductor` class, see [ResearchConductor and Workflow](#3.2). For configuration of LLMs used throughout the pipeline, see [Three-Tier LLM Strategy](#6.3). For specific research operation modes, see [Research Modes](#4).

---

## Pipeline Architecture Overview

The research pipeline consists of six sequential stages, each managed by specialized skill classes. The `GPTResearcher` class [gpt_researcher/agent.py:36-168]() orchestrates these stages through two primary methods: `conduct_research()` [gpt_researcher/skills/researcher.py:89-211]() (via the `ResearchConductor`) and `write_report()` [gpt_researcher/skills/writer.py:49-123]().

### End-to-End Pipeline Flow

```mermaid
graph TB
    subgraph "Stage 1: Query Processing"
        UserQuery["User Query"]
        ChooseAgent["choose_agent()<br/>agent_creator.py"]
        PlanResearch["plan_research_outline()<br/>query_processing.py:112"]
        GenSubQueries["generate_sub_queries()<br/>STRATEGIC_LLM"]
    end
    
    subgraph "Stage 2: Parallel Acquisition"
        ParallelExec["asyncio.gather()<br/>researcher.py"]
        ProcessSubQuery["_process_sub_query()<br/>researcher.py"]
        ScrapeURLs["scrape_urls()<br/>web_scraping.py:12"]
        MCPResearch["_execute_mcp_research()<br/>researcher.py"]
    end
    
    subgraph "Stage 3: Context Processing"
        ContextCompressor["ContextCompressor<br/>compression.py"]
        SimilarContent["get_similar_content_by_query()<br/>context_manager.py:37"]
    end
    
    subgraph "Stage 4: Source Evaluation"
        CurateSources["curate_sources()<br/>curator.py:33"]
        SourceRanking["LLM-based ranking<br/>SMART_LLM"]
    end
    
    subgraph "Stage 5: Report Synthesis"
        ImagePlanning["plan_and_generate_images()<br/>ImageGenerator"]
        WriteReport["write_report()<br/>writer.py:49"]
        GenReport["generate_report()<br/>SMART_LLM"]
    end
    
    subgraph "Stage 6: Output"
        ReportMarkdown["Markdown Report"]
        FinalFormat["PDF/DOCX/JSON"]
    end
    
    UserQuery --> ChooseAgent
    ChooseAgent --> PlanResearch
    PlanResearch --> GenSubQueries
    
    GenSubQueries --> ParallelExec
    ParallelExec --> ProcessSubQuery
    ProcessSubQuery --> ScrapeURLs
    ProcessSubQuery --> MCPResearch
    
    ScrapeURLs --> ContextCompressor
    MCPResearch --> ContextCompressor
    ContextCompressor --> SimilarContent
    
    SimilarContent --> CurateSources
    CurateSources --> SourceRanking
    
    SourceRanking --> ImagePlanning
    ImagePlanning --> WriteReport
    WriteReport --> GenReport
    GenReport --> ReportMarkdown
    ReportMarkdown --> FinalFormat
```

**Sources:** [gpt_researcher/agent.py:36-168](), [gpt_researcher/skills/researcher.py:89-211](), [gpt_researcher/skills/writer.py:49-123]()

---

## Query Planning and Decomposition

The pipeline begins by analyzing the user query to generate focused sub-queries. This process uses the **Strategic LLM** tier with fallback to Smart LLM. For details, see [Query Planning and Decomposition](#9.1).

### Planning Process

The `plan_research_outline()` function [gpt_researcher/actions/query_processing.py:112-169]() coordinates query decomposition:

1.  **Initial Search**: Retrieves initial search results using `get_search_results` [gpt_researcher/actions/query_processing.py:12-35]().
2.  **Context Building**: Formats results as context for the planning LLM.
3.  **Sub-Query Generation**: Uses Strategic LLM (defined by `STRATEGIC_LLM` [gpt_researcher/config/variables/default.py:9]()) to generate sub-queries.
4.  **MCP Awareness**: Skips sub-query generation if MCP is the sole retriever [gpt_researcher/actions/query_processing.py:145-153]().

### Strategic LLM Usage with Fallback

```mermaid
graph LR
    PlanOutline["plan_research_outline()"]
    CheckMCP["Check retriever_names<br/>for 'mcp' only"]
    SkipSubQ["Return [query]<br/>Skip sub-queries"]
    GenSubQ["generate_sub_queries()"]
    TryStrategic["Try STRATEGIC_LLM<br/>gpt_researcher/actions/query_processing.py:72"]
    FallbackSmart["Fallback to SMART_LLM<br/>gpt_researcher/actions/query_processing.py:99"]
    
    PlanOutline --> CheckMCP
    CheckMCP -->|"MCP only"| SkipSubQ
    CheckMCP -->|"Web/Hybrid"| GenSubQ
    GenSubQ --> TryStrategic
    TryStrategic -->|"Error"| FallbackSmart
```

**Sources:** [gpt_researcher/actions/query_processing.py:112-169](), [gpt_researcher/config/variables/default.py:7-12]()

---

## Parallel Sub-Query Processing

Once sub-queries are generated, the pipeline executes them in parallel to maximize throughput. For details, see [Parallel Sub-Query Processing](#9.2).

### Parallel Execution Architecture

The `ResearchConductor` manages the execution of these queries [gpt_researcher/skills/researcher.py:21-47]().

1.  **Worker Pool**: A `WorkerPool` is initialized in `BrowserManager` [gpt_researcher/skills/browser.py:32-35]() to handle concurrent scraping.
2.  **Scraping**: `scrape_urls` [gpt_researcher/actions/web_scraping.py:12-42]() processes the URLs found for each sub-query.
3.  **MCP Integration**: If configured, `MCP_STRATEGY` [gpt_researcher/config/variables/default.py:44]() determines how tools are called (fast vs deep).

**Sources:** [gpt_researcher/skills/researcher.py:89-211](), [gpt_researcher/skills/browser.py:32-35](), [gpt_researcher/actions/web_scraping.py:12-42]()

---

## Context Management and Compression

After acquiring raw content, the pipeline compresses and filters it to stay within LLM token limits. For details, see [Context Management and Compression](#9.3).

### Compression Architecture

The `ContextManager` [gpt_researcher/skills/context_manager.py:18-35]() handles this stage:

| Compressor | Purpose | Code Reference |
| :---------------------- | :------------------------------------------ | :------------------------------------------ |
| `ContextCompressor` | Compresses scraped web content | [gpt_researcher/skills/context_manager.py:55-63]() |
| `VectorstoreCompressor` | Retrieves and compresses from vector stores | [gpt_researcher/skills/context_manager.py:82-86]() |
| `WrittenContentCompressor` | Matches new queries against already written sections | [gpt_researcher/skills/context_manager.py:146-154]() |

**Sources:** [gpt_researcher/skills/context_manager.py:18-155](), [gpt_researcher/config/variables/default.py:13-15]()

---

## Source Curation and Validation

The `SourceCurator` [gpt_researcher/skills/curator.py:15-31]() performs LLM-based ranking to select the highest-quality sources. For details, see [Source Curation and Validation](#9.4).

### Curation Flow

1.  **Evaluation**: LLM evaluates sources based on credibility and relevance [gpt_researcher/skills/curator.py:33-48]().
2.  **Ranking**: Sources are ranked using the `SMART_LLM` model [gpt_researcher/config/variables/default.py:8]().
3.  **Filtering**: The top `max_results` (default 10) are returned [gpt_researcher/skills/curator.py:36]().

**Sources:** [gpt_researcher/skills/curator.py:15-97](), [gpt_researcher/config/variables/default.py:8]()

---

## Report Generation and Formatting

The final stage synthesizes curated sources into a coherent report. For details, see [Report Generation and Formatting](#9.5).

### Report Generation Pipeline

The `ReportGenerator` [gpt_researcher/skills/writer.py:20-47]() manages the final output:

-   **Introduction**: Written using `write_introduction` [gpt_researcher/skills/writer.py:164-193]().
-   **Main Body**: Generated via `write_report` [gpt_researcher/skills/writer.py:49-123]().
-   **Conclusion**: Finalized using `write_report_conclusion` [gpt_researcher/skills/writer.py:125-162]().

**Sources:** [gpt_researcher/skills/writer.py:20-253](), [gpt_researcher/config/variables/default.py:20-21]()

---

## Image Generation System

The image generation system produces contextually relevant illustrations using Google Gemini or Imagen models. For details, see [Image Generation System](#9.6).

### Generation Strategy

1.  **Planning**: The `ImageGenerator` [gpt_researcher/skills/image_generator.py]() identifies sections that need visual aids.
2.  **Prompts**: `generate_image_analysis_prompt` [gpt_researcher/prompts.py:121-175]() creates the instructions for the image model.
3.  **Style**: Controlled by `IMAGE_GENERATION_STYLE` (dark/light/auto) [gpt_researcher/config/variables/default.py:53]().

**Sources:** [gpt_researcher/skills/image_generator.py](), [gpt_researcher/prompts.py:121-192](), [gpt_researcher/config/variables/default.py:47-53]()

---

# Page: Query Planning and Decomposition

# Query Planning and Decomposition

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.python-version](.python-version)
- [docs/docs/gpt-researcher/gptr/config.md](docs/docs/gpt-researcher/gptr/config.md)
- [gpt_researcher/actions/query_processing.py](gpt_researcher/actions/query_processing.py)
- [gpt_researcher/config/variables/base.py](gpt_researcher/config/variables/base.py)
- [gpt_researcher/config/variables/default.py](gpt_researcher/config/variables/default.py)
- [gpt_researcher/prompts.py](gpt_researcher/prompts.py)
- [gpt_researcher/utils/enum.py](gpt_researcher/utils/enum.py)
- [tests/test_quick_search.py](tests/test_quick_search.py)

</details>



## Purpose and Scope

This document explains how GPT Researcher decomposes user queries into executable research plans. The planning phase determines the research strategy by selecting an appropriate agent, gathering initial context, and generating focused sub-queries that guide parallel research execution. This process is primarily orchestrated by the `ResearchConductor` skill. For information about how these sub-queries are executed, see [Parallel Sub-Query Processing](9.2). For configuration of the models used in planning, see [Three-Tier LLM Strategy](6.3).

## Overview: From Query to Research Plan

Query planning transforms a single research question into a structured set of sub-queries that can be researched in parallel. This decomposition happens in three stages:

1.  **Agent Selection**: Choose a specialized research agent based on query characteristics.
2.  **Initial Search**: Gather preliminary context about the query domain to inform the plan.
3.  **Outline Planning**: Generate focused sub-queries using the `STRATEGIC_LLM`.

The planning process is managed by the `ResearchConductor` class and configured through settings like `STRATEGIC_LLM`, `REASONING_EFFORT`, and `MAX_ITERATIONS`.

Sources: [gpt_researcher/skills/researcher.py:1-87](), [gpt_researcher/actions/query_processing.py:112-169]()

## Query Planning Architecture

The following diagram illustrates the flow from a raw user query to a list of executable sub-queries, highlighting the interaction between the conductor and the strategic LLM.

```mermaid
graph TB
    subgraph "Natural Language Space"
        Query["User Query"]
        SubQueries["Sub-Query List"]
    end

    subgraph "Code Entity Space"
        ConductResearch["ResearchConductor.conduct_research()"]
        ChooseAgent["choose_agent()"]
        PlanResearch["ResearchConductor.plan_research()"]
        GetSearchResults["get_search_results()"]
        PlanOutline["plan_research_outline()"]
        GenSubQueries["generate_sub_queries()"]
        StrategicLLM["STRATEGIC_LLM<br/>(e.g., o4-mini)"]
        Config["Config Instance"]
    end
    
    Query --> ConductResearch
    ConductResearch --> ChooseAgent
    ConductResearch --> PlanResearch
    PlanResearch --> GetSearchResults
    PlanResearch --> PlanOutline
    GetSearchResults --> PlanOutline
    PlanOutline --> GenSubQueries
    GenSubQueries --> StrategicLLM
    StrategicLLM --> SubQueries
    
    Config -.->|"MAX_ITERATIONS"| GenSubQueries
    Config -.->|"REASONING_EFFORT"| StrategicLLM
```

**Diagram: Query Planning Pipeline**

The `ResearchConductor` coordinates planning by first gathering initial search results to provide context for the `STRATEGIC_LLM`, which then generates the research outline.

Sources: [gpt_researcher/skills/researcher.py:48-87](), [gpt_researcher/actions/query_processing.py:112-169](), [gpt_researcher/config/variables/default.py:9-12]()

## Agent Selection Process

Before generating sub-queries, GPT Researcher selects a specialized research agent tailored to the query domain. This is handled by the `choose_agent` action.

### Agent Selection Flow

```mermaid
graph TB
    subgraph "Natural Language Space"
        UserQuery["User Query"]
        AgentRole["'Finance Agent', 'Healthcare Researcher', etc."]
    end

    subgraph "Code Entity Space"
        AgentInit["GPTResearcher.__init__"]
        CondResearch["ResearchConductor.conduct_research()"]
        ChooseAgentFn["choose_agent()"]
        PromptFam["PromptFamily.auto_agent_instructions()"]
        SmartLLM["SMART_LLM<br/>(e.g., gpt-4.1)"]
        JsonRepair["json_repair.loads()"]
    end

    UserQuery --> CondResearch
    CondResearch --> ChooseAgentFn
    ChooseAgentFn --> PromptFam
    PromptFam --> SmartLLM
    SmartLLM --> JsonRepair
    JsonRepair --> AgentRole
    AgentRole --> AgentInit
```

**Diagram: Agent Selection Decision Tree**

The agent selection uses the `SMART_LLM` (defaulting to `gpt-4.1`) to analyze the query and return a JSON object containing the `agent_role_prompt`. If parsing fails, the system uses `json_repair` or falls back to a default "AI critical thinker" persona.

Sources: [gpt_researcher/actions/agent_creator.py:18-62](), [gpt_researcher/agent.py:119-127](), [gpt_researcher/config/variables/default.py:8]()

## Initial Search Phase

The planning process in `ResearchConductor.plan_research` begins by gathering initial context. This provides the LLM with real-world information about the query domain, allowing for more specific and relevant sub-query generation.

### Context Gathering Logic

The initial search uses only the first configured retriever to minimize latency:

```python
# gpt_researcher/skills/researcher.py:62
search_results = await get_search_results(query, self.researcher.retrievers[0], query_domains, researcher=self.researcher)
```

The results are passed to `plan_research_outline`, which serves as the bridge to sub-query generation.

Sources: [gpt_researcher/skills/researcher.py:48-87](), [gpt_researcher/actions/query_processing.py:12-35]()

## Research Outline Planning

With initial context gathered, the system generates a structured research outline by decomposing the query into focused sub-queries using the `STRATEGIC_LLM`.

### Sub-Query Generation Process

The `generate_sub_queries` function implements a robust fallback mechanism to ensure a research plan is always created:

1.  **Primary Attempt**: Calls `STRATEGIC_LLM` (e.g., `o4-mini`) with `REASONING_EFFORT` set to `medium`. [gpt_researcher/actions/query_processing.py:72-81]()
2.  **Token Limit Retry**: If the primary call fails (common with unbounded token requests on some providers), it retries using the `STRATEGIC_TOKEN_LIMIT`. [gpt_researcher/actions/query_processing.py:82-97]()
3.  **Smart LLM Fallback**: If strategic calls fail, it falls back to the `SMART_LLM` (e.g., `gpt-4.1`) with standard temperature settings. [gpt_researcher/actions/query_processing.py:98-108]()

Sources: [gpt_researcher/actions/query_processing.py:71-110](), [gpt_researcher/config/variables/default.py:9, 45]()

### Configuration Parameters

| Parameter | Default Value | Role in Planning |
| :--- | :--- | :--- |
| `STRATEGIC_LLM` | `openai:o4-mini` | Primary model for query decomposition [gpt_researcher/config/variables/default.py:9]() |
| `STRATEGIC_TOKEN_LIMIT` | `4000` | Token ceiling for planning responses [gpt_researcher/config/variables/default.py:12]() |
| `REASONING_EFFORT` | `medium` | Effort level for reasoning models (o1, o3, o4) [gpt_researcher/config/variables/default.py:45]() |
| `MAX_ITERATIONS` | `3` | Maximum number of sub-queries to generate [gpt_researcher/config/variables/default.py:22]() |
| `MAX_SUBTOPICS` | `3` | Limit for subtopic generation in detailed reports [gpt_researcher/config/variables/default.py:27]() |

Sources: [gpt_researcher/config/variables/default.py:9-12, 22, 27, 45]()

## Special Cases and Optimizations

### MCP Retriever Behavior

When Model Context Protocol (MCP) retrievers are configured, the query planning logic adapts. If MCP is the **only** retriever, the system skips sub-query generation entirely and uses the original query, as MCP servers often handle their own internal tool-calling and decomposition. [gpt_researcher/actions/query_processing.py:145-153]()

```python
# gpt_researcher/actions/query_processing.py:145-153
if retriever_names and ("mcp" in retriever_names or "MCPRetriever" in retriever_names):
    mcp_only = (len(retriever_names) == 1 and 
               ("mcp" in retriever_names or "MCPRetriever" in retriever_names))
    
    if mcp_only:
        logger.info("Using MCP retriever only - skipping sub-query generation")
        return [query]
```

Sources: [gpt_researcher/actions/query_processing.py:140-156](), [gpt_researcher/skills/researcher.py:129-133]()

### Detailed Report Subtopics

In `ReportType.DetailedReport` mode, the system uses subtopic construction to create a hierarchical plan. This involves generating a list of subtopics which are then individually researched as if they were standalone queries. This behavior is triggered by the `DetailedReport` enum value. [gpt_researcher/utils/enum.py:17, 25]()

Sources: [gpt_researcher/utils/enum.py:6-28](), [gpt_researcher/config/variables/default.py:27]()

## Integration with Research Execution

The output of the planning phase is a `List[str]` of sub-queries returned by `plan_research_outline`. [gpt_researcher/actions/query_processing.py:169]() The `ResearchConductor` then iterates through these queries to gather context:

1.  **Context Gathering**: Conducted via `_get_context_by_search` or specialized web/local methods.
2.  **Source Filtering**: If `REPORT_SOURCE` is set to `local` or `web`, the conductor directs retrieval accordingly. [gpt_researcher/config/variables/default.py:29]()
3.  **Aggregation**: All results are aggregated into the research context for the final report generation.

Sources: [gpt_researcher/skills/researcher.py:48-87](), [gpt_researcher/actions/query_processing.py:112-169]()

---

# Page: Parallel Sub-Query Processing

# Parallel Sub-Query Processing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/report_type/deep_research/example.py](backend/report_type/deep_research/example.py)
- [gpt_researcher/agent.py](gpt_researcher/agent.py)
- [gpt_researcher/skills/browser.py](gpt_researcher/skills/browser.py)
- [gpt_researcher/skills/deep_research.py](gpt_researcher/skills/deep_research.py)
- [gpt_researcher/skills/researcher.py](gpt_researcher/skills/researcher.py)
- [gpt_researcher/utils/rate_limiter.py](gpt_researcher/utils/rate_limiter.py)
- [gpt_researcher/utils/workers.py](gpt_researcher/utils/workers.py)
- [tests/test_deep_research_parsing.py](tests/test_deep_research_parsing.py)

</details>



## Purpose and Scope

This document explains how GPT Researcher executes multiple sub-queries concurrently to gather comprehensive research data efficiently. After query planning generates a list of sub-queries (see [9.1 Query Planning and Decomposition]), the system processes these queries in parallel to maximize throughput while managing API rate limits and resource constraints.

This page covers the parallel execution architecture, MCP (Model Context Protocol) strategy handling, result aggregation, and the coordination mechanisms that ensure efficient concurrent processing.

## Parallel Processing Architecture

The `ResearchConductor` class in [gpt_researcher/skills/researcher.py:21-32]() orchestrates parallel sub-query processing. The architecture separates concerns between MCP retrievers and traditional web retrievers, with configurable strategies for optimizing performance vs. thoroughness.

The main entry point for this parallel flow is `_get_context_by_web_search` [gpt_researcher/skills/researcher.py:266-266](), which coordinates the generation of sub-queries and their subsequent concurrent execution.

### System Entity Map: Research Conductor

```mermaid
graph TB
    subgraph "gpt_researcher/skills/researcher.py"
        RC["ResearchConductor Class"]
        GCBWS["_get_context_by_web_search()"]
        PSQ["_process_sub_query()"]
        EMR["_execute_mcp_research_for_queries()"]
        GMS["_get_mcp_strategy()"]
        CMAW["_combine_mcp_and_web_context()"]
    end
    
    subgraph "Execution & State"
        AG["asyncio.gather()"]
        MCPC["_mcp_results_cache"]
        WP["WorkerPool"]
    end
    
    subgraph "External Skills"
        BM["BrowserManager.browse_urls()"]
        CM["ContextManager.get_similar_content_by_query()"]
    end
    
    GCBWS --> GMS
    GCBWS --> EMR
    EMR --> MCPC
    GCBWS --> AG
    AG --> PSQ
    PSQ --> BM
    BM --> WP
    PSQ --> CM
    PSQ --> CMAW
```

**Sources:** [gpt_researcher/skills/researcher.py:21-32](), [gpt_researcher/skills/researcher.py:266-365](), [gpt_researcher/skills/browser.py:14-35]()

## Sub-Query Processing Pipeline

The parallel processing pipeline begins after sub-query generation and involves several coordinated stages:

### Pipeline Flow

```mermaid
flowchart TD
    Start["Query + Domains"] --> GetStrat["_get_mcp_strategy()"]
    GetStrat --> StratSwitch{Strategy?}
    
    StratSwitch -->|fast| RunOnceMCP["_execute_mcp_research_for_queries([query])"]
    StratSwitch -->|deep| DeferMCP["Set _mcp_results_cache = None"]
    StratSwitch -->|disabled| SkipMCP["Skip MCP Processing"]
    
    RunOnceMCP --> CacheMCP["Set _mcp_results_cache"]
    
    CacheMCP --> PlanRes["plan_research()"]
    DeferMCP --> PlanRes
    SkipMCP --> PlanRes
    
    PlanRes --> Gather["asyncio.gather(*[_process_sub_query(sq)])"]
    
    subgraph ParallelProc["_process_sub_query(sub_query)"]
        direction TB
        CheckCache{"Check Cache/Strategy"}
        CheckCache -->|fast| UseCache["Use _mcp_results_cache"]
        CheckCache -->|deep| RunDeep["_execute_mcp_research_for_queries([sq])"]
        
        UseCache --> Scrape["BrowserManager.browse_urls()"]
        RunDeep --> Scrape
        
        Scrape --> GetSim["ContextManager.get_similar_content()"]
        GetSim --> Combine["_combine_mcp_and_web_context()"]
    end
    
    Gather --> Filter["Filter empty & Join context"]
    Filter --> Return["Final Context String"]
```

**Sources:** [gpt_researcher/skills/researcher.py:266-365](), [gpt_researcher/skills/researcher.py:449-578]()

### Key Processing Methods

| Method | File:Line | Purpose |
|--------|-----------|---------|
| `_get_context_by_web_search` | [gpt_researcher/skills/researcher.py:266-266]() | Orchestrates the high-level parallel search flow. |
| `_process_sub_query` | [gpt_researcher/skills/researcher.py:449-449]() | Processes a single sub-query, combining MCP and web results. |
| `_execute_mcp_research_for_queries` | [gpt_researcher/skills/researcher.py:393-393]() | Interface for calling MCP-enabled tools for research. |
| `_get_mcp_strategy` | [gpt_researcher/skills/researcher.py:367-367]() | Resolves the MCP execution mode (fast, deep, disabled). |
| `_combine_mcp_and_web_context` | [gpt_researcher/skills/researcher.py:630-630]() | Merges results from different retrieval layers into one context. |

**Sources:** [gpt_researcher/skills/researcher.py:266-680]()

## MCP Strategy Configuration

The MCP strategy determines how specialized tools (via the Model Context Protocol) are invoked during research.

### Strategy Types

*   **Fast (Default)**: Runs MCP once with the original query. The results are cached in `_mcp_results_cache` [gpt_researcher/skills/researcher.py:44]() and reused for all sub-queries [gpt_researcher/skills/researcher.py:307-310]().
*   **Deep**: Runs MCP for every individual sub-query [gpt_researcher/skills/researcher.py:503-507](). This provides maximum thoroughness but increases API calls.
*   **Disabled**: Skips MCP entirely, relying solely on web retrievers [gpt_researcher/skills/researcher.py:284-287]().

### Strategy Resolution Priority

The `GPTResearcher` class resolves the strategy during initialization [gpt_researcher/agent.py:132-136]():
1.  Direct `mcp_strategy` parameter in `__init__`.
2.  `mcp_max_iterations` parameter (mapped to strategy for backward compatibility).
3.  Configuration file (`config.json`) or environment variables.
4.  Defaulting to `"fast"`.

**Sources:** [gpt_researcher/agent.py:132-136](), [gpt_researcher/skills/researcher.py:367-391]()

## Parallel Execution and Rate Limiting

The system uses Python's `asyncio.gather()` to execute sub-queries concurrently [gpt_researcher/skills/researcher.py:349-354](). To prevent overwhelming external APIs, a `WorkerPool` and `GlobalRateLimiter` manage the actual execution flow.

### Scraper Concurrency and Global Throttling

The `BrowserManager` utilizes a `WorkerPool` initialized with `max_scraper_workers` [gpt_researcher/skills/browser.py:32-35](). This pool integrates with a `GlobalRateLimiter` [gpt_researcher/utils/rate_limiter.py:13-19]() which enforces a minimum delay across all active researcher instances [gpt_researcher/utils/workers.py:21-24]().

```mermaid
sequenceDiagram
    participant RC as ResearchConductor
    participant AG as asyncio.gather
    participant PSQ as _process_sub_query
    participant BM as BrowserManager
    participant WP as WorkerPool
    participant GRL as GlobalRateLimiter
    participant S as Scraper

    RC->>AG: gather(*[_process_sub_query])
    par For each Sub-Query
        AG->>PSQ: Execute
        PSQ->>BM: browse_urls(urls)
        BM->>WP: throttle()
        WP->>GRL: wait_if_needed()
        GRL-->>WP: Delay completed
        WP-->>BM: Semaphore acquired
        BM->>S: scrape_urls()
        S-->>BM: Scraped Content
        BM-->>PSQ: content
        PSQ-->>AG: context string
    end
    AG-->>RC: List[context]
```

**Sources:** [gpt_researcher/skills/researcher.py:349-354](), [gpt_researcher/skills/browser.py:32-35](), [gpt_researcher/utils/workers.py:8-29](), [gpt_researcher/utils/rate_limiter.py:60-80]()

## Result Aggregation and Filtering

Once `asyncio.gather` completes, the results are processed to ensure a clean context for the report generator:

1.  **Filtering**: The system filters out any empty results from failed queries [gpt_researcher/skills/researcher.py:357-357]().
2.  **Joining**: Valid context strings are joined with space separators to form a single continuous context block [gpt_researcher/skills/researcher.py:359-359]().
3.  **Logging**: The total size of the combined context is logged for observability [gpt_researcher/skills/researcher.py:360-360]().

### Context Combination Logic
The `_combine_mcp_and_web_context` function handles the merging of structured MCP results and unstructured web content [gpt_researcher/skills/researcher.py:630-680](). It iterates through `mcp_context` (a list of dictionaries) and appends the `web_context` (a string), ensuring that source information is preserved where possible.

**Sources:** [gpt_researcher/skills/researcher.py:357-360](), [gpt_researcher/skills/researcher.py:630-680]()

---

# Page: Context Management and Compression

# Context Management and Compression

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [gpt_researcher/__init__.py](gpt_researcher/__init__.py)
- [gpt_researcher/actions/__init__.py](gpt_researcher/actions/__init__.py)
- [gpt_researcher/actions/report_generation.py](gpt_researcher/actions/report_generation.py)
- [gpt_researcher/context/__init__.py](gpt_researcher/context/__init__.py)
- [gpt_researcher/context/compression.py](gpt_researcher/context/compression.py)
- [gpt_researcher/context/retriever.py](gpt_researcher/context/retriever.py)
- [gpt_researcher/skills/context_manager.py](gpt_researcher/skills/context_manager.py)
- [gpt_researcher/skills/writer.py](gpt_researcher/skills/writer.py)
- [gpt_researcher/vector_store/__init__.py](gpt_researcher/vector_store/__init__.py)
- [gpt_researcher/vector_store/vector_store.py](gpt_researcher/vector_store/vector_store.py)

</details>



This page documents the context management and compression subsystem in GPT Researcher. Context management is responsible for filtering, retrieving, and compressing large volumes of scraped web content and documents into relevant, concise contexts suitable for LLM processing. This involves embedding-based similarity matching, text chunking, and intelligent filtering to select only the most pertinent information for report generation.

For information about how research queries are planned and decomposed, see [Query Planning and Decomposition](9.1). For details on how sources are curated and validated after compression, see [Source Curation and Validation](9.4).

## Overview

The context management system addresses a fundamental challenge in autonomous research: converting large volumes of raw scraped content (often hundreds of pages) into compact, relevant contexts that fit within LLM token limits. The system uses embedding-based similarity filtering to identify the most relevant text chunks for a given query, reducing information overload while preserving essential details.

**Key responsibilities:**
- Compress raw scraped content based on query relevance.
- Retrieve similar content from vector stores.
- Find relevant previously-written content to avoid duplication and maintain consistency.
- Optimize for both quality (relevance) and performance (cost/speed) using a "fast path" for small datasets.

Sources: [gpt_researcher/skills/context_manager.py:1-155](), [gpt_researcher/context/compression.py:1-256]()

## Architecture Overview

The following diagram illustrates how the context management classes interact with the core research skills and the underlying LangChain-based compression pipeline.

### System Entity Map

```mermaid
graph TB
    subgraph "Research Workflow Integration"
        ResearchConductor["ResearchConductor<br/>(gpt_researcher/skills/researcher.py)"]
        GPTResearcher["GPTResearcher<br/>(gpt_researcher/agent.py)"]
    end
    
    subgraph "ContextManager Skill"
        ContextManager["ContextManager<br/>(gpt_researcher/skills/context_manager.py)"]
        
        GetSimilarByQuery["get_similar_content_by_query()"]
        GetSimilarVectorstore["get_similar_content_by_query_with_vectorstore()"]
        GetSimilarWritten["get_similar_written_contents_by_draft_section_titles()"]
    end
    
    subgraph "Compression Classes"
        ContextCompressor["ContextCompressor<br/>(gpt_researcher/context/compression.py)"]
        VectorstoreCompressor["VectorstoreCompressor<br/>(gpt_researcher/context/compression.py)"]
        WrittenContentCompressor["WrittenContentCompressor<br/>(gpt_researcher/context/compression.py)"]
    end
    
    subgraph "Pipeline Components"
        TextSplitter["RecursiveCharacterTextSplitter<br/>chunk_size=1000, overlap=100"]
        EmbeddingsFilter["EmbeddingsFilter<br/>similarity_threshold=0.35"]
        Embeddings["Memory.get_embeddings()"]
    end
    
    subgraph "Base Retrievers"
        SearchAPIRetriever["SearchAPIRetriever<br/>(gpt_researcher/context/retriever.py)"]
        SectionRetriever["SectionRetriever<br/>(gpt_researcher/context/retriever.py)"]
    end
    
    GPTResearcher -->|"initializes"| ContextManager [gpt_researcher/agent.py:182-186]()
    ResearchConductor -->|"calls"| GetSimilarByQuery [gpt_researcher/skills/researcher.py:526-528]()
    ResearchConductor -->|"calls"| GetSimilarVectorstore [gpt_researcher/skills/researcher.py:530-532]()
    
    GetSimilarByQuery -->|"creates"| ContextCompressor [gpt_researcher/skills/context_manager.py:55-60]()
    GetSimilarVectorstore -->|"creates"| VectorstoreCompressor [gpt_researcher/skills/context_manager.py:82-85]()
    GetSimilarWritten -->|"creates"| WrittenContentCompressor [gpt_researcher/skills/context_manager.py:146-151]()
    
    ContextCompressor -->|"uses"| TextSplitter [gpt_researcher/context/compression.py:129]()
    ContextCompressor -->|"uses"| EmbeddingsFilter [gpt_researcher/context/compression.py:130-131]()
    ContextCompressor -->|"uses"| SearchAPIRetriever [gpt_researcher/context/compression.py:135-137]()
    
    WrittenContentCompressor -->|"uses"| TextSplitter [gpt_researcher/context/compression.py:222]()
    WrittenContentCompressor -->|"uses"| EmbeddingsFilter [gpt_researcher/context/compression.py:223-224]()
    WrittenContentCompressor -->|"uses"| SectionRetriever [gpt_researcher/context/compression.py:218-220]()
    
    VectorstoreCompressor -->|"uses"| Embeddings [gpt_researcher/context/compression.py:71-82]()
```

**ContextManager as a Skill**

The `ContextManager` class is initialized as a skill within `GPTResearcher`. It provides high-level methods to the `ResearchConductor` for retrieving relevant data:

| Method | Purpose | Returns |
|--------|---------|---------|
| `get_similar_content_by_query()` | Compress raw scraped documents by query similarity | Formatted context string |
| `get_similar_content_by_query_with_vectorstore()` | Retrieve from existing vector store | Formatted context string |
| `get_similar_written_contents_by_draft_section_titles()` | Find similar previously-written sections to maintain context | List of content strings |

Sources: [gpt_researcher/skills/context_manager.py:18-155](), [gpt_researcher/agent.py:182-186]()

## Compression Classes

Three specialized compressor classes in `gpt_researcher/context/compression.py` handle different context sources.

### ContextCompressor

This is the primary class for handling web-scraped content. It implements an optimization to skip heavy processing for small inputs.

```mermaid
flowchart TD
    Input["Input: List of scraped documents<br/>(raw_content, url, title)"]
    
    CheckSize{"Total chars < COMPRESSION_THRESHOLD<br/>AND docs <= max_results?"}
    
    FastPath["Fast Path:<br/>Return documents directly<br/>(No embedding filtering)"]
    
    BuildPipeline["Build Compression Pipeline<br/>(ContextualCompressionRetriever)"]
    
    Split["RecursiveCharacterTextSplitter<br/>chunk_size=1000, overlap=100"]
    
    Embed["Generate embeddings<br/>for chunks and query"]
    
    Filter["EmbeddingsFilter<br/>similarity_threshold=0.35"]
    
    Format["pretty_print_docs()"]
    
    Output["Output: Compressed context string"]
    
    Input --> CheckSize [gpt_researcher/context/compression.py:158-162]()
    CheckSize -->|"Yes"| FastPath [gpt_researcher/context/compression.py:164-171]()
    CheckSize -->|"No"| BuildPipeline [gpt_researcher/context/compression.py:174]()
    
    FastPath --> Output
    
    BuildPipeline --> Split [gpt_researcher/context/compression.py:129]()
    Split --> Embed [gpt_researcher/context/compression.py:130]()
    Embed --> Filter [gpt_researcher/context/compression.py:131]()
    Filter --> Format [gpt_researcher/context/compression.py:178]()
    Format --> Output
```

**Key features:**
- **Optimization threshold**: If total content is under `COMPRESSION_THRESHOLD` (default 8000 chars) [gpt_researcher/context/compression.py:159-162](), it returns documents directly [gpt_researcher/context/compression.py:164-171]().
- **Text chunking**: Uses `RecursiveCharacterTextSplitter` with 1000-character chunks [gpt_researcher/context/compression.py:129]().
- **Similarity filtering**: `EmbeddingsFilter` removes chunks below `SIMILARITY_THRESHOLD` (default 0.35) [gpt_researcher/context/compression.py:119-131]().
- **Cost tracking**: Uses `estimate_embedding_cost` and a `cost_callback` to track API usage [gpt_researcher/context/compression.py:175-176]().

Sources: [gpt_researcher/context/compression.py:85-179]()

### VectorstoreCompressor

**Purpose:** Retrieves relevant documents from an existing vector store using similarity search. Used when research is conducted against a vector database [gpt_researcher/skills/context_manager.py:65-86]().

**Key features:**
- Wraps `VectorStoreWrapper` [gpt_researcher/context/compression.py:36-55]().
- Performs async similarity search with `asimilarity_search` [gpt_researcher/context/compression.py:71-82]().
- Supports metadata filtering via the `filter` attribute [gpt_researcher/context/compression.py:67]().

Sources: [gpt_researcher/context/compression.py:36-83](), [gpt_researcher/vector_store/vector_store.py:10-44]()

### WrittenContentCompressor

**Purpose:** Specialized compressor for finding relevant sections from previously written report content to prevent redundancy in detailed reports [gpt_researcher/context/compression.py:181-185]().

**Key features:**
- Uses `SectionRetriever` to process previously written content [gpt_researcher/context/compression.py:218-220]().
- Defaults to a higher similarity threshold (0.5) to ensure high relevance [gpt_researcher/context/compression.py:205]().
- Returns a list of relevant strings rather than a single concatenated string [gpt_researcher/context/compression.py:245-256]().

Sources: [gpt_researcher/context/compression.py:181-256](), [gpt_researcher/skills/context_manager.py:88-154]()

## Compression Pipeline Components

### Text Splitter
The system utilizes `RecursiveCharacterTextSplitter` from `langchain_text_splitters` to divide documents into chunks of 1000 characters with a 100-character overlap [gpt_researcher/context/compression.py:129](). This overlap ensures that semantic context is not lost at the split points.

### Embeddings Filter
The `EmbeddingsFilter` [gpt_researcher/context/compression.py:130-131]() is the core logic for reducing context size. It calculates the cosine similarity between the research query and each text chunk. Chunks that do not meet the `SIMILARITY_THRESHOLD` (defaulting to 0.35) are discarded [gpt_researcher/context/compression.py:119]().

### Base Retrievers
Two custom retrievers bridge the raw data into the LangChain compression pipeline:
- **`SearchAPIRetriever`**: Handles web-scraped page dictionaries [gpt_researcher/context/retriever.py:16-35]().
- **`SectionRetriever`**: Handles structured sections of written content [gpt_researcher/context/retriever.py:37-68]().

Sources: [gpt_researcher/context/retriever.py:1-68](), [gpt_researcher/context/compression.py:122-141]()

## Integration with Research Workflow

The `ResearchConductor` coordinates the flow from scraping to compression.

```mermaid
sequenceDiagram
    participant RC as ResearchConductor
    participant CM as ContextManager
    participant BM as BrowserManager
    participant CC as ContextCompressor
    
    RC->>BM: browse_urls(urls)
    BM-->>RC: scraped_data[]
    
    RC->>CM: get_similar_content_by_query(query, scraped_data) [gpt_researcher/skills/context_manager.py:37]
    CM->>CC: new ContextCompressor(scraped_data, embeddings) [gpt_researcher/skills/context_manager.py:55]
    CM->>CC: async_get_context(query) [gpt_researcher/skills/context_manager.py:61]
    
    alt Total content < 8000 chars [gpt_researcher/context/compression.py:162]
        CC-->>CM: Return raw_content (Fast Path) [gpt_researcher/context/compression.py:171]
    else Content > 8000 chars
        CC->>CC: Split into 1000-char chunks [gpt_researcher/context/compression.py:129]
        CC->>CC: Filter by embedding similarity (0.35) [gpt_researcher/context/compression.py:130]
        CC-->>CM: Return relevant chunks [gpt_researcher/context/compression.py:178]
    end
    
    CM-->>RC: compressed_context_string
```

**Execution Steps:**
1. **Scraping**: `BrowserManager` scrapes content and updates the `research_sources` in the agent.
2. **Requesting Context**: `ResearchConductor` calls `ContextManager.get_similar_content_by_query` [gpt_researcher/skills/context_manager.py:37-63]().
3. **Embedding Selection**: The `ContextManager` retrieves the configured embedding model from the researcher's memory [gpt_researcher/skills/context_manager.py:57]().
4. **Compression**: The `ContextCompressor` executes the pipeline, applying text splitting and similarity filtering [gpt_researcher/context/compression.py:174-178]().
5. **Costing**: Embedding costs are estimated and added to the researcher's total cost via `add_costs` [gpt_researcher/context/compression.py:176]().

Sources: [gpt_researcher/skills/context_manager.py:37-63](), [gpt_researcher/context/compression.py:119-179]()

## Configuration and Optimization

### Environment Variables
The behavior of the compression system is controlled by several environment variables:

| Variable | Default | Purpose |
|----------|---------|---------|
| `SIMILARITY_THRESHOLD` | `0.35` | Minimum similarity score for a chunk to be included in context [gpt_researcher/context/compression.py:119](). |
| `COMPRESSION_THRESHOLD` | `8000` | Character count below which compression is skipped for performance [gpt_researcher/context/compression.py:159](). |
| `MAX_CONTENT_CHARS` | `50000` | Maximum characters of raw content to embed per document to avoid token limits [gpt_researcher/context/retriever.py:13](). |

### Context Formatting
Compressed documents are formatted into a readable string for the LLM using `PromptFamily.pretty_print_docs` [gpt_researcher/context/compression.py:82, 171, 178](). This ensures that the LLM receives structured data containing the source URL, title, and content for each relevant chunk.

Sources: [gpt_researcher/context/compression.py:119-171](), [gpt_researcher/context/retriever.py:13]()

---

# Page: Source Curation and Validation

# Source Curation and Validation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [gpt_researcher/actions/agent_creator.py](gpt_researcher/actions/agent_creator.py)
- [gpt_researcher/actions/report_generation.py](gpt_researcher/actions/report_generation.py)
- [gpt_researcher/actions/utils.py](gpt_researcher/actions/utils.py)
- [gpt_researcher/skills/context_manager.py](gpt_researcher/skills/context_manager.py)
- [gpt_researcher/skills/curator.py](gpt_researcher/skills/curator.py)
- [gpt_researcher/skills/writer.py](gpt_researcher/skills/writer.py)
- [gpt_researcher/utils/costs.py](gpt_researcher/utils/costs.py)
- [gpt_researcher/utils/tools.py](gpt_researcher/utils/tools.py)
- [tests/test_costs.py](tests/test_costs.py)
- [tests/test_llm_usage_tracking.py](tests/test_llm_usage_tracking.py)

</details>



## Purpose and Scope

Source Curation and Validation is the process of evaluating and ranking research sources based on relevance, credibility, and reliability using LLM-based assessment. This system filters gathered research data to prioritize high-quality, authoritative sources before report generation.

This page covers the `SourceCurator` class and its integration into the research pipeline. For information about gathering sources, see [Parallel Sub-Query Processing](). For context compression applied to curated sources, see [Context Management and Compression](). For how curated sources feed into reports, see [Report Generation and Formatting]().

---

## Source Curation Pipeline Flow

The curation process occurs after initial research data has been gathered and compressed, but before the final report is written.

```mermaid
graph TD
    subgraph "ResearchConductor Flow"
        A["ResearchConductor.conduct_research()"] --> B["_get_context_by_web_search()"]
        B --> C["Multiple sub-queries processed"]
        C --> D["Scraped content gathered"]
    end
    
    subgraph "Curation Stage"
        D --> E{"cfg.curate_sources<br/>enabled?"}
        E -->|Yes| F["SourceCurator.curate_sources()"]
        E -->|No| G["Use all sources"]
        F --> H["LLM evaluates sources"]
        H --> I["JSON response with<br/>ranked sources"]
    end
    
    subgraph "Evaluation Criteria"
        H --> J["Relevance to query"]
        H --> K["Source credibility"]
        H --> L["Content currency"]
        H --> M["Objectivity"]
        H --> N["Quantitative data<br/>priority"]
    end
    
    subgraph "Output"
        I --> O["self.researcher.context<br/>updated"]
        G --> O
        O --> P["ReportGenerator.write_report()"]
    end
```

**Diagram: Source Curation in Research Pipeline**

Sources: [gpt_researcher/skills/curator.py:33-85](), [gpt_researcher/skills/writer.py:49-77]()

---

## SourceCurator Class Architecture

The `SourceCurator` class provides LLM-based source evaluation and ranking capabilities. It is initialized within the `GPTResearcher` agent and maintains a reference to its parent to access configuration and logging utilities.

### Initialization and Structure

| Component | Type | Purpose |
|-----------|------|---------|
| `researcher` | `GPTResearcher` | Parent researcher instance for config and callbacks [gpt_researcher/skills/curator.py:29-31]() |
| `curate_sources()` | `async method` | Main curation entry point [gpt_researcher/skills/curator.py:33]() |
| LLM Provider | `smart_llm_model` | Model used for evaluation (typically GPT-4o) [gpt_researcher/skills/curator.py:61]() |
| Max Results | `int` | Maximum sources to return (default: 10) [gpt_researcher/skills/curator.py:36]() |

```mermaid
graph LR
    subgraph "GPTResearcher_Instance"
        A["GPTResearcher"] -- "instantiates" --> B["SourceCurator"]
    end
    
    subgraph "SourceCurator_Attributes"
        B -- "holds reference" --> C["self.researcher"]
    end
    
    subgraph "Access_to_Parent_Components"
        C --> D["self.researcher.cfg"]
        C --> E["self.researcher.role"]
        C --> F["self.researcher.query"]
        C --> G["self.researcher.websocket"]
        C --> H["self.researcher.add_costs"]
        C --> I["self.researcher.prompt_family"]
    end
    
    subgraph "Public_API"
        J["curate_sources(source_data, max_results)"] -- "returns" --> K["List[Dict]"]
    end
    
    B --> J
```

**Diagram: SourceCurator Component Relationships**

Sources: [gpt_researcher/skills/curator.py:15-31]()

### Key Method: `curate_sources()`

This method sends the gathered `source_data` to a "Smart LLM" (defined in `Config`) to rank them based on guidelines provided by the `PromptFamily`.

```mermaid
sequenceDiagram
    participant RC as ResearchConductor
    participant SC as SourceCurator
    participant LLM as create_chat_completion
    participant WS as stream_output
    
    RC->>SC: curate_sources(source_data, max_results=10)
    SC->>WS: type="logs", content="research_plan"
    SC->>SC: prompt_family.curate_sources(query, source_data, max_results)
    SC->>LLM: model=cfg.smart_llm_model, temp=0.2
    Note over SC,LLM: Max Tokens: 8000
    LLM-->>SC: JSON response string
    SC->>SC: json.loads(response)
    SC->>WS: type="logs", content="research_plan"
    SC-->>RC: Return curated_sources list
```

**Diagram: Source Curation Execution Flow**

Sources: [gpt_researcher/skills/curator.py:33-85](), [gpt_researcher/actions/utils.py:7-32]()

---

## LLM-Based Evaluation System

### Curation Prompt Structure

The curation prompt is generated via `self.researcher.prompt_family.curate_sources()`. It instructs the LLM to analyze the relevance and quality of each source provided in the context of the main research query.

**Evaluation Guidelines in Prompt:**

| Criterion | Priority | Description |
|-----------|----------|-------------|
| **Quantitative Value** | HIGHEST | Sources with statistics, numbers, or concrete data are prioritized. |
| **Relevance** | High | Sources directly or partially connected to the query. |
| **Credibility** | High | Authoritative sources are favored over unknown or personal blogs. |
| **Currency** | Medium | Recent information is preferred unless historical data is essential. |
| **Objectivity** | Medium | Biased sources are retained if they provide a unique perspective. |

Sources: [gpt_researcher/skills/curator.py:64-65]()

---

## Integration with Research Pipeline

### Pipeline Integration Points

The `ResearchConductor` (managed via `GPTResearcher`) orchestrates the transition of data from the `ContextManager` to the `SourceCurator`.

```mermaid
sequenceDiagram
    participant RC as ResearchConductor
    participant CM as ContextManager
    participant SC as SourceCurator
    participant RG as ReportGenerator
    
    Note over RC: conduct_research()
    
    RC->>CM: get_similar_content_by_query()
    CM-->>RC: research_data
    
    alt cfg.curate_sources == True
        RC->>SC: curate_sources(research_data)
        SC-->>RC: curated_sources
    end
    
    RC->>RG: write_report(ext_context=curated_sources)
```

**Diagram: Curation Integration in Research Lifecycle**

Sources: [gpt_researcher/skills/writer.py:49-77](), [gpt_researcher/skills/context_manager.py:37-63]()

---

## Error Handling and Fallback

### JSON Parsing and Completion Failures

The `SourceCurator` includes robust error handling to ensure the research pipeline does not crash if the LLM returns malformed JSON or fails to respond.

```python
try:
    response = await create_chat_completion(...)
    curated_sources = json.loads(response)
    return curated_sources
except Exception as e:
    # Log failure and return original data as fallback
    print(f"Error in curate_sources from LLM response: {response}")
    return source_data
```

**Fallback Mechanism:** If curation fails, the system returns the original `source_data` unranked, allowing the `ReportGenerator` to still proceed with the available context.

Sources: [gpt_researcher/skills/curator.py:87-96]()

---

## WebSocket Streaming and UI Feedback

The `SourceCurator` uses the `stream_output` utility to provide real-time updates to the user via WebSockets.

| Message Type | Step | Content |
|-------------|------|---------|
| `logs` | `research_plan` | "⚖️ Evaluating and curating sources by credibility and relevance..." [gpt_researcher/skills/curator.py:51-56]() |
| `logs` | `research_plan` | "🏅 Verified and ranked top X most reliable sources" [gpt_researcher/skills/curator.py:77-83]() |
| `logs` | `research_plan` | "🚫 Source verification failed: {error}" [gpt_researcher/skills/curator.py:89-95]() |

Sources: [gpt_researcher/skills/curator.py:51-95](), [gpt_researcher/actions/utils.py:7-32]()

---

## Summary of Technical Parameters

The curation step is a high-token operation using the "Smart" model tier to ensure accuracy.

| Parameter | Default Value | Implementation |
|-----------|---------------|----------------|
| **LLM Model** | `config.smart_llm_model` | [gpt_researcher/skills/curator.py:61]() |
| **Temperature** | `0.2` | Hardcoded for consistency [gpt_researcher/skills/curator.py:67]() |
| **Max Tokens** | `8000` | Hardcoded for large context [gpt_researcher/skills/curator.py:68]() |
| **Max Results** | `10` | Configurable parameter [gpt_researcher/skills/curator.py:36]() |

Sources: [gpt_researcher/skills/curator.py:60-72]()

---

# Page: Report Generation and Formatting

# Report Generation and Formatting

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/chat/chat.py](backend/chat/chat.py)
- [backend/run_server.py](backend/run_server.py)
- [backend/server/agent_discovery.py](backend/server/agent_discovery.py)
- [backend/server/app.py](backend/server/app.py)
- [backend/server/report_store.py](backend/server/report_store.py)
- [backend/utils.py](backend/utils.py)
- [gpt_researcher/actions/report_generation.py](gpt_researcher/actions/report_generation.py)
- [gpt_researcher/skills/context_manager.py](gpt_researcher/skills/context_manager.py)
- [gpt_researcher/skills/writer.py](gpt_researcher/skills/writer.py)
- [multi_agents/agents/utils/file_formats.py](multi_agents/agents/utils/file_formats.py)
- [multi_agents/langgraph.json](multi_agents/langgraph.json)
- [multi_agents/main.py](multi_agents/main.py)
- [multi_agents/requirements.txt](multi_agents/requirements.txt)
- [tests/test_agent_discovery.py](tests/test_agent_discovery.py)

</details>



This document covers the report generation and formatting system in GPT Researcher. After research context has been gathered and curated (see [Context Management](), section 9.3 and [Source Curation](), section 9.4), the system synthesizes this information into structured reports in multiple formats. This page documents the `ReportGenerator` skill, prompt engineering for different report types, LLM-based synthesis, and format conversion to PDF, DOCX, and Markdown.

---

## Report Generation Architecture

The report generation subsystem transforms raw research context into formatted reports through a multi-stage pipeline involving prompt engineering, LLM synthesis, and format conversion.

### Report Generation Pipeline

```mermaid
graph TB
    subgraph "Input Stage"
        Context["Research Context<br/>(from ContextManager)"]
        Sources["Source URLs<br/>(from visited_urls)"]
        Config["Configuration<br/>tone, report_format, language"]
    end
    
    subgraph "Report Generator - gpt_researcher/skills/writer.py"
        RG["ReportGenerator"]
        SelectPrompt["Select Prompt Family Method<br/>Based on report_type"]
        
        subgraph "Prompt Engineering"
            PromptFamily["PromptFamily Class<br/>gpt_researcher/prompts.py"]
            IntroPrompt["write_report_introduction()"]
            ReportPrompt["generate_report()"]
            ConclPrompt["write_conclusion()"]
        end
        
        FormatPrompt["Format Prompt with:<br/>context, query, tone"]
    end
    
    subgraph "LLM Synthesis - gpt_researcher/utils/llm.py"
        SmartLLM["Smart LLM<br/>(cfg.smart_llm_model)"]
        Generate["create_chat_completion()<br/>temperature: 0.25-0.4"]
        Stream["Stream Output via WebSocket"]
    end
    
    subgraph "Post-Processing"
        Markdown["Base Markdown Report"]
        AddRefs["add_references()<br/>Insert citation links"]
        AddTOC["table_of_contents()<br/>Generate TOC"]
    end
    
    subgraph "Format Conversion - backend/utils.py"
        MD["Markdown File<br/>write_text_to_md()"]
        PDF["PDF File<br/>write_md_to_pdf()<br/>md2pdf / weasyprint"]
        DOCX["DOCX File<br/>write_md_to_word()<br/>htmldocx / python-docx"]
    end
    
    Context --> RG
    Sources --> RG
    Config --> RG
    
    RG --> SelectPrompt
    SelectPrompt --> PromptFamily
    
    PromptFamily --> IntroPrompt
    PromptFamily --> ReportPrompt
    PromptFamily --> ConclPrompt
    
    IntroPrompt --> FormatPrompt
    ReportPrompt --> FormatPrompt
    ConclPrompt --> FormatPrompt
    
    FormatPrompt --> SmartLLM
    SmartLLM --> Generate
    Generate --> Stream
    Stream --> Markdown
    
    Markdown --> AddRefs
    AddRefs --> AddTOC
    AddTOC --> MD
    AddTOC --> PDF
    AddTOC --> DOCX
```

**Sources:** [gpt_researcher/skills/writer.py:31-47](), [gpt_researcher/actions/report_generation.py:12-220](), [backend/utils.py:62-130]()

---

## The ReportGenerator Skill

The `ReportGenerator` class (located in `gpt_researcher/skills/writer.py`) is a core skill initialized by the `GPTResearcher` agent. It encapsulates the logic for orchestrating the writing of different report segments.

### Core ReportGenerator Methods

| Method | Purpose | Implementation | Key Parameters |
|--------|---------|----------------|----------------|
| `write_report()` | Orchestrates the main report body generation | Calls `generate_report` action | `existing_headers`, `relevant_written_contents`, `available_images` |
| `write_introduction()` | Generates the report's opening section | Calls `write_report_introduction` | Uses `self.researcher.context` |
| `write_report_conclusion()` | Generates the final synthesis | Calls `write_conclusion` | `report_content` |
| `get_subtopics()` | Dynamically identifies sub-areas for research | Calls `construct_subtopics` | `self.researcher.context` |

**Sources:** [gpt_researcher/skills/writer.py:49-162](), [gpt_researcher/skills/writer.py:164-193](), [gpt_researcher/actions/report_generation.py:12-112]()

### ReportGenerator Skill Integration

```mermaid
graph LR
    subgraph "GPTResearcherAgent [gpt_researcher/agent.py]"
        Init["__init__()"]
        RG_Skill["self.report_generator<br/>= ReportGenerator(self)"]
    end
    
    subgraph "ReportWritingActions [gpt_researcher/actions/report_generation.py]"
        Action1["write_report_introduction()"]
        Action2["generate_report()"]
        Action3["write_conclusion()"]
    end
    
    Init --> RG_Skill
    RG_Skill -- "calls" --> Action1
    RG_Skill -- "calls" --> Action2
    RG_Skill -- "calls" --> Action3
```

**Sources:** [gpt_researcher/agent.py:164](), [gpt_researcher/skills/writer.py:113](), [gpt_researcher/skills/writer.py:152](), [gpt_researcher/skills/writer.py:183]()

---

## Prompt Families and Report Synthesis

The `PromptFamily` class in `gpt_researcher/prompts.py` provides the logic for formatting instructions sent to the LLM. It supports various report types via the `ReportType` enum.

### Specialized Prompt Methods

*   **Introduction Generation**: `generate_report_introduction()` creates a prompt for a concise, engaging opening that sets the stage for the research query [gpt_researcher/actions/report_generation.py:42-46]().
*   **Conclusion Generation**: `generate_report_conclusion()` asks the LLM to synthesize the entire report content into a final summary [gpt_researcher/actions/report_generation.py:95-97]().
*   **Subtopic Titles**: `generate_draft_titles_prompt()` helps the LLM decide on section headers for a specific subtopic based on available context [gpt_researcher/actions/report_generation.py:191-192]().

### Image Integration in Reports
The `ReportGenerator` also handles image metadata. If `available_images` are provided, they are streamed via WebSocket before the report text is written so the frontend can prepare the UI [gpt_researcher/skills/writer.py:63-75]().

**Sources:** [gpt_researcher/prompts.py:14-29](), [gpt_researcher/actions/report_generation.py:12-112](), [gpt_researcher/skills/writer.py:63-75]()

---

## Format Conversion and File Handling

Once the LLM generates a Markdown-formatted report, the system provides utilities to convert this content into professional documents.

### Conversion Utilities (`backend/utils.py`)

| Function | Library Used | Process |
|----------|--------------|---------|
| `write_text_to_md()` | `aiofiles` | Writes raw UTF-8 encoded text to an `.md` file in the `outputs/` directory [backend/utils.py:23-34](). |
| `write_md_to_pdf()` | `md2pdf` / `weasyprint` | Preprocesses image URLs to absolute paths, applies CSS from `pdf_styles.css`, and renders to PDF [backend/utils.py:62-97](). |
| `write_md_to_word()` | `htmldocx` / `python-docx` | Converts Markdown to HTML using `mistune`, then parses HTML into a Word `.docx` structure [backend/utils.py:99-130](). |

### PDF Image Preprocessing
To ensure images render correctly in PDFs, the `_preprocess_images_for_pdf` function transforms relative `/outputs/` URLs into absolute `file://` paths that the PDF engine can resolve on the local filesystem [backend/utils.py:36-59]().

**Sources:** [backend/utils.py:23-130](), [multi_agents/agents/utils/file_formats.py:40-104]()

---

## Multi-Agent Publication Flow

In the multi-agent framework, the `ChiefEditorAgent` orchestrates the workflow, and a separate set of utilities exists to handle file generation, using unique task IDs (UUIDs) for file naming to prevent collisions.

### Multi-Agent File Utilities

```mermaid
graph TD
    subgraph "FileFormats [multi_agents/agents/utils/file_formats.py]"
        UUID["uuid.uuid4().hex"]
        W_MD["write_text_to_md()"]
        W_PDF["write_md_to_pdf()"]
        W_DOCX["write_md_to_word()"]
    end
    
    subgraph "Publication [multi_agents/main.py]"
        CE["ChiefEditorAgent"]
        MD_Out["{path}/{uuid}.md"]
        PDF_Out["{path}/{uuid}.pdf"]
        DOCX_Out["{path}/{uuid}.docx"]
    end
    
    CE --> UUID
    UUID --> W_MD
    UUID --> W_PDF
    UUID --> W_DOCX
    
    W_MD --> MD_Out
    W_PDF --> PDF_Out
    W_DOCX --> DOCX_Out
```

**Sources:** [multi_agents/agents/utils/file_formats.py:33-104](), [multi_agents/main.py:44-56]()

---

# Page: Image Generation System

# Image Generation System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/gpt-researcher/gptr/ai-development.md](docs/docs/gpt-researcher/gptr/ai-development.md)
- [docs/docs/gpt-researcher/gptr/image_generation.md](docs/docs/gpt-researcher/gptr/image_generation.md)
- [frontend/nextjs/styles/markdown.css](frontend/nextjs/styles/markdown.css)
- [gpt_researcher/document/document.py](gpt_researcher/document/document.py)
- [gpt_researcher/llm_provider/image/__init__.py](gpt_researcher/llm_provider/image/__init__.py)
- [gpt_researcher/llm_provider/image/image_generator.py](gpt_researcher/llm_provider/image/image_generator.py)
- [gpt_researcher/llm_provider/image/modelslab_image_generator.py](gpt_researcher/llm_provider/image/modelslab_image_generator.py)
- [gpt_researcher/skills/image_generator.py](gpt_researcher/skills/image_generator.py)
- [pyproject.toml](pyproject.toml)
- [setup.py](setup.py)

</details>



The Image Generation System enables GPT Researcher to automatically create contextually relevant AI-generated illustrations that are embedded inline within research reports. This system uses Google's Gemini image generation models (referred to as "Nano Banana") or ModelsLab to analyze research context and produce professional diagrams, flowcharts, and conceptual visualizations.

---

## Overview and Architecture

The Image Generation System implements a **pre-generation strategy** where images are planned and created during the research phase, before report writing begins. This approach eliminates delays in report streaming and ensures a seamless user experience.

### System Flow

```mermaid
flowchart TB
    subgraph "Research Phase"
        CR["GPTResearcher.conduct_research()"]
        ContextGather["Gather research context<br/>(web search, scraping)"]
        CheckEnabled["ImageGenerator.is_enabled()"]
        CR --> ContextGather
        ContextGather --> CheckEnabled
    end
    
    subgraph "Image Planning Phase"
        PlanImages["ImageGenerator.plan_and_generate_images()"]
        AnalyzeContext["Analyze context for<br/>visualization opportunities"]
        LLMAnalysis["LLM analyzes sections<br/>via _plan_image_concepts()"]
        IdentifyConcepts["Identify 2-3 visualization concepts"]
        
        CheckEnabled -->|Enabled| PlanImages
        PlanImages --> AnalyzeContext
        AnalyzeContext --> LLMAnalysis
        LLMAnalysis --> IdentifyConcepts
    end
    
    subgraph "Image Generation Phase"
        ParallelGen["Generate all images in parallel<br/>(asyncio.gather)"]
        Provider["ImageGeneratorProvider or<br/>ModelsLabImageGeneratorProvider"]
        SaveImages["Save to outputs/images/<br/>{research_id}/"]
        CacheImages["Store in<br/>ImageGenerator.generated_images[]"]
        
        IdentifyConcepts --> ParallelGen
        ParallelGen --> Provider
        Provider --> SaveImages
        SaveImages --> CacheImages
    end
    
    subgraph "Report Writing Phase"
        WriteReport["GPTResearcher.write_report()"]
        PassImages["Pass generated_images<br/>to ReportGenerator"]
        EmbedMarkdown["Embed images inline<br/>as markdown"]
        StreamReport["Stream report to frontend<br/>with images already embedded"]
        
        CacheImages --> WriteReport
        WriteReport --> PassImages
        PassImages --> EmbedMarkdown
        EmbedMarkdown --> StreamReport
    end
    
    CheckEnabled -->|Disabled| WriteReport
```

**Sources:** [gpt_researcher/skills/image_generator.py:77-180](), [docs/docs/gpt-researcher/gptr/image_generation.md:62-82](), [gpt_researcher/llm_provider/image/image_generator.py:101-105]()

---

## Component Architecture

### Core Components

```mermaid
graph TB
    subgraph "GPTResearcher Agent Space"
        Agent["GPTResearcher"]
        ImageGen["ImageGenerator"]
    end
    
    subgraph "Provider Space"
        IGProvider["ImageGeneratorProvider<br/>(Google Gemini/Imagen)"]
        MLProvider["ModelsLabImageGeneratorProvider<br/>(Flux/SDXL)"]
    end
    
    subgraph "Configuration Space"
        ConfigClass["Config"]
        EnvVars["IMAGE_GENERATION_ENABLED<br/>IMAGE_GENERATION_PROVIDER<br/>IMAGE_GENERATION_MODEL<br/>IMAGE_GENERATION_STYLE"]
    end
    
    subgraph "Infrastructure Space"
        GoogleSDK["google-genai library"]
        ModelsLabAPI["ModelsLab REST API"]
        FileSystem["outputs/images/<br/>{research_id}/"]
    end
    
    EnvVars --> ConfigClass
    ConfigClass --> Agent
    Agent --> ImageGen
    ImageGen --> IGProvider
    ImageGen --> MLProvider
    
    IGProvider --> GoogleSDK
    MLProvider --> ModelsLabAPI
    IGProvider --> FileSystem
    MLProvider --> FileSystem
```

**Sources:** [gpt_researcher/skills/image_generator.py:33-68](), [gpt_researcher/llm_provider/image/image_generator.py:22-44](), [gpt_researcher/llm_provider/image/modelslab_image_generator.py:24-34]()

### Key Classes and Methods

| Component | Location | Key Methods |
|-----------|----------|-------------|
| `ImageGenerator` | `gpt_researcher/skills/image_generator.py` | `plan_and_generate_images()`, `_init_provider()` |
| `ImageGeneratorProvider` | `gpt_researcher/llm_provider/image/image_generator.py` | `generate_image()`, `_build_enhanced_prompt()` |
| `ModelsLabImageGeneratorProvider` | `gpt_researcher/llm_provider/image/modelslab_image_generator.py` | `generate_image()`, `_poll_for_result()` |
| `DocumentLoader` | `gpt_researcher/document/document.py` | `load()`, `_load_document()` |

**Sources:** [gpt_researcher/skills/image_generator.py:20-43](), [gpt_researcher/llm_provider/image/image_generator.py:48-63](), [gpt_researcher/llm_provider/image/modelslab_image_generator.py:38-46]()

---

## Configuration System

### Environment Variables

The image generation system is controlled by the following environment variables:

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `IMAGE_GENERATION_ENABLED` | boolean | `false` | Master switch to enable/disable feature |
| `IMAGE_GENERATION_PROVIDER` | string | `google` | Provider choice: `google` or `modelslab` |
| `GOOGLE_API_KEY` | string | - | Required for Google provider |
| `MODELSLAB_API_KEY` | string | - | Required for ModelsLab provider |
| `IMAGE_GENERATION_MODEL` | string | `models/gemini-2.5-flash-image` | Specific model identifier |
| `IMAGE_GENERATION_MAX_IMAGES` | integer | `3` | Maximum images per report |
| `IMAGE_GENERATION_STYLE` | string | `dark` | Style preset: `dark`, `light`, or `auto` |

**Sources:** [docs/docs/gpt-researcher/gptr/image_generation.md:20-36](), [gpt_researcher/skills/image_generator.py:42-62]()

---

## Provider Implementation

### Google Gemini / Imagen
The `ImageGeneratorProvider` uses the `google-genai` SDK. It distinguishes between standard Gemini models (free tier) and Imagen models (paid tier) [gpt_researcher/llm_provider/image/image_generator.py:32-44](). It includes a specialized `_crop_to_landscape` method using `PIL` to ensure images fit report layouts at a 16:9 ratio [gpt_researcher/llm_provider/image/image_generator.py:106-155]().

### ModelsLab
The `ModelsLabImageGeneratorProvider` interacts with the ModelsLab REST API. Since generation is often asynchronous, it implements `_poll_for_result` to check the fetch endpoint until the image is ready [gpt_researcher/llm_provider/image/modelslab_image_generator.py:84-121]().

---

## Image Styling and Prompting

The system automatically enhances user prompts to match specific aesthetics.

### Dark Mode (Default)
When `IMAGE_GENERATION_STYLE` is set to `dark`, the system appends instructions for:
- Dark backgrounds (`#0d1117`)
- Teal/Cyan accents (`#14b8a6`)
- Glowing, futuristic, and tech-forward aesthetics [gpt_researcher/llm_provider/image/image_generator.py:168-181]().

### Markdown Embedding
Images are saved locally and embedded using standard markdown syntax:
`![Title](/outputs/images/{research_id}/img_{hash}_{index}.png)` [docs/docs/gpt-researcher/gptr/image_generation.md:148-154]().

---

## Frontend Integration

### CSS Styling
The Next.js frontend provides specialized styling for generated visuals in `markdown.css`:
- **General Images**: 75% width, centered, with 8px border-radius [frontend/nextjs/styles/markdown.css:176-184]().
- **Generated Visuals**: Images with alt text starting with "Illustration:", "Diagram:", or "Visualization:" receive a teal accent border (`rgba(20, 184, 166, 0.3)`) and an enhanced box shadow [frontend/nextjs/styles/markdown.css:187-193]().

### WebSocket Events
The `ImageGenerator` streams status updates via WebSockets:
- `image_planning`: Analysis of context started.
- `image_concepts_identified`: Found N visualization opportunities.
- `image_generating`: Individual image creation in progress.
- `images_ready`: All images are saved and ready.

**Sources:** [gpt_researcher/skills/image_generator.py:102-171](), [docs/docs/gpt-researcher/gptr/image_generation.md:162-170]()

---

# Page: Multi-Agent System Deep Dive

# Multi-Agent System Deep Dive

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [multi_agents/README.md](multi_agents/README.md)
- [multi_agents/agent.py](multi_agents/agent.py)
- [multi_agents/agents/__init__.py](multi_agents/agents/__init__.py)
- [multi_agents/agents/editor.py](multi_agents/agents/editor.py)
- [multi_agents/agents/human.py](multi_agents/agents/human.py)
- [multi_agents/agents/orchestrator.py](multi_agents/agents/orchestrator.py)
- [multi_agents/agents/plan_review.py](multi_agents/agents/plan_review.py)
- [multi_agents/agents/publisher.py](multi_agents/agents/publisher.py)
- [multi_agents/agents/researcher.py](multi_agents/agents/researcher.py)
- [multi_agents/agents/reviewer.py](multi_agents/agents/reviewer.py)
- [multi_agents/agents/reviser.py](multi_agents/agents/reviser.py)
- [multi_agents/agents/writer.py](multi_agents/agents/writer.py)
- [multi_agents/memory/draft.py](multi_agents/memory/draft.py)
- [multi_agents/memory/research.py](multi_agents/memory/research.py)
- [multi_agents/task.json](multi_agents/task.json)
- [tests/test_multi_agents_plan_revisions.py](tests/test_multi_agents_plan_revisions.py)

</details>



## Purpose and Scope

This document provides detailed technical documentation of the LangGraph-based multi-agent research system in GPT Researcher. The multi-agent mode represents an advanced alternative to standard research workflows, employing collaborative specialized agents to produce higher-quality research reports through iterative refinement and quality validation.

This page covers the multi-agent system architecture, workflow stages, agent roles, state management, and configuration. 

For more detailed information, see the following child pages:
- **[ChiefEditorAgent Orchestration](#10.1)** — Master coordinator and five-stage workflow.
- **[Specialized Agents](#10.2)** — Individual roles: Browser, Editor, Researcher, Reviewer, Revisor, Writer, Publisher.
- **[Review-Revision Workflow](#10.3)** — Iterative draft improvement via LangGraph `StateGraph`.
- **[Multi-Agent Configuration](#10.4)** — `task.json` and `STRATEGIC_LLM` settings.
- **[Multi-Agent State Management](#10.5)** — `ResearchState` and `DraftState` flow.
- **[AG2 Multi-Agent Alternative](#10.6)** — The AutoGen2-based orchestration alternative.

**Sources:** [multi_agents/README.md:1-10]()

---

## System Overview

The multi-agent system orchestrates eight specialized agents using LangGraph's state machine framework to conduct research through five distinct stages: planning, initial research, parallel section research with review-revision loops, writing, and publication. This architecture is inspired by the STORM paper and produces comprehensive 5-6 page research reports with validated quality [multi_agents/README.md:7-11]().

### Key Differences from Standard Research

| Aspect | Standard Research | Multi-Agent Research |
|--------|-------------------|---------------------|
| **Orchestration** | `ResearchConductor` linear workflow | `ChiefEditorAgent` with LangGraph state machine |
| **Quality Control** | Single-pass generation | Iterative review-revision loops |
| **Parallelization** | Sub-query parallel processing | Section-level parallel research with per-section workflows |
| **Agent Specialization** | Single `GPTResearcher` instance | Specialized agents (Researcher, Editor, Reviewer, etc.) |
| **LLM Usage** | `SMART_LLM` and `FAST_LLM` | Primarily `SMART_LLM` / `STRATEGIC_LLM` |

**Sources:** [multi_agents/README.md:13-24](), [multi_agents/agents/editor.py:126-144]()

---

## Architecture and Workflow

### High-Level Agent Orchestration

The following diagram maps the high-level flow to specific code entities and files.

```mermaid
graph TB
    subgraph "Entry & Orchestration"
        Start["multi_agents/main.py"] --> Chief["ChiefEditorAgent<br/>(orchestrator.py)"]
    end

    subgraph "Stage 1 & 2: Planning"
        Chief --> Browser["ResearchAgent.run_initial_research<br/>(researcher.py)"]
        Chief --> Editor["EditorAgent.plan_research<br/>(editor.py)"]
        Chief --> Human["HumanAgent.review_plan<br/>(human.py)"]
    end

    subgraph "Stage 3: Parallel Loop"
        Editor --> Parallel["asyncio.gather<br/>(editor.py:74)"]
        Parallel --> Loop["DraftState Workflow<br/>(editor.py:126-144)"]
    end

    subgraph "Stage 4 & 5: Finalization"
        Chief --> Writer["WriterAgent.run<br/>(writer.py)"]
        Chief --> Publisher["PublisherAgent.run<br/>(publisher.py)"]
    end

    Loop --> Researcher["ResearchAgent.run_depth_research"]
    Loop --> Reviewer["ReviewerAgent.run"]
    Loop --> Revisor["ReviserAgent.run"]
```

**Sources:** [multi_agents/agents/editor.py:126-144](), [multi_agents/agents/orchestrator.py:1-10](), [multi_agents/agents/human.py:10-59]()

### The Five-Stage Workflow

1.  **Planning Stage**: The `EditorAgent` plans the report outline based on initial research [multi_agents/agents/editor.py:22-50](). Optionally involves `HumanAgent` for feedback [multi_agents/agents/human.py:18-45]().
2.  **Data Collection**: Initial broad research is conducted to ground the planning phase via `ResearchAgent.run_initial_research` [multi_agents/agents/researcher.py:34-44]().
3.  **Review and Revision**: For each section, a `ResearchAgent` generates a draft [multi_agents/agents/researcher.py:46-58](), which a `ReviewerAgent` critiques [multi_agents/agents/reviewer.py:63-79](). A `ReviserAgent` then updates the draft [multi_agents/agents/reviser.py:54-74]().
4.  **Writing**: The `WriterAgent` compiles the sections, adding an introduction, conclusion, and references [multi_agents/agents/writer.py:94-142]().
5.  **Publication**: The `PublisherAgent` formats the final report into PDF, Docx, or Markdown [multi_agents/agents/publisher.py:55-61]().

For details, see [ChiefEditorAgent Orchestration](#10.1).

---

## Agent Roles and Implementation

The multi-agent system implements specialized agents located in `multi_agents/agents/` [multi_agents/agents/__init__.py:1-21]().

### Specialized Agent Summary

| Agent | File | Primary Responsibility |
|-------|------|------------------------|
| **Chief Editor** | `orchestrator.py` | Master coordinator managing the LangGraph state [multi_agents/agents/__init__.py:10](). |
| **Researcher** | `researcher.py` | Wraps `GPTResearcher` to perform web or local data retrieval [multi_agents/agents/researcher.py:13-23](). |
| **Editor** | `editor.py` | Plans the research outline and triggers parallel section workflows [multi_agents/agents/editor.py:13-15](). |
| **Reviewer** | `reviewer.py` | Validates section drafts against `task.json` guidelines [multi_agents/agents/reviewer.py:9-13](). |
| **Revisor** | `reviser.py` | Updates drafts based on feedback from the Reviewer [multi_agents/agents/reviser.py:15-19](). |
| **Writer** | `writer.py` | Synthesizes all researched sections into a cohesive report [multi_agents/agents/writer.py:16-20](). |
| **Publisher** | `publisher.py` | Converts the final markdown to PDF, DOCX, and other formats [multi_agents/agents/publisher.py:9-14](). |
| **Human** | `human.py` | Provides human-in-the-loop feedback for research plans [multi_agents/agents/human.py:4-8](). |

For details, see [Specialized Agents](#10.2).

---

## State Management and Flow

The system uses `TypedDict` objects to maintain state across asynchronous steps.

- **`ResearchState`**: The global state tracking the entire project from initial query to final publication [multi_agents/memory/research.py:5-20]().
- **`DraftState`**: A localized state used within the parallel review-revision loop for individual sections [multi_agents/memory/draft.py:5-10]().

### Review-Revision State Machine

```mermaid
stateDiagram-v2
    [*] --> researcher : run_depth_research
    researcher --> reviewer : draft
    reviewer --> reviser : feedback (if needed)
    reviser --> reviewer : revised_draft
    reviewer --> [*] : accept (review is None)
```

**Sources:** [multi_agents/agents/editor.py:135-142](), [multi_agents/agents/reviewer.py:79](), [multi_agents/agents/reviser.py:71-74]()

For details, see [Multi-Agent State Management](#10.5) and [Review-Revision Workflow](#10.3).

---

## Configuration and Customization

The multi-agent system is primarily configured via `multi_agents/task.json` [multi_agents/task.json:1-19]().

### Key Configuration Parameters
- **`model`**: The LLM used by agents (e.g., `gpt-4o`) [multi_agents/task.json:12]().
- **`max_sections`**: Limits the number of subtopics researched [multi_agents/task.json:3]().
- **`include_human_feedback`**: If `true`, the `HumanAgent` is engaged [multi_agents/task.json:10]().
- **`follow_guidelines`**: If `true`, enables the iterative `Reviewer` and `Revisor` loop [multi_agents/task.json:11]().

For details, see [Multi-Agent Configuration](#10.4).

---

## AG2 Alternative

In addition to LangGraph, GPT Researcher supports **AG2 (AutoGen2)** for multi-agent orchestration. This alternative is located in `multi_agents_ag2/` and mirrors the specialized agent flow using the AG2 framework.

For details, see [AG2 Multi-Agent Alternative](#10.6).

---

# Page: ChiefEditorAgent Orchestration

# ChiefEditorAgent Orchestration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/utils.py](backend/utils.py)
- [multi_agents/README.md](multi_agents/README.md)
- [multi_agents/agent.py](multi_agents/agent.py)
- [multi_agents/agents/human.py](multi_agents/agents/human.py)
- [multi_agents/agents/orchestrator.py](multi_agents/agents/orchestrator.py)
- [multi_agents/agents/plan_review.py](multi_agents/agents/plan_review.py)
- [multi_agents/agents/utils/file_formats.py](multi_agents/agents/utils/file_formats.py)
- [multi_agents/langgraph.json](multi_agents/langgraph.json)
- [multi_agents/main.py](multi_agents/main.py)
- [multi_agents/memory/research.py](multi_agents/memory/research.py)
- [multi_agents/requirements.txt](multi_agents/requirements.txt)
- [multi_agents/task.json](multi_agents/task.json)
- [tests/test_multi_agents_plan_revisions.py](tests/test_multi_agents_plan_revisions.py)

</details>



## Purpose and Scope

The `ChiefEditorAgent` is the master coordinator of the LangGraph-based multi-agent research system. It manages a team of specialized agents—including the Researcher, Editor, Writer, and Publisher—through a structured five-stage workflow: planning, research, review, writing, and publication. Its primary responsibility is to maintain the `ResearchState`, orchestrate the flow of data between agents, and handle human-in-the-loop interactions.

Sources: [multi_agents/agents/orchestrator.py:23-24](), [multi_agents/README.md:15-24](), [multi_agents/main.py:40-50]()

---

## Five-Stage Workflow Architecture

The `ChiefEditorAgent` implements a sequential five-stage research pipeline inspired by the STORM paper. The workflow is built using LangGraph's `StateGraph`, where each node represents an agent's functional entry point.

### Workflow Stages and State Flow

```mermaid
graph TB
    subgraph Stage1["Stage 1: Planning (Exploration)"]
        Browser["node: 'browser' (ResearchAgent.run_initial_research)"]
    end
    
    subgraph Stage2["Stage 2: Planning (Outline)"]
        Planner["node: 'planner' (EditorAgent.plan_research)"]
        Human["node: 'human' (HumanAgent.review_plan)"]
        Router{"route_human_feedback"}
    end
    
    subgraph Stage3["Stage 3: Data Collection & Analysis"]
        Researcher["node: 'researcher' (EditorAgent.run_parallel_research)"]
    end
    
    subgraph Stage4["Stage 4: Writing & Submission"]
        Writer["node: 'writer' (WriterAgent.run)"]
    end
    
    subgraph Stage5["Stage 5: Publication"]
        Publisher["node: 'publisher' (PublisherAgent.run)"]
    end

    Browser --> Planner
    Planner --> Human
    Human --> Router
    Router -->|"revise"| Planner
    Router -->|"accept"| Researcher
    Researcher --> Writer
    Writer --> Publisher
    Publisher --> END[("END")]
```

Sources: [multi_agents/agents/orchestrator.py:56-85](), [multi_agents/README.md:26-32]()

---

## Technical Implementation

### The ChiefEditorAgent Class
The class is initialized with a `task` dictionary (typically from `task.json`), optional WebSocket handlers for streaming, and a research `tone`. Upon initialization, it generates a unique `task_id` and creates an output directory for artifacts.

**Key Methods:**
- `init_research_team()`: Initializes the 8 specialized agents and compiles the LangGraph `StateGraph` [multi_agents/agents/orchestrator.py:92-95]().
- `run_research_task()`: Compiles the workflow and executes it using `ainvoke` with the provided task and configuration [multi_agents/agents/orchestrator.py:104-127]().
- `_initialize_agents()`: Instantiates the `WriterAgent`, `EditorAgent`, `ResearchAgent`, `PublisherAgent`, and `HumanAgent` with shared communication channels [multi_agents/agents/orchestrator.py:47-54]().

### ResearchState Management
The `ResearchState` is a `TypedDict` that serves as the "single source of truth" passed between nodes.

| Field | Description | Source |
| :--- | :--- | :--- |
| `task` | The configuration from `task.json` | [multi_agents/memory/research.py:6]() |
| `initial_research` | Summary from the broad internet search | [multi_agents/memory/research.py:7]() |
| `sections` | List of subtopics/outline items | [multi_agents/memory/research.py:8]() |
| `research_data` | List of drafts for each section | [multi_agents/memory/research.py:9]() |
| `report` | The final compiled string of the research paper | [multi_agents/memory/research.py:20]() |

Sources: [multi_agents/memory/research.py:5-22]()

---

## Human-in-the-Loop & Revision Logic

The orchestration includes a critical feedback loop during the planning stage. The `HumanAgent` prompts the user for feedback on the proposed research outline.

### Plan Revision Flow
The system enforces a limit on how many times a human can request plan revisions to prevent infinite loops.

```mermaid
graph LR
    HumanNode["HumanAgent.review_plan"]
    RouteFunc["route_human_feedback()"]
    RevisionCount{"plan_revision_count > max?"}
    Error["MaxPlanRevisionsExceededError"]
    Revise["'revise' -> Planner"]
    Accept["'accept' -> Researcher"]

    HumanNode --> RouteFunc
    RouteFunc --> RevisionCount
    RevisionCount -->|"Yes"| Error
    RevisionCount -->|"No"| Revise
    RouteFunc -->|"No Feedback"| Accept
```

- **Configuration**: The limit is defined by `max_plan_revisions` in `task.json` (defaulting to 3) [multi_agents/agents/plan_review.py:1](), [multi_agents/task.json:4]().
- **Logic**: If `human_feedback` is provided, `plan_revision_count` is incremented. If it exceeds the limit, a `RuntimeError` is raised [multi_agents/agents/plan_review.py:15-23]().

Sources: [multi_agents/agents/plan_review.py:8-23](), [multi_agents/agents/human.py:50-59]()

---

## Data Flow and Publication

Once the `WriterAgent` compiles the final text, the `PublisherAgent` is responsible for multi-format output.

### Publication Orchestration
The `ChiefEditorAgent` passes the `output_dir` (unique to the run) to the `PublisherAgent` [multi_agents/agents/orchestrator.py:52](). The publisher then uses utility functions to write the final `report` from the state into the filesystem.

| Format | Utility Function | Logic |
| :--- | :--- | :--- |
| **Markdown** | `write_text_to_md` | Writes raw UTF-8 text to `.md` |
| **PDF** | `write_md_to_pdf` | Uses `md2pdf` with `pdf_styles.css` |
| **DOCX** | `write_md_to_word` | Converts MD to HTML, then uses `htmldocx` |

Sources: [multi_agents/agents/utils/file_formats.py:24-104](), [backend/utils.py:62-130]()

### Strategic LLM Override
During task initialization in `main.py`, the `ChiefEditorAgent`'s task model can be dynamically overridden by the `STRATEGIC_LLM` environment variable. This ensures the orchestrator and its sub-agents use the most capable model available for coordination tasks.

Sources: [multi_agents/main.py:29-38]()

---

# Page: Specialized Agents

# Specialized Agents

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [multi_agents/README.md](multi_agents/README.md)
- [multi_agents/agent.py](multi_agents/agent.py)
- [multi_agents/agents/__init__.py](multi_agents/agents/__init__.py)
- [multi_agents/agents/editor.py](multi_agents/agents/editor.py)
- [multi_agents/agents/human.py](multi_agents/agents/human.py)
- [multi_agents/agents/orchestrator.py](multi_agents/agents/orchestrator.py)
- [multi_agents/agents/plan_review.py](multi_agents/agents/plan_review.py)
- [multi_agents/agents/publisher.py](multi_agents/agents/publisher.py)
- [multi_agents/agents/researcher.py](multi_agents/agents/researcher.py)
- [multi_agents/agents/reviewer.py](multi_agents/agents/reviewer.py)
- [multi_agents/agents/reviser.py](multi_agents/agents/reviser.py)
- [multi_agents/agents/writer.py](multi_agents/agents/writer.py)
- [multi_agents/memory/draft.py](multi_agents/memory/draft.py)
- [multi_agents/memory/research.py](multi_agents/memory/research.py)
- [multi_agents/task.json](multi_agents/task.json)
- [tests/test_multi_agents_plan_revisions.py](tests/test_multi_agents_plan_revisions.py)

</details>



This document details the specialized agent classes in the multi-agent research system: `ResearchAgent`, `EditorAgent`, `ReviewerAgent`, `ReviserAgent`, `WriterAgent`, `PublisherAgent`, and the `HumanAgent`. Each agent encapsulates a specific responsibility in the collaborative research workflow, from initial research through to publication.

---

## Agent Architecture Overview

The multi-agent system consists of specialized agents instantiated with common parameters for communication and coordination. All agents share a similar initialization pattern and interact through typed state dictionaries defined in `multi_agents/memory/`.

### Specialized Agent Team
The research team is composed of the following roles:
- **Human**: Oversees the process and provides feedback [multi_agents/README.md:17]().
- **Chief Editor**: Coordinates the team using LangGraph [multi_agents/README.md:18]().
- **Researcher**: Conducts in-depth research using `gpt-researcher` [multi_agents/README.md:19]().
- **Editor**: Plans the research outline and structure [multi_agents/README.md:20]().
- **Reviewer**: Validates research results against criteria [multi_agents/README.md:21]().
- **Revisor**: Revises results based on reviewer feedback [multi_agents/README.md:22]().
- **Writer**: Compiles and writes the final report [multi_agents/README.md:23]().
- **Publisher**: Publishes the report in multiple formats [multi_agents/README.md:24]().

**Sources:** [multi_agents/README.md:15-24](), [multi_agents/agents/__init__.py:1-21]()

### Common Initialization Parameters

Most agents accept standard parameters during initialization to enable real-time communication:

| Parameter | Type | Purpose |
|-----------|------|---------|
| `websocket` | WebSocket | Real-time communication channel for streaming updates [multi_agents/agents/researcher.py:8]() |
| `stream_output` | Callable | Async function to send messages via WebSocket [multi_agents/agents/researcher.py:9]() |
| `tone` | Tone | Research tone (Objective, Formal, etc.) [multi_agents/agents/researcher.py:11]() |
| `headers` | dict | HTTP headers for API requests [multi_agents/agents/researcher.py:10]() |

**Sources:** [multi_agents/agents/researcher.py:7-11](), [multi_agents/agents/editor.py:16-20](), [multi_agents/agents/writer.py:17-20]()

---

## ResearchAgent

The `ResearchAgent` is a wrapper around the core `GPTResearcher` class. It serves as the bridge between the multi-agent system and the standard research engine [multi_agents/agents/researcher.py:1]().

### Core Methods

#### `research()`
Instantiates and executes a `GPTResearcher` instance.
- **Implementation**: Calls `conduct_research()` followed by `write_report()` [multi_agents/agents/researcher.py:19-21]().
- **Parameters**: Supports `query`, `report_type`, `source`, and `tone` [multi_agents/agents/researcher.py:13-14]().

#### `run_initial_research()`
Executes the first research phase to gather context for the `EditorAgent` to plan the outline [multi_agents/agents/researcher.py:34-44]().

#### `run_depth_research()`
Executes in-depth research for a specific section topic within a `DraftState` workflow [multi_agents/agents/researcher.py:46-58]().

**Sources:** [multi_agents/agents/researcher.py:13-58]()

---

## EditorAgent

The `EditorAgent` orchestrates the multi-section research process. It plans the report structure and coordinates parallel execution of section-specific research tasks.

### Planning and Workflow
- **`plan_research()`**: Uses an LLM to generate a JSON outline containing a `title`, `date`, and `sections` (maximum defined by `max_sections`) [multi_agents/agents/editor.py:22-50]().
- **`run_parallel_research()`**: 
  1. Initializes `ResearchAgent`, `ReviewerAgent`, and `ReviserAgent` [multi_agents/agents/editor.py:118-124]().
  2. Creates a `StateGraph` using `DraftState` [multi_agents/agents/editor.py:126-129]().
  3. Defines a node sequence: `researcher` -> `reviewer` -> `reviser` [multi_agents/agents/editor.py:131-133]().
  4. Implements a conditional edge from `reviewer` to either `END` (accept) or `reviser` (revise) [multi_agents/agents/editor.py:138-142]().

**Sources:** [multi_agents/agents/editor.py:22-144]()

---

## ReviewerAgent and ReviserAgent

These agents form the quality control loop for individual report sections.

### ReviewerAgent
- **Role**: Validates drafts against guidelines provided in `task.json` [multi_agents/agents/reviewer.py:21-22]().
- **Logic**: If the draft meets all guidelines, it returns `None` to signal acceptance [multi_agents/agents/reviewer.py:34](). Otherwise, it returns feedback strings [multi_agents/agents/reviewer.py:61]().

### ReviserAgent
- **Role**: Updates drafts based on `ReviewerAgent` notes [multi_agents/agents/reviser.py:33]().
- **Output**: Returns a JSON object containing the revised `draft` and `revision_notes` explaining the changes [multi_agents/agents/reviser.py:5-12]().

**Sources:** [multi_agents/agents/reviewer.py:15-79](), [multi_agents/agents/reviser.py:21-74]()

---

## WriterAgent

The `WriterAgent` synthesizes all section drafts into a cohesive document by generating the "glue" content.

- **`write_sections()`**: Generates an introduction, conclusion, and table of contents in JSON format [multi_agents/agents/writer.py:32-67]().
- **Source Handling**: Must include relevant sources as markdown hyperlinks in the introduction and conclusion [multi_agents/agents/writer.py:54-55]().
- **Header Revision**: Can revise header labels to match specific guidelines (e.g., language requirements) [multi_agents/agents/writer.py:69-92]().

**Sources:** [multi_agents/agents/writer.py:6-142]()

---

## PublisherAgent

The `PublisherAgent` handles final document assembly and file generation.

- **`generate_layout()`**: Combines the title, date, introduction, table of contents, research sections, conclusion, and references into a single markdown string [multi_agents/agents/publisher.py:22-53]().
- **Multi-format Support**: Uses utility functions to convert markdown to PDF, DOCX, and standard Markdown files based on `publish_formats` in the task configuration [multi_agents/agents/publisher.py:55-61]().

**Sources:** [multi_agents/agents/publisher.py:16-71]()

---

## HumanAgent

The `HumanAgent` enables "Human-in-the-loop" (HITL) interactions during the research process.

- **`review_plan()`**: Interrupts the workflow to request feedback on the planned research topics [multi_agents/agents/human.py:10-14]().
- **Communication**: 
  - If a `websocket` is present, it streams a request and waits for a `human_feedback` message type [multi_agents/agents/human.py:20-33]().
  - Otherwise, it falls back to a standard console `input()` prompt [multi_agents/agents/human.py:43-45]().

**Sources:** [multi_agents/agents/human.py:4-52]()

---

## Data Flow and Code Entity Mapping

The following diagrams illustrate how natural language tasks translate into specific code entities and how data flows between specialized agents.

### Entity Relationship Diagram
This diagram bridges the conceptual "Agent" with the specific Python classes and state objects.

```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        Task["Research Task (task.json)"]
        Feedback["Human Feedback"]
    end

    subgraph "CodeEntitySpace"
        State["ResearchState (TypedDict)"]
        Draft["DraftState (TypedDict)"]
        
        Editor["EditorAgent (editor.py)"]
        Researcher["ResearchAgent (researcher.py)"]
        Reviewer["ReviewerAgent (reviewer.py)"]
        Reviser["ReviserAgent (reviser.py)"]
        Writer["WriterAgent (writer.py)"]
        Publisher["PublisherAgent (publisher.py)"]
        Human["HumanAgent (human.py)"]
        
        GPTR["GPTResearcher (core)"]
    end

    Task --> State
    Human -- "review_plan()" --> Feedback
    Feedback --> State
    
    State -- "plan_research()" --> Editor
    Editor -- "run_depth_research()" --> Researcher
    Researcher --> GPTR
    
    Researcher -- "manages" --> Draft
    Draft -- "review_draft()" --> Reviewer
    Reviewer -- "revise_draft()" --> Reviser
    
    State -- "write_sections()" --> Writer
    State -- "publish_research_report()" --> Publisher
```

**Sources:** [multi_agents/agents/editor.py:13-20](), [multi_agents/memory/research.py:5-19](), [multi_agents/memory/draft.py:5-10](), [multi_agents/agents/human.py:10-14]()

### Parallel Research Execution Flow
This diagram details the `run_parallel_research` implementation in `EditorAgent`.

```mermaid
sequenceDiagram
    participant E as "EditorAgent"
    participant W as "StateGraph (Workflow)"
    participant R as "ResearchAgent"
    participant RV as "ReviewerAgent"
    participant RS as "ReviserAgent"

    E->>E: "_initialize_agents()"
    E->>W: "_create_workflow(DraftState)"
    Note over W: "Entry: researcher node"
    
    par "For each Section in sections"
        E->>W: "ainvoke(task_input)"
        W->>R: "run_depth_research(draft_state)"
        R-->>W: "{\"draft\": content}"
        W->>RV: "run(draft_state)"
        
        alt "review is None"
            RV-->>W: "{\"review\": None}"
            W-->>E: "Final Draft"
        else "review exists"
            RV-->>W: "{\"review\": feedback}"
            W->>RS: "run(draft_state)"
            RS-->>W: "{\"draft\": revised, \"notes\": notes}"
            W->>RV: "run(draft_state)"
        end
    end
    E->>E: "Aggregate research_results"
```

**Sources:** [multi_agents/agents/editor.py:52-77](), [multi_agents/agents/editor.py:126-144](), [multi_agents/agents/researcher.py:46-58]()

---

# Page: Review-Revision Workflow

# Review-Revision Workflow

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [multi_agents/README.md](multi_agents/README.md)
- [multi_agents/agent.py](multi_agents/agent.py)
- [multi_agents/agents/__init__.py](multi_agents/agents/__init__.py)
- [multi_agents/agents/editor.py](multi_agents/agents/editor.py)
- [multi_agents/agents/human.py](multi_agents/agents/human.py)
- [multi_agents/agents/orchestrator.py](multi_agents/agents/orchestrator.py)
- [multi_agents/agents/plan_review.py](multi_agents/agents/plan_review.py)
- [multi_agents/agents/publisher.py](multi_agents/agents/publisher.py)
- [multi_agents/agents/researcher.py](multi_agents/agents/researcher.py)
- [multi_agents/agents/reviewer.py](multi_agents/agents/reviewer.py)
- [multi_agents/agents/reviser.py](multi_agents/agents/reviser.py)
- [multi_agents/agents/writer.py](multi_agents/agents/writer.py)
- [multi_agents/memory/draft.py](multi_agents/memory/draft.py)
- [multi_agents/memory/research.py](multi_agents/memory/research.py)
- [multi_agents/task.json](multi_agents/task.json)
- [tests/test_multi_agents_plan_revisions.py](tests/test_multi_agents_plan_revisions.py)

</details>



## Purpose and Scope

This document explains the review-revision workflow in the Multi-Agent System, which ensures quality control for each section of a research report through iterative refinement. This workflow is part of Stage 3 of the multi-agent research pipeline and operates on individual section drafts in parallel.

For information about the overall multi-agent system architecture, see [Multi-Agent Framework](#4.4). For details on agent roles and responsibilities, see [Specialized Agents](#10.2). For configuration of multi-agent behavior, see [Multi-Agent Configuration](#10.4).

## Overview

The review-revision workflow implements an iterative quality assurance loop where each research section draft is validated against configurable guidelines and revised until it meets quality standards. The workflow uses LangGraph's `StateGraph` to orchestrate three specialized agents in a conditional loop.

**Workflow Stages:**

| Stage | Agent | Responsibility | Outcome |
|-------|-------|---------------|---------|
| 1. Draft Creation | `ResearchAgent` | Conducts in-depth research on section topic | Initial draft |
| 2. Quality Review | `ReviewerAgent` | Validates draft against guidelines | Feedback or `None` |
| 3. Revision | `ReviserAgent` | Improves draft based on feedback | Revised draft + notes |
| 4. Re-review | `ReviewerAgent` | Validates revised draft | Iterate or accept |

The loop terminates when `ReviewerAgent` returns `None`, indicating the draft meets all quality criteria.

**Sources:** [multi_agents/README.md:26-50](), [multi_agents/agents/editor.py:126-144]()

## LangGraph StateGraph Architecture

The workflow is implemented as a LangGraph `StateGraph` with conditional edges that determine whether to accept a draft or send it for revision.

```mermaid
graph TB
    Entry["Entry Point"]
    Researcher["researcher<br/>(ResearchAgent.run_depth_research)"]
    Reviewer["reviewer<br/>(ReviewerAgent.run)"]
    Reviser["reviser<br/>(ReviserAgent.run)"]
    End["END"]
    
    Entry --> Researcher
    Researcher --> Reviewer
    Reviewer -->|"review is None<br/>(accept)"| End
    Reviewer -->|"review is not None<br/>(revise)"| Reviser
    Reviser --> Reviewer
```

**Graph Construction**

The `EditorAgent._create_workflow()` method constructs the `StateGraph` using the `DraftState` typed dictionary:

```python
workflow = StateGraph(DraftState)

workflow.add_node("researcher", agents["research"].run_depth_research)
workflow.add_node("reviewer", agents["reviewer"].run)
workflow.add_node("reviser", agents["reviser"].run)

workflow.set_entry_point("researcher")
workflow.add_edge("researcher", "reviewer")
workflow.add_edge("reviser", "reviewer")
workflow.add_conditional_edges(
    "reviewer",
    lambda draft: "accept" if draft["review"] is None else "revise",
    {"accept": END, "revise": "reviser"},
)
```

The conditional edge function examines the `review` field in `DraftState`:
- If `review` is `None`, the draft is accepted and the workflow terminates at `END`.
- If `review` contains feedback string, the draft is sent to `ReviserAgent` for improvement.

**Sources:** [multi_agents/agents/editor.py:126-144]()

## DraftState Management

The workflow operates on a `DraftState` TypedDict that maintains state throughout the review-revision loop.

**DraftState Schema**

| Field | Type | Description |
|-------|------|-------------|
| `task` | `dict` | Task configuration including model, guidelines, verbose flag |
| `topic` | `str` | Section topic being researched |
| `draft` | `dict` | Current draft content (mapped by subtopic name) |
| `review` | `str` | Reviewer feedback or `None` if accepted |
| `revision_notes` | `str` | Revisor's notes about changes made |

**State Evolution Example:**

1. **After Researcher**: `{"task": {...}, "topic": "AI Market Trends", "draft": {"AI Market Trends": "..."}}`
2. **After First Review**: `{"...", "review": "Missing supporting sources for claims"}`
3. **After Revision**: `{"...", "draft": {"AI Market Trends": "...revised..."}, "revision_notes": "Added 3 citations"}`
4. **After Re-review**: `{"...", "review": None}` → Workflow terminates

**Sources:** [multi_agents/memory/draft.py:1-10](), [multi_agents/agents/researcher.py:56-58]()

## ReviewerAgent Operation

The `ReviewerAgent` validates draft quality against configurable guidelines specified in `task.json`.

### Review Logic

```mermaid
flowchart TD
    Start["ReviewerAgent.run()"]
    CheckGuidelines{"follow_guidelines<br/>in task?"}
    SkipReview["Return<br/>{review: None}"]
    PerformReview["ReviewerAgent.review_draft()"]
    BuildPrompt["Build prompt with<br/>guidelines + draft"]
    CallModel["call_model()<br/>with SMART_LLM"]
    CheckResponse{"Response<br/>contains 'None'?"}
    ReturnNone["Return None<br/>(accept draft)"]
    ReturnFeedback["Return feedback<br/>(revise draft)"]
    
    Start --> CheckGuidelines
    CheckGuidelines -->|"False"| SkipReview
    CheckGuidelines -->|"True"| PerformReview
    PerformReview --> BuildPrompt
    BuildPrompt --> CallModel
    CallModel --> CheckResponse
    CheckResponse -->|"Yes"| ReturnNone
    CheckResponse -->|"No"| ReturnFeedback
```

### Prompt Construction

The `ReviewerAgent.review_draft()` method constructs a prompt that instructs the LLM to validate the draft:

**System Prompt:**
The `TEMPLATE` constant defines the system persona as an expert research article reviewer. [multi_agents/agents/reviewer.py:4-6]()

**User Prompt Structure:**
- Guidelines are extracted and formatted from `task.get("guidelines")`. [multi_agents/agents/reviewer.py:22]()
- Current draft is pulled from `draft_state.get("draft")`. [multi_agents/agents/reviewer.py:37]()
- If this is a re-review, the prompt includes `revision_notes` to inform the reviewer of previous changes. [multi_agents/agents/reviewer.py:25-29]()

**Iterative Review Handling:**
When a draft has already been revised once, the prompt explicitly asks the reviewer to provide additional feedback ONLY if critical to prevent infinite loops. [multi_agents/agents/reviewer.py:27-28]()

**Sources:** [multi_agents/agents/reviewer.py:1-80]()

## ReviserAgent Operation

The `ReviserAgent` improves drafts based on reviewer feedback, maintaining consistency with other draft aspects.

### Revision Process

```mermaid
flowchart TD
    Start["ReviserAgent.run()"]
    BuildPrompt["Build revision prompt<br/>with draft + review"]
    CallModel["call_model()<br/>JSON format<br/>SMART_LLM"]
    ParseResponse["Parse JSON response"]
    ExtractDraft["Extract revised draft"]
    ExtractNotes["Extract revision_notes"]
    Return["Return<br/>{draft, revision_notes}"]
    
    Start --> BuildPrompt
    BuildPrompt --> CallModel
    CallModel --> ParseResponse
    ParseResponse --> ExtractDraft
    ParseResponse --> ExtractNotes
    ExtractDraft --> Return
    ExtractNotes --> Return
```

### Prompt Template

The revisor uses a structured JSON response format as defined in `sample_revision_notes`. [multi_agents/agents/reviser.py:5-12]()

**User Prompt Instructions:**
The revisor is instructed to write a new draft addressing all points raised by the reviewer while keeping all other aspects of the draft the same. [multi_agents/agents/reviser.py:38-40]()

**Sources:** [multi_agents/agents/reviser.py:21-52]()

## Integration with EditorAgent

The `EditorAgent.run_parallel_research()` method orchestrates parallel execution of the review-revision workflow for all report sections using `asyncio.gather`. [multi_agents/agents/editor.py:73-75]()

### Parallel Workflow Execution

```mermaid
flowchart LR
    EditorStart["EditorAgent.<br/>run_parallel_research()"]
    InitAgents["Initialize<br/>ResearchAgent<br/>ReviewerAgent<br/>ReviserAgent"]
    CreateWorkflow["EditorAgent._create_workflow()<br/>Build StateGraph"]
    CompileChain["chain = workflow.compile()"]
    
    subgraph "Parallel Execution"
        Section1["chain.ainvoke()<br/>Section 1"]
        Section2["chain.ainvoke()<br/>Section 2"]
        Section3["chain.ainvoke()<br/>Section N"]
    end
    
    Gather["asyncio.gather(*final_drafts)"]
    ExtractResults["Extract 'draft' field<br/>from each result"]
    Return["Return<br/>{research_data: [drafts]}"]
    
    EditorStart --> InitAgents
    InitAgents --> CreateWorkflow
    CreateWorkflow --> CompileChain
    CompileChain --> Section1
    CompileChain --> Section2
    CompileChain --> Section3
    Section1 --> Gather
    Section2 --> Gather
    Section3 --> Gather
    Gather --> ExtractResults
    ExtractResults --> Return
```

Each section runs through the complete review-revision loop independently and in parallel, ensuring all sections meet quality standards before proceeding to the writing stage.

**Sources:** [multi_agents/agents/editor.py:52-77]()

## Configuration and Guidelines

The review-revision workflow behavior is controlled by configuration in `task.json`.

### Key Configuration Parameters

| Parameter | Type | Description | Effect on Workflow |
|-----------|------|-------------|-------------------|
| `follow_guidelines` | `bool` | Enable/disable quality review | If `false`, `ReviewerAgent` skips review logic. [multi_agents/agents/reviewer.py:78]() |
| `guidelines` | `List[str]` | Quality criteria for drafts | Used by `ReviewerAgent` to validate content. [multi_agents/agents/reviewer.py:22]() |
| `model` | `str` | LLM model for agents | Used for both reviewing and revising. [multi_agents/agents/reviewer.py:44](), [multi_agents/agents/reviser.py:49]() |
| `verbose` | `bool` | Enable detailed logging | Controls printing of feedback and notes. [multi_agents/agents/reviewer.py:46]() |

**Sources:** [multi_agents/task.json:1-18](), [multi_agents/README.md:65-96]()

## Workflow Execution Flow

### Complete Section Processing

The following diagram shows a complete execution trace for one section through the review-revision workflow:

```mermaid
sequenceDiagram
    participant Editor as EditorAgent
    participant WF as StateGraph Workflow
    participant Researcher as ResearchAgent
    participant Reviewer as ReviewerAgent
    participant Revisor as ReviserAgent
    participant LLM as Language Model
    
    Editor->>WF: chain.ainvoke(task_input)
    Note over WF: DraftState: {task, topic}
    
    WF->>Researcher: run_depth_research(draft_state)
    Researcher->>Researcher: GPTResearcher.conduct_research()
    Researcher->>Researcher: GPTResearcher.write_report()
    Researcher-->>WF: {draft: section_content}
    
    WF->>Reviewer: ReviewerAgent.run(draft_state)
    Reviewer->>LLM: call_model(review_prompt)
    LLM-->>Reviewer: "Missing citations for claims"
    Reviewer-->>WF: {review: "Missing citations..."}
    
    Note over WF: Conditional: review != None<br/>Route to reviser
    
    WF->>Revisor: ReviserAgent.run(draft_state)
    Revisor->>LLM: call_model(revision_prompt)
    LLM-->>Revisor: {draft: revised, revision_notes: "Added 3 citations"}
    Revisor-->>WF: {draft: revised, revision_notes: "..."}
    
    WF->>Reviewer: ReviewerAgent.run(draft_state) [re-review]
    Reviewer->>LLM: call_model(review_prompt + revision_notes)
    LLM-->>Reviewer: "None" (draft acceptable)
    Reviewer-->>WF: {review: None}
    
    Note over WF: Conditional: review == None<br/>Route to END
    
    WF-->>Editor: {draft: final_section_content}
```

**Sources:** [multi_agents/agents/editor.py:52-77](), [multi_agents/agents/researcher.py:46-58](), [multi_agents/agents/reviewer.py:63-79](), [multi_agents/agents/reviser.py:54-74]()

## WebSocket Streaming Integration

The review-revision workflow integrates with the WebSocket communication system to stream real-time progress updates.

### Logging Points

| Agent | Log Type | Message | Trigger |
|-------|----------|---------|---------|
| `ReviewerAgent` | `review_feedback` | `"Review feedback is: {response}..."` | After LLM review. [multi_agents/agents/reviewer.py:51]() |
| `ReviserAgent` | `revision_notes` | `"Revision notes: {notes}"` | After revision completion. [multi_agents/agents/reviser.py:63]() |
| `EditorAgent` | `parallel_research` | `"Running parallel research for: {queries}"` | Before parallel execution. [multi_agents/agents/editor.py:152]() |
| `ResearchAgent` | `depth_research` | `"Running in depth research on: {topic}"` | Before section research. [multi_agents/agents/researcher.py:53]() |

**Sources:** [multi_agents/agents/reviewer.py:46-57](), [multi_agents/agents/reviser.py:58-69](), [multi_agents/agents/editor.py:146-159]()

---

# Page: Multi-Agent Configuration

# Multi-Agent Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/utils.py](backend/utils.py)
- [multi_agents/README.md](multi_agents/README.md)
- [multi_agents/agent.py](multi_agents/agent.py)
- [multi_agents/agents/human.py](multi_agents/agents/human.py)
- [multi_agents/agents/orchestrator.py](multi_agents/agents/orchestrator.py)
- [multi_agents/agents/plan_review.py](multi_agents/agents/plan_review.py)
- [multi_agents/agents/utils/file_formats.py](multi_agents/agents/utils/file_formats.py)
- [multi_agents/langgraph.json](multi_agents/langgraph.json)
- [multi_agents/main.py](multi_agents/main.py)
- [multi_agents/memory/research.py](multi_agents/memory/research.py)
- [multi_agents/requirements.txt](multi_agents/requirements.txt)
- [multi_agents/task.json](multi_agents/task.json)
- [tests/test_multi_agents_plan_revisions.py](tests/test_multi_agents_plan_revisions.py)

</details>



## Purpose and Scope

This page documents the configuration system for the LangGraph-based multi-agent research framework. The multi-agent system uses a dedicated `task.json` file to configure research behavior, agent parameters, and output formats. It also leverages the `STRATEGIC_LLM` environment variable for high-level model orchestration and provides mechanisms for human-in-the-loop feedback. For information about the multi-agent system architecture itself, see [Multi-Agent Framework]() and [Multi-Agent System Deep Dive](). For general GPT Researcher configuration, see [Configuration System]().

---

## Configuration File Overview

The multi-agent system is primarily configured via `task.json`, a JSON file located in the `multi_agents/` directory. This file defines all aspects of the research task including the query, model selection, quality controls, and output formats.

**File Location:** [multi_agents/task.json:1-19]()

**Loading Mechanism:** The configuration is loaded by the `open_task()` function in [multi_agents/main.py:17-38](), which:
1. Reads `task.json` from the `multi_agents/` directory [multi_agents/main.py:19-24]().
2. Validates that a task is present [multi_agents/main.py:26-27]().
3. Optionally overrides the `model` field with the `STRATEGIC_LLM` environment variable if defined [multi_agents/main.py:29-37]().

### Configuration Data Flow
The following diagram bridges the "Natural Language Space" (User Intent) to the "Code Entity Space" (System Implementation).

**Diagram: Configuration Injection Flow**
```mermaid
graph TD
    UserIntent["'Research Query & Guidelines'"]
    TaskJSON["task.json<br/>(multi_agents/task.json)"]
    EnvVar["STRATEGIC_LLM<br/>(Environment Variable)"]
    
    subgraph Code_Entity_Space ["Code Entity Space"]
        OpenTask["open_task()<br/>(multi_agents/main.py)"]
        ChiefEditor["ChiefEditorAgent<br/>(multi_agents/agents/orchestrator.py)"]
        ResearchState["ResearchState<br/>(multi_agents/memory/research.py)"]
    end

    UserIntent -.->|"defines"| TaskJSON
    TaskJSON -->|"read by"| OpenTask
    EnvVar -->|"overrides 'model' in"| OpenTask
    OpenTask -->|"returns task dict to"| ChiefEditor
    ChiefEditor -->|"initializes"| ResearchState
```
Sources: [multi_agents/main.py:17-38](), [multi_agents/memory/research.py:5-22]()

---

## Configuration Parameters Reference

The following table documents all available configuration parameters in `task.json`:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | `string` | Yes | - | The research query or topic to investigate [multi_agents/README.md:66]() |
| `model` | `string` | No | `"gpt-4o"` | The LLM model to use for all agents. Overridden by `STRATEGIC_LLM` env var [multi_agents/main.py:29-37]() |
| `max_sections` | `integer` | No | `3` | Maximum number of research sections/subtopics to generate [multi_agents/README.md:68]() |
| `max_plan_revisions` | `integer` | No | `3` | Max human-requested plan revisions before workflow exits [multi_agents/README.md:69](), [multi_agents/agents/plan_review.py:1]() |
| `include_human_feedback` | `boolean` | No | `false` | Whether to pause for human feedback after planning phase [multi_agents/README.md:70]() |
| `publish_formats` | `object` | No | All `true` | Specifies output formats: `{"markdown": bool, "pdf": bool, "docx": bool}` [multi_agents/README.md:71]() |
| `source` | `string` | No | `"web"` | Research data source. Options: `"web"` or `"local"` [multi_agents/README.md:72]() |
| `follow_guidelines` | `boolean` | No | `false` | Whether to enforce quality guidelines via agents [multi_agents/README.md:73]() |
| `guidelines` | `array[string]` | No | `[]` | List of guidelines that the report must follow [multi_agents/README.md:74]() |
| `verbose` | `boolean` | No | `true` | Whether to output detailed logging information [multi_agents/README.md:75]() |

Sources: [multi_agents/README.md:63-98](), [multi_agents/task.json:1-19](), [multi_agents/agents/plan_review.py:1-23]()

---

## STRATEGIC_LLM and Model Handling

The system utilizes a specialized logic for determining which LLM to use for the multi-agent workflow. While standard `gpt-researcher` uses `SMART_LLM` and `FAST_LLM`, the multi-agent framework prioritizes the `STRATEGIC_LLM` environment variable for the `ChiefEditorAgent`'s coordination tasks.

**Implementation Details:**
- **Override Logic:** In `open_task()`, if `STRATEGIC_LLM` contains a colon (e.g., `openai:gpt-4o`), the system extracts the model name after the colon [multi_agents/main.py:30-34]().
- **Direct Usage:** If no colon is present, it uses the variable value directly [multi_agents/main.py:35-36]().
- **Default:** If `STRATEGIC_LLM` is not set, the system falls back to the `model` specified in `task.json` [multi_agents/main.py:24]().

Sources: [multi_agents/main.py:29-37]()

---

## Configuration Flow and State Management

The `task` dictionary flows through the system via the `ResearchState` TypedDict. This ensures that every specialized agent has access to the user's requirements (like guidelines or max sections).

**Diagram: State Propagation to Agents**
```mermaid
graph TD
    subgraph States ["State Containers"]
        RS["ResearchState<br/>(multi_agents/memory/research.py)"]
    end

    subgraph Agents ["Specialized Agents"]
        Editor["EditorAgent<br/>(multi_agents/agents/orchestrator.py)"]
        Researcher["ResearchAgent<br/>(multi_agents/agents/orchestrator.py)"]
        Writer["WriterAgent<br/>(multi_agents/agents/orchestrator.py)"]
        Publisher["PublisherAgent<br/>(multi_agents/agents/orchestrator.py)"]
        Human["HumanAgent<br/>(multi_agents/agents/human.py)"]
    end

    RS -->|"provides task config to"| Editor
    RS -->|"provides task config to"| Writer
    RS -->|"provides task config to"| Researcher
    RS -->|"provides task config to"| Publisher
    RS -->|"provides task config to"| Human
```
Sources: [multi_agents/memory/research.py:5-22](), [multi_agents/agents/orchestrator.py:47-54]()

### Agent-Specific Parameter Consumption

1.  **HumanAgent:** Uses `include_human_feedback` to decide whether to prompt the user for feedback via WebSocket or console [multi_agents/agents/human.py:18-45](). It also tracks `plan_revision_count` [multi_agents/agents/human.py:50-53]().
2.  **ChiefEditorAgent (Routing):** Uses `max_plan_revisions` in `_route_human_feedback` to determine if the workflow should continue revising the plan or raise a `MaxPlanRevisionsExceededError` [multi_agents/agents/orchestrator.py:87-90](), [multi_agents/agents/plan_review.py:8-23]().
3.  **PublisherAgent:** Consumes the `output_dir` (generated from the query) and manages the final report generation based on the research results [multi_agents/agents/orchestrator.py:52]().
4.  **Formatters:** The system uses utility functions like `write_md_to_pdf` and `write_md_to_word` which resolve local resources like `pdf_styles.css` to ensure the configuration (like APA format) is reflected in the visual output [multi_agents/agents/utils/file_formats.py:40-104]().

Sources: [multi_agents/agents/human.py:10-59](), [multi_agents/agents/orchestrator.py:87-90](), [multi_agents/agents/plan_review.py:8-23](), [multi_agents/agents/utils/file_formats.py:40-104]()

---

## Programmatic Usage

While `task.json` is the default, the system can be configured programmatically by passing a dictionary to the `ChiefEditorAgent`.

```python
from multi_agents.agents import ChiefEditorAgent
from gpt_researcher.utils.enum import Tone

task = {
    "query": "Is AI in a hype cycle?",
    "model": "gpt-4o",
    "max_sections": 3,
    "max_plan_revisions": 3,
    "publish_formats": {
        "markdown": True,
        "pdf": True,
        "docx": True
    },
    "include_human_feedback": False,
    "source": "web"
}

chief_editor = ChiefEditorAgent(task, tone=Tone.Objective)
report = await chief_editor.run_research_task()
```

Sources: [multi_agents/main.py:40-50](), [multi_agents/agents/orchestrator.py:26-33](), [multi_agents/agent.py:3-17]()

---

# Page: Multi-Agent State Management

# Multi-Agent State Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [multi_agents/README.md](multi_agents/README.md)
- [multi_agents/__init__.py](multi_agents/__init__.py)
- [multi_agents/agent.py](multi_agents/agent.py)
- [multi_agents/agents/human.py](multi_agents/agents/human.py)
- [multi_agents/agents/orchestrator.py](multi_agents/agents/orchestrator.py)
- [multi_agents/agents/plan_review.py](multi_agents/agents/plan_review.py)
- [multi_agents/agents/utils/__init__.py](multi_agents/agents/utils/__init__.py)
- [multi_agents/agents/utils/pdf_styles.css](multi_agents/agents/utils/pdf_styles.css)
- [multi_agents/memory/__init__.py](multi_agents/memory/__init__.py)
- [multi_agents/memory/research.py](multi_agents/memory/research.py)
- [multi_agents/task.json](multi_agents/task.json)
- [tests/test_multi_agents_plan_revisions.py](tests/test_multi_agents_plan_revisions.py)

</details>



This document explains the state management architecture in the LangGraph-based multi-agent research system. It covers the two primary state objects (`ResearchState` and `DraftState`), their fields, lifecycle, and how they flow through the multi-agent workflow. For information about the overall multi-agent orchestration, see [ChiefEditorAgent Orchestration](#10.1). For details on the review-revision workflow mechanics, see [Review-Revision Workflow](#10.3).

## Purpose and Scope

State management in the multi-agent system is implemented using `TypedDict` classes that define the structure of data passed between agents. The system uses two distinct state objects:

- **`ResearchState`**: Global state that tracks the entire research process from initial query through final publication.
- **`DraftState`**: Per-section state that manages the review-revision loop for individual report sections.

These state objects enable LangGraph to coordinate asynchronous agent workflows, maintain data consistency, and support stateful graph execution with conditional edges.

## State Object Architecture

The multi-agent system defines two `TypedDict` classes that serve as strongly-typed state containers for the LangGraph state machine.

### ResearchState TypedDict

The `ResearchState` object maintains global research state across all workflow stages (planning, initial research, parallel research, writing, publication).

**Definition**: [multi_agents/memory/research.py:5-20]()

| Field | Type | Purpose | Populated By | Used By |
|-------|------|---------|--------------|---------|
| `task` | `dict` | Configuration from `task.json` (query, model, max_sections, etc.) | Initial input | All agents |
| `initial_research` | `str` | Broad research summary on main query | `ResearchAgent.run_initial_research` | `EditorAgent.plan_research` |
| `sections` | `List[str]` | Section headers for report outline | `EditorAgent.plan_research` | `EditorAgent.run_parallel_research` |
| `research_data` | `List[dict]` | Deep research results for each section | `EditorAgent.run_parallel_research` | `WriterAgent.write_sections` |
| `human_feedback` | `str` | Optional feedback on research plan | `HumanAgent.review_plan` | `EditorAgent.plan_research` |
| `plan_revision_count` | `int` | Counter for human-requested plan iterations | `HumanAgent.review_plan` | `ChiefEditorAgent._route_human_feedback` |
| `title` | `str` | Report title | `EditorAgent.plan_research` | `WriterAgent`, `PublisherAgent` |
| `headers` | `dict` | Localized header labels (title, introduction, etc.) | `WriterAgent.get_headers` | `PublisherAgent.generate_layout` |
| `date` | `str` | Report date | `EditorAgent.plan_research` | `PublisherAgent.generate_layout` |
| `table_of_contents` | `str` | Markdown ToC | `WriterAgent.write_sections` | `PublisherAgent.generate_layout` |
| `introduction` | `str` | Report introduction with citations | `WriterAgent.write_sections` | `PublisherAgent.generate_layout` |
| `conclusion` | `str` | Report conclusion with citations | `WriterAgent.write_sections` | `PublisherAgent.generate_layout` |
| `sources` | `List[str]` | All sources in APA format | `WriterAgent.write_sections` | `PublisherAgent.generate_layout` |
| `report` | `str` | Final compiled report in markdown | `PublisherAgent.generate_layout` | Output |

**Sources**: [multi_agents/memory/research.py:5-20](), [multi_agents/agents/human.py:50-59]()

### DraftState TypedDict

The `DraftState` object manages per-section state within the review-revision loop. Each section processed in parallel has its own `DraftState` instance.

**Definition**: [multi_agents/memory/draft.py:5-10]()

| Field | Type | Purpose | Populated By | Used By |
|-------|------|---------|--------------|---------|
| `task` | `dict` | Configuration from `ResearchState.task` | `EditorAgent._create_task_input` | All section agents |
| `topic` | `str` | Section header to research | `EditorAgent._create_task_input` | `ResearchAgent.run_depth_research` |
| `draft` | `dict` | Section draft (key=topic, value=content) | `ResearchAgent.run_depth_research` | `ReviewerAgent`, `ReviserAgent` |
| `review` | `str` or `None` | Reviewer feedback or `None` if accepted | `ReviewerAgent.review_draft` | `ReviserAgent.revise_draft`, conditional edge |
| `revision_notes` | `str` | Revisor's message about changes made | `ReviserAgent.revise_draft` | `ReviewerAgent.review_draft` |

**Sources**: [multi_agents/memory/draft.py:5-10]()

## ResearchState Lifecycle

The following diagram shows how `ResearchState` flows through the multi-agent workflow and which agents read/write specific fields.

```mermaid
graph TB
    Input["Initial Input:<br/>task.json → task field"]
    
    subgraph Stage1["Stage 1: Planning"]
        Browser["ResearchAgent.run_initial_research<br/>READS: task.query<br/>WRITES: initial_research"]
        Editor1["EditorAgent.plan_research<br/>READS: initial_research, human_feedback<br/>WRITES: title, date, sections"]
        Human["HumanAgent.review_plan<br/>WRITES: human_feedback, plan_revision_count"]
    end
    
    subgraph Stage2["Stage 2: Parallel Research"]
        Editor2["EditorAgent.run_parallel_research<br/>READS: sections, title<br/>Creates DraftState for each section<br/>WRITES: research_data"]
    end
    
    subgraph Stage3["Stage 3: Writing"]
        Writer["WriterAgent.write_sections<br/>READS: title, research_data, task<br/>WRITES: introduction, conclusion,<br/>table_of_contents, sources"]
        HeaderWriter["WriterAgent.get_headers<br/>WRITES: headers dict"]
    end
    
    subgraph Stage4["Stage 4: Publication"]
        Publisher["PublisherAgent.run<br/>READS: all fields<br/>WRITES: report"]
    end
    
    Output["Output:<br/>PDF, DOCX, Markdown"]
    
    Input --> Browser
    Browser --> Editor1
    Editor1 --> Human
    Human --> Routing{"ChiefEditorAgent._route_human_feedback"}
    Routing -- "revise" --> Editor1
    Routing -- "accept" --> Editor2
    Editor2 --> Writer
    Writer --> HeaderWriter
    HeaderWriter --> Publisher
    Publisher --> Output
```

**State Mutation Pattern**: Each agent returns a dictionary containing only the fields it wants to update. LangGraph automatically merges these updates into the existing `ResearchState` object.

**Sources**: [multi_agents/memory/research.py:5-20](), [multi_agents/agents/orchestrator.py:59-65](), [multi_agents/agents/human.py:50-59](), [multi_agents/agents/plan_review.py:8-23]()

## DraftState Lifecycle

The `DraftState` object manages the review-revision loop for a single section. This state graph runs in parallel for all sections defined in `ResearchState.sections`.

```mermaid
stateDiagram-v2
    [*] --> Researcher
    
    Researcher: ResearchAgent.run_depth_research<br/>INPUT: task, topic<br/>OUTPUT: draft (dict)
    
    Reviewer: ReviewerAgent.run<br/>INPUT: draft, task.guidelines, revision_notes<br/>OUTPUT: review (str or None)
    
    Reviser: ReviserAgent.run<br/>INPUT: draft, review<br/>OUTPUT: draft (revised), revision_notes
    
    Researcher --> Reviewer: draft populated
    
    Reviewer --> Accept: review = None
    Reviewer --> Reviser: review contains feedback
    
    Reviser --> Reviewer: draft updated,<br/>revision_notes populated
    
    Accept --> [*]: Returns to EditorAgent
    
    note right of Reviewer
        Conditional edge checks:
        if review is None → END
        else → "reviser"
    end note
```

**LangGraph StateGraph Configuration**: [multi_agents/agents/editor.py:126-144]()

```python
workflow = StateGraph(DraftState)
workflow.add_node("researcher", agents["research"].run_depth_research)
workflow.add_node("reviewer", agents["reviewer"].run)
workflow.add_node("reviser", agents["reviser"].run)

workflow.set_entry_point("researcher")
workflow.add_edge("researcher", "reviewer")
workflow.add_edge("reviser", "reviewer")
workflow.add_conditional_edges(
    "reviewer",
    lambda draft: "accept" if draft["review"] is None else "revise",
    {"accept": END, "revise": "reviser"},
)
```

**Sources**: [multi_agents/memory/draft.py:5-10](), [multi_agents/agents/editor.py:126-144]()

## State Flow Diagram: Natural Language to Code Entities

This diagram maps high-level workflow concepts to specific state fields and agent methods.

```mermaid
graph LR
    subgraph "User Input"
        TaskJSON["task.json<br/>{query, model, max_sections,<br/>guidelines, publish_formats}"]
    end
    
    subgraph "ResearchState Fields"
        RS_task["ResearchState.task"]
        RS_initial["ResearchState.initial_research"]
        RS_sections["ResearchState.sections"]
        RS_research["ResearchState.research_data"]
        RS_title["ResearchState.title"]
        RS_rev_count["ResearchState.plan_revision_count"]
        RS_intro["ResearchState.introduction"]
        RS_conclusion["ResearchState.conclusion"]
        RS_toc["ResearchState.table_of_contents"]
        RS_sources["ResearchState.sources"]
        RS_report["ResearchState.report"]
    end
    
    subgraph "DraftState Fields (per section)"
        DS_task["DraftState.task"]
        DS_topic["DraftState.topic"]
        DS_draft["DraftState.draft"]
        DS_review["DraftState.review"]
        DS_revision["DraftState.revision_notes"]
    end
    
    subgraph "Agent Methods"
        M1["ResearchAgent.run_initial_research()"]
        M2["EditorAgent.plan_research()"]
        M2H["HumanAgent.review_plan()"]
        M3["EditorAgent.run_parallel_research()"]
        M4["ResearchAgent.run_depth_research()"]
        M5["ReviewerAgent.run()"]
        M6["ReviserAgent.run()"]
        M7["WriterAgent.run()"]
        M8["PublisherAgent.run()"]
    end
    
    TaskJSON --> RS_task
    RS_task --> M1
    M1 --> RS_initial
    RS_initial --> M2
    M2 --> RS_sections
    M2 --> RS_title
    
    RS_sections --> M2H
    M2H --> RS_rev_count
    
    RS_sections --> M3
    M3 --> DS_task
    M3 --> DS_topic
    
    DS_topic --> M4
    M4 --> DS_draft
    DS_draft --> M5
    M5 --> DS_review
    DS_review --> M6
    M6 --> DS_draft
    M6 --> DS_revision
    
    DS_draft --> RS_research
    
    RS_research --> M7
    M7 --> RS_intro
    M7 --> RS_conclusion
    M7 --> RS_toc
    M7 --> RS_sources
    
    RS_intro --> M8
    RS_conclusion --> M8
    RS_toc --> M8
    RS_sources --> M8
    M8 --> RS_report
```

**Sources**: [multi_agents/memory/research.py:5-20](), [multi_agents/memory/draft.py:5-10](), [multi_agents/agents/orchestrator.py:59-65](), [multi_agents/agents/human.py:50-59](), [multi_agents/agents/plan_review.py:8-23]()

## State Update Mechanisms

Each agent in the multi-agent system returns a dictionary that LangGraph merges into the current state object.

### Partial State Updates

Agents return only the fields they modify. LangGraph handles the merge:

**Example from ResearchAgent**: [multi_agents/agents/researcher.py:43-44]()
```python
return {"task": task, "initial_research": await self.research(query=query, verbose=task.get("verbose"),
                                                              source=source, tone=self.tone, headers=self.headers)}
```

**Example from HumanAgent**: [multi_agents/agents/human.py:56-59]()
```python
return {
    "human_feedback": user_feedback,
    "plan_revision_count": plan_revision_count,
}
```

### State Accumulation Pattern

The `research_data` field uses a list accumulation pattern. Each section's draft is gathered from parallel runs:

**Parallel Execution**: [multi_agents/agents/editor.py:68-77]()
```python
final_drafts = [
    chain.ainvoke(self._create_task_input(
        research_state, query, title), config={"tags": ["gpt-researcher"]})
    for query in queries
]
research_results = [
    result["draft"] for result in await asyncio.gather(*final_drafts)
]

return {"research_data": research_results}
```

### Conditional State Updates and Routing

The `ChiefEditorAgent` uses the `plan_revision_count` to decide whether to continue the planning loop or error out if the human requests too many changes.

**Routing Logic**: [multi_agents/agents/plan_review.py:8-23]()
```python
def route_human_feedback(review, max_plan_revisions=DEFAULT_MAX_PLAN_REVISIONS):
    if review.get("human_feedback") is None:
        return "accept"

    plan_revision_count = review.get("plan_revision_count", 0)
    if plan_revision_count > max_plan_revisions:
        raise MaxPlanRevisionsExceededError(...)

    return "revise"
```

**Sources**: [multi_agents/agents/researcher.py:43-44](), [multi_agents/agents/human.py:56-59](), [multi_agents/agents/plan_review.py:8-23]()

## State Initialization and Task Configuration

The initial state is created from `task.json` and configuration passed to `ChiefEditorAgent`.

### Task Dictionary Structure

The `task` field contains configuration loaded from `task.json`:

**Task Schema**: [multi_agents/task.json:1-19]()
```json
{
  "query": "Is AI in a hype cycle?",
  "max_sections": 3,
  "max_plan_revisions": 3,
  "publish_formats": {
    "markdown": true,
    "pdf": true,
    "docx": true
  },
  "include_human_feedback": false,
  "model": "gpt-4o"
}
```

**Sources**: [multi_agents/task.json:1-19](), [multi_agents/agents/orchestrator.py:26-33]()

## State Persistence and Output

State exists only in memory during workflow execution. The `PublisherAgent` extracts all fields from `ResearchState` to generate the final report and save it to the filesystem.

### Output Generation from State

**Output Directory**: [multi_agents/agents/orchestrator.py:39-45]()
```python
def _create_output_directory(self):
    output_dir = "./outputs/" + \
        sanitize_filename(
            f"run_{self.task_id}_{self.task.get('query')[0:40]}")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir
```

**Sources**: [multi_agents/agents/orchestrator.py:39-45](), [multi_agents/agents/publisher.py:22-53]()

---

# Page: AG2 Multi-Agent Alternative

# AG2 Multi-Agent Alternative

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/faq.md](docs/docs/faq.md)
- [docs/docs/gpt-researcher/getting-started/how-to-choose.md](docs/docs/gpt-researcher/getting-started/how-to-choose.md)
- [docs/docs/gpt-researcher/multi_agents/ag2.md](docs/docs/gpt-researcher/multi_agents/ag2.md)
- [docs/docs/welcome.md](docs/docs/welcome.md)
- [docs/src/components/HomepageFeatures.js](docs/src/components/HomepageFeatures.js)
- [docs/static/img/ag2-pipeline.webp](docs/static/img/ag2-pipeline.webp)
- [multi_agents_ag2/README.md](multi_agents_ag2/README.md)
- [multi_agents_ag2/__init__.py](multi_agents_ag2/__init__.py)
- [multi_agents_ag2/agents/__init__.py](multi_agents_ag2/agents/__init__.py)
- [multi_agents_ag2/agents/editor.py](multi_agents_ag2/agents/editor.py)
- [multi_agents_ag2/agents/orchestrator.py](multi_agents_ag2/agents/orchestrator.py)
- [multi_agents_ag2/main.py](multi_agents_ag2/main.py)
- [multi_agents_ag2/requirements.txt](multi_agents_ag2/requirements.txt)

</details>



The AG2 (formerly AutoGen2) framework serves as a high-performance alternative to the default LangGraph orchestration for multi-agent research workflows [docs/docs/gpt-researcher/multi_agents/ag2.md:1-4](). While it mirrors the logical flow of the standard multi-agent system, it leverages the AG2 conversational agent paradigm to handle state transitions and agent collaboration [multi_agents_ag2/agents/orchestrator.py:20-21]().

## Overview and Purpose

The AG2 implementation is designed for users who prefer the AutoGen ecosystem or require specific conversational patterns not easily modeled in directed acyclic graphs. It maintains functional parity with the LangGraph version, utilizing the same set of specialized agents to conduct planning, data collection, review, and publication [docs/docs/gpt-researcher/multi_agents/ag2.md:17-26]().

### Key Differences from LangGraph
*   **Orchestration**: Uses AG2's `GroupChat` and `GroupChatManager` instead of a LangGraph `StateGraph` [multi_agents_ag2/agents/orchestrator.py:104-111]().
*   **Agent Communication**: Employs a message-passing interface where agents send messages to a manager [multi_agents_ag2/agents/orchestrator.py:113-117]().
*   **State Management**: While LangGraph uses `TypedDict` states, the AG2 `ChiefEditorAgent` manages state via a local dictionary and iterative loops within its `run_research_task` and `_run_section` methods [multi_agents_ag2/agents/orchestrator.py:143-163]().

**Sources:** [docs/docs/gpt-researcher/multi_agents/ag2.md:1-15](), [multi_agents_ag2/agents/orchestrator.py:55-111]()

---

## Agent Roles and Implementation

The AG2 framework utilizes eight distinct agent roles. These roles are implemented using AG2's `ConversableAgent` for the conversational layer and specialized logic classes for the research execution.

| Agent Name | AG2 Entity Type | Responsibility |
| :--- | :--- | :--- |
| **Chief Editor** | `ConversableAgent` | Orchestrates the multi-agent research workflow [multi_agents_ag2/agents/orchestrator.py:59-63](). |
| **Editor** | `ConversableAgent` | Plans the research outline from initial findings [multi_agents_ag2/agents/orchestrator.py:64-68](). |
| **Researcher** | `ConversableAgent` | Performs initial and deep research tasks via `GPTResearcher` [multi_agents_ag2/agents/orchestrator.py:69-73](). |
| **Reviewer** | `ConversableAgent` | Reviews drafts against given guidelines [multi_agents_ag2/agents/orchestrator.py:74-78](). |
| **Reviser** | `ConversableAgent` | Revises drafts based on reviewer feedback [multi_agents_ag2/agents/orchestrator.py:79-83](). |
| **Writer** | `ConversableAgent` | Compiles the final report from research drafts [multi_agents_ag2/agents/orchestrator.py:84-88](). |
| **Publisher** | `ConversableAgent` | Publishes the final report in requested formats [multi_agents_ag2/agents/orchestrator.py:89-93](). |
| **Human** | `UserProxyAgent` | Provides optional feedback on the research plan [multi_agents_ag2/agents/orchestrator.py:94-101](). |

**Sources:** [multi_agents_ag2/agents/orchestrator.py:58-102](), [docs/docs/gpt-researcher/multi_agents/ag2.md:17-26]()

---

## Technical Architecture and Data Flow

The AG2 alternative follows a structured five-stage pipeline: Planning, Data Collection/Analysis, Review/Revision, Writing, and Publication [docs/docs/gpt-researcher/multi_agents/ag2.md:32-38]().

### Workflow Visualization: Code Entity Space
This diagram maps the high-level research stages to the specific Python classes and methods that execute them within the `multi_agents_ag2` directory.

```mermaid
graph TD
    subgraph "Planning Stage"
        A["ChiefEditorAgent.run_research_task()"] --> B["EditorAgent.plan_research()"]
    end

    subgraph "Data Collection"
        B --> C["ChiefEditorAgent._run_parallel_research()"]
        C --> D["ResearchAgent.run_depth_research()"]
    end

    subgraph "Review & Revision Loop"
        D --> E["ReviewerAgent.run()"]
        E -- "If Feedback" --> F["ReviserAgent.run()"]
        F --> E
        E -- "If Accepted" --> G["WriterAgent.run()"]
    end

    subgraph "Finalization"
        G --> H["PublisherAgent.run()"]
    end
```
**Sources:** [multi_agents_ag2/agents/orchestrator.py:137-163](), [multi_agents_ag2/agents/orchestrator.py:171-181](), [multi_agents_ag2/agents/editor.py:17-41]()

---

## Implementation Details

### Conversational Orchestration
The `ChiefEditorAgent` initializes a `GroupChat` containing all agents [multi_agents_ag2/agents/orchestrator.py:104-109](). While the orchestration logic (loops and sequencing) is handled by the `run_research_task` method, it uses the `_log` and `_chat` methods to synchronize the AG2 conversation history with the internal state of the research [multi_agents_ag2/agents/orchestrator.py:113-125]().

### Parallel Research Execution
Parallelism is achieved through `asyncio.gather` within the `_run_parallel_research` method [multi_agents_ag2/agents/orchestrator.py:165-169](). This spawns multiple instances of the `_run_section` coroutine, each managing its own internal Review-Revision loop for a specific subtopic [multi_agents_ag2/agents/orchestrator.py:137-163]().

### Research to Code Mapping
The following diagram bridges the "Natural Language" requirements (Guidelines, Queries) to the "Code Entities" that process them in the AG2 context.

```mermaid
graph LR
    subgraph "Natural Language Space"
        Q["'Research Query'"]
        G["'Report Guidelines'"]
    end

    subgraph "Code Entity Space"
        T["multi_agents_ag2/task.json"]
        CO["ChiefEditorAgent._llm_config()"]
        EA["EditorAgent._create_planning_prompt()"]
        MA["main.py:run_research_task()"]
    end

    Q --> T
    G --> T
    T --> MA
    MA --> CO
    T --> EA
```
**Sources:** [multi_agents_ag2/task.json:1-10](), [multi_agents_ag2/main.py:37-47](), [multi_agents_ag2/agents/orchestrator.py:43-53](), [multi_agents_ag2/agents/editor.py:43-63]()

---

## Configuration and Execution

### Task Configuration
The system relies on a `task.json` file in the `multi_agents_ag2` directory. Key parameters include:
*   **`model`**: The OpenAI LLM to use (defaulting to `gpt-4o`) [multi_agents_ag2/agents/orchestrator.py:44-48]().
*   **`max_revisions`**: Maximum iterations for the reviewer/reviser loop [docs/docs/gpt-researcher/multi_agents/ag2.md:62-62]().
*   **`include_human_feedback`**: Toggles the `Human` agent's `human_input_mode` between `ALWAYS` and `NEVER` [multi_agents_ag2/agents/orchestrator.py:97-99]().

### Running the Application
The entry point is `multi_agents_ag2/main.py`. It loads environment variables, parses the task configuration, and invokes the `ChiefEditorAgent` [multi_agents_ag2/main.py:1-60]().

**Sources:** [multi_agents_ag2/main.py:1-60](), [docs/docs/gpt-researcher/multi_agents/ag2.md:39-53]()

---

# Page: Deployment and Operations

# Deployment and Operations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [Dockerfile](Dockerfile)
- [docker-compose.yml](docker-compose.yml)
- [main.py](main.py)
- [requirements.txt](requirements.txt)

</details>



This document covers the deployment infrastructure, configuration management, and operational procedures for GPT Researcher. It details the Docker-based deployment architecture, server configuration, environment management, and testing infrastructure. For information about the FastAPI backend API itself, see [FastAPI Backend and WebSocket API](#8.1). For configuration parameters and their values, see [Configuration System](#5).

---

## Docker Deployment Architecture

GPT Researcher uses Docker Compose to orchestrate multiple services with shared volumes and network connectivity. The deployment consists of four primary services defined in `docker-compose.yml`.

### Service Overview

```mermaid
graph TB
    subgraph "Docker Compose Services"
        Backend["gpt-researcher Service<br/>Port: 8000<br/>Image: gptresearcher/gpt-researcher"]
        Frontend["gptr-nextjs Service<br/>Port: 3000<br/>Image: gptresearcher/gptr-nextjs"]
        Tests["gpt-researcher-tests<br/>Profile: test<br/>pytest runner"]
        Discord["discord-bot<br/>Port: 3001<br/>Profile: discord"]
    end
    
    subgraph "Shared Volumes"
        MyDocs["./my-docs<br/>Local documents"]
        Outputs["./outputs<br/>Generated reports & images"]
        Logs["./logs<br/>Application logs"]
        NodeModules["node_modules<br/>Frontend dependencies"]
        NextCache[".next cache<br/>Next.js build"]
    end
    
    subgraph "Environment Configuration"
        EnvFile[".env file<br/>API keys & settings"]
    end
    
    Backend --> MyDocs
    Backend --> Outputs
    Backend --> Logs
    Frontend --> NodeModules
    Frontend --> NextCache
    Frontend --> Outputs
    Discord --> NodeModules
    
    EnvFile -.->|"Configures"| Backend
    EnvFile -.->|"Configures"| Frontend
    EnvFile -.->|"Configures"| Discord
    
    Frontend -->|"HTTP/WebSocket"| Backend
```

**Sources:** [docker-compose.yml:1-78]()

### Backend Service Configuration

The `gpt-researcher` service runs the Python FastAPI backend with Uvicorn:

| Configuration | Value | Description |
|--------------|-------|-------------|
| Port | `8000` | FastAPI server endpoint |
| Image | `gptresearcher/gpt-researcher` | Built from root Dockerfile |
| User | `root` | Required for dynamic pip installs via `_check_pkg` |
| Restart Policy | `always` | Auto-restart on failure |
| Build Policy | `build` | Always build from source |

**Key Environment Variables:**

```yaml
OPENAI_API_KEY: ${OPENAI_API_KEY}
OPENAI_BASE_URL: ${OPENAI_BASE_URL}
TAVILY_API_KEY: ${TAVILY_API_KEY}
LANGCHAIN_API_KEY: ${LANGCHAIN_API_KEY}
LOGGING_LEVEL: INFO
```

**Volume Mappings:**

| Host Path | Container Path | Purpose |
|-----------|---------------|---------|
| `./my-docs` | `/usr/src/app/my-docs` | Local document storage for `report_source=local` |
| `./outputs` | `/usr/src/app/outputs` | Generated reports and images |
| `./logs` | `/usr/src/app/logs` | Application log files |

**Sources:** [docker-compose.yml:2-24]()

### Frontend Service Configuration

The `gptr-nextjs` service provides the production Next.js interface:

| Configuration | Value | Description |
|--------------|-------|-------------|
| Port | `3000` | Next.js development server |
| Image | `gptresearcher/gptr-nextjs` | Built from `frontend/nextjs/Dockerfile.dev` |
| Restart Policy | `always` | Auto-restart on failure |

**Development Mode Settings:**

- `CHOKIDAR_USEPOLLING: "true"` - Enables file watching in Docker [docker-compose.yml:31]()
- `stdin_open: true` - Interactive mode for debugging [docker-compose.yml:29]()
- Node modules volume prevents host/container conflicts [docker-compose.yml:39]()

**Sources:** [docker-compose.yml:26-45]()

### Test Service Configuration

The `gpt-researcher-tests` service runs pytest with profile activation:

```bash
docker-compose --profile test up
```

Executes:
1. Install test dependencies: `pytest`, `pytest-asyncio`, `faiss-cpu` [docker-compose.yml:59]()
2. Run report type tests: `tests/report-types.py` [docker-compose.yml:60]()
3. Run vector store tests: `tests/vector-store.py` [docker-compose.yml:61]()

**Sources:** [docker-compose.yml:47-62]()

---

## Multi-Stage Docker Build Process

The `Dockerfile` implements a three-stage build strategy optimizing image size and build cache utilization.

```mermaid
graph LR
    subgraph "Stage 1: install-browser"
        BrowserInstall["Install System Packages<br/>- Chromium + chromedriver<br/>- Firefox ESR + geckodriver<br/>- build-essential"]
    end
    
    subgraph "Stage 2: gpt-researcher-install"
        PipInstall["Install Python Dependencies<br/>requirements.txt<br/>multi_agents/requirements.txt"]
    end
    
    subgraph "Stage 3: gpt-researcher"
        UserSetup["Security Hardening<br/>- Create non-root user<br/>- Set ownership<br/>- Create outputs directory"]
        CopyApp["Copy Application Code<br/>with proper ownership"]
        UvicornCmd["CMD: uvicorn main:app"]
    end
    
    BrowserInstall --> PipInstall
    PipInstall --> UserSetup
    UserSetup --> CopyApp
    CopyApp --> UvicornCmd
```

**Sources:** [Dockerfile:1-65]()

### Stage 1: Browser Installation

Base image: `python:3.12-slim-bookworm` [Dockerfile:3]()

Installs web scraping dependencies:

| Component | Version | Purpose |
|-----------|---------|---------|
| Chromium | Latest stable | Primary web scraping browser |
| Chromedriver | Matching version | Selenium WebDriver |
| Firefox ESR | Latest ESR | Alternative browser |
| Geckodriver | v0.36.0 | Firefox WebDriver |
| build-essential | - | Compilation tools for Python packages |

**Architecture-aware Installation:**
The Dockerfile detects system architecture and installs appropriate Geckodriver for `amd64` or `arm64`. [Dockerfile:15-20]()

**Sources:** [Dockerfile:1-21]()

### Stage 2: Python Dependencies

Installs packages from two requirement files:

```dockerfile
COPY ./requirements.txt ./requirements.txt
COPY ./multi_agents/requirements.txt ./multi_agents/requirements.txt

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt --upgrade --prefer-binary && \
    pip install --no-cache-dir -r multi_agents/requirements.txt --upgrade --prefer-binary
```

**Sources:** [Dockerfile:23-35]()

---

## Server Configuration and Entry Points

The primary entry point for the backend is `main.py`, which initializes logging and starts the FastAPI application via Uvicorn.

### Logging Configuration
Logging is configured to output to both a file (`logs/app.log`) and the console. [main.py:10-19]()
- Suppresses verbose logs from `fontTools` to keep output clean. [main.py:21-24]()
- Creates the `logs/` directory automatically if missing. [main.py:5-7]()

### Server Startup
The application is served using Uvicorn on port `8000` by default. [main.py:37]()

**Sources:** [main.py:1-38]()

---

## Environment Management

GPT Researcher implements a three-tier configuration system: environment variables override JSON configuration, which overrides hardcoded defaults.

### Environment Variable Categories

#### LLM and Search Configuration
- `OPENAI_API_KEY`: Primary LLM key. [docker-compose.yml:7]()
- `TAVILY_API_KEY`: Primary search engine key. [docker-compose.yml:9]()
- `LANGCHAIN_API_KEY`: For LangSmith observability. [docker-compose.yml:10]()

#### Image Generation Configuration
Controlled via specific variables to enable inline report visuals. [docker-compose.yml:12-16]()

| Variable | Default | Description |
|----------|---------|-------------|
| `IMAGE_GENERATION_ENABLED` | `false` | Enable/disable feature |
| `IMAGE_GENERATION_MODEL` | `gemini-2.0-flash-preview-image-generation` | Model for images |
| `IMAGE_GENERATION_MAX_IMAGES` | `3` | Max images per report |

**Sources:** [docker-compose.yml:6-16]()

---

## Dependency Management

GPT Researcher manages a wide array of dependencies for AI orchestration, document processing, and web scraping.

### Core Dependencies
- **Framework**: `fastapi`, `uvicorn`, `pydantic`. [requirements.txt:5-7]()
- **AI/LLM**: `langchain`, `langgraph`, `openai`, `litellm`, `ollama`. [requirements.txt:11-23]()
- **Scraping**: `beautifulsoup4`, `tavily-python`, `ddgs` (DuckDuckGo), `arxiv`. [requirements.txt:27-32]()
- **Documents**: `pymupdf` (PDF), `python-docx` (Word), `python-pptx` (PowerPoint), `unstructured`. [requirements.txt:33-36]()
- **Utilities**: `loguru`, `aiofiles`, `httpx`, `websockets`. [requirements.txt:45-51]()

**Sources:** [requirements.txt:1-68]()

---

## Summary of Operations

| Component | Role | Detail Link |
|-----------|------|-------------|
| **Docker** | Orchestration & Deployment | [Docker Deployment](#11.1) |
| **Server** | FastAPI/Uvicorn Backend | [Server Configuration and Entry Points](#11.2) |
| **Env** | Variable Management | [Environment Management](#11.3) |
| **Testing** | Pytest & Validation | [Testing and Validation](#11.4) |
| **Observability** | Logging & LangSmith | [Observability and Logging](#11.5) |
| **Cloud** | Infrastructure Deployment | [Cloud and Infrastructure Deployment](#11.6) |

**Sources:** [docker-compose.yml:1-78](), [Dockerfile:1-65](), [main.py:1-38](), [requirements.txt:1-68]()

---

# Page: Docker Deployment

# Docker Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [Dockerfile](Dockerfile)
- [Dockerfile.fullstack](Dockerfile.fullstack)
- [docker-compose.yml](docker-compose.yml)
- [frontend/nextjs/.dockerignore](frontend/nextjs/.dockerignore)
- [frontend/nextjs/.eslintrc.json](frontend/nextjs/.eslintrc.json)
- [frontend/nextjs/.example.env](frontend/nextjs/.example.env)
- [frontend/nextjs/.gitignore](frontend/nextjs/.gitignore)
- [frontend/nextjs/.prettierrc](frontend/nextjs/.prettierrc)
- [frontend/nextjs/Dockerfile](frontend/nextjs/Dockerfile)
- [frontend/nextjs/Dockerfile.dev](frontend/nextjs/Dockerfile.dev)
- [frontend/nextjs/actions/apiActions.ts](frontend/nextjs/actions/apiActions.ts)
- [frontend/nextjs/hooks/useAnalytics.ts](frontend/nextjs/hooks/useAnalytics.ts)
- [requirements.txt](requirements.txt)

</details>



This document covers deploying GPT Researcher using Docker and Docker Compose. It explains the multi-stage Dockerfile build process, service orchestration, volume management, and production deployment considerations. For information about server configuration and entry points without Docker, see [Server Configuration and Entry Points](#11.2). For environment variable management, see [Environment Management](#11.3).

## Overview

GPT Researcher provides a complete Docker deployment configuration with two primary services: the FastAPI backend (`gpt-researcher`) and the Next.js frontend (`gptr-nextjs`). The system uses multi-stage Docker builds to optimize image size and includes optional services for testing and Discord bot integration.

Sources: [docker-compose.yml:1-78]()

## Docker Architecture

The following diagram shows the service architecture defined in `docker-compose.yml`:

```mermaid
graph TB
    subgraph "Docker Compose Services"
        Backend["gpt-researcher<br/>Image: gptresearcher/gpt-researcher<br/>Port: 8000"]
        Frontend["gptr-nextjs<br/>Image: gptresearcher/gptr-nextjs<br/>Port: 3000"]
        Tests["gpt-researcher-tests<br/>Profile: test<br/>pytest runner"]
        Discord["discord-bot<br/>Profile: discord<br/>Port: 3001"]
    end
    
    subgraph "Volume Mounts"
        MyDocs["my-docs/<br/>Input documents"]
        Outputs["outputs/<br/>Generated reports"]
        Logs["logs/<br/>Application logs"]
        NextOutput["frontend/nextjs/.next<br/>Next.js build cache"]
    end
    
    subgraph "Environment Configuration"
        EnvFile[".env file<br/>API keys & config"]
    end
    
    subgraph "External Access"
        Browser["Web Browser"]
    end
    
    EnvFile --> Backend
    EnvFile --> Frontend
    
    Backend --> MyDocs
    Backend --> Outputs
    Backend --> Logs
    
    Frontend --> NextOutput
    Frontend --> Outputs
    
    Browser -->|"localhost:8000"| Backend
    Browser -->|"localhost:3000"| Frontend
    
    Frontend -.->|"API calls"| Backend
```

**Service Roles:**

| Service | Purpose | Default State |
|---------|---------|---------------|
| `gpt-researcher` | FastAPI backend server running on port 8000 | Always running |
| `gptr-nextjs` | Next.js frontend application on port 3000 | Always running |
| `gpt-researcher-tests` | pytest test runner for integration tests | Profile: `test` (manual) |
| `discord-bot` | Discord bot integration server on port 3001 | Profile: `discord` (manual) |

Sources: [docker-compose.yml:1-78]()

## Multi-Stage Dockerfile Build

The backend uses a three-stage build process optimized for layer caching and image size:

```mermaid
flowchart LR
    subgraph Stage1["Stage 1: install-browser<br/>FROM python:3.12-slim-bookworm"]
        Browsers["Install Chromium + Chromedriver<br/>Install Firefox + Geckodriver<br/>Install build-essential"]
    end
    
    subgraph Stage2["Stage 2: gpt-researcher-install<br/>FROM install-browser"]
        Deps["COPY requirements.txt<br/>COPY multi_agents/requirements.txt<br/>pip install dependencies"]
    end
    
    subgraph Stage3["Stage 3: gpt-researcher<br/>FROM gpt-researcher-install"]
        User["Create gpt-researcher user<br/>Set permissions"]
        App["COPY application code<br/>CMD uvicorn main:app"]
    end
    
    Stage1 --> Stage2
    Stage2 --> Stage3
```

**Stage Details:**

### Stage 1: Browser Installation (`install-browser`)
Installs browser engines required for JavaScript-enabled web scraping:
- Chromium with Chromedriver (architecture-aware) [Dockerfile:12-13]()
- Firefox ESR with Geckodriver (supports amd64 and arm64) [Dockerfile:14-20]()
- Build tools for native dependencies [Dockerfile:14-14]()

The stage uses architecture detection to install the correct Geckodriver version and cleans up apt lists to reduce image size [Dockerfile:8-21]().

Sources: [Dockerfile:1-21]()

### Stage 2: Dependency Installation (`gpt-researcher-install`)
Installs all Python dependencies in a single layer to optimize caching:
- Core dependencies from `requirements.txt` [Dockerfile:30-30]()
- Multi-agent dependencies from `multi_agents/requirements.txt` [Dockerfile:31-31]()
- Uses `--no-cache-dir` and `--prefer-binary` for smaller image size [Dockerfile:34-35]()

Sources: [Dockerfile:23-35]()

### Stage 3: Application Setup (`gpt-researcher`)
Creates the final runtime image:
- Creates non-root `gpt-researcher` user for security [Dockerfile:53-53]()
- Sets up work directory at `/usr/src/app` [Dockerfile:60-60]()
- Creates `outputs` directory with proper permissions (777 for write access) [Dockerfile:56-58]()
- Copies application code with correct ownership [Dockerfile:63-63]()
- Configures Uvicorn server via build arguments [Dockerfile:64-64]()

**Build Arguments:**

| Argument | Default | Purpose |
|----------|---------|---------|
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8000` | Server listen port |
| `WORKERS` | `1` | Number of Uvicorn workers |

Sources: [Dockerfile:37-64]()

## Service Configuration

### Backend Service (`gpt-researcher`)

The backend service configuration in `docker-compose.yml`:

```yaml
gpt-researcher:
  pull_policy: build
  image: gptresearcher/gpt-researcher
  build: ./
  environment: 
    OPENAI_API_KEY: ${OPENAI_API_KEY}
    TAVILY_API_KEY: ${TAVILY_API_KEY}
    # ... additional env vars
  volumes:
    - ${PWD}/my-docs:/usr/src/app/my-docs:rw
    - ${PWD}/outputs:/usr/src/app/outputs:rw
    - ${PWD}/logs:/usr/src/app/logs:rw
  user: root
  restart: always
  ports:
    - 8000:8000
```

**Key Configuration Elements:**

- **Pull Policy:** `build` forces local build instead of pulling from registry [docker-compose.yml:3-3]()
- **User:** Runs as `root` to enable dynamic package installation [docker-compose.yml:21-21]()
- **Restart Policy:** `always` ensures service recovery after crashes [docker-compose.yml:22-22]()
- **Port Mapping:** Exposes port 8000 to host [docker-compose.yml:24-24]()

**Environment Variables:**

| Variable | Required | Purpose |
|----------|----------|---------|
| `OPENAI_API_KEY` | Yes | LLM provider authentication |
| `OPENAI_BASE_URL` | No | Custom OpenAI-compatible API endpoint |
| `TAVILY_API_KEY` | Yes | Web search API authentication |
| `LANGCHAIN_API_KEY` | No | LangSmith tracing (optional) |
| `GOOGLE_API_KEY` | No | Image generation with Gemini |
| `IMAGE_GENERATION_ENABLED` | No | Enable inline images (default: false) |
| `IMAGE_GENERATION_MODEL` | No | Gemini model |
| `IMAGE_GENERATION_MAX_IMAGES` | No | Max images per report |
| `LOGGING_LEVEL` | No | Log verbosity (default: INFO) |

Sources: [docker-compose.yml:2-24](), [Dockerfile:51-59]()

### Frontend Service (`gptr-nextjs`)

The Next.js frontend service configuration:

```yaml
gptr-nextjs:
  pull_policy: build
  image: gptresearcher/gptr-nextjs
  build:
    dockerfile: Dockerfile.dev
    context: frontend/nextjs
  environment:
    CHOKIDAR_USEPOLLING: "true"
    NEXT_PUBLIC_GA_MEASUREMENT_ID: ${NEXT_PUBLIC_GA_MEASUREMENT_ID}
    NEXT_PUBLIC_GPTR_API_URL: ${NEXT_PUBLIC_GPTR_API_URL}
  volumes:
    - /app/node_modules
    - ./frontend/nextjs:/app
    - ./frontend/nextjs/.next:/app/.next
    - ./outputs:/app/outputs
  ports:
    - 3000:3000
```

**Configuration Details:**

- **Development Mode:** Uses `Dockerfile.dev` for hot-reload support [docker-compose.yml:36-36]()
- **File Watching:** `CHOKIDAR_USEPOLLING=true` enables polling for file changes in Docker [docker-compose.yml:31-31]()
- **Build Cache:** Mounts `.next` directory to persist build artifacts [docker-compose.yml:41-41]()
- **Output Access:** Mounts `outputs` directory to serve generated reports [docker-compose.yml:42-42]()
- **Node Modules:** Anonymous volume prevents host overwriting container dependencies [docker-compose.yml:39-39]()

Sources: [docker-compose.yml:26-45]()

## Volume Management Strategy

The following diagram shows the volume mount architecture:

```mermaid
graph TB
    subgraph "Host System"
        HostDocs["${PWD}/my-docs<br/>User documents"]
        HostOutputs["${PWD}/outputs<br/>Generated reports"]
        HostLogs["${PWD}/logs<br/>Application logs"]
        HostNext["${PWD}/frontend/nextjs<br/>Next.js source"]
    end
    
    subgraph "Backend Container<br/>/usr/src/app"
        BackendDocs["/usr/src/app/my-docs<br/>Read: local documents"]
        BackendOutputs["/usr/src/app/outputs<br/>Write: PDFs, DOCX, MD"]
        BackendLogs["/usr/src/app/logs<br/>Write: JSON logs"]
    end
    
    subgraph "Frontend Container<br/>/app"
        FrontendCode["/app<br/>Next.js source (hot-reload)"]
        FrontendNext["/app/.next<br/>Build cache"]
        FrontendOutputs["/app/outputs<br/>Static file serving"]
        FrontendModules["/app/node_modules<br/>Anonymous volume"]
    end
    
    HostDocs -.->|"rw mount"| BackendDocs
    HostOutputs -.->|"rw mount"| BackendOutputs
    HostOutputs -.->|"rw mount"| FrontendOutputs
    HostLogs -.->|"rw mount"| BackendLogs
    HostNext -.->|"bind mount"| FrontendCode
    HostNext -.->|"nested mount"| FrontendNext
```

**Volume Purposes:**

| Mount | Service | Purpose | Access |
|-------|---------|---------|--------|
| `my-docs` | Backend | Local document research source | Read/Write |
| `outputs` | Both | Report generation and serving | Read/Write |
| `logs` | Backend | JSON logging and debugging | Read/Write |
| `frontend/nextjs` | Frontend | Hot-reload development | Read/Write |
| `.next` | Frontend | Build cache persistence | Read/Write |
| `node_modules` | Frontend | Isolate container dependencies | Anonymous |

**Permission Considerations:**

The backend `outputs` directory is created with 777 permissions to ensure write access from the `gpt-researcher` user [Dockerfile:56-58]().

Sources: [docker-compose.yml:17-20,38-42](), [Dockerfile:55-58]()

## Fullstack Docker Image

For single-container deployments, `Dockerfile.fullstack` provides a combined image using `nginx` and `supervisor`.

```mermaid
flowchart TD
    subgraph BuildStages["Build Stages"]
        FB[frontend-builder Stage]
        IB[install-browser Stage]
        BB[backend-builder Stage]
    end

    subgraph FinalImage["Final Stage (final)"]
        S[Supervisord]
        N[Nginx Port 3000]
        F[FastAPI Port 8000]
        NX[Next.js Port 3001]
    end

    FB --> FinalImage
    BB --> FinalImage
    IB --> BB
    S --> N
    S --> F
    S --> NX
    N -->|"Proxy /outputs"| F
    N -->|"Proxy /reports"| F
    N -->|"Default"| NX
```

**Implementation Details:**
- **Frontend Build:** Uses `node:slim` to run `npm run build` [Dockerfile.fullstack:4-13]().
- **Nginx Configuration:** Proxies `/outputs` and `/reports` to the FastAPI backend while serving the Next.js application on the same port [Dockerfile.fullstack:133-147]().
- **Process Management:** Uses `supervisor` to manage the lifecycle of both the Python backend and Node.js frontend [Dockerfile.fullstack:73-77]().

Sources: [Dockerfile.fullstack:1-147]()

## Test and Optional Services

### Test Service (`gpt-researcher-tests`)

The test service runs pytest integration tests using a profile flag [docker-compose.yml:56-56]():

```yaml
gpt-researcher-tests:
  image: gptresearcher/gpt-researcher-tests
  build: ./
  environment: 
    OPENAI_API_KEY: ${OPENAI_API_KEY}
    TAVILY_API_KEY: ${TAVILY_API_KEY}
  profiles: ["test"]
  command: >
    /bin/sh -c "
    pip install pytest pytest-asyncio faiss-cpu &&
    python -m pytest tests/report-types.py &&
    python -m pytest tests/vector-store.py
    "
```

The service installs test dependencies dynamically and runs two test suites:
- `tests/report-types.py` - Tests different report generation modes [docker-compose.yml:60-60]()
- `tests/vector-store.py` - Tests vector store integration [docker-compose.yml:61-61]()

Sources: [docker-compose.yml:47-62]()

## Service Communication

```mermaid
sequenceDiagram
    participant Browser
    participant Frontend as gptr-nextjs<br/>:3000
    participant Backend as gpt-researcher<br/>:8000
    participant Volumes as Mounted Volumes
    
    Browser->>Frontend: HTTP GET localhost:3000
    Frontend->>Frontend: Serve Next.js app
    Frontend-->>Browser: HTML/JS/CSS
    
    Browser->>Frontend: Research request via WebSocket
    Frontend->>Backend: ws://localhost:8000/ws
    Backend->>Backend: GPTResearcher.conduct_research()
    Backend->>Volumes: Read from my-docs/
    Backend->>Backend: Generate report
    Backend->>Volumes: Write to outputs/
    Backend-->>Frontend: Stream progress events
    Frontend-->>Browser: Display results
    
    Browser->>Frontend: Download report
    Frontend->>Volumes: Read from /app/outputs
    Frontend-->>Browser: Serve PDF/DOCX
```

**Network Configuration:**

- Both services share the default Docker bridge network.
- Frontend references backend using the API URL provided in `NEXT_PUBLIC_GPTR_API_URL` [docker-compose.yml:34-34]().
- External access uses published ports 8000 [docker-compose.yml:24-24]() and 3000 [docker-compose.yml:45-45]().

Sources: [docker-compose.yml:1-78]()

## Production Deployment

For production use, consider these modifications:

**1. Use Pre-built Images**
Remove `build: ./` and change `pull_policy: build` to `pull_policy: always` to use Docker Hub images [docker-compose.yml:3-4]().

**2. Increase Workers**
Build with more Uvicorn workers for production load by setting the `WORKERS` env var [Dockerfile:48-49]().

**3. Production Frontend**
The production frontend build is handled in `frontend/nextjs/Dockerfile` which uses a multi-stage build:
- **Stage 1 (deps):** Installs `node_modules` [frontend/nextjs/Dockerfile:4-11]().
- **Stage 2 (builder):** Runs `npm run build` [frontend/nextjs/Dockerfile:16-22]().
- **Stage 3 (runner):** Copies only necessary artifacts (`.next`, `public`, `node_modules`) for a slim runtime image [frontend/nextjs/Dockerfile:27-42]().

Sources: [Dockerfile:40-49](), [frontend/nextjs/Dockerfile:1-43]()

## Summary Table

| Aspect | Configuration | Location |
|--------|--------------|----------|
| **Backend Image** | `gptresearcher/gpt-researcher` | [docker-compose.yml:4]() |
| **Backend Port** | `8000:8000` | [docker-compose.yml:23-24]() |
| **Backend Build** | Multi-stage (3 stages) | [Dockerfile:1-64]() |
| **Frontend Image** | `gptresearcher/gptr-nextjs` | [docker-compose.yml:28]() |
| **Frontend Port** | `3000:3000` | [docker-compose.yml:44-45]() |
| **Document Input** | `${PWD}/my-docs` → `/usr/src/app/my-docs` | [docker-compose.yml:18]() |
| **Report Output** | `${PWD}/outputs` → `/usr/src/app/outputs` | [docker-compose.yml:19]() |
| **Log Output** | `${PWD}/logs` → `/usr/src/app/logs` | [docker-compose.yml:20]() |
| **Test Profile** | `docker compose --profile test up` | [docker-compose.yml:56]() |
| **Required Env** | `OPENAI_API_KEY`, `TAVILY_API_KEY` | [docker-compose.yml:7-9]() |

Sources: [docker-compose.yml:1-78](), [Dockerfile:1-64](), [Dockerfile.fullstack:1-147]()

---

# Page: Server Configuration and Entry Points

# Server Configuration and Entry Points

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/chat/chat.py](backend/chat/chat.py)
- [backend/run_server.py](backend/run_server.py)
- [backend/server/agent_discovery.py](backend/server/agent_discovery.py)
- [backend/server/app.py](backend/server/app.py)
- [backend/server/report_store.py](backend/server/report_store.py)
- [main.py](main.py)
- [tests/test_agent_discovery.py](tests/test_agent_discovery.py)

</details>



## Purpose and Scope

This document describes the server initialization and configuration system for GPT Researcher's backend service. It covers the `main.py` entry point, Uvicorn server startup, logging infrastructure, and the structure of the FastAPI application defined in `backend/server/app.py`. This page focuses on the technical implementation of the server lifecycle and its configuration environment.

## Entry Point Architecture

The GPT Researcher backend starts through `main.py`, which serves as the primary entry point for the Uvicorn ASGI server. This file handles initialization order, logging setup, environment loading, and server launch. An alternative startup script is provided in `backend/run_server.py` for direct backend execution.

### Server Initialization Flow

```mermaid
flowchart TD
    Start["main.py execution"]
    CreateLogs["Create logs/ directory<br/>Path('logs').mkdir()"]
    ConfigLogging["Configure logging<br/>FileHandler + StreamHandler<br/>Suppress fontTools"]
    LoadEnv["Load environment variables<br/>load_dotenv()"]
    ImportApp["Import FastAPI app<br/>from backend.server.app import app"]
    CheckMain{"if __name__ == '__main__'"}
    StartUvicorn["uvicorn.run(app, host='0.0.0.0', port=8000)"]
    
    Start --> CreateLogs
    CreateLogs --> ConfigLogging
    ConfigLogging --> LoadEnv
    LoadEnv --> ImportApp
    ImportApp --> CheckMain
    CheckMain -->|"Direct execution"| StartUvicorn
    
    StartUvicorn --> Running["Server running on port 8000"]
```

**Sources:** [main.py:1-38](), [backend/run_server.py:1-27]()

## Main Entry Point (`main.py`)

The entry point follows a specific initialization sequence to ensure proper setup before the FastAPI application loads.

### Directory and Logging Setup

The first operation creates the logs directory to prevent file handler errors [main.py:5-7](). The logging system uses Python's built-in `logging` module with dual output handlers:

- **FileHandler**: Persists logs to `logs/app.log` [main.py:15]().
- **StreamHandler**: Outputs logs to the standard console [main.py:17]().

**Suppressed Loggers:**
The server explicitly suppresses verbose logging from `fontTools` libraries, which generate excessive output during PDF generation [main.py:21-24](). It also silences Uvicorn reload logs to keep the console clean [backend/server/app.py:48]().

**Sources:** [main.py:5-27](), [backend/server/app.py:41-49]()

### Environment Loading and App Import

After logging is configured, the entry point loads environment variables via `load_dotenv()` [main.py:29](). Only after the environment is ready does it import the FastAPI `app` instance from `backend.server.app` [main.py:31]().

## Backend Application Structure (`backend/server/app.py`)

The core of the server is the FastAPI application instance. It manages the lifecycle of the service, mounts static files, and configures middleware.

### Lifespan and Resource Management

The application uses an `asynccontextmanager` called `lifespan` to handle startup and shutdown events [backend/server/app.py:71-95]().

| Event | Actions Taken |
|-------|---------------|
| **Startup** | Creates `outputs/` directory; mounts `/outputs` for generated reports; mounts `/site` and `/static` for the frontend files [backend/server/app.py:73-89](). |
| **Shutdown** | Logs the shutdown sequence [backend/server/app.py:94](). |

### CORS and Security

The server configures Cross-Origin Resource Sharing (CORS) using `CORSMiddleware` [backend/server/app.py:114-120](). Allowed origins are pulled from the `CORS_ALLOW_ORIGINS` environment variable, defaulting to local development URLs and `https://app.gptr.dev` [backend/server/app.py:100-109]().

### Data Models and State

The server defines Pydantic models for incoming requests:
- `ResearchRequest`: Parameters for starting a new research task (task, tone, source, repo_name, etc.) [backend/server/app.py:53-61]().
- `ChatRequest`: Parameters for the research chat interface, allowing extra fields via `ConfigDict(extra="allow")` [backend/server/app.py:64-69]().

It also initializes the `WebSocketManager` for real-time communication and a `ReportStore` for local JSON-based persistence of research results [backend/server/app.py:133-135]().

**Sources:** [backend/server/app.py:53-135](), [backend/server/report_store.py:7-10]()

## Server Launch Modes

### Direct Uvicorn Execution

When `main.py` is executed as the main module, it starts Uvicorn on all interfaces (`0.0.0.0`) at port `8000` [main.py:33-37]().

### Backend Script Execution

The script `backend/run_server.py` provides an alternative entry point that specifically enables Uvicorn's `reload=True` mode for development [backend/run_server.py:21-27](). It also ensures the backend directory is added to the Python path to resolve imports correctly [backend/run_server.py:12-14]().

## Relationship Between Code Entities

The following diagram bridges the "Natural Language Space" of server concepts to the specific "Code Entity Space" found in the repository.

```mermaid
graph TD
    subgraph "Entry Point Space"
        main["main.py"]
        run_script["backend/run_server.py"]
    end

    subgraph "FastAPI App Entity Space"
        app_inst["app (FastAPI instance)"]
        lifespan_fn["lifespan (asynccontextmanager)"]
        ws_mgr["WebSocketManager"]
        rep_store["ReportStore"]
        disc_fn["build_agent_discovery_document"]
    end

    subgraph "Configuration Space"
        dotenv["load_dotenv()"]
        cors_env["CORS_ALLOW_ORIGINS"]
        report_path["REPORT_STORE_PATH"]
        disc_contact["AGENT_DISCOVERY_CONTACT"]
    end

    main -->|"imports"| app_inst
    run_script -->|"runs"| app_inst
    app_inst -->|"uses"| lifespan_fn
    app_inst -->|"manages"| ws_mgr
    app_inst -->|"persists via"| rep_store
    app_inst -->|"exposes"| disc_fn
    main -->|"initializes"| dotenv
    app_inst -->|"reads"| cors_env
    rep_store -->|"reads"| report_path
    app_inst -->|"reads"| disc_contact
```

**Sources:** [main.py:29-37](), [backend/server/app.py:71-172](), [backend/run_server.py:12-27](), [backend/server/agent_discovery.py:12-16]()

## Request Processing and Logic Flow

When a request enters the server, it is routed based on the path. The diagram below illustrates how the server entities interact to handle a research or chat request.

```mermaid
sequenceDiagram
    participant Client as "Client (Web/WS)"
    participant App as "backend/server/app.py"
    participant WS as "WebSocketManager"
    participant Chat as "ChatAgentWithMemory"
    participant Store as "ReportStore"

    Client->>App: POST /api/reports
    App->>Store: upsert_report(research_id, report)
    Store-->>App: Success
    App-->>Client: {"success": True}

    Client->>App: WebSocket /ws
    App->>WS: start_connection()
    Note over WS: WebSocketManager handles lifecycle

    Client->>App: POST /api/chat (ChatRequest)
    App->>Chat: __init__(report, config)
    Chat->>Chat: process_chat_completion()
    Chat-->>App: response
    App-->>Client: JSONResponse
```

**Sources:** [backend/server/app.py:133-210](), [backend/chat/chat.py:55-184](), [backend/server/report_store.py:44-49]()

## Agent Discovery Protocol

The server implements the Agent Discovery Protocol to advertise its capabilities [backend/server/app.py:162-172](). This is handled by the `build_agent_discovery_document` function, which maps internal endpoints like `/report/`, `/api/reports`, and `/ws` to a standardized JSON format [backend/server/agent_discovery.py:12-68]().

**Sources:** [backend/server/app.py:162-172](), [backend/server/agent_discovery.py:1-68]()

## Server-Side Logging Structure

The server maintains a consistent logging format across different components. While `main.py` sets the global configuration, individual modules like `backend/chat/chat.py` instantiate their own loggers to provide granular context [backend/chat/chat.py:19]().

**Sources:** [main.py:9-19](), [backend/chat/chat.py:21-27](), [backend/server/app.py:42-48]()

---

# Page: Environment Management

# Environment Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.cursorrules](.cursorrules)
- [.env.example](.env.example)
- [.gitignore](.gitignore)
- [CURSOR_RULES.md](CURSOR_RULES.md)
- [gpt_researcher/actions/retriever.py](gpt_researcher/actions/retriever.py)
- [gpt_researcher/config/config.py](gpt_researcher/config/config.py)
- [gpt_researcher/llm_provider/__init__.py](gpt_researcher/llm_provider/__init__.py)
- [gpt_researcher/retrievers/__init__.py](gpt_researcher/retrievers/__init__.py)
- [gpt_researcher/retrievers/openalex/__init__.py](gpt_researcher/retrievers/openalex/__init__.py)
- [gpt_researcher/retrievers/openalex/openalex.py](gpt_researcher/retrievers/openalex/openalex.py)
- [gpt_researcher/retrievers/utils.py](gpt_researcher/retrievers/utils.py)
- [gpt_researcher/retrievers/xquik/__init__.py](gpt_researcher/retrievers/xquik/__init__.py)
- [gpt_researcher/retrievers/xquik/xquik.py](gpt_researcher/retrievers/xquik/xquik.py)
- [gpt_researcher/utils/llm.py](gpt_researcher/utils/llm.py)

</details>



This document covers best practices for managing environment variables, API keys, and configuration settings in GPT Researcher. It details the environment loading mechanism, configuration priority hierarchy, and common troubleshooting approaches.

For information about the configuration system architecture and available parameters, see [Configuration System](#5). For Docker-specific environment configuration, see [Docker Deployment](#11.1). For server startup and initialization, see [Server Configuration and Entry Points](#11.2).

## Environment Loading Mechanism

GPT Researcher loads environment variables through a multi-stage process that combines `.env` files, system environment variables, and default configurations.

### Loading Sequence

```mermaid
graph TB
    Start["Application Start"] --> LoadDotenv["load_dotenv()"]
    LoadDotenv --> InitConfig["Config.__init__()<br/>[gpt_researcher/config/config.py:34-61]"]
    
    InitConfig --> LoadConfig["Config.load_config()<br/>[gpt_researcher/config/config.py:157-178]"]
    
    LoadConfig --> CheckPath{config_path<br/>provided?}
    CheckPath -->|No| UseDefault["Return DEFAULT_CONFIG<br/>[gpt_researcher/config/config.py:161]"]
    CheckPath -->|Yes| CheckExists{Path<br/>exists?}
    
    CheckExists -->|No| WarnDefault["Print warning<br/>Use DEFAULT_CONFIG<br/>[gpt_researcher/config/config.py:165-170]"]
    CheckExists -->|Yes| LoadJSON["json.load(config_path)<br/>[gpt_researcher/config/config.py:172-173]"]
    
    LoadJSON --> Merge["Merge with DEFAULT_CONFIG<br/>[gpt_researcher/config/config.py:176-177]"]
    
    UseDefault --> SetAttrs
    WarnDefault --> SetAttrs
    Merge --> SetAttrs["_set_attributes()<br/>[gpt_researcher/config/config.py:62-84]"]
    
    SetAttrs --> ForEach["For each config key:<br/>[gpt_researcher/config/config.py:71]"]
    ForEach --> CheckEnv{os.getenv(key)<br/>exists?<br/>[gpt_researcher/config/config.py:72-73]}
    
    CheckEnv -->|Yes| Convert["convert_env_value()<br/>Type conversion<br/>[gpt_researcher/config/config.py:258-289]"]
    CheckEnv -->|No| UseConfig["Use config value"]
    
    Convert --> SetAttr["setattr(self, key.lower(), value)<br/>[gpt_researcher/config/config.py:75]"]
    UseConfig --> SetAttr
    
    SetAttr --> SetEmbed["_set_embedding_attributes()<br/>[gpt_researcher/config/config.py:85-89]"]
    SetEmbed --> SetLLM["_set_llm_attributes()<br/>[gpt_researcher/config/config.py:91-96]"]
    SetLLM --> HandleDeprecated["_handle_deprecated_attributes()<br/>[gpt_researcher/config/config.py:98-146]"]
    HandleDeprecated --> SetDocPath["_set_doc_path()<br/>[gpt_researcher/config/config.py:147-155]"]
    
    SetDocPath --> Ready["Config Ready"]
```

**Diagram: Environment Variable Loading Sequence**

The loading sequence prioritizes environment variables over configuration files, which in turn override defaults. The `convert_env_value` method handles type conversion based on `BaseConfig.__annotations__` type hints [gpt_researcher/config/config.py:74]().

**Sources:** [gpt_researcher/config/config.py:34-178](), [gpt_researcher/config/config.py:258-289]()

### Type Conversion System

GPT Researcher automatically converts environment variable strings to appropriate Python types based on the `BaseConfig` type annotations:

| Type | Conversion Logic | Example |
|------|------------------|---------|
| `bool` | `"true"`, `"1"`, `"yes"`, `"on"` → `True` | `VERBOSE=true` |
| `int` | `int(env_value)` | `MAX_ITERATIONS=5` |
| `float` | `float(env_value)` | `TEMPERATURE=0.7` |
| `str` | Direct assignment | `FAST_LLM=openai:gpt-4o-mini` |
| `list` | `json.loads(env_value)` | `RETRIEVERS=["tavily","google"]` |
| `dict` | `json.loads(env_value)` | `MCP_SERVERS=[{"name":"github"}]` |
| `Union[T, None]` | Checks for `"none"`, `"null"`, `""` | `STRATEGIC_LLM=none` |

**Sources:** [gpt_researcher/config/config.py:258-289]()

## Configuration Priority Hierarchy

GPT Researcher resolves configuration values using a three-tier priority system:

```mermaid
graph LR
    Query["Configuration Query<br/>e.g., FAST_LLM"] --> Check1{Environment<br/>Variable Set?}
    
    Check1 -->|Yes| Env["Use os.getenv(key)<br/>Priority: 1 (Highest)<br/>[gpt_researcher/config/config.py:72-74]"]
    Check1 -->|No| Check2{Custom Config<br/>File Provided?}
    
    Check2 -->|Yes| Custom["Use config_path value<br/>Priority: 2<br/>[gpt_researcher/config/config.py:172-177]"]
    Check2 -->|No| Default["Use DEFAULT_CONFIG<br/>Priority: 3 (Lowest)<br/>[gpt_researcher/config/config.py:161]"]
    
    Env --> Result["Final Value"]
    Custom --> Result
    Default --> Result
```

**Diagram: Configuration Priority Hierarchy**

This hierarchy allows for flexible deployment strategies:
- **Development:** Override specific values via environment variables without modifying files.
- **Staging/Production:** Use custom config files with environment-specific API endpoints.
- **Testing:** Rely on defaults with minimal configuration.

**Sources:** [gpt_researcher/config/config.py:62-178]()

## Core Environment Variables Reference

### LLM Provider Configuration

GPT Researcher uses a three-tier LLM strategy. Each tier is configured using the `provider:model` format:

| Variable | Format | Default | Purpose |
|----------|--------|---------|---------|
| `FAST_LLM` | `provider:model` | `openai:gpt-4o-mini` | Quick operations (summaries, metadata) |
| `SMART_LLM` | `provider:model` | `openai:gpt-4o` | Complex analysis, report writing |
| `STRATEGIC_LLM` | `provider:model` | `openai:o3-mini` | Reasoning tasks, planning |
| `REASONING_EFFORT` | `low`\|`medium`\|`high` | `medium` | Effort for reasoning models (o3, o4) |

**Provider-Specific Base URLs:**

| Variable | Purpose | Example |
|----------|---------|---------|
| `OPENAI_BASE_URL` | Custom OpenAI-compatible endpoint | `http://localhost:11434/v1` (Ollama) |
| `OLLAMA_BASE_URL` | Ollama server endpoint | `http://localhost:11434` |

**Sources:** [gpt_researcher/config/config.py:91-96](), [gpt_researcher/utils/llm.py:99-103](), [.env.example:1-65]()

### Scraper and Performance Configuration

The environment allows fine-tuning of scraping behavior to respect rate limits and optimize latency:

| Variable | Type | Default | Purpose |
|----------|------|---------|---------|
| `MAX_SCRAPER_WORKERS` | `int` | `15` | Max concurrent browser instances [ .env.example:18]() |
| `SCRAPER_RATE_LIMIT_DELAY` | `float` | `0.0` | Seconds between requests [ .env.example:30]() |
| `COMPRESSION_THRESHOLD` | `int` | `8000` | Char limit to skip expensive compression [ .env.example:38]() |

**Sources:** [.env.example:8-38]()

### API Keys and Observability

GPT Researcher requires API keys for various services. Each provider has its own environment variable:

| Variable | Provider | Purpose |
|----------|----------|---------|
| `OPENAI_API_KEY` | OpenAI | Primary LLM/Embedding access [ .env.example:1]() |
| `TAVILY_API_KEY` | Tavily Search | Web search retrieval [ .env.example:2]() |
| `XQUIK_API_KEY` | Xquik | X/Twitter search retrieval [ .env.example:3]() |
| `LANGCHAIN_API_KEY` | LangSmith | Enhanced observability [ .env.example:45]() |
| `LANGCHAIN_TRACING_V2` | LangSmith | Enable/Disable tracing [ .env.example:43]() |

**Sources:** [.env.example:1-46]()

## .env File Management

The `.env` file should be placed in the repository root directory. It is explicitly ignored by version control to prevent secret leakage.

### Security and Git Integration

The project includes a robust `.gitignore` to protect sensitive environment files:

| Ignored Pattern | Description |
|-----------------|-------------|
| `.env` | Primary secrets file [ .gitignore:2]() |
| `.venv`, `env/` | Virtual environments [ .gitignore:3-9]() |
| `.envrc` | Direnv configuration [ .gitignore:4]() |
| `env.bak/` | Backup environment files [ .gitignore:13]() |

**Sources:** [ .gitignore:1-15]()

### .env.example Template

The repository provides a template for required and optional variables:

```bash
# [.env.example]
OPENAI_API_KEY=
TAVILY_API_KEY=
DOC_PATH=./my-docs

# Scraper Configuration
# MAX_SCRAPER_WORKERS=15
# SCRAPER_RATE_LIMIT_DELAY=0.0

# Performance Optimization
# COMPRESSION_THRESHOLD=8000

# LangChain Tracing (LangSmith)
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_API_KEY=
```

**Sources:** [.env.example:1-46]()

## Deprecated Configuration Handling

GPT Researcher maintains backward compatibility with deprecated configuration patterns while warning users to migrate:

```mermaid
graph TB
    CheckDeprecated["_handle_deprecated_attributes()<br/>[gpt_researcher/config/config.py:98]"]
    
    CheckDeprecated --> CheckEmbedProvider{EMBEDDING_PROVIDER<br/>env var set?<br/>[gpt_researcher/config/config.py:100]}
    
    CheckEmbedProvider -->|Yes| WarnEmbed["warnings.warn(FutureWarning)<br/>[gpt_researcher/config/config.py:101-105]"]
    WarnEmbed --> MapProvider{Provider type?<br/>[gpt_researcher/config/config.py:111-126]}
    
    MapProvider -->|ollama| UseOllama["Use OLLAMA_EMBEDDING_MODEL<br/>[gpt_researcher/config/config.py:112]"]
    MapProvider -->|custom| UseCustom["Use OPENAI_EMBEDDING_MODEL<br/>[gpt_researcher/config/config.py:113-114]"]
    MapProvider -->|openai| UseOAIEmbed["text-embedding-3-large<br/>[gpt_researcher/config/config.py:115-116]"]
    
    CheckEmbedProvider -->|No| CheckLLMProvider{LLM_PROVIDER<br/>env var set?<br/>[gpt_researcher/config/config.py:132]}
    
    CheckLLMProvider -->|Yes| WarnLLM["warnings.warn(FutureWarning)<br/>[gpt_researcher/config/config.py:133]"]
    WarnLLM --> SetProviders["Set fast_llm_provider<br/>Set smart_llm_provider<br/>[gpt_researcher/config/config.py:134-139]"]
    
    CheckLLMProvider -->|No| CheckFast{FAST_LLM_MODEL<br/>set?<br/>[gpt_researcher/config/config.py:140]}
    CheckFast -->|Yes| WarnFast["Set fast_llm_model<br/>[gpt_researcher/config/config.py:142]"]
    
    CheckFast -->|No| CheckSmart{SMART_LLM_MODEL<br/>set?<br/>[gpt_researcher/config/config.py:143]}
    CheckSmart -->|Yes| WarnSmart["Set smart_llm_model<br/>[gpt_researcher/config/config.py:145]"]
    
    CheckSmart -->|No| Done["Deprecation handling complete"]
```

**Diagram: Deprecated Configuration Handling Flow**

**Sources:** [gpt_researcher/config/config.py:98-146]()

## Troubleshooting Common Issues

### Issue: Scraper Rate Limiting
If you encounter 429 errors from search providers or scrapers, adjust the concurrency and delay:
- Decrease `MAX_SCRAPER_WORKERS` (e.g., set to 2 for Firecrawl Free) [ .env.example:14-18]().
- Increase `SCRAPER_RATE_LIMIT_DELAY` (e.g., set to 6.0 for 10 req/min limits) [ .env.example:24-30]().

### Issue: High Latency for Small Docs
If research is slow on local documents or small web pages, increase the `COMPRESSION_THRESHOLD`. This skips the embedding-based compression pipeline when content is already concise, potentially reducing latency by 40-50% [ .env.example:34-38]().

### Issue: Frontend API URL
If the Next.js frontend cannot connect to the FastAPI backend, verify `NEXT_PUBLIC_GPTR_API_URL`. It defaults to `http://localhost:8000` but may need to be overridden in certain network environments [ .env.example:6]().

**Sources:** [.env.example:1-46]()

---

# Page: Testing and Validation

# Testing and Validation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/docker-build.yml](.github/workflows/docker-build.yml)
- [docs/docs/gpt-researcher/context/tailored-research.md](docs/docs/gpt-researcher/context/tailored-research.md)
- [docs/docs/gpt-researcher/llms/testing-your-llm.md](docs/docs/gpt-researcher/llms/testing-your-llm.md)
- [docs/docs/gpt-researcher/multi_agents/langgraph.md](docs/docs/gpt-researcher/multi_agents/langgraph.md)
- [evals/README.md](evals/README.md)
- [evals/__init__.py](evals/__init__.py)
- [evals/hallucination_eval/evaluate.py](evals/hallucination_eval/evaluate.py)
- [evals/hallucination_eval/inputs/search_queries.jsonl](evals/hallucination_eval/inputs/search_queries.jsonl)
- [evals/hallucination_eval/requirements.txt](evals/hallucination_eval/requirements.txt)
- [evals/hallucination_eval/results/aggregate_results.json](evals/hallucination_eval/results/aggregate_results.json)
- [evals/hallucination_eval/results/evaluation_records.jsonl](evals/hallucination_eval/results/evaluation_records.jsonl)
- [evals/hallucination_eval/run_eval.py](evals/hallucination_eval/run_eval.py)
- [evals/simple_evals/.gitignore](evals/simple_evals/.gitignore)
- [evals/simple_evals/__init__.py](evals/simple_evals/__init__.py)
- [evals/simple_evals/logs/.gitkeep](evals/simple_evals/logs/.gitkeep)
- [evals/simple_evals/logs/README.md](evals/simple_evals/logs/README.md)
- [evals/simple_evals/logs/SimpleQA Eval 100 Problems 2-22-25.txt](evals/simple_evals/logs/SimpleQA Eval 100 Problems 2-22-25.txt)
- [evals/simple_evals/problems/Simple QA Test Set.csv](evals/simple_evals/problems/Simple QA Test Set.csv)
- [evals/simple_evals/requirements.txt](evals/simple_evals/requirements.txt)
- [evals/simple_evals/run_eval.py](evals/simple_evals/run_eval.py)
- [evals/simple_evals/simpleqa_eval.py](evals/simple_evals/simpleqa_eval.py)
- [tests/__init__.py](tests/__init__.py)
- [tests/gptr-logs-handler.py](tests/gptr-logs-handler.py)
- [tests/report-types.py](tests/report-types.py)
- [tests/research_test.py](tests/research_test.py)
- [tests/test-openai-llm.py](tests/test-openai-llm.py)
- [tests/test-your-llm.py](tests/test-your-llm.py)
- [tests/test_logging.py](tests/test_logging.py)
- [tests/test_logs.py](tests/test_logs.py)

</details>



This document covers the testing infrastructure, validation workflows, and evaluation frameworks for GPT Researcher. It details the pytest configuration, automated test suites, and specialized evaluation systems for measuring factuality (SimpleQA) and detecting hallucinations.

## Purpose and Scope

This page documents:
- **Test Infrastructure**: Pytest configuration and Docker-based test execution.
- **Integration Testing**: Validating research modes, source handling, and report generation.
- **Evaluation Frameworks**: Quantitative measurement of research quality using SimpleQA and hallucination detection.
- **CI/CD Integration**: Automated testing workflows via GitHub Actions.

## Test Infrastructure Overview

The testing environment is designed to handle asynchronous research workflows, requiring specific configuration for `pytest-asyncio` and environment variable injection for API providers.

Title: Testing and Validation Architecture
```mermaid
graph TB
    subgraph "Test_Configuration"
        PyprojectToml["pyproject.toml<br/>pytest.ini_options"]
        DockerCompose["docker-compose.yml<br/>gpt-researcher-tests"]
        Workflow["docker-build.yml<br/>GitHub Actions"]
    end
    
    subgraph "Execution_Engines"
        LocalPytest["Local pytest<br/>python -m pytest"]
        DockerTest["Docker Test Service<br/>profile: test"]
        GHActions["GPTR tests Workflow<br/>workflow_dispatch"]
    end
    
    subgraph "Validation_Suites"
        ResearchTest["tests/research_test.py<br/>Source URL validation"]
        ReportTypes["tests/report-types.py<br/>Mode validation"]
        HallucinationEval["evals/hallucination_eval/<br/>Fact-checking"]
        SimpleQA["evals/simple_evals/<br/>Accuracy metrics"]
    end
    
    PyprojectToml --> LocalPytest
    DockerCompose --> DockerTest
    Workflow --> GHActions
    
    LocalPytest --> ResearchTest
    LocalPytest --> ReportTypes
    DockerTest --> ResearchTest
    GHActions --> DockerTest
    
    ResearchTest --> Results["Validation Results"]
    ReportTypes --> Results
    HallucinationEval --> Metrics["Quality Metrics"]
    SimpleQA --> Metrics
```

**Sources:** [.github/workflows/docker-build.yml:1-45](), [tests/report-types.py:16-47](), [evals/README.md:1-176]()

## Pytest and Environment Configuration

### Pytest Settings
The framework uses `pytest-asyncio` in strict mode to manage the asynchronous nature of the `GPTResearcher` agent.

| Setting | Value | Purpose |
|---------|-------|---------|
| `asyncio_mode` | `"strict"` | Requires `@pytest.mark.asyncio` for async tests. |
| `testpaths` | `["tests"]` | Root directory for test discovery. |
| `python_files` | `"test_*.py"` | Naming convention for test modules. |

### GitHub Actions Workflow
The `GPTR tests` workflow automates testing in a containerized environment using secrets for API authentication.

- **Trigger**: Manual via `workflow_dispatch` [.github/workflows/docker-build.yml:7]().
- **Environment**: Uses the `tests` environment [.github/workflows/docker-build.yml:14]().
- **Secrets**: Injects `OPENAI_API_KEY`, `TAVILY_API_KEY`, and `LANGCHAIN_API_KEY` [.github/workflows/docker-build.yml:17-19]().
- **Execution**: Runs `docker-compose --profile test run --rm gpt-researcher-tests` [.github/workflows/docker-build.yml:45]().

**Sources:** [.github/workflows/docker-build.yml:1-45]()

## Research and Source Validation

The `tests/research_test.py` suite validates specific logic regarding how the agent handles user-provided URLs and web scouring.

### Source URL Logic
Tests verify the `source_urls` and `complement_source_urls` parameters in the `GPTResearcher` class.

1. **Restricted Research**: When `complement_source_urls=False`, the agent must only use provided URLs [tests/research_test.py:25-28]().
2. **Complemented Research**: When `complement_source_urls=True`, the agent gathers additional context from the web even if the provided sources are unrelated to the query [tests/research_test.py:74-77]().

### Report Type Validation
The `tests/report-types.py` script uses `pytest.mark.parametrize` to validate multiple research modes:
- `research_report`
- `subtopic_report`

It asserts that the generated report contains the query keywords and respects domain restrictions via `query_domains` [tests/report-types.py:17-43]().

**Sources:** [tests/research_test.py:1-111](), [tests/report-types.py:9-47](), [docs/docs/gpt-researcher/context/tailored-research.md:5-32]()

## SimpleQA Evaluation Framework

The `simple_evals` system measures short-form factuality based on OpenAI's methodology.

### Components and Metrics
- **Dataset**: `Simple QA Test Set.csv` containing factual questions and gold targets [evals/README.md:19]().
- **Grader**: Uses `gpt-4-turbo` (configurable) to grade responses on a three-point scale [evals/simple_evals/run_eval.py:80-84]().
- **Grades**:
    - `CORRECT`: Answer contains gold target info without contradictions [evals/simple_evals/simpleqa_eval.py:19-32]().
    - `INCORRECT`: Answer contradicts the gold target [evals/simple_evals/simpleqa_eval.py:34-48]().
    - `NOT_ATTEMPTED`: Answer neither confirms nor contradicts [evals/simple_evals/simpleqa_eval.py:50-62]().

### Implementation Flow
1. **Initialization**: `SimpleQAEval` loads random samples from the test set [evals/simple_evals/simpleqa_eval.py:101-117]().
2. **Execution**: `evaluate_single_query` runs `GPTResearcher.conduct_research()` and `write_report()` [evals/simple_evals/run_eval.py:30-44]().
3. **Grading**: The `GRADER_TEMPLATE` provides few-shot examples to the LLM judge to ensure consistent scoring [evals/simple_evals/simpleqa_eval.py:14-93]().

**Sources:** [evals/README.md:5-145](), [evals/simple_evals/simpleqa_eval.py:1-121](), [evals/simple_evals/run_eval.py:1-178]()

## Hallucination Evaluation

The `hallucination_eval` framework detects non-factual content by comparing generated reports against the retrieved source text.

### Evaluation Logic
The system utilizes the `judges` library to perform document summary evaluation.

Title: Hallucination Evaluation Sequence
```mermaid
sequenceDiagram
    participant RE as "ResearchEvaluator (evals/hallucination_eval/run_eval.py)"
    participant GR as "GPTResearcher (gpt_researcher/agent.py)"
    participant HE as "HallucinationEvaluator (evals/hallucination_eval/evaluate.py)"
    participant J as "Judges HaluEval (judges library)"

    RE->>GR: conduct_research(query)
    GR-->>RE: return context (source_text)
    RE->>GR: write_report()
    GR-->>RE: return report (model_output)
    RE->>HE: evaluate_response(model_output, source_text)
    HE->>J: judge(input=source_text, output=model_output)
    J-->>HE: return score & reasoning
    HE-->>RE: return eval_result
    RE->>RE: Save to evaluation_records.jsonl
```

### Key Classes and Methods
- `ResearchEvaluator.run_research(query)`: Orchestrates the `GPTResearcher` to produce a report and its associated context [evals/hallucination_eval/run_eval.py:68-95]().
- `HallucinationEvaluator.evaluate_response(model_output, source_text)`: Uses `HaluEvalDocumentSummaryNonFactual` to score the output [evals/hallucination_eval/evaluate.py:26-49]().
- `ResearchEvaluator.evaluate_research()`: Appends results to `evaluation_records.jsonl` and calculates aggregate hallucination rates [evals/hallucination_eval/run_eval.py:97-144]().

### Results Management
- **Detailed Records**: `evaluation_records.jsonl` stores per-query results, including reasoning for detected hallucinations [evals/hallucination_eval/results/evaluation_records.jsonl:1]().
- **Aggregates**: `aggregate_results.json` tracks total hallucination rates across a test run [evals/hallucination_eval/results/aggregate_results.json:1-7]().

**Sources:** [evals/hallucination_eval/run_eval.py:34-213](), [evals/hallucination_eval/evaluate.py:18-54](), [evals/hallucination_eval/results/aggregate_results.json:1-208]()

## Summary of Validation Commands

| Task | Command |
|------|---------|
| **Standard Tests** | `python -m pytest tests/report-types.py` |
| **Source Logic** | `python tests/research_test.py` |
| **SimpleQA Eval** | `python evals/simple_evals/run_eval.py --num_examples 5` |
| **Hallucination Eval** | `python evals/hallucination_eval/run_eval.py` |
| **Docker Tests** | `docker-compose --profile test run --rm gpt-researcher-tests` |

**Sources:** [evals/README.md:82, 172](), [.github/workflows/docker-build.yml:45](), [tests/report-types.py:47]()

---

# Page: Observability and Logging

# Observability and Logging

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/report_type/basic_report/basic_report.py](backend/report_type/basic_report/basic_report.py)
- [backend/report_type/detailed_report/detailed_report.py](backend/report_type/detailed_report/detailed_report.py)
- [backend/server/multi_agent_runner.py](backend/server/multi_agent_runner.py)
- [backend/server/server_utils.py](backend/server/server_utils.py)
- [backend/server/websocket_manager.py](backend/server/websocket_manager.py)
- [docs/docs/gpt-researcher/handling-logs/all-about-logs.md](docs/docs/gpt-researcher/handling-logs/all-about-logs.md)
- [docs/docs/gpt-researcher/handling-logs/langsmith-logs.md](docs/docs/gpt-researcher/handling-logs/langsmith-logs.md)
- [docs/docs/gpt-researcher/handling-logs/langsmith.png](docs/docs/gpt-researcher/handling-logs/langsmith.png)
- [docs/docs/gpt-researcher/handling-logs/simple-logs-example.md](docs/docs/gpt-researcher/handling-logs/simple-logs-example.md)
- [frontend/index.html](frontend/index.html)
- [frontend/scripts.js](frontend/scripts.js)
- [frontend/styles.css](frontend/styles.css)
- [tests/test_websocket_manager.py](tests/test_websocket_manager.py)

</details>



This document covers the observability and logging infrastructure in GPT Researcher, including real-time monitoring, structured JSON logging, and distributed tracing capabilities. For information about testing and validation, see [Testing and Validation](#11.4). For server configuration and startup, see [Server Configuration and Entry Points](#11.2).

## Purpose and Scope

GPT Researcher provides multiple layers of observability to track research execution, debug issues, and optimize performance:

1.  **Structured JSON Logging** - Captures all research events, sources, and outputs in timestamped log files.
2.  **Real-time WebSocket Monitoring** - Tracks connection health, research progress, and activity metrics in the frontend.
3.  **LangSmith Tracing** - Provides detailed traces of LLM interactions and multi-agent workflows for debugging.
4.  **Research ID Tracking** - Associates all logs and outputs with unique research identifiers for organization.

## Logging Infrastructure

### CustomLogsHandler

The `CustomLogsHandler` class is the central logging component that captures all research activity and streams it to both WebSocket clients and persistent JSON files. It is defined in [backend/server/server_utils.py:33-54]().

**Class Definition:**

| Property | Type | Purpose |
| :--- | :--- | :--- |
| `logs` | `List` | In-memory log accumulator |
| `websocket` | `WebSocket` | Connection for real-time streaming |
| `log_file` | `str` | Path to JSON output file in the `outputs` directory |
| `timestamp` | `str` | ISO format creation timestamp |

The handler is instantiated for each research task in the `handle_start_command` function [backend/server/server_utils.py:148-155]():

```python
# Create logs handler with websocket and task
logs_handler = CustomLogsHandler(websocket, task)
# Initialize log content with query
await logs_handler.send_json({
    "query": task,
    "sources": [],
    "context": [],
    "report": ""
})
```

**Key Method - send_json:**

The `send_json` method handles dual-output logging by updating a persistent JSON file and sending data to the client [backend/server/server_utils.py:56-79](). It updates the `events` list for logs or the `content` dictionary for report data [backend/server/server_utils.py:67-75]().

#### Logging Data Flow

Title: Research Logging and Data Persistence Flow
```mermaid
flowchart TD
    "handle_start_command"["backend/server/server_utils.py: handle_start_command"]
    "CustomLogsHandler"["backend/server/server_utils.py: CustomLogsHandler"]
    "InitFile"["Create outputs/{sanitized}.json"]
    "run_agent"["backend/server/websocket_manager.py: run_agent"]
    
    "handle_start_command" --> "CustomLogsHandler"
    "CustomLogsHandler" --> "InitFile"
    "handle_start_command" --> "run_agent"
    
    subgraph "Stream Loop"
        "stream_output"["gpt_researcher/actions/utils.py: stream_output"]
        "send_json"["CustomLogsHandler.send_json"]
        "WS"["WebSocket.send_json"]
        "Disk"["Update JSON File"]
        
        "stream_output" --> "send_json"
        "send_json" --> "WS"
        "send_json" --> "Disk"
    end
    
    "run_agent" --> "stream_output"
```
Sources: [backend/server/server_utils.py:33-80](), [backend/server/websocket_manager.py:116-119](), [gpt_researcher/actions/utils.py:15-15]()

### Research ID System

Each research task generates a unique identifier for tracking and file organization.

- **Basic Reports**: Generated via `_generate_research_id` in [backend/report_type/basic_report/basic_report.py:66-70]().
- **Detailed Reports**: Generated via `_generate_research_id` in [backend/report_type/detailed_report/detailed_report.py:78-82]().
- **Researcher Class**: Uses a timestamp and hash in [backend/server/server_utils.py:86-87]().

The implementation typically uses a hash of the query and a timestamp:
```python
def _generate_research_id(self, query: str) -> str:
    timestamp = str(int(time.time()))
    query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
    return f"detailed_{timestamp}_{query_hash}"
```

### Filename Sanitization

To prevent filesystem issues, the `sanitize_filename` function hashes task parts to create a clean output name [backend/server/server_utils.py:115-123](). It uses `hashlib.md5` to generate a 10-character hash of the task description [backend/server/server_utils.py:119-122]().

Sources: [backend/report_type/basic_report/basic_report.py:66-70](), [backend/report_type/detailed_report/detailed_report.py:78-82](), [backend/server/server_utils.py:115-123]()

## Real-time Monitoring

### WebSocket Status Panel

The frontend provides a monitoring panel (defined in [frontend/index.html:88-134]()) that tracks WebSocket health and research activity. This is initialized in the `initWebSocketPanel` function within [frontend/scripts.js]().

**Panel Elements:**

| Element ID | Purpose | Update Frequency |
| :--- | :--- | :--- |
| `connectionStatus` | Shows "Connected", "Disconnected", etc. | On change |
| `researchStatus` | "Active" or "Inactive" based on `isResearchActive` | Dynamic |
| `messagesReceived` | Counter incremented on each message | On event |
| `readyState` | Raw `WebSocket.readyState` value | Dynamic |

**Monitoring Variables:**
The following variables track state globally in [frontend/scripts.js:13-23]():
```javascript
let socket = null;
let connectionStartTime = null;
let lastActivityTime = null;
let connectionAttempts = 0;
let messagesReceived = 0;
```

#### WebSocket Monitoring Architecture

Title: Frontend WebSocket Monitoring State Machine
```mermaid
flowchart TD
    "init"["frontend/scripts.js: init"]
    "initWebSocketPanel"["frontend/scripts.js: initWebSocketPanel"]
    "updateWebSocketStatus"["frontend/scripts.js: updateWebSocketStatus"]
    "onmessage"["socket.onmessage"]
    
    "init" --> "initWebSocketPanel"
    "initWebSocketPanel" --> "updateWebSocketStatus"
    "onmessage" -->|"Increment messagesReceived"| "updateWebSocketStatus"
    
    subgraph "State Checks"
        "ReadyState"["socket.readyState"]
        "Duration"["Date.now() - connectionStartTime"]
    end
    
    "updateWebSocketStatus" --> "ReadyState"
    "updateWebSocketStatus" --> "Duration"
    
    "ReadyState" -->|"0"| "Connecting"
    "ReadyState" -->|"1"| "Connected"
    "ReadyState" -->|"3"| "Disconnected"
```
Sources: [frontend/scripts.js:13-23](), [frontend/index.html:88-134]()

### Research Progress Streaming

During active research, the backend streams log events. The `WebSocketManager` handles the low-level communication [backend/server/websocket_manager.py:21-29](), while `run_agent` coordinates the logging flow [backend/server/websocket_manager.py:116-120]().

**Message Types:**
- `logs`: Displayed in the output console [backend/server/server_utils.py:67-72]().
- `report`: Updates the main report container.
- `path`: Provides links to generated files (PDF, DOCX, JSON) via `send_file_paths` [backend/server/server_utils.py:178-178]().
- `chat`: Used for the interactive research assistant [backend/server/server_utils.py:187-210]().

Sources: [backend/server/websocket_manager.py:21-120](), [backend/server/server_utils.py:187-210]()

## LangSmith Integration

GPT Researcher supports **LangSmith** for distributed tracing of LLM interactions, as documented in the user guides [docs/docs/gpt-researcher/handling-logs/langsmith-logs.md:1-29]().

### Configuration
Tracing is enabled by setting environment variables as required by the LangChain ecosystem [docs/docs/gpt-researcher/handling-logs/langsmith-logs.md:11-16]():
- `LANGCHAIN_TRACING_V2=true`
- `LANGCHAIN_API_KEY=your_key`

### What Gets Traced
When enabled, LangSmith captures:
1.  **LLM Calls**: All interactions processed through the LangChain-compatible providers.
2.  **Multi-Agent Workflows**: State transitions in the LangGraph-based system coordinated by `ChiefEditorAgent` [backend/server/multi_agent_runner.py:31-33]().
3.  **Tool Invocations**: Web searches and scraping actions.

Sources: [docs/docs/gpt-researcher/handling-logs/langsmith-logs.md:1-29](), [backend/server/multi_agent_runner.py:31-33]()

## Log File Structure

### JSON Log Format
Each research task generates a JSON log file in the `outputs` directory [backend/server/server_utils.py:39-40]().

**Schema Description [backend/server/server_utils.py:43-54]():**

| Field | Description |
| :--- | :--- |
| `timestamp` | ISO format creation timestamp |
| `events[]` | Array of event objects containing individual timestamps and data |
| `content.query` | The original research query |
| `content.sources` | List of URLs visited |
| `content.context` | Research context gathered |
| `content.report` | The final Markdown content |
| `content.costs` | API usage cost (if available) |

### Output Directory Structure
All logs and generated files are stored in the `outputs/` directory [backend/server/server_utils.py:42-42]().

```text
outputs/
├── task_1700000000_abc123.json  # JSON log
├── task_1700000000_abc123.pdf   # PDF report
├── task_1700000000_abc123.docx  # Word report
└── task_1700000000_abc123.md    # Markdown report
```

Sources: [backend/server/server_utils.py:33-79](), [docs/docs/gpt-researcher/handling-logs/all-about-logs.md:9-13]()

## Debugging Workflows

### Debugging Research Execution
1.  **Check WebSocket Status**: Open the "Status" panel in the frontend to verify the connection is `OPEN` [frontend/index.html:88-134]().
2.  **Inspect JSON Logs**: Locate the `.json` file in the `outputs` folder to see the raw `events` sequence [docs/docs/gpt-researcher/handling-logs/all-about-logs.md:5-13]().
3.  **Review Console Logs**: The server uses standard Python logging for general errors [backend/server/websocket_manager.py:19-19]().

### Debugging Multi-Agent Workflows
Multi-agent tasks are handled by `run_multi_agent_task` [backend/server/multi_agent_runner.py:31-33]().
- **Logs Handler**: The `CustomLogsHandler` is passed as the `websocket` parameter to capture internal agent logs and route them to the UI [backend/server/websocket_manager.py:119-137]().
- **Human Feedback**: The system includes a `handle_human_feedback` function to receive and log manual input during the research loop [backend/server/server_utils.py:181-184]().

Sources: [backend/server/server_utils.py:181-184](), [backend/server/multi_agent_runner.py:31-33](), [backend/server/websocket_manager.py:116-137]()

---

# Page: Cloud and Infrastructure Deployment

# Cloud and Infrastructure Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/build.yml](.github/workflows/build.yml)
- [.github/workflows/deploy.yml](.github/workflows/deploy.yml)
- [.github/workflows/docker-build.yml](.github/workflows/docker-build.yml)
- [docs/docs/gpt-researcher/context/tailored-research.md](docs/docs/gpt-researcher/context/tailored-research.md)
- [docs/docs/gpt-researcher/multi_agents/langgraph.md](docs/docs/gpt-researcher/multi_agents/langgraph.md)
- [terraform/ecr-setup/main.tf](terraform/ecr-setup/main.tf)
- [terraform/ecr-setup/outputs.tf](terraform/ecr-setup/outputs.tf)
- [terraform/ecr-setup/variables.tf](terraform/ecr-setup/variables.tf)
- [terraform/ecr-setup/versions.tf](terraform/ecr-setup/versions.tf)
- [terraform/github-actions-setup/main.tf](terraform/github-actions-setup/main.tf)
- [terraform/github-actions-setup/outputs.tf](terraform/github-actions-setup/outputs.tf)
- [terraform/github-actions-setup/variables.tf](terraform/github-actions-setup/variables.tf)
- [terraform/github-actions-setup/versions.tf](terraform/github-actions-setup/versions.tf)
- [terraform/main.tf](terraform/main.tf)
- [tests/__init__.py](tests/__init__.py)
- [tests/gptr-logs-handler.py](tests/gptr-logs-handler.py)
- [tests/report-types.py](tests/report-types.py)
- [tests/research_test.py](tests/research_test.py)
- [tests/test_logging.py](tests/test_logging.py)
- [tests/test_logs.py](tests/test_logs.py)

</details>



This page documents the production-grade infrastructure for GPT Researcher, focusing on AWS deployment using Terraform, container orchestration via Amazon ECS (Fargate), and automated CI/CD pipelines using GitHub Actions.

## Infrastructure Architecture Overview

The GPT Researcher infrastructure is designed for high availability and scalability using a serverless container approach. The system is partitioned into three main Terraform layers: ECR Setup, GitHub Actions IAM Setup, and the Core ECS Service.

### System Infrastructure Diagram

The following diagram illustrates the relationship between the AWS infrastructure components and the deployment lifecycle.

**Infrastructure Component Relationship**
```mermaid
graph TD
    subgraph "AWS_Cloud"
        subgraph "Storage_Layer"
            [S3_Bucket] -->|Remote_State| [Terraform_Backend]
            [ECR_Repository] -->|Docker_Images| [ECS_Fargate]
            [EFS_Volume] -->|Persistent_Storage| [ECS_Fargate]
        end

        subgraph "Compute_Layer"
            [ECS_Fargate] -->|Runs| [GPT_Researcher_Container]
            [GPT_Researcher_Container] -->|Health_Check| [ALB_Target_Group]
        end

        subgraph "Security_Layer"
            [Secrets_Manager] -->|Injected_Env| [ECS_Fargate]
            [IAM_Roles] -->|Permissions| [ECS_Fargate]
            [Security_Groups] -->|Traffic_Control| [ECS_Fargate]
        end
    end

    subgraph "CI_CD_Pipeline"
        [GitHub_Repository] -->|Triggers| [Build_Workflow]
        [Build_Workflow] -->|Push_Image| [ECR_Repository]
        [Build_Workflow] -->|Dispatch| [Deploy_Workflow]
        [Deploy_Workflow] -->|Terraform_Apply| [ECS_Fargate]
    end
```
Sources: `terraform/main.tf:1-12`(), `.github/workflows/deploy.yml:1-11`()

## Container Registry (ECR) Setup

The application uses Amazon Elastic Container Registry (ECR) to store versioned Docker images. The repository is configured to be immutable to ensure deployment consistency.

*   **Repository Name:** Defaults to the project name `gpt-researcher` [terraform/ecr-setup/variables.tf:1-10]().
*   **Environment:** Configurable for `dev`, `staging`, or `prod` [terraform/ecr-setup/variables.tf:12-21]().
*   **Remote State:** The ECR URL is exported and consumed by the main ECS service via a `terraform_remote_state` data source [terraform/main.tf:1-16]().

Sources: `terraform/ecr-setup/variables.tf:1-21`(), `terraform/main.tf:1-16`()

## ECS Service Configuration

The core compute is handled by an ECS Service running on AWS Fargate. It utilizes a shared VPC and ECS cluster defined in a common modules repository.

### Compute and Networking
*   **Port:** The container runs on port `3535` (Gradio default) [terraform/main.tf:50-50]().
*   **Cluster:** Deployed into a `general` cluster managed by a common infrastructure module [terraform/main.tf:49-49]().
*   **Service Discovery:** Integrated with AWS CloudMap using the namespace provided by the common module [terraform/main.tf:52-54]().

### Persistent Storage (EFS)
To maintain state across container restarts (such as the SQLite database for research tasks), an Elastic File System (EFS) volume is mounted.
*   **Mount Point:** `/pipelines` [terraform/main.tf:202-202]().
*   **Database Path:** `/pipelines/gravity-researcher/research_tasks.db` [terraform/main.tf:171-171]().
*   **Security:** A dedicated security group `efs_nfs` allows traffic on port `2049` from the ECS service and specific pipeline security groups [terraform/main.tf:80-115]().

### Secrets Management
Secrets are fetched from AWS Secrets Manager and injected as environment variables via the `ecs_service` module.
*   **LLM Keys:** `OPENAI_API_KEY` and `GOOGLE_API_KEY` [terraform/main.tf:179-182]().
*   **Search Keys:** `GOOGLE_CX_KEY` [terraform/main.tf:183-183]().
*   **Email Integration:** Credentials for sending research reports via email [terraform/main.tf:184-186]().

Sources: `terraform/main.tf:151-204`(), `terraform/main.tf:80-115`()

## CI/CD Workflows

The deployment is automated through GitHub Action workflows including `GPTR tests` and `Terraform Deploy`.

### 1. Test and Build Workflow (`docker-build.yml`)
This workflow ensures code quality before deployment.
*   **Environment:** Uses a dedicated `tests` environment [ .github/workflows/docker-build.yml:14-14]().
*   **Docker Compose:** Runs tests within a containerized environment using the `test` profile [ .github/workflows/docker-build.yml:39-45]().

### 2. Deployment Workflow (`deploy.yml`)
This workflow handles the infrastructure-as-code application for the `master` branch.
*   **IAM Role Assumption:** Uses OIDC to assume an AWS role specifically for GitHub Actions [ .github/workflows/deploy.yml:63-67]().
*   **Plan Phase:** On pull requests, it runs `terraform plan` and uses `github-script` to post the plan output as a PR comment [ .github/workflows/deploy.yml:24-112]().
*   **Apply Phase:** On merges to `master`, it executes `terraform apply` [ .github/workflows/deploy.yml:113-200]().
*   **Image Tag Logic:** It determines the image tag based on the following priority:
    1.  Manual input from `workflow_dispatch`.
    2.  Extraction from the current active ECS Task Definition if no input is provided.
    3.  Fallback to `latest` [ .github/workflows/deploy.yml:138-176]().

Sources: `.github/workflows/docker-build.yml:1-45`(), `.github/workflows/deploy.yml:1-200`()

## Deployment Entity Mapping

The following diagram bridges the high-level infrastructure concepts to the specific Terraform resources and GitHub Action jobs.

**Code Entity to Infrastructure Mapping**
```mermaid
graph LR
    subgraph "GitHub_Actions_Space"
        [workflow_dispatch] -->|provides| [image_tag]
        [terraform-apply_Job] -->|executes| [terraform_apply_command]
    end

    subgraph "Terraform_Resource_Space"
        [terraform_apply_command] --> [module_ecs_service]
        [module_ecs_service] --> [aws_ecs_task_definition]
        [aws_ecs_task_definition] --> [container_definitions]
    end

    subgraph "AWS_Runtime_Space"
        [container_definitions] -->|env| [OPENAI_API_KEY]
        [container_definitions] -->|mount| [efs_volumes]
        [container_definitions] -->|image| [ecr_repository_url]
    end

    [image_tag] -.-> [container_definitions]
```
Sources: `terraform/main.tf:151-187`(), `terraform/main.tf:197-204`(), `.github/workflows/deploy.yml:138-176`()

## Environment Configuration

Key environment variables configured in the `ecs_service` module:

| Variable | Value / Source | Purpose |
| :--- | :--- | :--- |
| `PORT` | `3535` | Application listening port [terraform/main.tf:169-169]() |
| `DB_PATH` | `/pipelines/gravity-researcher/research_tasks.db` | Persistent SQLite storage [terraform/main.tf:171-171]() |
| `S3_BUCKET` | `ggai-generated-files` | Destination for research reports [terraform/main.tf:173-173]() |
| `TEMP_DIRECTORY` | `/pipelines/gravity-researcher/tmp` | Temporary processing space [terraform/main.tf:175-175]() |
| `AWS_REGION` | `us-east-1` | AWS deployment region [terraform/main.tf:170-170]() |

Sources: `terraform/main.tf:168-177`()

---

# Page: Development Guide

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.cursorrules](.cursorrules)
- [.gitignore](.gitignore)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CURSOR_RULES.md](CURSOR_RULES.md)
- [docs/docs/gpt-researcher/gptr/ai-development.md](docs/docs/gpt-researcher/gptr/ai-development.md)
- [docs/docs/gpt-researcher/gptr/image_generation.md](docs/docs/gpt-researcher/gptr/image_generation.md)
- [gpt_researcher/document/document.py](gpt_researcher/document/document.py)
- [pyproject.toml](pyproject.toml)
- [setup.py](setup.py)

</details>



This section provides resources for developers who want to extend, modify, or contribute to GPT Researcher. It covers project structure, dependency management, development environment setup, testing, build processes, and common development patterns.

For specific development tasks:
- Setting up your development environment and understanding the codebase layout → see [Project Structure and Dependencies](#12.1)
- Developing or modifying the Next.js or Vanilla JS frontends → see [Frontend Development](#12.2)
- Adding support for new LLM providers → see [Adding New LLM Providers](#12.3)
- Implementing new search/retrieval providers → see [Adding New Retrievers](#12.4)
- Using Claude or other AI assistants for development → see [AI-Assisted Development](#12.5)

For architecture understanding, refer to [Core Architecture](#3). For configuration details, see [Configuration System](#5).

---

## Repository Structure

The GPT Researcher codebase is organized into distinct layers, each with specific responsibilities. Understanding this structure is essential for effective development.

### Repository Organization Diagram

```mermaid
graph TB
    subgraph "Repository_Root"
        ["/"]
        
        subgraph "Core_Package"
            [gpt_researcher/]
            Agent["gpt_researcher/agent.py<br/>GPTResearcher class"]
            Config["gpt_researcher/config/"]
            Skills["gpt_researcher/skills/"]
            Document["gpt_researcher/document/"]
            Memory["gpt_researcher/memory/"]
            Orchestrator["gpt_researcher/orchestrator/"]
            Prompts["gpt_researcher/prompts.py"]
            Utils["gpt_researcher/utils/"]
        end
        
        subgraph "Multi_Agent_System"
            MultiAgents["multi_agents/"]
            MAMain["multi_agents/main.py"]
            Agents["multi_agents/agents/"]
            MALangGraph["multi_agents/langgraph_*.py"]
        end
        
        subgraph "Backend_Services"
            Backend["backend/"]
            Server["backend/server/"]
            ServerApp["backend/server/app.py<br/>FastAPI app"]
        end
        
        subgraph "Frontend_Applications"
            Frontend["frontend/"]
            NextJS["frontend/nextjs/"]
            VanillaJS["frontend/static/"]
        end
        
        subgraph "Build_System"
            ReqTxt["requirements.txt"]
            SetupPy["setup.py"]
            Pyproject["pyproject.toml"]
            Docker["Dockerfile"]
            Compose["docker-compose.yml"]
        end
        
        subgraph "Tests_Dir"
            Tests["tests/"]
        end
        
        subgraph "AI_Dev_Tools"
            Claude[".claude/skills/"]
            CursorRules["CURSOR_RULES.md"]
        end
    end
    
    ["/"] --> [gpt_researcher/]
    ["/"] --> MultiAgents
    ["/"] --> Backend
    ["/"] --> Frontend
    ["/"] --> SetupPy
    ["/"] --> Pyproject
    ["/"] --> Tests
    ["/"] --> Claude
    
    [gpt_researcher/] --> Agent
    [gpt_researcher/] --> Config
    [gpt_researcher/] --> Skills
    [gpt_researcher/] --> Document
    [gpt_researcher/] --> Memory
    [gpt_researcher/] --> Orchestrator
    [gpt_researcher/] --> Prompts
    [gpt_researcher/] --> Utils
    
    MultiAgents --> MAMain
    MultiAgents --> Agents
    MultiAgents --> MALangGraph
    
    Backend --> Server
    Server --> ServerApp
    
    Frontend --> NextJS
    Frontend --> VanillaJS
```

**Sources:** [setup.py:26-27](), [pyproject.toml:57-58](), [CURSOR_RULES.md:20-55](), [.cursorrules:1-15]()

### Key Directory Purposes

| Directory | Purpose | Key Entities |
|-----------|---------|-----------|
| `gpt_researcher/` | Core research engine package | `GPTResearcher` class [gpt_researcher/agent.py:1-5](), `DocumentLoader` [gpt_researcher/document/document.py:16-17]() |
| `multi_agents/` | LangGraph-based multi-agent system | `ChiefEditorAgent`, `ResearcherAgent` [CURSOR_RULES.md:165-172]() |
| `backend/server/` | FastAPI server and WebSocket handlers | `app` [CURSOR_RULES.md:150-151]() |
| `frontend/nextjs/` | Next.js production frontend | Production UI with enhanced features [CURSOR_RULES.md:21-23]() |
| `frontend/static/` | Vanilla JS lightweight frontend | Static FastAPI version [CURSOR_RULES.md:105-106]() |
| `.claude/skills/` | AI assistant development guides | `SKILL.md`, `REFERENCE.md` [docs/docs/gpt-researcher/gptr/ai-development.md:21-26]() |

**Sources:** [CURSOR_RULES.md:20-55](), [docs/docs/gpt-researcher/gptr/ai-development.md:21-26]()

---

## Development Environment Setup

### Prerequisites

- **Python 3.11+** required for core logic [setup.py:44](), [pyproject.toml:10]()
- **Node.js 18+** for Next.js frontend development [CURSOR_RULES.md:146-147]()
- **Docker** for containerized development [CURSOR_RULES.md:153-154]()

**Sources:** [setup.py:44](), [pyproject.toml:10](), [CURSOR_RULES.md:145-155]()

### Local Setup Workflow

```mermaid
flowchart TD
    Clone["Clone Repository<br/>git clone https://github.com/assafelovic/gpt-researcher"]
    
    PythonEnv["Create Python Environment<br/>python -m venv venv<br/>source venv/bin/activate"]
    
    InstallChoice{"Install Method?"}
    
    PipEditable["Editable Install<br/>pip install -e ."]
    PoetryInstall["Poetry Install<br/>poetry install"]
    
    EnvSetup["Configure Environment<br/>cp .env.example .env<br/>Edit API keys"]
    
    FrontendSetup{"Develop Frontend?"}
    
    NodeSetup["Install Node Dependencies<br/>cd frontend/nextjs<br/>npm install"]
    
    RunTests["Verify Installation<br/>python -m pytest"]
    
    DevReady["Development Ready"]
    
    Clone --> PythonEnv
    PythonEnv --> InstallChoice
    
    InstallChoice --> PipEditable
    InstallChoice --> PoetryInstall
    
    PipEditable --> EnvSetup
    PoetryInstall --> EnvSetup
    
    EnvSetup --> FrontendSetup
    
    FrontendSetup -->|"Yes"| NodeSetup
    FrontendSetup -->|"No"| RunTests
    
    NodeSetup --> RunTests
    RunTests --> DevReady
```

**Sources:** [setup.py:22-48](), [pyproject.toml:1-52](), [CURSOR_RULES.md:145-155]()

---

## Dependency Management

GPT Researcher uses `setup.py` for pip packaging and `pyproject.toml` for Poetry/UV dependency management.

### Core Dependencies

The project relies on several key libraries for its functionality:
- **LLM Orchestration**: `langchain`, `langgraph` [pyproject.toml:21-27]()
- **Web Scraping**: `beautifulsoup4`, `duckduckgo_search`, `arxiv` [pyproject.toml:12-15]()
- **Document Processing**: `PyMuPDF`, `python-docx`, `unstructured` [pyproject.toml:35-43]()
- **Web Server**: `fastapi`, `uvicorn`, `websockets` [pyproject.toml:16-45]()

**Sources:** [pyproject.toml:9-48](), [setup.py:19-20]()

---

## Development Workflow

### Research Execution Flow

The system follows a coordinated flow between the agent, document processing, and report generation.

```mermaid
sequenceDiagram
    participant U as User
    participant G as [gpt_researcher/agent.py]
    participant D as [gpt_researcher/document/document.py]
    participant I as [gpt_researcher/gptr/image_generation.md]

    U->>G: GPTResearcher(query, report_type)
    G->>G: conduct_research()
    G->>D: load() (if local docs)
    D-->>G: docs_content
    G->>I: Pre-generate images (if enabled)
    G->>G: write_report()
    G-->>U: Markdown Report
```

**Sources:** [gpt_researcher/document/document.py:16-61](), [docs/docs/gpt-researcher/gptr/image_generation.md:64-82](), [CURSOR_RULES.md:44-49]()

### Common Development Patterns

#### Adding a New Feature
When adding features like `IMAGE_GENERATION_ENABLED` [docs/docs/gpt-researcher/gptr/image_generation.md:23](), developers should follow the established pattern:
1. **Config**: Add environment variables to `.env` [docs/docs/gpt-researcher/gptr/image_generation.md:19-36]()
2. **Logic**: Implement in the core `gpt_researcher` package.
3. **Frontend**: Update the Next.js or static frontend to handle new data types.

**Sources:** [docs/docs/gpt-researcher/gptr/image_generation.md:19-36](), [CURSOR_RULES.md:135-144]()

---

## Testing Infrastructure

The project uses `pytest` for automated testing.

### Running Tests
- **Python Tests**: `python -m pytest` [CURSOR_RULES.md:149]()
- **Docker Tests**: `docker-compose run gpt-researcher-tests` [CURSOR_RULES.md:154]()
- **Frontend Tests**: `npm run test` [CURSOR_RULES.md:148]()

**Sources:** [pyproject.toml:54-59](), [CURSOR_RULES.md:145-155]()

---

## AI-Assisted Development

The project includes specific resources to help AI assistants understand the codebase:
- **`.claude/skills/SKILL.md`**: Comprehensive guide for Claude [docs/docs/gpt-researcher/gptr/ai-development.md:28-47]()
- **`CURSOR_RULES.md`**: Rules for the Cursor IDE to maintain code quality and follow project conventions [CURSOR_RULES.md:1-181]()

**Sources:** [docs/docs/gpt-researcher/gptr/ai-development.md:6-26](), [CURSOR_RULES.md:1-5]()

---

## Next Steps

For more detailed information on specific development topics:

- **Project Structure and Dependencies** → [Project Structure and Dependencies](#12.1)
- **Frontend Development** → [Frontend Development](#12.2)
- **Adding New LLM Providers** → [Adding New LLM Providers](#12.3)
- **Adding New Retrievers** → [Adding New Retrievers](#12.4)
- **AI-Assisted Development** → [AI-Assisted Development](#12.5)

---

# Page: Project Structure and Dependencies

# Project Structure and Dependencies

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [Dockerfile](Dockerfile)
- [docker-compose.yml](docker-compose.yml)
- [docs/docs/gpt-researcher/gptr/ai-development.md](docs/docs/gpt-researcher/gptr/ai-development.md)
- [docs/docs/gpt-researcher/gptr/image_generation.md](docs/docs/gpt-researcher/gptr/image_generation.md)
- [gpt_researcher/document/document.py](gpt_researcher/document/document.py)
- [pyproject.toml](pyproject.toml)
- [requirements.txt](requirements.txt)
- [setup.py](setup.py)

</details>



This document describes the organization of the GPT Researcher repository, how dependencies are managed across different package managers, and how the project is configured for distribution. This includes the directory structure, dependency files (`requirements.txt`, `pyproject.toml`, `setup.py`), Docker configuration, and development tooling.

## Repository Organization

The GPT Researcher repository follows a modular structure separating core research logic, user interfaces, multi-agent workflows, and supporting infrastructure.

### Directory Layout

The following diagram illustrates the high-level organization of the repository and how the `GPTResearcher` agent relates to its supporting modules.

**Repository Hierarchy**
```mermaid
graph TB
    Root["Repository Root"]
    
    Core["gpt_researcher/<br/>Core Research Engine"]
    Backend["backend/<br/>FastAPI Server"]
    Frontend["frontend/<br/>User Interfaces"]
    MultiAgent["multi_agents/<br/>LangGraph System"]
    Tests["tests/<br/>Test Suite"]
    Docs["docs/<br/>Documentation"]
    Config["Configuration Files"]
    
    Root --> Core
    Root --> Backend
    Root --> Frontend
    Root --> MultiAgent
    Root --> Tests
    Root --> Docs
    Root --> Config
    
    CoreSub1["agent.py<br/>GPTResearcher class"]
    CoreSub2["config/<br/>Config system"]
    CoreSub3["skills/<br/>Skill managers"]
    CoreSub4["document/<br/>DocumentLoader"]
    CoreSub5["memory/<br/>Memory class"]
    CoreSub6["llm_provider/<br/>GenericLLMProvider"]
    CoreSub7["retrievers/<br/>Search providers"]
    
    Core --> CoreSub1
    Core --> CoreSub2
    Core --> CoreSub3
    Core --> CoreSub4
    Core --> CoreSub5
    Core --> CoreSub6
    Core --> CoreSub7
    
    BackendSub1["server/<br/>FastAPI app"]
    BackendSub2["server_utils.py<br/>WebSocket handlers"]
    
    Backend --> BackendSub1
    Backend --> BackendSub2
    
    FrontendSub1["nextjs/<br/>Next.js app"]
    FrontendSub2["static/<br/>Vanilla JS"]
    FrontendSub3["embed.js<br/>Widget script"]
    
    Frontend --> FrontendSub1
    Frontend --> FrontendSub2
    Frontend --> FrontendSub3
    
    MASub1["agents/<br/>Specialized agents"]
    MASub2["main.py<br/>CLI entry"]
    MASub3["task.json<br/>Config template"]
    
    MultiAgent --> MASub1
    MultiAgent --> MASub2
    MultiAgent --> MASub3
    
    ConfigSub1["requirements.txt"]
    ConfigSub2["pyproject.toml"]
    ConfigSub3["setup.py"]
    ConfigSub4["docker-compose.yml"]
    ConfigSub5["Dockerfile"]
    ConfigSub6[".env"]
    
    Config --> ConfigSub1
    Config --> ConfigSub2
    Config --> ConfigSub3
    Config --> ConfigSub4
    Config --> ConfigSub5
    Config --> ConfigSub6
```
Sources: [requirements.txt:1-68](), [setup.py:1-48](), [pyproject.toml:1-214](), [docker-compose.yml:1-78](), [Dockerfile:1-65]()

### Core Module Structure

The `gpt_researcher/` directory contains the core research engine packaged for PyPI distribution. Key components include the `GPTResearcher` class in `agent.py` and the `DocumentLoader` for processing local files.

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `gpt_researcher/` | Main package root | `__init__.py`, `agent.py` (GPTResearcher class) |
| `gpt_researcher/config/` | Configuration system | `config.py` (Config class) |
| `gpt_researcher/skills/` | Research skills | `researcher.py`, `browser.py`, `context_manager.py` |
| `gpt_researcher/llm_provider/` | LLM abstraction | `generic_provider.py` (GenericLLMProvider) |
| `gpt_researcher/memory/` | Embeddings & vectors | `embeddings.py` (Memory class) |
| `gpt_researcher/retrievers/` | Search providers | `tavily.py`, `duckduckgo.py`, `arxiv.py` |
| `gpt_researcher/document/` | Document loading | `document.py` (DocumentLoader) |

Sources: [gpt_researcher/document/document.py:16-18](), [requirements.txt:1-68]()

## Dependency Management System

GPT Researcher uses three parallel dependency specification systems to support different package managers and use cases.

### Dependency Files Overview

The project maintains `requirements.txt` for simple pip/Docker installs, `pyproject.toml` for Poetry/UV workflows, and `setup.py` for PyPI distribution filtering.

**Dependency Flow Diagram**
```mermaid
graph TB
    subgraph "Package Managers"
        Pip["pip"]
        Poetry["poetry"]
        UV["uv"]
    end
    
    subgraph "Dependency Files"
        ReqTxt["requirements.txt<br/>Direct dependencies<br/>68 packages"]
        PyProject["pyproject.toml<br/>Poetry configuration<br/>214+ dependencies"]
        SetupPy["setup.py<br/>PyPI distribution<br/>Filters requirements.txt"]
    end
    
    subgraph "Installation Methods"
        PipInstall["pip install -r requirements.txt"]
        PoetryInstall["poetry install"]
        UVInstall["uv pip install"]
        PyPIInstall["pip install gpt-researcher"]
    end
    
    Pip --> ReqTxt
    Poetry --> PyProject
    UV --> PyProject
    
    ReqTxt --> PipInstall
    ReqTxt --> SetupPy
    PyProject --> PoetryInstall
    PyProject --> UVInstall
    SetupPy --> PyPIInstall
```
Sources: [requirements.txt:1-68](), [pyproject.toml:1-214](), [setup.py:1-48]()

### requirements.txt: Docker and pip

The `requirements.txt` file specifies direct dependencies for Docker builds and pip-based installations. It contains 68 core packages organized into functional groups.

| Category | Key Packages | Purpose |
|----------|-------------|---------|
| Core Framework | `fastapi>=0.104.1`, `uvicorn>=0.24.0.post1`, `pydantic>=2.5.1` | HTTP server and data validation [requirements.txt:5-7]() |
| LangChain v1 | `langchain>=1.0.0`, `langgraph>=0.2.76`, `langchain-openai>=1.0.0` | LLM orchestration [requirements.txt:11-18]() |
| LLM Providers | `openai>=1.3.3`, `ollama>=0.4.8`, `litellm>=1.71.0` | LLM API clients [requirements.txt:21-23]() |
| Search & Research | `tavily-python>=0.7.12`, `ddgs>=9.0.0`, `arxiv>=2.0.0` | Web search APIs [requirements.txt:27-29]() |
| Document Processing | `beautifulsoup4>=4.12.2`, `pymupdf>=1.23.6`, `python-docx>=1.1.0` | File parsing [requirements.txt:32-34]() |
| Output Formats | `md2pdf>=1.0.1`, `mistune>=3.0.2`, `htmldocx>=0.0.6` | Report generation [requirements.txt:55-57]() |

Sources: [requirements.txt:1-68]()

### pyproject.toml: Poetry and uv

The `pyproject.toml` file provides comprehensive dependency management. It includes a massive list of 214+ dependencies with exact version pins to ensure environment reproducibility.

**Key Configurations:**
- **Build System**: Uses `poetry-core` as the backend [pyproject.toml:50-52]().
- **Python Version**: Requires `python = ">=3.11"` [pyproject.toml:10]().
- **Optional Dependencies**: Includes `requirements-txt` group for various LLM providers like `langchain-anthropic`, `langchain-cohere`, and `langchain-google-genai` [pyproject.toml:216-239]().
- **Testing**: Configures `pytest` with `asyncio_mode = "strict"` [pyproject.toml:54-59]().
- **UV Support**: Defines workspace sources for `uv` [pyproject.toml:61-62]().

Sources: [pyproject.toml:1-214]()

### setup.py: PyPI Distribution

The `setup.py` file configures the package for PyPI distribution. It dynamically reads `requirements.txt` but filters out specific packages that are not needed for the library-only distribution.

**Excluded Packages in setup.py:** [setup.py:5-14]()
- `selenium`, `webdriver` (Optional browser automation)
- `fastapi`, `uvicorn` (Server-side components)
- `jinja2` (Template engine)
- `gpt-researcher` (Self-reference)
- `langgraph` (Multi-agent framework)

**Package Metadata:** [setup.py:22-45]()
- **Name**: `gpt-researcher`
- **Version**: `0.14.7` (Defined as `LATEST_VERSION`)
- **Author**: Assaf Elovic
- **License**: MIT
- **Python Requires**: `>=3.11`

Sources: [setup.py:1-48]()

## Docker Configuration

GPT Researcher uses a multi-stage Docker build strategy for optimized image size and `docker-compose` for service orchestration.

### Multi-Stage Dockerfile

The `Dockerfile` is split into three stages to manage browser dependencies and Python environments efficiently.

1.  **Stage 1: install-browser**: Installs Chromium, Chromedriver, Firefox-esr, and Geckodriver. It uses architecture detection for `amd64` and `arm64` [Dockerfile:3-21]().
2.  **Stage 2: gpt-researcher-install**: Copies and installs Python dependencies from `requirements.txt` and `multi_agents/requirements.txt` [Dockerfile:24-35]().
3.  **Stage 3: gpt-researcher**: Sets up a non-root user `gpt-researcher`, configures the `outputs/` directory permissions, and defines the entry point using `uvicorn main:app` [Dockerfile:38-64]().

Sources: [Dockerfile:1-65]()

### Docker Compose Services

The `docker-compose.yml` orchestrates the backend, frontend, and testing services.

| Service | Image/Build | Port | Role |
|---------|-------------|------|------|
| `gpt-researcher` | `gptresearcher/gpt-researcher` | 8000 | FastAPI Backend [docker-compose.yml:2-24]() |
| `gptr-nextjs` | `gptresearcher/gptr-nextjs` | 3000 | Next.js Frontend [docker-compose.yml:26-45]() |
| `gpt-researcher-tests` | `gptresearcher/gpt-researcher-tests` | N/A | Pytest suite (Profile: test) [docker-compose.yml:47-62]() |
| `discord-bot` | `./docs/discord-bot` | 3001 | Discord Integration (Profile: discord) [docker-compose.yml:64-78]() |

Sources: [docker-compose.yml:1-78]()

## Document Loading System

The `DocumentLoader` class is responsible for ingesting local files into the research context. It maps file extensions to specific LangChain loaders.

**Document Loading Implementation**
```mermaid
graph LR
    Loader["DocumentLoader<br/>(gpt_researcher/document/document.py)"]
    Path["Input: path (str/list)"]
    
    Loader --> Path
    Path --> ExtCheck["Extension Check"]
    
    ExtCheck -->|".pdf"| PDF["PyMuPDFLoader"]
    ExtCheck -->|".docx"| DOCX["UnstructuredWordDocumentLoader"]
    ExtCheck -->|".pptx"| PPTX["UnstructuredPowerPointLoader"]
    ExtCheck -->|".csv"| CSV["UnstructuredCSVLoader"]
    ExtCheck -->|".md"| MD["UnstructuredMarkdownLoader"]
    ExtCheck -->|".html"| HTML["BSHTMLLoader"]
    
    PDF --> Result["List of Documents<br/>(raw_content, url)"]
    DOCX --> Result
    PPTX --> Result
    CSV --> Result
    MD --> Result
    HTML --> Result
```
Sources: [gpt_researcher/document/document.py:16-93]()

### Supported File Types
The `_load_document` method handles the following mapping [gpt_researcher/document/document.py:63-78]():
- **PDF**: `PyMuPDFLoader`
- **Text**: `TextLoader`
- **Word**: `UnstructuredWordDocumentLoader` (for `.doc` and `.docx`)
- **PowerPoint**: `UnstructuredPowerPointLoader`
- **Excel**: `UnstructuredExcelLoader` (for `.xls` and `.xlsx`)
- **Markdown**: `UnstructuredMarkdownLoader`
- **HTML**: `BSHTMLLoader` (for `.html` and `.htm`)

Sources: [gpt_researcher/document/document.py:1-93]()

## AI-Assisted Development Tools

The project includes specialized configuration for AI assistants to facilitate contributions.

| Tool/Directory | Purpose |
|----------------|---------|
| `.claude/skills/` | Contains `SKILL.md` and `REFERENCE.md` for Claude Code onboarding [docs/docs/gpt-researcher/gptr/ai-development.md:19-26]() |
| `CONTRIBUTING.md` | Guidelines for reporting issues and contributing code [CONTRIBUTING.md:1-43]() |

Sources: [docs/docs/gpt-researcher/gptr/ai-development.md:1-168](), [CONTRIBUTING.md:1-43]()

---

# Page: Frontend Development

# Frontend Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [frontend/nextjs/.babelrc.build.json](frontend/nextjs/.babelrc.build.json)
- [frontend/nextjs/README.md](frontend/nextjs/README.md)
- [frontend/nextjs/app/globals.css](frontend/nextjs/app/globals.css)
- [frontend/nextjs/app/layout.tsx](frontend/nextjs/app/layout.tsx)
- [frontend/nextjs/components/Settings/Modal.tsx](frontend/nextjs/components/Settings/Modal.tsx)
- [frontend/nextjs/components/Settings/Settings.css](frontend/nextjs/components/Settings/Settings.css)
- [frontend/nextjs/helpers/getHost.ts](frontend/nextjs/helpers/getHost.ts)
- [frontend/nextjs/package.json](frontend/nextjs/package.json)
- [frontend/nextjs/package.lib.json](frontend/nextjs/package.lib.json)
- [frontend/nextjs/rollup.config.js](frontend/nextjs/rollup.config.js)
- [frontend/nextjs/src/GPTResearcher.tsx](frontend/nextjs/src/GPTResearcher.tsx)
- [frontend/nextjs/src/index.css](frontend/nextjs/src/index.css)
- [frontend/nextjs/src/index.ts](frontend/nextjs/src/index.ts)
- [frontend/nextjs/tsconfig.json](frontend/nextjs/tsconfig.json)
- [frontend/nextjs/tsconfig.lib.json](frontend/nextjs/tsconfig.lib.json)

</details>



This document provides technical guidance for developers working on the GPT Researcher frontend interfaces. It covers the Next.js production frontend, the Vanilla JS lightweight alternative, and the build processes for distribution.

## Overview

GPT Researcher provides multiple frontend implementations to accommodate different deployment scenarios:

| Frontend Type | Technology Stack | Use Case | Location |
|--------------|------------------|----------|----------|
| Next.js Production Frontend | React 18, Next.js 14, TypeScript, Tailwind CSS | Full-featured production deployments | `frontend/nextjs/` |
| Vanilla JS Frontend | HTML/CSS/JavaScript | Lightweight deployments served by FastAPI | `frontend/` (static files) |
| Next.js Library | Rollup, TypeScript | Embedding GPT Researcher as a React component | `frontend/nextjs/dist/` |

All frontends communicate with the FastAPI backend server using the WebSocket protocol for real-time research streaming.

Sources: [frontend/nextjs/package.json:2-13](), [frontend/nextjs/src/GPTResearcher.tsx:26-32]()

## Next.js Frontend Architecture

### Core Component Structure

The Next.js frontend is built as a modular React application. The central entry point for the UI component is `GPTResearcher.tsx`.

```mermaid
graph TD
    subgraph "Main Entry"
        GPTR["GPTResearcher.tsx<br/>(Main Component)"]
    end

    subgraph "Hooks & State"
        WS["useWebSocket.ts<br/>(Connection Logic)"]
        DataProc["dataProcessing.ts<br/>(Stream Parser)"]
    end

    subgraph "UI Layers"
        Hero["Hero.tsx<br/>(Landing/Input)"]
        SettingsModal["Modal.tsx<br/>(Preferences)"]
        ChatBox["ChatBox.tsx<br/>(Config/Settings)"]
        Results["ResearchResults.tsx<br/>(Output Display)"]
        HumanFeedback["HumanFeedback.tsx<br/>(Intervention UI)"]
    end

    GPTR --> WS
    GPTR --> Hero
    GPTR --> SettingsModal
    GPTR --> Results
    GPTR --> HumanFeedback
    SettingsModal --> ChatBox
    WS --> DataProc
```

**Diagram: Next.js Component Hierarchy and Data Flow**

Sources: [frontend/nextjs/src/GPTResearcher.tsx:1-32](), [frontend/nextjs/components/Settings/Modal.tsx:1-17]()

### WebSocket Implementation and Data Flow

The frontend maintains a persistent WebSocket connection to the backend to handle streamed research results, logs, and human feedback requests.

```mermaid
sequenceDiagram
    participant UI as "GPTResearcher.tsx"
    participant Hook as "useWebSocket.ts"
    participant WS as "WebSocket Server"

    UI->>Hook: initializeWebSocket(newQuestion, chatBoxSettings)
    Hook->>WS: new WebSocket(uri)
    
    loop Stream
        WS-->>Hook: onmessage (JSON data)
        Hook->>UI: setOrderedData(prev => [...prev, data])
    end

    alt Human Feedback Requested
        WS-->>Hook: type: 'human_feedback'
        Hook->>UI: setShowHumanFeedback(true)
        UI->>WS: send {type: 'human_feedback', content: feedback}
    end

    WS-->>Hook: type: 'report'
    Hook->>UI: setAnswer(data.output)
```

**Diagram: WebSocket Communication Lifecycle**

Key functions in the WebSocket flow:
- `initializeWebSocket`: Establishes the connection and sends the initial research request with user settings [frontend/nextjs/src/GPTResearcher.tsx:76-82]().
- `handleFeedbackSubmit`: Sends human intervention data back to the backend via the existing socket [frontend/nextjs/src/GPTResearcher.tsx:84-89]().
- `handleStopResearch`: Closes the socket connection and reloads the page to reset state [frontend/nextjs/src/GPTResearcher.tsx:194-203]().

Sources: [frontend/nextjs/src/GPTResearcher.tsx:76-203](), [frontend/nextjs/helpers/getHost.ts:5-26]()

## Configuration and Settings

The frontend provides a comprehensive settings interface via `Modal.tsx` and `ChatBox.tsx`. These settings are persisted in `localStorage`.

### Persistence Strategy
- `apiVariables`: Stores environment-specific settings like `DOC_PATH` [frontend/nextjs/components/Settings/Modal.tsx:22-24]().
- `chatBoxSettings`: Stores research preferences like `report_type`, `report_source`, and `tone` [frontend/nextjs/src/GPTResearcher.tsx:40-50]().
- `GPTR_API_URL`: The backend host URL, retrieved via the `getHost` helper [frontend/nextjs/helpers/getHost.ts:8-12]().

### Research Parameters
The `ChatBoxSettings` interface allows users to configure the following:
- **Report Type**: Default is `research_report` [frontend/nextjs/src/GPTResearcher.tsx:42]().
- **Report Source**: Options include `web`, `local`, etc. [frontend/nextjs/src/GPTResearcher.tsx:41]().
- **Tone**: Qualitative style of the report [frontend/nextjs/src/GPTResearcher.tsx:43]().
- **MCP**: Model Context Protocol settings including `mcp_enabled` and `mcp_strategy` [frontend/nextjs/src/GPTResearcher.tsx:47-49]().

Sources: [frontend/nextjs/src/GPTResearcher.tsx:40-50](), [frontend/nextjs/components/Settings/Modal.tsx:55-75]()

## Build Processes and NPM Scripts

The Next.js frontend supports two primary build modes: a standard Next.js application and a bundled library for external use.

### NPM Scripts Reference
| Script | Command | Purpose |
|--------|---------|---------|
| `dev` | `next dev` | Local development server [frontend/nextjs/package.json:16]() |
| `build` | `next build` | Production Next.js application build [frontend/nextjs/package.json:17]() |
| `build:lib` | `rollup -c` | Bundles the UI as a library using Rollup [frontend/nextjs/package.json:20]() |
| `build:types`| `cp src/index.d.ts dist/` | Copies TypeScript definitions to the distribution folder [frontend/nextjs/package.json:21]() |

### Library Bundling (Rollup)
The project uses Rollup to package the frontend as a reusable NPM library (`gpt-researcher-ui`).
- **PostCSS/Tailwind**: Injects CSS directly into the JS bundle [frontend/nextjs/rollup.config.js:34-42]().
- **Babel**: Transpiles TypeScript and React code with specific presets [frontend/nextjs/rollup.config.js:57-70]().
- **External Dependencies**: Excludes `react`, `next`, and Node.js built-ins like `fs` or `path` to prevent bundling conflicts [frontend/nextjs/rollup.config.js:73-83]().

Sources: [frontend/nextjs/package.json:1-23](), [frontend/nextjs/rollup.config.js:19-84]()

## Styling and Theming

The application uses Tailwind CSS for layout and styling, with global styles defined in `globals.css`.

### Visual Elements
- **Background Orbs**: Fixed position blurred orbs created using CSS `::before` and `::after` pseudo-elements on the `body` [frontend/nextjs/app/globals.css:57-81]().
- **Animations**: Custom keyframes for `gradientBG`, `float`, and `loader` (loading dots) [frontend/nextjs/app/globals.css:5-24](), [frontend/nextjs/app/globals.css:150-160]().
- **Sidebar**: Custom scrollbar and backdrop blur for history and navigation [frontend/nextjs/app/globals.css:182-221]().

Sources: [frontend/nextjs/app/globals.css:1-221](), [frontend/nextjs/components/Settings/Settings.css:42-49]()

## Data Processing Utilities

Before rendering, streamed data from the WebSocket is processed to ensure a clean UI state.

- **`preprocessOrderedData`**: Groups raw stream chunks into logical blocks like accordions or report sections [frontend/nextjs/src/GPTResearcher.tsx:225-235]().
- **Host Resolution**: The `getHost` helper determines the correct backend URL by checking `localStorage`, URL parameters (`GPTR_API_URL`), and environment variables (`NEXT_PUBLIC_GPTR_API_URL`) [frontend/nextjs/helpers/getHost.ts:5-26]().

Sources: [frontend/nextjs/src/GPTResearcher.tsx:225-240](), [frontend/nextjs/helpers/getHost.ts:1-28]()

---

# Page: Adding New LLM Providers

# Adding New LLM Providers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude/SKILL.md](.claude/SKILL.md)
- [.claude/references/adding-features.md](.claude/references/adding-features.md)
- [.claude/references/advanced-patterns.md](.claude/references/advanced-patterns.md)
- [.claude/references/api-reference.md](.claude/references/api-reference.md)
- [.claude/references/architecture.md](.claude/references/architecture.md)
- [.claude/references/components.md](.claude/references/components.md)
- [.claude/references/config-reference.md](.claude/references/config-reference.md)
- [.claude/references/deep-research.md](.claude/references/deep-research.md)
- [.claude/references/flows.md](.claude/references/flows.md)
- [.claude/references/mcp.md](.claude/references/mcp.md)
- [.claude/references/multi-agents.md](.claude/references/multi-agents.md)
- [docs/docs/gpt-researcher/llms/llms.md](docs/docs/gpt-researcher/llms/llms.md)
- [docs/docs/gpt-researcher/llms/supported-llms.md](docs/docs/gpt-researcher/llms/supported-llms.md)
- [gpt_researcher/llm_provider/generic/base.py](gpt_researcher/llm_provider/generic/base.py)
- [gpt_researcher/memory/embeddings.py](gpt_researcher/memory/embeddings.py)

</details>



This guide provides step-by-step instructions for extending GPT Researcher to support additional LLM providers. It covers the technical implementation details, required code modifications, and configuration patterns needed to integrate new language model providers into the system.

**Scope**: This page focuses specifically on adding new LLM providers to the `GenericLLMProvider` abstraction layer. For information about configuring existing providers, see [Supported Providers and Models](). For embedding provider integration, see [Embeddings and Memory System](). For overall LLM architecture concepts, see [LLM Provider Architecture]().

---

## LLM Provider Architecture Overview

The `GenericLLMProvider` class serves as the unified abstraction layer for all LLM providers. It provides a consistent interface regardless of which underlying provider is used, handling provider-specific initialization details and parameter transformations.

### LLM Integration Data Flow
Title: LLM Provider Integration Flow
```mermaid
graph TB
    Config["Config System<br/>gpt_researcher/config/config.py"]
    EnvVars["Environment Variables<br/>FAST_LLM, SMART_LLM<br/>STRATEGIC_LLM"]
    
    GenericProvider["GenericLLMProvider<br/>gpt_researcher/llm_provider/generic/base.py"]
    FromProvider["from_provider()<br/>classmethod"]
    CheckPkg["_check_pkg()<br/>Dynamic package loading"]
    
    SupportedSet["_SUPPORTED_PROVIDERS<br/>Set of provider names"]
    
    subgraph "Provider Implementations"
        OpenAI["OpenAI<br/>langchain_openai.ChatOpenAI"]
        Anthropic["Anthropic<br/>langchain_anthropic.ChatAnthropic"]
        Azure["AzureChatOpenAI"]
        Ollama["Ollama<br/>langchain_ollama.ChatOllama"]
        Others["30+ other providers"]
    end
    
    subgraph "Core Components"
        GPTResearcher["GPTResearcher<br/>gpt_researcher/agent.py"]
        ReportGen["ReportGenerator<br/>gpt_researcher/skills/writer.py"]
        MultiAgent["Multi-Agent System<br/>multi_agents/"]
    end
    
    Config --> EnvVars
    EnvVars --> GenericProvider
    GenericProvider --> FromProvider
    FromProvider --> CheckPkg
    FromProvider --> SupportedSet
    
    SupportedSet -.checks.-> FromProvider
    
    FromProvider --> OpenAI
    FromProvider --> Anthropic
    FromProvider --> Azure
    FromProvider --> Ollama
    FromProvider --> Others
    
    GenericProvider --> GPTResearcher
    GenericProvider --> ReportGen
    GenericProvider --> MultiAgent
```
Sources: [gpt_researcher/llm_provider/generic/base.py:13-39](), [gpt_researcher/llm_provider/generic/base.py:92-272](), [gpt_researcher/agent.py:17-50]()

---

## Prerequisites

Before adding a new provider, ensure:

1.  **LangChain Support**: Verify that LangChain has an integration package for your provider (e.g., `langchain-yourprovider`).
2.  **Chat Model Interface**: The provider must support chat-based interactions (not just completions).
3.  **Async Support**: The provider's LangChain integration must support `ainvoke` and `astream` methods [gpt_researcher/llm_provider/generic/base.py:275-307]().
4.  **API Access**: You have access to the provider's API and authentication credentials.

---

## Provider Registration Flow

### Dynamic Loading Sequence
Title: Provider Registration and Loading Sequence
```mermaid
sequenceDiagram
    participant User
    participant Config
    participant GenericLLMProvider
    participant CheckPkg
    participant LangChain
    participant Provider
    
    User->>Config: Set SMART_LLM="newprovider:model-name"
    Config->>GenericLLMProvider: from_provider("newprovider", model="model-name")
    GenericLLMProvider->>GenericLLMProvider: Check if "newprovider" in _SUPPORTED_PROVIDERS
    
    alt Provider supported
        GenericLLMProvider->>CheckPkg: _check_pkg("langchain_newprovider")
        
        alt Package not installed
            CheckPkg->>CheckPkg: subprocess.check_call(["pip", "install", "langchain-newprovider"])
            CheckPkg->>CheckPkg: importlib.import_module("langchain_newprovider")
        end
        
        GenericLLMProvider->>LangChain: Import ChatNewProvider
        GenericLLMProvider->>Provider: Instantiate ChatNewProvider(**kwargs)
        Provider-->>GenericLLMProvider: llm instance
        GenericLLMProvider-->>Config: GenericLLMProvider(llm)
    else Provider not supported
        GenericLLMProvider-->>User: ValueError: Unsupported provider
    end
```
Sources: [gpt_researcher/llm_provider/generic/base.py:122-272](), [gpt_researcher/llm_provider/generic/base.py:316-334]()

---

## Step-by-Step Implementation Guide

### Step 1: Add Provider to Supported Set

Add your provider name to the `_SUPPORTED_PROVIDERS` set in [gpt_researcher/llm_provider/generic/base.py:13-39]().

**Naming Convention**: Use lowercase with underscores for multi-word names (e.g., `azure_openai`, `google_genai`).

### Step 2: Implement Provider Case in `from_provider()`

Add a new `elif` block in the `from_provider` classmethod [gpt_researcher/llm_provider/generic/base.py:122-272]().

#### Pattern Variations:

*   **Standard Pattern**: Used for most native LangChain integrations like Anthropic [gpt_researcher/llm_provider/generic/base.py:132-136]().
*   **OpenAI-Compatible Pattern**: For providers using OpenAI-compatible endpoints like DeepSeek [gpt_researcher/llm_provider/generic/base.py:218-225]() or Dashscope [gpt_researcher/llm_provider/generic/base.py:207-211]().
*   **Parameter Mapping Pattern**: When a provider uses different parameter names (e.g., `model_id` instead of `model`), seen in HuggingFace [gpt_researcher/llm_provider/generic/base.py:186-193]() and Bedrock [gpt_researcher/llm_provider/generic/base.py:199-206]().
*   **Azure Pattern**: Specifically for Azure deployments where `model` maps to `azure_deployment` [gpt_researcher/llm_provider/generic/base.py:137-145]().

### Step 3: Handle Environment Variables

Your provider implementation should read API keys and configuration from environment variables within the `from_provider` logic. Common variables include `OPENAI_BASE_URL` [gpt_researcher/llm_provider/generic/base.py:128-129]() or `OLLAMA_BASE_URL` [gpt_researcher/llm_provider/generic/base.py:171]().

### Step 4: Configure Model-Specific Behavior

#### Temperature Handling
If your provider includes models that don't support the `temperature` parameter (like reasoning models), add them to `NO_SUPPORT_TEMPERATURE_MODELS` [gpt_researcher/llm_provider/generic/base.py:41-57]().

#### Reasoning Effort Parameter
For models that support reasoning effort levels (like o3-mini), add them to `SUPPORT_REASONING_EFFORT_MODELS` [gpt_researcher/llm_provider/generic/base.py:59-66](). The `ReasoningEfforts` enum [gpt_researcher/llm_provider/generic/base.py:68-71]() defines valid values: `high`, `medium`, and `low`.

### Step 5: Update Documentation

Add configuration examples to `docs/docs/gpt-researcher/llms/llms.md` [docs/docs/gpt-researcher/llms/llms.md:1-184]() and update the supported list in `docs/docs/gpt-researcher/llms/supported-llms.md` [docs/docs/gpt-researcher/llms/supported-llms.md:1-26]().

---

## Dynamic Package Loading System

Title: Dynamic Package Installation Logic in _check_pkg
```mermaid
flowchart TD
    Start["from_provider() called"]
    CheckPkg["_check_pkg('langchain_provider')"]
    FindSpec["importlib.util.find_spec()"]
    
    IsInstalled{Package<br/>installed?}
    
    Install["subprocess.check_call()<br/>pip install langchain-provider"]
    ImportModule["importlib.import_module()"]
    Success["Package available"]
    Error["ImportError:<br/>Installation failed"]
    
    Start --> CheckPkg
    CheckPkg --> FindSpec
    FindSpec --> IsInstalled
    
    IsInstalled -->|Yes| Success
    IsInstalled -->|No| Install
    
    Install -->|Success| ImportModule
    Install -->|Failure| Error
    
    ImportModule --> Success
```
Sources: [gpt_researcher/llm_provider/generic/base.py:316-334]()

The `_check_pkg()` function automatically handles package installation:
1.  Checks if package exists using `importlib.util.find_spec()` [gpt_researcher/llm_provider/generic/base.py:318]().
2.  Auto-installs missing packages via pip using `subprocess.check_call` [gpt_researcher/llm_provider/generic/base.py:326]().
3.  Converts underscore names to kebab-case for the pip command [gpt_researcher/llm_provider/generic/base.py:323]().
4.  Provides colored terminal output using `colorama` [gpt_researcher/llm_provider/generic/base.py:321-322]().

---

## Embedding Provider Extension

For providers that also offer embedding models, follow a parallel pattern in `Memory.__init__` [gpt_researcher/memory/embeddings.py:87-202]().

| Provider | LangChain Class | Key Parameters |
| :--- | :--- | :--- |
| OpenAI | `OpenAIEmbeddings` | `model`, `openai_api_base` [gpt_researcher/memory/embeddings.py:100-107]() |
| Azure | `AzureOpenAIEmbeddings` | `azure_endpoint`, `openai_api_version` [gpt_researcher/memory/embeddings.py:108-120]() |
| Ollama | `OllamaEmbeddings` | `base_url`, `model` [gpt_researcher/memory/embeddings.py:143-150]() |
| Custom | `OpenAIEmbeddings` | `openai_api_base` (e.g. LMStudio) [gpt_researcher/memory/embeddings.py:88-99]() |

Sources: [gpt_researcher/memory/embeddings.py:87-202]()

---

## Troubleshooting Checklist

*   **Unsupported Provider**: Ensure the string is in `_SUPPORTED_PROVIDERS` [gpt_researcher/llm_provider/generic/base.py:13-39]().
*   **Installation Failures**: Verify the kebab-case mapping in `_check_pkg` [gpt_researcher/llm_provider/generic/base.py:316-334]().
*   **Temperature Errors**: Add reasoning-only models to `NO_SUPPORT_TEMPERATURE_MODELS` [gpt_researcher/llm_provider/generic/base.py:41-57]().
*   **Missing API Keys**: Ensure environment variables are correctly accessed via `os.environ` or `os.getenv` [gpt_researcher/llm_provider/generic/base.py:128-129](), [gpt_researcher/memory/embeddings.py:94-95]().

Sources: [gpt_researcher/llm_provider/generic/base.py:1-335](), [gpt_researcher/memory/embeddings.py:1-202]()

---

# Page: Adding New Retrievers

# Adding New Retrievers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude/SKILL.md](.claude/SKILL.md)
- [.claude/references/adding-features.md](.claude/references/adding-features.md)
- [.claude/references/advanced-patterns.md](.claude/references/advanced-patterns.md)
- [.claude/references/api-reference.md](.claude/references/api-reference.md)
- [.claude/references/architecture.md](.claude/references/architecture.md)
- [.claude/references/components.md](.claude/references/components.md)
- [.claude/references/config-reference.md](.claude/references/config-reference.md)
- [.claude/references/deep-research.md](.claude/references/deep-research.md)
- [.claude/references/flows.md](.claude/references/flows.md)
- [.claude/references/mcp.md](.claude/references/mcp.md)
- [.claude/references/multi-agents.md](.claude/references/multi-agents.md)
- [.env.example](.env.example)
- [gpt_researcher/actions/retriever.py](gpt_researcher/actions/retriever.py)
- [gpt_researcher/retrievers/__init__.py](gpt_researcher/retrievers/__init__.py)
- [gpt_researcher/retrievers/bing/__init__.py](gpt_researcher/retrievers/bing/__init__.py)
- [gpt_researcher/retrievers/bing/bing.py](gpt_researcher/retrievers/bing/bing.py)
- [gpt_researcher/retrievers/google/google.py](gpt_researcher/retrievers/google/google.py)
- [gpt_researcher/retrievers/openalex/__init__.py](gpt_researcher/retrievers/openalex/__init__.py)
- [gpt_researcher/retrievers/openalex/openalex.py](gpt_researcher/retrievers/openalex/openalex.py)
- [gpt_researcher/retrievers/searchapi/searchapi.py](gpt_researcher/retrievers/searchapi/searchapi.py)
- [gpt_researcher/retrievers/searx/searx.py](gpt_researcher/retrievers/searx/searx.py)
- [gpt_researcher/retrievers/serpapi/serpapi.py](gpt_researcher/retrievers/serpapi/serpapi.py)
- [gpt_researcher/retrievers/serper/serper.py](gpt_researcher/retrievers/serper/serper.py)
- [gpt_researcher/retrievers/tavily/tavily_search.py](gpt_researcher/retrievers/tavily/tavily_search.py)
- [gpt_researcher/retrievers/utils.py](gpt_researcher/retrievers/utils.py)
- [gpt_researcher/retrievers/xquik/__init__.py](gpt_researcher/retrievers/xquik/__init__.py)
- [gpt_researcher/retrievers/xquik/xquik.py](gpt_researcher/retrievers/xquik/xquik.py)

</details>



## Purpose and Scope

This document provides a comprehensive guide for developers who want to add support for new web search retrievers to GPT Researcher. A retriever is responsible for fetching search results from external APIs or services (e.g., Google, Bing, Tavily, arXiv, or OpenAlex).

For information about the overall data source architecture, see [Data Sources and Retrieval](). For details on configuring existing retrievers, see [Configuration Parameters Reference]().

---

## Retriever Architecture Overview

The retriever system in GPT Researcher uses a factory pattern to support multiple search providers. Each retriever is a self-contained class that implements a standard interface for querying search APIs and returning structured results.

### System Context

```mermaid
graph TB
    subgraph "Research Pipeline"
        RC["gpt_researcher.skills.researcher.ResearchConductor"]
        QP["gpt_researcher.actions.query_processing.get_search_results"]
    end
    
    subgraph "Retriever Factory"
        GR["get_retriever(name)<br/>gpt_researcher/actions/retriever.py"]
        GetRetrievers["get_retrievers(headers, cfg)<br/>gpt_researcher/actions/retriever.py"]
    end
    
    subgraph "Retriever Implementations"
        Tavily["TavilySearch"]
        Google["GoogleSearch"]
        Bing["BingSearch"]
        DuckDuckGo["Duckduckgo"]
        Xquik["XquikSearch"]
        OpenAlex["OpenAlexSearch"]
        MCP["MCPRetriever"]
        NewRetriever["YourNewRetriever"]
    end
    
    subgraph "Configuration"
        Cfg["Config.retriever<br/>Config.retrievers"]
        Headers["headers['retriever']"]
    end
    
    RC -->|"plan_research"| QP
    RC -->|"_search_relevant_source_urls"| GetRetrievers
    
    QP --> GetRetrievers
    GetRetrievers --> GR
    
    GR -->|"match 'tavily'"| Tavily
    GR -->|"match 'google'"| Google
    GR -->|"match 'bing'"| Bing
    GR -->|"match 'duckduckgo'"| DuckDuckGo
    GR -->|"match 'xquik'"| Xquik
    GR -->|"match 'openalex'"| OpenAlex
    GR -->|"match 'mcp'"| MCP
    GR -->|"match 'yournew'"| NewRetriever
    
    Cfg --> GetRetrievers
    Headers --> GetRetrievers
```

**Sources:** [gpt_researcher/actions/retriever.py:8-106](), [gpt_researcher/retrievers/__init__.py:1-37]()

---

## Retriever Interface Requirements

All retrievers must implement a consistent interface to work with the GPT Researcher system. The interface consists of a constructor and a `search()` method.

### Required Constructor Signature

While specific implementations vary slightly (e.g., `BingSearch` takes fewer arguments), the standard expected by the factory is:

```python
def __init__(self, query: str, headers: dict = None, topic: str = "general", query_domains: list = None):
```

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | `str` | Yes | The search query string |
| `headers` | `dict` | No | Additional headers (may contain API keys) |
| `topic` | `str` | No | Topic category (e.g., "general", "news") |
| `query_domains` | `list` | No | List of domains to restrict search to |

### Required Search Method

```python
def search(self, max_results: int = 10) -> list[dict]:
```

**Returns:** A list of dictionaries, each containing:
- `"href"`: URL of the search result (string)
- `"body"`: Content snippet or description (string)
- `"title"`: (Optional) Title of the search result (string)

**Example Return Value:**
```python
[
    {"href": "https://example.com/article1", "body": "This article discusses...", "title": "Article 1"},
    {"href": "https://example.com/article2", "body": "An overview of...", "title": "Article 2"}
]
```

**Sources:** [gpt_researcher/retrievers/tavily/tavily_search.py:19-28](), [gpt_researcher/retrievers/google/google.py:13-21](), [gpt_researcher/retrievers/tavily/tavily_search.py:100-125]()

---

## Implementation Steps

### Step 1: Create Retriever Module

Create a new directory under `gpt_researcher/retrievers/` for your retriever:

```
gpt_researcher/retrievers/
├── your_retriever/
│   ├── __init__.py
│   └── your_retriever.py
```

### Step 2: Implement the Retriever Class

Implement your logic for calling the external API. Refer to `GoogleSearch` or `BingSearch` for examples of `requests`-based implementations.

```python
# Example logic based on gpt_researcher/retrievers/bing/bing.py
class YourNewSearch():
    def __init__(self, query, query_domains=None):
        self.query = query
        self.query_domains = query_domains or None
        self.api_key = self.get_api_key()

    def get_api_key(self):
        return os.environ.get("YOUR_API_KEY")

    def search(self, max_results=7) -> list[dict]:
        # ... API call logic using requests.get ...
        # Normalization to href/body format
        return [{"href": r["url"], "body": r["snippet"], "title": r["name"]} for r in results]
```

**Sources:** [gpt_researcher/retrievers/bing/bing.py:10-95](), [gpt_researcher/retrievers/google/google.py:9-100]()

### Step 3: Create `__init__.py`

Export your retriever class from the module so it can be imported by the central `retrievers` package.

---

## Registration Process

### 1. Update the Main Retrievers Package
Add your new retriever to `gpt_researcher/retrievers/__init__.py` and include it in the `__all__` list.

**Sources:** [gpt_researcher/retrievers/__init__.py:1-37]()

### 2. Add to Retriever Factory
Edit `gpt_researcher/actions/retriever.py` and add a new case to the `match retriever` block in the `get_retriever()` function to map a string name to your class.

```python
# gpt_researcher/actions/retriever.py
case "your_retriever":
    from gpt_researcher.retrievers import YourNewSearch
    return YourNewSearch
```

**Sources:** [gpt_researcher/actions/retriever.py:35-103]()

### 3. Update Valid Retrievers List
Add your retriever name to the `VALID_RETRIEVERS` list in `gpt_researcher/retrievers/utils.py`. This ensures the system recognizes it as a valid option during validation or fallback.

**Sources:** [gpt_researcher/retrievers/utils.py:62-80]()

---

## Configuration and Usage

### Retriever Selection Flow

The system determines which retrievers to use by checking headers, then configuration, and finally falling back to a default (Tavily).

```mermaid
graph TD
    subgraph "Selection Logic [gpt_researcher/actions/retriever.py]"
        Start["get_retrievers(headers, cfg)"]
        H_Mult{"headers['retrievers']?"}
        H_Sing{"headers['retriever']?"}
        C_Mult{"cfg.retrievers?"}
        C_Sing{"cfg.retriever?"}
        Default["get_default_retriever()"]
    end

    subgraph "Class Resolution"
        Lookup["get_retriever(name)"]
        Fallback["Use Default if name invalid"]
    end

    Start --> H_Mult
    H_Mult -- "Yes" --> Lookup
    H_Mult -- "No" --> H_Sing
    H_Sing -- "Yes" --> Lookup
    H_Sing -- "No" --> C_Mult
    C_Mult -- "Yes" --> Lookup
    C_Mult -- "No" --> C_Sing
    C_Sing -- "Yes" --> Lookup
    C_Sing -- "No" --> Default
    Lookup --> Fallback
```

**Sources:** [gpt_researcher/actions/retriever.py:109-146]()

### API Key Management
Retrievers typically fetch their API keys from the `headers` dictionary passed during initialization or from environment variables.

- **Google Example:** Checks `self.headers.get("google_api_key")` then `os.environ["GOOGLE_API_KEY"]`. [gpt_researcher/retrievers/google/google.py:22-37]()
- **Tavily Example:** Checks `self.headers.get("tavily_api_key")` then `os.environ["TAVILY_API_KEY"]`. [gpt_researcher/retrievers/tavily/tavily_search.py:45-54]()
- **OpenAlex Example:** Directly accesses `os.environ.get("OPENALEX_API_KEY")`. [gpt_researcher/retrievers/openalex/openalex.py:41-42]()

---

## Integration Points

### Data Flow from Code to Search

The following diagram bridges the high-level search requirement to the specific code entities involved in the retrieval process.

```mermaid
graph LR
    subgraph "Natural Language Space"
        Query["'Impact of AI on Healthcare'"]
    end

    subgraph "Code Entity Space"
        RC["gpt_researcher.GPTResearcher"]
        Factory["gpt_researcher.actions.retriever.get_retrievers"]
        Provider["gpt_researcher.retrievers.google.GoogleSearch"]
    end

    Query --> RC
    RC --> Factory
    Factory --> Provider
    Provider -->|"search()"| Results["[{'href': '...', 'body': '...'}]"]
```

**Sources:** [gpt_researcher/actions/retriever.py:109-146](), [gpt_researcher/retrievers/google/google.py:53-100]()

---

## Special Considerations

- **Package Dependencies:** Use the `check_pkg(pkg)` utility in `gpt_researcher/retrievers/utils.py` if your retriever requires an external library that isn't a core dependency. [gpt_researcher/retrievers/utils.py:44-59]()
- **Default Retriever:** The system currently defaults to `TavilySearch`. [gpt_researcher/actions/retriever.py:149-156]()
- **Dynamic Discovery:** The `get_all_retriever_names()` function in `utils.py` attempts to list all directories in the `retrievers` folder to dynamically identify available providers. [gpt_researcher/retrievers/utils.py:82-101]()
- **Domain Filtering:** If your search provider supports it, implement `query_domains` handling within the `search` method to restrict results to specific sites. [gpt_researcher/retrievers/google/google.py:59-63](), [gpt_researcher/retrievers/serper/serper.py:83-87]()

---

# Page: AI-Assisted Development

# AI-Assisted Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.claude/SKILL.md](.claude/SKILL.md)
- [.claude/references/adding-features.md](.claude/references/adding-features.md)
- [.claude/references/advanced-patterns.md](.claude/references/advanced-patterns.md)
- [.claude/references/api-reference.md](.claude/references/api-reference.md)
- [.claude/references/architecture.md](.claude/references/architecture.md)
- [.claude/references/components.md](.claude/references/components.md)
- [.claude/references/config-reference.md](.claude/references/config-reference.md)
- [.claude/references/deep-research.md](.claude/references/deep-research.md)
- [.claude/references/flows.md](.claude/references/flows.md)
- [.claude/references/mcp.md](.claude/references/mcp.md)
- [.claude/references/multi-agents.md](.claude/references/multi-agents.md)
- [.codex-plugin/plugin.json](.codex-plugin/plugin.json)
- [.cursorrules](.cursorrules)
- [.github/workflows/plugin-quality-gate.yml](.github/workflows/plugin-quality-gate.yml)
- [.gitignore](.gitignore)
- [.mcp.json](.mcp.json)
- [CURSOR_RULES.md](CURSOR_RULES.md)
- [skills/gpt-researcher/SKILL.md](skills/gpt-researcher/SKILL.md)

</details>



## Purpose and Scope

This document details GPT Researcher's AI-assisted development infrastructure, specifically the skills system and configuration rules that enable AI assistants like Claude and Cursor to understand, navigate, and contribute to the codebase. The project utilizes a structured `.claude/skills/` directory and a comprehensive `CURSOR_RULES.md` file to provide architectural context, component interactions, and development patterns. This allows AI assistants to implement features following established conventions such as the "8-Step Feature Pattern."

For information about the general project structure, see [Project Structure and Dependencies](#12.1). For frontend-specific development, see [Frontend Development](#12.2).

## AI Skill Infrastructure

The repository contains specialized configuration files that bridge the gap between natural language requirements and the internal code entity space. These include Model Context Protocol (MCP) definitions and skill sets for AI plugins.

### Skills Directory (.claude/skills/ and skills/)

The project maintains two distinct skill directories for different AI integrations:

| Directory | Purpose | Key Content |
|-----------|---------|-------------|
| `.claude/skills/` | Development Knowledge Base | Contains `SKILL.md` and deep references for AI agents helping developers. [.claude/SKILL.md:1-225]() |
| `skills/gpt-researcher/` | Codex/MCP Integration | Defines the `gpt-researcher` skill for use via MCP in Codex workflows. [skills/gpt-researcher/SKILL.md:1-13]() |

The `.claude/skills/` directory serves as a high-level knowledge base for AI agents:
* `SKILL.md`: Defines the planner-executor-publisher pattern and core class roles. [.claude/SKILL.md:8-10]()
* `references/adding-features.md`: Documents the "8-Step Pattern" for system extension. [.claude/references/adding-features.md:10-20]()
* `references/components.md`: Lists critical method signatures for `GPTResearcher` and `ResearchConductor`. [.claude/references/components.md:10-158]()

**Sources:** [.claude/SKILL.md:1-225](), [skills/gpt-researcher/SKILL.md:1-13](), [.claude/references/adding-features.md:1-20](), [.claude/references/components.md:1-158]()

### Codex and MCP Configuration

The project is configured as a Codex plugin, allowing AI assistants to invoke research capabilities directly through the Model Context Protocol (MCP).

* **Plugin Definition**: The `.codex-plugin/plugin.json` file identifies the repository as an autonomous research agent. [.codex-plugin/plugin.json:1-24]()
* **MCP Server**: The `.mcp.json` file defines the `gpt-researcher` server, which is executed via `uvx`. [.mcp.json:1-10]()
* **Quality Control**: A GitHub Action (`.github/workflows/plugin-quality-gate.yml`) ensures that changes to skills or MCP configs meet a minimum quality score. [.github/workflows/plugin-quality-gate.yml:1-21]()

**Sources:** [.codex-plugin/plugin.json:1-24](), [.mcp.json:1-10](), [.github/workflows/plugin-quality-gate.yml:1-21]()

### Cursor Rules (.cursorrules & CURSOR_RULES.md)

The `.cursorrules` file (and its readable copy `CURSOR_RULES.md`) defines the "Natural Language to Code" mapping for the Cursor AI editor. It enforces strict development guidelines and provides a lexicon for agent roles.

**Mapping Natural Language to Code Entities**

```mermaid
graph TD
    subgraph "Natural Language Space (User Intent)"
        UI_Req["'Add a new search engine'"]
        UI_Rep["'Change report tone'"]
        UI_Agent["'Modify agent behavior'"]
    end

    subgraph "Code Entity Space (Implementation)"
        Retriever["gpt_researcher/retrievers/"]
        Actions["gpt_researcher/actions/retriever.py"]
        Config["gpt_researcher/config/config.py"]
        Prompts["gpt_researcher/prompts.py"]
        MultiAgent["backend/multi_agents/agents/"]
    end

    UI_Req -->|Guided by Cursor Rule| Retriever
    UI_Req -->|Guided by Cursor Rule| Actions
    UI_Rep -->|Guided by Cursor Rule| Config
    UI_Rep -->|Guided by Cursor Rule| Prompts
    UI_Agent -->|Guided by Cursor Rule| MultiAgent
```

**Sources:** [.cursorrules:1-150](), [CURSOR_RULES.md:1-181]()

## Core Development Patterns

The AI-assisted workflow is built around specific code patterns that AI agents are instructed to follow.

### The 8-Step Feature Pattern
To ensure consistency, new features follow a rigid path documented in the AI skills:
1. **Config**: Update `gpt_researcher/config/variables/default.py`. [.claude/references/adding-features.md:24-32]()
2. **Provider**: Create in `gpt_researcher/llm_provider/`. [.claude/references/adding-features.md:45-59]()
3. **Skill**: Create in `gpt_researcher/skills/`. [.claude/references/adding-features.md:65-86]()
4. **Agent**: Integrate in `gpt_researcher/agent.py`. [.claude/references/adding-features.md:92-107]()
5. **Prompts**: Update `gpt_researcher/prompts.py`. [.claude/references/adding-features.md:111-117]()
6. **WebSocket**: Add events via `stream_output()`. [.claude/references/adding-features.md:119-121]()
7. **Frontend**: Update `useWebSocket.ts`. [.claude/references/adding-features.md:125-131]()
8. **Docs**: Update documentation. [.claude/references/adding-features.md:133-135]()

**Sources:** [.claude/references/adding-features.md:10-135](), [.claude/SKILL.md:86-97]()

### Research Orchestration Flow

AI assistants are trained to understand the internal method calls that drive the research process.

**Research Execution Path**

```mermaid
sequenceDiagram
    participant U as User Query
    participant G as "GPTResearcher (gpt_researcher/agent.py)"
    participant RC as "ResearchConductor (gpt_researcher/skills/researcher.py)"
    participant RM as "BrowserManager (gpt_researcher/skills/browser.py)"
    participant RG as "ReportGenerator (gpt_researcher/skills/writer.py)"

    U->>G: __init__(query, report_type)
    G->>G: choose_agent() [actions/agent_creator.py]
    G->>RC: conduct_research()
    RC->>RC: plan_research()
    loop For each sub_query
        RC->>RM: _scrape_data_by_urls()
        RM-->>RC: scraped_data
        RC->>RC: _process_sub_query()
    end
    RC-->>G: context
    G->>RG: write_report(context)
    RG-->>G: Markdown Report
```

**Sources:** [.claude/references/components.md:55-156](), [.claude/SKILL.md:58-78]()

## Critical Development Guidelines

AI assistants are restricted by several "Critical Gotchas" to prevent common architectural errors:

*   **Case Sensitivity**: Configuration keys are lowercased when accessed (e.g., `SMART_LLM` in env becomes `self.cfg.smart_llm` in code). [.claude/SKILL.md:125-130]()
*   **Async/Await**: All research methods must be `async`. [.claude/SKILL.md:205-205]()
*   **Graceful Degradation**: Skills must use try-except blocks to stream errors via `stream_output` instead of crashing. [.claude/references/advanced-patterns.md:107-119]()
*   **Retriever Registration**: New retrievers must be registered in the `match` statement within `gpt_researcher/actions/retriever.py`. [.claude/SKILL.md:111-115]()

**Sources:** [.claude/SKILL.md:180-210](), [.claude/references/advanced-patterns.md:101-119]()

## AI-Assisted Contribution Workflow

Developers can use the following workflow to leverage these AI skills:

1.  **Context Loading**: When opening the project in Cursor or Claude, the `.cursorrules` and `.claude/skills/` are automatically indexed. [.cursorrules:1-5]()
2.  **Feature Request**: Prompt the AI using the defined lexicon (e.g., "Add a new specialized Agent Role for legal research"). [CURSOR_RULES.md:165-172]()
3.  **Validation**: The AI validates changes against the "Rule Violation Monitoring" section, which flags unauthorized library additions or TypeScript strict mode violations. [.cursorrules:126-134]()
4.  **Testing**: AI is instructed to run `python -m pytest` or `npm run test` after implementation. [CURSOR_RULES.md:145-155]()

**Sources:** [.cursorrules:126-155](), [CURSOR_RULES.md:165-172]()

---

# Page: API Reference

# API Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/chat/chat.py](backend/chat/chat.py)
- [backend/run_server.py](backend/run_server.py)
- [backend/server/agent_discovery.py](backend/server/agent_discovery.py)
- [backend/server/app.py](backend/server/app.py)
- [backend/server/report_store.py](backend/server/report_store.py)
- [gpt_researcher/agent.py](gpt_researcher/agent.py)
- [gpt_researcher/skills/browser.py](gpt_researcher/skills/browser.py)
- [gpt_researcher/skills/researcher.py](gpt_researcher/skills/researcher.py)
- [tests/test_agent_discovery.py](tests/test_agent_discovery.py)

</details>



This page provides complete programmatic API documentation for GPT Researcher, covering the main `GPTResearcher` class, WebSocket protocol specifications, REST API endpoints, and configuration schemas. This documentation is intended for developers integrating GPT Researcher into applications, building custom frontends, or extending the system.

The API Reference is organized into five sections:
- **13.1 GPTResearcher Class API**: Python class interface for direct integration. For details, see [GPTResearcher Class API](#13.1).
- **13.2 WebSocket Protocol Reference**: Real-time bidirectional communication protocol. For details, see [WebSocket Protocol Reference](#13.2).
- **13.3 Configuration Schema**: Complete configuration parameter reference. For details, see [Configuration Schema](#13.3).
- **13.4 REST API Reference**: HTTP endpoints for mobile and restricted environments. For details, see [REST API Reference](#13.4).
- **13.5 Multi-Agent Task Configuration Schema**: Reference for task.json schema in multi-agent mode. For details, see [Multi-Agent Task Configuration Schema](#13.5).

---

## 13.1 GPTResearcher Class API

The `GPTResearcher` class is the primary orchestrator for conducting research programmatically. It manages the entire research pipeline by coordinating specialized "skills" such as the `ResearchConductor`, `ReportGenerator`, and `ContextManager`.

### Initialization Parameters
The constructor [gpt_researcher/agent.py:52-136]() accepts a wide range of parameters to customize the research behavior, including `query`, `report_type`, `report_source`, and integration settings for LangChain or MCP. It also supports `mcp_configs` for connecting to external Model Context Protocol servers [gpt_researcher/agent.py:113-131]().

### Core Methods
- `conduct_research()`: Starts the research process, gathering context from the configured sources [gpt_researcher/agent.py:290-331]().
- `write_report()`: Generates the final report based on gathered context [gpt_researcher/agent.py:373-389]().
- `get_subtopics()`: Retrieves subtopics for detailed research modes [gpt_researcher/agent.py:406-407]().

### Skill-Based Architecture
The class initializes several internal managers to handle specific tasks:
- `self.context_manager`: Handles context retrieval and compression [gpt_researcher/agent.py:186-186]().
- `self.browser_manager`: Manages web scraping and image selection [gpt_researcher/agent.py:185-185]().
- `self.researcher`: An instance of `ResearchConductor` that manages the search and planning workflow [gpt_researcher/agent.py:190-190]().

For a full method reference and usage examples, see [GPTResearcher Class API](#13.1).

**Sources:** [gpt_researcher/agent.py:36-136](), [gpt_researcher/agent.py:180-195](), [gpt_researcher/skills/researcher.py:21-47]()

---

## 13.2 WebSocket Protocol Reference

GPT Researcher uses WebSockets for real-time streaming of research logs, costs, and images to the frontend. The `WebSocketManager` [backend/server/app.py:133-133]() handles these connections in the FastAPI application.

### Communication Flow
1. **Client Sends**: A JSON payload containing research parameters like `task`, `report_type`, and `report_source` [backend/server/app.py:53-62]().
2. **Server Streams**: Messages of type `"logs"`, `"images"`, or `"cost"` using the `stream_output` utility [gpt_researcher/actions/utils.py:7-33]().
3. **Completion**: The server sends the final report and links to generated files such as PDF or DOCX [backend/server/app.py:174-180]().

For the full message format and protocol details, see [WebSocket Protocol Reference](#13.2).

**Sources:** [backend/server/app.py:133-135](), [gpt_researcher/actions/utils.py:7-33](), [gpt_researcher/skills/researcher.py:55-60]()

---

## 13.3 Configuration Schema

The system is configured via a `Config` object [gpt_researcher/agent.py:140-141]() that parses environment variables and local files.

### Key Configuration Areas
- **LLM Selection**: Defines `FAST_LLM`, `SMART_LLM`, and `STRATEGIC_LLM` providers and models.
- **Retriever Settings**: Configures which search engines (Tavily, Google, etc.) to use via `get_retrievers` [gpt_researcher/agent.py:16-17]().
- **Scraping**: Controls the `WorkerPool` size and rate limits for the `BrowserManager` [gpt_researcher/skills/browser.py:32-35]().
- **MCP**: Defines Model Context Protocol execution strategies such as `"fast"`, `"deep"`, or `"disabled"` [gpt_researcher/agent.py:132-135]().

For a complete list of parameters and their defaults, see [Configuration Schema](#13.3).

**Sources:** [gpt_researcher/agent.py:140-145](), [gpt_researcher/skills/browser.py:32-35](), [backend/chat/chat.py:65-65]()

---

## 13.4 REST API Reference

The FastAPI server in `backend/server/app.py` exposes several REST endpoints for non-streaming interactions, report management, and agent discovery.

### Primary Endpoints
- `GET /api/reports`: Lists available research reports from the `ReportStore` [backend/server/app.py:183-187]().
- `GET /report/{research_id}`: Downloads a generated report file [backend/server/app.py:174-179]().
- `POST /api/reports`: Creates or updates a report entry [backend/server/app.py:198-202]().
- `GET /.well-known/agent-discovery.json`: Advertises services via the Agent Discovery Protocol [backend/server/app.py:162-172]().

For endpoint specifications and request/response models, see [REST API Reference](#13.4).

**Sources:** [backend/server/app.py:147-210](), [backend/server/agent_discovery.py:12-68](), [backend/server/report_store.py:32-37]()

---

## 13.5 Multi-Agent Task Configuration Schema

When running in multi-agent mode, tasks are orchestrated by the `ChiefEditorAgent`. The execution is triggered via the `execute_multi_agents` utility [backend/server/app.py:28-28](). This mode uses a `task.json` schema to define the scope and agents involved.

For the multi-agent state definitions and task configuration options, see [Multi-Agent Task Configuration Schema](#13.5).

**Sources:** [backend/server/app.py:25-30]()

---

## System Integration Diagram

The following diagram illustrates how the API layers interact with the core research logic.

```mermaid
graph TD
    subgraph "External Interface Space"
        REST["FastAPI App<br/>backend/server/app.py"]
        WSM["WebSocketManager<br/>backend/server/websocket_manager.py"]
        Discovery["Agent Discovery<br/>backend/server/agent_discovery.py"]
    end

    subgraph "Orchestration Space"
        GR["GPTResearcher Class<br/>gpt_researcher/agent.py"]
        Chat["ChatAgentWithMemory<br/>backend/chat/chat.py"]
        RS["ReportStore<br/>backend/server/report_store.py"]
    end

    subgraph "Skill & Execution Space"
        RC["ResearchConductor<br/>gpt_researcher/skills/researcher.py"]
        RG["ReportGenerator<br/>gpt_researcher/skills/writer.py"]
        BM["BrowserManager<br/>gpt_researcher/skills/browser.py"]
    end

    REST --> Chat
    REST --> Discovery
    REST --> RS
    WSM --> GR
    GR --> RC
    GR --> RG
    RC --> BM
    Chat --> RS
```
**Sources:** [backend/server/app.py:133-135](), [gpt_researcher/agent.py:24-30](), [backend/chat/chat.py:55-68](), [backend/server/report_store.py:7-9]()

## Research Entity Mapping

This diagram maps Natural Language concepts to the specific Code Entities that implement them within the API.

```mermaid
graph LR
    subgraph "Natural Language Space"
        Planning["'Plan Research'"]
        Scraping["'Web Scraping'"]
        Writing["'Generate Report'"]
        Chatting["'Follow-up Chat'"]
    end

    subgraph "Code Entity Space"
        plan_research["ResearchConductor.plan_research()<br/>gpt_researcher/skills/researcher.py"]
        browse_urls["BrowserManager.browse_urls()<br/>gpt_researcher/skills/browser.py"]
        write_report["ReportGenerator.write_report()<br/>gpt_researcher/skills/writer.py"]
        process_chat["ChatAgentWithMemory.chat()<br/>backend/chat/chat.py"]
    end

    Planning --- plan_research
    Scraping --- browse_urls
    Writing --- write_report
    Chatting --- process_chat
```
**Sources:** [gpt_researcher/skills/researcher.py:48-54](), [gpt_researcher/skills/browser.py:37-46](), [backend/chat/chat.py:187-195](), [gpt_researcher/agent.py:373-380]()

---

# Page: GPTResearcher Class API

# GPTResearcher Class API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [gpt_researcher/agent.py](gpt_researcher/agent.py)
- [gpt_researcher/config/config.py](gpt_researcher/config/config.py)
- [gpt_researcher/llm_provider/__init__.py](gpt_researcher/llm_provider/__init__.py)
- [gpt_researcher/skills/browser.py](gpt_researcher/skills/browser.py)
- [gpt_researcher/skills/researcher.py](gpt_researcher/skills/researcher.py)
- [gpt_researcher/utils/llm.py](gpt_researcher/utils/llm.py)

</details>



This document provides a complete API reference for the `GPTResearcher` class, the main entry point for conducting autonomous research. This is the central orchestrator class that coordinates all research activities, manages skill components, and generates reports.

For broader architectural context, see [Core Architecture](). For information about configuration parameters, see [Configuration Parameters Reference](). For details on specific skill managers, see [Skill Managers and Components]().

---

## Class Overview

The `GPTResearcher` class is the primary interface for conducting research tasks. It orchestrates the entire research pipeline including query planning, web searching, content scraping, context management, and report generation using LLMs.

**Location**: [gpt_researcher/agent.py:36-720]()

**Key Responsibilities**:
- Initialize and coordinate research workflow.
- Manage skill-based components (`ResearchConductor`, `ReportGenerator`, etc.).
- Configure LLM providers and embeddings via `Config`.
- Track API costs and manage research state.
- Provide interface for research execution and report generation.

Sources: [gpt_researcher/agent.py:36-50]()

---

## Architecture Diagram

```mermaid
graph TB
    GPTResearcher["GPTResearcher<br/>(gpt_researcher/agent.py:36)"]
    
    subgraph "Configuration & Infrastructure"
        Config["Config<br/>(gpt_researcher/config/config.py)"]
        Memory["Memory<br/>(gpt_researcher/memory.py)"]
        PromptFamily["PromptFamily<br/>(gpt_researcher/prompts.py)"]
        GenericLLMProvider["GenericLLMProvider<br/>(gpt_researcher/llm_provider/generic/base.py)"]
    end
    
    subgraph "Skill Components"
        ResearchConductor["ResearchConductor<br/>(gpt_researcher/skills/researcher.py)"]
        ReportGenerator["ReportGenerator<br/>(gpt_researcher/skills/writer.py)"]
        ContextManager["ContextManager<br/>(gpt_researcher/skills/context_manager.py)"]
        BrowserManager["BrowserManager<br/>(gpt_researcher/skills/browser.py)"]
        SourceCurator["SourceCurator<br/>(gpt_researcher/skills/curator.py)"]
        ImageGenerator["ImageGenerator<br/>(gpt_researcher/skills/image_generator.py)"]
        DeepResearchSkill["DeepResearchSkill<br/>(gpt_researcher/skills/deep_research.py)"]
    end
    
    subgraph "State & Data"
        context["context: list"]
        visited_urls["visited_urls: set"]
        research_sources["research_sources: list"]
        research_images["research_images: list"]
        research_costs["research_costs: float"]
    end
    
    GPTResearcher --> Config
    GPTResearcher --> Memory
    GPTResearcher --> PromptFamily
    GPTResearcher --> GenericLLMProvider
    
    GPTResearcher --> ResearchConductor
    GPTResearcher --> ReportGenerator
    GPTResearcher --> ContextManager
    GPTResearcher --> BrowserManager
    GPTResearcher --> SourceCurator
    GPTResearcher --> ImageGenerator
    GPTResearcher --> DeepResearchSkill
    
    GPTResearcher --> context
    GPTResearcher --> visited_urls
    GPTResearcher --> research_sources
    GPTResearcher --> research_images
    GPTResearcher --> research_costs
    
    ResearchConductor -.->|"uses"| BrowserManager
    ResearchConductor -.->|"uses"| ContextManager
    ReportGenerator -.->|"uses"| ImageGenerator
```

**Diagram: GPTResearcher Component Architecture**

This diagram shows how `GPTResearcher` coordinates multiple skill components and manages configuration, state, and data throughout the research workflow.

Sources: [gpt_researcher/agent.py:36-195](), [gpt_researcher/skills/researcher.py:21-47](), [gpt_researcher/skills/browser.py:14-36]()

---

## Initialization

### Constructor Signature

```python
def __init__(
    self,
    query: str,
    report_type: str = ReportType.ResearchReport.value,
    report_format: str = "markdown",
    report_source: str = ReportSource.Web.value,
    tone: Tone = Tone.Objective,
    source_urls: list[str] | None = None,
    document_urls: list[str] | None = None,
    complement_source_urls: bool = False,
    query_domains: list[str] | None = None,
    documents=None,
    vector_store=None,
    vector_store_filter=None,
    config_path=None,
    websocket=None,
    agent=None,
    role=None,
    parent_query: str = "",
    subtopics: list | None = None,
    visited_urls: set | None = None,
    verbose: bool = True,
    context=None,
    headers: dict | None = None,
    max_subtopics: int = 5,
    log_handler=None,
    prompt_family: str | None = None,
    mcp_configs: list[dict] | None = None,
    mcp_max_iterations: int | None = None,
    mcp_strategy: str | None = None,
    **kwargs
)
```

Sources: [gpt_researcher/agent.py:52-83]()

---

### Parameter Reference

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | `str` | *required* | The research query or question to investigate. |
| `report_type` | `str` | `"research_report"` | Type of report from `ReportType` enum. [gpt_researcher/utils/enum.py:17]() |
| `report_format` | `str` | `"markdown"` | Output format (markdown, pdf, docx). |
| `report_source` | `str` | `"web"` | Data source from `ReportSource` enum. [gpt_researcher/utils/enum.py:17]() |
| `tone` | `Tone` | `Tone.Objective` | Report tone from `Tone` enum. [gpt_researcher/utils/enum.py:31]() |
| `source_urls` | `list[str] \| None` | `None` | Specific URLs to use as sources. |
| `document_urls` | `list[str] \| None` | `None` | URLs of documents to process. |
| `complement_source_urls` | `bool` | `False` | Complement `source_urls` with web search. |
| `query_domains` | `list[str] \| None` | `None` | Domains to restrict search to. |
| `documents` | `Any` | `None` | LangChain document objects. |
| `vector_store` | `Any` | `None` | Vector store for document retrieval. |
| `vector_store_filter` | `dict \| None` | `None` | Filter for vector store queries. |
| `config_path` | `str \| None` | `None` | Path to configuration file. |
| `websocket` | `Any` | `None` | WebSocket for streaming output. |
| `agent` | `str \| None` | `None` | Pre-defined agent type. |
| `role` | `str \| None` | `None` | Pre-defined agent role. |
| `parent_query` | `str` | `""` | Parent query for subtopic reports. |
| `subtopics` | `list \| None` | `None` | List of subtopics to research. |
| `visited_urls` | `set \| None` | `None` | Set of already visited URLs. |
| `verbose` | `bool` | `True` | Enable verbose logging. |
| `context` | `list \| None` | `None` | Pre-loaded research context. |
| `headers` | `dict \| None` | `None` | Additional HTTP headers. |
| `max_subtopics` | `int` | `5` | Max number of subtopics to generate. |
| `log_handler` | `Any` | `None` | Handler for logging events. |
| `prompt_family` | `str \| None` | `None` | Family of prompts (e.g., `"granite"`). |
| `mcp_configs` | `list[dict] \| None` | `None` | MCP server configurations. |
| `mcp_strategy` | `str \| None` | `None` | MCP strategy: `"fast"`, `"deep"`, or `"disabled"`. |

Sources: [gpt_researcher/agent.py:87-136]()

---

## Core Research Methods

### `conduct_research()`

Executes the main research workflow including agent selection, query planning, web searching, and context gathering.

```python
async def conduct_research(self) -> list | str
```

**Workflow**:
1. Selects agent and role via `choose_agent` if not provided. [gpt_researcher/skills/researcher.py:119-127]()
2. Depending on `report_source`, it triggers the `ResearchConductor`. [gpt_researcher/skills/researcher.py:135-171]()
3. If using web search, it decomposes the query into sub-queries. [gpt_researcher/skills/researcher.py:48-87]()
4. Scrapes content via `BrowserManager`. [gpt_researcher/skills/browser.py:37-84]()
5. Compresses and retrieves relevant context via `ContextManager`.

Sources: [gpt_researcher/agent.py:328-395](), [gpt_researcher/skills/researcher.py:89-211]()

---

### `write_report()`

Generates a research report based on accumulated context.

```python
async def write_report(
    self,
    existing_headers: list = [],
    relevant_written_contents: list = [],
    ext_context=None,
    custom_prompt="",
    available_images: list = None
) -> str
```

**Parameters**:
- `existing_headers`: Headers to avoid duplication.
- `relevant_written_contents`: Previously written sections for context.
- `ext_context`: External context to override internal context.
- `available_images`: Images available for embedding.

Sources: [gpt_researcher/agent.py:445-485]()

---

### `quick_search()`

Performs a quick search without the full research workflow.

```python
async def quick_search(
    self,
    query: str,
    query_domains: list[str] = None,
    aggregated_summary: bool = False
) -> list[Any] | str
```

Sources: [gpt_researcher/agent.py:512-544]()

---

## Skill Manager Reference

### `ResearchConductor`
Manages query planning and the overall search workflow.
- `plan_research(query)`: Decomposes query into sub-tasks using `plan_research_outline`. [gpt_researcher/skills/researcher.py:48-87]()
- `conduct_research()`: Coordinates search across retrievers (Web, Local, Hybrid). [gpt_researcher/skills/researcher.py:89-211]()

### `BrowserManager`
Handles URL scraping and image selection.
- `browse_urls(urls)`: Scrapes content using `WorkerPool`. [gpt_researcher/skills/browser.py:37-84]()
- `select_top_images(images, k)`: Ranks and deduplicates images using `get_image_hash`. [gpt_researcher/skills/browser.py:86-115]()

### `ContextManager`
Handles semantic retrieval and context compression.
- `get_similar_content_by_query(query, pages)`: Uses `ContextCompressor`.
- `get_similar_written_contents_by_draft_section_titles(...)`: Finds related previously written sections.

### `ReportGenerator`
Handles the writing phase.
- `write_report(...)`: Generates the main report.
- `write_report_conclusion(content)`: Generates conclusion section.
- `write_introduction()`: Generates introduction section.

### `SourceCurator`
Ranks sources by credibility.
- `curate_sources(source_data, max_results)`: Uses LLM to rank and verify sources.

---

## Code Entity Mapping

```mermaid
graph LR
    subgraph "Logic & Skills"
        GPTResearcher["GPTResearcher Class<br/>(gpt_researcher/agent.py)"]
        ResearchConductor["ResearchConductor<br/>(gpt_researcher/skills/researcher.py)"]
        ReportGenerator["ReportGenerator<br/>(gpt_researcher/skills/writer.py)"]
        BrowserManager["BrowserManager<br/>(gpt_researcher/skills/browser.py)"]
    end

    subgraph "Actions & Utilities"
        scrape_urls["scrape_urls()<br/>(gpt_researcher/actions/web_scraping.py)"]
        create_chat_completion["create_chat_completion()<br/>(gpt_researcher/utils/llm.py)"]
        construct_subtopics["construct_subtopics()<br/>(gpt_researcher/utils/llm.py)"]
    end

    GPTResearcher --> ResearchConductor
    GPTResearcher --> ReportGenerator
    GPTResearcher --> BrowserManager
    
    BrowserManager --> scrape_urls
    ReportGenerator --> create_chat_completion
    ReportGenerator --> construct_subtopics
```

**Diagram: GPTResearcher Code Entity Mapping**

This diagram maps the high-level `GPTResearcher` class to the underlying skill managers and utility functions that execute the logic.

Sources: [gpt_researcher/agent.py:36-195](), [gpt_researcher/utils/llm.py:41-146](), [gpt_researcher/skills/browser.py:37-84]()

---

## Utility Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `get_costs()` | `float` | Returns total accumulated research costs. [gpt_researcher/agent.py:688-693]() |
| `add_costs(cost)` | `None` | Increments research costs; validates input type. [gpt_researcher/agent.py:703-714]() |
| `get_research_sources()` | `list[dict]` | Returns all scraped sources (title, content, images). [gpt_researcher/agent.py:591-596]() |
| `get_research_images(top_k)` | `list[str]` | Returns top K selected images. [gpt_researcher/agent.py:598-600]() |
| `extract_headers(markdown)` | `list[dict]` | Extracts H1/H2/H3 headers from markdown. [gpt_researcher/agent.py:635-643]() |

Sources: [gpt_researcher/agent.py:591-714]()

---

# Page: WebSocket Protocol Reference

# WebSocket Protocol Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/chat/chat.py](backend/chat/chat.py)
- [backend/report_type/basic_report/basic_report.py](backend/report_type/basic_report/basic_report.py)
- [backend/report_type/detailed_report/detailed_report.py](backend/report_type/detailed_report/detailed_report.py)
- [backend/run_server.py](backend/run_server.py)
- [backend/server/agent_discovery.py](backend/server/agent_discovery.py)
- [backend/server/app.py](backend/server/app.py)
- [backend/server/multi_agent_runner.py](backend/server/multi_agent_runner.py)
- [backend/server/report_store.py](backend/server/report_store.py)
- [backend/server/server_utils.py](backend/server/server_utils.py)
- [backend/server/websocket_manager.py](backend/server/websocket_manager.py)
- [frontend/index.html](frontend/index.html)
- [frontend/nextjs/components/ResearchBlocks/AccessReport.tsx](frontend/nextjs/components/ResearchBlocks/AccessReport.tsx)
- [frontend/nextjs/components/Settings/ChatBox.tsx](frontend/nextjs/components/Settings/ChatBox.tsx)
- [frontend/nextjs/components/Settings/MCPSelector.tsx](frontend/nextjs/components/Settings/MCPSelector.tsx)
- [frontend/nextjs/components/Task/DomainFilter.tsx](frontend/nextjs/components/Task/DomainFilter.tsx)
- [frontend/nextjs/components/Task/ResearchForm.tsx](frontend/nextjs/components/Task/ResearchForm.tsx)
- [frontend/nextjs/hooks/useWebSocket.ts](frontend/nextjs/hooks/useWebSocket.ts)
- [frontend/nextjs/types/data.ts](frontend/nextjs/types/data.ts)
- [frontend/scripts.js](frontend/scripts.js)
- [frontend/styles.css](frontend/styles.css)
- [tests/test_agent_discovery.py](tests/test_agent_discovery.py)
- [tests/test_websocket_manager.py](tests/test_websocket_manager.py)

</details>



This document specifies the WebSocket protocol used for real-time communication between GPT Researcher clients and the FastAPI backend server. The protocol enables streaming research progress, report generation, and interactive chat functionality.

For information about the REST API endpoints, see [backend/server/app.py:183-231](). For details about the FastAPI backend architecture, see [backend/server/app.py:71-120]().

## Overview

The WebSocket protocol operates over the `/ws` endpoint and uses a text-based message format. The server streams research progress, logs, and generated content to clients in real-time, while clients send commands to initiate research tasks, provide feedback, or engage in post-research chat.

**Key characteristics:**
- **Endpoint:** `ws://{host}/ws` (or `wss://` for secure connections) [frontend/nextjs/hooks/useWebSocket.ts:63-63]()
- **Message format:** Text messages containing JSON payloads or command strings [backend/server/server_utils.py:127-127]()
- **Connection model:** Persistent bidirectional connection with queue-based message delivery [backend/server/websocket_manager.py:24-28]()
- **Streaming:** Server streams partial results during long-running research operations [backend/server/websocket_manager.py:101-114]()

Sources: [backend/server/websocket_manager.py:1-114](), [backend/server/server_utils.py:126-179]()

## Connection Lifecycle

### WebSocket Connection Flow

```mermaid
sequenceDiagram
    participant Client as "Client (Browser)"
    participant WS as "WebSocket Endpoint<br/>/ws"
    participant Manager as "WebSocketManager"
    participant Queue as "asyncio.Queue"
    participant Sender as "start_sender Task"
    
    Client->>WS: Connect to ws://host/ws
    WS->>Manager: connect(websocket)
    Manager->>Manager: websocket.accept()
    Manager->>Manager: active_connections.append()
    Manager->>Queue: Create asyncio.Queue
    Manager->>Sender: Create sender task
    Sender->>Sender: Loop: await queue.get()
    Manager-->>Client: Connection established
    
    Note over Client,Sender: Connection active
    
    Client->>WS: Send command
    WS->>Manager: Handle command
    Manager->>Queue: Put response messages
    Sender->>Queue: Get message
    Sender->>Client: Send message
    
    Client->>WS: Close connection
    WS->>Manager: disconnect(websocket)
    Manager->>Sender: Cancel task
    Manager->>Manager: Remove from active_connections
    Manager->>Queue: Clean up queue
    Manager-->>Client: Connection closed
```

### Connection Management

The `WebSocketManager` class in `backend/server/websocket_manager.py` handles connection lifecycle:

| Method | Purpose | Location |
|--------|---------|----------|
| `connect(websocket)` | Accept connection, create message queue and sender task | [backend/server/websocket_manager.py:53-60]() |
| `disconnect(websocket)` | Cancel sender task, cleanup queue, close connection | [backend/server/websocket_manager.py:66-99]() |
| `start_sender(websocket)` | Background task to send queued messages to client | [backend/server/websocket_manager.py:30-51]() |

**Connection state tracking:**
- `active_connections: List[WebSocket]` - List of connected clients [backend/server/websocket_manager.py:26]()
- `sender_tasks: Dict[WebSocket, asyncio.Task]` - Sender task per connection [backend/server/websocket_manager.py:27]()
- `message_queues: Dict[WebSocket, asyncio.Queue]` - Message queue per connection [backend/server/websocket_manager.py:28]()

Sources: [backend/server/websocket_manager.py:21-99]()

### Client-Side Connection Monitoring

The frontend tracks connection health and displays status in the `websocket-panel` defined in `frontend/index.html`:

```mermaid
graph TB
    Monitor["WebSocket Monitoring<br/>(scripts.js)"]
    Socket["socket<br/>(WebSocket instance)"]
    
    Monitor --> ReadyState["readyState<br/>0=CONNECTING<br/>1=OPEN<br/>2=CLOSING<br/>3=CLOSED"]
    Monitor --> ConnTime["connectionStartTime<br/>(timestamp)"]
    Monitor --> LastActivity["lastActivityTime<br/>(timestamp)"]
    Monitor --> Attempts["connectionAttempts<br/>(counter)"]
    Monitor --> Messages["messagesReceived<br/>(counter)"]
    
    Monitor --> Display["Status Panel UI<br/>#websocketPanel"]
    
    Socket --> Monitor
    
    style Monitor fill:#f9f9f9
    style Socket fill:#e8f5e9
```

**Monitoring variables:**
- `socket` - WebSocket instance [frontend/scripts.js:14]()
- `connectionStartTime` - Connection establishment timestamp [frontend/scripts.js:15]()
- `lastActivityTime` - Last message received timestamp [frontend/scripts.js:16]()
- `connectionAttempts` - Number of connection attempts [frontend/scripts.js:17]()
- `messagesReceived` - Total messages received counter [frontend/scripts.js:18]()

Sources: [frontend/scripts.js:13-23](), [frontend/index.html:87-134]()

## Message Format Specification

### Client-to-Server Commands

All client commands follow the format: `{command_name} {json_payload}` (except `ping`).

#### Command: `start`

Initiates a research task.

**Format:** `start {json_payload}` [backend/server/server_utils.py:127-127]()

**Payload schema:**
```json
{
  "task": "Research query string",
  "report_type": "research_report|detailed_report|resource_report|deep|multi_agents",
  "report_source": "web|local|hybrid|azure",
  "source_urls": ["url1", "url2"],
  "document_urls": ["doc_url1"],
  "tone": "Objective|Formal|Analytical|...",
  "headers": {},
  "query_domains": ["domain1.com", "domain2.com"],
  "mcp_enabled": true|false,
  "mcp_strategy": "fast|deep|disabled",
  "mcp_configs": [],
  "max_search_results": 10
}
```

**Required fields:** `task`, `report_type` [backend/server/server_utils.py:143-145]()

**Processing:** Handled by `handle_start_command` which extracts data and calls `manager.start_streaming` [backend/server/server_utils.py:126-173]().

Sources: [backend/server/server_utils.py:126-179](), [backend/server/websocket_manager.py:101-114]()

#### Command: `chat`

Sends a chat message for post-research Q&A.

**Format:** `chat {json_payload}` [backend/server/server_utils.py:191-192]()

**Payload schema:**
```json
{
  "message": "User question",
  "report": "Full report context",
  "messages": [
    {"role": "user", "content": "question1"},
    {"role": "assistant", "content": "answer1"}
  ]
}
```

**Processing:** Handled by `handle_chat_command` which uses `ChatAgentWithMemory` [backend/server/server_utils.py:187-251]().

Sources: [backend/server/server_utils.py:187-251](), [backend/chat/chat.py:55-184]()

#### Command: `human_feedback`

Provides human feedback in multi-agent workflows.

**Format:** `human_feedback {json_payload}` [backend/server/server_utils.py:182-182]()

**Processing:** Handled by `handle_human_feedback` [backend/server/server_utils.py:181-185]().

Sources: [backend/server/server_utils.py:181-185]()

#### Command: `ping`

Health check command used to keep connection alive.

**Format:** `ping` (no payload) [backend/server/websocket_manager.py:43-43]()

**Response:** `pong` (text response) [backend/server/websocket_manager.py:44-44]()

Sources: [backend/server/websocket_manager.py:41-44](), [frontend/nextjs/hooks/useWebSocket.ts:31-43]()

### Server-to-Client Message Types

All server messages (except `pong`) are JSON objects with a `type` field.

#### Message Type Routing Table

| Type | Purpose | Contains | Processing |
|------|---------|----------|------------|
| `logs` | Research progress events | `content`, `output` | Append to output display [backend/server/server_utils.py:67-72]() |
| `report` | Incremental report chunks | `output` | Append to report (streaming) [frontend/nextjs/hooks/useWebSocket.ts:120-121]() |
| `report_complete` | Final complete report | `output` | Replace report with final version [frontend/nextjs/hooks/useWebSocket.ts:122-125]() |
| `path` | Generated file paths | `output` | Enable download buttons [frontend/nextjs/hooks/useWebSocket.ts:126-127]() |
| `chat` | Chat response | `content`, `role`, `metadata` | Display in chat container [backend/server/server_utils.py:237-246]() |
| `human_feedback` | Feedback request | `content`, `output` | Show feedback UI [frontend/nextjs/hooks/useWebSocket.ts:113-115]() |
| `error` | Error message | `content`, `output` | Display error alert [frontend/nextjs/hooks/useWebSocket.ts:111-112]() |

Sources: [frontend/nextjs/hooks/useWebSocket.ts:102-134](), [backend/server/server_utils.py:56-80]()

### Message Type Schemas

#### Type: `logs`

Streams research progress and events.

```json
{
  "type": "logs",
  "content": "subqueries|added_source_url|mcp_init|research_step|error",
  "output": "Human-readable message"
}
```

Sources: [backend/server/websocket_manager.py:127-131](), [backend/server/server_utils.py:67-72]()

#### Type: `path`

Provides file paths for generated report outputs.

```json
{
  "type": "path",
  "output": {
    "pdf": "outputs/task_...pdf",
    "docx": "outputs/task_...docx",
    "md": "outputs/task_...md",
    "json": "outputs/task_...json"
  }
}
```

Sources: [backend/server/server_utils.py:175-178](), [backend/server/server_utils.py:253-261]()

## CustomLogsHandler

The `CustomLogsHandler` class in `backend/server/server_utils.py` captures streaming logs and stores them in a persistent JSON file.

### Architecture

```mermaid
graph LR
    Research["GPTResearcher<br/>Research Process"]
    Handler["CustomLogsHandler"]
    WS["WebSocket Client"]
    File["JSON Log File<br/>outputs/*.json"]
    
    Research -->|"send_json(data)"| Handler
    Handler -->|"Real-time"| WS
    Handler -->|"Persistent"| File
    
    File -->|Structure| Schema["timestamp<br/>events[]<br/>content.query<br/>content.sources<br/>content.context<br/>content.report<br/>content.costs"]
    
    style Handler fill:#f9f9f9
    style File fill:#f9f9f9
```

**Implementation Details:**
- **Initialization:** Creates a log file in `outputs/` with metadata [backend/server/server_utils.py:35-54]().
- **Persistence:** Every message sent via `send_json` is appended to the `events` or `content` section of the JSON file [backend/server/server_utils.py:56-79]().

Sources: [backend/server/server_utils.py:33-80]()

## Complete Message Flow Example

### Research Task Execution Flow

```mermaid
sequenceDiagram
    participant Client
    participant WS as WebSocket Handler
    participant Handler as CustomLogsHandler
    participant Manager as WebSocketManager
    participant Research as BasicReport/DetailedReport
    
    Client->>WS: start {"task": "...", "report_type": "..."}
    WS->>Handler: Create CustomLogsHandler(websocket, task)
    Handler->>Handler: Initialize JSON log file
    
    WS->>Manager: start_streaming(...)
    Manager->>Research: Create BasicReport or DetailedReport
    Manager->>Research: researcher.run()
    
    loop Research Progress
        Research->>Handler: send_json({type: "logs", content: "..."})
        Handler->>Client: Stream message
        Handler->>Handler: Append to JSON log
    end
    
    Research->>Handler: send_json({type: "report", output: "chunk"})
    Handler->>Client: Stream report chunk
    
    Research->>Handler: send_json({type: "report_complete", output: "full"})
    Handler->>Client: Send complete report
    
    Research-->>Manager: Return final report
    Manager->>WS: generate_report_files(report)
    WS->>Client: send_json({type: "path", output: {pdf, docx, md, json}})
```

Sources: [backend/server/server_utils.py:126-179](), [backend/server/websocket_manager.py:101-114](), [backend/report_type/basic_report/basic_report.py:72-75](), [backend/report_type/detailed_report/detailed_report.py:84-91]()

---

**Related documentation:**
- For REST API endpoints, see [REST API Reference](#13.4)
- For FastAPI backend architecture, see [FastAPI Backend and WebSocket API](#8.1)
- For frontend implementations, see [NextJS Production Frontend](#8.2), [Vanilla JS Lightweight Frontend](#8.3)
- For research workflow internals, see [Query Planning and Decomposition](#9.1) - [Image Generation System](#9.6)

---

# Page: Configuration Schema

# Configuration Schema

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/docs/gpt-researcher/gptr/config.md](docs/docs/gpt-researcher/gptr/config.md)
- [gpt_researcher/actions/query_processing.py](gpt_researcher/actions/query_processing.py)
- [gpt_researcher/config/config.py](gpt_researcher/config/config.py)
- [gpt_researcher/config/variables/base.py](gpt_researcher/config/variables/base.py)
- [gpt_researcher/config/variables/default.py](gpt_researcher/config/variables/default.py)
- [gpt_researcher/llm_provider/__init__.py](gpt_researcher/llm_provider/__init__.py)
- [gpt_researcher/utils/llm.py](gpt_researcher/utils/llm.py)

</details>



This page provides the complete configuration schema reference for GPT Researcher. It documents the structure, validation rules, and type constraints for configuration files (`config.json`), environment variables, and the internal `Config` class attributes.

The configuration system is designed to be hierarchical: it loads defaults, merges values from a JSON configuration file if provided, and finally overrides settings with environment variables.

---

## Configuration System Architecture

The configuration system is managed by the `Config` class, which handles loading, parsing, and type conversion.

### Configuration Flow and Data Mapping

This diagram illustrates how configuration data flows from raw sources into the `Config` class and maps to specific code entities.

```mermaid
graph TD
    subgraph "Configuration Sources"
        EnvVars["Environment Variables<br/>(os.getenv)"]
        JSONFile["JSON Config File<br/>(config.json)"]
        DefaultConfig["DEFAULT_CONFIG<br/>(variables/default.py)"]
    end
    
    subgraph "gpt_researcher.config.Config" [Config Class Entity]
        LoadConfig["Config.load_config()"]
        SetAttrs["Config._set_attributes()"]
        ConvertEnv["Config.convert_env_value()"]
        
        subgraph "Internal Parsers"
            ParseLLM["Config.parse_llm()"]
            ParseEmbed["Config.parse_embedding()"]
            ParseRetr["Config.parse_retrievers()"]
            ParseReason["Config.parse_reasoning_effort()"]
        end
    end
    
    subgraph "Downstream Usage"
        LLMUtil["gpt_researcher.utils.llm<br/>create_chat_completion()"]
        QueryProc["gpt_researcher.actions.query_processing<br/>generate_sub_queries()"]
    end

    DefaultConfig --> LoadConfig
    JSONFile --> LoadConfig
    LoadConfig --> SetAttrs
    EnvVars --> SetAttrs
    
    SetAttrs --> ConvertEnv
    ConvertEnv --> ParseLLM
    ConvertEnv --> ParseEmbed
    ConvertEnv --> ParseRetr
    ConvertEnv --> ParseReason
    
    ParseLLM --> LLMUtil
    ParseReason --> LLMUtil
    ParseRetr --> QueryProc
```

**Sources:** [gpt_researcher/config/config.py:19-61](), [gpt_researcher/config/config.py:157-167](), [gpt_researcher/utils/llm.py:41-53]()

---

## Configuration Parameter Reference

The following table details the parameters available in `BaseConfig`. Note that while the schema keys are uppercase (e.g., `RETRIEVER`), they are accessed as lowercase attributes on the `Config` instance (e.g., `cfg.retriever`).

### Core Settings

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `RETRIEVER` | `str` | `"tavily"` | Search engine(s) to use. Can be a comma-separated list. [gpt_researcher/config/config.py:78-83]() |
| `EMBEDDING` | `str` | `"openai:text-embedding-3-small"` | Embedding model in `provider:model` format. [gpt_researcher/config/variables/default.py:5]() |
| `FAST_LLM` | `str` | `"openai:gpt-4o-mini"` | Model for fast tasks like summarization. [gpt_researcher/config/variables/default.py:7]() |
| `SMART_LLM` | `str` | `"openai:gpt-4.1"` | Model for high-quality report generation. [gpt_researcher/config/variables/default.py:8]() |
| `STRATEGIC_LLM` | `str` | `"openai:o4-mini"` | Model for research planning and sub-query generation. [gpt_researcher/config/variables/default.py:9]() |
| `TEMPERATURE` | `float` | `0.4` | LLM sampling temperature. [gpt_researcher/config/variables/default.py:16]() |
| `REASONING_EFFORT` | `str` | `"medium"` | Reasoning effort for supported models (low, medium, high). [gpt_researcher/config/variables/default.py:45]() |

### Research Constraints

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `FAST_TOKEN_LIMIT` | `int` | `3000` | Max tokens for fast LLM responses. [gpt_researcher/config/variables/default.py:10]() |
| `SMART_TOKEN_LIMIT` | `int` | `6000` | Max tokens for smart LLM responses. [gpt_researcher/config/variables/default.py:11]() |
| `STRATEGIC_TOKEN_LIMIT` | `int` | `4000` | Max tokens for strategic LLM responses. [gpt_researcher/config/variables/default.py:12]() |
| `MAX_ITERATIONS` | `int` | `3` | Max iterations for query expansion. [gpt_researcher/config/variables/default.py:22]() |
| `MAX_SUBTOPICS` | `int` | `3` | Max subtopics for detailed reports. [gpt_researcher/config/variables/default.py:27]() |
| `TOTAL_WORDS` | `int` | `1200` | Target word count for the final report. [gpt_researcher/config/variables/default.py:20]() |

### Scraper and Source Settings

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `SCRAPER` | `str` | `"bs"` | Web scraper backend (e.g., `bs`, `newspaper`). [gpt_researcher/config/variables/default.py:24]() |
| `MAX_SCRAPER_WORKERS` | `int` | `15` | Max concurrent scraping tasks. [gpt_researcher/config/variables/default.py:25]() |
| `SCRAPER_RATE_LIMIT_DELAY` | `float` | `0.0` | Minimum seconds between scraper requests. [gpt_researcher/config/variables/default.py:26]() |
| `REPORT_SOURCE` | `str` | `"web"` | Source of data: `web`, `local`, `azure`, etc. [gpt_researcher/config/variables/default.py:29]() |
| `DOC_PATH` | `str` | `"./my-docs"` | Directory for local document research. [gpt_researcher/config/variables/default.py:30]() |
| `CURATE_SOURCES` | `bool` | `False` | Use an extra LLM step to rank sources. [gpt_researcher/config/variables/default.py:14]() |

### Image Generation Settings

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `IMAGE_GENERATION_ENABLED` | `bool` | `False` | Master switch for inline image generation. [gpt_researcher/config/variables/default.py:52]() |
| `IMAGE_GENERATION_MODEL` | `str` | `"models/gemini-2.5-flash-image"` | Model used for generating images. [gpt_researcher/config/variables/default.py:50]() |
| `IMAGE_GENERATION_PROVIDER` | `str` | `"google"` | Image provider: `google` or `modelslab`. [gpt_researcher/config/variables/default.py:54]() |
| `IMAGE_GENERATION_MAX_IMAGES` | `int` | `3` | Maximum images per report. [gpt_researcher/config/variables/default.py:51]() |

**Sources:** [gpt_researcher/config/variables/base.py:5-51](), [gpt_researcher/config/variables/default.py:3-55]()

---

## Deep Research Schema

Parameters specific to the recursive deep research mode introduced in newer versions.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `DEEP_RESEARCH_BREADTH` | `int` | `3` | Number of parallel paths to explore. [gpt_researcher/config/variables/default.py:36]() |
| `DEEP_RESEARCH_DEPTH` | `int` | `2` | Depth of the search tree. [gpt_researcher/config/variables/default.py:37]() |
| `DEEP_RESEARCH_CONCURRENCY` | `int` | `4` | Concurrent operations during deep research. [gpt_researcher/config/variables/default.py:38]() |

**Sources:** [gpt_researcher/config/variables/default.py:35-38]()

---

## Model Context Protocol (MCP) Schema

The MCP configuration allows GPT Researcher to connect to external tool servers.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `MCP_SERVERS` | `List[Dict]` | `[]` | List of server configs (name, command, args, env). [gpt_researcher/config/variables/default.py:41]() |
| `MCP_STRATEGY` | `str` | `"fast"` | Strategy: `fast`, `deep`, or `disabled`. [gpt_researcher/config/variables/default.py:44]() |
| `MCP_ALLOWED_ROOT_PATHS` | `List[str]` | `[]` | Filesystem paths accessible to MCP. [gpt_researcher/config/variables/default.py:43]() |
| `MCP_AUTO_TOOL_SELECTION` | `bool` | `True` | Automatically select the best tool for a query. [gpt_researcher/config/variables/default.py:42]() |

**Sources:** [gpt_researcher/config/variables/base.py:40-44](), [gpt_researcher/config/variables/default.py:40-44]()

---

## Implementation Details: Parsing and Validation

The `Config` class implements several private methods to transform raw strings into structured data.

### LLM and Embedding Parsing
The system uses a `provider:model` string format. For example, `openai:gpt-4o`.
- `Config.parse_llm(llm_str)`: Splits the string and returns a tuple of `(provider, model)`. [gpt_researcher/config/config.py:93-95]()
- `Config.parse_embedding(embedding_str)`: Similar logic for embedding providers. [gpt_researcher/config/config.py:87-89]()

### Reasoning Effort Validation
For models supporting reasoning effort (like OpenAI o-series), the system validates against the `ReasoningEfforts` enum.
- Supported values: `low`, `medium`, `high`. [gpt_researcher/llm_provider/generic/base.py:19]()
- Implementation: `Config.parse_reasoning_effort(os.getenv("REASONING_EFFORT"))`. [gpt_researcher/config/config.py:96]()

### LLM Configuration Logic
The following diagram shows how the `Config` attributes are used during a chat completion request in `gpt_researcher/utils/llm.py`.

```mermaid
graph LR
    subgraph "gpt_researcher.utils.llm.create_chat_completion" [create_chat_completion Function]
        CheckModel["Check model in<br/>SUPPORT_REASONING_EFFORT_MODELS"]
        CheckTemp["Check model in<br/>NO_SUPPORT_TEMPERATURE_MODELS"]
        GetLLM["get_llm(provider, **kwargs)"]
    end

    cfg_reasoning["cfg.reasoning_effort"] --> CheckModel
    cfg_temp["cfg.temperature"] --> CheckTemp
    cfg_limit["cfg.smart_token_limit"] --> GetLLM
    
    CheckModel -->|Yes| ReasoningArg["Add reasoning_effort to kwargs"]
    CheckTemp -->|No| TempArg["Add temperature/max_tokens to kwargs"]
    CheckTemp -->|Yes| NullArg["Set temperature/max_tokens to None"]
```

**Sources:** [gpt_researcher/utils/llm.py:83-98](), [gpt_researcher/config/config.py:96]()

---

## Type Conversion Rules

When loading from environment variables, the `Config` class performs automatic type conversion using the `BaseConfig` type hints via `BaseConfig.__annotations__`.

| Target Type | Conversion Logic |
| :--- | :--- |
| `bool` | Returns `True` if value is `"true"`, `"1"`, `"yes"`, or `"on"`. [gpt_researcher/config/config.py:73-74]() |
| `int` | Standard `int()` conversion. [gpt_researcher/config/config.py:74]() |
| `float` | Standard `float()` conversion. [gpt_researcher/config/config.py:74]() |
| `list` / `dict` | Parsed via `json.loads()`. [gpt_researcher/config/config.py:74]() |
| `Union[T, None]` | Handles conversion to `T` or sets to `None`. [gpt_researcher/config/config.py:74]() |

**Sources:** [gpt_researcher/config/config.py:71-75](), [gpt_researcher/config/variables/base.py:5-52]()

---

# Page: REST API Reference

# REST API Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/chat/chat.py](backend/chat/chat.py)
- [backend/run_server.py](backend/run_server.py)
- [backend/server/agent_discovery.py](backend/server/agent_discovery.py)
- [backend/server/app.py](backend/server/app.py)
- [backend/server/report_store.py](backend/server/report_store.py)
- [main.py](main.py)
- [tests/test_agent_discovery.py](tests/test_agent_discovery.py)

</details>



## Purpose and Scope

This document provides comprehensive technical documentation for the REST and WebSocket APIs exposed by the GPT Researcher FastAPI backend server. These APIs enable clients to conduct research, stream real-time logs, manage document context, and interact with AI chat functionality.

The server is built using **FastAPI** [backend/server/app.py:97]() and is typically started via `uvicorn` [main.py:37]() or the backend startup script [backend/run_server.py:21-27](). It serves both a research engine and a persistent storage layer for reports [backend/server/app.py:133-135]().

---

## API Architecture Overview

The backend operates as a stateful server combining standard RESTful endpoints with a high-concurrency `WebSocketManager` for real-time data streaming.

### System Data Flow

The following diagram maps the Natural Language request space to the Code Entity space within the backend.

**Title: Request Processing and Entity Mapping**
```mermaid
graph TD
    subgraph "Client Space"
        User["User Query"]
        JS["frontend/index.html"]
    end

    subgraph "FastAPI Routes (backend/server/app.py)"
        WS_Route["/ws (WebSocket)"]
        Report_Route["/api/reports (GET/POST)"]
        Discovery_Route["/.well-known/agent-discovery.json"]
    end

    subgraph "Core Logic Entities"
        WSM["WebSocketManager<br/>(websocket_manager.py)"]
        RS["ReportStore<br/>(report_store.py)"]
        RA["run_agent<br/>(websocket_manager.py)"]
        CA["ChatAgentWithMemory<br/>(chat/chat.py)"]
    end

    subgraph "Research Engine"
        GPTR["GPTResearcher Class"]
    end

    User --> JS
    JS --> WS_Route
    JS --> Report_Route
    JS --> Discovery_Route

    WS_Route --> WSM
    WSM --> RA
    WSM --> CA
    RA --> GPTR
    
    Report_Route --> RS
    Discovery_Route --> BAD["build_agent_discovery_document<br/>(agent_discovery.py)"]
```
**Sources:** [backend/server/app.py:132-135](), [backend/server/app.py:162-172](), [backend/server/app.py:183-200](), [backend/server/websocket_manager.py:32]()

---

## Base Configuration

### Server Details

| Property | Value | Code Reference |
|----------|-------|----------------|
| **Default Host** | `0.0.0.0` | [main.py:37]() |
| **Default Port** | `8000` | [main.py:37]() |
| **Framework** | FastAPI | [backend/server/app.py:97]() |
| **CORS** | Configurable via `CORS_ALLOW_ORIGINS` | [backend/server/app.py:100-120]() |

### Static File Serving
The server mounts several static directories to serve the frontend and generated outputs via the `lifespan` context manager [backend/server/app.py:71-92]():
- `/outputs`: Serves generated PDF/Docx reports [backend/server/app.py:75]().
- `/static`: Serves frontend assets and images [backend/server/app.py:86]().
- `/site`: Serves the main frontend application files [backend/server/app.py:80]().

---

## REST Endpoints Reference

### Report Management
The server uses a `ReportStore` to persist research metadata to a JSON file (default: `data/reports.json`) [backend/server/app.py:135]().

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/reports` | `GET` | Lists all reports or a filtered subset via `report_ids` query param [backend/server/app.py:183-187](). |
| `/api/reports/{id}` | `GET` | Retrieves a specific report's full JSON data [backend/server/app.py:190-196](). |
| `/api/reports` | `POST` | Creates or updates a report entry in the store [backend/server/app.py:198-210](). |
| `/report/{id}` | `GET` | Downloads the `.docx` version of a generated report [backend/server/app.py:174-179](). |

### Agent Discovery
GPT Researcher supports the Agent Discovery Protocol to advertise its services [backend/server/app.py:162-172]().

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/.well-known/agent-discovery.json` | `GET` | Returns a JSON document describing available research and chat services [backend/server/agent_discovery.py:12-68](). |

**Sources:** [backend/server/app.py:162-210](), [backend/server/report_store.py:32-57](), [backend/server/agent_discovery.py:20-57]()

---

## WebSocket API (`/ws`)

The WebSocket endpoint is the primary interface for the research workflow, managed by the `WebSocketManager` [backend/server/app.py:133]().

### Connection Lifecycle

**Title: WebSocket Execution Sequence**
```mermaid
sequenceDiagram
    participant C as Client (Browser)
    participant WSM as WebSocketManager
    participant RA as run_agent
    participant GPTR as GPTResearcher

    C->>WSM: Connect
    WSM->>WSM: add_connection()
    C->>WSM: "start {"task": "..."}"
    WSM->>RA: Trigger Research
    RA->>GPTR: Initialize & Conduct
    loop Researching
        GPTR->>WSM: stream_output(type="logs")
        WSM->>C: JSON Log
    end
    GPTR->>RA: Final Report
    RA->>WSM: stream_output(type="report")
    WSM->>C: Markdown Content
```
**Sources:** [backend/server/websocket_manager.py:32](), [backend/server/server_utils.py:28]()

### WebSocket Commands

#### 1. `start`
Initiates a research task.
**Payload Schema (`ResearchRequest` equivalent):**
```json
{
  "task": "string",
  "report_type": "research_report | detailed_report | deep | multi_agents",
  "report_source": "web | local | hybrid",
  "tone": "Objective | Formal | etc",
  "headers": {}
}
```
**Implementation:** Handled by `handle_websocket_communication` which routes to `run_agent` [backend/server/server_utils.py:28]().

#### 2. `chat`
Interacts with the `ChatAgentWithMemory` [backend/chat/chat.py:55]().
**Payload Schema (`ChatRequest`):**
```json
{
  "report": "string (context)",
  "messages": [{"role": "user", "content": "..."}]
}
```
**Implementation:** Uses `ChatAgentWithMemory.chat()` to process completions with tool support like `quick_search` via Tavily [backend/chat/chat.py:114-184]().

---

## Response Schemas (Server → Client)

The server communicates using a standardized JSON envelope for streaming.

### 1. Research Logs
```json
{
  "type": "logs",
  "output": "🔎 Finding relevant URLs..."
}
```

### 2. Report Content
```json
{
  "type": "report",
  "output": "# Research Results\n..."
}
```

### 3. Tool Metadata (Chat)
When the chat agent performs a web search, it returns metadata about the sources found [backend/chat/chat.py:134-142]().
```json
{
  "tool": "quick_search",
  "query": "search query",
  "search_metadata": {
    "query": "...",
    "sources": [{"title": "...", "url": "...", "content": "..."}]
  }
}
```

**Sources:** [backend/chat/chat.py:168-182](), [backend/server/app.py:64-69]()

---

## Error Handling

The API implements several layers of error protection:
1. **Report Persistence Safety:** `ReportStore` uses an `asyncio.Lock` and temporary file writes (`.tmp`) to prevent data corruption during concurrent access [backend/server/report_store.py:10-30]().
2. **WebSocket Disconnects:** `WebSocketDisconnect` is caught to gracefully remove connections from the manager [backend/server/app.py:14]().
3. **HTTP Exceptions:** REST endpoints return standard FastAPI `HTTPException` (e.g., 404 for missing reports) [backend/server/app.py:194]().

**Sources:** [backend/server/report_store.py:33-57](), [backend/server/app.py:193-195]()

---

# Page: Multi-Agent Task Configuration Schema

# Multi-Agent Task Configuration Schema

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [backend/utils.py](backend/utils.py)
- [multi_agents/README.md](multi_agents/README.md)
- [multi_agents/agent.py](multi_agents/agent.py)
- [multi_agents/agents/human.py](multi_agents/agents/human.py)
- [multi_agents/agents/orchestrator.py](multi_agents/agents/orchestrator.py)
- [multi_agents/agents/plan_review.py](multi_agents/agents/plan_review.py)
- [multi_agents/agents/utils/file_formats.py](multi_agents/agents/utils/file_formats.py)
- [multi_agents/langgraph.json](multi_agents/langgraph.json)
- [multi_agents/main.py](multi_agents/main.py)
- [multi_agents/memory/research.py](multi_agents/memory/research.py)
- [multi_agents/requirements.txt](multi_agents/requirements.txt)
- [multi_agents/task.json](multi_agents/task.json)
- [tests/test_multi_agents_plan_revisions.py](tests/test_multi_agents_plan_revisions.py)

</details>



## Purpose and Scope

This page provides a technical reference for the `task.json` configuration schema used in the multi-agent research system. The `task.json` file acts as the primary configuration entry point for defining research parameters, model selection, output formats, and quality control guidelines in the LangGraph-based multi-agent workflow.

The schema is primarily consumed by the `ChiefEditorAgent` and distributed across specialized agents including the `EditorAgent`, `ResearchAgent`, `ReviewerAgent`, `ReviserAgent`, `WriterAgent`, and `PublisherAgent`.

Sources: [multi_agents/task.json:1-19](), [multi_agents/README.md:63-75]()

---

## Schema Structure and Data Flow

The `task.json` file is located in the `multi_agents/` directory and is loaded during the initialization of the research process. The data flows from the JSON file into a Python dictionary, which is then embedded into the global `ResearchState`.

### Configuration Data Flow Diagram

This diagram illustrates how the `task.json` fields map to specific code entities and how they are processed by the system.

```mermaid
graph TD
    subgraph "Natural Language & Config Space (task.json)"
        JSON["task.json"]
        Q["'query'"]
        M["'model'"]
        S["'source'"]
        G["'guidelines'"]
        F["'publish_formats'"]
        MPR["'max_plan_revisions'"]
    end

    subgraph "Code Entity Space (Python)"
        Main["main.py: open_task()"]
        State["ResearchState (TypedDict)"]
        Chief["ChiefEditorAgent"]
        Human["HumanAgent: review_plan()"]
        Publisher["PublisherAgent: run()"]
    end

    JSON -->|"json.load()"| Main
    Q -->|"task['query']"| State
    M -->|"task['model']"| State
    S -->|"task['source']"| State
    MPR -->|"task['max_plan_revisions']"| State
    
    Main -->|"Initialize"| Chief
    State -->|"Passed to"| Human
    State -->|"Passed to"| Publisher

    Human -->|"route_human_feedback()"| PlanReview["agents/plan_review.py"]
    Publisher -->|"publish_formats parameter"| Formats["agents/utils/file_formats.py"]
```

Sources: [multi_agents/main.py:17-38](), [multi_agents/memory/research.py:5-20](), [multi_agents/agents/orchestrator.py:23-54](), [multi_agents/agents/human.py:10-15]()

---

## Complete Field Reference

The following table details the schema requirements for `task.json`.

| Field | Type | Description | Code Usage |
| :--- | :--- | :--- | :--- |
| `query` | `string` | The main research topic or question. | [multi_agents/main.py:42]() |
| `model` | `string` | The LLM model to use (e.g., `gpt-4o`). | [multi_agents/main.py:29-37]() |
| `max_sections` | `integer` | Max subtopics the Editor will plan. | [multi_agents/task.json:3]() |
| `max_plan_revisions` | `integer` | Max human-requested plan revisions allowed. | [multi_agents/agents/plan_review.py:8-23]() |
| `publish_formats` | `object` | Boolean flags for `markdown`, `pdf`, `docx`. | [multi_agents/agents/utils/file_formats.py:24-104]() |
| `include_human_feedback` | `boolean` | Whether to pause for human input via `HumanAgent`. | [multi_agents/agents/human.py:18]() |
| `follow_guidelines` | `boolean` | Enables stricter adherence to specified criteria. | [multi_agents/task.json:11]() |
| `guidelines` | `array` | List of strings defining quality criteria (e.g. APA format). | [multi_agents/task.json:13-17]() |
| `source` | `string` | Research source: `web` or `local`. | [multi_agents/README.md:70]() |
| `verbose` | `boolean` | Enables detailed agent logging. | [multi_agents/task.json:18]() |

Sources: [multi_agents/task.json:1-19](), [multi_agents/README.md:65-75](), [multi_agents/agents/plan_review.py:1-23]()

---

## Technical Implementation Details

### Configuration Loading and Overrides
The `open_task()` function in `multi_agents/main.py` is responsible for reading the file. It includes logic to override the `model` field if the `STRATEGIC_LLM` environment variable is present.

[multi_agents/main.py:29-36]():
```python
    # Override model with STRATEGIC_LLM if defined in environment
    strategic_llm = os.environ.get("STRATEGIC_LLM")
    if strategic_llm and ":" in strategic_llm:
        # Extract the model name (part after the first colon)
        model_name = strategic_llm.split(":", 1)[1]
        task["model"] = model_name
    elif strategic_llm:
        task["model"] = strategic_llm
```

### Human-in-the-loop and Revisions
The `HumanAgent` utilizes the `include_human_feedback` flag to decide whether to prompt the user via WebSocket or console. The `max_plan_revisions` field is critical for the `route_human_feedback` function, which determines if the workflow should loop back to the `planner` or proceed to `researcher`.

[multi_agents/agents/plan_review.py:8-23]():
```python
def route_human_feedback(review, max_plan_revisions=DEFAULT_MAX_PLAN_REVISIONS):
    if review.get("human_feedback") is None:
        return "accept"
    # ... logic to check plan_revision_count against max_plan_revisions
    return "revise"
```

Sources: [multi_agents/main.py:17-38](), [multi_agents/agents/human.py:18-45](), [multi_agents/agents/plan_review.py:8-23]()

---

## Multi-Agent Workflow Mapping

This diagram bridges the configuration requirements defined in `task.json` to the specific code entities that execute them during the research lifecycle using the `StateGraph`.

```mermaid
sequenceDiagram
    participant J as "task.json (JSON)"
    participant C as "ChiefEditorAgent (orchestrator.py)"
    participant H as "HumanAgent (human.py)"
    participant P as "PublisherAgent (publisher.py)"
    participant F as "file_formats.py"

    Note over J, F: Initialization
    J->>C: Load "query", "model"
    C->>C: _initialize_agents()

    Note over J, F: Human Feedback Loop
    J->>H: Load "include_human_feedback"
    C->>H: review_plan(research_state)
    H-->>C: human_feedback, plan_revision_count
    C->>C: _route_human_feedback(max_plan_revisions)

    Note over J, F: Publication Stage
    J->>P: Load "publish_formats"
    C->>P: run(research_state)
    P->>F: write_md_to_pdf() / write_md_to_word()
```

Sources: [multi_agents/agents/orchestrator.py:56-90](), [multi_agents/agents/human.py:10-59](), [multi_agents/agents/utils/file_formats.py:40-104]()

---

## Example Configuration

A standard `task.json` used for comprehensive research:

```json
{
  "query": "Is AI in a hype cycle?",
  "max_sections": 3,
  "max_plan_revisions": 3,
  "publish_formats": {
    "markdown": true,
    "pdf": true,
    "docx": true
  },
  "include_human_feedback": false,
  "source": "web",
  "follow_guidelines": true,
  "model": "gpt-4o",
  "guidelines": [
    "The report MUST be written in APA format",
    "The report MUST be written in english"
  ],
  "verbose": true
}
```

Sources: [multi_agents/task.json:1-19](), [multi_agents/README.md:78-99]()

---

# Page: Glossary

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README-ja_JP.md](README-ja_JP.md)
- [README-ko_KR.md](README-ko_KR.md)
- [README-zh_CN.md](README-zh_CN.md)
- [README.md](README.md)
- [docs/CNAME](docs/CNAME)
- [docs/docs/contribute.md](docs/docs/contribute.md)
- [docs/docs/gpt-researcher/gptr/config.md](docs/docs/gpt-researcher/gptr/config.md)
- [docs/docs/gpt-researcher/llms/llms.md](docs/docs/gpt-researcher/llms/llms.md)
- [docs/docs/gpt-researcher/llms/supported-llms.md](docs/docs/gpt-researcher/llms/supported-llms.md)
- [gpt_researcher/actions/query_processing.py](gpt_researcher/actions/query_processing.py)
- [gpt_researcher/agent.py](gpt_researcher/agent.py)
- [gpt_researcher/config/config.py](gpt_researcher/config/config.py)
- [gpt_researcher/config/variables/base.py](gpt_researcher/config/variables/base.py)
- [gpt_researcher/config/variables/default.py](gpt_researcher/config/variables/default.py)
- [gpt_researcher/llm_provider/__init__.py](gpt_researcher/llm_provider/__init__.py)
- [gpt_researcher/llm_provider/generic/base.py](gpt_researcher/llm_provider/generic/base.py)
- [gpt_researcher/memory/embeddings.py](gpt_researcher/memory/embeddings.py)
- [gpt_researcher/skills/browser.py](gpt_researcher/skills/browser.py)
- [gpt_researcher/skills/researcher.py](gpt_researcher/skills/researcher.py)
- [gpt_researcher/utils/llm.py](gpt_researcher/utils/llm.py)
- [multi_agents/README.md](multi_agents/README.md)
- [multi_agents/agent.py](multi_agents/agent.py)
- [multi_agents/agents/human.py](multi_agents/agents/human.py)
- [multi_agents/agents/orchestrator.py](multi_agents/agents/orchestrator.py)
- [multi_agents/agents/plan_review.py](multi_agents/agents/plan_review.py)
- [multi_agents/memory/research.py](multi_agents/memory/research.py)
- [multi_agents/task.json](multi_agents/task.json)
- [tests/test_multi_agents_plan_revisions.py](tests/test_multi_agents_plan_revisions.py)

</details>



This page provides definitions for codebase-specific terms, jargon, and domain concepts used throughout the **GPT Researcher** project. It serves as a technical reference for onboarding engineers to bridge the gap between high-level research concepts and their specific implementations in the code.

## Core System Entities

### GPTResearcher (The Orchestrator)
The central entry point and coordinator for the research process. It initializes configuration, manages state (costs, context, visited URLs), and delegates tasks to specialized "Skills".
*   **Implementation**: `GPTResearcher` class in [gpt_researcher/agent.py:36-83]().
*   **Key Role**: Orchestrates the flow from query input to final report generation [gpt_researcher/agent.py:39-42]().

### ResearchConductor
The "Skill" responsible for the execution logic of the research phase. It handles query planning, sub-query generation, and gathering context from various sources.
*   **Implementation**: `ResearchConductor` class in [gpt_researcher/skills/researcher.py:21-32]().
*   **Key Functions**: `plan_research` [gpt_researcher/skills/researcher.py:48-87]() and `conduct_research` [gpt_researcher/skills/researcher.py:89-160]().

### PromptFamily
A strategy pattern implementation for managing LLM prompts. Different model families (e.g., OpenAI, Granite) require different formatting or instruction styles.
*   **Implementation**: `PromptFamily` base class in [gpt_researcher/prompts.py:14-29]().
*   **Supported Types**: Defined in `PromptFamily` enum [gpt_researcher/utils/enum.py:94-101]().

### GenericLLMProvider
An abstraction layer that allows GPT Researcher to interact with over 25+ LLM providers (OpenAI, Anthropic, Ollama, etc.) using a unified interface.
*   **Implementation**: `GenericLLMProvider` in [gpt_researcher/llm_provider/generic/base.py:91-98]().
*   **Factory Method**: `from_provider` dynamically loads the correct LangChain integration [gpt_researcher/llm_provider/generic/base.py:122-214]().

---

## Natural Language to Code Mapping

The following diagrams illustrate how high-level research concepts map to specific classes and files within the repository.

### Diagram 1: Research Workflow Mapping
This diagram maps the logical steps of a research task to the code entities that execute them.

```mermaid
graph TD
    subgraph "Natural_Language_Space"
        Task["'Research Nvidia Stock'"]
        Plan["'Create sub-questions'"]
        Search["'Find web sources'"]
        Write["'Draft the report'"]
    end

    subgraph "Code_Entity_Space"
        Agent["GPTResearcher Class [gpt_researcher/agent.py]"]
        Conductor["ResearchConductor.plan_research() [gpt_researcher/skills/researcher.py]"]
        Retriever["get_search_results() [gpt_researcher/actions/query_processing.py]"]
        Generator["ReportGenerator.write_report() [gpt_researcher/skills/writer.py]"]
    end

    Task --> Agent
    Plan --> Conductor
    Search --> Retriever
    Write --> Generator
```
**Sources**: [gpt_researcher/agent.py:36-50](), [gpt_researcher/skills/researcher.py:21-47](), [gpt_researcher/skills/writer.py:1-30]()

### Diagram 2: Configuration and LLM Tier Mapping
This diagram shows how environmental configuration maps to the internal "Three-Tier" LLM strategy.

```mermaid
graph LR
    subgraph "Environment_Config"
        FAST["FAST_LLM=openai:gpt-4o-mini"]
        SMART["SMART_LLM=anthropic:claude-3-5-sonnet"]
        STRAT["STRATEGIC_LLM=openai:o1-preview"]
    end

    subgraph "Config_Class_[gpt_researcher/config/config.py]"
        F_Attr["self.fast_llm_model"]
        S_Attr["self.smart_llm_model"]
        ST_Attr["self.strategic_llm_model"]
    end

    subgraph "LLM_Utility_[gpt_researcher/utils/llm.py]"
        CCC["create_chat_completion()"]
    end

    FAST --> F_Attr
    SMART --> S_Attr
    STRAT --> ST_Attr
    F_Attr --> CCC
    S_Attr --> CCC
    ST_Attr --> CCC
```
**Sources**: [gpt_researcher/config/config.py:91-96](), [gpt_researcher/utils/llm.py:41-69](), [docs/docs/gpt-researcher/llms/llms.md:19-30]()

---

## Technical Jargon & Domain Terms

| Term | Definition | Code Pointer |
| :--- | :--- | :--- |
| **ReportSource** | Enum defining where data comes from (Web, Local, Hybrid, etc.). | [gpt_researcher/utils/enum.py:30-52]() |
| **ReportType** | Enum defining the structure/goal of the report (Research, Detailed, Deep, etc.). | [gpt_researcher/utils/enum.py:6-28]() |
| **Tone** | Specific writing styles applied to the final output (Objective, Analytical, etc.). | [gpt_researcher/utils/enum.py:54-92]() |
| **MCP** | Model Context Protocol; allows the agent to use external tools/servers for data. | [gpt_researcher/config/config.py:52-61]() |
| **Sub-queries** | Decomposed smaller questions generated from a single main research query. | [gpt_researcher/skills/researcher.py:48-54]() |
| **Context Compression** | Reducing large amounts of scraped text into relevant snippets for LLM context limits. | [gpt_researcher/skills/context_manager.py]() |
| **Reasoning Effort** | A parameter for specific models (like OpenAI's o1/o3) to control thinking depth. | [gpt_researcher/llm_provider/generic/base.py:68-71]() |
| **Three-Tier LLM** | Strategy using FAST (cheap), SMART (reasoning), and STRATEGIC (planning) models. | [gpt_researcher/config/config.py:91-96]() |

---

## Multi-Agent Concepts (LangGraph)

When running in multi-agent mode, the system uses a different set of specialized agents coordinated via a state graph.

*   **Chief Editor**: The master agent coordinating the LangGraph workflow [multi_agents/README.md:18]().
*   **ResearchState**: A `TypedDict` that tracks the overall research progress and shared context [multi_agents/memory/research.py]().
*   **Review-Revision Loop**: A cycle where a `ReviewerAgent` provides feedback and a `ReviserAgent` updates the draft until it meets criteria [multi_agents/README.md:46-47]().

```mermaid
graph TD
    Start((Start)) --> Researcher["ResearcherAgent"]
    Researcher --> Reviewer["ReviewerAgent"]
    Reviewer --> Decision{"Accepted?"}
    Decision -- "No" --> Revisor["ReviserAgent"]
    Revisor --> Reviewer
    Decision -- "Yes" --> End((End))
```
**Sources**: [multi_agents/README.md:40-49](), [multi_agents/agents/orchestrator.py]()