# Skeleton: agentscope（58 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 12KB | 3 | ~6 | 10 |
| 2 | Installation and Setup | L333 | 9KB | 2 | ~2 | 16 |
| 3 | Core Concepts and Architecture | L573 | 12KB | 3 | ~4 | 13 |
| 4 | Agent System | L839 | 15KB | 3 | ~2 | 22 |
| 5 | AgentBase Foundation | L1200 | 12KB | 5 | ~7 | 4 |
| 6 | ReActAgent Implementation | L1523 | 23KB | 6 | ~13 | 13 |
| 7 | Agent Lifecycle and Hooks | L2096 | 10KB | 4 | ~5 | 12 |
| 8 | Message Protocol and Content Blocks | L2324 | 8KB | 3 | ~14 | 4 |
| 9 | Planning System with PlanNotebook | L2541 | 14KB | 6 | ~3 | 13 |
| 10 | Realtime and UserAgent | L2902 | 8KB | 2 | ~4 | 17 |
| 11 | Model Integration | L3057 | 10KB | 2 | ~1 | 12 |
| 12 | ChatModelBase and Provider Architecture | L3289 | 7KB | 2 | ~5 | 8 |
| 13 | DashScope Integration | L3463 | 12KB | 4 | ~5 | 12 |
| 14 | OpenAI and Compatible APIs | L3773 | 11KB | 2 | ~7 | 12 |
| 15 | Gemini Integration | L4014 | 13KB | 3 | ~4 | 6 |
| 16 | Anthropic and Other Providers | L4338 | 8KB | 3 | ~4 | 17 |
| 17 | Message Formatters | L4527 | 13KB | 4 | ~4 | 22 |
| 18 | Streaming and Response Handling | L4792 | 12KB | 3 | ~4 | 15 |
| 19 | Structured Output and Tool Calling | L5064 | 11KB | 2 | ~6 | 18 |
| 20 | Realtime and TTS Models | L5322 | 9KB | 2 | ~4 | 19 |
| 21 | Embedding Models | L5498 | 8KB | 3 | ~2 | 3 |
| 22 | Tool System | L5665 | 16KB | 7 | ~3 | 13 |
| 23 | Toolkit Core Architecture | L6089 | 11KB | 3 | ~4 | 7 |
| 24 | Tool Registration and Execution | L6377 | 8KB | 2 | ~1 | 14 |
| 25 | Tool Groups and Meta-Tools | L6565 | 10KB | 5 | ~2 | 13 |
| 26 | MCP Integration | L6824 | 9KB | 3 | ~3 | 13 |
| 27 | Built-in Tools and Agent Skills | L6998 | 13KB | 2 | ~1 | 14 |
| 28 | Middleware System | L7325 | 11KB | 4 | ~5 | 4 |
| 29 | Memory and Knowledge Systems | L7678 | 15KB | 7 | ~6 | 9 |
| 30 | Working Memory Architecture | L8059 | 10KB | 4 | ~6 | 9 |
| 31 | Memory Compression | L8296 | 12KB | 4 | ~8 | 14 |
| 32 | Redis Memory and Multi-Tenancy | L8557 | 9KB | 3 | ~2 | 7 |
| 33 | Session State Management | L8734 | 11KB | 3 | ~4 | 12 |
| 34 | Long-Term Memory with Mem0 | L9019 | 18KB | 9 | ~6 | 9 |
| 35 | Long-Term Memory with ReME | L9552 | 10KB | 2 | ~1 | 11 |
| 36 | Long-Term Memory Integration | L9740 | 9KB | 3 | ~1 | 16 |
| 37 | RAG System Overview | L9956 | 13KB | 4 | ~5 | 25 |
| 38 | Vector Store Integrations | L10313 | 10KB | 3 | ~4 | 17 |
| 39 | Multi-Agent Orchestration | L10555 | 14KB | 6 | ~5 | 6 |
| 40 | MsgHub Communication | L10919 | 9KB | 2 | ~8 | 7 |
| 41 | Pipeline Patterns | L11149 | 9KB | 4 | ~1 | 13 |
| 42 | Subscriber Broadcasting | L11388 | 13KB | 4 | ~7 | 6 |
| 43 | Observability and Evaluation | L11740 | 6KB | 3 | ~3 | 9 |
| 44 | OpenTelemetry Integration | L11912 | 7KB | 2 | ~1 | 8 |
| 45 | Tracing Decorators and Usage | L12139 | 9KB | 3 | ~2 | 11 |
| 46 | Evaluation Framework | L12345 | 11KB | 4 | ~2 | 17 |
| 47 | OpenJudge Integration | L12596 | 18KB | 7 | ~6 | 4 |
| 48 | Production and Deployment | L13080 | 7KB | 2 | ~2 | 15 |
| 49 | State Serialization and Checkpointing | L13242 | 11KB | 4 | ~3 | 12 |
| 50 | Package Structure and Dependencies | L13530 | 8KB | 2 | ~8 | 15 |
| 51 | Production Deployment Patterns | L13737 | 9KB | 5 | ~4 | 12 |
| 52 | Advanced Topics | L13928 | 8KB | 4 | ~5 | 5 |
| 53 | Multimodal Agents | L14133 | 8KB | 2 | ~3 | 10 |
| 54 | Human-in-the-Loop and Interruption | L14306 | 7KB | 3 | ~2 | 9 |
| 55 | Extending AgentScope | L14480 | 11KB | 5 | ~6 | 14 |
| 56 | Agent Communication Protocols | L14820 | 8KB | 2 | ~1 | 7 |
| 57 | Agentic RL and Tuner | L14998 | 10KB | 2 | ~2 | 21 |
| 58 | Glossary | L15184 | 10KB | 2 | ~3 | 38 |


## · Overview  (L6)
  源文件: .github/workflows/unittest.yml, README.md, README_zh.md, assets/images/agentscope.png, docs/tutorial/en/src/task_tracing.py, docs/tutorial/zh_CN/src/task_tracing.py, src/agentscope/__init__.py, src/agentscope/_run_config.py, src/agentscope/model/_model_base.py, tests/config_test.py
  What is AgentScope?
  Design Philosophy
  System Initialization
    · Initialization and Observability Flow
  High-Level Architecture
    · Architecture Overview
  Major Subsystems
    · Core Components Detail
  Message Protocol
    · Message Structure
  Extensibility Points
  Getting Started
    · Quick Start Example
  Community and Resources

## · Installation and Setup  (L333)
  源文件: .github/workflows/unittest.yml, .pre-commit-config.yaml, examples/agent/voice_agent/README.md, examples/functionality/vector_store/oceanbase/README.md, examples/functionality/vector_store/oceanbase/main.py, pyproject.toml, src/agentscope/__init__.py, src/agentscope/_run_config.py, src/agentscope/model/_model_base.py, src/agentscope/model/_model_response.py, src/agentscope/rag/__init__.py, src/agentscope/rag/_store/__init__.py
  Prerequisites
  Installation Methods
    · Standard Installation via PyPI
    · Installation from Source
  Optional Dependencies
    · Dependency Architecture
    · Common Installation Commands
  Framework Initialization
    · The init() Function
    · Data Flow during Initialization
  Observability and Tracing Setup
    · Tracing Backends
    · Tracing Implementation
  Verification and Testing
    · Sanity Check
    · Running Unit Tests

