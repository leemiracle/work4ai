# Skeleton: aden-hive（31 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 14KB | 3 | ~10 | 38 |
| 2 | Getting Started | L336 | 11KB | 3 | ~14 | 10 |
| 3 | Environment Setup (Linux and macOS) | L655 | 11KB | 3 | ~13 | 10 |
| 4 | Environment Setup (Windows) | L1023 | 12KB | 3 | ~13 | 2 |
| 5 | Configuration Reference | L1365 | 14KB | 3 | ~25 | 18 |
| 6 | Architecture | L1809 | 22KB | 3 | ~13 | 28 |
| 7 | Agent Runtime and Execution Streams | L2215 | 23KB | 6 | ~20 | 30 |
| 8 | Graph Executor and Node Execution | L2747 | 24KB | 4 | ~37 | 22 |
| 9 | Event Loop Node | L3276 | 18KB | 5 | ~17 | 18 |
| 10 | Graph Primitives: Nodes, Edges, and Goals | L3687 | 20KB | 7 | ~28 | 12 |
| 11 | LLM Providers | L4239 | 15KB | 5 | ~18 | 4 |
| 12 | Conversation and Memory Management | L4606 | 17KB | 4 | ~19 | 8 |
| 13 | Output Validation | L5035 | 16KB | 4 | ~12 | 16 |
| 14 | Storage and Observability | L5449 | 19KB | 5 | ~41 | 18 |
| 15 | MCP Integration | L5964 | 12KB | 4 | ~5 | 22 |
| 16 | MCP Client and Tool Registry | L6247 | 14KB | 4 | ~11 | 6 |
| 17 | Agent Builder MCP Server | L6597 | 17KB | 4 | ~16 | 16 |
| 18 | Credential Management | L7113 | 17KB | 4 | ~16 | 22 |
| 19 | Credential Validation and Interactive Setup | L7491 | 15KB | 4 | ~5 | 9 |
| 20 | Aden Platform Credential Sync | L7815 | 19KB | 4 | ~27 | 13 |
| 21 | Tools Reference | L8279 | 21KB | 4 | ~37 | 28 |
| 22 | Email and Gmail Tools | L8722 | 16KB | 4 | ~25 | 7 |
| 23 | Web Search and Research Tools | L9174 | 17KB | 4 | ~22 | 25 |
| 24 | Terminal User Interface (TUI) | L9604 | 20KB | 7 | ~19 | 8 |
| 25 | Agent Development Guide | L10094 | 16KB | 3 | ~22 | 22 |
| 26 | Building Agents with Claude Skills | L10431 | 19KB | 5 | ~35 | 8 |
| 27 | Testing Framework | L10980 | 17KB | 5 | ~18 | 23 |
| 28 | Agent Examples and Recipes | L11386 | 18KB | 6 | ~29 | 23 |
| 29 | IDE Integration | L11841 | 9KB | 2 | ~7 | 5 |
| 30 | Contributing | L12113 | 12KB | 3 | ~19 | 10 |
| 31 | GitHub Automation and CI/CD | L12520 | 14KB | 6 | ~14 | 13 |


## · Overview  (L6)
  源文件: README.md, core/README.md, core/framework/graph/event_loop_node.py, core/framework/graph/executor.py, core/framework/graph/node.py, core/framework/runner/runner.py, core/framework/runtime/agent_runtime.py, core/framework/runtime/execution_stream.py, docs/agent_runtime.md, docs/architecture/README.md, docs/configuration.md, docs/contributing-lint-setup.md
  What Is Hive?
  Who Is Hive For?
  Core Concepts
  Top-Level Architecture
  Request Execution Flow
  Repository Structure
  Major Subsystems at a Glance
  The Goal-Execution Loop
  LLM Provider Support
  Key Design Decisions

## · Getting Started  (L336)
  源文件: CONTRIBUTING.md, README.md, docs/architecture/README.md, docs/contributing-lint-setup.md, docs/developer-guide.md, docs/environment-setup.md, docs/getting-started.md, docs/roadmap.md, package.json, quickstart.sh
  Prerequisites
  Installation
  What `quickstart.sh` Does
  Workspace Package Layout
  Verifying the Installation
  Configuring an LLM Provider
  Running Your First Agent
    · Using the TUI (Recommended)
    · Running an Agent Directly
    · Interactive Shell
    · CLI Command Reference
  Building Your First Agent
    · Claude Code
    · Codex CLI
    · Opencode
  Windows
  Common Troubleshooting

