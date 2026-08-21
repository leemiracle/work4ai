# Skeleton: gpt-pilot（33 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 7KB | 2 | ~4 | 4 |
| 2 | Getting Started | L199 | 17KB | 5 | ~10 | 10 |
| 3 | Installation and Setup | L690 | 14KB | 5 | ~8 | 5 |
| 4 | Configuration Guide | L1236 | 23KB | 6 | ~24 | 10 |
| 5 | CLI Usage and Commands | L2068 | 21KB | 9 | ~10 | 13 |
| 6 | System Architecture | L2837 | 15KB | 9 | ~0 | 13 |
| 7 | Core Components Overview | L3412 | 17KB | 9 | ~15 | 13 |
| 8 | State Management System | L3946 | 14KB | 9 | ~0 | 9 |
| 9 | Orchestrator and Control Flow | L4311 | 23KB | 12 | ~8 | 13 |
| 10 | UI and Communication Layer | L4997 | 19KB | 7 | ~6 | 13 |
| 11 | Agent System | L5613 | 43KB | 16 | ~4 | 9 |
| 12 | Agent Architecture and Base Classes | L6820 | 30KB | 7 | ~11 | 14 |
| 13 | Planning Agents | L7742 | 18KB | 6 | ~9 | 13 |
| 14 | Implementation Agents | L8249 | 28KB | 7 | ~4 | 11 |
| 15 | Frontend Development Agent | L9141 | 27KB | 14 | ~21 | 8 |
| 16 | Quality Assurance Agents | L9870 | 27KB | 8 | ~4 | 9 |
| 17 | Specialized Agents | L10599 | 18KB | 6 | ~5 | 8 |
| 18 | LLM Integration | L11124 | 13KB | 5 | ~5 | 15 |
| 19 | Configuration System | L11534 | 15KB | 5 | ~4 | 6 |
| 20 | LLM Client Architecture | L12049 | 18KB | 4 | ~7 | 18 |
| 21 | Prompt Engineering System | L12607 | 18KB | 7 | ~9 | 19 |
| 22 | Development Workflow | L13120 | 25KB | 8 | ~7 | 9 |
| 23 | Project Lifecycle and Stages | L13790 | 33KB | 13 | ~0 | 17 |
| 24 | Code Generation and File Management | L14899 | 19KB | 10 | ~13 | 15 |
| 25 | Context Filtering and Relevance | L15516 | 15KB | 7 | ~6 | 14 |
| 26 | User Testing and Feedback Loop | L15978 | 22KB | 8 | ~8 | 9 |
| 27 | Project Templates | L16611 | 7KB | 5 | ~3 | 10 |
| 28 | Template Architecture | L16826 | 14KB | 8 | ~5 | 8 |
| 29 | Vite React Templates | L17277 | 17KB | 9 | ~13 | 16 |
| 30 | Deployment and Operations | L17784 | 15KB | 10 | ~11 | 4 |
| 31 | Docker Environment | L18230 | 8KB | 6 | ~4 | 9 |
| 32 | Cloud Deployment | L18468 | 19KB | 5 | ~13 | 9 |
| 33 | Continuous Integration | L19043 | 14KB | 7 | ~10 | 5 |


## · Overview  (L6)
  源文件: CHANGELOG.md, README.md, pyproject.toml, requirements.txt
  Purpose and Scope
  Core Philosophy
  System Architecture
    · High-Level Architecture Diagram
  Development Workflow
    · Agent Workflow Diagram
  Agent Roles and Responsibilities
  Key Capabilities and Differentiators
  Using GPT Pilot

## · Getting Started  (L199)
  源文件: CHANGELOG.md, README.md, core/config/__init__.py, core/llm/anthropic_client.py, data/database/.gitkeep, example-config.json, pyproject.toml, requirements.txt, tests/config/test_config.py, tests/config/test_env_importer.py
  Prerequisites
  System Initialization Flow
    · Startup Sequence Diagram
  Quick Start Overview
    · 1. Clone and Setup
    · 2. Configure API Access
    · 3. Start GPT Pilot
  Configuration Loading Process
    · Configuration Flow Diagram
  Project Workspace Structure
    · Workspace Directory Tree
  First Project Workflow
    · New Project Initialization Flow
  CLI Command Patterns
    · Common CLI Operations
    · CLI Argument Processing Flow
  Environment and Dependencies
    · Core Dependencies
    · Optional Dependencies
  Next Steps

