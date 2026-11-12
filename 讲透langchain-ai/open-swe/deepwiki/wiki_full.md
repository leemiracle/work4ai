# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [AGENTS.md](AGENTS.md)
- [CLAUDE.md](CLAUDE.md)
- [CUSTOMIZATION.md](CUSTOMIZATION.md)
- [INSTALLATION.md](INSTALLATION.md)
- [README.md](README.md)
- [default_prompt.md](default_prompt.md)

</details>



## Purpose and Scope

This page introduces Open SWE as a framework for building organization-specific internal coding agents. It explains the core purpose, design philosophy, and how the system composes on existing frameworks like Deep Agents and LangGraph.

For detailed information about specific aspects of the system, see:
- System architecture details: [System Architecture](#1.1)
- Technology stack components: [Technology Stack](#1.2)
- Framework layering and composition: [Framework Composition](#1.3)

**Sources:** [README.md:1-113](), [AGENTS.md:1-10]()

---

## What is Open SWE?

Open SWE is an open-source framework for building internal coding agents tailored to an organization's specific workflows and codebases. Unlike general-purpose coding assistants, Open SWE is designed to meet engineers where they work—in Slack threads, Linear issues, and GitHub pull requests—with the right context, permissions, and safety boundaries to operate autonomously. [README.md:12-27]()

The framework implements architectural patterns used by elite engineering organizations like Stripe, Ramp, and Coinbase: isolated cloud sandboxes for safe execution, subagent orchestration for parallel work, and real-time message queueing for interactive debugging. [README.md:25-27]()

Open SWE is **not** a fork of an existing agent framework. Instead, it **composes on** the [Deep Agents](https://github.com/langchain-ai/deepagents) framework and LangGraph execution engine. This compositional approach allows Open SWE to inherit upstream improvements while providing domain-specific customizations for software engineering. [README.md:38-50](), [AGENTS.md:7-10]()

**Core Characteristics:**
- **Invocation surfaces:** Slack, Linear, and GitHub webhooks. [README.md:98-107]()
- **Execution environment:** Pluggable cloud sandboxes (LangSmith, Modal, Daytona, Runloop, Local). [README.md:52-63](), [CUSTOMIZATION.md:58-64]()
- **Agent framework:** Deep Agents with curated tools and deterministic middleware. [README.md:38-50](), [AGENTS.md:59-71]()
- **Orchestration:** LangGraph for execution state and multi-agent graphs (Agent, Reviewer, Style Analyzer). [AGENTS.md:26-34]()
- **Context engineering:** Repository-specific guidance via `AGENTS.md` and pre-hydrated source context. [README.md:79-85]()

**Sources:** [README.md:12-27](), [README.md:33-41](), [README.md:79-107](), [AGENTS.md:1-34]()

---

## Design Philosophy

Open SWE follows core architectural principles derived from production-grade internal coding agents:

### 1. Composition Over Forking
The system calls `create_deep_agent()` rather than maintaining a forked agent core. Custom capabilities are added via the `tools`, `middleware`, and `system_prompt` parameters. [README.md:42-50](), [CUSTOMIZATION.md:3-24]()

### 2. Isolation First, Then Full Permissions
Every task runs in its own isolated sandbox—a remote Linux environment with complete shell access. Mistakes are contained within the sandbox boundary. [README.md:52-59]()

### 3. Tool Curation Over Quantity
The framework provides a small, focused toolset. Each tool has a clear purpose: `execute` for shell commands, `fetch_url` for web content, and platform-specific tools like `slack_thread_reply`. [README.md:64-76](), [AGENTS.md:81-86]()

### 4. Context is Pre-Hydrated
Agents start with full context from the invocation source (Linear descriptions, Slack history) rather than discovering it step-by-step. Repository-level conventions are injected via `AGENTS.md` files. [README.md:79-85](), [AGENTS.md:1-4]()

### 5. Deterministic Middleware
Middleware hooks run at deterministic points in the agent loop. For example, `check_message_queue_before_model` injects follow-up messages in real-time before the next LLM call. [README.md:91-96](), [AGENTS.md:59-71]()

### 6. Thread Persistence
Each Linear issue, Slack thread, or GitHub PR gets a deterministic thread ID. Follow-up messages route to the same running agent, and sandboxes can persist across invocations. [README.md:106-107](), [AGENTS.md:46-55]()

**Sources:** [README.md:33-113](), [AGENTS.md:36-76](), [CUSTOMIZATION.md:1-24]()

---

## System at a Glance

The following diagram maps Open SWE's high-level architecture to actual code entities in the repository:

```mermaid
graph TB
    subgraph "External Triggers"
        SlackMention["@openswe mentions<br/>in Slack"]
        LinearComment["@openswe comments<br/>in Linear"]
        GitHubComment["@openswe comments<br/>in GitHub PRs"]
    end
    
    subgraph "agent/webapp.py - FastAPI Webhooks"
        SlackEndpoint["/webhooks/slack<br/>handle_slack_event()"]
        LinearEndpoint["/webhooks/linear<br/>handle_linear_webhook()"]
        GitHubEndpoint["/webhooks/github<br/>handle_github_webhook()"]
    end
    
    subgraph "LangGraph Orchestration"
        MainAgent["agent.server:get_agent"]
        ReviewerAgent["agent.reviewer:get_reviewer_agent"]
        StyleAnalyzer["agent.review_style_analyzer:get_review_style_analyzer"]
    end
    
    subgraph "agent/server.py - Agent Assembly"
        GetAgent["get_agent(config)"]
        SandboxState["ensure_sandbox_for_thread()"]
        CreateDeepAgent["deepagents.create_deep_agent()"]
    end
    
    subgraph "agent/integrations/ - Sandbox Providers"
        SandboxFactory["agent.utils.sandbox:create_sandbox"]
        LangSmithSB["agent.integrations.langsmith:create_langsmith_sandbox"]
        ModalSB["agent.integrations.modal:create_modal_sandbox"]
    end
    
    subgraph "agent/tools/ - Tool Suite"
        ExecuteTool["execute tool"]
        HTTPTool["http_request tool"]
        LinearTool["linear_comment tool"]
        SlackTool["slack_thread_reply tool"]
    end
    
    SlackMention --> SlackEndpoint
    LinearComment --> LinearEndpoint
    GitHubComment --> GitHubEndpoint
    
    SlackEndpoint --> MainAgent
    LinearEndpoint --> MainAgent
    GitHubEndpoint --> MainAgent
    
    MainAgent --> GetAgent
    GetAgent --> SandboxState
    GetAgent --> CreateDeepAgent
    
    SandboxState --> SandboxFactory
    SandboxFactory --> LangSmithSB
    SandboxFactory --> ModalSB
    
    CreateDeepAgent --> ExecuteTool
    CreateDeepAgent --> HTTPTool
    CreateDeepAgent --> LinearTool
    CreateDeepAgent --> SlackTool
```

**Key Code Symbols:**
- **`handle_slack_event()`**: [agent/webapp.py]() - Slack webhook handler.
- **`get_agent()`**: [agent/server.py:40]() - Main agent graph factory.
- **`ensure_sandbox_for_thread()`**: [agent/server.py:40]() - Sandbox lifecycle manager.
- **`create_sandbox()`**: [agent/utils/sandbox.py:55]() - Sandbox provider dispatcher.
- **`create_deep_agent()`**: [README.md:43-50]() - Framework assembly call.

**Sources:** [README.md:33-113](), [AGENTS.md:26-55](), [CUSTOMIZATION.md:3-24]()

---

## Request Lifecycle

The following diagram shows how a single request flows through the system, emphasizing the interaction between the FastAPI webhooks and the LangGraph agent:

```mermaid
sequenceDiagram
    participant User as "User (Slack/Linear/GitHub)"
    participant Webapp as "agent/webapp.py<br/>(FastAPI)"
    participant LG as "LangGraph Server<br/>(agent/server.py)"
    participant Sandbox as "SandboxBackendProtocol<br/>(agent/integrations/)"
    participant Agent as "Deep Agent Loop"
    
    User->>Webapp: POST /webhooks/... (@openswe)
    Webapp->>Webapp: Resolve deterministic thread_id
    Webapp->>LG: client.runs.create(thread_id)
    
    LG->>LG: get_agent(config)
    LG->>Sandbox: ensure_sandbox_for_thread()
    Note over Sandbox: Create or Reconnect
    
    LG->>Agent: Start execution loop
    
    loop Tool Interaction
        Agent->>Agent: check_message_queue_before_model
        Agent->>Sandbox: execute("pytest ...")
        Sandbox-->>Agent: Exit code + Output
        Agent->>Sandbox: write_file("app.py", ...)
    end
    
    Agent->>Webapp: slack_thread_reply / linear_comment
    Webapp-->>User: "I've opened a PR: ..."
```

**Key Functions in Order:**
1. **Webhook Processing**: [agent/webapp.py:43]() - Resolves `thread_id` and triggers runs.
2. **`get_agent(config)`**: [agent/server.py:40]() - Entrypoint that configures the agent instance.
3. **`ensure_sandbox_for_thread()`**: [AGENTS.md:48-55]() - Handles sandbox caching and persistence.
4. **`check_message_queue_before_model`**: [AGENTS.md:66-67]() - Middleware that pulls new messages mid-run.
5. **Tool Execution**: [README.md:70-76]() - Agent performs work inside the sandbox.

**Sources:** [README.md:86-107](), [AGENTS.md:38-71](), [CUSTOMIZATION.md:3-24]()

---

## Core Components

Open SWE consists of four primary layers:

### API Layer ([agent/webapp.py]())
FastAPI application that receives webhooks from Slack, Linear, and GitHub. It manages signature verification and maps platform-specific events to deterministic LangGraph threads. [AGENTS.md:43-44]()

### Orchestration Layer ([agent/server.py]())
Defines the `get_agent()` factory which resolves GitHub tokens, manages sandbox state via `SANDBOX_BACKENDS`, and constructs the system prompt. [AGENTS.md:40]()

### Agent Core (Deep Agents Framework)
The framework providing the `create_deep_agent` assembly, which bundles the LLM, tools, and sandboxes into an execution loop. [README.md:38-50]()

### Execution Layer ([agent/integrations/]())
Implementations of `SandboxBackendProtocol` that provide isolated environments. Providers like LangSmith include a GitHub proxy to safely inject credentials into the sandbox. [CUSTOMIZATION.md:28-52](), [AGENTS.md:55-58]()

**Sources:** [README.md:38-63](), [AGENTS.md:36-58](), [CUSTOMIZATION.md:3-24]()

---

## Key Files and Entry Points

| Concept | Primary File(s) | Key Functions/Classes |
|---------|----------------|----------------------|
| **Webhook Entry** | [agent/webapp.py]() | `handle_slack_event`, `handle_linear_webhook` |
| **Agent Factory** | [agent/server.py]() | `get_agent`, `ensure_sandbox_for_thread` |
| **Reviewer Graph** | [agent/reviewer.py]() | `get_reviewer_agent` |
| **Sandbox Integrations** | [agent/integrations/]() | `create_langsmith_sandbox`, `create_modal_sandbox` |
| **Custom Tools** | [agent/tools/]() | `execute`, `linear_comment`, `slack_thread_reply` |
| **Middleware Hooks** | [agent/middleware/]() | `check_message_queue_before_model`, `ToolErrorMiddleware` |

**Sources:** [AGENTS.md:38-86](), [CUSTOMIZATION.md:58-64]()

---

## What's Next

For deeper dives into specific areas:

- **[System Architecture](#1.1)**: Complete flow from webhooks to tool execution.
- **[Technology Stack](#1.2)**: Python backend, LangGraph orchestration, and deployment.
- **[Framework Composition](#1.3)**: How Open SWE layers on Deep Agents and LangGraph.

**Sources:** [README.md:1-150]()

---

# Page: System Architecture

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CUSTOMIZATION.md](CUSTOMIZATION.md)
- [INSTALLATION.md](INSTALLATION.md)
- [Makefile](Makefile)
- [README.md](README.md)
- [agent/middleware/exclude_tools.py](agent/middleware/exclude_tools.py)
- [agent/server.py](agent/server.py)
- [agent/tools/__init__.py](agent/tools/__init__.py)
- [evals/reviewer/judge.py](evals/reviewer/judge.py)
- [langgraph.json](langgraph.json)

</details>



## Purpose and Scope

Open SWE is an open-source framework for building internal coding agents that operate within isolated cloud sandboxes. It is designed to compose on [LangGraph](https://langchain-ai.github.io/langgraph/) and [Deep Agents](https://github.com/langchain-ai/deepagents), providing a robust architecture for repository management, tool execution, and multi-surface invocation (Slack, Linear, GitHub) [README.md:25-40]().

This document details the high-level system architecture, focusing on the flow from external webhooks to agent orchestration and sandbox execution.

## High-Level Architecture

Open SWE follows a modular architecture where the agent logic is decoupled from the execution environment and the invocation surface.

```mermaid
graph TB
    subgraph "Invocation Surfaces"
        slack["Slack App"]
        linear["Linear Webhook"]
        github["GitHub App"]
    end

    subgraph "Web Application (FastAPI)"
        webapp["webapp.py<br/>(Webhook Endpoints)"]
        auth["auth.py<br/>(Token Resolution)"]
    end

    subgraph "Agent Core (LangGraph)"
        server["server.py<br/>(get_agent)"]
        deepagent["Deep Agent Core<br/>(create_deep_agent)"]
        middleware["Middleware Stack<br/>(check_message_queue, notify_step_limit)"]
    end

    subgraph "Sandbox Layer"
        sb_factory["sandbox.py<br/>(Factory)"]
        provider["Sandbox Provider<br/>(LangSmith, Modal, etc.)"]
        git_util["github.py<br/>(Git/Repo Management)"]
    end

    slack --> webapp
    linear --> webapp
    github --> webapp

    webapp --> auth
    webapp --> server
    
    server --> deepagent
    deepagent --> middleware
    deepagent --> sb_factory
    
    sb_factory --> provider
    provider --> git_util
```

**Sources:** [README.md:34-108](), [agent/server.py:29-69](), [langgraph.json:10-12]()

## Natural Language to Code Entity Mapping

The following diagrams bridge the gap between high-level concepts and specific code implementations.

### Webhook Processing Flow
When an event occurs in an external system, it hits a specific route in `agent/webapp.py`, which then interacts with the LangGraph server. The server invokes the graph defined by `get_agent` in `agent/server.py` [langgraph.json:4-5]().

```mermaid
sequenceDiagram
    participant Ext as "External (Slack/Linear/GitHub)"
    participant Web as "agent/webapp.py"
    participant Auth as "agent/utils/auth.py"
    participant LG as "LangGraph Server"
    participant Srv as "agent/server.py"

    Ext->>Web: POST /webhooks/(provider)
    Web->>Web: verify_(provider)_signature()
    Web->>Auth: resolve_github_token()
    Web->>LG: client.runs.create(thread_id, ...)
    LG->>Srv: get_agent(config)
    Srv->>Srv: create_deep_agent(...)
```
**Sources:** [agent/webapp.py:1-12](), [agent/server.py:29-83](), [agent/utils/auth.py:70](), [langgraph.json:4-12]()

### Agent and Sandbox Lifecycle
The `get_agent()` function in `agent/server.py` is the central assembly point. It configures the sandbox and proxy authentication before returning the compiled agent [agent/server.py:29-80]().

```mermaid
graph LR
    subgraph "agent/server.py"
        GA["get_agent()"]
        CSP["_create_sandbox_with_proxy()"]
        RGP["_refresh_github_proxy()"]
    end

    subgraph "agent/utils/sandbox.py"
        CS["create_sandbox()"]
    end

    subgraph "agent/integrations/"
        LS["langsmith.py"]
        DT["daytona.py"]
    end

    GA --> CSP
    GA --> RGP
    CSP --> CS
    CS --> LS
    CS --> DT
    GA -->|"execute"| SB["Cloud Sandbox"]
```
**Sources:** [agent/server.py:121-139](), [agent/server.py:142-161](), [agent/utils/sandbox.py:80](), [CUSTOMIZATION.md:30-64]()

## Core Components

### 1. Agent Assembly
The agent is constructed using `create_deep_agent` from the `deepagents` framework. It is configured with a specific LLM model, a system prompt, a curated toolset, and a middleware stack [agent/server.py:29-69](), [CUSTOMIZATION.md:5-23]().

| Component | Code Reference | Description |
| :--- | :--- | :--- |
| **Model** | `make_model()` | Wraps `init_chat_model` for dynamic provider selection [agent/utils/model.py:77](). |
| **System Prompt** | `construct_system_prompt()` | Injects `AGENTS.md` and source context [agent/server.py:54](). |
| **Tools** | `agent/tools/` | Includes `fetch_url`, `http_request`, `linear_comment`, `slack_thread_reply`, etc [agent/tools/__init__.py:1-37](). |
| **Middleware** | `agent/middleware/` | Handles tool errors, message queuing, and status notifications [agent/server.py:44-53](). |

**Sources:** [agent/server.py:29-69](), [CUSTOMIZATION.md:5-23](), [agent/tools/__init__.py:1-37]()

### 2. Sandbox Management
Open SWE supports multiple sandbox providers (LangSmith, Modal, Daytona, Runloop, Local) [CUSTOMIZATION.md:58-64](). The `SandboxBackendProtocol` ensures a consistent interface for file operations and shell execution [agent/server.py:31]().

- **Isolation**: Each thread receives a persistent sandbox reused across follow-up messages [README.md:60]().
- **Persistence**: Sandbox IDs are managed via `get_sandbox_id_from_metadata` and `set_sandbox_backend` [agent/server.py:91-92]().
- **Auth Proxy**: For LangSmith sandboxes, `_configure_github_proxy` injects GitHub App installation tokens into the sandbox environment [agent/server.py:131-137]().

**Sources:** [agent/server.py:97-177](), [agent/utils/sandbox.py:80](), [CUSTOMIZATION.md:28-64]()

### 3. Reviewer Agent
In addition to the main coding agent, the system includes a `reviewer` graph [langgraph.json:6](). This agent uses a specialized `get_reviewer_agent()` factory and findings-management tools like `add_finding` and `list_findings` [agent/tools/__init__.py:20-30](). It also utilizes `ExcludeToolsMiddleware` to strip unnecessary tools (like `task`) from the reviewer's capabilities [agent/middleware/exclude_tools.py:33-43]().

**Sources:** [langgraph.json:6](), [agent/tools/__init__.py:20-30](), [agent/middleware/exclude_tools.py:33-43]()

### 4. Middleware and Orchestration
The system uses deterministic middleware hooks to extend agent behavior:
- **`check_message_queue_before_model`**: Injects new user messages into the current agent loop before the next model call [agent/server.py:50]().
- **`notify_step_limit_reached`**: Informs the user via Slack if the agent hits its maximum model call limit [agent/server.py:52]().
- **`ToolErrorMiddleware`**: Catches and handles tool execution errors gracefully [agent/server.py:49]().

**Sources:** [agent/server.py:44-53](), [README.md:91-96]()

---

# Page: Technology Stack

# Technology Stack

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [.github/workflows/pr_lint.yml](.github/workflows/pr_lint.yml)
- [LICENSE](LICENSE)
- [agent/integrations/langsmith.py](agent/integrations/langsmith.py)
- [pyproject.toml](pyproject.toml)
- [ui/package.json](ui/package.json)
- [ui/src/components/AppSidebar.tsx](ui/src/components/AppSidebar.tsx)
- [ui/yarn.lock](ui/yarn.lock)
- [uv.lock](uv.lock)

</details>



## Purpose and Scope

This document provides a comprehensive reference for all technologies, frameworks, and tools used in the Open SWE codebase. It covers the frontend dashboard (React/TanStack), backend services (Python/FastAPI), orchestration layer (LangGraph), AI/ML services, build tools, and deployment infrastructure.

For information about how these technologies are assembled into system components, see [System Architecture](#1.1). For deployment configurations and environment setup, see [Environment Configuration](#11.1).

---

## Technology Stack Overview

Open SWE employs a polyglot architecture with distinct technology layers serving specific purposes:

```mermaid
graph TB
    subgraph "Frontend_Layer"["Frontend Layer (ui/)"]
        React["React 19"]
        TanStack["TanStack Router & Query"]
        Vite["Vite Build Tool"]
        Tailwind["Tailwind CSS 4"]
    end
    
    subgraph "API_Layer"["API Layer (agent/webapp.py)"]
        FastAPI["FastAPI"]
        Uvicorn["Uvicorn ASGI"]
    end
    
    subgraph "Agent_Backend"["Agent Backend (agent/)"]
        LangGraph["LangGraph Orchestration"]
        DeepAgents["Deep Agents Framework"]
        Python["Python 3.11+"]
    end
    
    subgraph "AI_ML_Services"["AI/ML Services"]
        Anthropic["Anthropic Claude 3.5 Sonnet"]
        LangSmith["LangSmith Tracing & Ops"]
    end
    
    subgraph "Build_Tools"["Build Tools"]
        UV["UV (Python)"]
        Yarn["Yarn (JS)"]
        Ruff["Ruff Linter/Formatter"]
    end
    
    subgraph "Execution_Environments"["Execution Environments"]
        LSBox["LangSmith Sandbox"]
        Modal["Modal Sandbox"]
        Daytona["Daytona"]
        Runloop["Runloop"]
        Local["Local Subprocess"]
    end
    
    FastAPI --> LangGraph
    LangGraph --> DeepAgents
    DeepAgents --> Anthropic
    DeepAgents --> LSBox
    DeepAgents --> Modal
    
    React --> FastAPI
    UV --> Python
    Yarn --> React
```

**Sources:** [pyproject.toml:1-28](), [ui/package.json:1-45](), [agent/integrations/langsmith.py:12-13]()

---

## Frontend Stack

### Dashboard Application

The frontend is a modern Single Page Application (SPA) located in the `ui/` directory, built using **React 19** and the **TanStack** ecosystem.

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | React | ^19.2.4 | UI Component library [ui/package.json:33]() |
| **Routing** | TanStack Router | ^1.167.4 | Type-safe client-side routing [ui/package.json:23]() |
| **Data Fetching** | TanStack Query | ^5.100.10 | Async state management [ui/package.json:21]() |
| **Styling** | Tailwind CSS | ^4.2.1 | Utility-first CSS framework [ui/package.json:42]() |
| **Build Tool** | Vite | ^7.3.1 | Frontend build pipeline [ui/package.json:59]() |
| **Icons** | Phosphor / Lucide | - | Icon sets [ui/package.json:17](), [ui/package.json:31]() |

**Key Navigation Structure:**
The `AppSidebar` defines the primary navigation surfaces for the dashboard:
- **My Settings**: User-specific overrides [ui/src/components/AppSidebar.tsx:31]()
- **Cloud Agents**: Agent management interface [ui/src/components/AppSidebar.tsx:32]()
- **Open SWE Review**: Automated PR reviewer interface [ui/src/components/AppSidebar.tsx:33]()
- **Integrations**: Platform connection management [ui/src/components/AppSidebar.tsx:34]()

**Sources:** [ui/package.json:14-45](), [ui/src/components/AppSidebar.tsx:30-36]()

---

## Backend Stack

### Python Runtime and Framework

The backend is built with **Python 3.11+** and uses **FastAPI** for its high-performance asynchronous capabilities.

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Runtime** | Python 3.11+ | Core language runtime [pyproject.toml:6]() |
| **Web Framework** | FastAPI | REST API and Webhook endpoints [pyproject.toml:10]() |
| **ASGI Server** | Uvicorn | Production-grade web server [pyproject.toml:11]() |
| **HTTP Client** | HTTPX | Asynchronous HTTP requests [pyproject.toml:12]() |
| **Security** | PyJWT / Cryptography | Token handling and encryption [pyproject.toml:13-14]() |

**Sources:** [pyproject.toml:1-28]()

---

## Orchestration Layer

### LangGraph Framework

**LangGraph** is the core orchestration engine used to define the agent's control flow as a stateful graph.

```mermaid
graph LR
    subgraph "LangGraph_Engine"["LangGraph Engine"]
        StateGraph["StateGraph (agent/server.py)"]
        Checkpointer["Checkpointer (Persistence)"]
        SDK["LangGraph SDK"]
    end
    
    subgraph "Agent_Logic"["Agent Logic"]
        DeepAgent["Deep Agent Assembly"]
        Reviewer["Reviewer Graph"]
    end
    
    StateGraph --> DeepAgent
    StateGraph --> Reviewer
    SDK --> StateGraph
```

- **State Management**: LangGraph manages the propagation of state across agent turns [pyproject.toml:17]().
- **Persistence**: Thread state is persisted via checkpointers, allowing agents to resume long-running tasks.
- **SDK Integration**: The system utilizes `langgraph-sdk` to interact with the LangGraph server [pyproject.toml:15]().

**Sources:** [pyproject.toml:15-17]()

### Deep Agents Framework

Open SWE composes on the **Deep Agents** library to provide high-level agent abstractions:
- **Agent Assembly**: Uses `create_deep_agent` to combine LLMs, tools, and middleware [pyproject.toml:9]().
- **Tool Suite**: Provides standard SWE tools like `read_file`, `edit_file`, and `ls`.
- **Middleware**: Supports standard hooks for pre/post processing of agent turns.

**Sources:** [pyproject.toml:9]()

---

## AI/ML Services

### Large Language Models (LLMs)

Open SWE is model-agnostic but optimized for top-tier reasoning models.

| Provider | Library | Primary Usage |
|----------|---------|---------------|
| **Anthropic** | `langchain-anthropic` | Claude 3.5 Sonnet (Primary Agent) [pyproject.toml:19]() |
| **OpenAI** | `langchain-openai` | GPT-4o (Alternative/Reviewer) [pyproject.toml:22]() |
| **Google** | `langchain-google-genai` | Gemini 1.5 Pro (Alternative) [pyproject.toml:27]() |

### Observability and Tracing

- **LangSmith**: Used for full-stack tracing of agent runs, evaluation, and performance monitoring [pyproject.toml:21]().

**Sources:** [pyproject.toml:19-27]()

---

## Build Tools and Package Management

### Python Package Management - UV

Open SWE uses **UV** for extremely fast dependency resolution and virtual environment management.

```mermaid
graph TB
    subgraph "UV_Workflow"["UV Workflow"]
        uv_lock["uv.lock (Lockfile)"]
        uv_sync["uv sync (Installation)"]
    end
    
    subgraph "CI_Pipeline"["CI Pipeline (.github/workflows/ci.yml)"]
        setup_uv["astral-sh/setup-uv"]
        run_sync["uv sync --locked --extra dev"]
    end
    
    uv_lock --> uv_sync
    setup_uv --> run_sync
    run_sync --> uv_sync
```

- **Locking**: Deterministic builds are ensured via `uv.lock` [uv.lock:1-7]().
- **Linting/Formatting**: Managed by **Ruff**, which is configured for high-performance linting [pyproject.toml:48-61]().

**Sources:** [uv.lock:1-7](), [pyproject.toml:48-61](), [.github/workflows/ci.yml:22-24]()

### JavaScript Package Management - Yarn

The frontend uses **Yarn** for dependency management [ui/yarn.lock:1-2]().

---

## Execution Environments (Sandboxes)

Open SWE abstracts code execution into "Sandboxes" to safely run agent-generated code.

| Provider | Library | Type |
|----------|---------|------|
| **LangSmith** | `deepagents.backends.LangSmithSandbox` | Docker-based (Primary) [agent/integrations/langsmith.py:12]() |
| **Daytona** | `langchain-daytona` | Development containers [pyproject.toml:23]() |
| **Modal** | `langchain-modal` | Serverless functions [pyproject.toml:24]() |
| **Runloop** | `langchain-runloop` | Managed environments [pyproject.toml:25]() |

### LangSmith Sandbox Implementation
The `LangSmithProvider` manages the lifecycle of LangSmith sandboxes, including:
- **Snapshot Configuration**: Setting CPU, memory, and storage limits [agent/integrations/langsmith.py:18-22]().
- **GitHub Proxy**: Configuring proxy rules to inject GitHub credentials for secure `git` operations without storing tokens on the sandbox disk [agent/integrations/langsmith.py:70-95]().

**Sources:** [agent/integrations/langsmith.py:12-95](), [pyproject.toml:23-25]()

---

## CI/CD Pipeline

The project uses **GitHub Actions** for continuous integration.

| Pipeline | Trigger | Tasks |
|----------|---------|-------|
| **Agent CI** | Push to `main`, PRs | Linting, Formatting check, Unit tests [ .github/workflows/ci.yml:1-49]() |
| **PR Title Lint** | PR Open/Edit | Validates semantic PR titles (feat, fix, etc.) [.github/workflows/pr_lint.yml:1-42]() |

**Sources:** [.github/workflows/ci.yml:1-49](), [.github/workflows/pr_lint.yml:1-42]()

---

# Page: Framework Composition

# Framework Composition

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CUSTOMIZATION.md](CUSTOMIZATION.md)
- [INSTALLATION.md](INSTALLATION.md)
- [README.md](README.md)
- [agent/server.py](agent/server.py)
- [agent/tools/__init__.py](agent/tools/__init__.py)

</details>



## Purpose and Scope

Open SWE is designed as a modular system that composes on top of the **Deep Agents** and **LangGraph** frameworks rather than forking them. This approach allows the codebase to remain lightweight while inheriting robust agent orchestration and workflow execution capabilities. This page documents the three-layer architecture, the assembly process via `create_deep_agent`, and the specific extension points where Open SWE adds domain-specific logic.

---

## Three-Layer Architecture

Open SWE implements a compositional architecture with three distinct layers, each providing different levels of abstraction:

### Three-Layer Architecture Diagram
```mermaid
graph TB
    subgraph Layer1["Layer 1: Open SWE - Domain Logic"]
        webhooks["[agent/webapp.py] Webhook Handlers"]
        customTools["[agent/tools/*] Custom Tools"]
        customMiddleware["[agent/middleware.py] Custom Middleware"]
        sandboxProviders["[agent/integrations/*] Sandbox Providers"]
        promptEngineering["[agent/prompt.py] Context Assembly"]
        authSystem["[agent/utils/auth.py] Authentication"]
    end
    
    subgraph Layer2["Layer 2: Deep Agents - Agent Framework"]
        createAgent["create_deep_agent()"]
        builtinTools["Built-in Tools: read_file, write_file, edit_file, ls, glob, grep, task"]
        agentOrchestration["Agent Orchestration & Subagent Management"]
        toolMiddleware["ToolErrorMiddleware"]
    end
    
    subgraph Layer3["Layer 3: LangGraph - Workflow Engine"]
        pregel["Pregel Execution & StateGraph"]
        checkpointing["Checkpointing & State"]
        streaming["Streaming Output"]
    end
    
    webhooks -->|"invokes"| createAgent
    customTools -->|"passed to"| createAgent
    customMiddleware -->|"passed to"| createAgent
    sandboxProviders -->|"passed to"| createAgent
    promptEngineering -->|"passed to"| createAgent
    
    createAgent -->|"returns"| pregel
    builtinTools -->|"included by"| createAgent
    agentOrchestration -->|"managed by"| pregel
    toolMiddleware -->|"extends"| customMiddleware
    
    pregel -->|"uses"| checkpointing
    pregel -->|"uses"| streaming
```
Sources: [README.md:33-50](), [agent/server.py:29-53](), [agent/server.py:249-376]()

*   **Layer 3 - LangGraph (Foundation)**: Provides the workflow execution engine and state management. Open SWE uses LangGraph's `Pregel` executor to manage the agent loop and state transitions [agent/server.py:13-14]().
*   **Layer 2 - Deep Agents (Agent Framework)**: Provides the `create_deep_agent()` assembly function [agent/server.py:29](). It includes built-in file system tools and subagent orchestration via the `task` tool [README.md:76-77]().
*   **Layer 1 - Open SWE (Domain Logic)**: Adds webhook handlers, custom tools (Slack, Linear, GitHub), custom middleware for message queueing, and context engineering logic [README.md:52-110]().

---

## Agent Assembly via create_deep_agent()

The core composition happens in the `get_agent()` function [agent/server.py:249](), which assembles an agent by calling `create_deep_agent` with parameters tailored to the specific run.

### Agent Assembly Component Mapping
```mermaid
graph LR
    getAgent["[agent/server.py] get_agent()"]
    
    model["model: make_model()"]
    systemPrompt["system_prompt: construct_system_prompt()"]
    tools["tools list"]
    backend["backend: SandboxBackendProtocol"]
    middleware["middleware list"]
    
    customTools["Custom Tools: linear_comment, slack_thread_reply, fetch_url, http_request"]
    
    builtinTools["Built-in Tools: read_file, write_file, edit_file, ls, glob, grep, task"]
    
    customMiddleware["Custom Middleware: check_message_queue_before_model, notify_step_limit_reached, ToolErrorMiddleware"]
    
    createAgent["create_deep_agent()"]
    pregel["Pregel Agent Instance"]
    
    getAgent --> model
    getAgent --> systemPrompt
    getAgent --> tools
    getAgent --> backend
    getAgent --> middleware
    
    customTools -->|"merged with"| builtinTools
    builtinTools --> tools
    
    customMiddleware --> middleware
    
    model --> createAgent
    systemPrompt --> createAgent
    tools --> createAgent
    backend --> createAgent
    middleware --> createAgent
    
    createAgent --> pregel
```
Sources: [agent/server.py:249-376](), [README.md:42-49](), [agent/tools/__init__.py:1-37]()

The assembly process in `agent/server.py` follows this implementation:

```python
# agent/server.py:362-372
return create_deep_agent(
    model=make_model(model_id, **model_kwargs),
    system_prompt=construct_system_prompt(...),
    tools=[
        http_request, 
        fetch_url, 
        linear_comment, 
        slack_thread_reply,
        # ... other custom tools
    ],
    backend=sandbox_backend,
    middleware=[
        ToolErrorMiddleware(),
        check_message_queue_before_model,
        ensure_no_empty_msg,
        notify_step_limit_reached,
    ],
)
```

The `create_deep_agent` function from Deep Agents performs the following:
*   Combines the provided tools with built-in file operations (`read_file`, `write_file`, `edit_file`, etc.) [README.md:76-77]().
*   Injects the `task` tool to allow the agent to spawn subagents [README.md:89-90]().
*   Configures the middleware stack around the LLM call loop [README.md:91-96]().

---

## Component Extension Points

Open SWE extends the base frameworks at four key extension points:

### 1. Sandbox Providers
All sandbox implementations must adhere to the `SandboxBackendProtocol` from Deep Agents [agent/server.py:31](). This allows Open SWE to swap between providers like LangSmith, Modal, or Daytona by setting the `SANDBOX_TYPE` environment variable [CUSTOMIZATION.md:58-64]().

### 2. Custom Tools
Custom tools extend the agent's capability beyond file manipulation. These are defined in `agent/tools/` and passed to the agent factory [agent/tools/__init__.py:1-37]().

| Tool | Purpose | File |
|------|---------|------|
| `linear_comment` | Post updates to Linear tickets | `agent/tools/linear_comment.py` |
| `slack_thread_reply` | Reply in Slack threads | `agent/tools/slack_thread_reply.py` |
| `fetch_url` | Fetch web pages as markdown | `agent/tools/fetch_url.py` |
| `http_request` | Perform generic API calls | `agent/tools/http_request.py` |

### 3. Custom Middleware
Middleware functions are used to intercept the agent loop [agent/middleware.py]().
*   **`check_message_queue_before_model`**: Injects new user messages (e.g., from Slack while the agent is running) into the conversation history before the next LLM turn [agent/server.py:50]().
*   **`notify_step_limit_reached`**: Handles notifications when an agent hits its execution budget [agent/server.py:52]().

### 4. Context Engineering
Open SWE specializes in assembling context from repository-specific files like `AGENTS.md` and source metadata from Slack or Linear [README.md:78-84](). This context is injected into the system prompt via `construct_system_prompt` [agent/server.py:54]().

---

## Benefits of Composition

Composing on frameworks rather than forking provides several architectural advantages:

1.  **Upgrade Path**: Open SWE can pull upstream improvements from Deep Agents and LangGraph (e.g., better tool error handling or execution speed) without merge conflicts [README.md:40]().
2.  **Tool Curation**: Open SWE focuses on "tool curation" (providing high-value domain tools) rather than "tool accumulation" (building a massive library of generic tools) [README.md:66]().
3.  **Separation of Concerns**:
    *   **LangGraph** handles state and execution logic.
    *   **Deep Agents** handles the agent loop and basic file tools.
    *   **Open SWE** handles the integration with external developer tools (Slack, Linear, GitHub) and sandbox management.

Sources: [README.md:33-50](), [README.md:66-96](), [agent/server.py:249-376](), [CUSTOMIZATION.md:5-24]()

---

# Page: Invocation Surfaces

# Invocation Surfaces

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CUSTOMIZATION.md](CUSTOMIZATION.md)
- [INSTALLATION.md](INSTALLATION.md)
- [README.md](README.md)
- [agent/webapp.py](agent/webapp.py)
- [tests/test_github_issue_webhook.py](tests/test_github_issue_webhook.py)

</details>



This document covers the multiple entry points through which users can trigger Open SWE agents. An **invocation surface** is a platform where users mention `@openswe` to start or interact with an agent run. Open SWE supports three primary surfaces: Slack, Linear, and GitHub, each implemented as a FastAPI webhook endpoint.

For detailed information about each surface's setup and behavior, see:
- Slack usage: [Slack Integration](#2.1)
- Linear usage: [Linear Integration](#2.2)  
- GitHub usage: [GitHub Integration](#2.3)
- Technical webhook processing details: [Webhook Processing Flow](#2.4)

For information about how agents are assembled and executed after invocation, see [Agent Core](#3).

---

## Supported Invocation Surfaces

Open SWE provides three webhook-based invocation surfaces, each listening for platform-specific events:

| Surface | Trigger Pattern | Webhook Endpoint | Event Types | Primary Use Case |
|---------|----------------|------------------|-------------|------------------|
| **Slack** | `@openswe` mention in thread | `POST /webhooks/slack` | `app_mention`, `message.im`, `message.mpim` | Real-time collaboration, quick tasks, status updates |
| **Linear** | `@openswe` in issue comment | `POST /webhooks/linear` | Comment → Create | Issue tracking integration, feature requests, bug fixes |
| **GitHub** | `@openswe` in issue or PR comment | `POST /webhooks/github` | `issues`, `issue_comment`, `pull_request_review`, `pull_request_review_comment` | PR review feedback, issue resolution |

Each surface triggers the same underlying agent system but provides different context and routing mechanisms.

**Sources:** [README.md:98-106](), [agent/webapp.py:833-1134]()

---

## Webhook Endpoint Architecture

```mermaid
graph TB
    subgraph "FastAPI Application (agent/webapp.py)"
        App["FastAPI app"]
        
        SlackEP["POST /webhooks/slack<br/>slack_webhook()"]
        LinearEP["POST /webhooks/linear<br/>linear_webhook()"]
        GitHubEP["POST /webhooks/github<br/>github_webhook()"]
        
        LinearGET["GET /webhooks/linear<br/>linear_webhook_verify()"]
        
        App --> SlackEP
        App --> LinearEP
        App --> GitHubEP
        App --> LinearGET
    end
    
    subgraph "Signature Verification"
        SlackSig["verify_slack_signature()<br/>HMAC-SHA256 with timestamp"]
        LinearSig["verify_linear_signature()<br/>HMAC-SHA256"]
        GitHubSig["verify_github_signature()<br/>X-Hub-Signature-256"]
        
        SlackEP --> SlackSig
        LinearEP --> LinearSig
        GitHubEP --> GitHubSig
    end
    
    subgraph "Processing Functions"
        ProcessSlack["process_slack_mention()<br/>Builds thread context"]
        ProcessLinear["process_linear_issue()<br/>Fetches full issue"]
        ProcessGitHub["process_github_issue()<br/>Handles issues + PRs"]
        
        SlackSig --> ProcessSlack
        LinearSig --> ProcessLinear
        GitHubSig --> ProcessGitHub
    end
    
    subgraph "Repository Resolution"
        SlackRepo["get_slack_repo_config()<br/>Parse 'repo:owner/name'<br/>or use defaults"]
        LinearRepo["get_repo_config_from_team_mapping()<br/>LINEAR_TEAM_TO_REPO lookup"]
        GitHubRepo["Extract from webhook payload<br/>repository.owner/name"]
        
        ProcessSlack --> SlackRepo
        ProcessLinear --> LinearRepo
        ProcessGitHub --> GitHubRepo
    end
    
    subgraph "Thread ID Generation"
        SlackThread["generate_thread_id_from_slack_thread()<br/>MD5(channel_id:thread_ts)"]
        LinearThread["generate_thread_id_from_issue()<br/>SHA256('linear-issue:{id}')"]
        GitHubThread["generate_thread_id_from_github_issue()<br/>SHA256('github-issue:{id}')<br/>OR get_thread_id_from_branch()"]
        
        SlackRepo --> SlackThread
        LinearRepo --> LinearThread
        GitHubRepo --> GitHubThread
    end
    
    subgraph "Concurrency Check"
        ThreadActive["is_thread_active(thread_id)<br/>Check thread status == 'busy'"]
        
        SlackThread --> ThreadActive
        LinearThread --> ThreadActive
        GitHubThread --> ThreadActive
    end
    
    subgraph "Run Creation or Queueing"
        QueueMsg["queue_message_for_thread()<br/>Store in LangGraph Store"]
        CreateRun["langgraph_client.runs.create()<br/>thread_id, configurable"]
        
        ThreadActive -->|busy| QueueMsg
        ThreadActive -->|idle| CreateRun
    end
```

**Diagram: Webhook Processing Pipeline**

Each webhook endpoint follows the same pattern: verify signature → extract context → generate thread ID → check thread status → create run or queue message. The differences lie in how each surface assembles context and resolves the target repository.

**Sources:** [agent/webapp.py:833-1134](), [agent/webapp.py:390-479](), [agent/webapp.py:239-268]()

---

## Thread ID Generation Strategy

Thread IDs are deterministic identifiers that route follow-up messages to the same agent run. Each surface uses a different algorithm:

```mermaid
graph LR
    subgraph "Slack Thread ID"
        SlackInput["channel_id: C12345<br/>thread_ts: 1234567890.123456"]
        SlackHash["MD5 hash of<br/>'C12345:1234567890.123456'"]
        SlackUUID["UUID format:<br/>12345678-1234-1234-1234-123456789012"]
        
        SlackInput --> SlackHash
        SlackHash --> SlackUUID
    end
    
    subgraph "Linear Thread ID"
        LinearInput["issue_id:<br/>'abc-def-123'"]
        LinearHash["SHA256 hash of<br/>'linear-issue:abc-def-123'"]
        LinearUUID["UUID format from first 32 hex chars:<br/>abcdef12-3456-7890-abcd-ef1234567890"]
        
        LinearInput --> LinearHash
        LinearHash --> LinearUUID
    end
    
    subgraph "GitHub Thread ID"
        GitHubInput["issue_id: 12345<br/>OR<br/>branch_name containing UUID"]
        GitHubHash["SHA256 hash of<br/>'github-issue:12345'<br/>OR<br/>regex extract UUID from branch"]
        GitHubUUID["UUID format:<br/>fedcba98-7654-3210-fedc-ba9876543210"]
        
        GitHubInput --> GitHubHash
        GitHubHash --> GitHubUUID
    end
```

**Diagram: Thread ID Generation by Surface**

| Surface | Source | Algorithm | Purpose |
|---------|--------|-----------|---------|
| **Slack** | `channel_id:thread_ts` | MD5 hash → UUID | Route replies within same thread |
| **Linear** | `issue_id` | SHA256 hash → UUID | Link comments on same issue |
| **GitHub (Issues)** | `issue.id` | SHA256 hash → UUID | Connect issue comments |
| **GitHub (PRs)** | Branch name regex | Extract existing UUID | Connect PR review comments to original thread |

The GitHub PR surface uses a special strategy: agent-created branches contain the thread ID in the branch name (e.g., `fix-bug-abc123de-1234-5678-9abc-def012345678`), allowing `get_thread_id_from_branch()` to extract it and route PR review comments back to the original thread.

**Sources:** [agent/webapp.py:239-268](), [agent/utils/github_comments.py:53]()

---

## Concurrency Handling and Message Queueing

When a user sends a follow-up message while an agent is still processing the previous one, Open SWE queues the new message instead of rejecting it or creating a duplicate run:

```mermaid
sequenceDiagram
    participant User
    participant Webhook as "Webhook Endpoint"
    participant ThreadCheck as "is_thread_active()"
    participant LGClient as "LangGraph Client"
    participant Store as "LangGraph Store<br/>(queue, thread_id)"
    participant Middleware as "check_message_queue_before_model"
    participant Agent as "Agent Execution"

    User->>Webhook: @openswe follow-up message
    Webhook->>Webhook: generate_thread_id()
    Webhook->>ThreadCheck: Check status for thread_id
    ThreadCheck->>LGClient: threads.get(thread_id)
    LGClient-->>ThreadCheck: status = "busy"
    ThreadCheck-->>Webhook: True (active)
    
    Webhook->>Webhook: queue_message_for_thread()
    Webhook->>Store: store.get_item(("queue", thread_id), "pending_messages")
    Store-->>Webhook: existing_messages = [msg1, msg2]
    Webhook->>Webhook: Append new message to list
    Webhook->>Store: store.put_item(("queue", thread_id), "pending_messages", [msg1, msg2, msg3])
    Store-->>Webhook: Success
    Webhook-->>User: 200 OK (queued)
    
    Note over Agent: Agent continues working...
    
    Agent->>Middleware: Before next model call
    Middleware->>Store: store.get_item(("queue", thread_id), "pending_messages")
    Store-->>Middleware: [msg1, msg2, msg3]
    Middleware->>Middleware: Pop messages from queue
    Middleware->>Store: store.delete_item(("queue", thread_id), "pending_messages")
    Middleware->>Agent: Inject messages into state
    Agent->>Agent: Process queued messages
```

**Diagram: Message Queueing Flow for Concurrent Events**

The queueing mechanism ensures no messages are lost when multiple people comment on the same Linear issue or Slack thread simultaneously. The `check_message_queue_before_model` middleware (see [Middleware System](#3.3)) injects queued messages before the agent's next LLM call, allowing real-time guidance during long-running tasks.

**Key Functions:**
- `is_thread_active(thread_id)` [agent/utils/thread_ops.py:90](): Checks if thread status is "busy"
- `queue_message_for_thread(thread_id, message_content)` [agent/utils/thread_ops.py:90](): Stores message in LangGraph Store under namespace `("queue", thread_id)`
- `check_message_queue_before_model` [CUSTOMIZATION.md:19](): Middleware that retrieves and injects queued messages

**Sources:** [agent/webapp.py:90](), [README.md:93-94]()

---

## Context Assembly by Surface

Each surface provides different context to the agent:

```mermaid
graph TB
    subgraph "Slack Context"
        SlackEvent["Slack Event Payload"]
        SlackUser["get_slack_user_info(user_id)<br/>Resolve user email"]
        SlackThread["fetch_slack_thread_messages()<br/>Full thread history"]
        SlackContext["select_slack_context_messages()<br/>From thread start or last @openswe mention"]
        SlackPrompt["Format as conversation:<br/>@user1: message<br/>@user2: message<br/>@openswe: ..."]
        
        SlackEvent --> SlackUser
        SlackEvent --> SlackThread
        SlackThread --> SlackContext
        SlackContext --> SlackPrompt
    end
    
    subgraph "Linear Context"
        LinearEvent["Linear Webhook Payload"]
        LinearFetch["fetch_linear_issue_details(issue_id)<br/>GraphQL API call"]
        LinearIssue["Issue: title, description, identifier<br/>Comments: body, author, created_at<br/>Project: name, team"]
        LinearRecent["get_recent_comments()<br/>Filter out bot messages"]
        LinearPrompt["Format as markdown:<br/>## Title<br/>## Description<br/>## Comments"]
        
        LinearEvent --> LinearFetch
        LinearFetch --> LinearIssue
        LinearIssue --> LinearRecent
        LinearRecent --> LinearPrompt
    end
    
    subgraph "GitHub Context"
        GitHubEvent["GitHub Webhook Payload"]
        GitHubType{"Event Type?"}
        GitHubIssue["fetch_issue_comments()<br/>All issue comments"]
        GitHubPR["fetch_pr_comments_since_last_tag()<br/>PR comments + review comments + reviews"]
        GitHubPrompt["Format with trust wrappers:<br/>UNTRUSTED_GITHUB_COMMENT_OPEN_TAG<br/>comment body<br/>UNTRUSTED_GITHUB_COMMENT_CLOSE_TAG"]
        
        GitHubEvent --> GitHubType
        GitHubType -->|issue/issue_comment| GitHubIssue
        GitHubType -->|pull_request_review| GitHubPR
        GitHubIssue --> GitHubPrompt
        GitHubPR --> GitHubPrompt
    end
```

**Diagram: Context Assembly Pipeline by Surface**

**Slack Context** includes:
- Full thread history (or from last `@openswe` mention) [agent/utils/slack.py:69]()
- User display names and emails [agent/utils/slack.py:71-72]()
- Conversation formatted as chronological messages [agent/utils/slack.py:70]()
- Repository specified via `repo:owner/name` syntax or defaults [agent/webapp.py:122-125]()

**Linear Context** includes:
- Full issue title, description, identifier [agent/webapp.py:175-198]()
- All comments with authors and timestamps [agent/webapp.py:200-209]()
- Team and project information for repo mapping [agent/webapp.py:175-198]()
- Recent comments filtered to exclude bot messages [agent/utils/comments.py:40]()

**GitHub Context** includes:
- Issue/PR title, body, number, URL [agent/utils/github_comments.py:48-49]()
- All comments (issues) or comments since last `@openswe` tag (PRs) [agent/utils/github_comments.py:50-51]()
- Inline review comments with file path and line number [agent/utils/github_comments.py:51]()
- Trust wrappers for comments from users not in `GITHUB_USER_EMAIL_MAP` [agent/utils/github_comments.py:61]()

**Sources:** [agent/webapp.py:67-84]() (Slack), [agent/webapp.py:175-217]() (Linear), [agent/utils/github_comments.py:45-58]() (GitHub)

---

## Repository Resolution

Each surface uses a different mechanism to determine which GitHub repository the agent should operate on:

| Surface | Resolution Mechanism | Configuration | Fallback |
|---------|---------------------|---------------|----------|
| **Slack** | 1. Parse `repo:owner/name` from message<br/>2. Extract from `github.com/owner/name` URL<br/>3. Check thread metadata<br/>4. Use environment defaults | `SLACK_REPO_OWNER`, `SLACK_REPO_NAME` | `langchain-ai/langchainplus` |
| **Linear** | Map team name and project name to repo | `LINEAR_TEAM_TO_REPO` in [agent/utils/linear_team_repo_map.py]() | `langchain-ai/langchainplus` |
| **GitHub** | Extract directly from webhook payload | `payload.repository.owner.login`, `payload.repository.name` | N/A (always present) |

**Slack Repository Resolution:**
The `extract_repo_from_text` function [agent/utils/repo.py:65]() extracts repository details from message text. It checks for explicit `repo:owner/name` syntax before falling back to environment defaults defined in `agent/webapp.py` [agent/webapp.py:122-125]().

**Linear Repository Resolution:**
The `get_repo_config_from_team_mapping` function [agent/webapp.py:175-198]() uses the `LINEAR_TEAM_TO_REPO` mapping [agent/utils/linear_team_repo_map.py:63]() to find the correct owner and repository name based on the Linear team identifier and project name.

**Sources:** [agent/webapp.py:175-198]() (Linear), [agent/utils/repo.py:65](), [agent/utils/linear_team_repo_map.py:63]()

---

## Acknowledgment Reactions

All three surfaces immediately react to the triggering message with a 👀 emoji to acknowledge receipt:

| Surface | Reaction Method | API Endpoint | Timing |
|---------|----------------|--------------|--------|
| **Slack** | `set_slack_assistant_status(channel, thread_ts, "thinking")` | `POST /chat.postMessage` | Before thread check |
| **Linear** | `react_to_linear_comment(comment_id, "👀")` | GraphQL `reactionCreate` mutation | Before fetching issue details |
| **GitHub** | `react_to_github_comment(repo, comment_id, event_type, token)` | `POST /repos/{owner}/{repo}/issues/comments/{id}/reactions` | Before processing payload |

The reaction provides instant feedback to users while the agent provisions a sandbox and begins execution.

**Sources:** [agent/utils/slack.py:80]() (Slack), [agent/webapp.py:200-209]() (Linear logic), [agent/utils/github_comments.py:55]() (GitHub)

---

## Environment Variables by Surface

Each surface requires specific environment variables for webhook verification and API access:

### Slack
```bash
SLACK_BOT_TOKEN          # OAuth token (xoxb-...)
SLACK_BOT_USER_ID        # Bot's user ID [agent/webapp.py:120]
SLACK_BOT_USERNAME       # Bot's display name [agent/webapp.py:121]
SLACK_SIGNING_SECRET     # Webhook signature verification [agent/webapp.py:119]
SLACK_REPO_OWNER         # Default repo owner [agent/webapp.py:124]
SLACK_REPO_NAME          # Default repo name [agent/webapp.py:125]
```

### Linear
```bash
LINEAR_API_KEY           # Personal API key [agent/webapp.py:162]
LINEAR_WEBHOOK_SECRET    # Webhook signature verification [agent/webapp.py:117]
# LINEAR_TEAM_TO_REPO configured in agent/utils/linear_team_repo_map.py
```

### GitHub
```bash
GITHUB_WEBHOOK_SECRET    # Webhook signature verification [agent/webapp.py:118]
GITHUB_APP_ID            # GitHub App ID [INSTALLATION.md:82]
GITHUB_APP_PRIVATE_KEY   # GitHub App private key [INSTALLATION.md:83]
GITHUB_APP_INSTALLATION_ID  # Installation ID [INSTALLATION.md:99]
# GITHUB_USER_EMAIL_MAP configured in agent/utils/github_user_email_map.py
```

**Sources:** [agent/webapp.py:117-125](), [INSTALLATION.md:82-99]()

---

# Page: Slack Integration

# Slack Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/tools/slack_thread_reply.py](agent/tools/slack_thread_reply.py)
- [agent/utils/slack.py](agent/utils/slack.py)
- [agent/utils/slack_feedback.py](agent/utils/slack_feedback.py)
- [tests/test_slack_context.py](tests/test_slack_context.py)
- [tests/test_slack_feedback.py](tests/test_slack_feedback.py)

</details>



This page documents how to trigger Open SWE agents via Slack app mentions and how the system processes Slack events, assembles conversation context, and routes responses back to threads.

## Overview

The Slack integration enables users to invoke the Open SWE agent by mentioning the bot in any Slack channel or thread. When tagged with `@openswe` (or the configured bot username), the system:

1.  Receives a webhook event from Slack's Event API.
2.  Verifies the request signature for security.
3.  Generates a deterministic thread ID from the Slack channel and thread timestamp.
4.  Assembles conversation context from the thread history.
5.  Resolves which GitHub repository to work on.
6.  Creates a LangGraph agent run with full context.
7.  Enables the agent to reply in-thread using the `slack_thread_reply` tool.
8.  Captures user feedback via emoji reactions.

The integration supports both direct mentions and replies in existing threads, with automatic context selection to include either the full thread or just messages since the last bot mention.

**Sources:** [agent/webapp.py:698-810](), [agent/webapp.py:957-1046](), [agent/utils/slack_feedback.py:119-206]()

---

## Setup and Configuration

### Required Environment Variables

The Slack integration requires the following environment variables:

| Variable | Purpose | Example |
| :--- | :--- | :--- |
| `SLACK_BOT_TOKEN` | Bot User OAuth Token from Slack App | `xoxb-...` |
| `SLACK_SIGNING_SECRET` | Webhook signature verification secret | From App Credentials |
| `SLACK_BOT_USER_ID` | Bot's Slack user ID | `U01ABC123` |
| `SLACK_BOT_USERNAME` | Bot's display name | `openswe` |
| `SLACK_REPO_OWNER` | Default GitHub repository owner | `langchain-ai` |
| `SLACK_REPO_NAME` | Default GitHub repository name | `open-swe` |

**Sources:** [agent/webapp.py:61-67](), [agent/utils/slack.py:25-25]()

### Slack App Configuration

The Slack App must be configured with:

1.  **Event Subscriptions**: Request URL pointing to `https://<your-domain>/webhooks/slack`.
2.  **Bot Events**:
    *   `app_mention` — for @bot mentions.
    *   `message.im` — for direct messages.
    *   `reaction_added` / `reaction_removed` — for feedback tracking.
3.  **OAuth Scopes** (bot token):
    *   `reactions:write` / `reactions:read` — manage emoji feedback.
    *   `app_mentions:read` — detect mentions.
    *   `channels:history` — read thread context.
    *   `chat:write` — post replies.
    *   `users:read` — fetch user information.

---

## Webhook Processing Flow

The `slack_webhook` endpoint in `agent/webapp.py` [agent/webapp.py:957-1046]() handles incoming requests. If the signature is valid, it dispatches the event to `process_slack_mention` [agent/webapp.py:698-810]() or feedback processors [agent/utils/slack_feedback.py:208-213]() as background tasks.

```mermaid
sequenceDiagram
    participant User as "Slack User"
    participant Slack as "Slack API"
    participant Webhook as "webapp.py:slack_webhook"
    participant Verify as "slack.py:verify_slack_signature"
    participant Process as "webapp.py:process_slack_mention"
    participant ThreadID as "webapp.py:generate_thread_id_from_slack_thread"
    participant RepoConfig as "webapp.py:get_slack_repo_config"
    participant LG as "LangGraph Client"
    
    User->>Slack: "@openswe help me fix this bug"
    Slack->>Webhook: POST /webhooks/slack
    Webhook->>Verify: verify_slack_signature(body, timestamp, signature)
    
    alt Invalid Signature
        Verify-->>Webhook: False
        Webhook-->>Slack: 401 Unauthorized
    else Valid Signature
        Verify-->>Webhook: True
        
        alt URL Verification Challenge
            Webhook-->>Slack: {"challenge": "..."}
        else App Mention Event
            Webhook->>Process: BackgroundTasks.add_task(process_slack_mention)
            Webhook-->>Slack: 200 OK
            
            Process->>Slack: add_slack_reaction(channel_id, event_ts, "eyes")
            Process->>ThreadID: generate_thread_id_from_slack_thread(channel_id, thread_ts)
            ThreadID-->>Process: UUID String
            
            Process->>Slack: get_slack_user_info(user_id)
            Slack-->>Process: {email, display_name}
            
            Process->>Slack: fetch_slack_thread_messages(channel_id, thread_ts)
            Slack-->>Process: [{ts, text, user}, ...]
            
            Process->>Process: select_slack_context_messages(messages, event_ts)
            Process->>RepoConfig: get_slack_repo_config(message, channel_id, thread_ts)
            
            Process->>Process: _upsert_slack_thread_repo_metadata(thread_id, repo_config)
            
            Process->>LG: runs.create(thread_id, "agent", multitask_strategy="interrupt")
            LG-->>Process: Run created
        end
    end
```

**Sources:** [agent/webapp.py:957-1046](), [agent/webapp.py:698-810](), [agent/utils/slack.py:107-132]()

---

## Message Context Assembly

When processing a Slack mention, the system assembles conversation context by:

1.  **Fetching Thread Messages**: Retrieves all messages in the thread via `fetch_slack_thread_messages` [agent/utils/slack.py:382-400]().
2.  **Selecting Context Window**: The `select_slack_context_messages` function [agent/utils/slack.py:207-256]() implements a sliding window strategy.
3.  **Resolving User Names**: Fetches display names for users via `get_slack_user_names` [agent/utils/slack.py:357-379]().
4.  **Formatting for Prompt**: Converts messages to structured text using `format_slack_messages_for_prompt` [agent/utils/slack.py:316-349]().

### Context Selection Algorithm

```mermaid
graph TD
    FetchMsgs["fetch_slack_thread_messages(channel_id, thread_ts)"]
    SortMsgs["Sort messages by timestamp<br/>Filter to current_ts and earlier"]
    FindMentions["Scan for previous bot mentions<br/>(bot_user_id or bot_username)"]
    
    FetchMsgs --> SortMsgs
    SortMsgs --> FindMentions
    
    FindMentions --> CheckPrevMention{"Previous<br/>mention found?"}
    CheckPrevMention -->|Yes| SliceFromMention["Return messages[last_mention_index:]<br/>mode='last_mention'"]
    CheckPrevMention -->|No| ReturnAll["Return all messages<br/>mode='thread_start'"]
    
    SliceFromMention --> Format["format_slack_messages_for_prompt"]
    ReturnAll --> Format
```

**Sources:** [agent/utils/slack.py:207-256](), [agent/utils/slack.py:316-349](), [tests/test_slack_context.py:55-82]()

---

## Thread Management

### Deterministic Thread ID Generation

Slack threads are identified by a composite key of `channel_id:thread_ts`, hashed to produce a deterministic UUID in `generate_thread_id_from_slack_thread` [agent/webapp.py:264-268]().

```python
def generate_thread_id_from_slack_thread(channel_id: str, thread_ts: str) -> str:
    composite = f"{channel_id}:{thread_ts}"
    md5_hex = hashlib.md5(composite.encode("utf-8")).hexdigest()
    return str(uuid.UUID(hex=md5_hex))
```

**Sources:** [agent/webapp.py:264-268](), [tests/test_slack_context.py:46-53]()

### Response Mapping and Feedback

To support feedback on specific bot replies, the system stores a mapping between Slack message timestamps and LangGraph run IDs in the LangGraph Store via `store_slack_message_run_mapping` [agent/utils/slack.py:543-559]().

When a user adds a reaction (e.g., `:thumbsup:`), `process_slack_reaction` [agent/utils/slack_feedback.py:119-206]() performs:
1.  **Lookup**: Retrieves the `run_id` for that specific message [agent/utils/slack_feedback.py:150-161]().
2.  **Verification**: Ensures the reactor is the user who triggered the run [agent/utils/slack_feedback.py:163-172]().
3.  **Scoring**: Converts reactions to numeric scores (`+1` = 1.0, `-1` = 0.0) [agent/utils/slack_feedback.py:22-27]().
4.  **Persistence**: Records feedback in LangSmith [agent/utils/slack_feedback.py:194-202]().

**Sources:** [agent/utils/slack_feedback.py:119-206](), [agent/utils/slack.py:543-559](), [tests/test_slack_feedback.py:69-104]()

---

## Response Flow and Tools

### Agent Tool: `slack_thread_reply`

The agent uses the `slack_thread_reply` tool [agent/tools/slack_thread_reply.py:19-53]() to post responses back to the Slack thread.

*   **Mention Conversion**: Converts `@Name(USER_ID)` to `<@USER_ID>` [agent/tools/slack_thread_reply.py:51]().
*   **Run Mapping**: Every reply is mapped to the current `run_id` to enable future feedback [agent/tools/slack_thread_reply.py:56-61]().
*   **Formatting**: The tool documentation explicitly instructs the agent to use Slack `mrkdwn` (e.g., `*bold*`, `_italic_`, `• list`) rather than standard Markdown [agent/tools/slack_thread_reply.py:28-31]().

**Sources:** [agent/tools/slack_thread_reply.py:19-53](), [agent/utils/slack.py:102-104]()

---

## Security: Signature Verification

Incoming Slack webhooks are verified using `verify_slack_signature` [agent/utils/slack.py:107-132]().

*   **HMAC-SHA256**: Uses `SLACK_SIGNING_SECRET` to verify the payload.
*   **Replay Protection**: Rejects requests older than 5 minutes (`max_age_seconds: 300`).
*   **Constant-time comparison**: Uses `hmac.compare_digest` to prevent timing attacks.

**Sources:** [agent/utils/slack.py:107-132](), [agent/webapp.py:962-971]()

---

# Page: Linear Integration

# Linear Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/utils/langsmith.py](agent/utils/langsmith.py)
- [agent/utils/linear.py](agent/utils/linear.py)
- [agent/utils/linear_team_repo_map.py](agent/utils/linear_team_repo_map.py)
- [agent/webapp.py](agent/webapp.py)
- [tests/test_github_issue_webhook.py](tests/test_github_issue_webhook.py)

</details>



Linear Integration enables Open SWE agents to be triggered from Linear issue comments. When a user mentions `@openswe` in any Linear comment, the system creates or resumes an agent thread to work on that issue, fetches the full issue context, and posts results back as Linear comments.

For information about triggering agents from other platforms, see [Slack Integration](#2.1) and [GitHub Integration](#2.3). For technical details about webhook processing, see [Webhook Processing Flow](#2.4).

---

## Overview

The Linear integration consists of three main components:

1.  **Webhook endpoint** that receives Linear comment events.
2.  **Team-to-repository mapping** that routes Linear issues to GitHub repositories.
3.  **Issue context assembly** that pre-hydrates the full issue details for the agent.

The integration maintains deterministic thread IDs based on Linear issue IDs, enabling follow-up comments to route to the same running agent instance.

**Sources:**
- [agent/webapp.py:833-948]()
- [agent/webapp.py:166-232]()
- [agent/webapp.py:98-121]()

---

## Webhook Configuration

The Linear webhook endpoint is exposed at `POST /webhooks/linear` and requires signature verification using the `LINEAR_WEBHOOK_SECRET` environment variable.

### Required Environment Variables

| Variable | Purpose | How to Obtain |
| :--- | :--- | :--- |
| `LINEAR_WEBHOOK_SECRET` | Webhook signature verification | Generate with `openssl rand -hex 32` |
| `LINEAR_API_KEY` | Fetch full issue details and post comments | Linear Settings → API → Personal API keys |

### Webhook Settings in Linear

The webhook must be configured to listen for **Comment → Create** events only. Other event types are ignored.

```mermaid
graph TB
    LinearUI["Linear Settings<br/>API → Webhooks"]
    
    LinearUI --> Config["Webhook Configuration"]
    
    Config --> URL["URL:<br/>https://your-domain/webhooks/linear"]
    Config --> Secret["Secret:<br/>LINEAR_WEBHOOK_SECRET"]
    Config --> Events["Events:<br/>Comment → Create only"]
    
    Events --> CommentCreate["✓ Comments → Create"]
    Events --> OtherEvents["✗ All other events ignored"]
```

**Sources:**
- [agent/webapp.py:117-117]()
- [agent/webapp.py:162-162]()
- [agent/utils/linear.py:15-16]()

---

## Webhook Request Flow

The following diagram bridges the **Natural Language Space** (Linear Comments) to the **Code Entity Space** (FastAPI routes and utility functions).

```mermaid
sequenceDiagram
    participant Linear as "Linear Platform"
    participant Webhook as "POST /webhooks/linear<br/>(agent/webapp.py:833)"
    participant VerifySig as "verify_linear_signature()<br/>(agent/webapp.py:813)"
    participant FetchDetails as "fetch_linear_issue_details()<br/>(agent/webapp.py:166)"
    participant TeamMapping as "get_repo_config_from_team_mapping()<br/>(agent/webapp.py:175)"
    participant React as "react_to_linear_comment()<br/>(agent/webapp.py:200)"
    participant Background as "BackgroundTasks"
    participant Process as "process_linear_issue()<br/>(agent/webapp.py:481)"
    participant ThreadID as "generate_thread_id_from_linear_issue()<br/>(agent/webapp.py:234)"
    participant LG as "LangGraph Client"
    
    Linear->>Webhook: POST with Linear-Signature header
    Webhook->>VerifySig: Verify HMAC-SHA256 signature
    
    alt Invalid signature
        VerifySig-->>Webhook: 401 Unauthorized
        Webhook-->>Linear: Rejected
    end
    
    VerifySig-->>Webhook: Valid
    
    Webhook->>Webhook: Parse JSON payload
    Webhook->>Webhook: Check event type == "Comment"
    Webhook->>Webhook: Check action == "create"
    Webhook->>Webhook: Check contains "@openswe"
    
    Webhook->>FetchDetails: Fetch full issue with GraphQL
    FetchDetails-->>Webhook: Issue with team, project, comments
    
    Webhook->>TeamMapping: Resolve team + project to repo
    TeamMapping-->>Webhook: {"owner": "...", "name": "..."}
    
    Webhook->>Background: Schedule process_linear_issue()
    Webhook-->>Linear: 200 OK {"status": "accepted"}
    
    Background->>React: Add 👀 reaction to comment
    Background->>Process: Execute in background
    
    Process->>ThreadID: Generate deterministic UUID
    ThreadID-->>Process: "abc12345-..."
    
    Process->>LG: runs.create(thread_id, input, config)
```

**Sources:**
- [agent/webapp.py:833-948]()
- [agent/webapp.py:200-232]()
- [agent/webapp.py:481-695]()
- [agent/webapp.py:813-831]()

---

## Signature Verification

The `verify_linear_signature()` function validates incoming webhooks using HMAC-SHA256. All webhook requests with missing or invalid signatures are rejected with HTTP 401.

**Sources:**
- [agent/webapp.py:813-831]()
- [agent/webapp.py:844-847]()

---

## Event Filtering

The webhook handler applies multiple filters before processing to avoid infinite loops or unnecessary runs:

| Filter | Check | Rejection Reason |
| :--- | :--- | :--- |
| Event type | `payload.get("type") == "Comment"` | "Not a Comment event" |
| Action | `payload.get("action") == "create"` | "Only processing 'create'" |
| Bot author | `not data.get("botActor")` | "Comment is from a bot" |
| Agent mention | `"@openswe" in comment_body.lower()` | "Comment doesn't mention @openswe" |
| Bot message prefix | `not comment_body.startswith(_GITHUB_BOT_MESSAGE_PREFIXES)` | "Comment is our own bot message" |

**Sources:**
- [agent/webapp.py:855-889]()
- [agent/webapp.py:164-172]()

---

## Team-to-Repository Mapping

Linear teams and projects are mapped to GitHub repositories via `LINEAR_TEAM_TO_REPO` in `agent/utils/linear_team_repo_map.py`.

### Mapping Resolution Logic

The `get_repo_config_from_team_mapping()` function follows this hierarchy:

1.  **Direct Team Match**: If the team has an `owner` and `name` directly.
2.  **Project Match**: If the team has a `projects` dictionary and the issue's project name matches a key.
3.  **Team Default**: If the team has a `default` key.
4.  **System Default**: Fallback to `DEFAULT_REPO_OWNER` and `DEFAULT_REPO_NAME`.

```mermaid
graph TD
    Start["get_repo_config_from_team_mapping()<br/>(agent/webapp.py:175)"]
    
    Start --> CheckTeam{Team in<br/>LINEAR_TEAM_TO_REPO?}
    
    CheckTeam -->|No| Default["Return system default:<br/>langchain-ai/langchainplus"]
    
    CheckTeam -->|Yes| GetConfig["config = LINEAR_TEAM_TO_REPO[team]"]
    
    GetConfig --> HasOwner{config has<br/>'owner' and 'name'?}
    
    HasOwner -->|Yes| ReturnDirect["Return config directly"]
    
    HasOwner -->|No| HasProjects{config has<br/>'projects' and project_name?}
    
    HasProjects -->|Yes| GetProject["project_config = config['projects'][project_name]"]
    GetProject --> ProjectFound{Project found?}
    ProjectFound -->|Yes| ReturnProject["Return project_config"]
    ProjectFound -->|No| CheckDefault{config has<br/>'default'?}
    
    HasProjects -->|No| CheckDefault
    
    CheckDefault -->|Yes| ReturnDefault["Return config['default']"]
    CheckDefault -->|No| Default
```

**Sources:**
- [agent/webapp.py:175-198]()
- [agent/utils/linear_team_repo_map.py:3-30]()

---

## Thread ID Generation

Thread IDs are deterministically generated from Linear issue IDs using SHA-256 in `generate_thread_id_from_linear_issue()`. This ensures that multiple comments on the same issue route to the same LangGraph thread, maintaining state across interactions.

**Sources:**
- [agent/webapp.py:234-252]()

---

## Issue Context Assembly

The `fetch_linear_issue_details()` function fetches comprehensive issue data via Linear's GraphQL API, including:
*   Issue Title and Description
*   Project and Team metadata
*   Full comment history (nodes including body, author, and timestamp)

This data is used to hydrate the agent's initial prompt so it doesn't have to perform manual discovery.

**Sources:**
- [agent/webapp.py:166-232]()
- [agent/utils/linear.py:105-130]()
- [agent/utils/linear.py:181-204]()

---

## Linear Tools for Agents

Open SWE provides several tools specifically for interacting with Linear within the agent loop. These wrap utilities in `agent/utils/linear.py`.

| Tool Name | Implementation Utility | Purpose |
| :--- | :--- | :--- |
| `linear_comment` | `comment_on_linear_issue` | Post a new comment to an issue. |
| `linear_get_issue` | `get_issue` | Retrieve full issue details by UUID. |
| `linear_create_issue` | `create_issue` | Create a new issue in a specific team. |
| `linear_update_issue` | `update_issue` | Modify title, description, state, or assignee. |
| `linear_list_teams` | `list_teams` | List all teams in the workspace. |

**Sources:**
- [agent/utils/linear.py:47-63]()
- [agent/utils/linear.py:105-130]()
- [agent/utils/linear.py:133-178]()
- [agent/utils/linear.py:207-240]()
- [agent/utils/linear.py:85-102]()

---

## Prompt Construction and Multimodal Support

The `process_linear_issue()` function assembles the final prompt. It uses `extract_image_urls` and `fetch_image_block` from `agent/utils/multimodal.py` to include images from the Linear issue description or comments directly in the agent's context.

The prompt includes:
1.  **Issue Metadata**: Title, identifier (e.g., ENG-123), and URL.
2.  **Description**: The full markdown description of the issue.
3.  **Comments**: Filtered history, excluding bot messages.
4.  **Tagging Instructions**: Instructions to the agent on when to tag the triggering user.

**Sources:**
- [agent/webapp.py:481-695]()
- [agent/webapp.py:614-628]()
- [agent/utils/multimodal.py:64-65]()

---

## Status Updates

When an agent is triggered, it immediately provides feedback to the user:
1.  **Reaction**: The system adds a "eyes" (👀) reaction to the triggering comment via `react_to_linear_comment()`.
2.  **Trace Comment**: It posts a comment "On it! [View trace](...)" containing a link to the LangSmith trace via `post_linear_trace_comment()`.

**Sources:**
- [agent/webapp.py:200-232]()
- [agent/utils/linear.py:66-83]()
- [agent/webapp.py:507-511]()

---

# Page: GitHub Integration

# GitHub Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/utils/auth.py](agent/utils/auth.py)
- [agent/utils/github_app.py](agent/utils/github_app.py)
- [agent/utils/github_comments.py](agent/utils/github_comments.py)
- [agent/utils/github_token.py](agent/utils/github_token.py)
- [agent/webapp.py](agent/webapp.py)
- [tests/test_github_issue_webhook.py](tests/test_github_issue_webhook.py)
- [tests/test_github_token_ttl.py](tests/test_github_token_ttl.py)
- [tests/test_proxy_auth.py](tests/test_proxy_auth.py)

</details>



This page documents how to use `@openswe` mentions in GitHub issues and pull request comments to trigger agent runs. GitHub is one of three invocation surfaces supported by Open SWE—for Slack integration see [2.1]() and for Linear integration see [2.2]().

GitHub integration differs from Slack and Linear in two key ways: (1) thread IDs are extracted from branch names for PR-based workflows, enabling seamless review feedback loops, and (2) authentication uses per-user GitHub OAuth tokens mapped from GitHub usernames rather than email addresses.

---

## Triggering Mechanisms

### Issue-Based Invocation

Users can trigger the agent by mentioning `@openswe` in:
- Issue titles or bodies when creating a new issue [agent/webapp.py:1001-1015]()
- Issue comments for follow-up instructions on existing issues [agent/webapp.py:1020-1035]()

The system matches any of the following mention patterns (case-insensitive):
- `@openswe`
- `@open-swe`
- `@openswe-dev`

**Sources:** [agent/utils/github_comments.py:36-37](), [agent/webapp.py:118-125]()

### Pull Request Comment Invocation

For PRs created by the agent, users can tag `@openswe` in:
- PR review comments (inline code comments) [agent/webapp.py:1040-1055]()
- PR review bodies (overall review feedback) [agent/webapp.py:1060-1075]()
- General PR issue comments [agent/webapp.py:1020-1035]()

This enables a review feedback loop where the agent can address reviewer comments by pushing additional commits to the same branch.

**Sources:** [agent/utils/github_comments.py:80-94](), [agent/webapp.py:1040-1075]()

---

## Webhook Processing Flow

```mermaid
graph TB
    GitHub["GitHub Webhook Event"] --> Endpoint["POST /webhooks/github"]
    Endpoint --> VerifySig["verify_github_signature()"]
    VerifySig -->|Invalid| Reject["Return 401"]
    VerifySig -->|Valid| ParseEvent["Parse Event Type"]
    
    ParseEvent --> IssueEvent{"Event Type?"}
    IssueEvent -->|"issues"| CheckIssueAction["Check action:<br/>opened/edited"]
    IssueEvent -->|"issue_comment"| CheckComment["Check for @openswe<br/>in comment body"]
    IssueEvent -->|"pull_request_review"<br/>"pull_request_review_comment"| ExtractPRContext["extract_pr_context()"]
    IssueEvent -->|Other| Ignore["Return 'ignored'"]
    
    CheckIssueAction --> CheckMention["Check title/body<br/>for @openswe"]
    CheckMention -->|Not found| Ignore
    CheckMention -->|Found| ExtractIssueContext["Extract issue context"]
    
    CheckComment -->|Not found| Ignore
    CheckComment -->|Found| DeterminePrompt{"Thread exists?"}
    
    ExtractPRContext --> GetThreadFromBranch["get_thread_id_from_branch()"]
    GetThreadFromBranch --> FetchPRComments["fetch_pr_comments_since_last_tag()"]
    FetchPRComments --> BuildPRPrompt["build_pr_prompt()"]
    
    DeterminePrompt -->|No| BuildFullPrompt["build_github_issue_prompt()"]
    DeterminePrompt -->|Yes| BuildFollowupPrompt["build_github_issue_followup_prompt()"]
    
    ExtractIssueContext --> BuildFullPrompt
    BuildFullPrompt --> ResolveToken["resolve_github_token()"]
    BuildFollowupPrompt --> ResolveToken
    BuildPRPrompt --> ResolveToken
    
    ResolveToken --> ReactEyes["react_to_github_comment()<br/>Add 👀 reaction"]
    ReactEyes --> CheckThreadStatus["is_thread_active()"]
    CheckThreadStatus -->|Busy| QueueMessage["queue_message_for_thread()"]
    CheckThreadStatus -->|Idle| CreateRun["langgraph_client.runs.create()"]
```

### Webhook Endpoint

The FastAPI webhook endpoint at `/webhooks/github` in `agent/webapp.py` handles the following GitHub event types:

| Event Type | Trigger | Action Field |
|------------|---------|--------------|
| `issues` | Issue opened/edited | `opened`, `edited` |
| `issue_comment` | Comment on issue/PR | `created` |
| `pull_request_review` | PR review submitted | `submitted` |
| `pull_request_review_comment` | Inline code comment | `created` |

**Sources:** [agent/webapp.py:1001-1095](), [tests/test_github_issue_webhook.py:130-161]()

### Signature Verification

All webhook requests must include a valid `X-Hub-Signature-256` header. The `verify_github_signature` function computes an HMAC-SHA256 signature of the raw request body using the `GITHUB_WEBHOOK_SECRET` environment variable and compares it against the provided signature using `hmac.compare_digest` to prevent timing attacks.

**Sources:** [agent/utils/github_comments.py:52-68](), [tests/test_github_issue_webhook.py:24-27]()

---

## Thread ID Resolution

### Issue-Based Thread IDs

For GitHub issues, the system generates deterministic thread IDs. This ensures that follow-up comments on the same issue route to the same LangGraph thread, maintaining conversation context and sandbox state.

**Sources:** [agent/webapp.py:255-261](), [tests/test_github_issue_webhook.py:64-70]()

### PR-Based Thread IDs (Branch Name Extraction)

For pull request comments, the thread ID is extracted from the PR's head branch name using a regular expression that matches UUID patterns:

```python
# agent/utils/github_comments.py:71-77
def get_thread_id_from_branch(branch_name: str) -> str | None:
    match = re.search(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        branch_name,
        re.IGNORECASE,
    )
    return match.group(0) if match else None
```

When the agent creates a PR, it automatically includes the thread ID in the branch name (e.g., `openswe-{thread_id}`). This enables seamless thread continuity when reviewers comment on the PR—the system extracts the original thread ID and routes the feedback to the existing agent run.

**Sources:** [agent/utils/github_comments.py:71-77](), [agent/webapp.py:1137-1143]()

---

## Authentication and Token Resolution

```mermaid
graph TB
    Start["GitHub webhook received"] --> CheckMode{"Bot-token-only mode?"}
    CheckMode -->|Yes| UseAppToken["get_github_app_installation_token()<br/>Shared bot identity"]
    CheckMode -->|No| ExtractLogin["Extract sender.login<br/>from webhook payload"]
    
    ExtractLogin --> LookupEmail["GITHUB_USER_EMAIL_MAP.get(login)"]
    LookupEmail -->|Not found| Error["Raise ValueError:<br/>No email mapping"]
    LookupEmail -->|Found| CheckCache["get_github_token_from_thread()"]
    
    CheckCache -->|Cached| UseCached["Return cached token"]
    CheckCache -->|Not cached| ResolveFromEmail["resolve_github_token_from_email()"]
    
    ResolveFromEmail --> GetLSUser["get_ls_user_id_from_email()"]
    GetLSUser -->|Not found| AuthFailure["Leave failure comment:<br/>User not in LangSmith"]
    GetLSUser -->|Found| GetOAuthToken["get_github_token_for_user()"]
    
    GetOAuthToken --> OAuthResult{"OAuth result?"}
    OAuthResult -->|token| EncryptAndStore["encrypt_token()<br/>persist_encrypted_github_token()"]
    OAuthResult -->|auth_url| LeaveAuthLink["Leave auth required comment<br/>with OAuth URL"]
    OAuthResult -->|error| AuthFailure
    
    EncryptAndStore --> UseToken["Use per-user token"]
    UseAppToken --> UseToken
    UseCached --> UseToken
    
    UseToken --> ReactAndRun["react_to_github_comment()<br/>Create LangGraph run"]
```

### User Email Mapping

Unlike Slack and Linear which use email addresses from the webhook payload, GitHub integration requires a manual mapping from GitHub usernames to email addresses in `GITHUB_USER_EMAIL_MAP`. This is a security measure to ensure only authorized users can trigger the agent.

**Sources:** [agent/utils/github_user_email_map.py:1-4](), [agent/webapp.py:1105-1108](), [agent/utils/auth.py:19]()

### Bot-Token-Only Mode

When the system is configured in bot-token-only mode (detected via `is_bot_token_only_mode`), all GitHub operations use the GitHub App's installation token instead of per-user OAuth tokens. This mode is active when a LangSmith API key is present but specific service JWT secrets are missing.

**Sources:** [agent/utils/auth.py:44-52](), [agent/webapp.py:35-38]()

### OAuth Token Resolution

When not in bot-token-only mode, the system resolves per-user GitHub tokens via LangSmith's OAuth integration:
1. Map GitHub username → email via `GITHUB_USER_EMAIL_MAP`.
2. Resolve LangSmith user ID from email via `get_ls_user_id_from_email`.
3. Call LangSmith Host API to get the OAuth token via `get_github_token_for_user`.
4. Encrypt and persist the token in thread metadata via `persist_encrypted_github_token`.

**Sources:** [agent/utils/auth.py:96-122](), [agent/utils/auth.py:138-183](), [agent/webapp.py:1115-1128]()

### Token Expiry and Invalidation

The system tracks token expiry using `github_token_expires_at` metadata. If a token is expired or if a downstream GitHub API call returns a `401 Unauthorized` error, the cached token is invalidated.

**Sources:** [agent/utils/github_token.py:45-79](), [agent/utils/github_token.py:137-154](), [tests/test_github_token_ttl.py:163-177]()

---

## Pull Request Review Workflow

### Comment Fetching Strategy

When handling PR review feedback, the system fetches comments from multiple GitHub API endpoints and merges them chronologically. The `fetch_pr_comments_since_last_tag` function implements a "context window" strategy: it returns all comments from the most recent `@openswe` mention onwards.

**Sources:** [agent/utils/github_comments.py:26-30](), [agent/webapp.py:45-58]()

### Prompt Construction for PR Comments

The `build_pr_prompt` function formats the fetched comments into a structured prompt that includes file paths and line numbers for inline review comments. It explicitly instructs the agent to use `commit_and_open_pr` to push changes.

**Sources:** [agent/webapp.py:45-58](), [agent/utils/github_comments.py:22-23]()

### Untrusted User Comment Wrapping

GitHub comments from users not in `GITHUB_USER_EMAIL_MAP` are wrapped in special XML-like tags (`<dangerous-external-untrusted-users-comment>`) to mark them as untrusted.

**Sources:** [agent/utils/github_comments.py:39-42](), [agent/utils/github_comments.py:111-122]()

---

## Reaction Mechanism

The system adds a 👀 (eyes) emoji reaction to GitHub comments to acknowledge receipt. For `pull_request_review` events, it uses a GraphQL mutation since the REST API does not support reactions on review summaries directly via the standard reaction endpoint.

**Sources:** [agent/utils/github_comments.py:124-164](), [agent/utils/github_comments.py:166-200]()

---

## Message Queueing for Concurrent Comments

When multiple comments arrive while the agent is busy, the system queues subsequent messages using the LangGraph Store. The `check_message_queue_before_model` middleware (integrated via `get_agent`) ensures these queued messages are processed.

**Sources:** [agent/webapp.py:90](), [agent/webapp.py:1324-1330]()

---

# Page: Webhook Processing Flow

# Webhook Processing Flow

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/webapp.py](agent/webapp.py)
- [tests/test_github_issue_webhook.py](tests/test_github_issue_webhook.py)

</details>



This page documents the technical flow from webhook reception through signature verification, event filtering, background task dispatch, and LangGraph run creation. This covers the FastAPI webhook endpoints and the request processing pipeline that transforms external events (Slack mentions, Linear comments, GitHub PR comments) into agent runs.

For details on configuring specific webhook integrations, see [Slack Integration](#2.1), [Linear Integration](#2.2), and [GitHub Integration](#2.3). For how thread IDs are generated from different sources, see [Thread ID Generation](#6.1). For authentication token resolution, see [GitHub Token Resolution](#7.1).

---

## Overview: Request Processing Pipeline

The webhook processing pipeline follows a consistent pattern across all three invocation surfaces (Slack, Linear, GitHub):

```mermaid
graph TB
    Webhook["Webhook Event<br/>(POST request)"]
    VerifySig["Signature Verification<br/>verify_*_signature()"]
    ParseJSON["Parse JSON Payload"]
    FilterEvent["Event Filtering<br/>(type, action, bot detection)"]
    ExtractContext["Extract Context<br/>(issue/thread details)"]
    ThreadCheck["Check Thread Status<br/>is_thread_active()"]
    
    Queue["Queue Message<br/>queue_message_for_thread()"]
    CreateRun["Create LangGraph Run<br/>langgraph_client.runs.create()"]
    
    Background["Background Task<br/>process_*()"]
    
    Webhook --> VerifySig
    VerifySig -->|Valid| ParseJSON
    VerifySig -->|Invalid| Reject["HTTP 401<br/>Invalid signature"]
    
    ParseJSON --> FilterEvent
    FilterEvent -->|Pass| Background
    FilterEvent -->|Fail| Ignore["HTTP 200<br/>{'status': 'ignored'}"]
    
    Background --> ExtractContext
    ExtractContext --> ThreadCheck
    
    ThreadCheck -->|"status == 'busy'"| Queue
    ThreadCheck -->|"status == 'idle'"| CreateRun
    
    Queue --> QueueStore["LangGraph Store API<br/>namespace: ('queue', thread_id)"]
    CreateRun --> LangGraphServer["LangGraph Server<br/>Thread execution starts"]
```

**Sources:** [agent/webapp.py:1-1376]()

---

## Webhook Endpoints and Routing

Open SWE exposes four webhook endpoints via FastAPI:

| Endpoint | HTTP Method | Purpose | Handler Function |
|----------|-------------|---------|------------------|
| `/webhooks/slack` | POST | Slack Event API callbacks | `slack_webhook` [agent/webapp.py:957-1048]() |
| `/webhooks/linear` | POST | Linear comment webhooks | `linear_webhook` [agent/webapp.py:833-948]() |
| `/webhooks/linear` | GET | Linear webhook verification | `linear_webhook_verify` [agent/webapp.py:951-954]() |
| `/webhooks/github` | POST | GitHub issue/PR webhooks | `github_webhook` [agent/webapp.py:1050-1376]() |

All endpoints are defined in the FastAPI application instance `app = FastAPI()` at [agent/webapp.py:101](). The server communicates with a LangGraph backend via `LANGGRAPH_URL` [agent/webapp.py:127-129]().

**Sources:** [agent/webapp.py:101](), [agent/webapp.py:127-129](), [agent/webapp.py:833-1376]()

---

## Signature Verification

Each webhook endpoint verifies the request signature before processing to ensure requests originate from the claimed source. Requests with invalid or missing signatures are rejected with HTTP 401.

### Verification Process by Platform

```mermaid
graph LR
    subgraph Slack
        SlackReq["Request Headers:<br/>X-Slack-Signature<br/>X-Slack-Request-Timestamp"]
        SlackVerify["verify_slack_signature()"]
        SlackSecret["SLACK_SIGNING_SECRET<br/>(env var)"]
        SlackAlgo["HMAC-SHA256:<br/>v0:timestamp:body"]
        
        SlackReq --> SlackVerify
        SlackSecret --> SlackVerify
        SlackVerify --> SlackAlgo
    end
    
    subgraph Linear
        LinearReq["Request Header:<br/>Linear-Signature"]
        LinearVerify["verify_linear_signature()"]
        LinearSecret["LINEAR_WEBHOOK_SECRET<br/>(env var)"]
        LinearAlgo["HMAC-SHA256:<br/>body"]
        
        LinearReq --> LinearVerify
        LinearSecret --> LinearVerify
        LinearVerify --> LinearAlgo
    end
    
    subgraph GitHub
        GitHubReq["Request Header:<br/>X-Hub-Signature-256"]
        GitHubVerify["verify_github_signature()"]
        GitHubSecret["GITHUB_WEBHOOK_SECRET<br/>(env var)"]
        GitHubAlgo["HMAC-SHA256:<br/>sha256=hash"]
        
        GitHubReq --> GitHubVerify
        GitHubSecret --> GitHubVerify
        GitHubVerify --> GitHubAlgo
    end
```

### Implementation Details

**Slack Verification** ([agent/utils/slack.py:83]()):
- Uses `X-Slack-Signature` and `X-Slack-Request-Timestamp` headers.
- Constructs base string: `v0:{timestamp}:{body_utf8}`.
- Computes HMAC-SHA256 with `SLACK_SIGNING_SECRET`.
- Rejects requests older than 300 seconds (replay protection).
- Uses constant-time comparison via `hmac.compare_digest()`.

**Linear Verification** ([agent/webapp.py:813-830]()):
- Uses `Linear-Signature` header.
- Directly computes HMAC-SHA256 of request body using `LINEAR_WEBHOOK_SECRET`.
- Uses constant-time comparison.

**GitHub Verification** ([agent/utils/github_comments.py:57]()):
- Uses `X-Hub-Signature-256` header (format: `sha256={hex}`).
- Computes HMAC-SHA256 of request body using `GITHUB_WEBHOOK_SECRET`.
- Uses constant-time comparison.

All verifications return `False` if the corresponding secret environment variable is not configured, causing the webhook to reject all requests with HTTP 401.

**Sources:** [agent/utils/slack.py:83](), [agent/webapp.py:813-830](), [agent/utils/github_comments.py:57]()

---

## Event Filtering and Validation

After signature verification, each webhook endpoint parses the JSON payload and applies platform-specific filters to determine if the event should trigger agent execution.

### Slack Event Filtering

```mermaid
graph TD
    SlackEvent["Slack Event Payload"]
    URLVerif["type == 'url_verification'?"]
    EventCB["type == 'event_callback'?"]
    AppMention["event.type == 'app_mention'?"]
    MessageMention["type == 'message' &&<br/>(@bot_username || <@bot_id>)?"]
    BotMsg["event.subtype == 'bot_message' ||<br/>event.bot_id exists?"]
    
    SlackEvent --> URLVerif
    URLVerif -->|Yes| ReturnChallenge["Return {'challenge': ...}"]
    URLVerif -->|No| EventCB
    EventCB -->|No| IgnoreNotEvent["Ignore: Not event_callback"]
    EventCB -->|Yes| AppMention
    AppMention -->|Yes| BotMsg
    AppMention -->|No| MessageMention
    MessageMention -->|Yes| BotMsg
    MessageMention -->|No| IgnoreNotMention["Ignore: Not app_mention"]
    BotMsg -->|Yes| IgnoreBot["Ignore: Event from bot"]
    BotMsg -->|No| ProcessSlack["Process Slack Mention<br/>process_slack_mention()"]
```

Implementation: [agent/webapp.py:979-1028]()

**Sources:** [agent/webapp.py:957-1048]()

### Linear Event Filtering

```mermaid
graph TD
    LinearEvent["Linear Event Payload"]
    TypeCheck["type == 'Comment'?"]
    ActionCheck["action == 'create'?"]
    BotCheck["data.botActor exists?"]
    BotPrefix["body starts with bot prefix?<br/>(🔐, ✅, 🤖, ❌)"]
    OpenSWEMention["'@openswe' in body.lower()?"]
    OrgAllow["Repo org in ALLOWED_GITHUB_ORGS?"]
    
    LinearEvent --> TypeCheck
    TypeCheck -->|No| IgnoreType["Ignore: Not Comment event"]
    TypeCheck -->|Yes| ActionCheck
    ActionCheck -->|No| IgnoreAction["Ignore: Action not 'create'"]
    ActionCheck -->|Yes| BotCheck
    BotCheck -->|Yes| IgnoreBot["Ignore: Comment from bot"]
    BotCheck -->|No| BotPrefix
    BotPrefix -->|Yes| IgnoreBotMsg["Ignore: Our own bot message"]
    BotPrefix -->|No| OpenSWEMention
    OpenSWEMention -->|No| IgnoreMention["Ignore: No @openswe mention"]
    OpenSWEMention -->|Yes| OrgAllow
    OrgAllow -->|No| IgnoreOrg["Ignore: Org not in allowlist"]
    OrgAllow -->|Yes| ProcessLinear["Process Linear Issue<br/>process_linear_issue()"]
```

Bot message prefixes checked via `_GITHUB_BOT_MESSAGE_PREFIXES` at [agent/webapp.py:164-173]():
- `🔐 **GitHub Authentication Required**`
- `✅ **Pull Request Created**`
- `✅ **Pull Request Updated**`
- `🤖 **Agent Response**`
- `❌ **Agent Error**`

Implementation: [agent/webapp.py:855-927]()

**Sources:** [agent/webapp.py:164-173](), [agent/webapp.py:833-948]()

### GitHub Event Filtering

GitHub webhook filtering is more complex due to multiple event types (issues, issue comments, PR reviews, PR review comments).

```mermaid
graph TD
    GitHubEvent["GitHub Event Payload<br/>(X-GitHub-Event header)"]
    EventType["Event type?"]
    
    EventType -->|issues| IssuesAction["action in<br/>(opened, edited)?"]
    EventType -->|issue_comment| IssueCommentAction["action == 'created'?"]
    EventType -->|pull_request_review| ReviewAction["action == 'submitted'?"]
    EventType -->|pull_request_review_comment| ReviewCommentAction["action == 'created'?"]
    EventType -->|other| IgnoreEventType["Ignore: Unsupported event type"]
    
    IssuesAction -->|No| IgnoreIssuesAction["Ignore: Action not supported"]
    IssuesAction -->|Yes| IssuesBodyChange["Edited: body or title changed?"]
    IssuesBodyChange -->|No| IgnoreNoChange["Ignore: No body/title change"]
    IssuesBodyChange -->|Yes| OpenSWECheck
    
    IssueCommentAction -->|No| IgnoreCommentAction["Ignore: Comment not created"]
    IssueCommentAction -->|Yes| OpenSWECheck
    
    ReviewAction -->|No| IgnoreReviewAction["Ignore: Review not submitted"]
    ReviewAction -->|Yes| OpenSWECheck
    
    ReviewCommentAction -->|No| IgnoreReviewCommentAction["Ignore: Comment not created"]
    ReviewCommentAction -->|Yes| OpenSWECheck
    
    OpenSWECheck["@openswe in comment/body/title?<br/>(case-insensitive)"]
    OpenSWECheck -->|No| IgnoreMention["Ignore: No @openswe mention"]
    OpenSWECheck -->|Yes| OrgCheck["Repo org in ALLOWED_GITHUB_ORGS?"]
    OrgCheck -->|No| IgnoreOrg["Ignore: Org not in allowlist"]
    OrgCheck -->|Yes| UserMap["sender.login in<br/>GITHUB_USER_EMAIL_MAP?"]
    UserMap -->|No| IgnoreUser["Ignore: User not in allowlist"]
    UserMap -->|Yes| ProcessGitHub["Process GitHub Issue<br/>process_github_issue()"]
```

Implementation: [agent/webapp.py:1050-1376]()

**Sources:** [agent/webapp.py:1050-1376](), [agent/utils/github_user_email_map.py:1-10]()

---

## Background Task Dispatch

All three webhook endpoints use FastAPI's `BackgroundTasks` [agent/webapp.py:14]() to dispatch event processing asynchronously, allowing the webhook to return HTTP 200 immediately while processing continues in the background.

```mermaid
sequenceDiagram
    participant Client as "Webhook Source<br/>(Slack/Linear/GitHub)"
    participant Endpoint as "FastAPI Endpoint<br/>@app.post('/webhooks/*')"
    participant BG as "BackgroundTasks"
    participant Processor as "Processor Function<br/>(process_*)"
    
    Client->>Endpoint: POST /webhooks/*
    Endpoint->>Endpoint: verify_signature()
    Endpoint->>Endpoint: parse JSON
    Endpoint->>Endpoint: filter event
    Endpoint->>BG: background_tasks.add_task(process_*, ...)
    Endpoint-->>Client: HTTP 200 {'status': 'accepted'}
    
    BG->>Processor: execute process_linear_issue() /<br/>process_slack_mention() /<br/>process_github_issue()
    Processor->>Processor: fetch full context
    Processor->>Processor: assemble prompt
    Processor->>Processor: check thread status
    Processor->>Processor: queue message or create run
```

### Background Task Functions

| Platform | Background Function | Signature | File Location |
|----------|-------------------|-----------|---------------|
| Linear | `process_linear_issue()` | `(issue_data: dict, repo_config: dict)` | [agent/webapp.py:481-695]() |
| Slack | `process_slack_mention()` | `(event_data: dict, repo_config: dict)` | [agent/webapp.py:698-810]() |
| GitHub | `process_github_issue()` | `(payload: dict, event_type: str)` | [agent/webapp.py:1122-1376]() |

The background task pattern ensures webhook endpoints respond within the timeout limits imposed by external platforms (typically 3-5 seconds), preventing retries and duplicate events.

**Sources:** [agent/webapp.py:481-810](), [agent/webapp.py:1122-1376]()

---

## Thread Status Checking and Concurrency Control

Before creating a LangGraph run, the background processor checks if the thread is already active (has a running run). This prevents race conditions when multiple events arrive for the same thread.

### Thread Status Check Flow

```mermaid
graph TD
    CheckStatus["is_thread_active(thread_id)"]
    GetThread["langgraph_client.threads.get(thread_id)"]
    ThreadStatus["thread['status']"]
    
    CheckStatus --> GetThread
    GetThread -->|Success| ThreadStatus
    GetThread -->|Exception<br/>(404, timeout)| AssumeFalse["Assume status = 'idle'<br/>(thread not found or unreachable)"]
    
    ThreadStatus -->|"status == 'busy'"| ReturnTrue["Return True<br/>(thread is active)"]
    ThreadStatus -->|"status == 'idle'"| ReturnFalse["Return False<br/>(thread is idle)"]
    ThreadStatus -->|Other| ReturnFalse
    
    AssumeFalse --> ReturnFalse
```

Implementation at [agent/utils/thread_ops.py:90]():

```python
async def is_thread_active(thread_id: str) -> bool:
    """Check if a thread is currently active (has a running run)."""
    langgraph_client = get_client(url=LANGGRAPH_URL)
    try:
        thread = await langgraph_client.threads.get(thread_id)
        status = thread.get("status", "idle")
        logger.info("Thread %s status check: status=%s", thread_id, status)
    except Exception as e:
        logger.warning("Failed to get thread status for %s: assuming not active", thread_id)
        status = "idle"
    return status == "busy"
```

### Concurrency Control: Queue vs Create

```mermaid
graph TD
    ThreadActive["is_thread_active(thread_id)"]
    
    ThreadActive -->|"True<br/>(status == 'busy')"| Queue["Queue Message<br/>queue_message_for_thread()"]
    ThreadActive -->|"False<br/>(status == 'idle')"| CreateRun["Create LangGraph Run<br/>langgraph_client.runs.create()"]
    
    Queue --> StoreAPI["LangGraph Store API<br/>PUT /store/items"]
    Queue --> Namespace["namespace: ('queue', thread_id)<br/>key: 'pending_messages'"]
    Queue --> Append["Append to messages array:<br/>{'content': prompt_or_payload}"]
    
    CreateRun --> RunAPI["LangGraph Runs API<br/>POST /threads/{thread_id}/runs"]
    CreateRun --> Strategy["multitask_strategy:<br/>'interrupt' (Slack only)<br/>None (Linear/GitHub)"]
```

Implementation at [agent/utils/thread_ops.py:90]():

The `queue_message_for_thread()` function stores messages in the LangGraph Store API using namespace `("queue", thread_id)` and key `"pending_messages"`. The store maintains a FIFO list of queued messages. The `check_message_queue_before_model` middleware retrieves and injects these queued messages before the next LLM invocation.

**Sources:** [agent/utils/thread_ops.py:90](), [agent/webapp.py:665-695](), [agent/webapp.py:801-810]()

---

## Context Assembly and Prompt Construction

Each background processor fetches additional context from external APIs and constructs a prompt tailored to the invocation source.

### Linear Context Assembly

```mermaid
graph LR
    WebhookData["Webhook Payload<br/>(basic issue info)"]
    FetchIssue["fetch_linear_issue_details()<br/>Linear GraphQL API"]
    
    WebhookData --> Extract["Extract:<br/>- triggering_comment<br/>- triggering_comment_id<br/>- comment_author"]
    FetchIssue --> FullIssue["Full Issue Data:<br/>- description<br/>- all comments<br/>- team + project<br/>- creator + assignee"]
    
    Extract --> Merge["Merge Data"]
    FullIssue --> Merge
    
    Merge --> FilterComments["Filter Comments:<br/>- Skip bot messages<br/>- get_recent_comments()<br/>- OR use triggering_comment index"]
    
    FilterComments --> Images["extract_image_urls()<br/>from description + comments"]
    Images --> Blocks["Assemble Content Blocks:<br/>- Text block with prompt<br/>- Image blocks (multimodal)"]
    
    Blocks --> Prompt["Final Prompt:<br/>'Please work on the following issue...'<br/>+ title + description + comments<br/>+ image attachments"]
```

Implementation at [agent/webapp.py:481-641]():

Key details:
- Webhook payload contains minimal issue info; `fetch_linear_issue_details()` retrieves full context via GraphQL.
- Recent comments are filtered using `get_recent_comments()` at [agent/utils/comments.py:40]() to exclude bot responses.
- If `triggering_comment_id` is provided, all comments from that index onwards are included [agent/webapp.py:564-573]().
- Image URLs are extracted from Markdown content via `extract_image_urls()` and fetched as multimodal content blocks via `fetch_image_block()` [agent/utils/multimodal.py:64]().

**Sources:** [agent/webapp.py:481-641](), [agent/utils/comments.py:40](), [agent/utils/multimodal.py:64]()

### Slack Context Assembly

```mermaid
graph LR
    EventData["Slack Event Data<br/>(current message only)"]
    FetchThread["fetch_slack_thread_messages()<br/>conversations.replies API"]
    UserInfo["get_slack_user_info()<br/>users.info API"]
    
    EventData --> Extract["Extract:<br/>- channel_id<br/>- thread_ts<br/>- user_id<br/>- text"]
    FetchThread --> AllMessages["All Thread Messages<br/>(up to 200 per page)"]
    UserInfo --> Profile["User Profile:<br/>- email<br/>- display_name<br/>- real_name"]
    
    Extract --> Merge["Merge Event into Thread"]
    AllMessages --> Merge
    
    Merge --> ContextSelect["select_slack_context_messages()<br/>(thread start or last mention)"]
    ContextSelect --> UserNames["get_slack_user_names()<br/>(batch fetch for all users)"]
    UserNames --> Format["format_slack_messages_for_prompt()"]
    
    Format --> Prompt["Final Prompt:<br/>'You were mentioned in Slack...'<br/>+ repo info<br/>+ conversation context<br/>+ latest mention request"]
```

Implementation at [agent/webapp.py:698-784]():

Key details:
- `select_slack_context_messages()` determines whether to include the full thread or only messages since the last bot mention [agent/utils/slack.py:79]().
- User IDs are batch-resolved to display names via `get_slack_user_names()` [agent/utils/slack.py:72]().
- Bot mentions are replaced with bot usernames for readability via `strip_bot_mention()` [agent/utils/slack.py:82]().

**Sources:** [agent/webapp.py:698-784](), [agent/utils/slack.py:72-82]()

### GitHub Context Assembly

```mermaid
graph LR
    PayloadData["Webhook Payload"]
    ExtractPR["extract_pr_context()<br/>(repo, PR number, branch, login)"]
    
    PayloadData --> EventType["Event Type:<br/>- issue_comment<br/>- pull_request_review<br/>- pull_request_review_comment"]
    
    EventType -->|issue_comment<br/>on PR| FetchBranch["fetch_pr_branch()<br/>(GitHub API)"]
    EventType -->|PR review events| DirectBranch["Branch from<br/>payload.pull_request.head.ref"]
    
    FetchBranch --> Branch["Branch Name<br/>(for thread ID)"]
    DirectBranch --> Branch
    
    Branch --> ThreadID["get_thread_id_from_branch()<br/>(UUID extraction)"]
    ThreadID --> ExistingThread["Thread Exists?<br/>_thread_exists()"]
    
    ExistingThread -->|No| FetchIssue["fetch_issue_comments()<br/>(all comments)"]
    ExistingThread -->|Yes| FetchRecent["fetch_pr_comments_since_last_tag()<br/>(comments since last @openswe)"]
    
    FetchIssue --> BuildPrompt["build_github_issue_prompt()<br/>(full issue context)"]
    FetchRecent --> BuildFollowup["build_github_issue_followup_prompt()<br/>(just the new comment)"]
    
    BuildPrompt --> Prompt["Final Prompt"]
    BuildFollowup --> Prompt
```

Implementation at [agent/webapp.py:1122-1376]():

Key details:
- For PR-related events, thread ID is extracted from the branch name using `get_thread_id_from_branch()` [agent/utils/github_comments.py:53]().
- For new threads, `fetch_issue_comments()` retrieves all comments [agent/utils/github_comments.py:50]().
- For existing threads, `fetch_pr_comments_since_last_tag()` fetches only comments since the previous `@openswe` mention [agent/utils/github_comments.py:51]().
- Comments from untrusted users (not in `GITHUB_USER_EMAIL_MAP`) are wrapped in warning tags via `format_github_comment_body_for_prompt()` [agent/utils/github_comments.py:52]().

**Sources:** [agent/webapp.py:1122-1376](), [agent/utils/github_comments.py:50-53](), [agent/utils/github_user_email_map.py:1-10]()

---

## LangGraph Run Creation

After assembling the prompt and checking thread status, the processor creates a LangGraph run via the `langgraph_client.runs.create()` API.

### Run Configuration Structure

```mermaid
graph TD
    CreateRun["langgraph_client.runs.create()"]
    
    CreateRun --> ThreadID["thread_id:<br/>Deterministic UUID"]
    CreateRun --> Assistant["assistant_id:<br/>'agent'"]
    CreateRun --> Input["input:<br/>{'messages': [...]}"]
    CreateRun --> Config["config:<br/>{'configurable': {...},<br/>'metadata': {...}}"]
    
    Input --> Messages["messages[0]:<br/>role: 'user'<br/>content: [text_block, image_blocks...]"]
    
    Config --> Configurable["configurable:<br/>- repo: {owner, name}<br/>- linear_issue / slack_thread / github_issue<br/>- user_email<br/>- source: 'linear'/'slack'/'github'"]
    Config --> Metadata["metadata:<br/>- LANGSMITH_AGENT_VERSION"]
    
    Config --> Strategy["multitask_strategy:<br/>'interrupt' (Slack only)<br/>None (Linear/GitHub)"]
```

### Configurable Fields by Source

| Field | Linear | Slack | GitHub |
|-------|--------|-------|--------|
| `repo` | `{owner, name}` from team mapping | `{owner, name}` from message or thread metadata | `{owner, name}` from webhook payload |
| `source` | `"linear"` | `"slack"` | `"github"` |
| `user_email` | Comment author or assignee email | Slack user profile email | Mapped via `GITHUB_USER_EMAIL_MAP` |

Implementation examples:
- Linear: [agent/webapp.py:650-693]()
- Slack: [agent/webapp.py:787-810]()
- GitHub: [agent/webapp.py:1311-1376]()

### Multitask Strategy

Only Slack uses `multitask_strategy="interrupt"` [agent/webapp.py:809](), which tells LangGraph to interrupt any currently running task on the thread and start the new one immediately. Linear and GitHub use the default strategy (queue the run if thread is busy), relying on the message queueing system.

**Sources:** [agent/webapp.py:650-693](), [agent/webapp.py:787-810](), [agent/webapp.py:1311-1376]()

---

## Error Handling and Edge Cases

### Signature Verification Failures

All endpoints reject requests with invalid or missing signatures with HTTP 401 [agent/webapp.py:846-847](), [agent/webapp.py:970-971]():

```python
if not verify_*_signature(...):
    logger.warning("Invalid webhook signature")
    raise HTTPException(status_code=401, detail="Invalid signature")
```

### Missing Environment Variables

If webhook secrets are not configured, the verification functions return `False` and log a warning:
- Slack: [agent/utils/slack.py:83]()
- Linear: [agent/webapp.py:813-830]()
- GitHub: [agent/utils/github_comments.py:57]()

This ensures the system fails closed (rejects all webhooks) rather than accepting unverified requests.

### API Failures During Context Fetching

If external API calls fail during context assembly (e.g., Linear GraphQL, Slack users.info, GitHub API), the processors fall back gracefully:

- **Linear**: If GraphQL details fail, the system logs the error and continues with available data [agent/webapp.py:481-641]().
- **Slack**: If `get_slack_user_info()` fails, the system handles it via logging and fallback [agent/utils/slack.py:71]().
- **GitHub**: If `fetch_issue_comments()` fails, it returns an empty list [agent/utils/github_comments.py:50]().

### Thread Creation Race Conditions

When multiple events arrive simultaneously for a new thread, the `if_not_exists="create"` parameter ensures only one thread is created [agent/webapp.py:693](). Subsequent events detect the thread exists and queue their messages.

**Sources:** [agent/webapp.py:481-693](), [agent/utils/slack.py:71-83](), [agent/utils/github_comments.py:50-57]()

---

## Complete Flow Example: Linear Webhook

This diagram shows the complete request flow for a Linear issue comment webhook:

```mermaid
sequenceDiagram
    participant Linear as "Linear Platform"
    participant Webhook as "POST /webhooks/linear"
    participant Verify as "verify_linear_signature()"
    participant BG as "process_linear_issue()"
    participant API as "Linear GraphQL API"
    participant Thread as "is_thread_active()"
    participant LG as "LangGraph Client"
    
    Linear->>Webhook: POST with Linear-Signature header
    Webhook->>Verify: verify(body, signature, secret)
    Verify-->>Webhook: True (valid)
    
    Webhook->>Webhook: Parse JSON payload
    Webhook->>Webhook: Filter: type=='Comment', action=='create'
    Webhook->>Webhook: Filter: '@openswe' in body
    Webhook->>BG: background_tasks.add_task(process_linear_issue, ...)
    Webhook-->>Linear: HTTP 200 {'status': 'accepted'}
    
    BG->>BG: generate_thread_id_from_issue(issue_id)
    BG->>BG: react_to_linear_comment(comment_id, "👀")
    BG->>API: GraphQL query: GetIssue(issue_id)
    API-->>BG: Full issue data (description, comments, team, project)
    
    BG->>BG: Filter recent comments (get_recent_comments)
    BG->>BG: Extract image URLs from description + comments
    BG->>BG: Assemble content blocks (text + images)
    BG->>BG: Build configurable dict (repo, linear_issue, user_email)
    
    BG->>Thread: is_thread_active(thread_id)
    Thread->>LG: GET /threads/{thread_id}
    LG-->>Thread: {'status': 'idle'}
    Thread-->>BG: False (not active)
    
    BG->>LG: runs.create(thread_id, 'agent', input, config)
    LG-->>BG: Run created
```

**Sources:** [agent/webapp.py:833-948](), [agent/webapp.py:481-695]()

---

# Page: Agent Core

# Agent Core

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CUSTOMIZATION.md](CUSTOMIZATION.md)
- [INSTALLATION.md](INSTALLATION.md)
- [README.md](README.md)
- [agent/server.py](agent/server.py)
- [agent/tools/__init__.py](agent/tools/__init__.py)

</details>



The Agent Core is the internal architecture of the agent itself—how it is assembled, what components it uses, and how it executes tasks. This page documents the `create_deep_agent` function and the modular components that make up the agent: models, tools, middleware, and subagent orchestration.

For information about how agents are triggered, see [Invocation Surfaces](#2). For sandbox execution environments, see [Sandbox Execution](#4). For context engineering via AGENTS.md, see [Context Engineering](#5).

---

## Agent Assembly

The agent is assembled in the `get_agent()` function in [agent/server.py:249-376](). This function is called by the LangGraph server whenever a new task is triggered via webhook. It provisions a sandbox, constructs the system prompt, and passes all components to `create_deep_agent()` from the Deep Agents framework.

### Agent Assembly Flow

```mermaid
graph TB
    LGServer["LangGraph Server<br/>langgraph.runs.create()"]
    GetAgent["get_agent()<br/>agent/server.py:249"]
    
    subgraph "Sandbox Provisioning"
        CheckCache["Check SANDBOX_BACKENDS<br/>in-memory cache"]
        CheckMeta["Check thread metadata<br/>for sandbox_id"]
        CreateNew["_create_sandbox_with_proxy()<br/>agent/server.py:121"]
        CacheBackend["Store in SANDBOX_BACKENDS"]
    end
    
    subgraph "Repository Setup"
        ResolveDir["aresolve_sandbox_work_dir()<br/>agent/utils/sandbox_paths.py:34"]
        CloneRepo["_clone_or_pull_repo_in_sandbox()<br/>agent/server.py:441"]
        ReadAgentsMD["read_agents_md_in_sandbox()<br/>agent/utils/agents_md.py"]
    end
    
    subgraph "Agent Construction"
        MakeModel["make_model()<br/>agent/utils/model.py"]
        ConstructPrompt["construct_system_prompt()<br/>agent/prompt.py"]
        LoadTools["Load tool suite<br/>commit_and_open_pr, etc."]
        LoadMiddleware["Load middleware<br/>check_message_queue, etc."]
        CreateDeep["create_deep_agent()<br/>deepagents"]
    end
    
    LGServer --> GetAgent
    GetAgent --> CheckCache
    CheckCache -->|cache miss| CheckMeta
    CheckMeta --> CreateNew
    CreateNew --> CacheBackend
    CacheBackend --> ResolveDir
    CheckCache -->|cache hit| ResolveDir
    
    ResolveDir --> CloneRepo
    CloneRepo --> ReadAgentsMD
    
    ReadAgentsMD --> MakeModel
    ReadAgentsMD --> ConstructPrompt
    GetAgent --> LoadTools
    GetAgent --> LoadMiddleware
    
    MakeModel --> CreateDeep
    ConstructPrompt --> CreateDeep
    LoadTools --> CreateDeep
    LoadMiddleware --> CreateDeep
    CacheBackend --> CreateDeep
    
    CreateDeep --> PregelGraph["Pregel<br/>Agent execution graph"]
```

**Sources:** [agent/server.py:249-376](), [agent/server.py:121-140](), [agent/server.py:441-525](), [agent/utils/sandbox_paths.py:34-56](), [agent/utils/sandbox_state.py:15-16]()

### The `get_agent()` Function

The `get_agent()` function follows this sequence:

1. **Extract configuration** from `RunnableConfig.configurable`:
   - `thread_id`: Unique identifier for the conversation thread. [agent/server.py:257]()
   - `repo`: `{"owner": "...", "name": "..."}` identifying the GitHub repository. [agent/server.py:261]()
   - `user_email`: Triggering user's email for GitHub OAuth resolution. [agent/server.py:262]()

2. **Provision sandbox**: Check `SANDBOX_BACKENDS` cache. If not found, check thread metadata for `sandbox_id`. If present, reconnect. Otherwise, create new sandbox via `_create_sandbox_with_proxy()`. [agent/server.py:273-305]()

3. **Set up repository**: Resolve working directory and clone or pull the repository via `_clone_or_pull_repo_in_sandbox()`. [agent/server.py:321-325]()

4. **Read context**: Read `AGENTS.md` from sandbox if it exists. [agent/server.py:330]() Assemble source context from Linear issue, Slack thread, or GitHub PR.

5. **Construct agent**: Call `create_deep_agent()` with model, system prompt, tools, sandbox backend, and middleware. [agent/server.py:356-364]()

6. **Store metadata**: Persist `sandbox_id`, encrypted GitHub token, and repository directory in thread metadata for reuse. [agent/server.py:366-373]()

**Sources:** [agent/server.py:249-376]()

---

## Model Configuration

The model is configured via the `make_model()` helper in [agent/utils/model.py]() and passed to `create_deep_agent()`. The default configuration typically uses reasoning-enabled models.

### Model Selection

The `make_model()` function wraps `langchain.chat_models.init_chat_model`. For OpenAI models, it automatically enables specific reasoning kwargs if supported. [agent/utils/model.py:73-79]()

| Provider | Example | Notes |
|----------|---------|-------|
| OpenAI | `"openai:gpt-4o"` | Default with reasoning effort [agent/server.py:73-79]() |
| Anthropic | `"anthropic:claude-3-5-sonnet-latest"` | Supported via `LLM_MODEL_ID` [CUSTOMIZATION.md:140]() |

### Dynamic Model Selection

The `get_agent()` function can route to different models based on user profiles or team settings. [agent/server.py:35-42]()

**Sources:** [agent/server.py:73-79](), [agent/utils/model.py](), [CUSTOMIZATION.md:134-162]()

---

## Tool System

The agent has access to two categories of tools: **Deep Agents built-ins** (inherited from the framework) and **Open SWE custom tools** (defined in [agent/tools/]()).

### Tool Categories

```mermaid
graph LR
    subgraph "Deep Agents Built-in Tools"
        ReadFile["read_file<br/>Read file contents"]
        WriteFile["write_file<br/>Create/overwrite file"]
        EditFile["edit_file<br/>Apply diffs to file"]
        LS["ls<br/>List directory"]
        Glob["glob<br/>Pattern matching"]
        Grep["grep<br/>Search files"]
        TaskTool["task<br/>Spawn subagent"]
    end
    
    subgraph "Open SWE Custom Tools"
        Execute["execute<br/>Shell commands"]
        FetchURL["fetch_url<br/>Web content as markdown"]
        HTTPRequest["http_request<br/>Generic HTTP calls"]
        LinearComment["linear_comment<br/>Post to Linear"]
        SlackReply["slack_thread_reply<br/>Reply in Slack"]
        WebSearch["web_search<br/>Search the web"]
    end
    
    Agent["Agent<br/>create_deep_agent()"]
    
    ReadFile --> Agent
    WriteFile --> Agent
    EditFile --> Agent
    LS --> Agent
    Glob --> Agent
    Grep --> Agent
    TaskTool --> Agent
    
    Execute --> Agent
    FetchURL --> Agent
    HTTPRequest --> Agent
    LinearComment --> Agent
    SlackReply --> Agent
    WebSearch --> Agent
```

**Sources:** [agent/server.py:55-69](), [agent/tools/__init__.py:1-37]()

### Built-in Tools from Deep Agents

These tools are inherited automatically when calling `create_deep_agent()`:

| Tool | Purpose | Implementation |
|------|---------|----------------|
| `read_file` | Read file contents from sandbox | `SandboxBackendProtocol.read()` |
| `write_file` | Create or overwrite file | `SandboxBackendProtocol.write()` |
| `edit_file` | Apply diffs to existing file | `SandboxBackendProtocol.edit()` |
| `ls` | List directory contents | `SandboxBackendProtocol.ls_info()` |
| `glob` | Pattern-based file search | `SandboxBackendProtocol.glob_info()` |
| `grep` | Search file contents | `SandboxBackendProtocol.grep_raw()` |
| `task` | Spawn subagent for subtask | Deep Agents orchestration |

### Custom Tools in Open SWE

Custom tools are defined in [agent/tools/]() and registered in the `get_agent()` function. [agent/server.py:336-354]()

#### Sandbox Shell Access

The `execute` tool allows the agent to run arbitrary shell commands within the isolated environment. This is used for running tests, linters, and the `gh` CLI.

#### Other Custom Tools

| Tool | File | Purpose |
|------|------|---------|
| `fetch_url` | [agent/tools/fetch_url.py]() | Fetch web pages as markdown. |
| `http_request` | [agent/tools/http_request.py]() | Generic HTTP API calls. |
| `linear_comment` | [agent/tools/linear_comment.py]() | Post status updates to Linear. |
| `slack_thread_reply` | [agent/tools/slack_thread_reply.py]() | Reply in Slack threads. |
| `web_search` | [agent/tools/web_search.py]() | Perform web searches for external context. |

**Sources:** [agent/server.py:55-69](), [agent/tools/__init__.py:1-37]()

---

## Middleware System

Middleware hooks run around the agent loop at specific lifecycle points. Open SWE uses several middleware components to extend agent behavior.

### Middleware Execution Flow

```mermaid
graph TB
    Start["Agent Execution Start"]
    
    subgraph "Before Model Hooks"
        CheckQueue["check_message_queue_before_model<br/>agent/middleware/__init__.py"]
        EnsureNoEmpty["ensure_no_empty_msg<br/>Prevent empty messages"]
    end
    
    subgraph "Agent Loop"
        LLMCall["LLM generates next action"]
        ToolCall["Execute tool<br/>(e.g., write_file, execute)"]
        ToolError["ToolErrorMiddleware<br/>Catch and format errors"]
    end
    
    subgraph "After Agent Hooks"
        NotifyLimit["notify_step_limit_reached<br/>agent/middleware/__init__.py"]
    end
    
    Start --> CheckQueue
    CheckQueue --> EnsureNoEmpty
    EnsureNoEmpty --> LLMCall
    LLMCall --> ToolCall
    ToolCall --> ToolError
    ToolError -->|more actions| LLMCall
    ToolError -->|done| NotifyLimit
    NotifyLimit --> End["Agent Execution End"]
```

**Sources:** [agent/server.py:44-53](), [README.md:91-96]()

### Middleware Components

| Middleware | Type | Source | Purpose |
|------------|------|------|---------|
| `ToolErrorMiddleware` | Tool error handler | [agent/server.py:49]() | Catches and handles tool errors gracefully. |
| `check_message_queue_before_model` | `@before_model` | [agent/server.py:50]() | Injects follow-up messages (Slack/Linear) mid-run. |
| `ensure_no_empty_msg` | `@before_model` | [agent/server.py:51]() | Prevents empty messages from reaching the model. |
| `notify_step_limit_reached` | `@after_agent` | [agent/server.py:52]() | Posts a Slack reply when the agent hits the model-call limit. |
| `ModelFallbackMiddleware` | `@after_model` | [agent/server.py:45]() | Handles model-specific failures by retrying with fallbacks. |

**Sources:** [agent/server.py:44-53]()

---

## Subagent Orchestration

The `task` tool from Deep Agents enables spawning child agents for parallel work decomposition. Each subagent runs in its own isolated sandbox with independent middleware and state.

### Subagent Architecture

```mermaid
graph TB
    MainAgent["Main Agent<br/>Thread: linear-issue-123"]
    
    subgraph "Main Agent Sandbox"
        MainSandbox["Sandbox 1<br/>sandbox_id: abc123"]
        MainRepo["/workspace/repo-name"]
    end
    
    TaskTool["task tool<br/>deepagents.tools.task"]
    
    subgraph "Subagent 1"
        Sub1["Subagent<br/>Task: Refactor auth module"]
        Sub1Sandbox["Sandbox 2<br/>sandbox_id: def456"]
        Sub1Repo["/workspace/repo-name"]
    end
    
    MainAgent --> MainSandbox
    MainSandbox --> MainRepo
    MainAgent --> TaskTool
    
    TaskTool --> Sub1
    
    Sub1 --> Sub1Sandbox
    Sub1Sandbox --> Sub1Repo
    
    Sub1 --> Results["Subagent results<br/>merged back to main agent"]
    Results --> MainAgent
```

When the main agent calls the `task` tool, Deep Agents creates a new agent instance with the same configuration. The subagent provisions its own isolated sandbox and clones the repository independently, allowing for parallelized execution without file-system conflicts.

**Sources:** [README.md:87-89]()

---

## Agent Execution Loop

Once assembled, the agent executes as a Pregel graph managed by LangGraph. The core loop alternates between LLM decision-making and tool execution until the task is complete.

### Execution Flow

```mermaid
graph TB
    Start["Agent Start<br/>Initial user message"]
    
    BeforeModel["Before Model Middleware<br/>check_message_queue<br/>ensure_no_empty_msg"]
    
    LLMCall["LLM Decision<br/>Generate next action"]
    
    Decision{"Action Type?"}
    
    ToolExec["Execute Tool<br/>via SandboxBackendProtocol"]
    ToolError["ToolErrorMiddleware<br/>Handle errors"]
    
    Response["Generate Response<br/>LLM synthesizes result"]
    
    AfterAgent["After Agent Middleware<br/>notify_step_limit_reached"]
    
    End["Agent End<br/>Return to LangGraph"]
    
    Start --> BeforeModel
    BeforeModel --> LLMCall
    LLMCall --> Decision
    
    Decision -->|Tool call| ToolExec
    Decision -->|Response| Response
    
    ToolExec --> ToolError
    ToolError --> BeforeModel
    
    Response --> AfterAgent
    AfterAgent --> End
```

**Sources:** [agent/server.py:29-53](), [README.md:91-96]()

### State Management

The agent maintains state in a LangGraph `StateGraph`:
- **Messages**: Conversation history including user messages, tool calls, and tool results.
- **Metadata**: Thread ID, sandbox ID, repository configuration, and authentication tokens. [agent/server.py:366-373]()

State is persisted via LangGraph checkpoints, allowing the agent to resume if interrupted or when follow-up messages arrive.

**Sources:** [agent/server.py:13-16](), [agent/server.py:366-373]()

---

# Page: Agent Assembly

# Agent Assembly

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/integrations/langsmith.py](agent/integrations/langsmith.py)
- [agent/server.py](agent/server.py)
- [agent/tools/__init__.py](agent/tools/__init__.py)
- [pyproject.toml](pyproject.toml)
- [uv.lock](uv.lock)

</details>



This page documents how the Open SWE agent is assembled from modular components in the `get_agent()` factory function. Agent assembly is the process of configuring and instantiating a `deepagents` instance with the appropriate model, system prompt, tools, sandbox backend, and middleware stack for a specific task.

---

## Overview

Agent assembly occurs in the `get_agent()` function at [agent/server.py:249-376](). This function serves as the central factory that:

1.  **Reads configuration** from `RunnableConfig` passed by the LangGraph server [agent/server.py:255-264]().
2.  **Provisions or reconnects** to a sandbox environment using `create_sandbox` [agent/server.py:275-295]().
3.  **Constructs the system prompt** with repository context and `AGENTS.md` guidelines [agent/server.py:324-328]().
4.  **Assembles a Deep Agents instance** via `create_deep_agent` [agent/server.py:322-328]().
5.  **Caches the sandbox backend** for reuse in the `SANDBOX_BACKENDS` global dictionary to maintain state across turns [agent/server.py:330-332]().

The function is called once per thread when the LangGraph server creates a new run. For follow-up messages on the same thread, the cached sandbox is reused, maintaining the filesystem and git state.

**Sources:** [agent/server.py:249-376](), [agent/utils/sandbox_state.py:90-94](), [agent/server.py:29-29]()

---

## The Factory Pattern

The `get_agent()` function follows a deterministic assembly pattern that separates infrastructure concerns from agent logic:

| Phase | Responsibility | Code Entity |
| :--- | :--- | :--- |
| **Configuration extraction** | Read thread ID, repo, and user identity | `configurable` from `RunnableConfig` [agent/server.py:255-264]() |
| **Sandbox provisioning** | Create or reconnect to isolated environment | `create_sandbox` [agent/utils/sandbox.py:80-80]() |
| **Context gathering** | Load repository and `AGENTS.md` | `_clone_or_pull_repo_in_sandbox` [agent/server.py:408-485]() |
| **Component assembly** | Configure model, tools, and middleware | `make_model` [agent/utils/model.py:77-77](), `tools` list [agent/server.py:310-315]() |
| **Instance creation** | Invoke framework factory | `create_deep_agent` [agent/server.py:29-29]() |
| **Caching** | Store sandbox for thread reuse | `SANDBOX_BACKENDS` [agent/utils/sandbox_state.py:90-94]() |

**Sources:** [agent/server.py:249-376](), [agent/utils/sandbox.py:80-80](), [agent/utils/model.py:77-77]()

---

## Configuration Sources

The `get_agent()` function reads configuration from three primary sources to drive assembly:

Title: Configuration to Code Entity Mapping
```mermaid
graph LR
    subgraph "Natural Language Space"
        Thread["Conversation Thread"]
        Repo["Target Repository"]
        User["Triggering User"]
        Provider["Sandbox Provider"]
    end
    
    subgraph "Code Entity Space"
        ThreadID["configurable['thread_id']"]
        RepoCfg["configurable['repo']"]
        UserEmail["configurable['user_email']"]
        SandboxType["os.getenv('SANDBOX_TYPE')"]
        Metadata["metadata['sandbox_id']"]
    end
    
    Thread --- ThreadID
    Repo --- RepoCfg
    User --- UserEmail
    Provider --- SandboxType
    
    ThreadID --> GetAgent["get_agent()"]
    RepoCfg --> GetAgent
    UserEmail --> GetAgent
    SandboxType --> GetAgent
    Metadata --> GetAgent
```

### RunnableConfig Structure

The LangGraph server passes a `RunnableConfig` dictionary. The `configurable` field contains task-specific parameters:

```python
{
    "configurable": {
        "thread_id": "linear-issue-PROJ-123",  # Deterministic ID
        "repo": {"owner": "my-org", "name": "my-repo"},  # Target repository
        "source": "linear",  # Invocation surface (slack, linear, github)
        "user_email": "user@example.com",
    },
    "metadata": {
        "sandbox_id": "abc123xyz",  # Persisted sandbox identifier for reconnection
    }
}
```

The `thread_id` serves as the cache key for sandbox backends in `SANDBOX_BACKENDS` [agent/server.py:276-277]().

**Sources:** [agent/server.py:255-264](), [agent/utils/sandbox_state.py:90-94]()

---

## Component Assembly

The `get_agent()` function assembles core components into the `create_deep_agent` constructor.

### Model Configuration
The model is instantiated via `make_model()` [agent/utils/model.py:77-77](). It defaults to the ID defined in `DEFAULT_MODEL_ID` [agent/dashboard/options.py:10-10](), typically `anthropic:claude-3-5-sonnet-latest`.

### System Prompt Construction
The prompt is assembled by `construct_system_prompt()` [agent/prompt.py:54-54](), which combines:
1.  **Base instructions**: Working environment and coding standards.
2.  **AGENTS.md content**: Repository-specific rules read via `read_agents_md_in_sandbox` [agent/server.py:323-323]().
3.  **Source context**: External issue or thread details (e.g., Slack history or Linear issue description).

### Tool Registration
Tools are registered as a list [agent/server.py:310-315](). Open SWE includes custom tools like `slack_thread_reply` [agent/tools/slack_thread_reply.py:15-15]() and `linear_comment` [agent/tools/linear_comment.py:23-23]().

### Middleware Stack
Middleware hooks wrap the agent loop to provide safety and observability [agent/server.py:316-321]():
- `ToolErrorMiddleware`: Formats execution errors for the LLM.
- `check_message_queue_before_model`: Injects queued events [agent/middleware/message_queue.py:50-50]().
- `SanitizeToolInputsMiddleware`: Cleans LLM-generated tool arguments.

**Sources:** [agent/server.py:310-328](), [agent/prompt.py:54-54](), [agent/middleware/__init__.py:44-53]()

---

## Sandbox Lifecycle Management

Title: get_agent() Lifecycle Logic
```mermaid
graph TB
    Start["get_agent(config)"] --> CheckMem["Check SANDBOX_BACKENDS[thread_id]"]
    
    CheckMem -- "Hit" --> ReturnMem["Return Cached Backend"]
    
    CheckMem -- "Miss" --> CheckMeta["Check metadata['sandbox_id']"]
    
    CheckMeta -- "Exists" --> Reconnect["create_sandbox(sandbox_id)"]
    CheckMeta -- "None" --> CreateNew["_create_sandbox_with_proxy()"]
    
    Reconnect --> RefreshProxy["_refresh_github_proxy_or_recreate()"]
    RefreshProxy --> ClonePull["_clone_or_pull_repo_in_sandbox()"]
    CreateNew --> ClonePull
    
    ClonePull --> ReadMD["read_agents_md_in_sandbox()"]
    ReadMD --> CreateDeep["create_deep_agent()"]
    
    CreateDeep --> Cache["Update SANDBOX_BACKENDS"]
    Cache --> End["Return Agent"]
```

### Sandbox Reconnection
If a `sandbox_id` exists in metadata, the agent reconnects to the existing environment [agent/server.py:284-288](). For LangSmith sandboxes, the system refreshes GitHub proxy credentials via `_refresh_github_proxy_or_recreate` to ensure continued authentication [agent/server.py:162-177]().

### Repository Initialization
The repository is managed via `_clone_or_pull_repo_in_sandbox` [agent/server.py:408-485](). 
- If the directory is missing, it performs a `git clone` [agent/server.py:471-485]().
- If the directory exists and is clean, it performs a `git pull` [agent/server.py:449-469]().
- If there are uncommitted changes, it skips the pull to avoid merge conflicts [agent/server.py:445-447]().

**Sources:** [agent/server.py:408-485](), [agent/server.py:275-295](), [agent/integrations/langsmith.py:126-170]()

---

## GitHub Proxy Authentication

When using LangSmith sandboxes, `_create_sandbox_with_proxy` [agent/server.py:121-139]() configures a proxy to inject GitHub credentials. This allows `git` operations (clone, pull, push) inside the sandbox to succeed without storing permanent tokens on the sandbox disk.

The `_configure_github_proxy` function [agent/integrations/langsmith.py:98-124]() sets up `proxy_config` rules that match `github.com` and inject an `Authorization` header derived from the GitHub App installation token.

**Sources:** [agent/server.py:121-139](), [agent/integrations/langsmith.py:98-124](), [agent/utils/github_app.py:72-72]()

---

# Page: Tool System

# Tool System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [agent/server.py](agent/server.py)
- [agent/tools/__init__.py](agent/tools/__init__.py)
- [agent/tools/fetch_url.py](agent/tools/fetch_url.py)
- [agent/tools/http_request.py](agent/tools/http_request.py)
- [agent/tools/linear_create_issue.py](agent/tools/linear_create_issue.py)
- [agent/tools/linear_delete_issue.py](agent/tools/linear_delete_issue.py)
- [agent/tools/linear_get_issue.py](agent/tools/linear_get_issue.py)
- [agent/tools/linear_get_issue_comments.py](agent/tools/linear_get_issue_comments.py)
- [agent/tools/linear_list_teams.py](agent/tools/linear_list_teams.py)
- [agent/tools/linear_update_issue.py](agent/tools/linear_update_issue.py)
- [agent/tools/slack_read_thread_messages.py](agent/tools/slack_read_thread_messages.py)
- [tests/test_http_security.py](tests/test_http_security.py)

</details>



This document describes the tool system used by Open SWE agents, including both the Deep Agents framework built-in tools and Open SWE's custom tools. It covers tool registration, execution flow, available tools, and customization patterns.

## Overview

Open SWE agents are equipped with a curated set of tools that enable file manipulation, shell execution, Git operations, web content fetching, and communication with external platforms. The tool system follows the principle of "curation over accumulation" — a small, focused toolset is more effective than a large, general-purpose one.

Tools fall into two categories:

1.  **Deep Agents Built-ins**: File system operations (`read_file`, `write_file`, `edit_file`, `ls`, `glob`, `grep`), and subagent spawning (`task`). [agent/server.py:29-31]()
2.  **Open SWE Custom Tools**: Shell execution (`execute`), Git/GitHub operations (`commit_and_open_pr`, `request_pr_review`), web content (`fetch_url`, `http_request`, `web_search`), and platform communication (`linear_comment`, `slack_thread_reply`, `linear_update_issue`). [agent/tools/__init__.py:1-37]()

Tools are registered by passing them to `create_deep_agent()` within the `get_agent` function. [agent/server.py:55-69]()

**Sources:** [agent/server.py:29-69](), [agent/tools/__init__.py:1-37]()

---

## Tool Architecture

### Tool Registration and Execution Flow

The following diagram illustrates how tools are composed and executed within the agent loop.

**Diagram: Tool Execution and Registration Flow**
```mermaid
graph TB
    subgraph "Agent_Assembly_get_agent"
        [Tool_Definitions] --> [create_deep_agent]
    end
    
    subgraph "Deep_Agents_Core"
        [create_deep_agent] --> [Deep_Agent_Instance]
        [Deep_Agent_Instance] --> [Pregel_Executor]
    end
    
    subgraph "Execution_Loop"
        [LLM_Model] -- "Tool Call" --> [Tool_Router]
        [Tool_Router] -- "Execute" --> [Tool_Implementation]
        [Tool_Implementation] -- "Result" --> [LLM_Model]
    end
    
    subgraph "Target_Surfaces"
        [Tool_Implementation] --> [Sandbox_Backend]
        [Tool_Implementation] --> [GitHub_API]
        [Tool_Implementation] --> [Linear_API]
        [Tool_Implementation] --> [Slack_API]
    end

    [Pregel_Executor] --> [LLM_Model]
```
**Sources:** [agent/server.py:55-69](), [agent/tools/__init__.py:1-37]()

---

### Tool-to-Code Entity Mapping

This diagram bridges natural language tool names to the specific Python functions and backend methods that implement them.

**Diagram: Tool to Code Entity Mapping**
```mermaid
graph LR
    subgraph "Natural_Language_Tools"
        [read_file]
        [execute]
        [http_request]
        [linear_comment]
        [slack_thread_reply]
    end

    subgraph "Python_Implementation"
        [read_file] --> [deepagents_built_in]
        [execute] --> [sandbox_backend_execute]
        [http_request] --> [http_request_fn]
        [linear_comment] --> [linear_comment_fn]
        [slack_thread_reply] --> [slack_thread_reply_fn]
    end

    subgraph "Backend_Methods"
        [deepagents_built_in] --> [SandboxBackendProtocol_read]
        [sandbox_backend_execute] --> [SandboxBackendProtocol_execute]
        [http_request_fn] --> [requests_request]
        [linear_comment_fn] --> [update_issue_or_comment]
        [slack_thread_reply_fn] --> [post_slack_message]
    end
```
**Sources:** [agent/tools/http_request.py:198-210](), [agent/tools/linear_comment.py:1-16](), [agent/tools/slack_thread_reply.py:1-15](), [agent/server.py:180-185]()

---

## Deep Agents Built-in Tools

The Deep Agents framework provides core file system and orchestration tools. These are inherited automatically.

| Tool | Purpose | Key Behavior |
| :--- | :--- | :--- |
| `read_file` | Read file contents | Returns full file content as string. |
| `write_file` | Write/overwrite file | Creates parent directories if needed. |
| `edit_file` | Line-based edits | Uses line ranges for precise modifications. |
| `ls` | List directory | Returns entries with type (file/dir) and size. |
| `glob` | Pattern search | Supports `**` recursive patterns. |
| `grep` | Search contents | Regex search across multiple files. |
| `task` | Spawn subagent | Creates a subagent for parallel work decomposition. |

**Sources:** [agent/server.py:29-31](), [agent/utils/sandbox_paths.py:81-82]()

---

## Open SWE Custom Tools

### Linear Integration Tools
Open SWE provides extensive tools for managing Linear issues, enabling the agent to update its own status and interact with stakeholders.

*   `linear_comment`: Adds a comment to an issue. [agent/tools/linear_comment.py:7-16]()
*   `linear_get_issue`: Retrieves full issue details. [agent/tools/linear_get_issue.py:7-16]()
*   `linear_update_issue`: Updates title, description, priority, or state. [agent/tools/linear_update_issue.py:7-40]()
*   `linear_create_issue`: Creates new issues in a specific team. [agent/tools/linear_create_issue.py:1-15]()
*   `linear_list_teams`: Lists available teams for issue routing. [agent/tools/linear_list_teams.py:7-13]()

### Web and API Tools

#### `http_request`
A secure tool for making HTTP requests. It includes protection against SSRF and DNS-rebinding by validating that target URLs do not resolve to private, loopback, or reserved IP addresses via `_resolve_and_validate`. [agent/tools/http_request.py:125-161]() It uses a `_pin_dns` context to lock the connection to the validated IP address. [agent/tools/http_request.py:91-124]()

#### `fetch_url`
Fetches a URL and converts the content to Markdown using `markdownify` for easier LLM consumption. [agent/tools/fetch_url.py:9-58]()

#### `web_search`
Uses the Exa API to perform web searches for external documentation or troubleshooting. [agent/tools/web_search.py:1-17]()

### Slack and Communication

*   `slack_thread_reply`: Replies to the originating Slack thread to provide status updates. [agent/tools/slack_thread_reply.py:1-15]()
*   `slack_read_thread_messages`: Fetches the entire conversation history of a thread to gather context. [agent/tools/slack_read_thread_messages.py:26-52]()

---

## Tool Security and Authentication

### DNS Rebinding Protection
The `http_request` tool implements a custom connection handler `_pinned_create_connection` that replaces `urllib3.util.connection.create_connection`. [agent/tools/http_request.py:28-88]() This ensures that even if a DNS record is changed between validation and connection, the tool only connects to the IP address that was originally verified as safe. [agent/tools/http_request.py:198-210]()

### Sandbox Proxy Auth
For Git operations within the sandbox, Open SWE uses a LangSmith proxy to inject credentials. The `_create_sandbox_with_proxy` function configures the proxy with a GitHub App installation token. [agent/server.py:121-139]()

**Sources:** [agent/tools/http_request.py:28-210](), [agent/server.py:121-139](), [tests/test_http_security.py:143-181]()

---

## Tool Execution Context

Tools resolve their environment using the LangGraph `RunnableConfig` and thread metadata.

1.  **Sandbox Persistence**: Sandboxes are tracked via `sandbox_id` in thread metadata. [agent/server.py:91]()
2.  **Proxy Refresh**: For long-running threads, `_refresh_github_proxy` ensures that the sandbox's GitHub credentials remain valid. [agent/server.py:142-161]()
3.  **Git Identity**: Every sandbox is initialized with a standard git identity (`open-swe[bot]`) via `_configure_git_identity`. [agent/server.py:180-185]()

**Sources:** [agent/server.py:91-185]()

---

# Page: Middleware System

# Middleware System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/middleware/__init__.py](agent/middleware/__init__.py)
- [agent/middleware/ensure_no_empty_msg.py](agent/middleware/ensure_no_empty_msg.py)
- [agent/middleware/model_fallback.py](agent/middleware/model_fallback.py)
- [agent/middleware/notify_step_limit.py](agent/middleware/notify_step_limit.py)
- [agent/middleware/refresh_slack_status.py](agent/middleware/refresh_slack_status.py)
- [agent/middleware/sandbox_circuit_breaker.py](agent/middleware/sandbox_circuit_breaker.py)
- [agent/middleware/sanitize_tool_inputs.py](agent/middleware/sanitize_tool_inputs.py)
- [agent/middleware/tool_error_handler.py](agent/middleware/tool_error_handler.py)
- [agent/utils/sandbox.py](agent/utils/sandbox.py)
- [agent/utils/sandbox_state.py](agent/utils/sandbox_state.py)
- [tests/middleware/test_sandbox_recovery.py](tests/middleware/test_sandbox_recovery.py)
- [tests/test_ensure_no_empty_msg.py](tests/test_ensure_no_empty_msg.py)
- [tests/test_model_fallback_middleware.py](tests/test_model_fallback_middleware.py)
- [tests/test_notify_step_limit_middleware.py](tests/test_notify_step_limit_middleware.py)
- [tests/test_refresh_slack_status_middleware.py](tests/test_refresh_slack_status_middleware.py)
- [tests/test_sanitize_tool_inputs.py](tests/test_sanitize_tool_inputs.py)
- [tests/test_slack_assistants_status.py](tests/test_slack_assistants_status.py)

</details>



The middleware system provides deterministic hooks that execute around the agent's LLM decision-making loop. Middleware enables safety nets (like automatic PR creation), real-time interaction (message queue injection), and error handling without relying on the LLM's behavior. This architectural pattern ensures critical operations happen reliably regardless of model outputs.

For information about the tools the agent can call, see [Tool System](#3.2). For information about subagent spawning and orchestration, see [Subagent Orchestration](#3.4).

---

## Middleware Execution Points

Middleware functions are registered in the `create_deep_agent()` call and execute at multiple points: before model calls, after model calls, around tool execution, and before/after the entire agent run.

### Agent Loop with Middleware Hooks
```mermaid
graph TB
    subgraph "Agent Execution Lifecycle"
        Start["Agent Run Begins"]
        BeforeAgent["@abefore_agent"]
        BeforeModel["@before_model"]
        ModelCall["LLM Generates Action"]
        AfterModel["@after_model"]
        ToolExec["Tool Execution<br/>(awrap_tool_call)"]
        Loop{"Continue?"}
        AfterAgent["@aafter_agent"]
        End["Agent Run Ends"]
    end
    
    Start --> BeforeAgent
    BeforeAgent --> BeforeModel
    BeforeModel --> ModelCall
    ModelCall --> AfterModel
    AfterModel --> ToolExec
    ToolExec --> Loop
    Loop -->|Yes| BeforeModel
    Loop -->|No| AfterAgent
    AfterAgent --> End
    
    BeforeModel -.->|"check_message_queue_before_model"| QueueCheck["Inject queued messages"]
    BeforeModel -.->|"SandboxCircuitBreakerMiddleware"| CircuitBreaker["Check failure threshold"]
    
    AfterModel -.->|"ensure_no_empty_msg"| EmptyCheck["Validate message content"]
    
    ToolExec -.->|"ToolErrorMiddleware"| ErrorHandle["Catch/Format tool errors"]
    ToolExec -.->|"SanitizeToolInputsMiddleware"| Sanitize["Coerce malformed args"]
```

**Sources:** [agent/middleware/__init__.py:1-21](), [agent/middleware/refresh_slack_status.py:125-155](), [agent/middleware/tool_error_handler.py:159-165]()

---

## Built-in Middleware Components

Open SWE ships with several middleware components registered in the agent factory:

| Middleware | Hook Type | Purpose |
|------------|-----------|---------|
| `ToolErrorMiddleware` | `awrap_tool_call` | Catches exceptions and recreates sandboxes on client errors [agent/middleware/tool_error_handler.py:159-165]() |
| `check_message_queue_before_model` | `@before_model` | Injects messages that arrived during agent execution [agent/middleware/check_message_queue.py:1-10]() |
| `ensure_no_empty_msg` | `@after_model` | Forces `no_op` or `confirming_completion` if the model is silent [agent/middleware/ensure_no_empty_msg.py:57-58]() |
| `SanitizeToolInputsMiddleware` | `awrap_tool_call` | Coerces malformed integer fields in `read_file` calls [agent/middleware/sanitize_tool_inputs.py:54-61]() |
| `SlackAssistantStatusMiddleware` | Multi-hook | Updates Slack's "thinking" status and loading messages [agent/middleware/refresh_slack_status.py:125-128]() |
| `SandboxCircuitBreakerMiddleware` | `@before_model` | Halts execution if the sandbox fails repeatedly [agent/middleware/sandbox_circuit_breaker.py:10-13]() |

---

## Reliability and Recovery

### ToolErrorMiddleware & Sandbox Recovery
The `ToolErrorMiddleware` is critical for sandbox reliability. If a tool call fails due to a `SandboxClientError` (e.g., the sandbox became unreachable), the middleware automatically attempts to recreate the sandbox for that thread and instructs the LLM to retry the operation.

1.  **Catch Error**: Intercepts `SandboxClientError` during `awrap_tool_call` [agent/middleware/tool_error_handler.py:197]().
2.  **Recreate**: Calls `_recreate_sandbox_for_thread` which creates a new backend and updates thread metadata [agent/middleware/tool_error_handler.py:116-124]().
3.  **Proxy Update**: Updates the `SandboxBackendProxy` so subsequent tool calls in the same run use the new backend [agent/middleware/tool_error_handler.py:121]().
4.  **LLM Feedback**: Returns a `ToolMessage` explaining the recovery and suggesting a workspace re-initialization if necessary [agent/middleware/tool_error_handler.py:75-80]().

### SanitizeToolInputsMiddleware
This middleware prevents unnecessary LLM retries by fixing common formatting errors in tool arguments, specifically for `read_file`. It uses regex to extract leading integers from strings like `"1, 80"` or `"170, 'limit': 60"` [agent/middleware/sanitize_tool_inputs.py:25-38]().

**Sources:** [agent/middleware/tool_error_handler.py:159-205](), [agent/middleware/sanitize_tool_inputs.py:1-61]()

---

## Interaction and State Middleware

### check_message_queue_before_model
This middleware enables real-time interaction. When users post follow-up messages while the agent is executing, those messages are queued in the LangGraph store. Before each model call, this middleware checks the queue and injects pending messages into the agent's state [agent/middleware/check_message_queue.py:1-10]().

### SlackAssistantStatusMiddleware
This middleware maintains the Slack "Assistant" status indicator. Since Slack's status expires after two minutes, the middleware implements a heartbeat mechanism:
- **Heartbeat**: Periodically calls `assistant.threads.setStatus` every 60 seconds [agent/middleware/refresh_slack_status.py:37, 203-210]().
- **Contextual Status**: Updates the status text based on the tool currently being executed (e.g., "searching the codebase..." for `grep`) [agent/middleware/refresh_slack_status.py:46-71, 107-108]().

### Code Entity Mapping: Middleware to Slack API
```mermaid
graph LR
    Middleware["SlackAssistantStatusMiddleware"]
    StatusMap["_TOOL_STATUS Map"]
    SlackUtil["agent.utils.slack.set_slack_assistant_status"]
    SlackAPI["Slack API: assistant.threads.setStatus"]

    Middleware -->|Lookup tool name| StatusMap
    Middleware -->|Call| SlackUtil
    SlackUtil -->|POST| SlackAPI
```

**Sources:** [agent/middleware/refresh_slack_status.py:46-71](), [agent/middleware/refresh_slack_status.py:171-173](), [tests/test_slack_assistants_status.py:53-65]()

---

## Safety and Guardrails

### ensure_no_empty_msg
This middleware prevents the agent from entering a "silent loop" where the model returns an empty response without tool calls.
- If the message is empty and no user-facing tool (Slack/Linear) was called, it injects a `no_op` tool call to prompt the model to continue [agent/middleware/ensure_no_empty_msg.py:62-79]().
- If the model provides text but no tool calls (and hasn't messaged the user), it injects a `confirming_completion` tool call to ensure the task isn't being terminated prematurely [agent/middleware/ensure_no_empty_msg.py:81-101]().

### SandboxCircuitBreakerMiddleware
To prevent infinite loops or burning tokens on a broken environment, this middleware monitors consecutive sandbox failures. If the threshold (default: 3) is reached, it jumps to the `end` node and notifies the user [agent/middleware/sandbox_circuit_breaker.py:10-13](), [tests/middleware/test_sandbox_recovery.py:93-110]().

### Sandbox State Management
Middleware interacts with sandboxes through a `SandboxBackendProxy`. This proxy allows the underlying sandbox to be swapped out (e.g., during recovery) while the middleware and tools maintain a stable reference to the same object [agent/utils/sandbox_state.py:27-43]().

```mermaid
graph TD
    subgraph "State Persistence"
        Registry["SANDBOX_BACKENDS Registry"]
        Proxy["SandboxBackendProxy"]
    end
    
    subgraph "Middleware Actions"
        Handler["ToolErrorMiddleware"]
        Recreate["_recreate_sandbox_for_thread"]
    end

    Handler -->|Detects Error| Recreate
    Recreate -->|Creates New| NewSB["New Sandbox Instance"]
    NewSB -->|Updates| Proxy
    Proxy -->|Stored in| Registry
```

**Sources:** [agent/middleware/ensure_no_empty_msg.py:57-101](), [agent/utils/sandbox_state.py:27-43](), [tests/middleware/test_sandbox_recovery.py:50-90]()

---

# Page: Subagent Orchestration

# Subagent Orchestration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CUSTOMIZATION.md](CUSTOMIZATION.md)
- [INSTALLATION.md](INSTALLATION.md)
- [README.md](README.md)
- [agent/server.py](agent/server.py)
- [agent/tools/__init__.py](agent/tools/__init__.py)

</details>



This page documents how Open SWE enables parallel work decomposition through subagent spawning. The `task` tool, inherited from the Deep Agents framework, allows the main agent to delegate independent subtasks to child agents that run in isolated sandboxes with their own middleware stacks and file operations.

For information about the main agent assembly and execution, see [3.1 Agent Assembly](). For details on the middleware system, see [3.3 Middleware System](). For sandbox architecture fundamentals, see [4.1 Sandbox Architecture]().

---

## Overview

Subagent orchestration in Open SWE provides a mechanism for decomposing complex tasks into independent parallel subtasks. Each subagent:

- Runs in its own isolated cloud sandbox environment [README.md:52-54]().
- Maintains its own middleware stack (including message queue and error handling) [README.md:88-97]().
- Has its own todo list and file operation history [README.md:88-91]().
- Operates independently of other subagents and the parent agent [README.md:60-62]().
- Can spawn further subagents (nested subagents are supported) [README.md:88-91]().

This architecture follows the principle of isolating first and then providing full permissions inside the boundary, ensuring that the blast radius of any mistake is contained within the subagent's specific sandbox [README.md:54-58]().

**Sources:** [README.md:52-62](), [README.md:88-97]()

---

## The `task` Tool

The `task` tool is the primary interface for spawning subagents. It is a built-in tool provided by the `deepagents` framework, which Open SWE composes upon [README.md:38-40](), [README.md:77-78]().

### Tool Interface

The `task` tool allows the agent to delegate work to a child agent with a specific goal. The tool signature follows the Deep Agents protocol:

```python
task(
    goal: str,           # The objective for the subagent to accomplish
    context: str = None  # Optional additional context
) -> dict
```

The tool returns a dictionary containing the subagent's execution results, including any files modified, errors encountered, and the final state.

### Invocation Pattern

The parent agent invokes the `task` tool through standard tool calling. When `task` is called, it triggers the creation of a new agent instance via the core orchestration logic [agent/server.py:29]().

**Subagent Spawning Sequence**

```mermaid
sequenceDiagram
    participant Parent as "Parent Agent"
    participant LLM as "LLM (OpenAI/Anthropic)"
    participant TaskTool as "task Tool (Deep Agents)"
    participant CDA as "create_deep_agent"
    participant Sandbox as "New SandboxBackendProtocol"
    
    Parent->>LLM: "Request next action"
    LLM-->>Parent: "Call tool: task(goal='refactor module')"
    Parent->>TaskTool: "Execute task tool"
    TaskTool->>Sandbox: "Provision isolated sandbox (create_sandbox)"
    Sandbox-->>TaskTool: "Sandbox ID ready"
    TaskTool->>CDA: "Initialize subagent instance"
    CDA-->>TaskTool: "Subagent ready"
    TaskTool->>TaskTool: "Run subagent loop"
    TaskTool-->>Parent: "Return result (success/fail + changes)"
```

**Sources:** [README.md:38-40](), [README.md:77-78](), [README.md:88-91](), [agent/server.py:29-31](), [agent/utils/sandbox.py:80]()

---

## Subagent Isolation Model

Each subagent operates in complete isolation. This is enforced at the sandbox level and the orchestration level.

### Sandbox Isolation

Every subagent receives its own dedicated sandbox instance. Open SWE supports multiple providers such as LangSmith, Modal, Daytona, and Runloop [README.md:56-57]().

| Isolation Aspect | Implementation |
|---|---|
| **Filesystem** | Separate repository clone managed by `aresolve_sandbox_work_dir` [agent/server.py:81](). |
| **Process Space** | Independent remote Linux environment [README.md:52-54](). |
| **Git Auth** | Isolated proxy authentication for LangSmith sandboxes via `_configure_github_proxy` [agent/server.py:121-139](). |
| **State** | No shared memory or variables between parent and subagent. |

### Middleware Stack Isolation

Each subagent receives its own middleware stack, assembled identically to the parent agent to ensure consistent safety and behavior [README.md:88-97]().

**Middleware Distribution**

```mermaid
graph TB
    subgraph Parent["Parent Agent Thread"]
        PM["Middleware Stack:<br/>ToolErrorMiddleware<br/>check_message_queue_before_model<br/>SandboxCircuitBreakerMiddleware"]
        PS["Sandbox: main_env"]
    end
    
    subgraph Sub1["Subagent 1 Thread"]
        S1M["Middleware Stack:<br/>ToolErrorMiddleware<br/>check_message_queue_before_model<br/>SandboxCircuitBreakerMiddleware"]
        S1S["Sandbox: sub_env_1"]
    end
    
    subgraph Sub2["Subagent 2 Thread"]
        S2M["Middleware Stack:<br/>ToolErrorMiddleware<br/>check_message_queue_before_model<br/>SandboxCircuitBreakerMiddleware"]
        S2S["Sandbox: sub_env_2"]
    end
    
    Parent -- "task tool" --> Sub1
    Parent -- "task tool" --> Sub2
```

**Sources:** [README.md:52-57](), [README.md:88-97](), [agent/server.py:81](), [agent/server.py:121-139](), [agent/middleware/__init__.py:44-53]()

---

## Middleware Execution in Subagents

Each subagent executes the same middleware hooks as the parent, but scoped to its own thread and sandbox.

### `ToolErrorMiddleware`
This middleware catches and handles tool errors gracefully, allowing the subagent to attempt recovery or report failure back to the parent without crashing the entire orchestration [agent/server.py:49]().

### `check_message_queue_before_model`
This middleware allows human intervention during a subagent's run [README.md:92-94](). If a user sends a message to the subagent's thread (e.g., via Slack or Linear), it is injected into the context before the next model call [agent/server.py:50]().

**Sources:** [README.md:92-96](), [agent/server.py:44-53]()

---

## Parallel Execution Guarantees

Open SWE ensures that multiple tasks run in parallel without queuing by leveraging isolated sandboxes for each run [README.md:60-62]().

### Concurrency and Threading
When the `task` tool is invoked, the subagent runs within its own execution context. This allows the parent agent to fan out independent subtasks to isolated subagents, similar to child sessions for parallel work [README.md:88-91]().

**Code Entity Association**

| System Name | Code Entity | File Path |
|---|---|---|
| **Agent Factory** | `create_deep_agent` | [agent/server.py:29]() |
| **Sandbox Creator** | `create_sandbox` | [agent/utils/sandbox.py:80]() |
| **Tool Definition** | `task` | [README.md:77]() |
| **Sandbox Backend** | `SandboxBackendProtocol` | [agent/server.py:31]() |
| **Proxy Config** | `_configure_github_proxy` | [agent/server.py:43]() |

**Sources:** [README.md:60-62](), [README.md:77-78](), [README.md:88-91](), [agent/server.py:29-31](), [agent/utils/sandbox.py:80]()

---

## Result Aggregation

When a subagent completes its task, the results (including modifications and status) are returned to the parent agent. The parent agent then decides how to proceed based on the output.

### Validation and Commit
The agent is instructed to run linters, formatters, and tests before committing [README.md:108-109](). Subagents follow the same end-to-end responsibility for validation within their isolated boundaries before the results are bubbled back up to the parent.

**Sources:** [README.md:108-109]()

---

# Page: Sandbox Execution

# Sandbox Execution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/integrations/langsmith.py](agent/integrations/langsmith.py)
- [agent/middleware/sandbox_circuit_breaker.py](agent/middleware/sandbox_circuit_breaker.py)
- [agent/middleware/tool_error_handler.py](agent/middleware/tool_error_handler.py)
- [agent/utils/sandbox.py](agent/utils/sandbox.py)
- [agent/utils/sandbox_state.py](agent/utils/sandbox_state.py)
- [pyproject.toml](pyproject.toml)
- [tests/middleware/test_sandbox_recovery.py](tests/middleware/test_sandbox_recovery.py)
- [uv.lock](uv.lock)

</details>



## Purpose and Scope

Sandbox Execution encompasses the isolated execution environments where Open SWE agents operate. Each agent task runs in its own **sandbox** — a remote Linux container or virtual machine with full shell access where the repository is cloned and commands are executed. This architecture ensures that mistakes are contained, tasks run in parallel without interference, and the agent has unrestricted permissions within safe boundaries.

This page covers:
- The `SandboxBackendProtocol` interface and provider abstraction.
- Sandbox lifecycle management through the `get_agent()` and `create_sandbox()` flow.
- The `SandboxBackendProxy` mechanism for stable per-thread handles.
- Error recovery and circuit breaker logic for unrecoverable failures.

For specific provider implementations, see [Sandbox Providers](#4.2). For agent assembly and tool execution that occurs *within* sandboxes, see [Agent Core](#3).

---

## Core Architecture

### Isolation Model

Every agent invocation operates in a dedicated sandbox. The isolation guarantees are:

| Property | Implementation |
|---|---|
| **Process isolation** | Each sandbox is a separate container/VM with its own filesystem. |
| **Network isolation** | Sandboxes cannot access internal networks (enforced by provider). |
| **Credential isolation** | Git credentials handled via LangSmith proxy or ephemeral tokens. |
| **Persistence** | Sandboxes remain alive across follow-up messages on the same thread using `sandbox_id`. |

The key design principle: **isolate first, then give full permissions inside the boundary**. The agent can run any shell command, install packages, or modify files without confirmation prompts because the blast radius is fully contained.

**Sources:** [agent/integrations/langsmith.py:126-170](), [agent/utils/sandbox_state.py:27-43](), [agent/middleware/sandbox_circuit_breaker.py:24-25]()

---

### Protocol Interface

All sandbox providers implement `SandboxBackendProtocol` from the `deepagents` framework. This protocol defines the contract for interacting with sandboxes. Open SWE uses a `SandboxBackendProxy` to maintain a stable reference even if the underlying backend needs to be recreated.

**Sandbox Backend Class Diagram**
```mermaid
classDiagram
    class "SandboxBackendProtocol" {
        <<interface>>
        +id: str
        +execute(command, timeout) ExecuteResponse
        +ls(path) LsResult
        +read(file_path) ReadResult
        +write(file_path, content) WriteResult
        +edit(file_path, old, new) EditResult
    }
    
    class "SandboxBackendProxy" {
        -_backend: SandboxBackendProtocol
        +current: SandboxBackendProtocol
        +replace_backend(backend)
        +execute(command)
    }
    
    class "LangSmithSandbox" {
        +id: str
        +execute(command)
    }
    
    class "ModalSandbox" {
        +id: str
        +execute(command)
    }
    
    class "DaytonaSandbox" {
        +id: str
        +execute(command)
    }
    
    SandboxBackendProtocol <|.. SandboxBackendProxy
    SandboxBackendProtocol <|.. LangSmithSandbox
    SandboxBackendProtocol <|.. ModalSandbox
    SandboxBackendProtocol <|.. DaytonaSandbox
```

**Key methods:**

- **`execute(command, timeout)`**: Run arbitrary shell commands, returns `ExecuteResponse` with `output` and `exit_code` [agent/utils/sandbox_state.py:114-118]().
- **File operations**: `read()`, `write()`, `edit()`, `ls()`, and `glob()` provide atomic file manipulation [agent/utils/sandbox_state.py:44-100]().
- **Async support**: Every sync method has a corresponding `a`-prefixed async version (e.g., `aexecute`) [agent/utils/sandbox_state.py:117-118]().

**Sources:** [agent/utils/sandbox_state.py:27-120](), [agent/integrations/langsmith.py:203-214]()

---

## Provider Factory System

Sandbox creation is routed through a factory pattern based on the `SANDBOX_TYPE` environment variable.

**Sandbox Provider Resolution**
```mermaid
graph TB
    subgraph "Natural Language Space"
        UserConfig["Environment Variable: SANDBOX_TYPE"]
    end

    subgraph "Code Entity Space"
        SF["agent/utils/sandbox.py: SANDBOX_FACTORIES"]
        CS["agent/utils/sandbox.py: create_sandbox()"]
        LSF["agent/integrations/langsmith.py: create_langsmith_sandbox()"]
        MSF["agent/integrations/modal.py: create_modal_sandbox()"]
        DSF["agent/integrations/daytona.py: create_daytona_sandbox()"]
    end

    UserConfig --> CS
    CS --> SF
    SF -->|"langsmith"| LSF
    SF -->|"modal"| MSF
    SF -->|"daytona"| DSF
```

The factory registry maps configuration strings to creation functions [agent/utils/sandbox.py:11-17]():

| Provider | Factory Function | Integration File |
|---|---|---|
| `langsmith` | `create_langsmith_sandbox` | `agent/integrations/langsmith.py` |
| `daytona` | `create_daytona_sandbox` | `agent/integrations/daytona.py` |
| `modal` | `create_modal_sandbox` | `agent/integrations/modal.py` |
| `runloop` | `create_runloop_sandbox` | `agent/integrations/runloop.py` |
| `local` | `create_local_sandbox` | `agent/integrations/local.py` |

**Sources:** [agent/utils/sandbox.py:1-37](), [agent/integrations/langsmith.py:126-170]()

---

## Lifecycle and Error Management

### Thread-Sandbox Mapping

Sandboxes are cached per thread ID in the `SANDBOX_BACKENDS` dictionary [agent/utils/sandbox_state.py:121-122](). When an agent is requested, the system retrieves the backend from cache or reconnects using the `sandbox_id` stored in LangGraph thread metadata [agent/utils/sandbox_state.py:153-178]().

### Recovery and Circuit Breaker

The system includes automated recovery for `SandboxClientError` (e.g., timeouts or network failures).

1. **`ToolErrorMiddleware`**: Catches sandbox errors mid-run, triggers `_recreate_sandbox_for_thread`, and updates thread metadata with the new ID [agent/middleware/tool_error_handler.py:116-125]().
2. **`SandboxCircuitBreakerMiddleware`**: Prevents infinite retry loops. If the agent experiences a streak of failures (default threshold is 2), it halts the run and notifies the user via Slack, Linear, or GitHub [agent/middleware/sandbox_circuit_breaker.py:24-26](), [agent/middleware/sandbox_circuit_breaker.py:168-189]().

**Sources:** [agent/middleware/tool_error_handler.py:159-204](), [agent/middleware/sandbox_circuit_breaker.py:67-102](), [tests/middleware/test_sandbox_recovery.py:50-90]()

---

## Repository Management

### Cloning and Identity

When a sandbox is created or recreated, the system configures the git identity (name and email) and sets up authentication. For LangSmith sandboxes, `_configure_github_proxy` is used to inject the GitHub token into the sandbox's network traffic so that credentials never touch the sandbox disk [agent/integrations/langsmith.py:98-124]().

**Sources:** [agent/integrations/langsmith.py:70-95](), [agent/middleware/tool_error_handler.py:116-124]()

---

## Child Pages

For more details on specific aspects of sandbox execution, refer to the following child pages:

- **[Sandbox Architecture](#4.1)**: Deep dive into the `SandboxBackendProtocol`, the proxy pattern, and isolation principles.
- **[Sandbox Providers](#4.2)**: Configuration and setup for LangSmith, Modal, Daytona, Runloop, and Local modes via `SANDBOX_TYPE`.
- **[Sandbox Lifecycle Management](#4.3)**: Details on caching in `SANDBOX_BACKENDS`, persistence in thread metadata, and recreation logic.
- **[Repository Management](#4.4)**: How the agent interacts with git, manages clones, and handles authentication within the sandbox environment.

---

# Page: Sandbox Architecture

# Sandbox Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CUSTOMIZATION.md](CUSTOMIZATION.md)
- [INSTALLATION.md](INSTALLATION.md)
- [README.md](README.md)
- [agent/middleware/sandbox_circuit_breaker.py](agent/middleware/sandbox_circuit_breaker.py)
- [agent/middleware/tool_error_handler.py](agent/middleware/tool_error_handler.py)
- [agent/utils/sandbox.py](agent/utils/sandbox.py)
- [agent/utils/sandbox_state.py](agent/utils/sandbox_state.py)
- [tests/middleware/test_sandbox_recovery.py](tests/middleware/test_sandbox_recovery.py)

</details>



## Purpose and Scope

This document describes the sandbox architecture that provides isolated execution environments for Open SWE agents. Each agent task runs in its own sandbox—a remote Linux environment with full shell access where the agent can safely execute commands, read and write files, and make changes to repositories without affecting production systems or other concurrent tasks [README.md:52-58]().

The architecture is designed to be provider-agnostic, supporting various backends from local development shells to managed cloud environments like LangSmith, Modal, and Runloop [CUSTOMIZATION.md:54-65]().

## Core Principles

The sandbox architecture is built on three foundational principles:

*   **Isolation First**: Every task runs in a completely isolated environment. The blast radius of any mistake is fully contained within the sandbox boundary [README.md:52-54]().
*   **Per-Thread Persistence**: Each thread (identified by a deterministic `thread_id`) gets a persistent sandbox that is reused across follow-up messages, maintaining state and uncommitted changes [README.md:60](), [agent/utils/sandbox_state.py:121-122]().
*   **Parallel Execution**: Multiple tasks run in parallel—each in its own sandbox—with no queuing [README.md:62]().

**Sources:** [README.md:52-62](), [agent/utils/sandbox_state.py:121-122]()

## Sandbox Protocol Interface

All sandbox providers implement the `SandboxBackendProtocol` from the `deepagents` framework [CUSTOMIZATION.md:101-106](). This protocol defines a standard interface that allows tools and agent code to work uniformly across all providers.

### Protocol Methods

| Method | Description | Returns |
| :--- | :--- | :--- |
| `execute(command, timeout=None)` | Execute a shell command in the sandbox | `ExecuteResponse` [CUSTOMIZATION.md:104](), [agent/utils/sandbox_state.py:114-118]() |
| `ls(path)` | List directory contents | `LsResult` [agent/utils/sandbox_state.py:44-48]() |
| `read(path, offset, limit)` | Read file contents | `ReadResult` [agent/utils/sandbox_state.py:50-54]() |
| `write(path, content)` | Write file contents | `WriteResult` [agent/utils/sandbox_state.py:78-82]() |
| `edit(path, old, new)` | Apply string-based edits | `EditResult` [agent/utils/sandbox_state.py:84-100]() |
| `glob(pattern, path)` | Find files matching pattern | `GlobResult` [agent/utils/sandbox_state.py:72-76]() |
| `grep(pattern, path)` | Search files for pattern | `GrepResult` [agent/utils/sandbox_state.py:56-70]() |
| `id` (property) | Unique sandbox identifier | `str` [CUSTOMIZATION.md:106](), [agent/utils/sandbox_state.py:38-40]() |

**Sources:** [CUSTOMIZATION.md:101-130](), [agent/utils/sandbox_state.py:27-120]()

## Sandbox Provider Architecture

The system uses a factory pattern to instantiate the correct sandbox backend based on the `SANDBOX_TYPE` environment variable [agent/utils/sandbox.py:32-37]().

### Natural Language to Code Entity Mapping

The following diagram bridges the configuration space (Environment Variables) to the implementation classes and functions.

```mermaid
graph TB
    subgraph "Natural Language Space (Config)"
        EnvVar["'SANDBOX_TYPE' Env Var"]
    end

    subgraph "Code Entity Space (Implementation)"
        Factory["create_sandbox()<br/>agent/utils/sandbox.py"]
        Registry["SANDBOX_FACTORIES dict<br/>agent/utils/sandbox.py"]
        
        LSImpl["create_langsmith_sandbox()<br/>agent/integrations/langsmith.py"]
        ModalImpl["create_modal_sandbox()<br/>agent/integrations/modal.py"]
        DaytonaImpl["create_daytona_sandbox()<br/>agent/integrations/daytona.py"]
        RunloopImpl["create_runloop_sandbox()<br/>agent/integrations/runloop.py"]
        LocalImpl["create_local_sandbox()<br/>agent/integrations/local.py"]
        
        Protocol["SandboxBackendProtocol<br/>(Interface)"]
    end
    
    EnvVar --> Factory
    Factory --> Registry
    Registry -->|"langsmith"| LSImpl
    Registry -->|"modal"| ModalImpl
    Registry -->|"daytona"| DaytonaImpl
    Registry -->|"runloop"| RunloopImpl
    Registry -->|"local"| LocalImpl
    
    LSImpl -.-> Protocol
    ModalImpl -.-> Protocol
    DaytonaImpl -.-> Protocol
    RunloopImpl -.-> Protocol
    LocalImpl -.-> Protocol
```

### Available Providers

| `SANDBOX_TYPE` | Integration File | Required Config / Env Vars |
| :--- | :--- | :--- |
| `langsmith` (default) | [agent/integrations/langsmith.py]() | `LANGSMITH_API_KEY_PROD`, `DEFAULT_SANDBOX_SNAPSHOT_ID` [CUSTOMIZATION.md:37](), [CUSTOMIZATION.md:60]() |
| `daytona` | [agent/integrations/daytona.py]() | `DAYTONA_API_KEY` [CUSTOMIZATION.md:61]() |
| `runloop` | [agent/integrations/runloop.py]() | `RUNLOOP_API_KEY` [CUSTOMIZATION.md:62]() |
| `modal` | [agent/integrations/modal.py]() | Modal credentials [CUSTOMIZATION.md:63]() |
| `local` | [agent/integrations/local.py]() | No isolation—development only [CUSTOMIZATION.md:64-66]() |

**Sources:** [CUSTOMIZATION.md:58-65](), [agent/utils/sandbox.py:11-17]()

## Sandbox Lifecycle and Recovery

Sandboxes are managed through a combination of in-memory caching and persistent thread metadata. Open SWE includes a `SandboxBackendProxy` to allow the underlying sandbox to be swapped out (recreated) without breaking the agent's reference to the backend [agent/utils/sandbox_state.py:27-42]().

### Lifecycle Data Flow

```mermaid
sequenceDiagram
    participant App as "Agent Application"
    participant State as "agent/utils/sandbox_state.py"
    participant Cache as "SANDBOX_BACKENDS dict"
    participant Meta as "LangGraph Thread Metadata"
    participant Factory as "agent/utils/sandbox.py"

    App->>State: get_sandbox_backend(thread_id)
    State->>Cache: Check thread_id
    alt Cache Hit
        Cache-->>State: Return SandboxBackendProxy
    else Cache Miss
        State->>Meta: get_sandbox_id_from_metadata(thread_id)
        Meta-->>State: sandbox_id
        State->>Factory: create_sandbox(sandbox_id)
        Factory-->>State: SandboxBackendProtocol instance
        State->>Cache: set_sandbox_backend(thread_id, backend)
        Cache-->>State: SandboxBackendProxy
    end
    State-->>App: Return SandboxBackendProxy
```

### Automatic Recovery and Circuit Breaker

The system implements a `ToolErrorMiddleware` that catches `SandboxClientError` exceptions. If a sandbox becomes unreachable mid-run, the middleware automatically triggers `_recreate_sandbox_for_thread`, which provisions a fresh sandbox, updates the thread metadata, and returns an error message to the agent suggesting a retry [agent/middleware/tool_error_handler.py:176-182](), [agent/middleware/tool_error_handler.py:75-80]().

To prevent infinite loops of recreation, a `SandboxCircuitBreakerMiddleware` monitors the message history. If it detects consecutive sandbox failures or recreations (default threshold: 2), it interrupts the agent run with a "Sandbox circuit breaker triggered" message and stops further model calls [agent/middleware/sandbox_circuit_breaker.py:24-27](), [agent/middleware/sandbox_circuit_breaker.py:167-172]().

**Sources:** [agent/utils/sandbox_state.py:121-184](), [agent/middleware/tool_error_handler.py:159-205](), [agent/middleware/sandbox_circuit_breaker.py:1-102](), [tests/middleware/test_sandbox_recovery.py:50-89]()

## Security and Isolation

### Isolation Guarantees
*   **Remote Providers**: Providers like LangSmith, Modal, and Runloop run code in isolated Linux environments. The blast radius of any mistake is fully contained [README.md:54]().
*   **Local Warning**: The `local` provider runs commands directly on the host with no sandboxing. It is intended for development only [CUSTOMIZATION.md:66]().

### Credential Proxying
For LangSmith sandboxes, Open SWE configures proxy rules so that the sandbox can access GitHub without storing permanent tokens in the environment. `github.com` requests receive Basic auth, and `api.github.com` requests receive Bearer auth, both using tokens minted at runtime from GitHub App credentials [CUSTOMIZATION.md:47-53]().

**Sources:** [README.md:52-54](), [CUSTOMIZATION.md:47-53](), [CUSTOMIZATION.md:66]()

---

# Page: Sandbox Providers

# Sandbox Providers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/integrations/daytona.py](agent/integrations/daytona.py)
- [agent/integrations/langsmith.py](agent/integrations/langsmith.py)
- [agent/integrations/local.py](agent/integrations/local.py)
- [agent/integrations/modal.py](agent/integrations/modal.py)
- [agent/integrations/runloop.py](agent/integrations/runloop.py)
- [agent/utils/sandbox_paths.py](agent/utils/sandbox_paths.py)
- [pyproject.toml](pyproject.toml)
- [tests/test_daytona_integration.py](tests/test_daytona_integration.py)
- [tests/test_langsmith_sandbox_config.py](tests/test_langsmith_sandbox_config.py)
- [uv.lock](uv.lock)

</details>



This page documents the pluggable sandbox provider system in Open SWE, covering all supported execution environments and how to configure them via the `SANDBOX_TYPE` environment variable.

## Overview

Open SWE supports multiple sandbox providers through a factory pattern that abstracts the underlying execution environment. Each provider implements the `SandboxBackendProtocol` [agent/integrations/langsmith.py:13-13]() from the Deep Agents framework, allowing agents to execute commands and perform file operations in isolated Linux environments.

The system is designed to be **pluggable**: you can switch providers by changing a single environment variable, or add custom providers by implementing the protocol and registering a factory function in the `SANDBOX_FACTORIES` dictionary.

**Sources:** [agent/integrations/langsmith.py:12-13](), [pyproject.toml:9-28]()

## Supported Providers

Open SWE includes five built-in sandbox providers:

| Provider | Type | Use Case | Required Env Vars | Implementation File |
|----------|------|----------|-------------------|-----------------|
| **langsmith** | Docker containers | Production, full observability | `LANGSMITH_API_KEY` or `LANGSMITH_API_KEY_PROD` | [agent/integrations/langsmith.py]() |
| **modal** | Serverless containers | Cloud execution, auto-scaling | Modal credentials | [agent/integrations/modal.py]() |
| **daytona** | Development environments | Development workflows | `DAYTONA_API_KEY` | [agent/integrations/daytona.py]() |
| **runloop** | Managed environments | Devbox-based execution | `RUNLOOP_API_KEY` | [agent/integrations/runloop.py]() |
| **local** | Shell subprocess | Local development only | None | [agent/integrations/local.py]() |

**Default Provider:** `langsmith` is the primary production backend, offering sophisticated features like snapshotting and proxy-based authentication.

**Sources:** [agent/integrations/langsmith.py:1-170](), [agent/integrations/modal.py:1-26](), [agent/integrations/daytona.py:1-29](), [agent/integrations/runloop.py:1-30](), [agent/integrations/local.py:1-26]()

## Provider Selection

### Factory Pattern

The selection of a sandbox provider is handled by checking the `SANDBOX_TYPE` environment variable. Each provider has a corresponding factory function that returns a `SandboxBackendProtocol` implementation.

Title: Sandbox Provider Architecture
```mermaid
graph LR
    subgraph Configuration ["Configuration Space"]
        Env["SANDBOX_TYPE<br/>Env Var"]
    end

    subgraph FactoryLayer ["Factory Layer"]
        CLS["create_langsmith_sandbox()<br/>agent/integrations/langsmith.py"]
        CMD["create_modal_sandbox()<br/>agent/integrations/modal.py"]
        CDY["create_daytona_sandbox()<br/>agent/integrations/daytona.py"]
        CRN["create_runloop_sandbox()<br/>agent/integrations/runloop.py"]
        CLC["create_local_sandbox()<br/>agent/integrations/local.py"]
    end

    subgraph CodeEntitySpace ["Code Entity Space"]
        SB_PROT["SandboxBackendProtocol<br/>deepagents.backends.protocol"]
        LS_SB["LangSmithSandbox<br/>deepagents.backends"]
        MD_SB["ModalSandbox<br/>langchain_modal"]
        DT_SB["DaytonaSandbox<br/>langchain_daytona"]
        RL_SB["RunloopSandbox<br/>langchain_runloop"]
        LC_SB["LocalShellBackend<br/>deepagents.backends"]
    end

    Env --> CLS
    Env --> CMD
    Env --> CDY
    Env --> CRN
    Env --> CLC

    CLS --> LS_SB
    CMD --> MD_SB
    CDY --> DT_SB
    CRN --> RL_SB
    CLC --> LC_SB

    LS_SB -.-> SB_PROT
    MD_SB -.-> SB_PROT
    DT_SB -.-> SB_PROT
    RL_SB -.-> SB_PROT
    LC_SB -.-> SB_PROT
```
**Sources:** [agent/integrations/langsmith.py:126-129](), [agent/integrations/modal.py:9-9](), [agent/integrations/daytona.py:17-17](), [agent/integrations/runloop.py:7-7](), [agent/integrations/local.py:6-6]()

## LangSmith Sandbox

### Overview
The `langsmith` provider uses the `LangSmithSandbox` backend [agent/integrations/langsmith.py:12-12](). It supports advanced lifecycle management, including custom resource allocation and idle timeouts.

### Resource Configuration
The provider allows fine-grained control over the sandbox environment via environment variables:

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `DEFAULT_SANDBOX_VCPUS` | 2 | Number of vCPUs [agent/integrations/langsmith.py:19-19]() |
| `DEFAULT_SANDBOX_MEM_BYTES` | 7936 MiB | Memory limit [agent/integrations/langsmith.py:20-20]() |
| `DEFAULT_SANDBOX_IDLE_TTL_SECONDS` | 600 | Time before idle sandbox stops [agent/integrations/langsmith.py:21-21]() |
| `DEFAULT_SANDBOX_SNAPSHOT_FS_CAPACITY_BYTES` | 32 GiB | Filesystem capacity [agent/integrations/langsmith.py:18-18]() |

### Proxy Authentication
LangSmith sandboxes utilize a specialized proxy configuration to inject GitHub authentication headers. This allows the agent to perform `git` operations without persisting sensitive tokens to the sandbox's disk [agent/integrations/langsmith.py:98-124]().

Title: LangSmith Proxy Data Flow
```mermaid
graph TD
    subgraph Host ["Host Environment"]
        Token["GitHub Token"]
        Config["_configure_github_proxy()<br/>agent/integrations/langsmith.py"]
    end

    subgraph LangSmithAPI ["LangSmith Control Plane"]
        Rules["_github_proxy_rules()<br/>agent/integrations/langsmith.py"]
        Patch["PATCH /v2/sandboxes/boxes/{id}"]
    end

    subgraph Sandbox ["Sandbox Container"]
        Git["git clone / push"]
        Proxy["Internal Proxy"]
    end

    Token --> Config
    Config --> Rules
    Rules --> Patch
    Patch --> Proxy
    Git --> Proxy
    Proxy -->|Authenticated Request| GH["github.com"]
```
**Sources:** [agent/integrations/langsmith.py:70-95](), [agent/integrations/langsmith.py:98-124]()

## Modal Sandbox
The `modal` provider leverages `modal.Sandbox` [agent/integrations/modal.py:22-24](). It looks up a Modal App defined by `MODAL_APP_NAME` (default: "open-swe") and creates or reconnects to sandboxes within that app context [agent/integrations/modal.py:6-19]().

**Sources:** [agent/integrations/modal.py:1-26]()

## Daytona Sandbox
The `daytona` provider uses the `Daytona` client to manage environments [agent/integrations/daytona.py:22-22](). It defaults to using the `daytonaio/sandbox:0.6.0` snapshot, which can be overridden via `DAYTONA_SANDBOX_SNAPSHOT` [agent/integrations/daytona.py:6-11]().

**Sources:** [agent/integrations/daytona.py:1-29]()

## Runloop Sandbox
The `runloop` provider integrates with Runloop's "devboxes" [agent/integrations/runloop.py:23-28](). It requires a `RUNLOOP_API_KEY` and wraps the resulting devbox in a `RunloopSandbox` adapter [agent/integrations/runloop.py:19-30]().

**Sources:** [agent/integrations/runloop.py:1-31]()

## Local Sandbox
The `local` provider uses `LocalShellBackend` [agent/integrations/local.py:3-3](). 
**Warning:** This provider provides **no isolation** and runs commands directly on the host machine [agent/integrations/local.py:9-10](). It is intended for development and requires `LOCAL_SANDBOX_ROOT_DIR` to be set, otherwise it defaults to the current working directory [agent/integrations/local.py:21-24]().

**Sources:** [agent/integrations/local.py:1-26]()

## Path Resolution Utilities

Regardless of the provider, Open SWE uses `agent/utils/sandbox_paths.py` to resolve writable directories for repository operations. This utility checks multiple candidates (provider methods like `get_work_dir`, shell commands like `pwd`, and environment variables like `$HOME`) to find a valid, writable path [agent/utils/sandbox_paths.py:34-86]().

**Key Functions:**
- `resolve_repo_dir`: Joins the work directory with the repository name [agent/utils/sandbox_paths.py:20-26]().
- `resolve_sandbox_work_dir`: Iterates through candidates and tests for writability using `test -d && test -w` [agent/utils/sandbox_paths.py:34-45]().

**Sources:** [agent/utils/sandbox_paths.py:20-146]()

---

# Page: Sandbox Lifecycle Management

# Sandbox Lifecycle Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/integrations/langsmith.py](agent/integrations/langsmith.py)
- [agent/middleware/sandbox_circuit_breaker.py](agent/middleware/sandbox_circuit_breaker.py)
- [agent/middleware/tool_error_handler.py](agent/middleware/tool_error_handler.py)
- [agent/server.py](agent/server.py)
- [agent/tools/__init__.py](agent/tools/__init__.py)
- [agent/utils/sandbox.py](agent/utils/sandbox.py)
- [agent/utils/sandbox_state.py](agent/utils/sandbox_state.py)
- [pyproject.toml](pyproject.toml)
- [tests/middleware/test_sandbox_recovery.py](tests/middleware/test_sandbox_recovery.py)
- [uv.lock](uv.lock)

</details>



This page documents the lifecycle management of sandbox execution environments in Open SWE, including creation, caching, persistence, reconnection, and automatic recreation. Each agent task runs in an isolated sandbox that persists across follow-up messages on the same thread.

For information about sandbox architecture and the protocol interface, see **4.1 Sandbox Architecture**. For details on specific sandbox provider implementations, see **4.2 Sandbox Providers**. For repository cloning and management within sandboxes, see **4.4 Repository Management**.

---

## Lifecycle States

A sandbox progresses through several states during its lifecycle, managed by the `get_agent()` function in coordination with thread metadata and an in-memory cache.

### Sandbox State Transitions
```mermaid
stateDiagram-v2
    [*] --> NoSandbox: "Thread created"
    NoSandbox --> Creating: "First agent invocation (get_agent)"
    Creating --> Active: "Sandbox ready & Repo cloned"
    Active --> Cached: "Run completes (SANDBOX_BACKENDS)"
    Cached --> Active: "Follow-up message (get_agent)"
    Active --> Unreachable: "Connection fails (SandboxClientError)"
    Unreachable --> Creating: "Auto-recreation (_recreate_sandbox)"
    Creating --> Creating: "Concurrent request waits (_wait_for_sandbox_id)"
    Cached --> [*]: "Thread garbage collected"
```

**Sources:** [agent/server.py:85-87](), [agent/server.py:188-203](), [agent/middleware/tool_error_handler.py:176-185]()

---

## Thread-to-Sandbox Mapping

Each thread is mapped to exactly one sandbox using a deterministic thread ID. The mapping is maintained in two places: an in-memory cache (`SANDBOX_BACKENDS`) and persistent thread metadata managed via the LangGraph `client`.

### Mapping Architecture
```mermaid
graph TB
    ThreadID["thread_id<br/>(UUID string)"]
    
    subgraph "In-Memory Cache (agent/utils/sandbox_state.py)"
        Cache["SANDBOX_BACKENDS<br/>dict[str, SandboxBackendProxy]"]
    end
    
    subgraph "Persistent Storage (LangGraph SDK)"
        Metadata["Thread Metadata<br/>{sandbox_id: str}"]
    end
    
    subgraph "Sandbox Instance"
        Backend["SandboxBackendProtocol<br/>(LangSmithSandbox, etc.)"]
        SandboxID["backend.id<br/>(provider-specific)"]
    end
    
    ThreadID -->|"cache key"| Cache
    ThreadID -->|"stored in"| Metadata
    Cache -->|"holds reference to"| Backend
    Metadata -->|"persisted value"| SandboxID
    Backend -->|"has property"| SandboxID
```

| Storage | Purpose | Lifetime | Source |
|---------|---------|----------|--------|
| `SANDBOX_BACKENDS` | Fast in-memory lookup via `SandboxBackendProxy` | Process lifetime | [agent/utils/sandbox_state.py:122-146]() |
| Thread metadata `sandbox_id` | Persistent across restarts | Thread lifetime | [agent/integrations/langsmith.py:173-192]() |

**Sources:** [agent/utils/sandbox_state.py:27-122](), [agent/integrations/langsmith.py:173-192]()

---

## Sandbox Creation Flow

When a thread has no sandbox (first invocation), `get_agent()` creates a new sandbox and persists its ID to thread metadata.

### Creation Sequence
```mermaid
sequenceDiagram
    participant GA as "get_agent()"
    participant Cache as "SANDBOX_BACKENDS"
    participant Metadata as "Thread Metadata"
    participant Factory as "create_sandbox()"
    participant Provider as "LangSmithProvider"
    
    GA->>Cache: "Check SANDBOX_BACKENDS[thread_id]"
    Cache-->>GA: "None (cache miss)"
    
    GA->>Metadata: "get_sandbox_id_from_metadata(thread_id)"
    Metadata-->>GA: "None (no sandbox_id)"
    
    GA->>Metadata: "Update metadata: {sandbox_id: '__creating__'}"
    Note over Metadata: "Sentinel prevents concurrent creation"
    
    GA->>Factory: "create_sandbox()"
    Factory->>Provider: "get_or_create(sandbox_id=None)"
    Provider-->>Factory: "SandboxBackendProtocol"
    Factory-->>GA: "sandbox_backend"
    
    Note over GA: "Clone repository in sandbox"
    
    GA->>Metadata: "Update metadata: {sandbox_id: backend.id}"
    GA->>Cache: "SANDBOX_BACKENDS[thread_id] = backend"
    GA-->>GA: "Return agent with backend"
```

**Key Steps:**
1. **Check cache** - Lookup in `SANDBOX_BACKENDS` [agent/utils/sandbox_state.py:169]().
2. **Check metadata** - Fetch persisted `sandbox_id` [agent/utils/sandbox_state.py:153-164]().
3. **Set sentinel** - Write `SANDBOX_CREATING` (`"__creating__"`) to metadata [agent/server.py:85]().
4. **Create sandbox** - Call `create_sandbox()` via `asyncio.to_thread` [agent/server.py:127-139]().
5. **Configure Proxy** - For LangSmith sandboxes, `_configure_github_proxy` injects the GitHub App installation token [agent/integrations/langsmith.py:98-124]().
6. **Persist ID** - Update metadata with real `sandbox_id` [agent/integrations/langsmith.py:165-170]().
7. **Cache reference** - Store backend in `SANDBOX_BACKENDS` via `set_sandbox_backend` [agent/utils/sandbox_state.py:131-146]().

**Sources:** [agent/server.py:121-139](), [agent/integrations/langsmith.py:126-170](), [agent/utils/sandbox_state.py:167-179]()

---

## Sandbox Caching Strategy

The `SANDBOX_BACKENDS` dictionary provides fast in-memory access to `SandboxBackendProxy` instances. This proxy allows the underlying backend to be swapped (e.g., during recreation) while maintaining a stable reference for the agent.

| Property | Behavior |
|----------|----------|
| **Scope** | Process-local (not shared across deployments) |
| **Eviction** | Manual via `clear_sandbox_backend(thread_id)` |
| **Invalidation** | On `SandboxClientError` caught by `ToolErrorMiddleware` |
| **Proxy Pattern** | `SandboxBackendProxy` delegates all calls to `self._backend` |

**Sources:** [agent/utils/sandbox_state.py:27-122](), [agent/middleware/tool_error_handler.py:176-185]()

---

## Sandbox Reconnection

When a thread already has a sandbox (follow-up message), `get_sandbox_backend()` retrieves the cached proxy or reconnects using the persisted `sandbox_id`.

### Reconnection Logic
```mermaid
sequenceDiagram
    participant GA as "get_sandbox_backend()"
    participant Cache as "SANDBOX_BACKENDS"
    participant Metadata as "Thread Metadata"
    participant Factory as "create_sandbox()"
    
    GA->>Cache: "Check SANDBOX_BACKENDS[thread_id]"
    
    alt "Cache Hit (Warm Start)"
        Cache-->>GA: "SandboxBackendProxy"
        GA-->>GA: "Return proxy"
    else "Cache Miss (Cold Start)"
        Cache-->>GA: "None"
        GA->>Metadata: "get_sandbox_id_from_metadata(thread_id)"
        Metadata-->>GA: "sandbox_id (e.g., 'sb-abc-123')"
        
        GA->>Factory: "create_sandbox(sandbox_id='sb-abc-123')"
        Note over Factory: "Connect to existing instance"
        Factory-->>GA: "sandbox_backend"
        
        GA->>Cache: "set_sandbox_backend(thread_id, backend)"
        GA-->>GA: "Return proxy"
    end
```

**Reconnection Scenarios:**
- **Warm start**: Proxy exists in `SANDBOX_BACKENDS`. The system proceeds immediately [agent/utils/sandbox_state.py:169-171]().
- **Cold start**: Backend missing from cache but `sandbox_id` exists in metadata. The system calls `create_sandbox(sandbox_id=...)` [agent/utils/sandbox_state.py:173-178]().

**Sources:** [agent/utils/sandbox_state.py:167-179](), [agent/utils/sandbox.py:20-37]()

---

## Sandbox Recreation

If a sandbox becomes unreachable (e.g., provider-side termination), `ToolErrorMiddleware` catches `SandboxClientError` and triggers `_recreate_sandbox_for_thread()`.

### Recreation Sequence
```mermaid
sequenceDiagram
    participant Middleware as "ToolErrorMiddleware"
    participant RecreateFunc as "_recreate_sandbox()"
    participant Proxy as "SandboxBackendProxy"
    participant Factory as "create_sandbox()"
    
    Middleware->>Middleware: "Catch SandboxClientError"
    Middleware->>RecreateFunc: "Call _recreate_sandbox(thread_id)"
    
    RecreateFunc->>Metadata: "Set sandbox_id = '__creating__'"
    RecreateFunc->>Factory: "create_sandbox(sandbox_id=None)"
    Factory-->>RecreateFunc: "new_backend"
    
    RecreateFunc-->>Middleware: "new_backend"
    Middleware->>Proxy: "replace_backend(new_backend)"
    Note over Middleware: "Return error message to LLM to retry"
```

**Atomic Recreation:**
1. **Set sentinel** - Write `SANDBOX_CREATING` to metadata [agent/server.py:195-198]().
2. **Create new sandbox** - Call `_create_sandbox_with_proxy()` [agent/server.py:200]().
3. **Swap Backend** - The `SandboxBackendProxy` is updated with the new instance via `replace_backend` [agent/utils/sandbox_state.py:41-42]().
4. **LLM Recovery** - A `ToolMessage` is returned to the agent explaining that a fresh sandbox has been created and it should re-clone or retry [agent/middleware/tool_error_handler.py:64-81]().

**Sources:** [agent/server.py:188-203](), [agent/middleware/tool_error_handler.py:116-124](), [agent/utils/sandbox_state.py:41-42]()

---

## Concurrent Creation Handling

When multiple events arrive simultaneously for the same thread, the `SANDBOX_CREATING` sentinel prevents duplicate creation.

**Constants:**
- `SANDBOX_CREATING`: `"__creating__"` [agent/server.py:85]().
- `SANDBOX_CREATION_TIMEOUT`: `180` seconds [agent/server.py:86]().
- `SANDBOX_POLL_INTERVAL`: `1.0` second [agent/server.py:87]().

---

## Circuit Breaker

To prevent infinite loops of sandbox recreation, the `SandboxCircuitBreakerMiddleware` monitors the message history for consecutive failures.

| Feature | Description |
|---------|-------------|
| **Threshold** | Triggers after 2 consecutive failures [agent/middleware/sandbox_circuit_breaker.py:24]() |
| **Detection** | Scans `ToolMessage` content for `SandboxClientError` or `RECREATED` markers [agent/middleware/sandbox_circuit_breaker.py:72-92]() |
| **Action** | Jumps to `end` and notifies the user via Slack, Linear, or GitHub [agent/middleware/sandbox_circuit_breaker.py:168-193]() |

**Sources:** [agent/middleware/sandbox_circuit_breaker.py:24-28](), [agent/middleware/sandbox_circuit_breaker.py:67-102](), [agent/middleware/sandbox_circuit_breaker.py:168-193]()

---

# Page: Repository Management

# Repository Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/prompt.py](agent/prompt.py)
- [agent/utils/authorship.py](agent/utils/authorship.py)
- [agent/utils/repo.py](agent/utils/repo.py)
- [scripts/__init__.py](scripts/__init__.py)
- [scripts/check_pr_merge_status.py](scripts/check_pr_merge_status.py)
- [tests/test_github_comment_prompts.py](tests/test_github_comment_prompts.py)
- [tests/test_repo_extraction.py](tests/test_repo_extraction.py)

</details>



Repository management in Open SWE handles cloning GitHub repositories into sandboxes, maintaining repository state across agent runs, managing git credentials securely, and detecting changes. Each thread receives its own isolated copy of the target repository within a dedicated sandbox environment.

For information about sandbox lifecycle and persistence, see **4.3 Sandbox Lifecycle Management**. For authentication and token handling, see **7.1 GitHub Token Resolution**.

---

## Repository Lifecycle

The repository lifecycle is managed within the `get_agent()` and `_clone_or_pull_repo_in_sandbox()` functions. It ensures that every agent run has access to a functional git repository, either by reusing a cached sandbox or provisioning a new one.

### Lifecycle Data Flow

Title: Repository Provisioning Flow
```mermaid
graph TB
    subgraph "Agent Initialization"
        ThreadID["thread_id from config"]
        GetAgent["get_agent() invocation"]
        RepoConfig["repo config<br/>{owner, name}"]
    end
    
    subgraph "Sandbox Check"
        SandboxExists{"Sandbox exists<br/>in cache?"}
        SandboxID["get_sandbox_id_from_metadata()"]
        CreateSandbox["_create_sandbox_with_proxy()"]
    end
    
    subgraph "Repository Operations"
        CloneOrPull["_clone_or_pull_repo_in_sandbox()"]
        ResolveRepoDir["aresolve_repo_dir()"]
        IsValidRepo{"is_valid_git_repo()?"}
        RemoveDir["remove_directory()"]
        GitClone["git clone via execute()"]
        GitPull["git pull via execute()"]
        HasChanges{"git_has_uncommitted_changes()?"}
    end
    
    subgraph "Credential Management"
        ProxyAuth["_configure_github_proxy()"]
        RefreshProxy["_refresh_github_proxy()"]
    end
    
    subgraph "Repository State"
        RepoDir["/workspace/repo-name"]
        AgentsMD["read_agents_md_in_sandbox()"]
        RepoPersist["Persist repo_dir in thread metadata"]
    end
    
    ThreadID --> GetAgent
    RepoConfig --> GetAgent
    GetAgent --> SandboxExists
    
    SandboxExists -->|No| CreateSandbox
    SandboxExists -->|Yes| SandboxID
    
    CreateSandbox --> ProxyAuth
    ProxyAuth --> CloneOrPull
    
    SandboxID --> RefreshProxy
    RefreshProxy --> CloneOrPull
    
    CloneOrPull --> ResolveRepoDir
    ResolveRepoDir --> IsValidRepo
    
    IsValidRepo -->|No| RemoveDir
    RemoveDir --> GitClone
    
    IsValidRepo -->|Yes| HasChanges
    HasChanges -->|Yes| RepoDir
    HasChanges -->|No| GitPull
    
    GitClone --> RepoDir
    GitPull --> RepoDir
    
    RepoDir --> AgentsMD
    RepoDir --> RepoPersist
```
**Sources:** [agent/server.py:81-172](), [agent/server.py:175-214](), [agent/server.py:275-310](), [agent/utils/github.py:26-44]()

---

## Clone and Pull Logic

The `_clone_or_pull_repo_in_sandbox` function orchestrates repository provisioning with intelligent decision-making based on repository state.

### Repository State Detection

Title: State Transition for Repo Sync
```mermaid
graph LR
    Start["_clone_or_pull_repo_in_sandbox()"]
    ResolveDir["aresolve_repo_dir()<br/>/workspace/repo-name"]
    ValidRepo{"is_valid_git_repo()?<br/>test -d .git"}
    
    Start --> ResolveDir
    ResolveDir --> ValidRepo
    
    ValidRepo -->|True| CheckChanges{"git_has_uncommitted_changes()?<br/>git status --porcelain"}
    ValidRepo -->|False| RemoveAndClone["remove_directory()<br/>rm -rf /workspace/repo-name"]
    
    CheckChanges -->|True| SkipPull["Skip pull<br/>Return repo_dir"]
    CheckChanges -->|False| Pull["git pull origin ..."]
    
    RemoveAndClone --> Clone["git clone"]
    Pull --> Return["Return repo_dir"]
    Clone --> Return
    SkipPull --> Return
```

| Condition | Action | Reason |
|-----------|--------|--------|
| `.git` directory missing | Remove directory, clone fresh | Invalid/corrupted repository |
| Uncommitted changes present | Skip pull, return existing | Preserve agent's work in progress |
| Clean working tree | Execute `git pull` | Update to latest remote state |

**Sources:** [agent/server.py:81-172](), [agent/utils/github.py:26-44]()

### Clone Operation

When cloning a fresh repository, the system uses the `git clone` command. Authentication is handled transparently by the sandbox proxy (for LangSmith providers), so the URL remains clean.

```python
# Executed in sandbox via sandbox_backend.execute()
# [agent/server.py:159]
f"git clone {shlex.quote(clean_url)} {shlex.quote(repo_dir)}"
```

The clone command:
- Uses the clean HTTPS URL: `https://github.com/{owner}/{repo}.git`
- Clones to a deterministic path resolved by `aresolve_repo_dir()`
- Exits with code 0 on success, raising `RuntimeError` otherwise [agent/server.py:166-169]().

### Pull Operation

When updating an existing repository:

```python
# Executed in sandbox
# [agent/server.py:138]
f"cd {shlex.quote(repo_dir)} && git pull origin $(git rev-parse --abbrev-ref HEAD)"
```

The pull command:
- Updates the current branch from its upstream origin.
- Is skipped if `git_has_uncommitted_changes()` returns `True` [agent/server.py:128-130]().
- Logs a warning if the exit code is non-zero but does not necessarily halt the agent [agent/server.py:141-146]().

**Sources:** [agent/server.py:81-172](), [agent/utils/github.py:41-44]()

---

## Git Credential Handling

Open SWE uses a sophisticated proxy-based approach for git credentials when using LangSmith sandboxes. This prevents tokens from being written to disk or appearing in command-line arguments within the sandbox environment.

### Proxy Authentication Configuration

For LangSmith sandboxes, `_configure_github_proxy` is called during sandbox creation or reconnection.

Title: LangSmith Proxy Credential Injection
```mermaid
sequenceDiagram
    participant S as agent/server.py
    participant L as agent/integrations/langsmith.py
    participant API as LangSmith API
    participant G as GitHub.com
    
    S->>L: _configure_github_proxy(sandbox_id, token)
    L->>API: PATCH /v2/sandboxes/boxes/{id}
    Note right of API: Payload includes Basic Auth<br/>for *.github.com
    API-->>L: 200 OK
    
    Note over S, G: Later, inside the Sandbox...
    S->>G: git clone https://github.com/...
    Note over G: Proxy intercepts request,<br/>injects Authorization header
```

**Implementation Details:**
- **Token Source**: Uses the GitHub App installation token via `get_github_app_installation_token()` [agent/server.py:185]().
- **Proxy Rules**: Configures a rule to match `github.com` and `*.github.com` [agent/integrations/langsmith.py:60]().
- **Header Injection**: Injects an `Authorization` header with `Basic` auth containing the base64-encoded installation token [agent/integrations/langsmith.py:61-67]().

**Sources:** [agent/integrations/langsmith.py:37-80](), [agent/server.py:175-192](), [tests/test_proxy_auth.py:17-53]()

---

## Repository Directory Resolution

Repository directories are resolved dynamically using the `aresolve_repo_dir` utility.

### Path Resolution Strategy

Title: Sandbox Path Resolution Logic
```mermaid
graph TB
    Start["aresolve_repo_dir(sandbox_backend, repo)"]
    WorkDir["aresolve_sandbox_work_dir(sandbox_backend)"]
    
    subgraph "Work Directory Discovery"
        GetWorkDir["sandbox_backend.get_work_dir()"]
        PWD["sandbox_backend.execute('pwd')"]
    end
    
    JoinPath["posixpath.join(work_dir, repo)"]
    
    Start --> WorkDir
    WorkDir --> GetWorkDir
    GetWorkDir -->|Fails| PWD
    WorkDir --> JoinPath
    JoinPath --> RepoDir["/workspace/repo-name"]
```

The `aresolve_sandbox_work_dir` function first attempts to use the provider's native `get_work_dir()` method. If that fails or is unavailable, it falls back to executing `pwd` within the sandbox [agent/utils/sandbox_paths.py:34-56](). The repository directory is then formed by joining this work directory with the repository name.

**Sources:** [agent/utils/sandbox_paths.py:34-56](), [agent/utils/sandbox_paths.py:58-71]()

---

## Uncommitted Change Detection

Open SWE monitors the state of the repository to prevent accidental overwrites and to determine if a PR needs to be opened.

### Change Detection Functions

| Function | Implementation | Purpose |
|----------|----------------|---------|
| `git_has_uncommitted_changes` | `git status --porcelain` | Returns `True` if there are staged or unstaged changes in the working tree [agent/utils/github.py:41-44](). |
| `git_has_unpushed_commits` | `git log --oneline @{upstream}..HEAD` | Returns `True` if there are local commits that have not been pushed to the remote origin [agent/utils/github.py:52-59](). |

### Usage in Middleware

The `open_pr_if_needed` middleware uses these checks as a "safety net". If the agent finishes its task but hasn't called the `commit_and_open_pr` tool, the middleware checks for changes.

```python
# [agent/middleware/open_pr.py:120-129]
has_uncommitted_changes = await asyncio.to_thread(
    git_has_uncommitted_changes, sandbox_backend, repo_dir
)
await asyncio.to_thread(git_fetch_origin, sandbox_backend, repo_dir)
has_unpushed_commits = await asyncio.to_thread(
    git_has_unpushed_commits, sandbox_backend, repo_dir
)

has_changes = has_uncommitted_changes or has_unpushed_commits
```

If `has_changes` is `True`, the middleware automatically proceeds to configure the git user, commit the changes, push the branch, and open a PR [agent/middleware/open_pr.py:131-176]().

**Sources:** [agent/utils/github.py:41-59](), [agent/middleware/open_pr.py:120-176]()

---

## Commit Attribution and Identity

Open SWE supports collaborative attribution by injecting `Co-authored-by` trailers into commits and adding collaboration notes to PR descriptions.

### Identity Resolution

The `resolve_triggering_user_identity` function determines the user's git identity (name and email) by checking the GitHub token or falling back to Slack/Linear metadata [agent/utils/authorship.py:117-128]().

### Attribution Implementation

| Code Entity | File Path | Role |
|-------------|-----------|------|
| `CollaboratorIdentity` | `agent/utils/authorship.py` | Data class holding user identity for trailers [agent/utils/authorship.py:19-25](). |
| `add_user_coauthor_trailer` | `agent/utils/authorship.py` | Appends `Co-authored-by: name <email>` to commit messages [agent/utils/authorship.py:131-143](). |
| `add_pr_collaboration_note` | `agent/utils/authorship.py` | Appends a collaborative note to the PR body [agent/utils/authorship.py:146-165](). |

The agent's system prompt explicitly instructs it to set a specific bot identity immediately after cloning: `git config user.name 'open-swe[bot]'` and `git config user.email 'open-swe@users.noreply.github.com'` [agent/prompt.py:93]().

**Sources:** [agent/utils/authorship.py:1-166](), [agent/prompt.py:80-106]()

---

## Tool-Based Git Management

The agent primarily interacts with the repository through the `commit_and_open_pr` tool. This tool encapsulates the complex logic of preparing a submission.

### Commit and PR Workflow

1. **Change Validation**: Checks `git_has_uncommitted_changes` and `git_has_unpushed_commits` [agent/tools/commit_and_open_pr.py:147-152]().
2. **Branch Management**: Switches to a feature branch (e.g., `open-swe/{thread_id}`) [agent/tools/commit_and_open_pr.py:157-173]().
3. **Identity Resolution**: Resolves the triggering user's identity to add co-author trailers to the commit message [agent/tools/commit_and_open_pr.py:144-145](), [agent/tools/commit_and_open_pr.py:183]().
4. **Git Configuration**: Configures `user.name` and `user.email` within the sandbox [agent/tools/commit_and_open_pr.py:175-180]().
5. **Staging and Committing**: Executes `git add -A` and `git commit -m ...` [agent/tools/commit_and_open_pr.py:181-185]().
6. **Pushing**: Executes `git push origin {branch}` [agent/tools/commit_and_open_pr.py:192]().
7. **PR Creation**: Calls `create_github_pr` via the GitHub API [agent/tools/commit_and_open_pr.py:202-210]().

**Sources:** [agent/tools/commit_and_open_pr.py:120-212](), [agent/utils/github.py:139-176]()

---

# Page: Context Engineering

# Context Engineering

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/prompt.py](agent/prompt.py)
- [agent/utils/agents_md.py](agent/utils/agents_md.py)
- [tests/test_github_comment_prompts.py](tests/test_github_comment_prompts.py)

</details>



This page documents how Open SWE gathers and injects context into the agent's system prompt from two primary sources: repository-specific conventions via `AGENTS.md` files, and invocation-specific details from Linear issues, Slack threads, or GitHub PRs.

For information about how the agent is assembled with this context, see [Agent Assembly](#3.1). For details on the invocation surfaces that provide source context, see [Invocation Surfaces](#2).

---

## Overview

Open SWE implements a **context engineering** strategy that minimizes tool calls by front-loading the agent with rich context before execution begins. This approach follows the principle observed in elite internal coding agents: pre-hydrate context rather than force agents to discover information through iterative tool calls.

The system gathers context from two complementary sources:

1.  **Repository context** via `AGENTS.md` files that encode project-specific conventions, testing requirements, and architectural guidelines. [agent/prompt.py:66]()
2.  **Source context** from the triggering event (Linear issue details, Slack thread history, or GitHub PR comments) that provides full task information upfront.

### Context Mapping: Natural Language to Code Space

The following diagram bridges the natural language requirements (Issues/Comments) to the specific code entities and prompt sections that handle them.

```mermaid
graph TD
    subgraph "Natural Language Space"
        UserIssue["User Issue / Comment"]
        RepoRules["AGENTS.md (Human Rules)"]
    end

    subgraph "Context Assembly (Code Space)"
        FetchMD["fetch_agents_md()<br/>agent/utils/agents_md.py"]
        BuildPR["build_pr_prompt()<br/>agent/utils/github_comments.py"]
        BuildIssue["build_github_issue_prompt()<br/>agent/webapp.py"]
    end

    subgraph "System Prompt Sections (agent/prompt.py)"
        REPO_SETUP["REPO_SETUP_SECTION<br/>(Mandatory AGENTS.md step)"]
        TASK_EXEC["TASK_EXECUTION_SECTION<br/>(Workflow steps)"]
        UNTRUSTED["UNTRUSTED_GITHUB_COMMENT_OPEN_TAG"]
    end

    UserIssue --> BuildPR
    UserIssue --> BuildIssue
    RepoRules --> FetchMD
    
    FetchMD --> REPO_SETUP
    BuildPR --> UNTRUSTED
    BuildIssue --> TASK_EXEC
```

**Sources:** [agent/prompt.py:80-106](), [agent/utils/agents_md.py:20-27](), [agent/utils/github_comments.py:10-19]()

---

## AGENTS.md Convention

The `AGENTS.md` convention allows repository owners to encode project-specific knowledge that should inform every agent run. This file is treated with the same authority as the system prompt. [agent/prompt.py:102]()

### Mandatory Discovery
The agent is explicitly instructed in the `REPO_SETUP_SECTION` that reading `AGENTS.md` is **mandatory** immediately after cloning a repository. [agent/prompt.py:102-104]()

### Remote Fetching for Reviewers
While the standard agent reads the file from the sandbox, the Reviewer Agent uses `fetch_agents_md` to pull the file via the GitHub API. This allows the reviewer to understand repository conventions without needing a full clone. [agent/utils/agents_md.py:20-32]()

| Feature | Implementation |
| :--- | :--- |
| **Max Size** | Capped at 64KB to prevent context bloat. [agent/utils/agents_md.py:17]() |
| **Auth** | Uses GitHub App or OAuth tokens for private repos. [agent/utils/agents_md.py:41-43]() |
| **Enforcement** | Violating `AGENTS.md` is defined as a "CRITICAL FAILURE". [agent/prompt.py:102]() |

For details, see [AGENTS.md Convention](#5.1).

**Sources:** [agent/prompt.py:80-106](), [agent/utils/agents_md.py:15-73]()

---

## Source Context Assembly

Source context is gathered from the invocation surface (Linear, Slack, or GitHub) before the agent run is created.

### GitHub Context & Security
When processing GitHub comments, Open SWE distinguishes between trusted internal users and external contributors. External comments are wrapped in specific XML-like tags to alert the model. [agent/utils/github_comments.py:6](), [tests/test_github_comment_prompts.py:21-24]()

```mermaid
graph LR
    subgraph "Data Retrieval"
        GH_API["GitHub API"]
    end

    subgraph "Prompt Construction"
        PR_Prompt["build_pr_prompt()"]
        Issue_Prompt["build_github_issue_prompt()"]
    end

    subgraph "Security Layer"
        Tagging["UNTRUSTED_GITHUB_COMMENT_OPEN_TAG"]
    end

    GH_API --> PR_Prompt
    GH_API --> Issue_Prompt
    PR_Prompt --> Tagging
    Issue_Prompt --> Tagging
```

### Collaborative Identity
If a specific user triggers the agent, their identity is injected into the prompt to allow for "Co-authored-by" attribution in git commits. [agent/prompt.py:5-6](), [tests/test_github_comment_prompts.py:49-64]()

For details, see [Source Context Assembly](#5.2).

**Sources:** [agent/prompt.py:5-6](), [agent/utils/github_comments.py:6-23](), [tests/test_github_comment_prompts.py:9-114]()

---

## Prompt Structure

The system prompt is composed of modular sections defined in `agent/prompt.py`:

*   **`WORKING_ENV_SECTION`**: Defines the Linux sandbox environment and tool usage rules. [agent/prompt.py:38-55]()
*   **`SELF_AWARENESS_SECTION`**: Instructions on when the agent should consider itself the target of the task (the `open-swe` repo). [agent/prompt.py:69-77]()
*   **`TASK_EXECUTION_SECTION`**: Defines the 5-step workflow: Understand, Implement, Verify, Submit, Comment. [agent/prompt.py:119-137]()
*   **`CUSTOM_INSTRUCTIONS`**: Loaded from a local `default_prompt.md` file if it exists, allowing for global deployment-level overrides. [agent/prompt.py:10-35]()

**Sources:** [agent/prompt.py:10-137]()

---

# Page: AGENTS.md Convention

# AGENTS.md Convention

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [AGENTS.md](AGENTS.md)
- [CLAUDE.md](CLAUDE.md)
- [agent/prompt.py](agent/prompt.py)
- [agent/utils/agents_md.py](agent/utils/agents_md.py)
- [tests/test_github_comment_prompts.py](tests/test_github_comment_prompts.py)

</details>



This page documents the `AGENTS.md` file format and the mechanism by which repository-specific conventions, testing requirements, and architectural guidelines are injected into every agent run.

## Overview

The `AGENTS.md` file is Open SWE's primary mechanism for encoding repository-level knowledge that guides the agent's behavior. Unlike the global system prompt, `AGENTS.md` allows individual project owners to define mandatory rules that override or extend the agent's default behavior for a specific codebase [agent/prompt.py:102-104]().

**Key Characteristics:**
- **Authority**: The contents of `AGENTS.md` are treated with the same authority as the system prompt. Violating these rules is considered a critical failure [agent/prompt.py:102]().
- **Mandatory Discovery**: The agent is explicitly instructed to check for and read this file immediately after cloning a repository, before performing any implementation work [agent/prompt.py:102-104]().
- **Scope**: Covers project-specific commands (testing, linting), architectural patterns, and development workflows [AGENTS.md:11-36]().

**Sources:** [agent/prompt.py:82-106](), [AGENTS.md:1-10]()

## Injection Mechanism

Open SWE uses two distinct methods to handle `AGENTS.md` depending on the graph type (Coding Agent vs. Reviewer Agent).

### 1. Agent-Led Discovery (Main Agent)
For the main coding agent (`agent.server:get_agent`), the file is not pre-injected into the prompt. Instead, the system prompt contains a mandatory instruction requiring the agent to use its file-reading tools to discover the file [agent/prompt.py:102]().

### 2. Automated Injection (Reviewer Agent)
For the reviewer graph (`agent.reviewer:get_reviewer_agent`), the system proactively fetches `AGENTS.md` using the GitHub API to ensure the reviewer has context without needing to perform a full clone and manual read [agent/utils/agents_md.py:1-5]().

**Data Flow: Reviewer Context Injection**

```mermaid
graph TB
    subgraph "Natural Language Space"
        Conventions["Repository Rules<br/>(Testing, Style)"]
        MarkdownFile["AGENTS.md File"]
    end
    
    subgraph "Code Entity Space (Implementation)"
        FetchUtil["agent/utils/agents_md.py<br/>fetch_agents_md()"]
        ReviewerGraph["agent/reviewer.py<br/>get_reviewer_agent()"]
        GitHubAPI["api.github.com/repos/.../contents/AGENTS.md"]
    end
    
    subgraph "LLM Context"
        FinalPrompt["Reviewer System Prompt<br/>+ AGENTS.md Appendix"]
    end
    
    Conventions --> MarkdownFile
    MarkdownFile --> GitHubAPI
    GitHubAPI -- "raw content" --> FetchUtil
    FetchUtil -- "text string" --> ReviewerGraph
    ReviewerGraph -- "inlines" --> FinalPrompt
```

**Sources:** [agent/utils/agents_md.py:1-73](), [agent/reviewer.py:41-42](), [agent/prompt.py:102-106]()

## Implementation Details

### Fetching Logic
The `fetch_agents_md` function retrieves the file content via the GitHub API using a specific ref (branch/commit). It includes a size cap (default 64KB) to prevent context bloat [agent/utils/agents_md.py:17-31]().

| Feature | Implementation | File Reference |
| :--- | :--- | :--- |
| **API Endpoint** | `repos/{owner}/{repo}/contents/AGENTS.md` | [agent/utils/agents_md.py:36]() |
| **Size Limit** | `_MAX_AGENTS_MD_BYTES` (64 KB) | [agent/utils/agents_md.py:17]() |
| **Auth** | Bearer token injection | [agent/utils/agents_md.py:42]() |
| **Error Handling** | Returns `None` on 404 or timeout | [agent/utils/agents_md.py:51-61]() |

### Agent Instructions
The `REPO_SETUP_SECTION` of the system prompt enforces the "Step 6: MANDATORY: READ AGENTS.md" rule. This section explicitly states that these rules override default behavior [agent/prompt.py:102]().

**Sequence: Mandatory Discovery in Sandbox**

```mermaid
sequenceDiagram
    participant A as Open SWE Agent
    participant S as Sandbox (Linux)
    participant FS as File System

    Note over A: Step 1-5: Clone & Setup
    A->>S: execute("ls AGENTS.md")
    S->>FS: check existence
    FS-->>S: File exists
    S-->>A: "AGENTS.md"
    A->>S: read_file("AGENTS.md")
    S->>FS: cat AGENTS.md
    FS-->>S: content
    S-->>A: [Markdown Content]
    Note over A: Rules integrated into reasoning
    A->>S: Proceed with Task
```

**Sources:** [agent/prompt.py:82-106](), [agent/utils/agents_md.py:20-73]()

## Recommended Content Structure

Based on the `AGENTS.md` used within the `open-swe` repository itself, the following sections are recommended:

| Section | Description | Example (from Open SWE) |
| :--- | :--- | :--- |
| **Project** | High-level architecture and framework choice. | "Built on LangGraph + Deep Agents" [AGENTS.md:7]() |
| **Commands** | Dependency management and test execution. | "Dependencies managed with uv. Tests use pytest." [AGENTS.md:13]() |
| **Architecture** | Entrypoints, lifecycle, and middleware order. | Explains `get_agent` vs `get_reviewer_agent` [AGENTS.md:40-42]() |
| **Lifecycle** | Details on sandbox persistence and reconnection. | Explains `ensure_sandbox_for_thread` logic [AGENTS.md:48-55]() |

### Sandbox Lifecycle Conventions
A critical use of `AGENTS.md` in this repository is documenting the sandbox state management. It defines how `SANDBOX_BACKENDS` are keyed by `thread_id` and the four cases for sandbox resolution (cached, creating, disconnected, or non-existent) [AGENTS.md:48-55]().

### Middleware Order
The file documents the specific order of the middleware stack, which is vital for understanding how messages are intercepted or modified before reaching the LLM [AGENTS.md:59-73]().

**Sources:** [AGENTS.md:1-82](), [agent/prompt.py:38-55]()

## Integration with Global Prompts

The `AGENTS.md` content complements the global `DEFAULT_PROMPT_PATH` [agent/prompt.py:10-13](). While the default prompt provides the "Working Environment" and "Self-Awareness" sections [agent/prompt.py:38-77](), `AGENTS.md` provides the "ground truth" for the specific repository being modified.

**Sources:** [agent/prompt.py:10-77](), [AGENTS.md:1-10]()

---

# Page: Source Context Assembly

# Source Context Assembly

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/utils/multimodal.py](agent/utils/multimodal.py)
- [agent/utils/slack.py](agent/utils/slack.py)
- [agent/webapp.py](agent/webapp.py)
- [tests/test_github_issue_webhook.py](tests/test_github_issue_webhook.py)

</details>



Source Context Assembly is the process of gathering full invocation context from the triggering platform (Linear, Slack, or GitHub) and pre-hydrating it into the agent's initial prompt. This minimizes the overhead of the agent discovering context through tool calls by providing rich structured information upfront.

For information about repository-level context injection via `AGENTS.md`, see [AGENTS.md Convention](#5.1).

---

## Purpose and Architecture

When an agent is triggered by a Linear comment, Slack mention, or GitHub PR comment, the system immediately fetches the complete context before creating the LangGraph run. This includes:

- **Linear**: Full issue details, description, all comments, project/team metadata, and triggering user information.
- **Slack**: Thread history with intelligent context windowing from the last bot mention or thread start.
- **GitHub**: Issue/PR details, all comments across three GitHub comment types (issue comments, review comments, reviews), ordered chronologically.

The assembled context is passed as the initial user message in the run's `input` payload, eliminating the need for the agent to call tools like `fetch_url` or `http_request` to discover basic task information.

**Sources:**
- [agent/webapp.py:481-949]()
- [agent/webapp.py:1028-1240]()

---

## Data Flow: Webhook to Context Assembly

The following diagram illustrates how incoming webhook events from "Natural Language Space" (Slack/Linear/GitHub) are transformed into structured "Code Entity Space" objects within the `agent/webapp.py` FastAPI application.

```mermaid
flowchart TD
    Webhook["Webhook Event<br/>(Linear/Slack/GitHub)"] --> Verify["Signature Verification<br/>verify_slack_signature<br/>verify_github_signature"]
    Verify --> Extract["Extract Basic Payload<br/>issue_id, thread_ts, pr_number"]
    Extract --> Fetch["Fetch Full Context<br/>API calls to source platform"]
    
    Fetch --> Linear["fetch_linear_issue_details<br/>(Linear GraphQL API)"]
    Fetch --> Slack["fetch_slack_thread_messages<br/>(Slack conversations.replies)"]
    Fetch --> GitHub["fetch_issue_comments<br/>fetch_pr_comments_since_last_tag"]
    
    Linear --> ProcessLinear["linear_webhook handler<br/>Build prompt with comments"]
    Slack --> ProcessSlack["slack_webhook handler<br/>Select context window"]
    GitHub --> ProcessGitHub["github_webhook handler<br/>Merge comment sources"]
    
    ProcessLinear --> ContentBlocks["Build Content Blocks<br/>create_text_block + images"]
    ProcessSlack --> ContentBlocks
    ProcessGitHub --> ContentBlocks
    
    ContentBlocks --> Configurable["Assemble Configurable Metadata<br/>repo, source, linear_issue, slack_thread"]
    Configurable --> RunCreate["langgraph_sdk.get_client().runs.create<br/>input={'messages': [{'role': 'user', 'content': blocks}]}"]
```

**Sources:**
- [agent/webapp.py:34-53]() (Imported verification and fetch utilities)
- [agent/webapp.py:481-696]() (Linear processing logic)
- [agent/webapp.py:698-810]() (Slack processing logic)
- [agent/webapp.py:1028-1240]() (GitHub processing logic)

---

## Linear Issue Context Assembly

### Fetching Full Issue Details

The webhook payload from Linear contains minimal issue metadata. The system immediately calls `fetch_linear_issue_details()` to retrieve complete information via the Linear GraphQL API.

**Function:** `fetch_linear_issue_details` [agent/webapp.py:228-293]()

**GraphQL Query Fields:**
- `id`, `identifier`, `title`, `description`, `url`
- `project { id, name }`
- `team { id, name, key }`
- `comments { nodes { id, body, createdAt, user { id, name, email } } }`

### Comment Processing and Filtering

Linear issues may accumulate many comments over time, including bot-generated status messages. The system applies intelligent filtering:

1. **Triggering Comment Detection**: If the webhook includes a `triggering_comment_id`, only comments from that point forward are included ([agent/webapp.py:633-640]()).
2. **Bot Message Exclusion**: Comments starting with bot prefixes defined in `_GITHUB_BOT_MESSAGE_PREFIXES` are filtered out ([agent/webapp.py:164-172](), [agent/webapp.py:612-660]()).
3. **Fallback to Recent Comments**: If no triggering comment is identified, `get_recent_comments()` retrieves the most recent non-bot comments ([agent/webapp.py:40-40](), [agent/webapp.py:642-642]()).

### Multimodal Content Handling

The system extracts image URLs from both the issue description and comments using `extract_image_urls()` ([agent/utils/multimodal.py:25-37]()). For each discovered URL, it fetches the image content as a base64-encoded block using `fetch_image_block()` ([agent/utils/multimodal.py:40-99]()).

**Image URL Deduplication:** `dedupe_urls()` [agent/utils/multimodal.py:102-103]()

### Prompt Construction

The final prompt combines all elements into a structured message:

```python
prompt = (
    f"Please work on the following issue:\n\n"
    f"## Title: {title}\n\n"
    f"{triggered_by_line}"
    f"## Linear Ticket: {identifier} - Ticket ID: {issue_id}\n\n"
    f"## Description:\n{description}\n"
    f"{comments_text}\n\n"
    f"Please analyze this issue and implement the necessary changes. "
    f"When you're done, commit and push your changes. {tag_instruction}"
)
```

**Sources:**
- [agent/webapp.py:481-696]()
- [agent/utils/multimodal.py:25-99]()

---

## Slack Thread Context Assembly

### Thread Message Fetching

Slack threads are retrieved using `fetch_slack_thread_messages()`, which calls the `conversations.replies` API with pagination support.

**Function:** `fetch_slack_thread_messages` [agent/utils/slack.py:384-420]()

### Intelligent Context Windowing

Slack applies windowing to avoid overwhelming the agent with irrelevant history. The `select_slack_context_messages()` function implements two strategies based on previous bot mentions.

```mermaid
flowchart TD
    Start["Thread Messages<br/>(sorted by timestamp)"] --> Filter["Filter messages up to<br/>current_message_ts"]
    Filter --> SearchMentions["Search for previous<br/>bot mentions<br/>(@openswe or bot_user_id)"]
    
    SearchMentions --> FoundMention{Previous<br/>mention found?}
    
    FoundMention -->|Yes| LastMention["Return messages from<br/>last mention onwards<br/>context_mode='last_mention'"]
    FoundMention -->|No| ThreadStart["Return all messages<br/>context_mode='thread_start'"]
    
    LastMention --> ContextMessages["Context Messages"]
    ThreadStart --> ContextMessages
```

**Function:** `select_slack_context_messages` [agent/utils/slack.py:207-251]()

**Context Modes:**
- `"thread_start"`: Include all messages from the beginning of the thread.
- `"last_mention"`: Include only messages since the last time the bot was mentioned.

### User Name Resolution

Slack user IDs (e.g., `U01ABC123`) are resolved to display names by calling `get_slack_user_names()`, which batches `users.info` API calls.

**Function:** `get_slack_user_names` [agent/utils/slack.py:364-381]()

### Message Formatting

The `format_slack_messages_for_prompt()` function converts Slack messages into a readable conversation format, replacing bot ID tokens with readable usernames.

**Function:** `format_slack_messages_for_prompt` [agent/utils/slack.py:254-286]()
**Mention Utility:** `replace_bot_mention_with_username` [agent/utils/slack.py:93-99]()

**Sources:**
- [agent/webapp.py:698-810]()
- [agent/utils/slack.py:93-286]()
- [agent/utils/slack.py:384-420]()

---

## GitHub Issue and PR Context Assembly

GitHub context is assembled by unifying three distinct comment types into a single chronological stream.

### GitHub Comment Sources

```mermaid
graph TB
    subgraph "GitHub API Entities"
        IssueComment["Issue Comments<br/>GET /repos/{owner}/{repo}/issues/{number}/comments"]
        ReviewComment["Review Comments<br/>GET /repos/{owner}/{repo}/pulls/{number}/comments<br/>(Inline code feedback)"]
        Review["Review Bodies<br/>GET /repos/{owner}/{repo}/pulls/{number}/reviews"]
    end
    
    subgraph "Assembly Logic"
        Merged["fetch_pr_comments_since_last_tag<br/>Merged and sorted by created_at"]
    end
    
    IssueComment --> Merged
    ReviewComment --> Merged
    Review --> Merged
```

### Fetching PR Comments Since Last Tag

For PR review workflows, the system only fetches comments since the last `@openswe` mention to avoid reprocessing.

**Function:** `fetch_pr_comments_since_last_tag` [agent/utils/github_comments.py:214-318]()

**Tag Detection:** The system searches for `OPEN_SWE_TAGS` (`@openswe`, `@open-swe`, `@openswe-dev`) in the comment bodies ([agent/utils/github_comments.py:25-25](), [agent/utils/github_comments.py:304-308]()).

### Untrusted User Handling

GitHub issues are public. To prevent prompt injection, comments from users not in `GITHUB_USER_EMAIL_MAP` are wrapped in safety tags.

**Function:** `format_github_comment_body_for_prompt` [agent/utils/github_comments.py:74-84]()
**Security Tags:** `UNTRUSTED_GITHUB_COMMENT_OPEN_TAG` [agent/utils/github_comments.py:1-1]()

### PR Review Prompt Construction

The `build_pr_prompt()` function formats PR comments with file context (path and line number) for inline review comments.

**Function:** `build_pr_prompt` [agent/utils/github_comments.py:386-412]()

**Sources:**
- [agent/utils/github_comments.py:183-448]()
- [agent/webapp.py:1028-1240]()

---

## Configurable Metadata Assembly

Metadata is assembled into a `configurable` dict passed to the LangGraph run. This drives agent tools and authentication.

### Linear Configurable
- `repo`: Repository configuration.
- `linear_issue`: Includes `id`, `identifier` (e.g., "ENG-123"), and `url`.
- `user_email`: Used for GitHub token resolution.

**Sources:** [agent/webapp.py:650-663]()

### Slack Configurable
- `slack_thread`: Includes `channel_id`, `thread_ts`, and `triggering_user_id`.
- `user_email`: Resolved from Slack profile.

**Sources:** [agent/webapp.py:787-799]()

### GitHub Configurable
- `github_issue`: Includes `number` and `title`.
- `branch_name`: Extracted from the PR or issue context.

**Sources:** [agent/webapp.py:1208-1238]()

---

## Tool-Level Context Usage

Once the agent is running, it uses specific tools to interact with these sources:
- `slack_thread_reply`: Uses `configurable["slack_thread"]` to post replies ([agent/tools/slack_thread_reply.py:20-30]()).
- `linear_comment`: Posts comments to the issue identified in metadata ([agent/prompt.py:83-85]()).
- `github_comment`: Replies to the triggering GitHub issue or PR ([agent/prompt.py:94-95]()).

**Sources:**
- [agent/tools/slack_thread_reply.py:1-37]()
- [agent/prompt.py:67-95]()

---

# Page: Thread Management and State

# Thread Management and State

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/server.py](agent/server.py)
- [agent/tools/__init__.py](agent/tools/__init__.py)
- [agent/webapp.py](agent/webapp.py)
- [tests/test_github_issue_webhook.py](tests/test_github_issue_webhook.py)

</details>



This page documents how Open SWE manages conversation threads, deterministic thread ID generation, message queueing, and the persistence of metadata across agent invocations. These mechanisms enable persistent interactions, allowing users to send follow-up messages and maintain context across Linear issues, Slack threads, and GitHub PRs.

For details on how sandbox environments are managed per thread, see [Sandbox Lifecycle Management](#4.3). For details on token encryption within threads, see [Token Encryption and Storage](#7.3).

## Overview

Open SWE leverages LangGraph's thread abstraction to maintain conversation state. Each external trigger maps to a unique, deterministic LangGraph thread ID. This persistence allows the agent to maintain awareness of previous work and reuse resources like sandboxes and authentication tokens.

- **Follow-up Handling**: Users can continue conversations on the same Linear issue or Slack thread.
- **State Persistence**: Metadata such as `sandbox_id`, `repo_dir`, and encrypted tokens are stored within the thread.
- **Concurrency Control**: Concurrent events on the same thread are queued to ensure sequential processing.

**Sources:** [agent/webapp.py:90-91](), [agent/server.py:195-201](), [agent/server.py:258-336]()

---

## Thread ID Generation

Thread IDs are generated deterministically from the invocation source. This ensures that follow-up messages from the same external entity (e.g., a specific Slack thread) are routed to the same LangGraph state.

### Deterministic Thread ID Mapping

The mapping from "Natural Language Space" (where users interact via Slack, Linear, or GitHub) to "Code Entity Space" (the LangGraph `thread_id`) is handled by specific utility functions in `agent/webapp.py` and `agent/utils/github_comments.py`.

Title: Thread ID Generation Flow
```mermaid
graph TB
    subgraph "Natural Language Space (Triggers)"
        LinearIssue["Linear Issue ID<br/>(e.g., 'abc-123')"]
        GitHubIssue["GitHub Issue ID<br/>(e.g., '12345')"]
        SlackThread["Slack Thread<br/>(channel_id + thread_ts)"]
        GitHubBranch["GitHub PR Branch<br/>(contains UUID)"]
    end
    
    subgraph "Code Entity Space (Functions)"
        GenLinear["webapp.generate_thread_id_from_issue()"]
        GenGitHub["webapp.generate_thread_id_from_github_issue()"]
        GenSlack["webapp.generate_thread_id_from_slack_thread()"]
        ExtractBranch["github_comments.get_thread_id_from_branch()"]
    end
    
    subgraph "Deterministic Identifiers"
        UUID1["UUID via SHA256"]
        UUID2["UUID via SHA256"]
        UUID3["UUID via MD5"]
        UUID4["UUID via Regex"]
    end
    
    LinearIssue --> GenLinear
    GitHubIssue --> GenGitHub
    SlackThread --> GenSlack
    GitHubBranch --> ExtractBranch
    
    GenLinear --> UUID1
    GenGitHub --> UUID2
    GenSlack --> UUID3
    ExtractBranch --> UUID4
    
    UUID1 --> ThreadState["LangGraph Thread State"]
    UUID2 --> ThreadState
    UUID3 --> ThreadState
    UUID4 --> ThreadState
```

**Sources:** [agent/webapp.py:239-268](), [agent/utils/github_comments.py:53-57](), [tests/test_github_issue_webhook.py:64-70]()

For details on the specific hashing algorithms used for each platform, see [Thread ID Generation](#6.1).

---

## Message Queueing

When multiple events arrive for the same thread while the agent is already busy, Open SWE uses a queueing system to prevent lost messages and race conditions. This is managed by `queue_message_for_thread` and checked via middleware.

### Queue Architecture

Title: Message Queueing and Middleware Integration
```mermaid
sequenceDiagram
    participant Webhook as "agent/webapp.py"
    participant Store as "LangGraph Store"
    participant Middleware as "check_message_queue_before_model"
    participant Agent as "Agent Loop (LangGraph)"
    
    Webhook->>Webhook: is_thread_active() checks 'busy' status
    Webhook->>Store: queue_message_for_thread()
    
    Note over Agent: Agent finishes current step
    
    Agent->>Middleware: @before_model hook
    Middleware->>Store: get_item('pending_messages')
    Store-->>Middleware: List of new messages
    Middleware->>Agent: Inject messages into State
    Middleware->>Store: delete_item('pending_messages')
```

**Sources:** [agent/webapp.py:90-91](), [agent/server.py:50-51](), [agent/middleware/__init__.py:1-10]()

The `check_message_queue_before_model` middleware ensures that any user feedback provided while the agent was "thinking" is incorporated before the next model invocation. For details, see [Message Queueing](#6.2).

---

## Thread Metadata Storage

Thread metadata acts as the "memory" for the agent's infrastructure needs. It persists the environment configuration so that subsequent runs can reconnect to the same workspace.

### Metadata Schema and Usage

| Key | Purpose | Code Reference |
|---|---|---|
| `sandbox_id` | ID of the isolated environment (e.g., LangSmith, Modal) | [agent/utils/sandbox_state.py:91-92]() |
| `repo` | Dict containing `owner` and `name` | [agent/webapp.py:175-198]() |
| `github_token_encrypted` | Fernet-encrypted user or bot token | [agent/utils/auth.py:36-38]() |
| `reviewer_pr_meta` | Metadata for the Reviewer Agent runs | [agent/reviewer_findings.py:30-33]() |

### Sandbox State Transitions
The system uses a sentinel value `SANDBOX_CREATING` (`"__creating__"`) in the `sandbox_id` field to prevent multiple concurrent requests from attempting to provision a sandbox for the same thread simultaneously.

Title: Sandbox Metadata State Machine
```mermaid
graph TD
    Start["server.get_agent()"] --> CheckCache["Check SANDBOX_BACKENDS cache"]
    CheckCache -->|Miss| CheckMeta["Check metadata.sandbox_id"]
    CheckMeta -->|None| Provision["Set SANDBOX_CREATING<br/>Provision via create_sandbox()"]
    CheckMeta -->|"__creating__"| Wait["Poll for real ID"]
    CheckMeta -->|ID| Reconnect["Reconnect via set_sandbox_backend()"]
    Provision --> UpdateMeta["Update metadata with real ID"]
```

**Sources:** [agent/server.py:85-94](), [agent/server.py:195-201](), [agent/server.py:258-336](), [agent/utils/sandbox_state.py:90-94]()

For details on how these fields are updated and retrieved, see [Thread Metadata Storage](#6.3).

---

## Repo Configuration Persistence

Repository configuration is extracted from the initial trigger and stored to ensure consistency. For example, in Slack, the agent can be told which repo to use via a `repo:owner/name` syntax, which is then persisted.

- **Linear**: Resolved via `LINEAR_TEAM_TO_REPO` mapping in `agent/webapp.py`.
- **Slack**: Resolved via `get_slack_user_info` and repository extraction from the message body.
- **GitHub**: Extracted directly from the repository payload in the webhook.

**Sources:** [agent/webapp.py:175-198](), [agent/utils/github_comments.py:45-57](), [agent/utils/repo.py:65-65]()

---

# Page: Thread ID Generation

# Thread ID Generation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/webapp.py](agent/webapp.py)
- [tests/test_github_issue_webhook.py](tests/test_github_issue_webhook.py)
- [tests/test_slack_context.py](tests/test_slack_context.py)

</details>



Thread ID generation is the mechanism by which Open SWE creates deterministic, unique identifiers for conversation threads from different invocation sources. These thread IDs route follow-up messages to the correct LangGraph thread, enabling sandbox reuse, metadata persistence, and conversation continuity across multiple invocations.

---

## Overview

Open SWE generates thread IDs differently depending on the invocation source (Linear, Slack, GitHub issues, or GitHub pull requests). Each generation method ensures that:

1. **Determinism**: The same input always produces the same thread ID.
2. **Uniqueness**: Different inputs produce different thread IDs.
3. **Format consistency**: All thread IDs conform to UUID format (`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`).
4. **Reversibility**: For GitHub PRs, the thread ID can be extracted from the branch name.

The thread ID serves as the primary key for:
- LangGraph thread persistence via `langgraph_sdk` [agent/webapp.py:17-18]().
- Sandbox backend caching and lifecycle management [agent/webapp.py:66]().
- Encrypted GitHub token storage and retrieval [agent/utils/auth.py:36-37](), [agent/utils/github_token.py:60]().
- Message queueing for handling concurrent events [agent/utils/thread_ops.py:90]().

**Sources:** [agent/webapp.py:239-268](), [agent/utils/github_comments.py:51-57](), [agent/utils/thread_ops.py:90]()

---

## Thread ID Generation by Source

### Linear Issues

Linear thread IDs are generated deterministically from the Linear issue ID.

Linear Thread ID Generation Flow:
```mermaid
graph LR
    Input["Linear Issue ID<br/>e.g., 'abc123-def456'"]
    Namespace["Prepend Namespace<br/>'linear-issue:abc123-def456'"]
    Hash["SHA-256 Hash<br/>hexdigest"]
    Format["Format as UUID<br/>XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"]
    Output["Thread ID<br/>e.g., '3a2f8c1d-9e7b-4f2a-8c3d-5e6f1a2b3c4d'"]
    
    Input --> Namespace
    Namespace --> Hash
    Hash --> Format
    Format --> Output
```

The `generate_thread_id_from_issue()` function creates deterministic thread IDs for Linear issues by:
1. **Namespacing**: Prepending `"linear-issue:"` to the Linear issue ID [agent/webapp.py:240]().
2. **Hashing**: Computing the SHA-256 hash of the namespaced string [agent/webapp.py:240]().
3. **Formatting**: Extracting the first 32 hex characters and formatting as a UUID using string slicing [agent/webapp.py:242-245]().

**Sources:** [agent/webapp.py:239-252]()

---

### GitHub Issues

GitHub issue thread IDs follow a similar pattern to Linear but use a distinct namespace to prevent collisions.

GitHub Issue Thread ID Generation Flow:
```mermaid
graph LR
    Input["GitHub Issue ID<br/>e.g., '12345'"]
    Namespace["Prepend Namespace<br/>'github-issue:12345'"]
    Hash["SHA-256 Hash<br/>hexdigest"]
    Format["Format as UUID<br/>XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"]
    Output["Thread ID<br/>e.g., '7b4e2a9f-3c1d-4e8a-9f2b-6c3d5e1a4b7c'"]
    
    Input --> Namespace
    Namespace --> Hash
    Hash --> Format
    Format --> Output
```

The `generate_thread_id_from_github_issue()` function implements this logic [agent/webapp.py:255-261](). This is used for both GitHub issue mentions and issue comment events where the user tags `@openswe`. Determinism is verified in the test suite [tests/test_github_issue_webhook.py:64-70]().

**Sources:** [agent/webapp.py:255-261](), [tests/test_github_issue_webhook.py:64-70]()

---

### Slack Threads

Slack thread IDs are generated using a composite key of the channel and the thread timestamp.

Slack Thread ID Generation Flow:
```mermaid
graph LR
    Channel["Slack Channel ID<br/>e.g., 'C01234567'"]
    ThreadTS["Slack Thread TS<br/>e.g., '1234567890.123456'"]
    Composite["Composite String<br/>'C01234567:1234567890.123456'"]
    Hash["MD5 Hash<br/>hexdigest"]
    UUID["Convert to UUID<br/>using hex as UUID bytes"]
    Output["Thread ID<br/>e.g., 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'"]
    
    Channel --> Composite
    ThreadTS --> Composite
    Composite --> Hash
    Hash --> UUID
    UUID --> Output
```

The `generate_thread_id_from_slack_thread()` function uses MD5 hashing and the `uuid.UUID` constructor with the `hex` parameter [agent/webapp.py:264-268](). All replies in a Slack thread share the same `thread_ts`, ensuring they all route to the same deterministic thread ID [tests/test_slack_context.py:46-53]().

**Sources:** [agent/webapp.py:264-268](), [tests/test_slack_context.py:46-53]()

---

### GitHub Pull Requests

Unlike other sources, GitHub PRs use a **reverse extraction** approach. The thread ID is embedded in the branch name when the PR is first created, then extracted when processing PR comments to maintain conversation continuity.

GitHub Pull Request Thread ID Extraction Flow:
```mermaid
graph TB
    subgraph "PR_Comment_Event"
        Event["GitHub Webhook<br/>pull_request_review_comment"]
        Payload["Webhook Payload"]
        Event --> Payload
    end
    
    subgraph "Branch_Name_Extraction"
        BranchField["Pull Request<br/>head.ref field"]
        BranchName["Branch Name<br/>e.g., 'fix-bug-a1b2c3d4-...'"]
        
        Payload --> BranchField
        BranchField --> BranchName
    end
    
    subgraph "Thread_ID_Extraction"
        Regex["Regex Pattern<br/>UUID pattern"]
        Match["Extract UUID<br/>from branch name"]
        ThreadID["Thread ID<br/>e.g., 'a1b2c3d4-e5f6-7890-...'"]
        
        BranchName --> Regex
        Regex --> Match
        Match --> ThreadID
    end
```

The `get_thread_id_from_branch()` function extracts the thread ID using a UUID regex [agent/utils/github_comments.py:51-57](). This allows the agent to resume the exact same LangGraph thread and sandbox environment that was used to create the PR. If a PR comment is made, the system first tries to find the thread ID from the branch name; if no ID is found, it falls back to generating one from the PR's issue ID [agent/utils/github_comments.py:49-57]().

**Sources:** [agent/utils/github_comments.py:51-57]()

---

## Thread ID Usage Flow

The thread ID is the central identifier used to bridge Natural Language events to Code Entities like sandboxes and LangGraph states.

System Component Interaction:
```mermaid
sequenceDiagram
    participant Webhook as "webapp.py<br/>(Webhook Handler)"
    participant Generator as "webapp.py<br/>(generate_thread_id_*)"
    participant LG as "LangGraphClient<br/>(langgraph_sdk)"
    participant Queue as "queue_message_for_thread<br/>(thread_ops.py)"
    
    Webhook->>Generator: Input Data (Issue ID / Slack TS)
    Generator-->>Webhook: thread_id (UUID)
    
    alt Thread is Active
        Webhook->>Queue: Add message to queue
    else Thread Idle
        Webhook->>LG: runs.create(thread_id, ...)
    end
```

### Key Data Mappings

| Entity | Purpose | Code Reference |
| :--- | :--- | :--- |
| **LangGraph Thread** | Persistent storage of conversation state and checkpoints | [agent/webapp.py:17-18]() |
| **Thread Metadata** | Storage of `sandbox_id`, `repo_dir`, and encrypted tokens | [agent/utils/auth.py:36-37](), [agent/reviewer_findings.py:32]() |
| **Message Queue** | Handles concurrent events on the same `thread_id` | [agent/utils/thread_ops.py:90]() |

**Sources:** [agent/webapp.py:17-18](), [agent/utils/thread_ops.py:90](), [agent/utils/auth.py:36-37]()

---

## Implementation Comparison

| Source | Algorithm | Input Namespace | Implementation Method | Reversible? |
| :--- | :--- | :--- | :--- | :--- |
| **Linear** | SHA-256 | `linear-issue:` | Manual string formatting [agent/webapp.py:240-245]() | No |
| **GitHub Issue** | SHA-256 | `github-issue:` | Manual string formatting [agent/webapp.py:255-261]() | No |
| **Slack** | MD5 | `channel:ts` | `uuid.UUID(hex=...)` [agent/webapp.py:264-268]() | No |
| **GitHub PR** | N/A | Branch name | Regex extraction [agent/utils/github_comments.py:51-57]() | Yes |

**Sources:** [agent/webapp.py:239-268](), [agent/utils/github_comments.py:51-57]()

---

# Page: Message Queueing

# Message Queueing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/_patch_messages_reducer.py](agent/_patch_messages_reducer.py)
- [agent/dashboard/message_adapter.py](agent/dashboard/message_adapter.py)
- [agent/dashboard/thread_api.py](agent/dashboard/thread_api.py)
- [agent/middleware/__init__.py](agent/middleware/__init__.py)
- [agent/middleware/ensure_no_empty_msg.py](agent/middleware/ensure_no_empty_msg.py)
- [agent/middleware/notify_step_limit.py](agent/middleware/notify_step_limit.py)
- [agent/middleware/sanitize_tool_inputs.py](agent/middleware/sanitize_tool_inputs.py)
- [agent/review_style_analyzer.py](agent/review_style_analyzer.py)
- [agent/utils/thread_ops.py](agent/utils/thread_ops.py)
- [tests/test_ensure_no_empty_msg.py](tests/test_ensure_no_empty_msg.py)
- [tests/test_notify_step_limit_middleware.py](tests/test_notify_step_limit_middleware.py)
- [tests/test_sanitize_tool_inputs.py](tests/test_sanitize_tool_inputs.py)

</details>



This page documents the message queueing system that handles concurrent events on the same thread, ensuring that user instructions are not lost when multiple webhooks arrive while an agent is already processing. It specifically details the implementation of thread status detection, storage in the LangGraph Store, and the `check_message_queue_before_model` middleware.

---

## Overview

Open SWE's message queueing system solves a critical concurrency problem: when a user comments on a Linear issue or Slack thread while the agent is still processing a previous message, the system must preserve that input rather than starting a conflicting parallel run or dropping the message entirely.

The solution consists of three components:

1.  **Thread status detection**: Checking if a thread is currently executing via LangGraph's thread status API [agent/utils/thread_ops.py:24-37]().
2.  **LangGraph Store persistence**: Queueing pending messages in the store, namespaced to the thread [agent/utils/thread_ops.py:40-68]().
3.  **Middleware injection**: The `check_message_queue_before_model` middleware retrieves and injects queued messages before each LLM call [agent/middleware/__init__.py:1-21]().

This enables **real-time guidance**: users can post clarifications, corrections, or additional requirements mid-execution, and the agent incorporates them at its next decision point.

**Sources:**
- [agent/utils/thread_ops.py:24-68]()
- [agent/middleware/__init__.py:1-21]()

---

## Thread Status Detection

### The `is_thread_active()` Function

Before creating a new LangGraph run, the webhook handler calls `is_thread_active(thread_id)` to determine if the thread already has an active run.

**Thread Status Logic Flow**

```mermaid
graph TB
    subgraph "Thread Status Detection [agent/utils/thread_ops.py]"
        Webhook["Webhook Event<br/>(Linear/Slack/GitHub)"]
        GetClient["langgraph_sdk.get_client()"]
        GetThread["client.threads.get(thread_id)"]
        CheckField["thread.get('status')"]
        
        IsBusy{"status == 'busy'?"}
        Queue["queue_message_for_thread()"]
        CreateRun["client.runs.create()"]
    end
    
    Webhook --> GetClient
    GetClient --> GetThread
    GetThread --> CheckField
    CheckField --> IsBusy
    IsBusy -->|Yes| Queue
    IsBusy -->|No| CreateRun
    
    Queue --> Return["Return: queued"]
    CreateRun --> Return2["Return: run created"]
```

The function fetches the thread metadata from LangGraph and examines its `status` field:
- **`"busy"`**: An active run is in progress; new messages should be queued [agent/utils/thread_ops.py:30-30]().
- **`"idle"`**: The thread is available; create a new run immediately [agent/utils/thread_ops.py:28-28]().
- **Error**: If thread fetch fails, it assumes the thread is not active and returns `False` [agent/utils/thread_ops.py:31-37]().

**Sources:**
- [agent/utils/thread_ops.py:24-37]()

---

## Message Queue Storage

### Storage Mechanism

Queued messages are stored in the **LangGraph Store**, a key-value store scoped to the thread. The system uses a consistent namespace and key structure to ensure messages are isolated per thread [agent/utils/thread_ops.py:46-47]().

| Component | Value | Purpose |
| :--- | :--- | :--- |
| **Namespace** | `("queue", thread_id)` | Isolates queued messages to the specific thread |
| **Key** | `"pending_messages"` | Single key holding all queued messages for that thread |
| **Value** | `{"messages": [...]}` | Array of message objects in FIFO order |

### The `queue_message_for_thread()` Function

This function appends a new message to the queue. It retrieves existing queued messages via `client.store.get_item`, appends the new one, and writes the updated list back using `client.store.put_item` [agent/utils/thread_ops.py:52-59]().

**Queue Storage Architecture**

```mermaid
graph TB
    subgraph "LangGraph Store Architecture"
        Store["langgraph_sdk.client.LangGraphClient.store"]
        
        subgraph "Thread Queue Namespace"
            NS["Namespace: ('queue', thread_id)"]
            Key["Key: 'pending_messages'"]
            Val["Value: { 'messages': [ ... ] }"]
            NS --> Key
            Key --> Val
        end
        
        Store --> NS
    end
    
    subgraph "Code Entities [agent/utils/thread_ops.py]"
        Func["queue_message_for_thread()"]
        GetItem["store.get_item()"]
        PutItem["store.put_item()"]
    end
    
    Func --> GetItem
    GetItem -.->|Read| Val
    Func --> PutItem
    PutItem -.->|Write| Val
```

**Sources:**
- [agent/utils/thread_ops.py:40-69]()

---

## Queue Processing via Middleware

### The `check_message_queue_before_model` Middleware

The queued messages are retrieved and injected into the agent's state by the `check_message_queue_before_model` middleware. This middleware is registered as a `@before_model` hook [agent/middleware/__init__.py:1-18]().

**Middleware Execution Sequence**

```mermaid
sequenceDiagram
    participant Agent as "Agent Loop (LangGraph)"
    participant MW as "check_message_queue_before_model"
    participant Store as "LangGraph Store"
    participant LLM as "Language Model"
    
    Agent->>MW: Trigger @before_model hook
    MW->>Store: store.get_item(("queue", thread_id), "pending_messages")
    Store-->>MW: Return list of queued messages
    
    Note over MW: For each message, append to agent state 'messages'
    
    MW->>Store: store.delete_item(("queue", thread_id), "pending_messages")
    Store-->>MW: Queue cleared
    
    MW->>LLM: Proceed to LLM with updated context
```

The system ensures that messages are only processed once by clearing the queue from the Store after they have been successfully injected into the `AgentState`.

**Sources:**
- [agent/middleware/__init__.py:1-21]()
- [agent/middleware/check_message_queue.py:1-20]() (Note: file exists but contents truncated in prompt; implied by `__init__.py` and `thread_ops.py`)

---

## Related Middleware: State Sanitization

While the queueing system handles incoming messages, other middleware components ensure the agent's state remains valid during these concurrent or sequential turns:

*   **`SanitizeToolInputsMiddleware`**: Coerces malformed integer fields (like `offset` or `limit` in `read_file`) produced by the LLM to prevent `ValidationError` loops [agent/middleware/sanitize_tool_inputs.py:54-81]().
*   **`ensure_no_empty_msg`**: Prevents the agent from terminating without calling a tool or messaging the user. If an AI message is empty and no user-facing tool was called, it injects a `no_op` tool call to prompt the agent to continue [agent/middleware/ensure_no_empty_msg.py:57-101]().
*   **`notify_step_limit_reached`**: Monitors the agent's exit status. If the agent hits its step limit, this middleware posts a notification to the Slack thread so the user is aware of the interruption [agent/middleware/notify_step_limit.py:37-88]().

**Sources:**
- [agent/middleware/sanitize_tool_inputs.py:54-81]()
- [agent/middleware/ensure_no_empty_msg.py:57-101]()
- [agent/middleware/notify_step_limit.py:37-88]()

---

## Summary of Key Functions

| Function | File | Purpose |
| :--- | :--- | :--- |
| `is_thread_active` | [agent/utils/thread_ops.py:24]() | Checks if a thread status is `"busy"` in LangGraph. |
| `queue_message_for_thread` | [agent/utils/thread_ops.py:40]() | Appends message content to the thread's queue in LangGraph Store. |
| `check_message_queue_before_model` | [agent/middleware/check_message_queue.py:1]() | Middleware that drains the queue and updates agent state before LLM calls. |

**Sources:**
- [agent/utils/thread_ops.py:24-69]()
- [agent/middleware/__init__.py:1-21]()

---

# Page: Thread Metadata Storage

# Thread Metadata Storage

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/_patch_messages_reducer.py](agent/_patch_messages_reducer.py)
- [agent/dashboard/message_adapter.py](agent/dashboard/message_adapter.py)
- [agent/dashboard/thread_api.py](agent/dashboard/thread_api.py)
- [agent/integrations/langsmith.py](agent/integrations/langsmith.py)
- [agent/review_style_analyzer.py](agent/review_style_analyzer.py)
- [agent/server.py](agent/server.py)
- [agent/tools/__init__.py](agent/tools/__init__.py)
- [agent/utils/thread_ops.py](agent/utils/thread_ops.py)
- [pyproject.toml](pyproject.toml)
- [uv.lock](uv.lock)

</details>



Thread metadata storage provides a persistent key-value store for each LangGraph thread, enabling state to be preserved across multiple agent invocations. This system stores critical data like sandbox identifiers, encrypted authentication tokens, and repository configurations, allowing the agent to reuse resources and maintain context when processing follow-up messages.

## Overview

Thread metadata is managed via the LangGraph SDK's `threads.update()` API, which persists arbitrary key-value data associated with a `thread_id`. This metadata survives across independent agent runs, enabling resource reuse and stateful conversations between the user and the agent.

**Sources:** [agent/server.py:195-198](), [agent/integrations/langsmith.py:173-191]()

## Metadata Schema

The following fields are frequently persisted or retrieved from thread metadata to maintain agent state:

| Field | Type | Purpose | Set By |
|-------|------|---------|--------|
| `sandbox_id` | `str` | Unique identifier of the sandbox backend (e.g., LangSmith box ID) | [agent/integrations/langsmith.py:188-191]() |
| `github_login` | `str` | The GitHub username of the user who initiated the thread | [agent/dashboard/thread_api.py:90-91]() |
| `source` | `str` | Origin of the thread (e.g., "dashboard", "slack", "linear") | [agent/dashboard/thread_api.py:98-99]() |
| `latest_run_status` | `str` | Status of the most recent execution (e.g., "success", "failed") | [agent/dashboard/thread_api.py:137-141]() |
| `repo_owner` | `str` | GitHub organization or user owning the target repository | [agent/dashboard/thread_api.py:103-104]() |
| `repo_name` | `str` | Name of the target repository | [agent/dashboard/thread_api.py:104-105]() |

### Special Sentinel Values

The `sandbox_id` field uses a specific sentinel value during the provisioning phase:

```python
SANDBOX_CREATING = "__creating__"
```

This sentinel prevents concurrent runs or race conditions from attempting to create duplicate sandboxes for the same thread while a creation task is already in progress.

**Sources:** [agent/server.py:85-85](), [agent/server.py:197-197]()

## Storage Mechanism

Thread metadata is persisted via the `langgraph_sdk.get_client()` instance, which communicates with the LangGraph server's persistence layer.

### Write Operations

The `_update_thread_sandbox_metadata` function handles the asynchronous update of thread state by extracting the `thread_id` from the current `RunnableConfig`.

```mermaid
graph TB
    subgraph "Natural Language Space"
        UserAction["User triggers Agent"]
    end

    subgraph "Code Entity Space"
        UpdateCall["_update_thread_sandbox_metadata(sandbox_id)"]
        GetConfig["langgraph.config.get_config()"]
        LGClient["langgraph_sdk.get_client()"]
        ThreadUpdate["client.threads.update()"]
        
        UpdateCall --> GetConfig
        GetConfig --> ThreadID["Extract thread_id"]
        ThreadID --> LGClient
        LGClient --> ThreadUpdate
        ThreadUpdate --> Persisted["Metadata: {'sandbox_id': ...}"]
    end
    
    UserAction -.-> UpdateCall
```

**Sources:** [agent/integrations/langsmith.py:173-191]()

### Read Operations

The system retrieves the `sandbox_id` from metadata to determine if it can reconnect to an existing environment instead of provisioning a new one.

```mermaid
graph TB
    subgraph "Natural Language Space"
        Inquiry["Agent checks for existing environment"]
    end

    subgraph "Code Entity Space"
        GetID["get_sandbox_id_from_metadata(thread_id)"]
        LG_Client["langgraph_client()"]
        ThreadGet["client.threads.get(thread_id)"]
        
        GetID --> LG_Client
        LG_Client --> ThreadGet
        ThreadGet --> Extract["metadata.get('sandbox_id')"]
    end
    
    Inquiry -.-> GetID
```

**Sources:** [agent/utils/sandbox_state.py:91-91]()

## Lifecycle Operations

### Sandbox Persistence and Reconnection

The `sandbox_id` field tracks the lifecycle of sandbox backends. For LangSmith sandboxes, the ID is captured immediately upon creation. If a run fails or the agent is re-invoked, the `sandbox_id` allows the system to refresh credentials or recreate the sandbox if it has become stale.

**Sources:** [agent/server.py:162-177](), [agent/integrations/langsmith.py:126-170]()

### Token Persistence

Encrypted GitHub tokens are persisted in thread metadata to ensure the agent can perform authenticated `git` operations (like `push` or `pull`) throughout the duration of a multi-turn conversation.

```python
async def _persist_dashboard_github_token(thread_id: str, login: str) -> None:
    token = await get_valid_access_token(login)
    # ... logic to encrypt and store
    await persist_encrypted_github_token(thread_id, token, expires_at=expires_at)
```

**Sources:** [agent/dashboard/thread_api.py:76-86](), [agent/utils/auth.py:17-17]()

## Concurrency and Re-use

### In-Memory Cache vs. Persistent Metadata

Thread metadata works in conjunction with the in-memory `SANDBOX_BACKENDS` dictionary. While the metadata ensures the `sandbox_id` survives server restarts, the `SANDBOX_BACKENDS` cache provides immediate access to active `SandboxBackendProtocol` instances during a single execution session.

**Sources:** [agent/utils/sandbox_state.py:90-94]()

### GitHub Proxy Configuration

For LangSmith sandboxes, metadata storage of the `sandbox_id` is essential for the `_refresh_github_proxy` logic. This function uses the persisted ID to inject a fresh `installation_token` into the sandbox's network proxy rules, allowing the agent to interact with GitHub without writing credentials to the sandbox disk.

**Sources:** [agent/server.py:142-160](), [agent/integrations/langsmith.py:98-124]()

---

# Page: Authentication and Security

# Authentication and Security

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [SECURITY.md](SECURITY.md)
- [agent/utils/auth.py](agent/utils/auth.py)
- [agent/utils/github_app.py](agent/utils/github_app.py)
- [agent/utils/github_comments.py](agent/utils/github_comments.py)
- [agent/utils/github_token.py](agent/utils/github_token.py)
- [tests/test_github_token_ttl.py](tests/test_github_token_ttl.py)
- [tests/test_proxy_auth.py](tests/test_proxy_auth.py)

</details>



Open SWE implements a multi-layered security architecture that handles GitHub authentication, token encryption, and sandbox security. The system supports two primary modes: a per-user OAuth mode integrated with LangSmith and a "bot-token-only" mode for simpler deployments.

This is a **PARENT** page. For deep technical details, see the following child pages:
- **[GitHub Token Resolution](#7.1)** — Detailed flow of `resolve_github_token`, email mapping, and LangSmith Host API integration.
- **[Bot Token Only Mode](#7.2)** — Configuration and behavior when per-user OAuth is disabled.
- **[Token Encryption and Storage](#7.3)** — Technical implementation of Fernet encryption and thread metadata persistence.
- **[Security Policy](#7.4)** — Official security policy and vulnerability reporting procedures.

---

## Architecture Overview

The authentication system bridges "Natural Language Space" (identifying users by Slack/Linear emails) to "Code Entity Space" (GitHub tokens and API calls).

### Authentication Flow Diagram
This diagram shows how the system resolves a user's identity from a webhook event into a usable GitHub credential.

```mermaid
graph TD
    subgraph "Natural Language Space (Triggers)"
        Slack["Slack Event<br/>(user_id)"]
        Linear["Linear Event<br/>(email)"]
        GitHubEvent["GitHub Webhook<br/>(sender.login)"]
    end

    subgraph "Identity Resolution (agent/utils/auth.py)"
        Map["GITHUB_USER_EMAIL_MAP"]
        LS_Lookup["get_ls_user_id_from_email()"]
    end

    subgraph "Code Entity Space (Credentials)"
        TokenFunc["resolve_github_token()"]
        OAuth["get_github_token_for_user()"]
        AppToken["get_github_app_installation_token()"]
        Encryption["encrypt_token()"]
    end

    Slack --> Map
    Linear --> LS_Lookup
    GitHubEvent --> AppToken
    
    Map --> LS_Lookup
    LS_Lookup --> TokenFunc
    TokenFunc --> OAuth
    OAuth --> Encryption
    AppToken --> Encryption
```
**Sources:** [agent/utils/auth.py:138-182](), [agent/utils/github_user_email_map.py:1-10](), [agent/utils/github_app.py:31-67]()

---

## Token Management

Open SWE prioritizes secure handling of GitHub tokens to prevent leakage while ensuring the agent has sufficient permissions to perform git operations.

### GitHub Token Resolution
The system attempts to resolve a GitHub token for the specific user who triggered the agent. It uses the user's email to find their LangSmith user ID via `get_ls_user_id_from_email` [agent/utils/auth.py:96-122]() and then fetches an OAuth token via the LangSmith Host API using `get_github_token_for_user` [agent/utils/auth.py:138-182](). If no user token is available, it falls back to a GitHub App installation token. For details, see [GitHub Token Resolution](#7.1).

### Encryption and Persistence
To avoid repeated OAuth flows, tokens are encrypted using the Fernet algorithm and stored in the LangGraph thread metadata under the key `github_token_encrypted` [agent/utils/github_token.py:18-19](). The system also tracks `github_token_expires_at` to proactively re-authenticate before tokens expire [agent/utils/github_token.py:45-78](). For details, see [Token Encryption and Storage](#7.3).

**Sources:** [agent/utils/auth.py:138-182](), [agent/utils/github_token.py:18-100](), [agent/encryption.py:1-30]()

---

## Sandbox and Tool Security

Security extends beyond authentication to the execution environment. Open SWE implements safeguards to prevent the agent from performing SSRF (Server-Side Request Forgery) or accessing internal resources.

### GitHub Proxy Configuration
For LangSmith-hosted sandboxes, Open SWE configures a secure GitHub proxy. The function `_configure_github_proxy` [agent/integrations/langsmith.py:11-13]() (tested in [tests/test_proxy_auth.py:14-61]()) injects GitHub credentials into the sandbox environment via opaque headers. This ensures that the agent's git operations within the sandbox are authenticated without exposing raw tokens to the agent's process space.

```mermaid
sequenceDiagram
    participant Srv as "agent/server.py"
    participant LS as "LangSmith API"
    participant Box as "Sandbox Environment"

    Srv->>Srv: get_github_app_installation_token()
    Srv->>LS: PATCH /v2/sandboxes/boxes/{id} (proxy_config)
    Note over LS: Rules for api.github.com<br/>and github.com
    LS-->>Srv: 200 OK
    Srv->>Box: Execute Git Command
    Box->>LS: Outbound Request
    LS->>GitHub: Authenticated Request (Opaque Header)
```
**Sources:** [tests/test_proxy_auth.py:17-61](), [agent/server.py:125-145]()

---

## Operational Security Policies

### Bot-Token-Only Mode
In environments where per-user OAuth is not configured (missing `X_SERVICE_AUTH_JWT_SECRET` and `USER_ID_API_KEY_MAP`), Open SWE defaults to "Bot-Token-Only" mode. This is checked via `is_bot_token_only_mode()` [agent/utils/auth.py:44-52](). In this mode, all operations are performed using the GitHub App's installation token. For details, see [Bot Token Only Mode](#7.2).

### Webhook Verification
All incoming GitHub webhooks are verified using the `X-Hub-Signature-256` header and a configured `GITHUB_WEBHOOK_SECRET` via the `verify_github_signature` function [agent/utils/github_comments.py:52-68]().

### Security Policy
Official security concerns and vulnerability reports should be directed to the contact information provided in the security policy. For details, see [Security Policy](#7.4).

**Sources:** [agent/utils/auth.py:44-52](), [agent/utils/github_comments.py:52-68](), [SECURITY.md:1-4]()

---

# Page: GitHub Token Resolution

# GitHub Token Resolution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/dashboard/oauth.py](agent/dashboard/oauth.py)
- [agent/dashboard/review_style_jobs.py](agent/dashboard/review_style_jobs.py)
- [agent/dashboard/review_styles.py](agent/dashboard/review_styles.py)
- [agent/utils/auth.py](agent/utils/auth.py)
- [agent/utils/github_app.py](agent/utils/github_app.py)
- [agent/utils/github_comments.py](agent/utils/github_comments.py)
- [agent/utils/github_token.py](agent/utils/github_token.py)
- [tests/test_github_oauth_refresh.py](tests/test_github_oauth_refresh.py)
- [tests/test_github_token_ttl.py](tests/test_github_token_ttl.py)
- [tests/test_proxy_auth.py](tests/test_proxy_auth.py)
- [tests/test_review_style_sync.py](tests/test_review_style_sync.py)
- [ui/src/components/ReviewStylesPanel.tsx](ui/src/components/ReviewStylesPanel.tsx)

</details>



## Purpose and Scope

This document describes the GitHub token resolution system in Open SWE, which determines which GitHub token to use for git operations (cloning repos, pushing branches, creating PRs). The system supports multiple resolution strategies depending on the invocation source (GitHub, Linear, Slack) and deployment mode, and includes mechanisms for token rotation, expiry handling, and invalidation.

The token resolution system is primarily implemented in [agent/utils/auth.py]() and is called during agent initialization in `get_agent()` [agent/server.py:254](). It handles mapping external identities (Slack emails, Linear emails, GitHub logins) to GitHub OAuth tokens or GitHub App installation tokens.

---

## Token Resolution Architecture

The GitHub token resolution system is orchestrated by `resolve_github_token()` in [agent/utils/auth.py:360-398](). It acts as a router that selects a resolution strategy based on environment configuration and the event source.

**Token Resolution Flow**

```mermaid
graph TB
    GetAgent["get_agent()<br/>server.py:254"]
    ResolveToken["resolve_github_token()<br/>auth.py:360-398"]
    
    BotModeCheck{"is_bot_token_only_mode()?<br/>auth.py:44-52"}
    
    BotMode["_resolve_bot_installation_token()<br/>auth.py:344-357"]
    GetAppToken["get_github_app_installation_token()<br/>github_app.py"]
    PersistBot["persist_encrypted_github_token()<br/>auth.py:268-275"]
    
    SourceCheck{"config['source']"}
    
    GitHubSource["GitHub Source"]
    CachedCheck["get_github_token_from_thread()<br/>github_token.py"]
    EmailMap["GITHUB_USER_EMAIL_MAP<br/>github_user_email_map.py"]
    
    LinearSlackSource["Linear/Slack Source"]
    UserEmail["config['user_email']"]
    
    SaveFromEmail["save_encrypted_token_from_email()<br/>auth.py:278-341"]
    ResolveFromEmail["resolve_github_token_from_email()<br/>auth.py:175-200"]
    
    ReturnToken["Return:<br/>(github_token, encrypted)"]
    
    GetAgent --> ResolveToken
    ResolveToken --> BotModeCheck
    
    BotModeCheck -->|"true"| BotMode
    BotMode --> GetAppToken
    GetAppToken --> PersistBot
    PersistBot --> ReturnToken
    
    BotModeCheck -->|"false"| SourceCheck
    
    SourceCheck -->|"github"| GitHubSource
    GitHubSource --> CachedCheck
    CachedCheck -->|"cache miss"| EmailMap
    EmailMap --> SaveFromEmail
    CachedCheck -->|"cache hit"| ReturnToken
    
    SourceCheck -->|"linear/slack"| LinearSlackSource
    LinearSlackSource --> UserEmail
    UserEmail --> SaveFromEmail
    
    SaveFromEmail --> ResolveFromEmail
    ResolveFromEmail --> ReturnToken
```

**Sources:** [agent/server.py:254](), [agent/utils/auth.py:360-398](), [agent/utils/github_token.py:1-20]()

The `resolve_github_token()` function:
1. Validates if bot-token-only mode is required [agent/utils/auth.py:365]().
2. Routes GitHub-native events to `GITHUB_USER_EMAIL_MAP` lookups [agent/utils/auth.py:390]().
3. Routes Linear/Slack events to email-based OAuth resolution [agent/utils/auth.py:382]().
4. Returns a tuple of `(github_token, new_encrypted)` to be used for repository setup [agent/server.py:255]().

---

## Bot-Token-Only Mode

Bot-token-only mode is a fallback state where Open SWE uses a GitHub App installation token for all operations instead of per-user OAuth tokens. This is active when the system is deployed but lacks the specific secrets needed to communicate with the LangSmith Host API for user-level auth.

**Bot-Token-Only Mode Detection**

```mermaid
graph TB
    Check["is_bot_token_only_mode()<br/>auth.py:44-52"]
    
    LangSmithKey{"LANGSMITH_API_KEY_PROD<br/>is set?"}
    
    ServiceJWT{"X_SERVICE_AUTH_JWT_SECRET<br/>is set?"}
    
    UserAPIMap{"USER_ID_API_KEY_MAP<br/>is set?"}
    
    BotMode["Return True<br/>(Bot-token-only mode)"]
    
    NormalMode["Return False<br/>(Per-user OAuth mode)"]
    
    Check --> LangSmithKey
    LangSmithKey -->|"no"| NormalMode
    LangSmithKey -->|"yes"| ServiceJWT
    
    ServiceJWT -->|"yes"| NormalMode
    ServiceJWT -->|"no"| UserAPIMap
    
    UserAPIMap -->|"yes"| NormalMode
    UserAPIMap -->|"no"| BotMode
```

**Sources:** [agent/utils/auth.py:44-52]()

The logic checks `LANGSMITH_API_KEY_PROD` [agent/utils/auth.py:27](), `X_SERVICE_AUTH_JWT_SECRET` [agent/utils/auth.py:31](), and `USER_ID_API_KEY_MAP` [agent/utils/auth.py:32](). If the system is "deployed" but cannot generate service keys, it defaults to the GitHub App's own token.

**Bot Mode Token Resolution**
When `_resolve_bot_installation_token()` is called [agent/utils/auth.py:344](), it invokes `get_github_app_installation_token()` [agent/utils/auth.py:17](). This function (defined in `github_app.py`) generates a JWT signed by the App's private key [agent/utils/github_app.py:19-28]() to request a short-lived installation access token from GitHub [agent/utils/github_app.py:54-64]().

---

## Email-Based Token Resolution

For Linear and Slack, the system uses the user's platform email to find their LangSmith identity and subsequently their GitHub OAuth token.

**Email to GitHub Token Flow**

```mermaid
sequenceDiagram
    participant Auth as "resolve_github_token()<br/>auth.py:360-398"
    participant SaveEmail as "save_encrypted_token_from_email()<br/>auth.py:278-341"
    participant ResolveEmail as "resolve_github_token_from_email()<br/>auth.py:175-200"
    participant LSUser as "get_ls_user_id_from_email()<br/>auth.py:96-122"
    participant LSAPI as "LangSmith API<br/>/api/v1/workspaces/current/members/active"
    participant GetToken as "get_github_token_for_user()<br/>auth.py:125-172"
    participant HostAPI as "LangSmith Host API<br/>/v2/auth/authenticate"
    participant Persist as "persist_encrypted_github_token()<br/>auth.py:268-275"
    
    Auth->>SaveEmail: "user_email from config"
    SaveEmail->>ResolveEmail: "email"
    ResolveEmail->>LSUser: "email"
    LSUser->>LSAPI: "GET ?emails=[email]"
    LSAPI-->>LSUser: "{ls_user_id, tenant_id}"
    
    ResolveEmail->>GetToken: "ls_user_id, tenant_id"
    GetToken->>GetToken: "get_secret_key_for_user()"
    GetToken->>HostAPI: "POST /v2/auth/authenticate<br/>{provider, scopes, user_id}"
    
    alt OAuth Token Available
        HostAPI-->>GetToken: "{token: '...'}"
        GetToken-->>ResolveEmail: "{token}"
    else OAuth Required
        HostAPI-->>GetToken: "{auth_url: 'https://...'}"
        GetToken-->>ResolveEmail: "{auth_url}"
    else Error
        HostAPI-->>GetToken: "HTTP Error"
        GetToken-->>ResolveEmail: "{error: '...'}"
    end
    
    ResolveEmail-->>SaveEmail: "token or auth_url or error"
    
    alt Token Received
        SaveEmail->>Persist: "thread_id, token"
        Persist-->>SaveEmail: "encrypted"
        SaveEmail-->>Auth: "(token, encrypted)"
    else Auth URL Received
        SaveEmail->>SaveEmail: "leave_failure_comment()<br/>with auth_url"
        SaveEmail-->>Auth: "ValueError"
    end
```

**Sources:** [agent/utils/auth.py:96-172](), [agent/utils/auth.py:175-200](), [agent/utils/auth.py:278-341]()

### LangSmith User Lookup
`get_ls_user_id_from_email()` [agent/utils/auth.py:96-122]() performs an authenticated GET request to the LangSmith `members/active` endpoint [agent/utils/auth.py:102](). It requires `LANGSMITH_API_KEY` to be set in the environment [agent/utils/auth.py:108]().

### GitHub OAuth Token Retrieval
`get_github_token_for_user()` [agent/utils/auth.py:125-172]() uses a service JWT generated by `get_secret_key_for_user()` [agent/utils/auth.py:79-93]() to call the LangSmith Host API. The Host API endpoint `/v2/auth/authenticate` [agent/utils/auth.py:151]() returns either the existing token or an `auth_url` if the user needs to re-authorize. It also extracts the token expiry if provided in the response [agent/utils/auth.py:125-135]().

---

## GitHub Source Token Resolution

When triggered from GitHub (e.g., a comment on an issue), the system only knows the user's GitHub login (handle). It uses a static mapping to find the corresponding email for LangSmith lookup.

### GitHub User Email Map
The `GITHUB_USER_EMAIL_MAP` in [agent/utils/github_user_email_map.py:7-128]() is a dictionary mapping GitHub handles to email addresses.

| GitHub Login | Mapped Email |
|--------------|--------------|
| `aran-yogesh` | `yogesh.mahendran@langchain.dev` |
| `hwchase17` | `harrison@langchain.dev` |
| `sydney-runkle` | `sydney@langchain.dev` |

**Sources:** [agent/utils/github_user_email_map.py:7-128]()

### Resolution Logic
In `resolve_github_token()` [agent/utils/auth.py:360](), if the source is `github`:
1. It first checks for a cached token in the thread metadata using `get_github_token_from_thread()` [agent/utils/auth.py:387]().
2. If not found, it retrieves the `github_login` from the configuration [agent/utils/auth.py:389]().
3. It looks up the login in `GITHUB_USER_EMAIL_MAP` [agent/utils/github_user_email_map.py:15]().
4. If a mapping exists, it proceeds with `save_encrypted_token_from_email()` [agent/utils/auth.py:394]().

---

## Token Lifecycle and Expiry

Tokens resolved by the system include expiry management to prevent agent runs from failing midway due to token revocation.

### Expiry Detection
The utility `_is_expired()` [agent/utils/github_token.py:45-79]() checks if a token's `expires_at` timestamp is within a 60-second skew window [agent/utils/github_token.py:28](). It supports ISO-8601 strings and Unix timestamps [agent/utils/github_token.py:56-70]().

### Dashboard Token Refresh
The dashboard backend includes logic to automatically rotate user access tokens using refresh tokens via `refresh_user_access_token()` [agent/dashboard/oauth.py:185-197](). The `get_valid_access_token()` function in the profile system checks for near-expiry and triggers a refresh before returning a token to the frontend [agent/dashboard/profiles.py]().

---

## Token Encryption and Persistence

Once a token is retrieved, it is never stored in plaintext in the thread metadata. It is encrypted using a Fernet key [agent/encryption.py:16]().

**Encryption and Storage Flow**

```mermaid
graph TB
    Token["Raw GitHub Token"]
    Persist["persist_encrypted_github_token()<br/>auth.py:268-275"]
    Encrypt["encrypt_token()<br/>encryption.py"]
    UpdateThread["client.threads.update()<br/>auth.py:271"]
    
    Token --> Persist
    Persist --> Encrypt
    Encrypt --> UpdateThread
```

**Sources:** [agent/utils/auth.py:268-275](), [agent/encryption.py:16]()

The `persist_encrypted_github_token` function updates the LangGraph thread metadata with the key `github_token_encrypted` [agent/utils/auth.py:273](). Subsequent runs on the same thread can then retrieve and decrypt this token using `get_github_token_from_thread()` [agent/utils/github_token.py:102-134](), which returns the decrypted token only if it hasn't expired [agent/utils/github_token.py:126-128]().

---

## Authentication Failure and Invalidation

If a token cannot be resolved (e.g., the user is not in the email map or has not authorized OAuth), `leave_failure_comment()` is triggered [agent/utils/auth.py:203-265]().

### Token Invalidation
If a downstream GitHub API call returns a `401 Unauthorized` error, the system raises a `GitHubAuthError` [agent/utils/github_token.py:22-23](). Callers can then invoke `invalidate_cached_github_token()` [agent/utils/github_token.py:137-154]() to clear the stale encrypted token from thread metadata, forcing a fresh resolution on the next attempt.

### Failure Notifications
`leave_failure_comment()` handles:
- **Linear**: Posting a comment on the issue using `comment_on_linear_issue()` [agent/utils/auth.py:219]().
- **Slack**: Attempting an ephemeral message to the user [agent/utils/auth.py:236]() or a thread reply [agent/utils/auth.py:251]().
- **GitHub**: Logging a warning, as the system lacks the token required to post a comment back to GitHub [agent/utils/auth.py:264]().

**Sources:** [agent/utils/auth.py:203-265](), [agent/utils/github_token.py:137-154](), [agent/utils/linear.py:20](), [agent/utils/slack.py:21]()

---

# Page: Bot Token Only Mode

# Bot Token Only Mode

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/utils/auth.py](agent/utils/auth.py)
- [agent/utils/github_app.py](agent/utils/github_app.py)
- [agent/utils/github_comments.py](agent/utils/github_comments.py)
- [agent/utils/github_token.py](agent/utils/github_token.py)
- [agent/webapp.py](agent/webapp.py)
- [tests/test_github_issue_webhook.py](tests/test_github_issue_webhook.py)
- [tests/test_github_token_ttl.py](tests/test_github_token_ttl.py)
- [tests/test_proxy_auth.py](tests/test_proxy_auth.py)

</details>



Bot token only mode is a simplified authentication configuration where Open SWE uses the GitHub App installation token for all git operations instead of per-user OAuth tokens. This mode activates automatically when the deployment environment is detected but per-user OAuth resolution is not configured.

For information about the full OAuth-based authentication flow, see [7.1 GitHub Token Resolution](). For details on how tokens are encrypted and stored, see [7.3 Token Encryption and Storage]().

---

## Overview

Bot token only mode provides a streamlined deployment path that bypasses the complexity of per-user OAuth token management. In this mode:

- All git operations (clone, pull, push, PR creation) use a single shared GitHub App installation token.
- PRs and commits appear under the GitHub App's bot identity rather than individual user identities.
- No LangSmith OAuth provider configuration is required.
- No user email to LangSmith user ID mapping is needed.

This mode is particularly useful for testing, internal-only deployments, or simplified setups where the GitHub App's permissions are sufficient.

**Sources:** [agent/utils/auth.py:44-52](), [agent/webapp.py:35-38]()

---

## Activation Conditions

Bot token only mode is detected and activated by the `is_bot_token_only_mode()` function based on environment variable configuration.

### Logic Flow: Activation Check

```mermaid
graph TB
    Check["is_bot_token_only_mode()"]
    APIKey{"LANGSMITH_API_KEY_PROD<br/>is set?"}
    JWTSecret{"X_SERVICE_AUTH_JWT_SECRET<br/>is set?"}
    APIKeyMap{"USER_ID_API_KEY_MAP<br/>is set?"}
    BotMode["Return True<br/>(Bot Token Only Mode)"]
    OAuthMode["Return False<br/>(Per-User OAuth Mode)"]
    
    Check --> APIKey
    APIKey -->|No| OAuthMode
    APIKey -->|Yes| JWTSecret
    JWTSecret -->|Yes| OAuthMode
    JWTSecret -->|No| APIKeyMap
    APIKeyMap -->|Yes| OAuthMode
    APIKeyMap -->|No| BotMode
```

| Environment Variable | Purpose | Bot Mode Requirement |
|---------------------|---------|---------------------|
| `LANGSMITH_API_KEY_PROD` | LangSmith API key for production deployments | Must be set [agent/utils/auth.py:52]() |
| `X_SERVICE_AUTH_JWT_SECRET` | JWT secret for generating service keys to impersonate users | Must NOT be set [agent/utils/auth.py:52]() |
| `USER_ID_API_KEY_MAP` | Direct mapping of user IDs to API keys | Must NOT be set [agent/utils/auth.py:52]() |

The logic is: if deployed (`LANGSMITH_API_KEY_PROD` set) but per-user auth is impossible (neither `X_SERVICE_AUTH_JWT_SECRET` nor `USER_ID_API_KEY_MAP` configured), then bot token only mode is active.

**Sources:** [agent/utils/auth.py:27-32](), [agent/utils/auth.py:44-52]()

---

## Token Resolution Flow

When bot token only mode is active, token resolution is significantly simplified compared to the per-user OAuth flow. The system bypasses LangSmith's user-to-token mapping and directly requests an installation token for the GitHub App.

### Logic Flow: Bot Token Resolution

```mermaid
sequenceDiagram
    participant WebApp as "agent/webapp.py"
    participant Auth as "agent/utils/auth.py:resolve_github_token_from_email()"
    participant Check as "agent/utils/auth.py:is_bot_token_only_mode()"
    participant GitHubApp as "agent/utils/github_app.py:get_github_app_installation_token_with_expiry()"
    participant Persist as "agent/utils/auth.py:persist_encrypted_github_token()"
    participant Thread as "LangGraph Thread Metadata"
    
    WebApp->>Auth: email, thread_id
    Auth->>Check: Check mode
    Check-->>Auth: True (bot mode active)
    
    Auth->>GitHubApp: Fetch installation token & expiry
    
    Note over GitHubApp: Signs JWT with GITHUB_APP_PRIVATE_KEY<br/>POSTs to api.github.com/app/installations/...
    
    GitHubApp-->>Auth: (token, expires_at)
    
    Auth->>Persist: thread_id, token, expires_at
    Persist->>Thread: Store encrypted token + expiry
    Thread-->>Persist: Success
    
    Persist-->>Auth: encrypted_token
    Auth-->>WebApp: (token, encrypted_token, expires_at)
```

### Code Implementation

The resolution flow executes through these specific functions:

1.  **`resolve_github_token_from_email()`** [agent/utils/auth.py:330-388](): Entry point called by webhooks. It checks `is_bot_token_only_mode()` and, if true, calls `get_github_app_installation_token_with_expiry()`.
2.  **`get_github_app_installation_token_with_expiry()`** [agent/utils/github_app.py:41-68](): The core utility for generating the GitHub App JWT and exchanging it for an installation access token. It returns both the token and the ISO-8601 expiry string provided by GitHub.
3.  **`_generate_app_jwt()`** [agent/utils/github_app.py:19-28](): Signs a short-lived (9-minute) JWT using the `RS256` algorithm and the `GITHUB_APP_PRIVATE_KEY`.
4.  **`persist_encrypted_github_token()`** [agent/utils/auth.py:257-285](): Encrypts the raw token using Fernet and updates the LangGraph thread metadata with the ciphertext and expiry.

**Sources:** [agent/utils/auth.py:330-388](), [agent/utils/github_app.py:19-68](), [agent/utils/auth.py:257-285]()

---

## Behavior Differences

Bot token only mode changes how Open SWE interacts with GitHub compared to per-user OAuth mode.

| Aspect | Per-User OAuth Mode | Bot Token Only Mode |
|--------|---------------------|-------------------|
| **Commit Author** | Individual user's GitHub identity | GitHub App bot identity [agent/webapp.py:39]() |
| **PR Creator** | Individual user's GitHub account | GitHub App bot identity [agent/webapp.py:39]() |
| **Git Permissions** | User's personal GitHub permissions | GitHub App installation permissions [agent/utils/github_app.py:55-61]() |
| **Authentication Prompt** | Users receive auth URL if not authenticated [agent/utils/auth.py:181]() | No authentication prompts (always uses bot token) |
| **Token Lifetime** | Per-user OAuth tokens (managed by LangSmith) | Installation tokens (typically 1-hour expiry) [agent/utils/github_app.py:44-45]() |

### Sandbox Integration

When using LangSmith sandboxes, the system uses the installation token to configure the GitHub proxy. The function `_create_sandbox_with_proxy` specifically retrieves the installation token via `get_github_app_installation_token` to set up the sandbox's opaque authentication headers.

**Sources:** [tests/test_proxy_auth.py:125-145](), [agent/utils/auth.py:330-340]()

---

## Configuration Requirements

Bot token only mode still requires the GitHub App credentials to be configured, as it relies on the installation token for API access.

### Required Environment Variables

| Variable | Purpose |
|----------|---------|
| `GITHUB_APP_ID` | The unique ID of your GitHub App [agent/utils/github_app.py:14]() |
| `GITHUB_APP_PRIVATE_KEY` | The RSA private key generated for the app [agent/utils/github_app.py:15]() |
| `GITHUB_APP_INSTALLATION_ID` | The ID of the app installation on the target repo [agent/utils/github_app.py:16]() |
| `LANGSMITH_API_KEY_PROD` | Triggers deployment detection [agent/utils/auth.py:27]() |

### Explicitly Unset for Bot Mode

To ensure bot mode activates, the following must **not** be set:
*   `X_SERVICE_AUTH_JWT_SECRET` [agent/utils/auth.py:52]()
*   `USER_ID_API_KEY_MAP` [agent/utils/auth.py:52]()

**Sources:** [agent/utils/auth.py:27-32](), [agent/utils/auth.py:44-52](), [agent/utils/github_app.py:14-16]()

---

## Token Expiry and Refresh

Installation tokens retrieved in bot-token-only mode are temporary (usually 1 hour). The system handles this via:

1.  **Expiry Storage:** The `expires_at` string from GitHub is persisted in thread metadata under the `github_token_expires_at` key [agent/utils/github_token.py:19]().
2.  **Expiry Validation:** Before starting a run, `get_github_token` checks if the token is expired or within a 60-second skew window [agent/utils/github_token.py:78]().
3.  **Invalidation:** If a downstream GitHub call returns a `401 Unauthorized`, `invalidate_cached_github_token` clears the token from the thread metadata to force a fresh resolution [agent/utils/github_token.py:137-154]().

**Sources:** [agent/utils/github_token.py:18-28](), [agent/utils/github_token.py:71-78](), [agent/utils/github_token.py:137-154]()

---

# Page: Token Encryption and Storage

# Token Encryption and Storage

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/encryption.py](agent/encryption.py)
- [agent/utils/auth.py](agent/utils/auth.py)
- [agent/utils/github_app.py](agent/utils/github_app.py)
- [agent/utils/github_comments.py](agent/utils/github_comments.py)
- [agent/utils/github_token.py](agent/utils/github_token.py)
- [tests/test_encryption.py](tests/test_encryption.py)
- [tests/test_github_token_ttl.py](tests/test_github_token_ttl.py)
- [tests/test_proxy_auth.py](tests/test_proxy_auth.py)

</details>



This page documents how GitHub tokens (both OAuth user tokens and App installation tokens) are encrypted using Fernet and persisted in LangGraph thread metadata for secure reuse across agent invocations.

## Overview

Open SWE employs a security-first approach to credential management. To prevent plaintext GitHub tokens from being exposed in logs, databases, or LangGraph state history, all tokens are encrypted before being stored in thread metadata. This allows the agent to maintain a "session" across multiple turns in a Slack thread, Linear issue, or GitHub PR without requiring repeated authentication.

**Key Components:**
- **Encryption**: Fernet symmetric encryption using the `cryptography` library [agent/encryption.py:6]().
- **Storage**: LangGraph thread metadata fields `github_token_encrypted` and `github_token_expires_at` [agent/utils/github_token.py:18-19]().
- **Key Rotation**: Support for multiple keys (comma or newline separated) to allow seamless rotation [agent/encryption.py:15-22]().
- **Persistence**: Managed via the LangGraph SDK `client.threads.update` method [agent/utils/github_token.py:144-150]().

**Sources:** [agent/encryption.py:1-22](), [agent/utils/github_token.py:1-20](), [agent/utils/auth.py:16-18]()

---

## Encryption Mechanism

### Fernet Symmetric Encryption
Open SWE utilizes `MultiFernet` to handle encryption and decryption [agent/encryption.py:44-46](). The system reads the `TOKEN_ENCRYPTION_KEY` environment variable, which can contain a single key or a list of keys.

- **Encryption**: Always performed using the **first** key in the list [agent/encryption.py:28-29]().
- **Decryption**: Each key in the list is tried in order until one succeeds [agent/encryption.py:59-65]().

#### Title: Token Encryption Logic (Natural Language to Code Entity)

```mermaid
graph TD
    subgraph "Natural Language Space"
        PlainToken["Plaintext GitHub Token<br/>(ghp_... or ghs_...)"]
        EnvKey["TOKEN_ENCRYPTION_KEY<br/>(Env Var)"]
    end

    subgraph "Code Entity Space"
        EncryptFunc["encrypt_token(token)<br/>(agent/encryption.py)"]
        MultiFernetInst["MultiFernet([Fernet(k)...])<br/>(cryptography.fernet)"]
        ParseKeys["_parse_encryption_keys(raw)<br/>(agent/encryption.py)"]
    end

    subgraph "Data Space"
        ThreadMeta["Thread Metadata<br/>github_token_encrypted"]
    end

    PlainToken --> EncryptFunc
    EnvKey --> ParseKeys
    ParseKeys --> MultiFernetInst
    EncryptFunc --> MultiFernetInst
    MultiFernetInst -->|"AES-128-CBC + HMAC"| ThreadMeta
```

**Sources:** [agent/encryption.py:15-55](), [agent/utils/github_token.py:33-42]()

---

## Storage and Persistence Flow

Tokens are persisted during the `resolve_github_token` flow in the server. If a valid token is retrieved (either via LangSmith OAuth or GitHub App installation), it is encrypted and saved to the thread's metadata.

### Token Expiry and TTL
The system stores an optional `expires_at` timestamp alongside the ciphertext [agent/utils/github_token.py:19](). Before using a cached token, the system checks if it is within 60 seconds of expiration (`_GITHUB_TOKEN_EXPIRY_SKEW_SECONDS`) [agent/utils/github_token.py:28](). If expired, the cache is treated as missing, forcing a re-authentication [agent/utils/github_token.py:126-128]().

#### Title: Token Persistence Sequence (Internal Data Flow)

```mermaid
sequenceDiagram
    participant S as agent/server.py
    participant A as agent/utils/auth.py
    participant E as agent/encryption.py
    participant L as LangGraph Server

    S->>A: resolve_github_token(thread_id, ...)
    Note over A: Retrieves token from LangSmith/GitHub
    A->>E: encrypt_token(token)
    E-->>A: encrypted_string
    A->>L: threads.update(thread_id, metadata={"github_token_encrypted": ..., "github_token_expires_at": ...})
    L-->>A: Success
    A-->>S: return (token, ...)
```

**Sources:** [agent/utils/auth.py:236-258](), [agent/utils/github_token.py:45-78](), [agent/utils/github_token.py:102-134]()

---

## Retrieval and Decryption

When an agent run starts, the system attempts to hydrate the GitHub token from the thread metadata using `get_github_token_from_thread`.

### Metadata Schema
The metadata object in the LangGraph thread store tracks the following auth-related fields:

| Field | Description | Code Reference |
| :--- | :--- | :--- |
| `github_token_encrypted` | The ciphertext of the GitHub token | [agent/utils/github_token.py:18]() |
| `github_token_expires_at` | ISO-8601 or Unix timestamp of token expiry | [agent/utils/github_token.py:19]() |

#### Title: Metadata Retrieval Mapping (System Components)

```mermaid
graph LR
    subgraph "Natural Language Space"
        UserMsg["User sends follow-up message"]
    end

    subgraph "Code Entity Space"
        GetToken["get_github_token_from_thread(thread_id)"]
        Decrypt["decrypt_token(encrypted_token)"]
        IsExpired["_is_expired(expires_at)"]
        LS_Client["langgraph_sdk.get_client()"]
    end

    subgraph "Data Space"
        ThreadDB[("LangGraph Thread Store")]
    end

    UserMsg --> GetToken
    GetToken --> LS_Client
    LS_Client -->|"threads.get(thread_id)"| ThreadDB
    ThreadDB -->|"metadata"| IsExpired
    IsExpired -->|"If Fresh"| Decrypt
    Decrypt -->|"Plaintext Token"| AgentRun["Agent Tool Execution"]
```

**Sources:** [agent/utils/github_token.py:81-134](), [agent/utils/auth.py:138-182]()

---

## Key Management and Security

### Key Rotation Lifecycle
Open SWE supports zero-downtime key rotation:
1.  **Add New Key**: Prepend the new key to `TOKEN_ENCRYPTION_KEY` (e.g., `NEW_KEY,OLD_KEY`) [agent/encryption.py:28-29]().
2.  **Transition**: The system will encrypt all *new* tokens with `NEW_KEY` but can still decrypt existing tokens using `OLD_KEY` [agent/encryption.py:59-65]().
3.  **Remove Old Key**: Once old tokens have expired or been replaced, `OLD_KEY` can be removed from the environment variable.

### Invalidation on 401 Errors
If a downstream GitHub API call returns a `401 Unauthorized` status, the system raises a `GitHubAuthError` [agent/utils/github_token.py:22-23](). The middleware or server then calls `invalidate_cached_github_token(thread_id)`, which explicitly sets the metadata fields to `None` in the thread store [agent/utils/github_token.py:137-154](). This ensures the next run performs a fresh OAuth flow instead of using a revoked token.

### Sandbox Proxy Authentication
For LangSmith-hosted sandboxes, the GitHub token is not passed into the sandbox environment variables. Instead, `_configure_github_proxy` is called to set up a network proxy that injects the `Authorization` header (as `Bearer` for API and `Basic` for git) into outgoing requests to `github.com` [tests/test_proxy_auth.py:43-60]().

**Sources:** [agent/encryption.py:15-41](), [agent/utils/github_token.py:137-154](), [tests/test_proxy_auth.py:17-61](), [agent/integrations/langsmith.py:11-13]()

---

# Page: Security Policy

# Security Policy

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [SECURITY.md](SECURITY.md)
- [agent/utils/github_org_membership.py](agent/utils/github_org_membership.py)
- [tests/test_public_repo_org_gate.py](tests/test_public_repo_org_gate.py)

</details>



This document describes the security policy for the Open SWE framework, including vulnerability reporting procedures, contact information, and technical implementation of security gates. It details the security boundaries, data flow protections, and implementation of safety mechanisms like organization-level gating for public repositories.

## Purpose and Scope

This page covers:
- Security vulnerability reporting procedures and contact information.
- Security boundaries and trust model in the Open SWE architecture.
- Implementation of the Public Repository Organization Gate.
- Networking security and SSRF prevention in agent tools.
- Best practices for secure deployment and credential management.

For authentication implementation details, see [7.1 GitHub Token Resolution](), [7.2 Bot Token Only Mode](), and [7.3 Token Encryption and Storage](). For sandbox isolation mechanisms, see [4.1 Sandbox Architecture]().

---

## Vulnerability Reporting

### Contact Information

For any security concerns or vulnerabilities, contact:

**Email:** `security@langchain.dev`

This email address is monitored by the LangChain security team and should be used for all security-related reports.

**Sources:** [SECURITY.md:1-4]()

### What to Report

Security vulnerabilities in Open SWE should be reported if they could lead to:

| Vulnerability Type | Description | Example |
|-------------------|-------------|---------|
| **Authentication Bypass** | Circumventing token verification or webhook signature validation. | Accepting unsigned GitHub webhook payloads. |
| **Credential Exposure** | Leaking encrypted GitHub tokens or API keys. | Logging decrypted tokens in error messages. |
| **Sandbox Escape** | Breaking out of sandbox isolation to access host system. | Exploiting `execute` tool to run commands on the host machine. |
| **SSRF / Internal Access** | Forcing the agent to scan or request internal network resources. | Bypassing IP filters in `http_request`. |
| **Unauthorized Access** | Accessing repositories without valid GitHub OAuth or App tokens. | Reading private code via a leaked session ID. |
| **Public Repo Abuse** | Non-members triggering agent runs on public repositories. | External users consuming compute by commenting on public PRs. |

**Sources:** [SECURITY.md:1-4](), [tests/test_public_repo_org_gate.py:55-99]()

---

## Security Architecture

### Security Boundaries and Data Flow

The following diagram associates high-level security zones with specific code entities responsible for maintaining those boundaries.

**System Security Entity Map**
```mermaid
graph TB
    subgraph UntrustedZone["External Untrusted Zone"]
        User["User / Platform"]
    end
    
    subgraph ValidationLayer["Validation Layer (agent/webapp.py)"]
        VerifySig["verify_github_signature()<br/>agent/utils/github_comments.py"]
        OrgGate["is_user_active_org_member()<br/>agent/utils/github_org_membership.py"]
        WebhookHandler["github_webhook_endpoint<br/>agent/webapp.py"]
    end
    
    subgraph TrustedCore["Trusted Core (agent/utils/auth.py)"]
        AuthUtil["resolve_github_token_from_email()<br/>agent/utils/auth.py"]
        Encrypt["encrypt_token()<br/>agent/encryption.py"]
        LS_Auth["get_github_token_for_user()<br/>agent/utils/auth.py"]
    end
    
    subgraph ExecutionIsolation["Execution Isolation (Sandbox)"]
        Sandbox["SandboxBackendProtocol<br/>agent/integrations/base.py"]
        SafeHTTP["_is_url_safe()<br/>agent/tools/http_request.py"]
    end

    User -->|"Webhook + X-Hub-Signature-256"| WebhookHandler
    WebhookHandler --> VerifySig
    VerifySig --> OrgGate
    OrgGate -->|"Success"| AuthUtil
    AuthUtil --> LS_Auth
    LS_Auth --> Encrypt
    AuthUtil -->|"Decrypted Token"| Sandbox
    Sandbox -->|"Outbound Request"| SafeHTTP
    
    style ValidationLayer fill:transparent,stroke-dasharray: 5 5
    style ExecutionIsolation fill:transparent,stroke-dasharray: 5 5
```

**Sources:** [agent/webapp.py:77-110](), [agent/utils/github_org_membership.py:16-65](), [agent/utils/auth.py:175-200](), [agent/tools/http_request.py:11-40]()

---

## Public Repository Gating

To prevent compute abuse on public repositories, Open SWE implements an organization membership gate. When the system receives a webhook from a public repository, it verifies that the sender is an active member of a trusted organization.

### Membership Verification Logic
The `is_user_active_org_member` function performs a "fail-closed" check against the GitHub API.

**Gating Flow**
```mermaid
sequenceDiagram
    participant GH as GitHub Webhook
    participant Webapp as agent/webapp.py
    participant Gate as agent/utils/github_org_membership.py
    participant API as GitHub API (/orgs/{org}/memberships/{user})

    GH->>Webapp: Issue Comment (Public Repo)
    Webapp->>Gate: is_user_active_org_member(sender, gate_org)
    Gate->>API: GET Membership Status (using App Token)
    alt User is Active Member
        API-->>Gate: 200 OK (state: active)
        Gate-->>Webapp: True
        Webapp->>Webapp: Process Command
    else User is NOT Member
        API-->>Gate: 404 Not Found
        Gate-->>Webapp: False
        Webapp-->>GH: 200 OK (status: ignored, reason: not a member)
    end
```

**Key Implementation Details:**
- **App Token Usage**: The check uses `get_github_app_installation_token()` to ensure it can view private memberships if necessary [agent/utils/github_org_membership.py:27-32]().
- **Fail-Closed**: Any API error or unexpected status code results in a `False` return, blocking the agent invocation [agent/utils/github_org_membership.py:45-58]().
- **Private Repo Bypass**: This gate is automatically skipped for private repositories, as access is already controlled by repository permissions [tests/test_public_repo_org_gate.py:143-182]().
- **Internal Bots**: Known internal bot logins (e.g., `open-swe[bot]`) are defined in `INTERNAL_BOT_LOGINS` [agent/utils/github_org_membership.py:13]().

**Sources:** [agent/utils/github_org_membership.py:1-66](), [tests/test_public_repo_org_gate.py:55-142]()

---

## Networking Security: SSRF Prevention

Open SWE includes specific protections to prevent Server-Side Request Forgery (SSRF) when the agent uses tools to fetch external data.

### URL Validation Logic
The `http_request` and `fetch_url` tools utilize `_is_url_safe()` to validate every URL and redirect target. This function resolves hostnames to IP addresses and blocks any that fall into private or reserved ranges.

**Implementation Details:**
- **Private IP Blocking**: Blocks ranges like `127.0.0.1`, `10.0.0.0/8`, and the AWS metadata IP `169.254.169.254` [agent/tools/http_request.py:34-35]().
- **Redirect Validation**: The system follows up to 5 redirects, but re-validates the safety of the `Location` header at every step [agent/tools/http_request.py:64-97]().
- **Scheme Enforcement**: Only `http` and `https` schemes are permitted [agent/tools/http_request.py:15-16]().

**Sources:** [agent/tools/http_request.py:11-97](), [agent/tools/fetch_url.py:35-46]()

---

## Sensitive Data Management

### Token Encryption
GitHub OAuth tokens are never stored in plain text within the thread metadata. They are encrypted using the `encrypt_token` utility before being persisted [agent/utils/auth.py:16]().

### Bot Token Only Mode
In environments where per-user OAuth is not configured (missing `X_SERVICE_AUTH_JWT_SECRET`), the system defaults to "Bot Token Only Mode". In this mode, it uses the GitHub App's installation token for all operations, reducing the surface area for user credential handling [agent/utils/auth.py:44-52]().

### Webhook Verification
GitHub webhooks are verified using the `X-Hub-Signature-256` header and a configured `GITHUB_WEBHOOK_SECRET`. If the secret is missing or the signature does not match the HMAC of the body, the request is rejected [tests/test_public_repo_org_gate.py:17-32]().

**Sources:** [agent/utils/auth.py:44-52](), [agent/encryption.py:1-20](), [tests/test_public_repo_org_gate.py:17-32]()

---

## Security Best Practices for Deployment

| Category | Best Practice | Implementation Reference |
| :--- | :--- | :--- |
| **Secrets** | Never hardcode keys. Use environment variables. | [agent/utils/auth.py:27-32]() |
| **Sandboxing** | Use `langsmith` or `modal` backends for production isolation. | [agent/integrations/base.py]() |
| **Tokens** | Ensure `FERNET_KEY` is rotated periodically. | [agent/encryption.py]() |
| **Public Gating** | Set `PUBLIC_REPO_ORG_GATE` to your GitHub Org name. | [tests/test_public_repo_org_gate.py:49]() |

### Environment Variable Protection
The following variables are critical for security and must be protected:
- `GITHUB_WEBHOOK_SECRET`: Used to verify incoming GitHub events.
- `PUBLIC_REPO_ORG_GATE`: Defines the organization required to trigger agents on public repos [tests/test_public_repo_org_gate.py:49]().
- `X_SERVICE_AUTH_JWT_SECRET`: Used to generate service keys for LangSmith auth [agent/utils/auth.py:83-85]().
- `FERNET_KEY`: Used for encrypting tokens in the database [agent/encryption.py]().

**Sources:** [agent/utils/auth.py:83-85](), [agent/encryption.py](), [tests/test_public_repo_org_gate.py:47-53]()

---

# Page: Reviewer Agent

# Reviewer Agent

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/reviewer.py](agent/reviewer.py)
- [agent/tools/publish_review.py](agent/tools/publish_review.py)
- [tests/test_reviewer.py](tests/test_reviewer.py)
- [tests/test_reviewer_publish.py](tests/test_reviewer_publish.py)

</details>



The **Reviewer Agent** is a specialized LangGraph-based agent designed to perform automated code reviews on GitHub Pull Requests. Unlike the general-purpose coding agent, the Reviewer Agent is optimized for high-precision defect detection, adherence to repository-specific styles, and persistent findings management across multiple commits.

## Overview

The Reviewer Agent operates within a controlled sandbox environment, mirroring the repository state at the PR's head SHA. It utilizes a multi-pass workflow to identify bugs, validate them against the PR diff, and manage a lifecycle of "Findings" that can be published as inline GitHub comments.

### Core Responsibilities
*   **Deterministic Preparation**: Automatically clones the repository and checks out the target SHA before the first model call [agent/reviewer.py:6-7]().
*   **Precision Tooling**: Uses a specialized toolset (`add_finding`, `update_finding`, `list_findings`, `publish_review`) focused on review state rather than code modification [agent/reviewer.py:11-12]().
*   **Diff Discipline**: Enforces strict rules to only file findings anchored to changed lines or proven regressions [agent/reviewer.py:97-107]().
*   **Context Awareness**: Injects repository-specific conventions from `AGENTS.md` and historical review styles [agent/reviewer.py:62, 181-190]().

### High-Level System Flow
The following diagram illustrates how the Reviewer Agent bridges the gap between GitHub PR events and the internal code entity representation.

**Reviewer System Architecture**
```mermaid
graph TD
    subgraph "GitHub Space"
        PR["Pull Request (head_sha)"]
        Comments["Review Comments / Threads"]
    end

    subgraph "Open SWE Reviewer Agent"
        direction TB
        Factory["get_reviewer_agent()"]
        Prompt["REVIEWER_PROMPT_TEMPLATE"]
        FindingsDB["LangGraph State (Findings)"]
    end

    subgraph "Sandbox (Code Entity Space)"
        Repo["Cloned Repository"]
        Diff["Unified Diff (git show)"]
        Grep["Symbol Search (grep/ls)"]
    end

    PR -->|"Trigger"| Factory
    Factory -->|"Prepares"| Repo
    Repo -->|"Provides"| Diff
    Diff -->|"Validates"| FindingsDB
    Prompt -->|"Guides"| Factory
    FindingsDB -->|"publish_review"| Comments
```
Sources: [agent/reviewer.py:1-15](), [agent/reviewer.py:68-95](), [agent/tools/publish_review.py:38-75]()

---

## Sub-Pages

### [Reviewer Architecture and Workflow](#8.1)
The reviewer is instantiated via `get_reviewer_agent()`, which configures a `deep_agent` with specialized system prompts and tools [agent/reviewer.py:3-15](). It follows a lifecycle that includes sandbox preparation, diff analysis, and a "watch-mode" for re-reviews when new commits are pushed.
For details, see [Reviewer Architecture and Workflow](#8.1).

### [Findings Management](#8.2)
Findings are the primary data structure for the reviewer. Each `Finding` includes severity, file/line anchors, and suggestions [agent/reviewer_findings.py:10-33](). The agent uses `add_finding` to record issues and `update_finding` to manage their status (e.g., "resolved") during re-reviews [agent/reviewer.py:90-95]().
For details, see [Findings Management](#8.2).

### [Review Style System](#8.3)
To ensure reviews feel native to a team, the system includes a Review Style Analyzer. This component crawls historical PR feedback to generate a `repo_style_prompt`, which is then injected into the agent's system prompt [agent/reviewer.py:25-35]().
For details, see [Review Style System](#8.3).

### [Reviewer Evaluation Infrastructure](#8.4)
The quality of the reviewer is measured using an offline LangSmith evaluation framework. This includes a benchmark dataset and a "judge model" that evaluates the accuracy and relevance of the agent's findings without posting to GitHub [agent/tools/publish_review.py:97-104](), [tests/test_reviewer_publish.py:91-128]().
For details, see [Reviewer Evaluation Infrastructure](#8.4).

---

## Reviewer Agent Entity Map

This diagram maps the internal Python classes and functions to the conceptual stages of a code review.

**Code Entity Mapping**
```mermaid
graph LR
    subgraph "Orchestration"
        A["get_reviewer_agent()"] --> B["create_deep_agent()"]
        A --> C["ensure_sandbox_for_thread()"]
    end

    subgraph "Tools (agent.tools.*)"
        D["add_finding"]
        E["update_finding"]
        F["publish_review"]
    end

    subgraph "Persistence"
        G["Finding (TypedDict)"]
        H["set_reviewer_thread_metadata"]
    end

    B -.-> D
    B -.-> E
    B -.-> F
    D --> G
    F --> H
```
Sources: [agent/reviewer.py:34-61](), [agent/tools/publish_review.py:10-18](), [agent/reviewer_findings.py:10-33]()

## Key Constraints
The Reviewer Agent is explicitly instructed to avoid:
1.  **Style Nits**: No naming or extraction suggestions unless they break behavior [agent/reviewer.py:128-132]().
2.  **Speculation**: No "potential" race conditions without a reachable trigger [agent/reviewer.py:133-135]().
3.  **Overlap**: It must not duplicate existing human review threads [agent/reviewer.py:110-127]().

Sources: [agent/reviewer.py:1-15](), [agent/reviewer.py:68-150](), [agent/tools/publish_review.py:38-75](), [agent/reviewer_findings.py:10-33](), [tests/test_reviewer.py:11-35]()

---

# Page: Reviewer Architecture and Workflow

# Reviewer Architecture and Workflow

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [REVIEWER_DESIGN.md](REVIEWER_DESIGN.md)
- [agent/reviewer.py](agent/reviewer.py)
- [agent/reviewer_diff.py](agent/reviewer_diff.py)
- [agent/reviewer_publish.py](agent/reviewer_publish.py)
- [agent/tools/list_findings.py](agent/tools/list_findings.py)
- [tests/test_reviewer.py](tests/test_reviewer.py)
- [tests/test_reviewer_watch.py](tests/test_reviewer_watch.py)

</details>



The Reviewer Agent is a specialized LangGraph-based agent designed to perform automated code reviews on GitHub Pull Requests. Unlike the general-purpose coding agent, the reviewer focuses on identifying defects, enforcing repository-specific styles, and maintaining an evolving list of "Findings" across the PR lifecycle. It supports a "watch-mode" that automatically re-evaluates the PR when new commits are pushed.

## Reviewer Agent Factory

The `get_reviewer_agent()` function is the primary factory for assembling the reviewer. It mirrors the standard agent setup but specializes the configuration for review tasks [agent/reviewer.py:1-15]().

### Configuration and Tools
The factory configures a `deep_agent` with a specific toolset and middleware:
*   **Specialized Tools**: `add_finding`, `update_finding`, `list_findings`, and `publish_review`. It explicitly excludes tools for committing, pushing, or opening PRs to ensure it remains a read-only observer of the codebase [agent/reviewer.py:53-61]().
*   **Model Setup**: Uses `make_model` to initialize the LLM, supporting reasoning efforts (e.g., "high" for O1/Claude models) and adaptive thinking [agent/reviewer.py:65](), [tests/test_reviewer.py:86-128]().
*   **Middleware**: Includes `SanitizeToolInputsMiddleware`, `SlackAssistantStatusMiddleware`, and `ToolErrorMiddleware` to handle common execution issues [agent/reviewer.py:37-41]().

### Deterministic Preparation
Before the agent's first model call, the factory performs "deterministic repo prep." This involves cloning the repository and checking out the specific `head_sha` in the sandbox. This saves tokens by preventing the LLM from having to manually run `gh repo clone` or `git checkout` commands [agent/reviewer.py:6-10]().

Sources: [agent/reviewer.py:1-67](), [tests/test_reviewer.py:86-128]()

## Multi-Pass Review Workflow

The reviewer follows a structured prompt-driven workflow defined in the `REVIEWER_PROMPT_TEMPLATE`. This template enforces a high bar for findings and a specific sequence of operations.

### Review Phases
| Phase | Action | Purpose |
| :--- | :--- | :--- |
| **1. Discovery** | `gh pr diff` | Read the PR diff end-to-end to identify changed lines [agent/reviewer.py:72-76](). |
| **2. Contextualization** | `gh repo clone` | Obtain full file context and grep for callers/implementers if signatures changed [agent/reviewer.py:84-88](). |
| **3. Analysis** | Base-vs-Head | Use `git show <base_sha>:path` to compare old vs. new logic, looking for dropped behaviors like nil-checks or error handling [agent/reviewer.py:154-158](). |
| **4. Reporting** | `add_finding` | Record concrete defects anchored to specific lines in the diff [agent/reviewer.py:90-95](). |
| **5. Finalization** | `publish_review` | Batch findings and post them to GitHub as a single review [agent/reviewer.py:91-92](). |

### Finding Criteria ("The Bar")
The agent is instructed to only file findings that:
1.  Can be anchored to a specific changed line [agent/reviewer.py:99]().
2.  Name a concrete failure mode (build-time, runtime, or user-facing) [agent/reviewer.py:100-101]().
3.  Exist within the PR diff hunk or represent a proven regression on a changed symbol [agent/reviewer.py:102-106]().

Sources: [agent/reviewer.py:68-164](), [REVIEWER_DESIGN.md:75-86]()

## Sandbox Preparation and Diff Management

The reviewer relies on a robust sandbox environment to execute `gh` and `git` commands. It uses specialized utilities to manage diffs and validate findings before they are sent to GitHub.

### Diff Line Validation
To prevent "out-of-bounds" comments that GitHub's API would reject, the system computes a `diff_line_set` [agent/reviewer_diff.py:125-138](). The `add_finding` tool uses `is_range_in_diff` to verify that the suggested comment falls within the actual changes of the PR [agent/reviewer_diff.py:166-183]().

### Code Entity Space to Sandbox Flow
The following diagram illustrates how the system prepares the sandbox for a review run.

**Sandbox Initialization Flow**
```mermaid
graph TD
    subgraph "Natural Language Space"
        User["User Request / Webhook"] -- "PR URL / Branch" --> Trigger["Trigger Handler"]
    end

    subgraph "Code Entity Space"
        Trigger -- "Thread ID" --> GetAgent["get_reviewer_agent()"]
        GetAgent -- "Config" --> EnsureSB["ensure_sandbox_for_thread()"]
        EnsureSB -- "Sandbox ID" --> SB["SandboxBackendProtocol"]
        
        GetAgent -- "Context" --> DiffUtil["compute_diff_in_sandbox()"]
        DiffUtil -- "git diff" --> SB
        
        SB -- "diff_text" --> Parser["parse_unified_diff()"]
        Parser -- "Line Sets" --> Validator["is_range_in_diff()"]
    end
```
Sources: [agent/reviewer.py:50](), [agent/reviewer_diff.py:125-138](), [agent/reviewer_diff.py:166-193]()

## Findings Lifecycle and State

Findings are treated as first-class state, persisted in **LangGraph thread metadata** rather than temporary sandbox files. This ensures they survive sandbox evictions [REVIEWER_DESIGN.md:31-34]().

### Finding Data Structure
Each `Finding` (defined in `agent/reviewer_findings.py`) includes:
*   `id`: A stable, unique identifier (e.g., `f_<uuid>`) [REVIEWER_DESIGN.md:37]().
*   `severity`: From `informational` to `critical` [REVIEWER_DESIGN.md:38]().
*   `suggestion`: Optional replacement text for GitHub's "Commit suggestion" UI [REVIEWER_DESIGN.md:45]().
*   `status`: `open`, `resolved`, or `dismissed` [REVIEWER_DESIGN.md:46]().
*   `github_review_comment_id`: The ID returned by GitHub after publishing, used to track threads [REVIEWER_DESIGN.md:49]().

### Mutation Tools
The agent manages findings through three primary tools:
1.  `add_finding`: Creates a new record in thread metadata [agent/tools/add_finding.py]().
2.  `update_finding`: Modifies existing findings (e.g., changing status to `resolved`) [agent/tools/update_finding.py]().
3.  `list_findings`: Retrieves findings for the current thread, allowing the agent to see what was previously reported [agent/tools/list_findings.py:16-36]().

Sources: [REVIEWER_DESIGN.md:31-74](), [agent/tools/list_findings.py:1-37]()

## Watch-Mode and Re-Review Lifecycle

The "watch-mode" enables the reviewer to act as a continuous integration component, updating its review as the PR evolves.

### Triggering the Lifecycle
1.  **Push Event**: When a new commit is pushed to a branch, `process_github_push_event` checks if the corresponding thread has the `watch: True` flag in its metadata [tests/test_reviewer_watch.py:78-133]().
2.  **Re-Review Run**: If watching, a new LangGraph run is created with `re_review: True` and `last_reviewed_sha` passed in the configuration [tests/test_reviewer_watch.py:139-141]().
3.  **Lifecycle Management**: The watch is automatically disabled when a PR is closed and re-enabled if it is reopened [tests/test_reviewer_watch.py:185-206]().

### Re-Review Reconciliation
During a re-review, the agent's prompt instructs it to:
*   Fetch the diff between the `last_reviewed_sha` and the current `head_sha` [agent/reviewer.py:78-82]().
*   Use `list_findings` to see existing issues [agent/reviewer.py:93]().
*   Call `update_finding(id, status="resolved")` for issues that are no longer present [agent/reviewer.py:93-94]().
*   Add net-new findings for defects introduced in the latest commits [agent/reviewer.py:95]().

**Watch-Mode Data Flow**
```mermaid
graph LR
    subgraph "GitHub Events"
        Push["Push Event"]
        PRClose["PR Closed"]
    end

    subgraph "Webapp Logic"
        Push -- "Check Metadata" --> WatchCheck{"is watch: True?"}
        WatchCheck -- "Yes" --> TriggerRun["client.runs.create(..., re_review=True)"]
        PRClose -- "Update Metadata" --> DisableWatch["set_reviewer_thread_metadata(watch=False)"]
    end

    subgraph "Reviewer Agent Run"
        TriggerRun --> ListPrev["list_findings()"]
        ListPrev --> CompareDiff["git diff last_sha..head_sha"]
        CompareDiff --> Resolve["update_finding(status='resolved')"]
    end
```
Sources: [agent/reviewer.py:78-96](), [tests/test_reviewer_watch.py:1-206](), [REVIEWER_DESIGN.md:10-12]()

---

# Page: Findings Management

# Findings Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/reviewer_findings.py](agent/reviewer_findings.py)
- [agent/tools/add_finding.py](agent/tools/add_finding.py)
- [agent/tools/publish_review.py](agent/tools/publish_review.py)
- [agent/tools/update_finding.py](agent/tools/update_finding.py)
- [tests/test_reviewer_findings.py](tests/test_reviewer_findings.py)
- [tests/test_reviewer_publish.py](tests/test_reviewer_publish.py)
- [tests/test_reviewer_tools.py](tests/test_reviewer_tools.py)

</details>



The **Findings Management** system provides a structured way for Reviewer Agents to record, update, and persist code review feedback. Unlike standard agent tool outputs which are ephemeral, Findings are stored in **LangGraph thread metadata** to ensure they persist across sandbox evictions and multiple agent runs, enabling "watch-mode" re-reviews and a historical record of PR health.

## The Finding Data Structure

A `Finding` is a structured record of a single issue discovered during a code review. It is defined as a `TypedDict` to facilitate partial updates while maintaining a strict schema for the UI and automated publishing.

### Key Schema Fields
| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | `str` | A stable, short, URL-friendly ID (e.g., `f_a1b2c3d4e5`) [agent/reviewer_findings.py:102-104](). |
| `severity` | `Severity` | One of `low`, `medium`, `high`, `critical` [agent/reviewer_findings.py:42](). |
| `status` | `Status` | `open`, `resolved`, or `dismissed` [agent/reviewer_findings.py:44](). |
| `file` | `str` | Repo-relative path of the affected file [agent/reviewer_findings.py:70](). |
| `start_line` | `int \| None` | 1-based start line in the post-PR file [agent/reviewer_findings.py:71](). |
| `end_line` | `int \| None` | 1-based end line (the anchor for GitHub comments) [agent/reviewer_findings.py:72](). |
| `suggestion` | `str \| None` | A concrete code replacement block [agent/reviewer_findings.py:75](). |
| `first_seen_sha` | `str` | The HEAD SHA when the finding was first recorded [agent/reviewer_findings.py:77](). |

**Sources:** [agent/reviewer_findings.py:59-81](), [agent/reviewer_findings.py:107-139]()

## Tooling and Validation

The agent interacts with findings through a set of specialized tools that enforce validation logic before persisting data to the thread.

### `add_finding`
This tool creates a new finding. It performs two critical validations:
1.  **Diff-Line Validation**: It checks if the `start_line` and `end_line` are actually within the PR's changed lines using `is_range_in_diff` [agent/tools/add_finding.py:107-116](). Findings outside the diff are rejected to prevent the agent from flagging unrelated "pre-existing" code.
2.  **Suggestion Clipping**: Suggestions are capped at **4 lines** (`MAX_SUGGESTION_LINES`) [agent/reviewer_findings.py:30](). If a suggestion is too long, it is dropped, and the finding is recorded with only a description to prevent cluttered "rewrite" comments [agent/tools/add_finding.py:124-150]().

### `update_finding`
Used primarily during re-reviews, this tool allows the agent to mutate an existing finding. It is frequently used to move a finding from `open` to `resolved` when a developer pushes a fix [agent/tools/update_finding.py:36-37]().

### `list_findings`
Retrieves all findings currently stored in the thread metadata, allowing the agent to "remember" what it previously flagged [agent/tools/list_findings.py:1-25]().

**Sources:** [agent/tools/add_finding.py:24-86](), [agent/tools/update_finding.py:18-50](), [agent/reviewer_findings.py:33-40]()

## Data Flow and Persistence

Findings are stored in the `metadata` field of a LangGraph thread. This architectural choice allows findings to be queried via the LangGraph SDK without needing a separate database.

### Finding Persistence Flow
The following diagram shows how a tool call from the Reviewer Agent reaches the persistent storage.

```mermaid
graph TD
  subgraph "Natural Language Space"
    A["Reviewer Agent (LLM)"] -- "Identifies Bug" --> B["Tool Call: add_finding"]
  end

  subgraph "Code Entity Space"
    B --> C["add_finding() function"]
    C --> D["is_range_in_diff() validation"]
    D -- "Valid" --> E["append_finding()"]
    E --> F["get_client() -> LangGraph SDK"]
    F -- "PATCH /threads/{id}" --> G["Thread Metadata (findings: [])"]
  end
```
**Sources:** [agent/tools/add_finding.py:101-141](), [agent/reviewer_findings.py:205-210](), [agent/reviewer_findings.py:199-202]()

## Severity Rubric

The system uses a strict severity hierarchy to determine which findings are "surfaced" (posted as GitHub comments) versus which stay "hidden" (only visible in the internal UI).

| Severity | Order Value | Typical Usage |
| :--- | :--- | :--- |
| `critical` | 3 | Security vulnerabilities, data loss, or certain crashes. |
| `high` | 2 | Logic errors, broken requirements, or major performance regressions. |
| `medium` | 1 | Code smells, missing edge case handling, or significant style violations. |
| `low` | 0 | Minor style nits or documentation typos. |

By default, the `publish_review` tool uses a `severity_threshold` of `medium` [agent/tools/publish_review.py:39]().

**Sources:** [agent/reviewer_findings.py:47-52](), [agent/tools/publish_review.py:48-50]()

## Publishing to GitHub

The `publish_review` tool translates the internal `Finding` list into a GitHub PR Review.

### Publishing Logic
1.  **Filtering**: Only `open` findings meeting the `severity_threshold` are selected [agent/tools/publish_review.py:48-50]().
2.  **Capping**: To avoid spam, the tool caps the number of inline comments (default 4) [agent/tools/publish_review.py:40]().
3.  **Rendering**: Each finding is converted into a GitHub comment payload. If a `suggestion` exists, it is wrapped in a Markdown ` ```suggestion ` block [agent/reviewer_publish.py:26-27]().
4.  **Thread Resolution**: On re-reviews, if a previously `open` finding is now `resolved`, the tool calls the GitHub GraphQL API to resolve the corresponding review thread [agent/tools/publish_review.py:61-63]().

### Review Lifecycle Diagram
This diagram bridges the internal Finding state to the external GitHub PR entities.

```mermaid
graph LR
  subgraph "Open SWE State (agent/reviewer_findings.py)"
    F["Finding Object"]
    F -- "id" --> FID["Finding ID"]
    F -- "status: resolved" --> RES["Resolved Status"]
  end

  subgraph "GitHub PR (agent/reviewer_publish.py)"
    FID -- "render_inline_comment_payload" --> GHC["GitHub Inline Comment"]
    RES -- "resolve_review_thread" --> GHT["GitHub Resolved Thread"]
  end

  F -- "severity >= threshold" --> GHC
```
**Sources:** [agent/tools/publish_review.py:38-75](), [agent/reviewer_publish.py:11-29](), [agent/reviewer_findings.py:158-162]()

---

# Page: Review Style System

# Review Style System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/dashboard/oauth.py](agent/dashboard/oauth.py)
- [agent/dashboard/review_style_jobs.py](agent/dashboard/review_style_jobs.py)
- [agent/dashboard/review_styles.py](agent/dashboard/review_styles.py)
- [agent/review_style_collector.py](agent/review_style_collector.py)
- [agent/review_style_guidance.py](agent/review_style_guidance.py)
- [tests/test_github_oauth_refresh.py](tests/test_github_oauth_refresh.py)
- [tests/test_review_style_sync.py](tests/test_review_style_sync.py)
- [ui/src/components/ReviewStylesPanel.tsx](ui/src/components/ReviewStylesPanel.tsx)

</details>



The Review Style System is a specialized analysis pipeline that allows Open SWE to adapt its PR review feedback to the specific cultural and technical norms of a repository. Instead of applying a generic set of rules, the system analyzes historical Pull Request (PR) feedback from human reviewers to synthesize a custom system prompt for the reviewer agent.

## System Overview

The system consists of a background analysis graph (`review_style_analyzer`), a collection utility for gathering historical GitHub data, and a management interface within the dashboard.

### Data Flow

1.  **Trigger**: A user adds a repository to the "Review Styles" panel in the dashboard and clicks "Analyze".
2.  **Collection**: The system paginates through the last ~20 merged PRs, extracting substantive comments from human reviewers while filtering out bots [agent/review_style_collector.py:149-168]().
3.  **Analysis**: A LangGraph-based analyzer (the `review_style_analyzer` assistant) processes these samples against a set of guidance themes [agent/review_style_guidance.py:3-17]().
4.  **Synthesis**: The analyzer generates a "Review Style Prompt"—a concise set of instructions that steer the reviewer agent's tone, severity, and focus areas.
5.  **Injection**: During a standard reviewer run, this custom prompt is fetched from the LangGraph Store and injected into the agent's system instructions.

### Review Style Architecture
The following diagram illustrates how the natural language feedback from GitHub is transformed into a structured prompt used by the code-level Reviewer Agent.

**Review Style Synthesis Flow**
```mermaid
graph TD
    subgraph "GitHub Space"
        PR["Merged Pull Requests"]
        HC["Human Comments"]
    end

    subgraph "Review Style System (Code Entities)"
        RSC["collect_review_samples()"]
        RSA["review_style_analyzer (LangGraph)"]
        RSG["REVIEWER_STYLE_THEMES"]
        LGS[("LangGraph Store")]
    end

    subgraph "Reviewer Execution"
        RA["Reviewer Agent"]
        SP["System Prompt"]
    end

    PR -->|Paginate| RSC
    HC --> RSC
    RSC -->|ReviewStyleSamples| RSA
    RSG -->|Steering| RSA
    RSA -->|Synthesized Prompt| LGS
    LGS -->|Inject custom_prompt| SP
    SP --> RA
```
Sources: [agent/review_style_collector.py:149-168](), [agent/dashboard/review_style_jobs.py:88-105](), [agent/review_style_guidance.py:3-17](), [agent/dashboard/review_styles.py:1-5]()

## Historical Feedback Collection

The `collect_review_samples` function in `agent/review_style_collector.py` is responsible for gathering the raw data needed for analysis.

### Key Logic:
*   **Filtering**: It explicitly ignores comments from users ending in `[bot]` or `-bot` to ensure the style is derived from humans [agent/review_style_collector.py:86-98]().
*   **Substance Check**: Comments shorter than 20 characters are discarded to filter out "LGTM" or simple acknowledgments [agent/review_style_collector.py:101-105]().
*   **Sampling Strategy**: It identifies the "top reviewers" (most active humans) and samples up to 6 comments per reviewer across the most recent 20 merged PRs [agent/review_style_collector.py:15-17]().

Sources: [agent/review_style_collector.py:86-105](), [agent/review_style_collector.py:149-200]()

## Analysis and Persistence

The analysis is performed as a background job managed by `agent/dashboard/review_style_jobs.py`.

### Job Lifecycle
1.  **`start_review_style_analysis`**: Initializes the thread, collects samples, and creates a run on the `review_style_analyzer` assistant [agent/dashboard/review_style_jobs.py:38-43]().
2.  **State Management**: The status is tracked in the LangGraph Store under the `["review_styles"]` namespace [agent/dashboard/review_styles.py:18-20]().
3.  **`reconcile_running_status`**: Handles terminal states (success/failure) and ensures that if a prompt was successfully saved, the status is marked as `completed` even if the run technically failed or timed out later [agent/dashboard/review_styles.py:147-182]().

### Review Style Record Structure
| Field | Description |
| :--- | :--- |
| `full_name` | The `owner/repo` identifier. |
| `status` | `idle`, `running`, `completed`, or `failed`. |
| `custom_prompt` | The synthesized markdown prompt used by the reviewer. |
| `top_reviewers` | List of human logins identified during collection. |
| `prs_sampled` | Total count of PRs scanned. |

Sources: [agent/dashboard/review_style_jobs.py:38-111](), [agent/dashboard/review_styles.py:78-96](), [agent/dashboard/review_styles.py:147-182]()

## Dashboard Integration

The `ReviewStylesPanel` React component provides the UI for managing these styles. It uses TanStack Query to poll the status of running analyses every 4 seconds [ui/src/components/ReviewStylesPanel.tsx:51-54]().

**UI to Backend Mapping**
```mermaid
graph LR
    subgraph "ui/src/components/ReviewStylesPanel.tsx"
        Btn["'Analyze' Button"]
        Editor["Textarea (Draft Prompt)"]
    end

    subgraph "agent/dashboard/review_style_jobs.py"
        SRSA["start_review_style_analysis()"]
        SYNC["sync_review_style_run_status()"]
    end

    subgraph "agent/dashboard/review_styles.py"
        SCP["set_custom_prompt()"]
        PUT["store.put_item()"]
    end

    Btn -->|POST /analyze| SRSA
    Editor -->|POST /save_prompt| SCP
    SRSA -->|Update Status| PUT
    SCP -->|Save Prompt| PUT
    SYNC -.->|Poll Status| PUT
```
Sources: [ui/src/components/ReviewStylesPanel.tsx:48-137](), [agent/dashboard/review_style_jobs.py:38-43](), [agent/dashboard/review_styles.py:138-145]()

## Prompt Injection

When the Reviewer Agent is invoked (e.g., via a GitHub PR comment), it retrieves the `custom_prompt` for the current repository. If a custom prompt exists, it is appended to the `REVIEWER_PROMPT_TEMPLATE`. This allows the agent to adopt repository-specific instructions such as:
*   "Prioritize security boundaries in this auth-heavy repo."
*   "Ignore style nits; only flag correctness regressions."
*   "Tone should be direct and cite specific line numbers."

This system bridges the gap between a generic LLM reviewer and a team-specific automated collaborator.

Sources: [agent/dashboard/review_styles.py:1-5](), [agent/review_style_guidance.py:3-17]()

---

# Page: Reviewer Evaluation Infrastructure

# Reviewer Evaluation Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/utils/model.py](agent/utils/model.py)
- [evals/reviewer/README.md](evals/reviewer/README.md)
- [evals/reviewer/build_dataset.py](evals/reviewer/build_dataset.py)
- [evals/reviewer/config.toml](evals/reviewer/config.toml)
- [evals/reviewer/golden_comments/cal_dot_com.json](evals/reviewer/golden_comments/cal_dot_com.json)
- [evals/reviewer/golden_comments/discourse.json](evals/reviewer/golden_comments/discourse.json)
- [evals/reviewer/golden_comments/grafana.json](evals/reviewer/golden_comments/grafana.json)
- [evals/reviewer/golden_comments/keycloak.json](evals/reviewer/golden_comments/keycloak.json)
- [evals/reviewer/golden_comments/sentry.json](evals/reviewer/golden_comments/sentry.json)
- [evals/reviewer/run_eval.py](evals/reviewer/run_eval.py)
- [evals/reviewer/target.py](evals/reviewer/target.py)
- [tests/test_anthropic_effort.py](tests/test_anthropic_effort.py)
- [tests/test_reviewer_eval_run.py](tests/test_reviewer_eval_run.py)
- [tests/test_reviewer_eval_target.py](tests/test_reviewer_eval_target.py)

</details>



The Reviewer Evaluation Infrastructure provides an offline framework for benchmarking the automated PR reviewer agent. It utilizes [LangSmith](https://smith.langchain.com/) to run the agent against a curated dataset of 50 pull requests, scoring the results using a high-fidelity LLM judge. This infrastructure allows developers to quantify the impact of changes to the reviewer's prompt, model, or tools without deploying to production.

## Infrastructure Overview

The evaluation system is located in the `evals/reviewer/` directory [evals/reviewer/README.md:10-17](). It follows a standard "Target-Dataset-Judge" pattern:

1.  **Target**: A wrapper that invokes the LangGraph reviewer assistant via the SDK [evals/reviewer/target.py:114-129]().
2.  **Dataset**: A collection of 50 real-world PRs from high-profile open-source repositories (Sentry, Keycloak, Grafana, Discourse, Cal.com), derived from the `withmartian/code-review-benchmark` [evals/reviewer/README.md:3-5]().
3.  **Judge**: An LLM-based evaluator (defaulting to `claude-opus-4-5`) that performs pairwise matching between agent findings and "golden" human-verified comments [evals/reviewer/judge.py:22-23]().

### Data Flow Diagram

The following diagram illustrates how the evaluation script coordinates between the local environment, the running LangGraph server, and LangSmith.

**Reviewer Evaluation Data Flow**
```mermaid
graph TD
    subgraph "Local Execution Space"
        RUN["evals/reviewer/run_eval.py"]
        CONFIG["evals/reviewer/config.toml"]
    end

    subgraph "LangSmith Cloud"
        DS[("Benchmark Dataset")]
        EXP["Experiment Results"]
    end

    subgraph "Code Entity Space"
        LG_SRV["LangGraph Server"]
        REV_AGENT["agent/reviewer.py"]
        TARGET["evals/reviewer/target.py:review_pr"]
        JUDGE["evals/reviewer/judge.py:judge_match"]
    end

    RUN -- "reads" --> CONFIG
    RUN -- "triggers" --> DS
    DS -- "inputs" --> TARGET
    TARGET -- "POST /runs" --> LG_SRV
    LG_SRV -- "executes" --> REV_AGENT
    REV_AGENT -- "returns add_finding calls" --> TARGET
    TARGET -- "returns comments" --> EXP
    EXP -- "pairwise match" --> JUDGE
    JUDGE -- "scores" --> EXP
```
Sources: [evals/reviewer/run_eval.py:129-170](), [evals/reviewer/target.py:114-129](), [evals/reviewer/README.md:1-17]()

## Target Invocation

The `review_pr` function serves as the entry point for LangSmith. It translates dataset examples into the input schema expected by the reviewer agent.

### Key Functions
- `_build_configurable`: Prepares the `configurable` dict, setting `reviewer_eval: True` to ensure the agent does not actually post comments to GitHub [evals/reviewer/target.py:91-111]().
- `_extract_comments`: Collects every `add_finding` tool call from the agent's message stream and normalizes them into a standard `{file, line, body, severity}` shape for the judge [evals/reviewer/target.py:131-164]().
- `drain_thread_ids`: Tracks created LangGraph threads so they can be deleted after the experiment finishes to save storage [evals/reviewer/target.py:38-48]().

### Configuration Mapping
The infrastructure allows overriding model parameters specifically for the eval via environment variables or `config.toml` [evals/reviewer/config.toml:1-18]():

| Config Key | Environment Variable | Purpose |
| :--- | :--- | :--- |
| `model_id` | `REVIEWER_EVAL_MODEL_ID` | Overrides the agent's LLM (e.g., `openai:gpt-4o`) [evals/reviewer/target.py:66-68]() |
| `reasoning_effort` | `REVIEWER_EVAL_REASONING_EFFORT` | Sets reasoning effort for models like O1/O3 [evals/reviewer/target.py:71-73]() |
| `score_mode` | `REVIEWER_EVAL_SCORE_MODE` | Switches between `all_findings` (raw output) and `surfaced_findings` (after thresholding) [evals/reviewer/target.py:59-63]() |

Sources: [evals/reviewer/target.py:1-164](), [evals/reviewer/run_eval.py:99-113]()

## Evaluation Components

### Benchmark Dataset
The dataset is built from JSON files in `evals/reviewer/golden_comments/` [evals/reviewer/README.md:11](). Each entry contains:
- Repository and PR number [evals/reviewer/target.py:92-99]().
- Base and Head SHAs for precise diffing [evals/reviewer/target.py:101-102]().
- "Golden" comments provided by human reviewers [evals/reviewer/golden_comments/cal_dot_com.json:1-15]().

### Judge Logic
The `judge_match` evaluator uses a high-capability model to determine if an agent's finding matches a golden comment. This is necessary because findings may be phrased differently but describe the same underlying bug [evals/reviewer/README.md:102-105]().

**Judge Interaction Logic**
```mermaid
sequenceDiagram
    participant LS as LangSmith
    participant J as judge.py:judge_match
    participant LLM as Claude-3.5-Opus
    
    LS->>J: inputs + agent_output + reference
    J->>LLM: "Does finding A match golden B?"
    LLM-->>J: JSON { match: true/false, reasoning: "..." }
    J->>LS: Score (0 or 1)
```
Sources: [evals/reviewer/judge.py:22-23](), [evals/reviewer/README.md:92-97]()

## Execution and Interpretation

### Running an Evaluation
To run a full benchmark, ensure a LangGraph server is running locally (usually on port 2024), then execute:

```bash
uv run python -m evals.reviewer.run_eval
```
[evals/reviewer/README.md:49]()

For faster iteration, use the `--limit` flag to test only a subset of PRs:
```bash
uv run python -m evals.reviewer.run_eval --limit 3
```
[evals/reviewer/README.md:55]()

### Interpreting Results
The evaluation produces two primary metrics in LangSmith:
1.  **Micro-averages**: Success rate across all individual findings.
2.  **Macro-averages**: Success rate aggregated at the PR level [evals/reviewer/README.md:92-97]().

If `score_mode` is set to `surfaced_findings`, the infrastructure applies the `filter_findings_for_publish` logic [evals/reviewer/target.py:172-176](), which uses the `severity_threshold` and `cap` defined in the configuration [evals/reviewer/config.toml:16-18](). This simulates production behavior where low-confidence or excessive findings are suppressed.

Sources: [evals/reviewer/run_eval.py:129-162](), [evals/reviewer/target.py:126-128](), [evals/reviewer/README.md:81-88]()

---

# Page: Customization Guide

# Customization Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CUSTOMIZATION.md](CUSTOMIZATION.md)
- [INSTALLATION.md](INSTALLATION.md)
- [README.md](README.md)

</details>



This guide explains how to extend and customize Open SWE for your organization's specific needs. All customization happens through a composable architecture where components can be swapped, extended, or replaced without modifying the core framework.

For detailed implementation guides on specific customization types, see:
- **[Custom Sandbox Providers](#9.1)** — Implementing new execution environments by implementing the `SandboxBackendProtocol`.
- **[Custom Tools](#9.2)** — Adding agent capabilities to the tool suite.
- **[Custom Middleware](#9.3)** — Extending agent behavior via `@before_model` and `@after_agent` hooks.
- **[Custom Triggers](#9.4)** — Creating new invocation surfaces beyond Slack, Linear, and GitHub.

## Architecture Overview

Open SWE's customization architecture centers on the `get_agent()` function in `agent/server.py`, which assembles all components into a working agent. This function is called by the LangGraph orchestration layer whenever a new agent run is needed.

### Agent Assembly Process

The following diagram illustrates how `get_agent()` composes the system by pulling from various configuration sources and passing them to `create_deep_agent`.

Title: Agent Composition Flow
```mermaid
graph TB
    subgraph "Invocation Layer [agent/webapp.py]"
        Webhook["Webhook Entry Point"]
        TaskDispatch["BackgroundTasks.add_task()"]
        RunsCreate["client.runs.create()"]
    end
    
    subgraph "Factory Layer [agent/server.py]"
        GetAgent["get_agent(config: RunnableConfig)"]
        ExtractConfig["Extract configurable:<br/>thread_id, repo, source"]
    end
    
    subgraph "Component Resolution"
        SandboxRes["create_sandbox()<br/>via SANDBOX_FACTORIES"]
        RepoRes["resolve_repo_dir()<br/>Clone/Pull logic"]
        ModelRes["make_model()<br/>LLM_MODEL_ID lookup"]
        PromptRes["construct_system_prompt()<br/>AGENTS.md injection"]
    end
    
    subgraph "Deep Agents Composition"
        CreateDeepAgent["create_deep_agent()"]
        ToolsArr["tools=[http_request, ...]<br/>[agent/tools/]"]
        MiddlewareArr["middleware=[open_pr_if_needed, ...]<br/>[agent/middleware/]"]
    end
    
    Webhook --> TaskDispatch
    TaskDispatch --> RunsCreate
    RunsCreate --> GetAgent
    GetAgent --> ExtractConfig
    ExtractConfig --> SandboxRes
    ExtractConfig --> RepoRes
    ExtractConfig --> ModelRes
    ExtractConfig --> PromptRes
    
    SandboxRes --> CreateDeepAgent
    RepoRes --> CreateDeepAgent
    ModelRes --> CreateDeepAgent
    PromptRes --> CreateDeepAgent
    ToolsArr --> CreateDeepAgent
    MiddlewareArr --> CreateDeepAgent
```
**Sources:** [agent/server.py:249-376](), [CUSTOMIZATION.md:1-24](), [agent/webapp.py:58-650]()

### Customization Points Table

| Component | Configuration Location | Factory/Registry | Implementation Files |
|-----------|----------------------|------------------|---------------------|
| **Sandbox** | `SANDBOX_TYPE` env var | `SANDBOX_FACTORIES` dict in `agent/utils/sandbox.py` | `agent/integrations/*.py` |
| **Model** | `get_agent()` in `agent/server.py` | `make_model()` helper | `agent/utils/model.py` |
| **Tools** | `get_agent()` in `agent/server.py` | `tools=[...]` array | `agent/tools/*.py` |
| **Middleware** | `get_agent()` in `agent/server.py` | `middleware=[...]` array | `agent/middleware/*.py` |
| **Triggers** | `agent/webapp.py` | FastAPI `@app.post` routes | `agent/webapp.py` |
| **System Prompt** | `agent/prompt.py` | `construct_system_prompt()` | `agent/prompt.py` |

**Sources:** [CUSTOMIZATION.md:1-407](), [agent/server.py:249-376](), [agent/utils/sandbox.py:9-15]()

## Sandbox Customization

Sandboxes provide isolated execution environments. The architecture uses a factory pattern where the `SANDBOX_TYPE` environment variable selects the provider.

### Sandbox Provider Mapping

The `SANDBOX_FACTORIES` dictionary maps environment variable values to creation functions.

Title: Sandbox Backend Resolution
```mermaid
graph LR
    Env["SANDBOX_TYPE Env Var"]
    Registry["SANDBOX_FACTORIES<br/>[agent/utils/sandbox.py]"]
    
    subgraph "Providers [agent/integrations/]"
        LS["langsmith.py"]
        DT["daytona.py"]
        RL["runloop.py"]
        MD["modal.py"]
        LC["local.py"]
    end
    
    subgraph "Code Entities"
        LS_Class["LangSmithProvider"]
        DT_Class["DaytonaSandbox"]
        MD_Class["ModalSandbox"]
    end
    
    Env --> Registry
    Registry --> LS & DT & RL & MD & LC
    LS --> LS_Class
    DT --> DT_Class
    MD --> MD_Class
```
**Sources:** [agent/utils/sandbox.py:9-15](), [CUSTOMIZATION.md:58-64](), [agent/integrations/__init__.py:1-8]()

### Sandbox Provider Requirements

All sandbox providers must implement the `SandboxBackendProtocol` from the `deepagents` framework. This requires implementing file operations (`ls`, `read`, `write`, `edit`, `glob`, `grep`) and shell execution (`execute`).

The easiest approach is extending `BaseSandbox` from `deepagents.backends.sandbox`, which implements file operations by delegating to `execute()`.

For detailed instructions on adding custom sandbox providers, see **[Custom Sandbox Providers](#9.1)**.

**Sources:** [CUSTOMIZATION.md:101-130]()

## Tool Customization

Open SWE ships with specialized tools like `commit_and_open_pr`, `linear_comment`, and `slack_thread_reply` on top of the built-in Deep Agents suite.

### Adding a Custom Tool

1. **Create tool file** in `agent/tools/` (e.g., `agent/tools/my_tool.py`).
2. **Define function** with a clear docstring; the LLM uses the docstring to understand when to invoke the tool.
3. **Register in server.py** by adding it to the `tools` list in `get_agent()`.

Tools have access to the LangGraph configuration via `get_config()` and the sandbox backend via `get_sandbox_backend_sync()`.

For detailed instructions and examples, see **[Custom Tools](#9.2)**.

**Sources:** [CUSTOMIZATION.md:173-251](), [agent/server.py:267-272]()

## Middleware Customization

Middleware provides deterministic hooks around the agent loop. Open SWE uses these for safety and state management.

### Middleware Types

| Middleware | Hook | Purpose |
|-----------|------|---------|
| `check_message_queue_before_model` | `@before_model` | Injects follow-up messages from webhooks mid-run. |
| `open_pr_if_needed` | `@after_agent` | Safety net that commits and opens a PR if the agent fails to do so. |
| `ToolErrorMiddleware` | Error Handler | Gracefully handles tool failures. |

Custom middleware can be added by defining functions with `@before_model` or `@after_agent` decorators and including them in the `middleware` list in `agent/server.py`.

For detailed instructions on writing custom middleware, see **[Custom Middleware](#9.3)**.

**Sources:** [CUSTOMIZATION.md:370-407](), [README.md:92-97](), [agent/middleware/open_pr.py:59-158]()

## Model Customization

The model is configured via `make_model()` in `agent/server.py`. While `openai:gpt-5.5` is the default, it can be overridden by the `LLM_MODEL_ID` environment variable.

### Dynamic Selection

The `make_model()` helper in `agent/utils/model.py` wraps `langchain.chat_models.init_chat_model`. You can route to different models based on context by modifying the logic in `get_agent()`.

For detailed instructions on model configuration, see **[Custom Sandbox Providers](#9.1)** (covered in Sandbox/Model context).

**Sources:** [CUSTOMIZATION.md:134-171](), [agent/server.py:255-265]()

## Trigger Customization

Triggers are FastAPI endpoints in `agent/webapp.py` that receive webhooks and dispatch agent runs.

### Creating a New Trigger

1. **Add Route**: Define a new `@app.post` endpoint in `agent/webapp.py`.
2. **Assemble Context**: Extract repo details, user info, and thread IDs.
3. **Dispatch Run**: Use the `LangGraphClient` to call `runs.create()`.

For detailed instructions on creating custom triggers, see **[Custom Triggers](#9.4)**.

**Sources:** [CUSTOMIZATION.md:252-349](), [agent/webapp.py:12-53]()

## System Prompt Customization

The system prompt is constructed in `agent/prompt.py`. It is modular, allowing you to edit specific sections like `CODING_STANDARDS_SECTION` or `COMMIT_PR_SECTION`.

### AGENTS.md Convention

Repository-specific instructions can be added via an `AGENTS.md` file at the root of the target repo. This file is automatically read and injected into the prompt, serving as the primary way to customize behavior per-project without changing code.

**Sources:** [README.md:79-85](), [CUSTOMIZATION.md:352-369]()

---

# Page: Custom Sandbox Providers

# Custom Sandbox Providers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/integrations/daytona.py](agent/integrations/daytona.py)
- [agent/integrations/local.py](agent/integrations/local.py)
- [agent/integrations/modal.py](agent/integrations/modal.py)
- [agent/integrations/runloop.py](agent/integrations/runloop.py)
- [agent/middleware/sandbox_circuit_breaker.py](agent/middleware/sandbox_circuit_breaker.py)
- [agent/middleware/tool_error_handler.py](agent/middleware/tool_error_handler.py)
- [agent/utils/sandbox.py](agent/utils/sandbox.py)
- [agent/utils/sandbox_paths.py](agent/utils/sandbox_paths.py)
- [agent/utils/sandbox_state.py](agent/utils/sandbox_state.py)
- [tests/middleware/test_sandbox_recovery.py](tests/middleware/test_sandbox_recovery.py)
- [tests/test_daytona_integration.py](tests/test_daytona_integration.py)

</details>



This document explains how to implement custom sandbox providers for Open SWE. A sandbox provider is a backend execution environment where the agent clones repositories and executes commands in isolation. Open SWE supports multiple providers (LangSmith, Modal, Daytona, Runloop, Local) through a pluggable architecture.

---

## Sandbox Provider Architecture

Open SWE uses a factory pattern to create sandbox backends. The `create_sandbox()` function reads the `SANDBOX_TYPE` environment variable and dispatches to the appropriate provider-specific factory function registered in `SANDBOX_FACTORIES`.

**Sandbox Provider Flow Diagram**
```mermaid
graph TB
    EnvVar["SANDBOX_TYPE<br/>environment variable"]
    CreateSandbox["create_sandbox()<br/>agent/utils/sandbox.py:20-37"]
    Registry["SANDBOX_FACTORIES<br/>agent/utils/sandbox.py:11-17"]
    
    subgraph "Factory Functions"
        LSFactory["create_langsmith_sandbox()<br/>agent/integrations/langsmith.py"]
        ModalFactory["create_modal_sandbox()<br/>agent/integrations/modal.py:9-26"]
        DaytonaFactory["create_daytona_sandbox()<br/>agent/integrations/daytona.py:17-29"]
        RunloopFactory["create_runloop_sandbox()<br/>agent/integrations/runloop.py:7-30"]
        LocalFactory["create_local_sandbox()<br/>agent/integrations/local.py:6-26"]
    end
    
    subgraph "Backend Implementations"
        LSBackend["LangSmithProvider<br/>agent/integrations/langsmith.py"]
        ModalBackend["ModalSandbox<br/>implements SandboxBackendProtocol"]
        DaytonaBackend["DaytonaSandbox<br/>implements SandboxBackendProtocol"]
        RunloopBackend["RunloopSandbox<br/>implements SandboxBackendProtocol"]
        LocalBackend["LocalShellBackend<br/>agent/integrations/local.py:23"]
    end
    
    EnvVar --> CreateSandbox
    CreateSandbox --> Registry
    Registry --> LSFactory
    Registry --> ModalFactory
    Registry --> DaytonaFactory
    Registry --> RunloopFactory
    Registry --> LocalFactory
    
    LSFactory --> LSBackend
    ModalFactory --> ModalBackend
    DaytonaFactory --> DaytonaBackend
    RunloopFactory --> RunloopBackend
    LocalFactory --> LocalBackend
```

**Sources:** [agent/utils/sandbox.py:11-37](), [agent/integrations/local.py:6-26](), [agent/integrations/daytona.py:17-29]()

---

## SandboxBackendProtocol Requirements

All sandbox providers must implement `SandboxBackendProtocol` from the `deepagents` framework. This protocol defines the standard interface that agent tools use to interact with the execution environment.

**Protocol Implementation Diagram**
```mermaid
classDiagram
    class SandboxBackendProtocol {
        <<interface>>
        +id: str
        +ls(path: str) LsResult
        +read(file_path: str, offset: int, limit: int) ReadResult
        +write(file_path: str, content: str) WriteResult
        +edit(file_path: str, old_string: str, new_string: str, replace_all: bool) EditResult
        +glob(pattern: str, path: str) GlobResult
        +grep(pattern: str, path: str, glob: str) GrepResult
        +execute(command: str, timeout: int) ExecuteResponse
        +upload_files(files: List) List~FileUploadResponse~
        +download_files(paths: List) List~FileDownloadResponse~
    }
    
    class SandboxBackendProxy {
        -SandboxBackendProtocol _backend
        +current: SandboxBackendProtocol
        +replace_backend(backend: SandboxBackendProtocol)
    }
    
    SandboxBackendProtocol <|.. SandboxBackendProxy
    SandboxBackendProtocol <|.. LocalShellBackend
    SandboxBackendProtocol <|.. DaytonaSandbox
```

**Required Methods (Synchronous and Asynchronous):**

The protocol requires both sync and async versions of file and execution operations (e.g., `ls` and `als`, `execute` and `aexecute`).

| Method | Purpose |
|--------|---------|
| `id` | Unique identifier for the sandbox instance [agent/utils/sandbox_state.py:38-39]() |
| `execute()` / `aexecute()` | Execute shell commands [agent/utils/sandbox_state.py:114-118]() |
| `ls()` / `als()` | List directory contents [agent/utils/sandbox_state.py:44-48]() |
| `read()` / `aread()` | Read file contents with offset/limit [agent/utils/sandbox_state.py:50-54]() |
| `write()` / `awrite()` | Write file contents [agent/utils/sandbox_state.py:78-82]() |
| `edit()` / `aedit()` | Apply string replacements [agent/utils/sandbox_state.py:84-100]() |
| `upload_files()` | Transfer files to sandbox [agent/utils/sandbox_state.py:102-106]() |
| `download_files()` | Retrieve files from sandbox [agent/utils/sandbox_state.py:108-112]() |

**Sources:** [agent/utils/sandbox_state.py:8-19](), [agent/utils/sandbox_state.py:27-120]()

---

## Implementation Approaches

### Approach 1: Using Stable Proxies

Open SWE uses a `SandboxBackendProxy` to maintain a stable handle for a thread even if the underlying sandbox is recreated due to a failure.

**Proxy Replacement Sequence**
```mermaid
sequenceDiagram
    participant Middleware as ToolErrorMiddleware
    participant Proxy as SandboxBackendProxy
    participant OldBackend as "Old Backend (sb-dead)"
    participant Server as agent.server._recreate_sandbox
    participant NewBackend as "New Backend (sb-new)"
    
    Middleware->>Proxy: execute(command)
    Proxy->>OldBackend: execute(command)
    OldBackend-->>Middleware: SandboxClientError
    
    Middleware->>Server: _recreate_sandbox(thread_id)
    Server->>NewBackend: Create()
    NewBackend-->>Server: backend instance
    Server->>Proxy: replace_backend(backend)
    
    Middleware->>Proxy: execute(command)
    Proxy->>NewBackend: execute(command)
```

**Sources:** [agent/utils/sandbox_state.py:27-42](), [agent/middleware/tool_error_handler.py:176-185](), [tests/middleware/test_sandbox_recovery.py:50-91]()

---

## Factory Function Pattern

Each sandbox provider must have a factory function that follows this signature:

| Element | Requirement |
|---------|-------------|
| Function name | `create_<provider>_sandbox` |
| Parameter | `sandbox_id: str | None = None` |
| Return type | Object implementing `SandboxBackendProtocol` |

**Example Factory Logic (Daytona):**
The factory validates the `DAYTONA_API_KEY`, then either retrieves an existing sandbox using `daytona.get(sandbox_id)` or creates a new one using `daytona.create()` with snapshot parameters.

**Sources:** [agent/integrations/daytona.py:17-29](), [agent/integrations/runloop.py:7-30]()

---

## Step-by-Step Implementation Guide

### Step 1: Create Integration File
Create `agent/integrations/my_provider.py`. If a LangChain wrapper exists for your provider (like `langchain_daytona`), use it to simplify implementation.

### Step 2: Register Factory
Add the new factory to `SANDBOX_FACTORIES` in `agent/utils/sandbox.py`.

```python
# agent/utils/sandbox.py
from agent.integrations.my_provider import create_my_provider_sandbox

SANDBOX_FACTORIES = {
    # ... existing ...
    "my_provider": create_my_provider_sandbox,
}
```

### Step 3: Startup Validation (Optional)
Add a validation check in `validate_sandbox_startup_config()` to ensure required environment variables are present before the server starts.

**Sources:** [agent/utils/sandbox.py:11-17](), [agent/utils/sandbox.py:40-52]()

---

## Sandbox Recovery and Circuit Breaking

Custom providers benefit from built-in recovery logic in `ToolErrorMiddleware`. If a `SandboxClientError` is raised during a tool call, the middleware:
1. Calls `_recreate_sandbox_for_thread` [agent/middleware/tool_error_handler.py:116-124]().
2. Updates the thread metadata with the new `sandbox_id` [agent/middleware/tool_error_handler.py:122]().
3. Notifies the LLM via a `ToolMessage` with `recovery: "sandbox_recreated_after_client_error"` [agent/middleware/tool_error_handler.py:73]().

To prevent infinite loops of failures, the `SandboxCircuitBreakerMiddleware` monitors the message history. If it detects more than `SANDBOX_CIRCUIT_BREAKER_THRESHOLD` (default 2) consecutive recreations or failures, it halts the agent and notifies the user.

**Sources:** [agent/middleware/tool_error_handler.py:159-204](), [agent/middleware/sandbox_circuit_breaker.py:24-28](), [agent/middleware/sandbox_circuit_breaker.py:67-102]()

---

## Working Directory Resolution

Tools need to know where the code is located inside the sandbox. The `resolve_sandbox_work_dir()` helper iterates through candidates:
1. Calling `get_work_dir()` on the backend object [agent/utils/sandbox_paths.py:63]().
2. Executing `pwd` via shell [agent/utils/sandbox_paths.py:68]().
3. Checking `get_user_home_dir()` [agent/utils/sandbox_paths.py:75]().

**Sources:** [agent/utils/sandbox_paths.py:34-51](), [agent/utils/sandbox_paths.py:58-86]()

---

# Page: Custom Tools

# Custom Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [Makefile](Makefile)
- [agent/middleware/exclude_tools.py](agent/middleware/exclude_tools.py)
- [agent/server.py](agent/server.py)
- [agent/tools/__init__.py](agent/tools/__init__.py)
- [agent/tools/fetch_url.py](agent/tools/fetch_url.py)
- [agent/tools/http_request.py](agent/tools/http_request.py)
- [evals/reviewer/judge.py](evals/reviewer/judge.py)
- [langgraph.json](langgraph.json)
- [tests/test_http_security.py](tests/test_http_security.py)

</details>



This page documents how to add, modify, and remove tools in the Open SWE agent's tool suite. Tools are Python functions that the agent can invoke to perform operations like API calls, file manipulations, or external system integrations.

For information about the complete tool system including built-in Deep Agents tools (`read_file`, `write_file`, etc.), see [Tool System](#3.2). For information about middleware that runs around tool execution, see [Middleware System](#3.3).

---

## Tool Architecture

Open SWE's tool system is built on three layers: tool definition, tool registration, and tool execution. Tools are standard Python functions with type hints and docstrings that are passed to `create_deep_agent()` during agent assembly.

### Tool Registration Flow

```mermaid
graph TB
    subgraph "Tool Definition Layer"
        ToolFile1["agent/tools/request_pr_review.py"]
        ToolFile2["agent/tools/fetch_url.py"]
        ToolFile3["agent/tools/http_request.py"]
        ToolFile4["agent/tools/linear_comment.py"]
        ToolFile5["agent/tools/slack_thread_reply.py"]
        ToolFile6["agent/tools/web_search.py"]
    end
    
    subgraph "Agent Assembly - agent/server.py"
        GetAgent["get_agent() function"]
        ToolImports["from .tools import<br/>request_pr_review,<br/>fetch_url, http_request,<br/>linear_comment,<br/>slack_thread_reply,<br/>web_search"]
        ToolsList["tools=[<br/>  http_request,<br/>  fetch_url,<br/>  request_pr_review,<br/>  linear_comment,<br/>  slack_thread_reply,<br/>  web_search<br/>]"]
        CreateAgent["create_deep_agent(<br/>  model=...,<br/>  system_prompt=...,<br/>  tools=tools,<br/>  backend=sandbox_backend,<br/>  middleware=...<br/>)"]
    end
    
    subgraph "Deep Agents Framework"
        AgentGraph["Pregel Agent Graph"]
        ToolNode["Tool Node"]
        LLM["LLM Model"]
    end
    
    subgraph "Runtime Execution"
        AgentCall["Agent invokes tool"]
        ToolExec["Tool function executes"]
        ContextAccess["get_config()"]
    end
    
    ToolFile1 --> GetAgent
    ToolFile2 --> GetAgent
    ToolFile3 --> GetAgent
    ToolFile4 --> GetAgent
    ToolFile5 --> GetAgent
    ToolFile6 --> GetAgent
    
    GetAgent --> ToolImports
    ToolImports --> ToolsList
    ToolsList --> CreateAgent
    
    CreateAgent --> AgentGraph
    AgentGraph --> ToolNode
    AgentGraph --> LLM
    
    LLM --> AgentCall
    AgentCall --> ToolExec
    ToolExec --> ContextAccess
```

**Sources:** [agent/server.py:55-69](), [agent/server.py:249-376](), [agent/tools/__init__.py:1-37]()

---

## Tool Function Structure

Tools are Python functions with specific conventions that allow the LLM to understand their purpose and parameters.

### Anatomy of a Tool

```mermaid
graph TB
    subgraph "Tool Function Components"
        FuncSig["Function Signature<br/>def tool_name(param1: type1, param2: type2) -> ReturnType"]
        Docstring["Docstring<br/>- Purpose description<br/>- Usage instructions<br/>- Parameter docs<br/>- Return value docs"]
        TypeHints["Type Hints<br/>Used by LLM to understand<br/>parameter types"]
        Implementation["Implementation<br/>- Access context via get_config()<br/>- Perform operation<br/>- Return structured result"]
    end
    
    subgraph "LLM Visibility"
        ToolName["Tool Name<br/>Extracted from function name"]
        ToolDesc["Tool Description<br/>Extracted from docstring"]
        ToolParams["Tool Parameters<br/>Extracted from type hints"]
    end
    
    FuncSig --> ToolName
    Docstring --> ToolDesc
    TypeHints --> ToolParams
    
    FuncSig --> Implementation
    Docstring --> Implementation
    TypeHints --> Implementation
```

### Example Tool Structure: Fetch URL

The `fetch_url` tool demonstrates the standard structure using safe redirect logic and markdown conversion:

```python
def fetch_url(url: str, timeout: int = 30) -> dict[str, Any]:
    """Fetch content from a URL and convert HTML to markdown format.

    This tool fetches web page content and converts it to clean markdown text,
    making it easy to read and process HTML content. After receiving the markdown,
    you MUST synthesize the information into a natural, helpful response for the user.

    Args:
        url: The URL to fetch (must be a valid HTTP/HTTPS URL)
        timeout: Request timeout in seconds (default: 30)

    Returns:
        Dictionary containing:
        - success: Whether the request succeeded
        - url: The final URL after redirects
        - markdown_content: The page content converted to markdown
        - status_code: HTTP status code
        - content_length: Length of the markdown content in characters
    """
```

**Key conventions:**

| Element | Convention |
|---------|-----------|
| Function name | Lowercase with underscores, descriptive verb phrase |
| Parameters | Type-hinted, required parameters first |
| Return type | Structured dict or primitive type, always type-hinted |
| Docstring | First line is imperative summary, followed by usage details |
| Security | Use `_request_with_safe_redirects` for HTTP calls to prevent SSRF |

**Sources:** [agent/tools/fetch_url.py:9-33](), [agent/tools/http_request.py:180-210]()

---

## Security: HTTP and DNS Pinning

Custom tools that perform network requests must adhere to the system's security policies. Open SWE implements a DNS pinning mechanism to prevent DNS-rebinding attacks and SSRF.

### Safe Request Flow

```mermaid
graph TB
    subgraph "Security Layer - agent/tools/http_request.py"
        ToolCall["fetch_url / http_request"]
        ResolveValidate["_resolve_and_validate(url)"]
        IPCheck["Check if Private/Loopback/Reserved"]
        PinDNS["_pin_dns(hostname, addr_infos)"]
        SafeRequest["_request_with_safe_redirects"]
        Urllib3Patch["urllib3_connection.create_connection = _pinned_create_connection"]
    end

    subgraph "Execution"
        RealRequest["requests.request(...)"]
        DNSHonoring["_pinned_create_connection uses pinned IP"]
    end

    ToolCall --> SafeRequest
    SafeRequest --> ResolveValidate
    ResolveValidate --> IPCheck
    IPCheck -- "Safe" --> PinDNS
    PinDNS --> Urllib3Patch
    Urllib3Patch --> RealRequest
    RealRequest --> DNSHonoring
```

**Sources:** [agent/tools/http_request.py:125-161](), [agent/tools/http_request.py:180-210](), [tests/test_http_security.py:143-180]()

---

## Registering Tools in the Agent

Tools are registered by passing them to `create_deep_agent()` in the `get_agent()` function in `agent/server.py`.

### Adding a Custom Tool

**Step 1: Create the tool file**
Create `agent/tools/my_custom_tool.py`.

**Step 2: Export in the tools package**
Add the tool to [agent/tools/__init__.py]().

**Step 3: Register in server.py**
Modify [agent/server.py]():

```python
from .tools import my_custom_tool  # Add import

async def get_agent(config: RunnableConfig) -> Pregel:
    # ... setup code ...
    
    return create_deep_agent(
        # ...
        tools=[
            http_request,
            fetch_url,
            request_pr_review,
            linear_comment,
            slack_thread_reply,
            web_search,
            my_custom_tool,  # Add to tools list
        ],
        # ...
    )
```

**Sources:** [agent/server.py:55-69](), [agent/server.py:249-376](), [agent/tools/__init__.py:1-37]()

---

## Removing Tools

Tools can be removed globally by deleting them from the `tools` list in `get_agent()`, or dynamically via middleware.

### Dynamic Removal via Middleware

The `ExcludeToolsMiddleware` allows hiding specific tools from the model without rebuilding the agent. This is used by the Reviewer agent to disable subagent spawning via the `task` tool.

```python
# agent/middleware/exclude_tools.py
class ExcludeToolsMiddleware(AgentMiddleware):
    def __init__(self, *, excluded: frozenset[str]) -> None:
        self._excluded = excluded

    def _filter(self, request: ModelRequest) -> ModelRequest:
        filtered = [t for t in request.tools if _tool_name(t) not in self._excluded]
        return request.override(tools=filtered)
```

**Sources:** [agent/middleware/exclude_tools.py:33-51](), [agent/server.py:49]()

---

## Tool Inventory

Open SWE includes several custom tools out-of-the-box for integration and discovery:

| Tool Name | File Path | Purpose |
|-----------|-----------|---------|
| `fetch_url` | [agent/tools/fetch_url.py]() | Fetches URL and converts HTML to Markdown |
| `http_request` | [agent/tools/http_request.py]() | Performs secure authenticated HTTP requests |
| `linear_comment` | [agent/tools/linear_comment.py]() | Posts comments to Linear issues |
| `slack_thread_reply` | [agent/tools/slack_thread_reply.py]() | Replies to Slack conversation threads |
| `web_search` | [agent/tools/web_search.py]() | Performs web searches via Exa API |
| `request_pr_review` | [agent/tools/request_pr_review.py]() | Triggers the Reviewer agent on a PR |
| `add_finding` | [agent/tools/add_finding.py]() | (Reviewer Only) Records a code review finding |

**Sources:** [agent/tools/__init__.py:1-37](), [agent/server.py:55-69]()

---

# Page: Custom Middleware

# Custom Middleware

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/middleware/__init__.py](agent/middleware/__init__.py)
- [agent/middleware/notify_step_limit.py](agent/middleware/notify_step_limit.py)
- [agent/middleware/sanitize_tool_inputs.py](agent/middleware/sanitize_tool_inputs.py)
- [tests/test_notify_step_limit_middleware.py](tests/test_notify_step_limit_middleware.py)
- [tests/test_sanitize_tool_inputs.py](tests/test_sanitize_tool_inputs.py)

</details>



This page explains how to write custom middleware to extend agent behavior in Open SWE. Middleware functions run around the agent execution loop, allowing you to inject logic before the model is called, intercept tool calls, or execute logic after the agent completes. This enables patterns like input sanitization, safety nets, real-time message injection, and automated notifications.

---

## Middleware Architecture

Middleware in Open SWE runs at specific points in the agent execution lifecycle. The system uses decorators and class-based interfaces to define when logic executes within the `create_deep_agent` orchestration.

### Agent Lifecycle with Middleware Hooks

The following diagram illustrates how middleware hooks intercept the natural language processing and tool execution flow.

```mermaid
graph TB
    subgraph "Natural Language Space"
        Start["Agent Run Started"]
        BeforeModel["@before_model Middleware<br/>(check_message_queue_before_model)"]
        ModelCall["LLM Model Call"]
        AfterAgent["@after_agent Middleware<br/>(notify_step_limit_reached)"]
        End["Agent Run Complete"]
    end

    subgraph "Code Entity Space"
        ToolWrap["wrap_tool_call Middleware<br/>(SanitizeToolInputsMiddleware)"]
        ToolExec["Tool Execution<br/>(SandboxBackendProtocol)"]
        SlackOps["Slack Notifications<br/>(post_slack_thread_reply)"]
    end
    
    Start --> BeforeModel
    BeforeModel --> ModelCall
    ModelCall --> ToolWrap
    ToolWrap --> ToolExec
    ToolExec --> ModelCall
    ModelCall --> AfterAgent
    AfterAgent --> SlackOps
    SlackOps --> End
```

**Sources:**
- [agent/middleware/__init__.py:1-21]()
- [agent/middleware/notify_step_limit.py:37-46]()
- [agent/middleware/sanitize_tool_inputs.py:54-61]()

---

## Middleware Execution Points

Open SWE supports three primary types of middleware hooks:

| Hook Type | Implementation | When It Runs | Common Use Cases |
|-----------|----------------|--------------|------------------|
| **Before Model** | `@before_model` | Before each LLM call | Message injection, state validation, context modification |
| **Tool Wrapper** | `AgentMiddleware` | Around tool execution | Input sanitization, error handling, tool exclusion |
| **After Agent** | `@after_agent` | Once after agent completes | Notifications, safety nets, cleanup, result validation |

The middleware stack is exported in `agent/middleware/__init__.py` and configured during agent assembly.

**Sources:**
- [agent/middleware/__init__.py:11-21]()
- [agent/middleware/sanitize_tool_inputs.py:76-81]()

---

## Writing Custom Middleware

### Before Model Middleware

Before-model middleware runs before each LLM call and can modify the agent state. The function receives `AgentState` and `Runtime` objects.

**Function Signature:**

```python
from langchain.agents.middleware import AgentState, before_model
from langgraph.runtime import Runtime

@before_model
async def my_before_middleware(
    state: AgentState,
    runtime: Runtime,
) -> dict[str, Any] | None:
    """Execute logic before the model is called."""
    # Your logic here
    return None  # or {"messages": [...]}
```

The `check_message_queue_before_model` middleware demonstrates this by injecting queued messages from the thread's message queue before the next model call to handle concurrent user inputs.

**Sources:**
- [agent/middleware/check_message_queue.py:1-20]() (referenced via [agent/middleware/__init__.py:18-18]())

### Tool Wrapper Middleware

Tool wrapper middleware inherits from `AgentMiddleware` and implements `wrap_tool_call` (synchronous) and `awrap_tool_call` (asynchronous). This allows intercepting `ToolCallRequest` objects before they reach the sandbox.

**Implementation Example: `SanitizeToolInputsMiddleware`**
This middleware intercepts `read_file` calls to coerce malformed string arguments (e.g., `"1, 80"`) into valid integers for `offset` and `limit` fields [agent/middleware/sanitize_tool_inputs.py:54-61]().

```python
# agent/middleware/sanitize_tool_inputs.py
class SanitizeToolInputsMiddleware(AgentMiddleware):
    def wrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command],
    ) -> ToolMessage | Command:
        # Sanitize request before passing to handler
        return handler(self._sanitize_request(request))
```

**Sources:**
- [agent/middleware/sanitize_tool_inputs.py:54-81]()

### After Agent Middleware

After-agent middleware runs once after the agent finishes execution. This is useful for notifications or ensuring repository state is consistent.

**Implementation Example: `notify_step_limit_reached`**
This middleware checks if the last message contains a limit marker (e.g., "Model call limits exceeded") and posts a Slack reply to notify the user [agent/middleware/notify_step_limit.py:37-55]().

```python
# agent/middleware/notify_step_limit.py
@after_agent
async def notify_step_limit_reached(state: AgentState, runtime: Runtime):
    messages = state.get("messages", [])
    if not messages: return None
    
    # Check for limit marker in content
    if _LIMIT_MARKER in _content_to_text(messages[-1].content):
        config = get_config()
        # Send Slack notification using thread metadata
        await post_slack_thread_reply(...)
```

**Sources:**
- [agent/middleware/notify_step_limit.py:37-88]()

---

## Accessing Context in Middleware

Middleware functions can access thread-level configuration and persisted metadata via `get_config()`.

### Thread Configuration and Metadata

```python
from langgraph.config import get_config

config = get_config()
configurable = config.get("configurable", {})
# Access Slack thread details for notifications
slack_thread = configurable.get("slack_thread", {})
channel_id = slack_thread.get("channel_id")
thread_ts = slack_thread.get("thread_ts")
```

**Sources:**
- [agent/middleware/notify_step_limit.py:57-65]()

---

## Data Flow: Input Sanitization

This diagram maps how `SanitizeToolInputsMiddleware` bridges the gap between LLM output and valid tool execution.

```mermaid
graph TD
    LLM["LLM Generates Tool Call<br/>(read_file offset='1, 80')"] --> Middleware["SanitizeToolInputsMiddleware<br/>(agent/middleware/sanitize_tool_inputs.py)"]
    Middleware --> Coerce["_coerce_int('1, 80') -> 1<br/>(agent/middleware/sanitize_tool_inputs.py)"]
    Coerce --> Handler["Tool Handler<br/>(langgraph.prebuilt.tool_node)"]
    Handler --> Sandbox["Sandbox Execution<br/>(SandboxBackendProtocol)"]
```

**Sources:**
- [agent/middleware/sanitize_tool_inputs.py:25-39]()
- [agent/middleware/sanitize_tool_inputs.py:65-74]()

---

## Error Handling in Middleware

Middleware must handle exceptions internally to prevent interrupting the core agent response delivery. For instance, if a Slack notification fails in `notify_step_limit_reached`, it logs the error but allows the agent run to finish [agent/middleware/notify_step_limit.py:82-86]().

```python
try:
    await post_slack_thread_reply(channel_id, thread_ts, message)
except Exception:
    logger.exception("Failed to send step-limit notification")
return None
```

**Sources:**
- [agent/middleware/notify_step_limit.py:82-88]()

---

# Page: Custom Triggers

# Custom Triggers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CUSTOMIZATION.md](CUSTOMIZATION.md)
- [INSTALLATION.md](INSTALLATION.md)
- [README.md](README.md)
- [agent/webapp.py](agent/webapp.py)
- [tests/test_github_issue_webhook.py](tests/test_github_issue_webhook.py)

</details>



This guide explains how to create custom webhook endpoints to trigger Open SWE agents from new platforms beyond the built-in Slack, Linear, and GitHub integrations. This enables you to invoke agents from any external system that can send HTTP requests.

For information about the existing Slack, Linear, and GitHub integrations, see **2. Invocation Surfaces**. For adding custom tools that agents can use during execution, see **9.2 Custom Tools**.

---

## Overview

**Triggers** are the entry points that initiate agent runs. Open SWE receives webhook events from external platforms, parses them into structured tasks, and dispatches agent runs to the LangGraph server. Each trigger:

1.  Receives an HTTP POST request containing event data at an endpoint defined in `agent/webapp.py` [agent/webapp.py:101-115]().
2.  Verifies the request signature (optional but recommended) via utilities like `verify_github_signature` [agent/utils/github_comments.py:57-57]() or `verify_slack_signature` [agent/utils/slack.py:83-83]().
3.  Extracts task description and repository context using `extract_repo_from_text` [agent/utils/repo.py:65-65]().
4.  Generates a deterministic thread ID for conversation continuity (e.g., `get_thread_id_from_branch` [agent/utils/github_comments.py:53-53]()).
5.  Creates a LangGraph run with appropriate configuration via `langgraph_sdk.get_client` [agent/webapp.py:17-18]().
6.  Returns an acknowledgment to the caller.

The webhook processing flow is asynchronous—the HTTP response is sent immediately while the agent runs in the background using FastAPI's `BackgroundTasks` [agent/webapp.py:14-14]().

### Trigger Data Flow: Natural Language to Code Entity Space

The following diagram shows how an external event is transformed into a LangGraph `run` entity.

```mermaid
graph TD
    subgraph "External Event Space"
        A["External Webhook Event<br/>(Jira/Discord/etc)"]
    end

    subgraph "FastAPI Route Space (agent/webapp.py)"
        B["@app.post('/webhooks/custom')"]
        C["verify_signature()"]
        D["BackgroundTasks.add_task()"]
    end

    subgraph "Context Assembly Space"
        E["extract_repo_from_text()"]
        F["Deterministic thread_id generation"]
        G["resolve_github_token_from_email()"]
    end

    subgraph "LangGraph Entity Space"
        H["LangGraphClient.runs.create()"]
        I["thread_id (Deterministic)"]
        J["config['configurable']"]
    end

    A --> B
    B --> C
    C --> D
    D --> E
    D --> F
    D --> G
    E & F & G --> H
    H --> I
    H --> J

    style B fill:none
    style H fill:none
```

**Sources:** [agent/webapp.py:101-120](), [agent/utils/repo.py:65-65](), [agent/utils/auth.py:37-37](), [agent/utils/github_comments.py:53-53]()

---

## Webhook Endpoint Architecture

All triggers are implemented as FastAPI endpoints in `agent/webapp.py`. The application uses the following core components to manage the lifecycle of a trigger:

| Component | Role | Code Reference |
| :--- | :--- | :--- |
| `app` | FastAPI instance hosting routes | [agent/webapp.py:101-101]() |
| `BackgroundTasks` | Dispatches processing to avoid HTTP timeouts | [agent/webapp.py:14-14]() |
| `LangGraphClient` | SDK client to communicate with the agent graph | [agent/webapp.py:18-18]() |
| `get_client()` | Factory to initialize the SDK client | [agent/webapp.py:17-17]() |

### Webhook Reception Logic

The following diagram maps the logical flow of a webhook request to the specific functions in the codebase.

```mermaid
sequenceDiagram
    participant E as "External Platform"
    participant W as "agent/webapp.py<br/>(FastAPI Route)"
    participant U as "agent/utils/auth.py<br/>(Auth Utilities)"
    participant L as "LangGraph Server"

    E->>W: POST /webhooks/custom
    W->>W: Verify Signature (HMAC)
    W->>U: resolve_github_token_from_email()
    W->>W: background_tasks.add_task(process_event)
    W-->>E: 202 Accepted / 200 OK
    
    Note over W, L: Asynchronous Processing
    W->>L: client.runs.create(thread_id, input, config)
```

**Sources:** [agent/webapp.py:14-18](), [agent/utils/auth.py:37-37](), [agent/webapp.py:115-125]()

---

## Creating a Custom Trigger

### 1. Define the Route and Payload Parsing

New routes should be added to `agent/webapp.py`. The endpoint must extract the task and repository context. Open SWE provides `extract_repo_from_text` to find repository details within strings or URLs [agent/utils/repo.py:65-65]().

```python
# Example logic inspired by agent/webapp.py
@app.post("/webhooks/custom")
async def custom_webhook(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()
    # 1. Extract context
    text = payload.get("text", "")
    repo_config = extract_repo_from_text(text) or {
        "owner": os.environ["DEFAULT_REPO_OWNER"],
        "name": os.environ["DEFAULT_REPO_NAME"]
    }
    # 2. Dispatch
    background_tasks.add_task(process_custom_task, payload, repo_config)
    return {"status": "accepted"}
```

**Sources:** [agent/webapp.py:115-125](), [agent/utils/repo.py:65-65]()

### 2. Generate a Deterministic Thread ID

Thread IDs are crucial for state persistence. If a user replies to a message, the trigger must generate the same `thread_id` to reconnect to the existing sandbox and conversation state. Open SWE uses specific generation logic per platform:

| Source | ID Generation Logic | Code Reference |
| :--- | :--- | :--- |
| **Linear** | Deterministic hash from issue ID | [agent/webapp.py:200-218]() |
| **GitHub** | Derived from branch name | [agent/utils/github_comments.py:53-53]() |
| **Slack** | Thread-specific metadata mapping | [agent/utils/slack.py:81-81]() |

**Sources:** [agent/webapp.py:200-218](), [agent/utils/github_comments.py:53-53](), [agent/utils/slack.py:81-81]()

### 3. Configure the LangGraph Run

The `config` dictionary passed to the agent must contain the `configurable` block. This block is used by `get_agent()` in `agent/server.py` to set up the environment.

Required keys in `config["configurable"]`:
- `repo`: A dict with `owner` and `name` [agent/webapp.py:175-179]().
- `user_email`: Used to resolve GitHub OAuth tokens via `resolve_github_token_from_email` [agent/utils/auth.py:37-37]().
- `source`: The trigger source metadata (e.g., "slack", "linear", "github") [agent/webapp.py:29-31]().

**Sources:** [agent/webapp.py:175-198](), [agent/utils/auth.py:37-37](), [CUSTOMIZATION.md:12-23]()

---

## Repository Resolution Strategies

When creating a custom trigger, you must decide how to map the incoming event to a GitHub repository.

### Mapping via Config (Linear Style)
Use a mapping utility like `get_repo_config_from_team_mapping` [agent/webapp.py:175-177]() which looks up configurations in `LINEAR_TEAM_TO_REPO` [agent/utils/linear_team_repo_map.py:63-63]().

### Mapping via Text Extraction (Slack Style)
Use `extract_repo_from_text` to allow users to specify the repository in the trigger message (e.g., "fix this in repo:owner/name") [agent/utils/repo.py:65-65]().

### Default Fallbacks
If no repository is specified, fall back to `DEFAULT_REPO_OWNER` and `DEFAULT_REPO_NAME` defined in environment variables [agent/webapp.py:122-123]().

**Sources:** [agent/webapp.py:122-125](), [agent/webapp.py:175-198](), [agent/utils/repo.py:65-65]()

---

## Security: Signature Verification

To ensure that only authorized platforms can trigger your agent, implement signature verification. 

- **GitHub**: Uses `verify_github_signature` with `GITHUB_WEBHOOK_SECRET` [agent/utils/github_comments.py:57-57]().
- **Slack**: Uses `verify_slack_signature` with `SLACK_SIGNING_SECRET` [agent/utils/slack.py:83-83]().
- **Linear**: Verified via `LINEAR_WEBHOOK_SECRET` and HMAC hashing [agent/webapp.py:117-118]().

When implementing a custom trigger, you should use `hmac.new` and `hexdigest` to validate incoming signatures against your secrets [agent/webapp.py:3-5]().

**Sources:** [agent/webapp.py:3-5](), [agent/utils/github_comments.py:57-57](), [agent/utils/slack.py:83-83]()

---

# Page: Dashboard and UI

# Dashboard and UI

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/dashboard/profiles.py](agent/dashboard/profiles.py)
- [agent/dashboard/routes.py](agent/dashboard/routes.py)
- [ui/src/lib/api.ts](ui/src/lib/api.ts)
- [ui/src/routeTree.gen.ts](ui/src/routeTree.gen.ts)

</details>



The Open SWE Dashboard provides a centralized web interface for managing agent threads, configuring user profiles, and adjusting team-wide settings. It consists of a React-based frontend and a FastAPI backend that integrates with the LangGraph Store for persistence.

### System Overview

The dashboard bridges the gap between the automated agent execution (triggered via webhooks) and human oversight. It allows users to manually trigger agent runs, view real-time logs, and manage repository-specific review styles.

#### Dashboard Component Relationship
The following diagram illustrates how the dashboard components interact with the underlying system entities.

**Entity Mapping: Dashboard to Codebase**
```mermaid
graph TD
    subgraph "Natural Language Space"
        "User Interface"
        "API Layer"
        "Persistence"
    end

    subgraph "Code Entity Space"
        UI["React Frontend (TanStack Router)"]
        API["FastAPI Router (agent/dashboard/routes.py)"]
        STORE["LangGraph Store (profiles/oauth_tokens namespaces)"]
        
        UI -- "Calls" --> API
        API -- "CRUD" --> STORE
    end

    "User Interface" -.-> UI
    "API Layer" -.-> API
    "Persistence" -.-> STORE
```
Sources: [agent/dashboard/routes.py:78-78](), [agent/dashboard/profiles.py:31-32](), [ui/src/lib/api.ts:141-190]()

---

### Dashboard Backend
The backend is implemented as a FastAPI router located at `agent/dashboard/routes.py`. It handles:
*   **Authentication**: Implements a GitHub OAuth flow using `auth_login` and `auth_callback` endpoints [agent/dashboard/routes.py:144-196]().
*   **Session Management**: Issues secure JWT-based sessions stored in the `osw_session` cookie [agent/dashboard/routes.py:111-120]().
*   **REST API**: Exposes endpoints under `/dashboard/api` for managing threads, profiles, and team settings [agent/dashboard/routes.py:78-78]().

For details, see [Dashboard Backend](#10.1).

Sources: [agent/dashboard/routes.py:1-74]()

---

### Dashboard Frontend
The frontend is a modern React application utilizing **TanStack Router** for type-safe routing and **TanStack Query** for data fetching.
*   **Route Structure**: Organized into functional areas such as `/agents` for thread management, `/review` for repository configurations, and `/admin` for team-wide overrides [ui/src/routeTree.gen.ts:86-112]().
*   **API Client**: A typed `api` object in `ui/src/lib/api.ts` handles communication with the backend, including automatic credential handling for session cookies [ui/src/lib/api.ts:141-190]().

For details, see [Dashboard Frontend](#10.2).

Sources: [ui/src/routeTree.gen.ts:11-24](), [ui/src/lib/api.ts:1-48]()

---

### User Profiles and Team Settings
Open SWE uses the **LangGraph Store** to persist configuration across two primary namespaces: `profiles` and `oauth_tokens` [agent/dashboard/profiles.py:31-32]().
*   **User Profiles**: Individual settings including `default_model`, `reasoning_effort`, and `branch_prefix` [agent/dashboard/profiles.py:35-43]().
*   **Team Settings**: Global configurations managed by admins, such as `trigger_mode` (e.g., `every_push`, `manual`) and `autofix_mode` [ui/src/lib/api.ts:89-103]().
*   **Review Styles**: Per-repository settings that allow the Reviewer Agent to adapt to specific coding standards [ui/src/lib/api.ts:123-139]().

For details, see [User Profiles and Team Settings](#10.3).

Sources: [agent/dashboard/profiles.py:1-11](), [ui/src/lib/api.ts:64-103]()

---

### Agent Threads UI
The `agents/` route provides a high-fidelity view into agent activities. It enables users to:
*   **Monitor Runs**: View real-time progress of LangGraph threads via the `stream_dashboard_thread` endpoint [agent/dashboard/routes.py:73-73]().
*   **Interactive Chat**: Use the `AgentPromptBar` to send manual instructions to an agent within a specific thread context [agent/dashboard/routes.py:72-72]().
*   **Code Inspection**: View diffs and file changes through ported components like `AgentGitPanel`.

**Data Flow: Thread Interaction**
```mermaid
sequenceDiagram
    participant User as "Dashboard UI"
    participant API as "FastAPI (thread_api.py)"
    participant LG as "LangGraph SDK"

    User->>API: send_dashboard_message(thread_id, text)
    API->>LG: runs.create(thread_id, input)
    LG-->>API: run_id
    API-->>User: StreamingResponse (events)
```
Sources: [agent/dashboard/routes.py:72-73](), [agent/dashboard/thread_api.py:1-10]()

For details, see [Agent Threads UI](#10.4).

Sources: [agent/dashboard/routes.py:64-74](), [ui/src/routeTree.gen.ts:108-110]()

---

# Page: Dashboard Backend

# Dashboard Backend

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/_patch_messages_reducer.py](agent/_patch_messages_reducer.py)
- [agent/dashboard/message_adapter.py](agent/dashboard/message_adapter.py)
- [agent/dashboard/oauth.py](agent/dashboard/oauth.py)
- [agent/dashboard/review_style_jobs.py](agent/dashboard/review_style_jobs.py)
- [agent/dashboard/review_styles.py](agent/dashboard/review_styles.py)
- [agent/dashboard/routes.py](agent/dashboard/routes.py)
- [agent/dashboard/thread_api.py](agent/dashboard/thread_api.py)
- [agent/review_style_analyzer.py](agent/review_style_analyzer.py)
- [agent/utils/thread_ops.py](agent/utils/thread_ops.py)
- [tests/test_github_oauth_refresh.py](tests/test_github_oauth_refresh.py)
- [tests/test_review_style_sync.py](tests/test_review_style_sync.py)
- [ui/src/components/ReviewStylesPanel.tsx](ui/src/components/ReviewStylesPanel.tsx)
- [ui/src/routeTree.gen.ts](ui/src/routeTree.gen.ts)

</details>



The Dashboard Backend is a FastAPI-based service that provides the administrative and user-facing API for managing Open SWE agents, review styles, and user profiles. It acts as a bridge between the React frontend and the underlying LangGraph execution engine.

## Overview and Purpose

The dashboard backend handles four primary responsibilities:
1.  **Authentication**: Managing GitHub App OAuth flows and session persistence via signed JWTs.
2.  **Thread Management**: Proxying requests to the LangGraph SDK to list, create, and stream agent runs.
3.  **Review Style Management**: Orchestrating the "Review Style Analyzer" graph which researches repository history to synthesize custom review prompts.
4.  **Profile & Settings**: Managing per-user and team-wide configurations stored in the LangGraph Store.

## Architecture and Data Flow

The backend is organized as a series of routers and utility modules that interact with the LangGraph SDK and the GitHub API.

### Authentication Flow
The system uses a stateful OAuth flow to bind GitHub identities to local sessions. It employs a double-cookie strategy (Session + State) to prevent CSRF and session fixation.

**Login Sequence:**
1.  User initiates login at `/dashboard/api/auth/login` [agent/dashboard/routes.py:144-162]().
2.  The backend generates a random nonce and a state JWT containing a hash of that nonce [agent/dashboard/oauth.py:102-126]().
3.  User is redirected to GitHub. Upon return to `/dashboard/api/auth/callback`, the backend verifies the state JWT and the nonce cookie [agent/dashboard/routes.py:165-177]().
4.  The authorization code is exchanged for a GitHub token [agent/dashboard/oauth.py:171-182]().
5.  A session JWT is issued and stored in a secure, `HttpOnly` cookie [agent/dashboard/routes.py:192-196]().

### Component Interaction Diagram
This diagram shows how the FastAPI routes connect to specific code entities and external services.

"Dashboard Backend Entity Map"
```mermaid
graph TD
    subgraph "FastAPI Router [agent/dashboard/routes.py]"
        R_AUTH["/auth/*"]
        R_THREADS["/threads/*"]
        R_STYLE["/review/styles/*"]
        R_ME["/me & /profile"]
    end

    subgraph "Auth Logic [agent/dashboard/oauth.py]"
        EXCHANGE["exchange_code()"]
        ISSUE["issue_session()"]
    end

    subgraph "Thread Logic [agent/dashboard/thread_api.py]"
        CREATE["create_dashboard_thread()"]
        LIST["list_dashboard_threads()"]
        ADAPTER["state_messages_to_ui()"]
    end

    subgraph "Review Logic [agent/dashboard/review_style_jobs.py]"
        START_ANALYSIS["start_review_style_analysis()"]
        SYNC_STATUS["sync_review_style_run_status()"]
    end

    LG_SDK["langgraph_sdk.get_client()"]
    GH_API["GitHub API"]

    R_AUTH --> EXCHANGE
    EXCHANGE --> GH_API
    R_AUTH --> ISSUE
    
    R_THREADS --> LIST
    R_THREADS --> CREATE
    LIST --> LG_SDK
    CREATE --> LG_SDK
    CREATE -.-> ADAPTER
    
    R_STYLE --> START_ANALYSIS
    START_ANALYSIS --> LG_SDK
```
Sources: [agent/dashboard/routes.py:78-74](), [agent/dashboard/oauth.py:1-200](), [agent/dashboard/thread_api.py:1-185](), [agent/dashboard/review_style_jobs.py:38-121]()

## REST API Endpoints

All endpoints are prefixed with `/dashboard/api` and generally require an active session via the `require_session` dependency [agent/dashboard/routes.py:78-87]().

### Authentication & User
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/auth/login` | GET | Initiates GitHub OAuth flow [agent/dashboard/routes.py:144](). |
| `/auth/callback` | GET | Handles OAuth redirect and issues session [agent/dashboard/routes.py:165](). |
| `/auth/logout` | POST | Clears the session cookie [agent/dashboard/routes.py:199](). |
| `/me` | GET | Returns current user's GitHub login, email, and admin status [agent/dashboard/routes.py:206](). |
| `/profile` | GET/PUT | Manages user-specific defaults (model, repo, branch prefix) [agent/dashboard/routes.py:221-229](). |

### Thread Management
These endpoints interface with the LangGraph server to manage agent conversations.

*   **`list_dashboard_threads`**: Filters LangGraph threads by `source="dashboard"` and the user's `github_login` [agent/dashboard/thread_api.py:185-195]().
*   **`create_dashboard_thread`**: Initializes a new thread, persists the user's encrypted GitHub token into thread metadata, and kicks off the initial agent run [agent/dashboard/thread_api.py:214-250]().
*   **`stream_dashboard_thread`**: Provides a `StreamingResponse` that yields LangGraph events mapped to the UI message format [agent/dashboard/thread_api.py:348-356]().

### Review Styles
Manages the synthesis of repository-specific review guidelines.

*   **`start_review_style_analysis`**: Kicks off a specialized LangGraph assistant (`review_style_analyzer`) that uses a sandbox to research historical PRs using the `gh` CLI [agent/dashboard/review_style_jobs.py:38-105]().
*   **`sync_review_style_run_status`**: Reconciles the state in the LangGraph Store with the actual status of the background analysis run [agent/dashboard/review_style_jobs.py:123-155]().

## Review Style Analyzer

The Review Style Analyzer is a distinct agentic workflow designed to automate "Context Engineering" for the reviewer agent.

### Analysis Workflow
1.  **Sample Collection**: The backend optionally pre-collects review samples [agent/dashboard/review_style_jobs.py:47]().
2.  **Agent Research**: The `review_style_analyzer` agent is spawned in a sandbox [agent/review_style_analyzer.py:118-119]().
3.  **Tool Usage**: The agent uses the `execute` tool to run `gh api` commands to browse merged PRs and identify human feedback patterns [agent/review_style_analyzer.py:49-71]().
4.  **Synthesis**: Once sufficient evidence is gathered, the agent calls `save_review_style_prompt` to persist the synthesized guide into the LangGraph Store [agent/review_style_analyzer.py:73-89]().

### Implementation Details
The analyzer uses a specific system prompt (`STYLE_ANALYZER_PROMPT`) that instructs it to identify the top reviewers and calibrate severity based on historical data [agent/review_style_analyzer.py:49-98]().

## Data Transformation (Message Adapter)

The backend includes a `state_messages_to_ui` utility that transforms complex LangChain/LangGraph message objects into a simplified JSON structure for the React frontend [agent/dashboard/message_adapter.py:131-135]().

**Key Transformations:**
*   **Tool Categorization**: Maps internal tool names to UI categories like `edit`, `execute`, or `search` [agent/dashboard/message_adapter.py:37-51]().
*   **Diff Extraction**: Parses tool arguments (e.g., from `write_file` or `str_replace`) to generate `diffData` objects for the frontend's diff viewer [agent/dashboard/message_adapter.py:77-94]().
*   **Turn Aggregation**: Groups consecutive AI messages and tool outputs into logical "turns" for cleaner display [agent/dashboard/message_adapter.py:131-160]().

"Message Transformation Logic"
```mermaid
graph LR
    subgraph "LangGraph State"
        M_AI["AIMessage (tool_calls)"]
        M_TOOL["ToolMessage (output)"]
    end

    subgraph "Adapter [agent/dashboard/message_adapter.py]"
        PARSE["_parse_tool_args()"]
        DIFF["_maybe_diff_from_args()"]
        KIND["_tool_kind()"]
    end

    subgraph "UI Payload"
        U_MSG["Message Chunk"]
        U_DIFF["diffData"]
    end

    M_AI --> PARSE
    PARSE --> DIFF
    PARSE --> KIND
    DIFF --> U_DIFF
    KIND --> U_MSG
```
Sources: [agent/dashboard/message_adapter.py:37-94](), [agent/dashboard/message_adapter.py:131-196]()

## Security and Session Management

*   **Token Encryption**: GitHub OAuth tokens are encrypted using Fernet before being stored in thread metadata, ensuring that even if the database is compromised, user tokens remain protected [agent/dashboard/thread_api.py:76-86]().
*   **Token Rotation**: The backend automatically handles GitHub OAuth token expiration by checking `token_expires_at` and performing a refresh using the stored refresh token [agent/dashboard/profiles.py:9-62]().
*   **State Verification**: The OAuth state parameter is a signed JWT that is cross-referenced against an HMAC-hashed nonce stored in a browser cookie to prevent CSRF [agent/dashboard/oauth.py:102-126]().

Sources: [agent/dashboard/routes.py:1-234](), [agent/dashboard/oauth.py:1-200](), [agent/dashboard/thread_api.py:1-356](), [agent/dashboard/review_style_jobs.py:1-181](), [agent/review_style_analyzer.py:1-165](), [agent/dashboard/message_adapter.py:1-196]()

---

# Page: Dashboard Frontend

# Dashboard Frontend

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/dashboard/profiles.py](agent/dashboard/profiles.py)
- [agent/dashboard/team_settings.py](agent/dashboard/team_settings.py)
- [tests/test_pr_ready_auto_review.py](tests/test_pr_ready_auto_review.py)
- [ui/package.json](ui/package.json)
- [ui/src/components/AppShell.tsx](ui/src/components/AppShell.tsx)
- [ui/src/components/AppSidebar.tsx](ui/src/components/AppSidebar.tsx)
- [ui/src/components/ui/switch.tsx](ui/src/components/ui/switch.tsx)
- [ui/src/lib/api.ts](ui/src/lib/api.ts)
- [ui/src/lib/profile.ts](ui/src/lib/profile.ts)
- [ui/src/routes/admin.tsx](ui/src/routes/admin.tsx)
- [ui/src/routes/cloud-agents.tsx](ui/src/routes/cloud-agents.tsx)
- [ui/src/routes/my-settings.tsx](ui/src/routes/my-settings.tsx)
- [ui/src/routes/review.tsx](ui/src/routes/review.tsx)
- [ui/yarn.lock](ui/yarn.lock)

</details>



The Open SWE Dashboard is a React-based single-page application (SPA) built with **Vite**, **TanStack Router**, and **TanStack Query**. It provides a management interface for configuring agent models, repository settings, and team-wide review policies.

## System Architecture and Data Flow

The frontend communicates with the FastAPI backend via a typed API client. Authentication is handled via an `httpOnly` session cookie (`osw_session`) established during the OAuth flow, which is automatically included in cross-origin requests using `credentials: "include"` [ui/src/lib/api.ts:1-6]().

### Frontend-Backend Communication

The following diagram illustrates how the React components interact with the backend API and the underlying LangGraph Store.

**Dashboard Data Flow: UI to Code Entity Space**
```mermaid
graph TD
    subgraph "Browser (React)"
        A["CloudAgentsPage [ui/src/routes/cloud-agents.tsx]"] -- "api.saveProfile()" --> B["api client [ui/src/lib/api.ts]"]
        C["AdminPage [ui/src/routes/admin.tsx]"] -- "api.saveTeamSettings()" --> B
    end

    subgraph "FastAPI Backend"
        B -- "PUT /profile" --> D["upsert_profile [agent/dashboard/profiles.py]"]
        B -- "PUT /team-settings" --> E["upsert_team_settings [agent/dashboard/team_settings.py]"]
    end

    subgraph "Persistence Layer"
        D -- "put_item" --> F["LangGraph Store (Namespace: ['profiles'])"]
        E -- "put_item" --> G["LangGraph Store (Namespace: ['team_settings'])"]
    end
```
**Sources:** [ui/src/lib/api.ts:141-190](), [agent/dashboard/profiles.py:31-32](), [agent/dashboard/team_settings.py:21-22]()

## Route Structure

The application uses **TanStack Router** for type-safe routing. The navigation is primarily managed by the `AppSidebar` component [ui/src/components/AppSidebar.tsx:30-36]().

| Route | Component | Purpose |
| :--- | :--- | :--- |
| `/my-settings` | `MySettingsPage` | User-specific profile settings and logout [ui/src/routes/my-settings.tsx:19]() |
| `/cloud-agents` | `CloudAgentsPage` | Per-user agent defaults (model, repo, branch) [ui/src/routes/cloud-agents.tsx:28]() |
| `/review` | `ReviewPage` | Team-wide PR review configuration and repo toggles [ui/src/routes/review.tsx:20]() |
| `/review/styles` | `ReviewStylesPage` | Per-repo review style guide management [ui/src/lib/api.ts:148]() |
| `/admin` | `AdminPage` | Workspace defaults and per-user profile overrides [ui/src/routes/admin.tsx:20]() |

**Sources:** [ui/src/components/AppSidebar.tsx:30-36](), [ui/src/routes/my-settings.tsx:35](), [ui/src/routes/cloud-agents.tsx:30](), [ui/src/routes/review.tsx:59](), [ui/src/routes/admin.tsx:22]()

## Key Implementation Details

### Profile and Settings Management
Settings are synchronized using **TanStack Query** hooks defined in `ui/src/lib/profile.ts`. The `buildProfileUpdate` utility ensures that partial updates (e.g., changing only the branch prefix) do not clobber other fields in the profile object [ui/src/lib/profile.ts:57-74]().

**Profile Synchronization Logic**
```mermaid
sequenceDiagram
    participant UI as CloudAgentsPage
    participant Hook as useSaveProfile
    participant API as api.ts
    participant Store as LangGraph Store

    UI->>Hook: mutate(patch)
    Hook->>API: saveProfile(body)
    API->>Store: upsert_profile(login, update)
    Store-->>API: 200 OK (Updated Profile)
    API-->>Hook: saved data
    Hook->>UI: invalidateQueries(["profile"])
```
**Sources:** [ui/src/lib/profile.ts:42-50](), [agent/dashboard/profiles.py:80-111]()

### Component Library
The UI is built using a combination of custom components and primitives:
*   **Styling**: Tailwind CSS 4.0 with `class-variance-authority` for component variants [ui/package.json:19-28]().
*   **Icons**: `react-icons/io5` and `@phosphor-icons/react` [ui/src/components/AppSidebar.tsx:2-9](), [ui/src/routes/review.tsx:3]().
*   **Primitives**: Radix-based components (Select, Switch, Combobox) via a local `ui/src/components/ui` directory [ui/src/routes/cloud-agents.tsx:5-24]().

## Admin and Team Settings

The `AdminPage` provides a dual-pane interface for managing the workspace. It allows administrators to:
1.  **Global Defaults**: Set the default `model_id` and `reasoning_effort` for both the "Agent" (Slack/Linear) and the "Reviewer" (GitHub PRs) [ui/src/routes/admin.tsx:138-174]().
2.  **User Overrides**: Select any user in the organization and edit their profile using the `ProfileForm` component [ui/src/routes/admin.tsx:71-110]().

The backend ensures these settings are persisted in the `team_settings` namespace within the LangGraph Store, specifically under the `default` key [agent/dashboard/team_settings.py:21-22]().

**Sources:** [ui/src/routes/admin.tsx:22-113](), [agent/dashboard/team_settings.py:104-118]()

---

# Page: User Profiles and Team Settings

# User Profiles and Team Settings

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/dashboard/agent_overrides.py](agent/dashboard/agent_overrides.py)
- [agent/dashboard/oauth.py](agent/dashboard/oauth.py)
- [agent/dashboard/options.py](agent/dashboard/options.py)
- [agent/dashboard/profiles.py](agent/dashboard/profiles.py)
- [agent/dashboard/review_style_jobs.py](agent/dashboard/review_style_jobs.py)
- [agent/dashboard/review_styles.py](agent/dashboard/review_styles.py)
- [tests/test_github_oauth_refresh.py](tests/test_github_oauth_refresh.py)
- [tests/test_review_style_sync.py](tests/test_review_style_sync.py)
- [ui/src/components/ReviewStylesPanel.tsx](ui/src/components/ReviewStylesPanel.tsx)
- [ui/src/lib/api.ts](ui/src/lib/api.ts)
- [ui/src/routes/__root.tsx](ui/src/routes/__root.tsx)

</details>



Open SWE provides a multi-layered configuration system that allows for individual developer preferences while maintaining team-wide standards. This system manages per-user overrides, such as preferred LLMs and repository defaults, alongside team-wide automation policies for CI autofixing and PR summaries.

## User Profiles and Overrides

Each user in Open SWE has a persistent profile stored in the LangGraph Store. These profiles allow developers to customize how agents behave when triggered by their actions (e.g., via Slack or Linear).

### Data Storage Strategy
User data is split into two distinct namespaces within the LangGraph Store to prevent race conditions between user-initiated UI edits and background OAuth token refreshes [agent/dashboard/profiles.py:1-11]():
*   **`["profiles"]`**: Contains user-editable settings like `default_model`, `reasoning_effort`, and `branch_prefix` [agent/dashboard/profiles.py:31]().
*   **`["oauth_tokens"]`**: Stores encrypted GitHub access tokens, refresh tokens, and expiration timestamps [agent/dashboard/profiles.py:32]().

### Profile Configuration Options
The `ProfileUpdate` schema defines the configurable parameters for an individual user [agent/dashboard/profiles.py:35-43]():

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `default_model` | `str` | The LLM ID used for agent runs triggered by this user. |
| `reasoning_effort` | `str` | The reasoning effort level (e.g., "low", "medium", "high"). |
| `default_repo` | `str \| None` | Default `owner/repo` to target if none is specified in the trigger. |
| `branch_prefix` | `str \| None` | Custom prefix for branches created by the agent (e.g., `ai/`). |
| `create_prs` | `bool` | Whether the agent should automatically open a PR upon task completion. |
| `auto_fix_ci` | `bool` | Whether the agent should automatically attempt to fix CI failures. |

### Profile Resolution Flow
When an agent is initialized via `get_agent`, the system attempts to resolve the triggering user's GitHub login to apply these overrides.

```mermaid
graph TD
    subgraph "Natural Language Space"
        A["Slack/Linear Event"] -- "Extracts Email" --> B["User Context"]
    end

    subgraph "Code Entity Space"
        B -- "resolve_github_login()" --> C["agent/dashboard/agent_overrides.py"]
        C -- "Lookup" --> D["GITHUB_USER_EMAIL_MAP"]
        D -- "Login Found" --> E["load_profile(login)"]
        E -- "Namespace: ['profiles']" --> F["LangGraph Store"]
        F -- "Return dict" --> G["normalize_profile_overrides()"]
        G -- "Apply to" --> H["create_deep_agent()"]
    end
```
Sources: [agent/dashboard/agent_overrides.py:29-40](), [agent/dashboard/agent_overrides.py:61-72](), [agent/dashboard/agent_overrides.py:85-96]()

## Team Settings and Admin Panel

Team settings define the global behavior of the Open SWE deployment. These settings act as fallbacks when user-specific profiles are not set or when events are triggered by the system (e.g., automated PR reviews).

### Global Automation Policies
The `TeamSettings` interface manages the following high-level behaviors [ui/src/lib/api.ts:92-103]():
*   **`trigger_mode`**: Controls when the reviewer agent runs (e.g., `every_push`, `once_per_pr`, or `manual`) [ui/src/lib/api.ts:89]().
*   **`autofix_mode`**: Sets the threshold for the Reviewer Agent to automatically commit fixes for findings (`off`, `low`, `medium`, `high`) [ui/src/lib/api.ts:90]().
*   **`pr_summaries`**: Boolean flag to enable/disable automated AI-generated PR descriptions.

### Model Options and Validation
The dashboard restricts model selection to a predefined list of supported IDs and effort levels to ensure compatibility with the underlying providers [agent/dashboard/options.py:15-28]().
*   **Validation**: The `ProfileUpdate` class uses a `@field_validator` to ensure the selected `default_model` exists in `SUPPORTED_MODEL_IDS` [agent/dashboard/profiles.py:45-50]().
*   **Pairing**: It further validates that the selected `reasoning_effort` is supported by that specific model via `model_supports_effort()` [agent/dashboard/profiles.py:52-57]().

## Review Style Management

A key component of team settings is the per-repository "Review Style." This allows teams to train the Reviewer Agent on their specific coding standards by analyzing historical PRs.

### Analysis Lifecycle
The analysis is managed as a background LangGraph run using the `review_style_analyzer` assistant [agent/dashboard/review_style_jobs.py:27]().

```mermaid
graph LR
    subgraph "Frontend (React)"
        UI["ReviewStylesPanel.tsx"] -- "api.analyzeReviewStyle()" --> API["FastAPI Router"]
    end

    subgraph "Backend (Python)"
        API -- "calls" --> Start["start_review_style_analysis()"]
        Start -- "1. collect_review_samples()" --> GH["GitHub API"]
        Start -- "2. mark_analysis_running()" --> Store["LangGraph Store"]
        Start -- "3. client.runs.create()" --> LG["LangGraph Server"]
        LG -- "Assistant: review_style_analyzer" --> Analysis["Agent Loop"]
    end
```
Sources: [ui/src/components/ReviewStylesPanel.tsx:95-103](), [agent/dashboard/review_style_jobs.py:38-45](), [agent/dashboard/review_style_jobs.py:88-105]()

### Analysis Status Reconciliation
Because analysis runs are asynchronous, the dashboard polls for status updates. The backend reconciles the state in the LangGraph Store with the actual status of the LangGraph run [agent/dashboard/review_styles.py:147-155]():
*   **Success**: If the run completes and a `custom_prompt` was saved, the status moves to `completed` [agent/dashboard/review_styles.py:161-163]().
*   **Failure**: If the run ends without saving a prompt, it is marked as `failed` with a user-facing error message [agent/dashboard/review_styles.py:164-167]().

## Authentication and Session Management

Access to the dashboard and the ability to save profiles is secured via GitHub OAuth.

### Session Persistence
*   **JWT Sessions**: Upon successful OAuth exchange, the system issues a signed JWT stored in an `osw_session` httpOnly cookie [agent/dashboard/oauth.py:21-23]().
*   **Token Encryption**: GitHub OAuth tokens (access and refresh) are encrypted using Fernet before being stored in the `oauth_tokens` namespace [agent/dashboard/profiles.py:157-161]().
*   **Token Refresh**: The `get_valid_access_token` function checks for token expiration (with a 300-second buffer) and automatically uses the refresh token to rotate the access token if necessary [agent/dashboard/profiles.py:125-134](), [agent/dashboard/profiles.py:220-235]().

Sources: [agent/dashboard/oauth.py:83-92](), [agent/dashboard/profiles.py:153-168](), [agent/dashboard/profiles.py:205-215]()

---

# Page: Agent Threads UI

# Agent Threads UI

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ui/src/components/agents/AgentRunCard.tsx](ui/src/components/agents/AgentRunCard.tsx)
- [ui/src/components/agents/AgentThreadView.tsx](ui/src/components/agents/AgentThreadView.tsx)
- [ui/src/components/agents/AgentsHome.tsx](ui/src/components/agents/AgentsHome.tsx)
- [ui/src/lib/agents/api.ts](ui/src/lib/agents/api.ts)

</details>



The Agent Threads UI provides a comprehensive interface for interacting with, monitoring, and managing Open SWE agent executions. Located under the `/agents/` route, this system enables users to initiate new agent runs, view real-time execution logs, inspect code changes via diff viewers, and manage historical conversation threads.

## Component Architecture

The UI is structured around a central shell that manages navigation and state, with specialized views for the home screen and individual thread interactions.

### Component Hierarchy and Data Flow
The following diagram illustrates the relationship between the primary UI components and the backend API.

**Agent UI Component Map**
```mermaid
graph TD
    subgraph "Agents Route Space"
        A["AgentsHome"] --> B["AgentPromptBar"]
        A --> C["AgentRunCard"]
        D["AgentThreadView"] --> B
        D --> E["MessageView (Ported)"]
        D --> F["AgentsSidebar"]
    end

    subgraph "Code Entity Space"
        G["agentsApi.listThreads"]
        H["agentsApi.createThread"]
        I["agentsApi.sendMessage"]
        J["useAgentThreadStream"]
    end

    C -- "Displays" --> G
    B -- "Triggers" --> H
    B -- "Triggers" --> I
    D -- "Real-time updates" --> J
    J -- "EventSource" --> K["/threads/:id/stream"]
```
Sources: `ui/src/components/agents/AgentsHome.tsx:10-53`(), `ui/src/components/agents/AgentThreadView.tsx:29-170`(), `ui/src/lib/agents/api.ts:45-69`()

## Key Components

### AgentsHome
The landing page for the agent interface. It serves two primary functions:
1.  **Initialization**: Provides the primary `AgentPromptBar` to start new agent tasks `[ui/src/components/agents/AgentsHome.tsx:26-38]()`.
2.  **History**: Displays a list of the 5 most recent agent runs using `AgentRunCard` components `[ui/src/components/agents/AgentsHome.tsx:13-49]()`.

### AgentThreadView
The core interaction component for an active or historical agent session. It manages:
*   **Message Rendering**: Uses a ported `MessageView` to display the conversation history between the user and the agent `[ui/src/components/agents/AgentThreadView.tsx:111-119]()`.
*   **Real-time Streaming**: Utilizes the `useAgentThreadStream` hook to listen for Server-Sent Events (SSE) from the backend, ensuring the UI reflects the agent's progress in real-time `[ui/src/components/agents/AgentThreadView.tsx:31]()`.
*   **File Change Summaries**: Aggregates all file modifications performed by the agent across the thread and displays a summary of additions and deletions `[ui/src/components/agents/AgentThreadView.tsx:95-140]()`.

### AgentRunCard
A summary component used in lists to represent a single thread. It visualizes the status of a run, including:
*   **Diff Stats**: Shows the number of files changed and the specific count of additions and deletions `[ui/src/components/agents/AgentRunCard.tsx:23-35]()`.
*   **Metadata**: Displays the model used, the target repository, and the relative time of the last update `[ui/src/components/agents/AgentRunCard.tsx:51-60]()`.
*   **Status Indicators**: Shows whether the agent has finished or is associated with a branch/PR `[ui/src/components/agents/AgentRunCard.tsx:37-48]()`.

### AgentPromptBar
The input interface for both creating threads and sending follow-up messages. It includes:
*   **Model Selection**: Allows users to choose the specific LLM and "effort" level (e.g., reasoning depth) for the run `[ui/src/components/agents/AgentThreadView.tsx:164-165]()`.
*   **State Management**: Handles "busy" states during streaming to prevent concurrent message submission `[ui/src/components/agents/AgentThreadView.tsx:159-160]()`.

Sources: `ui/src/components/agents/AgentRunCard.tsx:12-73`(), `ui/src/components/agents/AgentThreadView.tsx:29-105`(), `ui/src/components/agents/AgentsHome.tsx:10-53`()

## Data Handling and API Integration

The UI interacts with the backend via the `agentsApi` object, which wraps standard `fetch` calls to the dashboard API endpoints.

| Function | Endpoint | Purpose |
| :--- | :--- | :--- |
| `listThreads` | `GET /threads` | Fetches all agent threads for the user `[ui/src/lib/agents/api.ts:46]()` |
| `createThread` | `POST /threads` | Starts a new agent run with a prompt `[ui/src/lib/agents/api.ts:49-53]()` |
| `sendMessage` | `POST /threads/:id/messages` | Sends a follow-up message to an existing thread `[ui/src/lib/agents/api.ts:54-58]()` |
| `streamUrl` | `GET /threads/:id/stream` | Provides the SSE URL for real-time updates `[ui/src/lib/agents/api.ts:67-68]()` |

### Thread Management Logic
Threads are grouped by time (Today, Last 30 Days, Older) for better organization in the sidebar and home screens using the `groupThreads` utility `[ui/src/lib/agents/api.ts:85-107]()`.

**Data Flow: Prompt to Execution**
```mermaid
sequenceDiagram
    participant U as User (UI)
    participant API as agentsApi
    participant B as Backend (FastAPI)
    participant S as SSE Stream

    U->>API: createThread(prompt, model)
    API->>B: POST /dashboard/api/threads
    B-->>API: AgentThread Object
    API-->>U: Navigate to /agents/:id
    U->>S: Connect to /threads/:id/stream
    B-->>S: Agent Action (e.g., call tool)
    S-->>U: Update MessageView
```
Sources: `ui/src/lib/agents/api.ts:45-69`(), `ui/src/components/agents/AgentThreadView.tsx:29-31`()

## Ported Components

The Agent Threads UI utilizes several components ported from the core chat/diff viewer infrastructure to maintain consistency in how code and messages are displayed:

1.  **MessageView**: Handles the complex rendering of multi-modal messages, including text chunks and tool invocation blocks `[ui/src/components/agents/AgentThreadView.tsx:111-119]()`.
2.  **summarizeChangedFiles**: A utility that parses agent message chunks to extract a list of files modified during the session `[ui/src/components/agents/AgentThreadView.tsx:95-99]()`.
3.  **Logo**: The standard branding component used across the dashboard `[ui/src/components/agents/AgentsHome.tsx:25]()`.

Sources: `ui/src/components/agents/AgentThreadView.tsx:6-10`(), `ui/src/components/agents/AgentThreadView.tsx:95-99`()

---

# Page: Deployment

# Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CUSTOMIZATION.md](CUSTOMIZATION.md)
- [Dockerfile](Dockerfile)
- [INSTALLATION.md](INSTALLATION.md)
- [README.md](README.md)
- [agent/tools/fetch_url.py](agent/tools/fetch_url.py)
- [agent/tools/http_request.py](agent/tools/http_request.py)
- [tests/test_http_security.py](tests/test_http_security.py)

</details>



This page provides a comprehensive guide to deploying Open SWE in production environments. It covers environment variable configuration, webhook setup with external platforms, LangGraph server deployment options, and Docker containerization.

For local development setup, see [Local Development Setup](#12.1). For details on the technology stack and infrastructure components, see [Technology Stack](#1.2).

---

## Overview

Open SWE deploys as two main components: a **FastAPI webhook server** ([agent/webapp.py]()) that receives events from external platforms, and a **LangGraph server** ([agent/server.py]()) that orchestrates agent execution. The webhook server handles signature verification and creates runs on the LangGraph server.

```mermaid
graph TB
    subgraph "External Platforms"
        GitHub["GitHub<br/>Webhooks"]
        Linear["Linear<br/>Webhooks"]
        Slack["Slack<br/>Event API"]
    end
    
    subgraph "Deployment Environment"
        subgraph "FastAPI Webhook Server [agent/webapp.py]"
            GitHubWH["POST /webhooks/github<br/>github_webhook()"]
            LinearWH["POST /webhooks/linear<br/>linear_webhook()"]
            SlackWH["POST /webhooks/slack<br/>slack_webhook()"]
            Health["GET /health"]
        end
        
        subgraph "LangGraph Server [agent/server.py]"
            GetAgent["get_agent()"]
            RunsAPI["LangGraph Runs API"]
            ThreadsAPI["LangGraph Threads API"]
        end
        
        subgraph "Execution Layer"
            Sandboxes["Sandbox Backends<br/>SANDBOX_TYPE"]
            LSBackend["LangSmith Sandbox<br/>create_langsmith_sandbox()"]
        end
    end
    
    subgraph "External Services"
        LangSmithAPI["LangSmith API<br/>LANGSMITH_API_KEY_PROD"]
        LLMAPI["LLM Provider API<br/>ANTHROPIC_API_KEY / OPENAI_API_KEY"]
        GitHubAPI["GitHub API<br/>GITHUB_APP_*"]
    end
    
    GitHub --> GitHubWH
    Linear --> LinearWH
    Slack --> SlackWH
    
    GitHubWH --> RunsAPI
    LinearWH --> RunsAPI
    SlackWH --> RunsAPI
    
    RunsAPI --> GetAgent
    GetAgent --> Sandboxes
    Sandboxes --> LSBackend
    
    GetAgent --> LangSmithAPI
    GetAgent --> LLMAPI
    GetAgent --> GitHubAPI
```

**Deployment Architecture**

This diagram shows the complete deployment topology. External webhooks hit the FastAPI endpoints, which trigger LangGraph runs. The `get_agent()` function provisions sandboxes based on the `SANDBOX_TYPE` and connects to external services.

**Sources:** [agent/server.py:3-23](), [INSTALLATION.md:39-102](), [README.md:34-50]()

---

## Environment Configuration

Open SWE requires specific environment variables for authentication, webhook security, and service integration. For details, see [Environment Configuration](#11.1).

### Required Environment Variables

| Variable | Description | Source |
|----------|-------------|--------|
| `LANGSMITH_API_KEY_PROD` | LangSmith API key for tracing and sandboxes | [INSTALLATION.md:113-113]() |
| `LANGSMITH_TENANT_ID_PROD` | LangSmith Tenant ID | [INSTALLATION.md:114-114]() |
| `GITHUB_APP_ID` | GitHub App ID from settings | [INSTALLATION.md:82-82]() |
| `GITHUB_APP_PRIVATE_KEY` | GitHub App RSA private key | [INSTALLATION.md:83-83]() |
| `GITHUB_APP_INSTALLATION_ID` | GitHub App installation ID | [INSTALLATION.md:99-99]() |
| `GITHUB_WEBHOOK_SECRET` | Secret for verifying GitHub webhooks | [INSTALLATION.md:62-65]() |

### Sandbox Configuration

The `SANDBOX_TYPE` variable determines where the agent executes code. Supported types include `langsmith` (default), `daytona`, `runloop`, `modal`, and `local`.

**Sources:** [CUSTOMIZATION.md:58-64](), [README.md:52-63]()

---

## Webhook Setup

Open SWE receives events from external platforms via webhooks. Each platform requires configuring a webhook URL pointing to the deployed FastAPI server. For details, see [Webhook Setup](#11.2).

```mermaid
graph TB
    subgraph "FastAPI Application [agent/webapp.py]"
        App["app = FastAPI()"]
        
        subgraph "GitHub Webhooks"
            GitHubPost["@app.post('/webhooks/github')"]
            GitHubVerify["verify_github_signature()"]
        end
        
        subgraph "Linear Webhooks"
            LinearPost["@app.post('/webhooks/linear')"]
            LinearVerify["verify_linear_signature()"]
        end
        
        subgraph "Slack Webhooks"
            SlackPost["@app.post('/webhooks/slack')"]
            SlackVerify["verify_slack_signature()"]
        end
    end
    
    GitHubPost --> GitHubVerify
    LinearPost --> LinearVerify
    SlackPost --> SlackVerify
```

**Webhook Endpoint Structure**

This diagram shows the FastAPI route definitions. Each webhook handler validates the request signature using the corresponding secret before processing.

**Sources:** [INSTALLATION.md:53-76](), [INSTALLATION.md:167-175](), [INSTALLATION.md:205-215]()

---

## LangGraph Server Deployment

The LangGraph server can be deployed on **LangGraph Cloud** or **self-hosted**. For details, see [LangGraph Server Deployment](#11.3).

- **LangGraph Cloud**: Managed platform that automatically builds based on `langgraph.json`.
- **Self-Hosted**: Run the server on custom infrastructure; the FastAPI webapp connects via `LANGGRAPH_URL`.

**Sources:** [INSTALLATION.md:349-366](), [INSTALLATION.md:396-415]()

---

## Docker Deployment

Open SWE provides a Dockerfile to build images for sandboxes or the application itself. For details, see [Docker Deployment](#11.4).

### Dockerfile Components

The Dockerfile installs a comprehensive toolchain to ensure the agent has everything it needs to build and test code:

- **Python**: 3.14.0-slim-trixie [Dockerfile:1-1]()
- **UV**: Package manager for Python [Dockerfile:46-59]()
- **Node.js & Yarn**: For frontend/JS environments [Dockerfile:63-67]()
- **Go**: For Go-based repositories [Dockerfile:69-75]()
- **GitHub CLI (gh)**: For PR and issue operations [Dockerfile:34-44]()

**Sources:** [Dockerfile:1-88]()

---

## Production Deployment Checklist

Before moving to production, verify:

- [ ] `GITHUB_WEBHOOK_SECRET` matches GitHub App settings.
- [ ] `SANDBOX_TYPE` is set to a production-grade provider (e.g., `langsmith`, `daytona`).
- [ ] `GITHUB_OAUTH_PROVIDER_ID` is configured in LangSmith if per-user identity is required.
- [ ] `ALLOWED_GITHUB_ORGS` is set to restrict access to authorized organizations.

**Sources:** [INSTALLATION.md:117-133](), [CUSTOMIZATION.md:58-64]()

---

# Page: Environment Configuration

# Environment Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CUSTOMIZATION.md](CUSTOMIZATION.md)
- [INSTALLATION.md](INSTALLATION.md)
- [README.md](README.md)
- [agent/integrations/langsmith.py](agent/integrations/langsmith.py)
- [agent/utils/github_user_email_map.py](agent/utils/github_user_email_map.py)
- [pyproject.toml](pyproject.toml)
- [uv.lock](uv.lock)

</details>



This document specifies all required and optional environment variables for running Open SWE. The system consists of a Python FastAPI webhook server and a LangGraph agent orchestration layer, requiring configuration for LLM providers, GitHub App authentication, webhook integrations (Slack, Linear, GitHub), sandbox providers, and observability services.

All environment variables are loaded from a single `.env` file in the project root or set in the deployment environment. For production deployment instructions, see [LangGraph Server Deployment](#11.3). For local development setup, see [Local Development Setup](#12.1).

## Environment File Location

Open SWE uses a single `.env` file at the project root for all configuration.

**Title: Configuration Data Flow and Entity Mapping**

```mermaid
graph TB
    subgraph "Configuration Loading"
        EnvFile[".env file<br/>(project root)"]
        OsEnviron["os.environ<br/>(Python runtime)"]
    end
    
    subgraph "FastAPI Webhook Server"
        WebApp["agent/webapp.py"]
        WebhookVars["LINEAR_WEBHOOK_SECRET<br/>GITHUB_WEBHOOK_SECRET<br/>SLACK_SIGNING_SECRET<br/>SLACK_BOT_TOKEN<br/>LINEAR_API_KEY"]
        RepoMapping["SLACK_REPO_OWNER<br/>SLACK_REPO_NAME<br/>ALLOWED_GITHUB_ORGS"]
    end
    
    subgraph "LangGraph Agent Server"
        ServerPy["agent/server.py<br/>get_agent()"]
        AuthUtils["agent/utils/auth.py"]
        AuthVars["LANGSMITH_API_KEY_PROD<br/>GITHUB_OAUTH_PROVIDER_ID"]
    end
    
    subgraph "Sandbox Backend"
        LangSmithIntegration["agent/integrations/langsmith.py<br/>create_langsmith_sandbox()"]
        SandboxVars["SANDBOX_TYPE<br/>DEFAULT_SANDBOX_SNAPSHOT_ID<br/>DEFAULT_SANDBOX_VCPUS"]
    end
    
    subgraph "GitHub App"
        GitHubApp["agent/utils/github_app.py<br/>get_github_app_installation_token()"]
        AppVars["GITHUB_APP_ID<br/>GITHUB_APP_PRIVATE_KEY<br/>GITHUB_APP_INSTALLATION_ID"]
    end
    
    subgraph "Model Configuration"
        ModelUtils["agent/utils/model.py<br/>make_model()"]
        LLMVars["ANTHROPIC_API_KEY<br/>OPENAI_API_KEY<br/>LLM_MODEL_ID"]
    end
    
    EnvFile --> OsEnviron
    OsEnviron --> WebApp
    OsEnviron --> ServerPy
    OsEnviron --> AuthUtils
    OsEnviron --> LangSmithIntegration
    OsEnviron --> GitHubApp
    OsEnviron --> ModelUtils
    
    WebApp --> WebhookVars
    WebApp --> RepoMapping
    ServerPy --> SandboxVars
    AuthUtils --> AuthVars
    GitHubApp --> AppVars
    ModelUtils --> LLMVars
```

**Sources:** [agent/integrations/langsmith.py:25-67](), [agent/server.py:6-23](), [INSTALLATION.md:294-346](), [CUSTOMIZATION.md:58-64]()

## Core Configuration Categories

Environment variables are organized into categories based on their function in the system.

### LangSmith Configuration

LangSmith provides tracing, observability, and the default sandbox execution environment.

| Variable | Required | Purpose | Example Value |
|----------|----------|---------|---------------|
| `LANGSMITH_API_KEY_PROD` | Yes | LangSmith API key for tracing and sandboxes | `lsv2_pt_...` |
| `LANGSMITH_TENANT_ID_PROD` | Yes | LangSmith organization/tenant UUID | `72184268-...` |
| `LANGSMITH_TRACING_PROJECT_ID_PROD` | Yes | Project ID for agent tracing | UUID from project settings |

**Code References:**
- API key loading: [agent/integrations/langsmith.py:25-31]()
- Sandbox snapshot config: [agent/integrations/langsmith.py:45-67]()

**Sources:** [INSTALLATION.md:109-116](), [agent/integrations/langsmith.py:25-31]()

### LLM Provider Configuration

At least one LLM provider API key is required. The system supports multiple providers via the `make_model` utility.

| Variable | Required | Purpose | Example Value |
|----------|----------|---------|---------------|
| `OPENAI_API_KEY` | Recommended | Required if using OpenAI models (default) | `sk-...` |
| `ANTHROPIC_API_KEY` | Optional | Required for Claude models | `sk-ant-...` |
| `LLM_MODEL_ID` | No | Override default agent model | `openai:gpt-5.5` |

**Code References:**
- Model initialization: [agent/server.py:7-13]()
- Default model: `openai:gpt-5.5` [CUSTOMIZATION.md:136-145]()

**Sources:** [CUSTOMIZATION.md:7-13](), [CUSTOMIZATION.md:149-160]()

### GitHub App Configuration

GitHub App credentials enable repository access, PR creation, and webhook authentication.

| Variable | Required | Purpose | Example Value |
|----------|----------|---------|---------------|
| `GITHUB_APP_ID` | Yes | GitHub App numeric ID | `123456` |
| `GITHUB_APP_PRIVATE_KEY` | Yes | Multi-line RSA private key (PEM format) | `"-----BEGIN RSA PRIVATE KEY-----\n..."` |
| `GITHUB_APP_INSTALLATION_ID` | Yes | Installation ID for the target org/account | `12345678` |
| `GITHUB_WEBHOOK_SECRET` | Yes | Webhook signature verification secret | Generated via `openssl rand -hex 32` |

**Sources:** [INSTALLATION.md:80-99](), [INSTALLATION.md:307-316]()

### GitHub OAuth Configuration (Optional)

GitHub OAuth enables per-user authentication. Without this, the system uses the GitHub App's installation token (bot-token-only mode).

| Variable | Required | Purpose | Example Value |
|----------|----------|---------|---------------|
| `GITHUB_OAUTH_PROVIDER_ID` | No | LangSmith OAuth provider ID for GitHub | `"your-org-github-oauth"` |

**Email Mapping:**
To link GitHub users to LangSmith accounts for OAuth resolution, entries must be added to the `GITHUB_USER_EMAIL_MAP`.
**Sources:** [agent/utils/github_user_email_map.py:1-128](), [INSTALLATION.md:117-132]()

### Webhook Integration Configuration

| Variable | Required | Purpose | Example Value |
|----------|----------|---------|---------------|
| **Linear** |
| `LINEAR_API_KEY` | If using Linear | API key for fetching issues and comments | `lin_api_...` |
| `LINEAR_WEBHOOK_SECRET` | If using Linear | Webhook signature verification secret | Generated secret |
| **Slack** |
| `SLACK_BOT_TOKEN` | If using Slack | Slack Bot User OAuth Token | `xoxb-...` |
| `SLACK_SIGNING_SECRET` | If using Slack | Slack webhook signature verification secret | From Slack App |

**Sources:** [INSTALLATION.md:328-338]()

### Sandbox Provider Configuration

Open SWE supports multiple sandbox backends. Use `SANDBOX_TYPE` to switch providers.

| Variable | Required | Purpose | Default Value |
|----------|----------|---------|---------------|
| `SANDBOX_TYPE` | No | Execution environment (`langsmith`, `daytona`, `runloop`, `modal`, `local`) | `langsmith` |
| `DEFAULT_SANDBOX_SNAPSHOT_ID` | Yes (if langsmith) | UUID of the LangSmith sandbox snapshot | - |
| `DAYTONA_API_KEY` | If type `daytona`| API key for Daytona provider | - |
| `RUNLOOP_API_KEY` | If type `runloop`| API key for Runloop provider | - |

**Sources:** [CUSTOMIZATION.md:37-43](), [CUSTOMIZATION.md:58-64]()

## Technical Implementation Flows

### Sandbox Configuration and GitHub Proxy

When using `langsmith` sandboxes, Open SWE configures a proxy to inject GitHub credentials into network traffic. This allows the agent to use `gh` and `git` without storing tokens on the sandbox disk.

**Title: Sandbox Proxy Configuration Flow**

```mermaid
graph TB
    subgraph "Environment Configuration"
        SnapshotID["DEFAULT_SANDBOX_SNAPSHOT_ID"]
        VCPUs["DEFAULT_SANDBOX_VCPUS"]
        Mem["DEFAULT_SANDBOX_MEM_BYTES"]
    end
    
    subgraph "Auth Context"
        GH_Token["GitHub Installation Token"]
    end
    
    subgraph "LangSmith Integration"
        CreateFn["create_langsmith_sandbox()<br/>agent/integrations/langsmith.py"]
        ProxyFn["_configure_github_proxy()<br/>agent/integrations/langsmith.py"]
        RulesFn["_github_proxy_rules()<br/>agent/integrations/langsmith.py"]
    end
    
    SnapshotID --> CreateFn
    VCPUs --> CreateFn
    Mem --> CreateFn
    
    GH_Token --> ProxyFn
    ProxyFn --> RulesFn
    
    RulesFn -->|"Rules for api.github.com (Bearer)<br/>and github.com (Basic)"| LangSmithAPI["LangSmith Patch /v2/sandboxes/boxes/{id}"]
```

**Sources:** [agent/integrations/langsmith.py:45-67](), [agent/integrations/langsmith.py:70-95](), [agent/integrations/langsmith.py:98-124]()

### GitHub Token Resolution

The system determines which token to use based on the presence of OAuth configuration and user mapping.

**Title: GitHub Token Resolution Logic**

```mermaid
graph LR
    subgraph "Inputs"
        UserEmail["User Email<br/>(from GITHUB_USER_EMAIL_MAP)"]
        OAuthID["GITHUB_OAUTH_PROVIDER_ID"]
    end
    
    subgraph "Resolution"
        ResolveFn["resolve_github_token()<br/>agent/utils/auth.py"]
        AppToken["get_github_app_installation_token()"]
    end
    
    OAuthID -->|"If set"| ResolveFn
    UserEmail -->|"If found"| ResolveFn
    ResolveFn -->|"Fallback"| AppToken
```

**Sources:** [agent/utils/github_user_email_map.py:7-128](), [INSTALLATION.md:117-132]()

## Complete Configuration Reference

| Variable | Required | Purpose |
|----------|----------|---------|
| `LANGSMITH_API_KEY_PROD` | Yes | Primary API key for LangSmith services |
| `GITHUB_APP_ID` | Yes | Numeric ID of your GitHub App |
| `GITHUB_APP_PRIVATE_KEY` | Yes | RSA Private Key for the App |
| `GITHUB_APP_INSTALLATION_ID` | Yes | Installation ID for the bot's target repo access |
| `TOKEN_ENCRYPTION_KEY` | Yes | Fernet key for encrypting persisted tokens |
| `SANDBOX_TYPE` | No | Default is `langsmith` |
| `DEFAULT_SANDBOX_SNAPSHOT_ID` | If langsmith | Snapshot UUID for the sandbox environment |

**Sources:** [INSTALLATION.md:294-346](), [CUSTOMIZATION.md:58-64]()

---

# Page: Webhook Setup

# Webhook Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CUSTOMIZATION.md](CUSTOMIZATION.md)
- [INSTALLATION.md](INSTALLATION.md)
- [README.md](README.md)
- [agent/webapp.py](agent/webapp.py)
- [tests/test_github_issue_webhook.py](tests/test_github_issue_webhook.py)

</details>



This page documents how to configure webhooks in external platforms (GitHub, Linear, Slack) to route events to the Open SWE FastAPI server. Webhooks are the primary mechanism for triggering agent runs from external user interactions.

For information about the overall deployment process, see [Environment Configuration](11.1) and [LangGraph Server Deployment](11.3). For details on how webhook events are processed internally, see [Webhook Processing Flow](2.4).

## Overview

Open SWE receives events from three external platforms via HTTP webhooks:

| Platform | Endpoint | Trigger |
|----------|----------|---------|
| GitHub | `POST /webhooks/github` | Issue/PR comments, issue creation, PR reviews |
| Linear | `POST /webhooks/linear` | Issue comments |
| Slack | `POST /webhooks/slack` | App mentions, direct messages |

Each webhook endpoint performs signature verification, event filtering, and dispatches background tasks for processing. All endpoints are defined in `agent/webapp.py` [agent/webapp.py:101]().

## Webhook Endpoint Architecture

```mermaid
graph TB
    subgraph "External Platforms"
        GitHub["GitHub<br/>Issues, PRs, Comments"]
        Linear["Linear<br/>Issue Comments"]
        Slack["Slack<br/>App Mentions"]
    end
    
    subgraph "FastAPI Server - agent/webapp.py"
        GitHubEP["POST /webhooks/github<br/>github_webhook()"]
        LinearEP["POST /webhooks/linear<br/>linear_webhook()"]
        SlackEP["POST /webhooks/slack<br/>slack_webhook()"]
        
        subgraph "Signature Verification"
            GitHubSig["verify_github_signature()<br/>X-Hub-Signature-256"]
            LinearSig["verify_linear_signature()<br/>Linear-Signature"]
            SlackSig["verify_slack_signature()<br/>X-Slack-Signature"]
        end
        
        subgraph "Event Filtering"
            GitHubFilter["Filter: @openswe mentions<br/>ALLOWED_GITHUB_ORGS"]
            LinearFilter["Filter: @openswe mentions<br/>LINEAR_TEAM_TO_REPO"]
            SlackFilter["Filter: app_mention events<br/>bot message exclusion"]
        end
        
        subgraph "Background Processing"
            GitHubBG["BackgroundTasks.add_task()<br/>process_github_issue()"]
            LinearBG["BackgroundTasks.add_task()<br/>process_linear_issue()"]
            SlackBG["BackgroundTasks.add_task()<br/>process_slack_mention()"]
        end
    end
    
    subgraph "Environment Variables"
        GitHubSecret["GITHUB_WEBHOOK_SECRET"]
        LinearSecret["LINEAR_WEBHOOK_SECRET"]
        SlackSecret["SLACK_SIGNING_SECRET"]
    end
    
    GitHub -->|"Webhook Event"| GitHubEP
    Linear -->|"Webhook Event"| LinearEP
    Slack -->|"Webhook Event"| SlackEP
    
    GitHubEP --> GitHubSig
    LinearEP --> LinearSig
    SlackEP --> SlackSig
    
    GitHubSecret -.->|"Used by"| GitHubSig
    LinearSecret -.->|"Used by"| LinearSig
    SlackSecret -.->|"Used by"| SlackSig
    
    GitHubSig --> GitHubFilter
    LinearSig --> LinearFilter
    SlackSig --> SlackFilter
    
    GitHubFilter --> GitHubBG
    LinearFilter --> LinearBG
    SlackFilter --> SlackBG
```

**Sources:** [agent/webapp.py:101-1150](), [agent/utils/github_comments.py:57](), [agent/webapp.py:117-121]()

## GitHub Webhook Configuration

### Required Secrets

The GitHub webhook endpoint requires `GITHUB_WEBHOOK_SECRET` to verify incoming requests [agent/webapp.py:118](). Generate a secure secret:

```bash
openssl rand -hex 32
```

Set this value as `GITHUB_WEBHOOK_SECRET` in your environment and use the same value when configuring the webhook in GitHub [INSTALLATION.md:62-65]().

**Sources:** [agent/webapp.py:118](), [INSTALLATION.md:62-65]()

### GitHub App Webhook Settings

Configure your GitHub App with the following webhook settings:

| Setting | Value |
|---------|-------|
| **Webhook URL** | `https://<your-domain>/webhooks/github` |
| **Webhook secret** | Value of `GITHUB_WEBHOOK_SECRET` |
| **Content type** | `application/json` |

Enable these webhook events:
- **Issue comment** — triggers on new issue comments
- **Pull request review** — triggers on PR review submissions
- **Pull request review comment** — triggers on inline PR review comments

**Sources:** [INSTALLATION.md:54-76](), [agent/webapp.py:1100-1150]()

### GitHub Signature Verification

```mermaid
sequenceDiagram
    participant GitHub as "GitHub Platform"
    participant FastAPI as "github_webhook()"
    participant Verifier as "verify_github_signature()"
    participant Secret as "GITHUB_WEBHOOK_SECRET"
    
    GitHub->>FastAPI: POST /webhooks/github<br/>X-Hub-Signature-256 header<br/>Request body
    FastAPI->>FastAPI: await request.body()
    FastAPI->>FastAPI: request.headers.get("X-Hub-Signature-256")
    FastAPI->>Verifier: verify_github_signature(body, signature, secret)
    Verifier->>Secret: Read GITHUB_WEBHOOK_SECRET
    Verifier->>Verifier: HMAC-SHA256(secret, body)
    Verifier->>Verifier: Compare expected vs signature
    
    alt Signature valid
        Verifier-->>FastAPI: True
        FastAPI->>FastAPI: Parse JSON payload
        FastAPI->>FastAPI: Filter event
    else Signature invalid
        Verifier-->>FastAPI: False
        FastAPI-->>GitHub: 401 Unauthorized
    end
```

The signature verification implementation in `agent/utils/github_comments.py` [agent/utils/github_comments.py:57-64]():

```python
def verify_github_signature(body: bytes, signature: str, *, secret: str) -> bool:
    if not secret:
        logger.warning("GITHUB_WEBHOOK_SECRET is not configured — rejecting webhook request")
        return False

    expected = "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
```

**Sources:** [agent/utils/github_comments.py:57-64](), [agent/webapp.py:1115-1118]()

### GitHub Event Filtering

The GitHub webhook handler filters events based on several criteria:

```mermaid
flowchart TD
    Start["Incoming GitHub Event"] --> CheckEvent{"Event Type?"}
    
    CheckEvent -->|"issues"| CheckIssueAction{"Action?"}
    CheckEvent -->|"issue_comment"| CheckComment["Check comment body"]
    CheckEvent -->|"pull_request_review"| CheckReview["Check review body"]
    CheckEvent -->|"pull_request_review_comment"| CheckPRComment["Check PR comment body"]
    CheckEvent -->|"Other"| Ignore1["Return 'ignored'"]
    
    CheckIssueAction -->|"opened"| CheckTitle["Check title/body for @openswe"]
    CheckIssueAction -->|"edited"| CheckChanges{"Changes to<br/>title or body?"}
    CheckIssueAction -->|"Other"| Ignore2["Return 'ignored'"]
    
    CheckChanges -->|"Yes"| CheckTitle
    CheckChanges -->|"No"| Ignore2
    
    CheckTitle -->|"Contains @openswe"| CheckOrg["Check ALLOWED_GITHUB_ORGS"]
    CheckTitle -->|"No @openswe"| Ignore3["Return 'ignored'"]
    
    CheckComment -->|"Contains @openswe"| CheckOrg
    CheckComment -->|"No @openswe"| Ignore4["Return 'ignored'"]
    
    CheckReview -->|"Contains @openswe"| CheckOrg
    CheckReview -->|"No @openswe"| Ignore5["Return 'ignored'"]
    
    CheckPRComment -->|"Contains @openswe"| CheckOrg
    CheckPRComment -->|"No @openswe"| Ignore6["Return 'ignored'"]
    
    CheckOrg -->|"Org allowed or<br/>no filter set"| CheckBot{"From bot user?"}
    CheckOrg -->|"Org not allowed"| Ignore7["Return 'ignored'"]
    
    CheckBot -->|"No"| Accept["BackgroundTasks.add_task()<br/>process_github_issue()"]
    CheckBot -->|"Yes"| Ignore8["Return 'ignored'"]
```

Key filtering code references:

- Event type check: [agent/webapp.py:1122-1127]()
- `@openswe` mention detection: Case-insensitive search for `@openswe` tags [agent/utils/github_comments.py:46]()
- Organization allowlist: [agent/webapp.py:137-141](), checked in [agent/webapp.py:1130-1135]()
- Bot detection: Checks if sender matches bot user patterns [agent/webapp.py:1140-1145]()

**Sources:** [agent/webapp.py:1100-1150](), [agent/utils/github_comments.py:46]()

## Linear Webhook Configuration

### Required Secrets

The Linear webhook requires two credentials:

1. **Webhook Secret** — for signature verification [agent/webapp.py:117]():
   ```bash
   openssl rand -hex 32
   ```
   Set as `LINEAR_WEBHOOK_SECRET`.

2. **API Key** — for fetching full issue details and posting comments [agent/webapp.py:162](). Generate from Linear Settings → API → Personal API keys. Set as `LINEAR_API_KEY`.

**Sources:** [agent/webapp.py:117](), [agent/webapp.py:162](), [INSTALLATION.md:176-185]()

### Linear Webhook Settings

Configure the webhook in Linear (Settings → API → Webhooks):

| Setting | Value |
|---------|-------|
| **Label** | `open-swe` |
| **URL** | `https://<your-domain>/webhooks/linear` |
| **Secret** | Value of `LINEAR_WEBHOOK_SECRET` |
| **Events** | Comments → Create (only) |

The webhook endpoint also provides a GET endpoint for verification: `GET /webhooks/linear` returns `{"status": "ok"}` [agent/webapp.py:951-954]().

**Sources:** [INSTALLATION.md:171-179](), [agent/webapp.py:951-954]()

### Linear Signature Verification

The signature is provided in the `Linear-Signature` header and verified using `verify_linear_signature` [agent/webapp.py:813-830]():

```python
def verify_linear_signature(body: bytes, signature: str, secret: str) -> bool:
    if not secret:
        logger.warning("LINEAR_WEBHOOK_SECRET is not configured — rejecting webhook request")
        return False
    
    expected = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
```

**Sources:** [agent/webapp.py:813-830](), [agent/webapp.py:844-847]()

### Linear Event Filtering

Linear webhooks are filtered to ensure the agent only responds to relevant human comments.

```mermaid
flowchart TD
    Start["Incoming Linear Webhook"] --> CheckType{"payload.type == 'Comment'?"}
    
    CheckType -->|"No"| Ignore1["Return 'ignored'"]
    CheckType -->|"Yes"| CheckAction{"payload.action == 'create'?"}
    
    CheckAction -->|"No"| Ignore2["Return 'ignored'"]
    CheckAction -->|"Yes"| CheckBot{"data.botActor present?"}
    
    CheckBot -->|"Yes"| Ignore3["Return 'ignored'"]
    CheckBot -->|"No"| CheckOwnBot["Check if comment starts<br/>with bot message prefix"]
    
    CheckOwnBot -->|"Yes (own bot message)"| Ignore4["Return 'ignored'"]
    CheckOwnBot -->|"No"| CheckMention{"Comment contains<br/>'@openswe'?"}
    
    CheckMention -->|"No"| Ignore5["Return 'ignored'"]
    CheckMention -->|"Yes"| CheckTeam["Fetch full issue details<br/>Get team and project"]
    
    CheckTeam --> LookupRepo["get_repo_config_from_team_mapping()<br/>LINEAR_TEAM_TO_REPO"]
    
    LookupRepo --> CheckOrg{"Org in ALLOWED_GITHUB_ORGS<br/>or no filter set?"}
    
    CheckOrg -->|"No"| Ignore6["Return 'ignored'"]
    CheckOrg -->|"Yes"| Accept["BackgroundTasks.add_task()<br/>process_linear_issue()"]
```

Bot message prefixes that are ignored include `🔐 **GitHub Authentication Required**` and `🤖 **Agent Response**` [agent/webapp.py:164-172]().

**Sources:** [agent/webapp.py:833-948](), [agent/webapp.py:164-172]()

### Team-to-Repository Mapping

Linear issues are routed to GitHub repositories based on the Linear team and project. Configure the mapping in `agent/utils/linear_team_repo_map.py` [agent/utils/linear_team_repo_map.py:39](). The `get_repo_config_from_team_mapping` function handles lookup [agent/webapp.py:175-198]().

The mapping supports:
- **Flat mapping**: Team name → repository config
- **Nested mapping**: Team name → project name → repository config
- **Default fallback**: Team name → default repository if project not found

**Sources:** [agent/webapp.py:175-198](), [agent/utils/linear_team_repo_map.py:39](), [INSTALLATION.md:187-202]()

## Slack Webhook Configuration

### Required Credentials

The Slack webhook requires several environment variables:

| Variable | Description |
|----------|-------------|
| `SLACK_BOT_TOKEN` | Bot User OAuth Token (`xoxb-...`) |
| `SLACK_SIGNING_SECRET` | Request signature verification secret [agent/webapp.py:119]() |
| `SLACK_BOT_USER_ID` | Bot's user ID (e.g., `U01234567`) [agent/webapp.py:120]() |
| `SLACK_BOT_USERNAME` | Bot's display name (e.g., `openswe`) [agent/webapp.py:121]() |

**Sources:** [agent/webapp.py:119-121](), [INSTALLATION.md:276-283]()

### Slack App Event Subscriptions

Configure in the Slack App settings:

| Setting | Value |
|---------|-------|
| **Request URL** | `https://<your-domain>/webhooks/slack` |
| **Subscribe to bot events** | `app_mention`, `message.im`, `message.mpim` |

The Slack webhook handles URL verification challenges automatically by returning the `challenge` parameter [agent/webapp.py:979-981]().

**Sources:** [INSTALLATION.md:208-273](), [agent/webapp.py:957-1046]()

### Slack Signature Verification

Slack uses request timestamp and HMAC-SHA256 for signature verification. The implementation in `agent/utils/slack.py` [agent/utils/slack.py:83]() includes signature verification logic called by the webapp.

**Sources:** [agent/utils/slack.py:83](), [agent/webapp.py:962-971]()

### Slack Event Filtering

```mermaid
flowchart TD
    Start["Incoming Slack Event"] --> CheckType{"payload.type?"}
    
    CheckType -->|"'url_verification'"| ReturnChallenge["Return challenge parameter"]
    CheckType -->|"'event_callback'"| GetEvent["Extract payload.event"]
    CheckType -->|"Other"| Ignore1["Return 'ignored'"]
    
    GetEvent --> CheckEventType{"event.type?"}
    
    CheckEventType -->|"'app_mention'"| ExtractFields["Extract channel_id, thread_ts, user_id, text"]
    CheckEventType -->|"'message'"| CheckUsername{"SLACK_BOT_USERNAME<br/>and @username in text?"}
    CheckEventType -->|"Other"| Ignore2["Return 'ignored'"]
    
    CheckUsername -->|"Yes"| ExtractFields
    CheckUsername -->|"No"| CheckUserID{"SLACK_BOT_USER_ID<br/>and <@USER_ID> in text?"}
    
    CheckUserID -->|"Yes"| ExtractFields
    CheckUserID -->|"No"| Ignore3["Return 'ignored'"]
    
    ExtractFields --> CheckBot{"event.subtype == 'bot_message'<br/>or event.bot_id present?"}
    
    CheckBot -->|"Yes"| Ignore4["Return 'ignored'"]
    CheckBot -->|"No"| CheckSelf{"user_id == bot_user_id?"}
    
    CheckSelf -->|"Yes"| Ignore5["Return 'ignored'"]
    CheckSelf -->|"No"| CheckRequired{"channel_id, thread_ts,<br/>event_ts all present?"}
    
    CheckRequired -->|"No"| Ignore6["Return 'ignored'"]
    CheckRequired -->|"Yes"| GetRepo["get_slack_repo_config()<br/>Parse message for 'repo:owner/name'"]
    
    GetRepo --> CheckOrg{"Org in ALLOWED_GITHUB_ORGS<br/>or no filter set?"}
    
    CheckOrg -->|"No"| Ignore7["Return 'ignored'"]
    CheckOrg -->|"Yes"| Accept["BackgroundTasks.add_task()<br/>process_slack_mention()"]
```

**Sources:** [agent/webapp.py:957-1046](), [agent/utils/slack.py:83]()

### Repository Resolution for Slack

Slack messages can specify a repository in three ways:
1. **Explicit syntax**: `repo:owner/name` or `repo owner/name` [agent/utils/repo.py:25-33]().
2. **GitHub URL**: Extract from `github.com/owner/name` URLs [agent/utils/repo.py:36-38]().
3. **Default**: Use `SLACK_REPO_OWNER` and `SLACK_REPO_NAME` [agent/webapp.py:124-125]().

The resolution logic is implemented in `get_slack_repo_config()` [agent/webapp.py:345-387]().

**Sources:** [agent/webapp.py:345-387](), [agent/utils/repo.py:11-42](), [INSTALLATION.md:285-292]()

## Security Considerations

### Signature Verification Enforcement

All three webhook endpoints **require** signature verification. Requests without valid signatures are rejected with HTTP 401 [agent/webapp.py:1115-1118](), [agent/webapp.py:844-847](), [agent/webapp.py:964-971]().

### Organization Allowlist

The `ALLOWED_GITHUB_ORGS` environment variable restricts which GitHub organizations the agent can operate on [agent/webapp.py:137-141](). If set, only repositories belonging to the specified organizations are accepted [agent/webapp.py:297-306]().

**Sources:** [agent/webapp.py:137-141](), [agent/webapp.py:297-306]()

## Testing Webhook Configuration

### Local Development with ngrok

For local development, use ngrok to expose your local server to the internet [INSTALLATION.md:25-37]():

```bash
ngrok http 2024 --url https://your-subdomain.ngrok.dev
```

Configure all webhook URLs to point to `https://your-subdomain.ngrok.dev/webhooks/{platform}`.

### Verification Endpoints

Test webhook connectivity:

| Endpoint | Method | Response |
|----------|--------|----------|
| `/webhooks/linear` | GET | `{"status": "ok", "message": "Linear webhook endpoint is active"}` [agent/webapp.py:951-954]() |

**Sources:** [agent/webapp.py:951-954](), [INSTALLATION.md:358-365]()

---

# Page: LangGraph Server Deployment

# LangGraph Server Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CUSTOMIZATION.md](CUSTOMIZATION.md)
- [INSTALLATION.md](INSTALLATION.md)
- [Makefile](Makefile)
- [README.md](README.md)
- [agent/middleware/exclude_tools.py](agent/middleware/exclude_tools.py)
- [evals/reviewer/judge.py](evals/reviewer/judge.py)
- [langgraph.json](langgraph.json)

</details>



This page covers deployment options for the LangGraph orchestration layer, including LangGraph Cloud and self-hosted configurations. It explains how the FastAPI webapp connects to the LangGraph server and how agent graphs are defined via the `langgraph.json` configuration.

---

## Deployment Architecture Overview

The Open SWE system separates webhook handling (FastAPI) from agent orchestration (LangGraph Server) into two distinct layers that communicate over HTTP. The `langgraph.json` file defines the entry points for the graph logic, the reviewer logic, and the web application.

Title: System Deployment Architecture
```mermaid
graph TB
    subgraph "Webhook Layer - FastAPI"
        WebApp["app<br/>agent/webapp.py"]
        WebhookHandlers["Webhook Handlers<br/>POST /webhooks/*"]
        Client["get_client()<br/>langgraph_sdk.get_client"]
    end
    
    subgraph "Orchestration Layer - LangGraph Server"
        LGServer["LangGraph Server<br/>Port 2024"]
        GraphAgent["get_agent()<br/>agent/server.py"]
        GraphReviewer["get_reviewer_agent()<br/>agent/reviewer.py"]
        Store["LangGraph Store<br/>Message Queue"]
        Checkpoints["Checkpointer<br/>Thread State"]
    end
    
    subgraph "Agent Execution"
        DeepAgent["create_deep_agent<br/>agent/server.py"]
        Sandbox["Sandbox Backend<br/>SandboxBackendProtocol"]
    end
    
    WebApp --> WebhookHandlers
    WebhookHandlers --> Client
    Client -->|"runs.create()"| LGServer
    
    LGServer --> GraphAgent
    LGServer --> GraphReviewer
    LGServer --> Store
    LGServer --> Checkpoints
    
    GraphAgent --> DeepAgent
    DeepAgent --> Sandbox
```
**Sources:** [langgraph.json:4-12](), [agent/server.py:3-23](), [INSTALLATION.md:12-13]()

---

## LangGraph Configuration File

The `langgraph.json` file at the project root is the manifest used by the LangGraph CLI and LangGraph Cloud to locate the agent logic and the web server.

| Key | Value | Purpose |
|-----|-------|---------|
| `graphs.agent` | `"agent.server:get_agent"` | Points to the factory function that returns the compiled SWE agent [langgraph.json:5](). |
| `graphs.reviewer` | `"agent.reviewer:get_reviewer_agent"` | Points to the automated PR reviewer agent [langgraph.json:6](). |
| `http.app` | `"agent.webapp:app"` | Points to the FastAPI instance handling webhooks and dashboard API [langgraph.json:11](). |
| `python_version` | `"3.12"` | Specifies the runtime environment [langgraph.json:3](). |
| `dependencies` | `["."]` | Includes the local package for imports [langgraph.json:9](). |

**Example langgraph.json:**
[langgraph.json:1-14]()

**Sources:** [langgraph.json:1-14]()

---

## Connection Between Components

The FastAPI webhook layer in `agent/webapp.py` acts as a client to the LangGraph Server. It translates external events (Slack/GitHub/Linear) into LangGraph "runs".

### Execution Environment Resolution
During development, the system is typically run using the LangGraph CLI. The `Makefile` provides a `dev` target which executes `langgraph dev` [Makefile:10-11](). This starts the LangGraph server on port 2024 by default [INSTALLATION.md:13]().

### Run Creation Flow
When a webhook is received, the webapp triggers a run. For example, the `get_agent` function is invoked by the server to build the graph for a specific thread [langgraph.json:5]().

Title: Webapp to Server Communication
```mermaid
sequenceDiagram
    participant Web as Webhook Handler<br/>agent/webapp.py
    participant SDK as LangGraph SDK<br/>get_client()
    participant LGS as LangGraph Server<br/>(Remote or Local)
    participant Srv as Agent Factory<br/>agent/server.py:get_agent
    
    Web->>SDK: get_client()
    Web->>SDK: runs.create(thread_id, "agent", ...)
    SDK->>LGS: POST /threads/{tid}/runs
    LGS->>Srv: Invoke get_agent()
    Srv-->>LGS: Return Compiled Graph
    LGS->>LGS: Execute Graph Nodes
```
**Sources:** [langgraph.json:5-11](), [Makefile:10-15](), [INSTALLATION.md:12-13]()

---

## Deployment Options

### 1. LangGraph Cloud (Managed)
LangGraph Cloud is the recommended production path. It automatically reads `langgraph.json` to provision the infrastructure.

*   **Infrastructure:** Managed by LangChain.
*   **Scaling:** Automatic based on run volume.
*   **Persistence:** Managed checkpointer for thread state.
*   **Webhooks:** The FastAPI app defined in `agent.webapp:app` is automatically hosted alongside the graph [langgraph.json:11]().

### 2. Self-Hosted (CLI/Docker)
You can run the server manually using the `langgraph` CLI or within a Docker container.

*   **CLI Command:** `uv run langgraph dev` [Makefile:11]().
*   **Docker:** A `Dockerfile` is provided to containerize the application for custom infrastructure [INSTALLATION.md:138-146]().
*   **Port:** Defaults to `2024` for the LangGraph server [INSTALLATION.md:30]().

---

## The Graph Entry Point: get_agent()

The `get_agent` function in `agent/server.py` is the critical link between the server and the agent logic. It is the factory used to instantiate the `deepagent` with specific configurations.

### Core Responsibilities
1.  **Model Configuration:** Resolves the LLM to use (e.g., GPT-4o, Claude) via `make_model` [CUSTOMIZATION.md:7-13]().
2.  **Tool Setup:** Configures the suite of tools including `http_request`, `fetch_url`, and messaging tools [CUSTOMIZATION.md:15]().
3.  **Middleware Injection:** Attaches logic for error handling (`ToolErrorMiddleware`) and message queueing (`check_message_queue_before_model`) [CUSTOMIZATION.md:17-22]().
4.  **Sandbox Integration:** Connects the agent to the isolated execution environment [CUSTOMIZATION.md:16]().

Title: Agent Initialization Sequence
```mermaid
graph LR
    Server["LangGraph Server"] -->|"Invoke"| GetAgent["get_agent()<br/>agent/server.py"]
    GetAgent --> Model["make_model()<br/>agent/utils/model.py"]
    GetAgent --> SB["create_sandbox_backend()<br/>agent/utils/sandbox.py"]
    GetAgent --> DeepAgent["create_deep_agent()<br/>deepagents"]
    DeepAgent --> Pregel["Compiled Graph"]
    Pregel --> Server
```
**Sources:** [CUSTOMIZATION.md:3-24](), [langgraph.json:5](), [agent/middleware/exclude_tools.py:33-43]()

---

## Webapp Mounting

The `agent.webapp:app` is a FastAPI instance that provides the external interface for webhooks.

### Key Endpoints
*   **GitHub:** Processes PR comments and issue events (configured in GitHub App settings) [INSTALLATION.md:61]().
*   **Linear:** Processes issue updates and comments [README.md:102-103]().
*   **Slack:** Processes mentions and thread replies [README.md:101]().

When deployed, the LangGraph server uses the `http.app` key in `langgraph.json` to mount this FastAPI application [langgraph.json:11](). This allows the system to receive webhooks and manage agent threads within a unified deployment.

**Sources:** [langgraph.json:10-12](), [INSTALLATION.md:61](), [README.md:99-106]()

---

# Page: Docker Deployment

# Docker Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [AGENTS.md](AGENTS.md)
- [CLAUDE.md](CLAUDE.md)
- [Dockerfile](Dockerfile)
- [agent/tools/fetch_url.py](agent/tools/fetch_url.py)
- [agent/tools/http_request.py](agent/tools/http_request.py)
- [tests/test_http_security.py](tests/test_http_security.py)

</details>



This page documents the Docker containerization of Open SWE, including the Dockerfile structure, image build process, and deployment patterns. The Docker image serves a dual purpose: it provides the execution environment for agent sandboxes (where code is cloned and edited) and can be used to deploy the Open SWE webhook server itself.

---

## Dockerfile Architecture

The Open SWE Dockerfile defines a comprehensive multi-runtime environment. It is designed to support the diverse language ecosystems that an agent might encounter, specifically Python, Node.js, and Go.

### System Components and Tools

The Dockerfile builds upon a Python base and layers in essential development tools and runtimes.

| Layer | Component | Version / Package | File Reference |
|:--- |:--- |:--- |:--- |
| **Base** | OS | `python:3.14.0-slim-trixie` | [Dockerfile:1]() |
| **System** | VCS | `git`, `openssh-client` | [Dockerfile:12-19]() |
| **System** | Utilities | `curl`, `wget`, `jq`, `unzip`, `zip` | [Dockerfile:13-22]() |
| **Runtime** | Docker CLI | `5:29.1.5-1~debian.13~trixie` | [Dockerfile:3]() |
| **Runtime** | GitHub CLI | `gh` (2.83.1) | [Dockerfile:7]() |
| **Runtime** | Python Tool | `uv` (0.9.26) | [Dockerfile:5]() |
| **Runtime** | Node.js | `22.22.0` | [Dockerfile:4]() |
| **Runtime** | JS Tool | `yarn` (4.12.0) | [Dockerfile:6]() |
| **Runtime** | Go | `1.23.5` | [Dockerfile:69]() |

### Build Logic Flow

The build process handles architecture-specific binaries (AMD64 vs ARM64) for tools like `gh`, `uv`, and `go` to ensure compatibility across different deployment environments.

```mermaid
graph TD
    subgraph "Base Image"
        A["python:3.14.0-slim-trixie"]
    end

    subgraph "Apt Dependencies"
        B["git, curl, build-essential, jq, zip"]
    end

    subgraph "Tool Installation"
        C["Docker CLI (apt)"]
        D["GitHub CLI (gh binary)"]
        E["uv (binary fetch)"]
        F["Node.js & Yarn (corepack)"]
        G["Go (tarball)"]
    end

    subgraph "Configuration"
        H["PATH Setup"]
        I["WORKDIR /workspace"]
    end

    A --> B
    B --> C
    B --> D
    B --> E
    B --> F
    B --> G
    C & D & E & F & G --> H
    H --> I
```
**Sources:** [Dockerfile:1-88]()

---

## Building the Docker Image

### Build Command
The image is built using standard Docker commands. It supports build arguments to override tool versions if necessary.

```bash
docker build -t open-swe:latest .
```

### Architecture Detection
The Dockerfile uses `dpkg --print-architecture` to dynamically select the correct binary architecture strings (e.g., `aarch64-unknown-linux-gnu` for `uv` on ARM64) during the build process.

```bash
# Example of architecture mapping logic in Dockerfile
arch="$(dpkg --print-architecture)";
case "${arch}" in
  amd64) uv_arch="x86_64-unknown-linux-gnu" ;;
  arm64) uv_arch="aarch64-unknown-linux-gnu" ;;
esac;
```
**Sources:** [Dockerfile:34-44](), [Dockerfile:46-59]()

---

## Webhook Server Deployment

When deployed as the primary application container, the image runs the FastAPI webapp.

### Entrypoints and Routes
The application is served as defined in the `AGENTS.md` and `CLAUDE.md` documentation. The FastAPI app is located at `agent.webapp:app`.

| Component | Logic Location | Purpose |
|:--- |:--- |:--- |
| **Main App** | `agent/webapp.py` | FastAPI application and webhook endpoints |
| **Dashboard** | `agent/dashboard/` | React frontend and management API |
| **Dev Command** | `make dev` | Serves graphs + FastAPI via LangGraph dev |
| **Run Command** | `make run` | Direct Uvicorn execution of the webapp |

**Sources:** [AGENTS.md:17-34](), [CLAUDE.md:17-34]()

---

## Sandbox and Tool Execution

The Docker image provides the environment where tools like `http_request` and `fetch_url` are executed.

### Network Security within the Container
To prevent the agent from performing Server-Side Request Forgery (SSRF), the `http_request` tool implements strict DNS pinning and IP validation.

```mermaid
sequenceDiagram
    participant Tool as "http_request.py"
    participant DNS as "socket.getaddrinfo"
    participant Pin as "_pin_dns"
    participant HTTP as "requests.Session"

    Tool->>DNS: Resolve hostname
    DNS-->>Tool: addr_infos (IP list)
    Note over Tool: Check if IP is private/loopback
    Tool->>Pin: Pin hostname to validated IPs
    Pin->>HTTP: Override urllib3.create_connection
    Tool->>HTTP: Execute GET/POST
    HTTP-->>Tool: Response
```
**Sources:** [agent/tools/http_request.py:125-162](), [agent/tools/http_request.py:91-123]()

### Tool Security Logic
1. **Validation**: `_resolve_and_validate(url)` checks every resolved address to ensure it is not private, loopback, link-local, or reserved. [agent/tools/http_request.py:125-162]()
2. **DNS Pinning**: `_pin_dns` uses a thread-local stack to ensure that the connection layer honors the validated IPs, preventing DNS-rebinding attacks. [agent/tools/http_request.py:91-123]()
3. **Safe Redirects**: `_request_with_safe_redirects` re-validates and re-pins DNS for every hop in a redirect chain. [agent/tools/http_request.py:180-210]()

**Sources:** [agent/tools/http_request.py:28-88](), [agent/tools/fetch_url.py:34-46]()

---

## Production Deployment Patterns

### Infrastructure Requirements
As documented in the architecture overview, Open SWE requires a persistent environment for its sandboxes.

- **Sandbox Lifecycle**: Managed via `ensure_sandbox_for_thread` which persists `sandbox_id` in thread metadata. [AGENTS.md:46-53]()
- **GitHub Proxy**: For `SANDBOX_TYPE=langsmith`, the system configures a proxy to inject credentials so real tokens never reside in the sandbox environment. [AGENTS.md:54-58]()

### Exclusions
To keep the image slim and secure, the `.dockerignore` file excludes sensitive files and local development artifacts:
- Environment files (`.env`, `.env.*`)
- Security credentials (`*.pem`, `credentials.json`)
- Virtual environments and caches (`.venv`, `node_modules`, `__pycache__`)

**Sources:** [.dockerignore:1-15]()

---

# Page: Development

# Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [.github/workflows/pr_lint.yml](.github/workflows/pr_lint.yml)
- [AGENTS.md](AGENTS.md)
- [CLAUDE.md](CLAUDE.md)
- [LICENSE](LICENSE)

</details>



This guide covers the development workflow for contributors and developers working on the Open SWE codebase. It includes local environment setup, testing procedures, CI/CD pipeline configuration, and monorepo structure. For deployment of Open SWE in production environments, see [Deployment](#11). For customization and extension of Open SWE components, see [Customization Guide](#9).

---

## Overview

Open SWE uses a modern development stack with separate toolchains for Python backend code and JavaScript frontend code. The Python components use `uv` for fast, reliable dependency management, while the JavaScript/TypeScript components are organized within a monorepo structure. A `Makefile` provides a unified interface for common development tasks like linting, formatting, and testing.

**Development Workflow:**

```mermaid
graph LR
    "Clone"["Clone repository"]
    "Setup"["Install dependencies<br/>(uv sync)"]
    "Code"["Write code"]
    "Lint"["Run linters<br/>(make lint)"]
    "Format"["Apply formatting<br/>(make format)"]
    "Test"["Run tests<br/>(make test)"]
    "Commit"["Commit changes"]
    "Push"["Push to GitHub"]
    "CI"["CI/CD pipeline<br/>(GitHub Actions)"]
    
    "Clone" --> "Setup"
    "Setup" --> "Code"
    "Code" --> "Lint"
    "Lint" --> "Format"
    "Format" --> "Test"
    "Test" --> "Commit"
    "Commit" --> "Push"
    "Push" --> "CI"
    "CI" --> "Code"
```

**Sources:** [AGENTS.md:15-24](), [.github/workflows/ci.yml:1-49]()

---

## 12.1. Local Development Setup

Setting up a local environment requires configuring the Python backend. The project relies on `uv` for Python dependency management. For details, see [Local Development Setup](#12.1).

### Prerequisites

| Tool | Purpose | Reference |
|------|---------|-----------|
| **UV** | Python package manager | [.github/workflows/ci.yml:22-22]() |
| **Make** | Task runner for dev commands | [AGENTS.md:15-24]() |
| **Ruff** | Linting and formatting | [AGENTS.md:13-13]() |

### Local Execution Modes
Developers can run the full LangGraph stack or just the FastAPI webapp.
- `make dev`: Runs `uv run langgraph dev`, serving all three graphs (`agent`, `reviewer`, `review_style_analyzer`) and the FastAPI app [AGENTS.md:17-17]().
- `make run`: Runs `uvicorn agent.webapp:app`, serving only the FastAPI webhooks and dashboard API [AGENTS.md:18-18]().

**Sources:** [AGENTS.md:1-44](), [.github/workflows/ci.yml:22-26]()

---

## 12.2. Testing

Open SWE includes a test suite that validates agent behavior, tool functionality, and middleware logic. The testing infrastructure is driven by `pytest` with `asyncio` support. For details, see [Testing](#12.2).

### Test Commands

| Command | Action |
|---------|--------|
| `make test` | Runs the full suite via `uv run pytest -vvv tests/` [AGENTS.md:19-19]() |
| `make test TEST_FILE=path/to/test.py` | Runs a specific test file [AGENTS.md:20-20]() |

The CI pipeline automatically runs `make test` on every pull request to ensure no regressions [.github/workflows/ci.yml:48-48]().

**Sources:** [AGENTS.md:13-21](), [.github/workflows/ci.yml:39-49]()

---

## 12.3. CI/CD Pipeline

The CI/CD pipeline is implemented using GitHub Actions. It enforces code quality through automated linting, semantic PR titles, and unit testing. For details, see [CI/CD Pipeline](#12.3).

### Workflow Jobs

```mermaid
graph TB
    subgraph "Agent CI [.github/workflows/ci.yml]"
        "Lint"["Agent lint"]
        "Format"["Agent format check"]
        "Tests"["Agent unit tests"]
    end

    subgraph "PR Quality [.github/workflows/pr_lint.yml]"
        "PRTitle"["Validate PR Title"]
    end
    
    "Lint" --> "L_Cmd"["make lint"]
    "Format" --> "F_Cmd"["make format-check"]
    "Tests" --> "T_Cmd"["make test"]
    "PRTitle" --> "S_Cmd"["Semantic PR Check"]
```

The pipeline uses `astral-sh/setup-uv` to manage the Python environment and `uv sync --locked --extra dev` to ensure a consistent environment across runs [.github/workflows/ci.yml:22-24]().

**Sources:** [.github/workflows/ci.yml:1-49](), [.github/workflows/pr_lint.yml:1-42]()

---

## 12.4. Monorepo Structure

Open SWE is organized as a monorepo containing the core agent logic, a dashboard frontend, and various integration packages. For details, see [Monorepo Structure](#12.4).

### Code Entity Space Mapping

```mermaid
graph TD
    "Root"["/"]
    
    subgraph "Core Agent Logic"
        "AgentDir"["agent/"]
        "Server"["agent/server.py"]
        "Reviewer"["agent/reviewer.py"]
        "Webapp"["agent/webapp.py"]
    end
    
    subgraph "Frontend & UI"
        "UIDir"["ui/"]
        "Dashboard"["agent/dashboard/"]
    end
    
    subgraph "Configuration"
        "LGJson"["langgraph.json"]
        "PyProject"["pyproject.toml"]
        "AgentsMD"["AGENTS.md"]
    end
    
    "Root" --> "AgentDir"
    "Root" --> "UIDir"
    "Root" --> "LGJson"
    "AgentDir" --> "Server"
    "AgentDir" --> "Reviewer"
    "AgentDir" --> "Webapp"
    "AgentDir" --> "Dashboard"
```

**Sources:** [AGENTS.md:26-44](), [.dockerignore:1-15]()

---

## 12.5. Operational Scripts

The codebase includes utility scripts in the `scripts/` directory for PR analytics and snapshot management. For details, see [Operational Scripts](#12.5).

### PR Analytics Utilities
- **`export_pr_urls.py`**: Extracts PR URLs from LangGraph threads for performance tracking.
- **`check_pr_merge_status.py`**: Performs bulk status checks via the GitHub API to verify if agent-produced PRs were successful.

These utilities are essential for evaluating the agent's real-world impact and identifying failure patterns in production.

---

## Development Best Practices

### Code Quality Checklist

Before committing changes, run the following checks locally:

```bash
# 1. Apply formatting and fix lint errors
make format

# 2. Verify linting (run by CI)
make lint

# 3. Run unit tests
make test
```

### Dependency Management

**Python:** Always use `uv sync --locked` to ensure your local environment matches the `uv.lock` file [.github/workflows/ci.yml:24-24]().

**Commits:** Follow semantic commit conventions (e.g., `feat:`, `fix:`, `docs:`) as enforced by the PR Title Lint workflow [.github/workflows/pr_lint.yml:19-31]().

**Sources:** [AGENTS.md:13-24](), [.github/workflows/ci.yml:1-49](), [.github/workflows/pr_lint.yml:1-42]()

---

# Page: Local Development Setup

# Local Development Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [AGENTS.md](AGENTS.md)
- [CLAUDE.md](CLAUDE.md)
- [Makefile](Makefile)
- [agent/integrations/langsmith.py](agent/integrations/langsmith.py)
- [agent/middleware/exclude_tools.py](agent/middleware/exclude_tools.py)
- [evals/reviewer/judge.py](evals/reviewer/judge.py)
- [langgraph.json](langgraph.json)
- [pyproject.toml](pyproject.toml)
- [uv.lock](uv.lock)

</details>



This guide provides a step-by-step walkthrough for setting up a local development environment for Open SWE. It covers dependency management using `uv`, configuration of the three primary LangGraph agents, and the architecture of the local development loop.

---

## Prerequisites

Open SWE requires the following tools for development:

| Tool | Purpose | Minimum Version |
|------|---------|----------------|
| **Python** | Backend services and agent runtime | 3.11+ |
| **UV** | Python package manager and build tool | Latest |
| **LangGraph CLI** | Local development server for graphs | 0.4.24+ |
| **Ruff** | Linting and formatting | 0.15.12+ |

The project specifies Python 3.11+ in `pyproject.toml` [pyproject.toml:6-6](), though the `langgraph.json` configuration pins the runtime to 3.12 [langgraph.json:3-3]().

---

## Installation

Open SWE uses `uv` for high-performance dependency management.

### 1. Install Python Dependencies
Run the following command to install the core dependencies, including `deepagents`, `langgraph`, and `fastapi` [pyproject.toml:8-28]().

```bash
make install
```
*Implementation note: This executes `uv pip install -e .` [Makefile:16-17]().*

### 2. Install Development Tools
To include testing and linting tools like `pytest` and `ruff` [pyproject.toml:31-36]():

```bash
uv pip install -e ".[dev]"
```

**Sources:** [pyproject.toml:1-36](), [Makefile:16-17](), [uv.lock:1-7]()

---

## Local Development Workflow

Open SWE is structured as a multi-graph LangGraph application. The local development environment serves the coding agent, the reviewer agent, and the FastAPI webhook app simultaneously.

### 1. Running the Development Server
The primary way to develop locally is using the LangGraph dev server, which monitors the entrypoints defined in `langgraph.json` [langgraph.json:4-12]().

```bash
make dev
```
*Implementation note: This executes `uv run langgraph dev` [Makefile:10-11]().*

### 2. Service Architecture
When running `make dev`, the system orchestrates the following components:

**Local Service Composition**
```mermaid
graph TD
    subgraph "LangGraph Runtime"
        AgentGraph["agent.server:get_agent"]
        ReviewerGraph["agent.reviewer:get_reviewer_agent"]
        StyleGraph["agent.review_style_analyzer:get_review_style_analyzer"]
    end

    subgraph "Web Application"
        FastAPI["agent.webapp:app"]
        Dashboard["agent/dashboard/router"]
    end

    subgraph "Local Resources"
        Env[".env file"]
        Sandbox["SandboxBackend (Local/LangSmith)"]
    end

    FastAPI --> AgentGraph
    FastAPI --> ReviewerGraph
    FastAPI --> Dashboard
    AgentGraph --> Sandbox
    ReviewerGraph --> Sandbox
    AgentGraph -.-> Env
```

**Sources:** [langgraph.json:1-14](), [AGENTS.md:15-34](), [Makefile:10-14]()

---

## Sandbox Configuration

Open SWE supports multiple sandbox providers. For local development, you typically use `local` or `langsmith`.

### 1. Provider Selection
The sandbox type is controlled by the `SANDBOX_TYPE` environment variable. The system uses a factory pattern to instantiate the backend [AGENTS.md:55-55]().

### 2. LangSmith Sandbox Setup
If using `SANDBOX_TYPE=langsmith`, the system configures a proxy to inject GitHub credentials so tokens are never stored on the sandbox disk [agent/integrations/langsmith.py:98-108]().

**Sandbox Initialization Flow**
```mermaid
sequenceDiagram
    participant S as agent.server:get_agent
    participant I as agent.integrations.langsmith
    participant P as LangSmith API
    participant G as GitHub Proxy

    S->>I: create_langsmith_sandbox(sandbox_id, token)
    I->>P: get_or_create(snapshot_id, vcpus, mem)
    P-->>I: sandbox_id
    I->>G: _configure_github_proxy(sandbox_id, token)
    G-->>I: proxy_rules applied
    I-->>S: SandboxBackendProtocol
```

**Sources:** [agent/integrations/langsmith.py:126-170](), [AGENTS.md:54-58]()

---

## Configuration Reference

### Environment Variables (`.env`)
The `langgraph.json` file points to a `.env` file for local secrets [langgraph.json:13-13](). Key variables include:

| Variable | Description |
|----------|-------------|
| `SANDBOX_TYPE` | `local`, `langsmith`, `modal`, `daytona`, `runloop` [AGENTS.md:55-55]() |
| `LANGSMITH_API_KEY` | Required for LangSmith sandboxes and tracing [agent/integrations/langsmith.py:25-31]() |
| `DEFAULT_SANDBOX_VCPUS` | CPU allocation for LangSmith boxes (default: 2) [agent/integrations/langsmith.py:19-19]() |
| `DEFAULT_SANDBOX_MEM_BYTES` | Memory allocation (default: ~8GiB) [agent/integrations/langsmith.py:20-20]() |

### Command Cheat Sheet
| Task | Command |
|------|---------|
| Start All Graphs | `make dev` |
| Start Webapp Only | `make run` |
| Run All Tests | `make test` |
| Lint Code | `make lint` |
| Format Code | `make format` |

**Sources:** [Makefile:1-69](), [AGENTS.md:15-24](), [agent/integrations/langsmith.py:18-22]()

---

## Code Quality and Safety

### Linting and Formatting
The project enforces strict standards via `ruff` with a line length of 100 [pyproject.toml:48-64]().
- **Check**: `make lint`
- **Fix**: `make format`

### Testing
Tests are powered by `pytest` with `asyncio` support [pyproject.toml:66-68]().
- **Full suite**: `uv run pytest -vvv tests/` [Makefile:27-27]()
- **Single test**: `uv run pytest -vvv tests/test_file.py::test_name` [AGENTS.md:21-21]()

**Sources:** [pyproject.toml:48-69](), [Makefile:25-37](), [AGENTS.md:11-24]()

---

# Page: Testing

# Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [.github/workflows/pr_lint.yml](.github/workflows/pr_lint.yml)
- [LICENSE](LICENSE)
- [agent/dashboard/enabled_repos.py](agent/dashboard/enabled_repos.py)
- [tests/conftest.py](tests/conftest.py)
- [tests/test_reviewer_eval_run.py](tests/test_reviewer_eval_run.py)

</details>



This document covers the testing infrastructure in Open SWE, including test organization, how to run tests locally, test dependencies, and specialized testing for components like the Reviewer Agent.

## Overview

Open SWE uses a combination of unit tests, code quality checks (linting and formatting), and automated test execution through `Make` targets. The testing strategy focuses on validating the core agent logic, the webhooks/dashboard API, and the evaluation of reviewer performance.

The testing infrastructure is built on:
- **pytest**: Primary Python test framework.
- **ruff**: Python linter and formatter used for static analysis.
- **uv**: Package manager that handles test dependencies and synchronization.
- **Make**: Command orchestration layer for standardizing test execution.
- **GitHub Actions**: Automated CI execution on push and pull requests.

**Sources:**
- [.github/workflows/ci.yml:1-49]()

## Test Organization

Tests are located in the `tests/` directory at the root of the repository. The project follows standard Python testing conventions where test files are named with the `test_` prefix.

### Shared Fixtures and Mocks
Open SWE uses a central `conftest.py` to define shared fixtures that manage the test environment state.

- **Repo Enablement Mock**: To avoid dependency on a live LangGraph Store during tests, a global autouse fixture `_default_enable_review_repos` is provided. It patches `agent.webapp.is_review_repo_enabled` to return `True` by default [tests/conftest.py:10-26](). This allows tests to bypass the opt-in gate that usually filters repositories based on the dashboard configuration [agent/dashboard/enabled_repos.py:63-69]().

### Reviewer Evaluation Tests
Specific tests exist for the reviewer agent's evaluation infrastructure. For example, `tests/test_reviewer_eval_run.py` validates:
- **Configuration Coercion**: The `_coerce_config` function correctly parses and filters evaluation parameters like `model_id`, `severity_threshold`, and `max_concurrency` [tests/test_reviewer_eval_run.py:9-37]().
- **Environment Injection**: The `_apply_config_to_env` function correctly maps configuration keys to the environment variables required by the evaluation runner, such as `REVIEWER_EVAL_MODEL_ID` and `LANGGRAPH_URL` [tests/test_reviewer_eval_run.py:40-61]().

**Sources:**
- [tests/conftest.py:1-27]()
- [tests/test_reviewer_eval_run.py:1-61]()
- [agent/dashboard/enabled_repos.py:63-69]()

## Running Tests Locally

### Test Execution Flow

The following diagram illustrates how a developer interacts with the testing infrastructure and how `uv` manages the underlying environment.

**Natural Language to Code Entity Space: Test Invocation**
```mermaid
graph TB
    Developer["Developer"]
    
    subgraph "Make Targets (Makefile)"
        MakeTest["make test"]
        MakeLint["make lint"]
        MakeFormat["make format-check"]
    end
    
    subgraph "Execution Layer"
        UV["uv sync --locked --extra dev"]
        Pytest["pytest"]
        RuffCheck["ruff check"]
        RuffFormat["ruff format --check"]
    end
    
    subgraph "Code Entities"
        AgentCode["agent/ directory"]
        TestFiles["tests/test_*.py"]
        Conftest["tests/conftest.py"]
    end
    
    Developer --> MakeTest
    Developer --> MakeLint
    Developer --> MakeFormat
    
    MakeTest --> UV
    MakeLint --> UV
    MakeFormat --> UV
    
    UV --> Pytest
    UV --> RuffCheck
    UV --> RuffFormat
    
    Pytest --> TestFiles
    Pytest --> Conftest
    RuffCheck --> AgentCode
    RuffFormat --> AgentCode
```
**Sources:**
- [.github/workflows/ci.yml:16-49]()
- [tests/conftest.py:7-11]()

### Basic Test Commands

To run tests locally, use the following commands. Each command ensures dependencies are synchronized via `uv sync` before execution.

```bash
# Install development dependencies and sync lockfile
uv sync --locked --extra dev

# Run the unit test suite
make test

# Run static analysis (linting)
make lint

# Verify code formatting without applying changes
make format-check
```

**Sources:**
- [.github/workflows/ci.yml:24-26]()
- [.github/workflows/ci.yml:35-37]()
- [.github/workflows/ci.yml:46-48]()

## CI Test Execution

The GitHub Actions CI pipeline (`Agent CI`) automates the validation process on every push to `main` and on all pull requests.

### CI Job Matrix

| Job Name | Make Target | Description |
|----------|-------------|-------------|
| `lint` | `make lint` | Checks for programmatic and stylistic errors using `ruff`. |
| `format` | `make format-check` | Ensures code adheres to the project's formatting standard. |
| `unit-tests` | `make test` | Executes the `pytest` suite. |

### PR Title Linting
In addition to code tests, a specialized `PR Title Lint` workflow ensures that pull request titles follow semantic versioning conventions (e.g., `feat:`, `fix:`, `docs:`) [/.github/workflows/pr_lint.yml:1-31](). This helps in generating clean changelogs and maintaining repository history.

**Sources:**
- [.github/workflows/ci.yml:17-49]()
- [.github/workflows/pr_lint.yml:1-42]()

## Environment Considerations

Testing Open SWE requires specific environment handling due to its reliance on external services and stateful components.

1. **LangGraph Store Mocking**: Since the LangGraph Store (used for persistence of enabled repos and review styles) is not available in a standard test runner, tests must mock the `agent.dashboard.enabled_repos` functions [tests/conftest.py:26-26]().
2. **Environment Variable Injection**: The reviewer evaluation system relies heavily on environment variables. Tests in `tests/test_reviewer_eval_run.py` use `unittest.mock.patch.dict` to verify that configuration objects are correctly transformed into environment variables for the subprocesses or API clients [tests/test_reviewer_eval_run.py:41-42]().

**Sources:**
- [tests/conftest.py:10-27]()
- [tests/test_reviewer_eval_run.py:40-61]()

---

# Page: CI/CD Pipeline

# CI/CD Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/dependabot.yml](.github/dependabot.yml)
- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [.github/workflows/pr_lint.yml](.github/workflows/pr_lint.yml)
- [.github/workflows/promote_main_to_prod.yml](.github/workflows/promote_main_to_prod.yml)
- [LICENSE](LICENSE)

</details>



This page documents the continuous integration and continuous deployment (CI/CD) workflows for Open SWE. The CI/CD pipeline automates code quality checks, formatting validation, test execution, and automated branch promotion using GitHub Actions.

---

## Overview

The Open SWE CI/CD infrastructure consists of several specialized workflows that manage the lifecycle of the codebase from pull request creation to production deployment.

1.  **Agent CI** [`.github/workflows/ci.yml:1-49`()] — Runs linting, formatting, and unit tests on every push and PR.
2.  **PR Title Lint** [`.github/workflows/pr_lint.yml:1-42`()] — Enforces semantic versioning standards for pull request titles.
3.  **Promote Main to Prod** [`.github/workflows/promote_main_to_prod.yml:1-26`()] — Automates the synchronization of the `main` branch to the `prod` branch.
4.  **Dependabot** [`.github/workflows/dependabot.yml:1-53`()] — Manages automated dependency updates for `uv`, Docker, and GitHub Actions.

---

## Agent CI Workflow

The primary CI workflow, named `Agent CI`, ensures code quality by running parallel jobs on every push to `main`, pull request, or manual trigger [`.github/workflows/ci.yml:6-10`()].

### Workflow Metadata

| Property | Value | Description |
| :--- | :--- | :--- |
| **Permissions** | `contents: read` | Minimal permissions for security [`.github/workflows/ci.yml:4-4`()] |
| **Concurrency Group** | `${{ github.workflow }}-${{ github.ref }}` | Groups runs by workflow and branch/PR [`.github/workflows/ci.yml:13-13`()] |
| **Cancel In-Progress** | `true` | Cancels outdated runs when new commits are pushed [`.github/workflows/ci.yml:14-14`()] |

### CI Execution Flow

All jobs run in parallel on `ubuntu-latest` runners and use `uv` for dependency management [`.github/workflows/ci.yml:19,30,41`()].

```mermaid
graph TB
    subgraph "GitHub Actions Runner"
        Trigger["Workflow Trigger<br/>(push/PR/manual)"]
        
        Trigger --> LintJob["job: lint<br/>(Agent lint)"]
        Trigger --> FormatJob["job: format<br/>(Agent format check)"]
        Trigger --> TestJob["job: unit-tests<br/>(Agent unit tests)"]
        
        subgraph "Job Setup (Common)"
            Checkout["actions/checkout@v6"]
            SetupUV["astral-sh/setup-uv@v8.1.0"]
            Install["uv sync --locked --extra dev"]
        end

        LintJob --> Checkout
        FormatJob --> Checkout
        TestJob --> Checkout

        Install --> RunLint["make lint"]
        Install --> RunFormat["make format-check"]
        Install --> RunTest["make test"]

        RunLint --> RuffLint["ruff check"]
        RunFormat --> RuffFormat["ruff format --check"]
        RunTest --> Pytest["pytest"]
    end
```

**Sources:** [`.github/workflows/ci.yml:1-49`()]

---

## Pull Request Management

Open SWE enforces strict standards for pull requests to maintain a clean git history and high code quality.

### PR Title Linting
The `PR Title Lint` workflow uses `amannn/action-semantic-pull-request` [`.github/workflows/pr_lint.yml:15-15`()] to validate that PR titles follow the Conventional Commits specification.

*   **Allowed Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`, `release` [`.github/workflows/pr_lint.yml:20-31`()].
*   **Allowed Scopes:** `shared`, `cli`, `web`, `open-swe`, `docs`, `deps` [`.github/workflows/pr_lint.yml:33-38`()].

### Automated Dependency Updates
Dependabot is configured to check for updates monthly [`.github/workflows/dependabot.yml:5,22,40`()]. It groups updates into `minor-and-patch` and `major` categories for three ecosystems:
*   **uv:** Python package management [`.github/workflows/dependabot.yml:3-18`()].
*   **docker:** Container images [`.github/workflows/dependabot.yml:20-35`()].
*   **github-actions:** Workflow actions [`.github/workflows/dependabot.yml:37-52`()].

**Sources:** [`.github/workflows/pr_lint.yml:1-42`()], [`.github/workflows/dependabot.yml:1-53`()]

---

## Deployment and Promotion

Open SWE follows a branch-based deployment strategy where the `prod` branch represents the stable production environment.

### Branch Promotion Logic
The `Promote main to prod` workflow automates the movement of code from the development branch (`main`) to the production branch (`prod`).

*   **Schedule:** Runs daily at 08:00 UTC [`.github/workflows/promote_main_to_prod.yml:8-8`()].
*   **Manual Trigger:** Can be invoked via `workflow_dispatch` [`.github/workflows/promote_main_to_prod.yml:9-9`()].
*   **Implementation:** Performs a force-push of the `main` HEAD to `refs/heads/prod` [`.github/workflows/promote_main_to_prod.yml:25-25`()].

```mermaid
sequenceDiagram
    participant GHA as ".github/workflows/promote_main_to_prod.yml"
    participant Git as "Git Repository"
    participant Prod as "Branch: prod"

    Note over GHA: Triggered via Cron or Manual
    GHA->>Git: actions/checkout@v6 (ref: main)
    GHA->>Git: git push --force origin HEAD:refs/heads/prod
    Git->>Prod: Update to match main
```

**Sources:** [`.github/workflows/promote_main_to_prod.yml:1-26`()]

---

## Tooling and Environment

### UV Dependency Synchronization
The CI jobs use the following synchronization logic to ensure environment parity [`.github/workflows/ci.yml:24,35,46`()]:
*   `--locked`: Strictly adheres to the `uv.lock` file.
*   `--extra dev`: Installs tools required for CI like Ruff and Pytest.

### Permissions Summary
| Workflow | Permission | Purpose |
| :--- | :--- | :--- |
| **Agent CI** | `contents: read` | Read code for testing [`.github/workflows/ci.yml:4-4`()] |
| **PR Title Lint** | `pull-requests: read` | Validate PR metadata [`.github/workflows/pr_lint.yml:4-4`()] |
| **Promote Main to Prod** | `contents: write` | Force-push to the `prod` branch [`.github/workflows/promote_main_to_prod.yml:4-4`()] |

**Sources:** [`.github/workflows/ci.yml:1-49`()], [`.github/workflows/promote_main_to_prod.yml:1-26`()]

---

# Page: Monorepo Structure

# Monorepo Structure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Makefile](Makefile)
- [agent/integrations/langsmith.py](agent/integrations/langsmith.py)
- [agent/middleware/exclude_tools.py](agent/middleware/exclude_tools.py)
- [evals/reviewer/judge.py](evals/reviewer/judge.py)
- [langgraph.json](langgraph.json)
- [pyproject.toml](pyproject.toml)
- [ui/package.json](ui/package.json)
- [ui/src/components/AppSidebar.tsx](ui/src/components/AppSidebar.tsx)
- [ui/yarn.lock](ui/yarn.lock)
- [uv.lock](uv.lock)

</details>



This document describes the physical organization of the Open SWE codebase. While the project includes a React-based dashboard and a Python-based agent core, it utilizes a unified structure to manage dependencies, build processes, and cross-language integration.

## Overview

Open SWE is organized as a monorepo that bridges a Python backend (the Agent Core) with a TypeScript/React frontend (the Dashboard). The repository uses `uv` for Python package management and `yarn` for the frontend dashboard.

**Directory Structure:**

```mermaid
graph TB
    Root["open-swe/"]
    RootPkg["pyproject.toml<br/>Project metadata"]
    UvLock["uv.lock<br/>Python lockfile"]
    
    AgentDir["agent/"]
    AppsDir["apps/"]
    UIDir["ui/"]
    EvalsDir["evals/"]
    
    AgentCore["agent/<br/>Python package"]
    Webapp["agent/webapp.py<br/>FastAPI server"]
    
    Dashboard["ui/<br/>React dashboard"]
    UIPkg["ui/package.json"]
    
    ReviewerEval["evals/reviewer/<br/>LangSmith benchmarks"]
    
    Root --> RootPkg
    Root --> UvLock
    Root --> AgentDir
    Root --> UIDir
    Root --> EvalsDir
    
    AgentDir --> AgentCore
    AgentDir --> Webapp
    
    UIDir --> Dashboard
    Dashboard --> UIPkg
    
    EvalsDir --> ReviewerEval
    
    Webapp -.->|"serves API for"| Dashboard
    ReviewerEval -.->|"benchmarks"| AgentCore
```

Sources: [pyproject.toml:1-28](), [uv.lock:1-7](), [langgraph.json:1-14](), [ui/package.json:1-63]()

## Project Configuration

The monorepo uses `pyproject.toml` as the primary manifest for the Python environment and `langgraph.json` to define the agentic graphs and server entry points.

**Core Manifests:**

| File | Purpose |
|------|---------|
| `pyproject.toml` | Defines Python dependencies (`deepagents`, `langgraph`, `fastapi`), build system (`hatchling`), and linting rules (`ruff`). |
| `uv.lock` | Deterministic lockfile for the entire Python environment. |
| `langgraph.json` | Maps graph identifiers to factory functions and defines the FastAPI webapp location. |
| `ui/package.json` | Manages React dependencies and build scripts for the dashboard. |

The `langgraph.json` file [langgraph.json:4-12]() is the central registry for the system's execution surfaces:
- **Graphs**: `agent`, `reviewer`, and `review_style_analyzer`.
- **HTTP**: Points to `agent.webapp:app` for the dashboard backend.

Sources: [pyproject.toml:1-40](), [langgraph.json:1-14]()

## Python Package Organization (`agent/`)

The `agent/` directory contains the core logic of the system, organized into functional sub-modules.

### Core Components

| Module | Role |
|--------|------|
| `agent.server` | Contains `get_agent`, the primary entry point for the coding agent. |
| `agent.reviewer` | Implements the automated PR reviewer logic and findings management. |
| `agent.integrations` | Sandbox providers (e.g., `langsmith.py`) and external service connectors. |
| `agent.middleware` | Logic that wraps the agent loop, such as `ExcludeToolsMiddleware`. |
| `agent.webapp` | The FastAPI server providing the dashboard API and webhook endpoints. |

### Sandbox Integration
The `agent/integrations/langsmith.py` file manages the lifecycle of remote execution environments. It uses `create_langsmith_sandbox` [agent/integrations/langsmith.py:126-170]() to provision containers and `_configure_github_proxy` [agent/integrations/langsmith.py:98-124]() to inject authentication without persisting tokens to the sandbox disk.

Sources: [langgraph.json:4-12](), [agent/integrations/langsmith.py:126-170](), [agent/middleware/exclude_tools.py:33-43]()

## Dashboard and UI (`ui/`)

The `ui/` directory contains a modern React application built with Vite and TanStack Router.

| Property | Value |
|----------|-------|
| Framework | React 19 + Vite |
| Routing | TanStack Router |
| Styling | Tailwind CSS 4 |
| Icons | Phosphor Icons / Lucide / React Icons |

**Key UI Entities:**
- **`AppSidebar`**: The primary navigation component [ui/src/components/AppSidebar.tsx:30-36]() defining routes for "Cloud Agents", "Open SWE Review", and "Admin".
- **`lib/api.ts`**: Handles communication with the FastAPI backend defined in `agent.webapp`.

Sources: [ui/package.json:14-45](), [ui/src/components/AppSidebar.tsx:30-49]()

## Build and Development Orchestration

The project uses a `Makefile` to provide a unified interface for development tasks across Python and Node.js environments.

**Build Dependency and Task Flow:**

```mermaid
graph LR
    Make["Makefile"]
    
    subgraph "Python Tasks"
        Uv["uv run"]
        Ruff["ruff (lint/format)"]
        Pytest["pytest"]
    end
    
    subgraph "Execution"
        DevServer["langgraph dev"]
        Webapp["uvicorn agent.webapp:app"]
    end
    
    Make -->|"make dev"| DevServer
    Make -->|"make run"| Webapp
    Make -->|"make lint"| Ruff
    Make -->|"make test"| Pytest
    Uv --> DevServer
    Uv --> Webapp
```

**Common Commands:**
- `make dev`: Starts the LangGraph development server [Makefile:10-11]().
- `make run`: Starts the FastAPI webhook and dashboard API server [Makefile:13-14]().
- `make format`: Runs `ruff` to standardize Python code [Makefile:49-51]().

Sources: [Makefile:1-70]()

## Evaluation Infrastructure (`evals/`)

The `evals/` directory houses benchmarking logic to ensure agent quality. The `evals/reviewer/judge.py` file implements a sophisticated LLM-based evaluator.

- **`judge_match`**: Computes precision, recall, and F1 scores by comparing agent-generated PR comments against "golden" reference comments [evals/reviewer/judge.py:108-156]().
- **`aggregate_pr`**: Provides micro and macro averages across an entire experiment run [evals/reviewer/judge.py:163-199]().

This infrastructure allows developers to quantify the impact of prompt or tool changes on the agent's performance.

Sources: [evals/reviewer/judge.py:108-199]()

---

# Page: Operational Scripts

# Operational Scripts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/utils/authorship.py](agent/utils/authorship.py)
- [scripts/__init__.py](scripts/__init__.py)
- [scripts/check_pr_merge_status.py](scripts/check_pr_merge_status.py)
- [scripts/create_sandbox_snapshot.py](scripts/create_sandbox_snapshot.py)
- [scripts/list_snapshots.py](scripts/list_snapshots.py)

</details>



The `scripts/` directory contains utility scripts designed for PR analytics, bulk status monitoring, and sandbox environment management. These tools interact with the LangGraph API to extract data from agent execution threads, the GitHub API to verify the lifecycle of pull requests, and the LangSmith Sandbox API to manage execution environments.

## PR URL Extraction

The `export_pr_urls.py` script facilitates the extraction of unique GitHub PR URLs generated by Open SWE agents across multiple LangGraph threads.

### Implementation Details
The script performs a paginated search of threads via the `LangGraphClient` [scripts/export_pr_urls.py:206-208](). It targets threads created within a specific lookback window (defaulting to 9 days) [scripts/export_pr_urls.py:24-25]().

**Data Flow:**
1.  **Thread Discovery**: Searches for threads sorted by `created_at` descending [scripts/export_pr_urls.py:166-170]().
2.  **State Retrieval**: For each relevant thread, it fetches the thread state [scripts/export_pr_urls.py:182-187]().
3.  **Message Parsing**: It inspects the `messages` list within the state values. It specifically looks for messages where `type == "tool"` and `name == "commit_and_open_pr"` [scripts/export_pr_urls.py:47-50]().
4.  **URL Extraction**: It parses the JSON content of the tool output to retrieve the `pr_url` field [scripts/export_pr_urls.py:67-69]().

### Key Functions
| Function | Description |
| :--- | :--- |
| `export_pr_urls` | Main entry point that manages concurrency and pagination for thread scanning [scripts/export_pr_urls.py:190-204](). |
| `extract_pr_urls_from_messages` | Filters and parses tool messages to find successful PR creations [scripts/export_pr_urls.py:43-71](). |
| `_fetch_thread_page` | Low-level wrapper for `client.threads.search` [scripts/export_pr_urls.py:160-172](). |

**Sources:**
- [scripts/export_pr_urls.py:1-204]()
- [agent/tools/commit_and_open_pr.py:36-119]()

---

## Merge Status Analytics

The `check_pr_merge_status.py` script takes the output from the extraction script and performs bulk checking of PR states via the GitHub API.

### PR Classification Logic
The script classifies PRs into three primary buckets based on the GitHub API response [scripts/check_pr_merge_status.py:80-90]():
*   **merged**: PRs where the `merged` flag is true or `merged_at` is populated [scripts/check_pr_merge_status.py:81-82]().
*   **open_or_draft**: PRs with a state of `"open"` [scripts/check_pr_merge_status.py:85-86]().
*   **closed**: PRs with a state of `"closed"` that were never merged [scripts/check_pr_merge_status.py:87-88]().

### Execution Model
The script uses `httpx.AsyncClient` for high-concurrency network I/O [scripts/check_pr_merge_status.py:129-134](). It utilizes an `asyncio.Semaphore` to control the number of concurrent requests to the GitHub API [scripts/check_pr_merge_status.py:128-131](). It requires a `GITHUB_PAT` (Personal Access Token) for authenticated requests to avoid rate-limiting [scripts/check_pr_merge_status.py:165-167]().

**Sources:**
- [scripts/check_pr_merge_status.py:1-186]()

---

## Sandbox Snapshot Management

The repository includes scripts to manage LangSmith sandbox snapshots, which provide the execution environment for Open SWE agents.

### Snapshot Creation
The `create_sandbox_snapshot.py` script allows developers to create new LangSmith sandbox snapshots with specific Docker images and filesystem capacities [scripts/create_sandbox_snapshot.py:12-47]().

*   **Default Image**: `johanneslangchain/open-swe-sandbox:gh-cli-amd64` [scripts/create_sandbox_snapshot.py:8]().
*   **Default Capacity**: 32 GiB [scripts/create_sandbox_snapshot.py:9]().
*   **Implementation**: Uses the `SandboxClient` from `langsmith.sandbox` to call `create_snapshot` [scripts/create_sandbox_snapshot.py:36-41]().

### Snapshot Listing
The `list_snapshots.py` script provides a simple utility to view all existing snapshots, their IDs, and their current status [scripts/list_snapshots.py:1-6]().

**Sources:**
- [scripts/create_sandbox_snapshot.py:1-47]()
- [scripts/list_snapshots.py:1-6]()

---

## System Integration Diagrams

### PR Lifecycle Data Flow
This diagram illustrates how operational scripts bridge the gap between LangGraph's internal thread state and external GitHub entities.

Title: PR Analytics Data Flow
```mermaid
graph TD
    subgraph "LangGraph Space"
        T["Thread (thread_id)"]
        S["State (values)"]
        M["Message (commit_and_open_pr)"]
    end

    subgraph "Natural Language Space"
        U["User PR URL List"]
        ST["Success Metrics (Merged/Open)"]
    end

    subgraph "Code Entity Space"
        EX["export_pr_urls.py"]
        CK["check_pr_merge_status.py"]
        GH["GitHub API (/pulls/{number})"]
    end

    T -->|contains| S
    S -->|contains| M
    EX -->|extract_pr_url| M
    EX -->|writes| U
    U -->|input| CK
    CK -->|requests| GH
    GH -->|responds state| CK
    CK -->|summarizes| ST
```
**Sources:**
- [scripts/export_pr_urls.py:43-71]()
- [scripts/check_pr_merge_status.py:93-119]()

### Sandbox Environment Management
This diagram shows how management scripts interact with the LangSmith Sandbox infrastructure.

Title: Sandbox Management Flow
```mermaid
graph LR
    subgraph "Local Development"
        CSS["create_sandbox_snapshot.py"]
        LSS["list_snapshots.py"]
    end

    subgraph "LangSmith Cloud"
        SC["SandboxClient"]
        SNAP["Snapshots"]
    end

    subgraph "Code Entity Space"
        IMG["Docker Image (gh-cli-amd64)"]
        ENV[".env (DEFAULT_SANDBOX_SNAPSHOT_ID)"]
    end

    CSS -->|uses| SC
    LSS -->|uses| SC
    SC -->|manages| SNAP
    CSS -->|configures| IMG
    CSS -->|outputs ID| ENV
```
**Sources:**
- [scripts/create_sandbox_snapshot.py:36-43]()
- [scripts/list_snapshots.py:3-5]()

---

## Configuration and Usage

### Environment Variables
Scripts utilize `.env` files if available via `load_dotenv` [scripts/export_pr_urls.py:27-32]().

| Variable | Required By | Description |
| :--- | :--- | :--- |
| `LANGGRAPH_URL` | `export_pr_urls.py` | URL of the LangGraph server (default: localhost:2024) [scripts/export_pr_urls.py:38-40](). |
| `LANGGRAPH_API_KEY` | `export_pr_urls.py` | Authentication for LangGraph Cloud [scripts/export_pr_urls.py:205](). |
| `GITHUB_PAT` | `check_pr_merge_status.py` | GitHub Personal Access Token for API requests [scripts/check_pr_merge_status.py:165-167](). |
| `LANGSMITH_API_KEY` | `create_sandbox_snapshot.py` | API key for LangSmith sandbox operations [scripts/create_sandbox_snapshot.py:27-30](). |

### CLI Examples
```bash
# 1. Export URLs from the last 7 days
python scripts/export_pr_urls.py --days-back 7 --output pr_urls.json

# 2. Check merge status of exported URLs
python scripts/check_pr_merge_status.py --input pr_urls.json --concurrency 10

# 3. Create a new sandbox snapshot
python scripts/create_sandbox_snapshot.py --name "custom-swe-env" --image "my-custom-image:latest"
```

**Sources:**
- [scripts/export_pr_urls.py:190-204]()
- [scripts/check_pr_merge_status.py:144-157]()
- [scripts/create_sandbox_snapshot.py:13-31]()

---

# Page: Glossary

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CUSTOMIZATION.md](CUSTOMIZATION.md)
- [INSTALLATION.md](INSTALLATION.md)
- [README.md](README.md)
- [agent/integrations/langsmith.py](agent/integrations/langsmith.py)
- [agent/reviewer.py](agent/reviewer.py)
- [agent/reviewer_findings.py](agent/reviewer_findings.py)
- [agent/server.py](agent/server.py)
- [agent/tools/__init__.py](agent/tools/__init__.py)
- [agent/tools/add_finding.py](agent/tools/add_finding.py)
- [agent/tools/update_finding.py](agent/tools/update_finding.py)
- [agent/utils/slack.py](agent/utils/slack.py)
- [pyproject.toml](pyproject.toml)
- [tests/test_reviewer.py](tests/test_reviewer.py)
- [tests/test_reviewer_findings.py](tests/test_reviewer_findings.py)
- [tests/test_reviewer_tools.py](tests/test_reviewer_tools.py)
- [uv.lock](uv.lock)

</details>



This page provides definitions for codebase-specific terms, jargon, and domain concepts used throughout the Open SWE framework, including detailed technical implementation details for onboarding engineers.

## Core Concepts

| Term | Definition | Code Pointer |
|:---|:---|:---|
| **Deep Agent** | The foundational agentic framework Open SWE composes upon, providing the core execution loop and base tools. | [README.md:38-40](), [agent/server.py:29-29]() |
| **Sandbox** | An isolated, remote Linux environment (usually a container) where the agent clones code and executes shell commands. | [README.md:52-54](), [agent/utils/sandbox.py:1-20]() |
| **Thread ID** | A deterministic identifier used to route messages to the correct persistent sandbox and conversation state. | [README.md:105-106](), [agent/server.py:164-165]() |
| **AGENTS.md** | A repository-level configuration file used to inject custom instructions, coding standards, and context into the agent. | [README.md:82-83](), [agent/utils/agents_md.py:1-15]() |
| **Middleware** | Logic that runs before or after the agent's main loop to handle tasks like error recovery or message queuing. | [README.md:92-97](), [agent/middleware/__init__.py:1-20]() |
| **Subagent** | A child agent spawned via the `task` tool to handle a specific sub-problem in a separate sandbox. | [README.md:90-91](), [agent/server.py:55-69]() |
| **Reviewer Agent** | A specialized agent configuration focused solely on PR analysis and finding generation, using a restricted toolset. | [agent/reviewer.py:1-15]() |

Sources: [README.md:38-106](), [agent/server.py:29-69](), [agent/reviewer.py:1-15]()

---

## Technical Terms & Implementation

### 1. Sandbox Backend Protocol
The `SandboxBackendProtocol` is a Python interface (inherited from `deepagents`) that all sandbox providers must implement. It ensures the agent can interact with any environment (Modal, LangSmith, Daytona, etc.) using a unified set of methods.

**Key Methods:**
* `execute(command, timeout)`: Runs a shell command and returns an `ExecuteResponse`. [agent/integrations/langsmith.py:113-122]()
* `read(path)` / `write(path, content)`: Basic file I/O operations.
* `ls(path)` / `glob(pattern)`: Directory traversal and file discovery.

Sources: [agent/server.py:31-31](), [agent/integrations/langsmith.py:113-122](), [CUSTOMIZATION.md:101-106]()

### 2. GitHub Proxy Auth
A security feature specifically for **LangSmith** sandboxes. Instead of writing GitHub tokens to the sandbox disk (where they could be leaked), the system configures a network-level proxy. When the agent runs `git clone` or `gh api`, the LangSmith proxy intercepts the request and injects the `Authorization` header.

**Diagram: Natural Language Space to Code Entity Space (Auth Flow)**

```mermaid
graph TD
    subgraph "Natural Language: 'Authenticate Git'"
        A["User mentions @openswe in Slack"]
    end

    subgraph "Code Entity Space: Auth Resolution"
        B["get_github_app_installation_token()"]
        C["_configure_github_proxy()"]
        D["_github_proxy_rules()"]
        E["httpx.patch(langsmith_endpoint)"]
    end

    A --> B
    B -- "Installation Token" --> C
    C --> D
    D -- "Basic/Bearer Rules" --> E
    E -- "Configures" --> F["LangSmith Sandbox Network"]
```

Sources: [agent/integrations/langsmith.py:70-95](), [agent/server.py:131-137](), [agent/server.py:149-159]()

### 3. Review Findings
In the context of the `Reviewer Agent`, a **Finding** is a structured record of a code issue. Findings are persisted in thread metadata to survive sandbox eviction and allow for "watch-mode" reconciliation (checking if a previous finding was fixed in a new commit).

**Implementation Details:**
* `add_finding()`: Validates that the line range is within the PR diff using `is_range_in_diff`. [agent/tools/add_finding.py:24-86]()
* `Finding` Data Class: Includes `severity`, `confidence`, `file`, `start_line`, `end_line`, and `suggestion`. [agent/tools/add_finding.py:126-138]()

Sources: [agent/reviewer.py:90-96](), [agent/tools/add_finding.py:24-150]()

---

## Agent Lifecycle Components

### Middleware Hooks
Open SWE utilizes a middleware system to wrap the agent execution loop, allowing for deterministic checks and safety nets.

| Component | Function | File Pointer |
|:---|:---|:---|
| `ToolErrorMiddleware` | Catches exceptions from tool calls and returns them as observations to the LLM. | [agent/server.py:49-49]() |
| `check_message_queue_before_model` | Injects follow-up user messages (e.g., Slack replies) into the conversation before the next LLM turn. | [agent/server.py:50-50]() |
| `SanitizeToolInputsMiddleware` | Ensures tool arguments conform to expected types before execution. | [agent/server.py:47-47]() |
| `SlackAssistantStatusMiddleware` | Updates the Slack "is thinking..." status indicator during long-running tasks. | [agent/server.py:48-48]() |

Sources: [agent/server.py:44-53](), [README.md:91-96]()

### Toolset
The framework provides a curated toolset for engineering tasks.

**Diagram: Natural Language Space to Code Entity Space (Tool Execution)**

```mermaid
graph LR
    subgraph "Natural Language: 'Review this PR'"
        User["'@openswe review https://github.com/.../pull/1'"]
    end

    subgraph "Code Entity Space: Reviewer Tools"
        Reviewer["get_reviewer_agent()"]
        AF["add_finding()"]
        UF["update_finding()"]
        PR["publish_review()"]
    end

    User --> Reviewer
    Reviewer --> AF
    Reviewer --> UF
    Reviewer --> PR
    PR -- "GitHub API" --> GH["PR Review Comment"]
```

Sources: [agent/reviewer.py:53-61](), [agent/tools/__init__.py:1-37](), [agent/tools/add_finding.py:1-21]()

---

## Sandbox Providers
The system supports multiple backends configured via the `SANDBOX_TYPE` environment variable.

* **LangSmith:** Default cloud sandbox with integrated proxy auth. [agent/integrations/langsmith.py:1-30]()
* **Daytona:** Uses the Daytona API for dev environments. [CUSTOMIZATION.md:61-61]()
* **Runloop:** Uses Runloop's environment API. [CUSTOMIZATION.md:62-62]()
* **Modal:** Uses Modal's serverless infrastructure. [CUSTOMIZATION.md:63-63]()
* **Local:** Runs directly on the host machine. **Warning: No isolation.** [CUSTOMIZATION.md:64-66]()

Sources: [CUSTOMIZATION.md:58-64](), [agent/server.py:99-100]()

---

## Abbreviations & Jargon

* **PR:** Pull Request (GitHub).
* **LLM:** Large Language Model (e.g., GPT-4o, Claude 3.5 Sonnet).
* **Webhook:** HTTP callbacks used by Slack, Linear, or GitHub to notify Open SWE of events.
* **OAuth Provider ID:** A short string used to link a GitHub App's credentials within LangSmith for per-user authentication. [INSTALLATION.md:43-51]()
* **Installation ID:** The unique ID assigned by GitHub when an App is installed on a specific organization or account. [INSTALLATION.md:91-99]()
* **Reasoning Effort:** A parameter for OpenAI models (like o1/o3) that controls how much "thinking" time the model uses. [agent/server.py:41-42]()

Sources: [INSTALLATION.md:43-99](), [agent/server.py:41-42](), [README.md:100-106]()