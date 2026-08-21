# Skeleton: plandex（33 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Introduction to Plandex | L6 | 11KB | 3 | ~2 | 11 |
| 2 | Installation and Quick Start | L290 | 11KB | 3 | ~3 | 11 |
| 3 | Core Concepts | L639 | 12KB | 7 | ~13 | 11 |
| 4 | System Architecture Overview | L1005 | 11KB | 7 | ~0 | 18 |
| 5 | CLI Reference | L1374 | 21KB | 11 | ~8 | 6 |
| 6 | REPL Interface | L2043 | 13KB | 7 | ~6 | 6 |
| 7 | Plan Execution Commands | L2458 | 18KB | 8 | ~13 | 15 |
| 8 | Context Management Commands | L2938 | 9KB | 5 | ~3 | 3 |
| 9 | Model Configuration Commands | L3176 | 12KB | 4 | ~5 | 7 |
| 10 | Streaming Terminal UI | L3572 | 16KB | 9 | ~6 | 5 |
| 11 | Plan Execution System | L4077 | 14KB | 7 | ~1 | 7 |
| 12 | Plan Lifecycle and States | L4511 | 14KB | 10 | ~7 | 7 |
| 13 | AI Model Integration and Task Control | L4896 | 14KB | 10 | ~4 | 20 |
| 14 | File Modification Pipeline | L5338 | 14KB | 8 | ~6 | 10 |
| 15 | Server Architecture | L5773 | 32KB | 17 | ~4 | 6 |
| 16 | HTTP API and Request Handlers | L6504 | 25KB | 9 | ~14 | 17 |
| 17 | Data Models and Shared Types | L7156 | 11KB | 10 | ~0 | 5 |
| 18 | Active Plan Management | L7561 | 12KB | 6 | ~0 | 12 |
| 19 | AI Model Integration | L7855 | 15KB | 9 | ~2 | 13 |
| 20 | Model Configuration and Management | L8286 | 13KB | 9 | ~2 | 20 |
| 21 | Context and Token Management | L8711 | 11KB | 11 | ~4 | 16 |
| 22 | Response Processing and Error Handling | L9047 | 12KB | 7 | ~8 | 13 |
| 23 | Data Storage and Management | L9378 | 18KB | 11 | ~7 | 9 |
| 24 | Database Schema and Migrations | L9978 | 16KB | 7 | ~4 | 11 |
| 25 | Repository Locking and Git Integration | L10479 | 15KB | 10 | ~3 | 9 |
| 26 | Authentication and User Management | L10852 | 14KB | 6 | ~10 | 11 |
| 27 | Development and Deployment | L11266 | 18KB | 5 | ~15 | 7 |
| 28 | Module Dependencies and Architecture | L11866 | 18KB | 9 | ~16 | 7 |
| 29 | Local Development Environment | L12377 | 9KB | 7 | ~3 | 13 |
| 30 | Self-Hosting Plandex | L12640 | 14KB | 12 | ~6 | 17 |
| 31 | Version History and Releases | L13145 | 14KB | 5 | ~4 | 7 |
| 32 | CLI Release History | L13492 | 11KB | 3 | ~6 | 7 |
| 33 | Server Release History | L13802 | 10KB | 3 | ~11 | 3 |


## · Introduction to Plandex  (L6)
  源文件: README.md, docs/docs/cli-reference.md, docs/docs/environment-variables.md, docs/docs/hosting/cloud.md, docs/docs/hosting/self-hosting/_category_.json, docs/docs/hosting/self-hosting/advanced-self-hosting.md, docs/docs/hosting/self-hosting/local-mode-quickstart.md, docs/docs/install.md, docs/docs/models/claude-subscription.md, docs/docs/models/models-overview.md, docs/docs/quick-start.md
  Purpose and Scope
  What is Plandex
  System Architecture Overview
  Core Components
    · Key Component Descriptions
  Key Concepts
    · Plans and Branches
    · Context Management
    · Model Packs and Roles
    · Plan Lifecycle
  Workflow Overview
  Hosting and Deployment Options
  Next Steps

