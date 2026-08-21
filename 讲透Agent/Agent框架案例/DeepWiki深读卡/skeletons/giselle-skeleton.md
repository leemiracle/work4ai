# Skeleton: giselle（37 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 26KB | 5 | ~12 | 21 |
| 2 | Project Structure and Organization | L663 | 25KB | 2 | ~5 | 7 |
| 3 | Package Architecture and Dependencies | L1505 | 22KB | 4 | ~26 | 7 |
| 4 | Build System and Development Workflow | L2290 | 21KB | 3 | ~12 | 20 |
| 5 | Core Engine and SDK | L2929 | 23KB | 9 | ~19 | 14 |
| 6 | Engine Architecture and Configuration | L3555 | 20KB | 7 | ~10 | 14 |
| 7 | Generation Pipeline and Lifecycle | L4115 | 31KB | 11 | ~11 | 14 |
| 8 | Language Models and AI Provider Integration | L5036 | 30KB | 13 | ~7 | 21 |
| 9 | Act Runner and Workflow Orchestration | L5914 | 28KB | 10 | ~4 | 21 |
| 10 | Storage and Vault Systems | L6748 | 20KB | 12 | ~13 | 14 |
| 11 | Database Schema and Data Model | L7370 | 27KB | 10 | ~27 | 16 |
| 12 | Tool System and External Integrations | L7990 | 19KB | 9 | ~6 | 14 |
| 13 | Knowledge and Context Systems | L8539 | 44KB | 11 | ~15 | 16 |
| 14 | Document Processing Pipeline | L9413 | 16KB | 5 | ~3 | 13 |
| 15 | Vector Store Management | L9839 | 36KB | 13 | ~7 | 16 |
| 16 | RAG System and Query Execution | L10747 | 20KB | 7 | ~5 | 16 |
| 17 | GitHub Integration | L11218 | 38KB | 10 | ~7 | 9 |
| 18 | GitHub Triggers and Event Processing | L12085 | 24KB | 8 | ~10 | 9 |
| 19 | GitHub Actions and Integration | L12634 | 23KB | 9 | ~12 | 9 |
| 20 | Workflow Designer UI | L13129 | 24KB | 13 | ~13 | 13 |
| 21 | Editor Architecture and State Management | L13783 | 33KB | 13 | ~10 | 13 |
| 22 | Node Rendering and Visual System | L14683 | 28KB | 11 | ~10 | 17 |
| 23 | Properties Panels and Node Configuration | L15495 | 31KB | 9 | ~10 | 13 |
| 24 | Toolbar and Node Creation Flow | L16201 | 24KB | 6 | ~15 | 17 |
| 25 | Generation Execution and Results Display | L16750 | 36KB | 6 | ~6 | 13 |
| 26 | Model Configuration Panels | L17746 | 28KB | 12 | ~13 | 17 |
| 27 | Applications and User Interfaces | L18406 | 41KB | 18 | ~24 | 7 |
| 28 | Studio Application | L19542 | 22KB | 6 | ~12 | 10 |
| 29 | Workspace Context and Feature Flags | L20107 | 16KB | 6 | ~9 | 3 |
| 30 | Stage System and Act Execution | L20604 | 25KB | 7 | ~13 | 19 |
| 31 | Vector Store Management Interface | L21269 | 45KB | 11 | ~17 | 16 |
| 32 | Playground Application | L22411 | 12KB | 4 | ~9 | 7 |
| 33 | Infrastructure and Cross-Cutting Concerns | L22816 | 17KB | 7 | ~6 | 7 |
| 34 | Feature Flag System | L23346 | 20KB | 6 | ~10 | 3 |
| 35 | UI Component Library and Theming | L24012 | 19KB | 7 | ~3 | 13 |
| 36 | Observability and Telemetry | L24603 | 23KB | 16 | ~7 | 21 |
| 37 | Build and Deployment | L25308 | 18KB | 6 | ~4 | 20 |


## · Overview  (L6)
  源文件: apps/playground/giselle-engine.ts, apps/playground/package.json, apps/studio.giselles.ai/app/giselle-engine.ts, apps/studio.giselles.ai/package.json, internal-packages/workflow-designer-ui/package.json, package.json, packages/giselle/package.json, packages/giselle/src/engine/acts/run-act.ts, packages/giselle/src/engine/generations/generate-content.ts, packages/giselle/src/engine/generations/generate-image.ts, packages/giselle/src/engine/generations/internal/use-generation-executor.ts, packages/giselle/src/engine/generations/types.ts
  Purpose and Scope
  System Architecture
  Monorepo Organization
    · Workspace Structure
    · Dependency Management
  Key Applications
    · studio.giselles.ai
    · playground
    · ui.giselles.ai
  Core Engine Packages
    · @giselles-ai/giselle
    · @giselles-ai/protocol
    · @giselles-ai/language-model
    · @giselles-ai/node-registry
    · @giselles-ai/action-registry & @giselles-ai/trigger-registry
    · @giselles-ai/rag
  Technology Stack
    · Frontend Stack
    · Backend Stack
    · LLM Provider Integration
    · Build Toolchain
  Deployment and Infrastructure
    · Hosting
    · Configuration Management
    · Observability
  Development Workflow
    · Build Pipeline
    · Code Quality Gates
    · Release Process
  Summary

## · Project Structure and Organization  (L663)
  源文件: apps/playground/package.json, apps/studio.giselles.ai/package.json, internal-packages/workflow-designer-ui/package.json, package.json, packages/giselle/package.json, pnpm-lock.yaml, pnpm-workspace.yaml
  Purpose and Scope
  Monorepo Overview
    · Directory Layout
  Apps Directory
    · studio.giselles.ai
    · playground
    · ui.giselles.ai
  Packages Directory (Giselle SDK)
    · Core Engine Packages
    · Data Processing Packages
    · Integration Packages
    · Storage and Observability Packages
    · UI and Editor Packages
    · Supporting Packages
  Internal Packages Directory
    · @giselle-internal/ui
    · @giselle-internal/workflow-designer-ui
  Tools Directory
    · @giselle/giselle-sdk-tsconfig
  Package Dependency Graph
  Workspace Protocol and Dependency Management
    · Workspace Dependency Syntax
    · Catalog System
    · Package Manager Configuration
    · Package Manager Configuration
  Scripts and Utilities
    · report-colors.mjs
    · Codemods
  Build Configuration and TypeScript Setup
    · Build Output Locations
    · TypeScript Configuration
    · PostCSS Configuration
    · Server External Packages
  Summary

