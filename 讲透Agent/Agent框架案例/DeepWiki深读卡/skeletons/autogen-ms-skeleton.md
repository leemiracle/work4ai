# Skeleton: autogen-ms（37 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 8KB | 2 | ~1 | 14 |
| 2 | Package Architecture | L209 | 20KB | 9 | ~23 | 31 |
| 3 | Installation and Setup | L743 | 8KB | 2 | ~2 | 20 |
| 4 | Core Foundation | L959 | 9KB | 2 | ~0 | 21 |
| 5 | Agent Runtime System | L1109 | 31KB | 11 | ~13 | 24 |
| 6 | Model Client System | L1825 | 15KB | 3 | ~7 | 18 |
| 7 | Message Types and Tool Agents | L2059 | 12KB | 2 | ~3 | 20 |
| 8 | Memory Systems | L2232 | 12KB | 2 | ~4 | 22 |
| 9 | Component Configuration System | L2401 | 9KB | 2 | ~2 | 16 |
| 10 | AgentChat API | L2555 | 12KB | 3 | ~2 | 16 |
| 11 | AssistantAgent | L2723 | 14KB | 4 | ~4 | 15 |
| 12 | Code Execution Agents | L2996 | 13KB | 3 | ~8 | 16 |
| 13 | Specialized Agents | L3194 | 12KB | 3 | ~0 | 17 |
| 14 | Multi-Agent Teams | L3365 | 21KB | 7 | ~4 | 16 |
| 15 | Team Orchestration | L3814 | 14KB | 3 | ~1 | 16 |
| 16 | Termination Conditions | L4045 | 15KB | 6 | ~6 | 15 |
| 17 | GraphFlow | L4337 | 10KB | 3 | ~6 | 9 |
| 18 | MagenticOne System | L4551 | 14KB | 4 | ~2 | 17 |
| 19 | Model Integrations | L4801 | 17KB | 3 | ~10 | 17 |
| 20 | OpenAI and Azure OpenAI | L5062 | 24KB | 4 | ~15 | 17 |
| 21 | Other Model Providers | L5494 | 11KB | 2 | ~0 | 18 |
| 22 | Tools and Extensions | L5672 | 13KB | 3 | ~2 | 17 |
| 23 | Code Execution | L5945 | 30KB | 11 | ~2 | 16 |
| 24 | MCP Integration | L6635 | 29KB | 7 | ~9 | 21 |
| 25 | Web and File Interaction | L7221 | 13KB | 3 | ~5 | 17 |
| 26 | Azure AI Agent and Additional Integrations | L7431 | 9KB | 2 | ~0 | 20 |
| 27 | AutoGen Studio | L7560 | 9KB | 2 | ~3 | 18 |
| 28 | Studio Backend | L7715 | 14KB | 2 | ~2 | 22 |
| 29 | Studio Frontend | L7925 | 15KB | 2 | ~2 | 20 |
| 30 | .NET Framework | L8135 | 8KB | 2 | ~2 | 22 |
| 31 | .NET Agent System | L8271 | 20KB | 2 | ~2 | 24 |
| 32 | .NET SDK Distribution | L8530 | 11KB | 3 | ~2 | 33 |
| 33 | Development Environment | L8754 | 21KB | 4 | ~12 | 16 |
| 34 | Python Workspace | L9380 | 12KB | 2 | ~11 | 23 |
| 35 | Development Containers | L9673 | 9KB | 4 | ~3 | 4 |
| 36 | CI/CD Workflows | L9924 | 11KB | 3 | ~2 | 23 |
| 37 | Glossary | L10166 | 16KB | 2 | ~2 | 24 |


## · Overview  (L6)
  源文件: .github/ISSUE_TEMPLATE/1-bug_report.yml, .github/workflows/docs.yml, CONTRIBUTING.md, LICENSE, README.md, SECURITY.md, TRANSPARENCY_FAQS.md, docs/switcher.json, python/README.md, python/packages/autogen-agentchat/pyproject.toml, python/packages/autogen-core/pyproject.toml, python/packages/autogen-ext/pyproject.toml
  Repository Structure
    · Repository Component Map
  Three-Layer Architecture
    · From Logic to Code Entities
  Core Packages
    · autogen-core (v0.7.5)
    · autogen-agentchat (v0.7.5)
    · autogen-ext (v0.7.5)
  Developer Tools
    · AutoGen Studio
    · agbench
    · Magentic-One CLI
  Cross-Language Support
    · Python SDK
    · .NET SDK
  Version Management
  Installation Quick Reference

## · Package Architecture  (L209)
  源文件: .github/ISSUE_TEMPLATE/1-bug_report.yml, .github/workflows/checks.yml, .github/workflows/codeql.yml, .github/workflows/docs.yml, .github/workflows/dotnet-build.yml, .github/workflows/integration.yml, .github/workflows/single-python-package.yml, README.md, docs/switcher.json, python/.gitignore, python/docs/src/conf.py, python/packages/agbench/pyproject.toml
  Layered Architecture
  Core Package: autogen-core
    · Package Metadata
    · Core Dependencies
  AgentChat Package: autogen-agentchat
    · Package Metadata
    · Dependencies
  Extensions Package: autogen-ext
    · Package Metadata
    · Extension Categories
    · Installation Patterns
    · Extension Implementations Table
  Developer Tools
    · AutoGen Studio
    · AGBench
    · Magentic-One CLI
  Compatibility Layer: pyautogen
    · Package Metadata
  .NET SDK
    · NuGet Package Table
  Workspace Structure
    · Workspace Configuration
    · Workspace Members
    · Shared Development Dependencies
  Version Synchronization

## · Installation and Setup  (L743)
  源文件: .github/ISSUE_TEMPLATE/1-bug_report.yml, .github/workflows/docs.yml, CONTRIBUTING.md, README.md, docs/switcher.json, python/README.md, python/packages/agbench/pyproject.toml, python/packages/autogen-agentchat/pyproject.toml, python/packages/autogen-core/pyproject.toml, python/packages/autogen-ext/pyproject.toml, python/packages/autogen-studio/pyproject.toml, python/templates/new-package/cookiecutter.json
  Installation
    · Pip Installation
    · UV Installation (Recommended for Developers)
    · Extension Extras
  Environment Configuration
  Quickstart Examples
    · Hello World (AssistantAgent)
    · Tool-Augmented Agent (MCP)
  Creating New Packages
    · Package Initialization Flow
  Package Architecture and Data Flow
  AutoGen Studio Setup

