# Skeleton: phoenix（39 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Phoenix Overview | L6 | 13KB | 3 | ~2 | 31 |
| 2 | Package Structure & Monorepo | L272 | 14KB | 2 | ~12 | 30 |
| 3 | Core Concepts & Terminology | L541 | 20KB | 3 | ~21 | 33 |
| 4 | Server Architecture | L962 | 11KB | 3 | ~0 | 32 |
| 5 | Application Server & Configuration | L1207 | 21KB | 4 | ~13 | 37 |
| 6 | GraphQL API | L1614 | 15KB | 4 | ~4 | 24 |
| 7 | REST API & OpenAPI | L1893 | 14KB | 2 | ~0 | 16 |
| 8 | OTLP Ingestion & gRPC Server | L2079 | 11KB | 3 | ~5 | 28 |
| 9 | Database Layer & Migrations | L2308 | 22KB | 5 | ~5 | 27 |
| 10 | Authentication & Authorization | L2699 | 15KB | 2 | ~3 | 28 |
| 11 | Cost Tracking & Model Pricing | L2963 | 12KB | 2 | ~0 | 32 |
| 12 | Client Libraries | L3203 | 11KB | 2 | ~3 | 32 |
| 13 | Python Client (arize-phoenix-client) | L3405 | 24KB | 4 | ~2 | 23 |
| 14 | Python OpenTelemetry (arize-phoenix-otel) | L3766 | 13KB | 4 | ~2 | 22 |
| 15 | Python Evaluations (arize-phoenix-evals) | L4047 | 21KB | 2 | ~5 | 17 |
| 16 | TypeScript Client | L4379 | 15KB | 4 | ~3 | 24 |
| 17 | Command Line Interface (CLI) | L4654 | 17KB | 3 | ~2 | 27 |
| 18 | MCP Server | L4934 | 15KB | 3 | ~6 | 30 |
| 19 | Frontend Application | L5209 | 9KB | 2 | ~3 | 22 |
| 20 | Application Structure & Build System | L5358 | 11KB | 3 | ~1 | 32 |
| 21 | State Management & Theming | L5610 | 18KB | 6 | ~4 | 24 |
| 22 | Playground Interface | L5935 | 21KB | 5 | ~3 | 25 |
| 23 | AI Assistant (PxI) Interface | L6356 | 17KB | 4 | ~1 | 28 |
| 24 | Feature Systems | L6666 | 15KB | 2 | ~2 | 33 |
| 25 | Tracing & Observability | L6956 | 19KB | 5 | ~0 | 22 |
| 26 | Evaluation Framework | L7342 | 18KB | 4 | ~1 | 17 |
| 27 | Datasets & Experiments | L7679 | 27KB | 5 | ~7 | 25 |
| 28 | Prompt Management | L8244 | 23KB | 6 | ~7 | 22 |
| 29 | Playground System | L8759 | 18KB | 7 | ~2 | 25 |
| 30 | AI Agent Backend (PxI) | L9158 | 20KB | 3 | ~1 | 32 |
| 31 | Sessions & Annotations | L9495 | 18KB | 3 | ~5 | 25 |
| 32 | Development & Deployment | L9825 | 12KB | 4 | ~0 | 20 |
| 33 | Development Workflow & Tooling | L10077 | 19KB | 3 | ~13 | 40 |
| 34 | Testing Strategy | L10469 | 18KB | 3 | ~3 | 26 |
| 35 | CI/CD Pipeline | L10823 | 19KB | 2 | ~8 | 32 |
| 36 | Release Management | L11226 | 14KB | 3 | ~7 | 30 |
| 37 | Kubernetes Deployment | L11571 | 22KB | 5 | ~9 | 33 |
| 38 | API Reference Documentation | L12081 | 18KB | 4 | ~3 | 31 |
| 39 | Glossary | L12419 | 23KB | 4 | ~3 | 35 |


## · Phoenix Overview  (L6)
  源文件: .github/workflows/generate-sitemap.yml, .github/workflows/release.yml, .github/workflows/update-phoenix-package-versions.yml, .release-please-manifest.json, CHANGELOG.md, README.md, docs.json, docs/phoenix/cookbook/guardrails/jailbreak-and-prompt-injection-defense.mdx, docs/phoenix/integrations.mdx, docs/phoenix/integrations/llm-providers/cohere.mdx, docs/phoenix/integrations/llm-providers/cohere/cohere-tracing.mdx, docs/phoenix/integrations/llm-providers/orcarouter.mdx
  What is Phoenix?
  Key Capabilities
  Package Structure
    · Phoenix Monorepo Structure
  High-Level Architecture
    · Mapping Natural Language to Key Code Entities
  Data Ingestion Flow
  Quick Start
    · Installation
    · Launch Server
    · Instrument Your Application

## · Package Structure & Monorepo  (L272)
  源文件: .github/workflows/release.yml, .github/workflows/update-phoenix-package-versions.yml, .release-please-manifest.json, CHANGELOG.md, js/examples/apps/demo-document-relevancy-experiment/CHANGELOG.md, js/examples/apps/demo-document-relevancy-experiment/package.json, js/package.json, js/packages/phoenix-cli/CHANGELOG.md, js/packages/phoenix-cli/package.json, js/packages/phoenix-client/CHANGELOG.md, js/packages/phoenix-client/package.json, js/packages/phoenix-config/CHANGELOG.md
  Monorepo Overview
    · Mapping System Components to Monorepo Packages
  Python Package Structure
    · Main Package: `arize-phoenix`
    · Client Package: `arize-phoenix-client`
    · Evaluations Package: `arize-phoenix-evals`
    · SQLite Extension: `phoenix-sqlean`
  TypeScript Package Structure
    · TypeScript Client Package: `@arizeai/phoenix-client`
    · Model Context Protocol Package: `@arizeai/phoenix-mcp`
  Version Manifest & Release Automation
  Dependency Management & Tooling
    · Python (`uv`)
    · TypeScript (`pnpm`)

## · Core Concepts & Terminology  (L541)
  源文件: .github/workflows/generate-sitemap.yml, cspell.json, docs.json, docs/phoenix/cookbook/guardrails/jailbreak-and-prompt-injection-defense.mdx, docs/phoenix/integrations.mdx, docs/phoenix/integrations/llm-providers/cohere.mdx, docs/phoenix/integrations/llm-providers/cohere/cohere-tracing.mdx, docs/phoenix/integrations/llm-providers/orcarouter.mdx, docs/phoenix/integrations/llm-providers/orcarouter/openai-tracing.mdx, docs/phoenix/integrations/llm-providers/together.mdx, docs/phoenix/integrations/llm-providers/together/together-tracing.mdx, docs/phoenix/integrations/python/agentspec.mdx
  Overview of Core Entities
    · Entity Relationship Diagram
  Traces and Spans
    · Trace
    · Span
    · Natural Language to Code Entity Mapping: Tracing
    · SpanKind Enumeration
  Projects and Sessions
    · Project
    · ProjectSession
  Datasets and Experiments
    · Dataset
    · Experiment
  Annotations
    · Annotation Interface (GraphQL)
  Evaluators
    · Natural Language to Code Entity Mapping: Evaluation
    · LLMEvaluator
  Prompts and Versions
    · Prompt
    · PromptVersion

