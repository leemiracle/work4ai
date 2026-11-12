# Skeleton: claw-code（35 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 7KB | 2 | ~3 | 13 |
| 2 | Getting Started | L131 | 8KB | 2 | ~2 | 21 |
| 3 | Repository Structure | L333 | 7KB | 2 | ~4 | 15 |
| 4 | Rust Implementation | L491 | 8KB | 2 | ~2 | 11 |
| 5 | CLI and REPL (claw-cli) | L648 | 9KB | 2 | ~2 | 24 |
| 6 | Slash Commands and Input Handling | L813 | 8KB | 3 | ~2 | 8 |
| 7 | Runtime and Conversation Engine | L983 | 9KB | 2 | ~2 | 13 |
| 8 | Session Management and Compaction | L1130 | 10KB | 2 | ~4 | 14 |
| 9 | System Prompt and Project Context | L1307 | 7KB | 2 | ~3 | 8 |
| 10 | API Client and Provider Abstraction | L1445 | 9KB | 2 | ~2 | 14 |
| 11 | Model Compatibility and Provider Routing | L1625 | 8KB | 2 | ~2 | 10 |
| 12 | Tool Execution Engine | L1783 | 9KB | 2 | ~1 | 9 |
| 13 | MCP Integration | L1951 | 9KB | 2 | ~4 | 10 |
| 14 | Plugin System | L2100 | 9KB | 3 | ~1 | 13 |
| 15 | Worker Boot and Lane System | L2267 | 9KB | 2 | ~0 | 16 |
| 16 | Recovery Recipes and Branch Management | L2433 | 7KB | 2 | ~3 | 7 |
| 17 | LSP Integration | L2567 | 8KB | 3 | ~3 | 6 |
| 18 | Compat Harness | L2723 | 9KB | 2 | ~3 | 10 |
| 19 | Policy Engine, Green Contract, and Approval Tokens | L2899 | 9KB | 2 | ~2 | 9 |
| 20 | Task Packet, Task Registry, and Team/Cron System | L3062 | 7KB | 2 | ~3 | 7 |
| 21 | Lane Events and Report Schema | L3213 | 8KB | 2 | ~2 | 11 |
| 22 | claw-analog: Lightweight Agent Harness | L3367 | 9KB | 2 | ~2 | 14 |
| 23 | claw-rag-service: Workspace RAG and Embedding Service | L3555 | 7KB | 2 | ~1 | 12 |
| 24 | Python Porting Workspace | L3709 | 7KB | 2 | ~2 | 14 |
| 25 | Python CLI and Query Engine | L3850 | 9KB | 3 | ~4 | 15 |
| 26 | Python Runtime and Subsystem Modules | L4091 | 8KB | 2 | ~4 | 14 |
| 27 | Parity Audit and Reference Data | L4242 | 10KB | 2 | ~2 | 13 |
| 28 | Python Commands and Tools Registries | L4411 | 8KB | 2 | ~2 | 9 |
| 29 | Configuration and Permissions | L4568 | 9KB | 2 | ~2 | 9 |
| 30 | Runtime Configuration (Rust) | L4708 | 9KB | 2 | ~5 | 5 |
| 31 | Permission Modes and OAuth | L4869 | 9KB | 2 | ~4 | 16 |
| 32 | Testing and CI | L5038 | 7KB | 2 | ~2 | 13 |
| 33 | Rust Test Suite | L5167 | 10KB | 2 | ~3 | 21 |
| 34 | Python Test Suite and CI Pipeline | L5328 | 10KB | 2 | ~2 | 18 |
| 35 | Glossary | L5495 | 10KB | 2 | ~2 | 38 |


## · Overview  (L6)
  源文件: PHILOSOPHY.md, README.md, ROADMAP.md, USAGE.md, concept.md, docs/g011-acp-json-rpc-status-contract.md, docs/local-openai-compatible-providers.md, docs/navigation-file-context.md, docs/personal-assistant-roadmap.md, rust/README.md, rust/crates/commands/src/lib.rs, rust/crates/rusty-claude-cli/src/main.rs
  Dual-Track Architecture
    · 1. Production Rust Implementation (`rust/`)
    · 2. Python Porting Workspace (`src/`)
  Key Concepts
    · System Relationship Diagram
  Navigating the Wiki
    · Component Map: Natural Language to Code