## · Installation and Quick Start  (L290)
  源文件: README.md, docs/docs/cli-reference.md, docs/docs/environment-variables.md, docs/docs/hosting/cloud.md, docs/docs/hosting/self-hosting/_category_.json, docs/docs/hosting/self-hosting/advanced-self-hosting.md, docs/docs/hosting/self-hosting/local-mode-quickstart.md, docs/docs/install.md, docs/docs/models/claude-subscription.md, docs/docs/models/models-overview.md, docs/docs/quick-start.md
  Installation Methods
    · Quick Install
    · Manual Install
    · Build from Source
    · Platform Support
  Deployment Options
    · 1. Plandex Cloud (Integrated Models)
    · 2. Plandex Cloud (BYO API Key)
    · 3. Self-hosted/Local Mode
  API Key Setup
    · OpenRouter.ai API Key
    · OpenAI API Key
  Quick Start Guide
    · Basic Steps
    · Using REPL Flags
  Self-Hosting Setup
    · Local Mode Quickstart
    · Docker Compose Configuration
    · Advanced Self-Hosting
  Environment Variables
  Next Steps

## · Core Concepts  (L639)
  源文件: README.md, docs/docs/cli-reference.md, docs/docs/environment-variables.md, docs/docs/hosting/cloud.md, docs/docs/hosting/self-hosting/_category_.json, docs/docs/hosting/self-hosting/advanced-self-hosting.md, docs/docs/hosting/self-hosting/local-mode-quickstart.md, docs/docs/install.md, docs/docs/models/claude-subscription.md, docs/docs/models/models-overview.md, docs/docs/quick-start.md
  Plans and Plan Lifecycle
    · Plan States and Commands
  Context Management
    · Context Types and Token Management
  AI Model Integration: Roles and Model Packs
    · Model Configuration Commands
  Autonomy Levels
    · Autonomy Configuration
  Branches and Version Control
    · Branch Management Commands
  Streaming and Real-time Interaction
    · Stream States and Control
  Core Concept Relationships

## · System Architecture Overview  (L1005)
  源文件: README.md, app/cli/go.mod, app/cli/go.sum, app/server/go.mod, app/server/go.sum, app/shared/go.mod, app/shared/go.sum, docs/docs/cli-reference.md, docs/docs/environment-variables.md, docs/docs/hosting/cloud.md, docs/docs/hosting/self-hosting/_category_.json, docs/docs/hosting/self-hosting/advanced-self-hosting.md
  Architecture Overview
    · High-Level System Components
    · Module Structure and Dependencies
  Client-Server Communication
    · API Communication Flow
  Data Storage Architecture
    · Data Storage Components
  AI Model Integration
    · Model Provider Architecture
  Plan Execution Pipeline
    · Plan Execution Flow
  Hosting and Deployment
    · Deployment Architecture

## · CLI Reference  (L1374)
  源文件: app/cli/cmd/current.go, app/cli/cmd/new.go, app/cli/cmd/plan_start_helpers.go, app/cli/cmd/repl.go, app/cli/cmd/root.go, app/cli/term/help.go
  Command Structure and Organization
  REPL Architecture
  Command Execution Flow
  REPL Command Processing
  Plan Management Commands
  Context Management Commands
  Configuration Management
  Model Management Commands
  Streaming and Background Execution
  Command Auto-completion and Suggestions
  Command Help System

## · REPL Interface  (L2043)
  源文件: app/cli/cmd/current.go, app/cli/cmd/new.go, app/cli/cmd/plan_start_helpers.go, app/cli/cmd/repl.go, app/cli/cmd/root.go, app/cli/term/help.go
  Purpose and Scope
  REPL Architecture Overview
  Command Processing Flow
  Mode Management and State
    · Mode Switching
  Autocomplete and Suggestion System
  File Reference Processing
  Multi-line Editing Support
  Command Validation and Error Handling
  Integration with CLI Commands

