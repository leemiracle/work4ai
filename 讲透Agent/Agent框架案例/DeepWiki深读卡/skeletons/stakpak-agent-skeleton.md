# Skeleton: stakpak-agent（36 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 15KB | 5 | ~9 | 7 |
| 2 | System Architecture | L407 | 12KB | 4 | ~3 | 12 |
| 3 | Workspace Structure and Packages | L731 | 12KB | 3 | ~8 | 4 |
| 4 | Installation and Getting Started | L1114 | 16KB | 4 | ~12 | 8 |
| 5 | CLI Interface | L1564 | 16KB | 7 | ~6 | 8 |
| 6 | Main Entry Point and Configuration | L1946 | 19KB | 7 | ~19 | 5 |
| 7 | Agent Execution Modes | L2586 | 20KB | 10 | ~19 | 5 |
| 8 | Context Injection Pipeline | L3219 | 15KB | 6 | ~4 | 5 |
| 9 | Session and Profile Management | L3669 | 20KB | 15 | ~12 | 8 |
| 10 | Terminal User Interface (TUI) | L4255 | 16KB | 5 | ~13 | 7 |
| 11 | Core Architecture and Event Loop | L4676 | 9KB | 5 | ~2 | 4 |
| 12 | State Management | L4963 | 22KB | 5 | ~32 | 4 |
| 13 | Event Handling and User Input | L5494 | 24KB | 8 | ~4 | 9 |
| 14 | Rendering System | L6202 | 20KB | 9 | ~14 | 9 |
| 15 | Message System and Display | L6788 | 23KB | 12 | ~18 | 5 |
| 16 | Interactive Components | L7563 | 53KB | 21 | ~32 | 6 |
| 17 | Shell Mode Integration | L9038 | 17KB | 4 | ~7 | 9 |
| 18 | Agent Provider and API | L9583 | 25KB | 8 | ~13 | 8 |
| 19 | AgentProvider Trait | L10336 | 17KB | 7 | ~21 | 4 |
| 20 | Remote Client Implementation | L10813 | 17KB | 10 | ~15 | 7 |
| 21 | Local Client Implementation | L11359 | 23KB | 9 | ~15 | 4 |
| 22 | Data Models and Types | L12123 | 21KB | 8 | ~23 | 0 |
| 23 | MCP (Model Context Protocol) System | L12811 | 17KB | 9 | ~6 | 18 |
| 24 | MCP Architecture | L13283 | 14KB | 6 | ~5 | 7 |
| 25 | Tool Container and Execution Flow | L13752 | 14KB | 7 | ~7 | 6 |
| 26 | Local Tools Implementation | L14173 | 18KB | 11 | ~7 | 6 |
| 27 | Task Management System | L14733 | 20KB | 8 | ~21 | 6 |
| 28 | Remote Operations and SSH | L15375 | 12KB | 9 | ~8 | 6 |
| 29 | Security and Privacy | L15668 | 17KB | 6 | ~6 | 13 |
| 30 | Secret Substitution System | L16088 | 20KB | 8 | ~6 | 10 |
| 31 | Warden Guardrails | L16723 | 11KB | 6 | ~5 | 8 |
| 32 | Privacy Mode and Data Redaction | L17058 | 15KB | 4 | ~7 | 7 |
| 33 | Build System and Deployment | L17560 | 26KB | 8 | ~16 | 8 |
| 34 | CI/CD Pipeline | L18254 | 14KB | 5 | ~7 | 5 |
| 35 | Release Management | L18648 | 21KB | 9 | ~14 | 5 |
| 36 | Distribution Channels | L19328 | 14KB | 5 | ~12 | 8 |


## · Overview  (L6)
  源文件: Cargo.lock, Cargo.toml, README.md, assets/stakpak-dark.png, assets/stakpak-light.png, cli/Cargo.toml, tui/Cargo.toml
  Purpose and Scope
  System Architecture
    · Workspace Structure and Dependencies
    · Runtime Architecture: CLI to TUI Communication
    · AgentProvider Architecture
  Core Components
    · Command Line Interface (CLI)
    · Terminal User Interface (TUI)
    · Model Context Protocol (MCP) System
    · API Client and Shared Libraries
  Key Features
    · Security Architecture
    · Tool Execution System
    · Configuration and Context Injection
    · Session Management
  Installation and Basic Usage
    · Installation Methods
    · Authentication and Configuration
    · Execution Modes

