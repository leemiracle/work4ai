# Skeleton: agentgpt（21 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 10KB | 3 | ~3 | 14 |
| 2 | System Architecture | L248 | 11KB | 6 | ~5 | 18 |
| 3 | Frontend | L596 | 14KB | 8 | ~5 | 21 |
| 4 | Landing Page UI | L1050 | 12KB | 4 | ~0 | 20 |
| 5 | Agent Interface | L1368 | 9KB | 5 | ~5 | 15 |
| 6 | UI Components | L1605 | 13KB | 6 | ~9 | 24 |
| 7 | State Management | L1992 | 11KB | 7 | ~6 | 10 |
| 8 | Workflow System | L2352 | 8KB | 4 | ~4 | 2 |
| 9 | Backend | L2588 | 11KB | 4 | ~6 | 10 |
| 10 | Agent API | L2899 | 11KB | 5 | ~3 | 15 |
| 11 | Agent Service | L3197 | 20KB | 8 | ~0 | 13 |
| 12 | Agent Tools | L3658 | 11KB | 5 | ~2 | 10 |
| 13 | Storage and Database | L3966 | 13KB | 6 | ~10 | 5 |
| 14 | Agent System | L4400 | 11KB | 4 | ~2 | 15 |
| 15 | Agent Lifecycle | L4673 | 23KB | 8 | ~11 | 14 |
| 16 | Task Execution | L5159 | 13KB | 12 | ~2 | 15 |
| 17 | Prompts and Output Parsing | L5483 | 9KB | 7 | ~3 | 12 |
| 18 | Setup and Deployment | L5725 | 11KB | 4 | ~3 | 22 |
| 19 | Environment Configuration | L6040 | 8KB | 4 | ~5 | 15 |
| 20 | Docker Deployment | L6272 | 14KB | 7 | ~6 | 18 |
| 21 | CLI Configuration | L6644 | 8KB | 4 | ~4 | 7 |


## · Overview  (L6)
  源文件: .github/PULL_REQUEST_TEMPLATE/pull_request_template.md, README.md, docs/README.hu-Cs4K1Sr4C.md, docs/README.zh-HANS.md, next/src/components/console/ChatMessage.tsx, next/src/components/console/ChatWindow.tsx, next/src/components/console/MacWindowHeader.tsx, next/src/components/console/SummarizeButton.tsx, next/src/pages/agent/index.tsx, next/src/pages/index.tsx, next/src/services/agent/agent-run-model.tsx, next/src/services/agent/autonomous-agent.ts
  System Purpose
  High-Level Architecture
    · System Architecture Diagram
  Core Components
    · Frontend Application
    · Backend Services
    · Agent Execution Engine
  Agent Execution Flow
    · Agent Lifecycle Diagram
  Technology Stack
    · Component Integration Diagram
  Deployment Architecture

## · System Architecture  (L248)
  源文件: .github/PULL_REQUEST_TEMPLATE/pull_request_template.md, README.md, docs/README.hu-Cs4K1Sr4C.md, docs/README.zh-HANS.md, next/package-lock.json, next/package.json, next/public/locales/en/indexPage.json, next/src/components/Button.tsx, next/src/components/Input.tsx, next/src/components/Label.tsx, next/src/components/Switch.tsx, next/src/components/console/ChatMessage.tsx
  Purpose and Scope
  High-Level Architecture Overview
  Frontend Architecture
    · Key Frontend Components
  Backend Architecture
    · Core Backend Services
    · Configuration Management
  Database Architecture and Data Flow
    · Data Flow Patterns
  External Service Integration
    · API Integration Architecture
    · Service Configuration
  Development and Deployment Infrastructure
    · Deployment Architecture

## · Frontend  (L596)
  源文件: next/public/favicon.svg, next/public/locales/en/drawer.json, next/public/prod_square.png, next/src/components/AppHead.tsx, next/src/components/BannerBadge.tsx, next/src/components/GlowWrapper.tsx, next/src/components/HeroCard.tsx, next/src/components/NavBar.tsx, next/src/components/console/ChatWindow.tsx, next/src/components/console/MacWindowHeader.tsx, next/src/components/console/SummarizeButton.tsx, next/src/components/landing/Hero.tsx
  Architecture Overview
    · Frontend Technology Stack
    · Main Page Components
    · Page State Logic
  Key UI Components
    · Hero Component
    · Navigation System
    · Chat Interface
  State Management System
    · Store Architecture
    · Agent Lifecycle Management
  Agent Integration Layer
    · Service Layer Architecture
    · Agent State Synchronization
  Styling and Theme System
    · Custom Design System
    · CSS Custom Classes

