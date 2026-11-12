# Skeleton: agency-swarm（39 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 7KB | 2 | ~0 | 18 |
| 2 | Architecture | L158 | 8KB | 3 | ~2 | 20 |
| 3 | Key Concepts | L334 | 8KB | 2 | ~0 | 25 |
| 4 | Core Framework | L483 | 9KB | 4 | ~0 | 15 |
| 5 | Agency Class | L685 | 11KB | 2 | ~3 | 17 |
| 6 | Agent Class | L896 | 8KB | 3 | ~4 | 20 |
| 7 | Thread System | L1071 | 8KB | 2 | ~1 | 20 |
| 8 | BaseTool Class | L1211 | 8KB | 2 | ~3 | 17 |
| 9 | Tool System | L1369 | 7KB | 2 | ~0 | 16 |
| 10 | ToolFactory | L1512 | 9KB | 3 | ~2 | 24 |
| 11 | Built-in Tools | L1704 | 10KB | 2 | ~2 | 29 |
| 12 | MCP Integration | L1875 | 7KB | 2 | ~1 | 18 |
| 13 | Agent Communication | L2011 | 6KB | 2 | ~0 | 14 |
| 14 | Message System | L2131 | 7KB | 2 | ~1 | 10 |
| 15 | Communication Flows | L2256 | 9KB | 2 | ~1 | 26 |
| 16 | Specialized Agents | L2429 | 5KB | 2 | ~1 | 9 |
| 17 | BrowsingAgent | L2561 | 6KB | 2 | ~1 | 12 |
| 18 | Genesis Agency | L2718 | 7KB | 2 | ~2 | 18 |
| 19 | OpenClaw Agent | L2885 | 9KB | 2 | ~4 | 21 |
| 20 | Advanced Features | L3043 | 6KB | 1 | ~4 | 10 |
| 21 | Observability | L3171 | 8KB | 3 | ~1 | 24 |
| 22 | Asynchronous Processing | L3336 | 10KB | 2 | ~1 | 24 |
| 23 | CLI Interface | L3503 | 7KB | 2 | ~0 | 16 |
| 24 | Voice Agents and Realtime | L3654 | 8KB | 2 | ~3 | 17 |
| 25 | Visualization | L3813 | 8KB | 2 | ~2 | 10 |
| 26 | FastAPI Integration | L3970 | 7KB | 2 | ~0 | 12 |
| 27 | Server Setup and Endpoints | L4102 | 9KB | 2 | ~2 | 22 |
| 28 | Request Lifecycle and Client Config | L4250 | 9KB | 2 | ~2 | 12 |
| 29 | File Handling | L4403 | 8KB | 2 | ~1 | 12 |
| 30 | MCP OAuth in FastAPI | L4567 | 9KB | 2 | ~2 | 19 |
| 31 | Guides and Tutorials | L4748 | 8KB | 3 | ~0 | 21 |
| 32 | Getting Started | L4957 | 6KB | 2 | ~0 | 11 |
| 33 | Creating Custom Agents | L5167 | 9KB | 2 | ~2 | 25 |
| 34 | Creating Custom Tools | L5338 | 9KB | 1 | ~2 | 17 |
| 35 | Demos and Examples | L5541 | 10KB | 2 | ~2 | 30 |
| 36 | Infrastructure and Development | L5722 | 5KB | 2 | ~0 | 14 |
| 37 | Build and Configuration | L5862 | 6KB | 2 | ~4 | 6 |
| 38 | Testing and CI | L5990 | 6KB | 2 | ~2 | 10 |
| 39 | Glossary | L6134 | 10KB | 2 | ~2 | 30 |


## · Overview  (L6)
  源文件: README.md, docs/additional-features/azure-openai.mdx, docs/additional-features/observability.mdx, docs/additional-features/streaming.mdx, docs/core-framework/tools/custom-tools/step-by-step-guide.mdx, docs/docs.json, docs/faq.mdx, docs/platform/how-credits-work.mdx, docs/platform/overview.mdx, docs/platform/pricing.mdx, docs/welcome/ai-agency-vs-other-frameworks.mdx, docs/welcome/getting-started/from-scratch.mdx
  Framework Architecture
  Communication Flow
  Key Components
    · Agency
    · Agent
    · Tool System
    · Persistence and Threads
  Key Features
  Exploration Guide

## · Architecture  (L158)
  源文件: README.md, docs/additional-features/azure-openai.mdx, docs/additional-features/observability.mdx, docs/core-framework/tools/custom-tools/step-by-step-guide.mdx, docs/welcome/getting-started/from-scratch.mdx, src/agency_swarm/__init__.py, src/agency_swarm/agency/core.py, src/agency_swarm/agent/conversation_starters_cache.py, src/agency_swarm/agent/conversation_starters_streaming.py, src/agency_swarm/agent/execution.py, src/agency_swarm/agent/execution_helpers.py, src/agency_swarm/agent/execution_streaming.py
  Core Framework Architecture
    · System Hierarchy
  Component Architecture
    · The Agency Class
    · The Agent Class
    · Thread & Message Management
  Execution Data Flow
    · get_response Pipeline
    · Mapping Natural Language to Code Entities
  Advanced Execution Features
    · Streaming and Guardrails
    · Observability Integration