## · Environment Setup (Linux and macOS)  (L655)
  源文件: CONTRIBUTING.md, README.md, docs/architecture/README.md, docs/contributing-lint-setup.md, docs/developer-guide.md, docs/environment-setup.md, docs/getting-started.md, docs/roadmap.md, package.json, quickstart.sh
  Prerequisites
  Running the Wizard
  Wizard Step Map
  Step 1: Python Detection and `uv` Installation
    · `uv` Installation
  Step 2: Package Installation
  Step 3: Verify Python Imports
  LLM Provider Configuration
    · Provider Selection Flow
    · Supported Providers
    · Model Selection
    · Shell RC File Detection
  `~/.hive/configuration.json` — Output Structure
  Verification Commands
  Manual Setup (Alternative to `quickstart.sh`)
  Troubleshooting
  Next Steps

## · Environment Setup (Windows)  (L1023)
  源文件: hive.ps1, quickstart.ps1
  Prerequisites
  Running the Setup Wizard
  Setup Flow
  Step-by-Step Breakdown
    · Step 1 — Python Check
    · uv Installation
    · Step 2 — Package Installation
    · Step 2.5 — Windows Defender Exclusions (Optional)
    · Step 5 — LLM Provider Configuration
    · Step 6 — Credential Store Initialization
    · Step 7 — Import Verification
    · Step 8 — CLI Wrapper
  The `hive.ps1` Runtime Wrapper
    · Why `hive.ps1` Is Needed
    · Runtime Startup Flow
    · Environment Variable Loading Detail
  Environment Variable Architecture
  After Setup
  Troubleshooting

## · Configuration Reference  (L1365)
  源文件: .gitignore, .mcp.json, .python-version, core/README.md, core/framework/agents/hive_coder/guardian.py, core/framework/agents/hive_coder/nodes/__init__.py, core/framework/agents/hive_coder/reference/anti_patterns.md, core/framework/config.py, docs/configuration.md, docs/i18n/es.md, docs/i18n/hi.md, docs/i18n/ja.md
  Configuration Layers
  Global Configuration File
    · File format
    · Fields
    · Helper functions
    · `RuntimeConfig` dataclass
  Environment Variables
    · LLM Provider Keys
    · Tool API Keys
    · Runtime Flags and Paths
  Per-Agent Configuration (`config.py`)
  Agent Graph Specification (`agent.json`)
    · Top-level structure
    · Key fields
    · Node spec fields (`NodeSpec`)
    · Edge spec fields (`EdgeSpec`)
  MCP Server Configuration (`.mcp.json`)
    · Repository-level `.mcp.json`
    · Per-agent `mcp_servers.json`
  Storage Layout
  IDE Source Root Setup
    · VS Code
    · PyCharm
  Configuration Summary Diagram

## · Architecture  (L1809)
  源文件: README.md, core/framework/graph/event_loop_node.py, core/framework/graph/executor.py, core/framework/graph/node.py, core/framework/runner/runner.py, core/framework/runtime/agent_runtime.py, core/framework/runtime/execution_stream.py, docs/agent_runtime.md, docs/architecture/README.md, docs/contributing-lint-setup.md, docs/developer-guide.md, docs/environment-setup.md
  Conceptual Subsystems and Their Code Counterparts
  System Architecture Diagram
  Runtime Layer
    · `AgentRunner`
    · `AgentRuntime`
    · `ExecutionStream`
  Worker Bees: Graph Execution
    · `GraphSpec` and `NodeSpec`
    · `GraphExecutor`
  Event Loop Node
    · Lifecycle
    · Judge
    · `OutputAccumulator`
  Infrastructure
    · `EventBus`
    · `SharedMemory`
    · `ToolRegistry`
    · Storage Backends
    · Credential Store
  Data Flow: Complete Request Lifecycle
  External Event Processing
  Observability

