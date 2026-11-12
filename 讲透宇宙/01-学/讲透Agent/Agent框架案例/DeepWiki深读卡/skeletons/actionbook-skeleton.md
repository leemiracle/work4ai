# Skeleton: actionbook（40 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 18KB | 4 | ~12 | 8 |
| 2 | Getting Started | L424 | 15KB | 4 | ~7 | 5 |
| 3 | Architecture Overview | L1000 | 23KB | 9 | ~2 | 15 |
| 4 | User Interfaces | L1642 | 15KB | 7 | ~9 | 5 |
| 5 | CLI (Command Line Interface) | L2146 | 18KB | 7 | ~17 | 14 |
| 6 | Browser Automation Commands | L2725 | 13KB | 4 | ~7 | 11 |
| 7 | MCP Server | L3078 | 14KB | 2 | ~12 | 9 |
| 8 | JavaScript SDK | L3562 | 25KB | 5 | ~16 | 5 |
| 9 | Skills and Plugins | L4460 | 12KB | 5 | ~13 | 4 |
| 10 | Core Services | L4877 | 16KB | 4 | ~10 | 8 |
| 11 | API Service | L5284 | 21KB | 4 | ~20 | 3 |
| 12 | Action Builder Service | L5985 | 27KB | 8 | ~20 | 12 |
| 13 | Task Execution Pipeline | L6766 | 30KB | 7 | ~16 | 8 |
| 14 | Action Recording | L7574 | 24KB | 8 | ~12 | 12 |
| 15 | Recording Tools Reference | L8234 | 32KB | 4 | ~26 | 12 |
| 16 | Batch Crawling and Import | L9230 | 20KB | 6 | ~15 | 12 |
| 17 | Playbook Builder Service | L9829 | 28KB | 7 | ~7 | 10 |
| 18 | Playbook Task Controller | L10655 | 17KB | 8 | ~12 | 9 |
| 19 | Browser Automation Layer | L11128 | 34KB | 5 | ~12 | 16 |
| 20 | BrowserAdapter Interface | L12050 | 23KB | 4 | ~18 | 9 |
| 21 | StagehandBrowser Implementation | L12711 | 24KB | 11 | ~18 | 9 |
| 22 | AgentCoreBrowser Implementation | L13408 | 24KB | 12 | ~14 | 9 |
| 23 | Browser Profiles | L14230 | 15KB | 5 | ~8 | 7 |
| 24 | Data Layer | L14681 | 16KB | 9 | ~12 | 3 |
| 25 | Database Schema | L15219 | 21KB | 5 | ~44 | 7 |
| 26 | Database Connection Management | L15828 | 12KB | 8 | ~6 | 1 |
| 27 | Search and Indexing | L16164 | 13KB | 2 | ~6 | 2 |
| 28 | AI and LLM Integration | L16571 | 19KB | 6 | ~21 | 16 |
| 29 | AIClient | L17065 | 17KB | 7 | ~2 | 16 |
| 30 | Selector Optimizer | L17572 | 16KB | 4 | ~11 | 12 |
| 31 | Capability Discovery | L17974 | 21KB | 10 | ~8 | 14 |
| 32 | Data Models and Types | L18564 | 26KB | 9 | ~51 | 11 |
| 33 | Capability Types | L19390 | 16KB | 4 | ~37 | 7 |
| 34 | Selector Types | L19800 | 21KB | 8 | ~13 | 12 |
| 35 | Tool Definitions | L20316 | 18KB | 7 | ~5 | 4 |
| 36 | Development Guide | L20936 | 11KB | 3 | ~6 | 16 |
| 37 | Monorepo Structure | L21278 | 14KB | 2 | ~2 | 11 |
| 38 | Build System | L21653 | 14KB | 4 | ~6 | 7 |
| 39 | Local Development Setup | L22124 | 16KB | 5 | ~5 | 2 |
| 40 | Testing | L22843 | 18KB | 4 | ~6 | 12 |


## · Overview  (L6)
  源文件: .prettierignore, .prettierrc.json, CLAUDE.md, README.md, services/action-builder/scripts/login.ts, services/action-builder/src/optimizer/SelectorOptimizer.ts, services/common/browser-profile/package.json, services/common/browser-profile/src/BrowserProfileManager.ts
  Purpose and Scope
  What is Actionbook
  Core Value Proposition
  System Architecture
    · High-Level Component Architecture
  Domain Model Hierarchy
  Integration Methods
    · Integration Method Comparison
    · User Interaction Flow
  Key Components Overview
    · User-Facing Packages
    · Core Services
    · Browser Automation
    · Data Layer
  Build Pipeline Overview
  Technology Stack
    · Core Technologies
    · Browser Automation
    · AI/LLM Integration
    · API and Protocols
    · Database Features
  Monorepo Structure

## · Getting Started  (L424)
  源文件: LICENSE, README.md, packages/cli/package.json, packages/js-sdk/package.json, packages/mcp/package.json
  Prerequisites
  Installation Method Selection
  Option 1: CLI Installation
    · Installation Steps
    · Core CLI Commands
    · First Commands to Try
  Option 2: MCP Server Installation
    · Supported IDEs
    · Standard Configuration Format
    · MCP Tool Flow
  Option 3: JavaScript SDK Installation
    · Installation
    · Basic Usage Pattern
    · SDK Method Structure
  Verification Steps
    · CLI Verification
    · MCP Verification
    · SDK Verification
  Common First Tasks
    · Task 1: Find and Use a Specific Element Selector
    · Task 2: Explore Available Websites
    · Task 3: Integrate with AI Agent Frameworks
  Browser Automation Commands
    · Available Commands
  Next Steps
    · Community Resources
  Troubleshooting Common Issues
    · Issue: `actionbook: command not found` after global install
    · Issue: Browser install fails
    · Issue: MCP server not appearing in IDE
    · Issue: SDK import errors