## · Landing Page UI  (L1050)
  源文件: next/public/favicon.svg, next/public/hero-background.png, next/public/locales/en/drawer.json, next/public/prod_square.png, next/src/components/AppHead.tsx, next/src/components/BannerBadge.tsx, next/src/components/GlowWrapper.tsx, next/src/components/HeroCard.tsx, next/src/components/Menu.tsx, next/src/components/NavBar.tsx, next/src/components/WindowButton.tsx, next/src/components/landing/Backing.tsx
  Overview
  Component Structure
  Navigation Bar (NavBar)
    · Structure and Features
    · Implementation Details
  Hero Section
    · Key Components
    · User Interaction Flow
  HeroCard Component
    · Structure and Properties
    · Visual Styling
  Visual Styling and Animations
    · CSS Classes and Effects
    · Responsive Design
    · CSS Implementation
  User Interaction Flows
    · Navigation
    · Call-to-Action
    · Hero Cards Carousel
    · Screen Size Adaptation
  Integration with Page Structure
  Technical Implementation Details
    · Key Technologies
    · State Management
    · Event Handlers
  Summary

## · Agent Interface  (L1368)
  源文件: next/src/components/console/ChatWindow.tsx, next/src/components/console/MacWindowHeader.tsx, next/src/components/console/SummarizeButton.tsx, next/src/pages/agent/index.tsx, next/src/pages/index.tsx, next/src/pages/settings.tsx, next/src/services/agent/agent-run-model.tsx, next/src/services/agent/autonomous-agent.ts, next/src/services/agent/message-service.ts, next/src/stores/agentStore.ts, next/src/stores/modelSettingsStore.ts, next/src/types/modelSettings.ts
  Main Interface Components
  Agent State Management
  Chat Interface Components
  Agent Creation and Lifecycle
  Settings Integration
  Message and Task Display

## · UI Components  (L1605)
  源文件: next/package-lock.json, next/package.json, next/public/errorFavicon.ico, next/public/locales/en/indexPage.json, next/src/components/Button.tsx, next/src/components/Input.tsx, next/src/components/Label.tsx, next/src/components/PrimaryButton.tsx, next/src/components/Switch.tsx, next/src/components/TextButton.tsx, next/src/components/console/MarkdownRenderer.tsx, next/src/components/console/SourceCard.tsx
  Component Architecture Overview
  Core Button Components
    · Base Button Component
    · Button Variants
  Input Components
    · Input Features
    · Switch Component
  Dialog System
    · Dialog Features
  Specialized Content Components
    · MarkdownRenderer
    · SourceLink Component
  Drawer and Navigation Components
    · Component Responsibilities
  Styling and Theming System
    · Technology Stack
    · Styling Patterns

## · State Management  (L1992)
  源文件: next/src/components/console/MarkdownRenderer.tsx, next/src/pages/settings.tsx, next/src/stores/configStore.ts, next/src/stores/modelSettingsStore.ts, next/src/types/modelSettings.ts, next/src/ui/combox.tsx, next/src/ui/input.tsx, next/src/utils/constants.ts, platform/reworkd_platform/db/utils.py, platform/reworkd_platform/services/ssl.py
  Purpose and Scope
  Architecture Overview
    · Store Architecture
  Store Implementations
    · Configuration Store
    · Model Settings Store
  State Persistence System
    · Zustand Middleware Integration
    · Storage Keys and Versioning
  Component Integration Patterns
    · Settings Page Integration
    · State-UI Synchronization
  State Management Patterns
    · Type Safety and Generics
    · Selector Pattern Implementation

## · Workflow System  (L2352)
  源文件: next/src/services/fetch-utils.ts, next/src/ui/select.tsx
  Purpose and Scope
  System Architecture
    · High-Level Architecture
    · Component Structure
  Visual Interface Components
    · Select Component Integration
  API Communication Layer
    · Fetch Utilities Integration
    · Request Flow
  Integration with Agent System
    · Workflow to Agent Translation
    · State Management Integration