## · Server Architecture  (L962)
  源文件: cspell.json, docs/phoenix/self-hosting/features/authentication.mdx, docs/phoenix/settings/data-retention.mdx, src/phoenix/config.py, src/phoenix/db/engines.py, src/phoenix/server/api/context.py, src/phoenix/server/api/dataloaders/__init__.py, src/phoenix/server/api/queries.py, src/phoenix/server/api/routers/oauth2.py, src/phoenix/server/api/types/Experiment.py, src/phoenix/server/api/types/Project.py, src/phoenix/server/api/types/ProjectSession.py
  Purpose and Scope
  Application Lifecycle
    · Startup Flow Overview
    · Entry Point: `main()`
    · Application Factory: `create_app()`
    · Lifespan and Background Services
  API Layers
    · GraphQL API
    · REST API (v1)
    · OTLP & gRPC
  Database Architecture
    · ORM and Models
    · Request Context & DataLoaders
  Architecture Bridging Diagrams
    · Code-to-System Mapping: Ingestion Path
    · Code-to-System Mapping: GraphQL Resolution
  Session Management

## · Application Server & Configuration  (L1207)
  源文件: cspell.json, docs/phoenix/self-hosting/features/authentication.mdx, docs/phoenix/settings/data-retention.mdx, src/phoenix/config.py, src/phoenix/db/bulk_inserter.py, src/phoenix/db/constants.py, src/phoenix/db/engines.py, src/phoenix/db/types/trace_retention.py, src/phoenix/server/agents/config.py, src/phoenix/server/api/context.py, src/phoenix/server/api/dataloaders/__init__.py, src/phoenix/server/api/queries.py
  Purpose and Scope
  Server Architecture Overview
    · Phoenix Application Server - Component Architecture
  FastAPI Application Creation
    · `create_app()` - Factory Function
  Server Lifecycle Management (Lifespan)
    · Background Daemons Managed by `_lifespan()`
    · Lifespan Startup/Shutdown Sequence Diagram
  Middleware Stack
  Configuration Management
    · Key Environment Variables
    · Runtime Settings Singleton
  Session and Notebook Handling
    · Session Classes
    · `Session` Base Class
    · Dataflow: Notebook Session Integration
  Database Configuration & Engines
    · SQLite Optimization

## · GraphQL API  (L1614)
  源文件: src/phoenix/db/migrations/versions/02463bd83119_add_evaluators.py, src/phoenix/server/api/dataloaders/annotation_summaries.py, src/phoenix/server/api/dataloaders/average_experiment_run_latency.py, src/phoenix/server/api/dataloaders/dataset_example_spans.py, src/phoenix/server/api/dataloaders/document_evaluation_summaries.py, src/phoenix/server/api/dataloaders/experiment_annotation_summaries.py, src/phoenix/server/api/dataloaders/experiment_error_rates.py, src/phoenix/server/api/dataloaders/experiment_run_counts.py, src/phoenix/server/api/dataloaders/experiment_sequence_number.py, src/phoenix/server/api/dataloaders/latency_ms_quantile.py, src/phoenix/server/api/dataloaders/min_start_or_max_end_times.py, src/phoenix/server/api/dataloaders/record_counts.py
  Purpose and Scope
  Schema Construction
    · Schema Building Architecture
  Core Type System
    · Node Interface Hierarchy
    · Primary Domain Types and Relationships
  Query Operations
    · Relay-Style Pagination
    · Complex Field Resolvers
  DataLoader Architecture
    · Key DataLoaders
    · Data Flow Diagram
  Mutation Operations
    · Evaluator Mutations
    · Mutation Logic Space
  Subscription Operations
  Context and Optimization
    · GraphQL Context
    · N+1 Optimization Example

## · REST API & OpenAPI  (L1893)
  源文件: .mintignore, docs/openapi.json, docs/phoenix/sdk-api-reference/rest-api/api-reference/annotations.mdx, docs/phoenix/sdk-api-reference/rest-api/api-reference/annotations/delete-session-annotations-by-filter.mdx, docs/phoenix/sdk-api-reference/rest-api/api-reference/annotations/delete-span-annotations-by-filter.mdx, docs/phoenix/sdk-api-reference/rest-api/api-reference/annotations/delete-trace-annotations-by-filter.mdx, docs/phoenix/sdk-api-reference/rest-api/api-reference/annotations/get-session-annotations-for-a-list-of-session_ids.mdx, docs/phoenix/sdk-api-reference/rest-api/api-reference/annotations/get-trace-annotations-for-a-list-of-trace_ids.mdx, docs/phoenix/sdk-api-reference/rest-api/api-reference/experiments.mdx, docs/phoenix/sdk-api-reference/rest-api/api-reference/experiments/delete-experiment-by-id.mdx, docs/phoenix/sdk-api-reference/rest-api/api-reference/experiments/get-incomplete-evaluations-for-an-experiment.mdx, docs/phoenix/sdk-api-reference/rest-api/api-reference/experiments/get-incomplete-runs-for-an-experiment.mdx
  Architecture Overview
    · Request Flow and Data Transformation
    · API to Code Entity Mapping
  OpenAPI Specification
  Client Generation
    · TypeScript Client Generation
    · Python Client Generation
  Key API Subsystems
    · Traces & Spans
    · Datasets & Experiments
    · Prompt Management
  Implementation Diagram

## · OTLP Ingestion & gRPC Server  (L2079)
  源文件: examples/computer_use_agent/instrumentor.py, requirements/integration-tests.txt, src/phoenix/db/bulk_inserter.py, src/phoenix/db/constants.py, src/phoenix/db/insertion/span.py, src/phoenix/db/migrations/data_migration_scripts/populate_project_sessions.py, src/phoenix/db/migrations/versions/4ded9e43755f_create_project_sessions_table.py, src/phoenix/db/types/trace_retention.py, src/phoenix/server/grpc_server.py, src/phoenix/server/prometheus.py, src/phoenix/server/retention.py, src/phoenix/server/telemetry.py
  Purpose and Scope
  Architecture Overview
    · System Components Diagram: From Ingestion to Code
  OTLP Protocol Support
    · Data Flow Diagram: OTLP Trace Export Request to Phoenix Span Insertion
    · OTLP Export Method Processing
  Request Processing Pipeline
    · Bulk Inserter Mechanism
    · Database Insertion Logic
  Capacity Management & Monitoring
  Summary of Key Entities
    · OTLP Ingestion Pipeline: Natural Language to Code Entities