## · Architecture Overview  (L1000)
  源文件: .gitignore, .prettierignore, .prettierrc.json, CLAUDE.md, README.md, mcp-servers.json, package.json, pnpm-lock.yaml, pnpm-workspace.yaml, services/action-builder/.nvmrc, services/action-builder/scripts/login.ts, services/action-builder/src/optimizer/SelectorOptimizer.ts
  Purpose and Scope
  System Overview
  Monorepo Structure
    · Published Packages
    · Internal Packages
    · Services
  Component Architecture
  Data Flow Architecture
    · Query Flow (User → API → Database)
    · Build Flow (Service → Browser → Database)
  Browser Automation Layer
  Task Orchestration Pipeline
  AI and LLM Integration
  Data Layer
  Browser Profile Management
  Build System
  Key Design Patterns
    · Strategy Pattern: Browser Abstraction
    · Producer-Consumer: Task Queue
    · Singleton: Database Connection
    · Template Method: Recording Pipeline
    · Facade: SDK Abstraction

## · User Interfaces  (L1642)
  源文件: LICENSE, README.md, packages/cli/package.json, packages/js-sdk/package.json, packages/mcp/package.json
  Purpose and Scope
  Overview
  Interface Architecture
  CLI (Command Line Interface)
    · Command Structure
    · Dependencies
  MCP Server
    · Tool Definitions
    · IDE Integration Configuration
    · MCP Protocol Integration
  JavaScript SDK
    · SDK Core API
    · Tool Definition Structure
    · SDK Dependencies
    · Framework Integration Patterns
  Interface Communication Flow
  Installation Methods
    · CLI Installation
    · MCP Server Installation
    · SDK Installation
  Common Type Definitions
  Environment Configuration
    · CLI Environment Variables
    · MCP Server Environment Variables
    · SDK Configuration
  Selecting the Right Interface

## · CLI (Command Line Interface)  (L2146)
  源文件: LICENSE, packages/cli/README.md, packages/cli/package.json, packages/cli/src/commands/browser.ts, packages/cli/src/commands/get.ts, packages/cli/src/commands/search.ts, packages/cli/src/commands/sources.ts, packages/cli/src/index.ts, packages/cli/src/output.ts, packages/cli/src/utils/process.ts, packages/cli/tsconfig.build.json, packages/cli/tsconfig.json
  Purpose and Scope
  Package Architecture
    · Key Components
  Installation and Setup
    · Installation Methods
    · Authentication
  Command Architecture
    · Command Registration Flow
  Search Command
    · Command Definition
    · Options
    · Implementation Details
  Get Command
    · Command Definition
    · Action ID Format
    · Formatted Output Structure
  Sources Command
    · Base Command
    · Search Subcommand
    · Source List Formatting
  Browser Command
    · Architecture
    · Command Configuration
    · Agent Browser Execution
    · Installation Command
    · Error Handling
  Output Format System
    · Output Mode Selection
    · Formatted Output Implementation
  Error Handling System
    · Error Handler Function
    · SDK Error Format
    · Exit Code Handling
  Dependencies
    · Direct Dependencies
    · Build and Development Dependencies
    · TypeScript Configuration
  Build and Publishing
    · Build Scripts
    · Package Distribution

## · Browser Automation Commands  (L2725)
  源文件: README.md, packages/cli/README.md, packages/cli/src/commands/browser.ts, packages/cli/src/commands/get.ts, packages/cli/src/commands/search.ts, packages/cli/src/commands/sources.ts, packages/cli/src/index.ts, packages/cli/src/output.ts, packages/cli/src/utils/process.ts, packages/cli/tsconfig.build.json, packages/cli/tsconfig.json
  Purpose and Scope
  Command Architecture
    · Command Registration
  Installation Process
    · Installation Flow
    · Playwright CLI Resolution
    · Installation Command Arguments
  Command Execution and Forwarding
    · Execution Flow
    · Output Transformation
    · Working Directory Context
  Available Commands
    · Selector Reference Syntax
  Error Handling
    · Command Not Found (ENOENT)
    · Signal Handling
    · Installation Failure Messages
  Integration with Actionbook Workflow

## · MCP Server  (L3078)
  源文件: .claude-plugin/marketplace.json, .claude-plugin/plugin.json, LICENSE, README.md, commands/manual.md, packages/cli/package.json, packages/js-sdk/package.json, packages/mcp/package.json, skills/actionbook/SKILL.md
  Overview
  Architecture
    · Component Responsibilities
  Installation and Configuration
    · NPM Package
    · IDE Integration
    · Environment Variables
  Available Tools
    · Tool Execution Flow
    · `search_actions`
    · `get_action_by_id`
  Usage Patterns
    · Basic Workflow in AI IDEs
    · Integration with Browser Automation
    · Skill System Integration
  Command Line Interface
  Marketplace Distribution
  Implementation Details
    · Dependencies
    · Build Process

## · JavaScript SDK  (L3562)
  源文件: README.md, packages/js-sdk/src/api-client.ts, packages/js-sdk/src/client.ts, packages/js-sdk/src/tool-defs.ts, packages/js-sdk/src/types.ts
  Purpose and Scope
  Installation
  Client Architecture
  Client Initialization
  API Methods
    · searchActions()
    · getActionById()
    · listSources()
    · searchSources()
  Tool Definition System
  LLM Framework Integration
    · Vercel AI SDK
    · OpenAI SDK
    · Anthropic Claude SDK
    · Google Gemini SDK
  Type System
    · Core Types
    · ChunkSearchResult Structure
    · ChunkActionDetail Structure
    · ParsedElements Structure
  Error Handling
    · Error Types
    · Retry Logic
  Custom Fetch Implementation
  Complete Integration Example

## · Skills and Plugins  (L4460)
  源文件: .claude-plugin/marketplace.json, .claude-plugin/plugin.json, commands/manual.md, skills/actionbook/SKILL.md
  Plugin Architecture
    · Plugin Manifest Structure
    · Plugin Component Diagram
  Skills
    · Skill Definition Format
    · Actionbook Core Skill
    · Skill Usage Patterns
    · Skill Guidelines
  Commands
    · Command Definition Format
  Usage
  Examples
    · Command Execution Flow
  Plugin Marketplace
    · Marketplace Structure
    · Available Plugins
    · Plugin Distribution Diagram
  Integration Points
    · Skills ↔ Commands ↔ MCP Tools
  Implementation References
    · File Paths for Plugin System
    · Related Documentation