## · System Architecture  (L407)
  源文件: Cargo.lock, Cargo.toml, README.md, assets/stakpak-dark.png, assets/stakpak-light.png, cli/Cargo.toml, cli/src/commands/agent/run/helpers.rs, cli/src/commands/agent/run/mode_async.rs, cli/src/commands/agent/run/mode_interactive.rs, cli/src/commands/mod.rs, cli/src/main.rs, tui/Cargo.toml
  Workspace Structure and Crate Dependencies
  Core Components and Runtime Architecture
  Execution Flow with Code References
  Deployment and Distribution Architecture

## · Workspace Structure and Packages  (L731)
  源文件: Cargo.lock, Cargo.toml, cli/Cargo.toml, tui/Cargo.toml
  Purpose and Scope
  Workspace Organization
  Package Catalog
  Inter-Crate Dependencies
    · Dependency Graph
    · Primary Dependencies by Package
  Shared Dependencies
    · Key Shared Dependencies
    · RMCP Feature Configuration
  Version Management
    · Workspace-Level Versioning
    · Metadata Sharing
  Build Configuration
    · Linting Rules
    · Resolver Version
  Special Dependencies
    · CLI-Specific Dependencies
    · TUI-Specific Dependencies
  Package Publication
    · Published Crates
  Workspace Structure Summary

## · Installation and Getting Started  (L1114)
  源文件: .github/workflows/build-and-release.yml, README.md, assets/stakpak-dark.png, assets/stakpak-light.png, cliff.toml, libs/popup-widget/Cargo.toml, libs/popup-widget/README.md, release.sh
  Installation Methods
    · Installation Distribution Flow
    · Installation Commands by Method
  Configuration and Authentication
    · Configuration Architecture
    · Configuration File Structure
    · Environment Variables
  Basic Usage and Startup Modes
    · CLI Command Structure
    · Common Usage Commands
    · Interactive TUI Mode
    · Docker Deployment
  MCP Server Modes
    · MCP Server Architecture
    · Tool Mode Configuration
    · MCP Server Startup Examples
    · MCP Proxy Mode
    · Security Features
  Configuration Files and Environment
    · Environment Variables

## · CLI Interface  (L1564)
  源文件: README.md, assets/stakpak-dark.png, assets/stakpak-light.png, cli/src/commands/agent/run/helpers.rs, cli/src/commands/agent/run/mode_async.rs, cli/src/commands/agent/run/mode_interactive.rs, cli/src/commands/mod.rs, cli/src/main.rs
  CLI Argument Structure
    · Main CLI Structure
    · Subcommand Structure
  Execution Flow
    · Main Dispatch Logic
    · Configuration and Profile Management
  Agent Execution Modes  
    · Mode Determination and Configuration
    · Execution Mode Characteristics
    · Configuration Structures
  Integration Points
    · System Component Integration
    · MCP Server Integration
    · Code Index Management

## · Main Entry Point and Configuration  (L1946)
  源文件: cli/src/commands/agent/run/helpers.rs, cli/src/commands/agent/run/mode_async.rs, cli/src/commands/agent/run/mode_interactive.rs, cli/src/commands/mod.rs, cli/src/main.rs
  Purpose and Scope
  Application Entry Point
    · Initialization Sequence Diagram
    · Key Initialization Steps
  Command-Line Interface Structure
    · Cli Struct Overview
    · Commands Enum
  Configuration System
    · AppConfig Loading
    · Configuration Structure
    · Profile Hierarchy
  Provider Initialization
    · ProviderType Selection
    · RemoteClient Initialization
    · LocalClient Initialization
  Execution Routing
    · Routing Decision Tree
    · Warden Pre-Execution Check
    · Machine Name Generation
  Authentication and Credential Resolution
    · Authentication Check Flow
    · Credential Resolution Chain
  Agent Initialization Sequence
    · Pre-Execution Setup
    · Parallel Initialization Optimization
  Configuration File Format
    · Sample Configuration
  Execution Mode Selection
    · Mode Determination Logic
    · RunAsyncConfig Structure
    · RunInteractiveConfig Structure
  Summary Table: Initialization Flow

