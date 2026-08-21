# Skeleton: cortex-mem（51 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 9KB | 2 | ~7 | 25 |
| 2 | System Architecture | L207 | 10KB | 3 | ~1 | 25 |
| 3 | Key Features | L423 | 11KB | 3 | ~4 | 26 |
| 4 | Getting Started | L654 | 8KB | 3 | ~4 | 20 |
| 5 | Installation | L840 | 9KB | 2 | ~1 | 29 |
| 6 | Configuration | L1089 | 9KB | 2 | ~10 | 15 |
| 7 | Quick Start Examples | L1319 | 9KB | 2 | ~3 | 31 |
| 8 | Core Architecture | L1570 | 9KB | 1 | ~2 | 26 |
| 9 | Memory Manager | L1745 | 9KB | 2 | ~2 | 15 |
| 10 | Vector Store Integration | L1946 | 9KB | 2 | ~5 | 14 |
| 11 | LLM Client & AI Processing | L2118 | 8KB | 2 | ~3 | 21 |
| 12 | Memory Operations & Shared Tools | L2292 | 11KB | 2 | ~6 | 20 |
| 13 | Optimization Engine | L2520 | 8KB | 2 | ~3 | 4 |
| 14 | Service Interfaces | L2691 | 8KB | 3 | ~4 | 24 |
| 15 | HTTP API Service | L2891 | 9KB | 2 | ~1 | 28 |
| 16 | MCP Server | L3063 | 8KB | 3 | ~8 | 26 |
| 17 | Command Line Interface | L3292 | 8KB | 2 | ~0 | 16 |
| 18 | Web Dashboard | L3500 | 6KB | 2 | ~2 | 8 |
| 19 | Dashboard & Monitoring | L3657 | 8KB | 3 | ~5 | 3 |
| 20 | Analytics & Statistics | L3861 | 9KB | 2 | ~2 | 1 |
| 21 | TARS Application | L4043 | 7KB | 2 | ~2 | 20 |
| 22 | TUI Interface & State Management | L4211 | 8KB | 3 | ~9 | 14 |
| 23 | Multi-Agent System | L4437 | 8KB | 4 | ~3 | 14 |
| 24 | Audio Integration API | L4669 | 9KB | 3 | ~2 | 10 |
| 25 | Integration Guides | L4904 | 8KB | 3 | ~8 | 19 |
| 26 | RIG Framework Integration | L5117 | 9KB | 3 | ~5 | 11 |
| 27 | MCP Client Integration | L5337 | 9KB | 4 | ~6 | 15 |
| 28 | HTTP Client Integration | L5630 | 8KB | 2 | ~3 | 16 |
| 29 | Direct Library Integration | L5836 | 10KB | 2 | ~4 | 20 |
| 30 | OpenClaw Plugin Integration | L6130 | 9KB | 2 | ~7 | 24 |
| 31 | Development & Testing | L6307 | 7KB | 2 | ~0 | 2 |
| 32 | Evaluation Framework | L6478 | 9KB | 1 | ~4 | 9 |
| 33 | Evaluation Metrics | L6640 | 8KB | 2 | ~4 | 6 |
| 34 | Architecture Decisions | L6832 | 9KB | 2 | ~2 | 17 |
| 35 | Contributing Guidelines | L7045 | 6KB | 1 | ~0 | 9 |
| 36 | API Reference | L7200 | 10KB | 3 | ~2 | 24 |
| 37 | HTTP API Endpoints | L7408 | 10KB | 2 | ~4 | 28 |
| 38 | MCP Tool Definitions | L7661 | 9KB | 2 | ~4 | 25 |
| 39 | Core Types & Interfaces | L7875 | 9KB | 3 | ~3 | 19 |
| 40 | CLI Command Reference | L8155 | 8KB | 2 | ~5 | 16 |
| 41 | Configuration Reference | L8395 | 7KB | 2 | ~2 | 14 |
| 42 | Core Configuration | L8572 | 8KB | 2 | ~8 | 6 |
| 43 | Service Configuration | L8767 | 8KB | 3 | ~4 | 17 |
| 44 | Environment Variables | L8969 | 7KB | 2 | ~2 | 11 |
| 45 | Bot Configuration | L9177 | 10KB | 4 | ~5 | 14 |
| 46 | Deployment Guide | L9416 | 9KB | 2 | ~4 | 28 |
| 47 | Docker Deployment | L9660 | 10KB | 2 | ~3 | 21 |
| 48 | Production Considerations | L9928 | 8KB | 2 | ~0 | 14 |
| 49 | Multi-Service Architecture | L10088 | 8KB | 3 | ~2 | 18 |
| 50 | Performance Optimization | L10290 | 8KB | 2 | ~5 | 2 |
| 51 | Glossary | L10481 | 9KB | 2 | ~1 | 33 |


## · Overview  (L6)
  源文件: Cargo.toml, README.md, README_zh.md, cortex-mem-config/Cargo.toml, cortex-mem-core/Cargo.toml, cortex-mem-core/src/incremental_memory_updater.rs, cortex-mem-core/src/llm/prompts.rs, cortex-mem-core/src/search/vector_engine.rs, cortex-mem-mcp/Cargo.toml, cortex-mem-rig/Cargo.toml, cortex-mem-service/Cargo.toml, cortex-mem-service/src/handlers/automation.rs
  Purpose and Scope
  What is Cortex-Mem?
  Ecosystem Overview
  Three-Domain Architecture
  Memory Lifecycle & Workflows
  Technology Stack
  Integration Patterns
  Getting Started

## · System Architecture  (L207)
  源文件: Cargo.toml, README.md, README_zh.md, cortex-mem-config/Cargo.toml, cortex-mem-core/Cargo.toml, cortex-mem-core/src/incremental_memory_updater.rs, cortex-mem-core/src/llm/prompts.rs, cortex-mem-core/src/search/vector_engine.rs, cortex-mem-mcp/Cargo.toml, cortex-mem-rig/Cargo.toml, cortex-mem-service/Cargo.toml, cortex-mem-service/src/handlers/automation.rs
  Purpose and Scope
  Three-Domain Architecture Pattern
    · 1. Configuration Domain
    · 2. Core Memory Domain
    · 3. Tool Support Domain
  Modular Monolith Pattern
    · System Architecture Overview
  Memory Hierarchy and Data Flow
    · Semantic Search Data Flow
  Event-Driven Automation
    · Memory Update Pipeline