## · Key Concepts  (L334)
  源文件: .claude/agents/agent-creator.md, .claude/agents/tools-creator.md, README.md, docs/additional-features/agency-context.mdx, docs/additional-features/azure-openai.mdx, docs/additional-features/custom-communication-flows/common-use-cases.mdx, docs/additional-features/custom-communication-flows/overview.mdx, docs/additional-features/fastapi-integration.mdx, docs/additional-features/observability.mdx, docs/core-framework/agents/advanced-configuration.mdx, docs/core-framework/agents/overview.mdx, docs/core-framework/tools/custom-tools/best-practices.mdx
  Core Entities
    · Agency
    · Agent
    · Thread Management
  Communication Concepts
    · SendMessage and Handoffs
    · MasterContext
  Execution and Guardrails
    · Guardrails
    · System Reminders
  Tooling Primitives
    · BaseTool
    · Model Context Protocol (MCP)

## · Core Framework  (L483)
  源文件: src/agency_swarm/agency/core.py, src/agency_swarm/agency/helpers.py, src/agency_swarm/agency/setup.py, src/agency_swarm/agent/constants.py, src/agency_swarm/agent/conversation_starters_cache.py, src/agency_swarm/agent/conversation_starters_streaming.py, src/agency_swarm/agent/core.py, src/agency_swarm/agent/initialization.py, tests/integration/agency/test_shared_resources.py, tests/test_agency_modules/test_agency_helpers.py, tests/test_agency_modules/test_agency_initialization.py, tests/test_agency_modules/test_agent_flow_integration.py
  Architecture Overview
  Natural Language to Code Mapping
    · Agency Orchestration Space
    · Agent Capability Space
  Components in Detail
    · Agency
    · Agent
    · Thread System
    · BaseTool
  Data Flow and Communication
  Initialization Pipeline

## · Agency Class  (L685)
  源文件: docs/additional-features/deployment-to-production.mdx, docs/core-framework/agencies/communication-flows.mdx, src/agency_swarm/agency/core.py, src/agency_swarm/agency/helpers.py, src/agency_swarm/agency/responses.py, src/agency_swarm/agency/setup.py, src/agency_swarm/agent/conversation_starters_cache.py, src/agency_swarm/agent/conversation_starters_streaming.py, tests/integration/agency/test_shared_resources.py, tests/test_agency_modules/_response_test_helpers.py, tests/test_agency_modules/test_agency_helpers.py, tests/test_agency_modules/test_agency_initialization.py
  Architecture Overview
    · Code Entity Mapping
  Initialization and Setup
    · Constructor Parameters
    · Initialization Pipeline
  Communication Methods
    · get_response
    · get_response_stream
    · Recipient Reminders
  Persistence and Hooks
  FastAPI Integration
  Visualization

## · Agent Class  (L896)
  源文件: src/agency_swarm/agent/__init__.py, src/agency_swarm/agent/constants.py, src/agency_swarm/agent/core.py, src/agency_swarm/agent/file_manager.py, src/agency_swarm/agent/file_sync.py, src/agency_swarm/agent/initialization.py, src/agency_swarm/agent/subagents.py, src/agency_swarm/agent/tools.py, src/agency_swarm/cli/main.py, src/agency_swarm/utils/create_agent_template.py, src/agency_swarm/utils/model_utils.py, tests/integration/cli/test_create_agent_template_integration.py
  Agent Class Architecture
  Initialization Pipeline
    · Framework Defaults
  Capabilities and Configuration
    · Tool Discovery
    · File Management
    · Guardrails and Reminders
  Execution Data Flow
  Deprecated Parameters
  Technical Reference: Capability Detection

## · Thread System  (L1071)
  源文件: examples/agency_context.py, examples/custom_persistence.py, examples/fastapi_integration/client.py, examples/handoffs.py, examples/interactive/hybrid_communication_flows.py, examples/multi_agent_workflow.py, examples/streaming.py, src/agency_swarm/messages/message_formatter.py, src/agency_swarm/utils/thread.py, tests/integration/communication/test_streaming_order_consistency.py, tests/integration/litellm_integration/test_litellm_anthropic_message_ordering.py, tests/integration/litellm_integration/test_litellm_anthropic_nonstreaming.py
  Overview
    · Architecture and Data Flow
  Core Components
    · ThreadManager
    · MessageStore
    · MessageFormatter
  Thread Lifecycle and Persistence
    · Initialization and Loading
    · Message Addition and Saving
  History Protocols and Compatibility
    · Ephemeral Content
  Multi-Agent Interaction Handling