## · Installation and Setup  (L690)
  源文件: .github/workflows/ci.yml, CHANGELOG.md, README.md, pyproject.toml, requirements.txt
  Prerequisites
  Installation Methods
    · Installation Flow
  Using Poetry (Recommended for Development)
    · Installation Steps
  Using pip (Standard Installation)
    · Installation Steps
  Core Dependencies
  Dependency Architecture
  Initial Configuration
    · Configuration Setup Steps
    · Minimal Configuration Structure
  Database Setup
    · SQLite (Default)
    · PostgreSQL (Optional)
  Database Migration System
  Environment Variables
    · Supported Environment Variables
  Verification and Testing
    · 1. Check CLI Help
    · 2. List Projects
    · 3. Run Test Suite (Development Only)
  Workspace Structure
  Troubleshooting Common Installation Issues
    · Import Errors
    · Database Connection Errors
    · API Key Errors
    · Poetry Lock File Issues
  Next Steps

## · Configuration Guide  (L1236)
  源文件: CHANGELOG.md, README.md, core/config/__init__.py, core/llm/anthropic_client.py, data/database/.gitkeep, example-config.json, pyproject.toml, requirements.txt, tests/config/test_config.py, tests/config/test_env_importer.py
  Configuration File Structure
    · Creating the Configuration File
    · Configuration File Schema
  LLM Provider Configuration
    · Provider Configuration Structure
    · Supported LLM Providers
    · Example Provider Configurations
  Agent-to-Model Mapping
    · Agent Configuration Structure
    · Agent Resolution Flow
    · Default Agent Configurations
    · Custom Agent Configuration Example
  Database Configuration
    · Database Configuration Structure
    · Supported Database Types
    · SQLite Configuration (Default)
    · PostgreSQL Configuration
  File System Configuration
    · File System Configuration Structure
    · Default Ignore Patterns
    · Example File System Configuration
  UI Adapter Configuration
    · Available UI Adapters
    · Plain UI Configuration
    · IPC Client Configuration
    · Virtual UI Configuration
  Logging Configuration
    · Logging Configuration Structure
    · Example Logging Configuration
  Prompt Template Configuration
    · Prompt Configuration Structure
    · Example Prompt Configuration
  Configuration Loading and Validation
    · Configuration Loading Flow
    · Configuration Class Hierarchy
    · Accessing Configuration
  Advanced Configuration Topics
    · AWS Bedrock Support
    · Environment Variable Fallbacks
    · Configuration File Encoding
  Configuration Validation Errors
  Complete Configuration Example

## · CLI Usage and Commands  (L2068)
  源文件: CHANGELOG.md, README.md, core/cli/helpers.py, core/cli/main.py, core/db/models/project.py, core/db/models/project_state.py, core/db/v0importer.py, core/state/state_manager.py, core/ui/api_server.py, pyproject.toml, requirements.txt, tests/cli/test_cli.py
  Overview
  Command Structure
    · Basic Invocation
  Project Management Commands
    · Listing Projects
    · Creating a New Project
    · Loading Existing Projects
    · Deleting Projects
  Configuration Options
    · Config File Path
    · Show Default Configuration
    · Log Level
    · Database URL
  LLM Configuration Options
    · LLM Endpoint
    · LLM API Key
  IPC and Extension Options
    · Local IPC Connection
    · API Server Options
    · Extension Version
  Advanced Options
    · Import Legacy Database
    · Email for Telemetry
    · Git Version Control
    · Access Token
    · Auto-Confirm Breakdown
  Command-Line Argument Reference
  Usage Examples
    · Basic Development Workflow
    · Advanced Workflows
  State Management and Persistence
    · Project State Hierarchy
    · Workspace File System
  Error Handling and Exit Codes
    · Exit Codes
    · Signal Handling
  Integration with Other Components
    · Orchestrator Invocation
    · UI Abstraction
  Telemetry and Analytics

## · System Architecture  (L2837)
  源文件: core/agents/architect.py, core/agents/frontend.py, core/agents/orchestrator.py, core/agents/spec_writer.py, core/cli/helpers.py, core/cli/main.py, core/db/models/project.py, core/db/models/project_state.py, core/db/v0importer.py, core/state/state_manager.py, core/ui/api_server.py, tests/cli/test_cli.py
  Overview
  Agent System
    · Orchestrator
    · Agent Roles and Workflow
  State Management
    · State Persistence Flow
    · Project Structure
  Infrastructure Layer
    · LLM Integration
    · UI Abstraction
    · Process Management
  Development Workflow
  Conclusion

## · Core Components Overview  (L3412)
  源文件: core/agents/architect.py, core/agents/frontend.py, core/agents/orchestrator.py, core/agents/spec_writer.py, core/cli/helpers.py, core/cli/main.py, core/db/models/project.py, core/db/models/project_state.py, core/db/v0importer.py, core/state/state_manager.py, core/ui/api_server.py, tests/cli/test_cli.py
  System Entry Point and Initialization
  Component Architecture
  StateManager: Project State and Persistence
  Orchestrator: Central Control Flow
  Agent System: Specialized AI Workers
  UI Layer: User Interaction Abstraction
  File System and Database Integration
  Execution Flow Summary