## · Core Concepts and Architecture  (L573)
  源文件: README.md, README_zh.md, assets/images/agentscope.png, docs/tutorial/en/src/task_tracing.py, docs/tutorial/zh_CN/src/task_tracing.py, examples/game/werewolves/structured_model.py, src/agentscope/agent/_agent_base.py, src/agentscope/message/_message_base.py, src/agentscope/message/_message_block.py, src/agentscope/pipeline/__init__.py, src/agentscope/pipeline/_functional.py, tests/formatter_a2a_test.py
  Core Building Blocks
    · Agents
    · Models
    · Messages
    · Tools
    · Memory
  Component Interaction Architecture
  Message Flow Through Pipelines
  Architecture Layers
  Key Architectural Patterns
    · Lifecycle Hooks
    · Publish-Subscribe Communication
    · State Management
    · Observability

## · Agent System  (L839)
  源文件: src/agentscope/_utils/_common.py, src/agentscope/agent/_agent_base.py, src/agentscope/agent/_react_agent.py, src/agentscope/model/_anthropic_model.py, src/agentscope/model/_dashscope_model.py, src/agentscope/model/_gemini_model.py, src/agentscope/model/_model_usage.py, src/agentscope/model/_ollama_model.py, src/agentscope/model/_openai_model.py, src/agentscope/pipeline/__init__.py, src/agentscope/pipeline/_functional.py, tests/model_anthropic_test.py
  Overview
  System Architecture
  Agent Types
    · AgentBase
    · ReActAgent
  Agent Lifecycle
    · Phase 1: Entry Point (`__call__`)
    · Phase 2: Pre-Processing
    · Phase 3: Reasoning-Acting Loop
    · Phase 4: Post-Processing
    · Phase 5: Exception Handling
  Message Protocol
  Multi-Agent Communication

## · AgentBase Foundation  (L1200)
  源文件: src/agentscope/agent/_agent_base.py, src/agentscope/pipeline/__init__.py, src/agentscope/pipeline/_functional.py, tests/pipeline_test.py
  Class Architecture
    · Inheritance Hierarchy
    · Key Attributes
  Core Abstract Methods
    · reply Method
    · observe Method
    · handle_interrupt Method
  Hook System
    · Hook Architecture
    · Hook Management
  Subscriber Mechanism
    · Subscriber Data Structure
    · Broadcasting Flow
  Message Printing System
    · print Method
    · Streaming Cache
  Interrupt Handling
    · interrupt Method
    · Lifecycle of an Interruption
  Integration with Pipeline System
    · Functional Pipelines
    · Stream Printing

## · ReActAgent Implementation  (L1523)
  源文件: src/agentscope/_utils/_common.py, src/agentscope/agent/_react_agent.py, src/agentscope/model/_anthropic_model.py, src/agentscope/model/_dashscope_model.py, src/agentscope/model/_gemini_model.py, src/agentscope/model/_model_usage.py, src/agentscope/model/_ollama_model.py, src/agentscope/model/_openai_model.py, tests/model_anthropic_test.py, tests/model_dashscope_test.py, tests/model_ollama_test.py, tests/model_openai_test.py
  Class Overview and Dependencies
  Initialization Parameters
    · Core Parameters
    · Tool and Memory Parameters
    · Long-Term Memory Parameters
    · Knowledge and Planning Parameters
    · Execution Control Parameters
    · Output and Compression Parameters
  CompressionConfig Structure
    · Configuration Fields
    · Default SummarySchema
  Reasoning-Acting Loop Architecture
    · Loop Execution Flow
  Reasoning Phase Implementation
    · Key Operations
  Acting Phase Implementation
    · Execution Details
  Memory Compression System
    · Compression Algorithm
  Structured Output Generation
    · Implementation Flow
  Knowledge Retrieval Integration
    · Retrieval Process
  State Management
    · Registered State Variables
    · Dynamic sys_prompt Property

## · Agent Lifecycle and Hooks  (L2096)
  源文件: docs/tutorial/en/src/task_embedding.py, docs/tutorial/en/src/task_rag.py, docs/tutorial/zh_CN/src/task_embedding.py, docs/tutorial/zh_CN/src/task_rag.py, examples/functionality/rag/README.md, examples/functionality/rag/agentic_usage.py, examples/functionality/rag/basic_usage.py, src/agentscope/agent/_agent_base.py, src/agentscope/hooks/_studio_hooks.py, src/agentscope/pipeline/__init__.py, src/agentscope/pipeline/_functional.py, tests/pipeline_test.py
  Agent Invocation Pipeline
    · Basic Execution Flow
    · Agent State During Execution
  Hook System Architecture
    · Supported Hook Types
    · Hook Execution Order
    · Studio Integration via Hooks
  ReActAgent Reply Lifecycle
    · Complete Reply Flow
    · Reasoning Phase (`_reasoning`)
    · Acting Phase (`_acting`)
  Interrupt Handling
    · Interrupt Mechanism
  Pipeline Execution Flow
    · Stream Printing Messages

## · Message Protocol and Content Blocks  (L2324)
  源文件: examples/game/werewolves/structured_model.py, src/agentscope/message/_message_base.py, src/agentscope/message/_message_block.py, tests/formatter_a2a_test.py
  Overview
  Content Block Type System
  Text and Thinking Blocks
    · TextBlock
    · ThinkingBlock
  Media Source Types
    · Base64Source
    · URLSource
  Multimodal Content Blocks
    · ImageBlock, AudioBlock, and VideoBlock
  Tool Interaction Blocks
    · ToolUseBlock
    · ToolResultBlock
  The Msg Object
  Response Parsing Architecture

## · Planning System with PlanNotebook  (L2541)
  源文件: docs/tutorial/_static/images/plan.png, docs/tutorial/en/src/quickstart_agent.py, docs/tutorial/en/src/task_plan.py, docs/tutorial/zh_CN/src/quickstart_agent.py, docs/tutorial/zh_CN/src/task_plan.py, examples/functionality/plan/README.md, examples/functionality/plan/main_agent_managed_plan.py, src/agentscope/plan/_in_memory_storage.py, src/agentscope/plan/_plan_model.py, src/agentscope/plan/_plan_notebook.py, tests/plan_test.py, tests/toolkit_basic_test.py
  Purpose and Scope
  Core Concepts
    · Plan and SubTask Models
  Architecture Overview
  PlanNotebook Class
    · Initialization Parameters
    · Tool Functions Interface
  Plan and SubTask State Transitions
    · SubTask State Machine
    · Plan State Management
  Tool Functions in Detail
    · Plan Creation and Revision
    · Subtask State Management
  Hint Generation System
    · DefaultPlanToHint
  State Serialization
  Plan Change Hooks

## · Realtime and UserAgent  (L2902)
  源文件: docs/tutorial/en/build.sh, docs/tutorial/en/src/task_realtime.py, docs/tutorial/zh_CN/build.sh, docs/tutorial/zh_CN/src/task_realtime.py, examples/agent/realtime_voice_agent/README.md, examples/agent/realtime_voice_agent/chatbot.html, examples/deployment/README.md, examples/deployment/planning_agent/README.md, examples/deployment/planning_agent/main.py, examples/deployment/planning_agent/test_post.py, src/agentscope/agent/_user_input.py, src/agentscope/realtime/_dashscope_realtime_model.py
  Realtime Interaction System
    · RealtimeAgent Lifecycle and Data Flow
    · Realtime Models and Protocols
    · Event Protocols
  UserAgent and Human-in-the-Loop
    · Implementation and Behavior
    · Key Functions
  Comparison: Realtime vs. UserAgent

