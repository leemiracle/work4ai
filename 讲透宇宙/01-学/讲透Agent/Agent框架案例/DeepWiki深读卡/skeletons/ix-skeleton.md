# Skeleton: ix（20 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 9KB | 5 | ~0 | 14 |
| 2 | Getting Started | L325 | 10KB | 2 | ~6 | 19 |
| 3 | Core Architecture | L680 | 12KB | 9 | ~0 | 15 |
| 4 | Chain System | L1071 | 13KB | 9 | ~0 | 21 |
| 5 | Agent Execution System | L1525 | 11KB | 5 | ~5 | 13 |
| 6 | Component Integration | L1921 | 12KB | 9 | ~4 | 15 |
| 7 | API Reference | L2259 | 13KB | 5 | ~15 | 12 |
| 8 | Chain Management API | L2636 | 8KB | 2 | ~8 | 6 |
| 9 | Chat and Agent API | L2931 | 9KB | 7 | ~3 | 6 |
| 10 | GraphQL API | L3235 | 7KB | 6 | ~3 | 3 |
| 11 | Frontend Documentation | L3524 | 10KB | 4 | ~0 | 16 |
| 12 | Chain Graph Editor | L3792 | 20KB | 12 | ~6 | 19 |
| 13 | Chat Interface | L4474 | 10KB | 4 | ~3 | 9 |
| 14 | UI Components | L4768 | 11KB | 6 | ~2 | 4 |
| 15 | Configuration and Extensions | L5096 | 15KB | 8 | ~5 | 10 |
| 16 | LLM Configuration | L5568 | 12KB | 7 | ~2 | 7 |
| 17 | Tool Integration | L5968 | 9KB | 3 | ~7 | 3 |
| 18 | Development Guide | L6264 | 11KB | 4 | ~6 | 15 |
| 19 | Testing | L6647 | 13KB | 9 | ~2 | 5 |
| 20 | Deployment | L7049 | 11KB | 7 | ~7 | 10 |


## · Overview  (L6)
  源文件: README.md, docs/FizzBuzzExample.gif, docs/chat.png, docs/chat_interactions.png, docs/create_task.png, ix/api/artifacts/endpoints.py, ix/api/artifacts/types.py, ix/api/tests/test_artifacts.py, ix/runnable/tests/__init__.py, ix/server/fast_api.py, ix/server/settings.py, ix/server/test_settings.py
  Purpose and Scope
  Platform Architecture
    · System Overview
  Core Concepts
    · Chains
    · Agents  
    · Components
    · Tasks
  API Structure
  Data Models and Relationships
  Execution Flow
  Component Integration

## · Getting Started  (L325)
  源文件: .github/actions/run-docker/action.yml, .github/workflows/publish-dev.yml, .github/workflows/publish.yml, .github/workflows/test.yml, .gitignore, Dockerfile, Makefile, bin/get_uuid.py, docker-compose.yml, ix/chains/fixtures/agent/code2.json, ix/chains/fixtures/agent/each.json, ix/chains/fixtures/agent/gemini.json
  Prerequisites
  Quick Start
    · Service Architecture
  Development Setup Process
    · Build Process Flow
    · Manual Step-by-Step Setup
    · Key Build Targets
  Service Management
    · Starting Services
    · Service Status and Logs
    · Development Containers
  Verification Steps
    · 1. Check Service Health
    · 2. Access Web Interface
    · 3. Test API Endpoints
    · 4. Verify Agent Functionality
  Configuration
    · Environment Variables
    · LLM Provider Setup
  Troubleshooting
    · Common Issues
    · Reset and Clean Commands
  Next Steps