## · Key Features  (L423)
  源文件: README.md, README_zh.md, cortex-mem-core/src/automation/indexer.rs, cortex-mem-core/src/automation/layer_generator.rs, cortex-mem-core/src/automation/manager.rs, cortex-mem-core/src/automation/mod.rs, cortex-mem-core/src/automation/sync.rs, cortex-mem-core/src/cascade_layer_updater.rs, cortex-mem-core/src/incremental_memory_updater.rs, cortex-mem-core/src/layers/generator.rs, cortex-mem-core/src/layers/manager.rs, cortex-mem-core/src/llm/client.rs
  Core Intelligence Features
    · Automatic Fact Extraction
    · Layered Memory Hierarchy (L0/L1/L2)
    · Memory Forgetting Mechanism
  Storage and Retrieval Architecture
    · Vector-Based Semantic Search
    · Multi-Tenancy and Isolation
  Multi-Interface Access
    · Service Interfaces
    · Event-Driven Automation
  Performance and Optimization
    · LLM Result Caching
    · Search Reranking

## · Getting Started  (L654)
  源文件: Cargo.toml, README.md, README_zh.md, cortex-mem-config/Cargo.toml, cortex-mem-core/Cargo.toml, cortex-mem-core/src/incremental_memory_updater.rs, cortex-mem-core/src/llm/prompts.rs, cortex-mem-core/src/search/vector_engine.rs, cortex-mem-mcp/Cargo.toml, cortex-mem-rig/Cargo.toml, cortex-mem-service/Cargo.toml, cortex-mem-service/src/handlers/automation.rs
  Prerequisites
  System Components Overview
  Installation Methods
  Configuration Structure
  First Steps & Verification
    · 1. Initialize the Runtime
    · 2. Add a Memory
    · 3. Search Memories

## · Installation  (L840)
  源文件: Cargo.toml, README.md, README_zh.md, cortex-mem-cli/README.md, cortex-mem-cli/tests/cli_commands_test.rs, cortex-mem-config/Cargo.toml, cortex-mem-config/README.md, cortex-mem-core/Cargo.toml, cortex-mem-core/README.md, cortex-mem-core/src/incremental_memory_updater.rs, cortex-mem-core/src/llm/prompts.rs, cortex-mem-core/src/search/vector_engine.rs
  Purpose and Scope
  Prerequisites
    · System Dependency Mapping
  External Dependency Setup
    · 1. Qdrant Vector Database
    · 2. LLM and Embedding API
  Installing Cortex Memory Components
    · 1. Build from Source
    · 2. Component Installation Details
  Implementation & Data Flow
  Verification
    · 1. Initialize Configuration
    · 2. Start the Service
    · 3. Verify Vector Store Connectivity
    · 4. Test Search Latency
  Troubleshooting

## · Configuration  (L1089)
  源文件: cortex-mem-cli/README.md, cortex-mem-cli/src/main.rs, cortex-mem-cli/tests/cli_commands_test.rs, cortex-mem-config/README.md, cortex-mem-config/src/lib.rs, cortex-mem-core/README.md, cortex-mem-core/src/config.rs, cortex-mem-mcp/README.md, cortex-mem-rig/README.md, cortex-mem-rig/src/lib.rs, cortex-mem-service/README.md, cortex-mem-tools/README.md
  Purpose and Scope
  Configuration File Format
  Configuration Structure
  Configuration Sections
    · Qdrant Configuration (`[qdrant]`)
    · LLM Configuration (`[llm]`)
    · Embedding Configuration (`[embedding]`)
    · Cortex Core Configuration (`[cortex]`)
  Configuration Hierarchy and Data Directory Detection
    · Data Directory Priority
    · Loading Logic
  Auto-Detection and Management Features
    · TARS Auto-Configuration
    · Bot Configuration (`bots.json`)
  Technical Implementation Details
    · Key Classes
    · LLM Intent Analysis Toggle
  Configuration Example

## · Quick Start Examples  (L1319)
  源文件: README.md, README_zh.md, cortex-mem-cli/Cargo.toml, cortex-mem-cli/README.md, cortex-mem-cli/src/commands/add.rs, cortex-mem-cli/src/commands/delete.rs, cortex-mem-cli/src/commands/get.rs, cortex-mem-cli/src/commands/layers.rs, cortex-mem-cli/src/commands/list.rs, cortex-mem-cli/src/commands/mod.rs, cortex-mem-cli/src/commands/search.rs, cortex-mem-cli/src/commands/session.rs
  Interface Overview
  Command Line Interface (CLI)
    · Common Commands
    · Example: Storing and Extracting a Fact
  HTTP API Usage
    · Storing a Message
    · Semantic Search
  Using with an AI Agent (MCP)
    · Agent Tool Examples
  Programmatic Rust Example
  Summary of Memory Layers

## · Core Architecture  (L1570)
  源文件: README.md, README_zh.md, cortex-mem-core/src/automation/indexer.rs, cortex-mem-core/src/automation/layer_generator.rs, cortex-mem-core/src/automation/manager.rs, cortex-mem-core/src/automation/mod.rs, cortex-mem-core/src/automation/sync.rs, cortex-mem-core/src/cascade_layer_updater.rs, cortex-mem-core/src/incremental_memory_updater.rs, cortex-mem-core/src/layers/generator.rs, cortex-mem-core/src/layers/manager.rs, cortex-mem-core/src/llm/client.rs
  Overview
    · Core Architecture Diagram
    · Component Responsibilities
  Memory Manager & Event Coordination
    · Event-Driven Pipeline
  Hybrid Storage: Filesystem & Vector Store
    · The `cortex://` URI Scheme
    · Vector Store Integration
  AI Processing & Search Engine
    · Layered Semantic Search
    · Intent Analysis
  Memory Operations & Automation
    · Automation Features

## · Memory Manager  (L1745)
  源文件: cortex-mem-core/src/automation/layer_generator.rs, cortex-mem-core/src/automation/manager.rs, cortex-mem-core/src/cascade_layer_updater.rs, cortex-mem-core/src/layers/generator.rs, cortex-mem-core/src/layers/manager.rs, cortex-mem-core/src/lib.rs, cortex-mem-core/src/llm/client.rs, cortex-mem-core/src/memory_event_coordinator.rs, cortex-mem-core/src/session/extraction.rs, cortex-mem-core/src/session/manager.rs, cortex-mem-core/src/session/message.rs, cortex-mem-tools/src/operations.rs
  Purpose and Scope
  Component Architecture
    · MemoryManager Orchestration (Code Entity Space)
    · The MemoryOperations Facade
  Memory Lifecycle and Event Flow
    · Data Flow: From Message to Long-Term Memory
    · Memory Event Coordinator (MEC)
  Key Implementation Details
    · Multi-Layer Memory Management
    · Session Management & Extraction
    · Initialization Example
  Optimization Mechanisms

