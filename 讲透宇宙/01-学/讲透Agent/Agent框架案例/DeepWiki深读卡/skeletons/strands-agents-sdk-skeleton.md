# Skeleton: strands-agents-sdk（58 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Introduction to Strands Agents SDK | L6 | 15KB | 3 | ~7 | 24 |
| 2 | Installation and Quick Start | L270 | 10KB | 3 | ~4 | 26 |
| 3 | Core Concepts and Architecture | L544 | 20KB | 3 | ~4 | 23 |
| 4 | Strands MCP Server | L940 | 16KB | 3 | ~0 | 11 |
| 5 | Agent System | L1302 | 9KB | 2 | ~2 | 21 |
| 6 | Agent Class and Initialization | L1483 | 12KB | 2 | ~5 | 25 |
| 7 | Event Loop and Execution Flow | L1707 | 15KB | 2 | ~5 | 20 |
| 8 | Streaming Responses | L1976 | 9KB | 2 | ~8 | 18 |
| 9 | Conversation Management | L2195 | 28KB | 3 | ~2 | 20 |
| 10 | Agent State and Session Management | L2657 | 12KB | 2 | ~1 | 22 |
| 11 | Error Handling and Recovery | L2835 | 12KB | 5 | ~3 | 24 |
| 12 | Model Providers | L3101 | 10KB | 2 | ~4 | 19 |
| 13 | Model Provider Architecture | L3280 | 11KB | 2 | ~2 | 21 |
| 14 | AWS Bedrock Models | L3487 | 10KB | 2 | ~5 | 19 |
| 15 | OpenAI Compatible Models | L3715 | 16KB | 3 | ~5 | 24 |
| 16 | LiteLLM Multi-Provider Support | L4025 | 18KB | 7 | ~8 | 22 |
| 17 | Additional Model Providers | L4447 | 16KB | 2 | ~2 | 27 |
| 18 | Structured Output Generation | L4697 | 13KB | 2 | ~3 | 12 |
| 19 | Tool System | L4917 | 18KB | 6 | ~4 | 23 |
| 20 | Creating Tools with @tool Decorator | L5370 | 20KB | 3 | ~4 | 19 |
| 21 | Tool Registry and Discovery | L5748 | 18KB | 4 | ~5 | 13 |
| 22 | Tool Execution Strategies | L6097 | 11KB | 3 | ~2 | 27 |
| 23 | Model Context Protocol (MCP) Integration | L6284 | 13KB | 2 | ~5 | 23 |
| 24 | Vended Tools and Sandbox Environments | L6509 | 20KB | 3 | ~2 | 23 |
| 25 | Extensibility System | L6812 | 18KB | 4 | ~4 | 26 |
| 26 | Plugin System | L7141 | 15KB | 6 | ~4 | 15 |
| 27 | Hook System and Events | L7538 | 14KB | 3 | ~6 | 28 |
| 28 | Custom Hook Providers | L7758 | 24KB | 3 | ~4 | 26 |
| 29 | Interrupt Handling and Human-in-the-Loop | L8270 | 28KB | 3 | ~5 | 16 |
| 30 | Agent Skills Plugin | L8748 | 11KB | 2 | ~2 | 25 |
| 31 | Steering System | L8958 | 14KB | 2 | ~1 | 20 |
| 32 | Context Offloader Plugin | L9196 | 15KB | 2 | ~2 | 20 |
| 33 | Memory System and Context Injection | L9402 | 28KB | 3 | ~0 | 22 |
| 34 | Goal Loop Plugin | L9779 | 14KB | 4 | ~3 | 11 |
| 35 | Multi-Agent Orchestration | L10111 | 9KB | 2 | ~0 | 34 |
| 36 | Multi-Agent Base and Patterns | L10295 | 13KB | 3 | ~7 | 24 |
| 37 | Graph-based Orchestration | L10548 | 29KB | 3 | ~18 | 24 |
| 38 | Swarm Collaboration | L11200 | 26KB | 6 | ~16 | 24 |
| 39 | Multi-Agent State and Persistence | L11836 | 12KB | 2 | ~8 | 28 |
| 40 | Agent-to-Agent (A2A) Protocol | L12044 | 8KB | 2 | ~1 | 10 |
| 41 | Telemetry and Observability | L12200 | 16KB | 3 | ~6 | 10 |
| 42 | OpenTelemetry Integration | L12521 | 11KB | 3 | ~4 | 15 |
| 43 | Tracing and Spans | L12749 | 14KB | 3 | ~5 | 8 |
| 44 | Metrics and Performance Monitoring | L13019 | 13KB | 2 | ~7 | 9 |
| 45 | Experimental Features | L13330 | 10KB | 2 | ~1 | 16 |
| 46 | Bidirectional Streaming Agent | L13494 | 15KB | 3 | ~1 | 20 |
| 47 | Bidirectional Model Providers | L13699 | 11KB | 2 | ~2 | 16 |
| 48 | Checkpoint System | L13873 | 8KB | 2 | ~3 | 19 |
| 49 | Development and Contributing | L14014 | 13KB | 3 | ~5 | 24 |
| 50 | Development Environment Setup | L14247 | 16KB | 2 | ~13 | 25 |
| 51 | Testing Infrastructure | L14592 | 17KB | 2 | ~5 | 29 |
| 52 | CI/CD Pipeline | L14866 | 42KB | 4 | ~5 | 33 |
| 53 | Team Governance and Design Process | L15604 | 16KB | 2 | ~0 | 15 |
| 54 | Documentation Site | L15869 | 11KB | 1 | ~0 | 21 |
| 55 | Site Architecture and Navigation | L16064 | 15KB | 4 | ~0 | 30 |
| 56 | Content Authoring and Code Snippets | L16313 | 18KB | 2 | ~0 | 29 |
| 57 | API Documentation Generation | L16604 | 14KB | 2 | ~0 | 11 |
| 58 | Glossary | L16910 | 16KB | 2 | ~3 | 33 |


## · Introduction to Strands Agents SDK  (L6)
  源文件: .github/CODEOWNERS, .gitignore, AGENTS.md, CODE_OF_CONDUCT.md, CONTRIBUTING.md, NOTICE, README.md, package-lock.json, package.json, pyproject.toml, site/src/content/docs/user-guide/build-with-ai.mdx, strandly/package.json
  Purpose and Scope
  What is Strands Agents SDK
  Core Capabilities
  System Architecture Overview
  Core Component Mapping
  Agent Execution Flow
  Extensibility Architecture
    · Hook System
    · Plugin System
    · Tool Provider Interface
  Model Provider Ecosystem
  Experimental Features
  Strands MCP Server
  Next Steps

## · Installation and Quick Start  (L270)
  源文件: .gitignore, AGENTS.md, CONTRIBUTING.md, README.md, package-lock.json, package.json, pyproject.toml, site/src/content/docs/contribute/contributing/documentation.mdx, site/src/content/docs/contribute/contributing/documentation.ts, site/src/content/docs/labs/ai-functions.mdx, site/src/content/docs/user-guide/concepts/agents/conversation-management.mdx, site/src/content/docs/user-guide/concepts/agents/conversation-management.ts
  Overview
  System Requirements
  Installation Paths
  Python SDK Installation
    · Minimal Setup
    · Optional Dependencies (Extras)
  TypeScript SDK Installation
    · Minimal Setup
  Quick Start Examples
    · Python Quick Start
    · TypeScript Quick Start
  Bridging Space: Model Selection
  Bridging Space: Tool Execution
  Development Setup (Monorepo)
    · Python SDK Development
    · TypeScript SDK Development
  Environment Configuration
    · AWS Credentials (Bedrock)
    · Model Access

## · Core Concepts and Architecture  (L544)
  源文件: .gitignore, AGENTS.md, CONTRIBUTING.md, README.md, package-lock.json, package.json, pyproject.toml, site/src/content/docs/user-guide/concepts/agents/agent-loop.mdx, strandly/package.json, strands-py/AGENTS.md, strands-py/docs/TESTING.md, strands-py/src/strands/telemetry/metrics.py
  Core Abstractions
    · Agent
    · Model
    · Tool
    · Hook
  Architectural Layers
  Event Loop Architecture
    · Event Loop Cycle Flow
    · Stop Reasons and Termination
  Streaming and Event Processing
    · Stream Processing Pipeline
  State Management
    · State Components
  Error Handling
  Cross-SDK Parity and Monorepo Structure
    · Monorepo Workspace Layout
    · Parity Principles
    · Implementation Details

## · Strands MCP Server  (L940)
  源文件: site/src/content/docs/user-guide/build-with-ai.mdx, strands-mcp/README.md, strands-mcp/src/strands_mcp_server/server.py, strands-mcp/src/strands_mcp_server/utils/cache.py, strands-mcp/src/strands_mcp_server/utils/indexer.py, strands-mcp/tests/test_cache.py, strands-mcp/tests/test_indexer.py, strands-mcp/tests/test_indexer_concurrency.py, strands-mcp/tests/test_server.py, strands-py/README.md, strands-ts/README.md
  Features
  Tools
    · `search_docs`
    · `fetch_doc`
    · TF-IDF Ranking Implementation
    · Diagram: Documentation Search Flow
    · Diagram: Document Fetch Flow
  Configuration
    · Diagram: Prefetching Mechanism
  Installation in MCP Clients
    · Prerequisites
    · Kiro
    · Cursor
    · VS Code
    · Claude Code
    · Other MCP Clients
    · Using with Strands Agents
    · Verify Connection

