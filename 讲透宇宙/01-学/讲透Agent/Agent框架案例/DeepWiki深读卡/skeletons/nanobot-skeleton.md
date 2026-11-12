# Skeleton: nanobot（49 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 10KB | 2 | ~5 | 26 |
| 2 | Getting Started | L206 | 9KB | 3 | ~2 | 25 |
| 3 | Installation & Configuration | L449 | 8KB | 2 | ~5 | 20 |
| 4 | First Run & Interactive Mode | L612 | 9KB | 2 | ~1 | 23 |
| 5 | Architecture | L786 | 10KB | 1 | ~2 | 27 |
| 6 | Message Bus & Event Flow | L966 | 11KB | 4 | ~10 | 16 |
| 7 | Multi-Instance Architecture | L1195 | 9KB | 2 | ~4 | 19 |
| 8 | Agent System | L1401 | 10KB | 3 | ~0 | 12 |
| 9 | Agent Loop | L1617 | 10KB | 2 | ~4 | 18 |
| 10 | Context Building | L1817 | 11KB | 5 | ~4 | 21 |
| 11 | Memory System | L2051 | 9KB | 2 | ~2 | 19 |
| 12 | Skills | L2216 | 10KB | 2 | ~7 | 22 |
| 13 | Subagents | L2432 | 10KB | 2 | ~6 | 16 |
| 14 | Communication Channels | L2637 | 8KB | 2 | ~4 | 10 |
| 15 | Channel Architecture | L2815 | 10KB | 2 | ~3 | 20 |
| 16 | Telegram | L3012 | 14KB | 2 | ~7 | 10 |
| 17 | Feishu | L3299 | 15KB | 3 | ~12 | 10 |
| 18 | Matrix | L3632 | 26KB | 11 | ~13 | 10 |
| 19 | Other Channels | L4243 | 11KB | 2 | ~3 | 28 |
| 20 | LLM Providers | L4453 | 10KB | 2 | ~2 | 12 |
| 21 | Provider Selection & Registry | L4635 | 12KB | 2 | ~6 | 18 |
| 22 | Provider Implementations | L4891 | 12KB | 2 | ~1 | 23 |
| 23 | Tools & Capabilities | L5105 | 8KB | 2 | ~2 | 6 |
| 24 | Built-in Tools | L5269 | 14KB | 2 | ~4 | 39 |
| 25 | MCP Integration | L5554 | 9KB | 2 | ~3 | 10 |
| 26 | Security & Sandboxing | L5751 | 12KB | 3 | ~2 | 28 |
| 27 | CLI Apps (CLI-Anything) | L5994 | 9KB | 3 | ~4 | 17 |
| 28 | Configuration | L6155 | 7KB | 2 | ~0 | 14 |
| 29 | Config Schema Reference | L6306 | 11KB | 2 | ~10 | 19 |
| 30 | Config Migration & Backfilling | L6530 | 9KB | 2 | ~4 | 15 |
| 31 | CLI Reference | L6702 | 11KB | 3 | ~12 | 25 |
| 32 | Command Router & Built-in Commands | L7010 | 9KB | 3 | ~3 | 17 |
| 33 | Automation & Scheduling | L7201 | 8KB | 2 | ~1 | 18 |
| 34 | Cron Service | L7352 | 11KB | 4 | ~10 | 7 |
| 35 | Heartbeat Service | L7640 | 8KB | 2 | ~3 | 17 |
| 36 | Local Triggers | L7802 | 7KB | 2 | ~2 | 8 |
| 37 | Session Management | L7950 | 9KB | 2 | ~0 | 18 |
| 38 | Session Lifecycle | L8137 | 10KB | 2 | ~3 | 20 |
| 39 | Memory Consolidation | L8298 | 9KB | 2 | ~1 | 15 |
| 40 | Deployment | L8462 | 9KB | 2 | ~4 | 14 |
| 41 | Docker & Container Deployment | L8655 | 7KB | 2 | ~0 | 9 |
| 42 | CI/CD & Contributing | L8808 | 8KB | 2 | ~0 | 5 |
| 43 | Python SDK | L8956 | 7KB | 2 | ~2 | 12 |
| 44 | SDK Quick Start & API Reference | L9101 | 9KB | 2 | ~2 | 21 |
| 45 | AgentHook & Lifecycle Callbacks | L9316 | 11KB | 2 | ~5 | 20 |
| 46 | WebUI | L9526 | 7KB | 2 | ~0 | 15 |
| 47 | WebUI Architecture & Components | L9660 | 11KB | 2 | ~4 | 35 |
| 48 | WebUI Development & i18n | L9845 | 9KB | 2 | ~4 | 34 |
| 49 | Glossary | L10014 | 14KB | 2 | ~4 | 42 |


## · Overview  (L6)
  源文件: .agent/design.md, .agent/gotchas.md, AGENTS.md, CLAUDE.md, README.md, core_agent_lines.sh, docs/README.md, docs/architecture.md, docs/chat-commands.md, docs/cli-reference.md, docs/concepts.md, docs/configuration.md
  Purpose and Scope
  System Description
  Core Architecture
  Key Components
  Message Processing Flow
  Technology Stack
  Workspace & Configuration
    · Configuration (`config.json`)
    · Workspace Files

## · Getting Started  (L206)
  源文件: README.md, docs/README.md, docs/architecture.md, docs/chat-commands.md, docs/cli-reference.md, docs/concepts.md, docs/configuration.md, docs/guides/deploy-nanobot-gateway.md, docs/multiple-instances.md, docs/provider-cookbook.md, docs/providers.md, docs/quick-start.md
  Installation
  Initialization Flow
  Workspace Structure
  Configuration File Schema
  Minimal Configuration
    · 1. Provider API Key
    · 2. Model Preset
  First Interaction: WebUI and CLI
    · WebUI Workbench
    · CLI Agent
  CLI Execution Path
  Next Steps