## · Vector Store Integration  (L1946)
  源文件: cortex-mem-core/src/automation/indexer.rs, cortex-mem-core/src/automation/mod.rs, cortex-mem-core/src/automation/sync.rs, cortex-mem-core/src/builder.rs, cortex-mem-core/src/embedding/client.rs, cortex-mem-core/src/types.rs, cortex-mem-core/src/vector_store/qdrant.rs, cortex-mem-insights/src/lib/api.ts, cortex-mem-insights/src/lib/pages/Dashboard.svelte, cortex-mem-insights/src/lib/pages/Search.svelte, cortex-mem-insights/src/lib/stores/search.ts, cortex-mem-insights/src/lib/stores/tenant.ts
  Purpose and Scope
  Architecture and Trait Abstraction
    · System Entity Mapping: Logic to Storage
    · The VectorStore Trait
  Qdrant Implementation Details
    · Initialization and Schema Sync
    · Data Flow: Memory to Vector Point
  Schema and Metadata Management
    · Payload Structure
    · Filtering Logic
  Automated Indexing Patterns
    · The AutoIndexer
    · SyncManager

## · LLM Client & AI Processing  (L2118)
  源文件: README.md, README_zh.md, cortex-mem-core/src/automation/layer_generator.rs, cortex-mem-core/src/automation/manager.rs, cortex-mem-core/src/cascade_layer_updater.rs, cortex-mem-core/src/incremental_memory_updater.rs, cortex-mem-core/src/layers/generator.rs, cortex-mem-core/src/layers/manager.rs, cortex-mem-core/src/llm/client.rs, cortex-mem-core/src/llm/prompts.rs, cortex-mem-core/src/memory_event_coordinator.rs, cortex-mem-core/src/search/vector_engine.rs
  Purpose and Scope
  Architecture & Data Flow
    · AI Processing Orchestration
    · LLM Client Implementation
  Fact Extraction
    · Extraction Logic
    · Memory Schema Mapping
  Hierarchical Layer Processing (L0/L1)
    · Cascade Layer Update
    · Layer Generators
  Search & Intent Analysis
    · VectorSearchEngine Intent Logic
  Configuration and Tuning

## · Memory Operations & Shared Tools  (L2292)
  源文件: cortex-mem-core/src/lib.rs, cortex-mem-core/src/llm/mod.rs, cortex-mem-core/src/session/manager.rs, cortex-mem-mcp/src/service.rs, cortex-mem-tools/src/docs/commit.md, cortex-mem-tools/src/docs/explore.md, cortex-mem-tools/src/docs/ls.md, cortex-mem-tools/src/docs/recall.md, cortex-mem-tools/src/docs/search.md, cortex-mem-tools/src/docs/store.md, cortex-mem-tools/src/mcp/definitions.rs, cortex-mem-tools/src/operations.rs
  Purpose and Scope
  Architectural Context
    · Design Rationale
    · Component Interaction
  The MemoryOperations API
    · Initialization
    · Core Methods
  Memory Storage & Asynchronous Processing
    · Storage Logic Flow
  Semantic Search & Tiered Retrieval
    · Layered Search Strategy
    · Data Structures for Search
  Shared Tool Definitions
    · Standard Tools Table
  Integration Patterns
    · MCP Server Integration
    · RIG Framework Integration
    · TARS Application Usage

## · Optimization Engine  (L2520)
  源文件: cortex-mem-core/src/cascade_layer_debouncer.rs, cortex-mem-core/src/llm_result_cache.rs, cortex-mem-core/src/memory_cleanup.rs, cortex-mem-core/src/memory_index_manager.rs
  System Architecture
  Memory Cleanup & Forgetting
    · Forgetting Logic
    · Vector Synchronization
  Cascade Layer Debouncing
    · How Debouncing Works
  LLM Result Cache
  OptimizationDetector
    · Issue Detection Methods
  ExecutionEngine
    · Action Implementations
  Memory Index Management

## · Service Interfaces  (L2691)
  源文件: cortex-mem-cli/Cargo.toml, cortex-mem-cli/src/commands/add.rs, cortex-mem-cli/src/commands/delete.rs, cortex-mem-cli/src/commands/get.rs, cortex-mem-cli/src/commands/layers.rs, cortex-mem-cli/src/commands/list.rs, cortex-mem-cli/src/commands/mod.rs, cortex-mem-cli/src/commands/search.rs, cortex-mem-cli/src/commands/session.rs, cortex-mem-cli/src/commands/tenant.rs, cortex-mem-core/src/builder.rs, cortex-mem-core/src/embedding/client.rs
  Purpose and Scope
  Interface Architecture
    · System Interface Topology
  Interface Comparison
    · Code Entity Mapping
  Shared Core Integration
    · Common Capabilities Matrix
  Interface Selection Guidelines
    · Decision Tree
    · Key Considerations

## · HTTP API Service  (L2891)
  源文件: README.md, README_zh.md, cortex-mem-core/src/builder.rs, cortex-mem-core/src/embedding/client.rs, cortex-mem-core/src/incremental_memory_updater.rs, cortex-mem-core/src/llm/prompts.rs, cortex-mem-core/src/search/vector_engine.rs, cortex-mem-insights/src/lib/api.ts, cortex-mem-insights/src/lib/pages/Dashboard.svelte, cortex-mem-insights/src/lib/pages/Search.svelte, cortex-mem-insights/src/lib/stores/search.ts, cortex-mem-insights/src/lib/stores/tenant.ts
  Architecture and State Management
    · Code Entity Mapping
    · Application State (`AppState`)
  Endpoint Reference
    · Session Management
    · Semantic Search
    · Filesystem & Automation
  Core Processing Logic
    · Intent Analysis & Search Optimization
    · Event-Driven Updates
  Usage Examples
    · Starting the Service
    · API Request: Semantic Search
    · Error Handling

## · MCP Server  (L3063)
  源文件: cortex-mem-cli/README.md, cortex-mem-cli/tests/cli_commands_test.rs, cortex-mem-config/README.md, cortex-mem-core/README.md, cortex-mem-core/src/filesystem/operations.rs, cortex-mem-mcp/README.md, cortex-mem-mcp/skill/SKILL.md, cortex-mem-mcp/src/main.rs, cortex-mem-mcp/src/service.rs, cortex-mem-rig/README.md, cortex-mem-service/README.md, cortex-mem-tools/README.md
  Architecture Overview
    · System Context Diagram
    · Core Components
  Service Implementation
    · Initialization Process
    · Auto-Trigger Mechanism
    · Tool Execution Flow
  Tool Definitions
    · Available Tools
    · Parameter Mapping and Defaults
  Configuration
    · CLI Arguments
    · Logging and Diagnostics
  Integration Patterns
    · Claude Desktop Integration
    · Memory URI Scoping

