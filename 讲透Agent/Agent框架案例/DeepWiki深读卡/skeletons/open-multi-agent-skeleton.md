# Skeleton: open-multi-agent（26 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 4KB | 2 | ~0 | 3 |
| 2 | Getting Started | L125 | 5KB | 2 | ~2 | 4 |
| 3 | Public API Reference | L278 | 6KB | 2 | ~0 | 3 |
| 4 | Core Architecture | L457 | 6KB | 2 | ~2 | 3 |
| 5 | Orchestrator | L598 | 6KB | 2 | ~2 | 3 |
| 6 | Team and Messaging | L732 | 6KB | 2 | ~1 | 3 |
| 7 | Task System | L880 | 6KB | 2 | ~4 | 3 |
| 8 | Scheduler and AgentPool | L1038 | 6KB | 1 | ~2 | 3 |
| 9 | Agent Layer | L1158 | 5KB | 2 | ~0 | 2 |
| 10 | Agent Class | L1282 | 6KB | 2 | ~1 | 2 |
| 11 | AgentRunner and Conversation Loop | L1440 | 5KB | 2 | ~4 | 2 |
| 12 | LLM Adapters | L1577 | 4KB | 2 | ~4 | 2 |
| 13 | LLMAdapter Interface | L1690 | 5KB | 2 | ~6 | 2 |
| 14 | Anthropic and OpenAI Adapters | L1845 | 6KB | 2 | ~2 | 3 |
| 15 | Tool System | L1985 | 5KB | 2 | ~0 | 3 |
| 16 | Tool Framework: defineTool and ToolRegistry | L2118 | 6KB | 2 | ~4 | 2 |
| 17 | ToolExecutor | L2267 | 6KB | 2 | ~2 | 2 |
| 18 | Built-in Tools | L2398 | 7KB | 2 | ~2 | 6 |
| 19 | Memory System | L2542 | 4KB | 2 | ~0 | 3 |
| 20 | MemoryStore and InMemoryStore | L2643 | 6KB | 2 | ~2 | 2 |
| 21 | SharedMemory | L2792 | 4KB | 2 | ~1 | 2 |
| 22 | Usage Examples | L2939 | 5KB | 2 | ~2 | 4 |
| 23 | Single Agent and Streaming | L3058 | 6KB | 3 | ~3 | 2 |
| 24 | Team Collaboration and Task Pipelines | L3205 | 7KB | 2 | ~4 | 3 |
| 25 | Multi-Model Teams and Custom Tools | L3348 | 6KB | 2 | ~4 | 3 |
| 26 | Glossary | L3474 | 6KB | 3 | ~3 | 9 |


## · Overview  (L6)
  源文件: README.md, package.json, src/index.ts
  High-Level Architecture
    · System Component Relationship
  Key Concepts
    · 1. The Orchestrator
    · 2. Teams and Messaging
    · 3. Task DAG Scheduling
    · 4. Agents and Tools
  Natural Language to Code Entity Mapping
  Next Steps

## · Getting Started  (L125)
  源文件: .gitignore, package-lock.json, package.json, tsconfig.json
  Prerequisites
  Installation and Setup
    · Build and Test Scripts
  Quick Start: Usage Patterns
    · Pattern 1: Single Agent Execution
    · Pattern 2: Team Collaboration (Coordinator Pattern)
  System Initialization Flow
  Implementation Detail: Component Interaction

## · Public API Reference  (L278)
  源文件: README.md, src/index.ts, src/types.ts
  Overview of Public Surface
    · Code Entity Mapping
  Orchestrator and Scheduling
    · `OpenMultiAgent`
    · `Scheduler`
  Agent and Pool Layer
    · `Agent`
    · `AgentPool`
  Task and Team Layer
    · `Team`
    · `Task` and `TaskQueue`
  Tool System
    · `defineTool`
    · `ToolRegistry` & `ToolExecutor`
    · Built-in Tools
  Memory and LLM Adapters
    · Memory
    · LLM Adapters
  Core Type Reference
    · Content Blocks
    · Execution Results

## · Core Architecture  (L457)
  源文件: README.md, src/orchestrator/orchestrator.ts, src/types.ts
  Architectural Layers
    · System Data Flow
  Core Components
    · 1. Orchestrator (`OpenMultiAgent`)
    · 2. Team and Messaging
    · 3. Task System
    · 4. Scheduler and AgentPool
  Mapping Natural Language to Code Entities
  Data Flow: From Goal to Result

## · Orchestrator  (L598)
  源文件: README.md, src/orchestrator/orchestrator.ts, src/orchestrator/scheduler.ts
    · Core Responsibilities
  The Coordinator Pattern
    · Decomposition and Synthesis Loop
    · Natural Language to Code Entity Mapping: Decomposition
  Orchestration Loop (executeQueue)
    · Task Scheduling Strategies
  System Wiring and Data Flow
    · Key Public Methods