## · Database Layer & Migrations  (L2308)
  源文件: Makefile, packages/phoenix-client/scripts/codegen/transform.py, requirements/integration-tests.txt, scripts/README.md, scripts/ddl/compare_schemas.py, scripts/ddl/generate_ddl_postgresql.py, scripts/ddl/generate_ddl_sqlite.py, src/phoenix/db/alembic.ini, src/phoenix/db/ddl/__init__.py, src/phoenix/db/ddl/postgresql_schema.sql, src/phoenix/db/ddl/sqlite_schema.sql, src/phoenix/db/helpers.py
  Overview
  Database Architecture
  Database Support
    · PostgreSQL Specifics
    · SQLite Specifics & `phoenix-sqlean`
  SQLAlchemy ORM Models
    · Core Entity Relationships
    · Key Model Classes
  Custom Type Decorators
  Migration System
    · Alembic Integration
    · Migration Evolution Highlights
  DDL Generation and Schema Comparison
  Insertion Logic & Helpers
    · Span Insertion Flow
    · Experiment Run and Annotation Upsert
    · From Natural Language Concepts to Database Layer Components
    · From Phoenix System Names to Database Code Artifacts

## · Authentication & Authorization  (L2699)
  源文件: .github/.scripts/sync_models.py, docs/phoenix/self-hosting/features/authentication.mdx, docs/phoenix/settings/data-retention.mdx, scripts/verify_threshold_cost.py, src/phoenix/auth.py, src/phoenix/config.py, src/phoenix/db/engines.py, src/phoenix/db/facilitator.py, src/phoenix/db/migrations/versions/cd164e83824f_users_and_tokens.py, src/phoenix/server/api/auth.py, src/phoenix/server/api/dataloaders/span_annotations.py, src/phoenix/server/api/input_types/CreateProjectInput.py
  Overview
  Authentication Architecture
    · Code Entity Space Mapping of Authentication Components
  Authentication Methods
    · Local Authentication (Password-Based)
    · OAuth2/OIDC Integration
  Role-Based Access Control (RBAC)
    · Enforcement
  Token & API Key Management
    · JwtStore
    · API Keys
  Facilitator Pattern
  Security Features
    · Brute Force Login Protection
    · Rate Limiting

## · Cost Tracking & Model Pricing  (L2963)
  源文件: .github/.scripts/sync_models.py, .github/workflows/cost-sync.yml, .github/workflows/helm-ci.yml, .github/workflows/playwright.yaml, .github/workflows/publish.yaml, .github/workflows/pypi-smoke-test.yml, .github/workflows/python-CI.yml, .github/workflows/python-all-platforms.yml, .github/workflows/sync-lockfile-release-pr.yml, .github/workflows/typescript-CI.yml, Dockerfile, scripts/docker/devops/Dockerfile
  System Architecture
    · Overview Diagram: Cost Tracking System Components and Data Flow
  Model Cost Manifest
    · Structure and Content
  CostModelLookup Class
    · Key Responsibilities
  GenerativeModelStore Daemon
    · Functionality and Implementation
  SpanCostCalculator Overview
    · Process Steps
    · Span Cost Calculation Sequence Diagram
  Database Seeding and Facilitation
    · Model Cost Initialization
  Managing Models via GraphQL API Mutations
    · Key Mutations Supported
  Cost-Sync Workflow

## · Client Libraries  (L3203)
  源文件: README.md, js/examples/apps/demo-document-relevancy-experiment/CHANGELOG.md, js/examples/apps/demo-document-relevancy-experiment/package.json, js/examples/apps/eve-agent/README.md, js/package.json, js/packages/phoenix-cli/CHANGELOG.md, js/packages/phoenix-cli/package.json, js/packages/phoenix-client/CHANGELOG.md, js/packages/phoenix-client/README.md, js/packages/phoenix-client/examples/create_dataset_from_spans.ts, js/packages/phoenix-client/examples/delete_experiment_project.ts, js/packages/phoenix-client/package.json
  Package Ecosystem
    · Client Libraries Architecture Diagram
  Package Distribution
  Common Usage Patterns
    · Code Entity Mapping
  OpenTelemetry Tracing
    · Python OpenTelemetry (arize-phoenix-otel)
    · TypeScript OpenTelemetry (@arizeai/phoenix-otel)
  Code Generation
  Evaluation Libraries
  Developer Tools
    · CLI (`@arizeai/phoenix-cli`)
    · MCP Server (`@arizeai/phoenix-mcp`)

## · Python Client (arize-phoenix-client)  (L3405)
  源文件: docs/phoenix/sdk-api-reference/typescript/packages/phoenix-client/prompts.mdx, js/packages/phoenix-client/.cursor/rules/general.mdc, js/packages/phoenix-client/examples/dataset_get_by_name.ts, js/packages/phoenix-client/src/constants/serverRequirements.ts, js/packages/phoenix-client/src/datasets/appendDatasetExamples.ts, js/packages/phoenix-client/src/datasets/createDataset.ts, js/packages/phoenix-client/src/datasets/getDataset.ts, js/packages/phoenix-client/src/datasets/getDatasetExamples.ts, js/packages/phoenix-client/src/datasets/getDatasetInfo.ts, js/packages/phoenix-client/src/datasets/getDatasetInfoByName.ts, js/packages/phoenix-client/src/datasets/index.ts, js/packages/phoenix-client/src/experiments/getExperimentInfo.ts
  Architecture and Client Structure
    · Client and Resource Class Overview
  Initialization and Configuration
  Resource APIs
    · 1. Spans and Annotations
    · 2. Datasets and Experiments
    · 3. Prompt Management
  Implementation Details
    · Span Modification and Capture for Experiments
    · Data Flow from Client to Phoenix Server
    · Rate Limiting and Retry Logic
  Harbor and ATIF Support