## · Agent System  (L1302)
  源文件: strands-py/src/strands/agent/agent.py, strands-py/src/strands/event_loop/event_loop.py, strands-py/tests/strands/event_loop/test_event_loop.py, strands-py/tests/strands/event_loop/test_event_loop_metadata.py, strands-py/tests/strands/event_loop/test_event_loop_structured_output.py, strands-ts/src/agent/__tests__/agent.hook.test.ts, strands-ts/src/agent/__tests__/agent.model-retry.test.ts, strands-ts/src/agent/__tests__/agent.test.ts, strands-ts/src/agent/agent.ts, strands-ts/src/conversation-manager/__tests__/null-conversation-manager.test.ts, strands-ts/src/hooks/__tests__/events.test.ts, strands-ts/src/hooks/events.ts
  Core Architecture
    · Agent System Components
  Execution Lifecycle
  Subsystem Overviews
    · Agent Class and Initialization
    · Event Loop and Execution Flow
    · Streaming Responses
    · Conversation Management
    · Agent State and Session Management
    · Error Handling and Recovery

## · Agent Class and Initialization  (L1483)
  源文件: strands-py/src/strands/__init__.py, strands-py/src/strands/agent/_concurrency.py, strands-py/src/strands/agent/agent.py, strands-py/src/strands/event_loop/event_loop.py, strands-py/src/strands/storage/__init__.py, strands-py/src/strands/tools/_caller.py, strands-py/src/strands/types/exceptions.py, strands-py/tests/strands/agent/test_agent.py, strands-py/tests/strands/agent/test_concurrency.py, strands-py/tests/strands/event_loop/test_event_loop.py, strands-py/tests/strands/event_loop/test_event_loop_metadata.py, strands-py/tests/strands/event_loop/test_event_loop_structured_output.py
  Overview
  Agent Architecture
    · Agent Component Mapping
  Constructor Parameters
    · Model Configuration
    · Conversation & Tooling
    · State & Persistence
  Initialization Flow
    · Initialization Sequence
  Concurrency and Idempotency
    · Concurrency Controller
    · Idempotency Token
  ToolCaller Proxy
  Default Behaviors and Sentinels
    · Retry Strategy
    · Callback Handler

## · Event Loop and Execution Flow  (L1707)
  源文件: site/src/content/docs/user-guide/concepts/agents/agent-loop.mdx, strands-py/AGENTS.md, strands-py/docs/TESTING.md, strands-py/src/strands/agent/agent.py, strands-py/src/strands/event_loop/event_loop.py, strands-py/src/strands/event_loop/streaming.py, strands-py/src/strands/telemetry/metrics.py, strands-py/src/strands/tools/executors/_executor.py, strands-py/src/strands/tools/executors/sequential.py, strands-py/src/strands/tools/mcp/mcp_types.py, strands-py/src/strands/types/streaming.py, strands-py/tests/strands/event_loop/test_event_loop.py
  Overview
  Event Loop Architecture
    · Code Entity Flow Diagram
  Invocation State Management
    · Invocation State Structure
  Cycle Initialization and Lifecycle
    · Initialization Sequence Diagram
  Model Execution with Retry Logic
    · Retry Configuration
  Stop Reason Handling
    · Limit Validation
  Tool Execution and Recursion
    · Recursion Mechanics
  InvokeModelStage Middleware Chain
  Metrics and Usage Tracking

## · Streaming Responses  (L1976)
  源文件: strands-py/src/strands/agent/agent.py, strands-py/src/strands/event_loop/event_loop.py, strands-py/src/strands/event_loop/streaming.py, strands-py/src/strands/types/streaming.py, strands-py/tests/strands/event_loop/test_event_loop.py, strands-py/tests/strands/event_loop/test_event_loop_metadata.py, strands-py/tests/strands/event_loop/test_event_loop_structured_output.py, strands-py/tests/strands/event_loop/test_streaming.py, strands-ts/src/agent/__tests__/agent.hook.test.ts, strands-ts/src/agent/__tests__/agent.model-retry.test.ts, strands-ts/src/agent/__tests__/agent.test.ts, strands-ts/src/agent/agent.ts
  Purpose and Scope
  Using the Streaming API
    · Basic Usage Patterns
  Event Hierarchy and Types
    · Lifecycle and Data Events (TypeScript)
    · Model Streaming Events (Python)
  Internal Streaming Architecture
    · Stream Transformation Flow
    · Message Normalization
  Event Processing and Hooks
    · Hook Integration
    · Middleware Stages
  Agent Results and Termination

## · Conversation Management  (L2195)
  源文件: site/src/content/docs/contribute/contributing/documentation.mdx, site/src/content/docs/contribute/contributing/documentation.ts, site/src/content/docs/labs/ai-functions.mdx, site/src/content/docs/user-guide/concepts/agents/conversation-management.mdx, site/src/content/docs/user-guide/concepts/agents/conversation-management.ts, site/src/content/docs/user-guide/concepts/agents/conversation-management_imports.ts, site/src/content/docs/user-guide/concepts/context-management.mdx, site/src/content/docs/user-guide/concepts/context-management.ts, site/src/content/docs/user-guide/concepts/context-management_imports.ts, site/src/content/docs/user-guide/concepts/model-providers/amazon-bedrock.ts, site/src/content/docs/user-guide/concepts/model-providers/index.mdx, site/src/content/docs/user-guide/concepts/model-providers/index.ts
  Overview
  Architecture
    · ConversationManager Interface
  Integration with Agent Lifecycle
    · Lifecycle Integration Flow
    · 1. Context Overflow Handling (Reactive)
    · 2. Proactive Context Compression
  Built-in Conversation Managers
    · NullConversationManager
    · SlidingWindowConversationManager
    · SummarizingConversationManager
  Context Manager Modes
    · Automatic Context Management (`"auto"`)
    · Agentic Context Management (`"agentic"`)
    · Null Context Management (`null`)
  Data Flow: Summarization Process
  State Persistence
  Summary of Strategy Differences

## · Agent State and Session Management  (L2657)
  源文件: site/src/content/docs/user-guide/concepts/agents/session-management.mdx, site/src/content/docs/user-guide/concepts/agents/session-manager.ts, site/src/content/docs/user-guide/concepts/memory/bedrock-knowledge-base.mdx, site/src/content/docs/user-guide/concepts/memory/bedrock-knowledge-base.ts, site/src/content/docs/user-guide/concepts/memory/bedrock-knowledge-base_imports.ts, site/src/content/docs/user-guide/concepts/plugins/context-offloader.mdx, site/src/content/docs/user-guide/concepts/plugins/context-offloader.ts, site/src/content/docs/user-guide/concepts/plugins/context-offloader_imports.ts, site/src/content/docs/user-guide/concepts/storage.mdx, site/src/content/docs/user-guide/concepts/storage.py, site/src/content/docs/user-guide/concepts/storage.ts, site/src/content/docs/user-guide/concepts/storage_imports.ts
  Overview
  AgentState: Custom Application State
    · Code Entity Mapping: Agent State
  Session Management Implementations
    · 1. SnapshotSessionManager (Recommended)
    · 2. RepositorySessionManager (Legacy/Structured)
  Storage Backends
    · Code Entity Mapping: Storage and Session Flow
  Specialized State Persistence
    · Context Offloader State
    · Bedrock Knowledge Base Store

## · Error Handling and Recovery  (L2835)
  源文件: site/src/content/docs/user-guide/concepts/agents/prompts.mdx, site/src/content/docs/user-guide/concepts/agents/retry-strategies.mdx, site/src/content/docs/user-guide/concepts/agents/snapshots.mdx, site/src/content/docs/user-guide/concepts/agents/state.mdx, site/src/content/docs/user-guide/concepts/agents/structured-output.mdx, site/src/content/docs/user-guide/concepts/model-providers/google.mdx, site/src/content/docs/user-guide/concepts/multi-agent/agents-as-tools.mdx, site/src/content/docs/user-guide/safety-security/trusted-message-history.mdx, strands-py/src/strands/__init__.py, strands-py/src/strands/agent/_concurrency.py, strands-py/src/strands/agent/agent.py, strands-py/src/strands/event_loop/_retry.py
  Exception Types
    · Core Exception Hierarchy
  Retry Strategy Architecture
  ModelRetryStrategy Configuration
    · Initialization and Defaults
    · Exponential Backoff Calculation
  Context Window Overflow Handling
  Max Tokens Handling and Recovery
    · Message Recovery Utility
  Cancellation and Interruption
    · Cancellation Pattern
    · Interrupt Handling
  Concurrency and Idempotency Control
    · ConcurrentInvocationMode
    · Idempotency Deduplication

## · Model Providers  (L3101)
  源文件: site/src/content/docs/user-guide/concepts/model-providers/amazon-bedrock.mdx, site/src/content/docs/user-guide/concepts/model-providers/anthropic.mdx, site/src/content/docs/user-guide/concepts/model-providers/anthropic.ts, site/src/content/docs/user-guide/concepts/model-providers/anthropic_imports.ts, strands-py/src/strands/models/anthropic.py, strands-py/src/strands/models/bedrock.py, strands-py/src/strands/models/model.py, strands-py/tests/strands/models/test_anthropic.py, strands-py/tests/strands/models/test_bedrock.py, strands-ts/src/models/__tests__/anthropic.test.ts, strands-ts/src/models/__tests__/bedrock.test.ts, strands-ts/src/models/__tests__/defaults.test.ts
  The Model Abstraction
  How Models Integrate with Agents
  Available Model Providers
  Provider Configuration and Caching
  Structured Output