## · Agent Execution Modes  (L2586)
  源文件: cli/src/commands/agent/run/helpers.rs, cli/src/commands/agent/run/mode_async.rs, cli/src/commands/agent/run/mode_interactive.rs, cli/src/commands/mod.rs, cli/src/main.rs
  Purpose and Scope
  Execution Mode Selection
    · Decision Flow
    · Mode Selection Flags
  Configuration Structures
    · RunInteractiveConfig
    · RunAsyncConfig
    · Key Differences
  Interactive Mode Architecture
    · Component Architecture
    · Event Flow and Communication
    · Profile Switching Mechanism
    · Key OutputEvent Handlers
  Async Mode Architecture
    · Execution Flow
    · Step Execution Logic
    · Output Rendering
  Mode Comparison
    · Architectural Differences
    · Execution Context
    · Common Components
  When to Use Each Mode
    · Interactive Mode (Default)
    · Async Mode (Batch)
    · Single-Step Mode (Print Flag)
  Mode-Specific Features
    · Interactive Mode Only
    · Async Mode Only

## · Context Injection Pipeline  (L3219)
  源文件: cli/src/commands/agent/run/helpers.rs, cli/src/commands/agent/run/mode_async.rs, cli/src/commands/agent/run/mode_interactive.rs, cli/src/commands/mod.rs, cli/src/main.rs
  Purpose and Scope
  Pipeline Architecture
    · Pipeline Execution Flow
  Context Components
    · Local Context Component
    · Rulebooks Component
    · Subagents Component
    · AGENTS.md Component
    · Shell History Component
  Pipeline Implementation in Execution Modes
    · Interactive Mode Pipeline
    · Async Mode Pipeline
  Helper Function Reference
    · add_local_context
    · add_rulebooks
    · add_subagents
    · add_agents_md
    · tool_call_history_string
  Configuration and Initialization
  XML Tag Convention

## · Session and Profile Management  (L3669)
  源文件: README.md, assets/stakpak-dark.png, assets/stakpak-light.png, cli/src/commands/agent/run/helpers.rs, cli/src/commands/agent/run/mode_async.rs, cli/src/commands/agent/run/mode_interactive.rs, cli/src/commands/mod.rs, cli/src/main.rs
  Purpose and Scope
  Profile-Based Configuration System
    · Profile Structure
    · Special "all" Profile
    · Profile Selection Priority
    · Profile Loading Flow
  Session Management
    · Session Structure
    · Session Lifecycle in Interactive Mode
    · Session Operations
    · Session Storage by Provider Type
  Checkpoint System
    · Checkpoint Structure
    · Checkpoint ID Embedding
    · Checkpoint Creation and Retrieval Flow
    · Loading Checkpoint Messages
    · CLI Checkpoint Flag
  Runtime Profile Switching
    · Profile Switch Flow
    · Profile Switch Outer Loop
    · Profile Validation
    · TUI Profile Display
  Session and Profile State Management
    · State Variables in Interactive Mode
    · Rulebook Re-injection
    · TUI Session State
    · Session List Loading
  Configuration Commands
    · Profile Management Commands
    · Profile List Interactive Menu
    · Session Storage Locations
  Integration with Context Injection
    · First Message vs. Subsequent Messages
    · Context Re-injection on Resume
  Summary

## · Terminal User Interface (TUI)  (L4255)
  源文件: README.md, assets/stakpak-dark.png, assets/stakpak-light.png, tui/src/app.rs, tui/src/lib.rs, tui/src/services/update.rs, tui/src/view.rs
  System Position and Communication
  Entry Point and Initialization
  State Management Architecture
  Event System Architecture
  Event Loop Implementation
  Rendering Pipeline
  Terminal Management

## · Core Architecture and Event Loop  (L4676)
  源文件: tui/src/app.rs, tui/src/lib.rs, tui/src/services/update.rs, tui/src/view.rs
  Architecture Overview
  Channel Communication System
  Main Event Loop Structure
  Event Processing Pipeline
  Task Orchestration and Lifecycle

## · State Management  (L4963)
  源文件: tui/src/app.rs, tui/src/lib.rs, tui/src/services/update.rs, tui/src/view.rs
  AppState Structure and Subsystems
  State Initialization and Configuration
    · AppStateOptions Structure
    · Background Service Initialization
  Unidirectional Data Flow Pattern
    · The Update Function
    · Event Types
  Key State Subsystems
    · Input & TextArea State
    · Messages & Scrolling State
    · Tool Call State
    · Shell Popup State
    · Side Panel State
  File Search and Command Completion
    · File Search Worker Initialization
    · Polling Results
  Shell Command State Lifecycle
    · Shell State Fields
    · Event Flow
  Security and Privacy State