## · Package Architecture and Dependencies  (L1505)
  源文件: apps/playground/package.json, apps/studio.giselles.ai/package.json, internal-packages/workflow-designer-ui/package.json, package.json, packages/giselle/package.json, pnpm-lock.yaml, pnpm-workspace.yaml
  Overview and Scope
  Monorepo Structure
  Dependency Catalog System
    · Catalog Definition
    · Catalog Usage
    · Catalog Benefits
  Package Layers and Dependencies
    · Layer Overview
  Protocol Layer
    · @giselles-ai/protocol
    · @giselles-ai/language-model
  Registry Layer
    · @giselles-ai/action-registry
    · @giselles-ai/trigger-registry
    · @giselles-ai/node-registry
  Core Engine Layer
    · @giselles-ai/giselle
  Integration Layer
    · @giselles-ai/rag
    · @giselles-ai/github-tool
    · @giselles-ai/web-search
    · @giselles-ai/document-preprocessor
    · @giselles-ai/supabase-driver
  Utility Layer
    · @giselles-ai/text-editor
    · @giselles-ai/text-editor-utils
    · @giselles-ai/langfuse
    · @giselles-ai/telemetry
    · @giselles-ai/utils
  Internal Packages Layer
    · @giselle-internal/ui
    · @giselle-internal/workflow-designer-ui
  Applications Layer
    · studio.giselles.ai
    · playground
  Key External Dependencies
    · AI and Language Models
    · React and UI Framework
    · Database and Vector Store
    · Authentication and Storage
    · GitHub Integration
    · Observability
    · Infrastructure
  Complete Dependency Graph
  Package Version Management
    · Workspace Protocol
    · Overrides

## · Build System and Development Workflow  (L2290)
  源文件: apps/playground/package.json, apps/studio.giselles.ai/package.json, docs/packages-license.md, internal-packages/workflow-designer-ui/package.json, package.json, packages/document-preprocessor/README.md, packages/document-preprocessor/package.json, packages/document-preprocessor/src/global.d.ts, packages/document-preprocessor/src/index.ts, packages/document-preprocessor/src/pdf.ts, packages/document-preprocessor/src/text.test.ts, packages/document-preprocessor/src/text.ts
  Purpose and Scope
  Package Management with pnpm
    · Workspace Configuration
    · Lockfile Structure
    · Package Manager Version
  Dependency Catalog System
    · Catalog Definition
    · Catalog Usage Pattern
    · Catalog in Lockfile
  Turbo Build Orchestration
    · Turbo Configuration
    · Build Scripts
    · Task Filtering
    · Turbo Caching
  Workspace Dependency Graph
  Key External Dependencies
    · AI and LLM Integration
    · Next.js and React Ecosystem
    · Database and Storage
    · UI and Visualization
    · Observability and Monitoring
    · Background Processing
  Build Scripts and Commands
    · Root-Level Scripts
    · Application-Level Scripts
    · Utility Scripts
  Version Constraints and Overrides
    · Node.js Version Requirements
    · Dependency Overrides
    · TypeScript Version
  Dependency Resolution Flow
  Development Tools
    · Code Quality with Biome
    · Dependency Analysis with Knip
    · Bundle Analysis
  Build Output Structure

## · Core Engine and SDK  (L2929)
  源文件: apps/playground/giselle-engine.ts, apps/studio.giselles.ai/app/giselle-engine.ts, packages/giselle/src/engine/acts/run-act.ts, packages/giselle/src/engine/generations/generate-content.ts, packages/giselle/src/engine/generations/generate-image.ts, packages/giselle/src/engine/generations/internal/use-generation-executor.ts, packages/giselle/src/engine/generations/types.ts, packages/giselle/src/engine/generations/utils.ts, packages/giselle/src/engine/operations/execute-query.ts, packages/giselle/src/engine/telemetry/index.ts, packages/giselle/src/engine/telemetry/types.ts, packages/giselle/src/engine/triggers/resolve-trigger.ts
  Purpose and Scope
  Architecture Overview
  NextGiselleEngine Configuration
    · Configuration Interface
    · Studio Configuration Example
    · Runtime Environment Detection
  SDK Package Ecosystem
    · Core SDK Packages
    · Package Responsibilities
  Generation Operations
    · Operation Function Signatures
    · Operation Implementations
  useGenerationExecutor Lifecycle
    · Resolver Functions
    · finishGeneration Function
  Integration Points
    · LLM Provider Integration
    · Vector Store Integration
    · Tool Integration
  Process Delegation
    · Generate Content Process Delegation
    · Run Act Process Delegation
  Callbacks and Telemetry
    · Callback Types
    · Telemetry Context
  Storage Interface Abstraction

## · Engine Architecture and Configuration  (L3555)
  源文件: apps/playground/giselle-engine.ts, apps/studio.giselles.ai/app/giselle-engine.ts, packages/giselle/src/engine/acts/run-act.ts, packages/giselle/src/engine/generations/generate-content.ts, packages/giselle/src/engine/generations/generate-image.ts, packages/giselle/src/engine/generations/internal/use-generation-executor.ts, packages/giselle/src/engine/generations/types.ts, packages/giselle/src/engine/generations/utils.ts, packages/giselle/src/engine/operations/execute-query.ts, packages/giselle/src/engine/telemetry/index.ts, packages/giselle/src/engine/telemetry/types.ts, packages/giselle/src/engine/triggers/resolve-trigger.ts
  Overview
  Engine Initialization
    · NextGiselleEngine Factory
    · GiselleEngineContext Structure
  Runtime Environment Detection
    · getRuntimeEnv Function
    · Processor Selection Logic
  Configuration Components
    · Storage Driver Configuration
    · Vault Driver Configuration
    · LLM Provider Configuration
    · AI Gateway Configuration
    · Integration Configuration
  Callback System
    · Lifecycle Callbacks
    · Telemetry Configuration
  Process Delegation
    · Content Generation Process
    · Act Execution Process
  Vector Store Query Services
  Configuration Differences: Studio vs Playground
  Sample App Workspace IDs