## · Model Provider Architecture  (L3280)
  源文件: site/src/content/docs/user-guide/concepts/model-providers/amazon-bedrock.mdx, site/src/content/docs/user-guide/concepts/model-providers/anthropic.mdx, site/src/content/docs/user-guide/concepts/model-providers/anthropic.ts, site/src/content/docs/user-guide/concepts/model-providers/anthropic_imports.ts, strands-py/src/strands/_context_manager/modes/agentic/agentic_context.py, strands-py/src/strands/agent/conversation_manager/conversation_manager.py, strands-py/src/strands/models/_defaults.py, strands-py/src/strands/models/anthropic.py, strands-py/src/strands/models/bedrock.py, strands-py/src/strands/models/model.py, strands-py/tests/strands/agent/test_conversation_manager.py, strands-py/tests/strands/agent/test_summarizing_conversation_manager.py
  Purpose and Scope
  Model Abstract Base Class
    · Code Entity Space: Model Class Hierarchy
    · Core Methods and Properties
  Token Counting and Estimation
    · Native vs. Heuristic Counting
  Prompt Caching
    · Cache Configuration
    · Provider Implementation Details
  The Stream Method and Event Normalization
    · Request Flow: Code Interaction
    · StreamEvent Types
  Message Formatting Pipeline
  Switching Providers

## · AWS Bedrock Models  (L3487)
  源文件: site/src/content/docs/user-guide/concepts/model-providers/amazon-bedrock.mdx, site/src/content/docs/user-guide/concepts/model-providers/anthropic.mdx, site/src/content/docs/user-guide/concepts/model-providers/anthropic.ts, site/src/content/docs/user-guide/concepts/model-providers/anthropic_imports.ts, strands-py/src/strands/models/anthropic.py, strands-py/src/strands/models/bedrock.py, strands-py/src/strands/models/model.py, strands-py/tests/strands/models/test_anthropic.py, strands-py/tests/strands/models/test_bedrock.py, strands-ts/src/models/__tests__/anthropic.test.ts, strands-ts/src/models/__tests__/bedrock.test.ts, strands-ts/src/models/__tests__/defaults.test.ts
  Overview
    · Class Hierarchy
  Configuration
    · BedrockConfig Options
    · Initialization and Region Resolution
  Prompt Caching
    · Caching Strategy
    · TTL Constraint
  Guardrails Integration
    · Guardrail Redaction
    · Latest Message Assessment
  Media and S3 Handling
  Implementation Details
    · Llama Tool Turn Workaround
    · Token Counting
    · Stop Reason Normalization
  Error Handling

## · OpenAI Compatible Models  (L3715)
  源文件: site/src/content/docs/user-guide/concepts/model-providers/openai.mdx, site/src/content/docs/user-guide/concepts/model-providers/openai.ts, site/src/content/docs/user-guide/concepts/model-providers/openai_imports.ts, strands-py/src/strands/models/_openai_bedrock.py, strands-py/src/strands/models/_openai_errors.py, strands-py/src/strands/models/openai.py, strands-py/src/strands/models/openai_responses.py, strands-py/tests/strands/models/test_openai.py, strands-py/tests/strands/models/test_openai_errors.py, strands-py/tests/strands/models/test_openai_responses.py, strands-py/tests_integ/models/test_mantle_routing.py, strands-py/tests_integ/models/test_model_mantle.py
  Purpose and Scope
  OpenAIModel Class Overview
    · Class Structure
  OpenAI Responses API Model
    · Key Differences from OpenAIModel
  Configuration
    · Initialization Patterns
    · Mantle Routing
  Message Formatting Pipeline
    · Content Block Mapping
    · Tool Message Handling
  OpenAI-Specific Features
    · Built-in Tools Support (Responses API)
    · Reasoning Content (o1/o3 Models)
    · Image Splitting in Tool Results
    · LiteLLM Proxy Support
  Error Handling and Throttling
    · Exception Mapping
  Structured Output

## · LiteLLM Multi-Provider Support  (L4025)
  源文件: site/docs/examples/cdk/deploy_to_apprunner/package-lock.json, site/docs/examples/cdk/deploy_to_apprunner/package.json, site/docs/examples/cdk/deploy_to_ec2/package-lock.json, site/docs/examples/cdk/deploy_to_ec2/package.json, site/docs/examples/cdk/deploy_to_fargate/package-lock.json, site/docs/examples/cdk/deploy_to_fargate/package.json, site/docs/examples/cdk/deploy_to_lambda/package-lock.json, site/docs/examples/cdk/deploy_to_lambda/package.json, site/scripts/api-generation-typescript.ts, strandly/src/cli.ts, strands-py/src/strands/hooks/registry.py, strands-py/src/strands/models/__init__.py
  Purpose and Scope
  Architecture Overview
    · LiteLLMModel Class Hierarchy
    · Provider Support Matrix
  Configuration
    · Basic Configuration
    · Client Arguments
    · Proxy Configuration
  Message Formatting
    · Gemini Thought Signatures
    · Content Types
  Streaming Behavior
    · Dual-Mode Response Handling
    · Content Switching and Event Generation
  Structured Output
    · Adaptive Output Strategy
  Model Routing System
    · ModelRouter
    · RoutingStrategy
    · FallbackStrategy
  Provider-Specific Features
    · Prompt Caching
    · Reasoning Support
  Error Handling
    · Context Window Overflow
    · Response Validation

## · Additional Model Providers  (L4447)
  源文件: site/src/content/docs/user-guide/concepts/model-providers/amazon-bedrock.mdx, site/src/content/docs/user-guide/concepts/model-providers/anthropic.mdx, site/src/content/docs/user-guide/concepts/model-providers/anthropic.ts, site/src/content/docs/user-guide/concepts/model-providers/anthropic_imports.ts, strands-py/src/strands/models/anthropic.py, strands-py/src/strands/models/bedrock.py, strands-py/src/strands/models/gemini.py, strands-py/src/strands/models/llamaapi.py, strands-py/src/strands/models/llamacpp.py, strands-py/src/strands/models/mistral.py, strands-py/src/strands/models/model.py, strands-py/src/strands/models/ollama.py
  Provider Overview and Data Flow
    · Model Request Transformation Flow
  Anthropic Claude
    · Key Features
  Google Gemini
    · Tool Integration
    · Features
  Mistral AI
    · Configuration
    · Formatting Logic
  Ollama (Local Models)
    · Message Flattening
    · Configuration
  Amazon SageMaker AI
    · Request Structure
    · User Agent
  LlamaAPI and Writer
    · LlamaAPI
    · Writer
  LlamaCpp (Local Server)
    · Advanced Features
  Vercel AI (TypeScript)
    · Key Features
  Error Handling and Throttling

## · Structured Output Generation  (L4697)
  源文件: strands-py/src/strands/agent/agent.py, strands-py/src/strands/event_loop/event_loop.py, strands-py/tests/strands/event_loop/test_event_loop.py, strands-py/tests/strands/event_loop/test_event_loop_metadata.py, strands-py/tests/strands/event_loop/test_event_loop_structured_output.py, strands-ts/src/telemetry/__tests__/config.test.node.ts, strands-ts/src/telemetry/__tests__/config.test.ts, strands-ts/src/telemetry/config.ts, strands-ts/src/tools/__tests__/zod-tool.test-d.ts, strands-ts/src/tools/tool-factory.ts, strands-ts/src/tools/zod-tool.ts, strands-ts/test/integ/telemetry.test.node.ts
  Overview
  Architecture and Dispatch Flow
  Implementation Details
    · StructuredOutputContext (Python)
    · Schema Conversion (Python)
    · `zod-tool` Factory (TypeScript)
  Provider Specific Implementations
    · OpenAI and LiteLLM
    · AWS Bedrock
  Agent Integration
  Streaming and Tool Choice

## · Tool System  (L4917)
  源文件: site/src/content/docs/user-guide/concepts/agents/agent-loop.mdx, site/src/content/docs/user-guide/concepts/tools/vended-tools-imports.ts, site/src/content/docs/user-guide/concepts/tools/vended-tools.mdx, site/src/content/docs/user-guide/concepts/tools/vended-tools.ts, strands-py/AGENTS.md, strands-py/docs/TESTING.md, strands-py/src/strands/experimental/tools/__init__.py, strands-py/src/strands/experimental/tools/stop/__init__.py, strands-py/src/strands/experimental/tools/stop/stop.py, strands-py/src/strands/telemetry/metrics.py, strands-py/src/strands/tools/executors/_executor.py, strands-py/src/strands/tools/executors/sequential.py
  Purpose and Scope
  Architecture Overview
    · Tool Lifecycle
  Core Interfaces
    · AgentTool Abstract Base Class
    · ToolSpec Structure
  Tool Definition
    · Using the @tool Decorator
    · Metadata Extraction Process
    · Module-Based Tools
    · ToolProvider Interface
  Tool Registry
    · ToolRegistry Class
    · Tool Name Validation
  Tool Execution
    · Execution Flow
    · Input Validation
  Tool Context and Framework Integration
    · ToolContext Injection
  Schema Normalization
    · Tool Spec Normalization
  Tool Result Format

