# Page: Introduction to Plandex

# Introduction to Plandex

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/docs/cli-reference.md](docs/docs/cli-reference.md)
- [docs/docs/environment-variables.md](docs/docs/environment-variables.md)
- [docs/docs/hosting/cloud.md](docs/docs/hosting/cloud.md)
- [docs/docs/hosting/self-hosting/_category_.json](docs/docs/hosting/self-hosting/_category_.json)
- [docs/docs/hosting/self-hosting/advanced-self-hosting.md](docs/docs/hosting/self-hosting/advanced-self-hosting.md)
- [docs/docs/hosting/self-hosting/local-mode-quickstart.md](docs/docs/hosting/self-hosting/local-mode-quickstart.md)
- [docs/docs/install.md](docs/docs/install.md)
- [docs/docs/models/claude-subscription.md](docs/docs/models/claude-subscription.md)
- [docs/docs/models/models-overview.md](docs/docs/models/models-overview.md)
- [docs/docs/quick-start.md](docs/docs/quick-start.md)

</details>



## Purpose and Scope

This document provides a comprehensive introduction to Plandex, an AI-powered coding agent designed for large-scale software development tasks. It covers the system's core architecture, fundamental concepts, and key components to help developers understand how Plandex operates and integrates into development workflows.

For detailed CLI command reference, see [CLI Reference](#2). For specific configuration and setup instructions, see [Installation and Quick Start](#1.1). For in-depth technical implementation details, see [System Architecture Overview](#1.3).

## What is Plandex

Plandex is a terminal-based AI development tool that can plan and execute large coding tasks spanning multiple steps and files. It operates through a client-server architecture where the CLI client communicates with a server that orchestrates AI model interactions, file operations, and plan execution.

The system is designed to handle projects with up to 2M tokens of context directly and can index directories with 20M+ tokens using tree-sitter project maps. It maintains AI-generated changes in a sandbox environment separate from project files until they are ready to be applied.

**Sources:** [README.md:81-90](), [README.md:65-66](), [README.md:83-84]()

## System Architecture Overview

Plandex follows a layered client-server architecture with distinct responsibilities for user interaction, plan execution, AI integration, and data persistence.

```mermaid
graph TB
    subgraph "Client Layer"
        CLI["plandex CLI"]
        REPL["Interactive REPL"]
        StreamUI["Real-time Stream UI"]
        TUI["Terminal UI Components"]
    end
    
    subgraph "Server Layer"
        HTTPServer["HTTP API Server"]
        PlanEngine["Plan Execution Engine"]
        ModelClient["AI Model Client"]
        BuildSystem["File Build System"]
        SyntaxEngine["Syntax & Validation"]
    end
    
    subgraph "AI Providers"
        OpenAI["OpenAI API"]
        Anthropic["Anthropic API"]
        Google["Google AI Studio"]
        OpenRouter["OpenRouter.ai"]
        Ollama["Local Ollama"]
    end
    
    subgraph "Storage"
        PostgreSQL[("PostgreSQL Database")]
        GitRepos[("Git Repositories")]
        FileSystem[("Local File System")]
    end
    
    CLI --> HTTPServer
    REPL --> CLI
    StreamUI --> CLI
    TUI --> CLI
    
    HTTPServer --> PlanEngine
    PlanEngine --> ModelClient
    PlanEngine --> BuildSystem
    BuildSystem --> SyntaxEngine
    
    ModelClient --> OpenAI
    ModelClient --> Anthropic
    ModelClient --> Google
    ModelClient --> OpenRouter
    ModelClient --> Ollama
    
    HTTPServer --> PostgreSQL
    PlanEngine --> GitRepos
    BuildSystem --> FileSystem
```

The architecture separates concerns between user interaction (Client Layer), business logic (Server Layer), external AI services (AI Providers), and data persistence (Storage). The CLI provides multiple interfaces including an interactive REPL and streaming UI for real-time feedback during plan execution.

**Sources:** [README.md:121-124](), [docs/docs/cli-reference.md:34-46](), [docs/docs/hosting/self-hosting/local-mode-quickstart.md:8]()

## Core Components

The following diagram shows the key components and their relationships within the Plandex system:

```mermaid
graph TB
    subgraph "User Interface"
        plandex_cmd["plandex command"]
        pdx_alias["pdx alias"]
        repl_mode["REPL mode"]
        chat_mode["chat mode"]
        tell_mode["tell mode"]
    end
    
    subgraph "Plan Management"
        new_cmd["new command"]
        plans_cmd["plans command"]
        current_cmd["current command"]
        cd_cmd["cd command"]
        branches_cmd["branches command"]
        checkout_cmd["checkout command"]
    end
    
    subgraph "Context Operations"
        load_cmd["load command"]
        ls_cmd["ls command"]
        rm_cmd["rm command"]
        update_cmd["update command"]
        clear_cmd["clear command"]
    end
    
    subgraph "Execution Control"
        tell_cmd["tell command"]
        continue_cmd["continue command"]
        build_cmd["build command"]
        apply_cmd["apply command"]
        debug_cmd["debug command"]
    end
    
    subgraph "Model Configuration"
        models_cmd["models command"]
        set_model_cmd["set-model command"]
        model_packs_cmd["model-packs command"]
        providers_cmd["providers command"]
    end
    
    subgraph "Changes Management"
        diff_cmd["diff command"]
        reject_cmd["reject command"]
        log_cmd["log command"]
        rewind_cmd["rewind command"]
    end
    
    plandex_cmd --> repl_mode
    pdx_alias --> repl_mode
    repl_mode --> chat_mode
    repl_mode --> tell_mode
    
    repl_mode --> Plan Management
    repl_mode --> Context Operations
    repl_mode --> Execution Control
    repl_mode --> Model Configuration
    repl_mode --> Changes Management
```

### Key Component Descriptions

- **CLI Entry Points**: The `plandex` command and `pdx` alias serve as the primary entry points to the system
- **REPL Mode**: Interactive shell providing fuzzy auto-complete and command processing
- **Plan Management**: Commands for creating, listing, and switching between plans and branches
- **Context Operations**: File and directory loading, listing, and management within plan context
- **Execution Control**: Core workflow commands for implementing tasks and applying changes
- **Model Configuration**: Settings and management for AI models and providers
- **Changes Management**: Review, diff, and version control operations for pending changes

**Sources:** [docs/docs/cli-reference.md:10-15](), [docs/docs/cli-reference.md:34-46](), [docs/docs/cli-reference.md:80-210](), [docs/docs/cli-reference.md:212-292](), [docs/docs/cli-reference.md:294-433]()

## Key Concepts

### Plans and Branches
Plans are the fundamental unit of work in Plandex, representing a conversation and associated context for a specific task. Each plan can have multiple branches, similar to Git branches, allowing exploration of different implementation approaches.

Plans maintain their own conversation history, context files, and pending changes. The `current` command shows the active plan, while `plans` lists all available plans with their status and token counts.

### Context Management
Context refers to the files, directories, notes, and other information loaded into a plan to provide the AI with necessary background. Context can include:
- Source code files loaded via the `load` command
- Directory structures and file maps using `--tree` and `--map` flags
- URLs, images, and notes
- Piped command output

The system automatically manages context freshness and can auto-load relevant files during execution.

### Model Packs and Roles
Plandex uses specialized AI models for different roles in the development process:
- **Planner**: Creates high-level implementation plans
- **Architect**: Designs system structure and file organization  
- **Coder**: Implements specific code changes
- **Builder**: Processes and validates file modifications
- **Validator**: Ensures syntax and logical correctness
- **Namer**: Generates appropriate names for plans and files

Model packs group these role assignments into coherent configurations like `daily`, `strong`, `cheap`, and `oss` (open source).

### Plan Lifecycle
The typical workflow follows a `tell` → `build` → `apply` cycle:
1. **Tell**: Describe the task or feature to implement
2. **Build**: Generate and validate specific file changes
3. **Apply**: Write changes to the local file system

Plans can be paused, resumed, rewound to previous states, and branches can be created for alternative approaches.

**Sources:** [docs/docs/cli-reference.md:80-124](), [docs/docs/cli-reference.md:212-292](), [docs/docs/cli-reference.md:295-370](), [docs/docs/cli-reference.md:675-690](), [README.md:102-118]()

## Workflow Overview

The following diagram illustrates the typical development workflow using Plandex:

```mermaid
flowchart TD
    start["Start plandex in project directory"]
    chat_mode["Chat mode - explore ideas"]
    tell_mode["Tell mode - describe task"]
    context_load["Load relevant context"]
    plan_execution["AI generates plan"]
    build_changes["Build file changes"]
    review_diff["Review diff output"]
    apply_changes["Apply changes to files"]
    execute_commands["Execute commands (tests, builds)"]
    debug_cycle["Auto-debug failures"]
    commit_git["Commit to git"]
    
    start --> chat_mode
    chat_mode --> tell_mode
    tell_mode --> context_load
    context_load --> plan_execution
    plan_execution --> build_changes
    build_changes --> review_diff
    review_diff --> apply_changes
    apply_changes --> execute_commands
    execute_commands --> debug_cycle
    debug_cycle --> commit_git
    
    review_diff -.-> tell_mode
    debug_cycle -.-> plan_execution
    execute_commands -.-> commit_git
```

The workflow supports both fully automated execution and step-by-step manual control through configurable autonomy levels ranging from `none` (manual) to `full` (automatic apply and execution).

**Sources:** [README.md:128-131](), [docs/docs/cli-reference.md:48-63](), [docs/docs/cli-reference.md:295-370](), [docs/docs/cli-reference.md:371-401]()

## Hosting and Deployment Options

Plandex supports multiple deployment configurations:

| Option | Description |
|--------|-------------|
| **Plandex Cloud (Integrated)** | Hosted service with built-in model credits |
| **Plandex Cloud (BYO Key)** | Hosted service using your API keys |
| **Self-hosted Local** | Local Docker deployment for single users |
| **Self-hosted Production** | Remote server deployment for multiple users |

Each option requires different setup procedures and has distinct authentication, billing, and model provider configurations.

**Sources:** [docs/docs/quick-start.md:18-25](), [docs/docs/hosting/cloud.md:13-33](), [docs/docs/hosting/self-hosting/local-mode-quickstart.md:10-51]()

## Next Steps

For hands-on experience with Plandex:
- Follow the [Installation and Quick Start](#1.1) guide to set up Plandex
- Review [Core Concepts](#1.2) for detailed explanations of plans, context, and model packs  
- Explore the [CLI Reference](#2) for comprehensive command documentation
- Learn about [Plan Execution System](#3) for understanding the workflow implementation
- See [AI Model Integration](#5) for configuring models and providers

For system administrators and developers:
- Review [System Architecture Overview](#1.3) for implementation details
- See [Self-Hosting Plandex](#7.3) for deployment guidance
- Explore [Development and Deployment](#7) for contribution guidelines

**Sources:** [README.md:178-207](), [docs/docs/quick-start.md:34-63](), [docs/docs/cli-reference.md:1-9]()

---

# Page: Installation and Quick Start

# Installation and Quick Start

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/docs/cli-reference.md](docs/docs/cli-reference.md)
- [docs/docs/environment-variables.md](docs/docs/environment-variables.md)
- [docs/docs/hosting/cloud.md](docs/docs/hosting/cloud.md)
- [docs/docs/hosting/self-hosting/_category_.json](docs/docs/hosting/self-hosting/_category_.json)
- [docs/docs/hosting/self-hosting/advanced-self-hosting.md](docs/docs/hosting/self-hosting/advanced-self-hosting.md)
- [docs/docs/hosting/self-hosting/local-mode-quickstart.md](docs/docs/hosting/self-hosting/local-mode-quickstart.md)
- [docs/docs/install.md](docs/docs/install.md)
- [docs/docs/models/claude-subscription.md](docs/docs/models/claude-subscription.md)
- [docs/docs/models/models-overview.md](docs/docs/models/models-overview.md)
- [docs/docs/quick-start.md](docs/docs/quick-start.md)

</details>



This guide walks you through installing the Plandex CLI and getting started with basic usage patterns. Plandex uses a client-server architecture where the CLI communicates with either Plandex Cloud or a self-hosted server to orchestrate AI-powered development tasks.

## Installation Methods

Plandex offers several installation methods to suit different needs and preferences.

### Quick Install

The fastest way to install Plandex is using the provided install script:

```bash
curl -sL https://plandex.ai/install.sh | bash
```

This script will download and install the appropriate binary for your system.

### Manual Install

Alternatively, you can manually download and install the binary:

1. Download the appropriate binary for your platform from the latest [release](https://github.com/plandex-ai/plandex/releases)
2. Place it somewhere in your `PATH`

### Build from Source

For those who prefer to build from source:

```bash
git clone https://github.com/plandex-ai/plandex.git
cd plandex/app/cli
go build -ldflags "-X plandex/version.Version=$(cat version.txt)"
mv plandex /usr/local/bin # adapt as needed for your system
```

### Platform Support

Plandex works on:
- Linux
- macOS
- Windows (via WSL only)

Note: On Windows, Plandex only works correctly in the WSL shell. It doesn't work in Windows CMD prompt or PowerShell.

Sources: [README.md:146-152](), [docs/docs/install.md:10-32]()

## Deployment Options

There are three primary ways to deploy and use Plandex:

```mermaid
flowchart TD
    Start["Deployment Options"] --> Cloud1["Plandex Cloud (Integrated Models)"]
    Start --> Cloud2["Plandex Cloud (BYO API Key)"]
    Start --> SelfHost["Self-hosted/Local Mode"]
    
    Cloud1 --> Features1["No separate accounts or API keys
                        Central billing and cost tracking
                        $10 trial with credits"]
                        
    Cloud2 --> Features2["Use your own API keys
                        OpenRouter.ai and OpenAI accounts required
                        Free trial up to 10 plans"]
                        
    SelfHost --> Features3["Run locally with Docker
                          Your own API keys
                          Complete control over deployment"]
                          
    Features1 -.-> Usage1["plandex sign-in
                         Select Plandex Cloud"]
                         
    Features2 -.-> Usage2["plandex sign-in
                         Set OPENROUTER_API_KEY
                         Set OPENAI_API_KEY"]
                         
    Features3 -.-> Usage3["Clone repository
                         ./start_local.sh
                         Set API keys"]
```

### 1. Plandex Cloud (Integrated Models)
- No separate accounts or API keys required
- Easy multi-device usage
- Centralized billing, budgeting, usage tracking, and cost reporting
- Start with a $10 trial (includes $10 in credits)
- After the trial, upgrade to a paid plan for $45 per month (includes $20 in credits that never expire)

### 2. Plandex Cloud (BYO API Key)
- Use Plandex Cloud with your own OpenRouter.ai and OpenAI keys
- Start with a free trial up to 10 plans and 20 model responses per plan
- After the trial, upgrade to a paid plan for $30 per month

### 3. Self-hosted/Local Mode
- Run Plandex locally with Docker or host on your own server
- Use your own OpenRouter.ai and OpenAI keys
- Complete control over your deployment environment
- Best for organizations with specific security requirements

Sources: [README.md:154-161](), [docs/docs/quick-start.md:19-24](), [docs/docs/hosting/cloud.md:10-34](), [docs/docs/hosting/self-hosting/local-mode-quickstart.md:1-8]()

## API Key Setup

If you're using the "BYO API Key" option with Plandex Cloud or self-hosting, you'll need to set up API keys for the AI model providers.

### OpenRouter.ai API Key
1. Sign up at [OpenRouter.ai](https://openrouter.ai/signup) if you don't have an account
2. Generate an API key at [OpenRouter.ai/keys](https://openrouter.ai/keys)
3. Set the environment variable:
   ```bash
   export OPENROUTER_API_KEY=<your-openrouter-api-key>
   ```

### OpenAI API Key
1. Sign up at [OpenAI Platform](https://platform.openai.com/signup) if you don't have an account
2. Generate an API key at [OpenAI API Keys](https://platform.openai.com/account/api-keys)
3. Set the environment variable:
   ```bash
   export OPENAI_API_KEY=<your-openai-api-key>
   ```

Sources: [README.md:163-169](), [docs/docs/quick-start.md:26-31](), [docs/docs/hosting/self-hosting/local-mode-quickstart.md:35-46]()

## Quick Start Guide

Once you've installed Plandex, follow these steps to start using it:

```mermaid
sequenceDiagram
    actor User
    participant CLI as "Plandex CLI"
    participant Server as "Plandex Server"
    participant AI as "AI Models"
    
    User->>CLI: cd your-project-dir
    Note over User,CLI: Optionally: git init
    User->>CLI: plandex (or pdx)
    CLI->>Server: Connect to server
    
    alt First-time use
        Server->>User: Authentication prompt
        User->>Server: Select Plandex Cloud or local mode
        
        alt Plandex Cloud
            Server->>User: Start trial prompt
            User->>Server: Confirm trial
        else Self-hosted
            Note over User,Server: API keys must be set
        end
    end
    
    CLI->>User: REPL starts in chat mode
    User->>CLI: Type prompt or command
    CLI->>Server: Send request
    Server->>AI: Generate response
    AI->>Server: Response
    Server->>CLI: Stream response
    CLI->>User: Display response
```

### Basic Steps

1. Change to your project directory:
   ```bash
   cd your-project-dir
   ```

2. Optionally initialize a git repository (if starting a new project):
   ```bash
   git init
   ```

3. Start the Plandex REPL:
   ```bash
   plandex
   ```
   or use the shorter alias:
   ```bash
   pdx
   ```

4. If using Plandex Cloud for the first time, you'll be prompted to start a trial.

5. The REPL starts in chat mode by default. You can ask questions about your project or discuss ideas.

6. To implement code changes, follow the prompts to switch to "tell mode".

### Using REPL Flags

You can customize your REPL experience with various flags:

```bash
# Start in tell mode for implementation
plandex --tell

# Set autonomy level
plandex --full     # Full automation
plandex --semi     # Semi-automation
plandex --basic    # Basic automation
plandex --no-auto  # No automation

# Choose model pack
plandex --daily      # Default balanced models
plandex --strong     # More capable models (higher cost)
plandex --cheap      # Less capable models (lower cost)
plandex --oss        # Open source models
```

Sources: [README.md:173-193](), [docs/docs/quick-start.md:33-61](), [docs/docs/cli-reference.md:34-53](), [docs/docs/repl.md:10-53]()

## Self-Hosting Setup

If you choose to self-host Plandex, there are several options available.

### Local Mode Quickstart

The easiest way to self-host Plandex is using the provided local mode script:

```mermaid
flowchart TD
    Start["Self-Hosting Setup"] --> Clone["1. Clone Repository
                                        git clone https://github.com/plandex-ai/plandex.git
                                        cd plandex/app"]
    Clone --> StartServer["2. Start Server
                          ./start_local.sh"]
    StartServer --> InstallCLI["3. Install Plandex CLI
                               curl -sL https://plandex.ai/install.sh | bash"]
    InstallCLI --> SignIn["4. Sign In
                          plandex sign-in
                          Select 'Local mode host'"]
    SignIn --> SetKeys["5. Set API Keys
                       export OPENROUTER_API_KEY=...
                       export OPENAI_API_KEY=..."]
    SetKeys --> StartPlandex["6. Start Using Plandex
                             cd your-project-dir
                             plandex"]
```

1. Clone the repository and start the local server:
   ```bash
   git clone https://github.com/plandex-ai/plandex.git
   cd plandex/app
   ./start_local.sh
   ```

2. In a new terminal, install the Plandex CLI if you haven't already:
   ```bash
   curl -sL https://plandex.ai/install.sh | bash
   ```

3. Sign in to the local server:
   ```bash
   plandex sign-in
   ```
   When prompted, select "Local mode host" and confirm the default host (`http://localhost:8099`).

4. Set up your API keys:
   ```bash
   export OPENROUTER_API_KEY=<your-openrouter-api-key>
   export OPENAI_API_KEY=<your-openai-api-key>
   ```

5. Start using Plandex in a project directory:
   ```bash
   cd your-project-dir
   plandex
   ```

### Docker Compose Configuration

The Docker Compose setup includes:

- PostgreSQL database container for data storage
- Plandex server container for the backend
- Shared network for communication
- Volumes for persistent data storage

The docker-compose.yml file configures both containers with appropriate environment variables and port mappings.

### Advanced Self-Hosting

For more complex deployments, Plandex supports running the server directly:

- Development or production mode (set via `GOENV` environment variable)
- Custom PostgreSQL database connection (via `DATABASE_URL`)
- Custom base directory for file storage (via `PLANDEX_BASE_DIR`)
- SMTP configuration for email in production mode
- Options to run from Docker or source code

See [Advanced Self-Hosting](#6.2) for more details.

Sources: [docs/docs/hosting/self-hosting/local-mode-quickstart.md:10-52](), [app/docker-compose.yml:1-38](), [app/start_local.sh:1-36](), [docs/docs/hosting/self-hosting/advanced-self-hosting.md:1-154]()

## Environment Variables

Here are the key environment variables that can be configured for Plandex:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | OpenRouter.ai API key | Required for BYO API Key mode |
| `OPENAI_API_KEY` | OpenAI API key | Required for BYO API Key mode |
| `PLANDEX_ENV` | Environment for development | Defaults to production |
| `PLANDEX_API_HOST` | Custom API host | `http://localhost:8099` in development, `https://api.plandex.ai` in production |
| `OPENAI_API_BASE` | Custom OpenAI server URL | Empty (uses OpenAI's default) |
| `OPENAI_ORG_ID` | OpenAI organization ID | Empty |
| `GOENV` | Server mode (development/production) | Required for self-hosting |
| `DATABASE_URL` | PostgreSQL connection string | Required for self-hosting |
| `PLANDEX_BASE_DIR` | Base directory for server files | `$HOME/plandex-server` (dev) or `/plandex-server` (prod) |

For a complete list of environment variables, see [Environment Variables](#11).

Sources: [docs/docs/environment-variables.md:10-97]()

## Next Steps

Now that you have Plandex installed and running, you can:

1. Explore the [CLI Reference](#3) to learn about all available commands
2. Learn more about the [Core Concepts](#1.2) to understand Plandex's capabilities
3. Set up [Context Management](#3.3) to help AI models understand your codebase
4. Configure [Model Settings](#5.1) to customize AI behavior

For help or feedback, you can join the [Discord community](https://discord.gg/plandex-ai) or check the [GitHub repository](https://github.com/plandex-ai/plandex).

---

# Page: Core Concepts

# Core Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/docs/cli-reference.md](docs/docs/cli-reference.md)
- [docs/docs/environment-variables.md](docs/docs/environment-variables.md)
- [docs/docs/hosting/cloud.md](docs/docs/hosting/cloud.md)
- [docs/docs/hosting/self-hosting/_category_.json](docs/docs/hosting/self-hosting/_category_.json)
- [docs/docs/hosting/self-hosting/advanced-self-hosting.md](docs/docs/hosting/self-hosting/advanced-self-hosting.md)
- [docs/docs/hosting/self-hosting/local-mode-quickstart.md](docs/docs/hosting/self-hosting/local-mode-quickstart.md)
- [docs/docs/install.md](docs/docs/install.md)
- [docs/docs/models/claude-subscription.md](docs/docs/models/claude-subscription.md)
- [docs/docs/models/models-overview.md](docs/docs/models/models-overview.md)
- [docs/docs/quick-start.md](docs/docs/quick-start.md)

</details>



This document explains the fundamental concepts that form the foundation of Plandex's AI-assisted development workflow. Understanding these concepts is essential for effectively using Plandex to plan and execute coding tasks.

For information about installing and getting started with Plandex, see [Installation and Quick Start](#1.1). For details about the overall system architecture, see [System Architecture Overview](#1.3). For comprehensive command reference, see [CLI Reference](#2).

## Plans and Plan Lifecycle

A **plan** is the central unit of work in Plandex. Each plan represents a specific coding task or feature implementation that progresses through a defined lifecycle of chat, implementation, building, and application phases.

```mermaid
graph LR
    Start["User starts plan"] --> Chat["Chat Mode<br/>plandex chat"]
    Chat --> Tell["Tell Mode<br/>plandex tell"]
    Tell --> Build["Build Phase<br/>plandex build"]
    Build --> Review["Review Changes<br/>plandex diff"]
    Review --> Apply["Apply Changes<br/>plandex apply"]
    Apply --> Complete["Plan Complete"]
    
    Chat --> Chat
    Tell --> Continue["Continue<br/>plandex continue"]
    Continue --> Tell
    Review --> Reject["Reject Changes<br/>plandex reject"]
    Reject --> Tell
```

### Plan States and Commands

Plans progress through distinct phases, each with associated CLI commands:

| Phase | Command | Purpose |
|-------|---------|---------|
| Chat | `plandex chat` | Discussion and exploration without making changes |
| Tell | `plandex tell` | Describe implementation tasks |
| Continue | `plandex continue` | Continue plan execution |
| Build | `plandex build` | Convert plan responses into file modifications |
| Apply | `plandex apply` | Write changes to project files |

**Sources:** [docs/docs/cli-reference.md:295-400](), [README.md:128-131]()

## Context Management

**Context** encompasses all information that Plandex uses to understand your project: files, directories, project structure, notes, images, and URLs. Effective context management is crucial for getting accurate results from AI models.

```mermaid
graph TB
    subgraph "Context Sources"
        Files["Files<br/>plandex load file.ts"]
        Dirs["Directories<br/>plandex load lib -r"]
        Trees["Directory Trees<br/>plandex load . --tree"]
        Maps["File Maps<br/>plandex load . --map"]
        URLs["URLs<br/>plandex load https://..."]
        Notes["Notes<br/>plandex load -n 'note text'"]
        Images["Images<br/>plandex load image.png"]
        Piped["Piped Data<br/>npm test | plandex load"]
    end
    
    subgraph "Context Operations"
        List["List Context<br/>plandex ls"]
        Show["Show Context<br/>plandex show"]
        Remove["Remove Context<br/>plandex rm"]
        Update["Update Context<br/>plandex update"]
        Clear["Clear All<br/>plandex clear"]
    end
    
    Files --> ContextDB["Context Database"]
    Dirs --> ContextDB
    Trees --> ContextDB
    Maps --> ContextDB
    URLs --> ContextDB
    Notes --> ContextDB
    Images --> ContextDB
    Piped --> ContextDB
    
    ContextDB --> List
    ContextDB --> Show
    ContextDB --> Remove
    ContextDB --> Update
    ContextDB --> Clear
```

### Context Types and Token Management

Plandex supports a 2M token effective context window and uses context caching to reduce costs and latency. Context is categorized by type and managed efficiently:

| Context Type | Command Example | Token Impact |
|--------------|-----------------|--------------|
| File content | `plandex load component.ts` | Full file tokens |
| Directory tree | `plandex load . --tree` | File names only |
| File map | `plandex load . --map` | Signatures and types |
| Notes | `plandex load -n "instructions"` | Note text tokens |
| Images | `plandex load mockup.png` | Vision model tokens |

**Sources:** [docs/docs/cli-reference.md:213-292](), [README.md:91-100]()

## AI Model Integration: Roles and Model Packs

Plandex uses specialized AI models for different aspects of development work. Each **role** handles specific responsibilities, and **model packs** define which models are assigned to each role.

```mermaid
graph TB
    subgraph "Model Roles"
        Planner["Planner Role<br/>Task planning and breakdown"]
        Architect["Architect Role<br/>High-level design decisions"]
        Coder["Coder Role<br/>Code implementation"]
        Builder["Builder Role<br/>File modifications and edits"]
        Validator["Validator Role<br/>Syntax and logic validation"]
        Namer["Namer Role<br/>Variable and function naming"]
    end
    
    subgraph "Built-in Model Packs"
        Daily["Daily Driver Pack<br/>--daily"]
        Reasoning["Reasoning Pack<br/>--reasoning"]
        Strong["Strong Pack<br/>--strong"]
        Cheap["Cheap Pack<br/>--cheap"]
        OSS["Open Source Pack<br/>--oss"]
    end
    
    subgraph "Model Providers"
        OpenAI["OpenAI<br/>GPT-4, o1, o3"]
        Anthropic["Anthropic<br/>Claude 3.5, Claude 4"]
        Google["Google<br/>Gemini 2.0 Pro"]
        OpenRouter["OpenRouter<br/>Various models"]
        Local["Local<br/>Ollama models"]
    end
    
    Daily --> Planner
    Daily --> Architect
    Daily --> Coder
    Daily --> Builder
    Daily --> Validator
    Daily --> Namer
    
    Planner --> OpenAI
    Architect --> Anthropic
    Coder --> Google
    Builder --> OpenRouter
    Validator --> Local
```

### Model Configuration Commands

| Command | Purpose |
|---------|---------|
| `plandex models` | Show current plan's model settings |
| `plandex models default` | Show default model settings |
| `plandex set-model` | Change current plan's models |
| `plandex set-model default` | Set default models for new plans |
| `plandex model-packs` | List available model packs |
| `plandex providers` | Show available model providers |

**Sources:** [docs/docs/cli-reference.md:674-799](), [docs/docs/models/models-overview.md:10-17]()

## Autonomy Levels

**Autonomy levels** control how much automation Plandex performs during plan execution. These levels range from step-by-step manual control to full automation.

```mermaid
graph LR
    None["None<br/>--no-auto<br/>Step-by-step manual control"]
    Basic["Basic<br/>--basic<br/>Auto-continue plans only"]
    Plus["Plus<br/>--plus<br/>Auto-update context<br/>Smart context<br/>Auto-commit changes"]
    Semi["Semi-Auto<br/>--semi<br/>Auto-load context"]
    Full["Full-Auto<br/>--full<br/>Auto-apply<br/>Auto-exec<br/>Auto-debug"]
    
    None --> Basic
    Basic --> Plus
    Plus --> Semi
    Semi --> Full
    
    style None fill:#ffebee
    style Basic fill:#fff3e0
    style Plus fill:#e8f5e8
    style Semi fill:#e1f5fe
    style Full fill:#f3e5f5
```

### Autonomy Configuration

| Level | Features | Use Case |
|-------|----------|----------|
| **None** | Manual confirmation for every step | Maximum control, learning Plandex |
| **Basic** | Auto-continue plans | Moderate oversight |
| **Plus** | Context management automation | Balanced workflow |
| **Semi-Auto** | Smart context loading | Streamlined development |
| **Full-Auto** | Complete automation | Maximum productivity |

Configuration commands:
- `plandex set-auto [level]` - Set autonomy for current plan
- `plandex set-auto default [level]` - Set default for new plans

**Sources:** [docs/docs/cli-reference.md:646-672](), [docs/docs/cli-reference.md:48-76]()

## Branches and Version Control

**Branches** allow exploration of different implementation approaches within a single plan. Each branch maintains its own conversation history and file modifications.

```mermaid
graph TB
    Plan["Plan: feature-auth"] --> Main["main branch"]
    Plan --> Experimental["experimental branch<br/>plandex checkout experimental"]
    Plan --> Alternative["alternative branch<br/>plandex checkout alternative"]
    
    Main --> MainHistory["Conversation History"]
    Main --> MainChanges["Pending Changes"]
    
    Experimental --> ExpHistory["Separate History"]
    Experimental --> ExpChanges["Independent Changes"]
    
    Alternative --> AltHistory["Different Approach"]
    Alternative --> AltChanges["Alternative Implementation"]
    
    MainChanges --> GitCommit["Git Integration<br/>Auto-commit with --commit"]
    ExpChanges --> GitCommit
    AltChanges --> GitCommit
```

### Branch Management Commands

| Command | Purpose |
|---------|---------|
| `plandex branches` | List all branches for current plan |
| `plandex checkout [branch]` | Switch to or create branch |
| `plandex delete-branch [branch]` | Delete a branch |

Each branch maintains:
- Independent conversation history
- Separate pending file changes
- Individual context state
- Branch-specific configuration

**Sources:** [docs/docs/cli-reference.md:537-571]()

## Streaming and Real-time Interaction

**Streaming** provides real-time interaction with AI models during plan execution. Users can monitor progress, make decisions, and intervene as needed through the terminal UI.

```mermaid
graph LR
    subgraph "Plan Execution"
        UserInput["User Input<br/>plandex tell"]
        AIResponse["AI Model Response<br/>Streaming tokens"]
        Decision["Decision Points<br/>Continue/Apply/Stop"]
    end
    
    subgraph "Stream Management"
        ActiveStreams["Active Streams<br/>plandex ps"]
        Connect["Connect to Stream<br/>plandex connect"]
        Stop["Stop Stream<br/>plandex stop"]
        Background["Background Tasks<br/>--bg flag"]
    end
    
    UserInput --> AIResponse
    AIResponse --> Decision
    Decision --> UserInput
    
    AIResponse --> ActiveStreams
    ActiveStreams --> Connect
    ActiveStreams --> Stop
    UserInput --> Background
```

### Stream States and Control

| State | Description | Actions Available |
|-------|-------------|-------------------|
| **Active** | Currently processing | Connect, stop, monitor |
| **Finished** | Completed successfully | Review results |
| **Stopped** | Manually halted | Resume or start new |
| **Errored** | Failed with error | Debug and retry |
| **Waiting** | Needs user input | Provide missing information |

**Sources:** [docs/docs/cli-reference.md:574-602]()

## Core Concept Relationships

```mermaid
graph TB
    subgraph "User Interaction Layer"
        REPL["REPL Interface<br/>plandex command"]
        CLI["CLI Commands<br/>Direct invocation"]
    end
    
    subgraph "Plan Management"
        Plans["Plans<br/>plandex new/cd/delete-plan"]
        Branches["Branches<br/>plandex checkout/branches"]
        History["History<br/>plandex log/rewind"]
    end
    
    subgraph "Context System"
        Context["Context Loading<br/>plandex load"]
        ProjectMap["Project Mapping<br/>tree-sitter analysis"]
        ContextDB["Context Database<br/>2M token window"]
    end
    
    subgraph "AI Execution"
        Models["Model Packs<br/>plandex set-model"]
        Roles["Model Roles<br/>Planner/Coder/Builder"]
        Streaming["Streaming Responses<br/>Real-time interaction"]
    end
    
    subgraph "Autonomy Control"
        AutoLevels["Autonomy Levels<br/>none/basic/plus/semi/full"]
        Config["Configuration<br/>plandex set-config"]
    end
    
    subgraph "File Management"
        Build["Build Process<br/>plandex build"]
        Diff["Change Review<br/>plandex diff"]
        Apply["Apply Changes<br/>plandex apply"]
        Git["Git Integration<br/>Auto-commit"]
    end
    
    REPL --> Plans
    CLI --> Plans
    
    Plans --> Branches
    Plans --> History
    Plans --> Context
    
    Context --> ProjectMap
    ProjectMap --> ContextDB
    
    Plans --> Models
    Models --> Roles
    Roles --> Streaming
    
    Plans --> AutoLevels
    AutoLevels --> Config
    
    Streaming --> Build
    Build --> Diff
    Diff --> Apply
    Apply --> Git
    
    Config --> Models
    Config --> AutoLevels
```

**Sources:** [README.md:80-90](), [docs/docs/cli-reference.md:1-50](), Architecture diagrams from system overview

---

# Page: System Architecture Overview

# System Architecture Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [app/cli/go.mod](app/cli/go.mod)
- [app/cli/go.sum](app/cli/go.sum)
- [app/server/go.mod](app/server/go.mod)
- [app/server/go.sum](app/server/go.sum)
- [app/shared/go.mod](app/shared/go.mod)
- [app/shared/go.sum](app/shared/go.sum)
- [docs/docs/cli-reference.md](docs/docs/cli-reference.md)
- [docs/docs/environment-variables.md](docs/docs/environment-variables.md)
- [docs/docs/hosting/cloud.md](docs/docs/hosting/cloud.md)
- [docs/docs/hosting/self-hosting/_category_.json](docs/docs/hosting/self-hosting/_category_.json)
- [docs/docs/hosting/self-hosting/advanced-self-hosting.md](docs/docs/hosting/self-hosting/advanced-self-hosting.md)
- [docs/docs/hosting/self-hosting/local-mode-quickstart.md](docs/docs/hosting/self-hosting/local-mode-quickstart.md)
- [docs/docs/install.md](docs/docs/install.md)
- [docs/docs/models/claude-subscription.md](docs/docs/models/claude-subscription.md)
- [docs/docs/models/models-overview.md](docs/docs/models/models-overview.md)
- [docs/docs/quick-start.md](docs/docs/quick-start.md)
- [releases/cli/versions/2.0.8.md](releases/cli/versions/2.0.8.md)

</details>



This document provides a high-level technical overview of Plandex's system architecture, covering the client-server design, module structure, and key components. It focuses on how the major subsystems interact and the overall data flow through the system.

For detailed information about individual CLI commands and their usage, see [CLI Reference](#2). For specifics about plan execution workflows, see [Plan Execution System](#3). For server-side implementation details, see [Server Architecture](#4).

## Architecture Overview

Plandex follows a client-server architecture built in Go, with three main modules: CLI, Server, and Shared components. The system is designed to handle AI-assisted coding tasks through a sophisticated plan execution pipeline that integrates with multiple AI model providers and maintains state in PostgreSQL.

### High-Level System Components

```mermaid
graph TB
    subgraph "Client Layer"
        CLI["plandex-cli"]
        REPL["REPL Interface"]
        StreamUI["Streaming UI"]
        TUI["Terminal Components"]
    end
    
    subgraph "Server Layer"
        APIServer["HTTP API Server"]
        PlanEngine["Plan Execution Engine"]
        ModelClient["AI Model Client"]
        BuildSystem["File Build System"]
        ContextManager["Context Manager"]
    end
    
    subgraph "Data Layer"
        PostgreSQL[("PostgreSQL Database")]
        FileSystem[("File System")]
        GitRepos[("Git Repositories")]
    end
    
    subgraph "External Services"
        OpenAI["OpenAI API"]
        Anthropic["Anthropic API"]
        Google["Google AI"]
        OpenRouter["OpenRouter"]
        LocalModels["Ollama/Local"]
    end
    
    CLI --> REPL
    CLI --> StreamUI
    CLI --> TUI
    
    CLI --> APIServer
    APIServer --> PlanEngine
    PlanEngine --> ModelClient
    PlanEngine --> BuildSystem
    PlanEngine --> ContextManager
    
    APIServer --> PostgreSQL
    PlanEngine --> FileSystem
    BuildSystem --> GitRepos
    
    ModelClient --> OpenAI
    ModelClient --> Anthropic
    ModelClient --> Google
    ModelClient --> OpenRouter
    ModelClient --> LocalModels
```

Sources: [README.md:81-125](), [app/cli/go.mod:1-107](), [app/server/go.mod:1-54](), [app/shared/go.mod:1-25]()

### Module Structure and Dependencies

```mermaid
graph TB
    subgraph "plandex-cli Module"
        CLIMain["main.go"]
        REPLCmd["REPL Commands"]
        StreamProcessor["Stream Processor"]
        UIComponents["UI Components"]
        ConfigManager["Config Manager"]
    end
    
    subgraph "plandex-server Module"
        ServerMain["main.go"]
        HTTPHandlers["HTTP Handlers"]
        PlanExec["Plan Execution"]
        ModelIntegration["Model Integration"]
        DBOperations["Database Operations"]
    end
    
    subgraph "plandex-shared Module"
        SharedTypes["Shared Types"]
        APIContracts["API Contracts"]
        CommonUtils["Common Utilities"]
        TokenUtils["Token Management"]
    end
    
    subgraph "External Dependencies"
        Cobra["github.com/spf13/cobra"]
        Mux["github.com/gorilla/mux"]
        SQLX["github.com/jmoiron/sqlx"]
        OpenAISDK["github.com/sashabaranov/go-openai"]
        PostgreSQL["github.com/lib/pq"]
        TreeSitter["github.com/smacker/go-tree-sitter"]
    end
    
    CLIMain --> SharedTypes
    CLIMain --> APIContracts
    REPLCmd --> Cobra
    UIComponents --> CommonUtils
    
    ServerMain --> SharedTypes
    ServerMain --> APIContracts
    HTTPHandlers --> Mux
    ModelIntegration --> OpenAISDK
    DBOperations --> SQLX
    DBOperations --> PostgreSQL
    
    SharedTypes --> TokenUtils
    CommonUtils --> TreeSitter
```

Sources: [app/cli/go.mod:5-28](), [app/server/go.mod:5-12](), [app/shared/go.mod:5-10]()

## Client-Server Communication

The CLI communicates with the server through HTTP APIs, with support for both synchronous requests and streaming responses for real-time plan execution.

### API Communication Flow

```mermaid
sequenceDiagram
    participant CLI as "plandex CLI"
    participant API as "HTTP API Server"
    participant PlanExec as "Plan Execution Engine"
    participant Models as "AI Model Clients"
    participant DB as "PostgreSQL"
    
    CLI->>API: "/api/plans" (Create Plan)
    API->>DB: Store Plan
    API->>CLI: Plan Created
    
    CLI->>API: "/api/tell" (Plan Request)
    API->>PlanExec: Execute Plan
    PlanExec->>Models: Model Request
    Models->>PlanExec: Streaming Response
    PlanExec->>API: Stream Updates
    API->>CLI: Real-time Stream
    
    CLI->>API: "/api/build" (Build Changes)
    API->>PlanExec: Build File Updates
    PlanExec->>DB: Store Updates
    API->>CLI: Build Complete
    
    CLI->>API: "/api/apply" (Apply Changes)
    API->>PlanExec: Apply to Files
    PlanExec->>CLI: File System Updates
```

Sources: [docs/docs/cli-reference.md:296-370](), [app/server/go.mod:8]()

## Data Storage Architecture

Plandex uses a hybrid storage approach combining PostgreSQL for structured data and the file system for project files and Git repositories.

### Data Storage Components

```mermaid
graph LR
    subgraph "PostgreSQL Database"
        Plans["plans table"]
        Contexts["contexts table"]
        Conversations["conversations table"]
        Users["users table"]
        Organizations["organizations table"]
    end
    
    subgraph "File System Storage"
        BaseDir["PLANDEX_BASE_DIR"]
        ProjectFiles["Project Files"]
        ContextFiles["Context Cache"]
        BuildArtifacts["Build Artifacts"]
    end
    
    subgraph "Git Integration"
        LocalRepos["Local Git Repos"]
        Commits["Auto Commits"]
        Branches["Plan Branches"]
    end
    
    Plans --> ProjectFiles
    Contexts --> ContextFiles
    Conversations --> BuildArtifacts
    
    ProjectFiles --> LocalRepos
    BuildArtifacts --> Commits
    Plans --> Branches
```

Sources: [docs/docs/hosting/self-hosting/advanced-self-hosting.md:28-36](), [docs/docs/environment-variables.md:87](), [app/server/go.mod:46]()

## AI Model Integration

The system supports multiple AI model providers through a unified client interface with role-based model assignment and fallback mechanisms.

### Model Provider Architecture

```mermaid
graph TB
    subgraph "Model Client System"
        ClientRouter["Model Client Router"]
        OpenAIClient["OpenAI Client"]
        AnthropicClient["Anthropic Client"]
        GoogleClient["Google AI Client"]
        OpenRouterClient["OpenRouter Client"]
        OllamaClient["Ollama Client"]
    end
    
    subgraph "Model Roles"
        PlannerRole["Planner Role"]
        ArchitectRole["Architect Role"]
        CoderRole["Coder Role"]
        BuilderRole["Builder Role"]
        ValidatorRole["Validator Role"]
        NamerRole["Namer Role"]
    end
    
    subgraph "Configuration"
        ModelPacks["Model Packs"]
        CustomModels["Custom Models"]
        ProviderConfigs["Provider Configs"]
    end
    
    ClientRouter --> OpenAIClient
    ClientRouter --> AnthropicClient
    ClientRouter --> GoogleClient
    ClientRouter --> OpenRouterClient
    ClientRouter --> OllamaClient
    
    ModelPacks --> PlannerRole
    ModelPacks --> ArchitectRole
    ModelPacks --> CoderRole
    ModelPacks --> BuilderRole
    ModelPacks --> ValidatorRole
    ModelPacks --> NamerRole
    
    ProviderConfigs --> ClientRouter
    CustomModels --> ModelPacks
```

Sources: [docs/docs/models/models-overview.md:10-12](), [docs/docs/environment-variables.md:22-58](), [app/server/go.mod:10]()

## Plan Execution Pipeline

The core plan execution system processes user requests through multiple stages, from initial planning to file modifications.

### Plan Execution Flow

```mermaid
flowchart TD
    UserInput["User Input via CLI"]
    TellHandler["/api/tell Handler"]
    PlanExecution["Plan Execution Engine"]
    ContextLoader["Context Loader"]
    ModelDispatcher["Model Dispatcher"]
    StreamProcessor["Stream Processor"]
    BuildQueue["Build Queue"]
    FileValidator["File Validator"]
    GitOperations["Git Operations"]
    ApplyHandler["/api/apply Handler"]
    
    UserInput --> TellHandler
    TellHandler --> PlanExecution
    PlanExecution --> ContextLoader
    PlanExecution --> ModelDispatcher
    ModelDispatcher --> StreamProcessor
    StreamProcessor --> BuildQueue
    BuildQueue --> FileValidator
    FileValidator --> GitOperations
    PlanExecution --> ApplyHandler
    
    ContextLoader --> ModelDispatcher
    StreamProcessor --> UserInput
```

Sources: [docs/docs/cli-reference.md:295-333](), [README.md:128-131]()

## Hosting and Deployment

Plandex supports multiple deployment modes including cloud hosting and self-hosting with Docker.

### Deployment Architecture

```mermaid
graph TB
    subgraph "Plandex Cloud"
        CloudAPI["api.plandex.ai"]
        IntegratedModels["Integrated Models"]
        BYOKey["BYO API Key Mode"]
    end
    
    subgraph "Self-Hosted Options"
        LocalDocker["Local Docker Mode"]
        RemoteServer["Remote Server"]
        DockerCompose["docker-compose.yml"]
    end
    
    subgraph "Environment Variables"
        GOENV["GOENV=development|production"]
        DatabaseURL["DATABASE_URL"]
        APIHost["API_HOST"]
        SMTPConfig["SMTP Configuration"]
    end
    
    subgraph "Required Services"
        PostgreSQLDB[("PostgreSQL Database")]
        FileSystemStorage[("File System Storage")]
        GitInstallation["Git Installation"]
    end
    
    CloudAPI --> IntegratedModels
    CloudAPI --> BYOKey
    
    LocalDocker --> DockerCompose
    RemoteServer --> GOENV
    RemoteServer --> DatabaseURL
    RemoteServer --> APIHost
    RemoteServer --> SMTPConfig
    
    LocalDocker --> PostgreSQLDB
    RemoteServer --> PostgreSQLDB
    LocalDocker --> FileSystemStorage
    RemoteServer --> FileSystemStorage
    LocalDocker --> GitInstallation
    RemoteServer --> GitInstallation
```

Sources: [docs/docs/hosting/cloud.md:14-33](), [docs/docs/hosting/self-hosting/local-mode-quickstart.md:12-19](), [docs/docs/environment-variables.md:84-111]()

This architecture enables Plandex to scale from single-user local development to multi-tenant cloud deployments while maintaining consistent functionality across all deployment modes.

---

# Page: CLI Reference

# CLI Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/cli/cmd/current.go](app/cli/cmd/current.go)
- [app/cli/cmd/new.go](app/cli/cmd/new.go)
- [app/cli/cmd/plan_start_helpers.go](app/cli/cmd/plan_start_helpers.go)
- [app/cli/cmd/repl.go](app/cli/cmd/repl.go)
- [app/cli/cmd/root.go](app/cli/cmd/root.go)
- [app/cli/term/help.go](app/cli/term/help.go)

</details>



This document provides comprehensive documentation of the Plandex command-line interface, covering command structure, REPL functionality, and command execution patterns. For server-side API details, see [Server Architecture](#4). For AI model integration specifics, see [AI Model Integration](#5). For plan execution workflows, see [Plan Execution System](#3).

## Command Structure and Organization

The Plandex CLI provides both standalone command execution and an interactive REPL environment. Commands are organized into logical categories based on their functional purpose in the plan lifecycle.

**Command Organization by Category**

```mermaid
graph TD
    CLI["plandex / pdx CLI"]
    
    subgraph "Plan Management"
        NewCmd["new - Start new plan"]
        PlansCmd["plans (pl) - List plans"]
        CdCmd["cd - Set current plan"]
        CurrentCmd["current (cu) - Show current"]
        RenameCmd["rename - Rename plan"]
        DeletePlanCmd["delete-plan (dp) - Delete plan"]
        ArchiveCmd["archive (arc) - Archive plan"]
        UnarchiveCmd["unarchive (unarc) - Unarchive plan"]
    end
    
    subgraph "Context Management"
        LoadCmd["load (l) - Load context"]
        LsCmd["ls - List context"]
        RmCmd["rm - Remove context"]
        ClearCmd["clear - Remove all context"]
        UpdateCmd["update (u) - Update context"]
        ShowCmd["show - Show context"]
    end
    
    subgraph "Plan Execution"
        TellCmd["tell (t) - Describe task"]
        ChatCmd["chat (ch) - Ask questions"]
        ContinueCmd["continue (c) - Continue plan"]
        BuildCmd["build (b) - Build changes"]
        DebugCmd["debug (db) - Debug commands"]
    end
    
    subgraph "Change Management"
        DiffCmd["diff - Review changes"]
        ApplyCmd["apply (ap) - Apply changes"]
        RejectCmd["reject (rj) - Reject changes"]
    end
    
    subgraph "History & Branches"
        LogCmd["log - Show history"]
        RewindCmd["rewind (rw) - Rewind state"]
        ConvoCmd["convo - Show conversation"]
        SummaryCmd["summary - Show summary"]
        BranchesCmd["branches (br) - List branches"]
        CheckoutCmd["checkout (co) - Switch branch"]
        DeleteBranchCmd["delete-branch (dlb) - Delete branch"]
    end
    
    subgraph "Configuration"
        ConfigCmd["config - Show config"]
        SetConfigCmd["set-config - Update config"]
        SetAutoCmd["set-auto - Set autonomy"]
        ModelsCmd["models - Show models"]
        SetModelCmd["set-model - Update models"]
        ModelPacksCmd["model-packs - Show packs"]
    end
    
    CLI --> NewCmd
    CLI --> PlansCmd
    CLI --> LoadCmd
    CLI --> TellCmd
    CLI --> DiffCmd
    CLI --> LogCmd
    CLI --> ConfigCmd
```

Sources: [app/cli/term/help.go:19-145]()

## REPL Architecture

The REPL (Read-Eval-Print Loop) is implemented through the `go-prompt` library and provides the primary interactive interface for Plandex usage.

**REPL Component Architecture**

```mermaid
graph TB
    subgraph "REPL Core Components"
        PromptNew["prompt.New()"]
        ExecutorFunc["executor() function"]
        CompleterFunc["completer() function"]
        ParseCommandFunc["parseCommand() function"]
    end
    
    subgraph "Input Processing"
        InputCapture["Input text capture"]
        BackslashDetect["Command detection (\\\\)"]
        AtSymbolDetect["File reference (@)"]
        GetSuggestions["getSuggestions() function"]
    end
    
    subgraph "Command Execution"
        ReplBuiltins["Built-in REPL commands"]
        ExecPlandexCommand["lib.ExecPlandexCommandWithParams()"]
        TellChatModes["tell/chat mode handling"]
    end
    
    subgraph "State Management"
        CurrentReplState["lib.CurrentReplState"]
        ReplModeTell["lib.ReplModeTell"]
        ReplModeChat["lib.ReplModeChat"]
        IsMultiState["IsMulti for multiline"]
    end
    
    PromptNew --> InputCapture
    InputCapture --> BackslashDetect
    InputCapture --> AtSymbolDetect
    BackslashDetect --> ParseCommandFunc
    AtSymbolDetect --> GetSuggestions
    
    ParseCommandFunc --> ReplBuiltins
    ParseCommandFunc --> ExecPlandexCommand
    ParseCommandFunc --> TellChatModes
    
    ExecutorFunc --> CurrentReplState
    ExecutorFunc --> ReplModeTell
    CompleterFunc --> GetSuggestions
    
    ReplBuiltins -.-> IsMultiState
    ReplBuiltins -.-> ReplModeChat
```

Sources: [app/cli/cmd/repl.go:31-220](), [app/cli/cmd/repl.go:521-762]()

## Command Execution Flow

Command execution follows different paths depending on whether commands are invoked directly or through the REPL interface.

**CLI Command Execution Pipeline**

```mermaid
graph TD
    subgraph "Entry Points"
        DirectCLI["Direct CLI: plandex [cmd]"]
        ReplInterface["REPL: \\\\[cmd]"]
        AutoREPL["Auto-REPL: plandex (no args)"]
    end
    
    subgraph "Command Resolution"
        RootCmdExecute["RootCmd.Execute()"]
        ReplCmdRun["replCmd.Run()"]
        ParseFlags["cobra flag parsing"]
        CommandLookup["term.CliCommands lookup"]
    end
    
    subgraph "Authentication & Project"
        MustResolveAuth["auth.MustResolveAuthWithOrg()"]
        MustResolveProject["lib.MustResolveOrCreateProject()"]
        LoadState["lib.LoadState()"]
    end
    
    subgraph "Command Execution"
        ExecPlandexCommandWithParams["lib.ExecPlandexCommandWithParams()"]
        ApiClientCalls["api.Client method calls"]
        TermOutput["term output functions"]
        WriteState["lib.WriteState()"]
    end
    
    DirectCLI --> RootCmdExecute
    AutoREPL --> ReplCmdRun
    ReplInterface --> ExecPlandexCommandWithParams
    
    RootCmdExecute --> ParseFlags
    ReplCmdRun --> MustResolveAuth
    ParseFlags --> CommandLookup
    
    MustResolveAuth --> MustResolveProject
    MustResolveProject --> LoadState
    
    CommandLookup --> ExecPlandexCommandWithParams
    ExecPlandexCommandWithParams --> ApiClientCalls
    ApiClientCalls --> TermOutput
    TermOutput --> WriteState
```

Sources: [app/cli/cmd/root.go:15-70](), [app/cli/cmd/repl.go:72-220]()

## REPL Command Processing

The REPL implements sophisticated command processing with fuzzy matching, auto-completion, and context-aware suggestions.

**REPL Input Processing Flow**

```mermaid
graph LR
    subgraph "Input Analysis"
        UserInput["User input text"]
        LastLineExtract["Extract last line"]
        BackslashIndex["Find lastBackslashIndex"]
        AtIndex["Find lastAtIndex"]
    end
    
    subgraph "Command Matching"
        FuzzyFilter["prompt.FilterFuzzy()"]
        PrefixFilter["prompt.FilterHasPrefix()"]
        ReplCmdAliases["lib.ReplCmdAliases lookup"]
        FindSimilarCommands["findSimilarCommands()"]
    end
    
    subgraph "Suggestion Generation"
        CliSuggestions["cliSuggestions from term.CliCommands"]
        ProjectPathsSuggestions["projectPaths.ActivePaths"]
        BuiltinSuggestions["Built-in REPL suggestions"]
        FileSuggestions["File path auto-complete"]
    end
    
    subgraph "Execution Routing"
        BuiltinExecution["quit, help, multi, send execution"]
        ExecPlandexCommand["CLI command execution"]
        TellChatExecution["tell/chat mode execution"]
        FileLoading["Auto-load file references"]
    end
    
    UserInput --> LastLineExtract
    LastLineExtract --> BackslashIndex
    LastLineExtract --> AtIndex
    
    BackslashIndex --> FuzzyFilter
    BackslashIndex --> ReplCmdAliases
    FuzzyFilter --> FindSimilarCommands
    
    FindSimilarCommands --> CliSuggestions
    AtIndex --> ProjectPathsSuggestions
    ProjectPathsSuggestions --> FileSuggestions
    
    ReplCmdAliases --> BuiltinExecution
    ReplCmdAliases --> ExecPlandexCommand
    BackslashIndex --> TellChatExecution
    AtIndex --> FileLoading
```

Sources: [app/cli/cmd/repl.go:521-762](), [app/cli/cmd/repl.go:914-1035]()

## Plan Management Commands

Plan management commands handle the complete lifecycle of Plandex plans from creation through deletion.

| Command | Alias | Function | Implementation |
|---------|-------|----------|----------------|
| `new` | `n` | Create new plan | [app/cli/cmd/new.go]() |
| `plans` | `pl` | List all plans | Via `term.CliCommands` |
| `cd` | - | Switch current plan | Via `term.CliCommands` |
| `current` | `cu` | Show current plan | [app/cli/cmd/current.go]() |
| `delete-plan` | `dp` | Delete plan(s) | Via `term.CliCommands` |
| `archive` | `arc` | Archive a plan | Via `term.CliCommands` |
| `unarchive` | `unarc` | Unarchive a plan | Via `term.CliCommands` |

**Plan Creation Workflow**

```mermaid
graph TD
    NewCommand["newCmd.Run()"]
    
    subgraph "Initialization Phase"
        MustResolveAuth["auth.MustResolveAuthWithOrg()"]
        MustResolveProject["lib.MustResolveOrCreateProject()"]
        StartSpinner["term.StartSpinner()"]
    end
    
    subgraph "Concurrent API Operations"
        CreatePlanAPI["api.Client.CreatePlan()"]
        GetDefaultConfig["api.Client.GetDefaultPlanConfig()"]
        ErrorChannel["errCh chan error"]
    end
    
    subgraph "State Persistence"
        WriteCurrentPlan["lib.WriteCurrentPlan(planId)"]
        WriteCurrentBranch["lib.WriteCurrentBranch('main')"]
        ResolveAutoMode["resolveAutoMode()"]
        ResolveModelPack["resolveModelPack()"]
    end
    
    subgraph "Context Auto-Loading"
        CheckAutoLoadContext["config.AutoLoadContext check"]
        MustLoadContext["lib.MustLoadContext() with DefsOnly"]
    end
    
    NewCommand --> MustResolveAuth
    MustResolveAuth --> MustResolveProject
    MustResolveProject --> StartSpinner
    
    StartSpinner --> CreatePlanAPI
    StartSpinner --> GetDefaultConfig
    CreatePlanAPI --> ErrorChannel
    GetDefaultConfig --> ErrorChannel
    
    ErrorChannel --> WriteCurrentPlan
    WriteCurrentPlan --> WriteCurrentBranch
    WriteCurrentBranch --> ResolveAutoMode
    ResolveAutoMode --> ResolveModelPack
    
    ResolveModelPack --> CheckAutoLoadContext
    CheckAutoLoadContext --> MustLoadContext
```

Sources: [app/cli/cmd/new.go:39-134]()

## Context Management Commands

Context management provides control over what information is available to AI models during plan execution.

| Command | Alias | Purpose | Supported Types |
|---------|-------|---------|-----------------|
| `load` | `l` | Add context to plan | Files, URLs, Notes, Images, Piped data |
| `ls` | - | List current context | All context types |
| `rm` | - | Remove context items | By index/name/glob pattern |
| `clear` | - | Remove all context | All context types |
| `update` | `u` | Refresh outdated context | File-based context only |
| `show` | - | Display context content | Individual context items |

**Context Loading Strategies**

```mermaid
graph TD
    LoadCommand["load command invocation"]
    
    subgraph "Input Type Detection"
        FileInput["Files: component.ts"]
        DirectoryInput["Directories: lib"]
        URLInput["URLs: https://example.com"]
        NoteInput["Notes: -n 'instruction'"]
        ImageInput["Images: ui-mockup.png"]
        PipedInput["Piped: npm test | plandex load"]
    end
    
    subgraph "Loading Flags"
        RecursiveFlag["--recursive (-r)"]
        TreeFlag["--tree (directory structure)"]
        MapFlag["--map (function signatures)"]
        ForceFlag["--force (ignore .gitignore)"]
        DetailFlag["--detail (image quality)"]
    end
    
    subgraph "Context Processing"
        ApiClientLoad["api.Client context methods"]
        ContextTypeMapping["shared.ContextType constants"]
        TokenCalculation["Token size calculation"]
        ValidationChecks["File existence validation"]
    end
    
    LoadCommand --> FileInput
    LoadCommand --> DirectoryInput
    LoadCommand --> URLInput
    LoadCommand --> NoteInput
    LoadCommand --> ImageInput
    LoadCommand --> PipedInput
    
    DirectoryInput --> RecursiveFlag
    DirectoryInput --> TreeFlag
    DirectoryInput --> MapFlag
    FileInput --> ForceFlag
    ImageInput --> DetailFlag
    
    RecursiveFlag --> ApiClientLoad
    TreeFlag --> ContextTypeMapping
    MapFlag --> TokenCalculation
    ForceFlag --> ValidationChecks
```

Sources: [app/cli/term/help.go:71-76](), [docs/docs/cli-reference.md:200-229]()

## Configuration Management

Configuration commands control plan behavior through the `shared.PlanConfig` struct and autonomy level settings.

**Configuration Command Architecture**

```mermaid
graph TB
    subgraph "Configuration Commands"
        ConfigShow["config command"]
        ConfigDefault["config default command"]
        SetConfigCmd["set-config command"]
        SetConfigDefault["set-config default command"]
        SetAutoCmd["set-auto command"]
        SetAutoDefault["set-auto default command"]
    end
    
    subgraph "Configuration Data Structures"
        PlanConfig["shared.PlanConfig struct"]
        AutoModeType["shared.AutoModeType enum"]
        ConfigSettingsByKey["shared.ConfigSettingsByKey map"]
        ConfigSetting["shared.ConfigSetting struct"]
    end
    
    subgraph "Autonomy Level Constants"
        AutoModeFull["AutoModeFull - Full automation"]
        AutoModeSemi["AutoModeSemi - Semi-auto context"]
        AutoModePlus["AutoModePlus - Context + smart features"]
        AutoModeBasic["AutoModeBasic - Auto-continue only"]
        AutoModeNone["AutoModeNone - Manual step-by-step"]
        AutoModeCustom["AutoModeCustom - Individual settings"]
    end
    
    subgraph "Configuration Processing"
        UpdateConfigFunc["updateConfig() function"]
        SetAutoModeMethod["PlanConfig.SetAutoMode() method"]
        UpdatePlanConfigAPI["api.Client.UpdatePlanConfig()"]
        LoadMapIfNeeded["loadMapIfNeeded() function"]
    end
    
    SetConfigCmd --> UpdateConfigFunc
    SetAutoCmd --> SetAutoModeMethod
    UpdateConfigFunc --> ConfigSettingsByKey
    SetAutoModeMethod --> AutoModeFull
    SetAutoModeMethod --> AutoModeSemi
    SetAutoModeMethod --> AutoModePlus
    SetAutoModeMethod --> AutoModeBasic
    SetAutoModeMethod --> AutoModeNone
    
    UpdateConfigFunc --> UpdatePlanConfigAPI
    UpdatePlanConfigAPI --> PlanConfig
    UpdateConfigFunc --> LoadMapIfNeeded
```

Sources: [app/cli/cmd/set_config.go:26-367](), [app/shared/plan_config.go:19-477]()

## Model Management Commands

Model management commands control AI model selection and configuration for the different roles in plan execution.

| Command | Purpose | Scope |
|---------|---------|-------|
| `models` | Show current model settings | Current plan |
| `models default` | Show org default settings | Organization-wide |
| `models available` | List available models | All providers |
| `set-model` | Update model configuration | Current plan |
| `set-model default` | Update default models | Organization-wide |
| `model-packs` | Show available model packs | Built-in and custom |

**Model System Architecture**

```mermaid
graph LR
    subgraph "Model Roles"
        PlannerRole["planner role"]
        CoderRole["coder role"]
        ArchitectRole["architect role"]
        BuilderRole["builder role"]
    end
    
    subgraph "Built-in Model Packs"
        DailyDriverPack["daily-driver pack"]
        ReasoningPack["reasoning pack"]
        StrongPack["strong pack"]
        CheapPack["cheap pack"]
        OssPack["oss pack"]
        GeminiPreviewPack["gemini-preview pack"]
    end
    
    subgraph "Provider Integration"
        OpenAIAPI["OpenAI API direct"]
        OpenRouterAPI["OpenRouter API"]
        AnthropicViaOR["Anthropic via OpenRouter"]
        GoogleViaOR["Google via OpenRouter"]
    end
    
    subgraph "Model Configuration"
        ModelSettings["Model temperature, top-p"]
        TokenLimits["max-tokens, max-convo-tokens"]
        CustomModels["User-defined custom models"]
        ModelPackCreation["Custom model pack creation"]
    end
    
    PlannerRole --> DailyDriverPack
    CoderRole --> DailyDriverPack
    ArchitectRole --> StrongPack
    BuilderRole --> ReasoningPack
    
    DailyDriverPack --> OpenAIAPI
    DailyDriverPack --> OpenRouterAPI
    StrongPack --> AnthropicViaOR
    ReasoningPack --> GoogleViaOR
    
    OpenAIAPI --> ModelSettings
    OpenRouterAPI --> TokenLimits
    AnthropicViaOR --> CustomModels
    GoogleViaOR --> ModelPackCreation
```

Sources: [app/cli/term/help.go:106-127](), [docs/docs/cli-reference.md:652-796]()

## Streaming and Background Execution

Plandex supports background task execution through stream management for long-running plan operations.

**Stream Management Architecture**

```mermaid
graph TD
    subgraph "Stream Management Commands"
        PsCommand["ps command"]
        ConnectCommand["connect (conn) command"]
        StopCommand["stop command"]
    end
    
    subgraph "Background Execution Support"
        BgFlag["--bg flag"]
        StreamIdGeneration["Unique stream ID generation"]
        StreamStatusTracking["Status: active/finished/stopped/errored"]
        WaitingForFile["waiting for missing file status"]
    end
    
    subgraph "Streamable Command Types"
        TellBgStream["tell --bg streams"]
        BuildBgStream["build --bg streams"]
        ChatBgStream["chat --bg streams"]
        DebugBgStream["debug --bg streams"]
    end
    
    subgraph "Stream Coordination"
        SessionIdGeneration["sessionId = uuid.New().String()"]
        ExecPlandexCommandParams["lib.ExecPlandexCommandParams"]
        StreamingTUI["Real-time terminal UI updates"]
        StreamReconnection["Stream reconnection capability"]
    end
    
    PsCommand --> StreamStatusTracking
    ConnectCommand --> StreamIdGeneration
    StopCommand --> StreamStatusTracking
    
    BgFlag --> TellBgStream
    BgFlag --> BuildBgStream
    BgFlag --> ChatBgStream
    BgFlag --> DebugBgStream
    
    TellBgStream --> SessionIdGeneration
    BuildBgStream --> ExecPlandexCommandParams
    ChatBgStream --> StreamingTUI
    DebugBgStream --> StreamReconnection
```

Sources: [app/cli/term/help.go:128-131](), [app/cli/cmd/repl.go:72-74]()

## Command Auto-completion and Suggestions

The REPL provides intelligent command completion based on multiple suggestion sources and context analysis.

**Suggestion System Architecture**

```mermaid
graph TB
    subgraph "Suggestion Data Sources"
        CliCommandsArray["term.CliCommands array"]
        ReplCmdAliasesMap["lib.ReplCmdAliases map"]
        ProjectPathsActive["projectPaths.ActivePaths"]
        BuiltinReplCmds["quit, help, multi, send, tell, chat, run"]
    end
    
    subgraph "Suggestion Processing Functions"
        FilterFuzzyFunc["prompt.FilterFuzzy()"]
        FilterHasPrefixFunc["prompt.FilterHasPrefix()"]
        IsValidPositionFunc["isValidPosition() validation"]
        FindSimilarCommandsFunc["findSimilarCommands()"]
    end
    
    subgraph "Context-Aware Filtering"
        ReplModeFiltering["Filter by config.Repl flag"]
        CommandSpecificSuggestions["Command-specific suggestions"]
        FileExtensionFiltering[".md/.txt filtering for \\\\run"]
        DirectoryFlagSuggestions["-r, --map, --tree for directories"]
    end
    
    subgraph "Suggestion Ranking Logic"
        PrefixMatchesFirst["Prefix matches prioritized"]
        BuiltinCommandPriority["Built-in commands at top"]
        AliasMatchPriority["Exact alias matches first"]
        AlphabeticalSorting["Alphabetical for remaining"]
    end
    
    CliCommandsArray --> FilterFuzzyFunc
    ReplCmdAliasesMap --> FindSimilarCommandsFunc
    ProjectPathsActive --> FileExtensionFiltering
    BuiltinReplCmds --> PrefixMatchesFirst
    
    FilterFuzzyFunc --> ReplModeFiltering
    FilterHasPrefixFunc --> CommandSpecificSuggestions
    IsValidPositionFunc --> DirectoryFlagSuggestions
    
    ReplModeFiltering --> PrefixMatchesFirst
    CommandSpecificSuggestions --> BuiltinCommandPriority
    DirectoryFlagSuggestions --> AliasMatchPriority
    FileExtensionFiltering --> AlphabeticalSorting
```

Sources: [app/cli/cmd/repl.go:521-762](), [app/cli/cmd/repl.go:222-292]()

## Command Help System

The CLI provides comprehensive help through multiple interfaces using structured command definitions.

**Help System Architecture**

```mermaid
graph LR
    subgraph "Help Command Types"
        HelpBasic["plandex help"]
        HelpAllCommands["plandex help --all"]
        CommandSpecificHelp["plandex [cmd] --help"]
        ReplHelpCommand["\\\\help in REPL"]
    end
    
    subgraph "Help Data Sources"
        CliCommandsConfig["term.CliCommands configuration"]
        CmdConfigStruct["term.CmdConfig struct"]
        AutoModeDescriptions["shared.AutoModeDescriptions"]
        CommandAliasMapping["Command alias mappings"]
    end
    
    subgraph "Help Formatting Functions"
        PrintCustomHelpFunc["term.PrintCustomHelp()"]
        PrintHelpAllCommandsFunc["term.PrintHelpAllCommands()"]
        ColorNewStyling["color.New() ANSI styling"]
        CategoryGrouping["Commands grouped by category"]
    end
    
    subgraph "Interactive Help Elements"
        PrintCmdsFunc["term.PrintCmds() suggestions"]
        ContextualHelpDisplay["Context-aware help display"]
        ErrorTriggeredHelp["Help on command errors"]
        ReplWelcomeHelp["replWelcome() help display"]
    end
    
    HelpBasic --> PrintCustomHelpFunc
    HelpAllCommands --> PrintHelpAllCommandsFunc
    ReplHelpCommand --> CliCommandsConfig
    
    CliCommandsConfig --> CmdConfigStruct
    CmdConfigStruct --> CommandAliasMapping
    AutoModeDescriptions --> ColorNewStyling
    
    PrintCustomHelpFunc --> CategoryGrouping
    PrintHelpAllCommandsFunc --> PrintCmdsFunc
    ColorNewStyling --> ContextualHelpDisplay
    CategoryGrouping --> ErrorTriggeredHelp
    ContextualHelpDisplay --> ReplWelcomeHelp
```

Sources: [app/cli/term/help.go:218-344](), [app/cli/cmd/root.go:77-91]()

---

# Page: REPL Interface

# REPL Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/cli/cmd/current.go](app/cli/cmd/current.go)
- [app/cli/cmd/new.go](app/cli/cmd/new.go)
- [app/cli/cmd/plan_start_helpers.go](app/cli/cmd/plan_start_helpers.go)
- [app/cli/cmd/repl.go](app/cli/cmd/repl.go)
- [app/cli/cmd/root.go](app/cli/cmd/root.go)
- [app/cli/term/help.go](app/cli/term/help.go)

</details>



## Purpose and Scope

The REPL (Read-Eval-Print Loop) Interface provides an interactive command-line environment for Plandex that allows users to execute commands, switch between chat and tell modes, load files, and manage plans without repeatedly invoking the `plandex` binary. This document covers the interactive prompt system, command processing, autocomplete functionality, and mode management.

For information about individual CLI commands available within the REPL, see [Plan Execution Commands](#2.2) and [Context Management Commands](#2.3). For details about the streaming terminal UI that displays plan execution progress, see [Streaming Terminal UI](#2.5).

## REPL Architecture Overview

The REPL system is built around the `go-prompt` library and integrates closely with the main CLI command system:

```mermaid
graph TB
    subgraph "REPL Entry Points"
        RootCmd["RootCmd.Execute()"]
        MainArgs["main() arg processing"]
        ReplCmd["replCmd.Run()"]
    end
    
    subgraph "REPL Core Components"
        PromptNew["prompt.New()"]
        Executor["executor() function"]
        Completer["completer() function"]
        ParseCommand["parseCommand()"]
    end
    
    subgraph "Command Processing"
        ExecWithInput["execWithInput()"]
        ExecPlandexCmd["lib.ExecPlandexCommandWithParams()"]
        SuggestCmds["suggestCmds()"]
        FindSimilarCmds["findSimilarCommands()"]
    end
    
    subgraph "State Management"
        CurrentReplState["lib.CurrentReplState"]
        ReplModeChat["ReplModeChat"]
        ReplModeTell["ReplModeTell"]
        IsMulti["IsMulti (multi-line)"]
    end
    
    subgraph "Data Sources"
        CliCommands["term.CliCommands[]"]
        ProjectPaths["projectPaths.ActivePaths"]
        ReplCmdAliases["lib.ReplCmdAliases"]
    end
    
    RootCmd --> ReplCmd
    MainArgs --> ReplCmd
    ReplCmd --> PromptNew
    PromptNew --> Executor
    PromptNew --> Completer
    
    Executor --> ParseCommand
    Executor --> ExecWithInput
    ExecWithInput --> ExecPlandexCmd
    ExecWithInput --> SuggestCmds
    SuggestCmds --> FindSimilarCmds
    
    Executor --> CurrentReplState
    CurrentReplState --> ReplModeChat
    CurrentReplState --> ReplModeTell
    CurrentReplState --> IsMulti
    
    Completer --> CliCommands
    Completer --> ProjectPaths
    Completer --> ReplCmdAliases
```

**Sources:** [app/cli/cmd/repl.go:31-219](), [app/cli/cmd/root.go:29-38](), [app/cli/main.go:64-82]()

## Command Processing Flow

The REPL processes user input through a sophisticated parsing and execution pipeline:

```mermaid
graph TD
    subgraph "Input Processing"
        UserInput["User Input"]
        TrimInput["strings.TrimSpace(in)"]
        ParseLines["Split by newlines, get lastLine"]
        CheckPrefix["Check plandex/pdx prefix"]
    end
    
    subgraph "Command Type Detection"
        FindBackslash["Find last \\ in lastLine"]
        FindAt["Find last @ in lastLine"]
        IsValidPosition["isValidPosition() check"]
        DetermineType["Determine command type"]
    end
    
    subgraph "Command Execution Paths"
        PlandexPrefix["Direct plandex command"]
        BackslashCmd["Backslash command (\\cmd)"]
        AtFileRef["File reference (@file)"]
        FuzzyMatch["Fuzzy command matching"]
        ModeBasedExec["Mode-based execution"]
    end
    
    subgraph "Built-in REPL Commands"
        QuitCmd["\\quit -> os.Exit(0)"]
        HelpCmd["\\help -> replHelp()"]
        MultiCmd["\\multi -> toggle IsMulti"]
        SendCmd["\\send -> execute buffer"]
        TellCmd["\\tell -> switch mode"]
        ChatCmd["\\chat -> switch mode"]
        RunCmd["\\run -> handleRunCommand()"]
    end
    
    subgraph "CLI Command Execution"
        MatchCliCmd["Match against term.CliCommands"]
        ExecWithParams["lib.ExecPlandexCommandWithParams()"]
        SessionId["Pass sessionId"]
    end
    
    UserInput --> TrimInput
    TrimInput --> ParseLines
    ParseLines --> CheckPrefix
    CheckPrefix --> PlandexPrefix
    
    ParseLines --> FindBackslash
    ParseLines --> FindAt
    FindBackslash --> IsValidPosition
    FindAt --> IsValidPosition
    IsValidPosition --> DetermineType
    
    DetermineType --> BackslashCmd
    DetermineType --> AtFileRef
    DetermineType --> FuzzyMatch
    DetermineType --> ModeBasedExec
    
    BackslashCmd --> QuitCmd
    BackslashCmd --> HelpCmd
    BackslashCmd --> MultiCmd
    BackslashCmd --> SendCmd
    BackslashCmd --> TellCmd
    BackslashCmd --> ChatCmd
    BackslashCmd --> RunCmd
    BackslashCmd --> MatchCliCmd
    
    MatchCliCmd --> ExecWithParams
    PlandexPrefix --> ExecWithParams
    ExecWithParams --> SessionId
```

**Sources:** [app/cli/cmd/repl.go:311-519](), [app/cli/cmd/repl.go:914-1035](), [app/cli/cmd/repl.go:1141-1367]()

## Mode Management and State

The REPL maintains state for different operational modes and multi-line editing:

| State Variable | Type | Purpose |
|----------------|------|---------|
| `lib.CurrentReplState.Mode` | `ReplModeType` | Current mode: `ReplModeTell` or `ReplModeChat` |
| `lib.CurrentReplState.IsMulti` | `bool` | Multi-line editing enabled |
| `replConfig` | `*shared.PlanConfig` | Current plan configuration |
| `sessionId` | `string` | Unique session identifier |
| `projectPaths` | `*types.ProjectPaths` | Active project file paths |

### Mode Switching

The REPL supports two primary modes with different behaviors:

```mermaid
graph LR
    subgraph "Tell Mode"
        TellIcon["⚡️ Tell mode"]
        TellDesc["Implementation and coding tasks"]
        TellWarning["❗️ Auto-apply warning if enabled"]
    end
    
    subgraph "Chat Mode"
        ChatIcon["💬 Chat mode"]
        ChatDesc["Conversation without file changes"]
        ChatSwitch["Auto-suggest tell mode switch"]
    end
    
    subgraph "Mode Transitions"
        TellToChat["\\chat command"]
        ChatToTell["\\tell command"]
        AutoSwitch["Regex-based auto-switch detection"]
    end
    
    TellIcon --> TellToChat
    TellToChat --> ChatIcon
    ChatIcon --> ChatToTell
    ChatToTell --> TellIcon
    ChatIcon --> AutoSwitch
    AutoSwitch --> TellIcon
```

**Sources:** [app/cli/cmd/repl.go:889-912](), [app/cli/cmd/repl.go:483-516](), [app/cli/cmd/repl.go:1177-1204]()

## Autocomplete and Suggestion System

The REPL provides intelligent autocomplete based on context, commands, and file paths:

```mermaid
graph TB
    subgraph "Suggestion Sources"
        BuiltInCmds["Built-in REPL commands"]
        CliCommandsList["term.CliCommands filtered by .Repl"]
        ActivePaths["projectPaths.ActivePaths"]
        FileExtensions["Markdown/text files for \\run"]
    end
    
    subgraph "Suggestion Processing"
        GetSuggestions["getSuggestions()"]
        FilterFuzzy["prompt.FilterFuzzy()"]
        FilterPrefix["prompt.FilterHasPrefix()"]
        SortByPriority["Sort by command priority"]
    end
    
    subgraph "Context-Aware Filtering"
        MultiLineCheck["Check IsMulti state"]
        ModeCheck["Check current mode"]
        CommandValidation["Validate command prefixes"]
        FilePathValidation["Validate file paths"]
    end
    
    subgraph "Suggestion Types"
        CommandSuggestions["\\command suggestions"]
        FileSuggestions["@file suggestions"]
        LoadSuggestions["\\load file suggestions"]
        RunSuggestions["\\run file suggestions"]
        AliasSuggestions["Command aliases"]
    end
    
    BuiltInCmds --> GetSuggestions
    CliCommandsList --> GetSuggestions
    ActivePaths --> GetSuggestions
    FileExtensions --> GetSuggestions
    
    GetSuggestions --> FilterFuzzy
    GetSuggestions --> FilterPrefix
    FilterFuzzy --> SortByPriority
    FilterPrefix --> SortByPriority
    
    SortByPriority --> MultiLineCheck
    SortByPriority --> ModeCheck
    SortByPriority --> CommandValidation
    SortByPriority --> FilePathValidation
    
    CommandValidation --> CommandSuggestions
    FilePathValidation --> FileSuggestions
    CommandValidation --> LoadSuggestions
    FilePathValidation --> RunSuggestions
    CommandValidation --> AliasSuggestions
```

**Sources:** [app/cli/cmd/repl.go:222-292](), [app/cli/cmd/repl.go:521-762](), [app/cli/cmd/repl.go:645-723]()

## File Reference Processing

The REPL supports `@` prefixed file references for quick context loading:

```mermaid
graph TD
    subgraph "File Reference Detection"
        FindAtSymbol["Find last @ in input"]
        ValidatePosition["Check @ position validity"]
        ParsePaths["Split input by @ symbols"]
        FilterPaths["Filter valid paths"]
    end
    
    subgraph "Path Processing"
        CheckProjectPaths["projectPaths.ActivePaths[p]"]
        AutoComplete["Use suggestion if path incomplete"]
        BuildLoadArgs["Build load command arguments"]
        AddRecursiveFlag["Add -r flag for directories"]
    end
    
    subgraph "Command Execution"
        ExecLoadCmd["Execute load command"]
        PreserveBuffer["Preserve buffer before @"]
        InsertText["p.InsertTextMoveCursor()"]
        ErrorHandling["Handle load errors"]
    end
    
    FindAtSymbol --> ValidatePosition
    ValidatePosition --> ParsePaths
    ParsePaths --> FilterPaths
    
    FilterPaths --> CheckProjectPaths
    CheckProjectPaths --> AutoComplete
    AutoComplete --> BuildLoadArgs
    BuildLoadArgs --> AddRecursiveFlag
    
    AddRecursiveFlag --> ExecLoadCmd
    ExecLoadCmd --> PreserveBuffer
    PreserveBuffer --> InsertText
    ExecLoadCmd --> ErrorHandling
```

**Sources:** [app/cli/cmd/repl.go:354-394](), [app/cli/cmd/repl.go:936-966](), [app/cli/cmd/repl.go:257-289]()

## Multi-line Editing Support

The REPL provides multi-line editing capabilities with special handling:

| Feature | Single-line Mode | Multi-line Mode |
|---------|------------------|-----------------|
| Enter Behavior | Execute command | Add line break |
| Send Command | Automatic on enter | `\send` command |
| Mode Toggle | `\multi` to enable | `\multi` to disable |
| Visual Indicator | `1️⃣ Multi-line mode is disabled` | `🔢 Multi-line mode is enabled` |

```mermaid
graph LR
    subgraph "executeOnEnter() Logic"
        CheckInput["Check input for commands"]
        CheckMultiState["Check IsMulti state"]
        ReturnExecute["Return (0, true) to execute"]
        ReturnContinue["Return (0, false) to continue"]
    end
    
    subgraph "Multi-line Commands"
        SendCommand["\\send - execute buffer"]
        MultiToggle["\\multi - toggle mode"]
        QuitCommand["\\quit - exit REPL"]
        RunCommand["\\run - execute file"]
    end
    
    CheckInput --> CheckMultiState
    CheckMultiState --> ReturnExecute
    CheckMultiState --> ReturnContinue
    
    ReturnContinue --> SendCommand
    ReturnContinue --> MultiToggle
    ReturnContinue --> QuitCommand
    ReturnContinue --> RunCommand
```

**Sources:** [app/cli/cmd/repl.go:294-307](), [app/cli/cmd/repl.go:901-912](), [app/cli/cmd/repl.go:225-251]()

## Command Validation and Error Handling

The REPL includes sophisticated command validation and error recovery:

```mermaid
graph TD
    subgraph "Command Validation"
        CheckValidCommand["Check if command exists"]
        FuzzyMatching["findSimilarCommands()"]
        EditDistance["Calculate similarity scores"]
        ThresholdCheck["Check similarity threshold"]
    end
    
    subgraph "Error Recovery"
        SuggestOptions["Present command options"]
        UserSelection["term.SelectFromList()"]
        CancelOption["Cancel option"]
        PromptOption["Send as prompt option"]
        RetryExecution["Retry with selected command"]
    end
    
    subgraph "Fallback Handling"
        ModeBasedFallback["Mode-based execution"]
        TellExecution["Execute as tell command"]
        ChatExecution["Execute as chat command"]
        AutoSwitchDetection["Detect mode switch requests"]
    end
    
    CheckValidCommand --> FuzzyMatching
    FuzzyMatching --> EditDistance
    EditDistance --> ThresholdCheck
    
    ThresholdCheck --> SuggestOptions
    SuggestOptions --> UserSelection
    UserSelection --> CancelOption
    UserSelection --> PromptOption
    UserSelection --> RetryExecution
    
    RetryExecution --> ModeBasedFallback
    ModeBasedFallback --> TellExecution
    ModeBasedFallback --> ChatExecution
    ChatExecution --> AutoSwitchDetection
```

**Sources:** [app/cli/cmd/repl.go:1099-1120](), [app/cli/cmd/repl.go:420-460](), [app/cli/cmd/repl.go:483-516]()

## Integration with CLI Commands

The REPL seamlessly integrates with the main CLI command system:

| Integration Point | Implementation | Purpose |
|------------------|----------------|---------|
| Command Definitions | `term.CliCommands` array | Shared command metadata |
| Command Execution | `lib.ExecPlandexCommandWithParams()` | Execute CLI commands with session context |
| Session Tracking | `sessionId` parameter | Track REPL session for analytics |
| State Persistence | `lib.WriteHistory()`, `lib.WriteState()` | Maintain command history and REPL state |
| Configuration Access | `replConfig` variable | Access current plan configuration |

**Sources:** [app/cli/term/help.go:19-145](), [app/cli/cmd/repl.go:332-340](), [app/cli/cmd/repl.go:72-73]()

---

# Page: Plan Execution Commands

# Plan Execution Commands

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/cli/cmd/build.go](app/cli/cmd/build.go)
- [app/cli/cmd/chat.go](app/cli/cmd/chat.go)
- [app/cli/cmd/continue.go](app/cli/cmd/continue.go)
- [app/cli/cmd/debug.go](app/cli/cmd/debug.go)
- [app/cli/cmd/tell.go](app/cli/cmd/tell.go)
- [app/cli/lib/apply.go](app/cli/lib/apply.go)
- [app/cli/main.go](app/cli/main.go)
- [app/cli/plan_exec/action_menu.go](app/cli/plan_exec/action_menu.go)
- [app/cli/plan_exec/apply_exec.go](app/cli/plan_exec/apply_exec.go)
- [app/cli/plan_exec/build.go](app/cli/plan_exec/build.go)
- [app/cli/plan_exec/params.go](app/cli/plan_exec/params.go)
- [app/cli/plan_exec/tell.go](app/cli/plan_exec/tell.go)
- [app/cli/types/apply.go](app/cli/types/apply.go)
- [app/cli/types/exec.go](app/cli/types/exec.go)
- [app/cli/types/fs.go](app/cli/types/fs.go)

</details>



This document covers the core plan execution commands in Plandex that enable users to interact with AI models to implement coding tasks. These commands form the primary interface for sending prompts, continuing work, building changes, and managing the plan lifecycle.

For information about context management (loading files, URLs, notes), see [Context Management Commands](#2.3). For model configuration, see [Model Configuration Commands](#2.4).

## Command Overview

Plandex provides several commands for executing plans and interacting with AI models. These commands can be used both in standalone CLI mode and within the interactive REPL.

| Command | Alias | Description | Usage Context |
|---------|-------|-------------|---------------|
| `tell` | `t` | Send a prompt to implement a task | CLI/REPL |
| `continue` | `c` | Continue the current plan | CLI/REPL |
| `build` | `b` | Build pending changes without new prompts | CLI/REPL |
| `apply` | `a` | Apply pending changes to files | CLI/REPL |
| `chat` | `ch` | Ask questions without making changes | CLI/REPL |
| `debug` | `db` | Debug failing commands with AI assistance | CLI/REPL |

**Sources:** [app/cli/cmd/tell.go:24-31](), [app/cli/cmd/continue.go:18-23](), [app/cli/cmd/build.go:16-23](), [app/cli/lib/apply.go:37-42](), [app/cli/cmd/chat.go:15-22](), [app/cli/cmd/debug.go:31-37]()

## Core Execution Commands

### Tell Command

The `tell` command is the primary interface for describing tasks to AI models. It sends prompts to begin implementation work.

```bash
# Basic usage
plandex tell "Add a login form to the homepage"

# With file input
plandex tell -f requirements.txt

# With piped input
echo "Fix the validation bug" | plandex tell

# Implementation from chat discussion
plandex tell --from-chat
```

The command supports multiple input methods:
- Direct prompt argument
- File input via `-f` flag (`tellPromptFile`)
- Piped stdin data
- Interactive editor when no input provided
- Implementation flag (`--from-chat`) for transitioning from chat to implementation

**Tell Command Execution Flow:**

```mermaid
graph TD
    doTell["doTell()"] --> mustResolveAuth["auth.MustResolveAuthWithOrg()"]
    mustResolveAuth --> mustResolveProject["lib.MustResolveProject()"]
    mustResolveProject --> getTellPrompt["getTellPrompt()"]
    
    getTellPrompt --> checkInput{"Input method?"}
    checkInput -->|"args[0]"| directPrompt["Direct prompt"]
    checkInput -->|"tellPromptFile"| fileInput["os.ReadFile()"]
    checkInput -->|"stdin pipe"| pipeInput["bufio.NewReader(os.Stdin)"]
    checkInput -->|"none"| editorInput["getEditorPrompt()"]
    
    directPrompt --> createTellFlags["Create TellFlags struct"]
    fileInput --> createTellFlags
    pipeInput --> createTellFlags
    editorInput --> createTellFlags
    
    createTellFlags --> planExecTellPlan["plan_exec.TellPlan()"]
    planExecTellPlan --> checkAutoApply{"tellAutoApply?"}
    checkAutoApply -->|"true"| mustApplyPlan["lib.MustApplyPlan()"]
    checkAutoApply -->|"false"| done["Complete"]
```

**Sources:** [app/cli/cmd/tell.go:41-100](), [app/cli/cmd/tell.go:102-142](), [app/cli/plan_exec/tell.go:26-286]()

### Continue Command

The `continue` command resumes an existing plan without providing additional prompts, allowing the AI to continue working on the current task.

```bash
# Basic continue
plandex continue

# Continue in chat mode (no file changes)
plandex continue --chat
```

The command reuses the same execution pipeline as `tell` but with the `IsUserContinue` flag set to true.

**Sources:** [app/cli/cmd/continue.go:36-87]()

### Build Command

The `build` command processes pending changes without sending new prompts to AI models. It validates and prepares file modifications for review.

```bash
# Build pending changes
plandex build

# Build in background
plandex build --bg
```

**Build Process Flow:**

```mermaid
graph TD
    buildCmd["buildCmd.Run()"] --> buildExec["plan_exec.Build()"]
    buildExec --> checkContext["Check outdated context"]
    checkContext --> apiCall["api.Client.BuildPlan()"]
    apiCall --> streamCheck{"Background mode?"}
    streamCheck -->|"No"| streamUI["streamtui.StartStreamUI()"]
    streamCheck -->|"Yes"| return["Return immediately"]
    streamUI --> completion["Build completion"]
```

**Sources:** [app/cli/cmd/build.go:38-102](), [app/cli/plan_exec/build.go:17-105]()

### Apply Command

The `apply` command takes built changes and applies them to the actual project files. It handles file modifications, execution of apply scripts, and Git integration.

```bash
# Apply all pending changes
plandex apply

# Apply with automatic confirmation
plandex apply --yes

# Apply and commit changes
plandex apply --commit

# Apply without executing scripts
plandex apply --no-exec
```

**Apply Command Process Flow:**

```mermaid
graph TD
    MustApplyPlan["MustApplyPlan()"] --> checkPendingBuilds["Check HasPendingBuilds()"]
    checkPendingBuilds -->|"true"| buildRequired["Prompt to build first"]
    checkPendingBuilds -->|"false"| getProjectPaths["fs.GetProjectPaths()"]
    
    buildRequired --> buildPlanInlineFn["buildPlanInlineFn()"]
    buildPlanInlineFn --> getProjectPaths
    
    getProjectPaths --> CheckOutdatedContext["CheckOutdatedContextWithOutput()"]
    CheckOutdatedContext --> getCurrentPlanFiles["Get currentPlanFiles"]
    
    getCurrentPlanFiles --> checkChanges{"Has changes?"}
    checkChanges -->|"false"| noChanges["No changes to apply"]
    checkChanges -->|"true"| ApplyFiles["ApplyFiles()"]
    
    ApplyFiles --> checkApplyScript{"Has _apply.sh?"}
    checkApplyScript -->|"true"| handleApplyScript["handleApplyScript()"]
    checkApplyScript -->|"false"| onExecSuccess["onExecSuccess()"]
    
    handleApplyScript --> execApplyScript["execApplyScript()"]
    execApplyScript --> onExecSuccess
    onExecSuccess --> apiApplyPlan["apiApplyPlan()"]
    apiApplyPlan --> commitApplied["commitApplied()"]
```

**Sources:** [app/cli/lib/apply.go:37-252](), [app/cli/lib/apply.go:622-750]()

### Chat Command

The `chat` command enables conversational interaction without making file changes. It's useful for asking questions and exploring ideas.

```bash
# Ask a question
plandex chat "How does the authentication system work?"

# Chat with file context
plandex chat -f question.txt
```

Chat mode sets the `IsChatOnly` flag, which prevents file modifications while allowing full AI interaction.

**Sources:** [app/cli/cmd/chat.go:39-64]()

### Debug Command

The `debug` command helps fix failing commands by running them repeatedly and using Plandex to analyze and fix failures automatically.

```bash
# Debug a failing command (default 5 tries)
plandex debug "npm test"

# Debug with custom retry count
plandex debug 3 "go build ./..."

# Debug with commit on success
plandex debug --commit "docker build -t myapp ."
```

**Debug Command Execution Flow:**

```mermaid
graph TD
    doDebug["doDebug()"] --> parseTries["Parse tries count and command"]
    parseTries --> executeLoop["Execute command loop"]
    
    executeLoop --> execCommand["exec.Command with shell"]
    execCommand --> setProcessAttrs["SetPlatformSpecificAttrs()"]
    setProcessAttrs --> startCommand["execCmd.Start()"]
    
    startCommand --> setupSignalHandling["Setup SIGINT/SIGTERM handling"]
    setupSignalHandling --> waitForCompletion["execCmd.Wait()"]
    
    waitForCompletion --> checkSuccess{"Command succeeded?"}
    checkSuccess -->|"true"| success["Report success"]
    checkSuccess -->|"false"| checkAttempts{"More attempts?"}
    
    checkAttempts -->|"false"| failed["Command failed after all tries"]
    checkAttempts -->|"true"| createPrompt["Create debug prompt with output"]
    
    createPrompt --> planExecTellPlan["plan_exec.TellPlan() with IsUserDebug"]
    planExecTellPlan --> mustApplyPlan["lib.MustApplyPlan() with auto flags"]
    mustApplyPlan --> executeLoop
```

**Sources:** [app/cli/cmd/debug.go:44-269]()

## Execution Flags and Options

All execution commands share a common set of flags defined in `initExecFlags()`:

### Automation Flags

| Flag | Description | Default | Used By |
|------|-------------|---------|---------|
| `--bg` | Run in background | false | tell, continue, build |
| `--stop` | Stop after first response | false | tell, continue |
| `--no-build` | Skip building changes | false | tell, continue |
| `--auto-apply` | Automatically apply changes | false | tell, continue, build |
| `--auto-context` | Automatically load context | false | tell, continue, chat |
| `--smart-context` | Use smart context loading | false | tell, continue |
| `--no-exec` | Skip execution of apply scripts | false | tell, continue, build |
| `--auto-exec` | Automatically execute apply scripts | false | tell, continue, build |

### File and Editor Flags

| Flag | Description | Used By |
|------|-------------|---------|
| `-f, --file` | Read prompt from file | tell, chat |
| `--editor` | Specify editor (vim/nano) | tell |
| `--from-chat` | Begin implementation from chat | tell |

### Apply-Specific Flags

| Flag | Description | Default |
|------|-------------|---------|
| `--yes` | Auto-confirm file changes | false |
| `--commit` | Auto-commit after apply | false |
| `--no-commit` | Skip Git commit prompt | false |

### Debug-Specific Flags

| Flag | Description | Default |
|------|-------------|---------|
| `-c, --commit` | Commit after successful execution | false |

**Sources:** [app/cli/cmd/tell.go:36-38](), [app/cli/cmd/continue.go:25-34](), [app/cli/cmd/debug.go:41-42](), [app/cli/lib/apply.go:49-57]()

## Plan Execution Pipeline

The core execution logic is implemented in the `plan_exec` package, which orchestrates the interaction between CLI commands, API calls, and the streaming UI.

**Complete TellPlan Execution Flow:**

```mermaid
graph TD
    TellPlan["TellPlan(params, prompt, flags)"] --> PromptSyncModelsIfNeeded["PromptSyncModelsIfNeeded()"]
    PromptSyncModelsIfNeeded --> ListContext["api.Client.ListContext()"]
    ListContext --> GetProjectPaths["fs.GetProjectPaths()"]
    GetProjectPaths --> CheckOutdatedContext["params.CheckOutdatedContext()"]
    
    CheckOutdatedContext --> checkOutdated{"Context outdated?"}
    checkOutdated -->|"true, !didUpdate"| stopPlan["Stop plan execution"]
    checkOutdated -->|"false or didUpdate"| buildRequest["Build TellPlanRequest"]
    
    buildRequest --> setAuthVars["Set AuthVars"]
    setAuthVars --> setProjectPaths["Set ProjectPaths"]
    setProjectPaths --> setBuildMode["Set BuildMode (Auto/None)"]
    setBuildMode --> apiTellPlan["api.Client.TellPlan()"]
    
    apiTellPlan --> checkTrialLimit{"Trial limit exceeded?"}
    checkTrialLimit -->|"true"| promptUpgrade["Prompt for upgrade"]
    checkTrialLimit -->|"false"| checkBackground{"tellBg flag?"}
    
    checkBackground -->|"true"| returnBg["Return (background mode)"]
    checkBackground -->|"false"| startStreamUI["streamtui.StartStreamUI()"]
    
    startStreamUI --> checkBalance["Check trial balance if needed"]
    checkBalance --> checkChatOnly{"isChatOnly?"}
    checkChatOnly -->|"true"| showChatCmds["Show chat commands"]
    checkChatOnly -->|"false"| checkAutoApply{"autoApply or skipChangesMenu?"}
    
    checkAutoApply -->|"true"| complete["Complete execution"]
    checkAutoApply -->|"false"| getDiffs["getDiffs()"]
    getDiffs --> showHotkeyMenu["showHotkeyMenu()"]
    showHotkeyMenu --> handleHotkey["handleHotkey()"]
```

**Key Data Structures:**

- `ExecParams`: Contains `CurrentPlanId`, `CurrentBranch`, `AuthVars`, and `CheckOutdatedContext` function
- `TellFlags`: Contains execution flags like `TellBg`, `TellStop`, `AutoApply`, `IsChatOnly`, etc.
- `shared.TellPlanRequest`: API request with `Prompt`, `ConnectStream`, `BuildMode`, `ProjectPaths`, etc.
- `stream.OnStreamPlan`: Callback function for handling streaming responses

**Sources:** [app/cli/plan_exec/tell.go:26-286](), [app/cli/plan_exec/params.go:8-13](), [app/cli/plan_exec/action_menu.go:77-284]()

## Apply Execution Pipeline  

The apply process handles the actual modification of project files and execution of generated scripts.

**Apply Process Architecture:**

```mermaid
graph TD
    MustApplyPlan["MustApplyPlan()"] --> GetCurrentPlanState["api.Client.GetCurrentPlanState()"]
    GetCurrentPlanState --> extractFiles["Extract toApply and toRemove maps"]
    extractFiles --> ApplyFiles["ApplyFiles() - concurrent file operations"]
    
    ApplyFiles --> createRollback["Create ApplyRollbackPlan"]
    createRollback --> checkApplyScript{"_apply.sh exists?"}
    
    checkApplyScript -->|"false"| onExecSuccess["onExecSuccess()"]
    checkApplyScript -->|"true"| handleApplyScript["handleApplyScript()"]
    
    handleApplyScript --> showCommands["Show commands to execute"]
    showCommands --> confirmExec{"User confirms execution?"}
    confirmExec -->|"false"| rollbackPrompt["Prompt: Keep or rollback changes"]
    confirmExec -->|"true"| execApplyScript["execApplyScript()"]
    
    execApplyScript --> setupSignals["Setup signal handling (SIGINT, SIGTERM)"]
    setupSignals --> executeScript["Execute shell script"]
    executeScript --> checkExitCode{"Exit code == 0?"}
    
    checkExitCode -->|"false"| onExecFail["onExecFail callback"]
    checkExitCode -->|"true"| onExecSuccess
    
    onExecSuccess --> apiApplyPlan["api.Client.ApplyPlan()"]
    apiApplyPlan --> commitApplied["commitApplied() if Git repo"]
```

**Sources:** [app/cli/lib/apply.go:37-252](), [app/cli/lib/apply.go:254-574](), [app/cli/lib/apply.go:622-750]()

## Interactive Action Menu

After plan execution completes, users can interact with changes through a hotkey-driven menu system implemented in `action_menu.go`.

**Action Menu Flow:**

```mermaid
graph TD
    tellComplete["Plan execution complete"] --> getDiffs["getDiffs()"]
    getDiffs --> showHotkeyMenu["showHotkeyMenu()"]
    showHotkeyMenu --> handleHotkey["handleHotkey()"]
    
    handleHotkey --> keyInput{"User input?"}
    keyInput -->|"d"| diffUI["diff --ui (browser)"]
    keyInput -->|"g"| gitDiff["git diff format"]
    keyInput -->|"r"| rejectChanges["reject command"]
    keyInput -->|"a"| applyChanges["apply command"]
    keyInput -->|"f"| fullAutoMode["apply --full (REPL only)"]
    keyInput -->|"ArrowDown"| dropdownMenu["SelectFromList()"]
    keyInput -->|"q/Enter"| exitMenu["Exit menu"]
    
    diffUI --> showHotkeyMenu
    gitDiff --> showHotkeyMenu  
    rejectChanges --> exitUnlessDiffs["exitUnlessDiffs()"]
    applyChanges --> exitProgram["os.Exit(0)"]
    fullAutoMode --> exitProgram
    dropdownMenu --> executeSelected["Execute selected option"]
    executeSelected --> showHotkeyMenu
    exitUnlessDiffs --> showHotkeyMenu
```

### Available Hotkeys

| Key | Command | Description | Context |
|-----|---------|-------------|---------|
| `d` | `diff ui` | Review diffs in browser UI | All |
| `g` | `git diff format` | Review diffs in git diff format | All |  
| `r` | `reject` | Reject some or all pending changes | All |
| `a` | `apply` | Apply all pending changes | All |
| `f` | `full auto` | Apply and debug in full auto mode | REPL only, with apply script |
| `↓` | dropdown | Show dropdown menu | All |
| `q`/`Enter` | exit | Exit menu | All |

**Sources:** [app/cli/plan_exec/action_menu.go:28-75](), [app/cli/plan_exec/action_menu.go:77-150](), [app/cli/plan_exec/action_menu.go:152-284]()

## Auto-Apply and Retry Logic

When execution fails (particularly with apply scripts), Plandex provides sophisticated retry and debugging capabilities.

**Apply Failure Handling:**

```mermaid
graph TD
    execApplyScript["execApplyScript()"] --> commandFail{"Command failed?"}
    commandFail -->|"false"| onSuccess["onSuccess()"]
    commandFail -->|"true"| getOnApplyExecFail["getOnApplyExecFail()"]
    
    getOnApplyExecFail --> checkAutoDebug{"AutoDebug > 0?"}
    checkAutoDebug -->|"true, attempt < AutoDebug"| autoRetry["Automatic retry"]
    checkAutoDebug -->|"false or exceeded"| userPrompt["User selection menu"]
    
    userPrompt --> userChoice{"User choice?"}
    userChoice -->|"Debug and retry once"| manualRetry["proceed = true"]
    userChoice -->|"Debug in full auto mode"| enableFullAuto["Enable full auto mode"]
    userChoice -->|"Rollback and exit"| rollback["lib.Rollback()"]
    userChoice -->|"Apply and exit"| applyAnyway["onSuccess()"]
    
    autoRetry --> createDebugPrompt["Create debug prompt with exit status and output"]
    manualRetry --> createDebugPrompt
    enableFullAuto --> updatePlanConfig["api.Client.UpdatePlanConfig()"]
    updatePlanConfig --> createDebugPrompt
    
    createDebugPrompt --> tellPlanDebug["TellPlan() with IsApplyDebug=true"]
    tellPlanDebug --> mustApplyPlanAttempt["lib.MustApplyPlanAttempt(attempt+1)"]
    mustApplyPlanAttempt --> execApplyScript
```

**Sources:** [app/cli/plan_exec/apply_exec.go:26-169](), [app/cli/lib/apply.go:254-318]()

## Error Handling and Validation

Plan execution includes comprehensive error handling for common scenarios:

### Context Validation
- Outdated context detection and auto-update prompts
- Missing context warnings
- File path validation

### API Error Handling  
- Trial message limits with upgrade prompts
- Authentication failures
- Model provider errors with fallbacks

### Build Validation
- Syntax error detection
- File modification conflicts
- Git repository state checks

**Sources:** [app/cli/plan_exec/tell.go:78-97](), [app/cli/plan_exec/tell.go:161-189]()

---

# Page: Context Management Commands

# Context Management Commands

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/cli/lib/context_load.go](app/cli/lib/context_load.go)
- [app/cli/lib/context_update.go](app/cli/lib/context_update.go)
- [app/cli/types/types.go](app/cli/types/types.go)

</details>



This document covers the CLI commands and underlying system for managing project context in Plandex plans. Context management includes loading files, directories, URLs, notes, and other content into a plan's context, as well as keeping that context synchronized with changes in the filesystem.

For information about the overall plan execution system that uses this context, see [Plan Execution System](#3). For details about the streaming terminal interface during context operations, see [Streaming Terminal UI](#2.5).

## Overview and Context Types

Plandex context management handles multiple types of content that can be loaded into a plan's working context. The system processes these context types through the `MustLoadContext` function and related infrastructure.

### Supported Context Types

| Context Type | Description | Source |
|--------------|-------------|--------|
| `ContextFileType` | Individual files with full content | Local filesystem |
| `ContextDirectoryTreeType` | Directory structures (names only) | Local filesystem |
| `ContextMapType` | Code definitions and structure maps | Local filesystem |
| `ContextURLType` | Web content from URLs | Remote web resources |
| `ContextNoteType` | User-provided text notes | Command line input |
| `ContextPipedDataType` | Data piped from other commands | Standard input |
| `ContextImageType` | Image files (base64 encoded) | Local filesystem |

Sources: [app/cli/lib/context_load.go:60-87](), [shared types for context types]()

## Context Loading Process

The context loading system processes different resource types through a unified pipeline that handles concurrent processing, size limits, and conflict detection.

```mermaid
graph TD
    CLI["CLI load command"] --> Parse["ParseInputPaths()"]
    Parse --> Filter["Filter ignored paths"]
    Filter --> Branch{Context Type}
    
    Branch --> File["ContextFileType"]
    Branch --> Dir["ContextDirectoryTreeType"] 
    Branch --> Map["ContextMapType"]
    Branch --> URL["ContextURLType"]
    Branch --> Note["ContextNoteType"]
    Branch --> Pipe["ContextPipedDataType"]
    
    File --> FileProcess["Read file content<br/>Calculate SHA256<br/>Estimate tokens"]
    Dir --> DirProcess["Parse directory tree<br/>Filter active paths<br/>Apply size limits"]
    Map --> MapProcess["Process code definitions<br/>Batch file mapping<br/>Handle large files"]
    URL --> URLProcess["FetchURLContent()<br/>Sanitize URL name<br/>Size validation"]
    Note --> NoteProcess["Direct text input<br/>Token estimation"]
    Pipe --> PipeProcess["Read from stdin<br/>Process as text"]
    
    FileProcess --> LoadReq["LoadContextRequest"]
    DirProcess --> LoadReq
    MapProcess --> LoadReq  
    URLProcess --> LoadReq
    NoteProcess --> LoadReq
    PipeProcess --> LoadReq
    
    LoadReq --> Conflicts["checkContextConflicts()"]
    Conflicts --> APICall["api.Client.LoadContext()"]
    APICall --> Response["LoadContextResponse"]
```

Sources: [app/cli/lib/context_load.go:26-757](), [app/cli/lib/context_load.go:94-610]()

### Concurrent Processing and Limits

The context loading system uses goroutines with a semaphore to control concurrency and applies multiple size and count limits:

```mermaid
graph LR
    Sem["Semaphore<br/>ContextMapMaxClientConcurrency"] --> Routines["Parallel goroutines<br/>per file/URL"]
    
    Routines --> Limits{Apply Limits}
    Limits --> SizeLimit["MaxContextBodySize<br/>per item"]
    Limits --> CountLimit["MaxContextCount<br/>total contexts"]
    Limits --> MapLimit["MaxContextMapPaths<br/>for definitions"]
    
    SizeLimit --> Skip1["filesSkippedTooLarge"]
    CountLimit --> Skip2["filesSkippedAfterSizeLimit"] 
    MapLimit --> Skip3["mapFilesSkippedAfterSizeLimit"]
    
    Skip1 --> Report["printSkippedFilesMsg()"]
    Skip2 --> Report
    Skip3 --> Report
```

Sources: [app/cli/lib/context_load.go:155-156](), [app/cli/lib/context_load.go:358-399](), [app/cli/lib/context_load.go:752-756]()

## Context Update and Synchronization

The context update system detects when loaded context has become outdated compared to the filesystem and provides mechanisms to synchronize changes.

### Outdated Context Detection

```mermaid
graph TD
    Check["CheckOutdatedContextWithOutput()"] --> List["api.Client.ListContext()"]
    List --> Parallel{Process Each Context Type}
    
    Parallel --> FileCheck["File Context Check"]
    Parallel --> DirCheck["Directory Tree Check"] 
    Parallel --> MapCheck["Map Context Check"]
    Parallel --> URLCheck["URL Context Check"]
    
    FileCheck --> FileSHA["Compare SHA256<br/>os.ReadFile()<br/>NormalizeEOL()"]
    DirCheck --> DirSHA["ParseInputPaths()<br/>Join paths<br/>Compare SHA256"]
    MapCheck --> MapSHA["Check each map file<br/>getMapFileDetails()<br/>Batch processing"]
    URLCheck --> URLSHA["FetchURLContent()<br/>Compare SHA256"]
    
    FileSHA --> Changed{Has Changed?}
    DirSHA --> Changed
    MapSHA --> Changed
    URLCheck --> Changed
    
    Changed -->|Yes| UpdateReq["Add to UpdateContextParams"]
    Changed -->|No| Skip["Skip update"]
    
    UpdateReq --> TokenDiff["Calculate token diff"]
    TokenDiff --> Result["ContextOutdatedResult"]
```

Sources: [app/cli/lib/context_update.go:24-196](), [app/cli/lib/context_update.go:289-1025]()

### Update Request Processing

The system builds update requests through concurrent processing while maintaining consistency:

```mermaid
graph LR
    OutdatedRes["ContextOutdatedResult"] --> ReqFn["ReqFn() function"]
    ReqFn --> Concurrent["Concurrent request building"]
    
    Concurrent --> FileReq["File update requests<br/>new Body content"]
    Concurrent --> MapReq["Map update requests<br/>MapBodies, InputShas<br/>RemovedMapPaths"]
    Concurrent --> URLReq["URL update requests<br/>new Body content"]
    
    FileReq --> Collect["Collect all requests"]
    MapReq --> Collect
    URLReq --> Collect
    
    Collect --> APIUpdate["api.Client.UpdateContext()"]
    APIUpdate --> Conflicts["Check conflicts"]
    Conflicts --> Build["Auto-trigger build if conflicts"]
```

Sources: [app/cli/lib/context_update.go:936-961](), [app/cli/lib/context_update.go:209-287]()

## Key Data Structures

### LoadContextParams

The `LoadContextParams` struct controls how context loading behaves:

```go
type LoadContextParams struct {
    Note              string                // Direct text note content
    Recursive         bool                  // Load directories recursively  
    NamesOnly         bool                  // Directory tree mode (names only)
    ForceSkipIgnore   bool                  // Ignore .gitignore/.plandexignore
    ImageDetail       openai.ImageURLDetail // Image processing detail level
    DefsOnly          bool                  // Load code definitions only (maps)
    SkipIgnoreWarning bool                  // Suppress ignore warnings
    AutoLoaded        bool                  // Automatically loaded context
    SessionId         string                // Session identifier
}
```

Sources: [app/cli/types/types.go:10-20]()

### Context Processing Results

The `ContextOutdatedResult` tracks what changed during context checking:

```go
type ContextOutdatedResult struct {
    Msg             string                     // Status message
    UpdatedContexts []*shared.Context         // Contexts that changed
    RemovedContexts []*shared.Context         // Contexts that were deleted
    TokenDiffsById  map[string]int            // Token count changes by context ID
    NumFiles        int                       // Number of updated files
    NumUrls         int                       // Number of updated URLs  
    NumTrees        int                       // Number of updated directory trees
    NumMaps         int                       // Number of updated maps
    NumFilesRemoved int                       // Number of removed files
    NumTreesRemoved int                       // Number of removed trees
    ReqFn           func() (map[string]*shared.UpdateContextParams, error) // Update function
}
```

Sources: [app/cli/types/types.go:22-34]()

## CLI Command Integration

Context management commands integrate with the broader CLI system through several entry points:

### Command Processing Flow

```mermaid
graph TD
    CLICmd["CLI Command"] --> CmdType{Command Type}
    
    CmdType --> Load["plandex load"]
    CmdType --> Update["Auto-update check"]
    CmdType --> Tell["plandex tell<br/>(auto-context)"]
    
    Load --> LoadParams["Parse LoadContextParams"]
    LoadParams --> LoadCall["MustLoadContext()"]
    
    Update --> UpdateCheck["CheckOutdatedContextWithOutput()"]
    UpdateCheck --> Confirm["User confirmation"]
    Confirm --> UpdateCall["UpdateContextWithOutput()"]
    
    Tell --> AutoLoad["Auto-load context"]
    AutoLoad --> LoadCall
    
    LoadCall --> Response["Display results"]
    UpdateCall --> Response
    Response --> BuildCheck["Check conflicts"]
    BuildCheck --> AutoBuild["buildPlanInlineFn()"]
```

Sources: [app/cli/lib/context_load.go:26](), [app/cli/lib/context_update.go:24](), [app/cli/lib/context_load.go:733-740]()

---

# Page: Model Configuration Commands

# Model Configuration Commands

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/cli/cmd/model_packs.go](app/cli/cmd/model_packs.go)
- [app/cli/cmd/model_providers.go](app/cli/cmd/model_providers.go)
- [app/cli/cmd/models.go](app/cli/cmd/models.go)
- [app/cli/cmd/set_model.go](app/cli/cmd/set_model.go)
- [app/cli/lib/model_settings.go](app/cli/lib/model_settings.go)
- [app/server/handlers/models.go](app/server/handlers/models.go)
- [app/shared/ai_models_custom.go](app/shared/ai_models_custom.go)

</details>



This document covers CLI commands for configuring and managing AI models in Plandex. This includes selecting model packs, creating custom models and providers, and managing model-specific settings for different AI roles.

For information about how models are integrated with the execution system, see [AI Model Integration and Task Control](#3.2). For details about model pack data structures and configuration schemas, see [Model Configuration and Management](#5.1).

## Purpose and Scope

Model configuration commands allow users to:
- View current model settings for plans and organization defaults
- Select and switch between built-in model packs
- Create and manage custom models, providers, and model packs
- Configure model-specific parameters like temperature and token limits
- Manage different AI model roles (planner, architect, coder, builder, etc.)

## Core Concepts

### Model Roles
Plandex assigns different AI models to specialized roles during plan execution:
- **Planner**: Orchestrates the overall development plan
- **Architect**: Designs system architecture and file structure
- **Coder**: Implements specific code changes
- **Builder**: Processes and validates file modifications
- **PlanSummary**: Generates plan summaries
- **Namer**: Creates names for plans and commits
- **CommitMsg**: Generates commit messages
- **ExecStatus**: Evaluates execution status

### Model Packs
Model packs are predefined configurations that assign specific models to each role. They include built-in packs (like "daily-driver" and "opus-planner") and custom user-defined packs.

### Custom Models and Providers
Users can define custom models that use various providers (OpenAI, Anthropic, custom endpoints, etc.) and create model packs that utilize these custom models.

Sources: [app/cli/cmd/models.go:364-507](), [app/shared/ai_models_custom.go:25-306]()

## Command Hierarchy

```mermaid
graph TD
    models["plandex models"]
    setModel["plandex set-model"]
    modelPacks["plandex model-packs"]
    providers["plandex providers"]
    
    models --> modelsDefault["models default"]
    models --> modelsAvailable["models available"]
    models --> modelsCustom["models custom"]
    
    setModel --> setModelDefault["set-model default"]
    
    modelPacks --> modelPacksShow["model-packs show"]
    modelPacks --> modelPacksCustom["model-packs --custom"]
    
    modelsAvailable --> modelsAvailableCustom["models available --custom"]
    
    modelsCustom --> customSave["models custom --save"]
    modelsCustom --> customFile["models custom --file"]
    
    setModel --> setModelJson["set-model --json"]
    setModel --> setModelFile["set-model --file"]
    setModel --> setModelSave["set-model --save"]
    
    setModelDefault --> defaultJson["set-model default --json"]
    setModelDefault --> defaultFile["set-model default --file"]
    setModelDefault --> defaultSave["set-model default --save"]
    
    style models fill:#e1f5fe
    style setModel fill:#fff3e0
    style modelPacks fill:#f3e5f5
    style providers fill:#e8f5e8
```

Sources: [app/cli/cmd/models.go:28-44](), [app/cli/cmd/set_model.go:23-35](), [app/cli/cmd/model_packs.go:51-59](), [app/cli/cmd/model_providers.go:42-47]()

## Viewing Model Configurations

### Current Plan Model Settings

The `plandex models` command displays the current model configuration for the active plan:

```bash
plandex models           # Show current plan's model settings
plandex models --all     # Show all model properties including temperature, top-p
```

This command calls the `models()` function which:
1. Retrieves the current plan via `api.Client.GetPlan()`
2. Fetches plan settings via `api.Client.GetSettings()`
3. Renders the model pack information using `renderSettings()`

The output includes:
- Current model pack name and description
- Models assigned to each role
- Token limits and model-specific parameters (with `--all` flag)

Sources: [app/cli/cmd/models.go:240-277]()

### Organization Default Settings

The `plandex models default` command shows organization-wide default model settings:

```bash
plandex models default
```

This retrieves default settings via `api.Client.GetOrgDefaultSettings()` and displays them using the same rendering logic as plan-specific settings.

Sources: [app/cli/cmd/models.go:279-302]()

### Available Models

List all available models (built-in and custom):

```bash
plandex models available         # List all models
plandex models available --custom # List only custom models
```

The `listAvailableModels()` function:
- Fetches custom models via `api.Client.ListCustomModels()`
- Displays built-in models from `shared.BuiltInBaseModels`
- Shows model capabilities (input tokens, output tokens, reserved tokens)

Sources: [app/cli/cmd/models.go:304-362]()

## Setting Model Configurations

### Model Pack Selection

Set a model pack for the current plan or organization defaults:

```bash
plandex set-model [model-pack-name]          # Set for current plan
plandex set-model default [model-pack-name]  # Set organization default
```

The model selection flow:

```mermaid
graph TD
    setModelCmd["set-model command"]
    hasArg{"Has model pack name?"}
    useJson{"Use JSON file?"}
    
    setModelCmd --> hasArg
    hasArg -->|Yes| findPack["Find model pack by name"]
    hasArg -->|No| promptUser["Prompt: Select pack or edit JSON?"]
    
    promptUser --> selectPack["Select model pack"]
    promptUser --> useJson
    
    useJson -->|Yes| jsonFlow["JSON file workflow"]
    selectPack --> findPack
    findPack --> updateSettings["Update plan settings"]
    
    jsonFlow --> writeFile["Write model settings JSON"]
    jsonFlow --> openEditor["Open file in editor"]
    jsonFlow --> saveChanges["Apply changes from JSON"]
    saveChanges --> updateSettings
    
    updateSettings --> apiCall["api.Client.UpdateSettings()"]
    
    style setModelCmd fill:#e1f5fe
    style jsonFlow fill:#fff3e0
    style updateSettings fill:#f3e5f5
```

Sources: [app/cli/cmd/set_model.go:52-135](), [app/cli/cmd/set_model.go:137-379]()

### JSON-Based Configuration

For advanced configuration, users can edit model settings as JSON:

```bash
plandex set-model --json              # Edit current plan settings
plandex set-model default --json      # Edit default settings
plandex set-model --file path.json    # Use specific file
plandex set-model --save              # Apply changes from existing file
```

The JSON workflow:
1. Generates a JSON file with current settings via `lib.WriteModelSettingsFile()`
2. Opens the file for editing (with optional editor prompt)
3. Validates changes using schema validation
4. Applies changes via `lib.ApplyModelSettings()`

Sources: [app/cli/cmd/set_model.go:231-303](), [app/cli/lib/model_settings.go:73-151]()

## Managing Custom Models and Providers

### Custom Models Management

The `plandex models custom` command provides a comprehensive interface for managing custom models, providers, and model packs:

```bash
plandex models custom               # Manage custom configurations
plandex models custom --save        # Apply changes from file
plandex models custom --file path   # Use specific file path
```

The custom models workflow:

```mermaid
graph TD
    customCmd["models custom"]
    hasChanges{"Has existing custom models?"}
    
    customCmd --> getServerInput["lib.GetServerModelsInput()"]
    customCmd --> getDefaultConfig["api.Client.GetDefaultPlanConfig()"]
    
    getServerInput --> hasChanges
    hasChanges -->|No| createTemplate["Create example template"]
    hasChanges -->|Yes| checkConflicts["Check for local changes"]
    
    createTemplate --> writeExample["Write example JSON file"]
    checkConflicts --> hasConflicts{"Has local changes?"}
    
    hasConflicts -->|Yes| warnUser["Warn about conflicts"]
    hasConflicts -->|No| writeFile["Write current config to file"]
    
    warnUser --> userChoice{"User confirms?"}
    userChoice -->|Yes| writeFile
    userChoice -->|No| exit["Exit"]
    
    writeFile --> openEditor["Open file for editing"]
    writeExample --> openEditor
    
    openEditor --> syncChanges["lib.MustSyncCustomModels()"]
    syncChanges --> serverUpdate["Update server via API"]
    
    style customCmd fill:#e1f5fe
    style createTemplate fill:#fff3e0
    style syncChanges fill:#f3e5f5
```

Sources: [app/cli/cmd/models.go:93-238]()

### Example Template Structure

When no custom models exist, the system generates an example template via `getExampleTemplate()`:

```json
{
  "$schema": "https://plandex.ai/schemas/models-input.schema.json",
  "providers": [
    {
      "name": "togetherai",
      "baseUrl": "https://api.together.xyz/v1",
      "apiKeyEnvVar": "TOGETHER_API_KEY"
    }
  ],
  "models": [
    {
      "modelId": "meta-llama/llama-4-maverick",
      "publisher": "meta-llama",
      "description": "Meta Llama 4 Maverick",
      "maxTokens": 1048576,
      "providers": [...]
    }
  ],
  "modelPacks": [
    {
      "name": "example-model-pack",
      "description": "Example model pack",
      "planner": "deepseek/r1",
      "architect": "deepseek/r1",
      "coder": {...}
    }
  ]
}
```

Sources: [app/cli/cmd/models.go:516-612]()

### Model Providers

View available model providers:

```bash
plandex providers                # List all providers
plandex providers --custom       # List only custom providers
```

The providers list shows:
- Built-in providers (OpenAI, Anthropic, Google, etc.)
- Base URLs and authentication requirements
- Custom providers (self-hosted only)

Sources: [app/cli/cmd/model_providers.go:49-163]()

### Model Packs Management

List and inspect model packs:

```bash
plandex model-packs              # List all model packs
plandex model-packs --custom     # List only custom packs
plandex model-packs show [name]  # Show detailed pack configuration
```

The `showModelPack()` function displays:
- Model pack metadata (name, description)
- Role-to-model assignments
- Fallback configurations (large-context, large-output, error fallbacks)
- Model parameters (temperature, top-p, token limits)

Sources: [app/cli/cmd/model_packs.go:125-202]()

## Server-Side Model Management

### Custom Models API

The server provides REST endpoints for managing custom models:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/custom_models` | POST | Create/update custom models, providers, packs |
| `/custom_models` | GET | List custom models |
| `/custom_providers` | GET | List custom providers |
| `/model_packs` | GET | List custom model packs |

The `UpsertCustomModelsHandler` performs comprehensive validation:
- Checks for duplicate names/IDs
- Validates provider references
- Ensures model compatibility with cloud/local environments
- Performs atomic updates using database transactions

Sources: [app/server/handlers/models.go:19-339]()

### Data Flow for Custom Models

```mermaid
graph LR
    cliFile["CLI JSON File"]
    validation["Schema Validation"]
    serverAPI["Server API"]
    database[("PostgreSQL Database")]
    
    cliFile --> validation
    validation --> serverAPI
    serverAPI --> upsertValidation["Upsert Validation"]
    upsertValidation --> dbTransaction["Database Transaction"]
    dbTransaction --> database
    
    database --> customModels[("custom_models table")]
    database --> customProviders[("custom_providers table")]
    database --> modelPacks[("model_packs table")]
    
    serverAPI --> listEndpoints["List Endpoints"]
    listEndpoints --> cliDisplay["CLI Display"]
    
    style validation fill:#e1f5fe
    style serverAPI fill:#fff3e0
    style dbTransaction fill:#f3e5f5
```

Sources: [app/server/handlers/models.go:290-328](), [app/shared/ai_models_custom.go:63-98]()

## Command Reference

| Command | Purpose | Key Flags |
|---------|---------|-----------|
| `plandex models` | Show current plan model settings | `--all` |
| `plandex models default` | Show organization default settings | |
| `plandex models available` | List available models | `--custom` |
| `plandex models custom` | Manage custom models/providers/packs | `--save`, `--file` |
| `plandex set-model [name]` | Set current plan model pack | `--json`, `--file`, `--save` |
| `plandex set-model default [name]` | Set organization default model pack | `--json`, `--file`, `--save` |
| `plandex model-packs` | List model packs | `--custom`, `--all` |
| `plandex model-packs show [name]` | Show model pack details | `--all` |
| `plandex providers` | List model providers | `--custom` |

Sources: [app/cli/cmd/models.go:46-91](), [app/cli/cmd/set_model.go:37-50](), [app/cli/cmd/model_packs.go:19-49](), [app/cli/cmd/model_providers.go:22-41]()

---

# Page: Streaming Terminal UI

# Streaming Terminal UI

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/cli/stream_tui/model.go](app/cli/stream_tui/model.go)
- [app/cli/stream_tui/run.go](app/cli/stream_tui/run.go)
- [app/cli/stream_tui/update.go](app/cli/stream_tui/update.go)
- [app/cli/stream_tui/view.go](app/cli/stream_tui/view.go)
- [app/server/types/active_plan.go](app/server/types/active_plan.go)

</details>



The Streaming Terminal UI provides a real-time, interactive interface for monitoring and controlling plan execution in Plandex. It displays live AI responses, build progress, and allows users to interact with the running plan through keyboard commands. This component is built using the Bubble Tea framework and handles all user-facing aspects of active plan execution.

For information about plan execution logic and server-side coordination, see [Plan Execution System](#3). For details about the REPL interface used outside of plan execution, see [REPL Interface](#2.1).

## Architecture Overview

The streaming UI operates as a client-side terminal application that receives real-time updates from the server via WebSocket-like streaming connections. The architecture separates concerns between UI rendering, state management, and message processing.

### Streaming UI Component Architecture

```mermaid
graph TB
    subgraph "Client Terminal Interface"
        StartStreamUI["StartStreamUI()"]
        streamUIModel["streamUIModel"]
        Update["Update()"]
        View["View()"]
        Send["Send()"]
    end
    
    subgraph "UI State Management"
        readState["readState()"]
        updateState["updateState()"]
        stateMu["stateMu sync.RWMutex"]
        updateDebouncer["UpdateDebouncer"]
    end
    
    subgraph "Message Processing"
        streamUpdate["streamUpdate()"]
        StreamMessage["shared.StreamMessage"]
        buildStatusPoll["buildStatusPollMsg"]
        contextLoadDone["contextLoadDoneMsg"]
    end
    
    subgraph "UI Components"
        mainViewport["mainViewport viewport.Model"]
        renderMainView["renderMainView()"]
        renderBuild["renderBuild()"]
        renderProcessing["renderProcessing()"]
        renderHelp["renderHelp()"]
    end
    
    subgraph "Server Streaming"
        ActivePlan["ActivePlan"]
        Stream["Stream()"]
        subscription["subscription"]
        streamCh["streamCh chan string"]
    end
    
    StartStreamUI --> streamUIModel
    streamUIModel --> Update
    streamUIModel --> View
    
    Update --> streamUpdate
    Update --> readState
    Update --> updateState
    
    streamUpdate --> StreamMessage
    
    View --> renderMainView
    View --> renderBuild
    View --> renderProcessing
    View --> renderHelp
    
    readState --> stateMu
    updateState --> stateMu
    updateState --> updateDebouncer
    
    Send --> StreamMessage
    StreamMessage --> subscription
    subscription --> streamCh
    streamCh --> ActivePlan
    ActivePlan --> Stream
    
    style streamUIModel fill:#e1f5fe
    style Update fill:#fff3e0
    style StreamMessage fill:#f3e5f5
    style ActivePlan fill:#e8f5e8
```

Sources: [app/cli/stream_tui/model.go:38-88](), [app/cli/stream_tui/update.go:25-169](), [app/cli/stream_tui/view.go:17-36](), [app/server/types/active_plan.go:48-93]()

### Message Flow and State Synchronization

```mermaid
sequenceDiagram
    participant User
    participant streamUIModel
    participant Update
    participant ActivePlan
    participant Server
    
    User->>streamUIModel: Key input / Window resize
    streamUIModel->>Update: tea.KeyMsg / tea.WindowSizeMsg
    
    Server->>ActivePlan: Plan execution events
    ActivePlan->>ActivePlan: Stream()
    ActivePlan->>streamUIModel: shared.StreamMessage
    streamUIModel->>Update: StreamMessage
    
    Update->>Update: streamUpdate()
    Update->>streamUIModel: updateState()
    Update->>streamUIModel: updateReplyDisplay()
    
    streamUIModel->>User: View() renders updated UI
    
    Note over Update: Message types: Reply, BuildInfo, Error, Finished
    Note over streamUIModel: State: reply, building, processing, finished
```

Sources: [app/cli/stream_tui/update.go:355-549](), [app/server/types/active_plan.go:186-311]()

## UI State Management

The `streamUIModel` struct maintains all UI state with thread-safe access patterns using read-write mutexes. State updates are coordinated through the `updateState()` and `readState()` functions to prevent race conditions during concurrent message processing.

### Core State Structure

| Field | Type | Purpose |
|-------|------|---------|
| `reply` | `string` | Accumulated AI response text |
| `mainDisplay` | `string` | Formatted display content |
| `processing` | `bool` | Indicates AI is generating response |
| `building` | `bool` | Indicates files are being built |
| `tokensByPath` | `map[string]int` | Token counts per file path |
| `finishedByPath` | `map[string]bool` | Build completion status per file |
| `mainViewport` | `viewport.Model` | Scrollable content viewport |
| `buildViewCollapsed` | `bool` | Build section visibility state |

Sources: [app/cli/stream_tui/model.go:38-88]()

### State Synchronization Patterns

```mermaid
graph LR
    subgraph "Thread-Safe State Access"
        readState["readState()"]
        updateState["updateState()"]
        stateMu["stateMu sync.RWMutex"]
    end
    
    subgraph "State Update Operations"
        updateReplyDisplay["updateReplyDisplay()"]
        updateViewportDimensions["updateViewportDimensions()"]
        windowResized["windowResized()"]
    end
    
    subgraph "Concurrent Access Points"
        Update["Update() tea.Msg handler"]
        streamUpdate["streamUpdate() message processor"]
        Tick["Tick() timer events"]
    end
    
    Update --> readState
    streamUpdate --> readState
    Tick --> readState
    
    Update --> updateState
    streamUpdate --> updateState
    
    updateState --> stateMu
    readState --> stateMu
    
    updateState --> updateReplyDisplay
    updateState --> updateViewportDimensions
    windowResized --> updateViewportDimensions
    
    style stateMu fill:#e1f5fe
    style updateState fill:#fff3e0
    style readState fill:#f3e5f5
```

Sources: [app/cli/stream_tui/model.go:228-238](), [app/cli/stream_tui/update.go:197-243]()

## Message Types and Processing

The streaming UI processes various message types from the server, each triggering specific UI updates and state changes. The `streamUpdate()` function serves as the central message dispatcher.

### Stream Message Types

```mermaid
graph TB
    subgraph "Core Message Types"
        StreamMessageReply["StreamMessageReply"]
        StreamMessageBuildInfo["StreamMessageBuildInfo"]
        StreamMessageError["StreamMessageError"]
        StreamMessageFinished["StreamMessageFinished"]
    end
    
    subgraph "Control Messages"
        StreamMessageMulti["StreamMessageMulti"]
        StreamMessageConnectActive["StreamMessageConnectActive"]
        StreamMessageDescribing["StreamMessageDescribing"]
        StreamMessageLoadContext["StreamMessageLoadContext"]
    end
    
    subgraph "Interactive Messages"
        StreamMessagePromptMissingFile["StreamMessagePromptMissingFile"]
        StreamMessageRepliesFinished["StreamMessageRepliesFinished"]
        StreamMessageAborted["StreamMessageAborted"]
    end
    
    subgraph "UI State Changes"
        updateReply["reply += msg.ReplyChunk"]
        updateBuilding["building = true"]
        setProcessing["processing = true/false"]
        showPrompt["promptingMissingFile = true"]
    end
    
    StreamMessageReply --> updateReply
    StreamMessageBuildInfo --> updateBuilding
    StreamMessageDescribing --> setProcessing
    StreamMessagePromptMissingFile --> showPrompt
    
    style StreamMessageReply fill:#e1f5fe
    style StreamMessageBuildInfo fill:#fff3e0
    style updateReply fill:#f3e5f5
    style updateBuilding fill:#e8f5e8
```

Sources: [app/cli/stream_tui/update.go:355-549](), [app/shared/stream.go]()

### Build Progress Message Handling

The UI tracks file build progress through `StreamMessageBuildInfo` messages, maintaining per-file token counts and completion status. Build display automatically collapses when too many files are being processed.

```mermaid
graph LR
    subgraph "Build Message Processing"
        BuildInfo["msg.BuildInfo"]
        tokensByPath["tokensByPath[path]"]
        finishedByPath["finishedByPath[path]"]
        removedByPath["removedByPath[path]"]
    end
    
    subgraph "Auto-Collapse Logic"
        getRows["getRows(false)"]
        rowCount["len(rows) > 3"]
        buildViewCollapsed["buildViewCollapsed = true"]
        userToggledBuild["userToggledBuild check"]
    end
    
    subgraph "Display Updates"
        renderBuild["renderBuild()"]
        updateViewportDimensions["updateViewportDimensions()"]
        Tick["Tick() for spinners"]
    end
    
    BuildInfo --> tokensByPath
    BuildInfo --> finishedByPath
    BuildInfo --> removedByPath
    
    getRows --> rowCount
    rowCount --> buildViewCollapsed
    userToggledBuild --> buildViewCollapsed
    
    buildViewCollapsed --> renderBuild
    renderBuild --> updateViewportDimensions
    
    BuildInfo --> Tick
    
    style BuildInfo fill:#e1f5fe
    style buildViewCollapsed fill:#fff3e0
    style renderBuild fill:#f3e5f5
```

Sources: [app/cli/stream_tui/update.go:432-489](), [app/cli/stream_tui/view.go:77-141]()

## User Interactions and Controls

The streaming UI supports various keyboard controls for navigation, plan control, and interaction with prompts. The `keymap` struct defines all available key bindings and their handlers.

### Keyboard Controls

| Key(s) | Function | Context |
|--------|----------|---------|
| `s` | Stop plan execution | Always available |
| `b` | Send plan to background | When `canSendToBg` is true |
| `j/k` | Scroll down/up | When not prompting missing file |
| `d/u` | Page down/up | When not prompting missing file |
| `g/G` | Go to start/end | When not prompting missing file |
| `↑/↓` | Navigate build view | When building |
| `Enter` | Select option | When prompting missing file |

Sources: [app/cli/stream_tui/model.go:90-103](), [app/cli/stream_tui/update.go:89-136]()

### Scroll and Navigation Handling

```mermaid
graph TB
    subgraph "Scroll State Management"
        atScrollBottom["atScrollBottom bool"]
        replyScrollable["replyScrollable()"]
        mainViewport["mainViewport viewport.Model"]
    end
    
    subgraph "Scroll Operations"
        scrollDown["scrollDown()"]
        scrollUp["scrollUp()"]
        pageDown["pageDown()"]
        pageUp["pageUp()"]
        scrollStart["scrollStart()"]
        scrollEnd["scrollEnd()"]
    end
    
    subgraph "Auto-Scroll Logic"
        updateReplyDisplay["updateReplyDisplay()"]
        GotoBottom["mainViewport.GotoBottom()"]
        checkAtBottom["AtBottom() check"]
    end
    
    replyScrollable --> scrollDown
    replyScrollable --> scrollUp
    
    scrollDown --> atScrollBottom
    scrollUp --> atScrollBottom
    
    updateReplyDisplay --> atScrollBottom
    atScrollBottom --> GotoBottom
    
    mainViewport --> replyScrollable
    mainViewport --> checkAtBottom
    
    style atScrollBottom fill:#e1f5fe
    style mainViewport fill:#fff3e0
    style updateReplyDisplay fill:#f3e5f5
```

Sources: [app/cli/stream_tui/update.go:275-353](), [app/cli/stream_tui/model.go:45-46]()

## Build Progress Display

The build progress section shows real-time status of file operations, with automatic collapsing for better space management. Progress is visualized using icons, token counts, and completion indicators.

### Build Display Components

```mermaid
graph TB
    subgraph "Build Header"
        getBuildHeader["getBuildHeader()"]
        buildStatusLabel["Building plan / Built plan"]
        collapseHint["(↓) collapse / (↑) expand"]
    end
    
    subgraph "File Status Display"
        getRows["getRows()"]
        fileIcon["📄 / 🚀 icons"]
        statusIndicator["✅ / ❌ / 🪙 / spinner"]
        filePath["File path display"]
    end
    
    subgraph "Layout Management"
        doRenderBuild["doRenderBuild()"]
        buildViewCollapsed["buildViewCollapsed state"]
        collapsedSummary["Collapsed summary view"]
        expandedRows["Full file list"]
    end
    
    getBuildHeader --> buildStatusLabel
    getBuildHeader --> collapseHint
    
    getRows --> fileIcon
    getRows --> statusIndicator
    getRows --> filePath
    
    doRenderBuild --> buildViewCollapsed
    buildViewCollapsed --> collapsedSummary
    buildViewCollapsed --> expandedRows
    
    style getBuildHeader fill:#e1f5fe
    style getRows fill:#fff3e0
    style buildViewCollapsed fill:#f3e5f5
```

Sources: [app/cli/stream_tui/view.go:147-175](), [app/cli/stream_tui/view.go:177-277]()

### File Status Indicators

The UI displays different indicators based on file processing state:

- **📄** - Regular file
- **🚀** - Command script (`_apply.sh`)
- **✅** - Build completed successfully
- **❌** - File removed/deleted
- **🪙 + number** - Token count during processing
- **Spinner** - Currently processing

Sources: [app/cli/stream_tui/view.go:205-223]()

## Missing File Prompts

When the AI needs to process a file not currently in context, the UI presents an interactive prompt allowing users to load the file, skip it, or allow overwriting.

### Missing File Prompt Flow

```mermaid
graph TB
    subgraph "Missing File Detection"
        checkMissingFile["checkMissingFile()"]
        MissingFilePath["msg.MissingFilePath"]
        MissingFileAutoContext["msg.MissingFileAutoContext"]
    end
    
    subgraph "Prompt Display"
        promptingMissingFile["promptingMissingFile = true"]
        renderMissingFilePrompt["renderMissingFilePrompt()"]
        missingFileSelectOpts["Load / Skip / Overwrite options"]
        missingFileSelectedIdx["Selected option index"]
    end
    
    subgraph "User Response"
        selectedMissingFileOpt["selectedMissingFileOpt()"]
        RespondMissingFile["api.Client.RespondMissingFile()"]
        promptChoices["RespondMissingFileChoice enum"]
    end
    
    MissingFilePath --> checkMissingFile
    MissingFileAutoContext --> checkMissingFile
    
    checkMissingFile --> promptingMissingFile
    promptingMissingFile --> renderMissingFilePrompt
    renderMissingFilePrompt --> missingFileSelectOpts
    
    missingFileSelectedIdx --> selectedMissingFileOpt
    selectedMissingFileOpt --> RespondMissingFile
    RespondMissingFile --> promptChoices
    
    style checkMissingFile fill:#e1f5fe
    style promptingMissingFile fill:#fff3e0
    style selectedMissingFileOpt fill:#f3e5f5
```

Sources: [app/cli/stream_tui/update.go:668-741](), [app/cli/stream_tui/update.go:622-666](), [app/cli/stream_tui/view.go:279-312]()

## Server-Side Streaming Infrastructure

The server maintains active plan subscriptions and manages message broadcasting to connected clients through the `ActivePlan` type and its streaming infrastructure.

### Subscription Management

```mermaid
graph LR
    subgraph "ActivePlan Streaming"
        Subscribe["Subscribe()"]
        Unsubscribe["Unsubscribe()"]
        subscriptions["subscriptions map"]
        streamCh["streamCh chan string"]
    end
    
    subgraph "Message Broadcasting"
        Stream["Stream()"]
        streamMessageBuffer["streamMessageBuffer"]
        FlushStreamBuffer["FlushStreamBuffer()"]
        MaxStreamRate["MaxStreamRate throttling"]
    end
    
    subgraph "Subscription Processing"
        newSubscription["newSubscription()"]
        processMessages["processMessages()"]
        enqueueMessage["enqueueMessage()"]
        messageQueue["messageQueue []string"]
    end
    
    Subscribe --> newSubscription
    newSubscription --> processMessages
    
    Stream --> streamMessageBuffer
    Stream --> MaxStreamRate
    MaxStreamRate --> FlushStreamBuffer
    
    streamCh --> enqueueMessage
    enqueueMessage --> messageQueue
    messageQueue --> processMessages
    
    subscriptions --> Subscribe
    subscriptions --> Unsubscribe
    
    style Subscribe fill:#e1f5fe
    style Stream fill:#fff3e0
    style processMessages fill:#f3e5f5
```

Sources: [app/server/types/active_plan.go:339-384](), [app/server/types/active_plan.go:186-311](), [app/server/types/active_plan.go:390-436]()

---

# Page: Plan Execution System

# Plan Execution System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/server/model/plan/tell_exec.go](app/server/model/plan/tell_exec.go)
- [app/server/model/plan/tell_load.go](app/server/model/plan/tell_load.go)
- [app/server/model/plan/tell_state.go](app/server/model/plan/tell_state.go)
- [app/server/model/plan/tell_stream_finish.go](app/server/model/plan/tell_stream_finish.go)
- [app/server/model/plan/tell_stream_main.go](app/server/model/plan/tell_stream_main.go)
- [app/server/model/plan/tell_stream_processor.go](app/server/model/plan/tell_stream_processor.go)
- [app/server/model/plan/tell_summary.go](app/server/model/plan/tell_summary.go)

</details>



This document covers the core plan execution engine that processes user requests, coordinates with AI models, and generates file modifications. The system handles the complete lifecycle from initial user input through AI model interaction to file operations and auto-continuation logic.

For information about the CLI commands that trigger plan execution, see [Plan Execution Commands](#2.2). For details about file modification and building, see [File Modification Pipeline](#3.3). For AI model configuration and management, see [AI Model Integration](#5).

## Core Execution Flow

The plan execution system centers around the `Tell` function and its associated streaming pipeline. When a user provides input through commands like `tell` or `continue`, the system orchestrates a complex flow involving context loading, AI model interaction, and response processing.

```mermaid
graph TD
    subgraph "Entry Points"
        TellAPI["Tell API Handler"]
        ContinueAPI["Continue API Handler"]
    end
    
    subgraph "Core Execution"
        TellFunc["Tell()"]
        ActivatePlan["activatePlan()"]
        ExecTellPlan["execTellPlan()"]
    end
    
    subgraph "Data Loading"
        LoadTellPlan["loadTellPlan()"]
        GetPlanContexts["db.GetPlanContexts()"]
        GetPlanConvo["db.GetPlanConvo()"]
        GetPlanSubtasks["db.GetPlanSubtasks()"]
    end
    
    subgraph "AI Interaction"
        FormatPrompt["formatModelContext()"]
        GetTellSysPrompt["getTellSysPrompt()"]
        DoTellRequest["doTellRequest()"]
        ListenStream["listenStream()"]
    end
    
    subgraph "Response Processing"
        ProcessChunk["processChunk()"]
        HandleOperations["handleNewOperations()"]
        HandleFinished["handleStreamFinished()"]
    end
    
    TellAPI --> TellFunc
    ContinueAPI --> TellFunc
    TellFunc --> ActivatePlan
    TellFunc --> ExecTellPlan
    
    ExecTellPlan --> LoadTellPlan
    LoadTellPlan --> GetPlanContexts
    LoadTellPlan --> GetPlanConvo
    LoadTellPlan --> GetPlanSubtasks
    
    ExecTellPlan --> FormatPrompt
    ExecTellPlan --> GetTellSysPrompt
    ExecTellPlan --> DoTellRequest
    DoTellRequest --> ListenStream
    
    ListenStream --> ProcessChunk
    ProcessChunk --> HandleOperations
    ListenStream --> HandleFinished
    
    HandleFinished --> ExecTellPlan
```

**Execution Orchestration Flow**

Sources: [app/server/model/plan/tell_exec.go:32-71](), [app/server/model/plan/tell_load.go:20-427](), [app/server/model/plan/tell_stream_main.go:20-284]()

## Plan Stages and State Management

The execution system operates through distinct stages managed by the `activeTellStreamState` structure. Each stage determines the appropriate AI model role and prompt formatting strategy.

```mermaid
graph LR
    subgraph "Planning Stages"
        ContextPhase["PlanningPhaseContext"]
        TasksPhase["PlanningPhaseTasks"] 
    end
    
    subgraph "Implementation Stage"
        ImplStage["TellStageImplementation"]
    end
    
    subgraph "Model Roles"
        Architect["Architect Model"]
        Planner["Planner Model"] 
        Coder["Coder Model"]
    end
    
    subgraph "State Components"
        ActiveState["activeTellStreamState"]
        CurrentStage["currentStage"]
        Subtasks["subtasks"]
        ModelContext["modelContext"]
        ConvoHistory["convo"]
    end
    
    ContextPhase --> Architect
    TasksPhase --> Planner
    ImplStage --> Coder
    
    ActiveState --> CurrentStage
    ActiveState --> Subtasks
    ActiveState --> ModelContext
    ActiveState --> ConvoHistory
    
    CurrentStage --> ContextPhase
    CurrentStage --> TasksPhase
    CurrentStage --> ImplStage
```

**Plan Stage Progression and Model Assignment**

The `currentStage` field in `activeTellStreamState` determines execution behavior:

| Stage | Model Role | Purpose | Token Limit Source |
|-------|------------|---------|-------------------|
| `PlanningPhaseContext` | Architect | Context analysis and file loading | `GetArchitectEffectiveMaxTokens()` |
| `PlanningPhaseTasks` | Planner | Task breakdown and planning | `GetPlannerEffectiveMaxTokens()` |
| `TellStageImplementation` | Coder | Code generation and file modification | `GetCoderEffectiveMaxTokens()` |

Sources: [app/server/model/plan/tell_state.go:14-69](), [app/server/model/plan/tell_exec.go:181-204]()

## Context and Token Management

The system performs sophisticated context loading and token management to stay within model limits while providing maximum relevant information.

```mermaid
graph TD
    subgraph "Context Loading"
        ResolveStage["resolveCurrentStage()"]
        FormatContext["formatModelContext()"]
        AutoContext["Auto Context Loading"]
        ManualContext["Manual Context Loading"]
    end
    
    subgraph "Token Calculation"
        DryRun["dryRunCalculateTokensWithoutContext()"]
        TokensBeforeConvo["tokensBeforeConvo"]
        ConvoTokens["conversationTokens"]
        ContextTokens["contextTokens"]
    end
    
    subgraph "Conversation Management"
        AddConvoMsgs["addConversationMessages()"]
        SummarizeConvo["summarizeConvo()"]
        ConvoSummary["ConvoSummary"]
    end
    
    ResolveStage --> FormatContext
    FormatContext --> AutoContext
    FormatContext --> ManualContext
    
    DryRun --> TokensBeforeConvo
    TokensBeforeConvo --> ConvoTokens
    ConvoTokens --> AddConvoMsgs
    AddConvoMsgs --> SummarizeConvo
    SummarizeConvo --> ConvoSummary
    
    ContextTokens --> FormatContext
```

**Context and Token Management Pipeline**

The system uses several strategies to manage context and tokens effectively:

- **Auto Context**: Automatically loads relevant files based on `activatePaths` and `activatePathsOrdered`
- **Token Estimation**: Pre-calculates token usage with `dryRunCalculateTokensWithoutContext()`
- **Conversation Summarization**: Uses `summarizeConvo()` to compress conversation history when token limits are exceeded
- **Smart Context**: Enables selective context loading based on relevance scoring

Sources: [app/server/model/plan/tell_exec.go:206-276](), [app/server/model/plan/tell_summary.go:22-231](), [app/server/model/plan/tell_summary.go:246-434]()

## Streaming Response Processing

The streaming system processes AI model responses in real-time, parsing operations and handling various content types including code blocks and file operations.

```mermaid
graph TD
    subgraph "Stream Management"
        ListenStream["listenStream()"]
        FirstTokenTimeout["firstTokenTimeout()"]
        StreamFinished["streamFinished"]
        UsageChunk["handleUsageChunk()"]
    end
    
    subgraph "Chunk Processing"
        ProcessChunk["processChunk()"]
        ChunkProcessor["chunkProcessor"]
        ReplyParser["replyParser"]
        BufferOrStream["bufferOrStream()"]
    end
    
    subgraph "Content Handling"
        FileOpen["fileOpen"]
        AwaitingTag["awaitingBlockOpeningTag"]
        AwaitingClosing["awaitingBlockClosingTag"]
        AwaitingBackticks["awaitingBackticks"]
    end
    
    subgraph "Operation Detection"
        HandleNewOps["handleNewOperations()"]
        QueueBuilds["queueBuilds()"]
        Operations["Operations[]"]
    end
    
    ListenStream --> FirstTokenTimeout
    ListenStream --> ProcessChunk
    ListenStream --> StreamFinished
    StreamFinished --> UsageChunk
    
    ProcessChunk --> ChunkProcessor
    ChunkProcessor --> ReplyParser
    ChunkProcessor --> BufferOrStream
    
    BufferOrStream --> FileOpen
    BufferOrStream --> AwaitingTag
    BufferOrStream --> AwaitingClosing
    BufferOrStream --> AwaitingBackticks
    
    ProcessChunk --> HandleNewOps
    HandleNewOps --> QueueBuilds
    HandleNewOps --> Operations
```

**Streaming Response Processing Architecture**

The `chunkProcessor` manages complex state for parsing structured content:

- **File Blocks**: Tracks `<PlandexBlock>` tags and converts them to markdown code blocks
- **Operation Parsing**: Detects file operations and queues them for building
- **Content Buffering**: Buffers partial content while waiting for complete tags
- **Stop Sequences**: Handles manual stop sequences and model finish reasons

Sources: [app/server/model/plan/tell_stream_main.go:20-284](), [app/server/model/plan/tell_stream_processor.go:29-593](), [app/server/model/plan/tell_state.go:71-81]()

## Error Handling and Retry Logic

The system implements comprehensive error handling with fallback mechanisms, retry logic, and model switching capabilities.

```mermaid
graph TD
    subgraph "Error Types"
        StreamErr["streamErr"]
        ModelErr["modelErr"] 
        TimeoutErr["Timeout Errors"]
        ContextCanceled["Context Canceled"]
    end
    
    subgraph "Error Handling"
        OnError["onError()"]
        ClassifyError["ClassifyModelError()"]
        FallbackLogic["GetFallbackForModelError()"]
        RetryLogic["Retry Logic"]
    end
    
    subgraph "Fallback Strategies"
        ProviderFallback["Provider Fallback"]
        ModelFallback["Model Fallback"]
        NumErrorRetry["numErrorRetry"]
        NumFallbackRetry["numFallbackRetry"]
    end
    
    subgraph "Recovery Actions"
        ExecHookOnStop["execHookOnStop()"]
        ResetModelCtx["ResetModelCtx()"]
        ContinueStream["Continue Stream"]
        StopExecution["Stop Execution"]
    end
    
    StreamErr --> OnError
    ModelErr --> ClassifyError
    TimeoutErr --> OnError
    ContextCanceled --> ExecHookOnStop
    
    OnError --> FallbackLogic
    ClassifyError --> FallbackLogic
    FallbackLogic --> ProviderFallback
    FallbackLogic --> ModelFallback
    
    FallbackLogic --> NumErrorRetry
    FallbackLogic --> NumFallbackRetry
    NumErrorRetry --> RetryLogic
    
    OnError --> ResetModelCtx
    OnError --> ContinueStream
    OnError --> StopExecution
```

**Error Handling and Recovery System**

The system tracks error state through multiple fields in `activeTellStreamState`:

- `numErrorRetry`: Count of retry attempts for the current request
- `numFallbackRetry`: Count of provider/model fallback attempts  
- `modelErr`: Classified model error for fallback decision making
- `didProviderFallback`: Tracks whether provider fallback has been attempted

Sources: [app/server/model/plan/tell_stream_main.go:102-144](), [app/server/model/plan/tell_exec.go:500-508]()

## Auto-Continuation and Completion Logic

The system automatically determines when to continue execution based on task completion, new subtasks, and context changes.

```mermaid
graph TD
    subgraph "Completion Analysis"
        HandleFinished["handleStreamFinished()"]
        CheckNewSubtasks["checkNewSubtasks()"]
        CheckRemoveSubtasks["checkRemoveSubtasks()"]
        CheckAutoLoadContext["checkAutoLoadContext()"]
    end
    
    subgraph "Decision Factors"
        HasExplicitTasks["hasExplicitTasks"]
        AllSubtasksFinished["allSubtasksFinished"] 
        AutoLoadPaths["autoLoadPaths"]
        HasExplicitPaths["hasExplicitPaths"]
    end
    
    subgraph "Continuation Logic"
        WillContinue["willContinuePlan()"]
        MaxIterations["MaxAutoContinueIterations"]
        AutoContinue["Auto Continue"]
        FinishPlan["Finish Plan"]
    end
    
    subgraph "State Updates"
        StoreOnFinished["storeOnFinished()"]
        UpdateSubtasks["Update Subtasks"]
        SummarizeBackground["Summarize in Background"]
    end
    
    HandleFinished --> CheckNewSubtasks
    HandleFinished --> CheckRemoveSubtasks  
    HandleFinished --> CheckAutoLoadContext
    
    CheckNewSubtasks --> HasExplicitTasks
    CheckAutoLoadContext --> AutoLoadPaths
    CheckAutoLoadContext --> HasExplicitPaths
    
    HasExplicitTasks --> WillContinue
    AllSubtasksFinished --> WillContinue
    AutoLoadPaths --> WillContinue
    HasExplicitPaths --> WillContinue
    
    WillContinue --> MaxIterations
    MaxIterations --> AutoContinue
    MaxIterations --> FinishPlan
    
    HandleFinished --> StoreOnFinished
    StoreOnFinished --> UpdateSubtasks
    HandleFinished --> SummarizeBackground
```

**Auto-Continuation Decision Tree**

The `willContinuePlan()` function evaluates multiple conditions:

1. **New Subtasks**: If explicit tasks were added, continue to implement them
2. **Context Changes**: If new files were auto-loaded, continue with updated context  
3. **Iteration Limit**: Respect `MaxAutoContinueIterations = 200` to prevent infinite loops
4. **Task Completion**: Stop if all subtasks are marked as finished

The system also handles background operations like conversation summarization and context loading timeouts during continuation decisions.

Sources: [app/server/model/plan/tell_stream_finish.go:25-277](), [app/server/model/plan/tell_stream_finish.go:18]()

## Missing File Handling

When the AI attempts to modify files not present in the current context, the system implements a user interaction flow to handle the situation gracefully.

```mermaid
graph LR
    subgraph "Detection"
        ProcessChunk["processChunk()"]
        MissingFileCheck["currentFile not in context"]
        ProjectPathsCheck["req.ProjectPaths[currentFile]"]
    end
    
    subgraph "User Interaction"
        HandleMissingFile["handleMissingFile()"]
        SetStatus["SetPlanStatus(MissingFile)"]
        PromptUser["StreamMessagePromptMissingFile"]
        WaitResponse["Wait for User Choice"]
    end
    
    subgraph "Resolution"
        UserChoice["RespondMissingFileChoice"]
        ContinueExecution["Continue execTellPlan()"]
        UpdateContext["Update AllowOverwritePaths"]
    end
    
    ProcessChunk --> MissingFileCheck
    MissingFileCheck --> ProjectPathsCheck
    ProjectPathsCheck --> HandleMissingFile
    
    HandleMissingFile --> SetStatus
    HandleMissingFile --> PromptUser
    PromptUser --> WaitResponse
    
    WaitResponse --> UserChoice
    UserChoice --> UpdateContext
    UpdateContext --> ContinueExecution
```

**Missing File Resolution Workflow**

The system detects missing files when `currentFile` exists in `req.ProjectPaths` but not in `active.ContextsByPath` and not in `active.AllowOverwritePaths`. This triggers a 30-minute timeout waiting for user response through `active.MissingFileResponseCh`.

Sources: [app/server/model/plan/tell_stream_processor.go:595-726](), [app/server/model/plan/tell_stream_processor.go:115-121]()

---

# Page: Plan Lifecycle and States

# Plan Lifecycle and States

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/server/model/plan/tell_exec.go](app/server/model/plan/tell_exec.go)
- [app/server/model/plan/tell_load.go](app/server/model/plan/tell_load.go)
- [app/server/model/plan/tell_state.go](app/server/model/plan/tell_state.go)
- [app/server/model/plan/tell_stream_finish.go](app/server/model/plan/tell_stream_finish.go)
- [app/server/model/plan/tell_stream_main.go](app/server/model/plan/tell_stream_main.go)
- [app/server/model/plan/tell_stream_processor.go](app/server/model/plan/tell_stream_processor.go)
- [app/server/model/plan/tell_summary.go](app/server/model/plan/tell_summary.go)

</details>



This document covers the plan execution lifecycle in Plandex, including the various states a plan transitions through from initial user prompt to final file modifications. It details the tell execution stages, streaming response processing, and active plan state management.

For information about the HTTP API endpoints that trigger these processes, see [HTTP API and Request Handlers](#4.1). For details about the AI model integration that powers plan execution, see [AI Model Integration and Task Control](#3.2).

## Plan State Overview

Plans in Plandex progress through several distinct database states during execution, with runtime coordination managed through `activeTellStreamState` and `ActivePlan` structures.

### Database Plan States

| State | Purpose | Set By |
|-------|---------|--------|
| `PlanStatusReplying` | Plan is actively generating AI responses | [tell_exec.go:140]() |
| `PlanStatusDescribing` | Plan is analyzing completion and next steps | [tell_stream_finish.go:61]() |
| `PlanStatusBuilding` | Plan is applying changes to files | [tell_stream_finish.go:251]() |
| `PlanStatusMissingFile` | Plan is waiting for user response about file overwrite | [tell_stream_processor.go:617]() |

**Plan State Transition Flow**

```mermaid
stateDiagram-v2
    [*] --> PlanStatusReplying: "Tell() activates plan"
    PlanStatusReplying --> PlanStatusDescribing: "Stream finished"
    PlanStatusDescribing --> PlanStatusReplying: "Auto-continue decision"
    PlanStatusDescribing --> PlanStatusBuilding: "willContinue=false"
    PlanStatusDescribing --> PlanStatusMissingFile: "File not in context"
    PlanStatusMissingFile --> PlanStatusReplying: "User response received"
    PlanStatusBuilding --> [*]: "Build complete, plan finished"
    PlanStatusReplying --> [*]: "Plan cancelled or error"
```

Sources: [tell_exec.go:140](), [tell_stream_finish.go:61](), [tell_stream_finish.go:251](), [tell_stream_processor.go:617]()

## Tell Execution Lifecycle

The tell execution process handles user prompts through a sophisticated multi-stage pipeline involving plan activation, stage determination, model selection, and streaming response processing.

### Main Execution Flow

**Tell Execution Entry Point**

```mermaid
graph TD
    TellRequest["TellPlanRequest"] --> Tell["Tell()"]
    Tell --> activatePlan["activatePlan()"]
    activatePlan --> execTellPlan["execTellPlan()"]
    
    execTellPlan --> loadTellPlan["loadTellPlan()"]
    loadTellPlan --> resolveCurrentStage["resolveCurrentStage()"]
    resolveCurrentStage --> modelSelection["Model selection based on stage"]
    
    modelSelection --> doTellRequest["doTellRequest()"]
    doTellRequest --> listenStream["listenStream()"]
    listenStream --> handleStreamFinished["handleStreamFinished()"]
```

Sources: [tell_exec.go:32-71](), [tell_exec.go:86-491](), [tell_load.go:20-427]()

### Tell Stages and Model Selection

The system uses different AI models based on the current execution stage:

| Stage | Phase | Model Used | Purpose |
|-------|-------|------------|---------|
| `TellStagePlanning` | `PlanningPhaseContext` | `GetArchitect()` | Load and analyze project context |
| `TellStagePlanning` | `PlanningPhaseTasks` | `Planner` | Break down work into subtasks |
| `TellStageImplementation` | - | `GetCoder()` | Generate code implementations |

**Stage and Model Selection Logic**

```mermaid
graph TD
    resolveCurrentStage["resolveCurrentStage()"] --> checkStage{"currentStage.TellStage"}
    
    checkStage -->|TellStagePlanning| checkPhase{"currentStage.PlanningPhase"}
    checkStage -->|TellStageImplementation| coderModel["ModelPack.GetCoder()"]
    
    checkPhase -->|PlanningPhaseContext| architectModel["ModelPack.GetArchitect()"]
    checkPhase -->|PlanningPhaseTasks| plannerModel["ModelPack.Planner"]
    
    architectModel --> GetRoleForInputTokens1["GetRoleForInputTokens()"]
    plannerModel --> GetRoleForInputTokens2["GetRoleForInputTokens()"]
    coderModel --> GetRoleForInputTokens3["GetRoleForInputTokens()"]
    
    GetRoleForInputTokens1 --> modelConfig["Final modelConfig"]
    GetRoleForInputTokens2 --> modelConfig
    GetRoleForInputTokens3 --> modelConfig
```

Sources: [tell_exec.go:181-204](), [tell_exec.go:397-409]()

### Plan Loading and State Initialization

**loadTellPlan Process**

```mermaid
graph TD
    loadTellPlan["loadTellPlan()"] --> parallelLoad["Parallel goroutines"]
    
    parallelLoad --> getPlanSettings["Get plan settings & orgUserConfig"]
    parallelLoad --> getPlanContexts["Get plan contexts"]
    parallelLoad --> getPlanConvo["Get conversation & summaries"]
    parallelLoad --> getPlanSubtasks["Get plan subtasks"]
    
    getPlanSettings --> renameDraft["Rename 'draft' plans"]
    getPlanContexts --> setContexts["Set modelContext"]
    getPlanConvo --> storeUserMessage["Store user message"]
    getPlanSubtasks --> setSubtasks["Set current subtask"]
    
    renameDraft --> getCurrentPlanState["GetCurrentPlanState()"]
    setContexts --> getCurrentPlanState
    storeUserMessage --> getCurrentPlanState
    setSubtasks --> getCurrentPlanState
    
    getCurrentPlanState --> updateActivePlan["Update ActivePlan state"]
```

Sources: [tell_load.go:56-338](), [tell_load.go:69-139](), [tell_load.go:141-169](), [tell_load.go:171-290](), [tell_load.go:292-309]()

## Streaming Response Processing

The system processes AI model responses through a sophisticated streaming pipeline that handles real-time content parsing, operation detection, and user interaction.

### Stream Processing Flow

**Main Streaming Loop**

```mermaid
graph TD
    doTellRequest["doTellRequest()"] --> CreateStream["CreateChatCompletionStream()"]
    CreateStream --> listenStream["listenStream()"]
    
    listenStream --> mainLoop["Main select loop"]
    mainLoop --> contextDone["<-active.Ctx.Done()"]
    mainLoop --> timerTimeout["<-timer.C (timeout)"]
    mainLoop --> streamError["<-streamErrCh"]
    mainLoop --> responseReceived["<-respCh"]
    
    contextDone --> execHookOnStop1["execHookOnStop(false)"]
    timerTimeout --> onError1["onError() - timeout"]
    streamError --> onError2["onError() - stream error"]
    responseReceived --> processChunk["processChunk()"]
    
    processChunk --> handleFinished["choice.FinishReason != ''"]
    handleFinished --> handleStreamFinished["handleStreamFinished()"]
    
    handleStreamFinished --> autoLoadContext["Check auto-load context"]
    handleStreamFinished --> checkSubtasks["Check new/removed subtasks"]
    handleStreamFinished --> willContinue["willContinuePlan()"]
    
    willContinue -->|true| autoContinue["Auto-continue: execTellPlan()"]
    willContinue -->|false| finishPlan["Finish plan execution"]
```

Sources: [tell_stream_main.go:20-284](), [tell_stream_finish.go:25-277]()

### Chunk Processing and Operation Detection

**processChunk Flow**

```mermaid
graph TD
    processChunk["processChunk()"] --> replyParser["replyParser.AddChunk()"]
    replyParser --> parserRead["replyParser.Read()"]
    parserRead --> checkOperations["Check for new operations"]
    
    checkOperations --> missingFileCheck{"File not in context?"}
    missingFileCheck -->|Yes| handleMissingFile["handleMissingFile()"]
    missingFileCheck -->|No| bufferOrStream["bufferOrStream()"]
    
    bufferOrStream --> shouldStream{"shouldStream?"}
    shouldStream -->|Yes| streamMessage["Stream to client"]
    shouldStream -->|No| bufferContent["Buffer content"]
    
    streamMessage --> handleNewOperations["handleNewOperations()"]
    bufferContent --> handleNewOperations
    
    handleMissingFile --> stopStream["Stop stream"]
    stopStream --> waitUserResponse["Wait for user choice"]
    waitUserResponse --> continueExecution["Continue execution"]
    
    handleNewOperations --> autoBuild{"BuildMode == Auto?"}
    autoBuild -->|Yes| queueBuilds["Queue builds"]
    autoBuild -->|No| operationsOnly["Store operations only"]
```

Sources: [tell_stream_processor.go:29-156](), [tell_stream_processor.go:522-593](), [tell_stream_processor.go:595-726]()

### Content Buffering and Stream Management

The system implements sophisticated buffering to handle XML-like tags and code blocks properly:

| Buffer State | Purpose | Trigger |
|--------------|---------|---------|
| `awaitingBlockOpeningTag` | Buffer until `<PlandexBlock>` complete | Partial opening tag detected |
| `awaitingBlockClosingTag` | Buffer until `</PlandexBlock>` complete | Partial closing tag detected |
| `awaitingOpClosingTag` | Buffer until `<EndPlandexFileOps/>` complete | Partial operation tag detected |
| `awaitingBackticks` | Buffer until code block backticks handled | Backticks in file content |

Sources: [tell_stream_processor.go:165-520]()

## Active Plan State Management

The runtime state during plan execution is managed through two key structures: `activeTellStreamState` for execution state and `ActivePlan` for coordination and streaming.

### activeTellStreamState Structure

**Core State Components**

```mermaid
graph TB
    subgraph "activeTellStreamState"
        activePlan["activePlan: *ActivePlan"]
        modelStreamId["modelStreamId: string"]
        clients["clients: map[string]ClientInfo"]
        
        subgraph "Request Context"
            req["req: *TellPlanRequest"]
            auth["auth: *ServerAuth"]
            iteration["iteration: int"]
            missingFileResponse["missingFileResponse"]
        end
        
        subgraph "Plan Data"
            plan["plan: *db.Plan"]
            branch["branch: string"]
            modelContext["modelContext: []*db.Context"]
            convo["convo: []*db.ConvoMessage"]
            subtasks["subtasks: []*db.Subtask"]
            currentSubtask["currentSubtask: *db.Subtask"]
        end
        
        subgraph "Model Interaction"
            messages["messages: []ExtendedChatMessage"]
            modelConfig["modelConfig: *ModelRoleConfig"]
            baseModelConfig["baseModelConfig: *BaseModelConfig"]
            replyParser["replyParser: *ReplyParser"]
        end
        
        subgraph "Processing State"
            chunkProcessor["chunkProcessor: *chunkProcessor"]
            currentStage["currentStage: CurrentStage"]
            replyId["replyId: string"]
        end
    end
    
    activePlan --> clients
    req --> iteration
    plan --> modelContext
    messages --> modelConfig
    chunkProcessor --> currentStage
```

Sources: [tell_state.go:14-69]()

### Chunk Processing State

**chunkProcessor Structure**

```mermaid
graph TB
    subgraph "chunkProcessor"
        replyOperations["replyOperations: []*Operation"]
        chunksReceived["chunksReceived: int"]
        
        subgraph "Content Buffering"
            contentBuffer["contentBuffer: string"]
            maybeRedundantOpeningTagContent["maybeRedundantOpeningTagContent"]
        end
        
        subgraph "State Flags"
            fileOpen["fileOpen: bool"]
            awaitingBlockOpeningTag["awaitingBlockOpeningTag: bool"]
            awaitingBlockClosingTag["awaitingBlockClosingTag: bool"]
            awaitingOpClosingTag["awaitingOpClosingTag: bool"]
            awaitingBackticks["awaitingBackticks: bool"]
        end
    end
    
    replyOperations --> chunksReceived
    contentBuffer --> fileOpen
    awaitingBlockOpeningTag --> awaitingBlockClosingTag
```

Sources: [tell_state.go:71-81]()

### State Management Functions

| Function | Purpose | Returns |
|----------|---------|---------|
| `loadTellPlan()` | Load plan data from database | `activeTellStreamState` populated |
| `setActivePlan()` | Link to `ActivePlan` instance | Error if plan not active |
| `resolveCurrentStage()` | Determine execution stage/phase | `activatePaths`, `activatePathsOrdered` |
| `dryRunCalculateTokensWithoutContext()` | Token calculation without context | Token count, success flag |

Sources: [tell_load.go:20-427](), [tell_load.go:429-442](), [tell_exec.go:584-684]()

### Plan Continuation Logic

**willContinuePlan Decision Flow**

```mermaid
graph TD
    willContinuePlan["willContinuePlan()"] --> checkIterations{"iteration > MaxAutoContinueIterations?"}
    checkIterations -->|Yes| stopExecution["Return false - prevent infinite loop"]
    checkIterations -->|No| checkConditions["Check continuation conditions"]
    
    checkConditions --> hasNewSubtasks{"hasNewSubtasks?"}
    checkConditions --> allSubtasksFinished{"allSubtasksFinished?"}
    checkConditions --> hasActivatePaths{"len(activatePaths) > 0?"}
    checkConditions --> removedSubtasks{"removedSubtasks?"}
    checkConditions --> hasExplicitPaths{"hasExplicitPaths?"}
    
    hasNewSubtasks -->|Yes| continueTrue["Return true"]
    allSubtasksFinished -->|No| continueTrue
    hasActivatePaths -->|Yes| continueTrue
    removedSubtasks -->|Yes| continueTrue
    hasExplicitPaths -->|Yes| continueTrue
    
    hasNewSubtasks -->|No| checkNext1["Check next condition"]
    allSubtasksFinished -->|Yes| checkNext2["Check next condition"]
    hasActivatePaths -->|No| checkNext3["Check next condition"]
    removedSubtasks -->|No| checkNext4["Check next condition"]
    hasExplicitPaths -->|No| continueFalse["Return false"]
    
    checkNext1 --> allSubtasksFinished
    checkNext2 --> hasActivatePaths
    checkNext3 --> removedSubtasks
    checkNext4 --> hasExplicitPaths
```

Sources: [tell_stream_finish.go:204-224](), [tell_stream_finish.go:18]()

## Conversation and Summary Management

Plan execution maintains conversation history and generates summaries when token limits are approached.

### Token Management Flow

```mermaid
graph TD
    ConvoStart["Add conversation messages"] --> TokenCalc["Calculate total tokens"]
    TokenCalc --> CheckLimit{"Exceeds GetPlannerEffectiveMaxTokens()?"}
    CheckLimit -->|No| AddMessages["Add all messages"]
    CheckLimit -->|Yes| FindSummary["Find suitable ConvoSummary"]
    
    FindSummary --> SummaryFound{"Summary reduces tokens enough?"}
    SummaryFound -->|Yes| UseSummary["Use summary + recent messages"]
    SummaryFound -->|No| CreateSummary["Generate new summary"]
    
    CreateSummary --> SummaryModel["ModelPack summarizer"]
    SummaryModel --> StoreSummary["db.StoreSummary()"]
    StoreSummary --> UseSummary
    
    AddMessages --> Continue["Continue execution"]
    UseSummary --> Continue
```

The system automatically summarizes conversation history when approaching token limits, using the configured summarizer model.

Sources: [tell_summary.go:22-231](), [tell_summary.go:246-432](), [summarize.go:31-98]()

---

# Page: AI Model Integration and Task Control

# AI Model Integration and Task Control

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/cli/lib/model_credentials.go](app/cli/lib/model_credentials.go)
- [app/server/model/client.go](app/server/model/client.go)
- [app/server/model/client_stream.go](app/server/model/client_stream.go)
- [app/server/model/model_error.go](app/server/model/model_error.go)
- [app/server/model/model_request.go](app/server/model/model_request.go)
- [app/server/model/name.go](app/server/model/name.go)
- [app/server/model/plan/build_exec.go](app/server/model/plan/build_exec.go)
- [app/server/model/plan/commit_msg.go](app/server/model/plan/commit_msg.go)
- [app/server/model/plan/exec_status.go](app/server/model/plan/exec_status.go)
- [app/server/model/plan/tell_stream_error.go](app/server/model/plan/tell_stream_error.go)
- [app/server/model/prompts/exec_status.go](app/server/model/prompts/exec_status.go)
- [app/server/model/summarize.go](app/server/model/summarize.go)
- [app/server/types/message.go](app/server/types/message.go)
- [app/shared/ai_models_available.go](app/shared/ai_models_available.go)
- [app/shared/ai_models_data_models.go](app/shared/ai_models_data_models.go)
- [app/shared/ai_models_errors.go](app/shared/ai_models_errors.go)
- [app/shared/ai_models_packs.go](app/shared/ai_models_packs.go)
- [app/shared/ai_models_providers.go](app/shared/ai_models_providers.go)
- [test/smoke_test.sh](test/smoke_test.sh)
- [test/test_utils.sh](test/test_utils.sh)

</details>



This document covers how Plandex integrates with multiple AI model providers and controls task execution flow. It explains the model configuration system, authentication mechanisms, streaming request handling, and the logic for determining when AI-generated tasks are complete.

For information about model configuration commands and user interfaces, see [Model Configuration Commands](#2.4). For details about the plan execution lifecycle, see [Plan Lifecycle and States](#3.1). For file modification processing, see [File Modification Pipeline](#3.3).

## Model Provider Architecture

Plandex supports multiple AI model providers through a unified configuration system that handles authentication, fallback logic, and provider-specific adaptations.

### Supported Providers

```mermaid
graph TB
    subgraph "Cloud Providers"
        OpenAI["ModelProviderOpenAI<br/>api.openai.com"]
        Anthropic["ModelProviderAnthropic<br/>via LiteLLM"]
        Google["ModelProviderGoogleAIStudio<br/>via LiteLLM"]
        Azure["ModelProviderAzureOpenAI<br/>via LiteLLM"]
        OpenRouter["ModelProviderOpenRouter<br/>openrouter.ai"]
        ClaudeMax["ModelProviderAnthropicClaudeMax<br/>Claude Subscription"]
    end
    
    subgraph "Local Providers"
        Ollama["ModelProviderOllama<br/>via LiteLLM"]
        Custom["ModelProviderCustom<br/>User-defined"]
    end
    
    subgraph "Enterprise Providers"
        Bedrock["ModelProviderAmazonBedrock<br/>via LiteLLM"]
        Vertex["ModelProviderGoogleVertex<br/>via LiteLLM"]
    end
    
    subgraph "Authentication Methods"
        APIKey["API Key<br/>Environment Variables"]
        AWS["AWS Credentials<br/>Profile/IAM"]
        OAuth["OAuth Token<br/>Claude Max"]
        ServiceAccount["Service Account<br/>Google Cloud"]
    end
    
    OpenAI --> APIKey
    Anthropic --> APIKey
    OpenRouter --> APIKey
    ClaudeMax --> OAuth
    Bedrock --> AWS
    Vertex --> ServiceAccount
    Ollama --> Local["No Authentication"]
```

**Sources:** [app/shared/ai_models_providers.go:36-77](), [app/shared/ai_models_providers.go:116-219]()

### Provider Configuration Schema

The `ModelProviderConfigSchema` defines how each provider is configured:

| Field | Purpose | Example |
|-------|---------|---------|
| `Provider` | Provider identifier | `ModelProviderOpenAI` |
| `BaseUrl` | API endpoint | `https://api.openai.com/v1` |
| `ApiKeyEnvVar` | Environment variable for API key | `OPENAI_API_KEY` |
| `ExtraAuthVars` | Additional authentication variables | AWS credentials, project IDs |
| `HasAWSAuth` | Uses AWS credential chain | Bedrock models |
| `HasClaudeMaxAuth` | Uses Claude subscription OAuth | Claude Max integration |
| `SkipAuth` | No authentication required | Local Ollama |

**Sources:** [app/shared/ai_models_providers.go:86-103](), [app/cli/lib/model_credentials.go:124-169]()

## Model Configuration and Roles

Plandex assigns specialized roles to different models within a model pack, allowing optimal model selection for specific tasks.

### Model Role Specialization

```mermaid
graph TB
    subgraph "Planning Phase"
        UserInput["User Request"]
        Planner["ModelRolePlanner<br/>High-reasoning models<br/>o3, Claude Sonnet-4"]
        Architect["ModelRoleArchitect<br/>Context analysis<br/>Large context models"]
    end
    
    subgraph "Implementation Phase"  
        Coder["ModelRoleCoder<br/>Code generation<br/>Claude Sonnet-4, GPT-4"]
        Builder["ModelRoleBuilder<br/>File operations<br/>o4-mini variants"]
        WholeFileBuilder["ModelRoleWholeFileBuilder<br/>Complete file rewrites"]
    end
    
    subgraph "Support Tasks"
        Namer["ModelRoleName<br/>Generate names<br/>GPT-4 Mini"]
        CommitMsg["ModelRoleCommitMsg<br/>Commit messages<br/>GPT-4 Mini"] 
        ExecStatus["ModelRoleExecStatus<br/>Task completion<br/>o4-mini-low"]
        Summary["ModelRolePlanSummary<br/>Conversation summary<br/>Fast models"]
    end
    
    UserInput --> Planner
    Planner --> Architect
    Architect --> Coder
    Coder --> Builder
    Builder --> WholeFileBuilder
    
    Planner --> ExecStatus
    Coder --> ExecStatus
    Builder --> Namer
    Builder --> CommitMsg
    Planner --> Summary
```

**Sources:** [app/shared/ai_models_packs.go:124-451](), [app/shared/ai_models_data_models.go:274-303]()

### Model Pack Configuration

Model packs define which models to use for each role. The `DailyDriverModelPack` demonstrates the configuration:

```mermaid
graph LR
    subgraph "DailyDriverSchema"
        PlannerModel["Planner: claude-sonnet-4<br/>Fallback: gemini-2.5-pro"]
        CoderModel["Coder: claude-sonnet-4<br/>Fallback: gpt-4.1"]
        BuilderModel["Builder: o4-mini-medium<br/>StrongModel: o4-mini-high"]
    end
    
    subgraph "Model Resolution"
        GetBaseModelConfig["GetBaseModelConfig()"]
        GetProviderComposite["GetProviderComposite()"] 
        GetFallbackForModelError["GetFallbackForModelError()"]
    end
    
    PlannerModel --> GetBaseModelConfig
    CoderModel --> GetProviderComposite
    BuilderModel --> GetFallbackForModelError
```

**Sources:** [app/shared/ai_models_packs.go:129-153](), [app/shared/ai_models_data_models.go:586-616]()

## AI Client Management

The client management system handles authentication, request routing, and provider-specific adaptations.

### Client Initialization Flow

```mermaid
sequenceDiagram
    participant Auth as "MustVerifyAuthVars()"
    participant Init as "InitClients()"
    participant Provider as "newClient()"
    participant Config as "openai.DefaultConfig()"
    
    Auth->>Auth: CheckCredentialStatus()
    Auth->>Auth: ResolveProviderAuthVars()
    Auth->>Init: authVars, settings, orgUserConfig
    
    loop For each provider
        Init->>Provider: providerConfig, authVars
        Provider->>Config: apiKey
        Provider->>Provider: Configure BaseURL, OrgID
        Provider-->>Init: ClientInfo
    end
    
    Init-->>Auth: map[string]ClientInfo
```

**Sources:** [app/server/model/client.go:46-80](), [app/cli/lib/model_credentials.go:49-106]()

### Request Creation and Streaming

The `CreateChatCompletionStream` function handles model requests with fallback logic:

```mermaid
graph TB
    Request["CreateChatCompletionStream()"]
    Resolve["resolveReq()<br/>Handle system prompts<br/>Role parameters"]
    
    subgraph "Provider Adaptation"
        OpenAI["Direct OpenAI API"]
        LiteLLM["LiteLLM Proxy<br/>Anthropic, Google, etc."]
        Extensions["Provider Extensions<br/>Azure, Vertex, Bedrock"]
    end
    
    subgraph "Stream Processing"
        ExtendedStream["ExtendedChatCompletionStream"]
        StreamReader["StreamReader[T]"]
        ErrorAccumulator["ErrorAccumulator"]
    end
    
    Request --> Resolve
    Resolve --> OpenAI
    Resolve --> LiteLLM
    Resolve --> Extensions
    
    OpenAI --> ExtendedStream
    LiteLLM --> ExtendedStream
    Extensions --> ExtendedStream
    
    ExtendedStream --> StreamReader
    StreamReader --> ErrorAccumulator
```

**Sources:** [app/server/model/client.go:107-214](), [app/server/model/client.go:216-397]()

## Task Execution Control

Plandex uses an AI-powered system to determine when coding tasks are complete, preventing infinite loops and ensuring progress.

### Task Completion Assessment

The `execStatusShouldContinue` function evaluates whether a subtask is finished:

```mermaid
graph TB
    Start["execStatusShouldContinue()"]
    CheckMarker{"Completion marker<br/>found in message?"}
    CheckTries{"Previous attempts<br/> >= MaxPreviousMessages?"}
    LLMCall["AI Model Call<br/>ExecStatus role"]
    
    subgraph "Completion Detection"
        Marker["**{subtask.Title} has been completed**"]
        MaxRetries["MaxPreviousMessages = 4"]
        AIDecision["AI evaluates completion<br/>reasoning + boolean"]
    end
    
    Start --> CheckMarker
    CheckMarker -->|Yes| Finished["subtaskFinished: true"]
    CheckMarker -->|No| CheckTries
    CheckTries -->|Yes| Finished
    CheckTries -->|No| LLMCall
    
    LLMCall --> AIDecision
    AIDecision --> Decision["subtaskFinished: true/false"]
    
    Marker -.-> CheckMarker
    MaxRetries -.-> CheckTries
```

**Sources:** [app/server/model/plan/exec_status.go:30-210](), [app/server/model/plan/exec_status.go:21-24]()

### AI Model Evaluation Logic

The system uses specialized prompts to evaluate task completion:

```mermaid
graph LR
    subgraph "Input Context"
        UserPrompt["Original user request"]
        CurrentSubtask["Current subtask description"] 
        CurrentMessage["Latest AI response"]
        PreviousMessages["Previous attempt messages"]
    end
    
    subgraph "Evaluation Process"
        Prompt["GetExecStatusFinishedSubtask()"]
        ModelCall["ModelRequest()<br/>ExecStatus role"]
        Parse["Parse XML/JSON response"]
    end
    
    subgraph "Output Decision"
        Reasoning["Explanation of decision"]
        Finished["Boolean: task complete?"]
    end
    
    UserPrompt --> Prompt
    CurrentSubtask --> Prompt  
    CurrentMessage --> Prompt
    PreviousMessages --> Prompt
    
    Prompt --> ModelCall
    ModelCall --> Parse
    Parse --> Reasoning
    Parse --> Finished
```

**Sources:** [app/server/model/plan/exec_status.go:128-161](), [app/server/model/prompts/exec_status.go:10-82]()

## Error Handling and Fallback

The system implements sophisticated error classification and fallback mechanisms to handle model failures gracefully.

### Error Classification System

```mermaid
graph TB
    Error["HTTP/Stream Error"]
    Classify["classifyBasicError()"]
    
    subgraph "Error Types"
        Context["ErrContextTooLong<br/>Input too large"]
        RateLimit["ErrRateLimited<br/>429, 529 status"]
        Overloaded["ErrOverloaded<br/>Model capacity"]
        Cache["ErrCacheSupport<br/>Cache control unsupported"]
        Other["ErrOther<br/>General errors"]
    end
    
    subgraph "Error Properties" 
        Retriable["Retriable: bool"]
        RetryAfter["RetryAfterSeconds: int"]
        ShouldIncrement["ShouldIncrementRetry()"]
    end
    
    Error --> Classify
    Classify --> Context
    Classify --> RateLimit  
    Classify --> Overloaded
    Classify --> Cache
    Classify --> Other
    
    Context --> Retriable
    RateLimit --> RetryAfter
    Overloaded --> ShouldIncrement
```

**Sources:** [app/server/model/model_error.go:38-88](), [app/shared/ai_models_errors.go:10-29]()

### Fallback Resolution Logic

The `GetFallbackForModelError` method implements a sophisticated fallback strategy:

```mermaid
graph TB
    Start["GetFallbackForModelError()"]
    ContextError{"ErrContextTooLong?"}
    HasLargeContext{"LargeContextFallback<br/>defined?"}
    
    NonRetriable{"Non-retriable or<br/>max retries reached?"}
    HasErrorFallback{"ErrorFallback<br/>defined?"}
    HasProviderFallback{"Provider fallback<br/>available?"}
    
    subgraph "Fallback Types"
        LargeContextFB["LargeContextFallback<br/>Higher context limit model"]
        ErrorFB["ErrorFallback<br/>Alternative model"]
        ProviderFB["Provider Fallback<br/>OpenRouter or next provider"]
    end
    
    Start --> ContextError
    ContextError -->|Yes| HasLargeContext
    ContextError -->|No| NonRetriable
    
    HasLargeContext -->|Yes| LargeContextFB
    HasLargeContext -->|No| NonRetriable
    
    NonRetriable -->|Yes| HasErrorFallback
    HasErrorFallback -->|Yes| ErrorFB
    HasErrorFallback -->|No| HasProviderFallback
    HasProviderFallback -->|Yes| ProviderFB
    HasProviderFallback -->|No| NoFallback["Use original model"]
```

**Sources:** [app/shared/ai_models_errors.go:49-105](), [app/shared/ai_models_errors.go:111-149]()

## Streaming and Response Processing

Plandex processes AI responses through a streaming architecture that handles real-time updates and partial results.

### Stream Processing Architecture

```mermaid
graph TB
    subgraph "Stream Creation"
        CreateStream["CreateChatCompletionStream()"]
        WithRetries["withStreamingRetries()"]
        ProcessStream["processChatCompletionStream()"]
    end
    
    subgraph "Response Processing"
        Accumulator["StreamCompletionAccumulator"]
        ChunkProcessor["Process chunks"]
        OnStream["OnStreamFn callback"]
    end
    
    subgraph "Timeout Management"
        ActiveTimeout["ACTIVE_STREAM_CHUNK_TIMEOUT<br/>60 seconds"]
        UsageTimeout["USAGE_CHUNK_TIMEOUT<br/>10 seconds"]
        Timer["time.NewTimer()"]
    end
    
    subgraph "Completion Detection"
        EOF["io.EOF"]
        Usage["Usage chunk received"]
        FinishReason["FinishReason != ''"]
    end
    
    CreateStream --> WithRetries
    WithRetries --> ProcessStream
    ProcessStream --> Accumulator
    
    Accumulator --> ChunkProcessor
    ChunkProcessor --> OnStream
    ChunkProcessor --> Timer
    
    Timer --> ActiveTimeout
    Timer --> UsageTimeout
    
    ChunkProcessor --> EOF
    ChunkProcessor --> Usage
    ChunkProcessor --> FinishReason
```

**Sources:** [app/server/model/client_stream.go:19-84](), [app/server/model/client_stream.go:86-228]()

### Model Response Types

The system handles different response formats based on model capabilities:

| Output Format | Models | Processing |
|---------------|--------|------------|
| `ModelOutputFormatToolCallJson` | OpenAI models | JSON schema validation, function calls |
| `ModelOutputFormatXml` | Anthropic, Google | XML tag extraction |

**Sources:** [app/shared/ai_models_data_models.go:18-23](), [app/server/model/name.go:36-53]()

---

# Page: File Modification Pipeline

# File Modification Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/server/model/plan/build_finish.go](app/server/model/plan/build_finish.go)
- [app/server/model/plan/build_load.go](app/server/model/plan/build_load.go)
- [app/server/model/plan/build_state.go](app/server/model/plan/build_state.go)
- [app/server/model/plan/build_structured_edits.go](app/server/model/plan/build_structured_edits.go)
- [app/server/model/plan/build_validate_and_fix.go](app/server/model/plan/build_validate_and_fix.go)
- [app/server/model/plan/build_whole_file.go](app/server/model/plan/build_whole_file.go)
- [app/server/model/plan/tell_stream_usage.go](app/server/model/plan/tell_stream_usage.go)
- [app/server/types/model.go](app/server/types/model.go)
- [app/shared/plan_result_replacements.go](app/shared/plan_result_replacements.go)
- [app/shared/streamed_change.go](app/shared/streamed_change.go)

</details>



## Purpose and Scope

The File Modification Pipeline is the core system responsible for transforming AI model outputs into actual file changes in Plandex. This system takes proposed content from AI models, processes it through structured edits, validates syntax, applies replacements, and commits the final results to Git repositories. The pipeline handles error recovery, syntax validation, and multiple processing strategies to ensure reliable file modifications.

For information about plan execution and AI model integration, see [Plan Execution System](#3) and [AI Model Integration](#5). For details about Git repository management, see [Repository Locking and Git Integration](#6.2).

## Pipeline Overview

The File Modification Pipeline operates as a multi-stage processing system that transforms AI-generated content into validated file changes:

```mermaid
graph TD
    subgraph "Input Stage"
        AIOutput["AI Model Output"]
        PendingBuilds["Pending Builds Queue"]
        FileContext["File Context & State"]
    end
    
    subgraph "Processing Stage"
        LoadBuild["loadBuildFile()"]
        StructuredEdits["buildStructuredEdits()"]
        WholeFileFallback["buildWholeFileFallback()"]
        ValidationLoop["buildValidateLoop()"]
    end
    
    subgraph "Application Stage"
        ApplyReplacements["ApplyReplacements()"]
        SyntaxValidation["validateSyntax()"]
        GitCommit["GitAddAndCommit()"]
    end
    
    subgraph "State Management"
        ActiveBuild["ActiveBuild"]
        BuildState["activeBuildStreamFileState"]
        PlanResult["PlanFileResult"]
    end
    
    AIOutput --> LoadBuild
    PendingBuilds --> LoadBuild
    FileContext --> LoadBuild
    
    LoadBuild --> StructuredEdits
    StructuredEdits --> ValidationLoop
    StructuredEdits --> WholeFileFallback
    WholeFileFallback --> ValidationLoop
    
    ValidationLoop --> ApplyReplacements
    ApplyReplacements --> SyntaxValidation
    SyntaxValidation --> GitCommit
    
    BuildState --> StructuredEdits
    BuildState --> WholeFileFallback
    BuildState --> ValidationLoop
    
    ActiveBuild --> BuildState
    GitCommit --> PlanResult
    
    style StructuredEdits fill:#f9f9f9
    style ValidationLoop fill:#f9f9f9
    style ApplyReplacements fill:#f9f9f9
```

**Sources:** [app/server/model/plan/build_load.go:17-157](), [app/server/model/plan/build_structured_edits.go:20-221](), [app/server/model/plan/build_finish.go:18-163]()

## Build State Management

The pipeline uses several key state structures to track build progress and manage file processing:

| State Structure | Purpose | Key Fields |
|----------------|---------|------------|
| `activeBuildStreamState` | Global build coordination | `modelStreamId`, `clients`, `plan`, `branch` |
| `activeBuildStreamFileState` | Per-file build tracking | `filePath`, `activeBuild`, `preBuildState`, `parser` |
| `ActiveBuild` | Individual build execution | `FileContent`, `FileDescription`, `Success`, `Error` |
| `PlanFileResult` | Final build output | `Path`, `Replacements`, `Content` |

```mermaid
stateDiagram-v2
    [*] --> LoadPending
    LoadPending --> LoadBuildFile
    LoadBuildFile --> ProcessStructuredEdits
    ProcessStructuredEdits --> ValidateAndFix
    ProcessStructuredEdits --> WholeFileFallback
    WholeFileFallback --> ValidateAndFix
    ValidateAndFix --> ApplyReplacements
    ApplyReplacements --> FinishBuild
    ValidateAndFix --> ProcessStructuredEdits : Retry
    FinishBuild --> [*]
    
    ProcessStructuredEdits --> BuildError : Syntax Errors
    WholeFileFallback --> BuildError : Model Errors
    ValidateAndFix --> BuildError : Max Retries
    BuildError --> [*]
```

**Sources:** [app/server/model/plan/build_state.go:16-49](), [app/server/types/model.go:7-13]()

## Structured Edits Processing

The primary file modification strategy uses structured edits with syntax validation and smart fallback mechanisms:

### Main Processing Flow

The `buildStructuredEdits()` function implements the core processing logic:

```mermaid
graph TD
    subgraph "Input Analysis"
        CheckType["Check Edit Type"]
        ReplaceOrRemove["Replace/Remove?"]
        CallFastApply1["Call Fast Apply Hook"]
    end
    
    subgraph "Primary Processing"
        ApplyChanges["syntax.ApplyChanges()"]
        ValidateSyntax1["validateSyntax()"]
        CheckValidity["Check Validity"]
    end
    
    subgraph "Fallback Processing"
        CallFastApply2["Call Fast Apply Hook"]
        BuildRace["buildRace()"]
        FastApplyResult["Fast Apply Result"]
    end
    
    subgraph "Output Generation"
        StripBlankLines["utils.StripAddedBlankLines()"]
        GetDiffReplacements["diff_pkg.GetDiffReplacements()"]
        CreatePlanResult["Create PlanFileResult"]
    end
    
    CheckType --> ReplaceOrRemove
    ReplaceOrRemove --> CallFastApply1
    CallFastApply1 --> ApplyChanges
    ReplaceOrRemove --> ApplyChanges
    
    ApplyChanges --> ValidateSyntax1
    ValidateSyntax1 --> CheckValidity
    
    CheckValidity --> StripBlankLines : Valid
    CheckValidity --> CallFastApply2 : Invalid
    CallFastApply2 --> BuildRace
    BuildRace --> FastApplyResult
    FastApplyResult --> StripBlankLines
    
    StripBlankLines --> GetDiffReplacements
    GetDiffReplacements --> CreatePlanResult
    
    style ApplyChanges fill:#f9f9f9
    style BuildRace fill:#f9f9f9
```

**Sources:** [app/server/model/plan/build_structured_edits.go:20-221](), [app/server/syntax/apply_changes.go]()

### Syntax Validation and Error Handling

The pipeline includes comprehensive syntax validation using tree-sitter parsers:

```mermaid
graph LR
    subgraph "Validation Process"
        ParseFile["Parse with tree-sitter"]
        CheckErrors["Check Syntax Errors"]
        TimeoutCheck["Check Timeout"]
        ValidationResult["Validation Result"]
    end
    
    subgraph "Error Categories"
        SyntaxErrors["Syntax Errors"]
        NeedsVerifyReasons["Needs Verify Reasons"]
        ParserTimeout["Parser Timeout"]
    end
    
    ParseFile --> CheckErrors
    CheckErrors --> TimeoutCheck
    TimeoutCheck --> ValidationResult
    
    ValidationResult --> SyntaxErrors
    ValidationResult --> NeedsVerifyReasons
    ValidationResult --> ParserTimeout
    
    style ValidationResult fill:#f9f9f9
```

**Sources:** [app/server/model/plan/build_structured_edits.go:223-238](), [app/server/syntax/validate.go]()

## Validation and Fix Loop

When structured edits produce invalid results, the pipeline enters a validation and fix loop with AI model assistance:

### Validation Loop Architecture

```mermaid
graph TD
    subgraph "Loop Control"
        StartLoop["Start Validation Loop"]
        AttemptCounter["Attempt Counter"]
        MaxAttempts["Max Attempts Check"]
    end
    
    subgraph "Model Interaction"
        BuildPrompt["Build Validation Prompt"]
        ModelRequest["model.ModelRequest()"]
        ParseResponse["handleXMLResponse()"]
    end
    
    subgraph "Response Processing"
        CheckCorrect["Check <PlandexCorrect/>"]
        ExtractReplacements["Extract Replacements"]
        ApplyXMLReplacements["Apply XML Replacements"]
        ValidateResult["Validate Result"]
    end
    
    StartLoop --> AttemptCounter
    AttemptCounter --> MaxAttempts
    MaxAttempts --> BuildPrompt : Continue
    MaxAttempts --> ReturnFailed : Max Reached
    
    BuildPrompt --> ModelRequest
    ModelRequest --> ParseResponse
    
    ParseResponse --> CheckCorrect
    CheckCorrect --> ReturnSuccess : Correct
    CheckCorrect --> ExtractReplacements : Needs Fix
    ExtractReplacements --> ApplyXMLReplacements
    ApplyXMLReplacements --> ValidateResult
    ValidateResult --> AttemptCounter : Invalid
    ValidateResult --> ReturnSuccess : Valid
    
    style ModelRequest fill:#f9f9f9
    style ApplyXMLReplacements fill:#f9f9f9
```

**Sources:** [app/server/model/plan/build_validate_and_fix.go:44-159](), [app/server/model/plan/build_validate_and_fix.go:182-325]()

### XML Response Processing

The validation system processes structured XML responses from AI models:

| XML Tag | Purpose | Processing |
|---------|---------|------------|
| `<PlandexCorrect/>` | Indicates changes are valid | Return success immediately |
| `<PlandexReplacements>` | Contains fix instructions | Extract and apply replacements |
| `<Replacement>` | Individual fix operation | Parse old/new content with line numbers |
| `<Old>` | Content to replace | Extract with line number prefixes |
| `<New>` | Replacement content | Apply to target location |

**Sources:** [app/server/model/plan/build_validate_and_fix.go:327-453]()

## Replacement Application System

The final stage applies validated changes through a sophisticated replacement system:

### Replacement Processing

```mermaid
graph TD
    subgraph "Replacement Input"
        PlanResult["PlanFileResult"]
        ReplacementList["Replacements Array"]
        OriginalContent["Original File Content"]
    end
    
    subgraph "Application Logic"
        IterateReplacements["Iterate Replacements"]
        FindOldContent["Find Old Content"]
        CheckEntireFile["Check EntireFile Flag"]
        StringReplace["strings.Replace()"]
        UpdateIndices["Update lastInsertedIdx"]
    end
    
    subgraph "Error Handling"
        IndexNotFound["Index Not Found"]
        SetFailed["Set replacement.Failed"]
        ReturnPartial["Return Partial Result"]
    end
    
    PlanResult --> ReplacementList
    ReplacementList --> IterateReplacements
    OriginalContent --> IterateReplacements
    
    IterateReplacements --> FindOldContent
    FindOldContent --> CheckEntireFile
    CheckEntireFile --> StringReplace : Found
    FindOldContent --> IndexNotFound : Not Found
    
    StringReplace --> UpdateIndices
    UpdateIndices --> IterateReplacements : Next
    
    IndexNotFound --> SetFailed
    SetFailed --> ReturnPartial
    
    style StringReplace fill:#f9f9f9
    style UpdateIndices fill:#f9f9f9
```

**Sources:** [app/shared/plan_result_replacements.go:20-137]()

### Git Integration and Commit Process

Successfully processed files are committed to Git through the repository management system:

```mermaid
graph LR
    subgraph "Build Completion"
        FinishBuild["onFinishBuild()"]
        CheckStreaming["Check Still Streaming"]
        WaitForReply["Wait for Reply Done"]
    end
    
    subgraph "Git Operations"
        ExecRepoOperation["db.ExecRepoOperation()"]
        GetPlanState["GetCurrentPlanState()"]
        UpdateDescriptions["Update Build Descriptions"]
        GitAddAndCommit["repo.GitAddAndCommit()"]
    end
    
    subgraph "Finalization"
        CommitMessage["PendingChangesSummaryForBuild()"]
        UpdateActivePlan["Update Active Plan State"]
        NotifyCompletion["Notify Completion"]
    end
    
    FinishBuild --> CheckStreaming
    CheckStreaming --> WaitForReply
    WaitForReply --> ExecRepoOperation
    
    ExecRepoOperation --> GetPlanState
    GetPlanState --> UpdateDescriptions
    UpdateDescriptions --> GitAddAndCommit
    
    GitAddAndCommit --> CommitMessage
    CommitMessage --> UpdateActivePlan
    UpdateActivePlan --> NotifyCompletion
    
    style GitAddAndCommit fill:#f9f9f9
    style ExecRepoOperation fill:#f9f9f9
```

**Sources:** [app/server/model/plan/build_finish.go:18-163](), [app/server/db/git.go]()

## Error Handling and Retry Logic

The pipeline implements comprehensive error handling with exponential backoff and multiple retry strategies:

### Retry Mechanisms

| Component | Max Retries | Backoff Strategy | Error Types |
|-----------|-------------|------------------|-------------|
| Validation Loop | `MaxValidationFixAttempts` (3) | Linear with model switching | Syntax errors, AI failures |
| Whole File Fallback | `MaxBuildErrorRetries` (3) | Exponential with jitter | Model request failures |
| General Build Operations | `MaxBuildErrorRetries` (3) | Exponential with jitter | Network, parsing errors |

```mermaid
graph TD
    subgraph "Error Detection"
        SyntaxError["Syntax Error"]
        ModelError["Model Request Error"]
        ValidationError["Validation Error"]
        GitError["Git Operation Error"]
    end
    
    subgraph "Retry Logic"
        CheckRetryCount["Check Retry Count"]
        ExponentialBackoff["Exponential Backoff"]
        SwitchModel["Switch to Strong Model"]
        RetryOperation["Retry Operation"]
    end
    
    subgraph "Failure Handling"
        MaxRetriesReached["Max Retries Reached"]
        SetBuildError["Set Build Error"]
        NotifyError["Notify Error"]
        StreamError["Stream Error to Client"]
    end
    
    SyntaxError --> CheckRetryCount
    ModelError --> CheckRetryCount
    ValidationError --> CheckRetryCount
    GitError --> CheckRetryCount
    
    CheckRetryCount --> ExponentialBackoff : Retry Available
    CheckRetryCount --> MaxRetriesReached : No Retries Left
    
    ExponentialBackoff --> SwitchModel
    SwitchModel --> RetryOperation
    RetryOperation --> CheckRetryCount : Still Failing
    
    MaxRetriesReached --> SetBuildError
    SetBuildError --> NotifyError
    NotifyError --> StreamError
    
    style RetryOperation fill:#f9f9f9
    style SetBuildError fill:#f9f9f9
```

**Sources:** [app/server/model/plan/build_validate_and_fix.go:455-486](), [app/server/model/plan/build_whole_file.go:143-171](), [app/server/model/plan/build_finish.go:276-313]()

## Performance Optimizations

The pipeline includes several performance optimizations:

- **Parallel Processing**: Multiple files can be processed concurrently through build queues
- **Syntax Caching**: Tree-sitter parsers are cached and reused across builds
- **Fast Apply Hooks**: External tools can provide optimized merge strategies
- **Token Caching**: OpenAI prompt caching reduces API costs for repeated patterns
- **Incremental Updates**: Only changed portions of files are processed when possible

**Sources:** [app/server/model/plan/build_structured_edits.go:54-98](), [app/server/model/plan/build_load.go:17-157]()

---

# Page: Server Architecture

# Server Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/cli/api/clients.go](app/cli/api/clients.go)
- [app/server/db/user_helpers.go](app/server/db/user_helpers.go)
- [app/server/handlers/sessions.go](app/server/handlers/sessions.go)
- [app/server/main.go](app/server/main.go)
- [app/server/routes/routes.go](app/server/routes/routes.go)
- [app/server/setup/setup.go](app/server/setup/setup.go)

</details>



This document covers the server-side components of Plandex, including the HTTP API server, request handlers, middleware, routing, and core server infrastructure. For information about plan execution logic and AI model integration, see [Plan Execution Engine](#4.3). For database schema and data models, see [Data Models and Shared Types](#4.2).

## Overview

The Plandex server is a Go-based HTTP API server that provides REST endpoints for plan management, context operations, and real-time plan execution. The server follows a layered architecture with clear separation between HTTP handling, business logic, and data persistence.

```mermaid
graph TD
    subgraph "Server Initialization"
        MainFunc["main()"] --> RegisterRoutes["routes.RegisterHandlePlandex()"]
        RegisterRoutes --> LiteLLM["model.EnsureLiteLLM(2)"]
        LiteLLM --> RouterSetup["mux.NewRouter()"]
        RouterSetup --> LoadIP["setup.MustLoadIp()"]
        LoadIP --> InitDB["setup.MustInitDb()"]
        InitDB --> StartServer["setup.StartServer()"]
    end
    
    subgraph "Route Categories"
        HealthRoutes["routes.AddHealthRoutes()<br/>/health, /version"]
        ApiRoutes["routes.AddApiRoutes()<br/>Standard operations"]
        ProxyRoutes["routes.AddProxyableApiRoutes()<br/>Real-time operations"]
    end
    
    subgraph "Middleware Stack"
        LogMiddleware["loggingMiddleware()<br/>Request/response logging"]
        MaxBytes["maxBytesMiddleware()<br/>1GB request limit"]
        Auth["Authenticate()<br/>Per-handler JWT validation"]
    end
    
    subgraph "Handler Types"
        SessionHandlers["handlers/sessions.go<br/>CreateEmailVerificationHandler<br/>SignInHandler<br/>SignOutHandler"]
        UserHandlers["db/user_helpers.go<br/>GetUser<br/>GetUserByEmail<br/>CreateUser"]
        PlanHandlers["Plan execution handlers<br/>TellPlanHandler<br/>BuildPlanHandler"]
    end
    
    subgraph "External Dependencies"
        PostgreSQL[("PostgreSQL Database<br/>User data & plans")]
        LiteLLMProxy["LiteLLM Proxy Server<br/>AI model abstraction"]
        GitRepositories[("Git Repositories<br/>Plan file storage")]
    end
    
    StartServer --> HealthRoutes
    StartServer --> ApiRoutes
    StartServer --> ProxyRoutes
    
    RouterSetup --> LogMiddleware
    LogMiddleware --> MaxBytes
    MaxBytes --> Auth
    
    Auth --> SessionHandlers
    Auth --> UserHandlers  
    Auth --> PlanHandlers
    
    InitDB --> PostgreSQL
    LiteLLM --> LiteLLMProxy
    PlanHandlers --> GitRepositories
```

**Sources:** [app/server/main.go:14-38](), [app/server/setup/setup.go:66-185](), [app/server/routes/routes.go:20-203]()
</thinking>

## HTTP Server Configuration

The server configuration in `setup.go` implements comprehensive middleware, graceful shutdown, and database initialization. The `StartServer` function orchestrates the complete HTTP server lifecycle:

```mermaid
graph LR
    subgraph "Server Configuration"
        StartServer["StartServer()"] --> EnvCheck["GOENV development check"]
        EnvCheck --> ShutdownCtx["shutdown.ShutdownCtx setup"]
        ShutdownCtx --> PortConfig["PORT env var<br/>default: 8099"]
        PortConfig --> MiddlewareStack["Middleware application"]
    end
    
    subgraph "Middleware Pipeline"
        LoggingMW["loggingMiddleware()<br/>Skip /health, /version"] --> MaxBytesMW["maxBytesMiddleware()<br/>1GB limit, 1MB headers"]
        MaxBytesMW --> ConfigureFn["configureFn()<br/>Optional configuration"]
    end
    
    subgraph "HTTP Server Specs"
        ServerConfig["http.Server<br/>Addr: :PORT<br/>MaxHeaderBytes: 1MB<br/>ReadHeaderTimeout: 5s"] --> ListenServe["ListenAndServe()<br/>Goroutine"]
    end
    
    subgraph "Shutdown Handling"
        SignalCapture["signal.Notify()<br/>SIGTERM, SIGINT"] --> WaitActivePlans["waitForActivePlans()<br/>1s ticker polling<br/>plan.NumActivePlans()"]
        WaitActivePlans --> CleanupLocks["db.CleanupActiveLocks()"] 
        CleanupLocks --> HTTPShutdown["server.Shutdown()<br/>30s timeout"]
        HTTPShutdown --> ShutdownHooks["Execute shutdown hooks<br/>model.ShutdownLiteLLMServer()"]
    end
    
    MiddlewareStack --> ServerConfig
    ListenServe --> SignalCapture
```

The middleware stack includes several critical components:
- `loggingMiddleware`: Logs request method, path, and duration while excluding monitoring endpoints
- `maxBytesMiddleware`: Uses `http.MaxBytesReader` to enforce the 1GB request body limit
- Database connection cleanup with deferred `db.Conn.Close()`
- Graceful shutdown with 60-second active plan timeout followed by 30-second HTTP shutdown timeout

**Sources:** [app/server/setup/setup.go:66-185](), [app/server/setup/setup.go:50-64](), [app/server/setup/setup.go:187-214]()

## Route Organization

Routes are organized using the `mux.Router` from Gorilla Mux with a configurable handler registration system. The `routes.go` file defines three distinct route categories:

| Route Function | Purpose | Handler Registration |
|---|---|---|
| `AddHealthRoutes` | System monitoring | `/health`, `/version` endpoints |
| `AddApiRoutes` | Standard CRUD operations | Plan, context, user management |
| `AddProxyableApiRoutes` | Real-time operations | Active plan streaming, status |

```mermaid
graph TD
    subgraph "Route Registration Pattern"
        RegisterFn["routes.RegisterHandlePlandex()"] --> HandlePlandexFn["HandlePlandexFn variable<br/>Function pointer"]
        HandlePlandexFn --> RouteDefinition["router.HandleFunc(path, handler)"]
    end
    
    subgraph "Health Routes"
        HealthCheck["/health --> hooks.ExecHook(hooks.HealthCheck)"]
        VersionCheck["/version --> Read version.txt<br/>Handle IS_CLOUD env"]
    end
    
    subgraph "Standard API Routes (89 total)"
        AccountRoutes["/accounts/email_verifications<br/>/accounts/sign_in<br/>/accounts/sign_out"]
        OrgRoutes["/orgs<br/>/orgs/session<br/>/users"]
        PlanRoutes["/plans<br/>/plans/{planId}<br/>/plans/{planId}/{branch}/context"]
        ModelRoutes["/custom_models<br/>/model_sets<br/>/default_settings"]
    end
    
    subgraph "Proxyable API Routes"
        ConnectRoute["/plans/{planId}/{branch}/connect<br/>ConnectPlanHandler<br/>isStreaming: true"]
        StopRoute["/plans/{planId}/{branch}/stop<br/>StopPlanHandler"]
        StatusRoute["/plans/{planId}/{branch}/build_status<br/>GetBuildStatusHandler"]
    end
    
    RouteDefinition --> HealthCheck
    RouteDefinition --> VersionCheck
    RouteDefinition --> AccountRoutes
    RouteDefinition --> OrgRoutes
    RouteDefinition --> PlanRoutes
    RouteDefinition --> ModelRoutes
    RouteDefinition --> ConnectRoute
    RouteDefinition --> StopRoute
    RouteDefinition --> StatusRoute
```

The route registration uses a function pointer pattern where `HandlePlandexFn` is set during server initialization in `main.go`, allowing for flexible handler configuration while maintaining type safety through the `PlandexHandler` type alias.

**Sources:** [app/server/routes/routes.go:15-28](), [app/server/routes/routes.go:89-190](), [app/server/routes/routes.go:192-203](), [app/server/main.go:18-20]()

## Authentication and Session Management

The server implements a comprehensive authentication system with email verification, sign-in codes, and JWT token management handled primarily in `handlers/sessions.go`:

```mermaid
graph TD
    subgraph "Email Verification Flow"
        CreateVerification["CreateEmailVerificationHandler"] --> CheckUser["GetUserByEmail()<br/>HasAccount determination"]
        CheckUser --> GeneratePin["GetRandomAlphanumeric(6)<br/>SHA256 hash"]
        GeneratePin --> StoreVerification["db.CreateEmailVerification()"]
        StoreVerification --> SendEmail["email.SendVerificationEmail()"]
    end
    
    subgraph "Sign-In Process"
        SignInRequest["SignInHandler"] --> ValidatePin["CheckEmailPinHandler<br/>db.ValidateEmailVerification()"]
        ValidatePin --> ValidateAndSignIn["ValidateAndSignIn()<br/>Create JWT token"]
        ValidateAndSignIn --> SetCookies["Set auth cookies<br/>for browser clients"]
    end
    
    subgraph "Cross-Client Authentication"
        CreateSignInCode["CreateSignInCodeHandler<br/>Authenticated endpoint"] --> GenerateCode["GetRandomAlphanumeric(6)<br/>SHA256 hash"]
        GenerateCode --> StoreCode["db.CreateSignInCode()"]
        StoreCode --> ShareCode["Return plain code<br/>for client transfer"]
    end
    
    subgraph "Session Management"
        SignOut["SignOutHandler"] --> InvalidateToken["UPDATE auth_tokens<br/>SET deleted_at = NOW()"]
        InvalidateToken --> ClearCookies["ClearAuthCookieIfBrowser()<br/>ClearAccountFromCookies()"]
    end
    
    subgraph "User Configuration"
        GetOrgConfig["GetOrgUserConfigHandler"] --> LoadConfig["db.GetOrgUserConfig()"]
        UpdateOrgConfig["UpdateOrgUserConfigHandler"] --> SaveConfig["db.UpdateOrgUserConfig()"]
    end
```

Key authentication features include:
- Local development mode bypass with `GOENV=development` and `LOCAL_MODE=1`
- PIN-based email verification with 6-character alphanumeric codes
- Cross-client sign-in codes for UI-to-CLI authentication transfer
- JWT token invalidation on sign-out with database cleanup
- Per-organization user configuration management

**Sources:** [app/server/handlers/sessions.go:18-136](), [app/server/handlers/sessions.go:176-209](), [app/server/handlers/sessions.go:252-285](), [app/server/handlers/sessions.go:287-346]()

## Database Integration and User Management

Database operations are centralized in the `db` package with comprehensive user and organization management in `user_helpers.go`:

```mermaid
graph TD
    subgraph "Database Connection Flow"
        MustInitDb["setup.MustInitDb()"] --> DbConnect["db.Connect()"]
        DbConnect --> Migrations["db.MigrationsUp()"]
        Migrations --> CacheRoles["db.CacheOrgRoleIds()"]
    end
    
    subgraph "User Operations"
        GetUser["GetUser(userId)<br/>Single user lookup"] --> UserQuery["SELECT * FROM users<br/>WHERE id = $1"]
        GetUserByEmail["GetUserByEmail(email)"] --> EmailQuery["SELECT * FROM users<br/>WHERE email = $1"]
        CreateUser["CreateUser(name, email, tx)<br/>Domain extraction"] --> InsertUser["INSERT INTO users<br/>RETURNING id"]
    end
    
    subgraph "Organization User Management"
        GetOrgUser["GetOrgUser(userId, orgId)"] --> OrgUserQuery["SELECT * FROM orgs_users<br/>WHERE user_id = $1 AND org_id = $2"]
        ListOrgUsers["ListOrgUsers(orgId)"] --> ListUsers["ListUsers(orgId)<br/>JOIN with users table"]
        GetOrgUserConfig["GetOrgUserConfig()"] --> ConfigQuery["SELECT config FROM orgs_users"]
    end
    
    subgraph "Error Handling"
        SqlNoRows["sql.ErrNoRows<br/>Returns nil"] --> NonUniqueErr["IsNonUniqueErr()<br/>Duplicate handling"]
        NonUniqueErr --> PqArray["pq.Array() for bulk operations"]
    end
    
    UserQuery --> SqlNoRows
    EmailQuery --> SqlNoRows
    InsertUser --> NonUniqueErr
    ListUsers --> PqArray
```

The database layer includes sophisticated error handling and transaction management:
- `sql.ErrNoRows` handling to distinguish between missing records and errors
- Domain extraction from email addresses for user categorization
- Bulk operations using PostgreSQL array parameters via `pq.Array()`
- Transaction support with `*sqlx.Tx` parameter passing
- Role-based access control with `NumUsersWithRole()` validation

**Sources:** [app/server/db/user_helpers.go:13-26](), [app/server/db/user_helpers.go:28-41](), [app/server/db/user_helpers.go:132-155](), [app/server/db/user_helpers.go:98-130](), [app/server/setup/setup.go:27-42]()

## Server Lifecycle and LiteLLM Integration

The server initialization process in `main.go` includes critical AI model proxy setup and graceful shutdown handling:

```mermaid
graph LR
    subgraph "Initialization Sequence"
        MainStart["main()"] --> LogConfig["log.SetFlags()<br/>LstdFlags | Lmicroseconds | Lshortfile"]
        LogConfig --> RouteReg["routes.RegisterHandlePlandex()<br/>Function pointer setup"]
        RouteReg --> LiteLLMSetup["model.EnsureLiteLLM(2)<br/>AI proxy startup"]
        LiteLLMSetup --> ShutdownReg["setup.RegisterShutdownHook()<br/>model.ShutdownLiteLLMServer()"]
    end
    
    subgraph "Router Configuration"
        RouterCreate["mux.NewRouter()"] --> HealthRoutes["routes.AddHealthRoutes(r)"]
        HealthRoutes --> ApiRoutes["routes.AddApiRoutes(r)"]
        ApiRoutes --> ProxyRoutes["routes.AddProxyableApiRoutes(r)"]
    end
    
    subgraph "Server Startup"
        IPLoad["setup.MustLoadIp()"] --> DBInit["setup.MustInitDb()"]
        DBInit --> ServerStart["setup.StartServer(r, nil, nil)"]
        ServerStart --> OsExit["os.Exit(0)"]
    end
    
    ShutdownReg --> RouterCreate
    ProxyRoutes --> IPLoad
```

Key lifecycle components include:
- LiteLLM proxy server management with retry count parameter (2 retries)
- Comprehensive logging configuration with microsecond timestamps and short file names  
- Shutdown hook registration for clean AI model proxy termination
- Fatal error handling with `panic()` for critical startup failures
- Graceful exit with `os.Exit(0)` after server shutdown completion

**Sources:** [app/server/main.go:14-38](), [app/server/main.go:22-28](), [app/server/setup/setup.go:44-48]()

## Client-Server Communication

The CLI communicates with the server through a sophisticated HTTP client architecture with retry logic, authentication, and timeout management:

```mermaid
graph TD
    subgraph "Client Architecture"
        ApiStruct["Api struct<br/>implements types.ApiClient"] --> GetApiHost["GetApiHost()<br/>Cloud vs self-hosted"]
        GetApiHost --> ClientTypes["Multiple HTTP clients<br/>Fast, Slow, Streaming"]
    end
    
    subgraph "Transport Layer"
        BaseTransport["baseTransport<br/>net.Dialer timeout: 10s"] --> RetryTransport["retryTransport<br/>MaxRetries: 3<br/>BaseDelay: 500ms<br/>MaxDelay: 5s<br/>Jitter: 300ms"]
        RetryTransport --> AuthTransports["authenticatedTransport<br/>vs unauthenticatedTransport"]
    end
    
    subgraph "Client Configurations"
        UnauthClient["unauthenticatedClient<br/>fastReqTimeout: 30s"] --> PublicEndpoints["Health, version checks"]
        AuthFastClient["authenticatedFastClient<br/>fastReqTimeout: 30s"] --> QuickOps["List, get operations"]
        AuthSlowClient["authenticatedSlowClient<br/>slowReqTimeout: 5min"] --> LongOps["Apply, build operations"]
        AuthStreamClient["authenticatedStreamingClient<br/>No timeout"] --> StreamOps["Tell, connect operations"]
    end
    
    subgraph "Retry Logic"
        RetryCheck["retryTransport.RoundTrip()"] --> StatusCheck["RetryStatuses map<br/>502, 503, 504"]
        StatusCheck --> BackoffCalc["Exponential backoff<br/>math.Pow(2, attempt)"]
        BackoffCalc --> JitterAdd["Jitter randomization<br/>rand.Int63n()"]
    end
    
    AuthTransports --> UnauthClient
    AuthTransports --> AuthFastClient
    AuthTransports --> AuthSlowClient
    AuthTransports --> AuthStreamClient
    
    RetryTransport --> RetryCheck
```

The client system includes sophisticated error handling and environment configuration:
- Dynamic API host selection based on `auth.Current.IsCloud` flag
- Development environment support via `PLANDEX_ENV` and `PLANDEX_API_HOST` variables
- Network timeout detection with `net.Error` interface checking
- Exponential backoff with jitter to prevent thundering herd problems
- Authentication header injection via `auth.SetAuthHeader()` and `auth.SetVersionHeader()`

**Sources:** [app/cli/api/clients.go:23-42](), [app/cli/api/clients.go:66-117](), [app/cli/api/clients.go:136-161](), [app/cli/api/clients.go:44-64]()
</old_str>
<new_str>
## HTTP Server Configuration

The server configuration in `setup.go` implements comprehensive middleware, graceful shutdown, and database initialization. The `StartServer` function orchestrates the complete HTTP server lifecycle:

```mermaid
graph LR
    subgraph "Server Configuration"
        StartServer["StartServer()"] --> EnvCheck["GOENV development check"]
        EnvCheck --> ShutdownCtx["shutdown.ShutdownCtx setup"]
        ShutdownCtx --> PortConfig["PORT env var<br/>default: 8099"]
        PortConfig --> MiddlewareStack["Middleware application"]
    end
    
    subgraph "Middleware Pipeline"
        LoggingMW["loggingMiddleware()<br/>Skip /health, /version"] --> MaxBytesMW["maxBytesMiddleware()<br/>1GB limit, 1MB headers"]
        MaxBytesMW --> ConfigureFn["configureFn()<br/>Optional configuration"]
    end
    
    subgraph "HTTP Server Specs"
        ServerConfig["http.Server<br/>Addr: :PORT<br/>MaxHeaderBytes: 1MB<br/>ReadHeaderTimeout: 5s"] --> ListenServe["ListenAndServe()<br/>Goroutine"]
    end
    
    subgraph "Shutdown Handling"
        SignalCapture["signal.Notify()<br/>SIGTERM, SIGINT"] --> WaitActivePlans["waitForActivePlans()<br/>1s ticker polling<br/>plan.NumActivePlans()"]
        WaitActivePlans --> CleanupLocks["db.CleanupActiveLocks()"] 
        CleanupLocks --> HTTPShutdown["server.Shutdown()<br/>30s timeout"]
        HTTPShutdown --> ShutdownHooks["Execute shutdown hooks<br/>model.ShutdownLiteLLMServer()"]
    end
    
    MiddlewareStack --> ServerConfig
    ListenServe --> SignalCapture
```

The middleware stack includes several critical components:
- `loggingMiddleware`: Logs request method, path, and duration while excluding monitoring endpoints
- `maxBytesMiddleware`: Uses `http.MaxBytesReader` to enforce the 1GB request body limit
- Database connection cleanup with deferred `db.Conn.Close()`
- Graceful shutdown with 60-second active plan timeout followed by 30-second HTTP shutdown timeout

**Sources:** [app/server/setup/setup.go:66-185](), [app/server/setup/setup.go:50-64](), [app/server/setup/setup.go:187-214]()

## Route Organization

Routes are organized using the `mux.Router` from Gorilla Mux with a configurable handler registration system. The `routes.go` file defines three distinct route categories:

| Route Function | Purpose | Handler Registration |
|---|---|---|
| `AddHealthRoutes` | System monitoring | `/health`, `/version` endpoints |
| `AddApiRoutes` | Standard CRUD operations | Plan, context, user management |
| `AddProxyableApiRoutes` | Real-time operations | Active plan streaming, status |

```mermaid
graph TD
    subgraph "Route Registration Pattern"
        RegisterFn["routes.RegisterHandlePlandex()"] --> HandlePlandexFn["HandlePlandexFn variable<br/>Function pointer"]
        HandlePlandexFn --> RouteDefinition["router.HandleFunc(path, handler)"]
    end
    
    subgraph "Health Routes"
        HealthCheck["/health --> hooks.ExecHook(hooks.HealthCheck)"]
        VersionCheck["/version --> Read version.txt<br/>Handle IS_CLOUD env"]
    end
    
    subgraph "Standard API Routes (89 total)"
        AccountRoutes["/accounts/email_verifications<br/>/accounts/sign_in<br/>/accounts/sign_out"]
        OrgRoutes["/orgs<br/>/orgs/session<br/>/users"]
        PlanRoutes["/plans<br/>/plans/{planId}<br/>/plans/{planId}/{branch}/context"]
        ModelRoutes["/custom_models<br/>/model_sets<br/>/default_settings"]
    end
    
    subgraph "Proxyable API Routes"
        ConnectRoute["/plans/{planId}/{branch}/connect<br/>ConnectPlanHandler<br/>isStreaming: true"]
        StopRoute["/plans/{planId}/{branch}/stop<br/>StopPlanHandler"]
        StatusRoute["/plans/{planId}/{branch}/build_status<br/>GetBuildStatusHandler"]
    end
    
    RouteDefinition --> HealthCheck
    RouteDefinition --> VersionCheck
    RouteDefinition --> AccountRoutes
    RouteDefinition --> OrgRoutes
    RouteDefinition --> PlanRoutes
    RouteDefinition --> ModelRoutes
    RouteDefinition --> ConnectRoute
    RouteDefinition --> StopRoute
    RouteDefinition --> StatusRoute
```

The route registration uses a function pointer pattern where `HandlePlandexFn` is set during server initialization in `main.go`, allowing for flexible handler configuration while maintaining type safety through the `PlandexHandler` type alias.

**Sources:** [app/server/routes/routes.go:15-28](), [app/server/routes/routes.go:89-190](), [app/server/routes/routes.go:192-203](), [app/server/main.go:18-20]()

## HTTP Server Configuration

The server is configured in `setup.go` with specific timeouts, middleware, and graceful shutdown handling. The `StartServer` function sets up the complete HTTP server stack:

```mermaid
graph LR
    subgraph "Server Setup Flow"
        Start["StartServer()"] --> LoadConfig["Load Configuration<br/>PORT env var"]
        LoadConfig --> Middleware["Apply Middleware<br/>loggingMiddleware<br/>maxBytesMiddleware"]
        Middleware --> HTTPServer["http.Server<br/>MaxHeaderBytes: 1MB<br/>ReadHeaderTimeout: 5s"]
        HTTPServer --> Listen["ListenAndServe<br/>on configured port"]
    end
    
    subgraph "Shutdown Handling"
        SigTerm["SIGTERM/SIGINT"] --> WaitPlans["waitForActivePlans()<br/>60s timeout"]
        WaitPlans --> CleanupLocks["db.CleanupActiveLocks()"]
        CleanupLocks --> ServerShutdown["server.Shutdown()<br/>30s timeout"]
    end
    
    Listen --> SigTerm
```

The server includes several key middleware components:
- `loggingMiddleware`: Logs all requests except `/health` and `/version` endpoints
- `maxBytesMiddleware`: Limits request body size to 1GB
- Authentication middleware: Handled per-route basis in handlers

**Sources:** [app/server/setup/setup.go:66-185](), [app/server/setup/setup.go:50-64](), [app/server/setup/setup.go:206-214]()

## Route Organization

Routes are organized into two main categories defined in `routes.go`:

| Route Category | Function | Purpose |
|---|---|---|
| `AddApiRoutes` | Standard API endpoints | Plan management, context, settings |
| `AddProxyableApiRoutes` | Real-time endpoints | Active plan operations, streaming |

```mermaid
graph TD
    subgraph "API Route Categories"
        Standard["Standard API Routes<br/>addApiRoutes()"]
        Proxyable["Proxyable API Routes<br/>addProxyableApiRoutes()"]
    end
    
    subgraph "Standard Endpoints"
        Plans["/plans - ListPlansHandler<br/>/plans/{id} - GetPlanHandler<br/>/plans/{id}/{branch}/context - LoadContextHandler"]
        Auth["/accounts/sign_in - SignInHandler<br/>/orgs - ListOrgsHandler"]
        Settings["/plans/{id}/settings - GetSettingsHandler<br/>/model_sets - ListModelPacksHandler"]
    end
    
    subgraph "Proxyable Endpoints"
        Connect["/plans/{id}/{branch}/connect - ConnectPlanHandler"]
        Stop["/plans/{id}/{branch}/stop - StopPlanHandler"]
        Status["/plans/{id}/{branch}/build_status - GetBuildStatusHandler"]
    end
    
    Standard --> Plans
    Standard --> Auth
    Standard --> Settings
    
    Proxyable --> Connect
    Proxyable --> Stop
    Proxyable --> Status
```

**Sources:** [app/server/routes/routes.go:73-185](), [app/server/routes/routes.go:187-198]()

## Authentication and Session Management

The server implements a comprehensive authentication system with email verification, sign-in codes, and JWT token management handled primarily in `handlers/sessions.go`:

```mermaid
graph TD
    subgraph "Email Verification Flow"
        CreateVerification["CreateEmailVerificationHandler"] --> CheckUser["GetUserByEmail()<br/>HasAccount determination"]
        CheckUser --> GeneratePin["GetRandomAlphanumeric(6)<br/>SHA256 hash"]
        GeneratePin --> StoreVerification["db.CreateEmailVerification()"]
        StoreVerification --> SendEmail["email.SendVerificationEmail()"]
    end
    
    subgraph "Sign-In Process"
        SignInRequest["SignInHandler"] --> ValidatePin["CheckEmailPinHandler<br/>db.ValidateEmailVerification()"]
        ValidatePin --> ValidateAndSignIn["ValidateAndSignIn()<br/>Create JWT token"]
        ValidateAndSignIn --> SetCookies["Set auth cookies<br/>for browser clients"]
    end
    
    subgraph "Cross-Client Authentication"
        CreateSignInCode["CreateSignInCodeHandler<br/>Authenticated endpoint"] --> GenerateCode["GetRandomAlphanumeric(6)<br/>SHA256 hash"]
        GenerateCode --> StoreCode["db.CreateSignInCode()"]
        StoreCode --> ShareCode["Return plain code<br/>for client transfer"]
    end
    
    subgraph "Session Management"
        SignOut["SignOutHandler"] --> InvalidateToken["UPDATE auth_tokens<br/>SET deleted_at = NOW()"]
        InvalidateToken --> ClearCookies["ClearAuthCookieIfBrowser()<br/>ClearAccountFromCookies()"]
    end
    
    subgraph "User Configuration"
        GetOrgConfig["GetOrgUserConfigHandler"] --> LoadConfig["db.GetOrgUserConfig()"]
        UpdateOrgConfig["UpdateOrgUserConfigHandler"] --> SaveConfig["db.UpdateOrgUserConfig()"]
    end
```

Key authentication features include:
- Local development mode bypass with `GOENV=development` and `LOCAL_MODE=1`
- PIN-based email verification with 6-character alphanumeric codes
- Cross-client sign-in codes for UI-to-CLI authentication transfer
- JWT token invalidation on sign-out with database cleanup
- Per-organization user configuration management

**Sources:** [app/server/handlers/sessions.go:18-136](), [app/server/handlers/sessions.go:176-209](), [app/server/handlers/sessions.go:252-285](), [app/server/handlers/sessions.go:287-346]()

## Database Integration and User Management

Database operations are centralized in the `db` package with comprehensive user and organization management in `user_helpers.go`:

```mermaid
graph TD
    subgraph "Database Connection Flow"
        MustInitDb["setup.MustInitDb()"] --> DbConnect["db.Connect()"]
        DbConnect --> Migrations["db.MigrationsUp()"]
        Migrations --> CacheRoles["db.CacheOrgRoleIds()"]
    end
    
    subgraph "User Operations"
        GetUser["GetUser(userId)<br/>Single user lookup"] --> UserQuery["SELECT * FROM users<br/>WHERE id = $1"]
        GetUserByEmail["GetUserByEmail(email)"] --> EmailQuery["SELECT * FROM users<br/>WHERE email = $1"]
        CreateUser["CreateUser(name, email, tx)<br/>Domain extraction"] --> InsertUser["INSERT INTO users<br/>RETURNING id"]
    end
    
    subgraph "Organization User Management"
        GetOrgUser["GetOrgUser(userId, orgId)"] --> OrgUserQuery["SELECT * FROM orgs_users<br/>WHERE user_id = $1 AND org_id = $2"]
        ListOrgUsers["ListOrgUsers(orgId)"] --> ListUsers["ListUsers(orgId)<br/>JOIN with users table"]
        GetOrgUserConfig["GetOrgUserConfig()"] --> ConfigQuery["SELECT config FROM orgs_users"]
    end
    
    subgraph "Error Handling"
        SqlNoRows["sql.ErrNoRows<br/>Returns nil"] --> NonUniqueErr["IsNonUniqueErr()<br/>Duplicate handling"]
        NonUniqueErr --> PqArray["pq.Array() for bulk operations"]
    end
    
    UserQuery --> SqlNoRows
    EmailQuery --> SqlNoRows
    InsertUser --> NonUniqueErr
    ListUsers --> PqArray
```

The database layer includes sophisticated error handling and transaction management:
- `sql.ErrNoRows` handling to distinguish between missing records and errors
- Domain extraction from email addresses for user categorization
- Bulk operations using PostgreSQL array parameters via `pq.Array()`
- Transaction support with `*sqlx.Tx` parameter passing
- Role-based access control with `NumUsersWithRole()` validation

**Sources:** [app/server/db/user_helpers.go:13-26](), [app/server/db/user_helpers.go:28-41](), [app/server/db/user_helpers.go:132-155](), [app/server/db/user_helpers.go:98-130](), [app/server/setup/setup.go:27-42]()

## Server Lifecycle and LiteLLM Integration

The server initialization process in `main.go` includes critical AI model proxy setup and graceful shutdown handling:

```mermaid
graph LR
    subgraph "Initialization Sequence"
        MainStart["main()"] --> LogConfig["log.SetFlags()<br/>LstdFlags | Lmicroseconds | Lshortfile"]
        LogConfig --> RouteReg["routes.RegisterHandlePlandex()<br/>Function pointer setup"]
        RouteReg --> LiteLLMSetup["model.EnsureLiteLLM(2)<br/>AI proxy startup"]
        LiteLLMSetup --> ShutdownReg["setup.RegisterShutdownHook()<br/>model.ShutdownLiteLLMServer()"]
    end
    
    subgraph "Router Configuration"
        RouterCreate["mux.NewRouter()"] --> HealthRoutes["routes.AddHealthRoutes(r)"]
        HealthRoutes --> ApiRoutes["routes.AddApiRoutes(r)"]
        ApiRoutes --> ProxyRoutes["routes.AddProxyableApiRoutes(r)"]
    end
    
    subgraph "Server Startup"
        IPLoad["setup.MustLoadIp()"] --> DBInit["setup.MustInitDb()"]
        DBInit --> ServerStart["setup.StartServer(r, nil, nil)"]
        ServerStart --> OsExit["os.Exit(0)"]
    end
    
    ShutdownReg --> RouterCreate
    ProxyRoutes --> IPLoad
```

Key lifecycle components include:
- LiteLLM proxy server management with retry count parameter (2 retries)
- Comprehensive logging configuration with microsecond timestamps and short file names  
- Shutdown hook registration for clean AI model proxy termination
- Fatal error handling with `panic()` for critical startup failures
- Graceful exit with `os.Exit(0)` after server shutdown completion

**Sources:** [app/server/main.go:14-38](), [app/server/main.go:22-28](), [app/server/setup/setup.go:44-48]()

## Request Processing Pipeline

Each request goes through a standardized processing pipeline with middleware, authentication, and business logic layers:

```mermaid
graph TD
    subgraph "Middleware Layer"
        IncomingReq["HTTP Request"] --> LogMiddleware["loggingMiddleware()<br/>Log method & path"]
        LogMiddleware --> MaxBytesMiddleware["maxBytesMiddleware()<br/>1GB body limit"]
        MaxBytesMiddleware --> RouterMatch["mux.Router<br/>Path matching"]
    end
    
    subgraph "Handler Execution"
        RouterMatch --> HandlerType{Handler Type}
        HandlerType -->|Authentication Required| AuthFlow["Authenticate(w, r, true)<br/>JWT validation"]
        HandlerType -->|Public Endpoint| DirectHandler["Health/Version handlers"]
        AuthFlow --> ParseBody["Parse Request Body<br/>json.Unmarshal()"]
        ParseBody --> BizLogic["Handler-specific Logic"]
    end
    
    subgraph "Response Generation"
        BizLogic --> ProcessResult["Process Result"]
        ProcessResult --> MarshalResp["json.Marshal(response)"]
        MarshalResp --> WriteResponse["w.Write(bytes)"]
        DirectHandler --> WriteResponse
    end
    
    subgraph "Error Handling"
        AuthFlow -->|Auth Failure| AuthError["http.Error()<br/>401/403 status"]
        ParseBody -->|Parse Error| ParseError["http.Error()<br/>400 status"]
        BizLogic -->|Logic Error| BizError["http.Error()<br/>5xx status"]
    end
```

The pipeline includes comprehensive error handling at each stage:
- Middleware errors return early with appropriate HTTP status codes
- Authentication failures use standard HTTP error responses
- JSON parsing errors return 400 Bad Request
- Business logic errors map to appropriate 4xx/5xx status codes

**Sources:** [app/server/setup/setup.go:50-64](), [app/server/handlers/sessions.go:179-183](), [app/server/handlers/sessions.go:223-237]()

## Client-Server Communication

The CLI communicates with the server through HTTP clients with sophisticated retry and authentication logic:

```mermaid
graph TD
    subgraph "Client Architecture"
        ApiStruct["Api struct<br/>Implements ApiClient"] --> Clients["HTTP Clients<br/>Fast, Slow, Streaming"]
        Clients --> Transport["Transport Layer<br/>Retry & Auth"]
    end
    
    subgraph "Transport Types"
        AuthTransport["authenticatedTransport<br/>Adds auth headers"] --> RetryTransport["retryTransport<br/>Exponential backoff<br/>502/503/504 retries"]
        UnauthTransport["unauthenticatedTransport<br/>No auth required"]
    end
    
    subgraph "Client Types"
        FastClient["authenticatedFastClient<br/>30s timeout"] --> QuickOps["Quick operations<br/>List, Get, Delete"]
        SlowClient["authenticatedSlowClient<br/>5min timeout"] --> LongOps["Long operations<br/>Apply, Build"]
        StreamClient["authenticatedStreamingClient<br/>No timeout"] --> RealTime["Real-time ops<br/>Tell, Connect"]
    end
    
    Transport --> AuthTransport
    Transport --> UnauthTransport
    Clients --> FastClient
    Clients --> SlowClient
    Clients --> StreamClient
```

**Sources:** [app/cli/api/clients.go:18-160]()

## Server Lifecycle Management

The server implements graceful startup and shutdown procedures:

```mermaid
graph LR
    subgraph "Startup Sequence"
        Start["main()"] --> LoadIP["MustLoadIp()<br/>Host configuration"]
        LoadIP --> InitDB["MustInitDb()<br/>Connect & migrate"]
        InitDB --> StartServer["StartServer()<br/>HTTP listener"]
    end
    
    subgraph "Shutdown Sequence"
        Signal["SIGTERM/SIGINT"] --> WaitPlans["Wait for Active Plans<br/>60s timeout"]
        WaitPlans --> CleanupLocks["Cleanup Repository Locks<br/>db.CleanupActiveLocks"]
        CleanupLocks --> HTTPShutdown["HTTP Server Shutdown<br/>30s timeout"]
        HTTPShutdown --> DBClose["Close Database<br/>db.Conn.Close()"]
    end
    
    StartServer --> Signal
```

**Sources:** [app/server/main.go:12-28](), [app/server/setup/setup.go:20-42](), [app/server/setup/setup.go:119-185]()

---

# Page: HTTP API and Request Handlers

# HTTP API and Request Handlers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/cli/api/clients.go](app/cli/api/clients.go)
- [app/cli/lib/git.go](app/cli/lib/git.go)
- [app/server/db/result_helpers.go](app/server/db/result_helpers.go)
- [app/server/db/user_helpers.go](app/server/db/user_helpers.go)
- [app/server/handlers/branches.go](app/server/handlers/branches.go)
- [app/server/handlers/client_helper.go](app/server/handlers/client_helper.go)
- [app/server/handlers/context_helper.go](app/server/handlers/context_helper.go)
- [app/server/handlers/plans_changes.go](app/server/handlers/plans_changes.go)
- [app/server/handlers/plans_context.go](app/server/handlers/plans_context.go)
- [app/server/handlers/plans_convo.go](app/server/handlers/plans_convo.go)
- [app/server/handlers/plans_exec.go](app/server/handlers/plans_exec.go)
- [app/server/handlers/plans_versions.go](app/server/handlers/plans_versions.go)
- [app/server/handlers/sessions.go](app/server/handlers/sessions.go)
- [app/server/handlers/settings.go](app/server/handlers/settings.go)
- [app/server/main.go](app/server/main.go)
- [app/server/routes/routes.go](app/server/routes/routes.go)
- [app/server/setup/setup.go](app/server/setup/setup.go)

</details>



This document details the REST API endpoints and their corresponding request handlers in the Plandex server. These handlers implement the HTTP interface between clients (primarily the Plandex CLI) and the server, enabling plan management, context operations, and user interactions.

The handlers are organized into several modules in the `app/server/handlers/` directory, each responsible for different aspects of the system functionality.

## Request Handler Architecture

The Plandex server implements RESTful HTTP handlers organized by functionality. Each handler module contains functions that process specific API requests, handle authentication, execute business logic, and return appropriate responses.

```mermaid
graph TD
    subgraph "Handler Module Organization"
        plansExec["plans_exec.go<br/>TellPlanHandler<br/>BuildPlanHandler<br/>ConnectPlanHandler<br/>StopPlanHandler"]
        plansContext["plans_context.go<br/>LoadContextHandler<br/>ListContextHandler<br/>UpdateContextHandler<br/>DeleteContextHandler"]
        plansChanges["plans_changes.go<br/>ApplyPlanHandler<br/>RejectAllChangesHandler<br/>RejectFileHandler<br/>GetPlanDiffsHandler"]
        branches["branches.go<br/>ListBranchesHandler<br/>CreateBranchHandler<br/>DeleteBranchHandler"]
        contextHelper["context_helper.go<br/>loadContexts()"]
    end

    httpRequest["HTTP Request"] --> authentication["Authenticate()"]
    authentication --> authorization["authorizePlan()"]
    authorization --> plansExec
    authorization --> plansContext
    authorization --> plansChanges
    authorization --> branches
    
    plansContext --> contextHelper
    
    plansExec --> modelPlan["model/plan.Tell()"]
    plansExec --> modelPlan2["model/plan.Build()"]
    
    plansContext --> dbLoadContexts["db.LoadContexts()"]
    plansChanges --> dbApplyPlan["db.ApplyPlan()"]
    branches --> dbListBranches["db.ListPlanBranches()"]
```

Sources: [app/server/handlers/plans_exec.go:1-589](), [app/server/handlers/plans_context.go:1-447](), [app/server/handlers/plans_changes.go:1-566](), [app/server/handlers/branches.go:1-207]()

## API Routes Registration

The Plandex server registers API routes in the `routes.go` file, configuring HTTP handlers using the Gorilla mux router. Routes are categorized into:

1. Regular API routes (`addApiRoutes`)
2. Proxyable API routes (`addProxyableApiRoutes`) - These can be handled by any server in a distributed setup

```mermaid
graph TD
    subgraph "Route Registration Process"
        Main["main.go#main()"] --> Setup["setup.StartServer()"]
        Setup --> Router["mux.NewRouter()"]
        Router --> ApiRoutes["AddApiRoutes()"]
        Router --> ProxyRoutes["AddProxyableApiRoutes()"]
        
        ApiRoutes --> HandleFunc["router.HandleFunc()"]
        ProxyRoutes --> HandleFunc
        
        HandleFunc --> Handlers["Handler Functions"]
    end
```

Sources: [app/server/main.go:11-28](), [app/server/routes/routes.go:72-185](), [app/server/setup/setup.go:62-95]()

## API Endpoints Overview

The following table summarizes the key API endpoints by category:

| Category | Example Endpoint | Description |
|----------|------------------|-------------|
| Authentication | `/accounts/sign_in` | User authentication and session management |
| Plan Management | `/plans` | List, create, update, and delete plans |
| Plan Execution | `/plans/{planId}/{branch}/tell` | Execute plans with AI models |
| Context Management | `/plans/{planId}/{branch}/context` | Manage context for AI models |
| Plan Changes | `/plans/{planId}/{branch}/apply` | Apply or reject generated changes |
| Branch Management | `/plans/{planId}/branches` | Manage Git branches |
| Organization | `/orgs` | Manage organizations and users |
| Projects | `/projects` | Manage projects |
| Model Configuration | `/model_sets` | Configure AI models |

Sources: [app/server/routes/routes.go:89-185](), [app/server/routes/routes.go:187-198]()

## Request Handler Common Patterns

Most handlers follow consistent patterns for authentication, authorization, and error handling.

### Authentication and Authorization Flow

```mermaid
graph TD
    httpRequest["HTTP Request"] --> authenticate["Authenticate(w, r, true)"]
    authenticate --> authSuccess{"Authentication Success?"}
    authSuccess -- "No" --> return401["Return 401 Unauthorized"]
    authSuccess -- "Yes" --> authorizePlan["authorizePlan(w, planId, auth)"]
    authorizePlan --> planAuth{"Plan Authorization?"}
    planAuth -- "No" --> return403["Return 403 Forbidden"]
    planAuth -- "Yes" --> parseBody["Parse Request Body"]
    parseBody --> validateInput["Validate Input"]
    validateInput --> execOperation["Execute Business Logic"]
    execOperation --> response["Return Response"]
```

**Core Authentication Functions:**
- `Authenticate(w http.ResponseWriter, r *http.Request, required bool) *types.ServerAuth`
- `authorizePlan(w http.ResponseWriter, planId string, auth *types.ServerAuth) *db.Plan`
- `authorizePlanExecUpdate(w http.ResponseWriter, planId string, auth *types.ServerAuth) *db.Plan`

The `authorizePlanExecUpdate` function adds an additional permission check for plan modification operations using `auth.HasPermission(shared.PermissionUpdateAnyPlan)`.

Sources: [app/server/handlers/plans_exec.go:575-588](), [app/server/handlers/plans_exec.go:26-40]()

### Repository Operation Pattern

Many handlers use `db.ExecRepoOperation()` to ensure proper Git repository locking and transaction management:

```mermaid
graph TD
    handler["Handler Function"] --> execRepo["db.ExecRepoOperation()"]
    execRepo --> acquireLock["Acquire Repository Lock"]
    acquireLock --> operation["Execute Repository Operation"]
    operation --> gitCommit["Git Add & Commit"]
    gitCommit --> releaseLock["Release Lock"]
    releaseLock --> response["Return Response"]
    
    operation -- "Error" --> rollback["Rollback Changes"]
    rollback --> releaseLock
```

**ExecRepoOperationParams Structure:**
- `OrgId string` - Organization identifier
- `UserId string` - User identifier  
- `PlanId string` - Plan identifier
- `Branch string` - Git branch name
- `Scope db.LockScope` - Read or write lock scope
- `Reason string` - Operation description for logging

Sources: [app/server/handlers/plans_changes.go:151-177](), [app/server/handlers/plans_context.go:196-206]()

## Plan Execution Request Handlers

The plan execution handlers in `plans_exec.go` manage the core AI-powered planning and implementation workflow.

### TellPlanHandler Function

**Endpoint:** `POST /plans/{planId}/{branch}/tell`  
**Handler:** `TellPlanHandler(w http.ResponseWriter, r *http.Request)`

Initiates or continues a planning session with AI models. The handler processes `shared.TellPlanRequest` structures.

**Request Structure (TellPlanRequest):**
- `Prompt string` - User's natural language instruction
- `ApiKeys map[string]string` - API keys for different model providers  
- `ConnectStream bool` - Whether to establish streaming connection
- `AutoContext bool` - Enable automatic context loading
- `BuildMode BuildMode` - Auto or manual build mode
- `SessionId string` - Session identifier for tracking

**Handler Implementation Flow:**
1. `Authenticate(w, r, true)` - Verify user authentication
2. `authorizePlanExecUpdate(w, planId, auth)` - Check plan modification permissions  
3. `json.Unmarshal(body, &requestBody)` - Parse TellPlanRequest
4. `initClients()` - Initialize AI model clients from API keys
5. `modelPlan.Tell(clients, plan, branch, auth, &requestBody)` - Execute planning logic
6. `startResponseStream()` - Start streaming if ConnectStream=true

```mermaid
sequenceDiagram
    participant CLI as "CLI api.TellPlan()"
    participant Handler as "TellPlanHandler"
    participant Auth as "authorizePlanExecUpdate"
    participant Clients as "initClients"
    participant ModelPlan as "modelPlan.Tell"
    participant Stream as "startResponseStream"
    
    CLI->>Handler: POST with TellPlanRequest
    Handler->>Auth: Verify plan update permissions
    Auth-->>Handler: Plan authorized
    Handler->>Clients: initClients from ApiKeys
    Clients-->>Handler: Model clients initialized
    Handler->>ModelPlan: Tell(clients, plan, branch, auth, request)
    ModelPlan-->>Handler: Planning execution started
    
    alt ConnectStream = true
        Handler->>Stream: startResponseStream(ctx, w, auth, planId, branch)
        Stream-->>CLI: Server-Sent Events
    end
```

Sources: [app/server/handlers/plans_exec.go:23-98](), [app/shared/req_res.go:120-142]()

### BuildPlanHandler Function

**Endpoint:** `PATCH /plans/{planId}/{branch}/build`  
**Handler:** `BuildPlanHandler(w http.ResponseWriter, r *http.Request)`

Implements the plan by generating concrete code changes. Processes `shared.BuildPlanRequest` structures.

**Request Structure (BuildPlanRequest):**
- `ApiKeys map[string]string` - Model provider API keys
- `ConnectStream bool` - Enable streaming responses
- `SessionId string` - Session tracking identifier

**Implementation:** The handler follows similar authentication and client initialization patterns, then calls `modelPlan.Build()` to generate file modifications.

Sources: [app/server/handlers/plans_exec.go:100-170](), [app/shared/req_res.go:144-153]()

### ConnectPlanHandler Function

**Endpoint:** `PATCH /plans/{planId}/{branch}/connect`  
**Handler:** `ConnectPlanHandler(w http.ResponseWriter, r *http.Request)`

Establishes streaming connection to active plan execution. Uses `modelPlan.GetActivePlan()` to locate running plans and `startResponseStream()` for client communication.

Sources: [app/server/handlers/plans_exec.go:172-212]()

### StopPlanHandler Function

**Endpoint:** `DELETE /plans/{planId}/{branch}/stop`  
**Handler:** `StopPlanHandler(w http.ResponseWriter, r *http.Request)`

Terminates active plan execution by sending abort signals via `active.Stream()` and calling `modelPlan.Stop()`.

Sources: [app/server/handlers/plans_exec.go:214-288]()

### Build Plan

**Endpoint:** `PATCH /plans/{planId}/{branch}/build`

Implements the plan by generating code changes.

**Request Body:**
```json
{
  "apiKeys": {"openai": "key1", "anthropic": "key2"},
  "connectStream": true,
  "sessionId": "optional-session-id"
}
```

**Implementation Details:**
The handler authenticates the user, initializes AI model clients, calls `modelPlan.Build()` to generate code implementations, and optionally streams the results back to the client.

Sources: [app/server/handlers/plans_exec.go:100-170]()

### Connect Plan

**Endpoint:** `PATCH /plans/{planId}/{branch}/connect`

Establishes a streaming connection to an active plan.

**Implementation Details:**
Gets the active plan for the specified ID and branch. If no active plan exists locally, proxies the request to another server. Then starts a response stream to the client.

Sources: [app/server/handlers/plans_exec.go:172-212]()

### Stop Plan

**Endpoint:** `DELETE /plans/{planId}/{branch}/stop`

Terminates an active plan execution.

**Implementation Details:**
Gets the active plan, sends an abort message to the client, stores any partial reply, and stops the plan execution.

Sources: [app/server/handlers/plans_exec.go:214-288]()

## Context Management Endpoints

Contexts provide AI models with information about the codebase. These endpoints manage context loading and manipulation.

### LoadContextHandler Function

**Endpoint:** `POST /plans/{planId}/{branch}/context`  
**Handler:** `LoadContextHandler(w http.ResponseWriter, r *http.Request)`

Loads new contexts into a plan. Processes `shared.LoadContextRequest` which is an array of `LoadContextParams`.

**Request Structure (LoadContextParams):**
- `ContextType shared.ContextType` - File, URL, note, directory tree, piped data, image, or map
- `FilePath string` - Path for file contexts
- `Body string` - Content body for contexts
- `MapBodies shared.FileMapBodies` - For map-type contexts containing multiple files
- `ImageDetail openai.ImageURLDetail` - Detail level for image contexts
- `AutoLoaded bool` - Whether context was automatically loaded

**Handler Implementation:**
The handler delegates to `loadContexts()` helper function which handles validation, token calculation, and repository operations.

```mermaid
sequenceDiagram
    participant CLI as "CLI api.LoadContext()"
    participant Handler as "LoadContextHandler"
    participant Helper as "loadContexts()"
    participant Validator as "Context Validation"
    participant ExecRepo as "db.ExecRepoOperation"
    participant LoadCtx as "db.LoadContexts"
    participant GitRepo as "repo.GitAddAndCommit"
    
    CLI->>Handler: POST with LoadContextRequest[]
    Handler->>Helper: loadContexts(loadContextsParams)
    Helper->>Validator: Check MaxContextCount & MaxContextBodySize
    Validator-->>Helper: Validation passed
    Helper->>ExecRepo: ExecRepoOperation with LoadContexts
    ExecRepo->>LoadCtx: LoadContexts(ctx, LoadContextsParams)
    LoadCtx->>LoadCtx: Calculate token usage
    LoadCtx->>GitRepo: GitAddAndCommit(branchName, commitMsg)
    GitRepo-->>LoadCtx: Commit successful
    LoadCtx-->>ExecRepo: Return LoadContextResponse
    ExecRepo-->>Helper: Context loaded
    Helper-->>Handler: LoadContextResponse
    Handler-->>CLI: JSON with TokensAdded & TotalTokens
```

**Context Validation Logic:**
The `loadContexts()` helper in `context_helper.go` performs several validation checks:
- Total file count against `shared.MaxContextCount`
- Individual file size against `shared.MaxContextBodySize`  
- Map context paths against `shared.MaxContextMapPaths`
- Map file size against `shared.MaxContextMapSingleInputSize`

Sources: [app/server/handlers/plans_context.go:154-212](), [app/server/handlers/context_helper.go:29-280](), [app/shared/req_res.go:185-205]()

### List Contexts

**Endpoint:** `GET /plans/{planId}/{branch}/context`

Lists all contexts associated with a plan.

**Implementation Details:**
Executes a repository operation to get plan contexts and returns the list of contexts.

Sources: [app/server/handlers/plans_context.go:17-78]()

### Update Context

**Endpoint:** `PUT /plans/{planId}/{branch}/context`

Updates existing contexts in a plan.

Sources: [app/server/handlers/plans_context.go:214-318]()

### Delete Context

**Endpoint:** `DELETE /plans/{planId}/{branch}/context`

Removes contexts from a plan.

Sources: [app/server/handlers/plans_context.go:320-447]()

## Plan Changes Endpoints

These endpoints manage the changes produced by plan execution, allowing you to view, apply, or reject them.

### ApplyPlanHandler Function

**Endpoint:** `PATCH /plans/{planId}/{branch}/apply`  
**Handler:** `ApplyPlanHandler(w http.ResponseWriter, r *http.Request)`

Applies pending plan changes to the repository. Processes `shared.ApplyPlanRequest` and returns the generated commit message.

**Request Structure (ApplyPlanRequest):**
- `ApiKeys map[string]string` - Model provider API keys for commit message generation
- `SessionId string` - Session tracking identifier

**Handler Implementation Flow:**
1. `authorizePlan(w, planId, auth)` - Verify plan access
2. `db.GetPlanSettings(plan, true)` - Load plan configuration
3. `db.GetCurrentPlanState(currentPlanParams)` - Get pending changes
4. `modelPlan.GenCommitMsgForPendingResults()` - AI-generate commit message
5. `db.ApplyPlan()` - Apply changes and commit to repository

```mermaid
sequenceDiagram
    participant CLI as "CLI api.ApplyPlan()"
    participant Handler as "ApplyPlanHandler"
    participant GetState as "db.GetCurrentPlanState"
    participant GenCommit as "modelPlan.GenCommitMsgForPendingResults"
    participant ApplyPlan as "db.ApplyPlan"
    participant GitRepo as "Git Repository"
    
    CLI->>Handler: PATCH with ApplyPlanRequest
    Handler->>GetState: Get current plan state & pending changes
    GetState-->>Handler: CurrentPlanState with PlanResult
    Handler->>GenCommit: Generate commit message using AI
    GenCommit-->>Handler: Generated commit message
    Handler->>ApplyPlan: ExecRepoOperation with ApplyPlanParams
    ApplyPlan->>GitRepo: Apply file changes
    ApplyPlan->>GitRepo: Git commit with generated message
    GitRepo-->>ApplyPlan: Changes committed
    ApplyPlan-->>Handler: Apply successful
    Handler-->>CLI: Return commit message string
```

Sources: [app/server/handlers/plans_changes.go:106-236](), [app/shared/req_res.go:320-325]()

### RejectAllChangesHandler Function

**Endpoint:** `PATCH /plans/{planId}/{branch}/reject_all`  
**Handler:** `RejectAllChangesHandler(w http.ResponseWriter, r *http.Request)`

Rejects all pending changes in the plan. Calls `db.RejectAllResults()` and commits the rejection.

Sources: [app/server/handlers/plans_changes.go:238-287]()

### RejectFileHandler and RejectFilesHandler Functions

**Endpoints:** 
- `PATCH /plans/{planId}/{branch}/reject_file` 
- `PATCH /plans/{planId}/{branch}/reject_files`

**Handlers:** `RejectFileHandler` and `RejectFilesHandler`

Reject changes to specific files. Process `shared.RejectFileRequest` and `shared.RejectFilesRequest` respectively.

Sources: [app/server/handlers/plans_changes.go:289-417]()

### Reject Changes

**Endpoints:** 
- `PATCH /plans/{planId}/{branch}/reject_all`
- `PATCH /plans/{planId}/{branch}/reject_file`
- `PATCH /plans/{planId}/{branch}/reject_files`

Reject pending changes, either all changes or changes to specific files.

**Implementation Details:**
Execute repository operations to reject the specified changes and commit the rejection to the repository.

Sources: [app/server/handlers/plans_changes.go:238-417]()

### Get Plan Diffs

**Endpoint:** `GET /plans/{planId}/{branch}/diffs`

Retrieves diffs for pending changes.

Sources: [app/server/handlers/plans_changes.go:509-566]()

## Branch Management Endpoints

These endpoints manage Git branches for plans, allowing parallel work streams.

### List Branches

**Endpoint:** `GET /plans/{planId}/branches`

Lists all branches for a plan.

Sources: [app/server/handlers/branches.go:18-78]()

### Create Branch

**Endpoint:** `POST /plans/{planId}/{branch}/branches`

Creates a new branch from an existing branch.

Sources: [app/server/handlers/branches.go:80-158]()

### Delete Branch

**Endpoint:** `DELETE /plans/{planId}/branches/{branch}`

Deletes a branch.

Sources: [app/server/handlers/branches.go:160-207]()

## Request and Response Data Structures

The API handlers work with strongly-typed request and response structures defined in `shared/req_res.go` and `shared/data_models.go`.

### Core Request Types

| Handler Function | Request Type | Key Fields |
|------------------|--------------|------------|
| `TellPlanHandler` | `TellPlanRequest` | `Prompt`, `ApiKeys`, `ConnectStream`, `AutoContext` |
| `BuildPlanHandler` | `BuildPlanRequest` | `ApiKeys`, `ConnectStream`, `SessionId` |
| `LoadContextHandler` | `LoadContextRequest` | Array of `LoadContextParams` |
| `ApplyPlanHandler` | `ApplyPlanRequest` | `ApiKeys`, `SessionId` |
| `CreateBranchHandler` | `CreateBranchRequest` | `Name` |

### Core Response Types

| Handler Function | Response Type | Key Fields |
|------------------|---------------|------------|
| `LoadContextHandler` | `LoadContextResponse` | `TokensAdded`, `TotalTokens`, `MaxTokensExceeded` |
| `ListContextHandler` | `[]*shared.Context` | Array of context objects |
| `ApplyPlanHandler` | `string` | Generated commit message |
| `GetBuildStatusHandler` | `GetBuildStatusResponse` | `BuiltFiles`, `IsBuildingByPath` |

### Context Type System

Context types are defined as `shared.ContextType` constants:
- `ContextFileType` - Individual files
- `ContextURLType` - Web URLs  
- `ContextNoteType` - User notes
- `ContextDirectoryTreeType` - Directory structures
- `ContextPipedDataType` - Piped input data
- `ContextImageType` - Image files
- `ContextMapType` - File maps containing multiple files

Sources: [app/shared/req_res.go:120-372](), [app/shared/data_models.go:83-93](), [app/server/handlers/plans_exec.go:54-60]()

## Streaming Response Implementation

Several handlers support streaming responses using Server-Sent Events (SSE) for real-time updates during plan execution.

### startResponseStream Function

Handlers that support streaming call `startResponseStream(r.Context(), w, auth, planId, branch, isConnect)` to establish the streaming connection. This function:

1. Sets appropriate HTTP headers for SSE
2. Subscribes to the active plan's stream  
3. Forwards `shared.StreamMessage` events to the client
4. Handles stream abortion and cleanup

### Streaming-Enabled Handlers

| Handler | Stream Trigger | Purpose |
|---------|----------------|---------|
| `TellPlanHandler` | `req.ConnectStream = true` | Real-time planning updates |
| `BuildPlanHandler` | `req.ConnectStream = true` | Code generation progress |
| `ConnectPlanHandler` | Always streams | Connect to existing active plan |

```mermaid
sequenceDiagram
    participant CLI as "Plandex CLI"
    participant Handler as "Handler Function"
    participant Stream as "startResponseStream()"
    participant ActivePlan as "types.ActivePlan"
    participant ModelPlan as "AI Model Execution"
    
    CLI->>Handler: Request with ConnectStream=true
    Handler->>ModelPlan: Start execution (Tell/Build)
    Handler->>Stream: startResponseStream(ctx, w, auth, planId, branch)
    Stream->>Stream: Set SSE headers
    Stream->>ActivePlan: Subscribe to stream
    
    loop AI Processing
        ModelPlan->>ActivePlan: Send progress updates
        ActivePlan->>Stream: Forward StreamMessage
        Stream-->>CLI: Server-Sent Event
    end
    
    alt User Stops Plan
        CLI->>Handler: StopPlanHandler request
        Handler->>ActivePlan: Send abort signal
        ActivePlan->>Stream: StreamMessageAborted
        Stream-->>CLI: Abort notification
        Stream->>Stream: Close connection
    end
```

Sources: [app/server/handlers/plans_exec.go:94-95](), [app/server/handlers/plans_exec.go:165-167](), [app/server/handlers/plans_exec.go:209]()

## Error Handling Patterns

Request handlers implement consistent error handling patterns with logging, appropriate HTTP status codes, and error response formatting.

### Common Error Handling Functions

**HTTP Error Responses:**
```go
http.Error(w, "Error message", http.StatusCode)
```

**API Error Structure:**
Handlers can return structured errors using `shared.ApiError` with fields for error type, status code, and message.

### Error Scenarios by Handler Type

| Error Type | Status Code | Example Handlers | Trigger Conditions |
|------------|-------------|------------------|-------------------|
| Authentication Failed | 401 | All handlers | `Authenticate()` returns nil |
| Authorization Failed | 403 | `authorizePlanExecUpdate` | User lacks plan update permission |
| Invalid Request Body | 400 | `TellPlanHandler`, `LoadContextHandler` | `json.Unmarshal()` fails |
| Plan Not Found | 404 | `authorizePlan` calls | Plan doesn't exist or access denied |
| Context Limits Exceeded | 400 | `LoadContextHandler` | Exceeds `MaxContextCount` or `MaxContextBodySize` |
| Repository Operation Failed | 500 | `ExecRepoOperation` calls | Git operations fail |
| Internal Server Error | 500 | All handlers | Unexpected runtime errors |

### Error Logging Pattern

Handlers consistently log errors with context:
```go
log.Printf("Error description: %v\n", err)
http.Error(w, "Error description: "+err.Error(), http.StatusInternalServerError)
```

Sources: [app/server/handlers/plans_exec.go:43-59](), [app/server/handlers/plans_exec.go:151-162](), [app/server/handlers/context_helper.go:54-81]()

## Health and Monitoring Endpoints

The server provides endpoints for health monitoring:

| Endpoint | Description |
|----------|-------------|
| `/health` | Basic health check - returns "OK" if server is running |
| `/version` | Returns the server version information |

Sources: [app/server/routes/routes.go:30-71]()

## API Authentication Flow

```mermaid
graph TD
    subgraph "Authentication Process"
        Request["Incoming Request"] --> AuthHeader["Extract Auth Header/Cookie"]
        AuthHeader --> ValidateToken["Validate Token"]
        ValidateToken --> LoadUser["Load User Info"]
        LoadUser --> CheckPermissions["Check Permissions"]
        CheckPermissions --> Allow["Allow Request"]
        CheckPermissions -- "Insufficient Permissions" --> Reject["Reject with 403"]
        ValidateToken -- "Invalid Token" --> Reject
    end
```

Sources: [app/server/handlers/plans_exec.go:558-571](), [app/server/handlers/sessions.go:211-250]()

## Conclusion

The Plandex API provides a comprehensive set of endpoints for interacting with the Plandex system. This document has outlined the key endpoints, their functionality, and implementation details. Clients like the Plandex CLI use these endpoints to manage plans, contexts, branches, and execute AI-powered coding operations.

---

# Page: Data Models and Shared Types

# Data Models and Shared Types

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/cli/api/methods.go](app/cli/api/methods.go)
- [app/cli/types/api.go](app/cli/types/api.go)
- [app/server/db/data_models.go](app/server/db/data_models.go)
- [app/shared/data_models.go](app/shared/data_models.go)
- [app/shared/req_res.go](app/shared/req_res.go)

</details>



This document covers the core data structures and type definitions used throughout the Plandex system. These models define the fundamental entities for organizations, plans, contexts, conversations, and file modifications that flow between the CLI client and server components.

For information about how these models are used in API communication, see [HTTP API and Request Handlers](#4.1). For details about the plan execution engine that processes these models, see [Plan Execution Engine](#4.3).

## Core Entity Models

The Plandex system is built around several fundamental entities that represent organizations, plans, and their associated data. These models are defined in the shared package and used consistently across client and server components.

### Organization and User Models

The system supports multi-tenant organizations with role-based access control:

```mermaid
erDiagram
    Org ||--o{ User : "contains"
    Org ||--o{ OrgUser : "has"
    User ||--o{ OrgUser : "belongs to"
    Org ||--o{ Project : "owns"
    User ||--o{ Plan : "creates"
    OrgRole ||--o{ OrgUser : "assigned to"
    
    Org {
        string Id
        string Name
        bool IsTrial
        bool AutoAddDomainUsers
        CloudBillingFields CloudBillingFields
    }
    
    User {
        string Id
        string Name
        string Email
        bool IsTrial
        int NumNonDraftPlans
        PlanConfig DefaultPlanConfig
    }
    
    OrgUser {
        string OrgId
        string UserId
        string OrgRoleId
    }
    
    OrgRole {
        string Id
        bool IsDefault
        string Label
        string Description
    }
```

**Sources:** [app/shared/data_models.go:10-66](), [app/server/db/data_models.go:24-109]()

### Project and Plan Hierarchy

Projects contain plans, which contain branches for different development paths:

```mermaid
erDiagram
    Project ||--o{ Plan : "contains"
    Plan ||--o{ Branch : "has"
    Branch ||--o{ Context : "uses"
    Branch ||--o{ ConvoMessage : "tracks"
    
    Project {
        string Id
        string Name
    }
    
    Plan {
        string Id
        string OwnerId
        string ProjectId
        string Name
        time SharedWithOrgAt
        int TotalReplies
        int ActiveBranches
        PlanConfig PlanConfig
        time ArchivedAt
    }
    
    Branch {
        string Id
        string PlanId
        string OwnerId
        string ParentBranchId
        string Name
        PlanStatus Status
        int ContextTokens
        int ConvoTokens
        time SharedWithOrgAt
        time ArchivedAt
    }
```

**Sources:** [app/shared/data_models.go:49-81](), [app/server/db/data_models.go:111-190]()

## Context and Content Models

Context represents the various types of input data that can be loaded into a plan, including files, URLs, notes, and images.

### Context Type Hierarchy

```mermaid
graph TD
    Context["Context"] --> ContextFileType["file"]
    Context --> ContextURLType["url"] 
    Context --> ContextNoteType["note"]
    Context --> ContextDirectoryTreeType["directory tree"]
    Context --> ContextPipedDataType["piped data"]
    Context --> ContextImageType["image"]
    Context --> ContextMapType["map"]
    
    ContextFileType --> FileMapBodies["FileMapBodies"]
    ContextMapType --> FileMapBodies
    ContextImageType --> ImageURLDetail["ImageURLDetail"]
```

The `Context` struct supports multiple content types through a flexible design:

- **File contexts** contain source code or text files
- **URL contexts** fetch and store web content  
- **Note contexts** store user-provided text
- **Image contexts** include visual content for AI analysis
- **Map contexts** represent directory structures with file mappings

**Sources:** [app/shared/data_models.go:83-117](), [app/server/db/data_models.go:387-460]()

### Context Loading and Management

```mermaid
sequenceDiagram
    participant CLI as "CLI Client"
    participant Handler as "LoadContextHandler"
    participant Helper as "loadContexts"
    participant DB as "db.LoadContexts"
    
    CLI->>Handler: LoadContextRequest
    Handler->>Helper: loadContextsParams
    Helper->>Helper: Validate file limits
    Helper->>Helper: Generate names for piped data/notes
    Helper->>DB: LoadContextsParams
    DB->>DB: Process contexts by type
    DB->>Handler: LoadContextResponse
    Handler->>CLI: Context metadata + tokens
```

**Sources:** [app/server/handlers/context_helper.go:29-280](), [app/server/handlers/plans_context.go:154-212]()

## Plan Execution Models

Plan execution involves conversation messages, file results, and build tracking that represent the AI's work on a plan.

### Conversation and Message Flow

```mermaid
erDiagram
    ConvoMessage ||--o{ ConvoMessageDescription : "describes"
    ConvoMessage ||--o{ Subtask : "tracks"
    ConvoMessage ||--o{ PlanFileResult : "generates" 
    PlanFileResult ||--o{ Replacement : "contains"
    
    ConvoMessage {
        string Id
        string UserId
        string Role
        int Tokens
        int Num
        string Message
        bool Stopped
        ConvoMessageFlags Flags
        Subtask Subtask
        Subtask[] AddedSubtasks
        string[] RemovedSubtasks
        string[] ActiveContextIds
    }
    
    ConvoMessageFlags {
        bool DidMakePlan
        bool DidRemoveTasks
        bool DidLoadContext
        bool IsChat
        bool DidWriteCode
        bool DidCompleteTask
        bool HasError
        CurrentStage CurrentStage
    }
    
    PlanFileResult {
        string Id
        string ConvoMessageId
        string Path
        string Content
        bool AnyFailed
        time AppliedAt
        time RejectedAt
        Replacement[] Replacements
        bool RemovedFile
    }
```

**Sources:** [app/shared/data_models.go:138-267](), [app/server/db/data_models.go:462-581]()

### Plan State Management

The `CurrentPlanState` aggregates all plan data for client consumption:

```mermaid
graph LR
    CurrentPlanState["CurrentPlanState"] --> PlanResult["PlanResult"]
    CurrentPlanState --> CurrentPlanFiles["CurrentPlanFiles"] 
    CurrentPlanState --> ConvoMessageDescriptions["ConvoMessageDescription[]"]
    CurrentPlanState --> PlanApplies["PlanApply[]"]
    CurrentPlanState --> ContextsByPath["map[string]*Context"]
    
    PlanResult --> FileResultsByPath["PlanFileResultsByPath"]
    PlanResult --> ReplacementsByPath["map[string][]*Replacement"]
    
    CurrentPlanFiles --> Files["map[string]string"]
    CurrentPlanFiles --> Removed["map[string]bool"]
    CurrentPlanFiles --> UpdatedAtByPath["map[string]time.Time"]
```

**Sources:** [app/shared/data_models.go:269-299](), [app/server/handlers/plans_changes.go:19-104]()

## Request and Response Models

The system uses structured request/response models for all API communication, providing type safety and validation.

### Plan Execution Requests

```mermaid
classDiagram
    class TellPlanRequest {
        +string Prompt
        +BuildMode BuildMode
        +bool ConnectStream
        +bool AutoContinue
        +bool IsUserContinue
        +bool AutoContext
        +bool SmartContext
        +map[string]string ApiKeys
        +map[string]bool ProjectPaths
        +string SessionId
    }
    
    class BuildPlanRequest {
        +bool ConnectStream
        +map[string]string ApiKeys
        +map[string]bool ProjectPaths
        +string SessionId
    }
    
    class LoadContextRequest {
        +LoadContextParams[] params
    }
    
    class LoadContextParams {
        +ContextType ContextType
        +string Name
        +string FilePath
        +string Body
        +bool ForceSkipIgnore
        +FileMapBodies MapBodies
    }
```

**Sources:** [app/shared/req_res.go:120-207](), [app/server/handlers/plans_exec.go:54-84]()

### Response Models

Response models provide structured feedback and streaming capabilities:

```mermaid
classDiagram
    class LoadContextResponse {
        +int TokensAdded
        +int TotalTokens
        +bool MaxTokensExceeded
        +int MaxTokens
        +string Msg
    }
    
    class GetBuildStatusResponse {
        +map[string]bool BuiltFiles
        +map[string]bool IsBuildingByPath
    }
    
    class ListPlansRunningResponse {
        +Branch[] Branches
        +map[string]time StreamStartedAtByBranchId
        +map[string]time StreamFinishedAtByBranchId
        +map[string]*Plan PlansById
    }
```

**Sources:** [app/shared/req_res.go:209-334](), [app/cli/api/methods.go:267-301]()

## Model Conversion Patterns

The system maintains separation between server-side database models and client-facing API models through consistent conversion patterns.

### ToApi() Conversion Pattern

```mermaid
sequenceDiagram
    participant Server as "Server DB Model"
    participant Conversion as "ToApi() Method"
    participant Client as "Shared API Model"
    participant JSON as "JSON Response"
    
    Server->>Conversion: Database record
    Conversion->>Conversion: Filter server-only fields
    Conversion->>Client: Create shared model
    Client->>JSON: Marshal to client
    
    note over Conversion: Ensures server data doesn't leak
    note over Client: Safe for client consumption
```

Database models include `ToApi()` methods that convert server-side data to client-safe shared models:

```go
// Server-side model (db package)
type Plan struct {
    Id       string
    OrgId    string  // Server-only
    OwnerId  string
    Name     string
    // ... other fields
}

// Conversion method
func (plan *Plan) ToApi() *shared.Plan {
    return &shared.Plan{
        Id:      plan.Id,
        OwnerId: plan.OwnerId,
        Name:    plan.Name,
        // OrgId omitted - server-only
    }
}
```

**Sources:** [app/server/db/data_models.go:141-155](), [app/server/handlers/plans_context.go:63-67]()

### Data Flow Architecture

```mermaid
graph TB
    subgraph "Client Side"
        CLICommands["CLI Commands"] --> APIClient["API Client"]
        APIClient --> SharedModels["Shared Models"]
    end
    
    subgraph "Network Layer"
        HTTPRequests["HTTP Requests/Responses"]
    end
    
    subgraph "Server Side"
        HTTPHandlers["HTTP Handlers"] --> ServerModels["Server DB Models"]
        ServerModels --> ToApiMethods["ToApi() Methods"]
        ToApiMethods --> SharedModelsServer["Shared Models"]
        ServerModels --> Database[("PostgreSQL Database")]
        ServerModels --> GitRepo[("Git Repository")]
    end
    
    APIClient <--> HTTPRequests
    HTTPRequests <--> HTTPHandlers
    SharedModels -.-> SharedModelsServer
    
    style SharedModels fill:#e1f5fe
    style SharedModelsServer fill:#e1f5fe
    style ToApiMethods fill:#f3e5f5
```

This architecture ensures:
- **Type safety** across client-server boundaries
- **Data isolation** preventing server internals from leaking to clients
- **Consistent interfaces** through shared model definitions
- **Validation** at API boundaries through structured types

**Sources:** [app/cli/api/methods.go:75-133](), [app/server/handlers/plans_exec.go:23-98](), [app/server/db/data_models.go:11-15]()

---

# Page: Active Plan Management

# Active Plan Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/cli/stream_tui/model.go](app/cli/stream_tui/model.go)
- [app/cli/stream_tui/run.go](app/cli/stream_tui/run.go)
- [app/cli/stream_tui/update.go](app/cli/stream_tui/update.go)
- [app/cli/stream_tui/view.go](app/cli/stream_tui/view.go)
- [app/server/model/plan/tell_exec.go](app/server/model/plan/tell_exec.go)
- [app/server/model/plan/tell_load.go](app/server/model/plan/tell_load.go)
- [app/server/model/plan/tell_state.go](app/server/model/plan/tell_state.go)
- [app/server/model/plan/tell_stream_finish.go](app/server/model/plan/tell_stream_finish.go)
- [app/server/model/plan/tell_stream_main.go](app/server/model/plan/tell_stream_main.go)
- [app/server/model/plan/tell_stream_processor.go](app/server/model/plan/tell_stream_processor.go)
- [app/server/model/plan/tell_summary.go](app/server/model/plan/tell_summary.go)
- [app/server/types/active_plan.go](app/server/types/active_plan.go)

</details>



This document covers the server-side management of active plans in Plandex, including real-time streaming, state management, and coordination between AI model execution and client interactions. For information about plan data storage and persistence, see [Database Schema and Migrations](#6.1). For details about AI model integration during plan execution, see [AI Model Integration and Task Control](#3.2).

## Core ActivePlan Structure

The `ActivePlan` struct serves as the central coordinator for all real-time plan operations, managing streaming, state, and communication between server components and connected clients.

```mermaid
graph TB
    subgraph "ActivePlan Core State"
        AP["ActivePlan"]
        AP --> ID["Id, UserId, OrgId"]
        AP --> Branch["Branch"]
        AP --> Prompt["Prompt, BuildOnly"]
        AP --> Session["SessionId"]
    end
    
    subgraph "Context Management"
        AP --> Ctx["Ctx (context.Context)"]
        AP --> CancelFn["CancelFn"]
        AP --> ModelStreamCtx["ModelStreamCtx"]
        AP --> CancelModelStreamFn["CancelModelStreamFn"]
        AP --> SummaryCtx["SummaryCtx"]
        AP --> SummaryCancelFn["SummaryCancelFn"]
    end
    
    subgraph "Streaming Infrastructure"
        AP --> StreamDoneCh["StreamDoneCh"]
        AP --> CurrentStreamingReplyId["CurrentStreamingReplyId"]
        AP --> CurrentReplyDoneCh["CurrentReplyDoneCh"]
        AP --> ModelStreamId["ModelStreamId"]
        AP --> streamCh["streamCh"]
        AP --> subscriptions["subscriptions map"]
    end
    
    subgraph "Content and State"
        AP --> Contexts["Contexts []*db.Context"]
        AP --> ContextsByPath["ContextsByPath map"]
        AP --> Operations["Operations []*shared.Operation"]
        AP --> CurrentReplyContent["CurrentReplyContent"]
        AP --> NumTokens["NumTokens"]
        AP --> MessageNum["MessageNum"]
    end
    
    subgraph "Build Management"
        AP --> BuildQueuesByPath["BuildQueuesByPath"]
        AP --> BuiltFiles["BuiltFiles map"]
        AP --> IsBuildingByPath["IsBuildingByPath map"]
        AP --> RepliesFinished["RepliesFinished"]
    end
```

The `ActivePlan` includes multiple context hierarchies to enable granular cancellation control. The main context manages the overall plan lifecycle, while separate contexts handle model streaming and background summarization tasks.

Sources: [app/server/types/active_plan.go:48-93]()

## Plan Lifecycle and State Management

Active plans follow a structured lifecycle from creation through completion, with specific state transitions and cleanup procedures.

```mermaid
stateDiagram-v2
    [*] --> Created: "NewActivePlan()"
    Created --> Activating: "activatePlan()"
    Activating --> Executing: "execTellPlan()"
    
    state Executing {
        [*] --> Loading: "loadTellPlan()"
        Loading --> Replying: "SetPlanStatus(Replying)"
        Replying --> Describing: "SetPlanStatus(Describing)"
        Describing --> Building: "Build operations"
        Building --> Summarizing: "Background summary"
        Summarizing --> CheckingContinue: "willContinuePlan()"
        CheckingContinue --> Loading: "Auto-continue"
        CheckingContinue --> Finished: "No continuation"
    }
    
    Executing --> MissingFile: "File not in context"
    MissingFile --> Executing: "User response"
    
    Executing --> Error: "Stream error"
    Error --> Retrying: "Fallback available"
    Retrying --> Executing
    Error --> Failed: "No fallback"
    
    Executing --> Cancelled: "User stop/timeout"
    
    Finished --> [*]: "Cleanup"
    Failed --> [*]: "Cleanup"
    Cancelled --> [*]: "Cleanup"
```

The plan execution flow is managed primarily through the `execTellPlan` function, which coordinates between different execution phases and handles state transitions.

Sources: [app/server/model/plan/tell_exec.go:86-492](), [app/server/model/plan/tell_stream_finish.go:25-277]()

## Streaming and Subscription System

Active plans implement a sophisticated streaming system that allows multiple clients to subscribe to real-time updates with automatic buffering and rate limiting.

```mermaid
graph TB
    subgraph "Subscription Management"
        ActivePlan --> subscriptionMu["subscriptionMu (sync.Mutex)"]
        ActivePlan --> subscriptions["subscriptions map[string]*subscription"]
        
        subscription --> ch["ch (chan string)"]
        subscription --> ctx["ctx (context.Context)"]
        subscription --> cancelFn["cancelFn"]
        subscription --> messageQueue["messageQueue []string"]
        subscription --> cond["cond (*sync.Cond)"]
    end
    
    subgraph "Stream Processing"
        ActivePlan --> streamCh["streamCh (chan string)"]
        ActivePlan --> streamMu["streamMu (sync.Mutex)"]
        ActivePlan --> lastStreamMessageSent["lastStreamMessageSent"]
        ActivePlan --> streamMessageBuffer["streamMessageBuffer"]
        
        streamCh --> StreamManager["Stream Manager Goroutine"]
        StreamManager --> DistributeToSubs["Distribute to Subscriptions"]
    end
    
    subgraph "Rate Limiting"
        Stream["Stream()"] --> CheckRate["Check MaxStreamRate"]
        CheckRate --> Buffer["Buffer if too frequent"]
        CheckRate --> DirectSend["Send directly"]
        Buffer --> FlushBuffer["FlushStreamBuffer()"]
        FlushBuffer --> MultiMessage["StreamMessageMulti"]
    end
```

The streaming system includes automatic message buffering when updates arrive faster than the configured `MaxStreamRate` (70ms), combining multiple messages into `StreamMessageMulti` batches to reduce client-side processing overhead.

Sources: [app/server/types/active_plan.go:186-311](), [app/server/types/active_plan.go:339-378](), [app/server/types/active_plan.go:390-436]()

## Plan Execution Flow

The plan execution system coordinates AI model interactions, file operations, and client communication through a multi-phase process.

```mermaid
sequenceDiagram
    participant Client
    participant TellHandler as "Tell Handler"
    participant ExecTell as "execTellPlan"
    participant LoadPlan as "loadTellPlan"
    participant StreamState as "activeTellStreamState"
    participant ModelClient as "Model Client"
    participant BuildSystem as "Build System"
    
    Client->>TellHandler: "TellPlanRequest"
    TellHandler->>ExecTell: "activatePlan() + go execTellPlan()"
    
    ExecTell->>LoadPlan: "loadTellPlan()"
    LoadPlan-->>ExecTell: "contexts, convo, summaries, subtasks"
    
    ExecTell->>StreamState: "Setup state + messages"
    StreamState->>ModelClient: "CreateChatCompletionStream"
    ModelClient-->>StreamState: "Stream chunks"
    
    loop "Stream Processing"
        StreamState->>StreamState: "processChunk()"
        StreamState->>Client: "StreamMessage (reply)"
        StreamState->>BuildSystem: "queueBuilds() for operations"
    end
    
    StreamState->>StreamState: "handleStreamFinished()"
    StreamState->>StreamState: "checkAutoLoadContext()"
    StreamState->>StreamState: "willContinuePlan()"
    
    alt "Continue Plan"
        StreamState->>ExecTell: "execTellPlan() iteration+1"
    else "Finish Plan"
        StreamState->>Client: "StreamMessageFinished"
    end
```

The execution flow includes automatic continuation logic that determines whether to proceed with additional iterations based on unfinished subtasks, new context, or explicit task additions.

Sources: [app/server/model/plan/tell_exec.go:86-492](), [app/server/model/plan/tell_load.go:20-427](), [app/server/model/plan/tell_stream_main.go:20-284]()

## Build Management System

Active plans manage file building operations through queued builds that process AI-generated operations into actual file modifications.

```mermaid
graph TB
    subgraph "Build Queue Management"
        ActivePlan --> BuildQueuesByPath["BuildQueuesByPath map[string][]*ActiveBuild"]
        ActivePlan --> IsBuildingByPath["IsBuildingByPath map[string]bool"]
        ActivePlan --> BuiltFiles["BuiltFiles map[string]bool"]
        
        ActiveBuild --> ReplyId["ReplyId"]
        ActiveBuild --> FileDescription["FileDescription"]
        ActiveBuild --> FileContent["FileContent"]
        ActiveBuild --> Path["Path"]
        ActiveBuild --> Success["Success"]
        ActiveBuild --> Error["Error"]
        ActiveBuild --> IsMoveOp["IsMoveOp, IsRemoveOp, IsResetOp"]
    end
    
    subgraph "Build Processing"
        Operations["shared.Operation"] --> QueueBuild["queueBuilds()"]
        QueueBuild --> ActiveBuild
        
        BuildSystem["Build System"] --> ProcessBuild["Process ActiveBuild"]
        ProcessBuild --> ValidationSyntax["Syntax Validation"]
        ValidationSyntax --> FileSystem["Write to FileSystem"]
        FileSystem --> UpdateStatus["Update build status"]
    end
    
    subgraph "Status Tracking"
        BuildFinished["BuildFinished()"] --> CheckAllPaths["Check all paths"]
        CheckAllPaths --> PathQueueEmpty["PathQueueEmpty()"]
        PathQueueEmpty --> BuildComplete["All builds complete"]
    end
```

The build system processes operations concurrently per file path while maintaining ordering within each path's queue. Build status is tracked both server-side and communicated to clients via streaming updates.

Sources: [app/server/types/active_plan.go:24-37](), [app/server/types/active_plan.go:317-337](), [app/server/model/plan/tell_stream_processor.go:522-593]()

## Integration with Model Streaming

Active plans coordinate closely with AI model streaming, handling real-time content processing, error recovery, and context management.

```mermaid
graph TB
    subgraph "Model Integration"
        activeTellStreamState --> modelStreamId["modelStreamId"]
        activeTellStreamState --> clients["clients map[string]ClientInfo"]
        activeTellStreamState --> modelConfig["modelConfig *ModelRoleConfig"]
        activeTellStreamState --> baseModelConfig["baseModelConfig *BaseModelConfig"]
        activeTellStreamState --> fallbackRes["fallbackRes FallbackResult"]
    end
    
    subgraph "Stream Processing"
        activeTellStreamState --> messages["messages []ExtendedChatMessage"]
        activeTellStreamState --> replyParser["replyParser *ReplyParser"]
        activeTellStreamState --> chunkProcessor["chunkProcessor *chunkProcessor"]
        
        chunkProcessor --> replyOperations["replyOperations []*Operation"]
        chunkProcessor --> fileOpen["fileOpen bool"]
        chunkProcessor --> contentBuffer["contentBuffer string"]
        chunkProcessor --> awaitingBlockOpeningTag["awaitingBlockOpeningTag"]
        chunkProcessor --> awaitingBlockClosingTag["awaitingBlockClosingTag"]
    end
    
    subgraph "Error Handling"
        activeTellStreamState --> numErrorRetry["numErrorRetry int"]
        activeTellStreamState --> numFallbackRetry["numFallbackRetry int"]
        activeTellStreamState --> modelErr["modelErr *ModelError"]
        activeTellStreamState --> didProviderFallback["didProviderFallback bool"]
    end
    
    subgraph "Context Management"
        activeTellStreamState --> currentStage["currentStage CurrentStage"]
        activeTellStreamState --> subtasks["subtasks []*Subtask"]
        activeTellStreamState --> currentSubtask["currentSubtask *Subtask"]
        activeTellStreamState --> settings["settings *PlanSettings"]
    end
```

The integration includes sophisticated chunk processing that handles AI model output formatting, operation parsing, and real-time streaming to clients while maintaining context awareness and error recovery capabilities.

Sources: [app/server/model/plan/tell_state.go:14-82](), [app/server/model/plan/tell_stream_processor.go:29-156](), [app/server/model/plan/tell_stream_main.go:20-284]()

---

# Page: AI Model Integration

# AI Model Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/cli/lib/model_credentials.go](app/cli/lib/model_credentials.go)
- [app/server/model/client.go](app/server/model/client.go)
- [app/server/model/client_stream.go](app/server/model/client_stream.go)
- [app/server/model/model_error.go](app/server/model/model_error.go)
- [app/server/model/plan/tell_stream_error.go](app/server/model/plan/tell_stream_error.go)
- [app/server/types/message.go](app/server/types/message.go)
- [app/shared/ai_models_available.go](app/shared/ai_models_available.go)
- [app/shared/ai_models_data_models.go](app/shared/ai_models_data_models.go)
- [app/shared/ai_models_errors.go](app/shared/ai_models_errors.go)
- [app/shared/ai_models_packs.go](app/shared/ai_models_packs.go)
- [app/shared/ai_models_providers.go](app/shared/ai_models_providers.go)
- [test/smoke_test.sh](test/smoke_test.sh)
- [test/test_utils.sh](test/test_utils.sh)

</details>



This document provides a technical overview of how Plandex integrates with AI models to enable its core code generation, planning, and task execution capabilities. It covers the client initialization process, request handling, response streaming, error management, context formation, and model role configuration. This system forms the bridge between the Plandex application and the external AI providers that power its intelligent coding features.

For information about specific model configurations and model packs, see [Model Configuration](#5.1). For details on context and token management strategies, see [Context and Token Management](#5.2).

## Architecture Overview

The AI model integration in Plandex consists of several interrelated components that work together to enable communication with various AI model providers and optimize the interaction for different scenarios.

```mermaid
flowchart TD
    subgraph "Plandex Server"
        ModelClient["ModelClient"]
        ModelConfig["shared.ModelRoleConfig"]
        StreamManager["ExtendedChatCompletionStream"]
        ContextFormatter["formatModelContext()"]
        ErrorHandler["withRetries()"]
        TokenManager["GetMessagesTokenEstimate()"]
    end
    
    subgraph "External AI Providers"
        OpenAI["OpenAI API"]
        Anthropic["Anthropic API"]
        Google["Google API"]
        OpenRouter["OpenRouter.ai API"]
        Together["Together.ai API"]
    end
    
    ModelClient --> |"API Requests"|OpenAI
    ModelClient --> |"API Requests"|Anthropic
    ModelClient --> |"API Requests"|Google
    ModelClient --> |"API Requests"|OpenRouter
    ModelClient --> |"API Requests"|Together
    
    ModelConfig --> ModelClient
    ModelClient --> StreamManager
    ContextFormatter --> ModelClient
    TokenManager --> ContextFormatter
    ErrorHandler --> ModelClient
```

Sources: `app/server/model/client.go`, `app/server/model/plan/tell_context.go`, `README.md`

## Supported AI Model Providers

Plandex supports multiple AI model providers, allowing users to leverage different models based on their capabilities, cost, and availability:

| Provider | Description | Environment Variable |
|----------|-------------|---------------------|
| OpenAI | Providers of GPT models | `OPENAI_API_KEY` |
| Anthropic | Providers of Claude models | `ANTHROPIC_API_KEY` |
| Google | Providers of Gemini models | `GOOGLE_API_KEY` |
| OpenRouter.ai | Gateway to multiple models | `OPENROUTER_API_KEY` |
| Together.ai | Providers of open-source models | `TOGETHER_API_KEY` |

### Client Initialization Process

The client initialization process establishes connections to the various AI providers using API keys and configuring appropriate endpoints:

```mermaid
sequenceDiagram
    participant Server as "Plandex Server"
    participant InitClients as "InitClients()"
    participant ClientInfo as "ClientInfo struct"
    participant Provider as "AI Provider APIs"
    
    Server->>InitClients: Call with apiKeys, endpoints, openAIEndpoint, orgId
    loop For Each API Key
        InitClients->>ClientInfo: newClient(apiKey, endpoint, orgId)
        Note over ClientInfo: Configure client with proper<br>authentication and endpoint
        ClientInfo->>Provider: Initialize connection
    end
    InitClients->>Server: Return map of configured clients
```

Sources: `app/server/model/client.go:42-56`, `app/server/model/client.go:58-73`

## Client Configuration

Each AI provider requires specific configuration, which is handled through the `ClientInfo` struct and the initialization process:

```go
type ClientInfo struct {
    Client   *openai.Client
    ApiKey   string
    OrgId    string
    Endpoint string
}
```

Configuration options include:
- **Custom Endpoints**: Set via the `OPENAI_ENDPOINT` environment variable
- **Organization ID**: For OpenAI multi-org accounts via `OPENAI_ORG_ID`
- **Provider-specific Headers**: Such as OpenRouter's region and preference settings

Sources: `app/server/model/client.go:35-40`, `releases/server/versions/0.8.3.md:2-4`

## Request Processing Flow

The system uses a robust request processing flow to communicate with AI models:

```mermaid
flowchart TD
    Start["ModelRequest()"]
    Filter["FilterEmptyMessages()"]
    Estimate["GetMessagesTokenEstimate()"]
    SelectModel["modelConfig.GetRoleForInputTokens()"]
    CreateReq["Create ExtendedChatCompletionRequest"]
    ExecHook["Execute WillSendModelRequest hook"]
    SendReq["CreateChatCompletionWithInternalStream()"]
    Process["Process model response"]
    TrackUsage["Track token usage with DidSendModelRequest hook"]
    End["Return ModelResponse"]
    
    Start --> Filter
    Filter --> Estimate
    Estimate --> SelectModel
    SelectModel --> CreateReq
    CreateReq --> ExecHook
    ExecHook --> SendReq
    SendReq --> Process
    Process --> TrackUsage
    TrackUsage --> End
```

Sources: `app/server/model/model_request.go:45-187`, `app/server/model/model_request.go:189-206`

## Message Formatting

Plandex extends the standard OpenAI message format to accommodate additional features:

```mermaid
classDiagram
    class ExtendedChatMessage {
        +Role string
        +Content []ExtendedChatMessagePart
        +ToOpenAI() *openai.ChatCompletionMessage
    }
    
    class ExtendedChatMessagePart {
        +Type string
        +Text string
        +ImageURL *openai.ChatMessageImageURL
        +CacheControl *CacheControlSpec
    }
    
    class ExtendedChatCompletionRequest {
        +Model shared.ModelName
        +Messages []ExtendedChatMessage
        +Temperature float32
        +TopP float32
        +Stop []string
        +Tools []openai.Tool
        +ToolChoice any
        +Prediction *OpenAIPrediction
        +Provider *OpenRouterProviderConfig
        +IncludeReasoning bool
        +ToOpenAI() *ExtendedOpenAIChatCompletionRequest
    }
    
    ExtendedChatMessage --> ExtendedChatMessagePart: Contains
    ExtendedChatCompletionRequest --> ExtendedChatMessage: Contains
```

Sources: `app/server/types/message.go:22-32`, `app/server/types/message.go:34-57`, `app/server/types/message.go:69-124`

## Streaming Response Handling

Streaming is a critical feature for providing real-time feedback during code generation. The system implements a sophisticated streaming mechanism:

```mermaid
sequenceDiagram
    participant Client as "Plandex Client"
    participant Server as "Plandex Server"
    participant streamState as "activeTellStreamState"
    participant streamManager as "ExtendedChatCompletionStream"
    participant Provider as "AI Provider API"
    
    Client->>Server: Request generation
    Server->>streamState: execTellPlan()
    streamState->>Provider: CreateChatCompletionStream()
    Provider-->>streamState: Return stream object
    streamState->>streamState: listenStream(stream)
    
    loop For Each Chunk
        streamState->>streamManager: Recv()
        streamManager->>Provider: Get next chunk
        Provider-->>streamManager: Return chunk
        streamManager-->>streamState: Return processed chunk
        streamState->>streamState: processChunk()
        streamState-->>Client: Stream update
    end
    
    Provider-->>streamManager: Stream end signal
    streamManager-->>streamState: Signal completion
    streamState->>streamState: handleStreamFinished()
    streamState->>streamState: storeOnFinished()
    streamState-->>Client: Completed response
```

The streaming system includes:
- **Timeout Management**: Handles inactivity with configurable timeouts
- **Retry Logic**: Automatically retries failed requests with backoff
- **Chunk Processing**: Parses and processes stream chunks
- **State Management**: Tracks and updates the state of the streaming process

Sources: `app/server/model/client.go:75-108`, `app/server/model/plan/tell_stream_main.go:17-251`, `app/server/model/plan/tell_stream_finish.go:17-248`

## Error Handling and Retries

The system implements robust error handling with sophisticated retry logic:

```mermaid
flowchart TD
    Start["withRetries()"]
    Attempt["Execute operation()"]
    CheckError{"Error occurred?"}
    CheckRetryable{"isNonRetriableErr()"}
    CheckMaxRetries{"numRetry >= OPENAI_MAX_RETRIES"}
    ParseRetryTime["parseRetryAfter()"]
    HasDuration{"duration != nil"}
    CalcWait["Calculate wait with OPENAI_BACKOFF_MULTIPLIER"]
    CheckAbort{"waitDuration > OPENAI_ABORT_WAIT_DURATION"}
    CheckMax{"waitDuration > OPENAI_MAX_WAIT_DURATION"}
    SetMax["waitDuration = OPENAI_MAX_WAIT_DURATION"]
    UseBackoff["waitBackoff(numRetry)"]
    Wait["time.Sleep(waitDuration)"]
    Increment["numRetry++"]
    Return["Return result"]
    ReturnError["Return error"]
    
    Start --> Attempt
    Attempt --> CheckError
    CheckError -- "No" --> Return
    CheckError -- "Yes" --> CheckRetryable
    CheckRetryable -- "Yes" --> ReturnError
    CheckRetryable -- "No" --> CheckMaxRetries
    CheckMaxRetries -- "Yes" --> ReturnError
    CheckMaxRetries -- "No" --> ParseRetryTime
    ParseRetryTime --> HasDuration
    HasDuration -- "Yes" --> CalcWait
    HasDuration -- "No" --> UseBackoff
    CalcWait --> CheckAbort
    CheckAbort -- "Yes" --> ReturnError
    CheckAbort -- "No" --> CheckMax
    CheckMax -- "Yes" --> SetMax
    CheckMax -- "No" --> Wait
    SetMax --> Wait
    UseBackoff --> Wait
    Wait --> Increment
    Increment --> Attempt
```

Key error handling features:
1. **Error Classification**: Categorizes errors as retryable or non-retryable
2. **Exponential Backoff**: Increases wait time between retries
3. **Rate Limit Handling**: Respects provider rate limit headers
4. **Maximum Retries**: Caps retry attempts to prevent endless loops

Sources: `app/server/model/client.go:408-434`, `app/server/model/client.go:436-440`, `app/server/model/client.go:544-589`

## Context Management

The context management system ensures AI models have the necessary information while optimizing token usage:

```mermaid
flowchart TD
    Start["formatModelContext()"]
    InitContext["Initialize context bodies"]
    FilterContext["Apply context filters"]
    CollectFiles["Collect files to include"]
    SortByRelevance["Sort by relevance if ordered"]
    ProcessFiles["Process each file up to token limit"]
    FormatMessages["Format as ExtendedChatMessagePart"]
    AddImages["Add image context if present"]
    AddApplyScript["Add _apply.sh script if needed"]
    AddEnd["Add END OF CONTEXT marker"]
    Return["Return formatted context"]
    
    Start --> InitContext
    InitContext --> FilterContext
    FilterContext --> CollectFiles
    CollectFiles --> SortByRelevance
    SortByRelevance --> ProcessFiles
    ProcessFiles --> FormatMessages
    FormatMessages --> AddImages
    AddImages --> AddApplyScript
    AddApplyScript --> AddEnd
    AddEnd --> Return
```

Context management features:
1. **Smart Context Selection**: Prioritizes relevant files based on current task
2. **Auto-Loading**: Automatically identifies and loads files referenced in the plan
3. **Token Management**: Ensures context stays within model token limits
4. **Context Caching**: Optimizes performance and costs through caching

Sources: `app/server/model/plan/tell_context.go:16-366`, `app/server/model/plan/tell_context.go:368-443`

## Model Roles System

Plandex uses a sophisticated role-based system for AI models, where different models are configured for specific tasks:

```mermaid
flowchart TD
    subgraph "ModelPack System"
        ModelPack["ModelPack Configuration"]
        ModelRoleConfigs["ModelRoleConfig instances"]
    end
    
    subgraph "Model Roles"
        Architect["Architect\n(System Design)"]
        Planner["Planner\n(Task Planning)"]
        Coder["Coder\n(Code Generation)"]
        Builder["Builder\n(Integration)"]
        Verifier["Verifier\n(Validation)"]
        AutoFix["AutoFix\n(Bug Fixing)"]
    end
    
    subgraph "Model Selection Process"
        EstimateTokens["GetMessagesTokenEstimate()"]
        SelectRole["GetRoleForInputTokens()"]
        CreateRequest["ModelRequest() in model_request.go"]
        SendRequest["CreateChatCompletionStream() in client.go"]
    end
    
    ModelPack --> ModelRoleConfigs
    ModelRoleConfigs --> Architect
    ModelRoleConfigs --> Planner
    ModelRoleConfigs --> Coder
    ModelRoleConfigs --> Builder
    ModelRoleConfigs --> Verifier
    ModelRoleConfigs --> AutoFix
    
    EstimateTokens --> SelectRole
    SelectRole --> CreateRequest
    CreateRequest --> SendRequest
```

The role system allows for:
1. **Specialized Models**: Different models optimized for different tasks
2. **Parameter Tuning**: Role-specific temperature, top_p, and other settings
3. **Token Management**: Role-specific token limits and prioritization
4. **Cost Optimization**: Using lower-cost models for appropriate tasks

Sources: `app/server/model/model_request.go:16-44`, `app/server/model/model_request.go:73-74`

## Provider-Specific Optimizations

The system includes various optimizations for specific providers:

1. **OpenRouter optimizations**:
   - Adding the `:nitro` suffix to choose the fastest provider
   - Setting headers for region preferences and throughput
   - Configuring referer information

2. **OpenAI optimizations**:
   - Support for organization ID
   - Custom endpoints
   - Handling system prompt disabling for models that don't support it

3. **Streaming optimizations**:
   - Timeouts tuned by provider (30s for chunks, 5s for usage)
   - Provider-specific response parsing
   - Fallback handling for differently structured responses

Sources: `app/server/model/client.go:110-125`, `app/server/model/client.go:459-528`, `app/server/model/client.go:592-599`

## Usage Tracking

The system tracks AI model usage through hooks that record token usage, models used, and other metrics:

```mermaid
sequenceDiagram
    participant Server as "Plandex Server"
    participant ModelRequest as "ModelRequest()"
    participant AI as "AI Provider"
    participant Hooks as "hooks.ExecHook()"
    
    Server->>ModelRequest: Make request with parameters
    ModelRequest->>Hooks: WillSendModelRequest hook
    Hooks-->>ModelRequest: Continue if allowed
    ModelRequest->>AI: Send request to provider
    AI-->>ModelRequest: Return response
    ModelRequest->>Hooks: DidSendModelRequest hook
    Note over Hooks: Record usage metrics:<br>- Input tokens<br>- Output tokens<br>- Cached tokens<br>- Model name & provider<br>- Purpose & generation ID
    Hooks-->>ModelRequest: Processing complete
    ModelRequest-->>Server: Return final response
```

Usage tracking includes:
- Input, output, and cached token counts
- Model identification (name, provider, role)
- Purpose categorization
- Request timing metrics
- Content generation IDs

Sources: `app/server/model/model_request.go:151-184`

## Conclusion

Plandex's AI Model Integration system provides a robust, flexible interface to various AI providers while handling the complexities of token management, streaming, error handling, and provider-specific optimizations. This system forms the foundation for Plandex's AI-powered capabilities, allowing it to leverage multiple models for different aspects of the development process while maintaining a consistent interface for the rest of the application.

---

# Page: Model Configuration and Management

# Model Configuration and Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/cli/cmd/model_packs.go](app/cli/cmd/model_packs.go)
- [app/cli/cmd/model_providers.go](app/cli/cmd/model_providers.go)
- [app/cli/cmd/models.go](app/cli/cmd/models.go)
- [app/cli/cmd/set_model.go](app/cli/cmd/set_model.go)
- [app/cli/lib/model_credentials.go](app/cli/lib/model_credentials.go)
- [app/cli/lib/model_settings.go](app/cli/lib/model_settings.go)
- [app/server/handlers/models.go](app/server/handlers/models.go)
- [app/server/model/client.go](app/server/model/client.go)
- [app/server/model/client_stream.go](app/server/model/client_stream.go)
- [app/server/model/model_error.go](app/server/model/model_error.go)
- [app/server/model/plan/tell_stream_error.go](app/server/model/plan/tell_stream_error.go)
- [app/server/types/message.go](app/server/types/message.go)
- [app/shared/ai_models_available.go](app/shared/ai_models_available.go)
- [app/shared/ai_models_custom.go](app/shared/ai_models_custom.go)
- [app/shared/ai_models_data_models.go](app/shared/ai_models_data_models.go)
- [app/shared/ai_models_errors.go](app/shared/ai_models_errors.go)
- [app/shared/ai_models_packs.go](app/shared/ai_models_packs.go)
- [app/shared/ai_models_providers.go](app/shared/ai_models_providers.go)
- [test/smoke_test.sh](test/smoke_test.sh)
- [test/test_utils.sh](test/test_utils.sh)

</details>



This document covers Plandex's comprehensive model configuration and management system, including built-in and custom AI models, model providers, model packs, and the infrastructure for managing authentication, fallbacks, and client connections to various AI services.

For information about how models are used during plan execution, see [AI Model Integration and Task Control](#3.2). For details about context and token management, see [Context and Token Management](#5.2).

## Model Configuration Architecture

Plandex organizes AI models through a hierarchical configuration system that spans from individual model definitions to complete model packs assigned to specific roles.

### Model Configuration Hierarchy

```mermaid
graph TD
    subgraph "Configuration Levels"
        ModelPack["ModelPack"]
        ModelRole["ModelRoleConfig"]
        BaseModel["BaseModelConfig"]
        Provider["ModelProviderConfigSchema"]
    end
    
    subgraph "Built-in System"
        BuiltInModels["BuiltInModels[]"]
        BuiltInPacks["BuiltInModelPacks[]"]
        BuiltInProviders["BuiltInModelProviderConfigs"]
    end
    
    subgraph "Custom System"
        CustomModels["CustomModel[]"]
        CustomPacks["CustomModelPacks[]"]
        CustomProviders["CustomProvider[]"]
    end
    
    ModelPack --> ModelRole
    ModelRole --> BaseModel
    BaseModel --> Provider
    
    BuiltInModels --> BaseModel
    BuiltInPacks --> ModelPack
    BuiltInProviders --> Provider
    
    CustomModels --> BaseModel
    CustomPacks --> ModelPack
    CustomProviders --> Provider
```

**Sources:** [app/shared/ai_models_data_models.go:273-303](), [app/shared/ai_models_packs.go:24-41](), [app/shared/ai_models_available.go:49-586]()

### Model Role System

Plandex assigns specific AI models to different roles within the planning and execution workflow. Each role has distinct requirements and fallback mechanisms.

```mermaid
graph LR
    subgraph "Model Roles"
        Planner["ModelRolePlanner"]
        Architect["ModelRoleArchitect"] 
        Coder["ModelRoleCoder"]
        Builder["ModelRoleBuilder"]
        WholeFileBuilder["ModelRoleWholeFileBuilder"]
        PlanSummary["ModelRolePlanSummary"]
        Namer["ModelRoleName"]
        CommitMsg["ModelRoleCommitMsg"]
        ExecStatus["ModelRoleExecStatus"]
    end
    
    subgraph "Fallback Types"
        LargeContext["LargeContextFallback"]
        LargeOutput["LargeOutputFallback"]
        Error["ErrorFallback"]
        Strong["StrongModel"]
    end
    
    Planner --> LargeContext
    Coder --> LargeContext
    Builder --> Strong
    Coder --> Error
    
    subgraph "Example: Daily Driver Pack"
        PlannerModel["anthropic/claude-sonnet-4"]
        CoderModel["anthropic/claude-sonnet-4"]
        BuilderModel["openai/o4-mini-medium"]
    end
    
    Planner -.-> PlannerModel
    Coder -.-> CoderModel
    Builder -.-> BuilderModel
```

**Sources:** [app/shared/ai_models_packs.go:124-403](), [app/shared/ai_models_data_models.go:286-303]()

## Built-in Models and Providers

### Available Model Definitions

The system includes comprehensive definitions for models from major AI providers, with detailed token limits, capabilities, and provider mappings.

| Model Example | Max Tokens | Max Output | Reserved Output | Compatibility |
|---------------|------------|------------|-----------------|---------------|
| `openai/o3-high` | 200,000 | 100,000 | 40,000 | Full |
| `anthropic/claude-sonnet-4` | 200,000 | 128,000 | 40,000 | Full + Cache |
| `google/gemini-2.5-pro` | 1,048,576 | 65,535 | 65,535 | Full |
| `deepseek/r1` | 164,000 | 33,000 | 20,000 | Full |

**Sources:** [app/shared/ai_models_available.go:49-586]()

### Built-in Model Providers

```mermaid
graph TD
    subgraph "Provider Categories"
        Direct["Direct API Providers"]
        Aggregated["Aggregated Providers"]
        Local["Local Providers"]
        Cloud["Cloud Platforms"]
    end
    
    subgraph "Direct APIs"
        OpenAI["ModelProviderOpenAI<br/>api.openai.com"]
        Anthropic["ModelProviderAnthropic<br/>LiteLLM Proxy"]
        DeepSeek["ModelProviderDeepSeek<br/>LiteLLM Proxy"]
    end
    
    subgraph "Aggregated"
        OpenRouter["ModelProviderOpenRouter<br/>openrouter.ai"]
        ClaudeMax["ModelProviderAnthropicClaudeMax<br/>OAuth Integration"]
    end
    
    subgraph "Cloud Platforms"
        Vertex["ModelProviderGoogleVertex<br/>Service Account Auth"]
        Azure["ModelProviderAzureOpenAI<br/>Deployment Mapping"]
        Bedrock["ModelProviderAmazonBedrock<br/>AWS Credentials"]
    end
    
    subgraph "Local"
        Ollama["ModelProviderOllama<br/>Local LLM Server"]
    end
    
    Direct --> OpenAI
    Direct --> Anthropic
    Direct --> DeepSeek
    
    Aggregated --> OpenRouter
    Aggregated --> ClaudeMax
    
    Cloud --> Vertex
    Cloud --> Azure
    Cloud --> Bedrock
    
    Local --> Ollama
```

**Sources:** [app/shared/ai_models_providers.go:116-219](), [app/shared/ai_models_providers.go:38-77]()

## Custom Models and Providers

### Custom Model Configuration

Users can define custom models and providers through JSON configuration files managed via the CLI.

```mermaid
graph TD
    subgraph "Custom Configuration Flow"
        ClientInput["ClientModelsInput<br/>(JSON Schema)"]
        ServerInput["ModelsInput<br/>(Server Processing)"]
        Database["PostgreSQL Storage"]
        Runtime["Runtime Model Resolution"]
    end
    
    subgraph "Custom Entities"
        CustomModel["CustomModel<br/>modelId, providers[]"]
        CustomProvider["CustomProvider<br/>name, baseUrl, auth"]
        CustomPack["CustomModelPack<br/>roles configuration"]
    end
    
    ClientInput --> ServerInput
    ServerInput --> Database
    Database --> Runtime
    
    CustomModel --> ClientInput
    CustomProvider --> ClientInput
    CustomPack --> ClientInput
```

**Sources:** [app/shared/ai_models_custom.go:57-62](), [app/server/handlers/models.go:19-59]()

### Example Custom Model Definition

The system supports defining custom models with provider mappings and authentication requirements:

```json
{
  "models": [{
    "modelId": "meta-llama/llama-4-maverick",
    "publisher": "meta-llama",
    "description": "Meta Llama 4 Maverick",
    "maxTokens": 1048576,
    "maxOutputTokens": 16000,
    "providers": [{
      "provider": "custom",
      "customProvider": "togetherai",
      "modelName": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"
    }]
  }],
  "providers": [{
    "name": "togetherai",
    "baseUrl": "https://api.together.xyz/v1",
    "apiKeyEnvVar": "TOGETHER_API_KEY"
  }]
}
```

**Sources:** [app/cli/cmd/models.go:516-612]()

## CLI Commands for Model Management

### Primary Model Commands

The CLI provides comprehensive commands for inspecting and configuring models:

```mermaid
graph TD
    subgraph "Model Commands"
        models["plandex models<br/>Show current plan settings"]
        setModel["plandex set-model<br/>Change model configuration"]
        available["plandex models available<br/>List all models"]
        custom["plandex models custom<br/>Manage custom definitions"]
    end
    
    subgraph "Model Pack Commands"
        packs["plandex model-packs<br/>List available packs"]
        showPack["plandex model-packs show<br/>Show pack details"]
    end
    
    subgraph "Provider Commands"
        providers["plandex providers<br/>List providers"]
        credStatus["Credential validation<br/>CheckCredentialStatus()"]
    end
    
    models --> ModelRoleDisplay
    setModel --> ModelPackSelection
    custom --> JSONFileEditor
    
    ModelRoleDisplay["renderSettings()<br/>Table output with roles"]
    ModelPackSelection["updateModelSettings()<br/>Pack or JSON selection"]
    JSONFileEditor["manageCustomModels()<br/>Edit + sync workflow"]
```

**Sources:** [app/cli/cmd/models.go:240-277](), [app/cli/cmd/set_model.go:52-93](), [app/cli/cmd/model_packs.go:61-122]()

### Model Selection Workflow

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Editor
    participant Server
    
    User->>CLI: plandex set-model
    CLI->>CLI: Load current settings
    CLI->>User: Present options:<br/>1. Select model pack<br/>2. Edit JSON settings
    
    alt Model Pack Selection
        User->>CLI: Choose "daily-driver"
        CLI->>Server: UpdateSettings API
    else JSON Configuration
        CLI->>Editor: Open model-settings.json
        User->>Editor: Edit configuration
        CLI->>CLI: Validate changes
        CLI->>Server: UpdateSettings API
    end
    
    Server->>CLI: Confirmation message
```

**Sources:** [app/cli/cmd/set_model.go:137-379]()

## Server-Side Model Client Management

### Client Initialization and Provider Resolution

The server manages AI model clients through a sophisticated provider resolution and authentication system:

```mermaid
graph TD
    subgraph "Client Management"
        InitClients["InitClients()<br/>Map auth vars to providers"]
        ClientInfo["ClientInfo<br/>openai.Client + config"]
        CreateStream["CreateChatCompletionStream()<br/>Request routing"]
    end
    
    subgraph "Provider Resolution"
        AuthVars["map[string]string<br/>Environment variables"]
        GetProviders["GetProvidersForAuthVars()<br/>Filter available providers"]
        ProviderConfig["ModelProviderConfigSchema<br/>Auth + URL configuration"]
    end
    
    subgraph "Request Flow"
        ModelConfig["ModelRoleConfig<br/>Role-specific config"]
        BaseConfig["GetBaseModelConfig()<br/>Resolve provider"]
        ExtendedReq["ExtendedChatCompletionRequest<br/>Provider-specific fields"]
    end
    
    AuthVars --> GetProviders
    GetProviders --> ProviderConfig
    ProviderConfig --> InitClients
    InitClients --> ClientInfo
    
    ModelConfig --> BaseConfig
    BaseConfig --> CreateStream
    CreateStream --> ExtendedReq
```

**Sources:** [app/server/model/client.go:46-80](), [app/shared/ai_models_providers.go:229-288]()

### Authentication and Credential Management

```mermaid
graph TD
    subgraph "Credential Types"
        APIKeys["API Key Environment Variables<br/>OPENAI_API_KEY, etc."]
        OAuth["OAuth Integration<br/>Claude Max subscription"]
        ServiceAccount["Service Account JSON<br/>Google Vertex AI"]
        AWSCreds["AWS Credentials<br/>Bedrock access"]
    end
    
    subgraph "Validation Flow"
        CheckStatus["CheckCredentialStatus()<br/>Validate all providers"]
        ResolveAuth["ResolveProviderAuthVars()<br/>Load credentials"]
        MustVerify["MustVerifyAuthVars()<br/>CLI validation"]
    end
    
    subgraph "Provider-Specific Auth"
        ClaudeMaxAuth["hasClaudeMaxAuth<br/>OAuth token"]
        AWSAuth["hasAWSAuth<br/>AWS SDK config"]
        SkipAuth["skipAuth<br/>Local providers"]
    end
    
    APIKeys --> ResolveAuth
    OAuth --> ClaudeMaxAuth
    ServiceAccount --> ResolveAuth
    AWSCreds --> AWSAuth
    
    CheckStatus --> ResolveAuth
    ResolveAuth --> MustVerify
```

**Sources:** [app/cli/lib/model_credentials.go:49-106](), [app/cli/lib/model_credentials.go:237-299]()

### Error Handling and Fallbacks

The system implements sophisticated error classification and fallback mechanisms:

```mermaid
graph TD
    subgraph "Error Classification"
        HTTPError["HTTPError<br/>Status + body parsing"]
        ClassifyError["ClassifyModelError()<br/>Map to ModelError types"]
        ModelError["ModelError<br/>Kind + retriable + delay"]
    end
    
    subgraph "Error Types"
        ContextTooLong["ErrContextTooLong<br/>→ LargeContextFallback"]
        RateLimited["ErrRateLimited<br/>→ Retry with delay"]
        Overloaded["ErrOverloaded<br/>→ Retry"]
        Other["ErrOther<br/>→ ErrorFallback"]
    end
    
    subgraph "Fallback Resolution"
        GetFallback["GetFallbackForModelError()<br/>Select appropriate fallback"]
        ProviderFallback["GetProviderFallback()<br/>Try different provider"]
        RetryLogic["withStreamingRetries()<br/>Exponential backoff"]
    end
    
    HTTPError --> ClassifyError
    ClassifyError --> ModelError
    
    ModelError --> ContextTooLong
    ModelError --> RateLimited
    ModelError --> Overloaded
    ModelError --> Other
    
    ContextTooLong --> GetFallback
    Other --> GetFallback
    GetFallback --> ProviderFallback
    ProviderFallback --> RetryLogic
```

**Sources:** [app/server/model/model_error.go:90-165](), [app/shared/ai_models_errors.go:49-105](), [app/server/model/client_stream.go:230-340]()

---

# Page: Context and Token Management

# Context and Token Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/cli/lib/context_load.go](app/cli/lib/context_load.go)
- [app/cli/lib/context_update.go](app/cli/lib/context_update.go)
- [app/cli/lib/model_credentials.go](app/cli/lib/model_credentials.go)
- [app/cli/types/types.go](app/cli/types/types.go)
- [app/server/model/client.go](app/server/model/client.go)
- [app/server/model/client_stream.go](app/server/model/client_stream.go)
- [app/server/model/model_error.go](app/server/model/model_error.go)
- [app/server/model/plan/tell_stream_error.go](app/server/model/plan/tell_stream_error.go)
- [app/server/types/message.go](app/server/types/message.go)
- [app/shared/ai_models_available.go](app/shared/ai_models_available.go)
- [app/shared/ai_models_data_models.go](app/shared/ai_models_data_models.go)
- [app/shared/ai_models_errors.go](app/shared/ai_models_errors.go)
- [app/shared/ai_models_packs.go](app/shared/ai_models_packs.go)
- [app/shared/ai_models_providers.go](app/shared/ai_models_providers.go)
- [test/smoke_test.sh](test/smoke_test.sh)
- [test/test_utils.sh](test/test_utils.sh)

</details>



This page covers how Plandex manages context loading, token counting, and memory optimization when interacting with AI models. This includes file processing, token estimation, context truncation strategies, and model-specific token limits.

For information about model configuration and selection, see [Model Configuration and Management](#5.1). For details about AI response processing, see [Response Processing and Error Handling](#5.3).

## Overview

Plandex's context and token management system ensures efficient use of AI model context windows while maintaining comprehensive project understanding. The system handles multiple context types, enforces token limits, and implements optimization strategies to maximize the useful information sent to models.

## Context Types and Loading

### Context Type Hierarchy

```mermaid
graph TD
    Context["Context"]
    Context --> FileType["ContextFileType"]
    Context --> TreeType["ContextDirectoryTreeType"] 
    Context --> MapType["ContextMapType"]
    Context --> ImageType["ContextImageType"]
    Context --> URLType["ContextURLType"]
    Context --> NoteType["ContextNoteType"]
    Context --> PipedType["ContextPipedDataType"]
    
    FileType --> RegularFile["Regular Files"]
    TreeType --> DirStructure["Directory Structures"]
    MapType --> CodeMap["Code Definition Maps"]
    ImageType --> Images["Image Files"]
    URLType --> WebContent["Web Content"]
    NoteType --> UserNotes["User Notes"]
    PipedType --> StdinData["Piped Data"]
```

**Sources:** [app/cli/lib/context_load.go:429-438](), [app/shared/context.go]()

### Context Loading Limits

The system enforces multiple limits during context loading:

| Limit Type | Constant | Value | Purpose |
|------------|----------|-------|---------|
| Max Context Body Size | `MaxContextBodySize` | 500MB | Individual file size limit |
| Max Context Count | `MaxContextCount` | 1000 | Total number of context items |
| Max Context Map Paths | `MaxContextMapPaths` | 5000 | Map-type context limit |
| Context Map Max Batch Size | `ContextMapMaxBatchSize` | 50 | Files per map batch |
| Context Map Max Batch Bytes | `ContextMapMaxBatchBytes` | 50MB | Bytes per map batch |

**Sources:** [app/cli/lib/context_load.go:24](), [app/shared/constants.go](), [app/cli/lib/context_load.go:462-494]()

### Context Loading Flow

```mermaid
flowchart TD
    LoadRequest["MustLoadContext()"]
    ParsePaths["ParseInputPaths()"]
    CheckLimits["Size & Count Limits"]
    ProcessFiles["Process Files Concurrently"]
    TokenEstimate["GetNumTokensEstimate()"]
    BatchMap["Batch Map Contents"]
    SendServer["Send to Server"]
    
    LoadRequest --> ParsePaths
    ParsePaths --> CheckLimits
    CheckLimits --> ProcessFiles
    ProcessFiles --> TokenEstimate
    TokenEstimate --> BatchMap
    BatchMap --> SendServer
    
    CheckLimits --> Skip1["Skip Too Large"]
    CheckLimits --> Skip2["Skip After Limit"]
    ProcessFiles --> MapDetails["getMapFileDetails()"]
    MapDetails --> TruncateMap["Truncate Large Maps"]
```

**Sources:** [app/cli/lib/context_load.go:26-757](), [app/cli/lib/context_load.go:482-551]()

## Token Counting and Estimation

### Token Estimation Methods

Plandex uses different token counting strategies based on content type:

```mermaid
graph LR
    Content["Content"]
    Content --> TextContent["Text Content"]
    Content --> ImageContent["Image Content"]
    
    TextContent --> BasicEstimate["GetNumTokensEstimate()"]
    ImageContent --> ImageTokens["GetImageTokens()"]
    
    BasicEstimate --> CharCount["Character-based estimation"]
    ImageTokens --> DetailLevel["Image detail level"]
    DetailLevel --> TokenCalc["Token calculation"]
```

**Sources:** [app/cli/lib/context_update.go:459](), [app/cli/lib/context_update.go:450-451](), [app/shared/token_estimation.go]()

### Model-Specific Token Limits

Different models have varying token limits and management strategies:

```mermaid
graph TD
    ModelConfig["BaseModelConfig"]
    ModelConfig --> MaxTokens["MaxTokens"]
    ModelConfig --> MaxOutput["MaxOutputTokens"] 
    ModelConfig --> Reserved["ReservedOutputTokens"]
    ModelConfig --> ConvoTokens["DefaultMaxConvoTokens"]
    ModelConfig --> Padding["TokenEstimatePaddingPct"]
    
    MaxTokens --> EffectiveInput["Effective Input = MaxTokens - ReservedOutputTokens"]
    MaxOutput --> OutputBudget["Output Budget"]
    Reserved --> SafetyMargin["Safety Margin"]
    ConvoTokens --> ConvoLimit["Conversation Token Limit"]
    Padding --> EstimateAdjust["Estimation Adjustment"]
```

**Sources:** [app/shared/ai_models_available.go:14-21](), [app/shared/ai_models_data_models.go:31-50]()

## Context Optimization Strategies

### File Processing Pipeline

```mermaid
flowchart TD
    FileInput["File Input"]
    SizeCheck["Size Check"]
    NormEOL["NormalizeEOL()"]
    TokenEst["Token Estimation"]
    CacheCheck["Cache SHA Check"]
    Batch["Batch Processing"]
    
    FileInput --> SizeCheck
    SizeCheck --> TooBig["Skip if > MaxContextBodySize"]
    SizeCheck --> NormEOL
    NormEOL --> TokenEst
    TokenEst --> CacheCheck
    CacheCheck --> Changed["File Changed?"]
    Changed --> Batch
    
    TooBig --> SkipLarge["filesSkippedTooLarge"]
    Batch --> SizeLimitReached["totalSize > limit"]
    SizeLimitReached --> SkipAfter["filesSkippedAfterSizeLimit"]
```

**Sources:** [app/cli/lib/context_load.go:454-480](), [app/cli/lib/context_update.go:418-439](), [app/shared/file_utils.go]()

### Map File Optimization

Map files receive special processing to handle large codebases efficiently:

```mermaid
graph TD
    MapFile["Map File"]
    MapFile --> Support["HasFileMapSupport()"]
    Support --> Process["getMapFileDetails()"]
    Process --> SizeCheck["Size Check"]
    SizeCheck --> Truncate["Truncate if needed"]
    SizeCheck --> Batch["Add to Batch"]
    
    Truncate --> TruncList["mapFilesTruncatedTooLarge"]
    Batch --> BatchFull["Batch Size Check"]
    BatchFull --> NewBatch["Create New Batch"]
    BatchFull --> ContinueBatch["Continue Current Batch"]
```

**Sources:** [app/cli/lib/context_load.go:482-510](), [app/cli/lib/context_load.go:620-663]()

## Model Context Management

### Context Resolution for Models

```mermaid
flowchart LR
    ModelRequest["Model Request"]
    ModelRequest --> ResolveReq["resolveReq()"]
    ResolveReq --> SystemPrompt["System Prompt Check"]
    ResolveReq --> RoleParams["Role Params Check"]
    
    SystemPrompt --> Disabled1["SystemPromptDisabled?"]
    Disabled1 --> ChangeRole["Change to User Role"]
    
    RoleParams --> Disabled2["RoleParamsDisabled?"]
    Disabled2 --> ClearParams["Clear Temperature/TopP"]
    
    ChangeRole --> FinalReq["Final Request"]
    ClearParams --> FinalReq
```

**Sources:** [app/server/model/client.go:502-532]()

### Cache Control Integration

For models supporting cache control (like Anthropic Claude):

```mermaid
graph TD
    Message["Chat Message"]
    Message --> Parts["Message Parts"]
    Parts --> CacheControl["CacheControl Check"]
    CacheControl --> Ephemeral["CacheControlTypeEphemeral"]
    CacheControl --> None["No Cache Control"]
    
    Ephemeral --> CacheBreakpoint["Cache Breakpoint"]
    None --> Regular["Regular Processing"]
    
    CacheBreakpoint --> ModelRequest["Send to Model"]
    Regular --> ModelRequest
    
    ModelRequest --> CacheError["Cache Support Error?"]
    CacheError --> RemoveCache["Remove Cache Control"]
    CacheError --> Retry["Retry Request"]
```

**Sources:** [app/server/model/client.go:189-197](), [app/server/types/message.go:12-27]()

## Context Update and Synchronization

### Outdated Context Detection

```mermaid
flowchart TD
    CheckStart["CheckOutdatedContext()"]
    CheckStart --> GetContexts["Get Current Contexts"]
    GetContexts --> Concurrent["Process Concurrently"]
    
    Concurrent --> FileCheck["File Existence Check"]
    Concurrent --> ShaCheck["SHA Comparison"]
    Concurrent --> SizeCheck["Size Validation"]
    
    FileCheck --> Missing["File Missing"]
    ShaCheck --> Changed["Content Changed"]
    SizeCheck --> SizeLimit["Size Limit Check"]
    
    Missing --> Remove["Mark for Removal"]
    Changed --> Update["Mark for Update"]
    SizeLimit --> Skip["Skip if Too Large"]
    
    Remove --> TokenDiff1["Calculate Token Diff"]
    Update --> TokenDiff2["Calculate Token Diff"]
    Skip --> SkipList["Add to Skip List"]
```

**Sources:** [app/cli/lib/context_update.go:291-616](), [app/cli/lib/context_update.go:368-475]()

### Context Update Pipeline

```mermaid
graph LR
    UpdateReq["Update Request"]
    UpdateReq --> ConflictCheck["checkContextConflicts()"]
    ConflictCheck --> ServerUpdate["UpdateContext API"]
    ConflictCheck --> DeleteOp["DeleteContext API"]
    
    ServerUpdate --> Response1["Update Response"]
    DeleteOp --> Response2["Delete Response"]
    
    Response1 --> Conflicts["Has Conflicts?"]
    Response2 --> Conflicts
    Conflicts --> BuildTrigger["Trigger Build if Needed"]
```

**Sources:** [app/cli/lib/context_update.go:224-287](), [app/cli/lib/context_update.go:672-676]()

## Performance and Error Handling

### Memory Management

The system implements several strategies to prevent memory issues:

| Strategy | Implementation | Purpose |
|----------|----------------|---------|
| Concurrent Processing | `sem := make(chan struct{}, ContextMapMaxClientConcurrency)` | Limit concurrent file processing |
| Size Limits | `MaxContextBodySize` checks | Prevent individual file overload |
| Batch Processing | Map file batching | Handle large numbers of files |
| Early Termination | Count and size limit checks | Stop processing when limits reached |

**Sources:** [app/cli/lib/context_load.go:155](), [app/cli/lib/context_update.go:359]()

### Error Recovery

```mermaid
graph TD
    ProcessError["Processing Error"]
    ProcessError --> ErrorType["Error Classification"]
    
    ErrorType --> SizeError["Size Limit Error"]
    ErrorType --> TokenError["Token Limit Error"]
    ErrorType --> IOError["I/O Error"]
    
    SizeError --> SkipFile["Skip File"]
    TokenError --> Truncate["Truncate Content"]
    IOError --> LogError["Log and Continue"]
    
    SkipFile --> Continue["Continue Processing"]
    Truncate --> Continue
    LogError --> Continue
    
    Continue --> Summary["Generate Summary"]
    Summary --> UserNotify["Notify User of Skipped Items"]
```

**Sources:** [app/cli/lib/context_load.go:752-756](), [app/cli/lib/context_update.go:322-324]()

---

# Page: Response Processing and Error Handling

# Response Processing and Error Handling

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/cli/lib/model_credentials.go](app/cli/lib/model_credentials.go)
- [app/server/model/client.go](app/server/model/client.go)
- [app/server/model/client_stream.go](app/server/model/client_stream.go)
- [app/server/model/model_error.go](app/server/model/model_error.go)
- [app/server/model/plan/tell_stream_error.go](app/server/model/plan/tell_stream_error.go)
- [app/server/types/message.go](app/server/types/message.go)
- [app/shared/ai_models_available.go](app/shared/ai_models_available.go)
- [app/shared/ai_models_data_models.go](app/shared/ai_models_data_models.go)
- [app/shared/ai_models_errors.go](app/shared/ai_models_errors.go)
- [app/shared/ai_models_packs.go](app/shared/ai_models_packs.go)
- [app/shared/ai_models_providers.go](app/shared/ai_models_providers.go)
- [test/smoke_test.sh](test/smoke_test.sh)
- [test/test_utils.sh](test/test_utils.sh)

</details>



This page covers how Plandex processes streaming responses from AI models and handles various error conditions. It details the error classification system, retry logic, fallback mechanisms, and timeout management that ensure robust AI model interactions.

For model configuration and provider management, see [Model Configuration and Management](#5.1). For context processing and token management, see [Context and Token Management](#5.2).

## Overview

Plandex exclusively uses streaming requests for AI model interactions to enable real-time user feedback and more predictable cancellation behavior. The response processing system handles Server-Sent Events (SSE) streams, classifies errors, implements retry logic with exponential backoff, and provides multiple fallback strategies when primary models fail.

**Sources:** [app/server/model/client.go:25-27]()

## Streaming Response Processing

### Stream Architecture

```mermaid
graph TD
    Request["ExtendedChatCompletionRequest"] --> CreateStream["CreateChatCompletionStream"]
    CreateStream --> StreamReader["StreamReader[ExtendedChatCompletionStreamResponse]"]
    StreamReader --> ProcessChunk["processChatCompletionStream"]
    ProcessChunk --> Accumulator["StreamCompletionAccumulator"]
    Accumulator --> Timer["ACTIVE_STREAM_CHUNK_TIMEOUT"]
    Timer --> CheckContent["Check for Content/Usage/EOF"]
    CheckContent --> OnStream["OnStreamFn callback"]
    OnStream --> Result["ModelResponse"]
    
    CheckContent --> ErrorPath["HTTPError/StreamError"]
    ErrorPath --> ErrorClassify["classifyBasicError"]
    ErrorClassify --> RetryLogic["withStreamingRetries"]
```

The streaming system processes responses through several key components:

| Component | Purpose | Key Types |
|-----------|---------|-----------|
| `ExtendedChatCompletionStream` | Wrapper for OpenAI or custom streams | [app/server/model/client.go:82-87]() |
| `StreamReader` | Handles SSE parsing and JSON unmarshaling | [app/server/model/client.go:89-96]() |
| `ErrorAccumulator` | Tracks streaming errors with thread safety | [app/server/model/client.go:98-102]() |
| `StreamCompletionAccumulator` | Accumulates content and tracks timing | [app/server/types/message.go:255-273]() |

**Sources:** [app/server/model/client.go:82-102](), [app/server/model/client_stream.go:19-30]()

### Stream Processing Flow

```mermaid
graph TD
    Start["Start Stream"] --> Timer["Reset Timer"]
    Timer --> WaitChunk["Wait for Chunk"]
    WaitChunk --> Timeout{"Timeout?"}
    WaitChunk --> Received{"Chunk Received?"}
    WaitChunk --> Context{"Context Done?"}
    
    Timeout --> StreamFinished{"Stream Finished?"}
    StreamFinished -->|Yes| UsageWait["Wait for Usage Chunk"]
    StreamFinished -->|No| TimeoutError["Return Timeout Error"]
    UsageWait --> Complete["Complete"]
    
    Context --> Canceled["Return Context Error"]
    
    Received --> ParseSSE["Parse SSE Data"]
    ParseSSE --> CheckDone{"data: [DONE]?"}
    CheckDone -->|Yes| EOF["Return EOF"]
    CheckDone -->|No| Unmarshal["JSON Unmarshal"]
    Unmarshal --> ProcessChoice["Process Choice"]
    ProcessChoice --> Accumulate["Accumulate Content"]
    Accumulate --> Callback["OnStream Callback"]
    Callback --> Timer
    
    ProcessChoice --> FinishReason{"Finish Reason?"}
    FinishReason -->|error| ErrorFinish["Return Error"]
    FinishReason -->|stop| SetFinished["Set Stream Finished"]
    SetFinished --> UsageTimer["Reset Usage Timer"]
    UsageTimer --> Timer
```

The stream processing implements several timeout mechanisms:

- `ACTIVE_STREAM_CHUNK_TIMEOUT` (60 seconds): Maximum time between chunks
- `USAGE_CHUNK_TIMEOUT` (10 seconds): Time to wait for final usage chunk after stream completion

**Sources:** [app/server/model/client_stream.go:114-165](), [app/server/model/client.go:30-35]()

## Error Classification System

### Error Types and Classification

```mermaid
graph TD
    Error["Error Received"] --> HTTPCheck{"HTTPError?"}
    HTTPCheck -->|Yes| StatusCode["Check Status Code"]
    HTTPCheck -->|No| MessageClassify["ClassifyErrMsg"]
    
    StatusCode --> Code429["429/529: Rate Limited"]
    StatusCode --> Code413["413: Context Too Long"]
    StatusCode --> Code5xx["5xx: Server Error"]
    StatusCode --> CodeOther["Other Codes"]
    
    MessageClassify --> ContextMsg["Context length exceeded"]
    MessageClassify --> OverloadMsg["Model overloaded"]
    MessageClassify --> CacheMsg["Cache control error"]
    MessageClassify --> NoMatch["No classification match"]
    
    Code429 --> RateLimit["ErrRateLimited"]
    Code413 --> ContextLong["ErrContextTooLong"]
    Code5xx --> Retriable["ErrOther (retriable)"]
    CodeOther --> NonRetriable["ErrOther (non-retriable)"]
    
    ContextMsg --> ContextLong
    OverloadMsg --> Overload["ErrOverloaded"]
    CacheMsg --> Cache["ErrCacheSupport"]
    NoMatch --> Basic["Basic Error Check"]
    
    Basic --> NonRetriableBasic["isNonRetriableBasicErr"]
    NonRetriableBasic --> FinalClassification["Final ModelError"]
```

The error classification system recognizes several error types defined in `ModelErrKind`:

| Error Kind | Retriable | Purpose |
|------------|-----------|---------|
| `ErrContextTooLong` | No | Input exceeds model's context limit |
| `ErrOverloaded` | Yes | Model is temporarily overloaded |
| `ErrRateLimited` | Yes | Rate limit exceeded |
| `ErrSubscriptionQuotaExhausted` | Conditional | Claude Max subscription limit reached |
| `ErrCacheSupport` | Yes | Cache control not supported |
| `ErrOther` | Conditional | Generic error category |

**Sources:** [app/server/model/model_error.go:38-88](), [app/shared/ai_models_errors.go:10-29]()

### Retry-After Parsing

The system extracts retry timing from multiple sources:

1. `Retry-After` HTTP header (seconds or HTTP-date)
2. `X-RateLimit-Reset` header (epoch timestamp)
3. JSON body patterns like `"retry_after_ms": 1234`
4. Text patterns like "try again in 59 seconds"

**Sources:** [app/server/model/model_error.go:167-228]()

## Retry and Fallback Mechanisms

### Fallback Decision Tree

```mermaid
graph TD
    Error["Model Error"] --> Retriable{"Retriable?"}
    Retriable -->|No| NonRetriableFlow["Non-Retriable Flow"]
    Retriable -->|Yes| RetryCount{"Retry Count < Max?"}
    
    NonRetriableFlow --> ContextCheck{"ErrContextTooLong?"}
    ContextCheck -->|Yes| LargeContext["LargeContextFallback?"]
    ContextCheck -->|No| ErrorFallback["ErrorFallback?"]
    
    LargeContext -->|Exists| UseLarge["Use Large Context Model"]
    LargeContext -->|None| NoFallback["No Fallback Available"]
    
    ErrorFallback -->|Exists| UseError["Use Error Fallback Model"]
    ErrorFallback -->|None| ProviderFallback["Provider Fallback?"]
    
    ProviderFallback -->|Available| UseProvider["Use Different Provider"]
    ProviderFallback -->|None| NoFallback
    
    RetryCount -->|Yes| DelayCalc["Calculate Retry Delay"]
    RetryCount -->|No| CheckFallback["Check Fallbacks"]
    
    DelayCalc --> RetryAfter{"Has RetryAfterSeconds?"}
    RetryAfter -->|Yes| UseRetryAfter["Use RetryAfter * 1.1"]
    RetryAfter -->|No| UseJitter["Use Random Jitter"]
    
    UseRetryAfter --> Sleep["Sleep and Retry"]
    UseJitter --> Sleep
    Sleep --> RetryRequest["Retry Same Request"]
    
    CheckFallback --> ErrorFallback
```

### Fallback Types and Priority

The fallback system implements a hierarchy of recovery strategies:

| Fallback Type | Trigger | Implementation |
|---------------|---------|----------------|
| **Large Context** | `ErrContextTooLong` | `ModelRoleConfig.LargeContextFallback` |
| **Error Fallback** | Non-retriable errors | `ModelRoleConfig.ErrorFallback` |
| **Provider Fallback** | Provider-level failures | Different provider for same model |
| **Strong Model** | Task complexity | `ModelRoleConfig.StrongModel` |

**Sources:** [app/shared/ai_models_errors.go:49-105](), [app/shared/ai_models_errors.go:111-149]()

### Retry Configuration

```mermaid
graph LR
    Constants["Retry Constants"] --> MaxRetries["MAX_RETRIES_WITHOUT_FALLBACK = 3"]
    Constants --> MaxFallback["MAX_ADDITIONAL_RETRIES_WITH_FALLBACK = 1"]
    Constants --> MaxDelay["MAX_RETRY_DELAY_SECONDS = 10"]
    Constants --> FallbackTrigger["MAX_RETRIES_BEFORE_FALLBACK = 1"]
    
    RetryLogic["withStreamingRetries"] --> RetryCount["Track numTotalRetry"]
    RetryLogic --> FallbackCount["Track numFallbackRetry"]
    RetryLogic --> ProviderFlag["Track didProviderFallback"]
```

**Sources:** [app/server/model/client.go:32-35](), [app/shared/ai_models_errors.go:47]()

## Timeout Management

### Timeout Configuration

| Timeout Type | Duration | Purpose |
|--------------|----------|---------|
| `ACTIVE_STREAM_CHUNK_TIMEOUT` | 60 seconds | Maximum time between stream chunks |
| `USAGE_CHUNK_TIMEOUT` | 10 seconds | Time to wait for final usage information |

### Timeout Handling Flow

```mermaid
graph TD
    StartStream["Start Stream Processing"] --> SetTimer["Set ACTIVE_STREAM_CHUNK_TIMEOUT"]
    SetTimer --> WaitEvent["Wait for Event"]
    
    WaitEvent --> ChunkReceived["Chunk Received"]
    WaitEvent --> TimerExpired["Timer Expired"] 
    WaitEvent --> ContextDone["Context Cancelled"]
    
    ChunkReceived --> ResetTimer["Reset Timer"]
    ResetTimer --> ProcessChunk["Process Chunk"]
    ProcessChunk --> FinishCheck{"Finish Reason?"}
    
    FinishCheck -->|None| WaitEvent
    FinishCheck -->|Stop| UsageTimer["Set USAGE_CHUNK_TIMEOUT"]
    FinishCheck -->|Error| StreamError["Stream Error"]
    
    UsageTimer --> WaitUsage["Wait for Usage Chunk"]
    WaitUsage --> UsageReceived["Usage Received"]
    WaitUsage --> UsageTimeout["Usage Timeout"]
    
    UsageReceived --> Complete["Stream Complete"]
    UsageTimeout --> CompleteWithoutUsage["Complete Without Usage"]
    
    TimerExpired --> StreamFinished{"streamFinished?"}
    StreamFinished -->|Yes| CompleteWithoutUsage
    StreamFinished -->|No| TimeoutError["Timeout Error"]
    
    ContextDone --> PartialResult["Return Partial Result"]
```

**Sources:** [app/server/model/client_stream.go:114-136](), [app/server/model/client_stream.go:196-202]()

## Error Recovery Strategies

### Plan-Level Error Handling

The plan execution system implements additional error recovery specifically for tell/chat operations:

```mermaid
graph TD
    TellError["Tell Stream Error"] --> CanRetry{"canRetry?"}
    CanRetry -->|No| StoreError["Store Error Description"]
    CanRetry -->|Yes| RetryCheck["Check Retry Limits"]
    
    RetryCheck --> WithinLimits{"Within Limits?"}
    WithinLimits -->|No| MaxRetries["Max Retries Reached"]
    WithinLimits -->|Yes| RetryDelay["Calculate Retry Delay"]
    
    RetryDelay --> ModelErr{"Has ModelError?"}
    ModelErr -->|Yes| UseRetryAfter["Use RetryAfterSeconds * 1.1"]
    ModelErr -->|No| UseJitter["Use Random Jitter 1000-1200ms"]
    
    UseRetryAfter --> Sleep["Sleep"]
    UseJitter --> Sleep
    Sleep --> ResetContext["Reset Model Context"]
    ResetContext --> RetryRequest["Retry doTellRequest"]
    
    StoreError --> StoreMessage["Store Assistant Message"]
    StoreMessage --> StoreDesc["Store Description"]
    StoreDesc --> GitCommit["Git Commit"]
    
    MaxRetries --> StoreError
```

### Cache Support Error Handling

A special case exists for cache control errors where the system removes cache control breakpoints and retries:

1. Detect `ErrCacheSupport` error
2. Set `noCacheSupportErr` flag  
3. Remove `CacheControl` from all message content parts
4. Retry with same model configuration

**Sources:** [app/server/model/plan/tell_stream_error.go:34-152](), [app/server/model/client.go:189-197]()

### Provider Fallback Selection

When error and context fallbacks are exhausted, the system attempts provider fallback:

1. **OpenRouter Priority**: If OpenRouter credentials are available and not using Claude Max subscription, prefer OpenRouter for its built-in fallback routing
2. **Second Provider**: Otherwise, use the second available provider in the priority list
3. **Model Compatibility**: Ensure the fallback provider supports the same model ID

**Sources:** [app/shared/ai_models_errors.go:111-149]()

---

# Page: Data Storage and Management

# Data Storage and Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/server/db/db.go](app/server/db/db.go)
- [app/server/db/git.go](app/server/db/git.go)
- [app/server/db/locks.go](app/server/db/locks.go)
- [app/server/model/plan/state.go](app/server/model/plan/state.go)
- [app/server/model/plan/stop.go](app/server/model/plan/stop.go)
- [app/shared/plan_model_settings.go](app/shared/plan_model_settings.go)
- [releases/cli/versions/0.8.3.md](releases/cli/versions/0.8.3.md)
- [releases/server/versions/0.8.4.md](releases/server/versions/0.8.4.md)
- [releases/server/versions/2.1.3.md](releases/server/versions/2.1.3.md)

</details>



This page covers Plandex's data storage architecture, including database management, repository locking mechanisms, Git integration, and in-memory state management. It documents the persistence layer, concurrency control systems, and data serialization patterns that support plan execution and file management.

For information about API data models and request handling, see [Data Models and Shared Types](#4.2). For database schema details and migrations, see [Database Schema and Migrations](#6.1).

## Storage Architecture Overview

Plandex employs a multi-layered storage architecture combining PostgreSQL for persistent data, Git repositories for version control, and sophisticated in-memory state management for active operations.

### Storage Systems Diagram

```mermaid
graph TB
    subgraph "Client_Requests"
        APIRequest["API Request"]
    end
    
    subgraph "Server_Storage_Layer"
        PostgreSQL[("PostgreSQL Database")]
        GitRepos[("Git Repositories")]
        FileSystem[("Local File System")]
        InMemoryState["activePlans SafeMap"]
    end
    
    subgraph "Data_Management_Components"
        DBConn["db.Conn (*sqlx.DB)"]
        RepoLocks["Repository Locks System"]
        GitOps["Git Operations (GitRepo)"]
        ActivePlanMgr["Active Plan Manager"]
    end
    
    subgraph "Concurrency_Control"
        LockScope["LockScope (Read/Write)"]
        Heartbeat["Lock Heartbeat System"]
        RetryLogic["Exponential Backoff Retry"]
    end
    
    APIRequest --> DBConn
    APIRequest --> ActivePlanMgr
    
    DBConn --> PostgreSQL
    ActivePlanMgr --> InMemoryState
    
    RepoLocks --> PostgreSQL
    GitOps --> GitRepos
    GitOps --> FileSystem
    
    RepoLocks --> LockScope
    RepoLocks --> Heartbeat
    RepoLocks --> RetryLogic
    
    ActivePlanMgr --> GitOps
    ActivePlanMgr --> RepoLocks
    
    style PostgreSQL fill:#f9f
    style GitRepos fill:#9f9
    style InMemoryState fill:#99f
```

Sources: [app/server/db/db.go:18-94](), [app/server/db/locks.go:38-53](), [app/server/model/plan/state.go:17-19](), [app/server/db/git.go:32-40]()

## Database Connection and Configuration

The database layer centers around a global `*sqlx.DB` connection with specific PostgreSQL optimizations for concurrent operations.

### Database Connection Management

```mermaid
graph TB
    subgraph "Connection_Setup"
        EnvVars["Environment Variables"]
        ConnString["Connection String Builder"]
        SqlxDB["db.Conn (*sqlx.DB)"]
    end
    
    subgraph "Connection_Config"
        Timeouts["Timeout Settings"]
        PoolSettings["Connection Pool"]
        PGSettings["PostgreSQL Settings"]
    end
    
    subgraph "Migration_System"
        MigrateInstance["migrate.NewWithDatabaseInstance"]
        MigrationFiles["file://migrations"]
        MigrationUp["m.Up()"]
    end
    
    EnvVars --> ConnString
    ConnString --> SqlxDB
    SqlxDB --> Timeouts
    SqlxDB --> PoolSettings
    SqlxDB --> PGSettings
    
    SqlxDB --> MigrateInstance
    MigrationFiles --> MigrateInstance
    MigrateInstance --> MigrationUp
    
    style SqlxDB fill:#f9f
```

| Configuration Parameter | Production Value | Development Value | Purpose |
|------------------------|------------------|-------------------|---------|
| `StatementTimeout` | 30000ms | 30000ms | Query execution limit |
| `LockTimeout` | 4000ms | 4000ms | Row-level lock timeout |
| `IdleInTransactionSessionTimeout` | 90000ms | 90000ms | Idle transaction cleanup |
| `MaxOpenConns` | 50 | 10 | Connection pool size |
| `MaxIdleConns` | 20 | 5 | Idle connection limit |

The connection initialization includes automatic timezone setting to UTC and comprehensive timeout configuration to prevent hanging transactions during concurrent operations.

Sources: [app/server/db/db.go:20-94](), [app/server/db/db.go:96-175]()

## Repository Locking System

Plandex implements a sophisticated distributed locking mechanism to prevent concurrent modifications to Git repositories during plan execution.

### Lock Types and Scopes

```mermaid
graph TB
    subgraph "Lock_Scopes"
        ReadLock["LockScopeRead"]
        WriteLock["LockScopeWrite"]
    end
    
    subgraph "Lock_Conflicts"
        ReadRead["Read + Read: Allowed (same branch)"]
        ReadWrite["Read + Write: Blocked"]
        WriteWrite["Write + Write: Blocked"]
        ReadReadDiff["Read + Read: Blocked (different branch)"]
    end
    
    subgraph "Lock_Management"
        LockParams["LockRepoParams"]
        HeartbeatSys["Heartbeat System"]
        ExpiredCleanup["Expired Lock Cleanup"]
    end
    
    ReadLock --> ReadRead
    ReadLock --> ReadWrite
    WriteLock --> ReadWrite
    WriteLock --> WriteWrite
    ReadLock --> ReadReadDiff
    
    LockParams --> HeartbeatSys
    HeartbeatSys --> ExpiredCleanup
    
    style WriteLock fill:#fcc
    style ReadLock fill:#cfc
```

The `LockRepoParams` struct defines the complete context for lock acquisition:

| Field | Purpose |
|-------|---------|
| `OrgId` | Organization scope |
| `UserId` | User identification |
| `PlanId` | Plan identifier |
| `Branch` | Git branch target |
| `Scope` | Read or write lock |
| `PlanBuildId` | Build operation context |
| `Reason` | Debug logging context |

Sources: [app/server/db/locks.go:41-52](), [app/server/db/locks.go:249-278]()

### Lock Acquisition and Retry Logic

```mermaid
graph TB
    subgraph "Lock_Acquisition_Flow"
        StartLock["lockRepoDB()"]
        BeginTx["Begin RepeatableRead Tx"]
        SelectForUpdate["SELECT ... FOR UPDATE/SHARE"]
        CheckConflicts["Check Existing Locks"]
        InsertLock["INSERT new lock"]
        CommitTx["Commit Transaction"]
        StartHeartbeat["Start Heartbeat Goroutine"]
    end
    
    subgraph "Retry_Logic"
        RetryCheck{"Retry Needed?"}
        ExponentialBackoff["Exponential Backoff"]
        MaxRetries{"< maxLockRetries?"}
        RetryAttempt["Retry Attempt"]
    end
    
    subgraph "Heartbeat_System"
        HeartbeatLoop["Heartbeat Loop"]
        UpdateTimestamp["UPDATE last_heartbeat_at"]
        CheckHeartbeat{"Heartbeat Success?"}
        CancelOnFailure["Cancel Context"]
    end
    
    StartLock --> BeginTx
    BeginTx --> SelectForUpdate
    SelectForUpdate --> CheckConflicts
    CheckConflicts --> InsertLock
    InsertLock --> CommitTx
    CommitTx --> StartHeartbeat
    
    CheckConflicts -->|Conflict| RetryCheck
    RetryCheck --> ExponentialBackoff
    ExponentialBackoff --> MaxRetries
    MaxRetries -->|Yes| RetryAttempt
    RetryAttempt --> StartLock
    
    StartHeartbeat --> HeartbeatLoop
    HeartbeatLoop --> UpdateTimestamp
    UpdateTimestamp --> CheckHeartbeat
    CheckHeartbeat -->|Failure| CancelOnFailure
    CheckHeartbeat -->|Success| HeartbeatLoop
    
    style RetryAttempt fill:#ffa
    style CancelOnFailure fill:#fcc
```

The retry mechanism uses exponential backoff with jitter to handle lock contention:

- **Initial retry delay**: 300ms
- **Backoff factor**: 2x
- **Jitter**: ±30%
- **Maximum retries**: 6 attempts
- **Delete retries**: 60 attempts with 50ms delay

Sources: [app/server/db/locks.go:54-290](), [app/server/db/locks.go:564-611]()

### Heartbeat and Lock Lifecycle

```mermaid
sequenceDiagram
    participant Client as "Plan Execution"
    participant LockSys as "Lock System"
    participant DB as "PostgreSQL"
    participant Heartbeat as "Heartbeat Goroutine"
    
    Client->>LockSys: lockRepoDB(params)
    LockSys->>DB: BEGIN TRANSACTION
    LockSys->>DB: SELECT FOR UPDATE/SHARE
    LockSys->>DB: INSERT new lock
    LockSys->>DB: COMMIT
    LockSys->>Client: Return lock ID
    
    par Lock Usage
        Client->>Client: Perform Git operations
    and Heartbeat Loop
        loop Every 3 seconds
            Heartbeat->>DB: UPDATE last_heartbeat_at
            DB-->>Heartbeat: Rows affected check
            alt Lock exists
                Heartbeat->>Heartbeat: Continue heartbeat
            else Lock gone
                Heartbeat->>Heartbeat: Stop heartbeat
            end
        end
    end
    
    Client->>LockSys: Release lock
    LockSys->>DB: DELETE FROM repo_locks
    LockSys->>Heartbeat: Context cancellation
```

The heartbeat system maintains lock validity through regular database updates every 3 seconds, with a 60-second timeout for abandoned locks.

Sources: [app/server/db/locks.go:387-457](), [app/server/db/locks.go:480-521]()

## Git Integration and File Management

The Git integration layer provides version control operations with comprehensive lock file handling and retry mechanisms for concurrent access.

### GitRepo Operations

```mermaid
graph TB
    subgraph "GitRepo_Structure"
        GitRepo["GitRepo struct"]
        OrgId["orgId string"]
        PlanId["planId string"]
        PlanDir["getPlanDir()"]
    end
    
    subgraph "Core_Operations"
        GitAdd["GitAddAndCommit()"]
        GitCheckout["GitCheckoutBranch()"]
        GitReset["GitResetToSha()"]
        GitRewind["GitRewindToSha()"]
        GitClean["GitClearUncommittedChanges()"]
    end
    
    subgraph "State_Operations"
        GetCommitSha["GetCurrentCommitSha()"]
        GetHistory["GetGitCommitHistory()"]
        ListBranches["GitListBranches()"]
        CreateBranch["GitCreateBranch()"]
    end
    
    subgraph "Lock_File_Management"
        RemoveLockFiles["gitRemoveIndexLockFileIfExists()"]
        LockPaths["index.lock, HEAD.lock paths"]
        RetryRemoval["Retry lock removal"]
    end
    
    GitRepo --> OrgId
    GitRepo --> PlanId
    PlanDir --> GitAdd
    PlanDir --> GitCheckout
    
    GitAdd --> RemoveLockFiles
    GitCheckout --> RemoveLockFiles
    GitReset --> RemoveLockFiles
    
    RemoveLockFiles --> LockPaths
    RemoveLockFiles --> RetryRemoval
    
    style RemoveLockFiles fill:#ffa
```

All Git write operations are wrapped in `gitWriteOperation()` which provides automatic retry logic for lock file conflicts and exponential backoff for transient failures.

Sources: [app/server/db/git.go:32-65](), [app/server/db/git.go:655-684](), [app/server/db/git.go:604-645]()

### Git Lock File Handling

```mermaid
graph TB
    subgraph "Lock_File_Types"
        IndexLock[".git/index.lock"]
        HeadLock[".git/HEAD.lock"]
        RefHeadLock[".git/refs/heads/HEAD.lock"]
    end
    
    subgraph "Removal_Process"
        CheckExists["os.Stat() check"]
        ParallelRemoval["Parallel goroutines"]
        RetryLoop["Retry up to 10 times"]
        DelayBetween["20ms delay between attempts"]
    end
    
    subgraph "Error_Handling"
        NotExistOK["os.IsNotExist() → OK"]
        OtherErrors["Log other errors"]
        PanicRecovery["Panic recovery"]
    end
    
    IndexLock --> CheckExists
    HeadLock --> CheckExists
    RefHeadLock --> CheckExists
    
    CheckExists --> ParallelRemoval
    ParallelRemoval --> RetryLoop
    RetryLoop --> DelayBetween
    
    ParallelRemoval --> NotExistOK
    ParallelRemoval --> OtherErrors
    ParallelRemoval --> PanicRecovery
    
    style PanicRecovery fill:#fcc
```

The lock file removal system uses parallel goroutines to handle multiple lock file types simultaneously, with comprehensive error handling for race conditions.

Sources: [app/server/db/git.go:604-645](), [app/server/db/git.go:557-602]()

## In-Memory State Management

Active plan state is managed through a thread-safe map structure that coordinates real-time plan execution and client subscriptions.

### Active Plan Lifecycle

```mermaid
graph TB
    subgraph "Plan_State_Map"
        SafeMap["activePlans SafeMap[*ActivePlan]"]
        PlanKey["planId|branch key"]
        ActivePlan["types.ActivePlan"]
    end
    
    subgraph "Plan_Creation"
        CreateActive["CreateActivePlan()"]
        NewActivePlan["types.NewActivePlan()"]
        SetInMap["activePlans.Set()"]
        StartGoroutine["State monitoring goroutine"]
    end
    
    subgraph "State_Monitoring"
        ContextDone["<-activePlan.Ctx.Done()"]
        StreamDone["<-activePlan.StreamDoneCh"]
        SetStopped["SetPlanStatus(Stopped)"]
        SetFinished["SetPlanStatus(Finished)"]
        SetError["SetPlanStatus(Error)"]
    end
    
    subgraph "Plan_Cleanup"
        DeleteActive["DeleteActivePlan()"]
        ClearChanges["GitClearUncommittedChanges()"]
        RemoveFromMap["activePlans.Delete()"]
    end
    
    CreateActive --> NewActivePlan
    NewActivePlan --> SetInMap
    SetInMap --> StartGoroutine
    
    StartGoroutine --> ContextDone
    StartGoroutine --> StreamDone
    ContextDone --> SetStopped
    StreamDone --> SetFinished
    StreamDone --> SetError
    
    SetStopped --> DeleteActive
    SetFinished --> DeleteActive
    SetError --> DeleteActive
    
    DeleteActive --> ClearChanges
    ClearChanges --> RemoveFromMap
    
    style SetError fill:#fcc
    style DeleteActive fill:#ffa
```

The `SafeMap` provides thread-safe operations for the global `activePlans` registry, enabling concurrent access from multiple request handlers while maintaining consistency.

Sources: [app/server/model/plan/state.go:17-29](), [app/server/model/plan/state.go:99-137]()

### Subscription and Real-Time Updates

```mermaid
graph TB
    subgraph "Subscription_System"
        SubscribePlan["SubscribePlan()"]
        GetActivePlan["GetActivePlan()"]
        Subscribe["activePlan.Subscribe(ctx)"]
        ReturnChannel["return id, chan string"]
    end
    
    subgraph "Update_Distribution"
        UpdateActive["UpdateActivePlan()"]
        SafeMapUpdate["activePlans.Update()"]
        StreamMessage["activePlan.Stream()"]
        AllSubscribers["Broadcast to all subscribers"]
    end
    
    subgraph "Cleanup_System"
        UnsubscribePlan["UnsubscribePlan()"]
        Unsubscribe["activePlan.Unsubscribe()"]
        ChannelClose["Close subscriber channel"]
    end
    
    SubscribePlan --> GetActivePlan
    GetActivePlan --> Subscribe
    Subscribe --> ReturnChannel
    
    UpdateActive --> SafeMapUpdate
    SafeMapUpdate --> StreamMessage
    StreamMessage --> AllSubscribers
    
    UnsubscribePlan --> Unsubscribe
    Unsubscribe --> ChannelClose
    
    style AllSubscribers fill:#9f9
```

The subscription system allows multiple clients to receive real-time updates from active plan execution through dedicated channels managed by the `ActivePlan` type.

Sources: [app/server/model/plan/state.go:143-174]()

## Data Serialization and Persistence

Plan configuration and model settings are stored as JSON in PostgreSQL using custom serialization interfaces.

### Plan Settings Storage

```mermaid
graph TB
    subgraph "PlanSettings_Structure"
        PlanSettings["PlanSettings struct"]
        ModelPackName["ModelPackName string"]
        ModelPack["ModelPack *ModelPack"]
        CustomModels["CustomModels []*CustomModel"]
        UpdatedAt["UpdatedAt time.Time"]
    end
    
    subgraph "Serialization_Interface"
        ScanMethod["Scan(interface{}) error"]
        ValueMethod["Value() (driver.Value, error)"]
        JSONMarshal["json.Marshal()"]
        JSONUnmarshal["json.Unmarshal()"]
    end
    
    subgraph "Configuration_Methods"
        Configure["Configure()"]
        GetModelPack["GetModelPack()"]
        SetModelPack["SetModelPackByName()"]
        DeepCopy["DeepCopy()"]
    end
    
    PlanSettings --> ModelPackName
    PlanSettings --> ModelPack
    PlanSettings --> CustomModels
    PlanSettings --> UpdatedAt
    
    PlanSettings --> ScanMethod
    PlanSettings --> ValueMethod
    ValueMethod --> JSONMarshal
    ScanMethod --> JSONUnmarshal
    
    PlanSettings --> Configure
    PlanSettings --> GetModelPack
    PlanSettings --> SetModelPack
    PlanSettings --> DeepCopy
    
    style JSONMarshal fill:#9f9
    style JSONUnmarshal fill:#9f9
```

The `PlanSettings` type implements PostgreSQL's `driver.Valuer` and `sql.Scanner` interfaces for seamless JSON serialization to database columns.

| Method | Purpose | Implementation |
|--------|---------|----------------|
| `Scan()` | Deserialize from database | JSON unmarshal from bytes/string |
| `Value()` | Serialize to database | JSON marshal to bytes |
| `Configure()` | Runtime configuration | Set custom models and providers |
| `DeepCopy()` | Safe copying | Full JSON round-trip |

Sources: [app/shared/plan_model_settings.go:86-103](), [app/shared/plan_model_settings.go:238-249]()

## Concurrency Control and Safety

The storage layer implements multiple levels of concurrency control to ensure data consistency during simultaneous plan operations.

### Multi-Level Locking Strategy

```mermaid
graph TB
    subgraph "Database_Level"
        TransactionIsolation["REPEATABLE READ"]
        RowLevelLocks["FOR UPDATE/SHARE"]
        DeadlockDetection["Deadlock detection"]
    end
    
    subgraph "Application_Level"
        RepoLocks["Repository locks table"]
        HeartbeatMechanism["Heartbeat validation"]
        ExpiredCleanup["Expired lock cleanup"]
    end
    
    subgraph "Git_Level"
        IndexLockHandling["index.lock removal"]
        AtomicOperations["Atomic git commands"]
        RetryOnConflict["Retry on lock conflicts"]
    end
    
    subgraph "Memory_Level"
        SafeMapOps["Thread-safe map operations"]
        ChannelSync["Channel synchronization"]
        ContextCancellation["Context-based cleanup"]
    end
    
    TransactionIsolation --> RowLevelLocks
    RowLevelLocks --> DeadlockDetection
    
    RepoLocks --> HeartbeatMechanism
    HeartbeatMechanism --> ExpiredCleanup
    
    IndexLockHandling --> AtomicOperations
    AtomicOperations --> RetryOnConflict
    
    SafeMapOps --> ChannelSync
    ChannelSync --> ContextCancellation
    
    style DeadlockDetection fill:#ffa
    style ExpiredCleanup fill:#ffa
```

This multi-layered approach ensures that concurrent operations can proceed safely at the database, application, Git, and memory levels without data corruption or deadlocks.

Sources: [app/server/db/locks.go:105-141](), [app/server/db/locks.go:552-562](), [app/server/db/git.go:655-684]()

---

# Page: Database Schema and Migrations

# Database Schema and Migrations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/server/db/db.go](app/server/db/db.go)
- [app/server/db/git.go](app/server/db/git.go)
- [app/server/db/locks.go](app/server/db/locks.go)
- [app/server/migrations/2024013000_plan_build_convo_ids.down.sql](app/server/migrations/2024013000_plan_build_convo_ids.down.sql)
- [app/server/migrations/2024013000_plan_build_convo_ids.up.sql](app/server/migrations/2024013000_plan_build_convo_ids.up.sql)
- [app/server/model/plan/state.go](app/server/model/plan/state.go)
- [app/server/model/plan/stop.go](app/server/model/plan/stop.go)
- [app/shared/plan_model_settings.go](app/shared/plan_model_settings.go)
- [releases/cli/versions/0.8.3.md](releases/cli/versions/0.8.3.md)
- [releases/server/versions/0.8.4.md](releases/server/versions/0.8.4.md)
- [releases/server/versions/2.1.3.md](releases/server/versions/2.1.3.md)

</details>



This document covers Plandex's data persistence layer, including the PostgreSQL database schema, file-based storage system, and migration management. It details the core database tables, their relationships, and how data flows between different storage systems.

For information about Git repository management and concurrency control, see [Repository Locking and Git Integration](#6.2). For user authentication and access control details, see [Authentication and User Management](#6.3).

## Database Architecture Overview

Plandex uses PostgreSQL as the primary database with specific connection management and timeout configurations handled by the `db.Connect()` function. The database is configured with strict timeouts and connection pooling for production environments.

**Database Connection Configuration**

The system establishes connections through `db.Conn` with the following parameters:
- `statement_timeout`: 30 seconds
- `lock_timeout`: 4 seconds  
- `idle_in_transaction_session_timeout`: 90 seconds
- Connection pooling: 50 max open connections (production), 10 (development)

```mermaid
graph TB
    subgraph "PostgreSQL Database Tables"
        auth_tokens["auth_tokens<br/>id, user_id, token_hash"]
        users["users<br/>id, name, email, domain"]
        orgs["orgs<br/>id, name, domain, owner_id"]
        org_users["org_users<br/>org_id, user_id, org_role_id"]
        projects["projects<br/>id, org_id, name"]
        plans["plans<br/>id, project_id, plan_config"]
        branches["branches<br/>id, plan_id, status, context_tokens"]
        plan_builds["plan_builds<br/>id, plan_id, convo_message_ids"]
        convo_summaries["convo_summaries<br/>id, plan_id, summary, tokens"]
        model_packs["model_packs<br/>id, org_id, planner, coder"]
        available_models["available_models<br/>id, provider, model_id"]
        repo_locks["repo_locks<br/>id, plan_id, scope, last_heartbeat_at"]
        lockable_plan_ids["lockable_plan_ids<br/>plan_id"]
    end
    
    subgraph "File Storage System"
        git_repos["Git Repositories<br/>getPlanDir(orgId, planId)"]
        context_files["Context Files<br/>JSON storage"]
        convo_files["Conversation Messages<br/>JSON storage"]
        result_files["Plan File Results<br/>JSON storage"]
    end
    
    subgraph "Connection Management"
        db_conn["db.Conn (*sqlx.DB)<br/>Connection pool"]
        migrations["migrate.NewWithDatabaseInstance<br/>Schema evolution"]
    end
    
    users --> org_users
    orgs --> org_users
    orgs --> projects
    projects --> plans
    plans --> branches
    plans --> repo_locks
    plans --> lockable_plan_ids
    
    db_conn --> auth_tokens
    db_conn --> users
    db_conn --> orgs
    migrations --> db_conn
    
    plans -.->|"File references"| git_repos
    git_repos --> context_files
    git_repos --> convo_files
    git_repos --> result_files
```

**Database vs File Storage Decision Matrix**

| Data Type | Storage | Timeout Sensitivity | Query Pattern |
|-----------|---------|-------------------|---------------|
| User authentication | PostgreSQL | High (4s lock timeout) | Frequent lookups |
| Plan status/metadata | PostgreSQL | Medium (30s statement) | Real-time updates |
| Conversation content | Files | Low | Sequential access |
| File build results | Files | Low | Version controlled |
| Repository locks | PostgreSQL | Critical (heartbeat every 3s) | Concurrency control |

Sources: [app/server/db/db.go:24-94](), [app/server/db/locks.go:27-32](), [app/server/db/git.go:37-40]()

## Core Database Tables

### User and Organization Management

The system uses a multi-tenant architecture with organizations containing users and projects.

```mermaid
erDiagram
    orgs {
        uuid id PK
        text name
        text domain
        boolean auto_add_domain_users
        uuid owner_id FK
        boolean is_trial
        timestamp created_at
        timestamp updated_at
    }
    
    users {
        uuid id PK
        text name
        text email
        text domain
        int num_non_draft_plans
        jsonb default_plan_config
        timestamp created_at
        timestamp updated_at
    }
    
    org_users {
        uuid id PK
        uuid org_id FK
        uuid user_id FK
        uuid org_role_id FK
        timestamp created_at
        timestamp updated_at
    }
    
    auth_tokens {
        uuid id PK
        uuid user_id FK
        text token_hash
        timestamp created_at
        timestamp deleted_at
    }
    
    invites {
        uuid id PK
        uuid org_id FK
        text email
        text name
        uuid inviter_id FK
        uuid invitee_id FK
        uuid org_role_id FK
        timestamp accepted_at
        timestamp created_at
        timestamp updated_at
    }
    
    orgs ||--o{ org_users : contains
    users ||--o{ org_users : member_of
    users ||--o{ auth_tokens : authenticated_by
    orgs ||--o{ invites : sends
    users ||--o{ invites : invited_by
    users ||--o{ invites : invited_user
```

**Key Database Entities:**
- `Org` struct maps to `orgs` table with trial status and domain-based auto-enrollment
- `User` struct maps to `users` table with plan count tracking for billing
- `AuthToken` provides session management with hashed token storage
- `OrgUser` manages many-to-many relationships between users and organizations

Sources: [app/server/db/data_models.go:24-109](), [app/shared/data_models.go:10-47]()

### Project and Plan Management

Projects contain plans, which have branches for parallel development workflows.

```mermaid
erDiagram
    projects {
        uuid id PK
        uuid org_id FK
        text name
        timestamp created_at
        timestamp updated_at
    }
    
    plans {
        uuid id PK
        uuid org_id FK
        uuid owner_id FK
        uuid project_id FK
        text name
        timestamp shared_with_org_at
        int total_replies
        int active_branches
        jsonb plan_config
        timestamp archived_at
        timestamp created_at
        timestamp updated_at
    }
    
    branches {
        uuid id PK
        uuid org_id FK
        uuid owner_id FK
        uuid plan_id FK
        uuid parent_branch_id FK
        text name
        enum status
        text error
        int context_tokens
        int convo_tokens
        timestamp shared_with_org_at
        timestamp archived_at
        timestamp created_at
        timestamp updated_at
        timestamp deleted_at
    }
    
    convo_summaries {
        uuid id PK
        uuid org_id FK
        uuid plan_id FK
        uuid latest_convo_message_id
        timestamp latest_convo_message_created_at
        text summary
        int tokens
        int num_messages
        timestamp created_at
    }
    
    plan_builds {
        uuid id PK
        uuid org_id FK
        uuid plan_id FK
        uuid convo_message_id FK
        text file_path
        text error
        timestamp created_at
        timestamp updated_at
    }
    
    projects ||--o{ plans : contains
    plans ||--o{ branches : has_branches
    plans ||--o{ convo_summaries : summarized_by
    plans ||--o{ plan_builds : built_by
    branches ||--o{ branches : parent_child
```

**Plan Status Enumeration:**
The `branches.status` field uses the `PlanStatus` enum to track execution state:
- Planning, building, applying phases
- Error and stopped states
- Completion status

Sources: [app/server/db/data_models.go:111-236](), [app/shared/data_models.go:54-81]()

### AI Model Configuration

Model management supports multiple AI providers with role-based configurations.

```mermaid
erDiagram
    model_packs {
        uuid id PK
        uuid org_id FK
        text name
        text description
        jsonb planner
        jsonb coder
        jsonb plan_summary
        jsonb builder
        jsonb whole_file_builder
        jsonb namer
        jsonb commit_msg
        jsonb exec_status
        jsonb context_loader
        timestamp created_at
        timestamp updated_at
    }
    
    available_models {
        uuid id PK
        uuid org_id FK
        enum provider
        text custom_provider
        text base_url
        text model_id
        text model_name
        text description
        int max_tokens
        text api_key_env_var
        int default_max_convo_tokens
        int max_output_tokens
        int reserved_output_tokens
        boolean has_image_support
        enum preferred_output_format
        timestamp created_at
        timestamp updated_at
    }
    
    model_packs ||--o{ available_models : uses
```

**Model Role Configuration:**
Each `ModelPack` contains role-specific configurations stored as JSONB:
- `planner`: Task breakdown and planning
- `coder`: Code generation and modification  
- `builder`: Syntax validation and building
- `namer`: File and commit naming
- `architect`: Context loading and analysis

Sources: [app/server/db/data_models.go:298-374](), [app/shared/data_models.go:308-327]()

## File-based Storage System

Large content is stored in files within the plan's Git repository to enable version control and efficient handling of code and conversation data.

### File Storage Structure

```mermaid
graph TD
    PlanRepo["Plan Repository<br/>Git-managed per plan"]
    
    subgraph "File Storage Locations"
        ContextFiles["contexts/<br/>Context metadata & content"]
        ConvoFiles["conversations/<br/>Message history JSON"]
        ResultFiles["results/<br/>File modification results"]
        ApplyFiles["applies/<br/>Application records"]
    end
    
    subgraph "Database References"
        PlanTable["plans table<br/>Metadata only"]
        BranchTable["branches table<br/>State tracking"]
        BuildTable["plan_builds table<br/>Build status"]
    end
    
    PlanRepo --> ContextFiles
    PlanRepo --> ConvoFiles  
    PlanRepo --> ResultFiles
    PlanRepo --> ApplyFiles
    
    PlanTable -.->|"References files by ID"| ContextFiles
    BranchTable -.->|"References files by ID"| ConvoFiles
    BuildTable -.->|"References files by path"| ResultFiles
```

**File-stored Entity Examples:**

| Entity | Storage Pattern | Content Type |
|--------|----------------|--------------|
| `Context` | `contexts/{contextId}.json` | File content, metadata, tokens |
| `ConvoMessage` | `conversations/{messageId}.json` | AI conversations, flags, subtasks |
| `PlanFileResult` | `results/{resultId}.json` | Generated code, replacements |
| `ConvoMessageDescription` | `descriptions/{descId}.json` | Operation summaries, commit messages |

**Dual Storage Pattern:**
The system uses a dual storage pattern where:
1. Database stores metadata, relationships, and frequently-queried fields
2. Files store large content that's accessed less frequently
3. Both share the same struct definitions with `ToApi()` methods for client serialization

Sources: [app/server/db/data_models.go:387-626](), [app/shared/data_models.go:97-299]()

## Migration System

Plandex implements database schema migrations using the `golang-migrate` library with PostgreSQL driver integration. The migration system is managed through `db.MigrationsUp()` and `db.migrationsUp()` functions.

### Migration Infrastructure

```mermaid
graph TB
    subgraph "Migration Management Functions"
        MigrationsUp["db.MigrationsUp()<br/>Entry point"]
        migrationsUp["db.migrationsUp(dir)<br/>Core logic"]
        postgres_driver["postgres.WithInstance(Conn.DB)<br/>Database driver"]
        migrate_instance["migrate.NewWithDatabaseInstance<br/>Migration engine"]
    end
    
    subgraph "Migration Directory Structure"
        migrations_dir["migrations/ directory<br/>MIGRATIONS_DIR env var"]
        up_files["*.up.sql files<br/>Forward migrations"]
        down_files["*.down.sql files<br/>Rollback migrations"]
    end
    
    subgraph "Migration Execution Flow"
        force_version["m.Force(version)<br/>Development reset"]
        run_down["m.Down()<br/>Database reset"]
        run_steps["m.Steps(-n)<br/>Selective rollback"]
        run_up["m.Up()<br/>Apply pending"]
    end
    
    MigrationsUp --> migrationsUp
    migrationsUp --> postgres_driver
    postgres_driver --> migrate_instance
    migrate_instance --> migrations_dir
    
    migrations_dir --> up_files
    migrations_dir --> down_files
    
    migrate_instance --> force_version
    migrate_instance --> run_down
    migrate_instance --> run_steps
    migrate_instance --> run_up
```

**Migration Configuration and Safety Features**

The migration system includes several safety mechanisms:
- Development-only forced migration states for recovery
- Conditional down migrations (commented out by default)
- Error handling for `migrate.ErrNoChange` (no pending migrations)
- Automatic directory resolution via `MIGRATIONS_DIR` environment variable

**Migration File Naming Convention**: `YYYYMMDDNN_description.{up|down}.sql`

### Schema Evolution Example - Plan Build Conversation IDs

The `2024013000_plan_build_convo_ids` migration demonstrates the transformation from single conversation message tracking to multiple message support:

```sql
-- Up: Enable multiple conversation messages per build
ALTER TABLE plan_builds
  RENAME COLUMN convo_message_id TO convo_message_ids;

ALTER TABLE plan_builds
  ALTER COLUMN convo_message_ids TYPE UUID[] USING ARRAY[convo_message_ids];
```

```sql
-- Down: Revert to single conversation message  
ALTER TABLE plan_builds
  RENAME COLUMN convo_message_ids TO convo_message_id;

ALTER TABLE plan_builds
  ALTER COLUMN convo_message_id TYPE UUID USING (convo_message_id[1]);
```

This schema change enables the `PlanBuild` struct to reference multiple `ConvoMessage` entities, supporting complex AI conversation flows where builds span multiple interactions.

Sources: [app/server/db/db.go:96-175](), [app/server/migrations/2024013000_plan_build_convo_ids.up.sql:1-6](), [app/server/migrations/2024013000_plan_build_convo_ids.down.sql:1-5]()

## Data Access Patterns

The system implements a layered data access pattern with clear separation between database operations and file operations.

```mermaid
graph TB
    subgraph "Client Layer"
        CLICommands["CLI Commands<br/>plandex tell, build, apply"]
        APIClient["API Client<br/>authenticatedFastClient"]
    end
    
    subgraph "Server Layer"  
        HTTPHandlers["HTTP Handlers<br/>POST /plans/{id}/{branch}/tell"]
        BusinessLogic["Business Logic<br/>plan execution engine"]
        DataAccess["Data Access Layer"]
    end
    
    subgraph "Storage Layer"
        DBOperations["Database Operations<br/>CRUD on metadata"]
        FileOperations["File Operations<br/>JSON read/write"]
        GitOperations["Git Operations<br/>Version control"]
    end
    
    CLICommands --> APIClient
    APIClient --> HTTPHandlers
    HTTPHandlers --> BusinessLogic
    BusinessLogic --> DataAccess
    
    DataAccess --> DBOperations
    DataAccess --> FileOperations  
    DataAccess --> GitOperations
    
    DBOperations -.->|"Fast queries"| PostgreSQL[(PostgreSQL)]
    FileOperations -.->|"Large content"| FileSystem[(File System)]
    GitOperations -.->|"Version history"| GitRepos[(Git Repos)]
```

**Transaction Boundaries:**
- Database transactions for metadata consistency
- File operations within Git transactions for atomicity  
- Cross-system consistency through careful ordering of operations
- Repository locking prevents concurrent modifications

**Query Patterns:**
- Metadata queries hit PostgreSQL for fast access
- Content loading reads from files only when needed
- API responses use `ToApi()` methods to transform database models to client models
- Streaming operations bypass database for real-time updates

Sources: [app/cli/api/methods.go:1-1200](), [app/server/db/data_models.go:36-625](), [app/shared/data_models.go:1-399]()

---

# Page: Repository Locking and Git Integration

# Repository Locking and Git Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/server/db/db.go](app/server/db/db.go)
- [app/server/db/git.go](app/server/db/git.go)
- [app/server/db/locks.go](app/server/db/locks.go)
- [app/server/model/plan/state.go](app/server/model/plan/state.go)
- [app/server/model/plan/stop.go](app/server/model/plan/stop.go)
- [app/shared/plan_model_settings.go](app/shared/plan_model_settings.go)
- [releases/cli/versions/0.8.3.md](releases/cli/versions/0.8.3.md)
- [releases/server/versions/0.8.4.md](releases/server/versions/0.8.4.md)
- [releases/server/versions/2.1.3.md](releases/server/versions/2.1.3.md)

</details>



This document covers Plandex's repository locking system and Git integration, which provides concurrency control for plan execution and manages Git operations across multiple plans and branches. This system ensures that only one operation can modify a repository at a time while allowing multiple read operations under specific conditions.

For information about plan execution workflow, see [Plan Execution System](#3). For database schema details, see [Database Schema and Migrations](#6.1).

## Lock Management System

Plandex implements a sophisticated database-backed locking system that coordinates access to Git repositories across multiple concurrent plan executions. The system uses PostgreSQL's row-level locking combined with application-level heartbeat monitoring.

### Lock Types and Scopes

The locking system supports two primary lock scopes defined in the `LockScope` type:

| Lock Scope | Purpose | Conflicts With |
|------------|---------|----------------|
| `LockScopeRead` | Repository read operations, branch checkout | Write locks, read locks on different branches |
| `LockScopeWrite` | Repository modifications, commits | All other locks (read and write) |

Read locks allow multiple concurrent operations on the same branch but prevent branch switching during execution. Write locks provide exclusive access for repository modifications.

```mermaid
graph TD
    subgraph "Lock Request Processing"
        LockRequest["Lock Request"] --> LockParams["LockRepoParams"]
        LockParams --> ValidateParams["Validate Parameters"]
        ValidateParams --> StartTx["Begin Transaction"]
        StartTx --> SelectLockableId["SELECT lockable_plan_ids FOR UPDATE/SHARE"]
        SelectLockableId --> QueryExisting["Query Existing Locks"]
    end
    
    subgraph "Lock Conflict Resolution"
        QueryExisting --> CheckExpired["Check Expired Locks"]
        CheckExpired --> DeleteExpired["DELETE Expired Locks"]
        DeleteExpired --> EvaluateConflicts["Evaluate Lock Conflicts"]
        EvaluateConflicts --> CanAcquire{"Can Acquire Lock?"}
        CanAcquire -->|No| RetryWithBackoff["Exponential Backoff Retry"]
        RetryWithBackoff --> LockRequest
        CanAcquire -->|Yes| InsertLock["INSERT New Lock"]
    end
    
    subgraph "Lock Maintenance"
        InsertLock --> CommitTx["Commit Transaction"]
        CommitTx --> StartHeartbeat["Start Heartbeat Goroutine"]
        StartHeartbeat --> HeartbeatLoop["UPDATE last_heartbeat_at"]
        HeartbeatLoop --> CheckContext["Check Context Cancellation"]
        CheckContext --> HeartbeatLoop
    end
    
    subgraph "Git Operations"
        CommitTx --> RemoveIndexLock["gitRemoveIndexLockFileIfExists"]
        RemoveIndexLock --> CheckoutBranch["gitCheckoutBranch"]
        CheckoutBranch --> ReturnLockId["Return Lock ID"]
    end
```

*Sources: [app/server/db/locks.go:41-52](), [app/server/db/locks.go:54-478]()*

### Lock Acquisition Process

The `lockRepoDB` function implements the core lock acquisition logic with retry mechanisms and deadlock handling:

```mermaid
graph TD
    subgraph "Lock Parameters"
        LRP["LockRepoParams"] --> OrgId["OrgId"]
        LRP --> UserId["UserId"] 
        LRP --> PlanId["PlanId"]
        LRP --> Branch["Branch"]
        LRP --> Scope["LockScope (read/write)"]
        LRP --> PlanBuildId["PlanBuildId"]
        LRP --> Context["context.Context"]
        LRP --> Reason["Reason (debugging)"]
    end
    
    subgraph "Transaction Management"
        BeginTx["Conn.BeginTxx(RepeatableRead)"] --> LockableQuery["SELECT * FROM lockable_plan_ids"]
        LockableQuery --> ExistingQuery["SELECT * FROM repo_locks"]
        ExistingQuery --> ProcessLocks["Process Existing Locks"]
    end
    
    subgraph "Conflict Detection"
        ProcessLocks --> CheckExpiry["Check Heartbeat Timeout"]
        CheckExpiry --> ExpiredIds["Collect Expired Lock IDs"]
        ExpiredIds --> DeleteExpired["DELETE expired locks"]
        DeleteExpired --> EvaluateConflict["Evaluate Lock Conflicts"]
    end
    
    subgraph "Lock Insertion"
        EvaluateConflict --> InsertNewLock["INSERT INTO repo_locks ON CONFLICT DO NOTHING"]
        InsertNewLock --> CheckInserted["Check RETURNING id"]
        CheckInserted --> CommitTransaction["tx.Commit()"]
        CommitTransaction --> UpdateActiveLocks["activeLockIds[id] = true"]
    end
```

*Sources: [app/server/db/locks.go:54-478](), [app/server/db/locks.go:249-290]()*

### Heartbeat Mechanism

Each acquired lock starts a heartbeat goroutine that periodically updates the `last_heartbeat_at` timestamp to prove the lock holder is still active:

```mermaid
graph LR
    subgraph "Heartbeat Lifecycle"
        StartGoroutine["Start Heartbeat Goroutine"] --> HeartbeatInterval["Wait lockHeartbeatInterval (3s)"]
        HeartbeatInterval --> UpdateHeartbeat["UPDATE repo_locks SET last_heartbeat_at = NOW()"]
        UpdateHeartbeat --> CheckErrors["Check for Errors"]
        CheckErrors --> CheckRowsAffected["Check RowsAffected"]
        CheckRowsAffected --> ContinueLoop["Continue Loop"]
        ContinueLoop --> HeartbeatInterval
        
        CheckErrors -->|"Too Many Errors"| CancelContext["Cancel Context"]
        CheckRowsAffected -->|"0 Rows"| LockNotFound["Lock Not Found - Exit"]
        UpdateHeartbeat -->|"Context Cancelled"| ExitGoroutine["Exit Goroutine"]
    end
    
    subgraph "Constants"
        Constants["lockHeartbeatInterval: 3s<br/>lockHeartbeatTimeout: 60s<br/>maxLockRetries: 6"]
    end
```

*Sources: [app/server/db/locks.go:27-32](), [app/server/db/locks.go:387-457]()*

## Git Integration Architecture

The Git integration system provides repository management capabilities with automatic lock file handling and retry mechanisms for Git operations.

### GitRepo Structure and Operations

The `GitRepo` struct encapsulates Git operations for a specific organization and plan:

```mermaid
graph TD
    subgraph "GitRepo Operations"
        GitRepo["GitRepo{orgId, planId}"] --> AddCommit["GitAddAndCommit(branch, message)"]
        GitRepo --> RewindSha["GitRewindToSha(branch, sha)"]
        GitRepo --> ResetSha["GitResetToSha(sha)"]
        GitRepo --> CheckoutSha["GitCheckoutSha(sha)"]
        GitRepo --> GetHistory["GetGitCommitHistory(branch)"]
        GitRepo --> ListBranches["GitListBranches()"]
        GitRepo --> CreateBranch["GitCreateBranch(newBranch)"]
        GitRepo --> DeleteBranch["GitDeleteBranch(branchName)"]
        GitRepo --> ClearChanges["GitClearUncommittedChanges(branch)"]
        GitRepo --> CheckoutBranch["GitCheckoutBranch(branch)"]
    end
    
    subgraph "Low-Level Git Commands"
        AddCommit --> gitAdd["gitAdd(repoDir, path)"]
        AddCommit --> gitCommit["gitCommit(repoDir, commitMsg)"]
        RewindSha --> gitRewindToSha["gitRewindToSha(repoDir, sha)"]
        CheckoutBranch --> gitCheckoutBranch["gitCheckoutBranch(repoDir, branch)"]
    end
    
    subgraph "Lock File Management"
        gitAdd --> RemoveLocks["gitRemoveIndexLockFileIfExists()"]
        gitCommit --> RemoveLocks
        gitCheckoutBranch --> RemoveLocks
        RemoveLocks --> IndexLock["Remove .git/index.lock"]
        RemoveLocks --> HeadLock["Remove .git/HEAD.lock"] 
        RemoveLocks --> RefsLock["Remove .git/refs/heads/HEAD.lock"]
    end
```

*Sources: [app/server/db/git.go:32-65](), [app/server/db/git.go:67-400](), [app/server/db/git.go:604-644]()*

### Git Write Operations with Retry Logic

All Git write operations are wrapped with `gitWriteOperation` which provides exponential backoff retry logic for lock file conflicts:

```mermaid
sequenceDiagram
    participant Client as "Git Operation"
    participant Wrapper as "gitWriteOperation"
    participant Git as "Git Command"
    participant FS as "File System"

    Client->>Wrapper: Call Git Operation
    Wrapper->>Git: Execute Git Command
    Git-->>Wrapper: Lock File Error
    Wrapper->>FS: gitRemoveIndexLockFileIfExists()
    FS->>Wrapper: Lock Files Removed
    Wrapper->>Wrapper: Exponential Backoff Delay
    Wrapper->>Git: Retry Git Command
    Git-->>Wrapper: Success
    Wrapper->>Client: Operation Complete
    
    Note over Wrapper: maxGitRetries: 5<br/>baseGitRetryDelay: 100ms<br/>Exponential backoff: 2^attempt
```

*Sources: [app/server/db/git.go:655-684](), [app/server/db/git.go:19-22]()*

## Repository Lock Integration with Plan Execution

The locking system integrates with the plan execution engine through the `ExecRepoOperation` wrapper function, which provides a standardized interface for executing Git operations with proper locking.

### ExecRepoOperation Workflow

```mermaid
graph TD
    subgraph "Plan Execution Context"
        ExecRequest["ExecRepoOperationParams"] --> LockAcquisition["LockRepo(params)"]
        LockAcquisition --> GetRepo["getGitRepo(orgId, planId)"]
        GetRepo --> ExecuteOp["operation(repo)"]
        ExecuteOp --> ReleaseLock["deleteRepoLockDB(lockId)"]
    end
    
    subgraph "Lock Parameters"
        ExecParams["ExecRepoOperationParams"] --> ExecOrgId["OrgId"]
        ExecParams --> ExecUserId["UserId"]
        ExecParams --> ExecPlanId["PlanId"] 
        ExecParams --> ExecBranch["Branch"]
        ExecParams --> ExecScope["LockScope"]
        ExecParams --> ExecCtx["Context"]
        ExecParams --> ExecReason["Reason"]
    end
    
    subgraph "Error Handling"
        ExecuteOp -->|Error| ErrorLogging["Log Operation Error"]
        ReleaseLock -->|Error| LockReleaseError["Log Lock Release Error"]
        ErrorLogging --> CleanupAttempt["Attempt Lock Cleanup"]
        CleanupAttempt --> ReturnError["Return Original Error"]
    end
```

*Sources: [app/server/model/plan/state.go:113-128](), [app/server/db/locks.go:42-52]()*

### Active Plan Integration

Active plans use the locking system to coordinate Git operations during plan execution and cleanup:

```mermaid
graph TD
    subgraph "Active Plan Lifecycle"
        CreatePlan["CreateActivePlan()"] --> PlanExecution["Plan Execution"]
        PlanExecution --> StreamDone["<-activePlan.StreamDoneCh"]
        StreamDone --> DeletePlan["DeleteActivePlan()"]
        DeletePlan --> ClearChanges["GitClearUncommittedChanges()"]
    end
    
    subgraph "Lock Usage in Plans"
        ClearChanges --> ExecRepoOp["ExecRepoOperation()"]
        ExecRepoOp --> AcquireWriteLock["LockScope: Write"]
        AcquireWriteLock --> GitReset["git reset --hard"]
        AcquireWriteLock --> GitClean["git clean -d -f"]
        GitReset --> ReleaseLock["Release Lock"]
        GitClean --> ReleaseLock
    end
    
    subgraph "Cleanup Context"
        DeletePlan --> TimeoutCtx["context.WithTimeout(10s)"]
        TimeoutCtx --> ExecRepoOp
        ReleaseLock --> PlanDeleted["Plan Deleted from activePlans"]
    end
```

*Sources: [app/server/model/plan/state.go:99-137](), [app/server/db/git.go:333-383]()*

## Concurrency Control and Error Handling

The system implements multiple layers of concurrency control to handle race conditions, deadlocks, and system failures.

### Lock Conflict Resolution

```mermaid
graph TD
    subgraph "Read Lock Conflicts"
        ReadRequest["Read Lock Request"] --> ExistingReads["Check Existing Read Locks"]
        ExistingReads --> SameBranch{"Same Branch?"}
        SameBranch -->|Yes| AllowRead["Allow Read Lock"]
        SameBranch -->|No| DenyRead["Deny - Branch Conflict"]
        ExistingReads --> ExistingWrites["Check Existing Write Locks"]
        ExistingWrites --> DenyWrite["Deny - Write Lock Exists"]
    end
    
    subgraph "Write Lock Conflicts"
        WriteRequest["Write Lock Request"] --> AnyExisting{"Any Existing Locks?"}
        AnyExisting -->|Yes| DenyWriteLock["Deny - Exclusive Access Required"]
        AnyExisting -->|No| AllowWrite["Allow Write Lock"]
    end
    
    subgraph "Retry Logic"
        DenyRead --> ExponentialBackoff["Exponential Backoff"]
        DenyWrite --> ExponentialBackoff
        DenyWriteLock --> ExponentialBackoff
        ExponentialBackoff --> RetryAttempt["Retry Lock Acquisition"]
        RetryAttempt --> MaxRetries{"Max Retries?"}
        MaxRetries -->|No| ReadRequest
        MaxRetries -->|Yes| LockFailed["Lock Acquisition Failed"]
    end
```

*Sources: [app/server/db/locks.go:249-290](), [app/server/db/locks.go:564-598]()*

### Deadlock Detection and Recovery

The system includes deadlock detection for PostgreSQL serialization conflicts and Git lock file issues:

```mermaid
graph LR
    subgraph "Deadlock Handling"
        PostgresError["PostgreSQL Error"] --> CheckErrorCode["Check Error Code"]
        CheckErrorCode --> IsDeadlock{"Code 40001/40P01?"}
        IsDeadlock -->|Yes| LogDeadlock["Log Deadlock"]
        IsDeadlock -->|No| RegularError["Handle Regular Error"]
        LogDeadlock --> ContinueOperation["Continue Operation"]
        
        GitLockError["Git Lock File Error"] --> DetectLockFile["Detect index.lock/HEAD.lock"]
        DetectLockFile --> RemoveLockFiles["removeLockFile()"]
        RemoveLockFiles --> RetryGitOp["Retry Git Operation"]
    end
    
    subgraph "Cleanup Operations"
        ActiveLockCleanup["CleanupActiveLocks()"] --> BeginCleanupTx["Begin Transaction"]
        BeginCleanupTx --> DeleteAllLocks["DELETE FROM repo_locks WHERE id = ANY(activeLockIds)"]
        DeleteAllLocks --> CommitCleanup["Commit"]
        CommitCleanup --> ClearActiveLocks["Clear activeLockIds map"]
    end
```

*Sources: [app/server/db/locks.go:552-562](), [app/server/db/locks.go:613-668](), [app/server/db/git.go:557-602]()*

### Lock Release and Cleanup

Lock cleanup happens through multiple mechanisms to ensure system reliability:

| Cleanup Trigger | Mechanism | Implementation |
|-----------------|-----------|----------------|
| Normal completion | `deleteRepoLockDB()` | Explicit lock release with retry |
| Context cancellation | Heartbeat goroutine exit | Automatic timeout detection |
| Server shutdown | `CleanupActiveLocks()` | Bulk cleanup of all active locks |
| Lock expiry | Heartbeat timeout | Automatic removal during lock acquisition |

```mermaid
graph TD
    subgraph "Lock Release Mechanisms"
        NormalRelease["deleteRepoLockDB(id)"] --> DeleteQuery["DELETE FROM repo_locks WHERE id = $1"]
        DeleteQuery --> CheckRows["Check RowsAffected"]
        CheckRows --> UpdateMap["delete(activeLockIds, id)"]
        
        HeartbeatTimeout["Heartbeat Timeout"] --> ExpiredDetection["now.Sub(lastHeartbeat) > 60s"]
        ExpiredDetection --> BulkDelete["DELETE WHERE id = ANY(expiredIds)"]
        
        ShutdownCleanup["Server Shutdown"] --> CleanupActive["CleanupActiveLocks()"]
        CleanupActive --> BulkDeleteAll["DELETE WHERE id = ANY(activeLockIds)"]
    end
```

*Sources: [app/server/db/locks.go:480-521](), [app/server/db/locks.go:215-247](), [app/server/db/locks.go:613-668]()*

---

# Page: Authentication and User Management

# Authentication and User Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/cli/api/clients.go](app/cli/api/clients.go)
- [app/cli/api/methods.go](app/cli/api/methods.go)
- [app/cli/types/api.go](app/cli/types/api.go)
- [app/server/db/data_models.go](app/server/db/data_models.go)
- [app/server/db/user_helpers.go](app/server/db/user_helpers.go)
- [app/server/handlers/sessions.go](app/server/handlers/sessions.go)
- [app/server/main.go](app/server/main.go)
- [app/server/routes/routes.go](app/server/routes/routes.go)
- [app/server/setup/setup.go](app/server/setup/setup.go)
- [app/shared/data_models.go](app/shared/data_models.go)
- [app/shared/req_res.go](app/shared/req_res.go)

</details>



This document covers Plandex's authentication and user management system, including user registration, login/logout flows, session management, organization membership, role-based access control, and invitation workflows. For information about data storage and database schema, see [Database Schema and Migrations](#6.1).

## System Architecture Overview

**Authentication and Authorization Flow**

```mermaid
graph TB
    subgraph "Client Layer"
        CLI["CLI Client"]
        UIClient["UI Client"]
        ApiClient["API Client Layer"]
    end
    
    subgraph "Authentication Transport"
        AuthTransport["authenticatedTransport"]
        UnauthTransport["unauthenticatedTransport"]
        AuthHeader["Authorization Headers"]
    end
    
    subgraph "Server Authentication"
        EmailVerify["CreateEmailVerificationHandler"]
        SignIn["SignInHandler"]
        SignOut["SignOutHandler"]
        SignInCode["CreateSignInCodeHandler"]
        Authenticate["Authenticate Middleware"]
    end
    
    subgraph "Session Management"
        AuthToken["AuthToken Table"]
        EmailVerifications["email_verifications Table"]
        SignInCodes["sign_in_codes Table"]
    end
    
    subgraph "User & Organization Management"
        UserHandler["User Handlers"]
        OrgHandler["Organization Handlers"]
        InviteHandler["Invitation Handlers"]
        RoleHandler["Role Handlers"]
    end
    
    subgraph "Database Layer"
        Users["users Table"]
        Orgs["orgs Table"]
        OrgUsers["orgs_users Table"]
        OrgRoles["org_roles Table"]
        Invites["invites Table"]
    end
    
    CLI --> ApiClient
    UIClient --> ApiClient
    ApiClient --> AuthTransport
    ApiClient --> UnauthTransport
    
    AuthTransport --> AuthHeader
    UnauthTransport --> EmailVerify
    AuthHeader --> Authenticate
    
    Authenticate --> SignIn
    Authenticate --> SignOut
    Authenticate --> SignInCode
    
    SignIn --> AuthToken
    EmailVerify --> EmailVerifications
    SignInCode --> SignInCodes
    
    Authenticate --> UserHandler
    Authenticate --> OrgHandler
    Authenticate --> InviteHandler
    Authenticate --> RoleHandler
    
    UserHandler --> Users
    OrgHandler --> Orgs
    InviteHandler --> Invites
    RoleHandler --> OrgRoles
    OrgHandler --> OrgUsers
    
    style Authenticate fill:#fff3e0
    style AuthToken fill:#e8f5e8
    style Users fill:#e1f5fe
```

Sources: [app/cli/api/clients.go:44-64](), [app/server/routes/routes.go:89-190](), [app/server/handlers/sessions.go:1-347](), [app/server/db/data_models.go:19-261]()

## Core Data Models

**User and Organization Relationship Model**

```mermaid
erDiagram
    User {
        string id PK
        string name
        string email UK
        string domain
        int num_non_draft_plans
        PlanConfig default_plan_config
        timestamp created_at
        timestamp updated_at
    }
    
    Org {
        string id PK
        string name
        string domain
        bool auto_add_domain_users
        string owner_id FK
        bool is_trial
        timestamp created_at
        timestamp updated_at
    }
    
    OrgUser {
        string id PK
        string org_id FK
        string user_id FK
        string org_role_id FK
        OrgUserConfig config
        timestamp created_at
        timestamp updated_at
    }
    
    OrgRole {
        string id PK
        string org_id FK
        string name
        string label
        string description
        timestamp created_at
        timestamp updated_at
    }
    
    Invite {
        string id PK
        string org_id FK
        string email
        string name
        string inviter_id FK
        string invitee_id FK
        string org_role_id FK
        timestamp accepted_at
        timestamp created_at
        timestamp updated_at
    }
    
    AuthToken {
        string id PK
        string user_id FK
        string token_hash
        timestamp created_at
        timestamp deleted_at
    }
    
    User ||--o{ OrgUser : "belongs to orgs"
    Org ||--o{ OrgUser : "has members"
    OrgRole ||--o{ OrgUser : "assigns role"
    Org ||--o{ OrgRole : "defines roles"
    User ||--o{ Invite : "invites others"
    User ||--o{ Invite : "receives invites"
    Org ||--o{ Invite : "org invitations"
    OrgRole ||--o{ Invite : "role assignment"
    User ||--o{ AuthToken : "authentication"
    User ||--|| Org : "owns"
```

Sources: [app/shared/data_models.go:21-49](), [app/server/db/data_models.go:48-261]()

### Key Data Structures

| Model | Purpose | Key Fields |
|-------|---------|------------|
| `User` | Core user identity | `email`, `domain`, `name`, `default_plan_config` |
| `Org` | Organization/workspace | `name`, `auto_add_domain_users`, `is_trial`, `owner_id` |
| `OrgUser` | User-organization membership | `user_id`, `org_id`, `org_role_id`, `config` |
| `OrgRole` | Role-based permissions | `name`, `label`, `description` |
| `Invite` | Pending invitations | `email`, `inviter_id`, `invitee_id`, `accepted_at` |
| `AuthToken` | Session authentication | `user_id`, `token_hash`, `deleted_at` |

Sources: [app/shared/data_models.go:10-50](), [app/server/db/data_models.go:27-261]()

## Authentication Flow

**Email-Based Authentication Process**

```mermaid
sequenceDiagram
    participant Client
    participant CreateEmailVerificationHandler
    participant EmailService
    participant CheckEmailPinHandler
    participant SignInHandler
    participant Database
    
    Client->>CreateEmailVerificationHandler: POST /accounts/email_verifications
    CreateEmailVerificationHandler->>Database: Check if user exists
    CreateEmailVerificationHandler->>Database: Create email verification with PIN hash
    CreateEmailVerificationHandler->>EmailService: Send verification email with PIN
    CreateEmailVerificationHandler->>Client: Response with hasAccount status
    
    Client->>CheckEmailPinHandler: POST /accounts/email_verifications/check_pin
    CheckEmailPinHandler->>Database: Validate PIN against hash
    CheckEmailPinHandler->>Client: PIN validation result
    
    Client->>SignInHandler: POST /accounts/sign_in
    SignInHandler->>Database: ValidateAndSignIn()
    Database->>Database: Create auth token
    SignInHandler->>Client: SessionResponse with token and orgs
```

Sources: [app/server/handlers/sessions.go:18-136](), [app/server/handlers/sessions.go:138-172](), [app/server/handlers/sessions.go:211-250]()

### Authentication Components

The authentication system uses several key components:

- **Email Verification**: PIN-based email verification using SHA256 hashing ([app/server/handlers/sessions.go:86-113]())
- **Authentication Tokens**: Server-side token management with hash storage ([app/server/db/data_models.go:19-25]())
- **Transport Layer**: Client-side automatic token injection via `authenticatedTransport` ([app/cli/api/clients.go:44-55]())
- **Session Management**: Token-based sessions with organization context ([app/shared/req_res.go:44-51]())

### Sign-in Code Flow

For cross-client authentication (e.g., UI to CLI), Plandex implements a sign-in code system:

```mermaid
graph LR
    AuthenticatedClient["Authenticated Client"]
    CreateSignInCodeHandler["CreateSignInCodeHandler"]
    UnauthenticatedClient["Unauthenticated Client"]
    SignInHandler["SignInHandler"]
    
    AuthenticatedClient -->|"POST /accounts/sign_in_codes"| CreateSignInCodeHandler
    CreateSignInCodeHandler -->|"6-digit PIN"| AuthenticatedClient
    AuthenticatedClient -->|"Share PIN"| UnauthenticatedClient
    UnauthenticatedClient -->|"POST /accounts/sign_in with PIN"| SignInHandler
    SignInHandler -->|"SessionResponse"| UnauthenticatedClient
```

Sources: [app/server/handlers/sessions.go:176-209](), [app/shared/req_res.go:27-31]()

## Authorization and Role Management

**Organization Role System**

```mermaid
graph TB
    subgraph "Role Management Endpoints"
        ListOrgRoles["/orgs/roles - ListOrgRolesHandler"]
        ListUsers["/users - ListUsersHandler"]
        DeleteUser["/orgs/users/{userId} - DeleteOrgUserHandler"]
    end
    
    subgraph "Database Operations"
        GetOrgRoles["db.ListOrgRoles()"]
        GetOrgUsers["db.ListOrgUsers()"]
        GetUsers["db.ListUsers()"]
        NumUsersWithRole["db.NumUsersWithRole()"]
    end
    
    subgraph "Data Storage"
        OrgRolesTable["org_roles Table"]
        OrgUsersTable["orgs_users Table"]
        UsersTable["users Table"]
    end
    
    ListOrgRoles --> GetOrgRoles
    ListUsers --> GetOrgUsers
    ListUsers --> GetUsers
    DeleteUser --> NumUsersWithRole
    
    GetOrgRoles --> OrgRolesTable
    GetOrgUsers --> OrgUsersTable
    GetUsers --> UsersTable
    NumUsersWithRole --> OrgUsersTable
```

Sources: [app/server/routes/routes.go:103-105](), [app/server/db/user_helpers.go:98-166]()

### Organization User Configuration

Each organization membership includes configuration through `OrgUserConfig`:

- **Config Storage**: JSON configuration stored in `orgs_users.config` column ([app/server/db/data_models.go:102]())
- **Retrieval**: `GetOrgUserConfigHandler` endpoint at `/org_user_config` ([app/server/handlers/sessions.go:287-312]())
- **Updates**: `UpdateOrgUserConfigHandler` for configuration changes ([app/server/handlers/sessions.go:314-346]())

Sources: [app/server/handlers/sessions.go:287-346](), [app/server/db/user_helpers.go:73-96]()

## API Endpoints and Routing

**Authentication and User Management Routes**

| Route Pattern | Method | Handler | Purpose |
|---------------|--------|---------|---------|
| `/accounts/email_verifications` | POST | `CreateEmailVerificationHandler` | Start email verification |
| `/accounts/email_verifications/check_pin` | POST | `CheckEmailPinHandler` | Validate PIN |
| `/accounts/sign_in_codes` | POST | `CreateSignInCodeHandler` | Generate cross-client auth code |
| `/accounts/sign_in` | POST | `SignInHandler` | User authentication |
| `/accounts/sign_out` | POST | `SignOutHandler` | Session termination |
| `/accounts` | POST | `CreateAccountHandler` | User registration |
| `/orgs/session` | GET | `GetOrgSessionHandler` | Current org context |
| `/orgs` | GET/POST | `ListOrgsHandler`/`CreateOrgHandler` | Organization management |
| `/users` | GET | `ListUsersHandler` | List org users |
| `/orgs/users/{userId}` | DELETE | `DeleteOrgUserHandler` | Remove user from org |
| `/invites` | POST | `InviteUserHandler` | Send invitation |
| `/invites/{type}` | GET | `List{Type}InvitesHandler` | List invitations |
| `/org_user_config` | GET/PUT | `GetOrgUserConfigHandler`/`UpdateOrgUserConfigHandler` | User-specific org config |

Sources: [app/server/routes/routes.go:92-111](), [app/server/routes/routes.go:188-189]()

### Client-Side API Implementation

The CLI implements a comprehensive API client with authentication management:

**API Client Interface**

```mermaid
classDiagram
    class ApiClient {
        +CreateEmailVerification()
        +CreateAccount()
        +SignIn()
        +SignOut()
        +CreateOrg()
        +ListOrgs()
        +ListUsers()
        +InviteUser()
        +ListPendingInvites()
        +GetOrgUserConfig()
        +UpdateOrgUserConfig()
    }
    
    class authenticatedTransport {
        +RoundTrip(req) response
        -SetAuthHeader()
        -SetVersionHeader()
    }
    
    class retryTransport {
        +RoundTrip(req) response
        -MaxRetries int
        -BaseDelay time.Duration
        -RetryStatuses map
    }
    
    ApiClient --> authenticatedTransport
    authenticatedTransport --> retryTransport
    
    note for authenticatedTransport "Automatically injects\nauth headers for\nauthenticated requests"
```

Sources: [app/cli/types/api.go:17-119](), [app/cli/api/clients.go:44-64](), [app/cli/api/clients.go:66-117]()

## Session Management and Security

### Token Management

Authentication tokens are managed through several layers:

- **Server Storage**: `AuthToken` records in database with SHA256 hashed tokens ([app/server/db/data_models.go:19-25]())
- **Client Storage**: Handled by authentication system in CLI client
- **Token Lifecycle**: Creation on sign-in, deletion on sign-out ([app/server/handlers/sessions.go:260-266]())
- **Automatic Injection**: `authenticatedTransport` adds tokens to requests ([app/cli/api/clients.go:48-54]())

### Security Features

| Feature | Implementation | Location |
|---------|----------------|----------|
| PIN Hashing | SHA256 hash storage for email verification PINs | [app/server/handlers/sessions.go:94-96]() |
| Token Hashing | SHA256 hash storage for auth tokens | [app/server/db/data_models.go:22]() |
| Email Validation | Domain extraction and validation | [app/server/db/user_helpers.go:133-137]() |
| Request Retry | Exponential backoff with jitter for failed requests | [app/cli/api/clients.go:75-116]() |
| Local Dev Mode | Bypass email verification in development | [app/server/handlers/sessions.go:85-123]() |

Sources: [app/server/handlers/sessions.go:86-123](), [app/cli/api/clients.go:66-134]()

### Organization Context Management

Users operate within organization contexts, managed through:

- **Session Response**: `SessionResponse` includes available organizations ([app/shared/req_res.go:44-51]())
- **Organization Selection**: Client maintains current organization context
- **Multi-Organization Support**: Users can belong to multiple organizations ([app/server/db/data_models.go:97-114]())
- **Domain-Based Auto-Add**: Organizations can automatically add users from matching email domains ([app/server/db/data_models.go:31]())

Sources: [app/shared/req_res.go:44-51](), [app/server/db/data_models.go:27-46]()

---

# Page: Development and Deployment

# Development and Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/cli/go.mod](app/cli/go.mod)
- [app/cli/go.sum](app/cli/go.sum)
- [app/server/go.mod](app/server/go.mod)
- [app/server/go.sum](app/server/go.sum)
- [app/shared/go.mod](app/shared/go.mod)
- [app/shared/go.sum](app/shared/go.sum)
- [releases/cli/versions/2.0.8.md](releases/cli/versions/2.0.8.md)

</details>



This page covers setting up Plandex for development and deploying it in various environments. It includes the module architecture, local development setup, and deployment options for self-hosting.

For production hosting with Plandex Cloud, see the hosting documentation.

## Overview

Plandex uses a client-server architecture with three main Go modules: CLI, server, and shared components. The system supports both cloud-hosted and self-hosted deployments, with the ability to run locally for development or deploy to production environments.

### Development and Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        DevCLI["plandex-cli module"]
        DevServer["plandex-server module"]  
        DevShared["plandex-shared module"]
        DevDocker["Docker Compose\n(start_local.sh)"]
    end
    
    subgraph "Build System"
        CLIBuild["CLI Binary\n(go build)"]
        ServerBuild["Server Binary\n(go run main.go)"]
        DockerBuild["Docker Image\n(Dockerfile.server)"]
    end
    
    subgraph "Deployment Targets"
        LocalDev["Local Development\n(localhost:8099)"]
        SelfHosted["Self-Hosted Production\n(Custom Host)"]
        CloudHosted["Plandex Cloud\n(api.plandex.ai)"]
    end
    
    DevCLI --> CLIBuild
    DevServer --> ServerBuild
    DevServer --> DockerBuild
    DevDocker --> LocalDev
    
    CLIBuild --> LocalDev
    CLIBuild --> SelfHosted
    CLIBuild --> CloudHosted
    
    ServerBuild --> LocalDev
    ServerBuild --> SelfHosted
    DockerBuild --> SelfHosted
```

Sources: [app/cli/go.mod:1-89](), [app/server/go.mod:1-51](), [app/shared/go.mod:1-23](), [docs/docs/hosting/self-hosting/local-mode-quickstart.md:14-19]()

### Module Dependencies Comparison

| Module | Purpose | Key Dependencies | Build Output |
|--------|---------|------------------|--------------|
| `plandex-cli` | Command-line interface | `cobra`, `bubbletea`, `chromedp`, `go-prompt` | Binary executable |
| `plandex-server` | HTTP API server | `gorilla/mux`, `lib/pq`, `golang-migrate`, `go-tree-sitter` | Server binary or Docker image |
| `plandex-shared` | Common types and utilities | `go-openai`, `tiktoken-go`, `tablewriter` | Shared library |

Sources: [app/cli/go.mod:5-85](), [app/server/go.mod:5-48](), [app/shared/go.mod:5-22]()

## Module Dependencies and Architecture

The Plandex codebase consists of three Go modules that work together to provide the complete system functionality.

### Go Module Structure

```mermaid
graph TB
    subgraph "app/cli (plandex-cli)"
        CLI_Main["main.go"]
        CLI_Cobra["cobra commands"]
        CLI_REPL["bubbletea REPL"]
        CLI_TUI["Terminal UI"]
        CLI_HTTP["HTTP client"]
    end
    
    subgraph "app/server (plandex-server)" 
        Server_Main["main.go"]
        Server_Mux["gorilla/mux router"]
        Server_DB["lib/pq PostgreSQL"]
        Server_TreeSitter["go-tree-sitter parser"]
        Server_Migrate["golang-migrate/v4"]
    end
    
    subgraph "app/shared (plandex-shared)"
        Shared_Types["Common types"]
        Shared_OpenAI["go-openai client"]
        Shared_Tiktoken["tiktoken-go tokenizer"]
        Shared_Utils["Utility functions"]
    end
    
    CLI_Main --> Shared_Types
    CLI_HTTP --> Shared_OpenAI
    CLI_REPL --> Shared_Utils
    
    Server_Main --> Shared_Types  
    Server_Mux --> Shared_OpenAI
    Server_DB --> Shared_Utils
```

Sources: [app/cli/go.mod:1-89](), [app/server/go.mod:1-51](), [app/shared/go.mod:1-23]()

### CLI Module Dependencies

The CLI module (`plandex-cli`) provides the command-line interface and includes:

| Dependency | Purpose | Version |
|------------|---------|---------|
| `github.com/spf13/cobra` | Command-line interface framework | v1.8.0 |
| `github.com/charmbracelet/bubbletea` | Terminal UI framework for REPL | v1.3.0 |
| `github.com/charmbracelet/lipgloss` | Terminal styling | v1.0.0 |
| `github.com/chromedp/chromedp` | Browser automation for diff UI | v0.13.3 |
| `github.com/plandex-ai/go-prompt` | Interactive prompt library | Custom fork |
| `github.com/sashabaranov/go-openai` | OpenAI API client | v1.38.1 |

The CLI replaces the shared module dependency with:
```go
replace plandex-shared => ../shared
```

Sources: [app/cli/go.mod:5-25](), [app/cli/go.mod:88]()

### Server Module Dependencies

The server module (`plandex-server`) provides the HTTP API and includes:

| Dependency | Purpose | Version |
|------------|---------|---------|
| `github.com/gorilla/mux` | HTTP router | v1.8.1 |
| `github.com/lib/pq` | PostgreSQL driver | v1.10.9 |
| `github.com/jmoiron/sqlx` | SQL extensions | v1.4.0 |
| `github.com/golang-migrate/migrate/v4` | Database migrations | v4.18.2 |
| `github.com/smacker/go-tree-sitter` | Code parsing | v0.0.0-20240827094217 |
| `github.com/sashabaranov/go-openai` | OpenAI API client | v1.38.1 |

Sources: [app/server/go.mod:5-48]()

### Shared Module Dependencies

The shared module (`plandex-shared`) contains common types and utilities:

| Dependency | Purpose | Version |
|------------|---------|---------|
| `github.com/sashabaranov/go-openai` | OpenAI API client types | v1.38.1 |
| `github.com/pkoukk/tiktoken-go` | Token counting | v0.1.7 |
| `github.com/olekukonko/tablewriter` | Table formatting | v0.0.5 |
| `github.com/shopspring/decimal` | Decimal number handling | v1.4.0 |

Sources: [app/shared/go.mod:5-22]()

## Local Development Environment

Setting up Plandex for local development involves running the server locally and connecting the CLI to it. This is ideal for contributing to Plandex or customizing it for your needs.

### Local Development Architecture

```mermaid
graph TB
    subgraph "Local Development Setup"
        DevCLI["plandex CLI\n(go build)"]
        StartScript["start_local.sh"]
        DockerCompose["docker-compose.yml"]
    end
    
    subgraph "Development Server Stack"
        LocalServer["plandex-server:8099\n(Docker container)"]
        PostgresDB["postgres:15\n(Docker container)"]
        FileSystem["~/plandex-server\n(Volume mount)"]
    end
    
    subgraph "External Services"
        OpenRouter["openrouter.ai\n(OPENROUTER_API_KEY)"]
        OpenAI["platform.openai.com\n(OPENAI_API_KEY)"]
    end
    
    StartScript --> DockerCompose
    DockerCompose --> LocalServer
    DockerCompose --> PostgresDB
    LocalServer --> FileSystem
    
    DevCLI --> LocalServer
    LocalServer --> OpenRouter
    LocalServer --> OpenAI
```

Sources: [docs/docs/hosting/self-hosting/local-mode-quickstart.md:14-19](), [docs/docs/hosting/self-hosting/local-mode-quickstart.md:56-64]()

### Quick Development Setup

The quickest way to set up a local development environment:

1. **Clone the repository and start the server:**
   ```bash
   git clone https://github.com/plandex-ai/plandex.git
   cd plandex/app
   ./start_local.sh
   ```

   The `start_local.sh` script will:
   - Pull the latest Docker images
   - Start PostgreSQL and Plandex server containers
   - Set up the development environment on `http://localhost:8099`

2. **Install the CLI (if not already installed):**
   ```bash
   curl -sL https://plandex.ai/install.sh | bash
   ```

3. **Configure the CLI for local development:**
   ```bash
   plandex sign-in
   ```
   Select 'Local mode host' and confirm the default host `http://localhost:8099`.

4. **Set required API keys:**
   ```bash
   export OPENROUTER_API_KEY=<your-openrouter-api-key>
   export OPENAI_API_KEY=<your-openai-api-key>  # optional
   ```

5. **Start developing:**
   ```bash
   cd your-project-directory
   plandex
   ```

Sources: [docs/docs/hosting/self-hosting/local-mode-quickstart.md:14-53]()

### Building from Source

For development, you can build and run the components from source:

#### CLI Development Build

```bash
cd plandex/app/cli
go build -ldflags "-X plandex/version.Version=$(cat version.txt)"
./plandex --help
```

#### Server Development Build

```bash
cd plandex/app/server
export GOENV=development
export DATABASE_URL=postgres://user:password@localhost:5432/plandex
export PLANDEX_BASE_DIR=~/plandex-server
go run main.go
```

Sources: [docs/docs/install.md:20-25](), [docs/docs/hosting/self-hosting/advanced-self-hosting.md:119-129]()

### Development Environment Variables

For local development, set these environment variables:

| Variable | Purpose | Example |
|----------|---------|---------|
| `GOENV` | Server mode (development/production) | `development` |
| `DATABASE_URL` | PostgreSQL connection string | `postgres://user:pass@localhost:5432/plandex` |
| `PLANDEX_BASE_DIR` | Base directory for file storage | `~/plandex-server` |
| `OPENROUTER_API_KEY` | OpenRouter API access | Your API key |
| `OPENAI_API_KEY` | OpenAI API access (optional) | Your API key |
| `PLANDEX_ENV` | CLI environment mode | `development` |

Sources: [docs/docs/hosting/self-hosting/advanced-self-hosting.md:41-72]()

### Upgrading the Development Environment

To upgrade after a new release:

```bash
cd plandex/app
# Stop the current server
ctrl-c
# Restart with latest images
./start_local.sh
```

The script automatically pulls the latest Docker images before starting.

Sources: [docs/docs/hosting/self-hosting/local-mode-quickstart.md:56-64]()

## Self-Hosting Plandex

Self-hosting Plandex provides full control over your infrastructure and data. You can deploy it for production use with multiple users or organizations.

### Self-Hosted Production Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        CLIUsers["Multiple CLI Clients"]
        WebAPI["HTTP API Clients"]
    end
    
    subgraph "Application Layer"
        LoadBalancer["Load Balancer\n(Optional)"]
        PlandexServer["plandex-server\n(gorilla/mux)"]
        HealthCheck["Health Check\n(/health endpoint)"]
    end
    
    subgraph "Data Layer"
        PostgresDB["PostgreSQL v14+\n(lib/pq driver)"]
        FileSystem["File Storage\n(/plandex-server)"]
        GitRepos["Git Repositories\n(per-plan storage)"]
    end
    
    subgraph "External Services"
        SMTP["SMTP Server\n(Production mode)"]
        ModelAPIs["AI Model APIs\n(OpenRouter/OpenAI)"]
    end
    
    CLIUsers --> LoadBalancer
    WebAPI --> LoadBalancer
    LoadBalancer --> PlandexServer
    PlandexServer --> HealthCheck
    PlandexServer --> PostgresDB
    PlandexServer --> FileSystem
    PlandexServer --> GitRepos
    PlandexServer --> SMTP
    PlandexServer --> ModelAPIs
```

Sources: [docs/docs/hosting/self-hosting/advanced-self-hosting.md:10-26](), [docs/docs/hosting/self-hosting/advanced-self-hosting.md:131-133]()

### System Requirements

For self-hosting Plandex, you need:

| Component | Requirement | Purpose |
|-----------|-------------|---------|
| **PostgreSQL** | v14+ recommended | Plan and conversation storage |
| **File System** | Persistent storage | Git repositories and file context |
| **Git** | Latest version | Version control for plans |
| **Build Tools** | gcc, g++, make | Required for `go-tree-sitter` dependency |
| **Go Runtime** | v1.23.3+ | Server execution |
| **Docker** (Optional) | Latest version | Containerized deployment |

Sources: [docs/docs/hosting/self-hosting/advanced-self-hosting.md:10-15](), [app/server/go.mod:3]()

### Environment Configuration

#### Development vs. Production Mode

Set the deployment mode with the `GOENV` environment variable:

| Mode | Use Case | Email | Auth Pins | Base Directory |
|------|----------|-------|-----------|----------------|
| `development` | Single user, local testing | Disabled | Skipped | `$HOME/plandex-server` |
| `production` | Multi-user, production | Required (SMTP) | Email-based | `/plandex-server` |

```bash
export GOENV=production  # or development
```

Sources: [docs/docs/hosting/self-hosting/advanced-self-hosting.md:16-26]()

#### Database Setup

Create a PostgreSQL database for Plandex:

```sql
CREATE USER 'plandex_user' WITH PASSWORD 'secure_password';
CREATE DATABASE 'plandex' OWNER 'plandex_user';
GRANT ALL PRIVILEGES ON DATABASE 'plandex' TO 'plandex_user';
```

Set the database connection:
```bash
export DATABASE_URL=postgres://plandex_user:secure_password@localhost:5432/plandex
```

Sources: [docs/docs/hosting/self-hosting/advanced-self-hosting.md:30-36](), [docs/docs/hosting/self-hosting/advanced-self-hosting.md:52-56]()

#### Production Environment Variables

For production deployment, configure these environment variables:

```bash
# Core Configuration
export GOENV=production
export DATABASE_URL=postgres://user:password@host:5432/plandex
export PLANDEX_BASE_DIR=/plandex-server
export PORT=8099
export API_HOST=api.your-domain.com

# SMTP Configuration (Required for production)
export SMTP_HOST=smtp.your-domain.com
export SMTP_PORT=587
export SMTP_USER=noreply@your-domain.com
export SMTP_PASSWORD=smtp_password
export SMTP_FROM=noreply@your-domain.com
```

Sources: [docs/docs/hosting/self-hosting/advanced-self-hosting.md:58-78]()

### Deployment Methods

#### Docker Deployment

**Using pre-built images from DockerHub:**

```bash
docker pull plandexai/plandex-server:latest
docker run -p 8099:8099 \
  -v /plandex-server:/plandex-server \
  -e DATABASE_URL=postgres://user:password@host:5432/plandex \
  -e GOENV=production \
  -e API_HOST=api.your-domain.com \
  -e SMTP_HOST=smtp.your-domain.com \
  -e SMTP_PORT=587 \
  -e SMTP_USER=noreply@your-domain.com \
  -e SMTP_PASSWORD=smtp_password \
  plandexai/plandex-server:latest
```

**Building from source:**

```bash
git clone https://github.com/plandex-ai/plandex.git
VERSION=$(cat app/server/version.txt)
git checkout server/v$VERSION
cd plandex/app
docker build -t plandex-server -f Dockerfile.server .
```

Sources: [docs/docs/hosting/self-hosting/advanced-self-hosting.md:106-113](), [docs/docs/hosting/self-hosting/advanced-self-hosting.md:84-101]()

#### Source Deployment

Run the server directly from Go source:

```bash
git clone https://github.com/plandex-ai/plandex.git
cd plandex/
VERSION=$(cat app/server/version.txt)
git checkout server/v$VERSION
cd app/server

# Set environment variables
export GOENV=production
export DATABASE_URL=postgres://user:password@host:5432/plandex
export PLANDEX_BASE_DIR=/plandex-server

# Run server
go run main.go
```

The server will start on port 8099 by default (configurable with `PORT` environment variable).

Sources: [docs/docs/hosting/self-hosting/advanced-self-hosting.md:119-129]()

### Health Monitoring

The server provides a health check endpoint for monitoring:

```bash
curl http://your-server:8099/health
```

A successful response returns HTTP 200, indicating the server is running properly.

Sources: [docs/docs/hosting/self-hosting/advanced-self-hosting.md:131-133]()

### Client Configuration

Configure the Plandex CLI to connect to your self-hosted server:

```bash
# Set API host for production server
export API_HOST=api.your-domain.com

# Sign in to your server
plandex sign-in
```

When prompted, select "Another host" and enter your server URL.

For development servers, you can use:
```bash
export PLANDEX_ENV=development
plandex sign-in
```

Sources: [docs/docs/hosting/self-hosting/advanced-self-hosting.md:74-78](), [docs/docs/hosting/self-hosting/advanced-self-hosting.md:137-141]()

## Security Considerations

### API Key Security

- When self-hosting or using BYO API Key Mode, API keys are stored only in memory during active use
- Keys are never written to disk, logged, or stored in a database
- When a plan stream ends, API keys are removed from memory

Best practices:
- Avoid storing API keys in multiple places
- Don't expose keys to third-party services
- Don't send keys in plain text

Sources: [docs/docs/security.md:12-17]()

### File Security

Plandex respects `.gitignore` and won't load ignored files unless explicitly forced:

- Use `.gitignore` to exclude sensitive files
- Create a `.plandexignore` file with additional ignore patterns
- Use the `--force/-f` flag with `plandex load` to override ignores when needed

Sources: [docs/docs/security.md:8-9]()

## Switching Between Deployment Options

You can switch between deployment options by signing in with the desired host:

1. To switch to Plandex Cloud:
   ```bash
   plandex sign-in
   ```
   When prompted, select 'Plandex Cloud'.

2. To switch to a self-hosted server:
   ```bash
   plandex sign-in
   ```
   When prompted, select 'Local mode host' or 'Another host', then enter the appropriate host URL.

3. For development environments:
   ```bash
   export PLANDEX_ENV=development
   plandex sign-in
   ```
   This defaults to using the local development server.

Sources: [docs/docs/environment-variables.md:15-16](), [docs/docs/hosting/self-hosting/local-mode-quickstart.md:33-34]()

## Setup Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant CLI as Plandex CLI
    participant Server as Plandex Server
    participant DB as PostgreSQL
    participant AI as AI Provider APIs
    
    User->>CLI: Install CLI (curl -sL https://plandex.ai/install.sh | bash)
    User->>CLI: plandex sign-in
    
    alt Plandex Cloud
        CLI->>Server: Connect to Plandex Cloud
        User->>CLI: Select hosting mode (Integrated/BYO)
        
        alt Integrated Models
            User->>CLI: Start trial or enter payment info
        else BYO API Key
            User->>CLI: Export OPENROUTER_API_KEY & OPENAI_API_KEY
        end
    else Self-Hosted
        User->>Server: Deploy server (Docker or custom)
        Server->>DB: Initialize database
        User->>CLI: Select "Local mode host" or "Another host"
        User->>CLI: Export OPENROUTER_API_KEY & OPENAI_API_KEY
    end
    
    User->>CLI: cd project-directory
    User->>CLI: plandex
    CLI->>Server: Create new plan
    Server->>DB: Store plan
    User->>CLI: Enter prompt
    CLI->>Server: Send prompt
    Server->>AI: Query AI models
    AI->>Server: Return response
    Server->>CLI: Stream response
    CLI->>User: Display results
```

Sources: [docs/docs/cli-reference.md:800-811](), [docs/docs/quick-start.md:33-56](), [docs/docs/hosting/self-hosting/local-mode-quickstart.md:10-53]()

---

# Page: Module Dependencies and Architecture

# Module Dependencies and Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/cli/go.mod](app/cli/go.mod)
- [app/cli/go.sum](app/cli/go.sum)
- [app/server/go.mod](app/server/go.mod)
- [app/server/go.sum](app/server/go.sum)
- [app/shared/go.mod](app/shared/go.mod)
- [app/shared/go.sum](app/shared/go.sum)
- [releases/cli/versions/2.0.8.md](releases/cli/versions/2.0.8.md)

</details>



This document details the Go module structure, dependency management, and architectural relationships between the main components of the Plandex codebase. It focuses on how the CLI, server, and shared modules are organized and their external dependencies.

For information about the overall system architecture and data flow, see [System Architecture Overview](#1.3). For details about the server-side components and business logic, see [Server Architecture](#4).

## Module Structure

Plandex is organized as a monorepo with three main Go modules using Go 1.23.3 that follow a clear separation of concerns:

**Module Dependency Architecture**

```mermaid
graph TB
    subgraph "Plandex Monorepo (Go 1.23.3)"
        CLI[plandex-cli]
        Server[plandex-server] 
        Shared[plandex-shared]
    end
    
    subgraph "External Dependencies"
        OpenAI["github.com/sashabaranov/go-openai"]
        Cobra["github.com/spf13/cobra"]
        Mux["github.com/gorilla/mux"]
        PostgreSQL["github.com/lib/pq"]
        Bubbletea["github.com/charmbracelet/bubbletea"]
        Chromedp["github.com/chromedp/chromedp"]
    end
    
    CLI --> Shared
    Server --> Shared
    CLI --> |"HTTP API Calls"| Server
    
    CLI --> OpenAI
    CLI --> Cobra
    CLI --> Bubbletea  
    CLI --> Chromedp
    Server --> Mux
    Server --> PostgreSQL
    Shared --> OpenAI
```

**Module Configuration and Replace Directives**

Each module uses local path replacement to depend on the shared module:

| Module | Path | Go Version | Shared Dependency |
|--------|------|------------|------------------|
| `plandex-cli` | `app/cli/` | 1.23.3 | `replace plandex-shared => ../shared` |
| `plandex-server` | `app/server/` | 1.23.3 | `replace plandex-shared => ../shared` |
| `plandex-shared` | `app/shared/` | 1.23.3 | N/A (base dependency) |

Sources: [app/cli/go.mod:1-3](), [app/cli/go.mod:106](), [app/server/go.mod:1-3](), [app/server/go.mod:53](), [app/shared/go.mod:1-3]()

## CLI Module Dependencies

The CLI module (`plandex-cli`) handles user interaction through multiple interfaces and communicates with the Plandex server via HTTP APIs.

**CLI Dependency Architecture**

```mermaid
graph TB
    subgraph "plandex-cli Module"
        cobra_cmd["github.com/spf13/cobra v1.8.0"]
        go_prompt["github.com/plandex-ai/go-prompt v0.0.0-20250304173555-1f364907fc6c"]
        bubbletea["github.com/charmbracelet/bubbletea v1.3.0"]
        bubbles["github.com/charmbracelet/bubbles v0.20.0"] 
        lipgloss["github.com/charmbracelet/lipgloss v1.0.0"]
        survey["github.com/plandex-ai/survey/v2 v2.3.7"]
        chromedp["github.com/chromedp/chromedp v0.13.3"]
        goquery["github.com/PuerkitoBio/goquery v1.8.1"]
        openai["github.com/sashabaranov/go-openai v1.38.1"]
        aws_config["github.com/aws/aws-sdk-go-v2/config v1.29.14"]
    end
    
    subgraph "CLI Interface Systems"
        REPL["REPL (cmd/repl.go)"]
        TUI["Streaming TUI (tui)"]
        Commands["CLI Commands (cmd)"]
        Browser["Web Scraping (browse)"]
    end
    
    subgraph "External Services"
        AI_APIs["AI Model APIs"]
        Web_Content["Web Pages"]
        Plandex_Server["Plandex HTTP Server"]
        AWS_Services["AWS Services"]
    end
    
    cobra_cmd --> Commands
    go_prompt --> REPL
    bubbletea --> TUI
    bubbles --> TUI
    lipgloss --> TUI
    survey --> Commands
    chromedp --> Browser
    goquery --> Browser
    openai --> AI_APIs
    aws_config --> AWS_Services
    
    REPL --> Plandex_Server
    TUI --> Plandex_Server
    Commands --> Plandex_Server
    Browser --> Web_Content
```

**CLI Dependencies by Category**

| Category | Dependencies | Version | Purpose |
|----------|--------------|---------|---------|
| **Command Framework** | `github.com/spf13/cobra` | v1.8.0 | CLI command structure and argument parsing |
| **Interactive REPL** | `github.com/plandex-ai/go-prompt` | v0.0.0-20250304173555 | Custom REPL interface with autocomplete |
| **User Input** | `github.com/plandex-ai/survey/v2` | v2.3.7 | Form-based user input collection |
| **Terminal UI** | `github.com/charmbracelet/bubbletea` | v1.3.0 | Real-time streaming interface framework |
| | `github.com/charmbracelet/bubbles` | v0.20.0 | Pre-built UI components |
| | `github.com/charmbracelet/lipgloss` | v1.0.0 | Terminal styling and layout |
| **Web Automation** | `github.com/chromedp/chromedp` | v0.13.3 | Headless Chrome browser automation |
| | `github.com/PuerkitoBio/goquery` | v1.8.1 | HTML parsing and DOM manipulation |
| **AI Integration** | `github.com/sashabaranov/go-openai` | v1.38.1 | OpenAI API client |
| **Cloud Services** | `github.com/aws/aws-sdk-go-v2/config` | v1.29.14 | AWS SDK configuration |
| **Utilities** | `github.com/google/uuid` | v1.6.0 | UUID generation |
| | `github.com/fatih/color` | v1.18.0 | Terminal color output |
| | `github.com/briandowns/spinner` | v1.23.0 | Loading indicators |

Sources: [app/cli/go.mod:5-28](), [app/cli/go.mod:84-103]()

## Server Module Dependencies

The server module (`plandex-server`) implements the core business logic, database operations, and AI model integration.

**Server Dependency Architecture**

```mermaid
graph TB
    subgraph "plandex-server Module"
        mux["github.com/gorilla/mux v1.8.1"]
        libpq["github.com/lib/pq v1.10.9"]
        sqlx["github.com/jmoiron/sqlx v1.4.0"]
        migrate["github.com/golang-migrate/migrate/v4 v4.18.3"]
        openai_server["github.com/sashabaranov/go-openai v1.40.0"]
        tree_sitter["github.com/smacker/go-tree-sitter v0.0.0-20240827094217-dd81d9e9be82"]
        aws_sdk["github.com/aws/aws-sdk-go v1.55.7"]
        beeep["github.com/gen2brain/beeep v0.0.0-20240516210008-9c006672e7f4"]
        uuid_server["github.com/google/uuid v1.6.0"]
    end
    
    subgraph "Server Components"
        HTTP_Routes["HTTP Routes (routes)"]
        DB_Layer["Database Layer (db)"]
        AI_Client["AI Model Client (model)"]
        Code_Parser["Syntax Parser (syntax)"]
        Plan_Engine["Plan Execution (plan)"]
        File_Builder["File Builder (build)"]
    end
    
    subgraph "External Infrastructure"
        PostgreSQL_DB["PostgreSQL Database"]
        AI_Model_APIs["AI Model APIs"]
        File_System["File System & Git"]
        OS_Services["Operating System"]
        AWS_S3["AWS S3 Storage"]
    end
    
    mux --> HTTP_Routes
    libpq --> DB_Layer
    sqlx --> DB_Layer
    migrate --> DB_Layer
    openai_server --> AI_Client
    tree_sitter --> Code_Parser
    aws_sdk --> AWS_S3
    beeep --> OS_Services
    uuid_server --> Plan_Engine
    
    HTTP_Routes --> Plan_Engine
    DB_Layer --> PostgreSQL_DB
    AI_Client --> AI_Model_APIs
    Code_Parser --> File_System
    Plan_Engine --> File_Builder
    File_Builder --> File_System
```

**Server Dependencies by Category**

| Category | Dependencies | Version | Purpose |
|----------|--------------|---------|---------|
| **HTTP Framework** | `github.com/gorilla/mux` | v1.8.1 | HTTP routing, middleware, and request handling |
| **Database** | `github.com/lib/pq` | v1.10.9 | PostgreSQL driver |
| | `github.com/jmoiron/sqlx` | v1.4.0 | SQL query builder and result mapping |
| | `github.com/golang-migrate/migrate/v4` | v4.18.3 | Database schema migrations |
| **AI Integration** | `github.com/sashabaranov/go-openai` | v1.40.0 | OpenAI API client (newer than CLI version) |
| **Code Analysis** | `github.com/smacker/go-tree-sitter` | v0.0.0-20240827094217 | Language-agnostic syntax tree parsing |
| **Cloud Services** | `github.com/aws/aws-sdk-go` | v1.55.7 | AWS service integration |
| **System Integration** | `github.com/gen2brain/beeep` | v0.0.0-20240516210008 | Cross-platform desktop notifications |
| **Core Utilities** | `github.com/google/uuid` | v1.6.0 | UUID generation for plans and sessions |
| | `github.com/pkg/errors` | v0.9.1 | Enhanced error handling |

**Version Discrepancies**
- The server uses `go-openai v1.40.0` while CLI and shared use `v1.38.1`
- Server uses AWS SDK v1 while CLI uses AWS SDK v2

Sources: [app/server/go.mod:5-12](), [app/server/go.mod:39-51]()

## Shared Module Dependencies

The shared module (`plandex-shared`) contains common types, utilities, and interfaces used by both CLI and server.

**Shared Module Architecture**

```mermaid
graph TB
    subgraph "plandex-shared Module"
        openai_shared["github.com/sashabaranov/go-openai v1.38.1"]
        tiktoken["github.com/pkoukk/tiktoken-go v0.1.7"]
        uuid_shared["github.com/google/uuid v1.6.0"]
        decimal["github.com/shopspring/decimal v1.4.0"]
        tablewriter["github.com/olekukonko/tablewriter v0.0.5"]
        image["golang.org/x/image v0.25.0"]
        copier["github.com/jinzhu/copier v0.4.0"]
    end
    
    subgraph "Shared Components"
        API_Types["API Types (types)"]
        Model_Types["Model Types (model)"]
        Token_Utils["Token Utils (tiktoken)"]
        Table_Utils["Table Formatting (table)"]
        Data_Utils["Data Utilities (utils)"]
        Image_Utils["Image Processing (image)"]
    end
    
    subgraph "Module Consumers"
        CLI_Import["plandex-cli imports"]
        Server_Import["plandex-server imports"]
    end
    
    openai_shared --> Model_Types
    tiktoken --> Token_Utils
    uuid_shared --> Data_Utils
    decimal --> Data_Utils  
    tablewriter --> Table_Utils
    image --> Image_Utils
    copier --> Data_Utils
    
    API_Types --> CLI_Import
    API_Types --> Server_Import
    Model_Types --> CLI_Import
    Model_Types --> Server_Import
    Token_Utils --> CLI_Import
    Token_Utils --> Server_Import
    Table_Utils --> CLI_Import
    Data_Utils --> CLI_Import
    Data_Utils --> Server_Import
    Image_Utils --> CLI_Import
```

**Shared Dependencies by Category**

| Category | Dependencies | Version | Purpose |
|----------|--------------|---------|---------|
| **AI Integration** | `github.com/sashabaranov/go-openai` | v1.38.1 | Common AI model types and interfaces |
| **Token Management** | `github.com/pkoukk/tiktoken-go` | v0.1.7 | Token counting for AI context management |
| **Data Utilities** | `github.com/google/uuid` | v1.6.0 | UUID generation for entities |
| | `github.com/shopspring/decimal` | v1.4.0 | Precise decimal arithmetic |
| | `github.com/jinzhu/copier` | v0.4.0 | Struct copying utilities |
| **Output Formatting** | `github.com/olekukonko/tablewriter` | v0.0.5 | ASCII table formatting for CLI output |
| **Media Processing** | `golang.org/x/image` | v0.25.0 | Image manipulation and processing |

**Core Shared Types**
- Plan definitions and state management
- AI model configuration and response types  
- Context management structures
- File build and validation types
- HTTP API request/response contracts

Sources: [app/shared/go.mod:5-10](), [app/shared/go.mod:17-24]()

## Dependency Management Architecture

The Plandex codebase uses sophisticated dependency management patterns to support its multi-module architecture.

**Module Replace Directives**

```mermaid
graph TB
    subgraph "Local Module Resolution"
        cli_replace["plandex-cli/go.mod<br/>replace plandex-shared => ../shared"]
        server_replace["plandex-server/go.mod<br/>replace plandex-shared => ../shared"]
        shared_base["plandex-shared/go.mod<br/>Base module (no replaces)"]
    end
    
    subgraph "Dependency Resolution"
        shared_deps["Shared Dependencies<br/>go-openai, tiktoken-go, uuid, decimal"]
        cli_deps["CLI-Specific Dependencies<br/>cobra, bubbletea, chromedp"]
        server_deps["Server-Specific Dependencies<br/>gorilla/mux, lib/pq, tree-sitter"]
    end
    
    subgraph "Version Coordination"
        go_version["Go 1.23.3<br/>All modules"]
        openai_version["go-openai Version Mismatch<br/>CLI/Shared: v1.38.1<br/>Server: v1.40.0"]
        uuid_version["Consistent UUID<br/>v1.6.0 across all modules"]
    end
    
    cli_replace --> shared_base
    server_replace --> shared_base
    shared_base --> shared_deps
    cli_replace --> cli_deps
    server_replace --> server_deps
    
    shared_deps --> go_version
    cli_deps --> openai_version
    server_deps --> openai_version
    shared_deps --> uuid_version
```

**Cross-Module Type Sharing**

The shared module provides common interfaces and types that bridge CLI and server implementations:

```mermaid
graph LR
    subgraph "plandex-shared Types"
        plan_types["Plan Types<br/>PlanState, PlanBranch"]
        context_types["Context Types<br/>ContextFile, ProjectContext"]
        model_types["Model Types<br/>ModelConfig, ModelRole"]
        api_types["API Types<br/>Request/Response structs"]
        build_types["Build Types<br/>FileContent, BuildResult"]
    end
    
    subgraph "CLI Usage"
        cli_commands["CLI Commands<br/>cmd/ package"]
        cli_tui["Terminal UI<br/>tui/ package"]
        cli_api["API Client<br/>api/ package"]
    end
    
    subgraph "Server Usage"
        server_handlers["HTTP Handlers<br/>handlers/ package"]
        server_db["Database Layer<br/>db/ package"]
        server_plan["Plan Engine<br/>plan/ package"]
    end
    
    plan_types --> cli_commands
    plan_types --> server_handlers
    context_types --> cli_api
    context_types --> server_db
    model_types --> cli_tui
    model_types --> server_plan
    api_types --> cli_api
    api_types --> server_handlers
    build_types --> cli_commands
    build_types --> server_plan
```

Sources: [app/cli/go.mod:106](), [app/server/go.mod:53](), [app/shared/go.mod]()

## External Integration Architecture  

The Plandex modules integrate with multiple external services and systems through well-defined dependency interfaces.

**External Service Dependencies**

```mermaid
graph TB
    subgraph "AI Model Providers"
        openai_api["OpenAI API<br/>sashabaranov/go-openai"]
        anthropic_api["Anthropic API<br/>Direct HTTP"]
        google_api["Google AI API<br/>Direct HTTP"] 
        openrouter_api["OpenRouter API<br/>Direct HTTP"]
        local_llm["Local LLMs<br/>Ollama/Local"]
    end
    
    subgraph "Infrastructure Services"
        postgres_db["PostgreSQL<br/>lib/pq + jmoiron/sqlx"]
        aws_s3["AWS S3<br/>aws-sdk-go"]
        git_repos["Git Repositories<br/>os/exec + git commands"]
        file_system["File System<br/>os package"]
    end
    
    subgraph "Web Services"
        browser_automation["Web Scraping<br/>chromedp/chromedp"]
        html_parsing["HTML Processing<br/>PuerkitoBio/goquery"]
        http_apis["HTTP APIs<br/>net/http"]
    end
    
    subgraph "System Integration"
        desktop_notifications["Desktop Notifications<br/>gen2brain/beeep"]
        system_clipboard["Clipboard<br/>atotto/clipboard"]
        terminal_ui["Terminal UI<br/>charmbracelet ecosystem"]
    end
    
    subgraph "Plandex Modules"
        CLI_Module["plandex-cli"]
        Server_Module["plandex-server"]
        Shared_Module["plandex-shared"]
    end
    
    CLI_Module --> openai_api
    CLI_Module --> browser_automation
    CLI_Module --> html_parsing
    CLI_Module --> desktop_notifications
    CLI_Module --> system_clipboard
    CLI_Module --> terminal_ui
    
    Server_Module --> openai_api
    Server_Module --> anthropic_api
    Server_Module --> google_api
    Server_Module --> openrouter_api
    Server_Module --> local_llm
    Server_Module --> postgres_db
    Server_Module --> aws_s3
    Server_Module --> git_repos
    Server_Module --> file_system
    
    Shared_Module --> openai_api
```

**Custom Fork Dependencies**

Plandex maintains custom forks of several dependencies for specific functionality:

| Package | Original | Custom Fork | Modifications |
|---------|----------|-------------|---------------|
| `go-prompt` | `c-bata/go-prompt` | `plandex-ai/go-prompt v0.0.0-20250304173555` | REPL customizations |
| `survey` | `AlecAivazis/survey` | `plandex-ai/survey/v2 v2.3.7` | Enhanced input collection |

**Tree-sitter Language Support**

The server uses `go-tree-sitter` for multi-language syntax parsing:

```mermaid
graph LR
    subgraph "Tree-sitter Integration"
        go_tree_sitter["github.com/smacker/go-tree-sitter<br/>v0.0.0-20240827094217"]
        language_grammars["Language Grammars<br/>JavaScript, Python, Go, etc."]
        syntax_parser["Syntax Parser<br/>server/syntax/"]
        file_builder["File Builder<br/>server/build/"]
    end
    
    go_tree_sitter --> language_grammars
    language_grammars --> syntax_parser
    syntax_parser --> file_builder
```

Sources: [app/cli/go.mod:19-20](), [app/server/go.mod:47](), [app/cli/go.mod:8-9]()

## Route Registration System

The server uses a flexible route registration system that supports different handler types and middleware configurations:

```mermaid
graph TB
    subgraph "Route Registration"
        Register["RegisterHandlePlandex()<br/>Function Registration"]
        Ensure["EnsureHandlePlandex()<br/>Validation"]
        Handle["HandlePlandexFn<br/>Dynamic Handler"]
    end
    
    subgraph "Route Categories"
        Health["Health Routes<br/>/health, /version"]
        API["API Routes<br/>Account, Plan, Context Management"]
        Proxyable["Proxyable API Routes<br/>Streaming, Real-time Operations"]
    end
    
    subgraph "Handler Types"
        Standard["Standard Handlers<br/>handlers.CreatePlanHandler"]
        Streaming["Streaming Handlers<br/>handlers.TellPlanHandler<br/>handlers.BuildPlanHandler"]
        Proxy["Proxy Handlers<br/>handlers.ConnectPlanHandler"]
    end
    
    Register --> Handle
    Handle --> Ensure
    Ensure --> Health
    Ensure --> API
    Ensure --> Proxyable
    
    Health --> Standard
    API --> Standard
    API --> Streaming
    Proxyable --> Streaming
    Proxyable --> Proxy
```

**Route Categories**

| Category | Function | Routes | Purpose |
|----------|----------|--------|---------|
| **Health** | `AddHealthRoutes()` | `/health`, `/version` | System monitoring |
| **API** | `AddApiRoutes()` | Core business logic | Plan and context management |
| **Proxyable** | `AddProxyableApiRoutes()` | Real-time operations | Streaming and live connections |

Sources: [app/server/routes/routes.go:15-28](), [app/server/routes/routes.go:30-71](), [app/server/routes/routes.go:89-185](), [app/server/routes/routes.go:187-198]()

---

# Page: Local Development Environment

# Local Development Environment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/cli/api/clients.go](app/cli/api/clients.go)
- [app/cli/go.mod](app/cli/go.mod)
- [app/cli/go.sum](app/cli/go.sum)
- [app/server/db/user_helpers.go](app/server/db/user_helpers.go)
- [app/server/go.mod](app/server/go.mod)
- [app/server/go.sum](app/server/go.sum)
- [app/server/handlers/sessions.go](app/server/handlers/sessions.go)
- [app/server/main.go](app/server/main.go)
- [app/server/routes/routes.go](app/server/routes/routes.go)
- [app/server/setup/setup.go](app/server/setup/setup.go)
- [app/shared/go.mod](app/shared/go.mod)
- [app/shared/go.sum](app/shared/go.sum)
- [releases/cli/versions/2.0.8.md](releases/cli/versions/2.0.8.md)

</details>



This document provides a comprehensive guide for setting up a local development environment for Plandex. It covers the server and CLI components, database configuration, and development workflow. For production deployment considerations, see [Self-Hosting Plandex](#7.3). For understanding the overall module architecture, see [Module Dependencies and Architecture](#7.1).

## Environment Structure

Plandex consists of three main Go modules organized in a monorepo structure with clear separation of concerns between client, server, and shared components.

### Module Architecture

```mermaid
graph TB
    subgraph "Plandex Monorepo"
        subgraph "app/cli"
            CliMod["plandex-cli module"]
            CliCode["CLI Application Code"]
            CliAPI["api/clients.go"]
        end
        
        subgraph "app/server" 
            ServerMod["plandex-server module"]
            ServerCode["Server Application Code"]
            ServerMain["main.go"]
            ServerSetup["setup/setup.go"]
            ServerRoutes["routes/routes.go"]
        end
        
        subgraph "app/shared"
            SharedMod["plandex-shared module"]
            SharedTypes["Shared Types & Utils"]
        end
    end
    
    CliMod --> SharedMod
    ServerMod --> SharedMod
    CliAPI --> ServerRoutes
```

**Sources:** [app/cli/go.mod:1-107](), [app/server/go.mod:1-54](), [app/shared/go.mod:1-25]()

### Development Dependencies

The development environment requires several key dependencies managed through Go modules:

| Component | Key Dependencies | Purpose |
|-----------|------------------|---------|
| CLI | `gorilla/mux`, `spf13/cobra`, `charmbracelet/bubbletea` | HTTP routing, CLI framework, TUI |
| Server | `jmoiron/sqlx`, `lib/pq`, `golang-migrate/migrate` | Database access, PostgreSQL driver, migrations |
| Shared | `sashabaranov/go-openai`, `pkoukk/tiktoken-go` | AI model integration, token counting |

**Sources:** [app/cli/go.mod:5-28](), [app/server/go.mod:5-51](), [app/shared/go.mod:5-24]()

## Server Development Setup

The server component handles API requests, plan execution, and database operations. The development setup involves database initialization, environment configuration, and server startup.

### Server Initialization Flow

```mermaid
graph TD
    Start["main.go"] --> Setup["setup.RegisterShutdownHook()"]
    Setup --> LiteLLM["model.EnsureLiteLLM(2)"]
    LiteLLM --> Routes["routes.AddHealthRoutes()"]
    Routes --> API["routes.AddApiRoutes()"]
    API --> Proxy["routes.AddProxyableApiRoutes()"]
    Proxy --> LoadIP["setup.MustLoadIp()"]
    LoadIP --> InitDB["setup.MustInitDb()"]
    InitDB --> DBConnect["db.Connect()"]
    DBConnect --> Migrations["db.MigrationsUp()"]
    Migrations --> Cache["db.CacheOrgRoleIds()"]
    Cache --> StartServer["setup.StartServer()"]
    StartServer --> Listen["server.ListenAndServe()"]
```

**Sources:** [app/server/main.go:14-38](), [app/server/setup/setup.go:20-42]()

### Development Environment Variables

The server recognizes several environment variables for development configuration:

```go
// Development mode detection
GOENV=development           // Enables development features
PLANDEX_ENV=development    // CLI development mode  
LOCAL_MODE=1               // Bypasses email verification
PORT=8099                  // Server port (default)
IS_CLOUD=""                // Cloud deployment flag
```

**Sources:** [app/server/setup/setup.go:67-88](), [app/cli/api/clients.go:24-32](), [app/server/handlers/sessions.go:85]()

### Database Setup

The server requires PostgreSQL with automatic migration handling:

```mermaid
graph LR
    Connect["db.Connect()"] --> Migrate["db.MigrationsUp()"]
    Migrate --> Cache["db.CacheOrgRoleIds()"]
    Cache --> Ready["Database Ready"]
    
    Connect --> PostgreSQL["PostgreSQL Database"]
    Migrate --> Schema["Migration Scripts"]
```

**Sources:** [app/server/setup/setup.go:27-42]()

### Local Server Startup

To start the server in development mode:

1. **Database**: Ensure PostgreSQL is running and accessible
2. **Environment**: Set `GOENV=development` 
3. **Run**: Execute `go run main.go` from `app/server/`
4. **Verify**: Server starts on port 8099 with health endpoint at `/health`

The server includes graceful shutdown handling that waits for active plans to complete before terminating.

**Sources:** [app/server/main.go:14-38](), [app/server/setup/setup.go:66-185]()

## CLI Development Setup

The CLI connects to either local development servers or the cloud API based on environment configuration.

### API Client Configuration

```mermaid
graph TB
    Init["CLI Initialization"] --> EnvCheck["Check PLANDEX_ENV"]
    EnvCheck -->|development| LocalHost["PLANDEX_API_HOST or localhost:8099"]
    EnvCheck -->|production| CloudHost["api-v2.plandex.ai"]
    
    LocalHost --> AuthCheck["auth.Current.IsCloud"]
    CloudHost --> AuthCheck
    AuthCheck -->|true| CloudAPI["Use Cloud API"]
    AuthCheck -->|false| LocalAPI["Use Local Server"]
    
    CloudAPI --> HTTPClient["authenticatedTransport"]
    LocalAPI --> HTTPClient
```

**Sources:** [app/cli/api/clients.go:23-42]()

### HTTP Client Architecture

The CLI implements sophisticated HTTP client handling with authentication, retries, and timeout management:

```mermaid
graph TD
    BaseTransport["http.Transport"] --> RetryTransport["retryTransport"]
    RetryTransport --> AuthTransport["authenticatedTransport"] 
    AuthTransport --> FastClient["30s timeout"]
    AuthTransport --> SlowClient["5min timeout"]
    AuthTransport --> StreamingClient["no timeout"]
    
    RetryTransport --> Config["MaxRetries: 3<br/>BaseDelay: 500ms<br/>MaxDelay: 5s"]
```

**Sources:** [app/cli/api/clients.go:66-162]()

### Development CLI Usage

For CLI development against a local server:

1. **Environment**: Set `PLANDEX_ENV=development`
2. **API Host**: Set `PLANDEX_API_HOST=http://localhost:8099` (optional)
3. **Build**: `go build` from `app/cli/`
4. **Run**: Execute CLI commands against local server

The CLI automatically detects development mode and adjusts API endpoints accordingly.

**Sources:** [app/cli/api/clients.go:24-32]()

## Development Workflow

### Local Development Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        CLI["Plandex CLI<br/>:local"] --> Server["Plandex Server<br/>:8099"]
        Server --> PostgreSQL["PostgreSQL<br/>Database"]
        Server --> LiteLLM["LiteLLM Proxy<br/>AI Models"]
        
        subgraph "Server Components"
            Routes["routes/routes.go<br/>HTTP Handlers"]
            Setup["setup/setup.go<br/>Initialization"]
            Handlers["handlers/*<br/>Business Logic"]
        end
        
        Server --> Routes
        Routes --> Handlers
        Setup --> Server
    end
    
    subgraph "External Dependencies"
        AIProviders["OpenAI, Anthropic<br/>Google, etc."]
    end
    
    LiteLLM --> AIProviders
```

**Sources:** [app/server/main.go:14-38](), [app/server/routes/routes.go:73-203](), [app/server/setup/setup.go:66-185]()

### Development Features

The development environment includes several debugging and development-specific features:

| Feature | Implementation | Purpose |
|---------|----------------|---------|
| Request Logging | `loggingMiddleware` | Logs all HTTP requests with timing |
| Local Mode | `LOCAL_MODE=1` | Bypasses email verification |
| Development Detection | `GOENV=development` | Enables dev-specific behavior |
| Graceful Shutdown | Signal handling | Waits for active plans completion |

**Sources:** [app/server/setup/setup.go:50-64](), [app/server/setup/setup.go:119-185](), [app/server/handlers/sessions.go:85-123]()

### Database Development

The server automatically handles database migrations and role caching during startup:

```mermaid
graph LR
    Startup["Server Startup"] --> Connect["Database Connection"]
    Connect --> Migrate["Run Migrations"]
    Migrate --> Cache["Cache Org Role IDs"]
    Cache --> Ready["Server Ready"]
    
    Shutdown["Server Shutdown"] --> Cleanup["Cleanup Active Locks"]
    Cleanup --> Close["Close DB Connection"]
```

**Sources:** [app/server/setup/setup.go:27-42](), [app/server/setup/setup.go:155-158](), [app/server/setup/setup.go:75-82]()

This development environment setup ensures consistent behavior between local development and production while providing the necessary tools for debugging and testing Plandex components.

---

# Page: Self-Hosting Plandex

# Self-Hosting Plandex

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [app/cli/api/clients.go](app/cli/api/clients.go)
- [app/server/db/user_helpers.go](app/server/db/user_helpers.go)
- [app/server/handlers/sessions.go](app/server/handlers/sessions.go)
- [app/server/main.go](app/server/main.go)
- [app/server/routes/routes.go](app/server/routes/routes.go)
- [app/server/setup/setup.go](app/server/setup/setup.go)
- [docs/docs/cli-reference.md](docs/docs/cli-reference.md)
- [docs/docs/environment-variables.md](docs/docs/environment-variables.md)
- [docs/docs/hosting/cloud.md](docs/docs/hosting/cloud.md)
- [docs/docs/hosting/self-hosting/_category_.json](docs/docs/hosting/self-hosting/_category_.json)
- [docs/docs/hosting/self-hosting/advanced-self-hosting.md](docs/docs/hosting/self-hosting/advanced-self-hosting.md)
- [docs/docs/hosting/self-hosting/local-mode-quickstart.md](docs/docs/hosting/self-hosting/local-mode-quickstart.md)
- [docs/docs/install.md](docs/docs/install.md)
- [docs/docs/models/claude-subscription.md](docs/docs/models/claude-subscription.md)
- [docs/docs/models/models-overview.md](docs/docs/models/models-overview.md)
- [docs/docs/quick-start.md](docs/docs/quick-start.md)

</details>



This document covers the complete setup and configuration of a self-hosted Plandex server environment. It explains the server architecture, deployment options, database configuration, and operational considerations for running Plandex in your own infrastructure.

For client installation and usage, see [Installation and Quick Start](#1.1). For development environment setup, see [Local Development Environment](#7.2).

## Architecture Overview

Plandex uses a client-server architecture where the CLI communicates with a stateful server that manages plans, contexts, and AI model interactions. The server requires PostgreSQL for data persistence and a file system for storing project files and contexts.

**Server Architecture**
```mermaid
graph TB
    subgraph "Server Components"
        MainGo["main.go"]
        SetupGo["setup.go"]
        RoutesGo["routes.go"]
        HandlersDir["handlers/"]
        DBDir["db/"]
        ModelDir["model/"]
    end
    
    subgraph "External Dependencies"
        PostgreSQL[("PostgreSQL Database")]
        FileSystem[("Persistent File System")]
        GitRepo[("Git Repositories")]
        LiteLLM["LiteLLM Proxy"]
    end
    
    subgraph "Network Interface"
        HealthEndpoint["/health"]
        VersionEndpoint["/version"]
        APIEndpoints["/api/*"]
    end
    
    MainGo --> SetupGo
    SetupGo --> RoutesGo
    RoutesGo --> HandlersDir
    HandlersDir --> DBDir
    HandlersDir --> ModelDir
    
    SetupGo --> PostgreSQL
    SetupGo --> FileSystem
    ModelDir --> LiteLLM
    ModelDir --> GitRepo
    
    RoutesGo --> HealthEndpoint
    RoutesGo --> VersionEndpoint
    RoutesGo --> APIEndpoints
```

Sources: [app/server/main.go:1-38](), [app/server/setup/setup.go:1-215](), [app/server/routes/routes.go:1-204]()

## Deployment Options

Plandex supports two primary self-hosting approaches:

| Option | Use Case | Complexity | Requirements |
|--------|----------|------------|--------------|
| **Local Mode** | Single user, development | Low | Docker, git |
| **Advanced Self-Hosting** | Multiple users, production | High | PostgreSQL, SMTP, server management |

### Local Mode Quickstart

Local mode uses Docker Compose for single-user development environments:

```bash
git clone https://github.com/plandex-ai/plandex.git
cd plandex/app
./start_local.sh
```

**Local Mode Architecture**
```mermaid
graph TB
    subgraph "Docker Environment"
        PlandexServer["plandex-server container"]
        PostgresContainer["postgres container"]
        VolumeMount["~/plandex-server volume"]
    end
    
    subgraph "Host System"
        CLI["plandex CLI"]
        LocalProject["Project Directory"]
        GitRepo["Local Git Repository"]
    end
    
    CLI --> PlandexServer
    PlandexServer --> PostgresContainer
    PlandexServer --> VolumeMount
    CLI --> LocalProject
    LocalProject --> GitRepo
    
    PlandexServer -.-> GitRepo
```

Sources: [docs/docs/hosting/self-hosting/local-mode-quickstart.md:1-63](), [README.md:154-161]()

### Advanced Self-Hosting

Advanced self-hosting supports production deployments with multiple users and organizations:

**Production Deployment Architecture**
```mermaid
graph TB
    subgraph "Production Environment"
        LoadBalancer["Load Balancer"]
        PlandexServerProd["Plandex Server"]
        PostgresProd[("PostgreSQL Database")]
        FileSystemProd[("Persistent Storage")]
        SMTPService["SMTP Service"]
    end
    
    subgraph "Client Environments"
        CLIClient1["CLI Client 1"]
        CLIClient2["CLI Client 2"]
        CLIClientN["CLI Client N"]
    end
    
    subgraph "External Services"
        AIProviders["AI Model Providers"]
        EmailService["Email Delivery"]
    end
    
    CLIClient1 --> LoadBalancer
    CLIClient2 --> LoadBalancer
    CLIClientN --> LoadBalancer
    
    LoadBalancer --> PlandexServerProd
    PlandexServerProd --> PostgresProd
    PlandexServerProd --> FileSystemProd
    PlandexServerProd --> SMTPService
    PlandexServerProd --> AIProviders
    SMTPService --> EmailService
```

Sources: [docs/docs/hosting/self-hosting/advanced-self-hosting.md:1-157]()

## Server Configuration

### Environment Modes

The server operates in two distinct modes controlled by the `GOENV` environment variable:

| Mode | Purpose | Authentication | Base Directory | Email |
|------|---------|----------------|----------------|-------|
| `development` | Local single-user | Pins skipped | `$HOME/plandex-server` | Disabled |
| `production` | Multi-user/org | Email verification | `/plandex-server` | Required |

**Server Initialization Flow**
```mermaid
graph TD
    StartServer["StartServer()"]
    LoadIP["MustLoadIp()"]
    InitDB["MustInitDb()"]
    RegisterRoutes["Register Routes"]
    StartHTTP["Start HTTP Server"]
    
    InitDB --> ConnectDB["db.Connect()"]
    InitDB --> RunMigrations["db.MigrationsUp()"]
    InitDB --> CacheRoles["db.CacheOrgRoleIds()"]
    
    RegisterRoutes --> HealthRoutes["AddHealthRoutes()"]
    RegisterRoutes --> APIRoutes["AddApiRoutes()"]
    RegisterRoutes --> ProxyRoutes["AddProxyableApiRoutes()"]
    
    StartServer --> LoadIP
    LoadIP --> InitDB
    InitDB --> RegisterRoutes
    RegisterRoutes --> StartHTTP
```

Sources: [app/server/setup/setup.go:20-42](), [app/server/main.go:14-38]()

### Core Environment Variables

```bash
# Server Mode
GOENV=production  # or development
PORT=8099        # Server port

# Database
DATABASE_URL=postgres://user:pass@host:5432/plandex

# File System
PLANDEX_BASE_DIR=/plandex-server

# Production Mode (SMTP required)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=user
SMTP_PASSWORD=password

# API Host (production only)
API_HOST=https://api.your-domain.ai
```

Sources: [docs/docs/environment-variables.md:79-124](), [docs/docs/hosting/self-hosting/advanced-self-hosting.md:39-78]()

## Database Setup

### PostgreSQL Requirements

Plandex requires PostgreSQL (ideally v14+) with proper user permissions:

```sql
CREATE USER 'plandex_user' WITH PASSWORD 'secure_password';
CREATE DATABASE 'plandex' OWNER 'plandex_user';
GRANT ALL PRIVILEGES ON DATABASE 'plandex' TO 'plandex_user';
```

**Database Initialization Process**
```mermaid
graph TD
    DBConnect["db.Connect()"]
    RunMigrations["db.MigrationsUp()"]
    CacheRoles["db.CacheOrgRoleIds()"]
    
    DBConnect --> CheckConnection["Verify Connection"]
    CheckConnection --> RunMigrations
    RunMigrations --> ApplySchemaChanges["Apply Schema Changes"]
    ApplySchemaChanges --> CacheRoles
    CacheRoles --> CacheOrgRoleData["Cache Organization Role IDs"]
    
    DBConnect -.->|"Failure"| FatalError["log.Fatal()"]
    RunMigrations -.->|"Failure"| FatalError
    CacheRoles -.->|"Failure"| FatalError
```

Sources: [app/server/setup/setup.go:27-42](), [docs/docs/hosting/self-hosting/advanced-self-hosting.md:29-36]()

## Server Lifecycle Management

### Startup Process

The server initialization follows a strict sequence managed by the `setup` package:

```mermaid
graph TD
    Main["main()"]
    RegisterHandler["RegisterHandlePlandex()"]
    EnsureLiteLLM["EnsureLiteLLM()"]
    CreateRouter["mux.NewRouter()"]
    StartServer["StartServer()"]
    
    Middleware["loggingMiddleware()"]
    MaxBytes["maxBytesMiddleware()"]
    HTTPServer["http.Server"]
    
    Main --> RegisterHandler
    RegisterHandler --> EnsureLiteLLM
    EnsureLiteLLM --> CreateRouter
    CreateRouter --> StartServer
    
    StartServer --> Middleware
    Middleware --> MaxBytes
    MaxBytes --> HTTPServer
```

Sources: [app/server/main.go:14-38](), [app/server/setup/setup.go:66-105]()

### Graceful Shutdown

The server implements graceful shutdown with plan completion monitoring:

```mermaid
graph TD
    SigTerm["SIGTERM/SIGINT"]
    ShutdownCtx["Create Shutdown Context"]
    WaitPlans["waitForActivePlans()"]
    CleanupLocks["CleanupActiveLocks()"]
    ShutdownHTTP["Shutdown HTTP Server"]
    ExecuteHooks["Execute Shutdown Hooks"]
    
    SigTerm --> ShutdownCtx
    ShutdownCtx --> WaitPlans
    WaitPlans --> CheckActivePlans["plan.NumActivePlans()"]
    CheckActivePlans -->|"Active Plans"| WaitTicker["Wait 1 second"]
    WaitTicker --> CheckActivePlans
    CheckActivePlans -->|"No Active Plans"| CleanupLocks
    
    CleanupLocks --> ShutdownHTTP
    ShutdownHTTP --> ExecuteHooks
    ExecuteHooks --> Complete["Shutdown Complete"]
```

Sources: [app/server/setup/setup.go:119-185](), [app/server/setup/setup.go:187-204]()

## API Route Configuration

### Route Registration

The server exposes three categories of endpoints through the `routes` package:

```mermaid
graph LR
    Router["mux.Router"]
    
    subgraph "Route Categories"
        HealthRoutes["Health Routes"]
        APIRoutes["API Routes"]
        ProxyRoutes["Proxyable API Routes"]
    end
    
    subgraph "Health Endpoints"
        HealthCheck["/health"]
        VersionCheck["/version"]
    end
    
    subgraph "Core API"
        PlansAPI["/plans/*"]
        ContextAPI["/context/*"]
        ModelsAPI["/models/*"]
        AccountsAPI["/accounts/*"]
    end
    
    subgraph "Streaming API"
        ConnectStream["/connect"]
        TellStream["/tell"]
        BuildStream["/build"]
    end
    
    Router --> HealthRoutes
    Router --> APIRoutes
    Router --> ProxyRoutes
    
    HealthRoutes --> HealthCheck
    HealthRoutes --> VersionCheck
    
    APIRoutes --> PlansAPI
    APIRoutes --> ContextAPI
    APIRoutes --> ModelsAPI
    APIRoutes --> AccountsAPI
    
    ProxyRoutes --> ConnectStream
    ProxyRoutes --> TellStream
    ProxyRoutes --> BuildStream
```

Sources: [app/server/routes/routes.go:30-71](), [app/server/routes/routes.go:89-190](), [app/server/routes/routes.go:192-203]()

## Health Monitoring

### Health Check Endpoints

The server provides monitoring endpoints for operational health:

| Endpoint | Purpose | Response |
|----------|---------|----------|
| `/health` | Service health check | `OK` or error |
| `/version` | Server version info | Version string |

**Health Check Implementation**
```mermaid
graph TD
    HealthRequest["/health Request"]
    ExecHook["hooks.ExecHook(HealthCheck)"]
    HookResult{"Hook Success?"}
    ReturnOK["Return 'OK'"]
    ReturnError["Return Error"]
    
    VersionRequest["/version Request"]
    ReadVersion["Read version.txt"]
    ReturnVersion["Return Version String"]
    
    HealthRequest --> ExecHook
    ExecHook --> HookResult
    HookResult -->|"Success"| ReturnOK
    HookResult -->|"Failure"| ReturnError
    
    VersionRequest --> ReadVersion
    ReadVersion --> ReturnVersion
```

Sources: [app/server/routes/routes.go:30-71]()

## Security Considerations

### Authentication Flow

The server implements token-based authentication with email verification:

```mermaid
graph TD
    EmailVerification["CreateEmailVerificationHandler"]
    CheckPin["CheckEmailPinHandler"]
    SignIn["SignInHandler"]
    AuthToken["Generate Auth Token"]
    
    LocalMode{"Local Mode?"}
    SendEmail["Send Verification Email"]
    SkipEmail["Skip Email Verification"]
    
    EmailVerification --> LocalMode
    LocalMode -->|"Production"| SendEmail
    LocalMode -->|"Development"| SkipEmail
    
    SendEmail --> CheckPin
    SkipEmail --> CheckPin
    CheckPin --> SignIn
    SignIn --> AuthToken
```

Sources: [app/server/handlers/sessions.go:18-136](), [app/server/handlers/sessions.go:138-172]()

### Request Middleware

The server applies security middleware to all requests:

```mermaid
graph TD
    IncomingRequest["HTTP Request"]
    LoggingMiddleware["loggingMiddleware()"]
    MaxBytesMiddleware["maxBytesMiddleware()"]
    AuthMiddleware["Authentication Check"]
    RouteHandler["Route Handler"]
    
    IncomingRequest --> LoggingMiddleware
    LoggingMiddleware --> MaxBytesMiddleware
    MaxBytesMiddleware --> AuthMiddleware
    AuthMiddleware --> RouteHandler
    
    MaxBytesMiddleware -.->|"1GB Limit"| RejectLarge["Reject Large Requests"]
    AuthMiddleware -.->|"Invalid Token"| Return401["401 Unauthorized"]
```

Sources: [app/server/setup/setup.go:50-64](), [app/server/setup/setup.go:206-214]()

## Storage and Persistence

The server manages multiple types of persistent data:

| Data Type | Storage | Purpose |
|-----------|---------|---------|
| User accounts, plans, contexts | PostgreSQL | Relational data |
| Project files, contexts | File system | File content |
| Git repositories | File system | Version control |
| Model configurations | PostgreSQL | AI model settings |

**Data Flow Architecture**
```mermaid
graph TD
    subgraph "Client Operations"
        LoadContext["Load Context"]
        CreatePlan["Create Plan"]
        ApplyChanges["Apply Changes"]
    end
    
    subgraph "Server Storage"
        PostgreSQLDB[("PostgreSQL")]
        FileSystemStorage[("File System")]
        GitRepos[("Git Repositories")]
    end
    
    subgraph "Data Types"
        PlanData["Plans, Branches, Conversations"]
        ContextData["Context Metadata"]
        FileContent["File Content, Project Maps"]
        GitData["Version History, Commits"]
    end
    
    LoadContext --> ContextData
    CreatePlan --> PlanData
    ApplyChanges --> FileContent
    ApplyChanges --> GitData
    
    PlanData --> PostgreSQLDB
    ContextData --> PostgreSQLDB
    FileContent --> FileSystemStorage
    GitData --> GitRepos
```

Sources: [docs/docs/hosting/self-hosting/advanced-self-hosting.md:11-14](), [app/server/setup/setup.go:27-42]()

---

# Page: Version History and Releases

# Version History and Releases

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/cli/version.txt](app/cli/version.txt)
- [releases/cli/CHANGELOG.md](releases/cli/CHANGELOG.md)
- [releases/cli/versions/0.7.1.md](releases/cli/versions/0.7.1.md)
- [releases/cli/versions/2.0.0.md](releases/cli/versions/2.0.0.md)
- [releases/cli/versions/2.0.4.md](releases/cli/versions/2.0.4.md)
- [releases/server/versions/2.0.0.md](releases/server/versions/2.0.0.md)
- [releases/server/versions/2.0.4.md](releases/server/versions/2.0.4.md)

</details>



This page documents the release history and version information for Plandex, covering both the CLI and server components. It provides a chronological overview of major releases, key features introduced in each version, and notable bug fixes. For more detailed information about specific CLI and server releases, see [CLI Releases](#7.1) and [Server Releases](#7.2).

## Versioning Overview

Plandex uses semantic versioning (MAJOR.MINOR.PATCH) for both CLI and server components, with occasional build/hotfix indicators (like "+1"). The CLI and server components are versioned separately but typically align closely in their major and minor versions.

### Current Versions

| Component | Current Version | Release Date |
|-----------|----------------|--------------|
| CLI       | 2.1.6+1        | Latest       |
| Server    | 2.1.8          | Latest       |

Sources: [app/cli/version.txt:1](), [app/server/version.txt:1]()

## Release Timeline

The following timeline shows the major releases of Plandex from the initial release to the current version:

```mermaid
timeline
    title "Plandex Release Timeline"
    section v0.x Series
        0.7.0 : "Initial release"
        0.8.x : "User management improvements"
        0.9.x : "Custom model support<br>Archiving plans<br>File update improvements"
    section v1.x Series
        1.0.0 : "GPT-4o as default model<br>Significant reliability improvements"
        1.1.0 : "Image context support<br>File rejection capabilities"
        1.1.1 : "Claude 3.5 Sonnet support<br>Stream handling improvements"
    section v2.x Series
        2.0.0 : "Major rewrite with new features<br>MIT License<br>REPL interface<br>Auto context loading"
        2.0.4 : "New models: Claude 3.7, Gemini 2.5, DeepSeek V3<br>Browser debugging"
        2.0.7 : "Command handling improvements<br>Bugfixes"
        2.1.0 : "OpenRouter-only mode<br>New models: o4-mini, o3, gpt-4.1<br>Gemini caching"
        2.1.5 : "Claude Sonnet 4 and Opus 4<br>Model fallback improvements"
        2.1.6 : "Sonnet 4 as default<br>strong-opus model pack"
```

Sources: [releases/cli/CHANGELOG.md:55-174](), [releases/server/CHANGELOG.md:46-60]()

## Version 2.x Series (Current)

The 2.x series represents a major evolution of Plandex, with significant architectural improvements and new capabilities.

### Version 2.0.0 (Major Release)

Released as a beta version, 2.0.0 was described as a "new project with far more ambitious goals" rather than a simple update to 1.x. It included:

- **Architecture**: Complete redesign with a multi-model approach combining models from Anthropic, OpenAI, and Google
- **Developer Experience**: New REPL interface with fuzzy autocomplete and multi-line editing
- **Context Management**: Automatic context selection with tree-sitter project maps supporting 30+ languages
- **File Editing**: Improved reliability for large files up to 100k tokens
- **Automation**: Configurable levels from basic to full auto with command execution integration
- **Licensing**: Transition from AGPL 3.0 to MIT License

```mermaid
flowchart TD
    subgraph "Plandex 2.0 Architecture"
        User["User Interface"] --> REPL["REPL Interface"]
        User --> Commands["Direct CLI Commands"]
        
        REPL --> ModelSelector["Model Selection<br>daily-driver/strong/cheap/oss"]
        Commands --> ModelSelector
        
        ModelSelector --> RoleDistribution["Role Distribution"]
        
        subgraph "Role-based Model Assignment"
            RoleDistribution --> Architect["Architect Role"]
            RoleDistribution --> Coder["Coder Role"]
            RoleDistribution --> Planner["Planner Role"]
            RoleDistribution --> BuilderVerifier["Builder/Verifier Roles"]
        end
        
        Architect --> Planning["Planning Phase"]
        Coder --> Implementation["Implementation Phase"]
        Planner --> Orchestration["Orchestration"]
        BuilderVerifier --> Validation["Validation & Auto-Fix"]
        
        Planning --> FileOps["File Operations"]
        Implementation --> FileOps
        Validation --> FileOps
        
        FileOps --> GitIntegration["Git Integration"]
    end
```

Sources: [releases/cli/CHANGELOG.md:55-174](), [releases/cli/versions/2.0.0.md](), [releases/server/versions/2.0.0.md]()

### Version 2.0.4

This release added important new model support and debugging capabilities:

- **Models**:
  - Claude Sonnet 3.7 thinking (available in the `reasoning` model pack)
  - Gemini 2.5 Pro (experimental) 
  - DeepSeek V3 03-24 (used in the `oss` pack)
  - OpenAI GPT 4.5
- **Debugging**: Browser application debugging via Chrome console logs
- **Reliability**: HTTP retry logic with exponential backoff
- **Model Pack Management**: New `model-packs update` and `model-packs show` commands

Sources: [releases/cli/CHANGELOG.md:11-41](), [releases/cli/versions/2.0.4.md](), [releases/server/versions/2.0.4.md]()

### Version 2.1.x Series (Latest)

The 2.1.x series builds upon the 2.0 foundation with significant model improvements, enhanced reliability, and expanded provider support.

#### Version 2.1.0

This major feature release introduced:

- **OpenRouter-Only Mode**: BYO key users can now use Plandex with only an `OPENROUTER_API_KEY`, eliminating the need for separate OpenAI accounts
- **New Model Integration**: 
  - Gemini 2.5 Pro Preview as default for 200k-1M token contexts
  - OpenAI o4-mini with high/medium/low reasoning effort levels (replacing o3-mini)
  - OpenAI o3 with reasoning effort levels and o3-high as default in `strong` pack
  - GPT-4.1, GPT-4.1-mini, and GPT-4.1-nano replacing GPT-4o models
- **Enhanced Fallback System**: Robust fallback and retry system for newly released models and preview models
- **Gemini Caching**: Prompt caching support for Gemini models, reducing costs and latency
- **REPL Improvements**: Better handling of mistyped commands and suggestions

#### Version 2.1.5-2.1.6+1

Recent releases focus on cutting-edge model integration:

- **Claude Sonnet 4**: Added as built-in model, promoted to default in daily-driver pack (2.1.6)
- **Claude Opus 4**: Available in new `strong-opus` and `opus-planner` model packs
- **Enhanced Reliability**: Additional retries for unresponsive models and provider rate limits
- **Error Handling**: Fixes for garbled error messages and lock acquisition issues

Sources: [releases/cli/CHANGELOG.md:1-103](), [releases/server/CHANGELOG.md:1-37]()

### Version 2.0.5 - 2.0.7

These releases focused on stability, reliability and user experience improvements:

- Error handling and model error messaging improvements
- Better handling of partial or mistyped commands in the REPL
- Consolidated Gemini 2.5 Pro Experimental into a single model pack
- Fixed whitespace handling and prevent '\send' command inclusion in multi-line mode

Sources: [releases/cli/CHANGELOG.md:104-153](), [releases/server/CHANGELOG.md:38-77]()

## Version 1.x Series

The 1.x series represented Plandex's first stable release, with several significant feature additions and improvements.

### Version 1.0.0

This marked the first stable release of Plandex:

- **GPT-4o Integration**: Made GPT-4o the default model, delivering 2x faster planning and execution
- **Reliability**: Introduction of automatic syntax and logic validation with auto-correction for file updates
- **Planning Engine**: Improved "memory" for handling long plans without skipping or repeating tasks
- **Cost Efficiency**: 50% cost reduction from GPT-4o's lower per-token pricing

### Version 1.1.0

Notable features in this release:

- **Image Context**: Support for loading images (png, jpeg, gif, webp) into context with GPT-4o
- **Improved Model Support**: Non-OpenAI models support for all roles including builder, verifier, and auto-fix
- **File Management**: Added `plandex reject` command to reject pending changes
- **Conversation Management**: Improved `plandex convo` command with plain text output and message range selection

Sources: [releases/cli/CHANGELOG.md:175-249](), [releases/server/CHANGELOG.md:61-67]()

## Version 0.x Series (Early Releases)

The 0.x series represented the initial development of Plandex, with rapid feature addition and stabilization.

### Version 0.7.0 - 0.8.x

Early releases focusing on core functionality and user management:

- Initial release of core functionality
- User management improvements: inviting users, listing users, and revoking invites
- Repository locking system
- SMTP email integration
- Context management capabilities

### Version 0.9.x

Key features added:

- Custom models and model packs integration
- Plan archiving functionality
- Significant file update improvements for accuracy and reliability
- Better handling of braces, parentheses, and code structures
- Introduction of the `plandex diff` command

Sources: [releases/cli/CHANGELOG.md:250-360](), [releases/server/CHANGELOG.md:144-163](), [releases/server/versions/0.8.1.md]()

## Component Relationship and Release Process

The following diagram illustrates how the CLI and server components interact and their versioning relationship:

```mermaid
graph TD
    subgraph "Release Components"
        CLI["CLI Component<br>Current: 2.1.6+1"]
        Server["Server Component<br>Current: 2.1.8"]
        
        CLI -- "HTTP API Calls" --> Server
        Server -- "JSON Responses" --> CLI
        
        CLI --> CLIChangelog["CLI Changelog<br>releases/cli/CHANGELOG.md"]
        Server --> ServerChangelog["Server Changelog<br>releases/server/CHANGELOG.md"]
        
        CLI --> CLIVersionTxt["app/cli/version.txt"]
        Server --> ServerVersionTxt["app/server/version.txt"]
    end
    
    subgraph "Version Control"
        Repo["Git Repository<br>github.com/plandex-ai/plandex"]
        Repo --> TagsCLI["CLI Tags<br>cli/v{version}"]
        Repo --> TagsServer["Server Tags<br>server/v{version}"]
        
        TagsCLI --> CLIRelease["CLI Releases"]
        TagsServer --> ServerRelease["Server Releases"]
    end
    
    subgraph "Version Files"
        CLIVersionTxt --> CLIRelease
        ServerVersionTxt --> ServerRelease
    end
    
    CLIRelease --> CLI
    ServerRelease --> Server
```

**Model Pack Configuration Flow**

```mermaid
flowchart LR
    subgraph "Model Configuration System"
        ModelPacks["Model Packs<br>daily-driver, strong, cheap, oss"]
        ModelRoles["Model Roles<br>planner, architect, coder, builder"]
        BuiltInModels["Built-in Models<br>claude-sonnet-4, o4-mini, gpt-4.1"]
        CustomModels["Custom Models<br>via model add command"]
    end
    
    subgraph "CLI Commands"
        SetModel["plandex set-model"]
        ModelPacksCmd["plandex model-packs"]
        ModelsCmd["plandex models"]
    end
    
    subgraph "Configuration Storage"
        PlanConfig["Plan-specific Config"]
        DefaultConfig["Default Config"]
        UserConfig["User Config"]
    end
    
    SetModel --> ModelPacks
    ModelPacksCmd --> ModelPacks
    ModelsCmd --> BuiltInModels
    ModelsCmd --> CustomModels
    
    ModelPacks --> ModelRoles
    ModelRoles --> BuiltInModels
    ModelRoles --> CustomModels
    
    ModelPacks --> PlanConfig
    ModelPacks --> DefaultConfig
    ModelPacks --> UserConfig
```

Sources: [releases/cli/CHANGELOG.md](), [releases/server/CHANGELOG.md](), [app/cli/version.txt:1](), [app/server/version.txt:1]()

## Feature Evolution

The following table highlights key features and their introduction/improvement across major versions:

| Feature | First Introduced | Major Improvements |
|---------|-----------------|-------------------|
| Model Integration | 0.7.0 | 0.9.0 (Custom models), 1.0.0 (GPT-4o), 2.0.0 (Multi-model approach), 2.1.0 (OpenRouter-only, o4-mini), 2.1.5-6 (Sonnet 4, Opus 4) |
| Context Management | 0.7.0 | 1.1.0 (Image support), 2.0.0 (Automatic selection), 2.1.0 (2M token window with Gemini) |
| File Operations | 0.7.0 | 0.9.0 (Accuracy), 1.0.0 (Validation), 2.0.0 (Large file support, up to 100k tokens) |
| User Interface | 0.7.0 (CLI) | 2.0.0 (REPL interface), 2.1.0 (Enhanced command suggestions) |
| Automation | 0.7.0 (Basic) | 2.0.0 (Configurable levels), 2.0.4 (Browser debugging) |
| Model Fallbacks | 2.1.0 | 2.1.0 (Robust fallback system), 2.1.5+ (Enhanced fallbacks for new models) |
| Caching | 2.0.0 (OpenAI/Anthropic) | 2.1.0 (Gemini caching support) |

**Model Pack Evolution Timeline**

```mermaid
gantt
    title "Model Pack Evolution Across Versions"
    dateFormat  X
    axisFormat %s
    
    section Core Packs
    daily-driver (GPT-based)    :0, 12
    daily-driver (Multi-model)  :12, 18
    daily-driver (Sonnet 4)     :18, 20
    
    section Specialized Packs
    strong (o1-based)           :12, 15
    strong (o3-based)           :15, 18
    strong-opus (Opus 4)        :18, 20
    
    section Cost-Effective
    cheap                       :12, 20
    oss (Open Source)           :12, 20
    
    section Experimental
    reasoning (Sonnet 3.7)      :16, 20
    gemini-preview              :15, 20
```

Sources: [releases/cli/CHANGELOG.md](), [releases/cli/versions/2.0.0.md](), [releases/cli/versions/2.0.4.md]()

## Upgrade Notes

Upgrading between minor versions within the same major version is generally straightforward. However, upgrading between major versions (e.g., 1.x to 2.x) may require additional steps:

- **1.x to 2.x**: Version 2.x is designed to run separately and independently from v1. Follow the quickstart guide as if you were a new user rather than upgrading in-place.
- **Cloud Users**: The Plandex Cloud service is automatically updated to the latest version.
- **Self-hosted Users**: Refer to the deployment documentation for instructions on upgrading self-hosted instances.

Sources: [releases/cli/CHANGELOG.md:159-161](), [releases/cli/versions/2.0.0.md:105-106]()

---

# Page: CLI Release History

# CLI Release History

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/cli/version.txt](app/cli/version.txt)
- [releases/cli/CHANGELOG.md](releases/cli/CHANGELOG.md)
- [releases/cli/versions/0.7.1.md](releases/cli/versions/0.7.1.md)
- [releases/cli/versions/2.0.0.md](releases/cli/versions/2.0.0.md)
- [releases/cli/versions/2.0.4.md](releases/cli/versions/2.0.4.md)
- [releases/server/versions/2.0.0.md](releases/server/versions/2.0.0.md)
- [releases/server/versions/2.0.4.md](releases/server/versions/2.0.4.md)

</details>



This document tracks the version history and evolution of the Plandex CLI component, documenting feature additions, architectural changes, and major milestones from initial releases through the current version. It covers command-line interface improvements, user experience enhancements, model integration updates, and configuration system changes.

For server-side release history, see [Server Release History](#8.2). For overall system architecture information, see [System Architecture Overview](#1.3).

## Release Timeline and Major Milestones

The CLI has evolved through several major version families, each representing significant architectural and feature improvements:

```mermaid
timeline
    title "Plandex CLI Release Evolution"
    
    section "Early Development"
        0.7.1 : Basic CLI functionality
             : User input fixes
    
    section "Pre-1.0 Stabilization"
        0.8.2 : OpenAI endpoint support
             : Custom help system
        0.8.3 : GPT-4 Turbo integration
             : Model defaults
        0.9.0 : Custom models via OpenRouter
             : Model packs system
             : Archive functionality
        0.9.1 : Stream TUI improvements
             : Auto-upgrade enhancements
    
    section "Version 1.x Stable"
        1.0.0 : Production-ready release
             : Core feature set established
        1.1.0 : Image context support
             : Non-OpenAI model roles
             : Reject command
        1.1.1 : Claude 3.5 Sonnet packs
             : Stream performance improvements
    
    section "Version 2.x Rewrite"
        2.0.0 : Complete architectural overhaul
             : REPL interface introduction
             : Autonomous capabilities
             : Multi-provider architecture
        2.1.0 : OpenRouter-only mode
             : Enhanced model fallbacks
             : Gemini 2.5 Pro integration
        2.2.0 : Provider flexibility expansion
             : JSON-based configuration
             : Ollama integration
        2.2.1 : Claude subscription support
             : Bug fixes
```

Sources: [releases/cli/CHANGELOG.md:1-567](), [app/cli/version.txt:1-2]()

## Architecture Evolution Overview

The CLI architecture has undergone fundamental changes, particularly between version 1.x and 2.x:

```mermaid
graph TB
    subgraph "Version 1.x Architecture"
        CLI1["CLI Commands"] --> API1["Server API"]
        CLI1 --> Stream1["Basic Streaming"]
        CLI1 --> Config1["Simple Config"]
        API1 --> OpenAI1["OpenAI Only"]
    end
    
    subgraph "Version 2.x Architecture"
        REPL2["REPL Interface"] --> CLI2["CLI Commands"]
        CLI2 --> StreamTUI["Advanced Stream TUI"]
        CLI2 --> ConfigJSON["JSON Configuration"]
        CLI2 --> ModelMgmt["Model Management"]
        
        ModelMgmt --> OpenAI2["OpenAI API"]
        ModelMgmt --> Anthropic["Anthropic API"]
        ModelMgmt --> Google["Google AI Studio"]
        ModelMgmt --> OpenRouter["OpenRouter"]
        ModelMgmt --> Ollama["Ollama Local"]
        ModelMgmt --> Azure["Azure OpenAI"]
        ModelMgmt --> AWS["AWS Bedrock"]
        
        StreamTUI --> AutoContext["Auto Context Loading"]
        StreamTUI --> CommandExec["Command Execution"]
        StreamTUI --> DebugMode["Debug Capabilities"]
    end
    
    CLI1 -.-> REPL2
    Stream1 -.-> StreamTUI
    Config1 -.-> ConfigJSON
    OpenAI1 -.-> ModelMgmt
    
    style REPL2 fill:#e1f5fe
    style ModelMgmt fill:#fff3e0
    style StreamTUI fill:#f3e5f5
```

Sources: [releases/cli/CHANGELOG.md:277-383](), [releases/cli/versions/2.0.0.md:1-122]()

## Major Version Milestones

### Version 0.x - Foundation Period

The early versions established core CLI functionality with basic plan execution and context management:

| Version | Key Features | Breaking Changes |
|---------|-------------|------------------|
| 0.7.1 | Basic CLI commands, user input handling | Initial implementation |
| 0.8.2 | `OPENAI_ENDPOINT` environment variable support | None |
| 0.8.3 | GPT-4 Turbo as default model | Model behavior changes |
| 0.9.0 | Custom models via `plandex models add`, Model packs system | New command structure |
| 0.9.1 | Stream TUI improvements, auto-upgrade with sudo | None |

### Version 1.x - Stable Release

Version 1.0.0 marked the first production-ready release with a stable feature set:

**Core Commands Established:**
- `plandex tell` - Plan initiation
- `plandex continue` - Plan continuation  
- `plandex build` - File building
- `plandex apply` - Change application
- `plandex load` - Context loading
- `plandex set-model` - Model configuration

**Version 1.1.x Enhancements:**
- Image context support via `plandex load path/to/image.png`
- `plandex reject` command for change rejection
- Claude 3.5 Sonnet model pack integration
- Non-OpenAI models for builder/verifier roles

### Version 2.x - Architectural Transformation

Version 2.0.0 introduced a complete rewrite with fundamentally different user interaction patterns:

**REPL Interface:**
The primary interaction mode shifted from individual CLI commands to an interactive REPL accessible via `plandex` command without arguments.

**Autonomous Capabilities:**
- `basic` mode - Manual operation like v1.x
- `semi-auto` mode - Automatic context loading (default)
- `full-auto` mode - Complete autonomy including command execution

**Multi-Provider Architecture:**
Expanded from OpenAI-only to supporting multiple AI providers with automatic fallback mechanisms.

Sources: [releases/cli/CHANGELOG.md:14-383](), [releases/cli/versions/2.0.0.md:7-91]()

## Feature Evolution Matrix

```mermaid
graph LR
    subgraph "Context Management Evolution"
        V1Context["Manual Loading"] --> V2Context["Auto Context Selection"]
        V2Context --> TreeSitter["Tree-sitter Project Maps"]
        TreeSitter --> TokenLimit["2M Token Context Window"]
    end
    
    subgraph "Model Integration Evolution"
        OpenAIOnly["OpenAI Only"] --> CustomModels["Custom Models via OpenRouter"]
        CustomModels --> ModelPacks["Model Pack System"]
        ModelPacks --> MultiProvider["Multi-Provider Architecture"]
        MultiProvider --> JSONConfig["JSON Configuration System"]
    end
    
    subgraph "User Interface Evolution"
        BasicCLI["Basic CLI Commands"] --> StreamTUI["Streaming TUI"]
        StreamTUI --> REPL["Interactive REPL"]
        REPL --> Autocomplete["Fuzzy Autocomplete"]
        Autocomplete --> MultiLine["Multi-line Mode"]
    end
    
    subgraph "Automation Evolution"
        Manual["Manual Execution"] --> SemiAuto["Semi-Automated"]
        SemiAuto --> FullAuto["Full Autonomy"]
        FullAuto --> CommandExec["Command Execution"]
        CommandExec --> DebugMode["Automated Debugging"]
    end
```

Sources: [releases/cli/CHANGELOG.md:314-356](), [releases/cli/versions/2.0.0.md:38-80]()

## Configuration System Evolution

The configuration management has undergone significant changes across versions:

### Version 1.x Configuration
- Environment variables: `OPENAI_API_KEY`, `OPENAI_ENDPOINT`
- Simple model selection via `plandex set-model`
- Basic model pack creation

### Version 2.x Configuration  
- JSON-based model configuration with IDE support
- Schema validation and autocomplete
- Multiple provider credentials management
- Unified custom configuration via `models custom` command

**Key Configuration Files:**
- Model settings: JSON schema-validated configuration
- Custom models: Centralized provider and model definitions
- Default settings: `set-model default` for new plan defaults

### Current Provider Support (v2.2.x)
The system now supports the following built-in providers:

| Provider | Environment Variable | Capabilities |
|----------|---------------------|--------------|
| OpenAI | `OPENAI_API_KEY` | Full feature set |
| Anthropic | `ANTHROPIC_API_KEY` | Direct API access |
| Google AI Studio | `GOOGLE_AI_STUDIO_API_KEY` | Gemini models |
| Google Vertex AI | Vertex credentials | Enterprise Gemini |
| Azure OpenAI | Azure credentials | Enterprise OpenAI |
| AWS Bedrock | AWS credentials | Bedrock models |
| OpenRouter | `OPENROUTER_API_KEY` | Aggregated access |
| Ollama | Local connection | Local model serving |
| DeepSeek | `DEEPSEEK_API_KEY` | DeepSeek models |
| Perplexity | `PERPLEXITY_API_KEY` | Perplexity models |

Sources: [releases/cli/CHANGELOG.md:17-31](), [releases/cli/CHANGELOG.md:43-68]()

## Command Interface Changes

### Traditional CLI Commands (All Versions)
Core commands that remain consistent across versions:

```bash
plandex tell "description"     # Initiate or continue plan
plandex continue              # Continue current plan  
plandex build                 # Build pending changes
plandex apply                 # Apply changes to files
plandex load <path>          # Load context
plandex changes              # Review pending changes
plandex diff                 # Show changes in git diff format
```

### Version 2.x REPL Commands
Interactive REPL-specific commands (prefixed with `\`):

```bash
\tell "description"          # Same as CLI tell
\continue                    # Same as CLI continue
\build                       # Same as CLI build
\apply                       # Same as CLI apply
\load <path>                # Same as CLI load
\set-model                  # Model configuration
\chat "message"             # Chat mode vs tell mode
\send                       # Send multi-line input
```

### Model Management Commands Evolution

**Version 1.x:**
```bash
plandex set-model           # Basic model selection
plandex models              # List available models
```

**Version 2.x:**
```bash
plandex models custom       # Unified custom model management
plandex set-model --json   # JSON configuration mode
plandex models default     # Set default models
plandex model-packs create # Custom model pack creation
```

Sources: [releases/cli/CHANGELOG.md:53-74](), [releases/cli/CHANGELOG.md:114-119]()

## Current State (Version 2.2.1)

The current CLI version represents a mature, multi-provider AI coding agent with the following key characteristics:

**Core Capabilities:**
- Interactive REPL as primary interface
- Multi-provider AI model support with automatic fallbacks
- JSON-based configuration with IDE integration
- Autonomous execution modes with configurable automation levels
- Claude Pro/Max subscription integration
- Built-in Ollama support for local models

**Active Development Areas:**
- Enhanced model provider integrations
- Improved error handling and retry mechanisms  
- Cost optimization through direct provider calls
- Advanced debugging capabilities

The CLI has evolved from a simple command-line interface for AI-assisted coding to a sophisticated autonomous coding agent capable of handling complex, multi-file projects with minimal human intervention.

Sources: [releases/cli/CHANGELOG.md:1-13](), [app/cli/version.txt:1-2]()

---

# Page: Server Release History

# Server Release History

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/server/version.txt](app/server/version.txt)
- [releases/server/CHANGELOG.md](releases/server/CHANGELOG.md)
- [releases/server/versions/0.8.1.md](releases/server/versions/0.8.1.md)

</details>



This document provides a comprehensive changelog of Plandex server versions, tracking API changes, backend improvements, stability enhancements, and feature additions. The server component handles plan execution, AI model integration, data persistence, and API endpoints that the CLI clients interact with.

For information about CLI version history and client-side changes, see [CLI Release History](#8.1).

## Current Server Version

The current server version is **2.1.8** as of the latest release.

Sources: [app/server/version.txt:1]()

## Release Timeline Overview

```mermaid
timeline
    title "Server Release Timeline"
    
    section Early Releases
        Version 0.7.0 : Initial Release
        Version 0.8.0 : User Management
                      : Backend Commands
        Version 0.8.1 : Crash Prevention
                      : Git Repository Fixes
        Version 0.8.2 : Organization Management
                      : File Update Reliability
        Version 0.8.3 : SMTP Configuration
                      : Custom OpenAI Endpoints
        Version 0.8.4 : New OpenAI Models
                      : Default Model Updates
    
    section Major Overhaul
        Version 0.9.0 : Custom Models Support
                      : Plan Management Commands
                      : Accuracy Improvements
        Version 0.9.1 : Auto-continue Logic
                      : Pipe Data Naming
    
    section 1.0 Milestone
        Version 1.0.0 : GPT-4o Integration
                      : Syntax Validation
                      : Planning Engine Overhaul
        Version 1.0.1 : Rate Limit Handling
                      : Error Fixes
        Version 1.1.0 : Stream Optimization
                      : Claude 3.5 Support
        Version 1.1.1 : Stream Handling
                      : Performance Improvements
    
    section 2.0 Architecture
        Version 2.0.0 : Major Architecture Update
        Version 2.0.2 : Context Auto-load Fix
        Version 2.0.3 : Crash Prevention
        Version 2.0.4 : Database Locking
                      : API Enhancements
        Version 2.0.5 : Model Reliability
                      : Error Handling
        Version 2.0.6 : Process Management
                      : Command Execution
    
    section Current Era
        Version 2.1.0 : Feature Additions
        Version 2.1.1 : Context Error Handling
        Version 2.1.2 : Auto-load Fixes
        Version 2.1.3 : Model Pack Fixes
        Version 2.1.4 : File Edit Improvements
        Version 2.1.5-2.1.8 : Stability Updates
                            : Conversation Fixes
```

Sources: [releases/server/CHANGELOG.md:1-249]()

## Server Component Release Impact

```mermaid
graph TB
    subgraph "Server Architecture Evolution"
        HTTPServer["HTTP Server<br/>REST API Endpoints"]
        PlanEngine["Plan Execution Engine<br/>execTellPlan, execBuildPlan"]
        ModelClient["Model Integration<br/>OpenAI, Anthropic clients"]
        DatabaseOps["Database Operations<br/>PostgreSQL schema"]
        GitOps["Git Repository Management<br/>Per-plan versioning"]
        StreamHandler["Stream Processing<br/>Real-time updates"]
    end
    
    subgraph "Version 0.7-0.8 Foundation"
        v07["Version 0.7.0<br/>Initial Release"]
        v08["Version 0.8.x<br/>User Management<br/>SMTP Config<br/>Crash Prevention"]
    end
    
    subgraph "Version 0.9-1.0 Enhancement"
        v09["Version 0.9.x<br/>Custom Models<br/>Plan Commands<br/>Auto-continue"]
        v10["Version 1.0.x<br/>GPT-4o Default<br/>Syntax Validation<br/>Stream Optimization"]
    end
    
    subgraph "Version 2.0-2.1 Maturity"
        v20["Version 2.0.x<br/>Architecture Overhaul<br/>Database Locking<br/>Process Management"]
        v21["Version 2.1.x<br/>Stability Focus<br/>Error Handling<br/>Queue Management"]
    end
    
    v07 --> HTTPServer
    v07 --> PlanEngine
    v07 --> DatabaseOps
    
    v08 --> HTTPServer
    v08 --> DatabaseOps
    v08 --> GitOps
    
    v09 --> ModelClient
    v09 --> PlanEngine
    v09 --> StreamHandler
    
    v10 --> ModelClient
    v10 --> PlanEngine
    v10 --> StreamHandler
    
    v20 --> DatabaseOps
    v20 --> PlanEngine
    v20 --> GitOps
    
    v21 --> StreamHandler
    v21 --> PlanEngine
    v21 --> ModelClient
```

Sources: [releases/server/CHANGELOG.md:1-249]()

## Detailed Release History

### Version 2.1.x Series (Current) - Stability and Reliability Focus

| Version | Key Changes | Critical Fixes |
|---------|-------------|----------------|
| **2.1.8** | File map queue hang protection | Queue processing reliability |
| **2.1.7** | Conversation summary error fixes | Stream panic prevention, goroutine protection |
| **2.1.6+1** | See CLI release | Coordinated client-server updates |
| **2.1.6** | See CLI release | Feature parity maintenance |
| **2.1.5** | See CLI release | Synchronized functionality |
| **2.1.4** | File editing improvements | Removal of extraneous blank lines |
| **2.1.3** | Model pack error handling | Fix for `execTellPlan` panic with incomplete model packs |
| **2.1.2** | Context loading fixes | Auto-load context EOF error resolution |
| **2.1.1+1** | Enhanced error handling | Anthropic context length error message variations |
| **2.1.1** | See CLI release | Cross-component stability |
| **2.1.0+1** | Context length fallback | Improved retry mechanism for context exceeded errors |
| **2.1.0** | See CLI release | Major feature alignment |

Sources: [releases/server/CHANGELOG.md:1-37]()

### Version 2.0.x Series - Architecture Modernization

| Version | Focus Area | Major Improvements |
|---------|------------|-------------------|
| **2.0.6** | Process Management | Command execution cleanup, model request logging reduction |
| **2.0.5** | Model Reliability | Enhanced error handling, rate limit management, retry logic fixes |
| **2.0.4** | Database & API | Enhanced locking mechanisms, custom model endpoints, process lifecycle |
| **2.0.3** | Crash Prevention | Chat/tell operation fixes, panic handling, queue management |
| **2.0.2** | Context Loading | Auto-load hanging fixes for invalid context scenarios |
| **2.0.0+2** | DevOps | GitHub Action fixes for DockerHub deployment |
| **2.0.0+1** | Model Management | Custom model creation, version check fixes, container deployment |
| **2.0.0** | Major Release | See CLI 2.0.0 for comprehensive changes |

Sources: [releases/server/CHANGELOG.md:39-85]()

### Version 1.x Series - Performance and Intelligence Leap

#### Version 1.1.x - Stream Processing Optimization
- **1.1.1**: Stream handling improvements reducing terminal flickering and CPU usage
- **1.1.0**: Note naming automation, summarization fixes, verification improvements, rate limit handling

#### Version 1.0.x - GPT-4o Integration Milestone
- **1.0.1**: Error handling for verify state, Git operations, rate limit parsing with automatic retry
- **1.0.0**: Major release featuring GPT-4o as default model, automatic syntax validation, planning engine improvements

Key technical improvements in 1.0.0:
- 90% reduction in syntax errors through validation pipeline
- 2x performance improvement with GPT-4o
- Enhanced memory management for complex plans
- Automatic correction step for file updates

Sources: [releases/server/CHANGELOG.md:87-182]()

### Version 0.9.x Series - Customization and Accuracy

| Version | Primary Focus | Technical Enhancements |
|---------|---------------|----------------------|
| **0.9.1** | Auto-continue Logic | Summary incorporation, pipe data naming via `namer` role |
| **0.9.0** | Custom Models | Model packs, default models, file update accuracy, plan management commands |

Major 0.9.0 server-side additions:
- Support for `plandex diff` command
- Plan archiving/unarchiving functionality  
- `plandex summary` command backend
- `plandex rename` command support
- Enhanced commit message generation

Sources: [releases/server/CHANGELOG.md:183-201]()

### Version 0.8.x Series - Foundation and Stability

| Version | Core Improvements | Infrastructure |
|---------|------------------|----------------|
| **0.8.4** | Model Support | GPT-4-turbo integration, default model updates, file handling |
| **0.8.3** | Configuration | SMTP_FROM, OPENAI_ENDPOINT, OPENAI_ORG_ID environment variables |
| **0.8.2** | Organization Management | Domain-based auto-add, crash prevention, file update reliability |
| **0.8.1** | Crash Prevention | Git repo locking fixes, server stability, build improvements |
| **0.8.0** | User Management | Backend for `invite`, `users`, `revoke` commands, email improvements |

Sources: [releases/server/CHANGELOG.md:202-242](), [releases/server/versions/0.8.1.md:1-11]()

### Version 0.7.x Series - Initial Release

- **0.7.1**: SMTP fixes, `/version` endpoint addition
- **0.7.0**: Initial public release establishing core server functionality

Sources: [releases/server/CHANGELOG.md:243-249]()

## Key Technical Evolution Areas

```mermaid
graph LR
    subgraph "Error Handling Evolution"
        EH1["v0.8.1<br/>Basic Crash Prevention"]
        EH2["v1.0.0<br/>Syntax Validation"]
        EH3["v2.0.5<br/>Model Error Classification"]
        EH4["v2.1.7<br/>Goroutine Protection"]
    end
    
    subgraph "Model Integration Maturity"
        MI1["v0.8.4<br/>GPT-4-turbo Support"]
        MI2["v0.9.0<br/>Custom Models"]
        MI3["v1.0.0<br/>GPT-4o Default"]
        MI4["v2.0.4<br/>Model Pack Endpoints"]
    end
    
    subgraph "Performance Optimization"
        PO1["v1.0.0<br/>2x Speed Improvement"]
        PO2["v1.1.1<br/>Stream Optimization"]
        PO3["v2.0.6<br/>Process Management"]
        PO4["v2.1.8<br/>Queue Protection"]
    end
    
    subgraph "Data Management"
        DM1["v0.8.0<br/>User Management"]
        DM2["v2.0.4<br/>Database Locking"]
        DM3["v2.1.2<br/>Context Auto-load"]
        DM4["v2.1.7<br/>Conversation State"]
    end
    
    EH1 --> EH2 --> EH3 --> EH4
    MI1 --> MI2 --> MI3 --> MI4
    PO1 --> PO2 --> PO3 --> PO4
    DM1 --> DM2 --> DM3 --> DM4
```

Sources: [releases/server/CHANGELOG.md:1-249]()