## · Getting Started  (L131)
  源文件: .claw.json, .dockerignore, .github/scripts/check_release_readiness.py, .github/workflows/release.yml, .gitignore, README.md, USAGE.md, docker-compose.yml, docs/g009-windows-docs-release-verification-map.md, docs/g011-acp-json-rpc-status-contract.md, docs/local-openai-compatible-providers.md, docs/navigation-file-context.md
  Prerequisites
  Installation and Build
    · Rust CLI (Production)
    · Python Workspace (Porting)
  Environment Variables and Auth
  Workspace Configuration
    · CLAUDE.md / CLAW.md (Project Memory)
    · .claw.json
    · .claw/ Directory
  First-Run Experience: Project Initialization
    · Initialization Logic Flow
    · Implementation Details
  Running the System
    · Interactive REPL
    · One-Shot Prompts
    · Container / Docker Workflow

## · Repository Structure  (L333)
  源文件: PARITY.md, README.md, USAGE.md, docs/g007-plugin-mcp-verification-map.md, docs/g011-acp-json-rpc-status-contract.md, docs/local-openai-compatible-providers.md, docs/navigation-file-context.md, rust/Cargo.toml, rust/MOCK_PARITY_HARNESS.md, rust/README.md, rust/crates/mock-anthropic-service/src/lib.rs, rust/crates/rusty-claude-cli/build.rs
  Top-Level Directory Layout
  Rust Workspace (Production)
    · Crate Graph and Data Flow
    · Key Rust Crates
  Clean-Room Methodology and Parity Tracking
    · Parity Audit System
  Data Flow: Input to Execution
  Workspace Health and Initialization

## · Rust Implementation  (L491)
  源文件: README.md, ROADMAP.md, USAGE.md, docs/g011-acp-json-rpc-status-contract.md, docs/local-openai-compatible-providers.md, docs/navigation-file-context.md, rust/Cargo.toml, rust/README.md, rust/crates/commands/src/lib.rs, rust/crates/rusty-claude-cli/src/main.rs, rust/crates/rusty-claude-cli/tests/output_format_contract.rs
    · Crate Collaboration Map
    · Core Subsystems
    · Code Entity Mapping
    · Crate Dependency Summary

## · CLI and REPL (claw-cli)  (L648)
  源文件: .claw.json, .gitignore, ROADMAP.md, rust/.claude/sessions/session-1775010333630.json, rust/.claude/sessions/session-1775010384918.json, rust/.claude/sessions/session-1775010909274.json, rust/.claude/sessions/session-1775011146355.json, rust/.claude/sessions/session-1775011562247.json, rust/.claw.json, rust/.gitignore, rust/.omc/plans/tui-enhancement-plan.md, rust/.sandbox-home/.rustup/settings.toml
  Core Architecture
    · CLI Lifecycle and Argument Parsing
    · System Component Map
  Session Management
  Input Handling and Line Editor
    · Multi-line and Shortcuts
    · Completion and Help
  Terminal Rendering
    · Visual Feedback
  Project Initialization
  Command Flow Diagram

## · Slash Commands and Input Handling  (L813)
  源文件: ROADMAP.md, rust/crates/commands/Cargo.toml, rust/crates/commands/src/lib.rs, rust/crates/rusty-claude-cli/src/main.rs, rust/crates/rusty-claude-cli/tests/cli_flags_and_config_defaults.rs, rust/crates/rusty-claude-cli/tests/compact_output.rs, rust/crates/rusty-claude-cli/tests/output_format_contract.rs, rust/crates/rusty-claude-cli/tests/resume_slash_commands.rs
  Slash Command Architecture
    · Command Definition and Categories
    · The SlashCommand Enum
  Input Handling and Line Editing
    · LineEditor and SlashCommandHelper
    · Multi-line Input and Tab Completion
  Command Execution Data Flow
  Specialized Handlers and Helpers
    · Plugin and MCP Management
    · Git and Workspace Workflow
    · Session Control and Compaction
    · JSON Output for Automation

## · Runtime and Conversation Engine  (L983)
  源文件: rust/crates/compat-harness/src/lib.rs, rust/crates/runtime/src/compact.rs, rust/crates/runtime/src/config.rs, rust/crates/runtime/src/config_validate.rs, rust/crates/runtime/src/conversation.rs, rust/crates/runtime/src/file_ops.rs, rust/crates/runtime/src/lib.rs, rust/crates/runtime/src/oauth.rs, rust/crates/runtime/src/prompt.rs, rust/crates/runtime/src/session.rs, rust/crates/runtime/src/summary_compression.rs, rust/crates/runtime/src/usage.rs
  Core Architecture
    · Runtime Data Flow
  Session Management and Compaction
    · Token Usage and Pricing
  System Prompt and Project Context
    · Context Discovery Logic
  Tool and MCP Integration
  Public API Overview