## · BaseTool Class  (L1211)
  源文件: docs/core-framework/tools/built-in-tools.mdx, docs/core-framework/tools/custom-tools/multimodal-outputs.mdx, docs/core-framework/tools/overview.mdx, examples/data/daily_revenue.png, examples/data/daily_revenue_report.pdf, examples/multimodal_outputs.py, src/agency_swarm/tools/base_tool.py, src/agency_swarm/tools/tool_factory_utils/base_tool_adapter.py, src/agency_swarm/tools/utils.py, src/agency_swarm/utils/dry_run.py, tests/integration/communication/test_send_message_extra_params.py, tests/integration/fastapi/test_fastapi_dry_run.py
  Overview
    · Core Class Structure
  Key Components
    · Pydantic Field Definitions
    · The ToolConfig Class
    · MasterContext Access
  Implementation Flow: From Code to SDK
    · Adaptation Details
  Multimodal Outputs
    · Multimodal Utilities
  Extending BaseTool
  Advanced Usage: Extra Params in SendMessage

## · Tool System  (L1369)
  源文件: examples/fastapi_integration/print_openapi_schema.py, src/agency_swarm/cli/import_tool.py, src/agency_swarm/tools/built_in/IPythonInterpreter.py, src/agency_swarm/tools/built_in/LoadFileAttachment.py, src/agency_swarm/tools/built_in/PersistentShellTool.py, src/agency_swarm/tools/built_in/PresentFiles.py, src/agency_swarm/tools/built_in/__init__.py, src/agency_swarm/tools/mcp_manager.py, src/agency_swarm/tools/tool_factory.py, tests/integration/tools/test_present_files_tool.py, tests/test_agent_modules/test_mcp_manager.py, tests/test_agent_modules/test_mcp_oauth.py
  Tool System Architecture
  BaseTool Class
    · Key Features
  ToolFactory
  Built-in Tools
  MCP Integration
  Tool Execution Lifecycle

## · ToolFactory  (L1512)
  源文件: examples/fastapi_integration/print_openapi_schema.py, src/agency_swarm/integrations/fastapi_utils/logging_middleware.py, src/agency_swarm/integrations/fastapi_utils/tool_endpoints.py, src/agency_swarm/integrations/fastapi_utils/tool_request_models.py, src/agency_swarm/tools/function_tool_compat.py, src/agency_swarm/tools/tool_factory.py, src/agency_swarm/tools/tool_factory_utils/__init__.py, src/agency_swarm/tools/tool_factory_utils/factory.py, src/agency_swarm/tools/tool_factory_utils/file_loader.py, src/agency_swarm/tools/tool_factory_utils/langchain.py, src/agency_swarm/tools/tool_factory_utils/mcp.py, src/agency_swarm/tools/tool_factory_utils/openapi_exporter.py
  Purpose and Scope
  Overview
    · Tool Factory Architecture
  Tool Creation Methods
  Adaptation and Compatibility
    · Data Flow: BaseTool to FunctionTool
    · Context Preservation
  Specialized Importers
    · OpenAPI Integration
    · MCP Integration
    · LangChain Integration
  Tool Factory Utilities
  Integration with FastAPI

## · Built-in Tools  (L1704)
  源文件: docs/additional-features/guardrails/input-guardrails.mdx, docs/additional-features/guardrails/output-guardrails.mdx, docs/core-framework/agents/built-in-tools.mdx, docs/platform/marketplace/onboarding.mdx, examples/README.md, examples/guardrails_input.py, examples/interactive/third_party_models.py, examples/interactive/tui.py, examples/observability.py, src/agency_swarm/agent/attachment_manager.py, src/agency_swarm/agent/file_manager.py, src/agency_swarm/agent/file_sync.py
  Core Built-in Tools
    · IPythonInterpreter
    · PersistentShellTool
    · PresentFiles
    · LoadFileAttachment
  File and Attachment Management
    · AgentFileManager
    · AttachmentManager
  Hosted Tool Compatibility
    · Compatibility Logic
  Tool Summary Table

## · MCP Integration  (L1875)
  源文件: docs/additional-features/mcp-tools-server.mdx, examples/mcp_servers.py, examples/utils/sse_mcp_server.py, examples/utils/stdio_mcp_server.py, src/agency_swarm/integrations/mcp_server.py, src/agency_swarm/mcp/oauth_flow.py, src/agency_swarm/tools/hosted_mcp_activation.py, src/agency_swarm/tools/mcp_converter.py, src/agency_swarm/tools/mcp_loop_proxy.py, src/agency_swarm/tools/mcp_manager.py, src/agency_swarm/tools/mcp_oauth_bridge.py, src/agency_swarm/tools/mcp_persistence.py
  Overview and Architecture
    · Data Flow and Materialization
  Key Components
    · PersistentMCPServerManager
    · LoopAffineAsyncProxy
    · mcp_converter
  Server Transports
  Hosted MCP Tools
  Serving Tools via MCP
  OAuth and Persistence Keys