## · Command Line Interface  (L3292)
  源文件: cortex-mem-cli/Cargo.toml, cortex-mem-cli/src/commands/add.rs, cortex-mem-cli/src/commands/delete.rs, cortex-mem-cli/src/commands/get.rs, cortex-mem-cli/src/commands/layers.rs, cortex-mem-cli/src/commands/list.rs, cortex-mem-cli/src/commands/mod.rs, cortex-mem-cli/src/commands/search.rs, cortex-mem-cli/src/commands/session.rs, cortex-mem-cli/src/commands/tenant.rs, cortex-mem-cli/src/main.rs, cortex-mem-config/src/lib.rs
  Purpose and Scope
  Overview
  Architecture and Data Flow
    · System Integration Diagram
    · Search Execution Flow
  Command Reference
    · Global Arguments
    · Core Commands
  Configuration Management
    · Example `config.toml`
  Scripting Examples
    · Batch Indexing
    · Automated Session Closing
    · Searching from External Scripts

## · Web Dashboard  (L3500)
  源文件: cortex-mem-insights/README.md, cortex-mem-insights/bun.lock, cortex-mem-insights/package.json, cortex-mem-insights/svelte.config.js, cortex-mem-insights/vite.config.ts, Memory Browser, Dashboard & Monitoring, Analytics & Statistics
  System Architecture
    · Component Hierarchy
    · Technical Stack
  API Client & Integration
    · Service Mapping
    · Core Data Structures
  Dashboard Features
    · 1. System Overview & Tenants
    · 2. Memory & File Browser
    · 3. Vector Search Interface
    · 4. Standalone Server

## · Dashboard & Monitoring  (L3657)
  源文件: cortex-mem-insights/server.ts, litho.docs/en/4.Deep-Exploration/Automation Management Domain.md, litho.docs/en/4.Deep-Exploration/Layer Management Domain.md
  Overview
  Dashboard Page Architecture
    · Statistics Calculation
  Monitor Page Architecture
    · Performance Metrics Calculation
    · Resource Usage Monitoring
  ServiceStatus Component
    · Detailed LLM Monitoring
  Standalone Host & Proxying

## · Analytics & Statistics  (L3861)
  源文件: cortex-mem-insights/.gitignore
  Overview
  Architecture and Data Flow
    · Component Structure
    · Data Loading Sequence
  Statistics Calculation Engine
    · Summary Statistics
    · Distribution and Trend Analysis
  Visualization Components
    · Chart.js Integration
    · Distribution Visuals
  User Interface Layout
    · Loading and Error States
  Integration Points
    · API Endpoints

## · TARS Application  (L4043)
  源文件: Cargo.lock, cortex-mem-cli/src/main.rs, cortex-mem-config/src/lib.rs, cortex-mem-core/src/config.rs, cortex-mem-core/src/lib.rs, cortex-mem-core/src/session/manager.rs, cortex-mem-rig/src/lib.rs, cortex-mem-tools/src/operations.rs, cortex-mem-tools/src/tools/storage.rs, examples/cortex-mem-tars/.gitignore, examples/cortex-mem-tars/Cargo.lock, examples/cortex-mem-tars/Cargo.toml
  Purpose and Scope
  Architecture Overview
    · System Components
  Application Lifecycle
    · Initialization and Execution Flow
  Memory Integration Strategy
    · Bot-Specific Agent Construction
  Child Pages

## · TUI Interface & State Management  (L4211)
  源文件: Cargo.lock, cortex-mem-core/src/lib.rs, cortex-mem-core/src/session/manager.rs, cortex-mem-tools/src/operations.rs, cortex-mem-tools/src/tools/storage.rs, examples/cortex-mem-tars/.gitignore, examples/cortex-mem-tars/Cargo.lock, examples/cortex-mem-tars/Cargo.toml, examples/cortex-mem-tars/src/agent.rs, examples/cortex-mem-tars/src/app.rs, examples/cortex-mem-tars/src/lib.rs, examples/cortex-mem-tars/src/logger.rs
  Purpose and Scope
  State Machine Architecture
    · Primary State Machine
    · Code Entity Mapping: State Enums
  UI Component Structure
    · AppUi Component Diagram
    · Key Implementation Details
  Event Loop & Message Passing
    · Data Flow: Natural Language to Code Entities
    · Message Types
  Keyboard & Mouse Handling
    · Keyboard Event Routing
    · Mouse Interaction
  Theme System
  Summary of Key Functions

## · Multi-Agent System  (L4437)
  源文件: Cargo.lock, cortex-mem-cli/src/main.rs, cortex-mem-config/src/lib.rs, cortex-mem-core/src/config.rs, cortex-mem-rig/src/lib.rs, examples/cortex-mem-tars/.gitignore, examples/cortex-mem-tars/Cargo.lock, examples/cortex-mem-tars/Cargo.toml, examples/cortex-mem-tars/src/config.rs, examples/cortex-mem-tars/src/infrastructure.rs, examples/cortex-mem-tars/src/lib.rs, examples/cortex-mem-tars/src/logger.rs
  Bot Configuration Structure
    · BotConfig Schema
    · Configuration Persistence (`bots.json`)
  Bot Lifecycle and State Management
    · State Machine Diagram
    · Agent Initialization
  Agent Isolation and Memory Scoping
    · Isolation Implementation
  Bot Management UI
    · UI Components
    · Keyboard Interaction (`KeyAction`)
  Password Protection
    · Implementation Details
  Default Bot Provisioning

## · Audio Integration API  (L4669)
  源文件: Cargo.lock, examples/cortex-mem-tars/.gitignore, examples/cortex-mem-tars/Cargo.lock, examples/cortex-mem-tars/Cargo.toml, examples/cortex-mem-tars/src/audio_input.rs, examples/cortex-mem-tars/src/audio_transcription.rs, examples/cortex-mem-tars/src/lib.rs, examples/cortex-mem-tars/src/logger.rs, examples/cortex-mem-tars/src/main.rs, examples/cortex-mem-tars/src/ui.rs
  Purpose and Scope
  Local Audio Capture System
    · Audio Capture Implementation
    · Local Transcription (Whisper)
  API Server Architecture
  Operating Modes
    · Store Mode
    · Chat Mode
  API Endpoints
    · Health Check
    · Store Memory
    · Retrieve Memory
    · List Memory
  Bot ID Management and Memory Isolation
  Logging and Monitoring