## · Core Services  (L4877)
  源文件: .gitignore, README.md, mcp-servers.json, package.json, pnpm-lock.yaml, pnpm-workspace.yaml, services/action-builder/.nvmrc, turbo.json
  Purpose and Scope
  Service Architecture
  Service Responsibilities
  API Service
  Action Builder Service
    · Architecture Components
    · Key Classes and Files
  Playbook Builder Service
    · Core Functionality
    · Key Classes
  Knowledge Builder Service
    · Core Functionality
    · Database Integration
  Service Communication Flow
    · Stage Progression
  Shared Infrastructure
    · Database Package (`services/db`)
    · Browser Package (`services/common/browser`)
    · Browser Profile Package (`services/common/browser-profile`)
  Deployment Architecture
  Environment Configuration
  Build and Development

## · API Service  (L5284)
  源文件: README.md, services/db/migrations/0019_add_vector_indexes.sql, services/db/migrations/0020_add_chunks_fulltext_index.sql
  Purpose and Scope
  Architecture Overview
  Endpoints
    · Endpoint Summary
  Search Actions Endpoint
    · Endpoint: `GET /actions/search`
  Get Action by ID Endpoint
    · Endpoint: `GET /actions/:id`
  Sources Endpoints
    · Endpoint: `GET /sources`
  Hybrid Search Implementation
  Full-Text Search Implementation
    · Database Index Structure
    · Performance Characteristics
    · Full-Text Query Processing
    · Supporting Indexes
  Vector Search Implementation
    · Vector Index Structure
    · HNSW Index Parameters
    · Vector Search Query Flow
    · Performance Trade-offs
    · Supporting Indexes for Vector Search
  Hybrid Search Query Processing
    · Search Flow Diagram
    · Result Combination Algorithm
    · Query Optimization Strategies
  Authentication and Access Control
    · Current State (Open Beta)
    · Usage in Client Libraries
  Database Queries and Performance
    · Index Strategy Summary
    · Query Pattern Examples
  Integration with Client Libraries
    · Client Integration Matrix
    · API Client Architecture
    · Tool Definition Schema
  Error Handling and Status Codes
    · HTTP Status Codes
    · Error Response Format

## · Action Builder Service  (L5985)
  源文件: services/action-builder/.env.example, services/action-builder/.gitignore, services/action-builder/README.md, services/action-builder/package.json, services/action-builder/scripts/coordinator.ts, services/action-builder/scripts/crawl-playbook-batch.ts, services/action-builder/scripts/crawl-sites.txt.example, services/action-builder/scripts/import-playbook-batch.ts, services/action-builder/src/llm/AIClient.ts, services/action-builder/src/utils/logger.ts, services/action-builder/vitest.setup.ts, services/db/migrations/meta/0018_snapshot.json
  Architecture Overview
    · Three-Layer Architecture
    · Layer Responsibilities
    · Key Design Patterns
  Build Pipeline Flow
    · Stage Details
  Task Types
    · Build Tasks vs Recording Tasks
    · Chunk Type Detection
    · Task Lifecycle State Machine
  Configuration
    · Environment Variables Reference
    · Concurrency Model
    · Logging Modes
  Data Storage
    · Database Schema
    · Key Indexes
  Output Format
    · YAML File Structure
    · Element Properties
  Usage Modes
    · Mode 1: Automated Coordinator (Production)
    · Mode 2: Manual Task CLI (Development)
    · Batch Operations
  Integration Points
    · Component Dependencies
  Error Handling and Recovery
    · Failure Recovery Matrix
    · Partial Success Policy
    · Logging and Observability

## · Task Execution Pipeline  (L6766)
  源文件: services/action-builder/.env.example, services/action-builder/README.md, services/action-builder/scripts/coordinator.ts, services/action-builder/src/task-worker/build-task-runner.ts, services/action-builder/src/task-worker/coordinator.ts, services/action-builder/src/task-worker/recording-task-queue-worker.ts, services/action-builder/test/coordinator.integration.it.test.ts, services/action-builder/test/task-worker/integration/end-to-end.it.test.ts
  Purpose and Scope
  Architecture Overview
    · Three-Layer Architecture
  Task Lifecycle
    · Build Task State Transitions
    · Recording Task State Transitions
  Components
    · Coordinator
    · BuildTaskRunner
    · RecordingTaskQueueWorker
    · TaskExecutor
  Concurrency Control
    · Build Task Concurrency
    · Recording Task Concurrency
    · Atomic Task Claiming
  Heartbeat and Monitoring
    · Heartbeat Mechanism
    · Metrics Output
  Failure Handling
    · Retry Logic
    · Stale Detection and Recovery
  Configuration
    · Environment Variables
    · Starting the Coordinator
  Summary

## · Action Recording  (L7574)
  源文件: services/action-builder/scripts/playbook-record.ts, services/action-builder/src/ActionBuilder.ts, services/action-builder/src/llm/prompts/capability-recorder.ts, services/action-builder/src/recorder/ActionRecorder.ts, services/action-builder/src/recorder/RecorderToolExecutor.ts, services/action-builder/src/task-worker/task-executor.ts, services/action-builder/src/types/config.ts, services/action-builder/src/validator/SelectorValidator.ts, services/action-builder/test/ActionBuilder.ut.test.ts, services/action-builder/test/browser/xpath-optimizer.ut.test.ts, services/action-builder/test/task-worker/task-executor.ut.test.ts, services/action-builder/test/validator/SelectorValidator.ut.test.ts
  Purpose and Scope
  Architecture Overview
    · Core Classes
  Recording Flow
    · Recording Loop Details
  Tool Execution Flow
    · Tool Execution with Retry
    · Pre-Action Hooks
  Element Discovery
    · Observe Result Format
  Multi-Selector Extraction
    · Selector Types and Confidence Scores
    · Template Pattern Detection
  Recording Modes
    · Exploratory Mode
    · Task-Driven Mode
  Termination Strategy
    · Termination Configuration
    · Early Termination with Partial Results
  Selector Optimization
    · Optimization Benefits
  Token and Statistics Tracking
    · Statistics Output
    · Real-Time Step Events
  Integration Points