## · Python OpenTelemetry (arize-phoenix-otel)  (L3766)
  源文件: examples/computer_use_agent/instrumentor.py, packages/phoenix-client/src/phoenix/client/utils/config.py, packages/phoenix-otel/CHANGELOG.md, packages/phoenix-otel/docs/source/api/exporters.rst, packages/phoenix-otel/docs/source/api/processors.rst, packages/phoenix-otel/docs/source/api/provider.rst, packages/phoenix-otel/docs/source/api/register.rst, packages/phoenix-otel/docs/source/api/settings.rst, packages/phoenix-otel/pyproject.toml, packages/phoenix-otel/src/phoenix/otel/__init__.py, packages/phoenix-otel/src/phoenix/otel/otel.py, packages/phoenix-otel/src/phoenix/otel/settings.py
  Package Overview
  Module Structure
  Core Components
    · The `register()` Function
    · TracerProvider
    · Span Exporters
  Configuration & .env.phoenix Discovery
    · Environment Variables
    · Discovery Logic
  Auto-Instrumentation

## · Python Evaluations (arize-phoenix-evals)  (L4047)
  源文件: docs/phoenix/evaluation/pre-built-metrics.mdx, docs/phoenix/evaluation/pre-built-metrics/hallucination.mdx, docs/phoenix/evaluation/pre-built-metrics/toxicity.mdx, js/benchmarks/evals-benchmarks/src/hallucination.eval.ts, js/benchmarks/evals-benchmarks/src/toxicity.eval.ts, js/packages/phoenix-evals/src/__generated__/default_templates/DOCUMENT_RELEVANCE_CLASSIFICATION_EVALUATOR_CONFIG.ts, js/packages/phoenix-evals/src/__generated__/default_templates/HALLUCINATION_CLASSIFICATION_EVALUATOR_CONFIG.ts, js/packages/phoenix-evals/src/__generated__/default_templates/TOXICITY_CLASSIFICATION_EVALUATOR_CONFIG.ts, js/packages/phoenix-evals/src/__generated__/default_templates/index.ts, js/packages/phoenix-evals/src/llm/createHallucinationEvaluator.ts, js/packages/phoenix-evals/src/llm/createToxicityEvaluator.ts, js/packages/phoenix-evals/src/llm/index.ts
  Architecture Overview
    · Evaluation Data Flow
  Core Abstractions
    · Evaluator Base Class
    · Score Model
  LLM Provider Support
    · Provider Registry and Adapters
    · Execution & Concurrency
  Built-in Metrics
  Templating and Data Handling
    · Prompt Templates
    · Evaluation Execution Functions
  Tracing and Instrumentation

## · TypeScript Client  (L4379)
  源文件: js/examples/apps/phoenix-experiment-runner/index.ts, js/examples/notebooks/phoenix_prompts_cross_sdk_tutorial.ipynb, js/examples/notebooks/phoenix_prompts_openai_tutorial.ipynb, js/examples/notebooks/phoenix_prompts_vercel_ai_sdk.ipynb, js/packages/phoenix-cli/src/commands/options.ts, js/packages/phoenix-cli/src/config.ts, js/packages/phoenix-cli/src/pxi/index.tsx, js/packages/phoenix-cli/src/pxi/preflight.ts, js/packages/phoenix-cli/test/pxiPreflight.test.ts, js/packages/phoenix-client/examples/apply_prompt_vercel.ts, js/packages/phoenix-client/examples/dataset_get_by_name.ts, js/packages/phoenix-client/examples/resume_experiment.ts
  Package Structure
    · High-Level Module Organization
  Client Initialization and Configuration
  Dataset Management
  Experiment Framework
    · Experiment Execution (`runExperiment`)
    · Resuming Experiments
  Prompt Management and SDK Converters
    · Supported SDK Conversions
  Tracing Integration
  System Mapping
    · Concept to Code Mapping
    · API Flow

## · Command Line Interface (CLI)  (L4654)
  源文件: .agents/skills/phoenix-cli/SKILL.md, .agents/skills/phoenix-cli/references/axial-coding.md, .agents/skills/phoenix-cli/references/open-coding.md, .agents/skills/phoenix-evals/references/integrations-pytest.md, .agents/skills/phoenix-evals/references/integrations-vitest-jest.md, .agents/skills/phoenix-integration-snippets/SKILL.md, .oxlintrc.json, docs/phoenix/datasets-and-experiments/how-to-experiments/eval-ci-with-pytest.mdx, docs/phoenix/datasets-and-experiments/how-to-experiments/run-experiments.mdx, docs/phoenix/evaluation/integrations/pytest.mdx, docs/phoenix/evaluation/integrations/vitest-jest.mdx, docs/phoenix/integrations/remote-mcp.mdx
  Installation and Configuration
    · Installation
    · Configuration
    · Profiles
  Interactive PXI Terminal Agent
    · PXI Implementation
  Architecture and Data Flow
    · Component Overview Diagram
  Command Reference
    · Traces and Spans
    · Datasets and Experiments
    · Setup and MCP
  Implementation Details
    · Setup and Instrumentation Scaffolding
    · Safety Guards on Deletes
  Bridging Natural Language to Code Entities
    · CLI Command Dispatch Flow
    · PXI Agent Interaction Flow
    · Sources

## · MCP Server  (L4934)
  源文件: README.md, docs/phoenix/integrations/remote-mcp.mdx, js/examples/apps/demo-document-relevancy-experiment/CHANGELOG.md, js/examples/apps/demo-document-relevancy-experiment/package.json, js/examples/apps/eve-agent/README.md, js/package.json, js/packages/phoenix-cli/.gitignore, js/packages/phoenix-cli/CHANGELOG.md, js/packages/phoenix-cli/package.json, js/packages/phoenix-cli/src/commands/setupMcp.ts, js/packages/phoenix-cli/src/setup/agents/registry.ts, js/packages/phoenix-cli/src/setup/mcp/agents.ts
  Purpose and Scope
  Architecture Overview
    · MCP Server Data Flow
  Package Configuration
    · Core Dependencies
  Available Tools
  Implementation Details
    · Entry Point and Initialization
  Code Entity to Natural Language Space Mapping
    · Diagram 1: Trace Retrieval Workflow
    · Diagram 2: Project Management Flow
  Development and Deployment
    · Development Workflow
    · Environment Variables and Configuration
    · Integration with AI Assistants

## · Frontend Application  (L5209)
  源文件: .agents/skills/agent-browser/SKILL.md, .agents/skills/phoenix-design/SKILL.md, .agents/skills/phoenix-design/references/bem.md, .agents/skills/phoenix-design/references/counters.md, .agents/skills/phoenix-design/references/dialogs.md, .agents/skills/phoenix-design/references/error-display.md, .agents/skills/phoenix-frontend/SKILL.md, .agents/skills/phoenix-frontend/references/accessibility.md, .agents/skills/phoenix-frontend/references/components.md, .agents/skills/phoenix-playwright-tests/SKILL.md, .agents/skills/phoenix-typescript/SKILL.md, docs/phoenix/cookbook/ai-engineering-workflows/iterative-evaluation-and-experimentation-workflow-typescript.mdx
  Technology Stack
  Application Architecture
    · Directory Structure
    · Navigation and Layout
  Build and Development Workflow
  Key Feature Systems
    · Tracing and Observability
    · State and Theming
    · Playground Interface
    · AI Assistant (PxI) Interface

