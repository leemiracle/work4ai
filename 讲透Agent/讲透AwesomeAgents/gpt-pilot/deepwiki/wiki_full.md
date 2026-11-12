# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [pyproject.toml](pyproject.toml)
- [requirements.txt](requirements.txt)

</details>



GPT Pilot is an AI-powered system that automates software development by generating and implementing code for full applications while collaborating with human developers. Unlike code completion tools or simple helpers for PR messages, GPT Pilot aims to be a comprehensive AI developer companion that can write complete features, debug code, and engage in meaningful development conversations.

## Purpose and Scope

This document provides a high-level introduction to the GPT Pilot system, its architecture, and its core functionality. For detailed information on specific components, please refer to the corresponding wiki pages linked throughout this document.

## Core Philosophy

GPT Pilot operates on the principle that AI can handle approximately 95% of application code, while human oversight remains essential for the remaining 5%. As stated in the project README:

> "The main idea is that AI can write most of the code for an app (maybe 95%), but for the rest, 5%, a developer is and will be needed until we get full AGI."

This human-in-the-loop approach enables GPT Pilot to scale to complex applications while maintaining high code quality through developer feedback and collaboration.

## System Architecture

### High-Level Architecture Diagram

```mermaid
graph TD
    User(["Human Developer"]) --> UI["UI Layer"]
    UI --> Orchestrator["Orchestrator"]
    
    subgraph "Agent System"
        Orchestrator --> TechLead["Tech Lead Agent"]
        Orchestrator --> Developer["Developer Agent"]
        Orchestrator --> BugHunter["Bug Hunter Agent"]
        Orchestrator --> Troubleshooter["Troubleshooter Agent"]
        Orchestrator --> Frontend["Frontend Agent"]
        Orchestrator --> CodeMonkey["Code Monkey Agent"]
        Orchestrator --> SpecWriter["Spec Writer Agent"]
        Orchestrator --> Architect["Architect Agent"]
    end
    
    subgraph "State Management"
        Orchestrator --> StateManager["State Manager"]
        StateManager --> Database[("Database")]
        Database --> SQLite[("SQLite")]
        Database --> PostgreSQL[("PostgreSQL")]
        StateManager --> FileSystem["File System"]
    end
    
    subgraph "LLM Integration"
        TechLead --> LLMClient["LLM Client"]
        Developer --> LLMClient
        BugHunter --> LLMClient
        Troubleshooter --> LLMClient
        Frontend --> LLMClient
        CodeMonkey --> LLMClient
        SpecWriter --> LLMClient
        Architect --> LLMClient
        
        LLMClient --> OpenAI["OpenAI Provider"]
        LLMClient --> Anthropic["Anthropic Provider"]
        LLMClient --> Groq["Groq Provider"]
    end
    
    StateManager --> Templates["Project Templates"]
    StateManager --> WorkspaceDir["workspace/ directory"]
```

Sources: [README.md:76-191]()

The system consists of several core components:

1. **UI Layer**: Provides interfaces for developer interaction, including a VS Code extension, console interface, and virtual UI for automated testing.

2. **Orchestrator**: Coordinates the activities of different agents and manages project state.

3. **Agent System**: A collection of specialized AI agents that handle different aspects of the development process.

4. **State Management**: Maintains project state through databases (SQLite or PostgreSQL) and the file system.

5. **LLM Integration**: Connects agents to various LLM providers (OpenAI, Anthropic, Groq).

6. **Project Templates**: Provides starting points for different project types.

For more detailed information on the system architecture, see [System Architecture](#2).

## Development Workflow

### Agent Workflow Diagram

```mermaid
flowchart LR
    User(["Human Developer"]) -- "App Requirements" --> SW["Spec Writer Agent"]
    SW -- "Refined Requirements" --> A["Architect Agent"]
    A -- "Tech Stack Selection" --> TL["Tech Lead Agent"]
    
    TL -- "Tasks" --> D["Developer Agent"]
    D -- "Implementation Plan" --> CM["Code Monkey Agent"]
    CM -- "Code Implementation" --> T["Troubleshooter Agent"]
    
    T -- "Testing Instructions" --> User
    User -- "Bug Report" --> BH["Bug Hunter Agent"]
    BH -- "Bug Analysis" --> CM
    
    subgraph "UI Development"
        TL -- "Frontend Tasks" --> FE["Frontend Agent"]
        FE -- "UI Code" --> CM
    end
```

Sources: [README.md:178-191]()

The development process follows these steps:

1. The human developer provides initial application requirements
2. The **Spec Writer Agent** asks clarifying questions to refine requirements
3. The **Architect Agent** determines the technology stack
4. The **Tech Lead Agent** breaks down the project into manageable tasks
5. The **Developer Agent** creates detailed implementation plans
6. The **Code Monkey Agent** writes actual code based on these plans
7. The **Troubleshooter Agent** helps identify and fix issues
8. The **Bug Hunter Agent** analyzes bugs reported by the developer
9. The **Frontend Agent** handles UI-specific implementation

Throughout this process, the human developer provides feedback, reviews code, and helps overcome obstacles when needed.

## Agent Roles and Responsibilities

GPT Pilot employs a team of specialized AI agents that mirror roles in a real development team:

| Agent | Role |
|-------|------|
| Spec Writer | Asks clarifying questions to understand requirements better |
| Architect | Determines technologies to be used and ensures they're installed |
| Tech Lead | Breaks down projects into development tasks |
| Developer | Creates implementation plans for each task in human-readable form |
| Code Monkey | Implements code changes based on the Developer's description |
| Reviewer | Reviews task implementation and provides feedback |
| Troubleshooter | Helps identify issues and suggests solutions |
| Bug Hunter | Analyzes and resolves bugs reported by users |
| Frontend | Handles UI implementation |
| Technical Writer | Creates documentation for the project |

Sources: [README.md:178-191]()

For more detailed information on specific agents, see [Core Agents](#3).

## Key Capabilities and Differentiators

GPT Pilot distinguishes itself from similar tools like Smol Developer and GPT Engineer in several key ways:

1. **Step-by-Step Development**: Rather than generating an entire codebase at once, GPT Pilot codes incrementally, making debugging easier.

2. **Scalability**: Uses intelligent code filtering to present only relevant portions to the LLM, allowing it to handle larger projects without context limitations.

3. **Human Collaboration**: Designed to work with developers rather than replace them, creating a collaborative development process.

4. **Multi-Agent Architecture**: Utilizes specialized agents that work together, mimicking a development team structure.

5. **Continuous Development**: Supports adding new features to existing applications through natural language instructions.

Sources: [README.md:194-199]()

## Using GPT Pilot

GPT Pilot can be used either through its VS Code extension or via the command-line interface. The system writes all generated code to a workspace directory inside the project folder.

Basic installation steps include:

1. Clone the repository
2. Install dependencies
3. Configure LLM provider API keys
4. Run GPT Pilot

For detailed setup instructions, see [Configuration and LLM Integration](#5).

For information on commands and usage options, see [Development Workflow](#6).

Sources: [README.md:97-120](), [README.md:137-176]()

---

# Page: Getting Started

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [core/config/__init__.py](core/config/__init__.py)
- [core/llm/anthropic_client.py](core/llm/anthropic_client.py)
- [data/database/.gitkeep](data/database/.gitkeep)
- [example-config.json](example-config.json)
- [pyproject.toml](pyproject.toml)
- [requirements.txt](requirements.txt)
- [tests/config/test_config.py](tests/config/test_config.py)
- [tests/config/test_env_importer.py](tests/config/test_env_importer.py)

</details>



This section provides an overview of how to install, configure, and begin using GPT Pilot. It covers the essential steps to get the system running and explains the basic workflow for creating your first AI-generated application.

For detailed installation instructions, see [Installation and Setup](#2.1). For comprehensive configuration options, see [Configuration Guide](#2.2). For complete CLI command reference, see [CLI Usage and Commands](#2.3).

---

## Prerequisites

GPT Pilot requires:
- **Python 3.9 or higher** - The minimum version specified in [pyproject.toml:27]()
- **LLM API access** - At least one of: OpenAI, Anthropic, Groq, or Azure OpenAI
- **Poetry or pip** - For dependency management
- **Git** (optional) - For cloning the repository
- **PostgreSQL** (optional) - SQLite is used by default

**Sources:** [pyproject.toml:27](), [README.md:105]()

---

## System Initialization Flow

Understanding how GPT Pilot starts up helps contextualize the installation and configuration steps. The following diagram shows the initialization sequence from command invocation to ready state.

### Startup Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant main.py
    participant ConfigLoader
    participant Database
    participant StateManager
    participant UIAdapter
    participant Orchestrator

    User->>main.py: python main.py [--args]
    main.py->>main.py: parse CLI arguments
    main.py->>ConfigLoader: load("config.json")
    ConfigLoader->>ConfigLoader: parse JSON, validate schema
    ConfigLoader-->>main.py: Config object
    
    main.py->>Database: initialize_database(db_url)
    Database->>Database: run Alembic migrations
    Database-->>main.py: database ready
    
    main.py->>UIAdapter: create UI (PlainConsoleUI or IPCClientUI)
    UIAdapter-->>main.py: ui instance
    
    main.py->>main.py: async_main(project_args, ui, config)
    main.py->>StateManager: create StateManager
    StateManager->>Database: connect to session
    StateManager-->>main.py: state_manager ready
    
    main.py->>Orchestrator: create Orchestrator(state_manager, ui)
    main.py->>Orchestrator: run(project_args)
    
    alt New Project
        Orchestrator->>User: "What is your app called?"
        User-->>Orchestrator: app name
        Orchestrator->>Orchestrator: create Project, Branch("main")
        Orchestrator->>StateManager: create_project_state(step_index=0)
    else Existing Project
        Orchestrator->>StateManager: load_project(project_id, step)
        StateManager-->>Orchestrator: ProjectState restored
    end
    
    Orchestrator->>Orchestrator: enter agent workflow
    Orchestrator-->>User: Ready for development
```

**Key Components:**

- **`main.py`**: Entry point that orchestrates initialization
- **`ConfigLoader`** ([core/config/__init__.py:444-502]()): Loads and validates `config.json`
- **`Database`**: SQLite (default) or PostgreSQL with async support
- **`UIAdapter`**: Either `PlainConsoleUI` (terminal) or `IPCClientUI` (VSCode extension)
- **`StateManager`**: Transaction-based state persistence system
- **`Orchestrator`**: Central control flow coordinator

**Sources:** [README.md:116-128](), [core/config/__init__.py:444-502]()

---

## Quick Start Overview

The basic workflow to get started with GPT Pilot:

### 1. Clone and Setup

```bash
git clone https://github.com/Pythagora-io/gpt-pilot.git
cd gpt-pilot
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Access

```bash
cp example-config.json config.json
# Edit config.json to add your API keys
```

### 3. Start GPT Pilot

```bash
python main.py
```

The system will prompt you for your application name and description, then begin the development workflow through specialized AI agents.

**Sources:** [README.md:116-128]()

---

## Configuration Loading Process

GPT Pilot uses a structured configuration system that loads settings from `config.json` and applies them across all components. Understanding this process is essential for customization.

### Configuration Flow Diagram

```mermaid
graph TB
    ConfigFile["config.json"]
    
    ConfigFile --> ConfigLoader["ConfigLoader.load()"]
    ConfigLoader --> ParseJSON["Remove comments<br/>Parse JSON"]
    ParseJSON --> Validate["Pydantic validation"]
    
    Validate --> Config["Config object"]
    
    Config --> LLMConfig["LLM Provider Configs<br/>(openai, anthropic, groq)"]
    Config --> AgentConfig["Agent-Specific Configs<br/>(default, CodeMonkey, etc.)"]
    Config --> DBConfig["Database Config<br/>(db.url, debug_sql)"]
    Config --> FSConfig["FileSystem Config<br/>(workspace_root, ignore_paths)"]
    Config --> UIConfig["UI Config<br/>(plain, ipc-client, virtual)"]
    Config --> LogConfig["Logging Config<br/>(level, output, format)"]
    
    LLMConfig --> ProviderConfig["ProviderConfig:<br/>base_url, api_key<br/>timeouts, extras"]
    AgentConfig --> AgentLLMConfig["AgentLLMConfig:<br/>provider, model<br/>temperature"]
    
    Config --> GetLLM["config.llm_for_agent(name)"]
    GetLLM --> MergedLLM["LLMConfig<br/>(merged provider + agent)"]
    
    MergedLLM --> LLMClient["BaseLLMClient<br/>(OpenAI/Anthropic/Groq)"]
    
    style Config fill:#f9f9f9
    style ConfigLoader fill:#e8e8e8
```

**Key Configuration Classes:**

| Class | Purpose | File Location |
|-------|---------|---------------|
| `ConfigLoader` | Loads and parses config.json | [core/config/__init__.py:444-502]() |
| `Config` | Root configuration model | [core/config/__init__.py:325-442]() |
| `ProviderConfig` | LLM provider settings | [core/config/__init__.py:93-120]() |
| `AgentLLMConfig` | Agent-specific LLM settings | [core/config/__init__.py:122-138]() |
| `LLMConfig` | Complete merged LLM config | [core/config/__init__.py:140-188]() |
| `DBConfig` | Database connection settings | [core/config/__init__.py:233-261]() |
| `FileSystemConfig` | Workspace configuration | [core/config/__init__.py:305-323]() |

**Configuration Resolution:**

1. `ConfigLoader` reads `config.json` and strips comments ([core/config/__init__.py:462-471]())
2. Pydantic validates structure and applies defaults
3. For each agent, `config.llm_for_agent(agent_name)` merges provider and agent configs ([core/config/__init__.py:423-434]())
4. If agent-specific config doesn't exist, falls back to `"default"` agent

**Sources:** [core/config/__init__.py:93-442](), [example-config.json:1-89]()

---

## Project Workspace Structure

GPT Pilot organizes all generated code and metadata in a structured workspace. Understanding this layout helps with project management and debugging.

### Workspace Directory Tree

```mermaid
graph TB
    Root["Repository Root"]
    
    Root --> Workspace["workspace/<br/>(configurable via fs.workspace_root)"]
    Root --> Data["data/"]
    Root --> Core["core/"]
    Root --> ConfigJSON["config.json"]
    Root --> MainPy["main.py"]
    
    Workspace --> App1["app_name_1/"]
    Workspace --> App2["app_name_2/"]
    Workspace --> AppN["app_name_N/"]
    
    App1 --> SrcFiles["Source files<br/>(generated code)"]
    App1 --> GitIgnore[".gitignore"]
    App1 --> Dependencies["package.json, requirements.txt<br/>(depending on stack)"]
    
    Data --> Database["database/<br/>pythagora.db"]
    Data --> Logs["pythagora.log<br/>(if log.output configured)"]
    
    Database --> Projects["Project metadata"]
    Database --> Branches["Branch records"]
    Database --> States["ProjectState history"]
    Database --> Files["File references"]
    Database --> FileContent["FileContent<br/>(deduplicated by hash)"]
    
    Core --> ConfigPy["config/__init__.py"]
    Core --> Agents["agents/"]
    Core --> LLM["llm/"]
    Core --> DB["db/"]
    
    style Workspace fill:#e8f4e8
    style Data fill:#f4e8e8
    style Database fill:#e8e8f4
```

**Workspace Defaults:**

- **Root Location**: `workspace/` ([core/config/__init__.py:312]())
- **Ignored Patterns**: `.git`, `node_modules`, `venv`, `*.min.js`, etc. ([core/config/__init__.py:11-34]())
- **Size Threshold**: Files >50KB are ignored by default ([core/config/__init__.py:35]())

**Database Schema:**

The SQLite database (default location: `data/database/pythagora.db`) stores:
- **Projects**: High-level project records with metadata
- **Branches**: Currently only `"main"` branch is supported (multi-branch planned)
- **ProjectStates**: Immutable snapshots at each development step
- **Files**: References to file paths within projects
- **FileContent**: Deduplicated file content (keyed by SHA-256 hash)
- **LLM Requests**: Optional logging of all LLM interactions (if `db.save_llm_requests: true`)

**Sources:** [core/config/__init__.py:11-35, 305-323](), [example-config.json:58-88](), [README.md:129]()

---

## First Project Workflow

When you run `python main.py` without arguments, GPT Pilot initiates a new project workflow. This sequence demonstrates how the system progresses from user input to generated code.

### New Project Initialization Flow

```mermaid
stateDiagram-v2
    [*] --> ParseArgs: python main.py
    
    ParseArgs --> LoadConfig: Load config.json
    LoadConfig --> InitDB: Initialize database
    InitDB --> CreateUI: Create PlainConsoleUI or IPCClientUI
    
    CreateUI --> AskProjectName: Orchestrator asks for app name
    AskProjectName --> CreateProject: Create Project + Branch("main")
    
    CreateProject --> InitState: Create ProjectState(step_index=0)
    InitState --> Wizard: Wizard agent initializes project
    
    Wizard --> SpecWriter: SpecWriter collects requirements
    
    state SpecWriter {
        [*] --> AskDescription: "Describe your app"
        AskDescription --> AskQuestions: Ask clarifying questions
        AskQuestions --> GenerateSpec: Generate specification document
        GenerateSpec --> [*]
    }
    
    SpecWriter --> CommitState1: StateManager commits state (step_index=1)
    CommitState1 --> Architect: Architect selects tech stack
    
    state Architect {
        [*] --> AnalyzeRequirements
        AnalyzeRequirements --> SelectStack: Choose frameworks/languages
        SelectStack --> ApplyTemplate: Apply ProjectTemplate
        ApplyTemplate --> [*]
    }
    
    Architect --> CommitState2: StateManager commits state (step_index=2)
    CommitState2 --> TechLead: TechLead creates epics
    
    state TechLead {
        [*] --> CreateEpics: Break project into epics
        CreateEpics --> BreakdownTasks: Break epics into tasks
        BreakdownTasks --> [*]
    }
    
    TechLead --> CommitState3: StateManager commits state (step_index=3)
    CommitState3 --> Developer: Developer begins implementation
    
    Developer --> CodeLoop: Enter development loop
    
    note right of Wizard
        Agent: Wizard
        Initializes project structure
    end note
    
    note right of SpecWriter
        Agent: SpecWriter
        Defines "what" to build
        Output: Specification object
    end note
    
    note right of Architect
        Agent: Architect
        Defines "how" to build
        Output: Architecture + Template
    end note
    
    note right of TechLead
        Agent: TechLead
        Breaks work into hierarchy
        Output: Epics[] + Tasks[]
    end note
```

**Project State Progression:**

Each successful agent completion increments `step_index` and commits a new `ProjectState`. This creates an immutable history that can be:
- **Replayed**: Using `--project <id> --step <N>` to restore any historical state
- **Audited**: All LLM requests, user inputs, and command executions are logged
- **Branched**: Future feature to create alternative development paths (currently single branch only)

**Agent Sequence:**

1. **Wizard** ([core/agents/wizard.py]()): Initializes project structure, validates environment
2. **SpecWriter** ([core/agents/spec_writer.py]()): Gathers requirements through interactive Q&A
3. **Architect** ([core/agents/architect.py]()): Selects technology stack, applies project template
4. **TechLead** ([core/agents/tech_lead.py]()): Creates epic hierarchy, breaks into implementable tasks
5. **Developer** ([core/agents/developer.py]()): Converts tasks into step-by-step implementation plans
6. **CodeMonkey** ([core/agents/code_monkey.py]()): Generates actual code using `<pythagoracode>` tags

**Sources:** [README.md:186-198]()

---

## CLI Command Patterns

GPT Pilot provides several command-line operations for project management. The basic patterns are:

### Common CLI Operations

| Command | Purpose | Key Files |
|---------|---------|-----------|
| `python main.py` | Start new project | [main.py]() |
| `python main.py --list` | List all projects and branches | [README.md:150-153]() |
| `python main.py --project <id>` | Continue from latest step | [README.md:157-159]() |
| `python main.py --project <id> --step <N>` | Load specific historical state | [README.md:162-167]() |
| `python main.py --delete <id>` | Delete project (permanent) | [README.md:170-175]() |
| `python main.py --help` | Show all available options | [README.md:179-183]() |

### CLI Argument Processing Flow

```mermaid
graph TB
    CLI["Command Line"]
    CLI --> ArgParser["Argument Parser"]
    
    ArgParser --> ProjectID{--project<br/>specified?}
    ArgParser --> Step{--step<br/>specified?}
    ArgParser --> List{--list<br/>flag?}
    ArgParser --> Delete{--delete<br/>specified?}
    
    List -->|Yes| QueryDB["Query database<br/>for all projects"]
    QueryDB --> PrintProjects["Print project list<br/>with branches"]
    PrintProjects --> Exit1["Exit"]
    
    Delete -->|Yes| DeleteProject["Delete project<br/>from database"]
    DeleteProject --> DeleteFiles["Delete workspace files"]
    DeleteFiles --> Exit2["Exit"]
    
    ProjectID -->|Yes| LoadProject["StateManager.load_project()"]
    Step -->|Yes| LoadStep["StateManager.load_project(step=N)"]
    Step -->|No| LoadLatest["Load latest step"]
    
    LoadProject --> RestoreState["Restore ProjectState<br/>from database"]
    LoadStep --> WarnDelete["Warning: deletes progress<br/>after step N"]
    WarnDelete --> RestoreState
    
    RestoreState --> SyncFiles["FileSystemService.sync_files()"]
    SyncFiles --> ContinueWork["Continue development<br/>from restored state"]
    
    ProjectID -->|No| NewProject["Create new project"]
    NewProject --> AskName["Prompt for app name"]
    AskName --> StartWizard["Start Wizard agent"]
    
    style LoadProject fill:#e8f4e8
    style NewProject fill:#f4e8e8
```

**State Loading Behavior:**

When using `--project <id> --step <N>`:
1. All `ProjectState` records after step N are **deleted** from database
2. All file modifications after step N are **reverted**
3. The workspace is restored to exact state at step N
4. Development continues from that point (destructive operation)

**Project Listing Output:**

The `--list` command shows:
- Project ID (for use with `--project`)
- App name
- Branch name (currently always `"main"`)
- Current step index
- Last modified timestamp

**Sources:** [README.md:146-183]()

---

## Environment and Dependencies

GPT Pilot uses modern Python async/await patterns and requires specific package versions for compatibility.

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `python` | ^3.9 | Minimum Python version |
| `openai` | ^1.40.6 | OpenAI API client |
| `anthropic` | ^0.39.0 | Anthropic/Claude API client |
| `groq` | ^0.6.0 | Groq API client |
| `jinja2` | ^3.1.4 | Prompt template engine |
| `tiktoken` | ^0.8.0 | Token counting for OpenAI models |
| `sqlalchemy[asyncio]` | ^2.0.32 | Async ORM for database |
| `aiosqlite` | ^0.20.0 | Async SQLite driver |
| `pydantic` | ^2.8.2 | Configuration validation |
| `alembic` | ^1.13.2 | Database migrations |
| `tenacity` | 9.0.0 | Retry logic for LLM requests |
| `prompt-toolkit` | ^3.0.48 | CLI input handling |

### Optional Dependencies

- **PostgreSQL Support**: `asyncpg` + `psycopg2` (install separately)
- **Development**: `pytest`, `ruff`, `pytest-cov` (in dev group)

**Virtual Environment Isolation:**

GPT Pilot should always be run in a virtual environment to avoid dependency conflicts:

```bash
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

**Sources:** [pyproject.toml:26-42](), [requirements.txt:1-38](), [README.md:136-143]()

---

## Next Steps

Now that you understand the basic concepts and workflow, proceed to:

- **[Installation and Setup](#2.1)**: Detailed installation instructions for various platforms
- **[Configuration Guide](#2.2)**: Comprehensive configuration reference for `config.json`
- **[CLI Usage and Commands](#2.3)**: Complete CLI command reference with examples

For understanding the system architecture after setup, see:

- **[System Architecture](#3)**: Deep dive into core components and design patterns
- **[Agent System](#4)**: How specialized AI agents coordinate to build applications
- **[LLM Integration](#5)**: Configuration and usage of different LLM providers

**Sources:** [README.md:1-221]()

---

# Page: Installation and Setup

# Installation and Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [pyproject.toml](pyproject.toml)
- [requirements.txt](requirements.txt)

</details>



**Purpose and Scope**: This document covers the installation of GPT Pilot, dependency management, virtual environment setup, and initial configuration. For runtime configuration details (LLM providers, model selection, agent settings), see [Configuration Guide](#2.2). For CLI commands and project management, see [CLI Usage and Commands](#2.3).

---

## Prerequisites

GPT Pilot requires Python 3.9 or higher. The system is tested on multiple platforms and Python versions through continuous integration.

| Requirement | Minimum Version | Tested Versions |
|------------|----------------|-----------------|
| Python | 3.9 | 3.9, 3.12 |
| Operating Systems | - | Ubuntu, macOS, Windows |
| Optional: PostgreSQL | Any | Latest |

The CI system validates compatibility across all major platforms [.github/workflows/ci.yml:12-18]().

**Sources**: [.github/workflows/ci.yml:1-36](), [pyproject.toml:27](), [README.md:105]()

---

## Installation Methods

GPT Pilot supports two installation approaches: Poetry (recommended for development) and pip (simpler for end users).

### Installation Flow

```mermaid
flowchart TD
    Start["Start Installation"]
    CheckPython{"Python 3.9+<br/>installed?"}
    InstallPython["Install Python 3.9+"]
    Clone["Clone Repository<br/>git clone https://github.com/Pythagora-io/gpt-pilot.git"]
    ChooseMethod{"Choose<br/>Installation Method"}
    
    Poetry["Poetry Method"]
    Pip["Pip Method"]
    
    InstallPoetry["Install Poetry<br/>pip install poetry"]
    PoetryInstall["poetry install"]
    
    CreateVenv["Create Virtual Environment<br/>python -m venv venv"]
    ActivateVenv["Activate venv<br/>source venv/bin/activate"]
    PipInstall["pip install -r requirements.txt"]
    
    ConfigSetup["Configuration Setup"]
    Verify["Verify Installation<br/>python main.py --help"]
    Complete["Installation Complete"]
    
    Start --> CheckPython
    CheckPython -->|No| InstallPython
    CheckPython -->|Yes| Clone
    InstallPython --> Clone
    Clone --> ChooseMethod
    
    ChooseMethod -->|Development| Poetry
    ChooseMethod -->|Production| Pip
    
    Poetry --> InstallPoetry
    InstallPoetry --> PoetryInstall
    PoetryInstall --> ConfigSetup
    
    Pip --> CreateVenv
    CreateVenv --> ActivateVenv
    ActivateVenv --> PipInstall
    PipInstall --> ConfigSetup
    
    ConfigSetup --> Verify
    Verify --> Complete
```

**Sources**: [README.md:116-128](), [.github/workflows/ci.yml:26-29]()

---

## Using Poetry (Recommended for Development)

Poetry provides dependency resolution, lock files, and development environment isolation. This is the method used in the CI pipeline.

### Installation Steps

1. **Install Poetry**:
   ```bash
   python -m pip install poetry
   ```

2. **Clone the repository**:
   ```bash
   git clone https://github.com/Pythagora-io/gpt-pilot.git
   cd gpt-pilot
   ```

3. **Install dependencies**:
   ```bash
   # Production dependencies only
   poetry install
   
   # Include development dependencies (testing, linting)
   poetry install --with=dev
   ```

4. **Activate the Poetry shell** (optional):
   ```bash
   poetry shell
   ```

The `pyproject.toml` file defines the complete dependency specification [pyproject.toml:26-42](), including:
- Core runtime dependencies (OpenAI, Anthropic, Groq clients)
- Database support (SQLAlchemy, aiosqlite)
- Development tools (pytest, ruff, pre-commit)

**Sources**: [.github/workflows/ci.yml:26-29](), [pyproject.toml:1-65]()

---

## Using pip (Standard Installation)

For users who prefer traditional pip-based installation or don't need development tools.

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Pythagora-io/gpt-pilot.git
   cd gpt-pilot
   ```

2. **Create a virtual environment**:
   ```bash
   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   
   # Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

The `requirements.txt` file contains pinned versions of all dependencies [requirements.txt:1-38](), ensuring reproducible installations.

**Sources**: [README.md:116-121](), [requirements.txt:1-38]()

---

## Core Dependencies

The following table lists critical dependencies and their roles in the system:

| Dependency | Version | Purpose | Referenced In |
|-----------|---------|---------|--------------|
| `pydantic` | ^2.8.2 | Data validation and settings management | StateManager, Agent models |
| `openai` | ^1.40.6 | OpenAI API client | `OpenAIClient` class |
| `anthropic` | ^0.39.0 | Anthropic API client | `AnthropicClient` class |
| `groq` | ^0.6.0 | Groq API client | `GroqClient` class |
| `jinja2` | ^3.1.4 | Prompt template rendering | Agent prompt system |
| `tiktoken` | ^0.8.0 | Token counting for context management | LLM client token limits |
| `sqlalchemy` | ^2.0.32 | Database ORM with async support | StateManager, persistence layer |
| `aiosqlite` | ^0.20.0 | Async SQLite driver | Default database backend |
| `alembic` | ^1.13.2 | Database migrations | Schema versioning |
| `tenacity` | 9.0.0 | Retry logic for API calls | LLM client resilience |
| `prompt-toolkit` | ^3.0.48 | CLI interface components | PlainConsoleUI |

**Sources**: [pyproject.toml:26-42](), [requirements.txt:1-38]()

---

## Dependency Architecture

```mermaid
graph TB
    subgraph "Core Runtime Dependencies"
        Pydantic["pydantic<br/>Data Models"]
        SQLAlchemy["sqlalchemy[asyncio]<br/>Database ORM"]
        Aiosqlite["aiosqlite<br/>SQLite Driver"]
    end
    
    subgraph "LLM Provider Clients"
        OpenAI["openai<br/>OpenAI API"]
        Anthropic["anthropic<br/>Claude API"]
        Groq["groq<br/>Groq API"]
    end
    
    subgraph "Prompt & Token Management"
        Jinja2["jinja2<br/>Template Engine"]
        Tiktoken["tiktoken<br/>Token Counter"]
        Tenacity["tenacity<br/>Retry Logic"]
    end
    
    subgraph "CLI & User Interface"
        PromptToolkit["prompt-toolkit<br/>CLI Components"]
        Httpx["httpx<br/>HTTP Client"]
    end
    
    subgraph "Utilities"
        Jsonref["jsonref<br/>JSON References"]
        Psutil["psutil<br/>Process Management"]
        Dotenv["python-dotenv<br/>Environment Variables"]
        Alembic["alembic<br/>DB Migrations"]
    end
    
    subgraph "Development Only"
        Pytest["pytest<br/>Testing Framework"]
        Ruff["ruff<br/>Linter & Formatter"]
        PytestCov["pytest-cov<br/>Coverage Reports"]
        PreCommit["pre-commit<br/>Git Hooks"]
    end
    
    App["GPT Pilot Application"]
    
    App --> Pydantic
    App --> SQLAlchemy
    App --> OpenAI
    App --> Anthropic
    App --> Groq
    App --> Jinja2
    App --> Tiktoken
    App --> PromptToolkit
    
    SQLAlchemy --> Aiosqlite
    SQLAlchemy --> Alembic
    App --> Tenacity
    App --> Httpx
    App --> Jsonref
    App --> Psutil
    App --> Dotenv
    
    style App fill:#f9f9f9,stroke:#333,stroke-width:3px
```

**Sources**: [pyproject.toml:26-50](), [requirements.txt:1-38]()

---

## Initial Configuration

After installing dependencies, configure the application by creating a `config.json` file.

### Configuration Setup Steps

1. **Copy the example configuration**:
   ```bash
   cp example-config.json config.json
   ```

2. **Edit `config.json`** with your settings (see structure below).

The configuration file controls LLM provider settings, database connections, and file system behavior. Detailed configuration options are documented in [Configuration Guide](#2.2).

### Minimal Configuration Structure

```mermaid
graph TB
    ConfigFile["config.json"]
    
    ConfigFile --> LLM["llm"]
    ConfigFile --> DB["db"]
    ConfigFile --> FS["fs"]
    
    LLM --> DefaultProvider["default_provider<br/>(openai/anthropic/groq)"]
    LLM --> OpenAIConfig["openai.api_key<br/>openai.endpoint"]
    LLM --> AnthropicConfig["anthropic.api_key<br/>anthropic.endpoint"]
    LLM --> GroqConfig["groq.api_key<br/>groq.endpoint"]
    LLM --> AgentModels["agent_overrides<br/>(per-agent model selection)"]
    
    DB --> DBUrl["url<br/>(sqlite:/// or postgresql+asyncpg://)"]
    
    FS --> WorkspaceRoot["workspace_root<br/>(default: ./workspace)"]
    FS --> IgnorePaths["ignore_paths<br/>(file exclusion patterns)"]
    
    style ConfigFile fill:#f9f9f9,stroke:#333,stroke-width:3px
```

**Example minimal configuration**:
```json
{
  "llm": {
    "default_provider": "openai",
    "openai": {
      "api_key": "sk-...",
      "endpoint": null
    }
  },
  "db": {
    "url": "sqlite:///pythagora.db"
  },
  "fs": {
    "workspace_root": "workspace",
    "ignore_paths": ["node_modules", ".git", "__pycache__"]
  }
}
```

**Sources**: [README.md:121-127]()

---

## Database Setup

GPT Pilot uses SQLAlchemy for database abstraction, supporting both SQLite (default) and PostgreSQL.

### SQLite (Default)

SQLite requires no additional setup. The database file is created automatically in the project root when you first run the application.

**Configuration**:
```json
{
  "db": {
    "url": "sqlite:///pythagora.db"
  }
}
```

The `aiosqlite` package provides async SQLite support [requirements.txt:1]().

### PostgreSQL (Optional)

For production deployments or multi-user scenarios, PostgreSQL is recommended.

**Additional dependencies required**:
```bash
pip install asyncpg psycopg2
```

**Configuration**:
```json
{
  "db": {
    "url": "postgresql+asyncpg://user:password@localhost/pythagora"
  }
}
```

The `asyncpg` driver provides high-performance async PostgreSQL access, while `psycopg2` is used by Alembic for schema migrations.

**Sources**: [README.md:137-143](), [pyproject.toml:34-35]()

---

## Database Migration System

```mermaid
graph LR
    Alembic["alembic<br/>Migration Manager"]
    MigrationScripts["core/db/migrations/<br/>Version Scripts"]
    Database["SQLite or PostgreSQL<br/>Database Instance"]
    
    Alembic --> MigrationScripts
    MigrationScripts --> Database
    
    StateManager["StateManager<br/>Application Code"]
    StateManager -.->|"Uses Schema"| Database
```

Alembic manages database schema versioning [pyproject.toml:38](). Migration scripts are located in `core/db/migrations/` and are automatically applied on startup.

**Sources**: [pyproject.toml:38](), [pyproject.toml:58]()

---

## Environment Variables

For sensitive configuration like API keys, use environment variables instead of storing them in `config.json`.

### Supported Environment Variables

| Variable | Purpose | Config Equivalent |
|----------|---------|-------------------|
| `OPENAI_API_KEY` | OpenAI API authentication | `llm.openai.api_key` |
| `ANTHROPIC_API_KEY` | Anthropic API authentication | `llm.anthropic.api_key` |
| `GROQ_API_KEY` | Groq API authentication | `llm.groq.api_key` |
| `DATABASE_URL` | Database connection string | `db.url` |

The system uses `python-dotenv` [requirements.txt:25]() to automatically load variables from a `.env` file in the project root.

**Example `.env` file**:
```
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/pythagora
```

If a configuration value is `null` in `config.json`, the system attempts to read it from environment variables [README.md:124]().

**Sources**: [README.md:122-125](), [requirements.txt:25]()

---

## Verification and Testing

After installation and configuration, verify the setup:

### 1. Check CLI Help

```bash
python main.py --help
```

This validates that dependencies are installed and the entry point is functional.

### 2. List Projects

```bash
python main.py --list
```

This tests database connectivity and the StateManager initialization.

### 3. Run Test Suite (Development Only)

If you installed with `poetry install --with=dev`:

```bash
# Run all tests
poetry run pytest

# Run with coverage report
poetry run pytest --cov=core

# Run linting
poetry run ruff check

# Run formatting check
poetry run ruff format --check
```

The test configuration [pyproject.toml:52-54]() includes:
- Coverage reporting (`pytest-cov`)
- 10-second test timeout (`pytest-timeout`)
- Async test support (`pytest-asyncio`)

**Sources**: [.github/workflows/ci.yml:30-35](), [pyproject.toml:44-50](), [pyproject.toml:52-54]()

---

## Workspace Structure

After successful installation, GPT Pilot creates the following directory structure:

```mermaid
graph TB
    Root["Project Root"]
    
    Root --> Core["core/<br/>(Source Code)"]
    Root --> Workspace["workspace/<br/>(Generated Projects)"]
    Root --> Config["config.json<br/>(Configuration)"]
    Root --> DB["pythagora.db<br/>(SQLite Database)"]
    Root --> Venv["venv/<br/>(Virtual Environment)"]
    
    Workspace --> Project1["project-name/<br/>(Generated App Code)"]
    
    Core --> Agents["agents/<br/>(Agent Implementations)"]
    Core --> DBLayer["db/<br/>(Database & Migrations)"]
    Core --> LLMClients["llm/<br/>(LLM Provider Clients)"]
    Core --> UILayer["ui/<br/>(CLI & IPC Interfaces)"]
    Core --> Templates["templates/<br/>(Project Templates)"]
    
    style Workspace fill:#f9f9f9,stroke:#333,stroke-width:2px
    style Config fill:#f9f9f9,stroke:#333,stroke-width:2px
```

All generated application code is stored in `workspace/<app-name>/` [README.md:129](). This isolation prevents conflicts between GPT Pilot's own code and generated projects.

**Sources**: [README.md:129](), [pyproject.toml:8]()

---

## Troubleshooting Common Installation Issues

### Import Errors

**Symptom**: `ModuleNotFoundError` when running `python main.py`

**Solution**: Ensure virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Database Connection Errors

**Symptom**: SQLAlchemy connection errors on startup

**Solution**: 
- For SQLite: Ensure directory is writable
- For PostgreSQL: Verify `asyncpg` is installed and database exists
- Check `db.url` format in `config.json`

### API Key Errors

**Symptom**: Authentication errors when contacting LLM providers

**Solution**:
- Verify API key in `config.json` or environment variables
- Check `default_provider` matches your configured provider
- Ensure no whitespace in API keys

### Poetry Lock File Issues

**Symptom**: `poetry install` fails with lock file conflicts

**Solution**:
```bash
poetry lock --no-update
poetry install
```

**Sources**: [README.md:116-143]()

---

## Next Steps

After successful installation:

1. **Configure LLM providers and agent settings**: See [Configuration Guide](#2.2)
2. **Learn CLI commands**: See [CLI Usage and Commands](#2.3)
3. **Understand the development workflow**: See [Project Lifecycle and Stages](#6.1)
4. **Explore VSCode extension**: Install from the [VS Code marketplace](https://marketplace.visualstudio.com/items?itemName=PythagoraTechnologies.pythagora-vs-code)

**Sources**: [README.md:108-128]()

---

# Page: Configuration Guide

# Configuration Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [core/config/__init__.py](core/config/__init__.py)
- [core/llm/anthropic_client.py](core/llm/anthropic_client.py)
- [data/database/.gitkeep](data/database/.gitkeep)
- [example-config.json](example-config.json)
- [pyproject.toml](pyproject.toml)
- [requirements.txt](requirements.txt)
- [tests/config/test_config.py](tests/config/test_config.py)
- [tests/config/test_env_importer.py](tests/config/test_env_importer.py)

</details>



This document explains the configuration system used by GPT Pilot, including the structure of `config.json`, LLM provider settings, agent-to-model mappings, database options, file system configuration, and UI adapters. For information about CLI arguments and commands, see [CLI Usage and Commands](#2.3). For details on the LLM client implementation and prompt engineering, see [LLM Integration](#5).

---

## Configuration File Structure

GPT Pilot uses a single JSON configuration file (`config.json`) located in the project root directory. This file controls all aspects of the system's behavior, from LLM provider settings to database connections.

### Creating the Configuration File

The configuration file is created from the example template:

```bash
cp example-config.json config.json
```

The configuration parser supports JSON with comments (lines starting with `//`), which are automatically stripped during parsing [core/config/__init__.py:462-471]().

### Configuration File Schema

```mermaid
graph TB
    ConfigFile["config.json"]
    
    ConfigFile --> LLMSection["llm: {provider: ProviderConfig}"]
    ConfigFile --> AgentSection["agent: {name: AgentLLMConfig}"]
    ConfigFile --> LogSection["log: LogConfig"]
    ConfigFile --> DBSection["db: DBConfig"]
    ConfigFile --> UISection["ui: UIConfig"]
    ConfigFile --> FSSection["fs: FileSystemConfig"]
    ConfigFile --> PromptSection["prompt: PromptConfig"]
    
    LLMSection --> OpenAIProvider["openai"]
    LLMSection --> AnthropicProvider["anthropic"]
    LLMSection --> GroqProvider["groq"]
    LLMSection --> AzureProvider["azure"]
    LLMSection --> RelaceProvider["relace"]
    
    AgentSection --> DefaultAgent["default"]
    AgentSection --> CodeMonkeyAgent["CodeMonkey"]
    AgentSection --> SpecWriterAgent["SpecWriter"]
    AgentSection --> TechLeadAgent["TechLead.*"]
    
    OpenAIProvider --> ProviderAttrs["base_url<br/>api_key<br/>connect_timeout<br/>read_timeout<br/>extra"]
    
    DefaultAgent --> AgentAttrs["provider<br/>model<br/>temperature"]
    
    style ConfigFile fill:#f9f9f9,stroke:#333,stroke-width:3px
    style LLMSection fill:#e6f3ff,stroke:#333,stroke-width:2px
    style AgentSection fill:#ffe6f0,stroke:#333,stroke-width:2px
```

**Configuration Object Hierarchy**

Sources: [core/config/__init__.py:325-443](), [example-config.json:1-89]()

---

## LLM Provider Configuration

The `llm` section defines connection settings for each LLM provider. Each provider configuration includes the API endpoint, authentication, and timeout settings.

### Provider Configuration Structure

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `base_url` | string \| null | Provider default | Base URL for API requests (exclude `/chat/completions`) |
| `api_key` | string \| null | Environment variable | API key for authentication |
| `connect_timeout` | float | 60.0 | Connection timeout in seconds |
| `read_timeout` | float | 60.0 | Response stream timeout in seconds |
| `extra` | object \| null | null | Provider-specific extra configuration |

### Supported LLM Providers

```mermaid
graph LR
    subgraph "LLMProvider Enum"
        OPENAI["OPENAI"]
        ANTHROPIC["ANTHROPIC"]
        GROQ["GROQ"]
        AZURE["AZURE"]
        RELACE["RELACE"]
        LMSTUDIO["LM_STUDIO"]
    end
    
    subgraph "Client Implementations"
        OpenAIClient["OpenAIClient"]
        AnthropicClient["AnthropicClient"]
        GroqClient["GroqClient"]
        AzureClient["AzureClient<br/>extends OpenAIClient"]
        RelaceClient["RelaceClient"]
    end
    
    OPENAI --> OpenAIClient
    ANTHROPIC --> AnthropicClient
    GROQ --> GroqClient
    AZURE --> AzureClient
    RELACE --> RelaceClient
    LMSTUDIO --> OpenAIClient
    
    OpenAIClient -.->|also supports| OpenRouter["OpenRouter"]
    OpenAIClient -.->|also supports| LocalLLM["Local LLMs<br/>LM-Studio"]
```

Sources: [core/config/__init__.py:70-81](), [core/llm/anthropic_client.py:26-39]()

### Example Provider Configurations

**OpenAI Configuration:**
```json
{
  "llm": {
    "openai": {
      "base_url": null,
      "api_key": null,
      "connect_timeout": 60.0,
      "read_timeout": 20.0
    }
  }
}
```

When `base_url` and `api_key` are `null`, the client uses default values from environment variables (`OPENAI_API_KEY`, `OPENAI_BASE_URL`).

**Anthropic Configuration:**
```json
{
  "llm": {
    "anthropic": {
      "base_url": "https://api.anthropic.com",
      "api_key": "your-api-key",
      "connect_timeout": 60.0,
      "read_timeout": 20.0
    }
  }
}
```

**Azure OpenAI Configuration:**
```json
{
  "llm": {
    "azure": {
      "base_url": "https://your-resource.openai.azure.com/",
      "api_key": "your-api-key",
      "connect_timeout": 60.0,
      "read_timeout": 20.0,
      "extra": {
        "azure_deployment": "your-deployment-id",
        "api_version": "2024-02-01"
      }
    }
  }
}
```

**OpenRouter Configuration:**
```json
{
  "llm": {
    "openai": {
      "base_url": "https://openrouter.ai/api/v1",
      "api_key": "sk-or-v1-your-key"
    }
  }
}
```

OpenRouter uses the `openai` provider with a custom `base_url`.

Sources: [example-config.json:5-30](), [core/config/__init__.py:93-120]()

---

## Agent-to-Model Mapping

The `agent` section maps specific agents to LLM models and providers. This allows different agents to use different models optimized for their specific tasks.

### Agent Configuration Structure

Each agent configuration specifies:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `provider` | LLMProvider | OPENAI | Which LLM provider to use |
| `model` | string | "gpt-4o-2024-05-13" | Specific model identifier |
| `temperature` | float | 0.5 | Sampling temperature (0.0-1.0) |

### Agent Resolution Flow

```mermaid
graph TD
    AgentCall["Agent calls<br/>self.llm_req()"]
    GetConfig["Config.llm_for_agent(agent_name)"]
    CheckAgent{"agent_name<br/>in config.agent?"}
    
    AgentCall --> GetConfig
    GetConfig --> CheckAgent
    
    CheckAgent -->|Yes| GetAgentConfig["agent_config =<br/>config.agent[agent_name]"]
    CheckAgent -->|No| GetDefaultConfig["agent_config =<br/>config.agent['default']"]
    
    GetAgentConfig --> GetProvider["provider_config =<br/>config.llm[agent_config.provider]"]
    GetDefaultConfig --> GetProvider
    
    GetProvider --> MergeConfigs["LLMConfig.from_provider_and_agent_configs()"]
    
    MergeConfigs --> FinalConfig["LLMConfig<br/>provider, model, base_url,<br/>api_key, temperature,<br/>timeouts"]
    
    FinalConfig --> CreateClient["Create LLM client<br/>OpenAIClient/AnthropicClient/etc"]
```

Sources: [core/config/__init__.py:423-434](), [core/config/__init__.py:176-187]()

### Default Agent Configurations

The system includes optimized default configurations for specific agents:

| Agent Name | Provider | Model | Temperature | Purpose |
|------------|----------|-------|-------------|---------|
| `default` | openai | gpt-4o-2024-05-13 | 0.5 | General tasks |
| `CodeMonkey` | openai | claude-sonnet-4-20250514 | 0.0 | Code generation |
| `CodeMonkey.code_review` | openai | claude-3-5-sonnet-20240620 | 0.0 | Code review |
| `CodeMonkey.implement_changes` | relace | relace-code-merge | 0.0 | Code merging |
| `CodeMonkey.describe_files` | openai | gpt-4o-mini-2024-07-18 | 0.0 | File descriptions |
| `BugHunter.check_logs` | openai | claude-sonnet-4-20250514 | 0.5 | Log analysis |
| `Developer.parse_task` | openai | claude-3-5-sonnet-20241022 | 0.0 | Task parsing |
| `Developer.breakdown_current_task` | openai | claude-sonnet-4-20250514 | 0.5 | Task breakdown |
| `SpecWriter` | openai | claude-sonnet-4-20250514 | 0.0 | Specification writing |
| `TechLead.plan_epic` | openai | claude-3-5-sonnet-20240620 | 0.5 | Epic planning |
| `TechLead.epic_breakdown` | openai | claude-3-5-sonnet-20241022 | 0.5 | Epic breakdown |
| `Frontend` | openai | claude-sonnet-4-20250514 | 0.0 | Frontend development |
| `Troubleshooter.generate_bug_report` | openai | claude-sonnet-4-20250514 | 0.5 | Bug reporting |
| `get_relevant_files` | openai | gpt-4o-2024-05-13 | 0.5 | File relevance |

Sources: [core/config/__init__.py:38-53](), [core/config/__init__.py:337-415]()

### Custom Agent Configuration Example

To override the default configuration for a specific agent:

```json
{
  "agent": {
    "CodeMonkey": {
      "provider": "anthropic",
      "model": "claude-3-opus-20240229",
      "temperature": 0.2
    }
  }
}
```

If an agent name is not found in the configuration, it falls back to the `default` agent configuration [core/config/__init__.py:431]().

Sources: [tests/config/test_config.py:40-62]()

---

## Database Configuration

The `db` section configures the database connection used for state persistence and project storage.

### Database Configuration Structure

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `url` | string | sqlite+aiosqlite:///data/database/pythagora.db | SQLAlchemy connection URL |
| `debug_sql` | boolean | false | Log all SQL queries to console |
| `save_llm_requests` | boolean | false | Persist LLM requests to database |

### Supported Database Types

```mermaid
graph TB
    DBConfig["DBConfig"]
    
    DBConfig --> SQLite["SQLite<br/>sqlite+aiosqlite://"]
    DBConfig --> PostgreSQL["PostgreSQL<br/>postgresql+asyncpg://"]
    
    SQLite --> SQLiteDriver["aiosqlite<br/>Built-in dependency"]
    PostgreSQL --> PostgreSQLDrivers["asyncpg + psycopg2<br/>Optional dependencies"]
    
    SQLiteDriver --> ValidateURL["validate_url_scheme()<br/>line 251"]
    PostgreSQLDrivers --> ValidateURL
    
    ValidateURL --> CheckImport{"Import asyncpg<br/>successful?"}
    CheckImport -->|No| RaiseError["Raise ValueError:<br/>'install asyncpg and psycopg2'"]
    CheckImport -->|Yes| AllowPostgreSQL["Allow PostgreSQL"]
```

Sources: [core/config/__init__.py:233-261]()

### SQLite Configuration (Default)

SQLite is used by default and requires no additional setup:

```json
{
  "db": {
    "url": "sqlite+aiosqlite:///data/database/pythagora.db",
    "debug_sql": false,
    "save_llm_requests": false
  }
}
```

The database file is created at `data/database/pythagora.db` relative to the project root [data/database/.gitkeep:1]().

### PostgreSQL Configuration

To use PostgreSQL, first install the required drivers:

```bash
pip install asyncpg psycopg2
```

Then update the configuration:

```json
{
  "db": {
    "url": "postgresql+asyncpg://user:password@localhost:5432/gpt_pilot",
    "debug_sql": false
  }
}
```

The URL format is: `postgresql+asyncpg://<user>:<password>@<host>:<port>/<database>`

Sources: [README.md:135-143](), [example-config.json:49-54](), [core/config/__init__.py:249-260]()

---

## File System Configuration

The `fs` section configures the virtual file system used to manage project files.

### File System Configuration Structure

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `type` | string | "local" | File system type (only "local" supported) |
| `workspace_root` | string | "workspace" | Root directory for all projects |
| `ignore_paths` | array | [See below] | Paths to ignore when scanning |
| `ignore_size_threshold` | integer | 50000 | Maximum file size in bytes |

### Default Ignore Patterns

The following patterns are ignored by default [core/config/__init__.py:11-34]():

```python
DEFAULT_IGNORE_PATHS = [
    ".git",
    ".gpt-pilot",
    ".idea",
    ".vscode",
    ".next",
    ".DS_Store",
    "__pycache__",
    "site-packages",
    "node_modules",
    "package-lock.json",
    "venv",
    ".venv",
    "dist",
    "build",
    "target",
    "*.min.js",
    "*.min.css",
    "*.svg",
    "*.csv",
    "*.log",
    "go.sum",
    "migration_lock.toml",
]
```

Files larger than `ignore_size_threshold` (default 50KB) are automatically ignored, even if they don't match any pattern [core/config/__init__.py:35]().

### Example File System Configuration

```json
{
  "fs": {
    "type": "local",
    "workspace_root": "workspace",
    "ignore_paths": [
      ".git",
      "node_modules",
      "*.log",
      "custom_folder"
    ],
    "ignore_size_threshold": 100000
  }
}
```

Sources: [core/config/__init__.py:296-323](), [example-config.json:58-88]()

---

## UI Adapter Configuration

The `ui` section selects the user interface adapter used for communication between GPT Pilot and the user.

### Available UI Adapters

```mermaid
graph TB
    UIConfig["UIConfig<br/>discriminated union"]
    
    UIConfig --> PlainUI["PlainUIConfig<br/>type: 'plain'"]
    UIConfig --> IPCUI["LocalIPCConfig<br/>type: 'ipc-client'"]
    UIConfig --> VirtualUI["VirtualUIConfig<br/>type: 'virtual'"]
    
    PlainUI --> Terminal["PlainConsoleUI<br/>Terminal interface"]
    IPCUI --> VSCode["IPCClientUI<br/>VSCode extension"]
    VirtualUI --> Testing["VirtualUI<br/>Testing only"]
    
    IPCUI --> IPCParams["host: 'localhost'<br/>port: 8125"]
    VirtualUI --> InputsList["inputs: [...]<br/>Pre-configured responses"]
```

Sources: [core/config/__init__.py:83-293]()

### Plain UI Configuration

The plain UI adapter uses a terminal-based interface:

```json
{
  "ui": {
    "type": "plain"
  }
}
```

This is the default configuration and suitable for CLI usage [core/config/__init__.py:263-268]().

### IPC Client Configuration

The IPC client adapter communicates with the VSCode extension via TCP socket:

```json
{
  "ui": {
    "type": "ipc-client",
    "host": "localhost",
    "port": 8125
  }
}
```

The VSCode extension automatically sets this configuration when launching GPT Pilot [core/config/__init__.py:271-278]().

### Virtual UI Configuration

The virtual UI is used for testing and automation:

```json
{
  "ui": {
    "type": "virtual",
    "inputs": [
      "Create a todo app",
      "yes",
      "continue"
    ]
  }
}
```

This adapter provides pre-configured responses instead of prompting the user [core/config/__init__.py:281-287]().

Sources: [core/config/__init__.py:263-293]()

---

## Logging Configuration

The `log` section controls application logging behavior.

### Logging Configuration Structure

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `level` | string | "DEBUG" | Minimum log level (DEBUG/INFO/WARNING/ERROR/CRITICAL) |
| `format` | string | "%(asctime)s %(levelname)s..." | Python logging format string |
| `output` | string \| null | "data/pythagora.log" | Log file path (null for stderr) |
| `max_lines` | integer | (from constants) | Maximum log file lines |

### Example Logging Configuration

**File Logging (Default):**
```json
{
  "log": {
    "level": "DEBUG",
    "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
    "output": "pythagora.log"
  }
}
```

**Console Logging:**
```json
{
  "log": {
    "level": "INFO",
    "format": "%(levelname)s: %(message)s",
    "output": null
  }
}
```

Setting `output` to `null` sends logs to stderr instead of a file [core/config/__init__.py:223-226]().

Sources: [core/config/__init__.py:209-231](), [example-config.json:42-48]()

---

## Prompt Template Configuration

The `prompt` section configures the search paths for Jinja2 prompt templates.

### Prompt Configuration Structure

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `paths` | array | ["core/prompts"] | Directories to search for templates |

### Example Prompt Configuration

```json
{
  "prompt": {
    "paths": [
      "core/prompts",
      "custom_prompts"
    ]
  }
}
```

All paths must be valid directories, otherwise validation fails [core/config/__init__.py:200-206]().

Sources: [core/config/__init__.py:190-207]()

---

## Configuration Loading and Validation

### Configuration Loading Flow

```mermaid
graph TD
    StartCLI["CLI: python main.py"]
    CheckConfigPath{"--config<br/>specified?"}
    
    StartCLI --> CheckConfigPath
    
    CheckConfigPath -->|Yes| LoadCustom["Load custom path"]
    CheckConfigPath -->|No| LoadDefault["Load config.json"]
    
    LoadCustom --> ReadFile["ConfigLoader.load(path)"]
    LoadDefault --> ReadFile
    
    ReadFile --> DetectEncoding{"BOM or<br/>null bytes?"}
    
    DetectEncoding -->|Yes| UTF16["Decode as UTF-16"]
    DetectEncoding -->|No| UTF8["Decode as UTF-8"]
    
    UTF16 --> RemoveComments["_remove_json_comments()"]
    UTF8 --> RemoveComments
    
    RemoveComments --> ParseJSON["Config.model_validate_json()"]
    
    ParseJSON --> Validate["Pydantic validation"]
    
    Validate --> CheckDB{"db.url<br/>valid scheme?"}
    Validate --> CheckPrompts{"prompt.paths<br/>exist?"}
    
    CheckDB -->|Invalid| RaiseDBError["ValueError:<br/>Unsupported scheme"]
    CheckPrompts -->|Invalid| RaisePromptError["ValueError:<br/>Invalid path"]
    
    CheckDB -->|Valid| StoreConfig["loader.config = Config()"]
    CheckPrompts -->|Valid| StoreConfig
    
    StoreConfig --> AdaptBedrock["adapt_for_bedrock()"]
    AdaptBedrock --> Ready["Configuration ready"]
```

Sources: [core/config/__init__.py:444-502](), [core/config/__init__.py:507-532]()

### Configuration Class Hierarchy

The configuration uses Pydantic models for validation:

| Class | Description | Location |
|-------|-------------|----------|
| `Config` | Root configuration object | [core/config/__init__.py:325-443]() |
| `LLMConfig` | Complete LLM configuration for an agent | [core/config/__init__.py:140-188]() |
| `ProviderConfig` | Provider connection settings | [core/config/__init__.py:93-120]() |
| `AgentLLMConfig` | Agent model selection | [core/config/__init__.py:122-138]() |
| `DBConfig` | Database connection | [core/config/__init__.py:233-261]() |
| `FileSystemConfig` | File system settings | [core/config/__init__.py:305-323]() |
| `UIConfig` | UI adapter (discriminated union) | [core/config/__init__.py:290-293]() |
| `LogConfig` | Logging settings | [core/config/__init__.py:209-231]() |
| `PromptConfig` | Prompt template paths | [core/config/__init__.py:190-207]() |

All configuration classes inherit from `_StrictModel` which sets `extra="forbid"` to reject unknown fields [core/config/__init__.py:60-67]().

### Accessing Configuration

```python
from core.config import get_config

config = get_config()

# Get LLM config for specific agent
llm_config = config.llm_for_agent("CodeMonkey")
print(llm_config.provider)  # LLMProvider.ANTHROPIC
print(llm_config.model)      # "claude-3-opus"

# Get all LLM configs
all_configs = config.all_llms()
```

Sources: [core/config/__init__.py:535-544](), [tests/config/test_config.py:40-62]()

---

## Advanced Configuration Topics

### AWS Bedrock Support

When using Anthropic models via AWS Bedrock, model names must be adapted to Bedrock-specific identifiers. The `adapt_for_bedrock()` function automatically converts model names:

| Standard Model | Bedrock Model |
|----------------|---------------|
| claude-3-5-sonnet-20241022 | us.anthropic.claude-3-5-sonnet-20241022-v2:0 |
| claude-3-5-sonnet-20240620 | us.anthropic.claude-3-5-sonnet-20240620-v1:0 |
| claude-3-sonnet-20240229 | us.anthropic.claude-3-sonnet-20240229-v1:0 |
| claude-3-haiku-20240307 | us.anthropic.claude-3-haiku-20240307-v1:0 |
| claude-3-opus-20240229 | us.anthropic.claude-3-opus-20240229-v1:0 |

This conversion is triggered when the Anthropic `base_url` contains "bedrock/anthropic" [core/config/__init__.py:507-532]().

Example Bedrock configuration:

```json
{
  "llm": {
    "anthropic": {
      "base_url": "https://bedrock-runtime.us-east-1.amazonaws.com/bedrock/anthropic",
      "api_key": "your-aws-access-key"
    }
  }
}
```

### Environment Variable Fallbacks

When `api_key` is set to `null`, LLM clients read keys from environment variables:

| Provider | Environment Variable |
|----------|---------------------|
| OpenAI | `OPENAI_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |
| Groq | `GROQ_API_KEY` |
| Azure | `AZURE_OPENAI_API_KEY` |

This allows keeping sensitive credentials out of the configuration file [core/config/__init__.py:102-104]().

### Configuration File Encoding

The configuration loader supports multiple encodings:

- UTF-8 (default)
- UTF-16 with BOM (byte order mark)
- UTF-16-LE with BOM
- UTF-16-BE with BOM

The loader automatically detects the encoding by checking for null bytes and BOM markers [core/config/__init__.py:490-498]().

Sources: [core/config/__init__.py:507-542](), [tests/config/test_config.py:111-131](), [tests/config/test_env_importer.py:5-29]()

---

## Configuration Validation Errors

Common validation errors and their solutions:

**Unsupported Provider:**
```
ValidationError: agent.default.provider
  Input should be 'openai', 'anthropic', 'groq', 'azure', 'relace', or 'lm-studio'
```
Solution: Use a supported provider name from the `LLMProvider` enum [core/config/__init__.py:70-81]().

**Invalid Database URL:**
```
ValueError: Unsupported database URL scheme in: mysql://...
```
Solution: Use `sqlite+aiosqlite://` or `postgresql+asyncpg://` [core/config/__init__.py:249-260]().

**Missing PostgreSQL Drivers:**
```
ValueError: To use PostgreSQL database, please install `asyncpg` and `psycopg2` packages
```
Solution: Run `pip install asyncpg psycopg2` [core/config/__init__.py:256-258]().

**Invalid Prompt Path:**
```
ValueError: Invalid prompt path: /nonexistent/path
```
Solution: Ensure all paths in `prompt.paths` exist and are directories [core/config/__init__.py:200-206]().

**Unknown Configuration Field:**
```
ValidationError: Extra inputs are not permitted
```
Solution: Remove unknown fields. The configuration uses `extra="forbid"` [core/config/__init__.py:65-66]().

Sources: [tests/config/test_config.py:73-94](), [core/config/__init__.py:60-67]()

---

## Complete Configuration Example

Here is a complete, annotated configuration file:

```json
{
  "llm": {
    "openai": {
      "base_url": null,
      "api_key": null,
      "connect_timeout": 60.0,
      "read_timeout": 20.0
    },
    "anthropic": {
      "base_url": "https://api.anthropic.com",
      "api_key": "sk-ant-...",
      "connect_timeout": 60.0,
      "read_timeout": 20.0
    },
    "groq": {
      "base_url": "https://api.groq.com/openai/v1",
      "api_key": "gsk_...",
      "connect_timeout": 60.0,
      "read_timeout": 20.0
    }
  },
  "agent": {
    "default": {
      "provider": "openai",
      "model": "gpt-4o-2024-05-13",
      "temperature": 0.5
    },
    "CodeMonkey": {
      "provider": "anthropic",
      "model": "claude-3-5-sonnet-20241022",
      "temperature": 0.0
    },
    "SpecWriter": {
      "provider": "openai",
      "model": "gpt-4o-2024-05-13",
      "temperature": 0.5
    }
  },
  "log": {
    "level": "DEBUG",
    "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
    "output": "pythagora.log"
  },
  "db": {
    "url": "sqlite+aiosqlite:///data/database/pythagora.db",
    "debug_sql": false,
    "save_llm_requests": false
  },
  "ui": {
    "type": "plain"
  },
  "fs": {
    "type": "local",
    "workspace_root": "workspace",
    "ignore_paths": [
      ".git",
      "node_modules",
      "venv",
      "*.log"
    ],
    "ignore_size_threshold": 50000
  },
  "prompt": {
    "paths": [
      "core/prompts"
    ]
  }
}
```

Sources: [example-config.json:1-89](), [core/config/__init__.py:325-443]()

---

# Page: CLI Usage and Commands

# CLI Usage and Commands

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [core/cli/helpers.py](core/cli/helpers.py)
- [core/cli/main.py](core/cli/main.py)
- [core/db/models/project.py](core/db/models/project.py)
- [core/db/models/project_state.py](core/db/models/project_state.py)
- [core/db/v0importer.py](core/db/v0importer.py)
- [core/state/state_manager.py](core/state/state_manager.py)
- [core/ui/api_server.py](core/ui/api_server.py)
- [pyproject.toml](pyproject.toml)
- [requirements.txt](requirements.txt)
- [tests/cli/test_cli.py](tests/cli/test_cli.py)
- [tests/db/test_project.py](tests/db/test_project.py)

</details>



This page documents the command-line interface (CLI) for GPT Pilot, including all available commands, options, and their usage patterns. The CLI provides a terminal-based interface for managing projects, controlling the development workflow, and configuring the system.

For information about configuring LLM providers, database settings, and file system options, see [Configuration Guide](#2.2). For details about the VSCode extension interface, see [UI and Communication Layer](#3.4).

---

## Overview

The GPT Pilot CLI is the primary interface for developers who prefer terminal-based workflows or need to integrate GPT Pilot into automated pipelines. The main entry point is `python main.py`, which accepts various command-line arguments to control its behavior.

**Sources:** [core/cli/main.py:429-438](), [README.md:107-128]()

---

## Command Structure

### Basic Invocation

The CLI follows this general pattern:

```bash
python main.py [OPTIONS]
```

All commands are executed through a single entry point with different option combinations determining the behavior. The CLI uses an async architecture with `async_main()` as the core orchestration function.

**Command Flow Diagram:**

```mermaid
graph TB
    Start["python main.py"] --> ParseArgs["parse_arguments()"]
    ParseArgs --> LoadConfig["load_config(args)"]
    LoadConfig --> InitDB["SessionManager.start()"]
    InitDB --> InitUI["UIBase.start()"]
    InitUI --> RouteCmd{Command Type}
    
    RouteCmd -->|"--list"| ListProjects["list_projects_branches_states()"]
    RouteCmd -->|"--list-json"| ListJSON["list_projects_json()"]
    RouteCmd -->|"--show-config"| ShowConfig["show_config()"]
    RouteCmd -->|"--delete"| DeleteProject["delete_project()"]
    RouteCmd -->|"--import-v0"| ImportV0["LegacyDatabaseImporter.import_database()"]
    RouteCmd -->|"--project/--branch/--step"| LoadExisting["load_project()"]
    RouteCmd -->|"No args"| StartNew["start_new_project()"]
    
    LoadExisting --> RunSession["run_pythagora_session()"]
    StartNew --> RunSession
    
    RunSession --> Orchestrator["Orchestrator.run()"]
    Orchestrator --> Cleanup["cleanup()"]
    
    ListProjects --> End["Exit"]
    ListJSON --> End
    ShowConfig --> End
    DeleteProject --> End
    ImportV0 --> End
    Cleanup --> End
    
    style Start fill:#e1f5e1
    style End fill:#ffe1e1
    style Orchestrator fill:#fff4e1
```

**Sources:** [core/cli/main.py:324-427](), [core/cli/helpers.py:180-281]()

---

## Project Management Commands

### Listing Projects

#### List Projects (Human-Readable)

```bash
python main.py --list
```

Displays all projects with their branches and states in a human-readable format:

```
* project_name (project_id)
  - branch_name (branch_id)
    States: 1-N
```

**Implementation:** [core/cli/helpers.py:385-435]()

#### List Projects (JSON)

```bash
python main.py --list-json
```

Outputs project information in JSON format for programmatic consumption:

```json
[
  {
    "id": "project_uuid",
    "name": "My Project",
    "folder_name": "my-project",
    "updated_at": "2024-01-01T12:00:00"
  }
]
```

**Implementation:** [core/cli/helpers.py:333-352]()

### Creating a New Project

```bash
python main.py
```

Starting GPT Pilot without arguments initiates a new project creation workflow:

1. Prompts user to select project type (`node` or `swagger`)
2. Creates a new `Project` with a unique ID
3. Initializes default `Branch` (named "main")
4. Creates initial `ProjectState` with empty specification
5. Sets up workspace directory in `config.fs.workspace_root`

**New Project Flow:**

```mermaid
stateDiagram-v2
    [*] --> AskProjectType: "python main.py"
    AskProjectType --> SelectNode: "User selects 'node'"
    AskProjectType --> SelectSwagger: "User selects 'swagger'"
    
    SelectNode --> CreateProject: "create_project(project_type='node')"
    SelectSwagger --> CreateProject: "create_project(project_type='swagger')"
    
    CreateProject --> InitState: "ProjectState.create_initial_state()"
    InitState --> SetupVFS: "init_file_system(load_existing=False)"
    SetupVFS --> LaunchOrchestrator: "Orchestrator.run()"
    LaunchOrchestrator --> [*]
```

**Auto-Start with Initial Prompt:**

```bash
python main.py --initial-prompt "Build a todo app with React"
```

Automatically selects "node" stack and starts the project with the given description, bypassing interactive prompts.

**Sources:** [core/cli/main.py:121-191](), [core/state/state_manager.py:172-246]()

### Loading Existing Projects

#### Load Latest State

```bash
python main.py --project <project_id>
```

Loads the project at its latest committed state. The `project_id` is a UUID displayed by `--list` commands.

**Example:**
```bash
python main.py --project ca7a0cc9-767f-472a-aefb-0c8d3377c9bc
```

#### Load Specific Step

```bash
python main.py --project <project_id> --step <step_index>
```

Loads the project at a specific step index. **Warning:** This deletes all progress after the specified step.

**Example:**
```bash
python main.py --project ca7a0cc9-767f-472a-aefb-0c8d3377c9bc --step 42
```

**State Loading Mechanism:**

```mermaid
graph TB
    LoadCmd["load_project(project_id, branch_id, step_index)"] --> GetBranch["Branch.get_by_id() or Project.get_branch()"]
    GetBranch --> GetState{step_index provided?}
    
    GetState -->|Yes| LoadStep["branch.get_state_at_step(step_index)"]
    GetState -->|No| LoadLast["branch.get_last_state()"]
    
    LoadStep --> DeleteAfter["state.delete_after()"]
    LoadLast --> CreateNext["state.create_next_state()"]
    DeleteAfter --> CreateNext
    
    CreateNext --> InitVFS["init_file_system(load_existing=True)"]
    InitVFS --> SetCurrent["StateManager.current_state = state"]
    SetCurrent --> Done["Return ProjectState"]
```

#### Load Specific Branch

```bash
python main.py --branch <branch_id>
```

Loads a specific branch (currently only "main" branch is supported, but the architecture supports multiple branches).

#### Load Specific Project State

```bash
python main.py --project-state-id <state_id>
```

Loads a specific project state by its UUID, useful for debugging or examining historical states.

**Sources:** [core/cli/main.py:204-315](), [core/state/state_manager.py:272-415](), [core/cli/helpers.py:585-660]()

### Deleting Projects

```bash
python main.py --delete <project_id>
```

Permanently deletes a project and all associated data:
- All project states in all branches
- All files and file contents
- User inputs, command logs, LLM requests
- Orphaned specifications and knowledge bases

**Warning:** This operation cannot be undone.

**Deletion Cascade:**

```mermaid
graph TD
    DeleteCmd["delete_project(project_id)"] --> DeleteProj["Project.delete_by_id(session, project_id)"]
    DeleteProj --> CascadeBranch["CASCADE: Delete all Branch records"]
    CascadeBranch --> CascadeState["CASCADE: Delete all ProjectState records"]
    CascadeState --> CascadeFile["CASCADE: Delete all File records"]
    
    DeleteProj --> CleanupOrphans["Cleanup orphaned records"]
    CleanupOrphans --> CleanSpec["Specification.delete_orphans()"]
    CleanupOrphans --> CleanContent["FileContent.delete_orphans()"]
    CleanupOrphans --> CleanKB["KnowledgeBase.delete_orphans()"]
```

**Sources:** [core/state/state_manager.py:248-259](), [core/db/models/project.py:167-177]()

---

## Configuration Options

### Config File Path

```bash
python main.py --config /path/to/config.json
```

Specifies a custom configuration file path. Defaults to `config.json` in the current directory.

**Sources:** [core/cli/helpers.py:212](), [core/cli/helpers.py:284-330]()

### Show Default Configuration

```bash
python main.py --show-config
```

Outputs the complete default configuration in JSON format to stdout. Useful for creating a custom config file.

**Sources:** [core/cli/helpers.py:437-441](), [core/cli/helpers.py:213]()

### Log Level

```bash
python main.py --level debug
```

Sets the logging verbosity level. Valid values: `debug`, `info`, `warning`, `error`, `critical`.

**Sources:** [core/cli/helpers.py:214](), [core/cli/helpers.py:303-304]()

### Database URL

```bash
python main.py --database sqlite+aiosqlite:///path/to/db.db
```

Overrides the database URL from the config file. Supports SQLite and PostgreSQL:

- SQLite: `sqlite+aiosqlite:///data/database/pythagora.db`
- PostgreSQL: `postgresql+asyncpg://user:pass@localhost/dbname`

**Sources:** [core/cli/helpers.py:215](), [core/cli/helpers.py:306-307]()

---

## LLM Configuration Options

### LLM Endpoint

```bash
python main.py --llm-endpoint openai:https://api.openai.com
python main.py --llm-endpoint anthropic:https://api.anthropic.com
```

Specifies custom API endpoints for LLM providers. Format: `<provider>:<url>`

Supported providers: `openai`, `anthropic`, `groq`, `azure`

**Multiple Endpoints:**
```bash
python main.py \
  --llm-endpoint openai:https://custom.openai.proxy \
  --llm-endpoint anthropic:https://custom.anthropic.proxy
```

**Sources:** [core/cli/helpers.py:228-234](), [core/cli/helpers.py:61-86]()

### LLM API Key

```bash
python main.py --llm-key openai:sk-abc123
python main.py --llm-key anthropic:sk-ant-xyz789
```

Provides LLM API keys via command line. Format: `<provider>:<key>`

**Security Note:** Prefer using environment variables or config file for API keys rather than command-line arguments, which may be visible in process lists.

**Sources:** [core/cli/helpers.py:235-241](), [core/cli/helpers.py:156-178]()

---

## IPC and Extension Options

### Local IPC Connection

```bash
python main.py --local-ipc-port 8125 --local-ipc-host localhost
```

Connects to a local IPC server (typically the VSCode extension) instead of using terminal UI. The CLI acts as an IPC client in this mode.

**IPC Architecture:**

```mermaid
graph LR
    VSCode["VSCode Extension"] -->|"TCP Socket :8125"| IPCServer["IPCServer"]
    IPCServer <-->|"Length-Prefixed JSON"| IPCClientUI["IPCClientUI"]
    IPCClientUI --> Orchestrator["Orchestrator"]
    
    PlainConsoleUI["PlainConsoleUI"] -.->|"Alternative to"| IPCClientUI
```

**Sources:** [core/cli/helpers.py:216-217](), [core/cli/helpers.py:309-310]()

### API Server Options

```bash
python main.py --enable-api-server \
  --local-api-server-host 0.0.0.0 \
  --local-api-server-port 8222
```

Starts an IPC server that external clients can connect to for querying project state, chat history, and other information. Separate from the IPC client connection.

**Default:** Enabled on `localhost:8222`

**Sources:** [core/cli/main.py:371-380](), [core/cli/helpers.py:258-275]()

### Extension Version

```bash
python main.py --extension-version 1.2.3
```

Reports the VSCode extension version to telemetry. Used internally by the VSCode extension.

**Sources:** [core/cli/helpers.py:248](), [core/cli/main.py:362-365]()

---

## Advanced Options

### Import Legacy Database

```bash
python main.py --import-v0 /path/to/old/database.db
```

Imports projects from a GPT Pilot v0 (legacy) database into the current database format. Preserves:
- Project metadata
- Architecture and specifications
- Latest task state and files
- Development history (converted to new format)

**Import Process:**

```mermaid
graph TB
    Start["--import-v0 old.db"] --> Verify["Verify v0 schema"]
    Verify --> LoadApps["Load app records"]
    LoadApps --> ForEach["For each app"]
    
    ForEach --> CheckExists{Project exists?}
    CheckExists -->|Yes| Skip["Skip import"]
    CheckExists -->|No| Import["Import app"]
    
    Import --> CreateProj["Create Project + Branch"]
    CreateProj --> CreateSpec["Create Specification"]
    CreateSpec --> ImportTask["Import latest task"]
    ImportTask --> SaveFiles["Save task files"]
    SaveFiles --> Commit["Commit state"]
    
    Skip --> Next{More apps?}
    Commit --> Next
    Next -->|Yes| ForEach
    Next -->|No| Done["Import complete"]
```

**Sources:** [core/db/v0importer.py:30-275](), [core/cli/helpers.py:242-246]()

### Email for Telemetry

```bash
python main.py --email user@example.com
```

Associates telemetry data with an email address. Used for crash reporting and analytics.

**Sources:** [core/cli/helpers.py:247](), [core/cli/main.py:356-360]()

### Git Version Control

```bash
python main.py --use-git
```

Enables Git integration for version control (feature flag, implementation may vary).

**Sources:** [core/cli/helpers.py:249]()

### Access Token

```bash
python main.py --access-token abc123xyz789
```

Provides an access token for authenticating with Pythagora cloud services.

**Sources:** [core/cli/helpers.py:257](), [core/cli/main.py:367-369]()

### Auto-Confirm Breakdown

```bash
python main.py --no-auto-confirm-breakdown
```

Disables automatic confirmation during task breakdown, requiring manual user approval for each step.

**Default:** Auto-confirmation is enabled

**Sources:** [core/cli/helpers.py:250-256](), [core/cli/main.py:381-382]()

---

## Command-Line Argument Reference

**Complete Options Table:**

| Argument | Type | Description | Default |
|----------|------|-------------|---------|
| `--config` | path | Path to configuration file | `config.json` |
| `--show-config` | flag | Output default configuration to stdout | - |
| `--level` | string | Log level (debug/info/warning/error/critical) | From config |
| `--database` | string | Database URL | From config |
| `--local-ipc-port` | int | Local IPC port for client connection | - |
| `--local-ipc-host` | string | Local IPC host for client connection | `localhost` |
| `--version` | flag | Show version and exit | - |
| `--list` | flag | List all projects (human-readable) | - |
| `--list-json` | flag | List all projects (JSON format) | - |
| `--project` | UUID | Load specific project | - |
| `--branch` | UUID | Load specific branch | - |
| `--step` | int | Load specific step (deletes progress after) | - |
| `--project-state-id` | UUID | Load specific project state | - |
| `--delete` | UUID | Delete project permanently | - |
| `--llm-endpoint` | string | Custom LLM endpoint (provider:url) | From config |
| `--llm-key` | string | LLM API key (provider:key) | From config |
| `--import-v0` | path | Import from legacy v0 database | - |
| `--email` | string | User email for telemetry | - |
| `--extension-version` | string | VSCode extension version | - |
| `--use-git` | flag | Enable Git integration | `false` |
| `--access-token` | string | Pythagora cloud access token | - |
| `--no-auto-confirm-breakdown` | flag | Disable auto-confirmation | `false` (auto-confirm on) |
| `--enable-api-server` | flag | Enable IPC server for clients | `true` |
| `--local-api-server-host` | string | IPC server host | `localhost` |
| `--local-api-server-port` | int | IPC server port | `8222` |
| `--initial-prompt` | string | Auto-start with prompt (node stack) | - |

**Sources:** [core/cli/helpers.py:180-281]()

---

## Usage Examples

### Basic Development Workflow

**1. Start a new project:**
```bash
python main.py
# Select project type when prompted
```

**2. Continue working on existing project:**
```bash
python main.py --project ca7a0cc9-767f-472a-aefb-0c8d3377c9bc
```

**3. Roll back to specific step:**
```bash
python main.py --project ca7a0cc9-767f-472a-aefb-0c8d3377c9bc --step 25
```

**4. List all projects:**
```bash
python main.py --list
```

### Advanced Workflows

**Custom configuration and logging:**
```bash
python main.py \
  --config my-config.json \
  --level debug \
  --database postgresql+asyncpg://localhost/mydb
```

**Using custom LLM endpoints:**
```bash
python main.py \
  --llm-endpoint openai:https://my-proxy.com \
  --llm-key openai:sk-custom-key
```

**VSCode extension mode:**
```bash
python main.py \
  --local-ipc-port 8125 \
  --extension-version 2.0.0 \
  --email developer@example.com
```

**Import and migrate from v0:**
```bash
python main.py --import-v0 /path/to/old/gpt-pilot.db
python main.py --list  # Verify imported projects
```

**Automated CI/CD with initial prompt:**
```bash
python main.py \
  --initial-prompt "Build a REST API for user management" \
  --config ci-config.json \
  --email ci@example.com \
  --no-auto-confirm-breakdown
```

**Sources:** [README.md:145-184](), [core/cli/main.py:324-427]()

---

## State Management and Persistence

### Project State Hierarchy

Every CLI operation interacts with the database through `StateManager`, which maintains a two-state transaction model:

```mermaid
graph TB
    Project["Project (UUID)"] --> Branch["Branch (main)"]
    Branch --> StateChain["ProjectState Chain"]
    
    StateChain --> Current["current_state (read-only)"]
    StateChain --> Next["next_state (working copy)"]
    
    Current --> Spec["Specification"]
    Current --> KB["KnowledgeBase"]
    Current --> Epics["Epics []"]
    Current --> Tasks["Tasks []"]
    Current --> Steps["Steps []"]
    Current --> Files["Files []"]
    
    Next -.->|"commit()"| NewCurrent["New current_state"]
    NewCurrent -.->|"create_next_state()"| NewNext["New next_state"]
```

**Key Methods:**

- `StateManager.load_project()` - Loads project at specific state
- `StateManager.commit()` - Commits next_state to database
- `StateManager.rollback()` - Abandons next_state changes
- `ProjectState.create_next_state()` - Creates new working state
- `ProjectState.delete_after()` - Removes all states after current

**Sources:** [core/state/state_manager.py:47-93](), [core/db/models/project_state.py:269-315]()

### Workspace File System

The CLI manages a workspace directory where generated code is stored:

```mermaid
graph LR
    Config["config.fs.workspace_root"] --> Root["/workspace"]
    Root --> Proj1["my-project/"]
    Root --> Proj2["another-app/"]
    
    Proj1 --> VFS["LocalDiskVFS"]
    VFS --> IgnoreMatcher["IgnoreMatcher"]
    IgnoreMatcher --> FileOps["save(), read(), list()"]
```

**Workspace Initialization:**
- New projects: Creates unique folder, fails if exists
- Existing projects: Loads files from disk, syncs with database
- Ignored paths: Configured via `config.fs.ignore_paths`

**Sources:** [core/state/state_manager.py:628-678](), [core/disk/vfs.py]()

---

## Error Handling and Exit Codes

### Exit Codes

The CLI uses the following exit codes:

| Code | Meaning |
|------|---------|
| `0` | Success |
| `-1` | Failure (configuration error, runtime error, etc.) |

**Implementation:**
```python
# core/cli/main.py:429-438
def run_pythagora():
    ui, db, args = init()
    if not ui or not db:
        return -1
    success = run(async_main(ui, db, args))
    return 0 if success else -1
```

### Signal Handling

The CLI gracefully handles interruption signals:

- `SIGINT` (Ctrl+C): Rolls back current transaction, sends telemetry, exits
- `SIGTERM`: Same as SIGINT

**Cleanup Process:**
1. Stop orchestrator agent
2. Send telemetry data
3. Roll back uncommitted state
4. Close UI connection
5. Close database session

**Sources:** [core/cli/main.py:51-61](), [core/cli/main.py:391-413]()

---

## Integration with Other Components

### Orchestrator Invocation

After project loading/creation, the CLI delegates to the Orchestrator agent:

```mermaid
sequenceDiagram
    participant CLI as async_main()
    participant SM as StateManager
    participant Orca as Orchestrator
    participant Agents as AI Agents
    
    CLI->>SM: load_project() or create_project()
    SM-->>CLI: ProjectState
    
    CLI->>Orca: Orchestrator(sm, ui, args)
    CLI->>Orca: run()
    
    loop Development Cycle
        Orca->>Agents: Coordinate agents
        Agents->>SM: Modify next_state
        Agents->>SM: commit()
        SM-->>Orca: New current_state
    end
    
    Orca-->>CLI: Success/Failure
    CLI->>CLI: cleanup()
```

**Sources:** [core/cli/main.py:63-105](), [core/cli/main.py:194-321]()

### UI Abstraction

The CLI supports two UI modes:

1. **PlainConsoleUI**: Terminal-based interface
2. **IPCClientUI**: VSCode extension connection

Both implement the `UIBase` interface, allowing agents to work identically regardless of UI.

**UI Selection Logic:**
```python
# Based on config.ui.type or --local-ipc-port argument
if args.local_ipc_port:
    ui = IPCClientUI(host=args.local_ipc_host, port=args.local_ipc_port)
else:
    ui = PlainConsoleUI()
```

**Sources:** [core/cli/helpers.py:443-470](), [core/ui/base.py]()

---

## Telemetry and Analytics

The CLI collects telemetry data during execution:

**Tracked Events:**
- Project creation
- Stack choice (node/swagger)
- Number of steps, tasks, epics
- LLM token usage
- Command executions
- User inputs
- Crashes and errors
- End result (success/failure)

**Opt-out:** See [docs/TELEMETRY.md]() for opt-out instructions.

**Sources:** [core/cli/main.py:356-365](), [core/telemetry/](), [README.md:214-215]()

---

# Page: System Architecture

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [core/agents/architect.py](core/agents/architect.py)
- [core/agents/frontend.py](core/agents/frontend.py)
- [core/agents/orchestrator.py](core/agents/orchestrator.py)
- [core/agents/spec_writer.py](core/agents/spec_writer.py)
- [core/cli/helpers.py](core/cli/helpers.py)
- [core/cli/main.py](core/cli/main.py)
- [core/db/models/project.py](core/db/models/project.py)
- [core/db/models/project_state.py](core/db/models/project_state.py)
- [core/db/v0importer.py](core/db/v0importer.py)
- [core/state/state_manager.py](core/state/state_manager.py)
- [core/ui/api_server.py](core/ui/api_server.py)
- [tests/cli/test_cli.py](tests/cli/test_cli.py)
- [tests/db/test_project.py](tests/db/test_project.py)

</details>



This document describes the high-level architecture of GPT Pilot, detailing the major components and their interactions. It explains how the system is organized to support automated software development through a team of AI agents. For information about specific agents and their implementation details, see [Core Agents](#3).

## Overview

GPT Pilot is built as a multi-agent system that mimics a software development team, with different agents specializing in various aspects of the development process. The architecture follows a modular design with three primary layers:

1. **Agent System** - A team of specialized AI agents that handle different aspects of software development
2. **State Management** - Core mechanisms for managing and persisting project state
3. **Infrastructure Layer** - Support systems including LLM integration, UI abstraction, and file management

```mermaid
flowchart TD
    subgraph "Agent System"
        Orchestrator["Orchestrator"]
        TechLead["Tech Lead"]
        Developer["Developer"]
        CodeMonkey["Code Monkey"] 
        BugHunter["Bug Hunter"]
        Troubleshooter["Troubleshooter"]
        Frontend["Frontend"]
        SpecWriter["Spec Writer"]
        Architect["Architect"]
    end
    
    subgraph "State Management"
        StateManager["StateManager"]
        DB[(Database)]
        VFS["VirtualFileSystem"]
    end
    
    subgraph "Infrastructure"
        UI["UI Layer"]
        LLMClient["LLM Client"]
        ProcessManager["Process Manager"]
        KnowledgeBase["Knowledge Base"]
    end
    
    Users((Users)) <--> UI
    
    Orchestrator --> TechLead
    Orchestrator --> Developer
    Orchestrator --> CodeMonkey
    Orchestrator --> BugHunter
    Orchestrator --> Troubleshooter
    Orchestrator --> Frontend
    Orchestrator --> SpecWriter
    Orchestrator --> Architect
    
    Orchestrator <--> StateManager
    StateManager <--> DB
    StateManager <--> VFS
    
    TechLead <--> LLMClient
    Developer <--> LLMClient
    CodeMonkey <--> LLMClient
    BugHunter <--> LLMClient
    Troubleshooter <--> LLMClient
    Frontend <--> LLMClient
    SpecWriter <--> LLMClient
    Architect <--> LLMClient
    
    TechLead <--> UI
    Developer <--> UI
    CodeMonkey <--> UI
    BugHunter <--> UI
    Troubleshooter <--> UI
    Frontend <--> UI
    SpecWriter <--> UI
    Architect <--> UI
    
    Developer <--> ProcessManager
    Frontend <--> ProcessManager
    
    StateManager <--> KnowledgeBase
```

Sources:
- [core/agents/orchestrator.py]()
- [core/state/state_manager.py]()
- [README.md:177-191]()

## Agent System

The agent system is the core of GPT Pilot, consisting of specialized agents designed to mimic the roles in a software development team. Each agent has a specific responsibility in the development process and interacts with other agents through the Orchestrator.

```mermaid
classDiagram
    class BaseAgent {
        +agent_type: str
        +display_name: str
        +run() AgentResponse
        +get_llm()
        +send_message()
        +ask_question()
    }
    
    class Orchestrator {
        +run() bool
        +create_agent()
        +handle_done()
        +create_agent_for_step()
    }
    
    class TechLead {
        +plan_epic()
        +create_initial_project_epic()
        +ask_for_new_feature()
    }
    
    class Developer {
        +breakdown_current_task()
        +breakdown_current_iteration()
        +set_next_steps()
    }
    
    class CodeMonkey {
        +implement_changes()
        +run_code_review()
        +describe_files()
    }
    
    class BugHunter {
        +check_logs()
        +ask_user_to_test()
        +start_pair_programming()
    }
    
    class Troubleshooter {
        +create_iteration()
        +propose_solution()
        +find_solution()
    }
    
    class Frontend {
        +init_frontend()
        +start_frontend()
        +iterate_frontend()
    }
    
    BaseAgent <|-- Orchestrator
    BaseAgent <|-- TechLead
    BaseAgent <|-- Developer
    BaseAgent <|-- CodeMonkey
    BaseAgent <|-- BugHunter
    BaseAgent <|-- Troubleshooter
    BaseAgent <|-- Frontend
    BaseAgent <|-- SpecWriter
    BaseAgent <|-- Architect
    
    class SpecWriter
    class Architect
    
    Orchestrator --> TechLead : invokes
    Orchestrator --> Developer : invokes
    Orchestrator --> CodeMonkey : invokes
    Orchestrator --> BugHunter : invokes
    Orchestrator --> Troubleshooter : invokes
    Orchestrator --> Frontend : invokes
    Orchestrator --> SpecWriter : invokes
    Orchestrator --> Architect : invokes
```

Sources:
- [core/agents/orchestrator.py:32-410]()
- [core/agents/base.py]()
- [core/agents/tech_lead.py:48-320]()
- [core/agents/developer.py:76-367]()
- [core/agents/bug_hunter.py:46-364]()
- [core/agents/troubleshooter.py:34-396]()
- [core/agents/frontend.py:17-298]()
- [core/agents/code_monkey.py:58-461]()

### Orchestrator

The Orchestrator (`Orchestrator` class) is the central coordinator of all agents. It determines which agent should be executed based on the current project state, manages the sequence of operations, and handles the responses from agents.

Key responsibilities:
- Determining which agent to run next based on the current state
- Creating and invoking agents
- Handling agent responses and updating project state
- Managing the overall workflow of the development process
- Coordinating file operations and user interactions

Sources:
- [core/agents/orchestrator.py:32-410]()

### Agent Roles and Workflow

GPT Pilot implements a development team workflow through specialized agents:

1. **Spec Writer** - Refines project requirements and creates a detailed specification
2. **Architect** - Selects technologies and designs the high-level system architecture
3. **Tech Lead** - Breaks down the project into epics and tasks
4. **Developer** - Creates detailed implementation plans for tasks
5. **Code Monkey** - Implements code changes and files
6. **Bug Hunter** - Identifies and analyzes bugs in the code
7. **Troubleshooter** - Tests implementations and gathers user feedback
8. **Frontend** - Specializes in UI implementation

```mermaid
flowchart LR
    User((User)) --> SpecWriter
    SpecWriter["Spec Writer"] --> Architect
    Architect --> TechLead["Tech Lead"]
    TechLead --> Developer
    Developer --> CodeMonkey["Code Monkey"]
    CodeMonkey --> Troubleshooter
    Troubleshooter -- "Bug Detected" --> BugHunter["Bug Hunter"]
    BugHunter --> Developer
    TechLead -- "UI Tasks" --> Frontend
    Frontend --> CodeMonkey
    Troubleshooter -- "Success" --> NextTask["Next Task"]
```

Sources:
- [README.md:177-191]()
- [core/agents/orchestrator.py:242-329]()

## State Management

The state management system is responsible for maintaining, persisting, and updating the project state throughout the development lifecycle. The `StateManager` class is the central component that orchestrates all state-related operations.

```mermaid
classDiagram
    class StateManager {
        +current_state: ProjectState
        +next_state: ProjectState
        +file_system: VirtualFileSystem
        +commit()
        +create_project()
        +load_project()
        +save_file()
        +get_file_by_path()
        +import_files()
        +restore_files()
    }
    
    class ProjectState {
        +files: List~File~
        +epics: List~dict~
        +tasks: List~dict~
        +steps: List~dict~
        +iterations: List~dict~
        +knowledge_base: dict
        +create_next_state()
        +get_file_by_path()
        +save_file()
    }
    
    class VirtualFileSystem {
        +save()
        +read()
        +remove()
        +list()
        +hash_string()
    }
    
    class LocalDiskVFS {
        +get_full_path()
    }
    
    class MemoryVFS {
    }
    
    class File {
        +path: str
        +content: FileContent
        +meta: dict
    }
    
    class FileContent {
        +content: str
        +hash: str
    }
    
    StateManager o-- ProjectState: manages
    StateManager o-- VirtualFileSystem: uses
    VirtualFileSystem <|-- LocalDiskVFS
    VirtualFileSystem <|-- MemoryVFS
    ProjectState o-- "many" File: contains
    File --> FileContent: references
```

Key components:

1. **StateManager** - Manages loading, updating, and saving project states
2. **ProjectState** - Represents a snapshot of the project at a particular point
3. **VirtualFileSystem** - Abstraction for file operations (implementations: LocalDiskVFS, MemoryVFS)
4. **File/FileContent** - Models representing files and their content

Sources:
- [core/state/state_manager.py:30-759]()

### State Persistence Flow

The state management system uses a dual-state approach with `current_state` and `next_state`:

1. `current_state` - The committed project state loaded from the database
2. `next_state` - A working copy of the state that accumulates changes before committing

When changes are ready to be committed:
1. The `commit()` method is called
2. `next_state` becomes the new `current_state`
3. A new `next_state` is created for future changes

```mermaid
sequenceDiagram
    participant Agent
    participant StateManager
    participant Database
    participant FileSystem
    
    Agent->>StateManager: Make changes to next_state
    Agent->>StateManager: commit()
    StateManager->>Database: Save next_state
    StateManager->>FileSystem: Update files
    StateManager->>StateManager: current_state = next_state
    StateManager->>StateManager: Create new next_state
    StateManager-->>Agent: Return new current_state
```

Sources:
- [core/state/state_manager.py:238-284]()

### Project Structure

The project state includes:

1. **Epics** - High-level features or major components
2. **Tasks** - Specific implementation tasks within epics
3. **Steps** - Detailed implementation steps within tasks
4. **Iterations** - Cycles of implementation, testing, and bug fixing
5. **Files** - Source code and other project files
6. **Knowledge Base** - Accumulated project knowledge (implemented APIs, pages, etc.)

Sources:
- [core/state/state_manager.py:610-736]()

## Infrastructure Layer

### LLM Integration

GPT Pilot integrates with multiple LLM providers including OpenAI, Anthropic, and Groq. The integration is handled through a provider-agnostic interface that allows seamless switching between different LLM providers.

```mermaid
classDiagram
    class LLMClient {
        +get_llm()
        +request()
        +stream()
    }
    
    class OpenAIClient {
        +chat_completion()
        +streaming_chat_completion()
    }
    
    class AnthropicClient {
        +completion()
        +streaming_completion()
    }
    
    class GroqClient {
        +chat_completion()
        +streaming_chat_completion()
    }
    
    class AgentConvo {
        +messages: list
        +user()
        +assistant()
        +system()
        +template()
        +require_schema()
    }
    
    class BaseAgent {
        +get_llm()
        +stream_handler()
    }
    
    LLMClient <|-- OpenAIClient
    LLMClient <|-- AnthropicClient
    LLMClient <|-- GroqClient
    
    BaseAgent --> LLMClient: uses
    BaseAgent --> AgentConvo: creates
```

Sources:
- [core/agents/base.py]()
- [core/llm/providers]()
- [core/agents/convo.py]()

### UI Abstraction

The UI layer provides an abstraction that allows GPT Pilot to interact with users through different interfaces, such as VS Code extension, console, or automated tests.

```mermaid
classDiagram
    class UIBase {
        +send_message()
        +ask_question()
        +send_file_status()
        +generate_diff()
        +send_test_instructions()
        +send_epics_and_tasks()
    }
    
    class ConsoleUI {
        +_print_message()
        +_get_input()
    }
    
    class IPCClientUI {
        +_send_to_server()
        +_receive_from_server()
    }
    
    class VirtualUI {
        +set_responses()
    }
    
    class BaseAgent {
        +ui: UIBase
        +send_message()
        +ask_question()
    }
    
    UIBase <|-- ConsoleUI
    UIBase <|-- IPCClientUI
    UIBase <|-- VirtualUI
    
    BaseAgent --> UIBase: uses
```

Sources:
- [core/ui/base.py]()
- [core/agents/base.py]()

### Process Management

The Process Manager handles execution of shell commands and processes, allowing agents like the Developer and Frontend to interact with the file system, run builds, and execute tests.

```mermaid
classDiagram
    class ProcessManager {
        +run_command()
        +run_background_command()
        +kill_process()
    }
    
    class Executor {
        +process_manager: ProcessManager
        +for_step()
        +execute_command()
    }
    
    class BaseAgent {
        +process_manager: ProcessManager
    }
    
    Executor o-- ProcessManager: contains
    BaseAgent --> ProcessManager: uses
```

Sources:
- [core/proc/process_manager.py]()
- [core/agents/executor.py]()

## Development Workflow

The complete development workflow in GPT Pilot follows these stages:

1. **Project Initialization**
   - User provides app description
   - Spec Writer refines requirements
   - Architect selects technologies

2. **Project Planning**
   - Tech Lead breaks down project into epics and tasks
   - Developer breaks down tasks into implementation steps

3. **Implementation**
   - Code Monkey implements files and changes
   - Frontend builds UI components
   - Developer coordinates implementation steps

4. **Testing and Debugging**
   - Troubleshooter generates testing instructions
   - User tests implementation
   - Bug Hunter identifies and fixes issues

5. **Iteration**
   - Cycle repeats for each task until project is complete
   - New features can be added when initial project is complete

```mermaid
stateDiagram-v2
    [*] --> ProjectDescription
    ProjectDescription --> RequirementRefinement
    RequirementRefinement --> TechnologySelection
    TechnologySelection --> EpicBreakdown
    EpicBreakdown --> TaskBreakdown
    
    TaskBreakdown --> StepImplementation
    StepImplementation --> Testing
    
    Testing --> Feedback
    Feedback --> BugFixed: No issues
    Feedback --> BugHunting: Issues found
    
    BugHunting --> LoggingChanges: Need more logs
    BugHunting --> ImplementSolution: Bug identified
    BugHunting --> PairProgramming: Complex issue
    
    LoggingChanges --> BugHunting
    ImplementSolution --> Testing
    PairProgramming --> Testing
    
    BugFixed --> NextTask: More tasks
    BugFixed --> ProjectComplete: All tasks done
    
    NextTask --> TaskBreakdown
    
    ProjectComplete --> NewFeature: Add feature
    ProjectComplete --> [*]: Done
    
    NewFeature --> RequirementRefinement
```

Sources:
- [core/agents/orchestrator.py:44-116]()
- [README.md:177-191]()

## Conclusion

GPT Pilot's architecture is designed to mimic a human development team, with specialized agents handling different aspects of the development process. The system is built on a robust state management framework that maintains project state throughout the development lifecycle and ensures persistence across sessions.

The modular design allows for flexibility and extensibility, while the agent-based approach enables complex reasoning and problem-solving capabilities. Together, these components create a system capable of generating complete, working applications with minimal human intervention.

Sources:
- [README.md]()
- [core/agents/orchestrator.py]()
- [core/state/state_manager.py]()

---

# Page: Core Components Overview

# Core Components Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [core/agents/architect.py](core/agents/architect.py)
- [core/agents/frontend.py](core/agents/frontend.py)
- [core/agents/orchestrator.py](core/agents/orchestrator.py)
- [core/agents/spec_writer.py](core/agents/spec_writer.py)
- [core/cli/helpers.py](core/cli/helpers.py)
- [core/cli/main.py](core/cli/main.py)
- [core/db/models/project.py](core/db/models/project.py)
- [core/db/models/project_state.py](core/db/models/project_state.py)
- [core/db/v0importer.py](core/db/v0importer.py)
- [core/state/state_manager.py](core/state/state_manager.py)
- [core/ui/api_server.py](core/ui/api_server.py)
- [tests/cli/test_cli.py](tests/cli/test_cli.py)
- [tests/db/test_project.py](tests/db/test_project.py)

</details>



This document provides an overview of GPT Pilot's core architectural components and how they interact to enable AI-driven software development. The system consists of four primary layers: the **StateManager** (state persistence and transaction management), the **Orchestrator** (workflow coordination), the **Agent System** (specialized AI agents), and the **UI Layer** (user interaction interfaces).

For detailed information about specific subsystems:
- State management internals and transaction model: see [State Management System](#3.2)
- Orchestrator workflow coordination: see [Orchestrator and Control Flow](#3.3)  
- UI protocols and VSCode extension: see [UI and Communication Layer](#3.4)
- Individual agent implementations: see [Agent System](#4)

---

## System Entry Point and Initialization

The application starts through `core.cli.main.async_main()`, which initializes the database, UI, and state manager before creating the Orchestrator.

```mermaid
flowchart TB
    main["async_main()<br/>(core/cli/main.py)"]
    init["init()<br/>(core/cli/helpers.py)"]
    args["parse_arguments()"]
    config["load_config()"]
    setup_db["SessionManager"]
    setup_ui["UIBase<br/>(PlainConsoleUI or IPCClientUI)"]
    sm["StateManager<br/>(core/state/state_manager.py)"]
    orca["Orchestrator<br/>(core/agents/orchestrator.py)"]
    
    main --> init
    init --> args
    init --> config
    init --> setup_db
    init --> setup_ui
    
    main --> sm
    sm --> setup_db
    sm --> setup_ui
    
    main --> orca
    orca --> sm
    orca --> setup_ui
    
    orca --> run["orca.run()"]
```

**Sources:** [core/cli/main.py:324-426](), [core/cli/helpers.py:180-330]()

---

## Component Architecture

The system follows a layered architecture where each component has a clear responsibility:

```mermaid
graph TB
    subgraph "Entry Layer"
        CLI["CLI<br/>async_main()"]
        VSCode["VSCode Extension<br/>IPC Connection"]
    end
    
    subgraph "Coordination Layer"
        Orchestrator["Orchestrator<br/>core/agents/orchestrator.py<br/>Agent coordination & workflow"]
    end
    
    subgraph "State Layer"
        SM["StateManager<br/>core/state/state_manager.py<br/>Transaction management"]
        DB[("Database<br/>SQLAlchemy<br/>SQLite/PostgreSQL")]
        VFS["VirtualFileSystem<br/>core/disk/vfs.py<br/>LocalDiskVFS/MemoryVFS"]
    end
    
    subgraph "Agent Layer"
        SpecWriter["SpecWriter<br/>Requirements"]
        Architect["Architect<br/>Tech Stack"]
        TechLead["TechLead<br/>Task Planning"]
        Developer["Developer<br/>Breakdown"]
        CodeMonkey["CodeMonkey<br/>Implementation"]
        Frontend["Frontend<br/>UI Building"]
        Troubleshooter["Troubleshooter<br/>Testing"]
        BugHunter["BugHunter<br/>Debugging"]
    end
    
    subgraph "LLM Layer"
        LLMClients["BaseLLMClient<br/>OpenAI/Anthropic/Groq/Azure"]
    end
    
    subgraph "UI Layer"
        UIBase["UIBase<br/>core/ui/base.py<br/>Abstract interface"]
        PlainUI["PlainConsoleUI<br/>Terminal output"]
        IPCUI["IPCClientUI<br/>VSCode integration"]
    end
    
    CLI --> Orchestrator
    VSCode --> IPCUI
    IPCUI --> Orchestrator
    
    Orchestrator --> SM
    Orchestrator --> UIBase
    
    SM --> DB
    SM --> VFS
    
    Orchestrator -.-> SpecWriter
    Orchestrator -.-> Architect
    Orchestrator -.-> TechLead
    Orchestrator -.-> Developer
    Orchestrator -.-> CodeMonkey
    Orchestrator -.-> Frontend
    Orchestrator -.-> Troubleshooter
    Orchestrator -.-> BugHunter
    
    SpecWriter --> LLMClients
    Architect --> LLMClients
    TechLead --> LLMClients
    Developer --> LLMClients
    CodeMonkey --> LLMClients
    Frontend --> LLMClients
    Troubleshooter --> LLMClients
    BugHunter --> LLMClients
    
    UIBase --> PlainUI
    UIBase --> IPCUI
    
    SpecWriter --> UIBase
    Architect --> UIBase
    TechLead --> UIBase
    Developer --> UIBase
    CodeMonkey --> UIBase
    Frontend --> UIBase
    Troubleshooter --> UIBase
    BugHunter --> UIBase
```

**Sources:** [core/cli/main.py:1-438](), [core/agents/orchestrator.py:1-673](), [core/state/state_manager.py:47-1163]()

---

## StateManager: Project State and Persistence

The `StateManager` class manages the project's state lifecycle, providing transaction semantics for all state changes. It maintains two state references:

| Attribute | Type | Purpose |
|-----------|------|---------|
| `current_state` | `ProjectState` | Read-only committed state |
| `next_state` | `ProjectState` | Writable working copy |
| `project` | `Project` | Current project metadata |
| `branch` | `Branch` | Current branch |
| `file_system` | `VirtualFileSystem` | File I/O abstraction |

**Transaction Model**

```mermaid
stateDiagram-v2
    [*] --> Loaded: load_project()
    Loaded --> Working: create_next_state()
    Working --> Working: Agents modify next_state
    Working --> Committed: commit()
    Committed --> Working: create_next_state()
    Working --> Rolledback: rollback()
    Rolledback --> [*]
    Committed --> [*]: Close session
```

The transaction pattern ensures atomicity:
1. Agents read from `current_state` (immutable)
2. Agents write to `next_state` (mutable)
3. `commit()` makes `next_state` the new `current_state`
4. A new `next_state` is created for further modifications

**Key Methods**

| Method | Purpose | File Reference |
|--------|---------|----------------|
| `load_project()` | Load existing project state | [core/state/state_manager.py:272-415]() |
| `create_project()` | Initialize new project | [core/state/state_manager.py:172-246]() |
| `commit()` | Commit state changes | [core/state/state_manager.py:433-478]() |
| `rollback()` | Abandon uncommitted changes | [core/state/state_manager.py:480-489]() |
| `save_file()` | Save file to state and disk | [core/state/state_manager.py:589-627]() |
| `import_files()` | Import external file changes | [core/state/state_manager.py:703-738]() |

**Sources:** [core/state/state_manager.py:47-1163](), [core/db/models/project_state.py:59-850]()

---

## Orchestrator: Central Control Flow

The `Orchestrator` class (inheriting from `BaseAgent`) coordinates the entire development workflow by selecting and running agents based on the current project state.

```mermaid
flowchart TD
    Start["Orchestrator.run()"] --> Init["Initialize UI & Check Changes"]
    Init --> Loop["Main Loop"]
    
    Loop --> CreateAgent["create_agent(response)"]
    CreateAgent --> IsParallel{Parallel<br/>Agents?}
    
    IsParallel -->|Yes| ParallelRun["asyncio.gather(*tasks)"]
    IsParallel -->|No| SingleRun["await agent.run()"]
    
    ParallelRun --> HandleResponse["handle_parallel_responses()"]
    SingleRun --> CheckType{Response<br/>Type?}
    
    HandleResponse --> CheckType
    
    CheckType -->|EXIT| End["Return True"]
    CheckType -->|DONE| HandleDone["handle_done()"]
    CheckType -->|Other| Loop
    
    HandleDone --> Commit["state_manager.commit()"]
    Commit --> ImportFiles["import_files()"]
    ImportFiles --> Loop
```

**Agent Selection Logic**

The `create_agent()` method examines the current project state to determine which agent should run next:

| State Condition | Agent Selected | File Reference |
|-----------------|----------------|----------------|
| No specification | `SpecWriter` | [core/agents/orchestrator.py:505-507]() |
| No architecture | `Architect` | [core/agents/orchestrator.py:508-510]() |
| No tasks | `TechLead` | [core/agents/orchestrator.py:511-513]() |
| Has unfinished tasks | `Developer` | [core/agents/orchestrator.py:533-535]() |
| Task has steps | `CodeMonkey` | [core/agents/orchestrator.py:536-539]() |
| Has iterations | `Troubleshooter` or `BugHunter` | [core/agents/orchestrator.py:540-547]() |

**Sources:** [core/agents/orchestrator.py:36-673](), [core/agents/base.py:1-468]()

---

## Agent System: Specialized AI Workers

All agents inherit from `BaseAgent`, which provides common functionality for LLM interaction, state access, and user communication.

**BaseAgent Interface**

```mermaid
classDiagram
    class BaseAgent {
        +StateManager state_manager
        +UIBase ui
        +ProcessManager process_manager
        +ProjectState current_state
        +ProjectState next_state
        +agent_type: str
        +display_name: str
        +run() AgentResponse
        +get_llm() BaseLLMClient
        +ask_question() UserInput
        +send_message() None
    }
    
    class SpecWriter {
        +agent_type = "spec-writer"
        +initialize_spec_and_project()
        +change_spec()
        +update_spec()
    }
    
    class Architect {
        +agent_type = "architect"
        +plan_architecture()
        +select_templates()
        +check_system_dependencies()
    }
    
    class TechLead {
        +agent_type = "tech-lead"
        +create_epics()
        +break_down_epic()
        +update_tasks()
    }
    
    class Developer {
        +agent_type = "developer"
        +get_task_breakdown()
        +breakdown_current_iteration()
    }
    
    class CodeMonkey {
        +agent_type = "code-monkey"
        +implement_step()
        +save_files()
    }
    
    class Frontend {
        +agent_type = "frontend"
        +start_frontend()
        +iterate_frontend()
    }
    
    class Troubleshooter {
        +agent_type = "troubleshooter"
        +get_user_feedback()
    }
    
    class BugHunter {
        +agent_type = "bug-hunter"
        +hunt_bug()
        +check_logs()
    }
    
    BaseAgent <|-- SpecWriter
    BaseAgent <|-- Architect
    BaseAgent <|-- TechLead
    BaseAgent <|-- Developer
    BaseAgent <|-- CodeMonkey
    BaseAgent <|-- Frontend
    BaseAgent <|-- Troubleshooter
    BaseAgent <|-- BugHunter
```

**Agent Responsibilities**

| Agent | Primary Function | State Modifications | File Reference |
|-------|------------------|---------------------|----------------|
| `SpecWriter` | Capture user requirements | `specification.description` | [core/agents/spec_writer.py:19-357]() |
| `Architect` | Select tech stack | `specification.architecture`, `system_dependencies` | [core/agents/architect.py:95-295]() |
| `TechLead` | Create epics and tasks | `epics[]`, `tasks[]` | [core/agents/tech_lead.py]() |
| `Developer` | Break tasks into steps | `steps[]` | [core/agents/developer.py]() |
| `CodeMonkey` | Generate code | `files[]`, file content | [core/agents/code_monkey.py]() |
| `Frontend` | Build UI | Frontend-specific files | [core/agents/frontend.py:40-603]() |
| `Troubleshooter` | Collect user feedback | `iterations[]` | [core/agents/troubleshooter.py]() |
| `BugHunter` | Debug issues | Log analysis, fix implementation | [core/agents/bug_hunter.py]() |

**Sources:** [core/agents/base.py:42-468](), [core/agents/spec_writer.py:19-357](), [core/agents/architect.py:95-295](), [core/agents/frontend.py:40-603]()

---

## UI Layer: User Interaction Abstraction

The UI system uses the `UIBase` abstract class to support multiple interfaces without changing agent code.

**UI Architecture**

```mermaid
classDiagram
    class UIBase {
        <<abstract>>
        +start() bool
        +stop() None
        +send_message(content, source) None
        +ask_question(question, buttons) UserInput
        +send_project_stage(data) None
        +send_file_status(path, status) None
        +generate_diff(path, old, new) None
        +open_editor(path) None
    }
    
    class PlainConsoleUI {
        +start() bool
        +send_message() None
        +ask_question() UserInput
    }
    
    class IPCClientUI {
        -IPCClient client
        -host: str
        -port: int
        +start() bool
        +send_message() None
        +ask_question() UserInput
        +_send_ipc_message() None
        +_receive_ipc_response() dict
    }
    
    class VirtualUI {
        -inputs: list
        +ask_question() UserInput
    }
    
    UIBase <|-- PlainConsoleUI
    UIBase <|-- IPCClientUI
    UIBase <|-- VirtualUI
```

**UI Implementations**

| Class | Use Case | Communication | File Reference |
|-------|----------|---------------|----------------|
| `PlainConsoleUI` | CLI usage | Direct terminal I/O | [core/ui/console.py]() |
| `IPCClientUI` | VSCode extension | TCP socket (localhost:8125) | [core/ui/ipc_client.py]() |
| `VirtualUI` | Testing | Predefined input queue | [core/ui/virtual.py]() |

**Message Flow for IPCClientUI**

```mermaid
sequenceDiagram
    participant Agent
    participant IPCClientUI
    participant Socket
    participant VSCode
    
    Agent->>IPCClientUI: ask_question(text, buttons)
    IPCClientUI->>Socket: Length (4 bytes) + JSON message
    Socket->>VSCode: Forward message
    VSCode->>VSCode: Display to user
    VSCode->>Socket: User response
    Socket->>IPCClientUI: Response data
    IPCClientUI->>Agent: UserInput object
```

The IPC protocol uses length-prefixed JSON messages. Each message contains:
- `type`: Message type enum (`MessageType.USER_INPUT_REQUEST`, etc.)
- `content`: Message payload (dict)
- `request_id`: Optional UUID for request/response matching

**Sources:** [core/ui/base.py:44-1085](), [core/ui/console.py](), [core/ui/ipc_client.py:30-485]()

---

## File System and Database Integration

**Virtual File System**

The `VirtualFileSystem` interface abstracts file operations, enabling both production (disk) and testing (memory) scenarios:

```mermaid
classDiagram
    class VirtualFileSystem {
        <<abstract>>
        +root: str
        +save(path, content) None
        +read(path) str
        +remove(path) None
        +list() list[str]
        +hash_string(content) str
    }
    
    class LocalDiskVFS {
        -ignore_matcher: IgnoreMatcher
        +save(path, content) None
        +read(path) str
    }
    
    class MemoryVFS {
        -files: dict
        +save(path, content) None
        +read(path) str
    }
    
    VirtualFileSystem <|-- LocalDiskVFS
    VirtualFileSystem <|-- MemoryVFS
```

**Database Models**

The database schema centers around `ProjectState`, which contains snapshots of the project at each step:

| Model | Purpose | Key Fields | File Reference |
|-------|---------|------------|----------------|
| `Project` | Project metadata | `id`, `name`, `folder_name` | [core/db/models/project.py:18-178]() |
| `Branch` | Version branches | `id`, `name`, `project_id` | [core/db/models/branch.py]() |
| `ProjectState` | State snapshot | `step_index`, `epics`, `tasks`, `files` | [core/db/models/project_state.py:59-850]() |
| `File` | File reference | `path`, `project_state_id`, `content_id` | [core/db/models/file.py]() |
| `FileContent` | Deduplicated content | `id`, `content`, `hash` | [core/db/models/file_content.py]() |
| `Specification` | Project spec | `description`, `architecture` | [core/db/models/specification.py]() |

**Content Deduplication**

Files are content-addressable using SHA-256 hashes. Multiple `File` records can reference the same `FileContent` record, minimizing storage:

```mermaid
graph LR
    State1["ProjectState<br/>step_index=1"]
    State2["ProjectState<br/>step_index=2"]
    File1A["File<br/>path=app.js"]
    File1B["File<br/>path=config.js"]
    File2A["File<br/>path=app.js"]
    File2B["File<br/>path=config.js"]
    Content1["FileContent<br/>hash=abc123<br/>content='...'"]
    Content2["FileContent<br/>hash=def456<br/>content='...'"]
    
    State1 --> File1A
    State1 --> File1B
    State2 --> File2A
    State2 --> File2B
    
    File1A --> Content1
    File2A --> Content1
    File1B --> Content2
    File2B --> Content2
```

**Sources:** [core/disk/vfs.py](), [core/db/models/project.py:18-178](), [core/db/models/project_state.py:59-850](), [core/db/models/file_content.py]()

---

## Execution Flow Summary

A typical development session follows this sequence:

1. **Initialization**: `async_main()` loads configuration, creates `SessionManager`, initializes UI
2. **Project Setup**: `StateManager.create_project()` or `StateManager.load_project()`
3. **Orchestration**: `Orchestrator.run()` enters main loop
4. **Agent Execution**: Orchestrator selects and runs agents based on state
5. **State Commit**: After each agent completes, `StateManager.commit()` persists changes
6. **Iteration**: Loop continues until all work complete or user exits

Each agent run follows this pattern:
1. Agent reads `current_state` (immutable)
2. Agent modifies `next_state` (mutable)
3. Agent calls LLM via `get_llm()` and `AgentConvo`
4. Agent updates files via `state_manager.save_file()`
5. Agent returns `AgentResponse` (DONE, EXIT, etc.)
6. Orchestrator handles response and commits state

**Sources:** [core/cli/main.py:194-321](), [core/agents/orchestrator.py:48-167](), [core/state/state_manager.py:433-478]()

---

# Page: State Management System

# State Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [core/cli/helpers.py](core/cli/helpers.py)
- [core/cli/main.py](core/cli/main.py)
- [core/db/models/project.py](core/db/models/project.py)
- [core/db/models/project_state.py](core/db/models/project_state.py)
- [core/db/v0importer.py](core/db/v0importer.py)
- [core/state/state_manager.py](core/state/state_manager.py)
- [core/ui/api_server.py](core/ui/api_server.py)
- [tests/cli/test_cli.py](tests/cli/test_cli.py)
- [tests/db/test_project.py](tests/db/test_project.py)

</details>



The State Management system in GPT Pilot is responsible for tracking, persisting, and synchronizing the state of development projects throughout their lifecycle. This documentation explains how GPT Pilot manages project state, including the project structure, state transitions, file management, and the knowledge base.

For information about the agent system that uses this state management, see [Agent System](#2.1).

## Overview

The state management architecture uses a dual-state approach where the current state is considered immutable (read-only), while a next state is used to accumulate changes. When changes are committed, the next state becomes the current state, and a new next state is created for future modifications. This approach ensures that the system always has a consistent view of the project at any point in time.

```mermaid
flowchart TD
    subgraph "State Management Architecture"
        StateManager["StateManager"] --> CurrentState["current_state (read-only)"]
        StateManager --> NextState["next_state (writable)"]
        StateManager --> FileSystem["file_system"]
        
        CurrentState --> ProjectStructure["Project Structure"]
        ProjectStructure --> Epics["epics"]
        ProjectStructure --> Tasks["tasks"]
        ProjectStructure --> Steps["steps"]
        ProjectStructure --> Iterations["iterations"]
        
        CurrentState --> Files["files"]
        CurrentState --> Specification["specification"]
        CurrentState --> KnowledgeBase["knowledge_base"]
        
        StateManager --> Database[(SQLite/PostgreSQL)]
        StateManager --> VFS["Virtual File System"]
        
        VFS --> LocalDiskVFS["LocalDiskVFS"]
        VFS --> MemoryVFS["MemoryVFS"]
    end
    
    Agent["BaseAgent"] --> StateManager
```

Sources: [core/state/state_manager.py:30-108](core/state/state_manager.py:30-108), [core/db/models/project_state.py:49-102](core/db/models/project_state.py:49-102)

## State Manager

The `StateManager` class is the core of the state management system. It provides methods for:

1. Creating and loading projects
2. Managing state transitions
3. Persisting state to the database
4. Synchronizing files between the database and file system
5. Tracking LLM requests, user inputs, and command executions

The state manager maintains two key state objects:
- `current_state`: The immutable, current state of the project (read-only)
- `next_state`: The mutable state where changes are made (writable)

```mermaid
sequenceDiagram
    participant Agent
    participant StateManager
    participant Database
    participant VFS as "Virtual File System"
    
    Agent->>StateManager: Read from current_state
    Agent->>StateManager: Modify next_state
    Agent->>StateManager: commit()
    StateManager->>Database: Save next_state to database
    StateManager->>StateManager: current_state = next_state
    StateManager->>StateManager: Create new next_state
    StateManager->>VFS: Synchronize files
```

Sources: [core/state/state_manager.py:239-269](core/state/state_manager.py:239-269), [core/agents/orchestrator.py:199-225](core/agents/orchestrator.py:199-225)

## Project State Structure

The `ProjectState` model represents the state of a project at a specific point in time. It contains the following key components:

### Epics

Epics represent high-level features or project components. Each epic is a dictionary containing:
- `id`: Unique identifier
- `name`: Epic name
- `description`: Epic description
- `completed`: Boolean indicating completion status
- `source`: Origin of the epic (e.g., "frontend", "feature")

### Tasks

Tasks represent specific work items within an epic. Each task contains:
- `description`: Task description
- `status`: Current status (todo, in_progress, reviewed, documented, done, skipped)
- `instructions`: Detailed implementation instructions
- `related_api_endpoints`: References to related API endpoints

### Steps

Steps are atomic units of work created by the Developer agent. Each step has:
- `type`: Step type (save_file, command, human_intervention, etc.)
- Action-specific data (e.g., file path and content for save_file)
- `completed`: Boolean indicating completion status

### Iterations

Iterations track troubleshooting or problem-solving cycles. Each iteration includes:
- `description`: Issue description
- `user_feedback`: Feedback from the user
- `status`: Current status of the iteration

```mermaid
flowchart TD
    subgraph "ProjectState Structure"
        ProjectState --> Epics["epics: List[dict]"]
        ProjectState --> Tasks["tasks: List[dict]"]
        ProjectState --> Steps["steps: List[dict]"]
        ProjectState --> Iterations["iterations: List[dict]"]
        ProjectState --> Files["files: List[File]"]
        ProjectState --> KnowledgeBase["knowledge_base: dict"]
        ProjectState --> Specification["specification: Specification"]
        
        Epics --> CurrentEpic["current_epic"]
        Tasks --> CurrentTask["current_task"]
        Steps --> CurrentStep["current_step"]
        Iterations --> CurrentIteration["current_iteration"]
    end
    
    subgraph "Helper Methods"
        ProjectState --> GetFileByPath["get_file_by_path()"]
        ProjectState --> SaveFile["save_file()"]
        ProjectState --> CompleteStep["complete_step()"]
        ProjectState --> CompleteTask["complete_task()"]
        ProjectState --> CompleteEpic["complete_epic()"]
        ProjectState --> CompleteIteration["complete_iteration()"]
    end
```

Sources: [core/db/models/project_state.py:97-179](core/db/models/project_state.py:97-179), [core/db/models/project_state.py:287-352](core/db/models/project_state.py:287-352)

## File Management

GPT Pilot uses a virtual file system (VFS) abstraction to manage files, with implementations for local disk storage (`LocalDiskVFS`) and in-memory storage (`MemoryVFS`). The state manager provides methods for:

1. Saving files to both the database and file system
2. Importing files from the file system into the database
3. Restoring files from the database to the file system
4. Tracking modified files

```mermaid
flowchart TD
    subgraph "File Management System"
        StateManager["StateManager"] --> SaveFile["save_file()"]
        StateManager --> ImportFiles["import_files()"]
        StateManager --> RestoreFiles["restore_files()"]
        StateManager --> GetModifiedFiles["get_modified_files()"]
        
        SaveFile --> VFS["VirtualFileSystem"]
        ImportFiles --> VFS
        RestoreFiles --> VFS
        GetModifiedFiles --> VFS
        
        VFS --> LocalDiskVFS["LocalDiskVFS (real files)"]
        VFS --> MemoryVFS["MemoryVFS (testing)"]
        
        SaveFile --> Database[(Database)]
        ImportFiles --> Database
    end
    
    subgraph "File Operations"
        File["File"] --> Path["path: str"]
        File --> Content["content: FileContent"]
        File --> Meta["meta: dict"]
        
        FileContent["FileContent"] --> Hash["hash: str"]
        FileContent --> Content["content: str"]
    end
```

Sources: [core/state/state_manager.py:386-435](core/state/state_manager.py:386-435), [core/state/state_manager.py:476-532](core/state/state_manager.py:476-532)

## Knowledge Base

The knowledge base is a dictionary in the `ProjectState` that stores contextual information about the project. It includes:

1. Implemented pages and their locations
2. API endpoints and their implementation status
3. User options and preferences
4. Utility functions and their status

The knowledge base helps agents understand the current state of implementation and make informed decisions.

```mermaid
flowchart TD
    subgraph "Knowledge Base Structure"
        KnowledgeBase["knowledge_base"] --> Pages["pages: List[str]"]
        KnowledgeBase --> APIs["apis: List[dict]"]
        KnowledgeBase --> UserOptions["user_options: dict"]
        KnowledgeBase --> UtilityFunctions["utility_functions: List[dict]"]
        
        Pages --> ImplementedPages["Implemented UI pages"]
        
        APIs --> APIEndpoint["API endpoint metadata"]
        APIEndpoint --> Description["description: str"]
        APIEndpoint --> Endpoint["endpoint: str"]
        APIEndpoint --> Request["request: str"]
        APIEndpoint --> Response["response: str"]
        APIEndpoint --> Locations["locations: dict"]
        APIEndpoint --> Status["status: str"]
    end
    
    subgraph "Knowledge Base Operations"
        StateManager["StateManager"] --> UpdateImplementedPages["update_implemented_pages_and_apis()"]
        StateManager --> UpdateAPIs["update_apis()"]
        StateManager --> UpdateUtilityFunctions["update_utility_functions()"]
    end
```

Sources: [core/state/state_manager.py:620-664](core/state/state_manager.py:620-664), [core/agents/frontend.py:144-146](core/agents/frontend.py:144-146)

## State Transitions

State transitions happen when agents commit their changes to the database. The process involves:

1. Saving the next state to the database
2. Setting the current state to the next state
3. Creating a new next state for future modifications
4. Preloading file contents to ensure they're available

```mermaid
flowchart TD
    subgraph "State Transition Process"
        Orchestrator["Orchestrator"] --> HandleDone["handle_done()"]
        HandleDone --> Commit["state_manager.commit()"]
        
        Commit --> SaveNextState["Save next_state to database"]
        SaveNextState --> CurrentToNext["current_state = next_state"]
        CurrentToNext --> CreateNewNext["Create new next_state"]
        CreateNewNext --> PreloadFiles["Preload file contents"]
        
        HandleDone --> ImportFiles["import_files()"]
        HandleDone --> DescribeFiles["describe_files()"]
    end
    
    subgraph "Automatic State Updates"
        Agent["Agent"] --> ModifyNextState["Modify next_state"]
        Agent --> FlagModified["Flag modified collections"]
        
        FlagModified --> FlagEpics["flag_epics_as_modified()"]
        FlagModified --> FlagTasks["flag_tasks_as_modified()"]
        FlagModified --> FlagIterations["flag_iterations_as_modified()"]
        FlagModified --> FlagKnowledgeBase["flag_knowledge_base_as_modified()"]
    end
```

Sources: [core/state/state_manager.py:239-276](core/state/state_manager.py:239-276), [core/agents/orchestrator.py:199-239](core/agents/orchestrator.py:199-239)

## Agent Interaction with State Management

Agents interact with the state management system through their access to the `StateManager` instance. They:

1. Read from `current_state` to understand the project context
2. Modify `next_state` to make changes
3. Use helper methods like `save_file()` to update files
4. Call `commit()` (via the Orchestrator) to persist changes

```mermaid
flowchart TD
    subgraph "Agent-State Interaction"
        Agent["BaseAgent"] --> CurrentState["agent.current_state (read-only)"]
        Agent --> NextState["agent.next_state (writable)"]
        Agent --> StateManager["agent.state_manager"]
        
        CurrentState --> ReadEpics["Read epics, tasks, steps"]
        CurrentState --> ReadFiles["Read file contents"]
        CurrentState --> ReadKnowledgeBase["Read knowledge base"]
        
        NextState --> ModifyEpics["Modify epics, tasks, steps"]
        NextState --> FlagAsModified["Flag as modified"]
        NextState --> CompleteItems["Complete steps/tasks/epics"]
        
        StateManager --> SaveFile["save_file()"]
        StateManager --> CommitChanges["commit()"]
    end
```

Sources: [core/agents/orchestrator.py:199-225](core/agents/orchestrator.py:199-225), [core/agents/code_monkey.py:207-225](core/agents/code_monkey.py:207-225)

## Persistence 

Project state is stored in a SQLite or PostgreSQL database using SQLAlchemy. The state includes:

1. Project metadata
2. Branch information
3. State history (steps)
4. File contents (with content-addressable storage)
5. LLM requests and responses
6. User inputs
7. Command execution logs

```mermaid
flowchart TD
    subgraph "Database Models"
        ProjectState["ProjectState"] --> Project["Project"]
        ProjectState --> Branch["Branch"]
        ProjectState --> PrevState["prev_state: ProjectState"]
        ProjectState --> NextState["next_state: ProjectState"]
        ProjectState --> Files["files: List[File]"]
        ProjectState --> Specification["specification: Specification"]
        ProjectState --> LLMRequests["llm_requests: List[LLMRequest]"]
        ProjectState --> UserInputs["user_inputs: List[UserInput]"]
        ProjectState --> ExecLogs["exec_logs: List[ExecLog]"]
        
        Files --> FileContent["FileContent"]
    end
```

Sources: [core/db/models/project_state.py:49-96](core/db/models/project_state.py:49-96), [core/state/state_manager.py:307-348](core/state/state_manager.py:307-348)

## Offline Changes Management

The state manager provides mechanisms to handle changes made outside of GPT Pilot, including:

1. Detecting modified files in the workspace
2. Importing external changes into the project state
3. Restoring files from the database to the workspace

This allows users to make changes to files directly and have GPT Pilot recognize and incorporate those changes.

```mermaid
flowchart TD
    subgraph "Offline Changes Handling"
        Orchestrator["Orchestrator"] --> OfflineChangesCheck["offline_changes_check()"]
        OfflineChangesCheck --> GetModifiedFiles["get_modified_files_with_content()"]
        GetModifiedFiles --> UserChoice["Ask user what to do"]
        
        UserChoice --> |"Keep changes"| ImportFiles["import_files()"]
        UserChoice --> |"Discard changes"| RestoreFiles["restore_files()"]
    end
```

Sources: [core/agents/orchestrator.py:157-198](core/agents/orchestrator.py:157-198), [core/state/state_manager.py:536-608](core/state/state_manager.py:536-608)

## Conclusion

The state management system in GPT Pilot provides a robust foundation for tracking project development, managing files, and maintaining a consistent view of the project state. The dual-state approach with current (read-only) and next (writable) states ensures that changes are applied atomically, while the virtual file system abstraction allows for flexible file management across different environments.

---

# Page: Orchestrator and Control Flow

# Orchestrator and Control Flow

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [core/agents/architect.py](core/agents/architect.py)
- [core/agents/frontend.py](core/agents/frontend.py)
- [core/agents/orchestrator.py](core/agents/orchestrator.py)
- [core/agents/spec_writer.py](core/agents/spec_writer.py)
- [core/cli/helpers.py](core/cli/helpers.py)
- [core/cli/main.py](core/cli/main.py)
- [core/db/models/project.py](core/db/models/project.py)
- [core/db/models/project_state.py](core/db/models/project_state.py)
- [core/db/v0importer.py](core/db/v0importer.py)
- [core/state/state_manager.py](core/state/state_manager.py)
- [core/ui/api_server.py](core/ui/api_server.py)
- [tests/cli/test_cli.py](tests/cli/test_cli.py)
- [tests/db/test_project.py](tests/db/test_project.py)

</details>



The Orchestrator is the central control system in GPT Pilot that coordinates all specialized AI agents and manages the development workflow. It implements a state machine that determines which agent should execute at each step based on the current project state, handles agent responses, and manages state persistence through commits to the database.

For information about the individual agents that the Orchestrator coordinates, see [Agent System](#4). For details about state persistence and transactions, see [State Management System](#3.2).

---

## Orchestrator Architecture

The `Orchestrator` class in [core/agents/orchestrator.py:36-167]() serves as both an agent itself and a coordinator for other agents. It inherits from `BaseAgent` and `GitMixin`, giving it both agent capabilities and Git integration.

### Class Structure

```mermaid
graph TB
    subgraph "Orchestrator Class"
        Orchestrator["Orchestrator<br/>(BaseAgent + GitMixin)"]
        Orchestrator --> run["run()<br/>Main Control Loop"]
        Orchestrator --> create_agent["create_agent()<br/>Agent Factory"]
        Orchestrator --> handle_done["handle_done()<br/>Response Handler"]
        Orchestrator --> handle_parallel["handle_parallel_responses()<br/>Parallel Handler"]
    end
    
    subgraph "Core Dependencies"
        StateManager["StateManager<br/>current_state, next_state"]
        UIBase["UIBase<br/>User Interface"]
        Executor["Executor<br/>process_manager"]
        ProcessManager["ProcessManager<br/>Command Execution"]
    end
    
    subgraph "Coordinated Agents"
        SpecWriter["SpecWriter<br/>Requirements"]
        Architect["Architect<br/>Tech Stack"]
        TechLead["TechLead<br/>Epic Planning"]
        Developer["Developer<br/>Task Breakdown"]
        CodeMonkey["CodeMonkey<br/>Implementation"]
        Frontend["Frontend<br/>UI Building"]
        Troubleshooter["Troubleshooter<br/>Testing"]
        BugHunter["BugHunter<br/>Debugging"]
    end
    
    run --> create_agent
    create_agent --> SpecWriter
    create_agent --> Architect
    create_agent --> TechLead
    create_agent --> Developer
    create_agent --> CodeMonkey
    create_agent --> Frontend
    create_agent --> Troubleshooter
    create_agent --> BugHunter
    
    Orchestrator -.->|uses| StateManager
    Orchestrator -.->|uses| UIBase
    Orchestrator -.->|uses| Executor
    Executor -.->|manages| ProcessManager
```

**Sources:** [core/agents/orchestrator.py:36-62](), [core/agents/base.py:1-50]()

---

## Main Control Loop

The `Orchestrator.run()` method implements the core control flow as an infinite loop that continues until an agent requests an exit.

### Control Flow State Machine

```mermaid
stateDiagram-v2
    [*] --> Initialize
    
    Initialize --> CheckRedoTask: Check redo_human_instructions
    
    CheckRedoTask --> UpdateStats: No redo needed
    CheckRedoTask --> ReloadProject: Redo requested
    ReloadProject --> UpdateStats
    
    UpdateStats --> CreateAgent: Get agent for current state
    
    CreateAgent --> IsList{Agent is list?}
    
    IsList --> RunParallel: Yes - Multiple agents
    IsList --> RunSingle: No - Single agent
    
    RunParallel --> GatherResponses: asyncio.gather()
    GatherResponses --> HandleParallel: handle_parallel_responses()
    
    RunSingle --> RunAgent: agent.run()
    RunAgent --> CheckUserInterrupt{UserInterruptError?}
    CheckUserInterrupt --> ForceExit: Yes
    CheckUserInterrupt --> HandleResponse: No
    
    HandleParallel --> CheckType
    ForceExit --> CheckType
    HandleResponse --> CheckType
    
    CheckType --> ResponseType{response.type?}
    
    ResponseType --> Exit: EXIT
    ResponseType --> HandleDone: DONE
    ResponseType --> UpdateStats: Other types
    
    HandleDone --> Commit: handle_done()
    Commit --> UpdateStats
    
    Exit --> [*]
    
    note right of CreateAgent
        create_agent() uses
        current_state to determine
        which agent to run next
    end note
    
    note right of HandleDone
        Commits next_state to DB,
        imports files, describes files,
        creates new next_state
    end note
```

**Sources:** [core/agents/orchestrator.py:48-167](), [core/cli/main.py:63-105]()

### Loop Implementation Details

The main loop at [core/agents/orchestrator.py:87-167]() performs these key operations:

1. **Check for task redo**: Lines 89-104 handle cases where a task needs to be restarted with new instructions
2. **Update statistics**: Line 105 updates telemetry metrics
3. **Create agent(s)**: Line 106 determines which agent(s) to run based on current state
4. **Handle parallel execution**: Lines 109-140 process multiple agents running concurrently
5. **Handle single execution**: Lines 142-148 run a single agent
6. **Process response**: Lines 149-164 handle different response types

**Sources:** [core/agents/orchestrator.py:87-167]()

---

## Agent Creation and Selection

The `create_agent()` method acts as a factory that instantiates the appropriate agent based on the current project state. This method is not shown in the provided files but is referenced and its behavior can be inferred.

### Agent Selection Logic

```mermaid
flowchart TD
    Start["create_agent(response)"] --> CheckResponse{Previous<br/>response<br/>exists?}
    
    CheckResponse -->|No| CheckState[Check current_state]
    CheckResponse -->|Yes| CheckResponseType{response.type?}
    
    CheckResponseType -->|UPDATE_SPEC| SpecWriter[Return SpecWriter]
    CheckResponseType -->|ADD_TASK| TechLead[Return TechLead]
    CheckResponseType -->|Other| CheckState
    
    CheckState --> HasSpec{Has<br/>specification?}
    HasSpec -->|No| SpecWriter
    HasSpec -->|Yes| HasEpics{Has<br/>epics?}
    
    HasEpics -->|No| Architect[Return Architect]
    HasEpics -->|Yes| HasTasks{Has<br/>tasks?}
    
    HasTasks -->|No| TechLead
    HasTasks -->|Yes| CheckTaskStatus{Current task<br/>status?}
    
    CheckTaskStatus -->|TODO| Developer[Return Developer]
    CheckTaskStatus -->|IN_PROGRESS| CheckSteps{Has<br/>steps?}
    
    CheckSteps -->|No| Developer
    CheckSteps -->|Yes| CheckIterations{Has<br/>iterations?}
    
    CheckIterations -->|Yes| CheckIterStatus{Iteration<br/>status?}
    CheckIterStatus -->|HUNTING_FOR_BUG| BugHunter[Return BugHunter]
    CheckIterStatus -->|Other| Troubleshooter[Return Troubleshooter]
    
    CheckIterations -->|No| CheckCompleted{All steps<br/>completed?}
    CheckCompleted -->|No| CheckStepType{Step type?}
    CheckCompleted -->|Yes| TaskCompleter[Return TaskCompleter]
    
    CheckStepType -->|command| Executor[Return Executor]
    CheckStepType -->|save_file| CheckParallel{Multiple<br/>files?}
    CheckStepType -->|human_intervention| HumanInput[Return HumanInput]
    
    CheckParallel -->|Yes| CodeMonkeyList[Return list of<br/>CodeMonkey agents]
    CheckParallel -->|No| CodeMonkey[Return CodeMonkey]
```

**Sources:** Based on agent workflow patterns from [core/agents/orchestrator.py:106](), [core/db/models/project_state.py:32-57](), [core/agents/response.py:1-30]()

---

## Response Type System

Agents return `AgentResponse` objects that signal to the Orchestrator what action to take next. The response type determines the control flow.

### Response Type Enumeration

| Response Type | Purpose | Handling |
|--------------|---------|----------|
| `ResponseType.DONE` | Agent completed successfully | Commit state, continue to next agent |
| `ResponseType.EXIT` | Stop execution | Exit main loop |
| `ResponseType.INPUT_REQUIRED` | User input needed | Route to HumanInput agent |
| `ResponseType.UPDATE_SPECIFICATION` | Spec needs updating | Route to SpecWriter |
| `ResponseType.DESCRIBE_FILES` | Files need descriptions | Describe files before continuing |
| `ResponseType.IMPORT_PROJECT` | Import external changes | Run Importer agent |

### Response Handling Flow

```mermaid
sequenceDiagram
    participant Agent
    participant Orchestrator
    participant StateManager
    participant DB
    participant NextAgent
    
    Agent->>Orchestrator: return AgentResponse(type=DONE)
    
    Orchestrator->>Orchestrator: handle_done(agent, response)
    
    Orchestrator->>StateManager: commit()
    StateManager->>DB: Persist next_state
    StateManager->>StateManager: next_state becomes current_state
    StateManager->>StateManager: Create new next_state
    StateManager-->>Orchestrator: committed state
    
    Orchestrator->>Orchestrator: import_files()
    Note over Orchestrator: Check for offline changes
    
    Orchestrator->>Orchestrator: describe_files()
    Note over Orchestrator: Add metadata to new files
    
    Orchestrator->>Orchestrator: update_stats()
    
    Orchestrator->>Orchestrator: create_agent(response)
    Orchestrator->>NextAgent: Create next agent instance
    
    Orchestrator->>NextAgent: run()
    NextAgent-->>Orchestrator: AgentResponse
```

**Sources:** [core/agents/orchestrator.py:418-479](), [core/state/state_manager.py:433-479](), [core/agents/response.py:1-30]()

---

## State Commitment Process

When an agent completes with `ResponseType.DONE`, the `handle_done()` method manages the transaction commit and prepares for the next step.

### Commit Transaction Flow

```mermaid
graph LR
    subgraph "Before Commit"
        CurrentState["current_state<br/>(read-only)"]
        NextState["next_state<br/>(writable)"]
    end
    
    subgraph "Commit Process"
        HandleDone["handle_done()"]
        Commit["state_manager.commit()"]
        ImportFiles["import_files()"]
        DescribeFiles["describe_files()"]
    end
    
    subgraph "After Commit"
        NewCurrent["new current_state<br/>(former next_state)"]
        NewNext["new next_state<br/>(fresh copy)"]
    end
    
    NextState -->|modified by agent| HandleDone
    HandleDone --> Commit
    Commit -->|persist to DB| NewCurrent
    Commit -->|clone state| NewNext
    HandleDone --> ImportFiles
    HandleDone --> DescribeFiles
    
    CurrentState -.->|unchanged| NewCurrent
```

**Key Operations in `handle_done()`:**

1. **Log progress** [core/agents/orchestrator.py:427-444](): Count finished epics, tasks, iterations, and steps
2. **Commit to database** [core/agents/orchestrator.py:446](): Call `state_manager.commit()`
3. **Import external files** [core/agents/orchestrator.py:451](): Detect and import files changed outside GPT Pilot
4. **Describe new files** [core/agents/orchestrator.py:454-462](): Add metadata to files missing descriptions
5. **Update knowledge base** [core/agents/orchestrator.py:465-474](): Update pages and APIs if needed

**Sources:** [core/agents/orchestrator.py:418-479](), [core/state/state_manager.py:433-479]()

---

## Parallel Agent Execution

The Orchestrator supports running multiple instances of the same agent type in parallel, currently only implemented for `CodeMonkey` agents when multiple files need to be saved.

### Parallel Execution Architecture

```mermaid
sequenceDiagram
    participant Orchestrator
    participant CM1 as CodeMonkey 1
    participant CM2 as CodeMonkey 2
    participant CM3 as CodeMonkey 3
    participant Gather as asyncio.gather()
    
    Orchestrator->>Orchestrator: create_agent() returns [CM1, CM2, CM3]
    
    Orchestrator->>Gather: Start all agents concurrently
    
    par Parallel Execution
        Gather->>CM1: run()
        CM1->>CM1: Process file 1
        CM1-->>Gather: AgentResponse
    and
        Gather->>CM2: run()
        CM2->>CM2: Process file 2
        CM2-->>Gather: AgentResponse
    and
        Gather->>CM3: run()
        CM3->>CM3: Process file 3
        CM3-->>Gather: AgentResponse
    end
    
    Gather-->>Orchestrator: [response1, response2, response3]
    
    Orchestrator->>Orchestrator: handle_parallel_responses(agent, responses)
    
    Note over Orchestrator: Combine responses:<br/>Check for INPUT_REQUIRED,<br/>aggregate results
    
    Orchestrator-->>Orchestrator: Single combined AgentResponse
```

### Implementation Details

The parallel execution logic at [core/agents/orchestrator.py:109-140]():

1. **Detection**: Check if `create_agent()` returns a list
2. **Execution**: Use `asyncio.gather(*tasks)` to run agents concurrently
3. **Combination**: Call `handle_parallel_responses()` to merge results
4. **Knowledge base update**: Check if any agent modified pages or APIs

The `handle_parallel_responses()` method at [core/agents/orchestrator.py:345-368]() handles merging:

- For `CodeMonkey` agents: Aggregates files that require user input
- Returns a single `AgentResponse` representing the combined result
- Raises error for unsupported parallel agent types

**Sources:** [core/agents/orchestrator.py:109-140](), [core/agents/orchestrator.py:345-368]()

---

## Initialization and Setup

Before entering the main control loop, the Orchestrator performs several initialization tasks.

### Initialization Sequence

```mermaid
graph TD
    Start["Orchestrator.run()"] --> CreateExecutor["Create Executor<br/>process_manager"]
    CreateExecutor --> InitUI["init_ui()"]
    InitUI --> OfflineCheck["offline_changes_check()"]
    
    OfflineCheck --> CheckModified{Files<br/>modified?}
    CheckModified -->|Yes| AskUser["Ask user:<br/>Keep or restore?"]
    CheckModified -->|No| CheckEmpty{Workspace<br/>empty?}
    
    AskUser -->|Keep| ImportFiles["import_files()"]
    AskUser -->|Restore| RestoreFiles["restore_files()"]
    
    CheckEmpty -->|Yes| RestoreFiles
    CheckEmpty -->|No| InstallDeps
    
    ImportFiles --> InstallDeps
    RestoreFiles --> InstallDeps
    
    InstallDeps["install_dependencies()"] --> CheckGit["Check git installed"]
    CheckGit --> InitGit{Git<br/>available?}
    
    InitGit -->|Yes| GitInit["init_git_if_needed()"]
    InitGit -->|No| SetupScripts
    
    GitInit --> SetupScripts["Setup scripts:<br/>- set_frontend_script()<br/>- set_package_json()<br/>- set_vite_config()<br/>- set_favicon()<br/>- enable_debugger()"]
    
    SetupScripts --> UpdateKB["Update UI with<br/>knowledge_base"]
    UpdateKB --> EnterLoop["Enter main<br/>control loop"]
```

### Key Initialization Methods

| Method | Purpose | Location |
|--------|---------|----------|
| `init_ui()` | Initialize user interface | [core/agents/base.py]() |
| `offline_changes_check()` | Detect external file modifications | [core/agents/orchestrator.py:370-417]() |
| `install_dependencies()` | Run `npm install` if needed | [core/agents/orchestrator.py:169-181]() |
| `init_git_if_needed()` | Initialize Git repository | [core/agents/git.py]() |
| `set_frontend_script()` | Inject Pythagora utilities script | [core/agents/orchestrator.py:182-221]() |
| `enable_debugger()` | Add debug script to package.json | [core/agents/orchestrator.py:222-251]() |

**Sources:** [core/agents/orchestrator.py:48-86](), [core/agents/orchestrator.py:169-344](), [core/agents/orchestrator.py:370-417]()

---

## Entry Point Integration

The Orchestrator is instantiated and started from the CLI entry point.

### Application Startup Flow

```mermaid
graph TB
    Main["main.py::run_pythagora()"] --> Init["init()"]
    Init --> ParseArgs["parse_arguments()"]
    Init --> LoadConfig["load_config()"]
    Init --> CreateDB["SessionManager<br/>(database)"]
    Init --> CreateUI["Create UIBase<br/>(console or IPC)"]
    
    Main --> AsyncMain["async_main()"]
    
    AsyncMain --> LoadOrCreate{Load existing<br/>or new project?}
    
    LoadOrCreate -->|Existing| LoadProject["load_project()"]
    LoadOrCreate -->|New| StartNew["start_new_project()"]
    
    LoadProject --> RunProject["run_project()"]
    StartNew --> CreateProject["StateManager.create_project()"]
    CreateProject --> RunProject
    
    RunProject --> CreateOrchestrator["Orchestrator(sm, ui, args)"]
    CreateOrchestrator --> OrchestratorRun["orchestrator.run()"]
    
    OrchestratorRun --> Success{Success?}
    Success -->|True| Cleanup["cleanup()<br/>Send telemetry"]
    Success -->|False| Rollback["sm.rollback()"]
    
    Cleanup --> Exit
    Rollback --> Exit["Exit"]
```

### Main Entry Points

1. **CLI Entry**: [core/cli/main.py:429-438]() - `run_pythagora()` function
2. **Async Main**: [core/cli/main.py:324-426]() - `async_main()` coroutine
3. **Session Runner**: [core/cli/main.py:194-321]() - `run_pythagora_session()`
4. **Project Runner**: [core/cli/main.py:63-105]() - `run_project()` creates and runs Orchestrator

**Sources:** [core/cli/main.py:63-105](), [core/cli/main.py:194-321](), [core/cli/main.py:324-438]()

---

## Error Handling and Recovery

The Orchestrator implements several error handling strategies to recover from failures and user interruptions.

### Exception Handling Strategy

```mermaid
graph TB
    Try["try block:<br/>orchestrator.run()"] --> Success["Success"]
    Try --> Exceptions{Exception Type}
    
    Exceptions -->|KeyboardInterrupt| UserInt["User Interruption"]
    Exceptions -->|UIClosedError| UserInt
    Exceptions -->|APIError| APIErr["LLM API Error"]
    Exceptions -->|CustomAssertionError| SDKErr["Anthropic SDK Error"]
    Exceptions -->|Other Exception| UnknownErr["Uncaught Exception"]
    
    UserInt --> Log1["Log interruption"]
    APIErr --> SendErr1["send_error(ui)"]
    SDKErr --> SendErr2["send_error(ui)"]
    UnknownErr --> SendErr3["send_error(ui)"]
    
    Log1 --> Rollback["state_manager.rollback()"]
    SendErr1 --> Rollback
    SendErr2 --> Rollback
    SendErr3 --> RecordCrash["telemetry.record_crash()"]
    
    RecordCrash --> Rollback
    Rollback --> SetTelemetry["Set telemetry end_result"]
    Success --> SetTelemetry
    
    SetTelemetry --> Return["Return success status"]
```

### Error Types and Handling

| Exception Type | Source | Handling | Telemetry |
|----------------|--------|----------|-----------|
| `KeyboardInterrupt` | User presses Ctrl+C | Rollback state, clean exit | `end_result: interrupt` |
| `UIClosedError` | UI connection lost | Rollback state, clean exit | `end_result: interrupt` |
| `APIError` | LLM API failure | Show error, rollback state | `end_result: failure:api-error` |
| `CustomAssertionError` | Anthropic SDK issue | Show error, rollback state | `end_result: failure:assertion-error` |
| `UserInterruptError` | User cancels agent action | Force DONE response | Continue workflow |
| Generic `Exception` | Unknown error | Send fatal error, crash report | `end_result: crash` |

**Sources:** [core/cli/main.py:80-104](), [core/cli/main.py:108-118](), [core/agents/orchestrator.py:143-148]()

---

## File Import and Description Pipeline

After committing state, the Orchestrator checks for external file changes and ensures all files have metadata descriptions.

### File Processing Pipeline

```mermaid
sequenceDiagram
    participant Orchestrator
    participant SM as StateManager
    participant VFS as VirtualFileSystem
    participant Importer
    participant DescribeFiles
    participant LLM
    
    Orchestrator->>SM: import_files()
    SM->>VFS: list()
    VFS-->>SM: workspace files
    
    SM->>SM: Compare with current_state.files
    
    alt Files changed externally
        SM->>SM: Calculate diffs
        SM-->>Orchestrator: (imported, removed)
        
        Orchestrator->>Orchestrator: Check for INPUT_REQUIRED
        
        alt Input required
            Orchestrator->>Importer: Run Importer agent
            Importer->>Orchestrator: User provides input
        end
        
        SM->>SM: Save imported files to next_state
    end
    
    Orchestrator->>Orchestrator: Check for missing descriptions
    
    alt Files missing metadata
        Orchestrator->>DescribeFiles: Run DescribeFiles agent
        
        loop For each file
            DescribeFiles->>LLM: Generate description
            LLM-->>DescribeFiles: File metadata
            DescribeFiles->>SM: Update file metadata
        end
        
        DescribeFiles-->>Orchestrator: Complete
    end
```

### Implementation Details

**Import Process** [core/agents/orchestrator.py:451]():
- Calls `state_manager.import_files()` to scan workspace
- Compares current files with database state
- Detects new, modified, and deleted files
- Returns `AgentResponse.import_project()` if input required

**Description Process** [core/agents/orchestrator.py:454-462]():
- Identifies files without `metadata.description`
- Returns `AgentResponse.describe_files()` with file list
- Routes to `DescribeFiles` agent to add metadata
- Ensures all files have searchable descriptions

**Sources:** [core/agents/orchestrator.py:418-479](), [core/state/state_manager.py:703-738](), [core/agents/importer.py]()

---

## Knowledge Base Updates

The Orchestrator tracks when agents modify pages or API endpoints and updates the knowledge base accordingly.

### Knowledge Base Update Logic

```mermaid
graph TD
    AgentComplete["Agent completes"] --> CheckAgent{Agent type?}
    
    CheckAgent -->|CodeMonkey| CheckFiles{Modified files<br/>in src/pages/<br/>or src/api/?}
    CheckAgent -->|Frontend| CheckPages{Modified<br/>frontend pages?}
    CheckAgent -->|Other| NoUpdate["No KB update"]
    
    CheckFiles -->|Yes| GatherAPIs["Gather API endpoints<br/>from modified files"]
    CheckFiles -->|No| NoUpdate
    
    CheckPages -->|Yes| UpdatePages["update_implemented_pages_and_apis()"]
    CheckPages -->|No| NoUpdate
    
    GatherAPIs --> UpdateAPIs["update_apis(files)"]
    UpdateAPIs --> UpdatePages
    
    UpdatePages --> SendUI["Send knowledge_base_update<br/>to UI"]
    
    SendUI --> Continue["Continue workflow"]
    NoUpdate --> Continue
```

### Implementation References

**Parallel Agent KB Check** [core/agents/orchestrator.py:117-140]():
- After parallel CodeMonkey execution
- Checks if any agent modified `src/pages/` or `src/api/`
- Aggregates `related_api_endpoints` from tasks
- Calls `state_manager.update_apis()` and `update_implemented_pages_and_apis()`

**Frontend Agent KB Update** [core/agents/frontend.py:164]():
- After frontend iteration completes
- Calls `state_manager.update_implemented_pages_and_apis()`
- Updates UI with current pages and APIs

**Sources:** [core/agents/orchestrator.py:117-140](), [core/agents/frontend.py:162-165](), [core/state/state_manager.py:840-920]()

---

## Orchestrator Lifecycle Summary

### Complete Workflow Diagram

```mermaid
stateDiagram-v2
    [*] --> Init: Start Orchestrator
    
    Init --> OfflineCheck: Initialize UI, DB, Executor
    OfflineCheck --> InstallDeps: Check/import external changes
    InstallDeps --> SetupScripts: npm install if needed
    SetupScripts --> MainLoop: Configure project files
    
    MainLoop --> CheckRedo: Begin control loop
    CheckRedo --> UpdateStats: Handle task redo if needed
    UpdateStats --> CreateAgent: Update telemetry
    
    CreateAgent --> IsParallel{Multiple agents?}
    IsParallel --> RunParallel: Yes
    IsParallel --> RunSingle: No
    
    RunParallel --> HandleParallel: asyncio.gather()
    RunSingle --> RunAgent: agent.run()
    
    HandleParallel --> CheckResponse
    RunAgent --> CheckResponse: AgentResponse
    
    CheckResponse --> ResponseType{response.type}
    
    ResponseType --> Exit: EXIT
    ResponseType --> HandleDone: DONE
    ResponseType --> MainLoop: Other
    
    HandleDone --> CommitState: Persist changes
    CommitState --> ImportFiles: Save to database
    ImportFiles --> DescribeFiles: Import external changes
    DescribeFiles --> UpdateKB: Add file metadata
    UpdateKB --> MainLoop: Update knowledge base
    
    Exit --> Cleanup: End orchestrator
    Cleanup --> [*]: Send telemetry
```

**Sources:** [core/agents/orchestrator.py:48-167](), [core/cli/main.py:63-105]()

---

# Page: UI and Communication Layer

# UI and Communication Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [core/cli/helpers.py](core/cli/helpers.py)
- [core/cli/main.py](core/cli/main.py)
- [core/db/models/project.py](core/db/models/project.py)
- [core/db/models/project_state.py](core/db/models/project_state.py)
- [core/db/v0importer.py](core/db/v0importer.py)
- [core/state/state_manager.py](core/state/state_manager.py)
- [core/ui/api_server.py](core/ui/api_server.py)
- [core/ui/base.py](core/ui/base.py)
- [core/ui/console.py](core/ui/console.py)
- [core/ui/ipc_client.py](core/ui/ipc_client.py)
- [core/ui/virtual.py](core/ui/virtual.py)
- [tests/cli/test_cli.py](tests/cli/test_cli.py)
- [tests/db/test_project.py](tests/db/test_project.py)

</details>



## Purpose and Scope

This document describes the UI and Communication Layer of GPT Pilot, which provides an abstraction for user interaction and real-time communication between the core system and external interfaces. The layer supports multiple UI adapters (terminal, VSCode extension, testing) through a unified interface, enabling the system to operate in different environments without modifying agent code.

For information about how the Orchestrator coordinates agents and manages workflow, see [Orchestrator and Control Flow](#3.3). For details on agent implementations, see [Agent System](#4).

---

## Architecture Overview

The UI and Communication Layer follows an adapter pattern with a common `UIBase` abstract class that defines the interface for all user interactions. This design allows agents to communicate with users without knowledge of the underlying UI implementation.

### UI Adapter Diagram

```mermaid
graph TB
    subgraph "Agent Layer"
        Agent[BaseAgent]
        Orchestrator[Orchestrator]
    end
    
    subgraph "UI Abstraction"
        UIBase[UIBase Abstract Class]
    end
    
    subgraph "UI Implementations"
        PlainConsoleUI[PlainConsoleUI<br/>Terminal Interface]
        IPCClientUI[IPCClientUI<br/>VSCode Extension]
        VirtualUI[VirtualUI<br/>Testing Mock]
    end
    
    subgraph "External Components"
        Terminal[Terminal<br/>stdout/stdin]
        VSCodeExt[VSCode Extension<br/>TCP Socket]
        TestRunner[Test Framework]
    end
    
    Agent --> UIBase
    Orchestrator --> UIBase
    
    UIBase -.implements.- PlainConsoleUI
    UIBase -.implements.- IPCClientUI
    UIBase -.implements.- VirtualUI
    
    PlainConsoleUI --> Terminal
    IPCClientUI <--> VSCodeExt
    VirtualUI --> TestRunner
    
    style UIBase fill:#ffcc99
```

**Sources:** [core/ui/base.py:104-567](), [core/ui/console.py:11-273](), [core/ui/ipc_client.py:130-662](), [core/ui/virtual.py:9-254]()

---

## UIBase Abstract Class

The `UIBase` class at [core/ui/base.py:104-567]() defines the contract for all UI implementations. It provides over 40 methods for different types of user interactions and system notifications.

### Core Method Categories

| Category | Methods | Purpose |
|----------|---------|---------|
| **Lifecycle** | `start()`, `stop()` | Initialize and cleanup UI adapter |
| **Messaging** | `send_message()`, `send_stream_chunk()` | Display information to users |
| **User Input** | `ask_question()` | Request user responses with optional buttons |
| **File Operations** | `open_editor()`, `generate_diff()`, `send_file_status()` | Show file changes and diffs |
| **Progress** | `send_task_progress()`, `send_step_progress()`, `send_epics_and_tasks()` | Update project state |
| **Special Events** | `send_key_expired()`, `send_app_finished()`, `loading_finished()` | Handle lifecycle events |

### UISource and Message Attribution

The system uses `UISource` and `AgentSource` classes to attribute messages to their origin:

```python
# From core/ui/base.py:38-83
class UISource:
    display_name: str  # Human-readable name
    type_name: str     # Type identifier for IPC
    
class AgentSource(UISource):
    # type_name becomes "agent:{agent_type}"
```

This allows the UI to display which agent (Developer, CodeMonkey, etc.) is sending each message.

**Sources:** [core/ui/base.py:38-83](), [core/ui/base.py:104-567]()

---

## PlainConsoleUI Implementation

`PlainConsoleUI` at [core/ui/console.py:11-273]() provides a simple terminal-based interface using standard I/O streams. It's the default UI when no IPC connection is available.

### Key Implementation Details

```python
# From core/ui/console.py:86-132
async def ask_question(self, question: str, ...) -> UserInput:
    # Prints question to stdout
    # Uses prompt_toolkit for async input
    session = PromptSession("> ")
    choice = await session.prompt_async(default=initial_text or "")
```

**Features:**
- **Synchronous Output**: Messages printed directly to stdout
- **Async Input**: Uses `prompt_toolkit.PromptSession` for non-blocking input
- **Button Support**: Displays button options as text choices
- **Simplified Display**: Most visual features (diffs, progress bars) are no-ops

**Sources:** [core/ui/console.py:11-273]()

---

## IPCClientUI and VSCode Extension

The `IPCClientUI` class at [core/ui/ipc_client.py:130-662]() connects to the VSCode extension via TCP socket, enabling rich IDE integration with real-time updates, syntax highlighting, and interactive debugging.

### Connection Architecture

```mermaid
graph LR
    subgraph "Python Core"
        IPCClientUI[IPCClientUI]
        SM[StateManager]
        Agents[Agents]
    end
    
    subgraph "IPC Protocol"
        Socket[TCP Socket<br/>localhost:8125]
    end
    
    subgraph "VSCode Extension"
        IPCServer[Extension Backend]
        UI[Extension UI]
    end
    
    Agents --> IPCClientUI
    SM --> IPCClientUI
    IPCClientUI <-->|Length-Prefixed<br/>JSON Messages| Socket
    Socket <-->|Message Protocol| IPCServer
    IPCServer --> UI
    
    style Socket fill:#e6e6e6
```

### Message Protocol

Messages are transmitted using a **length-prefixed JSON protocol**:

```
[4-byte length][JSON payload]
```

The `Message` class at [core/ui/ipc_client.py:75-128]() defines the structure:

```python
class Message(BaseModel):
    type: MessageType           # Message type enum
    category: Optional[str]      # Source agent type
    content: Union[str, dict]    # Message payload
    project_state_id: Optional[str]
    extra_info: Optional[dict]   # Additional metadata
    request_id: Optional[str]    # For request-response matching
```

**Wire Format Methods:**
- `to_bytes()` at [core/ui/ipc_client.py:101-105](): Serializes to JSON bytes
- `from_bytes()` at [core/ui/ipc_client.py:108-127](): Deserializes with error handling

**Sources:** [core/ui/ipc_client.py:75-128](), [core/ui/ipc_client.py:130-217]()

---

## Message Types

The `MessageType` enum at [core/ui/ipc_client.py:21-73]() defines over 50 message types for different communication scenarios:

### Message Type Categories

```mermaid
graph TB
    subgraph "Streaming Messages"
        STREAM["STREAM<br/>LLM output chunks"]
        IMPORTANT_STREAM["IMPORTANT_STREAM<br/>Markdown display"]
        BREAKDOWN_STREAM["BREAKDOWN_STREAM<br/>Task breakdown"]
    end
    
    subgraph "User Interaction"
        USER_INPUT_REQUEST["USER_INPUT_REQUEST<br/>Ask questions"]
        CHAT_MESSAGE["CHAT_MESSAGE<br/>Chat interface"]
        TEST_INSTRUCTIONS["TEST_INSTRUCTIONS<br/>Testing guidance"]
    end
    
    subgraph "File Operations"
        OPEN_FILE["OPEN_FILE<br/>Open in editor"]
        GENERATE_DIFF["GENERATE_DIFF<br/>Show file changes"]
        FILE_STATUS["FILE_STATUS<br/>File state updates"]
    end
    
    subgraph "Progress Updates"
        EPICS_AND_TASKS["EPICS_AND_TASKS<br/>Project structure"]
        PROGRESS["PROGRESS<br/>Task/step progress"]
        BUG_HUNTER_STATUS["BUG_HUNTER_STATUS<br/>Debug cycles"]
    end
    
    subgraph "Lifecycle Events"
        LOADING_FINISHED["LOADING_FINISHED<br/>Project loaded"]
        APP_FINISHED["APP_FINISHED<br/>Project complete"]
        EXIT["EXIT<br/>Shutdown"]
    end
```

### Key Message Types

| Type | Direction | Purpose |
|------|-----------|---------|
| `STREAM` | Core → Extension | Stream LLM response chunks |
| `USER_INPUT_REQUEST` | Core → Extension | Request user input with optional buttons |
| `RESPONSE` | Extension → Core | User's answer to question |
| `GENERATE_DIFF` | Core → Extension | Show file diff with syntax highlighting |
| `OPEN_FILE` | Core → Extension | Open file at specific line |
| `EPICS_AND_TASKS` | Core → Extension | Update project structure view |
| `CHAT_MESSAGE` | Bidirectional | Chat interface for interactive debugging |
| `LOADING_FINISHED` | Core → Extension | Signal project load complete |

**Sources:** [core/ui/ipc_client.py:21-73]()

---

## IPCClientUI Send Methods

The `IPCClientUI` class implements all `UIBase` methods by sending appropriate messages over the socket:

### Streaming Messages

```python
# From core/ui/ipc_client.py:219-239
async def send_stream_chunk(self, chunk: Optional[str], ...):
    if chunk is None:
        chunk = "<__stream_end__>"  # End-of-stream marker
    await self._send(MessageType.STREAM, content=chunk, ...)
```

### User Questions

```python
# From core/ui/ipc_client.py:316-394
async def ask_question(self, question: str, ...) -> UserInput:
    # Send question
    await self._send(MessageType.USER_INPUT_REQUEST, content=question, ...)
    
    # Wait for response
    response = await self._receive()
    
    # Parse button or text answer
    if response.content == "exitPythagoraCore":
        raise KeyboardInterrupt()
    return UserInput(button=answer, text=answer, ...)
```

### File Diffs

```python
# From core/ui/ipc_client.py:587-608
async def generate_diff(self, file_path, old_content, new_content, ...):
    await self._send(
        MessageType.GENERATE_DIFF,
        content={
            "file_path": file_path,
            "old_content": old_content,
            "new_content": new_content,
            "n_new_lines": n_new_lines,
            "n_del_lines": n_del_lines,
        }
    )
```

**Sources:** [core/ui/ipc_client.py:156-608]()

---

## Message Flow Patterns

### Pattern 1: Streaming LLM Responses

```mermaid
sequenceDiagram
    participant Agent
    participant IPCClientUI
    participant VSCodeExt
    
    Agent->>IPCClientUI: stream_handler(chunk1)
    IPCClientUI->>VSCodeExt: STREAM {"chunk": "Hello"}
    
    Agent->>IPCClientUI: stream_handler(chunk2)
    IPCClientUI->>VSCodeExt: STREAM {"chunk": " world"}
    
    Agent->>IPCClientUI: stream_handler(None)
    IPCClientUI->>VSCodeExt: STREAM {"chunk": "<__stream_end__>"}
```

### Pattern 2: User Input Request-Response

```mermaid
sequenceDiagram
    participant Agent
    participant IPCClientUI
    participant VSCodeExt
    participant User
    
    Agent->>IPCClientUI: ask_question("Continue?")
    IPCClientUI->>VSCodeExt: USER_INPUT_REQUEST
    VSCodeExt->>User: Display prompt
    User->>VSCodeExt: Click "yes"
    VSCodeExt->>IPCClientUI: RESPONSE {"content": "yes"}
    IPCClientUI->>Agent: UserInput(button="yes")
```

### Pattern 3: File Status Updates

```mermaid
sequenceDiagram
    participant CodeMonkey
    participant StateManager
    participant IPCClientUI
    participant VSCodeExt
    
    CodeMonkey->>StateManager: save_file(path, content)
    StateManager->>IPCClientUI: send_file_status(path, "done")
    IPCClientUI->>VSCodeExt: FILE_STATUS {"path": "...", "status": "done"}
    
    CodeMonkey->>IPCClientUI: generate_diff(path, old, new)
    IPCClientUI->>VSCodeExt: GENERATE_DIFF {file_path, old_content, new_content}
    VSCodeExt->>VSCodeExt: Display diff with syntax highlighting
```

**Sources:** [core/ui/ipc_client.py:219-608](), [core/agents/base.py]()

---

## IPCServer: API Server for External Clients

The `IPCServer` class at [core/ui/api_server.py:43-640]() provides a server-side IPC implementation that allows external clients (like VSCode extension chat interface) to query project state and interact with the system.

### Server Architecture

```mermaid
graph TB
    subgraph "IPCServer"
        Server[IPCServer<br/>asyncio.start_server]
        Handlers[Message Handlers]
    end
    
    subgraph "Message Handlers"
        EPICS[_handle_epics_and_tasks]
        CHAT[_handle_chat_message]
        INFO[_handle_project_info]
        KB[_handle_knowledge_base]
        SPECS[_handle_project_specs]
        TASK[_handle_task_convo]
    end
    
    subgraph "Data Layer"
        SM[StateManager]
        DB[(Database)]
    end
    
    Server --> Handlers
    Handlers --> EPICS
    Handlers --> CHAT
    Handlers --> INFO
    Handlers --> KB
    Handlers --> SPECS
    Handlers --> TASK
    
    EPICS --> SM
    CHAT --> SM
    INFO --> SM
    KB --> SM
    SPECS --> SM
    TASK --> SM
    SM --> DB
```

### Handler Registration

Handlers are registered in `_setup_handlers()` at [core/ui/api_server.py:64-78]():

```python
self.handlers[MessageType.EPICS_AND_TASKS] = self._handle_epics_and_tasks
self.handlers[MessageType.CHAT_MESSAGE] = self._handle_chat_message
self.handlers[MessageType.PROJECT_INFO] = self._handle_project_info
self.handlers[MessageType.KNOWLEDGE_BASE] = self._handle_knowledge_base
# ... more handlers
```

### Key Handler: Chat Message

The chat handler at [core/ui/api_server.py:246-377]() enables interactive debugging by:

1. **Creating a temporary ChatAgent** that can query project state
2. **Generating contextual prompts** with current task, bugs, and commands
3. **Streaming responses** back to the client
4. **Persisting chat history** in the database

```python
# Simplified from core/ui/api_server.py:246-377
async def _handle_chat_message(self, message: Message, writer):
    class ChatAgent(BaseAgent):
        async def stream_handler(self, content_chunk: str):
            await send_stream_chunk(writer, message_type, content_chunk, request_id)
        
        async def generate_prompt(self, convo_id, user_msg):
            # Load relevant project state
            state = await self.state_manager.get_project_state_for_convo_id(convo_id)
            
            # Build context with task description, bugs, commands
            return AgentConvo(self).template(
                "chat",
                initial_description=...,
                task_description=...,
                bug_hunt_cycle_user_feedback=...,
                # ... more context
            )
```

**Sources:** [core/ui/api_server.py:43-640]()

---

## UI Initialization and Selection

The UI adapter is selected during application startup in [core/cli/main.py:324-427]() and [core/cli/helpers.py:284-331]():

### Configuration-Based Selection

```python
# From core/cli/helpers.py:284-331
def load_config(args: Namespace) -> Optional[Config]:
    config = loader.load(args.config)
    
    # Override UI type if --local-ipc-port is provided
    if args.local_ipc_port:
        config.ui = LocalIPCConfig(port=args.local_ipc_port, host=args.local_ipc_host)
```

### UI Instantiation

```python
# From core/cli/helpers.py (not shown fully but referenced)
if config.ui.type == UIAdapter.PLAIN:
    ui = PlainConsoleUI()
elif config.ui.type == UIAdapter.IPC_CLIENT:
    ui = IPCClientUI(config.ui)
```

### StateManager Integration

The `StateManager` receives the UI instance at initialization [core/state/state_manager.py:60-62]():

```python
def __init__(self, session_manager: SessionManager, ui: Optional[UIBase] = None):
    self.ui = ui
    # ... other initialization
```

Agents then access the UI through their `StateManager` reference to send messages, ask questions, and display progress.

**Sources:** [core/cli/main.py:324-427](), [core/cli/helpers.py:284-331](), [core/state/state_manager.py:60-62]()

---

## Error Handling and Connection Management

### Connection Lifecycle

The `IPCClientUI` manages connection lifecycle at [core/ui/ipc_client.py:143-217]():

```python
async def start(self):
    self.reader, self.writer = await asyncio.open_connection(
        self.config.host,
        self.config.port,
        limit=MESSAGE_SIZE_LIMIT,  # 512KB
    )
    
async def stop(self):
    await self._send(MessageType.EXIT)
    self.writer.close()
    await self.writer.wait_closed()
```

### UIClosedError Handling

When the connection is lost or the user closes the extension, `UIClosedError` is raised at [core/ui/ipc_client.py:162-172]():

```python
if self.writer.is_closing():
    log.error("IPC connection closed, can't send the message")
    raise UIClosedError()
```

This exception is caught in the main loop at [core/cli/main.py:84-87]() to gracefully handle user interruptions:

```python
except (KeyboardInterrupt, UIClosedError):
    log.info("Interrupted by user")
    telemetry.set("end_result", "interrupt")
    await sm.rollback()
```

**Sources:** [core/ui/ipc_client.py:143-217](), [core/ui/base.py:30-36](), [core/cli/main.py:84-87]()

---

## VirtualUI for Testing

The `VirtualUI` class at [core/ui/virtual.py:9-254]() provides a mock implementation for automated testing:

```python
class VirtualUI(UIBase):
    def __init__(self, inputs: list[dict[str, str]]):
        self.virtual_inputs = [UserInput(**input) for input in inputs]
    
    async def ask_question(self, question: str, ...) -> UserInput:
        if self.virtual_inputs:
            ret = self.virtual_inputs[0]
            self.virtual_inputs = self.virtual_inputs[1:]
            return ret
        # ... fallback to default answers
```

This allows tests to pre-configure user responses without human interaction.

**Sources:** [core/ui/virtual.py:9-254]()

---

## Integration with StateManager

The `StateManager` uses the UI to:

1. **Notify project info** at [core/state/state_manager.py:388-402]()
2. **Send task progress** when loading projects [core/state/state_manager.py:388-402]()
3. **Request new access tokens** when expired [core/state/state_manager.py:232-240]()
4. **Display error messages** during failures [core/state/state_manager.py:239-245]()

### Example: Project Load Notification

```python
# From core/state/state_manager.py:388-402
if self.current_state.current_epic and self.current_state.current_task and self.ui:
    await self.ui.send_epics_and_tasks(
        self.current_state.current_epic.get("sub_epics"),
        self.current_state.tasks,
    )
    await self.ui.send_task_progress(
        self.current_state.tasks.index(self.current_state.current_task) + 1,
        len(self.current_state.tasks),
        self.current_state.current_task["description"],
        source,
        "in-progress",
        self.current_state.get_source_index(source),
        self.current_state.tasks,
    )
```

**Sources:** [core/state/state_manager.py:388-402](), [core/state/state_manager.py:232-245]()

---

## Summary

The UI and Communication Layer provides:

- **Abstraction**: `UIBase` allows agents to work with any UI implementation
- **Multiple Adapters**: Console, VSCode IPC, and testing UIs
- **Rich Protocol**: 50+ message types for comprehensive IDE integration
- **Bidirectional Communication**: Request-response and streaming patterns
- **Server Support**: `IPCServer` enables external client queries
- **Error Handling**: Graceful degradation on connection loss
- **Testing Support**: `VirtualUI` for automated testing

This architecture enables GPT Pilot to operate in different environments (CLI, IDE, tests) without modifying agent logic, while providing rich real-time feedback to users through the VSCode extension.

---

# Page: Agent System

# Agent System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [core/agents/architect.py](core/agents/architect.py)
- [core/agents/bug_hunter.py](core/agents/bug_hunter.py)
- [core/agents/developer.py](core/agents/developer.py)
- [core/agents/frontend.py](core/agents/frontend.py)
- [core/agents/mixins.py](core/agents/mixins.py)
- [core/agents/orchestrator.py](core/agents/orchestrator.py)
- [core/agents/spec_writer.py](core/agents/spec_writer.py)
- [core/agents/tech_lead.py](core/agents/tech_lead.py)
- [core/agents/troubleshooter.py](core/agents/troubleshooter.py)

</details>



GPT Pilot uses a multi-agent architecture where specialized AI agents collaborate to perform software development tasks. Each agent corresponds to a specific role in the development lifecycle (e.g., architect, developer, tester) and operates autonomously while coordinating through a shared state management system.

The agent system is orchestrated by the `Orchestrator` class, which determines execution flow based on project state and coordinates agent interactions. All agents inherit from `BaseAgent` and communicate with LLMs through a unified interface.

**Agent Execution Model:**

```mermaid
graph TB
    Orchestrator["Orchestrator.run()"]
    Orchestrator -->|"create_agent()"| AgentSelection{"Agent Selection<br/>Based on State"}
    
    AgentSelection -->|"No epics"| Wizard["Wizard"]
    AgentSelection -->|"No specification"| SpecWriter["SpecWriter"]
    AgentSelection -->|"Frontend epic"| Frontend["Frontend"]
    AgentSelection -->|"No architecture"| Architect["Architect"]
    AgentSelection -->|"No tasks"| TechLead["TechLead"]
    AgentSelection -->|"No steps"| Developer["Developer"]
    AgentSelection -->|"Current step"| StepExecution["Executor/CodeMonkey"]
    AgentSelection -->|"Unfinished iterations"| IterationHandling["Troubleshooter/BugHunter"]
    
    Wizard --> Response["AgentResponse"]
    SpecWriter --> Response
    Frontend --> Response
    Architect --> Response
    TechLead --> Response
    Developer --> Response
    StepExecution --> Response
    IterationHandling --> Response
    
    Response -->|"ResponseType.DONE"| Commit["state_manager.commit()"]
    Response -->|"ResponseType.EXIT"| End["Exit"]
    Response -->|"ResponseType.INPUT_REQUIRED"| HumanInput["HumanInput"]
    Response -->|"ResponseType.EXTERNAL_DOCS_REQUIRED"| ExternalDocs["ExternalDocumentation"]
    
    Commit --> Orchestrator
    HumanInput --> Orchestrator
    ExternalDocs --> Orchestrator
```

Sources: [core/agents/orchestrator.py:48-167](), [core/agents/orchestrator.py:463-573]()

## Agent Architecture and Base Classes

### BaseAgent Class

All agents inherit from `BaseAgent`, which provides the foundational interface for agent operations:

**Core Attributes:**
- `agent_type: str` - Identifier for the agent type
- `display_name: str` - Human-readable name
- `current_state: ProjectState` - Read-only access to current project state
- `next_state: ProjectState` - Writable state for modifications
- `state_manager: StateManager` - Interface to persistence layer
- `ui: UIBase` - User interface communication
- `process_manager: ProcessManager` - Command execution

**Key Methods:**
- `run() -> AgentResponse` - Main execution method (must be implemented by subclasses)
- `send_message(message: str)` - Send information to user
- `ask_question(question: str, buttons: dict) -> UserInput` - Get user input
- `get_llm(name: str, stream_output: bool) -> LLMClient` - Get configured LLM client

**Agent Class Hierarchy:**

```mermaid
classDiagram
    class BaseAgent {
        <<abstract>>
        +agent_type: str
        +display_name: str
        +current_state: ProjectState
        +next_state: ProjectState
        +state_manager: StateManager
        +ui: UIBase
        +process_manager: ProcessManager
        +run()* AgentResponse
        +send_message(msg: str)
        +ask_question(q: str) UserInput
        +get_llm(name: str) LLMClient
    }
    
    class Wizard {
        +agent_type = "wizard"
        +run() AgentResponse
    }
    
    class SpecWriter {
        +agent_type = "spec-writer"
        +initialize_spec_and_project()
        +change_spec()
        +update_spec()
    }
    
    class Architect {
        +agent_type = "architect"
        +plan_architecture()
        +select_templates()
        +check_system_dependencies()
    }
    
    class TechLead {
        +agent_type = "tech-lead"
        +plan_epic()
        +create_initial_project_epic()
        +ask_for_new_feature()
    }
    
    class Developer {
        +agent_type = "developer"
        +breakdown_current_task()
        +breakdown_current_iteration()
        +set_next_steps()
    }
    
    class CodeMonkey {
        +agent_type = "code-monkey"
        +implement_changes()
        +run_code_review()
        +describe_files()
    }
    
    class Frontend {
        +agent_type = "frontend"
        +start_frontend()
        +continue_frontend()
        +iterate_frontend()
    }
    
    class Troubleshooter {
        +agent_type = "troubleshooter"
        +create_iteration()
        +get_user_feedback()
        +propose_solution()
    }
    
    class BugHunter {
        +agent_type = "bug-hunter"
        +check_logs()
        +ask_user_to_test()
        +start_pair_programming()
    }
    
    class Orchestrator {
        +agent_type = "orchestrator"
        +create_agent()
        +handle_done()
    }
    
    BaseAgent <|-- Wizard
    BaseAgent <|-- SpecWriter
    BaseAgent <|-- Architect
    BaseAgent <|-- TechLead
    BaseAgent <|-- Developer
    BaseAgent <|-- CodeMonkey
    BaseAgent <|-- Frontend
    BaseAgent <|-- Troubleshooter
    BaseAgent <|-- BugHunter
    BaseAgent <|-- Orchestrator
```

Sources: [core/agents/base.py]()

### Agent Mixins

Agents use mixins to share common functionality without duplicating code:

**Mixin Classes:**

| Mixin | Purpose | Key Methods | Used By |
|-------|---------|-------------|---------|
| `RelevantFilesMixin` | Identifies files relevant to current task by filtering large codebases | `get_relevant_files_parallel()`, `get_relevant_files()` | TechLead, Developer, Troubleshooter |
| `ChatWithBreakdownMixin` | Enables interactive refinement of task breakdowns with user | `chat_with_breakdown(convo, breakdown)` | Developer, BugHunter, Troubleshooter |
| `IterationPromptMixin` | Generates solutions based on user feedback and problem analysis | `find_solution(user_feedback, ...)` | Troubleshooter, ProblemSolver |
| `FileDiffMixin` | Calculates line changes between file versions | `get_line_changes(old, new)` | Frontend, CodeMonkey |
| `GitMixin` | Git operations (commit, branch) | `git_commit(message)`, `init_git_if_needed()` | Orchestrator, Frontend |

**Mixin Implementation Pattern:**

```mermaid
classDiagram
    class RelevantFilesMixin {
        +get_relevant_files_parallel()
        +get_relevant_files(dir_type)
    }
    
    class ChatWithBreakdownMixin {
        +chat_with_breakdown(convo, breakdown)
    }
    
    class IterationPromptMixin {
        +find_solution(user_feedback)
    }
    
    class FileDiffMixin {
        +get_line_changes(old, new)
    }
    
    class Developer {
    }
    
    class TechLead {
    }
    
    class Troubleshooter {
    }
    
    class Frontend {
    }
    
    RelevantFilesMixin <|-- TechLead
    RelevantFilesMixin <|-- Developer
    RelevantFilesMixin <|-- Troubleshooter
    
    ChatWithBreakdownMixin <|-- Developer
    ChatWithBreakdownMixin <|-- BugHunter
    ChatWithBreakdownMixin <|-- Troubleshooter
    
    IterationPromptMixin <|-- Troubleshooter
    
    FileDiffMixin <|-- Frontend
    FileDiffMixin <|-- CodeMonkey
```

Sources: [core/agents/mixins.py:122-189](), [core/agents/mixins.py:37-80](), [core/agents/mixins.py:82-120](), [core/agents/mixins.py:191-209]()

### AgentResponse System

Agents return `AgentResponse` objects to communicate their completion status and next actions:

**Response Types:**

```mermaid
graph TD
    AgentResponse["AgentResponse"]
    
    AgentResponse --> DONE["ResponseType.DONE<br/>Agent completed successfully"]
    AgentResponse --> INPUT_REQUIRED["ResponseType.INPUT_REQUIRED<br/>User input needed"]
    AgentResponse --> EXIT["ResponseType.EXIT<br/>Terminate workflow"]
    AgentResponse --> EXTERNAL_DOCS["ResponseType.EXTERNAL_DOCS_REQUIRED<br/>Fetch documentation"]
    AgentResponse --> DESCRIBE_FILES["ResponseType.DESCRIBE_FILES<br/>Generate file descriptions"]
    AgentResponse --> UPDATE_SPEC["ResponseType.UPDATE_SPECIFICATION<br/>Modify project spec"]
    AgentResponse --> IMPORT["ResponseType.IMPORT_PROJECT<br/>Import external project"]
    
    DONE --> NextAgent["Orchestrator.create_agent()"]
    INPUT_REQUIRED --> HumanInput["HumanInput agent"]
    EXIT --> Terminate["End workflow"]
    EXTERNAL_DOCS --> ExternalDocs["ExternalDocumentation agent"]
    DESCRIBE_FILES --> CodeMonkey["CodeMonkey.describe_files()"]
    UPDATE_SPEC --> SpecWriter["SpecWriter.update_spec()"]
    IMPORT --> Importer["Importer agent"]
```

**Factory Methods:**
- `AgentResponse.done(agent)` - Standard completion
- `AgentResponse.input_required(agent, files)` - Requires user to fill in placeholders
- `AgentResponse.external_docs_required(agent)` - Needs external documentation
- `AgentResponse.describe_files(agent)` - Files need descriptions
- `AgentResponse.update_specification(agent, description)` - Spec needs updating
- `AgentResponse.exit(agent)` - End processing

Sources: [core/agents/response.py]()

### Orchestrator

The `Orchestrator` class coordinates all agent execution and manages the development workflow:

**Orchestration Logic:**

```python
# Simplified orchestrator logic from core/agents/orchestrator.py:463-552
def create_agent(self, prev_response):
    state = self.current_state
    
    if prev_response:
        # Handle special response types
        if prev_response.type == ResponseType.INPUT_REQUIRED:
            return HumanInput(...)
        if prev_response.type == ResponseType.EXTERNAL_DOCS_REQUIRED:
            return ExternalDocumentation(...)
        # ... other response type handlers
    
    # State-based agent selection
    if not state.epics:
        return Wizard(...)  # Initialize project
    elif not state.specification.description:
        return SpecWriter(...)  # Get requirements
    elif state.current_epic and state.current_epic.get("source") == "frontend":
        return Frontend(...)  # Build frontend
    elif not state.specification.architecture:
        return Architect(...)  # Design architecture
    elif not state.unfinished_tasks:
        return TechLead(...)  # Plan tasks
    elif not state.steps and not state.iterations:
        return Developer(...)  # Break down task
    elif state.current_step:
        return self.create_agent_for_step(state.current_step)
    elif state.unfinished_iterations:
        # Handle iteration statuses
        if state.current_iteration["status"] == IterationStatus.HUNTING_FOR_BUG:
            return BugHunter(...)
        # ... other iteration status handlers
    else:
        return Troubleshooter(...)  # Request user testing
```

Sources: [core/agents/orchestrator.py:463-552]()

## Planning Agents

Planning agents are responsible for project initialization, requirements gathering, architecture design, and task breakdown.

### SpecWriter

The `SpecWriter` agent refines project requirements and creates detailed specifications.

**Responsibilities:**
- Gathering initial project description from user
- Refining specifications through interactive Q&A
- Determining project complexity (`SIMPLE`, `MODERATE`, `HARD`)
- Updating specifications when new features are requested
- Determining authentication requirements

**Key Methods:**
- `initialize_spec_and_project()` - Gathers initial app description and creates specification
- `change_spec()` - Iteratively refines specification based on user feedback
- `update_spec()` - Updates specification when new features are added
- `check_prompt_complexity()` - Analyzes prompt to determine project complexity

**State Transitions:**

```mermaid
stateDiagram-v2
    [*] --> InitializeSpec: No specification
    InitializeSpec --> ChangeSpec: Initial spec created
    ChangeSpec --> ChangeSpec: User adds details
    ChangeSpec --> SpecFinished: User satisfied
    SpecFinished --> [*]: Specification complete
    
    SpecFinished --> UpdateSpec: New feature requested
    UpdateSpec --> SpecFinished: Update complete
```

**Specification Flow:**

```python
# From core/agents/spec_writer.py:63-162
async def initialize_spec_and_project(self):
    # Get project description from user
    description = await self.ask_question("Please describe the app...")
    
    # Use LLM to expand description
    llm = self.get_llm(SPEC_WRITER_AGENT_NAME)
    convo = AgentConvo(self).template("build_full_specification", 
                                       initial_prompt=description)
    llm_assisted_description = await llm(convo)
    
    # Generate project name
    project_name = await self.generate_project_name(llm_assisted_description)
    
    # Store in state
    self.next_state.specification.description = llm_assisted_description
    self.next_state.specification.original_description = description
```

Sources: [core/agents/spec_writer.py:19-33](), [core/agents/spec_writer.py:63-162](), [core/agents/spec_writer.py:163-303]()

### Architect

The `Architect` agent designs the project architecture, selects technologies, and checks system dependencies.

**Responsibilities:**
- Selecting appropriate project templates
- Defining system dependencies (Node.js, Python, databases)
- Defining package dependencies (Express, React, etc.)
- Checking if required dependencies are installed
- Warning about unsupported technologies

**Key Methods:**
- `plan_architecture()` - Designs overall architecture and selects technologies
- `select_templates()` - Chooses appropriate project templates based on requirements
- `check_system_dependencies()` - Verifies required dependencies are installed
- `check_compatibility()` - Warns about unsupported frameworks/tools

**Architecture Definition:**

```python
# Pydantic models from core/agents/architect.py:69-82
class Architecture(BaseModel):
    app_type: AppType  # WEB, API, MOBILE, DESKTOP, CLI
    system_dependencies: list[SystemDependency]
    package_dependencies: list[PackageDependency]

class SystemDependency(BaseModel):
    name: str
    description: str
    test: str  # Command to test if installed
    required_locally: bool

class PackageDependency(BaseModel):
    name: str
    description: str
```

**Dependency Checking:**

```mermaid
flowchart TD
    Start["plan_architecture()"]
    Start --> SelectTemplates["select_templates()"]
    SelectTemplates --> LLM["LLM: Generate Architecture"]
    LLM --> CheckCompat["check_compatibility()"]
    CheckCompat --> WarnUser{"Uses unsupported<br/>tech?"}
    WarnUser -->|Yes| ShowWarning["Show warning to user"]
    WarnUser -->|No| CheckDeps["check_system_dependencies()"]
    ShowWarning --> CheckDeps
    
    CheckDeps --> ForEach["For each dependency"]
    ForEach --> RunTest["Run dep['test'] command"]
    RunTest --> Installed{"Exit code == 0?"}
    Installed -->|Yes| ShowSuccess["✅ Available"]
    Installed -->|No| ShowFailure["❌ Not available"]
    ShowFailure --> AskInstall["Ask user to install"]
    AskInstall --> Next["Next dependency"]
    ShowSuccess --> Next
    Next --> Done["Update specification"]
```

Sources: [core/agents/architect.py:95-122](), [core/agents/architect.py:173-198](), [core/agents/architect.py:237-267]()

### TechLead

The `TechLead` agent breaks down projects and features into manageable epics and tasks.

**Responsibilities:**
- Creating the initial project epic structure
- Breaking epics into sub-epics and tasks
- Creating task breakdowns with API endpoints
- Managing feature requests from users
- Creating quick implementation tasks

**Key Methods:**
- `create_initial_project_epic()` - Sets up the initial "Build frontend" and main project epic
- `plan_epic(epic)` - Breaks an epic into sub-epics and tasks using LLM
- `ask_for_new_feature()` - Prompts user for new feature or quick task
- `process_epic(sub_epic_number, sub_epic)` - Processes a single sub-epic into tasks
- `update_epics_and_tasks()` - Adds hardcoded tasks (e.g., authentication)

**Planning Models:**

```python
# From core/agents/tech_lead.py:37-52
class Epic(BaseModel):
    description: str

class Task(BaseModel):
    description: str
    related_api_endpoints: list[APIEndpoint]
    testing_instructions: str

class APIEndpoint(BaseModel):
    description: str
    method: str  # GET, POST, PUT, DELETE
    endpoint: str  # URL path
    request_body: dict
    response_body: dict
```

**Epic Planning Flow:**

```mermaid
flowchart TD
    Run["TechLead.run()"]
    Run --> CheckEpics{"len(epics) == 1?"}
    
    CheckEpics -->|Yes| CreateInitial["create_initial_project_epic()"]
    CreateInitial --> CreateEpic["Create 'Build frontend' epic<br/>and main project epic"]
    CreateEpic --> Done["Return done()"]
    
    CheckEpics -->|No| HasCurrent{"Has current_epic?"}
    
    HasCurrent -->|Yes| PlanEpic["plan_epic(current_epic)"]
    HasCurrent -->|No| AskFeature["ask_for_new_feature()"]
    
    PlanEpic --> GetRelevant["get_relevant_files_parallel()"]
    GetRelevant --> LLMPlan["LLM: Generate DevelopmentPlan"]
    LLMPlan --> CreateSubEpics["Create sub_epics list"]
    CreateSubEpics --> ParallelTasks["Parallel: process_epic()<br/>for each sub-epic"]
    ParallelTasks --> GatherTasks["asyncio.gather() results"]
    GatherTasks --> UpdateUI["ui.send_epics_and_tasks()"]
    UpdateUI --> Done
    
    AskFeature --> UserChoice{"User choice"}
    UserChoice -->|New Feature| CreateFeatureEpic["Create feature epic"]
    UserChoice -->|Quick Task| CreateQuickTask["Add task to current epic"]
    UserChoice -->|Done| ExitResponse["Return exit()"]
    CreateFeatureEpic --> SpecUpdate["Return update_specification()"]
    CreateQuickTask --> Done
```

Sources: [core/agents/tech_lead.py:55-90](), [core/agents/tech_lead.py:92-108](), [core/agents/tech_lead.py:146-260](), [core/agents/tech_lead.py:296-368]()

## Implementation Agents

Implementation agents handle the actual code generation and task execution.

### Developer

The `Developer` agent breaks down tasks into executable implementation steps.

**Responsibilities:**
- Breaking down tasks into implementation steps with `<pythagoracode>` tags
- Breaking down iterations/bug fixes into steps
- Identifying relevant files for implementation
- Managing user approval for tasks
- Updating knowledge base with utility functions

**Key Methods:**
- `breakdown_current_task()` - Converts a task into detailed implementation steps
- `breakdown_current_iteration()` - Handles iteration/bug fix breakdowns
- `ask_to_execute_task()` - Gets user approval to execute, skip, or edit task
- `set_next_steps()` - Creates step objects from LLM response
- `update_knowledge_base()` - Registers utility functions

**Step Types:**

```python
# From core/agents/developer.py:32-77
class StepType(str, Enum):
    COMMAND = "command"
    SAVE_FILE = "save_file"
    HUMAN_INTERVENTION = "human_intervention"
    UTILITY_FUNCTION = "utility_function"

class SaveFileStep(BaseModel):
    type: Literal[StepType.SAVE_FILE]
    save_file: SaveFileOptions  # Contains path

class CommandStep(BaseModel):
    type: Literal[StepType.COMMAND]
    command: CommandOptions  # Contains command, timeout

class HumanInterventionStep(BaseModel):
    type: Literal[StepType.HUMAN_INTERVENTION]
    human_intervention_description: str

class UtilityFunction(BaseModel):
    type: Literal[StepType.UTILITY_FUNCTION]
    file: str
    function_name: str
    description: str
```

**Task Breakdown Flow:**

```mermaid
flowchart TD
    Run["Developer.run()"]
    Run --> CheckStep{"current_step type?"}
    
    CheckStep -->|"utility_function"| UpdateKB["update_knowledge_base()"]
    CheckStep -->|None| CheckTasks{"Has unfinished_tasks?"}
    
    UpdateKB --> CompleteStep["complete_step()"]
    CompleteStep --> Done["Return done()"]
    
    CheckTasks -->|No| Done
    CheckTasks -->|Yes| CheckIter{"Has unfinished_iterations?"}
    
    CheckIter -->|Yes| BreakdownIter["breakdown_current_iteration()"]
    CheckIter -->|No| CheckAsk{"Should ask to execute?"}
    
    CheckAsk -->|Yes| AskExecute["ask_to_execute_task()"]
    AskExecute --> UserResponse{"User response"}
    UserResponse -->|Skip| SetSkipped["Set TaskStatus.SKIPPED"]
    UserResponse -->|Edit| SaveEdits["Save task edits"]
    UserResponse -->|Approve| CheckDocs{"docs == None?"}
    SetSkipped --> Done
    SaveEdits --> Done
    
    CheckAsk -->|No| CheckDocs
    CheckDocs -->|Yes| ExternalDocs["Return external_docs_required()"]
    CheckDocs -->|No| BreakdownTask["breakdown_current_task()"]
    
    BreakdownTask --> GetRelevant["get_relevant_files_parallel()"]
    GetRelevant --> LLMBreakdown["LLM: Generate task breakdown"]
    LLMBreakdown --> ChatBreakdown["chat_with_breakdown()"]
    ChatBreakdown --> ParseTask["LLM: Parse into TaskSteps"]
    ParseTask --> SetSteps["set_next_steps()"]
    SetSteps --> Done
    
    BreakdownIter --> GetRelevantIter["get_relevant_files_parallel()"]
    GetRelevantIter --> LLMParse["LLM: Parse iteration steps"]
    LLMParse --> SetStepsIter["set_next_steps()"]
    SetStepsIter --> UpdateStatus["Update iteration status"]
    UpdateStatus --> Done
```

Sources: [core/agents/developer.py:91-120](), [core/agents/developer.py:204-311](), [core/agents/developer.py:121-202](), [core/agents/developer.py:313-348]()

### CodeMonkey

The `CodeMonkey` agent implements code changes by parsing `<pythagoracode>` tags and writing files.

**Responsibilities:**
- Parsing and implementing `<pythagoracode>` file changes
- Running code reviews on implemented changes
- Describing files for documentation
- Generating diffs for user review
- Handling Relace-based code merging

**Key Methods:**
- `implement_changes()` - Implements code from `<pythagoracode>` tags
- `run_code_review()` - Reviews changes for quality and correctness
- `describe_files()` - Generates file descriptions for missing metadata
- `accept_changes()` - Saves approved changes to file system

**Code Implementation Process:**

```python
# From core/agents/code_monkey.py:138-225
async def implement_changes(self):
    # Parse <pythagoracode> tags
    step = self.current_state.current_step
    file_path = step["save_file"]["path"]
    
    # Get instructions from task
    instructions = self.current_state.current_task["instructions"]
    
    # Extract code for this file
    code_blocks = self.parse_code_blocks(instructions, file_path)
    
    if not code_blocks:
        # Fallback to direct LLM generation
        new_content = await self.generate_file_with_llm(file_path)
    else:
        new_content = code_blocks[0]
    
    # Store in temporary location for review
    self.next_state.modified_files[file_path] = new_content
```

**CodeMonkey Workflow:**

```mermaid
flowchart TD
    Run["CodeMonkey.run()"]
    Run --> CheckResponse{"prev_response type?"}
    
    CheckResponse -->|DESCRIBE_FILES| Describe["describe_files()"]
    CheckResponse -->|Other| Implement["implement_changes()"]
    
    Describe --> GatherFiles["Gather files without descriptions"]
    GatherFiles --> ForEach["For each file"]
    ForEach --> LLMDescribe["LLM: Generate description"]
    LLMDescribe --> UpdateMeta["Update file.content.meta"]
    UpdateMeta --> CheckMore{"More files?"}
    CheckMore -->|Yes| ForEach
    CheckMore -->|No| Done["Return done()"]
    
    Implement --> ParseTags["Parse <pythagoracode> tags"]
    ParseTags --> HasTags{"Found code?"}
    HasTags -->|No| DirectLLM["LLM: Generate file directly"]
    HasTags -->|Yes| ExtractCode["Extract code content"]
    DirectLLM --> StoreModified["Store in modified_files"]
    ExtractCode --> StoreModified
    
    StoreModified --> Review["run_code_review()"]
    Review --> LLMReview["LLM: Review code quality"]
    LLMReview --> CheckFeedback{"Has feedback?"}
    
    CheckFeedback -->|Yes| UpdateInstructions["Add feedback to instructions"]
    UpdateInstructions --> Implement
    
    CheckFeedback -->|No| Accept["accept_changes()"]
    Accept --> GenerateDiff["ui.generate_diff()"]
    GenerateDiff --> SaveFile["state_manager.save_file()"]
    SaveFile --> CompleteStep["complete_step()"]
    CompleteStep --> CheckInput{"Requires input?"}
    
    CheckInput -->|Yes| InputRequired["Return input_required()"]
    CheckInput -->|No| Done
```

Sources: [core/agents/code_monkey.py:44-67](), [core/agents/code_monkey.py:138-281](), [core/agents/code_monkey.py:206-225]()

## Frontend Development Agent

### Frontend

The `Frontend` agent builds and iterates on the UI portion of the application.

**Responsibilities:**
- Building initial frontend from specification
- Applying Vite React or Vite React Swagger templates
- Implementing UI changes based on user feedback
- Removing mock API implementations when integrating real backends
- Auto-debugging frontend errors
- Managing frontend iteration cycles

**Key Methods:**
- `start_frontend()` - Builds initial frontend implementation
- `continue_frontend()` - Continues building when initial response is incomplete
- `iterate_frontend()` - Implements user-requested changes
- `remove_mock()` - Replaces mock API calls with real endpoints
- `try_auto_debug()` - Automatically detects and reports frontend errors
- `process_response()` - Processes LLM response blocks (files and commands)

**Frontend Workflow:**

```mermaid
stateDiagram-v2
    [*] --> StartFrontend: epics[-1]["messages"] empty
    StartFrontend --> ContinueFrontend: fe_iteration_done == False
    ContinueFrontend --> ContinueFrontend: Response incomplete
    ContinueFrontend --> RemoveMock: Has file_paths_to_remove_mock
    ContinueFrontend --> IterateFrontend: fe_iteration_done == True
    RemoveMock --> IterateFrontend
    IterateFrontend --> AutoDebug: Start iteration
    AutoDebug --> UserFeedback: No errors found
    AutoDebug --> ImplementFix: Errors found
    ImplementFix --> IterateFrontend
    UserFeedback --> Done: User done with UI
    UserFeedback --> IterateFrontend: User requests changes
    Done --> [*]
```

**Response Processing:**

```python
# From core/agents/frontend.py:356-449
async def process_response(self, response_blocks, removed_mock=False, relace=False):
    for block in response_blocks:
        description = block.description.strip()
        content = block.content.strip()
        
        last_line = description.split("\n")[-1].strip()
        
        if "file:" in last_line:
            # Extract file path
            file_path = last_line[last_line.index("file:") + 5:].strip()
            new_content = content
            old_content = self.current_state.get_file_content_by_path(file_path)
            
            if relace:
                # Use Relace for code merging
                new_content = await self.relace_merge(old_content, new_content)
            
            # Save file and generate diff
            await self.state_manager.save_file(file_path, new_content)
            await self.ui.generate_diff(file_path, old_content, new_content)
            
        elif "command:" in last_line:
            # Execute commands (npm install, etc.)
            commands = content.strip().split("\n")
            for command in commands:
                await self.process_manager.run_command(command)
```

**Auto-Debug Feature:**

The Frontend agent includes automatic error detection:

```python
# From core/agents/frontend.py:554-602
async def try_auto_debug(self):
    # Start frontend server
    npm_proc = await self.process_manager.start_process("npm run start &")
    
    # Wait for output
    await asyncio.sleep(5)
    diff_stdout, diff_stderr = await npm_proc.read_output()
    
    # Test the app
    await self.process_manager.run_command("curl http://localhost:5173")
    
    # Check for errors
    if diff_stdout or diff_stderr:
        return f"I got an error. Here are the logs:\n{diff_stdout}\n{diff_stderr}"
    
    return ""  # No errors found
```

Sources: [core/agents/frontend.py:40-60](), [core/agents/frontend.py:61-110](), [core/agents/frontend.py:112-150](), [core/agents/frontend.py:151-318](), [core/agents/frontend.py:356-449](), [core/agents/frontend.py:554-602]()

## Quality Assurance Agents

Quality assurance agents handle testing, user feedback collection, and bug fixing.

### Troubleshooter

The `Troubleshooter` agent coordinates testing and gathers user feedback.

**Responsibilities:**
- Generating test instructions for tasks
- Collecting user feedback on implementations
- Detecting iteration loops (when stuck in bug fixing cycles)
- Proposing solutions to reported issues
- Routing bugs to BugHunter or changes to SpecWriter
- Marking tasks as reviewed when complete

**Key Methods:**
- `create_iteration()` - Creates iteration based on user feedback
- `get_user_instructions()` - Generates test steps using LLM
- `get_user_feedback()` - Prompts user to test and provide feedback
- `propose_solution()` - Generates solution for reported issue
- `complete_task()` - Marks task as `TaskStatus.REVIEWED`
- `trace_loop()` - Sends telemetry when iteration loops detected

**Iteration Status Management:**

```python
# From core/agents/troubleshooter.py:127-145
# Create new iteration based on feedback type
if is_loop:
    iteration_status = IterationStatus.PROBLEM_SOLVER
elif bug_report is not None:
    iteration_status = IterationStatus.HUNTING_FOR_BUG
else:  # change_description is not None
    iteration_status = IterationStatus.NEW_FEATURE_REQUESTED

self.next_state.iterations.append({
    "id": uuid4().hex,
    "user_feedback": user_feedback,
    "user_feedback_qa": user_feedback_qa,
    "description": None,
    "alternative_solutions": [],
    "attempts": 1,
    "status": iteration_status,
    "bug_hunting_cycles": [],
})
```

**Testing Flow:**

```mermaid
flowchart TD
    Run["Troubleshooter.run()"]
    Run --> HasIter{"Has unfinished_iterations?"}
    
    HasIter -->|Yes| CheckStatus{"status == FIND_SOLUTION?"}
    HasIter -->|No| CreateIter["create_iteration()"]
    
    CheckStatus -->|Yes| ProposeSolution["propose_solution()"]
    CheckStatus -->|No| Error["Raise ValueError"]
    
    ProposeSolution --> FindSolution["find_solution()"]
    FindSolution --> SetStatus["Set status to IMPLEMENT_SOLUTION"]
    SetStatus --> Done["Return done()"]
    
    CreateIter --> GetRunCmd["get_run_command()"]
    GetRunCmd --> HasInstructions{"Has test_instructions?"}
    
    HasInstructions -->|No| GetInstructions["get_user_instructions()"]
    GetInstructions --> CheckNeedsTest{"Needs testing?"}
    CheckNeedsTest -->|No| CompleteTask["complete_task()"]
    CheckNeedsTest -->|Yes| SaveInstructions["Save to task"]
    SaveInstructions --> Done
    
    HasInstructions -->|Yes| SendInstructions["ui.send_test_instructions()"]
    SendInstructions --> GetFeedback["get_user_feedback()"]
    
    GetFeedback --> ShouldIterate{"should_iterate?"}
    ShouldIterate -->|No| CompleteTask
    ShouldIterate -->|Yes| CheckLoop{"is_loop?"}
    
    CheckLoop -->|Yes| SetProblemSolver["Create iteration<br/>PROBLEM_SOLVER status"]
    CheckLoop -->|No, bug| SetBugHunter["Create iteration<br/>HUNTING_FOR_BUG status"]
    CheckLoop -->|No, change| SetFeature["Create iteration<br/>NEW_FEATURE_REQUESTED status"]
    
    SetProblemSolver --> Done
    SetBugHunter --> Done
    SetFeature --> Done
    CompleteTask --> SetReviewed["Set TaskStatus.REVIEWED"]
    SetReviewed --> Done
```

**Loop Detection:**

The Troubleshooter detects when the system is stuck in a loop (defined as `LOOP_THRESHOLD = 3` iterations) and triggers the ProblemSolver agent:

```python
# From core/agents/troubleshooter.py:22-23, 112-119, 143-145
LOOP_THRESHOLD = 3

# In create_iteration()
last_iteration = self.current_state.iterations[-1] if len(self.current_state.iterations) >= 3 else None

if is_loop:
    if last_iteration is not None and last_iteration.get("alternative_solutions"):
        return self.try_next_alternative_solution(user_feedback, user_feedback_qa)
    else:
        iteration_status = IterationStatus.PROBLEM_SOLVER
        await self.trace_loop("loop-feedback")
        
if len(self.next_state.iterations) == LOOP_THRESHOLD:
    await self.trace_loop("loop-start")
```

Sources: [core/agents/troubleshooter.py:35-46](), [core/agents/troubleshooter.py:63-146](), [core/agents/troubleshooter.py:148-159](), [core/agents/troubleshooter.py:203-231](), [core/agents/troubleshooter.py:244-346]()

### BugHunter

The `BugHunter` agent identifies and resolves bugs through log analysis and user interaction.

**Responsibilities:**
- Generating bug reproduction instructions
- Analyzing logs to identify bug sources
- Determining whether to add logs or implement fixes
- Guiding users through testing bug fixes
- Facilitating pair programming for complex bugs
- Managing bug hunting cycles

**Key Methods:**
- `get_bug_reproduction_instructions()` - Creates steps to reproduce bug
- `check_logs()` - Analyzes logs to identify bug cause
- `ask_user_to_test()` - Prompts user to test fix or reproduce bug
- `start_pair_programming()` - Initiates interactive debugging session
- `set_data_for_next_hunting_cycle()` - Prepares next debugging attempt

**Bug Hunting Cycle:**

```python
# From core/agents/bug_hunter.py:400-411
def set_data_for_next_hunting_cycle(self, human_readable_instructions, new_status):
    self.next_state.current_iteration["description"] = human_readable_instructions
    self.next_state.current_iteration["bug_hunting_cycles"] += [{
        "human_readable_instructions": human_readable_instructions,
        "fix_attempted": any(
            c["fix_attempted"] for c in self.current_state.current_iteration["bug_hunting_cycles"]
        ),
    }]
    self.next_state.current_iteration["status"] = new_status
```

**BugHunter Workflow:**

```mermaid
flowchart TD
    Run["BugHunter.run()"]
    Run --> HasRepro{"Has bug_reproduction_description?"}
    
    HasRepro -->|No| GetRepro["get_bug_reproduction_instructions()"]
    GetRepro --> Done["Return done()"]
    
    HasRepro -->|Yes| CheckStatus{"Check iteration.status"}
    
    CheckStatus -->|HUNTING_FOR_BUG| CheckLogs["check_logs()"]
    CheckStatus -->|AWAITING_USER_TEST| AskTestFix["ask_user_to_test(awaiting_user_test=True)"]
    CheckStatus -->|AWAITING_BUG_REPRODUCTION| AskRepro["ask_user_to_test(awaiting_bug_reproduction=True)"]
    CheckStatus -->|START_PAIR_PROGRAMMING| PairProg["start_pair_programming()"]
    
    CheckLogs --> GenConvo["generate_iteration_convo_so_far()"]
    GenConvo --> LLMAnalysis["LLM: Analyze logs and cycles"]
    LLMAnalysis --> ChatBreakdown["chat_with_breakdown()"]
    ChatBreakdown --> LLMConclusion["LLM: Bug found or add logs?"]
    
    LLMConclusion --> IsIdentified{"Conclusion?"}
    IsIdentified -->|PROBLEM_IDENTIFIED| SetFixStatus["Set AWAITING_BUG_FIX"]
    IsIdentified -->|ADD_LOGS| SetLogStatus["Set AWAITING_LOGGING"]
    SetFixStatus --> Done
    SetLogStatus --> Done
    
    AskTestFix --> SendTestInstructions["Send test instructions to UI"]
    SendTestInstructions --> UserTest["User tests fix"]
    UserTest --> IsFixed{"Bug fixed?"}
    IsFixed -->|Yes| CompleteIteration["complete_iteration()"]
    IsFixed -->|No, start pair| SetPairStatus["Set START_PAIR_PROGRAMMING"]
    IsFixed -->|No, continue| PrepareNext["Prepare next hunting cycle"]
    CompleteIteration --> Done
    SetPairStatus --> Done
    PrepareNext --> SetHuntingStatus["Set HUNTING_FOR_BUG"]
    SetHuntingStatus --> Done
    
    AskRepro --> SendReproInstructions["Send repro instructions"]
    SendReproInstructions --> UserRepro["User reproduces bug"]
    UserRepro --> HasFeedback{"Got feedback?"}
    HasFeedback -->|Yes| SetHuntingStatus
    HasFeedback -->|No, done| CompleteIteration
    HasFeedback -->|No, pair| SetPairStatus
    
    PairProg --> LLMExplain["LLM: Generate problem explanation"]
    LLMExplain --> LLMLogsData["LLM: Extract important logs"]
    LLMLogsData --> SendLogsToUI["ui.send_data_about_logs()"]
    SendLogsToUI --> PairLoop["Interactive Q&A loop"]
    PairLoop --> UserChoice{"User action"}
    UserChoice -->|Question| LLMAnswer["LLM: Answer question"]
    UserChoice -->|Tell me more| LLMMore["LLM: Elaborate"]
    UserChoice -->|Solution hint| HumanHint["Get hint from user"]
    UserChoice -->|Done| CompleteIteration
    LLMAnswer --> PairLoop
    LLMMore --> PairLoop
    HumanHint --> LLMInstructions["LLM: Generate fix instructions"]
    LLMInstructions --> UserApprove{"User approves?"}
    UserApprove -->|Yes| SetFixStatus
    UserApprove -->|No| PairLoop
```

**Iteration Status Transitions:**

```mermaid
stateDiagram-v2
    [*] --> HUNTING_FOR_BUG: User reports bug
    HUNTING_FOR_BUG --> AWAITING_LOGGING: Need more logs
    HUNTING_FOR_BUG --> AWAITING_BUG_FIX: Bug identified
    AWAITING_LOGGING --> AWAITING_BUG_REPRODUCTION: Logs added
    AWAITING_BUG_FIX --> AWAITING_USER_TEST: Fix implemented
    AWAITING_BUG_REPRODUCTION --> HUNTING_FOR_BUG: Bug reproduced
    AWAITING_USER_TEST --> [*]: Bug fixed
    AWAITING_USER_TEST --> HUNTING_FOR_BUG: Still broken
    AWAITING_USER_TEST --> START_PAIR_PROGRAMMING: User requests help
    AWAITING_BUG_REPRODUCTION --> START_PAIR_PROGRAMMING: User requests help
    START_PAIR_PROGRAMMING --> AWAITING_BUG_FIX: Solution found
    START_PAIR_PROGRAMMING --> [*]: User fixed it
```

Sources: [core/agents/bug_hunter.py:57-80](), [core/agents/bug_hunter.py:82-101](), [core/agents/bug_hunter.py:103-142](), [core/agents/bug_hunter.py:144-239](), [core/agents/bug_hunter.py:241-361](), [core/agents/bug_hunter.py:363-411]()

### Frontend

The Frontend agent builds and iterates on the user interface portion of the application, applying UI templates and implementing frontend features.

**Key responsibilities:**
- Building the initial frontend of the app
- Applying frontend templates
- Implementing UI changes based on user feedback
- Managing frontend iterations

**Key methods:**
- `init_frontend()`: Gets the initial app description and sets up the project
- `start_frontend()`: Builds the initial frontend implementation
- `continue_frontend()`: Continues building the frontend after the initial setup
- `iterate_frontend()`: Implements changes requested by the user

```mermaid
flowchart TD
    subgraph "Frontend Agent Flow"
        run["run()"]
        run --> check_epics{"Has epics?"}
        
        check_epics -->|No| init["init_frontend()"]
        check_epics -->|Yes| check_messages{"Epic has messages?"}
        
        check_messages -->|No| start["start_frontend()"]
        check_messages -->|Yes| check_done{"Frontend iteration done?"}
        
        check_done -->|No| continue["continue_frontend()"]
        check_done -->|Yes| iterate["iterate_frontend()"]
        
        init --> get_description["Ask for app description"]
        get_description --> get_auth["Ask about authentication needs"]
        get_auth --> setup["Set up project"]
        setup --> apply_template["apply_template()"]
        
        start --> build["Build initial frontend"]
        build --> process_response["process_response()"]
        
        continue --> continue_build["Continue frontend implementation"]
        continue_build --> process_response
        
        iterate --> check_user_done{"User done with UI?"}
        check_user_done -->|Yes| return_true["Return True (finished)"]
        check_user_done -->|No| get_changes["Get requested changes"]
        get_changes --> implement_changes["Implement changes"]
        implement_changes --> process_response
        
        process_response --> check_inputs{"Requires user input?"}
        check_inputs -->|Yes| input_required["Return AgentResponse.input_required()"]
        check_inputs -->|No| done["Return AgentResponse.done()"]
    end
```

Sources: [core/agents/frontend.py:17-32](), [core/agents/frontend.py:34-184]()

### Code Monkey

The Code Monkey agent implements and reviews code changes, creating or modifying files according to implementation plans.

**Key responsibilities:**
- Implementing code changes for tasks
- Reviewing code changes to ensure quality
- Describing files for documentation
- Generating diffs for code review

**Key methods:**
- `implement_changes()`: Implements code changes based on instructions
- `run_code_review()`: Reviews implemented changes for quality and correctness
- `describe_files()`: Generates descriptions for files
- `accept_changes()`: Accepts and applies code changes

```mermaid
flowchart TD
    subgraph "CodeMonkey Agent Flow"
        run["run()"]
        run --> check_describe{"prev_response is DESCRIBE_FILES?"}
        
        check_describe -->|Yes| describe["describe_files()"]
        check_describe -->|No| implement["implement_changes()"]
        
        implement --> review["run_code_review()"]
        review --> check_feedback{"Needs rework?"}
        
        check_feedback -->|Yes| implement
        check_feedback -->|No| check_accept{"Should accept?"}
        
        check_accept -->|Yes| accept["accept_changes()"]
        
        describe --> gather["Gather files without descriptions"]
        gather --> loop["For each file"]
        loop --> generate_desc["Generate file description"]
        generate_desc --> update_meta["Update file metadata"]
        update_meta --> loop
        
        accept --> save["Save file to StateManager"]
        save --> complete["Complete step"]
        complete --> check_input{"Requires input?"}
        
        check_input -->|Yes| input_required["Return AgentResponse.input_required()"]
        check_input -->|No| done["Return AgentResponse.done()"]
    end
```

Sources: [core/agents/code_monkey.py:58-67](), [core/agents/code_monkey.py:74-136](), [core/agents/code_monkey.py:206-225]()

## Common Agent Mixins

Agents use various mixins to share common functionality:

| Mixin | Purpose | Key Methods | Used By |
|-------|---------|-------------|---------|
| `RelevantFilesMixin` | Find files relevant to the current task | `get_relevant_files()` | TechLead, Developer |
| `ChatWithBreakdownMixin` | Interact with users about task breakdowns | `chat_with_breakdown()` | BugHunter, Developer, Troubleshooter |
| `IterationPromptMixin` | Find solutions to problems based on feedback | `find_solution()` | Troubleshooter |
| `FileDiffMixin` | Generate and analyze code diffs | `get_line_changes()` | Frontend, CodeMonkey |

Sources: [core/agents/mixins.py:53-92](), [core/agents/mixins.py:95-132](), [core/agents/mixins.py:135-191](), [core/agents/mixins.py:194-225]()

## Agent Communication

Agents communicate through a standardized response system:

```mermaid
flowchart TD
    subgraph "Agent Response Types"
        AgentResponse["AgentResponse"]
        
        AgentResponse --> AgentResponse.done["AgentResponse.done()\nTask completed successfully"]
        AgentResponse --> AgentResponse.input_required["AgentResponse.input_required()\nNeeds user input"]
        AgentResponse --> AgentResponse.external_docs_required["AgentResponse.external_docs_required()\nNeeds documentation"]
        AgentResponse --> AgentResponse.describe_files["AgentResponse.describe_files()\nNeeds file descriptions"]
        AgentResponse --> AgentResponse.update_specification["AgentResponse.update_specification()\nSpec needs updating"]
        AgentResponse --> AgentResponse.exit["AgentResponse.exit()\nTerminate processing"]
        
        AgentResponse.done --> Orchestrator["Orchestrator selects next agent"]
        AgentResponse.input_required --> HumanInput["HumanInput agent"]
        AgentResponse.external_docs_required --> ExternalDocs["ExternalDocs agent"]
        AgentResponse.describe_files --> CodeMonkey["CodeMonkey agent (describe_files)"]
        AgentResponse.update_specification --> SpecWriter["SpecWriter agent"]
        AgentResponse.exit --> EndProcess["End processing"]
    end
```

Sources: [core/agents/response.py]()

## State Management

All agents interact with a shared state through the `StateManager` class, which provides:

- Access to current project state (`current_state`)
- A way to make changes to that state (`next_state`)
- Persistence of state changes to database
- File system operations

The state contains information about:
- Epics
- Tasks
- Steps
- Iterations
- Files
- Knowledge base

Sources: [core/state/state_manager.py:30-47](), [core/state/state_manager.py:100-148]()

---

# Page: Agent Architecture and Base Classes

# Agent Architecture and Base Classes

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [core/agents/base.py](core/agents/base.py)
- [core/agents/bug_hunter.py](core/agents/bug_hunter.py)
- [core/agents/developer.py](core/agents/developer.py)
- [core/agents/mixins.py](core/agents/mixins.py)
- [core/agents/tech_lead.py](core/agents/tech_lead.py)
- [core/agents/troubleshooter.py](core/agents/troubleshooter.py)
- [core/llm/azure_client.py](core/llm/azure_client.py)
- [core/llm/base.py](core/llm/base.py)
- [core/llm/openai_client.py](core/llm/openai_client.py)
- [core/utils/__init__.py](core/utils/__init__.py)
- [core/utils/text.py](core/utils/text.py)
- [tests/agents/test_base.py](tests/agents/test_base.py)
- [tests/llm/test_openai.py](tests/llm/test_openai.py)
- [tests/ui/test_ipc_client.py](tests/ui/test_ipc_client.py)

</details>



This document describes the foundational architecture of the agent system in GPT Pilot, including the `BaseAgent` base class, agent lifecycle patterns, state management, and common reusable components (mixins). For information about specific agent implementations and their workflows, see [Planning Agents](#4.2), [Implementation Agents](#4.3), [Frontend Development Agent](#4.4), and [Quality Assurance Agents](#4.5). For details on LLM integration, see [LLM Client Architecture](#5.2).

---

## Overview of the Agent System

GPT Pilot uses a multi-agent architecture where each agent specializes in a specific phase of the software development lifecycle. All agents inherit from the `BaseAgent` base class, which provides a consistent interface for state management, UI communication, and LLM interaction.

### Agent Class Hierarchy

```mermaid
classDiagram
    class BaseAgent {
        +str agent_type
        +str display_name
        +StateManager state_manager
        +UIBase ui
        +ProcessManager process_manager
        +current_state ProjectState
        +next_state ProjectState
        +run() AgentResponse
        +send_message(str)
        +ask_question(str) UserInput
        +get_llm(name, stream_output) Callable
        +stream_handler(str)
        +error_handler(LLMError, str) bool
    }
    
    class TechLead {
        +agent_type = "tech-lead"
        +display_name = "Tech Lead"
        +run() AgentResponse
        +plan_epic(epic) AgentResponse
        +create_initial_project_epic()
        +ask_for_new_feature() AgentResponse
    }
    
    class Developer {
        +agent_type = "developer"
        +display_name = "Developer"
        +run() AgentResponse
        +breakdown_current_task() AgentResponse
        +breakdown_current_iteration() AgentResponse
        +ask_to_execute_task() bool
    }
    
    class BugHunter {
        +agent_type = "bug-hunter"
        +display_name = "Bug Hunter"
        +run() AgentResponse
        +check_logs(str) AgentResponse
        +ask_user_to_test(bool, bool) AgentResponse
        +start_pair_programming() AgentResponse
    }
    
    class Troubleshooter {
        +agent_type = "troubleshooter"
        +display_name = "Troubleshooter"
        +run() AgentResponse
        +create_iteration() AgentResponse
        +get_user_feedback() tuple
        +complete_task() AgentResponse
    }
    
    class RelevantFilesMixin {
        +get_relevant_files_parallel() AgentResponse
        +get_relevant_files(feedback, description, dir_type) list
    }
    
    class ChatWithBreakdownMixin {
        +chat_with_breakdown(convo, breakdown) str
    }
    
    class IterationPromptMixin {
        +find_solution(feedback, qa, solution, cycles) str
    }
    
    BaseAgent <|-- TechLead
    BaseAgent <|-- Developer
    BaseAgent <|-- BugHunter
    BaseAgent <|-- Troubleshooter
    
    RelevantFilesMixin <|-- TechLead
    RelevantFilesMixin <|-- Developer
    RelevantFilesMixin <|-- Troubleshooter
    
    ChatWithBreakdownMixin <|-- Developer
    ChatWithBreakdownMixin <|-- BugHunter
    
    IterationPromptMixin <|-- Troubleshooter
```

**Sources:** [core/agents/base.py:1-232](), [core/agents/tech_lead.py:1-464](), [core/agents/developer.py:1-485](), [core/agents/bug_hunter.py:1-412](), [core/agents/troubleshooter.py:1-435](), [core/agents/mixins.py:1-209]()

---

## BaseAgent Core Architecture

The `BaseAgent` class ([core/agents/base.py:15-232]()) serves as the foundation for all specialized agents. It provides essential infrastructure for state management, UI communication, and LLM interaction.

### Key Properties and Initialization

```mermaid
graph TB
    subgraph "BaseAgent Instance"
        AgentType["agent_type: str<br/>(class attribute)"]
        DisplayName["display_name: str<br/>(class attribute)"]
        StateManager["state_manager: StateManager"]
        UI["ui: UIBase"]
        ProcessManager["process_manager: ProcessManager"]
        UISource["ui_source: AgentSource"]
    end
    
    subgraph "State Access"
        CurrentState["current_state<br/>(read-only property)"]
        NextState["next_state<br/>(write-only property)"]
    end
    
    StateManager --> CurrentState
    StateManager --> NextState
    
    DisplayName --> UISource
    AgentType --> UISource
    UISource --> UI
```

**Sources:** [core/agents/base.py:15-44]()

| Property | Type | Description |
|----------|------|-------------|
| `agent_type` | `str` | Machine-readable identifier (e.g., `"tech-lead"`, `"developer"`) |
| `display_name` | `str` | Human-readable name (e.g., `"Tech Lead"`, `"Developer"`) |
| `state_manager` | `StateManager` | Manages project state and persistence |
| `ui` | `UIBase` | Interface for user communication (CLI or IPC) |
| `process_manager` | `ProcessManager` | Manages external processes (optional) |
| `ui_source` | `AgentSource` | Combines display_name and agent_type for UI routing |

**Sources:** [core/agents/base.py:20-44]()

### Agent Initialization Pattern

```python
def __init__(
    self,
    state_manager: StateManager,
    ui: UIBase,
    *,
    step: Optional[Any] = None,
    prev_response: Optional["AgentResponse"] = None,
    process_manager: Optional["ProcessManager"] = None,
    data: Optional[Any] = None,
    args: Optional[Any] = None,
):
```

All agents receive:
- **state_manager**: Provides access to current/next state and logging
- **ui**: Handles all user interaction (messages, questions, streaming)
- **step** (optional): Current execution step data
- **prev_response** (optional): Response from previous agent in chain
- **process_manager** (optional): For running external commands
- **data** (optional): Agent-specific data
- **args** (optional): CLI arguments

**Sources:** [core/agents/base.py:23-44]()

---

## Agent Lifecycle and Execution

Every agent must implement the `run()` method, which defines the agent's core behavior. The Orchestrator calls this method to execute the agent's logic.

### Agent Execution Flow

```mermaid
stateDiagram-v2
    [*] --> AgentInitialized: Orchestrator creates agent
    
    AgentInitialized --> ExecuteRun: Orchestrator calls run()
    
    ExecuteRun --> ReadState: Access current_state
    ReadState --> PerformLogic: Execute agent logic
    
    PerformLogic --> QueryLLM: get_llm() and call
    QueryLLM --> StreamToUI: stream_handler()
    StreamToUI --> LogRequest: state_manager.log_llm_request()
    
    PerformLogic --> AskUser: ask_question()
    AskUser --> LogUserInput: state_manager.log_user_input()
    
    PerformLogic --> WriteState: Modify next_state
    WriteState --> ReturnResponse: Return AgentResponse
    
    ReturnResponse --> [*]: Orchestrator processes response
    
    note right of ReadState
        current_state is read-only
        from last committed state
    end note
    
    note right of WriteState
        next_state is working copy
        committed after agent completes
    end note
```

**Sources:** [core/agents/base.py:46-54](), [core/agents/base.py:225-231]()

### The run() Method Contract

```python
async def run() -> AgentResponse:
    """
    Run the agent.
    
    :return: Response from the agent.
    """
    raise NotImplementedError()
```

The `run()` method must return an `AgentResponse` indicating the agent's completion status and next action. Common return types:

| Response Type | Description | Example Usage |
|---------------|-------------|---------------|
| `AgentResponse.done(self)` | Agent completed successfully | Most common case |
| `AgentResponse.exit(self)` | User requested exit | User cancels operation |
| `AgentResponse.external_docs_required(self)` | Need external documentation | Before complex task |
| `AgentResponse.update_specification(self, desc)` | Spec needs updating | Adding new feature |
| `AgentResponse.input_required(self, inputs)` | Template requires input | After applying template |

**Sources:** [core/agents/base.py:225-231](), [core/agents/tech_lead.py:59-90]()

---

## State Management: current_state vs next_state

GPT Pilot uses a **two-state transaction pattern** where agents read from `current_state` and write to `next_state`. This ensures atomic updates and enables rollback capabilities.

### State Access Pattern

```mermaid
graph TB
    subgraph "StateManager"
        CommittedState["Last Committed<br/>ProjectState"]
        WorkingCopy["Working Copy<br/>ProjectState"]
    end
    
    subgraph "BaseAgent Properties"
        CurrentState["current_state<br/>(property)"]
        NextState["next_state<br/>(property)"]
    end
    
    CommittedState -->|read-only| CurrentState
    WorkingCopy -->|read-write| NextState
    
    Agent["Agent Logic"] -->|"Reads from"| CurrentState
    Agent -->|"Writes to"| NextState
    
    NextState -->|"On commit"| CommittedState
    
    note1["Always safe to read<br/>Never modified during execution"]
    note2["Changes tracked<br/>Committed after AgentResponse.done()"]
    
    CurrentState -.-> note1
    NextState -.-> note2
```

**Sources:** [core/agents/base.py:46-54]()

### State Properties Implementation

```python
@property
def current_state(self) -> ProjectState:
    """Current state of the project (read-only)."""
    return self.state_manager.current_state

@property
def next_state(self) -> ProjectState:
    """Next state of the project (write-only)."""
    return self.state_manager.next_state
```

**Key Rules:**
1. **Never modify `current_state`** - It represents the last committed state
2. **Always write to `next_state`** - Changes are committed after agent completion
3. **Clone before modifying** - Use `.clone()` on nested objects if needed
4. **Flag modifications** - Call `.flag_tasks_as_modified()` or `.flag_epics_as_modified()` for SQLAlchemy tracking

**Sources:** [core/agents/base.py:46-54]()

### Common State Operations

```python
# Reading current task
current_task = self.current_state.current_task

# Modifying task status
self.next_state.current_task["status"] = TaskStatus.IN_PROGRESS
self.next_state.flag_tasks_as_modified()

# Adding new steps
self.next_state.steps = finished_steps + new_steps

# Setting action description
self.next_state.action = "Creating development plan"

# Completing iterations
self.next_state.complete_iteration()
```

**Sources:** [core/agents/developer.py:286-311](), [core/agents/tech_lead.py:92-110]()

---

## UI Communication Interface

Agents communicate with users through the `UIBase` abstraction, which supports both CLI and VSCode extension interfaces. The `BaseAgent` class provides convenience methods that automatically set the correct source and project state ID.

### Communication Methods

```mermaid
graph TB
    subgraph "BaseAgent Communication"
        SendMessage["send_message(message, extra_info)"]
        AskQuestion["ask_question(question, buttons, ...)"]
        StreamHandler["stream_handler(content)"]
        ErrorHandler["error_handler(error, message)"]
    end
    
    subgraph "UIBase Interface"
        UIMessage["ui.send_message()"]
        UIQuestion["ui.ask_question()"]
        UIStream["ui.send_stream_chunk()"]
        UIKeyExpired["ui.send_key_expired()"]
    end
    
    SendMessage -->|"Sets source & state_id"| UIMessage
    AskQuestion -->|"Sets source & state_id<br/>Logs to state_manager"| UIQuestion
    StreamHandler -->|"Sets source & state_id"| UIStream
    ErrorHandler -->|"Handles LLM errors"| UIKeyExpired
    
    UIMessage -->|"Routes to"| CLI["PlainConsoleUI"]
    UIMessage -->|"Routes to"| VSCode["IPCClientUI"]
    
    UIQuestion --> CLI
    UIQuestion --> VSCode
    
    UIStream --> CLI
    UIStream --> VSCode
```

**Sources:** [core/agents/base.py:56-173]()

### send_message() Method

Used to display informational messages to the user:

```python
await self.send_message("Creating the development plan ...")
await self.send_message("Found the bug. I'm attempting to fix it ...")
```

**Implementation:**
```python
async def send_message(self, message: str, extra_info: Optional[dict] = None):
    await self.ui.send_message(
        message + "\n", 
        source=self.ui_source, 
        project_state_id=str(self.current_state.id), 
        extra_info=extra_info
    )
```

**Sources:** [core/agents/base.py:56-68](), [core/agents/tech_lead.py:299](), [core/agents/bug_hunter.py:132]()

### ask_question() Method

Used to request input from the user with optional buttons and validation:

```python
response = await self.ask_question(
    "Do you want to add a new feature or implement something quickly?",
    buttons={
        "task": "Implement new feature",
        "end": "No, I'm done",
    },
    buttons_only=True,
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `question` | `str` | Question text to display |
| `buttons` | `dict[str, str]` | Button ID to label mapping |
| `default` | `str` | Default button ID if user presses enter |
| `buttons_only` | `bool` | Only show buttons, no text input |
| `allow_empty` | `bool` | Allow empty text response |
| `hint` | `str` | Additional context shown in popup |
| `initial_text` | `str` | Pre-filled text for editing |
| `extra_info` | `dict` | Extension-specific functionality flags |

**Returns:** `UserInput` object with:
- `.text` - User's text response
- `.button` - Button ID that was clicked
- `.cancelled` - Whether user cancelled the question

**Sources:** [core/agents/base.py:70-124](), [core/agents/tech_lead.py:171-180](), [core/agents/developer.py:438-445]()

---

## LLM Integration Pattern

Agents interact with LLMs through a unified client interface that handles streaming, error handling, and request logging automatically.

### LLM Request Flow

```mermaid
sequenceDiagram
    participant Agent
    participant BaseAgent
    participant BaseLLMClient
    participant LLMProvider as "LLM Provider<br/>(OpenAI/Anthropic/etc)"
    participant StateManager
    participant UI

    Agent->>BaseAgent: get_llm(name, stream_output=True)
    BaseAgent->>BaseAgent: Load LLMConfig for agent
    BaseAgent->>BaseLLMClient: Create client instance
    BaseAgent-->>Agent: Return client callable
    
    Agent->>Agent: Build AgentConvo
    Agent->>BaseLLMClient: llm(convo, parser=JSONParser)
    
    BaseLLMClient->>LLMProvider: Send request with messages
    
    loop For each chunk
        LLMProvider-->>BaseLLMClient: Stream chunk
        BaseLLMClient->>BaseAgent: stream_handler(chunk)
        BaseAgent->>UI: send_stream_chunk()
    end
    
    LLMProvider-->>BaseLLMClient: Complete response
    BaseLLMClient->>BaseLLMClient: Apply parser if provided
    
    BaseLLMClient-->>Agent: (response, request_log)
    Agent->>StateManager: log_llm_request(request_log)
```

**Sources:** [core/agents/base.py:175-223](), [core/llm/base.py:124-413]()

### get_llm() Method

The `get_llm()` method creates an agent-specific LLM client configured with the appropriate model and settings:

```python
def get_llm(self, name=None, stream_output=False, route=None) -> Callable:
    """
    Get a new instance of the agent-specific LLM client.
    
    :param name: Name of the agent for configuration (default: class name).
    :param stream_output: Whether to enable streaming output.
    :param route: Route information for message routing.
    :return: LLM client for the agent.
    """
```

**Usage Examples:**

```python
# Use default model for agent
llm = self.get_llm()
response = await llm(convo, parser=JSONParser(DevelopmentPlan))

# Use specific agent's configuration
llm = self.get_llm(TASK_BREAKDOWN_AGENT_NAME, stream_output=True)
response = await llm(convo)

# Temperature override
llm = self.get_llm()
response = await llm(convo, temperature=0)
```

**Sources:** [core/agents/base.py:175-223](), [core/agents/tech_lead.py:274-275](), [core/agents/developer.py:164-172]()

### LLM Client Configuration by Agent

Different agents can use different LLM models optimized for their tasks. Configuration is defined in `config.json`:

```python
# In TechLead agent
llm = self.get_llm(TECH_LEAD_PLANNING)  # Uses "TechLead" config
llm = self.get_llm(TECH_LEAD_EPIC_BREAKDOWN)  # Uses "TechLead.epic_breakdown" config

# In Developer agent
llm = self.get_llm(TASK_BREAKDOWN_AGENT_NAME)  # Uses "Developer" config
llm = self.get_llm(PARSE_TASK_AGENT_NAME)  # Uses "Developer.parse_task" config
```

**Sources:** [core/agents/tech_lead.py:274-275](), [core/agents/tech_lead.py:304-318](), [core/agents/developer.py:164](), [core/agents/developer.py:233](), [core/agents/developer.py:292]()

### stream_handler() and Error Handling

The base class provides two handlers that agents can override or use as-is:

**stream_handler()** - Called for each LLM response chunk:
```python
async def stream_handler(self, content: str):
    """Handle streamed response from the LLM."""
    route = getattr(self, "_current_route", None)
    await self.ui.send_stream_chunk(
        content, 
        source=self.ui_source, 
        project_state_id=str(self.current_state.id), 
        route=route
    )
    
    if content is None:
        await self.ui.send_message("", source=self.ui_source, ...)
```

**error_handler()** - Called when LLM requests fail:
```python
async def error_handler(self, error: LLMError, message: Optional[str] = None) -> bool:
    """
    Handle error responses from the LLM.
    
    :param error: The error type (KEY_EXPIRED, RATE_LIMITED, GENERIC_API_ERROR)
    :param message: Optional message to show.
    :return: Whether the request should be retried.
    """
```

**Sources:** [core/agents/base.py:126-173]()

---

## Agent Mixins and Reusable Components

GPT Pilot uses mixins to share common functionality across multiple agents without duplicating code. Mixins use Python's multiple inheritance to add capabilities to agents.

### Available Mixins

```mermaid
classDiagram
    class RelevantFilesMixin {
        <<mixin>>
        +get_relevant_files_parallel(feedback, description) AgentResponse
        +get_relevant_files(feedback, description, dir_type) list[str]
    }
    
    class ChatWithBreakdownMixin {
        <<mixin>>
        +chat_with_breakdown(convo, breakdown) str
    }
    
    class IterationPromptMixin {
        <<mixin>>
        +find_solution(feedback, qa, solution, cycles) str
    }
    
    class FileDiffMixin {
        <<mixin>>
        +get_line_changes(old_content, new_content) tuple[int, int]
    }
    
    note for RelevantFilesMixin "Filters large codebase to\nonly relevant files for context"
    note for ChatWithBreakdownMixin "Interactive refinement of\nLLM-generated plans"
    note for IterationPromptMixin "Generate solutions based on\nuser feedback and bug history"
    note for FileDiffMixin "Calculate diff statistics\nfor file modifications"
```

**Sources:** [core/agents/mixins.py:1-209]()

### RelevantFilesMixin

**Purpose:** Filters the project's files to include only those relevant to the current task, preventing token limit issues with large codebases.

**Implementation:**
```python
class RelevantFilesMixin:
    async def get_relevant_files_parallel(
        self, 
        user_feedback: Optional[str] = None, 
        solution_description: Optional[str] = None
    ) -> AgentResponse:
        # Splits files into client/server and processes in parallel
        tasks = [
            self.get_relevant_files(..., dir_type="client"),
            self.get_relevant_files(..., dir_type="server"),
        ]
        responses = await asyncio.gather(*tasks)
        relevant_files = [item for sublist in responses for item in sublist]
        
        # Update both current and next state
        self.current_state.relevant_files = relevant_files
        self.next_state.relevant_files = relevant_files
```

**Used by:** `TechLead`, `Developer`, `Troubleshooter`

**Usage Example:**
```python
# In Developer.breakdown_current_task()
await self.get_relevant_files_parallel()

# In Troubleshooter with user feedback
await self.get_relevant_files_parallel(user_feedback=bug_report)
```

**Sources:** [core/agents/mixins.py:122-189](), [core/agents/developer.py:224](), [core/agents/tech_lead.py:302](), [core/agents/troubleshooter.py:321]()

### ChatWithBreakdownMixin

**Purpose:** Allows interactive refinement of LLM-generated implementation plans by letting users review and request changes before execution.

**Implementation:**
```python
class ChatWithBreakdownMixin:
    async def chat_with_breakdown(self, convo: AgentConvo, breakdown: str) -> str:
        llm = self.get_llm(TASK_BREAKDOWN_AGENT_NAME, stream_output=True)
        while True:
            await self.ui.send_project_stage({
                "stage": ProjectStage.BREAKDOWN_CHAT,
                "agent": self.agent_type,
            })
            
            if self.state_manager.auto_confirm_breakdown:
                break
            
            chat = await self.ask_question(
                MIX_BREAKDOWN_CHAT_PROMPT,
                buttons={"yes": "Yes, looks good!"},
                default="yes",
            )
            if chat.button == "yes":
                break
            
            # User provided feedback, regenerate
            convo.user(chat.text)
            breakdown = await llm(convo)
            convo.assistant(breakdown)
        
        return breakdown
```

**Used by:** `Developer`, `BugHunter`

**Usage Example:**
```python
# After LLM generates implementation steps
response = await llm(convo)
convo.assistant(response)

# Allow user to review and refine
response = await self.chat_with_breakdown(convo, response)
```

**Sources:** [core/agents/mixins.py:37-79](), [core/agents/developer.py:284](), [core/agents/bug_hunter.py:114]()

### IterationPromptMixin

**Purpose:** Generates implementation solutions for bug fixes and feature changes based on user feedback, previous attempts, and bug hunting cycles.

**Implementation:**
```python
class IterationPromptMixin:
    async def find_solution(
        self,
        user_feedback: str,
        *,
        user_feedback_qa: Optional[list[str]] = None,
        next_solution_to_try: Optional[str] = None,
        bug_hunting_cycles: Optional[dict] = None,
    ) -> str:
        llm = self.get_llm(TROUBLESHOOTER_BUG_REPORT, stream_output=True)
        convo = AgentConvo(self).template(
            "iteration",
            user_feedback=user_feedback,
            user_feedback_qa=user_feedback_qa,
            next_solution_to_try=next_solution_to_try,
            bug_hunting_cycles=bug_hunting_cycles,
            test_instructions=json.loads(self.current_state.current_task.get("test_instructions", "[]")),
        )
        llm_solution = await llm(convo)
        llm_solution = await self.chat_with_breakdown(convo, llm_solution)
        return llm_solution
```

**Used by:** `Troubleshooter`, `ProblemSolver`

**Sources:** [core/agents/mixins.py:82-119](), [core/agents/troubleshooter.py:48-61]()

---

## Agent Type Registration

Each agent must define two class attributes that identify it within the system:

```python
class TechLead(RelevantFilesMixin, BaseAgent):
    agent_type = "tech-lead"        # Machine-readable identifier
    display_name = "Tech Lead"       # Human-readable name
```

**Agent Type Registry:**

| Agent Class | agent_type | display_name | Primary Responsibility |
|-------------|------------|--------------|------------------------|
| `SpecWriter` | `"spec-writer"` | `"Spec Writer"` | Requirements gathering |
| `Architect` | `"architect"` | `"Architect"` | Tech stack selection |
| `TechLead` | `"tech-lead"` | `"Tech Lead"` | Epic and task planning |
| `Developer` | `"developer"` | `"Developer"` | Task breakdown into steps |
| `CodeMonkey` | `"code-monkey"` | `"Code Monkey"` | Code implementation |
| `Frontend` | `"frontend"` | `"Frontend"` | UI development |
| `Troubleshooter` | `"troubleshooter"` | `"Troubleshooter"` | Testing and user feedback |
| `BugHunter` | `"bug-hunter"` | `"Bug Hunter"` | Bug investigation and fixing |

**Sources:** [core/agents/tech_lead.py:55-57](), [core/agents/developer.py:91-93](), [core/agents/bug_hunter.py:57-59](), [core/agents/troubleshooter.py:35-37]()

---

## Common Agent Patterns

### Pattern 1: Conditional Logic in run()

Most agents use the `run()` method to route to different workflows based on state:

```python
async def run(self) -> AgentResponse:
    # Check for special cases first
    if self.current_state.current_step and self.current_state.current_step.get("type") == "utility_function":
        return await self.update_knowledge_base()
    
    # Check for incomplete work
    if not self.current_state.unfinished_tasks:
        return AgentResponse.done(self)
    
    # Route to appropriate workflow
    if self.current_state.unfinished_iterations:
        return await self.breakdown_current_iteration()
    else:
        return await self.breakdown_current_task()
```

**Sources:** [core/agents/developer.py:95-119](), [core/agents/troubleshooter.py:39-46](), [core/agents/bug_hunter.py:61-80]()

### Pattern 2: Progressive Message Updates

Agents typically inform users of their progress:

```python
async def plan_epic(self, epic) -> AgentResponse:
    await self.send_message("Creating the development plan ...")
    
    # ... LLM call to generate plan ...
    
    await self.send_message("Creating tasks ...")
    
    # ... Process tasks in parallel ...
    
    return AgentResponse.done(self)
```

**Sources:** [core/agents/tech_lead.py:296-368]()

### Pattern 3: Two-Phase Operations (LLM + Parse)

Many agents use a two-step pattern: first generate with streaming, then parse:

```python
# Phase 1: Generate with streaming for user feedback
llm = self.get_llm(TASK_BREAKDOWN_AGENT_NAME, stream_output=True)
await self.ui.start_breakdown_stream()
await self.ui.set_important_stream()

response: str = await llm(convo)  # Unstructured response
convo.assistant(response)

# Phase 2: Parse into structured format
llm = self.get_llm(PARSE_TASK_AGENT_NAME)
convo_parse = AgentConvo(self).template("parse_task", ...).require_schema(TaskSteps)
parsed_response: TaskSteps = await llm(convo_parse, parser=JSONParser(TaskSteps), temperature=0)
```

**Sources:** [core/agents/developer.py:228-296]()

### Pattern 4: Flag Modifications for Persistence

After modifying state collections, agents must flag them for SQLAlchemy:

```python
# Modify tasks
self.next_state.tasks[current_task_index] = {
    **current_task,
    "instructions": response,
}
# MUST flag as modified
self.next_state.flag_tasks_as_modified()

# Modify epics
self.next_state.epics = self.current_state.epics + [new_epic]
# MUST flag as modified
self.next_state.flag_epics_as_modified()
```

**Sources:** [core/agents/developer.py:286-291](), [core/agents/tech_lead.py:438-439]()

### Pattern 5: Async Task Management

Some agents need to run background tasks while executing:

```python
async def run(self) -> AgentResponse:
    current_iteration = self.current_state.current_iteration
    
    # Start async task if not already running
    if "bug_reproduction_description" not in current_iteration:
        if not self.state_manager.async_tasks:
            self.state_manager.async_tasks = []
            self.state_manager.async_tasks.append(
                asyncio.create_task(self.get_bug_reproduction_instructions())
            )
    
    # ... continue with main logic ...

async def async_task_finish(self):
    """Wait for async tasks to complete before proceeding."""
    if self.state_manager.async_tasks:
        if not self.state_manager.async_tasks[-1].done():
            await self.send_message("Waiting for the bug reproduction instructions...")
            await self.state_manager.async_tasks[-1]
        self.state_manager.async_tasks = []
```

**Sources:** [core/agents/bug_hunter.py:61-68](), [core/agents/bug_hunter.py:393-399]()

---

## Testing Agent Implementations

### Unit Testing Pattern

Agent tests typically mock the `StateManager` and `UIBase` dependencies:

```python
class AgentUnderTest(BaseAgent):
    agent_type = "test-agent"
    display_name = "Test Agent"

@pytest.mark.asyncio
async def test_send_message():
    ui = MagicMock(spec=UIBase)
    sm = AsyncMock()
    agent = AgentUnderTest(sm, ui)
    
    await agent.send_message("Hello, world!")
    ui.send_message.assert_called_once_with(
        "Hello, world!\n",
        source=agent.ui_source,
        project_state_id=str(agent.current_state.id),
        extra_info=None,
    )
```

**Key Testing Considerations:**
1. Mock `state_manager.current_state` and `state_manager.next_state`
2. Mock `ui.send_message()`, `ui.ask_question()`, `ui.send_stream_chunk()`
3. Verify LLM requests are logged with `state_manager.log_llm_request()`
4. Verify user inputs are logged with `state_manager.log_user_input()`

**Sources:** [tests/agents/test_base.py:1-93]()

---

## Summary

The agent architecture in GPT Pilot provides a robust foundation for building specialized AI agents with:

1. **Consistent Interface** - `BaseAgent` provides uniform patterns for state access, UI communication, and LLM interaction
2. **State Transaction Safety** - Two-state pattern (`current_state`/`next_state`) ensures atomic updates
3. **Flexible LLM Integration** - Per-agent model configuration with automatic streaming and error handling
4. **Reusable Components** - Mixins enable code sharing across agents without duplication
5. **Type-Safe Responses** - `AgentResponse` enum provides clear agent completion states
6. **Comprehensive Logging** - All LLM requests and user interactions are automatically persisted

Agents follow a simple lifecycle: receive state, perform work (possibly with LLM/user interaction), update state, and return a response. The Orchestrator handles state commits and determines which agent to run next based on the response.

**Sources:** [core/agents/base.py:1-232](), [core/agents/mixins.py:1-209](), [core/agents/tech_lead.py:1-464](), [core/agents/developer.py:1-485]()

---

# Page: Planning Agents

# Planning Agents

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [core/agents/architect.py](core/agents/architect.py)
- [core/agents/bug_hunter.py](core/agents/bug_hunter.py)
- [core/agents/developer.py](core/agents/developer.py)
- [core/agents/frontend.py](core/agents/frontend.py)
- [core/agents/mixins.py](core/agents/mixins.py)
- [core/agents/orchestrator.py](core/agents/orchestrator.py)
- [core/agents/spec_writer.py](core/agents/spec_writer.py)
- [core/agents/tech_lead.py](core/agents/tech_lead.py)
- [core/agents/troubleshooter.py](core/agents/troubleshooter.py)
- [core/prompts/developer/parse_task.prompt](core/prompts/developer/parse_task.prompt)
- [core/prompts/partials/project_tasks.prompt](core/prompts/partials/project_tasks.prompt)
- [core/prompts/tech-lead/epic_breakdown.prompt](core/prompts/tech-lead/epic_breakdown.prompt)
- [core/prompts/tech-lead/plan.prompt](core/prompts/tech-lead/plan.prompt)

</details>



## Purpose and Scope

This document describes the three planning agents in GPT Pilot: **SpecWriter**, **Architect**, and **TechLead**. These agents work sequentially during the planning phase to transform user requirements into a detailed development plan:

1. **SpecWriter** - Gathers and refines project requirements
2. **Architect** - Determines technical architecture and technology stack
3. **TechLead** - Creates epics and breaks them down into implementable tasks

Together, these agents establish a comprehensive development plan before implementation begins.

For information about implementation agents, see [Implementation Agents](#4.3). For the overall agent system architecture, see [Agent Architecture](#4.1).

## Overview

**Planning Phase Architecture**

```mermaid
flowchart TD
    User(["User<br/>Initial Description"])
    SpecWriter["SpecWriter<br/>spec_writer.py"]
    Architect["Architect<br/>architect.py"]
    TechLead["TechLead<br/>tech_lead.py"]
    Developer["Developer Agent<br/>(Implementation)"]
    
    User -->|"Project Description"| SpecWriter
    SpecWriter -->|"Specification<br/>(description, complexity)"| Architect
    Architect -->|"Architecture<br/>(templates, dependencies)"| TechLead
    TechLead -->|"Epics & Tasks<br/>(development plan)"| Developer
    
    subgraph "Planning Phase"
        SpecWriter
        Architect
        TechLead
    end
    
    subgraph "Implementation Phase"
        Developer
    end
```

Sources: [core/agents/spec_writer.py:19-33](), [core/agents/architect.py:95-122](), [core/agents/tech_lead.py:55-90]()

The planning agents transform user requirements into an actionable development plan through a three-stage process:

1. **SpecWriter** analyzes the user's project description and creates a comprehensive specification, including complexity assessment
2. **Architect** determines the technical architecture, selects project templates, and identifies system/package dependencies
3. **TechLead** breaks the specification down into epics (high-level features) and tasks (implementable units of work)

This planning phase ensures development has clear direction before any code is written.

## SpecWriter Agent

The SpecWriter agent is the entry point for all projects, transforming user descriptions into detailed specifications. It handles both initial project setup and feature requests during development iterations.

**SpecWriter Workflow**

```mermaid
flowchart TD
    Start(["User Input"])
    CheckMode{"New Project or<br/>Feature Request?"}
    
    InitSpec["initialize_spec_and_project()"]
    GetUserDesc["Ask Question:<br/>'Describe the app'"]
    BuildSpec["LLM: build_full_specification<br/>(SPEC_WRITER_AGENT_NAME)"]
    ProjectName["LLM: Generate project_name"]
    
    ChangeSpec["change_spec()"]
    AskSatisfied["Ask: 'Satisfied with<br/>description?'"]
    AddDetails["Ask: 'What to add?'"]
    RefineSpec["LLM: add_to_specification"]
    
    UpdateSpec["update_spec()"]
    FeatureDesc["Get feature_description<br/>from iteration/response"]
    AddFeature["LLM: add_new_feature"]
    UserConfirm["Ask: 'Accept changes?'"]
    
    CheckAuth["LLM: need_auth prompt"]
    CheckComplexity["check_prompt_complexity()"]
    
    Start --> CheckMode
    CheckMode -->|"New"| InitSpec
    CheckMode -->|"Change Spec"| ChangeSpec
    CheckMode -->|"Feature"| UpdateSpec
    
    InitSpec --> GetUserDesc
    GetUserDesc --> BuildSpec
    BuildSpec --> ProjectName
    ProjectName --> ChangeSpec
    
    ChangeSpec --> AskSatisfied
    AskSatisfied -->|"No"| AddDetails
    AddDetails --> RefineSpec
    RefineSpec --> AskSatisfied
    AskSatisfied -->|"Yes"| CheckAuth
    
    UpdateSpec --> FeatureDesc
    FeatureDesc --> AddFeature
    AddFeature --> UserConfirm
    
    CheckAuth --> CheckComplexity
    UserConfirm --> CheckComplexity
    CheckComplexity --> Done(["specification<br/>committed"])
```

Sources: [core/agents/spec_writer.py:23-343]()

### Key Responsibilities

| Responsibility | Method | Description |
|---------------|---------|-------------|
| **Initial Specification** | `initialize_spec_and_project()` | Creates specification from user's initial description |
| **Specification Refinement** | `change_spec()` | Allows user to iteratively improve the specification |
| **Feature Updates** | `update_spec()` | Updates specification when new features are requested |
| **Complexity Assessment** | `check_prompt_complexity()` | Categorizes project as "simple", "moderate", or "hard" |
| **Authentication Detection** | LLM prompt: `need_auth` | Determines if project requires authentication |
| **Template Application** | `apply_template()` | Applies project templates based on user options |

Sources: [core/agents/spec_writer.py:63-357]()

### State Updates

The SpecWriter updates the `ProjectState` with:

- `specification.description` - LLM-enhanced project description
- `specification.original_description` - User's raw input
- `specification.complexity` - Complexity assessment ("simple", "moderate", "hard")
- `specification.template_summary` - Summary of applied templates
- `knowledge_base.user_options['auth']` - Whether authentication is needed
- `knowledge_base.user_options['jwt_secret']` - Generated JWT secret (if auth enabled)

Sources: [core/agents/spec_writer.py:148-161](), [core/agents/spec_writer.py:246-263]()

### Complexity Assessment

The SpecWriter uses an LLM call to categorize project complexity:

| Complexity | Impact |
|-----------|--------|
| **"simple"** | Single epic/task, minimal breakdown |
| **"moderate"** | Multiple epics, standard breakdown |
| **"hard"** | Comprehensive planning, external docs may be required |

The complexity value influences how TechLead breaks down the project and whether Developer agent requests external documentation.

Sources: [core/agents/spec_writer.py:345-356](), [core/db/models/specification.py]()

## Architect Agent

The Architect agent determines the technical foundation for the project by selecting technologies, templates, and dependencies. It bridges the specification to concrete technical decisions.

**Architect Workflow**

```mermaid
flowchart TD
    Start(["specification from<br/>SpecWriter"])
    CheckExample{"example_project<br/>specified?"}
    
    PrepareExample["prepare_example_project()<br/>Load from EXAMPLE_PROJECTS"]
    
    SelectTemplates["select_templates()<br/>LLM: select_templates"]
    TemplateConvo["TemplateSelection schema:<br/>architecture, template"]
    
    PlanArch["plan_architecture()"]
    Technologies["LLM: technologies prompt<br/>Architecture schema"]
    
    CheckCompat["check_compatibility()<br/>Warn if using unsupported tech"]
    
    CheckSysDeps["check_system_dependencies()<br/>Test each dependency"]
    RunTest["process_manager.run_command(dep['test'])"]
    AskInstall["If not installed:<br/>Ask user to install"]
    
    Start --> CheckExample
    CheckExample -->|"Yes"| PrepareExample
    CheckExample -->|"No"| PlanArch
    
    PlanArch --> SelectTemplates
    SelectTemplates --> TemplateConvo
    TemplateConvo --> Technologies
    Technologies --> CheckCompat
    
    PrepareExample --> CheckSysDeps
    CheckCompat --> CheckSysDeps
    CheckSysDeps --> RunTest
    RunTest --> AskInstall
    AskInstall --> Done(["Architecture complete<br/>Pass to TechLead"])
```

Sources: [core/agents/architect.py:99-267]()

### Pydantic Models

The Architect uses strongly-typed schemas for LLM responses:

| Model | Fields | Purpose |
|-------|--------|---------|
| `AppType` (Enum) | `WEB`, `API`, `MOBILE`, `DESKTOP`, `CLI` | Categorizes application type |
| `SystemDependency` | `name`, `description`, `test`, `required_locally` | System-level requirements (Node.js, Python, etc.) |
| `PackageDependency` | `name`, `description` | Framework/library dependencies (Express, React, etc.) |
| `Architecture` | `app_type`, `system_dependencies`, `package_dependencies` | Complete architecture definition |
| `TemplateSelection` | `architecture`, `template` | Selected project template |

Sources: [core/agents/architect.py:29-93]()

### State Updates

The Architect updates the `specification` object with:

- `architecture` - High-level architecture description (string)
- `templates` - Dictionary mapping template names to options
- `system_dependencies` - List of system dependencies (serialized `SystemDependency` models)
- `package_dependencies` - List of package dependencies (serialized `PackageDependency` models)

Example:
```python
# Stored in ProjectState.specification
specification.architecture = "React frontend with Node.js Express backend"
specification.templates = {"vite_react": {...}}
specification.system_dependencies = [
    {"name": "Node.js", "test": "node --version", "installed": True, ...}
]
```

Sources: [core/agents/architect.py:193-197](), [core/agents/architect.py:227-235]()

### Compatibility Warnings

The Architect warns users about technologies that GPT Pilot doesn't officially support:

- **System Dependencies**: Docker, Kubernetes, Microservices
- **Frontend Frameworks**: Next.js, Vue, Svelte, Angular

These warnings don't block development but inform users they may encounter issues.

Sources: [core/agents/architect.py:22-24](), [core/agents/architect.py:199-225]()

## TechLead Agent

The TechLead agent is responsible for transforming the specification and architecture into an actionable development plan by creating **epics** (high-level features) and **tasks** (implementable units).

**TechLead Workflow**

```mermaid
flowchart TD
    Start(["Run TechLead"])
    CheckEpics{"len(epics) == 1?"}
    
    CreateInitial["create_initial_project_epic()"]
    InitialEpic["Create epic with:<br/>name='Initial Project'<br/>description=specification.description"]
    
    CheckCurrentEpic{"current_epic exists?"}
    PlanEpic["plan_epic(current_epic)"]
    
    AskFeature["ask_for_new_feature()"]
    UserChoice{"User wants to<br/>add feature?"}
    UpdateSpec["Return:<br/>AgentResponse.update_specification"]
    QuickTask["Create quick task<br/>in existing epic"]
    
    GetRelevantFiles["get_relevant_files_parallel()<br/>(if feature)"]
    
    PlanEpicLLM["LLM: plan prompt<br/>(TECH_LEAD_PLANNING)<br/>DevelopmentPlan schema"]
    
    CreateSubEpics["Create sub_epics array<br/>in current_epic"]
    
    ProcessEpics["For each sub_epic:<br/>process_epic()"]
    EpicBreakdown["LLM: epic_breakdown<br/>(TECH_LEAD_EPIC_BREAKDOWN)<br/>EpicPlan schema"]
    CreateTasks["Create tasks with:<br/>- description<br/>- related_api_endpoints<br/>- pre_breakdown_testing_instructions"]
    
    UpdateEpicsAndTasks["update_epics_and_tasks()<br/>Add auth task if needed"]
    
    Start --> CheckEpics
    CheckEpics -->|"Yes"| CreateInitial
    CreateInitial --> InitialEpic
    InitialEpic --> Done1(["Done"])
    
    CheckEpics -->|"No"| CheckCurrentEpic
    CheckCurrentEpic -->|"Yes"| GetRelevantFiles
    GetRelevantFiles --> PlanEpic
    CheckCurrentEpic -->|"No"| AskFeature
    
    PlanEpic --> PlanEpicLLM
    PlanEpicLLM --> CreateSubEpics
    CreateSubEpics --> ProcessEpics
    ProcessEpics --> EpicBreakdown
    EpicBreakdown --> CreateTasks
    CreateTasks --> UpdateEpicsAndTasks
    UpdateEpicsAndTasks --> Done2(["Done"])
    
    AskFeature --> UserChoice
    UserChoice -->|"New Feature"| UpdateSpec
    UserChoice -->|"Quick Task"| QuickTask
    UserChoice -->|"Done"| Exit(["Exit"])
    UpdateSpec --> Done3(["Triggers<br/>SpecWriter"])
    QuickTask --> Done3
```

Sources: [core/agents/tech_lead.py:59-368]()

### Epic and Task Hierarchy

The TechLead creates a hierarchical structure:

```mermaid
flowchart TD
    Epic["Epic<br/>(High-level feature)"]
    SubEpic1["Sub-Epic 1"]
    SubEpic2["Sub-Epic 2"]
    SubEpic3["Sub-Epic 3"]
    
    Task1["Task 1<br/>(Implementable unit)"]
    Task2["Task 2"]
    Task3["Task 3"]
    Task4["Task 4"]
    Task5["Task 5"]
    
    Epic --> SubEpic1
    Epic --> SubEpic2
    Epic --> SubEpic3
    
    SubEpic1 --> Task1
    SubEpic1 --> Task2
    SubEpic2 --> Task3
    SubEpic3 --> Task4
    SubEpic3 --> Task5
    
    Task1 -.->|"passes to"| Developer["Developer Agent"]
    
    style Epic fill:#e1f5ff
    style SubEpic1 fill:#fff4e1
    style SubEpic2 fill:#fff4e1
    style SubEpic3 fill:#fff4e1
    style Task1 fill:#e8f5e9
```

Sources: [core/agents/tech_lead.py:296-367]()

### Key Data Structures

The TechLead uses Pydantic models to structure the development plan:

| Model | Fields | Purpose |
|-------|--------|---------|
| `APIEndpoint` | `description`, `method`, `endpoint`, `request_body`, `response_body` | Defines an API endpoint to implement |
| `Epic` | `description` | High-level feature description |
| `Task` | `description`, `related_api_endpoints`, `testing_instructions` | Unit of work for Developer |
| `DevelopmentPlan` | `plan: list[Epic]` | Complete list of epics |
| `EpicPlan` | `plan: list[Task]` | Complete list of tasks for an epic |

Sources: [core/agents/tech_lead.py:29-52]()

### Epic Planning Process

The `plan_epic()` method breaks down an epic into tasks:

1. **Get Relevant Files** (if feature): Calls `get_relevant_files_parallel()` to identify files affected by the feature
2. **LLM Call - Development Plan**: Uses `plan` prompt with `TECH_LEAD_PLANNING` LLM to generate list of epics
3. **Create Sub-Epics**: Stores epics as `sub_epics` array in the current epic
4. **Parallel Epic Processing**: Calls `process_epic()` for each sub-epic in parallel using `asyncio.gather()`
5. **LLM Call - Epic Breakdown**: Each `process_epic()` uses `epic_breakdown` prompt to generate tasks
6. **Create Tasks**: Stores tasks with descriptions, API endpoints, and testing instructions
7. **Update Epic/Task State**: Calls `update_epics_and_tasks()` to add special tasks (e.g., authentication)

Sources: [core/agents/tech_lead.py:296-368](), [core/prompts/tech-lead/plan.prompt](), [core/prompts/tech-lead/epic_breakdown.prompt]()

### Task Structure

Each task created by TechLead contains:

```python
{
    "id": uuid4().hex,
    "description": "Combined description from all epic tasks",
    "instructions": None,  # Filled by Developer agent
    "pre_breakdown_testing_instructions": "How to test this task",
    "status": TaskStatus.TODO,
    "sub_epic_id": epic_number,
    "related_api_endpoints": [
        {
            "description": "API endpoint description",
            "method": "POST",
            "endpoint": "/api/users",
            "request_body": {"email": "string", ...},
            "response_body": {"id": "integer", ...}
        }
    ]
}
```

Sources: [core/agents/tech_lead.py:277-294]()

### Special Case: Authentication Task

If the project requires authentication (`knowledge_base.user_options['auth'] == True`), TechLead inserts a hardcoded authentication task at the beginning of the task list:

- **Description**: "Implement and test Login and Register pages"
- **API Endpoints**: `/api/auth/register`, `/api/auth/login`
- **Status**: `TaskStatus.TODO`
- **Flag**: `hardcoded: True` (prevents user from skipping it)

This ensures authentication is implemented before other features.

Sources: [core/agents/tech_lead.py:381-439]()

### Feature Request Flow

After completing all tasks, TechLead asks the user if they want to add features:

1. **Button Options**:
   - "Implement new feature" - Adds a new epic, triggers SpecWriter to update specification
   - (Hidden: "No, I'm done" - Exits)

2. **New Feature**: Creates a new epic and returns `AgentResponse.update_specification()`, which triggers SpecWriter to refine the feature description

3. **Quick Task**: Creates a single task in the last epic without creating a new epic, useful for small changes

Sources: [core/agents/tech_lead.py:146-260]()

## Workflow and Iteration

The agents operate in both initial project setup and during feature iterations:

### Initial Project Flow

1. User provides a project description
2. Spec Writer analyzes and refines the description
3. Architect plans the architecture and selects technologies
4. Project proceeds to development phase (Tech Lead agent)

### Feature Iteration Flow

1. User requests a new feature
2. Spec Writer updates the specification to incorporate the feature
3. Project proceeds to implementation of the feature

```mermaid
flowchart TD
    Start(["Project Start"])
    UserDesc["User Provides Project Description"]
    SpecWriter["Spec Writer Agent"]
    Architect["Architect Agent"]
    Development["Development Phase"]
    
    Feature(["Feature Request"])
    SpecUpdate["Spec Writer Updates Specification"]
    Implementation["Feature Implementation"]
    
    Start --> UserDesc
    UserDesc --> SpecWriter
    SpecWriter --> Architect
    Architect --> Development
    
    Feature --> SpecUpdate
    SpecUpdate --> Implementation
    
    subgraph "Initial Project Setup"
        UserDesc
        SpecWriter
        Architect
    end
    
    subgraph "Feature Iteration"
        Feature
        SpecUpdate
        Implementation
    end
```

Sources: [core/agents/spec_writer.py:26-33](), [core/db/models/project_state.py:126-139]()

## Conclusion

The Spec Writer and Architect agents form the foundation of project development in GPT Pilot by:

1. Taking user requirements and transforming them into comprehensive specifications
2. Determining the appropriate technologies and architecture for the project
3. Setting up the infrastructure for subsequent development stages

These agents ensure that the project has a solid foundation before development begins, helping to reduce errors and rework in later stages.

---

# Page: Implementation Agents

# Implementation Agents

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [core/agents/bug_hunter.py](core/agents/bug_hunter.py)
- [core/agents/code_monkey.py](core/agents/code_monkey.py)
- [core/agents/developer.py](core/agents/developer.py)
- [core/agents/mixins.py](core/agents/mixins.py)
- [core/agents/tech_lead.py](core/agents/tech_lead.py)
- [core/agents/troubleshooter.py](core/agents/troubleshooter.py)
- [core/prompts/bug-hunter/iteration.prompt](core/prompts/bug-hunter/iteration.prompt)
- [core/prompts/bug-hunter/log_data.prompt](core/prompts/bug-hunter/log_data.prompt)
- [core/prompts/developer/breakdown.prompt](core/prompts/developer/breakdown.prompt)
- [core/prompts/problem-solver/get_alternative_solutions.prompt](core/prompts/problem-solver/get_alternative_solutions.prompt)
- [core/prompts/troubleshooter/iteration.prompt](core/prompts/troubleshooter/iteration.prompt)

</details>



## Purpose and Scope

This page documents the **Developer** and **CodeMonkey** agents, which form the core implementation layer of GPT Pilot's code generation pipeline. These agents are responsible for converting high-level task descriptions into executable implementation steps and then generating the actual code files.

The Developer agent ([core/agents/developer.py]()) breaks down tasks into structured step-by-step plans, while the CodeMonkey agent ([core/agents/code_monkey.py]()) executes those plans by generating and modifying code files. For information about task planning and epic creation, see [Planning Agents](#4.2). For quality assurance and bug fixing, see [Quality Assurance Agents](#4.5).

**Sources:** [core/agents/developer.py:1-485](), [core/agents/code_monkey.py:1-233]()

---

## Implementation Flow Overview

The implementation workflow follows a clear producer-consumer pattern where Developer produces implementation plans and CodeMonkey consumes them to generate code:

```mermaid
graph TB
    TechLead["TechLead Agent<br/>(creates tasks)"]
    Developer["Developer Agent<br/>developer.py"]
    CodeMonkey["CodeMonkey Agent<br/>code_monkey.py"]
    StateManager["StateManager<br/>(state persistence)"]
    
    TechLead -->|"tasks[]"| Developer
    
    subgraph "Developer Responsibilities"
        AskExecute["ask_to_execute_task()<br/>User approval"]
        BreakdownTask["breakdown_current_task()<br/>LLM with breakdown.prompt"]
        ParseSteps["parse_task.prompt<br/>→ TaskSteps schema"]
        SetSteps["set_next_steps()<br/>Save to state.steps"]
    end
    
    subgraph "CodeMonkey Responsibilities"
        ImplementChanges["implement_changes()<br/>Generate code"]
        DescribeFiles["describe_files()<br/>File metadata"]
        AcceptChanges["accept_changes()<br/>Save & diff"]
    end
    
    Developer --> AskExecute
    AskExecute -->|"approved"| BreakdownTask
    BreakdownTask --> ParseSteps
    ParseSteps --> SetSteps
    SetSteps --> StateManager
    
    StateManager -->|"unfinished_steps"| CodeMonkey
    CodeMonkey --> ImplementChanges
    ImplementChanges --> AcceptChanges
    AcceptChanges --> StateManager
    
    StateManager -->|"on commit"| DescribeFiles
    
    style Developer fill:#ffe6cc
    style CodeMonkey fill:#ccf2ff
```

**Key Workflow Stages:**

1. **Task Assignment**: TechLead creates tasks and stores them in `state.tasks`
2. **User Approval**: Developer asks user to confirm, skip, or edit the task
3. **Task Breakdown**: Developer uses LLM to generate human-readable implementation instructions
4. **Step Parsing**: Instructions are parsed into structured `TaskSteps` (save_file, command, etc.)
5. **Code Generation**: CodeMonkey iterates through `save_file` steps and generates code
6. **File Persistence**: Files are saved to disk and state, with diffs generated
7. **Description**: Files receive AI-generated descriptions for future context filtering

**Sources:** [core/agents/developer.py:95-120](), [core/agents/code_monkey.py:72-80](), [core/agents/orchestrator.py]()

---

## Developer Agent: Task Breakdown

### Agent Architecture

The Developer agent is defined in `core/agents/developer.py` and inherits from multiple mixins:

```python
class Developer(ChatWithBreakdownMixin, RelevantFilesMixin, BaseAgent):
    agent_type = "developer"
    display_name = "Developer"
```

**Inheritance Chain:**
- `BaseAgent` - Core agent functionality, LLM access, state management
- `RelevantFilesMixin` - Filters relevant files to include in LLM context
- `ChatWithBreakdownMixin` - Enables user chat/feedback during breakdown

**Sources:** [core/agents/developer.py:91-93]()

---

### Task Breakdown Workflow

The Developer's primary workflow centers on the `breakdown_current_task()` method:

```mermaid
stateDiagram-v2
    [*] --> CheckState
    
    CheckState --> UtilityFunction: current_step.type == "utility_function"
    CheckState --> NoTasks: no unfinished_tasks
    CheckState --> IterationMode: unfinished_iterations
    CheckState --> TaskMode: else
    
    UtilityFunction --> UpdateKB["update_knowledge_base()"]
    UpdateKB --> [*]
    
    NoTasks --> [*]
    
    IterationMode --> BreakdownIteration["breakdown_current_iteration()"]
    BreakdownIteration --> [*]
    
    TaskMode --> AskExecute["ask_to_execute_task()"]
    AskExecute --> Skipped: button == "skip"
    AskExecute --> Edited: button == "edit"
    AskExecute --> CheckDocs: button == "yes"
    
    Skipped --> [*]
    Edited --> SaveEdits["Save edited description"]
    SaveEdits --> [*]
    
    CheckDocs --> FetchDocs: docs == None
    CheckDocs --> BreakdownTask: else
    
    FetchDocs --> [*]: return EXTERNAL_DOCS_REQUIRED
    
    BreakdownTask --> GetRelevant["get_relevant_files_parallel()"]
    GetRelevant --> LLMBreakdown["LLM with breakdown.prompt"]
    LLMBreakdown --> ChatLoop["chat_with_breakdown()"]
    ChatLoop --> ParseTask["LLM with parse_task.prompt"]
    ParseTask --> SetSteps["set_next_steps()"]
    SetSteps --> [*]
    
    note right of LLMBreakdown
        Uses TASK_BREAKDOWN_AGENT_NAME
        Streaming output enabled
        Temperature = default
    end note
    
    note right of ParseTask
        Uses PARSE_TASK_AGENT_NAME
        Requires TaskSteps schema
        Temperature = 0
    end note
```

**Sources:** [core/agents/developer.py:95-120](), [core/agents/developer.py:204-311]()

---

### Step Types and Data Structures

The Developer produces steps that conform to a discriminated union type system:

| Step Type | Purpose | Fields |
|-----------|---------|--------|
| `SAVE_FILE` | Create or modify a file | `path: str` |
| `COMMAND` | Execute a shell command | `command: str`, `timeout: int`, `success_message: str` |
| `HUMAN_INTERVENTION` | Request human action | `human_intervention_description: str` |
| `UTILITY_FUNCTION` | Mock API integration | `file: str`, `function_name: str`, `description: str`, `status: "mocked"\|"implemented"` |

**Pydantic Schema Definition:**

```python
# From core/agents/developer.py:32-77
class StepType(str, Enum):
    COMMAND = "command"
    SAVE_FILE = "save_file"
    HUMAN_INTERVENTION = "human_intervention"
    UTILITY_FUNCTION = "utility_function"

Step = Annotated[
    Union[SaveFileStep, CommandStep, HumanInterventionStep, UtilityFunction],
    Field(discriminator="type"),
]

class TaskSteps(BaseModel):
    steps: list[Step]
```

**State Storage:**

Steps are stored in `ProjectState.steps` with metadata:
```python
{
    "id": uuid4().hex,
    "completed": False,
    "source": "app" | "troubleshooting" | "bug_hunt",
    "iteration_index": int,
    "type": StepType,
    # ... type-specific fields
}
```

**Sources:** [core/agents/developer.py:32-82](), [core/agents/developer.py:313-329]()

---

### LLM Prompts and Context Management

The Developer uses two distinct prompt templates:

#### 1. breakdown.prompt - High-Level Instructions

This prompt generates human-readable implementation instructions (not structured steps):

**Template Location:** [core/prompts/developer/breakdown.prompt]()

**Key Context Injected:**
- Project details and specification
- List of all tasks with completion status
- Current task description with `related_api_endpoints`
- File list (filtered by `get_relevant_files_parallel()`)
- External documentation snippets (if available)
- Previous redo feedback (if task was previously attempted)

**Critical Instructions:**
```
- Use <pythagoracode file="path/to/file"> tags around code changes
- Never mix multiple files in one <pythagoracode> block
- Add meaningful logs for debugging
- Remove mocked frontend API calls and implement real requests
```

**LLM Configuration:**
```python
llm = self.get_llm(TASK_BREAKDOWN_AGENT_NAME, stream_output=True)
# TASK_BREAKDOWN_AGENT_NAME can be configured per-agent in config.json
```

**Sources:** [core/prompts/developer/breakdown.prompt:1-77](), [core/agents/developer.py:233-263]()

#### 2. parse_task.prompt - Structured Step Extraction

This prompt converts the human-readable instructions into structured `TaskSteps`:

**LLM Configuration:**
```python
llm = self.get_llm(PARSE_TASK_AGENT_NAME)
convo = AgentConvo(self).template(
    "parse_task", 
    implementation_instructions=response
).require_schema(TaskSteps)
response: TaskSteps = await llm(convo, parser=JSONParser(TaskSteps), temperature=0)
```

**Temperature Setting:** Uses `temperature=0` for deterministic structured output.

**Sources:** [core/agents/developer.py:292-296]()

---

### User Interaction Points

The Developer agent has three primary user interaction mechanisms:

#### 1. Task Execution Approval

```python
async def ask_to_execute_task(self) -> bool
```

**Buttons Presented:**
- `"yes"` - Execute task as-is
- `"edit"` - Edit task description
- `"skip"` - Skip this task (only if multiple tasks remain)
- `"redo"` - Redo task from scratch

**Auto-Skip Conditions:**
- Task has `redo_human_instructions` (already edited)
- Task is marked `quick_implementation` (user-added after completion)
- Task is `user_added_subsequently` (hot-fix task)
- Task is `hardcoded` (authentication setup task)

**Sources:** [core/agents/developer.py:349-477]()

#### 2. Breakdown Review Chat

After generating implementation instructions, the system asks:
> "Does this plan look good? If yes, just press ENTER. Otherwise, tell me what you want me to change."

This is implemented via `ChatWithBreakdownMixin.chat_with_breakdown()`:

```python
async def chat_with_breakdown(self, convo: AgentConvo, breakdown: str) -> str
```

Users can:
- Press ENTER (or click "Yes, looks good!") to approve
- Provide feedback, which triggers LLM to regenerate the breakdown
- Iterate until satisfied (with conversation pruning after `CONVO_ITERATIONS_LIMIT`)

**Auto-Skip:** If `state_manager.auto_confirm_breakdown` is True, this step is skipped.

**Sources:** [core/agents/mixins.py:42-79](), [core/agents/developer.py:284]()

#### 3. Task Description Editing

When user selects "Edit Task", they can modify the task description:

```python
user_response = await self.ask_question(
    "Edit the task description:",
    initial_text=description,
)
self.next_state.current_task["description"] = user_response.text
self.next_state.current_task["run_always"] = True
```

The `run_always` flag ensures the edited task executes immediately without re-prompting.

**Sources:** [core/agents/developer.py:457-476]()

---

### Iteration Handling

The Developer also handles breaking down **iterations** (bug fixes, changes) via `breakdown_current_iteration()`:

```mermaid
graph TB
    Start["breakdown_current_iteration()"]
    CheckStatus{iteration.status}
    
    Start --> CheckStatus
    
    CheckStatus -->|"AWAITING_BUG_FIX<br/>AWAITING_LOGGING"| BugFix["Use bug_hunting_cycles[-1]<br/>as description"]
    CheckStatus -->|"IMPLEMENT_SOLUTION<br/>NEW_FEATURE_REQUESTED"| IterDesc["Use iteration.description"]
    
    BugFix --> GetFiles["get_relevant_files_parallel()"]
    IterDesc --> GetFiles
    
    GetFiles --> ParseTask["LLM with parse_task.prompt"]
    ParseTask --> SetSteps["set_next_steps()"]
    
    SetSteps --> UpdateStatus{Update Status}
    
    UpdateStatus -->|"was AWAITING_BUG_FIX"| ToTest["status = AWAITING_USER_TEST"]
    UpdateStatus -->|"was AWAITING_LOGGING"| ToReproduce["status = AWAITING_BUG_REPRODUCTION"]
    UpdateStatus -->|"else"| Complete["complete_iteration()"]
    
    ToTest --> End[Done]
    ToReproduce --> End
    Complete --> End
```

**Key Differences from Task Breakdown:**
- No breakdown.prompt step (description comes from BugHunter or Troubleshooter)
- Goes straight to parse_task.prompt
- Updates iteration status based on previous state
- Source tagged as `"troubleshooting"` or `"bug_hunt"`

**Sources:** [core/agents/developer.py:121-202]()

---

## CodeMonkey Agent: Code Generation

### Agent Architecture

The CodeMonkey agent is defined in `core/agents/code_monkey.py`:

```python
class CodeMonkey(FileDiffMixin, BaseAgent):
    agent_type = "code-monkey"
    display_name = "Code Monkey"
```

**Inheritance:**
- `BaseAgent` - Core agent functionality
- `FileDiffMixin` - Diff generation using Python's `difflib`

**Primary Responsibilities:**
1. Execute `save_file` steps from Developer's breakdown
2. Generate or modify file contents using LLM
3. Create file descriptions for context filtering
4. Generate diffs for UI display
5. Detect `INPUT_REQUIRED` placeholders

**Sources:** [core/agents/code_monkey.py:68-70]()

---

### Code Implementation Workflow

```mermaid
sequenceDiagram
    participant Orch as Orchestrator
    participant CM as CodeMonkey
    participant LLM as LLM (OpenAI/Relace)
    participant SM as StateManager
    participant UI as UI Layer
    
    Orch->>CM: run() with save_file step
    CM->>SM: get_file_by_path(file_name)
    SM-->>CM: current file content
    
    CM->>UI: send_file_status("creating/updating")
    
    alt Has Relace Access Token & pythagoracode blocks
        CM->>LLM: Relace API (IMPLEMENT_CHANGES_AGENT_NAME)
        Note over LLM: Custom code merge model
    else Fallback or no blocks
        CM->>LLM: OpenAI API (CODE_MONKEY_AGENT_NAME)
        Note over LLM: implement_changes.prompt
    end
    
    LLM-->>CM: new_content
    
    CM->>CM: accept_changes()
    CM->>UI: generate_diff(old, new)
    CM->>SM: save_file(path, new_content)
    CM->>CM: Check for INPUT_REQUIRED
    
    alt Has INPUT_REQUIRED placeholders
        CM-->>Orch: AgentResponse.input_required(...)
    else No placeholders
        CM-->>Orch: AgentResponse.done()
    end
```

**Sources:** [core/agents/code_monkey.py:72-79](), [core/agents/code_monkey.py:81-158]()

---

### Implementation Strategy: Relace vs. OpenAI

CodeMonkey uses a two-tier strategy for code generation:

#### Tier 1: Relace API (Preferred)

```python
# From core/agents/code_monkey.py:118-133
if blocks and self.state_manager.get_access_token():
    try:
        block = next((item for item in blocks if item["file_name"] == file_name), None)
        if block:
            llm = self.get_llm(IMPLEMENT_CHANGES_AGENT_NAME)
            convo = Convo().user({
                "initialCode": file_content,
                "editSnippet": block["file_content"],
            })
            response = await llm(convo, temperature=0, parser=OptionalCodeBlockParser())
    except Exception:
        response = None
```

**Conditions for Relace:**
1. `<pythagoracode file="...">` blocks exist in Developer's instructions
2. Access token is available (`state_manager.get_access_token()`)
3. Current file matches a block's `file_name`

**Relace Model:** Configured via `IMPLEMENT_CHANGES_AGENT_NAME` (typically `"relace-code-merge"`)

**Advantages:**
- Specialized in code merging and editing
- More accurate diffs for existing files
- Faster inference

**Sources:** [core/agents/code_monkey.py:118-133]()

#### Tier 2: OpenAI Fallback

```python
# From core/agents/code_monkey.py:135-152
llm = self.get_llm(CODE_MONKEY_AGENT_NAME)
convo = AgentConvo(self).template(
    "implement_changes",
    file_name=file_name,
    file_content=file_content,
    instructions=instructions,
    user_feedback=user_feedback,
    user_feedback_qa=user_feedback_qa,
)
response = await llm(convo, temperature=0, parser=OptionalCodeBlockParser())
```

**Prompt Template:** `implement_changes.prompt`

**Context Provided:**
- Target file name
- Current file content (empty string for new files)
- Developer's human-readable instructions
- User feedback (if in iteration mode)
- User feedback Q&A (if available)

**Sources:** [core/agents/code_monkey.py:135-152]()

---

### Code Block Extraction

The `extract_code_blocks()` function parses `<pythagoracode>` tags from Developer's instructions:

```python
# From core/agents/code_monkey.py:61-65
def extract_code_blocks(content):
    code_blocks = re.findall(
        r'<pythagoracode\s+file="(.*?)">(.*?)</pythagoracode>', 
        content, 
        re.DOTALL
    )
    return [{"file_name": file_name, "file_content": file_content} 
            for file_name, file_content in code_blocks]
```

**Example Input:**
```
<pythagoracode file="server/routes/users.js">
router.get('/api/users', async (req, res) => {
  // implementation
});
</pythagoracode>
```

**Parsed Output:**
```python
[{
    "file_name": "server/routes/users.js",
    "file_content": "router.get('/api/users', async (req, res) => {\n  // implementation\n});"
}]
```

**Sources:** [core/agents/code_monkey.py:61-65]()

---

### File Metadata Generation

After files are committed to state, CodeMonkey describes them via `describe_files()`:

```mermaid
graph LR
    Trigger["Orchestrator detects<br/>ResponseType.DESCRIBE_FILES"]
    Filter["Filter files without<br/>meta.description"]
    
    subgraph "Parallel Execution"
        Desc1["describe_file(file1)"]
        Desc2["describe_file(file2)"]
        DescN["describe_file(fileN)"]
    end
    
    LLM["LLM with describe_file.prompt<br/>(DESCRIBE_FILES_AGENT_NAME)"]
    Schema["FileDescription schema"]
    Update["Update file.content.meta"]
    
    Trigger --> Filter
    Filter --> Desc1
    Filter --> Desc2
    Filter --> DescN
    
    Desc1 --> LLM
    Desc2 --> LLM
    DescN --> LLM
    
    LLM --> Schema
    Schema --> Update
```

**FileDescription Schema:**

```python
class FileDescription(BaseModel):
    summary: str = Field(
        description="Detailed description of what the file is about, major classes, functions, elements"
    )
    references: list[str] = Field(
        description="List of local project file paths that this file imports/includes"
    )
```

**Metadata Storage:**

```python
file.content.meta = {
    **file.content.meta,
    "description": llm_response.summary,
    "references": llm_response.references,
}
```

**Purpose:** These descriptions are used by `RelevantFilesMixin.get_relevant_files()` to filter which files to include in LLM context for future tasks.

**Sources:** [core/agents/code_monkey.py:160-208](), [core/agents/code_monkey.py:52-58]()

---

### Diff Generation and File Saving

The final step in code implementation is `accept_changes()`:

```python
# From core/agents/code_monkey.py:213-232
async def accept_changes(self, file_path: str, old_content: str, new_content: str) -> AgentResponse:
    await self.ui.send_file_status(file_path, "done", source=self.ui_source)
    
    n_new_lines, n_del_lines = self.get_line_changes(old_content, new_content)
    await self.ui.generate_diff(
        file_path, old_content, new_content, n_new_lines, n_del_lines, source=self.ui_source
    )
    
    await self.state_manager.save_file(file_path, new_content)
    self.step["save_file"]["content"] = new_content
    self.next_state.complete_step("save_file")
    
    input_required = self.state_manager.get_input_required(new_content, file_path)
    if input_required:
        return AgentResponse.input_required(
            self,
            [{"file": file_path, "line": line} for line in input_required],
        )
    else:
        return AgentResponse.done(self)
```

**Key Operations:**

1. **Status Update**: UI shows "done" badge for the file
2. **Diff Calculation**: Uses `difflib` to count added/deleted lines
3. **UI Diff Display**: Sends unified diff to VSCode extension or CLI
4. **File Persistence**: Saves to Virtual File System (disk or memory)
5. **Step Completion**: Marks `save_file` step as `completed: true`
6. **Input Detection**: Checks for `INPUT_REQUIRED` placeholders

**INPUT_REQUIRED Detection:**

```python
# From state_manager.py (referenced)
def get_input_required(self, content: str, file_path: str = None) -> list[int]:
    """Returns list of line numbers containing INPUT_REQUIRED placeholders"""
    lines = content.split('\n')
    return [i+1 for i, line in enumerate(lines) if 'INPUT_REQUIRED' in line]
```

If placeholders are found, returns `AgentResponse.input_required()` which pauses execution and prompts user to fill in values.

**Sources:** [core/agents/code_monkey.py:213-232](), [core/agents/mixins.py:196-208]()

---

## Integration with Orchestrator

The Orchestrator coordinates Developer and CodeMonkey through a step-based state machine:

```mermaid
stateDiagram-v2
    [*] --> Developer
    
    state Developer {
        [*] --> CheckTask
        CheckTask --> BreakdownTask: has unfinished task
        CheckTask --> Done: no tasks
        BreakdownTask --> SetSteps
        SetSteps --> [*]
    }
    
    Developer --> CheckSteps: commit state
    
    state CheckSteps <<choice>>
    CheckSteps --> CodeMonkey: has unfinished steps
    CheckSteps --> TechLead: all tasks complete
    
    state CodeMonkey {
        [*] --> ExecuteStep
        ExecuteStep --> SaveFile: step.type == "save_file"
        ExecuteStep --> Command: step.type == "command"
        ExecuteStep --> HumanIntervention: step.type == "human_intervention"
        
        SaveFile --> CompleteStep
        Command --> CompleteStep
        HumanIntervention --> CompleteStep
        CompleteStep --> [*]
    }
    
    CodeMonkey --> CheckSteps: commit state
    
    state TechLead {
        [*] --> NextTask
        NextTask --> Developer: more tasks
        NextTask --> Complete: all done
        Complete --> [*]
    }
```

**Step Execution Loop:**

1. Developer creates steps: `state.steps = [...unfinished steps]`
2. Orchestrator calls CodeMonkey repeatedly while `state.unfinished_steps` exists
3. Each CodeMonkey iteration:
   - Gets `state.current_step` (first unfinished step)
   - Executes based on `step.type`
   - Calls `next_state.complete_step()` to mark it done
4. When no unfinished steps remain, Orchestrator advances to next agent

**Sources:** [core/agents/orchestrator.py]() (referenced in high-level diagrams)

---

## Error Handling and Retries

### Developer: Incomplete Code Generation

The Developer has retry logic for incomplete `<pythagoracode>` blocks:

```python
# From core/agents/developer.py:265-282
max_retries = 2
retry_count = 0

while retry_count < max_retries:
    if has_correct_num_of_tags(response):
        break
    
    convo.user(
        "Ok, now think carefully... If your last response finishes with an incomplete file, "
        "implement that file and any other that needs implementation..."
    )
    continue_response: str = await llm(convo)
    
    last_open_tag_index = response.rfind("<pythagoracode file")
    response = response[:last_open_tag_index] + continue_response
    
    retry_count += 1
```

**Recovery Strategy:**
1. Check if opening `<pythagoracode file` tags match closing `</pythagoracode>` tags
2. If mismatch, prompt LLM to continue from last incomplete block
3. Concatenate responses, removing the incomplete opening tag
4. Retry up to 2 times

**Sources:** [core/agents/developer.py:84-88](), [core/agents/developer.py:265-282]()

### CodeMonkey: Review Feedback Loop (Disabled)

The code contains review infrastructure that is currently unused:

```python
# Constants in core/agents/code_monkey.py:29-32
MAX_REVIEW_RETRIES = 2
MAX_CODING_ATTEMPTS = 3
```

The `implement_changes()` method accepts a `data` parameter with `attempt` and `feedback` fields for rework cycles, but the review logic is not currently invoked by the Orchestrator.

**Historical Context:** Previous versions likely had CodeMonkey review its own changes and iterate based on self-critique. This has been simplified to a single-pass generation.

**Sources:** [core/agents/code_monkey.py:29-32](), [core/agents/code_monkey.py:81-102]()

---

## Configuration and LLM Assignments

Implementation agents can use different LLM models for different sub-tasks:

| Configuration Key | Purpose | Typical Model | Agent |
|-------------------|---------|---------------|-------|
| `TASK_BREAKDOWN_AGENT_NAME` | Generate human-readable implementation instructions | `gpt-4o`, `claude-sonnet-4` | Developer |
| `PARSE_TASK_AGENT_NAME` | Parse instructions into structured steps | `gpt-4o-mini` | Developer |
| `CODE_MONKEY_AGENT_NAME` | Generate code (OpenAI fallback) | `gpt-4o` | CodeMonkey |
| `IMPLEMENT_CHANGES_AGENT_NAME` | Generate code (Relace API) | `relace-code-merge` | CodeMonkey |
| `DESCRIBE_FILES_AGENT_NAME` | Generate file metadata | `gpt-4o-mini` | CodeMonkey |

**Example config.json:**

```json
{
  "agent": {
    "default": {
      "provider": "openai",
      "model": "gpt-4o-2024-05-13"
    },
    "code-monkey": {
      "provider": "anthropic",
      "model": "claude-sonnet-4"
    },
    "describe-files": {
      "provider": "openai",
      "model": "gpt-4o-mini"
    }
  }
}
```

This allows cost optimization (using `gpt-4o-mini` for simple tasks) and quality optimization (using `claude-sonnet-4` for complex code generation).

**Sources:** [core/config/__init__.py]() (referenced), [core/llm/base.py]() (referenced)

---

## Summary: Implementation Pipeline

The complete implementation pipeline can be visualized as:

```mermaid
graph TB
    subgraph "Input: Task Description"
        Task["task.description<br/>task.related_api_endpoints<br/>task.pre_breakdown_testing_instructions"]
    end
    
    subgraph "Developer Agent Pipeline"
        UserApproval["User Approval<br/>ask_to_execute_task()"]
        FilterFiles["Context Filtering<br/>get_relevant_files_parallel()"]
        LLMBreakdown["LLM Breakdown<br/>breakdown.prompt → instructions"]
        UserChat["User Review<br/>chat_with_breakdown()"]
        ParseSteps["Step Parsing<br/>parse_task.prompt → TaskSteps"]
        StoreSteps["Store Steps<br/>state.steps"]
    end
    
    subgraph "CodeMonkey Agent Pipeline"
        GetStep["Get current_step<br/>type == 'save_file'"]
        GetFile["Load file content<br/>state_manager.get_file_by_path()"]
        ExtractBlocks["Extract pythagoracode blocks"]
        
        TryRelace["Try Relace API<br/>IMPLEMENT_CHANGES_AGENT_NAME"]
        FallbackOpenAI["Fallback OpenAI<br/>CODE_MONKEY_AGENT_NAME"]
        
        SaveFile["Persist File<br/>state_manager.save_file()"]
        GenerateDiff["Generate Diff<br/>ui.generate_diff()"]
        CheckInput["Check INPUT_REQUIRED"]
        DescribeFile["Describe File<br/>DESCRIBE_FILES_AGENT_NAME"]
    end
    
    subgraph "Output: Code Files"
        Files["Updated Files in VFS<br/>with metadata"]
    end
    
    Task --> UserApproval
    UserApproval -->|approved| FilterFiles
    FilterFiles --> LLMBreakdown
    LLMBreakdown --> UserChat
    UserChat --> ParseSteps
    ParseSteps --> StoreSteps
    
    StoreSteps -->|commit state| GetStep
    GetStep --> GetFile
    GetFile --> ExtractBlocks
    
    ExtractBlocks -->|has blocks & token| TryRelace
    ExtractBlocks -->|no blocks or no token| FallbackOpenAI
    TryRelace -->|success| SaveFile
    TryRelace -->|failure| FallbackOpenAI
    FallbackOpenAI --> SaveFile
    
    SaveFile --> GenerateDiff
    GenerateDiff --> CheckInput
    CheckInput -->|no INPUT_REQUIRED| DescribeFile
    CheckInput -->|has INPUT_REQUIRED| PauseForInput["Pause for User Input"]
    
    DescribeFile --> Files
    PauseForInput --> Files
    
    style UserApproval fill:#fff3cd
    style UserChat fill:#fff3cd
    style TryRelace fill:#d1ecf1
    style FallbackOpenAI fill:#f8d7da
```

**Key Takeaways:**

1. **Two-Phase Generation**: Separate phases for planning (Developer) and execution (CodeMonkey) enable human oversight
2. **Multiple LLM Strategies**: Relace for precise code edits, OpenAI for flexible generation
3. **Context Optimization**: Relevant file filtering reduces token usage by 60-80%
4. **User Checkpoints**: Three approval points (task start, breakdown review, input placeholders)
5. **Metadata Layer**: File descriptions enable intelligent context filtering for future tasks

**Sources:** [core/agents/developer.py:1-485](), [core/agents/code_monkey.py:1-233]()

---

# Page: Frontend Development Agent

# Frontend Development Agent

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [core/agents/architect.py](core/agents/architect.py)
- [core/agents/frontend.py](core/agents/frontend.py)
- [core/agents/orchestrator.py](core/agents/orchestrator.py)
- [core/agents/spec_writer.py](core/agents/spec_writer.py)
- [core/agents/wizard.py](core/agents/wizard.py)
- [core/templates/tree/vite_react/client/src/api/api.ts](core/templates/tree/vite_react/client/src/api/api.ts)
- [core/templates/tree/vite_react_swagger/client/.env](core/templates/tree/vite_react_swagger/client/.env)
- [core/templates/tree/vite_react_swagger/client/src/api/api.ts](core/templates/tree/vite_react_swagger/client/src/api/api.ts)

</details>



## Purpose and Scope

The Frontend Development Agent is responsible for building the user interface layer of applications in GPT Pilot. This agent generates frontend code, handles UI iterations based on user feedback, and manages the transition from mock data to real API endpoints in Swagger-based projects. The Frontend agent operates after project specification and architecture planning are complete, typically as the first implementation phase of a project.

For information about backend implementation, see [Implementation Agents](#4.3). For the overall agent coordination system, see [Orchestrator and Control Flow](#3.3). For task breakdown and planning that precedes frontend work, see [Planning Agents](#4.2).

**Sources:** [core/agents/frontend.py:1-603](), [core/agents/orchestrator.py:486-488]()

---

## Agent Architecture

### Class Structure

The `Frontend` agent inherits from `BaseAgent` and incorporates two key mixins:

```mermaid
graph TB
    BaseAgent["BaseAgent<br/>Agent Lifecycle"]
    FileDiffMixin["FileDiffMixin<br/>File Comparison"]
    GitMixin["GitMixin<br/>Version Control"]
    Frontend["Frontend<br/>agent_type: 'frontend'<br/>display_name: 'Frontend'"]
    
    BaseAgent --> Frontend
    FileDiffMixin --> Frontend
    GitMixin --> Frontend
    
    Frontend --> run["run()<br/>Main Entry Point"]
    Frontend --> start_frontend["start_frontend()<br/>Initial Build"]
    Frontend --> continue_frontend["continue_frontend()<br/>Continuation Logic"]
    Frontend --> iterate_frontend["iterate_frontend()<br/>User Feedback Loop"]
    Frontend --> remove_mock["remove_mock()<br/>Mock Removal"]
    Frontend --> process_response["process_response()<br/>LLM Response Handler"]
```

**Sources:** [core/agents/frontend.py:40-42]()

---

## Frontend Development Workflow

### State Transition Flow

The Frontend agent operates through a state machine that progresses through multiple phases:

```mermaid
stateDiagram-v2
    [*] --> CheckState: Agent.run()
    
    CheckState --> StartFrontend: No messages in epic
    CheckState --> RemoveMock: file_paths_to_remove_mock exists
    CheckState --> ContinueFrontend: Not fe_iteration_done
    CheckState --> IterateFrontend: fe_iteration_done set
    
    StartFrontend --> BuildUI: FE_START action
    BuildUI --> ProcessBlocks: LLM generates code
    ProcessBlocks --> MarkDone: Set fe_iteration_done
    MarkDone --> EndIteration
    
    ContinueFrontend --> FE_CONTINUE: Check previous response
    FE_CONTINUE --> ContinueOrDone: LLM continues/finishes
    ContinueOrDone --> EndIteration
    
    RemoveMock --> RAGSearch: Query API docs
    RAGSearch --> ReplaceCode: Replace mock with real API
    ReplaceCode --> EndIteration
    
    IterateFrontend --> AutoDebug: try_auto_debug()
    AutoDebug --> UserFeedback: Ask for changes
    UserFeedback --> Done: "I'm done"
    UserFeedback --> FixErrors: Report bug/change
    FixErrors --> RelaceAttempt: Try relace first
    RelaceAttempt --> FullBuild: Relace fails
    RelaceAttempt --> ProcessCode: Relace succeeds
    FullBuild --> ProcessCode
    ProcessCode --> EndIteration
    
    Done --> CommitEpic: complete_epic()
    CommitEpic --> [*]
    
    EndIteration --> end_frontend_iteration
    end_frontend_iteration --> CheckInputs: Check for INPUT_REQUIRED
    CheckInputs --> [*]
    
    note right of StartFrontend
        First build of UI
        Uses build_frontend prompt
    end note
    
    note right of ContinueFrontend
        Continues incomplete work
        Max 15 message exchanges
    end note
    
    note right of IterateFrontend
        User testing phase
        Auto-debug then feedback
    end note
```

**Sources:** [core/agents/frontend.py:44-59](), [core/agents/frontend.py:61-110](), [core/agents/frontend.py:112-149](), [core/agents/frontend.py:151-318]()

---

## Initial Frontend Build

### Start Frontend Process

The `start_frontend()` method initiates the first UI build:

| Stage | Action | State Update |
|-------|--------|--------------|
| **Initialization** | Set `fe_auto_debug = True`, clear logs | `action = FE_START` |
| **LLM Invocation** | Call FRONTEND_AGENT_NAME with `build_frontend` template | Stream output to user |
| **Template Wait** | Await `async_tasks[-1]` completion if present | Ensure template is ready |
| **Response Processing** | Parse `DescriptiveCodeBlockParser()` blocks | Process files and commands |
| **Completion Check** | Check for "done" in last 20 chars OR message count > 11 | Set `fe_iteration_done` |

The agent uses the following LLM configuration:

```mermaid
graph LR
    Frontend["Frontend Agent"]
    LLM["get_llm(FRONTEND_AGENT_NAME)"]
    Convo["AgentConvo.template('build_frontend')"]
    Parser["DescriptiveCodeBlockParser"]
    
    Frontend --> LLM
    Frontend --> Convo
    Convo --> Parameters["Parameters:<br/>- summary<br/>- description<br/>- user_feedback<br/>- first_time_build"]
    LLM --> Parser
    Parser --> Blocks["response.blocks[]<br/>File and command blocks"]
```

**Sources:** [core/agents/frontend.py:61-110](), [core/agents/frontend.py:82-92]()

---

## Continuation and Completion

### Continue Frontend Logic

When the initial build is incomplete, `continue_frontend()` resumes work:

```mermaid
sequenceDiagram
    participant Agent as Frontend Agent
    participant State as ProjectState
    participant LLM as FRONTEND_AGENT_NAME
    participant Parser as DescriptiveCodeBlockParser
    
    Agent->>State: Get messages from epic
    Agent->>Agent: Create AgentConvo with existing messages
    Agent->>Agent: Add continuation prompt
    Note over Agent: "If response ends mentioning continuing,<br/>continue but don't re-implement.<br/>If incomplete file, finish it.<br/>Otherwise respond DONE."
    Agent->>LLM: Generate continuation
    LLM->>Parser: Parse code blocks
    Parser->>Agent: Return response blocks
    Agent->>Agent: process_response(blocks, relace=use_relace)
    Agent->>State: Update fe_iteration_done
    Note over State: Done if "done" in last 20 chars<br/>OR message count > 15
```

The continuation has two completion modes:

1. **Manual Iteration Mode** (`manual_iteration=True`): Completes when backticks are balanced OR retry_count ≥ 2
2. **Auto Mode**: Completes when "done" appears in response OR message count exceeds 15

**Sources:** [core/agents/frontend.py:112-149](), [core/agents/frontend.py:124-127]()

---

## User Feedback and Iteration

### Iterate Frontend Cycle

The `iterate_frontend()` method implements the core user testing loop:

```mermaid
graph TB
    Start["iterate_frontend()"] --> AutoDebug["try_auto_debug()<br/>3 attempts max"]
    AutoDebug --> HasErrors{Errors<br/>detected?}
    
    HasErrors -->|Yes| FixMessage["Show 'Errors detected, fixing...'"]
    HasErrors -->|No| AskUser["Ask: 'Do you want to change anything?'"]
    
    AskUser --> UserResponse{User<br/>Response}
    UserResponse -->|"I'm done building UI"| Confirm["Confirm: 'Yes, let's build backend?'"]
    UserResponse -->|Reports issue| UserInput["Capture user_input"]
    
    Confirm -->|Yes| UpdateLogs["Update UI logs to 'done'"]
    Confirm -->|No| UserInput
    UpdateLogs --> ReturnTrue["return True"]
    
    FixMessage --> CheckRAG{frontend_only<br/>project?}
    UserInput --> CheckRAG
    
    CheckRAG -->|Yes| RAGQuery["is_relevant_for_docs_search"]
    CheckRAG -->|No| TryRelace
    
    RAGQuery --> RAGNeeded{RAG<br/>needed?}
    RAGNeeded -->|Yes| FetchDocs["HTTP POST to /rag/search"]
    RAGNeeded -->|No| TryRelace
    FetchDocs --> TryRelace["LLM with iterate_frontend + system_relace"]
    
    TryRelace --> ProcessRelace["process_response(relace=True)"]
    ProcessRelace --> RelaceSuccess{Success?}
    
    RelaceSuccess -->|Yes| UpdateState["Set use_relace=True"]
    RelaceSuccess -->|No| FullRebuild["LLM with build_frontend"]
    FullRebuild --> ProcessFull["process_response(relace=False)"]
    ProcessFull --> UpdateState
    
    UpdateState --> SetFlags["fe_iteration_done=has_correct_backticks<br/>manual_iteration=True"]
    SetFlags --> ReturnFalse["return False"]
    
    ReturnTrue --> End([End])
    ReturnFalse --> End
```

**Sources:** [core/agents/frontend.py:151-318](), [core/agents/frontend.py:159-229](), [core/agents/frontend.py:280-317]()

---

## Response Processing System

### Code Block Processing

The `process_response()` method handles LLM output containing file modifications and commands:

```mermaid
graph TB
    Start["process_response(blocks, removed_mock, relace)"] --> Loop["For each block in blocks"]
    
    Loop --> Extract["Extract description and content"]
    Extract --> ParseDesc["Split description by newlines<br/>Get last line"]
    ParseDesc --> CheckType{Type?}
    
    CheckType -->|"file: path"| ExtractPath["Extract file path<br/>Strip quotes/backticks"]
    CheckType -->|"command:"| ExtractCmd["Extract commands<br/>Split by newlines"]
    CheckType -->|Unknown| LogUnknown["log.info('Unknown block')"]
    
    ExtractPath --> CheckRelace{relace<br/>flag?}
    CheckRelace -->|True| RelaceMerge["LLM: IMPLEMENT_CHANGES_AGENT_NAME<br/>Merge edit snippet into code"]
    CheckRelace -->|False| DirectContent["Use content directly"]
    
    RelaceMerge --> CheckResult{Valid<br/>result?}
    CheckResult -->|No| ReturnFalse["return False"]
    CheckResult -->|Yes| CalcDiff
    
    DirectContent --> CalcDiff["get_line_changes(old, new)"]
    CalcDiff --> SendDiff["ui.generate_diff()<br/>ui.send_file_status('done')"]
    SendDiff --> CheckMock{Swagger project<br/>AND 'client/src/api'?}
    CheckMock -->|Yes| AddToMockList["Add to file_paths_to_remove_mock"]
    CheckMock -->|No| SaveFile
    AddToMockList --> SaveFile["state_manager.save_file()"]
    
    ExtractCmd --> CmdLoop["For each command"]
    CmdLoop --> AddPrefix{Starts with<br/>'cd '?}
    AddPrefix -->|No| AddCD["Prepend 'cd client &&'"]
    AddPrefix -->|Yes| CheckSkip
    AddCD --> CheckSkip{Skip<br/>conditions?}
    
    CheckSkip -->|"run start/dev"| SkipCmd["continue"]
    CheckSkip -->|npm script not in package.json| SkipCmd
    CheckSkip -->|Valid| RunCmd["process_manager.run_command()"]
    
    SaveFile --> NextBlock["Next block"]
    RunCmd --> NextBlock
    LogUnknown --> NextBlock
    SkipCmd --> NextBlock
    NextBlock --> Loop
    
    Loop --> ReturnTrue["return True"]
    ReturnFalse --> End([End])
    ReturnTrue --> End
```

**File Path Extraction Rules:**
- Last line must contain `"file:"` keyword
- Path extracted after `"file:"` (index + 5)
- Strips quotes (`"'` \`) and backticks
- Empty paths are skipped

**Command Processing Rules:**
- Last line must contain `"command:"` keyword
- Multiple commands split by newlines
- Auto-prefixes `cd client &&` if not present
- Validates npm scripts against `package.json`
- Skips `run start` and `run dev` commands

**Sources:** [core/agents/frontend.py:356-449](), [core/agents/frontend.py:367-378](), [core/agents/frontend.py:408-443]()

---

## Mock Removal System

### Swagger API Integration

For Swagger-based projects, the Frontend agent replaces mock API implementations with real endpoint calls:

```mermaid
sequenceDiagram
    participant Frontend as Frontend Agent
    participant State as file_paths_to_remove_mock[]
    participant RAG as RAG Service
    participant LLM as FRONTEND_AGENT_NAME
    participant Files as State Manager
    
    Frontend->>State: Get new_file_paths list
    
    loop For each file_path
        Frontend->>Files: Get old_content
        Frontend->>LLM: create_rag_query template
        LLM-->>Frontend: topics string (or "None")
        
        alt topics != "None"
            Frontend->>RAG: POST /rag/search
            Note over Frontend,RAG: Send topics + project_id<br/>Auth: Bearer token
            RAG-->>Frontend: Array of documentation chunks
            
            alt Status 200
                Frontend->>Files: get_referencing_files()
                Frontend->>LLM: remove_mock template
                Note over Frontend,LLM: Params: relevant_api_documentation<br/>file_content, file_path<br/>referencing_files, lines
                LLM-->>Frontend: DescriptiveCodeBlockParser response
                Frontend->>Frontend: process_response(blocks, removed_mock=True)
                Frontend->>State: Remove file_path from list
            else Status 401/403
                Frontend->>Frontend: send_token_expired()
                Frontend->>Frontend: update_access_token()
            else Other error
                Frontend->>Frontend: Log warning, retry (max 3)
            end
        end
    end
```

**Key Implementation Details:**

| Aspect | Implementation |
|--------|---------------|
| **Trigger Condition** | `file_paths_to_remove_mock` exists in epic state |
| **File Detection** | During `process_response()` when path contains `"client/src/api"` |
| **RAG Query Generation** | LLM creates search query from file content |
| **Documentation Retrieval** | Posts to `PYTHAGORA_API/rag/search` with Bearer auth |
| **Code Replacement** | Uses `remove_mock` template with RAG documentation |
| **Error Handling** | 3 retry attempts, token refresh on 401/403 |
| **Completion** | Returns `None` on fatal error, `False` on success |

**Sources:** [core/agents/frontend.py:451-517](), [core/agents/frontend.py:47-50](), [core/agents/frontend.py:400-405]()

---

## Auto-Debugging System

### Frontend Error Detection

The `try_auto_debug()` method automatically detects and reports frontend errors:

```mermaid
graph TB
    Start["try_auto_debug()"] --> CheckFlag{fe_auto_debug<br/>enabled?}
    CheckFlag -->|No| EnableFlag["Set fe_auto_debug=True"]
    EnableFlag --> ReturnEmpty["return ''"]
    
    CheckFlag -->|Yes| CheckAttempts{auto_debug_attempts<br/>< 3?}
    CheckAttempts -->|No| ReturnEmpty
    CheckAttempts -->|Yes| SendMsg["send_message('Auto-debugging #N')"]
    
    SendMsg --> IncrementCount["Increment auto_debug_attempts"]
    IncrementCount --> KillApp["kill_app()<br/>Kill ports 5173, 3000"]
    KillApp --> StartNpm["start_process('npm run start &')"]
    
    StartNpm --> InitialWait["Sleep 5 seconds"]
    InitialWait --> ReadLoop["Read output loop (max 3 times)"]
    ReadLoop --> Sleep2["Sleep 2 seconds between reads"]
    Sleep2 --> CheckOutput{stdout/stderr<br/>empty OR<br/>count ≤ 0?}
    
    CheckOutput -->|Continue| ReadLoop
    CheckOutput -->|Break| CurlTest["run_command('curl http://localhost:5173')"]
    CurlTest --> FinalSleep["Sleep 1 second"]
    FinalSleep --> FinalRead["Read final output"]
    
    FinalRead --> KillAgain["kill_app() again"]
    KillAgain --> HasOutput{stdout OR<br/>stderr?}
    
    HasOutput -->|Yes| ReturnError["send_message('Auto-debugging found error')<br/>return error logs"]
    HasOutput -->|No| SendOK["send_message('All good, no errors')"]
    SendOK --> ReturnEmpty
    
    ReturnEmpty --> End([End])
    ReturnError --> End
```

**Platform-Specific Port Killing:**

| Platform | Command | Ports |
|----------|---------|-------|
| **Windows** | `netstat -ano \| findstr :PORT \| findstr LISTENING` → `taskkill /F /PID` | 5173 (frontend), 3000 (backend) |
| **Unix/Linux** | `lsof -ti:PORT \| xargs -r kill` | 5173 (frontend), 3000 (backend) |

**Auto-Debug Configuration:**

- **Maximum Attempts:** 3 per iteration (tracked in `epics[-1]["auto_debug_attempts"]`)
- **Initial Wait:** 5 seconds after starting npm
- **Poll Interval:** 2 seconds for output checks
- **Test Method:** curl request to `http://localhost:5173`
- **State Reset:** `fe_auto_debug` flag toggles on/off between iterations

**Sources:** [core/agents/frontend.py:554-602](), [core/agents/frontend.py:532-552]()

---

## LLM Integration

### Prompt Templates and Parsing

The Frontend agent uses specific prompt templates and parsers:

```mermaid
graph TB
    subgraph "Templates Used"
        BuildFrontend["build_frontend<br/>Initial/iteration builds"]
        IterateFrontend["iterate_frontend<br/>User feedback changes"]
        SystemRelace["system_relace<br/>Code merge prompt"]
        CreateRAGQuery["create_rag_query<br/>Search query generation"]
        RemoveMock["remove_mock<br/>Mock replacement"]
        IsRelevant["is_relevant_for_docs_search<br/>RAG relevance check"]
    end
    
    subgraph "LLM Clients"
        FrontendAgent["FRONTEND_AGENT_NAME<br/>Primary generation"]
        ImplementChanges["IMPLEMENT_CHANGES_AGENT_NAME<br/>Relace merging"]
    end
    
    subgraph "Parsers"
        DescriptiveParser["DescriptiveCodeBlockParser<br/>File + command blocks"]
        OptionalParser["OptionalCodeBlockParser<br/>Relace output"]
        StringParser["StringParser<br/>Simple text responses"]
    end
    
    BuildFrontend --> FrontendAgent
    IterateFrontend --> FrontendAgent
    SystemRelace --> FrontendAgent
    CreateRAGQuery --> FrontendAgent
    RemoveMock --> FrontendAgent
    IsRelevant --> FrontendAgent
    
    FrontendAgent --> DescriptiveParser
    ImplementChanges --> OptionalParser
    
    DescriptiveParser --> Process["process_response()"]
    OptionalParser --> Process
```

**Template Parameters:**

| Template | Key Parameters |
|----------|----------------|
| `build_frontend` | `summary`, `description`, `user_feedback`, `first_time_build` |
| `iterate_frontend` | `description`, `user_feedback`, `relevant_api_documentation`, `first_time_build` |
| `create_rag_query` | `file_content` |
| `remove_mock` | `relevant_api_documentation`, `file_content`, `file_path`, `referencing_files`, `lines` |

**Sources:** [core/agents/frontend.py:83-92](), [core/agents/frontend.py:281-292](), [core/agents/frontend.py:382-393](), [core/agents/frontend.py:461-490]()

---

## State Management

### Epic State Structure

The Frontend agent uses the epic state to track progress:

```mermaid
graph TB
    Epic["epics[-1] (Current Epic)"]
    
    Epic --> Messages["messages: list<br/>Conversation history"]
    Epic --> FileList["file_paths_to_remove_mock: list<br/>API files needing mock removal"]
    Epic --> IterDone["fe_iteration_done: bool<br/>Completion flag"]
    Epic --> UseRelace["use_relace: bool<br/>Relace merge success"]
    Epic --> ManualIter["manual_iteration: bool<br/>User feedback mode"]
    Epic --> AutoDebug["auto_debug_attempts: int<br/>Debug attempt count (max 3)"]
    Epic --> RetryCount["retry_count: int<br/>Continuation retry count"]
    
    Messages --> Convo["Used in continue_frontend()<br/>to maintain context"]
    FileList --> MockRemoval["Triggers remove_mock()<br/>workflow"]
    IterDone --> ControlFlow["Controls run() routing:<br/>False → continue_frontend<br/>True → iterate_frontend"]
    UseRelace --> ContinueMode["Affects process_response()<br/>relace parameter"]
    ManualIter --> CompletionCheck["Changes completion logic:<br/>backtick check vs 'done' check"]
    AutoDebug --> DebugLimit["Stops after 3 attempts<br/>in iterate_frontend"]
    RetryCount --> ContinueLimit["Max 2 retries in<br/>continue_frontend"]
```

**State Transitions:**

| State Field | Set By | Used By | Purpose |
|-------------|--------|---------|---------|
| `messages` | All frontend methods | `continue_frontend()` | Maintain LLM conversation context |
| `file_paths_to_remove_mock` | `process_response()` | `run()` → `remove_mock()` | Track Swagger API files to update |
| `fe_iteration_done` | `start_frontend()`, `continue_frontend()`, `iterate_frontend()` | `run()` | Route to correct handler method |
| `use_relace` | `iterate_frontend()` | `continue_frontend()` | Enable/disable Relace merging |
| `manual_iteration` | `iterate_frontend()` | `continue_frontend()` | Switch completion detection mode |
| `auto_debug_attempts` | `iterate_frontend()` | `try_auto_debug()` | Limit debug attempts per iteration |
| `retry_count` | `continue_frontend()` | `continue_frontend()` | Prevent infinite continuation loops |

**Sources:** [core/agents/frontend.py:104-108](), [core/agents/frontend.py:135-147](), [core/agents/frontend.py:312-316](), [core/agents/frontend.py:402-404]()

---

## Application Setup Methods

### Runtime Configuration

The Frontend agent configures the development environment:

```mermaid
graph TB
    SetAppDetails["set_app_details()"] --> Command["Set run_command = 'npm run start'"]
    SetAppDetails --> Link["Set app_link = 'http://localhost:5173'"]
    Command --> UICommand["ui.send_run_command()"]
    Link --> UILink["ui.send_app_link()"]
    
    KillApp["kill_app()"] --> DetectPlatform{Platform?}
    DetectPlatform -->|Windows| WinFront["netstat + taskkill<br/>Port 5173"]
    DetectPlatform -->|Unix| UnixFront["lsof + kill<br/>Port 5173"]
    
    WinFront --> CheckType{project_type?}
    UnixFront --> CheckType
    
    CheckType -->|"node"| KillBackend["Kill backend port 3000"]
    CheckType -->|Other| Skip["Skip backend kill"]
```

**Port Management:**

| Port | Purpose | Killed When |
|------|---------|-------------|
| **5173** | Vite development server (frontend) | Always during auto-debug and cleanup |
| **3000** | Express server (backend) | Only for `project_type == "node"` |

**Sources:** [core/agents/frontend.py:519-530](), [core/agents/frontend.py:532-552]()

---

## Completion and Handoff

### End Frontend Iteration

The `end_frontend_iteration()` method handles completion:

```mermaid
graph TB
    Start["end_frontend_iteration(finished)"] --> CheckFinished{finished<br/>parameter?}
    
    CheckFinished -->|True| SetAction["action = FE_ITERATION_DONE"]
    SetAction --> CompleteEpic["complete_epic()"]
    CompleteEpic --> Telemetry["telemetry.trace_code_event('frontend-finished')"]
    
    Telemetry --> CheckGit{git_available<br/>AND git_used?}
    CheckGit -->|Yes| GitCommit["git_commit('Frontend finished')"]
    CheckGit -->|No| CheckInputs
    GitCommit --> CheckInputs["Check files for INPUT_REQUIRED"]
    
    CheckInputs --> FindInputs["state_manager.get_input_required()"]
    FindInputs --> HasInputs{Inputs<br/>required?}
    
    HasInputs -->|Yes| InputResponse["AgentResponse.input_required(self, inputs)"]
    HasInputs -->|No| DoneResponse["AgentResponse.done(self)"]
    
    CheckFinished -->|False| DoneResponse
    
    InputResponse --> End([Return Response])
    DoneResponse --> End
```

**Input Required Detection:**

The agent scans all files for special markers indicating user input is needed:

```python
inputs = []
for file in self.current_state.files:
    if not file.content:
        continue
    input_required = self.state_manager.get_input_required(
        file.content.content, 
        file.path
    )
    if input_required:
        inputs += [{"file": file.path, "line": line} for line in input_required]
```

If any inputs are found, the system triggers the `HumanInput` agent before proceeding.

**Sources:** [core/agents/frontend.py:320-354](), [core/agents/frontend.py:344-352]()

---

## Integration with Project Templates

### Template Application

The Frontend agent works with project templates defined during the Architect phase:

```mermaid
graph TB
    SpecWriter["SpecWriter Agent"] --> ApplyTemplate["apply_template()"]
    ApplyTemplate --> GetOptions["Get user_options from KB"]
    GetOptions --> SelectTemplate{auth_type?}
    
    SelectTemplate -->|"api_key" or "none"| ViteSwagger["vite_react_swagger"]
    SelectTemplate -->|"login"| ViteReact["vite_react"]
    
    ViteSwagger --> CreateTemplate["PROJECT_TEMPLATES.get(name)"]
    ViteReact --> CreateTemplate
    
    CreateTemplate --> Instantiate["template_class(options, state_manager, process_manager)"]
    Instantiate --> Store["state_manager.template['template'] = template"]
    Store --> Apply["template.apply()"]
    Apply --> SetSummary["specification.template_summary = summary"]
    
    SetSummary --> Frontend["Frontend Agent"]
    Frontend --> UseSummary["Use template summary in build_frontend prompt"]
```

**Template Integration Points:**

| File | Purpose | Template Variables |
|------|---------|-------------------|
| `client/src/api/api.ts` | API client configuration | `options.auth_type`, `options.auth`, `options.api_key` |
| `client/.env` | Environment variables | `options.api_key`, `options.external_api_url` |
| `client/index.html` | HTML scaffold | Script injection points |
| `client/vite.config.ts` | Build configuration | Host, watch settings |

**Sources:** [core/agents/spec_writer.py:34-62](), [core/agents/frontend.py:83-91](), [core/templates/tree/vite_react/client/src/api/api.ts:1-172]()

---

## Error Handling

### Exception Management

The Frontend agent implements comprehensive error handling:

```mermaid
graph TB
    TryBlock["try:"] --> Operation["Frontend Operation"]
    Operation --> Success["Successful completion"]
    
    Operation --> CatchRAG["except RAG Error"]
    CatchRAG --> Retry["3 retry attempts"]
    Retry --> CheckStatus{HTTP<br/>Status}
    CheckStatus -->|401/403| RefreshToken["send_token_expired()<br/>update_access_token()"]
    CheckStatus -->|Other| LogError["log.warning()<br/>capture_exception()"]
    RefreshToken --> Retry
    LogError --> Retry
    Retry --> MaxRetries{Max retries?}
    MaxRetries -->|Yes| ShowError["send_message('Please try reloading')"]
    MaxRetries -->|No| Retry
    
    Operation --> CatchDebug["except Auto-Debug Error"]
    CatchDebug --> LogDebug["log.error()<br/>capture_exception()"]
    LogDebug --> ContinueGraceful["Return empty string<br/>Continue without debug"]
    
    ShowError --> ReturnNone["return None<br/>(signals exit)"]
    Success --> ReturnValue["return bool/AgentResponse"]
    ContinueGraceful --> ReturnValue
    ReturnNone --> ExitAgent["AgentResponse.exit()"]
```

**Error Recovery Strategies:**

| Error Type | Strategy | Max Attempts | Fallback |
|------------|----------|--------------|----------|
| **RAG API Errors** | Token refresh + retry | 3 | Exit with error message |
| **Auto-debug Exceptions** | Log and continue | N/A | Return empty string (no errors) |
| **Relace Failures** | Fall back to full build | 1 | Use `build_frontend` template |
| **Invalid LLM Output** | Check backtick balance | 2 (via retry_count) | Mark iteration done |

**Sources:** [core/agents/frontend.py:243-276](), [core/agents/frontend.py:465-515](), [core/agents/frontend.py:597-599]()

---

## Summary Table

### Key Methods and Their Roles

| Method | Trigger Condition | Primary Action | Return Value |
|--------|------------------|----------------|--------------|
| `run()` | Orchestrator calls Frontend agent | Route to appropriate handler | `AgentResponse` |
| `start_frontend()` | No messages in epic | Initial UI build with template | `False` (continue) |
| `continue_frontend()` | Not `fe_iteration_done` | Continue incomplete build | `False` (continue) |
| `iterate_frontend()` | `fe_iteration_done` set | User feedback loop | `True` (done) or `False` (continue) |
| `remove_mock()` | `file_paths_to_remove_mock` exists | Replace mock APIs with real endpoints | `None` (error) or `False` (success) |
| `process_response()` | After LLM generation | Parse and apply code blocks | `True` (success) or `False` (failure) |
| `try_auto_debug()` | Before user feedback | Detect frontend errors | Error string or empty string |
| `end_frontend_iteration()` | After iteration completes | Check inputs, complete epic | `AgentResponse` |
| `set_app_details()` | Before user testing | Configure run command and link | `None` |
| `kill_app()` | During auto-debug | Kill frontend/backend processes | `None` |

**Sources:** [core/agents/frontend.py:44-603]()

---

# Page: Quality Assurance Agents

# Quality Assurance Agents

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [core/agents/bug_hunter.py](core/agents/bug_hunter.py)
- [core/agents/developer.py](core/agents/developer.py)
- [core/agents/legacy_handler.py](core/agents/legacy_handler.py)
- [core/agents/mixins.py](core/agents/mixins.py)
- [core/agents/tech_lead.py](core/agents/tech_lead.py)
- [core/agents/troubleshooter.py](core/agents/troubleshooter.py)
- [core/db/migrations/versions/f708791b9270_adding_knowledge_base_field_to_.py](core/db/migrations/versions/f708791b9270_adding_knowledge_base_field_to_.py)
- [core/prompts/troubleshooter/define_user_review_goal.prompt](core/prompts/troubleshooter/define_user_review_goal.prompt)
- [core/prompts/troubleshooter/get_route_files.prompt](core/prompts/troubleshooter/get_route_files.prompt)

</details>



The Quality Assurance system in GPT Pilot consists of two specialized agents that work together to ensure code quality through testing and debugging:

1. **Troubleshooter**: Generates test instructions, collects user feedback, and manages the testing lifecycle
2. **BugHunter**: Investigates reported bugs through log analysis, reproduction steps, and interactive debugging

Together, these agents form a feedback loop that enables iterative refinement of implemented features until they meet requirements.

## Agent Architecture

Both QA agents inherit from `BaseAgent` and use specialized mixins for shared functionality:

**Agent Class Hierarchy**
```mermaid
classDiagram
    class BaseAgent {
        +agent_type: str
        +display_name: str
        +current_state: ProjectState
        +next_state: ProjectState
        +ui: UIBase
        +state_manager: StateManager
        +get_llm() BaseLLMClient
        +ask_question() QuestionResponse
        +send_message() void
    }
    
    class Troubleshooter {
        +agent_type: "troubleshooter"
        +display_name: "Troubleshooter"
        +run() AgentResponse
        +create_iteration() AgentResponse
        +propose_solution() AgentResponse
        +get_run_command() Optional[str]
        +get_user_instructions() Optional[str]
        +get_user_feedback() tuple
        +complete_task() AgentResponse
        +try_next_alternative_solution() AgentResponse
        +trace_loop() void
    }
    
    class BugHunter {
        +agent_type: "bug-hunter"
        +display_name: "Bug Hunter"
        +run() AgentResponse
        +check_logs() AgentResponse
        +ask_user_to_test() AgentResponse
        +start_pair_programming() AgentResponse
        +generate_iteration_convo_so_far() AgentConvo
        +set_data_for_next_hunting_cycle() void
        +get_bug_reproduction_instructions() void
    }
    
    class ChatWithBreakdownMixin {
        +chat_with_breakdown(convo, breakdown) str
    }
    
    class IterationPromptMixin {
        +find_solution(user_feedback, kwargs) str
    }
    
    class RelevantFilesMixin {
        +get_relevant_files_parallel() AgentResponse
        +get_relevant_files() list[str]
    }
    
    BaseAgent <|-- Troubleshooter
    BaseAgent <|-- BugHunter
    ChatWithBreakdownMixin <|-- Troubleshooter
    ChatWithBreakdownMixin <|-- BugHunter
    IterationPromptMixin <|-- Troubleshooter
    RelevantFilesMixin <|-- Troubleshooter
```

Sources:
- [core/agents/troubleshooter.py:35-37]()
- [core/agents/bug_hunter.py:57-59]()
- [core/agents/mixins.py:37-79]()
- [core/agents/mixins.py:82-119]()
- [core/agents/mixins.py:122-188]()

## Iteration Status Lifecycle

The QA agents use `IterationStatus` to track the state of bug fixes and feature requests. The status determines which agent handles the iteration next:

| Status | Description | Handler Agent |
|--------|-------------|---------------|
| `FIND_SOLUTION` | Analyzing issue and determining solution approach | Troubleshooter |
| `IMPLEMENT_SOLUTION` | Solution identified, ready for code changes | Developer |
| `HUNTING_FOR_BUG` | Initial bug investigation via log analysis | BugHunter |
| `AWAITING_BUG_FIX` | Bug identified, implementing fix | Developer |
| `AWAITING_LOGGING` | Adding diagnostic logs to trace bug | Developer |
| `AWAITING_USER_TEST` | Fix implemented, waiting for user verification | BugHunter |
| `AWAITING_BUG_REPRODUCTION` | Waiting for user to reproduce bug with logs | BugHunter |
| `NEW_FEATURE_REQUESTED` | User requested functionality change | Developer |
| `PROBLEM_SOLVER` | Loop detected, trying alternative solutions | Problem Solver |
| `START_PAIR_PROGRAMMING` | Initiating interactive debugging session | BugHunter |

Sources:
- [core/db/models/project_state.py]() (IterationStatus enum)
- [core/agents/troubleshooter.py:39-146]()
- [core/agents/bug_hunter.py:61-80]()

## QA Workflow Overview

The complete QA workflow shows how Troubleshooter and BugHunter collaborate with Developer to resolve issues:

**Complete QA Cycle Flow**
```mermaid
stateDiagram-v2
    [*] --> Troubleshooter_create_iteration: Task implemented
    
    Troubleshooter_create_iteration --> get_user_instructions: No test instructions
    get_user_instructions --> Troubleshooter_create_iteration: Save instructions
    
    Troubleshooter_create_iteration --> get_user_feedback: Has test instructions
    
    get_user_feedback --> complete_task: Everything works
    get_user_feedback --> iteration_HUNTING_FOR_BUG: Bug reported
    get_user_feedback --> iteration_NEW_FEATURE_REQUESTED: Change requested
    get_user_feedback --> iteration_PROBLEM_SOLVER: Loop detected
    
    iteration_HUNTING_FOR_BUG --> BugHunter_check_logs
    
    BugHunter_check_logs --> iteration_AWAITING_LOGGING: Need more logs
    BugHunter_check_logs --> iteration_AWAITING_BUG_FIX: Bug identified
    
    iteration_AWAITING_LOGGING --> Developer_breakdown_current_iteration
    iteration_AWAITING_BUG_FIX --> Developer_breakdown_current_iteration
    iteration_NEW_FEATURE_REQUESTED --> Developer_breakdown_current_iteration
    
    Developer_breakdown_current_iteration --> CodeMonkey: Implement changes
    CodeMonkey --> iteration_AWAITING_USER_TEST: Fix complete
    
    iteration_AWAITING_USER_TEST --> BugHunter_ask_user_to_test
    
    BugHunter_ask_user_to_test --> complete_task: Bug fixed
    BugHunter_ask_user_to_test --> iteration_AWAITING_BUG_REPRODUCTION: Still broken
    BugHunter_ask_user_to_test --> iteration_START_PAIR_PROGRAMMING: User requests help
    
    iteration_AWAITING_BUG_REPRODUCTION --> BugHunter_check_logs: User provides logs
    
    iteration_START_PAIR_PROGRAMMING --> BugHunter_start_pair_programming
    BugHunter_start_pair_programming --> iteration_AWAITING_BUG_FIX: Human provides hint
    BugHunter_start_pair_programming --> complete_task: Human fixed manually
    
    iteration_PROBLEM_SOLVER --> ProblemSolver: Try alternatives
    ProblemSolver --> Developer_breakdown_current_iteration
    
    complete_task --> [*]: Task reviewed
```

Sources:
- [core/agents/troubleshooter.py:39-146]()
- [core/agents/bug_hunter.py:61-361]()
- [core/agents/developer.py:121-202]()

## Troubleshooter Agent

The Troubleshooter agent generates test instructions, collects user feedback, and routes issues to appropriate handlers.

### Main Entry Point: `run()`

The Troubleshooter's `run()` method determines whether to create a new iteration or propose a solution:

```python
# Simplified logic from troubleshooter.py:39-46
async def run(self) -> AgentResponse:
    if self.current_state.unfinished_iterations:
        if current_iteration.status == IterationStatus.FIND_SOLUTION:
            return await self.propose_solution()
    else:
        return await self.create_iteration()
```

Sources:
- [core/agents/troubleshooter.py:39-46]()

### Test Instruction Generation

The Troubleshooter generates test instructions through a two-phase LLM call:

**Test Instruction Generation Sequence**
```mermaid
sequenceDiagram
    participant TS as Troubleshooter
    participant LLM
    participant RoutePrompt as get_route_files.prompt
    participant TestPrompt as define_user_review_goal.prompt
    participant UI
    
    TS->>TS: Check current_task["test_instructions"]
    
    alt No existing instructions
        TS->>LLM: Request route files
        Note over LLM,RoutePrompt: Uses RouteFilePaths schema
        LLM-->>TS: List of files with routes
        
        TS->>LLM: Request test instructions
        Note over LLM,TestPrompt: Uses TestSteps schema
        Note over TestPrompt: Context includes:<br/>- Task description<br/>- Route files content<br/>- Previous/next tasks
        LLM-->>TS: TestSteps with title/action/result
        
        TS->>TS: Save to current_task["test_instructions"]
        TS->>TS: Return AgentResponse.done()
    end
    
    TS->>UI: send_project_stage(ProjectStage.TEST_APP)
    TS->>UI: send_test_instructions(user_instructions)
    TS->>UI: send_run_command(run_command)
```

The `get_user_instructions()` method orchestrates this process:

1. Calls `_get_route_files()` to identify files containing API routes using `RouteFilePaths` schema
2. Uses the `define_user_review_goal` prompt template with route file content
3. LLM generates step-by-step test instructions as `TestSteps` schema
4. Returns `None` if LLM determines no testing is needed (empty steps)

Sources:
- [core/agents/troubleshooter.py:203-231]()
- [core/agents/troubleshooter.py:233-242]()
- [core/prompts/troubleshooter/get_route_files.prompt:1-14]()
- [core/prompts/troubleshooter/define_user_review_goal.prompt:1-83]()

### Run Command Detection

The `get_run_command()` method determines how to start the application:

```python
# From troubleshooter.py:187-201
async def get_run_command(self) -> Optional[str]:
    if self.current_state.run_command:
        return self.current_state.run_command
    
    llm = self.get_llm(TROUBLESHOOTER_GET_RUN_COMMAND)
    convo = self._get_task_convo().template("get_run_command")
    llm_response: str = await llm(convo, temperature=0, parser=OptionalCodeBlockParser())
    
    self.next_state.run_command = llm_response
    return llm_response
```

The LLM analyzes the task breakdown to determine the appropriate command (e.g., `npm run dev`, `python app.py`).

Sources:
- [core/agents/troubleshooter.py:187-201]()

### User Feedback Collection

The `get_user_feedback()` method presents UI buttons and collects feedback:

**User Feedback Flow with UI Interaction**
```mermaid
flowchart TD
    Start["get_user_feedback()"] --> SendStage["send_project_stage(GET_USER_FEEDBACK)"]
    SendStage --> SendRunCmd["send_run_command(run_command)"]
    SendRunCmd --> AskQuestion["ask_question(TS_APP_WORKING)"]
    
    AskQuestion --> UserChoice{"User clicks button"}
    
    UserChoice -->|"continue"| ReturnSuccess["Return (should_iterate=False)"]
    UserChoice -->|"bug"| DescribeIssue["ask_question(TS_DESCRIBE_ISSUE)"]
    UserChoice -->|"change"| DescribeChange["ask_question(describe change)"]
    UserChoice -->|"redo"| ReturnRedo["Return (should_redo=True)"]
    
    DescribeIssue --> CollectLogs["extra_info: collect_logs=True"]
    CollectLogs --> GetRelevant1["get_relevant_files_parallel(bug_report)"]
    GetRelevant1 --> ReturnBug["Return (should_iterate=True,<br/>bug_report=text)"]
    
    DescribeChange --> GetRelevant2["get_relevant_files_parallel(change_desc)"]
    GetRelevant2 --> ReturnChange["Return (should_iterate=True,<br/>change_description=text)"]
```

The method returns a tuple: `(should_iterate, is_loop, should_redo, bug_report, change_description)`

Button mapping in code:
- `"continue"` → No iteration needed, task complete
- `"bug"` → Creates iteration with `status=HUNTING_FOR_BUG`
- `"change"` → Creates iteration with `status=NEW_FEATURE_REQUESTED`
- `"redo"` → Resets task and asks for clarification

Sources:
- [core/agents/troubleshooter.py:244-346]()
- [core/config/actions.py]() (TS_APP_WORKING, TS_DESCRIBE_ISSUE constants)

### Iteration Creation

After collecting feedback, `create_iteration()` creates an iteration record:

```python
# Simplified from troubleshooter.py:127-146
self.next_state.iterations = self.current_state.iterations + [
    {
        "id": uuid4().hex,
        "user_feedback": user_feedback,
        "user_feedback_qa": user_feedback_qa,
        "description": None,
        "alternative_solutions": [],
        "attempts": 1,
        "status": iteration_status,  # HUNTING_FOR_BUG or NEW_FEATURE_REQUESTED
        "bug_hunting_cycles": [],
    }
]
```

The `iteration_status` determines the next agent:
- `HUNTING_FOR_BUG` → Routes to BugHunter
- `NEW_FEATURE_REQUESTED` → Routes to Developer
- `PROBLEM_SOLVER` → Routes to ProblemSolver (on loop detection)

Sources:
- [core/agents/troubleshooter.py:63-146]()
- [core/agents/troubleshooter.py:111-144]()

### Loop Detection and Alternative Solutions

The Troubleshooter detects loops when iterations exceed `LOOP_THRESHOLD = 3`:

```python
# From troubleshooter.py:22-23, 142-144
LOOP_THRESHOLD = 3

if len(self.next_state.iterations) == LOOP_THRESHOLD:
    await self.trace_loop("loop-start")
```

Loop detection logic:
1. Counts iterations for current task
2. If iterations ≥ 3 without resolution, sets `status=PROBLEM_SOLVER`
3. Calls `try_next_alternative_solution()` to attempt different approaches
4. Records telemetry via `trace_loop()` for monitoring

Sources:
- [core/agents/troubleshooter.py:22]()
- [core/agents/troubleshooter.py:112-119]()
- [core/agents/troubleshooter.py:142-144]()
- [core/agents/troubleshooter.py:348-366]()
- [core/agents/troubleshooter.py:426-434]()

### Task Completion

When user confirms everything works, `complete_task()` finalizes the task:

```python
# From troubleshooter.py:148-159
async def complete_task(self) -> AgentResponse:
    if len(self.current_state.iterations) >= LOOP_THRESHOLD:
        await self.trace_loop("loop-end")
    
    current_task_index1 = self.current_state.tasks.index(self.current_state.current_task) + 1
    self.next_state.action = TS_TASK_REVIEWED.format(current_task_index1)
    self.next_state.set_current_task_status(TaskStatus.REVIEWED)
    return AgentResponse.done(self)
```

This marks the task as `TaskStatus.REVIEWED`, allowing TechLead to proceed to the next task.

Sources:
- [core/agents/troubleshooter.py:148-159]()

## BugHunter Agent

The BugHunter agent investigates bugs through log analysis, reproduction steps, and interactive pair programming.

### Main Entry Point: `run()`

The BugHunter's `run()` method routes to different strategies based on iteration status:

```python
# Simplified from bug_hunter.py:61-80
async def run(self) -> AgentResponse:
    current_iteration = self.current_state.current_iteration
    
    if "bug_reproduction_description" not in current_iteration:
        # Async task to generate reproduction instructions
        self.state_manager.async_tasks.append(
            asyncio.create_task(self.get_bug_reproduction_instructions())
        )
    
    if current_iteration["status"] == IterationStatus.HUNTING_FOR_BUG:
        return await self.check_logs()
    elif current_iteration["status"] == IterationStatus.AWAITING_USER_TEST:
        return await self.ask_user_to_test(False, True)
    elif current_iteration["status"] == IterationStatus.AWAITING_BUG_REPRODUCTION:
        return await self.ask_user_to_test(True, False)
    elif current_iteration["status"] == IterationStatus.START_PAIR_PROGRAMMING:
        return await self.start_pair_programming()
```

Sources:
- [core/agents/bug_hunter.py:61-80]()
- [core/agents/bug_hunter.py:82-101]()

### Bug Reproduction Instructions

The BugHunter generates reproduction steps asynchronously using `get_bug_reproduction_instructions()`:

```python
# From bug_hunter.py:82-101
async def get_bug_reproduction_instructions(self):
    llm = self.get_llm()
    convo = (
        AgentConvo(self)
        .template(
            "get_bug_reproduction_instructions",
            current_task=self.current_state.current_task,
            user_feedback=self.current_state.current_iteration["user_feedback"],
            user_feedback_qa=self.current_state.current_iteration["user_feedback_qa"],
            docs=self.current_state.docs,
        )
        .require_schema(TestSteps)
    )
    bug_reproduction_instructions: TestSteps = await llm(convo, parser=JSONParser(TestSteps))
    self.next_state.current_iteration["bug_reproduction_description"] = json.dumps(
        [test.dict() for test in bug_reproduction_instructions.steps]
    )
```

This generates detailed steps for the user to reproduce the bug, which helps collect relevant logs.

Sources:
- [core/agents/bug_hunter.py:82-101]()
- [core/agents/mixins.py:27-34]() (TestSteps schema)

### Log Analysis: `check_logs()`

The `check_logs()` method analyzes conversation history to determine if more logs are needed or if the bug is identified:

**Bug Hunting Decision Flow**
```mermaid
flowchart TD
    Start["check_logs()"] --> GenConvo["generate_iteration_convo_so_far()"]
    GenConvo --> StreamLLM["LLM generates human_readable_instructions"]
    StreamLLM --> ChatBreakdown["chat_with_breakdown()"]
    
    ChatBreakdown --> ConclusionPrompt["Analyze with bug_found_or_add_logs prompt"]
    ConclusionPrompt --> LLMDecision{"LLM returns\nHuntConclusionType"}
    
    LLMDecision -->|"PROBLEM_IDENTIFIED"| SetBugFix["set_data_for_next_hunting_cycle()<br/>status = AWAITING_BUG_FIX"]
    LLMDecision -->|"ADD_LOGS"| SetLogging["set_data_for_next_hunting_cycle()<br/>status = AWAITING_LOGGING"]
    
    SetBugFix --> SendFixMsg["send_message('Found the bug')"]
    SetLogging --> SendLogMsg["send_message('Adding more logs')"]
    
    SendFixMsg --> UpdateUI1["send_bug_hunter_status('fixing_bug')"]
    SendLogMsg --> UpdateUI2["send_bug_hunter_status('adding_logs')"]
    
    UpdateUI1 --> ReturnDone["AgentResponse.done()"]
    UpdateUI2 --> ReturnDone
```

The `HuntConclusionType` enum uses `magic_words`:
- `ADD_LOGS` → Need more diagnostic logging
- `PROBLEM_IDENTIFIED` → Bug root cause found

Sources:
- [core/agents/bug_hunter.py:103-142]()
- [core/agents/bug_hunter.py:31-39]() (HuntConclusionType, HuntConclusionOptions)
- [core/agents/bug_hunter.py:363-391]() (generate_iteration_convo_so_far)
- [core/agents/bug_hunter.py:400-411]() (set_data_for_next_hunting_cycle)

### Bug Hunting Cycles

Each bug hunting attempt creates a cycle stored in `bug_hunting_cycles`:

```python
# From bug_hunter.py:400-411
def set_data_for_next_hunting_cycle(self, human_readable_instructions, new_status):
    self.next_state.current_iteration["description"] = human_readable_instructions
    self.next_state.current_iteration["bug_hunting_cycles"] += [
        {
            "human_readable_instructions": human_readable_instructions,
            "fix_attempted": any(
                c["fix_attempted"] for c in self.current_state.current_iteration["bug_hunting_cycles"]
            ),
        }
    ]
    self.next_state.current_iteration["status"] = new_status
```

The conversation builder in `generate_iteration_convo_so_far()` includes all previous cycles:

```python
# From bug_hunter.py:363-391
for hunting_cycle in hunting_cycles:
    convo = convo.assistant(hunting_cycle["human_readable_instructions"]).template(
        "log_data",
        backend_logs=hunting_cycle.get("backend_logs"),
        frontend_logs=hunting_cycle.get("frontend_logs"),
        fix_attempted=hunting_cycle.get("fix_attempted"),
        user_feedback=hunting_cycle.get("user_feedback"),
    )
```

This provides full context to the LLM for making informed decisions.

Sources:
- [core/agents/bug_hunter.py:363-391]()
- [core/agents/bug_hunter.py:400-411]()

### User Testing After Fix

The `ask_user_to_test()` method handles two scenarios via boolean flags:

**User Testing Workflow**
```mermaid
flowchart TD
    Start["ask_user_to_test(awaiting_bug_reproduction, awaiting_user_test)"] --> SendInstructions["send_test_instructions(bug_reproduction_description)"]
    SendInstructions --> SendRunCmd["send_run_command()"]
    SendRunCmd --> AskDone["ask_question(BH_HUMAN_TEST_AGAIN)"]
    
    AskDone --> IsUserTest{"awaiting_user_test?"}
    
    IsUserTest -->|"Yes"| AskFixed["ask_question(BH_IS_BUG_FIXED)"]
    AskFixed --> FixedResponse{"User response"}
    
    FixedResponse -->|"yes"| CompleteIter["complete_iteration()"]
    FixedResponse -->|"no"| SetReproduce["awaiting_bug_reproduction = True"]
    FixedResponse -->|"start_pair_programming"| SetPair1["status = START_PAIR_PROGRAMMING"]
    
    IsUserTest -->|"No"| IsReproduce{"awaiting_bug_reproduction?"}
    
    IsReproduce -->|"Yes"| AskFeedback["ask_question(BH_ADDITIONAL_FEEDBACK)<br/>extra_info: collect_logs=True"]
    AskFeedback --> FeedbackResponse{"User response"}
    
    FeedbackResponse -->|"done"| CompleteIter2["complete_iteration()"]
    FeedbackResponse -->|"start_pair_programming"| SetPair2["status = START_PAIR_PROGRAMMING"]
    FeedbackResponse -->|"continue or text"| SetHunting["Store logs in bug_hunting_cycles<br/>status = HUNTING_FOR_BUG<br/>attempts += 1"]
    
    SetReproduce --> IsReproduce
```

Key behaviors:
1. **awaiting_user_test=True**: After fix implementation, ask if bug is resolved
2. **awaiting_bug_reproduction=True**: After logging added, ask user to reproduce with logs
3. Logs collected via `extra_info: {"collect_logs": True}` flag
4. User can escalate to pair programming at any point

Sources:
- [core/agents/bug_hunter.py:144-239]()
- [core/config/actions.py]() (BH_HUMAN_TEST_AGAIN, BH_IS_BUG_FIXED, BH_ADDITIONAL_FEEDBACK)

### Pair Programming Mode

The `start_pair_programming()` method enables interactive debugging:

**Pair Programming Interaction Loop**
```mermaid
flowchart TD
    Start["start_pair_programming()"] --> ExplainProblem["LLM generates initial_explanation"]
    ExplainProblem --> GetLogData["LLM generates ImportantLogsForDebugging"]
    GetLogData --> SendLogs["send_data_about_logs(logs)"]
    
    SendLogs --> AskAction["ask_question(What do you want to do?)"]
    AskAction --> UserChoice{"User clicks button"}
    
    UserChoice -->|"done"| Complete["complete_iteration()"]
    UserChoice -->|"question"| AskQ["ask_question(what would you like to know?)"]
    UserChoice -->|"tell_me_more"| TellMore["LLM explains more details"]
    UserChoice -->|"solution_hint"| SolutionFlow["Human provides hint"]
    UserChoice -->|"other"| AskOther["ask_question(Let me know...)"]
    
    AskQ --> LLMAnswer1["LLM answers question"]
    TellMore --> LLMAnswer2["LLM provides more info"]
    AskOther --> LLMAnswer3["LLM responds"]
    
    LLMAnswer1 --> AskAction
    LLMAnswer2 --> AskAction
    LLMAnswer3 --> AskAction
    
    SolutionFlow --> GetHint["ask_question(How do you think we can solve?)"]
    GetHint --> GenerateFix["LLM generates implementation instructions"]
    GenerateFix --> AskApproval["ask_question(Can I implement this?)"]
    AskApproval --> Approval{"User approves?"}
    
    Approval -->|"yes"| SetFix["set_data_for_next_hunting_cycle()<br/>status = AWAITING_BUG_FIX"]
    Approval -->|"no"| GetHint
    
    SetFix --> Complete
```

The `ImportantLogsForDebugging` schema provides structured log analysis:

```python
# From bug_hunter.py:42-54
class ImportantLog(BaseModel):
    logCode: str  # Actual line of code that prints the log
    shouldBeDifferent: bool  # Whether output should differ from expected
    filePath: str
    currentOutput: str
    expectedOutput: str
    explanation: str

class ImportantLogsForDebugging(BaseModel):
    logs: list[ImportantLog]
```

This data is sent to the UI via `send_data_about_logs()` for visual presentation.

Sources:
- [core/agents/bug_hunter.py:241-361]()
- [core/agents/bug_hunter.py:42-54]() (ImportantLog, ImportantLogsForDebugging schemas)
- [core/config/actions.py]() (BH_STARTING_PAIR_PROGRAMMING)

## Integration with Developer Agent

Both QA agents route to the Developer agent for implementation. The Developer's `breakdown_current_iteration()` method handles QA-initiated changes:

**Developer Iteration Handling**
```mermaid
flowchart TD
    Start["Developer.breakdown_current_iteration()"] --> CheckStatus{"iteration.status"}
    
    CheckStatus -->|"AWAITING_BUG_FIX"| GetBugInstructions["description = bug_hunting_cycles[-1][human_readable_instructions]"]
    CheckStatus -->|"AWAITING_LOGGING"| GetLogInstructions["description = bug_hunting_cycles[-1][human_readable_instructions]"]
    CheckStatus -->|"IMPLEMENT_SOLUTION"| GetSolution["description = iteration[description]"]
    
    GetBugInstructions --> GetRelevant["get_relevant_files_parallel()"]
    GetLogInstructions --> GetRelevant
    GetSolution --> GetRelevant
    
    GetRelevant --> ParseTask["LLM call with parse_task prompt"]
    ParseTask --> SetSteps["set_next_steps(response)"]
    
    SetSteps --> UpdateStatus{"Update iteration status"}
    
    UpdateStatus -->|"AWAITING_BUG_FIX"| SetTestStatus["status = AWAITING_USER_TEST"]
    UpdateStatus -->|"AWAITING_LOGGING"| SetReproduceStatus["status = AWAITING_BUG_REPRODUCTION"]
    UpdateStatus -->|"IMPLEMENT_SOLUTION"| CompleteIter["complete_iteration()"]
    
    SetTestStatus --> Done["AgentResponse.done()"]
    SetReproduceStatus --> Done
    CompleteIter --> Done
```

Key logic from Developer agent:

```python
# Simplified from developer.py:129-195
if iteration["status"] == IterationStatus.AWAITING_BUG_FIX:
    # After bug fix, ask user to test
    self.next_state.action = DEV_WAIT_TEST
    self.next_state.current_iteration["status"] = IterationStatus.AWAITING_USER_TEST
elif iteration["status"] == IterationStatus.AWAITING_LOGGING:
    # After adding logs, ask user to reproduce
    self.next_state.current_iteration["status"] = IterationStatus.AWAITING_BUG_REPRODUCTION
```

Sources:
- [core/agents/developer.py:121-202]()
- [core/agents/developer.py:129-195]() (iteration status handling)

## Completing Tasks

When the user confirms that everything works correctly, the Troubleshooter:

1. Calls `complete_task()` method
2. Records loop telemetry if needed
3. Sets the current task status to `TaskStatus.REVIEWED`
4. Returns control to the Orchestrator with `AgentResponse.done()`

Sources:
- [core/agents/troubleshooter.py:134-147]()

## Implementation Details

### Mixins

The Troubleshooter leverages several mixins:

1. **ChatWithBreakdownMixin**: Enables interactive refinement of breakdown explanations
2. **IterationPromptMixin**: Provides solution generation functionality based on user feedback
3. **RelevantFilesMixin**: Identifies files related to the current issue or task

These mixins provide modular functionality that's shared across multiple agents, allowing the Troubleshooter to focus on its core responsibilities.

Sources:
- [core/agents/mixins.py:53-92]()
- [core/agents/mixins.py:95-132]()
- [core/agents/mixins.py:135-191]()

### Key Methods

The Troubleshooter's key methods include:

- `run()`: Entry point that determines whether to create or continue an iteration
- `get_run_command()`: Determines how to run the application for testing
- `get_user_instructions()`: Generates testing instructions for the user
- `get_user_feedback()`: Collects and processes user feedback about the application
- `find_solution()`: Generates solutions for reported issues (from IterationPromptMixin)
- `trace_loop()`: Records telemetry data when a solution loop is detected

Sources:
- [core/agents/troubleshooter.py:34-45]()
- [core/agents/troubleshooter.py:166-180]()
- [core/agents/troubleshooter.py:182-222]()
- [core/agents/troubleshooter.py:223-307]()
- [core/agents/mixins.py:95-132]()
- [core/agents/troubleshooter.py:387-395]()

## Conclusion

The Troubleshooter Agent serves as a crucial bridge between code implementation and bug fixing, managing the testing process and directing work to specialized agents as needed. By systematically collecting user feedback and creating structured iterations, it ensures issues are tracked and resolved methodically. Its integration with the Bug Hunter agent enables effective debugging of complex problems, while its loop detection capabilities prevent the system from getting stuck in repetitive fix attempts.

---

# Page: Specialized Agents

# Specialized Agents

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [core/agents/legacy_handler.py](core/agents/legacy_handler.py)
- [core/agents/wizard.py](core/agents/wizard.py)
- [core/db/migrations/versions/f708791b9270_adding_knowledge_base_field_to_.py](core/db/migrations/versions/f708791b9270_adding_knowledge_base_field_to_.py)
- [core/prompts/troubleshooter/define_user_review_goal.prompt](core/prompts/troubleshooter/define_user_review_goal.prompt)
- [core/prompts/troubleshooter/get_route_files.prompt](core/prompts/troubleshooter/get_route_files.prompt)
- [core/templates/tree/vite_react/client/src/api/api.ts](core/templates/tree/vite_react/client/src/api/api.ts)
- [core/templates/tree/vite_react_swagger/client/.env](core/templates/tree/vite_react_swagger/client/.env)
- [core/templates/tree/vite_react_swagger/client/src/api/api.ts](core/templates/tree/vite_react_swagger/client/src/api/api.ts)

</details>



This page documents specialized agents that handle specific workflows outside the main development lifecycle. These agents support project initialization, legacy migration, and utility functions.

For documentation on the main development agents (SpecWriter, Architect, TechLead), see [Planning Agents](#4.2). For code generation agents, see [Implementation Agents](#4.3) and [Frontend Development Agent](#4.4). For quality assurance agents, see [Quality Assurance Agents](#4.5).

---

## Overview

The GPT Pilot agent system includes several specialized agents that handle edge cases and initialization workflows:

| Agent | Type | Primary Responsibility |
|-------|------|----------------------|
| **Wizard** | `wizard` | Project initialization, template setup, authentication configuration |
| **LegacyHandler** | `legacy-handler` | Backward compatibility for deprecated workflows |
| **CodeReviewer** | `code-review` | Code quality analysis (referenced in configuration) |

These agents extend the `BaseAgent` class but operate outside the standard planning-implementation-testing cycle documented in pages 4.2-4.5.

Sources: [core/agents/wizard.py:20-28](), [core/agents/legacy_handler.py:5-14]()

---

## Wizard Agent

### Purpose and Entry Point

The `Wizard` agent is the first agent to run in a new project. It orchestrates project initialization by:
1. Setting up the selected project template
2. Configuring authentication methods for Swagger projects
3. Creating the initial `KnowledgeBase` instance
4. Defining the first epic ("Build frontend")

The Wizard is invoked at the start of the orchestration flow and transitions to the SpecWriter agent upon completion.

**Workflow Diagram: Wizard Agent Initialization**

```mermaid
graph TB
    Start["Orchestrator starts new project"] --> WizardRun["Wizard.run()"]
    
    WizardRun --> InitTemplate["init_template()"]
    
    InitTemplate --> CheckType{"Project type?"}
    
    CheckType -->|"'swagger'"| SwaggerFlow["Swagger Project Flow"]
    CheckType -->|"other"| StandardFlow["Standard Project Flow"]
    
    SwaggerFlow --> AskDocs["ask_question()<br/>Request OpenAPI/Swagger docs"]
    AskDocs --> UploadDocs["upload_docs()<br/>POST to PYTHAGORA_API/rag/upload"]
    UploadDocs --> ParseResponse["Parse external_api_url and types"]
    
    ParseResponse --> AuthConfig["Authentication Configuration"]
    AuthConfig --> AskAuthType["ask_question()<br/>buttons: none, api_key, bearer, etc."]
    
    AskAuthType --> CheckAuth{"Auth type?"}
    CheckAuth -->|"'api_key'"| AskKey["ask_question()<br/>Request API key"]
    CheckAuth -->|"'none'"| NoAuth["Set auth_type='none'"]
    CheckAuth -->|"other"| Telemetry["telemetry.trace_code_event()<br/>Track requested auth method"]
    
    AskKey --> StoreKey["Store in options['api_key']"]
    NoAuth --> CreateKB
    StoreKey --> CreateKB
    Telemetry --> CreateKB
    
    StandardFlow --> SetLoginAuth["Set auth_type='login'"]
    SetLoginAuth --> CreateKB
    
    CreateKB["Create KnowledgeBase instance<br/>pages=[], apis=[], user_options, utility_functions=[]"]
    CreateKB --> AddToSession["session.add(knowledge_base)<br/>next_state.knowledge_base = knowledge_base"]
    
    AddToSession --> CreateEpic["Create first epic:<br/>id=uuid4().hex<br/>name='Build frontend'<br/>source='frontend'"]
    
    CreateEpic --> ReturnTrue["return True"]
    ReturnTrue --> WizardDone["Wizard.run() returns<br/>AgentResponse.create_specification(self)"]
    
    WizardDone --> NextAgent["Orchestrator transitions to<br/>SpecWriter agent"]
    
    style WizardRun fill:#f9f9f9
    style CreateKB fill:#f9f9f9
    style WizardDone fill:#f9f9f9
```

Sources: [core/agents/wizard.py:24-28](), [core/agents/wizard.py:30-131]()

---

### Swagger Project Initialization

For projects with `project_type == "swagger"`, the Wizard performs additional steps to integrate with external APIs:

#### 1. OpenAPI Documentation Upload

The agent requests OpenAPI/Swagger documentation from the user and uploads it to a RAG (Retrieval-Augmented Generation) service:

```mermaid
sequenceDiagram
    participant User
    participant Wizard
    participant RAGService as PYTHAGORA_API/rag/upload
    participant StateManager

    User->>Wizard: Paste OpenAPI/Swagger docs
    
    loop up to 3 attempts
        Wizard->>RAGService: POST /rag/upload<br/>{text: docs, project_id}
        
        alt Success (200)
            RAGService-->>Wizard: {external_api_url, types}
            Wizard->>Wizard: Store external_api_url and types
            Note over Wizard: Break retry loop
        else Token Expired (403)
            RAGService-->>Wizard: 403 Forbidden
            Wizard->>User: send_token_expired()
            User-->>Wizard: New access token
            Wizard->>StateManager: update_access_token()
        else Error
            RAGService-->>Wizard: Error response
            Note over Wizard: Log error, retry
        end
    end
    
    alt Upload Failed
        Wizard->>User: "An error occurred while uploading the docs"
        Wizard-->>StateManager: return False (project creation aborted)
    else Upload Succeeded
        Wizard->>Wizard: Proceed to authentication config
    end
```

The upload returns two critical pieces of information:
- `external_api_url`: The base URL for the external API
- `types`: Authentication types supported by the API (e.g., `["apiKey", "bearer"]`)

Sources: [core/agents/wizard.py:41-58](), [core/agents/wizard.py:133-174]()

#### 2. Authentication Configuration

After uploading the API documentation, the Wizard prompts the user to select an authentication method:

**Authentication Flow Diagram**

```mermaid
stateDiagram-v2
    [*] --> AskAuthType: Display auth options
    
    AskAuthType --> APIKey: User selects "api_key"
    AskAuthType --> None: User selects "none"
    AskAuthType --> ComingSoon: User selects bearer/oauth2/openid
    
    APIKey --> CheckSupported: Verify "apiKey" in types
    CheckSupported --> WarnUnsupported: Not supported
    WarnUnsupported --> ConfirmContinue: Ask "Do you want to continue?"
    ConfirmContinue --> APIKey: User says "no"
    ConfirmContinue --> RequestKey: User says "yes"
    CheckSupported --> RequestKey: Supported
    
    RequestKey --> StoreCredentials: Store api_key in options
    StoreCredentials --> [*]
    
    None --> StoreAuthType: Set auth_type="none"
    StoreAuthType --> [*]
    
    ComingSoon --> AskTelemetry: "Can we contact you?"
    AskTelemetry --> SendTelemetry: User says "yes"
    AskTelemetry --> AskAuthType: User says "no"
    SendTelemetry --> TelemetryEvent: telemetry.trace_code_event("swagger-auth-method")
    TelemetryEvent --> AskAuthType
    
    note right of APIKey
        Currently implemented:
        - API Key authentication
        - No authentication
        
        Coming soon:
        - HTTP Bearer
        - OAuth2
        - OpenID Connect
    end note
```

The authentication configuration is stored in the `user_options` field of the `KnowledgeBase` and used by project templates to generate appropriate authentication code.

Sources: [core/agents/wizard.py:60-111]()

---

### Knowledge Base Creation

The Wizard creates a `KnowledgeBase` instance that persists throughout the project lifecycle:

```python
knowledge_base = KnowledgeBase(
    pages=[],                    # Frontend pages/components
    apis=[],                     # Backend API endpoints
    user_options=options,        # Contains auth_type, api_key, external_api_url
    utility_functions=[]         # Reusable helper functions
)
```

**Key fields in `user_options`:**

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `auth_type` | `str` | Authentication method | `"api_key"`, `"login"`, `"none"` |
| `api_key` | `str` | API key for external service (if applicable) | `"sk_test_123abc..."` |
| `external_api_url` | `str` | Base URL for external API (swagger only) | `"https://api.example.com"` |

This knowledge base is attached to the `ProjectState` and becomes available to all subsequent agents.

Sources: [core/agents/wizard.py:113-117]()

---

### Template Configuration Integration

The authentication settings configured by the Wizard are propagated to project templates via Jinja2 templating. The templates use conditional logic to generate appropriate API client code:

**API Client Template Structure:**

```mermaid
graph TB
    UserOptions["user_options from KnowledgeBase"] --> TemplateEngine["Jinja2 Template Engine"]
    
    TemplateEngine --> CheckAuthType{"options.auth_type"}
    
    CheckAuthType -->|"'api_key'"| APIKeyBlock["Generate API key header injection:<br/>config.headers['api_key'] = API_KEY"]
    CheckAuthType -->|"'login'"| LoginBlock["Generate Bearer token auth:<br/>config.headers.Authorization = Bearer token"]
    CheckAuthType -->|"'none'"| NoAuthBlock["No authentication code"]
    
    CheckAuthType -->|"not 'login'"| ExternalAPI["Generate externalApi axios instance:<br/>baseURL: EXTERNAL_API_URL"]
    CheckAuthType -->|"'login'"| LocalOnly["Only localApi instance"]
    
    APIKeyBlock --> SetupInterceptors["setupInterceptors(localApi)<br/>setupInterceptors(externalApi)"]
    LoginBlock --> SetupInterceptors
    NoAuthBlock --> SetupInterceptors
    ExternalAPI --> SetupInterceptors
    LocalOnly --> SetupInterceptors
    
    SetupInterceptors --> GeneratedFile["client/src/api/api.ts"]
    
    style UserOptions fill:#f9f9f9
    style GeneratedFile fill:#f9f9f9
```

**Example: API Key Authentication Template**

The generated `api.ts` file includes conditional blocks based on `options.auth_type`:

- **Lines 4-6**: Import API key from environment variable if `auth_type == "api_key"`
- **Lines 8-10**: Import external API URL if `auth_type != "login"`
- **Lines 22-32**: Create `externalApi` axios instance for external services
- **Lines 58-64**: Inject API key header in request interceptor

Sources: [core/templates/tree/vite_react/client/src/api/api.ts:4-6](), [core/templates/tree/vite_react/client/src/api/api.ts:58-64]()

The same pattern is used in the Vite React Swagger template:

Sources: [core/templates/tree/vite_react_swagger/client/src/api/api.ts:4-6](), [core/templates/tree/vite_react_swagger/client/src/api/api.ts:58-64]()

**Environment Variable Template:**

For Swagger projects with API key authentication, the Wizard also generates a `.env` file:

```
VITE_API_KEY={{ options.api_key }}
VITE_EXTERNAL_API_URL={{ options.external_api_url }}
```

Sources: [core/templates/tree/vite_react_swagger/client/.env:1-6]()

---

### Initial Epic Creation

The final step of the Wizard's initialization is creating the first epic:

```python
self.next_state.epics = [
    {
        "id": uuid4().hex,
        "name": "Build frontend",
        "source": "frontend",
        "description": "",
        "messages": [],
        "summary": None,
        "completed": False,
    }
]
```

This epic serves as the entry point for the Frontend agent (see [Frontend Development Agent](#4.4)). The TechLead agent may add additional epics during the planning phase.

Sources: [core/agents/wizard.py:119-129]()

---

## LegacyHandler Agent

### Purpose

The `LegacyHandler` agent provides backward compatibility for deprecated workflows. It handles legacy action types that existed in previous versions of GPT Pilot but have been superseded by newer agent implementations.

**Agent Structure:**

```python
class LegacyHandler(BaseAgent):
    agent_type = "legacy-handler"
    display_name = "Legacy Handler"
    
    async def run(self) -> AgentResponse:
        if self.data["type"] == "review_task":
            self.next_state.complete_step("review_task")
            return AgentResponse.done(self)
        
        raise ValueError(f"Unknown reason for calling Legacy Handler with data: {self.data}")
```

Sources: [core/agents/legacy_handler.py:5-14]()

### Supported Legacy Actions

Currently, the LegacyHandler supports one legacy action type:

| Legacy Action | Behavior | Migration Path |
|---------------|----------|----------------|
| `review_task` | Completes the "review_task" step in the project state | Task review functionality has been integrated into the Developer and CodeMonkey agents |

**Legacy Action Flow:**

```mermaid
sequenceDiagram
    participant Orchestrator
    participant LegacyHandler
    participant StateManager
    
    Orchestrator->>LegacyHandler: Call with data={type: "review_task"}
    LegacyHandler->>LegacyHandler: Check data["type"] == "review_task"
    LegacyHandler->>StateManager: next_state.complete_step("review_task")
    StateManager-->>LegacyHandler: Step marked complete
    LegacyHandler->>Orchestrator: AgentResponse.done(self)
    
    Note over Orchestrator: Continue to next step
```

For any unrecognized legacy action type, the agent raises a `ValueError` with diagnostic information.

Sources: [core/agents/legacy_handler.py:9-14]()

---

## CodeReviewer Agent

### Configuration Reference

The CodeReviewer agent is mentioned in the LLM configuration system but does not have an implementation in the provided source files. It is referenced in agent-to-model mapping:

**Configuration Example (from Diagram 4):**

```json
{
  "agent": {
    "code-review": {
      "provider": "anthropic",
      "model": "claude-3-5-sonnet-20241022"
    }
  }
}
```

This suggests that code review functionality is intended to use Claude 3.5 Sonnet for higher quality analysis. The agent would analyze generated code for:
- Code quality and best practices
- Security vulnerabilities
- Performance issues
- Consistency with project patterns

**Note:** This agent is not currently active in the workflow but is configured for future use.

Sources: High-level system architecture diagrams (Diagram 4)

---

## Integration with Main Workflow

### Agent Invocation Map

The following diagram shows how specialized agents integrate with the main orchestration flow:

```mermaid
graph LR
    Start([New Project]) --> Wizard
    ContinueProject([Continue Project]) --> CheckLegacy{Legacy action?}
    
    Wizard["Wizard<br/>init_template()"] -->|"AgentResponse.create_specification()"| SpecWriter
    
    CheckLegacy -->|Yes| LegacyHandler
    CheckLegacy -->|No| CurrentAgent[Current Agent]
    
    LegacyHandler["LegacyHandler<br/>complete_step()"] -->|"AgentResponse.done()"| NextStep[Next Step]
    
    CurrentAgent --> Planning[Planning Agents]
    Planning --> Implementation[Implementation Agents]
    Implementation --> QA[QA Agents]
    
    SpecWriter[SpecWriter] --> Architect[Architect]
    Architect --> TechLead[TechLead]
    TechLead --> Developer[Developer]
    Developer --> CodeMonkey[CodeMonkey]
    CodeMonkey --> Frontend[Frontend]
    Frontend --> Troubleshooter[Troubleshooter]
    Troubleshooter --> BugHunter[BugHunter]
    
    BugHunter -.->|Bug fixed| CodeMonkey
    Troubleshooter -.->|New feature| TechLead
    
    style Wizard fill:#f9f9f9
    style LegacyHandler fill:#f9f9f9
```

### State Transitions

Specialized agents use specific `AgentResponse` types to signal the orchestrator:

| Agent | Return Type | Next State |
|-------|-------------|------------|
| Wizard | `AgentResponse.create_specification(self)` | Transition to SpecWriter |
| LegacyHandler | `AgentResponse.done(self)` | Continue to next step in workflow |

Sources: [core/agents/wizard.py:24-28](), [core/agents/legacy_handler.py:9-12]()

---

## Database Schema Integration

### KnowledgeBase Model

The `KnowledgeBase` instance created by the Wizard is persisted as part of the `ProjectState`:

**Schema Evolution:**

A database migration added the `knowledge_base` field to the `project_states` table:

```python
def upgrade() -> None:
    with op.batch_alter_table("project_states", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("knowledge_base", sa.JSON(), server_default="{}", nullable=False)
        )
```

This allows the knowledge base to be:
- Versioned with each project state commit
- Rolled back when using the `--step` flag
- Queried by all subsequent agents

Sources: [core/db/migrations/versions/f708791b9270_adding_knowledge_base_field_to_.py:21-26]()

**Knowledge Base Access Pattern:**

```python
# Reading knowledge base (all agents)
current_kb = self.current_state.knowledge_base

# Modifying knowledge base (agent workflow)
session = inspect(self.next_state).async_session
session.add(knowledge_base)
self.next_state.knowledge_base = knowledge_base
```

Sources: [core/agents/wizard.py:115-117]()

---

## Best Practices for Extending Specialized Agents

When adding new specialized agents to GPT Pilot:

1. **Inherit from BaseAgent**: All agents must extend `BaseAgent` and implement `async def run() -> AgentResponse`

2. **Define agent metadata**:
   ```python
   agent_type = "my-agent"  # Lowercase with hyphens
   display_name = "My Agent"  # Human-readable name
   ```

3. **Use appropriate response types**:
   - `AgentResponse.done(self)` - Complete current step, continue workflow
   - `AgentResponse.exit(self)` - Abort project initialization
   - `AgentResponse.create_specification(self)` - Transition to SpecWriter

4. **Leverage StateManager transaction model**:
   - Read from `self.current_state` (immutable)
   - Write to `self.next_state` (working copy)
   - Commit happens automatically after `run()` completes

5. **Handle errors gracefully**:
   - Use retry loops for external API calls
   - Provide clear error messages to users via `send_message()`
   - Use `capture_exception()` for telemetry

Sources: [core/agents/wizard.py:20-28](), [core/agents/wizard.py:136-174](), [core/agents/legacy_handler.py:5-14]()

---

# Page: LLM Integration

# Configuration and LLM Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [core/agents/base.py](core/agents/base.py)
- [core/config/__init__.py](core/config/__init__.py)
- [core/llm/anthropic_client.py](core/llm/anthropic_client.py)
- [core/llm/azure_client.py](core/llm/azure_client.py)
- [core/llm/base.py](core/llm/base.py)
- [core/llm/openai_client.py](core/llm/openai_client.py)
- [core/utils/__init__.py](core/utils/__init__.py)
- [core/utils/text.py](core/utils/text.py)
- [data/database/.gitkeep](data/database/.gitkeep)
- [example-config.json](example-config.json)
- [tests/agents/test_base.py](tests/agents/test_base.py)
- [tests/config/test_config.py](tests/config/test_config.py)
- [tests/config/test_env_importer.py](tests/config/test_env_importer.py)
- [tests/llm/test_openai.py](tests/llm/test_openai.py)
- [tests/ui/test_ipc_client.py](tests/ui/test_ipc_client.py)

</details>



This document explains how GPT Pilot's configuration system works and how it integrates with various LLM (Large Language Model) providers. It covers the configuration structure, configuration loading process, supported LLM providers, and how different agents connect to these providers.

For information about the actual configuration options for specific agents, see [Core Agents](#3).

## Configuration System Overview

GPT Pilot uses a JSON-based configuration system that allows customization of LLM providers, agent-specific model selection, database connections, logging, and file system options. The configuration can be specified in a JSON file and optionally overridden via command-line arguments.

### Configuration Hierarchy

```mermaid
graph TD
    subgraph "Configuration System"
        Config["Config"]
        --> LLMConfig["LLM Provider Configs"]
        --> ProviderConfig["ProviderConfig"]
        
        Config --> AgentConfig["Agent LLM Configs"]
        --> AgentLLMConfig["AgentLLMConfig"]
        
        Config --> OtherConfig["Other Configurations"]
        OtherConfig --> DBConfig["DBConfig"]
        OtherConfig --> LogConfig["LogConfig"]
        OtherConfig --> UIConfig["UIConfig"]
        OtherConfig --> FSConfig["FileSystemConfig"]
        OtherConfig --> PromptConfig["PromptConfig"]

        LLMConfig -.-> CompleteLLM["Complete LLM Configuration"]
        AgentConfig -.-> CompleteLLM
        
        CommandLine["Command Line Arguments"]
        --> ConfigOverrides["Configuration Overrides"]
        --> Config
    end
```

Sources: [core/config/__init__.py:314-420](), [core/cli/helpers.py:144-190]()

### Configuration File Structure

The configuration file is a JSON document with the following top-level sections:

```
{
  "llm": { ... },      // LLM provider configurations
  "agent": { ... },    // Agent-specific LLM configurations
  "prompt": { ... },   // Prompt template configuration
  "log": { ... },      // Logging configuration
  "db": { ... },       // Database configuration
  "ui": { ... },       // UI configuration
  "fs": { ... }        // File system configuration
}
```

Sources: [example-config.json:1-89](), [config-docker.json:1-136]()

### Provider Configurations

The `llm` section contains provider-specific configurations:

```json
"llm": {
  "openai": {
    "base_url": "https://api.openai.com/v1/",
    "api_key": "your-api-key",
    "connect_timeout": 60.0,
    "read_timeout": 20.0
  },
  "anthropic": {
    "base_url": "https://api.anthropic.com",
    "api_key": "your-api-key",
    "connect_timeout": 60.0,
    "read_timeout": 20.0
  }
}
```

Each provider configuration maps to the `ProviderConfig` class which includes:
- `base_url`: The base URL for the provider's API
- `api_key`: API key for authentication
- `connect_timeout`: Timeout for establishing connection
- `read_timeout`: Timeout for receiving response chunks
- `extra`: Additional provider-specific configuration

Sources: [core/config/__init__.py:87-114](), [example-config.json:5-31]()

### Agent-Specific LLM Configurations

The `agent` section configures which LLM each agent uses:

```json
"agent": {
  "default": {
    "provider": "openai",
    "model": "gpt-4o-2024-05-13",
    "temperature": 0.5
  },
  "CodeMonkey": {
    "provider": "anthropic",
    "model": "claude-3-5-sonnet-20241022",
    "temperature": 0.0
  }
}
```

This allows different agents to use different models or providers based on their specific needs. The system includes optimized defaults for various specialized agent functions.

Sources: [core/config/__init__.py:116-132](), [core/config/__init__.py:325-394](), [config-docker.json:18-88]()

## Configuration Loading Process

The following diagram illustrates how configuration is loaded, merged, and used in the system:

```mermaid
sequenceDiagram
    participant CLI as "CLI"
    participant ConfigLoader as "ConfigLoader"
    participant Config as "Config Object"
    participant StateManager as "StateManager"
    participant LLMClient as "LLM Client"
    
    CLI->>ConfigLoader: parse_arguments()
    CLI->>ConfigLoader: load_config(args)
    ConfigLoader->>ConfigLoader: Check if file exists
    ConfigLoader->>ConfigLoader: import_from_dotenv()
    ConfigLoader->>ConfigLoader: Open and read file
    ConfigLoader->>Config: from_json(text_config)
    ConfigLoader->>Config: Apply command-line overrides
    CLI->>StateManager: Initialize with config
    StateManager->>LLMClient: Initialize with agent config
    LLMClient->>LLMClient: _init_client()
```

Sources: [core/cli/helpers.py:144-190](), [core/cli/helpers.py:303-329]()

### Default Configuration

GPT Pilot provides sensible defaults when no specific configuration is provided. The default configuration includes:

1. Default LLM provider is OpenAI with model `gpt-4o-2024-05-13`
2. Specialized agent configurations for different tasks:
   - Code generation tasks use Anthropic Claude models
   - Code review uses Claude 3.5 Sonnet
   - Simple tasks like describing files use smaller models
   - Long-context tasks use models with larger context windows

Sources: [core/config/__init__.py:325-394](), [config-docker.json:18-88]()

## LLM Provider Integration

GPT Pilot integrates with multiple LLM providers through a provider-agnostic client interface.

### LLM Integration Architecture

```mermaid
graph TD
    subgraph "Agent System"
        Agent["Base Agent"]
        Developer["Developer Agent"]
        CodeMonkey["Code Monkey Agent"]
        BugHunter["Bug Hunter Agent"]
    end
    
    subgraph "LLM Integration Layer"
        Agent --> BaseLLMClient["BaseLLMClient (Abstract)"]
        Developer --> BaseLLMClient
        CodeMonkey --> BaseLLMClient
        BugHunter --> BaseLLMClient
        
        BaseLLMClient --> OpenAIClient["OpenAIClient"]
        BaseLLMClient --> AnthropicClient["AnthropicClient"]
        BaseLLMClient --> GroqClient["GroqClient"]
        BaseLLMClient --> AzureClient["AzureClient"]
    end
    
    subgraph "External APIs"
        OpenAIClient --> OpenAI_API["OpenAI API"]
        AnthropicClient --> Anthropic_API["Anthropic API"]
        GroqClient --> Groq_API["Groq API"]
        AzureClient --> Azure_API["Azure OpenAI API"]
    end
    
    Config["Config"] --> Agent
    Config --> BaseLLMClient
```

Sources: [core/llm/anthropic_client.py:26-152](), [core/config/__init__.py:65-74]()

### Supported Providers

GPT Pilot supports the following LLM providers:

| Provider   | Class            | Description                             |
|------------|------------------|-----------------------------------------|
| OpenAI     | OpenAIClient     | OpenAI API (GPT-4, GPT-3.5)            |
| Anthropic  | AnthropicClient  | Anthropic Claude models                 |
| Groq       | GroqClient       | Groq API (Llama, Mixtral)              |
| Azure      | AzureClient      | Azure OpenAI API                        |
| LM Studio  | OpenAIClient     | Local models via OpenAI-compatible API  |

The system determines which client to use based on the provider specified in the agent or default configuration.

Sources: [core/config/__init__.py:65-74](), [example-config.json:5-31]()

### Provider-Specific Adaptations

Each provider client handles provider-specific adaptations:

1. Message format conversions
2. API-specific parameters
3. Timeout configuration
4. Rate limiting behavior
5. Error handling

For example, the Anthropic client converts message formats between GPT Pilot's internal format and Claude's expected format:

```python
def _adapt_messages(self, convo: Convo) -> list[dict[str, str]]:
    """
    Adapt the conversation messages to the format expected by the Anthropic Claude model.
    Claude only recognizes "user" and "assistant" roles...
    """
```

Sources: [core/llm/anthropic_client.py:41-66]()

### Special Configuration for AWS Bedrock

GPT Pilot includes special handling for AWS Bedrock, which requires model names to be adapted to the AWS naming conventions:

```mermaid
graph LR
    Config["Config"] --> BedrockAdapter["adapt_for_bedrock()"]
    BedrockAdapter --> AdaptedConfig["Adapted Config"]
    
    subgraph "Model Name Mapping"
        StandardName["Standard Model Names<br/>(e.g., claude-3-5-sonnet-20241022)"]
        -->
        BedrockName["Bedrock Model Names<br/>(e.g., us.anthropic.claude-3-5-sonnet-20241022-v2:0)"]
    end
```

Sources: [core/config/__init__.py:485-510]()

## Command-Line Configuration

GPT Pilot allows overriding configuration values via command-line arguments.

### Available Command-Line Options

| Option | Description |
|--------|-------------|
| `--config` | Path to configuration file |
| `--level` | Log level (DEBUG, INFO, etc.) |
| `--database` | Database URL |
| `--local-ipc-port` | Local IPC port (for VS Code extension) |
| `--llm-endpoint` | LLM provider endpoint (`provider:url`) |
| `--llm-key` | LLM provider API key (`provider:key`) |

Sources: [core/cli/helpers.py:74-141](), [tests/cli/test_cli.py:34-64]()

### Example Usage

```bash
python -m core --config my-config.json --level INFO --llm-endpoint openai:https://api.openai.com/v1/ --llm-key anthropic:sk-your-key
```

This would:
1. Load configuration from `my-config.json`
2. Set log level to INFO
3. Set OpenAI endpoint to the specified URL
4. Set Anthropic API key to the specified value

Sources: [core/cli/helpers.py:144-190](), [tests/cli/test_cli.py:144-155]()

## Agent-Specific LLM Selection

One of GPT Pilot's most powerful features is the ability to use different LLMs for different agent tasks. This allows optimal model selection based on task requirements.

```mermaid
graph LR
    subgraph "Agent System"
        TechLead["TechLead"]
        Developer["Developer"]
        CodeMonkey["CodeMonkey"]
        CodeReview["CodeMonkey.code_review"]
        DescribeFiles["CodeMonkey.describe_files"]
        BugHunter["BugHunter.check_logs"]
    end
    
    subgraph "Model Selection"
        TechLead --> Claude3["Claude 3.5 Sonnet"]
        Developer --> Claude3
        CodeMonkey --> Claude3
        CodeReview --> Claude3["Claude 3.5 Sonnet"]
        DescribeFiles --> GPTMini["GPT-4o Mini"]
        BugHunter --> Claude3
    end
```

The default configuration uses:
- High-capability Claude models for complex reasoning tasks (planning, code generation)
- Smaller, faster models for simpler tasks (file description)
- Different temperature settings based on task needs (lower for code generation, higher for creative tasks)

Sources: [core/config/__init__.py:325-394](), [config-docker.json:18-88]()

## Common Usage Patterns

### Setting Up a New Provider

To add a new provider configuration:

1. Add provider credentials to your config file:
   ```json
   "llm": {
     "anthropic": {
       "api_key": "sk-your-anthropic-key",
       "connect_timeout": 60.0,
       "read_timeout": 30.0
     }
   }
   ```

2. Configure an agent to use this provider:
   ```json
   "agent": {
     "CodeMonkey": {
       "provider": "anthropic",
       "model": "claude-3-5-sonnet-20241022",
       "temperature": 0.0
     }
   }
   ```

Sources: [example-config.json:5-31](), [example-config.json:35-40]()

### Using Different Models for Specialized Tasks

The default configuration already includes specialized model assignments for different tasks:

```json
"agent": {
  "default": {
    "provider": "openai",
    "model": "gpt-4o-2024-05-13",
    "temperature": 0.5
  },
  "BugHunter.check_logs": {
    "provider": "anthropic",
    "model": "claude-3-5-sonnet-20241022",
    "temperature": 0.5
  },
  "CodeMonkey.describe_files": {
    "provider": "openai",
    "model": "gpt-4o-mini-2024-07-18",
    "temperature": 0.0
  }
}
```

This configures:
- `default`: Most agents use OpenAI GPT-4o
- `BugHunter.check_logs`: Bug hunting uses Claude 3.5 Sonnet
- `CodeMonkey.describe_files`: File description uses a smaller GPT-4o Mini model

Sources: [core/config/__init__.py:325-394](), [config-docker.json:18-88]()

## Conclusion

GPT Pilot's configuration system provides a flexible way to customize LLM provider integration. The system supports:

1. Multiple LLM providers (OpenAI, Anthropic, Groq, Azure)
2. Agent-specific model selection and parameters
3. Command-line overrides for quick testing
4. Sensible defaults for optimal performance

This allows GPT Pilot to leverage the strengths of different LLM providers and models for various development tasks, optimizing for cost, performance, and capability.

---

# Page: Configuration System

# Configuration System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [core/config/__init__.py](core/config/__init__.py)
- [core/llm/anthropic_client.py](core/llm/anthropic_client.py)
- [data/database/.gitkeep](data/database/.gitkeep)
- [example-config.json](example-config.json)
- [tests/config/test_config.py](tests/config/test_config.py)
- [tests/config/test_env_importer.py](tests/config/test_env_importer.py)

</details>



This page documents the configuration system for GPT Pilot, which allows users to customize LLM providers, agent behaviors, database settings, filesystem preferences, and UI options. For information about LLM provider integration specifically, see [LLM Provider Integration](#5.2).

## Configuration Overview

The configuration system in GPT Pilot provides a flexible way to configure all aspects of the application through a combination of JSON files, environment variables, and command-line arguments. The system is built using the Pydantic library for validation, ensuring that all configuration values are type-safe and properly validated before use.

```mermaid
graph TD
    subgraph "Configuration Sources" 
        JSON["JSON Config Files"] --> ConfigLoader
        ENV["Environment Variables"] --> EnvImporter["Environment Importer"]
        CLI["Command-line Arguments"] --> CLIParser["CLI Parser"]
        EnvImporter --> ConfigLoader
        CLIParser --> ConfigOverrides["Config Overrides"]
    end
    
    subgraph "Configuration Processing"
        ConfigLoader --> Config
        ConfigOverrides --> Config
        Config --> "get_config()"
        "get_config()" --> ApplicationComponents["Application Components"]
    end
    
    subgraph "Configuration Consumers"
        ApplicationComponents --> AgentSystem["Agent System"]
        ApplicationComponents --> LLMClients["LLM Clients"]
        ApplicationComponents --> Database
        ApplicationComponents --> FileSystem["File System"]
        ApplicationComponents --> UserInterface["User Interface"]
        ApplicationComponents --> LogSystem["Logging System"]
    end
```

Sources:
[core/config/__init__.py:412-513]()
[core/cli/helpers.py:144-190]()

## Configuration Structure

The configuration system is hierarchically organized with the main `Config` class containing all settings. The configuration is divided into several key sections, each handling different aspects of the application.

```mermaid
classDiagram
    class Config {
        +dict[LLMProvider, ProviderConfig] llm
        +dict[str, AgentLLMConfig] agent
        +PromptConfig prompt
        +LogConfig log
        +DBConfig db
        +UIConfig ui
        +FileSystemConfig fs
        +llm_for_agent(agent_name: str) LLMConfig
        +all_llms() list[LLMConfig]
    }
    
    Config --> ProviderConfig : contains
    Config --> AgentLLMConfig : contains
    Config --> PromptConfig : contains
    Config --> LogConfig : contains
    Config --> DBConfig : contains
    Config --> UIConfig : contains
    Config --> FileSystemConfig : contains
    
    class ProviderConfig {
        +str? base_url
        +str? api_key
        +float connect_timeout
        +float read_timeout
        +dict? extra
    }
    
    class AgentLLMConfig {
        +LLMProvider? provider
        +str model
        +float temperature
    }
    
    class LLMConfig {
        +LLMProvider provider
        +str model
        +str? base_url
        +str? api_key
        +float temperature
        +float connect_timeout
        +float read_timeout
        +dict? extra
    }
    
    class UIConfig {
        +UIAdapter type
    }
    
    UIConfig <|-- PlainUIConfig
    UIConfig <|-- LocalIPCConfig
    UIConfig <|-- VirtualUIConfig
    
    class FileSystemConfig {
        +FileSystemType type
        +str workspace_root
        +list[str] ignore_paths
        +int ignore_size_threshold
    }
    
    class DBConfig {
        +str url
        +bool debug_sql
    }
    
    class LogConfig {
        +str level
        +str format
        +str? output
    }
    
    class PromptConfig {
        +list[str] paths
    }
```

Sources:
[core/config/__init__.py:87-399]()

## Configuration Loading Process

The configuration loading process follows a defined sequence that determines the precedence of different configuration sources:

1. **Default Values**: Hardcoded defaults are defined in the `Config` class
2. **JSON Files**: Configuration loaded from JSON files via `ConfigLoader`
3. **Environment Variables**: Optional import from environment variables
4. **Command-line Arguments**: Override specific settings from the CLI

The `ConfigLoader` class manages the parsing and loading of configuration files, while command-line argument handling is implemented in the CLI module.

```mermaid
sequenceDiagram
    participant App as Application
    participant CLI as CLI Parser
    participant Loader as ConfigLoader
    participant Config as Config Class
    
    App->>CLI: parse_arguments()
    CLI-->>App: args
    
    App->>Loader: load(args.config)
    Note over Loader: Check if file exists
    
    alt Config file exists
        Loader->>Loader: Read and parse JSON
        Loader->>Config: Create Config object
    else Config file does not exist
        Loader->>Loader: import_from_dotenv()
        Note over Loader: Try to import from .env
        Loader->>Config: Create default Config
    end
    
    App->>App: Apply CLI overrides
    Note over App: Override log level, database URL, etc.
    
    App->>App: get_config()
    Note over App: Final config ready for use
```

Sources:
[core/config/__init__.py:422-482]()
[core/cli/helpers.py:144-190]()

## LLM Providers Configuration

GPT Pilot supports multiple LLM providers, each with its own configuration settings. The providers are defined in the `LLMProvider` enum.

### Supported Providers

| Provider  | Model Format | Description |
|-----------|--------------|-------------|
| OPENAI    | `gpt-4o-2024-05-13`, `gpt-4-0125-preview`, etc. | OpenAI API models |
| ANTHROPIC | `claude-3-5-sonnet-20241022`, `claude-3-haiku-20240307`, etc. | Anthropic Claude models |
| GROQ      | Anthropic and OpenAI compatible models | Groq hosted models |
| LM_STUDIO | Local LLM APIs with OpenAI-compatible interface | Local model hosting |
| AZURE     | OpenAI models on Azure | Azure OpenAI Service |

### Provider Configuration

Each provider is configured through the `ProviderConfig` class, which includes:

- `base_url`: Base API endpoint URL (optional, uses provider defaults)
- `api_key`: API key for authentication (optional, falls back to environment variables)
- `connect_timeout`: Timeout for establishing connection
- `read_timeout`: Timeout for receiving data
- `extra`: Provider-specific additional configuration

```json
{
  "llm": {
    "openai": {
      "base_url": "https://api.openai.com/v1",
      "api_key": null,
      "connect_timeout": 60.0,
      "read_timeout": 20.0
    },
    "anthropic": {
      "base_url": "https://api.anthropic.com",
      "api_key": null,
      "connect_timeout": 60.0,
      "read_timeout": 20.0
    }
  }
}
```

Sources:
[core/config/__init__.py:65-75]()
[core/config/__init__.py:87-113]()
[example-config.json:1-31]()

## Agent-Specific LLM Configuration

A key feature of the configuration system is the ability to assign different LLM models to different agents or agent tasks. This allows for optimization of resource usage by using more capable models only where necessary.

### Agent Configuration Structure

Agent configurations are stored in a dictionary mapping agent names to their LLM configurations:

```json
{
  "agent": {
    "default": {
      "provider": "openai",
      "model": "gpt-4o-2024-05-13",
      "temperature": 0.5
    },
    "CodeMonkey": {
      "provider": "anthropic",
      "model": "claude-3-5-sonnet-20241022",
      "temperature": 0.0
    },
    "CodeMonkey.code_review": {
      "provider": "anthropic",
      "model": "claude-3-5-sonnet-20240620",
      "temperature": 0.0
    }
  }
}
```

The default configuration includes optimized settings for each agent type, with specific models assigned based on the task requirements. For example, code generation tasks use Anthropic's Claude models with low temperature, while the Spec Writer agent uses OpenAI's GPT-4.

### Agent Configuration Resolution

The `llm_for_agent()` method combines a provider configuration with an agent-specific configuration to create a complete `LLMConfig` for use by the agent:

```mermaid
flowchart LR
    AgentName["Agent Name"] --> LookupAgentConfig["Lookup Agent Config"]
    
    subgraph "Config Resolution"
        LookupAgentConfig --> AgentExists{Agent config exists?}
        AgentExists -- Yes --> GetAgentConfig["Get agent.{name}"]
        AgentExists -- No --> GetDefaultAgent["Get agent.default"]
        
        GetAgentConfig --> GetProvider["Get provider from agent config"]
        GetDefaultAgent --> GetProvider
        
        GetProvider --> GetProviderConfig["Get llm.{provider}"]
        
        GetProviderConfig --> CombineConfigs["Combine configs with LLMConfig.from_provider_and_agent_configs()"]
    end
    
    CombineConfigs --> CompleteLLMConfig["Complete LLMConfig"]
```

Sources:
[core/config/__init__.py:116-132]()
[core/config/__init__.py:134-181]()
[core/config/__init__.py:401-412]()
[config-docker.json:18-88]()

## Database Configuration

The database configuration determines how GPT Pilot stores project data, using SQLAlchemy as the ORM layer.

### Database URL Format

The database URL follows SQLAlchemy's format, with GPT Pilot supporting:

- SQLite with aiosqlite driver: `sqlite+aiosqlite:///path/to/database.db`
- PostgreSQL with asyncpg driver: `postgresql+asyncpg://user:password@host:port/dbname`

```python
class DBConfig(_StrictModel):
    url: str = Field(
        "sqlite+aiosqlite:///data/database/pythagora.db",
        description="Database connection URL",
    )
    debug_sql: bool = Field(False, description="Log all SQL queries to the console")
```

The database configuration is validated to ensure only supported database engines are used, and that the necessary dependencies are installed for PostgreSQL.

Sources:
[core/config/__init__.py:223-249]()
[example-config.json:49-54]()

## File System Configuration

The file system configuration controls how GPT Pilot interacts with project files, including workspace location and file filtering.

### Workspace and Ignore Patterns

```python
class FileSystemConfig(_StrictModel):
    type: Literal[FileSystemType.LOCAL] = FileSystemType.LOCAL
    workspace_root: str = Field(
        join(ROOT_DIR, "workspace"),
        description="Workspace directory containing all the projects",
    )
    ignore_paths: list[str] = Field(
        DEFAULT_IGNORE_PATHS,
        description="List of paths to ignore when scanning for files and folders",
    )
    ignore_size_threshold: int = Field(
        IGNORE_SIZE_THRESHOLD,
        description="Files larger than this size should be ignored",
    )
```

By default, GPT Pilot ignores common directories and files that don't contain user code, such as:
- Version control directories (`.git`)
- IDE config directories (`.idea`, `.vscode`)
- Dependency directories (`node_modules`, `site-packages`)
- Build artifacts (`dist`, `build`)
- Minified files (`*.min.js`, `*.min.css`)
- Large binary files (over 50KB by default)

Sources:
[core/config/__init__.py:285-311]()
[core/config/__init__.py:9-32]()
[example-config.json:58-88]()

## UI Configuration

GPT Pilot supports multiple UI adapters for different use cases:

```mermaid
graph TD
    subgraph "UI Configuration" 
        UIConfig["UIConfig Base Class"] --> UIAdapter{UI Adapter Type}
        
        UIAdapter -- "plain" --> PlainUIConfig["Plain Console UI"]
        UIAdapter -- "ipc-client" --> LocalIPCConfig["IPC Client for VSCode"]
        UIAdapter -- "virtual" --> VirtualUIConfig["Virtual UI for Testing"]
        
        PlainUIConfig --> ConsoleUI["Console Implementation"]
        LocalIPCConfig --> IPCClientUI["IPC Client Implementation"]
        VirtualUIConfig --> VirtualUI["Virtual UI Implementation"]
    end
    
    subgraph "UI Implementations"
        ConsoleUI --> Terminal["Terminal I/O"]
        IPCClientUI --> VSCodeExt["VS Code Extension"]
        VirtualUI --> TestSystem["Automated Testing"]
    end
```

Each UI adapter has its own configuration options:

| UI Type | Configuration | Use Case |
|---------|--------------|----------|
| `plain` | Default terminal UI | Standard console interaction |
| `ipc-client` | Host and port settings | VS Code extension integration |
| `virtual` | Predefined inputs | Automated testing |

Sources:
[core/config/__init__.py:77-84]()
[core/config/__init__.py:252-282]()
[core/cli/helpers.py:317-329]()

## Command-Line Configuration Overrides

Command-line arguments can override configuration settings for flexibility and testing. The main overrides include:

```
--config           Path to the configuration file
--level            Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
--database         Database URL
--local-ipc-port   Local IPC port for VS Code extension
--local-ipc-host   Local IPC host for VS Code extension
--llm-endpoint     Override LLM API endpoint (format: provider:url)
--llm-key          Override LLM API key (format: provider:key)
```

When these arguments are provided, they take precedence over the values in the configuration file.

Sources:
[core/cli/helpers.py:74-141]()
[tests/cli/test_cli.py:133-156]()

## Configuration Example

Here's a complete configuration example showing the major customization options:

```json
{
  "llm": {
    "openai": {
      "base_url": "https://api.openai.com/v1",
      "api_key": "your-api-key",
      "connect_timeout": 60.0,
      "read_timeout": 20.0
    },
    "anthropic": {
      "base_url": "https://api.anthropic.com",
      "api_key": "your-api-key",
      "connect_timeout": 60.0,
      "read_timeout": 20.0
    }
  },
  "agent": {
    "default": {
      "provider": "openai",
      "model": "gpt-4o-2024-05-13",
      "temperature": 0.5
    },
    "CodeMonkey": {
      "provider": "anthropic",
      "model": "claude-3-5-sonnet-20241022",
      "temperature": 0.0
    }
  },
  "log": {
    "level": "DEBUG",
    "format": "%(asctime)s %(levelname)s [%(name)s] %(message)s",
    "output": "pythagora.log"
  },
  "db": {
    "url": "sqlite+aiosqlite:///data/database/pythagora.db",
    "debug_sql": false
  },
  "ui": {
    "type": "plain"
  },
  "fs": {
    "type": "local",
    "workspace_root": "workspace",
    "ignore_paths": [".git", "node_modules", "dist", "*.min.js"],
    "ignore_size_threshold": 50000
  }
}
```

Sources:
[example-config.json:1-89]()

## Working with Configuration Programmatically

The configuration system provides helper functions for accessing configuration in code:

1. `get_config()`: Returns the current active configuration
2. `loader.load(path)`: Loads configuration from a file path
3. `config.llm_for_agent(agent_name)`: Gets LLM configuration for a specific agent

Example of getting configuration for a specific agent:

```python
from core.config import get_config

config = get_config()
llm_config = config.llm_for_agent("CodeMonkey")

# Use the config with an LLM client
client = LLMClient.for_provider(llm_config.provider)(llm_config)
```

Sources:
[core/config/__init__.py:513-519]()
[core/config/__init__.py:401-412]()
[core/llm/anthropic_client.py:29-39]()

## Configuration Validation

All configuration classes use Pydantic for validation, ensuring that:

1. Configuration values have the correct types
2. Required fields are present
3. Numeric values are within allowed ranges
4. Enum values are valid
5. Configuration structure matches the expected schema

When invalid configuration is detected, detailed error messages are provided to help identify the issue.

Sources:
[core/config/__init__.py:55-62]()
[tests/config/test_config.py:90-94]()

---

# Page: LLM Client Architecture

# LLM Provider Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [cloud/posthog.html](cloud/posthog.html)
- [core/agents/base.py](core/agents/base.py)
- [core/config/__init__.py](core/config/__init__.py)
- [core/llm/anthropic_client.py](core/llm/anthropic_client.py)
- [core/llm/azure_client.py](core/llm/azure_client.py)
- [core/llm/base.py](core/llm/base.py)
- [core/llm/openai_client.py](core/llm/openai_client.py)
- [core/llm/relace_client.py](core/llm/relace_client.py)
- [core/utils/__init__.py](core/utils/__init__.py)
- [core/utils/text.py](core/utils/text.py)
- [data/database/.gitkeep](data/database/.gitkeep)
- [example-config.json](example-config.json)
- [tests/agents/test_base.py](tests/agents/test_base.py)
- [tests/config/test_config.py](tests/config/test_config.py)
- [tests/config/test_env_importer.py](tests/config/test_env_importer.py)
- [tests/llm/test_openai.py](tests/llm/test_openai.py)
- [tests/ui/test_ipc_client.py](tests/ui/test_ipc_client.py)

</details>



This page documents how GPT Pilot integrates with various Language Model providers, enabling communication between the agent system and external LLM APIs. It covers the configuration system, supported providers, client implementations, and how different agents use different models based on their needs.

For information about the overall configuration system, see [Configuration System](#5.1).

## Overview

GPT Pilot uses a flexible LLM integration architecture that allows connecting to multiple providers (OpenAI, Anthropic, Groq, etc.) and configuring different models for different agents. This enables specialized model selection based on the specific requirements of each agent.

```mermaid
flowchart TD
    subgraph "Agent Layer"
        TL["TechLead"]
        Dev["Developer"]
        CM["CodeMonkey"]
        BH["BugHunter"]
        TS["Troubleshooter"]
    end

    subgraph "LLM Integration Layer"
        LC["LLM Client"]
        LC --> OpenAI["OpenAI Client"]
        LC --> Anthropic["Anthropic Client"]
        LC --> Groq["Groq Client"]
        LC --> Azure["Azure Client"]
    end

    subgraph "External APIs"
        OpenAI --> OpenAI_API["OpenAI API"]
        Anthropic --> Anthropic_API["Anthropic API"]
        Groq --> Groq_API["Groq API"]
        Azure --> Azure_API["Azure OpenAI API"]
    end

    TL --> LC
    Dev --> LC
    CM --> LC
    BH --> LC
    TS --> LC

    Config["Config System"] --> LC
```

Sources: [core/config/__init__.py:65-74](), [core/llm/anthropic_client.py](), [pyproject.toml:26-42]()

## Supported LLM Providers

GPT Pilot supports the following LLM providers:

| Provider | Enum Value | Default Base URL | Client Library |
|----------|------------|------------------|---------------|
| OpenAI   | `OPENAI`   | api.openai.com   | openai        |
| Anthropic | `ANTHROPIC` | api.anthropic.com | anthropic   |
| Groq     | `GROQ`     | api.groq.com     | groq          |
| Azure    | `AZURE`    | *.openai.azure.com | openai      |
| LM-Studio | `LM_STUDIO` | localhost:1234 | openai (compatible) |

Each provider is represented in the codebase by an enum value in the `LLMProvider` class:

```python
class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    LM_STUDIO = "lm-studio"
    AZURE = "azure"
```

Sources: [core/config/__init__.py:65-74](), [requirements.txt:1-36](), [pyproject.toml:26-42]()

## Configuration System

The LLM integration uses a multi-layered configuration approach:

1. **Provider-level configuration** - Basic connection settings for each LLM provider
2. **Agent-specific configuration** - Model selection and temperature settings for each agent
3. **Complete LLM configuration** - Combined settings used for actual API calls

```mermaid
classDiagram
    class ProviderConfig {
        base_url: Optional[str]
        api_key: Optional[str]
        connect_timeout: float
        read_timeout: float
        extra: Optional[dict]
    }
    
    class AgentLLMConfig {
        provider: LLMProvider
        model: str
        temperature: float
    }
    
    class LLMConfig {
        provider: LLMProvider
        model: str
        base_url: Optional[str]
        api_key: Optional[str]
        temperature: float
        connect_timeout: float
        read_timeout: float
        extra: Optional[dict]
        +from_provider_and_agent_configs()
    }
    
    class Config {
        llm: dict[LLMProvider, ProviderConfig]
        agent: dict[str, AgentLLMConfig]
        +llm_for_agent(agent_name: str)
    }
    
    Config "1" --> "*" ProviderConfig: contains
    Config "1" --> "*" AgentLLMConfig: contains
    LLMConfig ..> ProviderConfig: created from
    LLMConfig ..> AgentLLMConfig: created from
```

Sources: [core/config/__init__.py:87-181](), [core/config/__init__.py:319-412]()

### Provider Configuration

The `ProviderConfig` class defines connection settings for an LLM provider:

```python
class ProviderConfig:
    base_url: Optional[str]  # Base URL for the provider's API
    api_key: Optional[str]   # API key for authentication
    connect_timeout: float   # Timeout for connecting to the API
    read_timeout: float      # Timeout for receiving response chunks
    extra: Optional[dict]    # Provider-specific extra configuration
```

When a `base_url` is not specified, the system uses the provider's default URL. Similarly, when `api_key` is not specified, the system looks for the API key in environment variables.

Sources: [core/config/__init__.py:87-113](), [example-config.json:1-89]()

### Agent-Specific LLM Configuration

Each agent can be configured to use a different LLM provider and model:

```python
class AgentLLMConfig:
    provider: Optional[LLMProvider]  # LLM provider to use
    model: str                       # Model name
    temperature: float               # Sampling temperature
```

The system provides sensible defaults for different agents. For example:

| Agent | Default Provider | Default Model | Default Temperature |
|-------|-----------------|---------------|---------------------|
| Default | OpenAI | gpt-4o-2024-05-13 | 0.5 |
| CodeMonkey | Anthropic | claude-3-5-sonnet-20241022 | 0.0 |
| BugHunter.check_logs | Anthropic | claude-3-5-sonnet-20241022 | 0.5 |
| Frontend | Anthropic | claude-3-5-sonnet-20241022 | 0.0 |
| SpecWriter | OpenAI | gpt-4-0125-preview | 0.0 |

Sources: [core/config/__init__.py:116-131](), [core/config/__init__.py:325-393](), [config-docker.json:18-88]()

### Complete LLM Configuration

The complete LLM configuration combines provider and agent-specific settings:

```python
class LLMConfig:
    provider: LLMProvider  # LLM provider to use
    model: str             # Model name
    base_url: Optional[str] # Base URL for the provider's API
    api_key: Optional[str]  # API key for authentication
    temperature: float      # Sampling temperature
    connect_timeout: float  # Connection timeout
    read_timeout: float     # Read timeout
    extra: Optional[dict]   # Extra provider-specific configuration
```

The `Config.llm_for_agent()` method fetches the appropriate LLM configuration for a given agent by combining the provider config with the agent-specific LLM config:

```python
def llm_for_agent(self, agent_name: str = "default") -> LLMConfig:
    agent_name = agent_name if agent_name in self.agent else "default"
    agent_config = self.agent[agent_name]
    provider_config = self.llm[agent_config.provider]
    return LLMConfig.from_provider_and_agent_configs(provider_config, agent_config)
```

Sources: [core/config/__init__.py:134-181](), [core/config/__init__.py:401-412]()

## LLM Client Architecture

The LLM client architecture follows a common interface pattern with provider-specific implementations:

```mermaid
classDiagram
    class BaseLLMClient {
        <<abstract>>
        +config: LLMConfig
        +stream_handler: Optional[Callable]
        +_init_client()
        +_make_request()
        +rate_limit_sleep()
    }
    
    class AnthropicClient {
        +provider: LLMProvider.ANTHROPIC
        +_init_client()
        +_adapt_messages()
        +_make_request()
        +rate_limit_sleep()
    }
    
    class OpenAIClient {
        +provider: LLMProvider.OPENAI
        +_init_client()
        +_adapt_messages()
        +_make_request()
        +rate_limit_sleep()
    }
    
    class GroqClient {
        +provider: LLMProvider.GROQ
        +_init_client()
        +_adapt_messages()
        +_make_request()
        +rate_limit_sleep()
    }
    
    BaseLLMClient <|-- AnthropicClient
    BaseLLMClient <|-- OpenAIClient
    BaseLLMClient <|-- GroqClient

    class Convo {
        +messages: list[dict]
        +add_message()
        +get_system_prompt()
    }
    
    BaseLLMClient --> Convo: uses
```

Sources: [core/llm/anthropic_client.py:13-152](), [core/llm/anthropic_client.py:27-39]()

### Provider-Specific Implementations

Each provider has a specific implementation that handles:

1. **Client initialization** - Setting up the provider's API client
2. **Message adaptation** - Converting the internal message format to the provider's expected format
3. **Request handling** - Making API requests and handling response streaming
4. **Rate limit handling** - Detecting and responding to rate limit errors

For example, the Anthropic client implementation handles the specific requirements of Claude models:

```python
class AnthropicClient(BaseLLMClient):
    provider = LLMProvider.ANTHROPIC

    def _init_client(self):
        self.client = AsyncAnthropic(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            timeout=Timeout(
                max(self.config.connect_timeout, self.config.read_timeout),
                connect=self.config.connect_timeout,
                read=self.config.read_timeout,
            ),
        )

    def _adapt_messages(self, convo: Convo) -> list[dict[str, str]]:
        # Claude only recognizes "user" and "assistant" roles
        # Consecutive messages from the same role need to be merged
        messages = []
        for msg in convo.messages:
            if msg["role"] == "function":
                raise ValueError("Anthropic Claude doesn't support function calling")

            role = "user" if msg["role"] in ["user", "system"] else "assistant"
            if messages and messages[-1]["role"] == role:
                messages[-1]["content"] += "\n\n" + msg["content"]
            else:
                messages.append({"role": role, "content": msg["content"]})
        return messages
```

Sources: [core/llm/anthropic_client.py:26-66]()

## Agent-LLM Integration

Agents interact with LLMs through a unified interface, but each agent can be configured to use a different LLM provider and model based on its specific needs:

```mermaid
flowchart TD
    subgraph "Configuration System"
        Config["Config"] --> AgentConfig["Agent Configs"]
        AgentConfig --> TLConfig["TechLead: Claude-3-5-Sonnet"]
        AgentConfig --> DevConfig["Developer: Claude-3-5-Sonnet"]
        AgentConfig --> CMConfig["CodeMonkey: Claude-3-5-Sonnet"]
        AgentConfig --> BHConfig["BugHunter: Claude-3-5-Sonnet"]
        AgentConfig --> SWConfig["SpecWriter: GPT-4"] 
    end
    
    subgraph "Agent System"
        Agent["Agent Base Class"] 
        Agent --> TL["TechLead"]
        Agent --> Dev["Developer"]
        Agent --> CM["CodeMonkey"]
        Agent --> BH["BugHunter"]
        Agent --> SW["SpecWriter"]
    end
    
    TL --> get_llm["get_llm('TechLead.plan_epic')"]
    Dev --> get_llm2["get_llm('Developer.parse_task')"]
    CM --> get_llm3["get_llm('CodeMonkey')"]
    BH --> get_llm4["get_llm('BugHunter.check_logs')"]
    SW --> get_llm5["get_llm('SpecWriter')"]
    
    subgraph "LLM Client Factory"
        Factory["LLM Client Factory"]
        TLConfig --> Factory
        DevConfig --> Factory
        CMConfig --> Factory
        BHConfig --> Factory
        SWConfig --> Factory
        
        get_llm --> Factory
        get_llm2 --> Factory
        get_llm3 --> Factory
        get_llm4 --> Factory
        get_llm5 --> Factory
        
        Factory --> AnthropicClient["Anthropic Client"]
        Factory --> OpenAIClient["OpenAI Client"]
    end
    
    AnthropicClient --> Claude["Claude API"]
    OpenAIClient --> GPT["GPT API"]
```

Sources: [core/config/__init__.py:325-393](), [config-docker.json:18-88]()

### Model Selection Strategy

GPT Pilot uses a thoughtful model selection strategy, matching models to agent capabilities:

| Agent | Default Model | Rationale |
|-------|--------------|-----------|
| TechLead.plan_epic | claude-3-5-sonnet-20240620 | Strong system design and planning capabilities |
| CodeMonkey | claude-3-5-sonnet-20241022 | Excellent code generation with high precision (temp=0.0) |
| BugHunter.check_logs | claude-3-5-sonnet-20241022 | Strong log analysis and pattern recognition |
| SpecWriter | gpt-4-0125-preview | Good requirements analysis and specification writing |
| Developer.describe_files | gpt-4o-mini-2024-07-18 | Simple task that can use a smaller model |

Each agent in the system is configured with a specific provider, model, and temperature setting optimized for its primary task. This allows GPT Pilot to use more capable (but possibly more expensive) models for complex tasks while using smaller, faster models for simpler tasks.

Sources: [core/config/__init__.py:325-393](), [config-docker.json:18-88]()

## Configuration Methods

There are multiple ways to configure LLM providers in GPT Pilot:

### JSON Configuration File

The most flexible way to configure LLM providers is through a JSON configuration file:

```json
{
  "llm": {
    "openai": {
      "base_url": "https://api.openai.com/v1/",
      "api_key": "your-api-key",
      "connect_timeout": 60.0,
      "read_timeout": 20.0
    },
    "anthropic": {
      "base_url": "https://api.anthropic.com",
      "api_key": "your-api-key",
      "connect_timeout": 60.0,
      "read_timeout": 20.0
    }
  },
  "agent": {
    "default": {
      "provider": "openai",
      "model": "gpt-4o-2024-05-13",
      "temperature": 0.5
    },
    "CodeMonkey": {
      "provider": "anthropic",
      "model": "claude-3-5-sonnet-20241022",
      "temperature": 0.0
    }
  }
}
```

This allows configuring:
- Multiple providers with different connection settings
- Different models for different agents
- Custom temperature settings per agent

Sources: [example-config.json:1-89](), [config-docker.json:1-136]()

### Command-Line Arguments

LLM providers can also be configured via command-line arguments:

```
pythagora --llm-endpoint openai:https://custom-openai-endpoint.com --llm-key anthropic:sk-my-anthropic-key
```

The `--llm-endpoint` option sets the base URL for a provider, while `--llm-key` sets the API key.

Sources: [core/cli/helpers.py:23-71](), [core/cli/helpers.py:144-182](), [tests/cli/test_cli.py:66-98]()

### Environment Variables

GPT Pilot can import configuration from environment variables, which is useful for containerized deployments:

```
OPENAI_API_KEY=sk-your-key
ANTHROPIC_API_KEY=sk-ant-your-key
MODEL_NAME=gpt-4o
```

Sources: [core/cli/helpers.py:144-155](), [tests/config/test_env_importer.py:1-80]()

## Advanced Usage

### Provider-Specific Features

Each LLM provider may have specific features that are handled by their client implementation:

#### Anthropic-Specific Features

```python
# Handling Claude's token limits
if "sonnet" in self.config.model:
    completion_kwargs["max_tokens"] = MAX_TOKENS_SONNET  # 8192 tokens
else:
    completion_kwargs["max_tokens"] = MAX_TOKENS  # 4096 tokens

# Support for JSON mode (structured output)
if json_mode:
    completion_kwargs["response_format"] = {"type": "json_object"}

# Special handling for AWS Bedrock
if "bedrock/anthropic" in self.config.base_url:
    completion_kwargs["extra_headers"] = {"anthropic-version": "bedrock-2023-05-31"}
```

Sources: [core/llm/anthropic_client.py:68-90](), [core/config/__init__.py:485-520]()

### Rate Limit Handling

GPT Pilot includes sophisticated rate limit handling for various LLM providers:

```python
def rate_limit_sleep(self, err: RateLimitError) -> Optional[datetime.timedelta]:
    """
    Anthropic rate limits docs:
    https://docs.anthropic.com/en/api/rate-limits#response-headers
    Limit reset times are in RFC 3339 format.
    """
    headers = err.response.headers
    if "anthropic-ratelimit-tokens-remaining" not in headers:
        return None

    remaining_tokens = headers["anthropic-ratelimit-tokens-remaining"]
    if remaining_tokens == 0:
        relevant_dt = headers["anthropic-ratelimit-tokens-reset"]
    else:
        relevant_dt = headers["anthropic-ratelimit-requests-reset"]

    try:
        reset_time = datetime.datetime.fromisoformat(relevant_dt)
    except ValueError:
        return datetime.timedelta(seconds=5)

    try:
        now = datetime.datetime.now(tz=zoneinfo.ZoneInfo("UTC"))
    except zoneinfo.ZoneInfoNotFoundError:
        now = datetime.datetime.now(tz=datetime.timezone.utc)

    return reset_time - now
```

When a rate limit error occurs, the system calculates the appropriate wait time before retrying based on the provider's response headers.

Sources: [core/llm/anthropic_client.py:124-151]()

## Azure OpenAI Support

GPT Pilot includes special support for Azure OpenAI deployments:

```json
{
  "llm": {
    "azure": {
      "base_url": "https://your-resource-name.openai.azure.com/",
      "api_key": "your-api-key",
      "extra": {
        "azure_deployment": "your-azure-deployment-id",
        "api_version": "2024-02-01"
      }
    }
  }
}
```

The Azure OpenAI provider requires additional configuration through the `extra` field to specify the deployment ID and API version.

Sources: [example-config.json:20-30]()

## Conclusion

GPT Pilot's LLM Provider Integration system offers a flexible, extensible architecture for connecting to various LLM providers. Key features include:

1. Support for multiple LLM providers (OpenAI, Anthropic, Groq, Azure)
2. Agent-specific model selection and configuration
3. Multiple configuration methods (JSON, command-line, environment variables)
4. Provider-specific client implementations handling API differences
5. Sophisticated rate limit handling and retry mechanisms

This design allows GPT Pilot to leverage the best model for each specific task while providing a consistent interface for the agent system.

---

# Page: Prompt Engineering System

# Prompt Engineering System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [core/agents/base.py](core/agents/base.py)
- [core/agents/code_monkey.py](core/agents/code_monkey.py)
- [core/llm/azure_client.py](core/llm/azure_client.py)
- [core/llm/base.py](core/llm/base.py)
- [core/llm/openai_client.py](core/llm/openai_client.py)
- [core/prompts/bug-hunter/iteration.prompt](core/prompts/bug-hunter/iteration.prompt)
- [core/prompts/bug-hunter/log_data.prompt](core/prompts/bug-hunter/log_data.prompt)
- [core/prompts/developer/breakdown.prompt](core/prompts/developer/breakdown.prompt)
- [core/prompts/developer/parse_task.prompt](core/prompts/developer/parse_task.prompt)
- [core/prompts/partials/project_tasks.prompt](core/prompts/partials/project_tasks.prompt)
- [core/prompts/problem-solver/get_alternative_solutions.prompt](core/prompts/problem-solver/get_alternative_solutions.prompt)
- [core/prompts/tech-lead/epic_breakdown.prompt](core/prompts/tech-lead/epic_breakdown.prompt)
- [core/prompts/tech-lead/plan.prompt](core/prompts/tech-lead/plan.prompt)
- [core/prompts/troubleshooter/iteration.prompt](core/prompts/troubleshooter/iteration.prompt)
- [core/utils/__init__.py](core/utils/__init__.py)
- [core/utils/text.py](core/utils/text.py)
- [tests/agents/test_base.py](tests/agents/test_base.py)
- [tests/llm/test_openai.py](tests/llm/test_openai.py)
- [tests/ui/test_ipc_client.py](tests/ui/test_ipc_client.py)

</details>



This document details GPT Pilot's prompt engineering system - the technical infrastructure that transforms project state into structured LLM requests. The system handles Jinja2 template processing, context injection, token counting, and intelligent context pruning to maximize LLM effectiveness while staying within token limits.

## Overview

The prompt engineering system sits between the agent layer and the LLM client layer, transforming structured data (project state, files, tasks) into natural language prompts. Key responsibilities:

1. **Template Rendering**: Process Jinja2 templates with project state variables
2. **Context Injection**: Include relevant files, tasks, and user feedback
3. **Token Management**: Count tokens using `tiktoken` and prune context when necessary
4. **Prompt Composition**: Combine reusable partials into agent-specific prompts

The system is invoked through `AgentConvo.template()` method in [core/agents/convo.py](), which agents use to construct prompts before calling their LLM client.

Sources: [core/agents/base.py:175-223](), [core/llm/base.py:124-413](), [core/agents/convo.py]()

## Prompt Engineering Architecture

**Diagram: Prompt Template to LLM Request Flow**

```mermaid
graph TB
    subgraph "Agent Layer"
        Developer["Developer Agent"]
        CodeMonkey["CodeMonkey Agent"]
        TechLead["TechLead Agent"]
    end

    subgraph "Prompt Template System"
        AgentConvo["AgentConvo.template()"]
        TemplateLoader["Jinja2 TemplateLoader<br/>core/prompts/"]
        
        breakdown["breakdown.prompt"]
        implement["implement_changes.prompt"]
        plan["plan.prompt"]
        
        partials["Partials:<br/>project_details.prompt<br/>files_list.prompt<br/>project_tasks.prompt"]
    end

    subgraph "Context & Token Management"
        StateManager["StateManager.current_state"]
        ProjectState["ProjectState<br/>(files, tasks, epics)"]
        tiktoken["tiktoken.encode()<br/>Token Counter"]
        trim_logs["trim_logs()<br/>Context Pruner"]
    end

    subgraph "LLM Client Layer"
        BaseLLMClient["BaseLLMClient.__call__()"]
        Convo["Convo.messages"]
        OpenAIClient["OpenAIClient._make_request()"]
    end

    Developer --> AgentConvo
    CodeMonkey --> AgentConvo
    TechLead --> AgentConvo
    
    AgentConvo --> TemplateLoader
    TemplateLoader --> breakdown
    TemplateLoader --> implement
    TemplateLoader --> plan
    
    breakdown --> partials
    implement --> partials
    plan --> partials
    
    StateManager --> ProjectState
    ProjectState --> AgentConvo
    
    AgentConvo --> Convo
    Convo --> tiktoken
    tiktoken --> trim_logs
    
    trim_logs --> BaseLLMClient
    BaseLLMClient --> OpenAIClient
```

Sources: [core/agents/convo.py](), [core/agents/base.py:175-223](), [core/llm/base.py:167-181](), [core/utils/text.py:6-42]()

## Jinja2 Template System

GPT Pilot uses Jinja2 for prompt templating, with templates stored in `core/prompts/`. The `AgentConvo` class wraps Jinja2's `Environment` to load and render templates.

**Template Syntax:**

| Feature | Syntax | Example |
|---------|--------|---------|
| Variable interpolation | `{{ var }}` | `{{ state.branch.project.name }}` |
| Conditionals | `{% if %}...{% endif %}` | `{% if state.epics\|length == 1 %}` |
| Loops | `{% for %}...{% endfor %}` | `{% for task in state.tasks %}` |
| Includes | `{% include %}` | `{% include "partials/files_list.prompt" %}` |
| Filters | `{{ var\|filter }}` | `{{ task.description\|trim }}` |

**Template Composition Example** ([core/prompts/developer/breakdown.prompt:1-77]()):

```
You are working on "{{ state.branch.project.name }}"...

{% include "partials/project_details.prompt" %}
{% include "partials/features_list.prompt" %}
{% include "partials/files_list.prompt" %}

{% if state.epics|length == 1 %}
Remember, I created an empty folder...
{% endif %}
```

The template system automatically injects the `state` variable (a `ProjectState` instance) and other context variables when rendering.

**Diagram: Template Rendering Process**

```mermaid
flowchart LR
    Agent["Agent calls<br/>convo.template('breakdown')"]
    
    AgentConvo["AgentConvo.template()"]
    
    Jinja2Env["Jinja2.Environment<br/>(FileSystemLoader)"]
    
    Template["breakdown.prompt<br/>+ included partials"]
    
    Context["Context Dict:<br/>{state: ProjectState,<br/>task: dict,<br/>current_task_index: int}"]
    
    Rendered["Rendered Prompt String"]
    
    ConvoMsg["Convo.user(rendered)"]
    
    Agent --> AgentConvo
    AgentConvo --> Jinja2Env
    Jinja2Env --> Template
    Template --> Context
    Context --> Rendered
    Rendered --> ConvoMsg
```

Sources: [core/agents/convo.py](), [core/prompts/developer/breakdown.prompt:1-77]()

## Prompt Directory Structure

Prompts are organized by agent in `core/prompts/`, with shared components in `partials/`:

```
core/prompts/
├── partials/               # Reusable prompt fragments
│   ├── project_details.prompt
│   ├── features_list.prompt
│   ├── files_list.prompt
│   ├── project_tasks.prompt
│   ├── execution_order.prompt
│   ├── file_naming.prompt
│   ├── relative_paths.prompt
│   ├── human_intervention_explanation.prompt
│   └── user_feedback.prompt
├── architect/
├── bug-hunter/
│   └── iteration.prompt
├── code-monkey/
│   └── implement_changes.prompt
├── developer/
│   ├── breakdown.prompt
│   └── parse_task.prompt
├── tech-lead/
│   ├── plan.prompt
│   └── epic_breakdown.prompt
└── troubleshooter/
    └── iteration.prompt
```

**Agent-to-Prompt Mapping:**

| Agent Class | Prompt File | Key Template Variables |
|-------------|-------------|------------------------|
| `TechLead` | `tech-lead/plan.prompt` | `state`, `task_type`, `epic` |
| `Developer` | `developer/breakdown.prompt` | `state`, `task`, `current_task_index` |
| `CodeMonkey` | `code-monkey/implement_changes.prompt` | `file_name`, `file_content`, `instructions` |
| `BugHunter` | `bug-hunter/iteration.prompt` | `state`, `user_feedback`, `test_instructions` |
| `Troubleshooter` | `troubleshooter/iteration.prompt` | `state`, `user_feedback`, `next_solution_to_try` |

**Diagram: Partial Inclusion Pattern**

```mermaid
graph TB
    subgraph "Reusable Partials"
        project_details["project_details.prompt<br/>(name, description, stack)"]
        features_list["features_list.prompt<br/>(implemented features)"]
        files_list["files_list.prompt<br/>(current files + descriptions)"]
        project_tasks["project_tasks.prompt<br/>(rules for task creation)"]
        doc_snippets["doc_snippets.prompt<br/>(documentation references)"]
        user_feedback["user_feedback.prompt<br/>(iteration feedback)"]
    end

    subgraph "Agent Prompts"
        breakdown["developer/breakdown.prompt"]
        plan["tech-lead/plan.prompt"]
        iteration["bug-hunter/iteration.prompt"]
    end

    project_details --> breakdown
    project_details --> plan
    project_details --> iteration
    
    features_list --> breakdown
    features_list --> plan
    
    files_list --> breakdown
    files_list --> plan
    files_list --> iteration
    
    project_tasks --> plan
    
    doc_snippets --> breakdown
    doc_snippets --> iteration
    
    user_feedback --> iteration
```

Sources: [core/prompts/developer/breakdown.prompt:3-7](), [core/prompts/tech-lead/plan.prompt:4-5](), [core/prompts/bug-hunter/iteration.prompt:3-22]()

## Context Injection

Prompt templates receive context through variables injected by `AgentConvo.template()`. The primary context source is `ProjectState`, which contains:

**ProjectState Context Variables:**

| Variable Path | Type | Description |
|---------------|------|-------------|
| `state.branch.project.name` | str | Project name |
| `state.specification.description` | str | Project specification |
| `state.epics` | list[Epic] | All epics in the project |
| `state.tasks` | list[Task] | All tasks in current epic |
| `state.current_task` | Task | Currently executing task |
| `state.files` | list[File] | All project files |
| `state.iterations` | list[Iteration] | Bug hunting/troubleshooting iterations |

**Context Variables by Prompt:**

- **breakdown.prompt** ([core/prompts/developer/breakdown.prompt:1-77]()):
  - `state`: ProjectState
  - `task`: Current task dictionary
  - `current_task_index`: int
  - `redo_task_user_feedback`: Optional user feedback on failed task
  - `related_api_endpoints`: List of API endpoints for this task

- **implement_changes.prompt**:
  - `file_name`: str (path to file being modified)
  - `file_content`: str (current file content)
  - `instructions`: str (implementation instructions with `<pythagoracode>` tags)
  - `user_feedback`: Optional user feedback
  - `user_feedback_qa`: Optional QA feedback

- **iteration.prompt** ([core/prompts/bug-hunter/iteration.prompt:1-49]()):
  - `state`: ProjectState
  - `user_feedback`: User-reported bug description
  - `test_instructions`: List of test steps
  - `next_solution_to_try`: Suggested solution approach

**Diagram: Context Flow from State to Prompt**

```mermaid
flowchart TD
    StateManager["StateManager.current_state<br/>(read-only)"]
    
    ProjectState["ProjectState Object<br/>- branch.project<br/>- specification<br/>- epics, tasks<br/>- files<br/>- iterations"]
    
    Agent["Agent.get_llm()"]
    
    AgentConvo["convo = AgentConvo(self).template()"]
    
    TemplateVars["Template Variables:<br/>{state: ProjectState,<br/>task: Task,<br/>file_content: str,<br/>...}"]
    
    Jinja2["Jinja2 Render:<br/>{{ state.branch.project.name }}<br/>{% for task in state.tasks %}"]
    
    RenderedPrompt["Rendered Prompt with<br/>- Project info<br/>- File listings<br/>- Task descriptions<br/>- User feedback"]
    
    ConvoMessages["Convo.messages<br/>(list of role/content dicts)"]
    
    StateManager --> ProjectState
    ProjectState --> Agent
    Agent --> AgentConvo
    AgentConvo --> TemplateVars
    TemplateVars --> Jinja2
    Jinja2 --> RenderedPrompt
    RenderedPrompt --> ConvoMessages
```

Sources: [core/agents/base.py:46-54](), [core/prompts/developer/breakdown.prompt:1-77](), [core/prompts/bug-hunter/iteration.prompt:1-49]()

## Token Counting and Context Pruning

GPT Pilot manages token limits through two mechanisms: token counting with `tiktoken` and intelligent context pruning with `trim_logs()`.

**Token Counting Implementation** ([core/llm/base.py:167-186]()):

```python
# In BaseLLMClient.__call__()
prompt_tokens = sum(3 + len(tokenizer.encode(str(msg.get("content", "")))) 
                    for msg in convo.messages)

if prompt_tokens > 150_000:
    # Find messages containing logs
    for i, msg in enumerate(reversed(convo.messages)):
        if "Here are the backend logs" in msg["content"] or \
           "Here are the frontend logs" in msg["content"]:
            index = len(convo.messages) - 1 - i
            break
    
    if index != -1:
        # Trim log messages
        for i, msg in enumerate(convo.messages):
            if i < index:
                convo.messages[i]["content"] = trim_logs(convo.messages[i]["content"])
```

**Token Counting Table:**

| Component | Implementation | Location |
|-----------|----------------|----------|
| Tokenizer | `tiktoken.get_encoding("cl100k_base")` | [core/llm/base.py:22]() |
| Token counting | `tokenizer.encode(msg["content"])` | [core/llm/base.py:167]() |
| Threshold | 150,000 tokens | [core/llm/base.py:170]() |
| Context pruner | `trim_logs(content)` | [core/utils/text.py:6-42]() |

**Context Pruning Function** ([core/utils/text.py:6-42]()):

The `trim_logs()` function removes log content from prompts to stay under token limits:

```python
def trim_logs(logs: str) -> str:
    markers = ["Here are the backend logs", "Here are the frontend logs"]
    
    # Find first occurrence of any marker
    index = float("inf")
    for marker in markers:
        pos = logs.find(marker)
        if pos != -1 and pos < index:
            index = pos
    
    # Trim at marker if found
    if index != float("inf"):
        return logs[:index]
    
    return logs
```

This ensures that verbose log outputs don't consume the entire context window, allowing more room for code and task descriptions.

**Diagram: Token Management Flow**

```mermaid
flowchart TD
    ConvoMessages["Convo.messages<br/>(list of dicts)"]
    
    CountTokens["tiktoken.encode()<br/>Count tokens per message"]
    
    CheckLimit{"prompt_tokens<br/>> 150,000?"}
    
    FindLogMessages["Search for<br/>'Here are the backend logs'<br/>'Here are the frontend logs'"]
    
    TrimLogs["trim_logs()<br/>Remove logs from messages"]
    
    MakeRequest["BaseLLMClient._make_request()"]
    
    ConvoMessages --> CountTokens
    CountTokens --> CheckLimit
    
    CheckLimit -->|No| MakeRequest
    CheckLimit -->|Yes| FindLogMessages
    
    FindLogMessages --> TrimLogs
    TrimLogs --> MakeRequest
```

Sources: [core/llm/base.py:167-186](), [core/utils/text.py:6-42](), [core/llm/openai_client.py:78-85]()

## Prompt Invocation Flow

Agents invoke prompts through the `AgentConvo` class, which wraps Jinja2 template rendering. The typical flow:

1. **Agent creates conversation**: `convo = AgentConvo(self).template(template_name, **kwargs)`
2. **Template renders**: Jinja2 processes template with provided context variables
3. **Message added to convo**: Rendered prompt becomes a user message in `Convo.messages`
4. **LLM called**: Agent passes `convo` to `llm(convo, parser=...)`
5. **Response logged**: `StateManager.log_llm_request()` stores request/response

**Code Example** ([core/agents/code_monkey.py:136-152]()):

```python
# In CodeMonkey.implement_changes()
llm = self.get_llm(CODE_MONKEY_AGENT_NAME)
convo = AgentConvo(self).template(
    "implement_changes",
    file_name=file_name,
    file_content=file_content,
    instructions=instructions,
    user_feedback=user_feedback,
    user_feedback_qa=user_feedback_qa,
)
if feedback:
    convo.assistant(f"```\n{data['new_content']}\n```\n").template(
        "review_feedback",
        content=data["approved_content"],
        original_content=file_content,
        rework_feedback=feedback,
    )
response = await llm(convo, temperature=0, parser=OptionalCodeBlockParser())
```

**Diagram: Prompt to LLM Request Pipeline**

```mermaid
sequenceDiagram
    participant Agent as "CodeMonkey"
    participant AgentConvo as "AgentConvo"
    participant Jinja2 as "Jinja2 Loader"
    participant Convo as "Convo.messages"
    participant LLM as "BaseLLMClient"
    participant StateManager as "StateManager"
    
    Agent->>AgentConvo: template("implement_changes",<br/>file_name=..., file_content=...)
    AgentConvo->>Jinja2: Load implement_changes.prompt
    Jinja2->>Jinja2: Render with context variables
    Jinja2-->>AgentConvo: Rendered prompt string
    AgentConvo->>Convo: user(rendered_prompt)
    Convo-->>Agent: convo object
    
    Agent->>Agent: llm = self.get_llm(CODE_MONKEY_AGENT_NAME)
    Agent->>LLM: await llm(convo, parser=...)
    LLM->>LLM: tiktoken count tokens
    LLM->>LLM: trim_logs if > 150k tokens
    LLM->>LLM: _make_request()
    LLM-->>Agent: (response, request_log)
    
    Agent->>StateManager: log_llm_request(request_log)
```

Sources: [core/agents/code_monkey.py:136-152](), [core/agents/base.py:175-223](), [core/agents/convo.py]()

## Task Processing Flow

The prompt system facilitates the task processing workflow:

```mermaid
flowchart TD
    TaskStart["Task Start"] --> FilterFiles["Filter Relevant Files"]
    FilterFiles --> TaskBreakdown["Task Breakdown"]
    TaskBreakdown --> ParseTasks["Parse Task Steps"]
    ParseTasks --> ImplementChanges["Implement Changes"]
    
    subgraph "Prompt Templates"
        FilterFilesPrompt["filter_files.prompt"]
        BreakdownPrompt["breakdown.prompt"]
        ParseTaskPrompt["parse_task.prompt"]
        ImplementChangesPrompt["implement_changes.prompt"]
    end
    
    FilterFiles --- FilterFilesPrompt
    TaskBreakdown --- BreakdownPrompt
    ParseTasks --- ParseTaskPrompt
    ImplementChanges --- ImplementChangesPrompt
```

Sources: [core/prompts/developer/filter_files.prompt](), [core/prompts/developer/breakdown.prompt](), [core/prompts/developer/parse_task.prompt](), [core/prompts/code-monkey/implement_changes.prompt]()

## Human Interaction Prompts

The prompt system includes specialized sections for handling human feedback and intervention:

1. `human_intervention` steps in [core/prompts/developer/parse_task.prompt]()
2. User feedback processing in [core/prompts/partials/user_feedback.prompt]()

These components ensure GPT Pilot can smoothly incorporate human input during the development process.

Sources: [core/prompts/developer/parse_task.prompt:13-16](), [core/prompts/partials/user_feedback.prompt]()

## Related Systems

- For details on how LLM responses are structured, see [Code Generation and Review](#6.2)
- For information on the agent system that uses these prompts, see [Agent System](#2.1)
- For details on state management that provides context to prompts, see [State Management](#2.2)

---

# Page: Development Workflow

# Development Workflow

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [core/agents/architect.py](core/agents/architect.py)
- [core/agents/bug_hunter.py](core/agents/bug_hunter.py)
- [core/agents/developer.py](core/agents/developer.py)
- [core/agents/frontend.py](core/agents/frontend.py)
- [core/agents/mixins.py](core/agents/mixins.py)
- [core/agents/orchestrator.py](core/agents/orchestrator.py)
- [core/agents/spec_writer.py](core/agents/spec_writer.py)
- [core/agents/tech_lead.py](core/agents/tech_lead.py)
- [core/agents/troubleshooter.py](core/agents/troubleshooter.py)

</details>



This page documents the complete development lifecycle in GPT Pilot, from initial specification to deployment. It covers:

- Project lifecycle stages and state transitions
- Code generation using the `<pythagoracode>` tag system
- Context filtering for large codebases
- User testing and feedback loops
- Iteration and debugging workflows

For specific workflow stages, see:
- **[6.1 Project Lifecycle and Stages](#6.1)**: Initialization, epic/task hierarchy, and workflow progression
- **[6.2 Code Generation and File Management](#6.2)**: `<pythagoracode>` tag system and file operations
- **[6.3 Context Filtering and Relevance](#6.3)**: How GPT Pilot filters large codebases
- **[6.4 User Testing and Feedback Loop](#6.4)**: Testing, iteration, and bug hunting

For details on the agent architecture, see [Agent System](#4). For the state management system, see [State Management System](#3.2).

## Agent Orchestration Flow

The `Orchestrator` class ([core/agents/orchestrator.py:36-167]()) coordinates all agents through the `create_agent()` method, which selects the appropriate agent based on `ProjectState`:

### Orchestrator Agent Selection Flow

```mermaid
flowchart TD
    Start([Orchestrator.run]) --> CheckPrevResponse{prev_response type?}
    
    CheckPrevResponse -->|ERROR/CANCEL| ErrorHandler[ErrorHandler]
    CheckPrevResponse -->|DESCRIBE_FILES| CodeMonkey1[CodeMonkey]
    CheckPrevResponse -->|INPUT_REQUIRED| HumanInput1[HumanInput]
    CheckPrevResponse -->|EXTERNAL_DOCS| ExternalDocs[ExternalDocumentation]
    CheckPrevResponse -->|UPDATE_SPEC| SpecWriter1[SpecWriter]
    
    CheckPrevResponse -->|None| CheckEpics{state.epics empty?}
    CheckEpics -->|Yes| Wizard[Wizard]
    CheckEpics -->|No| CheckSpec{epics[0].description?}
    
    CheckSpec -->|No| SpecWriter2[SpecWriter]
    CheckSpec -->|Yes| CheckFrontend{current_epic.source == 'frontend'?}
    
    CheckFrontend -->|Yes| Frontend[Frontend]
    CheckFrontend -->|No| CheckArch{specification.architecture?}
    
    CheckArch -->|No| Architect[Architect]
    CheckArch -->|Yes| CheckTasks{unfinished_tasks or !files?}
    
    CheckTasks -->|Yes| TechLead[TechLead]
    CheckTasks -->|No| CheckTaskStatus{current_task.status?}
    
    CheckTaskStatus -->|REVIEWED| TechnicalWriter[TechnicalWriter]
    CheckTaskStatus -->|DOCUMENTED/SKIPPED| TaskCompleter[TaskCompleter]
    CheckTaskStatus -->|None| CheckSteps{steps empty?}
    
    CheckSteps -->|Yes| Developer[Developer]
    CheckSteps -->|No| CheckCurrentStep{current_step?}
    
    CheckCurrentStep -->|Yes| ExecuteStep[create_agent_for_step]
    CheckCurrentStep -->|No| CheckIterations{unfinished_iterations?}
    
    CheckIterations -->|HUNTING_FOR_BUG| BugHunter1[BugHunter]
    CheckIterations -->|START_PAIR_PROGRAMMING| BugHunter2[BugHunter]
    CheckIterations -->|AWAITING_LOGGING| Developer2[Developer]
    CheckIterations -->|AWAITING_BUG_FIX| Developer3[Developer]
    CheckIterations -->|FIND_SOLUTION| Troubleshooter1[Troubleshooter]
    CheckIterations -->|NEW_FEATURE_REQUESTED| SpecWriter3[SpecWriter]
    
    CheckIterations -->|No| Troubleshooter2[Troubleshooter]
```

**Key Decision Points:**

| State Condition | Agent Selected | Code Reference |
|----------------|----------------|----------------|
| `not state.epics` | `Wizard` | [core/agents/orchestrator.py:481-482]() |
| `not epics[0].get("description")` | `SpecWriter` | [core/agents/orchestrator.py:483-485]() |
| `current_epic.source == "frontend"` | `Frontend` | [core/agents/orchestrator.py:486-488]() |
| `not specification.architecture` | `Architect` | [core/agents/orchestrator.py:489-491]() |
| `not unfinished_tasks` | `TechLead` | [core/agents/orchestrator.py:492-494]() |
| `not steps and not iterations` | `Developer` | [core/agents/orchestrator.py:509-511]() |
| `current_step` | Step-specific agent | [core/agents/orchestrator.py:513-516]() |
| `unfinished_iterations` | Status-dependent | [core/agents/orchestrator.py:518-549]() |
| Task complete | `Troubleshooter` | [core/agents/orchestrator.py:552]() |

Sources: [core/agents/orchestrator.py:36-599](), [core/agents/orchestrator.py:463-573]()

## Project Hierarchy and State Structure

GPT Pilot organizes projects using a hierarchical structure stored in `ProjectState`:

### Hierarchy Structure

```mermaid
flowchart TD
    Project["Project\nDB: projects table"] --> Branch["Branch\nDB: branches table\ndefault: 'main'"]
    Branch --> State["ProjectState\nDB: project_states table\nstep_index increments"]
    
    State --> Spec["Specification\nspecification JSON field"]
    State --> KB["KnowledgeBase\nknowledge_base JSON field\napis, pages, utils"]
    State --> Epics["epics: list[dict]\nid, name, source, description,\ncompleted, sub_epics"]
    State --> Tasks["tasks: list[dict]\nid, description, status,\nsub_epic_id, instructions"]
    State --> Steps["steps: list[dict]\nid, type, completed,\nsource, iteration_index"]
    State --> Iterations["iterations: list[dict]\nid, user_feedback, status,\nbug_hunting_cycles"]
    State --> Files["files: list[File]\npath, content (FileContent)"]
```

### Epic Structure

Epics are created by `TechLead.plan_epic()` ([core/agents/tech_lead.py:296-368]()) and stored in `ProjectState.epics`:

```python
epic = {
    "id": uuid4().hex,
    "name": "Feature #N",
    "source": "app" | "feature" | "frontend",
    "description": "Epic description",
    "test_instructions": None,
    "summary": None,
    "completed": False,
    "complexity": Complexity.SIMPLE | Complexity.MODERATE | Complexity.HARD,
    "sub_epics": [
        {
            "id": 1,
            "description": "Sub-epic description"
        }
    ]
}
```

The initial project always has two epics:
1. **Epic 1**: "Build frontend" (source: "frontend") - created by `SpecWriter` ([core/agents/spec_writer.py:287-297]())
2. **Epic 2**: Project implementation (source: "app") - created by `TechLead.create_initial_project_epic()` ([core/agents/tech_lead.py:92-110]())

Sources: [core/agents/tech_lead.py:92-110](), [core/agents/tech_lead.py:296-368](), [core/agents/spec_writer.py:287-297]()

### Task Structure

Tasks are created by `TechLead.process_epic()` ([core/agents/tech_lead.py:262-294]()) and stored in `ProjectState.tasks`:

```python
task = {
    "id": uuid4().hex,
    "description": "Task description",
    "instructions": None,  # Set by Developer.breakdown_current_task()
    "pre_breakdown_testing_instructions": "Testing instructions",
    "test_instructions": None,  # Set by Troubleshooter
    "status": TaskStatus.TODO | IN_PROGRESS | DONE | REVIEWED | DOCUMENTED | SKIPPED,
    "sub_epic_id": 1,
    "related_api_endpoints": [
        {
            "description": "Endpoint description",
            "method": "POST",
            "endpoint": "/api/users",
            "request_body": {"field": "type"},
            "response_body": {"field": "type"}
        }
    ]
}
```

**Task Status Progression:**

`TODO` → `IN_PROGRESS` (Developer sets) → `REVIEWED` (Troubleshooter sets) → `DOCUMENTED` (TechnicalWriter sets) → Task complete

Sources: [core/agents/tech_lead.py:262-294](), [core/agents/developer.py:301](), [core/agents/troubleshooter.py:158]()

### Step Structure

Steps are created by `Developer.set_next_steps()` ([core/agents/developer.py:313-329]()) from `TaskSteps` schema:

```python
step = {
    "id": uuid4().hex,
    "completed": False,
    "source": "app" | "troubleshooting" | "bug_hunt",
    "iteration_index": 0,
    "type": "save_file" | "command" | "human_intervention" | "utility_function",
    
    # For type == "save_file"
    "save_file": {
        "path": "path/to/file.js"
    },
    
    # For type == "command"
    "command": {
        "command": "npm install express",
        "timeout": 60,
        "success_message": ""
    },
    
    # For type == "human_intervention"
    "human_intervention_description": "Description of action needed",
    
    # For type == "utility_function"
    "file": "path/to/file.js",
    "function_name": "calculateTotal",
    "description": "Calculates order total",
    "return_value": "number",
    "input_value": "Order object",
    "status": "mocked" | "implemented"
}
```

Steps are executed by:
- `save_file`: `CodeMonkey` (parallel execution) - [core/agents/orchestrator.py:554-561]()
- `command`: `Executor` - [core/agents/orchestrator.py:563]()
- `human_intervention`: `HumanInput` - [core/agents/orchestrator.py:565]()
- `utility_function`: `Developer.update_knowledge_base()` - [core/agents/developer.py:478-484]()

Sources: [core/agents/developer.py:32-82](), [core/agents/developer.py:313-329](), [core/agents/orchestrator.py:554-573]()

### Iteration Structure

Iterations are created by `Troubleshooter.create_iteration()` ([core/agents/troubleshooter.py:127-146]()) for bug fixes or changes:

```python
iteration = {
    "id": uuid4().hex,
    "user_feedback": "User-reported issue or change request",
    "user_feedback_qa": ["Additional Q&A"],
    "description": "Solution description",
    "alternative_solutions": [],
    "attempts": 1,
    "status": IterationStatus.HUNTING_FOR_BUG | AWAITING_USER_TEST | 
              AWAITING_BUG_FIX | FIND_SOLUTION | NEW_FEATURE_REQUESTED,
    "bug_hunting_cycles": [
        {
            "human_readable_instructions": "Debugging steps",
            "backend_logs": "...",
            "frontend_logs": "...",
            "fix_attempted": True,
            "user_feedback": "User response"
        }
    ]
}
```

**Iteration Status Flow:**

`FIND_SOLUTION` → `IMPLEMENT_SOLUTION` (or `NEW_FEATURE_REQUESTED` for spec changes)

`HUNTING_FOR_BUG` → `AWAITING_BUG_FIX` or `AWAITING_LOGGING` → `AWAITING_USER_TEST` → Complete or restart cycle

Sources: [core/agents/troubleshooter.py:127-146](), [core/db/models/project_state.py:22-31]()

## Code Generation Workflow

Code generation in GPT Pilot uses a structured tag system and multiple agent coordination:

### Developer Breakdown Process

`Developer.breakdown_current_task()` ([core/agents/developer.py:204-311]()) creates implementation instructions:

```mermaid
sequenceDiagram
    participant Orch as "Orchestrator"
    participant Dev as "Developer"
    participant LLM as "LLM (breakdown prompt)"
    participant Parser as "JSONParser(TaskSteps)"
    
    Orch->>Dev: breakdown_current_task()
    Dev->>Dev: get_relevant_files_parallel()
    Dev->>LLM: breakdown.prompt template
    LLM->>Dev: Return implementation instructions
    Note over Dev: Instructions use <pythagoracode> tags
    
    Dev->>Dev: chat_with_breakdown(convo, response)
    Note over Dev: User can provide feedback on breakdown
    
    Dev->>Parser: parse_task.prompt template
    Parser->>Dev: TaskSteps (structured steps)
    Dev->>Dev: set_next_steps(response)
    Note over Dev: Converts to executable steps
    Dev->>Orch: AgentResponse.done()
```

The LLM response uses `<pythagoracode>` tags to specify code changes:

```
<pythagoracode file="server/routes/users.js">
const express = require('express');
const router = express.Router();
// ... complete file content
</pythagoracode>
```

Sources: [core/agents/developer.py:204-311](), [core/agents/developer.py:251-263]()

### CodeMonkey Implementation Process

`CodeMonkey` implements `save_file` steps in parallel ([core/agents/orchestrator.py:554-561]()):

```mermaid
sequenceDiagram
    participant Orch as "Orchestrator"
    participant CM1 as "CodeMonkey #1"
    participant CM2 as "CodeMonkey #2"
    participant CMN as "CodeMonkey #N"
    participant LLM as "LLM Client"
    participant SM as "StateManager"
    
    Orch->>Orch: create_agent_for_step('save_file')
    Note over Orch: Returns list of CodeMonkey agents
    
    par Parallel Execution
        Orch->>CM1: run() for step 1
        Orch->>CM2: run() for step 2
        Orch->>CMN: run() for step N
    end
    
    CM1->>SM: get_file_content_by_path()
    CM1->>LLM: implement_changes.prompt
    LLM->>CM1: New file content
    CM1->>SM: save_file(path, content)
    CM1->>Orch: AgentResponse.done()
    
    Note over Orch: Waits for all agents with asyncio.gather()
```

The `CodeMonkey.run()` method ([core/agents/code_monkey.py:46-180]()) flow:

1. **Get current file content**: `self.current_state.get_file_content_by_path(file_path)` ([core/agents/code_monkey.py:65]())
2. **Get referencing files**: `self.state_manager.get_referencing_files()` ([core/agents/code_monkey.py:68-69]())
3. **Generate new content**: LLM call with `implement_changes` prompt ([core/agents/code_monkey.py:72-117]())
4. **Calculate diff**: `self.get_line_changes(old_content, new_content)` ([core/agents/code_monkey.py:133]())
5. **Save file**: `await self.state_manager.save_file(file_path, new_content)` ([core/agents/code_monkey.py:148]())

Sources: [core/agents/code_monkey.py:46-180](), [core/agents/orchestrator.py:554-561]()

### Frontend Code Generation

`Frontend` agent has a specialized workflow for UI development ([core/agents/frontend.py:44-603]()):

**Frontend Implementation Methods:**

| Method | Purpose | Code Reference |
|--------|---------|----------------|
| `start_frontend()` | Initial UI build | [core/agents/frontend.py:61-110]() |
| `continue_frontend()` | Continue incomplete build | [core/agents/frontend.py:112-149]() |
| `iterate_frontend()` | Handle user feedback | [core/agents/frontend.py:151-318]() |
| `process_response()` | Parse and execute LLM response | [core/agents/frontend.py:356-449]() |
| `remove_mock()` | Replace mock APIs with real ones | [core/agents/frontend.py:451-517]() |

`Frontend.process_response()` parses code blocks with special handling:

```python
for block in response_blocks:
    description = block.description.strip()
    content = block.content.strip()
    
    # Extract file path from last line
    if "file:" in last_line:
        file_path = last_line.split("file:")[1].strip()
        # Save file with relace or direct save
    
    elif "command:" in last_line:
        # Execute commands (filtered to prevent starting dev server)
        commands = content.strip().split("\n")
        for command in commands:
            if "run start" not in command and "run dev" not in command:
                await self.process_manager.run_command(command)
```

Sources: [core/agents/frontend.py:44-603](), [core/agents/frontend.py:356-449]()

## Testing and Iteration Workflow

### Troubleshooter Test Generation

After task completion, `Troubleshooter.create_iteration()` ([core/agents/troubleshooter.py:63-146]()) generates test instructions:

```mermaid
sequenceDiagram
    participant Orch as "Orchestrator"
    participant TS as "Troubleshooter"
    participant LLM as "LLM"
    participant User as "User"
    
    Orch->>TS: create_iteration()
    TS->>TS: get_run_command()
    Note over TS: Determines how to start the app
    
    TS->>LLM: define_user_review_goal template
    LLM->>TS: TestSteps (JSON schema)
    TS->>TS: Save to task['test_instructions']
    
    TS->>User: Display test instructions
    Note over User: User tests the application
    
    TS->>User: get_user_feedback()
    User->>TS: "continue" | "bug" | "change" | "redo"
    
    alt User reports bug
        TS->>TS: Create iteration (HUNTING_FOR_BUG)
    else User requests change
        TS->>TS: Create iteration (NEW_FEATURE_REQUESTED)
    else Everything works
        TS->>TS: complete_task()
    end
    
    TS->>Orch: AgentResponse.done()
```

Test instructions are generated by `Troubleshooter.get_user_instructions()` ([core/agents/troubleshooter.py:203-231]()):

```python
convo = self._get_task_convo().template(
    "define_user_review_goal",
    task=current_task,
    route_files=route_files,
    current_task_index=self.current_state.tasks.index(current_task),
).require_schema(TestSteps)

user_instructions: TestSteps = await llm(convo, parser=JSONParser(TestSteps))
```

The `TestSteps` schema ([core/agents/mixins.py:27-34]()):

```python
class Test(BaseModel):
    title: str = Field(description="Very short title of the test.")
    action: str = Field(description="Detailed description of actions to test.")
    result: str = Field(description="Expected result that verifies success.")

class TestSteps(BaseModel):
    steps: List[Test]
```

Sources: [core/agents/troubleshooter.py:63-146](), [core/agents/troubleshooter.py:203-231](), [core/agents/mixins.py:27-34]()

### Bug Hunting Workflow

When a user reports a bug, `BugHunter` follows a multi-cycle debugging process:

```mermaid
stateDiagram-v2
    [*] --> HUNTING_FOR_BUG: User reports bug
    
    HUNTING_FOR_BUG --> check_logs: BugHunter.check_logs()
    check_logs --> hunt_conclusion: Analyze logs
    
    hunt_conclusion --> AWAITING_LOGGING: ADD_LOGS needed
    hunt_conclusion --> AWAITING_BUG_FIX: PROBLEM_IDENTIFIED
    
    AWAITING_LOGGING --> Developer: Generate logging steps
    Developer --> AWAITING_BUG_REPRODUCTION: Steps implemented
    
    AWAITING_BUG_FIX --> Developer: Generate fix steps
    Developer --> AWAITING_USER_TEST: Steps implemented
    
    AWAITING_BUG_REPRODUCTION --> ask_user_to_test: BugHunter
    AWAITING_USER_TEST --> ask_user_to_test: BugHunter
    
    ask_user_to_test --> user_response: User tests
    user_response --> [*]: Bug fixed
    user_response --> HUNTING_FOR_BUG: Still broken
    user_response --> START_PAIR_PROGRAMMING: Complex issue
    
    START_PAIR_PROGRAMMING --> start_pair_programming: BugHunter
    start_pair_programming --> [*]: User fixes manually
```

**Bug Hunting Methods:**

| Method | Purpose | Status Transition |
|--------|---------|-------------------|
| `check_logs()` | Analyzes logs for root cause | `HUNTING_FOR_BUG` → `AWAITING_BUG_FIX` or `AWAITING_LOGGING` |
| `ask_user_to_test()` | Requests user testing | `AWAITING_USER_TEST`/`AWAITING_BUG_REPRODUCTION` → Complete or retry |
| `start_pair_programming()` | Interactive debugging with user | `START_PAIR_PROGRAMMING` → Complete |

`BugHunter.check_logs()` flow ([core/agents/bug_hunter.py:103-142]()):

1. **Generate instructions**: LLM analyzes iteration context and generates debugging steps
2. **Chat with breakdown**: User can refine the debugging approach
3. **Determine conclusion**: LLM decides if more logs are needed or problem is identified
4. **Create hunting cycle**: Adds cycle to `iteration["bug_hunting_cycles"]`

```python
convo = self.generate_iteration_convo_so_far()
human_readable_instructions = await llm(convo, temperature=0.5)

convo = AgentConvo(self).template(
    "bug_found_or_add_logs",
    hunt_conclusion=human_readable_instructions,
).require_schema(HuntConclusionOptions)

hunt_conclusion = await llm(convo, parser=JSONParser(HuntConclusionOptions))
```

Sources: [core/agents/bug_hunter.py:61-412](), [core/agents/bug_hunter.py:103-142](), [core/agents/bug_hunter.py:363-391]()

### Pair Programming Mode

For complex bugs, `BugHunter.start_pair_programming()` ([core/agents/bug_hunter.py:241-361]()) enables interactive debugging:

```mermaid
sequenceDiagram
    participant User
    participant BH as "BugHunter"
    participant LLM as "LLM"
    
    User->>BH: Start pair programming
    BH->>LLM: problem_explanation template
    LLM->>BH: Initial explanation
    
    BH->>LLM: data_about_logs template
    LLM->>BH: ImportantLogsForDebugging
    BH->>User: Display logs with context
    
    loop Interactive Session
        BH->>User: What do you want to do?
        User->>BH: "question" | "tell_me_more" | "solution_hint" | "done"
        
        alt User has question
            User->>BH: Ask question
            BH->>LLM: ask_a_question template
            LLM->>BH: Answer
            BH->>User: Display answer
        else User provides solution hint
            User->>BH: Describe solution
            BH->>LLM: instructions_from_human_hint
            LLM->>BH: Implementation instructions
            BH->>User: Can I implement this?
            User->>BH: Approve or reject
        else User says done
            BH->>BH: complete_iteration()
        end
    end
```

The `ImportantLogsForDebugging` schema ([core/agents/bug_hunter.py:42-54]()) structures log analysis:

```python
class ImportantLog(BaseModel):
    logCode: str = Field(description="Actual line of code that prints the log.")
    shouldBeDifferent: bool = Field(description="Whether output should differ.")
    filePath: str = Field(description="Path to file with the log.")
    currentOutput: str = Field(description="Current output of the log.")
    expectedOutput: str = Field(description="Expected output of the log.")
    explanation: str = Field(description="Brief explanation of the log.")
```

Sources: [core/agents/bug_hunter.py:241-361](), [core/agents/bug_hunter.py:42-54]()

## Context Management and File Filtering

GPT Pilot uses sophisticated context filtering to handle large codebases within LLM token limits.

### Relevant Files Selection

`RelevantFilesMixin.get_relevant_files_parallel()` ([core/agents/mixins.py:130-151]()) filters files in parallel:

```mermaid
graph TB
    Start[get_relevant_files_parallel] --> Split[Split by directory type]
    
    Split --> Client[get_relevant_files<br/>dir_type='client']
    Split --> Server[get_relevant_files<br/>dir_type='server']
    
    Client --> ClientLLM[LLM: filter_files prompt<br/>Frontend files only]
    Server --> ServerLLM[LLM: filter_files prompt<br/>Backend files only]
    
    ClientLLM --> ClientFiles[Client relevant files list]
    ServerLLM --> ServerFiles[Server relevant files list]
    
    ClientFiles --> Combine[Combine + filter existing]
    ServerFiles --> Combine
    
    Combine --> AddAlways[Add ALWAYS_RELEVANT_FILES]
    AddAlways --> UpdateState[Update current_state.relevant_files<br/>Update next_state.relevant_files]
```

**File Filtering Process:**

1. **Split by directory**: Separate frontend (`client/`) and backend (`server/`) files
2. **LLM filtering**: Each LLM call analyzes ~50% of files
3. **Combine results**: Merge both lists
4. **Add mandatory files**: Include files from `ALWAYS_RELEVANT_FILES` ([core/config/magic_words.py]())
5. **Verify existence**: Filter out non-existent files

The `filter_files` prompt ([core/prompts/developer/filter_files.prompt]()) receives:
- Current task description
- User feedback (if any)
- Solution description (if any)
- List of all project files with their descriptions
- Directory type filter

```python
convo = AgentConvo(self).template(
    "filter_files",
    user_feedback=user_feedback,
    solution_description=solution_description,
    relevant_files=relevant_files,
    dir_type=dir_type,
).require_schema(RelevantFiles)

llm_response: RelevantFiles = await llm(
    convo, 
    parser=JSONParser(RelevantFiles), 
    temperature=0
)
```

Sources: [core/agents/mixins.py:122-189](), [core/agents/mixins.py:130-151]()

### File Description and Metadata

Files lacking descriptions are analyzed by `CodeMonkey.describe_file()`:

When `Orchestrator.handle_done()` ([core/agents/orchestrator.py:418-461]()) detects missing descriptions:

```python
missing_descriptions = [
    file.path for file in self.current_state.files 
    if not file.content.meta.get("description")
]
if missing_descriptions:
    return AgentResponse.describe_files(self)
```

This triggers `CodeMonkey` in description mode, which generates file metadata without modifying content.

Sources: [core/agents/orchestrator.py:454-459](), [core/agents/code_monkey.py:182-230]()

## Development Workflow Example

Here's a concrete example of how a task flows through the system:

1. **Tech Lead breaks down epic**: Auth feature is split into "Implement user registration" and "Implement user login" tasks
2. **Developer analyzes task**: Describes what API endpoints, database models, and frontend changes are needed
3. **Developer breaks down implementation**: Tasks are converted to steps (save files, run commands)
4. **Code Monkey implements**: Writes or updates each file with required code
5. **Reviewer verifies**: Checks implementation, suggests improvements if needed
6. **Troubleshooter creates tests**: Generates instructions for the user to test the feature
7. **User provides feedback**: Reports issues or confirms functionality
8. **Bug Hunter addresses issues**: Analyzes and fixes any bugs found

This process repeats for each task in the project until completion.

Sources: [README.md:177-190]()

## Summary

GPT Pilot's development workflow is designed to create fully functioning applications with minimal human intervention. By breaking down projects into manageable units and following a strict development process, it can handle complex applications while maintaining code quality and addressing user requirements effectively.

The key to this workflow is the collaboration between specialized agents, each handling different aspects of the development process, and the structured approach to breaking down work into epics, tasks, and actionable steps.

---

# Page: Project Lifecycle and Stages

# Project Lifecycle and Stages

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [core/agents/architect.py](core/agents/architect.py)
- [core/agents/frontend.py](core/agents/frontend.py)
- [core/agents/orchestrator.py](core/agents/orchestrator.py)
- [core/agents/spec_writer.py](core/agents/spec_writer.py)
- [core/cli/helpers.py](core/cli/helpers.py)
- [core/cli/main.py](core/cli/main.py)
- [core/db/models/project.py](core/db/models/project.py)
- [core/db/models/project_state.py](core/db/models/project_state.py)
- [core/db/v0importer.py](core/db/v0importer.py)
- [core/prompts/developer/parse_task.prompt](core/prompts/developer/parse_task.prompt)
- [core/prompts/partials/project_tasks.prompt](core/prompts/partials/project_tasks.prompt)
- [core/prompts/tech-lead/epic_breakdown.prompt](core/prompts/tech-lead/epic_breakdown.prompt)
- [core/prompts/tech-lead/plan.prompt](core/prompts/tech-lead/plan.prompt)
- [core/state/state_manager.py](core/state/state_manager.py)
- [core/ui/api_server.py](core/ui/api_server.py)
- [tests/cli/test_cli.py](tests/cli/test_cli.py)
- [tests/db/test_project.py](tests/db/test_project.py)

</details>



## Purpose and Scope

This document explains the complete project lifecycle in GPT Pilot, from initialization through completion. It covers the sequential stages a project progresses through, the agents responsible for each stage, and how state transitions are tracked in the database. For information about individual agent implementations, see [Agent System](#4). For details on state persistence mechanisms, see [State Management System](#3.2).

---

## Project Hierarchy and State Structure

Before diving into lifecycle stages, it's important to understand how GPT Pilot structures project progression:

### Database Hierarchy

```mermaid
graph TB
    Project["Project<br/>(UUID id, name, folder_name)"]
    Branch["Branch<br/>(name='main')"]
    State1["ProjectState<br/>(step_index=1)<br/>Initial State"]
    State2["ProjectState<br/>(step_index=2)<br/>Spec Complete"]
    StateN["ProjectState<br/>(step_index=N)<br/>Current State"]
    
    Project -->|"has branches"| Branch
    Branch -->|"has sequential states"| State1
    State1 -->|"prev_state_id"| State2
    State2 -->|"prev_state_id"| StateN
    
    StateN -->|contains| Epics["epics: list[dict]"]
    StateN -->|contains| Tasks["tasks: list[dict]"]
    StateN -->|contains| Steps["steps: list[dict]"]
    StateN -->|contains| Iterations["iterations: list[dict]"]
    StateN -->|references| Spec["Specification"]
    StateN -->|references| KB["KnowledgeBase"]
    StateN -->|has many| Files["files: list[File]"]
```

**Sources:** [core/db/models/project_state.py:59-110](), [core/db/models/project.py:18-34]()

Each `ProjectState` represents an immutable snapshot of the project at a specific point. The `step_index` increments with each committed state, creating an audit trail.

**Key State Fields:**
- `epics`: High-level features/phases (e.g., "Build frontend", "Implement authentication")
- `tasks`: Concrete implementation units within epics
- `steps`: Individual development actions (save file, run command, human intervention)
- `iterations`: Bug hunting and troubleshooting cycles
- `action`: String describing what happened in this state (e.g., "SPEC_CREATE", "TASK_COMPLETE")

---

## Lifecycle Overview

The complete project lifecycle follows this progression:

```mermaid
stateDiagram-v2
    [*] --> Initialization
    
    Initialization --> SpecificationPhase: create_project()
    
    SpecificationPhase --> ArchitecturePhase: specification.description set
    note right of SpecificationPhase
        Action: SPEC_CREATE_STEP_NAME
        Agent: SpecWriter
        Output: specification.description
    end note
    
    ArchitecturePhase --> FrontendEpic: templates applied
    note right of ArchitecturePhase
        Action: ARCHITECTURE_STEP_NAME
        Agent: Architect
        Output: system_dependencies, package_dependencies
    end note
    
    FrontendEpic --> BackendEpics: FE_ITERATION_DONE
    note right of FrontendEpic
        Action: FE_START → FE_ITERATION_DONE
        Agent: Frontend
        Output: UI files in client/
    end note
    
    BackendEpics --> TaskExecution: epics[].sub_epics created
    note right of BackendEpics
        Agent: TechLead
        Output: epics with sub_epics
    end note
    
    TaskExecution --> TaskImplementation: tasks breakdown complete
    note right of TaskExecution
        Action: DEV_TASK_BREAKDOWN
        Agent: Developer
        Output: tasks[] with steps[]
    end note
    
    TaskImplementation --> QualityAssurance: steps completed
    note right of TaskImplementation
        Action: CM_UPDATE_FILES
        Agent: CodeMonkey
        Output: File modifications
    end note
    
    QualityAssurance --> TaskImplementation: bugs found
    QualityAssurance --> TaskComplete: tests pass
    note right of QualityAssurance
        Action: BH_START_BUG_HUNT
        Agents: Troubleshooter → BugHunter
        Output: iterations[]
    end note
    
    TaskComplete --> TaskExecution: more tasks
    TaskComplete --> EpicComplete: all tasks done
    
    EpicComplete --> BackendEpics: more epics
    EpicComplete --> [*]: all epics complete
```

**Sources:** [core/cli/main.py:194-321](), [core/agents/orchestrator.py:48-167]()

---

## Stage 1: Project Initialization

### Entry Points

Projects can be initialized in two ways:

1. **New Project Creation** - User provides initial description
2. **Existing Project Load** - Loads from database by project_id, branch_id, or step_index

```mermaid
graph LR
    Entry["async_main()"]
    CheckArgs{"args.project<br/>or args.branch?"}
    NewProject["start_new_project()"]
    LoadProject["load_project()"]
    CreateProject["sm.create_project()"]
    LoadState["sm.load_project()"]
    
    Entry --> CheckArgs
    CheckArgs -->|No| NewProject
    CheckArgs -->|Yes| LoadProject
    
    NewProject --> CreateProject
    LoadProject --> LoadState
    
    CreateProject -->|"Creates Project,<br/>Branch,<br/>ProjectState"| InitialState["ProjectState<br/>step_index=1"]
    LoadState -->|"Loads at specific<br/>step_index"| ExistingState["ProjectState<br/>step_index=N"]
```

**Sources:** [core/cli/main.py:121-192](), [core/cli/main.py:204-210]()

### Project Creation Sequence

When a new project is created:

```python
# core/state/state_manager.py:172-209
async def create_project(self, name, project_type, folder_name):
    project = Project(name=name, project_type=project_type, folder_name=folder_name)
    project.id = uuid4()
    branch = Branch(project=project)
    state = ProjectState.create_initial_state(branch)
    # ...
    return project
```

The `ProjectState.create_initial_state()` method creates the first state with:
- Empty `epics`, `tasks`, `steps`, `iterations`
- A new `Specification` object
- A new `KnowledgeBase` object
- `step_index = 1`

**Sources:** [core/state/state_manager.py:172-246](), [core/db/models/project_state.py:215-235]()

---

## Stage 2: Specification Phase (Epic 1)

### SpecWriter Agent

The first epic is always "Writing Specification", handled by the `SpecWriter` agent.

```mermaid
graph TB
    Start["SpecWriter.run()"]
    CheckSpec{"specification<br/>.description<br/>exists?"}
    
    Start --> CheckSpec
    CheckSpec -->|No| InitSpec["initialize_spec_and_project()"]
    CheckSpec -->|Yes| ChangeSpec["change_spec()"]
    
    InitSpec --> AskUser["Ask user for<br/>app description"]
    AskUser --> GenerateSpec["LLM: build_full_specification"]
    GenerateSpec --> GenerateName["LLM: project_name"]
    GenerateName --> SetSpec["next_state.specification<br/>.description = llm_response"]
    
    ChangeSpec --> RefineLoop["User refinement loop"]
    RefineLoop --> CheckAuth["LLM: need_auth"]
    CheckAuth --> SetAuth["knowledge_base<br/>.user_options['auth']"]
    SetAuth --> CreateEpic["Create Epic 1:<br/>'Build frontend'"]
    
    SetSpec --> Done["AgentResponse.done()"]
    CreateEpic --> Done
```

**Sources:** [core/agents/spec_writer.py:23-33](), [core/agents/spec_writer.py:63-161]()

### State After Specification Phase

After SpecWriter completes:

```python
# State structure at this point:
{
    "specification": {
        "description": "Full LLM-generated spec",
        "original_description": "User's input"
    },
    "epics": [
        {
            "id": "<uuid>",
            "name": "Build frontend",
            "source": "frontend",
            "description": "<spec_description>",
            "completed": False
        }
    ],
    "action": "SPEC_CREATE_STEP_NAME"  # or "SPEC_CHANGE_STEP_NAME"
}
```

**Sources:** [core/agents/spec_writer.py:287-297](), [core/config/actions.py:7-9]()

---

## Stage 3: Architecture and Template Phase

### Architect Agent

The `Architect` agent selects technology stack and applies project templates.

**Responsibilities:**
1. Select project template (if applicable)
2. Determine system dependencies (Node.js, npm, etc.)
3. Determine package dependencies (Express, React, etc.)
4. Apply template scaffolding

```mermaid
graph TB
    Run["Architect.run()"]
    Clone["spec = current_state<br/>.specification.clone()"]
    
    Run --> Clone
    Clone --> CheckExample{"spec.example_project<br/>exists?"}
    
    CheckExample -->|Yes| PrepareExample["prepare_example_project()"]
    CheckExample -->|No| PlanArch["plan_architecture()"]
    
    PlanArch --> SelectTemplate["select_templates()"]
    SelectTemplate --> PickTech["LLM: technologies prompt"]
    PickTech --> CheckCompat["check_compatibility()"]
    CheckCompat --> SetArch["spec.system_dependencies<br/>spec.package_dependencies"]
    
    PrepareExample --> SetArchExample["Set arch from<br/>EXAMPLE_PROJECTS"]
    
    SetArch --> CheckDeps["check_system_dependencies()"]
    SetArchExample --> CheckDeps
    CheckDeps --> SaveSpec["next_state.specification = spec"]
    SaveSpec --> SetAction["action = ARCHITECTURE_STEP_NAME"]
    SetAction --> Done["AgentResponse.done()"]
```

**Sources:** [core/agents/architect.py:99-122](), [core/agents/architect.py:173-197]()

### Template Application

If using a template (e.g., `vite_react_swagger`), SpecWriter applies it:

```python
# core/agents/spec_writer.py:34-62
async def apply_template(self):
    options = self.current_state.knowledge_base.user_options
    if options["auth_type"] == "api_key" or options["auth_type"] == "none":
        template_name = "vite_react_swagger"
    else:
        template_name = "vite_react"
    
    template = template_class(options, self.state_manager, self.process_manager)
    summary = await template.apply()
    
    self.next_state.relevant_files = template.relevant_files
    self.next_state.specification.template_summary = summary
```

Templates create initial file structure asynchronously while other agents continue.

**Sources:** [core/agents/spec_writer.py:34-62](), [core/agents/spec_writer.py:299-302]()

---

## Stage 4: Frontend Epic

### Frontend Agent Workflow

The Frontend agent builds the UI before backend implementation. It operates in distinct sub-stages:

```mermaid
stateDiagram-v2
    [*] --> CheckMessages
    
    CheckMessages: Check epics[-1]["messages"]
    CheckMessages --> StartFrontend: messages empty
    CheckMessages --> RemoveMock: file_paths_to_remove_mock exists
    CheckMessages --> ContinueFrontend: fe_iteration_done False
    CheckMessages --> IterateFrontend: fe_iteration_done True
    
    StartFrontend: start_frontend()
    StartFrontend --> ProcessResponse: LLM: build_frontend
    
    ContinueFrontend: continue_frontend()
    ContinueFrontend --> ProcessResponse: LLM continues
    
    RemoveMock: remove_mock()
    RemoveMock --> RAGSearch: Search API docs
    RAGSearch --> ReplaceAPI: Replace mock with real API
    
    IterateFrontend: iterate_frontend()
    IterateFrontend --> AutoDebug: try_auto_debug()
    AutoDebug --> UserFeedback: Ask for changes
    UserFeedback --> ImplementChanges: LLM: iterate_frontend
    
    ProcessResponse --> SaveFiles: process_response()
    SaveFiles --> CheckDone: Set fe_iteration_done
    
    ReplaceAPI --> CheckDone
    ImplementChanges --> CheckDone
    
    CheckDone --> [*]: end_frontend_iteration()
```

**Sources:** [core/agents/frontend.py:44-59](), [core/agents/frontend.py:61-149]()

### Frontend Sub-stages

#### 4.1 Start Frontend (`FE_START`)

```python
# core/agents/frontend.py:61-110
async def start_frontend(self):
    self.next_state.action = FE_START
    await self.ui.send_project_stage({"stage": ProjectStage.FRONTEND_STARTED})
    
    llm = self.get_llm(FRONTEND_AGENT_NAME, stream_output=True)
    convo = AgentConvo(self).template(
        "build_frontend",
        summary=self.state_manager.template["template"].get_summary(),
        description=self.next_state.epics[-1]["description"],
        first_time_build=True
    )
    response = await llm(convo, parser=DescriptiveCodeBlockParser())
    
    await self.process_response(response.blocks)
    self.next_state.epics[-1]["messages"] = convo.messages
    self.next_state.epics[-1]["fe_iteration_done"] = (
        "done" in response.original_response[-20:].lower().strip() or len(convo.messages) > 11
    )
```

The LLM generates file blocks in format:
```
file: client/src/components/Header.jsx
<code here>
```

These are parsed by `DescriptiveCodeBlockParser` and saved via `process_response()`.

**Sources:** [core/agents/frontend.py:61-110]()

#### 4.2 Continue Frontend (`FE_CONTINUE`)

If the first LLM response indicates more work is needed (`fe_iteration_done = False`):

```python
# core/agents/frontend.py:112-149
async def continue_frontend(self):
    self.next_state.action = FE_CONTINUE
    convo = AgentConvo(self)
    convo.messages = self.current_state.epics[-1]["messages"]
    convo.user(
        "Ok, now think carefully about your previous response. If the response ends by mentioning something about continuing with the implementation, continue but don't implement any files that have already been implemented..."
    )
    response = await llm(convo, parser=DescriptiveCodeBlockParser())
    # ...
```

This loop continues until LLM responds with "DONE" or message count exceeds threshold.

**Sources:** [core/agents/frontend.py:112-149]()

#### 4.3 Iterate Frontend (`FE_ITERATION`)

After initial frontend is complete, user tests and provides feedback:

```python
# core/agents/frontend.py:151-318
async def iterate_frontend(self):
    self.next_state.action = FE_ITERATION
    
    # Try auto-debugging first
    user_input = await self.try_auto_debug()
    
    if not user_input:
        # Ask user for feedback
        answer = await self.ask_question(
            "Do you want to change anything or report a bug?",
            buttons={"yes": "I'm done building the UI"},
            extra_info={"restart_app": True, "collect_logs": True}
        )
        
        if answer.button == "yes":
            # User is satisfied with frontend
            return True
        
        user_input = answer.text
    
    # Implement changes based on feedback
    llm = self.get_llm(FRONTEND_AGENT_NAME, stream_output=True)
    convo = AgentConvo(self).template(
        "iterate_frontend",
        description=self.current_state.epics[-1]["description"],
        user_feedback=user_input
    )
    response = await llm(convo)
    await self.process_response(response.blocks)
```

**Sources:** [core/agents/frontend.py:151-318]()

### Frontend Completion

When frontend iteration completes:

```python
# core/agents/frontend.py:320-354
async def end_frontend_iteration(self, finished: bool):
    if finished:
        self.next_state.action = FE_ITERATION_DONE
        self.next_state.complete_epic()
        
        # Check for INPUT_REQUIRED markers
        inputs = []
        for file in self.current_state.files:
            if not file.content:
                continue
            input_required = self.state_manager.get_input_required(file.content.content, file.path)
            if input_required:
                inputs += [{"file": file.path, "line": line} for line in input_required]
        
        if inputs:
            return AgentResponse.input_required(self, inputs)
    
    return AgentResponse.done(self)
```

The `FE_ITERATION_DONE` action signals that Epic 1 is complete and backend development should begin.

**Sources:** [core/agents/frontend.py:320-354](), [core/config/actions.py:22]()

---

## Stage 5: Backend Development Planning

### TechLead Creates Backend Epics

After frontend is complete, `TechLead` creates backend implementation epics:

```mermaid
graph TB
    TechLead["TechLead.run()"]
    CheckPlan{"Plan exists?"}
    
    TechLead --> CheckPlan
    CheckPlan -->|No| CreatePlan["create_initial_project_epic()"]
    CheckPlan -->|Yes| BreakdownEpic["breakdown_current_epic()"]
    
    CreatePlan --> LLMPlan["LLM: plan.prompt"]
    LLMPlan --> ParseEpics["Parse JSON response"]
    ParseEpics --> CreateSubEpics["Create sub_epics array"]
    CreateSubEpics --> SetEpics["next_state.epics[-1]['sub_epics']"]
    
    BreakdownEpic --> SelectEpic["Get current epic"]
    SelectEpic --> LLMBreakdown["LLM: epic_breakdown.prompt"]
    LLMBreakdown --> ParseTasks["Parse tasks"]
    ParseTasks --> SetTasks["next_state.tasks = tasks"]
    
    SetEpics --> Done["AgentResponse.done()"]
    SetTasks --> Done
```

**Sources:** [core/agents/tech_lead.py:41-110]()

### Epic Creation

The LLM receives the `plan.prompt` template with:
- Project specification
- Existing files (frontend + any backend scaffolding)
- API endpoints called from frontend

It must create backend epics that cover ALL frontend API endpoints.

**Key Prompt Rules (from `project_tasks.prompt`):**
- Rule #1: Only coding epics, no testing/research/deployment epics
- Rule #2: Minimum necessary epics based on complexity
- Rule #3: Clear 1-2 sentence descriptions
- Rule #4 (MOST IMPORTANT): Each epic relates to one or more API endpoints
- Rule #5: Logical order, dependencies last
- Rule #6: Don't reimplement what's already done

**Sources:** [core/prompts/tech-lead/plan.prompt](), [core/prompts/partials/project_tasks.prompt]()

### Example Epic Structure

```python
# After TechLead creates plan:
{
    "epics": [
        {
            "id": "<uuid_1>",
            "name": "Build frontend",
            "source": "frontend",
            "completed": True,  # Now marked complete
            "description": "..."
        },
        {
            "id": "<uuid_2>",
            "name": "Implement backend",
            "source": "app",
            "completed": False,
            "sub_epics": [
                {
                    "id": 0,
                    "description": "Update User model with additional fields"
                },
                {
                    "id": 1,
                    "description": "Create database models for projects and tasks"
                },
                {
                    "id": 2,
                    "description": "Implement CRUD operations for projects"
                },
                {
                    "id": 3,
                    "description": "Implement CRUD operations for tasks"
                }
            ]
        }
    ]
}
```

**Sources:** [core/agents/tech_lead.py:141-186]()

---

## Stage 6: Task Breakdown and Implementation

### Developer Agent Task Breakdown

For each epic, `Developer` breaks it into implementable tasks:

```mermaid
graph TB
    Developer["Developer.run()"]
    CheckTask{"current_task<br/>exists?"}
    
    Developer --> CheckTask
    CheckTask -->|No| GetNextTask["Get first TODO task<br/>from current epic"]
    CheckTask -->|Yes| CheckSteps{"unfinished_steps<br/>exist?"}
    
    GetNextTask --> TaskBreakdown["task_breakdown()"]
    TaskBreakdown --> LLMBreakdown["LLM: epic_breakdown.prompt"]
    LLMBreakdown --> ParseSteps["LLM: parse_task.prompt"]
    ParseSteps --> CreateSteps["Create steps[] array"]
    CreateSteps --> SetSteps["next_state.steps = steps"]
    SetSteps --> Done["AgentResponse.done()"]
    
    CheckSteps -->|Yes| ExecuteStep["Execute current step"]
    CheckSteps -->|No| CompleteTask["complete_task()"]
    
    ExecuteStep --> StepType{"step.type?"}
    StepType -->|save_file| CodeMonkey["→ CodeMonkey"]
    StepType -->|command| Executor["→ Executor"]
    StepType -->|human_intervention| HumanInput["→ HumanInput"]
    
    CompleteTask --> Done
```

**Sources:** [core/agents/developer.py:50-153]()

### Task Structure

Each task contains:

```python
{
    "id": "<uuid>",
    "description": "Implement GET /api/projects endpoint",
    "sub_epic_id": 2,  # Links to sub_epic
    "status": "todo",  # or "in_progress", "done"
    "related_api_endpoints": ["/api/projects"],  # Frontend calls
    "instructions": None  # Set after breakdown
}
```

**Sources:** [core/db/models/project_state.py:158-178](), [core/agents/developer.py:155-253]()

### Step Types

The `parse_task.prompt` generates three types of steps:

1. **`command`** - Run shell command
   ```python
   {
       "type": "command",
       "command": {
           "command": "cd server && npm install express",
           "timeout": 30,
           "success_message": "",
           "command_id": "install_express"
       }
   }
   ```

2. **`save_file`** - Create/modify file (CodeMonkey implements)
   ```python
   {
       "type": "save_file",
       "save_file": {
           "path": "server/routes/projects.js"
       }
   }
   ```

3. **`human_intervention`** - Manual action required
   ```python
   {
       "type": "human_intervention",
       "human_intervention_description": "Create AWS S3 bucket and add credentials to .env"
   }
   ```

**Sources:** [core/prompts/developer/parse_task.prompt:8-23]()

---

## Stage 7: Code Implementation

### CodeMonkey Agent

For each `save_file` step, `CodeMonkey` generates the actual code:

```mermaid
graph TB
    CM["CodeMonkey.run()"]
    GetStep["Get current_step"]
    
    CM --> GetStep
    GetStep --> CheckParallel{"Multiple save_file<br/>steps?"}
    
    CheckParallel -->|Yes| CreateAgents["Create CodeMonkey<br/>instance per step"]
    CheckParallel -->|No| SingleAgent["Single CodeMonkey"]
    
    CreateAgents --> ParallelRun["Run agents in parallel<br/>asyncio.gather()"]
    SingleAgent --> GenerateCode["implement_changes()"]
    
    ParallelRun --> GenerateCode
    
    GenerateCode --> LoadContext["Get relevant files"]
    LoadContext --> LLMGenerate["LLM: implement_changes.prompt"]
    LLMGenerate --> ParseCode["Parse code from response"]
    ParseCode --> SaveFile["sm.save_file(path, content)"]
    SaveFile --> UpdateKB["Update KnowledgeBase"]
    UpdateKB --> Done["AgentResponse.done()"]
```

**Sources:** [core/agents/code_monkey.py:46-151](), [core/agents/orchestrator.py:109-140]()

### Parallel Execution

Multiple `save_file` steps for the same task can execute in parallel:

```python
# core/agents/orchestrator.py:109-140
agent = self.create_agent(response)
if isinstance(agent, list):
    tasks = [single_agent.run() for single_agent in agent]
    responses = await asyncio.gather(*tasks)
    response = self.handle_parallel_responses(agent[0], responses)
    
    # Update knowledge base if APIs or pages were implemented
    should_update_knowledge_base = any(
        "src/pages/" in single_agent.step.get("save_file", {}).get("path", "")
        or "src/api/" in single_agent.step.get("save_file", {}).get("path", "")
        for single_agent in agent
    )
```

This speeds up implementation when multiple files need changes.

**Sources:** [core/agents/orchestrator.py:109-140]()

### State Commit Points

After each step completes, state is committed:

```python
# core/agents/orchestrator.py:418-446
async def handle_done(self, agent: BaseAgent, response: AgentResponse):
    log.debug(
        f"Agent {agent.__class__.__name__} is done, "
        f"committing state for step {self.current_state.step_index}"
    )
    
    await self.state_manager.commit()
    
    # Import any external file changes
    import_files_response = await self.import_files()
    # ...
```

Each commit creates a new `ProjectState` with incremented `step_index`, making the system fully resumable.

**Sources:** [core/agents/orchestrator.py:418-479](), [core/state/state_manager.py:433-478]()

---

## Stage 8: Quality Assurance and Iteration

### Troubleshooter → BugHunter Loop

After task implementation, the QA cycle begins:

```mermaid
stateDiagram-v2
    [*] --> Troubleshooter
    
    Troubleshooter: Generate test instructions
    Troubleshooter --> UserTest: Present instructions to user
    
    UserTest --> UserFeedback: User tests application
    
    UserFeedback --> CheckResult: Evaluate response
    
    CheckResult --> TaskComplete: "Works!"
    CheckResult --> BugHunter: "Bug found"
    CheckResult --> Developer: "Change request"
    
    BugHunter: Investigate issue
    BugHunter --> CheckLogs: Analyze logs
    
    CheckLogs --> AddLogging: Need more info
    CheckLogs --> FixBug: Problem identified
    CheckLogs --> PairProgramming: Complex issue
    
    AddLogging --> Developer: Add logging code
    FixBug --> CodeMonkey: Implement fix
    PairProgramming --> Interactive: Interactive debugging
    Interactive --> CodeMonkey: Solution found
    
    CodeMonkey --> Troubleshooter: Retest
    Developer --> CodeMonkey: Reimplement
    
    TaskComplete --> [*]
```

**Sources:** [core/agents/troubleshooter.py:39-168](), [core/agents/bug_hunter.py:45-280]()

### Iteration Structure

Each bug hunting cycle creates an iteration:

```python
# core/db/models/project_state.py:133-156
{
    "id": "<uuid>",
    "user_feedback": "Button doesn't work when clicked",
    "status": "check_logs",  # IterationStatus values
    "bug_reproduction_instructions": "...",
    "source": "troubleshooting",
    "description": "Fix button click handler"
}
```

**Iteration Statuses:**
- `HUNTING_FOR_BUG` / `check_logs` - Analyzing logs
- `AWAITING_LOGGING` - Need more debug info
- `AWAITING_BUG_FIX` - Implementing fix
- `START_PAIR_PROGRAMMING` - Interactive debugging
- `DONE` - Issue resolved

**Sources:** [core/db/models/project_state.py:43-57](), [core/agents/bug_hunter.py:87-158]()

---

## Stage 9: Task and Epic Completion

### Task Completion

When all steps are done and tests pass:

```python
# core/db/models/project_state.py:327-344
def complete_task(self):
    if not self.unfinished_tasks:
        raise ValueError("There are no unfinished tasks to complete")
    
    log.debug(f"Completing task {self.unfinished_tasks[0]['description']}")
    self.set_current_task_status(TaskStatus.DONE)
    self.steps = []
    self.iterations = []
    self.relevant_files = None
    self.modified_files = {}
    
    # If all tasks in epic are done, complete the epic
    if not self.unfinished_tasks and self.unfinished_epics:
        self.complete_epic()
```

Task completion clears temporary state (`steps`, `iterations`, `relevant_files`) and marks task as `DONE`.

**Sources:** [core/db/models/project_state.py:327-344]()

### Epic Completion

When all tasks in an epic are complete:

```python
# core/db/models/project_state.py:345-356
def complete_epic(self):
    if not self.unfinished_epics:
        raise ValueError("There are no unfinished epics to complete")
    
    log.debug(f"Completing epic {self.unfinished_epics[0]['name']}")
    self.unfinished_epics[0]["completed"] = True
    self.tasks = []
    flag_modified(self, "epics")
    
    if len(self.unfinished_epics) > 0:
        self.next_state.action = PS_EPIC_COMPLETE.format(self.unfinished_epics[0]["name"])
```

This marks the epic as complete and clears tasks, preparing for the next epic.

**Sources:** [core/db/models/project_state.py:345-356]()

---

## Stage 10: Project Completion and Continuation

### End-of-Project Decision

When all epics are complete, TechLead asks about next steps:

```python
# core/agents/tech_lead.py:217-258
if not self.current_state.unfinished_epics:
    # All epics done - ask what's next
    user_response = await self.ask_question(
        "All epics are completed! Do you have a new feature to add?",
        buttons={
            "continue": "Yes, I have a new feature",
            "end": "No, I'm done"
        }
    )
    
    if user_response.button == "continue":
        # Start new feature epic
        feature_description = await self.ask_question("What feature would you like to add?")
        return AgentResponse.update_specification(self, feature_description.text)
    
    elif user_response.button == "end":
        return AgentResponse.exit(self)
```

**Three possible outcomes:**

1. **New Feature** - Returns `ResponseType.UPDATE_SPECIFICATION`, triggering SpecWriter to update spec and create new epic
2. **Quick Task** - User provides immediate task description, bypassing epic creation
3. **Project Complete** - Returns `ResponseType.EXIT`, ending the session

**Sources:** [core/agents/tech_lead.py:217-258](), [core/agents/response.py:37-61]()

### Feature Addition Flow

When adding a feature:

```mermaid
graph LR
    AllEpicsDone["All epics completed"]
    AskFeature["TechLead asks:<br/>New feature?"]
    UserYes["User: Yes"]
    UpdateSpec["ResponseType.UPDATE_SPECIFICATION"]
    SpecWriter["SpecWriter.update_spec()"]
    UpdateDesc["Update specification.description"]
    TechLead["TechLead creates new epic"]
    
    AllEpicsDone --> AskFeature
    AskFeature --> UserYes
    UserYes --> UpdateSpec
    UpdateSpec --> SpecWriter
    SpecWriter --> UpdateDesc
    UpdateDesc --> TechLead
    TechLead -->|"Repeat<br/>from Stage 5"| TaskBreakdown["Task breakdown..."]
```

**Sources:** [core/agents/tech_lead.py:217-258](), [core/agents/spec_writer.py:305-343]()

---

## State Transition and Tracking

### Two-State Transaction Model

GPT Pilot uses a "current" and "next" state pattern:

```mermaid
graph LR
    Current["current_state<br/>(read-only)"]
    Next["next_state<br/>(writable)"]
    Commit["commit()"]
    NewCurrent["new current_state"]
    NewNext["new next_state"]
    
    Current -.->|"Agents read from"| AgentRead["Agent.current_state"]
    Next -.->|"Agents write to"| AgentWrite["Agent.next_state"]
    
    AgentWrite --> Commit
    Commit --> NewCurrent
    Commit --> NewNext
    NewCurrent -.->|"becomes"| Current
    NewNext -.->|"becomes"| Next
```

**Key methods:**

```python
# core/state/state_manager.py:433-478
async def commit(self):
    """Commit next_state to database."""
    await self.commit_with_retry()
    
    # Close and reopen session (best practice)
    self.current_session.expunge_all()
    await self.session_manager.close()
    self.current_session = await self.session_manager.start()
    
    # Swap states
    self.current_state = self.next_state
    self.current_session.add(self.next_state)
    self.next_state = await self.current_state.create_next_state()
```

This ensures:
- All changes are atomic (all-or-nothing)
- Agents can't corrupt committed states
- System is always resumable from last commit

**Sources:** [core/state/state_manager.py:433-478]()

### Resume and Time-Travel

Users can resume from any step:

```bash
# Resume at specific step
python main.py --project <uuid> --step 42

# Resume at latest step
python main.py --project <uuid>
```

```python
# core/state/state_manager.py:272-415
async def load_project(self, project_id, branch_id, step_index, project_state_id):
    # Load state at specific step_index
    if step_index is not None:
        state = await branch.get_state_at_step(step_index)
    else:
        state = await branch.get_last_state()
    
    # Delete all states after this one
    await state.delete_after()
    
    self.current_state = state
    self.next_state = await state.create_next_state()
    self.file_system = await self.init_file_system(load_existing=True)
```

This enables:
- Rollback after mistakes
- Replay for debugging
- Branch from earlier points

**Sources:** [core/state/state_manager.py:272-415](), [core/db/models/project_state.py:492-534]()

---

## Action Tracking

The `action` field on `ProjectState` records what happened:

```python
# Common action values:
SPEC_CREATE_STEP_NAME = "Create specification"
SPEC_CHANGE_STEP_NAME = "Refine specification"
ARCHITECTURE_STEP_NAME = "Project architecture"
FE_START = "Start frontend"
FE_CONTINUE = "Continue frontend"
FE_ITERATION = "Iterate frontend"
FE_ITERATION_DONE = "Frontend iteration done"
DEV_TASK_START = "Start task"
DEV_TASK_BREAKDOWN = "Break down task"
CM_UPDATE_FILES = "Update files"
BH_START_BUG_HUNT = "Start bug hunt"
TC_TASK_DONE = "Task done"
PS_EPIC_COMPLETE = "Epic '{}' complete"
```

This creates a human-readable audit trail of project progression.

**Sources:** [core/config/actions.py:1-33]()

---

## Summary: Complete Lifecycle Flow

```mermaid
graph TB
    Init["1. Initialize:<br/>create_project() or load_project()"]
    Spec["2. Specification:<br/>SpecWriter → specification.description"]
    Arch["3. Architecture:<br/>Architect → system/package dependencies"]
    FE["4. Frontend:<br/>Frontend → UI files in client/"]
    Plan["5. Planning:<br/>TechLead → epics with sub_epics"]
    Loop["6-8. Implementation Loop"]
    Complete["9. Completion"]
    
    Init --> Spec
    Spec --> Arch
    Arch --> FE
    FE --> Plan
    Plan --> Loop
    
    Loop --> TaskBreak["Developer → tasks → steps"]
    TaskBreak --> CodeImpl["CodeMonkey → save files"]
    CodeImpl --> QA["Troubleshooter/BugHunter → iterations"]
    QA --> TaskDone{"Task done?"}
    TaskDone -->|No| CodeImpl
    TaskDone -->|Yes| EpicDone{"Epic done?"}
    EpicDone -->|No| TaskBreak
    EpicDone -->|Yes| AllDone{"All epics done?"}
    AllDone -->|No| TaskBreak
    AllDone -->|Yes| Complete
    
    Complete --> NewFeature{"Add feature?"}
    NewFeature -->|Yes| Spec
    NewFeature -->|No| End["Project Complete"]
```

**Key Characteristics:**

1. **Sequential Stages** - Each stage builds on previous outputs
2. **State Commits** - Every agent completion creates new ProjectState
3. **Resumable** - Can reload at any step_index
4. **Iterative** - Bug hunting loops until tests pass
5. **Extensible** - Can add features after initial completion

**Sources:** [core/agents/orchestrator.py:48-167](), [core/cli/main.py:194-321]()

---

# Page: Code Generation and File Management

# Code Generation and File Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [core/agents/code_monkey.py](core/agents/code_monkey.py)
- [core/cli/helpers.py](core/cli/helpers.py)
- [core/cli/main.py](core/cli/main.py)
- [core/db/models/project.py](core/db/models/project.py)
- [core/db/models/project_state.py](core/db/models/project_state.py)
- [core/db/v0importer.py](core/db/v0importer.py)
- [core/prompts/bug-hunter/iteration.prompt](core/prompts/bug-hunter/iteration.prompt)
- [core/prompts/bug-hunter/log_data.prompt](core/prompts/bug-hunter/log_data.prompt)
- [core/prompts/developer/breakdown.prompt](core/prompts/developer/breakdown.prompt)
- [core/prompts/problem-solver/get_alternative_solutions.prompt](core/prompts/problem-solver/get_alternative_solutions.prompt)
- [core/prompts/troubleshooter/iteration.prompt](core/prompts/troubleshooter/iteration.prompt)
- [core/state/state_manager.py](core/state/state_manager.py)
- [core/ui/api_server.py](core/ui/api_server.py)
- [tests/cli/test_cli.py](tests/cli/test_cli.py)
- [tests/db/test_project.py](tests/db/test_project.py)

</details>



## Purpose and Scope

This document describes how GPT Pilot generates code and manages files throughout the development lifecycle. It covers the `<pythagoracode>` tag system used by LLM agents to structure code changes, the `CodeMonkey` agent responsible for implementing those changes, and the file storage architecture that provides versioning and content deduplication.

For information about how files are filtered for relevance in LLM context, see [Context Filtering and Relevance](#6.3). For details on the state management system that tracks file versions, see [State Management System](#3.2).

---

## The `<pythagoracode>` Tag System

### Overview

GPT Pilot uses a custom XML-like tag system to allow LLM agents to specify file changes in a structured format. Rather than relying on ambiguous natural language instructions like "ensure that..." or "make sure that...", agents wrap code changes in `<pythagoracode>` tags that explicitly identify the target file.

```xml
<pythagoracode file="client/src/api/api.ts">
// Code changes here
</pythagoracode>
```

### Tag Structure

The system enforces strict rules through prompt engineering:

| Rule | Description |
|------|-------------|
| **File attribute required** | Each tag must include a `file` attribute with the relative path |
| **One file per block** | Changes for multiple files cannot be mixed in a single block |
| **No other markers** | Backticks and other code markers are forbidden inside tags |
| **Complete code** | Tags must contain full implementation, not partial snippets |

### Parsing Implementation

The tag parser uses a regular expression to extract file-specific code blocks:

```python
PATTERN = r'<pythagoracode\s+file="(.*?)">(.*?)</pythagoracode>'
```

This pattern captures:
- The file path from the `file` attribute
- The complete code content between opening and closing tags

The parser returns a list of dictionaries, each containing `file_name` and `file_content` keys for downstream processing by the `CodeMonkey` agent.

**Sources:** [core/agents/code_monkey.py:61-65](), [core/prompts/developer/breakdown.prompt:36](), [core/prompts/bug-hunter/iteration.prompt:48](), [core/prompts/troubleshooter/iteration.prompt:1-56]()

---

## CodeMonkey Agent Architecture

### Agent Workflow

```mermaid
graph TB
    Step["Step with save_file instruction"] --> Check{"Describe files<br/>or implement?"}
    
    Check -->|implement| GetFile["Get current file<br/>from StateManager"]
    Check -->|describe| DescFiles["describe_files()"]
    
    GetFile --> Strategy{"Has access token<br/>and pythagoracode<br/>blocks?"}
    
    Strategy -->|yes| TryRelace["Try Relace model<br/>IMPLEMENT_CHANGES_AGENT"]
    Strategy -->|no| UseOpenAI["Use OpenAI/Anthropic<br/>CODE_MONKEY_AGENT"]
    
    TryRelace -->|success| Response[Response]
    TryRelace -->|fail| UseOpenAI
    
    UseOpenAI --> Response
    
    Response --> Accept["accept_changes()<br/>Generate diff<br/>Save to disk"]
    Accept --> InputCheck{"Input<br/>required?"}
    
    InputCheck -->|yes| ReturnInput["Return INPUT_REQUIRED"]
    InputCheck -->|no| Complete["Complete step<br/>Return DONE"]
    
    DescFiles --> Parallel["Describe files in parallel<br/>using asyncio.gather"]
    Parallel --> SaveMeta["Save descriptions<br/>to FileContent.meta"]
    SaveMeta --> Complete
```

**CodeMonkey Agent Workflow**

### Implementation Strategies

The `CodeMonkey` agent uses a two-tier strategy for code implementation:

#### 1. Relace Model (Primary)
When available, the agent attempts to use the Relace code merge model, a specialized LLM optimized for code modifications:

**Conditions:**
- Access token is available
- Instructions contain `<pythagoracode>` blocks
- Block exists for the target file

**Input format:**
```json
{
  "initialCode": "<current file content>",
  "editSnippet": "<code from pythagoracode block>"
}
```

The model returns the complete modified file without additional markup.

#### 2. Standard LLM (Fallback)
If Relace is unavailable or fails, the agent falls back to standard LLM providers (OpenAI, Anthropic, Groq):

**Prompt template:** `implement_changes`

**Context provided:**
- File name and current content
- Task instructions from `Developer` agent
- User feedback from iterations (if any)
- Review feedback from previous attempts (if reworking)

### File Description System

After code generation completes, the `CodeMonkey` must describe newly created or modified files. This metadata is used for context filtering in subsequent tasks.

```mermaid
graph LR
    Files["Files without<br/>description"] --> Filter["Filter: files in<br/>next_state without<br/>meta.description"]
    
    Filter --> Empty{"Content<br/>empty?"}
    
    Empty -->|yes| SetEmpty["Set meta:<br/>description='Empty file'<br/>references=[]"]
    Empty -->|no| Describe["Call LLM with<br/>DESCRIBE_FILES_AGENT"]
    
    Describe --> Template["Use describe_file prompt<br/>with path and content"]
    Template --> Parse["Parse FileDescription schema"]
    Parse --> SaveDesc["Save to FileContent.meta:<br/>description, references"]
    
    SetEmpty --> Gather["asyncio.gather all tasks"]
    SaveDesc --> Gather
    Gather --> Done["Return DONE"]
```

**File Description Workflow**

The `FileDescription` schema captures:

| Field | Type | Description |
|-------|------|-------------|
| `summary` | string | Detailed description of file purpose and major functionality |
| `references` | list[str] | Project-relative paths of files this file imports/includes |

**Sources:** [core/agents/code_monkey.py:68-233](), [core/config:12]()

---

## File Storage Architecture

### Virtual File System (VFS) Abstraction

GPT Pilot uses a `VirtualFileSystem` abstraction layer to support multiple storage backends:

```mermaid
graph TB
    subgraph "VFS Interface"
        VFS["VirtualFileSystem<br/>(Abstract Base Class)"]
    end
    
    subgraph "Implementations"
        Local["LocalDiskVFS<br/>Production storage"]
        Memory["MemoryVFS<br/>Testing/import"]
    end
    
    subgraph "LocalDiskVFS Components"
        Root["workspace_root<br/>config setting"]
        Ignore["IgnoreMatcher<br/>ignore_paths config"]
        Disk["Physical disk I/O"]
    end
    
    subgraph "Operations"
        Save["save(path, content)"]
        Read["read(path)"]
        List["list()"]
        Remove["remove(path)"]
        Hash["hash_string(content)"]
    end
    
    VFS --> Local
    VFS --> Memory
    
    Local --> Root
    Local --> Ignore
    Local --> Disk
    
    VFS --> Operations
```

**Virtual File System Architecture**

#### LocalDiskVFS Configuration

| Setting | Purpose |
|---------|---------|
| `workspace_root` | Base directory for all project folders |
| `allow_existing` | Whether to use existing folder (true when loading projects) |
| `ignore_matcher` | Filters files based on patterns and size thresholds |

#### MemoryVFS Use Cases

The in-memory implementation is used for:
- Unit testing without disk I/O
- Database import operations that shouldn't overwrite user changes
- Temporary file manipulation during analysis

### Database Storage Model

```mermaid
graph TB
    subgraph "ProjectState"
        State["ProjectState<br/>step_index, branch_id"]
        Files["files: list[File]"]
    end
    
    subgraph "File Model"
        File["File<br/>id, path, project_state_id,<br/>content_id"]
        FileContent["FileContent<br/>id, hash, content, meta"]
    end
    
    subgraph "Content Metadata"
        Meta["meta: dict<br/>- description: str<br/>- references: list[str]"]
    end
    
    State --> Files
    Files --> File
    File -->|Many-to-One| FileContent
    FileContent --> Meta
    
    File -.->|external: bool| Flag["Flag: created by<br/>user vs Pythagora"]
```

**File and FileContent Database Schema**

#### File Model

The `File` model represents a file at a specific point in project history:

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `path` | string | Relative path within project |
| `project_state_id` | UUID | Foreign key to ProjectState |
| `content_id` | int | Foreign key to FileContent |

#### FileContent Model

The `FileContent` model stores deduplicated file content:

| Column | Type | Description |
|--------|------|-------------|
| `id` | int | Primary key |
| `hash` | string | SHA-256 hash of content |
| `content` | text | Actual file content |
| `meta` | dict | Metadata (description, references) |

### Content Deduplication Mechanism

```mermaid
graph LR
    Save["save_file(path, content)"] --> Hash["Calculate SHA-256 hash"]
    
    Hash --> Store["FileContent.store(session, hash, content)"]
    
    Store --> Check{"Hash exists<br/>in DB?"}
    
    Check -->|yes| Reuse["Return existing<br/>FileContent instance"]
    Check -->|no| Create["Create new<br/>FileContent record"]
    
    Reuse --> Link["File.content_id = fc.id"]
    Create --> Link
    
    Link --> State["Add to next_state.files"]
```

**Content Deduplication Process**

This approach provides:

1. **Storage efficiency**: Identical files across states share one content record
2. **Fast equality checks**: Compare hashes instead of full content
3. **Change detection**: Different hash indicates modified file
4. **Reference tracking**: Multiple `File` records can point to same `FileContent`

**Sources:** [core/state/state_manager.py:589-627](), [core/db/models/project_state.py:428-490](), [core/disk/vfs.py:1-200]()

---

## File Operations

### save_file Workflow

```mermaid
sequenceDiagram
    participant Agent
    participant SM as StateManager
    participant VFS as VirtualFileSystem
    participant DB as Database
    participant NS as next_state
    
    Agent->>SM: save_file(path, content, metadata)
    
    SM->>SM: get_file_by_path(path)
    Note over SM: Check if file exists
    
    SM->>VFS: read(path)
    Note over VFS: Get original content<br/>for telemetry
    
    SM->>VFS: save(path, content)
    Note over VFS: Write to disk immediately
    
    SM->>VFS: hash_string(content)
    VFS-->>SM: SHA-256 hash
    
    SM->>DB: FileContent.store(session, hash, content, metadata)
    DB-->>SM: FileContent instance
    
    SM->>NS: save_file(path, file_content)
    Note over NS: Updates or creates File<br/>Adds to relevant_files<br/>Tracks in modified_files
    
    NS-->>SM: File instance
    SM-->>Agent: void
```

**save_file Operation Sequence**

#### Key Behaviors

| Aspect | Behavior |
|--------|----------|
| **Immediate write** | File is written to VFS immediately, before DB commit |
| **Rollback safety** | DB transaction can roll back without affecting disk |
| **Metadata handling** | If not provided, metadata is reset to force re-description |
| **Relevant files tracking** | Path is added to `next_state.relevant_files` list |
| **Modified files tracking** | Original content is stored in `modified_files` dict |

### import_files Operation

The `import_files` method synchronizes the database with the current workspace state:

**Algorithm:**
1. List all files in VFS
2. For each file:
   - Read content from disk
   - Compare hash with database version
   - If different or new, import to `next_state`
3. Identify removed files:
   - Files in database but not in workspace
   - Remove from `next_state.files`

**Use cases:**
- Detecting external changes made by user
- Initial project import
- Resuming after manual edits

### restore_files Operation

The `restore_files` method overwrites the workspace with database state:

**Algorithm:**
1. List files in workspace
2. Remove files not in database
3. For each file in database:
   - Write content to VFS
   - Overwrite any existing file

**Warning:** This operation can destroy user changes and should be used cautiously.

### Modified File Detection

```mermaid
graph TB
    Start["get_modified_files()"] --> List["List files in workspace"]
    
    List --> Loop["For each workspace file"]
    
    Loop --> Read["Read content from VFS"]
    Read --> Get["Get File from current_state"]
    
    Get --> Exists{"File exists<br/>in DB?"}
    
    Exists -->|yes| Compare["Compare content"]
    Exists -->|no| AddNew["Add to modified_files"]
    
    Compare -->|different| AddMod["Add to modified_files"]
    Compare -->|same| Continue["Continue"]
    
    AddNew --> Continue
    AddMod --> Continue
    
    Continue --> CheckRemoved["For each DB file"]
    CheckRemoved --> InWS{"In workspace?"}
    
    InWS -->|no| AddDel["Add to modified_files"]
    InWS -->|yes| Done
    
    AddDel --> Done["Return modified_files list"]
```

**Modified File Detection Algorithm**

This method returns a list of file paths that differ between workspace and database, enabling:
- Offline change detection
- User notification before overwriting
- Statistics tracking

**Sources:** [core/state/state_manager.py:589-839]()

---

## Version Control and State Management

### File Cloning in State Transitions

Each `ProjectState` maintains its own list of `File` objects. When creating a new state, files are cloned from the previous state:

```mermaid
graph TB
    subgraph "Current State (step N)"
        CS["ProjectState N"]
        CSF["files[<br/>  File(path='a.js', content_id=1),<br/>  File(path='b.js', content_id=2)<br/>]"]
    end
    
    subgraph "Next State (step N+1)"
        NS["ProjectState N+1"]
        NSF["files[<br/>  File(path='a.js', content_id=1),<br/>  File(path='b.js', content_id=3)<br/>]"]
    end
    
    subgraph "FileContent Pool"
        FC1["FileContent 1<br/>hash: abc123<br/>content: '...'"]
        FC2["FileContent 2<br/>hash: def456<br/>content: '...'"]
        FC3["FileContent 3<br/>hash: ghi789<br/>content: '...'"]
    end
    
    CS --> CSF
    NS --> NSF
    
    CSF -.->|References| FC1
    CSF -.->|References| FC2
    NSF -.->|References| FC1
    NSF -.->|References| FC3
    
    Note1["File 'a.js' unchanged:<br/>same content_id"]
    Note2["File 'b.js' modified:<br/>new content_id"]
```

**File Cloning and Content Sharing Across States**

#### Clone Implementation

The `create_next_state()` method performs the cloning:

1. **Clone File objects**: Each `File` in the current state gets a new `File` instance with:
   - Same `path`
   - Same `content_id` (references same `FileContent`)
   - New `id` (new primary key)
   - New `project_state_id` (references next state)

2. **Load FileContent**: For each cloned file, explicitly load the `FileContent` relationship from database

3. **Efficient copying**: Deep copy metadata (`epics`, `tasks`, `steps`) but share immutable `FileContent` records

### Atomic Commits

```mermaid
sequenceDiagram
    participant Agent
    participant SM as StateManager
    participant NS as next_state
    participant Session
    participant DB as Database
    
    Agent->>SM: Multiple operations on next_state
    Note over NS: Files modified, tasks updated, etc.
    
    Agent->>SM: commit()
    
    SM->>Session: commit()
    Note over Session: All changes or nothing
    
    Session->>DB: Write to database
    DB-->>Session: Success
    
    SM->>Session: expunge_all()
    SM->>Session: close()
    
    SM->>SM: current_session = new session
    SM->>SM: current_state = next_state
    
    SM->>NS: create_next_state()
    Note over SM: Clone files and metadata<br/>for next round of changes
    
    NS-->>SM: New next_state
```

**Atomic Commit Process**

#### Commit Guarantees

| Property | Implementation |
|----------|----------------|
| **Atomicity** | All changes in `next_state` commit together or roll back together |
| **Isolation** | `current_state` remains read-only and unaffected during modifications |
| **Session lifecycle** | New session created after each commit for shorter-lived transactions |
| **Retry logic** | 3 attempts with 1-second waits to handle `PendingRollbackError` |

#### State Transitions

After a successful commit:
1. `next_state` becomes `current_state`
2. New `next_state` is created by cloning
3. `FileContent` for each file is preloaded for efficient access
4. Step index increments by 1

### Rollback and State Deletion

The `delete_after()` method removes all states after a given point in history:

**Cleanup operations:**
1. Delete `ProjectState` records with higher `step_index`
2. Delete associated `UserInput` records
3. Delete orphaned `FileContent` records (not referenced by any `File`)
4. Delete orphaned `KnowledgeBase` records
5. Delete orphaned `Specification` records

This enables:
- Time-travel debugging by loading earlier states
- Branch-point creation for alternative implementations
- Undo operations when changes are unsatisfactory

**Sources:** [core/state/state_manager.py:433-479](), [core/db/models/project_state.py:269-315](), [core/db/models/project_state.py:492-534]()

---

## Integration Points

### CodeMonkey to File Management Flow

```mermaid
graph TB
    Dev["Developer agent<br/>Creates task breakdown"] --> Instructions["instructions with<br/>&lt;pythagoracode&gt; blocks"]
    
    Instructions --> Orca["Orchestrator<br/>Processes steps"]
    
    Orca --> Step["Step: save_file<br/>path: 'src/api.ts'"]
    
    Step --> CM["CodeMonkey.run()"]
    
    CM --> Extract["extract_code_blocks(instructions)"]
    Extract --> Blocks["blocks = [<br/>  {file: 'src/api.ts', content: '...'},<br/>  {file: 'src/db.ts', content: '...'}<br/>]"]
    
    Blocks --> Implement["implement_changes()"]
    
    Implement --> LLM["Get new_content<br/>from LLM"]
    
    LLM --> Accept["accept_changes(path, old, new)"]
    
    Accept --> Diff["Generate diff<br/>Send to UI"]
    
    Diff --> Save["StateManager.save_file(path, content)"]
    
    Save --> VFS["Write to VFS"]
    Save --> DB["Store in FileContent"]
    Save --> State["Add to next_state"]
    
    State --> Complete["Complete step"]
    
    Complete --> NextStep{"More steps?"}
    NextStep -->|yes| Step
    NextStep -->|no| Commit["StateManager.commit()"]
```

**End-to-End Code Generation and File Storage Flow**

This integration ensures that:
- LLM-generated code is immediately visible on disk for testing
- Database maintains consistent history for rollback
- UI receives real-time updates about file changes
- Content deduplication reduces storage overhead
- Version control enables time-travel debugging

**Sources:** [core/agents/code_monkey.py:72-233](), [core/state/state_manager.py:589-627](), [core/agents/orchestrator.py:1-500]()

---

# Page: Context Filtering and Relevance

# Context Filtering and Relevance

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [core/agents/base.py](core/agents/base.py)
- [core/agents/bug_hunter.py](core/agents/bug_hunter.py)
- [core/agents/developer.py](core/agents/developer.py)
- [core/agents/mixins.py](core/agents/mixins.py)
- [core/agents/tech_lead.py](core/agents/tech_lead.py)
- [core/agents/troubleshooter.py](core/agents/troubleshooter.py)
- [core/llm/azure_client.py](core/llm/azure_client.py)
- [core/llm/base.py](core/llm/base.py)
- [core/llm/openai_client.py](core/llm/openai_client.py)
- [core/utils/__init__.py](core/utils/__init__.py)
- [core/utils/text.py](core/utils/text.py)
- [tests/agents/test_base.py](tests/agents/test_base.py)
- [tests/llm/test_openai.py](tests/llm/test_openai.py)
- [tests/ui/test_ipc_client.py](tests/ui/test_ipc_client.py)

</details>



## Purpose and Scope

This document explains how GPT Pilot manages and filters context to stay within LLM token limits while providing agents with sufficient information to complete tasks. The system employs multiple strategies:

1. **File Relevance Detection**: Identifying which project files are needed for specific tasks
2. **Log Trimming**: Removing verbose log output from conversation history
3. **Token Counting and Management**: Tracking prompt size and pruning when necessary

These mechanisms work together to ensure agents receive focused, relevant context without exceeding the token limits imposed by LLM providers (typically 128K-200K tokens).

For information about how agents use this filtered context to generate code, see [Code Generation and File Management](#6.2).

Sources:
- [core/agents/mixins.py:122-189]()
- [core/llm/base.py:167-186]()
- [core/utils/text.py:6-42]()

## Context Management Architecture

GPT Pilot implements a multi-layered context management system to optimize LLM interactions:

### Context Management Flow

```mermaid
flowchart TB
    Task["Task Assignment"] --> RF["RelevantFilesMixin.get_relevant_files_parallel()"]
    RF --> FE["get_relevant_files(dir_type='client')"]
    RF --> BE["get_relevant_files(dir_type='server')"]
    
    FE --> FELLM["LLM Call: filter_files.prompt"]
    BE --> BELLM["LLM Call: filter_files.prompt"]
    
    FELLM --> FEFiles["Frontend Files List"]
    BELLM --> BEFiles["Backend Files List"]
    
    FEFiles --> Merge["Merge & Deduplicate"]
    BEFiles --> Merge
    
    Merge --> Store["current_state.relevant_files"]
    Store --> Convo["AgentConvo.template()"]
    
    Convo --> TokenCheck["BaseLLMClient: Token Counting"]
    TokenCheck --> Exceed{"Exceeds 150K tokens?"}
    
    Exceed -- "Yes" --> TrimLogs["trim_logs()"]
    Exceed -- "No" --> SendLLM["Send to LLM"]
    
    TrimLogs --> SendLLM
```

The primary goals of context management are:
- Provide sufficient context about the existing codebase
- Focus agent attention on files that matter for the current task
- Prevent context overflow by excluding irrelevant files
- Trim verbose logs from conversation history
- Track token usage to stay within LLM limits

Sources:
- [core/agents/mixins.py:130-151]()
- [core/llm/base.py:167-186]()
- [core/utils/text.py:6-42]()

## File Relevance System

### RelevantFilesMixin Implementation

The `RelevantFilesMixin` class provides file filtering functionality to multiple agents. The core implementation uses parallel processing to handle frontend and backend files separately:

```mermaid
graph TB
    subgraph "RelevantFilesMixin Class"
        GRFP["get_relevant_files_parallel()"]
        GRF["get_relevant_files(dir_type)"]
    end
    
    subgraph "Agent Classes"
        TL["TechLead"]
        Dev["Developer"]
        TS["Troubleshooter"]
        BH["BugHunter"]
    end
    
    TL --> |"inherits"| GRFP
    Dev --> |"inherits"| GRFP
    TS --> |"inherits"| GRFP
    BH --> |"inherits"| GRFP
    
    GRFP --> |"asyncio.gather()"| GRF
    GRF --> |"LLM call"| FilterPrompt["filter_files.prompt"]
    FilterPrompt --> |"JSONParser"| RelevantFiles["RelevantFiles schema"]
    RelevantFiles --> |"returns"| Paths["list[str]"]
```

### Key Methods

| Method | Location | Purpose |
|--------|----------|---------|
| `get_relevant_files_parallel()` | [core/agents/mixins.py:130-151]() | Launches parallel tasks for frontend/backend filtering |
| `get_relevant_files()` | [core/agents/mixins.py:153-188]() | Filters files for a specific directory type using LLM |
| `filter_files.prompt` | Template system | Provides context and instructions to LLM for filtering |

### Parallel Processing Flow

```mermaid
sequenceDiagram
    participant Agent
    participant Mixin as RelevantFilesMixin
    participant LLM as GET_RELEVANT_FILES_AGENT_NAME
    
    Agent->>Mixin: get_relevant_files_parallel(user_feedback, solution_description)
    
    par Frontend Task
        Mixin->>LLM: get_relevant_files(dir_type="client")
        LLM-->>Mixin: frontend_files[]
    and Backend Task
        Mixin->>LLM: get_relevant_files(dir_type="server")
        LLM-->>Mixin: backend_files[]
    end
    
    Mixin->>Mixin: Merge lists
    Mixin->>Mixin: Filter non-existent files
    Mixin->>Agent: Update current_state.relevant_files
    Mixin->>Agent: Update next_state.relevant_files
```

### LLM-Based File Selection

The `get_relevant_files()` method uses an LLM to determine file relevance:

1. Creates an `AgentConvo` with the `filter_files` template
2. Injects `user_feedback`, `solution_description`, and `dir_type` into the prompt
3. Requires the response to match the `RelevantFiles` schema (Pydantic model)
4. Parses the response using `JSONParser(RelevantFiles)`
5. Filters the returned paths to only include files that exist in `current_state.files`
6. Appends any `ALWAYS_RELEVANT_FILES` that weren't included

Sources:
- [core/agents/mixins.py:153-188]()
- [core/agents/mixins.py:21-24]()
- [core/config/magic_words.py]() (defines `ALWAYS_RELEVANT_FILES`)

## Log Trimming System

As conversations with the LLM grow longer, logs from command execution and bug reproduction accumulate in the context. The `trim_logs()` function removes verbose log output to reduce token usage.

### trim_logs() Function

```mermaid
flowchart LR
    Input["Conversation String"] --> Search["Find log markers"]
    Search --> Markers["'Here are the backend logs'<br/>'Here are the frontend logs'"]
    Markers --> Found{"Marker found?"}
    Found -- "Yes" --> Trim["Truncate at marker position"]
    Found -- "No" --> Return["Return original string"]
    Trim --> Return
```

**Implementation Details:**

The function searches for two marker phrases:
- `"Here are the backend logs"`
- `"Here are the frontend logs"`

When found, it truncates the string at the first occurrence, effectively removing all log output that follows.

**Usage in Context Management:**

The `BaseLLMClient.__call__()` method uses `trim_logs()` when the prompt exceeds 150,000 tokens:

```python
if prompt_tokens > 150_000:
    # Find the message containing logs
    for i, msg in enumerate(reversed(convo.messages)):
        if "Here are the backend logs" in msg["content"] or \
           "Here are the frontend logs" in msg["content"]:
            index = len(convo.messages) - 1 - i
            break
    
    if index != -1:
        # Trim all messages before the log message
        for i, msg in enumerate(convo.messages):
            if i < index:
                convo.messages[i]["content"] = trim_logs(convo.messages[i]["content"])
```

This ensures that historical log data doesn't consume excessive tokens while preserving recent, relevant information.

Sources:
- [core/utils/text.py:6-42]()
- [core/llm/base.py:169-181]()
- [core/agents/tech_lead.py:234-236]() (example usage in task descriptions)

## Token Management and Context Windows

### Token Counting

GPT Pilot uses the `tiktoken` library to estimate token counts before sending requests to LLMs:

```mermaid
flowchart TD
    Messages["convo.messages"] --> Encode["tiktoken.encode()"]
    Encode --> Count["Sum tokens across messages"]
    Count --> Check{"prompt_tokens > 150,000?"}
    
    Check -- "No" --> Send["Send to LLM"]
    Check -- "Yes" --> Trim["Apply trim_logs()"]
    Trim --> Send
    
    Send --> Response["LLM Response"]
    Response --> Log["LLMRequestLog"]
    Log --> Store["state_manager.log_llm_request()"]
```

**Token Calculation Formula:**

```
prompt_tokens = sum(3 + len(tokenizer.encode(msg.content)) for msg in messages)
```

Each message has a 3-token overhead for role/structure, plus the encoded content length.

### Context Window Limits

Different LLM providers have different context window sizes:

| Provider | Typical Limit | Notes |
|----------|---------------|-------|
| OpenAI GPT-4 | 128K tokens | Some models support 1M tokens |
| Anthropic Claude | 200K tokens | Claude 3.5 Sonnet and later |
| Groq | 32K-128K | Varies by model |
| Azure OpenAI | 128K tokens | Matches OpenAI limits |

GPT Pilot's trim threshold of 150,000 tokens provides a safety margin for most models while allowing substantial context.

### LLMRequestLog Tracking

Each LLM interaction is logged with token usage:

```python
request_log = LLMRequestLog(
    provider=self.provider,
    model=self.config.model,
    temperature=temperature,
    prompts=convo.prompt_log,
    prompt_tokens=prompt_tokens,
    completion_tokens=completion_tokens,
    duration=t1 - t0,
    status=LLMRequestStatus.SUCCESS,
    response=response,
)
```

This data is stored via `state_manager.log_llm_request()` for analysis and debugging.

Sources:
- [core/llm/base.py:21-22]() (tokenizer initialization)
- [core/llm/base.py:167-186]() (token counting logic)
- [core/llm/base.py:160-165]() (LLMRequestLog creation)
- [core/llm/base.py:406-411]() (final logging)

## Integration with Agent Workflows

### Agent Usage Patterns

Multiple agents inherit from `RelevantFilesMixin` and call file filtering at different points in their workflows:

```mermaid
graph TB
    subgraph "TechLead Agent"
        TLRun["TechLead.run()"]
        TLRun --> TLPlan["plan_epic()"]
        TLPlan --> TLCheck{"source == 'feature'?"}
        TLCheck -- "Yes" --> TLRF["get_relevant_files_parallel()"]
        TLRF --> TLConvo["AgentConvo with filtered files"]
    end
    
    subgraph "Developer Agent"
        DevRun["Developer.run()"]
        DevRun --> DevBreak["breakdown_current_task()"]
        DevBreak --> DevRF["get_relevant_files_parallel()"]
        DevRF --> DevConvo["AgentConvo with filtered files"]
        
        DevRun --> DevIter["breakdown_current_iteration()"]
        DevIter --> DevCheck{"files exist?"}
        DevCheck -- "Yes" --> DevRF2["get_relevant_files_parallel()"]
        DevRF2 --> DevConvo2["AgentConvo with filtered files"]
    end
    
    subgraph "Troubleshooter Agent"
        TSRun["Troubleshooter.run()"]
        TSRun --> TSFeed["get_user_feedback()"]
        TSFeed --> TSBug{"Bug reported?"}
        TSBug -- "Yes" --> TSRF["get_relevant_files_parallel()"]
        TSRF --> TSConvo["AgentConvo with filtered files"]
    end
```

### Code References by Agent

| Agent | Method | Line Reference | Context |
|-------|--------|----------------|---------|
| TechLead | `plan_epic()` | [core/agents/tech_lead.py:301-302]() | Filters for new features |
| Developer | `breakdown_current_task()` | [core/agents/developer.py:224]() | Filters before task breakdown |
| Developer | `breakdown_current_iteration()` | [core/agents/developer.py:152-153]() | Filters for debugging iterations |
| Troubleshooter | `get_user_feedback()` | [core/agents/troubleshooter.py:321]() | Filters when change requested |
| Troubleshooter | `get_user_feedback()` | [core/agents/troubleshooter.py:339]() | Filters when bug reported |

### State Management

Filtered file paths are stored in both `current_state` and `next_state`:

```python
self.current_state.relevant_files = relevant_files
self.next_state.relevant_files = relevant_files
```

This ensures:
1. The current agent execution has access to filtered files
2. Future agents in the workflow can reference the same filtered list
3. State is preserved across state transitions

The `relevant_files` property can be reset to `None` to force re-filtering:

```python
self.next_state.relevant_files = None  # Force re-filtering on next run
```

Sources:
- [core/agents/tech_lead.py:296-318]()
- [core/agents/developer.py:204-224]()
- [core/agents/developer.py:121-202]()
- [core/agents/troubleshooter.py:244-346]()
- [core/agents/mixins.py:146-149]()

## Frontend and Backend Parallel Processing

### Directory Type Filtering

The `get_relevant_files()` method accepts a `dir_type` parameter that restricts filtering to specific directories:

```python
async def get_relevant_files(
    self,
    user_feedback: Optional[str] = None,
    solution_description: Optional[str] = None,
    dir_type: Optional[str] = None,  # "client" or "server"
) -> list[str]:
```

When `dir_type="client"`, the LLM is instructed to focus on frontend files. When `dir_type="server"`, it focuses on backend files.

### Parallel Execution

The `get_relevant_files_parallel()` method launches two async tasks simultaneously:

```python
tasks = [
    self.get_relevant_files(
        user_feedback=user_feedback,
        solution_description=solution_description,
        dir_type="client"
    ),
    self.get_relevant_files(
        user_feedback=user_feedback,
        solution_description=solution_description,
        dir_type="server"
    ),
]

responses = await asyncio.gather(*tasks)
relevant_files = [item for sublist in responses for item in sublist]
```

### Benefits of Parallel Processing

1. **Performance**: Two LLM calls execute concurrently, reducing total wait time
2. **Focus**: Each LLM call has a narrower scope (frontend OR backend)
3. **Token Efficiency**: Smaller prompts with fewer files to consider
4. **Separation of Concerns**: Frontend and backend files are evaluated independently

### Full-Stack File Relationships

```mermaid
graph TB
    Client["client/ directory"]
    Server["server/ directory"]
    
    Client --> FEAPI["API client files"]
    Client --> FEUI["UI component files"]
    Client --> FEUtils["Frontend utilities"]
    
    Server --> BEAPI["API route handlers"]
    Server --> BEModels["Database models"]
    Server --> BEUtils["Backend utilities"]
    
    FEAPI -.->|"HTTP requests"| BEAPI
    FEUI -.->|"calls"| FEAPI
    BEAPI -.->|"uses"| BEModels
    
    FEAPI --> Relevant["relevant_files list"]
    FEUI --> Relevant
    BEAPI --> Relevant
    BEModels --> Relevant
```

Both frontend and backend files are merged into a single `relevant_files` list after parallel filtering completes.

Sources:
- [core/agents/mixins.py:130-151]()
- [core/agents/mixins.py:153-158]()
- [core/agents/mixins.py:142-144]()

## Best Practices

To ensure effective file filtering, GPT Pilot implements these best practices:

1. **Be inclusive rather than exclusive**: It's better to include a potentially relevant file than to miss an important one
2. **Read before adding**: Always examine a file's content before determining its relevance
3. **Consider interactions**: Files that interact with each other are often relevant together
4. **Focus on the task**: Always relate file relevance to the specific task requirements
5. **Read as many files as possible**: The system encourages reading up to 20 files at once before making filtering decisions

Sources:
- [core/prompts/partials/filter_files_actions.prompt:17-20]()
- [core/prompts/developer/filter_files.prompt:34-36]()

## Conclusion

File filtering and relevance determination is a fundamental process in GPT Pilot's workflow. By carefully selecting which files are relevant to a task, GPT Pilot provides focused context to its agents, enabling them to generate appropriate code modifications and implementations.

The iterative nature of the filtering process allows agents to gradually build a comprehensive understanding of the relevant parts of the codebase, ensuring they have the necessary context to complete tasks successfully while staying within the context limitations of LLMs.

---

# Page: User Testing and Feedback Loop

# User Testing and Feedback Loop

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [core/agents/bug_hunter.py](core/agents/bug_hunter.py)
- [core/agents/developer.py](core/agents/developer.py)
- [core/agents/legacy_handler.py](core/agents/legacy_handler.py)
- [core/agents/mixins.py](core/agents/mixins.py)
- [core/agents/tech_lead.py](core/agents/tech_lead.py)
- [core/agents/troubleshooter.py](core/agents/troubleshooter.py)
- [core/db/migrations/versions/f708791b9270_adding_knowledge_base_field_to_.py](core/db/migrations/versions/f708791b9270_adding_knowledge_base_field_to_.py)
- [core/prompts/troubleshooter/define_user_review_goal.prompt](core/prompts/troubleshooter/define_user_review_goal.prompt)
- [core/prompts/troubleshooter/get_route_files.prompt](core/prompts/troubleshooter/get_route_files.prompt)

</details>



This document describes how GPT Pilot manages the iterative testing and feedback cycle during development. After code is generated for a task, the system enters a feedback loop where users test the application, report issues or request changes, and the system responds by fixing bugs or implementing modifications. This process continues until the user confirms the task is complete.

For information about how tasks are broken down and implemented initially, see [Implementation Agents](#4.3). For details on the bug hunting strategies used during feedback cycles, see [Quality Assurance Agents](#4.5).

## Overview

The user testing and feedback loop is managed primarily by two agents:

| Agent | Primary Responsibility |
|-------|----------------------|
| `Troubleshooter` | Generates test instructions, collects user feedback, routes to appropriate handler |
| `BugHunter` | Investigates bugs, adds logging, implements fixes, manages pair programming sessions |

The loop operates as follows:

1. **Test Instruction Generation**: Troubleshooter creates step-by-step testing instructions
2. **User Testing**: User follows instructions and provides feedback
3. **Feedback Classification**: System determines if feedback is a bug, change request, or confirmation
4. **Iteration Creation**: New iteration is created with appropriate status
5. **Solution Implementation**: Developer breaks down solution into executable steps
6. **Verification**: Process repeats until user confirms task is complete

Sources: [core/agents/troubleshooter.py:1-435](), [core/agents/bug_hunter.py:1-412]()

## Test Instruction Generation

### TestSteps Model

The system uses structured test instructions defined by the `TestSteps` Pydantic model:

```python
class Test(BaseModel):
    title: str  # Short title of test step
    action: str  # Detailed actions to take
    result: str  # Expected result
    
class TestSteps(BaseModel):
    steps: List[Test]
```

Sources: [core/agents/mixins.py:27-34]()

### Automatic Test Generation

```mermaid
graph TB
    CurrentTask["current_task"] --> CheckInstructions{test_instructions<br/>exists?}
    
    CheckInstructions -->|No| GetRoutes["_get_route_files()<br/>Find route definition files"]
    CheckInstructions -->|Yes| SendToUser["send_test_instructions()"]
    
    GetRoutes --> LLMPrompt["define_user_review_goal.prompt<br/>Generate test steps"]
    LLMPrompt --> ParseSteps["JSONParser(TestSteps)<br/>Parse structured output"]
    
    ParseSteps --> CheckEmpty{steps list<br/>empty?}
    CheckEmpty -->|Yes| CompleteTask["complete_task()<br/>No testing needed"]
    CheckEmpty -->|No| SaveInstructions["current_task['test_instructions']<br/>Store for reuse"]
    
    SaveInstructions --> SendToUser
    SendToUser --> UserTesting["User follows instructions"]
    
    style LLMPrompt fill:#f9f9f9
    style ParseSteps fill:#f9f9f9
```

**Test Generation Process**

The `Troubleshooter.get_user_instructions()` method generates test steps:

1. **Route File Identification**: Uses `get_route_files.prompt` to find files containing route definitions
2. **Context Assembly**: Gathers implemented tasks, current task, and pending tasks
3. **LLM Generation**: Prompts LLM with comprehensive rules for creating actionable test steps
4. **Validation**: Checks if test steps are needed (some tasks require no user testing)

Sources: [core/agents/troubleshooter.py:203-231](), [core/prompts/troubleshooter/define_user_review_goal.prompt:1-83]()

### Test Instruction Rules

The `define_user_review_goal.prompt` enforces strict rules for test generation:

| Rule Category | Requirements |
|--------------|-------------|
| **Specificity** | Actions must be explicit with no ambiguity |
| **Testing Method** | Prefer browser testing over API tools; use full cURL commands if API testing required |
| **No Coding** | User should never need to write code or edit files |
| **Environment** | Commands must match user's OS; assume services (DB, etc.) are running |
| **Completeness** | URLs must be fully specified (e.g., `http://localhost:5173/form`, not `/form`) |
| **State Awareness** | Only test features already implemented; account for what's not yet available |

Sources: [core/prompts/troubleshooter/define_user_review_goal.prompt:5-82]()

### Run Command Detection

Before testing, the system determines how to start the application:

```mermaid
graph LR
    CheckCommand{run_command<br/>exists?} -->|No| DetectCommand["get_run_command()<br/>LLM analyzes task instructions"]
    CheckCommand -->|Yes| UseExisting["Use existing command"]
    
    DetectCommand --> ParseOutput["OptionalCodeBlockParser<br/>Remove markdown artifacts"]
    ParseOutput --> ValidateLength{Length >= 5?}
    ValidateLength -->|Yes| SaveCommand["next_state.run_command"]
    ValidateLength -->|No| EmptyCommand["Set to empty string"]
    
    SaveCommand --> UseExisting
    EmptyCommand --> UseExisting
    UseExisting --> SendToUI["send_run_command()"]
```

Sources: [core/agents/troubleshooter.py:187-201]()

## User Feedback Collection

### Feedback Classification Flow

```mermaid
stateDiagram-v2
    [*] --> AwaitingFeedback: send_test_instructions()
    
    AwaitingFeedback --> ButtonChoice: ask_question(TS_APP_WORKING)
    
    ButtonChoice --> Continue: "Everything works"
    ButtonChoice --> Bug: "There is an issue"
    ButtonChoice --> Change: "I want to make a change"
    ButtonChoice --> Redo: "Redo task"
    
    Continue --> CompleteTask: complete_task()
    CompleteTask --> [*]
    
    Redo --> AskRedoInfo: Request more details
    AskRedoInfo --> SetRedoFlag: current_task["redo_human_instructions"]
    SetRedoFlag --> [*]
    
    Bug --> DescribeIssue: TS_DESCRIBE_ISSUE
    DescribeIssue --> GetRelevantFiles: get_relevant_files_parallel()
    GetRelevantFiles --> CreateIteration: status=HUNTING_FOR_BUG
    
    Change --> DescribeChange: "Describe the change"
    DescribeChange --> GetRelevantFiles2: get_relevant_files_parallel()
    GetRelevantFiles2 --> CreateIteration2: status=NEW_FEATURE_REQUESTED
    
    CreateIteration --> [*]
    CreateIteration2 --> [*]
    
    note right of ButtonChoice
        ProjectStage.GET_USER_FEEDBACK
        Collect logs if "collect_logs" flag set
    end note
```

**Button Options**

The `get_user_feedback()` method presents context-aware buttons:

- **continue**: Task works as expected
- **bug**: There's a problem to fix
- **change**: User wants to modify functionality
- **redo**: Start the task over (not available for hardcoded tasks)

Sources: [core/agents/troubleshooter.py:244-346]()

### Iteration Status Types

When feedback is collected, the system creates an iteration with a specific status:

```python
class IterationStatus(str, Enum):
    HUNTING_FOR_BUG = "hunting_for_bug"
    AWAITING_USER_TEST = "awaiting_user_test"
    AWAITING_BUG_REPRODUCTION = "awaiting_bug_reproduction"
    START_PAIR_PROGRAMMING = "start_pair_programming"
    AWAITING_BUG_FIX = "awaiting_bug_fix"
    AWAITING_LOGGING = "awaiting_logging"
    FIND_SOLUTION = "find_solution"
    IMPLEMENT_SOLUTION = "implement_solution"
    NEW_FEATURE_REQUESTED = "new_feature_requested"
    PROBLEM_SOLVER = "problem_solver"
```

Sources: [core/db/models/project_state.py]() (referenced in imports)

### Iteration Data Structure

Each iteration contains:

```python
{
    "id": uuid4().hex,
    "user_feedback": str,  # User's description of issue/change
    "user_feedback_qa": list[str],  # Additional Q&A (optional)
    "description": str,  # LLM-generated solution description
    "alternative_solutions": list,  # For loop detection
    "attempts": int,  # Number of fix attempts
    "status": IterationStatus,
    "bug_hunting_cycles": list[dict],  # Logging/fix attempts
    "bug_reproduction_description": str  # JSON TestSteps for reproduction
}
```

Sources: [core/agents/troubleshooter.py:127-141]()

## Bug Hunting Cycle

### Bug Reproduction Instructions

When a bug is reported, the system asynchronously generates reproduction steps:

```mermaid
graph TB
    ReportBug["User reports bug"] --> CheckReproduction{bug_reproduction_description<br/>exists?}
    
    CheckReproduction -->|No| StartAsync["asyncio.create_task()<br/>get_bug_reproduction_instructions()"]
    CheckReproduction -->|Yes| HuntingStatus{current_iteration<br/>status?}
    
    StartAsync --> LLMGenerate["get_bug_reproduction_instructions.prompt<br/>Generate TestSteps"]
    LLMGenerate --> SaveSteps["Store as JSON in iteration"]
    SaveSteps --> HuntingStatus
    
    HuntingStatus -->|HUNTING_FOR_BUG| CheckLogs["check_logs()"]
    HuntingStatus -->|AWAITING_USER_TEST| AskUserTest["ask_user_to_test()<br/>awaiting_user_test=True"]
    HuntingStatus -->|AWAITING_BUG_REPRODUCTION| AskUserTest2["ask_user_to_test()<br/>awaiting_bug_reproduction=True"]
    HuntingStatus -->|START_PAIR_PROGRAMMING| StartPair["start_pair_programming()"]
    
    CheckLogs --> HuntConclusion["bug_found_or_add_logs.prompt<br/>ADD_LOGS or PROBLEM_IDENTIFIED?"]
    
    HuntConclusion -->|ADD_LOGS| SetLogging["status=AWAITING_LOGGING<br/>Developer adds log statements"]
    HuntConclusion -->|PROBLEM_IDENTIFIED| SetBugFix["status=AWAITING_BUG_FIX<br/>Developer implements fix"]
    
    SetLogging --> DeveloperBreakdown["Developer.breakdown_current_iteration()"]
    SetBugFix --> DeveloperBreakdown
    
    DeveloperBreakdown --> CodeMonkey["CodeMonkey implements steps"]
    CodeMonkey --> AskUserTest
    
    AskUserTest --> UserTests["User follows reproduction steps"]
    AskUserTest2 --> UserTests
    
    UserTests --> IsFixed{"Is bug fixed?"}
    IsFixed -->|Yes| CompleteIteration["complete_iteration()"]
    IsFixed -->|No| MoreFeedback["Additional feedback"]
    IsFixed -->|Pair Program| StartPair
    
    MoreFeedback --> CheckLogs
    CompleteIteration --> NextTask["Continue with next task"]
    
    style LLMGenerate fill:#f9f9f9
    style HuntConclusion fill:#f9f9f9
```

Sources: [core/agents/bug_hunter.py:61-80](), [core/agents/bug_hunter.py:82-101](), [core/agents/bug_hunter.py:103-142]()

### Hunt Conclusion Decision

The `check_logs()` method generates a human-readable debugging plan and determines next steps:

1. **Generate Instructions**: Uses LLM to analyze logs and user feedback
2. **Chat with Breakdown**: Allows user to provide input via `chat_with_breakdown()`
3. **Classify Conclusion**: Determines if more logs are needed or if problem is identified
4. **Set Status**: Updates iteration status to `AWAITING_LOGGING` or `AWAITING_BUG_FIX`
5. **UI Notification**: Sends bug hunter status to UI

Sources: [core/agents/bug_hunter.py:103-142]()

### Bug Hunting Cycles

Each bug hunting cycle tracks:

```python
{
    "human_readable_instructions": str,  # What to do
    "backend_logs": str | None,  # Backend log output
    "frontend_logs": str | None,  # Frontend log output
    "user_feedback": str,  # Additional user feedback
    "fix_attempted": bool  # Whether a fix was tried
}
```

Multiple cycles may be needed if initial logging is insufficient.

Sources: [core/agents/bug_hunter.py:400-409]()

## Pair Programming Mode

### Interactive Debugging Session

When automated debugging fails, the system offers interactive pair programming:

```mermaid
graph TB
    StartPair["start_pair_programming()"] --> GenerateExplanation["problem_explanation.prompt<br/>LLM explains issue"]
    
    GenerateExplanation --> IdentifyLogs["data_about_logs.prompt<br/>ImportantLogsForDebugging"]
    IdentifyLogs --> SendLogs["send_data_about_logs()<br/>Show to user"]
    
    SendLogs --> AskChoice["What do you want to do?"]
    
    AskChoice --> Question["question:<br/>I have a question"]
    AskChoice --> Done["done:<br/>I fixed the bug myself"]
    AskChoice --> TellMore["tell_me_more:<br/>Tell me more about the bug"]
    AskChoice --> Hint["solution_hint:<br/>I think I know where the problem is"]
    AskChoice --> Other["other:<br/>Other"]
    
    Question --> AskQuestion["ask_a_question.prompt<br/>Answer user question"]
    AskQuestion --> AskChoice
    
    TellMore --> TellMorePrompt["tell_me_more.prompt<br/>More detailed explanation"]
    TellMorePrompt --> AskChoice
    
    Other --> AskOther["User describes their thought"]
    AskOther --> AskQuestion
    
    Hint --> GetHint["User describes solution idea"]
    GetHint --> GenerateInstructions["instructions_from_human_hint.prompt<br/>Convert to implementation plan"]
    GenerateInstructions --> UserApproval{"User approves?"}
    
    UserApproval -->|Yes| SetBugFix["status=AWAITING_BUG_FIX<br/>bug_hunting_cycles.append()"]
    UserApproval -->|No| AskAgain["What did I misunderstand?"]
    AskAgain --> GetHint
    
    SetBugFix --> Done
    Done --> CompleteIteration["complete_iteration()"]
    
    style GenerateExplanation fill:#f9f9f9
    style IdentifyLogs fill:#f9f9f9
    style GenerateInstructions fill:#f9f9f9
```

**Important Logs Data Structure**

The system identifies critical log statements for debugging:

```python
class ImportantLog(BaseModel):
    logCode: str  # Actual logging code
    shouldBeDifferent: bool  # If current != expected
    filePath: str  # Where the log exists
    currentOutput: str  # What it currently shows
    expectedOutput: str  # What it should show
    explanation: str  # Why this log matters
```

Sources: [core/agents/bug_hunter.py:241-361](), [core/agents/bug_hunter.py:42-55]()

## Loop Detection

### Iteration Threshold

The system detects when it's stuck in a loop:

```python
LOOP_THRESHOLD = 3  # Number of iterations to trigger loop detection
```

When `len(iterations) == LOOP_THRESHOLD`, the system:
1. Traces telemetry event: `loop-start`
2. Sets iteration status to `PROBLEM_SOLVER`
3. Generates alternative solutions

Sources: [core/agents/troubleshooter.py:22](), [core/agents/troubleshooter.py:143-145]()

### Alternative Solution Handling

```mermaid
stateDiagram-v2
    [*] --> CheckIterations: User reports issue
    
    CheckIterations --> IsLoop: len(iterations) >= 3?
    IsLoop --> CheckAlternatives: Has alternative_solutions?
    
    CheckAlternatives --> TryNext: Yes, alternatives exist
    CheckAlternatives --> GenerateNew: No, first loop detection
    
    TryNext --> SetProblemSolver: status=PROBLEM_SOLVER
    GenerateNew --> SetProblemSolver
    
    SetProblemSolver --> ProblemSolver: ProblemSolver agent
    ProblemSolver --> Implement: Developer implements
    Implement --> Test: User tests
    
    Test --> Fixed: Works
    Test --> StillLooping: Still broken
    
    Fixed --> [*]
    StillLooping --> TryNext
    
    note right of CheckIterations
        LOOP_THRESHOLD = 3
        Telemetry: loop-start, loop-feedback, loop-end
    end note
```

Sources: [core/agents/troubleshooter.py:112-119](), [core/agents/troubleshooter.py:348-366](), [core/agents/troubleshooter.py:426-434]()

## Developer Iteration Breakdown

### Processing Iterations

The `Developer` agent converts iterations back into executable steps:

```mermaid
graph TB
    UnfinishedIter["unfinished_iterations exists"] --> CheckStatus{iteration status?}
    
    CheckStatus -->|AWAITING_BUG_FIX| BugFixBreakdown["bug_hunting_cycles[-1]<br/>human_readable_instructions"]
    CheckStatus -->|AWAITING_LOGGING| LogBreakdown["bug_hunting_cycles[-1]<br/>human_readable_instructions"]
    CheckStatus -->|IMPLEMENT_SOLUTION| SolutionBreakdown["iteration description"]
    
    BugFixBreakdown --> GetRelevant["get_relevant_files_parallel()"]
    LogBreakdown --> GetRelevant
    SolutionBreakdown --> GetRelevant
    
    GetRelevant --> ParseTask["parse_task.prompt<br/>Generate TaskSteps"]
    ParseTask --> SetSteps["set_next_steps()<br/>Add to state.steps"]
    
    SetSteps --> UpdateStatus{Status?}
    UpdateStatus -->|BUG_FIX| AwaitUserTest["status=AWAITING_USER_TEST"]
    UpdateStatus -->|LOGGING| AwaitRepro["status=AWAITING_BUG_REPRODUCTION"]
    UpdateStatus -->|IMPLEMENT| CompleteIter["complete_iteration()"]
    
    AwaitUserTest --> Done["AgentResponse.done()"]
    AwaitRepro --> Done
    CompleteIter --> Done
    
    style ParseTask fill:#f9f9f9
```

Sources: [core/agents/developer.py:121-202]()

### Step Type Mapping

The `parse_task.prompt` converts iteration descriptions into structured steps:

| Step Type | Description | Usage |
|-----------|-------------|-------|
| `save_file` | File modification | Code changes |
| `command` | Shell command | DB migrations, npm install |
| `human_intervention` | Manual action | User must perform something |
| `utility_function` | Mocked function | Placeholder for future implementation |

Sources: [core/agents/developer.py:32-77]()

## Task Completion

### Completion Flow

```mermaid
graph LR
    UserTest["User tests"] --> Feedback{Feedback?}
    
    Feedback -->|"Everything works"| CompleteTask["Troubleshooter.complete_task()"]
    Feedback -->|Issue/Change| CreateIteration["Create new iteration"]
    
    CompleteTask --> CheckLoop{iterations >= 3?}
    CheckLoop -->|Yes| TraceLoopEnd["telemetry.trace_loop('loop-end')"]
    CheckLoop -->|No| SetReviewed
    
    TraceLoopEnd --> SetReviewed["status=TaskStatus.REVIEWED<br/>action=TS_TASK_REVIEWED"]
    SetReviewed --> NextAgent["TechnicalWriter or TechLead"]
    
    CreateIteration --> Developer["Developer breaks down iteration"]
    Developer --> CodeMonkey["CodeMonkey implements"]
    CodeMonkey --> UserTest
    
    style CompleteTask fill:#e6f3ff
```

**TaskStatus Transitions**

During the feedback loop:
- `TODO` → `IN_PROGRESS` (when Developer starts task breakdown)
- `IN_PROGRESS` → `REVIEWED` (when Troubleshooter confirms completion)
- `REVIEWED` → next stage (documentation or next task)

Sources: [core/agents/troubleshooter.py:148-159]()

## UI Communication

### Project Stage Updates

The system sends stage updates to keep the UI synchronized:

| Stage | Constant | When Triggered |
|-------|----------|---------------|
| Test App | `ProjectStage.TEST_APP` | Before showing test instructions |
| Get Feedback | `ProjectStage.GET_USER_FEEDBACK` | Waiting for user's "works/bug/change" decision |
| Describe Issue | `ProjectStage.DESCRIBE_ISSUE` | User clicked "There is an issue" |
| Describe Change | `ProjectStage.DESCRIBE_CHANGE` | User clicked "I want to make a change" |
| Additional Feedback | `ProjectStage.ADDITIONAL_FEEDBACK` | Collecting logs after bug reproduction |
| Breakdown Chat | `ProjectStage.BREAKDOWN_CHAT` | LLM solution can be refined by user |

Sources: [core/agents/troubleshooter.py:78-79](), [core/agents/troubleshooter.py:277](), [core/agents/troubleshooter.py:313](), [core/agents/troubleshooter.py:325](), [core/agents/bug_hunter.py:204-208]()

### Test Instruction Display

Test instructions are sent with special formatting:

```python
await self.ui.send_test_instructions(
    user_instructions,  # JSON string of TestSteps
    project_state_id=str(self.current_state.id)
)
```

The VSCode extension displays these in a structured, interactive format.

Sources: [core/agents/troubleshooter.py:81](), [core/agents/bug_hunter.py:160]()

### Bug Hunter Status Indicators

The UI shows real-time bug hunting progress:

```python
await self.ui.send_bug_hunter_status(
    "adding_logs",  # or "fixing_bug", "close_status"
    num_bug_hunting_cycles
)
```

Sources: [core/agents/bug_hunter.py:73](), [core/agents/bug_hunter.py:76](), [core/agents/bug_hunter.py:79](), [core/agents/bug_hunter.py:133](), [core/agents/bug_hunter.py:138]()

## Integration Points

### State Management

Iterations are stored in `ProjectState.iterations` as a list:

```python
self.next_state.iterations = self.current_state.iterations + [new_iteration]
self.next_state.flag_iterations_as_modified()
```

The `flag_iterations_as_modified()` method ensures SQLAlchemy persists changes.

Sources: [core/agents/troubleshooter.py:141-142]()

### Relevant Files Filtering

Before processing user feedback, the system identifies relevant files:

```python
await self.get_relevant_files_parallel(
    user_feedback=bug_report  # or change_description
)
```

This ensures the LLM context includes only files related to the reported issue.

Sources: [core/agents/troubleshooter.py:321](), [core/agents/troubleshooter.py:339](), [core/agents/developer.py:153]()

### Task State Preservation

When quick tasks are added after completion:

```python
# Load previous state before tasks were deleted
wanted_project_state = await self.state_manager.get_project_state_by_id(
    self.current_state.prev_state_id
)
# Restore task list with new task appended
self.next_state.tasks = wanted_project_state.tasks + [new_task]
```

Sources: [core/agents/tech_lead.py:225-249]()

## Best Practices

### Test Instruction Quality

To ensure effective user testing:

1. **Be Specific**: URLs must be complete (`http://localhost:3000/api/users`, not `/api/users`)
2. **Match OS**: Commands must work on user's operating system
3. **Assume Running Services**: Don't ask user to start databases or dependencies
4. **No Code Required**: User should never need to edit files to test
5. **State Awareness**: Only test features that are already implemented

Sources: [core/prompts/troubleshooter/define_user_review_goal.prompt:5-20]()

### Feedback Loop Efficiency

The system optimizes feedback cycles by:

1. **Async Reproduction Steps**: Bug reproduction instructions are generated in parallel while other processing occurs
2. **Relevant File Filtering**: Only loads files related to the issue into LLM context
3. **Loop Detection**: Switches to alternative solution strategies after 3 iterations
4. **Pair Programming Fallback**: Offers interactive debugging when automated approaches fail

Sources: [core/agents/bug_hunter.py:65-67](), [core/agents/troubleshooter.py:143-145]()

### Telemetry Tracking

The system traces loop events for analytics:

```python
await telemetry.trace_loop(
    "loop-start",  # or "loop-feedback", "loop-end"
    {
        "task_description": task["description"],
        "task_number": num_completed_tasks + 1,
        "steps": len(steps),
        "iterations": len(iterations)
    }
)
```

Sources: [core/agents/troubleshooter.py:426-434]()

---

# Page: Project Templates

# Project Templates

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [core/prompts/frontend/build_frontend.prompt](core/prompts/frontend/build_frontend.prompt)
- [core/prompts/frontend/system.prompt](core/prompts/frontend/system.prompt)
- [core/prompts/partials/project_details.prompt](core/prompts/partials/project_details.prompt)
- [core/templates/registry.py](core/templates/registry.py)
- [core/templates/tree/vite_react/client/src/components/Header.tsx](core/templates/tree/vite_react/client/src/components/Header.tsx)
- [core/templates/tree/vite_react/client/src/components/ui/theme-provider.tsx](core/templates/tree/vite_react/client/src/components/ui/theme-provider.tsx)
- [core/templates/tree/vite_react/client/src/components/ui/theme-toggle.tsx](core/templates/tree/vite_react/client/src/components/ui/theme-toggle.tsx)
- [core/templates/vite_react.py](core/templates/vite_react.py)
- [tests/agents/test_tech_lead.py](tests/agents/test_tech_lead.py)
- [tests/templates/test_templates.py](tests/templates/test_templates.py)

</details>



## Purpose and Overview

Project Templates in GPT Pilot provide pre-configured starting points for new software projects. They establish initial file structures, dependencies, and configurations based on common technology stacks, enabling developers to bypass repetitive setup tasks. Templates are a core component of the State Management system (see [State Management](#2.2)) and work closely with the agent system to provide context about the codebase structure.

```mermaid
graph TD
    subgraph "Project Templates System"
        Registry["Registry"]
        Templates["Template Classes"]
        Options["Template Options"]
    end
    
    subgraph "State Management System"
        StateManager["StateManager"]
        FileSystem["File System"]
    end
    
    Registry -- "provides access to" --> Templates
    Templates -- "include" --> Options
    Templates -- "apply to" --> FileSystem
    StateManager -- "uses" --> Templates
    StateManager -- "manages" --> FileSystem
```

Sources: [core/templates/registry.py:1-29]()

## Template Registry

The template system is built around a registry pattern that maps template names to template classes. This allows the system to dynamically select and instantiate the appropriate template based on project requirements.

```mermaid
classDiagram
    class ProjectTemplateEnum {
        <<enum>>
        VITE_REACT
    }
    
    class PROJECT_TEMPLATES {
        <<dictionary>>
        +ViteReactProjectTemplate.name: ViteReactProjectTemplate
    }
    
    ProjectTemplateEnum -- PROJECT_TEMPLATES: references
```

Currently, the following templates are registered in the system, though only Vite React is fully active:

| Template Name | Status | Purpose |
|---------------|--------|---------|
| ViteReact | Active | React frontend application using Vite build tool |
| JavascriptReact | Commented out | React application with classic setup |
| NodeExpressMongoose | Commented out | Node.js backend with Express and MongoDB |
| ReactExpress | Commented out | Full-stack JS app with React frontend and Express backend |

Sources: [core/templates/registry.py:14-28]()

## Template Application Process

When a new project is created in GPT Pilot, the selected template is applied to establish the initial project structure. The template application process follows these steps:

```mermaid
sequenceDiagram
    participant User
    participant SM as "StateManager"
    participant TR as "Template Registry"
    participant TemplateClass
    participant FS as "File System"
    
    User->>SM: create_project("ProjectName")
    SM->>SM: commit()
    User->>TR: Select template
    TR->>TemplateClass: Get TemplateClass
    TemplateClass->>TemplateClass: Initialize with options
    TemplateClass->>FS: apply()
    FS->>SM: Create initial file structure
    SM->>User: Return initialized project
```

The template application process creates the initial file structure in the project's workspace. This establishes the foundation upon which the agents will build when implementing the application.

Sources: [tests/templates/test_templates.py:9-35](), [tests/templates/test_templates.py:60-81]()

## Template Options

Templates can be customized with options that affect what files are generated and what dependencies are included. These options are passed during template initialization and affect the final project structure.

```mermaid
classDiagram
    class BaseTemplate {
        <<abstract>>
        +name: string
        +options_class: Class
        +options_dict: dict
        +apply(): void
    }
    
    class ViteReactProjectTemplate {
        +name: "vite_react"
        +apply(): void
    }
    
    class ReactExpressTemplate {
        +name: "react_express"
        +options_class: Class
        +apply(): void
    }
    
    BaseTemplate <|-- ViteReactProjectTemplate
    BaseTemplate <|-- ReactExpressTemplate
    
    class TemplateOptions {
        <<abstract>>
        +to_dict(): dict
    }
    
    class ReactExpressOptions {
        +db_type: "sql"|"nosql"
        +auth: boolean
    }
    
    TemplateOptions <|-- ReactExpressOptions
    ReactExpressTemplate -- ReactExpressOptions: uses
```

Different templates support different options. For example, the React Express template supports options for database type (`sql` or `nosql`) and authentication features:

| Template | Options | Description |
|----------|---------|-------------|
| ReactExpress | `db_type: "sql"` | Uses Prisma ORM with SQL database |
| ReactExpress | `db_type: "nosql"` | Uses Mongoose with MongoDB |
| ReactExpress | `auth: true` | Includes authentication routes and components |

Sources: [tests/templates/test_templates.py:19-24](), [tests/templates/test_templates.py:45-49]()

## Template Integration with Prompts

Templates provide project knowledge that is integrated into the agent prompts. When a template is applied, it can generate a summary that describes the codebase structure, which is then included in prompts to provide context to the LLM agents.

```mermaid
flowchart LR
    Template["Template"] -- "generates" --> Summary["Template Summary"]
    Summary -- "stored in" --> State["Project State"]
    State -- "included in" --> Prompts["Agent Prompts"]
    Prompts -- "guide" --> Agents["LLM Agents"]
```

This integration allows agents to understand the initial structure of the codebase and make appropriate decisions when generating new code.

Sources: [core/prompts/partials/project_details.prompt:7-11]()

## Vite React Template

The Vite React template is currently the primary active template in GPT Pilot. It sets up a modern React application using Vite as the build tool, providing a fast development experience.

### File Structure

When applied, the Vite React template creates a structure similar to:

```
/
├── public/
│   └── assets/
├── src/
│   ├── components/
│   ├── pages/
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── package.json
├── vite.config.js
└── index.html
```

This structure follows modern React application conventions, making it easy for developers to navigate and extend.

Sources: [core/templates/registry.py:7](), [core/templates/registry.py:19-26]()

## Creating Custom Templates

While not explicitly documented in the provided files, the template system is designed to be extensible. New templates can be created by:

1. Creating a new template class that implements the expected interface
2. Adding the template to the registry
3. Adding the template to the `ProjectTemplateEnum`

Custom templates should follow the pattern established by existing templates, implementing an `apply()` method that creates the necessary file structure and configurations.

Sources: [core/templates/registry.py:5-9](), [core/templates/registry.py:17-20](), [core/templates/registry.py:23-27]()

---

# Page: Template Architecture

# Template Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [core/agents/architect.py](core/agents/architect.py)
- [core/agents/frontend.py](core/agents/frontend.py)
- [core/agents/orchestrator.py](core/agents/orchestrator.py)
- [core/agents/spec_writer.py](core/agents/spec_writer.py)
- [core/prompts/partials/project_details.prompt](core/prompts/partials/project_details.prompt)
- [core/templates/registry.py](core/templates/registry.py)
- [tests/agents/test_tech_lead.py](tests/agents/test_tech_lead.py)
- [tests/templates/test_templates.py](tests/templates/test_templates.py)

</details>



## Purpose and Scope

This document describes the template system used for project scaffolding in GPT Pilot. The template architecture provides pre-configured project structures that accelerate initial code generation by providing starter files, configurations, and boilerplate code. This page focuses on the registry, base architecture, and lifecycle of templates. For details on specific template implementations (Vite React, Vite React Swagger), see [7.2](#7.2).

---

## Template Registry System

### ProjectTemplateEnum

The available templates are defined in `ProjectTemplateEnum`, which serves as a centralized catalog of template choices that can be passed to the LLM for selection.

```python
class ProjectTemplateEnum(str, Enum):
    VITE_REACT = ViteReactProjectTemplate.name
```

**Sources:** [core/templates/registry.py:15-22]()

### PROJECT_TEMPLATES Dictionary

The `PROJECT_TEMPLATES` dictionary maps template names (strings) to their implementation classes. This registry is used throughout the system to instantiate templates dynamically.

```mermaid
graph LR
    Registry["PROJECT_TEMPLATES<br/>(dict)"]
    VRKey["'vite_react'<br/>(string key)"]
    VRClass["ViteReactProjectTemplate<br/>(class)"]
    VRSKey["'vite_react_swagger'<br/>(string key)"]
    VRSClass["ViteReactSwaggerProjectTemplate<br/>(class)"]
    
    Registry --> VRKey
    Registry --> VRSKey
    VRKey --> VRClass
    VRSKey --> VRSClass
    
    VRClass --> Instance1["template instance"]
    VRSClass --> Instance2["template instance"]
```

**Template Registry Structure**

| Template Name | Class | Purpose |
|--------------|-------|---------|
| `vite_react` | `ViteReactProjectTemplate` | Full-stack Vite + React application with authentication |
| `vite_react_swagger` | `ViteReactSwaggerProjectTemplate` | Frontend-only Vite + React with external API integration |

**Sources:** [core/templates/registry.py:24-30]()

---

## Template Lifecycle

### Selection Phase (Architect Agent)

The `Architect` agent selects appropriate templates based on the project specification using LLM-based reasoning.

```mermaid
stateDiagram-v2
    [*] --> select_templates
    select_templates --> TemplateSelection: "LLM analyzes spec"
    
    state TemplateSelection {
        [*] --> CreateConvo: "AgentConvo with<br/>select_templates prompt"
        CreateConvo --> LLMCall: "require_schema(TemplateSelection)"
        LLMCall --> ParseResponse: "JSONParser"
        ParseResponse --> [*]: "TemplateSelection object"
    }
    
    TemplateSelection --> CheckTemplate: "tpl.template value"
    CheckTemplate --> NoTemplate: "None"
    CheckTemplate --> ConfigureTemplate: "ProjectTemplateEnum"
    
    ConfigureTemplate --> configure_template: "template_class.options_class"
    configure_template --> LLMOptions: "LLM fills options"
    LLMOptions --> Instantiate: "template_class(options, sm, pm)"
    
    NoTemplate --> [*]: "empty templates dict"
    Instantiate --> [*]: "populated templates dict"
```

**TemplateSelection Response Schema**

The LLM returns this structured response when selecting templates:

```python
class TemplateSelection(BaseModel):
    architecture: str  # General architecture description
    template: Optional[ProjectTemplateEnum]  # Selected template or None
```

**Sources:** [core/agents/architect.py:84-93](), [core/agents/architect.py:124-171]()

### Configuration Phase

For templates with configurable options, the `configure_template()` method uses the LLM to fill in appropriate values based on the project specification.

```mermaid
graph TB
    Start["configure_template(spec, template_class)"]
    CheckOptions{"template_class.options_class<br/>is NoOptions?"}
    
    Start --> CheckOptions
    CheckOptions -->|Yes| ReturnEmpty["return NoOptions()"]
    CheckOptions -->|No| CreateConvo["AgentConvo.template<br/>('configure_template')"]
    
    CreateConvo --> RequireSchema["convo.require_schema<br/>(options_class)"]
    RequireSchema --> LLMCall["await llm(convo,<br/>parser=JSONParser)"]
    LLMCall --> ReturnOptions["return configured<br/>options model"]
    
    ReturnEmpty --> End[End]
    ReturnOptions --> End
```

**Sources:** [core/agents/architect.py:268-294]()

### Application Phase (SpecWriter Agent)

The `SpecWriter` agent applies the selected template through its `apply_template()` method.

```mermaid
sequenceDiagram
    participant SW as SpecWriter
    participant KB as KnowledgeBase
    participant Template as ProjectTemplate
    participant SM as StateManager
    participant PM as ProcessManager
    
    SW->>KB: Get user_options['auth_type']
    KB-->>SW: auth_type value
    
    SW->>SW: Determine template_name<br/>('vite_react_swagger' or 'vite_react')
    SW->>PROJECT_TEMPLATES: Get template_class
    
    SW->>Template: Instantiate(options, sm, pm)
    Template-->>SW: template instance
    
    SW->>SM: Store in state_manager.template
    SW->>Template: await template.apply()
    Template->>SM: Save files to VFS
    Template->>PM: Run installation commands
    Template-->>SW: summary string
    
    SW->>SW: next_state.relevant_files = template.relevant_files
    SW->>SW: next_state.specification.template_summary = summary
```

**Template Selection Logic**

```python
if options["auth_type"] == "api_key" or options["auth_type"] == "none":
    template_name = "vite_react_swagger"
else:
    template_name = "vite_react"
```

**Sources:** [core/agents/spec_writer.py:34-62]()

---

## Base Template Architecture

### BaseProjectTemplate Interface

All templates inherit from `BaseProjectTemplate` and must implement the following contract:

```mermaid
classDiagram
    class BaseProjectTemplate {
        <<abstract>>
        +str name
        +type options_class
        +StateManager state_manager
        +ProcessManager process_manager
        +list relevant_files
        
        +__init__(options, state_manager, process_manager)
        +dict options_dict*
        +apply() str*
        +get_summary() str*
    }
    
    class ViteReactProjectTemplate {
        +str name = "vite_react"
        +type options_class = ViteReactOptions
        +apply() str
        +get_summary() str
    }
    
    class ViteReactSwaggerProjectTemplate {
        +str name = "vite_react_swagger"
        +type options_class = ViteReactSwaggerOptions
        +apply() str
        +get_summary() str
    }
    
    class NoOptions {
        <<pydantic BaseModel>>
        (no fields)
    }
    
    BaseProjectTemplate <|-- ViteReactProjectTemplate
    BaseProjectTemplate <|-- ViteReactSwaggerProjectTemplate
    BaseProjectTemplate ..> NoOptions : "templates with<br/>no options use"
```

**Key Methods**

| Method | Purpose | Return Type |
|--------|---------|-------------|
| `apply()` | Generate and save template files | `str` (summary) |
| `get_summary()` | Provide template information for context | `str` |
| `options_dict` | Property exposing options as dictionary | `dict` |

**Sources:** Inferred from [core/agents/architect.py:268-294](), [core/agents/spec_writer.py:34-62](), [core/agents/frontend.py:83-92]()

### Template Storage in StateManager

Templates are stored in the `StateManager` for access throughout the agent workflow:

```python
# Storage structure
self.state_manager.template = {
    "template": template_instance,  # The actual template object
    "description": project_description  # Updated by SpecWriter
}
```

The template instance is accessed by agents that need template-specific information:

```python
# Frontend agent accessing template
summary = self.state_manager.template["template"].get_summary()
```

**Sources:** [core/agents/spec_writer.py:48-56](), [core/agents/frontend.py:83-92]()

---

## Integration with Agent System

### Template Usage Across Agents

```mermaid
graph TB
    Architect["Architect Agent"]
    SpecWriter["SpecWriter Agent"]
    TechLead["TechLead Agent"]
    Frontend["Frontend Agent"]
    
    Architect -->|"select_templates()"| Templates["PROJECT_TEMPLATES<br/>registry"]
    Templates -->|"template_class"| Architect
    Architect -->|"configure_template()"| LLM["LLM fills options"]
    LLM -->|"options model"| Architect
    Architect -->|"spec.templates = {...}"| Specification["Specification object"]
    
    Specification -->|"spec.templates"| SpecWriter
    SpecWriter -->|"apply_template()"| TemplateInstance["Template instance"]
    TemplateInstance -->|"apply()"| FileSystem["Virtual File System"]
    TemplateInstance -->|"get_summary()"| SpecWriter
    SpecWriter -->|"template_summary"| Specification
    
    Specification -->|"Check spec.templates"| TechLead
    TechLead -->|"Skip if templates exist"| Decision{"Files exist?"}
    
    Specification -->|"template_summary<br/>for context"| Frontend
    Frontend -->|"Use in prompts"| LLM2["LLM (Frontend)"]
```

**Agent Responsibilities**

| Agent | Template Role |
|-------|--------------|
| `Architect` | Selects and configures templates based on project requirements |
| `SpecWriter` | Applies templates, stores summary in specification |
| `TechLead` | Checks for applied templates to skip redundant planning |
| `Frontend` | Uses template summary as context in prompts |

**Sources:** [core/agents/architect.py:124-171](), [core/agents/spec_writer.py:34-62](), [core/agents/frontend.py:83-92]()

### Template Summary in Context

The template summary is stored in the specification and used to provide context to LLM agents about the existing codebase structure:

```jinja2
{% if state.specification.template_summary %}
~~INFORMATION_ABOUT_THE_CODEBASE~~
{{ state.specification.template_summary }}
~~END_OF_INFORMATION_ABOUT_THE_CODEBASE~~
{% endif %}
```

This summary appears in prompts to agents so they understand the initial project structure without needing to analyze all template files individually.

**Sources:** [core/prompts/partials/project_details.prompt:7-11]()

---

## Template Options System

### Options Model Pattern

Templates use Pydantic models to define configurable options:

```mermaid
graph TB
    NoOptions["NoOptions<br/>(BaseModel)"]
    CustomOptions["ViteReactOptions<br/>(BaseModel)"]
    
    NoOptions -->|"No fields"| Simple["Simple templates<br/>no configuration needed"]
    CustomOptions -->|"auth: bool<br/>db_type: str<br/>etc."| Complex["Complex templates<br/>with choices"]
    
    CustomOptions -->|"Validated by<br/>Pydantic"| Values["Type-safe<br/>option values"]
    CustomOptions -->|"LLM populates<br/>via JSONParser"| Architect["Architect agent"]
```

**NoOptions Class**

For templates that require no configuration:

```python
class NoOptions(BaseModel):
    pass  # Empty model
```

This pattern allows the template system to treat all templates uniformly, whether they have options or not.

**Sources:** Inferred from [core/agents/architect.py:280-282]()

### Options Access Pattern

Templates expose their options as a dictionary for serialization to the database:

```python
@property
def options_dict(self) -> dict:
    return self.options.model_dump()  # Pydantic model to dict
```

This allows the specification to store template configurations:

```python
spec.templates = {
    template.name: template.options_dict 
    for template in templates.values()
}
```

**Sources:** Inferred from [core/agents/architect.py:194]()

---

## Asynchronous Template Application

### Background Template Processing

The `SpecWriter` agent supports asynchronous template application to avoid blocking the UI during potentially long installation processes:

```mermaid
sequenceDiagram
    participant SW as SpecWriter
    participant SM as StateManager
    participant Template as Template.apply()
    participant Frontend as Frontend Agent
    
    SW->>SM: state_manager.async_tasks = []
    SW->>Template: asyncio.create_task(template.apply())
    Note over SW,Template: Non-blocking start
    
    SW->>Frontend: Continue to frontend building
    Frontend->>Frontend: Build UI...
    
    Frontend->>SM: Check async_tasks[-1].done()
    alt Task not complete
        Frontend->>SM: await async_tasks[-1]
        SM-->>Frontend: Wait for completion
    end
    
    Frontend->>SM: Clear async_tasks
    Frontend->>Frontend: Proceed with processed files
```

**Synchronization Point**

The `Frontend` agent ensures template application completes before processing responses:

```python
# Await the template task if it's not done yet
if self.state_manager.async_tasks:
    if not self.state_manager.async_tasks[-1].done():
        await self.state_manager.async_tasks[-1]
    self.state_manager.async_tasks = []
```

This pattern allows the UI to remain responsive during npm installation and other time-consuming template setup operations.

**Sources:** [core/agents/frontend.py:96-100](), [core/agents/spec_writer.py:299-301]()

---

## Template File Management

### Relevant Files Tracking

Templates specify which files are most relevant for the project context:

```python
self.next_state.relevant_files = template.relevant_files
self.next_state.modified_files = {}
```

The `relevant_files` list helps the system prioritize which files to include in LLM context when there are many files in the project. This is crucial for staying within token limits.

**Sources:** [core/agents/spec_writer.py:59-60]()

### Template Summary Persistence

The template summary is persisted in the project specification for future agent runs:

```python
self.next_state.specification.template_summary = summary
```

This ensures that even if the project is reloaded from a saved state, agents still have context about the template-generated structure.

**Sources:** [core/agents/spec_writer.py:61]()

---

# Page: Vite React Templates

# Vite React Templates

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [core/agents/wizard.py](core/agents/wizard.py)
- [core/prompts/frontend/build_frontend.prompt](core/prompts/frontend/build_frontend.prompt)
- [core/prompts/frontend/system.prompt](core/prompts/frontend/system.prompt)
- [core/templates/info/vite_react/summary.tpl](core/templates/info/vite_react/summary.tpl)
- [core/templates/tree/vite_react/client/src/api/api.ts](core/templates/tree/vite_react/client/src/api/api.ts)
- [core/templates/tree/vite_react/client/src/api/auth.ts](core/templates/tree/vite_react/client/src/api/auth.ts)
- [core/templates/tree/vite_react/client/src/components/Header.tsx](core/templates/tree/vite_react/client/src/components/Header.tsx)
- [core/templates/tree/vite_react/client/src/components/ui/theme-provider.tsx](core/templates/tree/vite_react/client/src/components/ui/theme-provider.tsx)
- [core/templates/tree/vite_react/client/src/components/ui/theme-toggle.tsx](core/templates/tree/vite_react/client/src/components/ui/theme-toggle.tsx)
- [core/templates/tree/vite_react/client/src/pages/Login.tsx](core/templates/tree/vite_react/client/src/pages/Login.tsx)
- [core/templates/tree/vite_react/client/src/pages/Register.tsx](core/templates/tree/vite_react/client/src/pages/Register.tsx)
- [core/templates/tree/vite_react_swagger/client/.env](core/templates/tree/vite_react_swagger/client/.env)
- [core/templates/tree/vite_react_swagger/client/src/api/api.ts](core/templates/tree/vite_react_swagger/client/src/api/api.ts)
- [core/templates/tree/vite_react_swagger/client/src/pages/Login.tsx](core/templates/tree/vite_react_swagger/client/src/pages/Login.tsx)
- [core/templates/tree/vite_react_swagger/client/src/pages/Register.tsx](core/templates/tree/vite_react_swagger/client/src/pages/Register.tsx)
- [core/templates/vite_react.py](core/templates/vite_react.py)

</details>



This document provides a comprehensive technical overview of the two Vite React templates included in GPT Pilot. Both templates create modern React applications powered by Vite, TypeScript, and Tailwind CSS, but differ in their backend architecture and authentication approaches.

## 1. Template Overview

GPT Pilot provides two React-based project templates:

1. **Vite React Template** (`vite_react`) - Full-stack application with integrated Node.js/Express backend
2. **Vite React Swagger Template** (`vite_react_swagger`) - Frontend-only application that connects to an external API

### Template Comparison

| Feature | Vite React | Vite React Swagger |
|---------|-----------|-------------------|
| **Tech Stack** | Vite + React + Node.js + MongoDB | Vite + React + External API |
| **Backend** | Included (Express + MongoDB) | External (user-provided) |
| **Authentication** | JWT-based login/register | API Key, Bearer, OAuth2, or None |
| **Project Type** | `"backend"` | `"swagger"` |
| **Template Path** | `vite_react` | `vite_react_swagger` |
| **Use Case** | New full-stack applications | Frontend for existing APIs |

### High-Level Architecture Comparison

```mermaid
graph TD
    subgraph "Vite React Template"
        VR_Client["client/<br/>React Frontend"] --> VR_Proxy["Vite Proxy<br/>/api/*"]
        VR_Proxy --> VR_Server["server/<br/>Express Backend"]
        VR_Server --> VR_DB["MongoDB"]
        VR_Auth["JWT Auth<br/>Login/Register"]
    end
    
    subgraph "Vite React Swagger Template"
        VS_Client["client/<br/>React Frontend"] --> VS_Local["Local Auth API<br/>/api/auth/*"]
        VS_Client --> VS_External["External API<br/>OpenAPI Spec"]
        VS_External --> VS_Backend["User's Backend<br/>API"]
        VS_Auth["API Key or<br/>Bearer Token"]
    end
```

Sources:
- [core/templates/vite_react.py:1-124]()
- [core/agents/wizard.py:30-131]()

## 2. Common Frontend Architecture

Both templates share the same frontend structure and component library:

### 2.1 Frontend Directory Structure

```mermaid
graph TD
    Client["client/"] --> ClientSrc["src/"]
    Client --> ClientConfig["vite.config.ts<br/>tsconfig.json<br/>tailwind.config.js"]
    
    ClientSrc --> Components["components/"]
    ClientSrc --> API["api/"]
    ClientSrc --> Contexts["contexts/"]
    ClientSrc --> Pages["pages/"]
    ClientSrc --> Hooks["hooks/"]
    ClientSrc --> Lib["lib/"]
    
    Components --> UI["ui/<br/>Shadcn Components"]
    Components --> Layout["Layout.tsx<br/>Header.tsx<br/>Footer.tsx"]
    Components --> Protected["ProtectedRoute.tsx"]
    
    API --> APIBase["api.ts"]
    API --> AuthAPI["auth.ts"]
    
    Contexts --> AuthContext["AuthContext.tsx"]
    
    Pages --> Login["Login.tsx"]
    Pages --> Register["Register.tsx"]
    Pages --> Home["Home Page"]
```

Sources:
- [core/templates/vite_react.py:9-103]()

### 2.2 UI Component Library

Both templates include a comprehensive set of Shadcn UI components in `client/src/components/ui/`:

| Component Category | Notable Components |
|-------------------|-------------------|
| **Layout** | Card, Layout, Accordion, AspectRatio, Sheet, Sidebar |
| **Data Input** | Button, Checkbox, Input, Select, Form, Textarea |
| **Navigation** | Tabs, Breadcrumb, NavigationMenu, Pagination, Menubar |
| **Feedback** | Alert, Dialog, Toast, Progress, AlertDialog |
| **Display** | Table, Avatar, Calendar, Badge, Chart |
| **Utility** | ThemeProvider, ThemeToggle, Toaster |

Sources:
- [core/templates/vite_react.py:9-102]()

## 3. Vite React Template (Full-Stack)

The standard `vite_react` template provides a complete full-stack application with integrated backend.

### 3.1 Project Structure

```mermaid
graph TD
    Root["Project Root"] --> Client["client/"]
    Root --> Server["server/"]
    Root --> RootPackage["package.json<br/>concurrently scripts"]
    
    Server --> Routes["routes/<br/>authRoutes.js<br/>index.js"]
    Server --> Models["models/<br/>User.js"]
    Server --> Services["services/<br/>userService.js<br/>llmService.js"]
    Server --> Config["config/<br/>database.js"]
    Server --> Middleware["routes/middleware/<br/>auth.js"]
    Server --> Utils["utils/<br/>auth.js<br/>password.js"]
    Server --> ServerJS["server.js"]
```

Sources:
- [core/templates/vite_react.py:87-102]()

### 3.2 Communication Flow

```mermaid
sequenceDiagram
    participant Client as "React Client"
    participant API as "api.ts"
    participant Proxy as "Vite Proxy<br/>localhost:5173"
    participant Server as "server.js<br/>localhost:3000"
    participant DB as "MongoDB"
    
    Client->>API: Call API function
    API->>Proxy: HTTP Request to /api/*
    Proxy->>Server: Forward to localhost:3000/api/*
    Server->>DB: Query or update data
    DB-->>Server: Return results
    Server-->>Proxy: JSON Response
    Proxy-->>API: Forward response
    API-->>Client: Return processed data
```

The Vite proxy configuration forwards all `/api/*` requests to the Express server running on port 3000.

Sources:
- [core/templates/info/vite_react/summary.tpl:1-28]()

### 3.3 Backend Configuration

The Express backend (`server/server.js`) is configured with:

| Middleware | Purpose |
|-----------|---------|
| `express.json()` | Parse JSON request bodies |
| `express.urlencoded()` | Parse URL-encoded bodies |
| `express-session` | Session management with MongoDB store |
| `connect-mongo` | MongoDB session persistence |
| `cors` | Cross-origin resource sharing |

Database connection is established via `config/database.js` using Mongoose.

Sources:
- [core/templates/vite_react.py:88-96]()
- [core/templates/info/vite_react/summary.tpl:16-27]()

### 3.4 API Layer Structure

The frontend API layer uses a single Axios instance (`localApi`) for all requests:

```mermaid
graph LR
    Component["React Component"] --> AuthAPI["auth.ts<br/>login()<br/>register()<br/>logout()"]
    AuthAPI --> APIUtil["api.ts<br/>localApi instance"]
    APIUtil --> Interceptors["Request/Response<br/>Interceptors"]
    Interceptors --> JWT["JWT Token<br/>Management"]
    JWT --> Backend["Express Backend<br/>/api/auth/*"]
```

Sources:
- [core/templates/tree/vite_react/client/src/api/api.ts:1-172]()
- [core/templates/tree/vite_react/client/src/api/auth.ts:1-45]()

## 4. Vite React Swagger Template (External API)

The `vite_react_swagger` template is designed for building frontends that connect to existing backend APIs documented with OpenAPI/Swagger specifications.

### 4.1 Template Initialization

When creating a Swagger project, the `Wizard` agent guides the user through setup:

```mermaid
sequenceDiagram
    participant User
    participant Wizard as "Wizard Agent"
    participant API as "Pythagora API<br/>/rag/upload"
    participant Template as "Template System"
    
    User->>Wizard: Start Swagger project
    Wizard->>User: Request OpenAPI/Swagger docs
    User->>Wizard: Paste JSON/YAML docs
    Wizard->>API: Upload docs for processing
    API-->>Wizard: Return external_api_url and types
    Wizard->>User: Select authentication method
    User->>Wizard: Choose auth type
    Wizard->>Template: Create KnowledgeBase with options
    Template->>Template: Generate project files
```

The wizard collects:
- OpenAPI/Swagger specification (JSON or YAML)
- External API URL (extracted from the spec)
- Authentication method (API Key, Bearer, OAuth2, or None)
- API credentials (if applicable)

Sources:
- [core/agents/wizard.py:30-131]()

### 4.2 Authentication Options

The Swagger template supports multiple authentication methods:

| Auth Type | Description | Configuration |
|-----------|-------------|---------------|
| `"api_key"` | API Key in headers | Stored in `.env` as `VITE_API_KEY` |
| `"none"` | No authentication | No credentials needed |
| `"bearer"` | HTTP Bearer tokens | Coming soon |
| `"oauth2"` | OAuth2 flow | Coming soon |
| `"open_id_connect"` | OpenID Connect | Coming soon |

Sources:
- [core/agents/wizard.py:60-111]()
- [core/templates/tree/vite_react_swagger/client/.env:1-6]()

### 4.3 Dual API Architecture

The Swagger template uses two Axios instances to handle local and external APIs:

```mermaid
graph TD
    Component["React Component"] --> APICall["api.get/post/put/delete"]
    APICall --> RouteCheck["getApiInstance(url)"]
    RouteCheck --> IsAuth{"url includes<br/>/api/auth?"}
    
    IsAuth -- "Yes" --> LocalAPI["localApi<br/>no baseURL"]
    IsAuth -- "No" --> ExternalAPI["externalApi<br/>baseURL: VITE_EXTERNAL_API_URL"]
    
    LocalAPI --> LocalEndpoint["Local Auth Endpoints<br/>/api/auth/login<br/>/api/auth/register"]
    ExternalAPI --> AddAPIKey["Add API Key Header<br/>if configured"]
    AddAPIKey --> ExternalEndpoint["External API<br/>User's Backend"]
```

This architecture allows the frontend to handle authentication locally while proxying all other requests to the external API.

Sources:
- [core/templates/tree/vite_react_swagger/client/src/api/api.ts:1-172]()

### 4.4 API Configuration Code Structure

The `client/src/api/api.ts` file creates two Axios instances:

```
localApi = axios.create({
  // No baseURL - uses Vite proxy for /api/auth/*
  headers: { 'Content-Type': 'application/json' }
})

externalApi = axios.create({
  baseURL: VITE_EXTERNAL_API_URL,  // From .env
  headers: { 'Content-Type': 'application/json' }
})
```

The `getApiInstance()` function routes requests:
- Auth endpoints (`/api/auth/*`) → `localApi`
- All other endpoints → `externalApi`

Request interceptors add authentication:
- API Key (if configured): Added to `api_key` header
- JWT tokens: Added to `Authorization` header as Bearer token

Sources:
- [core/templates/tree/vite_react_swagger/client/src/api/api.ts:12-44]()
- [core/templates/tree/vite_react_swagger/client/src/api/api.ts:55-145]()

### 4.5 Environment Variables

The Swagger template requires environment configuration in `client/.env`:

```
VITE_API_KEY=<user_provided_key>
VITE_EXTERNAL_API_URL=<backend_url>
```

These values are set during project initialization by the `Wizard` agent.

Sources:
- [core/templates/tree/vite_react_swagger/client/.env:1-6]()
- [core/agents/wizard.py:85-91]()

## 5. Authentication System

### 5.1 Login and Register Pages

Both templates include pre-built authentication pages with consistent UI:

**Login Page Components:**
- Email and password input fields
- Form validation using `react-hook-form`
- Error handling with toast notifications
- Mock data indicator during frontend development
- Navigation link to registration page

**Register Page Components:**
- Email and password input fields
- Account creation flow
- Redirect to login after successful registration
- Error handling with toast notifications

Both pages include a prominent yellow alert box with the text "Pythagora: You can use any email/password in the frontend phase" to indicate that authentication is mocked during frontend development.

Sources:
- [core/templates/tree/vite_react/client/src/pages/Login.tsx:1-118]()
- [core/templates/tree/vite_react/client/src/pages/Register.tsx:1-118]()
- [core/templates/tree/vite_react_swagger/client/src/pages/Login.tsx:1-118]()
- [core/templates/tree/vite_react_swagger/client/src/pages/Register.tsx:1-118]()

### 5.2 Authentication Context

The `AuthContext.tsx` provides global authentication state management:

```mermaid
graph TD
    AuthProvider["AuthProvider"] --> State["Authentication State<br/>isAuthenticated<br/>user<br/>loading"]
    AuthProvider --> Methods["Auth Methods<br/>login()<br/>register()<br/>logout()"]
    
    Methods --> Login["login()"]
    Login --> APICall["Call auth.ts API"]
    APICall --> StoreTokens["Store tokens in localStorage"]
    StoreTokens --> UpdateState["Update isAuthenticated"]
    
    Methods --> Logout["logout()"]
    Logout --> ClearTokens["Clear localStorage"]
    ClearTokens --> ResetState["Reset authentication state"]
```

Sources:
- [core/templates/tree/vite_react/client/src/contexts/AuthContext.tsx:1-70]()

### 5.3 Token Management and Refresh Flow

Both templates implement automatic token refresh on 401/403 errors:

```mermaid
sequenceDiagram
    participant Component
    participant Interceptor as "Response Interceptor"
    participant LocalAPI as "localApi"
    participant Server
    
    Component->>LocalAPI: Make API request
    LocalAPI->>Server: Request with access token
    Server-->>Interceptor: 401/403 Unauthorized
    
    Interceptor->>Interceptor: Check if retry attempted
    Interceptor->>LocalAPI: POST /api/auth/refresh
    LocalAPI->>Server: Send refresh token
    Server-->>LocalAPI: New access & refresh tokens
    LocalAPI-->>Interceptor: Return new tokens
    
    Interceptor->>Interceptor: Update localStorage
    Interceptor->>LocalAPI: Retry original request
    LocalAPI->>Server: Request with new token
    Server-->>Component: Success response
    
    Note over Interceptor: If refresh fails:<br/>Clear tokens and redirect to /login
```

The interceptor prevents infinite loops by:
1. Only refreshing on 401/403 errors
2. Using `_retry` flag to prevent multiple refresh attempts
3. Skipping refresh for `/api/auth/refresh` endpoint itself

Sources:
- [core/templates/tree/vite_react/client/src/api/api.ts:79-137]()
- [core/templates/tree/vite_react_swagger/client/src/api/api.ts:79-137]()

### 5.4 Protected Routes

The `ProtectedRoute.tsx` component guards authenticated pages:

```
<ProtectedRoute>
  <Dashboard />
</ProtectedRoute>
```

It checks `isAuthenticated` from `AuthContext` and redirects to `/login` if not authenticated.

Sources:
- [core/templates/vite_react.py:22]()

## 6. Development Workflow

### 6.1 Running the Application

The template provides scripts for development and installation:

| Script | Purpose |
|--------|---------|
| `npm run postinstall` | Install dependencies for both client and server |
| `npm run client` | Start client dev server on port 5173 |
| `npm run server` | Start server on port 3000 |
| `npm start` | Run client and server concurrently |

Sources:
- [core/templates/tree/vite_react/package.json:6-12]()
- [core/templates/info/vite_react/summary.tpl:1-28]()

### 6.2 API Mocking System

The template includes a standardized approach to API mocking:

```
// Description: [API purpose]
// Endpoint: [HTTP method and path]
// Request: [Request structure]
// Response: [Response structure]
export const apiFunction = (params) => {
  // Mock implementation (used during frontend development)
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({ /* mock data */ });
    }, 500);
  });
  
  // Real implementation (uncomment when backend is ready)
  // try {
  //   return await api.get('/api/endpoint', params);
  // } catch (error) {
  //   throw new Error(error?.response?.data?.error || error.message);
  // }
}
```

This pattern allows frontend development to proceed independently from backend implementation.

Sources:
- [core/templates/info/vite_react/summary.tpl:30-92]()
- [core/templates/tree/vite_react/client/src/api/auth.ts:8-43]()

## 7. Template Customization

The template can be customized with options:

| Option | Description | Implementation Impact |
|--------|-------------|----------------------|
| `auth` | Enable/disable authentication | Includes/excludes auth-related files and components |
| `db_type` | Database type (nosql/sql) | Configures database connection implementation |

These options are controlled through template conditions in the source files.

Sources:
- [core/templates/vite_react.py:105-106]()
- [core/templates/tree/vite_react/server/models/init.js:1-29]()

## 8. Installation Hook

The template includes an installation hook that runs when a new project is created:

```python
async def install_hook(self):
    await self.process_manager.run_command("npm install", show_output=False)
```

This ensures all dependencies are installed automatically after project creation.

Sources:
- [core/templates/vite_react.py:135-136]()

---

# Page: Deployment and Operations

# Deployment and Operations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [Dockerfile](Dockerfile)
- [cloud/posthog.html](cloud/posthog.html)
- [core/llm/relace_client.py](core/llm/relace_client.py)

</details>



This page documents deployment configurations and operational aspects of GPT Pilot. It covers Docker containerization, cloud-specific setup, and continuous integration workflows. For information about the project templates used during application creation, see [Project Templates](#7).

GPT Pilot provides a Docker-based deployment solution designed for cloud environments, with integrated code-server (browser-based VS Code), automatic extension installation, and analytics tracking.

## 8.1 Docker Environment

GPT Pilot's Docker container provides a complete development environment with browser-based VS Code (code-server), Python runtime, and all necessary dependencies.

### Dockerfile Structure and Build Process

**Container Base and Dependencies**

```mermaid
graph TB
    Base[Ubuntu 22.04] --> BuildArgs["TARGETPLATFORM<br/>BUILDPLATFORM"]
    BuildArgs --> CopyVSIX["Copy pythagora-vs-code.vsix"]
    CopyVSIX --> SetupDeps["setup-dependencies.sh<br/>Install system packages"]
    SetupDeps --> PythonSetup["Python Virtual Environment<br/>venv/bin/activate"]
    PythonSetup --> Requirements["Install requirements.txt"]
    Requirements --> CopyCore["Copy Core Application Files<br/>main.py, core/, config.json"]
    CopyCore --> ExposeCheck["Expose Ports<br/>27017, 8000, 8080, 5173, 3000"]
    ExposeCheck --> UserSetup["Create devuser:devusergroup<br/>UID/GID 1000"]
    UserSetup --> CodeServerSetup["Configure code-server"]
    CodeServerSetup --> PostHogSetup["Integrate PostHog Analytics"]
    PostHogSetup --> Entrypoint["Set /entrypoint.sh"]
```

Sources: [Dockerfile:1-99]()

The build process follows this sequence:
1. **Base Image**: Ubuntu 22.04 with multi-architecture support via `TARGETPLATFORM` and `BUILDPLATFORM` arguments [Dockerfile:1-9]()
2. **Extension Preparation**: VS Code extension VSIX file is copied early [Dockerfile:11-12]()
3. **Dependency Installation**: `setup-dependencies.sh` installs system packages, code-server, and runtime dependencies [Dockerfile:14-18]()
4. **Python Environment**: Virtual environment created at `${PYTH_INSTALL_DIR}/pythagora-core/venv` with requirements installed [Dockerfile:29-31]()
5. **Application Files**: Core Python modules and configuration copied [Dockerfile:34-37]()

### Multi-Architecture Support

The Docker image supports both AMD64 and ARM64 architectures using Docker buildx:

| Build Argument | Purpose | Example Value |
|----------------|---------|---------------|
| `TARGETPLATFORM` | Platform being built for | `linux/amd64`, `linux/arm64` |
| `BUILDPLATFORM` | Platform running the build | `linux/amd64` |

Sources: [Dockerfile:4-9]()

The `TARGETPLATFORM` environment variable is made available to build scripts for platform-specific installation logic.

### code-server Configuration

The container includes code-server (browser-based VS Code) with extensive configuration:

**Directory Structure Setup**

```mermaid
graph TB
    Root["/usr/local/share/code-server/data/"] --> User["User/"]
    User --> GlobalStorage["globalStorage/"]
    User --> History["History/"]
    Root --> Machine["Machine/<br/>settings.json"]
    Root --> Logs["logs/"]
    
    Permissions["chown -R devuser:devusergroup<br/>chmod -R 755"]
    
    Root --> Permissions
```

Sources: [Dockerfile:62-72]()

The following directories are created with proper permissions:
- `/usr/local/share/code-server/data/User/globalStorage` - Extension storage
- `/usr/local/share/code-server/data/User/History` - File history
- `/usr/local/share/code-server/data/Machine` - Machine-specific settings
- `/usr/local/share/code-server/data/logs` - Log files

**Custom Branding**

The container replaces code-server's default icons with custom Pythagora branding:

```mermaid
graph LR
    SourceIcons["/favicon.svg<br/>/favicon.ico"] --> TargetMedia["/usr/local/lib/code-server/src/browser/media/"]
    TargetMedia --> favicon.ico
    TargetMedia --> favicon-dark-support.svg
    TargetMedia --> favicon.svg
```

Sources: [Dockerfile:59-60,73-76]()

### User and Permissions

The container runs as a non-root user for security:

| Component | Value | Purpose |
|-----------|-------|---------|
| Group | `devusergroup` (GID 1000) | Primary group for development files |
| User | `devuser` (UID 1000) | Non-root user with sudo access |
| Password | `devuser` | Default password (should be changed) |
| Sudo | `NOPASSWD:ALL` | Passwordless sudo for convenience |

Sources: [Dockerfile:49-54]()

All application directories are owned by `devuser`:
- `/pythagora` - Installation directory
- `/usr/local/share/code-server` - code-server data
- `/pythagora/pythagora-core/workspace` - User workspace

Sources: [Dockerfile:71,87-92]()

### Environment Variables

**Installation Paths**

| Variable | Default Value | Purpose |
|----------|---------------|---------|
| `PYTH_INSTALL_DIR` | `/pythagora` | Base installation directory |
| `VIRTUAL_ENV` | `${PYTH_INSTALL_DIR}/pythagora-core/venv` | Python virtual environment |
| `PATH` | `$VIRTUAL_ENV/bin:$PATH` | Includes venv binaries |
| `PYTHAGORA_DATA_DIR` | `${PYTH_INSTALL_DIR}/pythagora-core/data/` | Persistent data storage |
| `TARGETPLATFORM` | `linux/amd64` (default) | Build platform target |

Sources: [Dockerfile:20,40-44,8-9]()

### Port Exposure

The container exposes multiple ports for different services:

| Port | Service | Purpose |
|------|---------|---------|
| 27017 | MongoDB | Database access |
| 8000 | Application | Main application server |
| 8080 | Application | Alternative HTTP port |
| 5173 | Vite Dev Server | Frontend development |
| 3000 | Application | Common application port |

Sources: [Dockerfile:46-47]()

### Git Configuration

The container pre-configures git for the `devuser`:

```
git config --global user.email 'devuser@pythagora.ai'
git config --global user.name 'pythagora'
```

Sources: [Dockerfile:94-96]()

This ensures all git operations within the container have proper attribution.

## 8.2 Cloud Deployment

Cloud deployment includes entrypoint orchestration, automatic VS Code extension installation, and analytics integration.

### Entrypoint Script

The `/entrypoint.sh` script orchestrates container initialization:

**Service Startup Sequence**

```mermaid
graph TB
    Start["Container Start"] --> EntryPoint["/entrypoint.sh"]
    EntryPoint --> CheckSSH["Check SSH_KEY_B64<br/>Environment Variable"]
    CheckSSH --> DecodeKey["Decode Base64 SSH Key<br/>Write to /home/devuser/.ssh/authorized_keys"]
    DecodeKey --> MongoDataDir["Create MongoDB Data Directory<br/>$PYTHAGORA_DATA_DIR/mongodata"]
    MongoDataDir --> StartMongo["Start MongoDB<br/>mongod --bind_ip_all"]
    StartMongo --> DBDataDir["Create Database Directory<br/>$PYTHAGORA_DATA_DIR/db"]
    DBDataDir --> StartSSH["Start SSH Server<br/>service ssh start"]
    StartSSH --> Monitor["Background Monitor<br/>on-event-extension-install.sh"]
    Monitor --> Wait["Wait for VS Code Server"]
```

Sources: [Dockerfile:56-58,85]()

The entrypoint script is referenced in the Dockerfile but the full implementation handles:
1. SSH key configuration for remote access
2. MongoDB data directory creation and service startup
3. Database directory initialization
4. SSH server startup for remote development
5. Background monitoring for VS Code server installation

### Automatic Extension Installation

The `on-event-extension-install.sh` script automatically installs the Pythagora VS Code extension when a code-server instance starts:

**Extension Installation Flow**

```mermaid
graph TB
    Monitor["on-event-extension-install.sh<br/>Background Process"] --> CheckServer["Check for New<br/>VS Code Server Instance"]
    CheckServer --> ServerFound{"Server<br/>Detected?"}
    ServerFound -->|No| WaitLoop["Sleep 5 seconds"]
    WaitLoop --> CheckServer
    ServerFound -->|Yes| InstallExtension["Install Extension<br/>code-server --install-extension<br/>/var/init_data/pythagora-vs-code.vsix"]
    InstallExtension --> ConfigureWorkspace["Create Workspace Settings<br/>.vscode/settings.json"]
    ConfigureWorkspace --> Complete["Extension Ready"]
```

Sources: [Dockerfile:58,86]()

The script is copied to `/var/init_data/on-event-extension-install.sh` and monitors for code-server initialization to automatically install the extension from `/var/init_data/pythagora-vs-code.vsix`.

### PostHog Analytics Integration

The container integrates PostHog analytics into code-server for usage tracking:

**PostHog Integration Process**

```mermaid
graph TB
    HTML["cloud/posthog.html<br/>Analytics Snippet"] --> CSP["Update Content Security Policy<br/>server-main.js"]
    CSP --> InjectHTML["Inject PostHog Script<br/>workbench.html <head>"]
    
    InjectHTML --> Config["PostHog Configuration"]
    Config --> ProjectKey["Project Key:<br/>phc_CPMrohXQJiasSs2PCwK3SItm1mUT6F69dcLo1TMZOz8"]
    Config --> APIHost["API Host:<br/>https://us.i.posthog.com"]
    Config --> PersonProfiles["Person Profiles:<br/>identified_only"]
```

Sources: [Dockerfile:78-83](), [cloud/posthog.html:1-8]()

**Step 1: Update Content Security Policy**

The Dockerfile modifies `/usr/local/lib/code-server/lib/vscode/out/server-main.js` to allow PostHog assets:

```
sed -i "s|'sha256-/r7rqQ+yrxt57sxLuQ6AMYcy/lUpvAIzHjIJt/OeLWU=' ;|'sha256-/r7rqQ+yrxt57sxLuQ6AMYcy/lUpvAIzHjIJt/OeLWU=' https://us-assets.i.posthog.com ;|g"
```

Sources: [Dockerfile:79]()

**Step 2: Inject PostHog Script**

The PostHog initialization script is injected into the code-server HTML:

```javascript
posthog.init('phc_CPMrohXQJiasSs2PCwK3SItm1mUT6F69dcLo1TMZOz8', {
    api_host: 'https://us.i.posthog.com',
    defaults: '2025-05-24',
    person_profiles: 'identified_only',
})
```

Sources: [cloud/posthog.html:3-7]()

The snippet is inserted into `/usr/local/lib/code-server/lib/vscode/out/vs/code/browser/workbench/workbench.html` at the `<head>` tag [Dockerfile:82]().

### Cloud-Specific Configuration

The Docker container uses a cloud-optimized configuration file:

**Configuration File Placement**

```mermaid
graph LR
    Source["cloud/config-docker.json"] --> Copy["ADD to Container"]
    Copy --> Destination["/pythagora/pythagora-core/config.json"]
```

Sources: [Dockerfile:37]()

This configuration file (`cloud/config-docker.json`) is copied as the default `config.json` and contains cloud-specific settings optimized for container deployment.

## 8.3 Continuous Integration

GPT Pilot uses GitHub Actions to ensure code quality and compatibility across multiple platforms and Python versions.

### CI Workflow Configuration

**GitHub Actions Workflow**

```mermaid
graph TB
    Trigger["Workflow Triggers"] --> PushMain["Push to main Branch"]
    Trigger --> PRMain["Pull Request to main"]
    Trigger --> PRRewrite["Pull Request to rewrite"]
    
    PushMain --> Matrix["Build Matrix Strategy"]
    PRMain --> Matrix
    PRRewrite --> Matrix
    
    Matrix --> PyMatrix["Python Versions<br/>3.9, 3.12"]
    Matrix --> OSMatrix["Operating Systems<br/>ubuntu-latest<br/>macos-latest<br/>windows-latest"]
    
    PyMatrix --> Jobs["6 Parallel Jobs"]
    OSMatrix --> Jobs
    
    Jobs --> Steps["Build Steps"]
```

Sources: [.github/workflows/ci.yml:1-19]()

The workflow is triggered on:
- Pushes to the `main` branch
- Pull requests targeting `main` or `rewrite` branches

### Build Matrix

The CI system tests all combinations of Python versions and operating systems:

| Python Version | Ubuntu | macOS | Windows | Total Jobs |
|----------------|--------|-------|---------|------------|
| 3.9 | ✓ | ✓ | ✓ | 3 |
| 3.12 | ✓ | ✓ | ✓ | 3 |
| **Total** | **2** | **2** | **2** | **6** |

Sources: [.github/workflows/ci.yml:14-18]()

The matrix uses `fail-fast: false` to ensure all combinations are tested even if one fails.

### Build Steps

**CI Pipeline Stages**

```mermaid
graph TB
    Checkout["actions/checkout@v4<br/>Clone Repository"] --> SetupPython["actions/setup-python@v4<br/>Install Python $version"]
    SetupPython --> InstallPoetry["pip install poetry"]
    InstallPoetry --> PoetryInstall["poetry install --with=dev<br/>Install dependencies + dev tools"]
    PoetryInstall --> RuffLint["poetry run ruff check<br/>--output-format github"]
    RuffLint --> RuffFormat["poetry run ruff format<br/>--check --diff"]
    RuffFormat --> Pytest["poetry run pytest<br/>Run test suite"]
```

Sources: [.github/workflows/ci.yml:20-35]()

**Step 1: Checkout Code**
- Uses `actions/checkout@v4` to clone the repository [.github/workflows/ci.yml:21]()

**Step 2: Setup Python**
- Uses `actions/setup-python@v4` to install the specified Python version [.github/workflows/ci.yml:22-25]()

**Step 3: Install Dependencies**
- Installs Poetry package manager
- Runs `poetry install --with=dev` to install all dependencies including development tools [.github/workflows/ci.yml:26-29]()

**Step 4: Lint with ruff**
- Runs `poetry run ruff check --output-format github`
- Outputs results in GitHub annotation format for inline PR feedback [.github/workflows/ci.yml:30-31]()

**Step 5: Check Code Style**
- Runs `poetry run ruff format --check --diff`
- Verifies code formatting without making changes
- Shows diff of formatting issues [.github/workflows/ci.yml:32-33]()

**Step 6: Run Tests**
- Executes `poetry run pytest` to run the test suite [.github/workflows/ci.yml:34-35]()

### Timeout Configuration

Each job has a 10-minute timeout to prevent hung tests from consuming resources:

```yaml
timeout-minutes: 10
```

Sources: [.github/workflows/ci.yml:13]()

### Multi-Platform Support

The CI workflow validates that GPT Pilot works correctly on all major development platforms:

| Platform | Purpose | Key Differences |
|----------|---------|-----------------|
| `ubuntu-latest` | Linux development and Docker base | Native UNIX tools, fastest execution |
| `macos-latest` | macOS development | Case-insensitive filesystem, BSD tools |
| `windows-latest` | Windows development | Different path separators, Windows tools |

Sources: [.github/workflows/ci.yml:18]()

This comprehensive testing ensures GPT Pilot can be deployed on diverse developer workstations and CI environments.

## 4. VS Code Integration

GPT Pilot provides a VS Code extension for an improved development experience, which is automatically installed in the Docker environment.

```mermaid
flowchart TD
    subgraph "VS Code Remote Connection"
        VSCode["VS Code Client"]
        SSHConn["SSH Connection"]
        RemoteServer["VS Code Server"]
        Extension["GPT Pilot Extension"]
        
        VSCode --> SSHConn
        SSHConn --> RemoteServer
        RemoteServer --> Extension
    end
    
    subgraph "Extension Installation"
        Monitor["on-event-extension-install.sh"]
        DetectServer["Detect New VS Code Server"]
        InstallExt["Install Extension from VSIX"]
        
        Monitor --> DetectServer
        DetectServer --> InstallExt
    end
    
    InstallExt --> Extension
```

Sources: [on-event-extension-install.sh:1-35](), [Dockerfile:127-160]()

### 4.1 Automatic Extension Installation

When a VS Code server is started in the container, a monitoring script (`on-event-extension-install.sh`) detects the new server and automatically installs the GPT Pilot extension. This ensures a seamless setup experience.

Sources: [on-event-extension-install.sh:20-34]()

### 4.2 Workspace Configuration

The VS Code integration automatically configures the workspace settings to work properly in a remote environment:

```json
{
  "gptPilot.isRemoteWs": true,
  "gptPilot.useRemoteWs": false
}
```

This configuration is written to `/pythagora/pythagora-core/workspace/.vscode/settings.json` during setup.

Sources: [on-event-extension-install.sh:28-32]()

---

# Page: Docker Environment

# Docker Environment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [cloud/config-docker.json](cloud/config-docker.json)
- [cloud/entrypoint.sh](cloud/entrypoint.sh)
- [cloud/favicon.ico](cloud/favicon.ico)
- [cloud/favicon.svg](cloud/favicon.svg)
- [cloud/on-event-extension-install.sh](cloud/on-event-extension-install.sh)
- [cloud/posthog.html](cloud/posthog.html)
- [cloud/setup-dependencies.sh](cloud/setup-dependencies.sh)
- [core/llm/relace_client.py](core/llm/relace_client.py)

</details>



This page documents the Docker setup for GPT Pilot, explaining its configuration, architecture, and usage. The Docker environment provides a standardized, isolated, and reproducible development and deployment environment for GPT Pilot, with all necessary dependencies pre-configured.

For information about continuous integration and automated testing, see [Continuous Integration](#8.2).

## Overview

GPT Pilot's Docker environment encapsulates all required dependencies in a containerized setup, allowing for consistent development and deployment across different platforms. The environment includes Python 3.12, Node.js, MongoDB, and SSH server configurations, all pre-configured with the necessary settings for optimal performance.

```mermaid
flowchart TD
    subgraph "Docker Container"
        App["GPT Pilot Application"] --> Python["Python 3.12 Environment"]
        App --> MongoDB["MongoDB Database"]
        App --> NodeJS["Node.js Runtime"]
        SSHD["SSH Server"]
        VSCode["VS Code Server"] --> Extension["GPT Pilot Extension"]
        User["devuser"] 
    end
    
    External["External SSH Client"] --> SSHD
    DataVolume["Persistent Data Volume"] <--> MongoDB
    DataVolume <--> App
```

Sources: [Dockerfile:1-169]()

## Container Configuration

The Docker environment is defined in a multi-architecture Dockerfile that supports both AMD64 (x86_64) and ARM64 platforms.

### Base Image and System Dependencies

The container is built on Ubuntu 22.04 and includes a comprehensive set of system dependencies:

```mermaid
flowchart LR
    Ubuntu["Ubuntu 22.04 Base"] --> BuildTools["Build Tools"]
    Ubuntu --> Python["Python 3.12"]
    Ubuntu --> NodeJS["Node.js LTS"]
    Ubuntu --> MongoDB["MongoDB 6.0"]
    Ubuntu --> SSH["OpenSSH Server"]
    Ubuntu --> Utils["Utilities (vim, nano, etc.)"]
```

Sources: [Dockerfile:1-24](), [Dockerfile:26-43](), [Dockerfile:45-61]()

### Key Configuration Details

| Component | Configuration | Purpose |
|-----------|---------------|---------|
| Python | 3.12 with virtual environment | Application runtime |
| MongoDB | Version 6.0 | Persistent data storage |
| Node.js | LTS version | Frontend dependencies |
| SSH | Secure remote access | Remote development |
| User | `devuser` (UID 1000) | Container operations |

Sources: [Dockerfile:26-43](), [Dockerfile:45-61](), [Dockerfile:98-104]()

### Environment Variables and Working Directory

The Docker container sets several environment variables to configure the application environment:

| Variable | Value | Purpose |
|----------|-------|---------|
| `PYTH_INSTALL_DIR` | `/pythagora` | Base installation directory |
| `VIRTUAL_ENV` | `/pythagora/pythagora-core/venv` | Python virtual environment path |
| `PYTHAGORA_DATA_DIR` | `/pythagora/pythagora-core/data/` | Data storage location |

The working directory is set to `/pythagora/pythagora-core`, where the application code resides.

Sources: [Dockerfile:70-93]()

## Container Runtime Behavior

When the Docker container starts, it executes a sequence of operations defined in the entrypoint script:

```mermaid
sequenceDiagram
    participant Container as "Docker Container"
    participant SSH as "SSH Service"
    participant MongoDB as "MongoDB Service"
    participant VSCode as "VS Code Server Monitor"
    
    Container->>Container: Decode SSH_KEY_B64 to authorized_keys
    Container->>MongoDB: Create data directory
    Container->>MongoDB: Start MongoDB server
    Container->>VSCode: Start extension installation monitor
    Container->>SSH: Start SSH daemon
    
    Note over Container,SSH: Container keeps running as long as SSH daemon is active
```

Sources: [entrypoint.sh:1-28]()

### SSH Configuration

The container configures SSH for secure remote access with these settings:
- Password authentication disabled
- Root login prohibited
- Public key authentication enabled

SSH keys are injected at runtime through the `SSH_KEY_B64` environment variable, which should contain a base64-encoded SSH public key.

Sources: [Dockerfile:63-68](), [entrypoint.sh:3-9]()

### MongoDB Setup

MongoDB is configured to:
- Store data in the persistent `$PYTHAGORA_DATA_DIR/mongodata` directory
- Listen on all interfaces (`--bind_ip_all`)
- Run in the background with logs redirected to a file

Sources: [entrypoint.sh:11-14]()

## VS Code Integration

The Docker environment includes special handling for VS Code's remote development capabilities:

```mermaid
flowchart TD
    VSCodeServer["VS Code Server Detection"] -- "New server detected" --> ExtensionInstall["Install GPT Pilot Extension"]
    ExtensionInstall --> ConfigWorkspace["Configure Workspace Settings"]
    
    subgraph "File System Monitoring"
        InotifyWatch["inotify-watch on .vscode-server/cli/servers"]
        InotifyWatch -- "Stable-* directory created" --> VSCodeServer
    end
```

Sources: [on-event-extension-install.sh:1-35]()

### Automatic Extension Installation

A background process monitors the VS Code server directory for new installations and automatically:
1. Detects when a new VS Code server is set up
2. Waits for the server to be fully initialized
3. Installs the GPT Pilot extension from a local `.vsix` file
4. Configures workspace settings for remote operation

This ensures that any VS Code instance connecting to the container will have the GPT Pilot extension ready to use.

Sources: [on-event-extension-install.sh:21-34](), [Dockerfile:128-154]()

## Multi-Architecture Support

The Dockerfile includes platform-specific instructions to support both AMD64 (x86_64) and ARM64 architectures:

```mermaid
flowchart TD
    BuildProcess["Docker Build Process"] -- "TARGETPLATFORM detection" --> ArchDetection["Architecture Detection"]
    
    ArchDetection -- "linux/amd64" --> AMD64["AMD64 Specific Configuration"]
    ArchDetection -- "linux/arm64" --> ARM64["ARM64 Specific Configuration"]
    
    AMD64 --> MongoAMD["MongoDB for x86_64"]
    ARM64 --> MongoARM["MongoDB for ARM64"]
```

The build process uses Docker's `TARGETPLATFORM` argument to determine which architecture-specific steps to execute, particularly for MongoDB installation which requires different package sources for each architecture.

Sources: [Dockerfile:8-10](), [Dockerfile:45-61]()

## Database Integration

The Docker environment supports SQLite and PostgreSQL databases through an async-aware session manager. The database configuration is specified through environment variables and can be adjusted based on deployment needs.

```mermaid
flowchart LR
    App["GPT Pilot Application"] --> SessionManager["SessionManager"]
    SessionManager -- "SQLite" --> SQLiteDB["SQLite Database"]
    SessionManager -- "PostgreSQL" --> PostgreSQL["PostgreSQL Database"]
    
    subgraph "Database Connections"
        SQLiteDB -- "PRAGMA foreign_keys=on" --> SQLiteConn["SQLite Connection"]
        PostgreSQL --> PGPool["PostgreSQL Connection Pool"]
    end
```

The `SessionManager` class provides an async context manager for database operations, creating and managing sessions as needed.

Sources: [core/db/session.py:10-75]()

## Usage and Configuration

To use the Docker environment:

1. Build the Docker image:
   ```
   docker build -t gpt-pilot .
   ```

2. Run the container with appropriate environment variables:
   ```
   docker run -d \
     -e SSH_KEY_B64="$(cat ~/.ssh/id_rsa.pub | base64)" \
     -p 22:22 -p 27017:27017 -p 8000:8000 \
     -v ./data:/pythagora/pythagora-core/data \
     gpt-pilot
   ```

3. Connect to the container via SSH:
   ```
   ssh devuser@localhost
   ```

The key configuration points are:
- The SSH key must be provided as a base64-encoded environment variable
- Data persistence is achieved through volume mounting
- The application is accessible on port 8000
- MongoDB is accessible on port 27017

Sources: [Dockerfile:95-96](), [entrypoint.sh:3-9]()

---

# Page: Cloud Deployment

# Cloud Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [cloud/config-docker.json](cloud/config-docker.json)
- [cloud/entrypoint.sh](cloud/entrypoint.sh)
- [cloud/favicon.ico](cloud/favicon.ico)
- [cloud/favicon.svg](cloud/favicon.svg)
- [cloud/on-event-extension-install.sh](cloud/on-event-extension-install.sh)
- [cloud/posthog.html](cloud/posthog.html)
- [cloud/setup-dependencies.sh](cloud/setup-dependencies.sh)
- [core/llm/relace_client.py](core/llm/relace_client.py)

</details>



## Purpose and Scope

This document covers cloud-specific deployment configuration for GPT Pilot, including container orchestration, browser-based IDE integration, analytics telemetry, and API authentication. It focuses on the production cloud deployment environment where GPT Pilot runs as a hosted service accessed through a web browser.

For general Docker container setup and development environment configuration, see [Docker Environment](#8.1). For automated testing and CI/CD pipelines, see [Continuous Integration](#8.3).

---

## Cloud Deployment Architecture

The cloud deployment architecture extends the base Docker container with browser-based IDE access, analytics tracking, and cloud service integration. The container runs a complete development environment accessible via code-server (browser-based VSCode).

```mermaid
graph TB
    subgraph "Cloud Container"
        Entrypoint["/entrypoint.sh<br/>Container Startup"]
        CodeServer["code-server<br/>Port 8080<br/>Browser VSCode"]
        PythagoraCore["GPT Pilot Core<br/>/pythagora/pythagora-core"]
        Workspace["Workspace<br/>/pythagora/pythagora-core/workspace"]
        Database["SQLite Database<br/>data/database/pythagora.db"]
        
        Entrypoint --> CodeServer
        CodeServer --> Workspace
        PythagoraCore --> Database
    end
    
    subgraph "External Services"
        PostHog["PostHog Analytics<br/>us.i.posthog.com"]
        RelaceAPI["Relace API<br/>api.pythagora.io"]
        LLMProviders["LLM Providers<br/>OpenAI/Anthropic"]
    end
    
    subgraph "User Access"
        Browser["Web Browser"]
    end
    
    Browser -->|"HTTP Port 8080"| CodeServer
    CodeServer -->|"IPC Protocol"| PythagoraCore
    PythagoraCore -->|"Analytics Events"| PostHog
    PythagoraCore -->|"Code Merge Requests"| RelaceAPI
    PythagoraCore -->|"LLM Requests"| LLMProviders
    
    CodeServer -.->|"File Operations"| Workspace
    PythagoraCore -.->|"File Storage"| Workspace
```

**Cloud Deployment Flow**

The container initialization follows this startup sequence:

```mermaid
stateDiagram-v2
    [*] --> Entrypoint: Container Start
    Entrypoint --> SetPermissions: "chown -R devuser"
    SetPermissions --> CreateDirectories: "mkdir data/database"
    CreateDirectories --> LaunchExtensionInstaller: "on-event-extension-install.sh"
    
    LaunchExtensionInstaller --> StartCodeServer: "code-server --port 8080"
    StartCodeServer --> WaitForHealthz: "Poll /healthz endpoint"
    WaitForHealthz --> Ready: "HTTP 200 OK"
    Ready --> [*]: "tail -f /dev/null"
    
    note right of Ready
        Container stays alive
        User accesses via browser
        GPT Pilot runs on-demand
    end note
```

**Sources:** [Dockerfile:1-99](), [cloud/entrypoint.sh:1-35]()

---

## Container Entrypoint Configuration

The entrypoint script [`/entrypoint.sh`](cloud/entrypoint.sh:1-35) orchestrates container startup and service initialization.

### Entrypoint Script Flow

| Step | Action | Purpose |
|------|--------|---------|
| 1 | Set environment variables | Configure `PYTHAGORA_DATA_DIR` and `DB_DIR` paths |
| 2 | Change ownership | Ensure `devuser` owns all data directories [cloud/entrypoint.sh:26]() |
| 3 | Create database directory | Initialize `data/database` for SQLite storage [cloud/entrypoint.sh:27]() |
| 4 | Launch extension installer | Start `on-event-extension-install.sh` as background process [cloud/entrypoint.sh:30]() |
| 5 | Keep container alive | Run `tail -f /dev/null` to prevent exit [cloud/entrypoint.sh:34]() |

### Directory Structure

```
/pythagora/
└── pythagora-core/
    ├── venv/                    # Python virtual environment
    ├── data/
    │   ├── database/            # SQLite database files
    │   │   └── pythagora.db
    │   └── pythagora.log        # Application logs
    ├── workspace/               # User project files
    │   └── .vscode/
    │       └── settings.json    # VSCode workspace config
    ├── core/                    # Application source code
    ├── main.py                  # Entry point
    └── config.json              # Cloud configuration
```

### Key Environment Variables

The Dockerfile and entrypoint configure these environment variables:

| Variable | Value | Purpose |
|----------|-------|---------|
| `PYTH_INSTALL_DIR` | `/pythagora` | Root installation directory [Dockerfile:20]() |
| `PYTHAGORA_DATA_DIR` | `/pythagora/pythagora-core/data/` | Data storage location [Dockerfile:43]() |
| `DB_DIR` | `${PYTHAGORA_DATA_DIR}/database` | SQLite database directory [cloud/entrypoint.sh:24]() |
| `VIRTUAL_ENV` | `/pythagora/pythagora-core/venv` | Python virtual environment [Dockerfile:40]() |
| `PATH` | `$VIRTUAL_ENV/bin:$PATH` | Include venv binaries [Dockerfile:41]() |

**Sources:** [Dockerfile:20-44](), [cloud/entrypoint.sh:8-27]()

---

## Code-Server Browser IDE Integration

GPT Pilot's cloud deployment uses code-server to provide a browser-accessible VSCode instance. The extension installer script manages code-server lifecycle and VSCode extension installation.

### Code-Server Configuration

The code-server configuration is defined at [`/etc/code-server/config.yaml`](Dockerfile:118-123):

```yaml
bind-addr: 0.0.0.0:8080
auth: none
extensions-dir: /usr/local/share/code-server/extensions
user-data-dir: /usr/local/share/code-server/data
```

Key configuration aspects:
- **Port 8080**: HTTP server listening on all interfaces
- **No authentication**: Auth handled by external proxy/gateway
- **Shared extensions directory**: Pre-installed Pythagora extension available to all sessions
- **Persistent user data**: Settings and workspace state preserved

### Extension Installation Process

The [`on-event-extension-install.sh`](cloud/on-event-extension-install.sh:1-26) script manages the browser IDE lifecycle:

```mermaid
sequenceDiagram
    participant Entrypoint as entrypoint.sh
    participant Installer as on-event-extension-install.sh
    participant CodeServer as code-server
    participant HealthCheck as Health Check Loop
    
    Entrypoint->>Installer: su -c "./on-event-extension-install.sh" devuser
    Installer->>Installer: Create workspace/.vscode/settings.json
    Installer->>CodeServer: Start code-server --port 8080
    Installer->>Installer: Save PID to /tmp/vscode-http-server.pid
    
    loop Every 0.5s for 15s
        HealthCheck->>CodeServer: curl http://localhost:8080/healthz
        alt Health Check Success
            CodeServer-->>HealthCheck: HTTP 200 OK
            HealthCheck->>Installer: Break loop
        else Timeout
            HealthCheck->>HealthCheck: Continue polling
        end
    end
    
    Installer->>Installer: Log "VS Code server started"
```

### Workspace Settings

The script creates workspace-specific settings at [`workspace/.vscode/settings.json`](cloud/on-event-extension-install.sh:8-9):

```json
{
  "gptPilot.isRemoteWs": true,
  "gptPilot.useRemoteWs": false,
  "workbench.colorTheme": "Default Dark+",
  "remote.autoForwardPorts": false
}
```

These settings configure the Pythagora extension for cloud operation:
- `isRemoteWs`: Indicates this is a remote workspace
- `useRemoteWs`: Controls whether to use remote workspace features
- `autoForwardPorts`: Disabled to prevent automatic port forwarding conflicts

### Custom Branding

The Dockerfile replaces default code-server icons with Pythagora branding:

```bash
cp -f /favicon.ico /usr/local/lib/code-server/src/browser/media/favicon.ico
cp -f /favicon.svg /usr/local/lib/code-server/src/browser/media/favicon-dark-support.svg
cp -f /favicon.svg /usr/local/lib/code-server/src/browser/media/favicon.svg
```

**Sources:** [Dockerfile:68-77](), [cloud/on-event-extension-install.sh:1-26](), [cloud/favicon.svg:1-5](), [cloud/favicon.ico:1-10]()

---

## Cloud Configuration Profile

The cloud deployment uses a specialized configuration file at [`cloud/config-docker.json`](cloud/config-docker.json:1-154) that optimizes settings for hosted environments.

### LLM Provider Configuration

Cloud instances configure LLM providers to use environment-based API keys:

```json
{
  "llm": {
    "openai": {
      "base_url": null,
      "api_key": null,
      "connect_timeout": 60.0,
      "read_timeout": 60.0
    },
    "anthropic": { ... },
    "relace": { ... }
  }
}
```

The `api_key: null` values indicate that API keys are injected at runtime through environment variables or external configuration management, rather than being hardcoded in the container image.

### Agent Model Assignments

Cloud deployments use optimized model selections for cost and performance:

| Agent/Function | Provider | Model | Temperature |
|----------------|----------|-------|-------------|
| Default | openai | gpt-4o-2024-05-13 | 0.5 |
| CodeMonkey | openai | claude-sonnet-4-20250514 | 0.0 |
| CodeMonkey.code_review | openai | claude-3-5-sonnet-20240620 | 0.0 |
| CodeMonkey.implement_changes | relace | relace-code-merge | 0.0 |
| CodeMonkey.describe_files | openai | gpt-4o-mini-2024-07-18 | 0.0 |
| Frontend | openai | claude-sonnet-4-20250514 | 0.0 |
| SpecWriter | openai | claude-sonnet-4-20250514 | 0.0 |

Notable configurations:
- **Relace integration**: Uses custom Relace API for code merging operations [cloud/config-docker.json:47-49]()
- **Cost optimization**: gpt-4o-mini for simple file description tasks [cloud/config-docker.json:51-55]()
- **Zero temperature**: Deterministic output for code generation agents [cloud/config-docker.json:39]()

### Database Configuration

Cloud deployments use SQLite with async support:

```json
{
  "db": {
    "url": "sqlite+aiosqlite:///data/database/pythagora.db",
    "debug_sql": false,
    "save_llm_requests": false
  }
}
```

Key settings:
- **Async SQLite**: Uses `aiosqlite` driver for non-blocking I/O [cloud/config-docker.json:118]()
- **LLM request logging disabled**: Reduces storage overhead in production [cloud/config-docker.json:120]()
- **Relative path**: Database stored in `data/database/` directory [cloud/config-docker.json:118]()

### File System Configuration

```json
{
  "fs": {
    "type": "local",
    "workspace_root": "/pythagora/pythagora-core/workspace",
    "ignore_paths": [
      ".git", ".gpt-pilot", ".idea", ".vscode", ".next",
      "node_modules", "venv", "dist", "build", "*.min.js"
    ],
    "ignore_size_threshold": 50000
  }
}
```

The workspace root is set to a dedicated directory within the container, and common development artifacts are excluded from file system operations to optimize context filtering.

**Sources:** [cloud/config-docker.json:1-154]()

---

## PostHog Analytics Integration

The cloud deployment integrates PostHog analytics to track usage metrics and user behavior. Analytics are injected directly into the code-server web interface.

### Analytics Injection Process

```mermaid
graph LR
    Dockerfile["Dockerfile<br/>Build Process"]
    PostHogHTML["cloud/posthog.html<br/>Script Template"]
    WorkbenchHTML["workbench.html<br/>Code-Server UI"]
    ServerMainJS["server-main.js<br/>CSP Configuration"]
    
    Dockerfile -->|"sed -i inject"| WorkbenchHTML
    PostHogHTML -->|"Script Content"| WorkbenchHTML
    Dockerfile -->|"sed -i modify CSP"| ServerMainJS
    
    WorkbenchHTML -.->|"Loads in Browser"| Analytics["PostHog Analytics<br/>us.i.posthog.com"]
```

### Content Security Policy Modification

The Dockerfile modifies code-server's Content Security Policy to allow PostHog script loading:

```bash
sed -i "s|'sha256-/r7rqQ+yrxt57sxLuQ6AMYcy/lUpvAIzHjIJt/OeLWU=' ;|'sha256-/r7rqQ+yrxt57sxLuQ6AMYcy/lUpvAIzHjIJt/OeLWU=' https://us-assets.i.posthog.com ;|g" \
  /usr/local/lib/code-server/lib/vscode/out/server-main.js
```

This adds `https://us-assets.i.posthog.com` to the script-src CSP directive, enabling the PostHog SDK to load.

### Analytics Script Injection

The PostHog initialization script is injected into the workbench HTML:

```bash
sed -i '/<head>/r /tmp/posthog.html' \
  /usr/local/lib/code-server/lib/vscode/out/vs/code/browser/workbench/workbench.html
```

### PostHog Configuration

The analytics script at [`cloud/posthog.html`](cloud/posthog.html:1-8) initializes PostHog with these settings:

| Setting | Value | Purpose |
|---------|-------|---------|
| Project API Key | `phc_CPMrohXQJiasSs2PCwK3SItm1mUT6F69dcLo1TMZOz8` | Identifies the Pythagora project |
| API Host | `https://us.i.posthog.com` | US-based PostHog instance |
| Defaults | `2025-05-24` | Feature flag defaults version |
| Person Profiles | `identified_only` | Only track identified users |

The `person_profiles: 'identified_only'` setting ensures anonymous usage is not tracked, only authenticated/identified cloud users generate profile data.

**Sources:** [Dockerfile:78-83](), [cloud/posthog.html:1-8]()

---

## Cloud API Authentication

Cloud deployments authenticate with Pythagora's cloud services using access tokens. This is primarily used for the Relace code merge API.

### Relace Client Authentication

The [`RelaceClient`](core/llm/relace_client.py:14-62) implements cloud API authentication:

```python
self.headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {self.state_manager.get_access_token() if self.state_manager.get_access_token() is not None else self.config.api_key if self.config.api_key is not None else ''}",
}
```

### Authentication Priority

The authorization header construction follows this priority:

```mermaid
graph TD
    Start["Build Authorization Header"]
    CheckStateManager{"state_manager.<br/>get_access_token()"}
    CheckConfig{"config.api_key"}
    UseAccessToken["Use access_token<br/>from StateManager"]
    UseConfigKey["Use api_key<br/>from Config"]
    UseEmpty["Use empty string<br/>(Anonymous)"]
    
    Start --> CheckStateManager
    CheckStateManager -->|"not None"| UseAccessToken
    CheckStateManager -->|"None"| CheckConfig
    CheckConfig -->|"not None"| UseConfigKey
    CheckConfig -->|"None"| UseEmpty
    
    UseAccessToken --> End["Bearer {token}"]
    UseConfigKey --> End
    UseEmpty --> End
```

### API Request Flow

The Relace API is used for code merging operations:

```python
async def _make_request(self, convo: Convo, ...):
    data = {
        "initialCode": convo.messages[0]["content"]["initialCode"],
        "editSnippet": convo.messages[0]["content"]["editSnippet"],
        "model": self.config.model,
    }
    
    response = await client.post(
        "https://api.pythagora.io/v1/relace/merge",
        headers=self.headers,
        json=data
    )
```

The API endpoint `https://api.pythagora.io/v1/relace/merge` receives:
- **initialCode**: The current code content
- **editSnippet**: The code changes to merge
- **model**: The Relace model identifier (e.g., `relace-code-merge`)

### Fallback Behavior

If the Relace API request fails, the client returns empty content and zero token counts:

```python
except Exception as e:
    log.debug(f"Relace API request failed: {e}")
    return ("", 0, 0)
```

This allows the system to gracefully fall back to other LLM providers when the cloud API is unavailable.

**Sources:** [core/llm/relace_client.py:14-62](), [cloud/config-docker.json:47-49]()

---

## Multi-Architecture Support

The cloud deployment supports both AMD64 and ARM64 architectures using Docker BuildKit's multi-platform build capabilities.

### Architecture Detection

The Dockerfile uses build arguments to detect target platform:

```dockerfile
ARG TARGETPLATFORM
ARG BUILDPLATFORM
ENV TARGETPLATFORM=${TARGETPLATFORM:-linux/amd64}
```

### Platform-Specific Dependency Installation

The [`setup-dependencies.sh`](cloud/setup-dependencies.sh:1-137) script adapts dependency installation based on architecture:

**MongoDB Installation**

```bash
case "$TARGETPLATFORM" in
    "linux/amd64")
        MONGO_ARCH="amd64"
        ;;
    "linux/arm64"|"linux/arm64/v8")
        MONGO_ARCH="arm64"
        ;;
    *)
        echo "Using default architecture amd64 for MongoDB"
        MONGO_ARCH="amd64"
        ;;
esac
```

**Code-Server Installation**

```bash
case "$TARGETPLATFORM" in
    "linux/amd64")
        PLATFORM="amd64"
        ;;
    "linux/arm64"|"linux/arm64/v8")
        PLATFORM="arm64"
        ;;
    *)
        echo "Using default platform amd64 for code-server"
        PLATFORM="amd64"
        ;;
esac

DOWNLOAD_URL="https://github.com/coder/code-server/releases/download/v${VERSION}/code-server-${VERSION}-linux-${PLATFORM}.tar.gz"
```

### Architecture-Specific Components

| Component | AMD64 Binary | ARM64 Binary | Version |
|-----------|-------------|--------------|---------|
| MongoDB | `amd64` | `arm64` | 6.0 [cloud/setup-dependencies.sh:78-80]() |
| code-server | `linux-amd64.tar.gz` | `linux-arm64.tar.gz` | 4.97.2 [cloud/setup-dependencies.sh:86-102]() |

### Certificate Management Workaround

The setup script includes a workaround for problematic certificate updates in multi-arch builds:

```bash
# Create dummy update-ca-certificates script
mv /usr/sbin/update-ca-certificates /usr/sbin/update-ca-certificates.orig
cat > /usr/sbin/update-ca-certificates << 'EOF'
#!/bin/sh
echo "Dummy update-ca-certificates called, doing nothing"
exit 0
EOF
chmod +x /usr/sbin/update-ca-certificates
```

This prevents build failures related to ca-certificates updates that can occur in emulated ARM64 builds. The original script is restored after package installation completes.

**Sources:** [Dockerfile:4-10](), [cloud/setup-dependencies.sh:8-136]()

---

## Port Exposure and Service Access

The cloud container exposes multiple ports for different services:

| Port | Service | Purpose |
|------|---------|---------|
| 8080 | code-server | Browser-based VSCode IDE |
| 8000 | Application | Backend API server (user projects) |
| 5173 | Vite | Frontend development server (Vite projects) |
| 3000 | Node | Node.js application server |
| 27017 | MongoDB | Database (currently unused, commented out) |

```dockerfile
EXPOSE 27017 8000 8080 5173 3000
```

### Primary Access Point

The main entry point for cloud deployments is port 8080, which serves the code-server web interface. Users access GPT Pilot through their browser at `http://<cloud-host>:8080`, which provides:
- Full VSCode-like IDE experience
- Integrated Pythagora extension
- Terminal access to run GPT Pilot
- File system browser for workspace management

### User and Permissions

The container creates a dedicated user for running services:

```dockerfile
RUN groupadd -g 1000 devusergroup && \
    useradd -m -u 1000 -g devusergroup -s /bin/bash devuser && \
    echo "devuser:devuser" | chpasswd && \
    adduser devuser sudo && \
    echo "devuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
```

Key aspects:
- **UID/GID 1000**: Standard non-root user ID
- **Sudo access**: Full sudo privileges without password
- **Shell**: bash for interactive terminal use
- **Default password**: `devuser` (should be changed in production)

**Sources:** [Dockerfile:46-54](), [Dockerfile:49-54]()

---

# Page: Continuous Integration

# Continuous Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/ci.yml](.github/workflows/ci.yml)
- [CHANGELOG.md](CHANGELOG.md)
- [README.md](README.md)
- [pyproject.toml](pyproject.toml)
- [requirements.txt](requirements.txt)

</details>



## Purpose and Scope

This document describes the continuous integration (CI) pipeline for GPT Pilot, which automatically validates code quality and functionality on every push and pull request. The CI system uses GitHub Actions to run tests, linters, and code style checks across multiple Python versions and operating systems to ensure cross-platform compatibility.

For information about deployment and running GPT Pilot in production environments, see [Docker Environment](#8.1) and [Cloud Deployment](#8.2).

---

## GitHub Actions Workflow

GPT Pilot uses GitHub Actions to automate testing and quality assurance. The CI pipeline is defined in [.github/workflows/ci.yml:1-36]() and executes on every push to the `main` branch and on pull requests targeting `main` or `rewrite` branches.

### Workflow Configuration

```mermaid
graph TB
    Trigger["Trigger: Push/PR"] --> Matrix["Matrix Strategy"]
    Matrix --> Python39Ubuntu["Python 3.9<br/>Ubuntu"]
    Matrix --> Python39macOS["Python 3.9<br/>macOS"]
    Matrix --> Python39Windows["Python 3.9<br/>Windows"]
    Matrix --> Python312Ubuntu["Python 3.12<br/>Ubuntu"]
    Matrix --> Python312macOS["Python 3.12<br/>macOS"]
    Matrix --> Python312Windows["Python 3.12<br/>Windows"]
    
    Python39Ubuntu --> Checkout["Checkout Code"]
    Python39macOS --> Checkout
    Python39Windows --> Checkout
    Python312Ubuntu --> Checkout
    Python312macOS --> Checkout
    Python312Windows --> Checkout
    
    Checkout --> SetupPython["Setup Python<br/>uses: actions/setup-python@v4"]
    SetupPython --> InstallDeps["Install Dependencies<br/>poetry install --with=dev"]
    InstallDeps --> Lint["Lint with Ruff<br/>poetry run ruff check"]
    Lint --> Format["Check Code Style<br/>poetry run ruff format --check"]
    Format --> Test["Run Tests<br/>poetry run pytest"]
    Test --> Complete["Job Complete"]
```

**Matrix Build Strategy**

The workflow employs a matrix strategy to test across:

| Dimension | Values |
|-----------|--------|
| Python Versions | 3.9, 3.12 |
| Operating Systems | ubuntu-latest, macos-latest, windows-latest |
| Total Combinations | 6 parallel jobs |

This matrix ensures GPT Pilot functions correctly across the minimum supported Python version (3.9) and a recent version (3.12), on all major operating systems.

**Sources:** [.github/workflows/ci.yml:12-18]()

### Workflow Steps

The CI pipeline executes the following steps in order:

1. **Checkout Code**: Uses `actions/checkout@v4` to clone the repository [.github/workflows/ci.yml:21]()
2. **Setup Python**: Installs the specified Python version using `actions/setup-python@v4` [.github/workflows/ci.yml:22-25]()
3. **Install Dependencies**: Uses Poetry to install all dependencies including dev dependencies [.github/workflows/ci.yml:26-29]()
4. **Lint with Ruff**: Runs `ruff check` with GitHub output format for inline PR comments [.github/workflows/ci.yml:30-31]()
5. **Code Style Check**: Runs `ruff format --check --diff` to verify formatting [.github/workflows/ci.yml:32-33]()
6. **Test with Pytest**: Executes the test suite using `pytest` [.github/workflows/ci.yml:34-35]()

The workflow has a 10-minute timeout and uses `fail-fast: false` to ensure all matrix jobs complete even if one fails [.github/workflows/ci.yml:13-15]().

**Sources:** [.github/workflows/ci.yml:20-35]()

---

## Dependency Management with Poetry

GPT Pilot uses Poetry for dependency management and virtual environment creation. The CI workflow installs Poetry globally, then uses it to install project dependencies.

### Dependency Installation

```mermaid
graph LR
    Poetry["poetry install --with=dev"] --> Core["Core Dependencies<br/>pyproject.toml:26-42"]
    Poetry --> Dev["Dev Dependencies<br/>pyproject.toml:44-50"]
    
    Core --> Runtime["Runtime Packages<br/>openai, anthropic, groq<br/>sqlalchemy, jinja2, etc"]
    Dev --> Testing["Testing Tools<br/>pytest, pytest-cov<br/>pytest-asyncio, pytest-timeout"]
    Dev --> Linting["Linting Tools<br/>ruff"]
    Dev --> Hooks["Pre-commit Hooks<br/>pre-commit"]
```

**Core Dependencies** [pyproject.toml:26-42]():
- **LLM Clients**: `openai`, `anthropic`, `groq` for AI model integration
- **Database**: `sqlalchemy`, `aiosqlite` for persistence
- **Templating**: `jinja2` for prompt engineering
- **Utilities**: `tiktoken` (token counting), `httpx` (HTTP client), `tenacity` (retry logic)

**Development Dependencies** [pyproject.toml:44-50]():
- **pytest**: Test framework with async support
- **pytest-cov**: Coverage reporting
- **pytest-timeout**: Test timeout enforcement
- **ruff**: Fast Python linter and formatter
- **pre-commit**: Git hook framework

**Sources:** [pyproject.toml:26-50](), [.github/workflows/ci.yml:26-29]()

---

## Testing Strategy

The test suite uses `pytest` with several plugins to provide comprehensive testing coverage.

### Pytest Configuration

The pytest configuration is defined in [pyproject.toml:52-54]():

```ini
[tool.pytest.ini_options]
addopts = "-ra -q --cov=core --no-cov-on-fail --timeout 10"
pythonpath = ["."]
```

**Configuration Breakdown**

| Option | Purpose |
|--------|---------|
| `-ra` | Show extra test summary info for all test outcomes except passed |
| `-q` | Quiet mode - less verbose output |
| `--cov=core` | Measure code coverage for the `core` package |
| `--no-cov-on-fail` | Don't report coverage if tests fail |
| `--timeout 10` | Fail tests that exceed 10 seconds |
| `pythonpath = ["."]` | Add project root to Python path |

### Coverage Configuration

Coverage reporting is configured to exclude certain code patterns [pyproject.toml:56-58]():

```ini
[tool.coverage.report]
exclude_lines = ["if TYPE_CHECKING:", "raise NotImplementedError()"]
omit = ["core/db/migrations/*", "core/templates/tpl/*"]
```

**Exclusions:**
- **TYPE_CHECKING blocks**: Import statements only used for type hints
- **NotImplementedError**: Abstract method placeholders
- **Database migrations**: Auto-generated code in `core/db/migrations/`
- **Templates**: Static template files in `core/templates/tpl/`

**Sources:** [pyproject.toml:52-58]()

### Test Execution Flow

```mermaid
graph TB
    Pytest["pytest command"] --> Discovery["Test Discovery<br/>Find test_*.py files"]
    Discovery --> Setup["Test Setup<br/>Create fixtures"]
    Setup --> Execute["Execute Tests<br/>10s timeout per test"]
    Execute --> Coverage["Coverage Collection<br/>Track executed lines"]
    
    Execute --> Pass{Test<br/>Result?}
    Pass -->|Success| Report["Generate Coverage Report"]
    Pass -->|Failure| Skip["Skip Coverage Reporting<br/>--no-cov-on-fail"]
    
    Report --> Summary["Test Summary<br/>-ra option"]
    Skip --> Summary
    
    Summary --> Exit{All<br/>Passed?}
    Exit -->|Yes| Success["Exit 0"]
    Exit -->|No| Failure["Exit 1"]
```

**Sources:** [pyproject.toml:52-58](), [.github/workflows/ci.yml:34-35]()

---

## Code Quality with Ruff

Ruff is a fast Python linter and formatter written in Rust. The CI pipeline uses Ruff for both linting (detecting code issues) and formatting (ensuring consistent style).

### Ruff Configuration

[pyproject.toml:60-64]() defines the Ruff configuration:

```ini
[tool.ruff]
line-length = 120
indent-width = 4
target-version = "py39"
lint.extend-select = ["I"]
```

**Configuration Parameters:**

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `line-length` | 120 | Maximum characters per line |
| `indent-width` | 4 | Number of spaces for indentation |
| `target-version` | "py39" | Minimum Python version compatibility |
| `lint.extend-select` | ["I"] | Enable import sorting checks |

### Linting Pipeline

```mermaid
graph TB
    Code["Source Code<br/>core/**/*.py"] --> RuffCheck["ruff check<br/>--output-format github"]
    Code --> RuffFormat["ruff format<br/>--check --diff"]
    
    RuffCheck --> Issues{Issues<br/>Found?}
    Issues -->|Yes| PRComments["Inline PR Comments<br/>GitHub format"]
    Issues -->|No| CheckStyle["Style Check"]
    
    RuffFormat --> StyleIssues{Formatting<br/>Issues?}
    StyleIssues -->|Yes| ShowDiff["Display Differences<br/>--diff flag"]
    StyleIssues -->|No| Success["All Checks Pass"]
    
    PRComments --> Fail["CI Fails"]
    ShowDiff --> Fail
    CheckStyle --> StyleIssues
```

**Linting Phase** [.github/workflows/ci.yml:30-31]():
- Runs `poetry run ruff check --output-format github`
- GitHub format enables inline comments on pull requests
- Detects code issues like unused imports, undefined variables, complexity issues

**Formatting Phase** [.github/workflows/ci.yml:32-33]():
- Runs `poetry run ruff format --check --diff`
- `--check` flag causes failure if formatting is needed
- `--diff` flag displays what changes would be made
- Does not modify files, only validates formatting

**Sources:** [pyproject.toml:60-64](), [.github/workflows/ci.yml:30-33]()

---

## Multi-Platform Support

The CI workflow ensures GPT Pilot works consistently across all major operating systems.

### Platform Matrix

```mermaid
graph TB
    subgraph "Operating Systems"
        Ubuntu["ubuntu-latest<br/>Primary Linux platform"]
        macOS["macos-latest<br/>Darwin/BSD compatibility"]
        Windows["windows-latest<br/>Windows-specific paths"]
    end
    
    subgraph "Python Versions"
        Py39["Python 3.9<br/>Minimum supported"]
        Py312["Python 3.12<br/>Current stable"]
    end
    
    subgraph "Test Coverage"
        Ubuntu --> FileSystem["File System Ops<br/>Path separators"]
        macOS --> FileSystem
        Windows --> FileSystem
        
        Py39 --> Syntax["Language Features<br/>3.9+ compatibility"]
        Py312 --> Syntax
        
        FileSystem --> Database["Database Tests<br/>SQLite/PostgreSQL"]
        Syntax --> Database
        
        Database --> LLMClients["LLM Client Tests<br/>HTTP/API calls"]
    end
```

**Platform-Specific Considerations:**

| Platform | Considerations |
|----------|----------------|
| **Ubuntu** | Primary development/deployment platform; Unix paths |
| **macOS** | BSD-based filesystem; case-sensitive vs case-insensitive HFS+ |
| **Windows** | Backslash path separators; case-insensitive NTFS |

**Python Version Support:**
- **3.9**: Minimum version as specified in [pyproject.toml:27]()
- **3.12**: Tests forward compatibility with recent Python features

The `fail-fast: false` setting [.github/workflows/ci.yml:15]() ensures all platform combinations run even if one fails, providing complete visibility into platform-specific issues.

**Sources:** [.github/workflows/ci.yml:12-18](), [pyproject.toml:27]()

---

## Pre-commit Hooks

GPT Pilot includes `pre-commit` in its development dependencies [pyproject.toml:50](), enabling developers to run the same checks locally before pushing code.

### Local Development Workflow

```mermaid
graph TB
    Developer["Developer<br/>Writes Code"] --> Stage["git add<br/>Stage Changes"]
    Stage --> Commit["git commit<br/>Trigger Pre-commit"]
    
    Commit --> PreCommit["pre-commit run"]
    PreCommit --> Ruff["Ruff Check<br/>Same as CI"]
    PreCommit --> Format["Ruff Format<br/>Same as CI"]
    PreCommit --> CustomHooks["Other Hooks<br/>(if configured)"]
    
    Ruff --> Passed{All<br/>Passed?}
    Format --> Passed
    CustomHooks --> Passed
    
    Passed -->|Yes| CommitSuccess["Commit Succeeds"]
    Passed -->|No| FixCode["Fix Issues<br/>Re-stage Files"]
    
    FixCode --> Stage
    CommitSuccess --> Push["git push"]
    Push --> CIWorkflow["GitHub Actions CI<br/>Same checks in CI"]
```

While the repository includes `pre-commit` as a dependency, individual hook configurations would be defined in a `.pre-commit-config.yaml` file (not shown in provided files). This allows developers to catch issues before the CI pipeline runs, reducing feedback time.

**Sources:** [pyproject.toml:50]()

---

## CI Workflow Execution Summary

### Complete Pipeline Flow

```mermaid
graph TB
    Push["git push / Pull Request"] --> Trigger["Workflow Trigger<br/>ci.yml"]
    
    Trigger --> MatrixSetup["Matrix Strategy Setup<br/>6 parallel jobs"]
    
    MatrixSetup --> Job1["ubuntu-latest<br/>Python 3.9"]
    MatrixSetup --> Job2["ubuntu-latest<br/>Python 3.12"]
    MatrixSetup --> Job3["macos-latest<br/>Python 3.9"]
    MatrixSetup --> Job4["macos-latest<br/>Python 3.12"]
    MatrixSetup --> Job5["windows-latest<br/>Python 3.9"]
    MatrixSetup --> Job6["windows-latest<br/>Python 3.12"]
    
    Job1 --> Steps["1. Checkout<br/>2. Setup Python<br/>3. Install deps<br/>4. Ruff lint<br/>5. Ruff format<br/>6. Pytest"]
    Job2 --> Steps
    Job3 --> Steps
    Job4 --> Steps
    Job5 --> Steps
    Job6 --> Steps
    
    Steps --> Results{All Jobs<br/>Pass?}
    Results -->|Yes| MergeReady["✓ Ready to Merge"]
    Results -->|No| ReviewFail["✗ Review Failures"]
    
    ReviewFail --> FixIssues["Developer Fixes Issues"]
    FixIssues --> Push
```

### Timeout and Failure Handling

The workflow implements multiple levels of timeout protection:

1. **Job-level timeout**: 10 minutes maximum [.github/workflows/ci.yml:13]()
2. **Test-level timeout**: 10 seconds per test [pyproject.toml:53]()
3. **Fail-fast disabled**: All matrix jobs complete even if one fails [.github/workflows/ci.yml:15]()

This configuration ensures:
- Long-running tests are caught and failed quickly
- Entire workflow doesn't hang indefinitely
- Complete visibility into which platform/Python combinations fail

**Sources:** [.github/workflows/ci.yml:13-15](), [pyproject.toml:53]()

---

## Integration with Development Workflow

The CI pipeline integrates with the broader development workflow described in [Development Workflow](#6).

### CI Touchpoints

| Development Phase | CI Role |
|-------------------|---------|
| **Code Generation** | Validates generated code compiles and runs |
| **Agent Implementation** | Tests agent logic and LLM interactions |
| **State Management** | Verifies transaction model and persistence |
| **File Operations** | Tests VFS operations across platforms |
| **Template Application** | Validates template installation and structure |

The CI system acts as a safety net, ensuring that:
- Agent-generated code meets quality standards
- Cross-platform compatibility is maintained
- State management transactions are atomic
- LLM integrations handle errors gracefully

**Sources:** [.github/workflows/ci.yml:1-36](), [pyproject.toml:26-64]()