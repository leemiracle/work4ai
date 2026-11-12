# Skeleton: mateclaw（47 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | MateClaw Overview | L6 | 8KB | 2 | ~2 | 20 |
| 2 | Getting Started & Deployment | L159 | 11KB | 2 | ~1 | 21 |
| 3 | Configuration Reference | L321 | 10KB | 2 | ~4 | 20 |
| 4 | Core Agent Runtime | L494 | 12KB | 2 | ~2 | 18 |
| 5 | StateGraph & Agent Patterns | L660 | 15KB | 2 | ~2 | 17 |
| 6 | Streaming & SSE Delivery | L845 | 12KB | 2 | ~4 | 17 |
| 7 | Tool Execution & Security | L998 | 12KB | 2 | ~0 | 15 |
| 8 | Conversation & History Management | L1147 | 12KB | 2 | ~2 | 18 |
| 9 | LLM Provider Layer | L1323 | 9KB | 2 | ~2 | 17 |
| 10 | Provider Management & Failover | L1482 | 14KB | 3 | ~2 | 16 |
| 11 | ChatModel Builders & Decorators | L1647 | 14KB | 2 | ~2 | 15 |
| 12 | OAuth & Authentication Flows | L1825 | 12KB | 2 | ~1 | 14 |
| 13 | Chat UI & Frontend Architecture | L1967 | 8KB | 1 | ~2 | 15 |
| 14 | Chat Console & Streaming Client | L2111 | 11KB | 2 | ~2 | 18 |
| 15 | Message Rendering & Components | L2295 | 9KB | 2 | ~2 | 16 |
| 16 | LLM Wiki Knowledge Base | L2442 | 9KB | 2 | ~1 | 17 |
| 17 | Ingestion Pipeline | L2584 | 12KB | 2 | ~0 | 18 |
| 18 | Wiki Pages, Retrieval & Enrichment | L2766 | 14KB | 2 | ~2 | 18 |
| 19 | Wiki UI | L2938 | 12KB | 2 | ~4 | 19 |
| 20 | Memory & Dreaming System | L3134 | 11KB | 2 | ~0 | 20 |
| 21 | Memory Lifecycle & Dreaming | L3298 | 14KB | 2 | ~1 | 16 |
| 22 | Fact Extraction & Structured Memory | L3471 | 14KB | 2 | ~2 | 16 |
| 23 | Memory UI (Morning Card & Browser) | L3657 | 10KB | 2 | ~3 | 21 |
| 24 | Tools & Skills | L3837 | 9KB | 2 | ~2 | 17 |
| 25 | Built-in Tools | L3997 | 16KB | 2 | ~2 | 17 |
| 26 | Skill System | L4199 | 14KB | 3 | ~2 | 17 |
| 27 | MCP (Model Context Protocol) Integration | L4388 | 8KB | 2 | ~2 | 6 |
| 28 | Media Generation Tools | L4546 | 11KB | 2 | ~2 | 18 |
| 29 | Channels & Multi-Surface Delivery | L4712 | 10KB | 2 | ~4 | 17 |
| 30 | Channel Framework | L4871 | 9KB | 2 | ~1 | 18 |
| 31 | IM Channel Adapters | L5017 | 9KB | 2 | ~2 | 17 |
| 32 | WebChat Widget & Talk Mode | L5180 | 10KB | 2 | ~1 | 22 |
| 33 | Security, Workspaces & Administration | L5324 | 9KB | 2 | ~2 | 18 |
| 34 | Authentication & RBAC | L5475 | 12KB | 2 | ~2 | 16 |
| 35 | Tool Guard & Audit | L5641 | 12KB | 2 | ~0 | 17 |
| 36 | System Settings & Dashboard | L5798 | 13KB | 2 | ~2 | 22 |
| 37 | Plugin SDK | L5988 | 8KB | 2 | ~2 | 18 |
| 38 | Plugin API Contract | L6128 | 9KB | 2 | ~2 | 15 |
| 39 | Building & Packaging a Plugin | L6310 | 9KB | 3 | ~2 | 18 |
| 40 | Database Schema & Migrations | L6479 | 10KB | 2 | ~2 | 18 |
| 41 | Core Schema & Seed Data | L6633 | 11KB | 2 | ~3 | 19 |
| 42 | Migration History | L6794 | 14KB | 3 | ~4 | 17 |
| 43 | Internationalization & Localization | L6979 | 8KB | 2 | ~4 | 12 |
| 44 | Testing | L7133 | 9KB | 2 | ~1 | 17 |
| 45 | Backend Test Patterns | L7264 | 13KB | 2 | ~0 | 16 |
| 46 | Frontend Test Cases | L7438 | 9KB | 2 | ~4 | 9 |
| 47 | Glossary | L7602 | 13KB | 2 | ~4 | 18 |


## · MateClaw Overview  (L6)
  源文件: LICENSE, README.md, README_zh.md, assets/architecture-biz-en.svg, assets/architecture-biz-zh.svg, assets/architecture-tech-en.svg, assets/architecture-tech-zh.svg, assets/images/preview.png, mateclaw-server/src/main/java/vip/mate/memory/controller/DreamController.java, mateclaw-server/src/main/java/vip/mate/memory/fact/repository/FactMapper.java, mateclaw-server/src/main/java/vip/mate/memory/service/MorningCardService.java, mateclaw-server/src/main/resources/db/data-en.sql
  Architectural Pillars
    · 1. Multi-Provider Failover & Health Tracking
    · 2. LLM Wiki Knowledge Base
    · 3. Workspace Memory & Dreaming
    · 4. Tool & Skill Ecosystem
    · 5. Multi-Channel Delivery
  System Architecture & Code Mapping
    · Logic Flow: From User Intent to Execution
    · Provider & Memory Lifecycle
  Project Structure
  Map to Detailed Documentation

## · Getting Started & Deployment  (L159)
  源文件: .dockerignore, .env.example, docker-compose.yml, docker/searxng/Dockerfile, docker/searxng/settings.yml, mateclaw-server/Dockerfile, mateclaw-server/settings.xml, mateclaw-server/src/main/java/vip/mate/config/FlywayRepairConfig.java, mateclaw-server/src/main/java/vip/mate/llm/config/OllamaAutoDiscoveryRunner.java, mateclaw-server/src/main/java/vip/mate/system/service/SystemSettingService.java, mateclaw-server/src/main/java/vip/mate/tool/mcp/runtime/CwdAwareStdioClientTransport.java, mateclaw-server/src/main/resources/application-mysql.yml
  Deployment Architecture
    · System Components & Data Flow
    · Docker Compose Configuration
  Environment Configuration (.env)
    · Critical Variables
  Multi-Stage Dockerfile Implementation
    · Build Stages
  Database Initialization & Seeding
    · Flyway Migrations
    · Ollama Auto-Discovery
  SearXNG Sidecar Integration

## · Configuration Reference  (L321)
  源文件: .dockerignore, .env.example, docker-compose.yml, docker/searxng/Dockerfile, docker/searxng/settings.yml, mateclaw-server/Dockerfile, mateclaw-server/settings.xml, mateclaw-server/src/main/java/vip/mate/agent/graph/StateGraphReActAgent.java, mateclaw-server/src/main/java/vip/mate/agent/graph/node/SummarizingNode.java, mateclaw-server/src/main/java/vip/mate/agent/graph/observation/ObservationProcessor.java, mateclaw-server/src/main/java/vip/mate/agent/graph/plan/StateGraphPlanExecuteAgent.java, mateclaw-server/src/main/java/vip/mate/channel/web/ChatStreamTracker.java
  1. Agent Graph & Observation Budgets
    · 1.1 Observation Thresholds
    · 1.2 Tool Result Spill Store (RFC-008)
  2. LLM Provider & Failover Logic
    · 2.1 Health Tracker & Cooldown
  3. Conversation Window Management
  4. Module-Specific Namespaces
    · 4.1 mate.wiki (LLM Wiki Knowledge Base)
    · 4.2 mate.memory (Memory & Dreaming)
  5. Security & System Configuration
    · 5.1 System Settings (DB-backed)
    · 5.2 Key Security Properties
  6. Runtime State Tracking (SSE)

## · Core Agent Runtime  (L494)
  源文件: mateclaw-server/src/main/java/vip/mate/agent/AgentGraphBuilder.java, mateclaw-server/src/main/java/vip/mate/agent/AgentService.java, mateclaw-server/src/main/java/vip/mate/agent/BaseAgent.java, mateclaw-server/src/main/java/vip/mate/agent/ThinkingLevelHolder.java, mateclaw-server/src/main/java/vip/mate/agent/graph/NodeStreamingChatHelper.java, mateclaw-server/src/main/java/vip/mate/agent/graph/StateGraphReActAgent.java, mateclaw-server/src/main/java/vip/mate/agent/graph/executor/ToolExecutionExecutor.java, mateclaw-server/src/main/java/vip/mate/agent/graph/node/ReasoningNode.java, mateclaw-server/src/main/java/vip/mate/agent/graph/node/SummarizingNode.java, mateclaw-server/src/main/java/vip/mate/agent/graph/plan/StateGraphPlanExecuteAgent.java, mateclaw-server/src/main/java/vip/mate/agent/model/AgentEntity.java, mateclaw-server/src/main/java/vip/mate/channel/service/ChannelService.java
  Architectural Overview
    · Core Components Mapping
    · Natural Language to Code Entity Space
  StateGraph & Agent Patterns
  Streaming & SSE Delivery
  Tool Execution & Security
  Conversation & History Management
  Component Interaction Diagram