## · Core Architecture  (L680)
  源文件: ix/agents/history.py, ix/agents/process.py, ix/agents/tests/test_history.py, ix/agents/tests/test_process.py, ix/api/components/types.py, ix/chains/loaders/__init__.py, ix/chains/loaders/core.py, ix/chains/loaders/memory.py, ix/chains/migrations/0005_refine_node_type.py, ix/chains/models.py, ix/conftest.py, ix/pg_vector/tests/models.py
  System Overview
    · Core System Architecture
  Chain System Architecture
    · Chain Data Model
    · Chain Loading Process
  Agent Execution Architecture
    · Agent Process Lifecycle
    · Task and Message Management
  Component Integration Architecture
    · NodeType System
    · Component Loading Flow
  Context and Memory Management
    · IxContext System
  Flow Execution System
    · Flow Placeholder Architecture

## · Chain System  (L1071)
  源文件: ix/agents/callback_manager.py, ix/api/components/types.py, ix/chains/functions.py, ix/chains/json.py, ix/chains/llm_chain.py, ix/chains/loaders/__init__.py, ix/chains/loaders/core.py, ix/chains/loaders/memory.py, ix/chains/loaders/tools.py, ix/chains/migrations/0005_refine_node_type.py, ix/chains/models.py, ix/chains/routing.py
  Core Architecture
  Chain Models and Data Structure
    · Chain Model
    · ChainNode Model
    · ChainEdge Model
    · NodeType Model
  Chain Loading Process
    · Phase 1: Graph Loading
    · Phase 2: Flow Placeholder Construction
    · Phase 3: Component Initialization
  Flow Processing and Placeholders
    · Sequence Processing
    · Parallel Processing
    · Branch Processing 
  Component Integration
    · Node Loading
    · Specialized Loaders
    · IxNode Wrapper
  Execution Context
    · Context Usage

## · Agent Execution System  (L1525)
  源文件: ix/agents/history.py, ix/agents/process.py, ix/agents/tests/test_history.py, ix/agents/tests/test_process.py, ix/chains/artifacts.py, ix/chains/callbacks.py, ix/chains/management/commands/create_ix_v2.py, ix/chains/moderator.py, ix/chains/tests/test_artifacts.py, ix/chains/tests/test_moderator.py, ix/task_log/models.py, ix/task_log/tasks/agent_runner.py
  Core Components
    · Agent Execution Flow
    · Key Classes and Their Roles
  Agent Execution Lifecycle
    · Process Initialization and Startup
    · Input Processing and Context Management
  Task Management and Logging
    · Task Model Structure
    · Message Types and Content Structure
  Callback System and Real-time Communication
    · IxHandler Callback Architecture
    · Streaming and WebSocket Integration
  Multi-Agent Coordination
    · Chat Moderator System
    · Task Delegation and Hierarchies
  Error Handling and Recovery
    · Exception Management
    · Celery Task Management

## · Component Integration  (L1921)
  源文件: ix/chains/components/memory.py, ix/chains/fixture_src/__init__.py, ix/chains/fixture_src/chat_memory_backend.py, ix/chains/fixture_src/common.py, ix/chains/fixture_src/deprecated.py, ix/chains/fixture_src/memory.py, ix/chains/fixture_src/openai_functions.py, ix/chains/management/commands/import_langchain.py, ix/chains/openapi.py, ix/chains/tests/mock_runnable.py, ix/runnable/tests/test_flow.py, requirements.txt
  Component Definition System
    · Fixture Architecture
    · Component Structure
  NodeType Registration Process
    · Registration Flow
    · Schema Generation
  Component Types and Integration Patterns
    · Memory Components
    · Custom IX Components
    · Tool and Agent Integration
  Runtime Integration
    · Component Instantiation Flow
    · Testing Framework
  Secret Management Integration