## · Recording Tools Reference  (L8234)
  源文件: services/action-builder/scripts/playbook-record.ts, services/action-builder/src/recorder/RecorderToolExecutor.ts, services/action-builder/src/recorder/RecorderTools.ts, services/action-builder/src/types/capability.ts, services/action-builder/src/utils/index.ts, services/action-builder/src/utils/url-matcher.ts, services/action-builder/src/validator/SelectorValidator.ts, services/action-builder/test/browser/xpath-optimizer.ut.test.ts, services/action-builder/test/recorder/RecorderTools.ut.test.ts, services/action-builder/test/types/capability.ut.test.ts, services/action-builder/test/utils/url-matcher.ut.test.ts, services/action-builder/test/validator/SelectorValidator.ut.test.ts
  Overview
  Tool Execution Architecture
  Tool Reference
    · navigate
    · observe_page
    · set_page_context
    · register_element
    · interact
    · wait
    · scroll
    · scroll_to_bottom
    · go_back
  Tool Execution Flow
  Selector Extraction Strategy
  Tool Definition Schema
  Common Usage Patterns
    · Pattern 1: Exploratory Recording (observe + register)
    · Pattern 2: Task-Driven Recording (interact)
    · Pattern 3: Lazy-Loaded Content
    · Pattern 4: Modal/Overlay Exploration
    · Pattern 5: Navigation Control
  Error Handling
  Implementation Notes
    · URL Normalization
    · ID Selector Escaping
    · Phantom Element Detection

## · Batch Crawling and Import  (L9230)
  源文件: services/action-builder/.env.example, services/action-builder/.gitignore, services/action-builder/README.md, services/action-builder/package.json, services/action-builder/scripts/coordinator.ts, services/action-builder/scripts/crawl-playbook-batch.ts, services/action-builder/scripts/crawl-sites.txt.example, services/action-builder/scripts/import-playbook-batch.ts, services/action-builder/src/llm/AIClient.ts, services/action-builder/src/utils/logger.ts, services/action-builder/vitest.setup.ts, services/db/migrations/meta/0018_snapshot.json
  Overview
  Batch Crawling Workflow
    · Configuration
    · Execution Flow
    · Command-Line Usage
    · Output Formats
  Batch Import Workflow
    · Execution Flow
    · Command-Line Usage
    · Auto-Detection Logic
    · Retry Failed Imports
    · Output Format
  Script Architecture
    · Key Functions
  Integration with Database
    · Data Flow Diagram
  Error Handling
    · Crawl Failures
    · Import Failures
  Comparison with Coordinator Pipeline

## · Playbook Builder Service  (L9829)
  源文件: README.md, services/action-builder/src/task-worker/utils/prompt-builder.ts, services/db/src/models/build-task.ts, services/playbook-builder/scripts/worker.ts, services/playbook-builder/src/analyzer/page-analyzer.ts, services/playbook-builder/src/controller/playbook-task-controller.ts, services/playbook-builder/src/discoverer/capabilities-discoverer.ts, services/playbook-builder/src/discoverer/page-discoverer.ts, services/playbook-builder/src/playbook-builder.ts, services/playbook-builder/src/types/index.ts
  Purpose and Scope
  Service Overview
  Architecture
    · Component Diagram
  Main Components
    · PlaybookBuilder
    · Page Discovery Process
    · PageDiscoverer
    · CapabilitiesDiscoverer
    · 0. Page URL
    · 1. Page Overview
    · 2. Page Function Summary
    · 3. Page Structure Summary
    · 4. DOM Structure Instance
    · 5. Parsing & Processing Summary
    · 6. Operation Summary
  PlaybookTaskController
    · Task Controller State Machine
    · Polling and Claiming
    · Task Execution Flow
    · Error Handling and Retry
  Build Pipeline Integration
    · Build Task Stage Progression
    · BuildTaskConfig for Playbook Builder
  Storage and Data Flow
    · Storage Operations
    · Embedding Generation
  Worker Process
    · CLI Entry Point
    · Controller Options
  Configuration
    · Environment Variables
    · Build Task Configuration
  Comparison with Action Builder
    · Architectural Differences
    · Prompt Differences
  Data Flow Summary

## · Playbook Task Controller  (L10655)
  源文件: services/action-builder/src/task-worker/utils/prompt-builder.ts, services/db/src/models/build-task.ts, services/playbook-builder/scripts/worker.ts, services/playbook-builder/src/analyzer/page-analyzer.ts, services/playbook-builder/src/controller/playbook-task-controller.ts, services/playbook-builder/src/discoverer/capabilities-discoverer.ts, services/playbook-builder/src/discoverer/page-discoverer.ts, services/playbook-builder/src/playbook-builder.ts, services/playbook-builder/src/types/index.ts
  Purpose and Scope
  Architecture Overview
    · System Context Diagram
  Controller States
    · State Machine
  Task Lifecycle
    · Task Lifecycle Flow
    · Build Task Stages
  Optimistic Locking
    · Claim Task Implementation
  Controller Configuration
    · Configuration Options
    · Playbook Builder Configuration
  Source Management
    · Source Resolution Algorithm
  Error Handling and Retry Logic
    · Retry Decision Flow
    · Error State Persistence
  Heartbeat Mechanism
    · Heartbeat Implementation
  Worker Entry Point
    · Worker Process Lifecycle
    · Worker Initialization Code
  Database Operations
    · Database Operation Summary
    · Task Status Query
  Integration with PlaybookBuilder
    · Execution Flow
  API Reference
    · PlaybookTaskController Interface
    · Factory Function