## · Application Structure & Build System  (L5358)
  源文件: .agents/skills/agent-browser/SKILL.md, .agents/skills/phoenix-design/SKILL.md, .agents/skills/phoenix-design/references/bem.md, .agents/skills/phoenix-design/references/counters.md, .agents/skills/phoenix-design/references/dialogs.md, .agents/skills/phoenix-design/references/error-display.md, .agents/skills/phoenix-frontend/SKILL.md, .agents/skills/phoenix-frontend/references/accessibility.md, .agents/skills/phoenix-frontend/references/components.md, .agents/skills/phoenix-playwright-tests/SKILL.md, .agents/skills/phoenix-typescript/SKILL.md, cspell.json
  Build System Overview
    · Package Management & Scripts
    · Vite Configuration
  Application Architecture
    · Routing System
    · State Management Strategy
  Relay Integration & Data Flow
  Component Architecture & Theming
    · Theming System
    · Component Organization
    · External Libraries

## · State Management & Theming  (L5610)
  源文件: .agents/skills/agent-browser/SKILL.md, .agents/skills/phoenix-design/SKILL.md, .agents/skills/phoenix-design/references/bem.md, .agents/skills/phoenix-design/references/counters.md, .agents/skills/phoenix-design/references/dialogs.md, .agents/skills/phoenix-design/references/error-display.md, .agents/skills/phoenix-frontend/SKILL.md, .agents/skills/phoenix-frontend/references/accessibility.md, .agents/skills/phoenix-frontend/references/components.md, .agents/skills/phoenix-playwright-tests/SKILL.md, .agents/skills/phoenix-typescript/SKILL.md, docs/phoenix/tracing/how-to-tracing.mdx
  State Management Architecture
    · Provider Tree Hierarchy
    · Zustand Stores
    · Relay Cache & Data Flow
  Theming System
    · CSS Custom Properties Architecture
    · Theme Selection & Application
  Domain Filter DSL: Span and Session Filtering
    · SpanFilter DSL
    · SessionFilter DSL
    · Flow from User Filter String to SQL Predicate and UI Filtering
  React Context Providers and Hooks

## · Playground Interface  (L5935)
  源文件: .agents/skills/phoenix-rest-api/SKILL.md, .agents/skills/phoenix-rest-api/references/endpoint-patterns.md, .agents/skills/phoenix-rest-api/references/openapi-codegen.md, .agents/skills/phoenix-rest-api/references/testing-patterns.md, internal_docs/specs/async-llm-client-lifecycle.md, internal_docs/specs/experiment-runner-background-process/appendix-rate-limiting.md, src/phoenix/server/api/evaluators.py, src/phoenix/server/api/helpers/message_helpers.py, src/phoenix/server/api/helpers/playground_clients.py, src/phoenix/server/api/helpers/playground_registry.py, src/phoenix/server/api/helpers/secrets.py, src/phoenix/server/api/input_types/EvaluatorPreviewInput.py
  Component Architecture
    · Component Hierarchy Diagram
  State Management
    · Store Structure Overview
    · Key Store Actions
    · Normalized Messages Pattern Diagram
    · Instance Initialization Logic
  Communication and Streaming Flow
    · Backend Streaming
    · Frontend Subscription and Chunk Handling
    · Sequence Diagram of Full Streaming Flow
  Template Editing and Message Handling
  Instance Management
  Credential Handling and Use
  Span Integration for Playground Hydration
    · Tool Call Processing

## · AI Assistant (PxI) Interface  (L6356)
  源文件: .oxlintrc.json, js/.oxlintrc.json, js/app/.oxlintrc.json, js/app/src/agent/chat/__tests__/createAgentSessionChat.test.ts, js/app/src/utils/filterConditionUtils.ts, js/app/stories/ExperimentItem.stories.tsx, js/packages/phoenix-cli/src/pxi/App.tsx, js/packages/phoenix-cli/src/pxi/commands.ts, js/packages/phoenix-cli/src/pxi/draftEditor.ts, js/packages/phoenix-cli/src/pxi/tokenUsage.ts, js/packages/phoenix-cli/src/pxi/toolPresentation.ts, js/packages/phoenix-cli/src/pxi/toolProgress.ts
  System Overview
    · Key Frontend Components
    · State Management
  Data Flow: From Natural Language to Code Entities
  Frontend Architecture
    · Session Management
    · Agent UI Surfaces and Positioning
    · Chat Runtime and Message Handling
    · Capability Flags and Feature Gating
  Tool Registry and Generative UI Components
    · Tool Call Lifecycle
    · Key Tool UI Components
  Integration with Phoenix Server
    · Request Construction and Metadata Injection
    · Usage Tracking and Session Updates
  Diagrams: Mapping Natural Language Space to Code Entities
    · PxI Request Lifecycle Full Stack Mapping
    · PxI Capability & Tooling Architecture Bridging UI and Code Entities
  Summary
  Sources

## · Feature Systems  (L6666)
  源文件: .github/workflows/generate-sitemap.yml, cspell.json, docs.json, docs/phoenix/cookbook/guardrails/jailbreak-and-prompt-injection-defense.mdx, docs/phoenix/integrations.mdx, docs/phoenix/integrations/llm-providers/cohere.mdx, docs/phoenix/integrations/llm-providers/cohere/cohere-tracing.mdx, docs/phoenix/integrations/llm-providers/orcarouter.mdx, docs/phoenix/integrations/llm-providers/orcarouter/openai-tracing.mdx, docs/phoenix/integrations/llm-providers/together.mdx, docs/phoenix/integrations/llm-providers/together/together-tracing.mdx, docs/phoenix/integrations/python/agentspec.mdx
  Feature System Architecture
  Core Feature Overviews
    · Tracing & Observability
    · Evaluation Framework
    · Datasets & Experiments
    · Prompt Management
    · Playground System
    · AI Agent Backend (PxI)
    · Sessions & Annotations
  Data Model Integration
  Cross-System Data Flow Example
  Common Infrastructure Features
    · Cost Tracking
    · Authentication & Authorization
    · DML Events and Real-Time Updates