## · StateGraph & Agent Patterns  (L660)
  源文件: mateclaw-server/src/main/java/vip/mate/agent/AgentGraphBuilder.java, mateclaw-server/src/main/java/vip/mate/agent/BaseAgent.java, mateclaw-server/src/main/java/vip/mate/agent/GraphEventPublisher.java, mateclaw-server/src/main/java/vip/mate/agent/context/ConversationWindowManager.java, mateclaw-server/src/main/java/vip/mate/agent/context/RuntimeContextInjector.java, mateclaw-server/src/main/java/vip/mate/agent/graph/NodeStreamingChatHelper.java, mateclaw-server/src/main/java/vip/mate/agent/graph/RepetitionDetector.java, mateclaw-server/src/main/java/vip/mate/agent/graph/edge/ObservationDispatcher.java, mateclaw-server/src/main/java/vip/mate/agent/graph/edge/ReasoningDispatcher.java, mateclaw-server/src/main/java/vip/mate/agent/graph/executor/ToolExecutionExecutor.java, mateclaw-server/src/main/java/vip/mate/agent/graph/executor/ToolResultProperties.java, mateclaw-server/src/main/java/vip/mate/agent/graph/executor/ToolResultStorage.java
  Graph Assembly via AgentGraphBuilder
    · ReAct Graph Pattern
    · Plan-Execute Graph Pattern
  Node Types & Responsibilities
    · Reasoning & Action Flow
  State Management: Keys & Accessors
    · Key State Keys (`MateClawStateKeys`)
    · Accessors
  Safety & Limit Handling
    · Repetition Detection
    · Budget & Iteration Limits
    · Edge Dispatchers
  Streaming Integration

## · Streaming & SSE Delivery  (L845)
  源文件: mateclaw-server/src/main/java/vip/mate/agent/AgentGraphBuilder.java, mateclaw-server/src/main/java/vip/mate/agent/BaseAgent.java, mateclaw-server/src/main/java/vip/mate/agent/controller/AgentController.java, mateclaw-server/src/main/java/vip/mate/agent/graph/NodeStreamingChatHelper.java, mateclaw-server/src/main/java/vip/mate/agent/graph/StateGraphReActAgent.java, mateclaw-server/src/main/java/vip/mate/agent/graph/executor/ToolExecutionExecutor.java, mateclaw-server/src/main/java/vip/mate/agent/graph/node/ReasoningNode.java, mateclaw-server/src/main/java/vip/mate/agent/graph/node/SummarizingNode.java, mateclaw-server/src/main/java/vip/mate/agent/graph/plan/StateGraphPlanExecuteAgent.java, mateclaw-server/src/main/java/vip/mate/channel/web/ChatController.java, mateclaw-server/src/main/java/vip/mate/channel/web/ChatStreamTracker.java, mateclaw-server/src/main/java/vip/mate/channel/web/Utf8SseEmitter.java
  Architectural Overview
    · Key Components
  SSE Delivery Pipeline
    · Data Flow: Producer to Consumer
    · Natural Language to Code Entity Space: Streaming Lifecycle
  Buffer & Reconnection Management
  Interrupt & Queue Pipeline
    · State Transitions and Queuing
  Emergency Save & JVM Shutdown
  Event Types & StreamDelta

## · Tool Execution & Security  (L998)
  源文件: mateclaw-server/src/main/java/vip/mate/agent/AgentGraphBuilder.java, mateclaw-server/src/main/java/vip/mate/agent/BaseAgent.java, mateclaw-server/src/main/java/vip/mate/agent/graph/NodeStreamingChatHelper.java, mateclaw-server/src/main/java/vip/mate/agent/graph/executor/ToolExecutionExecutor.java, mateclaw-server/src/main/java/vip/mate/agent/graph/node/ReasoningNode.java, mateclaw-server/src/main/java/vip/mate/approval/ApprovalController.java, mateclaw-server/src/main/java/vip/mate/approval/ApprovalService.java, mateclaw-server/src/main/java/vip/mate/channel/web/ChatController.java, mateclaw-server/src/main/java/vip/mate/config/DatabaseBootstrapRunner.java, mateclaw-server/src/main/java/vip/mate/skill/runtime/SkillDependencyChecker.java, mateclaw-server/src/main/java/vip/mate/tool/ToolRegistry.java, mateclaw-server/src/main/java/vip/mate/tool/builtin/ReadFileTool.java
  ToolExecutionExecutor: Two-Phase Model
    · 1. Preparation Phase (Phase 1)
    · 2. Execution Phase (Phase 2)
  Security & Guard Evaluation
    · ToolGuard & Approval Flow
    · WorkspacePathGuard
  Tool Data Flow and Entity Mapping
    · Tool Execution Logic Mapping
  Oversized Results & Spill Store
  Registry & Concurrency Control
    · ToolRegistry
    · ConcurrencyUnsafe
    · Tool System Sequence

## · Conversation & History Management  (L1147)
  源文件: mateclaw-server/src/main/java/vip/mate/agent/context/ConversationWindowManager.java, mateclaw-server/src/main/java/vip/mate/agent/graph/RepetitionDetector.java, mateclaw-server/src/main/java/vip/mate/agent/graph/edge/ReasoningDispatcher.java, mateclaw-server/src/main/java/vip/mate/agent/graph/node/ObservationNode.java, mateclaw-server/src/main/java/vip/mate/config/WebSocketConfig.java, mateclaw-server/src/main/java/vip/mate/tool/builtin/DelegateAgentTool.java, mateclaw-server/src/main/java/vip/mate/tool/builtin/DelegationContext.java, mateclaw-server/src/main/java/vip/mate/workspace/conversation/ConversationService.java, mateclaw-server/src/main/java/vip/mate/workspace/conversation/controller/ConversationController.java, mateclaw-server/src/main/java/vip/mate/workspace/conversation/model/ConversationEntity.java, mateclaw-server/src/main/java/vip/mate/workspace/conversation/model/MessageContentPart.java, mateclaw-server/src/main/resources/db/migration/h2/V5__conversation_parent.sql
  Conversation Architecture
    · Key Entities
    · Data Flow: Message Persistence
    · Conversation Parent/Child Relationships
  Context Window Management (RFC-052)
    · Compression Pipeline
    · Token Budgeting Logic
    · Context Compression Flow
  Agent-to-Agent Delegation
    · Delegation Modes
    · Security & Recursion Control
    · Real-time Event Relay
  Message Content & Multimodal Injection
    · Content Part Types
    · Multimodal Data Flow
  Shared and System Conversations

## · LLM Provider Layer  (L1323)
  源文件: mateclaw-server/src/main/java/vip/mate/agent/chatmodel/AgentAnthropicChatModelBuilder.java, mateclaw-server/src/main/java/vip/mate/agent/chatmodel/AgentDashScopeChatModelBuilder.java, mateclaw-server/src/main/java/vip/mate/llm/cache/CachePlanContext.java, mateclaw-server/src/main/java/vip/mate/llm/model/ModelInfoDTO.java, mateclaw-server/src/main/java/vip/mate/llm/model/ModelProtocol.java, mateclaw-server/src/main/java/vip/mate/llm/model/ProviderInfoDTO.java, mateclaw-server/src/main/java/vip/mate/llm/service/ModelConfigService.java, mateclaw-server/src/main/java/vip/mate/llm/service/ModelDiscoveryService.java, mateclaw-server/src/main/java/vip/mate/llm/service/ModelProviderService.java, mateclaw-server/src/main/java/vip/mate/memory/event/MemoryWriteEvent.java, mateclaw-server/src/main/java/vip/mate/memory/service/SoulSummarizerService.java, mateclaw-server/src/main/java/vip/mate/memory/service/StructuredMemoryService.java
  System Architecture
    · Provider to Code Entity Mapping
  Provider Management & Failover
  ChatModel Builders & Decorators
    · Model Capability Resolution
  OAuth & Authentication Flows
  Database Schema & Migrations

## · Provider Management & Failover  (L1482)
  源文件: mateclaw-server/src/main/java/vip/mate/llm/config/OllamaAutoDiscoveryRunner.java, mateclaw-server/src/main/java/vip/mate/llm/failover/FallbackEntry.java, mateclaw-server/src/main/java/vip/mate/llm/failover/ProviderHealthProperties.java, mateclaw-server/src/main/java/vip/mate/llm/failover/ProviderHealthTracker.java, mateclaw-server/src/main/java/vip/mate/llm/failover/probe/AnthropicListModelsProbe.java, mateclaw-server/src/main/java/vip/mate/llm/failover/probe/DashScopeListModelsProbe.java, mateclaw-server/src/main/java/vip/mate/llm/failover/probe/OpenAiCompatibleListModelsProbe.java, mateclaw-server/src/main/java/vip/mate/llm/model/ModelInfoDTO.java, mateclaw-server/src/main/java/vip/mate/llm/model/ProviderConfigRequest.java, mateclaw-server/src/main/java/vip/mate/llm/service/ModelProviderService.java, mateclaw-server/src/main/resources/application-mysql.yml, mateclaw-server/src/main/resources/db/migration/h2/V14__embedding_model_config.sql
  Core Service Architecture
    · Provider Entity Relationships
  Failover & Health Tracking
    · ProviderHealthTracker Lifecycle
    · Health Probes
  Ollama Auto-Discovery
  Settings → Models UI
    · Key UI Components
  Implementation Details Table