## · State Management System  (L3946)
  源文件: core/cli/helpers.py, core/cli/main.py, core/db/models/project.py, core/db/models/project_state.py, core/db/v0importer.py, core/state/state_manager.py, core/ui/api_server.py, tests/cli/test_cli.py, tests/db/test_project.py
  Overview
  State Manager
  Project State Structure
    · Epics
    · Tasks
    · Steps
    · Iterations
  File Management
  Knowledge Base
  State Transitions
  Agent Interaction with State Management
  Persistence 
  Offline Changes Management
  Conclusion

## · Orchestrator and Control Flow  (L4311)
  源文件: core/agents/architect.py, core/agents/frontend.py, core/agents/orchestrator.py, core/agents/spec_writer.py, core/cli/helpers.py, core/cli/main.py, core/db/models/project.py, core/db/models/project_state.py, core/db/v0importer.py, core/state/state_manager.py, core/ui/api_server.py, tests/cli/test_cli.py
  Orchestrator Architecture
    · Class Structure
  Main Control Loop
    · Control Flow State Machine
    · Loop Implementation Details
  Agent Creation and Selection
    · Agent Selection Logic
  Response Type System
    · Response Type Enumeration
    · Response Handling Flow
  State Commitment Process
    · Commit Transaction Flow
  Parallel Agent Execution
    · Parallel Execution Architecture
    · Implementation Details
  Initialization and Setup
    · Initialization Sequence
    · Key Initialization Methods
  Entry Point Integration
    · Application Startup Flow
    · Main Entry Points
  Error Handling and Recovery
    · Exception Handling Strategy
    · Error Types and Handling
  File Import and Description Pipeline
    · File Processing Pipeline
    · Implementation Details
  Knowledge Base Updates
    · Knowledge Base Update Logic
    · Implementation References
  Orchestrator Lifecycle Summary
    · Complete Workflow Diagram

## · UI and Communication Layer  (L4997)
  源文件: core/cli/helpers.py, core/cli/main.py, core/db/models/project.py, core/db/models/project_state.py, core/db/v0importer.py, core/state/state_manager.py, core/ui/api_server.py, core/ui/base.py, core/ui/console.py, core/ui/ipc_client.py, core/ui/virtual.py, tests/cli/test_cli.py
  Purpose and Scope
  Architecture Overview
    · UI Adapter Diagram
  UIBase Abstract Class
    · Core Method Categories
    · UISource and Message Attribution
  PlainConsoleUI Implementation
    · Key Implementation Details
  IPCClientUI and VSCode Extension
    · Connection Architecture
    · Message Protocol
  Message Types
    · Message Type Categories
    · Key Message Types
  IPCClientUI Send Methods
    · Streaming Messages
    · User Questions
    · File Diffs
  Message Flow Patterns
    · Pattern 1: Streaming LLM Responses
    · Pattern 2: User Input Request-Response
    · Pattern 3: File Status Updates
  IPCServer: API Server for External Clients
    · Server Architecture
    · Handler Registration
    · Key Handler: Chat Message
  UI Initialization and Selection
    · Configuration-Based Selection
    · UI Instantiation
    · StateManager Integration
  Error Handling and Connection Management
    · Connection Lifecycle
    · UIClosedError Handling
  VirtualUI for Testing
  Integration with StateManager
    · Example: Project Load Notification
  Summary

## · Agent System  (L5613)
  源文件: core/agents/architect.py, core/agents/bug_hunter.py, core/agents/developer.py, core/agents/frontend.py, core/agents/mixins.py, core/agents/orchestrator.py, core/agents/spec_writer.py, core/agents/tech_lead.py, core/agents/troubleshooter.py
  Agent Architecture and Base Classes
    · BaseAgent Class
    · Agent Mixins
    · AgentResponse System
    · Orchestrator
  Planning Agents
    · SpecWriter
    · Architect
    · TechLead
  Implementation Agents
    · Developer
    · CodeMonkey
  Frontend Development Agent
    · Frontend
  Quality Assurance Agents
    · Troubleshooter
    · BugHunter
    · Frontend
    · Code Monkey
  Common Agent Mixins
  Agent Communication
  State Management