## · Installation & Configuration  (L449)
  源文件: README.md, docs/configuration.md, docs/provider-cookbook.md, docs/providers.md, docs/start-without-technical-background.md, nanobot/agent/model_presets.py, nanobot/channels/registry.py, nanobot/cli/commands.py, nanobot/cli/gateway.py, nanobot/cli/onboard.py, nanobot/config/loader.py, nanobot/config/schema.py
  Installation
    · One-Command Installer
    · Manual Installation
  Configuration Structure
    · Core Configuration Sections
    · Environment Variable Interpolation
    · Configuration Data Flow
  The Onboard Wizard
    · Execution Flow
  Config Migration & Security
    · Configuration Field Mapping

## · First Run & Interactive Mode  (L612)
  源文件: docs/README.md, docs/architecture.md, docs/chat-commands.md, docs/cli-reference.md, docs/concepts.md, docs/guides/deploy-nanobot-gateway.md, docs/multiple-instances.md, docs/quick-start.md, docs/start-without-technical-background.md, docs/troubleshooting.md, docs/webui.md, nanobot/agent/model_presets.py
  Interactive Onboarding
    · The Wizard Flow
  Initial Launch & Terminal Setup
    · Terminal Initialization
  The Interactive REPL Loop
    · UI Feedback Components
    · Feedback Synchronization
  Tool Hints System
    · Smart Abbreviation & Formatting
    · Call Folding
  Reasoning and Progress Handling
    · Reasoning Buffer
    · Provider Retries
  Rendering Responses
    · Streaming Mode

## · Architecture  (L786)
  源文件: README.md, docs/configuration.md, docs/provider-cookbook.md, docs/providers.md, nanobot/agent/context.py, nanobot/agent/loop.py, nanobot/agent/subagent.py, nanobot/audio/transcription.py, nanobot/audio/transcription_registry.py, nanobot/channels/base.py, nanobot/channels/manager.py, nanobot/cli/commands.py
  Overview
  Component Map
  Message Bus & Event Flow
  Gateway Runtime: Service Orchestration
  AgentLoop: Core Processing Engine
  Multi-Instance Architecture

## · Message Bus & Event Flow  (L966)
  源文件: nanobot/agent/tools/sessions.py, nanobot/bus/events.py, nanobot/bus/outbound_events.py, nanobot/bus/runtime_events.py, nanobot/channels/websocket/runtime.py, nanobot/channels/websocket/tests/test_websocket_channel.py, nanobot/channels/websocket/tests/test_websocket_envelope_media.py, nanobot/channels/websocket/tests/test_websocket_reconnect_idle.py, nanobot/session/webui_turns.py, nanobot/webui/session_access.py, tests/agent/tools/test_sessions.py, tests/bus/test_outbound_events.py
  Message Bus Overview
  Event Types
    · InboundMessage
    · OutboundMessage
  MessageBus Implementation
    · Core Methods
  Channel Manager & Routing
    · Initialization and Discovery
    · Dispatcher and Coalescing
    · Streaming Support
  Runtime Events
    · Event Types
    · Event Lifecycle Management
  Session Turn Projections

## · Multi-Instance Architecture  (L1195)
  源文件: README.md, docs/configuration.md, docs/provider-cookbook.md, docs/providers.md, nanobot/channels/registry.py, nanobot/cli/commands.py, nanobot/config/loader.py, nanobot/config/schema.py, nanobot/gateway/__init__.py, nanobot/gateway/runtime.py, nanobot/gateway/service.py, nanobot/providers/registry.py
  Instance Isolation Model
  Path Resolution Logic
    · Resolution Priority
  Configuration Schema
    · Instance-Specific Config Fields
  Instance Isolation Boundaries
  Deployment and Management
    · Starting Instances via CLI
    · Background Service Management
    · Common Pitfalls

## · Agent System  (L1401)
  源文件: nanobot/agent/automation_turns.py, nanobot/agent/context.py, nanobot/agent/loop.py, nanobot/agent/runner.py, nanobot/agent/subagent.py, nanobot/utils/runtime.py, tests/agent/test_loop_progress.py, tests/agent/test_loop_save_turn.py, tests/agent/test_runner_core.py, tests/agent/test_runner_goal_continue.py, tests/agent/test_runner_hooks.py, tests/agent/test_runner_injections.py
  Component Architecture
  Core Components
    · AgentLoop
    · AgentRunner
    · SubagentManager
  Message Processing Flow
  Agent Loop Iteration
  Context Building
  Memory and Consolidation

## · Agent Loop  (L1617)
  源文件: nanobot/agent/automation_turns.py, nanobot/agent/context.py, nanobot/agent/loop.py, nanobot/agent/runner.py, nanobot/agent/subagent.py, nanobot/session/goal_state.py, nanobot/session/turn_continuation.py, nanobot/utils/runtime.py, tests/agent/test_loop_progress.py, tests/agent/test_loop_runner_integration.py, tests/agent/test_loop_save_turn.py, tests/agent/test_runner_core.py
  Overview
  Constructor and Initialization
  Tool Registration
  The Main Execution Loop (`run`)
  The Iteration Cycle (`AgentRunner.run`)
  Message Persistence and Turn Saving
  Command Handling
  Subagent Management