## · Agent Communication  (L2011)
  源文件: .claude/agents/agent-creator.md, .claude/agents/tools-creator.md, docs/additional-features/agency-context.mdx, docs/additional-features/custom-communication-flows/common-use-cases.mdx, docs/additional-features/custom-communication-flows/overview.mdx, docs/core-framework/tools/custom-tools/best-practices.mdx, docs/core-framework/tools/custom-tools/configuration.mdx, examples/custom_send_message.py, src/agency_swarm/agent/execution.py, src/agency_swarm/agent/execution_helpers.py, src/agency_swarm/agent/execution_streaming.py, src/agency_swarm/context.py
  Communication Architecture
  Core Communication Tools
    · SendMessage Tool
    · Handoff Tool
  The Message System and Context
    · MasterContext and Shared State
    · Message Formatting and Persistence
  Communication Lifecycle
  Sub-pages

## · Message System  (L2131)
  源文件: src/agency_swarm/messages/__init__.py, src/agency_swarm/messages/codex_input.py, src/agency_swarm/messages/message_formatter.py, src/agency_swarm/streaming/id_normalizer.py, tests/test_agent_modules/test_hosted_tool_results.py, tests/test_agent_modules/test_stream_id_normalization.py, tests/test_fastapi_utils_modules/_codex_input_role_boundary_helpers.py, tests/test_fastapi_utils_modules/test_codex_endpoint_role_boundary.py, tests/test_fastapi_utils_modules/test_codex_input_role_boundary.py, tests/test_messages_modules/test_message_formatter_history_protocol.py
  Overview
  MessageFormatter
    · History Protocols
    · Key Functions
  Codex Input Handling
  Stream ID Normalization
  Data Flow and Persistence
    · Filtering and Sanitization

## · Communication Flows  (L2256)
  源文件: .claude/agents/agent-creator.md, .claude/agents/tools-creator.md, docs/additional-features/agency-context.mdx, docs/additional-features/custom-communication-flows/common-use-cases.mdx, docs/additional-features/custom-communication-flows/overview.mdx, docs/additional-features/deployment-to-production.mdx, docs/core-framework/agencies/communication-flows.mdx, docs/core-framework/tools/custom-tools/best-practices.mdx, docs/core-framework/tools/custom-tools/configuration.mdx, examples/custom_send_message.py, src/agency_swarm/integrations/fastapi_utils/tool_endpoints.py, src/agency_swarm/tools/function_tool_compat.py
  Key Concepts in Agent Communication
  Defining Communication Flows
    · Orchestration Patterns
    · Syntax and Configuration
  The SendMessage Tool
    · Blocking and Concurrency Behavior
    · Custom SendMessage Configurations
  The Handoff Mechanism
    · Handoff Reminders
  Data Flow and Context Isolation
    · Agency Context
  Implementation Details
    · Tool Compatibility and Normalization

## · Specialized Agents  (L2429)
  源文件: .cursor/rules/writing-docs.mdc, docs/images/platform/openclaw-persistent-storage.png, docs/platform/integrations/openclaw-integration.mdx, docs/platform/marketplace/openclaw.mdx, src/agency_swarm/agents/openclaw.py, src/agency_swarm/integrations/README.md, src/agency_swarm/integrations/openclaw.py, src/agency_swarm/integrations/openclaw_model.py, tests/test_agent_modules/test_openclaw_agent.py
  Overview of Specialized Agents
  BrowsingAgent
    · Capabilities
  Genesis Agency
    · Components
  OpenClaw Agent
    · Key Constraints
    · Integration Architecture
  Comparison of Specialized Agents

## · BrowsingAgent  (L2561)
  源文件: docs/additional-features/guardrails/input-guardrails.mdx, docs/additional-features/guardrails/output-guardrails.mdx, docs/core-framework/agents/built-in-tools.mdx, docs/platform/marketplace/onboarding.mdx, examples/README.md, examples/guardrails_input.py, examples/interactive/third_party_models.py, examples/interactive/tui.py, examples/observability.py, src/agency_swarm/__init__.py, src/agency_swarm/tools/__init__.py, tests/test_agency_modules/test_package_exports.py
  Architecture Overview
  Core Capabilities
  Tool Integration
  Configuration
  Integration with Communication Flows
  Implementation Details
    · Model Settings and Reasoning
    · Handling Results

## · Genesis Agency  (L2718)
  源文件: .pre-commit-config.yaml, CONTRIBUTING.md, docs/contributing/contributing.mdx, package.json, src/agency_swarm/cli/__init__.py, src/agency_swarm/cli/main.py, src/agency_swarm/cli/migrate_agent.py, src/agency_swarm/cli/utils/__init__.py, src/agency_swarm/cli/utils/generate-agent-from-settings.ts, src/agency_swarm/hooks.py, src/agency_swarm/utils/create_agent_template.py, src/agency_swarm/utils/model_utils.py
  Architecture Overview
  CLI Agent Creation Workflow
    · Command Execution
    · The `create_agent_template` Utility
  Agent Template Structure
  Migration Utility
  Model Capability Detection