## · Tracing & Observability  (L6956)
  源文件: docs/phoenix/tracing/how-to-tracing.mdx, docs/phoenix/tracing/how-to-tracing/filter-expressions.mdx, docs/phoenix/tracing/how-to-tracing/importing-and-exporting-traces/exporting-annotated-spans.mdx, docs/phoenix/tracing/how-to-tracing/importing-and-exporting-traces/extract-data-from-spans.mdx, evals/pxi/datasets/product_knowledge.yaml, evals/pxi/evaluators/text.py, internal_docs/specs/session-filter-dsl.md, internal_docs/specs/span-filter-dsl.md, requirements/integration-tests.txt, scripts/data/generate_traces.py, src/phoenix/db/insertion/span.py, src/phoenix/db/migrations/data_migration_scripts/populate_project_sessions.py
  Purpose and Scope
  Architecture Overview
  Phoenix OTEL Packages and Span Ingestion
  Data Model & Trace Representation
    · Span & Trace Model
    · OpenInference Semantic Conventions
  Filtering System Using Custom DSL
  Observability Features and UI Components
    · Trace Tree & Span Details Views
    · Annotations and Span Evaluation
    · Filtering & Sorting in UI Tables
    · Performance Metrics
    · User Preferences
    · Trace & Span Observability UI Component Diagram
    · Summary: Natural Language to Code Entities in Tracing & Observability
    · Tracing & Filtering Code Entities Mapping

## · Evaluation Framework  (L7342)
  源文件: docs/phoenix/evaluation/pre-built-metrics.mdx, docs/phoenix/evaluation/pre-built-metrics/hallucination.mdx, docs/phoenix/evaluation/pre-built-metrics/toxicity.mdx, js/benchmarks/evals-benchmarks/src/hallucination.eval.ts, js/benchmarks/evals-benchmarks/src/toxicity.eval.ts, js/packages/phoenix-evals/src/__generated__/default_templates/DOCUMENT_RELEVANCE_CLASSIFICATION_EVALUATOR_CONFIG.ts, js/packages/phoenix-evals/src/__generated__/default_templates/HALLUCINATION_CLASSIFICATION_EVALUATOR_CONFIG.ts, js/packages/phoenix-evals/src/__generated__/default_templates/TOXICITY_CLASSIFICATION_EVALUATOR_CONFIG.ts, js/packages/phoenix-evals/src/__generated__/default_templates/index.ts, js/packages/phoenix-evals/src/llm/createHallucinationEvaluator.ts, js/packages/phoenix-evals/src/llm/createToxicityEvaluator.ts, js/packages/phoenix-evals/src/llm/index.ts
  Purpose and Scope
  Architecture Overview
    · Evaluation Framework Architecture Diagram
  Evaluator Implementations
    · LLMEvaluator
    · CodeEvaluator
    · BuiltInEvaluator
  Input Mapping and Context Resolution
    · GraphQL Input Mapping Schema
    · Input Mapping Data Flow
  Annotation Storage and Output Configuration
    · OutputConfig Types
    · OptimizationDirection Enum
    · Annotations
  Evaluation Result Flow in GraphQL Mutations
  UI Components for Evaluator Interaction
    · EvaluatorsTable
    · EvaluatorOutputPreview
  Summary Diagrams Bridging Natural Language Evaluation Concepts to Code Entities
    · 1. LLM Evaluator Execution Flow
    · 2. Code Evaluator Execution Flow

## · Datasets & Experiments  (L7679)
  源文件: js/examples/apps/phoenix-experiment-runner/index.ts, js/packages/phoenix-cli/src/commands/options.ts, js/packages/phoenix-cli/src/config.ts, js/packages/phoenix-client/src/config.ts, js/packages/phoenix-client/src/experiments/index.ts, js/packages/phoenix-client/src/experiments/logging.ts, js/packages/phoenix-client/src/experiments/resumeEvaluation.ts, js/packages/phoenix-client/src/experiments/resumeExperiment.ts, js/packages/phoenix-client/src/experiments/runExperiment.ts, js/packages/phoenix-client/src/experiments/tracing.ts, js/packages/phoenix-client/src/logger.ts, js/packages/phoenix-client/src/types/experiments.ts
  Overview
    · Natural Language to Code Entity Mapping
  Database Schema
  Datasets
    · Dataset Components
    · Dataset Versioning and Splits
    · Code-level Representation
    · Dataset Example Shape Validation
    · REST API Endpoints
    · Frontend Dataset Management
  Experiments
    · Experiment Model
    · Creating Experiments via API
    · Recording Experiment Runs
    · Evaluations
    · Visualizing Experiments in UI
  TypeScript Experiment Runner (`runExperiment`)
    · Key Features
    · Important Parameters
    · Data Flow
    · Snippet illustrating task invocation arguments:
    · Span and Trace Management
    · Error Handling
    · Usage Example
  System Architecture Diagram for Experiments and Datasets
  Database Migrations
  Integration with Trace and Span Observability

## · Prompt Management  (L8244)
  源文件: docs/phoenix/sdk-api-reference/typescript/packages/phoenix-client/prompts.mdx, js/examples/notebooks/phoenix_prompts_cross_sdk_tutorial.ipynb, js/examples/notebooks/phoenix_prompts_openai_tutorial.ipynb, js/examples/notebooks/phoenix_prompts_vercel_ai_sdk.ipynb, js/packages/phoenix-client/.cursor/rules/general.mdc, js/packages/phoenix-client/examples/apply_prompt_vercel.ts, js/packages/phoenix-client/examples/resume_experiment.ts, js/packages/phoenix-client/src/prompts/index.ts, js/packages/phoenix-client/src/prompts/sdks/toAI.ts, js/packages/phoenix-client/src/prompts/updatePrompt.ts, js/packages/phoenix-client/src/schemas/llm/constants.ts, js/packages/phoenix-client/src/schemas/llm/converters.ts
  Overview and Purpose
  Data Model
    · Key Entity Details
  Template Types and Formats
  Prompt Versioning and Lifecycle
    · Versioning Operations
    · Important Implementation Notes
  PromptVersion GraphQL Types
    · `Prompt` Type (Core container)
    · `PromptVersion` Type
  Prompt Mutations API
  Client SDK Helpers for Prompt Usage
    · Core SDK Features
  Integration with Evaluators and LLM Providers
  Template Parsing and Rendering
  User Interface: Prompt Pages and Playground
    · User Intent to Prompt Management Mutations and Models
    · PromptVersion Frontend Data Flow