## · API Reference  (L2259)
  源文件: frontend/chat/hooks/useSendInput.js, frontend/chat/input/ChatInput.js, frontend/chat/input/useSendInput.js, ix/api/chains/endpoints.py, ix/api/chains/types.py, ix/api/chats/endpoints.py, ix/api/chats/types.py, ix/api/editor/endpoints.py, ix/api/editor/types.py, ix/api/tests/test_chains.py, ix/api/tests/test_chat.py, ix/chains/migrations/0016_alter_chainedge_relation.py
  API Architecture Overview
  Chain Management API
    · Core Endpoints
    · Chain Creation Flow
    · Request/Response Models
  Chat and Agent API  
    · Chat Management
    · Agent and Message Operations
    · Message Processing Flow
  Chain Editor API
    · Node Operations
    · Edge Operations  
    · Graph Operations
    · Chain Graph Data Model
  Data Models and Types
    · Core Data Types
    · Chat Data Types
    · Pagination Support
  Authentication and Authorization
    · Access Control Implementation
  Error Handling and Responses
    · Standard HTTP Status Codes
    · Error Response Format
    · Common Error Patterns

## · Chain Management API  (L2636)
  源文件: ix/api/chains/endpoints.py, ix/api/chains/types.py, ix/api/editor/endpoints.py, ix/api/editor/types.py, ix/api/tests/test_chains.py, ix/chains/migrations/0016_alter_chainedge_relation.py
  Core Concepts
    · Chain Model
    · Node Model
    · Edge Model
  API Endpoints Overview
  Chain CRUD Operations
    · List Chains
    · Create Chain
    · Get Chain Details
    · Update Chain
    · Delete Chain
  Node Management
    · Add Node
    · Update Node
    · Update Node Position
    · Delete Node
  Edge Management
    · Add Edge
    · Update Edge
    · Delete Edge
  Chain Graph Operations
    · Get Complete Graph
    · Set Root Nodes
  Data Flow and Integration
  Error Handling
  Authentication and Authorization

## · Chat and Agent API  (L2931)
  源文件: frontend/chat/hooks/useSendInput.js, frontend/chat/input/ChatInput.js, frontend/chat/input/useSendInput.js, ix/api/chats/endpoints.py, ix/api/chats/types.py, ix/api/tests/test_chat.py
  Overview
  Core Entities
    · Chat Session Management
    · Agent Management
  Message Handling
    · Message Flow Architecture
    · Message API Endpoints
    · Message Data Models
  Agent Targeting and Delegation
    · Agent Selection Logic
    · Agent Management Operations
  Authentication and Authorization
  Integration Points
    · Frontend Integration
    · Backend Integration
  Error Handling

## · GraphQL API  (L3235)
  源文件: ix/schema/__init__.py, ix/schema/types/tasks.py, ix/task_log/migrations/0005_rename_artifact_storage.py
  Purpose and Scope
  Schema Architecture
    · GraphQL Schema Structure
  Queries
    · Task Queries
    · Query Implementation
  Subscriptions
    · Subscription Architecture
  GraphQL Types
    · Type Definitions
    · TaskType Fields and Relationships
    · GoalType Structure
  Integration with IX Platform
    · Data Flow Integration
  Usage Patterns
    · Querying Tasks
    · Real-time Subscriptions

## · Frontend Documentation  (L3524)
  源文件: frontend/agents/AgentEditButton.js, frontend/chains/ChainEditButton.js, frontend/chains/ChainEditorView.js, frontend/chains/ChainGraphEditor.js, frontend/chains/editor/EditorTopBar.js, frontend/chains/editor/contexts.js, frontend/chains/hooks/useChainState.js, frontend/chains/hooks/useEdgeState.js, frontend/chat/ChatInterface.js, frontend/chat/ChatMessages.js, frontend/chat/ChatView.js, frontend/chat/hooks/useChatGraph.js
  Purpose and Scope
  Frontend Architecture Overview
    · Component Architecture
    · State Management Architecture
  Key Frontend Systems
    · Chain Graph Editor System
    · Chat Interface System
  Data Flow Patterns
    · Editor Data Flow
    · Chat Data Flow
  API Integration Patterns
    · REST API Integration
    · GraphQL Subscriptions
    · Custom Hooks for API Integration
  Component Styling and Theming
    · Theme Configuration
    · Responsive Design