## · Backend  (L2588)
  源文件: next/src/utils/interfaces.ts, platform/poetry.lock, platform/pyproject.toml, platform/reworkd_platform/settings.py, platform/reworkd_platform/web/api/agent/agent_service/agent_service.py, platform/reworkd_platform/web/api/agent/agent_service/agent_service_provider.py, platform/reworkd_platform/web/api/agent/agent_service/mock_agent_service.py, platform/reworkd_platform/web/api/agent/agent_service/open_ai_agent_service.py, platform/reworkd_platform/web/api/agent/dependancies.py, platform/reworkd_platform/web/api/agent/views.py
  Architecture Overview
  Technology Stack
  Core Agent Service Architecture
  FastAPI Router and Endpoints
  Dependency Injection and Validation
  Configuration System
  Database Integration
  External Service Integration

## · Agent API  (L2899)
  源文件: next/package-lock.json, next/package.json, next/public/locales/en/indexPage.json, next/src/components/Button.tsx, next/src/components/Input.tsx, next/src/components/Label.tsx, next/src/components/Switch.tsx, next/src/components/drawer/DrawerItemButton.tsx, next/src/server/api/routers/agentRouter.ts, next/src/utils/interfaces.ts, platform/reworkd_platform/web/api/agent/agent_service/agent_service.py, platform/reworkd_platform/web/api/agent/agent_service/agent_service_provider.py
  Purpose and Scope
  API Architecture Overview
  REST API Endpoints
    · Agent Execution Flow
  Agent Service Architecture
  tRPC Integration
  Request/Response Schemas
    · Core Request Types
    · Response Types
  Authentication and Dependencies
    · Dependency Chain

## · Agent Service  (L3197)
  源文件: next/src/utils/interfaces.ts, platform/reworkd_platform/services/tokenizer/token_service.py, platform/reworkd_platform/tests/agent/test_analysis.py, platform/reworkd_platform/tests/agent/test_crud.py, platform/reworkd_platform/tests/agent/test_task_output_parser.py, platform/reworkd_platform/tests/agent/test_tools.py, platform/reworkd_platform/tests/test_settings.py, platform/reworkd_platform/web/api/agent/agent_service/agent_service.py, platform/reworkd_platform/web/api/agent/agent_service/agent_service_provider.py, platform/reworkd_platform/web/api/agent/agent_service/mock_agent_service.py, platform/reworkd_platform/web/api/agent/agent_service/open_ai_agent_service.py, platform/reworkd_platform/web/api/agent/model_factory.py
  Agent Service Interface
  Service Implementations
    · OpenAI Agent Service
    · Mock Agent Service
  Agent Service Provider
  API Integration and Method Mapping
  Model Factory
  Agent Service Operations
    · Agent Lifecycle Workflow
    · Method Details
  Error Handling
  Integration with Tools
  Token Management
  Summary

## · Agent Tools  (L3658)
  源文件: platform/reworkd_platform/web/api/agent/prompts.py, platform/reworkd_platform/web/api/agent/tools/code.py, platform/reworkd_platform/web/api/agent/tools/conclude.py, platform/reworkd_platform/web/api/agent/tools/image.py, platform/reworkd_platform/web/api/agent/tools/reason.py, platform/reworkd_platform/web/api/agent/tools/search.py, platform/reworkd_platform/web/api/agent/tools/tool.py, platform/reworkd_platform/web/api/agent/tools/tools.py, platform/reworkd_platform/web/api/agent/tools/utils.py, platform/reworkd_platform/web/api/agent/tools/wikipedia_search.py
  Tool Architecture Overview
    · Tool Class Hierarchy
  Available Tool Types
  Tool Execution Flow
  Tool Management System
    · Tool Discovery Functions
    · Tool Availability Checking
  Integration with Language Models and Prompts
    · Tool-Specific Prompt Usage
    · LLMChain Integration
  External Service Integration
    · API Integration Architecture
    · Error Handling and Fallbacks