## · Core Foundation  (L959)
  源文件: python/docs/src/user-guide/autogenstudio-user-guide/installation.md, python/packages/autogen-core/src/autogen_core/_agent.py, python/packages/autogen-core/src/autogen_core/_agent_instantiation.py, python/packages/autogen-core/src/autogen_core/_agent_runtime.py, python/packages/autogen-core/src/autogen_core/_base_agent.py, python/packages/autogen-core/src/autogen_core/_component_config.py, python/packages/autogen-core/src/autogen_core/_runtime_impl_helpers.py, python/packages/autogen-core/src/autogen_core/_single_threaded_agent_runtime.py, python/packages/autogen-core/src/autogen_core/_telemetry/_propagation.py, python/packages/autogen-core/src/autogen_core/_telemetry/_tracing.py, python/packages/autogen-core/tests/test_base_agent.py, python/packages/autogen-core/tests/test_component_config.py
  Agent Runtime System
  Model Client System
  Message Types and Tool Agents
  Memory Systems
  Component Configuration System

## · Agent Runtime System  (L1109)
  源文件: docs/design/01 - Programming Model.md, docs/design/02 - Topics.md, docs/design/03 - Agent Worker Protocol.md, docs/design/04 - Agent and Topic ID Specs.md, docs/design/05 - Services.md, dotnet/samples/dev-team/DevTeam.ServiceDefaults/Extensions.cs, protos/agent_worker.proto, protos/cloudevent.proto, python/docs/src/user-guide/agentchat-user-guide/tracing.ipynb, python/docs/src/user-guide/core-user-guide/framework/telemetry.md, python/fixup_generated_files.py, python/packages/autogen-core/src/autogen_core/_agent.py
  Runtime Protocol Interface
  Message Routing and Subscriptions
  Message Envelope System
  SingleThreadedAgentRuntime Implementation
    · Key Components
    · Message Processing Flow
  GrpcWorkerAgentRuntime Implementation
    · GRPC Communication Protocol
    · Connection Management
  Lifecycle Management
    · Runtime States
    · Agent Instantiation Context
  Telemetry and Tracing
    · Trace Propagation
    · Observability Features

## · Model Client System  (L1825)
  源文件: python/packages/autogen-agentchat/tests/test_declarative_components.py, python/packages/autogen-core/src/autogen_core/_constants.py, python/packages/autogen-core/src/autogen_core/_function_utils.py, python/packages/autogen-core/src/autogen_core/_routed_agent.py, python/packages/autogen-core/src/autogen_core/logging.py, python/packages/autogen-core/src/autogen_core/model_context/__init__.py, python/packages/autogen-core/src/autogen_core/model_context/_buffered_chat_completion_context.py, python/packages/autogen-core/src/autogen_core/model_context/_chat_completion_context.py, python/packages/autogen-core/src/autogen_core/model_context/_head_and_tail_chat_completion_context.py, python/packages/autogen-core/src/autogen_core/model_context/_token_limited_chat_completion_context.py, python/packages/autogen-core/src/autogen_core/model_context/_unbounded_chat_completion_context.py, python/packages/autogen-core/src/autogen_core/models/_model_client.py
  Core Architecture
    · Core Interface Methods
  Model Information and Capabilities
    · ModelInfo and ModelFamily
  Model Context Management
  Message Transformation Pipeline
    · Modular Transformer Pipeline
  Tools and Schema System
    · Tool Abstractions
    · Schema Generation
    · Tool Agent and Execution

## · Message Types and Tool Agents  (L2059)
  源文件: python/docs/src/user-guide/agentchat-user-guide/tutorial/agents.ipynb, python/packages/autogen-agentchat/src/autogen_agentchat/tools/_agent.py, python/packages/autogen-agentchat/src/autogen_agentchat/tools/_task_runner_tool.py, python/packages/autogen-agentchat/src/autogen_agentchat/tools/_team.py, python/packages/autogen-agentchat/tests/test_task_runner_tool.py, python/packages/autogen-core/src/autogen_core/_constants.py, python/packages/autogen-core/src/autogen_core/_function_utils.py, python/packages/autogen-core/src/autogen_core/_routed_agent.py, python/packages/autogen-core/src/autogen_core/_serialization.py, python/packages/autogen-core/src/autogen_core/logging.py, python/packages/autogen-core/src/autogen_core/models/_types.py, python/packages/autogen-core/src/autogen_core/tools/__init__.py
  LLM Message Types
    · Message Type Hierarchy
    · Core Message Types
    · AssistantMessage Thought Field
    · Function Execution Results
  Workbench and Tool Management
    · StaticWorkbench
    · Tool Abstractions
  Hierarchical Tool Orchestration
    · AgentTool and TeamTool
    · TaskRunnerTool Logic
  Tool Agent Caller Loop
    · Execution Loop Diagram
    · Key Logic in Caller Loop

## · Memory Systems  (L2232)
  源文件: .github/workflows/pytest-mem0.yml, .github/workflows/pytest-redis-memory.yml, .gitignore, docs/dotnet/docfx.json, python/docs/src/user-guide/agentchat-user-guide/memory.ipynb, python/docs/src/user-guide/autogenstudio-user-guide/installation.md, python/packages/autogen-core/src/autogen_core/_component_config.py, python/packages/autogen-core/src/autogen_core/_runtime_impl_helpers.py, python/packages/autogen-core/src/autogen_core/memory/_base_memory.py, python/packages/autogen-core/src/autogen_core/memory/_list_memory.py, python/packages/autogen-core/tests/test_component_config.py, python/packages/autogen-core/tests/test_memory.py
  Memory Protocol and Data Types
    · Core Entities
    · Key Protocol Functions
  Available Implementations
    · ListMemory (In-Core)
    · RedisMemory (Semantic + Sequential)
    · ChromaDB Memory
    · Mem0 Memory
    · TextCanvasMemory (Experimental)
  Memory Data Flow
    · Agent-Memory Interaction Flow
  Configuration and Serialization
    · Memory Configuration Mapping
    · Comparison of Memory Implementations