## · Model Integration  (L3057)
  源文件: src/agentscope/_utils/_common.py, src/agentscope/agent/_react_agent.py, src/agentscope/model/_anthropic_model.py, src/agentscope/model/_dashscope_model.py, src/agentscope/model/_gemini_model.py, src/agentscope/model/_model_usage.py, src/agentscope/model/_ollama_model.py, src/agentscope/model/_openai_model.py, tests/model_anthropic_test.py, tests/model_dashscope_test.py, tests/model_ollama_test.py, tests/model_openai_test.py
  Purpose and Scope
  Architecture Overview
    · Core Model Hierarchy
    · ChatModelBase Interface
  Provider Implementations
    · DashScope Integration
    · OpenAI and Compatible APIs
    · Gemini Integration
    · Anthropic and Other Providers
  Response and Message Structures
    · ChatResponse and Content Blocks
    · Streaming and Response Handling
  Specialized Model Types
    · Structured Output and Tool Calling
    · Realtime, TTS, and Embedding Models

## · ChatModelBase and Provider Architecture  (L3289)
  源文件: .github/workflows/unittest.yml, .pre-commit-config.yaml, examples/agent/voice_agent/README.md, src/agentscope/__init__.py, src/agentscope/_run_config.py, src/agentscope/model/_model_base.py, src/agentscope/model/_model_response.py, tests/config_test.py
  Overview
  ChatModelBase Abstract Interface
    · Core Methods
    · Standard Parameters
  Provider Implementation Pattern
    · Initialization Pattern
  Response and Usage Objects
    · ChatResponse
    · ChatUsage
  Observability Integration
  Content Block Types

## · DashScope Integration  (L3463)
  源文件: src/agentscope/_utils/_common.py, src/agentscope/agent/_react_agent.py, src/agentscope/model/_anthropic_model.py, src/agentscope/model/_dashscope_model.py, src/agentscope/model/_gemini_model.py, src/agentscope/model/_model_usage.py, src/agentscope/model/_ollama_model.py, src/agentscope/model/_openai_model.py, tests/model_anthropic_test.py, tests/model_dashscope_test.py, tests/model_ollama_test.py, tests/model_openai_test.py
  Overview and Architecture
    · System Architecture Diagram
  API Selection Logic
    · Selection Flow
  Constructor Parameters
    · Parameter Reference Table
    · Thinking Mode Enforcement
    · Custom Headers Configuration
  Core API Method
    · Request Preparation Flow
    · Tool Choice Conversion
    · Structured Output Override
  Streaming Response Processing
    · Streaming Architecture
    · Stream Tool Parsing
  Thinking and Reasoning Mode
    · Thinking Content Extraction
  Usage Tracking
    · Usage Extraction

## · OpenAI and Compatible APIs  (L3773)
  源文件: src/agentscope/_utils/_common.py, src/agentscope/agent/_react_agent.py, src/agentscope/model/_anthropic_model.py, src/agentscope/model/_dashscope_model.py, src/agentscope/model/_gemini_model.py, src/agentscope/model/_model_usage.py, src/agentscope/model/_ollama_model.py, src/agentscope/model/_openai_model.py, tests/model_anthropic_test.py, tests/model_dashscope_test.py, tests/model_ollama_test.py, tests/model_openai_test.py
  Overview
  OpenAIChatModel Initialization
    · Basic Parameters
    · Client Type Architecture
    · Reasoning Effort Configuration
  Compatible API Support
    · vLLM and Ollama Integration
    · DeepSeek Integration
    · Qwen-omni Audio Format
  API Call Flow
    · Request Pipeline
  Response Parsing
    · Streaming and Tool Parsing
    · Structured Output Support
  Usage with Other Providers
    · OllamaChatModel
    · DashScope Integration (Compatibility Note)

## · Gemini Integration  (L4014)
  源文件: src/agentscope/formatter/_gemini_formatter.py, tests/formatter_anthropic_test.py, tests/formatter_deepseek_test.py, tests/formatter_gemini_test.py, tests/formatter_ollama_test.py, tests/model_gemini_test.py
  Overview
  GeminiChatModel Architecture
  Initialization and Configuration
    · Basic Initialization
    · Configuration Parameters
    · Thinking Configuration
  Message Formatting System
    · GeminiChatFormatter
    · GeminiMultiAgentFormatter
  Content Block Formatting
    · Text Blocks
    · Tool Use Blocks
    · Tool Result Blocks
  Multimodal Content Handling
    · Supported Media Types
    · Media Processing Pipeline
  Tool Integration
    · JSON Schema Flattening
    · Tool Choice Configuration
  Response Parsing
    · Non-Streaming Responses
    · Streaming Responses

## · Anthropic and Other Providers  (L4338)
  源文件: src/agentscope/_utils/_common.py, src/agentscope/agent/_react_agent.py, src/agentscope/formatter/_anthropic_formatter.py, src/agentscope/formatter/_deepseek_formatter.py, src/agentscope/formatter/_ollama_formatter.py, src/agentscope/formatter/_openai_formatter.py, src/agentscope/model/_anthropic_model.py, src/agentscope/model/_dashscope_model.py, src/agentscope/model/_gemini_model.py, src/agentscope/model/_model_usage.py, src/agentscope/model/_ollama_model.py, src/agentscope/model/_openai_model.py
  AnthropicChatModel Architecture
    · Anthropic Initialization and Data Flow
    · Initialization Parameters
  DashScope Integration (Qwen & DeepSeek)
    · Thinking Mode in DashScope
  Google Gemini Integration
    · Schema Flattening
  Ollama and Local Models
    · Configuration Parameters
  Message Blocks and Content Types
  Response Handling and Tool Parsing
    · Model Usage Tracking

## · Message Formatters  (L4527)
  源文件: .gitignore, docs/tutorial/en/src/task_prompt.py, docs/tutorial/zh_CN/src/task_prompt.py, src/agentscope/formatter/_anthropic_formatter.py, src/agentscope/formatter/_dashscope_formatter.py, src/agentscope/formatter/_deepseek_formatter.py, src/agentscope/formatter/_formatter_base.py, src/agentscope/formatter/_gemini_formatter.py, src/agentscope/formatter/_ollama_formatter.py, src/agentscope/formatter/_openai_formatter.py, src/agentscope/mcp/_client_base.py, src/agentscope/memory/_long_term_memory/_long_term_memory_base.py
  Purpose and Scope
  Formatter Architecture
    · Formatter Hierarchy and File Locations
    · Base Class Responsibilities
  Formatter Patterns: Chat vs. Multi-Agent
    · ChatFormatter: User-Assistant Scenario
    · MultiAgentFormatter: Multi-Agent Scenario
  Provider Support Matrix
  ReAct-Oriented Formatting Logic
    · Message Sequence Processing
  Token Truncation and FIFO Strategy
    · Truncation Flow
    · Key Parameters
  Provider-Specific Implementations
    · OpenAI Formatter
    · DashScope Formatter
    · Gemini Formatter
  Implementation Details: Multi-Part Text Consolidation

## · Streaming and Response Handling  (L4792)
  源文件: .pre-commit-config.yaml, examples/agent/voice_agent/README.md, src/agentscope/_utils/_common.py, src/agentscope/agent/_react_agent.py, src/agentscope/model/_anthropic_model.py, src/agentscope/model/_dashscope_model.py, src/agentscope/model/_gemini_model.py, src/agentscope/model/_model_response.py, src/agentscope/model/_model_usage.py, src/agentscope/model/_ollama_model.py, src/agentscope/model/_openai_model.py, tests/model_anthropic_test.py
  Overview
  Streaming vs Non-Streaming Execution
    · Execution Mode Selection
    · Return Type Signatures
  ChatResponse Structure
    · Response Object Components
    · ChatUsage Structure
  Stream Tool Parsing
    · Incremental JSON Repair Mechanism
  Provider-Specific Streaming Implementation
    · DashScope Streaming
    · OpenAI Streaming
    · Gemini Streaming
    · Anthropic Streaming
    · Ollama Streaming
  Content Block Accumulation
  Best Practices
    · Consuming Streaming Responses