## · Session Management and Compaction  (L1130)
  源文件: rust/crates/compat-harness/src/lib.rs, rust/crates/runtime/src/bash.rs, rust/crates/runtime/src/bash_validation.rs, rust/crates/runtime/src/compact.rs, rust/crates/runtime/src/conversation.rs, rust/crates/runtime/src/file_ops.rs, rust/crates/runtime/src/oauth.rs, rust/crates/runtime/src/prompt.rs, rust/crates/runtime/src/recovery_recipes.rs, rust/crates/runtime/src/session.rs, rust/crates/runtime/src/session_control.rs, rust/crates/runtime/src/trident.rs
  Session Data Model
    · Key Entities
    · Serialization and Persistence
  Token Usage and Pricing
    · Token Tracking
    · Pricing Tiers
    · Cost Estimation
  Session Compaction
    · Compaction Logic
    · Trident Compaction Pipeline
    · Boundary Protection
  Workspace Isolation and Session Store
    · SessionStore Architecture
    · Key Operations

## · System Prompt and Project Context  (L1307)
  源文件: rust/crates/runtime/src/bootstrap.rs, rust/crates/runtime/src/compact.rs, rust/crates/runtime/src/conversation.rs, rust/crates/runtime/src/git_context.rs, rust/crates/runtime/src/oauth.rs, rust/crates/runtime/src/prompt.rs, rust/crates/runtime/src/session.rs, rust/crates/runtime/src/sse.rs
  SystemPromptBuilder Architecture
    · Composition Order
    · Data Flow: Context to Prompt
  Project Context Discovery
    · Instruction File Discovery
    · Budgeting and Deduplication
  Git and LSP Enrichment
    · Git Integration
    · Context Limits for Large Diffs
  Key Implementation Details

## · API Client and Provider Abstraction  (L1445)
  源文件: rust/crates/api/src/client.rs, rust/crates/api/src/error.rs, rust/crates/api/src/http_client.rs, rust/crates/api/src/lib.rs, rust/crates/api/src/prompt_cache.rs, rust/crates/api/src/providers/anthropic.rs, rust/crates/api/src/providers/mod.rs, rust/crates/api/src/providers/openai_compat.rs, rust/crates/api/src/sse.rs, rust/crates/api/src/types.rs, rust/crates/api/tests/client_integration.rs, rust/crates/api/tests/openai_compat_integration.rs
  Provider Abstraction Layer
    · ProviderClient Enum
    · The Provider Trait
    · Data Flow: Request to Provider
  Model Alias Resolution and Detection
  Authentication and AuthSource
    · OAuth and Token Management
  Stream Normalization and SSE Parsing
    · MessageStream Normalization
    · SseParser
  OpenAI-Compatible Client Support
  Prompt Caching
  Error Handling and Retries

## · Model Compatibility and Provider Routing  (L1625)
  源文件: docs/MODEL_COMPATIBILITY.md, prd.json, progress.txt, rust/crates/api/benches/request_building.rs, rust/crates/api/src/error.rs, rust/crates/api/src/providers/anthropic.rs, rust/crates/api/src/providers/mod.rs, rust/crates/api/src/providers/openai_compat.rs, rust/crates/api/tests/openai_compat_integration.rs, rust/crates/api/tests/provider_client_integration.rs
  Overview
    · Request Flow and Entity Mapping
  Model-Specific Handling
    · Reasoning Models and Parameter Stripping
    · Kimi and DashScope Routing
    · GPT-5 Token Handling
  Local Providers and Custom Gateways
    · Local Provider Setup (Ollama, vLLM)
    · Custom Gateway Support
  Provider Diagnostics and Routing
    · Summary Table: Model Compatibility Logic

