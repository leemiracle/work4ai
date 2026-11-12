# Skeleton: agentset（41 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 13KB | 2 | ~16 | 16 |
| 2 | Architecture Overview | L329 | 12KB | 5 | ~4 | 17 |
| 3 | Monorepo Structure | L673 | 9KB | 3 | ~6 | 14 |
| 4 | Technology Stack | L933 | 9KB | 3 | ~3 | 26 |
| 5 | Data Layer | L1123 | 7KB | 2 | ~2 | 17 |
| 6 | Database Schema | L1282 | 13KB | 2 | ~2 | 19 |
| 7 | Database Client Configuration | L1637 | 7KB | 3 | ~3 | 9 |
| 8 | Vector Store System | L1828 | 11KB | 4 | ~3 | 15 |
| 9 | Document Processing | L2081 | 18KB | 3 | ~7 | 12 |
| 10 | Ingestion Workflow | L2457 | 14KB | 3 | ~5 | 13 |
| 11 | Background Job Processing | L2766 | 15KB | 3 | ~6 | 23 |
| 12 | Ingestion Validation and Configuration | L3136 | 12KB | 3 | ~5 | 24 |
| 13 | RAG and Search System | L3384 | 11KB | 3 | ~5 | 18 |
| 14 | Vector Search | L3625 | 11KB | 4 | ~2 | 15 |
| 15 | Agentic Pipeline | L3925 | 12KB | 3 | ~5 | 16 |
| 16 | Chat and Search API Endpoints | L4204 | 12KB | 2 | ~7 | 21 |
| 17 | Hosting System | L4506 | 10KB | 2 | ~0 | 1 |
| 18 | Hosting Configuration | L4655 | 9KB | 2 | ~5 | 10 |
| 19 | Hosting UI Components | L4811 | 15KB | 2 | ~5 | 0 |
| 20 | Domain Management | L5057 | 9KB | 3 | ~4 | 18 |
| 21 | Frontend Architecture | L5272 | 8KB | 1 | ~3 | 10 |
| 22 | Document Management UI | L5419 | 14KB | 3 | ~2 | 0 |
| 23 | Ingestion Modal System | L5634 | 10KB | 3 | ~4 | 12 |
| 24 | Namespace and Demo System | L5852 | 11KB | 3 | ~1 | 21 |
| 25 | Chat UI Components | L6062 | 10KB | 2 | ~2 | 23 |
| 26 | Authentication and Billing | L6236 | 11KB | 2 | ~8 | 14 |
| 27 | Authentication System | L6455 | 9KB | 2 | ~4 | 12 |
| 28 | Billing and Subscriptions | L6673 | 13KB | 2 | ~2 | 13 |
| 29 | Authorization and Resource Limits | L6899 | 8KB | 2 | ~2 | 11 |
| 30 | API Architecture | L7067 | 8KB | 1 | ~5 | 7 |
| 31 | tRPC Routers | L7230 | 10KB | 3 | ~3 | 11 |
| 32 | Internal API Routes | L7439 | 15KB | 9 | ~4 | 1 |
| 33 | Public API and OpenAPI | L7793 | 9KB | 2 | ~7 | 16 |
| 34 | Infrastructure and Configuration | L7993 | 8KB | 3 | ~1 | 12 |
| 35 | Environment Configuration | L8188 | 7KB | 2 | ~5 | 12 |
| 36 | Job Orchestration with Trigger.dev | L8360 | 12KB | 3 | ~1 | 15 |
| 37 | External Service Integration | L8634 | 7KB | 2 | ~2 | 12 |
| 38 | Analytics and Events | L8824 | 7KB | 1 | ~1 | 21 |
| 39 | PostHog Event Tracking | L8976 | 8KB | 2 | ~3 | 23 |
| 40 | Webhook System | L9152 | 9KB | 2 | ~2 | 22 |
| 41 | Glossary | L9346 | 11KB | 2 | ~2 | 31 |


## · Overview  (L6)
  源文件: .github/ISSUE_TEMPLATE/bug_report.md, .github/ISSUE_TEMPLATE/feature_request.md, .github/assets/.gitkeep, .github/assets/readme-cover.png, .github/assets/screenshot.png, .github/assets/star-us.png, LICENSE.md, README.md, apps/web/next.config.ts, apps/web/package.json, bun.lock, package.json
  What is AgentSet
  Core Capabilities
  System Architecture
  Package Architecture and Dependencies
  Technology Stack
    · Frontend Stack
    · Backend Stack
    · AI/ML Stack
  Development Workflow
    · Environment Configuration
  Multi-Tenancy Model
  Key Entry Points
    · Web Application Routes
    · Background Job Tasks
    · Core Service Packages

## · Architecture Overview  (L329)
  源文件: .cursor/rules/project-structure.mdc, .github/ISSUE_TEMPLATE/bug_report.md, .github/ISSUE_TEMPLATE/feature_request.md, .github/assets/.gitkeep, .github/assets/readme-cover.png, .github/assets/screenshot.png, .github/assets/star-us.png, LICENSE.md, README.md, apps/web/next.config.ts, apps/web/package.json, bun.lock
  Purpose and Scope
  System Architecture
    · Three-Layer Architecture
  Frontend Layer
    · apps/web - Next.js Application
    · packages/ui - Shared Components
  Backend Services Layer
    · packages/jobs - Background Job Processing
    · packages/engine - AI/ML Processing
  Core Infrastructure Layer
    · packages/db - Database Client
    · packages/storage - S3 Integration
  Multi-Tenancy Model
    · Isolation Boundaries
  Component Interaction Patterns
    · Request Flow: Web App → tRPC → Database
    · Request Flow: Document Ingestion
  Package Dependency Graph
    · Build Orchestration

