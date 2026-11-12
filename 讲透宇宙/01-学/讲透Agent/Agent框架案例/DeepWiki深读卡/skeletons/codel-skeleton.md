# Skeleton: codel（17 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 10KB | 6 | ~6 | 9 |
| 2 | Getting Started | L349 | 8KB | 4 | ~3 | 13 |
| 3 | Core Systems | L628 | 18KB | 7 | ~5 | 6 |
| 4 | Task Processing System | L1175 | 9KB | 3 | ~4 | 2 |
| 5 | Language Model Integration | L1396 | 14KB | 9 | ~0 | 4 |
| 6 | Container Execution System | L1791 | 10KB | 7 | ~0 | 4 |
| 7 | Data Architecture | L2094 | 15KB | 5 | ~4 | 8 |
| 8 | Database Schema | L2598 | 11KB | 3 | ~12 | 11 |
| 9 | GraphQL API | L2906 | 11KB | 7 | ~5 | 5 |
| 10 | Real-time Communication | L3316 | 14KB | 5 | ~2 | 7 |
| 11 | User Interface | L3755 | 11KB | 7 | ~7 | 5 |
| 12 | Main Chat Interface | L4074 | 12KB | 5 | ~3 | 4 |
| 13 | Terminal Component | L4439 | 10KB | 4 | ~3 | 2 |
| 14 | Messages System | L4725 | 9KB | 10 | ~5 | 7 |
| 15 | Navigation and UI Components | L5011 | 11KB | 6 | ~0 | 9 |
| 16 | Deployment | L5370 | 9KB | 3 | ~3 | 9 |
| 17 | Application Bootstrapping | L5647 | 9KB | 11 | ~2 | 10 |


## · Overview  (L6)
  源文件: .github/logo.png, DEVELOPMENT.md, README.md, backend/.env.example, backend/go.mod, backend/go.sum, backend/main.go, backend/models/models.go, frontend/.env.example
  What is Codel?
  System Architecture
  Core Components
    · 1. Task Processing System
    · 2. Data Model
    · 3. Language Model Integration
    · 4. Container Execution System
  System Workflow
  Configuration and Deployment

## · Getting Started  (L349)
  源文件: .dockerignore, .github/logo.png, .gitignore, DEVELOPMENT.md, Dockerfile, README.md, backend/.env.example, backend/.gitignore, backend/config/config.go, backend/executor/browser.go, backend/providers/common.go, backend/providers/ollama.go
  Prerequisites
  Installation
    · Codel Deployment Architecture
  Configuration Options
    · Environment Variables
    · Configuration System Flow
  Using Codel
    · Creating Your First Task
    · Task Execution Flow
  Language Model Configuration
    · OpenAI
    · Ollama
    · Provider System Architecture
  Docker Integration
  Next Steps

## · Core Systems  (L628)
  源文件: backend/executor/processor.go, backend/executor/queue.go, backend/providers/openai.go, backend/providers/providers.go, backend/providers/types.go, backend/templates/prompts/agent.tmpl
  Overview of Core Systems
  Task Processing System
    · Queue Architecture
    · Task Processing Flow
  Language Model Integration
    · Provider Architecture
    · Tool Definitions
    · Agent Prompt and Task Generation
  Container Execution System
    · Container Management Architecture
    · Terminal Execution
    · Browser Execution
    · Code Execution
  Integration Between Core Systems

## · Task Processing System  (L1175)
  源文件: backend/executor/queue.go, backend/templates/prompts/agent.tmpl
  System Architecture
  Queue Management
  Task Types and Processing Flow
  Next Task Determination
  Language Model Prompt Template
  Integration with Other Systems
  Implementation Details