## · Plan Execution Commands  (L2458)
  源文件: app/cli/cmd/build.go, app/cli/cmd/chat.go, app/cli/cmd/continue.go, app/cli/cmd/debug.go, app/cli/cmd/tell.go, app/cli/lib/apply.go, app/cli/main.go, app/cli/plan_exec/action_menu.go, app/cli/plan_exec/apply_exec.go, app/cli/plan_exec/build.go, app/cli/plan_exec/params.go, app/cli/plan_exec/tell.go
  Command Overview
  Core Execution Commands
    · Tell Command
    · Continue Command
    · Build Command
    · Apply Command
    · Chat Command
    · Debug Command
  Execution Flags and Options
    · Automation Flags
    · File and Editor Flags
    · Apply-Specific Flags
    · Debug-Specific Flags
  Plan Execution Pipeline
  Apply Execution Pipeline  
  Interactive Action Menu
    · Available Hotkeys
  Auto-Apply and Retry Logic
  Error Handling and Validation
    · Context Validation
    · API Error Handling  
    · Build Validation

## · Context Management Commands  (L2938)
  源文件: app/cli/lib/context_load.go, app/cli/lib/context_update.go, app/cli/types/types.go
  Overview and Context Types
    · Supported Context Types
  Context Loading Process
    · Concurrent Processing and Limits
  Context Update and Synchronization
    · Outdated Context Detection
    · Update Request Processing
  Key Data Structures
    · LoadContextParams
    · Context Processing Results
  CLI Command Integration
    · Command Processing Flow

## · Model Configuration Commands  (L3176)
  源文件: app/cli/cmd/model_packs.go, app/cli/cmd/model_providers.go, app/cli/cmd/models.go, app/cli/cmd/set_model.go, app/cli/lib/model_settings.go, app/server/handlers/models.go, app/shared/ai_models_custom.go
  Purpose and Scope
  Core Concepts
    · Model Roles
    · Model Packs
    · Custom Models and Providers
  Command Hierarchy
  Viewing Model Configurations
    · Current Plan Model Settings
    · Organization Default Settings
    · Available Models
  Setting Model Configurations
    · Model Pack Selection
    · JSON-Based Configuration
  Managing Custom Models and Providers
    · Custom Models Management
    · Example Template Structure
    · Model Providers
    · Model Packs Management
  Server-Side Model Management
    · Custom Models API
    · Data Flow for Custom Models
  Command Reference

## · Streaming Terminal UI  (L3572)
  源文件: app/cli/stream_tui/model.go, app/cli/stream_tui/run.go, app/cli/stream_tui/update.go, app/cli/stream_tui/view.go, app/server/types/active_plan.go
  Architecture Overview
    · Streaming UI Component Architecture
    · Message Flow and State Synchronization
  UI State Management
    · Core State Structure
    · State Synchronization Patterns
  Message Types and Processing
    · Stream Message Types
    · Build Progress Message Handling
  User Interactions and Controls
    · Keyboard Controls
    · Scroll and Navigation Handling
  Build Progress Display
    · Build Display Components
    · File Status Indicators
  Missing File Prompts
    · Missing File Prompt Flow
  Server-Side Streaming Infrastructure
    · Subscription Management

## · Plan Execution System  (L4077)
  源文件: app/server/model/plan/tell_exec.go, app/server/model/plan/tell_load.go, app/server/model/plan/tell_state.go, app/server/model/plan/tell_stream_finish.go, app/server/model/plan/tell_stream_main.go, app/server/model/plan/tell_stream_processor.go, app/server/model/plan/tell_summary.go
  Core Execution Flow
  Plan Stages and State Management
  Context and Token Management
  Streaming Response Processing
  Error Handling and Retry Logic
  Auto-Continuation and Completion Logic
  Missing File Handling