## · Monorepo Structure  (L673)
  源文件: .cursor/mcp.json, .cursor/rules/animations.mdc, .cursor/rules/project-structure.mdc, .cursor/rules/shadcn.mdc, .cursor/rules/tailwind.mdc, apps/web/next.config.ts, apps/web/package.json, apps/web/src/app/robots.ts, bun.lock, package.json, packages/db/package.json, packages/jobs/package.json
  Purpose and Scope
  Workspace Organization
    · Directory Structure
    · Package Types
  Package Dependencies
    · Dependency Graph (Code Entity Space)
    · Workspace Management
  Catalog-Based Dependency Management
    · Standard Catalog
    · React19 Catalog
  Build Orchestration with Turborepo
    · Task Execution Flow
    · Environment Handling
  Key Package Implementation Details
    · `@agentset/ui` (Shared Components)
    · `@agentset/db` (Data Layer)
    · `@agentset/jobs` (Background Processing)

## · Technology Stack  (L933)
  源文件: .env.example, apps/web/next.config.ts, apps/web/package.json, apps/web/src/app/api/(internal-api)/chat/route.ts, apps/web/src/app/api/(internal-api)/hosting-chat/route.ts, apps/web/src/app/api/(internal-api)/hosting-search/route.ts, apps/web/src/env.ts, apps/web/src/instrumentation-client.ts, apps/web/src/lib/agentic/index.ts, apps/web/src/lib/agentic/search.ts, apps/web/src/server/api/routers/search.ts, bun.lock
  Core Framework Stack
    · Frontend & API Interaction
  AI and Machine Learning Stack
    · LLM Providers
    · RAG and Search Components
  Data Layer
    · Relational Database
    · Vector Stores
    · Caching and Rate Limiting
  Job Orchestration
  Infrastructure and Tooling
    · Monorepo Management
    · External Services

## · Data Layer  (L1123)
  源文件: apps/web/scripts/populate-document-namespace-id.ts, packages/db/.gitignore, packages/db/prisma/migrations/20250413055012_add_limits_and_plans/migration.sql, packages/db/prisma/migrations/20250413055328_make_org_slug_required/migration.sql, packages/db/prisma/migrations/20251202045758_update_auth_schema/migration.sql, packages/db/prisma/migrations/20260118061102_webhooks/migration.sql, packages/db/prisma/migrations/20260118131244_add_webhook_enabled/migration.sql, packages/db/prisma/migrations/20260208232321_add_member_user_id_idx/migration.sql, packages/db/prisma/schema/auth.prisma, packages/db/prisma/schema/namespace.prisma, packages/db/prisma/schema/organization.prisma, packages/db/prisma/schema/schema.prisma
  Purpose and Scope
  Data Architecture Overview
    · System Data Flow
  PostgreSQL and Prisma Integration
    · Core Entity Hierarchy
    · Database Client and Lifecycle
  Vector and Keyword Stores
  Auxiliary Storage Layers
    · Redis Caching
    · S3 File Storage

## · Database Schema  (L1282)
  源文件: apps/web/scripts/populate-document-namespace-id.ts, packages/db/.gitignore, packages/db/prisma/migrations/20250413055012_add_limits_and_plans/migration.sql, packages/db/prisma/migrations/20250413055328_make_org_slug_required/migration.sql, packages/db/prisma/migrations/20251202045758_update_auth_schema/migration.sql, packages/db/prisma/migrations/20260118061102_webhooks/migration.sql, packages/db/prisma/migrations/20260118131244_add_webhook_enabled/migration.sql, packages/db/prisma/migrations/20260208232321_add_member_user_id_idx/migration.sql, packages/db/prisma/schema/auth.prisma, packages/db/prisma/schema/document.prisma, packages/db/prisma/schema/ingest-job.prisma, packages/db/prisma/schema/namespace.prisma
  Purpose and Scope
  Overview
    · Core Characteristics
  Entity Relationship Diagram
  Tenant Hierarchy and Multi-Tenancy
    · Hierarchy Structure
  Ingestion Models
    · Document Model
    · IngestJob Model
  Organization and Membership
    · Organization Model
    · Member Model
  Namespace and Hosting
    · Namespace Model
    · Hosting and Domain
  Database Client Configuration
  Indexes and Query Optimization

## · Database Client Configuration  (L1637)
  源文件: apps/web/scripts/populate-document-namespace-id.ts, packages/db/.gitignore, packages/db/eslint.config.js, packages/db/prisma/schema/schema.prisma, packages/db/src/client.ts, packages/db/src/index.ts, packages/db/tsconfig.json, packages/jobs/src/db.ts, packages/jobs/trigger.config.ts
  Purpose and Scope
  Client Creation and Initialization
    · Connection Pooling and Adapter Setup
    · Logging Configuration
  Global Singleton Pattern
  Trigger.dev Integration
    · Task Middleware and Locals
    · Lifecycle Hooks
    · Build Configuration
  Data Flow and Exports

## · Vector Store System  (L1828)
  源文件: apps/web/src/server/api/routers/search.ts, apps/web/src/services/namespaces/validate.ts, packages/db/src/types/prisma.ts, packages/engine/src/embedding/index.ts, packages/engine/src/llm/index.ts, packages/engine/src/rerank/cohere.ts, packages/engine/src/rerank/common.ts, packages/engine/src/rerank/index.ts, packages/engine/src/vector-store/common/vector-store.ts, packages/engine/src/vector-store/index.ts, packages/engine/src/vector-store/pinecone/index.ts, packages/engine/src/vector-store/query.ts
  Purpose and Scope
  Architecture Overview
    · Natural Language Space to Code Entity Space
  Factory Pattern and Configuration
    · Namespace and Tenant Isolation
  Vector Store Interface
    · Core Methods
    · Query Options
  Implementation Details
    · Pinecone Implementation
    · Turbopuffer Implementation
  Query Helper and Reranking
    · Code Entity Integration
    · Validation and Dimensions