## · Event Handling and User Input  (L5494)
  源文件: tui/src/app.rs, tui/src/app/events.rs, tui/src/lib.rs, tui/src/services/commands.rs, tui/src/services/handlers/input.rs, tui/src/services/handlers/mod.rs, tui/src/services/handlers/popup.rs, tui/src/services/update.rs, tui/src/view.rs
  Event System Architecture
    · Event Flow Pattern
    · InputEvent Enum Structure
    · OutputEvent Enum
  Event Transformation Pipeline
    · Crossterm to InputEvent Mapping
    · Input Blocking and Filtering
  Update Dispatcher
    · Update Function Signature
    · Event Routing Pattern
  Handler Modules
    · Input Handler Module
    · Navigation Handler Module
    · Dialog Handler Module
    · Tool Handler Module
    · Shell Handler Module
    · Popup Handler Module
    · Message Handler Module
    · Misc Handler Module
  Special Input Modes
    · Shell Mode Input Interception
    · Popup Input Interception
    · Input Blocking During Profile Switch
  Command System
    · Command Registry
    · Command Execution Flow
    · Command Palette Integration

## · Rendering System  (L6202)
  源文件: tui/src/app.rs, tui/src/lib.rs, tui/src/services/bash_block.rs, tui/src/services/detect_term.rs, tui/src/services/markdown_renderer.rs, tui/src/services/message.rs, tui/src/services/syntax_highlighter.rs, tui/src/services/update.rs, tui/src/view.rs
  Overview and Architecture
    · Rendering Flow Diagram
  The View Function
    · View Function Signature and Flow
    · Layout Calculation Strategy
    · Key Layout Calculations
  Message Rendering Pipeline
    · Message Processing Flow
    · Message Content Type Handling
  Caching System
    · Cache Structure
    · Cache Validation Logic
  Content Type Renderers
    · Markdown Renderer
    · Bash Block Renderer
    · ANSI Processing
  Input Area Rendering
    · TextArea Rendering Flow
  Popup Rendering Order
  Terminal Adaptation
    · Terminal Detection and Color Adaptation
  Performance Characteristics
  Rendering Component Summary

## · Message System and Display  (L6788)
  源文件: tui/src/services/bash_block.rs, tui/src/services/detect_term.rs, tui/src/services/markdown_renderer.rs, tui/src/services/message.rs, tui/src/services/syntax_highlighter.rs
  Overview
  Message Architecture
    · MessageContent Enum
    · Message Struct
  Message Processing Pipeline
    · Entry Points and Caching
    · Cache Invalidation Strategy
    · Content Type Routing
  Content Rendering Systems
    · Bordered Block Rendering
    · BubbleColors System
    · Border Block Structure
  Terminal Output Processing
    · ANSI Code Handling
    · Carriage Return Processing
    · Unicode Width Calculation
  Markdown Rendering
    · Parsing Pipeline
    · MarkdownComponent Types
    · Syntax Highlighting
    · MarkdownStyle Configuration
  File Diff Rendering
    · Diff Extraction
    · Diff Line Styling
  Adaptive Color System
    · Terminal Detection
    · AdaptiveColors Methods
  Shell History Rendering
    · Detection and Parsing
  Result Block Rendering
    · Compact vs Bordered Display
    · Result Block Structure
  Performance Considerations
    · Caching Strategy
    · Processing Limits
    · Line Wrapping Optimization
  Special Content Processing
    · Markdown Delimiter Stripping
    · Local Context and Rulebook Stripping
    · Checkpoint Pattern Processing

## · Interactive Components  (L7563)
  源文件: tui/src/app/events.rs, tui/src/services/commands.rs, tui/src/services/handlers/input.rs, tui/src/services/handlers/mod.rs, tui/src/services/handlers/popup.rs, tui/src/services/hint_helper.rs
  Component Overview
  Profile Switcher
  Rulebook Switcher
  Command Palette and Shortcuts Popup
    · Command Palette (Commands Mode)
    · Command Execution Flow
  Approval Popup
    · Approval State Management
    · Approval Popup API
  File Changes Popup
    · File Change Tracking
    · File Changes Handlers
  Side Panel
    · Side Panel Implementation
  Hints System
    · Hint Display Logic
    · Context Utilization Hints
    · Hint Alignment
  Autocomplete System
  Dialog Systems
    · Confirmation Dialog
    · Sessions Dialog
  Shell Integration
    · Key Shell Features
  Hint and Helper System
    · Hint Display Logic
  Input Rendering
  Dropdown Rendering
  Autocomplete System
  Dialog Systems
    · Confirmation Dialog
    · Sessions Dialog
  Shell Integration
    · Key Shell Features
  Hint and Helper System
    · Hint Display Logic
  Input Rendering
  Dropdown Rendering