## · Structured Output and Tool Calling  (L5064)
  源文件: .gemini/styleguide.md, .github/copilot-instructions.md, src/agentscope/_utils/_common.py, src/agentscope/_version.py, src/agentscope/agent/_react_agent.py, src/agentscope/model/_anthropic_model.py, src/agentscope/model/_dashscope_model.py, src/agentscope/model/_gemini_model.py, src/agentscope/model/_model_usage.py, src/agentscope/model/_ollama_model.py, src/agentscope/model/_openai_model.py, src/agentscope/tool/_toolkit.py
  Purpose and Scope
  Tool Schema Format
    · Standard Tool Schema Structure
    · Schema Extraction from Python Functions
  Structured Output with Pydantic BaseModel
    · Conversion Mechanism
    · Implementation Details
    · Provider-Specific Handling
  Tool Calling Mechanics
    · ToolUseBlock Structure
    · Tool Choice Modes
    · Response Parsing Flow
  Provider-Specific Tool Formatting
    · Gemini Format and Schema Flattening
    · DashScope and Anthropic Validation
  Streaming and Tool Parsing
    · JSON Repair and Regression Prevention
    · Control Parameter: `stream_tool_parsing`
  Summary Table: Provider Comparison

## · Realtime and TTS Models  (L5322)
  源文件: assets/images/dingtalk_qr_code.png, docs/tutorial/en/build.sh, docs/tutorial/en/src/task_realtime.py, docs/tutorial/en/src/task_tts.py, docs/tutorial/zh_CN/build.sh, docs/tutorial/zh_CN/src/task_realtime.py, docs/tutorial/zh_CN/src/task_tts.py, src/agentscope/realtime/_base.py, src/agentscope/realtime/_dashscope_realtime_model.py, src/agentscope/realtime/_gemini_realtime_model.py, src/agentscope/realtime/_openai_realtime_model.py, src/agentscope/tts/__init__.py
  Realtime Models
    · RealtimeModelBase Architecture
    · Supported Realtime Providers
    · Event System and Data Flow
  Text-to-Speech (TTS) Models
    · TTSModelBase Interface
    · Supported TTS Providers
    · Implementation Detail: OpenAI TTS
  Voice Agent Pattern
    · Integration with ReActAgent
    · Realtime Voice Agent Components
    · Audio Configuration Requirements

## · Embedding Models  (L5498)
  源文件: src/agentscope/embedding/_dashscope_embedding.py, src/agentscope/embedding/_dashscope_multimodal_embedding.py, src/agentscope/embedding/_ollama_embedding.py
  Architecture and Base Abstractions
    · EmbeddingModelBase
    · EmbeddingResponse and Usage
    · Embedding Model Hierarchy
  Provider Implementations
    · Multimodal Embeddings
  Embedding Caching
  Usage in RAG Pipelines
    · Integration with Knowledge Systems
    · Batching and Efficiency

## · Tool System  (L5665)
  源文件: .gemini/styleguide.md, .github/copilot-instructions.md, docs/tutorial/en/src/quickstart_agent.py, src/agentscope/_version.py, src/agentscope/plan/_in_memory_storage.py, src/agentscope/plan/_plan_model.py, src/agentscope/plan/_plan_notebook.py, src/agentscope/tool/_toolkit.py, src/agentscope/tool/_types.py, tests/plan_test.py, tests/toolkit_async_execution_test.py, tests/toolkit_basic_test.py
  System Architecture
  Tool Registration
  Tool Execution
  Tool Groups and Dynamic Activation
  MCP Integration
  Agent Skills
  Middleware System
  State Management

## · Toolkit Core Architecture  (L6089)
  源文件: .gemini/styleguide.md, .github/copilot-instructions.md, src/agentscope/_version.py, src/agentscope/tool/_async_wrapper.py, src/agentscope/tool/_toolkit.py, src/agentscope/tool/_types.py, tests/toolkit_async_execution_test.py
  Overview
  Core Class Structure
    · Toolkit Data Model
  Tool Registration Pipeline
    · Registration Flow
    · RegisteredToolFunction Schema Extension
  Tool Execution Pipeline
    · Execution Architecture with Middleware
    · Async Execution Support
    · Unified Async Interface
  Tool Groups and Dynamic Control
    · Group Management System
  State Management

## · Tool Registration and Execution  (L6377)
  源文件: .gemini/styleguide.md, .github/copilot-instructions.md, docs/tutorial/en/src/quickstart_agent.py, src/agentscope/_version.py, src/agentscope/plan/_in_memory_storage.py, src/agentscope/plan/_plan_model.py, src/agentscope/plan/_plan_notebook.py, src/agentscope/tool/_async_wrapper.py, src/agentscope/tool/_toolkit.py, src/agentscope/tool/_types.py, tests/plan_test.py, tests/toolkit_async_execution_test.py
  Overview
  Tool Function Registration
    · Registration Flow
    · Function Type Handling
    · JSON Schema and Pydantic Extensions
    · Namesake Conflict Resolution
  Tool Execution Pipeline
    · Unified Execution Flow
    · Async Background Execution
    · Middleware and Post-processing
  Tracing and Observability

## · Tool Groups and Meta-Tools  (L6565)
  源文件: .gemini/styleguide.md, .github/copilot-instructions.md, docs/tutorial/en/src/quickstart_agent.py, src/agentscope/_version.py, src/agentscope/plan/_in_memory_storage.py, src/agentscope/plan/_plan_model.py, src/agentscope/plan/_plan_notebook.py, src/agentscope/tool/_toolkit.py, src/agentscope/tool/_types.py, tests/plan_test.py, tests/toolkit_async_execution_test.py, tests/toolkit_basic_test.py
  Purpose and Scope
  Tool Group Fundamentals
    · The ToolGroup Dataclass
    · The "basic" Group
  Creating and Managing Tool Groups
    · Creating Tool Groups
    · Group State Transitions
    · Bulk Group Management
  Dynamic Tool Control with reset_equipped_tools
    · The Meta-Tool Function
    · Function Behavior
  Dynamic Schema Generation
    · Schema Filtering by Active State
    · Extended Model System
  Notes and Usage Instructions
    · Retrieving Active Notes
  About Tool Group 'web_search'
  State Management
    · Serialization and Persistence
  Tool Execution and Group Validation

## · MCP Integration  (L6824)
  源文件: examples/functionality/mcp/README.md, examples/functionality/mcp/main.py, examples/functionality/mcp/mcp_add.py, examples/functionality/mcp/mcp_multiply.py, src/agentscope/formatter/_dashscope_formatter.py, src/agentscope/formatter/_formatter_base.py, src/agentscope/mcp/_client_base.py, src/agentscope/mcp/_http_stateless_client.py, src/agentscope/mcp/_mcp_function.py, src/agentscope/mcp/_stateful_client_base.py, src/agentscope/tool/_response.py, tests/formatter_dashscope_test.py
  Overview
  MCP Client Architecture
    · Natural Language to Code Entity Mapping
    · Client Types and Implementation
  MCPToolFunction Wrapper
    · Key Behaviors
  The get_callable_function Pattern
    · Implementation Details
  Data Flow: MCP Tool Execution
    · Content Conversion Mapping
  Lifecycle Management