## · Generation Pipeline and Lifecycle  (L4115)
  源文件: apps/playground/giselle-engine.ts, apps/studio.giselles.ai/app/giselle-engine.ts, packages/giselle/src/engine/acts/run-act.ts, packages/giselle/src/engine/generations/generate-content.ts, packages/giselle/src/engine/generations/generate-image.ts, packages/giselle/src/engine/generations/internal/use-generation-executor.ts, packages/giselle/src/engine/generations/types.ts, packages/giselle/src/engine/generations/utils.ts, packages/giselle/src/engine/operations/execute-query.ts, packages/giselle/src/engine/telemetry/index.ts, packages/giselle/src/engine/telemetry/types.ts, packages/giselle/src/engine/triggers/resolve-trigger.ts
  Purpose and Scope
  Generation Lifecycle States
    · Generation Type Definitions
  useGenerationExecutor Architecture
    · Key Responsibilities
  Generation Type Implementations
    · Text Generation Flow
    · Chunk Persistence and Resumability
    · Image Generation Flow
    · Query Execution Flow
  Streaming Operations
    · UI Message Stream Structure
    · Batch Writing for Resumability
  Cancellation Support
    · Cancellation Detection
    · UI Cancellation Flow
  Process Delegation: Self vs Trigger.dev
    · Delegation Configuration
    · Trigger.dev Process Configuration
  Storage Paths and Persistence
    · Generation Storage Paths
    · Storage Backend
  Callbacks and Telemetry
    · Lifecycle Callbacks
    · Callback Timing
  Summary: Key Components

## · Language Models and AI Provider Integration  (L5036)
  源文件: apps/playground/giselle-engine.ts, apps/playground/package.json, apps/studio.giselles.ai/app/giselle-engine.ts, apps/studio.giselles.ai/package.json, internal-packages/workflow-designer-ui/package.json, package.json, packages/giselle/package.json, packages/giselle/src/engine/acts/run-act.ts, packages/giselle/src/engine/generations/generate-content.ts, packages/giselle/src/engine/generations/generate-image.ts, packages/giselle/src/engine/generations/internal/use-generation-executor.ts, packages/giselle/src/engine/generations/types.ts
  Purpose and Scope
  Provider Architecture
    · Provider Registration
    · Provider SDK Mapping
  AI SDK Integration
    · Core Functions
    · Model Instantiation Pattern
  Model Selection System
    · Model Registry
    · UI Model Filtering
  Provider-Specific Features
    · Reasoning Configuration
    · Search Grounding
    · Tool Execution Limits
  Tier-Based Access Control
    · Model Tier System
    · Recommended Models by Tier
  Usage Calculation System
    · Usage Calculator Interface
    · Fal Image Generation Usage
    · OpenAI Image Generation Usage
    · Usage Calculator Factory
  Model Provider Utilities
    · Image Generation Model Provider Detection
  AI Gateway Configuration
    · Gateway Setup
    · Gateway vs Direct Provider
  Generation Pipeline Integration
    · Text Generation Flow
    · Image Generation Flow
    · Batch Generation (Trigger.dev)
  Configuration Workflow
    · Engine Initialization
    · Workspace Provider Integration

## · Act Runner and Workflow Orchestration  (L5914)
  源文件: apps/playground/.gitignore, apps/playground/giselle-engine.ts, apps/studio.giselles.ai/app/(main)/workspaces/actions.ts, apps/studio.giselles.ai/app/api/workspaces/route.ts, apps/studio.giselles.ai/app/giselle-engine.ts, apps/studio.giselles.ai/app/stage/(top)/actions.ts, apps/studio.giselles.ai/app/stage/(top)/circular-carousel.module.css, apps/studio.giselles.ai/app/stage/(top)/circular-carousel.tsx, apps/studio.giselles.ai/app/stage/(top)/form-input-renderer.tsx, apps/studio.giselles.ai/app/stage/(top)/form.tsx, apps/studio.giselles.ai/app/stage/(top)/helpers.ts, apps/studio.giselles.ai/app/stage/(top)/page.tsx
  Purpose and Scope
  Act Concept and Data Model
    · Act Status Lifecycle
  Act Creation and Initialization
    · Creation Flow Diagram
    · Act Creation Implementation
    · Starting Act Execution
  Execution Architecture
    · Processor Selection
    · Act Runner Process Configuration
    · setRunActProcess Configuration
  Sequence and Step Execution
    · Execution Flow
    · executeStep Implementation
    · waitUntilGenerationFinishes
  Patch Queue Management
    · Patch Queue Concept
    · Patch Queue Lifecycle
  Lifecycle Callbacks
    · Callback Types
    · Callback Invocation Flow
    · Callback Implementation Example
  Generation Execution within Acts
    · Act-Scoped Generation Lookup
    · Generation Index Paths
    · Generation Context Resolution
  Stage System Integration
    · Stage Components
    · Stage Act Creation Flow
    · Stage Act Tracking
  Act Status Monitoring
    · Status Navigation Links
    · Act List Filtering
  Integration with Generation Pipeline
    · Act-Generation Relationship
    · Generation Metadata in Acts
  Error Handling and Recovery
    · Error Propagation
    · Execution Error Handling
  Summary

## · Storage and Vault Systems  (L6748)
  源文件: apps/playground/giselle-engine.ts, apps/studio.giselles.ai/app/giselle-engine.ts, packages/giselle/src/engine/acts/run-act.ts, packages/giselle/src/engine/generations/generate-content.ts, packages/giselle/src/engine/generations/generate-image.ts, packages/giselle/src/engine/generations/internal/use-generation-executor.ts, packages/giselle/src/engine/generations/types.ts, packages/giselle/src/engine/generations/utils.ts, packages/giselle/src/engine/operations/execute-query.ts, packages/giselle/src/engine/telemetry/index.ts, packages/giselle/src/engine/telemetry/types.ts, packages/giselle/src/engine/triggers/resolve-trigger.ts
  Storage System Architecture
    · Storage Abstraction Interface
    · Storage Driver Implementations
    · Storage Path Organization
  Vault System Architecture
    · Vault Abstraction Interface
    · Vault Driver Implementations
    · Vault Integration in Engine Context
  Storage Usage Patterns
    · Generation Data Storage Flow
    · File Resolution and Retrieval
    · Generated Image Storage
    · Generation Index Storage
  Vault Usage Patterns
    · Secret Decryption for Tools
    · GitHub Authentication Decryption
    · Database Connection Decryption
  Runtime Environment Selection
    · Environment Detection
    · Driver Configuration Examples
  Storage Access Patterns
    · Batch Writing for Streaming Data
    · Generation Retrieval Pattern