## · Agent Runtime and Execution Streams  (L2215)
  源文件: core/framework/graph/event_loop_node.py, core/framework/graph/executor.py, core/framework/graph/node.py, core/framework/runner/runner.py, core/framework/runtime/agent_runtime.py, core/framework/runtime/core.py, core/framework/runtime/execution_stream.py, core/framework/runtime/stream_runtime.py, core/tests/test_client_io.py, core/tests/test_event_loop_integration.py, core/tests/test_event_loop_node.py, core/tests/test_event_type_extension.py
  Purpose and Scope
  Component Relationships
  AgentRunner
    · Loading an Agent
    · Initialization Sequence
    · LLM Resolution
  AgentRuntime
    · Configuration
    · Entry Point Registration
    · Start Sequence
    · Timer Entry Points
    · Triggering Executions
  ExecutionStream
    · Execution Lifecycle
    · Concurrency Control
    · Input Injection
    · Result Retention
  Isolation Levels
  Runtime Interface
    · Runtime (single-threaded)
    · StreamRuntime (concurrent)
    · StreamRuntimeAdapter
  Session State and Persistence
    · Storage Layout
    · Pause and Resume
    · Checkpoint Store
  Multi-Entry-Point Session Sharing
  Cleanup
  Summary of Key Classes

## · Graph Executor and Node Execution  (L2747)
  源文件: core/framework/builder/workflow.py, core/framework/graph/edge.py, core/framework/graph/event_loop_node.py, core/framework/graph/executor.py, core/framework/graph/goal.py, core/framework/graph/hitl.py, core/framework/graph/node.py, core/framework/runner/runner.py, core/framework/runtime/agent_runtime.py, core/framework/runtime/event_bus.py, core/framework/runtime/execution_stream.py, core/framework/runtime/outcome_aggregator.py
  Overview
  Core Data Structures
    · GraphSpec
    · NodeSpec
    · EdgeSpec and EdgeCondition
    · NodeContext
    · NodeResult
    · SharedMemory
  Data Structure Relationships
  GraphExecutor
    · Initialization
    · Execution Flow
    · Node Implementation Resolution
    · Retry Logic
    · Edge Traversal
    · Runtime Decision Recording
    · Output Validation
  NodeProtocol Interface
  Parallel Execution
  Session State and Checkpointing
  ExecutionResult

## · Event Loop Node  (L3276)
  源文件: core/framework/graph/event_loop_node.py, core/framework/graph/executor.py, core/framework/graph/node.py, core/framework/runner/runner.py, core/framework/runtime/agent_runtime.py, core/framework/runtime/core.py, core/framework/runtime/execution_stream.py, core/framework/runtime/stream_runtime.py, core/tests/test_client_io.py, core/tests/test_event_loop_integration.py, core/tests/test_event_loop_node.py, core/tests/test_event_type_extension.py
  Overview
  Core Components
  LoopConfig
  The Main Loop
  LLM Streaming and Turn Processing
  Synthetic Tools
  Judge System
    · JudgeProtocol
    · JudgeVerdict
    · Verdict handling
    · Implicit Judge
  OutputAccumulator
  Client-Facing Behavior
  Conversation Compaction
  Transient Error Retry
  Doom Loop and Stall Detection
    · Tool Doom Loop
    · Stall Detection
  Graceful Shutdown
  Integration with GraphExecutor
  Observability

## · Graph Primitives: Nodes, Edges, and Goals  (L3687)
  源文件: core/framework/builder/workflow.py, core/framework/graph/edge.py, core/framework/graph/goal.py, core/framework/graph/hitl.py, core/framework/runtime/event_bus.py, core/framework/runtime/outcome_aggregator.py, core/framework/runtime/shared_state.py, core/framework/schemas/decision.py, core/framework/schemas/run.py, core/framework/testing/approval_types.py, core/framework/testing/test_case.py, core/framework/testing/test_result.py
  The Goal Schema
    · `SuccessCriterion` Fields
    · `Constraint` Fields
    · `Goal.to_prompt_context()`
    · `Goal.is_success()`
  NodeSpec
    · Field Reference
    · `node_type` Values
    · `client_facing` Flag
  EdgeSpec
    · `EdgeCondition` Traversal Logic
    · `CONDITIONAL` Edges
    · `LLM_DECIDE` Edges
    · `input_mapping`
    · Edge Priority
  GraphSpec
    · Key `GraphSpec` Fields
    · `conversation_mode`
    · `GraphSpec.validate()`
    · `AsyncEntryPointSpec`
  How Primitives Relate at Runtime
  HITL Protocol
    · HITL Lifecycle
    · `HITLInputType` Reference
  `SharedStateManager` and Isolation Levels
    · `IsolationLevel` Values
    · `StreamMemory`
  Goal Progress Tracking
  `GraphBuilder` and the Build Workflow