## · Tool Execution Engine  (L1783)
  源文件: .claude/sessions/session-1775007846522.json, rust/Cargo.lock, rust/crates/rusty-claude-cli/Cargo.toml, rust/crates/rusty-claude-cli/src/input.rs, rust/crates/tools/Cargo.toml, rust/crates/tools/GIT_TOOLS_README.md, rust/crates/tools/src/lib.rs, rust/crates/tools/src/pdf_extract.rs, rust/crates/tools/tests/path_scope_enforcement.rs
  Tool Registry and Management
    · GlobalToolRegistry
  Tool Execution Pipeline
    · Dispatch Logic
    · Data Flow: Natural Language to Tool Execution
  Permission Modes and Security
    · Permission Gating
  Core Capabilities
    · Git-Aware Context Tools
    · Shell Execution (`bash`)
    · File Operations
    · PDF Extraction
    · Sub-agent Spawning
  Skill System
    · Registry Singletons

## · MCP Integration  (L1951)
  源文件: .github/scripts/check_doc_source_of_truth.py, docs/g007-mcp-lifecycle-mapping.md, rust/crates/api/Cargo.toml, rust/crates/runtime/Cargo.toml, rust/crates/runtime/src/branch_lock.rs, rust/crates/runtime/src/lane_events.rs, rust/crates/runtime/src/mcp.rs, rust/crates/runtime/src/mcp_client.rs, rust/crates/runtime/src/mcp_server.rs, rust/crates/runtime/src/mcp_stdio.rs
  MCP Lifecycle and Management
    · Hardened Lifecycle Phases
    · Connection and Initialization
  Transports and Framing
    · Supported Transport Types
    · JSON-RPC Framing
  Tool Discovery and Routing
    · Naming Conventions
  Tool Execution Bridge
    · Timeouts and Handshakes
  Configuration and Permissions
    · Scoped Configuration and Hashing
    · Permission Enforcement

## · Plugin System  (L2100)
  源文件: rust/PARITY.md, rust/crates/plugins/Cargo.toml, rust/crates/plugins/bundled/example-bundled/.claude-plugin/plugin.json, rust/crates/plugins/bundled/example-bundled/hooks/post.sh, rust/crates/plugins/bundled/example-bundled/hooks/pre.sh, rust/crates/plugins/bundled/sample-hooks/.claude-plugin/plugin.json, rust/crates/plugins/bundled/sample-hooks/hooks/post.sh, rust/crates/plugins/bundled/sample-hooks/hooks/pre.sh, rust/crates/plugins/src/hooks.rs, rust/crates/plugins/src/lib.rs, rust/crates/plugins/src/test_isolation.rs, rust/crates/runtime/src/hooks.rs
  Plugin Architecture and Types
    · Data Flow: Plugin Discovery to Registry
  Plugin Manifest Schema
    · Key Manifest Components
  Hook Execution System
    · Hook Events
    · Hook Runtime Environment
  Plugin Lifecycle and Health
    · Plugin States
    · Lifecycle Control
  Implementation Details
    · Registry Management
    · Test Isolation
    · Bundled Examples

## · Worker Boot and Lane System  (L2267)
  源文件: .github/scripts/check_doc_source_of_truth.py, rust/crates/api/Cargo.toml, rust/crates/claw-analog/src/lib.rs, rust/crates/runtime/Cargo.toml, rust/crates/runtime/src/bash.rs, rust/crates/runtime/src/bash_validation.rs, rust/crates/runtime/src/branch_lock.rs, rust/crates/runtime/src/lane_events.rs, rust/crates/runtime/src/mcp.rs, rust/crates/runtime/src/mcp_client.rs, rust/crates/runtime/src/mcp_stdio.rs, rust/crates/runtime/src/recovery_recipes.rs
  Worker Boot State Machine
    · Worker Status Transitions
    · Diagram: Worker Lifecycle and Code Entities
  Trust Resolution and Misdelivery Recovery
    · TrustResolver and Tool Permissions
    · Prompt-Misdelivery Detection and Recovery
    · Startup Evidence
  Lane Event System
    · Key Event Types (`LaneEventName`)
    · Failure Taxonomy
  SessionStore and Workspace Isolation
    · Workspace Fingerprinting
    · SessionControl and Error Taxonomy
    · Diagram: Session Resolution Flow
  Recovery Recipes and Branch Management