## · Database Schema and Data Model  (L7370)
  源文件: apps/playground/.gitignore, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/configure-sources-dialog.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/data.ts, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/diagnostic-modal.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-embedding-profiles.ts, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-store-create-dialog.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-vector-store-list.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/page.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/layout.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/navigation-layout.tsx
  Purpose and Scope
  Database Technology Stack
  Core Entity Relationship Diagram
  Team and User Management Schema
    · Teams Table
    · Users and Authentication
  Workflow and Execution Schema
    · Flow Triggers Table
    · Acts Table (Execution Tracking)
    · Act Status and Navigation
    · Agents Table
  Vector Store Schema
    · GitHub Vector Store System
    · Document Vector Store System
  Status Tracking and State Machines
    · Content Status State Machine
    · Ingestability Logic
    · Error Handling and Retry
  Data Access Patterns
    · Multi-Tenancy Enforcement
    · Quota Enforcement with Row Locking
    · Compound Status Queries
    · Cascading Deletes
  Embedding Profile Configuration
    · Supported Embedding Models
    · Profile Selection UI
  Storage Integration
    · Supabase Storage Structure
    · Storage Cleanup on Deletion
  pgvector Integration

## · Tool System and External Integrations  (L7990)
  源文件: apps/playground/giselle-engine.ts, apps/studio.giselles.ai/app/giselle-engine.ts, packages/giselle/src/engine/acts/run-act.ts, packages/giselle/src/engine/generations/generate-content.ts, packages/giselle/src/engine/generations/generate-image.ts, packages/giselle/src/engine/generations/internal/use-generation-executor.ts, packages/giselle/src/engine/generations/types.ts, packages/giselle/src/engine/generations/utils.ts, packages/giselle/src/engine/operations/execute-query.ts, packages/giselle/src/engine/telemetry/index.ts, packages/giselle/src/engine/telemetry/types.ts, packages/giselle/src/engine/triggers/resolve-trigger.ts
  Purpose and Architecture
    · Tool Lifecycle Overview
  PreparedToolSet Data Structure
  GitHub Tools Integration
    · GitHub Tool Configuration
    · Tool Preparation Logic
    · Authentication Flow
    · Available GitHub Tools
  Postgres Tools Integration
    · Postgres Tool Preparation
    · Implementation Details
  Web Search Tools Integration
    · Provider Tool Mapping
    · OpenAI Web Search Tools
    · Google Search and URL Context Tools
    · Anthropic Web Search Tool
  Tool Injection into LLM Calls
    · Tool Step Limiting
    · streamText Integration
  Tool Cleanup and Resource Management
    · Cleanup Execution Flow
  Integration Configuration
    · GitHub Integration Configuration
  Tool Security and Secrets Management
    · Secret Resolution Pattern

## · Knowledge and Context Systems  (L8539)
  源文件: apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/configure-sources-dialog.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/data.ts, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/diagnostic-modal.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-embedding-profiles.ts, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-store-create-dialog.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-vector-store-list.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/page.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/layout.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/navigation-layout.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/page.tsx
  3.1 Document Processing Pipeline
    · Architecture and Core Components
    · Processing Functions
    · PDF Processing Implementation
    · Text Normalization
    · Image Rendering Pipeline
    · Abort Signal Support
    · Security Considerations
  3.2 Vector Store Management
    · Vector Store Types and Database Schema
    · GitHub Repository Vector Store
    · Document Vector Store
    · Embedding Profile System
    · Manual Ingestion and Status Management
    · Diagnostic and Recovery System
    · Storage Layer Integration
  3.3 RAG System and Query Execution
    · RAG Pipeline Architecture
    · Chunking Strategies
    · Embedding Generation
    · Query Resolution and Template References
    · Similarity Search with pgvector
    · Query Execution and Context Assembly
    · Error Handling and Retry Logic
    · Integration with Workflow Nodes

## · Document Processing Pipeline  (L9413)
  源文件: docs/packages-license.md, packages/document-preprocessor/README.md, packages/document-preprocessor/package.json, packages/document-preprocessor/src/global.d.ts, packages/document-preprocessor/src/index.ts, packages/document-preprocessor/src/pdf.ts, packages/document-preprocessor/src/text.test.ts, packages/document-preprocessor/src/text.ts, packages/document-preprocessor/src/types.ts, packages/document-preprocessor/tsconfig.json, packages/document-preprocessor/tsup.config.ts, packages/document-preprocessor/turbo.json
  Purpose and Scope
  Architecture Overview
  Public API Surface
  PDF Text Extraction
    · Processing Flow
    · Configuration Options
    · Text Normalization
  PDF Image Rendering
    · Rendering Pipeline
    · DPI Calculation
    · PNG Encoding
    · Form Field Rendering
  Text and Markdown Processing
    · Encoding Support
  Internal Utilities
    · Abort Signal Handling
    · Binary Data Conversion
    · PDFium Document Lifecycle
  Type System
    · Input Types
    · Result Types
  Security Considerations
    · PDFium Sandboxing
    · Password-Protected PDFs
    · Resource Limits
  Integration with RAG System
    · Document Upload Flow
    · Output Format
    · Image Processing for Multimodal RAG
  Build Configuration
    · TypeScript Configuration
    · Build Setup
    · Package Metadata

## · Vector Store Management  (L9839)
  源文件: apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/configure-sources-dialog.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/data.ts, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/diagnostic-modal.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-embedding-profiles.ts, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-store-create-dialog.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-vector-store-list.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/page.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/layout.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/navigation-layout.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/page.tsx
  Purpose and Scope
  System Architecture Overview
  GitHub Vector Stores
    · Registration and Configuration
    · Content Type Management
    · Embedding Profile Selection
    · Repository Item Display and Status
    · Manual Ingestion
    · Diagnostic System
  Document Vector Stores
    · Creation and Configuration
    · Document Upload and Management
    · Document Vector Store Configuration
    · Document Deletion and Cleanup
  Database Schema
  Server Actions and API Routes
  Plan-Based Quota Management
  Navigation and Layout

## · RAG System and Query Execution  (L10747)
  源文件: apps/playground/giselle-engine.ts, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/configure-sources-dialog.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/data.ts, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/diagnostic-modal.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-embedding-profiles.ts, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-store-create-dialog.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-vector-store-list.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/page.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/layout.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/navigation-layout.tsx
  Purpose and Scope
  RAG System Architecture
  Query Context Types
  Query Execution Pipeline
  Query Resolution and Template Interpolation
    · Template Syntax
    · Resolution Logic
  Vector Store Query Services
    · Service Interface
    · Configured Services
  Embedding Profiles and Similarity Search
    · Embedding Profile Specification
    · Query Parameters
  Integration with Workflow Nodes
    · Node Connection Pattern
  Query Result Formatting
    · Result Structure
    · Text Conversion
  Observability and Telemetry
    · Embedding Callback