## · Agent Architecture and Base Classes  (L6820)
  源文件: core/agents/base.py, core/agents/bug_hunter.py, core/agents/developer.py, core/agents/mixins.py, core/agents/tech_lead.py, core/agents/troubleshooter.py, core/llm/azure_client.py, core/llm/base.py, core/llm/openai_client.py, core/utils/__init__.py, core/utils/text.py, tests/agents/test_base.py
  Overview of the Agent System
    · Agent Class Hierarchy
  BaseAgent Core Architecture
    · Key Properties and Initialization
    · Agent Initialization Pattern
  Agent Lifecycle and Execution
    · Agent Execution Flow
    · The run() Method Contract
  State Management: current_state vs next_state
    · State Access Pattern
    · State Properties Implementation
    · Common State Operations
  UI Communication Interface
    · Communication Methods
    · send_message() Method
    · ask_question() Method
  LLM Integration Pattern
    · LLM Request Flow
    · get_llm() Method
    · LLM Client Configuration by Agent
    · stream_handler() and Error Handling
  Agent Mixins and Reusable Components
    · Available Mixins
    · RelevantFilesMixin
    · ChatWithBreakdownMixin
    · IterationPromptMixin
  Agent Type Registration
  Common Agent Patterns
    · Pattern 1: Conditional Logic in run()
    · Pattern 2: Progressive Message Updates
    · Pattern 3: Two-Phase Operations (LLM + Parse)
    · Pattern 4: Flag Modifications for Persistence
    · Pattern 5: Async Task Management
  Testing Agent Implementations
    · Unit Testing Pattern
  Summary

## · Planning Agents  (L7742)
  源文件: core/agents/architect.py, core/agents/bug_hunter.py, core/agents/developer.py, core/agents/frontend.py, core/agents/mixins.py, core/agents/orchestrator.py, core/agents/spec_writer.py, core/agents/tech_lead.py, core/agents/troubleshooter.py, core/prompts/developer/parse_task.prompt, core/prompts/partials/project_tasks.prompt, core/prompts/tech-lead/epic_breakdown.prompt
  Purpose and Scope
  Overview
  SpecWriter Agent
    · Key Responsibilities
    · State Updates
    · Complexity Assessment
  Architect Agent
    · Pydantic Models
    · State Updates
    · Compatibility Warnings
  TechLead Agent
    · Epic and Task Hierarchy
    · Key Data Structures
    · Epic Planning Process
    · Task Structure
    · Special Case: Authentication Task
    · Feature Request Flow
  Workflow and Iteration
    · Initial Project Flow
    · Feature Iteration Flow
  Conclusion

## · Implementation Agents  (L8249)
  源文件: core/agents/bug_hunter.py, core/agents/code_monkey.py, core/agents/developer.py, core/agents/mixins.py, core/agents/tech_lead.py, core/agents/troubleshooter.py, core/prompts/bug-hunter/iteration.prompt, core/prompts/bug-hunter/log_data.prompt, core/prompts/developer/breakdown.prompt, core/prompts/problem-solver/get_alternative_solutions.prompt, core/prompts/troubleshooter/iteration.prompt
  Purpose and Scope
  Implementation Flow Overview
  Developer Agent: Task Breakdown
    · Agent Architecture
    · Task Breakdown Workflow
    · Step Types and Data Structures
    · LLM Prompts and Context Management
    · User Interaction Points
    · Iteration Handling
  CodeMonkey Agent: Code Generation
    · Agent Architecture
    · Code Implementation Workflow
    · Implementation Strategy: Relace vs. OpenAI
    · Code Block Extraction
    · File Metadata Generation
    · Diff Generation and File Saving
  Integration with Orchestrator
  Error Handling and Retries
    · Developer: Incomplete Code Generation
    · CodeMonkey: Review Feedback Loop (Disabled)
  Configuration and LLM Assignments
  Summary: Implementation Pipeline

## · Frontend Development Agent  (L9141)
  源文件: core/agents/architect.py, core/agents/frontend.py, core/agents/orchestrator.py, core/agents/spec_writer.py, core/agents/wizard.py, core/templates/tree/vite_react/client/src/api/api.ts, core/templates/tree/vite_react_swagger/client/.env, core/templates/tree/vite_react_swagger/client/src/api/api.ts
  Purpose and Scope
  Agent Architecture
    · Class Structure
  Frontend Development Workflow
    · State Transition Flow
  Initial Frontend Build
    · Start Frontend Process
  Continuation and Completion
    · Continue Frontend Logic
  User Feedback and Iteration
    · Iterate Frontend Cycle
  Response Processing System
    · Code Block Processing
  Mock Removal System
    · Swagger API Integration
  Auto-Debugging System
    · Frontend Error Detection
  LLM Integration
    · Prompt Templates and Parsing
  State Management
    · Epic State Structure
  Application Setup Methods
    · Runtime Configuration
  Completion and Handoff
    · End Frontend Iteration
  Integration with Project Templates
    · Template Application
  Error Handling
    · Exception Management
  Summary Table
    · Key Methods and Their Roles