## · Integration Guides  (L4904)
  源文件: cortex-mem-cli/README.md, cortex-mem-cli/tests/cli_commands_test.rs, cortex-mem-config/README.md, cortex-mem-core/README.md, cortex-mem-core/src/filesystem/operations.rs, cortex-mem-mcp/README.md, cortex-mem-mcp/src/main.rs, cortex-mem-rig/README.md, cortex-mem-service/README.md, cortex-mem-tools/README.md, cortex-mem-tools/src/errors.rs, cortex-mem-tools/src/lib.rs
  Integration Methods Overview
  Integration Architecture
    · Architecture Diagram: Code Entity Mapping
    · Key Architectural Components
  The Shared Tools Layer
    · Tiered Access Architecture
    · Standard Operation Flow
  Choosing an Integration Method
    · Decision Matrix
    · Integration Comparison
  Common Integration Concepts
    · Tenant and User Isolation
    · URI Scheme (`cortex://`)
  Next Steps

## · RIG Framework Integration  (L5117)
  源文件: cortex-mem-cli/src/main.rs, cortex-mem-config/src/lib.rs, cortex-mem-core/src/config.rs, cortex-mem-core/src/filesystem/operations.rs, cortex-mem-mcp/src/main.rs, cortex-mem-rig/src/lib.rs, cortex-mem-tools/src/errors.rs, cortex-mem-tools/src/lib.rs, cortex-mem-tools/src/types.rs, examples/cortex-mem-tars/src/config.rs, examples/cortex-mem-tars/src/infrastructure.rs
  Purpose and Architecture
    · Integration Layer Architecture
    · Code Entity Mapping
  MemoryTools Collection
    · Available Tools
  Initialization and Configuration
    · Initialization Sequence
    · Multi-Tenant Setup
  Tool Registration and Usage
    · Agent Registration
    · Shared Argument Structures
  Data Flow: From Agent to Memory
  Autonomous Memory Usage

## · MCP Client Integration  (L5337)
  源文件: cortex-mem-cli/README.md, cortex-mem-cli/tests/cli_commands_test.rs, cortex-mem-config/README.md, cortex-mem-core/README.md, cortex-mem-core/src/filesystem/operations.rs, cortex-mem-mcp/README.md, cortex-mem-mcp/skill/SKILL.md, cortex-mem-mcp/src/main.rs, cortex-mem-rig/README.md, cortex-mem-service/README.md, cortex-mem-tools/README.md, cortex-mem-tools/src/errors.rs
  Overview
  Server Configuration
    · Command-Line Arguments
    · Initialization Sequence
  stdio Transport Protocol
  MCP Tool Definitions
    · Tool-to-Code Mapping
  Tool Details & Schemas
    · 1. store_memory
    · 2. query_memory
    · 3. get_abstract
  Request Processing Pipeline
  Client Integration Examples
    · Claude Desktop Configuration
    · Cursor IDE Configuration
  Usage Patterns
    · Autonomous Memory Extraction
    · Tiered Access (L0/L1/L2)

## · HTTP Client Integration  (L5630)
  源文件: cortex-mem-core/src/builder.rs, cortex-mem-core/src/embedding/client.rs, cortex-mem-insights/src/lib/api.ts, cortex-mem-insights/src/lib/pages/Dashboard.svelte, cortex-mem-insights/src/lib/pages/Search.svelte, cortex-mem-insights/src/lib/stores/search.ts, cortex-mem-insights/src/lib/stores/tenant.ts, cortex-mem-insights/src/lib/types.ts, cortex-mem-service/src/handlers/filesystem.rs, cortex-mem-service/src/handlers/mod.rs, cortex-mem-service/src/main.rs, cortex-mem-service/src/models.rs
  Connection Setup
    · Service Configuration
    · System Entity Mapping
  Authentication and Multi-Tenancy
    · Tenant Management
    · Security Configuration
  Request and Response Formats
    · Standard Response Envelope
  Core API Operations
    · 1. Semantic Search
    · 2. Filesystem Operations
    · 3. Session Management
  Error Handling
  Implementation Examples
    · TypeScript (Axios/Fetch Pattern)
    · Rust (Direct Integration via Core)
  Data Flow: Search Request

## · Direct Library Integration  (L5836)
  源文件: Cargo.toml, cortex-mem-cli/src/main.rs, cortex-mem-config/Cargo.toml, cortex-mem-config/src/lib.rs, cortex-mem-core/Cargo.toml, cortex-mem-core/src/config.rs, cortex-mem-core/src/lib.rs, cortex-mem-core/src/session/manager.rs, cortex-mem-mcp/Cargo.toml, cortex-mem-rig/Cargo.toml, cortex-mem-rig/src/lib.rs, cortex-mem-service/Cargo.toml
  Purpose and Scope
  Initialization Architecture
    · Component Relationship
    · Initialization Sequence
  Core Usage Patterns
    · Initializing MemoryOperations
    · Storing Memories (Asynchronous Layering)
    · Semantic Search
  Session Management
  Advanced Integration: TARS Pattern
    · Multi-Tenant Re-initialization
  Configuration Reference
  Summary of Key Functions

## · OpenClaw Plugin Integration  (L6130)
  源文件: examples/@memclaw/plugin/README.md, examples/@memclaw/plugin/README_zh.md, examples/@memclaw/plugin/dist/index.js, examples/@memclaw/plugin/dist/plugin-impl.d.ts, examples/@memclaw/plugin/dist/plugin-impl.d.ts.map, examples/@memclaw/plugin/dist/plugin-impl.js, examples/@memclaw/plugin/dist/plugin-impl.js.map, examples/@memclaw/plugin/dist/src/binaries.d.ts.map, examples/@memclaw/plugin/dist/src/binaries.js, examples/@memclaw/plugin/dist/src/binaries.js.map, examples/@memclaw/plugin/dist/src/config.d.ts, examples/@memclaw/plugin/dist/src/config.d.ts.map
  1. Plugin Architecture & Orchestration
    · System Orchestration Flow
    · Data & Code Entity Mapping
  2. Tool Exposure & Skills
    · Core Memory Tools
    · The `cortex://` URI Scheme
  3. Tiered Retrieval (L0/L1/L2)
  4. Configuration & Setup
    · Required Fields
    · Service Defaults
  5. Migration from Native Memory

## · Development & Testing  (L6307)
  源文件: .github/workflows/rust.yml, scripts/publish-crates.js
  Overview
  Evaluation Framework Architecture
  CI/CD and Publishing
    · Automated Testing
    · Workspace Publishing
  Child Pages