## · Creating Tools with @tool Decorator  (L5370)
  源文件: strands-py/src/strands/tools/decorator.py, strands-py/tests/strands/tools/test_decorator.py, strands-ts/src/__fixtures__/tool-helpers.ts, strands-ts/src/__tests__/interrupt.test.ts, strands-ts/src/hooks/__tests__/registry.test.ts, strands-ts/src/hooks/index.ts, strands-ts/src/hooks/registry.ts, strands-ts/src/multiagent/__tests__/graph.tracer.test.ts, strands-ts/src/multiagent/__tests__/state.test.ts, strands-ts/src/telemetry/__tests__/config.test.node.ts, strands-ts/src/telemetry/__tests__/config.test.ts, strands-ts/src/telemetry/config.ts
  Purpose and Scope
  Overview
    · Decorator Syntax
  Tool Transformation Architecture
  Metadata Extraction
    · FunctionToolMetadata Class
    · Docstring Processing
    · Type Hint Processing
  ToolContext Injection
    · Enabling Context Injection
    · ToolContext Structure
  DecoratedFunctionTool Implementation
  Execution Flow
    · Tool Stream Processing
    · Return Value Handling
  Input Validation and Normalization
    · Schema Normalization
    · Validation Logic
  Direct Tool Calling
  Error and Interrupt Handling
    · Interruptions
    · General Errors
  TypeScript Tool Factories
    · `FunctionTool`
    · `ZodTool`
    · Tool Type Hierarchy

## · Tool Registry and Discovery  (L5748)
  源文件: strands-py/src/strands/tools/loader.py, strands-py/src/strands/tools/registry.py, strands-py/src/strands/tools/tools.py, strands-py/src/strands/vended_interventions/cedar/__init__.py, strands-py/tests/strands/tools/test_registry.py, strands-py/tests/strands/tools/test_tools.py, strands-py/tests/strands/vended_interventions/cedar/test_cedar_authorization.py, strands-py/tests/strands/vended_interventions/cedar/test_cedar_integration.py, strands-py/tests/strands/vended_interventions/cedar/test_schema_generator.py, strands-ts/src/agent/__tests__/tool-caller.test.ts, strands-ts/src/agent/tool-caller.ts, strands-ts/src/registry/__tests__/tool-registry.test.ts
  Overview
  ToolRegistry Internal Structure
  Tool Loading with process_tools() (Python)
    · Supported Input Formats (Python)
  Tool Registry Operations (TypeScript)
  ToolProvider Lifecycle (Python)
  Hot-Reloading and Directory Discovery (Python)
    · Directory Loading
    · Hot-Reload Logic
  Name Normalization and Collision Prevention
  Tool Registry Data Flow
  Tool Discovery via Module Scanning (Python)
  ToolCallerProxy for Direct Tool Invocation
    · Python `ToolCaller`
    · TypeScript `ToolCaller`

## · Tool Execution Strategies  (L6097)
  源文件: site/src/content/docs/user-guide/concepts/agents/agent-loop.mdx, site/src/content/docs/user-guide/concepts/tools/executors.ts, strands-py/AGENTS.md, strands-py/docs/TESTING.md, strands-py/src/strands/agent/agent.py, strands-py/src/strands/event_loop/event_loop.py, strands-py/src/strands/telemetry/metrics.py, strands-py/src/strands/tools/executors/_executor.py, strands-py/src/strands/tools/executors/sequential.py, strands-py/src/strands/tools/mcp/mcp_types.py, strands-py/tests/strands/event_loop/test_event_loop.py, strands-py/tests/strands/event_loop/test_event_loop_metadata.py
  ToolExecutor Abstraction
    · ToolExecutor Class Hierarchy
  ConcurrentToolExecutor
    · Concurrent Execution Flow
  SequentialToolExecutor
    · Execution Behavior
  Tool Execution Flow & Hooks
    · Lifecycle Diagram: Natural Language to Code Entity
    · Hook Integration
  Structured Output Integration
  Validation and Error Handling
    · Validation Logic
    · Error Handling Strategies

## · Model Context Protocol (MCP) Integration  (L6284)
  源文件: site/src/content/docs/user-guide/concepts/tools/mcp-tools.mdx, site/src/content/docs/user-guide/concepts/tools/mcp-tools.ts, strands-py/src/strands/tools/mcp/__init__.py, strands-py/src/strands/tools/mcp/mcp_agent_tool.py, strands-py/src/strands/tools/mcp/mcp_client.py, strands-py/src/strands/tools/mcp/mcp_instrumentation.py, strands-py/src/strands/types/tools.py, strands-py/tests/strands/tools/mcp/test_mcp_agent_tool.py, strands-py/tests/strands/tools/mcp/test_mcp_client.py, strands-py/tests/strands/tools/mcp/test_mcp_client_load_servers.py, strands-py/tests/strands/tools/mcp/test_mcp_client_tasks.py, strands-py/tests/strands/tools/mcp/test_mcp_client_tool_provider.py
  Overview
  Architecture and Threading Model
    · Background Thread Design
    · Transport Abstraction
  Task-Augmented Execution (Experimental)
  Tool Discovery and Registration
    · Tool Discovery Flow
    · Tool Filtering
  Tool Execution and Content Mapping
    · Content Mapping
    · Structured Content and Metadata
  Prompts and Resources
    · Prompts
    · Resources
  Elicitation Support
  OpenTelemetry Instrumentation

## · Vended Tools and Sandbox Environments  (L6509)
  源文件: site/src/content/docs/user-guide/concepts/sandbox/index.ts, site/src/content/docs/user-guide/concepts/sandbox/index_imports.ts, site/src/content/docs/user-guide/concepts/tools/vended-tools-imports.ts, site/src/content/docs/user-guide/concepts/tools/vended-tools.mdx, site/src/content/docs/user-guide/concepts/tools/vended-tools.ts, strands-py/src/strands/experimental/tools/__init__.py, strands-py/src/strands/experimental/tools/stop/__init__.py, strands-py/src/strands/experimental/tools/stop/stop.py, strands-py/src/strands/sandbox/__init__.py, strands-py/src/strands/sandbox/docker.py, strands-py/src/strands/sandbox/not_a_sandbox_local_environment.py, strands-py/src/strands/sandbox/ssh.py
  Vended Tools
    · Quick Start
    · Available Vended Tools
  Sandbox Environments
    · Sandbox Types
    · Tool Execution in Sandboxes

## · Extensibility System  (L6812)
  源文件: strands-py/src/strands/_middleware/README.md, strands-py/src/strands/_middleware/__init__.py, strands-py/src/strands/_middleware/registry.py, strands-py/src/strands/_middleware/stages.py, strands-py/src/strands/_middleware/types.py, strands-py/src/strands/experimental/bidi/agent/agent.py, strands-py/src/strands/interrupt.py, strands-py/src/strands/types/_events.py, strands-py/tests/strands/agent/test_agent_cancellation.py, strands-py/tests/strands/middleware/test_agent_middleware.py, strands-py/tests/strands/middleware/test_agent_stream_middleware.py, strands-py/tests/strands/middleware/test_execute_tool_middleware.py
  Extensibility Architecture
    · Extension Architecture Overview
  Hook System
    · Event Lifecycle
    · HookRegistry and Type Inference
  Middleware System
    · Middleware Stages
    · Middleware Execution Flow
  Plugin System
    · Plugin Lifecycle
    · Method Discovery
  Specialized Subsystems
    · Interrupt Handling and Human-in-the-Loop
    · Agent Skills
    · Steering System
    · Context Offloading
    · Memory System and Context Injection
    · Goal Loop Plugin
  Summary

## · Plugin System  (L7141)
  源文件: strands-py/src/strands/agent/agent.py, strands-py/src/strands/event_loop/event_loop.py, strands-py/tests/strands/event_loop/test_event_loop.py, strands-py/tests/strands/event_loop/test_event_loop_metadata.py, strands-py/tests/strands/event_loop/test_event_loop_structured_output.py, strands-ts/src/agent/__tests__/agent.hook.test.ts, strands-ts/src/agent/__tests__/agent.model-retry.test.ts, strands-ts/src/agent/__tests__/agent.test.ts, strands-ts/src/agent/agent.ts, strands-ts/src/conversation-manager/__tests__/null-conversation-manager.test.ts, strands-ts/src/hooks/__tests__/events.test.ts, strands-ts/src/hooks/events.ts
  Plugin Architecture
    · Plugin Class Structure
  Plugin Base Class
    · Required Attributes
    · Required Methods
    · Initialization and Auto-Discovery
  Plugin Lifecycle
    · Lifecycle Diagram
    · Lifecycle Phases
  Plugin Registry
    · Registry Implementation
    · Key Features
    · Auto-Registration Process
  The @hook Decorator
    · Decorator Mechanics
  Creating Custom Plugins
    · Pattern 1: Decorator-Only Plugin
    · Pattern 2: Plugin with Custom Initialization
    · Pattern 3: Async Initialization
  Method Resolution Order (MRO) and Inheritance
    · MRO Processing

## · Hook System and Events  (L7538)
  源文件: site/src/content/docs/user-guide/concepts/agents/hooks.mdx, site/src/content/docs/user-guide/concepts/agents/hooks.ts, site/src/content/docs/user-guide/concepts/interrupts.mdx, site/src/content/docs/user-guide/concepts/tools/custom-tools.mdx, site/src/content/docs/user-guide/concepts/tools/executors.mdx, site/src/content/docs/user-guide/concepts/tools/tools.ts, strands-py/docs/HOOKS.md, strands-py/src/strands/hooks/__init__.py, strands-py/src/strands/hooks/events.py, strands-py/tests/fixtures/mock_hook_provider.py, strands-py/tests/strands/agent/hooks/test_events.py, strands-py/tests/strands/agent/test_agent_hooks.py
  Hook System Architecture
    · Core Components and Entities
    · Data Flow and Registration
  Event Lifecycle and Types
    · Execution Event Flow
    · Key Event Categories
  Event Modification and Steering
    · Writable Properties and Controls
    · Callback Ordering
  Interrupt Handling
  Experimental and Bidi Hooks