## · Built-in Tools and Agent Skills  (L6998)
  源文件: .github/workflows/pre-commit.yml, LICENSE, docs/tutorial/en/src/task_agent_skill.py, docs/tutorial/zh_CN/src/task_agent_skill.py, examples/agent/react_agent/main.py, examples/functionality/agent_skill/README.md, examples/functionality/agent_skill/main.py, examples/functionality/agent_skill/skill/analyzing-agentscope-library/SKILL.md, examples/functionality/agent_skill/skill/analyzing-agentscope-library/view_agentscope_module.py, src/agentscope/tool/_coding/_python.py, src/agentscope/tool/_text_file/_view_text_file.py, src/agentscope/tool/_text_file/_write_text_file.py
  Built-in Tool Functions
    · Text File Manipulation Tools
    · Code Execution Tools
  Agent Skills System
    · Agent Skills Architecture
    · Registering Agent Skills
    · Generating Agent Skills Prompt
    · Integration with ReActAgent
    · Workflow: Skill Discovery to Execution
  Tool Response Format
    · Success Response (File Insertion)
    · Success Response (Code Execution)
    · Error Response

## · Middleware System  (L7325)
  源文件: docs/tutorial/en/src/task_middleware.py, docs/tutorial/zh_CN/src/task_middleware.py, src/agentscope/tracing/_trace.py, tests/toolkit_middleware_test.py
  Architecture Overview
    · Onion Model Structure
  Middleware Signature and Requirements
    · Function Signature
    · Parameter Specifications
  Middleware Registration and Execution
    · Registration Method
    · Execution Flow
  Implementation Details
    · The `_apply_middlewares` Decorator
    · Integration with `call_tool_function`
  Pre-Processing and Post-Processing Patterns
    · Pre-Processing Pattern
    · Post-Processing Pattern
  Code Entity Mapping
  Common Use Cases
    · Logging and Monitoring
    · Authorization and Access Control
    · Input/Output Transformation
  Integration with Observability
  Execution Order with Multiple Middleware
  Future Extensions

## · Memory and Knowledge Systems  (L7678)
  源文件: docs/tutorial/en/src/task_agent.py, docs/tutorial/en/src/task_long_term_memory.py, docs/tutorial/en/src/task_memory.py, docs/tutorial/zh_CN/src/task_agent.py, docs/tutorial/zh_CN/src/task_long_term_memory.py, docs/tutorial/zh_CN/src/task_memory.py, examples/functionality/long_term_memory/reme/README.md, examples/functionality/short_term_memory/memory_compression/README.md, src/agentscope/memory/__init__.py
  Overview and Scope
  Working Memory Architecture
    · MemoryBase Interface
    · InMemoryMemory Implementation
  Memory Compression
    · CompressionConfig
  Redis Memory and Multi-Tenancy
    · Key Design Patterns
  Session State Management
    · SessionBase Interface
  Long-Term Memory with Mem0
    · Mem0LongTermMemory Architecture
  Long-Term Memory with ReME
  RAG System Overview
    · KnowledgeBase Architecture
  Vector Store Integrations

## · Working Memory Architecture  (L8059)
  源文件: src/agentscope/memory/_working_memory/_in_memory_memory.py, src/agentscope/memory/_working_memory/_redis_memory.py, src/agentscope/session/__init__.py, src/agentscope/session/_json_session.py, src/agentscope/session/_redis_session.py, src/agentscope/session/_session_base.py, tests/memory_compression_test.py, tests/memory_test.py, tests/session_test.py
  Architecture Overview
  MemoryBase Interface
    · Core Methods
  InMemoryMemory Implementation
    · Internal Data Structure
  Message Marks System
    · Common Mark Types
    · Using Marks
  Memory Operations
    · Retrieving Messages: `get_memory()`
    · Adding Messages: `add()`
    · Updating Marks: `update_messages_mark()`
  State Management and Serialization
    · State Dictionary Format
    · Session Integration

## · Memory Compression  (L8296)
  源文件: src/agentscope/_utils/_common.py, src/agentscope/agent/_react_agent.py, src/agentscope/memory/_working_memory/_in_memory_memory.py, src/agentscope/model/_anthropic_model.py, src/agentscope/model/_dashscope_model.py, src/agentscope/model/_gemini_model.py, src/agentscope/model/_model_usage.py, src/agentscope/model/_ollama_model.py, src/agentscope/model/_openai_model.py, tests/memory_compression_test.py, tests/model_anthropic_test.py, tests/model_dashscope_test.py
  Overview
  CompressionConfig Class
  SummarySchema BaseModel
  Trigger Logic and Execution Flow
  Memory Marking and Summary Storage
  ReActAgent Integration

## · Redis Memory and Multi-Tenancy  (L8557)
  源文件: src/agentscope/memory/_working_memory/_redis_memory.py, src/agentscope/session/__init__.py, src/agentscope/session/_json_session.py, src/agentscope/session/_redis_session.py, src/agentscope/session/_session_base.py, tests/memory_test.py, tests/session_test.py
  Purpose and Scope
  RedisMemory Overview
  Key Structure and Namespacing
    · Complete Key Patterns
    · Marks Index System
  Multi-Tenancy and Isolation
    · TTL Management
  SQL-Backed Memory: AsyncSQLAlchemyMemory
    · Database Schema
    · Key Features
  Session State Persistence
    · RedisSession
    · JSONSession
    · Data Flow for Session Saving

## · Session State Management  (L8734)
  源文件: docs/tutorial/en/src/task_state.py, docs/tutorial/zh_CN/src/task_state.py, examples/functionality/session_with_sqlite/README.md, examples/functionality/session_with_sqlite/main.py, examples/functionality/session_with_sqlite/sqlite_session.py, src/agentscope/memory/_working_memory/_redis_memory.py, src/agentscope/session/__init__.py, src/agentscope/session/_json_session.py, src/agentscope/session/_redis_session.py, src/agentscope/session/_session_base.py, tests/memory_test.py, tests/session_test.py
  Purpose and Scope
  StateModule Interface
    · Core Methods
    · Automatic and Nested State
    · StateModule Implementation Pattern
  SessionBase Architecture
    · Interface Definition
    · Session Save/Load Flow
  JSONSession Implementation
    · Configuration and File Naming
    · Implementation Details
  RedisSession Implementation
    · Redis Key Pattern
    · Sliding TTL Mechanism
    · Multi-Tenant Isolation
  SQLite Session (Example Implementation)
    · Schema and Logic
  Memory vs. Session State
  Usage Summary

## · Long-Term Memory with Mem0  (L9019)
  源文件: .gitignore, docs/tutorial/en/src/task_prompt.py, docs/tutorial/zh_CN/src/task_prompt.py, examples/functionality/long_term_memory/mem0/README.md, examples/functionality/long_term_memory/mem0/memory_example.py, src/agentscope/memory/_long_term_memory/_long_term_memory_base.py, src/agentscope/memory/_long_term_memory/_mem0/_mem0_long_term_memory.py, src/agentscope/memory/_long_term_memory/_mem0/_mem0_utils.py, tests/mem0_utils_test.py
  Architecture Overview
  Wrapper Classes
    · AgentScopeLLM Wrapper
    · AgentScopeEmbedding Wrapper
    · Event Loop Management
  Configuration
    · Vector Store Configuration
    · Graph Store Configuration
    · Model Configuration
  Integration with ReActAgent
    · Integration Modes
    · Tool-Based Integration ("both" mode)
  Core Operations
    · Developer API: record() and retrieve()
    · Tool API: record_to_memory() and retrieve_from_memory()
  Implementation Details
    · Provider Registration
    · Identity Management and Metadata
    · Logging Suppression