## · Document Processing  (L2081)
  源文件: apps/web/src/server/api/routers/ingest-jobs.ts, apps/web/src/services/documents/delete.ts, apps/web/src/services/ingest-jobs/create.ts, apps/web/src/services/ingest-jobs/delete.ts, packages/jobs/src/schema.ts, packages/jobs/src/tasks/delete-document.ts, packages/jobs/src/tasks/delete-ingest-job.ts, packages/jobs/src/tasks/delete-namespace.ts, packages/jobs/src/tasks/delete-org.ts, packages/jobs/src/tasks/ingest.ts, packages/jobs/src/tasks/process-document.ts, packages/jobs/src/tasks/re-ingest.ts
  System Purpose and Scope
  Document Types and Input Sources
  Two-Tier Job Architecture
  Document Lifecycle and Status Transitions
    · Status Descriptions
  Partition API Integration
    · Async Processing Flow
  Embedding Generation and Vector Storage
    · Batch Processing Strategy
    · Rate Limiting for Pinecone
  Document Re-ingestion
  Deletion and Cleanup Workflows
    · Document Deletion
    · IngestJob Deletion
  Usage Metering and Billing
    · Metric Tracking
  Configuration and Validation
  Error Handling and Recovery

## · Ingestion Workflow  (L2457)
  源文件: apps/web/src/lib/redis.ts, apps/web/src/server/api/routers/ingest-jobs.ts, apps/web/src/services/documents/delete.ts, apps/web/src/services/ingest-jobs/create.ts, apps/web/src/services/ingest-jobs/delete.ts, packages/jobs/src/schema.ts, packages/jobs/src/tasks/delete-document.ts, packages/jobs/src/tasks/delete-ingest-job.ts, packages/jobs/src/tasks/delete-namespace.ts, packages/jobs/src/tasks/delete-org.ts, packages/jobs/src/tasks/ingest.ts, packages/jobs/src/tasks/process-document.ts
  Purpose and Scope
  Overview
  Ingestion Flow Diagram
  Job Creation
    · Validation and Preprocessing
    · Database Transaction
    · Trigger.dev Job Invocation
  Document Type Handling
    · Document Type Processing Flow
    · CRAWL and YOUTUBE Processing
    · Single Document and BATCH Types
  Two-Tier Job Architecture
    · Architecture Overview
    · Batch Spawning Pattern
  Document Processing Task
    · Processing Flow
    · Embedding and Vector Storage
    · Cleanup and Re-processing
  Webhook Emissions
  Re-ingestion and Deletion
    · Re-ingestion Flow
    · Deletion Flow

## · Background Job Processing  (L2766)
  源文件: apps/web/src/app/api/(internal-api)/stripe/webhook/invoice-payment-succeeded.ts, apps/web/src/app/api/(internal-api)/stripe/webhook/route.ts, apps/web/src/lib/webhook/emit.ts, packages/jobs/src/cron/usage.ts, packages/jobs/src/schema.ts, packages/jobs/src/tasks/delete-document.ts, packages/jobs/src/tasks/delete-ingest-job.ts, packages/jobs/src/tasks/delete-namespace.ts, packages/jobs/src/tasks/delete-org.ts, packages/jobs/src/tasks/ingest.ts, packages/jobs/src/tasks/meter-org-documents.ts, packages/jobs/src/tasks/process-document.ts
  Purpose and Scope
  Trigger.dev Integration
    · Configuration
    · Task Definition Pattern
  Task Architecture
    · Task Registry
    · Task Hierarchy and Orchestration
    · Priority Queueing
  Document Processing Pipeline
    · IngestJob Task
    · ProcessDocument Task
    · Batch Processing Strategy
  Webhook Integration
    · Event Emission
    · Webhook Delivery and Retries
  Deletion Workflows
    · Hierarchical Cascade
    · Rate Limiting for Vector Stores
  Re-ingestion Workflow
  Usage Metering
    · Real-time Metering
    · Bulk Metering

## · Ingestion Validation and Configuration  (L3136)
  源文件: apps/web/src/app/openapi.json/route.ts, apps/web/src/lib/code-examples/ingest.ts, apps/web/src/openapi/index.ts, apps/web/src/openapi/v1/ingest-jobs/create-job.ts, apps/web/src/openapi/v1/ingest-jobs/reingest-job.ts, apps/web/src/schemas/api/document.ts, apps/web/src/schemas/api/ingest-job.ts, apps/web/src/server/api/routers/documents.ts, internal-docs/analytics-events.md, packages/db/src/schemas.ts, packages/emails/src/env.ts, packages/engine/src/index.ts
  Purpose and Scope
  Validation Architecture
    · Schema Types and Hierarchy
    · Discriminated Union Pattern
  Configuration Schema
    · Supported Ingestion Options
    · Deprecated Parameters
  Partition Configuration Utility
    · Data Flow: Config to Partition Body
  API and UI Integration
    · Document and Job Actions
    · Frontend Validation
  Analytics and Event Tracking