## · LLM Providers  (L4239)
  源文件: core/framework/llm/anthropic.py, core/framework/llm/litellm.py, core/framework/llm/provider.py, core/tests/test_litellm_provider.py
  Overview
  Data Structures
  `LLMProvider` Abstract Interface
    · Abstract methods (must be implemented)
    · Default async implementations
    · `complete` parameters
  `LiteLLMProvider`
    · Supported backends
    · Constructor
    · `json_mode` behaviour
  `AnthropicProvider`
    · OAuth token patch
  Rate-Limit Retry Logic
    · Retry constants
    · `_compute_retry_delay` priority order
    · Failed request dumps
  Tool-Use Loop (`complete_with_tools`)
  Streaming
    · `StreamEvent` types
    · Streaming retry behaviour
  Call Flow: Provider in the Framework
  Configuration Summary

## · Conversation and Memory Management  (L4606)
  源文件: core/demos/github_outreach_demo.py, core/framework/graph/__init__.py, core/framework/graph/client_io.py, core/framework/graph/conversation.py, core/framework/schemas/session_state.py, core/framework/storage/__init__.py, core/framework/storage/conversation_store.py, core/tests/test_node_conversation.py
  Overview
  The `Message` Dataclass
  `NodeConversation`
    · Construction
    · Adding Messages
    · Querying State
    · Token Estimation
  Message Lifecycle Flow
  Orphaned Tool Call Repair
  Compaction
    · Standard Compaction
    · Phase-Graduated Compaction
    · Output Key Preservation
  Tool Result Pruning (Spillover Recovery)
  Phase-Aware Continuous Mode
  `ConversationStore` Protocol
  `FileConversationStore`
  Restore / Session Recovery
  Configuration Defaults Summary

## · Output Validation  (L5035)
  源文件: core/framework/graph/conversation_judge.py, core/framework/graph/validator.py, core/framework/llm/__init__.py, core/framework/llm/mock.py, core/framework/runtime/core.py, core/framework/runtime/stream_runtime.py, core/tests/test_client_io.py, core/tests/test_event_loop_integration.py, core/tests/test_event_loop_node.py, core/tests/test_event_type_extension.py, core/tests/test_execution_stream.py, core/tests/test_graph_executor.py
  Overview
  Core Data Structures
    · `ValidationResult`
    · `PhaseVerdict`
  `OutputValidator`
    · Key Presence Validation — `validate_output_keys`
    · Pydantic Model Validation — `validate_with_pydantic`
    · LLM Retry Feedback — `format_validation_feedback`
    · Hallucination Detection — `validate_no_hallucination`
    · JSON Schema Validation — `validate_schema`
    · Composite Validation — `validate_all`
  Hallucination Detection in `SharedMemory`
  Conversation-Aware Judge — `evaluate_phase_completion`
    · Prompt Structure
    · Output Formatting — `_format_outputs`
    · Failure Behavior
  Integration with `EventLoopNode`
    · `NodeSpec` Validation Configuration Fields

## · Storage and Observability  (L5449)
  源文件: core/framework/observability/README.md, core/framework/observability/__init__.py, core/framework/observability/logging.py, core/framework/runtime/runtime_log_schemas.py, core/framework/runtime/runtime_log_store.py, core/framework/runtime/runtime_logger.py, core/framework/runtime/tests/test_agent_runtime.py, core/framework/storage/backend.py, core/framework/storage/concurrent.py, core/framework/testing/test_storage.py, core/framework/utils/__init__.py, core/framework/utils/io.py
  Storage Backends
    · Current Architecture: Unified Session Storage
    · Deprecated: FileStorage
    · Deprecated: ConcurrentStorage
    · Atomic Write Utility
  Three-Level Runtime Logging
    · Log Schemas
    · RuntimeLogStore
    · RuntimeLogger
  Structured Logging
    · Configuration
    · Formatters
    · Trace Context Propagation
  EventBus
  MCP Tools for Querying Runtime Logs
  Storage Layout Summary