## · Quality Assurance Agents  (L9870)
  源文件: core/agents/bug_hunter.py, core/agents/developer.py, core/agents/legacy_handler.py, core/agents/mixins.py, core/agents/tech_lead.py, core/agents/troubleshooter.py, core/db/migrations/versions/f708791b9270_adding_knowledge_base_field_to_.py, core/prompts/troubleshooter/define_user_review_goal.prompt, core/prompts/troubleshooter/get_route_files.prompt
  Agent Architecture
  Iteration Status Lifecycle
  QA Workflow Overview
  Troubleshooter Agent
    · Main Entry Point: `run()`
    · Test Instruction Generation
    · Run Command Detection
    · User Feedback Collection
    · Iteration Creation
    · Loop Detection and Alternative Solutions
    · Task Completion
  BugHunter Agent
    · Main Entry Point: `run()`
    · Bug Reproduction Instructions
    · Log Analysis: `check_logs()`
    · Bug Hunting Cycles
    · User Testing After Fix
    · Pair Programming Mode
  Integration with Developer Agent
  Completing Tasks
  Implementation Details
    · Mixins
    · Key Methods
  Conclusion

## · Specialized Agents  (L10599)
  源文件: core/agents/legacy_handler.py, core/agents/wizard.py, core/db/migrations/versions/f708791b9270_adding_knowledge_base_field_to_.py, core/prompts/troubleshooter/define_user_review_goal.prompt, core/prompts/troubleshooter/get_route_files.prompt, core/templates/tree/vite_react/client/src/api/api.ts, core/templates/tree/vite_react_swagger/client/.env, core/templates/tree/vite_react_swagger/client/src/api/api.ts
  Overview
  Wizard Agent
    · Purpose and Entry Point
    · Swagger Project Initialization
    · Knowledge Base Creation
    · Template Configuration Integration
    · Initial Epic Creation
  LegacyHandler Agent
    · Purpose
    · Supported Legacy Actions
  CodeReviewer Agent
    · Configuration Reference
  Integration with Main Workflow
    · Agent Invocation Map
    · State Transitions
  Database Schema Integration
    · KnowledgeBase Model
  Best Practices for Extending Specialized Agents

## · LLM Integration  (L11124)
  源文件: core/agents/base.py, core/config/__init__.py, core/llm/anthropic_client.py, core/llm/azure_client.py, core/llm/base.py, core/llm/openai_client.py, core/utils/__init__.py, core/utils/text.py, data/database/.gitkeep, example-config.json, tests/agents/test_base.py, tests/config/test_config.py
  Configuration System Overview
    · Configuration Hierarchy
    · Configuration File Structure
    · Provider Configurations
    · Agent-Specific LLM Configurations
  Configuration Loading Process
    · Default Configuration
  LLM Provider Integration
    · LLM Integration Architecture
    · Supported Providers
    · Provider-Specific Adaptations
    · Special Configuration for AWS Bedrock
  Command-Line Configuration
    · Available Command-Line Options
    · Example Usage
  Agent-Specific LLM Selection
  Common Usage Patterns
    · Setting Up a New Provider
    · Using Different Models for Specialized Tasks
  Conclusion

## · Configuration System  (L11534)
  源文件: core/config/__init__.py, core/llm/anthropic_client.py, data/database/.gitkeep, example-config.json, tests/config/test_config.py, tests/config/test_env_importer.py
  Configuration Overview
  Configuration Structure
  Configuration Loading Process
  LLM Providers Configuration
    · Supported Providers
    · Provider Configuration
  Agent-Specific LLM Configuration
    · Agent Configuration Structure
    · Agent Configuration Resolution
  Database Configuration
    · Database URL Format
  File System Configuration
    · Workspace and Ignore Patterns
  UI Configuration
  Command-Line Configuration Overrides
  Configuration Example
  Working with Configuration Programmatically
  Configuration Validation

## · LLM Client Architecture  (L12049)
  源文件: Dockerfile, cloud/posthog.html, core/agents/base.py, core/config/__init__.py, core/llm/anthropic_client.py, core/llm/azure_client.py, core/llm/base.py, core/llm/openai_client.py, core/llm/relace_client.py, core/utils/__init__.py, core/utils/text.py, data/database/.gitkeep
  Overview
  Supported LLM Providers
  Configuration System
    · Provider Configuration
    · Agent-Specific LLM Configuration
    · Complete LLM Configuration
  LLM Client Architecture
    · Provider-Specific Implementations
  Agent-LLM Integration
    · Model Selection Strategy
  Configuration Methods
    · JSON Configuration File
    · Command-Line Arguments
    · Environment Variables
  Advanced Usage
    · Provider-Specific Features
    · Rate Limit Handling
  Azure OpenAI Support
  Conclusion