## · Shell Mode Integration  (L9038)
  源文件: tui/src/app.rs, tui/src/lib.rs, tui/src/services/bash_block.rs, tui/src/services/detect_term.rs, tui/src/services/markdown_renderer.rs, tui/src/services/message.rs, tui/src/services/syntax_highlighter.rs, tui/src/services/update.rs, tui/src/view.rs
  Overview and Purpose
  Architecture Overview
  State Management
    · Backward Compatibility State
  Shell Command Execution
    · Command Spawning Flow
    · Implementation Details
  VT100 Terminal Emulation
    · VT100 Parser Integration
    · Output Processing
  Shell Popup Display
    · Popup Rendering System
    · Layout Integration
    · Rendering Implementation
  Event Flow and Processing
    · Shell Event Types
    · Event Forwarding Task
  Interactive Input Support
    · Input Flow for Interactive Commands
    · Password Masking
  Shell History in Message Bubbles
    · History Rendering
    · Shell Block Parsing
  Integration Points
    · Message System Integration
    · Tool Call Integration
  Platform-Specific Considerations
    · Unix PTY Support
    · Non-Unix Background Process

## · Agent Provider and API  (L9583)
  源文件: libs/api/Cargo.toml, libs/api/src/lib.rs, libs/api/src/local/mod.rs, libs/api/src/models.rs, libs/mcp/server/README_SECRETS.md, libs/shared/src/container.rs, libs/shared/src/models/integrations/mod.rs, libs/shared/src/models/integrations/search_service.rs
  Purpose and Architecture
  AgentProvider Trait Definition
    · AgentProvider Method Categories
    · Method Signatures
  Core Data Models
    · Session and Checkpoint Structures
    · Key Model Types
  RemoteClient Implementation
    · RemoteClient Architecture
    · Configuration
    · Request Flow
  LocalClient Implementation
    · LocalClient Structure and Components
    · LocalClient Configuration
    · Initialization Sequence
  Session Management in LocalClient
    · Database Schema
    · Session Lifecycle
  Chat Completion Methods
    · Non-Streaming Flow
    · Streaming Flow Differences
  Hook System Integration
    · Lifecycle Events
  Search Services Integration
    · SearchServicesOrchestrator Architecture
    · Search Flow
    · SearchClient HTTP API
  Configuration Examples
    · Remote Client Configuration
    · Local Client Configuration
    · Model Options Defaults
  Error Handling

## · AgentProvider Trait  (L10336)
  源文件: libs/api/Cargo.toml, libs/api/src/lib.rs, libs/api/src/models.rs, libs/mcp/server/README_SECRETS.md
  Purpose and Scope
  Trait Definition and Structure
    · Trait Method Overview
  Method Categories
    · Account Management
    · Rulebook Management
    · Session Management
    · Chat Operations
    · Search and Memory
    · Slack Integration
  Key Data Models
    · Core Session Types
    · Rulebook Types
    · Block and Document Types
  Abstraction and Implementation Pattern
  Error Handling
  Dependencies
  Usage Pattern Example

## · Remote Client Implementation  (L10813)
  源文件: README.md, assets/stakpak-dark.png, assets/stakpak-light.png, libs/api/Cargo.toml, libs/api/src/lib.rs, libs/api/src/models.rs, libs/mcp/server/README_SECRETS.md
  Overview
  Configuration
    · Configuration Methods
    · Example Configuration
  Module Structure
  AgentProvider Trait Implementation
  HTTP Communication Layer
  Authentication Mechanism
  Data Models
    · Core Request Types
    · Core Response Types
  Streaming Support
  Error Handling
    · ApiStreamError Variants
  Session and Checkpoint Management
    · Session Data Structures
  Rulebook Operations
    · Rulebook Structure
    · API Methods
  Chat Completion Methods
    · Input Parameters
    · Synchronous Completion
    · Streaming Completion
  Search and Memory Operations
    · Document Search
    · Memory Operations
  Slack Integration
    · Slack Methods
    · Request Parameters
  Dependencies

## · Local Client Implementation  (L11359)
  源文件: libs/api/src/local/mod.rs, libs/shared/src/container.rs, libs/shared/src/models/integrations/mod.rs, libs/shared/src/models/integrations/search_service.rs
  Purpose and Scope
  Architecture Overview
  Core Components
    · LocalClient Structure
    · Configuration and Initialization
    · Model Selection System
    · SQLite Database Integration
    · Hook Registry and Lifecycle Management
    · Search Services Orchestrator
  AgentProvider Implementation
    · Account Management
    · Rulebook Management
    · Session Management
    · Chat Completion Methods
    · Search and Document Operations
    · Unsupported Operations
  Internal Implementation Details
    · Agent Completion Flow
    · Session Initialization
    · Session Update
    · Session Title Generation
    · Search Query Analysis
    · Search Results Validation
    · Model Selection for Search
  Summary