## · RAG and Search System  (L3384)
  源文件: .env.example, apps/web/src/app/api/(internal-api)/chat/route.ts, apps/web/src/app/api/(internal-api)/hosting-chat/route.ts, apps/web/src/app/api/(internal-api)/hosting-search/route.ts, apps/web/src/env.ts, apps/web/src/instrumentation-client.ts, apps/web/src/lib/agentic/index.ts, apps/web/src/lib/agentic/search.ts, apps/web/src/server/api/routers/search.ts, packages/engine/package.json, packages/engine/src/env.ts, packages/engine/src/vector-store/common/vector-store.ts
  Purpose and Scope
  System Architecture Overview
  Query Vector Store
  Agentic Search Pipeline
  Chat and Search API Endpoints

## · Vector Search  (L3625)
  源文件: apps/web/src/server/api/routers/search.ts, apps/web/src/services/namespaces/validate.ts, packages/db/src/types/prisma.ts, packages/engine/src/embedding/index.ts, packages/engine/src/llm/index.ts, packages/engine/src/rerank/cohere.ts, packages/engine/src/rerank/common.ts, packages/engine/src/rerank/index.ts, packages/engine/src/vector-store/common/vector-store.ts, packages/engine/src/vector-store/index.ts, packages/engine/src/vector-store/pinecone/index.ts, packages/engine/src/vector-store/query.ts
  Purpose and Scope
  Vector Store Abstraction Layer
    · Class Architecture
    · Core Interfaces
  Query Modes
    · Semantic Search
    · Keyword Search (BM25)
    · Hybrid Search with Reciprocal Rank Fusion (RRF)
  Pinecone Implementation
    · Configuration and Multi-tenancy
  Turbopuffer Implementation
    · Schema Configuration
    · Namespace Naming
  Query Flow and Reranking
    · Reranking Integration
  Validation and Consistency
    · Dimension Validation
    · Consistency Levels

## · Agentic Pipeline  (L3925)
  源文件: .env.example, apps/web/src/app/api/(internal-api)/chat/route.ts, apps/web/src/app/api/(internal-api)/chat/schema.ts, apps/web/src/app/api/(internal-api)/hosting-chat/route.ts, apps/web/src/app/api/(internal-api)/hosting-search/route.ts, apps/web/src/env.ts, apps/web/src/instrumentation-client.ts, apps/web/src/lib/agentic/index.ts, apps/web/src/lib/agentic/prompts.ts, apps/web/src/lib/agentic/search.ts, apps/web/src/lib/agentic/utils.ts, packages/engine/package.json
  Purpose and Scope
  System Overview
    · Diagram: Agentic Pipeline System Context
  Pipeline Workflow
    · Diagram: Agentic Pipeline Execution Flow
  Implementation Details
    · Core Functions and Types
    · Iterative Search Process (agenticSearch)
  Deep Research Pipeline
  Status Annotations and UI Integration
  Error Handling and Resilience
    · Stream Error Handler
    · Token Budget Exhaustion
  Performance Considerations

## · Chat and Search API Endpoints  (L4204)
  源文件: .env.example, apps/web/src/app/api/(internal-api)/chat/route.ts, apps/web/src/app/api/(internal-api)/hosting-chat/route.ts, apps/web/src/app/api/(internal-api)/hosting-search/route.ts, apps/web/src/components/chat/chat-input-modes.tsx, apps/web/src/components/chat/chat-model.tsx, apps/web/src/components/chat/chat-settings.store.ts, apps/web/src/components/chat/message-editor.tsx, apps/web/src/components/chat/use-chat.ts, apps/web/src/components/chat/use-hosting-chat.ts, apps/web/src/components/llm-selector.tsx, apps/web/src/components/reranker-selector.tsx
  Purpose and Scope
  Overview
    · Chat and Search Endpoints Architecture
  Internal Chat Endpoint
    · Endpoint Configuration
    · Request Parameters
    · Processing Modes
  Hosting Chat and Search
    · Hosting Chat API (`/api/hosting-chat`)
    · Hosting Search API (`/api/hosting-search`)
  Public Search Endpoint
    · Features
  Usage Tracking and Billing
    · Tracking Implementation
  Data Flow: Client to Vector Store
  Frontend Configuration

## · Hosting System  (L4506)
  源文件: apps/web/src/components/list-input.tsx
  Purpose and Scope
  System Architecture
    · Hosting System Components
  Lifecycle and State Management
    · Enabling Hosting
    · Configuration and Preview
    · Unsaved Changes Protection
  Key Feature Areas
    · Branding and UI
    · AI Behavior and Security
    · Domain and Connectivity
  Data Integration Flow
  Deployment Status

## · Hosting Configuration  (L4655)
  源文件: apps/web/src/components/list-input.tsx, apps/web/src/components/search-chunk.tsx, apps/web/src/components/sortable-list.tsx, apps/web/src/schemas/api/hosting.ts, apps/web/src/server/api/routers/hosting.ts, apps/web/src/server/api/trpc.ts, apps/web/src/services/hosting/delete.ts, apps/web/src/services/hosting/enable.ts, apps/web/src/services/hosting/get.ts, apps/web/src/services/hosting/update.ts
  Overview
  Configuration Data Model
    · Schema Fields
  AI and Retrieval Configuration
    · LLM and System Prompt
    · Retrieval and Reranking
    · Citation Path
  Implementation Details
    · Form Management
    · Image Uploads
    · API Access
  Components Summary

## · Hosting UI Components  (L4811)
  Purpose and Scope
  Architecture Overview
    · System Architecture Diagram
  Component Hierarchy and Data Flow
  Form State Management
  Unsaved Changes Protection
  Split-Pane Layout Architecture
    · Desktop Layout Structure
  Preview System
  Deployment Status Bar
  Configuration Tab System
  Custom Domain UI
    · Domain Status and DNS Records
  Shared UI Utilities
    · Sortable List
    · Search Chunk Preview