## · Long-Term Memory with ReME  (L9552)
  源文件: docs/tutorial/en/src/task_long_term_memory.py, docs/tutorial/zh_CN/src/task_long_term_memory.py, examples/functionality/long_term_memory/reme/README.md, examples/functionality/long_term_memory/reme/personal_memory_example.py, examples/functionality/long_term_memory/reme/task_memory_example.py, examples/functionality/long_term_memory/reme/tool_memory_example.py, examples/functionality/short_term_memory/reme/README.md, examples/functionality/short_term_memory/reme/reme_short_term_memory.py, examples/functionality/short_term_memory/reme/short_term_memory_example.py, src/agentscope/memory/__init__.py, tests/memory_reme_test.py
  Overview of ReMe Memory System
  Architecture and Data Flow
    · Natural Language to Code Entity Mapping
    · ReMeLongTermMemoryBase and Initialization
  Specialized Memory Types
    · 1. Personal Memory (`ReMePersonalLongTermMemory`)
    · 2. Task Memory (`ReMeTaskLongTermMemory`)
    · 3. Tool Memory (`ReMeToolLongTermMemory`)
  Integration with ReActAgent
  Implementation Details
    · Data Recording (record_to_memory)
    · Data Retrieval (retrieve_from_memory)
    · Context Management

## · Long-Term Memory Integration  (L9740)
  源文件: docs/tutorial/en/src/task_long_term_memory.py, docs/tutorial/zh_CN/src/task_long_term_memory.py, examples/functionality/long_term_memory/reme/README.md, src/agentscope/_utils/_common.py, src/agentscope/agent/_react_agent.py, src/agentscope/memory/__init__.py, src/agentscope/model/_anthropic_model.py, src/agentscope/model/_dashscope_model.py, src/agentscope/model/_gemini_model.py, src/agentscope/model/_model_usage.py, src/agentscope/model/_ollama_model.py, src/agentscope/model/_openai_model.py
  Purpose and Scope
  Integration Architecture
    · Code Entity Space Mapping
  Integration Modes in ReActAgent
  Tool-Based Memory Operations
    · Tool Registration Flow
    · Registered Function Signatures
  Memory Implementation Details
    · Mem0 Integration
    · ReMe (Reflection Memory) Suite
  Data Flow: Memory Recording and Retrieval
  Configuration Example

## · RAG System Overview  (L9956)
  源文件: docs/tutorial/en/src/task_embedding.py, docs/tutorial/en/src/task_rag.py, docs/tutorial/zh_CN/src/task_embedding.py, docs/tutorial/zh_CN/src/task_rag.py, examples/functionality/rag/README.md, examples/functionality/rag/agentic_usage.py, examples/functionality/rag/basic_usage.py, examples/functionality/vector_store/oceanbase/README.md, examples/functionality/vector_store/oceanbase/main.py, pyproject.toml, src/agentscope/hooks/_studio_hooks.py, src/agentscope/rag/__init__.py
  Core Components
    · Knowledge Base Architecture
    · Document Model
  Document Processing Pipeline
    · Pipeline Flow
    · Document Readers
    · Table and Image Utilities
  Vector Store Backend
    · VDBStoreBase Interface
    · Implementation Comparison
  SimpleKnowledge Implementation
    · Initialization and Retrieval
  ReActAgent Integration
    · Agentic Retrieval Workflow
    · Generic Retrieval Workflow

## · Vector Store Integrations  (L10313)
  源文件: examples/functionality/vector_store/alibabacloud_mysql_vector/README.md, examples/functionality/vector_store/alibabacloud_mysql_vector/main.py, examples/functionality/vector_store/milvus_lite/README.md, examples/functionality/vector_store/milvus_lite/main.py, examples/functionality/vector_store/mongodb/README.md, examples/functionality/vector_store/mongodb/main.py, examples/functionality/vector_store/oceanbase/README.md, examples/functionality/vector_store/oceanbase/main.py, pyproject.toml, src/agentscope/rag/__init__.py, src/agentscope/rag/_store/__init__.py, src/agentscope/rag/_store/_alibabacloud_mysql_store.py
  Architecture Overview
    · System to Code Entity Mapping
  VDBStoreBase Interface
  Document and Metadata Structure
  Concrete Implementations
    · QdrantStore
    · MilvusLiteStore
    · OceanBaseStore
    · MongoDBStore
    · AlibabaCloudMySQLStore
  Data Flow and Operations
    · Key Operations Summary
  Configuration and Dependencies

## · Multi-Agent Orchestration  (L10555)
  源文件: src/agentscope/agent/_agent_base.py, src/agentscope/pipeline/__init__.py, src/agentscope/pipeline/_class.py, src/agentscope/pipeline/_functional.py, src/agentscope/pipeline/_msghub.py, tests/pipeline_test.py
  Overview
  Architecture Overview
  Subscriber System
    · Implementation Details
    · Key Methods
  MsgHub: Central Message Router
    · Key Features
  Pipeline Patterns
    · Sequential Pipeline
    · Fanout Pipeline
    · Stream Printing Messages
  Agent Collaboration Patterns
    · observe() vs reply()
    · Message Queue for Streaming
  Summary

## · MsgHub Communication  (L10919)
  源文件: examples/game/werewolves/README.md, examples/game/werewolves/game.py, examples/game/werewolves/main.py, examples/game/werewolves/prompt.py, examples/game/werewolves/utils.py, src/agentscope/pipeline/_class.py, src/agentscope/pipeline/_msghub.py
  Overview
    · Core Features
  MsgHub Architecture
    · Communication Flow Diagram
  Creating and Configuring MsgHub
    · Basic Initialization
    · Implementation Details
  Broadcasting Modes
    · Auto-broadcast Mode
    · Manual Broadcast Mode
  Dynamic Participant Management
    · Key Functions
    · Lifecycle Management
  Integration with Pipelines
    · Sequential and Fanout Interaction
  Summary of Key Methods

## · Pipeline Patterns  (L11149)
  源文件: docs/tutorial/en/src/task_pipeline.py, docs/tutorial/zh_CN/src/task_pipeline.py, examples/functionality/stream_printing_messages/README.md, examples/functionality/stream_printing_messages/multi_agent.py, examples/workflows/multiagent_conversation/README.md, examples/workflows/multiagent_conversation/main.py, examples/workflows/multiagent_debate/README.md, src/agentscope/agent/_agent_base.py, src/agentscope/pipeline/__init__.py, src/agentscope/pipeline/_functional.py, src/agentscope/tool/_multi_modality/_dashscope_tools.py, src/agentscope/tool/_multi_modality/_openai_tools.py
  Purpose and Scope
  Overview of Pipeline Patterns
  Sequential Pipeline
    · Implementation Details
    · Data Flow Diagram
  Fanout Pipeline
    · Implementation Details
    · Concurrent Execution Flow
  Stream Printing Messages
    · Implementation Logic
    · Data Flow: Agent to Generator
  Pipeline Composition
    · Pattern: Sequential Fanout
    · Integration with MsgHub