## · Storage and Database  (L3966)
  源文件: next/prisma/schema.prisma, platform/poetry.lock, platform/pyproject.toml, platform/reworkd_platform/settings.py, platform/reworkd_platform/web/api/agent/dependancies.py
  Database Architecture Overview
    · Dual-ORM Architecture Diagram
  Database Schema
    · Core Entity Relationships
  Database Models
  Database Models
    · Authentication Models (NextAuth.js Integration)
    · Agent Execution Models
    · Organization Management Models
    · OAuth Integration Model
  Database Connectivity
    · Database Connection Architecture
    · Backend Database Configuration
    · Frontend Database Configuration
    · Database Session Management
  Data Persistence Patterns
    · Agent Execution Data Flow
    · CRUD Operations Architecture
    · Database Transaction Patterns
  Database Dependencies and Patterns
    · Dependency Injection Pattern
    · Validation and Data Flow
  Security Considerations

## · Agent System  (L4400)
  源文件: .github/PULL_REQUEST_TEMPLATE/pull_request_template.md, README.md, docs/README.hu-Cs4K1Sr4C.md, docs/README.zh-HANS.md, next/src/components/console/ChatMessage.tsx, platform/reworkd_platform/web/api/agent/prompts.py, platform/reworkd_platform/web/api/agent/tools/code.py, platform/reworkd_platform/web/api/agent/tools/conclude.py, platform/reworkd_platform/web/api/agent/tools/image.py, platform/reworkd_platform/web/api/agent/tools/reason.py, platform/reworkd_platform/web/api/agent/tools/search.py, platform/reworkd_platform/web/api/agent/tools/tool.py
  System Purpose
  Agent Architecture Overview
  Core Execution Loop
    · Agent Execution Flow
    · Task Generation and Analysis
  Tool Selection and Execution
    · Available Tool Types
    · Tool Availability and Selection
  Agent Service Implementation
    · Service Architecture
    · Tool Base Class Interface
  Streaming Response System
    · Response Flow
  Error Handling and Fallbacks

## · Agent Lifecycle  (L4673)
  源文件: .github/PULL_REQUEST_TEMPLATE/pull_request_template.md, README.md, docs/README.hu-Cs4K1Sr4C.md, docs/README.zh-HANS.md, next/src/components/console/ChatMessage.tsx, next/src/components/console/ChatWindow.tsx, next/src/components/console/MacWindowHeader.tsx, next/src/components/console/SummarizeButton.tsx, next/src/pages/agent/index.tsx, next/src/pages/index.tsx, next/src/services/agent/agent-run-model.tsx, next/src/services/agent/autonomous-agent.ts
  Agent Lifecycle Overview
  Agent Components and Architecture
    · Core Components
  Agent Initialization
  Agent Execution Process
    · Agent Execution Loop
    · AgentWork Types
  Agent-Backend Interaction
  Agent Tools
  Agent State Management
    · Zustand Stores
    · AgentLifecycle States
    · State Transitions
  Special Operations
    · Agent Summarization
    · Agent Chat Interaction
  Agent Error Handling
  Conclusion

## · Task Execution  (L5159)
  源文件: .github/PULL_REQUEST_TEMPLATE/pull_request_template.md, README.md, docs/README.hu-Cs4K1Sr4C.md, docs/README.zh-HANS.md, next/src/components/console/ChatMessage.tsx, platform/reworkd_platform/web/api/agent/prompts.py, platform/reworkd_platform/web/api/agent/tools/code.py, platform/reworkd_platform/web/api/agent/tools/conclude.py, platform/reworkd_platform/web/api/agent/tools/image.py, platform/reworkd_platform/web/api/agent/tools/reason.py, platform/reworkd_platform/web/api/agent/tools/search.py, platform/reworkd_platform/web/api/agent/tools/tool.py
  Overview
  Task Creation and Goal Decomposition
    · Initial Task Generation
    · Dynamic Task Creation
  Task Analysis and Tool Selection
    · Task Analysis Process
    · Available Tools Mapping
  Tool Execution
    · Tool Interface
    · Search Tool Execution
    · Code Tool Execution
    · Image Tool Execution
  Task Flow Control
    · Execution Loop
    · Task Conclusion
  Results Processing and Summarization
    · Result Summarization
    · Streaming Response Handling