## · Recovery Recipes and Branch Management  (L2433)
  源文件: rust/crates/runtime/src/bash.rs, rust/crates/runtime/src/bash_validation.rs, rust/crates/runtime/src/recovery_recipes.rs, rust/crates/runtime/src/session_control.rs, rust/crates/runtime/src/stale_base.rs, rust/crates/runtime/src/trident.rs, rust/crates/runtime/src/worker_boot.rs
  Recovery Recipes
    · Canonical Failure Scenarios
    · Recovery Steps and Policy
    · Data Flow: Failure to Recovery
  Branch Management and Freshness
    · StaleBase Divergence Guard
    · Session Isolation and Workspace Root
    · Git Operation Monitoring
  Safety and Validation

## · LSP Integration  (L2567)
  源文件: rust/crates/runtime/src/lsp_client.rs, rust/crates/runtime/src/mcp_tool_bridge.rs, rust/crates/runtime/src/permission_enforcer.rs, rust/crates/runtime/src/plugin_lifecycle.rs, rust/crates/runtime/src/stale_branch.rs, rust/crates/runtime/src/team_cron_registry.rs
  Architecture Overview
    · Data Flow: Natural Language to Code Entity Space
  Key Components
    · LspRegistry
    · LspAction
    · LspServerState
  Transport and Protocol
    · JSON-RPC Framing
  Data Structures
  Global Registry and Tool Integration

## · Compat Harness  (L2723)
  源文件: PARITY.md, docs/g007-plugin-mcp-verification-map.md, rust/MOCK_PARITY_HARNESS.md, rust/crates/compat-harness/src/lib.rs, rust/crates/mock-anthropic-service/src/lib.rs, rust/crates/runtime/src/file_ops.rs, rust/crates/runtime/src/usage.rs, rust/crates/rusty-claude-cli/tests/mock_parity_harness.rs, rust/mock_parity_scenarios.json, rust/scripts/run_mock_parity_diff.py
  Upstream Path Resolution
    · Resolution Heuristics
  Extraction Engine
    · Command Extraction
    · Tool Extraction
    · Bootstrap Plan Extraction
  Data Flow: Source to Manifest
    · Extraction Pipeline
  Entity Mapping: TypeScript to Rust
    · System Entity Mapping
  Implementation Details
    · Heuristic Parsers
    · Manifest Deduplication
    · Integration with Parity Audits

## · Policy Engine, Green Contract, and Approval Tokens  (L2899)
  源文件: docs/g004-events-reports-contract.md, rust/crates/runtime/src/approval_tokens.rs, rust/crates/runtime/src/g004_conformance.rs, rust/crates/runtime/src/green_contract.rs, rust/crates/runtime/src/permissions.rs, rust/crates/runtime/src/policy_engine.rs, rust/crates/runtime/tests/fixtures/g004_contract_bundle.valid.json, rust/crates/runtime/tests/g004_conformance.rs, rust/crates/runtime/tests/integration_tests.rs
  Policy Engine Architecture
    · Core Types
    · Evaluation Flow
    · Policy Engine Mapping: Natural Language to Code
  Green Contract and Evidence Assessment
    · Green Levels
    · Evidence Evaluation
  Approval Tokens
    · Token Lifecycle and Status
    · Approval Scope and Delegation
    · Token Ledger
    · Approval Token Data Flow
  G004 Conformance Harness
    · Validation Logic
    · Conformance Entities

## · Task Packet, Task Registry, and Team/Cron System  (L3062)
  源文件: docs/g005-branch-recovery-verification-map.md, docs/g006-task-policy-board-verification-map.md, rust/crates/runtime/src/mcp_lifecycle_hardened.rs, rust/crates/runtime/src/task_packet.rs, rust/crates/runtime/src/task_registry.rs, rust/crates/rusty-claude-cli/.claw/sessions/session-newer.jsonl, rust/crates/tools/src/lane_completion.rs
  TaskPacket Schema
    · Core Structure
    · Validation Logic
  TaskRegistry and Lifecycle
    · Task Status Transitions
    · Lane Board and Heartbeats
    · Task Registry Flow
  Lane Completion and Reporting
    · Detection Heuristics
    · Policy Evaluation
  Team and Cron Systems
    · System Entity Mapping
    · Key Components