## · Component Configuration System  (L2401)
  源文件: python/docs/src/user-guide/autogenstudio-user-guide/installation.md, python/packages/autogen-agentchat/tests/test_messages.py, python/packages/autogen-agentchat/tests/test_streaming_message_id_correlation.py, python/packages/autogen-core/src/autogen_core/_component_config.py, python/packages/autogen-core/src/autogen_core/_runtime_impl_helpers.py, python/packages/autogen-core/src/autogen_core/_serialization.py, python/packages/autogen-core/src/autogen_core/utils/__init__.py, python/packages/autogen-core/src/autogen_core/utils/_load_json.py, python/packages/autogen-core/tests/test_component_config.py, python/packages/autogen-core/tests/test_json_extraction.py, python/packages/autogen-core/tests/test_serialization.py, python/packages/autogen-ext/src/autogen_ext/agents/video_surfer/tools.py
  Core Architecture
    · ComponentModel
    · Component Data Flow
  Implementation Pattern
    · ComponentBase and Component Protocol
    · Example Implementation
  Provider Security and Trust
  Serialization System
    · Message Serializers
  Component Validation and Testing

## · AgentChat API  (L2555)
  源文件: python/docs/src/user-guide/agentchat-user-guide/magentic-one.md, python/packages/autogen-agentchat/src/autogen_agentchat/agents/__init__.py, python/packages/autogen-agentchat/src/autogen_agentchat/agents/_assistant_agent.py, python/packages/autogen-agentchat/src/autogen_agentchat/agents/_base_chat_agent.py, python/packages/autogen-agentchat/src/autogen_agentchat/agents/_code_executor_agent.py, python/packages/autogen-agentchat/src/autogen_agentchat/base/_chat_agent.py, python/packages/autogen-agentchat/src/autogen_agentchat/base/_task.py, python/packages/autogen-agentchat/src/autogen_agentchat/base/_team.py, python/packages/autogen-agentchat/src/autogen_agentchat/messages.py, python/packages/autogen-agentchat/src/autogen_agentchat/teams/__init__.py, python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_base_group_chat.py, python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_base_group_chat_manager.py
  Core API Components
    · Agent Hierarchy
    · Message Type System
  Agent Lifecycle and Execution
    · Agent State Management
    · Response Generation Flow
  Multi-Agent Orchestration
  Integration with Core Systems
  Specialized Agents

## · AssistantAgent  (L2723)
  源文件: python/packages/autogen-agentchat/src/autogen_agentchat/agents/_assistant_agent.py, python/packages/autogen-agentchat/src/autogen_agentchat/agents/_base_chat_agent.py, python/packages/autogen-agentchat/src/autogen_agentchat/agents/_user_proxy_agent.py, python/packages/autogen-agentchat/src/autogen_agentchat/base/_chat_agent.py, python/packages/autogen-agentchat/src/autogen_agentchat/base/_task.py, python/packages/autogen-agentchat/src/autogen_agentchat/base/_team.py, python/packages/autogen-agentchat/src/autogen_agentchat/messages.py, python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_base_group_chat.py, python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_base_group_chat_manager.py, python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_chat_agent_container.py, python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_events.py, python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_magentic_one/_magentic_one_group_chat.py
  Architecture Overview
    · Class Hierarchy
    · Core Components Integration
  Message Processing Flow
    · Core Message Flow
    · Tool Execution Process
  Core Capabilities
    · Tool Integration
    · Handoff Mechanism
    · Memory Integration
    · Structured Output
    · Streaming Support
  Configuration and State
    · AssistantAgentConfig
    · State Save/Load
    · Serialization

## · Code Execution Agents  (L2996)
  源文件: python/docs/src/user-guide/agentchat-user-guide/magentic-one.md, python/packages/autogen-agentchat/src/autogen_agentchat/agents/__init__.py, python/packages/autogen-agentchat/src/autogen_agentchat/agents/_code_executor_agent.py, python/packages/autogen-agentchat/src/autogen_agentchat/teams/__init__.py, python/packages/autogen-agentchat/tests/test_code_executor_agent.py, python/packages/autogen-ext/src/autogen_ext/agents/magentic_one/_magentic_one_coder_agent.py, python/packages/autogen-ext/src/autogen_ext/code_executors/__init__.py, python/packages/autogen-ext/src/autogen_ext/code_executors/azure/_azure_container_code_executor.py, python/packages/autogen-ext/src/autogen_ext/code_executors/docker/_docker_code_executor.py, python/packages/autogen-ext/src/autogen_ext/code_executors/docker_jupyter/_docker_jupyter.py, python/packages/autogen-ext/src/autogen_ext/code_executors/jupyter/_jupyter_code_executor.py, python/packages/autogen-ext/src/autogen_ext/code_executors/local/__init__.py
  Overview
  CodeExecutorAgent Architecture
    · Code Entity Mapping: Agent to Backend
    · Core Components
  Code Approval System
    · Approval Structures
  Event System
  Code Execution Backends
    · Implementation Matrix
    · The Factory Method
  MagenticOne Integration
  Configuration and Serialization
    · CodeExecutorAgentConfig

## · Specialized Agents  (L3194)
  源文件: python/packages/autogen-agentchat/src/autogen_agentchat/agents/_message_filter_agent.py, python/packages/autogen-agentchat/src/autogen_agentchat/agents/_society_of_mind_agent.py, python/packages/autogen-agentchat/src/autogen_agentchat/agents/_user_proxy_agent.py, python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_graph/__init__.py, python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_graph/_digraph_group_chat.py, python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_graph/_graph_builder.py, python/packages/autogen-agentchat/src/autogen_agentchat/ui/_console.py, python/packages/autogen-agentchat/tests/test_group_chat_endpoint.py, python/packages/autogen-agentchat/tests/test_group_chat_graph.py, python/packages/autogen-agentchat/tests/test_society_of_mind_agent.py, python/packages/autogen-agentchat/tests/test_userproxy_agent.py, python/packages/autogen-agentchat/tests/utils.py
  Overview
  OpenAI-Specific Agents
    · OpenAIAssistantAgent
    · OpenAIAgent
  SocietyOfMindAgent
  User Interaction and UI
    · UserProxyAgent
    · Console UI
  Message Filtering
  Graph-Based Orchestration