## · Custom Hook Providers  (L7758)
  源文件: site/src/content/docs/user-guide/concepts/tools/executors.ts, strands-py/src/strands/_middleware/README.md, strands-py/src/strands/_middleware/__init__.py, strands-py/src/strands/_middleware/registry.py, strands-py/src/strands/_middleware/stages.py, strands-py/src/strands/_middleware/types.py, strands-py/src/strands/experimental/bidi/agent/agent.py, strands-py/src/strands/interrupt.py, strands-py/src/strands/types/_events.py, strands-py/tests/strands/agent/test_agent_cancellation.py, strands-py/tests/strands/middleware/test_agent_middleware.py, strands-py/tests/strands/middleware/test_agent_stream_middleware.py
  Purpose and Scope
  The HookProvider Protocol
    · Protocol Definition
  Basic Implementation Pattern
    · Minimal Hook Provider
    · Integration with Agent
  Callback Signatures and Type Inference
    · Explicit Event Type Registration
    · Type Inference from Annotations
    · Union Type Support
    · List of Event Types
  Synchronous vs Asynchronous Callbacks
    · Synchronous Callbacks
    · Asynchronous Callbacks
    · Restrictions
  Hook Provider Architecture
    · Data Flow: Provider Registration to Execution
  Multi-Agent Hook Providers
    · Implementation Example for Multi-Agent
  Callback Execution Flow
    · Registration and Invocation Sequence
  Advanced Callback Behaviors
    · Reverse Order for Cleanup Events
    · Interrupt Aggregation
    · Deterministic Cancellation
    · Token Limit Recovery
  Middleware Stages and the MiddlewareRegistry
    · MiddlewareRegistry
    · Middleware Stages
    · Middleware Execution Model
    · Middleware-Initiated Interrupts
    · Hooks vs. Middleware
  Summary of Constraints

## · Interrupt Handling and Human-in-the-Loop  (L8270)
  源文件: site/src/content/docs/user-guide/concepts/agents/interventions/cedar-authorization.mdx, site/src/content/docs/user-guide/concepts/agents/interventions/cedar-authorization.py, site/src/content/docs/user-guide/concepts/agents/interventions/cedar-authorization.ts, site/src/content/docs/user-guide/concepts/agents/interventions/cedar-authorization_imports.ts, site/src/content/docs/user-guide/concepts/agents/interventions/human-in-the-loop.mdx, site/src/content/docs/user-guide/concepts/agents/interventions/human-in-the-loop.py, site/src/content/docs/user-guide/concepts/agents/interventions/human-in-the-loop.ts, site/src/content/docs/user-guide/concepts/agents/interventions/human-in-the-loop_imports.ts, site/src/content/docs/user-guide/concepts/agents/interventions/index.mdx, site/src/content/docs/user-guide/concepts/agents/interventions/interventions.py, site/src/content/docs/user-guide/concepts/agents/interventions/interventions.ts, site/src/content/docs/user-guide/concepts/agents/interventions/interventions_imports.ts
  Purpose and Scope
  Core Entities
    · Interrupt Data Model
    · InterruptException
    · _InterruptState
    · Interruptible Protocol
  Code-to-Logic Mapping
    · Entity Relationship: Interrupt State and Responses
    · Interrupt Flow: Middleware to Exception
  Interrupt Lifecycle
    · 1. Raising the Interrupt
    · 2. Returning to the User
    · 3. Responding and Resuming
  Implementation Details
    · Interrupt ID Generation
    · State Versioning
    · JSON Serialization
    · Interrupt State Context
    · Middleware-initiated Interrupts
  Human-in-the-Loop (HITL) Intervention
    · How it Works
    · Usage Modes
    · Risk Classifier
    · Trust Mode
  Cedar Authorization Intervention
    · How it Works
    · Basic Usage
    · Role-based Access Control
    · Rate Limiting
    · Schema Validation
    · Environment Gating
    · File-based Policies and Hot Reload
  Summary of Key Classes and Methods

## · Agent Skills Plugin  (L8748)
  源文件: .agents/references/voice-guide.md, .agents/skills/README.md, .agents/skills/docs-audit/SKILL.md, .agents/skills/docs-reviewer/SKILL.md, .agents/skills/docs-writer/SKILL.md, .agents/skills/pr-create/SKILL.md, .agents/skills/pr-feedback/SKILL.md, .agents/skills/pr-feedback/fetch-pr-feedback.sh, .agents/skills/pr-writer/SKILL.md, .agents/skills/pr-writer/get-diff.sh, .agents/skills/pre-push/SKILL.md, .agents/skills/pre-push/run-checks.sh
  Overview and Purpose
  Data Model: The Skill Dataclass
  Skill Discovery and Loading
    · SKILL.md Format
    · The `.agents/skills` Directory Structure
  Implementation Detail
    · System Prompt Injection
    · The Skills Tool
    · Architecture: Plugin Integration Flow
  Code Entity Mapping
  Usage Example

## · Steering System  (L8958)
  源文件: site/src/content/docs/user-guide/concepts/agents/interventions/human-in-the-loop.mdx, site/src/content/docs/user-guide/concepts/agents/interventions/human-in-the-loop.py, site/src/content/docs/user-guide/concepts/agents/interventions/human-in-the-loop.ts, site/src/content/docs/user-guide/concepts/agents/interventions/human-in-the-loop_imports.ts, site/src/content/docs/user-guide/concepts/agents/interventions/index.mdx, site/src/content/docs/user-guide/concepts/agents/interventions/interventions.py, site/src/content/docs/user-guide/concepts/agents/interventions/interventions.ts, site/src/content/docs/user-guide/concepts/agents/interventions/interventions_imports.ts, site/src/content/docs/user-guide/concepts/agents/interventions/steering.mdx, site/src/content/docs/user-guide/concepts/agents/interventions/steering.ts, site/src/content/docs/user-guide/concepts/agents/interventions/steering_imports.ts, site/src/content/docs/user-guide/concepts/plugins/steering.mdx
  Core Architecture
    · Steering Lifecycle Diagram
  Key Components
    · SteeringHandler (Python)
    · SteeringHandler (TypeScript)
    · Steering Actions
  LLM-Driven Steering
    · Implementation Pattern
  Context and State Management
    · LedgerProvider (Python) / ToolLedgerProvider (TypeScript)
    · Data Flow Diagram
  Advanced Use Cases
    · Forcing Tool Usage
    · Multi-Step Retries

## · Context Offloader Plugin  (L9196)
  源文件: site/docs/examples/typescript/deploy_to_bedrock_agentcore/invoke.ts, site/scripts/astro-broken-links-checker-check-links.js, site/src/content/docs/user-guide/concepts/agents/session-management.mdx, site/src/content/docs/user-guide/concepts/agents/session-manager.ts, site/src/content/docs/user-guide/concepts/plugins/context-offloader.mdx, site/src/content/docs/user-guide/concepts/plugins/context-offloader.ts, site/src/content/docs/user-guide/concepts/plugins/context-offloader_imports.ts, site/src/content/docs/user-guide/concepts/storage.mdx, site/src/content/docs/user-guide/concepts/storage.py, site/src/content/docs/user-guide/concepts/storage.ts, site/src/content/docs/user-guide/concepts/storage_imports.ts, site/src/content/docs/user-guide/concepts/streaming/async-iterators.ts
  Overview and Configuration
    · Configuration Parameters
    · Content Handling
  Architecture and Data Flow
    · Data Flow: Tool Result Interception
  Storage Backends
    · 1. InMemoryStorage
    · 2. FileStorage
    · 3. S3Storage
  Code Entity Map
    · System Entity Mapping
  The Retrieval Tool
    · Implementation Details
  The Search Module
    · Key Functions

## · Memory System and Context Injection  (L9402)
  源文件: .agents/references/terminology.md, site/src/content/docs/user-guide/concepts/memory/bedrock-knowledge-base.mdx, site/src/content/docs/user-guide/concepts/memory/bedrock-knowledge-base.ts, site/src/content/docs/user-guide/concepts/memory/bedrock-knowledge-base_imports.ts, site/src/content/docs/user-guide/concepts/memory/overview.mdx, site/src/content/docs/user-guide/concepts/memory/overview.ts, site/src/content/docs/user-guide/concepts/memory/overview_imports.ts, site/src/content/docs/user-guide/concepts/memory/test-memory-store.mdx, site/src/content/docs/user-guide/concepts/memory/test-memory-store.ts, site/src/content/docs/user-guide/concepts/memory/test-memory-store_imports.ts, site/src/content/docs/user-guide/concepts/plugins/context-injector.mdx, site/src/content/docs/user-guide/concepts/plugins/context-injector.ts
  MemoryManager
    · MemoryManager Tools
    · Data Flow for Memory Operations
  MemoryStore Interface
    · `MemoryEntry`
  Automatic Extraction
    · `ExtractionConfig`
    · `ExtractionCoordinator`
    · `ModelExtractor`
  BedrockKnowledgeBaseStore
    · Key Features
    · Configuration
  TestMemoryStore
    · Key Characteristics
  ContextInjector Plugin
    · `MemoryInjectionConfig`
    · Injection Subsystem