## · Context Building  (L1817)
  源文件: nanobot/agent/context.py, nanobot/agent/context_governance.py, nanobot/agent/loop.py, nanobot/agent/subagent.py, nanobot/providers/anthropic_provider.py, nanobot/templates/AGENTS.md, nanobot/templates/HEARTBEAT.md, nanobot/templates/SOUL.md, nanobot/templates/agent/identity.md, nanobot/templates/agent/tool_contract.md, nanobot/templates/legacy/SOUL.md, tests/agent/test_context_builder.py
  Overview
  System Prompt Pipeline
    · Identity Block
    · Bootstrap Files
    · Memory and History Sections
  Context Governance
  Model Runtime Selection
  Runtime Context Injection
  Subagent Isolation
  Class Dependency Diagram

## · Memory System  (L2051)
  源文件: nanobot/agent/autocompact.py, nanobot/agent/memory.py, nanobot/session/manager.py, nanobot/skills/memory/SKILL.md, nanobot/templates/agent/dream.md, nanobot/utils/gitstore.py, tests/agent/test_auto_compact.py, tests/agent/test_autocompact_unit.py, tests/agent/test_consolidate_offset.py, tests/agent/test_consolidator.py, tests/agent/test_dream.py, tests/agent/test_git_store.py
  Storage Architecture
  MemoryStore Implementation
    · Key Components
    · Code Entity Space Mapping
  Auto-Compact & Consolidation
    · Proactive Auto-Compact
    · Token-Based Consolidation
  The Dream Process
  Retrieval and Search
  Versioning with GitStore

## · Skills  (L2216)
  源文件: nanobot/agent/skills.py, nanobot/agent/tools/long_task.py, nanobot/skills/README.md, nanobot/skills/clawhub/SKILL.md, nanobot/skills/github/SKILL.md, nanobot/skills/skill-creator/SKILL.md, nanobot/skills/skill-creator/scripts/init_skill.py, nanobot/skills/skill-creator/scripts/package_skill.py, nanobot/skills/skill-creator/scripts/quick_validate.py, nanobot/skills/summarize/SKILL.md, nanobot/skills/tmux/SKILL.md, nanobot/skills/tmux/scripts/find-sessions.sh
  Overview
  SkillsLoader Class
    · Skill Discovery and Shadowing
    · Public Methods
  SKILL.md File Format
    · Frontmatter Fields
    · Requirement Validation
  Progressive Disclosure Strategy
  Creating and Packaging Skills
    · Validation
    · Packaging

## · Subagents  (L2432)
  源文件: nanobot/agent/__init__.py, nanobot/agent/context.py, nanobot/agent/loop.py, nanobot/agent/subagent.py, nanobot/agent/tools/message.py, nanobot/agent/tools/search.py, nanobot/agent/tools/spawn.py, tests/agent/test_hook_composite.py, tests/agent/test_loop_save_turn.py, tests/agent/test_subagent.py, tests/agent/tools/test_subagent_tools.py, tests/test_file_tool_toggle.py
  Overview
  Component Structure
  SubagentManager
    · Internal Tracking
    · `spawn()`
    · `_run_subagent()`
  SpawnTool
    · Context Handling
    · Tool Schema
  Subagent Tool Access
  Task Lifecycle
  Integration with AgentLoop

## · Communication Channels  (L2637)
  源文件: docs/chat-apps.md, nanobot/audio/transcription.py, nanobot/audio/transcription_registry.py, nanobot/channels/base.py, nanobot/channels/manager.py, nanobot/optional_features.py, nanobot/providers/transcription.py, tests/channels/test_channel_plugins.py, tests/providers/test_stepfun_asr.py, tests/providers/test_transcription.py
  Supported Platforms
  Message Flow Architecture
    · System Data Flow
  Channel Discovery and Registration
  Security and Lifecycle
    · Access Control and Pairing
    · Lifecycle Management
  Common Features
    · Audio Transcription
    · Interactive Login
    · Reasoning and Streaming

## · Channel Architecture  (L2815)
  源文件: nanobot/audio/transcription.py, nanobot/audio/transcription_registry.py, nanobot/bus/outbound_events.py, nanobot/channels/base.py, nanobot/channels/manager.py, nanobot/channels/websocket/tests/test_websocket_reconnect_idle.py, nanobot/cli/models.py, nanobot/command/router.py, nanobot/optional_features.py, nanobot/pairing/__init__.py, nanobot/pairing/store.py, nanobot/providers/transcription.py
  BaseChannel Abstraction
    · Class Hierarchy
    · Core Interface Methods
  Channel Management
    · Discovery and Initialization
  Access Control and Pairing
    · ACL (Access Control List)
    · Pairing Workflow
  Message Flow and Bus Integration
    · Inbound Flow (User → Agent)
    · Outbound Flow (Agent → User)
  Common Features
    · Reasoning Support
    · Transcription Services
    · Restart Notifications

## · Telegram  (L3012)
  源文件: nanobot/channels/discord/runtime.py, nanobot/channels/discord/tests/test_discord_channel.py, nanobot/channels/feishu/runtime.py, nanobot/channels/feishu/tests/test_feishu_card_extraction.py, nanobot/channels/feishu/tests/test_feishu_markdown_rendering.py, nanobot/channels/feishu/tests/test_feishu_streaming.py, nanobot/channels/matrix/runtime.py, nanobot/channels/matrix/tests/test_matrix_channel.py, nanobot/channels/telegram/runtime.py, nanobot/channels/telegram/tests/test_telegram_channel.py
  Purpose and Scope
  Configuration
    · Group Policies
  Architecture Overview
    · System Entity Map
  Long Polling and Lifecycle
    · Startup Sequence
    · Startup Flow Diagram
    · Proxy Support
  Inbound Message Processing
    · Sender ID Format
    · Media Download and Transcription
    · Media Groups (Albums)
  Outbound Message Sending
    · Markdown to HTML Conversion
    · Streaming and Progressive Editing
    · Message Splitting
  Threading and Topics
  Access Control