## · Multi-Agent Teams  (L3365)
  源文件: python/packages/autogen-agentchat/src/autogen_agentchat/__init__.py, python/packages/autogen-agentchat/src/autogen_agentchat/agents/_assistant_agent.py, python/packages/autogen-agentchat/src/autogen_agentchat/agents/_base_chat_agent.py, python/packages/autogen-agentchat/src/autogen_agentchat/base/_chat_agent.py, python/packages/autogen-agentchat/src/autogen_agentchat/base/_task.py, python/packages/autogen-agentchat/src/autogen_agentchat/base/_team.py, python/packages/autogen-agentchat/src/autogen_agentchat/base/_termination.py, python/packages/autogen-agentchat/src/autogen_agentchat/conditions/__init__.py, python/packages/autogen-agentchat/src/autogen_agentchat/conditions/_terminations.py, python/packages/autogen-agentchat/src/autogen_agentchat/messages.py, python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_base_group_chat.py, python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_base_group_chat_manager.py
  Team Architecture Overview
    · Core Team Architecture
    · Team Orchestration Components
  Group Chat Communication Flow
    · Message Flow Architecture
    · Team Initialization Process
  Orchestration Patterns
    · RoundRobinGroupChat
    · SelectorGroupChat
    · Swarm
    · MagenticOneGroupChat
  Termination Conditions
  GraphFlow Orchestration
  Team State Management
    · State Serialization
  Message Types and Events
    · Core Message Types
  Team Integration Patterns

## · Team Orchestration  (L3814)
  源文件: python/docs/src/user-guide/agentchat-user-guide/magentic-one.md, python/packages/autogen-agentchat/src/autogen_agentchat/agents/__init__.py, python/packages/autogen-agentchat/src/autogen_agentchat/agents/_assistant_agent.py, python/packages/autogen-agentchat/src/autogen_agentchat/agents/_base_chat_agent.py, python/packages/autogen-agentchat/src/autogen_agentchat/agents/_code_executor_agent.py, python/packages/autogen-agentchat/src/autogen_agentchat/base/_chat_agent.py, python/packages/autogen-agentchat/src/autogen_agentchat/base/_task.py, python/packages/autogen-agentchat/src/autogen_agentchat/base/_team.py, python/packages/autogen-agentchat/src/autogen_agentchat/messages.py, python/packages/autogen-agentchat/src/autogen_agentchat/teams/__init__.py, python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_base_group_chat.py, python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_base_group_chat_manager.py
  Architecture Overview
    · Core Class Hierarchy
    · Hub-and-Spoke Topic Model
  Orchestration Patterns
    · Round Robin Pattern
    · Selector Pattern
    · Swarm Pattern
    · MagenticOne Pattern
  Runtime Integration
    · State Save/Load

## · Termination Conditions  (L4045)
  源文件: python/packages/autogen-agentchat/src/autogen_agentchat/__init__.py, python/packages/autogen-agentchat/src/autogen_agentchat/agents/_assistant_agent.py, python/packages/autogen-agentchat/src/autogen_agentchat/agents/_base_chat_agent.py, python/packages/autogen-agentchat/src/autogen_agentchat/base/_chat_agent.py, python/packages/autogen-agentchat/src/autogen_agentchat/base/_task.py, python/packages/autogen-agentchat/src/autogen_agentchat/base/_team.py, python/packages/autogen-agentchat/src/autogen_agentchat/base/_termination.py, python/packages/autogen-agentchat/src/autogen_agentchat/conditions/__init__.py, python/packages/autogen-agentchat/src/autogen_agentchat/conditions/_terminations.py, python/packages/autogen-agentchat/src/autogen_agentchat/messages.py, python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_base_group_chat.py, python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_base_group_chat_manager.py
  Architecture Overview
    · Termination Protocol and Base Class
  Built-in Termination Conditions
    · Condition Class Hierarchy
    · Implementation Details
  Combining Conditions
  Custom Termination Logic
  State Management and Reset
  Configuration and Serialization

## · GraphFlow  (L4337)
  源文件: python/packages/autogen-agentchat/src/autogen_agentchat/agents/_message_filter_agent.py, python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_graph/__init__.py, python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_graph/_digraph_group_chat.py, python/packages/autogen-agentchat/src/autogen_agentchat/teams/_group_chat/_graph/_graph_builder.py, python/packages/autogen-agentchat/tests/test_group_chat_endpoint.py, python/packages/autogen-agentchat/tests/test_group_chat_graph.py, python/packages/autogen-agentchat/tests/utils.py, python/packages/autogen-ext/tests/test_filesurfer_agent.py, python/packages/autogen-ext/tests/test_websurfer_agent.py
  Purpose and Architecture
  GraphFlow Execution Model
  Core Components
    · GraphFlow Class
    · DiGraph Structure
    · DiGraphNode and DiGraphEdge
  Execution Flow Management
    · GraphFlowManager State Machine
    · Activation Logic
  DiGraphBuilder API
  Cycle Management
    · Cycle Detection and Validation
    · Activation Groups
  Integration with Message Filtering
    · MessageFilterAgent
  State Management and Persistence
    · State Serialization

## · MagenticOne System  (L4551)
  源文件: python/docs/src/user-guide/agentchat-user-guide/magentic-one.md, python/packages/autogen-agentchat/src/autogen_agentchat/agents/__init__.py, python/packages/autogen-agentchat/src/autogen_agentchat/agents/_code_executor_agent.py, python/packages/autogen-agentchat/src/autogen_agentchat/agents/_user_proxy_agent.py, python/packages/autogen-agentchat/src/autogen_agentchat/teams/__init__.py, python/packages/autogen-agentchat/src/autogen_agentchat/ui/_console.py, python/packages/autogen-agentchat/tests/test_code_executor_agent.py, python/packages/autogen-agentchat/tests/test_magentic_one_group_chat.py, python/packages/autogen-agentchat/tests/test_userproxy_agent.py, python/packages/autogen-ext/src/autogen_ext/agents/file_surfer/__init__.py, python/packages/autogen-ext/src/autogen_ext/agents/file_surfer/_file_surfer.py, python/packages/autogen-ext/src/autogen_ext/agents/file_surfer/_markdown_file_browser.py
  System Architecture
  MagenticOneOrchestrator
  Specialized Agents
    · Agent Roles and Capabilities
    · Agent Creation in MagenticOne Wrapper
  MagenticOne CLI (`m1`)
    · Entrypoint and Configuration
  Code Execution and Approval
    · Stall Detection and Retry
    · Human-in-the-loop (HIL) Approval
  Implementation Details
    · Web Browsing (`MultimodalWebSurfer`)
    · File Browsing (`FileSurfer`)