## · Prompt Engineering System  (L12607)
  源文件: core/agents/base.py, core/agents/code_monkey.py, core/llm/azure_client.py, core/llm/base.py, core/llm/openai_client.py, core/prompts/bug-hunter/iteration.prompt, core/prompts/bug-hunter/log_data.prompt, core/prompts/developer/breakdown.prompt, core/prompts/developer/parse_task.prompt, core/prompts/partials/project_tasks.prompt, core/prompts/problem-solver/get_alternative_solutions.prompt, core/prompts/tech-lead/epic_breakdown.prompt
  Overview
  Prompt Engineering Architecture
  Jinja2 Template System
  Prompt Directory Structure
  Context Injection
  Token Counting and Context Pruning
  Prompt Invocation Flow
  Task Processing Flow
  Human Interaction Prompts
  Related Systems

## · Development Workflow  (L13120)
  源文件: core/agents/architect.py, core/agents/bug_hunter.py, core/agents/developer.py, core/agents/frontend.py, core/agents/mixins.py, core/agents/orchestrator.py, core/agents/spec_writer.py, core/agents/tech_lead.py, core/agents/troubleshooter.py
  Agent Orchestration Flow
    · Orchestrator Agent Selection Flow
  Project Hierarchy and State Structure
    · Hierarchy Structure
    · Epic Structure
    · Task Structure
    · Step Structure
    · Iteration Structure
  Code Generation Workflow
    · Developer Breakdown Process
    · CodeMonkey Implementation Process
    · Frontend Code Generation
  Testing and Iteration Workflow
    · Troubleshooter Test Generation
    · Bug Hunting Workflow
    · Pair Programming Mode
  Context Management and File Filtering
    · Relevant Files Selection
    · File Description and Metadata
  Development Workflow Example
  Summary

## · Project Lifecycle and Stages  (L13790)
  源文件: core/agents/architect.py, core/agents/frontend.py, core/agents/orchestrator.py, core/agents/spec_writer.py, core/cli/helpers.py, core/cli/main.py, core/db/models/project.py, core/db/models/project_state.py, core/db/v0importer.py, core/prompts/developer/parse_task.prompt, core/prompts/partials/project_tasks.prompt, core/prompts/tech-lead/epic_breakdown.prompt
  Purpose and Scope
  Project Hierarchy and State Structure
    · Database Hierarchy
  Lifecycle Overview
  Stage 1: Project Initialization
    · Entry Points
    · Project Creation Sequence
  Stage 2: Specification Phase (Epic 1)
    · SpecWriter Agent
    · State After Specification Phase
  Stage 3: Architecture and Template Phase
    · Architect Agent
    · Template Application
  Stage 4: Frontend Epic
    · Frontend Agent Workflow
    · Frontend Sub-stages
    · Frontend Completion
  Stage 5: Backend Development Planning
    · TechLead Creates Backend Epics
    · Epic Creation
    · Example Epic Structure
  Stage 6: Task Breakdown and Implementation
    · Developer Agent Task Breakdown
    · Task Structure
    · Step Types
  Stage 7: Code Implementation
    · CodeMonkey Agent
    · Parallel Execution
    · State Commit Points
  Stage 8: Quality Assurance and Iteration
    · Troubleshooter → BugHunter Loop
    · Iteration Structure
  Stage 9: Task and Epic Completion
    · Task Completion
    · Epic Completion
  Stage 10: Project Completion and Continuation
    · End-of-Project Decision
    · Feature Addition Flow
  State Transition and Tracking
    · Two-State Transaction Model
    · Resume and Time-Travel
  Action Tracking
  Summary: Complete Lifecycle Flow

## · Code Generation and File Management  (L14899)
  源文件: core/agents/code_monkey.py, core/cli/helpers.py, core/cli/main.py, core/db/models/project.py, core/db/models/project_state.py, core/db/v0importer.py, core/prompts/bug-hunter/iteration.prompt, core/prompts/bug-hunter/log_data.prompt, core/prompts/developer/breakdown.prompt, core/prompts/problem-solver/get_alternative_solutions.prompt, core/prompts/troubleshooter/iteration.prompt, core/state/state_manager.py
  Purpose and Scope
  The `<pythagoracode>` Tag System
    · Overview
    · Tag Structure
    · Parsing Implementation
  CodeMonkey Agent Architecture
    · Agent Workflow
    · Implementation Strategies
    · File Description System
  File Storage Architecture
    · Virtual File System (VFS) Abstraction
    · Database Storage Model
    · Content Deduplication Mechanism
  File Operations
    · save_file Workflow
    · import_files Operation
    · restore_files Operation
    · Modified File Detection
  Version Control and State Management
    · File Cloning in State Transitions
    · Atomic Commits
    · Rollback and State Deletion
  Integration Points
    · CodeMonkey to File Management Flow