## · Domain Management  (L5057)
  源文件: apps/web/src/app/api/(internal-api)/middleware/default-org/route.ts, apps/web/src/app/api/(internal-api)/middleware/hosting/member/route.ts, apps/web/src/app/api/(internal-api)/middleware/hosting/route.ts, apps/web/src/app/hosting-not-found/page.tsx, apps/web/src/components/list-input.tsx, apps/web/src/components/search-chunk.tsx, apps/web/src/components/sortable-list.tsx, apps/web/src/lib/api/hosting-auth.ts, apps/web/src/lib/api/session.ts, apps/web/src/lib/domains/remove-domain.ts, apps/web/src/lib/domains/utils.ts, apps/web/src/lib/internal-api.ts
  Overview
    · Domain Configuration Data Flow
  Domain Validation and Utilities
    · Key Validation Functions
  Hosting and Domain Relationship
    · Namespace Access Verification
  Routing and Middleware
    · Hosting Middleware Logic
    · Internal API Security
  Verification and DNS Setup
    · DNS Record Requirements
  User Interface Flow
    · Implementation Components
    · Domain Enablement Sequence
  Access Control for Hosted Domains
    · Authorization Logic (`hostingAuth`)

## · Frontend Architecture  (L5272)
  源文件: apps/web/src/components/app-sidebar/index.tsx, apps/web/src/components/app-sidebar/links.ts, apps/web/src/components/app-sidebar/nav-items.tsx, apps/web/src/components/chat/message-status.tsx, apps/web/src/styles/globals.css, packages/ui/src/components/ai-elements/chain-of-thought.tsx, packages/ui/src/components/ai-elements/prompt-input.tsx, packages/ui/src/components/ai-elements/shimmer.tsx, packages/ui/src/components/ai-elements/snippet.tsx, packages/ui/src/components/ui/skeleton.tsx
  Overview
  Application Navigation and Layout
    · Sidebar and Routing
    · Styling System
  State Management
    · Playground Search and Explorer
  Shared AI Components
    · Chain of Thought (CoT)
    · Message Status
    · Prompt Input
  Child Pages

## · Document Management UI  (L5419)
  Purpose and Scope
    · Component Hierarchy
    · Core Components
  State and Data Flow
    · Data Fetching Hooks
    · Pagination and Filtering
  Jobs Management
    · Jobs Table Columns
    · Job Actions
  Document Management
    · Document Columns
    · Document Actions
  API Ingestion Modal
    · Implementation Detail
  Configuration Management
    · Configuration Merging Logic
    · Validation Schema

## · Ingestion Modal System  (L5634)
  源文件: apps/web/scripts/migrate-azure-config.ts, apps/web/src/components/create-namespace/models.ts, apps/web/src/hooks/use-upload.ts, apps/web/src/lib/api/tenant.ts, apps/web/src/lib/file-types.ts, apps/web/src/openapi/v1/utils.ts, apps/web/src/schemas/api/upload.ts, apps/web/src/schemas/chat.ts, apps/web/src/server/api/routers/uploads.ts, apps/web/src/services/uploads.ts, packages/ui/src/icons/turbopuffer.tsx, packages/validation/src/vector-store/index.ts
  Modal Architecture
    · Component Hierarchy
    · IngestModal Component
  Form Types and Validation
    · Form Pattern Mapping
    · TextForm
    · FilesForm
    · CrawlForm
    · YoutubeForm
  IngestConfig and Shared Components
    · Shared Logic: extractConfig
    · Configuration Options
    · DynamicArrayField
  File Upload Handling
    · Upload Data Flow
    · Technical Implementation

## · Namespace and Demo System  (L5852)
  源文件: apps/web/src/components/chat/chat-input.tsx, apps/web/src/components/chat/index.tsx, apps/web/src/components/chat/message-actions/index.tsx, apps/web/src/components/chat/message-actions/logs.tsx, apps/web/src/components/chat/message.tsx, apps/web/src/components/chat/messages.tsx, apps/web/src/components/chat/overview.tsx, apps/web/src/components/chat/suggested-actions.tsx, apps/web/src/components/create-namespace/details-step.tsx, apps/web/src/components/create-namespace/embedding-step.tsx, apps/web/src/components/create-namespace/index.tsx, apps/web/src/components/create-namespace/summary-step.tsx
  Purpose and Scope
  Namespace Creation Wizard
    · Creation State Machine
    · Wizard Steps Implementation
  Demo Template System
    · Template Definitions
    · Seeding Workflow
  Empty States and Dashboard
    · NamespacesEmptyState
    · Namespace Cards
  Chat Interface: Playground vs. Hosted
    · Playground Mode
    · Hosted Mode
    · Component Architecture
  Data Flow: Chat Message Submission

## · Chat UI Components  (L6062)
  源文件: apps/web/src/components/chat/chat-input-modes.tsx, apps/web/src/components/chat/chat-input.tsx, apps/web/src/components/chat/chat-model.tsx, apps/web/src/components/chat/chat-settings.store.ts, apps/web/src/components/chat/citation-button.tsx, apps/web/src/components/chat/citation-modal.tsx, apps/web/src/components/chat/index.tsx, apps/web/src/components/chat/markdown.tsx, apps/web/src/components/chat/message-actions/export-utils.ts, apps/web/src/components/chat/message-actions/export.tsx, apps/web/src/components/chat/message-actions/index.tsx, apps/web/src/components/chat/message-actions/logs.tsx
  Core Architecture and Data Flow
    · Chat Implementation Diagram
  Message Rendering and Markdown
    · Markdown with Citations
    · Reasoning and Status
  Message Actions and Tools
  Chat Settings Store
    · Configuration Schema
    · Request Integration
  Interactive Components
    · Multimodal Input
    · Suggested Actions