## · Browser Automation Layer  (L11128)
  源文件: .prettierignore, .prettierrc.json, CLAUDE.md, services/action-builder/scripts/login.ts, services/action-builder/src/index.ts, services/action-builder/src/optimizer/SelectorOptimizer.ts, services/common/browser-profile/package.json, services/common/browser-profile/src/BrowserProfileManager.ts, services/common/browser/package.json, services/common/browser/src/adapters/browser-adapter.ts, services/common/browser/src/adapters/index.ts, services/common/browser/src/implementations/agent-core-browser.ts
  Purpose and Scope
  Architecture Overview
  BrowserAdapter Interface
    · Lifecycle Methods
    · Navigation and Page Information
    · AI Capabilities
    · Element Inspection
    · Automation Helpers
  StagehandBrowser Implementation
    · Class Structure
    · LLM Provider Configuration
    · Browser Launch Options
    · Token Metrics Tracking
    · Error Handling and Retry Logic
  AgentCoreBrowser Implementation
    · Class Structure
    · Initialization
    · Bedrock Vision Integration
    · Response Parsing
    · SDK Method Signatures
    · XPath Normalization and Escaping
  Browser Profile Management
    · Purpose and Benefits
    · Class API
    · Lock File Cleanup
    · Usage with StagehandBrowser
    · Login Script
  Configuration and Initialization
    · Configuration Objects
    · Initialization Patterns
    · Environment Variable Precedence
  Common Patterns and Usage
    · Basic Navigation and Observation
    · Direct Action Execution
    · Error Handling
    · Token Usage Tracking
    · Popup Handling
    · Implementation Comparison Table
  Testing Strategy
    · Unit Tests
    · E2E Tests

## · BrowserAdapter Interface  (L12050)
  源文件: services/action-builder/src/index.ts, services/common/browser/package.json, services/common/browser/src/adapters/browser-adapter.ts, services/common/browser/src/adapters/index.ts, services/common/browser/src/implementations/agent-core-browser.ts, services/common/browser/src/implementations/stagehand-browser.ts, services/common/browser/src/types/browser.ts, services/common/browser/test/e2e/stagehand-browser.e2e.test.ts, services/common/browser/test/unit/agent-core-browser.ut.test.ts
  Purpose and Scope
  Interface Structure
  Lifecycle Methods
    · Usage Pattern
  Navigation Methods
    · NavigateOptions Type
    · Behavior
    · Implementation Details
  Screenshot Capabilities
    · ScreenshotOptions Type
    · Return Value
    · Format Support
  Waiting Operations
    · WaitForSelectorOptions Type
    · State Mapping
  Scrolling Operations
    · scroll() Parameters
    · scrollToBottom() Behavior
  AI Capabilities
    · AI Capabilities Overview
    · observe() Method
    · act() Method
    · actWithSelector() Method
  Element Inspection
    · getElementAttributesFromXPath()
    · getPage()
  Automation Helpers
    · autoClosePopups()
  Metrics
    · getTokenStats()
  Implementations Overview
    · Implementation Comparison
  Usage in Action Builder
  Error Handling
    · Common Error Types

## · StagehandBrowser Implementation  (L12711)
  源文件: services/action-builder/src/index.ts, services/common/browser/package.json, services/common/browser/src/adapters/browser-adapter.ts, services/common/browser/src/adapters/index.ts, services/common/browser/src/implementations/agent-core-browser.ts, services/common/browser/src/implementations/stagehand-browser.ts, services/common/browser/src/types/browser.ts, services/common/browser/test/e2e/stagehand-browser.e2e.test.ts, services/common/browser/test/unit/agent-core-browser.ut.test.ts
  Purpose and Scope
  Architecture Overview
    · Class Structure
    · Key Dependencies
  LLM Provider Configuration
    · Provider Selection Flow
    · Provider Configuration Details
    · Bedrock Proxy Configuration
  Initialization and Lifecycle
    · Initialization Process
    · Browser Launch Options
    · Storage State Injection
    · Cleanup
  AI Capabilities
    · observe() - Element Discovery
    · act() - Action Execution
    · Custom Error Types
    · Token Tracking
  Element Inspection
    · getElementAttributesFromXPath()
    · Iframe Handling
    · Selector Generation
    · Attribute Extraction Script
  Navigation and Page Control
    · navigate()
    · Scrolling Operations
  Automation Helpers
    · autoClosePopups()
  Metrics and Performance Logging
    · Token Statistics
    · Performance Logging
  Error Handling and Retry Logic
    · Rate Limit Detection
    · Exponential Backoff
    · Error Context
  Usage Examples
    · Basic Initialization
    · Element Discovery and Action
    · Token Tracking
  Configuration Reference
    · BrowserConfig
    · Environment Variables
  Testing
    · Unit Tests
    · E2E Tests

## · AgentCoreBrowser Implementation  (L13408)
  源文件: services/action-builder/src/index.ts, services/common/browser/package.json, services/common/browser/src/adapters/browser-adapter.ts, services/common/browser/src/adapters/index.ts, services/common/browser/src/implementations/agent-core-browser.ts, services/common/browser/src/implementations/stagehand-browser.ts, services/common/browser/src/types/browser.ts, services/common/browser/test/e2e/stagehand-browser.e2e.test.ts, services/common/browser/test/unit/agent-core-browser.ut.test.ts
  Purpose and Scope
  Architecture Overview
  Initialization and Lifecycle
    · Constructor and Configuration
    · Initialization Flow
    · Session Lifecycle
  Core Components
    · PlaywrightBrowser Client
    · BedrockRuntimeClient for AI
  AI Capabilities Implementation
    · observe() Method
    · Response Parsing
    · act() and actWithSelector()
  Method Implementations
    · Navigation Methods
    · Page Information Methods
    · Screenshot Method
    · Waiting Methods
    · Scrolling Methods
  Element Inspection
    · getElementAttributesFromXPath()
    · XPath and Selector Utilities
  Configuration and Environment
    · Environment Variable Resolution
    · AWS Credentials
  Comparison with StagehandBrowser
    · Key Differences
    · When to Use AgentCoreBrowser
  Error Handling and Edge Cases
    · Common Error Patterns
    · Response Parsing Robustness
  Testing
    · Unit Test Coverage
    · E2E Test Considerations
  Integration with Action Builder
  Package Structure and Dependencies
    · Package Configuration
    · Import Pattern