## · GitHub Integration  (L11218)
  源文件: internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/github-action-properties-panel.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/index.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/ui/github-action-configured-view.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/event-type-display.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/icons/index.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/install-application.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/labels-input-step.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/unauthorized.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/github-trigger-properties-panel.tsx
  System Purpose and Scope
  Architecture Overview
  GitHub App Configuration
    · Installation Flow
    · Installation Data Structure
  GitHub Triggers
    · Supported Event Types
    · Trigger Configuration State Machine
    · Callsign System
    · Labels System
    · Trigger Configuration Flow
    · Configured Trigger View
  Event Processing Pipeline
    · Webhook Reception and Routing
    · Event Handler Structure
    · Act Creation and Execution
    · Progress Tracking
  GitHub Actions
    · Supported Action Types
    · Action Configuration State Machine
    · Action Configuration Flow
    · Configured Action View
    · Action Execution
  Data Model and Protocol
    · GitHub Event Data Schema
    · Node State Schema
    · Helper Functions
  Code Organization
    · UI Components Hierarchy
    · Backend Event Processing
    · Protocol Definitions
    · Key Dependencies

## · GitHub Triggers and Event Processing  (L12085)
  源文件: internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/github-action-properties-panel.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/index.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/ui/github-action-configured-view.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/event-type-display.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/icons/index.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/install-application.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/labels-input-step.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/unauthorized.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/github-trigger-properties-panel.tsx
  Purpose and Scope
  Trigger Configuration States
  GitHub Integration Authentication States
  Trigger Configuration Workflow
    · Configuration Steps
    · Event Type Selection
    · Repository Selection
    · Callsign Input
    · Labels Input
    · Trigger Storage
  Event Handler Architecture
    · Event Processing Flow
    · Event Handler Array
    · Individual Event Handlers
    · Callsign Matching
    · Label Matching
  Act Execution and Progress Tracking
    · Act Creation with Callbacks
    · Progress Table Structure
    · Status Icon Mapping
    · Comment Creation by Event Type
  Event Handler Dependencies
  Configured Trigger Display
    · GitHubTriggerConfiguredView Component
    · Reconfiguration Modes
  Event Handler Testing
  Integration with Workflow System
    · Trigger Node Output Configuration
    · Webhook Event Input

## · GitHub Actions and Integration  (L12634)
  源文件: internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/github-action-properties-panel.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/index.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/action-node-properties-panel/ui/github-action-configured-view.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/event-type-display.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/icons/index.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/install-application.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/labels-input-step.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/components/unauthorized.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/trigger-node-properties-panel/providers/github-trigger/github-trigger-properties-panel.tsx
  Purpose and Scope
  Action Node Architecture
    · Node Type and States
  Available GitHub Actions
    · Action Registry
    · Action Input Fields
  Configuration UI Flow
    · Setup State Machine
    · Step 1: Repository Selection
    · Step 2: Action Type Selection
  Configured Action View
    · Input Parameter Management
    · Parameter Binding
    · Repository Display and Reconfiguration
  Action Execution
    · Execution Flow
    · Error Handling
  GitHub App Integration
    · Authentication and Installation Flow
    · Integration States
    · OAuth and Installation Popup
  GitHub Tool Integration with Event Handlers
    · Progress Reporting
  Code Entity Map
    · Key Components and Their Locations
    · Type Definitions

## · Workflow Designer UI  (L13129)
  源文件: internal-packages/ui/components/note.tsx, internal-packages/workflow-designer-ui/src/app/globals.css, internal-packages/workflow-designer-ui/src/editor/chat/floating-chat.tsx, internal-packages/workflow-designer-ui/src/editor/chat/index.ts, internal-packages/workflow-designer-ui/src/editor/context-menu/index.tsx, internal-packages/workflow-designer-ui/src/editor/context-menu/types.ts, internal-packages/workflow-designer-ui/src/editor/hooks/use-keyboard-shortcuts.ts, internal-packages/workflow-designer-ui/src/editor/node/index.ts, internal-packages/workflow-designer-ui/src/editor/v2/components/floating-properties-panel.tsx, internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx, internal-packages/workflow-designer-ui/src/editor/v2/components/v2-footer.tsx, internal-packages/workflow-designer-ui/src/editor/v2/state.ts
  Purpose and Scope
  System Architecture
    · High-Level Component Architecture
    · Component Hierarchy and Data Flow
  Core Components
    · V2Placeholder - Root Component
    · V2Container - Main Layout
    · V2NodeCanvas - ReactFlow Integration
  State Management
    · Store Structure
    · Node State Management
  User Interactions
    · Node Connection Flow
    · Node Creation with Toolbar
    · Keyboard Shortcuts
    · Context Menu
  Floating Properties Panel
    · Panel Architecture
  Footer Panel Controls
  CSS and Styling
    · Canvas Styling
    · Custom Animations
  Integration with Core Systems
    · Giselle Engine Integration
    · ReactFlow Node and Edge Types
  Read-Only Mode
  Summary

## · Editor Architecture and State Management  (L13783)
  源文件: internal-packages/ui/components/note.tsx, internal-packages/workflow-designer-ui/src/app/globals.css, internal-packages/workflow-designer-ui/src/editor/chat/floating-chat.tsx, internal-packages/workflow-designer-ui/src/editor/chat/index.ts, internal-packages/workflow-designer-ui/src/editor/context-menu/index.tsx, internal-packages/workflow-designer-ui/src/editor/context-menu/types.ts, internal-packages/workflow-designer-ui/src/editor/hooks/use-keyboard-shortcuts.ts, internal-packages/workflow-designer-ui/src/editor/node/index.ts, internal-packages/workflow-designer-ui/src/editor/v2/components/floating-properties-panel.tsx, internal-packages/workflow-designer-ui/src/editor/v2/components/v2-container.tsx, internal-packages/workflow-designer-ui/src/editor/v2/components/v2-footer.tsx, internal-packages/workflow-designer-ui/src/editor/v2/state.ts
  Purpose and Scope
  Architecture Overview
  State Management Architecture
    · Zustand Store Structure
    · ReactFlow State Integration
    · State Synchronization
  Component Hierarchy
    · V2Placeholder
    · V2Container
    · V2NodeCanvas
  Layout State Management
  Floating Properties Panel
  Event Handling
    · Connection Management
    · Node Manipulation
    · Edge Selection
    · Canvas Interaction
    · Context Menu
  Keyboard Shortcuts System
    · Shortcut Architecture
    · Shortcut Definitions
    · useKeyAction Hook
    · Browser Shortcut Prevention
  Focus and Scope Management
  Complete Data Flow
  Styling and Visual Presentation
  Performance Optimizations
    · Memoization and Caching
    · Shallow Equality Checks
    · Throttled Resize