## · Plan Lifecycle and States  (L4511)
  源文件: app/server/model/plan/tell_exec.go, app/server/model/plan/tell_load.go, app/server/model/plan/tell_state.go, app/server/model/plan/tell_stream_finish.go, app/server/model/plan/tell_stream_main.go, app/server/model/plan/tell_stream_processor.go, app/server/model/plan/tell_summary.go
  Plan State Overview
    · Database Plan States
  Tell Execution Lifecycle
    · Main Execution Flow
    · Tell Stages and Model Selection
    · Plan Loading and State Initialization
  Streaming Response Processing
    · Stream Processing Flow
    · Chunk Processing and Operation Detection
    · Content Buffering and Stream Management
  Active Plan State Management
    · activeTellStreamState Structure
    · Chunk Processing State
    · State Management Functions
    · Plan Continuation Logic
  Conversation and Summary Management
    · Token Management Flow

## · AI Model Integration and Task Control  (L4896)
  源文件: app/cli/lib/model_credentials.go, app/server/model/client.go, app/server/model/client_stream.go, app/server/model/model_error.go, app/server/model/model_request.go, app/server/model/name.go, app/server/model/plan/build_exec.go, app/server/model/plan/commit_msg.go, app/server/model/plan/exec_status.go, app/server/model/plan/tell_stream_error.go, app/server/model/prompts/exec_status.go, app/server/model/summarize.go
  Model Provider Architecture
    · Supported Providers
    · Provider Configuration Schema
  Model Configuration and Roles
    · Model Role Specialization
    · Model Pack Configuration
  AI Client Management
    · Client Initialization Flow
    · Request Creation and Streaming
  Task Execution Control
    · Task Completion Assessment
    · AI Model Evaluation Logic
  Error Handling and Fallback
    · Error Classification System
    · Fallback Resolution Logic
  Streaming and Response Processing
    · Stream Processing Architecture
    · Model Response Types

## · File Modification Pipeline  (L5338)
  源文件: app/server/model/plan/build_finish.go, app/server/model/plan/build_load.go, app/server/model/plan/build_state.go, app/server/model/plan/build_structured_edits.go, app/server/model/plan/build_validate_and_fix.go, app/server/model/plan/build_whole_file.go, app/server/model/plan/tell_stream_usage.go, app/server/types/model.go, app/shared/plan_result_replacements.go, app/shared/streamed_change.go
  Purpose and Scope
  Pipeline Overview
  Build State Management
  Structured Edits Processing
    · Main Processing Flow
    · Syntax Validation and Error Handling
  Validation and Fix Loop
    · Validation Loop Architecture
    · XML Response Processing
  Replacement Application System
    · Replacement Processing
    · Git Integration and Commit Process
  Error Handling and Retry Logic
    · Retry Mechanisms
  Performance Optimizations

## · Server Architecture  (L5773)
  源文件: app/cli/api/clients.go, app/server/db/user_helpers.go, app/server/handlers/sessions.go, app/server/main.go, app/server/routes/routes.go, app/server/setup/setup.go
  Overview
  HTTP Server Configuration
  Route Organization
  Authentication and Session Management
  Database Integration and User Management
  Server Lifecycle and LiteLLM Integration
  Client-Server Communication
  HTTP Server Configuration
  Route Organization
  HTTP Server Configuration
  Route Organization
  Authentication and Session Management
  Database Integration and User Management
  Server Lifecycle and LiteLLM Integration
  Request Processing Pipeline
  Client-Server Communication
  Server Lifecycle Management