## · Model Integrations  (L4801)
  源文件: python/packages/autogen-core/src/autogen_core/models/_model_client.py, python/packages/autogen-core/tests/test_tool_agent.py, python/packages/autogen-ext/src/autogen_ext/auth/azure/__init__.py, python/packages/autogen-ext/src/autogen_ext/experimental/task_centric_memory/utils/chat_completion_client_recorder.py, python/packages/autogen-ext/src/autogen_ext/models/anthropic/__init__.py, python/packages/autogen-ext/src/autogen_ext/models/anthropic/_anthropic_client.py, python/packages/autogen-ext/src/autogen_ext/models/anthropic/_model_info.py, python/packages/autogen-ext/src/autogen_ext/models/anthropic/config/__init__.py, python/packages/autogen-ext/src/autogen_ext/models/azure/_azure_ai_client.py, python/packages/autogen-ext/src/autogen_ext/models/llama_cpp/_llama_cpp_completion_client.py, python/packages/autogen-ext/src/autogen_ext/models/openai/__init__.py, python/packages/autogen-ext/src/autogen_ext/models/openai/_message_transform.py
  Architecture Overview
  Core Interface and Message Types
  Model Provider Implementations
  Message Transformation Pipeline
  Model Information and Capabilities
  Common Integration Patterns
    · Tool/Function Calling
    · Token Counting
    · Streaming Support
    · JSON and Structured Output

## · OpenAI and Azure OpenAI  (L5062)
  源文件: python/packages/autogen-core/src/autogen_core/_cache_store.py, python/packages/autogen-core/src/autogen_core/models/_model_client.py, python/packages/autogen-core/tests/test_tool_agent.py, python/packages/autogen-ext/src/autogen_ext/auth/azure/__init__.py, python/packages/autogen-ext/src/autogen_ext/cache_store/diskcache.py, python/packages/autogen-ext/src/autogen_ext/cache_store/redis.py, python/packages/autogen-ext/src/autogen_ext/experimental/task_centric_memory/utils/chat_completion_client_recorder.py, python/packages/autogen-ext/src/autogen_ext/models/anthropic/_model_info.py, python/packages/autogen-ext/src/autogen_ext/models/cache/_chat_completion_cache.py, python/packages/autogen-ext/src/autogen_ext/models/llama_cpp/_llama_cpp_completion_client.py, python/packages/autogen-ext/src/autogen_ext/models/openai/__init__.py, python/packages/autogen-ext/src/autogen_ext/models/openai/_message_transform.py
  Architecture Overview
    · Core Client Architecture
  Client Implementations
    · BaseOpenAIChatCompletionClient
    · OpenAIChatCompletionClient
    · AzureOpenAIChatCompletionClient
  Message Transformation System
    · Transformation Pipeline
    · Message Type Handling
  Model Information and Capabilities
    · Model Registry
    · Model Capabilities Matrix
  Tool Calling and Function Execution
    · Tool Conversion
  Advanced Features
    · Streaming Support
    · Vision Support
    · Structured Output
    · Reasoning Models (o1, o3, R1)
    · Caching

## · Other Model Providers  (L5494)
  源文件: dotnet/test/AutoGen.AzureAIInference.Tests/ChatCompletionClientAgentTests.cs, dotnet/test/AutoGen.AzureAIInference.Tests/ChatRequestMessageTests.cs, dotnet/test/AutoGen.Tests/Orchestrator/RolePlayOrchestratorTests.cs, python/docs/src/user-guide/agentchat-user-guide/tutorial/models.ipynb, python/packages/autogen-ext/src/autogen_ext/models/__init__.py, python/packages/autogen-ext/src/autogen_ext/models/anthropic/__init__.py, python/packages/autogen-ext/src/autogen_ext/models/anthropic/_anthropic_client.py, python/packages/autogen-ext/src/autogen_ext/models/anthropic/config/__init__.py, python/packages/autogen-ext/src/autogen_ext/models/azure/__init__.py, python/packages/autogen-ext/src/autogen_ext/models/azure/_azure_ai_client.py, python/packages/autogen-ext/src/autogen_ext/models/azure/config/__init__.py, python/packages/autogen-ext/src/autogen_ext/models/ollama/__init__.py
  Provider Architecture Overview
  Anthropic Integration
    · Thinking Mode and Configuration
    · Message Transformation and Normalization
  Azure AI Foundry and GitHub Models
    · R1 Thought Extraction
    · Tool Conversion
  Ollama (Local Inference)
    · Configuration and Options
    · Model Capabilities
  Semantic Kernel Adapter
    · Tool and Function Bridging
  Testing and Development Clients
    · ReplayChatCompletionClient
    · LlamaCpp

## · Tools and Extensions  (L5672)
  源文件: python/packages/autogen-ext/src/autogen_ext/code_executors/azure/_azure_container_code_executor.py, python/packages/autogen-ext/src/autogen_ext/code_executors/docker/_docker_code_executor.py, python/packages/autogen-ext/src/autogen_ext/code_executors/jupyter/_jupyter_code_executor.py, python/packages/autogen-ext/src/autogen_ext/code_executors/local/__init__.py, python/packages/autogen-ext/src/autogen_ext/tools/mcp/__init__.py, python/packages/autogen-ext/src/autogen_ext/tools/mcp/_actor.py, python/packages/autogen-ext/src/autogen_ext/tools/mcp/_base.py, python/packages/autogen-ext/src/autogen_ext/tools/mcp/_config.py, python/packages/autogen-ext/src/autogen_ext/tools/mcp/_session.py, python/packages/autogen-ext/src/autogen_ext/tools/mcp/_streamable_http.py, python/packages/autogen-ext/src/autogen_ext/tools/mcp/_workbench.py, python/packages/autogen-ext/tests/code_executors/test_aca_dynamic_sessions.py
  Overview
    · Tool and Executor Architecture
    · Code Executor Configuration and Lifecycle
  PythonCodeExecutionTool
    · Integration Example
  User-Defined Functions
    · Function Registration Flow
    · Function Requirements
  MCP Integration
    · MCP Component Architecture
  Detailed Subsections