## · Chain Graph Editor  (L3792)
  源文件: frontend/agents/AgentEditButton.js, frontend/chains/ChainEditButton.js, frontend/chains/ChainEditorView.js, frontend/chains/ChainGraphEditor.js, frontend/chains/editor/ConnectorPopover.js, frontend/chains/editor/EditorTopBar.js, frontend/chains/editor/contexts.js, frontend/chains/editor/styles.js, frontend/chains/editor/useColorMode.js, frontend/chains/flow/BranchNode.js, frontend/chains/flow/ChainNode.js, frontend/chains/flow/ConfigNode.js
  Purpose and Scope
  Architecture Overview
    · Core Architecture Diagram
  Core Components
    · ChainGraphEditor Component
    · Node Type System
  Node System
    · ConfigNode Architecture
    · Node Properties and Connectors
  Edge System
    · Edge Types and Relationships
    · Connection Validation
  State Management
    · Context-Based State Architecture
    · Tab State Management
  Drag and Drop System
    · Node Creation Flow
    · Auto-Connection Logic
  Styling and Theming
    · Color Mode System
    · Node Visual Styles

## · Chat Interface  (L4474)
  源文件: frontend/chat/ChatInterface.js, frontend/chat/ChatMessages.js, frontend/chat/ChatView.js, frontend/chat/hooks/useChatGraph.js, frontend/hooks/useLinkedScroll.js, frontend/site/RightSidebar.js, frontend/site/ScrollableBox.js, frontend/site/SidebarTabs.js, frontend/site/key_frames.js
  Architecture Overview
  Core Components
    · ChatView Component
    · ChatInterface Component
    · Message Display System
  Layout and UI Structure
    · Three-Pane Layout
    · Scrollable Content Management
  Styling and Theming
    · Chat Style System
    · Responsive Design Elements
  Integration Points
    · Backend Connectivity
    · Context Providers

## · UI Components  (L4768)
  源文件: frontend/chains/editor/PromptEditor.js, frontend/chains/flow/FunctionSchemaNode.js, frontend/components/DictForm.js, frontend/components/ListForm.js
  Purpose and Scope
  Component Architecture
  Dynamic Collection Components
    · ListForm Component
    · DictForm Component
  Specialized Editor Components
    · PromptEditor Component
    · FunctionSchemaNode Component
  Theming and Color Mode Integration
  Component Usage Patterns

## · Configuration and Extensions  (L5096)
  源文件: .env.template, ix/chains/fixture_src/llm.py, ix/chains/fixture_src/tools.py, ix/runnable/llm.py, ix/tools/metaphor.py, test_data/snapshots/components/langchain.chat_models.anthropic.ChatAnthropic.json, test_data/snapshots/components/langchain.chat_models.fireworks.ChatFireworks.json, test_data/snapshots/components/langchain.chat_models.google_palm.ChatGooglePalm.json, test_data/snapshots/components/langchain.llms.fireworks.Fireworks.json, test_data/snapshots/components/langchain.llms.llamacpp.LlamaCpp.json
  Configuration Architecture Overview
  LLM Configuration System
    · Supported LLM Providers
    · LLM Configuration Structure
    · Custom LLM Wrapper Example
  Tool Integration System
    · Available Tool Categories
    · Tool Configuration Patterns
    · Custom Tool Implementation Example
  Secret Management
    · Secret Configuration Flow
    · Secret Field Configuration
    · Environment Variable Integration
  Custom Component Development
    · Component Definition Structure
    · Custom Component Example
    · Adding Custom Components
  Environment Configuration
    · Configuration Hierarchy
    · Required vs Optional Configuration
    · Configuration Best Practices