## · ChatModel Builders & Decorators  (L1647)
  源文件: mateclaw-server/src/main/java/vip/mate/agent/chatmodel/AgentAnthropicChatModelBuilder.java, mateclaw-server/src/main/java/vip/mate/agent/chatmodel/AgentClaudeCodeChatModelBuilder.java, mateclaw-server/src/main/java/vip/mate/agent/chatmodel/AgentDashScopeChatModelBuilder.java, mateclaw-server/src/main/java/vip/mate/agent/chatmodel/AgentOpenAiCompatibleChatModelBuilder.java, mateclaw-server/src/main/java/vip/mate/agent/chatmodel/ClaudeCodeIdentityChatModelDecorator.java, mateclaw-server/src/main/java/vip/mate/agent/chatmodel/ClaudeCodeSystemArrayExchangeFilter.java, mateclaw-server/src/main/java/vip/mate/agent/chatmodel/ClaudeCodeSystemArrayInterceptor.java, mateclaw-server/src/main/java/vip/mate/agent/chatmodel/DeepSeekV4ThinkingDecorator.java, mateclaw-server/src/main/java/vip/mate/agent/chatmodel/RateLimitDiagnosticExchangeFilter.java, mateclaw-server/src/main/java/vip/mate/agent/chatmodel/RateLimitDiagnosticInterceptor.java, mateclaw-server/src/main/java/vip/mate/llm/anthropic/oauth/ClaudeCodeApiHeaders.java, mateclaw-server/src/main/java/vip/mate/llm/anthropic/oauth/ClaudeCodeTokenRefresher.java
  Architecture Overview
    · Model Resolution Flow
  Claude Code ChatModel Builder
    · OAuth & Header Masquerading
    · ClaudeCodeIdentityChatModelDecorator
  Anthropic & Thinking Mode
    · Thinking Budget Mapping
  DeepSeek V4 & OpenAI Compatibility
    · DeepSeekV4ThinkingDecorator
  Diagnostic Interceptors
    · RateLimitDiagnosticInterceptor
  Model Discovery & Protocol Filtering
    · DashScope Protocol Filtering

## · OAuth & Authentication Flows  (L1825)
  源文件: mateclaw-server/src/main/java/vip/mate/agent/chatmodel/AgentClaudeCodeChatModelBuilder.java, mateclaw-server/src/main/java/vip/mate/agent/chatmodel/AgentOpenAiCompatibleChatModelBuilder.java, mateclaw-server/src/main/java/vip/mate/agent/chatmodel/ClaudeCodeIdentityChatModelDecorator.java, mateclaw-server/src/main/java/vip/mate/agent/chatmodel/ClaudeCodeSystemArrayExchangeFilter.java, mateclaw-server/src/main/java/vip/mate/agent/chatmodel/ClaudeCodeSystemArrayInterceptor.java, mateclaw-server/src/main/java/vip/mate/agent/chatmodel/DeepSeekV4ThinkingDecorator.java, mateclaw-server/src/main/java/vip/mate/agent/chatmodel/RateLimitDiagnosticExchangeFilter.java, mateclaw-server/src/main/java/vip/mate/agent/chatmodel/RateLimitDiagnosticInterceptor.java, mateclaw-server/src/main/java/vip/mate/llm/anthropic/oauth/ClaudeCodeApiHeaders.java, mateclaw-server/src/main/java/vip/mate/llm/anthropic/oauth/ClaudeCodeCredentials.java, mateclaw-server/src/main/java/vip/mate/llm/anthropic/oauth/ClaudeCodeCredentialsReader.java, mateclaw-server/src/main/java/vip/mate/llm/anthropic/oauth/ClaudeCodeCredentialsWriter.java
  Claude Code OAuth Lifecycle
    · Authentication Service Stack
    · Identity Transformation
    · Claude Code Authentication Data Flow
  OpenAI OAuth Flow
    · Deployment Modes
  Rate-Limit Diagnostics
    · Failure Mode Classification
  System Array Interceptors
    · Request Entity Mapping

## · Chat UI & Frontend Architecture  (L1967)
  源文件: .gitignore, mateclaw-server/src/main/java/vip/mate/config/LoginRateLimitFilter.java, mateclaw-server/src/main/java/vip/mate/config/WebSocketConfig.java, mateclaw-server/src/main/java/vip/mate/tool/builtin/DatasourceTool.java, mateclaw-server/src/main/java/vip/mate/workspace/conversation/ConversationService.java, mateclaw-ui/index.html, mateclaw-ui/src/components/chat/ChatInput.vue, mateclaw-ui/src/components/workspace/WorkspaceSwitcher.vue, mateclaw-ui/src/composables/chat/useChat.ts, mateclaw-ui/src/main.ts, mateclaw-ui/src/router/index.ts, mateclaw-ui/src/views/ChatConsole.vue
  Main Layout & Routing
    · Core Routing Structure
    · Workspace Switcher
  Frontend Architecture Overview
    · UI to Code Entity Mapping
    · Component Hierarchy
  Chat Console & Logic Core
    · Unified Chat Composable (`useChat`)
  Message Rendering & Components
    · Interaction Elements
  Child Pages

## · Chat Console & Streaming Client  (L2111)
  源文件: mateclaw-server/src/main/java/vip/mate/channel/ChannelMessageRouter.java, mateclaw-server/src/main/java/vip/mate/config/WebSocketConfig.java, mateclaw-server/src/main/java/vip/mate/llm/chatgpt/ChatGPTChatModel.java, mateclaw-server/src/main/java/vip/mate/llm/chatgpt/ChatGPTResponsesClient.java, mateclaw-server/src/main/java/vip/mate/tool/builtin/DelegateAgentTool.java, mateclaw-server/src/main/java/vip/mate/tool/builtin/DelegationContext.java, mateclaw-server/src/main/java/vip/mate/workspace/conversation/ConversationService.java, mateclaw-server/src/main/java/vip/mate/workspace/conversation/model/ConversationEntity.java, mateclaw-server/src/main/java/vip/mate/workspace/conversation/model/MessageContentPart.java, mateclaw-server/src/main/resources/db/migration/h2/V5__conversation_parent.sql, mateclaw-ui/src/components/chat/ChatInput.vue, mateclaw-ui/src/components/chat/ToolCallSegment.vue
  ChatConsole.vue Hydration & Polling
    · Route Hydration
    · Conversation Polling
  useChat Composable: Stream Lifecycle
    · Turn ID & Stale Event Guard
    · Key Functions
    · Chat Streaming Lifecycle
  useStream: Low-Level SSE Parsing
    · SSEParser Implementation
  Message Queue & Interrupt Logic
    · State Dispatching
  Attachments & Blob Previews
    · Upload Flow
  Message Reconcile: Local vs. Remote
    · Richness Scoring

## · Message Rendering & Components  (L2295)
  源文件: mateclaw-server/src/main/java/vip/mate/agent/graph/plan/node/DirectAnswerNode.java, mateclaw-ui/TEST_CASES.md, mateclaw-ui/pnpm-lock.yaml, mateclaw-ui/src/assets/main.css, mateclaw-ui/src/components/chat/BrowserTimeline.vue, mateclaw-ui/src/components/chat/CompressionSummary.vue, mateclaw-ui/src/components/chat/MessageBubble.vue, mateclaw-ui/src/components/chat/MessageList.vue, mateclaw-ui/src/components/chat/ModelSelector.vue, mateclaw-ui/src/components/chat/PlanStepsPanel.vue, mateclaw-ui/src/components/chat/ThinkingSegment.vue, mateclaw-ui/src/components/chat/UserMessageContent.vue
  Message Segmented View
    · Implementation & Data Flow
    · Specialized UI Panels
  Markdown Rendering Pipeline
    · Key Features
  Chat Interaction Components
    · ChatInput & Approval Bar
    · MessageList & Auto-Scroll
    · Model Selector