## · Browser Profiles  (L14230)
  源文件: .prettierignore, .prettierrc.json, CLAUDE.md, services/action-builder/scripts/login.ts, services/action-builder/src/optimizer/SelectorOptimizer.ts, services/common/browser-profile/package.json, services/common/browser-profile/src/BrowserProfileManager.ts
  Purpose and Scope
  Overview
  Architecture
  BrowserProfileManager Class
    · Constructor and Configuration
    · Core Methods
  Profile Storage Structure
    · Lock File Cleanup
  Anti-Detection Configuration
    · Constants
    · Launch Options
  Login Workflow
    · Command Line Arguments
    · Script Implementation Details
  Integration with Browser Adapters
    · StagehandBrowser Integration
    · Profile Usage Pattern
  Environment Variables and Proxy Support
  Package Structure
  Best Practices
    · When to Use Profiles
    · Profile Lifecycle Management
    · Anti-Detection Considerations

## · Data Layer  (L14681)
  源文件: services/db/migrations/0019_add_vector_indexes.sql, services/db/migrations/0020_add_chunks_fulltext_index.sql, services/db/src/connection.ts
  Purpose and Scope
  Storage Architecture
  Database Connection Management
    · Connection Strategy
    · Driver Selection Logic
    · Connection Pool Configuration
    · Singleton Pattern
  Schema Organization
    · Key Tables Overview
  Version Management
  Dual Persistence Strategy
    · YAML File Structure
    · Benefits of Dual Persistence
  Search Infrastructure
    · Index Types
    · Index Configuration
    · Hybrid Search Implementation
  Data Flow Summary

## · Database Schema  (L15219)
  源文件: services/action-builder/src/task-worker/build-task-runner.ts, services/action-builder/src/task-worker/coordinator.ts, services/action-builder/src/task-worker/recording-task-queue-worker.ts, services/action-builder/test/coordinator.integration.it.test.ts, services/action-builder/test/task-worker/integration/end-to-end.it.test.ts, services/db/migrations/0019_add_vector_indexes.sql, services/db/migrations/0020_add_chunks_fulltext_index.sql
  Purpose and Scope
  Schema Overview
  Core Tables
    · Source Management Tables
    · Content Storage Tables
    · UI Discovery Tables
    · Build Pipeline Tables
  Entity Relationship Diagram
  Task Lifecycle and Status Transitions
  Recording Task Configuration
  Blue-Green Version Management
  Concurrency and Safety Mechanisms
    · Atomic Task Claiming
    · Heartbeat Monitoring
    · Idempotent Task Generation
  Composite Indexes for Query Performance
    · Full-Text Search Indexes
    · Vector Similarity Indexes
    · Relationship Indexes
  Integration Test Coverage

## · Database Connection Management  (L15828)
  源文件: services/db/src/connection.ts
  Purpose and Scope
  Driver Selection Strategy
    · Environment Detection Logic
  Database Type Unification
  Connection Creation
    · Node-Postgres Connection (`createPgDb`)
    · Neon Serverless Connection (`createNeonDb`)
  Connection Pooling Strategies
    · Pooling Parameters
    · Serverless Optimization
    · SSL Configuration
    · Error Handling
  Singleton Pattern
    · Usage Pattern
  Connection Lifecycle Management
    · Pool Tracking
    · Cleanup Process
  Integration with Services

## · Search and Indexing  (L16164)
  源文件: services/db/migrations/0019_add_vector_indexes.sql, services/db/migrations/0020_add_chunks_fulltext_index.sql
  Purpose and Scope
  Search Architecture
  Index Types
  Full-Text Search Implementation
    · GIN Indexes
    · Performance Characteristics
  Vector Similarity Search
    · HNSW Index Configuration
    · HNSW Algorithm
  Composite Indexes for Filtering
    · Version and Embedding Filter
    · Version Join Optimization
  Hybrid Search Strategy
    · Hybrid Search Algorithm
    · Search Type Selection
  Query Optimization Patterns
    · Active Version Filtering
    · Embedding Existence Check
    · Document Join Optimization
  Index Maintenance
    · Building Indexes
    · Index Build Time
    · Index Storage
  Performance Monitoring
    · Query Plan Analysis
    · Index Statistics

## · AI and LLM Integration  (L16571)
  源文件: .prettierignore, .prettierrc.json, CLAUDE.md, services/action-builder/.gitignore, services/action-builder/package.json, services/action-builder/scripts/crawl-playbook-batch.ts, services/action-builder/scripts/crawl-sites.txt.example, services/action-builder/scripts/import-playbook-batch.ts, services/action-builder/scripts/login.ts, services/action-builder/src/llm/AIClient.ts, services/action-builder/src/optimizer/SelectorOptimizer.ts, services/action-builder/src/utils/logger.ts
  Overview
  Multi-Provider LLM Architecture
    · AIClient Design
    · Provider Detection and Priority
    · Message Format Conversion
    · Proxy Support
    · Metrics and Observability
    · Retry Logic
  Selector Optimization
    · Unstable Selector Patterns
    · Selector Priority Ranking
    · Batch Processing
    · Model Configuration
  Integration Points
    · Action Recording Loop
    · Browser Automation AI Operations
    · Capability Discovery
  Configuration
    · Environment Variables
    · Explicit Provider Configuration
  Error Handling and Reliability
    · Error Classification
    · Retry Strategy
    · Cost Optimization
  Dependencies

## · AIClient  (L17065)
  源文件: .prettierignore, .prettierrc.json, CLAUDE.md, services/action-builder/.gitignore, services/action-builder/package.json, services/action-builder/scripts/crawl-playbook-batch.ts, services/action-builder/scripts/crawl-sites.txt.example, services/action-builder/scripts/import-playbook-batch.ts, services/action-builder/scripts/login.ts, services/action-builder/src/llm/AIClient.ts, services/action-builder/src/optimizer/SelectorOptimizer.ts, services/action-builder/src/utils/logger.ts
  Purpose and Scope
  Architecture and Provider Support
    · Provider Resolution Hierarchy
    · Supported Providers
  Configuration Resolution
    · AIClientConfig Interface
    · Model Creation with Proxy Support
  Message Format Conversion
    · Message Conversion Flow
    · Tool Call Conversion Details
  Tool Calling Support
    · Tool Conversion Process
    · Tool Call Response Conversion
  Metrics Collection
    · LLMMetrics Interface
    · Metrics Collection and Logging
    · Example Log Output
  Error Handling and Retry Logic
    · Built-in Retry Mechanism
    · Error Classification
  Proxy Support
    · Proxy Configuration Flow
  Usage in Action Builder
    · Class Structure and Dependencies
    · ActionRecorder Integration Example
  Configuration Examples
    · OpenRouter (Recommended)
    · OpenAI
    · Anthropic
    · AWS Bedrock
    · Proxy Configuration
  Related Components