## · Feishu  (L3299)
  源文件: nanobot/channels/discord/runtime.py, nanobot/channels/discord/tests/test_discord_channel.py, nanobot/channels/feishu/runtime.py, nanobot/channels/feishu/tests/test_feishu_card_extraction.py, nanobot/channels/feishu/tests/test_feishu_markdown_rendering.py, nanobot/channels/feishu/tests/test_feishu_streaming.py, nanobot/channels/matrix/runtime.py, nanobot/channels/matrix/tests/test_matrix_channel.py, nanobot/channels/telegram/runtime.py, nanobot/channels/telegram/tests/test_telegram_channel.py
  Overview
  Architecture and Integration
    · System-to-Code Entity Mapping
  Configuration
  Message Reception Flow
  Streaming Support (CardKit)
  Message Format Detection
  Interactive Card Rendering
  Media Handling
  Tool Hint Display
  Reply Quoting and Topic Isolation
  Event Registration

## · Matrix  (L3632)
  源文件: nanobot/channels/discord/runtime.py, nanobot/channels/discord/tests/test_discord_channel.py, nanobot/channels/feishu/runtime.py, nanobot/channels/feishu/tests/test_feishu_card_extraction.py, nanobot/channels/feishu/tests/test_feishu_markdown_rendering.py, nanobot/channels/feishu/tests/test_feishu_streaming.py, nanobot/channels/matrix/runtime.py, nanobot/channels/matrix/tests/test_matrix_channel.py, nanobot/channels/telegram/runtime.py, nanobot/channels/telegram/tests/test_telegram_channel.py
  Purpose and Scope
  Configuration Schema
  Channel Architecture
    · Class Hierarchy and Lifecycle
  Message Flow
    · Inbound Message Processing
    · Media Message Processing
    · Outbound Message Delivery
  Access Control and Room Policies
    · Group Policy Decision Tree
    · Policy Modes
  End-to-End Encryption (E2EE)
    · Encryption Architecture
    · E2EE Components
  Typing Indicators
    · Keepalive Mechanism
  Threading Support
    · Thread Metadata Flow
  Markdown Rendering and HTML Sanitization
    · Rendering Pipeline
  Media Handling
    · Upload Limit Resolution
    · Attachment Filename Sanitization
    · Workspace Restriction
  Error Handling
    · Response Error Callbacks
    · Media Download/Upload Failures
  Key Classes and Methods Reference

## · Other Channels  (L4243)
  源文件: docs/guides/configure-langfuse-observability.md, docs/guides/mattermost-ai-agent.md, nanobot/agent/tools/sessions.py, nanobot/bus/events.py, nanobot/channels/dingtalk/runtime.py, nanobot/channels/dingtalk/tests/test_dingtalk_channel.py, nanobot/channels/feishu/connect.py, nanobot/channels/feishu/tests/test_connect.py, nanobot/channels/mattermost/manifest.py, nanobot/channels/mattermost/runtime.py, nanobot/channels/mattermost/tests/test_mattermost_channel.py, nanobot/channels/websocket/runtime.py
  Purpose and Scope
  Channel Architecture Overview
    · Channel Classification and Entity Mapping
  Specific Channel Implementations
    · Personal WeChat (Weixin)
    · DingTalk (DingDing)
    · WeCom (Enterprise WeChat)
    · Mattermost
  React WebUI and WebSocket Channel
    · WebUI & Gateway Architecture
  Additional Channel Details
    · Reasoning and Progress Delivery

## · LLM Providers  (L4453)
  源文件: nanobot/providers/__init__.py, nanobot/providers/base.py, nanobot/providers/factory.py, nanobot/providers/fallback_provider.py, tests/agent/test_runner_fallback.py, tests/agent/test_runtime_refresh.py, tests/agent/test_self_model_preset.py, tests/config/test_model_presets.py, tests/providers/test_enforce_role_alternation.py, tests/providers/test_github_copilot_routing.py, tests/providers/test_provider_retry.py, tests/providers/test_providers_init.py
  Overview
  Data Structures
    · `ToolCallRequest`
    · `LLMResponse`
  Reliability & Failover
    · `FallbackProvider`
    · Message Sanitization
  Provider Configuration & Registry
  Child Pages

## · Provider Selection & Registry  (L4635)
  源文件: README.md, docs/configuration.md, docs/provider-cookbook.md, docs/providers.md, nanobot/agent/model_runtime.py, nanobot/cli/commands.py, nanobot/config/schema.py, nanobot/config/watcher.py, nanobot/providers/factory.py, nanobot/providers/registry.py, nanobot/utils/llm_runtime.py, tests/agent/test_model_runtime_resolver.py
  Purpose and Scope
  The PROVIDERS Registry
  ProviderSpec Structure
    · ProviderSpec Field Reference
  Provider Categories
    · Provider Category Diagram
  Provider Detection Algorithm
    · Detection Flow Diagram
    · Stage 1: Explicit Provider Name
    · Stage 2: Gateway/Local Detection
    · Stage 3: Model Name Matching
  Provider Factory & Failover
    · Core Creation Logic
    · Fallback Handling
  Provider-Specific Overrides
    · Thinking Styles
    · Reasoning Control