## · Language Model Integration  (L1396)
  源文件: backend/executor/processor.go, backend/providers/openai.go, backend/providers/providers.go, backend/providers/types.go
  Provider Architecture
    · Provider Interface
    · Provider Implementations
  Language Model Communication
    · Tool Definitions
    · Conversation Context Management
  Task Generation Process
    · Converting LLM Responses to Tasks
  Specialized LLM Functions
    · Task Summarization
    · Docker Image Selection
  Integration with Task Processing System
  Error Handling
  Summary

## · Container Execution System  (L1791)
  源文件: backend/assets/assets.go, backend/executor/container.go, backend/executor/terminal.go, backend/templates/scripts/content.js
  Purpose and Scope
  System Architecture
  Container Lifecycle Management
    · Container Initialization
    · Container Creation
    · Container Management
  Terminal Execution
    · Command Execution
    · File Operations
  Container Naming and Identification
  Error Handling and Recovery
  Data Flow
  Browser Integration
  Security Considerations
  Integration with Task Processing

## · Data Architecture  (L2094)
  源文件: backend/database/flows.sql.go, backend/database/models.go, backend/database/tasks.sql.go, backend/graph/generated.go, backend/graph/schema.graphqls, backend/migrations/20240328114536_tool_call_id_field.sql, backend/models/flows.sql, backend/models/tasks.sql
  Database Schema
    · Flows
    · Tasks
    · Containers
    · Logs
  GraphQL API
    · GraphQL Schema Types
    · GraphQL Operations
  Data Flow
  ORM Layer
    · SQL Query Definitions
    · Generated Code
  Schema Evolution
  Data Mapping
  Conclusion

## · Database Schema  (L2598)
  源文件: backend/database/containers.sql.go, backend/database/db.go, backend/database/flows.sql.go, backend/database/models.go, backend/database/tasks.sql.go, backend/migrations/20240325154630_initial_migration.sql, backend/migrations/20240328114536_tool_call_id_field.sql, backend/models/containers.sql, backend/models/flows.sql, backend/models/tasks.sql, backend/sqlc.yml
  Overview
  Table Definitions
    · Containers Table
    · Flows Table
    · Tasks Table
    · Logs Table
  Key Relationships
  Database Access Layer
    · Query Interfaces
  Database Usage in System Context
  Transaction Management
  Database Migrations
  JSON Data Storage

## · GraphQL API  (L2906)
  源文件: backend/graph/generated.go, backend/graph/schema.graphqls, frontend/generated/graphql.schema.json, frontend/generated/graphql.ts, frontend/src/pages/ChatPage/ChatPage.graphql
  Overview
  Schema Structure
    · Enumerations
  Operations
    · Queries
    · Mutations
    · Subscriptions
  Frontend Integration
    · Generated Hooks
  Backend Implementation
    · Resolver Interfaces
  Security Considerations
  Summary

## · Real-time Communication  (L3316)
  源文件: backend/graph/model/models_gen.go, backend/graph/subscriptions/broadcast.go, backend/graph/subscriptions/manager.go, backend/graph/subscriptions/subscriptions.go, frontend/src/graphql.ts, frontend/src/layouts/AppLayout/AppLayout.graphql, frontend/src/layouts/AppLayout/AppLayout.tsx
  Purpose and Scope
  Architecture Overview
  Subscription System
    · Backend Implementation
    · Frontend Implementation
  Subscription Types and Data Models
  Event Flow and Integration
    · Complete Event Flow
    · Integration with UI Components
  Summary

## · User Interface  (L3755)
  源文件: backend/graph/schema.resolvers.go, frontend/package.json, frontend/src/main.tsx, frontend/src/pages/ChatPage/ChatPage.tsx, frontend/yarn.lock
  Frontend Architecture Overview
  Core UI Components
  ChatPage Component Structure
  Data Flow and Real-time Updates
  Subscription System
  Dynamic Tab Management
  Task Submission Flow
  UI Components Integration with Backend
  Technology Stack
  Responsive Layout
  Conclusion