## · Context Filtering and Relevance  (L15516)
  源文件: core/agents/base.py, core/agents/bug_hunter.py, core/agents/developer.py, core/agents/mixins.py, core/agents/tech_lead.py, core/agents/troubleshooter.py, core/llm/azure_client.py, core/llm/base.py, core/llm/openai_client.py, core/utils/__init__.py, core/utils/text.py, tests/agents/test_base.py
  Purpose and Scope
  Context Management Architecture
    · Context Management Flow
  File Relevance System
    · RelevantFilesMixin Implementation
    · Key Methods
    · Parallel Processing Flow
    · LLM-Based File Selection
  Log Trimming System
    · trim_logs() Function
  Token Management and Context Windows
    · Token Counting
    · Context Window Limits
    · LLMRequestLog Tracking
  Integration with Agent Workflows
    · Agent Usage Patterns
    · Code References by Agent
    · State Management
  Frontend and Backend Parallel Processing
    · Directory Type Filtering
    · Parallel Execution
    · Benefits of Parallel Processing
    · Full-Stack File Relationships
  Best Practices
  Conclusion

## · User Testing and Feedback Loop  (L15978)
  源文件: core/agents/bug_hunter.py, core/agents/developer.py, core/agents/legacy_handler.py, core/agents/mixins.py, core/agents/tech_lead.py, core/agents/troubleshooter.py, core/db/migrations/versions/f708791b9270_adding_knowledge_base_field_to_.py, core/prompts/troubleshooter/define_user_review_goal.prompt, core/prompts/troubleshooter/get_route_files.prompt
  Overview
  Test Instruction Generation
    · TestSteps Model
    · Automatic Test Generation
    · Test Instruction Rules
    · Run Command Detection
  User Feedback Collection
    · Feedback Classification Flow
    · Iteration Status Types
    · Iteration Data Structure
  Bug Hunting Cycle
    · Bug Reproduction Instructions
    · Hunt Conclusion Decision
    · Bug Hunting Cycles
  Pair Programming Mode
    · Interactive Debugging Session
  Loop Detection
    · Iteration Threshold
    · Alternative Solution Handling
  Developer Iteration Breakdown
    · Processing Iterations
    · Step Type Mapping
  Task Completion
    · Completion Flow
  UI Communication
    · Project Stage Updates
    · Test Instruction Display
    · Bug Hunter Status Indicators
  Integration Points
    · State Management
    · Relevant Files Filtering
    · Task State Preservation
  Best Practices
    · Test Instruction Quality
    · Feedback Loop Efficiency
    · Telemetry Tracking

## · Project Templates  (L16611)
  源文件: core/prompts/frontend/build_frontend.prompt, core/prompts/frontend/system.prompt, core/prompts/partials/project_details.prompt, core/templates/registry.py, core/templates/tree/vite_react/client/src/components/Header.tsx, core/templates/tree/vite_react/client/src/components/ui/theme-provider.tsx, core/templates/tree/vite_react/client/src/components/ui/theme-toggle.tsx, core/templates/vite_react.py, tests/agents/test_tech_lead.py, tests/templates/test_templates.py
  Purpose and Overview
  Template Registry
  Template Application Process
  Template Options
  Template Integration with Prompts
  Vite React Template
    · File Structure
  Creating Custom Templates

## · Template Architecture  (L16826)
  源文件: core/agents/architect.py, core/agents/frontend.py, core/agents/orchestrator.py, core/agents/spec_writer.py, core/prompts/partials/project_details.prompt, core/templates/registry.py, tests/agents/test_tech_lead.py, tests/templates/test_templates.py
  Purpose and Scope
  Template Registry System
    · ProjectTemplateEnum
    · PROJECT_TEMPLATES Dictionary
  Template Lifecycle
    · Selection Phase (Architect Agent)
    · Configuration Phase
    · Application Phase (SpecWriter Agent)
  Base Template Architecture
    · BaseProjectTemplate Interface
    · Template Storage in StateManager
  Integration with Agent System
    · Template Usage Across Agents
    · Template Summary in Context
  Template Options System
    · Options Model Pattern
    · Options Access Pattern
  Asynchronous Template Application
    · Background Template Processing
  Template File Management
    · Relevant Files Tracking
    · Template Summary Persistence