## · Evaluation Framework  (L6478)
  源文件: assets/benchmark/cortex_mem_vs_langmem.png, assets/benchmark/cortex_mem_vs_openclaw_1.png, assets/benchmark/cortex_mem_vs_openclaw_2.png, assets/benchmark/cortex_mem_vs_openclaw_3.png, assets/benchmark/evaluation_cortex_mem.webp, assets/benchmark/evaluation_langmem.webp, examples/locomo-evaluation/BENCHMARK.md, examples/locomo-evaluation/benchmark/BENCHMARK.md, examples/locomo-evaluation/benchmark/qa-s0-v5.judge.md
  Purpose and Scope
  System Architecture
    · Evaluation Logic vs. Code Entities
  Dataset: LoCoMo10
    · Dataset Composition
    · Question Categories
  Comparison Methodology
    · The Judging Process
    · Performance Visualization
    · Token Efficiency Analysis
  Benchmark Results (Summary)
    · Comparative Context
  Evaluation Artifacts

## · Evaluation Metrics  (L6640)
  源文件: assets/benchmark/cortex_mem_vs_openclaw_1.png, assets/benchmark/cortex_mem_vs_openclaw_2.png, assets/benchmark/cortex_mem_vs_openclaw_3.png, examples/locomo-evaluation/BENCHMARK.md, examples/locomo-evaluation/benchmark/BENCHMARK.md, examples/locomo-evaluation/benchmark/qa-s0-v5.judge.md
  Purpose and Scope
  LoCoMo10 Benchmark Metrics
    · LLM-as-a-Judge Scoring
    · Category Breakdown
    · Efficiency Metrics
  Recall Metrics (Retrieval Accuracy)
    · Precision and Recall at K
    · Ranking Metrics
    · Recall Metrics Calculation Flow
  Effectiveness Metrics (Processing Quality)
    · Fact Extraction & Classification
    · Importance & Deduplication
    · Natural Language to Code Entity Mapping
  Overall Scoring Weights
  Interpretation of Results

## · Architecture Decisions  (L6832)
  源文件: README.md, README_zh.md, cortex-mem-core/src/incremental_memory_updater.rs, cortex-mem-core/src/llm/prompts.rs, cortex-mem-core/src/search/vector_engine.rs, cortex-mem-service/src/handlers/automation.rs, cortex-mem-service/src/handlers/search.rs, cortex-mem-service/src/handlers/sessions.rs, cortex-mem-service/src/routes/automation.rs, cortex-mem-service/src/state.rs, examples/@memclaw/bin-darwin-arm64/bin/README.md, examples/locomo-evaluation/eval.py
  Purpose and Scope
  1. Modular Monolith & Crate Architecture
    · Decision: Multi-Crate Workspace Structure
  2. Model Context Protocol (MCP) Integration
    · Decision: Native MCP Support
  3. Layered Retrieval & Intent Analysis
    · Decision: Token-Efficient Tiered Search (L0/L1/L2)
  4. Event-Driven Incremental Updates
    · Decision: Decoupled Background Processing
  5. Generic Memory Processing
    · Decision: Trait-Based Memory Items
  6. Multi-Tenancy & Isolation
    · Decision: Directory and Collection Partitioning
  7. Memory Forgetting Mechanism
    · Decision: Ebbinghaus-Based Retention
  8. Technology Stack Decisions

## · Contributing Guidelines  (L7045)
  源文件: .github/workflows/rust.yml, cortex-mem-core/src/llm/mod.rs, litho.docs/en/1.Overview.md, litho.docs/en/5.Boundary-Interfaces.md, scripts/.gitignore, scripts/README.md, scripts/package.json, scripts/publish-crates.js, scripts/update-versions.js
  Repository Structure
    · Dependency Flow and Crate Hierarchy
  Development Automation Tools
    · 1. Version Management (`update-versions.js`)
    · 2. Publishing Pipeline (`publish-crates.js`)
  Code Standards & CI
    · Rust Standards
    · Mocking for Tests
  Testing Frameworks
    · Rust Unit & Integration Tests
    · Evaluation Framework (`lomoco-evaluation`)
  PR Process

## · API Reference  (L7200)
  源文件: cortex-mem-cli/Cargo.toml, cortex-mem-cli/src/commands/add.rs, cortex-mem-cli/src/commands/delete.rs, cortex-mem-cli/src/commands/get.rs, cortex-mem-cli/src/commands/layers.rs, cortex-mem-cli/src/commands/list.rs, cortex-mem-cli/src/commands/mod.rs, cortex-mem-cli/src/commands/search.rs, cortex-mem-cli/src/commands/session.rs, cortex-mem-cli/src/commands/tenant.rs, cortex-mem-core/src/builder.rs, cortex-mem-core/src/embedding/client.rs
  API Surface Overview
    · API Comparison Matrix
  HTTP REST API (`cortex-mem-service`)
    · Key Features
  MCP Server (`cortex-mem-mcp`)
    · Auto-Triggering
  CLI Interface (`cortex-mem-cli`)
    · Command Groups
  Core Data Types & Interfaces
    · Memory Operations Bridge
    · Common Result Types
  API Flow: Semantic Search

## · HTTP API Endpoints  (L7408)
  源文件: README.md, README_zh.md, cortex-mem-core/src/builder.rs, cortex-mem-core/src/embedding/client.rs, cortex-mem-core/src/incremental_memory_updater.rs, cortex-mem-core/src/llm/prompts.rs, cortex-mem-core/src/search/vector_engine.rs, cortex-mem-insights/src/lib/api.ts, cortex-mem-insights/src/lib/pages/Dashboard.svelte, cortex-mem-insights/src/lib/pages/Search.svelte, cortex-mem-insights/src/lib/stores/search.ts, cortex-mem-insights/src/lib/stores/tenant.ts
  Purpose and Scope
  Service Architecture
    · Component Interaction
    · Multi-Tenancy and State
  Endpoint Reference
    · Health and Status
    · Session Management
    · Layered Search API
    · Filesystem Operations
    · Tenant and Automation
  Data Models
    · Search Result Schema
  Implementation Details
    · Rate Limiting (Embedding)
    · Intent Analysis
    · Event-Driven Updates

## · MCP Tool Definitions  (L7661)
  源文件: cortex-mem-cli/README.md, cortex-mem-cli/tests/cli_commands_test.rs, cortex-mem-config/README.md, cortex-mem-core/README.md, cortex-mem-core/src/filesystem/operations.rs, cortex-mem-mcp/README.md, cortex-mem-mcp/src/main.rs, cortex-mem-mcp/src/service.rs, cortex-mem-rig/README.md, cortex-mem-service/README.md, cortex-mem-tools/README.md, cortex-mem-tools/src/docs/commit.md
  Overview
  Tool Definition Architecture
    · Tool Schema Flow
    · Parameter Mapping Pipeline
  Core Tool Reference
    · 1. `store_memory`
    · 2. `query_memory`
    · 3. `list_memories`
    · 4. Tiered Access Tools (`get_abstract`, `get_memory`)
  Implementation Details
    · The `MemoryMcpService` Class
    · URI Normalization
  Usage Example (Agent Tool Call)