## · Provider Implementations  (L4891)
  源文件: nanobot/agent/context_governance.py, nanobot/providers/anthropic_provider.py, nanobot/providers/azure_openai_provider.py, nanobot/providers/github_copilot_provider.py, nanobot/providers/openai_codex_provider.py, nanobot/providers/openai_compat_provider.py, nanobot/providers/openai_responses/converters.py, nanobot/providers/openai_responses/parsing.py, nanobot/providers/openai_responses/state.py, tests/agent/test_context_governance.py, tests/agent/test_runner_governance.py, tests/agent/test_runner_persistence.py
  Base Interface
    · Core Data Structures
    · Shared Logic
  Provider Architecture
  OpenAICompatProvider
    · Thinking and Reasoning
    · Responses API & Circuit Breaker
  AnthropicProvider
  AzureOpenAIProvider
  OpenAICodexProvider
  GitHubCopilotProvider
  OpenAI Responses API Module

## · Tools & Capabilities  (L5105)
  源文件: nanobot/agent/tools/__init__.py, nanobot/agent/tools/base.py, nanobot/agent/tools/registry.py, nanobot/agent/tools/schema.py, tests/tools/test_tool_registry.py, tests/tools/test_tool_validation.py
  Overview
  Core Components
    · The `Tool` Base Class
    · The `ToolRegistry`
    · Discovery and Context
  Tool Categories
    · Built-in Tools
    · MCP Integration
    · Security & Sandboxing
    · CLI Apps (CLI-Anything)
  Tool Execution Lifecycle
  Parameter Validation Schema

## · Built-in Tools  (L5269)
  源文件: .agent/security.md, nanobot/agent/plugins.py, nanobot/agent/tools/_windows_job.py, nanobot/agent/tools/apply_patch.py, nanobot/agent/tools/cron.py, nanobot/agent/tools/exec_session.py, nanobot/agent/tools/filesystem.py, nanobot/agent/tools/message.py, nanobot/agent/tools/path_utils.py, nanobot/agent/tools/search.py, nanobot/agent/tools/shell.py, nanobot/agent/tools/web.py
  Tool Registry
  Tool Registration Flow
  Filesystem Tools
    · ReadFileTool
    · WriteFileTool
    · EditFileTool
    · ListDirTool
  Shell Execution Tool (`ExecTool`)
  Web Tools
    · WebSearchTool
    · WebFetchTool
  Communication & Scheduling
    · MessageTool
    · SpawnTool
    · CronTool
  Data Flow: Natural Language to Tool Execution
  Tool Context Management

## · MCP Integration  (L5554)
  源文件: nanobot/agent/tools/mcp.py, nanobot/security/network.py, nanobot/webui/mcp_presets_api.py, tests/agent/test_mcp_connection.py, tests/agent/test_mcp_transient_retry.py, tests/security/test_security_network.py, tests/tools/test_mcp_probe.py, tests/tools/test_mcp_tool.py, tests/tools/test_web_fetch_security.py, tests/webui/test_mcp_presets_api.py
  Overview
  Architecture
  Wrapper Implementations
    · `MCPToolWrapper`
    · `MCPResourceWrapper`
    · `MCPPromptWrapper`
  Transport Modes
    · Stdio Transport
    · SSE (Server-Sent Events)
    · Streamable HTTP
  Tool Filtering and Progress Handling
    · Tool Filtering
    · Progress Notification Filtering
  Lifecycle Management
    · `MCPProvider`
    · `_OwnedMCPConnection`
  Configuration Reference

## · Security & Sandboxing  (L5751)
  源文件: .agent/security.md, SECURITY.md, docs/openai-api.md, nanobot/agent/plugins.py, nanobot/agent/tools/filesystem.py, nanobot/agent/tools/mcp.py, nanobot/agent/tools/path_utils.py, nanobot/agent/tools/sandbox.py, nanobot/api/server.py, nanobot/security/network.py, nanobot/security/workspace_policy.py, nanobot/utils/document.py
  Security Architecture Overview
    · Tool Security Pipeline
  Access Control
    · Channel-Level Allowlists
    · API Server Security
  Workspace Restriction & Sandboxing
    · Workspace Escape Protection
    · Linux Kernel Isolation (bwrap)
  Shell Command Guards
    · Deny Patterns
    · Environment Isolation
  SSRF Prevention
    · Network Security Logic
  MCP Security & Stability
    · HTTP Probing
    · Transient Error Retries
    · Progress Notification Filtering
  File System Access Safety

## · CLI Apps (CLI-Anything)  (L5994)
  源文件: docs/image-generation.md, nanobot/agent/tools/cli_apps.py, nanobot/agent/tools/image_generation.py, nanobot/apps/cli/service.py, nanobot/providers/image_generation.py, nanobot/webui/cli_apps_api.py, nanobot/webui/nanobot_features_api.py, tests/agent/conftest.py, tests/agent/test_loop_image_generation_media.py, tests/agent/test_workspace_scope.py, tests/apps/test_cli_subprocess_env.py, tests/cli_apps/test_service.py
  Overview and Registry Sources
  CliAppManager Lifecycle
    · Data Flow: Catalog to Execution
    · Key Functions and Classes
  Manifest Format and Capabilities
  Tool Integration: `run_cli_app`
    · Runtime Context Injection
    · Security and Sandboxing
  Image Generation Integration
  WebUI Integration