## · MCP Integration  (L5964)
  源文件: .gitignore, .mcp.json, .python-version, CHANGELOG.md, core/framework/agents/credential_tester/__init__.py, core/framework/agents/credential_tester/agent.py, core/framework/agents/credential_tester/nodes/__init__.py, core/framework/credentials/__init__.py, core/framework/credentials/local/__init__.py, core/framework/credentials/local/models.py, core/framework/credentials/local/registry.py, core/framework/graph/prompt_composer.py
  Role of MCP in Hive
  The Two MCP Servers
    · 1. `agent-builder` Server
    · 2. `tools` Server (`aden_tools`)
  Configuration via `.mcp.json`
  How MCP Servers Are Registered at Runtime
  Code Entity Map
  MCPClient Transport Details
  ToolRegistry MCP Integration
  Data Structures
  Summary of Information Flow

## · MCP Client and Tool Registry  (L6247)
  源文件: CHANGELOG.md, core/framework/runner/mcp_client.py, core/framework/runner/tool_registry.py, core/pyproject.toml, examples/templates/README.md, tools/src/aden_tools/tools/web_scrape_tool/README.md
  Data Structures
    · `MCPServerConfig` fields
  MCPClient
    · Connection Lifecycle
    · `_run_async()` — Sync/Async Bridge
    · Tool Discovery
    · Tool Invocation
    · Disconnection and Cleanup
  ToolRegistry
    · Tool Discovery Order
    · Source → Registry Flow
    · `discover_from_module(module_path)`
    · `register_mcp_server(server_config)`
    · `load_mcp_config(config_path)`
    · Context Parameter Injection
    · `get_executor()`
    · Provider-Based Tool Filtering
    · Cleanup
  `@tool` Decorator
  End-to-End: From `.mcp.json` to Tool Execution

## · Agent Builder MCP Server  (L6597)
  源文件: .gitignore, .mcp.json, .python-version, core/framework/agents/credential_tester/__init__.py, core/framework/agents/credential_tester/agent.py, core/framework/agents/credential_tester/nodes/__init__.py, core/framework/credentials/__init__.py, core/framework/credentials/local/__init__.py, core/framework/credentials/local/models.py, core/framework/credentials/local/registry.py, core/framework/graph/prompt_composer.py, core/framework/mcp/agent_builder_server.py
  Overview
  Architecture
  BuildSession Data Model
    · Session ID and Timestamps
  Session Persistence
    · Deserialization Notes
  MCP Tools Reference
    · Session Management
    · Goal Definition — `set_goal()`
    · Node Management — `add_node()` and `update_node()`
    · Edge Management — `add_edge()` and `delete_edge()`
    · Graph Validation — `validate_graph()`
    · Graph Export — `export_graph()`
  Approval Flow
  Credential Validation During Build
  Session State Machine
  Integration with Claude Code Skills

## · Credential Management  (L7113)
  源文件: core/framework/agents/credential_tester/__init__.py, core/framework/agents/credential_tester/agent.py, core/framework/agents/credential_tester/nodes/__init__.py, core/framework/credentials/__init__.py, core/framework/credentials/local/__init__.py, core/framework/credentials/local/models.py, core/framework/credentials/local/registry.py, core/framework/credentials/setup.py, core/framework/credentials/validation.py, core/framework/graph/prompt_composer.py, core/framework/mcp/agent_builder_server.py, core/framework/tui/screens/__init__.py
  System Overview
  CredentialSpec and CREDENTIAL_SPECS
  Storage Backends
  Key Environment Variables
  CredentialStoreAdapter
  How Tools Receive Credentials
  LocalCredentialRegistry
  Aden Platform vs Local Credentials
  Pre-run Credential Validation

## · Credential Validation and Interactive Setup  (L7491)
  源文件: core/framework/credentials/oauth2/base_provider.py, core/framework/credentials/oauth2/lifecycle.py, core/framework/credentials/provider.py, core/framework/credentials/setup.py, core/framework/credentials/storage.py, core/framework/credentials/template.py, core/framework/credentials/tests/test_credential_store.py, core/framework/credentials/validation.py, core/framework/credentials/vault/hashicorp.py
  Overview
  Two-Phase Validation
    · Phase 1: Presence Check
    · Phase 2: Health Check
    · `CredentialError`
  Building a Setup Session from a Validation Error
  `CredentialSetupSession`
    · Key Data Structures
    · Construction Methods
    · `run_interactive` Flow
    · Setup Method: Direct API Key
    · Setup Method: Aden OAuth
    · `HIVE_CREDENTIAL_KEY` Initialization
    · I/O Customization
  `run_credential_setup_cli`
  Integration Points