## · OpenClaw Agent  (L2885)
  源文件: .cursor/rules/writing-docs.mdc, docs/core-framework/third-party-agents/openclaw-agent.mdx, docs/images/platform/openclaw-persistent-storage.png, docs/platform/integrations/openclaw-integration.mdx, docs/platform/marketplace/openclaw.mdx, src/agency_swarm/agents/__init__.py, src/agency_swarm/agents/openclaw.py, src/agency_swarm/integrations/README.md, src/agency_swarm/integrations/openclaw.py, src/agency_swarm/integrations/openclaw_model.py, tests/integration/fastapi/_openclaw_test_support.py, tests/integration/fastapi/test_openclaw_current_app_defaults.py
  Architecture and Data Flow
    · System Integration Map
  OpenClawAgent Class
    · Key Constraints
    · Configuration Parameters
  OpenClawRuntime and Lifecycle
    · Lifecycle Management
  Model Aliasing and Proxy
  Tool Modes: Full vs. Worker
  Environment Configuration

## · Advanced Features  (L3043)
  源文件: docs/additional-features/third-party-models.mdx, docs/core-framework/agencies/agent-swarm-cli.mdx, docs/core-framework/agencies/running-agency.mdx, docs/images/agent-swarm-cli-preview.png, src/agency_swarm/data/model_prices_and_context_window.json, src/agency_swarm/ui/demos/compact.py, src/agency_swarm/utils/usage_tracking.py, tests/integration/ui/test_compact_client_passthrough.py, tests/test_agent_modules/test_default_model_contract.py, tests/test_utils_modules/test_usage_tracking_costs.py
  Observability
    · Usage and Cost Tracking
  Asynchronous Processing
  CLI Interface
  Voice Agents and Realtime
  Visualization
  Summary of Advanced Entities

## · Observability  (L3171)
  源文件: docs/additional-features/guardrails/input-guardrails.mdx, docs/additional-features/guardrails/output-guardrails.mdx, docs/core-framework/agents/built-in-tools.mdx, docs/platform/marketplace/onboarding.mdx, examples/README.md, examples/guardrails_input.py, examples/interactive/third_party_models.py, examples/interactive/tui.py, examples/observability.py, examples/web_search.py, src/agency_swarm/data/model_prices_and_context_window.json, src/agency_swarm/ui/demos/compact.py
  Usage Tracking and Cost Calculation
    · Usage Data Structures
    · Pricing Engine
  Tracing Integrations
    · Native Tracing
    · Langfuse and AgentOps
  Citation Extraction
    · Supported Citation Types
    · Data Flow for Citations
  Thread Compaction

## · Asynchronous Processing  (L3336)
  源文件: examples/fastapi_integration/README.md, src/agency_swarm/agent/execution.py, src/agency_swarm/agent/execution_guardrails.py, src/agency_swarm/agent/execution_helpers.py, src/agency_swarm/agent/execution_stream_persistence.py, src/agency_swarm/agent/execution_stream_response.py, src/agency_swarm/agent/execution_streaming.py, src/agency_swarm/context.py, src/agency_swarm/messages/message_filter.py, src/agency_swarm/streaming/__init__.py, src/agency_swarm/streaming/utils.py, src/agency_swarm/tools/send_message.py
  Overview
  Streaming Execution
    · StreamingRunResponse and EventStreamMerger
    · Key Functions
  Guardrail Handling in Streams
    · Input Guardrails
    · Output Guardrails
  Execution Stream Persistence
  Message Filtering and ID Normalization
    · MessageFilter
    · StreamIdNormalizer
  Deterministic Ordering

## · CLI Interface  (L3503)
  源文件: docs/additional-features/third-party-models.mdx, docs/core-framework/agencies/agent-swarm-cli.mdx, docs/core-framework/agencies/running-agency.mdx, docs/images/agent-swarm-cli-preview.png, src/agency_swarm/cli/__init__.py, src/agency_swarm/cli/main.py, src/agency_swarm/cli/migrate_agent.py, src/agency_swarm/cli/utils/__init__.py, src/agency_swarm/cli/utils/generate-agent-from-settings.ts, src/agency_swarm/utils/create_agent_template.py, src/agency_swarm/utils/model_utils.py, tests/integration/cli/test_create_agent_template_integration.py
  Overview of CLI Commands
    · Code to Entity Mapping: CLI Entrypoint
  Command Details
    · create-agent-template
    · import-tool
    · migrate-agent
  TypeScript Migration Utility
    · Data Flow: Migration Utility
  Terminal User Interface (TUI)