## · Team and Messaging  (L732)
  源文件: src/memory/shared.ts, src/team/messaging.ts, src/team/team.ts
  The Team Class
    · Key Components
    · Team Initialization and Event Bridging
  Messaging System
    · Message Structure
    · Delivery Logic
    · Team Messaging Flow
  Shared Memory
    · Namespacing and Writing
    · Memory Summarization
  Shared Team Memory
    · researcher
    · coder
    · Memory Architecture
  Task Management in Team

## · Task System  (L880)
  源文件: src/task/queue.ts, src/task/task.ts, src/types.ts
  Task Model and Lifecycle
    · Task Status Lifecycle
    · The Task Entity
  Task Helpers and Validation
    · Creation and Readiness
    · Dependency Management
  TaskQueue: Dependency-Aware Scheduling
    · Event-Driven Architecture
    · Scheduling Logic
    · Failure Handling and Cascading
    · Key Methods
  Data Flow: Task Execution Loop

## · Scheduler and AgentPool  (L1038)
  源文件: src/agent/pool.ts, src/orchestrator/scheduler.ts, src/utils/semaphore.ts
  AgentPool
    · Concurrency Control
    · Registry and Status
  Scheduler
    · Scheduling Strategies
    · Keyword Matching Logic
  Data Flow: Task Assignment to Execution
    · Task Dispatch Pipeline
  Implementation Details
    · Semaphore-based Concurrency
    · Dependency Analysis
    · AgentPool Status Snapshot

## · Agent Layer  (L1158)
  源文件: src/agent/agent.ts, src/agent/runner.ts
    · Core Components
    · High-Level Architecture
  3.1 Agent Class
    · Key Responsibilities
  3.2 AgentRunner and Conversation Loop
    · The Agentic Loop
    · Execution Control

## · Agent Class  (L1282)
  源文件: src/agent/agent.ts, src/types.ts
    · Core Architecture and Data Flow
    · Agent Configuration and State
    · Execution API
    · Token Usage Tracking
    · Dynamic Tool Management
    · State and History Management

## · AgentRunner and Conversation Loop  (L1440)
  源文件: src/agent/runner.ts, src/types.ts
  The Agentic Loop
    · Conversation Lifecycle Diagram
  Runner Configuration and Options
    · RunnerOptions
    · RunOptions
  Tool Execution and Result Injection
    · Data Flow: Natural Language to Tool Execution
  Streaming via AsyncGenerator
    · Stream Event Types
  RunResult and Accounting
  Implementation Details: `_runLoop`

## · LLM Adapters  (L1577)
  源文件: src/llm/adapter.ts, src/types.ts
    · Architecture Overview
    · The LLMAdapter Interface
    · Concrete Implementations
    · Adapter Factory and Lazy Loading
    · Summary of Key Types

## · LLMAdapter Interface  (L1690)
  源文件: src/llm/adapter.ts, src/types.ts
  Interface Definition
    · LLMAdapter Interface
    · Core Data Structures
    · Configuration Options
  Streaming and Events
    · StreamEvent Types
  The Adapter Factory
    · Implementation Details
    · Logic Flow: createAdapter
  Data Flow: Code Entities to LLM Space
    · Summary Table: Adapter Capabilities

## · Anthropic and OpenAI Adapters  (L1845)
  源文件: src/llm/adapter.ts, src/llm/anthropic.ts, src/llm/openai.ts
    · Adapter Architecture and Data Flow
    · AnthropicAdapter
    · OpenAIAdapter
    · Error Handling and Abort Signals
    · Configuration