## · Configuration  (L6155)
  源文件: README.md, docs/configuration.md, docs/provider-cookbook.md, docs/providers.md, nanobot/channels/registry.py, nanobot/cli/commands.py, nanobot/config/loader.py, nanobot/config/schema.py, nanobot/providers/registry.py, tests/cli/test_commands.py, tests/config/test_config_load_errors.py, tests/config/test_dream_config.py
  Configuration File Location
  Configuration Schema
    · Schema Class Hierarchy
  Core Configuration Sections
    · Agents Configuration
    · Providers Configuration
    · Channels Configuration
    · Tools Configuration
  Configuration Loading and Overrides
    · Environment Variable Resolution
    · Runtime Overrides (MyTool)

## · Config Schema Reference  (L6306)
  源文件: README.md, docs/configuration.md, docs/provider-cookbook.md, docs/providers.md, nanobot/agent/model_runtime.py, nanobot/channels/registry.py, nanobot/cli/commands.py, nanobot/config/loader.py, nanobot/config/schema.py, nanobot/config/watcher.py, nanobot/providers/registry.py, nanobot/utils/llm_runtime.py
  Configuration Architecture
    · Data Flow & Validation
  1. Agents Section
    · DreamConfig (Background Consolidation)
  2. Providers Section
    · Supported Provider Keys
    · Model Presets
  3. Channels Section
    · TranscriptionConfig
  4. Tools Section
    · WebToolsConfig
    · ExecToolConfig
    · MCP Servers & Security
    · MyTool (Self-Awareness)
  5. Gateway Section
  Environment Variable Resolution

## · Config Migration & Backfilling  (L6530)
  源文件: nanobot/channels/registry.py, nanobot/command/builtin.py, nanobot/config/loader.py, tests/agent/test_dream_session.py, tests/agent/test_session_atomic.py, tests/cli/test_restart_command.py, tests/command/test_builtin_dream.py, tests/command/test_model_command.py, tests/config/test_config_load_errors.py, tests/config/test_config_migration.py, tests/config/test_dream_config.py, tests/config/test_env_interpolation.py
  Configuration Loading & Migration
    · Migration Logic
    · SSRF Whitelist Application
    · Data Flow: Config Loading
  Environment Variable Resolution
  Recursive Backfilling
    · Implementation Logic
    · Logic Entity Association
  Upgrade Workflow Summary
    · Configuration Save/Load Cycle

## · CLI Reference  (L6702)
  源文件: README.md, docs/README.md, docs/architecture.md, docs/chat-commands.md, docs/cli-reference.md, docs/concepts.md, docs/configuration.md, docs/guides/deploy-nanobot-gateway.md, docs/multiple-instances.md, docs/provider-cookbook.md, docs/providers.md, docs/quick-start.md
  Overview
  Global Flags
  `nanobot onboard`
  `nanobot agent`
    · Single-message mode (`-m`)
    · Interactive mode
  `nanobot webui`
  `nanobot gateway`
    · Startup Sequence
  `nanobot trigger`
  `nanobot serve`
  `nanobot status`
  `nanobot channels`
    · `nanobot channels status`
    · `nanobot channels login`
  `nanobot provider`
    · `nanobot provider login`
  Slash Commands

## · Command Router & Built-in Commands  (L7010)
  源文件: nanobot/cli/models.py, nanobot/command/builtin.py, nanobot/command/router.py, nanobot/pairing/__init__.py, nanobot/pairing/store.py, tests/agent/test_dream_session.py, tests/agent/test_session_atomic.py, tests/channels/test_base_channel.py, tests/cli/test_restart_command.py, tests/command/test_builtin_dream.py, tests/command/test_model_command.py, tests/command/test_router_dispatchable.py
  Overview of Command Routing
    · Command Tiers
  Technical Implementation
    · CommandContext
    · The Dispatch Flow
  Built-in Commands
    · System Control Commands (Priority)
    · Session & Model Commands (Standard)
    · Memory & Dream Commands
  Status Telemetry
  Code Entity Mapping
    · Pairing System Data Flow

## · Automation & Scheduling  (L7201)
  源文件: nanobot/agent/cron_turns.py, nanobot/agent/tools/cron.py, nanobot/cron/service.py, nanobot/cron/session_turns.py, nanobot/cron/types.py, nanobot/triggers/local_runner.py, nanobot/triggers/local_session_turns.py, nanobot/triggers/local_store.py, nanobot/triggers/local_types.py, nanobot/utils/dict_keys.py, nanobot/utils/run_records.py, tests/cron/test_cron_persistence.py
  Overview
  Architecture & Coordination
  CronService
    · Persistence & Safety
    · Session Binding
  Local Triggers
    · Components
  HeartbeatService

## · Cron Service  (L7352)
  源文件: nanobot/agent/tools/cron.py, nanobot/cron/service.py, nanobot/cron/session_turns.py, nanobot/cron/types.py, tests/cron/test_cron_persistence.py, tests/cron/test_cron_service.py, tests/cron/test_cron_tool_list.py
  Overview
  Data Model
    · Schedule Kinds
    · Payload Fields and Migration
  CronService
    · Lifecycle
    · Persistence and Atomic Writes
    · Execution and History
  CronTool
    · Context Binding and Recursion Guard
    · Tool Parameters
  Scheduling Logic
  Session Coordination

## · Heartbeat Service  (L7640)
  源文件: nanobot/agent/automation_turns.py, nanobot/agent/runner.py, nanobot/templates/AGENTS.md, nanobot/templates/HEARTBEAT.md, nanobot/templates/SOUL.md, nanobot/templates/agent/identity.md, nanobot/templates/agent/tool_contract.md, nanobot/templates/legacy/SOUL.md, nanobot/utils/runtime.py, tests/agent/test_context_builder.py, tests/agent/test_context_prompt_cache.py, tests/agent/test_loop_progress.py
  Purpose and Scope
  Three-Phase Workflow
    · Phase 1: Decision
    · Phase 2: Execution
    · Phase 3: Evaluation & Deliverability
  System Architecture
    · Code-to-System Mapping
  Data Flow: Heartbeat State Management
  HEARTBEAT.md and Persistence
  Code Entity Reference