## · Voice Agents and Realtime  (L3654)
  源文件: docs/additional-features/guardrails/input-guardrails.mdx, docs/additional-features/guardrails/output-guardrails.mdx, docs/additional-features/voice-agents/deployment.mdx, docs/additional-features/voice-agents/overview.mdx, docs/core-framework/agents/built-in-tools.mdx, docs/platform/marketplace/onboarding.mdx, examples/README.md, examples/guardrails_input.py, examples/interactive/third_party_models.py, examples/interactive/tui.py, examples/observability.py, src/agency_swarm/integrations/fastapi.py
  Realtime Architecture
    · Data Flow and Lifecycle
  Key Classes and Entities
    · RealtimeAgency and RealtimeAgent
    · Code Entity Mapping
  Configuration and Deployment
    · WebSocket Endpoint Configuration
    · Twilio Integration
  Implementation Details
    · Session Management
    · Request Scoped Overrides

## · Visualization  (L3813)
  源文件: docs/core-framework/agencies/visualization.mdx, src/agency_swarm/agency/visualization.py, src/agency_swarm/ui/core/layout_algorithms.py, src/agency_swarm/ui/demos/copilot.py, src/agency_swarm/ui/demos/copilot/app/api/copilotkit/route.ts, src/agency_swarm/ui/demos/copilot/package.json, src/agency_swarm/ui/generators/html_generator.py, src/agency_swarm/ui/templates/html/visualization.js, src/agency_swarm/utils/serialization.py, tests/test_agency_modules/test_ui.py
  Overview of Visualization Methods
    · Data Flow for Agency Visualization
  Layout Algorithms
    · Hierarchical Layout
  Interactive HTML Generator
    · Implementation Details
    · Browser Interaction
  Metadata and ReactFlow Integration
    · Node and Edge Schema
  Technical Architecture Diagram
  Specialized Visualizers
    · Terminal UI (TUI)
    · Copilot Demo

## · FastAPI Integration  (L3970)
  源文件: docs/additional-features/fastapi-integration.mdx, docs/core-framework/agents/advanced-configuration.mdx, docs/core-framework/agents/overview.mdx, docs/core-framework/tools/mcp-integration.mdx, docs/core-framework/tools/mcp-oauth.mdx, docs/references/api.mdx, src/agency_swarm/integrations/fastapi.py, src/agency_swarm/integrations/fastapi_utils/endpoint_handlers.py, src/agency_swarm/integrations/fastapi_utils/request_models.py, tests/integration/fastapi/test_fastapi_client_config.py, tests/test_fastapi_utils_modules/test_openai_client_config_models.py, tests/test_fastapi_utils_modules/test_openai_client_config_request_state.py
  Architecture Overview
    · Natural Language to Code Entity Mapping
  Core Components
    · 7.1 Server Setup and Endpoints
    · 7.2 Request Lifecycle and Client Config
    · 7.3 File Handling
    · 7.4 MCP OAuth in FastAPI
  Request Flow Diagram

## · Server Setup and Endpoints  (L4102)
  源文件: docs/additional-features/fastapi-integration.mdx, docs/core-framework/agents/advanced-configuration.mdx, docs/core-framework/agents/overview.mdx, docs/core-framework/tools/mcp-integration.mdx, docs/core-framework/tools/mcp-oauth.mdx, docs/references/api.mdx, src/agency_swarm/integrations/fastapi.py, src/agency_swarm/integrations/fastapi_utils/endpoint_handlers.py, src/agency_swarm/integrations/fastapi_utils/logging_middleware.py, src/agency_swarm/integrations/fastapi_utils/override_policy.py, src/agency_swarm/integrations/fastapi_utils/request_models.py, src/agency_swarm/ui/demos/agentswarm_cli.py
  Core Server Initialization
    · The `run_fastapi()` Function
  Generated Endpoints
    · 1. Response Endpoints
    · 2. Metadata and Realtime
    · 3. Tool and Auth Endpoints
  System Architecture: Natural Language to Code Bridge
    · Request Flow and Entity Mapping
    · Server Component Relationships
  Middleware and Security
    · CORS Configuration
    · Logging Middleware
    · ag-ui Protocol Bridge

## · Request Lifecycle and Client Config  (L4250)
  源文件: src/agency_swarm/integrations/fastapi.py, src/agency_swarm/integrations/fastapi_utils/endpoint_handlers.py, src/agency_swarm/integrations/fastapi_utils/override_policy.py, src/agency_swarm/integrations/fastapi_utils/request_models.py, src/agency_swarm/ui/demos/agentswarm_cli.py, tests/integration/fastapi/test_fastapi_client_config.py, tests/integration/fastapi/test_fastapi_metadata.py, tests/test_agency_modules/test_agentswarm_cli_tui.py, tests/test_fastapi_utils_modules/test_openai_client_config_models.py, tests/test_fastapi_utils_modules/test_openai_client_config_request_state.py, tests/test_fastapi_utils_modules/test_openai_client_config_response_overrides.py, tests/test_fastapi_utils_modules/test_override_policy.py
  Overview of the Request Lifecycle
    · Request Entity Mapping
  ClientConfig Overrides
    · Model Swap Logic
  Request Coordination and Locking
    · Locking Strategy
  ActiveRunRegistry and Stream Cancellation
  Data Flow: Client Override Implementation