## · Playground System  (L8759)
  源文件: .agents/skills/phoenix-rest-api/SKILL.md, .agents/skills/phoenix-rest-api/references/endpoint-patterns.md, .agents/skills/phoenix-rest-api/references/openapi-codegen.md, .agents/skills/phoenix-rest-api/references/testing-patterns.md, internal_docs/specs/async-llm-client-lifecycle.md, internal_docs/specs/experiment-runner-background-process/appendix-rate-limiting.md, src/phoenix/server/api/evaluators.py, src/phoenix/server/api/helpers/message_helpers.py, src/phoenix/server/api/helpers/playground_clients.py, src/phoenix/server/api/helpers/playground_registry.py, src/phoenix/server/api/helpers/secrets.py, src/phoenix/server/api/input_types/EvaluatorPreviewInput.py
  System Architecture
  LLM Client Abstraction Layer
    · PlaygroundClient Abstract Base Class Details
    · Provider-Specific Implementations
    · Provider Registration and Discovery
  Streaming Execution via GraphQL Subscriptions
    · Subscription Workflow
    · Concurrency and Cleanup
    · Message Chunk Types
  Multi-Provider Support and Rate Limiting
  Playground Registry
  Summary
  Natural Language: LLM Client Layer — Code Entities
  Natural Language: GraphQL Subscription Handler — Code Entities

## · AI Agent Backend (PxI)  (L9158)
  源文件: .github/pull_request_template.md, docs/phoenix/evaluation/typescript-quickstart.mdx, docs/phoenix/pxi.mdx, evals/pxi/README.md, evals/pxi/conftest.py, evals/pxi/datasets/experiment_observations.yaml, evals/pxi/gate.py, evals/pxi/harness/agent_task.py, evals/pxi/online_evals/OVERVIEW.md, evals/pxi/online_evals/evaluators/__init__.py, evals/pxi/online_evals/evaluators/tool_count_per_turn.py, evals/pxi/online_evals/evaluators/user_friction.py
  Purpose and Scope
  Architecture Overview
    · Key Components and Relationships
    · AI Agent Backend Data Flow
  `/agents` REST Endpoint
    · Request Message Model
    · Response Model
  Agent Factory (`build_agent`)
    · Inputs
    · Capabilities Composed
    · Output
  Model Selection (`build_model`)
    · Model Provider Types
    · Credential Resolution Logic
    · Wrapping and Instrumentation
  Tool Capabilities
  Context Resolution
    · Context Types
    · Context Resolution Flow
  OpenTelemetry Tracing (PxI)
    · Tracer Design
    · PxI Tracer Data Flow
  PXI Evaluation Harness
    · Structure
    · Capabilities
  Summary
  References and Sources

## · Sessions & Annotations  (L9495)
  源文件: src/phoenix/db/insertion/document_annotation.py, src/phoenix/db/insertion/span_annotation.py, src/phoenix/db/insertion/trace_annotation.py, src/phoenix/db/insertion/types.py, src/phoenix/db/types/annotation_configs.py, src/phoenix/server/api/auth.py, src/phoenix/server/api/dataloaders/annotation_summaries.py, src/phoenix/server/api/dataloaders/span_annotations.py, src/phoenix/server/api/input_types/CreateProjectInput.py, src/phoenix/server/api/input_types/CreateSpanAnnotationInput.py, src/phoenix/server/api/input_types/CreateTraceAnnotationInput.py, src/phoenix/server/api/input_types/PatchAnnotationInput.py
  Project Sessions
    · Data Model and Creation
    · Session Attributes and API Surface
    · Frontend Usage: Sessions Table and Session Details
    · Natural Language to Code Space: Sessions
  Annotation System
    · Core Annotation Models
    · Annotation Configuration
    · Annotation Management via API
    · Frontend Annotation UI Components
    · Natural Language to Code Space: Annotations
    · Annotation Data Flow
  Summary

## · Development & Deployment  (L9825)
  源文件: .agents/setup, .codex/config.toml, .codex/hooks.json, .codex/hooks/run_changed_file_checks.sh, .github/workflows/cost-sync.yml, .github/workflows/helm-ci.yml, .github/workflows/playwright.yaml, .github/workflows/publish.yaml, .github/workflows/pypi-smoke-test.yml, .github/workflows/python-CI.yml, .github/workflows/python-all-platforms.yml, .github/workflows/sync-lockfile-release-pr.yml
  Development Workflow & Tooling
    · Key Aspects:
    · How it fits together:
  Testing Strategy
    · Test Types:
  CI/CD Pipeline
    · Highlights:
  Release Management
    · Release Workflow:
  Kubernetes Deployment
    · Components and Features:
  API Reference Documentation

## · Development Workflow & Tooling  (L10077)
  源文件: .agents/setup, .agents/skills/phoenix-github/SKILL.md, .agents/skills/phoenix-github/scripts/_board.py, .agents/skills/phoenix-github/scripts/board.json, .agents/skills/phoenix-github/scripts/health.py, .agents/skills/phoenix-github/scripts/roadmap.py, .agents/skills/phoenix-github/scripts/rollover.py, .agents/skills/phoenix-github/scripts/snapshot.sh, .agents/skills/phoenix-github/scripts/standup.py, .claude/settings.json, .codex/config.toml, .codex/hooks.json
  Development Environment Overview
    · Workflow Tooling Diagram: Mapping Natural Language to Code Entities
  Python Development Tools
    · Package Management: uv
    · Testing & Environment Orchestration: tox
    · Code Formatting and Linting (Python)
  TypeScript Development Tools
    · Package Management: pnpm
    · Build and Quality Toolchain
  Pre-commit Hooks
    · Pre-commit Hooks Summary
    · Installing Pre-commit Hooks
  Agent / AI Coding Assistant Configuration Files
    · `.agents/` Directory
    · `.claude/settings.json`
    · `.cursor/`
    · `.codex/`
  Makefile and Unified Commands
    · Key Make Targets

## · Testing Strategy  (L10469)
  源文件: docs/phoenix/tracing/how-to-tracing/setup-tracing/setup-projects.mdx, internal_docs/specs/async-llm-client-lifecycle.md, internal_docs/specs/experiment-runner-background-process/appendix-rate-limiting.md, js/packages/phoenix-client/src/__generated__/api/v1.ts, js/packages/phoenix-testing/src/__generated__/api/v1.ts, packages/phoenix-client/src/phoenix/client/__generated__/v1/__init__.py, packages/phoenix-evals/tests/phoenix/evals/llm/adapters/litellm/test_adapter.py, packages/phoenix-evals/tests/phoenix/evals/llm/adapters/litellm/test_build_messages.py, pyproject.toml, requirements/ci.txt, requirements/integration-tests.txt, requirements/packages/phoenix-evals.txt
  Purpose and Scope
  Test Types and Scope
  Test Organization and Structure
    · Directory Layout
    · E2E Test Configuration with Playwright
  Database Fixture Strategy
    · Span Insertion as Core Database Interaction
  Migration Testing
  Package and Canary Testing
  Mock LLM Server
  Canary Tests for SDK Integration
  End-to-End Test Scenarios
    · Server Evaluators Workflow
    · Prompt Lifecycle
    · User & Access Management
  Code Entity Association Diagram