## · Authentication and Billing  (L6236)
  源文件: apps/web/src/app/api/(internal-api)/stripe/webhook/checkout-session-completed.ts, apps/web/src/app/api/(internal-api)/stripe/webhook/customer-subscription-deleted.ts, apps/web/src/app/api/(internal-api)/stripe/webhook/customer-subscription-updated.ts, apps/web/src/app/api/(internal-api)/stripe/webhook/invoice-payment-failed.ts, apps/web/src/app/api/(internal-api)/stripe/webhook/utils.ts, apps/web/src/lib/auth.ts, packages/emails/package.json, packages/emails/src/index.ts, packages/emails/src/templates/welcome-email.tsx, packages/stripe/src/functions.ts, packages/stripe/src/plans.ts, Authentication System
  Architecture Overview
  Better-Auth Configuration
    · Core Configuration
    · Email Integration
  User Creation and Organization Setup
  User and Organization Hierarchy
    · Member Roles
    · Organization State and Billing
  Stripe Billing Integration
    · Plan Tiers and Limits
    · Subscription Lifecycle (Webhooks)
    · Usage Metering
  Resource Limits and Enforcement

## · Authentication System  (L6455)
  源文件: apps/web/src/app/api/(internal-api)/stripe/webhook/invoice-payment-failed.ts, apps/web/src/app/app.agentset.ai/login/login-form.tsx, apps/web/src/app/app.agentset.ai/login/page.tsx, apps/web/src/hooks/use-auth.ts, apps/web/src/lib/auth-client.ts, apps/web/src/lib/auth.ts, packages/emails/package.json, packages/emails/src/index.ts, packages/emails/src/templates/email-otp.tsx, packages/emails/src/templates/welcome-email.tsx, packages/ui/src/components/client-only.tsx, packages/ui/src/components/ui/input-otp.tsx
  Purpose and Scope
  Better-Auth Framework
    · Core Configuration
    · Data Flow and Code Entities
  Authentication Methods
    · Magic Link and OTP
    · OAuth Providers
  User Onboarding and Lifecycle
    · Onboarding Workflow
  Session and Organization Management
    · Active Organization Logic
    · Session Retrieval
  Authentication UI Components
    · LoginForm Architecture
    · Redirection Logic
  Email Integration

## · Billing and Subscriptions  (L6673)
  源文件: apps/web/src/app/api/(internal-api)/stripe/webhook/checkout-session-completed.ts, apps/web/src/app/api/(internal-api)/stripe/webhook/customer-subscription-deleted.ts, apps/web/src/app/api/(internal-api)/stripe/webhook/customer-subscription-updated.ts, apps/web/src/app/api/(internal-api)/stripe/webhook/invoice-payment-succeeded.ts, apps/web/src/app/api/(internal-api)/stripe/webhook/route.ts, apps/web/src/app/api/(internal-api)/stripe/webhook/utils.ts, apps/web/src/hooks/use-organization.ts, apps/web/src/server/api/routers/billing.ts, packages/jobs/src/cron/usage.ts, packages/jobs/src/tasks/meter-org-documents.ts, packages/stripe/src/functions.ts, packages/stripe/src/meters.ts
  Overview
  Subscription Architecture
  Plan Tiers and Limits
  Stripe Checkout Flow
    · Checkout Session Creation
    · Post-Checkout Processing
  Webhook Event Handlers
    · customer.subscription.updated
    · customer.subscription.deleted
    · Shared Utilities (`utils.ts`)
  Usage Metering and Tracking
    · Reporting Usage to Stripe
    · Usage Reset and Cron
    · UI Tracking

## · Authorization and Resource Limits  (L6899)
  源文件: apps/web/src/app/api/(internal-api)/stripe/webhook/checkout-session-completed.ts, apps/web/src/app/api/(internal-api)/stripe/webhook/customer-subscription-deleted.ts, apps/web/src/app/api/(internal-api)/stripe/webhook/customer-subscription-updated.ts, apps/web/src/app/api/(internal-api)/stripe/webhook/utils.ts, apps/web/src/app/api/(public-api)/v1/namespace/route.ts, apps/web/src/lib/api/api-key.ts, apps/web/src/lib/api/handler/base.ts, apps/web/src/lib/api/handler/namespace.ts, apps/web/src/services/pagination.ts, packages/stripe/src/functions.ts, packages/stripe/src/plans.ts
  Authorization Middleware
    · Internal tRPC Middleware
    · Public API Handlers
    · Namespace Access Verification
  Resource Limits by Plan
    · Plan Definitions
    · Database Enforcement Fields
  Billing and Subscription Lifecycle
    · Webhook Handling Flow
    · Plan Transitions
  Usage Metering and Caching
    · Page Metering
    · Cache Invalidation

## · API Architecture  (L7067)
  源文件: apps/web/src/app/api/(public-api)/v1/namespace/route.ts, apps/web/src/lib/api/api-key.ts, apps/web/src/lib/api/errors.ts, apps/web/src/lib/api/handler/base.ts, apps/web/src/lib/api/handler/namespace.ts, apps/web/src/schemas/api/query.ts, apps/web/turbo.json
  API Architecture Overview
    · API Consumption Flow
    · Dual API Pattern
  Public REST API (v1)
    · Handler Pattern
    · Standardized Responses and Errors
  Validation and Schemas
    · Key API Schemas
  Child Pages