## · Goal Loop Plugin  (L9779)
  源文件: .agents/references/voice-guide.md, .agents/skills/docs-audit/SKILL.md, .agents/skills/docs-reviewer/SKILL.md, .agents/skills/docs-writer/SKILL.md, site/src/content/docs/user-guide/concepts/agents/agent-loop.ts, site/src/content/docs/user-guide/concepts/plugins/goal-loop.mdx, site/src/content/docs/user-guide/concepts/plugins/goal-loop.ts, site/src/content/docs/user-guide/concepts/plugins/goal-loop_imports.ts, strands-py/src/strands/vended_plugins/goal/__init__.py, strands-py/src/strands/vended_plugins/goal/judge.py, strands-py/tests/strands/vended_plugins/goal/__init__.py
  Purpose and Scope
  Overview of Behavior
  Key Classes and Functions
    · GoalLoop (Main Plugin Class)
    · Validator Interface and ValidationOutcome
    · Judge Component (Natural-Language Validator)
  Data Flow and Execution Sequence
  Example Usage
  Configuration Parameters
  Inspecting Plugin Results
  Integration with the Agent Event Loop
  Summary Diagram: Natural Language Goal to Code
  Summary

## · Multi-Agent Orchestration  (L10111)
  源文件: .gitignore, AGENTS.md, CONTRIBUTING.md, README.md, package-lock.json, package.json, pyproject.toml, site/src/content/docs/user-guide/concepts/multi-agent/swarm.mdx, strandly/package.json, strands-py/src/strands/multiagent/__init__.py, strands-py/src/strands/multiagent/base.py, strands-py/src/strands/multiagent/graph.py
  Overview and Architecture
    · Multi-Agent Abstraction Hierarchy
  Core Components
    · Multi-Agent Base and Patterns
    · Graph-based Orchestration
    · Swarm Collaboration
    · Multi-Agent State and Persistence
    · Agent-to-Agent (A2A) Protocol
  Execution Flow and Result Aggregation
    · Status Tracking

## · Multi-Agent Base and Patterns  (L10295)
  源文件: site/src/content/docs/user-guide/concepts/multi-agent/swarm.mdx, strands-py/src/strands/multiagent/__init__.py, strands-py/src/strands/multiagent/base.py, strands-py/src/strands/multiagent/graph.py, strands-py/src/strands/multiagent/swarm.py, strands-py/tests/strands/agent/hooks/test_hook_registry.py, strands-py/tests/strands/hooks/test_registry.py, strands-py/tests/strands/multiagent/test_base.py, strands-py/tests/strands/multiagent/test_graph.py, strands-py/tests/strands/multiagent/test_swarm.py, strands-py/tests/strands/plugins/test_multiagent_plugin.py, strands-py/tests_integ/test_multiagent_graph.py
  Purpose and Scope
  Overview
  MultiAgentBase Interface
    · Core Methods
  Common Data Structures
    · Status Enum
    · NodeResult
    · MultiAgentResult
  Orchestration Patterns
    · Pattern Comparison
    · Recursive Composition
  Execution Model
    · Invocation Flow
    · Event Streaming
  Result Aggregation
    · Metrics Accumulation
    · Result Flattening

## · Graph-based Orchestration  (L10548)
  源文件: site/src/content/docs/user-guide/concepts/multi-agent/graph.mdx, site/src/content/docs/user-guide/concepts/multi-agent/graph.ts, site/src/content/docs/user-guide/concepts/multi-agent/multi-agent-patterns.mdx, site/src/content/docs/user-guide/concepts/multi-agent/swarm.mdx, site/src/content/docs/user-guide/concepts/tools/index.mdx, site/src/content/docs/user-guide/concepts/tools/tools_imports.ts, site/src/content/docs/user-guide/observability-evaluation/logs.mdx, site/src/content/docs/user-guide/observability-evaluation/metrics.mdx, strands-py/src/strands/multiagent/__init__.py, strands-py/src/strands/multiagent/base.py, strands-py/src/strands/multiagent/graph.py, strands-py/src/strands/multiagent/swarm.py
  Core Architecture
    · Code Entity Relationship Diagram
    · GraphNode (Python)
    · Nodes (TypeScript)
    · GraphEdge (Python)
    · Edges (TypeScript)
    · GraphState (Python)
    · MultiAgentState (TypeScript)
  GraphBuilder API (Python)
    · Building a Graph (Python)
    · Node ID Assignment (Python)
    · Validation Rules (Python)
  Graph Constructor (TypeScript)
    · Building a Graph (TypeScript)
    · Node ID Assignment (TypeScript)
    · Validation Rules (TypeScript)
  Execution Model
    · Graph Execution Sequence
    · Parallel Batch Execution (Python)
    · Parallel Execution (TypeScript)
    · Dependency Resolution (Python)
    · Dependency Resolution (TypeScript)
  Conditional Edges
    · Example: Conditional Routing (Python)
    · Example: Conditional Routing (TypeScript)
  Cyclic Graphs and Reset Behavior
  Interrupt Handling
    · Interrupt State Management (Python)
    · Interrupt State Management (TypeScript)
  Event Streaming

## · Swarm Collaboration  (L11200)
  源文件: site/src/content/docs/user-guide/concepts/multi-agent/swarm.mdx, strands-py/src/strands/multiagent/__init__.py, strands-py/src/strands/multiagent/base.py, strands-py/src/strands/multiagent/graph.py, strands-py/src/strands/multiagent/swarm.py, strands-py/tests/strands/agent/hooks/test_hook_registry.py, strands-py/tests/strands/hooks/test_registry.py, strands-py/tests/strands/multiagent/test_base.py, strands-py/tests/strands/multiagent/test_graph.py, strands-py/tests/strands/multiagent/test_swarm.py, strands-py/tests/strands/plugins/test_multiagent_plugin.py, strands-py/tests_integ/test_multiagent_graph.py
  Swarm Architecture
  Creating a Swarm
    · Basic Initialization
    · Agent Naming Requirements
    · Entry Point Configuration
  Handoff Mechanism
    · Python: Tool Injection
    · Python: Handoff Tool Signature
    · Python: Tool Name Conflicts
    · TypeScript: Structured Output Handoff
    · Handoff Execution Flow
    · Auto-Completion
  Shared Context
    · Python: SharedContext Structure
    · TypeScript: Context Propagation
    · Node Input Construction
  Execution Flow
    · Synchronous vs Asynchronous Execution
    · Execution Loop
    · State Tracking
  Execution Limits and Controls
    · Limit Types
    · Limit Enforcement
    · Node Timeout
    · Repetitive Handoff Detection
  Event Streaming
    · Stream Event Types
    · Event Flow Example
  Swarm vs Graph Comparison
    · Architectural Differences
    · When to Use Each Pattern

## · Multi-Agent State and Persistence  (L11836)
  源文件: .gitignore, AGENTS.md, CONTRIBUTING.md, README.md, package-lock.json, package.json, pyproject.toml, site/src/content/docs/user-guide/concepts/memory/bedrock-knowledge-base.mdx, site/src/content/docs/user-guide/concepts/memory/bedrock-knowledge-base.ts, site/src/content/docs/user-guide/concepts/memory/bedrock-knowledge-base_imports.ts, strandly/package.json, strands-py/pyproject.toml
  Purpose and Scope
  State Structures
    · GraphState
    · SwarmState
  Session Management Implementation
    · RepositorySessionManager
    · Session Data Models
  Multi-Agent Persistence Hooks
  Interrupt and Resume
    · Interrupt State Restoration
    · Multi-Agent Resume Flow
  Implementation Details
    · Binary Data Handling
    · Sync Optimization

## · Agent-to-Agent (A2A) Protocol  (L12044)
  源文件: site/src/content/docs/user-guide/concepts/model-providers/custom_model_provider.mdx, site/src/content/docs/user-guide/concepts/model-providers/openai-responses.mdx, site/src/content/docs/user-guide/concepts/multi-agent/agent-to-agent.mdx, site/src/content/docs/user-guide/concepts/multi-agent/agent-to-agent.ts, strands-py/src/strands/multiagent/a2a/__init__.py, strands-py/src/strands/multiagent/a2a/executor.py, strands-py/src/strands/multiagent/a2a/server.py, strands-py/tests/strands/multiagent/a2a/conftest.py, strands-py/tests/strands/multiagent/a2a/test_executor.py, strands-py/tests/strands/multiagent/a2a/test_server.py
  Architecture Overview
    · Data Flow and Code Entity Mapping
  A2AServer: Exposing Agents
    · Key Components
    · Protocol Converters
  StrandsA2AExecutor
    · Multi-modal Handling
    · Streaming Modes
  A2AAgent: Consuming Remote Agents
    · Card Resolution
    · Usage in Multi-Agent Systems
    · Event Types

## · Telemetry and Observability  (L12200)
  源文件: strands-py/src/strands/memory/extraction/model_extractor.py, strands-py/src/strands/telemetry/tracer.py, strands-py/tests/strands/memory/test_model_extractor.py, strands-py/tests/strands/memory/test_telemetry.py, strands-py/tests/strands/telemetry/test_tracer.py, strands-ts/src/memory/__tests__/memory-tracing.test.ts, strands-ts/src/telemetry/__tests__/meter.test.ts, strands-ts/src/telemetry/__tests__/tracer.test.node.ts, strands-ts/src/telemetry/meter.ts, strands-ts/src/telemetry/tracer.ts
  Purpose and Scope
  Observability Architecture
    · Telemetry Execution Flow
  Core Components
    · Tracer Class
    · Telemetry Configuration
  Span Hierarchy and Lifecycle
    · Span Attributes
    · Span Events
  GenAI Semantic Conventions
    · Convention Versions
  Integration Points
    · Context Propagation
  Custom Trace Attributes
  Multi-Agent Telemetry
  Error Handling and Span Status
  Telemetry Best Practices
    · Non-Invasive Design
    · Structured Data Serialization
  Summary