## · Lane Events and Report Schema  (L3213)
  源文件: .github/scripts/check_doc_source_of_truth.py, docs/g004-events-reports-verification-map.md, rust/crates/api/Cargo.toml, rust/crates/runtime/Cargo.toml, rust/crates/runtime/src/branch_lock.rs, rust/crates/runtime/src/lane_events.rs, rust/crates/runtime/src/mcp.rs, rust/crates/runtime/src/mcp_client.rs, rust/crates/runtime/src/mcp_stdio.rs, rust/crates/runtime/src/report_schema.rs, rust/crates/runtime/tests/fixtures/report_schema_v1/README.md
  Lane Events System
    · LaneEventName Enum
    · LaneEventStatus and Failure Classification
    · Event Metadata and Provenance
    · Session Identity
  Canonical Report V1 Schema
    · Report Claims and Confidence
    · Negative Evidence
    · Field Deltas
    · Projection and Redaction
    · Data Flow: From Event to Report
  Implementation Details
    · Report Schema Registry
    · Fixtures and Validation
    · Mapping Code Entities to Concepts
    · Verification and Compliance

## · claw-analog: Lightweight Agent Harness  (L3367)
  源文件: README.md, USAGE.md, docs/g011-acp-json-rpc-status-contract.md, docs/local-openai-compatible-providers.md, docs/navigation-file-context.md, how_to_run.md, rust/README.md, rust/crates/claw-analog/Cargo.toml, rust/crates/claw-analog/src/agents.rs, rust/crates/claw-analog/src/config_cmd.rs, rust/crates/claw-analog/src/doctor.rs, rust/crates/claw-analog/src/lib.rs
  Overview and Purpose
    · Key Differences from claw CLI
  Configuration and .claw-analog.toml
    · AnalogFileConfig Schema
    · Profile Integration
  Agent Loop and Presets
    · Preset Modes
    · Permission Enforcement
  Tooling and RAG Integration
    · retrieve_context (RAG)
    · Multi-Agent Workflows
  Preflight and Diagnostics
    · The doctor Command
    · NDJSON Output Contract
  Data Flow Diagrams
    · Configuration Merging and Resolution
    · Non-Interactive Execution Loop

## · claw-rag-service: Workspace RAG and Embedding Service  (L3555)
  源文件: docs/rag-web-ui.md, rust/crates/claw-rag-service/Cargo.toml, rust/crates/claw-rag-service/Dockerfile, rust/crates/claw-rag-service/src/chunk.rs, rust/crates/claw-rag-service/src/db.rs, rust/crates/claw-rag-service/src/embed.rs, rust/crates/claw-rag-service/src/ingest.rs, rust/crates/claw-rag-service/src/lib.rs, rust/crates/claw-rag-service/src/main.rs, rust/crates/claw-rag-service/src/qdrant_index.rs, rust/crates/claw-rag-service/src/search.rs, rust/crates/claw-rag-service/static/index.html
  Architecture Overview
    · System Interaction Diagram
  Ingestion Pipeline
    · Ingestion Data Flow
    · Key Ingestion Components
  Embedding and Search
    · EmbedConfig
    · Search Execution
  Storage Backends
    · SQLite + sqlite-vec (Default)
    · Qdrant (Optional)
  HTTP API and Web UI
    · API Endpoints
    · Manual Index Inspection

## · Python Porting Workspace  (L3709)
  源文件: src/__init__.py, src/commands.py, src/context.py, src/history.py, src/main.py, src/models.py, src/path_scope.py, src/permissions.py, src/query_engine.py, src/runtime.py, src/setup.py, src/tools.py
  Architecture and Role
    · System Mapping: Logic to Code
  CLI and Query Engine
  Runtime and Subsystem Modules
  Parity Audit and Reference Data
  Commands and Tools Registries
    · Data Flow: Request Execution
  Workspace Summary

## · Python CLI and Query Engine  (L3850)
  源文件: assets/omx/omx-readme-review-1.png, assets/omx/omx-readme-review-2.png, src/QueryEngine.py, src/Tool.py, src/__init__.py, src/context.py, src/history.py, src/main.py, src/models.py, src/path_scope.py, src/permissions.py, src/query_engine.py
  CLI Entrypoint and Subcommands
    · Primary Subcommands
    · Command Logic Flow
  Query Engine Orchestration
    · Key Classes and Data Structures
    · Message Submission Pipeline
    · CLI to Query Engine Mapping
  Session Persistence and Transcript Compaction
    · Session Persistence
    · Transcript Compaction
  Path Scoping and Permissions
    · Path Validation Logic
  Workspace Setup and Runtime Session
    · Workspace Setup Sequence
    · Runtime Session Reports