## · tRPC Routers  (L7230)
  源文件: apps/web/src/components/list-input.tsx, apps/web/src/components/search-chunk.tsx, apps/web/src/components/sortable-list.tsx, apps/web/src/hooks/use-organization.ts, apps/web/src/lib/prompt.ts, apps/web/src/lib/prompts.ts, apps/web/src/server/api/routers/api-keys.ts, apps/web/src/server/api/routers/billing.ts, apps/web/src/server/api/routers/hosting.ts, apps/web/src/server/api/routers/organizations.ts, apps/web/src/services/api-key/create.ts
  Purpose and Scope
  Router Architecture
    · System Overview
  Hosting Router
    · Implementation Details
  Billing Router
    · Organization Middleware
    · Usage Metering
  API Keys Router
    · RBAC Enforcement
  Organization Router
    · Membership and Roles
    · Deletion Safety
  Client-Side Integration Patterns
    · Query Pattern
    · Mutation and Cache Invalidation
  Type-Safe API Design
    · Shared Schemas
    · Contextual Typing

## · Internal API Routes  (L7439)
  源文件: apps/web/src/lib/redis.ts
  Internal API Structure
  Stripe Webhook System
    · Webhook Event Flow
    · Webhook Handler: checkout.session.completed
    · Webhook Handler: customer.subscription.updated
    · Webhook Handler: customer.subscription.deleted
    · Webhook Handler: invoice.payment_failed
  Shared Webhook Utilities
    · Cache Revalidation System
    · Plan Update Utility
  Integration with Authentication System
  Redis Integration
    · Redis Usage Patterns
  Comparison: Internal vs Public vs tRPC APIs

## · Public API and OpenAPI  (L7793)
  源文件: apps/web/src/lib/api/errors.ts, apps/web/src/openapi/v1/code-samples.ts, apps/web/src/openapi/v1/documents/get-chunks-download-url.ts, apps/web/src/openapi/v1/documents/get-document.ts, apps/web/src/openapi/v1/documents/get-file-download-url.ts, apps/web/src/openapi/v1/documents/index.ts, apps/web/src/openapi/v1/documents/list-documents.ts, apps/web/src/openapi/v1/hosting/delete-hosting.ts, apps/web/src/openapi/v1/hosting/enable-hosting.ts, apps/web/src/openapi/v1/hosting/get-hosting.ts, apps/web/src/openapi/v1/hosting/index.ts, apps/web/src/openapi/v1/hosting/update-hosting.ts
  Overview
  OpenAPI Specification
    · Specification Structure
  Authentication and Error Handling
    · Authentication
    · Error Handling
  Document Management Endpoints
    · Retrieval and Downloads
    · Warm-up API
  Search and Query Configuration
    · Query Schema
  SDK Integration Examples
    · TypeScript Example: Downloading a Document
    · TypeScript Example: Updating Hosting
  Data Flow: Document Metadata Retrieval

## · Infrastructure and Configuration  (L7993)
  源文件: .env.example, apps/web/src/app/api/(internal-api)/chat/route.ts, apps/web/src/app/api/(internal-api)/hosting-chat/route.ts, apps/web/src/app/api/(internal-api)/hosting-search/route.ts, apps/web/src/env.ts, apps/web/src/instrumentation-client.ts, apps/web/src/lib/agentic/index.ts, apps/web/src/lib/agentic/search.ts, apps/web/src/lib/redis.ts, packages/engine/package.json, packages/engine/src/env.ts, turbo.json
  Environment Configuration Architecture
    · Configuration Hierarchy
    · Environment Variable Categories
    · Core Environment Variables
  Monorepo Structure and Build System
    · Workspace Organization
    · Dependency Management
  External Services Integration
    · AI and Vector Infrastructure
    · Chat and Search Endpoints

## · Environment Configuration  (L8188)
  源文件: .cursor/rules/project-structure.mdc, .env.example, apps/web/src/app/api/(internal-api)/chat/route.ts, apps/web/src/app/api/(internal-api)/hosting-chat/route.ts, apps/web/src/app/api/(internal-api)/hosting-search/route.ts, apps/web/src/env.ts, apps/web/src/instrumentation-client.ts, apps/web/src/lib/agentic/index.ts, apps/web/src/lib/agentic/search.ts, packages/engine/package.json, packages/engine/src/env.ts, turbo.json
  Purpose and Scope
  Environment Validation Architecture
    · Environment Flow Diagram
    · Implementation with @t3-oss/env-nextjs
  Required Configuration by Package
    · Engine Package (@agentset/engine)
    · Web Application (apps/web)
  Build System and Cache Invalidation
    · Global Environment Mapping
    · Code Entity Space: Environment Mapping
  Development Workflow
    · Local Setup
    · Validation Skipping

## · Job Orchestration with Trigger.dev  (L8360)
  源文件: apps/web/scripts/populate-document-namespace-id.ts, packages/db/.gitignore, packages/db/prisma/schema/schema.prisma, packages/db/src/client.ts, packages/db/src/index.ts, packages/jobs/src/db.ts, packages/jobs/src/schema.ts, packages/jobs/src/tasks/delete-document.ts, packages/jobs/src/tasks/delete-ingest-job.ts, packages/jobs/src/tasks/delete-namespace.ts, packages/jobs/src/tasks/delete-org.ts, packages/jobs/src/tasks/ingest.ts
  Configuration Architecture
    · Runtime Configuration
    · Build Optimizations
  Database Client Configuration
    · Connection Management
  Job Schema Definitions
    · Priority Management
    · Ingestion Job Schema
  Task Implementation Patterns
    · Ingestion Task (`ingestJob`)
    · Document Processing Task (`processDocument`)
  Deletion Task Hierarchy
    · Hierarchical Cleanup Details
    · Rate Limiting
  Re-ingestion Workflow
  Error Handling and Webhooks