## · CI/CD Pipeline  (L10823)
  源文件: .agents/skills/phoenix-docs-gap-audit/SKILL.md, .agents/skills/phoenix-skills-audit/SKILL.md, .agents/skills/phoenix-skills-audit/evals/evals.json, .eslintignore, .github/.scripts/collect-customer-issues.js, .github/actions/docker-build-image/action.yml, .github/actions/docker-merge-manifest/action.yml, .github/workflows/auto-label-external-issues.yaml, .github/workflows/check-dependabot-uv-version.yml, .github/workflows/claude-code-review.yml, .github/workflows/claude-docs-gap-audit.yml, .github/workflows/claude-implement-issue.yml
  Overview
  Pipeline Architecture
  Python CI Pipeline
    · Change Detection and Conditional Execution
    · Test Environments and Commands
  TypeScript CI Pipeline
    · Change Detection
    · Steps
  Playwright End-to-End Testing
    · Sandbox Runtime Setup
    · Execution
  Docker Build & Deployment Automation
    · Multi-Stage Dockerfile
    · Docker Build and Publish Workflow (`docker-build-release.yml`)
    · Manifest Publish and Deployment Manifest Update
  TypeScript Package Publishing
  Python Package Publishing
  Canary Tests for Third-Party SDK Compatibility
  Quality Gates and Conditional Execution

## · Release Management  (L11226)
  源文件: .agents/skills/phoenix-release-please/SKILL.md, .github/workflows/cost-sync.yml, .github/workflows/helm-ci.yml, .github/workflows/playwright.yaml, .github/workflows/publish.yaml, .github/workflows/pypi-smoke-test.yml, .github/workflows/python-CI.yml, .github/workflows/python-all-platforms.yml, .github/workflows/release.yml, .github/workflows/sync-lockfile-release-pr.yml, .github/workflows/typescript-CI.yml, .github/workflows/update-phoenix-package-versions.yml
  Overview
  Release-Please Configuration
    · Package Configuration Map
  Release Workflow
  Versioning Decisions
  Publishing Process
    · Python Packages
    · Docker Image Releases
  Version Manifest and Changelog Linkage
  Dev Preview Versioning Scheme
  Migration Documentation

## · Kubernetes Deployment  (L11571)
  源文件: .github/workflows/helm-release.yaml, docs/phoenix/datasets-and-experiments/how-to-experiments/using-evaluators.mdx, docs/phoenix/evaluation/llm-evals.mdx, docs/phoenix/production-guide.mdx, docs/phoenix/resources/frequently-asked-questions.mdx, docs/phoenix/sdk-api-reference/typescript/packages/phoenix-client/spans.mdx, docs/phoenix/self-hosting.mdx, docs/phoenix/self-hosting/architecture.mdx, docs/phoenix/self-hosting/configuration.mdx, docs/phoenix/self-hosting/configuration/using-amazon-aurora.mdx, docs/phoenix/self-hosting/configuration/using-azure-managed-identity.mdx, docs/phoenix/self-hosting/security/network-security.mdx
  Deployment Methods
    · Overview Diagram of Deployment Methods and Paths
  Helm Chart Architecture
    · Chart Structure and Interdependencies
    · Deployment Resource Provisioning Flow
  Database Persistence Strategies
    · Persistence Strategy Matrix
    · Strategy 1: SQLite with Persistent Storage
    · Strategy 2: Built-in PostgreSQL
    · Strategy 3: External PostgreSQL Database
    · Strategy 4: SQLite In-Memory (Testing/Demo Only)
    · Persistence Validation
  Configuration Management
    · ConfigMap: phoenix-configmap
    · Secret: phoenix-secret
  Networking and Ingress
    · Service Configuration
    · Ingress Configuration
  Authentication Configuration
    · Local Authentication
    · OAuth2 Authorization Server and Providers
    · LDAP / Active Directory Support
  Health Checks and Probes
  Operational Considerations
    · Memory Management (Span Queue)
    · Air-Gapped and External Resource Control
    · Security and Non-Root Execution
  System Components: Natural Language to Code Entity Mapping
    · Deployment Components and Corresponding Code Entities
    · Authentication Configuration Code Mapping
  References

## · API Reference Documentation  (L12081)
  源文件: .github/workflows/generate-sitemap.yml, .readthedocs.yaml, api_reference/.gitignore, api_reference/Makefile, api_reference/README.md, api_reference/make.bat, api_reference/requirements.txt, api_reference/source/_static/custom.css, api_reference/source/_static/logo.png, api_reference/source/_static/switcher.json, api_reference/source/_templates/custom_sidebar.html, api_reference/source/conf.py
  Purpose and Scope
  Sphinx-based Python API Reference
    · Configuration
    · Cleaning Doc Output
    · Diagram: Sphinx Documentation Generation Workflow
  ReadTheDocs Hosting
    · ReadTheDocs Configuration
  Versioning Strategy
    · How Version Matching Works
  Maintaining and Regenerating Reference Pages
    · Updating Docstrings and Documentation Content
    · Generating API Documentation Files
    · Sitemap Generation and CI Automation
    · Diagram: Sitemap Generation Workflow
  Mintlify Documentation Site (docs.json-driven)
    · Diagram: Natural Language to Code Entity Mapping for Phoenix API Reference Generation
    · Diagram: Bridging Mintlify Docs.json Configuration to Sitemap and Doc Pages

## · Glossary  (L12419)
  源文件: .github/pull_request_template.md, .github/workflows/generate-sitemap.yml, .github/workflows/release.yml, .github/workflows/update-phoenix-package-versions.yml, .release-please-manifest.json, CHANGELOG.md, cspell.json, docs.json, docs/phoenix/cookbook/guardrails/jailbreak-and-prompt-injection-defense.mdx, docs/phoenix/integrations.mdx, docs/phoenix/integrations/llm-providers/cohere.mdx, docs/phoenix/integrations/llm-providers/cohere/cohere-tracing.mdx
  Phoenix Core Concepts
    · Phoenix
    · Span  
    · Trace  
    · Project  
    · Dataset  
    · Experiment  
    · Evaluator  
    · Annotation  
    · Session  
  Monorepo Structure  
    · Python Packages
    · TypeScript Packages
  Server Architecture Highlights
    · FastAPI Application  
    · GraphQL API  
    · OTLP Ingestion  
    · Database Layer  
    · Cost Tracking System  
  Important Data Flows and Relationships
    · Data Flow from OTLP Ingestion to Database Storage
    · GraphQL Query Processing Pipeline for Project Data
  Bridging Natural Language Terms to Core Code Entities in Phoenix