## · Selector Optimizer  (L17572)
  源文件: .prettierignore, .prettierrc.json, CLAUDE.md, services/action-builder/scripts/login.ts, services/action-builder/scripts/playbook-record.ts, services/action-builder/src/optimizer/SelectorOptimizer.ts, services/action-builder/src/recorder/RecorderToolExecutor.ts, services/action-builder/src/validator/SelectorValidator.ts, services/action-builder/test/browser/xpath-optimizer.ut.test.ts, services/action-builder/test/validator/SelectorValidator.ut.test.ts, services/common/browser-profile/package.json, services/common/browser-profile/src/BrowserProfileManager.ts
  Purpose and Scope
  Overview
  Architecture
  Selector Stability Patterns
    · Unstable Patterns
    · Stable Patterns
  LLM Provider Configuration
    · Provider Priority
  Input and Output Format
    · SelectorInput
    · SelectorAnalysisResult
    · OptimizationResult
  Optimization Process
    · Step-by-Step Process
  Integration Points
    · Action Recording Integration
    · Database Persistence
  Error Handling
  Performance Considerations

## · Capability Discovery  (L17974)
  源文件: services/action-builder/scripts/playbook-record.ts, services/action-builder/src/recorder/RecorderToolExecutor.ts, services/action-builder/src/task-worker/utils/prompt-builder.ts, services/action-builder/src/validator/SelectorValidator.ts, services/action-builder/test/browser/xpath-optimizer.ut.test.ts, services/action-builder/test/validator/SelectorValidator.ut.test.ts, services/db/src/models/build-task.ts, services/playbook-builder/scripts/worker.ts, services/playbook-builder/src/analyzer/page-analyzer.ts, services/playbook-builder/src/controller/playbook-task-controller.ts, services/playbook-builder/src/discoverer/capabilities-discoverer.ts, services/playbook-builder/src/discoverer/page-discoverer.ts
  Purpose and Scope
  Discovery Architecture
    · Discovery Flow Diagram
  Element Discovery with observe_page
    · Tool Parameters
    · Execution Flow
    · ObserveResultItem Structure
  Element Registration with register_element
    · Selector Priority Hierarchy
    · Automatic Selector Extraction
  Multi-Selector Extraction Strategy
    · Extraction Logic
    · Special Handling: ID with Special Characters
  Template Pattern Detection
    · Template Detection Algorithm
    · Template Example
    · Component Overview
    · PageDiscoverer Workflow
    · DiscoveredPage Structure
  Capabilities Discovery (7-Section Playbook)
    · Playbook Structure
    · Playbook Generation Flow
    · Key Implementation Notes
  Integration with Action Recording
    · Task-Driven Discovery
    · Exploratory Discovery
  Real-World Example: Multi-Step Discovery
    · Step 1: Initial Observation
    · Step 2: Multi-Selector Registration
    · Step 3: Template Pattern Detection
  Validation Integration

## · Data Models and Types  (L18564)
  源文件: packages/js-sdk/src/api-client.ts, packages/js-sdk/src/client.ts, packages/js-sdk/src/tool-defs.ts, packages/js-sdk/src/types.ts, services/action-builder/src/recorder/RecorderTools.ts, services/action-builder/src/types/capability.ts, services/action-builder/src/utils/index.ts, services/action-builder/src/utils/url-matcher.ts, services/action-builder/test/recorder/RecorderTools.ut.test.ts, services/action-builder/test/types/capability.ut.test.ts, services/action-builder/test/utils/url-matcher.ut.test.ts
  Purpose and Scope
  Capability Type Hierarchy
    · Type Relationship Diagram
    · SiteCapability
    · PageCapability
    · ElementCapability
  Element Types and Enumerations
    · ElementType Enum
    · AllowMethod Enum
    · PageModule Enum
  Selector System
    · SelectorItem Structure
    · SelectorType Enum
    · Template Parameters
  Tool Definitions
    · Tool Definition Architecture
    · ToolDefinition Interface
    · ToolParams Interface
    · SDK Tool Schemas
  Recorder Tool Definitions
    · Recorder Tool Overview
    · Core Recorder Tools
    · Navigation and Utility Tools
  API Response Types
    · ChunkSearchResult
    · ChunkActionDetail
    · SourceItem
    · SourceListResult and SourceSearchResult
  Type System Relationships
    · Cross-System Type Flow
    · Type Import Patterns

## · Capability Types  (L19390)
  源文件: services/action-builder/src/recorder/RecorderTools.ts, services/action-builder/src/types/capability.ts, services/action-builder/src/utils/index.ts, services/action-builder/src/utils/url-matcher.ts, services/action-builder/test/recorder/RecorderTools.ut.test.ts, services/action-builder/test/types/capability.ut.test.ts, services/action-builder/test/utils/url-matcher.ut.test.ts
  Purpose and Scope
  Capability Hierarchy
  SiteCapability
  ElementCapability
    · Core Fields
    · Structural Relationships
    · Page Location
    · Element-Specific Attributes
  Type Enumerations
    · Element Types
    · Interaction Methods
    · Page Modules
  ArgumentDef
  Capability Type Flow
  Tool Definition Integration
  Type Re-exports and Dependencies