## · HTTP API and Request Handlers  (L6504)
  源文件: app/cli/api/clients.go, app/cli/lib/git.go, app/server/db/result_helpers.go, app/server/db/user_helpers.go, app/server/handlers/branches.go, app/server/handlers/client_helper.go, app/server/handlers/context_helper.go, app/server/handlers/plans_changes.go, app/server/handlers/plans_context.go, app/server/handlers/plans_convo.go, app/server/handlers/plans_exec.go, app/server/handlers/plans_versions.go
  Request Handler Architecture
  API Routes Registration
  API Endpoints Overview
  Request Handler Common Patterns
    · Authentication and Authorization Flow
    · Repository Operation Pattern
  Plan Execution Request Handlers
    · TellPlanHandler Function
    · BuildPlanHandler Function
    · ConnectPlanHandler Function
    · StopPlanHandler Function
    · Build Plan
    · Connect Plan
    · Stop Plan
  Context Management Endpoints
    · LoadContextHandler Function
    · List Contexts
    · Update Context
    · Delete Context
  Plan Changes Endpoints
    · ApplyPlanHandler Function
    · RejectAllChangesHandler Function
    · RejectFileHandler and RejectFilesHandler Functions
    · Reject Changes
    · Get Plan Diffs
  Branch Management Endpoints
    · List Branches
    · Create Branch
    · Delete Branch
  Request and Response Data Structures
    · Core Request Types
    · Core Response Types
    · Context Type System
  Streaming Response Implementation
    · startResponseStream Function
    · Streaming-Enabled Handlers
  Error Handling Patterns
    · Common Error Handling Functions
    · Error Scenarios by Handler Type
    · Error Logging Pattern
  Health and Monitoring Endpoints
  API Authentication Flow
  Conclusion

## · Data Models and Shared Types  (L7156)
  源文件: app/cli/api/methods.go, app/cli/types/api.go, app/server/db/data_models.go, app/shared/data_models.go, app/shared/req_res.go
  Core Entity Models
    · Organization and User Models
    · Project and Plan Hierarchy
  Context and Content Models
    · Context Type Hierarchy
    · Context Loading and Management
  Plan Execution Models
    · Conversation and Message Flow
    · Plan State Management
  Request and Response Models
    · Plan Execution Requests
    · Response Models
  Model Conversion Patterns
    · ToApi() Conversion Pattern
    · Data Flow Architecture

## · Active Plan Management  (L7561)
  源文件: app/cli/stream_tui/model.go, app/cli/stream_tui/run.go, app/cli/stream_tui/update.go, app/cli/stream_tui/view.go, app/server/model/plan/tell_exec.go, app/server/model/plan/tell_load.go, app/server/model/plan/tell_state.go, app/server/model/plan/tell_stream_finish.go, app/server/model/plan/tell_stream_main.go, app/server/model/plan/tell_stream_processor.go, app/server/model/plan/tell_summary.go, app/server/types/active_plan.go
  Core ActivePlan Structure
  Plan Lifecycle and State Management
  Streaming and Subscription System
  Plan Execution Flow
  Build Management System
  Integration with Model Streaming

## · AI Model Integration  (L7855)
  源文件: app/cli/lib/model_credentials.go, app/server/model/client.go, app/server/model/client_stream.go, app/server/model/model_error.go, app/server/model/plan/tell_stream_error.go, app/server/types/message.go, app/shared/ai_models_available.go, app/shared/ai_models_data_models.go, app/shared/ai_models_errors.go, app/shared/ai_models_packs.go, app/shared/ai_models_providers.go, test/smoke_test.sh
  Architecture Overview
  Supported AI Model Providers
    · Client Initialization Process
  Client Configuration
  Request Processing Flow
  Message Formatting
  Streaming Response Handling
  Error Handling and Retries
  Context Management
  Model Roles System
  Provider-Specific Optimizations
  Usage Tracking
  Conclusion