## · Code Execution  (L5945)
  源文件: python/docs/src/user-guide/agentchat-user-guide/magentic-one.md, python/packages/autogen-agentchat/src/autogen_agentchat/agents/__init__.py, python/packages/autogen-agentchat/src/autogen_agentchat/agents/_code_executor_agent.py, python/packages/autogen-agentchat/src/autogen_agentchat/teams/__init__.py, python/packages/autogen-agentchat/tests/test_code_executor_agent.py, python/packages/autogen-ext/src/autogen_ext/agents/magentic_one/_magentic_one_coder_agent.py, python/packages/autogen-ext/src/autogen_ext/code_executors/__init__.py, python/packages/autogen-ext/src/autogen_ext/code_executors/azure/_azure_container_code_executor.py, python/packages/autogen-ext/src/autogen_ext/code_executors/docker/_docker_code_executor.py, python/packages/autogen-ext/src/autogen_ext/code_executors/docker_jupyter/_docker_jupyter.py, python/packages/autogen-ext/src/autogen_ext/code_executors/jupyter/_jupyter_code_executor.py, python/packages/autogen-ext/src/autogen_ext/code_executors/local/__init__.py
  Executor Overview
  Core Interface
    · CodeExecutor Base Class
    · Data Structures
    · Cancellation and Timeout
  Executor Implementations
    · LocalCommandLineCodeExecutor
    · DockerCommandLineCodeExecutor
    · ACADynamicSessionsCodeExecutor
    · JupyterCodeExecutor
    · DockerJupyterCodeExecutor
  Integration Patterns
    · CodeExecutorAgent Integration
    · MagenticOne Integration Pattern
    · Tool Wrapping Pattern

## · MCP Integration  (L6635)
  源文件: .github/workflows/pytest-redis-memory.yml, .gitignore, docs/dotnet/docfx.json, python/docs/src/user-guide/agentchat-user-guide/memory.ipynb, python/packages/autogen-core/src/autogen_core/utils/_json_to_pydantic.py, python/packages/autogen-core/tests/test_json_to_pydantic.py, python/packages/autogen-ext/examples/mcp_example_server.py, python/packages/autogen-ext/examples/mcp_session_host_example.py, python/packages/autogen-ext/src/autogen_ext/experimental/task_centric_memory/__init__.py, python/packages/autogen-ext/src/autogen_ext/experimental/task_centric_memory/utils/__init__.py, python/packages/autogen-ext/src/autogen_ext/memory/redis/__init__.py, python/packages/autogen-ext/src/autogen_ext/memory/redis/_redis_memory.py
  Purpose and Scope
  Architecture Overview
  Connection Types and Server Parameters
  McpWorkbench Component
    · Key Methods
    · Tool Overrides
    · Context Manager Support
  McpSessionActor Component
    · Command Queue Pattern
    · Exception Handling
    · Callback Registration
  MCP Tool Adapters
    · McpToolAdapter Base Class
    · Content Normalization
    · Factory Pattern
  Bidirectional Capabilities: Host Components
    · Sampling: ChatCompletionClientSampler
    · Elicitation: StdioElicitor
    · Roots: StaticRootsProvider
    · McpSessionHost Configuration
  Complete Usage Example
    · Basic Setup
  Component Serialization
  Supported MCP Capabilities

## · Web and File Interaction  (L7221)
  源文件: python/packages/autogen-agentchat/src/autogen_agentchat/base/_handoff.py, python/packages/autogen-agentchat/tests/test_magentic_one_group_chat.py, python/packages/autogen-ext/src/autogen_ext/agents/file_surfer/__init__.py, python/packages/autogen-ext/src/autogen_ext/agents/file_surfer/_file_surfer.py, python/packages/autogen-ext/src/autogen_ext/agents/file_surfer/_markdown_file_browser.py, python/packages/autogen-ext/src/autogen_ext/agents/file_surfer/_tool_definitions.py, python/packages/autogen-ext/src/autogen_ext/agents/video_surfer/__init__.py, python/packages/autogen-ext/src/autogen_ext/agents/video_surfer/_video_surfer.py, python/packages/autogen-ext/src/autogen_ext/agents/web_surfer/__init__.py, python/packages/autogen-ext/src/autogen_ext/agents/web_surfer/_events.py, python/packages/autogen-ext/src/autogen_ext/agents/web_surfer/_multimodal_web_surfer.py, python/packages/autogen-ext/src/autogen_ext/agents/web_surfer/_prompts.py
  Overview
  Web Interaction Architecture
    · MultimodalWebSurfer Agent
    · Web Interaction Tool Flow
    · Browser Control Components
  File and Video Interaction
    · FileSurfer Agent
    · VideoSurfer Agent
  Data Retrieval Tools
    · Azure AI Search Tool
    · GraphRAG and HTTP Tools
  Summary of Interaction Components

## · Azure AI Agent and Additional Integrations  (L7431)
  源文件: python/packages/agbench/.gitignore, python/packages/agbench/CONTRIBUTING.md, python/packages/agbench/README.md, python/packages/agbench/benchmarks/GAIA/Templates/ParallelAgents/expected_answer.txt, python/packages/agbench/benchmarks/GAIA/Templates/ParallelAgents/prompt.txt, python/packages/agbench/benchmarks/GAIA/Templates/ParallelAgents/requirements.txt, python/packages/agbench/benchmarks/GAIA/Templates/ParallelAgents/scenario.py, python/packages/agbench/benchmarks/HumanEval/Templates/AgentChat/reasoning_model_context.py, python/packages/agbench/benchmarks/HumanEval/Templates/AgentChat/scenario.py, python/packages/agbench/src/agbench/remove_missing_cmd.py, python/packages/agbench/src/agbench/run_cmd.py, python/packages/agbench/src/agbench/tabulate_cmd.py
  Azure AI Agent
    · Implementation and Architecture
    · Data Flow: Azure AI Agent Interaction
  Chat Completion Cache
    · Cache Infrastructure
    · Serialization Logic
  agbench Benchmarking Suite
    · Core Commands
    · Scenario Expansion
    · Benchmark Templates