## · LLM Wiki Knowledge Base  (L2442)
  源文件: mateclaw-server/src/main/java/vip/mate/wiki/WikiAutoConfiguration.java, mateclaw-server/src/main/java/vip/mate/wiki/controller/WikiController.java, mateclaw-server/src/main/java/vip/mate/wiki/dto/WikiPageLite.java, mateclaw-server/src/main/java/vip/mate/wiki/event/WikiProcessingListener.java, mateclaw-server/src/main/java/vip/mate/wiki/model/WikiPageEntity.java, mateclaw-server/src/main/java/vip/mate/wiki/model/WikiRawMaterialEntity.java, mateclaw-server/src/main/java/vip/mate/wiki/repository/WikiPageMapper.java, mateclaw-server/src/main/java/vip/mate/wiki/service/HybridRetriever.java, mateclaw-server/src/main/java/vip/mate/wiki/service/WikiContextService.java, mateclaw-server/src/main/java/vip/mate/wiki/service/WikiKnowledgeBaseService.java, mateclaw-server/src/main/java/vip/mate/wiki/service/WikiRawMaterialService.java, mateclaw-server/src/main/java/vip/mate/wiki/service/WikiRelationService.java
  Module Architecture
    · Knowledge Flow Diagram
  Ingestion & Transformation
  Retrieval & Agent Integration
    · Retrieval Integration Diagram
  Wiki User Interface

## · Ingestion Pipeline  (L2584)
  源文件: mateclaw-server/src/main/java/vip/mate/wiki/WikiProperties.java, mateclaw-server/src/main/java/vip/mate/wiki/dto/GeneratedPage.java, mateclaw-server/src/main/java/vip/mate/wiki/dto/RouteResult.java, mateclaw-server/src/main/java/vip/mate/wiki/dto/RoutedPageMeta.java, mateclaw-server/src/main/java/vip/mate/wiki/dto/WikiChunkDraft.java, mateclaw-server/src/main/java/vip/mate/wiki/job/WikiKbConfig.java, mateclaw-server/src/main/java/vip/mate/wiki/job/WikiModelRoutingService.java, mateclaw-server/src/main/java/vip/mate/wiki/job/strategy/GlobalDefaultStepModelStrategy.java, mateclaw-server/src/main/java/vip/mate/wiki/job/strategy/KbDefaultModelStrategy.java, mateclaw-server/src/main/java/vip/mate/wiki/model/WikiChunkEntity.java, mateclaw-server/src/main/java/vip/mate/wiki/service/DocumentPreprocessService.java, mateclaw-server/src/main/java/vip/mate/wiki/service/WikiBatchCreateParser.java
  Core Architecture & Data Flow
    · High-Level Ingestion Flow
    · Data Flow Diagram
  Two-Phase Digest Strategy
    · Phase A: Route
    · Phase B: Merge / BatchCreate
    · Class Association Diagram
  Slug & Identity Management
  LLM Resilience and Retries
  Progress Tracking & SSE Events

## · Wiki Pages, Retrieval & Enrichment  (L2766)
  源文件: mateclaw-server/src/main/java/vip/mate/llm/controller/ModelConfigController.java, mateclaw-server/src/main/java/vip/mate/llm/embedding/EmbeddingModelFactory.java, mateclaw-server/src/main/java/vip/mate/llm/model/EmbeddingProtocol.java, mateclaw-server/src/main/java/vip/mate/llm/model/ModelConfigEntity.java, mateclaw-server/src/main/java/vip/mate/wiki/WikiProperties.java, mateclaw-server/src/main/java/vip/mate/wiki/controller/WikiAdminController.java, mateclaw-server/src/main/java/vip/mate/wiki/dto/EnrichmentBatchPlan.java, mateclaw-server/src/main/java/vip/mate/wiki/dto/EnrichmentPlan.java, mateclaw-server/src/main/java/vip/mate/wiki/dto/EnrichmentReplacement.java, mateclaw-server/src/main/java/vip/mate/wiki/dto/PageCitationWithRaw.java, mateclaw-server/src/main/java/vip/mate/wiki/dto/WikiPageLite.java, mateclaw-server/src/main/java/vip/mate/wiki/event/WikiKbDirtyEvent.java
  Wiki Page Lifecycle & Service
    · Key Implementation Details
    · Wiki Page State Transitions
  Retrieval & Vector Indexing
    · Hybrid Search Modes
    · Vector Indexing Pipeline
  Enrichment & Scaffold Services
    · WikiLink Enrichment
    · System Scaffold Pages
    · On-Demand Compilation
  Agent Interface: WikiTool

## · Wiki UI  (L2938)
  源文件: mateclaw-server/src/main/java/vip/mate/wiki/WikiAutoConfiguration.java, mateclaw-server/src/main/java/vip/mate/wiki/controller/WikiController.java, mateclaw-server/src/main/java/vip/mate/wiki/event/WikiProcessingListener.java, mateclaw-server/src/main/java/vip/mate/wiki/job/WikiProcessingJobService.java, mateclaw-server/src/main/java/vip/mate/wiki/model/WikiRawMaterialEntity.java, mateclaw-server/src/main/java/vip/mate/wiki/service/WikiContextService.java, mateclaw-server/src/main/java/vip/mate/wiki/service/WikiRawMaterialService.java, mateclaw-server/src/main/resources/db/migration/h2/V7__wiki_last_processed_hash.sql, mateclaw-server/src/main/resources/db/migration/h2/V8__wiki_raw_progress.sql, mateclaw-server/src/main/resources/prompts/wiki/batch-create-system.txt, mateclaw-server/src/main/resources/prompts/wiki/batch-create-user.txt, mateclaw-server/src/main/resources/prompts/wiki/create-page-system.txt
  Wiki Index Layout
    · Component Structure
    · Page Grouping and Protection
  WikiPageViewer and Content Rendering
    · Knowledge Enrichment and Repair
    · Wiki-Link Resolution
    · Data Flow: Page Viewer
  RawMaterialPanel: Ingestion & SSE Tracking
    · Upload Pipeline and Progress
    · Job Stage Tracking
    · Ingestion Flow: Material to Wiki Page
  WikiConfig and Knowledge Base Settings
    · Knowledge Base Configuration
    · Auto-Processing
  WikiGraphView and State Management
    · Knowledge Graph Visualization
    · useWikiStore
    · Code Entity Mapping

## · Memory & Dreaming System  (L3134)
  源文件: README.md, README_zh.md, assets/images/preview.png, mateclaw-server/src/main/java/vip/mate/memory/MemoryProperties.java, mateclaw-server/src/main/java/vip/mate/memory/archive/MemoryArchiveService.java, mateclaw-server/src/main/java/vip/mate/memory/controller/DreamController.java, mateclaw-server/src/main/java/vip/mate/memory/controller/MemoryController.java, mateclaw-server/src/main/java/vip/mate/memory/fact/controller/FactController.java, mateclaw-server/src/main/java/vip/mate/memory/fact/repository/FactMapper.java, mateclaw-server/src/main/java/vip/mate/memory/model/DreamReportEntity.java, mateclaw-server/src/main/java/vip/mate/memory/model/MemoryRecallEntity.java, mateclaw-server/src/main/java/vip/mate/memory/repository/DreamReportMapper.java
    · Memory Architecture Overview
  6.1 Memory Lifecycle & Dreaming
  6.2 Fact Extraction & Structured Memory
  6.3 Memory UI (Morning Card & Browser)

## · Memory Lifecycle & Dreaming  (L3298)
  源文件: mateclaw-server/src/main/java/vip/mate/memory/archive/MemoryArchiveService.java, mateclaw-server/src/main/java/vip/mate/memory/controller/MemoryController.java, mateclaw-server/src/main/java/vip/mate/memory/lifecycle/MemoryLifecycleEventListener.java, mateclaw-server/src/main/java/vip/mate/memory/lifecycle/MemoryLifecycleMediator.java, mateclaw-server/src/main/java/vip/mate/memory/lifecycle/TurnCompletedEvent.java, mateclaw-server/src/main/java/vip/mate/memory/lifecycle/TurnContext.java, mateclaw-server/src/main/java/vip/mate/memory/lifecycle/TurnStartedEvent.java, mateclaw-server/src/main/java/vip/mate/memory/listener/PostConversationMemoryListener.java, mateclaw-server/src/main/java/vip/mate/memory/model/DreamReportEntity.java, mateclaw-server/src/main/java/vip/mate/memory/model/MemoryRecallEntity.java, mateclaw-server/src/main/java/vip/mate/memory/model/MorningCardSeenEntity.java, mateclaw-server/src/main/java/vip/mate/memory/nudge/MemoryNudgeService.java
  Memory Lifecycle Mediator
    · Turn Lifecycle Events
    · Data Flow: Turn Execution
  Memory Recall & Scoring
    · Scoring Algorithm
    · Snippet-Level Tracking
  Dreaming & Emergence
    · Dreaming Modes
    · Consolidation Workflow
  Memory Nudge & Extraction
  Memory Archiving & UI
    · Key Entities