## · Model Configuration and Management  (L8286)
  源文件: app/cli/cmd/model_packs.go, app/cli/cmd/model_providers.go, app/cli/cmd/models.go, app/cli/cmd/set_model.go, app/cli/lib/model_credentials.go, app/cli/lib/model_settings.go, app/server/handlers/models.go, app/server/model/client.go, app/server/model/client_stream.go, app/server/model/model_error.go, app/server/model/plan/tell_stream_error.go, app/server/types/message.go
  Model Configuration Architecture
    · Model Configuration Hierarchy
    · Model Role System
  Built-in Models and Providers
    · Available Model Definitions
    · Built-in Model Providers
  Custom Models and Providers
    · Custom Model Configuration
    · Example Custom Model Definition
  CLI Commands for Model Management
    · Primary Model Commands
    · Model Selection Workflow
  Server-Side Model Client Management
    · Client Initialization and Provider Resolution
    · Authentication and Credential Management
    · Error Handling and Fallbacks

## · Context and Token Management  (L8711)
  源文件: app/cli/lib/context_load.go, app/cli/lib/context_update.go, app/cli/lib/model_credentials.go, app/cli/types/types.go, app/server/model/client.go, app/server/model/client_stream.go, app/server/model/model_error.go, app/server/model/plan/tell_stream_error.go, app/server/types/message.go, app/shared/ai_models_available.go, app/shared/ai_models_data_models.go, app/shared/ai_models_errors.go
  Overview
  Context Types and Loading
    · Context Type Hierarchy
    · Context Loading Limits
    · Context Loading Flow
  Token Counting and Estimation
    · Token Estimation Methods
    · Model-Specific Token Limits
  Context Optimization Strategies
    · File Processing Pipeline
    · Map File Optimization
  Model Context Management
    · Context Resolution for Models
    · Cache Control Integration
  Context Update and Synchronization
    · Outdated Context Detection
    · Context Update Pipeline
  Performance and Error Handling
    · Memory Management
    · Error Recovery

## · Response Processing and Error Handling  (L9047)
  源文件: app/cli/lib/model_credentials.go, app/server/model/client.go, app/server/model/client_stream.go, app/server/model/model_error.go, app/server/model/plan/tell_stream_error.go, app/server/types/message.go, app/shared/ai_models_available.go, app/shared/ai_models_data_models.go, app/shared/ai_models_errors.go, app/shared/ai_models_packs.go, app/shared/ai_models_providers.go, test/smoke_test.sh
  Overview
  Streaming Response Processing
    · Stream Architecture
    · Stream Processing Flow
  Error Classification System
    · Error Types and Classification
    · Retry-After Parsing
  Retry and Fallback Mechanisms
    · Fallback Decision Tree
    · Fallback Types and Priority
    · Retry Configuration
  Timeout Management
    · Timeout Configuration
    · Timeout Handling Flow
  Error Recovery Strategies
    · Plan-Level Error Handling
    · Cache Support Error Handling
    · Provider Fallback Selection

## · Data Storage and Management  (L9378)
  源文件: app/server/db/db.go, app/server/db/git.go, app/server/db/locks.go, app/server/model/plan/state.go, app/server/model/plan/stop.go, app/shared/plan_model_settings.go, releases/cli/versions/0.8.3.md, releases/server/versions/0.8.4.md, releases/server/versions/2.1.3.md
  Storage Architecture Overview
    · Storage Systems Diagram
  Database Connection and Configuration
    · Database Connection Management
  Repository Locking System
    · Lock Types and Scopes
    · Lock Acquisition and Retry Logic
    · Heartbeat and Lock Lifecycle
  Git Integration and File Management
    · GitRepo Operations
    · Git Lock File Handling
  In-Memory State Management
    · Active Plan Lifecycle
    · Subscription and Real-Time Updates
  Data Serialization and Persistence
    · Plan Settings Storage
  Concurrency Control and Safety
    · Multi-Level Locking Strategy