## · Aden Platform Credential Sync  (L7815)
  源文件: .claude/skills/triage-issue/SKILL.md, core/demos/event_loop_wss_demo.py, core/framework/agents/credential_tester/__main__.py, core/framework/agents/credential_tester/mcp_servers.json, core/framework/credentials/aden/__init__.py, core/framework/credentials/aden/client.py, core/framework/credentials/aden/provider.py, core/framework/credentials/aden/storage.py, core/framework/credentials/aden/tests/__init__.py, core/framework/credentials/aden/tests/test_aden_sync.py, core/framework/credentials/store.py, core/tests/test_event_loop_wiring.py
  Overview
  System Architecture
  `AdenCredentialClient`
    · Configuration
    · Key Methods
    · Data Structures
  `AdenSyncProvider`
    · Constructor Parameters
    · `can_handle(credential)`
    · `refresh(credential)`
    · `should_refresh(credential)`
    · `fetch_from_aden(integration_id)`
    · `sync_all(store)`
    · Internal Credential Mapping
  `AdenCachedStorage`
    · Constructor Parameters
    · In-Memory Indexes
    · Load Strategy
    · Alias-Based Lookup
  REST API Contract
  Error Handling
  Factory Method: `CredentialStore.with_aden_sync()`
  Environment Variables
  Multi-Account and Multi-Tenant
  Security Properties

## · Tools Reference  (L8279)
  源文件: core/framework/graph/safe_eval.py, core/setup_mcp.py, core/verify_mcp.py, tools/README.md, tools/mcp_server.py, tools/pyproject.toml, tools/src/aden_tools/__init__.py, tools/src/aden_tools/credentials/__init__.py, tools/src/aden_tools/credentials/browser.py, tools/src/aden_tools/credentials/health_check.py, tools/src/aden_tools/tools/__init__.py, tools/src/aden_tools/tools/arxiv_tool/README.md
  Package Layout
  MCP Server Entry Point
  Tool Registration Pattern
  Tool Categories
    · File System Toolkits
    · Data File Tools
    · Web & Search
    · Communication
    · Productivity & CRM
    · Cloud & APIs
    · Security Scanning
    · Utilities
  Credential Management via `CredentialStoreAdapter`
  Credential Specs (`CredentialSpec` and `CREDENTIAL_SPECS`)
  Credential Health Checks
  File System Sandbox
  `safe_eval` — Expression Evaluator
  Adding a New Tool

## · Email and Gmail Tools  (L8722)
  源文件: tools/src/aden_tools/credentials/email.py, tools/src/aden_tools/tools/email_tool/README.md, tools/src/aden_tools/tools/email_tool/__init__.py, tools/src/aden_tools/tools/email_tool/email_tool.py, tools/src/aden_tools/tools/gmail_tool/gmail_tool.py, tools/tests/tools/test_email_tool.py, tools/tests/tools/test_gmail_tool.py
  Overview
  Credential Resolution
  email_tool
    · `send_email`
    · `gmail_reply_email`
  gmail_tool
    · Tool Reference
  Testing
  Environment Variables Summary

## · Web Search and Research Tools  (L9174)
  源文件: core/framework/graph/safe_eval.py, core/setup_mcp.py, core/tests/test_path_traversal_fix.py, core/verify_mcp.py, scripts/auto-close-duplicates.ts, tools/README.md, tools/mcp_server.py, tools/src/aden_tools/__init__.py, tools/src/aden_tools/tools/arxiv_tool/README.md, tools/src/aden_tools/tools/arxiv_tool/__init__.py, tools/src/aden_tools/tools/arxiv_tool/arxiv_tool.py, tools/src/aden_tools/tools/hubspot_tool/hubspot_tool.py
  Tool Module Map
  `web_search`
    · Parameters
    · Provider Selection
    · Credential Resolution
    · Return Format
    · Rate-Limit Handling
    · Required Credentials Summary
  `web_scrape`
    · Parameters
    · Processing Pipeline
    · Content Detection
    · Link Extraction
    · Error Returns
  arXiv Tools: `search_papers` and `download_paper`
    · Module-Level Singletons
    · `search_papers`
    · `download_paper`
  `google_docs_*` Tools
  Credential Reference