## · OpenTelemetry Integration  (L12521)
  源文件: strands-py/src/strands/memory/extraction/model_extractor.py, strands-py/src/strands/telemetry/tracer.py, strands-py/tests/strands/memory/test_model_extractor.py, strands-py/tests/strands/memory/test_telemetry.py, strands-py/tests/strands/telemetry/test_tracer.py, strands-ts/src/memory/__tests__/memory-tracing.test.ts, strands-ts/src/telemetry/__tests__/config.test.node.ts, strands-ts/src/telemetry/__tests__/config.test.ts, strands-ts/src/telemetry/__tests__/tracer.test.node.ts, strands-ts/src/telemetry/config.ts, strands-ts/src/telemetry/tracer.ts, strands-ts/src/tools/__tests__/zod-tool.test-d.ts
  Purpose and Scope
  StrandsTelemetry Class Overview
    · Architecture
    · Class Responsibilities
  Initialization
    · Initialization Flow
  Resource Configuration
    · Resource Attributes
  Tracer Initialization and Semantic Conventions
    · Opt-in Semantic Conventions
    · Threading Support
  Trace Exporter Configuration
    · Console Exporter Setup
    · OTLP Exporter Setup
  Metrics Provider Configuration
  Tracer and Global Access
    · Code Entity Mapping
    · Singleton Access
    · JSON Serialization

## · Tracing and Spans  (L12749)
  源文件: strands-py/src/strands/memory/extraction/model_extractor.py, strands-py/src/strands/telemetry/tracer.py, strands-py/tests/strands/memory/test_model_extractor.py, strands-py/tests/strands/memory/test_telemetry.py, strands-py/tests/strands/telemetry/test_tracer.py, strands-ts/src/memory/__tests__/memory-tracing.test.ts, strands-ts/src/telemetry/__tests__/tracer.test.node.ts, strands-ts/src/telemetry/tracer.ts
  Purpose and Scope
  Span Type Hierarchy
    · Span Type Overview
    · Natural Language to Code Entity Space: Execution Flow
  Span Lifecycle
    · Lifecycle Stages
    · Generic Span Creation
    · Generic Span Termination
  Span Types and Methods
    · Agent Span
    · Event Loop Cycle Span
    · Model Invoke Span
    · Tool Call Span
    · Multi-Agent Span
    · Memory Spans
  Span Attributes and Semantic Conventions
    · Semantic Convention Versions
    · Common Attributes
    · Token Usage and Performance
    · Attribute Redaction
  Span Events
    · Content Block Mapping
    · Event Recording
  Tracer Infrastructure
    · Serialization
    · Tracer Singleton

## · Metrics and Performance Monitoring  (L13019)
  源文件: site/src/content/docs/user-guide/concepts/multi-agent/graph.mdx, site/src/content/docs/user-guide/concepts/multi-agent/graph.ts, site/src/content/docs/user-guide/concepts/multi-agent/multi-agent-patterns.mdx, site/src/content/docs/user-guide/concepts/tools/index.mdx, site/src/content/docs/user-guide/concepts/tools/tools_imports.ts, site/src/content/docs/user-guide/observability-evaluation/logs.mdx, site/src/content/docs/user-guide/observability-evaluation/metrics.mdx, strands-ts/src/telemetry/__tests__/meter.test.ts, strands-ts/src/telemetry/meter.ts
  Purpose and Scope
  Core Metrics Architecture
    · Metrics Data Structures
    · Metrics Collection Flow
  Token Usage and Performance Metrics
    · Standard Token Metrics
    · Performance Histograms
  Tool Execution Monitoring
  Metric Integration and Backends
    · OpenTelemetry Integration
    · Tracer and Semantic Conventions
  Programmatic Access to Metrics
    · Using the Trace API (Python)
    · Accessing Aggregated Results
  Summary of Metric Constants

## · Experimental Features  (L13330)
  源文件: strands-py/src/strands/experimental/bidi/_telemetry.py, strands-py/src/strands/experimental/bidi/agent/loop.py, strands-py/src/strands/experimental/bidi/models/gemini_live.py, strands-py/src/strands/experimental/bidi/models/nova_sonic.py, strands-py/src/strands/experimental/bidi/models/openai_realtime.py, strands-py/src/strands/models/_validation.py, strands-py/src/strands/types/_snapshot.py, strands-py/tests/strands/agent/test_snapshot.py, strands-py/tests/strands/experimental/bidi/agent/test_agent.py, strands-py/tests/strands/experimental/bidi/agent/test_loop.py, strands-py/tests/strands/experimental/bidi/agent/test_loop_telemetry.py, strands-py/tests/strands/experimental/bidi/models/test_gemini_live.py
  Overview of Experimental Subsystems
    · High-Level Component Interaction
  Bidirectional Streaming Agent
  Bidirectional Model Providers
    · Supported Experimental Models
  Checkpoint System
    · Checkpoint Positions
  Agent Configuration Utilities

## · Bidirectional Streaming Agent  (L13494)
  源文件: site/src/content/docs/user-guide/concepts/bidirectional-streaming/agent.mdx, site/src/content/docs/user-guide/concepts/bidirectional-streaming/events.mdx, site/src/content/docs/user-guide/concepts/bidirectional-streaming/models/nova_sonic.mdx, site/src/content/docs/user-guide/concepts/bidirectional-streaming/quickstart.mdx, site/src/content/docs/user-guide/concepts/bidirectional-streaming/session-management.mdx, strands-py/src/strands/experimental/bidi/__init__.py, strands-py/src/strands/experimental/bidi/_telemetry.py, strands-py/src/strands/experimental/bidi/agent/loop.py, strands-py/src/strands/experimental/bidi/models/gemini_live.py, strands-py/src/strands/experimental/bidi/models/openai_realtime.py, strands-py/src/strands/experimental/bidi/types/events.py, strands-py/src/strands/experimental/bidi/types/model.py
  Architecture and Task Management
    · Async Task Group Design
    · Data Flow: Natural Language to Code Entities
  Key Components
    · BidiAgent Class
    · BidiModel Protocol
  Event Loop and Interruption Handling
    · Connection Restarts
    · Interruption Logic
    · Graceful Shutdown
  Protocols: BidiInput and BidiOutput
    · Built-in I/O Implementations
    · Deprecated Tools
  Telemetry Integration
    · Session Spans
    · Connection Spans
    · Response Spans
    · Restart Spans
    · Interruption Events

## · Bidirectional Model Providers  (L13699)
  源文件: strands-py/src/strands/experimental/bidi/_telemetry.py, strands-py/src/strands/experimental/bidi/agent/loop.py, strands-py/src/strands/experimental/bidi/models/gemini_live.py, strands-py/src/strands/experimental/bidi/models/nova_sonic.py, strands-py/src/strands/experimental/bidi/models/openai_realtime.py, strands-py/src/strands/models/_validation.py, strands-py/src/strands/types/_snapshot.py, strands-py/tests/strands/agent/test_snapshot.py, strands-py/tests/strands/experimental/bidi/agent/test_agent.py, strands-py/tests/strands/experimental/bidi/agent/test_loop.py, strands-py/tests/strands/experimental/bidi/agent/test_loop_telemetry.py, strands-py/tests/strands/experimental/bidi/models/test_gemini_live.py
  The BidiModel Interface
  Provider Implementations
    · BidiNovaSonicModel
    · BidiOpenAIRealtimeModel
    · BidiGeminiLiveModel
  Audio and Text I/O Adapters
    · BidiTextIO
    · BidiAudioIO
  Data Flow and Tool Execution
    · Tool Interaction
  Async Management: _TaskGroup

## · Checkpoint System  (L13873)
  源文件: site/src/content/docs/user-guide/concepts/agents/prompts.mdx, site/src/content/docs/user-guide/concepts/agents/retry-strategies.mdx, site/src/content/docs/user-guide/concepts/agents/snapshots.mdx, site/src/content/docs/user-guide/concepts/agents/state.mdx, site/src/content/docs/user-guide/concepts/agents/structured-output.mdx, site/src/content/docs/user-guide/concepts/model-providers/google.mdx, site/src/content/docs/user-guide/concepts/multi-agent/agents-as-tools.mdx, site/src/content/docs/user-guide/safety-security/trusted-message-history.mdx, strands-py/src/strands/event_loop/_retry.py, strands-py/tests/strands/agent/test_agent_retry.py, strands-py/tests/strands/agent/test_retry.py, strands-ts/src/agent/__tests__/agent.checkpoint.test.ts
  Core Concepts
    · Checkpoint Positions
    · Data Flow and Resume Pattern
  Implementation Details
    · The Checkpoint Class
    · Logical Execution Flow
  Resilience and Limitations
    · Mapping Code Entities to System Space

## · Development and Contributing  (L14014)
  源文件: .github/workflows/ci.yml, .github/workflows/mcp-pr-and-push.yml, .github/workflows/mcp-security-audit.yml, .github/workflows/mcp-test-lint.yml, .github/workflows/mcp-test-package-build.yml, .github/workflows/pr-metrics-analyze.yml, .github/workflows/pr-metrics-label.yml, .github/workflows/pr-title.yml, .github/workflows/python-check-markdown-links.yml, .github/workflows/python-integration-test.yml, .github/workflows/python-pr-and-push.yml, .github/workflows/python-publish-lambda-layer.yml
  Overview
  Development Workflow
  Quality Gates and Standards
    · Code Quality Standards
  Pre-commit Hooks
  CI/CD Architecture
  Test Infrastructure
    · Test Matrix and Metrics
  Security and Authorization
    · Pull Request Security Model
  Contributing Guidelines