## · Database Schema and Migrations  (L9978)
  源文件: app/server/db/db.go, app/server/db/git.go, app/server/db/locks.go, app/server/migrations/2024013000_plan_build_convo_ids.down.sql, app/server/migrations/2024013000_plan_build_convo_ids.up.sql, app/server/model/plan/state.go, app/server/model/plan/stop.go, app/shared/plan_model_settings.go, releases/cli/versions/0.8.3.md, releases/server/versions/0.8.4.md, releases/server/versions/2.1.3.md
  Database Architecture Overview
  Core Database Tables
    · User and Organization Management
    · Project and Plan Management
    · AI Model Configuration
  File-based Storage System
    · File Storage Structure
  Migration System
    · Migration Infrastructure
    · Schema Evolution Example - Plan Build Conversation IDs
  Data Access Patterns

## · Repository Locking and Git Integration  (L10479)
  源文件: app/server/db/db.go, app/server/db/git.go, app/server/db/locks.go, app/server/model/plan/state.go, app/server/model/plan/stop.go, app/shared/plan_model_settings.go, releases/cli/versions/0.8.3.md, releases/server/versions/0.8.4.md, releases/server/versions/2.1.3.md
  Lock Management System
    · Lock Types and Scopes
    · Lock Acquisition Process
    · Heartbeat Mechanism
  Git Integration Architecture
    · GitRepo Structure and Operations
    · Git Write Operations with Retry Logic
  Repository Lock Integration with Plan Execution
    · ExecRepoOperation Workflow
    · Active Plan Integration
  Concurrency Control and Error Handling
    · Lock Conflict Resolution
    · Deadlock Detection and Recovery
    · Lock Release and Cleanup

## · Authentication and User Management  (L10852)
  源文件: app/cli/api/clients.go, app/cli/api/methods.go, app/cli/types/api.go, app/server/db/data_models.go, app/server/db/user_helpers.go, app/server/handlers/sessions.go, app/server/main.go, app/server/routes/routes.go, app/server/setup/setup.go, app/shared/data_models.go, app/shared/req_res.go
  System Architecture Overview
  Core Data Models
    · Key Data Structures
  Authentication Flow
    · Authentication Components
    · Sign-in Code Flow
  Authorization and Role Management
    · Organization User Configuration
  API Endpoints and Routing
    · Client-Side API Implementation
  Session Management and Security
    · Token Management
    · Security Features
    · Organization Context Management

## · Development and Deployment  (L11266)
  源文件: app/cli/go.mod, app/cli/go.sum, app/server/go.mod, app/server/go.sum, app/shared/go.mod, app/shared/go.sum, releases/cli/versions/2.0.8.md
  Overview
    · Development and Deployment Architecture
    · Module Dependencies Comparison
  Module Dependencies and Architecture
    · Go Module Structure
    · CLI Module Dependencies
    · Server Module Dependencies
    · Shared Module Dependencies
  Local Development Environment
    · Local Development Architecture
    · Quick Development Setup
    · Building from Source
    · Development Environment Variables
    · Upgrading the Development Environment
  Self-Hosting Plandex
    · Self-Hosted Production Architecture
    · System Requirements
    · Environment Configuration
    · Deployment Methods
    · Health Monitoring
    · Client Configuration
  Security Considerations
    · API Key Security
    · File Security
  Switching Between Deployment Options
  Setup Flow Diagram

## · Module Dependencies and Architecture  (L11866)
  源文件: app/cli/go.mod, app/cli/go.sum, app/server/go.mod, app/server/go.sum, app/shared/go.mod, app/shared/go.sum, releases/cli/versions/2.0.8.md
  Module Structure
  CLI Module Dependencies
  Server Module Dependencies
  Shared Module Dependencies
  Dependency Management Architecture
  External Integration Architecture  
  Route Registration System