## · AutoGen Studio  (L7560)
  源文件: python/packages/autogen-studio/autogenstudio/cli.py, python/packages/autogen-studio/autogenstudio/database/schema_manager.py, python/packages/autogen-studio/autogenstudio/datamodel/db.py, python/packages/autogen-studio/autogenstudio/datamodel/types.py, python/packages/autogen-studio/autogenstudio/gallery/builder.py, python/packages/autogen-studio/autogenstudio/gallery/tools/__init__.py, python/packages/autogen-studio/autogenstudio/teammanager/teammanager.py, python/packages/autogen-studio/autogenstudio/web/app.py, python/packages/autogen-studio/autogenstudio/web/initialization.py, python/packages/autogen-studio/autogenstudio/web/routes/runs.py, python/packages/autogen-studio/autogenstudio/web/serve.py, python/packages/autogen-studio/frontend/src/components/types/datamodel.ts
    · High-Level System Architecture
    · Core Functionality
    · Backend Overview
    · Frontend Overview
    · CLI and Deployment

## · Studio Backend  (L7715)
  源文件: .github/workflows/pytest-redis-memory.yml, .gitignore, docs/dotnet/docfx.json, python/docs/src/user-guide/agentchat-user-guide/memory.ipynb, python/packages/autogen-ext/src/autogen_ext/memory/redis/__init__.py, python/packages/autogen-ext/src/autogen_ext/memory/redis/_redis_memory.py, python/packages/autogen-ext/tests/memory/test_redis_memory.py, python/packages/autogen-studio/autogenstudio/cli.py, python/packages/autogen-studio/autogenstudio/database/db_manager.py, python/packages/autogen-studio/autogenstudio/database/schema_manager.py, python/packages/autogen-studio/autogenstudio/datamodel/db.py, python/packages/autogen-studio/autogenstudio/datamodel/types.py
  CLI Entrypoint and Initialization
    · CLI Entrypoint
    · App Initialization
  Data Flow: Web Request to Agent Execution
    · Natural Language to Code Entity Mapping
  Database Layer
    · DatabaseManager and SchemaManager
    · Cascade Deletion Logic
  Real-time Execution: WebSocketManager
    · Execution Loop
  Validation Service
    · Validation Workflow
  Component System and Gallery
    · Component Hierarchy

## · Studio Frontend  (L7925)
  源文件: .github/workflows/pytest-redis-memory.yml, .gitignore, docs/dotnet/docfx.json, python/docs/src/user-guide/agentchat-user-guide/memory.ipynb, python/packages/autogen-ext/src/autogen_ext/memory/redis/__init__.py, python/packages/autogen-ext/src/autogen_ext/memory/redis/_redis_memory.py, python/packages/autogen-ext/tests/memory/test_redis_memory.py, python/packages/autogen-studio/autogenstudio/validation/validation_service.py, python/packages/autogen-studio/autogenstudio/web/config.py, python/packages/autogen-studio/autogenstudio/web/routes/mcp.py, python/packages/autogen-studio/autogenstudio/web/routes/settingsroute.py, python/packages/autogen-studio/frontend/gatsby-config.ts
  Build and Project Setup
    · Build Pipeline
    · Key Dependencies
  Team Builder
    · Component Architecture and Data Flow
    · Data Flow: Natural Language to Code Entity
    · Component Editor Fields
    · Validation Logic
  Playground
    · Chat and Run View
    · Agent Flow Visualization
  Gallery and Store
  Settings and Environment
    · Model Configuration
    · Environment Variables
  Deployment Guides
  System Integration Diagram

## · .NET Framework  (L8135)
  源文件: dotnet/AutoGen.sln, dotnet/Directory.Build.props, dotnet/nuget/nuget-package.props, dotnet/samples/dev-team/DevTeam.Backend/Agents/Developer/Developer.cs, dotnet/samples/dev-team/DevTeam.Backend/Agents/DeveloperLead/DeveloperLead.cs, dotnet/samples/dev-team/DevTeam.Backend/Agents/ProductManager/ProductManager.cs, dotnet/samples/dev-team/DevTeam.Backend/DevTeam.Backend.csproj, dotnet/src/AutoGen.DotnetInteractive/InProccessDotnetInteractiveKernelBuilder.cs, dotnet/src/Microsoft.AutoGen/Agents/Microsoft.AutoGen.Agents.csproj, dotnet/src/Microsoft.AutoGen/Contracts/AgentProxy.cs, dotnet/src/Microsoft.AutoGen/Contracts/IAgent.cs, dotnet/src/Microsoft.AutoGen/Contracts/IAgentRuntime.cs
  Architecture Overview
    · .NET SDK Component Space
    · Package Hierarchy
  Core Framework Systems
    · Messaging and Runtime Flow
    · Key Components
  Integration Patterns

## · .NET Agent System  (L8271)
  源文件: dotnet/AutoGen.sln, dotnet/Directory.Build.props, dotnet/Directory.Packages.props, dotnet/nuget/nuget-package.props, dotnet/samples/dev-team/DevTeam.Backend/Agents/Developer/Developer.cs, dotnet/samples/dev-team/DevTeam.Backend/Agents/DeveloperLead/DeveloperLead.cs, dotnet/samples/dev-team/DevTeam.Backend/Agents/ProductManager/ProductManager.cs, dotnet/samples/dev-team/DevTeam.Backend/DevTeam.Backend.csproj, dotnet/src/AutoGen.Anthropic/Agent/AnthropicClientAgent.cs, dotnet/src/AutoGen.Anthropic/AnthropicClient.cs, dotnet/src/AutoGen.Anthropic/Converters/ContentBaseConverter.cs, dotnet/src/AutoGen.Anthropic/DTO/ChatCompletionRequest.cs
  Purpose and Scope
  Architecture Overview
    · Package Hierarchy and Core Entities
  Core Runtime System
    · IAgentRuntime and Implementations
    · BaseAgent and Messaging
    · AgentsApp
  Platform Integrations and Middleware
    · Supported Platforms
    · Middleware Pipeline
  Source Generator for Function Contracts
  AgentChat Layer
    · Group Chat and Routing
    · Terminations
  Development and Distribution