## · Core Types & Interfaces  (L7875)
  源文件: cortex-mem-core/src/automation/indexer.rs, cortex-mem-core/src/automation/layer_generator.rs, cortex-mem-core/src/automation/manager.rs, cortex-mem-core/src/automation/mod.rs, cortex-mem-core/src/automation/sync.rs, cortex-mem-core/src/cascade_layer_updater.rs, cortex-mem-core/src/filesystem/operations.rs, cortex-mem-core/src/layers/generator.rs, cortex-mem-core/src/layers/manager.rs, cortex-mem-core/src/llm/client.rs, cortex-mem-core/src/memory_event_coordinator.rs, cortex-mem-core/src/session/extraction.rs
  Memory Data Structures
    · Memory
    · MemoryMetadata
    · ContextLayer
  Filter and Query Types
    · Filters
  Trait Interfaces
    · LLMClient Trait
    · VectorStore Trait
  Event Coordination Types
    · MemoryEvent
  Shared Tool Types (`cortex-mem-tools`)
    · MemoryOperations
    · ExtractedMemories

## · CLI Command Reference  (L8155)
  源文件: cortex-mem-cli/Cargo.toml, cortex-mem-cli/src/commands/add.rs, cortex-mem-cli/src/commands/delete.rs, cortex-mem-cli/src/commands/get.rs, cortex-mem-cli/src/commands/layers.rs, cortex-mem-cli/src/commands/list.rs, cortex-mem-cli/src/commands/mod.rs, cortex-mem-cli/src/commands/search.rs, cortex-mem-cli/src/commands/session.rs, cortex-mem-cli/src/commands/tenant.rs, cortex-mem-cli/src/main.rs, cortex-mem-config/src/lib.rs
  Purpose and Scope
  CLI Architecture
  Global Options
  Command Reference
    · add
    · search
    · session
    · get
    · vector
  Data Flow: Session Closure
  Configuration & Environment
    · LLM Configuration
    · Qdrant Configuration

## · Configuration Reference  (L8395)
  源文件: Cargo.toml, cortex-mem-cli/src/main.rs, cortex-mem-config/Cargo.toml, cortex-mem-config/src/lib.rs, cortex-mem-core/Cargo.toml, cortex-mem-core/src/config.rs, cortex-mem-mcp/Cargo.toml, cortex-mem-rig/Cargo.toml, cortex-mem-rig/src/lib.rs, cortex-mem-service/Cargo.toml, cortex-mem-tools/Cargo.toml, examples/cortex-mem-tars/config.example.toml
  Purpose and Scope
  Configuration System Overview
  Configuration Structure Hierarchy
    · Configuration Entity Mapping
    · Configuration Sections Summary
  Configuration Loading and Initialization
    · Loading Pipeline
    · Data Directory Resolution
  Component-Specific Configurations
    · MemoryOperations Initialization
    · Bot Configuration (TARS)
  Related Documentation

## · Core Configuration  (L8572)
  源文件: cortex-mem-cli/src/main.rs, cortex-mem-config/src/lib.rs, cortex-mem-core/src/config.rs, cortex-mem-rig/src/lib.rs, examples/cortex-mem-tars/src/config.rs, examples/cortex-mem-tars/src/infrastructure.rs
  Configuration File Structure
  [qdrant] Section
    · Fields
    · Field Details
  [llm] Section
    · Fields
    · Field Details
  [embedding] Section
    · Fields
    · Field Details
  [cortex] Section
    · Fields
    · Field Details
  Data Flow & Component Initialization
  Summary of Defaults

## · Service Configuration  (L8767)
  源文件: Cargo.lock, cortex-mem-core/src/builder.rs, cortex-mem-core/src/embedding/client.rs, cortex-mem-insights/src/lib/api.ts, cortex-mem-insights/src/lib/pages/Dashboard.svelte, cortex-mem-insights/src/lib/pages/Search.svelte, cortex-mem-insights/src/lib/stores/search.ts, cortex-mem-insights/src/lib/stores/tenant.ts, cortex-mem-service/src/main.rs, examples/cortex-mem-tars/.gitignore, examples/cortex-mem-tars/Cargo.lock, examples/cortex-mem-tars/Cargo.toml
  Purpose and Scope
  HTTP Service Configuration
    · Configuration and CLI Priority
    · Service Initialization Flow
    · Router and Middleware
  Web Dashboard (Insights) Configuration
    · API Client Architecture
    · Search Configuration
  TARS Application & API Configuration
    · Logging and Monitoring
    · Audio and Transcription Configuration
  Optimization & Automation Settings
    · Automation Manager
    · Rate Limiting (Embedding)
  Service Startup and Exit

## · Environment Variables  (L8969)
  源文件: cortex-mem-cli/src/main.rs, cortex-mem-config/src/lib.rs, cortex-mem-core/src/config.rs, cortex-mem-core/src/filesystem/operations.rs, cortex-mem-mcp/src/main.rs, cortex-mem-rig/src/lib.rs, cortex-mem-tools/src/errors.rs, cortex-mem-tools/src/lib.rs, cortex-mem-tools/src/types.rs, examples/cortex-mem-tars/src/config.rs, examples/cortex-mem-tars/src/infrastructure.rs
  Purpose and Scope
  Configuration Precedence
    · Configuration Resolution Order
  Core System Variables
    · CORTEX_DATA_DIR
    · QDRANT_API_KEY
    · EMBEDDING_API_KEY / EMBEDDING_MODEL
  Service-Specific Variables
    · TARS_API_PORT
    · MCP Server CLI Flags as Environment Overrides
  Environment Variable Summary Table
  Deployment Scenarios
    · Local Development (CLI)
    · Docker Compose
    · MCP Integration
  Implementation Details: URI and Tenant Isolation

## · Bot Configuration  (L9177)
  源文件: Cargo.lock, cortex-mem-cli/src/main.rs, cortex-mem-config/src/lib.rs, cortex-mem-core/src/config.rs, cortex-mem-rig/src/lib.rs, examples/cortex-mem-tars/.gitignore, examples/cortex-mem-tars/Cargo.lock, examples/cortex-mem-tars/Cargo.toml, examples/cortex-mem-tars/src/config.rs, examples/cortex-mem-tars/src/infrastructure.rs, examples/cortex-mem-tars/src/lib.rs, examples/cortex-mem-tars/src/logger.rs
  Purpose and Scope
  Configuration File Location
    · File Search and Initialization Logic
    · Location Logic
    · Git Exclusion
  BotConfig Structure
    · Data Model
    · Field Definitions
    · Default Bot Generation
  ConfigManager Operations
  Bot Lifecycle Management (TUI)
    · UI State Integration
    · UI Components for Management
  Password Protection
    · Implementation Flow
  Integration with Cortex Memory
    · From Bot ID to Memory Isolation
    · Infrastructure vs. Bot Tenants