## · Local Development Environment  (L12377)
  源文件: app/cli/api/clients.go, app/cli/go.mod, app/cli/go.sum, app/server/db/user_helpers.go, app/server/go.mod, app/server/go.sum, app/server/handlers/sessions.go, app/server/main.go, app/server/routes/routes.go, app/server/setup/setup.go, app/shared/go.mod, app/shared/go.sum
  Environment Structure
    · Module Architecture
    · Development Dependencies
  Server Development Setup
    · Server Initialization Flow
    · Development Environment Variables
    · Database Setup
    · Local Server Startup
  CLI Development Setup
    · API Client Configuration
    · HTTP Client Architecture
    · Development CLI Usage
  Development Workflow
    · Local Development Architecture
    · Development Features
    · Database Development

## · Self-Hosting Plandex  (L12640)
  源文件: README.md, app/cli/api/clients.go, app/server/db/user_helpers.go, app/server/handlers/sessions.go, app/server/main.go, app/server/routes/routes.go, app/server/setup/setup.go, docs/docs/cli-reference.md, docs/docs/environment-variables.md, docs/docs/hosting/cloud.md, docs/docs/hosting/self-hosting/_category_.json, docs/docs/hosting/self-hosting/advanced-self-hosting.md
  Architecture Overview
  Deployment Options
    · Local Mode Quickstart
    · Advanced Self-Hosting
  Server Configuration
    · Environment Modes
    · Core Environment Variables
  Database Setup
    · PostgreSQL Requirements
  Server Lifecycle Management
    · Startup Process
    · Graceful Shutdown
  API Route Configuration
    · Route Registration
  Health Monitoring
    · Health Check Endpoints
  Security Considerations
    · Authentication Flow
    · Request Middleware
  Storage and Persistence

## · Version History and Releases  (L13145)
  源文件: app/cli/version.txt, releases/cli/CHANGELOG.md, releases/cli/versions/0.7.1.md, releases/cli/versions/2.0.0.md, releases/cli/versions/2.0.4.md, releases/server/versions/2.0.0.md, releases/server/versions/2.0.4.md
  Versioning Overview
    · Current Versions
  Release Timeline
  Version 2.x Series (Current)
    · Version 2.0.0 (Major Release)
    · Version 2.0.4
    · Version 2.1.x Series (Latest)
    · Version 2.0.5 - 2.0.7
  Version 1.x Series
    · Version 1.0.0
    · Version 1.1.0
  Version 0.x Series (Early Releases)
    · Version 0.7.0 - 0.8.x
    · Version 0.9.x
  Component Relationship and Release Process
  Feature Evolution
  Upgrade Notes

## · CLI Release History  (L13492)
  源文件: app/cli/version.txt, releases/cli/CHANGELOG.md, releases/cli/versions/0.7.1.md, releases/cli/versions/2.0.0.md, releases/cli/versions/2.0.4.md, releases/server/versions/2.0.0.md, releases/server/versions/2.0.4.md
  Release Timeline and Major Milestones
  Architecture Evolution Overview
  Major Version Milestones
    · Version 0.x - Foundation Period
    · Version 1.x - Stable Release
    · Version 2.x - Architectural Transformation
  Feature Evolution Matrix
  Configuration System Evolution
    · Version 1.x Configuration
    · Version 2.x Configuration  
    · Current Provider Support (v2.2.x)
  Command Interface Changes
    · Traditional CLI Commands (All Versions)
    · Version 2.x REPL Commands
    · Model Management Commands Evolution
  Current State (Version 2.2.1)

## · Server Release History  (L13802)
  源文件: app/server/version.txt, releases/server/CHANGELOG.md, releases/server/versions/0.8.1.md
  Current Server Version
  Release Timeline Overview
  Server Component Release Impact
  Detailed Release History
    · Version 2.1.x Series (Current) - Stability and Reliability Focus
    · Version 2.0.x Series - Architecture Modernization
    · Version 1.x Series - Performance and Intelligence Leap
    · Version 0.9.x Series - Customization and Accuracy
    · Version 0.8.x Series - Foundation and Stability
    · Version 0.7.x Series - Initial Release
  Key Technical Evolution Areas