## · Python Runtime and Subsystem Modules  (L4091)
  源文件: src/assistant/__init__.py, src/bootstrap/__init__.py, src/bridge/__init__.py, src/buddy/__init__.py, src/cli/__init__.py, src/commands.py, src/components/__init__.py, src/constants/__init__.py, src/coordinator/__init__.py, src/entrypoints/__init__.py, src/hooks/__init__.py, src/keybindings/__init__.py
  The PortRuntime and Session Management
    · PortRuntime and RuntimeSession
    · QueryEnginePort and Persistence
    · Data Flow: Prompt to Execution
  Subsystem Modules (The "Mirror" Packages)
    · Structure of a Subsystem Stub
  Workspace Setup and Prefetching
    · Setup and Prefetching
  Runtime Context and Environment

## · Parity Audit and Reference Data  (L4242)
  源文件: PARITY.md, docs/g007-plugin-mcp-verification-map.md, rust/MOCK_PARITY_HARNESS.md, rust/crates/mock-anthropic-service/src/lib.rs, rust/crates/rusty-claude-cli/tests/mock_parity_harness.rs, rust/mock_parity_scenarios.json, rust/scripts/run_mock_parity_diff.py, src/models.py, src/path_scope.py, src/permissions.py, src/query_engine.py, src/tools.py
  Overview of Parity Tracking
    · Data Flow for Parity Verification
  Reference Data Structures
    · Scenario Manifest
    · Command and Tool Snapshots
  Behavioral Parity: The Mock Harness
    · Mock Anthropic Service
    · Scenario Execution
  Security and Workspace Scoping Parity
    · Workspace Path Scope
  Gap Analysis: `PARITY.md`
    · 9-Lane Checkpoint
    · Implementation Mapping (Natural Language to Code)
  Summary of Reference Files

## · Python Commands and Tools Registries  (L4411)
  源文件: src/commands.py, src/models.py, src/path_scope.py, src/permissions.py, src/query_engine.py, src/runtime.py, src/tools.py, tests/test_porting_workspace.py, tests/test_security_scope.py
  Data Loading and Snapshots
    · The PortingModule Dataclass
    · Registry Loading Flow
  Command Dispatch and Execution
    · Key Functions
    · CommandExecution Dataclass
  Tool Registry and Permissions
    · ToolPermissionContext and PathScope
    · Key Tool Functions
  Runtime Integration
    · Prompt Routing
    · Session Bootstrapping
    · Registry Utilities

## · Configuration and Permissions  (L4568)
  源文件: rust/crates/runtime/src/approval_tokens.rs, rust/crates/runtime/src/config.rs, rust/crates/runtime/src/config_validate.rs, rust/crates/runtime/src/g004_conformance.rs, rust/crates/runtime/src/lib.rs, rust/crates/runtime/src/permissions.rs, rust/crates/runtime/tests/fixtures/g004_contract_bundle.valid.json, rust/crates/runtime/tests/g004_conformance.rs, rust/crates/rusty-claude-cli/src/setup_wizard.rs
  System Architecture Overview
    · Data Flow and Configuration Hierarchy
  Runtime Configuration (Rust)
  Permission Modes and OAuth
    · Permission Modes and Policies
    · Authentication and OAuth
  System Prompt Context Integration
    · Policy Exceptions and G004 Conformance

## · Runtime Configuration (Rust)  (L4708)
  源文件: rust/crates/runtime/src/config.rs, rust/crates/runtime/src/config_validate.rs, rust/crates/runtime/src/lib.rs, rust/crates/runtime/src/sandbox.rs, rust/crates/rusty-claude-cli/src/setup_wizard.rs
  Configuration Hierarchy and Loading
    · Data Flow: Config Resolution
  RuntimeConfig Schema
    · Core Configuration Components
    · MCP Configuration Collection
  Security and Sandboxing
    · Filesystem Isolation
    · Validation and Diagnostics
  Integration with System Prompt
  Setup and Discovery
    · Setup Wizard
    · OAuth Configuration