## · Node Rendering and Visual System  (L14683)
  源文件: apps/playground/app/globals.css, apps/playground/app/layout.tsx, apps/studio.giselles.ai/app/globals.css, apps/studio.giselles.ai/app/layout.tsx, apps/studio.giselles.ai/tailwind.config.ts, internal-packages/workflow-designer-ui/src/editor/node/node.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/vector-store/index.tsx, internal-packages/workflow-designer-ui/src/editor/tool/floating-node/component.tsx, internal-packages/workflow-designer-ui/src/editor/tool/toolbar/state.tsx, internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx, internal-packages/workflow-designer-ui/src/editor/tool/types.ts, internal-packages/workflow-designer-ui/src/icons/node/file-node.tsx
  Rendering Architecture Overview
  Rendering Component Architecture
    · ReactFlow Integration Layer
    · CustomXyFlowNode Wrapper
    · Data Flow to NodeComponent
  Node Type System
    · Node Categories
    · Type Guards and Helpers
    · Node Setup Requirements
  Handle Connection System
    · Handle Types and Positions
    · Input Handle Rendering
    · Output Handle Rendering
  Visual Styling Architecture
    · Variant Object System
    · Data Attribute System
    · CSS Variable and Gradient System
    · Border Overlay System
    · Handle Visual Coordination System
  Generation Status Display
    · Status Badge Rendering
    · Completion Label
  Node Metadata and Editing
    · Metadata Display
    · Editable Node Name
  Special Node Information Components
    · DocumentNodeInfo Component
    · GitHubNodeInfo Component
    · GitHubTriggerStatusBadge
  Node Icon System

## · Properties Panels and Node Configuration  (L15495)
  源文件: internal-packages/ui/components/prompt-editor.tsx, internal-packages/workflow-designer-ui/src/editor/index.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/app-entry-node-properties-panel/index.ts, internal-packages/workflow-designer-ui/src/editor/properties-panel/file-node-properties-panel/file-panel.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/file-node-properties-panel/index.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/generation-panel.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/index.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/prompt-panel.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/index.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/generation-panel.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/index.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/query-panel.tsx
  Properties Panel Architecture
    · Panel Component Structure
  Text Generation Node Configuration
    · Component Structure
    · Key Features
  Image Generation Node Configuration
    · Component Architecture
    · Provider-Specific Configuration
    · Key Implementation Details
  Query Node Configuration
    · Component Structure
    · Settings and Parameters
    · Query Input
    · Generation and Results
  File Node Configuration
    · Component Structure
    · File Type Configurations
    · Upload Methods
    · Validation and Error Handling
  Text Node Configuration
    · Component Structure
    · Implementation Details
  Model Selection and Eligibility System
    · Model Picker Architecture
    · Model Registry and Tier Access
    · Model Group Construction
  Model Parameter Controls
    · OpenAI Model Parameters (Text Generation)
    · Anthropic Model Parameters
    · Google Model Parameters
    · Parameter Update Flow
  Configuration Validation and Generation Execution
    · Validation and Execution Flow

## · Toolbar and Node Creation Flow  (L16201)
  源文件: apps/playground/app/globals.css, apps/playground/app/layout.tsx, apps/studio.giselles.ai/app/globals.css, apps/studio.giselles.ai/app/layout.tsx, apps/studio.giselles.ai/tailwind.config.ts, internal-packages/workflow-designer-ui/src/editor/node/node.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/vector-store/index.tsx, internal-packages/workflow-designer-ui/src/editor/tool/floating-node/component.tsx, internal-packages/workflow-designer-ui/src/editor/tool/toolbar/state.tsx, internal-packages/workflow-designer-ui/src/editor/tool/toolbar/toolbar.tsx, internal-packages/workflow-designer-ui/src/editor/tool/types.ts, internal-packages/workflow-designer-ui/src/icons/node/file-node.tsx
  Purpose and Scope
  Architecture Overview
  Tool State Machine
    · Tool State Transitions
  Toolbar Component Structure
    · Toolbar Button Configuration
  Node Creation Flow
    · Step-by-Step Flow
  Floating Node Preview System
    · Preview Component Details
  Tool Selection Popovers
    · Popover Common Structure
    · Trigger Selection Popover
    · Import (Source Category) Popover
    · Generation (Language Model) Popover
    · Action Selection Popover
    · Query (Retrieval Category) Popover
  Keyboard Shortcuts
  Integration with Canvas
  Styling and Theming
  Node Registry Integration

## · Generation Execution and Results Display  (L16750)
  源文件: internal-packages/ui/components/prompt-editor.tsx, internal-packages/workflow-designer-ui/src/editor/index.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/app-entry-node-properties-panel/index.ts, internal-packages/workflow-designer-ui/src/editor/properties-panel/file-node-properties-panel/file-panel.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/file-node-properties-panel/index.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/generation-panel.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/index.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/image-generation-node-properties-panel/prompt-panel.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/index.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/generation-panel.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/index.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/query-node-properties-panel/query-panel.tsx
  Purpose and Scope
  Generation Execution Architecture
  useNodeGenerations Hook
    · Hook Interface
    · Hook Return Values
    · Generation Context
  Execution Flow
    · Text Generation Execution
    · Execution Steps
  Results Display System
    · Generation View Component
    · Status-Based Rendering
    · Message Part Rendering
    · Image Generation Display
  Query Results Display
    · Query Result Structure
    · Data Source Tabs
    · Chunk Display
    · Pull Request Context
  Generation Panel Containers
    · Text Generation Panel
    · Panel Header Display
    · Execution Time Formatting
    · Text Content Extraction
  Expanded View System
    · Expansion Architecture
    · Overlay Implementation
    · Keyboard Navigation
    · Live Prompt Synchronization
  Spinner and Loading States
    · Text Generation Spinner
    · Image Generation Loading
  Generate CTA Button
    · Button States
  Node-Specific Implementations
    · Text Generation Node
    · Image Generation Node
    · Query Node
  Summary