## · .NET SDK Distribution  (L8530)
  源文件: .azure/pipelines/build.yaml, .azure/pipelines/templates/build.yaml, .azure/pipelines/templates/vars.yaml, docs/dotnet/.gitignore, docs/dotnet/README.md, docs/dotnet/core/differences-from-python.md, docs/dotnet/core/index.md, docs/dotnet/core/protobuf-message-types.md, docs/dotnet/core/toc.yml, docs/dotnet/core/tutorial.md, docs/dotnet/images/favicon.ico, docs/dotnet/index.md
  Overview
  Distribution Architecture
  NuGet Package Distribution
    · Package Layers
    · Official Release Packages
    · Nightly Build Feeds
  Azure Pipeline Build and Publish
  Documentation Site (DocFX)
  Hello Sample Walkthroughs
    · In-Process Execution
    · Distributed Execution with .NET Aspire

## · Development Environment  (L8754)
  源文件: .devcontainer/Dockerfile, .devcontainer/devcontainer.json, .devcontainer/docker-compose.yml, .devcontainer/startup.sh, .github/workflows/checks.yml, .github/workflows/codeql.yml, .github/workflows/dotnet-build.yml, .github/workflows/integration.yml, .github/workflows/single-python-package.yml, python/.gitignore, python/docs/src/conf.py, python/packages/pyautogen/LICENSE-CODE
  Development Environment Overview
    · Repository Structure
    · Development Environment Architecture
  DevContainer Configuration
    · Container Features
    · Post-Creation Setup
    · VS Code Integration
  Python Development Tooling
    · Package Management with uv
    · Code Quality Tools
    · Task Automation with poe
    · Protobuf Generation
  CI/CD Pipeline
    · CI/CD Workflow Structure
    · checks.yml: Python Quality Gates
    · dotnet-build.yml: .NET Build Pipeline
    · Deployment Workflows
  Development Workflow
    · Setting Up the Environment
    · Running Code Quality Checks
    · Testing Changes
    · Building Packages
    · Generating Protobuf Bindings
    · .NET Development
  Troubleshooting
    · Common Issues

## · Python Workspace  (L9380)
  源文件: .github/workflows/checks.yml, .github/workflows/codeql.yml, .github/workflows/dotnet-build.yml, .github/workflows/integration.yml, .github/workflows/single-python-package.yml, CONTRIBUTING.md, python/.gitignore, python/README.md, python/docs/src/conf.py, python/packages/agbench/pyproject.toml, python/packages/pyautogen/LICENSE-CODE, python/packages/pyautogen/README.md
  Overview
  Monorepo Structure
    · Workspace Members
    · Workspace Dependency Resolution
  Package Management with uv
    · Installation and Synchronization
    · Dependency Groups
    · Dependency Overrides
  Task Automation with poethepoet
    · Common Tasks
    · Protobuf Generation
  Code Quality Tools
    · Ruff
    · Mypy
    · Pyright
  Testing with Pytest
    · CI Test Execution
  Cookiecutter Template
    · Template Structure
  Summary of Quality Gates

## · Development Containers  (L9673)
  源文件: .devcontainer/Dockerfile, .devcontainer/devcontainer.json, .devcontainer/docker-compose.yml, .devcontainer/startup.sh
  Container Architecture
    · Development Container Components
  Configuration Structure
    · Configuration Flow
  Features and Extensions
    · Installed Features
    · VS Code Extensions
  Setup Process
    · Startup Script Workflow
  Volume Mounting and Development Workflow
    · Volume Configuration
    · Container Lifecycle Management
  Environment Variables

## · CI/CD Workflows  (L9924)
  源文件: .azure/pipelines/build.yaml, .azure/pipelines/templates/build.yaml, .azure/pipelines/templates/vars.yaml, .github/workflows/checks.yml, .github/workflows/codeql.yml, .github/workflows/dotnet-build.yml, .github/workflows/dotnet-release.yml, .github/workflows/integration.yml, .github/workflows/single-python-package.yml, dotnet/PACKAGING.md, dotnet/nuget/README.md, dotnet/src/AutoGen.DotnetInteractive/AutoGen.DotnetInteractive.csproj
  Overview
    · CI/CD Workflow Architecture
  Python CI Pipeline (`checks.yml`)
    · Key Pipeline Components
    · Test Coverage Flow
  .NET SDK Pipeline (`dotnet-build.yml`)
    · Build and Validation Stages
    · Coverage Merging
  Deployment Workflows
    · Python Package Deployment
    · .NET Release Pipeline
  Documentation and Security
    · Documentation Pipeline
    · CodeQL Security Scanning

## · Glossary  (L10166)
  源文件: .github/ISSUE_TEMPLATE/1-bug_report.yml, .github/workflows/docs.yml, README.md, docs/switcher.json, dotnet/src/Microsoft.AutoGen/Contracts/AgentProxy.cs, dotnet/src/Microsoft.AutoGen/Contracts/IAgent.cs, dotnet/src/Microsoft.AutoGen/Contracts/IAgentRuntime.cs, dotnet/src/Microsoft.AutoGen/Contracts/ISaveState.cs, dotnet/src/Microsoft.AutoGen/Contracts/KVStringParseHelper.cs, dotnet/src/Microsoft.AutoGen/Core.Grpc/GrpcAgentRuntime.cs, dotnet/src/Microsoft.AutoGen/Core/AgentsApp.cs, dotnet/src/Microsoft.AutoGen/Core/BaseAgent.cs
  Core Concepts
    · Agent Runtime
    · ChatCompletionClient
    · Component
  AgentChat Vocabulary
    · AssistantAgent
    · Team
    · Termination Condition
  System Architecture Diagrams
    · From Natural Language Space to Code Entity Space: Agent Execution
    · Message Flow Architecture
  Specialized Terminology
  Developer Tools
    · agbench
    · AutoGen Studio