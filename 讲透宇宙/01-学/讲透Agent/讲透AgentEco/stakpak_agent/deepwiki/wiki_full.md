# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Cargo.lock](Cargo.lock)
- [Cargo.toml](Cargo.toml)
- [README.md](README.md)
- [assets/stakpak-dark.png](assets/stakpak-dark.png)
- [assets/stakpak-light.png](assets/stakpak-light.png)
- [cli/Cargo.toml](cli/Cargo.toml)
- [tui/Cargo.toml](tui/Cargo.toml)

</details>



## Purpose and Scope

The stakpak agent is an AI-powered DevOps assistant designed with enterprise-grade security features. This system provides a secure, interactive terminal interface for DevOps tasks while maintaining strict controls over sensitive data through dynamic secret redaction, mutual TLS encryption, and privacy-first architecture.

This document covers the high-level architecture and core components of the stakpak system. For detailed information about specific subsystems, see: CLI Interface ([#2](#2)), Terminal User Interface ([#3](#3)), MCP System ([#4](#4)), Security and Privacy ([#6](#6)), and Deployment ([#7](#7)).

## System Architecture

The Stakpak Agent is implemented as a Rust workspace with 12 crates organized into three tiers: user-facing applications, core libraries, and MCP components.

### Workspace Structure and Dependencies

The workspace follows a dependency hierarchy where the CLI orchestrates all major components, while the TUI provides a focused interactive interface.

```mermaid
graph TB
    subgraph "User-Facing Applications"
        CLI["stakpak<br/>(cli/main.rs)<br/>Binary: stakpak"]
        TUI["stakpak-tui<br/>(tui/lib.rs)<br/>Library crate"]
    end
    
    subgraph "Core Libraries"
        API["stakpak-api<br/>(libs/api)<br/>AgentProvider trait"]
        AI["stakai<br/>(libs/ai)<br/>LLM integration"]
        SHARED["stakpak-shared<br/>(libs/shared)<br/>Common types"]
    end
    
    subgraph "MCP Components"
        MCPS["stakpak-mcp-server<br/>(libs/mcp/server)<br/>ToolContainer"]
        MCPC["stakpak-mcp-client<br/>(libs/mcp/client)<br/>Client wrapper"]
        MCPP["stakpak-mcp-proxy<br/>(libs/mcp/proxy)<br/>Session router"]
    end
    
    subgraph "Supporting Libraries"
        POPUP["stakpak-popup-widget<br/>(libs/popup-widget)<br/>TUI component"]
    end
    
    CLI --> TUI
    CLI --> API
    CLI --> MCPS
    CLI --> MCPC
    CLI --> MCPP
    
    TUI --> API
    TUI --> SHARED
    TUI --> POPUP
    
    API --> SHARED
    API --> AI
    
    MCPS --> SHARED
    MCPC --> SHARED
    MCPP --> SHARED
```

**Sources:** [Cargo.toml:1-94](), [cli/Cargo.toml:1-61](), [tui/Cargo.toml:1-51]()

### Runtime Architecture: CLI to TUI Communication

The CLI determines execution mode based on command-line flags. In async mode, it runs agent logic directly. In interactive mode, it spawns the TUI as a subprocess with bidirectional event channels.

```mermaid
graph TB
    subgraph "CLI Process"
        MAIN["cli/main.rs<br/>Entry point"]
        CONFIG["Configuration<br/>~/.stakpak/config.toml"]
        ROUTER["Agent Logic Router"]
        ASYNC["mode_async.rs<br/>Non-interactive loop"]
        INTERACTIVE["mode_interactive.rs<br/>TUI spawner"]
    end
    
    subgraph "TUI Process"
        TUI_ENTRY["tui::run_tui<br/>Entry point"]
        EVENT_LOOP["Event Loop<br/>Crossterm events"]
        INPUT_CHAN["InputEvent Channel<br/>Keyboard/mouse"]
        OUTPUT_CHAN["OutputEvent Channel<br/>Backend requests"]
        
        APPSTATE["AppState<br/>Central state store"]
        UPDATE["update Function<br/>Event handlers"]
        VIEW["view Function<br/>Ratatui rendering"]
    end
    
    subgraph "Backend Services"
        PROVIDER["AgentProvider Trait<br/>RemoteClient | LocalClient"]
        MCP_CLIENT["MCP Client<br/>Tool execution"]
        LLM["LLM Services<br/>OpenAI/Anthropic"]
    end
    
    MAIN --> CONFIG
    CONFIG --> ROUTER
    ROUTER --> ASYNC
    ROUTER --> INTERACTIVE
    
    INTERACTIVE --> TUI_ENTRY
    TUI_ENTRY --> EVENT_LOOP
    EVENT_LOOP --> INPUT_CHAN
    INPUT_CHAN --> UPDATE
    UPDATE --> APPSTATE
    APPSTATE --> VIEW
    VIEW --> EVENT_LOOP
    
    UPDATE --> OUTPUT_CHAN
    OUTPUT_CHAN --> INTERACTIVE
    
    INTERACTIVE --> PROVIDER
    INTERACTIVE --> MCP_CLIENT
    ASYNC --> PROVIDER
    ASYNC --> MCP_CLIENT
    
    PROVIDER --> LLM
```

**Sources:** [Cargo.toml:3-12](), [cli/Cargo.toml:11-17](), [tui/Cargo.toml:10-13]()

### AgentProvider Architecture

The `AgentProvider` trait abstracts backend interactions with 14 async methods. Two implementations enable different deployment models: `RemoteClient` for hosted services and `LocalClient` for local/offline operation.

```mermaid
graph TB
    subgraph "AgentProvider Trait - libs/api"
        TRAIT["pub trait AgentProvider<br/>14 async methods"]
        
        ACCOUNT["get_my_account<br/>get_billing_info"]
        RULEBOOKS["list_rulebooks<br/>get_rulebook<br/>create_rulebook<br/>delete_rulebook"]
        SESSIONS["list_sessions<br/>get_session<br/>checkpoint operations"]
        CHAT["chat_completion<br/>chat_completion_stream"]
        SEARCH["search_docs<br/>search_memory<br/>memorize"]
        SLACK["read_messages<br/>read_replies<br/>send_message"]
        
        TRAIT --> ACCOUNT
        TRAIT --> RULEBOOKS
        TRAIT --> SESSIONS
        TRAIT --> CHAT
        TRAIT --> SEARCH
        TRAIT --> SLACK
    end
    
    subgraph "RemoteClient"
        REMOTE["RemoteClient<br/>HTTP client<br/>reqwest backend"]
        STAKPAK_API["Stakpak Backend API<br/>STAKPAK_API_KEY auth"]
    end
    
    subgraph "LocalClient"
        LOCAL["LocalClient<br/>Local LLM calls"]
        STAKAI["StakAI Client<br/>Direct provider calls"]
        SQLITE["SQLite Database<br/>.stakpak/session/"]
        HOOKS["HookRegistry<br/>Lifecycle events"]
        SEARCH_ORCH["SearchServicesOrchestrator<br/>Docker SearXNG"]
    end
    
    TRAIT --> REMOTE
    TRAIT --> LOCAL
    
    REMOTE --> STAKPAK_API
    
    LOCAL --> STAKAI
    LOCAL --> SQLITE
    LOCAL --> HOOKS
    LOCAL --> SEARCH_ORCH
    
    STAKAI --> LLM1["OpenAI API"]
    STAKAI --> LLM2["Anthropic API"]
    STAKAI --> LLM3["Google Gemini"]
```

**Sources:** [Cargo.toml:26-32](), [cli/Cargo.toml:12]()

## Core Components

### Command Line Interface (CLI)

The `stakpak` binary ([cli/main.rs]()) serves as the main entry point with argument parsing via `clap`. It routes execution to different modes based on subcommands:

| Subcommand | Module | Purpose |
|------------|--------|---------|
| (default) | `mode_interactive.rs` | Spawns TUI for interactive agent sessions |
| `--async` | `mode_async.rs` | Runs agent in batch mode without TUI |
| `mcp start` | `libs/mcp/server` | Starts MCP server with configurable tool modes |
| `mcp proxy` | `libs/mcp/proxy` | Starts MCP proxy with upstream server routing |
| `acp` | ACP protocol handler | Starts Agent Client Protocol server for editors |
| `config` | Configuration manager | Manages profiles and API keys |
| `rulebooks` | Rulebook CRUD | Manages organizational SOPs and policies |
| `account` | Account viewer | Displays current account and billing info |

The CLI manages configuration loading from `~/.stakpak/config.toml`, profile selection, and API key authentication.

**Sources:** [cli/Cargo.toml:1-61](), [Cargo.toml:1-12]()

### Terminal User Interface (TUI)

The `stakpak-tui` crate ([tui/lib.rs]()) implements a unidirectional data flow architecture using Ratatui. The main entry point is the `run_tui` function, which establishes:

- **Event Loop**: Processes `crossterm` terminal events and converts them to strongly-typed `InputEvent` enums (90+ variants)
- **State Management**: Central `AppState` struct with 6 subsystems (input, messages, tools, popups, shell, session)
- **Update Dispatcher**: Routes events to specialized handlers (input.rs, popup.rs, shell.rs, tool.rs, commands.rs)
- **View Function**: Renders UI from `AppState` using Ratatui widgets with caching for performance
- **Output Channel**: Emits `OutputEvent` enums for backend operations (tool calls, chat requests)

The TUI communicates with the CLI via bidirectional channels, maintaining session state and providing visual feedback for agent operations.

**Sources:** [tui/Cargo.toml:1-51](), [Cargo.toml:31]()

### Model Context Protocol (MCP) System

The MCP system provides dual functionality:

#### MCP Server (`stakpak-mcp-server`)
Exposes Stakpak's tools to external AI systems through the Model Context Protocol. The `ToolContainer` struct ([libs/mcp/server]()) implements 11 tools:

- **Local Tools**: `run_command`, `run_command_task`, `view`, `create`, `str_replace`, `remove`, `get_all_tasks`, `cancel_task`, `wait_for_tasks`, `generate_password`, `view_web_page`
- **Remote Operations**: `RemoteConnectionManager` handles SSH/SFTP for remote system access
- **Task Management**: `TaskManager` enables asynchronous execution with status tracking
- **Security**: `SecretManager` provides Gitleaks-based secret redaction, mTLS encryption, and privacy mode

Three tool modes are available: `local` (no API key required), `remote` (AI tools only), and `combined` (default).

#### MCP Client (`stakpak-mcp-client`)
Wraps the `rmcp` crate to consume tools from MCP servers. Handles tool discovery, invocation, filtering by `allowed_tools` configuration, and result processing.

#### MCP Proxy (`stakpak-mcp-proxy`)
Multiplexes connections to multiple upstream MCP servers using `mcp.toml` configuration. Manages sessions, routes requests to appropriate upstream servers, and provides centralized secret redaction.

**Sources:** [Cargo.toml:28-30](), [cli/Cargo.toml:13-15]()

### API Client and Shared Libraries

#### `stakpak-api`
Defines the `AgentProvider` trait with two implementations:
- **`RemoteClient`**: HTTP client using `reqwest` to communicate with Stakpak's hosted API
- **`LocalClient`**: Direct LLM integration via `stakai`, SQLite session storage, and Docker-based search orchestration

The trait provides 14 methods grouped into: account management, rulebook CRUD, session operations, chat completion, search/memory, and Slack integration.

#### `stakpak-shared`
Contains common types and utilities used across all crates:
- Data models: `AgentSession`, `ChatMessage`, `Tool`, `Block`, `Dependency`
- Security utilities: Secret management, privacy filtering, validation
- Configuration types: Profile definitions, authentication credentials

**Sources:** [Cargo.toml:26-27,32]()

## Key Features

### Security Architecture

| Feature | Implementation | Code Location |
|---------|---------------|---------------|
| **Mutual TLS (mTLS)** | End-to-end encrypted MCP connections using `rustls` and `rcgen` for certificate generation | [libs/mcp/server]() |
| **Secret Substitution** | Dynamic secret redaction/restoration using Gitleaks patterns. Secrets replaced with placeholders before LLM processing | [libs/mcp/server]() SecretManager |
| **Privacy Mode** | Redacts IP addresses, AWS account IDs, and other PII using configurable patterns | [libs/shared]() |
| **Password Generation** | Cryptographically secure passwords via `generate_password` tool with complexity rules | [libs/mcp/server]() ToolContainer |

### Tool Execution System

The MCP server implements sophisticated tool routing:

```mermaid
graph TB
    TOOL_CALL["Tool Call from LLM"]
    PATH_DETECT["Path Detection<br/>is_remote_path?"]
    
    LOCAL["Local Execution<br/>std::process::Command<br/>FileBackupManager"]
    REMOTE["Remote Execution<br/>RemoteConnectionManager<br/>SSH/SFTP via russh"]
    
    ASYNC["Async Execution<br/>TaskManager::start_task<br/>Background tracking"]
    
    SECRET["SecretManager<br/>Redact → Execute → Restore"]
    OUTPUT["Output Processing<br/>Large file handler<br/>ANSI sanitization"]
    
    TOOL_CALL --> PATH_DETECT
    PATH_DETECT -->|"Local path"| LOCAL
    PATH_DETECT -->|"user@host:path"| REMOTE
    PATH_DETECT -->|"--async flag"| ASYNC
    
    LOCAL --> SECRET
    REMOTE --> SECRET
    ASYNC --> SECRET
    
    SECRET --> OUTPUT
```

**Key capabilities:**
- **Task Management**: `TaskManager` tracks background processes with `start_task`, `cancel_task`, `wait_for_tasks`, and `get_all_tasks` APIs
- **Remote Operations**: `RemoteConnectionManager` pools SSH connections with password or key-based authentication
- **File Backups**: `FileBackupManager` automatically backs up modified files to `.stakpak_backup/` for recovery
- **Progress Streaming**: Long-running commands stream output updates for real-time feedback

**Sources:** [Cargo.toml:74-78](), [cli/Cargo.toml:39]()

### Configuration and Context Injection

Stakpak injects context into agent prompts through multiple sources:

| Context Source | Description | Storage |
|----------------|-------------|---------|
| **Rulebooks** | Markdown files with YAML frontmatter defining SOPs, playbooks, and policies | Remote API or local SQLite |
| **AGENTS.md** | Local file in current directory defining agent-specific instructions | Current working directory |
| **Session Memory** | Persistent knowledge from previous interactions via `memorize` and `search_memory` | SQLite database or remote API |
| **Subagents** | Specialized research agents with restricted tool access (enabled via `--enable-subagents`) | In-memory during session |
| **Local Context** | Automatic indexing of Terraform, Kubernetes, Docker, and GitHub Actions files | `.stakpak/` directory |

Configuration is managed via TOML profiles supporting:
- **BYOK (Bring Your Own Keys)**: Direct provider credentials for Anthropic, OpenAI, Gemini, AWS Bedrock
- **BYOL (Bring Your Own LLM)**: Custom OpenAI-compatible endpoints (Ollama, LM Studio)
- **Hybrid**: Mix of built-in and custom providers

**Sources:** [README.md:143-218]()

### Session Management

Sessions support checkpointing and resumption:

```mermaid
graph LR
    START["stakpak<br/>New session"]
    SESSION["Session Storage<br/>SQLite or API"]
    CHECKPOINT["Checkpoint Created<br/>Full state snapshot"]
    RESUME["stakpak -c <id><br/>Resume execution"]
    
    START --> SESSION
    SESSION --> CHECKPOINT
    CHECKPOINT --> RESUME
    RESUME --> SESSION
```

Each session maintains:
- Conversation history with full message context
- Tool call results and approval state
- Profile configuration and model selection
- Environment variables and working directory
- Pending operations and background tasks

**Sources:** [README.md:224-226]()

## Installation and Basic Usage

### Installation Methods

The stakpak agent supports multiple installation methods:

| Method | Command | Platforms |
|--------|---------|-----------|
| Homebrew | `brew tap stakpak/stakpak && brew install stakpak` | Linux, macOS |
| Binary Release | Download from GitHub Releases | Linux, macOS, Windows |
| Docker | `docker pull ghcr.io/stakpak/agent:latest` | All platforms |

### Authentication and Configuration

The system requires an API key for full functionality:

```bash
# Set environment variable
export STAKPAK_API_KEY=<your-key>

# Or save to configuration file
stakpak login --api-key $STAKPAK_API_KEY
```

### Execution Modes

The CLI supports multiple execution modes:

```bash
# Interactive TUI mode (default)
stakpak

# Resume from checkpoint
stakpak -c <checkpoint-id>

# MCP server mode with different tool configurations
stakpak mcp --tool-mode local    # Local tools only
stakpak mcp --tool-mode remote   # Remote AI tools only  
stakpak mcp --tool-mode combined # All tools (default)
```

**Sources:** [README.md:29-149](), [.github/workflows/build-and-release.yml:1-233]()

---

# Page: System Architecture

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Cargo.lock](Cargo.lock)
- [Cargo.toml](Cargo.toml)
- [README.md](README.md)
- [assets/stakpak-dark.png](assets/stakpak-dark.png)
- [assets/stakpak-light.png](assets/stakpak-light.png)
- [cli/Cargo.toml](cli/Cargo.toml)
- [cli/src/commands/agent/run/helpers.rs](cli/src/commands/agent/run/helpers.rs)
- [cli/src/commands/agent/run/mode_async.rs](cli/src/commands/agent/run/mode_async.rs)
- [cli/src/commands/agent/run/mode_interactive.rs](cli/src/commands/agent/run/mode_interactive.rs)
- [cli/src/commands/mod.rs](cli/src/commands/mod.rs)
- [cli/src/main.rs](cli/src/main.rs)
- [tui/Cargo.toml](tui/Cargo.toml)

</details>



This document explains the overall system architecture of Stakpak, detailing how the CLI, TUI, MCP components, and API layer interact to provide an AI-powered DevOps agent. The architecture is organized as a Rust workspace with clear separation between user interface (CLI/TUI), business logic (API abstraction), and tool execution (MCP system).

The system supports two primary execution modes: **interactive mode** (TUI-based) and **async mode** (batch processing). Both modes share the same backend services through the `AgentProvider` trait abstraction, which supports both remote (Stakpak hosted API) and local (direct LLM) implementations.

For CLI commands and usage, see [CLI Interface](#2). For TUI internals, see [Terminal User Interface (TUI)](#3). For tool execution details, see [MCP System](#5).

## Workspace Structure and Crate Dependencies

The Stakpak agent is organized as a Cargo workspace with 11 crates, defined in the root [Cargo.toml:1-13](). The workspace uses resolver version 2 and shares common dependencies across all members.

| Crate | Path | Purpose |
|-------|------|---------|
| `stakpak` | `cli/` | Main CLI executable, entry point at [cli/src/main.rs:146-512]() |
| `stakpak-tui` | `tui/` | Terminal UI library, entry point `run_tui()` |
| `stakpak-api` | `libs/api/` | `AgentProvider` trait and implementations (`RemoteClient`, `LocalClient`) |
| `stakai` | `libs/ai/` | LLM client integrations (OpenAI, Anthropic, Google, AWS Bedrock) |
| `stakpak-shared` | `libs/shared/` | Common models and utilities shared across all crates |
| `stakpak-mcp-client` | `libs/mcp/client/` | MCP client for tool discovery and invocation |
| `stakpak-mcp-server` | `libs/mcp/server/` | MCP server exposing Stakpak tools (`ToolContainer` with 11 tools) |
| `stakpak-mcp-proxy` | `libs/mcp/proxy/` | MCP proxy for multiplexing upstream servers |
| `stakpak-popup-widget` | `libs/popup-widget/` | Ratatui popup widget for TUI |

**Workspace Dependency Graph**

```mermaid
graph TB
    CLI["stakpak (cli)"]
    TUI["stakpak-tui (tui)"]
    API["stakpak-api (libs/api)"]
    AI["stakai (libs/ai)"]
    Shared["stakpak-shared (libs/shared)"]
    MCPClient["stakpak-mcp-client"]
    MCPServer["stakpak-mcp-server"]
    MCPProxy["stakpak-mcp-proxy"]
    PopupWidget["stakpak-popup-widget"]
    
    CLI --> TUI
    CLI --> API
    CLI --> MCPClient
    CLI --> MCPServer
    CLI --> MCPProxy
    CLI --> Shared
    
    TUI --> API
    TUI --> Shared
    TUI --> PopupWidget
    
    API --> Shared
    API --> AI
    
    MCPServer --> Shared
    MCPClient --> Shared
    MCPProxy --> Shared
    
    subgraph "Key External Dependencies"
        RMCP["rmcp 0.11.0<br/>MCP protocol"]
        Tokio["tokio 1.x<br/>Async runtime"]
        Ratatui["ratatui 0.29.0<br/>TUI framework"]
        Crossterm["crossterm 0.29<br/>Terminal control"]
        Reqwest["reqwest 0.12.15<br/>HTTP client"]
    end
    
    MCPClient --> RMCP
    MCPServer --> RMCP
    MCPProxy --> RMCP
    CLI --> Tokio
    TUI --> Ratatui
    TUI --> Crossterm
    API --> Reqwest
```

The workspace uses shared version management through `[workspace.dependencies]` at [Cargo.toml:25-88](). Critical shared dependencies include `rmcp` (0.11.0) for MCP protocol, `tokio` for async runtime, `ratatui` (0.29.0) for TUI, and `reqwest` (0.12.15) for HTTP clients.

**Sources:** [Cargo.toml:1-94](), [cli/Cargo.toml:1-61](), [tui/Cargo.toml:1-51]()

## Core Components and Runtime Architecture

The system uses a layered architecture with the CLI as the orchestrator, dispatching to execution modes that share backend services through the `AgentProvider` abstraction.

**Component Interaction with Code Entities**

```mermaid
graph TB
    subgraph "CLI Entry Point"
        MainFn["main() in cli/src/main.rs:146"]
        CliParser["Cli struct (clap parser)"]
        ConfigLoad["AppConfig::load()"]
    end
    
    subgraph "Execution Mode Routing"
        CommandsEnum["Commands enum"]
        AgentInteractive["run_interactive()<br/>mode_interactive.rs:69"]
        AgentAsync["run_async()<br/>mode_async.rs:49"]
        SubcommandHandler["Commands::run()"]
    end
    
    subgraph "Backend Provider Layer"
        AgentProviderTrait["AgentProvider trait<br/>(14 async methods)"]
        RemoteClientImpl["RemoteClient<br/>(HTTP to Stakpak API)"]
        LocalClientImpl["LocalClient<br/>(Direct LLM calls)"]
    end
    
    subgraph "TUI Runtime"
        RunTuiFn["stakpak_tui::run_tui()"]
        AppState["AppState<br/>(central state)"]
        EventLoop["Event loop<br/>(InputEvent/OutputEvent)"]
    end
    
    subgraph "MCP System"
        McpInitFn["initialize_mcp_server_and_tools()"]
        ToolContainer["ToolContainer<br/>(11 tools)"]
        TaskManager["TaskManager<br/>(async execution)"]
        RemoteConnMgr["RemoteConnectionManager<br/>(SSH/SFTP)"]
    end
    
    MainFn --> CliParser
    CliParser --> ConfigLoad
    ConfigLoad --> CommandsEnum
    
    CommandsEnum -->|"No command"| AgentInteractive
    CommandsEnum -->|"--async flag"| AgentAsync
    CommandsEnum -->|"Subcommand"| SubcommandHandler
    
    AgentInteractive --> RunTuiFn
    AgentInteractive --> AgentProviderTrait
    AgentAsync --> AgentProviderTrait
    SubcommandHandler --> AgentProviderTrait
    
    AgentProviderTrait -->|"ProviderType::Remote"| RemoteClientImpl
    AgentProviderTrait -->|"ProviderType::Local"| LocalClientImpl
    
    RunTuiFn --> AppState
    AppState --> EventLoop
    
    AgentInteractive --> McpInitFn
    AgentAsync --> McpInitFn
    McpInitFn --> ToolContainer
    ToolContainer --> TaskManager
    ToolContainer --> RemoteConnMgr
```

The CLI at [cli/src/main.rs:146]() parses arguments using `clap` and determines execution mode. The `AppConfig` type (from `cli/src/config.rs`) manages configuration and credentials. The `AgentProvider` trait (from `libs/api/`) abstracts backend differences, with `RemoteClient` for hosted API and `LocalClient` for local LLM execution.

In interactive mode, `run_interactive()` at [cli/src/commands/agent/run/mode_interactive.rs:69]() spawns the TUI subprocess and establishes bidirectional channels (`InputEvent`/`OutputEvent`). In async mode, `run_async()` at [cli/src/commands/agent/run/mode_async.rs:49]() executes the agent in a loop without UI.

Both modes call `initialize_mcp_server_and_tools()` to set up the MCP system, which instantiates the `ToolContainer` with 11 tools, a `TaskManager` for async operations, and `RemoteConnectionManager` for SSH/SFTP.

**Sources:** [cli/src/main.rs:1-513](), [cli/src/commands/agent/run/mode_interactive.rs:1-100](), [cli/src/commands/agent/run/mode_async.rs:1-50](), [cli/src/commands/mod.rs:1-203]()

## Execution Flow with Code References

The CLI orchestrates different execution paths based on parsed arguments. All paths share the same backend abstraction through `AgentProvider`, ensuring consistent behavior.

**Detailed Execution Flow**

```mermaid
flowchart TD
    Start["main() entry<br/>cli/src/main.rs:146"]
    
    CliParse["Cli::parse()<br/>(clap derives)"]
    
    ConfigLoad["AppConfig::load()<br/>Profile selection"]
    
    WardenCheck{"Warden enabled?<br/>config.warden.enabled"}
    
    ModeCheck{"cli.command?"}
    
    SubcmdPath["Commands::run()<br/>commands/mod.rs:219"]
    
    AgentPath{"cli.async || cli.print?"}
    
    InteractivePath["run_interactive()<br/>mode_interactive.rs:69"]
    AsyncPath["run_async()<br/>mode_async.rs:49"]
    
    McpInit["initialize_mcp_server_and_tools()<br/>McpInitConfig"]
    
    ProviderCreate{"config.provider?"}
    
    RemoteCreate["RemoteClient::new()<br/>ClientConfig"]
    LocalCreate["LocalClient::new()<br/>LocalClientConfig"]
    
    TuiSpawn["tokio::spawn(run_tui)<br/>Separate task"]
    TuiChannels["InputEvent/OutputEvent<br/>mpsc channels"]
    
    AsyncLoop["Loop until max_steps<br/>or no tool_calls"]
    
    ChatCompletion["client.chat_completion()<br/>AgentProvider::chat_completion"]
    
    ToolExec["run_tool_call()<br/>MCP client invocation"]
    
    Start --> CliParse
    CliParse --> ConfigLoad
    ConfigLoad --> WardenCheck
    
    WardenCheck -->|"Yes"| WardenReexec["run_stakpak_in_warden()<br/>Re-execute in container"]
    WardenCheck -->|"No"| ModeCheck
    
    ModeCheck -->|"Some(cmd)"| SubcmdPath
    ModeCheck -->|"None"| AgentPath
    
    AgentPath -->|"true"| AsyncPath
    AgentPath -->|"false"| InteractivePath
    
    InteractivePath --> McpInit
    AsyncPath --> McpInit
    
    McpInit --> ProviderCreate
    
    ProviderCreate -->|"Remote"| RemoteCreate
    ProviderCreate -->|"Local"| LocalCreate
    
    InteractivePath --> TuiSpawn
    TuiSpawn --> TuiChannels
    TuiChannels --> ChatCompletion
    
    AsyncPath --> AsyncLoop
    AsyncLoop --> ChatCompletion
    
    ChatCompletion --> ToolExec
    ToolExec --> ChatCompletion
```

**Key Control Flow Points:**

1. **Entry**: [cli/src/main.rs:146]() initializes the async runtime and parses CLI arguments
2. **Config**: [cli/src/config.rs]() loads profile-based configuration from `~/.stakpak/config.toml`
3. **Warden Check**: If `config.warden.enabled`, re-executes inside Docker container via [cli/src/commands/warden.rs:206]()
4. **Mode Selection**: Based on `cli.command`, `cli.async`, and `cli.print` flags
5. **Provider Selection**: Instantiates either `RemoteClient` or `LocalClient` based on `config.provider`
6. **MCP Initialization**: `initialize_mcp_server_and_tools()` starts MCP server, proxy, and client
7. **Interactive Mode**: Spawns TUI in separate task with mpsc channels for communication
8. **Async Mode**: Executes agent loop directly in main task until completion

The system uses `tokio::spawn` to run the TUI concurrently with the backend agent logic. Communication happens through typed channels: `InputEvent` (UI → Backend) and `OutputEvent` (Backend → UI).

**Sources:** [cli/src/main.rs:146-512](), [cli/src/commands/agent/run/mode_interactive.rs:69-150](), [cli/src/commands/agent/run/mode_async.rs:49-110](), [cli/src/commands/mod.rs:219-468]()

## Deployment and Distribution Architecture

The system supports multiple deployment strategies including native binaries, Docker containers, and package managers. The build pipeline produces cross-platform artifacts with specialized container variants for different use cases.

**Deployment Architecture**

```mermaid
graph TB
    subgraph "Source Code"
        Workspace["Rust Workspace<br/>Multi-crate Structure"]
    end
    
    subgraph "Build Pipeline"
        CargoRelease["cargo build --release<br/>Cross-platform Targets"]
        Testing["cargo test<br/>Platform Testing"]
        Packaging["Binary Packaging<br/>tar.gz / zip"]
    end
    
    subgraph "Distribution Channels"
        GHReleases["GitHub Releases<br/>Binary Artifacts"]
        DockerRegistry["ghcr.io Registry<br/>Container Images"]
        Homebrew["Homebrew Tap<br/>Package Manager"]
    end
    
    subgraph "Container Variants"
        BaseImage["stakpak:latest<br/>Base Agent Image"]
        WardenImage["stakpak-warden:latest<br/>Proxy Wrapper"]
    end
    
    subgraph "Target Platforms"
        LinuxX64["linux/x86_64"]
        LinuxARM["linux/aarch64"]  
        MacosX64["darwin/x86_64"]
        MacosARM["darwin/aarch64"]
        WindowsX64["windows/x86_64"]
    end
    
    Workspace --> CargoRelease
    CargoRelease --> Testing
    Testing --> Packaging
    
    Packaging --> GHReleases
    Packaging --> DockerRegistry
    Packaging --> Homebrew
    
    DockerRegistry --> BaseImage
    DockerRegistry --> WardenImage
    
    GHReleases --> LinuxX64
    GHReleases --> LinuxARM
    GHReleases --> MacosX64
    GHReleases --> MacosARM
    GHReleases --> WindowsX64
```

The deployment strategy ensures broad platform compatibility while providing specialized container images for different operational requirements. The warden container variant adds transparent proxy capabilities for enhanced security in containerized environments.

**Sources:** [.github/workflows/build-and-release.yml:1-233](), [Cargo.toml:14-16]()

---

# Page: Workspace Structure and Packages

# Workspace Structure and Packages

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Cargo.lock](Cargo.lock)
- [Cargo.toml](Cargo.toml)
- [cli/Cargo.toml](cli/Cargo.toml)
- [tui/Cargo.toml](tui/Cargo.toml)

</details>



## Purpose and Scope

This page documents the Cargo workspace structure of the Stakpak codebase, including all member crates, their interdependencies, and shared dependencies. For information about system architecture and how these components interact at runtime, see [System Architecture](#1.1). For build and deployment processes, see [Build System and Deployment](#7).

## Workspace Organization

The Stakpak repository is organized as a Cargo workspace with 8 member crates defined in [Cargo.toml:1-12](). The workspace uses Cargo's version 2 resolver and shares common package metadata and dependencies across all members.

```mermaid
graph TB
    subgraph "Root Workspace"
        CARGO["Cargo.toml<br/>Workspace Definition"]
    end
    
    subgraph "Applications"
        CLI["cli/<br/>stakpak<br/>Main CLI application"]
        TUI["tui/<br/>stakpak-tui<br/>Terminal UI library"]
    end
    
    subgraph "Core Libraries"
        SHARED["libs/shared/<br/>stakpak-shared<br/>Common utilities"]
        API["libs/api/<br/>stakpak-api<br/>AgentProvider trait"]
        AI["libs/ai/<br/>stakai<br/>LLM integrations"]
    end
    
    subgraph "MCP Components"
        MCPS["libs/mcp/server/<br/>stakpak-mcp-server<br/>Tool implementations"]
        MCPC["libs/mcp/client/<br/>stakpak-mcp-client<br/>MCP client library"]
        MCPP["libs/mcp/proxy/<br/>stakpak-mcp-proxy<br/>MCP proxy server"]
    end
    
    subgraph "UI Components"
        POPUP["libs/popup-widget/<br/>stakpak-popup-widget<br/>Popup widget"]
    end
    
    CARGO --> CLI
    CARGO --> TUI
    CARGO --> SHARED
    CARGO --> API
    CARGO --> AI
    CARGO --> MCPS
    CARGO --> MCPC
    CARGO --> MCPP
```

**Workspace Members**

Sources: [Cargo.toml:1-12]()

## Package Catalog

The following table lists all packages in the workspace with their identifiers, locations, and primary purposes:

| Package Name | Crate Name | Location | Purpose |
|--------------|------------|----------|---------|
| **stakpak** | `stakpak` | `cli/` | Main CLI executable providing command-line interface and orchestration |
| **stakpak-tui** | `stakpak_tui` | `tui/` | Terminal user interface library with event loop and rendering system |
| **stakpak-shared** | `stakpak_shared` | `libs/shared/` | Common utilities, models, and types shared across all crates |
| **stakpak-api** | `stakpak_api` | `libs/api/` | AgentProvider trait and implementations (RemoteClient, LocalClient) |
| **stakai** | `stakai` | `libs/ai/` | AI/LLM integrations for multiple providers (OpenAI, Anthropic, etc.) |
| **stakpak-mcp-server** | `stakpak_mcp_server` | `libs/mcp/server/` | MCP server implementation with 11 local tools |
| **stakpak-mcp-client** | `stakpak_mcp_client` | `libs/mcp/client/` | MCP client for invoking tools from external MCP servers |
| **stakpak-mcp-proxy** | `stakpak_mcp_proxy` | `libs/mcp/proxy/` | MCP proxy server for multiplexing upstream MCP servers |
| **stakpak-popup-widget** | `popup_widget` | `libs/popup-widget/` | Reusable popup widget component for TUI |

Sources: [Cargo.toml:3-12](), [cli/Cargo.toml:2](), [tui/Cargo.toml:2]()

## Inter-Crate Dependencies

### Dependency Graph

```mermaid
graph LR
    CLI["cli<br/>(stakpak)"]
    TUI["tui<br/>(stakpak-tui)"]
    API["api<br/>(stakpak-api)"]
    SHARED["shared<br/>(stakpak-shared)"]
    AI["ai<br/>(stakai)"]
    MCPS["mcp/server"]
    MCPC["mcp/client"]
    MCPP["mcp/proxy"]
    POPUP["popup-widget"]
    
    CLI --> TUI
    CLI --> API
    CLI --> SHARED
    CLI --> MCPS
    CLI --> MCPC
    CLI --> MCPP
    
    TUI --> API
    TUI --> SHARED
    TUI --> POPUP
    
    API --> SHARED
    API --> AI
    
    MCPS --> SHARED
    MCPC --> SHARED
    MCPP --> SHARED
    
    AI --> SHARED
```

**CLI Dependencies**

The `stakpak` CLI crate depends on all major components as it serves as the orchestration layer:

Sources: [cli/Cargo.toml:11-17]()

### Primary Dependencies by Package

**stakpak (CLI)**
- `stakpak-api` - Agent provider abstraction
- `stakpak-mcp-server` - Local tool execution
- `stakpak-mcp-client` - External tool invocation  
- `stakpak-mcp-proxy` - MCP proxy functionality
- `stakpak-tui` - Interactive terminal UI
- `stakpak-shared` - Common utilities

Sources: [cli/Cargo.toml:12-17]()

**stakpak-tui (TUI)**
- `stakpak-api` - Backend communication
- `stakpak-shared` - Shared models and utilities
- `popup-widget` - Popup UI components

Sources: [tui/Cargo.toml:11-13]()

**stakpak-api (API)**
- `stakai` - AI/LLM functionality (inferred from system diagrams)
- `stakpak-shared` - Common types

**MCP Components (server, client, proxy)**
- `stakpak-shared` - All MCP components depend on shared utilities

**stakai (AI)**
- `stakpak-shared` - Common types (inferred)

Sources: [Cargo.toml:26-33]()

## Shared Dependencies

The workspace defines common dependencies that are shared across multiple crates. These are specified in [Cargo.toml:25-88]() and ensure version consistency.

### Key Shared Dependencies

| Dependency | Version | Key Features | Used By |
|------------|---------|--------------|---------|
| `serde` | 1.0.215 | `derive` | All crates |
| `serde_json` | 1.0.133 | JSON serialization | All crates |
| `tokio` | 1.x | `full` | Async runtime for all crates |
| `tracing` | 0.1.41 | Logging | CLI, API, MCP components |
| `anyhow` | 1.0.98 | Error handling | All crates |
| `rmcp` | 0.11.0 | MCP protocol implementation | CLI, MCP components |
| `reqwest` | 0.12.15 | `json`, `stream`, `rustls-tls` | CLI, API |
| `ratatui` | 0.29.0 | `scrolling-regions`, `unstable-*` | TUI |
| `chrono` | 0.4.38 | `serde` | Multiple crates |
| `uuid` | 1.10.0 | `serde`, `v4` | Multiple crates |
| `crossterm` | 0.29 | Terminal control | CLI, TUI |
| `regex` | 1.11.1 | Pattern matching | Multiple crates |
| `rustls` | 0.23.29 | TLS support | CLI, MCP components |

Sources: [Cargo.toml:34-88]()

### RMCP Feature Configuration

The `rmcp` dependency is configured with extensive features for MCP protocol support:

```toml
rmcp = { version = "0.11.0", features = [
    "base64",
    "macros",
    "client",
    "server",
    "reqwest",
    "transport-io",
    "transport-child-process",
    "transport-streamable-http-client",
    "transport-streamable-http-client-reqwest",
    "transport-streamable-http-server",
    "transport-streamable-http-server-session",
    "transport-worker",
], default-features = false }
```

This configuration enables multiple transport mechanisms (stdio, child process, HTTP streaming) for both client and server roles.

Sources: [Cargo.toml:41-54]()

## Version Management

### Workspace-Level Versioning

All crates share a common version number managed at the workspace level. The current version is `0.3.13` as defined in [Cargo.toml:17]().

Individual crate `Cargo.toml` files reference the workspace version:

```toml
[package]
version = { workspace = true }
```

This ensures all published crates maintain version parity.

Sources: [Cargo.toml:16-22](), [cli/Cargo.toml:3](), [tui/Cargo.toml:3]()

### Metadata Sharing

Common package metadata is also defined at the workspace level and inherited by member crates:

- `edition = "2024"` - Using Rust 2024 edition
- `license = "Apache-2.0"`
- `repository = "https://github.com/stakpak/agent"`
- `homepage = "https://stakpak.io"`
- `description` - Shared description of Stakpak

Sources: [Cargo.toml:16-22]()

## Build Configuration

### Linting Rules

The workspace enforces strict linting rules through Clippy at [Cargo.toml:91-93]():

```toml
[workspace.lints.clippy]
unwrap_used = "deny"
expect_used = "deny"
```

These rules are inherited by individual crates and prohibit use of `.unwrap()` and `.expect()` methods, requiring explicit error handling throughout the codebase.

Sources: [Cargo.toml:91-93](), [cli/Cargo.toml:58-60](), [tui/Cargo.toml:41-43]()

### Resolver Version

The workspace uses Cargo's version 2 resolver ([Cargo.toml:2]()), which provides improved dependency resolution and feature unification behavior.

## Special Dependencies

### CLI-Specific Dependencies

The CLI crate includes additional dependencies for its broader functionality:

- **Configuration**: `config` (0.14.1) for configuration management
- **CLI Framework**: `clap` (4.5.23) with `derive` and `env` features
- **ACP Protocol**: `agent-client-protocol` (0.9.2) for code editor integration
- **JSON-RPC**: `jsonrpc-core`, `jsonrpc-derive` for RPC server
- **Archive Handling**: `tar`, `flate2`, `zip` for compression
- **Interactive Input**: `rpassword` for secure password input

Sources: [cli/Cargo.toml:20-52]()

### TUI-Specific Dependencies

The TUI crate includes specialized dependencies for terminal rendering:

- **Rendering**: `ratatui` (0.29.0) with advanced features
- **Text Processing**: `textwrap`, `unicode-segmentation`, `unicode-width`
- **Syntax Highlighting**: `syntect` (5.2.0)
- **Fuzzy Matching**: `nucleo-matcher` (0.3.1)
- **ANSI Processing**: `ansi-to-tui` (7.0.0)
- **VT100 Emulation**: `vt100` (0.15.2) for shell mode
- **Platform-Specific**: 
  - `portable-pty` (0.8) for Unix/Windows PTY support
  - `arboard` (3) for clipboard on non-Android platforms

Sources: [tui/Cargo.toml:14-50]()

## Package Publication

### Published Crates

The following crates are published to crates.io:

1. **stakpak** - Main CLI binary
2. **stakpak-tui** - TUI library (can be used independently)
3. **stakpak-api** - API abstraction layer
4. **stakai** - AI/LLM integration library
5. **stakpak-shared** - Shared utilities
6. **stakpak-mcp-server** - MCP server library
7. **stakpak-mcp-client** - MCP client library
8. **stakpak-mcp-proxy** - MCP proxy library

The `popup-widget` crate is published as `stakpak-popup-widget` ([Cargo.toml:33]()).

Sources: [Cargo.toml:26-33]()

## Workspace Structure Summary

```mermaid
graph TB
    subgraph "Build System"
        WORKSPACE["Cargo Workspace<br/>Version: 0.3.13<br/>Edition: 2024"]
        SHARED_DEPS["Shared Dependencies<br/>serde, tokio, rmcp, etc."]
        LINTS["Linting Rules<br/>deny unwrap_used<br/>deny expect_used"]
    end
    
    subgraph "Application Layer"
        CLI["CLI Application<br/>Main orchestrator<br/>All dependencies"]
        TUI["TUI Library<br/>Independent UI layer<br/>Minimal dependencies"]
    end
    
    subgraph "Library Layer"
        API["API Library<br/>AgentProvider abstraction"]
        AI["AI Library<br/>LLM integrations"]
        SHARED["Shared Library<br/>Common utilities"]
    end
    
    subgraph "MCP Layer"
        MCPS["MCP Server<br/>Tool execution"]
        MCPC["MCP Client<br/>Tool invocation"]
        MCPP["MCP Proxy<br/>Server multiplexing"]
    end
    
    subgraph "UI Components"
        POPUP["Popup Widget<br/>Reusable UI"]
    end
    
    WORKSPACE --> SHARED_DEPS
    WORKSPACE --> LINTS
    WORKSPACE --> CLI
    WORKSPACE --> TUI
    WORKSPACE --> API
    WORKSPACE --> AI
    WORKSPACE --> SHARED
    WORKSPACE --> MCPS
    WORKSPACE --> MCPC
    WORKSPACE --> MCPP
    WORKSPACE --> POPUP
    
    CLI -.depends.-> TUI
    CLI -.depends.-> API
    CLI -.depends.-> SHARED
    CLI -.depends.-> MCPS
    CLI -.depends.-> MCPC
    CLI -.depends.-> MCPP
    
    TUI -.depends.-> API
    TUI -.depends.-> SHARED
    TUI -.depends.-> POPUP
    
    API -.depends.-> AI
    API -.depends.-> SHARED
    
    MCPS -.depends.-> SHARED
    MCPC -.depends.-> SHARED
    MCPP -.depends.-> SHARED
```

**Architecture Summary**

The workspace follows a layered architecture:
1. **Application Layer**: CLI orchestrates all components; TUI provides interactive UI
2. **Library Layer**: Core business logic in API, AI, and Shared crates
3. **MCP Layer**: Tool execution infrastructure for local and remote operations
4. **UI Components**: Reusable widgets for terminal interfaces

The `stakpak-shared` crate serves as the foundation, depended upon by nearly all other crates for common types and utilities. The CLI acts as the integration point, pulling together all components to provide the complete Stakpak experience.

Sources: [Cargo.toml:1-94](), [cli/Cargo.toml:1-61](), [tui/Cargo.toml:1-51]()

---

# Page: Installation and Getting Started

# Installation and Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/build-and-release.yml](.github/workflows/build-and-release.yml)
- [README.md](README.md)
- [assets/stakpak-dark.png](assets/stakpak-dark.png)
- [assets/stakpak-light.png](assets/stakpak-light.png)
- [cliff.toml](cliff.toml)
- [libs/popup-widget/Cargo.toml](libs/popup-widget/Cargo.toml)
- [libs/popup-widget/README.md](libs/popup-widget/README.md)
- [release.sh](release.sh)

</details>



This document covers the installation methods, authentication setup, and initial usage patterns for stakpak agent. It provides the essential steps to get the agent running in its various execution modes. For detailed information about system architecture, see [System Architecture](#1.1). For specific CLI commands and execution modes, see [CLI Interface](#2).

## Installation Methods

stakpak is distributed through three primary channels: Homebrew tap, GitHub Releases binary artifacts, and Docker images. The build and release process is automated via GitHub Actions workflow defined in [.github/workflows/build-and-release.yml]().

### Installation Distribution Flow

```mermaid
graph TB
    GitTag["Git Tag (vX.Y.Z)"] --> CI["GitHub Actions Workflow"]
    
    CI --> BuildJob["build job"]
    CI --> PublishJob["publish_crates_io job"]
    CI --> DockerJob["docker job"]
    CI --> HomebrewJob["homebrew job"]
    
    BuildJob --> Matrix["Platform Matrix"]
    Matrix --> Linux64["x86_64-unknown-linux-musl"]
    Matrix --> LinuxArm["aarch64-unknown-linux-musl"]
    Matrix --> Darwin64["x86_64-apple-darwin"]
    Matrix --> DarwinArm["aarch64-apple-darwin"]
    Matrix --> Win64["x86_64-pc-windows-msvc"]
    
    Linux64 --> Artifacts["GitHub Release Artifacts"]
    LinuxArm --> Artifacts
    Darwin64 --> Artifacts
    DarwinArm --> Artifacts
    Win64 --> Artifacts
    
    PublishJob --> CratesIO["crates.io packages"]
    DockerJob --> GHCR["ghcr.io/stakpak/agent"]
    HomebrewJob --> Formula["stakpak/homebrew-stakpak"]
    
    Artifacts --> Users["End Users"]
    CratesIO --> CargoInstall["cargo install stakpak"]
    GHCR --> DockerPull["docker pull"]
    Formula --> BrewInstall["brew install"]
```

Sources: [.github/workflows/build-and-release.yml:47-112](), [.github/workflows/build-and-release.yml:138-217](), [.github/workflows/build-and-release.yml:219-273](), [.github/workflows/build-and-release.yml:329-392]()

### Installation Commands by Method

| Method | Platforms | Installation | Verification |
|--------|-----------|--------------|--------------|
| **Quick Install Script** | Linux, MacOS | `curl -sSL https://stakpak.dev/install.sh \| sh` | `stakpak --version` |
| **Homebrew** | Linux, MacOS | `brew tap stakpak/stakpak && brew install stakpak` | `stakpak --version` |
| **Cargo** | Cross-platform | `cargo install stakpak` | `stakpak --version` |
| **Binary Release** | All | Download from [GitHub Releases](https://github.com/stakpak/agent/releases) | `./stakpak --version` |
| **Docker** | All with Docker | `docker pull ghcr.io/stakpak/agent:latest` | `docker run ghcr.io/stakpak/agent:latest --version` |

The build matrix targets five platforms: `x86_64-unknown-linux-musl`, `aarch64-unknown-linux-musl`, `x86_64-apple-darwin`, `aarch64-apple-darwin`, and `x86_64-pc-windows-msvc`. Each build produces compressed archives (`.tar.gz` for Unix, `.zip` for Windows) uploaded as GitHub Release artifacts.

The Docker image is built from `Dockerfile` and includes common DevOps tools: `docker`, `kubectl`, `aws`, `gcloud`, `azure`, `terraform`, `helm`.

Sources: [README.md:49-107](), [.github/workflows/build-and-release.yml:51-66](), [.github/workflows/build-and-release.yml:236-244]()

## Configuration and Authentication

stakpak supports two operational modes: **remote** (Stakpak-hosted backend) and **local** (bring-your-own-keys or custom LLM endpoint). Configuration is stored in `~/.stakpak/config.toml` following TOML format with profile-based settings.

### Configuration Architecture

```mermaid
graph TB
    ConfigFile["~/.stakpak/config.toml"] --> Profiles["[profiles.*] sections"]
    ConfigFile --> Settings["[settings] section"]
    
    Profiles --> RemoteProfile["[profiles.default]<br/>provider = 'remote'<br/>api_key from STAKPAK_API_KEY"]
    Profiles --> LocalProfile["[profiles.byok]<br/>provider = 'local'<br/>providers: anthropic/openai/gemini"]
    Profiles --> CustomProfile["[profiles.offline]<br/>provider = 'local'<br/>custom endpoint"]
    
    RemoteProfile --> RemoteClient["RemoteClient<br/>AgentProvider impl"]
    LocalProfile --> LocalClient["LocalClient<br/>AgentProvider impl"]
    CustomProfile --> LocalClient
    
    LocalClient --> StakAI["StakAI<br/>Direct LLM API calls"]
    LocalClient --> SQLite["SQLite Session Storage<br/>.stakpak/session/"]
    
    RemoteClient --> StakpakAPI["Stakpak Backend API"]
```

Sources: [README.md:110-217]()

### Configuration File Structure

The configuration file defines profiles with provider-specific settings. Two modes are supported:

#### Option A: Remote Provider (Stakpak API)

```toml
[profiles.default]
provider = "remote"
# API key sourced from STAKPAK_API_KEY env var or inline

[settings]
```

**Setup commands**:
```bash
# Interactive setup (opens browser for API key creation)
stakpak

# Or configure via command
stakpak login --api-key $STAKPAK_API_KEY

# Verify
stakpak account
```

#### Option B: Local Provider (BYOK)

```toml
[profiles.byok]
provider = "local"

# Model names auto-detected for built-in providers
smart_model = "claude-sonnet-4-5"
eco_model = "claude-haiku-4-5"

# Built-in providers - credentials via env vars or inline
[profiles.byok.providers.anthropic]
type = "anthropic"
api_key = "sk-ant-..."  # or ANTHROPIC_API_KEY env

[profiles.byok.providers.openai]
type = "openai"
api_key = "sk-..."  # or OPENAI_API_KEY env

[profiles.byok.providers.gemini]
type = "gemini"
api_key = "..."  # or GEMINI_API_KEY env

[settings]
```

**Setup commands**:
```bash
# Create config file manually or use:
mkdir -p ~/.stakpak
cat > ~/.stakpak/config.toml << 'EOF'
# ... paste config above ...
EOF

# Run with profile
stakpak --profile byok
```

#### Option C: Custom OpenAI-Compatible Endpoint

```toml
[profiles.offline]
provider = "local"

# Custom provider models use format: provider_key/model_name
smart_model = "offline/qwen/qwen3-coder-30b"
eco_model = "offline/qwen/qwen3-coder-30b"

[profiles.offline.providers.offline]
type = "custom"
api_endpoint = "http://localhost:11434/v1"
# api_key optional for local providers

[settings]
```

**Supported endpoints**: Ollama, LM Studio, vLLM, or any OpenAI-compatible API.

Sources: [README.md:141-217]()

### Environment Variables

| Variable | Purpose | Profiles |
|----------|---------|----------|
| `STAKPAK_API_KEY` | Stakpak backend authentication | Remote provider |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key | Local provider |
| `OPENAI_API_KEY` | OpenAI API key | Local provider |
| `GEMINI_API_KEY` | Google Gemini API key | Local provider |
| `HOME` | Config directory base (`~/.stakpak/`) | All |

Environment variables take precedence over inline `api_key` values in config file.

Sources: [README.md:154-166]()

## Basic Usage and Startup Modes

The `stakpak` binary provides multiple subcommands and operational modes. The default mode spawns an interactive TUI, while subcommands provide specific functionality like MCP server hosting, configuration management, and account operations.

### CLI Command Structure

```mermaid
graph TB
    Bin["stakpak binary<br/>main.rs entry point"] --> Args["CLI argument parsing"]
    
    Args --> DefaultMode["No subcommand"]
    Args --> LoginCmd["login subcommand"]
    Args --> ConfigCmd["config subcommand"]
    Args --> AccountCmd["account subcommand"]
    Args --> RulebooksCmd["rulebooks | rb subcommand"]
    Args --> MCPCmd["mcp subcommand"]
    Args --> ACPCmd["acp subcommand"]
    
    DefaultMode --> CheckpointArg{"-c/--checkpoint flag?"}
    CheckpointArg -->|Yes| LoadSession["Load session from checkpoint ID"]
    CheckpointArg -->|No| NewSession["Create new session"]
    
    LoadSession --> SpawnTUI["Spawn stakpak-tui process"]
    NewSession --> SpawnTUI
    
    SpawnTUI --> MCPServerLocal["Start local MCP server<br/>libs/mcp/server"]
    MCPServerLocal --> TUIEventLoop["TUI event loop<br/>libs/tui/src/lib.rs"]
    
    MCPCmd --> MCPSubcommands["start | proxy"]
    MCPSubcommands --> MCPStart["mcp start<br/>ToolContainer w/ 11 tools"]
    MCPSubcommands --> MCPProxy["mcp proxy<br/>Multiplexer for upstream servers"]
    
    RulebooksCmd --> RBSubcommands["get | apply | delete"]
    
    ACPCmd --> ACPServer["Agent Client Protocol server<br/>Zed editor integration"]
```

Sources: [README.md:219-327]()

### Common Usage Commands

| Command | Function | Configuration Required |
|---------|----------|------------------------|
| `stakpak` | Launch interactive TUI | Profile with provider |
| `stakpak -c <checkpoint-id>` | Resume session from checkpoint | Same as creation |
| `stakpak --profile <name>` | Use specific config profile | Named profile in config |
| `stakpak login --api-key <key>` | Save API key to config | None |
| `stakpak account` | Display account info | Remote provider API key |
| `stakpak config list` | List all profiles | Config file exists |
| `stakpak rb get` | List all rulebooks | Remote provider API key |
| `stakpak rb apply <file>` | Upload rulebook markdown | Remote provider API key |
| `stakpak mcp start` | Start MCP server (combined mode) | Profile with provider |
| `stakpak mcp start --tool-mode local` | Start MCP server (local tools only) | None |
| `stakpak mcp proxy` | Start MCP proxy server | `~/.stakpak/mcp.toml` config |
| `stakpak acp` | Start ACP server for Zed | Profile with provider |

### Interactive TUI Mode

The default execution mode starts the terminal user interface:

```bash
# Start new session
stakpak

# Resume from checkpoint
stakpak -c abc123

# With specific profile
stakpak --profile byok
```

The TUI spawns as a subprocess with bidirectional event channels (`InputEvent`/`OutputEvent`) for communication with the CLI parent process. See [TUI Architecture](#3) for detailed event flow.

Sources: [README.md:219-226]()

### Docker Deployment

Docker images support the same command structure with volume mounts for persistence and Docker socket access:

```bash
# Interactive TUI
docker run -it --entrypoint stakpak ghcr.io/stakpak/agent:latest

# With Docker socket for container operations
docker run -it \
  -v "/var/run/docker.sock":"/var/run/docker.sock" \
  -v "$(pwd)":"/agent/" \
  --entrypoint stakpak ghcr.io/stakpak/agent:latest

# With config persistence
docker run -it \
  -v "$HOME/.stakpak":"/root/.stakpak" \
  --entrypoint stakpak ghcr.io/stakpak/agent:latest
```

The image includes DevOps tools accessible to agent operations: `docker`, `kubectl`, `aws`, `gcloud`, `azure`, `terraform`, `helm`, `git`.

Sources: [README.md:228-237]()

## MCP Server Modes

The `stakpak mcp` subcommand provides two operational modes: `start` (tool server) and `proxy` (upstream multiplexer). The tool server exposes 11 tools through the `ToolContainer` struct defined in `libs/mcp/server`.

### MCP Server Architecture

```mermaid
graph TB
    MCPCommand["stakpak mcp"] --> StartMode["mcp start"]
    MCPCommand --> ProxyMode["mcp proxy"]
    
    StartMode --> ToolModeFlag["--tool-mode flag"]
    ToolModeFlag --> LocalMode["local"]
    ToolModeFlag --> RemoteMode["remote"]
    ToolModeFlag --> CombinedMode["combined (default)"]
    
    LocalMode --> ToolContainer["ToolContainer struct<br/>libs/mcp/server"]
    RemoteMode --> ToolContainer
    CombinedMode --> ToolContainer
    
    ToolContainer --> LocalTools["Local Tools (8)"]
    ToolContainer --> RemoteTools["Remote Tools (3)"]
    
    LocalTools --> RunCommand["run_command<br/>run_command_task"]
    LocalTools --> FileOps["view<br/>create<br/>str_replace<br/>remove"]
    LocalTools --> TaskOps["get_all_tasks<br/>cancel_task<br/>wait_for_tasks"]
    LocalTools --> Utils["generate_password<br/>view_web_page"]
    
    RemoteTools --> AIGen["generate_code<br/>AI-powered code generation"]
    RemoteTools --> Search["search_docs<br/>web search via SearXNG"]
    RemoteTools --> Memory["search_memory<br/>semantic search in session"]
    
    ToolContainer --> SecurityLayer["Security Layer"]
    SecurityLayer --> SecretManager["SecretManager<br/>Gitleaks-based redaction"]
    SecurityLayer --> mTLS["mTLS encryption<br/>--disable-mcp-mtls to disable"]
    SecurityLayer --> PrivacyMode["--privacy-mode<br/>redact IPs/account IDs"]
    
    ProxyMode --> ProxyConfig["~/.stakpak/mcp.toml"]
    ProxyConfig --> UpstreamServers["Upstream MCP servers"]
```

Sources: [README.md:241-289]()

### Tool Mode Configuration

The `--tool-mode` flag controls which tools are exposed:

| Mode | Tools Count | Description | API Key Required |
|------|-------------|-------------|------------------|
| `local` | 8 local tools | File operations, command execution, task management, password generation | No |
| `remote` | 3 remote tools | AI code generation, documentation search, memory search | Yes |
| `combined` | 11 total tools | Both local and remote tool sets | Yes |

**Local tools** (no API key required):
- `run_command` - Execute shell commands synchronously
- `run_command_task` - Execute shell commands asynchronously with task tracking
- `view` - Read file contents
- `create` - Create new files
- `str_replace` - Find and replace in files
- `remove` - Delete files/directories
- `get_all_tasks` - List running background tasks
- `cancel_task` - Cancel background task by ID
- `wait_for_tasks` - Wait for tasks to complete
- `generate_password` - Generate cryptographically secure passwords
- `view_web_page` - Fetch and convert web pages to markdown

**Remote tools** (API key required):
- `generate_code` - AI-powered code generation using configured LLM
- `search_docs` - Search technical documentation via SearXNG Docker container
- `search_memory` - Semantic search across session memory and indexed files

Sources: [README.md:244-272]()

### MCP Server Startup Examples

```bash
# Local tools only (no API key)
stakpak mcp start --tool-mode local

# Remote tools only (AI features)
stakpak mcp start --tool-mode remote

# Combined mode (default)
stakpak mcp start

# Disable mTLS (NOT recommended)
stakpak mcp start --disable-mcp-mtls

# Enable privacy mode (redact sensitive data)
stakpak mcp start --privacy-mode

# Disable secret redaction in logs (NOT recommended)
stakpak mcp start --disable-secret-redaction
```

### MCP Proxy Mode

The proxy multiplexes connections to multiple upstream MCP servers configured in `~/.stakpak/mcp.toml`:

```bash
# Auto-discover config
stakpak mcp proxy

# Explicit config file
stakpak mcp proxy --config-file ~/.stakpak/mcp.toml

# With privacy mode
stakpak mcp proxy --privacy-mode
```

The proxy enables aggregation of multiple MCP servers (e.g., filesystem, git, cloud provider tools) through a single endpoint.

Sources: [README.md:274-289]()

### Security Features

All MCP modes include:

- **mTLS encryption** - Mutual TLS for transport security (default enabled)
- **Secret redaction** - Gitleaks integration scans outputs and redacts secrets before transmission
- **Privacy mode** - Additional redaction of IP addresses, AWS account IDs, and other PII via `--privacy-mode` flag
- **Tool filtering** - `allowed_tools` configuration restricts which tools are callable

See [Security and Privacy](#6) for implementation details of `SecretManager` and `Warden` guardrails.

Sources: [README.md:55-61](), [README.md:268-272]()

## Configuration Files and Environment

The agent uses a configuration file located at `~/.stakpak/config.toml` for persistent settings. This file is created automatically when using the `stakpak login` command and stores the API key and other configuration parameters.

### Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `STAKPAK_API_KEY` | Authentication with stakpak service | For remote features |
| `HOME` | Location of config directory (`~/.stakpak/`) | Yes |

The agent checks for the API key first in the environment variable, then falls back to the configuration file if the environment variable is not set.

Sources: [README.md:76-86]()

---

# Page: CLI Interface

# CLI Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/stakpak-dark.png](assets/stakpak-dark.png)
- [assets/stakpak-light.png](assets/stakpak-light.png)
- [cli/src/commands/agent/run/helpers.rs](cli/src/commands/agent/run/helpers.rs)
- [cli/src/commands/agent/run/mode_async.rs](cli/src/commands/agent/run/mode_async.rs)
- [cli/src/commands/agent/run/mode_interactive.rs](cli/src/commands/agent/run/mode_interactive.rs)
- [cli/src/commands/mod.rs](cli/src/commands/mod.rs)
- [cli/src/main.rs](cli/src/main.rs)

</details>



This document covers the main command-line interface (`stakpak` CLI) that serves as the primary user entry point to the stakpak agent system. It handles argument parsing, authentication, configuration management, and dispatches to either specific subcommands or the main agent execution modes. For details about the TUI interactive interface, see [Terminal User Interface (TUI)](#3). For information about the MCP tool system integration, see [MCP (Model Context Protocol) System](#4).

## CLI Argument Structure

The CLI interface is built using the `clap` crate and defines a comprehensive set of options and flags through the `Cli` struct at [cli/src/main.rs:41-142](). The interface supports both direct agent execution and various utility subcommands.

### Main CLI Structure

**CLI Argument Structure**
```mermaid
graph TB
    CLI["Cli struct"] --> MainArgs["Main Arguments"]
    CLI --> SubCommands["Subcommands"]
    
    MainArgs --> ExecModes["Execution Modes"]
    MainArgs --> ConfigFlags["Configuration Flags"] 
    MainArgs --> SecurityFlags["Security Flags"]
    MainArgs --> ToolFlags["Tool Flags"]
    
    ExecModes --> print["-p --print<br/>Single step execution"]
    ExecModes --> async["-a --async<br/>Multi-step batch execution"]
    ExecModes --> max_steps["-m --max-steps<br/>Step limit (default: 50)"]
    ExecModes --> checkpoint["-c --checkpoint<br/>Resume from checkpoint"]
    ExecModes --> workdir["-w --workdir<br/>Set working directory"]
    
    ConfigFlags --> profile["--profile<br/>Configuration profile"]
    ConfigFlags --> config_path["--config<br/>Custom config file path"]
    ConfigFlags --> output_format["-o --output<br/>json/text format"]
    ConfigFlags --> model["--model<br/>smart/eco model selection"]
    ConfigFlags --> verbose["--verbose<br/>Verbose output"]
    ConfigFlags --> debug["--debug<br/>Debug logging"]
    
    SecurityFlags --> disable_secret_redaction["--disable-secret-redaction"]
    SecurityFlags --> privacy_mode["--privacy-mode"]
    SecurityFlags --> disable_mcp_mtls["--disable-mcp-mtls"]
    
    ToolFlags --> allowed_tools["-t --tool<br/>Filter allowed tools"]
    ToolFlags --> system_prompt_file["--system-prompt-file"]
    ToolFlags --> prompt_file["--prompt-file<br/>Read prompt from file"]
    ToolFlags --> enable_slack["--enable-slack-tools"]
    ToolFlags --> enable_subagents["--enable-subagents"]
    ToolFlags --> subagent_config["--subagent-config"]
    
    SubCommands --> Commands["Commands enum"]
```

The CLI defines mutually exclusive execution modes through boolean flags `print` and `async`. When neither flag is specified, the CLI launches in interactive mode (TUI). The optional `prompt` argument can be provided for all modes.

Sources: [cli/src/main.rs:41-142]()

### Subcommand Structure

The `Commands` enum at [cli/src/commands/mod.rs:102-167]() defines all available subcommands with their specific arguments and options:

| Subcommand | Purpose | Key Arguments | Requires Auth |
|------------|---------|---------------|---------------|
| `version` | Display CLI version | None | No |
| `login` | (Deprecated) Authenticate with API key | `--api-key` | No |
| `logout` | (Deprecated) Clear stored credentials | None | No |
| `acp` | Start Agent Client Protocol server for editor integration | `--system-prompt-file` | No |
| `set` | Update configuration values | `--machine-name`, `--auto-append-gitignore` | No |
| `config` | Configuration management | Subcommands: `list`, `show`, `sample`, `new` | No |
| `rulebooks` (alias `rb`) | Manage rulebooks | Subcommands: `get`, `apply`, `delete` | Yes |
| `account` | Get current account info | None | Yes |
| `mcp` | MCP server/proxy/client commands | Subcommands with various flags | Varies |
| `auth` | Provider authentication (OAuth, API keys) | Subcommands for different providers | No |
| `warden` | Security wrapper for agent execution | `--env`, `--volume`, subcommands | Yes |
| `update` | Update Stakpak Agent to latest version | None | No |

**ConfigCommands subcommands:**
- `list` (alias `ls`): List and select profiles interactively
- `show`: Show current configuration
- `sample`: Print a complete sample configuration file
- `new`: Create a new profile

**RulebookCommands subcommands:**
- `get [uri]`: Get specific rulebook or list all rulebooks
- `apply <file_path>`: Apply/create a rulebook from markdown file
- `delete <uri>`: Delete a rulebook

Sources: [cli/src/commands/mod.rs:70-167](), [cli/src/commands/mod.rs:206-218]()

## Execution Flow

The main execution flow follows a clear dispatch pattern based on whether subcommands are provided or the CLI should run in agent mode.

### Main Dispatch Logic

**Main Execution Flow from main()**
```mermaid
flowchart TD
    Start["main()"] --> InitCrypto["Initialize rustls crypto provider"]
    InitCrypto --> HandleConfigAlias["Handle 'stakpak config' → 'stakpak config list'"]
    HandleConfigAlias --> ParseCli["Cli::parse()"]
    ParseCli --> AutoUpdate{"Command is None<br/>AND not async/print?"}
    
    AutoUpdate -->|Yes| RunAutoUpdate["auto_update()"]
    AutoUpdate -->|No| SetWorkdir["Set workdir if specified"]
    RunAutoUpdate --> SetWorkdir
    
    SetWorkdir --> InitDebug{"cli.debug?"}
    InitDebug -->|Yes| SetupTracing["Setup tracing_subscriber"]
    InitDebug -->|No| DetermineProfile["Determine profile"]
    SetupTracing --> DetermineProfile
    
    DetermineProfile --> LoadConfig["AppConfig::load(profile, config_path)"]
    LoadConfig --> CheckWarden{"Warden enabled<br/>AND not STAKPAK_SKIP_WARDEN<br/>AND no subcommand?"}
    
    CheckWarden -->|Yes| RunWarden["commands::warden::run_stakpak_in_warden()"]
    CheckWarden -->|No| GenMachineName{"machine_name.is_none()?"}
    
    GenMachineName -->|Yes| GenerateName["Generate random machine name"]
    GenMachineName -->|No| CheckCommand{"command.is_some()?"}
    GenerateName --> SaveConfig["config.save()"]
    SaveConfig --> CheckCommand
    
    CheckCommand -->|Yes| CheckAuth{"command.requires_auth()?"}
    CheckCommand -->|No| AgentMode["Agent Mode Execution"]
    
    CheckAuth -->|Yes| HasApiKey{"config.get_stakpak_api_key().is_none()?"}
    CheckAuth -->|No| EnsureGitignore["Ensure .stakpak in .gitignore"]
    
    HasApiKey -->|Yes| RunOnboarding["run_onboarding()"]
    HasApiKey -->|No| EnsureGitignore
    RunOnboarding --> EnsureGitignore
    
    EnsureGitignore --> RunCommand["command.run(config)"]
    
    AgentMode --> CheckAuthAgent{"Provider is Remote<br/>AND no API key?"}
    CheckAuthAgent -->|Yes| RunOnboardingAgent["run_onboarding()"]
    CheckAuthAgent -->|No| AnalyzeContext["analyze_local_context()"]
    RunOnboardingAgent --> AnalyzeContext
    
    AnalyzeContext --> DiscoverAgentsMd["discover_agents_md()"]
    DiscoverAgentsMd --> CreateClient["Create AgentProvider<br/>(Remote or Local)"]
    
    CreateClient --> ParallelFetch["Parallel: get_my_account(),<br/>check_update(), list_rulebooks()"]
    ParallelFetch --> ValidateApi{"API validation<br/>successful?"}
    
    ValidateApi -->|No AND Remote| ExitError["Exit with error"]
    ValidateApi -->|Yes OR Local| LoadSubagents["Load subagent configs<br/>if --enable-subagents"]
    
    LoadSubagents --> ReadPrompts["Read system-prompt-file<br/>and prompt-file if specified"]
    ReadPrompts --> DetermineMode{"use_async_mode?<br/>(cli.async OR cli.print)"}
    
    DetermineMode -->|Yes| RunAsync["agent::run::run_async()"]
    DetermineMode -->|No| RunInteractive["agent::run::run_interactive()"]
```

The profile selection follows this priority chain:
1. CLI argument `--profile`
2. Environment variable `STAKPAK_PROFILE`
3. Default value `"default"`

The execution mode determination follows this logic:
- `use_async_mode = cli.async || cli.print`
- `max_steps = if cli.print { Some(1) } else { cli.max_steps }`

Sources: [cli/src/main.rs:146-512]()

### Configuration and Profile Management

The CLI manages configuration through the `AppConfig` system with support for multiple profiles:

**Profile Selection and Configuration Loading**
```mermaid
graph TB
    Start["Determine Profile"] --> Priority1{"CLI --profile<br/>flag present?"}
    Priority1 -->|Yes| UseCliProfile["Use CLI profile"]
    Priority1 -->|No| Priority2{"STAKPAK_PROFILE<br/>env var set?"}
    
    Priority2 -->|Yes| UseEnvProfile["Use env profile"]
    Priority2 -->|No| UseDefault["Use 'default' profile"]
    
    UseCliProfile --> LoadConfig["AppConfig::load(profile, config_path)"]
    UseEnvProfile --> LoadConfig
    UseDefault --> LoadConfig
    
    LoadConfig --> CheckWarden{"Warden enabled<br/>in profile?"}
    CheckWarden -->|Yes| WardenExec["Re-execute in warden container"]
    CheckWarden -->|No| CheckMachineName{"machine_name<br/>is None?"}
    
    CheckMachineName -->|Yes| GenerateName["names::Generator::with_naming()<br/>.next()"]
    CheckMachineName -->|No| ProcessConfig["Continue with config"]
    
    GenerateName --> SaveMachineName["config.save()"]
    SaveMachineName --> ProcessConfig
    
    ProcessConfig --> CheckAuth{"Needs authentication?"}
    CheckAuth -->|Yes| RunOnboarding["run_onboarding(config,<br/>OnboardingMode)"]
    CheckAuth -->|No| Proceed["Proceed with execution"]
    RunOnboarding --> Proceed
```

The configuration system supports:
- **Profile-based settings**: Multiple profiles stored in `~/.stakpak/config.toml`
- **Credential fallback chain**: Uses `auth.toml` for provider credentials
- **Warden integration**: Automatic container wrapping when `warden.enabled = true`
- **Machine identification**: Random name generation for device tracking

Sources: [cli/src/main.rs:191-230](), [cli/src/main.rs:198-216](), [cli/src/main.rs:218-229]()

## Agent Execution Modes  

The CLI supports two primary agent execution modes, each with distinct characteristics and use cases. The mode selection and configuration preparation happens in [cli/src/main.rs:426-506]().

### Mode Determination and Configuration

**Agent Mode Selection and Initialization**
```mermaid
graph TB
    ModeCheck["Mode Selection"] --> AsyncCheck{"--async OR --print?"}
    
    AsyncCheck -->|Yes| SetMaxSteps{"--print flag?"}
    AsyncCheck -->|No| InteractiveMode["Interactive Mode"]
    
    SetMaxSteps -->|Yes| ForceOne["max_steps = Some(1)"]
    SetMaxSteps -->|No| UseConfig["max_steps = cli.max_steps<br/>OR Some(50)"]
    
    ForceOne --> BuildAsyncConfig["Build RunAsyncConfig"]
    UseConfig --> BuildAsyncConfig
    
    BuildAsyncConfig --> RunAsync["agent::run::run_async()"]
    
    InteractiveMode --> BuildInteractiveConfig["Build RunInteractiveConfig"]
    BuildInteractiveConfig --> RunInteractive["agent::run::run_interactive()"]
    
    RunAsync --> AsyncLoop["Step loop with tools"]
    RunInteractive --> SpawnTui["Spawn TUI task"]
    RunInteractive --> SpawnClient["Spawn client task"]
    
    SpawnTui --> TuiEventLoop["TUI event loop"]
    SpawnClient --> ClientEventLoop["Client event loop"]
    
    TuiEventLoop --> OutputChannel["output_tx channel"]
    ClientEventLoop --> InputChannel["input_tx channel"]
    
    OutputChannel --> ProcessEvents["Process OutputEvent"]
    InputChannel --> UpdateTui["Update TUI state"]
```

### Execution Mode Characteristics

| Mode | Trigger | Max Steps | User Interaction | Output | Config Struct |
|------|---------|-----------|------------------|---------|---------------|
| Interactive | Default (no flags) | Unlimited | TUI-based real-time | Terminal interface | `RunInteractiveConfig` |
| Async (Multi-step) | `--async` | 50 (default) or user-specified | None | JSON/Text to stdout | `RunAsyncConfig` |
| Async (Single-step) | `--print` | 1 (forced) | None | JSON/Text to stdout | `RunAsyncConfig` |

### Configuration Structures

**RunAsyncConfig** ([cli/src/commands/agent/run/mode_async.rs:28-45]()):
- `prompt: String` - User prompt text
- `checkpoint_id: Option<String>` - Resume from checkpoint
- `local_context: Option<LocalContext>` - Local file context
- `verbose: bool` - Verbose output
- `redact_secrets: bool` - Secret redaction flag
- `privacy_mode: bool` - Privacy mode flag
- `rulebooks: Option<Vec<ListRuleBook>>` - Applied rulebooks
- `subagent_configs: Option<SubagentConfigs>` - Subagent configuration
- `max_steps: Option<usize>` - Maximum execution steps
- `output_format: OutputFormat` - JSON or Text
- `allowed_tools: Option<Vec<String>>` - Tool filter
- `enable_mtls: bool` - mTLS flag
- `system_prompt: Option<String>` - System prompt override
- `enabled_tools: EnabledToolsConfig` - Tool category enables
- `model: AgentModel` - Smart or Eco model
- `agents_md: Option<AgentsMdInfo>` - AGENTS.md metadata

**RunInteractiveConfig** ([cli/src/commands/agent/run/mode_interactive.rs:51-67]()):
- Similar fields as async, but no `prompt`, `verbose`, `max_steps`, or `output_format`
- Additional: `is_git_repo: bool`, `study_mode: bool`, `auto_approve: Option<Vec<String>>`

Sources: [cli/src/main.rs:426-506](), [cli/src/commands/agent/run/mode_async.rs:28-45](), [cli/src/commands/agent/run/mode_interactive.rs:51-67]()

## Integration Points

The CLI orchestrates integration with multiple system components through well-defined interfaces.

### System Component Integration

```mermaid
graph TB
    CliMain["CLI main()"] --> ConfigSys["AppConfig"]
    CliMain --> ApiClient["stakpak_api::Client"]
    CliMain --> CodeIndex["Code Index System"]
    CliMain --> McpServer["MCP Server"]
    
    ConfigSys --> AuthFlow["Authentication Flow"]
    ApiClient --> BackendAPI["Stakpak Backend API"]
    
    CodeIndex --> IndexBuild["get_or_build_local_code_index()"]
    CodeIndex --> IndexWatch["start_code_index_watcher()"]
    
    McpServer --> LocalTools["Local MCP Tools"]
    McpServer --> RemoteTools["Remote MCP Tools"]
    
    CliMain --> AgentModes["Agent Execution"]
    AgentModes --> TUI["TUI Interface"]
    AgentModes --> AsyncExec["Async Execution"]
    
    TUI --> McpClient["MCP Client"]
    AsyncExec --> McpClient
    McpClient --> McpServer
```

### MCP Server Integration

When running the `mcp` subcommand or agent modes, the CLI initializes the MCP server with specific configurations:

```mermaid
graph TB
    CliMcp["CLI mcp command"] --> ServerConfig["MCPServerConfig"]
    CliAgent["CLI agent mode"] --> LocalServer["Local MCP Server"]
    
    ServerConfig --> ToolMode["tool_mode: local/remote/combined"]
    ServerConfig --> Security["Security settings"]
    ServerConfig --> Network["Network configuration"]
    
    Security --> SecretRedaction["redact_secrets"]
    Security --> PrivacyMode["privacy_mode"] 
    Security --> MTLSConfig["certificate_chain"]
    
    Network --> BindAddress["find_available_bind_address()"]
    Network --> Listener["TCP Listener"]
    
    LocalServer --> SameConfig["Same configuration as MCP command"]
    
    ServerConfig --> StartServer["stakpak_mcp_server::start_server()"]
    LocalServer --> StartLocal["Local server for agent tools"]
```

Sources: [cli/src/commands/mod.rs:175-254](), [cli/src/main.rs:170-192]()

### Code Index Management

The CLI manages local code indexing for enhanced context in agent operations:

```mermaid
flowchart TD
    IndexTrigger["Index Trigger"] --> CheckMode{"Tool mode requires indexing?"}
    CheckMode -->|"RemoteOnly OR Combined"| StartIndex["get_or_build_local_code_index()"]
    CheckMode -->|"LocalOnly"| Skip["Skip indexing"]
    
    StartIndex --> IndexResult{"Indexing result"}
    IndexResult -->|"Success"| StartWatcher["start_code_index_watcher()"]
    IndexResult -->|"Threshold error"| ContinueSilent["Continue without watcher"]
    IndexResult -->|"Other error"| ExitError["Exit with error"]
    
    StartWatcher --> WatcherSpawn["tokio::spawn(watcher_task)"]
    ContinueSilent --> ProceedExecution["Proceed with execution"]
    WatcherSpawn --> ProceedExecution
```

The system handles large project thresholds gracefully, allowing users to override with the `--index-big-project` flag.

Sources: [cli/src/main.rs:170-192](), [cli/src/commands/mod.rs:185-212]()

---

# Page: Main Entry Point and Configuration

# Main Entry Point and Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cli/src/commands/agent/run/helpers.rs](cli/src/commands/agent/run/helpers.rs)
- [cli/src/commands/agent/run/mode_async.rs](cli/src/commands/agent/run/mode_async.rs)
- [cli/src/commands/agent/run/mode_interactive.rs](cli/src/commands/agent/run/mode_interactive.rs)
- [cli/src/commands/mod.rs](cli/src/commands/mod.rs)
- [cli/src/main.rs](cli/src/main.rs)

</details>



## Purpose and Scope

This document describes the CLI's main entry point (`main.rs`) and configuration system, which serves as the initialization layer for all Stakpak operations. It covers command-line argument parsing, configuration file loading, profile management, provider initialization, and the routing logic that determines execution mode. 

For details on how the agent executes after initialization, see [Agent Execution Modes](#2.2). For configuration of context injection (rulebooks, local files, etc.), see [Context Injection Pipeline](#2.3).

---

## Application Entry Point

The application starts in `main()` at [cli/src/main.rs:147-512](), which orchestrates the initialization sequence:

### Initialization Sequence Diagram

```mermaid
graph TB
    MAIN["main()"]
    CRYPTO["Install rustls CryptoProvider"]
    ARGS["Parse CLI arguments<br/>(Cli struct)"]
    UPDATE["Auto-update check<br/>(interactive mode only)"]
    WORKDIR["Set working directory<br/>(--workdir)"]
    LOGGING["Initialize tracing<br/>(--debug)"]
    PROFILE["Resolve profile name<br/>(CLI > env > default)"]
    LOAD["AppConfig::load()"]
    WARDEN_CHECK{"Warden enabled<br/>in profile?"}
    WARDEN["Re-execute in<br/>warden container"]
    MACHINE["Generate machine_name<br/>(if missing)"]
    ROUTE{"Route execution"}
    SUBCOMMAND["Execute subcommand"]
    AGENT["Initialize agent<br/>(interactive/async)"]
    
    MAIN --> CRYPTO
    CRYPTO --> ARGS
    ARGS --> UPDATE
    UPDATE --> WORKDIR
    WORKDIR --> LOGGING
    LOGGING --> PROFILE
    PROFILE --> LOAD
    LOAD --> WARDEN_CHECK
    WARDEN_CHECK -->|Yes| WARDEN
    WARDEN_CHECK -->|No| MACHINE
    MACHINE --> ROUTE
    ROUTE -->|command.is_some()| SUBCOMMAND
    ROUTE -->|None| AGENT
```

**Sources:** [cli/src/main.rs:147-217]()

### Key Initialization Steps

1. **Crypto Provider**: Installs `rustls` with AWS LC crypto backend [cli/src/main.rs:149]()
2. **Argument Parsing**: Parses CLI arguments into `Cli` struct using clap [cli/src/main.rs:158-162]()
3. **Auto-Update**: Checks for updates only in interactive mode [cli/src/main.rs:165-171]()
4. **Working Directory**: Changes to `--workdir` if specified [cli/src/main.rs:173-179]()
5. **Logging**: Initializes tracing subscriber if `--debug` flag is set [cli/src/main.rs:181-189]()
6. **Profile Resolution**: Determines profile name from CLI arg, `STAKPAK_PROFILE` env var, or defaults to "default" [cli/src/main.rs:192-195]()

---

## Command-Line Interface Structure

The CLI is defined using the `Cli` struct with clap attributes:

### Cli Struct Overview

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `print` | `bool` | Single-step execution mode | `false` |
| `r#async` | `bool` | Multi-step async execution | `false` |
| `max_steps` | `Option<usize>` | Maximum agent steps | `None` (50 for async) |
| `checkpoint_id` | `Option<String>` | Resume from checkpoint UUID | `None` |
| `workdir` | `Option<String>` | Working directory | Current dir |
| `verbose` | `bool` | Enable verbose output | `false` |
| `output_format` | `OutputFormat` | Output format (json/text) | `Text` |
| `debug` | `bool` | Enable debug logging | `false` |
| `disable_secret_redaction` | `bool` | Disable secret redaction | `false` |
| `privacy_mode` | `bool` | Enable privacy mode | `false` |
| `study_mode` | `bool` | Enable study assistant mode | `false` |
| `allowed_tools` | `Option<Vec<String>>` | Restrict available tools | `None` (all) |
| `system_prompt_file` | `Option<String>` | System prompt file path | `None` |
| `prompt_file` | `Option<String>` | Prompt file path | `None` |
| `profile` | `Option<String>` | Configuration profile | env/default |
| `model` | `Option<AgentModel>` | Agent model (smart/eco) | `Smart` |
| `config_path` | `Option<PathBuf>` | Custom config file path | `~/.stakpak/config.toml` |
| `prompt` | `Option<String>` | Direct prompt text | `None` |
| `command` | `Option<Commands>` | Subcommand to execute | `None` (agent) |

**Sources:** [cli/src/main.rs:41-142]()

### Commands Enum

The `Commands` enum defines all available subcommands:

```mermaid
graph LR
    CLI["Commands enum"]
    
    CLI --> VERSION["Version"]
    CLI --> AUTH["Auth<br/>(OAuth, API keys)"]
    CLI --> CONFIG["Config<br/>(list, show, sample, new)"]
    CLI --> RB["Rulebooks<br/>(get, apply, delete)"]
    CLI --> ACCOUNT["Account"]
    CLI --> MCP["Mcp<br/>(start, proxy, status)"]
    CLI --> WARDEN["Warden<br/>(security policies)"]
    CLI --> UPDATE["Update"]
    CLI --> ACP["Acp<br/>(editor protocol)"]
    CLI --> SET["Set<br/>(machine_name, etc)"]
```

**Sources:** [cli/src/commands/mod.rs:102-167]()

---

## Configuration System

### AppConfig Loading

Configuration is loaded through `AppConfig::load()` with profile support:

```mermaid
graph TB
    LOAD["AppConfig::load()<br/>(profile_name, config_path)"]
    FILE["~/.stakpak/config.toml<br/>(or custom path)"]
    PARSE["Parse TOML"]
    RESOLVE["Resolve profile:<br/>1. profiles.{name}<br/>2. profiles.all<br/>3. root level"]
    AUTH["Resolve credentials:<br/>auth.toml fallback chain"]
    VALIDATE["Validate configuration"]
    RETURN["Return AppConfig"]
    ERROR["Return error"]
    
    LOAD --> FILE
    FILE -->|Success| PARSE
    FILE -->|Not found| ERROR
    PARSE -->|Valid| RESOLVE
    PARSE -->|Invalid| ERROR
    RESOLVE --> AUTH
    AUTH --> VALIDATE
    VALIDATE -->|Valid| RETURN
    VALIDATE -->|Invalid| ERROR
```

**Sources:** [cli/src/main.rs:197-229]()

### Configuration Structure

The `AppConfig` contains these key fields:

| Field | Type | Description |
|-------|------|-------------|
| `profile_name` | `String` | Active profile name |
| `config_path` | `String` | Path to config file |
| `api_key` | `Option<String>` | Stakpak API key (for remote) |
| `api_endpoint` | `String` | API endpoint URL |
| `provider` | `ProviderType` | Remote or Local |
| `machine_name` | `Option<String>` | Device identifier |
| `mcp_server_host` | `Option<String>` | MCP server address |
| `allowed_tools` | `Option<Vec<String>>` | Tool whitelist |
| `auto_approve` | `Option<Vec<String>>` | Auto-approve tool list |
| `rulebooks` | `Option<RulebookConfig>` | Rulebook filters |
| `warden` | `Option<WardenConfig>` | Security policies |
| `editor` | `Option<String>` | Preferred editor |
| `eco_model` | `Option<String>` | Economy model name |
| `smart_model` | `Option<String>` | Smart model name |
| `recovery_model` | `Option<String>` | Recovery model name |
| `anonymous_id` | `Option<String>` | Telemetry ID |
| `collect_telemetry` | `Option<bool>` | Telemetry opt-in |

**Sources:** [cli/src/config.rs]() (referenced in imports)

### Profile Hierarchy

Profiles support inheritance with the following precedence:

1. **Profile-specific settings** (`profiles.{name}`)
2. **Common settings** (`profiles.all`)
3. **Root-level defaults**

Example configuration structure:

```toml
# Root-level defaults (lowest priority)
api_endpoint = "https://apiv2.stakpak.dev"

[profiles.all]
# Applies to all profiles
allowed_tools = ["view", "search_docs"]

[profiles.default]
# Specific profile (highest priority)
api_key = "sk-..."
allowed_tools = ["view", "search_docs", "create", "str_replace"]
```

**Sources:** [cli/src/commands/mod.rs:499-612]()

---

## Provider Initialization

### ProviderType Selection

The configuration determines which `AgentProvider` implementation to use:

```mermaid
graph TB
    CONFIG["AppConfig.provider"]
    REMOTE_TYPE["ProviderType::Remote"]
    LOCAL_TYPE["ProviderType::Local"]
    
    REMOTE_CLIENT["RemoteClient::new()<br/>ClientConfig"]
    LOCAL_CLIENT["LocalClient::new()<br/>LocalClientConfig"]
    
    REMOTE_API["Stakpak Backend API<br/>(api_endpoint)"]
    LOCAL_LLM["Direct LLM Integration<br/>(OpenAI, Anthropic, etc.)"]
    
    REMOTE_AUTH["API key<br/>(from config or auth.toml)"]
    LOCAL_AUTH["LLM credentials<br/>(from auth.toml)"]
    
    ARC["Arc<dyn AgentProvider>"]
    
    CONFIG -->|Remote| REMOTE_TYPE
    CONFIG -->|Local| LOCAL_TYPE
    
    REMOTE_TYPE --> REMOTE_CLIENT
    LOCAL_TYPE --> LOCAL_CLIENT
    
    REMOTE_CLIENT --> REMOTE_AUTH
    REMOTE_CLIENT --> REMOTE_API
    LOCAL_CLIENT --> LOCAL_AUTH
    LOCAL_CLIENT --> LOCAL_LLM
    
    REMOTE_CLIENT --> ARC
    LOCAL_CLIENT --> ARC
```

**Sources:** [cli/src/main.rs:267-296]()

### RemoteClient Initialization

For `ProviderType::Remote`:

```rust
RemoteClient::new(&ClientConfig {
    api_key: config.api_key.clone(),
    api_endpoint: config.api_endpoint.clone(),
})
```

**Sources:** [cli/src/main.rs:269-274](), [cli/src/commands/mode_interactive.rs:168-173]()

### LocalClient Initialization

For `ProviderType::Local`:

```rust
LocalClient::new(LocalClientConfig {
    stakpak_base_url: Some(config.api_endpoint.clone()),
    store_path: None,
    providers: config.get_llm_provider_config_async().await,
    eco_model: config.eco_model.clone(),
    recovery_model: config.recovery_model.clone(),
    smart_model: config.smart_model.clone(),
    hook_registry: None,
})
```

The `get_llm_provider_config_async()` method resolves LLM credentials from `auth.toml` and refreshes OAuth tokens in parallel to minimize startup delay.

**Sources:** [cli/src/main.rs:276-295](), [cli/src/commands/mode_interactive.rs:175-189]()

---

## Execution Routing

### Routing Decision Tree

After configuration loads, the application routes to one of three paths:

```mermaid
graph TB
    START["Configuration Loaded"]
    AUTH_CHECK{"Requires<br/>authentication?"}
    ONBOARD["run_onboarding()"]
    WARDEN_CHECK{"Warden enabled<br/>and not inside?"}
    WARDEN["run_stakpak_in_warden()"]
    MACHINE{"machine_name<br/>exists?"}
    GEN["Generate random<br/>machine_name"]
    ROUTE{"command.is_some()?"}
    
    SUBCOMMAND["Execute subcommand<br/>command.run(config)"]
    AGENT_INIT["Initialize agent mode"]
    
    CONTEXT["analyze_local_context()"]
    AGENTS_MD["discover_agents_md()"]
    PROVIDER["Create AgentProvider<br/>(Remote or Local)"]
    PARALLEL["Parallel HTTP calls:<br/>- get_my_account()<br/>- check_update()<br/>- list_rulebooks()"]
    SUBAGENTS["Load subagent configs<br/>(if --enable-subagents)"]
    PROMPTS["Load system/user prompts<br/>(from files if specified)"]
    
    MODE{"Execution mode?"}
    ASYNC["run_async()<br/>RunAsyncConfig"]
    INTERACTIVE["run_interactive()<br/>RunInteractiveConfig"]
    
    START --> WARDEN_CHECK
    WARDEN_CHECK -->|Yes| WARDEN
    WARDEN_CHECK -->|No| MACHINE
    MACHINE -->|No| GEN
    MACHINE -->|Yes| ROUTE
    GEN --> ROUTE
    
    ROUTE -->|Yes| AUTH_CHECK
    AUTH_CHECK -->|No auth| SUBCOMMAND
    AUTH_CHECK -->|Needs auth| ONBOARD
    ONBOARD --> SUBCOMMAND
    
    ROUTE -->|No| AGENT_INIT
    
    AGENT_INIT --> CONTEXT
    CONTEXT --> AGENTS_MD
    AGENTS_MD --> PROVIDER
    PROVIDER --> PARALLEL
    PARALLEL --> SUBAGENTS
    SUBAGENTS --> PROMPTS
    PROMPTS --> MODE
    
    MODE -->|async or print| ASYNC
    MODE -->|interactive| INTERACTIVE
```

**Sources:** [cli/src/main.rs:200-508]()

### Warden Pre-Execution Check

Before any agent execution, the system checks if Warden (security container) is enabled:

```rust
let should_use_warden = config.warden.as_ref().map(|w| w.enabled).unwrap_or(false)
    && std::env::var("STAKPAK_SKIP_WARDEN").is_err()
    && cli.command.is_none(); // Only for main agent, not for subcommands
```

If enabled, it re-executes the entire stakpak command inside the Warden container and exits.

**Sources:** [cli/src/main.rs:200-216]()

### Machine Name Generation

If no machine name exists in the config, it generates a random human-readable name:

```rust
let random_name = names::Generator::with_naming(Name::Numbered)
    .next()
    .unwrap_or_else(|| "unknown-machine".to_string());
```

**Sources:** [cli/src/main.rs:218-229]()

---

## Authentication and Credential Resolution

### Authentication Check Flow

```mermaid
graph TB
    CMD["Command execution"]
    REQ{"requires_auth()?"}
    API_KEY{"API key exists?"}
    PROVIDER{"ProviderType?"}
    ONBOARD["run_onboarding()"]
    EXEC["Execute command"]
    
    CMD --> REQ
    REQ -->|Yes| API_KEY
    REQ -->|No| EXEC
    
    API_KEY -->|No| PROVIDER
    API_KEY -->|Yes| EXEC
    
    PROVIDER -->|Remote| ONBOARD
    PROVIDER -->|Local| EXEC
    
    ONBOARD --> EXEC
```

**Sources:** [cli/src/main.rs:232-256]()

### Credential Resolution Chain

The system uses a fallback chain for credentials:

1. **Config file**: Direct `api_key` field in profile
2. **auth.toml**: Provider-specific credentials in `~/.stakpak/auth.toml`
3. **Environment variables**: `STAKPAK_API_KEY`, provider-specific env vars

For Local provider, the `get_llm_provider_config()` and `get_llm_provider_config_async()` methods resolve credentials for each LLM provider (OpenAI, Anthropic, etc.) from `auth.toml`.

**Sources:** [cli/src/main.rs:279](), [cli/src/commands/mod.rs:178]()

---

## Agent Initialization Sequence

### Pre-Execution Setup

Before launching the agent (interactive or async mode):

```mermaid
graph TB
    START["Agent mode selected"]
    
    CONTEXT["analyze_local_context()<br/>Scan files, git status"]
    AGENTS["discover_agents_md()<br/>Find AGENTS.md files"]
    
    PROVIDER["Create AgentProvider<br/>(Arc<dyn AgentProvider>)"]
    
    PARALLEL["tokio::join!()"]
    ACCOUNT["get_my_account()"]
    UPDATE["check_update()"]
    RULEBOOKS["list_rulebooks()<br/>+ filter by config"]
    
    SUBAGENTS{"--enable-subagents?"}
    LOAD_SUB["Load SubagentConfigs<br/>(from file or default)"]
    
    PROMPTS["Load prompts from files<br/>(--system-prompt-file,<br/>--prompt-file)"]
    
    GITIGNORE["ensure_stakpak_in_gitignore()"]
    
    MODE["Create RunAsyncConfig or<br/>RunInteractiveConfig"]
    LAUNCH["Launch agent"]
    
    START --> CONTEXT
    CONTEXT --> AGENTS
    AGENTS --> PROVIDER
    PROVIDER --> PARALLEL
    
    PARALLEL --> ACCOUNT
    PARALLEL --> UPDATE
    PARALLEL --> RULEBOOKS
    
    ACCOUNT --> SUBAGENTS
    UPDATE --> SUBAGENTS
    RULEBOOKS --> SUBAGENTS
    
    SUBAGENTS -->|Yes| LOAD_SUB
    SUBAGENTS -->|No| PROMPTS
    LOAD_SUB --> PROMPTS
    
    PROMPTS --> GITIGNORE
    GITIGNORE --> MODE
    MODE --> LAUNCH
```

**Sources:** [cli/src/main.rs:257-507]()

### Parallel Initialization Optimization

To minimize startup delay, three HTTP calls are executed in parallel using `tokio::join!()`:

```rust
let (api_result, update_result, rulebooks_result) = tokio::join!(
    client.get_my_account(),
    check_update(&current_version),
    async {
        client_for_rulebooks
            .list_rulebooks()
            .await
            .ok()
            .map(|rulebooks| {
                if let Some(rulebook_config) = &config_for_rulebooks.rulebooks {
                    rulebook_config.filter_rulebooks(rulebooks)
                } else {
                    rulebooks
                }
            })
    }
);
```

**Sources:** [cli/src/main.rs:304-320]()

---

## Configuration File Format

### Sample Configuration

The system can print a complete sample configuration using the `config sample` subcommand:

```toml
[profiles.all]
api_endpoint = "https://apiv2.stakpak.dev"
allowed_tools = ["view", "search_docs", "read_rulebook", "local_code_search"]
auto_approve = ["view", "search_docs", "read_rulebook"]

[profiles.all.rulebooks]
include = ["stakpak://yourdomain.com/common/**"]
exclude = ["stakpak://yourdomain.com/archive/**"]
include_tags = ["common", "shared"]
exclude_tags = ["archived", "obsolete"]

[profiles.default]
api_key = "your_api_key_here"
allowed_tools = ["view", "search_docs", "read_rulebook", "local_code_search", "create", "str_replace", "run_command"]

[profiles.default.rulebooks]
include = ["stakpak://yourdomain.com/*", "stakpak://**/*.md"]
exclude = ["stakpak://restricted.domain.com/**"]
include_tags = ["terraform", "kubernetes", "security"]
exclude_tags = ["deprecated", "experimental"]

[profiles.default.warden]
enabled = true
volumes = [
    "./:/agent:ro",
    "~/.aws:/home/agent/.aws:ro",
]

[settings]
machine_name = "my-development-machine"
auto_append_gitignore = true
editor = "nano"
```

**Sources:** [cli/src/commands/mod.rs:499-612]()

---

## Execution Mode Selection

### Mode Determination Logic

```rust
let use_async_mode = cli.r#async || cli.print;

match use_async_mode {
    true => run_async(config, RunAsyncConfig { ... }).await,
    false => run_interactive(config, RunInteractiveConfig { ... }).await,
}
```

| Mode | Trigger | Max Steps | UI |
|------|---------|-----------|-----|
| Interactive | Default (no flags) | N/A | Full TUI |
| Async | `--async` | 50 (configurable) | Terminal output |
| Print | `--print` | 1 | Terminal output |

**Sources:** [cli/src/main.rs:426-506]()

### RunAsyncConfig Structure

```rust
pub struct RunAsyncConfig {
    pub prompt: String,
    pub checkpoint_id: Option<String>,
    pub local_context: Option<LocalContext>,
    pub verbose: bool,
    pub redact_secrets: bool,
    pub privacy_mode: bool,
    pub rulebooks: Option<Vec<ListRuleBook>>,
    pub subagent_configs: Option<SubagentConfigs>,
    pub max_steps: Option<usize>,
    pub output_format: OutputFormat,
    pub allowed_tools: Option<Vec<String>>,
    pub enable_mtls: bool,
    pub system_prompt: Option<String>,
    pub enabled_tools: EnabledToolsConfig,
    pub model: AgentModel,
    pub agents_md: Option<AgentsMdInfo>,
}
```

**Sources:** [cli/src/commands/agent/run/mode_async.rs:28-45]()

### RunInteractiveConfig Structure

```rust
pub struct RunInteractiveConfig {
    pub checkpoint_id: Option<String>,
    pub local_context: Option<LocalContext>,
    pub redact_secrets: bool,
    pub privacy_mode: bool,
    pub rulebooks: Option<Vec<ListRuleBook>>,
    pub subagent_configs: Option<SubagentConfigs>,
    pub enable_mtls: bool,
    pub is_git_repo: bool,
    pub study_mode: bool,
    pub system_prompt: Option<String>,
    pub allowed_tools: Option<Vec<String>>,
    pub auto_approve: Option<Vec<String>>,
    pub enabled_tools: EnabledToolsConfig,
    pub model: AgentModel,
    pub agents_md: Option<AgentsMdInfo>,
}
```

**Sources:** [cli/src/commands/agent/run/mode_interactive.rs:51-67]()

---

## Summary Table: Initialization Flow

| Step | Function/Module | Key Operations | Error Handling |
|------|----------------|----------------|----------------|
| 1. Entry | `main()` | Parse args, set workdir | Exit on parse error |
| 2. Crypto | `CryptoProvider::install_default()` | Install rustls provider | Continue (best effort) |
| 3. Profile | Profile resolution | CLI > env > "default" | Use "default" |
| 4. Config Load | `AppConfig::load()` | Parse TOML, resolve profile | Print error, exit |
| 5. Warden Check | Warden config check | Re-execute if enabled | Continue on error |
| 6. Machine Name | Random name generation | Generate if missing | Save to config |
| 7. Auth Check | `requires_auth()` | Check API key presence | Run onboarding |
| 8. Provider | `RemoteClient` or `LocalClient` | Initialize client | Exit on error |
| 9. Context | `analyze_local_context()` | Scan files, git | Continue if fails |
| 10. Parallel Init | `tokio::join!()` | Account, update, rulebooks | Continue (partial) |
| 11. Mode Select | Flag inspection | Route to async/interactive | Default to interactive |
| 12. Agent Launch | `run_async()` or `run_interactive()` | Start agent loop | Print error, exit |

**Sources:** [cli/src/main.rs:147-512]()

---

# Page: Agent Execution Modes

# Agent Execution Modes

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cli/src/commands/agent/run/helpers.rs](cli/src/commands/agent/run/helpers.rs)
- [cli/src/commands/agent/run/mode_async.rs](cli/src/commands/agent/run/mode_async.rs)
- [cli/src/commands/agent/run/mode_interactive.rs](cli/src/commands/agent/run/mode_interactive.rs)
- [cli/src/commands/mod.rs](cli/src/commands/mod.rs)
- [cli/src/main.rs](cli/src/main.rs)

</details>



## Purpose and Scope

This document describes the two execution modes available in the Stakpak CLI: **Interactive Mode** (TUI-based) and **Async Mode** (batch execution). It explains how the CLI determines which mode to use, the architectural differences between them, their configuration structures, and when to use each mode.

For information about the TUI application itself and its internal architecture, see [Terminal User Interface (TUI)](#3). For details about the context injection pipeline that applies to both modes, see [Context Injection Pipeline](#2.3). For session management features available in both modes, see [Session and Profile Management](#2.4).

---

## Execution Mode Selection

The CLI determines which execution mode to use based on command-line flags provided by the user. The decision logic is implemented in [cli/src/main.rs:426-506]().

### Decision Flow

```mermaid
graph TB
    START["CLI Entry Point<br/>main.rs:147"]
    PARSE["Parse CLI Arguments<br/>Cli::parse()"]
    CHECK_COMMAND{"Has subcommand?"}
    CHECK_MODE{"Check mode flags"}
    ASYNC_MODE["Async Mode<br/>--async or --print"]
    INTERACTIVE_MODE["Interactive Mode<br/>Default"]
    RUN_ASYNC["agent::run::run_async()<br/>mode_async.rs:49"]
    RUN_INTERACTIVE["agent::run::run_interactive()<br/>mode_interactive.rs:69"]
    
    START --> PARSE
    PARSE --> CHECK_COMMAND
    CHECK_COMMAND -->|"Yes"| SUBCOMMAND["Execute subcommand<br/>commands/mod.rs:219"]
    CHECK_COMMAND -->|"No"| CHECK_MODE
    CHECK_MODE -->|"cli.async || cli.print"| ASYNC_MODE
    CHECK_MODE -->|"Default"| INTERACTIVE_MODE
    ASYNC_MODE --> RUN_ASYNC
    INTERACTIVE_MODE --> RUN_INTERACTIVE
    
    style RUN_ASYNC fill:#f9f9f9
    style RUN_INTERACTIVE fill:#f9f9f9
```

**Sources:** [cli/src/main.rs:41-142](), [cli/src/main.rs:426-506]()

### Mode Selection Flags

| Flag | Description | Resulting Mode | Max Steps Default |
|------|-------------|----------------|-------------------|
| None | Default behavior | Interactive (TUI) | N/A |
| `--async` / `-a` | Run until completion | Async | 50 |
| `--print` / `-p` | Single-step execution | Async | 1 |
| `--max-steps` / `-m` | Override step limit | Based on other flags | User-specified |

**Sources:** [cli/src/main.rs:45-55](), [cli/src/main.rs:426-433]()

---

## Configuration Structures

Both execution modes use dedicated configuration structures to encapsulate their parameters.

### RunInteractiveConfig

The `RunInteractiveConfig` structure contains all parameters required for interactive mode execution:

```mermaid
classDiagram
    class RunInteractiveConfig {
        +Option~String~ checkpoint_id
        +Option~LocalContext~ local_context
        +bool redact_secrets
        +bool privacy_mode
        +Option~Vec~ListRuleBook~~ rulebooks
        +Option~SubagentConfigs~ subagent_configs
        +bool enable_mtls
        +bool is_git_repo
        +bool study_mode
        +Option~String~ system_prompt
        +Option~Vec~String~~ allowed_tools
        +Option~Vec~String~~ auto_approve
        +EnabledToolsConfig enabled_tools
        +AgentModel model
        +Option~AgentsMdInfo~ agents_md
    }
    
    class EnabledToolsConfig {
        +bool slack
    }
    
    class AgentModel {
        <<enumeration>>
        Smart
        Eco
    }
    
    RunInteractiveConfig --> EnabledToolsConfig
    RunInteractiveConfig --> AgentModel
```

**Sources:** [cli/src/commands/agent/run/mode_interactive.rs:51-67]()

### RunAsyncConfig

The `RunAsyncConfig` structure contains parameters for async mode execution:

```mermaid
classDiagram
    class RunAsyncConfig {
        +String prompt
        +Option~String~ checkpoint_id
        +Option~LocalContext~ local_context
        +bool verbose
        +bool redact_secrets
        +bool privacy_mode
        +Option~Vec~ListRuleBook~~ rulebooks
        +Option~SubagentConfigs~ subagent_configs
        +Option~usize~ max_steps
        +OutputFormat output_format
        +Option~Vec~String~~ allowed_tools
        +bool enable_mtls
        +Option~String~ system_prompt
        +EnabledToolsConfig enabled_tools
        +AgentModel model
        +Option~AgentsMdInfo~ agents_md
    }
    
    class OutputFormat {
        <<enumeration>>
        Text
        Json
    }
    
    RunAsyncConfig --> OutputFormat
    RunAsyncConfig --> EnabledToolsConfig
    RunAsyncConfig --> AgentModel
```

**Sources:** [cli/src/commands/agent/run/mode_async.rs:28-45]()

### Key Differences

The main differences between the configuration structures:

| Feature | Interactive | Async | Rationale |
|---------|-------------|-------|-----------|
| `prompt` | Not present | Required `String` | Interactive takes prompt from TUI input |
| `auto_approve` | Present | Not present | Interactive mode supports tool approval workflow |
| `is_git_repo` | Present | Not present | TUI displays git-specific UI elements |
| `study_mode` | Present | Not present | TUI feature for study assistance |
| `verbose` | Not present | Present | Async mode controls console verbosity |
| `output_format` | Not present | Present | Async mode supports JSON/Text output |
| `max_steps` | Not present | Present | Async mode has step limits |

**Sources:** [cli/src/commands/agent/run/mode_interactive.rs:51-67](), [cli/src/commands/agent/run/mode_async.rs:28-45]()

---

## Interactive Mode Architecture

Interactive mode spawns a TUI subprocess and communicates with it through bidirectional channels. It supports profile switching through an outer loop that restarts the entire session.

### Component Architecture

```mermaid
graph TB
    subgraph "Main CLI Process"
        MAIN["run_interactive()<br/>mode_interactive.rs:69"]
        PROFILE_LOOP["Profile Switch Loop<br/>line 74"]
        CONFIG_INIT["Configuration Initialization<br/>lines 75-106"]
    end
    
    subgraph "Channel Communication"
        INPUT_TX["input_tx<br/>Sender~InputEvent~<br/>line 108"]
        INPUT_RX["input_rx<br/>Receiver~InputEvent~<br/>line 108"]
        OUTPUT_TX["output_tx<br/>Sender~OutputEvent~<br/>line 109"]
        OUTPUT_RX["output_rx<br/>Receiver~OutputEvent~<br/>line 109"]
    end
    
    subgraph "TUI Task - Spawned"
        TUI_SPAWN["tokio::spawn<br/>line 128"]
        TUI_RUN["stakpak_tui::run_tui()<br/>line 130"]
        TUI_EVENT_LOOP["TUI Event Loop"]
    end
    
    subgraph "Client Task - Spawned"
        CLIENT_SPAWN["tokio::spawn<br/>line 163"]
        PROVIDER_INIT["AgentProvider Initialization<br/>lines 166-190"]
        MCP_INIT["MCP Initialization<br/>lines 192-220"]
        EVENT_HANDLER["OutputEvent Handler Loop<br/>lines 294-828"]
    end
    
    subgraph "Backend Services"
        AGENT_PROVIDER["RemoteClient or LocalClient"]
        MCP_CLIENT["MCP Client"]
    end
    
    MAIN --> PROFILE_LOOP
    PROFILE_LOOP --> CONFIG_INIT
    CONFIG_INIT --> INPUT_TX
    CONFIG_INIT --> OUTPUT_RX
    
    INPUT_TX --> TUI_SPAWN
    TUI_SPAWN --> TUI_RUN
    TUI_RUN --> TUI_EVENT_LOOP
    TUI_EVENT_LOOP --> OUTPUT_TX
    OUTPUT_TX --> OUTPUT_RX
    OUTPUT_RX --> EVENT_HANDLER
    
    CLIENT_SPAWN --> PROVIDER_INIT
    PROVIDER_INIT --> MCP_INIT
    MCP_INIT --> EVENT_HANDLER
    
    EVENT_HANDLER --> INPUT_TX
    EVENT_HANDLER --> AGENT_PROVIDER
    EVENT_HANDLER --> MCP_CLIENT
    
    style PROFILE_LOOP fill:#f9f9f9
    style TUI_EVENT_LOOP fill:#f9f9f9
    style EVENT_HANDLER fill:#f9f9f9
```

**Sources:** [cli/src/commands/agent/run/mode_interactive.rs:69-773]()

### Event Flow and Communication

Interactive mode uses two channel pairs for bidirectional communication:

```mermaid
sequenceDiagram
    participant User
    participant TUI as "TUI Task<br/>(run_tui)"
    participant Main as "Main Thread"
    participant Client as "Client Task<br/>(Backend Logic)"
    participant Backend as "AgentProvider<br/>+ MCP Client"
    
    User->>TUI: Keyboard Input
    TUI->>TUI: map_crossterm_event_to_input_event
    TUI->>Main: OutputEvent::UserMessage
    Main->>Client: forward via output_rx
    Client->>Backend: chat_completion()
    Backend-->>Client: Response + ToolCalls
    Client->>TUI: InputEvent::MessageToolCalls
    TUI->>User: Display Tools
    User->>TUI: Approve Tool
    TUI->>Main: OutputEvent::AcceptTool
    Main->>Client: forward via output_rx
    Client->>Backend: run_tool_call()
    Backend-->>Client: Tool Result
    Client->>TUI: InputEvent::ToolResult
    TUI->>User: Display Result
```

**Sources:** [cli/src/commands/agent/run/mode_interactive.rs:108-157](), [cli/src/commands/agent/run/mode_interactive.rs:294-828]()

### Profile Switching Mechanism

Interactive mode implements profile switching through an outer loop that can restart the entire session:

```mermaid
graph TB
    START["run_interactive() Entry<br/>line 69"]
    OUTER_LOOP["'profile_switch_loop<br/>line 74"]
    INIT["Initialize State<br/>lines 75-106"]
    SPAWN_TASKS["Spawn TUI + Client Tasks<br/>lines 108-163"]
    EVENT_LOOP["Event Processing Loop<br/>lines 294-828"]
    SWITCH_EVENT{"OutputEvent::<br/>RequestProfileSwitch?"}
    VALIDATE["Validate New Profile<br/>lines 729-743"]
    SHUTDOWN["Send Shutdown Signal<br/>line 770"]
    RETURN_NEW_CONFIG["Return new AppConfig<br/>lines 773-778"]
    CONTINUE["Continue Event Loop"]
    
    START --> OUTER_LOOP
    OUTER_LOOP --> INIT
    INIT --> SPAWN_TASKS
    SPAWN_TASKS --> EVENT_LOOP
    EVENT_LOOP --> SWITCH_EVENT
    SWITCH_EVENT -->|"Yes"| VALIDATE
    SWITCH_EVENT -->|"No"| CONTINUE
    CONTINUE --> EVENT_LOOP
    VALIDATE --> SHUTDOWN
    SHUTDOWN --> RETURN_NEW_CONFIG
    RETURN_NEW_CONFIG --> OUTER_LOOP
    
    style OUTER_LOOP fill:#f9f9f9
    style SWITCH_EVENT fill:#f9f9f9
```

**Sources:** [cli/src/commands/agent/run/mode_interactive.rs:74-779]()

### Key OutputEvent Handlers

The client task handles various `OutputEvent` types from the TUI:

| Event Type | Handler Lines | Description |
|------------|---------------|-------------|
| `SwitchModel` | 296-299 | Switch between Smart/Eco models |
| `UserMessage` | 300-386 | Process user input with context injection |
| `AcceptTool` | 387-471 | Execute approved tool call |
| `RejectTool` | 472-485 | Reject tool call and continue |
| `ListSessions` | 486-512 | Fetch session list |
| `NewSession` | 513-524 | Clear current session |
| `ResumeSession` | 526-608 | Resume from checkpoint |
| `SwitchToSession` | 609-668 | Switch to specific session |
| `SendToolResult` | 670-701 | Submit shell mode result |
| `Memorize` | 702-713 | Trigger memorization |
| `RequestProfileSwitch` | 714-779 | Handle profile switch |
| `RequestRulebookUpdate` | 780-796 | Update active rulebooks |

**Sources:** [cli/src/commands/agent/run/mode_interactive.rs:294-828]()

---

## Async Mode Architecture

Async mode executes in a single linear loop without spawning additional tasks. It runs until completion or reaches the maximum step limit.

### Execution Flow

```mermaid
graph TB
    START["run_async() Entry<br/>line 49"]
    INIT["Initialize Components<br/>lines 50-110"]
    MCP_INIT["Initialize MCP Server<br/>lines 63-84"]
    PROVIDER["Create AgentProvider<br/>lines 86-110"]
    CHECKPOINT["Load Checkpoint if specified<br/>lines 113-142"]
    SYSTEM_PROMPT["Add System Prompt if specified<br/>lines 144-147"]
    USER_PROMPT["Add User Prompt with Context<br/>lines 149-177"]
    LOOP_START["Execution Loop Start<br/>line 187"]
    CHECK_STEPS{"step > max_steps?"}
    CHAT_COMPLETION["client.chat_completion()<br/>lines 202-209"]
    ACCUMULATE_USAGE["Accumulate Token Usage<br/>lines 213-233"]
    CHECK_TOOLS{"Has tool_calls?"}
    EXECUTE_TOOLS["Execute Tool Calls<br/>lines 281-342"]
    LOOP_END["Continue Loop"]
    COMPLETE["Execution Complete<br/>lines 344-349"]
    SUMMARY["Print Summary<br/>lines 363-447"]
    SHUTDOWN["Shutdown MCP<br/>lines 449-457"]
    
    START --> INIT
    INIT --> MCP_INIT
    MCP_INIT --> PROVIDER
    PROVIDER --> CHECKPOINT
    CHECKPOINT --> SYSTEM_PROMPT
    SYSTEM_PROMPT --> USER_PROMPT
    USER_PROMPT --> LOOP_START
    LOOP_START --> CHECK_STEPS
    CHECK_STEPS -->|"Yes"| COMPLETE
    CHECK_STEPS -->|"No"| CHAT_COMPLETION
    CHAT_COMPLETION --> ACCUMULATE_USAGE
    ACCUMULATE_USAGE --> CHECK_TOOLS
    CHECK_TOOLS -->|"Yes"| EXECUTE_TOOLS
    CHECK_TOOLS -->|"No"| COMPLETE
    EXECUTE_TOOLS --> LOOP_END
    LOOP_END --> LOOP_START
    COMPLETE --> SUMMARY
    SUMMARY --> SHUTDOWN
    
    style LOOP_START fill:#f9f9f9
    style CHECK_TOOLS fill:#f9f9f9
```

**Sources:** [cli/src/commands/agent/run/mode_async.rs:49-460]()

### Step Execution Logic

Each step in async mode follows this pattern:

1. **Increment Step Counter** - [line 188]()
2. **Check Step Limit** - [lines 189-198]() - Exits if `step > max_steps`
3. **Call LLM** - [lines 201-209]() - `client.chat_completion()` with messages and tools
4. **Accumulate Usage** - [lines 212-233]() - Track token consumption
5. **Render Response** - [lines 248-267]() - Display assistant message
6. **Process Tool Calls** - [lines 270-342]() - Execute each tool sequentially with 60-minute timeout per tool
7. **Append Results** - [line 332]() - Add tool results to `chat_messages`

**Sources:** [cli/src/commands/agent/run/mode_async.rs:187-350]()

### Output Rendering

Async mode uses the `OutputRenderer` to format console output based on `OutputFormat`:

```mermaid
classDiagram
    class OutputRenderer {
        +output_format: OutputFormat
        +verbose: bool
        +new(format, verbose) OutputRenderer
        +render_title(text) String
        +render_info(text) String
        +render_step_header(step, tool_count) String
        +render_assistant_message(content, stream) String
        +render_tool_execution(name, args, idx, total) String
        +render_tool_result(content) String
        +render_success(text) String
        +render_warning(text) String
        +render_error(text) String
        +render_section_break() String
        +render_token_usage_stats(usage) String
    }
    
    class OutputFormat {
        <<enumeration>>
        Text
        Json
    }
    
    OutputRenderer --> OutputFormat
```

**Sources:** [cli/src/commands/agent/run/mode_async.rs:54-184](), [cli/src/commands/agent/run/renderer.rs]()

---

## Mode Comparison

### Architectural Differences

| Aspect | Interactive Mode | Async Mode |
|--------|------------------|------------|
| **Process Model** | Multi-task (TUI + Client tasks) | Single-task linear execution |
| **User Interaction** | Real-time via TUI | Batch, no interaction during execution |
| **Communication** | Channel-based (InputEvent/OutputEvent) | Direct function calls |
| **Profile Switching** | Supported via outer loop | Not supported |
| **Tool Approval** | Manual approval per tool | Automatic execution |
| **Session Management** | Full support (resume, switch, new) | Checkpoint resume only |
| **Output Format** | Rich TUI rendering | Text or JSON |
| **Step Limit** | No limit (user controls) | Configurable max_steps (default: 50) |
| **Context Injection** | On first message + profile switch | On first message only |

**Sources:** [cli/src/commands/agent/run/mode_interactive.rs:69-1233](), [cli/src/commands/agent/run/mode_async.rs:49-460]()

### Execution Context

```mermaid
graph LR
    subgraph "Interactive Mode Context"
        ITUI["TUI Process"]
        ICLIENT["Client Task"]
        ISTATE["Persistent State"]
        IUSER["User Interaction"]
    end
    
    subgraph "Async Mode Context"
        ALOOP["Single Loop"]
        AMESSAGES["Message Array"]
        ASTEPS["Step Counter"]
    end
    
    ITUI <-->|"Channels"| ICLIENT
    IUSER -->|"Real-time"| ITUI
    ICLIENT <-->|"Events"| ISTATE
    
    ALOOP -->|"Append"| AMESSAGES
    ALOOP -->|"Increment"| ASTEPS
    
    style ITUI fill:#f9f9f9
    style ALOOP fill:#f9f9f9
```

**Sources:** [cli/src/commands/agent/run/mode_interactive.rs](), [cli/src/commands/agent/run/mode_async.rs]()

### Common Components

Both modes share several components:

1. **AgentProvider Initialization** - Both create either `RemoteClient` or `LocalClient` based on `ctx.provider`
   - Interactive: [lines 166-190]()
   - Async: [lines 86-110]()

2. **MCP Initialization** - Both use `initialize_mcp_server_and_tools()` with `McpInitConfig`
   - Interactive: [lines 192-220]()
   - Async: [lines 63-73]()

3. **Context Injection** - Both use helpers from `helpers.rs`:
   - `add_local_context()` - [lines 71-98]()
   - `add_rulebooks()` - [lines 100-130]()
   - `add_subagents()` - [lines 132-152]()
   - `add_agents_md()` - [lines 184-188]()

4. **Tool Execution** - Both use `run_tool_call()` from `tooling.rs`
   - Interactive: [lines 393-401]()
   - Async: [lines 295-296]()

5. **Checkpoint Loading** - Both use `get_checkpoint_messages()`
   - Interactive: [lines 249-285]()
   - Async: [lines 113-142]()

**Sources:** [cli/src/commands/agent/run/mode_interactive.rs](), [cli/src/commands/agent/run/mode_async.rs](), [cli/src/commands/agent/run/helpers.rs]()

---

## When to Use Each Mode

### Interactive Mode (Default)

**Use Cases:**
- Development and debugging workflows
- Exploratory tasks requiring human judgment
- Operations with destructive potential
- Learning and studying (with `--study-mode`)
- Working with unfamiliar codebases
- Multi-session management
- Profile switching during execution

**Advantages:**
- Full control over tool execution
- Visual feedback and progress tracking
- Ability to review tool calls before execution
- Session management (resume, switch, new)
- Profile switching without restarting
- Shell mode for interactive commands
- Rich markdown rendering

**Command:**
```bash
stakpak                              # Default interactive mode
stakpak --profile production         # With specific profile
stakpak --checkpoint abc123          # Resume from checkpoint
```

**Sources:** [cli/src/main.rs:476-505](), [cli/src/commands/agent/run/mode_interactive.rs:51-67]()

### Async Mode (Batch)

**Use Cases:**
- CI/CD pipelines
- Automated scripts
- Non-interactive environments
- Single-task execution with known parameters
- JSON output for programmatic processing
- Performance benchmarking

**Advantages:**
- No user interaction required
- Predictable execution (step limit)
- Structured output (JSON support)
- Lower resource usage (no TUI)
- Faster startup (no TUI initialization)
- Clean exit on completion

**Command:**
```bash
stakpak --async "implement user auth"      # Full execution
stakpak --print "explain this code"        # Single step
stakpak --async --max-steps 10             # Limited steps
stakpak --async --output json              # JSON output
stakpak --prompt-file task.txt --async     # From file
```

**Sources:** [cli/src/main.rs:441-473](), [cli/src/commands/agent/run/mode_async.rs:28-45]()

### Single-Step Mode (Print Flag)

The `--print` flag is a special case of async mode that forces `max_steps=1`:

```mermaid
graph LR
    PRINT_FLAG["--print flag"]
    FORCE_MAX["max_steps = Some(1)<br/>main.rs:429-433"]
    ASYNC_MODE["run_async()"]
    SINGLE_STEP["Single LLM Call"]
    EXIT["Exit after response"]
    
    PRINT_FLAG --> FORCE_MAX
    FORCE_MAX --> ASYNC_MODE
    ASYNC_MODE --> SINGLE_STEP
    SINGLE_STEP --> EXIT
    
    style FORCE_MAX fill:#f9f9f9
```

**Use Cases:**
- Getting explanations without execution
- Code review and analysis
- Quick questions
- Testing prompts

**Command:**
```bash
stakpak --print "explain this function"
```

**Sources:** [cli/src/main.rs:429-433](), [cli/src/commands/agent/run/mode_async.rs:189-198]()

---

## Mode-Specific Features

### Interactive Mode Only

| Feature | Description | Reference |
|---------|-------------|-----------|
| Profile Switching | Switch profiles without exiting | [lines 714-779]() |
| Tool Approval | Manual approval with `auto_approve` list | [lines 387-471]() |
| Session Management | List, resume, switch sessions | [lines 486-668]() |
| Shell Mode | Interactive shell with VT100 emulation | [lines 670-701]() |
| Rulebook Switcher | Change active rulebooks mid-session | [lines 780-796]() |
| Command Palette | Quick action menu | TUI feature |
| Hint System | Context-aware help | TUI feature |
| Billing Display | Real-time balance (remote only) | [lines 228-230]() |

**Sources:** [cli/src/commands/agent/run/mode_interactive.rs]()

### Async Mode Only

| Feature | Description | Reference |
|---------|-------------|-----------|
| Step Limiting | `max_steps` safety limit | [lines 189-198]() |
| JSON Output | Structured output format | [lines 54-55]() |
| Verbose Mode | Detailed execution logs | [lines 32, 54]() |
| Prompt Files | Read prompt from file | [main.rs:407-423]() |
| Execution Summary | Token usage and timing stats | [lines 359-446]() |
| Timeout Per Tool | 60-minute limit per tool | [lines 299-316]() |

**Sources:** [cli/src/commands/agent/run/mode_async.rs:28-460](), [cli/src/main.rs:407-423]()

---

# Page: Context Injection Pipeline

# Context Injection Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cli/src/commands/agent/run/helpers.rs](cli/src/commands/agent/run/helpers.rs)
- [cli/src/commands/agent/run/mode_async.rs](cli/src/commands/agent/run/mode_async.rs)
- [cli/src/commands/agent/run/mode_interactive.rs](cli/src/commands/agent/run/mode_interactive.rs)
- [cli/src/commands/mod.rs](cli/src/commands/mod.rs)
- [cli/src/main.rs](cli/src/main.rs)

</details>



## Purpose and Scope

The Context Injection Pipeline is responsible for enriching user prompts with relevant contextual information before sending them to the LLM. This system prepares the initial conversation by injecting local project context, organizational policies (rulebooks), subagent configurations, and AGENTS.md files into user messages. The pipeline executes conditionally based on message history and configuration settings, ensuring context is provided when needed without unnecessary repetition.

For information about session management and checkpoints, see [Session and Profile Management](#2.4). For details on how tools are executed after the LLM responds, see [Tool Container and Execution Flow](#5.2).

## Pipeline Architecture

The context injection pipeline consists of five distinct components, each handled by a dedicated helper function. These functions wrap user input with XML-tagged context sections that guide the LLM's understanding of the operational environment.

### Pipeline Execution Flow

```mermaid
graph TB
    UserInput["User Input<br/>(String)"]
    
    CheckFirst{"Is first message<br/>OR force_add?"}
    CheckRulebooks{"Rulebooks configured<br/>AND first message?"}
    CheckSubagents{"Subagents enabled<br/>AND first message?"}
    CheckAgentsMd{"AGENTS.md discovered<br/>AND first message?"}
    CheckShellHistory{"Shell history<br/>available?"}
    
    AddLocalContext["add_local_context()<br/>Wraps with &lt;local_context&gt;"]
    AddRulebooks["add_rulebooks()<br/>Wraps with &lt;rulebooks&gt;"]
    AddSubagents["add_subagents()<br/>Wraps with &lt;subagents&gt;"]
    AddAgentsMd["add_agents_md()<br/>Wraps with &lt;agents_md&gt;"]
    PrependHistory["tool_call_history_string()<br/>Prepends shell history"]
    
    FinalMessage["user_message()<br/>ChatMessage with Role::User"]
    
    UserInput --> CheckShellHistory
    CheckShellHistory -->|Yes| PrependHistory
    CheckShellHistory -->|No| CheckFirst
    PrependHistory --> CheckFirst
    
    CheckFirst -->|Yes| AddLocalContext
    CheckFirst -->|No| CheckRulebooks
    
    AddLocalContext --> CheckRulebooks
    CheckRulebooks -->|Yes| AddRulebooks
    CheckRulebooks -->|No| CheckSubagents
    
    AddRulebooks --> CheckSubagents
    CheckSubagents -->|Yes| AddSubagents
    CheckSubagents -->|No| CheckAgentsMd
    
    AddSubagents --> CheckAgentsMd
    CheckAgentsMd -->|Yes| AddAgentsMd
    CheckAgentsMd -->|No| FinalMessage
    
    AddAgentsMd --> FinalMessage
```

**Sources:** [cli/src/commands/agent/run/mode_interactive.rs:300-344](), [cli/src/commands/agent/run/mode_async.rs:150-176](), [cli/src/commands/agent/run/helpers.rs:71-188]()

## Context Components

### Local Context Component

The `LocalContext` structure provides filesystem and project metadata to the LLM. This component is managed by `add_local_context()` and only injects on the first message or when explicitly forced (e.g., after rulebook updates or session resume).

```mermaid
graph LR
    subgraph "LocalContext Structure"
        LC[LocalContext]
        Files["supported_files<br/>Vec&lt;String&gt;"]
        Tree["tree_display<br/>String"]
        Deps["dependencies<br/>Option&lt;Vec&lt;Dependency&gt;&gt;"]
    end
    
    subgraph "Injection Logic"
        Input["user_input: &str"]
        Check{"is_first_message<br/>OR force_add?"}
        Format["format_display()"]
        Wrap["Wrap with<br/>&lt;local_context&gt; tag"]
        Output["Modified user_input"]
    end
    
    LC --> Files
    LC --> Tree
    LC --> Deps
    
    Input --> Check
    Check -->|Yes| Format
    Format --> Wrap
    Wrap --> Output
    Check -->|No| Output
    
    Files --> Format
    Tree --> Format
    Deps --> Format
```

The `add_local_context()` function checks if the current message is the first non-system message in the conversation or if `force_add` is true. When triggered, it calls `local_context.format_display().await` to generate the context string and wraps it with `<local_context>` XML tags.

**Sources:** [cli/src/commands/agent/run/helpers.rs:71-98](), [cli/src/utils/local_context.rs]()

### Rulebooks Component

Rulebooks represent organizational policies and SOPs that guide agent behavior. The `add_rulebooks()` function formats a list of `ListRuleBook` objects into a human-readable list structure.

| Field | Type | Description |
|-------|------|-------------|
| `uri` | String | Unique identifier for the rulebook |
| `description` | String | Human-readable summary |
| `tags` | Vec\<String\> | Categorization tags |
| `content` | String | Full rulebook text |

The function formats rulebooks with indentation to improve readability:

```
<rulebooks>

# My Rule Books:

  - [URI] stakpak://domain.com/policy
    Description: Security best practices
    Tags: security, compliance
  
  - [URI] stakpak://domain.com/terraform
    Description: Terraform coding standards
    Tags: infrastructure, terraform

</rulebooks>
```

Rulebooks are only injected on the first message or after the user changes rulebook selections via the TUI switcher (controlled by `should_update_rulebooks_on_next_message` flag).

**Sources:** [cli/src/commands/agent/run/helpers.rs:100-130](), [cli/src/commands/agent/run/mode_interactive.rs:312-329]()

### Subagents Component

Subagent configurations enable delegating specialized tasks to other AI agents. The `add_subagents()` function injects `SubagentConfigs` on the first message only.

```mermaid
graph TB
    subgraph "SubagentConfigs"
        SC[SubagentConfigs]
        Agents["agents<br/>HashMap&lt;String, SubagentConfig&gt;"]
    end
    
    subgraph "SubagentConfig Fields"
        Name["name: String"]
        Desc["description: String"]
        Model["model: AgentModel"]
        Tools["tools: Vec&lt;String&gt;"]
        SysPrompt["system_prompt: Option&lt;String&gt;"]
    end
    
    subgraph "Injection"
        Format["format_for_context()"]
        Wrap["Wrap with<br/>&lt;subagents&gt; tag"]
        FirstMsg{"messages.is_empty()?"}
    end
    
    SC --> Agents
    Agents --> Name
    Agents --> Desc
    Agents --> Model
    Agents --> Tools
    Agents --> SysPrompt
    
    SC --> Format
    FirstMsg -->|Yes| Format
    Format --> Wrap
```

The formatted output includes each subagent's name, description, capabilities, and usage instructions. Subagents are loaded from either a custom `subagents.toml` file or the default embedded configuration.

**Sources:** [cli/src/commands/agent/run/helpers.rs:132-152](), [cli/src/main.rs:341-359](), [stakpak_shared/src/models/subagent.rs]()

### AGENTS.md Component

The `AGENTS.md` file is a special convention for documenting multi-agent systems. When discovered in the project directory hierarchy, it's injected on the first message via `add_agents_md()`.

The discovery process uses `discover_agents_md()` to search from the current working directory up through parent directories until an `AGENTS.md` file is found. The file is parsed to extract:

- Agent roles and responsibilities
- Communication patterns between agents
- Delegation guidelines

**Sources:** [cli/src/commands/agent/run/helpers.rs:184-188](), [cli/src/main.rs:259-265](), [cli/src/utils/agents_md.rs]()

### Shell History Component

When the TUI's shell mode has executed commands, their history is prepended to the user's next message via `tool_call_history_string()`. This provides continuity between interactive shell sessions and LLM conversations.

```mermaid
graph LR
    subgraph "Shell History"
        TCR["ToolCallResult[]<br/>from shell mode"]
        Extract["Extract command<br/>from arguments"]
        FormatCmd["Format as<br/>```shell blocks"]
        Prepend["Prepend to<br/>user input"]
    end
    
    TCR --> Extract
    Extract --> FormatCmd
    FormatCmd --> Prepend
```

Each tool call result is formatted as a shell block containing the command and its output:

```shell
$ ls -la
total 48
drwxr-xr-x  6 user  staff   192 Dec 10 14:23 .
...

$ cat package.json
{
  "name": "my-project",
  ...
}
```

**Sources:** [cli/src/commands/agent/run/helpers.rs:154-182](), [cli/src/commands/agent/run/mode_interactive.rs:303-308]()

## Pipeline Implementation in Execution Modes

### Interactive Mode Pipeline

In interactive mode (`mode_interactive.rs`), the pipeline executes when handling `OutputEvent::UserMessage` events. The implementation tracks state to determine when to re-inject context:

```mermaid
graph TB
    OutputEvent["OutputEvent::UserMessage<br/>(user_input, tool_calls_results, image_parts)"]
    
    CheckHistory{"tool_calls_results<br/>present?"}
    PrependHistory["Prepend shell history<br/>via tool_call_history_string()"]
    
    CheckConditions{"messages.is_empty()<br/>OR should_update_rulebooks<br/>_on_next_message?"}
    
    PipelineExec["Execute full pipeline:<br/>1. add_local_context()<br/>2. add_rulebooks()<br/>3. add_subagents()<br/>4. add_agents_md()"]
    
    SkipPipeline["Skip context injection<br/>(already provided)"]
    
    CreateMessage["Create ChatMessage<br/>with Role::User"]
    PushToMessages["messages.push(user_msg)"]
    
    OutputEvent --> CheckHistory
    CheckHistory -->|Yes| PrependHistory
    CheckHistory -->|No| CheckConditions
    PrependHistory --> CheckConditions
    
    CheckConditions -->|Yes| PipelineExec
    CheckConditions -->|No| SkipPipeline
    
    PipelineExec --> CreateMessage
    SkipPipeline --> CreateMessage
    CreateMessage --> PushToMessages
```

The `should_update_rulebooks_on_next_message` flag is set to `true` when:
- A session is resumed from checkpoint ([mode_interactive.rs:558]())
- A user switches to a different session ([mode_interactive.rs:627]())
- A user updates rulebook selections via the TUI ([mode_interactive.rs:793]())

**Sources:** [cli/src/commands/agent/run/mode_interactive.rs:300-373](), [cli/src/commands/agent/run/mode_interactive.rs:557-558](), [cli/src/commands/agent/run/mode_interactive.rs:793]()

### Async Mode Pipeline

In async mode (`mode_async.rs`), the pipeline executes once during initialization before the agent loop begins. Since async mode is non-interactive, context is injected unconditionally if the message list is empty:

```mermaid
graph TB
    CheckCheckpoint{"checkpoint_id<br/>provided?"}
    LoadCheckpoint["Load checkpoint messages<br/>via get_checkpoint_messages()"]
    
    CheckPrompt{"prompt<br/>not empty?"}
    
    AddLocalCtx["add_local_context()<br/>(force_add=false)"]
    AddRB["add_rulebooks()<br/>(if messages.is_empty())"]
    AddSA["add_subagents()<br/>(if messages.is_empty())"]
    AddAMD["add_agents_md()<br/>(if messages.is_empty())"]
    
    PushMessage["messages.push(<br/>user_message(user_input))"]
    
    StartLoop["Begin agent loop<br/>(chat_completion calls)"]
    
    CheckCheckpoint -->|Yes| LoadCheckpoint
    CheckCheckpoint -->|No| CheckPrompt
    LoadCheckpoint --> CheckPrompt
    
    CheckPrompt -->|Yes| AddLocalCtx
    CheckPrompt -->|No| StartLoop
    
    AddLocalCtx --> AddRB
    AddRB --> AddSA
    AddSA --> AddAMD
    AddAMD --> PushMessage
    PushMessage --> StartLoop
```

The conditional checks for `messages.is_empty()` within each helper function ensure context is only added if no checkpoint was loaded, since checkpoint messages already contain historical context.

**Sources:** [cli/src/commands/agent/run/mode_async.rs:149-177]()

## Helper Function Reference

### add_local_context

```rust
pub async fn add_local_context<'a>(
    messages: &'a [ChatMessage],
    user_input: &'a str,
    local_context: &'a Option<LocalContext>,
    force_add: bool,
) -> Result<(String, Option<&'a LocalContext>), Box<dyn std::error::Error>>
```

**Logic:**
1. Check if `local_context` is `Some`
2. Count non-system messages to determine if this is the first message
3. If first message OR `force_add` is true:
   - Call `local_context.format_display().await`
   - Wrap result in `<local_context>` tags
   - Return modified input
4. Otherwise, return original input unchanged

**Sources:** [cli/src/commands/agent/run/helpers.rs:71-98]()

### add_rulebooks

```rust
pub fn add_rulebooks(user_input: &str, rulebooks: &[ListRuleBook]) -> (String, Option<String>)
```

**Logic:**
1. Build formatted string from `rulebooks` slice
2. Each rulebook is indented with `  - ` for first line, `    ` for continuation
3. Wrap entire list in `<rulebooks>` tags
4. Return tuple of (modified_input, rulebooks_text)

**Sources:** [cli/src/commands/agent/run/helpers.rs:100-130]()

### add_subagents

```rust
pub fn add_subagents(
    messages: &[ChatMessage],
    user_input: &str,
    subagent_configs: &Option<SubagentConfigs>,
) -> (String, Option<String>)
```

**Logic:**
1. Check if `subagent_configs` is `Some`
2. Call `subagent_configs.format_for_context()` to generate text
3. If `messages.is_empty()`:
   - Wrap in `<subagents>` tags
   - Return modified input
4. Otherwise, return original input unchanged

**Sources:** [cli/src/commands/agent/run/helpers.rs:132-152]()

### add_agents_md

```rust
pub fn add_agents_md(user_input: &str, agents_md: &AgentsMdInfo) -> (String, String)
```

**Logic:**
1. Call `format_agents_md_for_context(agents_md)` to generate text
2. Wrap in `<agents_md>` tags
3. Return tuple of (modified_input, agents_text)

Unlike other helpers, this function has no conditional logic—the caller is responsible for checking `messages.is_empty()`.

**Sources:** [cli/src/commands/agent/run/helpers.rs:184-188]()

### tool_call_history_string

```rust
pub fn tool_call_history_string(tool_calls: &[ToolCallResult]) -> Option<String>
```

**Logic:**
1. Return `None` if `tool_calls` is empty
2. For each `ToolCallResult`:
   - Parse `function.arguments` JSON to extract `command` field
   - Format as shell code block with command and result
3. Join all blocks with newlines
4. Return `Some(formatted_history)`

**Sources:** [cli/src/commands/agent/run/helpers.rs:154-182]()

## Configuration and Initialization

Context components are initialized during CLI startup before entering execution mode:

| Component | Initialization | Location |
|-----------|----------------|----------|
| Local Context | `analyze_local_context(&config).await` | [main.rs:257]() |
| Rulebooks | `client.list_rulebooks().await` + filtering | [main.rs:307-319]() |
| Subagents | Load from file or default config | [main.rs:341-359]() |
| AGENTS.md | `discover_agents_md(&cwd)` | [main.rs:262-265]() |
| System Prompt | Load from file if `--system-prompt-file` | [main.rs:385-405]() |

These initialized values are passed to `RunInteractiveConfig` or `RunAsyncConfig` structures, which carry them through to the execution mode implementations.

**Sources:** [cli/src/main.rs:250-497]()

## XML Tag Convention

All context components use XML-style tags to clearly delineate boundaries for the LLM:

```
<local_context>
...filesystem tree and dependencies...
</local_context>

<rulebooks>
...organizational policies...
</rulebooks>

<subagents>
...delegatable agent definitions...
</subagents>

<agents_md>
...multi-agent system documentation...
</agents_md>
```

This convention ensures the LLM can reliably parse context sections and understand their semantic roles without confusion between different types of information.

**Sources:** [cli/src/commands/agent/run/helpers.rs:71-188]()

---

# Page: Session and Profile Management

# Session and Profile Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/stakpak-dark.png](assets/stakpak-dark.png)
- [assets/stakpak-light.png](assets/stakpak-light.png)
- [cli/src/commands/agent/run/helpers.rs](cli/src/commands/agent/run/helpers.rs)
- [cli/src/commands/agent/run/mode_async.rs](cli/src/commands/agent/run/mode_async.rs)
- [cli/src/commands/agent/run/mode_interactive.rs](cli/src/commands/agent/run/mode_interactive.rs)
- [cli/src/commands/mod.rs](cli/src/commands/mod.rs)
- [cli/src/main.rs](cli/src/main.rs)

</details>



## Purpose and Scope

This page documents how Stakpak manages conversation sessions and configuration profiles. It covers the profile-based configuration system, session persistence and resumption, checkpoint mechanisms, and runtime profile switching. 

For information about CLI initialization and configuration loading, see [Main Entry Point and Configuration](#2.1). For details about how sessions are used within different execution modes, see [Agent Execution Modes](#2.2).

---

## Profile-Based Configuration System

Stakpak uses a profile-based configuration system that allows users to maintain multiple configurations for different environments, providers, or use cases. Profiles are defined in `~/.stakpak/config.toml` and can be selected at runtime.

### Profile Structure

Profiles are defined under the `[profiles]` section in the configuration file. Each profile contains:

| Field | Description | Example |
|-------|-------------|---------|
| `provider` | Backend provider type (`remote` or `local`) | `"remote"` |
| `api_key` | API key for remote provider | `"sk-..."` |
| `api_endpoint` | API endpoint URL | `"https://apiv2.stakpak.dev"` |
| `allowed_tools` | List of permitted tool names | `["view", "create"]` |
| `auto_approve` | Tools that don't require approval | `["view"]` |
| `smart_model` | Model for complex tasks | `"claude-sonnet-4-5"` |
| `eco_model` | Model for simple tasks | `"claude-haiku-4-5"` |
| `rulebooks` | Rulebook filtering configuration | See below |
| `warden` | Security container configuration | See [Warden Guardrails](#6.2) |

Sources: [cli/src/config.rs](), [README.md:143-209]()

### Special "all" Profile

The `all` profile serves as a base configuration that all other profiles inherit from. Settings in the `all` profile apply to every profile unless explicitly overridden.

```toml
[profiles.all]
api_endpoint = "https://apiv2.stakpak.dev"
allowed_tools = ["view", "search_docs", "read_rulebook"]
auto_approve = ["view", "search_docs"]

[profiles.default]
# Inherits settings from 'all' and can override
allowed_tools = ["view", "search_docs", "create", "str_replace"]
```

Sources: [cli/src/commands/mod.rs:499-611]()

### Profile Selection Priority

Profile selection follows this priority order:

```mermaid
graph LR
    CLI["--profile CLI flag"] --> ENV["STAKPAK_PROFILE env var"]
    ENV --> DEFAULT["'default' profile"]
    DEFAULT --> LOAD["Load from config.toml"]
    LOAD --> APPLY["Apply settings"]
```

Sources: [cli/src/main.rs:191-196]()

### Profile Loading Flow

```mermaid
graph TB
    START["main.rs entry"] --> DETERMINE["Determine profile name<br/>(CLI > ENV > 'default')"]
    DETERMINE --> LOAD["AppConfig::load(profile_name, config_path)"]
    LOAD --> VALIDATE{"Profile exists?"}
    VALIDATE -->|No| ONBOARD["run_onboarding()"]
    VALIDATE -->|Yes| MERGE["Merge with 'all' profile"]
    MERGE --> CHECK_WARDEN{"Warden enabled?"}
    CHECK_WARDEN -->|Yes| REEXEC["Re-execute in warden container"]
    CHECK_WARDEN -->|No| CONTINUE["Continue with profile"]
    CONTINUE --> PROVIDER{"provider type?"}
    PROVIDER -->|"remote"| REMOTE["RemoteClient::new()"]
    PROVIDER -->|"local"| LOCAL["LocalClient::new()"]
    REMOTE --> RUN["Run agent"]
    LOCAL --> RUN
```

Sources: [cli/src/main.rs:192-297](), [cli/src/commands/agent/run/mode_interactive.rs:86-190]()

---

## Session Management

Sessions represent conversation threads with persistent message history and state. Sessions are the core unit of conversation continuity in Stakpak.

### Session Structure

Each session contains:

| Component | Description | Storage Location |
|-----------|-------------|------------------|
| Session ID | UUID identifier | Server (remote) or SQLite (local) |
| Messages | Chat message history | In-memory + persisted |
| Tool Calls | Pending and executed tools | In message history |
| Checkpoints | Resumption points | Server (remote) or SQLite (local) |
| Model | AI model used | In-memory |
| Token Usage | Cumulative token counts | In-memory |

Sources: [cli/src/commands/agent/run/mode_interactive.rs:164-190](), [stakpak_api model types]()

### Session Lifecycle in Interactive Mode

```mermaid
graph TB
    INIT["Interactive mode start"] --> CHECK_CHECKPOINT{"--checkpoint flag?"}
    CHECK_CHECKPOINT -->|Yes| LOAD_CHECKPOINT["resume_session_from_checkpoint()"]
    CHECK_CHECKPOINT -->|No| NEW["messages = Vec::new()<br/>current_session_id = None"]
    
    LOAD_CHECKPOINT --> EXTRACT["extract_checkpoint_messages_and_tool_calls()"]
    EXTRACT --> SET_ID["Set current_session_id"]
    EXTRACT --> POPULATE["Populate messages + tools_queue"]
    
    NEW --> WAIT_INPUT["Wait for user input"]
    POPULATE --> WAIT_INPUT
    SET_ID --> WAIT_INPUT
    
    WAIT_INPUT --> USER_MSG["OutputEvent::UserMessage"]
    USER_MSG --> CHAT["client.chat_completion()"]
    CHAT --> RESPONSE["Receive assistant message"]
    RESPONSE --> EXTRACT_CP["extract_checkpoint_id_from_messages()"]
    EXTRACT_CP --> SAVE_ID{"First checkpoint?"}
    SAVE_ID -->|Yes| STORE_ID["current_session_id = checkpoint.session.id"]
    SAVE_ID -->|No| KEEP["Keep existing session_id"]
    STORE_ID --> WAIT_INPUT
    KEEP --> WAIT_INPUT
```

Sources: [cli/src/commands/agent/run/mode_interactive.rs:249-285](), [cli/src/commands/agent/run/mode_interactive.rs:234-243]()

### Session Operations

#### Creating a New Session

A new session is created implicitly when the first message is sent without a checkpoint:

```
OutputEvent::NewSession → clear messages → current_session_id = None
```

Sources: [cli/src/commands/agent/run/mode_interactive.rs:513-524]()

#### Resuming a Session

Sessions can be resumed via checkpoint or session picker:

```mermaid
graph TB
    RESUME["OutputEvent::ResumeSession"] --> HAS_ID{"current_session_id exists?"}
    HAS_ID -->|Yes| USE_ID["Use current_session_id"]
    HAS_ID -->|No| LIST["list_sessions()"]
    LIST --> FIRST["Get first session"]
    USE_ID --> CALL["resume_session_from_checkpoint()"]
    FIRST --> CALL
    CALL --> LOAD["Load checkpoint messages"]
    LOAD --> UPDATE_FLAG["should_update_rulebooks_on_next_message = true"]
    UPDATE_FLAG --> RESET_USAGE["Reset total_session_usage"]
    RESET_USAGE --> EXTEND["messages.extend(chat_messages)"]
    EXTEND --> TOOLS["tools_queue.extend(tool_calls)"]
    TOOLS --> SEND["Send to TUI"]
```

Sources: [cli/src/commands/agent/run/mode_interactive.rs:526-607]()

#### Switching Sessions

The TUI provides a session picker that allows switching between sessions:

```mermaid
graph LR
    PICKER["User opens session picker"] --> LIST["OutputEvent::ListSessions"]
    LIST --> FETCH["client.list_sessions()"]
    FETCH --> DISPLAY["Display in TUI popup"]
    DISPLAY --> SELECT["User selects session"]
    SELECT --> SWITCH["OutputEvent::SwitchToSession(id)"]
    SWITCH --> RESUME["resume_session_from_checkpoint()"]
```

Sources: [cli/src/commands/agent/run/mode_interactive.rs:486-511](), [cli/src/commands/agent/run/mode_interactive.rs:609-668]()

### Session Storage by Provider Type

| Provider | Storage Mechanism | Location | Persistence |
|----------|------------------|----------|-------------|
| `remote` | Stakpak API server | Server-side database | Permanent |
| `local` | SQLite database | `~/.stakpak/store/sessions.db` | Local only |

Sources: [libs/api/src/local/mod.rs](), [libs/api/src/remote/mod.rs]()

---

## Checkpoint System

Checkpoints are resumption points within a session that capture the conversation state at a specific moment. They enable conversation continuity across restarts and mode switches.

### Checkpoint Structure

```mermaid
graph LR
    CHECKPOINT["Checkpoint"] --> ID["checkpoint_id: UUID"]
    CHECKPOINT --> SESSION["session_id: UUID"]
    CHECKPOINT --> MESSAGES["messages: Vec<ChatMessage>"]
    CHECKPOINT --> TIMESTAMP["created_at: DateTime"]
```

Sources: [stakpak_api model types](), [cli/src/commands/agent/run/checkpoint.rs]()

### Checkpoint ID Embedding

Checkpoint IDs are embedded in assistant messages using XML-style tags:

```
<checkpoint_id>550e8400-e29b-41d4-a716-446655440000</checkpoint_id>
```

This allows extraction from message history without separate metadata:

```rust
// Extract checkpoint ID from messages
fn extract_checkpoint_id_from_messages(messages: &[ChatMessage]) -> Option<String>

// Extract from individual message content
trait MessageContent {
    fn extract_checkpoint_id(&self) -> Option<String>
}
```

Sources: [cli/src/commands/agent/run/checkpoint.rs:1-30]()

### Checkpoint Creation and Retrieval Flow

```mermaid
graph TB
    ASSISTANT["Assistant message with checkpoint"] --> PARSE["extract_checkpoint_id_from_messages()"]
    PARSE --> HAS_ID{"Checkpoint ID found?"}
    HAS_ID -->|Yes| FETCH_SESSION{"Need session info?"}
    HAS_ID -->|No| END["No checkpoint"]
    
    FETCH_SESSION -->|Yes| GET_CP["client.get_agent_checkpoint(uuid)"]
    FETCH_SESSION -->|No| CONTINUE["Continue with ID"]
    
    GET_CP --> EXTRACT_SESSION["checkpoint.session.id"]
    EXTRACT_SESSION --> STORE["current_session_id = session.id"]
    STORE --> CONTINUE
    CONTINUE --> EMBED["Embed in message:<br/>&lt;checkpoint_id&gt;...&lt;/checkpoint_id&gt;"]
```

Sources: [cli/src/commands/agent/run/mode_interactive.rs:234-243](), [cli/src/commands/agent/run/checkpoint.rs:46-84]()

### Loading Checkpoint Messages

```mermaid
graph TB
    START["get_checkpoint_messages()"] --> PARSE["Parse checkpoint UUID"]
    PARSE --> FETCH["client.get_agent_checkpoint(uuid)"]
    FETCH --> EXTRACT["checkpoint.messages"]
    EXTRACT --> FILTER["Filter out system messages"]
    FILTER --> RETURN["Return Vec<ChatMessage>"]
    
    RESUME["resume_session_from_checkpoint()"] --> GET["get_checkpoint_messages()"]
    GET --> EXTRACT_TC["extract_checkpoint_messages_and_tool_calls()"]
    EXTRACT_TC --> SPLIT["Split messages and pending tools"]
    SPLIT --> SEND_TUI["send_input_event(InputEvent::*)"]
    SEND_TUI --> RETURN_DATA["Return (messages, tool_calls, session_id)"]
```

Sources: [cli/src/commands/agent/run/checkpoint.rs:86-177]()

### CLI Checkpoint Flag

The `--checkpoint` CLI flag allows resuming from a specific checkpoint:

```bash
stakpak --checkpoint 550e8400-e29b-41d4-a716-446655440000
```

This works in both interactive and async modes:

```mermaid
graph LR
    CLI["--checkpoint flag"] --> PARSE["Parse UUID"]
    PARSE --> MODE{"Execution mode?"}
    MODE -->|Interactive| TUI["Load in TUI startup"]
    MODE -->|Async| BATCH["Load before first message"]
    TUI --> MESSAGES["Populate message history"]
    BATCH --> MESSAGES
```

Sources: [cli/src/main.rs:58-59](), [cli/src/commands/agent/run/mode_interactive.rs:249-285](), [cli/src/commands/agent/run/mode_async.rs:113-142]()

---

## Runtime Profile Switching

The TUI supports switching profiles without restarting the application. This enables quick transitions between different configurations (e.g., from local to remote provider, or between different API keys).

### Profile Switch Flow

```mermaid
graph TB
    USER["User triggers profile switch"] --> REQUEST["OutputEvent::RequestProfileSwitch(profile_name)"]
    REQUEST --> NOTIFY1["InputEvent::ProfileSwitchRequested"]
    NOTIFY1 --> PROGRESS1["InputEvent::ProfileSwitchProgress<br/>'Validating API key...'"]
    
    PROGRESS1 --> VALIDATE["validate_profile_switch()"]
    VALIDATE --> LOAD["AppConfig::load(new_profile)"]
    LOAD --> CHECK_KEY{"API key valid?"}
    
    CHECK_KEY -->|Invalid| FAIL["InputEvent::ProfileSwitchFailed"]
    CHECK_KEY -->|Valid| PROGRESS2["InputEvent::ProfileSwitchProgress<br/>'✓ API key validated'"]
    
    PROGRESS2 --> PROGRESS3["InputEvent::ProfileSwitchProgress<br/>'Shutting down...'"]
    PROGRESS3 --> COMPLETE["InputEvent::ProfileSwitchComplete"]
    COMPLETE --> SHUTDOWN["shutdown_tx.send()"]
    SHUTDOWN --> RETURN["Return (messages, session_id, new_config)"]
    RETURN --> RESTART["Outer loop restarts with new config"]
    
    FAIL --> STAY["Continue with current profile"]
```

Sources: [cli/src/commands/agent/run/mode_interactive.rs:714-779](), [cli/src/commands/agent/run/profile_switch.rs]()

### Profile Switch Outer Loop

The interactive mode runs in an outer loop that enables profile switching:

```rust
'profile_switch_loop: loop {
    // Initialize with current config
    let mut messages: Vec<ChatMessage> = Vec::new();
    let mut current_session_id: Option<Uuid> = None;
    
    // ... run TUI and client tasks ...
    
    // If profile switch requested:
    return Ok((messages, current_session_id, Some(new_config), usage));
    
    // Outer loop receives new config and restarts
}
```

Sources: [cli/src/commands/agent/run/mode_interactive.rs:74-777]()

### Profile Validation

Before switching, the new profile is validated:

```mermaid
graph TB
    VALIDATE["validate_profile_switch()"] --> LOAD["AppConfig::load(profile, path)"]
    LOAD --> INHERIT{"Has api_key?"}
    INHERIT -->|No| USE_DEFAULT["Use default_api_key (from current)"]
    INHERIT -->|Yes| KEEP["Use profile's api_key"]
    
    USE_DEFAULT --> CREATE_CLIENT["Create client with config"]
    KEEP --> CREATE_CLIENT
    
    CREATE_CLIENT --> TEST["client.get_my_account().await"]
    TEST --> CHECK{"API call succeeds?"}
    CHECK -->|No| ERROR["Return Err(validation failed)"]
    CHECK -->|Yes| SUCCESS["Return Ok(new_config)"]
```

Sources: [cli/src/commands/agent/run/profile_switch.rs]()

### TUI Profile Display

The TUI displays the current profile and provides access to the profile switcher:

| UI Element | Location | Function |
|------------|----------|----------|
| Profile indicator | Top status bar | Shows `current_profile_name` |
| Profile switcher | Command palette | Lists available profiles |
| Switch confirmation | Progress messages | Shows validation steps |

Sources: [libs/tui/src/state.rs](), [libs/tui/src/widgets/popup.rs]()

---

## Session and Profile State Management

### State Variables in Interactive Mode

The `run_interactive` function maintains several state variables:

```rust
let mut messages: Vec<ChatMessage> = Vec::new();
let mut current_session_id: Option<Uuid> = None;
let mut should_update_rulebooks_on_next_message = false;
let mut total_session_usage = LLMTokenUsage::default();
```

| Variable | Purpose | Reset On |
|----------|---------|----------|
| `messages` | Conversation history | New session, profile switch |
| `current_session_id` | Active session UUID | New session |
| `should_update_rulebooks_on_next_message` | Flag to re-inject rulebooks | Session resume, rulebook update |
| `total_session_usage` | Token usage accumulator | New session, session resume |

Sources: [cli/src/commands/agent/run/mode_interactive.rs:76-84]()

### Rulebook Re-injection

When resuming a session or switching profiles, rulebooks need to be re-injected on the next user message:

```mermaid
graph LR
    TRIGGER["Resume/Switch event"] --> SET_FLAG["should_update_rulebooks_on_next_message = true"]
    SET_FLAG --> WAIT["Wait for next user message"]
    WAIT --> CHECK{"Flag set?"}
    CHECK -->|Yes| INJECT["add_rulebooks(user_input, rulebooks)"]
    CHECK -->|No| SKIP["Send message as-is"]
    INJECT --> RESET["should_update_rulebooks_on_next_message = false"]
    RESET --> SEND["Send to LLM"]
    SKIP --> SEND
```

Sources: [cli/src/commands/agent/run/mode_interactive.rs:557-558](), [cli/src/commands/agent/run/mode_interactive.rs:312-329]()

### TUI Session State

The TUI maintains session-related state in `AppState`:

```rust
pub struct AppState {
    pub sessions: Vec<Session>,           // Available sessions list
    pub current_profile: String,          // Active profile name
    pub available_profiles: Vec<String>,  // All profiles in config
    // ... other fields
}
```

Sources: [libs/tui/src/state.rs]()

### Session List Loading

```mermaid
graph TB
    REQUEST["OutputEvent::ListSessions"] --> LOADING["InputEvent::StartLoadingOperation<br/>(SessionsList)"]
    LOADING --> FETCH["client.list_sessions().await"]
    FETCH --> SUCCESS{"Success?"}
    SUCCESS -->|Yes| UPDATE["InputEvent::SetSessions(sessions)"]
    SUCCESS -->|No| ERROR["InputEvent::Error(message)"]
    UPDATE --> END_LOAD["InputEvent::EndLoadingOperation"]
    ERROR --> END_LOAD
```

Sources: [cli/src/commands/agent/run/mode_interactive.rs:486-511]()

---

## Configuration Commands

Stakpak provides CLI commands for managing profiles and sessions:

### Profile Management Commands

```bash
# List and select profiles interactively
stakpak config list

# Show current configuration
stakpak config show

# Print sample configuration
stakpak config sample

# Create a new profile
stakpak config new
```

Sources: [cli/src/commands/mod.rs:69-80](), [cli/src/commands/mod.rs:283-358]()

### Profile List Interactive Menu

```mermaid
graph TB
    CMD["stakpak config list"] --> LOAD["AppConfig::list_available_profiles()"]
    LOAD --> MENU["select_profile_interactive()"]
    MENU --> CHOICE{"User selection"}
    CHOICE -->|Existing| SWITCH["re_execute_stakpak_with_profile()"]
    CHOICE -->|CREATE_NEW_PROFILE| NEW["run_onboarding(New mode)"]
    CHOICE -->|Cancel| EXIT["Exit"]
    NEW --> PROMPT["Continue to stakpak?"]
    PROMPT --> SWITCH
    SWITCH --> REEXEC["Execute 'stakpak --profile <name>'"]
```

Sources: [cli/src/commands/mod.rs:285-318](), [cli/src/commands/mod.rs:614-660]()

### Session Storage Locations

| Provider Type | Sessions | Checkpoints | Messages |
|---------------|----------|-------------|----------|
| Remote | API server | API server | API server |
| Local | `~/.stakpak/store/sessions.db` | `~/.stakpak/store/sessions.db` | `.stakpak/session/messages.json` |

Sources: [libs/shared/src/local_store.rs](), [libs/api/src/local/mod.rs]()

---

## Integration with Context Injection

Sessions interact with the context injection pipeline (see [Context Injection Pipeline](#2.3)) in specific ways:

### First Message vs. Subsequent Messages

```mermaid
graph TB
    CHECK["User sends message"] --> EMPTY{"messages.is_empty()?"}
    EMPTY -->|Yes| FIRST["First message in session"]
    EMPTY -->|No| SUBSEQUENT["Subsequent message"]
    
    FIRST --> LOCAL["add_local_context()"]
    FIRST --> RULEBOOKS["add_rulebooks()"]
    FIRST --> SUBAGENTS["add_subagents()"]
    FIRST --> AGENTS_MD["add_agents_md()"]
    
    SUBSEQUENT --> CHECK_FLAG{"should_update_rulebooks?"}
    CHECK_FLAG -->|Yes| LOCAL
    CHECK_FLAG -->|No| PLAIN["Send message as-is"]
    
    LOCAL --> SEND["Send to LLM"]
    RULEBOOKS --> SEND
    SUBAGENTS --> SEND
    AGENTS_MD --> SEND
    PLAIN --> SEND
```

Sources: [cli/src/commands/agent/run/mode_interactive.rs:310-344]()

### Context Re-injection on Resume

When a session is resumed, context is re-injected on the next user message:

1. `resume_session_from_checkpoint()` sets `should_update_rulebooks_on_next_message = true`
2. Next user message triggers context injection
3. Flag is reset after injection

This ensures resumed sessions have up-to-date context (e.g., if rulebook settings changed).

Sources: [cli/src/commands/agent/run/mode_interactive.rs:557-558](), [cli/src/commands/agent/run/mode_interactive.rs:626-627]()

---

## Summary

Session and profile management in Stakpak provides:

1. **Profile System**: Multiple configurations with inheritance, runtime switching, and validation
2. **Session Persistence**: Conversation continuity through checkpoints and message history
3. **Checkpoint Mechanism**: Resume points embedded in messages with UUID-based identification
4. **Provider Flexibility**: Unified interface for remote (API) and local (SQLite) storage
5. **TUI Integration**: Interactive profile/session switching with progress feedback
6. **Context Coordination**: Smart re-injection of context when resuming or switching

The system enables seamless transitions between configurations and conversation threads, supporting workflows that require different tool access levels, providers, or security policies.

Sources: [cli/src/commands/agent/run/mode_interactive.rs](), [cli/src/commands/agent/run/checkpoint.rs](), [cli/src/commands/agent/run/profile_switch.rs](), [cli/src/config.rs](), [cli/src/main.rs]()

---

# Page: Terminal User Interface (TUI)

# Terminal User Interface (TUI)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/stakpak-dark.png](assets/stakpak-dark.png)
- [assets/stakpak-light.png](assets/stakpak-light.png)
- [tui/src/app.rs](tui/src/app.rs)
- [tui/src/lib.rs](tui/src/lib.rs)
- [tui/src/services/update.rs](tui/src/services/update.rs)
- [tui/src/view.rs](tui/src/view.rs)

</details>



The Terminal User Interface (TUI) is the interactive frontend for Stakpak, providing a rich terminal-based interface for conversing with AI agents. Built with `ratatui` and `crossterm`, the TUI is spawned by the CLI in interactive mode and communicates with backend services through bidirectional event channels.

The TUI implements a unidirectional data flow architecture where terminal events are transformed into typed `InputEvent`s, processed through the `update()` dispatcher to modify `AppState`, and rendered via the `view()` function. This separation ensures predictable state transitions and simplifies debugging.

**Key Features:**
- Real-time message streaming with markdown and bash code block rendering
- Interactive approval dialogs for tool calls with bulk approval support
- Command palette and helper dropdown with file search (`@` trigger)
- Shell mode with VT100 terminal emulation for interactive commands
- Profile and rulebook switchers with live configuration updates
- Side panel with context window usage, billing info, file changes, and todos
- Automatic secret detection and long paste handling
- Mouse support (Unix) with scrolling and clickable UI elements

**Related Documentation:** See [CLI Interface](#2) for execution modes and [Agent Provider and API](#4) for backend integration.

## System Position and Communication

The TUI operates as a subprocess of the CLI when running in interactive mode, communicating through `tokio::mpsc` channels for bidirectional event passing.

**TUI Integration in System Architecture**

```mermaid
graph TB
    subgraph CLI["CLI Process (cli/src/main.rs)"]
        MainEntry["main()"]
        ModeInteractive["mode_interactive::run()"]
    end
    
    subgraph TUI["TUI Process (tui/src/lib.rs)"]
        RunTui["run_tui()"]
        EventLoop["Event Loop"]
        AppState["AppState"]
        ViewFunc["view()"]
    end
    
    subgraph Channels["Communication Channels"]
        InputRx["input_rx: Receiver<InputEvent>"]
        OutputTx["output_tx: Sender<OutputEvent>"]
        CancelTx["cancel_tx: broadcast::Sender"]
    end
    
    subgraph Backend["Backend Services"]
        AgentProvider["AgentProvider"]
        MCPClient["MCP Client"]
    end
    
    MainEntry --> ModeInteractive
    ModeInteractive --> RunTui
    ModeInteractive --> InputRx
    ModeInteractive --> OutputTx
    
    RunTui --> EventLoop
    EventLoop --> AppState
    AppState --> ViewFunc
    ViewFunc --> EventLoop
    
    InputRx --> EventLoop
    EventLoop --> OutputTx
    
    ModeInteractive --> AgentProvider
    ModeInteractive --> MCPClient
    OutputTx --> ModeInteractive
```

**Sources:** [tui/src/lib.rs:1-55](), [tui/src/event_loop.rs]()

## Entry Point and Initialization

The `run_tui()` function in [tui/src/lib.rs:11]() is the main entry point, initializing the TUI with configuration and establishing event channels.

| Parameter | Type | Purpose |
|-----------|------|---------|
| `messages` | `Vec<Message>` | Initial conversation history |
| `session_id` | `String` | Current session identifier |
| `input_rx` | `mpsc::Receiver<InputEvent>` | Receives events from CLI/backend |
| `output_tx` | `mpsc::Sender<OutputEvent>` | Sends events to CLI/backend |
| `options` | `AppStateOptions` | Configuration flags and API keys |

The function performs the following initialization sequence:

1. **Terminal Setup** - Creates `TerminalGuard` to manage raw mode, alternate screen, and bracketed paste [tui/src/lib.rs:26-30]()
2. **State Initialization** - Constructs `AppState` with all subsystems [tui/src/app.rs:264-460]()
3. **Channel Setup** - Spawns internal event channel for crossterm events [tui/src/lib.rs:32-40]()
4. **Message Population** - Loads initial messages into state [tui/src/lib.rs:42-48]()
5. **Event Loop Launch** - Starts the main event loop via `event_loop::run()` [tui/src/event_loop.rs]()

**Sources:** [tui/src/lib.rs:1-55](), [tui/src/app.rs:264-460]()

## State Management Architecture

The `AppState` struct [tui/src/app.rs:31-221]() is the single source of truth for all TUI state, organized into 10 logical subsystems with 220+ fields. This structure enables the unidirectional data flow pattern where all state changes flow through the `update()` function.

**AppState Structure and Subsystems**

```mermaid
graph TB
    subgraph AppState["AppState (tui/src/app.rs:31-221)"]
        direction TB
        
        Input["Input & TextArea State<br/>text_area: TextArea<br/>cursor_visible: bool<br/>helpers: Vec<HelperCommand><br/>file_search: FileSearch"]
        
        Messages["Messages & Scrolling State<br/>messages: Vec<Message><br/>scroll: usize<br/>message_lines_cache: Option"]
        
        Loading["Loading State<br/>loading: bool<br/>loading_type: LoadingType<br/>loading_manager: LoadingStateManager"]
        
        Shell["Shell Popup State<br/>shell_popup_visible: bool<br/>active_shell_command: Option<ShellCommand><br/>shell_screen: vt100::Parser"]
        
        Tools["Tool Call State<br/>streaming_tool_results: HashMap<br/>completed_tool_calls: HashSet<br/>session_tool_calls_queue: HashMap"]
        
        Dialogs["Dialog & Approval State<br/>approval_popup: PopupService<br/>show_profile_switcher: bool<br/>show_command_palette: bool"]
        
        Sessions["Sessions Dialog State<br/>sessions: Vec<SessionInfo><br/>show_sessions_dialog: bool<br/>session_selected: usize"]
        
        Config["Configuration State<br/>secret_manager: SecretManager<br/>auto_approve_manager: AutoApproveManager<br/>agent_model: AgentModel"]
        
        SidePanel["Side Panel State<br/>show_side_panel: bool<br/>changeset: Changeset<br/>todos: Vec<TodoItem><br/>billing_info: Option"]
        
        Misc["Misc State<br/>terminal_size: Size<br/>mouse_capture_enabled: bool<br/>pending_editor_open: Option"]
    end
    
    Input -.->|"update()"| Messages
    Messages -.->|"update()"| Loading
    Loading -.->|"update()"| Shell
    Shell -.->|"update()"| Tools
    Tools -.->|"update()"| Dialogs
    Dialogs -.->|"update()"| Sessions
    Sessions -.->|"update()"| Config
    Config -.->|"update()"| SidePanel
    SidePanel -.->|"update()"| Misc
    
    Misc -.->|"view()"| Input
```

**Key State Methods:**

| Method | Location | Purpose |
|--------|----------|---------|
| `AppState::new()` | [tui/src/app.rs:264-460]() | Initialize all subsystems with configuration |
| `poll_file_search_results()` | [tui/src/app.rs:563-597]() | Update file search from async worker |
| `run_shell_command()` | [tui/src/app.rs:502-560]() | Spawn shell command with VT100 emulation |
| `is_input_blocked()` | [tui/src/app.rs:498-500]() | Check if input is disabled (profile switch) |
| `auto_show_side_panel()` | [tui/src/app.rs:598-603]() | Automatically show side panel on first file change |

**State Caching Strategy:**

The TUI implements aggressive caching to avoid expensive recalculations on every frame:

- `message_lines_cache` - Cached wrapped message lines with checksum validation
- `collapsed_message_lines_cache` - Separate cache for collapsed messages view
- `processed_lines_cache` - Pre-processed lines for rendering

Cache invalidation occurs only when messages change or terminal width changes [tui/src/view.rs:252-292]().

**Sources:** [tui/src/app.rs:31-221](), [tui/src/app.rs:264-460](), [tui/src/app.rs:502-603]()

## Event System Architecture

The TUI uses two complementary event enums for bidirectional communication: `InputEvent` for incoming events and `OutputEvent` for outgoing requests to backend services.

**Event Flow and Processing**

```mermaid
graph TB
    subgraph Sources["Event Sources"]
        Crossterm["crossterm::event::read()<br/>(Keyboard/Mouse)"]
        CLIBackend["CLI Backend<br/>(input_rx channel)"]
        Internal["Internal Events<br/>(Timers, async workers)"]
    end
    
    subgraph EventLoop["Event Loop (event_loop.rs)"]
        TokioSelect["tokio::select!"]
        MapEvent["map_crossterm_event_to_input_event()"]
    end
    
    subgraph Processing["Event Processing"]
        InputEnum["InputEvent (90+ variants)<br/>tui/src/app/events.rs"]
        UpdateFunc["update(state, event, output_tx)<br/>tui/src/services/handlers/"]
        Handlers["Specialized Handlers<br/>input.rs, popup.rs, shell.rs<br/>tool.rs, commands.rs"]
    end
    
    subgraph State["State Layer"]
        AppStateM["AppState<br/>(Mutable Reference)"]
    end
    
    subgraph Output["Output Layer"]
        OutputEnum["OutputEvent (20+ variants)<br/>tui/src/app/events.rs"]
        OutputChannel["output_tx.send()"]
    end
    
    Crossterm --> MapEvent
    CLIBackend --> InputEnum
    Internal --> InputEnum
    MapEvent --> InputEnum
    
    TokioSelect --> InputEnum
    InputEnum --> UpdateFunc
    UpdateFunc --> Handlers
    Handlers --> AppStateM
    Handlers --> OutputEnum
    
    OutputEnum --> OutputChannel
```

**InputEvent Categories** (90+ total variants):

| Category | Key Variants | Handler Module |
|----------|-------------|----------------|
| **User Input** | `InputChanged`, `InputSubmitted`, `Paste`, `Char`, `Backspace` | [tui/src/services/handlers/input.rs]() |
| **Navigation** | `CursorLeft/Right`, `ScrollUp/Down`, `PageUp/Down`, `Tab` | [tui/src/services/handlers/input.rs]() |
| **Messages** | `AssistantMessage`, `AssistantMessageChunk`, `ToolResult` | [tui/src/services/handlers/input.rs]() |
| **Shell** | `ShellOutput`, `ShellError`, `ShellCompleted`, `ShellClear` | [tui/src/services/handlers/shell.rs]() |
| **Tool Calls** | `ToolCallsReceived`, `ApproveAllTools`, `RejectTool` | [tui/src/services/handlers/tool.rs]() |
| **Popups** | `ToggleProfileSwitcher`, `ToggleCommandPalette`, `ShowFileChanges` | [tui/src/services/handlers/popup.rs]() |
| **System** | `Loading`, `Resize`, `Quit`, `Error` | [tui/src/services/handlers/input.rs]() |

**OutputEvent Categories** (20+ total variants):

| Category | Key Variants | Purpose |
|----------|-------------|---------|
| **Messages** | `UserMessage`, `UserMessageWithAttachments` | Send user input to agent |
| **Tools** | `AcceptTool`, `RejectTool`, `SendToolResult` | Tool approval and results |
| **Sessions** | `ListSessions`, `SwitchToSession`, `Checkpoint` | Session management |
| **Profiles** | `SwitchProfile`, `ListProfiles` | Profile switching |
| **Rulebooks** | `ListRulebooks`, `UpdateSelectedRulebooks` | Rulebook management |
| **Memory** | `Memorize` | Store information in agent memory |
| **Files** | `GetBackupPath` | File backup operations |

**Sources:** [tui/src/app/events.rs](), [tui/src/services/handlers/](), [tui/src/event.rs:1-300]()

## Event Loop Implementation

The event loop in [tui/src/event_loop.rs]() uses `tokio::select!` to concurrently handle multiple event sources without blocking.

**Event Loop Structure**

```mermaid
graph TB
    subgraph Loop["Main Loop (loop { ... })"]
        Select["tokio::select!"]
    end
    
    subgraph Branch1["Branch 1: External Events"]
        InputRecv["input_rx.recv()"]
        HandleInput["Handle InputEvent"]
    end
    
    subgraph Branch2["Branch 2: Terminal Events"]
        InternalRecv["internal_rx.recv()"]
        CrosstermEvent["crossterm::Event"]
        MapToInput["map_crossterm_event_to_input_event()"]
    end
    
    subgraph Branch3["Branch 3: Timer Events"]
        TimerTick["spinner_interval.tick()"]
        PollFileSearch["state.poll_file_search_results()"]
        IncrementSpinner["state.spinner_frame += 1"]
        BlinkCursor["Update cursor visibility"]
    end
    
    subgraph Processing["Shared Processing"]
        UpdateCall["update(&mut state, event, &output_tx)"]
        ViewCall["terminal.draw(|f| view(f, &mut state))"]
    end
    
    Select --> InputRecv
    Select --> InternalRecv
    Select --> TimerTick
    
    InputRecv --> HandleInput
    InternalRecv --> CrosstermEvent
    CrosstermEvent --> MapToInput
    MapToInput --> HandleInput
    
    TimerTick --> PollFileSearch
    PollFileSearch --> IncrementSpinner
    IncrementSpinner --> BlinkCursor
    
    HandleInput --> UpdateCall
    BlinkCursor --> ViewCall
    UpdateCall --> ViewCall
```

**Event Source Priorities:**

The event loop processes events in this order within each iteration:

1. **External Events** (Highest Priority) - Messages from CLI backend, tool results
2. **Terminal Events** - Keyboard/mouse input from user
3. **Timer Events** (Lowest Priority) - UI updates every 100ms

**Terminal Event Thread:**

Crossterm events are captured in a separate spawned thread that blocks on `crossterm::event::read()` and sends events through an internal channel [tui/src/event_loop.rs]():

```
tokio::spawn(async move {
    loop {
        match crossterm::event::read() {
            Ok(evt) => internal_tx.send(evt).await,
            Err(e) => break,
        }
    }
});
```

This pattern keeps the main event loop non-blocking while handling blocking crossterm I/O.

**Sources:** [tui/src/event_loop.rs](), [tui/src/event.rs:1-300]()

## Rendering Pipeline

The `view()` function [tui/src/view.rs:21-238]() is called on every frame to render the TUI. It uses `ratatui` widgets to compose a complex layout with multiple regions.

**View Layout Structure**

```mermaid
graph TB
    subgraph Frame["Frame (ratatui::Frame)"]
        HorizontalSplit["Horizontal Split"]
    end
    
    subgraph MainArea["Main Area"]
        VerticalLayout["Vertical Layout"]
        Messages["Messages Area<br/>(scrollable)"]
        LoadingLine["Loading Indicator Line<br/>(spinner + tokens)"]
        ShellPopup["Shell Popup<br/>(if visible)"]
        InputArea["Input Area<br/>(TextArea widget)"]
        Dropdown["Helper/File Dropdown<br/>(if active)"]
        Hint["Hint Line<br/>(keyboard shortcuts)"]
    end
    
    subgraph SidePanel["Side Panel (32 chars)"]
        Context["Context Section<br/>(token usage %)"]
        Billing["Billing Section<br/>(credits remaining)"]
        Todos["Todos Section<br/>(task list)"]
        Changes["File Changes Section<br/>(Changeset)"]
    end
    
    subgraph Overlays["Popup Overlays"]
        ApprovalPopup["Approval Popup<br/>(PopupService)"]
        ProfileSwitcher["Profile Switcher"]
        RulebookSwitcher["Rulebook Switcher"]
        CommandPalette["Command Palette"]
        ShortcutsPopup["Shortcuts Popup"]
        FileChangesPopup["File Changes Popup"]
        SessionsDialog["Sessions Dialog"]
    end
    
    Frame --> HorizontalSplit
    HorizontalSplit --> MainArea
    HorizontalSplit --> SidePanel
    
    VerticalLayout --> Messages
    Messages --> LoadingLine
    LoadingLine --> ShellPopup
    ShellPopup --> InputArea
    InputArea --> Dropdown
    Dropdown --> Hint
    
    MainArea -.->|"Rendered last"| Overlays
    SidePanel -.->|"Rendered last"| Overlays
```

**Rendering Functions by Component:**

| Component | Function | Location |
|-----------|----------|----------|
| Messages | `render_messages()` | [tui/src/view.rs:252-292]() |
| Input | `render_multiline_input()` | [tui/src/view.rs:388-420]() |
| Loading | `render_loading_indicator()` | [tui/src/view.rs:422-460]() |
| Shell Popup | `shell_popup::render_shell_popup()` | [tui/src/services/shell_popup.rs]() |
| Side Panel | `side_panel::render_side_panel()` | [tui/src/services/side_panel.rs]() |
| Dropdowns | `render_helper_dropdown()`, `render_file_search_dropdown()` | [tui/src/services/helper_dropdown.rs]() |
| Approval Popup | `PopupService::render()` | [tui/src/services/approval_popup.rs]() |

**Dynamic Layout Calculation:**

The layout adapts to content and active UI elements [tui/src/view.rs:47-112]():

1. Calculate input area height based on text wrapping
2. Determine dropdown height (0 if hidden, variable if showing)
3. Calculate shell popup height (0-80% of screen height)
4. Adjust constraints to hide input when shell popup is expanded

**Sources:** [tui/src/view.rs:21-460](), [tui/src/services/shell_popup.rs](), [tui/src/services/side_panel.rs]()

## Terminal Management

The TUI uses `TerminalGuard` for proper terminal state management and `crossterm` for cross-platform terminal control:

- **Raw Mode** - Enables character-by-character input processing
- **Alternate Screen** - Preserves the user's terminal content
- **Bracketed Paste** - Handles multi-line paste operations securely
- **Resource Cleanup** - Ensures terminal state restoration on exit

**Sources:** [tui/src/lib.rs:29-36](), [tui/src/lib.rs:196-204](), [tui/src/terminal.rs]()

---

# Page: Core Architecture and Event Loop

# Core Architecture and Event Loop

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tui/src/app.rs](tui/src/app.rs)
- [tui/src/lib.rs](tui/src/lib.rs)
- [tui/src/services/update.rs](tui/src/services/update.rs)
- [tui/src/view.rs](tui/src/view.rs)

</details>



This document covers the core architecture and event loop implementation of the TUI system. It focuses on the main async execution flow, channel-based communication, and task orchestration that drives the terminal user interface. For information about state management structures, see [State Management](#3.2). For details about event processing and user input handling, see [Event Handling and User Input](#3.3).

## Architecture Overview

The TUI system is built around an asynchronous event-driven architecture centered on the `run_tui` function. The architecture separates concerns into distinct layers: event capture, event processing, state management, and rendering.

```mermaid
graph TB
    subgraph "Event Sources"
        Crossterm["crossterm::event::read()"]
        ExternalRx["input_rx: Receiver<InputEvent>"]
        TimerTick["spinner_interval.tick()"]
    end
    
    subgraph "Event Processing"
        EventThread["Background Thread"]
        EventMapper["map_crossterm_event_to_input_event()"]
        InternalChannel["internal_tx/internal_rx"]
    end
    
    subgraph "Core Event Loop"
        TokioSelect["tokio::select! macro"]
        MainLoop["Main Event Loop in run_tui()"]
    end
    
    subgraph "State and Services"
        AppState["AppState"]
        UpdateService["services::update::update()"]
        ViewService["view::view()"]
    end
    
    subgraph "Output"
        Terminal["ratatui::Terminal"]
        OutputTx["output_tx: Sender<OutputEvent>"]
    end
    
    Crossterm --> EventThread
    EventThread --> EventMapper
    EventMapper --> InternalChannel
    ExternalRx --> TokioSelect
    InternalChannel --> TokioSelect
    TimerTick --> TokioSelect
    TokioSelect --> MainLoop
    MainLoop --> UpdateService
    UpdateService --> AppState
    AppState --> ViewService
    ViewService --> Terminal
    MainLoop --> OutputTx
```

**Event Loop Architecture**

Sources: [tui/src/lib.rs:20-205](), [tui/src/event.rs:1-97]()

## Channel Communication System

The TUI uses a multi-channel communication system to handle different types of events and maintain separation between synchronous and asynchronous operations.

```mermaid
graph LR
    subgraph "External Communication"
        InputRx["input_rx: Receiver<InputEvent>"]
        OutputTx["output_tx: Sender<OutputEvent>"]
        CancelTx["cancel_tx: broadcast::Sender"]
        ShutdownTx["shutdown_tx: broadcast::Sender"]
    end
    
    subgraph "Internal Communication"
        InternalTx["internal_tx: Sender<InputEvent>"]
        InternalRx["internal_rx: Receiver<InputEvent>"]
        ShellEventTx["shell_event_tx: Sender<InputEvent>"]
    end
    
    subgraph "Event Processing"
        CrosstermThread["Crossterm Reading Thread"]
        MainEventLoop["Main Event Loop"]
        UpdateService["services::update::update()"]
    end
    
    InputRx --> MainEventLoop
    CrosstermThread --> InternalTx
    InternalTx --> InternalRx
    InternalRx --> MainEventLoop
    MainEventLoop --> UpdateService
    UpdateService --> ShellEventTx
    MainEventLoop --> OutputTx
    MainEventLoop --> ShutdownTx
```

**Channel Communication Flow**

| Channel | Type | Purpose |
|---------|------|---------|
| `input_rx` | `Receiver<InputEvent>` | Receives events from external agent system |
| `output_tx` | `Sender<OutputEvent>` | Sends events to external agent system |
| `internal_tx/internal_rx` | `mpsc::channel<InputEvent>` | Internal event communication |
| `shell_event_tx` | `Sender<InputEvent>` | Shell-specific event forwarding |
| `cancel_tx` | `broadcast::Sender<()>` | Tool call cancellation |
| `shutdown_tx` | `broadcast::Sender<()>` | System shutdown coordination |

Sources: [tui/src/lib.rs:53-68](), [tui/src/lib.rs:21-27]()

## Main Event Loop Structure

The core event loop is implemented using `tokio::select!` to handle multiple asynchronous event sources concurrently. The loop processes three main categories of events with different priorities and handling logic.

```mermaid
graph TD
    subgraph "Event Loop Entry"
        RunTui["run_tui() function start"]
        Setup["Terminal Setup & AppState Creation"]
        ThreadSpawn["Spawn crossterm reading thread"]
    end
    
    subgraph "Main Select Loop"
        TokioSelect["tokio::select! block"]
        ExternalEvent["input_rx.recv()"]
        InternalEvent["internal_rx.recv()"]
        SpinnerTick["spinner_interval.tick()"]
    end
    
    subgraph "Event Processing Branches"
        ShellEvents["Shell Event Filtering"]
        ToolCallEvents["Tool Call Confirmation"]
        RegularEvents["Regular Event Processing"]
        QuitCheck["Quit Event Check"]
    end
    
    subgraph "State Updates"
        UpdateCall["services::update::update()"]
        StateUpdate["AppState modification"]
        AutoComplete["state.poll_autocomplete_results()"]
        Render["terminal.draw(view)"]
    end
    
    RunTui --> Setup
    Setup --> ThreadSpawn
    ThreadSpawn --> TokioSelect
    
    TokioSelect --> ExternalEvent
    TokioSelect --> InternalEvent
    TokioSelect --> SpinnerTick
    
    ExternalEvent --> ShellEvents
    ExternalEvent --> ToolCallEvents
    ExternalEvent --> RegularEvents
    ExternalEvent --> QuitCheck
    
    InternalEvent --> RegularEvents
    InternalEvent --> QuitCheck
    
    SpinnerTick --> StateUpdate
    
    ShellEvents --> UpdateCall
    ToolCallEvents --> UpdateCall
    RegularEvents --> UpdateCall
    
    UpdateCall --> StateUpdate
    StateUpdate --> AutoComplete
    AutoComplete --> Render
```

**Main Event Loop Structure**

Sources: [tui/src/lib.rs:76-194]()

## Event Processing Pipeline

The event processing follows a structured pipeline that transforms raw terminal events into application state changes and visual updates.

```mermaid
sequenceDiagram
    participant CT as "Crossterm Thread"
    participant IC as "Internal Channel"
    participant ML as "Main Loop"
    participant UP as "Update Service"
    participant AS as "AppState"
    participant VI as "View System"
    participant TE as "Terminal"

    CT->>CT: "crossterm::event::read()"
    CT->>CT: "map_crossterm_event_to_input_event()"
    CT->>IC: "internal_tx.send(InputEvent)"
    
    ML->>IC: "internal_rx.recv()"
    IC->>ML: "InputEvent"
    
    ML->>ML: "Calculate layout dimensions"
    ML->>UP: "services::update::update()"
    UP->>AS: "Modify state"
    AS->>UP: "State updated"
    UP->>ML: "Update complete"
    
    ML->>AS: "state.poll_autocomplete_results()"
    ML->>VI: "view::view(&state)"
    VI->>TE: "terminal.draw()"
    TE->>ML: "Render complete"
```

**Event Processing Sequence**

The pipeline handles special event types with different flows:

- **Shell Events**: Filtered and forwarded to `shell_event_tx` for shell integration
- **Tool Call Events**: Trigger confirmation dialogs before execution
- **Regular Input Events**: Standard processing through the update service
- **Timer Events**: Update spinner animation and poll autocomplete

Sources: [tui/src/lib.rs:88-106](), [tui/src/lib.rs:174-187]()

## Task Orchestration and Lifecycle

The TUI manages multiple concurrent tasks and coordinates their lifecycle through careful channel management and shutdown coordination.

```mermaid
graph TB
    subgraph "Initialization Phase"
        TerminalSetup["Terminal Configuration"]
        RawMode["crossterm::terminal::enable_raw_mode()"]
        AlternateScreen["EnterAlternateScreen"]
        ChannelSetup["Channel Creation"]
        ThreadSpawn["Background Thread Spawn"]
    end
    
    subgraph "Runtime Phase"
        EventLoop["Main Event Loop"]
        StateManagement["AppState Updates"]
        Rendering["Continuous Rendering"]
        AutoComplete["Autocomplete Polling"]
    end
    
    subgraph "Shutdown Phase"
        QuitDetection["InputEvent::Quit Detection"]
        ShutdownBroadcast["shutdown_tx.send()"]
        TerminalCleanup["Terminal Restoration"]
        RawModeDisable["disable_raw_mode()"]
        LeaveScreen["LeaveAlternateScreen"]
    end
    
    TerminalSetup --> RawMode
    RawMode --> AlternateScreen
    AlternateScreen --> ChannelSetup
    ChannelSetup --> ThreadSpawn
    ThreadSpawn --> EventLoop
    
    EventLoop --> StateManagement
    EventLoop --> Rendering
    EventLoop --> AutoComplete
    
    EventLoop --> QuitDetection
    QuitDetection --> ShutdownBroadcast
    ShutdownBroadcast --> TerminalCleanup
    TerminalCleanup --> RawModeDisable
    RawModeDisable --> LeaveScreen
```

**Task Lifecycle Management**

The system uses several mechanisms for coordinating task lifecycle:

- **Terminal Guard**: `TerminalGuard` RAII pattern ensures terminal cleanup
- **Quit Detection**: Double Ctrl+C handling with timer-based reset
- **Graceful Shutdown**: Broadcast channels coordinate shutdown across components
- **Resource Cleanup**: Proper terminal mode restoration and screen management

Sources: [tui/src/lib.rs:29-36](), [tui/src/lib.rs:196-204](), [tui/src/lib.rs:77-85]()

---

# Page: State Management

# State Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tui/src/app.rs](tui/src/app.rs)
- [tui/src/lib.rs](tui/src/lib.rs)
- [tui/src/services/update.rs](tui/src/services/update.rs)
- [tui/src/view.rs](tui/src/view.rs)

</details>



This document details the state management architecture within the Terminal User Interface (TUI) system. The `AppState` struct serves as the single source of truth, implementing a centralized state container that manages all UI components, user interactions, and system integrations. State updates follow a unidirectional data flow pattern where `InputEvent`s trigger state modifications through the `update` function, and the `view` function renders the UI based on the current state.

For information about the event loop and task orchestration, see [Core Architecture and Event Loop](#3.1). For details on how events are processed and trigger state updates, see [Event Handling and User Input](#3.3).

## AppState Structure and Subsystems

The `AppState` struct defined in [tui/src/app.rs:31-221]() organizes state into 10 major subsystems, each clearly delineated by comments in the source. This organization provides a logical separation of concerns while maintaining all state in a single, accessible structure.

**Major State Subsystems Diagram**

```mermaid
graph TB
    AppState["AppState<br/>(Single Source of Truth)"]
    
    subgraph Input["Input & TextArea State"]
        TextAreaStruct["text_area: TextArea"]
        TextAreaStateStruct["text_area_state: TextAreaState"]
        cursor_visible["cursor_visible: bool"]
        helpers["helpers: Vec<HelperCommand>"]
        file_search["file_search: FileSearch"]
        attached_images["attached_images: Vec<AttachedImage>"]
    end
    
    subgraph Messages["Messages & Scrolling State"]
        messages["messages: Vec<Message>"]
        scroll["scroll: usize"]
        scroll_to_bottom["scroll_to_bottom: bool"]
        message_lines_cache["message_lines_cache: Option<MessageLinesCache>"]
        show_collapsed_messages["show_collapsed_messages: bool"]
    end
    
    subgraph Loading["Loading State"]
        loading["loading: bool"]
        loading_type["loading_type: LoadingType"]
        spinner_frame["spinner_frame: usize"]
        loading_manager["loading_manager: LoadingStateManager"]
    end
    
    subgraph Shell["Shell Popup State"]
        shell_popup_visible["shell_popup_visible: bool"]
        active_shell_command["active_shell_command: Option<ShellCommand>"]
        shell_screen["shell_screen: vt100::Parser"]
        waiting_for_shell_input["waiting_for_shell_input: bool"]
    end
    
    subgraph ToolCalls["Tool Call State"]
        pending_bash_message_id["pending_bash_message_id: Option<Uuid>"]
        streaming_tool_results["streaming_tool_results: HashMap<Uuid, String>"]
        session_tool_calls_queue["session_tool_calls_queue: HashMap<String, ToolCallStatus>"]
        latest_tool_call["latest_tool_call: Option<ToolCall>"]
    end
    
    subgraph Dialogs["Dialog & Approval State"]
        is_dialog_open["is_dialog_open: bool"]
        approval_popup["approval_popup: PopupService"]
        message_tool_calls["message_tool_calls: Option<Vec<ToolCall>>"]
        message_approved_tools["message_approved_tools: Vec<ToolCall>"]
    end
    
    subgraph Sessions["Sessions Dialog State"]
        sessions["sessions: Vec<SessionInfo>"]
        show_sessions_dialog["show_sessions_dialog: bool"]
        session_selected["session_selected: usize"]
    end
    
    subgraph Profiles["Profile Switcher State"]
        show_profile_switcher["show_profile_switcher: bool"]
        available_profiles["available_profiles: Vec<String>"]
        current_profile_name["current_profile_name: String"]
        profile_switching_in_progress["profile_switching_in_progress: bool"]
    end
    
    subgraph Rulebooks["Rulebook Switcher State"]
        show_rulebook_switcher["show_rulebook_switcher: bool"]
        available_rulebooks["available_rulebooks: Vec<ListRuleBook>"]
        selected_rulebooks["selected_rulebooks: HashSet<String>"]
    end
    
    subgraph SidePanel["Side Panel State"]
        show_side_panel["show_side_panel: bool"]
        side_panel_focus["side_panel_focus: SidePanelSection"]
        changeset["changeset: Changeset"]
        todos["todos: Vec<TodoItem>"]
        billing_info["billing_info: Option<BillingResponse>"]
    end
    
    AppState --> Input
    AppState --> Messages
    AppState --> Loading
    AppState --> Shell
    AppState --> ToolCalls
    AppState --> Dialogs
    AppState --> Sessions
    AppState --> Profiles
    AppState --> Rulebooks
    AppState --> SidePanel
```

Sources: [tui/src/app.rs:31-221]()

## State Initialization and Configuration

The `AppState::new()` method in [tui/src/app.rs:264-460]() initializes application state with configuration options provided through `AppStateOptions`. The initialization establishes background services, configures security settings, and sets default values for all state subsystems.

**Initialization Flow Diagram**

```mermaid
graph TD
    new["AppState::new(options)"]
    options["AppStateOptions<br/>Configuration struct"]
    
    subgraph "Configuration Fields"
        latest_version["latest_version: Option<String>"]
        redact_secrets["redact_secrets: bool"]
        privacy_mode["privacy_mode: bool"]
        auto_approve_tools["auto_approve_tools: Option<Vec<String>>"]
        allowed_tools["allowed_tools: Option<Vec<String>>"]
        agent_model["agent_model: AgentModel"]
        editor_command["editor_command: Option<String>"]
    end
    
    subgraph "Background Services"
        helpers["get_helper_commands()"]
        file_search_channels["init_file_search_channels()"]
        file_search_worker["file_search_worker spawn"]
        secret_mgr["SecretManager::new()"]
    end
    
    subgraph "Manager Initialization"
        auto_approve_mgr["AutoApproveManager::new()"]
        loading_mgr["LoadingStateManager::new()"]
        approval_popup_svc["PopupService::new()"]
    end
    
    subgraph "Default State Values"
        text_area_new["TextArea::new()"]
        messages_empty["messages: Vec::new()"]
        shell_parser["vt100::Parser::new()"]
        changeset_new["Changeset::new()"]
    end
    
    new --> options
    options --> latest_version
    options --> redact_secrets
    options --> auto_approve_tools
    options --> agent_model
    
    new --> helpers
    new --> file_search_channels
    file_search_channels --> file_search_worker
    new --> secret_mgr
    new --> auto_approve_mgr
    new --> loading_mgr
    new --> approval_popup_svc
    new --> text_area_new
    new --> messages_empty
    new --> shell_parser
    new --> changeset_new
```

### AppStateOptions Structure

The `AppStateOptions` struct in [tui/src/app.rs:223-235]() defines the configuration parameters passed during initialization:

| Field | Type | Purpose |
|-------|------|---------|
| `latest_version` | `Option<String>` | Latest Stakpak version for update notifications |
| `redact_secrets` | `bool` | Enable secret redaction in output |
| `privacy_mode` | `bool` | Enable privacy mode (redact IPs, account IDs) |
| `is_git_repo` | `bool` | Whether current directory is a git repository |
| `auto_approve_tools` | `Option<&Vec<String>>` | Tools to auto-approve without user confirmation |
| `allowed_tools` | `Option<&Vec<String>>` | Whitelist of allowed tools |
| `input_tx` | `Option<mpsc::Sender<InputEvent>>` | Channel for sending input events |
| `agent_model` | `AgentModel` | LLM model configuration |
| `editor_command` | `Option<String>` | External editor command (vim, nvim, nano) |
| `auth_display_info` | `(Option<String>, Option<String>, Option<String>)` | Auth provider display information |

### Background Service Initialization

The initialization spawns the `file_search_worker` in [tui/src/app.rs:244-262]() to handle asynchronous file and helper command searching. This worker processes search requests through channels and returns filtered results without blocking the main UI thread.

Sources: [tui/src/app.rs:223-235](), [tui/src/app.rs:244-262](), [tui/src/app.rs:264-460]()

## Unidirectional Data Flow Pattern

State modifications follow a strict unidirectional data flow where `InputEvent`s trigger state updates through the `update` function, state changes are reflected in `AppState`, and the `view` function renders the UI based on current state. Some state updates also generate `OutputEvent`s to communicate with the backend.

**State Update Flow Diagram**

```mermaid
graph LR
    InputEvent["InputEvent<br/>(90+ variants)"]
    update["update(state, event)<br/>tui/src/services/update.rs"]
    handlers["Event Handlers<br/>tui/src/services/handlers/"]
    
    subgraph "Handler Modules"
        input_handler["input.rs<br/>Text input, paste"]
        popup_handler["popup.rs<br/>Dialogs, switchers"]
        shell_handler["shell.rs<br/>Shell mode ops"]
        tool_handler["tool.rs<br/>Tool approvals"]
        cmd_handler["commands.rs<br/>Slash commands"]
    end
    
    AppState["AppState<br/>(Modified)"]
    view["view(frame, state)<br/>tui/src/view.rs"]
    output_tx["output_tx<br/>Channel"]
    OutputEvent["OutputEvent<br/>(Backend requests)"]
    
    InputEvent --> update
    update --> handlers
    handlers --> input_handler
    handlers --> popup_handler
    handlers --> shell_handler
    handlers --> tool_handler
    handlers --> cmd_handler
    
    input_handler --> AppState
    popup_handler --> AppState
    shell_handler --> AppState
    tool_handler --> AppState
    cmd_handler --> AppState
    
    tool_handler --> OutputEvent
    cmd_handler --> OutputEvent
    OutputEvent --> output_tx
    
    AppState --> view
```

### The Update Function

The `update` function re-exported from [tui/src/services/update.rs:6]() serves as the central dispatcher for all state modifications. It routes `InputEvent`s to specialized handler modules based on event type and current application state. The update logic is organized into handler modules within `tui/src/services/handlers/` for better maintainability.

### Event Types

The `InputEvent` enum defined in [tui/src/app.rs:1-7]() (via events submodule) contains 90+ variants organized into categories:

| Category | Examples | Handler Module |
|----------|----------|----------------|
| Text Input | `InputChar`, `InputBackspace`, `InputSubmit`, `Paste` | `input.rs` |
| Navigation | `CursorLeft`, `CursorRight`, `ScrollUp`, `ScrollDown` | `input.rs` |
| Popups | `ToggleProfileSwitcher`, `ToggleRulebookSwitcher`, `ToggleCommandPalette` | `popup.rs` |
| Shell | `ShellOutput`, `ShellCompleted`, `ShellWaitingForInput` | `shell.rs` |
| Tool Calls | `RunToolCall`, `ToolResult`, `StreamToolResult`, `ApproveToolCall` | `tool.rs` |
| Commands | Triggered by slash command execution | `commands.rs` |

The `OutputEvent` enum handles communication with the backend layer, requesting operations like sending messages, executing tool calls, or switching sessions.

Sources: [tui/src/services/update.rs:1-7](), [tui/src/app.rs:1-7](), [tui/src/view.rs:1-461]()

## Key State Subsystems

Each state subsystem serves a specific functional area of the application. The following sections detail the most important subsystems and their constituent fields.

### Input & TextArea State

The input subsystem uses the `TextArea` widget for multi-line text editing with cursor management and rendering state tracked separately in `TextAreaState`.

| Field | Type | Purpose |
|-------|------|---------|
| `text_area` | `TextArea` | Multi-line text input widget |
| `text_area_state` | `TextAreaState` | Rendering state for TextArea |
| `cursor_visible` | `bool` | Cursor blink visibility |
| `helpers` | `Vec<HelperCommand>` | Available slash commands |
| `show_helper_dropdown` | `bool` | Show command dropdown |
| `helper_selected` | `usize` | Selected dropdown index |
| `filtered_helpers` | `Vec<HelperCommand>` | Filtered command list |
| `filtered_files` | `Vec<String>` | Filtered file paths for @ completion |
| `file_search` | `FileSearch` | File search state and worker |
| `file_search_tx` | `Option<mpsc::Sender>` | Channel to send search requests |
| `file_search_rx` | `Option<mpsc::Receiver>` | Channel to receive search results |
| `attached_images` | `Vec<AttachedImage>` | Images attached to current message |
| `is_pasting` | `bool` | Paste operation in progress |
| `pasted_long_text` | `Option<String>` | Long text paste buffer |

Sources: [tui/src/app.rs:32-52]()

### Messages & Scrolling State

The message subsystem manages the conversation history with sophisticated caching for performance optimization.

| Field | Type | Purpose |
|-------|------|---------|
| `messages` | `Vec<Message>` | Conversation message history |
| `scroll` | `usize` | Current scroll position in lines |
| `scroll_to_bottom` | `bool` | Trigger to scroll to bottom |
| `stay_at_bottom` | `bool` | Auto-scroll with new content |
| `content_changed_while_scrolled_up` | `bool` | Content updated while user scrolled up |
| `message_lines_cache` | `Option<MessageLinesCache>` | Cached wrapped message lines with checksums |
| `collapsed_message_lines_cache` | `Option<MessageLinesCache>` | Cached collapsed view lines |
| `processed_lines_cache` | `Option<(Vec<Message>, usize, Vec<Line>)>` | Cache for processed message lines |
| `show_collapsed_messages` | `bool` | Display collapsed messages popup |
| `collapsed_messages_scroll` | `usize` | Scroll position in collapsed view |
| `has_user_messages` | `bool` | Whether conversation contains user messages |

Sources: [tui/src/app.rs:54-66]()

### Tool Call State

The tool call subsystem tracks tool execution, streaming results, and queued operations.

| Field | Type | Purpose |
|-------|------|---------|
| `pending_bash_message_id` | `Option<Uuid>` | ID of message awaiting bash output |
| `streaming_tool_results` | `HashMap<Uuid, String>` | Accumulating tool output streams |
| `streaming_tool_result_id` | `Option<Uuid>` | Currently streaming tool result ID |
| `completed_tool_calls` | `HashSet<Uuid>` | Set of completed tool call IDs |
| `is_streaming` | `bool` | LLM response streaming indicator |
| `latest_tool_call` | `Option<ToolCall>` | Most recent tool call |
| `session_tool_calls_queue` | `HashMap<String, ToolCallStatus>` | Queued tool calls by ID |
| `tool_call_execution_order` | `Vec<String>` | Order of tool call execution |
| `last_message_tool_calls` | `Vec<ToolCall>` | Tool calls from last message |

Sources: [tui/src/app.rs:100-134]()

### Shell Popup State

The shell popup subsystem manages interactive shell command execution with VT100 terminal emulation.

| Field | Type | Purpose |
|-------|------|---------|
| `shell_popup_visible` | `bool` | Shell popup visibility |
| `shell_popup_expanded` | `bool` | Shell popup expanded state |
| `shell_popup_scroll` | `usize` | Scroll position in shell output |
| `shell_cursor_visible` | `bool` | Shell cursor blink state |
| `active_shell_command` | `Option<ShellCommand>` | Currently executing command |
| `active_shell_command_output` | `Option<String>` | Accumulated command output |
| `waiting_for_shell_input` | `bool` | Waiting for user input (password) |
| `shell_screen` | `vt100::Parser` | VT100 terminal emulator |
| `shell_scroll` | `u16` | Terminal scroll position |
| `shell_history_lines` | `Vec<Line>` | Accumulated styled shell history |

Sources: [tui/src/app.rs:74-98]()

### Side Panel State

The side panel displays context, changeset, todos, and billing information with collapsible sections.

| Field | Type | Purpose |
|-------|------|---------|
| `show_side_panel` | `bool` | Side panel visibility |
| `side_panel_focus` | `SidePanelSection` | Currently focused section |
| `side_panel_section_collapsed` | `HashMap<SidePanelSection, bool>` | Collapse state per section |
| `side_panel_areas` | `HashMap<SidePanelSection, Rect>` | Screen areas for mouse clicks |
| `session_id` | `String` | Current session ID for backup paths |
| `changeset` | `Changeset` | File changes tracking |
| `todos` | `Vec<TodoItem>` | TODO items extracted from code |
| `billing_info` | `Option<BillingResponse>` | Account billing information |
| `side_panel_auto_shown` | `bool` | Whether panel was auto-shown |

Sources: [tui/src/app.rs:197-220]()

## File Search and Command Completion

The file search subsystem provides asynchronous file and command completion through dedicated channels and a background worker. The `FileSearch` struct maintains search state while the `file_search_worker` handles filtering operations.

**File Search Architecture Diagram**

```mermaid
graph TB
    file_search_tx["file_search_tx<br/>mpsc::Sender<(String, usize)>"]
    file_search_rx_worker["file_search_rx<br/>(in worker)"]
    file_search_worker["file_search_worker<br/>tui/src/services/file_search.rs"]
    result_tx["result_tx<br/>(in worker)"]
    result_rx["file_search_rx<br/>mpsc::Receiver<FileSearchResult><br/>(in AppState)"]
    
    subgraph "AppState Fields"
        file_search["file_search: FileSearch"]
        filtered_helpers["filtered_helpers: Vec<HelperCommand>"]
        filtered_files["filtered_files: Vec<String>"]
        show_helper_dropdown["show_helper_dropdown: bool"]
    end
    
    subgraph "FileSearch Struct"
        is_file_mode["is_file_mode: bool"]
        trigger_char["trigger_char: Option<char>"]
        cached_files["filtered_files: Vec<String>"]
    end
    
    subgraph "Background Worker"
        find_at_trigger["find_at_trigger()"]
        filter_helpers["Filter helper commands"]
        filter_files["Filter file paths"]
    end
    
    file_search_tx --> file_search_rx_worker
    file_search_rx_worker --> file_search_worker
    file_search_worker --> find_at_trigger
    file_search_worker --> filter_helpers
    file_search_worker --> filter_files
    file_search_worker --> result_tx
    result_tx --> result_rx
    result_rx --> filtered_helpers
    result_rx --> filtered_files
    result_rx --> file_search
```

### File Search Worker Initialization

The `init_file_search_channels()` method in [tui/src/app.rs:244-262]() creates bidirectional channels and spawns the background worker:

1. Creates `file_search_tx` to send search requests (query string, cursor position)
2. Creates `result_rx` to receive filtered results
3. Spawns `file_search_worker` from [tui/src/services/file_search.rs]() with helper commands
4. Worker continuously processes requests and sends `FileSearchResult` back

### Polling Results

The `poll_file_search_results()` method in [tui/src/app.rs:563-597]() non-blockingly checks for new results:

```
while let Ok(result) = rx.try_recv() {
    - Update filtered_files
    - Update filtered_helpers
    - Update show_helper_dropdown
    - Reset helper_selected if out of bounds
}
```

This pattern enables responsive completion suggestions without blocking the UI thread.

Sources: [tui/src/app.rs:244-262](), [tui/src/app.rs:563-597](), [tui/src/services/file_search.rs]()

## Shell Command State Lifecycle

Shell command execution maintains state through a lifecycle that manages command spawning, output streaming with VT100 emulation, and completion tracking. The `run_shell_command()` method in [tui/src/app.rs:502-560]() demonstrates this pattern.

**Shell Command Lifecycle Diagram**

```mermaid
graph TD
    run_shell_command["run_shell_command(command, input_tx)"]
    
    subgraph "State Preparation"
        push_messages["Push spacing and command messages"]
        get_terminal_size["Get terminal size (rows, cols)"]
        create_channels["Create shell_tx/shell_rx channels"]
    end
    
    subgraph "Platform-Specific Spawn"
        unix_path["Unix: run_pty_command()<br/>PTY with terminal emulation"]
        windows_path["Windows: run_background_shell_command()<br/>Pipe-based execution"]
    end
    
    subgraph "State Updates"
        set_active_shell_command["active_shell_command = Some(cmd)"]
        set_output["active_shell_command_output = Some(empty)"]
        init_screen["shell_screen = vt100::Parser::new()"]
    end
    
    subgraph "Background Event Loop"
        spawn_task["tokio::spawn async"]
        recv_loop["while shell_rx.recv().await"]
        ShellOutput["ShellEvent::Output -> InputEvent::ShellOutput"]
        ShellError["ShellEvent::Error -> InputEvent::ShellError"]
        ShellCompleted["ShellEvent::Completed -> InputEvent::ShellCompleted"]
        ShellClear["ShellEvent::Clear -> InputEvent::ShellClear"]
    end
    
    run_shell_command --> push_messages
    run_shell_command --> get_terminal_size
    run_shell_command --> create_channels
    
    create_channels --> unix_path
    create_channels --> windows_path
    
    unix_path --> set_active_shell_command
    windows_path --> set_active_shell_command
    
    set_active_shell_command --> set_output
    set_active_shell_command --> init_screen
    set_active_shell_command --> spawn_task
    
    spawn_task --> recv_loop
    recv_loop --> ShellOutput
    recv_loop --> ShellError
    recv_loop --> ShellCompleted
    recv_loop --> ShellClear
```

### Shell State Fields

| Field | Purpose in Lifecycle |
|-------|---------------------|
| `active_shell_command` | Holds `ShellCommand` with process handle |
| `active_shell_command_output` | Accumulates output as it streams |
| `shell_screen` | VT100 parser tracks terminal state (cursor, colors, etc.) |
| `shell_history_lines` | Styled lines for rendering shell history |
| `waiting_for_shell_input` | Set when shell requests password/input |
| `shell_cursor_visible` | Controls cursor blinking in shell popup |

### Event Flow

The background task converts `ShellEvent`s from the command process into `InputEvent`s sent through `input_tx`. These events are then processed by the shell handler module to update state, providing real-time shell output display.

Sources: [tui/src/app.rs:502-560]()

## Security and Privacy State

The `secret_manager` field integrates security functionality directly into the application state, enabling secret detection and redaction throughout the TUI lifecycle. The `SecretManager` is configured during initialization with privacy and redaction settings.

| Security State Field | Type | Purpose |
|---------------------|------|---------|
| `secret_manager` | `SecretManager` | Handles secret detection and redaction |
| `ctrl_c_pressed_once` | `bool` | Tracks quit sequence state |
| `ctrl_c_timer` | `Option<std::time::Instant>` | Times quit confirmation window |

The security state is initialized in the `new()` method with configuration parameters for `redact_secrets` and `privacy_mode`, ensuring consistent security policy enforcement across all state operations.

Sources: [tui/src/app.rs:86](), [tui/src/app.rs:224]()

---

# Page: Event Handling and User Input

# Event Handling and User Input

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tui/src/app.rs](tui/src/app.rs)
- [tui/src/app/events.rs](tui/src/app/events.rs)
- [tui/src/lib.rs](tui/src/lib.rs)
- [tui/src/services/commands.rs](tui/src/services/commands.rs)
- [tui/src/services/handlers/input.rs](tui/src/services/handlers/input.rs)
- [tui/src/services/handlers/mod.rs](tui/src/services/handlers/mod.rs)
- [tui/src/services/handlers/popup.rs](tui/src/services/handlers/popup.rs)
- [tui/src/services/update.rs](tui/src/services/update.rs)
- [tui/src/view.rs](tui/src/view.rs)

</details>



This page documents the event handling system in the TUI, which transforms terminal events (keyboard, mouse, paste) into strongly-typed application events, routes them to specialized handler modules, and updates the application state. The event system follows a unidirectional data flow pattern where all state changes occur through the central `update` function.

For information about the event loop that drives this system, see [Core Architecture and Event Loop](#3.1). For information about how state changes affect the UI, see [Rendering System](#3.4).

## Event System Architecture

The TUI's event system uses two primary event types defined in [tui/src/app/events.rs:1-158]():

- **`InputEvent`**: Events that trigger state changes (90+ variants)
- **`OutputEvent`**: Requests to backend services (13 variants)

### Event Flow Pattern

```mermaid
graph TB
    Terminal["Terminal Events<br/>(Crossterm)"]
    Transform["map_crossterm_event_to_input_event<br/>[event.rs]"]
    InputEvent["InputEvent<br/>[app/events.rs:12-135]"]
    Channel["input_tx: mpsc::Sender<InputEvent>"]
    EventLoop["Event Loop<br/>[event_loop.rs]"]
    BlockCheck{"is_input_blocked()?<br/>[app.rs:498-500]"}
    PopupCheck{"Popup/Dialog<br/>Visible?"}
    UpdateDispatcher["update()<br/>[handlers/mod.rs:29-610]"]
    Handlers["Handler Modules"]
    StateUpdate["AppState Mutation"]
    OutputChannel["output_tx: mpsc::Sender<OutputEvent>"]
    Backend["Backend Services<br/>(CLI/Agent)"]
    
    Terminal --> Transform
    Transform --> InputEvent
    InputEvent --> Channel
    Channel --> EventLoop
    EventLoop --> BlockCheck
    BlockCheck -->|"Blocked"| Discard["Discard<br/>(except profile events)"]
    BlockCheck -->|"Not Blocked"| PopupCheck
    PopupCheck -->|"Yes"| InterceptHandler["Popup-specific<br/>Handler"]
    PopupCheck -->|"No"| UpdateDispatcher
    UpdateDispatcher --> Handlers
    Handlers --> StateUpdate
    Handlers --> OutputChannel
    OutputChannel --> Backend
    InterceptHandler --> StateUpdate
```

**Event Flow Sequence:**

1. Terminal captures raw input via Crossterm library
2. `map_crossterm_event_to_input_event` transforms to `InputEvent`
3. Event sent through `input_tx` channel
4. Event loop receives and checks if input is blocked
5. If not blocked, routes to `update()` dispatcher
6. `update()` routes to appropriate handler module
7. Handler mutates `AppState` and optionally emits `OutputEvent`

**Sources:** [tui/src/app/events.rs:1-158](), [tui/src/event.rs](), [tui/src/services/handlers/mod.rs:29-610]()

### InputEvent Enum Structure

The `InputEvent` enum contains 90+ variants organized into functional categories:

| Category | Example Variants | Purpose |
|----------|------------------|---------|
| Text Input | `InputChanged(char)`, `InputBackspace`, `HandlePaste(String)` | Character and text entry |
| Cursor Control | `CursorLeft`, `CursorRight`, `InputCursorStart`, `InputCursorEnd` | Text navigation |
| Submission | `InputSubmitted`, `InputSubmittedWith(String)` | Message submission |
| Navigation | `ScrollUp`, `ScrollDown`, `PageUp`, `PageDown`, `Up`, `Down` | UI navigation |
| Dialog | `ShowConfirmationDialog(ToolCall)`, `ToggleDialogFocus`, `HandleEsc` | Tool approval dialogs |
| Shell | `ShellMode`, `RunShellCommand(String)`, `ShellOutput(String)` | Interactive shell |
| Tool Execution | `RunToolCall(ToolCall)`, `ToolResult(ToolCallResult)`, `StreamToolResult(ToolCallResultProgress)` | Tool call handling |
| Popups | `ShowProfileSwitcher`, `ShowRulebookSwitcher`, `ShowCommandPalette` | Various popups |
| Profile Management | `ProfileSwitchRequested(String)`, `ProfileSwitchComplete(String)` | Profile switching |
| Messages | `StreamAssistantMessage(Uuid, String)`, `AddUserMessage(String)` | Message handling |
| System | `Quit`, `Resized(u16, u16)`, `Error(String)` | System events |

**Sources:** [tui/src/app/events.rs:12-135]()

### OutputEvent Enum

`OutputEvent` represents requests to backend services (CLI/Agent layer):

```rust
pub enum OutputEvent {
    UserMessage(String, Option<Vec<ToolCallResult>>, Vec<ContentPart>),
    AcceptTool(ToolCall),
    RejectTool(ToolCall, bool),
    ListSessions,
    SwitchToSession(String),
    NewSession,
    Memorize,
    SendToolResult(ToolCallResult, bool, Vec<ToolCall>),
    ResumeSession,
    RequestProfileSwitch(String),
    RequestRulebookUpdate(Vec<String>),
    RequestCurrentRulebooks,
    RequestTotalUsage,
    SwitchModel(AgentModel),
}
```

These events are sent via `output_tx` channel and processed by the CLI layer to interact with the `AgentProvider`.

**Sources:** [tui/src/app/events.rs:137-157]()

## Event Transformation Pipeline

### Crossterm to InputEvent Mapping

Raw terminal events are transformed into typed `InputEvent` variants by `map_crossterm_event_to_input_event` in [tui/src/event.rs]():

```mermaid
graph LR
    CrosstermEvent["crossterm::event::Event"]
    Key["Event::Key"]
    Mouse["Event::Mouse"]
    Paste["Event::Paste"]
    Resize["Event::Resize"]
    
    InputChanged["InputEvent::InputChanged(c)"]
    InputBackspace["InputEvent::InputBackspace"]
    InputSubmitted["InputEvent::InputSubmitted"]
    CursorLeft["InputEvent::CursorLeft"]
    ScrollUp["InputEvent::ScrollUp"]
    HandlePaste["InputEvent::HandlePaste(text)"]
    Resized["InputEvent::Resized(w, h)"]
    MouseClick["InputEvent::MouseClick(col, row)"]
    
    CrosstermEvent --> Key
    CrosstermEvent --> Mouse
    CrosstermEvent --> Paste
    CrosstermEvent --> Resize
    
    Key --> InputChanged
    Key --> InputBackspace
    Key --> InputSubmitted
    Key --> CursorLeft
    Key --> ScrollUp
    Mouse --> MouseClick
    Paste --> HandlePaste
    Resize --> Resized
```

**Key Bindings Examples:**
- `Char('c')` → `InputEvent::InputChanged('c')`
- `Backspace` → `InputEvent::InputBackspace`
- `Enter` → `InputEvent::InputSubmitted`
- `Ctrl+'c'` → `InputEvent::AttemptQuit`
- `Ctrl+'p'` → `InputEvent::ShowProfileSwitcher`
- `Ctrl+'k'` → `InputEvent::ShowRulebookSwitcher`
- `Esc` → `InputEvent::HandleEsc`

**Sources:** [tui/src/event.rs](), [tui/src/lib.rs:18]()

### Input Blocking and Filtering

Before events reach the dispatcher, several filtering layers apply:

```mermaid
graph TB
    InputEvent["InputEvent Received"]
    BlockCheck{"is_input_blocked()?<br/>[app.rs:498-500]"}
    AllowedEvent{"Profile/Quit<br/>Event?"}
    FileChangesCheck{"show_file_changes_popup?"}
    ShellCheck{"show_shell_mode &&<br/>active_shell_command?"}
    UpdateDispatcher["update() Dispatcher"]
    
    InputEvent --> BlockCheck
    BlockCheck -->|"true"| AllowedEvent
    AllowedEvent -->|"Yes"| UpdateDispatcher
    AllowedEvent -->|"No"| Discard["Discard Event"]
    BlockCheck -->|"false"| FileChangesCheck
    FileChangesCheck -->|"true"| FileChangesHandler["File Changes<br/>Popup Handler"]
    FileChangesCheck -->|"false"| ShellCheck
    ShellCheck -->|"true"| ShellInterceptor["Shell Input<br/>Interceptor"]
    ShellCheck -->|"false"| UpdateDispatcher
```

**Blocking Logic** [tui/src/services/handlers/mod.rs:40-59]():

When `profile_switching_in_progress` is `true`, all input is blocked except:
- `ProfilesLoaded`, `ProfileSwitchRequested`, `ProfileSwitchProgress`, `ProfileSwitchComplete`, `ProfileSwitchFailed`
- `RulebooksLoaded`, `CurrentRulebooksLoaded`
- `Quit`, `AttemptQuit`

This prevents user input corruption during profile transitions.

**Sources:** [tui/src/services/handlers/mod.rs:40-59](), [tui/src/app.rs:498-500]()

## Update Dispatcher

The `update()` function in [tui/src/services/handlers/mod.rs:29-610]() is the central event dispatcher. It receives an `InputEvent` and routes it to the appropriate handler module.

### Update Function Signature

```rust
pub fn update(
    state: &mut AppState,
    event: InputEvent,
    message_area_height: usize,
    message_area_width: usize,
    input_tx: &Sender<InputEvent>,
    output_tx: &Sender<OutputEvent>,
    cancel_tx: Option<tokio::sync::broadcast::Sender<()>>,
    shell_tx: &Sender<InputEvent>,
    terminal_size: Size,
)
```

**Parameters:**
- `state`: Mutable reference to application state
- `event`: The input event to process
- `message_area_height/width`: For scroll calculations
- `input_tx`: Channel to send new events (for cascading)
- `output_tx`: Channel to send backend requests
- `cancel_tx`: For canceling streaming operations
- `shell_tx`: Dedicated channel for shell events
- `terminal_size`: Current terminal dimensions

**Sources:** [tui/src/services/handlers/mod.rs:29-39]()

### Event Routing Pattern

```mermaid
graph TB
    Update["update()<br/>[handlers/mod.rs:29]"]
    Match["match event"]
    
    InputModule["input::handle_input_changed_event<br/>[handlers/input.rs:23]"]
    NavModule["navigation::handle_up_navigation<br/>[handlers/navigation.rs]"]
    DialogModule["dialog::handle_esc_event<br/>[handlers/dialog.rs]"]
    ToolModule["tool::handle_stream_tool_result<br/>[handlers/tool.rs]"]
    ShellModule["shell::handle_run_shell_command<br/>[handlers/shell.rs]"]
    PopupModule["popup::handle_show_profile_switcher<br/>[handlers/popup.rs]"]
    MessageModule["message::handle_stream_message<br/>[handlers/message.rs]"]
    MiscModule["misc::handle_error<br/>[handlers/misc.rs]"]
    
    Update --> Match
    Match -->|"InputChanged(c)"| InputModule
    Match -->|"Up/Down/ScrollUp"| NavModule
    Match -->|"HandleEsc"| DialogModule
    Match -->|"StreamToolResult"| ToolModule
    Match -->|"RunShellCommand"| ShellModule
    Match -->|"ShowProfileSwitcher"| PopupModule
    Match -->|"StreamAssistantMessage"| MessageModule
    Match -->|"Error/Resized"| MiscModule
```

**Routing Examples** [tui/src/services/handlers/mod.rs:237-607]():

```
InputEvent::InputChanged(c) → input::handle_input_changed_event()
InputEvent::InputBackspace → input::handle_input_backspace_event()
InputEvent::InputSubmitted → input::handle_input_submitted_event()
InputEvent::Up → navigation::handle_up_navigation()
InputEvent::HandleEsc → dialog::handle_esc_event()
InputEvent::RunShellCommand(cmd) → shell::handle_run_shell_command()
InputEvent::ShowProfileSwitcher → popup::handle_show_profile_switcher()
InputEvent::StreamToolResult(progress) → tool::handle_stream_tool_result()
```

**Sources:** [tui/src/services/handlers/mod.rs:237-607]()

## Handler Modules

Handler modules are organized by functionality in [tui/src/services/handlers/]():

```mermaid
graph TB
    HandlersDir["handlers/"]
    
    ModFile["mod.rs<br/>update() dispatcher"]
    InputFile["input.rs<br/>Text input & paste"]
    NavFile["navigation.rs<br/>Scrolling & cursor"]
    DialogFile["dialog.rs<br/>Tool approval dialogs"]
    ToolFile["tool.rs<br/>Tool execution"]
    ShellFile["shell.rs<br/>Shell mode"]
    PopupFile["popup.rs<br/>Popups & switchers"]
    MessageFile["message.rs<br/>Message stream"]
    MiscFile["misc.rs<br/>System events"]
    
    HandlersDir --> ModFile
    HandlersDir --> InputFile
    HandlersDir --> NavFile
    HandlersDir --> DialogFile
    HandlersDir --> ToolFile
    HandlersDir --> ShellFile
    HandlersDir --> PopupFile
    HandlersDir --> MessageFile
    HandlersDir --> MiscFile
```

**Sources:** [tui/src/services/handlers/mod.rs:1-14]()

### Input Handler Module

[tui/src/services/handlers/input.rs:1-1175]() handles text input, paste operations, and submission:

**Key Functions:**
- `handle_input_changed_event()` - Routes character input based on popup state
- `handle_input_changed()` - Processes character insertion
- `handle_input_backspace_event()` - Routes backspace based on popup state
- `handle_input_backspace()` - Processes character deletion
- `handle_input_submitted_event()` - Routes submission based on popup state
- `handle_input_submitted()` - Processes message submission
- `handle_paste()` - Processes clipboard paste (text/images)

**Special Features:**
- Secret redaction for pasted content [tui/src/services/handlers/input.rs:792-795]()
- Large paste placeholder generation (>5000 chars) [tui/src/services/handlers/input.rs:799-826]()
- Image path detection and attachment [tui/src/services/handlers/input.rs:845-892]()
- Path conversion for `@` file references [tui/src/services/handlers/input.rs:1011-1048]()

**Sources:** [tui/src/services/handlers/input.rs:1-1175]()

### Navigation Handler Module

[tui/src/services/handlers/navigation.rs]() handles scrolling and cursor movement:

**Functions:**
- `handle_up_navigation()` - Up arrow / scroll up
- `handle_down_navigation()` - Down arrow / scroll down
- `handle_page_up()` - Page up navigation
- `handle_page_down()` - Page down navigation
- `handle_dropdown_up()` - Helper dropdown navigation
- `handle_dropdown_down()` - Helper dropdown navigation
- `adjust_scroll()` - Maintains scroll position consistency

**Sources:** [tui/src/services/handlers/mod.rs:295-319]()

### Dialog Handler Module

[tui/src/services/handlers/dialog.rs]() manages tool approval dialogs:

**Key Functions:**
- `handle_show_confirmation_dialog()` - Shows tool approval dialog
- `handle_toggle_dialog_focus()` - Switches focus between message view and dialog
- `handle_esc_event()` - Handles escape key (cancel/reject)
- `handle_esc()` - Core escape logic with rejection options

**Sources:** [tui/src/services/handlers/mod.rs:320-341]()

### Tool Handler Module

[tui/src/services/handlers/tool.rs]() handles tool call execution and approval:

**Key Functions:**
- `handle_message_tool_calls()` - Processes batch tool call requests
- `handle_stream_tool_result()` - Processes streaming tool output
- `handle_retry_tool_call()` - Retries failed tool calls
- `handle_interactive_stall_detected()` - Handles interactive command stalls
- `handle_approval_popup_toggle_approval()` - Toggle tool approval status
- `execute_command_palette_selection()` - Execute command from palette

**Interactive Stall Detection:**
When a tool call detects an interactive stall (e.g., command waiting for input), it triggers shell mode automatically [tui/src/services/handlers/tool.rs]().

**Sources:** [tui/src/services/handlers/mod.rs:343-373]()

### Shell Handler Module

[tui/src/services/handlers/shell.rs]() manages interactive shell mode:

**Key Functions:**
- `handle_shell_mode()` - Toggles shell mode
- `handle_run_shell_command()` - Executes shell command
- `handle_run_shell_with_command()` - Spawns shell then executes command
- `handle_shell_output()` - Processes shell stdout
- `handle_shell_error()` - Processes shell stderr
- `handle_shell_completed()` - Handles shell completion
- `send_shell_input()` - Sends input to running shell

**Shell Mode Interception:**
When shell mode is active with a running command, input events are intercepted before reaching the main dispatcher [tui/src/services/handlers/mod.rs:113-234]():

```
InputChanged(c) → send_shell_input(c)
InputBackspace → send_shell_input("\x7f")
InputSubmitted → send_shell_input("\n")
CursorLeft → send_shell_input("\x1b[D")
```

**Sources:** [tui/src/services/handlers/mod.rs:375-409](), [tui/src/services/handlers/mod.rs:113-234]()

### Popup Handler Module

[tui/src/services/handlers/popup.rs:1-812]() manages various popup interfaces:

**Profile Switcher:**
- `handle_show_profile_switcher()` - Shows profile selection
- `handle_profile_switcher_select()` - Confirms profile switch
- `handle_profiles_loaded()` - Updates available profiles

**Rulebook Switcher:**
- `handle_show_rulebook_switcher()` - Shows rulebook selection
- `handle_rulebook_switcher_toggle()` - Toggles rulebook selection
- `handle_rulebook_switcher_confirm()` - Confirms rulebook changes

**Command Palette:**
- `handle_show_command_palette()` - Opens command palette
- `handle_command_palette_search_input_changed()` - Filters commands

**File Changes Popup:**
- `handle_show_file_changes_popup()` - Shows modified files
- `handle_file_changes_popup_revert()` - Reverts single file
- `handle_file_changes_popup_revert_all()` - Reverts all changes

**Sources:** [tui/src/services/handlers/popup.rs:1-812]()

### Message Handler Module

[tui/src/services/handlers/message.rs]() handles message streaming and display:

**Functions:**
- `handle_stream_message()` - Appends streaming text to message
- `handle_add_user_message()` - Adds user message to history
- `handle_stream_usage()` - Updates token usage stats
- `handle_total_usage()` - Updates total session usage

**Sources:** [tui/src/services/handlers/mod.rs:505-523]()

### Misc Handler Module

[tui/src/services/handlers/misc.rs]() handles system events:

**Functions:**
- `handle_error()` - Displays error messages
- `handle_resized()` - Updates terminal size
- `handle_toggle_cursor_visible()` - Cursor blinking
- `handle_toggle_auto_approve()` - Auto-approve settings
- `handle_attempt_quit()` - Double Ctrl+C quit logic
- `handle_ctrl_s()` - Save/shortcuts shortcut

**Sources:** [tui/src/services/handlers/mod.rs:525-607]()

## Special Input Modes

### Shell Mode Input Interception

When shell mode is active with a running command, all input is intercepted before reaching the main update dispatcher [tui/src/services/handlers/mod.rs:113-234]():

```mermaid
graph TB
    InputEvent["InputEvent Received"]
    ShellCheck{"show_shell_mode &&<br/>active_shell_command?"}
    InterceptCheck{"Event Type?"}
    
    SendChar["send_shell_input(c.to_string())"]
    SendBackspace["send_shell_input('\\x7f')"]
    SendEnter["send_shell_input('\\n')"]
    SendLeft["send_shell_input('\\x1b[D')"]
    SendUp["send_shell_input('\\x1b[A')"]
    SendTab["send_shell_input('\\t')"]
    SendCtrlC["send_shell_input('\\x03')"]
    
    MainDispatcher["Main update() Dispatcher"]
    Return["Return Early"]
    
    InputEvent --> ShellCheck
    ShellCheck -->|"false"| MainDispatcher
    ShellCheck -->|"true"| InterceptCheck
    
    InterceptCheck -->|"InputChanged(c)"| SendChar
    InterceptCheck -->|"InputBackspace"| SendBackspace
    InterceptCheck -->|"InputSubmitted"| SendEnter
    InterceptCheck -->|"CursorLeft"| SendLeft
    InterceptCheck -->|"Up"| SendUp
    InterceptCheck -->|"Tab"| SendTab
    InterceptCheck -->|"AttemptQuit"| SendCtrlC
    InterceptCheck -->|"HandleEsc"| MainDispatcher
    
    SendChar --> Return
    SendBackspace --> Return
    SendEnter --> Return
```

**Key Implementation:**
The shell interceptor sends VT100 escape sequences directly to the shell's stdin, bypassing normal text input processing. Only `HandleEsc` falls through to terminate the shell.

**Sources:** [tui/src/services/handlers/mod.rs:113-234]()

### Popup Input Interception

When the file changes popup is visible, all input is intercepted [tui/src/services/handlers/mod.rs:65-112]():

```
HandleEsc → handle_file_changes_popup_cancel()
FileChangesRevertAll → handle_file_changes_popup_revert_all()
FileChangesRevertFile → handle_file_changes_popup_revert()
Up/Down → handle_file_changes_popup_navigate()
InputChanged(c) → handle_file_changes_popup_search_input()
InputBackspace → handle_file_changes_popup_backspace()
```

**Other Popup Interceptions:**
- Approval popup visible → consume space bar for toggle [tui/src/services/handlers/input.rs:24-30]()
- Shortcuts popup visible → handle search input [tui/src/services/handlers/input.rs:31-35]()
- Rulebook switcher visible → handle search/toggle [tui/src/services/handlers/input.rs:36-45]()

**Sources:** [tui/src/services/handlers/mod.rs:65-112](), [tui/src/services/handlers/input.rs:23-46]()

### Input Blocking During Profile Switch

When `profile_switching_in_progress` is `true`, the `is_input_blocked()` method returns `true` [tui/src/app.rs:498-500]():

```rust
pub fn is_input_blocked(&self) -> bool {
    self.profile_switching_in_progress
}
```

The update dispatcher checks this and blocks all input except profile-related events [tui/src/services/handlers/mod.rs:40-59]():

```rust
if state.is_input_blocked() {
    match event {
        InputEvent::ProfilesLoaded(_, _)
        | InputEvent::ProfileSwitchRequested(_)
        | InputEvent::ProfileSwitchProgress(_)
        | InputEvent::ProfileSwitchComplete(_)
        | InputEvent::ProfileSwitchFailed(_)
        | InputEvent::RulebooksLoaded(_)
        | InputEvent::CurrentRulebooksLoaded(_)
        | InputEvent::Quit
        | InputEvent::AttemptQuit => {
            // Allow these events through
        }
        _ => {
            return; // Block everything else
        }
    }
}
```

This prevents race conditions during profile transitions.

**Sources:** [tui/src/app.rs:498-500](), [tui/src/services/handlers/mod.rs:40-59]()

## Command System

The TUI implements a unified command system where slash commands can be executed from multiple entry points.

### Command Registry

[tui/src/services/commands.rs:1-949]() defines all commands in a centralized registry:

```mermaid
graph TB
    Registry["Command Registry<br/>[commands.rs:106-193]"]
    
    HelperCommands["HelperCommand Vec<br/>For / dropdown<br/>[commands.rs:196-275]"]
    Commands["Command Vec<br/>For command palette<br/>[commands.rs:106-193]"]
    
    Executor["execute_command()<br/>[commands.rs:296-478]"]
    
    DropdownInput["Slash Command Input<br/>/help, /model, etc"]
    PaletteSelect["Command Palette<br/>Selection"]
    DirectInput["Direct Text Input<br/>/clear, /sessions"]
    
    Registry --> HelperCommands
    Registry --> Commands
    
    DropdownInput --> Executor
    PaletteSelect --> Executor
    DirectInput --> Executor
    
    Executor --> StateUpdate["AppState Mutation"]
    Executor --> OutputEvent["OutputEvent Emission"]
```

**Command Categories:**
- Session management: `/new`, `/sessions`, `/resume`
- Information: `/status`, `/usage`, `/model`
- Utilities: `/clear`, `/help`, `/memorize`, `/summarize`
- Support: `/issue`, `/support`
- Configuration: `/profiles`, `/toggle_auto_approve`, `/mouse_capture`
- Editor: `/editor <path>`

**Sources:** [tui/src/services/commands.rs:106-275]()

### Command Execution Flow

```mermaid
graph TB
    Input["User Types /command"]
    DropdownSelect["Select from Dropdown"]
    PaletteSelect["Select from Palette"]
    
    ParseInput["Parse Input"]
    ExtractID["Extract Command ID"]
    
    Execute["execute_command()<br/>[commands.rs:296]"]
    
    Match["match command_id"]
    
    Help["/help → push_help_message()"]
    Model["/model → switch_model()"]
    Clear["/clear → push_clear_message()"]
    Status["/status → push_status_message()"]
    Sessions["/sessions → OutputEvent::ListSessions"]
    Resume["/resume → resume_session()"]
    New["/new → new_session()"]
    Editor["/editor → open_in_editor()"]
    
    StateUpdate["AppState Mutation"]
    OutputSend["output_tx.send(OutputEvent)"]
    
    Input --> ParseInput
    DropdownSelect --> ExtractID
    PaletteSelect --> ExtractID
    
    ParseInput --> Execute
    ExtractID --> Execute
    
    Execute --> Match
    
    Match --> Help
    Match --> Model
    Match --> Clear
    Match --> Status
    Match --> Sessions
    Match --> Resume
    Match --> New
    Match --> Editor
    
    Help --> StateUpdate
    Model --> StateUpdate
    Model --> OutputSend
    Clear --> StateUpdate
    Status --> StateUpdate
    Sessions --> OutputSend
    Resume --> OutputSend
    New --> OutputSend
    Editor --> StateUpdate
```

**Execution Context:**

Commands receive a `CommandContext` struct [tui/src/services/commands.rs:97-101]():

```rust
pub struct CommandContext<'a> {
    pub state: &'a mut AppState,
    pub input_tx: &'a Sender<InputEvent>,
    pub output_tx: &'a Sender<OutputEvent>,
}
```

This provides access to state mutation, event emission, and backend requests.

**Sources:** [tui/src/services/commands.rs:97-478]()

### Command Palette Integration

The command palette displays commands from `get_all_commands()` [tui/src/services/commands.rs:106-193]():

**Command Structure:**
```rust
pub struct Command {
    pub name: String,        // Display name
    pub description: String, // Description
    pub shortcut: String,    // Keyboard shortcut
    pub action: CommandAction, // Action enum
}
```

**CommandAction Enum:**
```rust
pub enum CommandAction {
    OpenProfileSwitcher,
    OpenRulebookSwitcher,
    OpenSessions,
    OpenShortcuts,
    OpenShellMode,
    ResumeSession,
    ShowStatus,
    MemorizeConversation,
    // ... more actions
}
```

Some actions map to slash commands via `to_command_id()` [tui/src/services/commands.rs:65-83](), while others trigger events directly (e.g., `OpenProfileSwitcher` → `InputEvent::ShowProfileSwitcher`).

**Sources:** [tui/src/services/commands.rs:38-94](), [tui/src/services/commands.rs:106-193]()

---

# Page: Rendering System

# Rendering System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tui/src/app.rs](tui/src/app.rs)
- [tui/src/lib.rs](tui/src/lib.rs)
- [tui/src/services/bash_block.rs](tui/src/services/bash_block.rs)
- [tui/src/services/detect_term.rs](tui/src/services/detect_term.rs)
- [tui/src/services/markdown_renderer.rs](tui/src/services/markdown_renderer.rs)
- [tui/src/services/message.rs](tui/src/services/message.rs)
- [tui/src/services/syntax_highlighter.rs](tui/src/services/syntax_highlighter.rs)
- [tui/src/services/update.rs](tui/src/services/update.rs)
- [tui/src/view.rs](tui/src/view.rs)

</details>



The Rendering System is responsible for transforming the TUI's `AppState` into visual output on the terminal screen. It handles layout calculation, message formatting, text wrapping, caching, and adaptive color rendering across different terminal emulators. This system is built on top of the `ratatui` library and implements a single-pass rendering pipeline that executes on every frame.

For information about state management and how data flows to the rendering system, see [State Management](#3.2). For details on event handling that triggers re-renders, see [Event Handling and User Input](#3.3).

## Overview and Architecture

The rendering system follows a unidirectional data flow pattern where the `view` function reads from `AppState` and produces terminal output without modifying state. The system is optimized for performance through aggressive caching and lazy evaluation of expensive operations like markdown parsing and line wrapping.

### Rendering Flow Diagram

```mermaid
graph TB
    AppState["AppState<br/>(Single Source of Truth)"]
    view["view(frame, state)<br/>tui/src/view.rs:21"]
    
    subgraph "Layout Calculation"
        layout["Layout::default()<br/>Ratatui Layout System"]
        constraints["Constraint Calculation<br/>Dynamic Heights"]
        areas["Area Splitting<br/>Rect Definitions"]
    end
    
    subgraph "Content Rendering"
        messages["render_messages()<br/>view.rs:252"]
        input["render_multiline_input()<br/>view.rs:388"]
        loading["render_loading_indicator()<br/>view.rs:422"]
        shell["shell_popup::render_shell_popup()"]
        popups["Popup Rendering<br/>(approval, profile, etc)"]
        sidepanel["side_panel::render_side_panel()"]
    end
    
    subgraph "Message Processing"
        cache_check["Check message_lines_cache"]
        process["get_processed_message_lines()<br/>message.rs:495"]
        wrap["get_wrapped_message_lines()<br/>message.rs:445"]
        format["Content-Specific Formatting<br/>(markdown, bash, diffs)"]
    end
    
    frame["Ratatui Frame<br/>Terminal Output"]
    
    AppState --> view
    view --> layout
    layout --> constraints
    constraints --> areas
    areas --> messages
    areas --> input
    areas --> loading
    areas --> shell
    areas --> popups
    areas --> sidepanel
    
    messages --> cache_check
    cache_check -->|cache miss| process
    cache_check -->|cache hit| frame
    process --> wrap
    wrap --> format
    format --> frame
    
    input --> frame
    loading --> frame
    shell --> frame
    popups --> frame
    sidepanel --> frame

    style AppState fill:#f9f9f9
    style view fill:#e1f5ff
    style frame fill:#e1ffe1
```

Sources: [tui/src/view.rs:21-238](), [tui/src/services/message.rs:452-524]()

## The View Function

The `view` function in [tui/src/view.rs:21]() is the single entry point for rendering. It is called on every frame (typically 60 FPS) by the event loop and must complete quickly to maintain responsiveness.

### View Function Signature and Flow

```rust
pub fn view(f: &mut Frame, state: &mut AppState)
```

The function performs these operations in sequence:

1. **Calculate horizontal layout** (side panel vs main area)
2. **Calculate vertical layout** (messages, input, popups, hints)
3. **Render messages** with caching
4. **Render shell popup** if visible
5. **Render input area** unless hidden
6. **Render loading indicator**
7. **Render all popups** (rendered last to appear on top)

Sources: [tui/src/view.rs:21-238]()

### Layout Calculation Strategy

The layout system uses `ratatui`'s `Layout` with dynamic constraints that change based on state:

```mermaid
graph TB
    screen["Terminal Screen Area"]
    
    subgraph "Horizontal Split (if side_panel)"
        main["Main Area<br/>(Constraint::Min(1))"]
        side["Side Panel<br/>(Constraint::Length(32))"]
    end
    
    subgraph "Vertical Split (Main Area)"
        msg_area["Message Area<br/>(Constraint::Min(1))"]
        loading_line["Loading Line<br/>(Constraint::Length(1))"]
        dialog_margin["Dialog Margin<br/>(Constraint::Length(2))"]
        dialog["Dialog<br/>(Constraint::Length(11))"]
        shell_popup["Shell Popup<br/>(Constraint::Length(N))"]
        input_box["Input Box<br/>(Constraint::Length(H))"]
        dropdown["Dropdown<br/>(Constraint::Length(D))"]
        hint["Hint Line<br/>(Constraint::Length(1))"]
    end
    
    screen --> main
    screen --> side
    
    main --> msg_area
    main --> loading_line
    main --> dialog_margin
    main --> dialog
    main --> shell_popup
    main --> input_box
    main --> dropdown
    main --> hint
    
    note1["H = calculated from input content<br/>using TextArea::desired_height()"]
    note2["D = 0 if dropdown hidden,<br/>DROPDOWN_MAX_HEIGHT if visible"]
    note3["N = calculated based on<br/>shell_popup_expanded state"]
    
    input_box -.-> note1
    dropdown -.-> note2
    shell_popup -.-> note3
```

Sources: [tui/src/view.rs:22-112]()

### Key Layout Calculations

| Component | Height Calculation | Source |
|-----------|-------------------|--------|
| **Input Area** | `calculate_input_lines(state, width)` using `TextArea::desired_height()` | [view.rs:241-250]() |
| **Dropdown** | `DROPDOWN_MAX_HEIGHT` or compact calculation based on `filtered_helpers.len()` | [view.rs:55-76]() |
| **Shell Popup** | `shell_popup::calculate_popup_height(state, main_area.height)` | [view.rs:87]() |
| **Dialog** | Fixed height of 11 when `show_sessions_dialog` is true | [view.rs:83-84]() |
| **Message Area** | `Constraint::Min(1)` - takes all remaining space | [view.rs:98]() |

Sources: [tui/src/view.rs:48-112]()

## Message Rendering Pipeline

Message rendering is the most complex part of the system, handling multiple content types (markdown, tool calls, bash blocks, diffs) with aggressive caching to maintain 60 FPS performance.

### Message Processing Flow

```mermaid
graph TB
    render_messages["render_messages(frame, state, area, width, height)"]
    
    cache_check{"Check<br/>message_lines_cache"}
    cached_lines["Return cached<br/>processed_lines"]
    
    process["get_processed_message_lines(messages, width)"]
    
    subgraph "Processing Pipeline"
        wrap["get_wrapped_message_lines(messages, width)"]
        
        subgraph "Content Type Routing"
            plain["Plain Text<br/>get_wrapped_plain_lines()"]
            markdown["Markdown<br/>render_markdown_to_lines_with_width()"]
            bash["Bash Blocks<br/>render_bash_block()"]
            diff["File Diffs<br/>render_file_diff()"]
            result["Tool Results<br/>render_result_block()"]
        end
        
        pattern["process_checkpoint_patterns()"]
        spacing["Add SPACING_MARKER Lines"]
    end
    
    visible["Calculate Visible Lines<br/>(scroll + height)"]
    widget["Create Paragraph Widget"]
    render["f.render_widget()"]
    
    render_messages --> cache_check
    cache_check -->|valid| cached_lines
    cache_check -->|invalid| process
    
    process --> wrap
    wrap --> plain
    wrap --> markdown
    wrap --> bash
    wrap --> diff
    wrap --> result
    
    plain --> pattern
    markdown --> pattern
    bash --> pattern
    diff --> pattern
    result --> pattern
    
    pattern --> spacing
    spacing --> cached_lines
    
    cached_lines --> visible
    visible --> widget
    widget --> render

    style cache_check fill:#fff4e1
    style cached_lines fill:#e1ffe1
```

Sources: [tui/src/view.rs:252-292](), [tui/src/services/message.rs:495-524]()

### Message Content Type Handling

The system routes different message types to specialized renderers:

| `MessageContent` Type | Renderer | Output Format |
|----------------------|----------|---------------|
| `Plain(text, style)` | `get_wrapped_plain_lines()` | Styled spans with wrapping |
| `AssistantMD(text, style)` | `render_markdown_to_lines_with_width()` | Parsed markdown with syntax highlighting |
| `RenderPendingBorderBlock(tool_call, is_auto)` | `render_bash_block()` or `render_file_diff()` | Bordered block with tool info |
| `RenderResultBorderBlock(result)` | `render_result_block()` | Bordered block with output |
| `RenderStreamingBorderBlock(...)` | `render_styled_block_ansi_to_tui()` | Live-updating block |
| `Styled(line)` | Direct pass-through | Pre-formatted line |
| `StyledBlock(lines)` | Direct pass-through | Pre-formatted lines |

Sources: [tui/src/services/message.rs:592-891]()

## Caching System

The rendering system implements a multi-level caching strategy to avoid expensive re-computation on every frame.

### Cache Structure

```mermaid
graph TB
    AppState["AppState"]
    
    subgraph "Cache Fields"
        mlc["message_lines_cache<br/>Option&lt;(Vec&lt;Message&gt;, usize, Vec&lt;Line&gt;)&gt;"]
        clc["collapsed_message_lines_cache<br/>Option&lt;(Vec&lt;Message&gt;, usize, Vec&lt;Line&gt;)&gt;"]
        plc["processed_lines_cache<br/>Option&lt;(Vec&lt;Message&gt;, usize, Vec&lt;Line&gt;)&gt;"]
    end
    
    subgraph "Cache Validation"
        check_msgs["Compare message IDs"]
        check_width["Compare width"]
        check_len["Compare message count"]
    end
    
    subgraph "Invalidation Triggers"
        new_msg["New message added"]
        resize["Terminal resize"]
        scroll["User scrolled to bottom<br/>(during streaming)"]
    end
    
    AppState --> mlc
    AppState --> clc
    AppState --> plc
    
    mlc --> check_msgs
    mlc --> check_width
    mlc --> check_len
    
    new_msg --> invalidate["invalidate_message_lines_cache()"]
    resize --> invalidate
    scroll --> invalidate
    
    invalidate --> mlc
    invalidate --> clc

    style mlc fill:#e1f5ff
    style invalidate fill:#ffe1e1
```

Sources: [tui/src/app.rs:60-62](), [tui/src/services/message.rs:527-537]()

### Cache Validation Logic

The `get_wrapped_message_lines_cached()` function validates caches by checking:

1. **Message count**: `cached_messages.len() == messages.len()`
2. **Terminal width**: `cached_width == width`
3. **Message identity**: `cached_messages[i].id == messages[i].id` for all messages

If validation fails, the cache is invalidated and lines are re-computed.

**Smart Invalidation**: During streaming, the cache is NOT invalidated if the user has scrolled up (`!state.stay_at_bottom && state.is_streaming`). This prevents jitter when new chunks arrive while the user is reading old messages.

Sources: [tui/src/services/message.rs:452-492](), [tui/src/services/message.rs:527-537]()

## Content Type Renderers

The system includes specialized renderers for different content types, each producing styled `Line<'static>` vectors.

### Markdown Renderer

The `MarkdownRenderer` in [tui/src/services/markdown_renderer.rs]() parses and renders markdown with:

- **Syntax highlighting** for code blocks using `syntect`
- **Adaptive color schemes** based on terminal capabilities
- **Performance limits**: max 100KB content, 500 lines, 2-second timeout
- **Component support**: headings, lists, tables, code blocks, links, callouts

**Parsing Flow**:

```mermaid
graph LR
    input["Markdown Input"]
    preprocess["preprocess_input()<br/>Clean problematic patterns"]
    parse["parse_markdown()<br/>Split into components"]
    
    subgraph "Component Parsing"
        heading["H1-H6 Headings"]
        code["Code Blocks<br/>(with syntax highlighting)"]
        list["Lists & Tasks"]
        table["Tables"]
        inline["Inline Formatting<br/>(bold, italic, code)"]
    end
    
    render["render_component()<br/>Convert to Line&lt;'static&gt;"]
    lines["Vec&lt;Line&lt;'static&gt;&gt;"]
    
    input --> preprocess
    preprocess --> parse
    parse --> heading
    parse --> code
    parse --> list
    parse --> table
    parse --> inline
    
    heading --> render
    code --> render
    list --> render
    table --> render
    inline --> render
    
    render --> lines
```

Sources: [tui/src/services/markdown_renderer.rs:247-317](), [tui/src/services/markdown_renderer.rs:958-1068]()

### Bash Block Renderer

Tool calls and command outputs are rendered using `render_bash_block()` and related functions:

```mermaid
graph TB
    tool_call["ToolCall or ToolCallResult"]
    
    detect["Detect Tool Type<br/>create_file, edit_file, run_command, etc"]
    
    colors["Assign BubbleColors<br/>Based on tool type"]
    
    subgraph "Content Routing"
        str_replace["str_replace/create<br/>→ render_file_diff()"]
        markdown_file["*.md files (collapsed)<br/>→ render_markdown_block()"]
        command["run_command<br/>→ render_styled_block_ansi_to_tui()"]
        other["Other tools<br/>→ render_result_block()"]
    end
    
    format["Format with Borders<br/>╭────╮<br/>│ content │<br/>╰────╯"]
    
    lines["Vec&lt;Line&lt;'static&gt;&gt;<br/>with SPACING_MARKERs"]
    
    tool_call --> detect
    detect --> colors
    colors --> str_replace
    colors --> markdown_file
    colors --> command
    colors --> other
    
    str_replace --> format
    markdown_file --> format
    command --> format
    other --> format
    
    format --> lines

    style colors fill:#fff4e1
    style format fill:#e1f5ff
```

**Color Mapping**:

| Tool Type | Border Color | Use Case |
|-----------|--------------|----------|
| `create_file` | Green | File creation |
| `edit_file` / `str_replace` | Yellow | File modification |
| `run_command` | Cyan | Command execution |
| `read_file` / `view` | Magenta | File reading |
| `delete_file` / `remove` | Red | File deletion |

Sources: [tui/src/services/bash_block.rs:500-551](), [tui/src/services/bash_block.rs:753-776]()

### ANSI Processing

Terminal output (from commands) is processed to handle ANSI escape codes and terminal control sequences:

1. **Preprocessing**: `preprocess_terminal_output()` handles carriage returns (`\r`), filters empty lines
2. **ANSI parsing**: `ansi_to_tui` crate converts ANSI codes to ratatui `Span` styles
3. **Wrapping**: `wrap_ansi_text()` wraps content while preserving ANSI formatting
4. **Display width**: `calculate_display_width()` accounts for Unicode width (emojis, etc.)

Sources: [tui/src/services/bash_block.rs:56-98](), [tui/src/services/bash_block.rs:143-209]()

## Input Area Rendering

The input area uses a custom `TextArea` widget that supports:

- Multi-line text editing with wrapping
- Cursor positioning and visibility
- Password masking (for shell input)
- Session-empty state detection (for placeholder text)

### TextArea Rendering Flow

```mermaid
graph LR
    state["AppState"]
    text_area["state.text_area<br/>(TextArea instance)"]
    text_area_state["state.text_area_state<br/>(TextAreaState)"]
    
    calc_height["calculate_input_lines()<br/>TextArea::desired_height()"]
    
    layout["Layout with<br/>Constraint::Length(height)"]
    
    block["Block::default()<br/>with borders"]
    
    render_widget["f.render_stateful_widget_ref()<br/>or render_with_state()"]
    
    frame["Frame Buffer"]
    
    state --> text_area
    state --> text_area_state
    text_area --> calc_height
    calc_height --> layout
    layout --> block
    block --> render_widget
    text_area --> render_widget
    text_area_state --> render_widget
    render_widget --> frame
```

**Password Masking**: When `state.waiting_for_shell_input` is true, the `TextArea::render_with_state()` method is called with a mask parameter to hide password characters.

Sources: [tui/src/view.rs:388-420](), [tui/src/view.rs:241-250]()

## Popup Rendering Order

Popups are rendered after all main content to ensure they appear on top. The rendering order (from bottom to top) is:

```mermaid
graph TB
    main["Main Content<br/>(messages, input, loading)"]
    
    sessions["Sessions Dialog<br/>show_sessions_dialog"]
    approval["Approval Popup<br/>approval_popup.is_visible()"]
    profile["Profile Switcher<br/>show_profile_switcher"]
    files["File Changes Popup<br/>show_file_changes_popup"]
    shortcuts["Shortcuts Popup<br/>show_shortcuts_popup"]
    rulebook["Rulebook Switcher<br/>show_rulebook_switcher"]
    overlay["Profile Switch Overlay<br/>profile_switching_in_progress"]
    
    main --> sessions
    sessions --> approval
    approval --> profile
    profile --> files
    files --> shortcuts
    shortcuts --> rulebook
    rulebook --> overlay
    
    overlay --> screen["Screen Output"]

    style main fill:#f9f9f9
    style overlay fill:#ffe1e1
```

This ordering ensures that critical user interactions (like profile switching overlay) are always visible and cannot be obscured by other UI elements.

Sources: [tui/src/view.rs:205-237]()

## Terminal Adaptation

The rendering system adapts to different terminal capabilities using the `detect_term` module.

### Terminal Detection and Color Adaptation

```mermaid
graph TB
    env["Environment Variables<br/>TERM_PROGRAM, COLORTERM, TERM"]
    
    detect["detect_terminal()<br/>Returns TerminalInfo"]
    
    check["is_unsupported_terminal(emulator)"]
    
    decision{"Supports RGB?"}
    
    rgb["RGB Colors<br/>Color::Rgb(r, g, b)"]
    basic["Basic Colors<br/>Color::LightRed, Color::Reset"]
    
    adaptive["AdaptiveColors<br/>Static methods"]
    
    renderer["All Renderers<br/>Use adaptive colors"]
    
    env --> detect
    detect --> check
    check --> decision
    decision -->|Yes| rgb
    decision -->|No| basic
    
    rgb --> adaptive
    basic --> adaptive
    adaptive --> renderer

    style decision fill:#fff4e1
    style adaptive fill:#e1f5ff
```

**Unsupported Terminals**: The system maintains a list of terminals that don't support RGB colors (e.g., `Terminal.app`, `cmd.exe`, `PowerShell`). For these terminals, all colors fall back to basic ANSI colors.

**AdaptiveColors Methods**: The `AdaptiveColors` struct provides methods like `red()`, `green()`, `text()`, `dark_gray()`, etc., which return appropriate colors based on terminal capabilities.

Sources: [tui/src/services/detect_term.rs:21-277](), [tui/src/services/detect_term.rs:280-382]()

## Performance Characteristics

The rendering system is designed for 60 FPS performance with these optimizations:

| Optimization | Technique | Impact |
|--------------|-----------|--------|
| **Message Line Caching** | Store computed `Vec<Line<'static>>` by (messages, width) | Avoids markdown parsing and wrapping on every frame |
| **Smart Cache Invalidation** | Don't invalidate during streaming if user scrolled up | Prevents jitter during live updates |
| **Lazy Markdown Parsing** | Only parse when cache misses | Reduces CPU usage |
| **Pre-allocated Capacity** | `Vec::with_capacity()` for known sizes | Reduces allocations |
| **Timeout Protection** | 2-second limit on markdown parsing | Prevents UI freezing on large content |
| **Content Truncation** | Limit code blocks to 500 lines, markdown to 100KB | Caps worst-case rendering time |
| **Early Returns** | Check formatting needs before parsing | Skips unnecessary work |

The cached `Vec<Line<'static>>` uses owned data to avoid lifetime issues and enables zero-copy rendering when the cache is valid.

Sources: [tui/src/services/message.rs:452-524](), [tui/src/services/markdown_renderer.rs:247-317]()

## Rendering Component Summary

| Component | Renderer Function | Cached? | Layout Constraint |
|-----------|------------------|---------|-------------------|
| **Messages** | `render_messages()` | Yes (multi-level) | `Constraint::Min(1)` |
| **Loading Line** | `render_loading_indicator()` | No | `Constraint::Length(1)` |
| **Input Box** | `render_multiline_input()` | No | `Constraint::Length(H)` |
| **Dropdown** | `render_helper_dropdown()` / `render_file_search_dropdown()` | No | `Constraint::Length(D)` |
| **Hint Line** | `render_hint_or_shortcuts()` | No | `Constraint::Length(1)` |
| **Shell Popup** | `shell_popup::render_shell_popup()` | No | `Constraint::Length(N)` |
| **Side Panel** | `side_panel::render_side_panel()` | No | `Constraint::Length(32)` |
| **Popups** | Various popup renderers | No | Centered overlay |

Sources: [tui/src/view.rs:21-238]()

---

# Page: Message System and Display

# Message System and Display

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tui/src/services/bash_block.rs](tui/src/services/bash_block.rs)
- [tui/src/services/detect_term.rs](tui/src/services/detect_term.rs)
- [tui/src/services/markdown_renderer.rs](tui/src/services/markdown_renderer.rs)
- [tui/src/services/message.rs](tui/src/services/message.rs)
- [tui/src/services/syntax_highlighter.rs](tui/src/services/syntax_highlighter.rs)

</details>



This document describes the TUI's message rendering system, including message types, content processing, text formatting, and display logic. It covers how conversation messages, tool calls, results, markdown, and terminal output are transformed into styled terminal lines.

For information about the event handling and state management that drives message updates, see [Event Handling and User Input](#3.3). For the overall rendering pipeline and layout calculation, see [Rendering System](#3.4).

## Overview

The message system is responsible for converting high-level message content (user text, assistant responses, tool calls, results) into styled terminal lines that can be displayed by Ratatui. The system handles:

- Multiple content types (plain text, markdown, tool calls, results, file diffs)
- Text wrapping with proper Unicode and ANSI code handling
- Adaptive styling based on terminal capabilities
- Performance optimization through line caching
- Special formatting for shell history, code blocks, and tables

**Sources:** [tui/src/services/message.rs:1-50]()

## Message Architecture

### MessageContent Enum

The `MessageContent` enum defines all possible message types that can be displayed in the conversation:

```mermaid
graph TB
    MessageContent["MessageContent Enum"]
    
    MessageContent --> Plain["Plain(String, Style)<br/>Simple styled text"]
    MessageContent --> AssistantMD["AssistantMD(String, Style)<br/>Assistant markdown response"]
    MessageContent --> Styled["Styled(Line)<br/>Single styled line"]
    MessageContent --> StyledBlock["StyledBlock(Vec&lt;Line&gt;)<br/>Pre-rendered lines"]
    MessageContent --> Markdown["Markdown(String)<br/>Rendered markdown"]
    MessageContent --> PlainText["PlainText(String)<br/>Unformatted text"]
    MessageContent --> PendingBorder["RenderPendingBorderBlock<br/>Tool awaiting execution"]
    MessageContent --> PendingStall["RenderPendingBorderBlockWithStallWarning<br/>Tool with timeout warning"]
    MessageContent --> StreamingBorder["RenderStreamingBorderBlock<br/>Tool call in progress"]
    MessageContent --> ResultBorder["RenderResultBorderBlock<br/>Tool execution result"]
    MessageContent --> Collapsed["RenderCollapsedMessage<br/>Minimized tool display"]
    MessageContent --> EscapedText["RenderEscapedTextBlock<br/>Plain text content"]
    MessageContent --> BashBubble["BashBubble<br/>Shell command display"]
    MessageContent --> RefreshedTerminal["RenderRefreshedTerminal<br/>Terminal state snapshot"]
```

**Sources:** [tui/src/services/message.rs:27-52]()

### Message Struct

Each `Message` contains an ID, content variant, and optional collapse state:

| Field | Type | Purpose |
|-------|------|---------|
| `id` | `Uuid` | Unique identifier for cache invalidation |
| `content` | `MessageContent` | The actual content variant |
| `is_collapsed` | `Option<bool>` | Whether message is shown in collapsed view |

**Sources:** [tui/src/services/message.rs:115-120]()

## Message Processing Pipeline

### Entry Points and Caching

The message processing pipeline starts from two main entry points:

```mermaid
graph TB
    subgraph "Cache Layer"
        CacheCheck{"Cache Valid?"}
        Cache["message_lines_cache<br/>(Vec&lt;Message&gt;, width, Vec&lt;Line&gt;)"]
        CollapsedCache["collapsed_message_lines_cache<br/>(Vec&lt;Message&gt;, width, Vec&lt;Line&gt;)"]
    end
    
    subgraph "Processing Functions"
        GetCached["get_wrapped_message_lines_cached<br/>Main messages with caching"]
        GetCollapsed["get_wrapped_collapsed_message_lines_cached<br/>Collapsed messages only"]
        GetProcessed["get_processed_message_lines<br/>Heavy processing"]
        GetWrapped["get_wrapped_message_lines<br/>Content wrapping"]
        GetInternal["get_wrapped_message_lines_internal<br/>Core logic"]
    end
    
    subgraph "Rendering"
        ViewFunction["view() function<br/>UI rendering"]
    end
    
    ViewFunction --> GetCached
    ViewFunction --> GetCollapsed
    
    GetCached --> CacheCheck
    GetCollapsed --> CacheCheck
    
    CacheCheck -->|Invalid| GetProcessed
    CacheCheck -->|Valid| Cache
    
    GetProcessed --> GetWrapped
    GetWrapped --> GetInternal
    
    GetProcessed --> Cache
    GetInternal --> CollapsedCache
```

**Sources:** [tui/src/services/message.rs:452-492](), [tui/src/services/message.rs:539-590]()

### Cache Invalidation Strategy

The cache is invalidated selectively to prevent UI jitter during streaming:

```mermaid
graph LR
    Invalidate["invalidate_message_lines_cache()"]
    
    Check{"User scrolled up<br/>AND streaming?"}
    
    Invalidate --> Check
    Check -->|Yes| Skip["Skip invalidation<br/>Prevents jitter"]
    Check -->|No| Clear["state.message_lines_cache = None<br/>state.collapsed_message_lines_cache = None"]
```

**Sources:** [tui/src/services/message.rs:528-537]()

### Content Type Routing

The `get_wrapped_message_lines_internal` function routes each message content type to its specialized renderer:

| MessageContent Variant | Rendering Function | Output |
|------------------------|-------------------|---------|
| `AssistantMD` | `render_markdown_to_lines_with_width` | Styled markdown lines |
| `Plain` | `get_wrapped_plain_lines` | Wrapped text with shell history detection |
| `Styled` | `get_wrapped_styled_lines` | Direct pass-through |
| `StyledBlock` | `get_wrapped_styled_block_lines` | Direct pass-through |
| `RenderPendingBorderBlock` | `render_bash_block` or `render_file_diff` | Bordered tool call |
| `RenderStreamingBorderBlock` | `render_styled_block` | Streaming tool output |
| `RenderResultBorderBlock` | `render_result_block` | Tool execution result |
| `RenderCollapsedMessage` | `render_file_diff_full` | Expanded diff view |
| `RenderEscapedTextBlock` | `format_text_content` | Plain formatted text |
| `Markdown` | `get_wrapped_markdown_lines` | Rendered markdown |
| `PlainText` | Direct span creation | Single line |
| `BashBubble` | `get_wrapped_bash_bubble_lines` | Shell command bubble |
| `RenderRefreshedTerminal` | `render_refreshed_terminal_bubble` | Terminal snapshot |

**Sources:** [tui/src/services/message.rs:592-906]()

## Content Rendering Systems

### Bordered Block Rendering

Tool calls and results are rendered with Unicode box-drawing characters. The rendering pipeline for bordered blocks:

```mermaid
graph TB
    subgraph "Input Processing"
        ToolCall["ToolCall or<br/>ToolCallResult"]
        ExtractInfo["extract_bash_block_info()<br/>Extract command, colors"]
        DetermineType{"Tool Type?"}
    end
    
    subgraph "Rendering Functions"
        RenderBash["render_bash_block()<br/>Command preview"]
        RenderDiff["render_file_diff()<br/>Inline diff"]
        RenderResult["render_result_block()<br/>Execution output"]
        RenderFull["render_file_diff_full()<br/>Full diff with header"]
    end
    
    subgraph "Core Renderer"
        RenderStyled["render_styled_block_ansi_to_tui()<br/>ANSI-aware block"]
        WrapANSI["wrap_ansi_text()<br/>Width-aware wrapping"]
        Preprocess["preprocess_terminal_output()<br/>Clean control sequences"]
    end
    
    subgraph "Output"
        Lines["Vec&lt;Line&lt;'static&gt;&gt;<br/>Bordered, styled lines"]
    end
    
    ToolCall --> ExtractInfo
    ExtractInfo --> DetermineType
    
    DetermineType -->|str_replace/create| RenderDiff
    DetermineType -->|Other tools| RenderBash
    DetermineType -->|Result| RenderResult
    DetermineType -->|Collapsed| RenderFull
    
    RenderBash --> RenderStyled
    RenderResult --> RenderStyled
    
    RenderStyled --> Preprocess
    Preprocess --> WrapANSI
    WrapANSI --> Lines
```

**Sources:** [tui/src/services/bash_block.rs:212-409](), [tui/src/services/bash_block.rs:753-776]()

### BubbleColors System

Each tool type has a distinct color scheme defined by `BubbleColors`:

```rust
// Example from extract_bash_block_info
match tool_name {
    "create_file" => BubbleColors {
        border_color: Color::Green,
        title_color: Color::Gray,
        content_color: Color::LightGreen,
    },
    "edit_file" => BubbleColors {
        border_color: Color::Yellow,
        ...
    },
    "run_command" => BubbleColors {
        border_color: Color::Cyan,
        ...
    },
    ...
}
```

**Sources:** [tui/src/services/bash_block.rs:500-551](), [tui/src/services/message.rs:18-24]()

### Border Block Structure

The structure of a rendered bordered block:

```
╭─ Title (truncated if needed) ───────────────╮
│  Indented content with proper wrapping     │
│  Multiple lines preserved                  │
│  ANSI colors maintained                    │
╰────────────────────────────────────────────╯
```

The title border calculation handles Unicode width correctly:

**Sources:** [tui/src/services/bash_block.rs:243-271]()

## Terminal Output Processing

### ANSI Code Handling

Terminal output often contains ANSI escape sequences. The processing pipeline:

```mermaid
graph TB
    RawOutput["Raw Terminal Output<br/>with ANSI codes, \\r, \\n, etc"]
    
    Preprocess["preprocess_terminal_output()<br/>Handle carriage returns<br/>Filter empty lines"]
    
    StripANSI["strip_all_ansi()<br/>Remove ANSI sequences<br/>Two-pass cleaning"]
    
    IntoText["ansi_to_tui::IntoText<br/>Parse ANSI to Ratatui"]
    
    WrapANSI["wrap_ansi_text()<br/>Preserve styles while wrapping"]
    
    CalcWidth["calculate_display_width()<br/>Unicode-aware width"]
    
    Output["Styled, wrapped lines<br/>ready for display"]
    
    RawOutput --> Preprocess
    Preprocess --> StripANSI
    StripANSI --> IntoText
    IntoText --> WrapANSI
    WrapANSI --> CalcWidth
    CalcWidth --> Output
```

**Sources:** [tui/src/services/bash_block.rs:35-55](), [tui/src/services/bash_block.rs:57-98]()

### Carriage Return Processing

Carriage returns (`\r`) in terminal output simulate overwriting:

```rust
// From preprocess_terminal_output
for ch in text.chars() {
    match ch {
        '\r' => {
            // Carriage return - start overwriting the current line
            current_line.clear();
        }
        '\n' => {
            // Newline - finish the current line and start a new one
            lines.push(current_line.clone());
            current_line.clear();
        }
        '\t' => {
            current_line.push_str("    ");
        }
        _ => {
            current_line.push(ch);
        }
    }
}
```

**Sources:** [tui/src/services/bash_block.rs:57-98]()

### Unicode Width Calculation

Text wrapping must account for Unicode character widths (1 or 2 display columns):

```mermaid
graph LR
    Text["Input Text"]
    
    CalcDisplay["calculate_display_width()<br/>Strip ANSI, count Unicode width"]
    
    WrapSimple["wrap_text_simple_unicode()<br/>Character-by-character wrapping"]
    
    WrapANSI["wrap_ansi_text()<br/>Span-by-span wrapping"]
    
    Width["Display Width"]
    
    Text --> CalcDisplay
    CalcDisplay --> Width
    
    Text --> WrapSimple
    Text --> WrapANSI
    
    WrapSimple --> Width
    WrapANSI --> Width
```

**Sources:** [tui/src/services/bash_block.rs:100-105](), [tui/src/services/bash_block.rs:108-140]()

## Markdown Rendering

### Parsing Pipeline

The `MarkdownRenderer` parses markdown into components, then renders them to styled lines:

```mermaid
graph TB
    Input["Markdown String"]
    
    Preprocess["preprocess_input()<br/>Fix badges, normalize"]
    
    ParseMD["parse_markdown()<br/>Component extraction"]
    
    subgraph "Components"
        H1["H1-H6<br/>Headings"]
        Bold["Bold, Italic<br/>Inline styles"]
        Code["Code, CodeBlock<br/>Syntax highlighting"]
        List["Lists, Tables<br/>Structured content"]
        Link["Links, Images<br/>References"]
        Quote["Quotes, Callouts<br/>Special blocks"]
    end
    
    RenderLines["render_to_lines()<br/>Component to Line conversion"]
    
    Output["Vec&lt;Line&lt;'static&gt;&gt;"]
    
    Input --> Preprocess
    Preprocess --> ParseMD
    
    ParseMD --> H1
    ParseMD --> Bold
    ParseMD --> Code
    ParseMD --> List
    ParseMD --> Link
    ParseMD --> Quote
    
    H1 --> RenderLines
    Bold --> RenderLines
    Code --> RenderLines
    List --> RenderLines
    Link --> RenderLines
    Quote --> RenderLines
    
    RenderLines --> Output
```

**Sources:** [tui/src/services/markdown_renderer.rs:227-317](), [tui/src/services/markdown_renderer.rs:1031-1053]()

### MarkdownComponent Types

The parser recognizes these component types:

| Component | Pattern | Example |
|-----------|---------|---------|
| `H1` - `H6` | `# text` | `## Section Title` |
| `Bold` | `**text**` | `**important**` |
| `Italic` | `*text*` | `*emphasis*` |
| `Code` | `` `code` `` | `` `variable` `` |
| `CodeBlock` | ` ```lang` | ` ```python` |
| `Link` | `[text](url)` | `[docs](https://...)` |
| `Image` | `![alt](url)` | `![logo](img.png)` |
| `ListItem` | `- text` or `1. text` | `- Item one` |
| `Quote` | `> text` | `> Note: ...` |
| `Table` | `\| col \| col \|` | Markdown tables |
| `TaskOpen` | `- [ ] text` | `- [ ] Todo` |
| `TaskComplete` | `- [x] text` | `- [x] Done` |
| `HorizontalSeparator` | `---` or `***` | `---` |

**Sources:** [tui/src/services/markdown_renderer.rs:12-60]()

### Syntax Highlighting

Code blocks with language tags are syntax-highlighted using `syntect`:

```mermaid
graph LR
    CodeBlock["CodeBlock<br/>{language, content}"]
    
    Detect["Detect language<br/>from extension"]
    
    Highlight["apply_syntax_highlighting()<br/>syntect library"]
    
    Convert["syntect_color_to_ratatui_color()<br/>RGB or fallback"]
    
    StyledLines["Vec&lt;Line&gt;<br/>with syntax colors"]
    
    CodeBlock --> Detect
    Detect --> Highlight
    Highlight --> Convert
    Convert --> StyledLines
```

**Sources:** [tui/src/services/syntax_highlighter.rs:20-56]()

### MarkdownStyle Configuration

Markdown components are styled with `MarkdownStyle`, which adapts to terminal capabilities:

```rust
impl MarkdownStyle {
    pub fn adaptive() -> Self {
        if should_use_rgb_colors() {
            Self::dark_theme()  // RGB colors
        } else {
            Self::high_contrast_theme()  // Standard colors
        }
    }
}
```

**Sources:** [tui/src/services/markdown_renderer.rs:92-225]()

## File Diff Rendering

### Diff Extraction

File diffs for `str_replace` and `create` tool calls are rendered with visual indicators:

```mermaid
graph TB
    ToolCall["ToolCall<br/>(str_replace or create)"]
    
    ParseArgs["Parse arguments<br/>path, old_str, new_str"]
    
    BuildDiff["Build unified diff<br/>similar crate"]
    
    ProcessLines["Process diff lines"]
    
    AddedLine["+  Added line<br/>(Green background)"]
    RemovedLine["-  Removed line<br/>(Red background)"]
    ContextLine["   Context line<br/>(Normal)"]
    
    RenderFull["render_file_diff_full()<br/>With header"]
    RenderInline["render_file_diff()<br/>Inline in message"]
    
    Output["Bordered diff block"]
    
    ToolCall --> ParseArgs
    ParseArgs --> BuildDiff
    BuildDiff --> ProcessLines
    
    ProcessLines --> AddedLine
    ProcessLines --> RemovedLine
    ProcessLines --> ContextLine
    
    AddedLine --> RenderFull
    RemovedLine --> RenderFull
    ContextLine --> RenderFull
    
    AddedLine --> RenderInline
    RemovedLine --> RenderInline
    ContextLine --> RenderInline
    
    RenderFull --> Output
    RenderInline --> Output
```

**Sources:** [tui/src/services/file_diff.rs]() (referenced in bash_block.rs), [tui/src/services/bash_block.rs:681-751]()

### Diff Line Styling

Diff lines are color-coded:

- **Green background** (`dark_green`): Added lines with `+` prefix
- **Red background** (`dark_red`): Removed lines with `-` prefix
- **Normal**: Context lines

**Sources:** [tui/src/services/bash_block.rs:681-715]()

## Adaptive Color System

### Terminal Detection

The system detects terminal capabilities and adjusts colors accordingly:

```mermaid
graph TB
    DetectTerm["detect_terminal()<br/>Check env vars, parent process"]
    
    CheckSupport{"supports_rgb_colors?"}
    
    Unsupported["Terminal.app<br/>Terminus<br/>cmd.exe<br/>PowerShell<br/>etc."]
    
    Supported["iTerm2<br/>Alacritty<br/>Kitty<br/>VS Code<br/>etc."]
    
    UseRGB["Use RGB colors<br/>Color::Rgb(r, g, b)"]
    
    UseFallback["Use standard colors<br/>Color::LightRed, etc."]
    
    AdaptiveColors["AdaptiveColors::<br/>red(), green(), text(), etc."]
    
    DetectTerm --> CheckSupport
    CheckSupport -->|Yes| Supported
    CheckSupport -->|No| Unsupported
    
    Supported --> UseRGB
    Unsupported --> UseFallback
    
    UseRGB --> AdaptiveColors
    UseFallback --> AdaptiveColors
```

**Sources:** [tui/src/services/detect_term.rs:22-277]()

### AdaptiveColors Methods

The `AdaptiveColors` struct provides terminal-aware color constants:

| Method | RGB Value (if supported) | Fallback |
|--------|--------------------------|----------|
| `red()` | `Rgb(239, 100, 97)` | `LightRed` |
| `green()` | `Rgb(35, 218, 111)` | `LightGreen` |
| `text()` | `Rgb(180, 180, 180)` | `Reset` |
| `dark_gray()` | `Rgb(80, 80, 80)` | `DarkGray` |
| `dark_green()` | `Rgb(44, 51, 35)` | `Green` |
| `dark_red()` | `Rgb(51, 36, 35)` | `Red` |
| `code_bg()` | `Rgb(48, 48, 48)` | `Reset` |
| `code_block_bg()` | `Rgb(30, 30, 30)` | `Reset` |
| `list_bullet()` | `Rgb(180, 180, 180)` | `Gray` |

**Sources:** [tui/src/services/detect_term.rs:280-382]()

## Shell History Rendering

### Detection and Parsing

Plain text messages containing shell history are detected and rendered as bubbles:

```mermaid
graph TB
    PlainText["Plain text message<br/>contains 'Here's my shell history:'"]
    
    FindShell["Find ```shell blocks"]
    
    ParseLines["Parse lines<br/>Look for SHELL_PROMPT_PREFIX"]
    
    ExtractCmd["Extract command<br/>(starts with prefix)"]
    
    ExtractOut["Extract output<br/>(other lines)"]
    
    RenderBubble["render_shell_bubble_with_unicode_border()<br/>Create bordered display"]
    
    Output["Magenta-bordered<br/>command + output bubble"]
    
    PlainText --> FindShell
    FindShell --> ParseLines
    ParseLines --> ExtractCmd
    ParseLines --> ExtractOut
    
    ExtractCmd --> RenderBubble
    ExtractOut --> RenderBubble
    
    RenderBubble --> Output
```

**Sources:** [tui/src/services/message.rs:672-722](), [tui/src/services/message.rs:342-426]()

## Result Block Rendering

### Compact vs Bordered Display

Result blocks have two rendering modes based on whether the tool is collapsed:

```mermaid
graph TB
    Result["ToolCallResult"]
    
    CheckCollapsed{"is_collapsed_tool_call<br/>AND result.lines > 3?"}
    
    CollapsedMode["Collapsed Mode<br/>No borders<br/>Dot indicator<br/>Indented content"]
    
    BorderedMode["Bordered Mode<br/>Top/bottom borders<br/>Header with title<br/>Bordered content lines"]
    
    CheckMarkdown{"Result contains .md<br/>AND collapsed?"}
    
    RenderMD["render_markdown_block()<br/>Specialized markdown display"]
    
    RenderStandard["render_result_block()<br/>Standard result formatting"]
    
    Output["Formatted result lines"]
    
    Result --> CheckCollapsed
    CheckCollapsed -->|Yes| CollapsedMode
    CheckCollapsed -->|No| BorderedMode
    
    CollapsedMode --> CheckMarkdown
    CheckMarkdown -->|Yes| RenderMD
    CheckMarkdown -->|No| RenderStandard
    
    BorderedMode --> RenderStandard
    
    RenderMD --> Output
    RenderStandard --> Output
```

**Sources:** [tui/src/services/bash_block.rs:808-1092](), [tui/src/services/bash_block.rs:778-806]()

### Result Block Structure

A standard result block with borders:

```
╭──────────────────────────────────────────────╮
│ ● Title (command path = value)               │
│  Content line 1                              │
│  Content line 2                              │
│  ...                                         │
╰──────────────────────────────────────────────╯
```

A collapsed result block (no borders):

```
● Title (command path = value)
  Content line 1
  Content line 2
  ...
```

**Sources:** [tui/src/services/bash_block.rs:844-1036]()

## Performance Considerations

### Caching Strategy

The message system implements a two-level cache:

1. **Main cache** (`message_lines_cache`): All non-collapsed messages
2. **Collapsed cache** (`collapsed_message_lines_cache`): Only collapsed messages

Cache keys include:
- Message list (by ID)
- Terminal width
- Pre-rendered lines

**Sources:** [tui/src/services/message.rs:467-491](), [tui/src/services/message.rs:551-576]()

### Processing Limits

To prevent performance issues and hangs:

| Limit | Value | Purpose |
|-------|-------|---------|
| Max markdown size | 100KB | Prevent DoS from large content |
| Max markdown lines | 500 | Prevent infinite processing |
| Markdown timeout | 2 seconds | Keep UI responsive |
| Max code lines | 500 | Limit code block size |
| Max quote lines | 50 | Limit quote block size |
| Max table rows | 100 | Limit table size |
| Max output lines | 5000 | Prevent memory issues |

**Sources:** [tui/src/services/markdown_renderer.rs:260-262](), [tui/src/services/markdown_renderer.rs:271-276](), [tui/src/services/markdown_renderer.rs:516-526]()

### Line Wrapping Optimization

Text wrapping uses an efficient character-by-character approach with Unicode width calculation:

```rust
// From wrap_text_simple_unicode
for ch in stripped.chars() {
    let char_width = unicode_width::UnicodeWidthChar::width(ch).unwrap_or(1);
    
    if current_width + char_width > width && !current_line.is_empty() {
        lines.push(current_line.clone());
        current_line.clear();
        current_width = 0;
    }
    
    current_line.push(ch);
    current_width += char_width;
}
```

**Sources:** [tui/src/services/bash_block.rs:108-140]()

## Special Content Processing

### Markdown Delimiter Stripping

When resuming sessions, assistant messages may contain markdown code block delimiters that need to be stripped:

```rust
// From strip_markdown_delimiters
// Only process if this looks like a markdown code block
if !result.contains("```markdown") && !result.contains("```md") {
    return result; // Return unchanged
}

// Remove opening delimiter and any leading newline
// Remove closing delimiter and any trailing newline
```

**Sources:** [tui/src/services/message.rs:63-113]()

### Local Context and Rulebook Stripping

User messages may contain injected context that should not be displayed:

```rust
// Strip local_context blocks
while let Some(start) = cleaned.find("<local_context>") {
    if let Some(end) = cleaned[start..].find("</local_context>") {
        cleaned.replace_range(start..end_pos, "");
    }
}

// Strip rulebooks blocks
while let Some(start) = cleaned.find("<rulebooks>") {
    if let Some(end) = cleaned[start..].find("</rulebooks>") {
        cleaned.replace_range(start..end_pos, "");
    }
}
```

**Sources:** [tui/src/services/message.rs:652-670]()

### Checkpoint Pattern Processing

Checkpoint IDs in messages are detected and formatted specially:

```rust
// From get_processed_message_lines
if line_text.contains("<checkpoint_id>") {
    processed_lines.push(Line::from(""));
    let processed = process_checkpoint_patterns(&[(line.clone(), Style::default())], width);
    for (processed_line, _) in processed {
        processed_lines.push(processed_line);
    }
    processed_lines.push(Line::from(""));
}
```

**Sources:** [tui/src/services/message.rs:506-513]()

---

# Page: Interactive Components

# Interactive Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tui/src/app/events.rs](tui/src/app/events.rs)
- [tui/src/services/commands.rs](tui/src/services/commands.rs)
- [tui/src/services/handlers/input.rs](tui/src/services/handlers/input.rs)
- [tui/src/services/handlers/mod.rs](tui/src/services/handlers/mod.rs)
- [tui/src/services/handlers/popup.rs](tui/src/services/handlers/popup.rs)
- [tui/src/services/hint_helper.rs](tui/src/services/hint_helper.rs)

</details>



This document details the interactive popups, dialogs, and contextual assistance systems in the TUI. These components provide profile switching, rulebook management, command discovery, tool approval workflows, file change tracking, and contextual hints.

For core TUI architecture and event handling, see [Core Architecture and Event Loop](#3.1) and [Event Handling and User Input](#3.3). For shell integration, see [Shell Mode Integration](#3.7).

## Component Overview

The TUI implements several interactive components that overlay the main interface:

```mermaid
graph TB
    subgraph "Popup Systems"
        ProfileSwitcher["Profile Switcher<br/>show_profile_switcher"]
        RulebookSwitcher["Rulebook Switcher<br/>show_rulebook_switcher"]
        ShortcutsPopup["Shortcuts/Commands Popup<br/>show_shortcuts_popup"]
        ApprovalPopup["Approval Popup<br/>approval_popup: PopupService"]
        FileChangesPopup["File Changes Popup<br/>show_file_changes_popup"]
    end
    
    subgraph "Non-Modal Components"
        SidePanel["Side Panel<br/>show_side_panel"]
        HintSystem["Hint System<br/>render_hint_or_shortcuts()"]
    end
    
    subgraph "Event Handlers"
        PopupHandlers["handlers/popup.rs<br/>Profile/Rulebook/Command handlers"]
        InputHandlers["handlers/input.rs<br/>Input routing for popups"]
        ToolHandlers["handlers/tool.rs<br/>Approval popup handlers"]
    end
    
    subgraph "State Management"
        ProfileState["available_profiles<br/>profile_switcher_selected"]
        RulebookState["available_rulebooks<br/>selected_rulebooks"]
        CommandState["command_palette_search<br/>shortcuts_popup_mode"]
        ApprovalState["approval_popup<br/>message_tool_calls"]
        FileChangesState["changeset<br/>file_changes_selected"]
    end
    
    PopupHandlers --> ProfileSwitcher
    PopupHandlers --> RulebookSwitcher
    PopupHandlers --> ShortcutsPopup
    PopupHandlers --> FileChangesPopup
    ToolHandlers --> ApprovalPopup
    InputHandlers --> ProfileSwitcher
    InputHandlers --> RulebookSwitcher
    
    ProfileSwitcher --> ProfileState
    RulebookSwitcher --> RulebookState
    ShortcutsPopup --> CommandState
    ApprovalPopup --> ApprovalState
    FileChangesPopup --> FileChangesState
    SidePanel --> FileChangesState
```

**Interactive Components Architecture**
The TUI's popup and interactive systems with their handlers and state management.

Sources: [tui/src/services/handlers/popup.rs:1-812](), [tui/src/app/events.rs:1-158](), [tui/src/services/hint_helper.rs:1-213]()
</thinking>

## Profile Switcher

The profile switcher allows users to switch between configured profiles (API keys, models, settings):

```mermaid
graph TB
    subgraph "Trigger Events"
        CtrlF["Ctrl+F<br/>ShowProfileSwitcher"]
        SlashProfiles["/profiles command"]
    end
    
    subgraph "Profile Switcher Workflow"
        LoadProfiles["OutputEvent::RequestProfileSwitch<br/>Load available_profiles"]
        ShowPopup["show_profile_switcher = true<br/>Pre-select current profile"]
        Navigate["Up/Down<br/>profile_switcher_selected"]
        SelectProfile["Enter<br/>ProfileSwitcherSelect"]
    end
    
    subgraph "Profile Switch Process"
        RequestSwitch["OutputEvent::RequestProfileSwitch(profile)"]
        ProfileSwitchRequested["InputEvent::ProfileSwitchRequested"]
        ProfileSwitchProgress["InputEvent::ProfileSwitchProgress"]
        ProfileSwitchComplete["InputEvent::ProfileSwitchComplete"]
        ProfileSwitchFailed["InputEvent::ProfileSwitchFailed"]
    end
    
    subgraph "State Updates"
        BlockInput["profile_switching_in_progress = true"]
        ClearState["Clear messages, tools, shell state"]
        UpdateProfile["current_profile_name = profile"]
        ShowWelcome["Display welcome messages"]
    end
    
    CtrlF --> ShowPopup
    SlashProfiles --> ShowPopup
    ShowPopup --> Navigate
    Navigate --> SelectProfile
    SelectProfile --> RequestSwitch
    
    RequestSwitch --> ProfileSwitchRequested
    ProfileSwitchRequested --> BlockInput
    BlockInput --> ProfileSwitchProgress
    ProfileSwitchProgress --> ProfileSwitchComplete
    ProfileSwitchProgress --> ProfileSwitchFailed
    
    ProfileSwitchComplete --> ClearState
    ClearState --> UpdateProfile
    UpdateProfile --> ShowWelcome
```

**Profile Switcher Workflow**
From trigger to completion, showing state blocking during switch.

| Handler Function | Purpose | Location |
|-----------------|---------|----------|
| `handle_show_profile_switcher` | Display profile list, pre-select current | [tui/src/services/handlers/popup.rs:45-66]() |
| `handle_profile_switcher_select` | Initiate profile switch | [tui/src/services/handlers/popup.rs:68-87]() |
| `handle_profile_switch_requested` | Block input, show progress | [tui/src/services/handlers/popup.rs:106-119]() |
| `handle_profile_switch_complete` | Clear state, update profile | [tui/src/services/handlers/popup.rs:128-192]() |
| `handle_profile_switch_failed` | Show error, unblock input | [tui/src/services/handlers/popup.rs:195-208]() |

**State Fields**:
- `show_profile_switcher: bool` - Popup visibility
- `available_profiles: Vec<String>` - Loaded profile names
- `profile_switcher_selected: usize` - Current selection index
- `profile_switching_in_progress: bool` - Blocks all input during switch
- `current_profile_name: String` - Active profile name

The profile switcher prevents interaction with other dialogs during the switch process by checking `profile_switching_in_progress` in event handlers [tui/src/services/handlers/popup.rs:48-51]().

Sources: [tui/src/services/handlers/popup.rs:43-208](), [tui/src/app/events.rs:92-97]()

## Rulebook Switcher

The rulebook switcher provides multi-select functionality for activating rulebooks (SOPs, policies, context):

```mermaid
graph TB
    subgraph "Trigger"
        CtrlK["Ctrl+K<br/>ShowRulebookSwitcher"]
    end
    
    subgraph "Initialization"
        LoadRulebooks["OutputEvent::RequestCurrentRulebooks<br/>Load available_rulebooks"]
        ShowPopup["show_rulebook_switcher = true"]
        LoadCurrent["CurrentRulebooksLoaded<br/>Pre-select active rulebooks"]
    end
    
    subgraph "Search & Filter"
        SearchInput["RulebookSearchInputChanged(c)<br/>rulebook_search_input"]
        FilterRulebooks["filter_rulebooks()<br/>URI, description, tags"]
        UpdateFiltered["filtered_rulebooks<br/>Reset selection if needed"]
    end
    
    subgraph "Selection Management"
        Navigate["Up/Down<br/>rulebook_switcher_selected"]
        ToggleItem["Space<br/>RulebookSwitcherToggle"]
        SelectAll["Ctrl+A<br/>RulebookSwitcherSelectAll"]
        DeselectAll["Ctrl+D<br/>RulebookSwitcherDeselectAll"]
        UpdateSelected["selected_rulebooks: HashSet<String>"]
    end
    
    subgraph "Confirmation"
        ConfirmSelection["Enter<br/>RulebookSwitcherConfirm"]
        SendUpdate["OutputEvent::RequestRulebookUpdate<br/>Vec<String> of URIs"]
        ShowMessage["Display confirmation message"]
        ClosePopup["show_rulebook_switcher = false"]
    end
    
    CtrlK --> LoadRulebooks
    LoadRulebooks --> ShowPopup
    ShowPopup --> LoadCurrent
    LoadCurrent --> SearchInput
    
    SearchInput --> FilterRulebooks
    FilterRulebooks --> UpdateFiltered
    
    UpdateFiltered --> Navigate
    Navigate --> ToggleItem
    Navigate --> SelectAll
    Navigate --> DeselectAll
    ToggleItem --> UpdateSelected
    SelectAll --> UpdateSelected
    DeselectAll --> UpdateSelected
    
    UpdateSelected --> ConfirmSelection
    ConfirmSelection --> SendUpdate
    SendUpdate --> ShowMessage
    ShowMessage --> ClosePopup
```

**Rulebook Switcher Workflow**
Multi-select interface with search filtering and bulk selection operations.

The `filter_rulebooks` function at [tui/src/services/handlers/popup.rs:17-41]() filters rulebooks by matching the search term against URI, description, or tags (case-insensitive).

| Handler Function | Purpose | Location |
|-----------------|---------|----------|
| `handle_show_rulebook_switcher` | Clear input, request current rulebooks | [tui/src/services/handlers/popup.rs:213-232]() |
| `handle_rulebook_switcher_toggle` | Toggle selection of current item | [tui/src/services/handlers/popup.rs:250-264]() |
| `handle_rulebook_switcher_confirm` | Send selected URIs to CLI | [tui/src/services/handlers/popup.rs:272-291]() |
| `handle_rulebook_search_input_changed` | Update search, re-filter | [tui/src/services/handlers/popup.rs:313-318]() |
| `filter_rulebooks` | Filter by URI/description/tags | [tui/src/services/handlers/popup.rs:17-41]() |

**State Fields**:
- `show_rulebook_switcher: bool` - Popup visibility
- `available_rulebooks: Vec<ListRuleBook>` - All rulebooks from API
- `filtered_rulebooks: Vec<ListRuleBook>` - Search-filtered list
- `selected_rulebooks: HashSet<String>` - Selected URIs
- `rulebook_search_input: String` - Search query
- `rulebook_switcher_selected: usize` - Navigation index

Sources: [tui/src/services/handlers/popup.rs:210-338](), [tui/src/app/events.rs:108-120]()

## Command Palette and Shortcuts Popup

The unified shortcuts popup operates in two modes: **Commands** (command palette) and **Shortcuts** (keyboard reference):

```mermaid
graph TB
    subgraph "Trigger Events"
        SlashCommand["/commands<br/>ShowCommandPalette"]
        CtrlS["Ctrl+S<br/>ShowShortcuts"]
    end
    
    subgraph "Popup Modes"
        CommandsMode["ShortcutsPopupMode::Commands<br/>Searchable command list"]
        ShortcutsMode["ShortcutsPopupMode::Shortcuts<br/>Keyboard shortcuts reference"]
    end
    
    subgraph "Command Palette Features"
        SearchInput["CommandPaletteSearchInputChanged<br/>command_palette_search"]
        FilterCommands["filter_commands(query)<br/>Match name/description"]
        NavigateCommands["Up/Down<br/>command_palette_selected"]
        ExecuteCommand["Enter<br/>execute_command_palette_selection"]
    end
    
    subgraph "Command Execution"
        GetCommand["filtered_commands[selected]"]
        ConvertAction["action.to_command_id()"]
        ExecuteCmd["execute_command(command_id, ctx)"]
        SendEvent["InputEvent or OutputEvent"]
    end
    
    subgraph "Command Registry"
        GetAllCommands["get_all_commands()<br/>commands.rs"]
        CommandList["Profiles, Rulebooks, Shortcuts<br/>Shell, Sessions, Usage, etc."]
        CommandActions["CommandAction enum<br/>OpenProfileSwitcher, etc."]
    end
    
    SlashCommand --> CommandsMode
    CtrlS --> ShortcutsMode
    
    CommandsMode --> SearchInput
    SearchInput --> FilterCommands
    FilterCommands --> NavigateCommands
    NavigateCommands --> ExecuteCommand
    
    ExecuteCommand --> GetCommand
    GetCommand --> ConvertAction
    ConvertAction --> ExecuteCmd
    ExecuteCmd --> SendEvent
    
    GetAllCommands --> CommandList
    CommandList --> CommandActions
    CommandActions --> ConvertAction
```

**Unified Shortcuts Popup Architecture**
Two-mode popup for command discovery and keyboard shortcut reference.

### Command Palette (Commands Mode)

The command palette at [tui/src/services/commands.rs:106-193]() provides a searchable list of all TUI commands:

| Command | Description | Shortcut | Action |
|---------|-------------|----------|--------|
| Profiles | Change active profile | Ctrl+F | `OpenProfileSwitcher` |
| Rulebooks | Select rulebooks | Ctrl+K | `OpenRulebookSwitcher` |
| Context | Show context utilization | Ctrl+G | `ShowUsage` |
| Shortcuts | Show keyboard shortcuts | Ctrl+S | `OpenShortcuts` |
| Shell Mode | Open interactive shell | $ | `OpenShellMode` |
| New Session | Start new session | /new | `NewSession` |
| Sessions | List sessions | /sessions | `OpenSessions` |
| Resume | Resume last session | /resume | `ResumeSession` |
| Usage | Show token usage | /usage | `ShowUsage` |
| Status | Show account info | /status | `ShowStatus` |
| Memorize | Save to memory | /memorize | `MemorizeConversation` |
| Submit Issue | GitHub issue | /issue | `SubmitIssue` |
| Get Help | Discord support | /support | `GetSupport` |
| Switch Model | Toggle smart/eco | /model | `SwitchModel` |

The `filter_commands` function at [tui/src/services/commands.rs:278-291]() performs case-insensitive matching against command names and descriptions.

### Command Execution Flow

```mermaid
graph LR
    subgraph "Command Execution Pipeline"
        PaletteSelect["execute_command_palette_selection()"]
        GetAction["command.action"]
        ToCommandId["action.to_command_id()"]
        HasSlashCmd{"Has<br/>command_id?"}
        ExecuteCmd["execute_command(command_id)"]
        DirectEvent["Send InputEvent directly"]
    end
    
    PaletteSelect --> GetAction
    GetAction --> ToCommandId
    ToCommandId --> HasSlashCmd
    HasSlashCmd -->|Yes| ExecuteCmd
    HasSlashCmd -->|No| DirectEvent
    
    ExecuteCmd --> CommandCtx["CommandContext<br/>state, input_tx, output_tx"]
    DirectEvent --> EventSend["ShowProfileSwitcher<br/>ShowShortcuts, etc."]
```

**Command Execution Path**
Commands are either executed via `execute_command()` or trigger direct events.

The `CommandAction::to_command_id()` method at [tui/src/services/commands.rs:65-83]() converts actions to slash command IDs. Actions without slash commands (like `OpenProfileSwitcher`) are handled by sending `InputEvent`s directly at [tui/src/services/handlers/tool.rs:371-405]().

Sources: [tui/src/services/commands.rs:1-949](), [tui/src/services/handlers/popup.rs:340-402](), [tui/src/services/handlers/tool.rs:361-410]()

## Approval Popup

The approval popup (`PopupService`) provides a sophisticated multi-tool approval interface with tabs and detailed tool information:

```mermaid
graph TB
    subgraph "Tool Approval Workflow"
        ToolCalls["MessageToolCalls event<br/>Vec<ToolCall>"]
        CheckPolicy["Check AutoApprovePolicy<br/>per tool"]
        ShowPopup["approval_popup.toggle()<br/>is_dialog_open = true"]
    end
    
    subgraph "Popup State"
        ApprovalPopup["approval_popup: PopupService"]
        ToolTabs["One tab per tool call"]
        ApprovalStatus["Approved/Rejected per tool"]
        MaximizeState["is_maximized flag"]
    end
    
    subgraph "User Interaction"
        NavigateTabs["Tab/Shift+Tab<br/>ApprovalPopupNextTab/PrevTab"]
        ToggleStatus["Space<br/>ApprovalPopupToggleApproval"]
        ToggleMaximize["Ctrl+G<br/>toggle_maximize()"]
        Submit["Enter<br/>Get approved/rejected lists"]
        Cancel["Esc<br/>ApprovalPopupEscape"]
    end
    
    subgraph "Execution Flow"
        GetApproved["get_approved_tool_calls()"]
        GetRejected["get_rejected_tool_calls()"]
        UpdateQueue["session_tool_calls_queue<br/>HashMap<String, ToolCallStatus>"]
        ExecuteFirst["Execute first tool in order"]
        SendAccept["OutputEvent::AcceptTool"]
        SendReject["InputEvent::HandleReject"]
    end
    
    ToolCalls --> CheckPolicy
    CheckPolicy --> ShowPopup
    ShowPopup --> ApprovalPopup
    
    ApprovalPopup --> ToolTabs
    ToolTabs --> NavigateTabs
    ToolTabs --> ToggleStatus
    ToolTabs --> ToggleMaximize
    
    NavigateTabs --> Submit
    ToggleStatus --> Submit
    Submit --> GetApproved
    Submit --> GetRejected
    
    GetApproved --> UpdateQueue
    GetRejected --> UpdateQueue
    UpdateQueue --> ExecuteFirst
    ExecuteFirst --> SendAccept
    ExecuteFirst --> SendReject
```

**Approval Popup Workflow**
Multi-tool approval with tab navigation and execution ordering.

### Approval State Management

The approval popup maintains execution state via several data structures:

| Field | Type | Purpose |
|-------|------|---------|
| `message_tool_calls` | `Option<Vec<ToolCall>>` | Current batch of tools to approve |
| `message_approved_tools` | `HashSet<ToolCall>` | Approved tools from popup |
| `message_rejected_tools` | `HashSet<ToolCall>` | Rejected tools from popup |
| `tool_call_execution_order` | `Vec<String>` | Order to execute tool IDs |
| `session_tool_calls_queue` | `HashMap<String, ToolCallStatus>` | Per-tool execution status |
| `approval_popup` | `PopupService` | Popup service instance |

When the user presses Enter in the approval popup, the handler at [tui/src/services/handlers/input.rs:86-149]() extracts approved/rejected lists and creates a `tools_status` vector maintaining the original order from `message_tool_calls`. The first tool is executed immediately while others are queued.

### Approval Popup API

| Method | Purpose | Usage |
|--------|---------|-------|
| `toggle()` | Show/hide popup | [tui/src/services/handlers/input.rs:398]() |
| `is_visible()` | Check visibility | [tui/src/services/handlers/input.rs:24]() |
| `toggle_approval_status()` | Space to toggle current tool | [tui/src/services/handlers/input.rs:26]() |
| `toggle_maximize()` | Expand/collapse popup | [tui/src/services/handlers/popup.rs:413]() |
| `get_approved_tool_calls()` | Get approved list | [tui/src/services/handlers/input.rs:89]() |
| `get_rejected_tool_calls()` | Get rejected list | [tui/src/services/handlers/input.rs:95]() |
| `escape()` | Cancel and hide | [tui/src/services/handlers/input.rs:148]() |

Sources: [tui/src/services/handlers/input.rs:86-149](), [tui/src/services/handlers/tool.rs:48-90](), [tui/src/app/events.rs:85-90]()

## File Changes Popup

The file changes popup displays all file modifications tracked by the changeset system with revert and editor integration:

```mermaid
graph TB
    subgraph "Trigger"
        CtrlY["Side Panel Changeset Click<br/>ShowFileChangesPopup"]
        NoFiles{"file_count() > 0?"}
    end
    
    subgraph "Popup Display"
        ShowPopup["show_file_changes_popup = true"]
        ListFiles["changeset.files_in_order()"]
        SearchFilter["file_changes_search<br/>Filter by filename"]
        Navigate["Up/Down<br/>file_changes_selected"]
    end
    
    subgraph "File Operations"
        RevertFile["Ctrl+X<br/>FileChangesRevertFile"]
        RevertAll["Ctrl+Z<br/>FileChangesRevertAll"]
        OpenEditor["Ctrl+N<br/>FileChangesOpenEditor"]
    end
    
    subgraph "Revert Logic"
        GetFile["Get selected TrackedFile"]
        CheckBackup{"Has backup_path?"}
        RestoreBackup["Restore from backup"]
        DeleteFile["Delete created file"]
        UpdateState["Update FileState<br/>Reverted/Deleted"]
    end
    
    subgraph "Editor Integration"
        SetPending["pending_editor_open = Some(path)"]
        EventLoop["Event loop detects pending_editor_open"]
        OpenExternal["Open in external editor"]
    end
    
    CtrlY --> NoFiles
    NoFiles -->|Yes| ShowPopup
    NoFiles -->|No| Return["Return"]
    ShowPopup --> ListFiles
    ListFiles --> SearchFilter
    SearchFilter --> Navigate
    
    Navigate --> RevertFile
    Navigate --> RevertAll
    Navigate --> OpenEditor
    
    RevertFile --> GetFile
    GetFile --> CheckBackup
    CheckBackup -->|Yes| RestoreBackup
    CheckBackup -->|No| DeleteFile
    RestoreBackup --> UpdateState
    DeleteFile --> UpdateState
    
    OpenEditor --> SetPending
    SetPending --> EventLoop
    EventLoop --> OpenExternal
```

**File Changes Popup Architecture**
File modification tracking with revert and editor operations.

### File Change Tracking

The popup displays files from the `changeset` field, which tracks all file modifications during the session at [tui/src/services/changeset.rs]():

| File State | Description | Revert Behavior |
|------------|-------------|-----------------|
| `Created` | New file created by agent | Delete file |
| `Modified` | Existing file edited | Restore from backup |
| `Deleted` | File removed by agent | Restore from backup (if exists) |
| `Removed` | File removed without backup | Cannot revert |
| `Reverted` | Already reverted | Grayed out, skip |

### File Changes Handlers

| Handler Function | Keybinding | Purpose | Location |
|-----------------|------------|---------|----------|
| `handle_show_file_changes_popup` | Changeset click | Show popup if files exist | [tui/src/services/handlers/popup.rs:544-561]() |
| `handle_file_changes_popup_navigate` | ↑/↓ | Navigate file list | [tui/src/services/handlers/popup.rs:581-613]() |
| `handle_file_changes_popup_revert` | Ctrl+X | Revert selected file | [tui/src/services/handlers/popup.rs:615-671]() |
| `handle_file_changes_popup_revert_all` | Ctrl+Z | Revert all files | [tui/src/services/handlers/popup.rs:673-739]() |
| `handle_file_changes_popup_open_editor` | Ctrl+N | Open in editor | [tui/src/services/handlers/popup.rs:742-758]() |
| `handle_file_changes_popup_mouse_click` | Mouse | Click to open file | [tui/src/services/handlers/popup.rs:761-811]() |

The revert functions call `Changeset::revert_file()` which handles backup restoration and file deletion based on file state.

Sources: [tui/src/services/handlers/popup.rs:542-811](), [tui/src/app/events.rs:78-81]()

## Side Panel

The side panel provides a persistent display of session information and file changes:

```mermaid
graph TB
    subgraph "Sections"
        Changeset["Changeset<br/>File modifications"]
        Usage["Usage<br/>Token utilization"]
        SessionInfo["Session Info<br/>Profile, model"]
    end
    
    subgraph "State Management"
        ShowSidePanel["show_side_panel: bool"]
        Focus["side_panel_focus: SidePanelSection"]
        Collapsed["side_panel_section_collapsed<br/>HashMap<Section, bool>"]
        Areas["side_panel_areas<br/>HashMap<Section, Rect>"]
    end
    
    subgraph "Interactions"
        Toggle["Ctrl+Y<br/>ToggleSidePanel"]
        NextSection["Tab<br/>SidePanelNextSection"]
        ToggleSection["Enter<br/>SidePanelToggleSection"]
        MouseClick["Click<br/>Toggle or open popup"]
    end
    
    subgraph "Changeset Integration"
        FileList["Display file_count()"]
        FileClick["Click file<br/>Open file changes popup"]
        FileStats["Show file states<br/>Created/Modified/Deleted"]
    end
    
    Changeset --> ShowSidePanel
    Usage --> ShowSidePanel
    SessionInfo --> ShowSidePanel
    
    ShowSidePanel --> Focus
    Focus --> Collapsed
    Collapsed --> Areas
    
    Toggle --> ShowSidePanel
    NextSection --> Focus
    ToggleSection --> Collapsed
    MouseClick --> Areas
    
    Changeset --> FileList
    FileList --> FileClick
    FileClick --> FileStats
```

**Side Panel Architecture**
Multi-section panel with collapsible sections and mouse interaction.

### Side Panel Implementation

The side panel is toggled via `Ctrl+Y` which sends `InputEvent::ToggleSidePanel` at [tui/src/services/handlers/popup.rs:450-453](). The `SidePanelSection` enum defines available sections:

```rust
pub enum SidePanelSection {
    Changeset,
    Usage,
    // Future sections can be added here
}
```

The `side_panel_focus` field tracks which section is currently focused, and `side_panel_section_collapsed` stores collapse state per section. The rendering system stores clickable areas in `side_panel_areas` to enable mouse interaction.

**Mouse Click Handling**: When clicking the Changeset section at [tui/src/services/handlers/popup.rs:496-529](), the handler distinguishes between:
- **Header click** (row 0): Toggle collapse state
- **Content click** (other rows): Open file changes popup

Sources: [tui/src/services/handlers/popup.rs:448-540](), [tui/src/app/events.rs:130-134]()

## Hints System

The hint system provides contextual guidance based on application state with a priority-based display:

```mermaid
graph TB
    subgraph "Hint Priority Order"
        Priority1["1. is_pasting<br/>Pasting text..."]
        Priority2["2. ctrl_c_pressed_once<br/>Press Ctrl+C again to exit"]
        Priority3["3. show_shell_mode<br/>Shell mode is on   Esc to exit"]
        Priority4["4. show_shortcuts && input.is_empty()<br/>Full shortcuts display"]
        Priority5["5. latest_tool_call && !warnings<br/>Retry hint + shortcuts"]
        Priority6["6. Default<br/>Shortcuts + profile info"]
    end
    
    subgraph "Hint Components"
        ShortcutsLeft["$ shell | / commands | ctrl+s shortcuts"]
        ProfileRight["profile <name> | ctrl+y side panel"]
        RetryHint["ctrl+r to retry last command"]
        SelectHint["Fn/Option/Shift + drag to select"]
        ContextWarning["Approaching max context limit"]
    end
    
    subgraph "Context-Aware Hints"
        CheckContextUsage["total_session_usage vs max_tokens"]
        HighCostWarning["total_tokens >= 90% max"]
        ApproachingMax["tokens >= approach_warning_threshold"]
    end
    
    Priority1 --> ShortcutsLeft
    Priority2 --> ShortcutsLeft
    Priority3 --> ShortcutsLeft
    Priority4 --> ShortcutsLeft
    Priority5 --> RetryHint
    Priority6 --> ProfileRight
    
    CheckContextUsage --> HighCostWarning
    CheckContextUsage --> ApproachingMax
    HighCostWarning --> ContextWarning
    ApproachingMax --> ContextWarning
```

**Hint System Priority Flow**
Hints are displayed based on priority order, with context utilization warnings.

### Hint Display Logic

The `render_hint_or_shortcuts()` function at [tui/src/services/hint_helper.rs:13-212]() implements a waterfall of hint conditions:

| Priority | Condition | Hint Displayed | Purpose |
|----------|-----------|---------------|---------|
| 1 | `is_pasting` | "Pasting text..." | Feedback during paste |
| 2 | `ctrl_c_pressed_once` | "Press Ctrl+C again to exit Stakpak" | Quit confirmation |
| 3 | `show_shell_mode && !dialogs` | "Shell mode is on   Esc to exit" | Shell mode indicator |
| 4 | `show_shortcuts && input.is_empty()` | Full shortcuts layout | Keyboard shortcuts |
| 5 | `latest_tool_call && !warnings` | "ctrl+r to retry" + shortcuts | Retry hint |
| 6 | Default | Shortcuts + profile info | General usage |

### Context Utilization Hints

The hint system monitors token usage at [tui/src/services/hint_helper.rs:52-62]() and displays warnings when approaching context limits:

```rust
let context_info = state.llm_model.as_ref()
    .map(|model| model.context_info())
    .unwrap_or_default();
let max_tokens = context_info.max_tokens as u32;
let high_cost_warning = state.total_session_usage.total_tokens 
    >= (max_tokens as f64 * 0.9) as u32;
let approaching_max = (state.total_session_usage.total_tokens as f64 / max_tokens as f64)
    >= context_info.approach_warning_threshold;
```

When `high_cost_warning` or `approaching_max` is true, the retry hint is suppressed and context warnings may be displayed.

### Hint Alignment

The hints use left and right alignment for optimal space usage at [tui/src/services/hint_helper.rs:96-149]():
- **Left side**: `"$ shell | / commands | ctrl+s shortcuts"`
- **Right side**: `"profile <name> | ctrl+y side panel"`
- **Unix-only**: Second line with `"Fn/Option/Shift + drag to select"` for mouse selection

Sources: [tui/src/services/hint_helper.rs:1-213](), [tui/src/app/mod.rs]()

<old_str>
## Autocomplete System

The autocomplete system provides intelligent file and command completion triggered by Tab key or `@` symbol:

```mermaid
graph TB
    subgraph "AutoComplete Core"
        AutoCompleteStruct["AutoComplete struct"]
        FileCache["file_suggestions: Vec<String>"]
        FilterCache["filter_cache: HashMap<String, Vec<String>>"]
        DebouncedFilter["debounced_filter: DebouncedFilter"]
    end
    
    subgraph "Trigger Detection"
        TabTrigger["handle_tab_trigger()"]
        AtTrigger["handle_at_trigger()"]
        FindAtTrigger["find_at_trigger()"]
        GetCurrentWord["get_current_word()"]
    end
    
    subgraph "File System Integration"
        LoadFiles["load_files_from_directory()"]
        CollectRecursive["collect_files_recursive()"]
        GitignoreFilter["matches_gitignore_pattern()"]
    end
    
    subgraph "Filtering & Display"
        FilterFiles["filter_files()"]
        FuzzyMatch["fuzzy_match_optimized()"]
        HelperDropdown["render_file_dropdown()"]
    end
    
    TabTrigger --> AutoCompleteStruct
    AtTrigger --> FindAtTrigger
    FindAtTrigger --> GetCurrentWord
    GetCurrentWord --> FilterFiles
    
    AutoCompleteStruct --> FileCache
    AutoCompleteStruct --> FilterCache
    AutoCompleteStruct --> DebouncedFilter
    
    LoadFiles --> CollectRecursive
    CollectRecursive --> GitignoreFilter
    
    FilterFiles --> FuzzyMatch
    FilterFiles --> HelperDropdown
    
    FileCache --> FilterFiles
    FilterCache --> FilterFiles
```

**Autocomplete System Architecture**
Shows the flow from trigger detection through file system scanning to filtered results display.

The autocomplete system implements several key features:

| Feature | Implementation | Purpose |
|---------|---------------|---------|
| Tab Completion | `handle_tab_trigger()` at [tui/src/services/auto_complete.rs:279-302]() | Complete current word with files |
| @ File References | `handle_at_trigger()` at [tui/src/services/auto_complete.rs:305-314]() | Insert file paths with @ prefix |
| Gitignore Support | `matches_gitignore_pattern()` integration | Respect .gitignore patterns |
| Debounced Filtering | `DebouncedFilter` at [tui/src/services/auto_complete.rs:354-382]() | Prevent excessive filtering |
| Fuzzy Matching | `fuzzy_match_optimized()` at [tui/src/services/auto_complete.rs:208-231]() | Match partial file names |

Sources: [tui/src/services/auto_complete.rs:11-36](), [tui/src/services/auto_complete.rs:234-276](), [tui/src/services/auto_complete.rs:279-352]()

## Dialog Systems

The TUI implements multiple dialog types for user interaction:

```mermaid
graph TB
    subgraph "Dialog Types"
        ConfirmationDialog["ConfirmationDialog"]
        SessionsDialog["SessionsDialog"]
    end
    
    subgraph "Dialog State"
        IsDialogOpen["state.is_dialog_open"]
        ShowSessionsDialog["state.show_sessions_dialog"]
        SessionSelected["state.session_selected"]
    end
    
    subgraph "Dialog Rendering"
        RenderConfirmation["render_confirmation_dialog()"]
        RenderSessions["render_sessions_dialog()"]
        MessageLines["get_wrapped_message_lines()"]
        DialogPositioning["Dialog Positioning Logic"]
    end
    
    subgraph "User Actions"
        EnterKey["Enter - Confirm/Select"]
        EscapeKey["Escape - Cancel"]
        ArrowKeys["Arrow Keys - Navigate"]
        DollarKey["$ - Shell Mode"]
    end
    
    ConfirmationDialog --> IsDialogOpen
    SessionsDialog --> ShowSessionsDialog
    SessionsDialog --> SessionSelected
    
    IsDialogOpen --> RenderConfirmation
    ShowSessionsDialog --> RenderSessions
    
    RenderConfirmation --> MessageLines
    RenderSessions --> MessageLines
    MessageLines --> DialogPositioning
    
    EnterKey --> ConfirmationDialog
    EnterKey --> SessionsDialog
    EscapeKey --> ConfirmationDialog
    EscapeKey --> SessionsDialog
    ArrowKeys --> SessionsDialog
    DollarKey --> ConfirmationDialog
```

**Dialog System Architecture**
Shows dialog types, state management, and user interaction patterns.

### Confirmation Dialog

The confirmation dialog appears when the agent suggests executing potentially dangerous commands:

```rust
// Dialog message and options
"Press Enter to continue. '$' to run the command yourself or Esc to cancel and reprompt"
```

The dialog renders at [tui/src/services/confirmation_dialog.rs:11-49]() with dynamic positioning based on message content.

### Sessions Dialog

The sessions dialog allows users to select from available conversation sessions with formatted timestamps and titles at [tui/src/services/sessions_dialog.rs:11-92]().

Sources: [tui/src/services/confirmation_dialog.rs:1-50](), [tui/src/services/sessions_dialog.rs:1-93]()

## Shell Integration

The shell integration system enables background command execution while maintaining TUI responsiveness:

```mermaid
graph TB
    subgraph "Shell Mode Components"
        ShellCommand["ShellCommand struct"]
        ShellEvent["ShellEvent enum"]
        ProcessRegistry["PROCESS_REGISTRY"]
        ShellPromptPrefix["SHELL_PROMPT_PREFIX"]
    end
    
    subgraph "Command Execution"
        RunBackgroundShell["run_background_shell_command()"]
        RunPtyCommand["run_pty_command()"]
        IsInteractivePrompt["is_interactive_prompt()"]
        IsClearCommand["is_clear_command()"]
    end
    
    subgraph "Process Management"
        StdinChannel["stdin_tx: mpsc::Sender<String>"]
        StdoutThread["Stdout Reading Thread"]
        StderrThread["Stderr Reading Thread"]
        ProcessKill["ShellCommand::kill()"]
    end
    
    subgraph "Event Types"
        OutputEvent["ShellEvent::Output"]
        ErrorEvent["ShellEvent::Error"]
        WaitingEvent["ShellEvent::WaitingForInput"]
        CompletedEvent["ShellEvent::Completed"]
        ClearEvent["ShellEvent::Clear"]
    end
    
    RunBackgroundShell --> ShellCommand
    RunPtyCommand --> ShellCommand
    ShellCommand --> StdinChannel
    ShellCommand --> ProcessRegistry
    
    RunBackgroundShell --> StdoutThread
    RunBackgroundShell --> StderrThread
    
    StdoutThread --> IsInteractivePrompt
    StderrThread --> IsInteractivePrompt
    
    IsInteractivePrompt --> WaitingEvent
    StdoutThread --> OutputEvent
    StderrThread --> ErrorEvent
    
    IsClearCommand --> ClearEvent
    ProcessKill --> ProcessRegistry
```

**Shell Integration Architecture**
Shows command execution flow, process management, and event handling for shell operations.

### Key Shell Features

| Feature | Implementation | Description |
|---------|---------------|-------------|
| Background Execution | `run_background_shell_command()` at [tui/src/services/shell_mode.rs:93-260]() | Non-blocking command execution |
| PTY Support | `run_pty_command()` at [tui/src/services/shell_mode.rs:263-428]() | Unix PTY for interactive commands |
| Process Tracking | `PROCESS_REGISTRY` at [tui/src/services/shell_mode.rs:11-18]() | Global process management |
| Interactive Detection | `is_interactive_prompt()` at [tui/src/services/shell_mode.rs:21-26]() | Detect password prompts |
| Clear Command | `is_clear_command()` at [tui/src/services/shell_mode.rs:48-51]() | Handle screen clearing |

The shell mode uses `SHELL_PROMPT_PREFIX` constant (`"$ "`) to visually distinguish shell input from regular chat input.

Sources: [tui/src/services/shell_mode.rs:28-260](), [tui/src/services/shell_mode.rs:263-428]()

## Hint and Helper System

The hint system provides contextual guidance and shortcuts based on current application state:

```mermaid
graph TB
    subgraph "Hint Conditions"
        InputNotEmpty["!state.input.is_empty()"]
        ShowShellMode["state.show_shell_mode"]
        IsDialogOpen["state.is_dialog_open"]
        IsPasting["state.is_pasting"]
        CtrlCPressed["state.ctrl_c_pressed_once"]
        ShowShortcuts["state.show_shortcuts"]
        LatestToolCall["state.latest_tool_call"]
    end
    
    subgraph "Hint Types"
        SendHint["Press Enter to send"]
        PastingHint["Pasting text..."]
        ExitHint["Press Ctrl+C again to exit"]
        ShellModeHint["Shell mode is on     '$' to undo"]
        ShortcutsHint["Full shortcuts display"]
        RetryHint["Ctrl+R to retry last command"]
        QuestionHint["? for shortcuts"]
    end
    
    subgraph "Helper Messages"
        StatusMessage["push_status_message()"]
        HelpMessage["push_help_message()"]
        ErrorMessage["push_error_message()"]
        ClearMessage["push_clear_message()"]
        MemorizeMessage["push_memorize_message()"]
    end
    
    InputNotEmpty --> SendHint
    IsPasting --> PastingHint
    CtrlCPressed --> ExitHint
    ShowShellMode --> ShellModeHint
    ShowShortcuts --> ShortcutsHint
    LatestToolCall --> RetryHint
    
    StatusMessage --> HelpMessage
    HelpMessage --> ErrorMessage
    ErrorMessage --> ClearMessage
    ClearMessage --> MemorizeMessage
```

**Hint and Helper System Flow**
Shows conditional hint display logic and helper message types.

### Hint Display Logic

The `render_hint_or_shortcuts()` function at [tui/src/services/hint_helper.rs:11-91]() implements a priority-based hint system:

1. **Input hints** - When user has typed content
2. **Pasting indicator** - During paste operations  
3. **Exit confirmation** - After first Ctrl+C press
4. **Shell mode indicator** - When in shell mode
5. **Keyboard shortcuts** - When shortcuts are enabled
6. **Retry hint** - When last tool call is available

Sources: [tui/src/services/hint_helper.rs:1-92](), [tui/src/services/helper_block.rs:91-199]()

## Input Rendering

The input rendering system handles multiline input with cursor positioning and shell mode indicators:

```mermaid
graph TB
    subgraph "Input Processing"
        GetMultilineLines["get_multiline_input_lines()"]
        InputSegments["input.split('\n')"]
        CursorPosition["state.cursor_position"]
        WaitingForShell["state.waiting_for_shell_input"]
    end
    
    subgraph "Line Construction"
        LineSpans["Vec<Span>"]
        ShellPrefix["SHELL_PROMPT_PREFIX"]
        RegularPrefix["> "]
        CursorRendering["Cursor █ character"]
    end
    
    subgraph "Cursor States"
        BeforeCursor["Text before cursor"]
        AtCursor["Character at cursor"]
        AfterCursor["Text after cursor"]
        CursorAtEnd["Cursor at end of input"]
    end
    
    subgraph "Visual Modes"
        NormalMode["Normal chat input"]
        ShellModeInput["Shell command input"]
        PasswordMode["Masked password input"]
    end
    
    GetMultilineLines --> InputSegments
    InputSegments --> CursorPosition
    CursorPosition --> LineSpans
    
    WaitingForShell --> PasswordMode
    ShellPrefix --> ShellModeInput
    RegularPrefix --> NormalMode
    
    BeforeCursor --> LineSpans
    AtCursor --> CursorRendering
    AfterCursor --> LineSpans
    CursorAtEnd --> CursorRendering
    
    LineSpans --> CursorRendering
```

**Input Rendering Architecture**
Shows multiline input processing, cursor handling, and visual mode switching.

The input renderer at [tui/src/services/render_input.rs:6-129]() handles:

- **Multiline support** with proper line segmentation
- **Cursor visualization** using block character `█`
- **Shell mode indicators** with yellow `$` prefix
- **Password masking** when waiting for shell input
- **UTF-8 character handling** for proper cursor positioning

Sources: [tui/src/services/render_input.rs:1-130]()

## Dropdown Rendering

The dropdown system provides visual feedback for autocomplete and helper suggestions:

```mermaid
graph TB
    subgraph "Dropdown Types"
        HelperDropdown["Helper Command Dropdown"]
        FileDropdown["File Autocomplete Dropdown"]
    end
    
    subgraph "Rendering Components"
        RenderAutocomplete["render_autocomplete_dropdown()"]
        RenderHelperDrop["render_helper_dropdown()"]
        RenderFileDrop["render_file_dropdown()"]
        GetFileIcon["get_file_icon()"]
    end
    
    subgraph "State Dependencies"
        ShowHelperDropdown["state.show_helper_dropdown"]
        FilteredFiles["state.filtered_files"]
        FilteredHelpers["state.filtered_helpers"]
        HelperSelected["state.helper_selected"]
        AutocompleteTrigger["state.autocomplete.trigger_char"]
    end
    
    subgraph "File Icons"
        RustIcon["🦀 .rs files"]
        TomlIcon["⚙️ .toml files"]
        MarkdownIcon["📝 .md files"]
        JsonIcon["📋 .json files"]
        FolderIcon["📁 directories"]
        DefaultIcon["📄 default"]
    end
    
    RenderAutocomplete --> RenderHelperDrop
    RenderAutocomplete --> RenderFileDrop
    
    ShowHelperDropdown --> RenderAutocomplete
    FilteredFiles --> RenderFileDrop
    FilteredHelpers --> RenderHelperDrop
    HelperSelected --> RenderFileDrop
    AutocompleteTrigger --> RenderFileDrop
    
    GetFileIcon --> RustIcon
    GetFileIcon --> TomlIcon
    GetFileIcon --> MarkdownIcon
    GetFileIcon --> JsonIcon
    GetFileIcon --> FolderIcon
    GetFileIcon --> DefaultIcon
```

**Dropdown Rendering System**
Shows dropdown types, rendering logic, and file icon mapping for visual enhancement.

The dropdown renderer at [tui/src/services/helper_dropdown.rs:10-127]() provides:

- **File extension icons** using Unicode emojis
- **Trigger-specific styling** for Tab vs @ completion
- **Selection highlighting** with reversed colors
- **Dynamic sizing** based on content

Sources: [tui/src/services/helper_dropdown.rs:1-128]()

## Autocomplete System

The autocomplete system provides intelligent file and command completion triggered by Tab key or `@` symbol:

```mermaid
graph TB
    subgraph "AutoComplete Core"
        AutoCompleteStruct["AutoComplete struct"]
        FileCache["file_suggestions: Vec<String>"]
        FilterCache["filter_cache: HashMap<String, Vec<String>>"]
        DebouncedFilter["debounced_filter: DebouncedFilter"]
    end
    
    subgraph "Trigger Detection"
        TabTrigger["handle_tab_trigger()"]
        AtTrigger["handle_at_trigger()"]
        FindAtTrigger["find_at_trigger()"]
        GetCurrentWord["get_current_word()"]
    end
    
    subgraph "File System Integration"
        LoadFiles["load_files_from_directory()"]
        CollectRecursive["collect_files_recursive()"]
        GitignoreFilter["matches_gitignore_pattern()"]
    end
    
    subgraph "Filtering & Display"
        FilterFiles["filter_files()"]
        FuzzyMatch["fuzzy_match_optimized()"]
        HelperDropdown["render_file_dropdown()"]
    end
    
    TabTrigger --> AutoCompleteStruct
    AtTrigger --> FindAtTrigger
    FindAtTrigger --> GetCurrentWord
    GetCurrentWord --> FilterFiles
    
    AutoCompleteStruct --> FileCache
    AutoCompleteStruct --> FilterCache
    AutoCompleteStruct --> DebouncedFilter
    
    LoadFiles --> CollectRecursive
    CollectRecursive --> GitignoreFilter
    
    FilterFiles --> FuzzyMatch
    FilterFiles --> HelperDropdown
    
    FileCache --> FilterFiles
    FilterCache --> FilterFiles
```

**Autocomplete System Architecture**
Shows the flow from trigger detection through file system scanning to filtered results display.

The autocomplete system implements several key features:

| Feature | Implementation | Purpose |
|---------|---------------|---------|
| Tab Completion | `handle_tab_trigger()` at [tui/src/services/auto_complete.rs:279-302]() | Complete current word with files |
| @ File References | `handle_at_trigger()` at [tui/src/services/auto_complete.rs:305-314]() | Insert file paths with @ prefix |
| Gitignore Support | `matches_gitignore_pattern()` integration | Respect .gitignore patterns |
| Debounced Filtering | `DebouncedFilter` at [tui/src/services/auto_complete.rs:354-382]() | Prevent excessive filtering |
| Fuzzy Matching | `fuzzy_match_optimized()` at [tui/src/services/auto_complete.rs:208-231]() | Match partial file names |

Sources: [tui/src/services/auto_complete.rs:11-36](), [tui/src/services/auto_complete.rs:234-276](), [tui/src/services/auto_complete.rs:279-352]()

## Dialog Systems

The TUI implements multiple dialog types for user interaction:

```mermaid
graph TB
    subgraph "Dialog Types"
        ConfirmationDialog["ConfirmationDialog"]
        SessionsDialog["SessionsDialog"]
    end
    
    subgraph "Dialog State"
        IsDialogOpen["state.is_dialog_open"]
        ShowSessionsDialog["state.show_sessions_dialog"]
        SessionSelected["state.session_selected"]
    end
    
    subgraph "Dialog Rendering"
        RenderConfirmation["render_confirmation_dialog()"]
        RenderSessions["render_sessions_dialog()"]
        MessageLines["get_wrapped_message_lines()"]
        DialogPositioning["Dialog Positioning Logic"]
    end
    
    subgraph "User Actions"
        EnterKey["Enter - Confirm/Select"]
        EscapeKey["Escape - Cancel"]
        ArrowKeys["Arrow Keys - Navigate"]
        DollarKey["$ - Shell Mode"]
    end
    
    ConfirmationDialog --> IsDialogOpen
    SessionsDialog --> ShowSessionsDialog
    SessionsDialog --> SessionSelected
    
    IsDialogOpen --> RenderConfirmation
    ShowSessionsDialog --> RenderSessions
    
    RenderConfirmation --> MessageLines
    RenderSessions --> MessageLines
    MessageLines --> DialogPositioning
    
    EnterKey --> ConfirmationDialog
    EnterKey --> SessionsDialog
    EscapeKey --> ConfirmationDialog
    EscapeKey --> SessionsDialog
    ArrowKeys --> SessionsDialog
    DollarKey --> ConfirmationDialog
```

**Dialog System Architecture**
Shows dialog types, state management, and user interaction patterns.

### Confirmation Dialog

The confirmation dialog appears when the agent suggests executing potentially dangerous commands:

```rust
// Dialog message and options
"Press Enter to continue. '$' to run the command yourself or Esc to cancel and reprompt"
```

The dialog renders at [tui/src/services/confirmation_dialog.rs:11-49]() with dynamic positioning based on message content.

### Sessions Dialog

The sessions dialog allows users to select from available conversation sessions with formatted timestamps and titles at [tui/src/services/sessions_dialog.rs:11-92]().

Sources: [tui/src/services/confirmation_dialog.rs:1-50](), [tui/src/services/sessions_dialog.rs:1-93]()

## Shell Integration

The shell integration system enables background command execution while maintaining TUI responsiveness:

```mermaid
graph TB
    subgraph "Shell Mode Components"
        ShellCommand["ShellCommand struct"]
        ShellEvent["ShellEvent enum"]
        ProcessRegistry["PROCESS_REGISTRY"]
        ShellPromptPrefix["SHELL_PROMPT_PREFIX"]
    end
    
    subgraph "Command Execution"
        RunBackgroundShell["run_background_shell_command()"]
        RunPtyCommand["run_pty_command()"]
        IsInteractivePrompt["is_interactive_prompt()"]
        IsClearCommand["is_clear_command()"]
    end
    
    subgraph "Process Management"
        StdinChannel["stdin_tx: mpsc::Sender<String>"]
        StdoutThread["Stdout Reading Thread"]
        StderrThread["Stderr Reading Thread"]
        ProcessKill["ShellCommand::kill()"]
    end
    
    subgraph "Event Types"
        OutputEvent["ShellEvent::Output"]
        ErrorEvent["ShellEvent::Error"]
        WaitingEvent["ShellEvent::WaitingForInput"]
        CompletedEvent["ShellEvent::Completed"]
        ClearEvent["ShellEvent::Clear"]
    end
    
    RunBackgroundShell --> ShellCommand
    RunPtyCommand --> ShellCommand
    ShellCommand --> StdinChannel
    ShellCommand --> ProcessRegistry
    
    RunBackgroundShell --> StdoutThread
    RunBackgroundShell --> StderrThread
    
    StdoutThread --> IsInteractivePrompt
    StderrThread --> IsInteractivePrompt
    
    IsInteractivePrompt --> WaitingEvent
    StdoutThread --> OutputEvent
    StderrThread --> ErrorEvent
    
    IsClearCommand --> ClearEvent
    ProcessKill --> ProcessRegistry
```

**Shell Integration Architecture**
Shows command execution flow, process management, and event handling for shell operations.

### Key Shell Features

| Feature | Implementation | Description |
|---------|---------------|-------------|
| Background Execution | `run_background_shell_command()` at [tui/src/services/shell_mode.rs:93-260]() | Non-blocking command execution |
| PTY Support | `run_pty_command()` at [tui/src/services/shell_mode.rs:263-428]() | Unix PTY for interactive commands |
| Process Tracking | `PROCESS_REGISTRY` at [tui/src/services/shell_mode.rs:11-18]() | Global process management |
| Interactive Detection | `is_interactive_prompt()` at [tui/src/services/shell_mode.rs:21-26]() | Detect password prompts |
| Clear Command | `is_clear_command()` at [tui/src/services/shell_mode.rs:48-51]() | Handle screen clearing |

The shell mode uses `SHELL_PROMPT_PREFIX` constant (`"$ "`) to visually distinguish shell input from regular chat input.

Sources: [tui/src/services/shell_mode.rs:28-260](), [tui/src/services/shell_mode.rs:263-428]()

## Hint and Helper System

The hint system provides contextual guidance and shortcuts based on current application state:

```mermaid
graph TB
    subgraph "Hint Conditions"
        InputNotEmpty["!state.input.is_empty()"]
        ShowShellMode["state.show_shell_mode"]
        IsDialogOpen["state.is_dialog_open"]
        IsPasting["state.is_pasting"]
        CtrlCPressed["state.ctrl_c_pressed_once"]
        ShowShortcuts["state.show_shortcuts"]
        LatestToolCall["state.latest_tool_call"]
    end
    
    subgraph "Hint Types"
        SendHint["Press Enter to send"]
        PastingHint["Pasting text..."]
        ExitHint["Press Ctrl+C again to exit"]
        ShellModeHint["Shell mode is on     '$' to undo"]
        ShortcutsHint["Full shortcuts display"]
        RetryHint["Ctrl+R to retry last command"]
        QuestionHint["? for shortcuts"]
    end
    
    subgraph "Helper Messages"
        StatusMessage["push_status_message()"]
        HelpMessage["push_help_message()"]
        ErrorMessage["push_error_message()"]
        ClearMessage["push_clear_message()"]
        MemorizeMessage["push_memorize_message()"]
    end
    
    InputNotEmpty --> SendHint
    IsPasting --> PastingHint
    CtrlCPressed --> ExitHint
    ShowShellMode --> ShellModeHint
    ShowShortcuts --> ShortcutsHint
    LatestToolCall --> RetryHint
    
    StatusMessage --> HelpMessage
    HelpMessage --> ErrorMessage
    ErrorMessage --> ClearMessage
    ClearMessage --> MemorizeMessage
```

**Hint and Helper System Flow**
Shows conditional hint display logic and helper message types.

### Hint Display Logic

The `render_hint_or_shortcuts()` function at [tui/src/services/hint_helper.rs:11-91]() implements a priority-based hint system:

1. **Input hints** - When user has typed content
2. **Pasting indicator** - During paste operations  
3. **Exit confirmation** - After first Ctrl+C press
4. **Shell mode indicator** - When in shell mode
5. **Keyboard shortcuts** - When shortcuts are enabled
6. **Retry hint** - When last tool call is available

Sources: [tui/src/services/hint_helper.rs:1-92](), [tui/src/services/helper_block.rs:91-199]()

## Input Rendering

The input rendering system handles multiline input with cursor positioning and shell mode indicators:

```mermaid
graph TB
    subgraph "Input Processing"
        GetMultilineLines["get_multiline_input_lines()"]
        InputSegments["input.split('\n')"]
        CursorPosition["state.cursor_position"]
        WaitingForShell["state.waiting_for_shell_input"]
    end
    
    subgraph "Line Construction"
        LineSpans["Vec<Span>"]
        ShellPrefix["SHELL_PROMPT_PREFIX"]
        RegularPrefix["> "]
        CursorRendering["Cursor █ character"]
    end
    
    subgraph "Cursor States"
        BeforeCursor["Text before cursor"]
        AtCursor["Character at cursor"]
        AfterCursor["Text after cursor"]
        CursorAtEnd["Cursor at end of input"]
    end
    
    subgraph "Visual Modes"
        NormalMode["Normal chat input"]
        ShellModeInput["Shell command input"]
        PasswordMode["Masked password input"]
    end
    
    GetMultilineLines --> InputSegments
    InputSegments --> CursorPosition
    CursorPosition --> LineSpans
    
    WaitingForShell --> PasswordMode
    ShellPrefix --> ShellModeInput
    RegularPrefix --> NormalMode
    
    BeforeCursor --> LineSpans
    AtCursor --> CursorRendering
    AfterCursor --> LineSpans
    CursorAtEnd --> CursorRendering
    
    LineSpans --> CursorRendering
```

**Input Rendering Architecture**
Shows multiline input processing, cursor handling, and visual mode switching.

The input renderer at [tui/src/services/render_input.rs:6-129]() handles:

- **Multiline support** with proper line segmentation
- **Cursor visualization** using block character `█`
- **Shell mode indicators** with yellow `$` prefix
- **Password masking** when waiting for shell input
- **UTF-8 character handling** for proper cursor positioning

Sources: [tui/src/services/render_input.rs:1-130]()

## Dropdown Rendering

The dropdown system provides visual feedback for autocomplete and helper suggestions:

```mermaid
graph TB
    subgraph "Dropdown Types"
        HelperDropdown["Helper Command Dropdown"]
        FileDropdown["File Autocomplete Dropdown"]
    end
    
    subgraph "Rendering Components"
        RenderAutocomplete["render_autocomplete_dropdown()"]
        RenderHelperDrop["render_helper_dropdown()"]
        RenderFileDrop["render_file_dropdown()"]
        GetFileIcon["get_file_icon()"]
    end
    
    subgraph "State Dependencies"
        ShowHelperDropdown["state.show_helper_dropdown"]
        FilteredFiles["state.filtered_files"]
        FilteredHelpers["state.filtered_helpers"]
        HelperSelected["state.helper_selected"]
        AutocompleteTrigger["state.autocomplete.trigger_char"]
    end
    
    subgraph "File Icons"
        RustIcon["🦀 .rs files"]
        TomlIcon["⚙️ .toml files"]
        MarkdownIcon["📝 .md files"]
        JsonIcon["📋 .json files"]
        FolderIcon["📁 directories"]
        DefaultIcon["📄 default"]
    end
    
    RenderAutocomplete --> RenderHelperDrop
    RenderAutocomplete --> RenderFileDrop
    
    ShowHelperDropdown --> RenderAutocomplete
    FilteredFiles --> RenderFileDrop
    FilteredHelpers --> RenderHelperDrop
    HelperSelected --> RenderFileDrop
    AutocompleteTrigger --> RenderFileDrop
    
    GetFileIcon --> RustIcon
    GetFileIcon --> TomlIcon
    GetFileIcon --> MarkdownIcon
    GetFileIcon --> JsonIcon
    GetFileIcon --> FolderIcon
    GetFileIcon --> DefaultIcon
```

**Dropdown Rendering System**
Shows dropdown types, rendering logic, and file icon mapping for visual enhancement.

The dropdown renderer at [tui/src/services/helper_dropdown.rs:10-127]() provides:

- **File extension icons** using Unicode emojis
- **Trigger-specific styling** for Tab vs @ completion
- **Selection highlighting** with reversed colors
- **Dynamic sizing** based on content

Sources: [tui/src/services/helper_dropdown.rs:1-128]()

---

# Page: Shell Mode Integration

# Shell Mode Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tui/src/app.rs](tui/src/app.rs)
- [tui/src/lib.rs](tui/src/lib.rs)
- [tui/src/services/bash_block.rs](tui/src/services/bash_block.rs)
- [tui/src/services/detect_term.rs](tui/src/services/detect_term.rs)
- [tui/src/services/markdown_renderer.rs](tui/src/services/markdown_renderer.rs)
- [tui/src/services/message.rs](tui/src/services/message.rs)
- [tui/src/services/syntax_highlighter.rs](tui/src/services/syntax_highlighter.rs)
- [tui/src/services/update.rs](tui/src/services/update.rs)
- [tui/src/view.rs](tui/src/view.rs)

</details>



Shell Mode provides interactive terminal capabilities within the TUI, enabling users to execute shell commands and view their output with VT100 terminal emulation. This system supports both PTY-based execution on Unix systems and background process execution on other platforms, with real-time output streaming and interactive input handling.

For information about tool execution and MCP integration, see [Tool Container and Execution Flow](#5.2). For details on TUI event handling, see [Event Handling and User Input](#3.3).

---

## Overview and Purpose

Shell Mode serves two primary use cases:

1. **Interactive Shell Commands**: Executing commands triggered by the user (via `!` prefix) or by the agent (via tool calls) with real-time output display
2. **Shell History Display**: Rendering previously executed shell commands and their outputs in message bubbles with proper formatting

The system uses VT100 terminal emulation to accurately reproduce terminal output, including ANSI escape sequences, cursor movements, and control characters. On Unix systems, it leverages PTY (pseudo-terminal) devices for true interactive shell sessions.

Sources: [tui/src/app.rs:74-99](), [tui/src/services/message.rs:342-426]()

---

## Architecture Overview

```mermaid
graph TB
    subgraph "Shell Mode Components"
        RUN_CMD["run_shell_command()<br/>Command Spawner"]
        SHELL_CMD["ShellCommand<br/>Process Handle"]
        SHELL_EVENT["ShellEvent Enum<br/>Output/Error/Completed/Clear"]
        
        subgraph "Platform-Specific Execution"
            PTY["run_pty_command()<br/>Unix PTY-based"]
            BG["run_background_shell_command()<br/>Non-Unix Process"]
        end
        
        subgraph "Terminal Emulation"
            VT100["vt100::Parser<br/>Terminal State Machine"]
            HISTORY["shell_history_lines<br/>Accumulated Output"]
        end
        
        subgraph "Display System"
            POPUP["shell_popup::render_shell_popup()<br/>Active Command Display"]
            BUBBLE["render_shell_bubble_with_unicode_border()<br/>History Display"]
        end
    end
    
    subgraph "AppState"
        ACTIVE["active_shell_command<br/>Option<ShellCommand>"]
        OUTPUT["active_shell_command_output<br/>Option<String>"]
        SCREEN["shell_screen<br/>vt100::Parser"]
        VISIBLE["shell_popup_visible<br/>bool"]
        WAITING["waiting_for_shell_input<br/>bool"]
    end
    
    subgraph "Event Loop"
        INPUT_EVENT["InputEvent::ShellOutput<br/>InputEvent::ShellError<br/>InputEvent::ShellCompleted<br/>InputEvent::ShellClear"]
        HANDLER["update() handlers<br/>shell.rs"]
    end
    
    RUN_CMD --> PTY
    RUN_CMD --> BG
    PTY --> SHELL_CMD
    BG --> SHELL_CMD
    SHELL_CMD --> SHELL_EVENT
    SHELL_EVENT --> INPUT_EVENT
    INPUT_EVENT --> HANDLER
    HANDLER --> VT100
    VT100 --> HISTORY
    HANDLER --> ACTIVE
    HANDLER --> OUTPUT
    HANDLER --> SCREEN
    ACTIVE --> POPUP
    HISTORY --> BUBBLE
    SCREEN --> POPUP
    VISIBLE --> POPUP
    WAITING --> POPUP
```

**Diagram: Shell Mode System Architecture**

The architecture separates concerns into platform-specific execution, terminal emulation, and display layers. Commands flow through the event system, get parsed by the VT100 emulator, and are rendered either in the active shell popup or as message bubbles in history.

Sources: [tui/src/app.rs:502-560](), [tui/src/view.rs:86-171]()

---

## State Management

The TUI's `AppState` struct maintains comprehensive shell-related state across multiple subsystems:

| State Field | Type | Purpose |
|-------------|------|---------|
| `shell_popup_visible` | `bool` | Controls popup visibility |
| `shell_popup_expanded` | `bool` | Controls popup expansion state |
| `shell_popup_scroll` | `usize` | Vertical scroll position in popup |
| `shell_cursor_visible` | `bool` | Cursor visibility for blinking |
| `shell_cursor_blink_timer` | `u8` | Timer for cursor blink animation |
| `active_shell_command` | `Option<ShellCommand>` | Currently executing command handle |
| `active_shell_command_output` | `Option<String>` | Raw output buffer |
| `waiting_for_shell_input` | `bool` | Interactive input mode flag |
| `shell_screen` | `vt100::Parser` | VT100 terminal state machine |
| `shell_scroll` | `u16` | Terminal scroll position |
| `shell_history_lines` | `Vec<Line<'static>>` | Accumulated styled output lines |
| `interactive_shell_message_id` | `Option<Uuid>` | Message ID for interactive sessions |
| `shell_interaction_occurred` | `bool` | Tracks user interaction |

### Backward Compatibility State

Several fields exist for backward compatibility with older shell mode implementations:

```rust
pub show_shell_mode: bool,              // alias for shell_popup_visible && shell_popup_expanded
pub shell_mode_input: String,           // unused, kept for compatibility
pub is_tool_call_shell_command: bool,
pub ondemand_shell_mode: bool,
pub shell_pending_command: Option<String>,
```

Sources: [tui/src/app.rs:74-99](), [tui/src/app.rs:326-333]()

---

## Shell Command Execution

### Command Spawning Flow

```mermaid
sequenceDiagram
    participant User
    participant AppState
    participant run_shell_command
    participant Platform
    participant ShellEvent
    participant EventLoop
    
    User->>AppState: Trigger shell command
    AppState->>run_shell_command: command string
    run_shell_command->>Platform: Create channel<br/>mpsc::channel<ShellEvent>
    
    alt Unix Platform
        Platform->>Platform: run_pty_command()<br/>Create PTY
    else Non-Unix Platform
        Platform->>Platform: run_background_shell_command()<br/>Spawn process
    end
    
    Platform-->>run_shell_command: ShellCommand handle
    run_shell_command->>AppState: Store in active_shell_command
    run_shell_command->>AppState: Initialize shell_screen (VT100)
    run_shell_command->>EventLoop: Spawn async task
    
    loop Command Execution
        Platform->>ShellEvent: Output/Error/Clear
        ShellEvent->>EventLoop: Channel send
        EventLoop->>AppState: InputEvent::ShellOutput
        AppState->>AppState: Update VT100 parser
        AppState->>AppState: Update shell_history_lines
    end
    
    Platform->>ShellEvent: Completed(exit_code)
    ShellEvent->>EventLoop: Channel send
    EventLoop->>AppState: InputEvent::ShellCompleted
    AppState->>AppState: Clear active_shell_command
```

**Diagram: Shell Command Execution Sequence**

### Implementation Details

The `run_shell_command` method in `AppState` orchestrates command execution:

```rust
pub fn run_shell_command(&mut self, command: String, input_tx: &mpsc::Sender<InputEvent>) {
    let (shell_tx, mut shell_rx) = mpsc::channel::<ShellEvent>(100);
    
    // Add spacing markers and styled prompt
    self.messages.push(Message::plain_text("SPACING_MARKER"));
    push_styled_message(self, &command, AdaptiveColors::text(), 
                       SHELL_PROMPT_PREFIX, AdaptiveColors::dark_magenta());
    self.messages.push(Message::plain_text("SPACING_MARKER"));
    
    // Get terminal dimensions
    let rows = if self.terminal_size.height > 0 { self.terminal_size.height } else { 24 };
    let cols = if self.terminal_size.width > 0 { self.terminal_size.width } else { 80 };
```

Platform-specific execution branches:

**Unix (PTY-based)**:
```rust
#[cfg(unix)]
let shell_cmd = match run_pty_command(command.clone(), None, shell_tx, rows, cols) {
    Ok(cmd) => cmd,
    Err(e) => {
        push_error_message(self, &format!("Failed to run command: {}", e), None);
        return;
    }
};
```

**Non-Unix (Background Process)**:
```rust
#[cfg(not(unix))]
let shell_cmd = run_background_shell_command(command.clone(), shell_tx);
```

The method then stores the command handle, initializes the VT100 parser, and spawns an async task to forward shell events to the event loop.

Sources: [tui/src/app.rs:502-560](), [tui/src/app.rs:16-20]()

---

## VT100 Terminal Emulation

### VT100 Parser Integration

Shell Mode uses the `vt100` crate to accurately parse and render terminal output, handling ANSI escape sequences, cursor positioning, and control characters:

```rust
self.shell_screen = vt100::Parser::new(rows, cols, 0);
```

The parser is initialized with terminal dimensions (rows, cols) and maintains internal state for:
- Cursor position
- Character attributes (colors, styles)
- Screen buffer
- Scrollback history

### Output Processing

When shell output arrives via `InputEvent::ShellOutput`, it's processed through the VT100 parser:

1. Raw output string is fed to `shell_screen.process(bytes)`
2. Parser updates internal screen state
3. Processed output is extracted and converted to styled `Line<'static>` objects
4. Lines are appended to `shell_history_lines` for display

This approach ensures that complex terminal applications (like `vim`, `htop`, or progress bars) render correctly within the TUI.

Sources: [tui/src/app.rs:382](), [tui/src/app.rs:538]()

---

## Shell Popup Display

### Popup Rendering System

```mermaid
graph TB
    subgraph "View Layer"
        VIEW["view()<br/>Main render function"]
        CALC["calculate_popup_height()<br/>Dynamic sizing"]
        RENDER["render_shell_popup()<br/>Popup content"]
    end
    
    subgraph "Layout Calculation"
        HEIGHT["shell_popup_height<br/>Dynamic based on state"]
        INPUT_HIDE["effective_input_height<br/>0 if expanded"]
        CONSTRAINTS["Layout constraints<br/>[messages][loading][popup][input]"]
    end
    
    subgraph "Popup State"
        VISIBLE["shell_popup_visible"]
        EXPANDED["shell_popup_expanded"]
        SCROLL["shell_popup_scroll"]
    end
    
    subgraph "Content Sources"
        SCREEN["shell_screen<br/>VT100 parser state"]
        HISTORY["shell_history_lines<br/>Accumulated output"]
        ACTIVE["active_shell_command<br/>Current command"]
    end
    
    VIEW --> CALC
    CALC --> HEIGHT
    HEIGHT --> CONSTRAINTS
    VISIBLE --> RENDER
    EXPANDED --> INPUT_HIDE
    SCROLL --> RENDER
    SCREEN --> RENDER
    HISTORY --> RENDER
    ACTIVE --> RENDER
    CONSTRAINTS --> RENDER
```

**Diagram: Shell Popup Rendering Architecture**

### Layout Integration

The shell popup is positioned between the messages area and the input area, with dynamic height calculation:

```rust
// Calculate shell popup height (goes above input)
let shell_popup_height = shell_popup::calculate_popup_height(state, main_area.height);

// Hide input when shell popup is expanded (takes over input)
let effective_input_height = if state.shell_popup_visible && state.shell_popup_expanded {
    0 // Hide input when popup is expanded
} else {
    input_height
};
```

Layout constraints are arranged as:
1. Messages area (flexible)
2. Loading indicator (1 line)
3. Dialog margin/area
4. **Shell popup** (dynamic height, 0 if hidden)
5. **Input area** (hidden if popup expanded)
6. Helper dropdown
7. Hint area

When the shell popup is expanded, it effectively replaces the input area, providing a full-screen terminal experience.

### Rendering Implementation

The popup is rendered with padding in `view.rs`:

```rust
if state.shell_popup_visible && !state.show_sessions_dialog {
    let padded_shell_popup_area = Rect {
        x: shell_popup_area.x + 1,
        y: shell_popup_area.y,
        width: shell_popup_area.width.saturating_sub(2),
        height: shell_popup_area.height,
    };
    shell_popup::render_shell_popup(f, state, padded_shell_popup_area);
}
```

Sources: [tui/src/view.rs:86-171](), [tui/src/view.rs:21-46]()

---

## Event Flow and Processing

### Shell Event Types

Shell events are transmitted from the command execution layer to the TUI via `InputEvent` variants:

| Event Type | Purpose | Handling |
|------------|---------|----------|
| `InputEvent::ShellOutput(String)` | Normal output data | Feed to VT100 parser, append to history |
| `InputEvent::ShellError(String)` | Error output (stderr) | Feed to VT100 parser, append to history |
| `InputEvent::ShellCompleted(i32)` | Command finished | Clear active command, exit code |
| `InputEvent::ShellClear` | Clear screen request | Clear VT100 parser state, reset history |

### Event Forwarding Task

When a shell command is spawned, an async task forwards shell events:

```rust
let input_tx = input_tx.clone();
tokio::spawn(async move {
    while let Some(event) = shell_rx.recv().await {
        match event {
            ShellEvent::Output(line) => {
                let _ = input_tx.send(InputEvent::ShellOutput(line)).await;
            }
            ShellEvent::Error(line) => {
                let _ = input_tx.send(InputEvent::ShellError(line)).await;
            }
            ShellEvent::Completed(code) => {
                let _ = input_tx.send(InputEvent::ShellCompleted(code)).await;
                break;
            }
            ShellEvent::Clear => {
                let _ = input_tx.send(InputEvent::ShellClear).await;
            }
        }
    }
});
```

This task bridges the platform-specific shell execution layer with the TUI event loop.

Sources: [tui/src/app.rs:540-559]()

---

## Interactive Input Support

Shell Mode supports interactive commands that require user input (e.g., `sudo`, password prompts):

### Input Flow for Interactive Commands

```mermaid
sequenceDiagram
    participant User
    participant TextArea
    participant AppState
    participant ShellCommand
    participant PTY
    
    Note over AppState: waiting_for_shell_input = true
    User->>TextArea: Type input
    TextArea->>AppState: Characters entered
    AppState->>AppState: Render masked (if password)
    User->>AppState: Press Enter
    AppState->>ShellCommand: Send input to PTY
    ShellCommand->>PTY: Write to stdin
    PTY-->>ShellCommand: Command continues
    ShellCommand-->>AppState: More output events
    Note over AppState: waiting_for_shell_input = false
```

**Diagram: Interactive Input Handling Sequence**

### Password Masking

When `waiting_for_shell_input` is true, the TUI can optionally mask password input:

```rust
if state.show_shell_mode && state.waiting_for_shell_input {
    state.text_area.render_with_state(
        content_area,
        f.buffer_mut(),
        &mut state.text_area_state,
        state.waiting_for_shell_input, // Enable masking
    );
}
```

This provides a secure way to enter sensitive information within shell sessions.

Sources: [tui/src/view.rs:410-419](), [tui/src/app.rs:82]()

---

## Shell History in Message Bubbles

### History Rendering

Previously executed shell commands and their outputs are rendered as styled message bubbles in the conversation history:

```rust
fn render_shell_bubble_with_unicode_border(
    command: &str,
    output_lines: &[String],
    width: usize,
) -> Vec<Line<'static>>
```

This function creates bordered bubbles with:
- **Top border**: `╭───...───╮` with magenta color
- **Command line**: Prefixed with `SHELL_PROMPT_PREFIX`, truncated to fit
- **Output lines**: Each wrapped and truncated to fit terminal width
- **Bottom border**: `╰───...───╯` with magenta color

### Shell Block Parsing

When resuming sessions or displaying shell history, the system parses markdown shell blocks:

```markdown
Here's my shell history:
```shell
→ ls -la
total 48
drwxr-xr-x  8 user  staff  256 Jan 1 12:00 .
→ pwd
/home/user/project
```
```

The parser (`get_wrapped_message_lines_internal`) extracts commands (lines with `SHELL_PROMPT_PREFIX`) and their outputs, then renders each command-output pair as a separate bubble.

Sources: [tui/src/services/message.rs:342-426](), [tui/src/services/message.rs:673-742]()

---

## Integration Points

### Message System Integration

Shell Mode integrates with the message system through several `MessageContent` variants:

- **`RenderRefreshedTerminal`**: Displays terminal state with VT100-rendered content
- **`PlainText`**: Used for SPACING_MARKER and separators
- Shell history bubbles are added as `Styled` or `StyledBlock` messages

When `shell_popup_visible` is true, `RenderRefreshedTerminal` messages are filtered out to avoid duplicate display:

```rust
let messages: Vec<Message> = if state.shell_popup_visible {
    state.messages.iter()
        .filter(|m| !matches!(&m.content, MessageContent::RenderRefreshedTerminal(..)))
        .cloned()
        .collect()
} else {
    state.messages.clone()
};
```

### Tool Call Integration

Shell Mode is triggered by tool calls (like `run_command`) and user commands (prefixed with `!`). The system tracks whether a shell command originated from a tool call via `is_tool_call_shell_command` flag, enabling different UI treatments.

Sources: [tui/src/services/message.rs:452-464](), [tui/src/app.rs:91]()

---

## Platform-Specific Considerations

### Unix PTY Support

On Unix systems, shell commands use PTY (pseudo-terminal) devices via `run_pty_command`, enabling:
- Full terminal emulation (cursor positioning, colors)
- Interactive command support (password prompts)
- Proper signal handling (Ctrl+C, Ctrl+Z)
- Raw mode terminal access

### Non-Unix Background Process

On non-Unix systems, `run_background_shell_command` spawns background processes with:
- Separate stdout/stderr pipes
- No PTY (limited terminal emulation)
- No interactive input support
- Simple line-based output

The VT100 parser provides a consistent rendering layer across both platforms, though interactive capabilities are limited on non-Unix systems.

Sources: [tui/src/app.rs:524-534](), [tui/src/app.rs:16-19]()

---

# Page: Agent Provider and API

# Agent Provider and API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [libs/api/Cargo.toml](libs/api/Cargo.toml)
- [libs/api/src/lib.rs](libs/api/src/lib.rs)
- [libs/api/src/local/mod.rs](libs/api/src/local/mod.rs)
- [libs/api/src/models.rs](libs/api/src/models.rs)
- [libs/mcp/server/README_SECRETS.md](libs/mcp/server/README_SECRETS.md)
- [libs/shared/src/container.rs](libs/shared/src/container.rs)
- [libs/shared/src/models/integrations/mod.rs](libs/shared/src/models/integrations/mod.rs)
- [libs/shared/src/models/integrations/search_service.rs](libs/shared/src/models/integrations/search_service.rs)

</details>



This document describes the Agent Provider abstraction layer in the `stakpak-api` library, which provides a unified interface for interacting with AI agents through either remote hosted services or local LLM providers. This abstraction enables the CLI and TUI to work with different backend implementations without code changes.

For information about how the CLI uses the Agent Provider, see [CLI Interface](#2). For details about TUI integration with the provider, see [Terminal User Interface (TUI)](#3).

---

## Purpose and Architecture

The `AgentProvider` trait defines a contract for all agent interactions, including chat completions, session management, rulebook operations, and integrated services (search, memory, Slack). Two implementations provide different deployment models:

- **`RemoteClient`**: Communicates with Stakpak's hosted API service
- **`LocalClient`**: Executes agent logic locally using direct LLM integration

This abstraction allows applications to switch between cloud and local operation with a single configuration change, supporting both online collaboration and offline/air-gapped environments.

**Key Components:**
| Component | Purpose | Location |
|-----------|---------|----------|
| `AgentProvider` trait | Core abstraction with 14 async methods | `libs/api/src/lib.rs` |
| `RemoteClient` | HTTP client for hosted Stakpak API | `libs/api/src/remote/` |
| `LocalClient` | Local LLM integration with SQLite storage | `libs/api/src/local/mod.rs` |
| Data models | Session, checkpoint, message structures | `libs/api/src/models.rs` |

Sources: [libs/api/src/lib.rs:1-93](), [libs/api/src/local/mod.rs:42-50]()

---

## AgentProvider Trait Definition

The `AgentProvider` trait defines 14 async methods grouped into six functional categories. All implementations must provide these methods, ensuring consistent behavior across deployment modes.

### AgentProvider Method Categories

```mermaid
graph TB
    subgraph "AgentProvider Trait"
        TRAIT["AgentProvider<br/>14 async methods"]
        
        subgraph "Account Management"
            ACC1["get_my_account()<br/>→ GetMyAccountResponse"]
            ACC2["get_billing_info(username)<br/>→ BillingResponse"]
        end
        
        subgraph "Rulebook Management"
            RB1["list_rulebooks()<br/>→ Vec&lt;ListRuleBook&gt;"]
            RB2["get_rulebook_by_uri(uri)<br/>→ RuleBook"]
            RB3["create_rulebook(...)<br/>→ CreateRuleBookResponse"]
            RB4["delete_rulebook(uri)<br/>→ ()"]
        end
        
        subgraph "Session Management"
            SESS1["list_agent_sessions()<br/>→ Vec&lt;AgentSession&gt;"]
            SESS2["get_agent_session(id)<br/>→ AgentSession"]
            SESS3["get_agent_session_stats(id)<br/>→ AgentSessionStats"]
            SESS4["get_agent_checkpoint(id)<br/>→ RunAgentOutput"]
            SESS5["get_agent_session_latest_checkpoint(id)<br/>→ RunAgentOutput"]
        end
        
        subgraph "Chat Operations"
            CHAT1["chat_completion(model, messages, tools)<br/>→ ChatCompletionResponse"]
            CHAT2["chat_completion_stream(model, messages, tools, headers)<br/>→ Stream&lt;ChatCompletionStreamResponse&gt;"]
            CHAT3["cancel_stream(request_id)<br/>→ ()"]
        end
        
        subgraph "Search & Memory"
            SEARCH1["search_docs(input)<br/>→ Vec&lt;Content&gt;"]
            SEARCH2["search_memory(input)<br/>→ Vec&lt;Content&gt;"]
            SEARCH3["memorize_session(checkpoint_id)<br/>→ ()"]
        end
        
        subgraph "Slack Integration"
            SLACK1["slack_read_messages(input)<br/>→ Vec&lt;Content&gt;"]
            SLACK2["slack_read_replies(input)<br/>→ Vec&lt;Content&gt;"]
            SLACK3["slack_send_message(input)<br/>→ Vec&lt;Content&gt;"]
        end
    end
    
    TRAIT --> ACC1
    TRAIT --> ACC2
    TRAIT --> RB1
    TRAIT --> RB2
    TRAIT --> RB3
    TRAIT --> RB4
    TRAIT --> SESS1
    TRAIT --> SESS2
    TRAIT --> SESS3
    TRAIT --> SESS4
    TRAIT --> SESS5
    TRAIT --> CHAT1
    TRAIT --> CHAT2
    TRAIT --> CHAT3
    TRAIT --> SEARCH1
    TRAIT --> SEARCH2
    TRAIT --> SEARCH3
    TRAIT --> SLACK1
    TRAIT --> SLACK2
    TRAIT --> SLACK3
```

### Method Signatures

| Category | Method | Input Types | Return Type |
|----------|--------|-------------|-------------|
| **Account** | `get_my_account` | None | `GetMyAccountResponse` |
| | `get_billing_info` | `&str` (username) | `BillingResponse` |
| **Rulebooks** | `list_rulebooks` | None | `Vec<ListRuleBook>` |
| | `get_rulebook_by_uri` | `&str` (uri) | `RuleBook` |
| | `create_rulebook` | `&str, &str, &str, Vec<String>, Option<RuleBookVisibility>` | `CreateRuleBookResponse` |
| | `delete_rulebook` | `&str` (uri) | `()` |
| **Sessions** | `list_agent_sessions` | None | `Vec<AgentSession>` |
| | `get_agent_session` | `Uuid` (session_id) | `AgentSession` |
| | `get_agent_session_stats` | `Uuid` (session_id) | `AgentSessionStats` |
| | `get_agent_checkpoint` | `Uuid` (checkpoint_id) | `RunAgentOutput` |
| | `get_agent_session_latest_checkpoint` | `Uuid` (session_id) | `RunAgentOutput` |
| **Chat** | `chat_completion` | `AgentModel, Vec<ChatMessage>, Option<Vec<Tool>>` | `ChatCompletionResponse` |
| | `chat_completion_stream` | `AgentModel, Vec<ChatMessage>, Option<Vec<Tool>>, Option<HeaderMap>` | `(Pin<Box<Stream>>, Option<String>)` |
| | `cancel_stream` | `String` (request_id) | `()` |
| **Search/Memory** | `search_docs` | `&SearchDocsRequest` | `Vec<Content>` |
| | `search_memory` | `&SearchMemoryRequest` | `Vec<Content>` |
| | `memorize_session` | `Uuid` (checkpoint_id) | `()` |
| **Slack** | `slack_read_messages` | `&SlackReadMessagesRequest` | `Vec<Content>` |
| | `slack_read_replies` | `&SlackReadRepliesRequest` | `Vec<Content>` |
| | `slack_send_message` | `&SlackSendMessageRequest` | `Vec<Content>` |

Sources: [libs/api/src/lib.rs:16-92]()

---

## Core Data Models

The API uses strongly-typed models to represent sessions, checkpoints, messages, and configuration. These types are shared between both implementations.

### Session and Checkpoint Structures

```mermaid
graph TB
    subgraph "Session Hierarchy"
        AS["AgentSession<br/>id: Uuid<br/>title: String<br/>agent_id: AgentID<br/>visibility: AgentSessionVisibility<br/>checkpoints: Vec&lt;AgentCheckpointListItem&gt;<br/>created_at: DateTime&lt;Utc&gt;<br/>updated_at: DateTime&lt;Utc&gt;"]
        
        CHECKPOINT["AgentCheckpointListItem<br/>id: Uuid<br/>status: AgentStatus<br/>execution_depth: usize<br/>parent: Option&lt;AgentParentCheckpoint&gt;<br/>created_at: DateTime&lt;Utc&gt;<br/>updated_at: DateTime&lt;Utc&gt;"]
        
        OUTPUT["RunAgentOutput<br/>checkpoint: AgentCheckpointListItem<br/>session: AgentSessionListItem<br/>output: AgentOutput"]
        
        AGENT_OUTPUT["AgentOutput::PabloV1<br/>messages: Vec&lt;ChatMessage&gt;<br/>node_states: serde_json::Value"]
    end
    
    AS -->|"contains"| CHECKPOINT
    OUTPUT -->|"wraps"| CHECKPOINT
    OUTPUT -->|"contains"| AGENT_OUTPUT
    
    subgraph "Enumerations"
        STATUS["AgentStatus<br/>RUNNING | COMPLETE<br/>BLOCKED | FAILED"]
        VIS["AgentSessionVisibility<br/>PRIVATE | PUBLIC"]
        AID["AgentID<br/>PabloV1"]
    end
    
    AS --> VIS
    AS --> AID
    CHECKPOINT --> STATUS
```

### Key Model Types

**`AgentSession`** [libs/api/src/models.rs:66-74]()
- Represents a persistent conversation session
- Contains collection of checkpoint snapshots
- Tracks title, agent type, visibility, timestamps

**`AgentCheckpointListItem`** [libs/api/src/models.rs:112-119]()
- Immutable snapshot of agent state at a point in time
- Forms a tree structure via parent references
- Tracks execution depth for nested agent calls

**`RunAgentOutput`** [libs/api/src/models.rs:181-185]()
- Returned from checkpoint operations
- Bundles checkpoint metadata with agent output state
- Used as return type for checkpoint retrieval methods

**`AgentOutput`** [libs/api/src/models.rs:228-254]()
- Tagged enum for agent-specific output formats
- `PabloV1` variant contains messages and node states
- Provides methods to access/modify message history

**`AgentState`** [libs/api/src/models.rs:654-763]()
- Working state during agent execution
- Tracks input/output LLM interactions
- Used by hooks and local client for processing

Sources: [libs/api/src/models.rs:66-254](), [libs/api/src/models.rs:654-763]()

---

## RemoteClient Implementation

The `RemoteClient` provides a thin HTTP client wrapper over the Stakpak hosted API. It requires an API key for authentication and sends all requests to the remote service.

### RemoteClient Architecture

```mermaid
graph TB
    subgraph "Application Layer"
        CLI["CLI / TUI Application"]
    end
    
    subgraph "RemoteClient Structure"
        RC["RemoteClient<br/>base_url: String<br/>http_client: ClientWithMiddleware"]
        
        subgraph "HTTP Layer"
            TLS["TlsClientConfig<br/>with_timeout(300s)"]
            RETRY["RetryTransientMiddleware<br/>Exponential backoff"]
        end
        
        subgraph "API Methods"
            GET["GET requests<br/>/v1/account<br/>/v1/sessions<br/>/v1/rules"]
            POST["POST requests<br/>/v1/chat/completions<br/>/v1/tools/*"]
            STREAM["SSE streaming<br/>/v1/chat/completions (stream=true)"]
        end
    end
    
    subgraph "Stakpak Backend API"
        API["api.stakpak.dev<br/>Hosted Service"]
    end
    
    CLI -->|"uses"| RC
    RC -->|"configures"| TLS
    RC -->|"configures"| RETRY
    RC -->|"calls"| GET
    RC -->|"calls"| POST
    RC -->|"calls"| STREAM
    
    GET --> API
    POST --> API
    STREAM --> API
```

### Configuration

The `RemoteClient` requires:
- **Base URL**: Typically `https://api.stakpak.dev/v1`
- **API Key**: Passed via `X-API-Key` header
- **Timeout**: Default 300 seconds for long-running operations

### Request Flow

1. Client method called with parameters
2. Serialize request to JSON
3. Add authentication headers
4. Send HTTP request with retry middleware
5. Parse response or handle streaming
6. Deserialize to typed model
7. Return result or error

For streaming operations, the client returns a `Stream<ChatCompletionStreamResponse>` using Server-Sent Events (SSE) parsing.

Sources: [libs/api/src/lib.rs:1-93](), [libs/api/src/local/mod.rs:210-242]()

---

## LocalClient Implementation

The `LocalClient` provides a fully self-contained agent execution environment without requiring external API access. It integrates multiple components for LLM communication, session persistence, and service orchestration.

### LocalClient Structure and Components

```mermaid
graph TB
    subgraph "LocalClient Components"
        LC["LocalClient<br/>db: Connection<br/>stakpak_base_url: Option&lt;String&gt;<br/>providers: LLMProviderConfig<br/>model_options: ModelOptions<br/>hook_registry: Option&lt;Arc&lt;HookRegistry&gt;&gt;<br/>_search_services_orchestrator: Option&lt;Arc&lt;SearchServicesOrchestrator&gt;&gt;"]
        
        subgraph "Storage Layer"
            LIBSQL["libsql Connection<br/>~/.stakpak/data/local.db"]
            SCHEMA["Database Schema<br/>sessions table<br/>checkpoints table<br/>metadata table"]
        end
        
        subgraph "LLM Integration"
            STAKAI["StakAIClient<br/>Unified LLM adapter"]
            PROVIDERS["LLM Providers<br/>OpenAI<br/>Anthropic<br/>Google Gemini<br/>AWS Bedrock"]
        end
        
        subgraph "Model Configuration"
            MODELS["ModelOptions<br/>smart_model: Option&lt;LLMModel&gt;<br/>eco_model: Option&lt;LLMModel&gt;<br/>recovery_model: Option&lt;LLMModel&gt;"]
            MODELSET["ModelSet<br/>Resolved models with defaults"]
        end
        
        subgraph "Hook System"
            HOOKS["HookRegistry&lt;AgentState&gt;<br/>BeforeRequest<br/>BeforeInference<br/>AfterInference<br/>AfterRequest"]
            SCRATCHPAD["InlineScratchpadContextHook<br/>Context management"]
        end
        
        subgraph "Search Services"
            SEARCH_ORCH["SearchServicesOrchestrator<br/>Docker container management"]
            SEARXNG["SearXNG Container<br/>Web search engine"]
            SEARCH_CLIENT["SearchClient<br/>HTTP client for search API"]
        end
    end
    
    LC --> LIBSQL
    LC --> STAKAI
    LC --> MODELS
    LC --> HOOKS
    LC --> SEARCH_ORCH
    
    LIBSQL --> SCHEMA
    STAKAI --> PROVIDERS
    MODELS --> MODELSET
    HOOKS --> SCRATCHPAD
    SEARCH_ORCH --> SEARXNG
    SEARCH_ORCH --> SEARCH_CLIENT
```

### LocalClient Configuration

**`LocalClientConfig`** [libs/api/src/local/mod.rs:100-108]()
```rust
pub struct LocalClientConfig {
    pub stakpak_base_url: Option<String>,  // For rulebook API only
    pub store_path: Option<String>,         // SQLite DB path
    pub providers: LLMProviderConfig,       // LLM credentials
    pub smart_model: Option<String>,        // High-capability model
    pub eco_model: Option<String>,          // Cost-efficient model
    pub recovery_model: Option<String>,     // Fallback model
    pub hook_registry: Option<HookRegistry<AgentState>>,
}
```

### Initialization Sequence

1. **Database Setup** [libs/api/src/local/mod.rs:119-143]()
   - Resolve store path (default: `~/.stakpak/data/local.db`)
   - Create parent directories if needed
   - Open libsql connection
   - Initialize schema via `db::init_schema()`

2. **Model Configuration** [libs/api/src/local/mod.rs:145-149]()
   - Parse model strings to `LLMModel` enum
   - Store as `ModelOptions` with optional values
   - Defaults applied later: Claude 4.5 Sonnet (smart), Haiku (eco), GPT-5 (recovery)

3. **Hook Registration** [libs/api/src/local/mod.rs:152-177]()
   - Register `InlineScratchpadContextHook` for context management
   - Hook executes before inference to prepare LLM input
   - Options control history truncation and action logging

4. **Service Orchestration** [libs/api/src/local/mod.rs:185]()
   - Initialize `SearchServicesOrchestrator` (lazy Docker startup)
   - Search service starts on first `search_docs()` call

Sources: [libs/api/src/local/mod.rs:42-187]()

---

## Session Management in LocalClient

The `LocalClient` maintains session state in SQLite, enabling session resumption and checkpoint navigation.

### Database Schema

```mermaid
erDiagram
    sessions ||--o{ checkpoints : contains
    
    sessions {
        TEXT id PK
        TEXT title
        TEXT agent_id
        TEXT visibility
        TEXT created_at
        TEXT updated_at
    }
    
    checkpoints {
        TEXT id PK
        TEXT session_id FK
        TEXT status
        INTEGER execution_depth
        TEXT parent_id FK
        TEXT output_json
        TEXT created_at
        TEXT updated_at
    }
```

**Tables:**
- `sessions`: Top-level conversation containers
- `checkpoints`: Immutable state snapshots with parent references
- Both use TEXT for UUIDs and timestamps (ISO 8601 format)

### Session Lifecycle

**1. Initialize Session** [libs/api/src/local/mod.rs:735-788]()
```
Input: Vec<ChatMessage>
↓
Extract checkpoint_id from last assistant message
├─ If checkpoint_id exists:
│  └─ Load existing checkpoint from DB
└─ If new session:
   ├─ Generate session title via LLM
   ├─ Create AgentSession record
   ├─ Create root checkpoint (depth 0)
   └─ Return initial RunAgentOutput
```

**2. Execute Agent Turn** [libs/api/src/local/mod.rs:656-733]()
```
HookRegistry::execute(BeforeInference)
↓
Run LLM inference (chat or chat_stream)
↓
HookRegistry::execute(AfterInference)
↓
Return new ChatMessage
```

**3. Update Session** [libs/api/src/local/mod.rs:790-823]()
```
Input: Current checkpoint, new messages
↓
Create new checkpoint:
├─ Increment execution_depth
├─ Set parent reference
├─ Serialize updated AgentOutput
└─ Insert into checkpoints table
↓
Return new RunAgentOutput
```

Sources: [libs/api/src/local/mod.rs:656-823]()

---

## Chat Completion Methods

Both `chat_completion` and `chat_completion_stream` follow similar flows with different output handling.

### Non-Streaming Flow

```mermaid
sequenceDiagram
    participant App as "Application"
    participant LC as "LocalClient"
    participant HR as "HookRegistry"
    participant SAI as "StakAIClient"
    participant DB as "SQLite DB"
    participant LLM as "LLM Provider"
    
    App->>LC: chat_completion(model, messages, tools)
    LC->>LC: Create HookContext with AgentState
    LC->>HR: execute_hooks(BeforeRequest)
    HR-->>LC: Ok
    
    LC->>LC: initialize_session(messages)
    LC->>DB: Check for existing checkpoint
    alt New Session
        DB-->>LC: None
        LC->>SAI: Generate title
        SAI->>LLM: LLM inference
        LLM-->>SAI: Title
        SAI-->>LC: Title
        LC->>DB: Create session + root checkpoint
    else Existing Session
        DB-->>LC: Checkpoint data
    end
    
    LC->>HR: execute_hooks(BeforeInference)
    HR->>HR: InlineScratchpadContextHook
    HR-->>LC: Modified context (LLMInput prepared)
    
    LC->>SAI: chat(LLMInput)
    SAI->>LLM: API request
    LLM-->>SAI: Response
    SAI-->>LC: ChatMessage + usage
    
    LC->>LC: ctx.state.set_llm_output()
    LC->>HR: execute_hooks(AfterInference)
    HR-->>LC: Ok
    
    LC->>LC: update_session(messages + new_message)
    LC->>DB: Create new checkpoint
    DB-->>LC: checkpoint_id
    
    LC->>HR: execute_hooks(AfterRequest)
    HR-->>LC: Ok
    
    LC-->>App: ChatCompletionResponse
```

### Streaming Flow Differences

**Channel-Based Architecture** [libs/api/src/local/mod.rs:410-463]()
1. Create `mpsc::channel<StreamMessage>` for deltas
2. Spawn background task for agent execution
3. Return stream immediately to caller
4. Background task sends deltas as they arrive
5. Final checkpoint ID streamed at completion

**StreamMessage Types** [libs/api/src/local/mod.rs:111-114]()
- `Delta(GenerationDelta)`: Token/content updates from LLM
- `Ctx(Box<HookContext<AgentState>>)`: State updates

Sources: [libs/api/src/local/mod.rs:320-503]()

---

## Hook System Integration

The `HookRegistry` provides lifecycle events for extending agent behavior. The `LocalClient` uses hooks to manage context and prepare LLM inputs.

### Lifecycle Events

```mermaid
graph LR
    BR["BeforeRequest<br/>Initial setup"]
    BI["BeforeInference<br/>Prepare LLM input"]
    AI["AfterInference<br/>Process output"]
    AR["AfterRequest<br/>Final cleanup"]
    
    BR --> BI --> AI --> AR
    
    subgraph "Registered Hooks"
        ISC["InlineScratchpadContextHook<br/>Truncates history<br/>Prepares LLMInput<br/>Formats tools"]
    end
    
    BI -.->|"executes"| ISC
```

**`InlineScratchpadContextHook`** [libs/api/src/local/mod.rs:153-163]()
- Registered for `BeforeInference` event
- Options:
  - `history_action_message_size_limit: Some(100)` - Max chars per action message
  - `history_action_message_keep_last_n: Some(1)` - Keep only last action message
  - `history_action_result_keep_last_n: Some(50)` - Keep last 50 results
- Converts `ChatMessage` to `LLMInput` format
- Applies model-specific formatting

Sources: [libs/api/src/local/mod.rs:4-6](), [libs/api/src/local/mod.rs:153-163]()

---

## Search Services Integration

The `LocalClient` provides web search capabilities through a Docker-based architecture using SearXNG.

### SearchServicesOrchestrator Architecture

```mermaid
graph TB
    subgraph "LocalClient Context"
        LC["LocalClient<br/>search_docs(keywords)"]
    end
    
    subgraph "SearchServicesOrchestrator"
        ORCH["SearchServicesOrchestrator::start()"]
        CHECK["Check existing config<br/>~/.stakpak/session/search_config.json"]
        HEALTH["Health check existing container"]
        
        subgraph "Docker Management"
            IMAGE["Ensure image exists<br/>ghcr.io/stakpak/local_search:0.3"]
            RUN["Run container detached<br/>Port: 0:8000<br/>Env: SEARXNG_SECRET, PORT"]
            PORT["Get host port mapping"]
        end
        
        CONFIG["SearchConfig<br/>api_port: u16<br/>api_container_id: String"]
    end
    
    subgraph "Docker Container"
        CONTAINER["local_search:0.3<br/>SearXNG + Scraping API<br/>Port 8000 (internal)"]
    end
    
    subgraph "Search Execution"
        CLIENT["SearchClient<br/>http://localhost:{port}"]
        ANALYZE["analyze_search_query()<br/>LLM-based query optimization"]
        VALIDATE["validate_search_docs()<br/>LLM-based result validation"]
        LOOP["Iterative refinement<br/>Max 3 iterations"]
    end
    
    LC --> ORCH
    ORCH --> CHECK
    CHECK --> HEALTH
    HEALTH -->|"Unhealthy"| IMAGE
    HEALTH -->|"Healthy"| CONFIG
    IMAGE --> RUN
    RUN --> PORT
    PORT --> CONFIG
    
    CONFIG --> CLIENT
    LC --> ANALYZE
    ANALYZE --> CLIENT
    CLIENT --> CONTAINER
    CONTAINER --> VALIDATE
    VALIDATE -->|"Not satisfied"| LOOP
    LOOP --> CLIENT
    VALIDATE -->|"Satisfied"| LC
```

### Search Flow

**Step 1: Service Startup** [libs/shared/src/models/integrations/search_service.rs:235-307]()
```
SearchServicesOrchestrator::start()
├─ Load config from ~/.stakpak/session/search_config.json
├─ If exists: health check at http://localhost:{port}/health
├─ If unhealthy or missing:
│  ├─ Check docker available
│  ├─ Ensure image exists locally (ghcr.io/stakpak/local_search:0.3)
│  ├─ Run container with:
│  │  ├─ Random host port mapping (0:8000)
│  │  ├─ Environment: SEARXNG_SECRET, PORT, SEARXNG_BASE_URL
│  │  └─ Extra host: host.docker.internal:host-gateway
│  ├─ Get actual host port
│  └─ Save config to session file
└─ Return SearchConfig
```

**Step 2: Query Analysis** [libs/api/src/local/mod.rs:877-953]()
```
analyze_search_query(query)
├─ Send query to LLM with system prompt
├─ LLM identifies required documentation types
├─ LLM reformulates query for search engines
└─ Parse XML response → AnalysisResult
```

**Step 3: Iterative Search** [libs/api/src/local/mod.rs:545-599]()
```
for iteration in 0..3:
    ├─ SearchClient::search_and_scrape(current_query)
    ├─ validate_search_docs(results, required_docs, previous_queries)
    │  ├─ LLM evaluates result relevance
    │  ├─ Identifies valid docs
    │  ├─ Suggests missing URLs
    │  └─ Generates new query if unsatisfied
    ├─ Accumulate valid docs
    ├─ If satisfied: break
    └─ If new_query: update current_query and continue
```

**Step 4: Result Processing** [libs/api/src/local/mod.rs:605-613]()
```
Convert ScrapedContent to Vec<Content>
Format: "URL: {url}\nContent: {content}"
```

### SearchClient HTTP API

| Endpoint | Method | Request | Response |
|----------|--------|---------|----------|
| `/search` | POST | `SearchRequest` | `Vec<SearchResult>` |
| `/scrape` | POST | `ScrapeRequest` | `Vec<ScrapedContent>` |
| `/search-and-scrape` | POST | `SearchAndScrapeRequest` | `Vec<ScrapedContent>` |
| `/health` | GET | None | Status 200 |

Sources: [libs/api/src/local/mod.rs:509-614](), [libs/shared/src/models/integrations/search_service.rs:119-229](), [libs/shared/src/models/integrations/search_service.rs:234-415]()

---

## Configuration Examples

### Remote Client Configuration

```rust
use stakpak_api::remote::RemoteClient;

let client = RemoteClient::new(
    "https://api.stakpak.dev".to_string(),
    "sk_your_api_key".to_string(),
).await?;
```

### Local Client Configuration

```rust
use stakpak_api::local::{LocalClient, LocalClientConfig};
use stakpak_shared::models::llm::LLMProviderConfig;

let mut providers = LLMProviderConfig::new();
providers.add_provider("openai", openai_api_key);
providers.add_provider("anthropic", anthropic_api_key);

let config = LocalClientConfig {
    stakpak_base_url: Some("https://api.stakpak.dev".to_string()),
    store_path: Some("~/.stakpak/data/local.db".to_string()),
    providers,
    smart_model: Some("claude-4.5-sonnet".to_string()),
    eco_model: Some("claude-4.5-haiku".to_string()),
    recovery_model: Some("gpt-5".to_string()),
    hook_registry: None,
};

let client = LocalClient::new(config).await?;
```

### Model Options Defaults

| Option | Default | Purpose |
|--------|---------|---------|
| `smart_model` | `Claude 4.5 Sonnet` | High-capability reasoning tasks |
| `eco_model` | `Claude 4.5 Haiku` | Cost-efficient operations (titles, validation) |
| `recovery_model` | `GPT-5` | Fallback when primary models fail |

Sources: [libs/api/src/local/mod.rs:78-98]()

---

## Error Handling

Both implementations return `Result<T, String>` for all operations. Common error scenarios:

**RemoteClient Errors:**
- Network timeouts (after 300s)
- Authentication failures (invalid API key)
- Rate limiting (429 status)
- API errors (4xx/5xx responses)

**LocalClient Errors:**
- Database errors (connection, schema, queries)
- LLM provider errors (API failures, quota exceeded)
- Docker errors (image missing, container startup failure)
- Hook execution errors (propagated from hook registry)

**ApiStreamError Variants** [libs/api/src/models.rs:16-26]()
- `AgentInputInvalid(String)`: Invalid request parameters
- `AgentStateInvalid`: Corrupted session state
- `AgentExecutionLimitExceeded`: Too many iterations
- `AgentInvalidResponseStream`: Malformed SSE stream
- `Unknown(String)`: Catch-all for unexpected errors

Sources: [libs/api/src/models.rs:15-63]()

---

# Page: AgentProvider Trait

# AgentProvider Trait

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [libs/api/Cargo.toml](libs/api/Cargo.toml)
- [libs/api/src/lib.rs](libs/api/src/lib.rs)
- [libs/api/src/models.rs](libs/api/src/models.rs)
- [libs/mcp/server/README_SECRETS.md](libs/mcp/server/README_SECRETS.md)

</details>



## Purpose and Scope

The `AgentProvider` trait is the core abstraction in the `stakpak-api` library that defines a unified interface for interacting with AI agent capabilities. It provides 20 async methods organized into 6 functional categories, enabling both remote (hosted Stakpak API) and local (direct LLM) implementations without requiring client code changes.

This document covers the trait definition, method signatures, and data models. For details on the remote implementation, see [Remote Client Implementation](#4.2). For the local implementation, see [Local Client Implementation](#4.3). For data model details, see [Data Models and Types](#4.4).

**Sources:** [libs/api/src/lib.rs:1-93]()

## Trait Definition and Structure

The `AgentProvider` trait is defined with the `async_trait` macro to support asynchronous operations across both remote HTTP calls and local LLM interactions. It requires implementations to be `Send + Sync` for safe concurrent usage.

```rust
#[async_trait]
pub trait AgentProvider: Send + Sync {
    // 20 async methods grouped into 6 categories
}
```

### Trait Method Overview

```mermaid
graph TB
    subgraph "AgentProvider Trait"
        TRAIT["AgentProvider<br/>(async_trait)"]
        
        subgraph "Account Management (2)"
            M1["get_my_account()<br/>→ GetMyAccountResponse"]
            M2["get_billing_info(username)<br/>→ BillingResponse"]
        end
        
        subgraph "Rulebook Management (4)"
            M3["list_rulebooks()<br/>→ Vec&lt;ListRuleBook&gt;"]
            M4["get_rulebook_by_uri(uri)<br/>→ RuleBook"]
            M5["create_rulebook(...)<br/>→ CreateRuleBookResponse"]
            M6["delete_rulebook(uri)<br/>→ ()"]
        end
        
        subgraph "Session Management (5)"
            M7["list_agent_sessions()<br/>→ Vec&lt;AgentSession&gt;"]
            M8["get_agent_session(session_id)<br/>→ AgentSession"]
            M9["get_agent_session_stats(session_id)<br/>→ AgentSessionStats"]
            M10["get_agent_checkpoint(checkpoint_id)<br/>→ RunAgentOutput"]
            M11["get_agent_session_latest_checkpoint(session_id)<br/>→ RunAgentOutput"]
        end
        
        subgraph "Chat Operations (3)"
            M12["chat_completion(model, messages, tools)<br/>→ ChatCompletionResponse"]
            M13["chat_completion_stream(model, messages, tools, headers)<br/>→ Stream&lt;ChatCompletionStreamResponse&gt;"]
            M14["cancel_stream(request_id)<br/>→ ()"]
        end
        
        subgraph "Search & Document (1)"
            M15["search_docs(input)<br/>→ Vec&lt;Content&gt;"]
        end
        
        subgraph "Memory Management (2)"
            M16["memorize_session(checkpoint_id)<br/>→ ()"]
            M17["search_memory(input)<br/>→ Vec&lt;Content&gt;"]
        end
        
        subgraph "Slack Integration (3)"
            M18["slack_read_messages(input)<br/>→ Vec&lt;Content&gt;"]
            M19["slack_read_replies(input)<br/>→ Vec&lt;Content&gt;"]
            M20["slack_send_message(input)<br/>→ Vec&lt;Content&gt;"]
        end
        
        TRAIT --> M1
        TRAIT --> M2
        TRAIT --> M3
        TRAIT --> M4
        TRAIT --> M5
        TRAIT --> M6
        TRAIT --> M7
        TRAIT --> M8
        TRAIT --> M9
        TRAIT --> M10
        TRAIT --> M11
        TRAIT --> M12
        TRAIT --> M13
        TRAIT --> M14
        TRAIT --> M15
        TRAIT --> M16
        TRAIT --> M17
        TRAIT --> M18
        TRAIT --> M19
        TRAIT --> M20
    end
```

**Sources:** [libs/api/src/lib.rs:16-92]()

## Method Categories

### Account Management

These methods provide access to account information and billing details.

| Method | Signature | Purpose |
|--------|-----------|---------|
| `get_my_account` | `async fn() -> Result<GetMyAccountResponse, String>` | Retrieves current user account details (username, email, name, scope) |
| `get_billing_info` | `async fn(account_username: &str) -> Result<BillingResponse, String>` | Retrieves billing information for a specific account |

```mermaid
graph LR
    CLIENT["Client Code"]
    TRAIT["AgentProvider"]
    ACCOUNT_DATA["GetMyAccountResponse<br/>{username, id, email,<br/>first_name, last_name, scope}"]
    BILLING_DATA["BillingResponse<br/>(stakpak_shared)"]
    
    CLIENT -->|"get_my_account()"| TRAIT
    TRAIT -->|"Result&lt;T, String&gt;"| ACCOUNT_DATA
    
    CLIENT -->|"get_billing_info(username)"| TRAIT
    TRAIT -->|"Result&lt;T, String&gt;"| BILLING_DATA
```

**Sources:** [libs/api/src/lib.rs:18-23](), [libs/api/src/models.rs:538-554]()

### Rulebook Management

Rulebooks are reusable policy documents, SOPs, or context that can be injected into agent prompts. These methods manage their lifecycle.

| Method | Signature | Purpose |
|--------|-----------|---------|
| `list_rulebooks` | `async fn() -> Result<Vec<ListRuleBook>, String>` | Lists all available rulebooks with metadata |
| `get_rulebook_by_uri` | `async fn(uri: &str) -> Result<RuleBook, String>` | Retrieves full rulebook content by URI |
| `create_rulebook` | `async fn(uri, description, content, tags, visibility) -> Result<CreateRuleBookResponse, String>` | Creates a new rulebook |
| `delete_rulebook` | `async fn(uri: &str) -> Result<(), String>` | Deletes a rulebook by URI |

The `RuleBookVisibility` enum supports `Public` or `Private` visibility levels.

**Sources:** [libs/api/src/lib.rs:25-36](), [libs/api/src/models.rs:494-596]()

### Session Management

Agent sessions represent conversation contexts with checkpoints for state persistence. These methods manage session lifecycle and state retrieval.

| Method | Signature | Purpose |
|--------|-----------|---------|
| `list_agent_sessions` | `async fn() -> Result<Vec<AgentSession>, String>` | Lists all agent sessions for the user |
| `get_agent_session` | `async fn(session_id: Uuid) -> Result<AgentSession, String>` | Retrieves full session details including checkpoints |
| `get_agent_session_stats` | `async fn(session_id: Uuid) -> Result<AgentSessionStats, String>` | Retrieves statistics (tool usage, time saved, etc.) |
| `get_agent_checkpoint` | `async fn(checkpoint_id: Uuid) -> Result<RunAgentOutput, String>` | Retrieves a specific checkpoint state |
| `get_agent_session_latest_checkpoint` | `async fn(session_id: Uuid) -> Result<RunAgentOutput, String>` | Retrieves the most recent checkpoint for a session |

```mermaid
graph TB
    SESSION["AgentSession<br/>{id, title, agent_id,<br/>visibility, checkpoints[],<br/>created_at, updated_at}"]
    
    CHECKPOINT["AgentCheckpointListItem<br/>{id, status, execution_depth,<br/>parent, created_at, updated_at}"]
    
    OUTPUT["RunAgentOutput<br/>{checkpoint, session, output}"]
    
    AGENT_OUTPUT["AgentOutput::PabloV1<br/>{messages, node_states}"]
    
    STATS["AgentSessionStats<br/>{tool_calls, time_saved,<br/>tools_usage[]}"]
    
    SESSION -->|"contains Vec&lt;&gt;"| CHECKPOINT
    OUTPUT -->|"contains"| CHECKPOINT
    OUTPUT -->|"contains"| AGENT_OUTPUT
    SESSION -->|"stats for"| STATS
```

**Sources:** [libs/api/src/lib.rs:38-46](), [libs/api/src/models.rs:65-255](), [libs/api/src/models.rs:462-492]()

### Chat Operations

These methods provide direct access to LLM chat completion capabilities with support for tool calling and streaming responses.

| Method | Signature | Purpose |
|--------|-----------|---------|
| `chat_completion` | `async fn(model, messages, tools) -> Result<ChatCompletionResponse, String>` | Performs a single chat completion call |
| `chat_completion_stream` | `async fn(model, messages, tools, headers) -> Result<(Stream, Option<String>), String>` | Performs a streaming chat completion, returns stream and optional request_id |
| `cancel_stream` | `async fn(request_id: String) -> Result<(), String>` | Cancels an active streaming request |

The streaming method returns a `Pin<Box<dyn Stream<Item = Result<ChatCompletionStreamResponse, ApiStreamError>> + Send>>`, allowing for real-time token consumption.

```mermaid
graph TB
    CHAT_IN["Chat Input"]
    MODEL["AgentModel<br/>(from stakpak_shared)"]
    MESSAGES["Vec&lt;ChatMessage&gt;<br/>{role, content, tool_calls, etc.}"]
    TOOLS["Option&lt;Vec&lt;Tool&gt;&gt;"]
    
    CHAT_COMP["chat_completion()"]
    CHAT_STREAM["chat_completion_stream()"]
    
    RESPONSE["ChatCompletionResponse<br/>(non-streaming)"]
    STREAM["Stream&lt;ChatCompletionStreamResponse&gt;<br/>+ request_id"]
    
    ERROR["ApiStreamError<br/>{AgentInputInvalid, AgentStateInvalid,<br/>AgentExecutionLimitExceeded, etc.}"]
    
    MODEL --> CHAT_IN
    MESSAGES --> CHAT_IN
    TOOLS --> CHAT_IN
    
    CHAT_IN --> CHAT_COMP
    CHAT_IN --> CHAT_STREAM
    
    CHAT_COMP --> RESPONSE
    CHAT_STREAM --> STREAM
    STREAM -->|"Item = Result&lt;T, E&gt;"| ERROR
```

**Sources:** [libs/api/src/lib.rs:48-70](), [libs/api/src/models.rs:15-63]()

### Search and Memory

These methods provide access to document search capabilities and conversation memory management.

| Method | Signature | Purpose |
|--------|-----------|---------|
| `search_docs` | `async fn(input: &SearchDocsRequest) -> Result<Vec<Content>, String>` | Searches documentation with keywords and filters |
| `memorize_session` | `async fn(checkpoint_id: Uuid) -> Result<(), String>` | Stores a checkpoint in long-term memory for later retrieval |
| `search_memory` | `async fn(input: &SearchMemoryRequest) -> Result<Vec<Content>, String>` | Searches previously memorized sessions by keywords and time range |

The `Content` type comes from the `rmcp` (Remote Model Context Protocol) crate and represents structured content blocks.

**Request Types:**

```rust
// SearchDocsRequest
{
    keywords: String,
    exclude_keywords: Option<String>,
    limit: Option<u32>,
}

// SearchMemoryRequest
{
    keywords: Vec<String>,
    start_time: Option<DateTime<Utc>>,
    end_time: Option<DateTime<Utc>>,
}
```

**Sources:** [libs/api/src/lib.rs:72-77](), [libs/api/src/models.rs:621-633]()

### Slack Integration

These methods enable interaction with Slack workspaces, allowing agents to read and send messages.

| Method | Signature | Purpose |
|--------|-----------|---------|
| `slack_read_messages` | `async fn(input: &SlackReadMessagesRequest) -> Result<Vec<Content>, String>` | Reads messages from a Slack channel |
| `slack_read_replies` | `async fn(input: &SlackReadRepliesRequest) -> Result<Vec<Content>, String>` | Reads reply thread for a specific message |
| `slack_send_message` | `async fn(input: &SlackSendMessageRequest) -> Result<Vec<Content>, String>` | Sends a message to a Slack channel or thread |

**Request Types:**

```rust
// SlackReadMessagesRequest
{
    channel: String,
    limit: Option<u32>,
}

// SlackReadRepliesRequest
{
    channel: String,
    ts: String,  // Timestamp identifier for thread
}

// SlackSendMessageRequest
{
    channel: String,
    mrkdwn_text: String,
    thread_ts: Option<String>,  // For replying in thread
}
```

**Sources:** [libs/api/src/lib.rs:79-91](), [libs/api/src/models.rs:635-652]()

## Key Data Models

### Core Session Types

The trait extensively uses these data structures defined in `models.rs`:

```mermaid
graph TB
    subgraph "Session Hierarchy"
        SESSION["AgentSession<br/>{id: Uuid, title: String,<br/>agent_id: AgentID,<br/>visibility: AgentSessionVisibility,<br/>checkpoints: Vec&lt;AgentCheckpointListItem&gt;}"]
        
        CHECKPOINT["AgentCheckpointListItem<br/>{id: Uuid, status: AgentStatus,<br/>execution_depth: usize,<br/>parent: Option&lt;AgentParentCheckpoint&gt;}"]
        
        RUN_INPUT["RunAgentInput<br/>{checkpoint_id: Uuid,<br/>input: AgentInput}"]
        
        RUN_OUTPUT["RunAgentOutput<br/>{checkpoint: AgentCheckpointListItem,<br/>session: AgentSessionListItem,<br/>output: AgentOutput}"]
    end
    
    subgraph "Agent I/O"
        AGENT_INPUT["AgentInput::PabloV1<br/>{messages: Option&lt;Vec&lt;ChatMessage&gt;&gt;,<br/>node_states: Option&lt;Value&gt;}"]
        
        AGENT_OUTPUT["AgentOutput::PabloV1<br/>{messages: Vec&lt;ChatMessage&gt;,<br/>node_states: Value}"]
    end
    
    subgraph "Enums"
        AGENT_ID["AgentID::PabloV1"]
        STATUS["AgentStatus::<br/>Running | Complete | Blocked | Failed"]
        VISIBILITY["AgentSessionVisibility::<br/>Private | Public"]
    end
    
    SESSION -->|"contains"| CHECKPOINT
    RUN_INPUT -->|"uses"| AGENT_INPUT
    RUN_OUTPUT -->|"produces"| AGENT_OUTPUT
    SESSION -->|"has"| AGENT_ID
    SESSION -->|"has"| VISIBILITY
    CHECKPOINT -->|"has"| STATUS
```

**Sources:** [libs/api/src/models.rs:65-255]()

### Rulebook Types

```mermaid
graph LR
    LIST["ListRuleBook<br/>{id, uri, description,<br/>visibility, tags,<br/>created_at, updated_at}"]
    
    FULL["RuleBook<br/>{id, uri, description,<br/>content, visibility, tags,<br/>created_at, updated_at}"]
    
    CREATE_REQ["CreateRuleBookInput<br/>{uri, description, content,<br/>tags, visibility}"]
    
    CREATE_RES["CreateRuleBookResponse<br/>{id}"]
    
    VIS["RuleBookVisibility::<br/>Public | Private"]
    
    LIST -->|"list_rulebooks()"| FULL
    CREATE_REQ -->|"create_rulebook()"| CREATE_RES
    LIST -->|"has"| VIS
    FULL -->|"has"| VIS
```

**Sources:** [libs/api/src/models.rs:494-596]()

### Block and Document Types

The `Block` type represents infrastructure code blocks (Terraform, Kubernetes, etc.) with dependency information:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `Uuid` | Unique block identifier |
| `provisioner` | `ProvisionerType` | Terraform, Kubernetes, Dockerfile, GithubActions, or None |
| `language` | `String` | Programming/config language |
| `code` | `String` | Actual code content |
| `dependencies` | `Vec<Dependency>` | Block dependencies with selectors |
| `dependents` | `Vec<DependentBlock>` | Blocks depending on this one |
| `document_uri` | `String` | Source file path |
| `start_point` / `end_point` | `Point` | Location in file (row, column) |

**Sources:** [libs/api/src/models.rs:269-305](), [libs/api/src/models.rs:307-435]()

## Abstraction and Implementation Pattern

The trait enables a provider pattern where consuming code (CLI, TUI) works through the abstraction without knowledge of the underlying implementation.

```mermaid
graph TB
    subgraph "Consumer Code"
        CLI["CLI<br/>(cli/src)"]
        TUI["TUI<br/>(libs/tui/src)"]
        ASYNC["mode_async.rs"]
        INTERACTIVE["mode_interactive.rs"]
    end
    
    subgraph "AgentProvider Abstraction"
        TRAIT["AgentProvider Trait<br/>(libs/api/src/lib.rs:16-92)"]
    end
    
    subgraph "Implementations"
        REMOTE["RemoteClient<br/>(libs/api/src/remote/mod.rs)<br/>HTTP → Stakpak API"]
        LOCAL["LocalClient<br/>(libs/api/src/local/mod.rs)<br/>Direct → LLM Providers"]
    end
    
    subgraph "Backend Services"
        STAKPAK_API["Stakpak Hosted API<br/>(Remote Backend)"]
        
        subgraph "Local Backend Components"
            STAKAI["StakAI Client<br/>(libs/ai)"]
            SQLITE["SQLite Database<br/>(libsql)"]
            HOOKS["HookRegistry"]
            SEARCH["SearchServicesOrchestrator"]
        end
    end
    
    CLI --> ASYNC
    CLI --> INTERACTIVE
    TUI --> TRAIT
    ASYNC --> TRAIT
    INTERACTIVE --> TRAIT
    
    TRAIT -.->|"implements"| REMOTE
    TRAIT -.->|"implements"| LOCAL
    
    REMOTE --> STAKPAK_API
    
    LOCAL --> STAKAI
    LOCAL --> SQLITE
    LOCAL --> HOOKS
    LOCAL --> SEARCH
```

**Sources:** [libs/api/src/lib.rs:11-14]() (module declarations)

## Error Handling

All trait methods return `Result<T, String>` for simplicity, though streaming methods use the specialized `ApiStreamError` enum for detailed error classification:

| Error Variant | Trigger Condition |
|---------------|-------------------|
| `AgentInputInvalid(String)` | Invalid input parameters |
| `AgentStateInvalid` | Session state corrupted or invalid |
| `AgentNotSupported` | Requested agent type not available |
| `AgentExecutionLimitExceeded` | Thinking/execution limit reached |
| `AgentInvalidResponseStream` | Malformed streaming response |
| `InvalidGeneratedCode` | Generated code failed validation |
| `CopilotError` | Backend overloaded |
| `SaveError` | Persistence failure |
| `Unknown(String)` | Unclassified error |

The `ApiStreamError` implements `From<&str>` and `From<String>` for automatic parsing of error messages from stream responses.

**Sources:** [libs/api/src/models.rs:15-63]()

## Dependencies

The `stakpak-api` crate depends on:

| Dependency | Purpose |
|------------|---------|
| `async-trait` | Enable async trait methods |
| `futures-util` | Stream utilities for chat_completion_stream |
| `reqwest` | HTTP client (RemoteClient) |
| `libsql` | SQLite interface (LocalClient) |
| `rmcp` | MCP protocol types (Content) |
| `stakpak-shared` | Shared models (AgentModel, ChatMessage, Tool, etc.) |
| `uuid` | Session and checkpoint identifiers |
| `chrono` | Timestamp handling |
| `serde` / `serde_json` | Serialization |
| `eventsource-stream` | SSE parsing for streams |

**Sources:** [libs/api/Cargo.toml:10-27]()

## Usage Pattern Example

While this document focuses on the trait definition, typical usage follows this pattern:

1. Obtain an implementation (RemoteClient or LocalClient) based on configuration
2. Call trait methods through the abstract interface
3. Handle `Result` types for error cases
4. For streaming, consume the returned `Stream` asynchronously

The trait's design ensures that switching between remote and local backends requires no changes to consuming code, only configuration changes.

**Sources:** [libs/api/src/lib.rs:16-92]()

---

# Page: Remote Client Implementation

# Remote Client Implementation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/stakpak-dark.png](assets/stakpak-dark.png)
- [assets/stakpak-light.png](assets/stakpak-light.png)
- [libs/api/Cargo.toml](libs/api/Cargo.toml)
- [libs/api/src/lib.rs](libs/api/src/lib.rs)
- [libs/api/src/models.rs](libs/api/src/models.rs)
- [libs/mcp/server/README_SECRETS.md](libs/mcp/server/README_SECRETS.md)

</details>



This document describes the `RemoteClient` implementation of the `AgentProvider` trait, which provides agent capabilities through HTTP communication with Stakpak's hosted backend API. For local LLM integration without a hosted backend, see [Local Client Implementation](#4.3). For the trait definition and abstraction, see [AgentProvider Trait](#4.1).

## Overview

`RemoteClient` is the HTTP-based implementation of the `AgentProvider` trait that connects to Stakpak's hosted backend services. It is the simpler of the two provider implementations, requiring only an API key for authentication rather than direct LLM credentials.

The `RemoteClient` is instantiated when:
- The profile's `provider` field is not set to `"local"` in configuration
- A `STAKPAK_API_KEY` environment variable is present
- The `stakpak login` command has stored an API key in `~/.stakpak/config.toml`

**RemoteClient Architecture Position**

```mermaid
graph TB
    CLI["CLI Application<br/>cli/src"]
    TUI["TUI Application<br/>tui/src"]
    
    TRAIT["AgentProvider Trait<br/>libs/api/src/lib.rs"]
    
    REMOTE["RemoteClient<br/>libs/api/src/remote"]
    
    BACKEND["Stakpak Backend API<br/>api.stakpak.com"]
    
    CLI --> TRAIT
    TUI --> TRAIT
    
    TRAIT -.implements.-> REMOTE
    
    REMOTE -->|HTTP/HTTPS| BACKEND
    
    BACKEND -->|Routes to| LLM_SERVICES["LLM Services<br/>OpenAI, Anthropic, etc."]
    BACKEND -->|Routes to| SEARCH["Search Services"]
    BACKEND -->|Routes to| MEMORY["Memory Storage"]
    BACKEND -->|Routes to| SESSIONS["Session Storage"]
```

Sources: [libs/api/src/lib.rs:1-93](), [README.md:110-140]()

## Configuration

The `RemoteClient` is configured through profile settings in `~/.stakpak/config.toml` or environment variables. The default configuration uses the remote provider automatically when an API key is available.

### Configuration Methods

| Method | Configuration Location | Notes |
|--------|----------------------|-------|
| Environment Variable | `STAKPAK_API_KEY` | Highest precedence |
| Config File | `~/.stakpak/config.toml` | Set via `stakpak login` |
| Interactive Flow | Browser-based auth | Creates API key automatically |

### Example Configuration

When using the default profile without explicit local provider configuration, the `RemoteClient` is selected automatically:

```toml
# Implicit remote configuration - API key only
[settings]
api_key = "sk-..."
```

No additional LLM provider credentials are needed as the backend handles all LLM communication.

Sources: [README.md:112-140]()

## Module Structure

```mermaid
graph LR
    API["libs/api/src/lib.rs"]
    REMOTE["libs/api/src/remote/"]
    MODELS["libs/api/src/models.rs"]
    ERROR["libs/api/src/error.rs"]
    
    API -->|declares module| REMOTE
    API -->|exports types| MODELS
    API -->|exports errors| ERROR
    
    REMOTE -->|uses| MODELS
    REMOTE -->|returns| ERROR
```

Sources: [libs/api/src/lib.rs:11-14](), [libs/api/Cargo.toml:1-31]()

## AgentProvider Trait Implementation

The `RemoteClient` implements all 14 methods defined in the `AgentProvider` trait by translating them into HTTP API calls to the Stakpak backend.

**Method Categories and HTTP Endpoints**

```mermaid
graph TB
    subgraph "Account Management"
        GET_ACCOUNT["get_my_account()"]
        GET_BILLING["get_billing_info(account_username)"]
    end
    
    subgraph "Rulebook Management"
        LIST_RB["list_rulebooks()"]
        GET_RB["get_rulebook_by_uri(uri)"]
        CREATE_RB["create_rulebook(...)"]
        DELETE_RB["delete_rulebook(uri)"]
    end
    
    subgraph "Session Management"
        LIST_SESS["list_agent_sessions()"]
        GET_SESS["get_agent_session(id)"]
        GET_STATS["get_agent_session_stats(id)"]
        GET_CKPT["get_agent_checkpoint(id)"]
        GET_LATEST["get_agent_session_latest_checkpoint(id)"]
    end
    
    subgraph "Chat Operations"
        CHAT["chat_completion(model, messages, tools)"]
        CHAT_STREAM["chat_completion_stream(...)"]
        CANCEL["cancel_stream(request_id)"]
    end
    
    subgraph "Search & Memory"
        SEARCH_DOCS["search_docs(request)"]
        SEARCH_MEM["search_memory(request)"]
        MEMORIZE["memorize_session(checkpoint_id)"]
    end
    
    subgraph "Slack Integration"
        READ_MSG["slack_read_messages(request)"]
        READ_REPLIES["slack_read_replies(request)"]
        SEND_MSG["slack_send_message(request)"]
    end
```

Sources: [libs/api/src/lib.rs:17-92]()

## HTTP Communication Layer

The `RemoteClient` uses the `reqwest` HTTP client library to communicate with the backend API over HTTPS.

**Request/Response Flow**

```mermaid
sequenceDiagram
    participant App as "CLI/TUI Application"
    participant RC as "RemoteClient"
    participant HTTP as "reqwest::Client"
    participant Backend as "Stakpak Backend API"
    
    App->>RC: call AgentProvider method
    RC->>RC: construct request body
    RC->>RC: add authentication headers
    RC->>HTTP: send HTTP request
    HTTP->>Backend: HTTPS POST/GET/DELETE
    Backend->>Backend: process request
    Backend->>Backend: call LLM or other services
    Backend->>HTTP: JSON response
    HTTP->>RC: Result<Response>
    RC->>RC: parse JSON to Rust types
    alt Success
        RC->>App: Ok(typed_response)
    else Error
        RC->>App: Err(error_message)
    end
```

Sources: [libs/api/Cargo.toml:17](), [libs/api/src/lib.rs:16-92]()

## Authentication Mechanism

The `RemoteClient` authenticates requests using an API key transmitted in HTTP headers.

**Authentication Flow**

```mermaid
graph LR
    CONFIG["Config File<br/>~/.stakpak/config.toml"]
    ENV["Environment<br/>STAKPAK_API_KEY"]
    
    RC["RemoteClient"]
    
    HEADERS["HTTP Headers<br/>Authorization: Bearer"]
    
    CONFIG -->|loads| RC
    ENV -->|overrides| RC
    
    RC -->|adds to| HEADERS
    HEADERS -->|with every request| BACKEND["Backend API"]
```

The API key is:
- Loaded from `~/.stakpak/config.toml` at initialization
- Can be overridden by the `STAKPAK_API_KEY` environment variable
- Included as a Bearer token in the `Authorization` header for each request
- Validated by the backend before processing requests

Sources: [README.md:123-133]()

## Data Models

The `RemoteClient` uses typed data structures for all API communication, defined in the `models` module.

### Core Request Types

| Request Type | Purpose | Fields |
|--------------|---------|--------|
| `SearchDocsRequest` | Document search | `keywords`, `exclude_keywords`, `limit` |
| `SearchMemoryRequest` | Memory search | `keywords`, `start_time`, `end_time` |
| `SlackReadMessagesRequest` | Read Slack messages | `channel`, `limit` |
| `SlackReadRepliesRequest` | Read Slack thread | `channel`, `ts` |
| `SlackSendMessageRequest` | Send Slack message | `channel`, `mrkdwn_text`, `thread_ts` |
| `CreateRuleBookInput` | Create/update rulebook | `uri`, `description`, `content`, `tags`, `visibility` |

Sources: [libs/api/src/models.rs:622-652]()

### Core Response Types

| Response Type | Purpose | Key Fields |
|---------------|---------|------------|
| `GetMyAccountResponse` | Account information | `username`, `id`, `email`, `scope` |
| `AgentSession` | Session details | `id`, `title`, `checkpoints`, `visibility` |
| `RunAgentOutput` | Agent execution result | `checkpoint`, `session`, `output` |
| `RuleBook` | Rulebook document | `uri`, `description`, `content`, `tags` |
| `ChatCompletionResponse` | Synchronous chat | OpenAI-compatible format |
| `ChatCompletionStreamResponse` | Streaming chat chunk | SSE format |

Sources: [libs/api/src/models.rs:538-653]()

## Streaming Support

The `RemoteClient` provides streaming capabilities for real-time chat responses through Server-Sent Events (SSE).

**Streaming Architecture**

```mermaid
graph TB
    APP["Application Layer"]
    STREAM_METHOD["chat_completion_stream()"]
    HTTP_STREAM["HTTP Stream<br/>eventsource-stream"]
    SSE["Server-Sent Events<br/>Backend API"]
    
    APP -->|calls| STREAM_METHOD
    STREAM_METHOD -->|returns| STREAM_OBJ["Pin<Box<dyn Stream>>"]
    
    STREAM_OBJ -->|pulls chunks| HTTP_STREAM
    HTTP_STREAM -->|receives| SSE
    
    SSE -->|emits| EVENTS["ChatCompletionStreamResponse"]
    EVENTS -->|or| ERRORS["ApiStreamError"]
    
    STREAM_METHOD -->|also returns| REQUEST_ID["Option<String>"]
    REQUEST_ID -.->|used for| CANCEL["cancel_stream(request_id)"]
```

The streaming implementation:
- Returns a `Pin<Box<dyn Stream<Item = Result<ChatCompletionStreamResponse, ApiStreamError>>>>` 
- Provides an optional `request_id` string for stream cancellation
- Uses the `eventsource-stream` crate for SSE parsing
- Allows cancellation via the `cancel_stream()` method

Sources: [libs/api/src/lib.rs:55-70](), [libs/api/Cargo.toml:19]()

## Error Handling

The `RemoteClient` translates HTTP and API errors into strongly-typed error variants.

### ApiStreamError Variants

```mermaid
graph TB
    ERROR["ApiStreamError Enum"]
    
    ERROR --> INVALID["AgentInputInvalid(String)"]
    ERROR --> STATE["AgentStateInvalid"]
    ERROR --> NOT_SUPPORTED["AgentNotSupported"]
    ERROR --> LIMIT["AgentExecutionLimitExceeded"]
    ERROR --> INVALID_STREAM["AgentInvalidResponseStream"]
    ERROR --> INVALID_CODE["InvalidGeneratedCode"]
    ERROR --> COPILOT["CopilotError"]
    ERROR --> SAVE["SaveError"]
    ERROR --> UNKNOWN["Unknown(String)"]
    
    INVALID -.->|contains| DETAIL["Error message details"]
    UNKNOWN -.->|contains| RAW["Raw error string"]
```

Error strings from the backend are pattern-matched and converted into typed variants:

- "Agent not supported" → `AgentNotSupported`
- "Agent state is not valid" → `AgentStateInvalid`
- "Agent thinking limit exceeded" → `AgentExecutionLimitExceeded`
- "Invalid response stream" → `AgentInvalidResponseStream`
- "Agent input is not valid: ..." → `AgentInputInvalid(message)`
- Other errors → `Unknown(error_string)`

Sources: [libs/api/src/models.rs:15-63]()

## Session and Checkpoint Management

The `RemoteClient` provides methods for managing persistent agent sessions stored in the backend.

**Session Lifecycle**

```mermaid
stateDiagram-v2
    [*] --> Created: create session
    Created --> Running: start execution
    Running --> Running: continue execution
    Running --> Complete: task finished
    Running --> Blocked: needs approval
    Running --> Failed: error occurred
    Complete --> [*]
    Failed --> [*]
    Blocked --> Running: user approves
    
    Running --> Checkpoint: save state
    Checkpoint --> Running: resume
```

### Session Data Structures

| Type | Description | Status Values |
|------|-------------|---------------|
| `AgentSession` | Full session with checkpoints | N/A |
| `AgentCheckpointListItem` | Checkpoint metadata | `RUNNING`, `COMPLETE`, `BLOCKED`, `FAILED` |
| `RunAgentOutput` | Execution result | Contains checkpoint, session, and output |
| `AgentSessionStats` | Usage statistics | Tool calls, time saved, etc. |

The backend maintains the complete session history including:
- All messages exchanged with the LLM
- Tool calls and their results
- Execution state and node states
- Parent-child checkpoint relationships for execution depth tracking

Sources: [libs/api/src/models.rs:66-186]()

## Rulebook Operations

Rulebooks are markdown documents with YAML frontmatter that customize agent behavior. The `RemoteClient` provides full CRUD operations.

### Rulebook Structure

```yaml
---
uri: stakpak://org/document.md
description: Brief description
tags:
  - tag1
  - tag2
visibility: PUBLIC | PRIVATE
---

# Markdown Content
...
```

### API Methods

| Method | HTTP Operation | Parameters | Returns |
|--------|---------------|------------|---------|
| `list_rulebooks()` | GET | None | `Vec<ListRuleBook>` |
| `get_rulebook_by_uri(uri)` | GET | URI string | `RuleBook` |
| `create_rulebook(...)` | POST/PUT | URI, description, content, tags, visibility | `CreateRuleBookResponse` |
| `delete_rulebook(uri)` | DELETE | URI string | `()` |

The backend stores rulebooks with:
- Unique URI identifiers (e.g., `stakpak://organization/filename.md`)
- Content versioning (tracked via `updated_at` timestamp)
- Visibility control (public or private)
- Tag-based organization

Sources: [libs/api/src/lib.rs:25-36](), [libs/api/src/models.rs:494-596]()

## Chat Completion Methods

The `RemoteClient` provides both synchronous and streaming chat completion through the backend's LLM routing.

### Input Parameters

Both methods accept:
- `model`: `AgentModel` enum specifying which LLM to use
- `messages`: `Vec<ChatMessage>` with the conversation history
- `tools`: `Option<Vec<Tool>>` for function calling capabilities
- `headers` (stream only): Optional custom HTTP headers

### Synchronous Completion

```rust
async fn chat_completion(
    &self,
    model: AgentModel,
    messages: Vec<ChatMessage>,
    tools: Option<Vec<Tool>>,
) -> Result<ChatCompletionResponse, String>
```

Returns a complete response with:
- Generated message content
- Tool calls (if any)
- Token usage statistics
- Model and finish reason

### Streaming Completion

```rust
async fn chat_completion_stream(
    &self,
    model: AgentModel,
    messages: Vec<ChatMessage>,
    tools: Option<Vec<Tool>>,
    headers: Option<HeaderMap>,
) -> Result<(Stream, Option<String>), String>
```

Returns:
- A `Stream` of `ChatCompletionStreamResponse` chunks
- An optional `request_id` for cancellation

The backend handles:
- LLM selection and routing based on the `AgentModel`
- API key management for downstream LLM services
- Rate limiting and quota enforcement
- Response formatting to OpenAI-compatible schema

Sources: [libs/api/src/lib.rs:48-70](), [libs/api/src/models.rs:6-12]()

## Search and Memory Operations

The `RemoteClient` provides access to document search and session memory features hosted on the backend.

### Document Search

```mermaid
graph LR
    APP["Application"]
    SEARCH["search_docs()"]
    BACKEND["Backend Search"]
    DOCKER["Docker: SearXNG"]
    RESULTS["Vec<Content>"]
    
    APP -->|SearchDocsRequest| SEARCH
    SEARCH -->|HTTP POST| BACKEND
    BACKEND -->|web search| DOCKER
    DOCKER -->|aggregated results| BACKEND
    BACKEND -->|formatted| RESULTS
    RESULTS --> APP
```

**SearchDocsRequest Parameters:**
- `keywords`: Main search terms
- `exclude_keywords`: Terms to filter out (optional)
- `limit`: Maximum number of results (optional)

### Memory Operations

The memory system allows agents to store and retrieve information from past sessions:

| Method | Purpose | Input | Output |
|--------|---------|-------|--------|
| `search_memory()` | Search past sessions | Keywords, time range | `Vec<Content>` |
| `memorize_session()` | Save session to memory | Checkpoint ID | `()` |

Memory search supports:
- Keyword-based retrieval
- Time-range filtering with `start_time` and `end_time`
- Semantic relevance ranking by the backend

Sources: [libs/api/src/lib.rs:72-77](), [libs/api/src/models.rs:622-633]()

## Slack Integration

The `RemoteClient` provides Slack integration methods when the backend has appropriate credentials configured.

### Slack Methods

```mermaid
graph TB
    READ_MESSAGES["slack_read_messages()<br/>channel, limit"]
    READ_REPLIES["slack_read_replies()<br/>channel, thread_ts"]
    SEND_MESSAGE["slack_send_message()<br/>channel, text, thread_ts?"]
    
    READ_MESSAGES -->|returns| MSG_CONTENT["Vec<Content><br/>message list"]
    READ_REPLIES -->|returns| REPLY_CONTENT["Vec<Content><br/>thread replies"]
    SEND_MESSAGE -->|returns| SEND_RESULT["Vec<Content><br/>sent message confirmation"]
```

### Request Parameters

**SlackReadMessagesRequest:**
- `channel`: Channel ID or name
- `limit`: Maximum messages to retrieve (optional)

**SlackReadRepliesRequest:**
- `channel`: Channel ID or name  
- `ts`: Thread timestamp identifier

**SlackSendMessageRequest:**
- `channel`: Target channel
- `mrkdwn_text`: Message content in Markdown
- `thread_ts`: Thread timestamp for replies (optional)

The backend handles:
- Slack OAuth tokens and workspace authentication
- API rate limiting compliance
- Message formatting and content type conversion
- Error handling for invalid channels or permissions

Sources: [libs/api/src/lib.rs:79-92](), [libs/api/src/models.rs:635-652]()

## Dependencies

The `RemoteClient` relies on the following key dependencies:

| Crate | Purpose | Usage |
|-------|---------|-------|
| `reqwest` | HTTP client | All API communication |
| `serde` / `serde_json` | Serialization | Request/response encoding |
| `futures-util` | Async streams | Chat streaming |
| `eventsource-stream` | SSE parsing | Streaming responses |
| `async-trait` | Trait async methods | AgentProvider implementation |
| `uuid` | Unique IDs | Session and checkpoint identification |
| `chrono` | Date/time | Timestamps in responses |
| `urlencoding` | URL encoding | Query parameters |

Sources: [libs/api/Cargo.toml:10-27]()

---

# Page: Local Client Implementation

# Local Client Implementation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [libs/api/src/local/mod.rs](libs/api/src/local/mod.rs)
- [libs/shared/src/container.rs](libs/shared/src/container.rs)
- [libs/shared/src/models/integrations/mod.rs](libs/shared/src/models/integrations/mod.rs)
- [libs/shared/src/models/integrations/search_service.rs](libs/shared/src/models/integrations/search_service.rs)

</details>



## Purpose and Scope

The `LocalClient` is a local implementation of the `AgentProvider` trait that enables fully offline agent operation without requiring a Stakpak hosted API. It provides direct LLM integration, SQLite-based session persistence, and Docker-based search capabilities. This page documents the architecture, components, and implementation details of `LocalClient`.

For information about the `AgentProvider` trait interface, see [AgentProvider Trait](#4.1). For the alternative remote implementation, see [Remote Client Implementation](#4.2).

**Sources:** [libs/api/src/local/mod.rs:1-876]()

---

## Architecture Overview

**Component Architecture**

```mermaid
graph TB
    subgraph "LocalClient Structure"
        LC["LocalClient"]
        DB["db: Connection<br/>(libsql SQLite)"]
        PROVIDERS["providers: LLMProviderConfig"]
        MODEL_OPTS["model_options: ModelOptions"]
        HOOKS["hook_registry: Arc&lt;HookRegistry&gt;"]
        SEARCH["_search_services_orchestrator:<br/>Arc&lt;SearchServicesOrchestrator&gt;"]
    end
    
    subgraph "External Dependencies"
        SQLITE["SQLite Database<br/>~/.stakpak/data/local.db"]
        STAKAI["StakAIClient<br/>(libs/shared)"]
        DOCKER["Docker Containers<br/>(Search Services)"]
        LLMS["LLM Providers<br/>(OpenAI/Anthropic/Gemini/Bedrock)"]
    end
    
    subgraph "Supporting Types"
        MODEL_SET["ModelSet<br/>(smart/eco/recovery)"]
        AGENT_STATE["AgentState<br/>(HookContext state)"]
        HOOK_CTX["HookContext&lt;AgentState&gt;"]
    end
    
    LC --> DB
    LC --> PROVIDERS
    LC --> MODEL_OPTS
    LC --> HOOKS
    LC --> SEARCH
    
    DB --> SQLITE
    PROVIDERS --> STAKAI
    STAKAI --> LLMS
    SEARCH --> DOCKER
    
    MODEL_OPTS --> MODEL_SET
    HOOKS --> HOOK_CTX
    HOOK_CTX --> AGENT_STATE
```

**Sources:** [libs/api/src/local/mod.rs:42-66](), [libs/api/src/local/mod.rs:100-108]()

---

## Core Components

### LocalClient Structure

The `LocalClient` struct contains the essential components for local agent operation:

| Field | Type | Purpose |
|-------|------|---------|
| `db` | `Connection` | SQLite database connection for session persistence |
| `stakpak_base_url` | `Option<String>` | Optional URL for fetching rulebooks from Stakpak API |
| `providers` | `LLMProviderConfig` | Configuration for all available LLM providers |
| `model_options` | `ModelOptions` | User-specified model preferences for smart/eco/recovery modes |
| `hook_registry` | `Option<Arc<HookRegistry<AgentState>>>` | Lifecycle hooks for inference customization |
| `_search_services_orchestrator` | `Option<Arc<SearchServicesOrchestrator>>` | Docker-based search service manager |

**Sources:** [libs/api/src/local/mod.rs:42-50]()

### Configuration and Initialization

The `LocalClientConfig` structure defines the parameters for creating a `LocalClient`:

```rust
pub struct LocalClientConfig {
    pub stakpak_base_url: Option<String>,
    pub store_path: Option<String>,
    pub providers: LLMProviderConfig,
    pub smart_model: Option<String>,
    pub eco_model: Option<String>,
    pub recovery_model: Option<String>,
    pub hook_registry: Option<HookRegistry<AgentState>>,
}
```

The initialization process:

1. **Database Setup**: Creates SQLite database at `store_path` (defaults to `~/.stakpak/data/local.db`)
2. **Schema Initialization**: Calls `db::init_schema()` to create required tables
3. **Model Configuration**: Converts string model names to `LLMModel` enums
4. **Hook Registration**: Registers `InlineScratchpadContextHook` for context management
5. **Search Orchestrator**: Initializes `SearchServicesOrchestrator` for Docker-based search

**Sources:** [libs/api/src/local/mod.rs:100-108](), [libs/api/src/local/mod.rs:119-188]()

### Model Selection System

**ModelOptions and ModelSet**

```mermaid
graph LR
    subgraph "User Configuration"
        CONF["ModelOptions<br/>(Optional user preferences)"]
        SMART_OPT["smart_model: Option&lt;LLMModel&gt;"]
        ECO_OPT["eco_model: Option&lt;LLMModel&gt;"]
        REC_OPT["recovery_model: Option&lt;LLMModel&gt;"]
    end
    
    subgraph "Runtime Resolution"
        SET["ModelSet<br/>(Resolved models)"]
        SMART["smart_model: LLMModel<br/>(default: Claude-4.5-Sonnet)"]
        ECO["eco_model: LLMModel<br/>(default: Claude-4.5-Haiku)"]
        REC["recovery_model: LLMModel<br/>(default: GPT-5)"]
    end
    
    subgraph "Model Selection"
        AGENT_MODEL["AgentModel enum<br/>(Smart/Eco/Recovery)"]
        GET_MODEL["get_model() method"]
        FINAL["Selected LLMModel"]
    end
    
    CONF --> SMART_OPT
    CONF --> ECO_OPT
    CONF --> REC_OPT
    
    SMART_OPT --> SMART
    ECO_OPT --> ECO
    REC_OPT --> REC
    
    SMART --> SET
    ECO --> SET
    REC --> SET
    
    AGENT_MODEL --> GET_MODEL
    SET --> GET_MODEL
    GET_MODEL --> FINAL
```

The model selection system uses two levels of abstraction:

- **ModelOptions**: User-facing configuration with optional preferences
- **ModelSet**: Runtime structure with resolved models (fills in defaults)
- **AgentModel enum**: Request-time model selector (Smart/Eco/Recovery)

The `get_model()` method maps `AgentModel` to the appropriate `LLMModel` at runtime.

**Sources:** [libs/api/src/local/mod.rs:52-76](), [libs/api/src/local/mod.rs:78-98]()

### SQLite Database Integration

The `LocalClient` uses a SQLite database for persistent storage of sessions and checkpoints. Database operations are abstracted through the `db` module:

**Key Database Operations:**

| Function | Purpose | Location |
|----------|---------|----------|
| `init_schema()` | Creates tables for sessions and checkpoints | [libs/api/src/local/db.rs]() |
| `create_session()` | Stores a new `AgentSession` | [libs/api/src/local/mod.rs:766]() |
| `list_sessions()` | Retrieves all sessions | [libs/api/src/local/mod.rs:294]() |
| `get_session()` | Fetches session by UUID | [libs/api/src/local/mod.rs:298]() |
| `create_checkpoint()` | Stores checkpoint with messages | [libs/api/src/local/mod.rs:782]() |
| `get_checkpoint()` | Retrieves checkpoint by ID | [libs/api/src/local/mod.rs:310]() |
| `get_latest_checkpoint()` | Gets most recent checkpoint for session | [libs/api/src/local/mod.rs:317]() |

The database path defaults to `~/.stakpak/data/local.db` and is automatically created if it doesn't exist.

**Sources:** [libs/api/src/local/mod.rs:116](), [libs/api/src/local/mod.rs:135-143](), [libs/api/src/local/mod.rs:293-318]()

### Hook Registry and Lifecycle Management

The `LocalClient` uses a hook registry to execute custom logic at specific lifecycle events:

**Registered Hooks:**

- **InlineScratchpadContextHook**: Registered for `LifecycleEvent::BeforeInference`
  - Manages message history truncation
  - Limits action messages to 100 characters
  - Keeps last action message and last 50 results
  - Injects context into the LLM input

**Lifecycle Events:**

```mermaid
graph TB
    BR["LifecycleEvent::<br/>BeforeRequest"]
    BI["LifecycleEvent::<br/>BeforeInference"]
    AI["LifecycleEvent::<br/>AfterInference"]
    AR["LifecycleEvent::<br/>AfterRequest"]
    
    START["Request Start"]
    INIT["Initialize Session"]
    PREP["Prepare Context"]
    INFER["LLM Inference"]
    PROCESS["Process Response"]
    UPDATE["Update Session"]
    END["Request End"]
    
    START --> BR
    BR --> INIT
    INIT --> BI
    BI --> PREP
    PREP --> INFER
    INFER --> AI
    AI --> PROCESS
    PROCESS --> UPDATE
    UPDATE --> AR
    AR --> END
```

Hooks can modify the `HookContext<AgentState>` at each stage, enabling customization of prompt construction, response processing, and session state.

**Sources:** [libs/api/src/local/mod.rs:4-6](), [libs/api/src/local/mod.rs:152-163](), [libs/api/src/local/mod.rs:326-334](), [libs/api/src/local/mod.rs:661-667]()

### Search Services Orchestrator

The `SearchServicesOrchestrator` manages Docker-based web search functionality using the SearXNG search engine.

**Architecture:**

```mermaid
graph TB
    subgraph "SearchServicesOrchestrator"
        SSO["SearchServicesOrchestrator::start()"]
        CONFIG_CHECK["Load Existing Config"]
        HEALTH["Health Check API"]
        DOCKER_CHECK["is_docker_available()"]
        IMAGE_CHECK["ensure_image_exists()"]
        RUN["run_container_detached()"]
        SAVE["save_config()"]
    end
    
    subgraph "Docker Container"
        API_CONTAINER["ghcr.io/stakpak/local_search:0.3"]
        SEARXNG["SearXNG Engine<br/>(port 8080 internal)"]
        API["Search API<br/>(port 8000 internal)"]
    end
    
    subgraph "Configuration"
        CONFIG_FILE["~/.stakpak/session/<br/>search_config.json"]
        SEARCH_CONFIG["SearchConfig<br/>(api_port, container_id)"]
    end
    
    subgraph "Client Usage"
        SEARCH_CLIENT["SearchClient"]
        METHODS["search()<br/>scrape()<br/>search_and_scrape()"]
    end
    
    SSO --> CONFIG_CHECK
    CONFIG_CHECK --> HEALTH
    HEALTH -->|Healthy| SEARCH_CONFIG
    HEALTH -->|Unhealthy| DOCKER_CHECK
    DOCKER_CHECK --> IMAGE_CHECK
    IMAGE_CHECK --> RUN
    RUN --> API_CONTAINER
    API_CONTAINER --> SEARXNG
    API_CONTAINER --> API
    RUN --> SAVE
    SAVE --> CONFIG_FILE
    CONFIG_FILE --> SEARCH_CONFIG
    
    SEARCH_CONFIG --> SEARCH_CLIENT
    SEARCH_CLIENT --> METHODS
    METHODS --> API
```

**Container Configuration:**

| Environment Variable | Value | Purpose |
|---------------------|-------|---------|
| `INSTANCE_NAME` | "SearchPak" | Instance identifier |
| `SEARXNG_SECRET` | "stakpak-secret-key" | SearXNG secret key |
| `SEARXNG_PORT` | 8080 | Internal SearXNG port |
| `SEARXNG_BIND_ADDRESS` | "0.0.0.0" | Bind address |
| `PORT` | 8000 | Internal API port |

The orchestrator performs these steps:

1. **Load existing config** from `search_config.json`
2. **Health check** existing container if config found
3. **Docker availability check** if no healthy container
4. **Image existence check** (fails with actionable message if missing)
5. **Container launch** with dynamic port mapping (host port 0 → auto-assigned)
6. **Port discovery** using `get_container_host_port()`
7. **Config persistence** for future reuse

**Sources:** [libs/shared/src/models/integrations/search_service.rs:231-421](), [libs/api/src/local/mod.rs:49](), [libs/api/src/local/mod.rs:185]()

---

## AgentProvider Implementation

The `LocalClient` implements all 14 methods of the `AgentProvider` trait. This section details each implementation.

### Account Management

**get_my_account()**

Returns a static local account response:

```rust
GetMyAccountResponse {
    username: "local",
    id: "local",
    first_name: "local",
    last_name: "local",
    email: "local@stakpak.dev",
    scope: None,
}
```

**get_billing_info()**

Returns an error: "Billing info not supported in local mode"

**Sources:** [libs/api/src/local/mod.rs:192-208]()

### Rulebook Management

**list_rulebooks()**

Fetches rulebooks from the remote Stakpak API if `stakpak_base_url` is configured. Makes an HTTP GET request to `{base_url}/rules` and deserializes the response.

Returns empty list if `stakpak_base_url` is `None`.

**get_rulebook_by_uri()**

Fetches a specific rulebook by URI from `{base_url}/rules/{encoded_uri}`. URL-encodes the URI parameter before making the request.

**create_rulebook() / delete_rulebook()**

Not implemented. Return error: "Local provider does not support rulebooks yet"

**Sources:** [libs/api/src/local/mod.rs:210-291]()

### Session Management

**Session Lifecycle Flow:**

```mermaid
graph TB
    subgraph "list_agent_sessions()"
        LIST["db::list_sessions(&db)"]
        ALL_SESSIONS["Vec&lt;AgentSession&gt;"]
    end
    
    subgraph "get_agent_session()"
        GET_SESSION["db::get_session(&db, session_id)"]
        SESSION["AgentSession"]
    end
    
    subgraph "get_agent_checkpoint()"
        GET_CP["db::get_checkpoint(&db, checkpoint_id)"]
        CHECKPOINT["RunAgentOutput"]
    end
    
    subgraph "get_agent_session_latest_checkpoint()"
        GET_LATEST["db::get_latest_checkpoint(&db, session_id)"]
        LATEST_CP["RunAgentOutput"]
    end
    
    LIST --> ALL_SESSIONS
    GET_SESSION --> SESSION
    GET_CP --> CHECKPOINT
    GET_LATEST --> LATEST_CP
```

| Method | Implementation | Returns |
|--------|---------------|---------|
| `list_agent_sessions()` | `db::list_sessions()` | All sessions from database |
| `get_agent_session()` | `db::get_session()` | Single session by UUID |
| `get_agent_session_stats()` | Returns default stats | Not fully implemented |
| `get_agent_checkpoint()` | `db::get_checkpoint()` | Checkpoint by UUID |
| `get_agent_session_latest_checkpoint()` | `db::get_latest_checkpoint()` | Most recent checkpoint for session |

**Sources:** [libs/api/src/local/mod.rs:293-318]()

### Chat Completion Methods

**chat_completion()**

Synchronous chat completion flow:

```mermaid
graph TB
    START["chat_completion(model, messages, tools)"]
    CREATE_CTX["Create HookContext&lt;AgentState&gt;"]
    BEFORE_REQ["execute_hooks(BeforeRequest)"]
    INIT["initialize_session(messages)"]
    RUN["run_agent_completion(ctx, None)"]
    APPEND["Append new message"]
    UPDATE["update_session(checkpoint, messages)"]
    AFTER_REQ["execute_hooks(AfterRequest)"]
    BUILD_RESP["Build ChatCompletionResponse"]
    RETURN["Return response"]
    
    START --> CREATE_CTX
    CREATE_CTX --> BEFORE_REQ
    BEFORE_REQ --> INIT
    INIT --> RUN
    RUN --> APPEND
    APPEND --> UPDATE
    UPDATE --> AFTER_REQ
    AFTER_REQ --> BUILD_RESP
    BUILD_RESP --> RETURN
```

**chat_completion_stream()**

Streaming chat completion with async channel:

1. Creates `HookContext` and executes `BeforeRequest` hooks
2. Initializes session and gets checkpoint ID
3. Emits initial checkpoint ID: `<checkpoint_id>{id}</checkpoint_id>`
4. Spawns async task for agent completion:
   - Calls `run_agent_completion()` with stream channel
   - Forwards `GenerationDelta` chunks to receiver
   - Updates session upon completion
   - Emits final checkpoint ID
5. Returns pinned stream that yields `ChatCompletionStreamResponse` items

The stream alternates between `Delta` messages (LLM output chunks) and `Ctx` messages (state updates).

**Sources:** [libs/api/src/local/mod.rs:320-503]()

### Search and Document Operations

**search_docs()**

Implements multi-iteration search with LLM-guided query refinement:

```mermaid
graph TB
    START["search_docs(input)"]
    ORCH["SearchServicesOrchestrator::start()"]
    ANALYZE["analyze_search_query()<br/>(LLM analysis)"]
    
    subgraph "Iteration Loop (max 3)"
        SEARCH["search_client.search_and_scrape()"]
        VALIDATE["validate_search_docs()<br/>(LLM validation)"]
        CHECK{"is_satisfied?"}
        REFINE["Extract new_query"]
        ACCUMULATE["Accumulate valid_docs"]
    end
    
    BUILD["Build Content vector"]
    RETURN["Return Vec&lt;Content&gt;"]
    
    START --> ORCH
    ORCH --> ANALYZE
    ANALYZE --> SEARCH
    SEARCH --> VALIDATE
    VALIDATE --> CHECK
    CHECK -->|No| REFINE
    REFINE --> ACCUMULATE
    ACCUMULATE --> SEARCH
    CHECK -->|Yes| BUILD
    BUILD --> RETURN
```

**Process:**

1. **Start Orchestrator**: Launches Docker container if needed
2. **Analyze Query**: LLM extracts required documentation types and reformulates query
3. **Iterative Search** (max 3 iterations):
   - Search and scrape top results
   - Validate results with LLM against requirements
   - Accumulate valid documents
   - If not satisfied and new query suggested, repeat
4. **Return Results**: Format as MCP `Content` items

**Key Functions:**

- `analyze_search_query()`: Uses LLM to identify documentation needs and optimize query
- `validate_search_docs()`: LLM evaluates result relevance and completeness
- `parse_analysis_xml()` / `parse_validation_xml()`: Extract structured data from LLM XML responses

**Sources:** [libs/api/src/local/mod.rs:509-614](), [libs/api/src/local/mod.rs:877-1225]()

### Unsupported Operations

The following methods return empty results or errors:

| Method | Status | Return Value |
|--------|--------|--------------|
| `search_memory()` | Not implemented | Empty vector |
| `slack_read_messages()` | Not implemented | Empty vector |
| `slack_read_replies()` | Not implemented | Empty vector |
| `slack_send_message()` | Not implemented | Empty vector |
| `memorize_session()` | Not implemented | `Ok(())` |
| `cancel_stream()` | No-op | `Ok(())` |

**Sources:** [libs/api/src/local/mod.rs:505-648]()

---

## Internal Implementation Details

### Agent Completion Flow

The `run_agent_completion()` method orchestrates the LLM inference process:

**Execution Flow:**

```mermaid
graph TB
    START["run_agent_completion(ctx, stream_tx)"]
    BEFORE_INF["execute_hooks(BeforeInference)"]
    CHECK_INPUT{"llm_input<br/>present?"}
    ERROR["Return error:<br/>context hook not registered"]
    CREATE_CLIENT["StakAIClient::new(llm_config)"]
    
    subgraph "Stream Mode"
        CREATE_CHANNEL["Create internal channel"]
        STREAM_INPUT["LLMStreamInput"]
        SPAWN["Spawn async task"]
        FORWARD["Forward GenerationDelta"]
    end
    
    subgraph "Non-Stream Mode"
        SYNC_INPUT["LLMInput"]
        CALL["stakai_client.chat()"]
    end
    
    SET_OUTPUT["ctx.state.set_llm_output()"]
    AFTER_INF["execute_hooks(AfterInference)"]
    EXTRACT["Extract ChatMessage from llm_output"]
    RETURN["Return ChatMessage"]
    
    START --> BEFORE_INF
    BEFORE_INF --> CHECK_INPUT
    CHECK_INPUT -->|No| ERROR
    CHECK_INPUT -->|Yes| CREATE_CLIENT
    CREATE_CLIENT -->|stream_tx.is_some()| CREATE_CHANNEL
    CREATE_CLIENT -->|stream_tx.is_none()| SYNC_INPUT
    CREATE_CHANNEL --> STREAM_INPUT
    STREAM_INPUT --> SPAWN
    SPAWN --> FORWARD
    FORWARD --> SET_OUTPUT
    SYNC_INPUT --> CALL
    CALL --> SET_OUTPUT
    SET_OUTPUT --> AFTER_INF
    AFTER_INF --> EXTRACT
    EXTRACT --> RETURN
```

**Key Points:**

- Requires `llm_input` to be set by a `BeforeInference` hook (typically `InlineScratchpadContextHook`)
- Supports both streaming and non-streaming modes
- Uses `StakAIClient` for LLM provider abstraction
- Stores result in `ctx.state.llm_output` for downstream hooks

**Sources:** [libs/api/src/local/mod.rs:656-733]()

### Session Initialization

The `initialize_session()` method handles session creation or continuation:

**Decision Logic:**

```mermaid
graph TB
    START["initialize_session(messages)"]
    VALIDATE{"messages.is_empty()?"}
    ERROR["Return error"]
    EXTRACT["Extract checkpoint_id from last server message"]
    CHECK{"checkpoint_id<br/>exists?"}
    
    subgraph "Existing Session"
        GET_CP["db::get_checkpoint(checkpoint_id)"]
    end
    
    subgraph "New Session"
        GEN_TITLE["generate_session_title(messages)"]
        CREATE_SESSION["Create AgentSession<br/>(UUID, title, timestamps)"]
        SAVE_SESSION["db::create_session()"]
        CREATE_CP["Create initial checkpoint<br/>(root, depth 0)"]
        SAVE_CP["db::create_checkpoint()"]
        GET_NEW_CP["db::get_checkpoint(new_id)"]
    end
    
    RETURN["Return RunAgentOutput"]
    
    START --> VALIDATE
    VALIDATE -->|Yes| ERROR
    VALIDATE -->|No| EXTRACT
    EXTRACT --> CHECK
    CHECK -->|Yes| GET_CP
    CHECK -->|No| GEN_TITLE
    GET_CP --> RETURN
    GEN_TITLE --> CREATE_SESSION
    CREATE_SESSION --> SAVE_SESSION
    SAVE_SESSION --> CREATE_CP
    CREATE_CP --> SAVE_CP
    SAVE_CP --> GET_NEW_CP
    GET_NEW_CP --> RETURN
```

**Checkpoint ID Extraction:**

The method looks for `<checkpoint_id>{uuid}</checkpoint_id>` tags in the last server message's content to identify existing sessions. This enables seamless session continuation.

**Sources:** [libs/api/src/local/mod.rs:735-788]()

### Session Update

The `update_session()` method creates a new checkpoint after LLM inference:

**Checkpoint Creation:**

| Field | Value |
|-------|-------|
| `id` | New UUID |
| `status` | `AgentStatus::Complete` |
| `execution_depth` | `parent.execution_depth + 1` |
| `parent` | Reference to previous checkpoint |
| `created_at` / `updated_at` | Current timestamp |

The method clones the previous `AgentOutput`, updates its messages, and stores the new checkpoint in the database.

**Sources:** [libs/api/src/local/mod.rs:790-823]()

### Session Title Generation

The `generate_session_title()` method creates human-readable session titles using an LLM:

**Process:**

1. Select eco model (or fallback to available provider's smallest model)
2. Create prompt with system instructions and conversation history
3. Call LLM with max_tokens=100
4. Return generated title (typically 3-8 words)

The system prompt is loaded from `./prompts/session_title_generator.v1.txt`.

**Sources:** [libs/api/src/local/mod.rs:825-874](), [libs/api/src/local/mod.rs:117]()

### Search Query Analysis

The `analyze_search_query()` function uses an LLM to optimize search queries:

**LLM Prompt Structure:**

```
System: Expert search query analyzer
        - Identify required documentation types
        - Reformulate query for search engines
        
User:   <user_query>{original_query}</user_query>

Expected XML Response:
<analysis>
  <required_documentation>
    <item>documentation type</item>
  </required_documentation>
  <reformulated_query>optimized query</reformulated_query>
</analysis>
```

**Parsing:**

The `parse_analysis_xml()` function extracts:
- List of `<item>` tags (required documentation)
- Single `<reformulated_query>` tag (optimized search query)

**Sources:** [libs/api/src/local/mod.rs:877-993]()

### Search Results Validation

The `validate_search_docs()` function evaluates search results with LLM assistance:

**Validation Context:**

The LLM receives:
- Original query
- Required documentation types
- Previous queries (to avoid repetition)
- Accumulated needed URLs
- Current search results (up to 10 docs)

**Response Parsing:**

```
<validation>
  <is_satisfied>true/false</is_satisfied>
  <valid_docs>
    <doc><url>...</url></doc>
  </valid_docs>
  <needed_urls>
    <url>...</url>
  </needed_urls>
  <new_query>refined query if not satisfied</new_query>
  <reasoning>explanation</reasoning>
</validation>
```

The `parse_validation_xml()` function:
1. Extracts `is_satisfied` boolean
2. Filters valid URLs to those present in input docs
3. Identifies needed URLs not yet found
4. Extracts new query suggestion if not satisfied

**Sources:** [libs/api/src/local/mod.rs:995-1199]()

### Model Selection for Search

The `get_search_model()` function selects an appropriate model for search operations:

**Selection Logic:**

1. Prefer eco_model if specified
2. Fall back to smart_model if eco not available
3. Provider-specific defaults:
   - OpenAI → O4Mini
   - Anthropic → Claude-4.5-Haiku
   - Gemini → Gemini-3-Flash
4. Custom models passed through unchanged

This ensures search operations use cost-effective models suitable for structured extraction tasks.

**Sources:** [libs/api/src/local/mod.rs:1201-1225]()

---

## Summary

The `LocalClient` provides a complete local implementation of the `AgentProvider` interface with these key capabilities:

- **SQLite Persistence**: Session and checkpoint storage in `~/.stakpak/data/local.db`
- **Multi-Provider LLM Support**: Direct integration with OpenAI, Anthropic, Gemini, and Bedrock via `StakAIClient`
- **Hook System**: Extensible lifecycle management with `InlineScratchpadContextHook` for context optimization
- **Docker-Based Search**: Automatic SearXNG container orchestration for web search
- **LLM-Guided Search**: Iterative query refinement with validation for improved result quality
- **Streaming Support**: Async event channels for real-time LLM output
- **Session Continuity**: Checkpoint-based conversation threading

This implementation enables fully offline agent operation while maintaining compatibility with the broader Stakpak ecosystem.

---

# Page: Data Models and Types

## Search and Integration Models

The search system provides web search and document scraping capabilities through Docker-based services.

**Search Data Structures**

```mermaid
graph TB
    subgraph "SearchClient"
        Client[SearchClient]
        ClientReqwest["client: ClientWithMiddleware"]
        ClientApiUrl["api_url: String"]
        
        Client --> ClientReqwest
        Client --> ClientApiUrl
    end
    
    subgraph "Search Types"
        SearchResult[SearchResult]
        ResultTitle["title: String"]
        ResultUrl["url: String"]
        ResultSnippet["snippet: Option&lt;String&gt;"]
        ResultEngine["engine: Option&lt;String&gt;"]
        ResultScore["score: Option&lt;f32&gt;"]
        
        SearchResult --> ResultTitle
        SearchResult --> ResultUrl
        SearchResult --> ResultSnippet
    end
    
    subgraph "Scraped Content"
        ScrapedContent[ScrapedContent]
        ScrapedUrl["url: String"]
        ScrapedTitle["title: Option&lt;String&gt;"]
        ScrapedContent2["content: Option&lt;String&gt;"]
        ScrapedMetadata["metadata: Option&lt;Value&gt;"]
        ScrapedError["error: Option&lt;String&gt;"]
        
        ScrapedContent --> ScrapedUrl
        ScrapedContent --> ScrapedTitle
        ScrapedContent --> ScrapedContent2
        ScrapedContent --> ScrapedError
    end
    
    subgraph "Search Requests"
        SearchRequest[SearchRequest]
        SearchQuery["query: String"]
        SearchLimit["limit: u32"]
        SearchLang["lang: String"]
        SearchEngines["engines: Option&lt;Vec&lt;String&gt;&gt;"]
        
        SearchRequest --> SearchQuery
        SearchRequest --> SearchLimit
    end
    
    subgraph "Analysis Types"
        AnalysisResult[AnalysisResult]
        AnalysisRequiredDocs["required_documentation: Vec&lt;String&gt;"]
        AnalysisReformulated["reformulated_query: String"]
        
        AnalysisResult --> AnalysisRequiredDocs
        AnalysisResult --> AnalysisReformulated
    end
    
    subgraph "Validation Types"
        ValidationResult[ValidationResult]
        ValidationSatisfied["is_satisfied: bool"]
        ValidationValidDocs["valid_docs: Vec&lt;ScrapedContent&gt;"]
        ValidationNeededUrls["needed_urls: Vec&lt;String&gt;"]
        ValidationNewQuery["new_query: Option&lt;String&gt;"]
        
        ValidationResult --> ValidationSatisfied
        ValidationResult --> ValidationValidDocs
    end
```

Sources: [libs/shared/src/models/integrations/search_service.rs:22-61](), [libs/shared/src/models/integrations/search_service.rs:119-229]()

### SearchServicesOrchestrator

The `SearchServicesOrchestrator` manages Docker containers for search functionality:

| Method | Purpose |
|--------|---------|
| `start()` | Start search services in Docker, returns `SearchConfig` |
| `stop()` | Stop and remove Docker containers |
| `check()` | Verify services are running |

**Search Configuration:**
```rust
pub struct SearchConfig {
    pub api_port: u16,
    pub api_container_id: String,
}
```

Sources: [libs/shared/src/models/integrations/search_service.rs:113-118](), [libs/shared/src/models/integrations/search_service.rs:232-415]()

### Search Workflow

The search system implements an iterative validation workflow:

1. **Query Analysis**: LLM analyzes search intent and reformulates query
2. **Search and Scrape**: Fetch results and scrape top URLs
3. **Validation**: LLM validates whether results satisfy requirements
4. **Iteration**: Refine query if needed, repeat up to 3 times

This workflow is implemented in `LocalClient::search_docs()` at [libs/api/src/local/mod.rs:509-614]().

## Request and Response Models

Various request types for integrations and external services.

### Search Requests

| Type | Fields | Purpose |
|------|--------|---------|
| `SearchDocsRequest` | `keywords`, `exclude_keywords`, `limit` | Web search request |
| `SearchMemoryRequest` | `keywords`, `start_time`, `end_time` | Memory search request |

Sources: [libs/api/src/models.rs:621-633]()

### Slack Integration Requests

| Type | Fields | Purpose |
|------|--------|---------|
| `SlackReadMessagesRequest` | `channel`, `limit` | Read channel messages |
| `SlackReadRepliesRequest` | `channel`, `ts` | Read thread replies |
| `SlackSendMessageRequest` | `channel`, `mrkdwn_text`, `thread_ts` | Send message |

Sources: [libs/api/src/models.rs:635-652]()

## Rulebook Models

Rulebooks contain reusable policies and standard operating procedures.

```mermaid
graph TB
    subgraph "RuleBook"
        RuleBookStruct[RuleBook]
        RuleBookId["id: String"]
        RuleBookUri["uri: String"]
        RuleBookDescription["description: String"]
        RuleBookContent["content: String"]
        RuleBookVisibility["visibility: RuleBookVisibility"]
        RuleBookTags["tags: Vec&lt;String&gt;"]
        RuleBookTimestamps["created_at: Option&lt;DateTime&lt;Utc&gt;&gt;<br/>updated_at: Option&lt;DateTime&lt;Utc&gt;&gt;"]
        
        RuleBookStruct --> RuleBookId
        RuleBookStruct --> RuleBookUri
        RuleBookStruct --> RuleBookContent
        RuleBookStruct --> RuleBookVisibility
        RuleBookStruct --> RuleBookTags
    end
    
    subgraph "ListRuleBook"
        ListStruct[ListRuleBook]
        ListId["id: String"]
        ListUri["uri: String"]
        ListDescription["description: String"]
        ListVisibility["visibility: RuleBookVisibility"]
        ListTags["tags: Vec&lt;String&gt;"]
        
        ListStruct --> ListUri
        ListStruct --> ListDescription
        ListStruct --> ListVisibility
    end
    
    subgraph "RuleBookVisibility Enum"
        Visibility[RuleBookVisibility]
        Public["Public"]
        Private["Private"]
        
        Visibility --> Public
        Visibility --> Private
    end
    
    RuleBookVisibility --> Visibility
    ListVisibility --> Visibility
```

Sources: [libs/api/src/models.rs:494-596]()

### Rulebook Operations

| Type | Purpose |
|------|---------|
| `ListRuleBook` | Lightweight listing without content |
| `RuleBook` | Full rulebook with content |
| `CreateRuleBookInput` | Request to create new rulebook |
| `CreateRuleBookResponse` | Returns ID of created rulebook |

The `uri` field serves as a unique identifier in the format `owner/rulebook-name`.

Sources: [libs/api/src/models.rs:556-596]()

## Supporting Types

### Document Models

| Type | Fields | Purpose |
|------|--------|---------|
| `Document` | `content`, `uri`, `provisioner` | Full document with content |
| `SimpleDocument` | `uri`, `content` | Simplified document structure |

Sources: [libs/api/src/models.rs:257-267]()

### Account Models

| Type | Fields | Purpose |
|------|--------|---------|
| `GetMyAccountResponse` | `username`, `id`, `first_name`, `last_name`, `email`, `scope` | User account information |
| `APIKeyScope` | `type`, `name` | API key scope restrictions |

Sources: [libs/api/src/models.rs:525-554]()

### Session Statistics

The `AgentSessionStats` type provides analytics on tool usage and time savings:

```rust
pub struct AgentSessionStats {
    pub total_tool_calls: u32,
    pub successful_tool_calls: u32,
    pub failed_tool_calls: u32,
    pub aborted_tool_calls: u32,
    pub tools_usage: Vec<ToolUsageStats>,
    pub total_time_saved_seconds: Option<u32>,
    // ... other fields
}
```

Sources: [libs/api/src/models.rs:462-493]()

### Error Types

The `ApiStreamError` enum represents streaming errors:

| Variant | Description |
|---------|-------------|
| `AgentInputInvalid(String)` | Invalid input provided |
| `AgentStateInvalid` | Agent state is corrupted |
| `AgentExecutionLimitExceeded` | Too many execution steps |
| `CopilotError` | Backend overloaded |
| `Unknown(String)` | Other errors |

Sources: [libs/api/src/models.rs:15-63]()
# Data Models and Types

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [libs/api/Cargo.toml](libs/api/Cargo.toml)
- [libs/api/src/lib.rs](libs/api/src/lib.rs)
- [libs/api/src/local/mod.rs](libs/api/src/local/mod.rs)
- [libs/api/src/models.rs](libs/api/src/models.rs)
- [libs/mcp/server/README_SECRETS.md](libs/mcp/server/README_SECRETS.md)
- [libs/shared/src/container.rs](libs/shared/src/container.rs)
- [libs/shared/src/models/integrations/mod.rs](libs/shared/src/models/integrations/mod.rs)
- [libs/shared/src/models/integrations/search_service.rs](libs/shared/src/models/integrations/search_service.rs)

</details>



This document describes the core data structures used throughout the stakpak agent system. These types define the structure of information exchanged between components including the AgentProvider implementations, MCP tools, and the TUI.

For information about the AgentProvider abstraction, see [AgentProvider Trait](#4.1). For implementation details, see [Remote Client Implementation](#4.2) and [Local Client Implementation](#4.3).

## Overview of Data Model Categories

The stakpak system organizes data models into several categories:

| Category | Primary Types | Purpose |
|----------|--------------|---------|
| **Agent Sessions** | `AgentSession`, `AgentCheckpointListItem`, `RunAgentOutput` | Session management and checkpointing |
| **Messages** | `ChatMessage`, `MessageContent`, `Tool`, `ToolCall` | OpenAI-compatible chat interface |
| **Agent State** | `AgentState`, `LLMInput`, `LLMOutput` | Internal agent execution state |
| **Code Blocks** | `Block`, `Dependency`, `Point`, `Segment` | Infrastructure code representation |
| **Search** | `SearchResult`, `ScrapedContent`, `SearchClient` | Document search and scraping |
| **Integrations** | `SearchDocsRequest`, `SlackReadMessagesRequest` | External service integration |
| **Rulebooks** | `RuleBook`, `ListRuleBook` | Documentation and policies |

Sources: [libs/api/src/models.rs:1-764](), [libs/shared/src/models/integrations/search_service.rs:1-422]()

## Agent Session Models

Agent sessions represent persistent conversation contexts with checkpointing capabilities for resumable execution.

**AgentSession Structure**

```mermaid
graph TB
    subgraph "AgentSession"
        Session[AgentSession]
        SessionId["id: Uuid"]
        SessionTitle["title: String"]
        SessionAgentId["agent_id: AgentID"]
        SessionVisibility["visibility: AgentSessionVisibility"]
        SessionCheckpoints["checkpoints: Vec&lt;AgentCheckpointListItem&gt;"]
        SessionTimestamps["created_at: DateTime&lt;Utc&gt;<br/>updated_at: DateTime&lt;Utc&gt;"]
        
        Session --> SessionId
        Session --> SessionTitle
        Session --> SessionAgentId
        Session --> SessionVisibility
        Session --> SessionCheckpoints
        Session --> SessionTimestamps
    end
    
    subgraph "AgentID Enum"
        AgentID["AgentID"]
        PabloV1["PabloV1"]
        AgentID --> PabloV1
    end
    
    subgraph "AgentSessionVisibility Enum"
        Visibility["AgentSessionVisibility"]
        Private["Private"]
        Public["Public"]
        Visibility --> Private
        Visibility --> Public
    end
    
    subgraph "AgentCheckpointListItem"
        Checkpoint["AgentCheckpointListItem"]
        CheckpointId["id: Uuid"]
        CheckpointStatus["status: AgentStatus"]
        CheckpointDepth["execution_depth: usize"]
        CheckpointParent["parent: Option&lt;AgentParentCheckpoint&gt;"]
        CheckpointTimestamps["created_at: DateTime&lt;Utc&gt;<br/>updated_at: DateTime&lt;Utc&gt;"]
        
        Checkpoint --> CheckpointId
        Checkpoint --> CheckpointStatus
        Checkpoint --> CheckpointDepth
        Checkpoint --> CheckpointParent
        Checkpoint --> CheckpointTimestamps
    end
    
    subgraph "AgentStatus Enum"
        Status["AgentStatus"]
        Running["Running"]
        Complete["Complete"]
        Blocked["Blocked"]
        Failed["Failed"]
        
        Status --> Running
        Status --> Complete
        Status --> Blocked
        Status --> Failed
    end
    
    SessionAgentId --> AgentID
    SessionVisibility --> Visibility
    SessionCheckpoints --> Checkpoint
    CheckpointStatus --> Status
```

Sources: [libs/api/src/models.rs:65-119]()

### Key Session Types

| Type | Fields | Purpose |
|------|--------|---------|
| `AgentSession` | `id`, `title`, `agent_id`, `visibility`, `checkpoints`, timestamps | Top-level session container |
| `AgentCheckpointListItem` | `id`, `status`, `execution_depth`, `parent`, timestamps | Individual checkpoint in execution tree |
| `AgentParentCheckpoint` | `id` | Reference to parent checkpoint for branching |
| `AgentStatus` | enum: Running, Complete, Blocked, Failed | Current checkpoint execution state |
| `AgentSessionVisibility` | enum: Private, Public | Session access control |

Sources: [libs/api/src/models.rs:65-166]()

### RunAgentOutput

The `RunAgentOutput` type represents the result of an agent execution, combining checkpoint metadata with the actual output:

```mermaid
graph TB
    subgraph "RunAgentOutput"
        Output[RunAgentOutput]
        OutputCheckpoint["checkpoint: AgentCheckpointListItem"]
        OutputSession["session: AgentSessionListItem"]
        OutputAgentOutput["output: AgentOutput"]
        
        Output --> OutputCheckpoint
        Output --> OutputSession
        Output --> OutputAgentOutput
    end
    
    subgraph "AgentOutput Tagged Union"
        AgentOutput["AgentOutput"]
        PabloV1Output["PabloV1<br/>messages: Vec&lt;ChatMessage&gt;<br/>node_states: serde_json::Value"]
        
        AgentOutput --> PabloV1Output
    end
    
    OutputAgentOutput --> AgentOutput
```

Sources: [libs/api/src/models.rs:180-254]()

The `AgentOutput` enum is a tagged union that varies by agent type. For `PabloV1` (the current agent), it contains:
- `messages`: The conversation history as `Vec<ChatMessage>`
- `node_states`: Arbitrary state data as JSON

Sources: [libs/api/src/models.rs:228-254]()

## Message and Chat Models

The system uses OpenAI-compatible message types for chat interactions, defined in the `stakpak-shared` crate.

**ChatMessage Structure**

```mermaid
graph TB
    subgraph "ChatMessage"
        Message[ChatMessage]
        MessageRole["role: Role"]
        MessageContent["content: Option&lt;MessageContent&gt;"]
        MessageName["name: Option&lt;String&gt;"]
        MessageToolCalls["tool_calls: Option&lt;Vec&lt;ToolCall&gt;&gt;"]
        MessageToolCallId["tool_call_id: Option&lt;String&gt;"]
        MessageUsage["usage: Option&lt;LLMTokenUsage&gt;"]
        
        Message --> MessageRole
        Message --> MessageContent
        Message --> MessageName
        Message --> MessageToolCalls
        Message --> MessageToolCallId
        Message --> MessageUsage
    end
    
    subgraph "Role Enum"
        Role["Role"]
        System["System"]
        User["User"]
        Assistant["Assistant"]
        Tool["Tool"]
        
        Role --> System
        Role --> User
        Role --> Assistant
        Role --> Tool
    end
    
    subgraph "MessageContent Enum"
        Content["MessageContent"]
        StringContent["String(String)"]
        ListContent["List(Vec&lt;MessageContentItem&gt;)"]
        
        Content --> StringContent
        Content --> ListContent
    end
    
    subgraph "ToolCall"
        ToolCallStruct[ToolCall]
        ToolCallId["id: String"]
        ToolCallType["type: String"]
        ToolCallFunction["function: FunctionCall"]
        
        ToolCallStruct --> ToolCallId
        ToolCallStruct --> ToolCallType
        ToolCallStruct --> ToolCallFunction
    end
    
    subgraph "FunctionCall"
        FunctionCallStruct[FunctionCall]
        FunctionName["name: String"]
        FunctionArgs["arguments: String"]
        
        FunctionCallStruct --> FunctionName
        FunctionCallStruct --> FunctionArgs
    end
    
    MessageRole --> Role
    MessageContent --> Content
    MessageToolCalls --> ToolCallStruct
    ToolCallStruct --> FunctionCallStruct
```

Sources: [libs/api/src/models.rs:8-9]() (imports from stakpak_shared)

### Tool Definition

The `Tool` struct defines available functions that the LLM can call:

```mermaid
graph TB
    subgraph "Tool"
        ToolStruct[Tool]
        ToolType["type: String"]
        ToolFunction["function: ToolFunction"]
        
        ToolStruct --> ToolType
        ToolStruct --> ToolFunction
    end
    
    subgraph "ToolFunction"
        Function[ToolFunction]
        FunctionName["name: String"]
        FunctionDescription["description: Option&lt;String&gt;"]
        FunctionParameters["parameters: Option&lt;serde_json::Value&gt;"]
        
        Function --> FunctionName
        Function --> FunctionDescription
        Function --> FunctionParameters
    end
    
    ToolFunction --> Function
```

Sources: [libs/api/src/models.rs:8-9]() (Tool imported from stakpak_shared)

### Usage Example

The message flow for a tool-calling conversation:

| Step | Role | Content | Tool Calls |
|------|------|---------|------------|
| 1 | User | "What files are in the current directory?" | None |
| 2 | Assistant | "" | `[{id: "call_1", function: {name: "run_command", arguments: '{"command": "ls"}'}}]` |
| 3 | Tool | "file1.txt\nfile2.py\nREADME.md" | None (tool_call_id: "call_1") |
| 4 | Assistant | "The directory contains: file1.txt, file2.py, and README.md" | None |

## Agent State Models

The `AgentState` struct represents the internal state during agent execution, used by hook systems and the LocalClient.

**AgentState and LLM Types**

```mermaid
graph TB
    subgraph "AgentState"
        State[AgentState]
        StateModel["agent_model: AgentModel"]
        StateMessages["messages: Vec&lt;ChatMessage&gt;"]
        StateTools["tools: Option&lt;Vec&lt;Tool&gt;&gt;"]
        StateLLMInput["llm_input: Option&lt;LLMInput&gt;"]
        StateLLMOutput["llm_output: Option&lt;LLMOutput&gt;"]
        StateMetadata["metadata: Option&lt;HashMap&lt;String, Value&gt;&gt;"]
        
        State --> StateModel
        State --> StateMessages
        State --> StateTools
        State --> StateLLMInput
        State --> StateLLMOutput
        State --> StateMetadata
    end
    
    subgraph "AgentModel Enum"
        AgentModel["AgentModel"]
        Smart["Smart"]
        Eco["Eco"]
        Recovery["Recovery"]
        
        AgentModel --> Smart
        AgentModel --> Eco
        AgentModel --> Recovery
    end
    
    subgraph "LLMInput"
        Input[LLMInput]
        InputModel["model: LLMModel"]
        InputMessages["messages: Vec&lt;LLMMessage&gt;"]
        InputMaxTokens["max_tokens: u32"]
        InputTools["tools: Option&lt;Vec&lt;Tool&gt;&gt;"]
        InputProviderOptions["provider_options: Option&lt;Value&gt;"]
        
        Input --> InputModel
        Input --> InputMessages
        Input --> InputMaxTokens
        Input --> InputTools
        Input --> InputProviderOptions
    end
    
    subgraph "LLMOutput"
        Output[LLMOutput]
        OutputNewMessage["new_message: LLMMessage"]
        OutputUsage["usage: LLMTokenUsage"]
        
        Output --> OutputNewMessage
        Output --> OutputUsage
    end
    
    StateModel --> AgentModel
    StateLLMInput --> Input
    StateLLMOutput --> Output
```

Sources: [libs/api/src/models.rs:654-763]()

### AgentState Methods

The `AgentState` provides methods for state manipulation:

| Method | Purpose |
|--------|---------|
| `new(agent_model, messages, tools)` | Create new state |
| `set_messages(messages)` | Update message history |
| `set_tools(tools)` | Update available tools |
| `set_llm_input(input)` | Set input before inference |
| `set_llm_output(message, usage)` | Store inference result |
| `append_new_message(message)` | Add message to history |

Sources: [libs/api/src/models.rs:721-763]()

### LLM Model Types

The system supports multiple LLM providers through the `LLMModel` enum (defined in stakpak_shared):
- OpenAI models (GPT-4o, GPT-5, etc.)
- Anthropic models (Claude 4.5 Sonnet, Haiku)
- Google Gemini models
- AWS Bedrock models

The `AgentModel` enum maps to these via `ModelSet`:
- **Smart**: High-capability model (default: Claude 4.5 Sonnet)
- **Eco**: Cost-effective model (default: Claude 4.5 Haiku)
- **Recovery**: Fallback model (default: GPT-5)

Sources: [libs/api/src/local/mod.rs:52-98]()

## Code Block Models

The `Block` struct represents parsed infrastructure code segments with dependency tracking.

**Block Structure and Dependencies**

```mermaid
graph TB
    subgraph "Local Storage Structure"
        LocalStore["LocalStore"]
        SessionPath["get_local_session_store_path()<br/>Returns: '.stakpak/session'"]
        WriteData["write_session_data(path, data)<br/>Creates session directory if needed"]
        ReadData["read_session_data(path)<br/>Reads from session directory"]
        
        LocalStore --> SessionPath
        LocalStore --> WriteData
        LocalStore --> ReadData
    end
    
    subgraph "Session Data Types"
        SecretsJson["secrets.json<br/>Secret redaction mappings"]
        OtherSession["Other session files<br/>Agent state, preferences, etc."]
        
        WriteData --> SecretsJson
        WriteData --> OtherSession
        ReadData --> SecretsJson
        ReadData --> OtherSession
    end
    
    subgraph "File Operations"
        CreateDir["create_dir_all() if needed"]
        WriteFile["fs::write()"]
        ReadFile["fs::read_to_string()"]
        ErrorHandling["Error handling with descriptive messages"]
        
        WriteData --> CreateDir
        WriteData --> WriteFile
        ReadData --> ReadFile
        WriteData --> ErrorHandling
        ReadData --> ErrorHandling
    end
```

**Local Storage Implementation**

Sources: [libs/shared/src/local_store.rs:1-32]()

### Session File Management

The `LocalStore` provides simple file-based session management:

| Method | Purpose | Error Handling |
|--------|---------|---------------|
| `get_local_session_store_path()` | Returns `.stakpak/session` path | None - pure function |
| `write_session_data(path, data)` | Writes data to session file | Creates directory, descriptive errors |
| `read_session_data(path)` | Reads data from session file | File not found and I/O errors |

The session directory structure supports various types of session data, with `secrets.json` being the primary file for secret redaction mappings.

Sources: [libs/shared/src/local_store.rs:9-31]()

---

# Page: MCP (Model Context Protocol) System

# MCP (Model Context Protocol) System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/stakpak-dark.png](assets/stakpak-dark.png)
- [assets/stakpak-light.png](assets/stakpak-light.png)
- [cli/src/utils/local_context.rs](cli/src/utils/local_context.rs)
- [libs/api/Cargo.toml](libs/api/Cargo.toml)
- [libs/api/src/lib.rs](libs/api/src/lib.rs)
- [libs/api/src/models.rs](libs/api/src/models.rs)
- [libs/mcp/server/README_SECRETS.md](libs/mcp/server/README_SECRETS.md)
- [libs/mcp/server/src/local_tools.rs](libs/mcp/server/src/local_tools.rs)
- [libs/shared/src/local_store.rs](libs/shared/src/local_store.rs)
- [libs/shared/src/remote_connection.rs](libs/shared/src/remote_connection.rs)
- [libs/shared/src/task_manager.rs](libs/shared/src/task_manager.rs)
- [libs/shared/src/utils.rs](libs/shared/src/utils.rs)

</details>



The MCP system enables Stakpak to integrate with external AI systems and code editors through a standardized protocol for tool execution. The system has three primary components: an **MCP Server** that exposes Stakpak's tools to external clients, an **MCP Client** that invokes tools during agent execution, and an **MCP Proxy** that multiplexes connections to multiple upstream MCP servers. This architecture allows Stakpak to function both as a tool provider (server) and a tool consumer (client/proxy).

The MCP system is central to Stakpak's security model, implementing mTLS encryption, dynamic secret redaction, and privacy-mode data filtering. It also provides the infrastructure for asynchronous task execution and remote operations over SSH/SFTP.

**Related Sections:**
- For CLI commands that launch MCP servers and proxies, see [CLI Interface](#2)
- For how the TUI displays and manages tool calls, see [Terminal User Interface (TUI)](#3)
- For the AgentProvider integration that uses the MCP client, see [Agent Provider and API](#4)
- For security features (secret management, Warden), see [Security and Privacy](#6)

**Subsections:**
- [5.1 MCP Architecture](#5.1) - Detailed architecture of server, client, and proxy components
- [5.2 Tool Container and Execution Flow](#5.2) - How tools are routed and executed
- [5.3 Local Tools Implementation](#5.3) - The 11 local tools and their implementations
- [5.4 Task Management System](#5.4) - Background task execution and monitoring
- [5.5 Remote Operations and SSH](#5.5) - SSH/SFTP for remote system operations

## MCP Components Overview

The MCP system consists of three distinct components that work together to provide comprehensive tool integration:

### MCP Server - Tool Provider

**Title:** MCP Server Component Architecture

```mermaid
graph TB
    ExternalClients["External Clients<br/>(Claude Desktop, Zed, Cursor)"]
    
    subgraph "MCP Server Process"
        ServerEntry["stakpak mcp start"]
        MCPServerConfig["MCPServerConfig"]
        ToolMode["ToolMode<br/>(local/remote/combined)"]
        
        subgraph "Tool Layer"
            ToolContainer["ToolContainer"]
            LocalTools["11 Local Tools"]
            RemoteTools["Remote AI Tools"]
        end
        
        subgraph "Execution Layer"
            TaskManager["TaskManager<br/>(background tasks)"]
            RemoteConnectionManager["RemoteConnectionManager<br/>(SSH/SFTP)"]
            SecretManager["SecretManager<br/>(Gitleaks integration)"]
        end
        
        ServerEntry --> MCPServerConfig
        MCPServerConfig --> ToolMode
        ToolMode --> ToolContainer
        ToolContainer --> LocalTools
        ToolContainer --> RemoteTools
        ToolContainer --> TaskManager
        ToolContainer --> RemoteConnectionManager
        ToolContainer --> SecretManager
    end
    
    ExternalClients --> ServerEntry
```

The MCP Server (`stakpak mcp start`) exposes Stakpak's tools to external AI agents and code editors. It implements three operational modes:
- **Local Mode** (`--tool-mode local`): File operations, command execution, password generation (no API key required)
- **Remote Mode** (`--tool-mode remote`): AI-powered code generation, documentation search, memory operations (API key required)  
- **Combined Mode** (`--tool-mode combined`): All tools available (default, API key required)

Sources: [README.md:241-272](), [libs/mcp/server/src/lib.rs:19-27](), [libs/mcp/server/src/lib.rs:188-214]()

### MCP Client - Tool Consumer

The MCP Client enables Stakpak's agent to invoke tools during execution. It's used by both the CLI's async mode and the TUI's interactive mode to execute tool calls returned by the LLM.

**Title:** MCP Client Integration Flow

```mermaid
graph LR
    subgraph "Agent Execution"
        LLMResponse["LLM Response<br/>(with tool calls)"]
        MCPClient["mcp::client<br/>MCPClient"]
        ToolInvocation["Tool Invocation"]
    end
    
    subgraph "Tool Sources"
        LocalMCPServer["Local MCP Server<br/>(stakpak mcp start)"]
        UpstreamServers["Upstream MCP Servers<br/>(configured in mcp.toml)"]
    end
    
    LLMResponse --> MCPClient
    MCPClient --> ToolInvocation
    ToolInvocation --> LocalMCPServer
    ToolInvocation --> UpstreamServers
```

The client handles tool discovery, parameter validation, and result processing. It integrates with Stakpak's security model by enforcing `allowed_tools` filtering and secret redaction.

Sources: [Diagram 5 from context]()

### MCP Proxy - Connection Multiplexer

**Title:** MCP Proxy Architecture

```mermaid
graph TB
    ExternalClients["External Clients"]
    
    subgraph "MCP Proxy Process"
        ProxyEntry["stakpak mcp proxy"]
        ConfigFile["mcp.toml<br/>(upstream server config)"]
        SessionManager["Session Manager"]
        Router["Connection Router"]
        
        ProxyEntry --> ConfigFile
        ConfigFile --> SessionManager
        SessionManager --> Router
    end
    
    subgraph "Upstream MCP Servers"
        Upstream1["MCP Server 1"]
        Upstream2["MCP Server 2"]
        UpstreamN["MCP Server N"]
    end
    
    ExternalClients --> ProxyEntry
    Router --> Upstream1
    Router --> Upstream2
    Router --> UpstreamN
```

The MCP Proxy (`stakpak mcp proxy`) acts as a reverse proxy that aggregates tools from multiple upstream MCP servers into a single endpoint. This allows external clients to access tools from different sources through one connection. Configuration is specified in `~/.stakpak/mcp.toml`.

Sources: [README.md:273-289](), [Diagram 4 from context]()

## Tool Categories and Capabilities

The MCP Server exposes 11 tools organized into several functional categories:

### File and Directory Operations

| Tool | Purpose | Local/Remote Support |
|------|---------|---------------------|
| `view` | Read file contents or list directory contents | Both (SSH/SFTP) |
| `create` | Create new files with specified content | Both (SSH/SFTP) |
| `str_replace` | Replace exact text matches in files | Both (SSH/SFTP) |
| `remove` | Delete files or directories | Both (SSH/SFTP) |

**Remote Path Format:** `user@host:/path` or `user@host#port:/path` for non-default SSH ports

Sources: [libs/mcp/server/src/local_tools.rs:83-100](), [libs/mcp/server/src/local_tools.rs:102-126](), [libs/mcp/server/src/local_tools.rs:128-144](), [libs/mcp/server/src/local_tools.rs:154-170]()

### Command Execution

| Tool | Purpose | Execution Model |
|------|---------|----------------|
| `run_command` | Execute shell commands synchronously | Blocks until complete |
| `run_command_task` | Execute shell commands asynchronously | Returns immediately with task ID |

Both tools support remote execution via SSH by specifying the `remote` parameter (`user@host` or `user@host:port`).

Sources: [libs/mcp/server/src/local_tools.rs:32-48](), [libs/mcp/server/src/local_tools.rs:198-245](), [libs/mcp/server/src/local_tools.rs:247-337]()

### Task Management

| Tool | Purpose |
|------|---------|
| `get_all_tasks` | List all background tasks with status |
| `get_task_details` | Get detailed output for a specific task |
| `cancel_task` | Terminate a running background task |
| `wait_for_tasks` | Block until specified tasks complete |

These tools enable monitoring and control of long-running operations like port forwarding, log tailing, or remote builds.

Sources: [libs/mcp/server/src/local_tools.rs:339-424](), [libs/mcp/server/src/local_tools.rs:426-459](), [libs/mcp/server/src/local_tools.rs:461-518](), [libs/mcp/server/src/local_tools.rs:520-591]()

### Utility Tools

| Tool | Purpose |
|------|---------|
| `generate_password` | Generate cryptographically secure passwords |
| `view_web_page` | Fetch and convert web pages to markdown |

Sources: [libs/mcp/server/src/local_tools.rs:147-152](), [libs/mcp/server/src/local_tools.rs:172-176]()

### Tool Mode Configuration

**Title:** Tool Mode and API Key Requirements

```mermaid
graph TB
    ToolMode["ToolMode enum"]
    
    LocalOnly["LocalOnly<br/>--tool-mode local"]
    RemoteOnly["RemoteOnly<br/>--tool-mode remote"]
    Combined["Combined<br/>(default)"]
    
    ToolMode --> LocalOnly
    ToolMode --> RemoteOnly
    ToolMode --> Combined
    
    LocalOnly --> LocalTools["11 Local Tools<br/>(no API key)"]
    RemoteOnly --> RemoteTools["AI Tools<br/>(API key required)"]
    Combined --> AllTools["Local + Remote<br/>(API key required)"]
```

Sources: [libs/mcp/server/src/lib.rs:19-27](), [README.md:246-250]()

## Security and Privacy Features

The MCP system implements multiple security layers to protect sensitive data and prevent destructive operations:

### Secret Redaction with Gitleaks

**Title:** Secret Detection and Substitution Flow

```mermaid
graph LR
    subgraph "Tool Output"
        RawOutput["Raw Command Output<br/>Contains: AWS_KEY=AKIAIO..."]
        SecretDetection["Gitleaks Detection"]
        RedactedOutput["Redacted Output<br/>AWS_KEY=[REDACTED_SECRET:aws-key:abc123]"]
    end
    
    subgraph "Session Storage"
        SecretsJSON[".stakpak/session/secrets.json"]
        Mapping["Placeholder → Actual Value"]
    end
    
    subgraph "Tool Input"
        LLMCommand["LLM Command<br/>echo [REDACTED_SECRET:aws-key:abc123]"]
        SecretRestoration["Secret Restoration"]
        ActualCommand["Actual Command<br/>echo AKIAIO..."]
    end
    
    RawOutput --> SecretDetection
    SecretDetection --> RedactedOutput
    SecretDetection --> Mapping
    Mapping --> SecretsJSON
    
    LLMCommand --> SecretRestoration
    SecretsJSON --> SecretRestoration
    SecretRestoration --> ActualCommand
```

The system uses Gitleaks to detect secrets in tool output (API keys, passwords, tokens) and replaces them with placeholders like `[REDACTED_SECRET:rule-id:hash]`. These placeholders can be used in subsequent commands and are automatically restored to actual values before execution. The mapping is stored in `.stakpak/session/secrets.json`.

**Controlled by:** `--disable-secret-redaction` flag (redaction enabled by default)

Sources: [libs/mcp/server/README_SECRETS.md:1-218](), [libs/mcp/server/src/local_tools.rs:192-196](), [README.md:269]()

### Privacy Mode

When enabled with `--privacy-mode`, the system redacts additional sensitive information:
- IP addresses
- AWS account IDs
- Other personally identifiable information

This is useful when sharing logs or screenshots of agent sessions.

Sources: [README.md:271](), [libs/mcp/server/src/lib.rs:19-27]()

### mTLS Encryption

**Title:** MCP Server TLS Configuration

```mermaid
graph TB
    MCPServer["MCP Server"]
    
    subgraph "TLS Modes"
        mTLSEnabled["mTLS Enabled<br/>(default)"]
        mTLSDisabled["mTLS Disabled<br/>--disable-mcp-mtls"]
    end
    
    subgraph "Certificate Chain"
        CertChain["CertificateChain"]
        ServerCert["Server Certificate"]
        PrivateKey["Private Key"]
        
        CertChain --> ServerCert
        CertChain --> PrivateKey
    end
    
    subgraph "Network Layer"
        TcpListener["TcpListener"]
        AxumServerTLS["axum_server::tls_rustls"]
        AxumServe["axum::serve"]
    end
    
    MCPServer --> mTLSEnabled
    MCPServer --> mTLSDisabled
    mTLSEnabled --> CertChain
    CertChain --> AxumServerTLS
    AxumServerTLS --> TcpListener
    mTLSDisabled --> AxumServe
```

By default, the MCP Server uses mutual TLS to encrypt all traffic between clients and the server. This provides end-to-end encryption and mutual authentication. TLS can be disabled for testing with `--disable-mcp-mtls`, but this is not recommended for production.

Sources: [README.md:57](), [README.md:264](), [libs/mcp/server/src/lib.rs:224-239]()

## Background Task Management

The MCP system includes a sophisticated task management layer for long-running operations:

**Title:** TaskManager Architecture

```mermaid
graph TB
    subgraph "Task Creation"
        RunCommandTask["run_command_task tool"]
        TaskManager["TaskManager"]
        TaskEntry["TaskEntry<br/>(task + handle + cancel_tx)"]
    end
    
    subgraph "Task Execution"
        LocalTask["execute_local_task()"]
        RemoteTask["execute_remote_task()"]
        TaskStatus["TaskStatus enum"]
    end
    
    subgraph "Task Monitoring"
        GetAllTasks["get_all_tasks tool"]
        GetTaskDetails["get_task_details tool"]
        WaitForTasks["wait_for_tasks tool"]
    end
    
    subgraph "Task Control"
        CancelTask["cancel_task tool"]
        CancellationToken["oneshot::Receiver<()>"]
    end
    
    RunCommandTask --> TaskManager
    TaskManager --> TaskEntry
    TaskEntry --> LocalTask
    TaskEntry --> RemoteTask
    LocalTask --> TaskStatus
    RemoteTask --> TaskStatus
    
    GetAllTasks --> TaskManager
    GetTaskDetails --> TaskManager
    WaitForTasks --> TaskManager
    CancelTask --> CancellationToken
```

Tasks are tracked with unique IDs and support status monitoring, output streaming, cancellation, and timeout enforcement. Both local and remote (SSH) tasks are supported. See [Task Management System](#5.4) for implementation details.

Sources: [libs/shared/src/task_manager.rs:1-724](), [libs/mcp/server/src/local_tools.rs:247-337]()

## Remote Operations via SSH

The MCP system supports executing operations on remote systems through SSH/SFTP:

**Title:** Remote Operation Path Detection and Routing

```mermaid
graph TB
    ToolCall["Tool Call"]
    PathDetection["is_remote_path()<br/>Check for user@host: pattern"]
    
    subgraph "Local Execution"
        LocalFS["LocalFileSystemProvider"]
        LocalCommand["std::process::Command"]
    end
    
    subgraph "Remote Execution"
        RemoteConnectionManager["RemoteConnectionManager"]
        RemoteConnection["RemoteConnection"]
        
        subgraph "SSH Layer"
            SSHClient["russh::client"]
            SFTPSession["russh_sftp::SftpSession"]
        end
        
        subgraph "Authentication"
            PasswordAuth["Password Authentication"]
            KeyAuth["Private Key Authentication"]
            AutoKeyDiscovery["Auto Key Discovery<br/>(~/.ssh/id_*)"]
        end
        
        RemoteConnectionManager --> RemoteConnection
        RemoteConnection --> SSHClient
        RemoteConnection --> SFTPSession
        RemoteConnection --> PasswordAuth
        RemoteConnection --> KeyAuth
        RemoteConnection --> AutoKeyDiscovery
    end
    
    ToolCall --> PathDetection
    PathDetection -->|"Local"| LocalFS
    PathDetection -->|"Local"| LocalCommand
    PathDetection -->|"user@host:/path"| RemoteConnectionManager
```

### Remote Path Formats

- Standard: `user@host:/path/to/file`
- Custom port: `user@host#port:/path/to/file`
- SSH URL: `ssh://user@host/path/to/file`

### Authentication Methods

1. **Password**: Provided via `password` parameter
2. **Private Key**: Specified via `private_key_path` parameter
3. **Auto-Discovery**: Automatically searches `~/.ssh/` for common key files (`id_ed25519`, `id_rsa`, `id_ecdsa`, `id_dsa`)

The `RemoteConnectionManager` maintains a connection pool to avoid re-authenticating for each operation. See [Remote Operations and SSH](#5.5) for detailed implementation.

Sources: [libs/shared/src/remote_connection.rs:1-653](), [libs/mcp/server/src/local_tools.rs:183-190](), [libs/mcp/server/src/local_tools.rs:250-257]()

## Integration with Security Systems

The MCP server integrates closely with the stakpak security infrastructure, particularly for secret detection and privacy protection.

### Security Feature Integration

```mermaid
graph LR
    subgraph "Security Configuration"
        RedactSecrets["redact_secrets: bool"]
        PrivacyMode["privacy_mode: bool"]
        
        RedactSecrets --> GitleaksInit["init_gitleaks_if_needed()"]
        PrivacyMode --> GitleaksInit
    end
    
    subgraph "Secret Detection"
        GitleaksInit --> GitleaksConfig["stakpak_shared::secrets::initialize_gitleaks_config()"]
        GitleaksConfig --> SecretRules["Secret detection rules"]
    end
    
    subgraph "Tool Container Security"
        ToolContainer["ToolContainer::new()"]
        SecurityParams["redact_secrets, privacy_mode parameters"]
        
        RedactSecrets --> SecurityParams
        PrivacyMode --> SecurityParams
        SecurityParams --> ToolContainer
    end
```

The security integration occurs at two levels:
- **Server Level**: Gitleaks configuration is initialized during server startup
- **Tool Level**: Security parameters are passed to the `ToolContainer` for per-operation filtering

Sources: [libs/mcp/server/src/lib.rs:81-94](), [libs/mcp/server/src/lib.rs:188-214]()

---

# Page: MCP Architecture

# MCP Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/stakpak-dark.png](assets/stakpak-dark.png)
- [assets/stakpak-light.png](assets/stakpak-light.png)
- [libs/api/Cargo.toml](libs/api/Cargo.toml)
- [libs/api/src/lib.rs](libs/api/src/lib.rs)
- [libs/api/src/models.rs](libs/api/src/models.rs)
- [libs/mcp/server/README_SECRETS.md](libs/mcp/server/README_SECRETS.md)

</details>



This document describes the Model Context Protocol (MCP) system architecture in Stakpak, including the server, client, and proxy components. MCP enables AI agents and code editors to securely interact with Stakpak's tools through a standardized protocol. For details on specific tool implementations, see [Local Tools Implementation](#5.3). For task management internals, see [Task Management System](#5.4). For remote operation details, see [Remote Operations and SSH](#5.5).

## Overview

The MCP system consists of three primary components that enable bidirectional communication between external AI systems and Stakpak's tool execution infrastructure:

1. **MCP Server**: Exposes Stakpak's 11 security-hardened tools to external clients
2. **MCP Client**: Allows Stakpak's agent to consume tools from external MCP servers
3. **MCP Proxy**: Multiplexes connections to multiple upstream MCP servers through a single interface

The system supports three operational modes for tools: local-only (no API key required), remote-only (AI-powered tools), and combined mode (both local and remote tools).

Sources: [README.md:241-289](), [libs/mcp/server/README_SECRETS.md:1-218]()

## System Architecture

The following diagram shows how MCP components interact with external systems and internal Stakpak components:

```mermaid
graph TB
    subgraph "External Clients"
        CLAUDE["Claude Desktop"]
        ZED["Zed Editor"]
        CURSOR["Cursor Editor"]
        OTHER_AI["Other AI Agents"]
    end
    
    subgraph "Stakpak MCP Server"
        SERVER_CMD["stakpak mcp start"]
        TOOL_CONTAINER["ToolContainer<br/>11 Tools Implementation"]
        
        subgraph "Tool Modes"
            LOCAL_MODE["--tool-mode local<br/>File ops & commands only"]
            REMOTE_MODE["--tool-mode remote<br/>AI-powered tools"]
            COMBINED_MODE["--tool-mode combined<br/>All tools (default)"]
        end
        
        subgraph "Security Layer"
            MTLS["mTLS Transport Encryption"]
            SECRET_MGR["SecretManager<br/>Gitleaks Integration"]
            PRIVACY["Privacy Mode<br/>IP/Account Redaction"]
        end
        
        TASK_MGR["TaskManager<br/>Background Execution"]
        REMOTE_CONN["RemoteConnectionManager<br/>SSH/SFTP"]
    end
    
    subgraph "Stakpak MCP Proxy"
        PROXY_CMD["stakpak mcp proxy"]
        CONFIG_FILE["mcp.toml<br/>Upstream Configuration"]
        SESSION_MGR["Session Manager"]
    end
    
    subgraph "Upstream MCP Servers"
        UPSTREAM1["Server 1"]
        UPSTREAM2["Server 2"]
        UPSTREAMN["Server N"]
    end
    
    subgraph "Stakpak MCP Client"
        CLIENT_LIB["libs/mcp/client"]
        TOOL_DISCOVERY["Tool Discovery"]
        TOOL_INVOKE["Tool Invocation"]
    end
    
    CLAUDE --> SERVER_CMD
    ZED --> SERVER_CMD
    CURSOR --> SERVER_CMD
    OTHER_AI --> SERVER_CMD
    
    SERVER_CMD --> TOOL_CONTAINER
    TOOL_CONTAINER --> LOCAL_MODE
    TOOL_CONTAINER --> REMOTE_MODE
    TOOL_CONTAINER --> COMBINED_MODE
    
    LOCAL_MODE --> TASK_MGR
    REMOTE_MODE --> TASK_MGR
    COMBINED_MODE --> TASK_MGR
    
    TASK_MGR --> REMOTE_CONN
    
    SERVER_CMD --> MTLS
    SERVER_CMD --> SECRET_MGR
    SERVER_CMD --> PRIVACY
    
    CLAUDE --> PROXY_CMD
    ZED --> PROXY_CMD
    
    PROXY_CMD --> CONFIG_FILE
    PROXY_CMD --> SESSION_MGR
    SESSION_MGR --> UPSTREAM1
    SESSION_MGR --> UPSTREAM2
    SESSION_MGR --> UPSTREAMN
    
    CLIENT_LIB --> TOOL_DISCOVERY
    TOOL_DISCOVERY --> TOOL_INVOKE
```

**MCP System Component Interaction**

Sources: [README.md:241-289](), Diagram 4 from high-level overview

## Component Details

### MCP Server

The MCP Server is launched via `stakpak mcp start` and exposes Stakpak's tool set to external AI systems through the Model Context Protocol.

#### Command-Line Interface

```bash
# Local tools only (no API key required)
stakpak mcp start --tool-mode local

# Remote AI-powered tools only
stakpak mcp start --tool-mode remote

# Combined mode (default)
stakpak mcp start

# Disable mTLS (NOT recommended)
stakpak mcp start --disable-mcp-mtls

# Additional security options
stakpak mcp start --disable-secret-redaction  # NOT recommended
stakpak mcp start --privacy-mode               # Redact IPs, account IDs
stakpak mcp start --enable-slack-tools         # Experimental
```

Sources: [README.md:251-271]()

#### Tool Modes

The MCP Server supports three operational modes:

| Mode | Flag | API Key Required | Tools Available | Use Case |
|------|------|------------------|----------------|----------|
| Local | `--tool-mode local` | No | File operations, command execution | Offline operation, basic automation |
| Remote | `--tool-mode remote` | Yes | AI code generation, search tools | AI-assisted development |
| Combined | `--tool-mode combined` | Yes | All local + remote tools | Full-featured operation (default) |

**Local Mode Tools**:
- `run_command`, `run_command_task`
- `view`, `create`, `str_replace`, `remove`
- `get_all_tasks`, `cancel_task`, `wait_for_tasks`
- `generate_password`, `view_web_page`

**Remote Mode Tools**:
- AI-powered code generation
- Document search capabilities
- Memory search operations

Sources: [README.md:245-249]()

### MCP Proxy

The MCP Proxy multiplexes connections to multiple upstream MCP servers, allowing clients to access multiple tool providers through a single endpoint.

```bash
# Start with automatic config discovery
stakpak mcp proxy

# Specify explicit config file
stakpak mcp proxy --config-file ~/.stakpak/mcp.toml

# With security options
stakpak mcp proxy --privacy-mode
```

#### Proxy Configuration

The proxy uses `mcp.toml` to define upstream servers:

```mermaid
graph LR
    CLIENT["MCP Client<br/>(Claude, Zed)"]
    PROXY["MCP Proxy<br/>Session Manager"]
    CONFIG["mcp.toml<br/>Configuration"]
    
    UPSTREAM1["Upstream Server 1"]
    UPSTREAM2["Upstream Server 2"]
    UPSTREAMN["Upstream Server N"]
    
    CLIENT --> PROXY
    PROXY --> CONFIG
    PROXY --> UPSTREAM1
    PROXY --> UPSTREAM2
    PROXY --> UPSTREAMN
```

**MCP Proxy Connection Multiplexing**

Sources: [README.md:273-289]()

### MCP Client

The MCP Client (`libs/mcp/client`) enables Stakpak's agent to consume tools from external MCP servers. This allows the agent to leverage tools provided by other systems.

```mermaid
graph TB
    AGENT["Stakpak Agent"]
    CLIENT["MCP Client<br/>libs/mcp/client"]
    
    subgraph "Client Operations"
        DISCOVER["Tool Discovery<br/>List available tools"]
        FILTER["Tool Filtering<br/>allowed_tools config"]
        INVOKE["Tool Invocation<br/>Execute with params"]
    end
    
    EXTERNAL1["External MCP Server 1"]
    EXTERNAL2["External MCP Server 2"]
    
    AGENT --> CLIENT
    CLIENT --> DISCOVER
    DISCOVER --> FILTER
    FILTER --> INVOKE
    
    INVOKE --> EXTERNAL1
    INVOKE --> EXTERNAL2
```

**MCP Client Tool Discovery and Invocation**

Sources: Diagram 5 from high-level overview, [README.md:273-289]()

## Security Architecture

The MCP system implements multiple layers of security to protect sensitive data and operations.

### mTLS Transport Security

Mutual TLS (mTLS) is enabled by default for all MCP communications, providing:
- Bidirectional authentication (client and server verify each other)
- End-to-end encryption of all protocol messages
- Protection against man-in-the-middle attacks

Can be disabled with `--disable-mcp-mtls` flag (not recommended for production).

Sources: [README.md:57](), [README.md:264]()

### Dynamic Secret Substitution

The MCP Server implements dynamic secret redaction and restoration using the Gitleaks engine:

```mermaid
graph TB
    subgraph "Secret Detection Flow"
        INPUT["Command/File Content<br/>Contains Secrets"]
        DETECT["Gitleaks Engine<br/>Pattern Matching"]
        GENERATE["Generate Placeholder<br/>[REDACTED_SECRET:rule-id:hash]"]
        STORE["Store Mapping<br/>.stakpak/session/secrets.json"]
        OUTPUT["Redacted Content<br/>To LLM"]
    end
    
    subgraph "Secret Restoration Flow"
        LLM_INPUT["LLM Input<br/>Contains Placeholders"]
        LOOKUP["Lookup Mapping<br/>Session File"]
        RESTORE["Restore Original Values"]
        EXECUTE["Execute with Real Secrets"]
    end
    
    INPUT --> DETECT
    DETECT --> GENERATE
    GENERATE --> STORE
    STORE --> OUTPUT
    
    LLM_INPUT --> LOOKUP
    LOOKUP --> RESTORE
    RESTORE --> EXECUTE
```

**Secret Redaction and Restoration Flow**

The system uses placeholders in the format `[REDACTED_SECRET:rule-id:short-hash]` where:
- `rule-id`: The Gitleaks rule that detected the secret (e.g., "api-key", "aws-access-key")
- `short-hash`: A short hash to ensure uniqueness and prevent collisions

Session mappings are stored in `.stakpak/session/secrets.json`:

```json
{
  "[REDACTED_SECRET:api-key:bga278]": "api_125136713",
  "[REDACTED_SECRET:token:def456]": "ghp_1234567890abcdef",
  "[REDACTED_SECRET:aws-key:xyz789]": "AKIAIOSFODNN7EXAMPLE"
}
```

Sources: [libs/mcp/server/README_SECRETS.md:1-218]()

#### Tool Integration with Secret Redaction

All MCP tools integrate with the secret substitution system:

| Tool | Redaction Point | Restoration Point |
|------|----------------|-------------------|
| `run_command` | Command output | Command input |
| `view` | File contents shown to LLM | N/A |
| `str_replace` | N/A | old_string, new_string parameters |
| `create` | N/A | File content before writing |
| `insert` | N/A | Inserted text before writing |
| `generate_code` | Generated code shown to LLM | N/A |

Sources: [libs/mcp/server/README_SECRETS.md:96-104]()

### Privacy Mode

When enabled with `--privacy-mode`, the system redacts additional sensitive data:
- IP addresses
- AWS account IDs
- Other personally identifiable information

Sources: [README.md:60](), [README.md:270](), [README.md:288]()

## Tool Container Architecture

The `ToolContainer` class implements all 11 MCP tools and manages their execution lifecycle:

```mermaid
graph TB
    CONTAINER["ToolContainer<br/>Central Tool Registry"]
    
    subgraph "File Operations"
        VIEW["view<br/>Read file contents"]
        CREATE["create<br/>Write new file"]
        STR_REPLACE["str_replace<br/>Replace text in file"]
        REMOVE["remove<br/>Delete file"]
    end
    
    subgraph "Command Execution"
        RUN_CMD["run_command<br/>Synchronous execution"]
        RUN_TASK["run_command_task<br/>Async background task"]
    end
    
    subgraph "Task Management"
        GET_TASKS["get_all_tasks<br/>List running tasks"]
        CANCEL["cancel_task<br/>Stop background task"]
        WAIT["wait_for_tasks<br/>Block until completion"]
    end
    
    subgraph "Utilities"
        GEN_PASS["generate_password<br/>Secure random password"]
        VIEW_WEB["view_web_page<br/>Fetch web content"]
    end
    
    CONTAINER --> VIEW
    CONTAINER --> CREATE
    CONTAINER --> STR_REPLACE
    CONTAINER --> REMOVE
    
    CONTAINER --> RUN_CMD
    CONTAINER --> RUN_TASK
    
    CONTAINER --> GET_TASKS
    CONTAINER --> CANCEL
    CONTAINER --> WAIT
    
    CONTAINER --> GEN_PASS
    CONTAINER --> VIEW_WEB
    
    RUN_TASK --> TASK_MGR["TaskManager<br/>Background execution"]
    VIEW --> BACKUP["FileBackupManager<br/>Auto backups"]
    CREATE --> BACKUP
    STR_REPLACE --> BACKUP
```

**ToolContainer and Tool Organization**

Sources: Diagram 4 from high-level overview

## Configuration Files

### Server Configuration

The MCP Server reads configuration from the main Stakpak config file (`~/.stakpak/config.toml`) for:
- API credentials (if using remote tools)
- Profile selection
- Tool access permissions

### Proxy Configuration

The MCP Proxy requires `mcp.toml` (typically at `~/.stakpak/mcp.toml`) to define upstream servers. The proxy automatically discovers this file or accepts an explicit path via `--config-file`.

### Session State

Runtime state is maintained in `.stakpak/session/`:
- `secrets.json`: Secret redaction mappings
- Task state and output files
- Temporary execution artifacts

Sources: [libs/mcp/server/README_SECRETS.md:51-69](), [README.md:281]()

## Integration with Stakpak Agent

The Stakpak agent can act as both an MCP server (exposing its tools) and an MCP client (consuming external tools):

```mermaid
graph TB
    subgraph "Stakpak Agent Process"
        AGENT["Agent Logic"]
        
        subgraph "As MCP Server"
            SERVER["MCP Server<br/>Expose tools to AI"]
            TOOLS["Internal Tools"]
        end
        
        subgraph "As MCP Client"
            CLIENT["MCP Client<br/>Consume external tools"]
            EXTERNAL["External Tool Calls"]
        end
    end
    
    subgraph "External AI Systems"
        CLAUDE["Claude Desktop"]
        ZED["Zed Editor"]
    end
    
    subgraph "External MCP Servers"
        EXT_SERVER1["Server 1"]
        EXT_SERVER2["Server 2"]
    end
    
    CLAUDE --> SERVER
    ZED --> SERVER
    SERVER --> TOOLS
    
    AGENT --> CLIENT
    CLIENT --> EXTERNAL
    EXTERNAL --> EXT_SERVER1
    EXTERNAL --> EXT_SERVER2
```

**Dual Role: MCP Server and Client**

The agent uses the MCP Client to discover and invoke tools from upstream servers, while simultaneously exposing its own tools via the MCP Server. The MCP Proxy can sit in front of multiple upstream servers to simplify client configuration.

Sources: Diagram 4 from high-level overview, [README.md:241-289]()

## Command Reference

| Command | Purpose | Key Flags |
|---------|---------|-----------|
| `stakpak mcp start` | Start MCP server exposing tools | `--tool-mode`, `--disable-mcp-mtls`, `--privacy-mode`, `--disable-secret-redaction`, `--enable-slack-tools` |
| `stakpak mcp proxy` | Start MCP proxy for multiplexing | `--config-file`, `--disable-secret-redaction`, `--privacy-mode` |

Sources: [README.md:241-289]()

---

# Page: Tool Container and Execution Flow

# Tool Container and Routing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cli/src/utils/local_context.rs](cli/src/utils/local_context.rs)
- [libs/mcp/server/src/local_tools.rs](libs/mcp/server/src/local_tools.rs)
- [libs/shared/src/local_store.rs](libs/shared/src/local_store.rs)
- [libs/shared/src/remote_connection.rs](libs/shared/src/remote_connection.rs)
- [libs/shared/src/task_manager.rs](libs/shared/src/task_manager.rs)
- [libs/shared/src/utils.rs](libs/shared/src/utils.rs)

</details>



This document covers how tools are organized, routed, and executed within the MCP (Model Context Protocol) system. It explains the tool container architecture, request routing mechanisms, execution flows, and session management that enables both local and remote tool capabilities.

For information about specific local tools, see [Local Tools](#4.2). For details about remote AI-powered tools, see [Remote Tools](#4.3). For MCP server configuration and initialization, see [Server Architecture](#4.1).

## Tool Container Architecture

The MCP system uses a centralized tool container approach where all tools are managed through a single MCP server instance that acts as the execution environment and router.

```mermaid
graph TB
    subgraph "MCP Tool Container"
        MCPServer["MCP Server<br/>rmcp::server::Server"]
        ToolRegistry["Tool Registry<br/>HashMap<String, Tool>"]
        ToolRouter["Tool Router<br/>tools/call handler"]
        
        MCPServer --> ToolRegistry
        MCPServer --> ToolRouter
        ToolRouter --> ToolRegistry
    end
    
    subgraph "Tool Categories"
        LocalTools["Local Tools<br/>file operations, shell, tasks"]
        RemoteTools["Remote Tools<br/>AI generation, search, memory"]
        
        ToolRegistry --> LocalTools
        ToolRegistry --> RemoteTools
    end
    
    subgraph "Client Interface"
        APIClient["stakpak-api::Client"]
        JSONRPCCall["JSON-RPC tools/call"]
        ToolsCallParams["ToolsCallParams<br/>{name, arguments}"]
        
        APIClient --> JSONRPCCall
        JSONRPCCall --> ToolsCallParams
    end
    
    subgraph "Session Management"
        LocalStore["LocalStore<br/>.stakpak/session/"]
        SecretManager["Secret Redaction<br/>gitleaks integration"]
        
        ToolRouter --> LocalStore
        ToolRouter --> SecretManager
    end
    
    ToolsCallParams --> ToolRouter
    
    style MCPServer fill:#f9f9f9,stroke:#333,stroke-width:2px
    style ToolRouter fill:#f0f8ff,stroke:#333,stroke-width:2px
```

**Tool Container Components**

| Component | Purpose | Implementation |
|-----------|---------|----------------|
| `MCP Server` | Central container and request handler | `rmcp::server::Server` |
| `Tool Registry` | Maps tool names to implementations | `HashMap<String, Tool>` |
| `Tool Router` | Routes requests to appropriate tools | JSON-RPC `tools/call` method handler |
| `Session Manager` | Maintains state and secrets | `.stakpak/session/` directory |

Sources: [libs/api/src/lib.rs:702-735](), [libs/shared/src/local_store.rs:9-31]()

## Tool Routing Mechanisms

The MCP server implements tool routing through a JSON-RPC interface that dispatches tool calls based on tool names and modes.

### JSON-RPC Tool Call Protocol

```mermaid
graph LR
    subgraph "Client Side"
        ClientCall["Client::call_mcp_tool()"]
        ToolsCallParams["ToolsCallParams<br/>{name: String, arguments: Value}"]
        JSONPayload["JSON-RPC Payload<br/>{method: 'tools/call', params: {...}}"]
    end
    
    subgraph "Transport"
        HTTPPost["HTTP POST /mcp"]
        JSONRequest["JSON-RPC 2.0 Request"]
    end
    
    subgraph "Server Side"
        MCPHandler["MCP tools/call Handler"]
        ToolDispatcher["Tool Dispatcher"]
        ToolExecution["Tool Execution"]
        JSONResponse["JSON-RPC Response<br/>{result: {content: Vec<Content>}}"]
    end
    
    ClientCall --> ToolsCallParams
    ToolsCallParams --> JSONPayload
    JSONPayload --> HTTPPost
    HTTPPost --> JSONRequest
    JSONRequest --> MCPHandler
    MCPHandler --> ToolDispatcher
    ToolDispatcher --> ToolExecution
    ToolExecution --> JSONResponse
    
    style MCPHandler fill:#e6f3ff,stroke:#333,stroke-width:2px
    style ToolDispatcher fill:#fff2e6,stroke:#333,stroke-width:2px
```

The routing protocol follows this structure:

1. **Request Format**: JSON-RPC 2.0 with `method: "tools/call"`
2. **Parameters**: `{name: tool_name, arguments: tool_args}`
3. **Response**: `{result: {content: Vec<Content>}}`
4. **Error Handling**: Standard JSON-RPC error responses

Sources: [libs/api/src/lib.rs:705-713](), [libs/api/src/models.rs:1129-1137]()

### Tool Mode Routing

The MCP server supports different tool modes that determine which tools are available:

```mermaid
graph TD
    subgraph "Tool Mode Configuration"
        ToolMode["Tool Mode Setting"]
        LocalMode["Local Mode<br/>local tools only"]
        RemoteMode["Remote Mode<br/>API key required"]
        CombinedMode["Combined Mode<br/>all tools available"]
        
        ToolMode --> LocalMode
        ToolMode --> RemoteMode  
        ToolMode --> CombinedMode
    end
    
    subgraph "Tool Categories"
        FileOps["File Operations<br/>create, view, str_replace"]
        ShellOps["Shell Operations<br/>run_command"]
        TaskMgmt["Task Management<br/>background processes"]
        AIGeneration["AI Generation<br/>generate_code"]
        SearchOps["Search Operations<br/>query_blocks, memory_search"]
        DocOps["Documentation<br/>rulebook access"]
    end
    
    subgraph "Routing Logic"
        ToolRouter["Tool Router"]
        AuthCheck["API Key Check"]
        ToolLookup["Tool Registry Lookup"]
        ToolFilter["Mode Filter"]
    end
    
    LocalMode --> FileOps
    LocalMode --> ShellOps
    LocalMode --> TaskMgmt
    
    RemoteMode --> AIGeneration
    RemoteMode --> SearchOps
    RemoteMode --> DocOps
    
    CombinedMode --> FileOps
    CombinedMode --> ShellOps
    CombinedMode --> TaskMgmt
    CombinedMode --> AIGeneration
    CombinedMode --> SearchOps
    CombinedMode --> DocOps
    
    ToolRouter --> AuthCheck
    AuthCheck --> ToolLookup
    ToolLookup --> ToolFilter
    
    style ToolRouter fill:#f0f8ff,stroke:#333,stroke-width:2px
    style AuthCheck fill:#fff0f0,stroke:#333,stroke-width:2px
```

**Tool Mode Routing Rules**

| Mode | Authentication | Available Tools | Use Case |
|------|---------------|-----------------|----------|
| Local | None required | File, shell, task tools only | Offline development |
| Remote | API key required | AI-powered tools only | Cloud-based operations |
| Combined | API key required | All tools available | Full functionality |

Sources: Based on context diagrams and tool architecture

## Tool Execution Flow

The tool execution flow involves request processing, security handling, tool invocation, and response formatting.

### Request Processing Pipeline

```mermaid
graph TD
    subgraph "Request Processing"
        IncomingRequest["Incoming JSON-RPC Request"]
        RequestValidation["Request Validation<br/>schema, parameters"]
        ToolLookup["Tool Lookup<br/>registry.get(tool_name)"]
        AuthCheck["Authentication Check<br/>API key validation"]
    end
    
    subgraph "Security Layer"
        SecretDetection["Secret Detection<br/>gitleaks scan"]
        SecretSubstitution["Secret Substitution<br/>restore placeholders"]
        InputSanitization["Input Sanitization"]
    end
    
    subgraph "Tool Execution"
        ToolInvocation["Tool Invocation<br/>tool.execute(args)"]
        ResourceAccess["Resource Access<br/>filesystem, network, etc"]
        OutputCapture["Output Capture<br/>stdout, stderr, files"]
    end
    
    subgraph "Response Processing"
        OutputRedaction["Output Redaction<br/>secret detection"]
        SessionStorage["Session Storage<br/>update redaction map"]
        ResponseFormat["Response Formatting<br/>Vec<Content>"]
        JSONResponse["JSON-RPC Response"]
    end
    
    IncomingRequest --> RequestValidation
    RequestValidation --> ToolLookup
    ToolLookup --> AuthCheck
    AuthCheck --> SecretDetection
    SecretDetection --> SecretSubstitution
    SecretSubstitution --> InputSanitization
    InputSanitization --> ToolInvocation
    ToolInvocation --> ResourceAccess
    ResourceAccess --> OutputCapture
    OutputCapture --> OutputRedaction
    OutputRedaction --> SessionStorage
    SessionStorage --> ResponseFormat
    ResponseFormat --> JSONResponse
    
    style ToolInvocation fill:#e6ffe6,stroke:#333,stroke-width:2px
    style SecretDetection fill:#ffe6e6,stroke:#333,stroke-width:2px
    style OutputRedaction fill:#ffe6e6,stroke:#333,stroke-width:2px
```

**Execution Pipeline Stages**

1. **Validation**: JSON-RPC schema and parameter validation
2. **Authorization**: API key check for remote tools
3. **Security**: Secret detection and placeholder substitution
4. **Execution**: Tool invocation with resource access
5. **Post-processing**: Output redaction and session updates
6. **Response**: Formatted JSON-RPC response

Sources: [libs/mcp/server/README_SECRETS.md:75-103](), [libs/api/src/lib.rs:725-734]()

## Session Management and State

The MCP system maintains session state for tool executions, particularly for secret redaction mappings and background task management.

### Session Storage Architecture

```mermaid
graph TB
    subgraph "Session Directory Structure"
        SessionRoot[".stakpak/session/"]
        SecretsFile["secrets.json<br/>redaction mappings"]
        TaskState["task state files"]
        TempFiles["temporary data"]
        
        SessionRoot --> SecretsFile
        SessionRoot --> TaskState
        SessionRoot --> TempFiles
    end
    
    subgraph "LocalStore Interface"
        LocalStore["LocalStore::get_local_session_store_path()"]
        WriteSession["LocalStore::write_session_data()"]
        ReadSession["LocalStore::read_session_data()"]
        
        LocalStore --> SessionRoot
        WriteSession --> SessionRoot
        ReadSession --> SessionRoot
    end
    
    subgraph "Secret Management"
        RedactionMap["Redaction Map<br/>placeholder -> secret"]
        LoadMap["load_session_redaction_map()"]
        SaveMap["save_session_redaction_map()"]
        AddMapping["add_to_session_redaction_map()"]
        
        SecretsFile --> RedactionMap
        LoadMap --> RedactionMap
        SaveMap --> RedactionMap
        AddMapping --> RedactionMap
    end
    
    subgraph "Tool Integration"
        ToolExecution["Tool Execution"]
        SecretRestore["restore_secrets_in_string()"]
        SecretRedact["redact_and_store_secrets()"]
        
        ToolExecution --> SecretRestore
        ToolExecution --> SecretRedact
        SecretRestore --> LoadMap
        SecretRedact --> SaveMap
    end
    
    style SessionRoot fill:#f0f8ff,stroke:#333,stroke-width:2px
    style RedactionMap fill:#fff0f0,stroke:#333,stroke-width:2px
```

**Session Data Management**

| Component | File Path | Purpose | Format |
|-----------|-----------|---------|--------|
| `LocalStore` | `.stakpak/session/` | Session directory management | Directory structure |
| Secret mappings | `secrets.json` | Placeholder-to-secret mappings | JSON object |
| Task state | Various files | Background task persistence | Tool-specific |

### Secret Redaction Session Flow

The secret redaction system maintains session state to enable secure tool operations:

```mermaid
sequenceDiagram
    participant Tool as "Tool Execution"
    participant SecretMgr as "Secret Manager"
    participant Session as "Session Store"
    participant LLM as "LLM/Client"
    
    Note over Tool,LLM: Tool Output Processing
    Tool->>SecretMgr: redact_and_store_secrets(output)
    SecretMgr->>SecretMgr: detect secrets (gitleaks)
    SecretMgr->>SecretMgr: generate placeholders
    SecretMgr->>Session: save_session_redaction_map(mappings)
    SecretMgr->>Tool: redacted_output
    Tool->>LLM: [REDACTED_SECRET:rule:hash]
    
    Note over Tool,LLM: Tool Input Processing  
    LLM->>Tool: command with placeholders
    Tool->>SecretMgr: restore_secrets_in_string(command)
    SecretMgr->>Session: load_session_redaction_map()
    Session->>SecretMgr: placeholder mappings
    SecretMgr->>SecretMgr: substitute real secrets
    SecretMgr->>Tool: restored_command
    Tool->>Tool: execute with real secrets
```

**Secret Session Management**

1. **Detection**: Tools scan output for secrets using gitleaks rules
2. **Placeholder Generation**: Unique identifiers like `[REDACTED_SECRET:api-key:abc123]`
3. **Session Storage**: Mappings stored in `secrets.json` with pretty-printing
4. **Restoration**: Placeholders replaced with real values during execution
5. **Persistence**: Session data maintained throughout tool execution lifecycle

Sources: [libs/mcp/server/README_SECRETS.md:52-69](), [libs/shared/src/local_store.rs:13-30]()

## Error Handling and Diagnostics

The tool container implements comprehensive error handling for routing and execution failures.

### Error Response Structure

```mermaid
graph LR
    subgraph "Error Sources"
        ValidationError["Request Validation<br/>invalid JSON-RPC"]
        AuthError["Authentication Error<br/>missing/invalid API key"]  
        ToolNotFound["Tool Not Found<br/>unknown tool name"]
        ExecutionError["Execution Error<br/>tool runtime failure"]
        SecurityError["Security Error<br/>secret handling failure"]
    end
    
    subgraph "Error Handling"
        ErrorRouter["Error Router"]
        ErrorFormatter["Error Formatter"]
        LoggingSystem["Logging System"]
    end
    
    subgraph "Error Responses"
        JSONRPCError["JSON-RPC Error Response<br/>{error: {code, message}}"]
        ClientError["Client Error Handling<br/>stakpak-api::Client"]
        UserFeedback["User Error Display"]
    end
    
    ValidationError --> ErrorRouter
    AuthError --> ErrorRouter
    ToolNotFound --> ErrorRouter
    ExecutionError --> ErrorRouter
    SecurityError --> ErrorRouter
    
    ErrorRouter --> ErrorFormatter
    ErrorRouter --> LoggingSystem
    ErrorFormatter --> JSONRPCError
    JSONRPCError --> ClientError
    ClientError --> UserFeedback
    
    style ErrorRouter fill:#ffe6e6,stroke:#333,stroke-width:2px
    style JSONRPCError fill:#fff0e6,stroke:#333,stroke-width:2px
```

**Error Categories and Handling**

| Error Type | HTTP Status | JSON-RPC Code | Client Handling |
|------------|-------------|---------------|-----------------|
| Validation Error | 400 | -32600 | Parameter correction |
| Authentication Error | 401 | -32001 | Login prompt |
| Tool Not Found | 404 | -32601 | Tool availability check |
| Execution Error | 500 | -32000 | Retry with different params |
| Security Error | 403 | -32002 | Permission escalation |

Sources: [libs/api/src/lib.rs:51-69]()

---

# Page: Local Tools Implementation

# Local Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cli/src/utils/local_context.rs](cli/src/utils/local_context.rs)
- [libs/mcp/server/src/local_tools.rs](libs/mcp/server/src/local_tools.rs)
- [libs/shared/src/local_store.rs](libs/shared/src/local_store.rs)
- [libs/shared/src/remote_connection.rs](libs/shared/src/remote_connection.rs)
- [libs/shared/src/task_manager.rs](libs/shared/src/task_manager.rs)
- [libs/shared/src/utils.rs](libs/shared/src/utils.rs)

</details>



This document covers the local tools implementation within the MCP (Model Context Protocol) system, focusing on file operations, shell command execution, and task management capabilities that run directly on the local system without requiring external API access.

For information about remote AI-powered tools, see [Remote Tools](#4.3). For the overall MCP server architecture and tool routing, see [Server Architecture](#4.1) and [Tool Container and Routing](#4.4).

## Architecture Overview

The local tools are implemented as methods on the `ToolContainer` struct and provide direct system access capabilities including file manipulation, shell command execution, and background task management. All local tools integrate with the secret management system for security.

```mermaid
graph TB
    subgraph "ToolContainer Structure"
        ToolContainer["ToolContainer"]
        SecretManager["SecretManager"]
        TaskManagerHandle["TaskManagerHandle"]
        ToolRouter["ToolRouter&lt;Self&gt;"]
        
        ToolContainer --> SecretManager
        ToolContainer --> TaskManagerHandle  
        ToolContainer --> ToolRouter
    end
    
    subgraph "Local Tool Categories"
        FileOps["File Operations"]
        ShellOps["Shell Operations"]
        TaskOps["Task Operations"]
        UtilOps["Utility Operations"]
    end
    
    subgraph "File Operations Tools"
        ViewTool["view()"]
        CreateTool["create()"]
        StrReplaceTool["str_replace()"]
        
        FileOps --> ViewTool
        FileOps --> CreateTool
        FileOps --> StrReplaceTool
    end
    
    subgraph "Shell Operations Tools"
        RunCommand["run_command()"]
        RunCommandAsync["run_command_async()"]
        
        ShellOps --> RunCommand
        ShellOps --> RunCommandAsync
    end
    
    subgraph "Task Operations Tools"
        GetAllTasks["get_all_tasks()"]
        GetTaskDetails["get_task_details()"]
        CancelAsyncTask["cancel_async_task()"]
        
        TaskOps --> GetAllTasks
        TaskOps --> GetTaskDetails
        TaskOps --> CancelAsyncTask
    end
    
    subgraph "Utility Operations Tools"
        GeneratePassword["generate_password()"]
        
        UtilOps --> GeneratePassword
    end
    
    ToolContainer --> FileOps
    ToolContainer --> ShellOps
    ToolContainer --> TaskOps
    ToolContainer --> UtilOps
    
    SecretManager --> ViewTool
    SecretManager --> CreateTool
    SecretManager --> StrReplaceTool
    SecretManager --> RunCommand
    SecretManager --> RunCommandAsync
    SecretManager --> GeneratePassword
    
    TaskManagerHandle --> RunCommandAsync
    TaskManagerHandle --> GetAllTasks
    TaskManagerHandle --> GetTaskDetails
    TaskManagerHandle --> CancelAsyncTask
```

Sources: [libs/mcp/server/src/local_tools.rs:1-942](), [libs/mcp/server/src/tool_container.rs:11-53]()

## File Operations Tools

The file operations provide comprehensive file system access with built-in secret redaction and line-number support for precise file manipulation.

### View Tool

The `view` tool reads file contents or lists directory contents with automatic secret redaction and line truncation for large files.

```mermaid
graph TB
    subgraph "view() Function Flow"
        ViewRequest["ViewRequest"]
        PathValidation["Path Validation"]
        FileOrDir{"File or Directory?"}
        
        ViewRequest --> PathValidation
        PathValidation --> FileOrDir
    end
    
    subgraph "Directory Handling"
        ReadDir["fs::read_dir()"]
        SortEntries["Sort Entries<br/>(dirs first)"]
        FormatTree["Format Tree Output"]
        
        FileOrDir -->|Directory| ReadDir
        ReadDir --> SortEntries
        SortEntries --> FormatTree
    end
    
    subgraph "File Handling"
        ReadFile["fs::read_to_string()"]
        ViewRangeCheck{"view_range provided?"}
        LineSlicing["Line Range Slicing"]
        TruncationCheck["Truncation Check<br/>(MAX_LINES = 300)"]
        
        FileOrDir -->|File| ReadFile
        ReadFile --> ViewRangeCheck
        ViewRangeCheck -->|Yes| LineSlicing
        ViewRangeCheck -->|No| TruncationCheck
        LineSlicing --> TruncationCheck
    end
    
    subgraph "Security Processing"
        SecretRedaction["SecretManager.redact_and_store_secrets()"]
        
        FormatTree --> SecretRedaction
        TruncationCheck --> SecretRedaction
    end
    
    SecretRedaction --> CallToolResult["CallToolResult"]
```

The `ViewRequest` struct supports optional line ranges with 1-indexed line numbers:

| Parameter | Type | Description |
|-----------|------|-------------|
| `path` | `String` | File or directory path |
| `view_range` | `Option<[i32; 2]>` | Optional `[start_line, end_line]` range |

Sources: [libs/mcp/server/src/local_tools.rs:48-56](), [libs/mcp/server/src/local_tools.rs:560-728]()

### Create Tool

The `create` tool creates new files with automatic parent directory creation and secret restoration in content.

```mermaid
graph TB
    subgraph "create() Function Flow"
        CreateRequest["CreateRequest"]
        PathExists{"Path exists?"}
        ParentDirCheck["Parent Directory Check"]
        CreateParentDirs["fs::create_dir_all()"]
        
        CreateRequest --> PathExists
        PathExists -->|No| ParentDirCheck
        PathExists -->|Yes| FileExistsError["FILE_EXISTS Error"]
        ParentDirCheck --> CreateParentDirs
    end
    
    subgraph "Content Processing"
        SecretRestore["SecretManager.restore_secrets_in_string()"]
        WriteFile["fs::write()"]
        CountLines["Count Lines in Result"]
        
        CreateParentDirs --> SecretRestore
        SecretRestore --> WriteFile
        WriteFile --> CountLines
    end
    
    CountLines --> SuccessResult["Success Result"]
```

Sources: [libs/mcp/server/src/local_tools.rs:76-84](), [libs/mcp/server/src/local_tools.rs:829-874]()

### String Replace Tool

The `str_replace` tool performs exact string replacements with support for multiple occurrence handling and secret restoration.

```mermaid
graph TB
    subgraph "str_replace() Function Flow"
        StrReplaceRequest["StrReplaceRequest"]
        PathValidation["Path Validation"]
        SecretRestore["Restore Secrets in<br/>old_str and new_str"]
        
        StrReplaceRequest --> PathValidation
        PathValidation --> SecretRestore
    end
    
    subgraph "Match Detection"
        ReadFile["fs::read_to_string()"]
        FindMatches["content.match_indices()"]
        MatchCount{"Match Count?"}
        
        SecretRestore --> ReadFile
        ReadFile --> FindMatches
        FindMatches --> MatchCount
    end
    
    subgraph "Replacement Logic"
        SingleMatch["Single Match<br/>Replace Once"]
        MultipleMatch["Multiple Matches<br/>Check replace_all"]
        ReplaceAll{"replace_all = true?"}
        ReplaceAllOccurrences["Replace All"]
        MultipleMatchError["MULTIPLE_MATCHES Error"]
        
        MatchCount -->|"1"| SingleMatch
        MatchCount -->|"> 1"| MultipleMatch
        MatchCount -->|"0"| NoMatchError["NO_MATCH Error"]
        MultipleMatch --> ReplaceAll
        ReplaceAll -->|Yes| ReplaceAllOccurrences
        ReplaceAll -->|No| MultipleMatchError
    end
    
    SingleMatch --> WriteResult["fs::write()"]
    ReplaceAllOccurrences --> WriteResult
```

Sources: [libs/mcp/server/src/local_tools.rs:58-74](), [libs/mcp/server/src/local_tools.rs:740-824]()

## Shell Command Tools

The shell command tools provide both synchronous and asynchronous execution capabilities with real-time output streaming and comprehensive error handling.

### Synchronous Command Execution

The `run_command` tool executes shell commands with real-time output streaming and automatic secret handling.

```mermaid
graph TB
    subgraph "run_command() Execution Flow"
        RunCommandRequest["RunCommandRequest"]
        SecretRestore["SecretManager.restore_secrets_in_string()"]
        SpawnProcess["Command::new('sh')<br/>.arg('-c')"]
        
        RunCommandRequest --> SecretRestore
        SecretRestore --> SpawnProcess
    end
    
    subgraph "Stream Processing"
        StdoutReader["BufReader&lt;stdout&gt;"]
        StderrReader["BufReader&lt;stderr&gt;"]
        ConcurrentRead["tokio::select! loop"]
        ProgressNotification["ctx.peer.notify_progress()"]
        
        SpawnProcess --> StdoutReader
        SpawnProcess --> StderrReader
        StdoutReader --> ConcurrentRead
        StderrReader --> ConcurrentRead
        ConcurrentRead --> ProgressNotification
    end
    
    subgraph "Timeout and Cancellation"
        TimeoutCheck{"timeout provided?"}
        TimeoutSelect["tokio::time::timeout()"]
        CancellationSelect["ctx.ct.cancelled()"]
        KillProcess["child.kill()"]
        
        ConcurrentRead --> TimeoutCheck
        TimeoutCheck -->|Yes| TimeoutSelect
        TimeoutCheck -->|No| CancellationSelect
        TimeoutSelect --> CancellationSelect
        CancellationSelect --> KillProcess
    end
    
    subgraph "Output Processing"
        HandleLargeOutput["handle_large_output()<br/>(MAX_LINES = 300)"]
        SecretRedaction["SecretManager.redact_and_store_secrets()"]
        
        ConcurrentRead --> HandleLargeOutput
        HandleLargeOutput --> SecretRedaction
    end
    
    SecretRedaction --> Result["CallToolResult"]
```

The `RunCommandRequest` supports command execution with optional timeout:

| Parameter | Type | Description |
|-----------|------|-------------|
| `command` | `String` | Shell command to execute |
| `description` | `Option<String>` | Optional command description |
| `timeout` | `Option<u64>` | Optional timeout in seconds |

Sources: [libs/mcp/server/src/local_tools.rs:20-28](), [libs/mcp/server/src/local_tools.rs:106-273]()

### Asynchronous Command Execution

The `run_command_async` tool starts background tasks through the `TaskManagerHandle` for long-running operations.

```mermaid
graph TB
    subgraph "run_command_async() Flow"
        RunCommandRequest["RunCommandRequest"]
        SecretRestore["SecretManager.restore_secrets_in_string()"]
        TaskManagerStart["TaskManagerHandle.start_task()"]
        
        RunCommandRequest --> SecretRestore
        SecretRestore --> TaskManagerStart
    end
    
    subgraph "Task Creation"
        TimeoutDuration["timeout_duration creation"]
        TaskInfo["TaskInfo Response"]
        SerializeTaskInfo["serde_json::to_string_pretty()"]
        
        TaskManagerStart --> TimeoutDuration
        TimeoutDuration --> TaskInfo
        TaskInfo --> SerializeTaskInfo
    end
    
    SerializeTaskInfo --> SuccessResult["Success Result with Task ID"]
```

Sources: [libs/mcp/server/src/local_tools.rs:297-336]()

## Task Management Tools

The task management tools provide comprehensive monitoring and control of background tasks started with `run_command_async`.

### Task Listing

The `get_all_tasks` tool provides a markdown-formatted table of all background tasks with redacted output.

```mermaid
graph TB
    subgraph "get_all_tasks() Processing"
        GetAllTasksRequest["GetAllTasksRequest"]
        TaskManagerGetAll["TaskManagerHandle.get_all_tasks()"]
        EmptyCheck{"tasks.is_empty()?"}
        
        GetAllTasksRequest --> TaskManagerGetAll
        TaskManagerGetAll --> EmptyCheck
        EmptyCheck -->|Yes| EmptyMessage["No background tasks found"]
    end
    
    subgraph "Task Redaction"
        TaskIteration["Iterate through tasks"]
        OutputRedaction["SecretManager.redact_and_store_secrets()"]
        CommandRedaction["Redact task.command"]
        
        EmptyCheck -->|No| TaskIteration
        TaskIteration --> OutputRedaction
        OutputRedaction --> CommandRedaction
    end
    
    subgraph "Markdown Table Generation"
        TableHeader["Markdown Table Header"]
        TableRows["Format Table Rows"]
        EscapeCharacters["Escape pipe characters"]
        TruncateFields["Truncate to 100 chars"]
        
        CommandRedaction --> TableHeader
        TableHeader --> TableRows
        TableRows --> EscapeCharacters
        EscapeCharacters --> TruncateFields
    end
    
    TruncateFields --> MarkdownResult["Markdown Table Result"]
```

The generated table includes these columns:

| Column | Content |
|--------|---------|
| Task ID | Full unique identifier |
| Status | Running, Completed, Failed, Cancelled, TimedOut |
| Command | Truncated and redacted command (100 chars) |
| Start Time | RFC3339 formatted timestamp |
| Duration | Elapsed or total time in seconds |
| Output | Truncated and redacted output (100 chars) |

Sources: [libs/mcp/server/src/local_tools.rs:42-46](), [libs/mcp/server/src/local_tools.rs:352-439]()

### Task Details

The `get_task_details` tool provides comprehensive information about a specific task with full output.

```mermaid
graph TB
    subgraph "get_task_details() Flow"
        GetTaskDetailsRequest["GetTaskDetailsRequest"]
        TaskManagerGetDetails["TaskManagerHandle.get_task_details()"]
        TaskExists{"task found?"}
        
        GetTaskDetailsRequest --> TaskManagerGetDetails
        TaskManagerGetDetails --> TaskExists
        TaskExists -->|No| TaskNotFound["TASK_NOT_FOUND Error"]
    end
    
    subgraph "Detail Processing"
        FormatDuration["Format duration string"]
        RedactCommand["Redact task.command"]
        RedactOutput["Redact task.output"]
        HandleLargeOutput["handle_large_output()"]
        
        TaskExists -->|Yes| FormatDuration
        FormatDuration --> RedactCommand
        RedactCommand --> RedactOutput
        RedactOutput --> HandleLargeOutput
    end
    
    subgraph "Markdown Formatting"
        MarkdownHeader["# Task Details header"]
        StatusSection["Status information"]
        CommandSection["Command code block"]
        OutputSection["Output code block"]
        
        HandleLargeOutput --> MarkdownHeader
        MarkdownHeader --> StatusSection
        StatusSection --> CommandSection
        CommandSection --> OutputSection
    end
    
    OutputSection --> DetailedResult["Detailed Task Result"]
```

Sources: [libs/mcp/server/src/local_tools.rs:36-40](), [libs/mcp/server/src/local_tools.rs:490-548]()

### Task Cancellation

The `cancel_async_task` tool terminates running background tasks.

Sources: [libs/mcp/server/src/local_tools.rs:30-34](), [libs/mcp/server/src/local_tools.rs:450-474]()

## Password Generation Tool

The `generate_password` tool creates secure passwords with configurable constraints and automatic secret redaction.

```mermaid
graph TB
    subgraph "generate_password() Flow"
        GeneratePasswordRequest["GeneratePasswordRequest"]
        DefaultLength["length.unwrap_or(15)"]
        DefaultNoSymbols["no_symbols.unwrap_or(false)"]
        
        GeneratePasswordRequest --> DefaultLength
        DefaultLength --> DefaultNoSymbols
    end
    
    subgraph "Password Generation"
        StakpakUtilsGenerate["stakpak_shared::utils::generate_password()"]
        RedactPassword["SecretManager.redact_and_store_password()"]
        
        DefaultNoSymbols --> StakpakUtilsGenerate
        StakpakUtilsGenerate --> RedactPassword
    end
    
    RedactPassword --> RedactedResult["Redacted Password Result"]
```

The `GeneratePasswordRequest` parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `length` | `Option<usize>` | 15 | Password length |
| `no_symbols` | `Option<bool>` | false | Exclude symbols |

Sources: [libs/mcp/server/src/local_tools.rs:86-92](), [libs/mcp/server/src/local_tools.rs:882-901]()

## Secret Management Integration

All local tools integrate with the `SecretManager` for consistent secret handling across operations.

```mermaid
graph TB
    subgraph "Secret Management Pattern"
        InputSecret["Input with Secrets"]
        RestoreSecrets["SecretManager.restore_secrets_in_string()"]
        ProcessOperation["Process Operation"]
        OutputWithSecrets["Output with Secrets"]
        RedactSecrets["SecretManager.redact_and_store_secrets()"]
        
        InputSecret --> RestoreSecrets
        RestoreSecrets --> ProcessOperation
        ProcessOperation --> OutputWithSecrets
        OutputWithSecrets --> RedactSecrets
    end
    
    subgraph "Secret Storage"
        LoadSessionMap["load_session_redaction_map()"]
        AddToSessionMap["add_to_session_redaction_map()"]
        SaveSessionMap["save_session_redaction_map()"]
        
        RestoreSecrets --> LoadSessionMap
        RedactSecrets --> AddToSessionMap
        AddToSessionMap --> SaveSessionMap
    end
```

The secret management provides:
- **Input restoration**: Secret placeholders like `[REDACTED_SECRET:rule-id:hash]` are restored to actual values
- **Output redaction**: Sensitive data in results is replaced with placeholders
- **Session persistence**: Redaction mappings are stored in `secrets.json` via `LocalStore`

Sources: [libs/shared/src/secret_manager.rs:70-110](), [libs/mcp/server/src/local_tools.rs:117-120](), [libs/mcp/server/src/local_tools.rs:266-268]()

## Output Management

Large output handling is centralized through the `handle_large_output` function to prevent memory issues and improve usability.

```mermaid
graph TB
    subgraph "handle_large_output() Logic"
        OutputInput["Input Output String"]
        LineCount["Count output lines"]
        MaxLinesCheck{"lines >= MAX_LINES (300)?"}
        
        OutputInput --> LineCount
        LineCount --> MaxLinesCheck
        MaxLinesCheck -->|No| ReturnOriginal["Return original output"]
    end
    
    subgraph "Large Output Processing"
        GenerateFilename["Generate random filename"]
        WriteSessionData["LocalStore::write_session_data()"]
        TruncateOutput["Take last MAX_LINES"]
        FormatTruncated["Format with file reference"]
        
        MaxLinesCheck -->|Yes| GenerateFilename
        GenerateFilename --> WriteSessionData
        WriteSessionData --> TruncateOutput
        TruncateOutput --> FormatTruncated
    end
    
    FormatTruncated --> TruncatedResult["Truncated Result with File Path"]
```

The output management:
- Truncates output exceeding 300 lines
- Saves full output to session files using `LocalStore`
- Provides file path reference in truncated output
- Uses random hex suffixes for unique filenames

Sources: [libs/mcp/server/src/local_tools.rs:904-941](), [libs/mcp/server/src/local_tools.rs:260-260](), [libs/mcp/server/src/local_tools.rs:512-517]()

---

# Page: Task Management System

# Task Management System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cli/src/utils/local_context.rs](cli/src/utils/local_context.rs)
- [libs/mcp/server/src/local_tools.rs](libs/mcp/server/src/local_tools.rs)
- [libs/shared/src/local_store.rs](libs/shared/src/local_store.rs)
- [libs/shared/src/remote_connection.rs](libs/shared/src/remote_connection.rs)
- [libs/shared/src/task_manager.rs](libs/shared/src/task_manager.rs)
- [libs/shared/src/utils.rs](libs/shared/src/utils.rs)

</details>



The Task Management System provides asynchronous background task execution for long-running commands on both local and remote systems. It enables the MCP server to spawn commands as background tasks, track their status, stream their output, and manage their lifecycle (cancellation, timeout, etc.). This system is critical for operations like port forwarding, log tailing, server processes, and other long-running commands that should not block the main execution flow.

For information about the MCP tools that use this system, see [Local Tools Implementation](#5.3). For details about remote SSH connections used in remote task execution, see [Remote Operations and SSH](#5.5).

## System Architecture

The Task Management System uses an actor-based pattern where a central `TaskManager` maintains state and processes messages from multiple `TaskManagerHandle` instances. Tasks execute in separate Tokio tasks and communicate back to the manager via channels.

### High-Level Architecture

```mermaid
graph TB
    subgraph "MCP Tool Layer"
        RCT["run_command_task"]
        GAT["get_all_tasks"]
        CT["cancel_task"]
        WFT["wait_for_tasks"]
        GTD["get_task_details"]
    end
    
    subgraph "Handle Layer"
        TMH1["TaskManagerHandle"]
        TMH2["TaskManagerHandle"]
        TMH3["TaskManagerHandle"]
    end
    
    subgraph "Task Manager Actor"
        TM["TaskManager"]
        RX["message receiver"]
        TASKS["HashMap<TaskId, TaskEntry>"]
    end
    
    subgraph "Execution Layer"
        TE1["Task Execution<br/>tokio::spawn"]
        TE2["Task Execution<br/>tokio::spawn"]
        TE3["Task Execution<br/>tokio::spawn"]
        
        LOCAL["Local Process<br/>tokio::process::Command"]
        REMOTE["Remote SSH<br/>RemoteConnection"]
    end
    
    RCT --> TMH1
    GAT --> TMH2
    CT --> TMH3
    WFT --> TMH1
    GTD --> TMH2
    
    TMH1 --> RX
    TMH2 --> RX
    TMH3 --> RX
    
    RX --> TM
    TM --> TASKS
    
    TM --> TE1
    TM --> TE2
    TM --> TE3
    
    TE1 --> LOCAL
    TE2 --> REMOTE
    TE3 --> LOCAL
    
    TE1 -.->|"TaskUpdate"| RX
    TE2 -.->|"PartialUpdate"| RX
    TE3 -.->|"TaskUpdate"| RX
```

**Sources:** [libs/shared/src/task_manager.rs:1-866](), [libs/mcp/server/src/local_tools.rs:247-337]()

### Core Data Flow

```mermaid
sequenceDiagram
    participant Tool as MCP Tool
    participant Handle as TaskManagerHandle
    participant Manager as TaskManager
    participant Task as Task Execution
    participant Process as Local/Remote Process
    
    Tool->>Handle: start_task(command, timeout, remote_info)
    Handle->>Manager: TaskMessage::Start
    Manager->>Manager: create TaskEntry
    Manager->>Task: tokio::spawn(execute_task)
    Task->>Process: spawn command
    Manager-->>Handle: task_id
    Handle-->>Tool: TaskInfo
    
    loop Output streaming
        Process->>Task: stdout/stderr data
        Task->>Manager: TaskMessage::PartialUpdate
        Manager->>Manager: append to task.output
    end
    
    Process->>Task: exit status
    Task->>Manager: TaskMessage::TaskUpdate(completion)
    Manager->>Manager: update task status & duration
    
    Tool->>Handle: get_task_details(task_id)
    Handle->>Manager: TaskMessage::GetTaskDetails
    Manager-->>Handle: TaskInfo
    Handle-->>Tool: TaskInfo
```

**Sources:** [libs/shared/src/task_manager.rs:750-792](), [libs/shared/src/task_manager.rs:200-280]()

## Core Components

### TaskManager

The `TaskManager` is the central actor that maintains all task state and processes messages. It runs in its own Tokio task and handles concurrent requests from multiple handles.

| Component | Type | Purpose |
|-----------|------|---------|
| `tasks` | `HashMap<TaskId, TaskEntry>` | Map of active and completed tasks |
| `tx` | `mpsc::UnboundedSender<TaskMessage>` | Channel sender for message passing |
| `rx` | `mpsc::UnboundedReceiver<TaskMessage>` | Channel receiver for message processing |
| `shutdown_tx/rx` | `broadcast::Sender/Receiver<()>` | Broadcast channel for shutdown signaling |

**Sources:** [libs/shared/src/task_manager.rs:142-149]()

### TaskManagerHandle

The `TaskManagerHandle` is a lightweight handle that can be cloned and shared across threads. It provides the public API for interacting with the task manager.

```rust
pub struct TaskManagerHandle {
    tx: mpsc::UnboundedSender<TaskMessage>,
}
```

Available operations:
- `start_task()` - Start a new background task
- `cancel_task()` - Cancel a running task
- `get_task_status()` - Get current status of a task
- `get_task_details()` - Get detailed task information
- `get_all_tasks()` - List all tasks
- `shutdown()` - Shutdown the task manager

**Sources:** [libs/shared/src/task_manager.rs:745-865]()

### Task Data Structures

#### Task

Internal task representation with complete metadata:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `TaskId (String)` | Unique task identifier |
| `status` | `TaskStatus` | Current task state |
| `command` | `String` | The command being executed |
| `remote_connection` | `Option<RemoteConnectionInfo>` | Remote SSH details if applicable |
| `output` | `Option<String>` | Accumulated command output |
| `error` | `Option<String>` | Error message if failed |
| `start_time` | `DateTime<Utc>` | When the task started |
| `duration` | `Option<Duration>` | How long the task took (or is taking) |
| `timeout` | `Option<Duration>` | Configured timeout |

**Sources:** [libs/shared/src/task_manager.rs:26-37]()

#### TaskEntry

Internal entry that includes the task and execution handle:

| Field | Type | Description |
|-------|------|-------------|
| `task` | `Task` | The task metadata |
| `handle` | `JoinHandle<()>` | Tokio task handle for aborting |
| `process_id` | `Option<u32>` | Local process ID for cleanup |
| `cancel_tx` | `Option<oneshot::Sender<()>>` | Cancellation signal sender |

**Sources:** [libs/shared/src/task_manager.rs:39-44]()

#### TaskInfo

Public-facing task information (serializable):

| Field | Type | Description |
|-------|------|-------------|
| `id` | `TaskId` | Task identifier |
| `status` | `TaskStatus` | Current status |
| `command` | `String` | Command being executed |
| `output` | `Option<String>` | Command output (redacted) |
| `start_time` | `DateTime<Utc>` | Start time |
| `duration` | `Option<Duration>` | Elapsed/total duration |

**Sources:** [libs/shared/src/task_manager.rs:46-54]()

## Task Lifecycle and State Machine

### Task States

```mermaid
stateDiagram-v2
    [*] --> Pending: Task created
    Pending --> Running: Execution starts
    Running --> Completed: Success (exit code 0)
    Running --> Failed: Error or non-zero exit
    Running --> Cancelled: Manual cancellation
    Running --> TimedOut: Timeout exceeded
    
    Completed --> [*]
    Failed --> [*]
    Cancelled --> [*]
    TimedOut --> [*]
    
    note right of Running
        Output streaming via
        PartialUpdate messages
    end note
    
    note right of Completed
        Final TaskUpdate with
        output and duration
    end note
```

**Sources:** [libs/shared/src/task_manager.rs:16-24]()

### State Transitions

| From | To | Trigger | Actions |
|------|----|---------|---------| 
| N/A | `Pending` | Task spawned but not started | Create `TaskEntry` |
| `Pending` | `Running` | Process spawned successfully | Send process ID, start streaming |
| `Running` | `Completed` | Process exits with code 0 | Record duration, store final output |
| `Running` | `Failed` | Process exits with non-zero code | Record error, duration |
| `Running` | `Cancelled` | `cancel_task()` called | Kill process, abort task |
| `Running` | `TimedOut` | Timeout duration exceeded | Kill process, set timeout error |

**Sources:** [libs/shared/src/task_manager.rs:241-280]()

## Message Passing Architecture

The system uses an actor pattern with message-based communication. All operations are sent as `TaskMessage` variants to the manager's message queue.

### TaskMessage Variants

```mermaid
graph TB
    subgraph "TaskMessage Enum"
        START["Start<br/>{command, timeout, remote_connection,<br/>response_tx}"]
        CANCEL["Cancel<br/>{id, response_tx}"]
        GET_STATUS["GetStatus<br/>{id, response_tx}"]
        GET_DETAILS["GetTaskDetails<br/>{id, response_tx}"]
        GET_ALL["GetAllTasks<br/>{response_tx}"]
        UPDATE["TaskUpdate<br/>{id, completion}"]
        PARTIAL["PartialUpdate<br/>{id, output}"]
        SHUTDOWN["Shutdown<br/>{response_tx}"]
    end
    
    subgraph "Response Channels"
        ONE["oneshot::Sender<Result>"]
    end
    
    START --> ONE
    CANCEL --> ONE
    GET_STATUS --> ONE
    GET_DETAILS --> ONE
    GET_ALL --> ONE
    SHUTDOWN --> ONE
```

**Sources:** [libs/shared/src/task_manager.rs:106-140]()

### Message Handler Flow

The `handle_message` function processes each message type:

| Message | Handler Logic | Updates State |
|---------|---------------|---------------|
| `Start` | Create task entry, spawn execution task | Inserts into `tasks` HashMap |
| `Cancel` | Send cancel signal, kill process, abort handle | Removes from `tasks` |
| `GetStatus` | Read current status from task | Read-only |
| `GetTaskDetails` | Convert `Task` to `TaskInfo` | Read-only |
| `GetAllTasks` | Collect all tasks, sort by start time | Read-only |
| `TaskUpdate` | Update status, output, error, duration | Updates existing entry |
| `PartialUpdate` | Append output chunk | Appends to `task.output` |
| `Shutdown` | Cancel all tasks, exit message loop | Drains `tasks` |

**Sources:** [libs/shared/src/task_manager.rs:200-280]()

## Task Execution

### Local Task Execution

Local tasks execute commands using `tokio::process::Command` with proper process group handling for cleanup.

```mermaid
graph TB
    START["execute_local_task"]
    SPAWN["Spawn shell command<br/>(sh -c on Unix, cmd on Windows)"]
    PID["Send process_id to manager"]
    STREAM["Stream stdout/stderr"]
    WAIT["Wait for exit status"]
    
    subgraph "Concurrent Operations"
        STDOUT["Read stdout lines"]
        STDERR["Read stderr lines"]
        EXIT["Wait for exit"]
        CANCEL["Wait for cancellation"]
        TIMEOUT["Wait for timeout"]
    end
    
    PARTIAL["Send PartialUpdate messages"]
    COMPLETE["Return TaskCompletion"]
    
    START --> SPAWN
    SPAWN --> PID
    PID --> STREAM
    STREAM --> STDOUT
    STREAM --> STDERR
    STREAM --> EXIT
    STREAM --> CANCEL
    STREAM --> TIMEOUT
    
    STDOUT --> PARTIAL
    STDERR --> PARTIAL
    EXIT --> COMPLETE
    CANCEL --> COMPLETE
    TIMEOUT --> COMPLETE
```

**Sources:** [libs/shared/src/task_manager.rs:449-607]()

Key features:
- **Process Groups:** Creates new process group on Unix (`process_group(0)`) and Windows (`CREATE_NEW_PROCESS_GROUP`) for proper cleanup
- **Non-interactive:** Sets `DEBIAN_FRONTEND=noninteractive` and `SUDO_ASKPASS=/bin/false`
- **Output Streaming:** Uses `tokio::io::AsyncBufReadExt` to stream lines as they arrive
- **Cancellation:** Monitors cancel channel via `tokio::select!`
- **Timeout:** Uses `tokio::time::timeout` if timeout specified
- **Process Cleanup:** Uses `kill -9` on Unix and `taskkill /F` on Windows

**Sources:** [libs/shared/src/task_manager.rs:449-607]()

### Remote Task Execution

Remote tasks execute commands over SSH using `RemoteConnection` with streaming support.

```mermaid
graph TB
    START["execute_remote_task"]
    CONN["Get connection from<br/>RemoteConnectionManager"]
    CALLBACK["Create progress callback<br/>for PartialUpdate messages"]
    OPTIONS["Configure CommandOptions<br/>{timeout, with_progress=false, simple=false}"]
    EXEC["connection.execute_command_unified()"]
    
    subgraph "Remote Execution"
        SSH["Open SSH channel"]
        CMD["Execute command with PID wrapper"]
        STREAM["Stream output via callback"]
        WAIT["Wait for completion"]
    end
    
    RESULT["Return TaskCompletion"]
    
    START --> CONN
    CONN --> CALLBACK
    CALLBACK --> OPTIONS
    OPTIONS --> EXEC
    EXEC --> SSH
    SSH --> CMD
    CMD --> STREAM
    STREAM --> WAIT
    WAIT --> RESULT
```

**Sources:** [libs/shared/src/task_manager.rs:609-683]()

Remote execution differences:
- **Connection Pooling:** Reuses connections via `RemoteConnectionManager`
- **No Local Process ID:** Remote tasks don't have local process IDs
- **PID Extraction:** Wraps command to capture remote PID for cancellation
- **Progress Callback:** Converts streaming output to `PartialUpdate` messages
- **Error Mapping:** Maps SSH errors to `TaskStatus` (TimedOut, Cancelled, Failed)

**Sources:** [libs/shared/src/task_manager.rs:609-683](), [libs/shared/src/remote_connection.rs:421-597]()

## Task Operations

### Starting Tasks

The `start_task` operation creates and spawns a new background task:

1. Generate unique task ID (6-character alphanumeric)
2. Create `Task` with `Running` status
3. Create cancellation channel
4. Spawn execution task (local or remote)
5. Store `TaskEntry` in manager
6. Wait briefly for task to start (300ms)
7. Return `TaskInfo` or error if task failed to start

**Sources:** [libs/shared/src/task_manager.rs:750-792]()

Special handling:
- **Instant Failure Detection:** If task fails within the 300ms startup window, returns `TaskFailedOnStart` error
- **Remote vs Local:** Automatically routes to appropriate execution path based on `remote_connection` parameter
- **Process ID Tracking:** For local tasks, waits for process ID before returning (skipped for remote tasks)

**Sources:** [libs/shared/src/task_manager.rs:282-343]()

### Cancelling Tasks

The `cancel_task` operation terminates a running task:

```mermaid
graph TB
    START["cancel_task(task_id)"]
    LOOKUP["Look up TaskEntry"]
    STATUS["Set status to Cancelled"]
    SIGNAL["Send cancellation signal"]
    CHECK["Check if process exists"]
    KILL["Kill process by PID"]
    ABORT["Abort task handle"]
    DONE["Task cancelled"]
    
    START --> LOOKUP
    LOOKUP --> STATUS
    STATUS --> SIGNAL
    SIGNAL --> CHECK
    CHECK -->|"Process exists"| KILL
    CHECK -->|"No process"| ABORT
    KILL --> ABORT
    ABORT --> DONE
```

**Sources:** [libs/shared/src/task_manager.rs:345-407]()

Platform-specific cleanup:
- **Unix:** Uses `kill -0` to check existence, then `kill -9` to terminate
- **Windows:** Uses `tasklist` to check existence, then `taskkill /F` to terminate
- **Safety:** Always checks if process exists before killing to avoid errors

**Sources:** [libs/shared/src/task_manager.rs:345-407]()

### Waiting for Tasks

The `wait_for_tasks` operation blocks until specified tasks reach final states. This is implemented in the MCP tool layer with streaming progress updates.

**Implementation in local_tools.rs:**

```mermaid
sequenceDiagram
    participant Tool as wait_for_tasks tool
    participant Manager as TaskManager
    participant Context as MCP Context
    
    Tool->>Tool: Parse task IDs
    loop Every 500ms
        Tool->>Manager: get_task_details(task_id)
        Manager-->>Tool: TaskInfo
        Tool->>Tool: Check if all tasks done
        alt Any task still running
            Tool->>Context: Send progress notification
            Tool->>Tool: sleep(500ms)
        else All tasks complete
            Tool->>Manager: get_all_tasks()
            Manager-->>Tool: Vec<TaskInfo>
            Tool-->>Tool: Format results table
        end
    end
```

**Sources:** [libs/mcp/server/src/local_tools.rs:482-518](), [libs/mcp/server/src/tool_container.rs:1-200]()

The helper function `wait_for_tasks_with_streaming` provides:
- **Polling Loop:** Checks task status every 500ms
- **Timeout Support:** Optional overall timeout for waiting
- **Progress Notifications:** Sends MCP progress updates during wait
- **Final Status:** Returns all task details once complete

**Sources:** [libs/mcp/server/src/tool_container.rs:90-167]()

### Listing All Tasks

The `get_all_tasks` operation returns information about all tasks, sorted by start time (newest first):

| Field Displayed | Source | Format |
|-----------------|--------|--------|
| Task ID | `task.id` | Full UUID string |
| Status | `task.status` | Debug format (`Running`, `Completed`, etc.) |
| Command | `task.command` | Truncated to 100 chars, pipe chars escaped |
| Start Time | `task.start_time` | RFC3339 format |
| Duration | `task.duration` | Seconds with 2 decimal places, or "N/A" |
| Output | `task.output` | Truncated to 100 chars, redacted, pipe chars escaped |

The output is formatted as a markdown table for easy reading.

**Sources:** [libs/mcp/server/src/local_tools.rs:353-424]()

## Integration with MCP Tools

The Task Management System is primarily accessed through five MCP tools:

### Tool: run_command_task

Starts a command as a background task and returns immediately.

**Parameters:**
- `command` - Shell command to execute
- `timeout` - Optional timeout in seconds
- `remote` - Optional remote connection string
- `password` - Optional SSH password
- `private_key_path` - Optional SSH key path

**Returns:** `TaskInfo` with task ID and initial status

**Sources:** [libs/mcp/server/src/local_tools.rs:247-337]()

### Tool: get_all_tasks

Lists all background tasks in a markdown table format.

**Parameters:**
- `view` - Required parameter (value ignored, for compatibility)

**Returns:** Markdown table with all tasks

**Sources:** [libs/mcp/server/src/local_tools.rs:353-424]()

### Tool: cancel_task

Cancels a running background task.

**Parameters:**
- `task_id` - Task identifier to cancel

**Returns:** Updated `TaskInfo` with `Cancelled` status

**Sources:** [libs/mcp/server/src/local_tools.rs:435-459]()

### Tool: wait_for_tasks

Waits for one or more tasks to complete, with streaming progress updates.

**Parameters:**
- `task_ids` - Space-separated list of task IDs
- `timeout` - Optional timeout in seconds

**Returns:** Markdown table with final task statuses

**Sources:** [libs/mcp/server/src/local_tools.rs:482-518]()

### Tool: get_task_details

Gets detailed information about a specific task.

**Parameters:**
- `task_id` - Task identifier

**Returns:** Formatted markdown with complete task details including full output

**Sources:** [libs/mcp/server/src/local_tools.rs:534-591]()

## Streaming and Progress Updates

### Partial Updates

During task execution, output is streamed via `PartialUpdate` messages:

1. Task execution reads stdout/stderr line by line
2. Each line is sent as a `TaskMessage::PartialUpdate`
3. Manager appends the line to `task.output`
4. This allows real-time monitoring of task progress

**Sources:** [libs/shared/src/task_manager.rs:261-273](), [libs/shared/src/task_manager.rs:513-535]()

### MCP Progress Notifications

For tools that wait on tasks, progress is communicated via MCP progress notifications:

```rust
ctx.peer.notify_progress(ProgressNotificationParam {
    progress_token: ProgressToken(NumberOrString::Number(0)),
    progress: 50.0,
    total: Some(100.0),
    message: Some(/* serialized progress info *),
}).await;
```

This allows AI agents and other MCP clients to display progress to users.

**Sources:** [libs/shared/src/remote_connection.rs:498-510]()

## Task Cleanup and Shutdown

### Graceful Shutdown

The `shutdown` operation cleanly terminates all tasks:

1. Drain the `tasks` HashMap
2. For each task:
   - Send cancellation signal
   - Check if process still exists
   - Kill process if running
   - Abort task handle
3. Exit message loop

**Sources:** [libs/shared/src/task_manager.rs:685-742]()

### Memory Management

Completed tasks are kept in memory for querying via `get_all_tasks` and `get_task_details`. The code includes a TODO comment about implementing cleanup for old completed tasks, but currently all tasks persist until shutdown.

**Sources:** [libs/shared/src/task_manager.rs:254-258]()

### Error Handling

Task errors are captured in the `TaskCompletion` structure and stored in the task's `error` field:

| Error Type | Status | Error Message |
|------------|--------|---------------|
| Spawn failure | `Failed` | "Failed to spawn command: ..." |
| Non-zero exit | `Failed` | Command output + "Command failed with exit code: X" |
| Timeout | `TimedOut` | "Task timed out" |
| Cancellation | `Cancelled` | "Tool call was cancelled and don't try to run it again" |
| Remote connection failure | `Failed` | "Failed to establish remote connection: ..." |

**Sources:** [libs/shared/src/task_manager.rs:82-104](), [libs/shared/src/task_manager.rs:477-603]()

---

# Page: Remote Operations and SSH

# Remote Tools

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cli/src/utils/local_context.rs](cli/src/utils/local_context.rs)
- [libs/mcp/server/src/local_tools.rs](libs/mcp/server/src/local_tools.rs)
- [libs/shared/src/local_store.rs](libs/shared/src/local_store.rs)
- [libs/shared/src/remote_connection.rs](libs/shared/src/remote_connection.rs)
- [libs/shared/src/task_manager.rs](libs/shared/src/task_manager.rs)
- [libs/shared/src/utils.rs](libs/shared/src/utils.rs)

</details>



Remote tools provide AI-powered capabilities that extend beyond local system operations by connecting to external services and APIs. These tools require authentication and network connectivity to function, offering advanced features like code generation, documentation search, and memory access. For local system operations, see [Local Tools](#4.2). For information about how tools are organized within the MCP system, see [Tool Container and Routing](#4.4).

## Architecture Overview

Remote tools are implemented as part of the MCP server system and communicate with the Stakpak backend API to provide AI-enhanced functionality. Unlike local tools that operate directly on the filesystem and system resources, remote tools proxy requests to external services while maintaining security through secret redaction and privacy controls.

### Remote Tools System Flow

```mermaid
graph TB
    subgraph "MCP Client"
        McpClient["MCP Client"]
    end
    
    subgraph "MCP Server"
        ToolContainer["ToolContainer"]
        RemoteTools["remote_tools.rs"]
        SecretManager["Secret Manager"]
    end
    
    subgraph "Stakpak Backend"
        StakpakAPI["Stakpak API"]
        LLMServices["LLM Services"]
        DocumentDB["Documentation DB"]
        MemoryStore["Memory Store"]
    end
    
    subgraph "Local Storage"
        LocalStore["LocalStore"]
        CodeIndex["code_index.json"]
        IndexStatus["indexing_status.json"]
    end
    
    McpClient --> ToolContainer
    ToolContainer --> RemoteTools
    RemoteTools --> SecretManager
    RemoteTools --> StakpakAPI
    RemoteTools --> LocalStore
    
    StakpakAPI --> LLMServices
    StakpakAPI --> DocumentDB
    StakpakAPI --> MemoryStore
    
    LocalStore --> CodeIndex
    LocalStore --> IndexStatus
```

Sources: [libs/mcp/server/src/remote_tools.rs:1-16]()

### Tool Authentication and Client Integration

Remote tools depend on the `ToolContainer` having an authenticated client to the Stakpak API. Each tool validates client availability before making requests and returns structured error responses when authentication is unavailable.

```mermaid
graph LR
    subgraph "Tool Execution Flow"
        ToolCall["Tool Call"] --> ClientCheck["get_client()"]
        ClientCheck --> HasClient{"Client Available?"}
        HasClient -->|Yes| APICall["call_mcp_tool()"]
        HasClient -->|No| ErrorResponse["McpError::internal_error"]
        APICall --> Response["CallToolResult"]
    end
```

Sources: [libs/mcp/server/src/remote_tools.rs:138-145](), [libs/mcp/server/src/remote_tools.rs:369-376]()

## Code Generation Tool

The `generate_code` tool provides AI-powered code generation and editing capabilities with optional file system integration. This tool is designed for DevOps configurations and infrastructure as code with intelligent file management.

### Code Generation Request Structure

| Field | Type | Description |
|-------|------|-------------|
| `prompt` | `String` | Detailed generation prompt with file path specifications |
| `save_files` | `Option<bool>` | Whether to save generated files to filesystem (default: false) |
| `context` | `Option<Vec<String>>` | File paths to include as context for generation |

```mermaid
graph TB
    subgraph "generate_code Tool Flow"
        Request["GenerateCodeRequest"] --> ContextLoad["Load Context Files"]
        ContextLoad --> SecretRedact1["Redact Secrets in Context"]
        SecretRedact1 --> APICall["call_mcp_tool('generate_code')"]
        APICall --> Response["GenerationResult"]
        Response --> SaveCheck{"save_files == true?"}
        SaveCheck -->|No| ReturnMarkdown["Return Markdown Response"]
        SaveCheck -->|Yes| ProcessEdits["Process File Edits"]
        ProcessEdits --> CreateDirs["Create Parent Directories"]
        CreateDirs --> ApplyEdits["Apply File Changes"]
        ApplyEdits --> SecretRedact2["Redact Secrets in Output"]
        SecretRedact2 --> ResultReport["Generate Final Report"]
    end
```

The tool supports two output modes controlled by the `save_files` parameter:
- **Preview mode** (`save_files: false`): Returns markdown-formatted code for review
- **Save mode** (`save_files: true`): Processes JSON-formatted edit instructions to create/modify files

Sources: [libs/mcp/server/src/remote_tools.rs:18-32](), [libs/mcp/server/src/remote_tools.rs:88-104](), [libs/mcp/server/src/remote_tools.rs:165-187]()

### File Edit Processing

When `save_files` is enabled, the tool processes `GenerationResult.edits` to perform file operations:

```mermaid
graph TB
    subgraph "File Edit Processing"
        EditLoop["Process Each Edit"] --> ParseURI["Parse document_uri"]
        ParseURI --> CreateParent["Create Parent Directories"]
        CreateParent --> FileExists{"File Exists?"}
        FileExists -->|No| CreateFile["Create New File"]
        FileExists -->|Yes| EditType{"old_str.is_empty()?"}
        EditType -->|Yes| AppendContent["Append Content"]
        EditType -->|No| ReplaceContent["Replace Content"]
        AppendContent --> SecretRedaction["Apply Secret Redaction"]
        ReplaceContent --> ValidateOldStr["Validate old_str Exists"]
        ValidateOldStr --> SecretRedaction
        CreateFile --> SecretRedaction
        SecretRedaction --> ReportSuccess["Add to Success Report"]
    end
```

Sources: [libs/mcp/server/src/remote_tools.rs:192-321](), [libs/mcp/server/src/remote_tools.rs:240-270](), [libs/mcp/server/src/remote_tools.rs:272-319]()

## Documentation Search Tool

The `search_docs` tool provides web search capabilities for technical documentation across cloud providers, development frameworks, and other technical resources.

### Search Strategy Implementation

| Parameter | Type | Purpose |
|-----------|------|---------|
| `keywords` | `Vec<String>` | Primary search terms |
| `exclude_keywords` | `Option<Vec<String>>` | Terms to filter out |
| `limit` | `Option<u32>` | Max results (capped at 5) |

The tool implements intelligent search strategy guidance:
- **Specific queries**: Use multiple related keywords in single call for targeted results
- **Broad exploration**: Break into multiple calls with fewer keywords each

Sources: [libs/mcp/server/src/remote_tools.rs:34-46](), [libs/mcp/server/src/remote_tools.rs:349-367](), [libs/mcp/server/src/remote_tools.rs:377-384]()

## Memory Search Tool

The `search_memory` tool enables searching through previous conversation history and code generation sessions to accelerate request fulfillment.

### Memory Search Parameters

```mermaid
graph LR
    subgraph "SearchMemoryRequest"
        Keywords["keywords: Vec<String>"]
        StartTime["start_time: Option<DateTime<Utc>>"]
        EndTime["end_time: Option<DateTime<Utc>>"]
    end
    
    Keywords --> APICall["call_mcp_tool('search_memory')"]
    StartTime --> APICall
    EndTime --> APICall
```

The tool searches against memory title, tags, and content with optional time-based filtering for precise historical context retrieval.

Sources: [libs/mcp/server/src/remote_tools.rs:48-62](), [libs/mcp/server/src/remote_tools.rs:399-429]()

## Rulebook Access Tool

The `read_rulebook` tool provides access to user-defined playbooks, guidelines, policies, and rules stored in the Stakpak system.

### Rulebook Request Structure

| Field | Type | Description |
|-------|------|-------------|
| `uri` | `String` | Valid URI pointing to rulebook document |

```mermaid
graph TB
    ReadRulebook["read_rulebook(uri)"] --> ValidateURI["Validate URI"]
    ValidateURI --> APICall["call_mcp_tool('read_rulebook')"]
    APICall --> Content["Return Rulebook Content"]
```

Sources: [libs/mcp/server/src/remote_tools.rs:64-70](), [libs/mcp/server/src/remote_tools.rs:444-465]()

## Local Code Search Tool

The `local_code_search` tool searches through locally indexed code blocks for Terraform, Kubernetes, Dockerfile, and GitHub Actions files. While implemented in the remote tools module, it operates on local indices.

### Code Search Architecture

```mermaid
graph TB
    subgraph "Local Code Search Flow"
        SearchRequest["LocalCodeSearchRequest"] --> StatusCheck["Check indexing_status.json"]
        StatusCheck --> IndexAvailable{"Index Available?"}
        IndexAvailable -->|No| ErrorMsg["Return Index Error Message"]
        IndexAvailable -->|Yes| LoadIndex["Load code_index.json"]
        LoadIndex --> SearchBlocks["Search Through Blocks"]
        SearchBlocks --> ScoreResults["Score and Rank Results"]
        ScoreResults --> ApplyLimit["Apply Result Limit"]
        ApplyLimit --> SecretRedaction["Redact Secrets in Code"]
        SecretRedaction --> FormatResults["Format Search Results"]
    end
```

### Scoring Algorithm

The search implements a weighted scoring system:

| Match Type | Score Weight | Description |
|------------|--------------|-------------|
| Name match | 10 points | Block name contains keyword |
| Type match | 8 points | Block type contains keyword |
| Kind match | 6 points | Block kind contains keyword |
| File path match | 4 points | Document URI contains keyword |
| Code content match | 2 points | Block code contains keyword |
| Multi-keyword bonus | 5 points | Per additional matched keyword |

Sources: [libs/mcp/server/src/remote_tools.rs:72-84](), [libs/mcp/server/src/remote_tools.rs:479-532](), [libs/mcp/server/src/remote_tools.rs:538-594]()

### Index Dependency Management

The tool validates indexing status and provides guidance when indices are unavailable:

```mermaid
graph TB
    CheckStatus["Read indexing_status.json"] --> StatusExists{"Status File Exists?"}
    StatusExists -->|No| ContinueSearch["Continue Normal Flow"]
    StatusExists -->|Yes| ParseStatus["Parse IndexingStatus"]
    ParseStatus --> IsIndexed{"status.indexed == true?"}
    IsIndexed -->|No| ReturnError["Return Index Error with --index-big-project guidance"]
    IsIndexed -->|Yes| ContinueSearch
    ContinueSearch --> LoadIndex["Load code_index.json"]
```

Sources: [libs/mcp/server/src/remote_tools.rs:490-508](), [libs/mcp/server/src/remote_tools.rs:510-522]()

## Security Integration

All remote tools integrate with the secret management system to ensure sensitive data is redacted from both input and output. The `SecretManager` is called at key points in tool execution to maintain security boundaries.

### Secret Redaction Points

```mermaid
graph LR
    subgraph "Security Integration Points"
        ContextFiles["Context File Content"] --> SecretMgr1["get_secret_manager().redact_and_store_secrets()"]
        GeneratedCode["Generated Code Output"] --> SecretMgr2["get_secret_manager().redact_and_store_secrets()"]
        SearchResults["Local Code Search Results"] --> SecretMgr3["get_secret_manager().redact_and_store_secrets()"]
    end
```

For detailed information about the secret management system, see [Security and Privacy](#6).

Sources: [libs/mcp/server/src/remote_tools.rs:115-117](), [libs/mcp/server/src/remote_tools.rs:236-238](), [libs/mcp/server/src/remote_tools.rs:636-638]()

## Error Handling

Remote tools implement consistent error handling patterns with structured error responses. Each tool validates prerequisites and returns descriptive error messages with context for troubleshooting.

### Common Error Patterns

| Error Type | Condition | Response |
|------------|-----------|----------|
| Client unavailable | No authenticated API client | `McpError::internal_error` with "Client not found" |
| API failure | Backend service error | `CallToolResult::error` with tool-specific error code |
| Local resource missing | Required files/indices unavailable | Guidance message with resolution steps |

Sources: [libs/mcp/server/src/remote_tools.rs:140-145](), [libs/mcp/server/src/remote_tools.rs:387-394](), [libs/mcp/server/src/remote_tools.rs:497-501]()

---

# Page: Security and Privacy

# Security and Privacy

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/stakpak-dark.png](assets/stakpak-dark.png)
- [assets/stakpak-light.png](assets/stakpak-light.png)
- [cli/src/utils/local_context.rs](cli/src/utils/local_context.rs)
- [libs/api/Cargo.toml](libs/api/Cargo.toml)
- [libs/api/src/lib.rs](libs/api/src/lib.rs)
- [libs/api/src/models.rs](libs/api/src/models.rs)
- [libs/mcp/server/README_SECRETS.md](libs/mcp/server/README_SECRETS.md)
- [libs/mcp/server/src/local_tools.rs](libs/mcp/server/src/local_tools.rs)
- [libs/shared/src/local_store.rs](libs/shared/src/local_store.rs)
- [libs/shared/src/remote_connection.rs](libs/shared/src/remote_connection.rs)
- [libs/shared/src/task_manager.rs](libs/shared/src/task_manager.rs)
- [libs/shared/src/utils.rs](libs/shared/src/utils.rs)

</details>



Stakpak implements multiple layers of security to protect sensitive data and prevent destructive operations when AI agents interact with systems. The security architecture includes four primary components: **Dynamic Secret Substitution**, **Warden Guardrails**, **Privacy Mode**, and **mTLS Encryption**.

These security features are designed to work transparently across all system interactions—from user input and tool execution to remote connections and external API calls—ensuring that sensitive information never reaches the LLM and that operations are safely constrained.

## Overview of Security Components

```mermaid
graph TB
    subgraph "Input Layer"
        UserInput["User Input<br/>(TUI/CLI)"]
        FileOps["File Operations"]
        RemoteOps["Remote Connections"]
    end
    
    subgraph "Security Processing"
        SecretSubstitution["Secret Substitution<br/>Gitleaks Detection<br/>Dynamic Redaction"]
        PrivacyMode["Privacy Mode<br/>IP/Account ID Redaction"]
        WardenGuardrails["Warden Guardrails<br/>Network-Level Policies<br/>Destructive Op Blocking"]
    end
    
    subgraph "Transport Security"
        MCPmTLS["MCP mTLS<br/>TLS 1.3 Encryption<br/>Client Certificates"]
        SSHEncryption["SSH/SFTP<br/>Encrypted Connections"]
    end
    
    subgraph "Execution Layer"
        LocalTools["Local Tools<br/>run_command<br/>view, create, str_replace"]
        RemoteTools["Remote Tools<br/>AI Code Generation<br/>API Calls"]
        MCPProxy["MCP Proxy<br/>Upstream Servers"]
    end
    
    subgraph "Output Layer"
        ToLLM["To LLM<br/>Redacted Content"]
        ToUser["To User<br/>Sanitized Display"]
        ToExternal["To External APIs<br/>Clean Data"]
    end
    
    UserInput --> SecretSubstitution
    FileOps --> SecretSubstitution
    RemoteOps --> SecretSubstitution
    
    SecretSubstitution --> PrivacyMode
    PrivacyMode --> WardenGuardrails
    
    WardenGuardrails --> LocalTools
    WardenGuardrails --> RemoteTools
    WardenGuardrails --> MCPProxy
    
    LocalTools --> MCPmTLS
    RemoteTools --> SSHEncryption
    MCPProxy --> MCPmTLS
    
    MCPmTLS --> ToLLM
    SSHEncryption --> ToUser
    MCPmTLS --> ToExternal
    
    style SecretSubstitution fill:#f9f9f9,stroke:#333,stroke-width:2px
    style PrivacyMode fill:#f9f9f9,stroke:#333,stroke-width:2px
    style WardenGuardrails fill:#f9f9f9,stroke:#333,stroke-width:2px
    style MCPmTLS fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Sources:** [README.md:42-61](), [libs/mcp/server/README_SECRETS.md:1-218]()

## Security Features Matrix

| Feature | Purpose | Implementation | Coverage |
|---------|---------|----------------|----------|
| **Secret Substitution** | Prevent LLM from seeing actual secret values | Gitleaks-based detection, placeholder generation, session storage | All text input/output, file operations, command execution |
| **Warden Guardrails** | Block destructive operations before execution | Network-level policies, container-based sandboxing | Tool execution, network access |
| **Privacy Mode** | Redact personally identifiable information | Extended detection rules for IPs, account IDs | Optional enhancement to secret detection |
| **mTLS Encryption** | Secure MCP communication channels | TLS 1.3 with client certificates | MCP server connections |

**Sources:** [README.md:55-61](), [README.md:241-289]()

## Dynamic Secret Substitution

The secret substitution system uses the Gitleaks detection engine to automatically identify and redact sensitive information before it reaches the LLM, while maintaining functionality through placeholder restoration during execution.

### How It Works

```mermaid
graph LR
    subgraph "Detection Phase"
        Input["Command Output<br/>'API_KEY=sk-ant-xyz123'"]
        GitleaksEngine["Gitleaks Engine<br/>556+ Detection Rules"]
        Detected["Detected Secret<br/>'sk-ant-xyz123'"]
    end
    
    subgraph "Redaction Phase"
        GeneratePlaceholder["Generate Placeholder<br/>[REDACTED_SECRET:api-key:abc123]"]
        StoreMapping["Store in secrets.json<br/>placeholder → actual_value"]
        ToLLM["To LLM<br/>'API_KEY=[REDACTED_SECRET:api-key:abc123]'"]
    end
    
    subgraph "Restoration Phase"
        LLMCommand["LLM Command<br/>'echo [REDACTED_SECRET:api-key:abc123]'"]
        LookupMapping["Lookup in secrets.json"]
        RestoreSecret["Restore Original<br/>'echo sk-ant-xyz123'"]
        Execute["Execute with Real Value"]
    end
    
    Input --> GitleaksEngine
    GitleaksEngine --> Detected
    Detected --> GeneratePlaceholder
    GeneratePlaceholder --> StoreMapping
    StoreMapping --> ToLLM
    
    LLMCommand --> LookupMapping
    LookupMapping --> RestoreSecret
    RestoreSecret --> Execute
    
    style GitleaksEngine fill:#f9f9f9,stroke:#333,stroke-width:2px
    style StoreMapping fill:#f9f9f9,stroke:#333,stroke-width:2px
    style RestoreSecret fill:#f9f9f9,stroke:#333,stroke-width:2px
```

The system operates in three phases: **Detection** using Gitleaks rules, **Redaction** with placeholder generation and storage, and **Restoration** when executing commands. This allows the LLM to reference secrets without seeing their actual values.

**Key Implementation Details:**

- **Detection Engine**: Uses `detect_secrets()` in [libs/shared/src/secrets/gitleaks.rs:358-430]() with 556+ pre-configured rules
- **Session Storage**: Mappings stored in `.stakpak/session/secrets.json` via `LocalStore::write_session_data()` [libs/shared/src/local_store.rs:17-47]()
- **Placeholder Format**: `[REDACTED_SECRET:{rule_id}:{random_id}]` generated by `generate_redaction_key()` [libs/shared/src/secrets/mod.rs:189-193]()
- **Restoration**: `restore_secrets_in_string()` swaps placeholders back to real values before execution [libs/shared/src/secrets/mod.rs:143-152]()

For detailed implementation, see [Secret Substitution System](#6.1).

**Sources:** [libs/mcp/server/README_SECRETS.md:9-48](), [libs/mcp/server/src/local_tools.rs:193-196](), [libs/shared/src/secrets/mod.rs:36-141]()

## Warden Guardrails

Warden provides network-level protection by blocking destructive operations before they execute. This container-based security layer acts as a policy enforcement point for tool execution.

### Architecture

```mermaid
graph TB
    subgraph "Agent Execution"
        AgentRequest["Agent Tool Request<br/>run_command, str_replace, etc."]
        WardenCheck{"Warden<br/>Enabled?"}
    end
    
    subgraph "Warden Container"
        PolicyEngine["Policy Engine<br/>Network Rules"]
        DestructiveOps["Destructive Operations<br/>File Deletion<br/>System Modification"]
        NetworkAccess["Network Access Control<br/>Allowed Domains<br/>Blocked IPs"]
    end
    
    subgraph "Execution Outcomes"
        Allow["Execute<br/>Operation Allowed"]
        Block["Block<br/>Return Error"]
        Sandbox["Sandboxed<br/>Limited Execution"]
    end
    
    AgentRequest --> WardenCheck
    WardenCheck -->|Yes| PolicyEngine
    WardenCheck -->|No| Allow
    
    PolicyEngine --> DestructiveOps
    PolicyEngine --> NetworkAccess
    
    DestructiveOps -->|Blocked| Block
    DestructiveOps -->|Allowed| Sandbox
    NetworkAccess -->|Blocked| Block
    NetworkAccess -->|Allowed| Allow
    
    style PolicyEngine fill:#f9f9f9,stroke:#333,stroke-width:2px
    style Block fill:#f9f9f9,stroke:#333,stroke-width:2px
```

Warden runs as a separate Docker container that enforces security policies at the network and file system level. When enabled, all tool execution flows through Warden's policy engine, which can:

- **Block destructive file operations** (deletion, overwrite of critical paths)
- **Control network access** (whitelist/blacklist domains)
- **Sandbox execution** (isolate operations in controlled environment)
- **Audit operations** (log all attempted actions)

Configuration is managed through the Warden container deployment, separate from the main stakpak agent.

For detailed configuration, see [Warden Guardrails](#6.2).

**Sources:** [README.md:43-45](), [README.md:261-265]()

## Privacy Mode

Privacy mode extends secret detection to include personally identifiable information (PII) such as IP addresses and cloud account identifiers.

### Enhanced Detection

When privacy mode is enabled via the `--privacy-mode` flag, the system loads additional detection rules:

```mermaid
graph TD
    subgraph "Standard Mode"
        StandardRules["GITLEAKS_CONFIG<br/>API Keys, Tokens<br/>Database Credentials<br/>Private Keys"]
    end
    
    subgraph "Privacy Mode"
        PrivacyRules["GITLEAKS_CONFIG_WITH_PRIVACY<br/>Standard Rules +<br/>Public IPv4/IPv6<br/>AWS Account IDs<br/>Cloud Resource IDs"]
    end
    
    subgraph "Detection Examples"
        IPDetection["IP: 203.0.113.5<br/>→ [REDACTED_SECRET:public-ipv4:xyz]"]
        AccountDetection["Account: 123456789012<br/>→ [REDACTED_SECRET:aws-account-id:abc]"]
    end
    
    StandardRules --> PrivacyRules
    PrivacyRules --> IPDetection
    PrivacyRules --> AccountDetection
    
    style PrivacyRules fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Privacy-Specific Rules:**

| Rule Type | Pattern | Allowlist |
|-----------|---------|-----------|
| `public-ipv4` | Public IPv4 addresses | Excludes private ranges (10.x, 192.168.x, 172.16-31.x), localhost (127.x), link-local (169.254.x) |
| `public-ipv6` | Public IPv6 addresses | Excludes private/local ranges |
| `aws-account-id` | 12-digit AWS account numbers | Context-aware detection in ARNs |

Privacy mode is configured per-execution:

```bash
# Enable privacy mode for MCP server
stakpak mcp start --privacy-mode

# Enable privacy mode for MCP proxy
stakpak mcp proxy --privacy-mode
```

For detailed privacy rules, see [Privacy Mode and Data Redaction](#6.3).

**Sources:** [libs/shared/src/secrets/privacy_rules.toml:1-57](), [README.md:270-271](), [README.md:287-288]()

## mTLS Transport Security

The MCP server uses mutual TLS (mTLS) to encrypt and authenticate all connections between clients and servers.

### mTLS Architecture

```mermaid
graph TB
    subgraph "MCP Client"
        ClientApp["Client Application<br/>Claude Desktop, Zed"]
        ClientCert["Client Certificate<br/>TLS 1.3"]
    end
    
    subgraph "TLS Handshake"
        ServerVerify["Server Verifies Client Cert"]
        ClientVerify["Client Verifies Server Cert"]
        EstablishSession["Establish Encrypted Session"]
    end
    
    subgraph "Stakpak MCP Server"
        ServerCert["Server Certificate<br/>Self-Signed or CA-Issued"]
        MCPServer["MCP Server<br/>Tool Endpoints"]
        ToolContainer["ToolContainer<br/>Secure Execution"]
    end
    
    ClientApp --> ClientCert
    ClientCert --> ServerVerify
    ServerCert --> ClientVerify
    ServerVerify --> EstablishSession
    ClientVerify --> EstablishSession
    EstablishSession --> MCPServer
    MCPServer --> ToolContainer
    
    style EstablishSession fill:#f9f9f9,stroke:#333,stroke-width:2px
    style MCPServer fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**mTLS Features:**

- **TLS 1.3 Protocol**: Modern encryption standards with forward secrecy
- **Client Authentication**: Both parties verify each other's certificates
- **Automatic Certificate Generation**: Self-signed certificates created on first run
- **Enabled by Default**: Can be disabled with `--disable-mcp-mtls` (not recommended for production)

```bash
# Start MCP server with mTLS (default)
stakpak mcp start

# Disable mTLS (NOT recommended)
stakpak mcp start --disable-mcp-mtls
```

The mTLS implementation uses `TlsClientConfig` from [libs/shared/src/tls_client.rs] and `create_tls_client()` for secure HTTPS requests [libs/mcp/server/src/local_tools.rs:831-840]().

**Sources:** [README.md:57](), [README.md:263-264](), [libs/mcp/server/src/local_tools.rs:831]()

## Integration with MCP Tools

Security features are integrated directly into the MCP tool execution pipeline, ensuring all operations are protected by default.

### Tool-Level Security Integration

```mermaid
graph TB
    subgraph "Tool Execution Flow"
        ToolCall["Tool Call from LLM<br/>run_command, view, create, etc."]
        InputProcessing["Input Processing<br/>restore_secrets_in_string()"]
        Execution["Tool Execution<br/>Local or Remote"]
        OutputProcessing["Output Processing<br/>redact_and_store_secrets()"]
        ReturnToLLM["Return to LLM<br/>Redacted Output"]
    end
    
    subgraph "SecretManager in ToolContainer"
        RestoreSecrets["restore_secrets_in_string()<br/>Swap placeholders → real values"]
        RedactSecrets["redact_and_store_secrets()<br/>Detect and redact secrets"]
        SessionStorage[".stakpak/session/secrets.json"]
    end
    
    subgraph "Specific Tool Examples"
        RunCommand["run_command<br/>Command: echo [REDACTED_SECRET:api-key:xyz]<br/>Execution: echo sk-ant-real-key<br/>Output: [REDACTED_SECRET:api-key:xyz]"]
        ViewFile["view<br/>Input: /path/to/config<br/>Output: API_KEY=[REDACTED_SECRET:...]"]
        StrReplace["str_replace<br/>old_str: [REDACTED_SECRET:...]<br/>Actual replacement uses real value"]
    end
    
    ToolCall --> InputProcessing
    InputProcessing --> RestoreSecrets
    RestoreSecrets --> Execution
    Execution --> RedactSecrets
    RedactSecrets --> OutputProcessing
    OutputProcessing --> ReturnToLLM
    
    RestoreSecrets --> SessionStorage
    RedactSecrets --> SessionStorage
    
    Execution --> RunCommand
    Execution --> ViewFile
    Execution --> StrReplace
    
    style RestoreSecrets fill:#f9f9f9,stroke:#333,stroke-width:2px
    style RedactSecrets fill:#f9f9f9,stroke:#333,stroke-width:2px
    style SessionStorage fill:#f9f9f9,stroke:#333,stroke-width:2px
```

### Tool Security Methods

Each tool in `ToolContainer` uses the `SecretManager` for automatic security processing:

| Tool | Input Security | Output Security | Implementation |
|------|---------------|-----------------|----------------|
| `run_command` | Restores placeholders before execution [libs/mcp/server/src/local_tools.rs:293-295]() | Redacts output before returning [libs/mcp/server/src/local_tools.rs:217-227]() | Command runs with real secrets, output sanitized |
| `view` | N/A (read-only) | Redacts file contents | File contents never contain real secrets in LLM view |
| `str_replace` | Restores both `old_str` and `new_str` | Redacts diff output | Replacement uses real values, result shown redacted |
| `create` | Restores `file_text` content | N/A (write-only) | File written with real secrets, tracking maintained |
| `generate_password` | N/A (generates new) | Immediately redacts generated password [libs/mcp/server/src/local_tools.rs:783-786]() | LLM never sees actual generated password |

The `ToolContainer` maintains a `SecretManager` instance that provides:

- `get_secret_manager()`: Access to session-scoped secret mapping
- `redact_and_store_secrets()`: Detection and placeholder generation  
- `restore_secrets_in_string()`: Placeholder-to-value restoration

**Sources:** [libs/mcp/server/src/local_tools.rs:199-245](), [libs/mcp/server/src/local_tools.rs:617-648](), [libs/mcp/server/src/local_tools.rs:670-705](), [libs/mcp/server/README_SECRETS.md:94-104]()

## Configuration and Customization

### Rule Management

The system supports three levels of rule configuration:

1. **Base Rules** (`gitleaks.toml`): Standard gitleaks rule set with 556+ detection patterns
2. **Additional Rules** (`additional_rules.toml`): Custom extensions for specific services
3. **Privacy Rules** (`privacy_rules.toml`): PII detection patterns

Custom rules can be added by extending the `additional_rules.toml` configuration:

```toml
[[rules]]
id = "anthropic-api-key"
description = "Found an Anthropic API Key, posing a risk of unauthorized access to AI services and data manipulation."
regex = '''\bsk-ant-api03-[A-Za-z0-9_-]{20,100}[A-Za-z0-9_-]'''
entropy = 3.5
keywords = ["sk-ant-api", "anthropic"]
```

### Performance Optimization

The system includes several performance optimizations:

- **Lazy Loading**: Configurations loaded on first use via `Lazy<GitleaksConfig>` [libs/shared/src/secrets/gitleaks.rs:226-230]()
- **Keyword Pre-filtering**: Rules only process text containing relevant keywords [libs/shared/src/secrets/gitleaks.rs:587-592]()
- **Regex Compilation**: Pre-compiled patterns stored in configuration structures [libs/shared/src/secrets/gitleaks.rs:140-194]()
- **Entropy Calculation**: Shannon entropy validation for randomness checking [libs/shared/src/secrets/gitleaks.rs:324-347]()

**Sources:** [libs/shared/src/secrets/gitleaks.rs:226-278](), [libs/shared/src/secrets/additional_rules.toml:1-7](), [libs/shared/src/secrets/gitleaks.rs:587-610]()

---

# Page: Secret Substitution System

# Secret Substitution System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cli/src/utils/local_context.rs](cli/src/utils/local_context.rs)
- [libs/api/Cargo.toml](libs/api/Cargo.toml)
- [libs/api/src/lib.rs](libs/api/src/lib.rs)
- [libs/api/src/models.rs](libs/api/src/models.rs)
- [libs/mcp/server/README_SECRETS.md](libs/mcp/server/README_SECRETS.md)
- [libs/mcp/server/src/local_tools.rs](libs/mcp/server/src/local_tools.rs)
- [libs/shared/src/local_store.rs](libs/shared/src/local_store.rs)
- [libs/shared/src/remote_connection.rs](libs/shared/src/remote_connection.rs)
- [libs/shared/src/task_manager.rs](libs/shared/src/task_manager.rs)
- [libs/shared/src/utils.rs](libs/shared/src/utils.rs)

</details>



## Purpose and Scope

The Secret Substitution System provides dynamic detection, redaction, and restoration of sensitive values (API keys, passwords, tokens) within tool execution workflows. This system enables the Language Model to work with redacted placeholders while the actual secret values are safely stored and automatically restored before execution. The system operates transparently at the MCP tool layer, protecting secrets in command outputs, file contents, and tool inputs.

For information about the broader MCP tool architecture, see [Tool Container and Execution Flow](#5.2). For general security features including Warden guardrails, see [Security and Privacy](#6).

---

## System Architecture

```mermaid
graph TB
    subgraph "MCP Tool Layer"
        TC[ToolContainer]
        SM[SecretManager]
        
        subgraph "Tools with Secret Handling"
            RUN[run_command]
            VIEW[view]
            REPLACE[str_replace]
            CREATE[create]
            TASK[run_command_task]
            GEN_PWD[generate_password]
        end
    end
    
    subgraph "Secret Detection"
        GL[Gitleaks Engine]
        RULES[Detection Rules<br/>API keys, passwords,<br/>tokens, certificates]
    end
    
    subgraph "Session Storage"
        SFILE[".stakpak/session/secrets.json"]
        MAP["Placeholder → Secret Mapping"]
    end
    
    subgraph "Processing Flow"
        OUTPUT["Tool Output<br/>(may contain secrets)"]
        REDACTED["Redacted Output<br/>[REDACTED_SECRET:rule:hash]"]
        INPUT["Tool Input<br/>(may contain placeholders)"]
        RESTORED["Restored Input<br/>(actual secrets)"]
    end
    
    TC --> SM
    SM --> GL
    GL --> RULES
    SM --> SFILE
    SFILE --> MAP
    
    RUN --> OUTPUT
    OUTPUT --> SM
    SM --> REDACTED
    REDACTED --> LLM[Language Model]
    
    LLM --> INPUT
    INPUT --> SM
    SM --> RESTORED
    RESTORED --> RUN
    
    VIEW --> SM
    REPLACE --> SM
    CREATE --> SM
    TASK --> SM
    GEN_PWD --> SM
    
    style SM fill:#f9f9f9
    style SFILE fill:#f9f9f9
```

**Architecture Overview: Secret Substitution System Data Flow**

The `SecretManager` component sits between tool execution and LLM interaction, intercepting outputs for redaction and inputs for restoration. Gitleaks rules detect secrets, placeholders are generated, and mappings are persisted in the session file.

Sources: [libs/mcp/server/src/local_tools.rs:1-949](), [libs/mcp/server/README_SECRETS.md:1-218]()

---

## Secret Detection and Redaction Pipeline

```mermaid
sequenceDiagram
    participant Tool as "MCP Tool<br/>(run_command, view, etc)"
    participant SM as "SecretManager"
    participant GL as "Gitleaks"
    participant Store as "secrets.json"
    participant LLM as "Language Model"
    
    Tool->>SM: redact_and_store_secrets(content, path)
    SM->>GL: scan_content_for_secrets(content)
    GL-->>SM: List of detected secrets with rules
    
    loop For each secret
        SM->>SM: generate_placeholder(secret, rule_id)
        Note over SM: Format: [REDACTED_SECRET:rule-id:hash]
        SM->>Store: add_to_session_redaction_map(placeholder, secret)
    end
    
    Store-->>SM: Mapping saved
    SM->>SM: replace_secrets_with_placeholders(content)
    SM-->>Tool: redacted_content
    Tool-->>LLM: Return redacted content
    
    Note over LLM: LLM sees only placeholders,<br/>not actual secret values
```

**Secret Detection and Redaction Sequence**

When tool output contains secrets, the `SecretManager` invokes Gitleaks scanning, generates unique placeholders, stores mappings in the session file, and returns redacted content to the LLM.

Sources: [libs/mcp/server/README_SECRETS.md:10-48]()

---

## Placeholder Format and Generation

### Placeholder Structure

Placeholders follow the format: `[REDACTED_SECRET:rule-id:short-hash]`

| Component | Description | Example |
|-----------|-------------|---------|
| `REDACTED_SECRET` | Fixed prefix for identification | `REDACTED_SECRET` |
| `rule-id` | Gitleaks rule that detected the secret | `api-key`, `generic-password`, `aws-access-token` |
| `short-hash` | Truncated hash for uniqueness | `abc123`, `bga278` |

### Example Transformations

```
Original:  export API_KEY=sk-1234567890abcdef1234567890abcdef
Redacted:  export API_KEY=[REDACTED_SECRET:api-key:abc123]

Original:  password: mySecretP@ssw0rd
Redacted:  password: [REDACTED_SECRET:generic-password:def456]

Original:  AKIAIOSFODNN7EXAMPLE
Redacted:  [REDACTED_SECRET:aws-access-token:xyz789]
```

Sources: [libs/mcp/server/README_SECRETS.md:16-28]()

---

## Secret Restoration Flow

```mermaid
sequenceDiagram
    participant LLM as "Language Model"
    participant Tool as "MCP Tool<br/>(run_command, create, etc)"
    participant SM as "SecretManager"
    participant Store as "secrets.json"
    participant Exec as "Command Execution"
    
    LLM->>Tool: Input with placeholders<br/>"echo [REDACTED_SECRET:api-key:abc123]"
    Tool->>SM: restore_secrets_in_string(input)
    SM->>Store: load_session_redaction_map()
    Store-->>SM: Placeholder → Secret mappings
    
    loop For each placeholder in input
        SM->>SM: lookup_secret(placeholder)
        SM->>SM: replace_placeholder_with_secret()
    end
    
    SM-->>Tool: restored_input<br/>"echo sk-1234567890abcdef..."
    Tool->>Exec: execute_command(restored_input)
    Exec-->>Tool: execution_result
    Tool->>SM: redact_and_store_secrets(execution_result)
    SM-->>Tool: redacted_result
    Tool-->>LLM: Return redacted result
```

**Secret Restoration Process**

Before command execution or file operations, the `SecretManager` loads the session mapping, identifies placeholders in the input, and replaces them with actual secret values. The LLM remains unaware of the restoration.

Sources: [libs/mcp/server/README_SECRETS.md:30-48](), [libs/mcp/server/src/local_tools.rs:193-196]()

---

## Session Storage Implementation

### File Location and Structure

The session file is stored at `.stakpak/session/secrets.json` within the current working directory.

**File Structure:**

```json
{
  "[REDACTED_SECRET:api-key:bga278]": "api_125136713",
  "[REDACTED_SECRET:token:def456]": "ghp_1234567890abcdef1234567890abcdef12345678",
  "[REDACTED_SECRET:aws-key:xyz789]": "AKIAIOSFODNN7EXAMPLE"
}
```

### Session File Operations

```mermaid
graph LR
    subgraph "SecretManager Operations"
        LOAD[load_session_redaction_map]
        SAVE[save_session_redaction_map]
        ADD[add_to_session_redaction_map]
    end
    
    subgraph "LocalStore"
        GET_PATH[get_local_session_store_path]
        WRITE[write_session_data]
        READ[read_session_data]
    end
    
    subgraph "File System"
        SDIR[".stakpak/session/"]
        SFILE["secrets.json"]
    end
    
    LOAD --> READ
    SAVE --> WRITE
    ADD --> LOAD
    ADD --> SAVE
    
    READ --> SDIR
    WRITE --> SDIR
    GET_PATH --> SDIR
    SDIR --> SFILE
    
    style SDIR fill:#f9f9f9
    style SFILE fill:#f9f9f9
```

**Session File Operations Flow**

The `SecretManager` uses `LocalStore` utilities to manage the session file. The file is created on first secret detection and updated incrementally as new secrets are discovered.

Sources: [libs/shared/src/local_store.rs:1-55](), [libs/mcp/server/README_SECRETS.md:51-69]()

### LocalStore Integration

The session storage uses `LocalStore::get_local_session_store_path()` which resolves to:

```
<current_working_directory>/.stakpak/session/
```

Key operations:
- **`LocalStore::write_session_data(path, data)`** - Writes session data with automatic directory creation [libs/shared/src/local_store.rs:17-47]()
- **`LocalStore::read_session_data(path)`** - Reads session data with error handling [libs/shared/src/local_store.rs:49-54]()

Sources: [libs/shared/src/local_store.rs:1-55]()

---

## Integration with MCP Tools

### Tool-Specific Integration Points

```mermaid
graph TB
    subgraph "Command Execution Tools"
        RC[run_command<br/>lines 199-245]
        RCT[run_command_task<br/>lines 280-337]
    end
    
    subgraph "File Operation Tools"
        VIEW[view<br/>lines 618-648]
        REPLACE[str_replace<br/>lines 670-706]
        CREATE[create<br/>lines 726-752]
    end
    
    subgraph "Utility Tools"
        GENPWD[generate_password<br/>lines 772-790]
    end
    
    subgraph "Secret Manager Methods"
        REDACT["redact_and_store_secrets<br/>(output processing)"]
        RESTORE["restore_secrets_in_string<br/>(input processing)"]
    end
    
    RC -->|"Before execution"| RESTORE
    RC -->|"After execution"| REDACT
    
    RCT -->|"line 293-295"| RESTORE
    
    VIEW -->|"File contents"| REDACT
    REPLACE -->|"old_str, new_str"| RESTORE
    CREATE -->|"file_text"| RESTORE
    
    GENPWD -->|"Password generation"| REDACT
    
    style REDACT fill:#f9f9f9
    style RESTORE fill:#f9f9f9
```

**MCP Tool Integration Points**

Each MCP tool integrates with the `SecretManager` at specific points to ensure secrets are redacted in outputs and restored in inputs.

Sources: [libs/mcp/server/src/local_tools.rs:1-949](), [libs/mcp/server/README_SECRETS.md:92-105]()

### run_command Integration

The `run_command` tool integrates secret handling at execution boundaries:

**Tool Documentation (lines 193-196):**
```
SECRET HANDLING:
- Output containing secrets will be redacted and shown as placeholders like [REDACTED_SECRET:rule-id:hash]
- You can use these placeholders in subsequent commands - they will be automatically restored to actual values before execution
- Example: If you see 'export API_KEY=[REDACTED_SECRET:api-key:abc123]', you can use '[REDACTED_SECRET:api-key:abc123]' in later commands
```

**Implementation:**
- Output redaction occurs via `handle_large_output()` which internally processes secrets [libs/mcp/server/src/local_tools.rs:218-227]()
- The unified command execution helper handles both local and remote execution with secret awareness

Sources: [libs/mcp/server/src/local_tools.rs:180-245]()

### run_command_task Integration

Background tasks also support secret handling:

**Documentation (lines 273-277):**
```
SECRET HANDLING:
- Commands containing secrets will have them restored before execution
- Task output will be redacted when retrieved
- Use secret placeholders like [REDACTED_SECRET:rule-id:hash] in commands
```

**Implementation:**
```rust
// Restore secrets in the command before execution
let actual_command = self
    .get_secret_manager()
    .restore_secrets_in_string(&command);
```

Sources: [libs/mcp/server/src/local_tools.rs:280-337]()

### File Operation Tools

**view Tool (lines 611-616):**
```
SECRET HANDLING:
- File contents containing secrets will be redacted and shown as placeholders like [REDACTED_SECRET:rule-id:hash]
- These placeholders represent actual secret values that are safely stored for later use
- You can reference these placeholders when working with the file content
```

**str_replace Tool (lines 663-667):**
```
SECRET HANDLING:
- You can use secret placeholders like [REDACTED_SECRET:rule-id:hash] in both old_str and new_str parameters
- These placeholders will be automatically restored to actual secret values before performing the replacement
- This allows you to safely work with secret values without exposing them
```

**create Tool (lines 722-724):**
```
SECRET HANDLING:
- File content containing secrets will have them restored before writing to ensure functionality
- Use secret placeholders like [REDACTED_SECRET:rule-id:hash] in file_text parameter
```

Sources: [libs/mcp/server/src/local_tools.rs:618-752]()

### generate_password Tool

The password generation tool demonstrates automatic secret redaction:

**Implementation (lines 783-789):**
```rust
let password = stakpak_shared::utils::generate_password(length, no_symbols);

let redacted_password = self
    .get_secret_manager()
    .redact_and_store_password(&password, &password);

Ok(CallToolResult::success(vec![Content::text(
    &redacted_password,
)]))
```

Newly generated passwords are immediately redacted so the LLM never sees the actual password value.

Sources: [libs/mcp/server/src/local_tools.rs:772-790]()

---

## Implementation Details

### SecretManager Component Structure

```mermaid
classDiagram
    class SecretManager {
        -session_path: PathBuf
        -gitleaks_rules: Vec~Rule~
        +redact_and_store_secrets(content, path) String
        +restore_secrets_in_string(input) String
        +redact_and_store_password(password, context) String
        -load_session_redaction_map() HashMap
        -save_session_redaction_map(map)
        -add_to_session_redaction_map(placeholder, secret)
        -scan_content_for_secrets(content) Vec~DetectedSecret~
        -generate_placeholder(secret, rule_id) String
    }
    
    class LocalStore {
        +get_local_session_store_path() PathBuf
        +write_session_data(path, data) Result
        +read_session_data(path) Result
    }
    
    class ToolContainer {
        -secret_manager: SecretManager
        +get_secret_manager() SecretManager
    }
    
    ToolContainer --> SecretManager
    SecretManager --> LocalStore
```

**SecretManager Class Structure**

The `SecretManager` encapsulates all secret detection, redaction, and restoration logic. It maintains a reference to the session file and Gitleaks rules.

Sources: [libs/mcp/server/README_SECRETS.md:72-93]()

### Gitleaks Integration

The system uses the Gitleaks engine with comprehensive rule sets to detect various secret types:

**Detected Secret Types:**
- API keys and authentication tokens
- Database credentials (passwords, connection strings)
- Cloud provider keys (AWS, GCP, Azure)
- OAuth tokens and client secrets
- Private keys and certificates (RSA, ECDSA, SSH)
- Generic passwords and high-entropy strings

**Detection Process:**
1. Content is passed to Gitleaks scanning engine
2. Each rule is evaluated against the content
3. Matches are collected with rule metadata (rule ID, description)
4. Secret positions and values are extracted
5. Results returned for placeholder generation

Sources: [libs/mcp/server/README_SECRETS.md:108-117]()

### Placeholder Generation Algorithm

```mermaid
flowchart TD
    START[Detected Secret] --> HASH[Generate SHA256 hash of secret]
    HASH --> TRUNC[Truncate to 6 characters]
    TRUNC --> RULE[Extract rule_id from detection]
    RULE --> FORMAT["Format: [REDACTED_SECRET:rule_id:hash]"]
    FORMAT --> CHECK{Placeholder exists in session?}
    CHECK -->|Yes| REUSE[Reuse existing placeholder]
    CHECK -->|No| STORE[Store new mapping]
    STORE --> RETURN[Return placeholder]
    REUSE --> RETURN
```

**Placeholder Generation Flow**

The system generates consistent placeholders for identical secrets, ensuring the same secret always maps to the same placeholder within a session.

Sources: [libs/mcp/server/README_SECRETS.md:118-124]()

### Output Processing with Secret Redaction

The `handle_large_output()` utility integrates with secret redaction:

**Function Signature:**
```rust
pub fn handle_large_output(
    output: &str,
    file_prefix: &str,
    max_lines: usize,
    show_head: bool,
) -> Result<String, String>
```

This function:
1. Checks if output exceeds `max_lines` (typically 300)
2. Saves full output to session storage if needed
3. Returns truncated output with file reference
4. Secret redaction occurs during the save operation

Sources: [libs/shared/src/utils.rs:386-430](), [libs/mcp/server/src/local_tools.rs:218-227]()

---

## Task Manager Integration

Background tasks spawned by `run_command_task` also participate in secret handling:

```mermaid
sequenceDiagram
    participant LLM
    participant Tool as "run_command_task"
    participant SM as "SecretManager"
    participant TM as "TaskManager"
    participant Store as "secrets.json"
    
    LLM->>Tool: Command with placeholder
    Tool->>SM: restore_secrets_in_string(command)
    SM->>Store: Load mappings
    Store-->>SM: Secret mappings
    SM-->>Tool: Restored command
    Tool->>TM: start_task(restored_command)
    TM->>TM: Execute in background
    
    Note over TM: Task produces output
    
    LLM->>Tool: get_task_details(task_id)
    Tool->>TM: Get task output
    TM-->>Tool: Raw output
    Tool->>SM: redact_and_store_secrets(output)
    SM-->>Tool: Redacted output
    Tool-->>LLM: Return redacted task details
```

**Task Manager Secret Handling**

Background tasks have secrets restored before execution (line 293-295) and outputs are redacted when retrieved via `get_task_details` (lines 552-560).

Sources: [libs/mcp/server/src/local_tools.rs:280-337](), [libs/mcp/server/src/local_tools.rs:534-591](), [libs/shared/src/task_manager.rs:1-770]()

---

## Security Features and Considerations

### Session Scope and Isolation

| Feature | Implementation |
|---------|----------------|
| **Session Isolation** | Each session maintains its own `secrets.json` file |
| **Working Directory Scope** | Session files stored in `.stakpak/session/` relative to CWD |
| **No Cross-Session Leakage** | Mappings never shared between sessions |
| **Automatic Initialization** | Session file created on first secret detection |

### File System Security

The session file should have restricted permissions:
- Location: `.stakpak/session/secrets.json`
- Recommended permissions: `0600` (owner read/write only)
- Directory structure automatically created with appropriate permissions

Sources: [libs/shared/src/local_store.rs:6-47]()

### Detection Coverage

Gitleaks rules cover comprehensive secret patterns including:
- **Generic Patterns**: High-entropy strings, passwords, API keys
- **Service-Specific**: GitHub tokens, AWS keys, Slack tokens, Docker credentials
- **Database**: PostgreSQL, MySQL, MongoDB connection strings
- **Certificates**: Private keys (RSA, DSA, EC, OpenSSH)
- **Cloud Providers**: AWS, GCP, Azure, DigitalOcean credentials

Sources: [libs/mcp/server/README_SECRETS.md:108-117]()

### Limitations

| Limitation | Description |
|------------|-------------|
| **Session Persistence** | Mappings only persist within a single execution session |
| **Rule-Based Detection** | May miss custom or proprietary secret formats not in Gitleaks rules |
| **Local Storage Only** | Session files not synchronized across distributed systems |
| **Performance Overhead** | Secret scanning adds processing time to tool operations |
| **Pattern Dependence** | Detection effectiveness depends on Gitleaks rule quality |

Sources: [libs/mcp/server/README_SECRETS.md:191-197]()

---

## Remote Execution Integration

The secret handling system extends to remote command execution via SSH:

**RemoteConnection Command Execution:**
- Commands are restored before SSH transmission [libs/shared/src/task_manager.rs:609-683]()
- Remote command output is captured and redacted before return
- TaskManager supports both local and remote async tasks with unified secret handling

**Implementation in execute_remote_task:**
The `TaskManager::execute_remote_task()` method creates SSH connections through `RemoteConnectionManager` and applies the same secret restoration as local execution, ensuring consistent behavior across execution contexts.

Sources: [libs/shared/src/task_manager.rs:609-683](), [libs/shared/src/remote_connection.rs:421-597]()

---

## Configuration and Control

The secret redaction feature is controlled at the `ToolContainer` initialization level. When creating tools, secret handling can be enabled or disabled:

```rust
// With secret redaction enabled
let tools = ToolContainer::new(config, true);

// With secret redaction disabled
let tools = ToolContainer::new(config, false);
```

When disabled, all content passes through without modification, and no session mappings are created.

Sources: [libs/mcp/server/README_SECRETS.md:182-189]()

---

# Page: Warden Guardrails

# Warden Guardrails

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/build-and-release.yml](.github/workflows/build-and-release.yml)
- [README.md](README.md)
- [assets/stakpak-dark.png](assets/stakpak-dark.png)
- [assets/stakpak-light.png](assets/stakpak-light.png)
- [cliff.toml](cliff.toml)
- [libs/popup-widget/Cargo.toml](libs/popup-widget/Cargo.toml)
- [libs/popup-widget/README.md](libs/popup-widget/README.md)
- [release.sh](release.sh)

</details>



## Purpose and Scope

Warden Guardrails is a network-level security layer that blocks destructive operations before they execute. It operates as a containerized enforcement mechanism that sits between the AI agent and production systems, providing policy-based protection against dangerous commands and operations.

This document covers the architecture, deployment model, and integration of Warden Guardrails. For information about credential protection, see [Secret Substitution System](#6.1). For transport-level security, see [MCP Architecture](#5.1).

## Architecture Overview

Warden Guardrails implements a defense-in-depth security model where network policies are enforced at the container level, independent of the agent's decision-making process. This architectural separation ensures that even if the agent attempts a destructive operation, it can be blocked before reaching production systems.

```mermaid
graph TB
    subgraph "User Environment"
        USER["User/Developer"]
        CLI["stakpak CLI"]
    end
    
    subgraph "Warden Container"
        WARDEN["Warden Enforcement Layer"]
        POLICY_ENGINE["Policy Engine"]
        NETWORK_FILTER["Network Filter"]
        OPERATION_VALIDATOR["Operation Validator"]
    end
    
    subgraph "Agent Container"
        AGENT["Stakpak Agent"]
        MCP_SERVER["MCP Server"]
        TOOL_CONTAINER["ToolContainer"]
    end
    
    subgraph "Protected Resources"
        PROD_DB["Production Databases"]
        PROD_SERVERS["Production Servers"]
        CLOUD_INFRA["Cloud Infrastructure"]
        CRITICAL_FILES["Critical Files"]
    end
    
    USER --> CLI
    CLI --> WARDEN
    WARDEN --> POLICY_ENGINE
    POLICY_ENGINE --> NETWORK_FILTER
    POLICY_ENGINE --> OPERATION_VALIDATOR
    WARDEN --> AGENT
    AGENT --> MCP_SERVER
    MCP_SERVER --> TOOL_CONTAINER
    
    TOOL_CONTAINER -.blocked by.-> NETWORK_FILTER
    TOOL_CONTAINER -.blocked by.-> OPERATION_VALIDATOR
    
    NETWORK_FILTER -.allows safe access.-> PROD_DB
    NETWORK_FILTER -.allows safe access.-> PROD_SERVERS
    OPERATION_VALIDATOR -.allows safe access.-> CLOUD_INFRA
    OPERATION_VALIDATOR -.allows safe access.-> CRITICAL_FILES
```

**Sources:** [README.md:42-45](), [Diagram 4 from high-level architecture]()

## Deployment Model

Warden Guardrails is packaged as a separate Docker image that wraps the main Stakpak agent. The build system creates two distinct images:

| Image | Purpose | Base |
|-------|---------|------|
| `ghcr.io/stakpak/agent:latest` | Standard agent | Includes CLI tools (docker, kubectl, aws, gcloud) |
| `ghcr.io/stakpak/agent-warden:latest` | Warden-protected agent | Built on top of agent image with network policies |

### Build Process

```mermaid
graph LR
    subgraph "GitHub Actions Workflow"
        BUILD["build job"]
        DOCKER["docker job"]
        DOCKER_WARDEN["docker_warden job"]
    end
    
    BUILD --> DOCKER
    DOCKER --> DOCKER_WARDEN
    
    DOCKER -->|produces| BASE_IMAGE["ghcr.io/stakpak/agent:v1.2.3"]
    DOCKER_WARDEN -->|produces| WARDEN_IMAGE["ghcr.io/stakpak/agent-warden:v1.2.3"]
    
    WARDEN_IMAGE -->|uses as base| BASE_IMAGE
```

The build workflow creates the Warden image using the `.warden` context directory and passes the base image tag as a build argument:

**Sources:** [.github/workflows/build-and-release.yml:246-272]()

### Docker Image Structure

```mermaid
graph TB
    subgraph "Base Image: stakpak/agent"
        AGENT_BIN["stakpak binary"]
        CLI_TOOLS["DevOps CLI tools<br/>kubectl, aws, gcloud, docker"]
        MCP["MCP Server/Client"]
    end
    
    subgraph "Warden Layer"
        POLICIES["Network Policies"]
        ENFORCEMENT["Enforcement Engine"]
        AUDIT_LOG["Audit Logging"]
    end
    
    WARDEN_LAYER["agent-warden image"]
    BASE_LAYER["agent image"]
    
    BASE_LAYER -.contains.-> AGENT_BIN
    BASE_LAYER -.contains.-> CLI_TOOLS
    BASE_LAYER -.contains.-> MCP
    
    WARDEN_LAYER -.extends.-> BASE_LAYER
    WARDEN_LAYER -.adds.-> POLICIES
    WARDEN_LAYER -.adds.-> ENFORCEMENT
    WARDEN_LAYER -.adds.-> AUDIT_LOG
```

**Sources:** [.github/workflows/build-and-release.yml:246-272](), [README.md:102-107]()

## Policy Enforcement Mechanisms

Warden Guardrails operates at two levels to prevent destructive operations:

### Network-Level Filtering

Network policies restrict outbound connections to prevent unauthorized access to production systems. This operates independently of the agent's tool execution logic.

```mermaid
graph TB
    TOOL_CALL["Tool Call Execution"]
    
    subgraph "Network Policy Evaluation"
        CHECK_DEST["Check Destination"]
        CHECK_PORT["Check Port"]
        CHECK_PROTOCOL["Check Protocol"]
        POLICY_DB["Policy Database"]
    end
    
    DECISION{"Policy<br/>Decision"}
    ALLOW["Allow Connection"]
    BLOCK["Block & Log"]
    AUDIT["Audit Trail"]
    
    TOOL_CALL --> CHECK_DEST
    CHECK_DEST --> CHECK_PORT
    CHECK_PORT --> CHECK_PROTOCOL
    CHECK_PROTOCOL --> POLICY_DB
    POLICY_DB --> DECISION
    
    DECISION -->|permitted| ALLOW
    DECISION -->|forbidden| BLOCK
    BLOCK --> AUDIT
```

### Operation-Level Validation

Destructive operations are validated against policy rules before execution:

| Operation Type | Examples | Default Policy |
|----------------|----------|----------------|
| File deletion | `rm -rf`, `remove` tool | Requires explicit approval |
| Database drops | `DROP DATABASE`, `TRUNCATE` | Blocked in production |
| Infrastructure destruction | `terraform destroy`, `kubectl delete` | Requires multi-step approval |
| Credential modification | Password changes, key rotation | Audit + confirmation required |

**Sources:** [README.md:44](), [Diagram 4 security features]()

## Integration with Agent Components

Warden Guardrails integrates with the existing security architecture without modifying the core agent logic:

```mermaid
graph TB
    subgraph "Security Layers"
        WARDEN["Warden Guardrails<br/>Network & Operation Policies"]
        SECRET_MGR["SecretManager<br/>Dynamic Substitution"]
        MTLS["mTLS<br/>Transport Encryption"]
    end
    
    subgraph "Agent Components"
        TOOL_CONTAINER["ToolContainer"]
        REMOTE_CONN["RemoteConnectionManager"]
        SSH["SSH/SFTP Operations"]
        LOCAL_EXEC["Local Command Execution"]
    end
    
    subgraph "External Systems"
        PROD["Production Systems"]
        DEV["Development Systems"]
        CLOUD["Cloud Providers"]
    end
    
    TOOL_CONTAINER --> SECRET_MGR
    SECRET_MGR --> WARDEN
    WARDEN --> MTLS
    
    TOOL_CONTAINER --> REMOTE_CONN
    REMOTE_CONN --> SSH
    TOOL_CONTAINER --> LOCAL_EXEC
    
    MTLS --> PROD
    MTLS --> DEV
    MTLS --> CLOUD
```

### Integration Points

1. **Before Tool Execution:** Warden evaluates policy before `ToolContainer` executes any tool call
2. **Network Interception:** All outbound connections from `RemoteConnectionManager` pass through network filters
3. **Audit Trail:** All blocked and allowed operations are logged for compliance
4. **Secret Coordination:** Works in conjunction with `SecretManager` to ensure credentials are both protected and properly scoped

**Sources:** [Diagram 4 from high-level architecture](), [Diagram 5 tool execution flow]()

## Usage and Configuration

### Running with Warden Protection

Users can run Stakpak with Warden Guardrails enabled by using the Warden Docker image:

```bash
# Standard agent (no Warden)
docker run -it ghcr.io/stakpak/agent:latest

# Warden-protected agent
docker run -it ghcr.io/stakpak/agent-warden:latest
```

For containerization tasks requiring Docker socket access:

```bash
docker run -it \
  -v "/var/run/docker.sock":"/var/run/docker.sock" \
  -v "{your app path}":"/agent/" \
  --entrypoint stakpak \
  ghcr.io/stakpak/agent-warden:latest
```

**Sources:** [README.md:229-237]()

### Policy Configuration

While the exact policy configuration format is defined in the `.warden` directory (not included in provided files), the policies typically control:

- **Network Access:** Whitelist/blacklist of IP ranges, domains, and ports
- **Command Patterns:** Regular expressions matching destructive operations
- **Resource Protection:** Specific files, directories, or database names to protect
- **Time Windows:** Restrictions based on time of day or change windows
- **Approval Requirements:** Multi-factor or manual approval for sensitive operations

## Comparison with Other Security Features

Warden Guardrails complements but does not replace other security mechanisms:

| Feature | Layer | Purpose | Implementation |
|---------|-------|---------|----------------|
| **Warden Guardrails** | Network/Container | Prevent destructive operations from executing | Policy engine at container boundary |
| **Secret Substitution** | Data/Application | Prevent LLM from seeing actual credentials | Dynamic replacement via `SecretManager` |
| **mTLS** | Transport | Encrypt communication between components | Certificate-based encryption in MCP |
| **Privacy Mode** | Data/Application | Redact sensitive data from logs/outputs | Pattern-based redaction |

```mermaid
graph TD
    subgraph "Defense-in-Depth Security Model"
        APP_LAYER["Application Layer"]
        NETWORK_LAYER["Network Layer"]
        DATA_LAYER["Data Layer"]
        TRANSPORT_LAYER["Transport Layer"]
    end
    
    WARDEN["Warden Guardrails"] --> NETWORK_LAYER
    WARDEN --> APP_LAYER
    
    SECRET["Secret Substitution"] --> DATA_LAYER
    SECRET --> APP_LAYER
    
    MTLS["mTLS"] --> TRANSPORT_LAYER
    
    PRIVACY["Privacy Mode"] --> DATA_LAYER
    PRIVACY --> APP_LAYER
```

**Sources:** [README.md:42-45](), [README.md:55-60](), [Diagram 4 security features]()

## Release and Distribution

Warden images are automatically built and published during the release process:

1. **Tag Creation:** When a version tag (e.g., `v1.2.3`) is pushed
2. **Base Image Build:** `docker` job creates the standard agent image
3. **Warden Image Build:** `docker_warden` job extends the base image with Warden layer
4. **Multi-Version Tags:** Both versioned (`v1.2.3`) and `latest` tags are published for stable releases
5. **Beta Releases:** Beta tags (e.g., `v1.2.3-beta.1`) only get versioned tags, not `latest`

The separation of build jobs ensures that the Warden layer can be updated independently of the base agent, and that both images are always synchronized in version.

**Sources:** [.github/workflows/build-and-release.yml:219-272](), [release.sh:274-278]()

## Implementation Notes

The Warden Guardrails implementation resides in the `.warden` directory, which contains:
- Dockerfile with policy configuration
- Network policy definitions
- Operation validation rules
- Audit logging configuration

The specific implementation details of the policy engine, network filtering mechanisms, and operation validators are defined in that directory but are not included in the current documentation scope.

**Sources:** [.github/workflows/build-and-release.yml:266]()

---

# Page: Privacy Mode and Data Redaction

# Privacy Mode and Data Redaction

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/stakpak-dark.png](assets/stakpak-dark.png)
- [assets/stakpak-light.png](assets/stakpak-light.png)
- [libs/api/Cargo.toml](libs/api/Cargo.toml)
- [libs/api/src/lib.rs](libs/api/src/lib.rs)
- [libs/api/src/models.rs](libs/api/src/models.rs)
- [libs/mcp/server/README_SECRETS.md](libs/mcp/server/README_SECRETS.md)

</details>



## Purpose and Scope

Privacy mode is a security feature that redacts sensitive operational data from MCP server and proxy outputs to prevent exposure of private infrastructure information to LLMs and external systems. This includes IP addresses, AWS account IDs, and other identifying information that could reveal details about the deployment environment.

**Note:** Privacy mode is distinct from the [Secret Substitution System](#6.1), which handles credentials, API keys, and tokens. Privacy mode focuses on operational metadata, while secret substitution handles authentication credentials.

For information about blocking destructive operations at the network level, see [Warden Guardrails](#6.2).

**Sources:** [README.md:43-60](), [README.md:270-289]()

---

## Privacy Mode Overview

Privacy mode provides an additional layer of data protection by redacting infrastructure-identifying information that could expose deployment details or enable reconnaissance of the operational environment. Unlike secret substitution which prevents credential exposure, privacy mode prevents leakage of environmental context.

```mermaid
graph TB
    subgraph "Input Sources"
        CMD_OUTPUT["Command Output"]
        FILE_CONTENT["File Contents"]
        TOOL_RESPONSE["Tool Responses"]
    end
    
    subgraph "Privacy Mode Processing"
        DETECTOR["Privacy Data Detector"]
        IP_PATTERN["IP Address Pattern Matcher"]
        ACCOUNT_PATTERN["AWS Account ID Pattern Matcher"]
        REDACTOR["Data Redactor"]
    end
    
    subgraph "Redacted Output"
        LLM_OUTPUT["Sanitized Output to LLM"]
        LOG_OUTPUT["Sanitized Logs"]
    end
    
    CMD_OUTPUT --> DETECTOR
    FILE_CONTENT --> DETECTOR
    TOOL_RESPONSE --> DETECTOR
    
    DETECTOR --> IP_PATTERN
    DETECTOR --> ACCOUNT_PATTERN
    
    IP_PATTERN --> REDACTOR
    ACCOUNT_PATTERN --> REDACTOR
    
    REDACTOR --> LLM_OUTPUT
    REDACTOR --> LOG_OUTPUT
    
    style DETECTOR fill:#f9f9f9
    style REDACTOR fill:#f9f9f9
```

**Sources:** [README.md:55-61]()

---

## Data Types Redacted

Privacy mode targets specific categories of sensitive operational data:

| Data Type | Description | Example | Redacted Form |
|-----------|-------------|---------|---------------|
| **IP Addresses (IPv4)** | Public and private IP addresses | `192.168.1.100`, `54.123.45.67` | `[REDACTED_IP]` |
| **IP Addresses (IPv6)** | IPv6 addresses | `2001:0db8:85a3::8a2e:0370:7334` | `[REDACTED_IP]` |
| **AWS Account IDs** | 12-digit AWS account identifiers | `123456789012` | `[REDACTED_ACCOUNT_ID]` |
| **Infrastructure Identifiers** | Other deployment-specific identifiers | Varies by context | Context-specific redaction |

This redaction prevents:
- **Network topology exposure** - Hiding internal network structure and addressing schemes
- **Cloud account identification** - Preventing correlation of activities to specific AWS accounts
- **Deployment fingerprinting** - Obscuring infrastructure patterns that could aid reconnaissance
- **Cross-reference attacks** - Making it harder to correlate activities across different data sources

**Sources:** [README.md:60]()

---

## Configuration and Usage

### MCP Server with Privacy Mode

Privacy mode is enabled via the `--privacy-mode` command-line flag when starting the MCP server:

```bash
# Enable privacy mode with local tools
stakpak mcp start --tool-mode local --privacy-mode

# Enable privacy mode with combined tools (default)
stakpak mcp start --privacy-mode

# Privacy mode with other security features
stakpak mcp start --privacy-mode --enable-slack-tools
```

**Configuration Matrix:**

| Flag Combination | Secret Redaction | Privacy Mode | Use Case |
|------------------|------------------|--------------|----------|
| Default | Enabled | Disabled | Standard secure operation |
| `--privacy-mode` | Enabled | Enabled | Maximum data protection |
| `--disable-secret-redaction` | Disabled | Disabled | **Not recommended** - debugging only |
| `--disable-secret-redaction --privacy-mode` | Disabled | Enabled | Credentials visible, IPs hidden |

**Sources:** [README.md:251-272]()

### MCP Proxy with Privacy Mode

The MCP proxy server also supports privacy mode for multiplexing connections to upstream MCP servers:

```bash
# Enable privacy mode with automatic config discovery
stakpak mcp proxy --privacy-mode

# Enable privacy mode with explicit config file
stakpak mcp proxy --config-file ~/.stakpak/mcp.toml --privacy-mode

# Combined with secret redaction control
stakpak mcp proxy --privacy-mode --disable-secret-redaction
```

**Sources:** [README.md:277-289]()

---

## Privacy Mode Architecture

```mermaid
graph TB
    subgraph "MCP Server/Proxy Initialization"
        CLI_ARGS["Command-Line Arguments"]
        PRIVACY_FLAG["--privacy-mode flag"]
        CONFIG["Privacy Mode Configuration"]
    end
    
    subgraph "Tool Execution Layer"
        TOOL_EXEC["Tool Execution<br/>(run_command, view, etc)"]
        OUTPUT_CAPTURE["Output Capture"]
    end
    
    subgraph "Privacy Processor"
        PRIVACY_ENGINE["Privacy Data Engine"]
        
        subgraph "Pattern Matchers"
            IPV4_REGEX["IPv4 Regex Matcher"]
            IPV6_REGEX["IPv6 Regex Matcher"]
            AWS_REGEX["AWS Account ID Matcher"]
        end
        
        REDACTION_LOGIC["Redaction Logic"]
    end
    
    subgraph "Output Delivery"
        SANITIZED["Sanitized Response"]
        MCP_RESPONSE["MCP Response to Client"]
    end
    
    CLI_ARGS --> PRIVACY_FLAG
    PRIVACY_FLAG --> CONFIG
    
    CONFIG --> PRIVACY_ENGINE
    
    TOOL_EXEC --> OUTPUT_CAPTURE
    OUTPUT_CAPTURE --> PRIVACY_ENGINE
    
    PRIVACY_ENGINE --> IPV4_REGEX
    PRIVACY_ENGINE --> IPV6_REGEX
    PRIVACY_ENGINE --> AWS_REGEX
    
    IPV4_REGEX --> REDACTION_LOGIC
    IPV6_REGEX --> REDACTION_LOGIC
    AWS_REGEX --> REDACTION_LOGIC
    
    REDACTION_LOGIC --> SANITIZED
    SANITIZED --> MCP_RESPONSE
    
    style CONFIG fill:#f9f9f9
    style PRIVACY_ENGINE fill:#f9f9f9
    style REDACTION_LOGIC fill:#f9f9f9
```

**Sources:** [README.md:241-289]()

---

## Integration with Tool Execution

Privacy mode operates at the output processing layer, after tool execution but before responses are sent to clients:

```mermaid
sequenceDiagram
    participant Client as MCP Client
    participant Server as MCP Server
    participant Tools as ToolContainer
    participant Secret as SecretManager
    participant Privacy as Privacy Processor
    
    Client->>Server: Tool Call Request
    Server->>Tools: Execute Tool
    
    alt Secret Redaction Enabled
        Tools->>Secret: Redact Secrets in Output
        Secret-->>Tools: Output with [REDACTED_SECRET:...] placeholders
    end
    
    alt Privacy Mode Enabled
        Tools->>Privacy: Process Output
        Privacy->>Privacy: Detect IP Addresses
        Privacy->>Privacy: Detect AWS Account IDs
        Privacy->>Privacy: Apply Redactions
        Privacy-->>Tools: Sanitized Output
    end
    
    Tools-->>Server: Final Output
    Server-->>Client: MCP Response
    
    Note over Secret,Privacy: Both layers can operate independently
```

**Key Integration Points:**

1. **Tool Output Processing**: Privacy mode processes all tool outputs before they are returned
2. **Independent from Secret Redaction**: Privacy mode and secret substitution operate independently
3. **Log Sanitization**: Privacy mode also applies to server logs when enabled
4. **Streaming Support**: Works with both synchronous and streaming tool responses

**Sources:** [README.md:55-61](), [README.md:241-272]()

---

## Comparison: Privacy Mode vs Secret Substitution

The system provides two complementary data protection mechanisms:

| Aspect | Privacy Mode | Secret Substitution |
|--------|-------------|---------------------|
| **Primary Purpose** | Hide infrastructure metadata | Protect credentials |
| **Target Data** | IP addresses, account IDs | API keys, passwords, tokens |
| **Detection Method** | Pattern matching (regex) | Gitleaks rule engine |
| **Redaction Format** | `[REDACTED_IP]`, `[REDACTED_ACCOUNT_ID]` | `[REDACTED_SECRET:rule-id:hash]` |
| **Restoration** | Not restorable | Restorable via session mapping |
| **Configuration Flag** | `--privacy-mode` | `--disable-secret-redaction` (inverse) |
| **Session Storage** | No session file | `.stakpak/session/secrets.json` |
| **Default State** | Disabled | Enabled |
| **Use Case** | Prevent infrastructure exposure | Allow LLM to work with credentials |

**Sources:** [README.md:43-44](), [README.md:58-60](), [libs/mcp/server/README_SECRETS.md:1-28]()

---

## Security Considerations

### When to Enable Privacy Mode

Privacy mode should be enabled in the following scenarios:

1. **Multi-tenant Environments**: When multiple users or systems share infrastructure
2. **Cloud Deployments**: To hide cloud provider account identifiers
3. **Compliance Requirements**: When regulations prohibit exposure of network topology
4. **Third-party LLM Services**: When using external LLM providers that may log requests
5. **Audit Trail Sanitization**: When logs may be reviewed by personnel without infrastructure access

### Privacy Mode Limitations

Privacy mode has certain limitations operators should understand:

- **Pattern-based Detection**: Only redacts known patterns; may miss uncommon formats
- **No Restoration**: Unlike secret substitution, redacted data cannot be restored
- **Context Loss**: Aggressive redaction may remove information useful for legitimate operations
- **Performance Impact**: Pattern matching adds processing overhead (typically negligible)
- **Log Correlation**: Redaction may make it harder to correlate events across different log sources

### Combining Security Features

For maximum protection, combine privacy mode with other security features:

```bash
# Maximum security configuration
stakpak mcp start \
  --privacy-mode \
  --tool-mode local \
  --enable-slack-tools

# With explicit secret redaction (already default)
stakpak mcp start \
  --privacy-mode
  # Secret redaction is enabled by default

# For debugging only (NOT RECOMMENDED for production)
stakpak mcp start \
  --disable-secret-redaction \
  --disable-mcp-mtls
  # Privacy mode still disabled, no protection
```

**Sources:** [README.md:55-61](), [README.md:251-272]()

---

## Operational Examples

### Example 1: Command Output Redaction

Without privacy mode:
```bash
$ kubectl get nodes -o wide
NAME           STATUS   IP            INTERNAL-IP
node-1         Ready    54.123.45.67  10.0.1.50
node-2         Ready    54.123.45.68  10.0.1.51
```

With privacy mode enabled:
```bash
$ kubectl get nodes -o wide
NAME           STATUS   IP                 INTERNAL-IP
node-1         Ready    [REDACTED_IP]      [REDACTED_IP]
node-2         Ready    [REDACTED_IP]      [REDACTED_IP]
```

### Example 2: AWS Configuration Redaction

Without privacy mode:
```bash
$ aws sts get-caller-identity
{
    "UserId": "AIDAI...",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/admin"
}
```

With privacy mode enabled:
```bash
$ aws sts get-caller-identity
{
    "UserId": "AIDAI...",
    "Account": "[REDACTED_ACCOUNT_ID]",
    "Arn": "arn:aws:iam::[REDACTED_ACCOUNT_ID]:user/admin"
}
```

### Example 3: Log File Sanitization

Original log content:
```
2024-01-15 10:30:45 INFO Connecting to database at 10.0.1.100:5432
2024-01-15 10:30:46 INFO Connection established from 54.123.45.67
2024-01-15 10:30:47 INFO AWS Account: 123456789012, Region: us-east-1
```

With privacy mode enabled:
```
2024-01-15 10:30:45 INFO Connecting to database at [REDACTED_IP]:5432
2024-01-15 10:30:46 INFO Connection established from [REDACTED_IP]
2024-01-15 10:30:47 INFO AWS Account: [REDACTED_ACCOUNT_ID], Region: us-east-1
```

**Sources:** [README.md:60]()

---

## Implementation Architecture

Privacy mode integrates with the existing tool execution and output processing pipeline:

```mermaid
graph TB
    subgraph "Tool Execution Flow"
        TOOL_CALL["Tool Call Invocation"]
        EXECUTE["Tool Execution"]
        RAW_OUTPUT["Raw Output"]
    end
    
    subgraph "Security Processing Pipeline"
        SECRET_CHECK{Secret Redaction<br/>Enabled?}
        SECRET_PROC["SecretManager<br/>Gitleaks Processing"]
        
        PRIVACY_CHECK{Privacy Mode<br/>Enabled?}
        PRIVACY_PROC["Privacy Processor<br/>Pattern Matching"]
    end
    
    subgraph "Output Processing"
        LARGE_CHECK{Output > 300 lines?}
        FILE_WRITE["Write to File"]
        SANITIZE["ANSI Sanitization"]
        FINAL["Final Output"]
    end
    
    TOOL_CALL --> EXECUTE
    EXECUTE --> RAW_OUTPUT
    
    RAW_OUTPUT --> SECRET_CHECK
    SECRET_CHECK -->|Yes| SECRET_PROC
    SECRET_CHECK -->|No| PRIVACY_CHECK
    SECRET_PROC --> PRIVACY_CHECK
    
    PRIVACY_CHECK -->|Yes| PRIVACY_PROC
    PRIVACY_CHECK -->|No| LARGE_CHECK
    PRIVACY_PROC --> LARGE_CHECK
    
    LARGE_CHECK -->|Yes| FILE_WRITE
    LARGE_CHECK -->|No| SANITIZE
    FILE_WRITE --> SANITIZE
    SANITIZE --> FINAL
    
    style SECRET_PROC fill:#f9f9f9
    style PRIVACY_PROC fill:#f9f9f9
```

**Processing Order:**

1. **Tool Execution**: Run command or operation
2. **Secret Redaction**: Apply gitleaks-based secret detection (if enabled)
3. **Privacy Redaction**: Apply pattern-based privacy data redaction (if enabled)
4. **Large Output Handling**: Write to file if output exceeds threshold
5. **Sanitization**: Remove ANSI codes and normalize text
6. **Delivery**: Return to MCP client

**Sources:** Inferred from [README.md:241-272]() and system architecture context

---

## Best Practices

### Recommended Configurations

**Production Environment:**
```bash
# Maximum security for production
stakpak mcp start --privacy-mode
```

**Development Environment:**
```bash
# Privacy mode without mTLS for local development
stakpak mcp start --privacy-mode --disable-mcp-mtls
```

**Debugging (Temporary):**
```bash
# Disable redaction for debugging (restore after troubleshooting)
stakpak mcp start --disable-secret-redaction
# Note: Privacy mode is disabled by default, so IPs will be visible
```

### Operational Guidelines

1. **Enable by Default in Production**: Always use `--privacy-mode` flag for production deployments
2. **Document Exceptions**: If disabling privacy mode, document the reason and duration
3. **Review Logs Regularly**: Verify that redaction is working as expected
4. **Combine with Network Controls**: Use privacy mode alongside [Warden Guardrails](#6.2) for defense in depth
5. **Test Pattern Coverage**: Verify that your specific data formats are being caught by privacy mode patterns

### Troubleshooting

If privacy mode is not working as expected:

1. **Verify flag is set**: Check that `--privacy-mode` is present in command invocation
2. **Check output format**: Ensure sensitive data matches expected patterns (standard IPv4/IPv6, AWS account ID format)
3. **Review logs**: Look for any privacy processor errors or warnings
4. **Test incrementally**: Start with a simple command that outputs known patterns

**Sources:** [README.md:251-289]()

---

## Related Security Features

Privacy mode is part of Stakpak's comprehensive security architecture:

- **[Secret Substitution System](#6.1)**: Dynamic credential redaction and restoration
- **[Warden Guardrails](#6.2)**: Network-level policy enforcement and destructive operation blocking
- **mTLS Encryption**: End-to-end encrypted MCP communication
- **Secure Password Generation**: Cryptographic password generation tools

Together, these features provide layered security for AI-powered DevOps operations.

**Sources:** [README.md:55-61]()

---

# Page: Build System and Deployment

# Build System and Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/build-and-release.yml](.github/workflows/build-and-release.yml)
- [README.md](README.md)
- [assets/stakpak-dark.png](assets/stakpak-dark.png)
- [assets/stakpak-light.png](assets/stakpak-light.png)
- [cliff.toml](cliff.toml)
- [libs/popup-widget/Cargo.toml](libs/popup-widget/Cargo.toml)
- [libs/popup-widget/README.md](libs/popup-widget/README.md)
- [release.sh](release.sh)

</details>



This document covers the build system, release management, CI/CD pipeline, and distribution mechanisms for the Stakpak agent system. It details the automated release workflow, version management, multi-platform binary compilation, container image builds, and distribution through multiple channels including GitHub releases, crates.io, container registries, and package managers.

For information about workspace structure and package organization, see [Workspace Structure and Packages](#1.2). For security features implemented within deployment containers, see [Security and Privacy](#6).
</thinking>

## Build System Overview

Stakpak uses a Cargo workspace-based build system that compiles multiple interdependent crates into platform-specific binaries. The workspace configuration enforces unified versioning across all packages and includes comprehensive linting rules that deny `unwrap_used` and `expect_used` for production reliability.

**Workspace Structure:**

| Crate | Type | Purpose | Location |
|-------|------|---------|----------|
| `stakpak` | Binary | Main CLI executable | `cli/` |
| `stakpak-tui` | Library | Terminal user interface | `tui/` |
| `stakpak-shared` | Library | Common utilities and types | `libs/shared/` |
| `stakpak-api` | Library | Backend API client | `libs/api/` |
| `stakai` | Library | AI/LLM capabilities | `libs/ai/` |
| `stakpak-mcp-client` | Library | MCP protocol client | `libs/mcp/client/` |
| `stakpak-mcp-server` | Library | MCP protocol server | `libs/mcp/server/` |
| `stakpak-mcp-proxy` | Library | MCP proxy server | `libs/mcp/proxy/` |
| `stakpak-popup-widget` | Library | TUI popup component | `libs/popup-widget/` |

**Sources:** [Cargo.toml:1-17](), [Cargo.toml:19-61](), [Cargo.toml:64-66]()

## Release Management

The release process is managed through the `release.sh` script, which automates version bumping, git tagging, and triggers the CI/CD pipeline.

**Release Workflow:**

```mermaid
graph TB
    subgraph "Version Selection"
        ReleaseScript["release.sh execution"]
        BumpType["Bump type selection<br/>patch/minor/major/<version>"]
        BetaFlag["--beta flag<br/>(optional)"]
        
        ReleaseScript --> BumpType
        ReleaseScript --> BetaFlag
    end
    
    subgraph "Version Calculation"
        CurrentVersion["Get current version<br/>from Cargo.toml"]
        CalculateVersion["Calculate new version<br/>bump_version function"]
        BetaNumber["Get next beta number<br/>git tag analysis"]
        
        BumpType --> CurrentVersion
        CurrentVersion --> CalculateVersion
        BetaFlag --> BetaNumber
        CalculateVersion --> BetaNumber
    end
    
    subgraph "Workspace Update"
        WorkspaceVersion["Update [workspace.package]<br/>version field"]
        DependencyVersions["Update internal dependencies<br/>stakai, stakpak-*, popup-widget"]
        CargoLock["cargo update --workspace<br/>Regenerate Cargo.lock"]
        
        BetaNumber --> WorkspaceVersion
        WorkspaceVersion --> DependencyVersions
        DependencyVersions --> CargoLock
    end
    
    subgraph "Git Operations"
        GitAdd["git add Cargo.toml Cargo.lock"]
        GitCommit["git commit -m 'chore: bump version'"]
        GitTag["git tag v<version>"]
        GitPush["git push origin + tags"]
        
        CargoLock --> GitAdd
        GitAdd --> GitCommit
        GitCommit --> GitTag
        GitTag --> GitPush
    end
    
    subgraph "CI/CD Trigger"
        GithubActions["GitHub Actions workflow<br/>build-and-release.yml"]
        
        GitPush --> GithubActions
    end
    
    style ReleaseScript fill:#e1f5fe
    style WorkspaceVersion fill:#f3e5f5
    style GitTag fill:#fff4e1
```

**Key Features:**

- **Version Bump Types:** Supports `patch`, `minor`, `major`, or explicit version numbers (e.g., `1.2.3`)
- **Beta Releases:** `--beta` flag creates pre-release tags like `v0.1.101-beta.1` with auto-incrementing beta numbers
- **Workspace Synchronization:** Updates both workspace-level version and all internal dependency version references
- **Interactive Mode:** Prompts for version type if not specified as argument
- **Safety Checks:** Validates version format, checks git status, and requires confirmation before proceeding

**Usage Examples:**

```bash
# Patch release: 0.1.100 -> 0.1.101
./release.sh patch

# Beta release: 0.1.100 -> 0.1.101-beta.1
./release.sh patch --beta

# Specific version: 0.1.100 -> 1.0.0
./release.sh 1.0.0

# Interactive mode
./release.sh
```

**Sources:** [release.sh:1-325](), [release.sh:48-94](), [release.sh:96-122](), [release.sh:175-186](), [release.sh:161-173]()

## CI/CD Pipeline

The GitHub Actions workflow `build-and-release.yml` orchestrates multi-platform builds, testing, artifact creation, and distribution across all release channels.

**Pipeline Architecture:**


```mermaid
graph TB
    subgraph "Trigger Events"
        TagPush["git push --tags<br/>v* pattern"]
        BranchPush["git push<br/>main/beta branches"]
        
        TagPush --> SetupJob
        BranchPush --> BuildJob
    end
    
    subgraph "Setup Job"
        SetupJob["setup job<br/>ubuntu-22.04"]
        CheckBeta["Check if beta release<br/>*-beta* in tag"]
        ExtractVersion["Extract version<br/>from tag (remove 'v')"]
        
        SetupJob --> CheckBeta
        SetupJob --> ExtractVersion
    end
    
    subgraph "Build Matrix"
        BuildJob["build job matrix<br/>strategy.matrix"]
        LinuxX64["ubuntu-22.04<br/>x86_64-unknown-linux-musl"]
        LinuxARM["ubuntu-22.04-arm<br/>aarch64-unknown-linux-musl"]
        MacOSX64["macos-15<br/>x86_64-apple-darwin"]
        MacOSARM["macos-15<br/>aarch64-apple-darwin"]
        WindowsX64["windows-2022<br/>x86_64-pc-windows-msvc"]
        
        BuildJob --> LinuxX64
        BuildJob --> LinuxARM
        BuildJob --> MacOSX64
        BuildJob --> MacOSARM
        BuildJob --> WindowsX64
    end
    
    subgraph "Build Steps"
        RustToolchain["Install Rust 1.89.0<br/>dtolnay/rust-toolchain"]
        RustCache["Rust Cache<br/>Swatinem/rust-cache"]
        MUSLTools["Install MUSL tools<br/>(Linux only)"]
        CargoBuild["cargo build --release<br/>--target <matrix.target>"]
        CargoTest["cargo test<br/>--target <matrix.target>"]
        
        LinuxX64 --> RustToolchain
        LinuxARM --> RustToolchain
        MacOSX64 --> RustToolchain
        MacOSARM --> RustToolchain
        WindowsX64 --> RustToolchain
        RustToolchain --> RustCache
        RustCache --> MUSLTools
        MUSLTools --> CargoBuild
        CargoBuild --> CargoTest
    end
    
    subgraph "Artifact Packaging"
        PrepBinary["Prepare binary<br/>(tags only)"]
        LinuxTarGz["tar czf<br/>stakpak-linux-*.tar.gz"]
        DarwinTarGz["tar czf<br/>stakpak-darwin-*.tar.gz"]
        WindowsZip["7z a<br/>stakpak-windows-*.zip"]
        UploadArtifact["Upload artifact<br/>actions/upload-artifact@v4"]
        
        CargoTest --> PrepBinary
        PrepBinary --> LinuxTarGz
        PrepBinary --> DarwinTarGz
        PrepBinary --> WindowsZip
        LinuxTarGz --> UploadArtifact
        DarwinTarGz --> UploadArtifact
        WindowsZip --> UploadArtifact
    end
    
    subgraph "Distribution Jobs"
        ReleaseJob["release job<br/>Create GitHub Release"]
        CratesIOJob["publish_crates_io job<br/>Publish to crates.io"]
        DockerJob["docker job<br/>Build base image"]
        WardenJob["docker_warden job<br/>Build warden image"]
        HomebrewJob["homebrew job<br/>Update formula"]
        NotesJob["update-release-notes job<br/>Generate changelog"]
        
        UploadArtifact --> ReleaseJob
        UploadArtifact --> CratesIOJob
        ReleaseJob --> DockerJob
        DockerJob --> WardenJob
        ReleaseJob --> HomebrewJob
        ReleaseJob --> NotesJob
    end
    
    style SetupJob fill:#e1f5fe
    style BuildJob fill:#f3e5f5
    style ReleaseJob fill:#fff4e1
```

**Job Dependencies and Execution Flow:**

The workflow uses a dependency graph where downstream jobs wait for upstream jobs to complete successfully:

1. **setup** → Determines release type (`is_beta`, `version`)
2. **build** → Compiles for all platforms in parallel (no dependencies)
3. **release** → Waits for `setup` + `build`, creates GitHub release
4. **publish_crates_io** → Waits for `build`, publishes to crates.io registry
5. **docker** → Waits for `setup` + `build`, builds base Docker image
6. **docker_warden** → Waits for `setup` + `docker`, builds warden image
7. **homebrew** → Waits for `setup` + `release`, updates Homebrew tap
8. **update-release-notes** → Waits for `release`, generates changelog with git-cliff

**Sources:** [.github/workflows/build-and-release.yml:1-15](), [.github/workflows/build-and-release.yml:27-46](), [.github/workflows/build-and-release.yml:48-112](), [.github/workflows/build-and-release.yml:114-137]()

## Build Configuration and Targets

**Platform Build Matrix:**

| Platform | OS Runner | Rust Target | Artifact Format | Special Setup |
|----------|-----------|-------------|-----------------|---------------|
| Linux x86_64 | ubuntu-22.04 | x86_64-unknown-linux-musl | tar.gz | musl-tools installation |
| Linux ARM64 | ubuntu-22.04-arm | aarch64-unknown-linux-musl | tar.gz | musl-tools installation |
| macOS x86_64 | macos-15 | x86_64-apple-darwin | tar.gz | None |
| macOS ARM64 | macos-15 | aarch64-apple-darwin | tar.gz | None |
| Windows x86_64 | windows-2022 | x86_64-pc-windows-msvc | zip | 7z compression |

**Build Optimizations:**

- **MUSL Targets:** Linux builds use MUSL libc for static linking, producing fully portable binaries without dynamic library dependencies
- **Rust Cache:** `Swatinem/rust-cache@v2` with per-target shared keys reduces build times by caching dependencies
- **Static Linking:** Linux builds set `RUSTFLAGS: '-C target-feature=+crt-static'` for complete static linking

**Sources:** [.github/workflows/build-and-release.yml:48-66](), [.github/workflows/build-and-release.yml:74-94]()

## Crates.io Publishing

The `publish_crates_io` job publishes all workspace crates to the Rust package registry in dependency order.

**Publishing Sequence:**

```mermaid
graph TB
    subgraph "Pre-Publish"
        ExtractVersion["Extract version from tag<br/>sed, grep Cargo.toml"]
        VersionVerify["Verify tag matches Cargo.toml<br/>Update if mismatch"]
        CargoLogin["cargo login<br/>CRATES_IO_TOKEN"]
        
        ExtractVersion --> VersionVerify
        VersionVerify --> CargoLogin
    end
    
    subgraph "Dependency Order"
        PublishFunc["publish_package function<br/>cargo publish -p <pkg>"]
        
        stakai["stakai<br/>(no dependencies)"]
        shared["stakpak-shared<br/>(depends: stakai)"]
        api["stakpak-api<br/>(depends: shared)"]
        popup["stakpak-popup-widget<br/>(no dependencies)"]
        mcpclient["stakpak-mcp-client<br/>(depends: shared)"]
        mcpserver["stakpak-mcp-server<br/>(depends: shared)"]
        mcpproxy["stakpak-mcp-proxy<br/>(depends: shared)"]
        tui["stakpak-tui<br/>(depends: api, popup)"]
        cli["stakpak<br/>(depends: all)"]
        
        CargoLogin --> PublishFunc
        PublishFunc --> stakai
        stakai --> shared
        shared --> api
        shared --> popup
        shared --> mcpclient
        shared --> mcpserver
        shared --> mcpproxy
        api --> tui
        popup --> tui
        mcpclient --> cli
        mcpserver --> cli
        mcpproxy --> cli
        tui --> cli
    end
    
    subgraph "Error Handling"
        CheckAlreadyPublished["Check if already published<br/>grep 'already uploaded'"]
        WaitPropagate["Wait 15s for index<br/>propagation"]
        
        PublishFunc --> CheckAlreadyPublished
        CheckAlreadyPublished --> WaitPropagate
    end
    
    style PublishFunc fill:#e1f5fe
    style cli fill:#fff4e1
```

**Key Features:**

- **Dependency-First:** Publishes dependencies before dependents to avoid registry errors
- **Idempotency:** Skips already-published versions with "already uploaded" detection
- **Index Propagation:** 15-second wait between publishes for crates.io index to update
- **Verification Skip:** Uses `--no-verify` flag to skip re-compilation during publish
- **Version Synchronization:** Auto-updates Cargo.toml if tag version doesn't match

**Sources:** [.github/workflows/build-and-release.yml:139-218](), [.github/workflows/build-and-release.yml:179-200](), [.github/workflows/build-and-release.yml:202-214]()

## Docker Image Build Process

Docker images are built for both the base agent and the security-hardened warden wrapper.

**Base Image Build (`docker` job):**

```mermaid
graph TB
    subgraph "Builder Stage"
        RustBuilder["FROM rust:1.89.0-slim-bookworm"]
        BuildDeps["Install build dependencies<br/>pkg-config, libssl-dev, git"]
        CopySource["COPY workspace files"]
        CargoBuild["cargo build --release<br/>--bin stakpak"]
        ExtractBinary["Extract binary from<br/>target/release/stakpak"]
        
        RustBuilder --> BuildDeps
        BuildDeps --> CopySource
        CopySource --> CargoBuild
        CargoBuild --> ExtractBinary
    end
    
    subgraph "Runtime Stage"
        DebianBase["FROM debian:bookworm-slim"]
        RuntimeDeps["Install runtime dependencies<br/>ca-certificates, curl, sudo, etc"]
        CloudCLIs["Install cloud provider CLIs<br/>aws, gcloud, az, doctl"]
        InfraTools["Install infrastructure tools<br/>terraform, docker-cli"]
        CreateUser["Create agent user<br/>with docker group"]
        ConfigureSudo["Configure sudo permissions<br/>/etc/sudoers.d/agent"]
        CopyBinary["COPY stakpak binary<br/>from builder stage"]
        
        DebianBase --> RuntimeDeps
        RuntimeDeps --> CloudCLIs
        CloudCLIs --> InfraTools
        InfraTools --> CreateUser
        CreateUser --> ConfigureSudo
        ConfigureSudo --> CopyBinary
        ExtractBinary --> CopyBinary
    end
    
    subgraph "Publish"
        TagVersion["ghcr.io/stakpak/agent:v<version>"]
        TagLatest["ghcr.io/stakpak/agent:latest<br/>(stable only)"]
        
        CopyBinary --> TagVersion
        CopyBinary --> TagLatest
    end
    
    style CargoBuild fill:#e1f5fe
    style CopyBinary fill:#f3e5f5
```

**Installed Tooling:**

| Component | Purpose | Installation Method | Version Detection |
|-----------|---------|---------------------|-------------------|
| **AWS CLI** | Amazon Web Services management | Binary download | Architecture-specific (x86_64/aarch64) |
| **Google Cloud CLI** | Google Cloud Platform operations | APT repository | Latest stable from Google repo |
| **Azure CLI** | Microsoft Azure management | Microsoft script | Latest from install script |
| **DigitalOcean CLI** | DigitalOcean management | Binary download | GitHub API latest release |
| **Terraform** | Infrastructure as Code | Binary download | HashiCorp API latest version |
| **Docker CLI** | Container operations | APT repository | Latest from Docker official repo |
| **kubectl** | Kubernetes operations | Binary download | Latest stable version |
| **jq** | JSON processing | APT package | Debian repository version |

**User and Permissions Configuration:**

The container runs as a non-root `agent` user (UID 1001) with carefully configured sudo permissions:

- **User Setup:** Creates `agent` user and adds to `docker` group for Docker socket access
- **Sudo Rules:** `/etc/sudoers.d/agent` grants NOPASSWD access to package managers (apt-get, apt, dpkg, snap)
- **Working Directory:** `/agent` set as WORKDIR with agent ownership
- **Entrypoint:** `/usr/local/bin/stakpak` executable

**Sources:** [Dockerfile:1-113](), [Dockerfile:16-96](), [Dockerfile:97-113](), [Dockerfile:103-106]()

**Warden Image Build (`docker_warden` job):**

The warden image extends the base image with transparent proxy capabilities and enhanced security restrictions:

```mermaid
graph TB
    subgraph "Base"
        BaseImage["FROM ghcr.io/stakpak/agent:v<version>"]
        SwitchRoot["Switch to root<br/>for installation"]
        
        BaseImage --> SwitchRoot
    end
    
    subgraph "Proxy Setup"
        InstallRedsocks["Install redsocks<br/>transparent proxy"]
        InstallIptables["Install iptables<br/>firewall rules"]
        CopyConfig["COPY redsocks.conf.template<br/>/etc/redsocks/"]
        CopyScripts["COPY security scripts<br/>start/test-proxy/test-security"]
        MakeExecutable["chmod +x scripts"]
        
        SwitchRoot --> InstallRedsocks
        InstallRedsocks --> InstallIptables
        InstallIptables --> CopyConfig
        CopyConfig --> CopyScripts
        CopyScripts --> MakeExecutable
    end
    
    subgraph "Security Hardening"
        SudoRestrictions["Append sudo restrictions<br/>block iptables/netfilter"]
        RemoveSetuid["Remove setuid bits<br/>from network tools"]
        
        MakeExecutable --> SudoRestrictions
        SudoRestrictions --> RemoveSetuid
    end
    
    subgraph "Finalize"
        SwitchAgent["Switch back to agent user"]
        SetEntrypoint["ENTRYPOINT start-transparent-proxy.sh"]
        
        RemoveSetuid --> SwitchAgent
        SwitchAgent --> SetEntrypoint
    end
    
    subgraph "Publish"
        TagWardenVersion["ghcr.io/stakpak/agent-warden:v<version>"]
        TagWardenLatest["ghcr.io/stakpak/agent-warden:latest<br/>(stable only)"]
        
        SetEntrypoint --> TagWardenVersion
        SetEntrypoint --> TagWardenLatest
    end
    
    style InstallRedsocks fill:#e1f5fe
    style SudoRestrictions fill:#ffebee
```

**Warden Security Features:**

- **Transparent Proxy:** `redsocks` redirects all outbound traffic through a SOCKS proxy
- **iptables Configuration:** Custom rules route traffic and prevent direct internet access
- **Sudo Restrictions:** Additional rules block `iptables`, `ip6tables`, `nft`, and related tools
- **Setuid Removal:** Removes setuid bits from `ping`, `ping6`, `traceroute`, `traceroute6`
- **Startup Script:** `start-transparent-proxy.sh` configures proxy and launches stakpak

**Sources:** [.warden/Dockerfile:1-47](), [.warden/Dockerfile:24-26](), [.warden/Dockerfile:28-39](), [.warden/Dockerfile:41-47](), [.github/workflows/build-and-release.yml:220-245](), [.github/workflows/build-and-release.yml:247-273]()

## Release Notes Generation

The `update-release-notes` job uses `git-cliff` to generate formatted changelogs following Conventional Commits.

**Changelog Generation Process:**

```mermaid
graph TB
    subgraph "Setup"
        Checkout["Checkout repository<br/>fetch-depth: 0 (full history)"]
        InstallCliff["cargo install git-cliff"]
        
        Checkout --> InstallCliff
    end
    
    subgraph "Tag Analysis"
        GetCurrentTag["Get current tag<br/>GITHUB_REF#refs/tags/"]
        GetPreviousTag["git describe --tags<br/>--abbrev=0 TAG^"]
        
        InstallCliff --> GetCurrentTag
        GetCurrentTag --> GetPreviousTag
    end
    
    subgraph "Generation"
        RunCliff["git-cliff PREV..CURRENT<br/>--strip all"]
        CliffConfig["cliff.toml configuration<br/>Conventional Commits"]
        OutputMd["Generate release_notes.md"]
        
        GetPreviousTag --> RunCliff
        RunCliff --> CliffConfig
        CliffConfig --> OutputMd
    end
    
    subgraph "Validation"
        CheckEmpty["Check if notes are empty"]
        CheckWhitespace["Check for content"]
        
        OutputMd --> CheckEmpty
        CheckEmpty --> CheckWhitespace
    end
    
    subgraph "Update"
        GhRelease["gh release edit TAG<br/>--notes-file release_notes.md"]
        
        CheckWhitespace --> GhRelease
    end
    
    style RunCliff fill:#e1f5fe
    style CliffConfig fill:#f3e5f5
```

**Conventional Commit Categories:**

The `cliff.toml` configuration defines commit parsing rules:

| Commit Prefix | Category | Description |
|---------------|----------|-------------|
| `feat` | Features | New features and capabilities |
| `fix` | Bug Fixes | Bug fixes and corrections |
| `docs` | Documentation | Documentation updates |
| `perf` | Performance | Performance improvements |
| `refactor` | Refactoring | Code refactoring without behavior changes |
| `style` | Code Style | Formatting and style changes |
| `test` | Testing | Test additions and updates |
| `chore`, `ci` | Maintenance | Maintenance tasks and CI changes |
| `revert` | Reverts | Reverted changes |
| `*security*` (body) | Security | Security-related changes |

**Excluded Commits:**
- `chore(release): prepare for` - Release preparation commits
- `chore(deps*)` - Dependency update commits  
- `chore(pr)`, `chore(pull)` - PR-related commits

**Sources:** [.github/workflows/build-and-release.yml:275-328](), [cliff.toml:1-62](), [cliff.toml:31-46]()

## Homebrew Distribution

The `homebrew` job updates the Homebrew tap repository with new release information for stable (non-beta) releases only.

**Update Process:**

```mermaid
graph TB
    subgraph "Prerequisites"
        CheckBeta["Check is_beta flag<br/>(skip if beta)"]
        Checkout["Checkout homebrew-stakpak<br/>stakpak/homebrew-stakpak"]
        
        CheckBeta --> Checkout
    end
    
    subgraph "Download Artifacts"
        DownloadDarwinX64["curl darwin-x86_64.tar.gz"]
        DownloadDarwinARM["curl darwin-aarch64.tar.gz"]
        DownloadLinuxX64["curl linux-x86_64.tar.gz"]
        DownloadLinuxARM["curl linux-aarch64.tar.gz"]
        
        Checkout --> DownloadDarwinX64
        Checkout --> DownloadDarwinARM
        Checkout --> DownloadLinuxX64
        Checkout --> DownloadLinuxARM
    end
    
    subgraph "Calculate Checksums"
        SHA256DarwinX64["sha256sum darwin-x86_64"]
        SHA256DarwinARM["sha256sum darwin-aarch64"]
        SHA256LinuxX64["sha256sum linux-x86_64"]
        SHA256LinuxARM["sha256sum linux-aarch64"]
        
        DownloadDarwinX64 --> SHA256DarwinX64
        DownloadDarwinARM --> SHA256DarwinARM
        DownloadLinuxX64 --> SHA256LinuxX64
        DownloadLinuxARM --> SHA256LinuxARM
    end
    
    subgraph "Generate Formula"
        CreateFormula["cat > stakpak.rb"]
        VersionField["version field"]
        URLFields["url fields by platform/arch"]
        SHA256Fields["sha256 fields for verification"]
        InstallBlock["def install block<br/>bin.install 'stakpak'"]
        
        SHA256DarwinX64 --> CreateFormula
        SHA256DarwinARM --> CreateFormula
        SHA256LinuxX64 --> CreateFormula
        SHA256LinuxARM --> CreateFormula
        CreateFormula --> VersionField
        CreateFormula --> URLFields
        CreateFormula --> SHA256Fields
        CreateFormula --> InstallBlock
    end
    
    subgraph "Commit and Push"
        GitConfig["git config user<br/>GitHub Actions"]
        GitAdd["git add stakpak.rb"]
        GitCommit["git commit -m 'Update to v<version>'"]
        GitPush["git push"]
        
        InstallBlock --> GitConfig
        GitConfig --> GitAdd
        GitAdd --> GitCommit
        GitCommit --> GitPush
    end
    
    style CreateFormula fill:#e1f5fe
    style SHA256Fields fill:#f3e5f5
```

**Homebrew Formula Structure:**

The generated `stakpak.rb` formula includes:
- **Version Declaration:** Extracted from release tag
- **Platform Detection:** `on_macos` and `on_linux` blocks with CPU architecture checks
- **URL Generation:** GitHub release download URLs for each platform/architecture combination
- **SHA256 Verification:** Checksums for all artifacts to ensure download integrity
- **Installation Logic:** Simple `bin.install "stakpak"` to place binary in Homebrew's bin directory

**Sources:** [.github/workflows/build-and-release.yml:330-393](), [.github/workflows/build-and-release.yml:346-386]()

## Distribution Channels

The stakpak agent is distributed through multiple channels to support different deployment scenarios:

### GitHub Releases
Binary artifacts are automatically created for each tagged release with platform-specific packaging:
- Linux: `stakpak-linux-{x86_64,aarch64}.tar.gz`
- macOS: `stakpak-darwin-{x86_64,aarch64}.tar.gz`  
- Windows: `stakpak-windows-x86_64.zip`

### Container Registry
Docker images are published to GitHub Container Registry with semantic versioning:
- Base image: `ghcr.io/stakpak/agent:{version,latest}`
- Warden image: `ghcr.io/stakpak/agent-warden:{version,latest}`

### Homebrew Package Manager
The `homebrew` job automatically updates the Homebrew tap repository with new release information including SHA256 checksums for package verification.

```mermaid
graph LR
    subgraph "Release Artifacts"
        BinaryReleases["GitHub Release<br/>Cross-platform binaries"]
        DockerImages["Container Registry<br/>ghcr.io images"]
        HomebrewFormula["Homebrew Tap<br/>stakpak/homebrew-stakpak"]
    end
    
    subgraph "Installation Methods"
        DirectDownload["Direct binary download<br/>curl + tar/unzip"]
        DockerRun["docker run<br/>ghcr.io/stakpak/agent"]
        BrewInstall["brew install<br/>stakpak/stakpak/stakpak"]
        CargoInstall["cargo install --git<br/>Development builds"]
    end
    
    BinaryReleases --> DirectDownload
    DockerImages --> DockerRun
    HomebrewFormula --> BrewInstall
    BinaryReleases --> CargoInstall
    
    style BinaryReleases fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    style DockerImages fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
```

**Sources:** [.github/workflows/build-and-release.yml:84-106](), [.github/workflows/build-and-release.yml:129-137](), [.github/workflows/build-and-release.yml:171-232]()

## Workspace Configuration

The deployment is built from a Cargo workspace containing multiple crates with shared dependencies and unified versioning.

| Crate | Purpose | Location |
|-------|---------|----------|
| `cli` | Main binary and entry point | `cli/` |
| `tui` | Terminal user interface | `tui/` |
| `stakpak-shared` | Common utilities and types | `libs/shared/` |
| `stakpak-api` | Backend API client | `libs/api/` |
| `mcp-client` | MCP protocol client | `libs/mcp/client/` |
| `mcp-server` | MCP protocol server | `libs/mcp/server/` |

The workspace uses version `0.1.156` with Rust edition `2024` and includes comprehensive linting rules that deny `unwrap_used` and `expect_used` for enhanced reliability in production deployments.

**Sources:** [Cargo.toml:1-17](), [Cargo.toml:64-66]()

---

# Page: CI/CD Pipeline

# CI/CD Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/build-and-release.yml](.github/workflows/build-and-release.yml)
- [cliff.toml](cliff.toml)
- [libs/popup-widget/Cargo.toml](libs/popup-widget/Cargo.toml)
- [libs/popup-widget/README.md](libs/popup-widget/README.md)
- [release.sh](release.sh)

</details>



## Purpose and Scope

This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline implemented through GitHub Actions for the Stakpak project. The pipeline handles multi-platform builds, automated testing, artifact creation, and distribution across multiple channels including GitHub Releases, crates.io, Docker registries, and Homebrew.

For information about the manual release process and version management, see [Release Management](#7.2). For details on distribution channels and package formats, see [Distribution Channels](#7.3).

**Sources:** [.github/workflows/build-and-release.yml:1-393]()

---

## Workflow Triggers and Execution Modes

The CI/CD pipeline operates in two distinct modes based on the trigger type: **build-only mode** for branch pushes and **full release mode** for version tags.

### Trigger Conditions

| Trigger Type | Pattern | Execution Mode | Jobs Executed |
|-------------|---------|----------------|---------------|
| Branch Push | `main` | Build Only | `setup`, `build` |
| Branch Push | `beta` | Build Only | `setup`, `build` |
| Tag Push | `v1.2.3` | Full Release (Stable) | All jobs |
| Tag Push | `v1.2.3-beta.1` | Full Release (Beta) | All jobs |

The workflow uses `startsWith(github.ref, 'refs/tags/')` to differentiate between branch pushes and tag pushes. Beta releases are identified by the presence of `-beta` in the tag name.

**Sources:** [.github/workflows/build-and-release.yml:3-14](), [.github/workflows/build-and-release.yml:34-45]()

---

## Build Matrix and Platform Support

### Multi-Platform Build Architecture

The build system compiles native binaries for five platform/architecture combinations using a GitHub Actions matrix strategy:

```mermaid
graph TB
    subgraph "Build Matrix Strategy"
        MATRIX["Matrix Configuration<br/>.github/workflows/build-and-release.yml:48-66"]
    end
    
    subgraph "Linux Builds"
        LINUX_X64["x86_64-unknown-linux-musl<br/>ubuntu-22.04<br/>stakpak-linux-x86_64"]
        LINUX_ARM["aarch64-unknown-linux-musl<br/>ubuntu-22.04-arm<br/>stakpak-linux-aarch64"]
    end
    
    subgraph "macOS Builds"
        MACOS_X64["x86_64-apple-darwin<br/>macos-15<br/>stakpak-darwin-x86_64"]
        MACOS_ARM["aarch64-apple-darwin<br/>macos-15<br/>stakpak-darwin-aarch64"]
    end
    
    subgraph "Windows Builds"
        WINDOWS_X64["x86_64-pc-windows-msvc<br/>windows-2022<br/>stakpak-windows-x86_64"]
    end
    
    MATRIX --> LINUX_X64
    MATRIX --> LINUX_ARM
    MATRIX --> MACOS_X64
    MATRIX --> MACOS_ARM
    MATRIX --> WINDOWS_X64
```

**Diagram: Build Matrix Strategy and Platform Targets**

### Build Process Steps

Each platform build executes the following sequence:

1. **Toolchain Setup** - Installs Rust 1.89.0 with target-specific toolchain ([.github/workflows/build-and-release.yml:73-76]())
2. **Caching** - Uses `Swatinem/rust-cache@v2` with per-target cache keys ([.github/workflows/build-and-release.yml:78-81]())
3. **Platform-Specific Dependencies** - Linux MUSL builds install `musl-tools` ([.github/workflows/build-and-release.yml:83-85]())
4. **Compilation** - Executes `cargo build --release --target $TARGET` ([.github/workflows/build-and-release.yml:87-90]())
5. **Testing** - Runs `cargo test --target $TARGET` ([.github/workflows/build-and-release.yml:92-93]())
6. **Artifact Packaging** - Creates `.tar.gz` (Unix) or `.zip` (Windows) archives ([.github/workflows/build-and-release.yml:95-104]())
7. **Upload** - Stores artifacts for downstream jobs ([.github/workflows/build-and-release.yml:106-112]())

### Linux Static Linking

Linux builds use MUSL targets (`x86_64-unknown-linux-musl`, `aarch64-unknown-linux-musl`) to produce statically-linked binaries that run on any Linux distribution without external dependencies. The ARM64 build runs on GitHub's ARM runners (`ubuntu-22.04-arm`) for native compilation.

**Sources:** [.github/workflows/build-and-release.yml:48-112]()

---

## Job Dependency Graph and Execution Flow

```mermaid
graph TB
    SETUP["setup<br/>Check release type<br/>Output: is_beta, version"]
    BUILD["build<br/>Matrix: 5 platforms<br/>Compile, test, package"]
    RELEASE["release<br/>Create GitHub Release<br/>Upload artifacts"]
    CRATES["publish_crates_io<br/>Publish workspace to crates.io<br/>9 packages in order"]
    DOCKER["docker<br/>Build main image<br/>ghcr.io/stakpak/agent"]
    WARDEN["docker_warden<br/>Build Warden image<br/>ghcr.io/stakpak/agent-warden"]
    NOTES["update-release-notes<br/>Generate with git-cliff<br/>Update GitHub Release"]
    HOMEBREW["homebrew<br/>Update formula<br/>stakpak/homebrew-stakpak"]
    
    SETUP --> BUILD
    SETUP --> RELEASE
    BUILD --> RELEASE
    BUILD --> CRATES
    SETUP --> DOCKER
    BUILD --> DOCKER
    SETUP --> WARDEN
    DOCKER --> WARDEN
    RELEASE --> NOTES
    SETUP --> HOMEBREW
    RELEASE --> HOMEBREW
```

**Diagram: Job Dependency Graph for Release Pipeline**

### Job Descriptions

| Job Name | Depends On | Condition | Purpose |
|----------|-----------|-----------|---------|
| `setup` | None | Always | Extracts version from tag, determines if beta release |
| `build` | None | Always | Compiles binaries for all platforms, runs tests |
| `release` | `setup`, `build` | Tag push only | Creates GitHub Release, uploads binary artifacts |
| `publish_crates_io` | `build` | Tag push only | Publishes workspace packages to crates.io |
| `docker` | `setup`, `build` | Tag push only | Builds main Docker image |
| `docker_warden` | `setup`, `docker` | Tag push only | Builds Warden security container |
| `update-release-notes` | `release` | Tag push only | Generates changelog with git-cliff, updates release |
| `homebrew` | `setup`, `release` | Tag push, not beta | Updates Homebrew tap formula |

**Sources:** [.github/workflows/build-and-release.yml:27-45](), [.github/workflows/build-and-release.yml:114-392]()

---

## Release Creation and Artifact Distribution

### GitHub Release Job

The `release` job aggregates artifacts from all platform builds and creates a unified GitHub Release:

```mermaid
graph LR
    subgraph "Artifact Downloads"
        A1["stakpak-linux-x86_64.tar.gz"]
        A2["stakpak-linux-aarch64.tar.gz"]
        A3["stakpak-darwin-x86_64.tar.gz"]
        A4["stakpak-darwin-aarch64.tar.gz"]
        A5["stakpak-windows-x86_64.zip"]
    end
    
    subgraph "Release Creation"
        ACTION["softprops/action-gh-release@v1"]
    end
    
    subgraph "GitHub Release"
        RELEASE["GitHub Release<br/>Tag: v{version}<br/>Prerelease: if beta"]
    end
    
    A1 --> ACTION
    A2 --> ACTION
    A3 --> ACTION
    A4 --> ACTION
    A5 --> ACTION
    
    ACTION --> RELEASE
```

**Diagram: GitHub Release Artifact Aggregation**

The release is marked as prerelease if `is_beta == 'true'`, and GitHub automatically generates release notes from commit history ([.github/workflows/build-and-release.yml:124-136]()).

### Release Notes Enhancement

After the initial release, the `update-release-notes` job enhances the release notes using `git-cliff`:

1. **Install git-cliff** - Installs the changelog generator ([.github/workflows/build-and-release.yml:283-284]())
2. **Generate Changelog** - Runs `git-cliff $PREV_TAG..$VERSION --strip all` ([.github/workflows/build-and-release.yml:286-306]())
3. **Update Release** - Uses `gh release edit` to update notes ([.github/workflows/build-and-release.yml:308-327]())

The `cliff.toml` configuration groups commits by conventional commit type (feat, fix, docs, etc.) and formats them into categorized sections ([cliff.toml:31-46]()).

**Sources:** [.github/workflows/build-and-release.yml:114-136](), [.github/workflows/build-and-release.yml:274-327](), [cliff.toml:1-62]()

---

## Crates.io Publishing Pipeline

### Workspace Publishing Strategy

The `publish_crates_io` job publishes all workspace members to crates.io in dependency order to ensure each package's dependencies are available before publication:

```mermaid
graph TB
    subgraph "Publishing Order"
        P1["1. stakai<br/>AI/LLM capabilities"]
        P2["2. stakpak-shared<br/>Common utilities"]
        P3["3. stakpak-api<br/>AgentProvider trait"]
        P4["4. stakpak-popup-widget<br/>TUI component"]
        P5["5. stakpak-mcp-client<br/>MCP client"]
        P6["6. stakpak-mcp-server<br/>MCP server"]
        P7["7. stakpak-mcp-proxy<br/>MCP proxy"]
        P8["8. stakpak-tui<br/>Terminal UI"]
        P9["9. stakpak<br/>Main CLI crate"]
    end
    
    P1 --> P2
    P2 --> P3
    P3 --> P4
    P4 --> P5
    P5 --> P6
    P6 --> P7
    P7 --> P8
    P8 --> P9
```

**Diagram: Crates.io Publishing Dependency Order**

### Publishing Logic

The `publish_package` function handles each package publication with error handling:

- **Success Case**: Package publishes, waits 15 seconds for index propagation ([.github/workflows/build-and-release.yml:190-192]())
- **Already Published**: Detects "already uploaded" error, skips gracefully ([.github/workflows/build-and-release.yml:193-194]())
- **Failure**: Reports error and exits ([.github/workflows/build-and-release.yml:195-199]())

The job includes version verification to ensure the tag version matches `Cargo.toml`, updating it if necessary ([.github/workflows/build-and-release.yml:148-165]()).

**Sources:** [.github/workflows/build-and-release.yml:138-217]()

---

## Docker Image Build Pipeline

### Main Docker Image

The `docker` job builds the primary Stakpak Docker image:

- **Build Context**: Repository root directory
- **Platform**: `linux/amd64`
- **Registry**: GitHub Container Registry (`ghcr.io`)
- **Tags**: 
  - Version-specific: `ghcr.io/stakpak/agent:v{version}`
  - Latest (stable only): `ghcr.io/stakpak/agent:latest` ([.github/workflows/build-and-release.yml:242-244]())

The image uses Docker Buildx for efficient multi-stage builds ([.github/workflows/build-and-release.yml:226-227]()).

### Warden Security Container

The `docker_warden` job builds a specialized security-enhanced container:

- **Build Context**: `.warden` directory
- **Base Image**: Uses version-tagged main image as base via `BASE_IMAGE_TAG` build arg ([.github/workflows/build-and-release.yml:268-269]())
- **Tags**:
  - `ghcr.io/stakpak/agent-warden:v{version}`
  - `ghcr.io/stakpak/agent-warden:latest` (stable only)

This job depends on the `docker` job completing, ensuring the base image exists before building the Warden variant.

**Sources:** [.github/workflows/build-and-release.yml:219-272]()

---

## Homebrew Formula Updates

The `homebrew` job automatically updates the Homebrew tap for macOS and Linux installations. It only runs for **stable releases** (not beta) ([.github/workflows/build-and-release.yml:332]()).

### Update Process

```mermaid
graph TB
    CHECKOUT["Checkout homebrew-stakpak repo<br/>stakpak/homebrew-stakpak"]
    
    subgraph "Download Artifacts"
        D1["Download darwin-x86_64.tar.gz"]
        D2["Download darwin-aarch64.tar.gz"]
        D3["Download linux-x86_64.tar.gz"]
        D4["Download linux-aarch64.tar.gz"]
    end
    
    COMPUTE["Compute SHA256 checksums<br/>for each artifact"]
    
    GENERATE["Generate stakpak.rb formula<br/>Platform-specific URLs<br/>Architecture detection"]
    
    COMMIT["Commit and push<br/>to homebrew-stakpak"]
    
    CHECKOUT --> D1
    CHECKOUT --> D2
    CHECKOUT --> D3
    CHECKOUT --> D4
    
    D1 --> COMPUTE
    D2 --> COMPUTE
    D3 --> COMPUTE
    D4 --> COMPUTE
    
    COMPUTE --> GENERATE
    GENERATE --> COMMIT
```

**Diagram: Homebrew Formula Update Process**

The generated `stakpak.rb` formula includes:

- Platform detection (`on_macos`, `on_linux`)
- Architecture detection (`Hardware::CPU.arm?`)
- Platform-specific download URLs
- SHA256 checksums for verification
- Installation instructions ([.github/workflows/build-and-release.yml:356-386]())

**Sources:** [.github/workflows/build-and-release.yml:329-392]()

---

## Testing and Quality Assurance

### Automated Testing

Each platform build includes a test execution step that runs the full test suite for the target platform:

```bash
cargo test --target ${{ matrix.target }}
```

Tests run after compilation but before artifact packaging, ensuring only passing builds are released ([.github/workflows/build-and-release.yml:92-93]()).

### Version Verification

The crates.io publishing job includes version verification logic:

1. **Extract Tag Version**: Parses version from `GITHUB_REF` (e.g., `refs/tags/v1.2.3` → `1.2.3`)
2. **Extract Cargo Version**: Reads version from root `Cargo.toml`
3. **Compare**: If mismatch detected, updates `Cargo.toml` to match tag version
4. **Log Warning**: Reports discrepancy in job logs ([.github/workflows/build-and-release.yml:148-165]())

This ensures consistency between git tags and published package versions.

### Rust Cache Optimization

Build jobs use `Swatinem/rust-cache@v2` with target-specific shared keys to optimize compilation times across workflow runs. The cache stores:

- Compiled dependencies
- Incremental compilation artifacts
- Target-specific build outputs

Cache keys are scoped per target (`shared-key: ${{ matrix.target }}`) to prevent cross-contamination between different architectures ([.github/workflows/build-and-release.yml:78-81]()).

**Sources:** [.github/workflows/build-and-release.yml:78-81](), [.github/workflows/build-and-release.yml:92-93](), [.github/workflows/build-and-release.yml:148-165]()

---

## Permissions and Security

The workflow requires specific GitHub token permissions:

| Permission | Level | Purpose |
|-----------|-------|---------|
| `contents` | `write` | Create releases, push tags |
| `discussions` | `write` | Generate release discussions |
| `pull-requests` | `read` | Read PR information for release notes |
| `packages` | `write` | Push Docker images to GHCR |

Secrets used:
- `CRATES_IO_TOKEN` - Authentication for crates.io publishing
- `HOMEBREW_TAP_GITHUB_TOKEN` - Authentication for homebrew-stakpak repository updates

**Sources:** [.github/workflows/build-and-release.yml:16-20]()

---

## Environment Configuration

The workflow defines global environment variables:

- `CARGO_TERM_COLOR: always` - Enables colored Cargo output in CI logs
- `BINARY_NAME: stakpak` - Defines the executable name used in artifact packaging

**Sources:** [.github/workflows/build-and-release.yml:22-24]()

---

# Page: Release Management

# Release Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/build-and-release.yml](.github/workflows/build-and-release.yml)
- [cliff.toml](cliff.toml)
- [libs/popup-widget/Cargo.toml](libs/popup-widget/Cargo.toml)
- [libs/popup-widget/README.md](libs/popup-widget/README.md)
- [release.sh](release.sh)

</details>



## Purpose and Scope

This document describes the release management system for Stakpak, including version bumping, git tagging, and the automated CI/CD pipeline that builds and distributes releases. The release process uses the `release.sh` script for version management and GitHub Actions workflows for building and publishing artifacts across multiple platforms and distribution channels.

For information about the CI/CD pipeline architecture and build matrix, see [CI/CD Pipeline](#7.1). For details on distribution channels and package publishing, see [Distribution Channels](#7.3).

## Release Process Overview

The release management system consists of a local release script and an automated CI/CD pipeline:

**Release Process Flow Diagram**

```mermaid
graph TB
    DEV["Developer"]
    
    subgraph "Local: release.sh"
        SCRIPT["release.sh"]
        VERSION_SELECT["Version Selection<br/>patch/minor/major/custom"]
        VERSION_BUMP["bump_version()<br/>update_cargo_version()"]
        CARGO_UPDATE["cargo update --workspace"]
        GIT_COMMIT["commit_and_push()<br/>chore: bump version to X.Y.Z"]
        GIT_TAG["create_and_push_tag()<br/>vX.Y.Z or vX.Y.Z-beta.N"]
    end
    
    subgraph "Remote: GitHub Actions"
        WORKFLOW_TRIGGER["build-and-release.yml<br/>on: tags: v*"]
        
        SETUP_JOB["setup job<br/>Detect beta/stable"]
        BUILD_JOB["build job<br/>Multi-platform matrix"]
        RELEASE_JOB["release job<br/>Create GitHub Release"]
        CRATES_JOB["publish_crates_io job"]
        DOCKER_JOB["docker job"]
        DOCKER_WARDEN_JOB["docker_warden job"]
        NOTES_JOB["update-release-notes job<br/>git-cliff"]
        HOMEBREW_JOB["homebrew job<br/>stable only"]
    end
    
    DEV --> SCRIPT
    SCRIPT --> VERSION_SELECT
    VERSION_SELECT --> VERSION_BUMP
    VERSION_BUMP --> CARGO_UPDATE
    CARGO_UPDATE --> GIT_COMMIT
    GIT_COMMIT --> GIT_TAG
    
    GIT_TAG --> WORKFLOW_TRIGGER
    WORKFLOW_TRIGGER --> SETUP_JOB
    SETUP_JOB --> BUILD_JOB
    BUILD_JOB --> RELEASE_JOB
    BUILD_JOB --> CRATES_JOB
    BUILD_JOB --> DOCKER_JOB
    DOCKER_JOB --> DOCKER_WARDEN_JOB
    RELEASE_JOB --> NOTES_JOB
    RELEASE_JOB --> HOMEBREW_JOB
```

Sources: [release.sh:1-325](), [.github/workflows/build-and-release.yml:1-393]()

## Version Bumping with release.sh

The `release.sh` script manages version updates across the workspace. It provides both interactive and command-line modes for version bumping.

### Script Usage

| Command | Description | Example Result |
|---------|-------------|----------------|
| `./release.sh patch` | Bump patch version | 0.1.100 → 0.1.101 |
| `./release.sh minor` | Bump minor version | 0.1.100 → 0.2.0 |
| `./release.sh major` | Bump major version | 0.1.100 → 1.0.0 |
| `./release.sh 1.2.3` | Set specific version | → 1.2.3 |
| `./release.sh` | Interactive mode | Prompts for choice |
| `./release.sh patch --beta` | Create beta release | 0.1.100 → 0.1.101-beta.1 |

Sources: [release.sh:29-46]()

### Version Update Process

**Version Management Data Flow**

```mermaid
graph TB
    CURRENT["get_current_version()<br/>Parse Cargo.toml"]
    
    BUMP_TYPE{"Bump Type?"}
    
    BUMP_FUNC["bump_version()<br/>Calculate new version"]
    CUSTOM["Custom version input<br/>validate_version()"]
    
    BETA_CHECK{"--beta flag?"}
    BETA_NUM["get_next_beta_number()<br/>Check git tags for latest"]
    BETA_SUFFIX["Append -beta.N"]
    
    UPDATE_CARGO["update_cargo_version()"]
    
    subgraph "Cargo.toml Updates"
        WS_VERSION["[workspace.package]<br/>version = X.Y.Z"]
        DEP_VERSIONS["[workspace.dependencies]<br/>stakai, stakpak-*, popup-widget<br/>version = X.Y.Z"]
    end
    
    CARGO_LOCK["cargo update --workspace<br/>Update Cargo.lock"]
    
    CURRENT --> BUMP_TYPE
    BUMP_TYPE -->|patch/minor/major| BUMP_FUNC
    BUMP_TYPE -->|custom| CUSTOM
    
    BUMP_FUNC --> BETA_CHECK
    CUSTOM --> BETA_CHECK
    
    BETA_CHECK -->|yes| BETA_NUM
    BETA_NUM --> BETA_SUFFIX
    BETA_SUFFIX --> UPDATE_CARGO
    
    BETA_CHECK -->|no| UPDATE_CARGO
    
    UPDATE_CARGO --> WS_VERSION
    UPDATE_CARGO --> DEP_VERSIONS
    WS_VERSION --> CARGO_LOCK
    DEP_VERSIONS --> CARGO_LOCK
```

Sources: [release.sh:48-122]()

The version update process consists of:

1. **Current Version Extraction**: Uses `grep` and `sed` to parse the version from [Cargo.toml:1-999]()
2. **Version Calculation**: The `bump_version()` function increments major/minor/patch components [release.sh:64-94]()
3. **Validation**: The `validate_version()` function ensures semantic version format (X.Y.Z or X.Y.Z-beta.N) [release.sh:53-62]()
4. **Workspace Updates**: The `update_cargo_version()` function updates:
   - Workspace package version in `[workspace.package]` section
   - Internal dependency versions for `stakai`, `stakpak-*`, and `popup-widget` packages
   - All uses `sed` with regex patterns to update both occurrences [release.sh:96-112]()
5. **Lock File Update**: Runs `cargo update --workspace` to synchronize `Cargo.lock` [release.sh:115-121]()

## Git Workflow and Tagging

After updating version files, the script commits changes and creates git tags.

### Commit and Tag Creation

**Git Operations Sequence**

```mermaid
sequenceDiagram
    participant Script as release.sh
    participant Git as Git Repository
    participant Remote as GitHub Remote
    
    Script->>Script: check_git_status()<br/>Verify clean/warn dirty
    
    Script->>Git: git add Cargo.toml Cargo.lock
    
    alt Uncommitted changes exist
        Script->>Git: git add .
    end
    
    Script->>Git: git commit -m "chore: bump version to X.Y.Z"
    Script->>Remote: git push origin <current_branch>
    
    Note over Script: Tag format: vX.Y.Z or vX.Y.Z-beta.N
    
    Script->>Git: git tag "vX.Y.Z"
    Script->>Remote: git push --tags
    
    Note over Remote: GitHub Actions triggered by tag push
```

Sources: [release.sh:124-173]()

The git workflow functions:

- **check_git_status()**: Verifies working directory state, warns about uncommitted changes, and requests confirmation [release.sh:124-138]()
- **commit_and_push()**: Stages version files (Cargo.toml, Cargo.lock), commits with standardized message format "chore: bump version to X.Y.Z", and pushes to current branch [release.sh:140-159]()
- **create_and_push_tag()**: Creates annotated tag with "v" prefix (e.g., `v0.1.101` or `v0.1.101-beta.1`) and pushes to remote [release.sh:161-173]()

### Beta Version Tracking

For beta releases, the `get_next_beta_number()` function queries existing git tags to determine the next beta number:

```bash
git tag -l "v${base_version}-beta.*" | sort -V | tail -1
```

This ensures sequential beta versioning (beta.1, beta.2, beta.3, etc.) for the same base version [release.sh:175-186]().

Sources: [release.sh:175-186]()

## CI/CD Pipeline Trigger and Setup

The GitHub Actions workflow is triggered by tag pushes and branch pushes with different behaviors.

### Workflow Triggers

**Trigger Configuration Table**

| Trigger Type | Pattern | Build | Release | Publish |
|--------------|---------|-------|---------|---------|
| Tag (stable) | `v1.2.3` | ✓ | ✓ | ✓ all channels |
| Tag (beta) | `v1.2.3-beta.1` | ✓ | ✓ prerelease | ✓ (no Homebrew) |
| Branch (main) | `main` | ✓ | ✗ | ✗ |
| Branch (beta) | `beta` | ✓ | ✗ | ✗ |

Sources: [.github/workflows/build-and-release.yml:3-14]()

The workflow configuration:

```yaml
on:
  push:
    branches: [main, beta]  # Build only
    tags: ["v*"]            # Full release
```

### Setup Job

The `setup` job runs first to determine release characteristics:

**Setup Job Logic**

```mermaid
graph TB
    TRIGGER["Workflow Triggered"]
    
    CHECK["setup job<br/>check step"]
    
    EXTRACT_TAG["Extract tag from GITHUB_REF<br/>TAG=$${GITHUB_REF#refs/tags/}"]
    EXTRACT_VERSION["Remove 'v' prefix<br/>VERSION=$${TAG#v}"]
    
    BETA_CHECK{"TAG contains<br/>'-beta'?"}
    
    OUTPUT_BETA_TRUE["is_beta=true"]
    OUTPUT_BETA_FALSE["is_beta=false"]
    OUTPUT_VERSION["version=X.Y.Z"]
    
    DOWNSTREAM["Other jobs use:<br/>needs.setup.outputs.is_beta<br/>needs.setup.outputs.version"]
    
    TRIGGER --> CHECK
    CHECK --> EXTRACT_TAG
    EXTRACT_TAG --> EXTRACT_VERSION
    EXTRACT_VERSION --> BETA_CHECK
    
    BETA_CHECK -->|yes| OUTPUT_BETA_TRUE
    BETA_CHECK -->|no| OUTPUT_BETA_FALSE
    
    OUTPUT_BETA_TRUE --> OUTPUT_VERSION
    OUTPUT_BETA_FALSE --> OUTPUT_VERSION
    OUTPUT_VERSION --> DOWNSTREAM
```

Sources: [.github/workflows/build-and-release.yml:27-45]()

The setup job outputs:
- `is_beta`: Boolean flag indicating beta/stable release
- `version`: Parsed version number without "v" prefix

These outputs are consumed by downstream jobs via `needs.setup.outputs.*` references.

## Build Matrix and Artifacts

The `build` job creates binaries for multiple platforms using a matrix strategy.

### Build Matrix Configuration

| OS | Target Triple | Architecture | Artifact Name |
|----|---------------|--------------|---------------|
| ubuntu-22.04 | x86_64-unknown-linux-musl | x86_64 Linux | stakpak-linux-x86_64 |
| ubuntu-22.04-arm | aarch64-unknown-linux-musl | ARM64 Linux | stakpak-linux-aarch64 |
| macos-15 | x86_64-apple-darwin | x86_64 macOS | stakpak-darwin-x86_64 |
| macos-15 | aarch64-apple-darwin | ARM64 macOS | stakpak-darwin-aarch64 |
| windows-2022 | x86_64-pc-windows-msvc | x86_64 Windows | stakpak-windows-x86_64 |

Sources: [.github/workflows/build-and-release.yml:48-66]()

### Build Process Steps

**Build Job Workflow**

```mermaid
graph TB
    CHECKOUT["actions/checkout@v4"]
    
    RUST_INSTALL["Install Rust 1.89.0<br/>dtolnay/rust-toolchain"]
    RUST_TARGET["Add target:<br/>${{ matrix.target }}"]
    
    CACHE["Swatinem/rust-cache@v2<br/>key: ${{ matrix.target }}"]
    
    MUSL_CHECK{"Linux MUSL target?"}
    MUSL_INSTALL["apt-get install musl-tools"]
    
    BUILD["cargo build --release<br/>--target ${{ matrix.target }}"]
    TEST["cargo test<br/>--target ${{ matrix.target }}"]
    
    TAG_CHECK{"Tag push?<br/>startsWith(github.ref, 'refs/tags/')"}
    
    PREPARE["Prepare binary"]
    
    WINDOWS_CHECK{"Windows?"}
    ZIP["7z a artifact.zip stakpak.exe"]
    TARGZ["tar czf artifact.tar.gz stakpak"]
    
    UPLOAD["actions/upload-artifact@v4<br/>retention-days: 1"]
    
    CHECKOUT --> RUST_INSTALL
    RUST_INSTALL --> RUST_TARGET
    RUST_TARGET --> CACHE
    CACHE --> MUSL_CHECK
    
    MUSL_CHECK -->|yes| MUSL_INSTALL
    MUSL_CHECK -->|no| BUILD
    MUSL_INSTALL --> BUILD
    
    BUILD --> TEST
    TEST --> TAG_CHECK
    
    TAG_CHECK -->|yes| PREPARE
    TAG_CHECK -->|no| END["End"]
    
    PREPARE --> WINDOWS_CHECK
    WINDOWS_CHECK -->|yes| ZIP
    WINDOWS_CHECK -->|no| TARGZ
    
    ZIP --> UPLOAD
    TARGZ --> UPLOAD
```

Sources: [.github/workflows/build-and-release.yml:70-112]()

Key build features:
- Uses `RUSTFLAGS` for static linking on Linux GNU targets [.github/workflows/build-and-release.yml:90]()
- Linux MUSL targets require `musl-tools` package [.github/workflows/build-and-release.yml:83-85]()
- Windows artifacts use `.zip`, others use `.tar.gz` [.github/workflows/build-and-release.yml:96-104]()
- Artifacts retained for 1 day before release job processes them [.github/workflows/build-and-release.yml:112]()

## Release Creation and Publishing

After successful builds, multiple jobs handle release creation and distribution.

### Release Job

The `release` job creates the GitHub release with all platform artifacts:

**Release Creation Process**

```mermaid
graph TB
    BUILD_COMPLETE["build job complete"]
    
    TAG_GUARD{"Tag push?"}
    
    DOWNLOAD["actions/download-artifact@v4<br/>Download all artifacts"]
    
    CREATE_RELEASE["softprops/action-gh-release@v1"]
    
    FILES["Attach files:<br/>stakpak-linux-x86_64.tar.gz<br/>stakpak-linux-aarch64.tar.gz<br/>stakpak-darwin-x86_64.tar.gz<br/>stakpak-darwin-aarch64.tar.gz<br/>stakpak-windows-x86_64.zip"]
    
    BETA_FLAG{"is_beta == true?"}
    PRERELEASE["prerelease: true"]
    STABLE["prerelease: false"]
    
    AUTO_NOTES["generate_release_notes: true"]
    
    BUILD_COMPLETE --> TAG_GUARD
    TAG_GUARD -->|yes| DOWNLOAD
    TAG_GUARD -->|no| END["Skip"]
    
    DOWNLOAD --> CREATE_RELEASE
    CREATE_RELEASE --> FILES
    FILES --> BETA_FLAG
    
    BETA_FLAG -->|yes| PRERELEASE
    BETA_FLAG -->|no| STABLE
    
    PRERELEASE --> AUTO_NOTES
    STABLE --> AUTO_NOTES
```

Sources: [.github/workflows/build-and-release.yml:114-136]()

The release job:
- Downloads all artifacts from the build job [.github/workflows/build-and-release.yml:120-121]()
- Creates GitHub release using `softprops/action-gh-release` [.github/workflows/build-and-release.yml:124]()
- Marks as prerelease if `is_beta == 'true'` [.github/workflows/build-and-release.yml:133]()
- Generates release notes automatically from commits [.github/workflows/build-and-release.yml:134]()

### Crates.io Publishing

The `publish_crates_io` job publishes all workspace packages to crates.io in dependency order:

**Crates.io Publishing Sequence**

```mermaid
graph LR
    STAKAI["stakai"]
    SHARED["stakpak-shared"]
    API["stakpak-api"]
    POPUP["stakpak-popup-widget"]
    MCP_CLIENT["stakpak-mcp-client"]
    MCP_SERVER["stakpak-mcp-server"]
    MCP_PROXY["stakpak-mcp-proxy"]
    TUI["stakpak-tui"]
    CLI["stakpak"]
    
    STAKAI --> SHARED
    SHARED --> API
    SHARED --> POPUP
    SHARED --> MCP_CLIENT
    SHARED --> MCP_SERVER
    SHARED --> MCP_PROXY
    API --> TUI
    POPUP --> TUI
    MCP_CLIENT --> TUI
    TUI --> CLI
    MCP_SERVER --> CLI
    MCP_PROXY --> CLI
```

Sources: [.github/workflows/build-and-release.yml:202-213]()

The publishing process:
1. **Version Verification**: Checks that tag version matches `Cargo.toml`, updates if needed [.github/workflows/build-and-release.yml:148-165]()
2. **Sequential Publishing**: Uses `publish_package()` function that:
   - Runs `cargo publish -p <package> --no-verify` [.github/workflows/build-and-release.yml:185]()
   - Checks for "already uploaded" error and skips if present [.github/workflows/build-and-release.yml:193-194]()
   - Waits 15 seconds between packages for index propagation [.github/workflows/build-and-release.yml:191-192]()
3. **Dependency Order**: Publishes in strict order to ensure dependencies are available [.github/workflows/build-and-release.yml:202-213]()

Sources: [.github/workflows/build-and-release.yml:138-217]()

## Beta Releases

Beta releases follow a modified workflow with specific constraints.

### Beta Release Characteristics

| Feature | Stable Release | Beta Release |
|---------|----------------|--------------|
| Tag Format | `v1.2.3` | `v1.2.3-beta.1` |
| GitHub Release | Normal release | Marked as prerelease |
| Crates.io | Published | Published |
| Docker Images | `:latest` + `:vX.Y.Z` | `:vX.Y.Z-beta.N` only |
| Homebrew | Updated | **Skipped** |

Sources: [.github/workflows/build-and-release.yml:133](), [.github/workflows/build-and-release.yml:244](), [.github/workflows/build-and-release.yml:272](), [.github/workflows/build-and-release.yml:332]()

### Creating Beta Releases

To create a beta release:

```bash
# Interactive beta release
./release.sh --beta

# Automatic patch beta release
./release.sh patch --beta

# Specific version beta release
./release.sh 1.2.3 --beta
```

The script automatically:
1. Queries existing beta tags for the base version
2. Increments the beta number (e.g., beta.1 → beta.2)
3. Creates tag like `v1.2.3-beta.2`

Sources: [release.sh:40-45](), [release.sh:274-278]()

### Beta Release Conditional Logic

**Docker Image Tagging for Beta vs Stable**

```yaml
tags: |
  ghcr.io/${{ github.repository }}:v${{ needs.setup.outputs.version }}
  ${{ needs.setup.outputs.is_beta != 'true' && format('ghcr.io/{0}:latest', github.repository) || '' }}
```

This expression conditionally adds the `:latest` tag only for stable releases [.github/workflows/build-and-release.yml:242-244]().

The Homebrew job uses a conditional to skip beta releases entirely:

```yaml
if: startsWith(github.ref, 'refs/tags/') && needs.setup.outputs.is_beta == 'false'
```

Sources: [.github/workflows/build-and-release.yml:332]()

## Release Notes Generation

Release notes are generated using `git-cliff` with conventional commit parsing.

### Release Notes Workflow

**Release Notes Update Process**

```mermaid
graph TB
    RELEASE_COMPLETE["release job complete"]
    
    CHECKOUT["actions/checkout@v4<br/>fetch-depth: 0"]
    
    INSTALL["cargo install git-cliff"]
    
    EXTRACT_VERSION["VERSION=$${GITHUB_REF#refs/tags/}"]
    
    PREV_TAG["git describe --tags --abbrev=0<br/>$VERSION^"]
    
    PREV_CHECK{"Previous tag<br/>exists?"}
    
    CLIFF["git-cliff $PREV_TAG..$VERSION<br/>--strip all > release_notes.md"]
    
    EMPTY_CHECK{"Release notes<br/>empty?"}
    
    UPDATE_RELEASE["gh release edit $VERSION<br/>--notes-file release_notes.md"]
    
    RELEASE_COMPLETE --> CHECKOUT
    CHECKOUT --> INSTALL
    INSTALL --> EXTRACT_VERSION
    EXTRACT_VERSION --> PREV_TAG
    PREV_TAG --> PREV_CHECK
    
    PREV_CHECK -->|no| SKIP["Skip: No previous tag"]
    PREV_CHECK -->|yes| CLIFF
    
    CLIFF --> EMPTY_CHECK
    EMPTY_CHECK -->|yes| SKIP2["Skip: No commits"]
    EMPTY_CHECK -->|no| UPDATE_RELEASE
```

Sources: [.github/workflows/build-and-release.yml:274-327]()

### Git-Cliff Configuration

The `cliff.toml` configuration defines commit parsing rules:

**Commit Group Mappings**

| Commit Prefix | Group | Included in Notes |
|---------------|-------|-------------------|
| `feat` | Features | ✓ |
| `fix` | Bug Fixes | ✓ |
| `docs` | Documentation | ✓ |
| `perf` | Performance | ✓ |
| `refactor` | Refactoring | ✓ |
| `style` | Code Style | ✓ |
| `test` | Testing | ✓ |
| `chore`, `ci` | Maintenance | ✓ |
| `chore(release)` | - | ✗ Skipped |
| `chore(deps*)` | - | ✗ Skipped |
| `revert` | Reverts | ✓ |
| Body contains "security" | Security | ✓ |

Sources: [cliff.toml:31-46]()

The changelog template groups commits by category and links to pull requests:

```
## X.Y.Z
Released on YYYY-MM-DD.

### FEATURES
- Commit message (#123)

### BUG FIXES
- Commit message (#456)
```

Sources: [cliff.toml:8-23]()

## Docker Image Publishing

Two Docker images are built and published to GitHub Container Registry:

### Main Docker Image

The `docker` job builds the standard Stakpak image:

- **Context**: Root directory (`.`)
- **Platform**: `linux/amd64` only
- **Tags**: 
  - `ghcr.io/stakpak/agent:vX.Y.Z` (always)
  - `ghcr.io/stakpak/agent:latest` (stable only)

Sources: [.github/workflows/build-and-release.yml:219-244]()

### Warden Docker Image

The `docker_warden` job builds the security-focused Warden variant:

- **Context**: `.warden` directory
- **Base Image**: Uses main image as base via `BASE_IMAGE_TAG` build arg
- **Tags**: 
  - `ghcr.io/stakpak/agent-warden:vX.Y.Z` (always)
  - `ghcr.io/stakpak/agent-warden:latest` (stable only)

Sources: [.github/workflows/build-and-release.yml:246-272]()

The Warden job depends on the `docker` job completion to ensure the base image exists [.github/workflows/build-and-release.yml:247]().

## Homebrew Formula Updates

The `homebrew` job automatically updates the Homebrew tap for stable releases only.

**Homebrew Update Process**

```mermaid
graph TB
    RELEASE_COMPLETE["release job complete"]
    
    STABLE_CHECK{"Stable release?<br/>is_beta == false"}
    
    CHECKOUT["Checkout homebrew-stakpak<br/>stakpak/homebrew-stakpak"]
    
    DOWNLOAD["Download release artifacts:<br/>stakpak-darwin-x86_64.tar.gz<br/>stakpak-darwin-aarch64.tar.gz<br/>stakpak-linux-x86_64.tar.gz<br/>stakpak-linux-aarch64.tar.gz"]
    
    SHA256["Calculate SHA256 checksums<br/>for all platforms"]
    
    GENERATE["Generate stakpak.rb<br/>Ruby formula file"]
    
    subgraph "Formula Structure"
        HEADER["class Stakpak < Formula"]
        META["desc, homepage, version"]
        MACOS["on_macos: ARM vs x86_64<br/>url + sha256"]
        LINUX["on_linux: ARM vs x86_64<br/>url + sha256"]
        INSTALL["def install: bin.install"]
    end
    
    COMMIT["git commit -m<br/>'Update stakpak to vX.Y.Z'"]
    PUSH["git push"]
    
    RELEASE_COMPLETE --> STABLE_CHECK
    STABLE_CHECK -->|yes| CHECKOUT
    STABLE_CHECK -->|no| SKIP["Skip"]
    
    CHECKOUT --> DOWNLOAD
    DOWNLOAD --> SHA256
    SHA256 --> GENERATE
    
    GENERATE --> HEADER
    HEADER --> META
    META --> MACOS
    META --> LINUX
    MACOS --> INSTALL
    LINUX --> INSTALL
    
    INSTALL --> COMMIT
    COMMIT --> PUSH
```

Sources: [.github/workflows/build-and-release.yml:329-392]()

The formula generation:
1. Downloads all release artifacts from GitHub [.github/workflows/build-and-release.yml:346-349]()
2. Calculates SHA256 checksums for integrity verification [.github/workflows/build-and-release.yml:351-354]()
3. Generates `stakpak.rb` with platform-specific URLs and checksums [.github/workflows/build-and-release.yml:356-386]()
4. Commits and pushes to `stakpak/homebrew-stakpak` repository [.github/workflows/build-and-release.yml:388-392]()

The job requires a separate `HOMEBREW_TAP_GITHUB_TOKEN` secret for repository access [.github/workflows/build-and-release.yml:338]().

Sources: [.github/workflows/build-and-release.yml:329-392]()

---

# Page: Distribution Channels

# Distribution Channels

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/build-and-release.yml](.github/workflows/build-and-release.yml)
- [README.md](README.md)
- [assets/stakpak-dark.png](assets/stakpak-dark.png)
- [assets/stakpak-light.png](assets/stakpak-light.png)
- [cliff.toml](cliff.toml)
- [libs/popup-widget/Cargo.toml](libs/popup-widget/Cargo.toml)
- [libs/popup-widget/README.md](libs/popup-widget/README.md)
- [release.sh](release.sh)

</details>



This document describes the three primary distribution channels for Stakpak: crates.io registry publishing, Docker image builds, and Homebrew formula updates. These channels are automated through GitHub Actions and triggered by git tags. For information about the release workflow that creates these tags, see [Release Management](#7.2). For the broader CI/CD pipeline, see [CI/CD Pipeline](#7.1).

---

## Overview

Stakpak is distributed through three channels, each serving different use cases:

| Channel | Use Case | Trigger | Platforms |
|---------|----------|---------|-----------|
| **crates.io** | Rust developers, source builds | Git tags (`v*`) | Platform-agnostic |
| **Docker** | Containerized deployments | Git tags (`v*`) | linux/amd64 |
| **Homebrew** | macOS/Linux users | Git tags (`v*`, stable only) | darwin/linux x86_64/aarch64 |

All distribution channels are managed by the `build-and-release.yml` GitHub Actions workflow and execute only when a version tag (e.g., `v0.1.100` or `v0.1.101-beta.1`) is pushed.

**Sources:** [.github/workflows/build-and-release.yml:1-393]()

---

## Distribution Workflow Sequence

```mermaid
graph TB
    subgraph "Trigger"
        TAG["Git Tag Pushed<br/>(v1.2.3 or v1.2.3-beta.1)"]
    end
    
    subgraph "Setup Phase"
        SETUP["setup job<br/>Determines is_beta and version"]
    end
    
    subgraph "Build Phase"
        BUILD["build job<br/>Multi-platform binaries"]
    end
    
    subgraph "Release Creation"
        RELEASE["release job<br/>Creates GitHub Release<br/>with artifacts"]
    end
    
    subgraph "Distribution Channels"
        CRATES["publish_crates_io<br/>Publishes workspace to crates.io"]
        DOCKER_MAIN["docker<br/>ghcr.io/stakpak/agent"]
        DOCKER_WARDEN["docker_warden<br/>ghcr.io/stakpak/agent-warden"]
        HOMEBREW["homebrew<br/>stakpak/homebrew-stakpak tap"]
    end
    
    subgraph "Post-Processing"
        NOTES["update-release-notes<br/>git-cliff changelog generation"]
    end
    
    TAG --> SETUP
    SETUP --> BUILD
    BUILD --> RELEASE
    
    RELEASE --> CRATES
    RELEASE --> DOCKER_MAIN
    DOCKER_MAIN --> DOCKER_WARDEN
    RELEASE --> NOTES
    
    NOTES --> HOMEBREW
    
    style CRATES fill:#f9f9f9
    style DOCKER_MAIN fill:#f9f9f9
    style DOCKER_WARDEN fill:#f9f9f9
    style HOMEBREW fill:#f9f9f9
```

**Diagram: Complete Distribution Pipeline Flow**

This diagram shows the progression from tag creation through all distribution channels. The `setup` job determines whether the release is beta, which affects which channels are used. Beta releases skip Homebrew updates.

**Sources:** [.github/workflows/build-and-release.yml:27-392]()

---

## Crates.io Publishing

### Workspace Publishing Order

Stakpak uses a Cargo workspace with multiple crates that have interdependencies. Publishing must occur in dependency order to ensure each crate's dependencies are available on crates.io before it is published.

```mermaid
graph LR
    subgraph "Independent Crates"
        STAKAI["stakai"]
        SHARED["stakpak-shared"]
        POPUP["stakpak-popup-widget"]
    end
    
    subgraph "API Layer"
        API["stakpak-api"]
    end
    
    subgraph "MCP Components"
        MCPC["stakpak-mcp-client"]
        MCPS["stakpak-mcp-server"]
        MCPP["stakpak-mcp-proxy"]
    end
    
    subgraph "User-Facing Crates"
        TUI["stakpak-tui"]
        CLI["stakpak<br/>(main CLI crate)"]
    end
    
    STAKAI --> API
    SHARED --> API
    SHARED --> MCPC
    SHARED --> MCPS
    SHARED --> MCPP
    
    API --> TUI
    POPUP --> TUI
    
    MCPC --> CLI
    MCPS --> CLI
    MCPP --> CLI
    TUI --> CLI
```

**Diagram: Crate Dependency Graph and Publishing Order**

Publishing proceeds from left to right. Independent crates are published first, followed by crates that depend on them. The main `stakpak` CLI crate is published last.

**Sources:** [.github/workflows/build-and-release.yml:172-216]()

### Publishing Process

The `publish_crates_io` job handles crate publishing with the following features:

1. **Version Verification**: Extracts version from git tag and verifies it matches `Cargo.toml`:

```
VERSION=${GITHUB_REF#refs/tags/}
VERSION=${VERSION#v}
CARGO_VERSION=$(grep -m1 '^version = ' Cargo.toml | sed 's/version = "\(.*\)"/\1/')
if [ "$VERSION" != "$CARGO_VERSION" ]; then
  sed -i "s/^version = \".*\"/version = \"$VERSION\"/" Cargo.toml
fi
```

2. **Ordered Publishing**: Publishes crates using the `publish_package()` function:

| Order | Package | Notes |
|-------|---------|-------|
| 1 | `stakai` | AI/LLM library, no internal deps |
| 2 | `stakpak-shared` | Common types, no internal deps |
| 3 | `stakpak-api` | Depends on stakai, shared |
| 4 | `stakpak-popup-widget` | Independent TUI widget |
| 5 | `stakpak-mcp-client` | Depends on shared |
| 6 | `stakpak-mcp-server` | Depends on shared |
| 7 | `stakpak-mcp-proxy` | Depends on shared |
| 8 | `stakpak-tui` | Depends on API, popup-widget |
| 9 | `stakpak` | Main CLI, depends on all |

3. **Error Handling**: Skips already-published versions instead of failing:

```bash
if echo "$OUTPUT" | grep -q "already uploaded"; then
  echo "$pkg version $VERSION already published, skipping"
else
  echo "Error publishing $pkg:"
  exit 1
fi
```

4. **Index Propagation**: Waits 15 seconds between publishes to allow crates.io index to update.

**Sources:** [.github/workflows/build-and-release.yml:138-218]()

### Authentication

Publishing uses the `CRATES_IO_TOKEN` secret, which must be configured in the repository settings. The token is passed to `cargo login` before publishing begins.

**Sources:** [.github/workflows/build-and-release.yml:167-170]()

---

## Docker Images

Stakpak provides two Docker images, both published to GitHub Container Registry (ghcr.io):

### Main Image: ghcr.io/stakpak/agent

The main image is built from the repository root and includes popular DevOps CLI tools:

```mermaid
graph TB
    subgraph "Build Context"
        DOCKERFILE["Dockerfile<br/>(root)"]
        BINARY["Stakpak Binary<br/>(from release artifacts)"]
    end
    
    subgraph "Image Contents"
        TOOLS["DevOps Tools<br/>docker, kubectl, aws cli,<br/>gcloud, azure cli, etc."]
        STAKPAK_BIN["stakpak binary<br/>/usr/local/bin/stakpak"]
    end
    
    subgraph "Published Tags"
        VERSION_TAG["ghcr.io/stakpak/agent:v1.2.3"]
        LATEST_TAG["ghcr.io/stakpak/agent:latest<br/>(stable releases only)"]
    end
    
    DOCKERFILE --> TOOLS
    BINARY --> STAKPAK_BIN
    
    TOOLS --> VERSION_TAG
    STAKPAK_BIN --> VERSION_TAG
    
    VERSION_TAG --> LATEST_TAG
```

**Diagram: Main Docker Image Build and Tagging**

The main image is designed for everyday DevOps tasks and includes commonly needed tools alongside the Stakpak binary.

**Sources:** [.github/workflows/build-and-release.yml:219-245](), [README.md:101-107]()

### Warden Image: ghcr.io/stakpak/agent-warden

The Warden image extends the main image with network-level security policies:

```mermaid
graph TB
    subgraph "Base"
        BASE["ghcr.io/stakpak/agent:v1.2.3<br/>(main image)"]
    end
    
    subgraph "Warden Context"
        WARDEN_DOCKERFILE[".warden/Dockerfile"]
        POLICIES["Network Policies<br/>Destructive operation blocking"]
    end
    
    subgraph "Build Args"
        BASE_TAG["BASE_IMAGE_TAG=v1.2.3"]
    end
    
    subgraph "Published Tags"
        WARDEN_VERSION["ghcr.io/stakpak/agent-warden:v1.2.3"]
        WARDEN_LATEST["ghcr.io/stakpak/agent-warden:latest<br/>(stable releases only)"]
    end
    
    BASE --> WARDEN_DOCKERFILE
    BASE_TAG --> WARDEN_DOCKERFILE
    POLICIES --> WARDEN_DOCKERFILE
    
    WARDEN_DOCKERFILE --> WARDEN_VERSION
    WARDEN_VERSION --> WARDEN_LATEST
```

**Diagram: Warden Docker Image Build Chain**

The Warden image depends on the main image being built first, as it uses it as a base. This is enforced by job dependencies in the workflow.

**Sources:** [.github/workflows/build-and-release.yml:246-273]()

### Docker Build Configuration

Both Docker jobs use:

- **Platform**: `linux/amd64` only
- **Registry**: GitHub Container Registry (`ghcr.io`)
- **Authentication**: `GITHUB_TOKEN` (automatically provided)
- **Push condition**: Only on git tags (skips branch pushes)

Tagging strategy:

```yaml
tags: |
  ghcr.io/${{ github.repository }}:v${{ needs.setup.outputs.version }}
  ${{ needs.setup.outputs.is_beta != 'true' && format('ghcr.io/{0}:latest', github.repository) || '' }}
```

The `latest` tag is only applied to stable releases. Beta releases receive only version-specific tags.

**Sources:** [.github/workflows/build-and-release.yml:236-244](), [.github/workflows/build-and-release.yml:268-272]()

---

## Homebrew Formula

Homebrew provides package management for macOS and Linux. Stakpak maintains a tap (custom repository) at `stakpak/homebrew-stakpak`.

### Formula Generation Process

The `homebrew` job performs the following steps:

1. **Artifact Download**: Downloads pre-built binaries for all supported platforms:

| Platform | Artifact Name |
|----------|---------------|
| macOS x86_64 | `stakpak-darwin-x86_64.tar.gz` |
| macOS ARM64 | `stakpak-darwin-aarch64.tar.gz` |
| Linux x86_64 | `stakpak-linux-x86_64.tar.gz` |
| Linux ARM64 | `stakpak-linux-aarch64.tar.gz` |

2. **Checksum Generation**: Computes SHA256 checksums for each artifact

3. **Formula Creation**: Generates a Ruby formula file (`stakpak.rb`)

4. **Git Push**: Commits and pushes the formula to the tap repository

**Sources:** [.github/workflows/build-and-release.yml:329-392]()

### Formula Structure

The generated formula uses Homebrew's platform detection to provide the correct binary:

```mermaid
graph TB
    subgraph "Formula Logic"
        FORMULA["stakpak.rb"]
    end
    
    subgraph "Platform Detection"
        MACOS{"on_macos"}
        LINUX{"on_linux"}
        ARM{"Hardware::CPU.arm?"}
    end
    
    subgraph "Downloads"
        DARWIN_X64["darwin x86_64<br/>sha256: ..."]
        DARWIN_ARM["darwin aarch64<br/>sha256: ..."]
        LINUX_X64["linux x86_64<br/>sha256: ..."]
        LINUX_ARM["linux aarch64<br/>sha256: ..."]
    end
    
    FORMULA --> MACOS
    FORMULA --> LINUX
    
    MACOS --> ARM
    ARM -->|yes| DARWIN_ARM
    ARM -->|no| DARWIN_X64
    
    LINUX --> ARM
    ARM -->|yes| LINUX_ARM
    ARM -->|no| LINUX_X64
```

**Diagram: Homebrew Formula Platform Selection**

The formula dynamically selects the appropriate binary based on the user's operating system and CPU architecture.

**Sources:** [.github/workflows/build-and-release.yml:356-386]()

### Formula Template

The workflow generates the formula using a shell HERE document:

```ruby
class Stakpak < Formula
  desc "Stakpak CLI tool"
  homepage "https://github.com/stakpak/stakpak"
  version "${VERSION}"
  
  on_macos do
    if Hardware::CPU.arm?
      url "https://github.com/stakpak/agent/releases/download/v${VERSION}/stakpak-darwin-aarch64.tar.gz"
      sha256 "${SHA256_DARWIN_ARM}"
    else
      url "https://github.com/stakpak/agent/releases/download/v${VERSION}/stakpak-darwin-x86_64.tar.gz"
      sha256 "${SHA256_DARWIN_X64}"
    end
  end
  
  on_linux do
    if Hardware::CPU.arm?
      url "https://github.com/stakpak/agent/releases/download/v${VERSION}/stakpak-linux-aarch64.tar.gz"
      sha256 "${SHA256_LINUX_ARM}"
    else
      url "https://github.com/stakpak/agent/releases/download/v${VERSION}/stakpak-linux-x86_64.tar.gz"
      sha256 "${SHA256_LINUX_X64}"
    end
  end
  
  def install
    bin.install "stakpak"
  end
end
```

The variables `${VERSION}`, `${SHA256_*}` are substituted during the workflow execution.

**Sources:** [.github/workflows/build-and-release.yml:356-386]()

### Beta Release Handling

The Homebrew job includes a condition that prevents it from running for beta releases:

```yaml
if: startsWith(github.ref, 'refs/tags/') && needs.setup.outputs.is_beta == 'false'
```

Beta releases are distributed only through:
- GitHub Releases (binary downloads)
- Docker images (version-tagged, no `latest` tag)

This ensures the Homebrew tap only contains stable releases.

**Sources:** [.github/workflows/build-and-release.yml:332]()

### Authentication

The Homebrew job uses a separate token (`HOMEBREW_TAP_GITHUB_TOKEN`) with write access to the tap repository. This is necessary because the workflow needs to push to a different repository than the main agent repository.

**Sources:** [.github/workflows/build-and-release.yml:338]()

---

## Distribution Channel Comparison

| Feature | crates.io | Docker | Homebrew |
|---------|-----------|--------|----------|
| **Update Method** | `cargo install` | `docker pull` | `brew upgrade` |
| **Build From Source** | Yes | No (pre-built) | No (pre-built) |
| **Platform Support** | All Rust platforms | linux/amd64 | macOS/Linux x64/arm64 |
| **Beta Support** | Yes | Yes (tagged) | No |
| **Latest Tag** | N/A | Stable only | Always latest stable |
| **Prerequisites** | Rust toolchain | Docker | Homebrew |
| **Size** | Compile-time | ~200MB (with tools) | Binary only (~50MB) |

**Sources:** [.github/workflows/build-and-release.yml:1-393](), [README.md:77-95]()

---

## Distribution Triggers and Conditions

All distribution jobs share common trigger conditions defined at the workflow level:

```yaml
on:
  push:
    branches: [main, beta]  # Build only, no distribution
    tags: ["v*"]            # Full distribution workflow
```

The `setup` job determines release characteristics:

```yaml
outputs:
  is_beta: ${{ steps.check.outputs.is_beta }}
  version: ${{ steps.check.outputs.version }}
```

These outputs control:
- Whether `latest` tags are applied (stable only)
- Whether Homebrew updates occur (stable only)
- Release notes generation

**Sources:** [.github/workflows/build-and-release.yml:4-45]()

---

## Installation Instructions Reference

Each distribution channel has corresponding installation instructions in the README:

| Channel | Command | Documentation |
|---------|---------|---------------|
| Homebrew | `brew install stakpak/stakpak/stakpak` | [README.md:83-95]() |
| Binary | Manual download from GitHub Releases | [README.md:97-99]() |
| Docker | `docker pull ghcr.io/stakpak/agent:latest` | [README.md:101-107]() |
| crates.io | `cargo install stakpak` | Referenced in docs |

**Sources:** [README.md:77-107]()