## · Data Models and Types  (L12123)
  Search and Integration Models
    · SearchServicesOrchestrator
    · Search Workflow
  Request and Response Models
    · Search Requests
    · Slack Integration Requests
  Rulebook Models
    · Rulebook Operations
  Supporting Types
    · Document Models
    · Account Models
    · Session Statistics
    · Error Types
  Overview of Data Model Categories
  Agent Session Models
    · Key Session Types
    · RunAgentOutput
  Message and Chat Models
    · Tool Definition
    · Usage Example
  Agent State Models
    · AgentState Methods
    · LLM Model Types
  Code Block Models
    · Session File Management

## · MCP (Model Context Protocol) System  (L12811)
  源文件: README.md, assets/stakpak-dark.png, assets/stakpak-light.png, cli/src/utils/local_context.rs, libs/api/Cargo.toml, libs/api/src/lib.rs, libs/api/src/models.rs, libs/mcp/server/README_SECRETS.md, libs/mcp/server/src/local_tools.rs, libs/shared/src/local_store.rs, libs/shared/src/remote_connection.rs, libs/shared/src/task_manager.rs
  MCP Components Overview
    · MCP Server - Tool Provider
    · MCP Client - Tool Consumer
    · MCP Proxy - Connection Multiplexer
  Tool Categories and Capabilities
    · File and Directory Operations
    · Command Execution
    · Task Management
    · Utility Tools
    · Tool Mode Configuration
  Security and Privacy Features
    · Secret Redaction with Gitleaks
    · Privacy Mode
    · mTLS Encryption
  Background Task Management
  Remote Operations via SSH
    · Remote Path Formats
    · Authentication Methods
  Integration with Security Systems
    · Security Feature Integration

## · MCP Architecture  (L13283)
  源文件: README.md, assets/stakpak-dark.png, assets/stakpak-light.png, libs/api/Cargo.toml, libs/api/src/lib.rs, libs/api/src/models.rs, libs/mcp/server/README_SECRETS.md
  Overview
  System Architecture
  Component Details
    · MCP Server
    · MCP Proxy
    · MCP Client
  Security Architecture
    · mTLS Transport Security
    · Dynamic Secret Substitution
    · Privacy Mode
  Tool Container Architecture
  Configuration Files
    · Server Configuration
    · Proxy Configuration
    · Session State
  Integration with Stakpak Agent
  Command Reference

## · Tool Container and Execution Flow  (L13752)
  源文件: cli/src/utils/local_context.rs, libs/mcp/server/src/local_tools.rs, libs/shared/src/local_store.rs, libs/shared/src/remote_connection.rs, libs/shared/src/task_manager.rs, libs/shared/src/utils.rs
  Tool Container Architecture
  Tool Routing Mechanisms
    · JSON-RPC Tool Call Protocol
    · Tool Mode Routing
  Tool Execution Flow
    · Request Processing Pipeline
  Session Management and State
    · Session Storage Architecture
    · Secret Redaction Session Flow
  Error Handling and Diagnostics
    · Error Response Structure

## · Local Tools Implementation  (L14173)
  源文件: cli/src/utils/local_context.rs, libs/mcp/server/src/local_tools.rs, libs/shared/src/local_store.rs, libs/shared/src/remote_connection.rs, libs/shared/src/task_manager.rs, libs/shared/src/utils.rs
  Architecture Overview
  File Operations Tools
    · View Tool
    · Create Tool
    · String Replace Tool
  Shell Command Tools
    · Synchronous Command Execution
    · Asynchronous Command Execution
  Task Management Tools
    · Task Listing
    · Task Details
    · Task Cancellation
  Password Generation Tool
  Secret Management Integration
  Output Management