## · Deployment Guide  (L9416)
  源文件: README.md, README_zh.md, cortex-mem-core/src/builder.rs, cortex-mem-core/src/embedding/client.rs, cortex-mem-core/src/incremental_memory_updater.rs, cortex-mem-core/src/llm/prompts.rs, cortex-mem-core/src/search/vector_engine.rs, cortex-mem-insights/src/lib/api.ts, cortex-mem-insights/src/lib/pages/Dashboard.svelte, cortex-mem-insights/src/lib/pages/Search.svelte, cortex-mem-insights/src/lib/stores/search.ts, cortex-mem-insights/src/lib/stores/tenant.ts
  Deployment Architecture Overview
    · Component Deployment Model
    · Service Dependencies
  Prerequisites
    · Qdrant Vector Database
    · LLM API Access
  Configuration for Production
    · Configuration Resolution
    · Service Initialization
  Deployment Procedures
    · Service Deployment: `cortex-mem-service`
    · Web Dashboard: `cortex-mem-insights`
  Health and Monitoring
    · Health Check Endpoint
    · Search Performance Monitoring
  Verification and Testing
    · Post-Deployment Verification
  Service Orchestration
    · Multi-Service Topology

## · Docker Deployment  (L9660)
  源文件: README.md, README_zh.md, cortex-mem-core/src/builder.rs, cortex-mem-core/src/embedding/client.rs, cortex-mem-core/src/incremental_memory_updater.rs, cortex-mem-core/src/llm/prompts.rs, cortex-mem-core/src/search/vector_engine.rs, cortex-mem-insights/src/lib/api.ts, cortex-mem-insights/src/lib/pages/Dashboard.svelte, cortex-mem-insights/src/lib/pages/Search.svelte, cortex-mem-insights/src/lib/stores/search.ts, cortex-mem-insights/src/lib/stores/tenant.ts
  Purpose and Scope
  Deployment Architecture Overview
    · Multi-Service Docker Architecture
  Docker Compose Configuration
    · Complete Setup Example
  Service Container Configuration
    · cortex-mem-service Runtime State
    · Configuration Resolution
  Network and Service Discovery
    · Health Checks
  Volume Management and Persistence
    · Data Directory Structure
  Environment Variables and Secrets
    · Rate Limiting
  Troubleshooting Docker Deployments
    · Common Connection Issues
    · Reindexing Memories
    · Memory Event Coordination

## · Production Considerations  (L9928)
  源文件: README.md, README_zh.md, cortex-mem-core/src/incremental_memory_updater.rs, cortex-mem-core/src/llm/prompts.rs, cortex-mem-core/src/memory_cleanup.rs, cortex-mem-core/src/memory_index_manager.rs, cortex-mem-core/src/search/vector_engine.rs, cortex-mem-service/src/handlers/automation.rs, cortex-mem-service/src/handlers/search.rs, cortex-mem-service/src/handlers/sessions.rs, cortex-mem-service/src/routes/automation.rs, cortex-mem-service/src/state.rs
  1. System State & Initialization
    · Tenant Isolation Implementation
    · Component Lifecycle
  2. Search & Retrieval Optimization
    · Intent Analysis vs. Latency
    · Layered Search Logic
  3. Automated Memory Management
    · Incremental Updates
    · The Forgetting Mechanism
    · Event-Driven Architecture
  4. Production Entity Mapping
    · Logic Flow: Memory Ingestion to Retrieval
    · Multi-Tenant State Management
  5. Operations & Maintenance
    · Reindexing
    · Evaluation (LoCoMo)
    · Key Prompt Templates

## · Multi-Service Architecture  (L10088)
  源文件: cortex-mem-core/src/builder.rs, cortex-mem-core/src/embedding/client.rs, cortex-mem-core/src/lib.rs, cortex-mem-core/src/session/manager.rs, cortex-mem-insights/bun.lock, cortex-mem-insights/src/lib/api.ts, cortex-mem-insights/src/lib/pages/Dashboard.svelte, cortex-mem-insights/src/lib/pages/Search.svelte, cortex-mem-insights/src/lib/stores/search.ts, cortex-mem-insights/src/lib/stores/tenant.ts, cortex-mem-insights/svelte.config.js, cortex-mem-insights/vite.config.ts
  Service Topology and Interaction
    · System Architecture Overview
  Service Components
    · 1. HTTP API Service (`cortex-mem-service`)
    · 2. TARS Application (`cortex-mem-tars`)
    · 3. Insights Dashboard (`cortex-mem-insights`)
  Shared Infrastructure Coordination
    · The Memory Event Pipeline
  Configuration and Deployment
    · Shared Configuration
    · Port Allocation
  Code Entity Bridge: Multi-Service Interaction

## · Performance Optimization  (L10290)
  源文件: cortex-mem-core/src/cascade_layer_debouncer.rs, cortex-mem-core/src/llm_result_cache.rs
  1. Overview
  2. LLM Call Optimization
    · 2.1 Cascade Layer Debouncing
    · 2.2 LLM Result Caching
  3. Embedding and Vector Store Tuning
    · 3.1 Embedding Batch Configuration
    · 3.2 Vector Search Parameters
  4. Batch Processing Strategies
    · 4.1 Memory Addition Batching
    · 4.2 Rate Limiting
  5. Performance Monitoring and Benchmarking
    · 5.1 Cache Statistics
    · 5.2 Evaluation Framework

## · Glossary  (L10481)
  源文件: README.md, README_zh.md, cortex-mem-core/src/automation/layer_generator.rs, cortex-mem-core/src/automation/manager.rs, cortex-mem-core/src/cascade_layer_updater.rs, cortex-mem-core/src/filesystem/operations.rs, cortex-mem-core/src/incremental_memory_updater.rs, cortex-mem-core/src/layers/generator.rs, cortex-mem-core/src/layers/manager.rs, cortex-mem-core/src/lib.rs, cortex-mem-core/src/llm/client.rs, cortex-mem-core/src/llm/prompts.rs
  Architectural Layers (L0, L1, L2)
  Virtual File System (VFS) & `cortex://`
    · URI Structure
    · Code Entity Space: VFS Components
  Core Components
    · MemoryEventCoordinator
    · CascadeLayerUpdater
    · Tenant Isolation
  Domain Concepts
    · Ebbinghaus Forgetting Curve
    · Intent Analysis
    · MCP (Model Context Protocol)
    · RIG Framework
  Data Flow: From Interaction to Persistence