## · Terminal User Interface (TUI)  (L9604)
  源文件: core/framework/runner/cli.py, core/framework/tui/app.py, core/framework/tui/screens/agent_picker.py, core/framework/tui/screens/credential_setup.py, core/framework/tui/widgets/chat_repl.py, core/framework/tui/widgets/graph_view.py, core/framework/tui/widgets/log_pane.py, uv.lock
  Entry Points
  Application Layout
  Widget Reference
    · `StatusBar`
    · `GraphOverview`
    · `ChatRepl`
  Runtime Event Routing Pipeline
  Log Formatting (`log_pane.py`)
  Slash Commands
  Key Bindings
  Agent Swapping
  Escalation to Hive Coder
  Modal Screens
    · `AgentPickerScreen`
    · `CredentialSetupScreen`
  Session Management in ChatRepl
  Component-to-Code Mapping

## · Agent Development Guide  (L10094)
  源文件: .claude/skills/hive-create/SKILL.md, .claude/skills/hive-create/examples/deep_research_agent/config.py, .claude/skills/hive-credentials/SKILL.md, .claude/skills/hive-debugger/SKILL.md, .claude/skills/hive/SKILL.md, CONTRIBUTING.md, docs/agent_runtime.md, docs/getting-started.md, docs/roadmap-developer-success.md, examples/recipes/README.md, examples/recipes/ad_campaign_monitoring/README.md, examples/recipes/calendar_coordination/README.md
  Build Paths
  The `exports/` Package Structure
    · Key files
  Agent Development Lifecycle
  Claude Code Skills Workflow
    · The `/hive-create` Workflow (Step by Step)
    · Key Design Decisions Made During `/hive-create`
  Manual Authoring
  Running Agents
  Credential Setup
  Debugging
  Templates and Recipes
  Related Pages

## · Building Agents with Claude Skills  (L10431)
  源文件: .claude/skills/hive-create/SKILL.md, .claude/skills/hive-create/examples/deep_research_agent/config.py, .claude/skills/hive-credentials/SKILL.md, .claude/skills/hive-debugger/SKILL.md, .claude/skills/hive/SKILL.md, core/tests/test_executor_max_retries.py, examples/templates/deep_research_agent/config.py, examples/templates/tech_news_reporter/config.py
  The Skill Suite
  `/hive` — Orchestrator
  `/hive-create` — Agent Construction Workflow
    · Build Paths
    · Step-by-Step Workflow
    · Step 1: Initialization
    · Step 2: Capability Assessment
    · Step 3: Goal Definition
    · Step 4: Node Design
    · Step 5: Graph and Edge Design
    · Step 6a: Register with MCP
    · Step 6b: Write Python Package Files
    · Step 7: Validate and Finalize
  System Prompt Patterns
  `/hive-credentials` — Credential Setup
    · Workflow
    · Authentication Options
    · Credential Specs Reference
  `/hive-debugger` — Runtime Log Analysis
    · Log Level Reference
    · Debugging Stages
    · Attention Flag Triggers
    · Issue Categories
    · Forever-Alive Agent Awareness
    · Session and Checkpoint Tools
  End-to-End Flow

## · Testing Framework  (L10980)
  源文件: .claude/skills/hive-concepts/SKILL.md, .claude/skills/hive-create/examples/deep_research_agent/__main__.py, .claude/skills/hive-create/examples/deep_research_agent/agent.py, .claude/skills/hive-create/examples/deep_research_agent/nodes/__init__.py, .claude/skills/hive-patterns/SKILL.md, .claude/skills/hive-test/SKILL.md, .claude/skills/hive-test/examples/testing-youtube-agent.md, core/framework/__init__.py, core/framework/cli.py, core/framework/runtime/core.py, core/framework/runtime/stream_runtime.py, core/framework/testing/__init__.py
  Overview
  Module Structure
  Core Schemas
    · `Test`
    · `TestResult` and `TestSuiteResult`
    · `ErrorCategory`
  Test File Layout
  Code Generation Templates
    · `PYTEST_TEST_FILE_HEADER`
    · `PYTEST_CONFTEST_TEMPLATE`
  Key Pytest Fixtures
    · `mock_mode`
    · `runner`
    · `auto_responder`
  `ExecutionResult` Fields
  CLI Commands
    · `hive test-run <agent_path> --goal <goal_id>`
    · `hive test-debug <agent_path> <test_name>`
    · `hive test-list <agent_path>`
    · `hive test-stats <agent_path>`
  Approval Workflow
  Iterative Testing Loop
    · When to Resume vs. Re-run
  Credential Requirements
  `TestStorage`
  Safe Test Patterns
  Internal Framework Tests