## · Task Management System  (L14733)
  源文件: cli/src/utils/local_context.rs, libs/mcp/server/src/local_tools.rs, libs/shared/src/local_store.rs, libs/shared/src/remote_connection.rs, libs/shared/src/task_manager.rs, libs/shared/src/utils.rs
  System Architecture
    · High-Level Architecture
    · Core Data Flow
  Core Components
    · TaskManager
    · TaskManagerHandle
    · Task Data Structures
  Task Lifecycle and State Machine
    · Task States
    · State Transitions
  Message Passing Architecture
    · TaskMessage Variants
    · Message Handler Flow
  Task Execution
    · Local Task Execution
    · Remote Task Execution
  Task Operations
    · Starting Tasks
    · Cancelling Tasks
    · Waiting for Tasks
    · Listing All Tasks
  Integration with MCP Tools
    · Tool: run_command_task
    · Tool: get_all_tasks
    · Tool: cancel_task
    · Tool: wait_for_tasks
    · Tool: get_task_details
  Streaming and Progress Updates
    · Partial Updates
    · MCP Progress Notifications
  Task Cleanup and Shutdown
    · Graceful Shutdown
    · Memory Management
    · Error Handling

## · Remote Operations and SSH  (L15375)
  源文件: cli/src/utils/local_context.rs, libs/mcp/server/src/local_tools.rs, libs/shared/src/local_store.rs, libs/shared/src/remote_connection.rs, libs/shared/src/task_manager.rs, libs/shared/src/utils.rs
  Architecture Overview
    · Remote Tools System Flow
    · Tool Authentication and Client Integration
  Code Generation Tool
    · Code Generation Request Structure
    · File Edit Processing
  Documentation Search Tool
    · Search Strategy Implementation
  Memory Search Tool
    · Memory Search Parameters
  Rulebook Access Tool
    · Rulebook Request Structure
  Local Code Search Tool
    · Code Search Architecture
    · Scoring Algorithm
    · Index Dependency Management
  Security Integration
    · Secret Redaction Points
  Error Handling
    · Common Error Patterns

## · Security and Privacy  (L15668)
  源文件: README.md, assets/stakpak-dark.png, assets/stakpak-light.png, cli/src/utils/local_context.rs, libs/api/Cargo.toml, libs/api/src/lib.rs, libs/api/src/models.rs, libs/mcp/server/README_SECRETS.md, libs/mcp/server/src/local_tools.rs, libs/shared/src/local_store.rs, libs/shared/src/remote_connection.rs, libs/shared/src/task_manager.rs
  Overview of Security Components
  Security Features Matrix
  Dynamic Secret Substitution
    · How It Works
  Warden Guardrails
    · Architecture
  Privacy Mode
    · Enhanced Detection
  mTLS Transport Security
    · mTLS Architecture
  Integration with MCP Tools
    · Tool-Level Security Integration
    · Tool Security Methods
  Configuration and Customization
    · Rule Management
    · Performance Optimization

## · Secret Substitution System  (L16088)
  源文件: cli/src/utils/local_context.rs, libs/api/Cargo.toml, libs/api/src/lib.rs, libs/api/src/models.rs, libs/mcp/server/README_SECRETS.md, libs/mcp/server/src/local_tools.rs, libs/shared/src/local_store.rs, libs/shared/src/remote_connection.rs, libs/shared/src/task_manager.rs, libs/shared/src/utils.rs
  Purpose and Scope
  System Architecture
  Secret Detection and Redaction Pipeline
  Placeholder Format and Generation
    · Placeholder Structure
    · Example Transformations
  Secret Restoration Flow
  Session Storage Implementation
    · File Location and Structure
    · Session File Operations
    · LocalStore Integration
  Integration with MCP Tools
    · Tool-Specific Integration Points
    · run_command Integration
    · run_command_task Integration
    · File Operation Tools
    · generate_password Tool
  Implementation Details
    · SecretManager Component Structure
    · Gitleaks Integration
    · Placeholder Generation Algorithm
    · Output Processing with Secret Redaction
  Task Manager Integration
  Security Features and Considerations
    · Session Scope and Isolation
    · File System Security
    · Detection Coverage
    · Limitations
  Remote Execution Integration
  Configuration and Control

## · Warden Guardrails  (L16723)
  源文件: .github/workflows/build-and-release.yml, README.md, assets/stakpak-dark.png, assets/stakpak-light.png, cliff.toml, libs/popup-widget/Cargo.toml, libs/popup-widget/README.md, release.sh
  Purpose and Scope
  Architecture Overview
  Deployment Model
    · Build Process
    · Docker Image Structure
  Policy Enforcement Mechanisms
    · Network-Level Filtering
    · Operation-Level Validation
  Integration with Agent Components
    · Integration Points
  Usage and Configuration
    · Running with Warden Protection
    · Policy Configuration
  Comparison with Other Security Features
  Release and Distribution
  Implementation Notes