## · Prompts and Output Parsing  (L5483)
  源文件: platform/reworkd_platform/web/api/agent/helpers.py, platform/reworkd_platform/web/api/agent/prompts.py, platform/reworkd_platform/web/api/agent/task_output_parser.py, platform/reworkd_platform/web/api/agent/tools/code.py, platform/reworkd_platform/web/api/agent/tools/conclude.py, platform/reworkd_platform/web/api/agent/tools/image.py, platform/reworkd_platform/web/api/agent/tools/reason.py, platform/reworkd_platform/web/api/agent/tools/search.py, platform/reworkd_platform/web/api/agent/tools/tool.py, platform/reworkd_platform/web/api/agent/tools/tools.py, platform/reworkd_platform/web/api/agent/tools/utils.py, platform/reworkd_platform/web/api/agent/tools/wikipedia_search.py
  Prompt Template System
  Core Prompt Categories
    · Goal Initialization Prompts
    · Task Analysis and Tool Selection
    · Specialized Tool Prompts
    · Task Management Prompts
  Output Parsing Architecture
    · Task Output Parser
    · Parsing Helper Functions
  Error Handling and Validation
    · Parse Exception Management
    · Model Interaction Error Handling
  Integration with Agent Tools
    · Tool-Specific Prompt Usage
    · Streaming Response Integration
    · Model Chain Execution

## · Setup and Deployment  (L5725)
  源文件: .env.example, cli/package-lock.json, cli/package.json, cli/src/envGenerator.js, cli/src/helpers.js, cli/src/index.js, cli/src/questions/existingEnvQuestions.js, cli/src/questions/newEnvQuestions.js, cli/src/questions/sharedQuestions.js, docker-compose.yml, next/.husky/pre-commit, next/entrypoint.sh
  Deployment Architecture Overview
  Environment Configuration Process
    · Environment Variable Categories
    · Environment Validation
  Docker Service Configuration
    · Service Configurations
  Database Initialization Process
    · Database Connection Configuration
  Manual Deployment Process
    · Manual Setup Requirements
    · Environment Schema Validation
  Post-Deployment Verification

## · Environment Configuration  (L6040)
  源文件: .env.example, cli/package-lock.json, cli/package.json, cli/src/envGenerator.js, cli/src/helpers.js, cli/src/index.js, cli/src/questions/existingEnvQuestions.js, cli/src/questions/newEnvQuestions.js, cli/src/questions/sharedQuestions.js, docker-compose.yml, next/next.config.mjs, next/public/logos/panache-default-solid.svg
  Environment Variable Categories
    · Platform Configuration
    · API Service Keys
    · Database Configuration
    · Authentication Services
  CLI-Based Environment Generation
  Environment File Structure
  Environment Validation
    · Frontend Schema Validation
    · CLI Validation Process
  Docker Environment Integration
  Configuration Files and Paths

## · Docker Deployment  (L6272)
  源文件: .env.example, cli/src/envGenerator.js, docker-compose.yml, next/.husky/pre-commit, next/entrypoint.sh, next/next.config.mjs, next/public/locales/en/chat.missing.json, next/public/logos/panache-default-solid.svg, next/public/logos/yc-default-solid.svg, next/src/components/console/ExampleAgents.tsx, next/src/env/schema.mjs, next/wait-for-db.sh
  Prerequisites
  Docker Architecture
    · Docker Compose Services
  Container Initialization Flow
  Automated Setup with CLI
  Manual Docker Deployment
  Environment Configuration for Docker
  Docker-Specific Environment Configuration
    · Key Docker Environment Variables
    · Environment Variable Generation Logic
  Docker Container Details
    · Frontend Container Initialization
    · Platform Container Build and Runtime
    · Database Container
  Troubleshooting Docker Deployment
    · Common Issues and Solutions
    · Viewing Container Logs
    · Rebuilding Containers
  Summary

## · CLI Configuration  (L6644)
  源文件: cli/package-lock.json, cli/package.json, cli/src/helpers.js, cli/src/index.js, cli/src/questions/existingEnvQuestions.js, cli/src/questions/newEnvQuestions.js, cli/src/questions/sharedQuestions.js
  Overview
  CLI Architecture and Components
  Interactive Setup Process
    · New Environment Setup
    · Existing Environment Handling
  Deployment Integration
    · Docker Compose Integration
    · Manual Deployment Instructions
  Question System Architecture
  CLI Dependencies and Runtime