## · Development Environment Setup  (L14247)
  源文件: .agents/references/code-verification.md, .agents/skills/docs-planner/SKILL.md, .agents/skills/strands-review/SKILL.md, .github/workflows/ci.yml, .github/workflows/mcp-pr-and-push.yml, .github/workflows/pr-title.yml, .github/workflows/python-check-markdown-links.yml, .github/workflows/python-pr-and-push.yml, site/docs/examples/cdk/deploy_to_apprunner/package-lock.json, site/docs/examples/cdk/deploy_to_apprunner/package.json, site/docs/examples/cdk/deploy_to_ec2/package-lock.json, site/docs/examples/cdk/deploy_to_ec2/package.json
  Purpose and Scope
  Python Version Requirements
  Development Environment Architecture
    · Environment-to-Code Mapping
  Initial Setup
    · 1. Clone Repository and Install Dependencies
    · 2. Install Pre-Commit Hooks
  Python Development with Hatch
    · Environment Definitions
    · Development Commands
  TypeScript Development with npm Workspaces and `strandly` CLI
    · npm Workspaces
    · `strandly` CLI Tool
  Pre-Commit Hook Configuration
  Local Development Workflow
    · Contributor Flow Diagram
  AI-Assisted Development Guidelines
    · `AGENTS.md` - General Guidelines
    · `CLAUDE.md` - Claude-Specific Guidelines

## · Testing Infrastructure  (L14592)
  源文件: .github/workflows/mcp-security-audit.yml, .github/workflows/mcp-test-lint.yml, .github/workflows/mcp-test-package-build.yml, .github/workflows/pr-metrics-analyze.yml, .github/workflows/pr-metrics-label.yml, .github/workflows/python-integration-test.yml, .github/workflows/python-publish-lambda-layer.yml, .github/workflows/python-security-audit.yml, .github/workflows/python-test-lint.yml, .github/workflows/python-test-package-build.yml, .github/workflows/release-mcp.yml, .github/workflows/release-python.yml
  Purpose and Scope
  Testing Philosophy and Structure
  Test Environment Architecture
    · Build and Telemetry Flow
  Unit Testing and Mocking
    · Python Unit Testing
    · Python Async and Warning Utilities
    · TypeScript Unit Testing
  Integration Testing Infrastructure
    · Flaky Test Management
    · Integration Entity Mapping
    · Test Infrastructure CDK Stack (`test-infra/`)
  CI/CD and Coverage Requirements
    · Automated Test Execution
    · Coverage and Metrics
  Test Execution Commands

## · CI/CD Pipeline  (L14866)
  源文件: .github/ISSUE_TEMPLATE/bug_report.yml, .github/ISSUE_TEMPLATE/config.yml, .github/ISSUE_TEMPLATE/content_addition.yml, .github/ISSUE_TEMPLATE/documentation_improvement.yml, .github/ISSUE_TEMPLATE/documentation_question.yml, .github/ISSUE_TEMPLATE/feature_request.yml, .github/ISSUE_TEMPLATE/technical_correction.yml, .github/PULL_REQUEST_TEMPLATE.md, .github/dependabot.yml, .github/labelers/area.yml, .github/labelers/language.yml, .github/labelers/type.yml
  Purpose and Scope
  CI/CD Architecture
    · System Workflow Diagram
    · Workflow Trigger Matrix
  Quality Gates
    · Python Unit Testing
    · Python Linting and Type Checking
    · Python API Breaking Change Detection
    · Python Integration Testing
    · Python Security Audit (pip-audit)
    · TypeScript Unit Testing
    · TypeScript Type Checking
    · TypeScript Integration Testing
    · TypeScript Security Audit (npm audit)
    · MCP Unit Testing
    · MCP Linting
    · MCP Security Audit (pip-audit)
  Strands AI Automation
    · Command Handler
    · Auto Strands Review
  Release Pipeline
    · Release Workflow Overview
    · Scan Commits and Validate Version
    · Build Package Artifacts
    · Inspect Artifacts
    · Manual Approval and Publication
    · AWS Lambda Layer Publication
  PR Metrics (Size/Complexity Labels)
    · PR Metrics Labeling Workflow
  Documentation Site CI/CD
    · Docs Deploy Preview
    · Changelog Sync

## · Team Governance and Design Process  (L15604)
  源文件: .agents/skills/README.md, .agents/skills/pr-create/SKILL.md, .agents/skills/pr-feedback/SKILL.md, .agents/skills/pr-feedback/fetch-pr-feedback.sh, .agents/skills/pr-writer/SKILL.md, .agents/skills/pr-writer/get-diff.sh, .agents/skills/pre-push/SKILL.md, .agents/skills/pre-push/run-checks.sh, .github/workflows/api-review-label.yml, team/AGENT_GUIDELINES.md, team/API_BAR_RAISING.md, team/COMPLEXITY.md
  Development Tenets
  API Bar-Raising Process
    · Roles
    · Timeline and Scope of Review
    · Process Details
    · API Bar-Raising Workflow
  Feature Lifecycle
    · Compatibility Guarantees
  Cognitive Complexity Thresholds
    · How the Score Works
    · Strategies for Managing Complexity
    · Complexity in PRs
    · When High Complexity is Acceptable
    · Checking Complexity Locally
  Designs and RFC Process
    · Decision Records
    · Agent Guidelines

## · Documentation Site  (L15869)
  源文件: .agents/references/mdx-authoring.md, site/AGENTS.md, site/package-lock.json, site/package.json, site/scripts/api-generation-python.py, site/src/components/overrides/MarkdownContent.astro, site/src/config/navigation.yml, site/src/content.config.ts, site/src/content/catalog/strands-github-storage.yaml, site/src/content/docs/contribute/contributing/extensions.mdx, site/src/content/docs/integrations/storage/github.mdx, site/src/plugins/remark-mkdocs-snippets.ts
  Site Overview
    · Key Features
    · Site Structure
  Site Architecture and Navigation
    · Astro/Starlight Structure
    · Navigation
    · Content Collections and Schemas
    · Language Faceting
    · MarkdownContent.astro Override
  Content Authoring and Code Snippets
    · MDX Authoring Conventions
    · Code Snippet Inclusion
    · Integration Catalog
    · Changelog Sync Pipeline
  API Documentation Generation
    · Automated Generation Process
    · Build Integration
    · API Doc Generation Workflow

## · Site Architecture and Navigation  (L16064)
  源文件: .agents/references/mdx-authoring.md, site/AGENTS.md, site/SITE-ARCHITECTURE.md, site/astro.config.mjs, site/src/components/LanguageToggle.astro, site/src/components/Syntax.astro, site/src/components/landing/AgentSetupCard.astro, site/src/components/landing/CodeBlock.astro, site/src/components/landing/HeroSection.astro, site/src/components/landing/LangCodeBlock.astro, site/src/components/overrides/MarkdownContent.astro, site/src/config/changelog.ts
  Astro/Starlight Site Structure
  Navigation Management with `navigation.yml`
  Content Collections and Zod Schemas
    · `docs` Collection
    · `catalog` Collection
    · `changelog` Collection
    · `blog` and `authors` Collections
  Language Faceting System
  `MarkdownContent.astro` Override and Contextual Banners

## · Content Authoring and Code Snippets  (L16313)
  源文件: .agents/references/mdx-authoring.md, site/AGENTS.md, site/scripts/changelog/build-release-file.ts, site/scripts/changelog/derive-entries.ts, site/scripts/changelog/enrich.ts, site/scripts/changelog/github-client.ts, site/scripts/changelog/parse-release-body.ts, site/scripts/changelog/render-markdown.ts, site/scripts/changelog/run.ts, site/scripts/changelog/sync.ts, site/src/components/overrides/MarkdownContent.astro, site/src/config/navigation.yml
  MDX Authoring Conventions
    · Auto-Imported Components: `Tabs`, `Tab`, and `Syntax`
    · Callout Syntax
    · Frontmatter Schema
  Code Snippet Inclusion with `remark-mkdocs-snippets`
    · `--8<--` Directive
    · Dedenting and Markers
    · TypeScript Snippet Scoping
  Integration Catalog YAML Format
  Changelog Sync Pipeline
    · Pipeline Overview
    · Data Flow
    · Monorepo Stream Filtering

## · API Documentation Generation  (L16604)
  源文件: site/package-lock.json, site/package.json, site/scripts/api-generation-python.py, site/src/plugins/vite-plugin-sdk-setup.ts, site/src/util/api-counterparts.ts, site/src/util/github.ts, site/src/util/language-switch.ts, site/test-snippets/package.json, site/test/api-counterparts.test.ts, site/test/language-switch.test.ts, site/typedoc-tsconfig.json
  Overview of the Generation Pipeline
  Python API Documentation with pydoc-markdown
    · Key Components and Configuration
    · Python API Doc Generation Flow
  TypeScript API Documentation with Typedoc
    · Typedoc Configuration
  Automation and Integration
    · `vite-plugin-sdk-setup`
    · npm Scripts
    · API Counterpart Mapping
    · API Documentation Generation Pipeline

## · Glossary  (L16910)
  源文件: .agents/references/mdx-authoring.md, .gitignore, AGENTS.md, CONTRIBUTING.md, README.md, package-lock.json, package.json, pyproject.toml, site/AGENTS.md, site/src/components/overrides/MarkdownContent.astro, site/src/config/navigation.yml, site/src/content.config.ts
  Core Concepts
    · Agent
    · Model (Model Provider)
    · Tool / AgentTool
    · Event Loop
  Technical Terms & Jargon
  Data Flow & Architecture Diagrams
    · From Natural Language to Code Execution
    · Multi-Agent Orchestration Space
  Domain Concepts
    · Tool Context (`ToolContext`)
    · Interrupts
    · Telemetry (OpenTelemetry)