## · Privacy Mode and Data Redaction  (L17058)
  源文件: README.md, assets/stakpak-dark.png, assets/stakpak-light.png, libs/api/Cargo.toml, libs/api/src/lib.rs, libs/api/src/models.rs, libs/mcp/server/README_SECRETS.md
  Purpose and Scope
  Privacy Mode Overview
  Data Types Redacted
  Configuration and Usage
    · MCP Server with Privacy Mode
    · MCP Proxy with Privacy Mode
  Privacy Mode Architecture
  Integration with Tool Execution
  Comparison: Privacy Mode vs Secret Substitution
  Security Considerations
    · When to Enable Privacy Mode
    · Privacy Mode Limitations
    · Combining Security Features
  Operational Examples
    · Example 1: Command Output Redaction
    · Example 2: AWS Configuration Redaction
    · Example 3: Log File Sanitization
  Implementation Architecture
  Best Practices
    · Recommended Configurations
    · Operational Guidelines
    · Troubleshooting
  Related Security Features

## · Build System and Deployment  (L17560)
  源文件: .github/workflows/build-and-release.yml, README.md, assets/stakpak-dark.png, assets/stakpak-light.png, cliff.toml, libs/popup-widget/Cargo.toml, libs/popup-widget/README.md, release.sh
  Build System Overview
  Release Management
  CI/CD Pipeline
  Build Configuration and Targets
  Crates.io Publishing
  Docker Image Build Process
  Release Notes Generation
  Homebrew Distribution
  Distribution Channels
    · GitHub Releases
    · Container Registry
    · Homebrew Package Manager
  Workspace Configuration

## · CI/CD Pipeline  (L18254)
  源文件: .github/workflows/build-and-release.yml, cliff.toml, libs/popup-widget/Cargo.toml, libs/popup-widget/README.md, release.sh
  Purpose and Scope
  Workflow Triggers and Execution Modes
    · Trigger Conditions
  Build Matrix and Platform Support
    · Multi-Platform Build Architecture
    · Build Process Steps
    · Linux Static Linking
  Job Dependency Graph and Execution Flow
    · Job Descriptions
  Release Creation and Artifact Distribution
    · GitHub Release Job
    · Release Notes Enhancement
  Crates.io Publishing Pipeline
    · Workspace Publishing Strategy
    · Publishing Logic
  Docker Image Build Pipeline
    · Main Docker Image
    · Warden Security Container
  Homebrew Formula Updates
    · Update Process
  Testing and Quality Assurance
    · Automated Testing
    · Version Verification
    · Rust Cache Optimization
  Permissions and Security
  Environment Configuration

## · Release Management  (L18648)
  源文件: .github/workflows/build-and-release.yml, cliff.toml, libs/popup-widget/Cargo.toml, libs/popup-widget/README.md, release.sh
  Purpose and Scope
  Release Process Overview
  Version Bumping with release.sh
    · Script Usage
    · Version Update Process
  Git Workflow and Tagging
    · Commit and Tag Creation
    · Beta Version Tracking
  CI/CD Pipeline Trigger and Setup
    · Workflow Triggers
    · Setup Job
  Build Matrix and Artifacts
    · Build Matrix Configuration
    · Build Process Steps
  Release Creation and Publishing
    · Release Job
    · Crates.io Publishing
  Beta Releases
    · Beta Release Characteristics
    · Creating Beta Releases
    · Beta Release Conditional Logic
  Release Notes Generation
    · Release Notes Workflow
    · Git-Cliff Configuration
  X.Y.Z
    · FEATURES
    · BUG FIXES
  Docker Image Publishing
    · Main Docker Image
    · Warden Docker Image
  Homebrew Formula Updates

## · Distribution Channels  (L19328)
  源文件: .github/workflows/build-and-release.yml, README.md, assets/stakpak-dark.png, assets/stakpak-light.png, cliff.toml, libs/popup-widget/Cargo.toml, libs/popup-widget/README.md, release.sh
  Overview
  Distribution Workflow Sequence
  Crates.io Publishing
    · Workspace Publishing Order
    · Publishing Process
    · Authentication
  Docker Images
    · Main Image: ghcr.io/stakpak/agent
    · Warden Image: ghcr.io/stakpak/agent-warden
    · Docker Build Configuration
  Homebrew Formula
    · Formula Generation Process
    · Formula Structure
    · Formula Template
    · Beta Release Handling
    · Authentication
  Distribution Channel Comparison
  Distribution Triggers and Conditions
  Installation Instructions Reference