## · File Handling  (L4403)
  源文件: src/agency_swarm/agent/file_manager.py, src/agency_swarm/agent/file_sync.py, src/agency_swarm/integrations/fastapi_utils/file_handler.py, tests/integration/fastapi/test_fastapi_file_processing.py, tests/integration/files/test_file_handling.py, tests/test_agent_modules/test_agent_file_manager.py, tests/test_agent_modules/test_file_sync.py, tests/test_agent_modules/test_tools_utils.py, tests/test_fastapi_utils_modules/test_endpoint_handlers.py, tests/test_fastapi_utils_modules/test_endpoint_handlers_final_messages_payload.py, tests/test_fastapi_utils_modules/test_file_handler.py, tests/test_fastapi_utils_modules/test_file_handler_downloads.py
  File Attachment Pipeline
    · Data Flow Overview
    · File Handling Architecture
  Agent File Management
    · Core Functions
    · File Synchronization Logic
  AG-UI Content Parts
    · Content Types
    · Implementation Mapping
  Security and Validation

## · MCP OAuth in FastAPI  (L4567)
  源文件: docs/additional-features/fastapi-integration.mdx, docs/core-framework/agents/advanced-configuration.mdx, docs/core-framework/agents/overview.mdx, docs/core-framework/tools/mcp-integration.mdx, docs/core-framework/tools/mcp-oauth.mdx, docs/references/api.mdx, examples/fastapi_integration/notion_hosted_mcp_tool.py, examples/fastapi_integration/oauth_agency.py, examples/mcp_oauth/README.md, src/agency_swarm/mcp/oauth.py, src/agency_swarm/mcp/oauth_client.py, src/agency_swarm/mcp/oauth_config.py
  Deferred Authentication Strategy
    · Natural Language to Code Entity Mapping: Auth Flow
  Data Flow and Architecture
    · MCP OAuth Lifecycle Diagram
  Token Isolation and Storage
    · OAuthStorageHooks
    · FileTokenStorage
    · Configuration Parameters
  FastAPI Endpoints and Streaming
    · Event Sequence
    · Auth Endpoints
  Hosted MCP OAuth Activation
    · Tool Injection Logic
    · Entity Mapping: MCP Persistence

## · Guides and Tutorials  (L4748)
  源文件: README.md, docs/additional-features/azure-openai.mdx, docs/additional-features/guardrails/input-guardrails.mdx, docs/additional-features/guardrails/output-guardrails.mdx, docs/additional-features/observability.mdx, docs/core-framework/agents/built-in-tools.mdx, docs/core-framework/tools/custom-tools/step-by-step-guide.mdx, docs/platform/marketplace/onboarding.mdx, docs/welcome/getting-started/from-scratch.mdx, examples/README.md, examples/agency_context.py, examples/custom_persistence.py
  Tutorial Structure and Learning Path
  Tutorial Implementation Workflow
  Key Tutorials Overview
    · Getting Started
    · Creating Custom Agents
    · Creating Custom Tools
    · Demos and Examples
  System Entity Mapping
  Common Implementation Patterns
    · Basic Agency Setup Pattern
    · Custom Tool Creation Pattern (`@function_tool`)
  Next Steps

## · Getting Started  (L4957)
  源文件: README.md, docs/additional-features/azure-openai.mdx, docs/additional-features/few-shot-examples.mdx, docs/additional-features/observability.mdx, docs/additional-features/streaming.mdx, docs/core-framework/agencies/overview.mdx, docs/core-framework/tools/custom-tools/step-by-step-guide.mdx, docs/faq.mdx, docs/migration/guide.mdx, docs/welcome/getting-started/from-scratch.mdx, docs/welcome/installation.mdx
  Installation
  Environment Setup
  Core Framework Architecture
    · System Mapping: Natural Language to Code Entities
  Creating Tools
    · 1. Function Tool Decorator (Recommended)
    · 2. BaseTool Class
  Defining Agents
  Building and Running an Agency
    · Implementation Data Flow
    · Example Setup
  Observability and Streaming
    · Usage Tracking
    · Streaming
  Next Steps

## · Creating Custom Agents  (L5167)
  源文件: docs/additional-features/fastapi-integration.mdx, docs/additional-features/guardrails/input-guardrails.mdx, docs/additional-features/guardrails/output-guardrails.mdx, docs/core-framework/agents/advanced-configuration.mdx, docs/core-framework/agents/built-in-tools.mdx, docs/core-framework/agents/overview.mdx, docs/core-framework/tools/mcp-integration.mdx, docs/core-framework/tools/mcp-oauth.mdx, docs/platform/marketplace/onboarding.mdx, docs/references/api.mdx, examples/README.md, examples/guardrails_input.py
  Understanding Agents in Agency Swarm
    · Agent Architecture and Code Mapping
  Methods for Creating Custom Agents
    · 1. The Directory-Based Structure (Recommended)
    · 2. Programmatic Instantiation
    · 3. CLI Template Generation
  Advanced Configuration
    · Model Settings and Reasoning
    · System Reminders
    · Conversation Starters and Cache
    · Guardrails
  Capability Detection