## · Local Triggers  (L7802)
  源文件: nanobot/agent/cron_turns.py, nanobot/triggers/local_runner.py, nanobot/triggers/local_session_turns.py, nanobot/triggers/local_store.py, nanobot/triggers/local_types.py, nanobot/utils/dict_keys.py, nanobot/utils/run_records.py, tests/triggers/test_local_triggers.py
  Architecture and Data Flow
    · Trigger Lifecycle Diagram
  Storage and Persistence
    · Directory Structure
    · Key Classes and Types
  Delivery Mechanism
    · Local Runner Loop
    · Error Handling and Retries
  Agent Integration
    · Coordination Logic Diagram
    · Metadata and History
    · Concurrency and Deferral

## · Session Management  (L7950)
  源文件: nanobot/agent/autocompact.py, nanobot/agent/memory.py, nanobot/session/goal_state.py, nanobot/session/manager.py, nanobot/session/turn_continuation.py, nanobot/skills/memory/SKILL.md, tests/agent/test_auto_compact.py, tests/agent/test_autocompact_unit.py, tests/agent/test_consolidator.py, tests/agent/test_dream.py, tests/agent/test_loop_runner_integration.py, tests/agent/test_memory_store.py
  Purpose and Scope
  Session Architecture
    · Entity Relationship Diagram
  Session Dataclass
    · Key Capabilities
  Session Lifecycle and Persistence
    · Persistence Logic
    · Process Flow: Message to Session
  Memory Consolidation
  Goal State and Internal Continuation

## · Session Lifecycle  (L8137)
  源文件: nanobot/agent/autocompact.py, nanobot/agent/memory.py, nanobot/session/goal_state.py, nanobot/session/manager.py, nanobot/session/turn_continuation.py, nanobot/skills/memory/SKILL.md, tests/agent/test_auto_compact.py, tests/agent/test_autocompact_unit.py, tests/agent/test_consolidator.py, tests/agent/test_dream.py, tests/agent/test_loop_runner_integration.py, tests/agent/test_memory_store.py
  Session Identification and Storage
    · Persistence Mechanism
    · Session Structure
  The Session Lifecycle Flow
    · 1. Initialization and Loading
    · 2. Message Append and Updates
    · 3. Repair and Recovery
    · Session Management Data Flow
  Turn Saving and History Sanitization
    · Handling Orphan Tool Results
    · Assistant Replay Sanitization
    · Multimodal Rehydration
    · History Preparation Logic
  Auto-Compaction and Idle TTL

## · Memory Consolidation  (L8298)
  源文件: nanobot/agent/autocompact.py, nanobot/agent/memory.py, nanobot/session/manager.py, nanobot/skills/memory/SKILL.md, tests/agent/test_auto_compact.py, tests/agent/test_autocompact_unit.py, tests/agent/test_consolidate_offset.py, tests/agent/test_consolidator.py, tests/agent/test_dream.py, tests/agent/test_loop_consolidation_tokens.py, tests/agent/test_memory_store.py, tests/agent/test_session_manager_history.py
  Overview
  Consolidation Workflow
    · The Trigger Logic
    · The Consolidation Tool
    · Data Flow Diagram: Consolidation Loop
  Auto-Compact (Idle Archival)
    · Logic and Retention
  Offset Tracking and Immutability
    · Key Mechanisms
    · Code Entity Space: Session and Consolidation
  Robustness and Cursor Tracking

## · Deployment  (L8462)
  源文件: .dockerignore, .github/workflows/ci.yml, CONTRIBUTING.md, Dockerfile, LICENSE, docker-compose.bwrap.yml, docker-compose.yml, docs/deployment.md, docs/websocket.md, entrypoint.sh, nanobot/channels/websocket/tests/test_websocket_http_routes.py, nanobot/webui/ws_http.py
  Deployment Overview
  Deployment Architecture
    · Gateway vs CLI Mode
    · Configuration Resolution
  Choose a Runtime
  Docker Deployment
    · Security and Sandboxing
    · Docker Compose
  Render Deployment
  CI/CD & Contributing
    · Child Pages

## · Docker & Container Deployment  (L8655)
  源文件: .dockerignore, Dockerfile, docs/deployment.md, docs/websocket.md, entrypoint.sh, nanobot/channels/websocket/tests/test_websocket_http_routes.py, nanobot/webui/ws_http.py, render-config.json, render.yaml
  Dockerfile Structure
    · Build Phases
    · Runtime Configuration
    · Data Flow: Container Initialization
  Docker Compose Configuration
    · Services
    · Volume Persistence
  Container-Specific Considerations
    · Environment Variable Injection
    · Network Binding
    · WebUI Authentication

## · CI/CD & Contributing  (L8808)
  源文件: .github/workflows/ci.yml, CONTRIBUTING.md, LICENSE, docker-compose.bwrap.yml, docker-compose.yml
  GitHub Actions CI Pipeline
    · Workflow Jobs
  Contributing Guidelines
    · Contribution Flow
    · Code Entity Mapping: Development Workflow
  Technical Standards
    · Code Style & Linting
    · Core Design Constraints
    · Modifying CI Workflows