## · Subscriber Broadcasting  (L11388)
  源文件: examples/workflows/multiagent_concurrent/README.md, examples/workflows/multiagent_concurrent/main.py, src/agentscope/agent/_agent_base.py, src/agentscope/pipeline/__init__.py, src/agentscope/pipeline/_functional.py, tests/pipeline_test.py
  Purpose and Scope
  Overview
  Subscriber Data Structure
    · The `_subscribers` Dictionary
  Subscription Management API
    · `reset_subscribers` Method
    · `remove_subscribers` Method
  Broadcasting Mechanism
    · Architecture Overview
    · The `_broadcast_to_subscribers` Method
    · Integration with Agent Execution Flow
  Message Flow Example
    · Multi-Agent Broadcasting Workflow
  Typical Usage Patterns
    · Pattern 1: MsgHub-Managed Subscriptions
    · Pattern 2: Manual Subscription Management
    · Pattern 3: Multiple Subscription Groups
  Relationship with Other Communication Patterns
    · Comparison with Pipeline Patterns
    · Integration with MsgHub
  Implementation Details
    · Self-Exclusion
    · Error Handling

## · Observability and Evaluation  (L11740)
  源文件: README.md, README_zh.md, assets/images/agentscope.png, docs/tutorial/en/index.rst, docs/tutorial/en/src/task_eval_openjudge.py, docs/tutorial/en/src/task_tracing.py, docs/tutorial/zh_CN/index.rst, docs/tutorial/zh_CN/src/task_eval_openjudge.py, docs/tutorial/zh_CN/src/task_tracing.py
  Overview
  Tracing Architecture
    · Configuration and Initialization
    · Tracing Decorators
  Evaluation Framework
    · Core Architecture
    · Component Specifications
  OpenJudge Integration
    · Mapper Pattern

## · OpenTelemetry Integration  (L11912)
  源文件: README.md, README_zh.md, assets/images/agentscope.png, docs/tutorial/en/src/task_studio.py, docs/tutorial/en/src/task_tracing.py, docs/tutorial/zh_CN/src/task_studio.py, docs/tutorial/zh_CN/src/task_tracing.py, src/agentscope/tracing/_setup.py
  Tracing Architecture
    · Implementation Details
  Configuration via agentscope.init
    · Connecting to AgentScope Studio
    · Connecting to Third-Party OTLP Backends
  Supported Backends & Authentication
    · Alibaba Cloud CloudMonitor
    · Arize Phoenix
    · Langfuse
  Code Entity Association
    · Key Classes and Functions

## · Tracing Decorators and Usage  (L12139)
  源文件: docs/tutorial/en/src/task_middleware.py, docs/tutorial/zh_CN/src/task_middleware.py, src/agentscope/tracing/_attributes.py, src/agentscope/tracing/_converter.py, src/agentscope/tracing/_extractor.py, src/agentscope/tracing/_trace.py, src/agentscope/tracing/_utils.py, tests/toolkit_middleware_test.py, tests/tracing_converter_test.py, tests/tracing_extractor_test.py, tests/tracing_test.py
  Overview
  Decorator Architecture
    · Execution Flow Diagram
  Natural Language to Code Entity Mapping
    · LLM Tracing Bridge (`@trace_llm`)
    · Tool Execution Bridge (`@trace_toolkit`)
  Specialized Decorators
    · Agent Reply Tracing: `@trace_reply`
    · Toolkit Tracing: `@trace_toolkit`
    · Formatter Tracing: `@trace_format`
  Implementation Details
    · Attribute Extraction
    · Content Block Conversion
    · Streaming and Generators
    · Error Handling

## · Evaluation Framework  (L12345)
  源文件: docs/tutorial/en/index.rst, docs/tutorial/en/src/task_eval.py, docs/tutorial/en/src/task_eval_openjudge.py, docs/tutorial/zh_CN/index.rst, docs/tutorial/zh_CN/src/task_eval.py, docs/tutorial/zh_CN/src/task_eval_openjudge.py, examples/evaluation/ace_bench/main.py, src/agentscope/evaluate/_ace_benchmark/_ace_metric.py, src/agentscope/evaluate/_evaluator/_evaluator_base.py, src/agentscope/evaluate/_evaluator/_general_evaluator.py, src/agentscope/evaluate/_evaluator/_in_memory_exporter.py, src/agentscope/evaluate/_evaluator/_ray_evaluator.py
  Core Architecture
    · Component Overview
  Evaluator Implementations
    · GeneralEvaluator
    · RayEvaluator
    · Evaluation Execution Flow
  Task and Solution
    · Task Structure
    · SolutionOutput Structure
  Metrics and Evaluation Results
    · MetricBase
    · MetricResult
    · Metric Types
  Evaluator Storage
    · FileEvaluatorStorage
  Observability and Statistics
    · _InMemoryExporter
    · Usage in Execution
  OpenJudge Integration
    · OpenJudgeMetric Adapter
    · Data Mapping Flow
  Implementation Example: ACEBench

## · OpenJudge Integration  (L12596)
  源文件: docs/tutorial/en/index.rst, docs/tutorial/en/src/task_eval_openjudge.py, docs/tutorial/zh_CN/index.rst, docs/tutorial/zh_CN/src/task_eval_openjudge.py
  Purpose and Scope
  Architecture Overview
    · Evaluation Space Mapping
  OpenJudgeMetric Adapter Class
  Data Mapping System
    · Mapper Structure
    · Combined Data Structure
    · Field Extraction Process
  Evaluation Execution Flow
    · Phase Implementations
  Grader Types and Configuration
    · Common Graders
    · Model Configuration
  Integration with BenchmarkBase
    · Benchmark Implementation Pattern
  Result Structure and Interpretation
    · MetricResult Fields
    · Result Type Handling
  Dependencies and Installation
  Execution with GeneralEvaluator

## · Production and Deployment  (L13080)
  源文件: examples/functionality/vector_store/oceanbase/README.md, examples/functionality/vector_store/oceanbase/main.py, pyproject.toml, src/agentscope/memory/_working_memory/_redis_memory.py, src/agentscope/rag/__init__.py, src/agentscope/rag/_store/__init__.py, src/agentscope/rag/_store/_oceanbase_store.py, src/agentscope/session/__init__.py, src/agentscope/session/_json_session.py, src/agentscope/session/_redis_session.py, src/agentscope/session/_session_base.py, tests/memory_test.py
  State Serialization and Checkpointing
    · Serialization Architecture
  Package Structure and Dependencies
    · Dependency Groups
  Production Deployment Patterns
    · Multi-Tenant Redis Architecture

## · State Serialization and Checkpointing  (L13242)
  源文件: docs/tutorial/en/src/task_state.py, docs/tutorial/zh_CN/src/task_state.py, examples/functionality/session_with_sqlite/README.md, examples/functionality/session_with_sqlite/main.py, examples/functionality/session_with_sqlite/sqlite_session.py, src/agentscope/memory/_working_memory/_redis_memory.py, src/agentscope/session/__init__.py, src/agentscope/session/_json_session.py, src/agentscope/session/_redis_session.py, src/agentscope/session/_session_base.py, tests/memory_test.py, tests/session_test.py
  StateModule Interface
  Session Management Architecture
    · JSONSession Implementation
    · RedisSession Implementation
    · Custom SQLite Session Implementation
  Memory State Serialization
    · InMemoryMemory vs RedisMemory
  Agent State Registration
  Complete Save/Load Flow
  Usage Patterns
    · Checkpointing with JSONSession
    · Checkpointing with RedisSession