## · Agent Examples and Recipes  (L11386)
  源文件: docs/agent_runtime.md, docs/roadmap-developer-success.md, examples/recipes/README.md, examples/recipes/ad_campaign_monitoring/README.md, examples/recipes/calendar_coordination/README.md, examples/recipes/crm_update/README.md, examples/recipes/data_keeper/README.md, examples/recipes/documentation/README.md, examples/recipes/inbox_management/README.md, examples/recipes/inquiry_triaging/README.md, examples/recipes/news_jacking/README.md, examples/recipes/support_troubleshooting/README.md
  Examples vs. Recipes
  Template: Email Inbox Management Agent
    · File Structure
    · Goal Definition
    · Four-Node Graph
    · AsyncEntryPointSpec — Timer-Driven Execution
    · `EmailInboxManagementAgent` Class Structure
    · `_setup()`: Wiring Components Together
    · `_build_graph()`: GraphSpec Construction
    · Running the Agent
  Template: Deep Research Agent
  Template: Tech & AI News Reporter
  Template Comparison
  Recipe Blueprints
    · Available Recipes by Category
    · How to Use a Recipe
    · Recipe Structure: What Each Section Covers

## · IDE Integration  (L11841)
  源文件: .gitignore, .mcp.json, .python-version, docs/antigravity-setup.md, scripts/setup-antigravity-mcp.sh
  How IDE Integration Works
  MCP Servers Exposed
  Antigravity IDE Setup
    · Prerequisites
    · Running the Setup Script
    · Config File Locations
    · Config Format
  Claude Code Setup
    · Using `.mcp.json` (Repo-Local)
    · Using the Setup Script (User-Global)
  Skills
  File and Directory Map
  Verification
    · Manual Server Start Test
    · Checking Skills and Config
  Troubleshooting

## · Contributing  (L12113)
  源文件: CONTRIBUTING.md, README.md, docs/architecture/README.md, docs/contributing-lint-setup.md, docs/developer-guide.md, docs/environment-setup.md, docs/getting-started.md, docs/roadmap.md, package.json, quickstart.sh
  Issue Assignment Policy
  Getting Started
  Contribution Workflow Diagram
  Pull Request Requirements
  Commit Message Convention
  Code Style
    · Python Style Rules
  Linting and Formatting (Ruff)
    · Configuration File Map
  `make` Commands
  Pre-Commit Hooks
  Running Tests
  Tooling and File Map
  Editor Integration
    · VS Code
    · Other Editors
    · Claude Code
    · Cursor
  Project Structure Reference
  Community and Support

## · GitHub Automation and CI/CD  (L12520)
  源文件: .github/ISSUE_TEMPLATE/bug_report.md, .github/ISSUE_TEMPLATE/feature_request.md, .github/ISSUE_TEMPLATE/integration-request.md, .github/PULL_REQUEST_TEMPLATE.md, .github/workflows/auto-close-duplicates.yml, .github/workflows/ci.yml, .github/workflows/claude-issue-triage.yml, .github/workflows/pr-check-command.yml, .github/workflows/pr-requirements-backfill.yml, .github/workflows/pr-requirements.yml, .github/workflows/release.yml, docs/pr-requirements.md
  Workflow Overview
  PR Requirements Enforcement
    · Policy
    · Issue Reference Pattern
    · Enforcement Flow (`pr-requirements.yml`)
  PR Check Command (`pr-check-command.yml`)
  Issue Triage (`claude-issue-triage.yml`)
    · Overview
    · Triage Steps
    · Category Labels
    · Size Labels
    · Spam Detection Criteria
  Auto-Close Duplicates (`auto-close-duplicates.yml`)
    · Schedule
    · Mechanism
    · `decideAutoClose` Logic
  CI Pipeline (`ci.yml`)
    · Jobs
    · Job Details
    · Full CI Job Dependency Diagram
  Release Pipeline (`release.yml`)
  Backfill Utility (`pr-requirements-backfill.yml`)
  Required Secrets and Permissions Summary