## · Tool System  (L1985)
  源文件: src/tool/built-in/index.ts, src/tool/executor.ts, src/tool/framework.ts
  Overview of the Tool Lifecycle
    · 1. Definition & Registration
    · 2. Execution
    · 3. Built-in Capabilities
  Natural Language to Code Entity Mapping
    · Tool Definition Mapping
    · Execution Flow & Data Translation
  Sub-System Components
    · [Tool Framework: defineTool and ToolRegistry](#5.1)
    · [ToolExecutor](#5.2)
    · [Built-in Tools](#5.3)

## · Tool Framework: defineTool and ToolRegistry  (L2118)
  源文件: src/tool/framework.ts, src/types.ts
  Core Primitives
    · defineTool
    · ToolResult and Context
  ToolRegistry
    · Key Methods
    · Tool Registration Data Flow
  Schema Conversion: zodToJsonSchema
    · Supported Zod Types
    · Conversion Logic
  Implementation Summary

## · ToolExecutor  (L2267)
  源文件: src/tool/executor.ts, src/utils/semaphore.ts
  Core Responsibilities
    · From LLM Request to Code Execution
  Single Execution
  Batch Execution and Concurrency
    · Concurrency Control via Semaphore
  Error Handling and Result Formatting
  Class Reference
    · ToolExecutor
    · ToolExecutorOptions
    · BatchToolCall

## · Built-in Tools  (L2398)
  源文件: src/tool/built-in/bash.ts, src/tool/built-in/file-edit.ts, src/tool/built-in/file-read.ts, src/tool/built-in/file-write.ts, src/tool/built-in/grep.ts, src/tool/built-in/index.ts
    · Registration and Availability
    · Tool Data Flow
    · 1. Bash Execution (`bash`)
    · 2. File Operations (`file_read`, `file_write`, `file_edit`)
    · 3. Search (`grep`)
    · Summary Table

## · Memory System  (L2542)
  源文件: src/memory/shared.ts, src/memory/store.ts, src/types.ts
    · Memory Architecture Overview
  6.1 MemoryStore and InMemoryStore
    · Key Features
  6.2 SharedMemory
    · Core Concepts
    · Data Flow: Shared Memory Interaction

## · MemoryStore and InMemoryStore  (L2643)
  源文件: src/memory/store.ts, src/types.ts
  MemoryStore Interface
    · Data Structures
    · Core Methods
  InMemoryStore Implementation
    · Upsert and Lifecycle Semantics
    · Search Extension
    · System Entity Mapping: Store to Implementation
  Data Flow: Memory Persistence
  Swapping Backends (Redis/SQLite)
    · Implementation Guidance
    · Example Interface Alignment

## · SharedMemory  (L2792)
  源文件: src/memory/shared.ts, src/team/team.ts
  Overview and Namespace Pattern
    · Key Composition
    · Implementation Details
  Data Flow: Writing and Reading
    · Memory Access Flow
  Context Injection via getSummary
    · Summary Generation Logic
    · Example Output
  Shared Team Memory
    · researcher
    · coder
  Orchestrator Integration
    · Orchestrator Result Propagation
    · Key Functions

## · Usage Examples  (L2939)
  源文件: examples/01-single-agent.ts, examples/02-team-collaboration.ts, examples/03-task-pipeline.ts, examples/04-multi-model-team.ts
    · Core Patterns Overview
    · Single Agent and Streaming
    · Team Collaboration and Task Pipelines
    · Multi-Model Teams and Custom Tools

## · Single Agent and Streaming  (L3058)
  源文件: examples/01-single-agent.ts, src/agent/agent.ts
  Overview of Interaction Modes
  One-Shot Execution with OpenMultiAgent
    · Data Flow: runAgent
    · Code Entity Mapping: Orchestrator to Agent
  Streaming and Incremental Output
    · Implementation Details
    · Stream Event Flow
  Multi-Turn Conversations
    · History Management
    · Comparison: run() vs prompt()
  Technical Summary of Classes

## · Team Collaboration and Task Pipelines  (L3205)
  源文件: examples/02-team-collaboration.ts, examples/03-task-pipeline.ts, src/orchestrator/orchestrator.ts
  Overview of Collaboration Patterns
  The Coordinator Pattern (Example 02)
    · Code-to-System Mapping: Coordinator Workflow
    · Implementation Detail: `runTeam`
  Explicit Task Pipelines (Example 03)
    · Code-to-System Mapping: Dependency Pipeline
    · Key Implementation Features
  Progress Monitoring
    · Common Events

## · Multi-Model Teams and Custom Tools  (L3348)
  源文件: examples/04-multi-model-team.ts, src/agent/pool.ts, src/tool/framework.ts
  Overview of Example 04
    · Data Flow: Custom Tool Execution
  Defining Custom Tools
    · Example: Exchange Rate Tool
  Multi-Model Configuration
  Manual Wiring with AgentPool
    · Step-by-Step Wiring Process
    · Execution via AgentPool
  Key Classes and Interfaces

## · Glossary  (L3474)
  源文件: README.md, src/agent/runner.ts, src/memory/shared.ts, src/orchestrator/orchestrator.ts, src/orchestrator/scheduler.ts, src/task/queue.ts, src/tool/framework.ts, src/types.ts, src/utils/semaphore.ts
  Core Concepts
    · Agent
    · Coordinator Pattern
    · Task DAG (Directed Acyclic Graph)
    · Tool
  Mapping: Natural Language to Code Entities
    · Entity Mapping: Orchestration Flow
    · Entity Mapping: Execution Loop
  Technical Terms & Abbreviations
  Component Interactions
    · Data Flow: Task Execution Loop