## · Python SDK  (L8956)
  源文件: docs/python-sdk.md, nanobot/agent/hook.py, nanobot/agent/tools/context.py, nanobot/agent/turn_hooks.py, nanobot/nanobot.py, nanobot/runtime_context.py, nanobot/sdk/clients.py, nanobot/sdk/runtime.py, nanobot/sdk/types.py, tests/agent/test_loop_tool_context.py, tests/agent/test_turn_hooks.py, tests/test_nanobot_facade.py
    · Core Components
    · SDK Architecture & Data Flow
    · SDK Quick Start & API Reference
    · AgentHook & Lifecycle Callbacks
    · Session Isolation & Persistence

## · SDK Quick Start & API Reference  (L9101)
  源文件: SECURITY.md, docs/openai-api.md, docs/python-sdk.md, nanobot/agent/hook.py, nanobot/agent/tools/context.py, nanobot/agent/turn_hooks.py, nanobot/api/server.py, nanobot/nanobot.py, nanobot/runtime_context.py, nanobot/sdk/clients.py, nanobot/sdk/runtime.py, nanobot/sdk/types.py
  Quick Start
  Core API Reference
    · Nanobot Class
    · RunResult
  Data Flow & Architecture
    · SDK Execution and Data Capture
    · Initialization Sequence
  Session Management
    · Session Client (`bot.sessions`)
    · Usage and Isolation Example
  Advanced Usage: Streaming
    · Event Types

## · AgentHook & Lifecycle Callbacks  (L9316)
  源文件: docs/python-sdk.md, nanobot/agent/automation_turns.py, nanobot/agent/hook.py, nanobot/agent/runner.py, nanobot/agent/tools/context.py, nanobot/agent/turn_hooks.py, nanobot/nanobot.py, nanobot/runtime_context.py, nanobot/sdk/clients.py, nanobot/sdk/runtime.py, nanobot/sdk/types.py, nanobot/utils/runtime.py
  Overview of AgentHook
    · The Hook Contexts
  Lifecycle Methods
    · `before_run` & `after_run`
    · `before_iteration` & `after_iteration`
    · `on_stream` & `on_stream_end`
    · `emit_reasoning` & `emit_reasoning_end`
    · `before_execute_tools` & `before_execute_tool`
    · `finalize_content`
  Code Entity Interaction Diagram
  Composing Multiple Hooks
    · Error Isolation
    · Turn-Scoped Hook Assembly
  Implementation Example

## · WebUI  (L9526)
  源文件: nanobot/channels/weixin/state.py, nanobot/cli/webui.py, nanobot/cli/webui_support.py, nanobot/webui/dev.py, tests/webui/test_dev.py, webui/README.md, webui/src/App.tsx, webui/src/components/ChatList.tsx, webui/src/components/settings/SettingsView.tsx, webui/src/components/thread/ThreadComposer.tsx, webui/src/components/thread/ThreadShell.tsx, webui/src/tests/app-layout.test.tsx
  High-Level Architecture
    · Communication & Protocol
    · Visual Interface
    · System Component Mapping
  Core Functionalities
    · 1. Real-time Streaming
    · 2. Session & Persistence
    · 3. Settings & i18n
  Interaction Flow
  Detailed Documentation

## · WebUI Architecture & Components  (L9660)
  源文件: nanobot/webui/gateway_tokens.py, nanobot/webui/transcript.py, tests/utils/test_webui_transcript.py, webui/src/App.tsx, webui/src/components/ChatList.tsx, webui/src/components/CliAppMentionText.tsx, webui/src/components/CodeBlock.tsx, webui/src/components/FilePreviewPanel.tsx, webui/src/components/InlineTokenHighlight.tsx, webui/src/components/MarkdownTextRenderer.tsx, webui/src/components/MessageBubble.tsx, webui/src/components/SlashCommandText.tsx
  Tech Stack & Core Patterns
    · Data Flow Overview
  Core Components
    · 1. ThreadShell
    · 2. MessageBubble
    · 3. Sidebar & ChatList
    · 4. ThreadComposer
  WebSocket Streaming Protocol
    · Event Types & Handling
    · Stream Processing Flow
  View Architecture & Routing

## · WebUI Development & i18n  (L9845)
  源文件: nanobot/webui/http_utils.py, tests/webui/test_static_assets.py, webui/bun.lock, webui/index.html, webui/package-lock.json, webui/package.json, webui/public/brand/nanobot_icon_192.png, webui/public/brand/nanobot_icon_512.png, webui/public/brand/nanobot_icon_maskable.png, webui/public/manifest.json, webui/public/sw.js, webui/src/components/thread/WorkspaceControls.tsx
  Development Workflow
    · Vite HMR Dev Workflow
    · Build Process
    · Data Flow: Dev vs Production
  Internationalization (i18n)
    · Locale Structure
    · Translation Entity Mapping
  Adding New Languages
    · Language Features
  Testing i18n

## · Glossary  (L10014)
  源文件: README.md, docs/configuration.md, docs/provider-cookbook.md, docs/providers.md, nanobot/agent/autocompact.py, nanobot/agent/automation_turns.py, nanobot/agent/context.py, nanobot/agent/loop.py, nanobot/agent/memory.py, nanobot/agent/runner.py, nanobot/agent/subagent.py, nanobot/agent/tools/_windows_job.py
  Core Concepts
    · Agent Loop
    · Message Bus
    · Context Builder
    · Subagent
  System Architecture Diagrams
    · Natural Language to Code Entity Mapping
    · Data Flow: Message Processing
  Technical Terms & Jargon
  Implementation Specifics
    · Provider Architecture
    · Session & History Persistence
    · Image & Media Handling
    · Shell Execution & Security