## · Package Structure and Dependencies  (L13530)
  源文件: .github/workflows/publish-pypi.yml, .github/workflows/sphinx_docs.yml, .github/workflows/stale.yml, .github/workflows/toc.yml, .pre-commit-config.yaml, examples/agent/voice_agent/README.md, examples/functionality/vector_store/oceanbase/README.md, examples/functionality/vector_store/oceanbase/main.py, pyproject.toml, src/agentscope/model/_model_response.py, src/agentscope/rag/__init__.py, src/agentscope/rag/_store/__init__.py
  Core Project Structure
    · Project Metadata
  Dependency Architecture
    · Dependency Group Hierarchy
    · Core Dependencies
    · Optional Dependency Groups
  Lazy Loading Principle
    · Implementation Pattern: OceanBaseStore
  Summary of Version Constraints and Conflicts

## · Production Deployment Patterns  (L13737)
  源文件: docs/tutorial/en/src/task_state.py, docs/tutorial/zh_CN/src/task_state.py, examples/functionality/session_with_sqlite/README.md, examples/functionality/session_with_sqlite/main.py, examples/functionality/session_with_sqlite/sqlite_session.py, src/agentscope/memory/_working_memory/_redis_memory.py, src/agentscope/session/__init__.py, src/agentscope/session/_json_session.py, src/agentscope/session/_redis_session.py, src/agentscope/session/_session_base.py, tests/memory_test.py, tests/session_test.py
  Overview
  Memory Architecture: InMemory vs Redis vs SQL
    · Single-Instance Deployments
    · Distributed Deployments
  Redis Key Architecture
    · Key Structure
    · TTL and Expiration Strategy
  Session State Management
    · Serialization Pattern
    · Implementation Comparison
  Production Deployment Patterns
    · Pattern 1: Session Recovery with SQLite
    · Pattern 2: Distributed Agent Clusters
  Scaling Considerations

## · Advanced Topics  (L13928)
  源文件: README.md, README_zh.md, assets/images/agentscope.png, docs/tutorial/en/src/task_tracing.py, docs/tutorial/zh_CN/src/task_tracing.py
  Multimodal Content Handling
    · Content Block Architecture
    · Source Type Handling
    · Tool Result Image Promotion
  Human-in-the-Loop and Interruption
    · Interruption Mechanism
  Extending AgentScope
    · Extension Points Overview
  Agent Communication Protocols
    · A2A and MCP Integration
  Agentic RL and Tuner
    · RL Workflow Components

## · Multimodal Agents  (L14133)
  源文件: src/agentscope/agent/_agent_base.py, src/agentscope/formatter/_gemini_formatter.py, src/agentscope/pipeline/__init__.py, src/agentscope/pipeline/_functional.py, tests/formatter_anthropic_test.py, tests/formatter_deepseek_test.py, tests/formatter_gemini_test.py, tests/formatter_ollama_test.py, tests/model_gemini_test.py, tests/pipeline_test.py
  Overview
  Content Block Architecture
    · Content Block Types
    · Source Type Specifications
  Source Type Processing
    · Key Utility Functions
  Provider-Specific Handling
    · DashScope Multimodality Selection
    · OpenAI and Compatible Models
    · Gemini Inline Data
  Tool Result Image Promotion
  Token Counting

## · Human-in-the-Loop and Interruption  (L14306)
  源文件: examples/deployment/README.md, examples/deployment/planning_agent/README.md, examples/deployment/planning_agent/main.py, examples/deployment/planning_agent/test_post.py, src/agentscope/agent/_agent_base.py, src/agentscope/agent/_user_input.py, src/agentscope/pipeline/__init__.py, src/agentscope/pipeline/_functional.py, tests/pipeline_test.py
  Overview
  User Interaction Interfaces
    · UserInput Architecture
    · Implementation Details
  Interruption Mechanism
    · Interruption Handling in Pipelines
    · The handle_interrupt Method
  Streaming and Interruption
  Memory Preservation and Consistency
    · Deployment Patterns

## · Extending AgentScope  (L14480)
  源文件: .gemini/styleguide.md, .github/PULL_REQUEST_TEMPLATE.md, .github/copilot-instructions.md, .github/workflows/pr-title-check.yml, CONTRIBUTING.md, CONTRIBUTING_zh.md, src/agentscope/_version.py, src/agentscope/agent/_agent_base.py, src/agentscope/pipeline/__init__.py, src/agentscope/pipeline/_functional.py, src/agentscope/tool/_toolkit.py, src/agentscope/tool/_types.py
  Overview of Extension Points
  Creating Custom Agents
    · Required Methods
    · Minimal Agent Implementation
    · Agent Execution Flow
    · Hook System Integration
  Creating Custom Models
    · Model-Formatter Architecture
    · Implementing ChatModelBase
    · Creating Custom Formatters
  Creating Custom Tools
    · Tool Function Pattern
    · Async Execution and Middlewares
  Multi-Agent Pipelines
    · Pipeline Patterns
    · Capturing Custom Agent Output
  Summary of Guidelines

## · Agent Communication Protocols  (L14820)
  源文件: examples/agent/a2a_agent/setup_a2a_server.py, examples/game/werewolves/structured_model.py, src/agentscope/mcp/_http_stateless_client.py, src/agentscope/mcp/_mcp_function.py, src/agentscope/mcp/_stateful_client_base.py, src/agentscope/message/_message_base.py, tests/formatter_a2a_test.py
  Overview
  A2A (Agent-to-Agent) Protocol
    · A2A Message Formatting
    · A2A Architecture and Data Flow
    · A2A Server Implementation
  MCP (Model Context Protocol) Integration
    · MCP Integration Architecture
    · Client Types
    · MCPToolFunction Wrapper
  Agent Communication Patterns
    · Structured Output and Voting

## · Agentic RL and Tuner  (L14998)
  源文件: docs/tutorial/en/src/task_tuner.py, docs/tutorial/zh_CN/src/task_tuner.py, examples/tuner/model_tuning/main.py, examples/tuner/prompt_tuning/README.md, src/agentscope/model/__init__.py, src/agentscope/model/_trinity_model.py, src/agentscope/tune/__init__.py, src/agentscope/tuner/__init__.py, src/agentscope/tuner/_algorithm.py, src/agentscope/tuner/_config.py, src/agentscope/tuner/_dataset.py, src/agentscope/tuner/_judge.py
  Overview and Architecture
    · Data Flow and System Components
  Core Configuration Classes
    · 1. TunerModelConfig
    · 2. DatasetConfig
    · 3. AlgorithmConfig
  Agentic RL Workflow
    · Workflow Function (`WorkflowType`)
    · Judge Function (`JudgeType`)
  Prompt Tuning
    · PromptTuneConfig
    · Workflow
  Model Selection
  Implementation Details: `tune()`
    · Configuration Mapping

## · Glossary  (L15184)
  源文件: .gemini/styleguide.md, .github/copilot-instructions.md, README.md, README_zh.md, assets/images/agentscope.png, docs/tutorial/en/src/task_tracing.py, docs/tutorial/zh_CN/src/task_tracing.py, examples/functionality/vector_store/oceanbase/README.md, examples/functionality/vector_store/oceanbase/main.py, pyproject.toml, src/agentscope/_utils/_common.py, src/agentscope/_version.py
  Core Abstractions
    · Msg (Message Object)
    · Content Blocks
    · StateModule
  Memory Systems
    · Working Memory
    · Memory Marks
    · Memory Compression
  Tooling and Integration
    · Toolkit
    · MCP (Model Context Protocol)
    · Tool Group
  System Architecture Diagrams
    · From Natural Language Space to Code Entity Space
    · Data Flow: Message and State Persistence
  Table of Technical Terms