## · Model Configuration Panels  (L17746)
  源文件: apps/playground/app/ui/page.tsx, apps/studio.giselles.ai/app/(auth)/components/auth-container.tsx, internal-packages/ui/components/button.tsx, internal-packages/ui/components/dialog.tsx, internal-packages/ui/components/glass-dialog.tsx, internal-packages/ui/components/prompt-editor.tsx, internal-packages/ui/style.css, internal-packages/ui/styles/semantic.css, internal-packages/workflow-designer-ui/src/editor/chat/chat-panel.tsx, internal-packages/workflow-designer-ui/src/editor/index.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/app-entry-node-properties-panel/index.ts, internal-packages/workflow-designer-ui/src/editor/properties-panel/file-node-properties-panel/file-panel.tsx
  Purpose and Scope
  Architecture Overview
  Model Picker Component
    · Model Groups Structure
  OpenAI Model Panel
    · Configuration Flow
    · Parameter Controls by Model Type
    · Web Search Tool Integration
  Anthropic Model Panel
  Google Model Panel
    · Mutually Exclusive Features
    · Output Management
  Image Generation Model Panels
    · Fal Model Panel
    · OpenAI Image Model Panel
  Shared Model Control Components
    · Control Component Interface
    · Update Pattern
  Tool Configuration Dialogs
    · Anthropic Web Search Configuration
  Integration with Properties Panels
    · Text Generation Integration
  State Management and Data Flow
    · Update Functions
  Model Defaults and Initialization
    · Default Model Data Creation
    · Model Switching

## · Applications and User Interfaces  (L18406)
  源文件: apps/playground/package.json, apps/studio.giselles.ai/package.json, internal-packages/workflow-designer-ui/package.json, package.json, packages/giselle/package.json, pnpm-lock.yaml, pnpm-workspace.yaml
  Overview
  Application Architecture
  Studio Application
    · Application Structure
    · Technology Stack
    · Key Dependencies
  Workspace Context and Feature Flags
    · WorkspaceProvider Architecture
    · Feature Flag System
    · Context Data Flow
  Stage System and Act Execution
    · Stage Interface Architecture
    · Application Selection and Filtering
    · Dynamic Form Generation
    · Act Execution Lifecycle
    · Act Detail Page Structure
    · Database Schema for Stage System
  Vector Store Management Interface
    · Vector Store Settings UI Structure
    · GitHub Repository Integration
    · Document Upload and Processing
    · Vector Store Database Schema
    · Quota Management
    · Content Type Configuration
  Playground Application
    · Key Differences from Studio
    · Playground Architecture
    · Simplified Configuration
    · Development Workflow
    · Use Cases
  Routing and Navigation
    · Studio Application Routes
    · Route Protection and Middleware
  Build and Development Scripts
    · Studio Application Scripts
    · Playground Application Scripts
    · Environment Variables

## · Studio Application  (L19542)
  源文件: apps/playground/package.json, apps/studio.giselles.ai/flags.ts, apps/studio.giselles.ai/package.json, internal-packages/workflow-designer-ui/package.json, package.json, packages/giselle/package.json, packages/giselle/src/react/feature-flags/context.ts, packages/giselle/src/react/workspace/provider.tsx, pnpm-lock.yaml, pnpm-workspace.yaml
  Application Architecture
  Workspace Layout and Initialization
    · Initialization Steps
  Context Provider Hierarchy
    · Context Providers
    · Context Consumption Example
  Feature Flag System
    · Feature Flag Definitions
    · Flag Evaluation Logic
    · Flag Consumption in Components
  Data Fetching Pipeline
    · Data Fetching Sequence
  Integration Points
    · Flow Trigger Callbacks
  Comparison with Playground Application

## · Workspace Context and Feature Flags  (L20107)
  源文件: apps/studio.giselles.ai/flags.ts, packages/giselle/src/react/feature-flags/context.ts, packages/giselle/src/react/workspace/provider.tsx
  Purpose and Scope
  WorkspaceProvider Architecture
    · Context Hierarchy
    · Provider Props and Configuration
  Feature Flag System
    · Flag Definition Structure
    · Two-Tier Resolution Strategy
    · takeLocalEnv Helper Function
    · Available Feature Flags
    · Flag Resolution Examples
  Feature Flag Context
    · FeatureFlagContext Definition
    · Context Initialization
  Server-Side Flag Loading
    · Data Loading Pattern
    · Feature Flag Evaluation
  Configuration Cascading Flow
    · Complete Data Flow
    · Deprecated Layout Example
  Application-Specific Configuration
    · Playground Configuration
    · Studio vs Playground Differences
  Context Access Patterns
    · Nested Context Dependencies

## · Stage System and Act Execution  (L20604)
  源文件: apps/playground/.gitignore, apps/studio.giselles.ai/app/(main)/workspaces/actions.ts, apps/studio.giselles.ai/app/api/workspaces/route.ts, apps/studio.giselles.ai/app/stage/(top)/actions.ts, apps/studio.giselles.ai/app/stage/(top)/circular-carousel.module.css, apps/studio.giselles.ai/app/stage/(top)/circular-carousel.tsx, apps/studio.giselles.ai/app/stage/(top)/form-input-renderer.tsx, apps/studio.giselles.ai/app/stage/(top)/form.tsx, apps/studio.giselles.ai/app/stage/(top)/helpers.ts, apps/studio.giselles.ai/app/stage/(top)/page.tsx, apps/studio.giselles.ai/app/stage/(top)/resizable-layout.tsx, apps/studio.giselles.ai/app/stage/(top)/services.ts
  Purpose and Scope
  System Architecture
  Flow Trigger System
    · FlowTrigger Data Structure
    · Trigger Configuration Types
  Form Container and Input Rendering
    · Form State Management
    · Dynamic Input Generation
    · Input Rendering Component
    · Form Validation and Parsing
  App Selection UI
    · Circular Carousel View
    · List View
  Act Creation and Execution
    · Act Creation Flow with Code Entities
    · Server Action Implementation Details
    · Database Schema Integration
    · Act Lifecycle in Stage System
  Task List and Management
    · FilterableActsList Component
    · Search Query Parsing
    · Act Enrichment Process
    · Task Table Display
    · Empty States
  ResizableLayout Pattern
    · Layout Implementation
  Extended Duration Configuration

## · Vector Store Management Interface  (L21269)
  源文件: apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/actions.ts, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/configure-sources-dialog.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/data.ts, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/diagnostic-modal.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-embedding-profiles.ts, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-store-create-dialog.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document-vector-store-list.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/document-vector-store-item.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/document/page.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/layout.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/navigation-layout.tsx, apps/studio.giselles.ai/app/(main)/settings/team/vector-stores/page.tsx
  Architecture Overview
  GitHub Repository Vector Store Interface
    · Main Page Component
    · Repository Item Display
    · Repository Registration Dialog
    · Configure Sources Dialog
    · Diagnostic Modal
  Document Vector Store Interface
    · Document Vector Store Item
    · Document Vector Store Creation Dialog
  Server Actions
    · GitHub Repository Actions
    · Document Vector Store Actions
  Embedding Profile Configuration
    · GitHub Embedding Profiles
    · Document Embedding Profiles
  Navigation Layout
  Data Fetching
    · GitHub Repository Indexes Query
    · Installations and Repositories Query
    · Document Vector Stores Query
  Error Handling
    · Document Loader Error Codes
    · Action Result Type
  UI Component Library Usage