## · Fact Extraction & Structured Memory  (L3471)
  源文件: mateclaw-server/src/main/java/vip/mate/agent/chatmodel/AgentDashScopeChatModelBuilder.java, mateclaw-server/src/main/java/vip/mate/llm/model/ProviderInfoDTO.java, mateclaw-server/src/main/java/vip/mate/llm/service/ModelConfigService.java, mateclaw-server/src/main/java/vip/mate/memory/event/MemoryWriteEvent.java, mateclaw-server/src/main/java/vip/mate/memory/fact/contradiction/ContradictionDetector.java, mateclaw-server/src/main/java/vip/mate/memory/fact/extraction/CompositeEntityExtractor.java, mateclaw-server/src/main/java/vip/mate/memory/fact/extraction/EntityExtractor.java, mateclaw-server/src/main/java/vip/mate/memory/fact/extraction/ExtractedFact.java, mateclaw-server/src/main/java/vip/mate/memory/fact/extraction/LlmEntityExtractor.java, mateclaw-server/src/main/java/vip/mate/memory/fact/extraction/PatternEntityExtractor.java, mateclaw-server/src/main/java/vip/mate/memory/fact/model/FactContradictionEntity.java, mateclaw-server/src/main/java/vip/mate/memory/fact/model/FactEntity.java
  Structured Memory Architecture
    · Core Workspace Files
    · Data Flow: Memory Write to System Prompt
  Fact Extraction & Projection
    · Extraction Pipeline
    · Fact Trust & Decay
  Contradiction Detection
  Memory Retrieval Services
    · FactQueryService & Tool
    · SessionSearchService
    · SoulSummarizerService
  Technical Entity Mapping
  Memory Nudging

## · Memory UI (Morning Card & Browser)  (L3657)
  源文件: README.md, README_zh.md, assets/images/preview.png, mateclaw-server/src/main/java/vip/mate/agent/controller/AgentController.java, mateclaw-server/src/main/java/vip/mate/channel/web/Utf8SseEmitter.java, mateclaw-server/src/main/java/vip/mate/channel/webchat/WebChatController.java, mateclaw-server/src/main/java/vip/mate/memory/MemoryProperties.java, mateclaw-server/src/main/java/vip/mate/memory/controller/DreamController.java, mateclaw-server/src/main/java/vip/mate/memory/controller/DreamEventBroadcaster.java, mateclaw-server/src/main/java/vip/mate/memory/event/DreamCompletedEvent.java, mateclaw-server/src/main/java/vip/mate/memory/event/DreamFailedEvent.java, mateclaw-server/src/main/java/vip/mate/memory/fact/controller/FactController.java
  Memory Workspace Overview
    · Data Flow: Memory & Dreaming UI
  1. Dream Timeline & useMemoryStore
    · Backend: DreamController & Events
    · Frontend: useMemoryStore
  2. Morning Card (Briefing Component)
  3. Memory Browser & Workspace Files
    · Section Parsing & H2 Headers
    · Fact Management
  4. Technical Implementation Detail
    · REST API Endpoints
    · Code Mapping: Frontend to Backend