## · Selector Types  (L19800)
  源文件: services/action-builder/scripts/playbook-record.ts, services/action-builder/src/recorder/RecorderToolExecutor.ts, services/action-builder/src/recorder/RecorderTools.ts, services/action-builder/src/types/capability.ts, services/action-builder/src/utils/index.ts, services/action-builder/src/utils/url-matcher.ts, services/action-builder/src/validator/SelectorValidator.ts, services/action-builder/test/browser/xpath-optimizer.ut.test.ts, services/action-builder/test/recorder/RecorderTools.ut.test.ts, services/action-builder/test/types/capability.ut.test.ts, services/action-builder/test/utils/url-matcher.ut.test.ts, services/action-builder/test/validator/SelectorValidator.ut.test.ts
  Overview
  SelectorItem Data Structure
  Selector Types
    · Type Definitions
  Priority Ordering System
  Confidence Scores
    · Confidence Score Table
    · Confidence Adjustment
  Template Patterns
    · Template Parameter Definition
    · Template Usage Example
  Multi-Selector Extraction Process
    · Key Functions
  Selector Validation
    · Validation States
    · XPath Validation Special Handling
  Selector Optimization
  Common Selector Patterns
    · Special Character Handling
    · CSS Selector Template Detection
  Integration with Recording Tools

## · Tool Definitions  (L20316)
  源文件: packages/js-sdk/src/api-client.ts, packages/js-sdk/src/client.ts, packages/js-sdk/src/tool-defs.ts, packages/js-sdk/src/types.ts
  Purpose and Scope
  Tool Schema Architecture
    · Core Interfaces
    · Schema Format Conversion
  Tool Reference
    · searchActions
    · getActionById
    · listSources
    · searchSources
  SDK Integration Architecture
  Method Attachment Pattern
  LLM Framework Integration Examples
    · Tool Definition Export Structure
  Type Safety and Validation
  Tool Lifecycle and Error Handling

## · Development Guide  (L20936)
  源文件: .gitignore, LICENSE, README.md, mcp-servers.json, package.json, packages/cli/package.json, packages/js-sdk/package.json, packages/mcp/package.json, pnpm-lock.yaml, pnpm-workspace.yaml, services/action-builder/.nvmrc, turbo.json
  Prerequisites
  Workspace Organization
    · Monorepo Directory Structure
  Development Workflow
    · Development Task Flow
  Quick Start
  Common Development Commands
  Package Dependencies
    · Internal Package Dependency Graph
  Build Output and Artifacts
  Environment Configuration
  Git Hooks
  Next Steps

## · Monorepo Structure  (L21278)
  源文件: .gitignore, LICENSE, mcp-servers.json, package.json, packages/cli/package.json, packages/js-sdk/package.json, packages/mcp/package.json, pnpm-lock.yaml, pnpm-workspace.yaml, services/action-builder/.nvmrc, turbo.json
  Workspace Organization
    · Workspace Configuration
  Package Categories
    · Published Packages
    · Services
    · Common Packages
    · Playground and Evaluation
  Dependency Graph
  File System Layout
  Package Manager Configuration
  Development Workflow

## · Build System  (L21653)
  源文件: .gitignore, mcp-servers.json, package.json, pnpm-lock.yaml, pnpm-workspace.yaml, services/action-builder/.nvmrc, turbo.json
  Purpose and Scope
  Overview
  Turborepo Configuration
    · Task Dependency Graph
    · Task Definitions
  Workspace Organization
    · Workspace Package Mapping
  Build Task Execution
    · Topological Build Order
    · Task Execution Lifecycle
  Caching Strategy
    · Cache Behavior by Task
    · Cache Location
  Package Manager Integration
    · pnpm Configuration
    · Dependency Overrides
  Running Tasks
    · Root-Level Commands
    · Scoped Execution
    · Parallel Execution
  Build Outputs
    · Output Directory Structure
    · TypeScript Build Info
  Package-Specific Build Tools
    · Build Tool by Package Type
  Development Mode
    · Persistent Development Tasks
    · No Caching for Development
  Git Hooks Integration

## · Local Development Setup  (L22124)
  源文件: README.md, services/db/src/connection.ts
  Purpose and Scope
  Prerequisites
  Setup Flow Overview
  Step 1: Clone Repository and Install Dependencies
  Step 2: Database Setup
    · Local PostgreSQL Setup
  Step 3: Environment Configuration
    · Database Connection Strategy
    · Required Environment Files
    · Environment Variable Reference
    · Connection Pool Configuration
  Step 4: Database Migrations
  Step 5: Browser Setup
  Step 6: Running Services
    · Development Server
    · Individual Service Commands
    · Building Packages
  Step 7: Verification
    · Verify API Service
    · Verify CLI
    · Verify Database Connection
    · Verify Services Status
  Common Development Tasks
    · Resetting the Database
    · Clearing Browser Profiles
    · Running in Watch Mode
    · Inspecting the Database
  Troubleshooting
    · Database Connection Errors
    · Port Already in Use
    · Browser Installation Issues
    · TypeScript Build Errors
    · Migration Failures
  Next Steps

## · Testing  (L22843)
  源文件: .gitignore, mcp-servers.json, package.json, pnpm-lock.yaml, pnpm-workspace.yaml, services/action-builder/.nvmrc, services/action-builder/src/task-worker/build-task-runner.ts, services/action-builder/src/task-worker/coordinator.ts, services/action-builder/src/task-worker/recording-task-queue-worker.ts, services/action-builder/test/coordinator.integration.it.test.ts, services/action-builder/test/task-worker/integration/end-to-end.it.test.ts, turbo.json
  Testing Framework and Tools
    · Core Testing Stack
    · Package-Level Test Configuration
  Test Types and Organization
    · Test Naming Conventions
    · Unit Tests
    · Integration Tests
    · End-to-End Tests
  Running Tests
    · Running All Tests
    · Running Tests for Specific Package
    · Running Specific Test Files
    · Running Integration Tests Only
  Test Structure and Patterns
    · Typical Test File Structure
    · Lifecycle Hooks
    · Test Timeout Configuration
  Mocking Strategies
    · Mocking External Dependencies
    · Mock Characteristics
  Test Helpers and Utilities
    · Common Test Helper Functions
    · Helper Function Patterns
  Writing New Tests
    · Integration Test Template
    · Test Isolation Guidelines
    · Database Test Data Pattern
  Test Coverage Areas
    · Core Component Tests
    · Integration Test Matrix
  Continuous Integration
    · Turbo Task Configuration
    · Running Tests in CI
  Best Practices
    · Do's
    · Don'ts