## · Playground Application  (L22411)
  源文件: apps/playground/package.json, apps/studio.giselles.ai/package.json, internal-packages/workflow-designer-ui/package.json, package.json, packages/giselle/package.json, pnpm-lock.yaml, pnpm-workspace.yaml
  Purpose and Scope
  Application Structure
    · Next.js Application Configuration
    · Available Scripts
  Package Dependencies
    · Dependency Footprint
    · Core Dependencies
  Comparison with Studio
    · Dependency Differences
    · Configuration Simplification
  Development Workflow
    · Running the Playground
    · Development Use Cases
  Architecture Integration
    · Relationship to Workflow Designer UI
    · Engine Configuration
  Build and Deployment
    · Build Process
    · Type Generation
  Purpose-Built Constraints
    · What Playground Excludes
  Entry Point Reference

## · Infrastructure and Cross-Cutting Concerns  (L22816)
  源文件: apps/playground/package.json, apps/studio.giselles.ai/package.json, internal-packages/workflow-designer-ui/package.json, package.json, packages/giselle/package.json, pnpm-lock.yaml, pnpm-workspace.yaml
  Build System Architecture
    · Package Management
    · Build Scripts
  Continuous Integration Pipeline
    · CI Workflow Architecture
    · Color Validation System
  Release Management
    · Changeset Configuration
    · Release Workflow
  Deployment Pipelines
    · Trigger.dev Deployment
    · Vercel Deployment
  End-to-End Testing
    · E2E Workflow Configuration
    · Test Execution Environment
  License Compliance
    · License Finder Integration
  Development Environment Configuration
    · Zed Tasks Configuration
  Semantic Token Migration Strategy
    · Current State
    · Migration Goals
  Summary

## · Feature Flag System  (L23346)
  源文件: apps/studio.giselles.ai/flags.ts, packages/giselle/src/react/feature-flags/context.ts, packages/giselle/src/react/workspace/provider.tsx
  Purpose and Scope
  Architecture Overview
  Flag Definition System
    · Flag Definition Pattern
    · Example Flag Definition
  Environment-Aware Decision Logic
    · Local Development Helper
    · Development Environment Variables
    · Production Vercel Edge Config
  Flag Distribution Pattern
    · Server-Side Evaluation
    · Context Provider Initialization
    · WorkspaceProvider Implementation
  Flag Consumption in UI Components
    · Hook Interface
    · Conditional Rendering Pattern
    · Conditional Feature Availability
  Available Feature Flags
    · Flag Definitions by Category
  Development vs Production Configuration
    · Playground Static Configuration
    · Development Configuration Example
    · Production Edge Config Example
  Flag Lifecycle and Dependencies
    · Adding a New Feature Flag

## · UI Component Library and Theming  (L24012)
  源文件: apps/playground/app/ui/page.tsx, apps/studio.giselles.ai/app/(auth)/components/auth-container.tsx, internal-packages/ui/components/button.tsx, internal-packages/ui/components/dialog.tsx, internal-packages/ui/components/glass-dialog.tsx, internal-packages/ui/style.css, internal-packages/ui/styles/semantic.css, internal-packages/workflow-designer-ui/src/editor/chat/chat-panel.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model/anthropic.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model/google.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/model/openai.tsx, internal-packages/workflow-designer-ui/src/editor/properties-panel/text-generation-node-properties-panel/tab-content.tsx
  Package Structure
  Theme System Architecture
    · CSS Variable Organization
    · Theme Variable Hierarchy
  Component Variants
    · Variant System
    · Glass Variant Implementation
    · Solid Variant Implementation
    · Outline Variant Implementation
  Key Components
    · Button Component
    · Dialog Component
    · GlassSurfaceLayers Component
  Usage Patterns
    · Button Usage Examples
    · Dialog Usage Examples
  Context-Specific Styling
    · Auth Page Theming
    · Stage System Theming
    · Editor Theming
    · Chat Panel Theming
  Color System and Accessibility
    · Text Hierarchy
    · Status Colors with RGB Variants
  Base Layer Normalization
  Integration with Tailwind CSS

## · Observability and Telemetry  (L24603)
  源文件: apps/playground/giselle-engine.ts, apps/playground/package.json, apps/studio.giselles.ai/app/giselle-engine.ts, apps/studio.giselles.ai/package.json, internal-packages/workflow-designer-ui/package.json, package.json, packages/giselle/package.json, packages/giselle/src/engine/acts/run-act.ts, packages/giselle/src/engine/generations/generate-content.ts, packages/giselle/src/engine/generations/generate-image.ts, packages/giselle/src/engine/generations/internal/use-generation-executor.ts, packages/giselle/src/engine/generations/types.ts
  Overview
  Callback System Architecture
    · Callback Registration and Types
    · Callback Execution Flow
  Langfuse Integration
    · Generation Tracing
    · Embedding Tracing
  Metadata Enrichment Pipeline
    · Team and Plan Context
    · Request ID Tracking
  Telemetry Configuration
    · Engine Configuration
  Execution Context Handling
    · Origin-Based Context Resolution
    · Conditional Tracing in Studio Context
  Trigger.dev Task Telemetry
    · Task-Based Tracing
  Callback Implementation Details
    · Generation Complete Callback Structure
    · Embedding Complete Callback Structure
  Batch Writing for Streaming Data
  Error Tracking Integration
    · Generation Failure Handling
  Telemetry Flush Coordination
  Summary of Telemetry Data Flow

## · Build and Deployment  (L25308)
  源文件: apps/playground/package.json, apps/studio.giselles.ai/package.json, docs/packages-license.md, internal-packages/workflow-designer-ui/package.json, package.json, packages/document-preprocessor/README.md, packages/document-preprocessor/package.json, packages/document-preprocessor/src/global.d.ts, packages/document-preprocessor/src/index.ts, packages/document-preprocessor/src/pdf.ts, packages/document-preprocessor/src/text.test.ts, packages/document-preprocessor/src/text.ts
  Build System Architecture
  Development Workflow and Quality Checks
  CI/CD Pipeline Architecture
  Release and Versioning Process
    · Changeset Configuration
  License Compliance System
    · License Analysis Pipeline
  Testing and Quality Assurance
    · Testing Architecture
  Build Performance and Optimization
    · Caching and Performance Strategy
    · Build Target Optimization