## · Tools & Skills  (L3837)
  源文件: mateclaw-server/src/main/java/vip/mate/MateClawApplication.java, mateclaw-server/src/main/java/vip/mate/skill/controller/SkillController.java, mateclaw-server/src/main/java/vip/mate/skill/installer/BuiltinSkillSeedService.java, mateclaw-server/src/main/java/vip/mate/skill/model/SkillEntity.java, mateclaw-server/src/main/java/vip/mate/skill/runtime/SkillDependencyChecker.java, mateclaw-server/src/main/java/vip/mate/skill/runtime/SkillPackageResolver.java, mateclaw-server/src/main/java/vip/mate/skill/runtime/SkillRuntimeService.java, mateclaw-server/src/main/java/vip/mate/skill/service/SkillService.java, mateclaw-server/src/main/java/vip/mate/tool/ToolRegistry.java, mateclaw-server/src/main/resources/db/data-en.sql, mateclaw-server/src/main/resources/db/data-mysql-en.sql, mateclaw-server/src/main/resources/db/data-mysql-zh.sql
    · Tool Ecosystem Overview
    · [Built-in Tools](#7.1)
    · [Skill System](#7.2)
    · [MCP (Model Context Protocol) Integration](#7.3)
    · [Media Generation Tools](#7.4)
    · Dependency & Security Workflow

## · Built-in Tools  (L3997)
  源文件: mateclaw-server/pom.xml, mateclaw-server/src/main/java/vip/mate/approval/ApprovalController.java, mateclaw-server/src/main/java/vip/mate/approval/ApprovalService.java, mateclaw-server/src/main/java/vip/mate/config/DatabaseBootstrapRunner.java, mateclaw-server/src/main/java/vip/mate/datasource/controller/DatasourceController.java, mateclaw-server/src/main/java/vip/mate/datasource/model/DatasourceEntity.java, mateclaw-server/src/main/java/vip/mate/datasource/repository/DatasourceMapper.java, mateclaw-server/src/main/java/vip/mate/datasource/service/DatasourceConnectionManager.java, mateclaw-server/src/main/java/vip/mate/datasource/service/DatasourceService.java, mateclaw-server/src/main/java/vip/mate/datasource/service/EChartsOptionBuilder.java, mateclaw-server/src/main/java/vip/mate/datasource/service/SqlValidationService.java, mateclaw-server/src/main/java/vip/mate/skill/workspace/SkillWorkspaceBootstrapRunner.java
  1. Execution & Automation Tools
    · ShellExecuteTool
    · BrowserUseTool
  2. Information Retrieval Tools
    · WebSearchTool
    · DocumentExtractTool
  3. Data & Workspace Tools
    · SqlQueryTool & DatasourceTool
    · DocxRenderTool
  4. Agentic & System Tools
    · DelegateAgentTool
    · Iteration Control

## · Skill System  (L4199)
  源文件: mateclaw-server/src/main/java/vip/mate/MateClawApplication.java, mateclaw-server/src/main/java/vip/mate/agent/binding/model/AgentSkillBinding.java, mateclaw-server/src/main/java/vip/mate/agent/binding/model/AgentToolBinding.java, mateclaw-server/src/main/java/vip/mate/agent/binding/repository/AgentSkillBindingMapper.java, mateclaw-server/src/main/java/vip/mate/agent/binding/repository/AgentToolBindingMapper.java, mateclaw-server/src/main/java/vip/mate/agent/binding/service/AgentBindingService.java, mateclaw-server/src/main/java/vip/mate/audit/controller/AuditEventController.java, mateclaw-server/src/main/java/vip/mate/skill/controller/SkillController.java, mateclaw-server/src/main/java/vip/mate/skill/controller/SkillInstallController.java, mateclaw-server/src/main/java/vip/mate/skill/installer/BuiltinSkillSeedService.java, mateclaw-server/src/main/java/vip/mate/skill/installer/SkillInstaller.java, mateclaw-server/src/main/java/vip/mate/skill/installer/ZipSkillFetcher.java
  Skill Packaging (SKILL.md)
    · Structure of a Skill Package
    · Data Flow: Skill to Prompt
  Core Services
    · SkillService & SkillEntity
    · SkillRuntimeService
    · SkillPackageResolver & DependencyChecker
  Installation and Seeding
    · BuiltinSkillSeedService
    · SkillInstaller & ZipSkillFetcher
  AI Skill Synthesis
    · Synthesis Pipeline
    · Skill Synthesis Data Flow
  Agent-Skill Bindings
    · Runtime Tool Resolution

## · MCP (Model Context Protocol) Integration  (L4388)
  源文件: mateclaw-server/src/main/java/vip/mate/config/FlywayRepairConfig.java, mateclaw-server/src/main/java/vip/mate/tool/mcp/runtime/CwdAwareStdioClientTransport.java, mateclaw-server/src/main/java/vip/mate/tool/mcp/runtime/McpReturnDirectProperties.java, mateclaw-server/src/main/java/vip/mate/tool/mcp/runtime/McpToolCallbackProvider.java, mateclaw-server/src/main/java/vip/mate/tool/mcp/runtime/ReturnDirectMcpToolCallback.java, mateclaw-server/src/main/resources/db/migration/h2/V2__workspace_base_path.sql
  Architectural Overview
    · MCP Component Interaction
  Transport Modes
    · CwdAwareStdioClientTransport
  Tool Callback Management
    · McpToolCallbackProvider
    · Return Direct Optimization (RFC-052)
  Implementation Detail: Tool Execution Data Flow
  Claude Code Integration & Tool Prefixing
  Configuration

## · Media Generation Tools  (L4546)
  源文件: mateclaw-server/pom.xml, mateclaw-server/src/main/java/vip/mate/stt/AudioMimeTypes.java, mateclaw-server/src/main/java/vip/mate/stt/SttProvider.java, mateclaw-server/src/main/java/vip/mate/stt/SttProviderRegistry.java, mateclaw-server/src/main/java/vip/mate/stt/SttService.java, mateclaw-server/src/main/java/vip/mate/stt/WavPcmExtractor.java, mateclaw-server/src/main/java/vip/mate/stt/provider/DashScopeSttProvider.java, mateclaw-server/src/main/java/vip/mate/stt/provider/OpenAiSttProvider.java, mateclaw-server/src/main/java/vip/mate/system/model/SystemSettingsDTO.java, mateclaw-server/src/main/java/vip/mate/tool/builtin/DocumentExtractTool.java, mateclaw-server/src/main/java/vip/mate/tool/builtin/DocxRenderTool.java, mateclaw-server/src/main/java/vip/mate/tool/builtin/TikaExtractor.java
  Image Generation
    · Providers and Implementation
    · Data Flow: Text to Image
  Video Generation
    · MiniMaxVideoProvider
  Audio Processing (TTS & STT)
    · Text-to-Speech (TtsService)
    · Speech-to-Text (SttService)
  Document and File Utilities
    · DocxRenderTool
    · DocumentExtractTool
  File Delivery and Caching
    · GeneratedFileCache
  System Settings

## · Channels & Multi-Surface Delivery  (L4712)
  源文件: mateclaw-server/src/main/java/vip/mate/agent/AgentService.java, mateclaw-server/src/main/java/vip/mate/agent/ThinkingLevelHolder.java, mateclaw-server/src/main/java/vip/mate/agent/binding/controller/AgentBindingController.java, mateclaw-server/src/main/java/vip/mate/agent/model/AgentEntity.java, mateclaw-server/src/main/java/vip/mate/audit/service/AuditEventService.java, mateclaw-server/src/main/java/vip/mate/channel/AbstractChannelAdapter.java, mateclaw-server/src/main/java/vip/mate/channel/ChannelHealthMonitor.java, mateclaw-server/src/main/java/vip/mate/channel/ChannelManager.java, mateclaw-server/src/main/java/vip/mate/channel/controller/ChannelController.java, mateclaw-server/src/main/java/vip/mate/channel/service/ChannelService.java, mateclaw-server/src/main/java/vip/mate/channel/wecom/WeComImageCompressor.java, mateclaw-server/src/main/java/vip/mate/channel/weixin/WeixinAesUtil.java
  Channel Framework
    · Channel Lifecycle & Routing
  IM Channel Adapters
    · Adapter Connectivity Modes
  WebChat Widget & Talk Mode
  Data Schema Reference

## · Channel Framework  (L4871)
  源文件: mateclaw-server/src/main/java/vip/mate/agent/binding/controller/AgentBindingController.java, mateclaw-server/src/main/java/vip/mate/audit/service/AuditEventService.java, mateclaw-server/src/main/java/vip/mate/channel/AbstractChannelAdapter.java, mateclaw-server/src/main/java/vip/mate/channel/ChannelHealthMonitor.java, mateclaw-server/src/main/java/vip/mate/channel/ChannelManager.java, mateclaw-server/src/main/java/vip/mate/channel/ChannelMessageRouter.java, mateclaw-server/src/main/java/vip/mate/channel/controller/ChannelController.java, mateclaw-server/src/main/java/vip/mate/channel/wecom/WeComImageCompressor.java, mateclaw-server/src/main/java/vip/mate/channel/weixin/WeixinAesUtil.java, mateclaw-server/src/main/java/vip/mate/dashboard/controller/DashboardController.java, mateclaw-server/src/main/java/vip/mate/dashboard/service/CronJobRunService.java, mateclaw-server/src/main/java/vip/mate/dashboard/service/DashboardService.java
  Core Architecture
    · Component Overview Diagram
    · Data Flow: Inbound Message to Agent
  Channel Lifecycle & Management
    · ChannelManager
    · Connection Resilience
  Adapter Implementation
    · AbstractChannelAdapter
    · Connection Modes
  UI and Frontend Reconciliation
    · Channels.vue
    · Message Reconciliation

## · IM Channel Adapters  (L5017)
  源文件: mateclaw-server/src/main/java/vip/mate/channel/ChannelMessage.java, mateclaw-server/src/main/java/vip/mate/channel/feishu/FeishuChannelAdapter.java, mateclaw-server/src/main/java/vip/mate/channel/telegram/TelegramChannelAdapter.java, mateclaw-server/src/main/java/vip/mate/channel/wecom/WeComChannelAdapter.java, mateclaw-server/src/main/java/vip/mate/channel/weixin/ILinkClient.java, mateclaw-server/src/main/java/vip/mate/channel/weixin/WeixinChannelAdapter.java, mateclaw-server/src/main/java/vip/mate/common/security/SecretEquals.java, mateclaw-server/src/main/java/vip/mate/exception/GlobalExceptionHandler.java, mateclaw-server/src/main/java/vip/mate/tool/builtin/CronJobTool.java, mateclaw-server/src/main/java/vip/mate/tool/guard/DefaultToolGuard.java, mateclaw-server/src/main/java/vip/mate/tts/TtsService.java, mateclaw-server/src/main/resources/db/migration/h2/V3__register_cron_job_tool.sql
  Overview of Adapter Architecture
    · Data Flow: Platform to Agent
  Specific Adapter Implementations
    · WeixinChannelAdapter (WeChat Personal)
    · WeComChannelAdapter (Enterprise WeChat)
    · FeishuChannelAdapter
    · TelegramChannelAdapter
  Security and Integration Components
    · Timing-Safe Comparison
    · TtsService Integration
  Configuration Reference

## · WebChat Widget & Talk Mode  (L5180)
  源文件: mateclaw-server/src/main/java/vip/mate/agent/controller/AgentController.java, mateclaw-server/src/main/java/vip/mate/channel/web/TalkModeWebSocketHandler.java, mateclaw-server/src/main/java/vip/mate/channel/web/Utf8SseEmitter.java, mateclaw-server/src/main/java/vip/mate/channel/webchat/WebChatController.java, mateclaw-server/src/main/java/vip/mate/config/WebSocketConfig.java, mateclaw-server/src/main/java/vip/mate/memory/controller/DreamEventBroadcaster.java, mateclaw-server/src/main/java/vip/mate/memory/event/DreamCompletedEvent.java, mateclaw-server/src/main/java/vip/mate/memory/event/DreamFailedEvent.java, mateclaw-server/src/main/java/vip/mate/wiki/controller/WikiResearchController.java, mateclaw-server/src/main/java/vip/mate/wiki/repository/WikiChunkMapper.java, mateclaw-server/src/main/java/vip/mate/workspace/conversation/ConversationService.java, mateclaw-ui/src/components/chat/ChatInput.vue
  WebChat Widget
    · WebChat Backend Controller
    · WebChat Data Flow
  Talk Mode
    · TalkModeWebSocketHandler
    · Buffer Configuration
    · Talk Mode Frontend Component
  Implementation Details
    · SSE Encoding Safety
    · Persistence & Events
    · Interface Comparison

## · Security, Workspaces & Administration  (L5324)
  源文件: mateclaw-server/src/main/java/vip/mate/agent/AgentService.java, mateclaw-server/src/main/java/vip/mate/agent/ThinkingLevelHolder.java, mateclaw-server/src/main/java/vip/mate/agent/model/AgentEntity.java, mateclaw-server/src/main/java/vip/mate/auth/controller/AuthController.java, mateclaw-server/src/main/java/vip/mate/auth/model/LoginResponse.java, mateclaw-server/src/main/java/vip/mate/auth/service/AuthService.java, mateclaw-server/src/main/java/vip/mate/channel/service/ChannelService.java, mateclaw-server/src/main/java/vip/mate/config/SecurityConfig.java, mateclaw-server/src/main/java/vip/mate/config/SpaForwardController.java, mateclaw-server/src/main/java/vip/mate/cron/service/CronJobService.java, mateclaw-server/src/main/java/vip/mate/exception/MateClawException.java, mateclaw-server/src/main/java/vip/mate/memory/event/ConversationCompletionPublisher.java
  Security & Isolation Architecture
    · Logical Security Model
  Authentication & RBAC
  Tool Guard & Audit
  System Settings & Dashboard
    · Administrative Surface Overview
  Child Pages

## · Authentication & RBAC  (L5475)
  源文件: .gitignore, mateclaw-server/src/main/java/vip/mate/agent/graph/observation/ObservationProcessor.java, mateclaw-server/src/main/java/vip/mate/auth/controller/AuthController.java, mateclaw-server/src/main/java/vip/mate/auth/model/LoginResponse.java, mateclaw-server/src/main/java/vip/mate/auth/service/AuthService.java, mateclaw-server/src/main/java/vip/mate/config/LoginRateLimitFilter.java, mateclaw-server/src/main/java/vip/mate/config/SecurityConfig.java, mateclaw-server/src/main/java/vip/mate/config/SecurityStartupValidator.java, mateclaw-server/src/main/java/vip/mate/config/SpaForwardController.java, mateclaw-server/src/main/java/vip/mate/config/ToolTimeoutProperties.java, mateclaw-server/src/main/java/vip/mate/config/WebMvcConfig.java, mateclaw-server/src/main/java/vip/mate/tool/builtin/DatasourceTool.java
  Authentication & JWT Lifecycle
    · Key Components
    · Authentication Data Flow
  Workspace-Based RBAC
    · Workspace Roles
    · Implementation Logic
  User & Member Management UI
    · Members Management
    · Password Security
  Security Configuration & Startup
    · SecurityFilterChain
    · SPA Routing

## · Tool Guard & Audit  (L5641)
  源文件: mateclaw-server/src/main/java/vip/mate/agent/binding/model/AgentSkillBinding.java, mateclaw-server/src/main/java/vip/mate/agent/binding/model/AgentToolBinding.java, mateclaw-server/src/main/java/vip/mate/agent/binding/repository/AgentSkillBindingMapper.java, mateclaw-server/src/main/java/vip/mate/agent/binding/repository/AgentToolBindingMapper.java, mateclaw-server/src/main/java/vip/mate/agent/binding/service/AgentBindingService.java, mateclaw-server/src/main/java/vip/mate/approval/ApprovalController.java, mateclaw-server/src/main/java/vip/mate/approval/ApprovalService.java, mateclaw-server/src/main/java/vip/mate/audit/controller/AuditEventController.java, mateclaw-server/src/main/java/vip/mate/config/DatabaseBootstrapRunner.java, mateclaw-server/src/main/java/vip/mate/exception/GlobalExceptionHandler.java, mateclaw-server/src/main/java/vip/mate/tool/builtin/CronJobTool.java, mateclaw-server/src/main/java/vip/mate/tool/builtin/ShellExecuteTool.java
  Evaluation Pipeline
    · Decision Matrix
    · Data Flow Diagram: Tool Guard Evaluation
  ShellCommandGuardian & Pattern Matching
    · GuardFinding Severity Levels
    · Implementation Details
  Tool Guard Configuration & Seeding
    · ToolGuardRuleSeedService
    · Config Entities
  Audit & Event Logging
    · AuditEventService & AuditEventController
    · Data Flow: Audit Logging
  Tool Guard UI & User Approval
    · Approval Flow
    · Decision Localization

## · System Settings & Dashboard  (L5798)
  源文件: .dockerignore, .env.example, docker-compose.yml, docker/searxng/Dockerfile, docker/searxng/settings.yml, mateclaw-server/Dockerfile, mateclaw-server/settings.xml, mateclaw-server/src/main/java/vip/mate/agent/binding/controller/AgentBindingController.java, mateclaw-server/src/main/java/vip/mate/audit/service/AuditEventService.java, mateclaw-server/src/main/java/vip/mate/channel/controller/ChannelController.java, mateclaw-server/src/main/java/vip/mate/dashboard/controller/DashboardController.java, mateclaw-server/src/main/java/vip/mate/dashboard/service/CronJobRunService.java
  System Configuration Management
    · SystemSettingService & SystemSettingsDTO
  System Health & Diagnostics
    · Health Check Pipeline
    · Browser Diagnostics (DoctorDrawer)
    · System Health Data Flow
  Dashboard & Resource Monitoring
    · DashboardService & Controller
    · CronJobRunService
    · Channel Management
    · Administrative Logic Flow
  Browser Tool Infrastructure
    · Lifecycle & Performance
    · Browser Properties

## · Plugin SDK  (L5988)
  源文件: mateclaw-server/src/main/java/vip/mate/MateClawApplication.java, mateclaw-server/src/main/java/vip/mate/skill/controller/SkillController.java, mateclaw-server/src/main/java/vip/mate/skill/installer/BuiltinSkillSeedService.java, mateclaw-server/src/main/java/vip/mate/skill/model/SkillEntity.java, mateclaw-server/src/main/java/vip/mate/skill/runtime/SkillPackageResolver.java, mateclaw-server/src/main/java/vip/mate/skill/runtime/SkillRuntimeService.java, mateclaw-server/src/main/java/vip/mate/skill/service/SkillService.java, mateclaw-server/src/main/resources/db/migration/h2/V1__baseline_schema.sql, mateclaw-server/src/main/resources/db/migration/h2/V32__bailian_team_provider.sql, mateclaw-server/src/main/resources/db/migration/h2/V33__expand_api_key_column.sql, mateclaw-server/src/main/resources/db/migration/h2/V34__siliconflow_opencode_providers.sql, mateclaw-server/src/main/resources/db/migration/mysql/V1__baseline_schema.sql
    · Core Architecture
    · Plugin Manifest (`mateclaw-plugin.json`)
    · Extension Capabilities
    · Development Workflow
    · Child Pages

## · Plugin API Contract  (L6128)
  源文件: mateclaw-server/src/main/java/vip/mate/agent/AgentService.java, mateclaw-server/src/main/java/vip/mate/agent/ThinkingLevelHolder.java, mateclaw-server/src/main/java/vip/mate/agent/model/AgentEntity.java, mateclaw-server/src/main/java/vip/mate/channel/service/ChannelService.java, mateclaw-server/src/main/java/vip/mate/cron/service/CronJobService.java, mateclaw-server/src/main/java/vip/mate/exception/MateClawException.java, mateclaw-server/src/main/java/vip/mate/memory/event/ConversationCompletionPublisher.java, mateclaw-server/src/main/java/vip/mate/skill/runtime/SkillDependencyChecker.java, mateclaw-server/src/main/java/vip/mate/tool/ToolRegistry.java, mateclaw-server/src/main/java/vip/mate/tool/mcp/service/McpServerService.java, mateclaw-server/src/main/java/vip/mate/tool/service/ToolService.java, mateclaw-server/src/main/java/vip/mate/workspace/core/service/WorkspaceService.java
  Core Interface: MateClawPlugin
    · Lifecycle Methods
  PluginContext & Registration APIs
    · Key Methods
  Data Flow: Plugin Tool Registration
    · Plugin Tool Integration Flow
  Plugin Manifest (mateclaw-plugin.json)
    · Manifest Schema
    · Validation Rules
  Extension Points (SPIs)
    · PluginChannelAdapter SPI
    · PluginMemoryProvider SPI
  Code Entity Mapping
    · Entity Relationship Diagram
  Error Handling: PluginException

## · Building & Packaging a Plugin  (L6310)
  源文件: mateclaw-server/pom.xml, mateclaw-server/src/main/java/vip/mate/agent/AgentService.java, mateclaw-server/src/main/java/vip/mate/agent/ThinkingLevelHolder.java, mateclaw-server/src/main/java/vip/mate/agent/model/AgentEntity.java, mateclaw-server/src/main/java/vip/mate/channel/service/ChannelService.java, mateclaw-server/src/main/java/vip/mate/cron/service/CronJobService.java, mateclaw-server/src/main/java/vip/mate/exception/MateClawException.java, mateclaw-server/src/main/java/vip/mate/memory/event/ConversationCompletionPublisher.java, mateclaw-server/src/main/java/vip/mate/tool/builtin/DocumentExtractTool.java, mateclaw-server/src/main/java/vip/mate/tool/builtin/DocxRenderTool.java, mateclaw-server/src/main/java/vip/mate/tool/builtin/TikaExtractor.java, mateclaw-server/src/main/java/vip/mate/tool/document/GeneratedFileCache.java
  Plugin Development Workflow
    · 1. Maven Project Setup
    · 2. Implementing the Plugin Entry Point
    · 3. Defining Tools with Annotations
    · 4. Creating the Manifest
  Data Flow: Plugin Loading & Execution
  Packaging and Deployment
    · Building the JAR
    · Loading via UI
    · Security and Path Constraints

## · Database Schema & Migrations  (L6479)
  源文件: mateclaw-server/src/main/java/vip/mate/agent/AgentService.java, mateclaw-server/src/main/java/vip/mate/agent/ThinkingLevelHolder.java, mateclaw-server/src/main/java/vip/mate/agent/model/AgentEntity.java, mateclaw-server/src/main/java/vip/mate/channel/service/ChannelService.java, mateclaw-server/src/main/java/vip/mate/cron/service/CronJobService.java, mateclaw-server/src/main/java/vip/mate/exception/MateClawException.java, mateclaw-server/src/main/java/vip/mate/memory/event/ConversationCompletionPublisher.java, mateclaw-server/src/main/java/vip/mate/tool/mcp/service/McpServerService.java, mateclaw-server/src/main/java/vip/mate/tool/service/ToolService.java, mateclaw-server/src/main/java/vip/mate/workspace/core/service/WorkspaceService.java, mateclaw-server/src/main/resources/db/data-en.sql, mateclaw-server/src/main/resources/db/data-mysql-en.sql
  Dual-Database Strategy
    · Database Architecture Overview
  Flyway & Migration Lifecycle
  Core Table Groups
  Seed Data & Initialization
  Child Pages

## · Core Schema & Seed Data  (L6633)
  源文件: mateclaw-server/src/main/java/vip/mate/agent/AgentService.java, mateclaw-server/src/main/java/vip/mate/agent/ThinkingLevelHolder.java, mateclaw-server/src/main/java/vip/mate/agent/model/AgentEntity.java, mateclaw-server/src/main/java/vip/mate/approval/ApprovalController.java, mateclaw-server/src/main/java/vip/mate/approval/ApprovalService.java, mateclaw-server/src/main/java/vip/mate/channel/service/ChannelService.java, mateclaw-server/src/main/java/vip/mate/config/DatabaseBootstrapRunner.java, mateclaw-server/src/main/java/vip/mate/cron/service/CronJobService.java, mateclaw-server/src/main/java/vip/mate/exception/MateClawException.java, mateclaw-server/src/main/java/vip/mate/memory/event/ConversationCompletionPublisher.java, mateclaw-server/src/main/java/vip/mate/tool/builtin/ShellExecuteTool.java, mateclaw-server/src/main/java/vip/mate/tool/guard/guardian/FileWriteGuardian.java
  Database Entity Overview
    · Core Table Definitions
    · Data Flow: Natural Language to Database Entities
  Seed Data & Default Agents
    · Default Agent Templates
    · Built-in Providers
  Tool Registration & Synchronization
    · ShellExecuteTool Implementation
  Initialization Logic
    · Locale Selection & Desktop Mode
    · Dual Database Support
    · Migration History

## · Migration History  (L6794)
  源文件: mateclaw-server/pom.xml, mateclaw-server/src/main/java/vip/mate/llm/config/OllamaAutoDiscoveryRunner.java, mateclaw-server/src/main/java/vip/mate/llm/controller/ClaudeCodeOAuthController.java, mateclaw-server/src/main/java/vip/mate/tool/builtin/DocumentExtractTool.java, mateclaw-server/src/main/java/vip/mate/tool/builtin/DocxRenderTool.java, mateclaw-server/src/main/java/vip/mate/tool/builtin/TikaExtractor.java, mateclaw-server/src/main/java/vip/mate/tool/document/GeneratedFileCache.java, mateclaw-server/src/main/java/vip/mate/tool/document/GeneratedFileController.java, mateclaw-server/src/main/java/vip/mate/tool/document/MarkdownDocxRenderer.java, mateclaw-server/src/main/resources/application-mysql.yml, mateclaw-server/src/main/resources/db/migration/h2/V14__embedding_model_config.sql, mateclaw-server/src/main/resources/db/migration/h2/V1__baseline_schema.sql
  Overview of Schema Evolution
    · Core Migration Flow
  Chronological Migration Reference
    · Phase 1: Foundation (V1–V10)
    · Phase 2: Knowledge & Synthesis (V11–V20)
    · Phase 3: Memory & Security (V21–V40)
    · Phase 4: Modern Model Support & Tool Refinement (V41–V51)
  Key Implementation Details
    · Model Configuration & Thinking Management
    · Document Extraction Fallback Chain
    · Workspace Path Security
  Summary Table: Schema Versions

## · Internationalization & Localization  (L6979)
  源文件: mateclaw-server/src/main/java/vip/mate/exception/GlobalExceptionHandler.java, mateclaw-server/src/main/java/vip/mate/tool/builtin/CronJobTool.java, mateclaw-server/src/main/java/vip/mate/tool/guard/DefaultToolGuard.java, mateclaw-server/src/main/java/vip/mate/wiki/controller/WikiController.java, mateclaw-server/src/main/resources/db/migration/h2/V3__register_cron_job_tool.sql, mateclaw-server/src/main/resources/db/migration/mysql/V3__register_cron_job_tool.sql, mateclaw-server/src/main/resources/messages.properties, mateclaw-server/src/main/resources/messages_en.properties, mateclaw-ui/src/api/index.ts, mateclaw-ui/src/i18n/locales/en-US.ts, mateclaw-ui/src/i18n/locales/zh-CN.ts, mateclaw-ui/src/views/Wiki/components/RawMaterialPanel.vue
  Frontend Architecture
    · Locale Structure
    · UI State Machine Mapping
    · Natural Language to UI Entities
  Backend Internationalization
    · Resource Files
    · Exception Translation Flow
    · Tool & Security Guard Metadata
    · Backend Message Resolution
  Adding New Locale Keys
    · 1. Frontend Keys
    · 2. Backend Keys
    · 3. Database Seed Data

## · Testing  (L7133)
  源文件: mateclaw-server/src/main/java/vip/mate/llm/failover/FallbackEntry.java, mateclaw-server/src/main/java/vip/mate/llm/failover/ProviderHealthProperties.java, mateclaw-server/src/main/java/vip/mate/llm/failover/ProviderHealthTracker.java, mateclaw-server/src/main/java/vip/mate/llm/model/ProviderConfigRequest.java, mateclaw-server/src/main/java/vip/mate/memory/lifecycle/MemoryLifecycleEventListener.java, mateclaw-server/src/main/java/vip/mate/memory/lifecycle/MemoryLifecycleMediator.java, mateclaw-server/src/main/java/vip/mate/memory/lifecycle/TurnCompletedEvent.java, mateclaw-server/src/main/java/vip/mate/memory/lifecycle/TurnContext.java, mateclaw-server/src/main/java/vip/mate/memory/lifecycle/TurnStartedEvent.java, mateclaw-server/src/test/java/vip/mate/agent/graph/ErrorClassificationTest.java, mateclaw-server/src/test/java/vip/mate/agent/graph/NodeStreamingChatHelperFallbackChainTest.java, mateclaw-server/src/test/java/vip/mate/agent/graph/edge/ReasoningDispatcherLlmCallCountTest.java
  Backend Test Patterns
    · LLM Error Classification to Code Mapping
  Frontend Test Cases
  Key Test Areas
    · Wiki Ingestion & Recovery
    · Memory Lifecycle Guards
    · Security & Agent Bindings

## · Backend Test Patterns  (L7264)
  源文件: mateclaw-server/src/main/java/vip/mate/llm/failover/FallbackEntry.java, mateclaw-server/src/main/java/vip/mate/llm/failover/ProviderHealthProperties.java, mateclaw-server/src/main/java/vip/mate/llm/failover/ProviderHealthTracker.java, mateclaw-server/src/main/java/vip/mate/llm/failover/probe/AnthropicListModelsProbe.java, mateclaw-server/src/main/java/vip/mate/llm/failover/probe/DashScopeListModelsProbe.java, mateclaw-server/src/main/java/vip/mate/llm/failover/probe/OpenAiCompatibleListModelsProbe.java, mateclaw-server/src/main/java/vip/mate/llm/model/ProviderConfigRequest.java, mateclaw-server/src/main/java/vip/mate/memory/lifecycle/MemoryLifecycleEventListener.java, mateclaw-server/src/main/java/vip/mate/memory/lifecycle/MemoryLifecycleMediator.java, mateclaw-server/src/main/java/vip/mate/memory/lifecycle/TurnCompletedEvent.java, mateclaw-server/src/main/java/vip/mate/memory/lifecycle/TurnContext.java, mateclaw-server/src/main/java/vip/mate/memory/lifecycle/TurnStartedEvent.java
  Agent Graph Node & Edge Testing
    · State Transition Validation
    · Final Answer Semantics
  LLM Fallback & Health Tracking
    · Fallback Chain Construction
    · Error Classification
    · Provider Probing
  Memory Lifecycle Testing
    · Turn Lifecycle Events
    · Flag Guards
  Test Implementation Details
    · Mocking Patterns
    · Integration Testing with H2
    · Reflection for Private State

## · Frontend Test Cases  (L7438)
  源文件: mateclaw-server/src/main/java/vip/mate/agent/graph/plan/node/DirectAnswerNode.java, mateclaw-server/src/main/java/vip/mate/config/WebSocketConfig.java, mateclaw-server/src/main/java/vip/mate/workspace/conversation/ConversationService.java, mateclaw-ui/TEST_CASES.md, mateclaw-ui/src/components/chat/BrowserTimeline.vue, mateclaw-ui/src/components/chat/ChatInput.vue, mateclaw-ui/src/components/chat/PlanStepsPanel.vue, mateclaw-ui/src/composables/chat/useChat.ts, mateclaw-ui/src/views/ChatConsole.vue
  1. SSE Lifecycle & Reconnection
    · Implementation Details
    · Test Scenarios (TC-1)
  2. Interrupt & Queue Pipeline
    · Data Flow Diagram: Message Submission
    · Validation Areas
  3. Segmented Message Rendering
    · Component Mapping
    · Test Scenarios (TC-3)
  4. Approval Flow (Human-in-the-Loop)
    · Code Entity Association
    · Test Scenarios (TC-2)
  5. Wiki & Memory UI
    · Wiki Upload Progress
    · Memory Morning Card
  6. Visual & Theme Consistency
    · Theme Variable Validation
    · Regression Checklist

## · Glossary  (L7602)
  源文件: README.md, README_zh.md, assets/images/preview.png, mateclaw-server/src/main/java/vip/mate/agent/AgentGraphBuilder.java, mateclaw-server/src/main/java/vip/mate/agent/BaseAgent.java, mateclaw-server/src/main/java/vip/mate/agent/chatmodel/AgentClaudeCodeChatModelBuilder.java, mateclaw-server/src/main/java/vip/mate/agent/chatmodel/AgentOpenAiCompatibleChatModelBuilder.java, mateclaw-server/src/main/java/vip/mate/agent/chatmodel/ClaudeCodeIdentityChatModelDecorator.java, mateclaw-server/src/main/java/vip/mate/agent/chatmodel/ClaudeCodeSystemArrayExchangeFilter.java, mateclaw-server/src/main/java/vip/mate/agent/chatmodel/ClaudeCodeSystemArrayInterceptor.java, mateclaw-server/src/main/java/vip/mate/agent/chatmodel/DeepSeekV4ThinkingDecorator.java, mateclaw-server/src/main/java/vip/mate/agent/chatmodel/RateLimitDiagnosticExchangeFilter.java
  Core Architectural Concepts
    · Agent Graph
    · Provider Failover & Health
  Natural Language to Code Mapping
    · Agent Execution Pipeline
  Domain Specific Terms
    · LLM Wiki
    · Memory & Dreaming
    · Streaming & SSE
    · Wiki Ingestion Data Flow
  Frontend Interface Glossary
  Abbreviations Reference