## · Creating Custom Tools  (L5338)
  源文件: docs/core-framework/tools/built-in-tools.mdx, docs/core-framework/tools/custom-tools/multimodal-outputs.mdx, docs/core-framework/tools/overview.mdx, examples/data/daily_revenue.png, examples/data/daily_revenue_report.pdf, examples/multimodal_outputs.py, src/agency_swarm/tools/base_tool.py, src/agency_swarm/tools/tool_factory_utils/base_tool_adapter.py, src/agency_swarm/tools/utils.py, src/agency_swarm/utils/dry_run.py, tests/integration/communication/test_send_message_extra_params.py, tests/integration/fastapi/test_fastapi_dry_run.py
  Overview
  The BaseTool Class
    · Implementation Structure
    · Key Components
  Accessing Context and State
  Multimodal Outputs
    · Supported Output Classes
    · Convenience Utilities
    · Example: Chart Generation
  Function Tool Decorator
  Advanced Configuration
    · Strict Mode and Schema Validation
    · Custom Tool Names
  Best Practices

## · Demos and Examples  (L5541)
  源文件: docs/additional-features/guardrails/input-guardrails.mdx, docs/additional-features/guardrails/output-guardrails.mdx, docs/core-framework/agents/built-in-tools.mdx, docs/platform/marketplace/onboarding.mdx, examples/README.md, examples/agency_context.py, examples/agent_file_storage.py, examples/connectors.py, examples/custom_persistence.py, examples/fastapi_integration/client.py, examples/fastapi_integration/server.py, examples/guardrails_input.py
  Examples Directory Structure
  Multi-Agent Workflow: Financial Research
    · Implementation Details
  Thread Persistence and Isolation
    · Key Functions
  Real-Time Streaming
    · Data Flow
  Guardrails: Input Validation
    · Implementation
  Third-Party Models (LiteLLM)
  Observability and Tracing
  FastAPI Integration

## · Infrastructure and Development  (L5722)
  源文件: .github/ISSUE_TEMPLATE/bug_report.md, .github/workflows/tests.yml, .pre-commit-config.yaml, AGENTS.md, CLAUDE.md, CONTRIBUTING.md, Makefile, docs/contributing/contributing.mdx, package.json, pyproject.toml, src/agency_swarm/hooks.py, tests/test_build_modules/test_dependency_constraints.py
  Development Standards
    · Development Workflow Mapping
  Build and Configuration
  Testing and CI/CD
    · CI/CD Pipeline Structure
  Contribution Guidelines

## · Build and Configuration  (L5862)
  源文件: .github/workflows/publish.yml, hatch_build.py, pyproject.toml, tests/test_build_modules/test_dependency_constraints.py, tests/test_build_modules/test_hatch_build.py, uv.lock
  Build System Architecture
    · Key Build Components
    · Data Flow: Build Initialization
  Custom Build Hook (`hatch_build.py`)
  Dependency Management
    · Core Dependencies
    · Optional Extras
  Package Distribution Structure
    · Artifact Mapping
  Version Pinning Constraints

## · Testing and CI  (L5990)
  源文件: .github/ISSUE_TEMPLATE/bug_report.md, .github/workflows/tests.yml, AGENTS.md, CLAUDE.md, Makefile, pyproject.toml, tests/conftest.py, tests/integration/conftest.py, tests/test_build_modules/test_dependency_constraints.py, uv.lock
  1. Testing Infrastructure
    · 1.1 Directory Layout
    · 1.2 Test Execution Flow
  2. Testing Policies and Patterns
    · 2.1 The No-Mock Policy for Core Messaging
    · 2.2 Coverage and Constraints
    · 2.3 Pytest Markers
  3. CI/CD Pipeline
    · 3.1 Workflow Architecture
    · 3.2 Security and Secret Handling
  4. Mocking and Fixtures
    · 4.1 ThreadManager Mocking
    · 4.2 Dependency Constraint Testing

## · Glossary  (L6134)
  源文件: .cursor/rules/writing-docs.mdc, README.md, docs/additional-features/azure-openai.mdx, docs/additional-features/observability.mdx, docs/core-framework/tools/custom-tools/step-by-step-guide.mdx, docs/images/platform/openclaw-persistent-storage.png, docs/platform/integrations/openclaw-integration.mdx, docs/platform/marketplace/openclaw.mdx, docs/welcome/getting-started/from-scratch.mdx, src/agency_swarm/agency/core.py, src/agency_swarm/agent/conversation_starters_cache.py, src/agency_swarm/agent/conversation_starters_streaming.py
  Core Concepts
    · Agency
    · Agent
    · Communication Flow
  Technical Terminology
    · MasterContext
    · SendMessage & Handoff
    · Guardrail (Input/Output)
    · MCP (Model Context Protocol)
    · OpenClaw
  Diagrams
    · Execution Data Flow: Natural Language to Code Entities
    · Agent Initialization & Components
  Technical Abbreviations