## · Permission Modes and OAuth  (L4869)
  源文件: rust/crates/runtime/src/approval_tokens.rs, rust/crates/runtime/src/compact.rs, rust/crates/runtime/src/conversation.rs, rust/crates/runtime/src/g004_conformance.rs, rust/crates/runtime/src/lsp_client.rs, rust/crates/runtime/src/mcp_tool_bridge.rs, rust/crates/runtime/src/oauth.rs, rust/crates/runtime/src/permission_enforcer.rs, rust/crates/runtime/src/permissions.rs, rust/crates/runtime/src/plugin_lifecycle.rs, rust/crates/runtime/src/prompt.rs, rust/crates/runtime/src/session.rs
  Permission Modes
    · PermissionMode Enum
    · Enforcement and Policy
    · Tool-Specific Validation
    · Policy Exceptions and Approval Tokens
    · Entity Relationship: Permissions
  OAuth2 Authentication
    · PKCE Flow Implementation
    · Credential Storage
  API Client AuthSource
    · AuthSource Variants
    · Resolution and Refresh
    · Key Entities

## · Testing and CI  (L5038)
  源文件: .github/workflows/rust-ci.yml, PARITY.md, docs/g007-plugin-mcp-verification-map.md, rust/MOCK_PARITY_HARNESS.md, rust/crates/mock-anthropic-service/src/lib.rs, rust/crates/rusty-claude-cli/tests/mock_parity_harness.rs, rust/mock_parity_scenarios.json, rust/scripts/run_mock_parity_diff.py, scripts/dogfood-probe.py, scripts/roadmap-check-ids.sh, scripts/roadmap-next-id.sh, tests/__init__.py
    · Testing Architecture Overview
    · Rust Test Suite
    · Python Test Suite
    · CI Pipeline Configuration

## · Rust Test Suite  (L5167)
  源文件: PARITY.md, docs/g007-plugin-mcp-verification-map.md, rust/MOCK_PARITY_HARNESS.md, rust/crates/mock-anthropic-service/Cargo.toml, rust/crates/mock-anthropic-service/src/lib.rs, rust/crates/mock-anthropic-service/src/main.rs, rust/crates/runtime/src/approval_tokens.rs, rust/crates/runtime/src/g004_conformance.rs, rust/crates/runtime/src/green_contract.rs, rust/crates/runtime/src/permissions.rs, rust/crates/runtime/src/policy_engine.rs, rust/crates/runtime/tests/fixtures/g004_contract_bundle.valid.json
  Overview of Testing Strategy
    · Data Flow in Integration Tests
  API Client Integration Tests
    · Key Test Files
  Mock Parity Harness
    · Scenario-Based Testing
    · Validated Scenarios
  Runtime Integration Tests
    · Policy and Lane Evaluation
    · G004 Conformance Tests
  CLI and Resume Tests
  Compact Output Tests
  Workflow: Cargo Test
    · Execution Commands
    · CI Integration

## · Python Test Suite and CI Pipeline  (L5328)
  源文件: .github/ISSUE_TEMPLATE/anti_slop_triage.yml, .github/PULL_REQUEST_TEMPLATE.md, .github/hooks/pre-push, .github/workflows/rust-ci.yml, CONTRIBUTING.md, docs/anti-slop-triage.md, docs/g013-roadmap-pinpoints-693-695-verification-map.md, docs/pr-issue-resolution-gate.md, docs/pr-triage-g012-final-gate.json, scripts/dogfood-probe.py, scripts/roadmap-check-ids.sh, scripts/roadmap-next-id.sh
  Python Porting Workspace Test Suite
    · Manifest and Subsystem Validation
    · Parity Audit Validation
    · Subprocess and CLI Tests
  Rust CI and Development Gates
    · Local Pre-Push Hook
    · ROADMAP ID Management
  GitHub Actions CI Pipeline
    · Documentation and Metadata Gates
    · Windows Smoke Testing
    · PR and Issue Resolution Gate
  Summary of Test Coverage

## · Glossary  (L5495)
  源文件: .github/scripts/check_doc_source_of_truth.py, README.md, ROADMAP.md, USAGE.md, docs/g011-acp-json-rpc-status-contract.md, docs/local-openai-compatible-providers.md, docs/navigation-file-context.md, rust/PARITY.md, rust/README.md, rust/crates/api/Cargo.toml, rust/crates/claw-analog/src/lib.rs, rust/crates/claw-rag-service/src/db.rs
  Core Domain Concepts
    · Harness
    · Session
    · Compaction
  Technical Jargon & Abbreviations
  System Architecture Diagrams
    · Natural Language to Code Entity Mapping: Input Flow
    · Code Entity Mapping: Tool Execution Pipeline
  Recovery & Reliability Terms
    · Recovery Recipe
    · Failure Scenario
    · Worker Status
    · Permission Modes
    · Startup Evidence Bundle
    · Plugin Hooks