## · External Service Integration  (L8634)
  源文件: .gitignore, apps/web/src/lib/redis.ts, packages/storage/src/s3/base.ts, packages/storage/src/s3/document.ts, packages/tinybird/README.md, packages/tinybird/datasources/agentset_webhook_events.datasource, packages/tinybird/package.json, packages/tinybird/pipes/get_webhook_events.pipe, packages/tinybird/src/client.ts, packages/tinybird/src/index.ts, packages/tinybird/src/webhook-events.ts, packages/utils/src/constants.ts
  Overview
  Service Dependency Architecture
  AI/ML Service Integration
    · Embedding and LLM Providers
    · Reranking Services
  Vector Store Integration
    · Pinecone Integration
    · Turbopuffer Integration
  Storage Services
    · Object Storage (S3/R2)
    · Redis Cache
  Infrastructure and Analytics
    · Tinybird Analytics
    · Trigger.dev Job Orchestration
  Configuration Management
    · Environment Variable Pattern

## · Analytics and Events  (L8824)
  源文件: .gitignore, apps/web/src/lib/code-examples/ingest.ts, apps/web/src/openapi/v1/ingest-jobs/create-job.ts, apps/web/src/openapi/v1/ingest-jobs/reingest-job.ts, internal-docs/analytics-events.md, packages/tinybird/README.md, packages/tinybird/datasources/agentset_webhook_events.datasource, packages/tinybird/package.json, packages/tinybird/pipes/get_webhook_events.pipe, packages/tinybird/src/client.ts, packages/tinybird/src/index.ts, packages/tinybird/src/webhook-events.ts
  Overview
    · Event Flow Architecture
  PostHog Event Taxonomy
    · Core Event Categories
  Operational Analytics with Tinybird
    · Webhook Event Logging
    · Data Retrieval
  Webhook System
    · Execution and Reliability
    · Security
  Privacy and Data Handling

## · PostHog Event Tracking  (L8976)
  源文件: .env.example, apps/web/src/app/api/(internal-api)/chat/route.ts, apps/web/src/app/api/(internal-api)/hosting-chat/route.ts, apps/web/src/app/api/(internal-api)/hosting-search/route.ts, apps/web/src/env.ts, apps/web/src/instrumentation-client.ts, apps/web/src/lib/agentic/index.ts, apps/web/src/lib/agentic/search.ts, apps/web/src/lib/code-examples/ingest.ts, apps/web/src/openapi/v1/ingest-jobs/create-job.ts, apps/web/src/openapi/v1/ingest-jobs/reingest-job.ts, internal-docs/analytics-events.md
  Overview and Implementation
    · Key Infrastructure Components
    · Data Flow Diagram: Event Ingestion
  Event Taxonomy
    · 1. Authentication & Organization
    · 2. Namespace & Document Management
    · 3. Chat & Search Usage
    · 4. Public API Tracking
  Client vs. Server Tracking Split
    · Client-Side (PostHog Browser SDK)
    · Server-Side (PostHog Node SDK)
    · Usage Metering vs. Analytics

## · Webhook System  (L9152)
  源文件: apps/web/src/components/delete-confirmation.tsx, apps/web/src/components/webhooks/add-edit-webhook-form.tsx, apps/web/src/components/webhooks/no-events-placeholder.tsx, apps/web/src/components/webhooks/send-test-webhook-modal.tsx, apps/web/src/components/webhooks/webhook-card.tsx, apps/web/src/components/webhooks/webhook-events.tsx, apps/web/src/components/webhooks/webhook-header.tsx, apps/web/src/components/webhooks/webhook-status.tsx, apps/web/src/lib/webhook/create-webhook.ts, apps/web/src/lib/webhook/emit.ts, apps/web/src/lib/webhook/update-webhook.ts, apps/web/src/server/api/routers/webhooks.ts
  System Architecture
    · Delivery Flow
  Event Schemas and Triggers
    · Supported Triggers
    · Payload Structure
  HMAC Signature Verification
  Delivery and Retry Logic
    · Retry Policy
    · Timeout
  Failure Handling and Circuit Breaking
    · Failure Thresholds
    · State Management
  Tinybird Event Log
    · Recorded Data
    · User Interface

## · Glossary  (L9346)
  源文件: .env.example, .github/ISSUE_TEMPLATE/bug_report.md, .github/ISSUE_TEMPLATE/feature_request.md, .github/assets/.gitkeep, .github/assets/readme-cover.png, .github/assets/screenshot.png, .github/assets/star-us.png, LICENSE.md, README.md, apps/web/src/app/api/(internal-api)/chat/route.ts, apps/web/src/app/api/(internal-api)/hosting-chat/route.ts, apps/web/src/app/api/(internal-api)/hosting-search/route.ts
  Core Domain Entities
    · Namespace
    · Organization
    · Tenant ID
  Ingestion Concepts
    · Ingest Job
    · Partition API
    · Chunking
    · Data Flow: Natural Language to Code Entities (Ingestion)
  RAG & Search Concepts
    · Agentic Mode
    · Deep Research
    · Hybrid Search
    · Reciprocal Rank Fusion (RRF)
    · Data Flow: Query to Response (RAG)
  Infrastructure & Technical Jargon
  Billing & Lifecycle Terms
    · Overage
    · Revalidation
    · Webhook Emission