## · LLM Configuration  (L5568)
  源文件: ix/chains/fixture_src/llm.py, ix/runnable/llm.py, test_data/snapshots/components/langchain.chat_models.anthropic.ChatAnthropic.json, test_data/snapshots/components/langchain.chat_models.fireworks.ChatFireworks.json, test_data/snapshots/components/langchain.chat_models.google_palm.ChatGooglePalm.json, test_data/snapshots/components/langchain.llms.fireworks.Fireworks.json, test_data/snapshots/components/langchain.llms.llamacpp.LlamaCpp.json
  LLM Provider Architecture
  Configuration Components
    · Base Configuration Structure
    · Common Base Fields
  Supported LLM Providers
    · OpenAI Configuration
    · Anthropic Configuration
    · Google LLM Providers
    · Local Model Providers
    · Cloud API Providers
  Custom LLM Extensions
    · IXChatOpenAI Function Calling
  Secret Management Integration
  Configuration Registration

## · Tool Integration  (L5968)
  源文件: .env.template, ix/chains/fixture_src/tools.py, ix/tools/metaphor.py
  Tool Architecture
  Available Tools
    · Search Tools
    · Knowledge Base Tools
    · API Integration Tools
    · Chain Tools
  Tool Configuration
    · Environment Variables
    · Secret Management
  Tool Implementation Pattern
    · Key Implementation Components
  Tool Field Configuration
    · Common Tool Fields
    · Dynamic Field Generation
  Adding Custom Tools
    · 1. Tool Implementation
    · 2. Tool Fixture Definition
    · 3. Registration

## · Development Guide  (L6264)
  源文件: .github/actions/run-docker/action.yml, .github/workflows/publish-dev.yml, .github/workflows/publish.yml, .github/workflows/test.yml, .gitignore, Dockerfile, Makefile, bin/get_uuid.py, docker-compose.yml, ix/chains/loaders/tools.py, ix/chains/tests/conftest.py, ix/chains/tests/fake.py
  Development Environment Setup
    · Prerequisites
    · Core Development Services
    · Initial Setup
    · Service Management
  Development Workflow
    · Image Building System
    · Frontend Development
    · Database and Component Management
  Testing Infrastructure
    · Test Architecture
    · Running Tests
    · Test Utilities
  Build and Deployment Pipeline
    · CI/CD Architecture
    · Image Caching Strategy  
    · Multi-Platform Publishing
  Secret Management with Vault
  Development Shell Access
  Code Quality and Formatting

## · Testing  (L6647)
  源文件: ix/chains/loaders/tools.py, ix/chains/tests/conftest.py, ix/chains/tests/fake.py, ix/chains/tests/mock_configs.py, ix/chains/tests/test_config_loader.py
  Purpose and Scope
  Test Infrastructure Overview
    · Test Architecture
  Core Testing Patterns
    · Async Test Implementation
    · Database Integration Testing
  Component-Specific Testing
    · Memory System Testing
    · Agent Loading Testing
    · Flow Component Testing
  Test Utilities and Fixtures
    · Fake Data Generation
    · Complex Test Fixtures
    · Mock Configurations
  Tool Integration Testing
    · Tool Loading and Execution
  Testing Best Practices
    · Async Test Patterns
    · Mock and Fixture Usage
    · Component Validation

## · Deployment  (L7049)
  源文件: .github/actions/run-docker/action.yml, .github/workflows/publish-dev.yml, .github/workflows/publish.yml, .github/workflows/test.yml, .gitignore, Dockerfile, Makefile, bin/get_uuid.py, docker-compose.yml, psql.Dockerfile
  Docker Architecture
    · Multi-Stage Build Configuration
    · Service Architecture
  Build System
    · Image Tagging and Caching Strategy
    · Build Targets and Dependencies
  Service Orchestration
    · Docker Compose Configuration
    · Development vs Production Modes
  CI/CD Pipeline
    · GitHub Actions Workflow
    · Build and Test Matrix
    · Multi-Platform Publishing
  Production Deployment
    · Service Scaling Configuration
    · Environment Configuration
    · Volume Management
  Security and Secret Management
    · Vault Integration
    · Certificate Generation