## · Vite React Templates  (L17277)
  源文件: core/agents/wizard.py, core/prompts/frontend/build_frontend.prompt, core/prompts/frontend/system.prompt, core/templates/info/vite_react/summary.tpl, core/templates/tree/vite_react/client/src/api/api.ts, core/templates/tree/vite_react/client/src/api/auth.ts, core/templates/tree/vite_react/client/src/components/Header.tsx, core/templates/tree/vite_react/client/src/components/ui/theme-provider.tsx, core/templates/tree/vite_react/client/src/components/ui/theme-toggle.tsx, core/templates/tree/vite_react/client/src/pages/Login.tsx, core/templates/tree/vite_react/client/src/pages/Register.tsx, core/templates/tree/vite_react_swagger/client/.env
  1. Template Overview
    · Template Comparison
    · High-Level Architecture Comparison
  2. Common Frontend Architecture
    · 2.1 Frontend Directory Structure
    · 2.2 UI Component Library
  3. Vite React Template (Full-Stack)
    · 3.1 Project Structure
    · 3.2 Communication Flow
    · 3.3 Backend Configuration
    · 3.4 API Layer Structure
  4. Vite React Swagger Template (External API)
    · 4.1 Template Initialization
    · 4.2 Authentication Options
    · 4.3 Dual API Architecture
    · 4.4 API Configuration Code Structure
    · 4.5 Environment Variables
  5. Authentication System
    · 5.1 Login and Register Pages
    · 5.2 Authentication Context
    · 5.3 Token Management and Refresh Flow
    · 5.4 Protected Routes
  6. Development Workflow
    · 6.1 Running the Application
    · 6.2 API Mocking System
  7. Template Customization
  8. Installation Hook

## · Deployment and Operations  (L17784)
  源文件: .github/workflows/ci.yml, Dockerfile, cloud/posthog.html, core/llm/relace_client.py
  8.1 Docker Environment
    · Dockerfile Structure and Build Process
    · Multi-Architecture Support
    · code-server Configuration
    · User and Permissions
    · Environment Variables
    · Port Exposure
    · Git Configuration
  8.2 Cloud Deployment
    · Entrypoint Script
    · Automatic Extension Installation
    · PostHog Analytics Integration
    · Cloud-Specific Configuration
  8.3 Continuous Integration
    · CI Workflow Configuration
    · Build Matrix
    · Build Steps
    · Timeout Configuration
    · Multi-Platform Support
  4. VS Code Integration
    · 4.1 Automatic Extension Installation
    · 4.2 Workspace Configuration

## · Docker Environment  (L18230)
  源文件: Dockerfile, cloud/config-docker.json, cloud/entrypoint.sh, cloud/favicon.ico, cloud/favicon.svg, cloud/on-event-extension-install.sh, cloud/posthog.html, cloud/setup-dependencies.sh, core/llm/relace_client.py
  Overview
  Container Configuration
    · Base Image and System Dependencies
    · Key Configuration Details
    · Environment Variables and Working Directory
  Container Runtime Behavior
    · SSH Configuration
    · MongoDB Setup
  VS Code Integration
    · Automatic Extension Installation
  Multi-Architecture Support
  Database Integration
  Usage and Configuration

## · Cloud Deployment  (L18468)
  源文件: Dockerfile, cloud/config-docker.json, cloud/entrypoint.sh, cloud/favicon.ico, cloud/favicon.svg, cloud/on-event-extension-install.sh, cloud/posthog.html, cloud/setup-dependencies.sh, core/llm/relace_client.py
  Purpose and Scope
  Cloud Deployment Architecture
  Container Entrypoint Configuration
    · Entrypoint Script Flow
    · Directory Structure
    · Key Environment Variables
  Code-Server Browser IDE Integration
    · Code-Server Configuration
    · Extension Installation Process
    · Workspace Settings
    · Custom Branding
  Cloud Configuration Profile
    · LLM Provider Configuration
    · Agent Model Assignments
    · Database Configuration
    · File System Configuration
  PostHog Analytics Integration
    · Analytics Injection Process
    · Content Security Policy Modification
    · Analytics Script Injection
    · PostHog Configuration
  Cloud API Authentication
    · Relace Client Authentication
    · Authentication Priority
    · API Request Flow
    · Fallback Behavior
  Multi-Architecture Support
    · Architecture Detection
    · Platform-Specific Dependency Installation
    · Architecture-Specific Components
    · Certificate Management Workaround
  Port Exposure and Service Access
    · Primary Access Point
    · User and Permissions

## · Continuous Integration  (L19043)
  源文件: .github/workflows/ci.yml, CHANGELOG.md, README.md, pyproject.toml, requirements.txt
  Purpose and Scope
  GitHub Actions Workflow
    · Workflow Configuration
    · Workflow Steps
  Dependency Management with Poetry
    · Dependency Installation
  Testing Strategy
    · Pytest Configuration
    · Coverage Configuration
    · Test Execution Flow
  Code Quality with Ruff
    · Ruff Configuration
    · Linting Pipeline
  Multi-Platform Support
    · Platform Matrix
  Pre-commit Hooks
    · Local Development Workflow
  CI Workflow Execution Summary
    · Complete Pipeline Flow
    · Timeout and Failure Handling
  Integration with Development Workflow
    · CI Touchpoints