## · Main Chat Interface  (L4074)
  源文件: backend/graph/schema.resolvers.go, frontend/src/pages/ChatPage/ChatPage.css.ts, frontend/src/pages/ChatPage/ChatPage.graphql, frontend/src/pages/ChatPage/ChatPage.tsx
  Architecture Overview
  Component Layout
  Data Model and State Management
  User Interaction Flow
  GraphQL Integration
    · Key GraphQL Operations:
  Real-time Tab Management
  Backend Integration Details
  Key Components Implementation
    · ChatPage Component
    · Message Submission Implementation
  Conclusion

## · Terminal Component  (L4439)
  源文件: backend/router/router.go, frontend/src/components/Terminal/Terminal.tsx
  Purpose and Overview
  Component Architecture
  Implementation Details
    · Frontend Implementation
    · Key Component Properties
    · Terminal Initialization and Addon Loading
    · Log Rendering
    · Event Handling
    · Visual Interface
  Backend Integration
    · WebSocket Connection
    · Data Flow
  Integration with Codel
  Summary

## · Messages System  (L4725)
  源文件: frontend/src/assets/logo.png, frontend/src/assets/me.png, frontend/src/components/Messages/Message/Message.css.ts, frontend/src/components/Messages/Message/Message.tsx, frontend/src/components/Messages/Messages.css.ts, frontend/src/components/Messages/Messages.tsx, frontend/src/components/Panel/Panel.css.ts
  Component Overview
  Messages Component Structure
    · Component Properties
    · Key Features
  Message Component
    · Component Properties
    · Message Types and Styling
    · Expandable Output
  Visual Layout
  Complete Data Flow
  Message Component CSS Structure
  Interaction with TaskStatus and TaskType
  Conclusion

## · Navigation and UI Components  (L5011)
  源文件: frontend/src/components/Button/Button.css.ts, frontend/src/components/Button/Button.tsx, frontend/src/components/Panel/Panel.tsx, frontend/src/components/Sidebar/NewTask/NewTask.css.ts, frontend/src/components/Sidebar/NewTask/NewTask.tsx, frontend/src/components/Sidebar/Sidebar.css.ts, frontend/src/components/Sidebar/Sidebar.tsx, frontend/src/components/Tabs/Tabs.css.ts, frontend/src/components/Terminal/Terminal.css.ts
  Component Overview
  Sidebar Component
    · Structure and Implementation
    · NewTask Component
  Tabs Component
    · Structure and Styling
  Button Component
    · Variants and Usage
  Panel Component
  User Navigation Flow
  Component Style Consistency
  Integration with the Application

## · Deployment  (L5370)
  源文件: .dockerignore, .github/logo.png, .gitignore, DEVELOPMENT.md, Dockerfile, README.md, backend/.env.example, backend/.gitignore, frontend/.env.example
  Deployment Overview
  Basic Docker Deployment
  Environment Variables Configuration
  Docker Socket Configuration
  Deployment Architecture Components
  Container Build Process
  Production Deployment Best Practices
  Deployment Configuration Flow
  Development Environment Setup
  Troubleshooting
  Related Documentation

## · Application Bootstrapping  (L5647)
  源文件: backend/go.mod, backend/go.sum, backend/main.go, backend/models/models.go, frontend/index.html, frontend/public/android-chrome-192x192.png, frontend/src/App.tsx, frontend/src/vite-env.d.ts, frontend/tsconfig.json, frontend/vite.config.ts
  Overview
  Backend Bootstrapping
    · Backend Bootstrapping Sequence
    · Backend Embedded Resources
    · Database Initialization
    · Docker and Browser Initialization
  Frontend Bootstrapping
    · Frontend Initialization Sequence
    · React Application Structure
  Environment Configuration
    · Backend Configuration
    · Frontend Environment Variables
  GraphQL API Initialization
  Initialization Lifecycle
  Shutdown Process
  Data Models Used During Bootstrapping
  Conclusion