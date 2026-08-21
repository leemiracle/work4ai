# Skeleton: manifest（33 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 6KB | 2 | ~5 | 13 |
| 2 | Getting Started | L157 | 10KB | 2 | ~1 | 34 |
| 3 | Deployment | L339 | 8KB | 2 | ~3 | 16 |
| 4 | Architecture | L478 | 7KB | 2 | ~2 | 20 |
| 5 | Backend (NestJS) | L632 | 11KB | 3 | ~2 | 18 |
| 6 | Frontend (SolidJS Dashboard) | L830 | 10KB | 2 | ~2 | 21 |
| 7 | Agent Integration | L986 | 9KB | 2 | ~5 | 25 |
| 8 | Shared Package | L1186 | 8KB | 2 | ~2 | 21 |
| 9 | Request Routing | L1344 | 10KB | 2 | ~2 | 14 |
| 10 | Scoring Engine | L1512 | 10KB | 2 | ~4 | 19 |
| 11 | Proxy Pipeline | L1682 | 12KB | 2 | ~1 | 20 |
| 12 | Fallback and Resilience | L1822 | 10KB | 2 | ~2 | 17 |
| 13 | Provider Management | L1958 | 13KB | 2 | ~6 | 21 |
| 14 | Model Discovery and Pricing | L2148 | 9KB | 2 | ~2 | 17 |
| 15 | Model Discovery Pipeline | L2299 | 11KB | 2 | ~2 | 18 |
| 16 | Pricing Synchronization | L2459 | 10KB | 2 | ~2 | 14 |
| 17 | Free Models | L2623 | 8KB | 2 | ~1 | 12 |
| 18 | Analytics and Observability | L2773 | 10KB | 2 | ~2 | 17 |
| 19 | Analytics API | L2942 | 12KB | 3 | ~2 | 23 |
| 20 | OTLP Ingestion and SSE | L3133 | 12KB | 2 | ~1 | 20 |
| 21 | Notifications and Alerts | L3309 | 12KB | 2 | ~2 | 19 |
| 22 | Authentication and Security | L3511 | 8KB | 2 | ~2 | 16 |
| 23 | Better Auth and Session Management | L3662 | 11KB | 2 | ~2 | 26 |
| 24 | Agent API Key Authentication | L3840 | 8KB | 2 | ~3 | 19 |
| 25 | Security Hardening | L3989 | 9KB | 2 | ~1 | 15 |
| 26 | Database and Persistence | L4140 | 7KB | 2 | ~2 | 12 |
| 27 | Entity Schema | L4284 | 12KB | 2 | ~3 | 21 |
| 28 | Database Configuration and Migrations | L4447 | 10KB | 2 | ~0 | 20 |
| 29 | Development Guide | L4589 | 5KB | 2 | ~4 | 15 |
| 30 | Environment Setup | L4728 | 9KB | 3 | ~6 | 20 |
| 31 | Testing Infrastructure | L4925 | 9KB | 2 | ~1 | 16 |
| 32 | CI/CD and Release Process | L5088 | 8KB | 2 | ~2 | 12 |
| 33 | Glossary | L5229 | 12KB | 2 | ~5 | 29 |


## · Overview  (L6)
  源文件: .changeset/README.md, .changeset/config.json, .github/dependabot.yml, .gitignore, CLAUDE.md, CONTRIBUTING.md, README.md, package-lock.json, package.json, packages/backend/package.json, packages/manifest/CHANGELOG.md, packages/manifest/package.json
    · Core Value Proposition
    · Deployment Modes
    · Monorepo Structure
    · System Architecture Overview
    · Code Entity Mapping
    · Child Pages

## · Getting Started  (L157)
  源文件: .changeset/README.md, .changeset/config.json, .github/dependabot.yml, .github/workflows/docker-smoke.yml, .github/workflows/docker.yml, .gitignore, CLAUDE.md, CONTRIBUTING.md, README.md, docker/.env.example, docker/DOCKER_README.md, docker/Dockerfile
  Deployment Modes
  Self-Hosted Installation (Docker)
    · Quick Start Script
    · Manual Configuration
  Initial Configuration & Setup Wizard
    · Setup Flow
    · Request Lifecycle and Code Entity Mapping
  Agent Integration
    · Virtual Model: `manifest/auto`
    · Authentication
  Local Development (`devMode`)
    · Prerequisites
    · Development Setup
    · Loopback Bypass

## · Deployment  (L339)
  源文件: .github/workflows/docker-smoke.yml, .github/workflows/docker.yml, docker/.env.example, docker/DOCKER_README.md, docker/Dockerfile, docker/docker-compose.yml, docker/install.sh, packages/backend/.env.example, packages/backend/src/analytics/services/agent-analytics.service.ts, packages/backend/src/common/common.module.ts, packages/backend/src/common/services/manifest-runtime.service.ts, packages/backend/src/config/app.config.spec.ts
  Deployment Options
    · 1. Self-Hosted Docker (Primary)
    · 2. Managed Cloud Service
    · 3. Railway Deployment
  Infrastructure Architecture
  Configuration
    · Environment Variables
    · Ollama Integration
  Data Flow and Initialization
  Production Hardening

## · Architecture  (L478)
  源文件: .changeset/README.md, .changeset/config.json, .github/dependabot.yml, .gitignore, CLAUDE.md, CONTRIBUTING.md, README.md, package-lock.json, package.json, packages/backend/package.json, packages/backend/src/app.module.ts, packages/backend/src/common/filters/spa-fallback.filter.spec.ts
    · System Overview
    · Component Relationship Diagram
    · Request Lifecycle: Agent to Provider
    · Subsystems

## · Backend (NestJS)  (L632)
  源文件: packages/backend/src/app.module.ts, packages/backend/src/auth/session.guard.spec.ts, packages/backend/src/auth/session.guard.ts, packages/backend/src/common/filters/spa-fallback.filter.spec.ts, packages/backend/src/common/filters/spa-fallback.filter.ts, packages/backend/src/common/guards/api-key.guard.ts, packages/backend/src/common/utils/frontend-path.spec.ts, packages/backend/src/common/utils/frontend-path.ts, packages/backend/src/common/utils/local-ip.ts, packages/backend/src/main.ts, packages/backend/src/otlp/guards/agent-key-auth.guard.spec.ts, packages/backend/src/otlp/guards/agent-key-auth.guard.ts
  Application Lifecycle & Bootstrap
    · Bootstrap Sequence
    · Security Middleware
  Module Structure
    · AppModule Composition
    · Code Entity Mapping: Application Composition
  Authentication & Guards
    · Global Guards
    · Agent Authentication
    · Code Entity Mapping: Authentication Flow
  Frontend Integration (SPA Fallback)
    · SpaFallbackFilter
    · ServeStatic Configuration
    · Code Entity Mapping: SPA Routing Flow
  OAuth Integration
    · OpenaiOauthService

## · Frontend (SolidJS Dashboard)  (L830)
  源文件: packages/frontend/index.html, packages/frontend/public/example-messages.svg, packages/frontend/public/example-overview.svg, packages/frontend/public/fonts/boxicons/boxicons-duotone.min.css, packages/frontend/public/fonts/boxicons/boxicons-duotone.woff2, packages/frontend/public/og-image.png, packages/frontend/src/App.tsx, packages/frontend/src/components/VersionIndicator.tsx, packages/frontend/src/index.tsx, packages/frontend/src/pages/MessageLog.tsx, packages/frontend/src/pages/Overview.tsx, packages/frontend/src/services/api.ts
  Component Architecture and Data Flow
    · Page Structure
    · Real-Time Updates (SSE)
  Core Routing Configuration
    · Tier and Specificity Management
    · Provider Integration
  Message Logging and Analytics
    · Implementation Details
  Authentication and Security

## · Agent Integration  (L986)
  源文件: .changeset/README.md, .changeset/config.json, .github/dependabot.yml, .gitignore, CLAUDE.md, CONTRIBUTING.md, README.md, package-lock.json, package.json, packages/backend/package.json, packages/backend/src/otlp/services/api-key.service.spec.ts, packages/backend/src/otlp/services/api-key.service.ts
  Supported Agent Types
  The `manifest/auto` Virtual Model
  Agent API Keys (`mnfst_*`)
    · Key Characteristics
    · UI Onboarding Logic
  Agent Integration Details
    · OpenClaw Integration
    · Claude Code Integration
  Framework and SDK Integration
    · OpenAI SDK (Node.js/Python)
    · Vercel AI SDK
    · LangChain
  Development Mode Loopback Bypass

## · Shared Package  (L1186)
  源文件: packages/backend/src/common/utils/crypto.util.ts, packages/frontend/src/components/FallbackList.tsx, packages/frontend/src/components/ModelParamsDialog.tsx, packages/frontend/src/pages/RoutingTierCard.tsx, packages/frontend/src/services/routing-utils.ts, packages/frontend/src/styles/routing.css, packages/frontend/tests/components/FallbackList.test.tsx, packages/frontend/tests/components/ProviderKeyForm.test.tsx, packages/frontend/tests/components/RoutingModals.test.tsx, packages/frontend/tests/pages/RoutingActions.test.ts, packages/frontend/tests/pages/RoutingPanels.test.tsx, packages/frontend/tests/pages/RoutingTierCard.test.tsx
  Package Architecture
  Data Flow: Model Discovery to Routing
    · System Entity Mapping
  Key Utilities
    · Provider Inference Engine
    · Subscription Configurations
  Routing Logic and Model Routes
    · Routing Action Flow
  Reasoning and Thinking Defaults

## · Request Routing  (L1344)
  源文件: packages/backend/src/routing/dto/resolve-response.ts, packages/backend/src/routing/proxy/__tests__/proxy-fallback.service.spec.ts, packages/backend/src/routing/proxy/__tests__/proxy-response-handler.spec.ts, packages/backend/src/routing/proxy/__tests__/proxy.controller.spec.ts, packages/backend/src/routing/proxy/__tests__/proxy.service.spec.ts, packages/backend/src/routing/proxy/proxy-fallback.service.ts, packages/backend/src/routing/proxy/proxy-response-handler.ts, packages/backend/src/routing/proxy/proxy-types.ts, packages/backend/src/routing/proxy/proxy.controller.ts, packages/backend/src/routing/proxy/proxy.service.ts, packages/backend/src/routing/resolve/__tests__/resolve.service.spec.ts, packages/backend/src/routing/resolve/resolve.service.ts
  Routing Architecture
    · Request Flow Overview
    · Code Entity Space Mapping
  Core Components
    · [Scoring Engine](#3.1)
    · [Proxy Pipeline](#3.2)
    · [Fallback and Resilience](#3.3)
    · [Provider Management](#3.4)
  Routing Tiers Overview
  Proxy Request Lifecycle

## · Scoring Engine  (L1512)
  源文件: packages/backend/src/common/utils/baseline-cost.spec.ts, packages/backend/src/common/utils/baseline-cost.ts, packages/backend/src/database/migrations/1784000000000-DropLegacyRoutingColumns.spec.ts, packages/backend/src/database/migrations/1784000000000-DropLegacyRoutingColumns.ts, packages/backend/src/routing/routing-core/__tests__/provider.service.spec.ts, packages/backend/src/routing/routing-core/__tests__/routing-invalidation.service.spec.ts, packages/backend/src/routing/routing-core/__tests__/tier-auto-assign.service.spec.ts, packages/backend/src/scoring/__tests__/agent-envelope-regression.spec.ts, packages/backend/src/scoring/__tests__/envelope-peeler.spec.ts, packages/backend/src/scoring/__tests__/score-request-advanced.spec.ts, packages/backend/src/scoring/__tests__/score-request.spec.ts, packages/backend/src/scoring/__tests__/specificity-signals.spec.ts
  Classification Tiers
  Scoring Architecture
    · Data Flow Diagram: Request to Tier
  Scoring Dimensions
    · Keyword Analysis (`KeywordTrie`)
    · Structural Dimensions
  Special Logic and Overrides
    · Short-Message Fast Path
    · Formal Logic Override
    · Specificity Detector and Signal Boosts
  Normalization and Momentum
    · Sigmoid Normalization
    · Session Momentum
  Text Pre-processing
    · Envelope Peeling

## · Proxy Pipeline  (L1682)
  源文件: .changeset/fix-messages-cache-token-roundtrip.md, packages/backend/src/common/errors/__tests__/error-codes.spec.ts, packages/backend/src/common/errors/error-codes.ts, packages/backend/src/routing/proxy/__tests__/anthropic-cache-control-roundtrip.spec.ts, packages/backend/src/routing/proxy/__tests__/anthropic-messages-adapter.spec.ts, packages/backend/src/routing/proxy/__tests__/proxy-exception.filter.spec.ts, packages/backend/src/routing/proxy/__tests__/proxy-friendly-response.spec.ts, packages/backend/src/routing/proxy/__tests__/proxy-message-dedup.spec.ts, packages/backend/src/routing/proxy/__tests__/proxy-rate-limiter.spec.ts, packages/backend/src/routing/proxy/__tests__/proxy-response-handler.spec.ts, packages/backend/src/routing/proxy/__tests__/proxy.controller.spec.ts, packages/backend/src/routing/proxy/__tests__/proxy.service.spec.ts
  1. Request Lifecycle Overview
    · Code Entity Flow
  2. Rate Limiting and Concurrency
  3. Proxy Service Orchestration
    · Key Implementation Details
  4. Provider Adapters and Protocol Translation
  5. Cache Management & Message Recording
    · Thinking and Signature Caches
    · Proxy Message Recorder
  6. Error Handling and Resilience

## · Fallback and Resilience  (L1822)
  源文件: packages/backend/src/common/utils/hash.util.spec.ts, packages/backend/src/common/utils/hash.util.ts, packages/backend/src/database/migrations/1771500000000-HashApiKeys.ts, packages/backend/src/database/migrations/1773900000000-AddKeyPrefixIndex.spec.ts, packages/backend/src/database/migrations/1773900000000-AddKeyPrefixIndex.ts, packages/backend/src/routing/dto/resolve-response.ts, packages/backend/src/routing/proxy/__tests__/fallback-status-codes.spec.ts, packages/backend/src/routing/proxy/__tests__/proxy-fallback.service.spec.ts, packages/backend/src/routing/proxy/fallback-status-codes.ts, packages/backend/src/routing/proxy/proxy-error-sanitizer.spec.ts, packages/backend/src/routing/proxy/proxy-error-sanitizer.ts, packages/backend/src/routing/proxy/proxy-fallback.service.ts
  Fallback Chain Mechanism
    · Iteration Process
    · Fallback Execution Flow
  Credential Rotation
  Error Handling and Sanitization
    · Transport Errors
    · Sanitization
  Implementation Details
    · Key Functions and Classes

## · Provider Management  (L1958)
  源文件: .changeset/copilot-codex-routing.md, packages/backend/src/common/constants/openai-models.ts, packages/backend/src/common/constants/subscription-clients.ts, packages/backend/src/model-prices/model-prices.module.ts, packages/backend/src/routing/custom-provider/custom-provider.module.ts, packages/backend/src/routing/custom-provider/custom-provider.service.spec.ts, packages/backend/src/routing/custom-provider/custom-provider.service.ts, packages/backend/src/routing/minimax-oauth.controller.spec.ts, packages/backend/src/routing/minimax-oauth.service.spec.ts, packages/backend/src/routing/oauth/minimax-oauth-helpers.spec.ts, packages/backend/src/routing/oauth/minimax-oauth-helpers.ts, packages/backend/src/routing/oauth/minimax-oauth.service.spec.ts
  Provider Credential Management
    · ProviderKeyService & Security
    · Authentication Types
  Routing and Tier Assignment
    · TierAutoAssignService
    · Provider Endpoints Map
    · Custom Providers and Aliases
  Subscription Providers (OAuth & Device Flows)
    · Supported Subscription Flows
    · Code Entity Mapping: Subscription Auth
  Implementation Details
    · Provider Definitions
    · Request Forwarding and SSRF Protection

## · Model Discovery and Pricing  (L2148)
  源文件: packages/backend/src/database/database-seeder.service.spec.ts, packages/backend/src/database/database-seeder.service.ts, packages/backend/src/database/models-dev-sync.service.spec.ts, packages/backend/src/database/models-dev-sync.service.ts, packages/backend/src/database/pricing-sync.service.spec.ts, packages/backend/src/database/pricing-sync.service.ts, packages/backend/src/model-discovery/filter-non-chat-models.spec.ts, packages/backend/src/model-discovery/known-model-prices.spec.ts, packages/backend/src/model-discovery/known-model-prices.ts, packages/backend/src/model-discovery/model-fallback.spec.ts, packages/backend/src/model-discovery/model-fallback.ts, packages/backend/src/model-discovery/provider-model-fetcher.service.spec.ts
  System Overview
    · Core Entity Mapping
  Model Discovery Pipeline
  Pricing Synchronization
  Free Models
  Data Flow and Persistence
    · Key Services

## · Model Discovery Pipeline  (L2299)
  源文件: packages/backend/src/database/models-dev-sync.service.spec.ts, packages/backend/src/database/models-dev-sync.service.ts, packages/backend/src/model-discovery/anthropic-subscription-probe.spec.ts, packages/backend/src/model-discovery/anthropic-subscription-probe.ts, packages/backend/src/model-discovery/filter-non-chat-models.spec.ts, packages/backend/src/model-discovery/known-model-prices.spec.ts, packages/backend/src/model-discovery/known-model-prices.ts, packages/backend/src/model-discovery/model-discovery.service.spec.ts, packages/backend/src/model-discovery/model-discovery.service.ts, packages/backend/src/model-discovery/model-fallback.spec.ts, packages/backend/src/model-discovery/model-fallback.ts, packages/backend/src/model-discovery/provider-model-fetcher.service.spec.ts
  1. Discovery Lifecycle Orchestration
    · Discovery Workflow
    · Code Entity Interaction: Discovery Logic
  2. Provider Model Fetching
    · Normalization and Filtering
  3. Fallback Mechanisms
    · Model ID Normalization
  4. Capability and Metadata Enrichment
    · Data Flow: Discovery to Enrichment
    · Key Enrichment Steps

## · Pricing Synchronization  (L2459)
  源文件: packages/backend/src/database/database-seeder.service.spec.ts, packages/backend/src/database/database-seeder.service.ts, packages/backend/src/database/pricing-sync.service.spec.ts, packages/backend/src/database/pricing-sync.service.ts, packages/backend/src/database/quality-score.util.spec.ts, packages/backend/src/database/quality-score.util.ts, packages/backend/src/model-prices/model-name-normalizer.spec.ts, packages/backend/src/model-prices/model-name-normalizer.ts, packages/backend/src/model-prices/model-prices.controller.spec.ts, packages/backend/src/model-prices/model-prices.controller.ts, packages/backend/src/model-prices/model-prices.service.spec.ts, packages/backend/src/model-prices/model-prices.service.ts
  Data Flow Architecture
    · High-Level Pricing Pipeline
  Key Components
    · PricingSyncService
    · ModelsDevSyncService
    · ModelPricingCacheService
  Model Name Normalization
    · Normalization Sequence
  Quality Scores and Seeding
    · Quality Score Calculation
    · DatabaseSeederService
  Pricing Format and API
    · Model Prices Response Structure

## · Free Models  (L2623)
  源文件: packages/frontend/public/icons/gemini.svg, packages/frontend/public/icons/groq.svg, packages/frontend/src/components/CostByModelTable.tsx, packages/frontend/src/components/ModelPricesFilterBar.tsx, packages/frontend/src/pages/FreeModels.tsx, packages/frontend/src/pages/Help.tsx, packages/frontend/src/pages/ModelPrices.tsx, packages/frontend/src/services/cursor-pagination.ts, packages/frontend/src/services/pagination.ts, packages/frontend/tests/components/ModelPricesFilterBar.test.tsx, packages/frontend/tests/pages/FreeModels.test.tsx, packages/frontend/tests/pages/ModelPrices.test.tsx
  Architecture and Data Flow
    · System Components Diagram
  Backend Implementation
    · FreeModelsSyncService
    · FreeModelsService
    · API Endpoints
  Frontend Integration
    · Connection Logic
    · Code-to-Entity Mapping: Frontend UI
  Routing Integration
    · Pricing Visualization
    · Local vs Cloud Restrictions
    · Analytics and Costs

## · Analytics and Observability  (L2773)
  源文件: packages/backend/src/analytics/services/aggregation.service.spec.ts, packages/backend/src/analytics/services/aggregation.service.ts, packages/backend/src/analytics/services/message-details.service.spec.ts, packages/backend/src/analytics/services/message-details.service.ts, packages/backend/src/analytics/services/messages-query.service.spec.ts, packages/backend/src/analytics/services/messages-query.service.ts, packages/backend/src/analytics/services/timeseries-queries.service.spec.ts, packages/backend/src/analytics/services/timeseries-queries.service.ts, packages/backend/src/database/database.module.ts, packages/backend/src/entities/agent-message.entity.ts, packages/backend/src/routing/proxy/__tests__/proxy-message-recorder.spec.ts, packages/backend/src/routing/proxy/proxy-message-recorder.ts
    · System Overview
  Analytics API
  OTLP Ingestion and SSE
  Notifications and Alerts
  Dialect-Aware Analytics

## · Analytics API  (L2942)
  源文件: packages/backend/src/analytics/analytics.module.ts, packages/backend/src/analytics/controllers/messages.controller.spec.ts, packages/backend/src/analytics/controllers/messages.controller.ts, packages/backend/src/analytics/services/agent-duplication.service.spec.ts, packages/backend/src/analytics/services/agent-duplication.service.ts, packages/backend/src/analytics/services/aggregation.service.spec.ts, packages/backend/src/analytics/services/aggregation.service.ts, packages/backend/src/analytics/services/messages-query.service.spec.ts, packages/backend/src/analytics/services/messages-query.service.ts, packages/backend/src/analytics/services/query-helpers.spec.ts, packages/backend/src/analytics/services/query-helpers.ts, packages/backend/src/analytics/services/timeseries-queries.service.spec.ts
  Architecture and Data Flow
    · System Components Mapping
  REST Endpoints
    · Dashboard Overview
    · Time-series Data
    · Telemetry Logs
  Single Source of Truth for Message Projection
  SQL Utilities
    · Key Postgres SQL Functions
  Implementation Details
    · Aggregation Service
    · Agent Duplication Service
    · Timeseries Queries Service

## · OTLP Ingestion and SSE  (L3133)
  源文件: packages/backend/src/analytics/services/message-details.service.spec.ts, packages/backend/src/analytics/services/message-details.service.ts, packages/backend/src/common/constants/cache.constants.spec.ts, packages/backend/src/common/constants/cache.constants.ts, packages/backend/src/common/middleware/http-error-logger.middleware.spec.ts, packages/backend/src/common/middleware/http-error-logger.middleware.ts, packages/backend/src/common/utils/cost-calculator.spec.ts, packages/backend/src/common/utils/cost-calculator.ts, packages/backend/src/database/database.module.ts, packages/backend/src/database/migrations/1773800000000-FixNegativeCosts.spec.ts, packages/backend/src/database/migrations/1773800000000-FixNegativeCosts.ts, packages/backend/src/database/migrations/1782000000000-RetuneSpecificityMiscategorizedIndex.spec.ts
  OTLP Ingestion Pipeline
    · Data Flow Architecture
    · Authentication: AgentKeyAuthGuard
  Proxy Message Recording
    · Token and Cost Calculation
  Real-Time Updates (SSE)
    · IngestEventBusService
    · SSE Implementation
  Public Stats Endpoint
    · Data Aggregation Logic
  Implementation Detail: ProxyMessageRecorder
    · Key Logic

## · Notifications and Alerts  (L3309)
  源文件: packages/backend/src/common/utils/period.util.spec.ts, packages/backend/src/common/utils/period.util.ts, packages/backend/src/database/migrations/1771700000000-EmailProviderConfigs.ts, packages/backend/src/entities/email-provider-config.entity.ts, packages/backend/src/notifications/dto/set-email-provider.dto.ts, packages/backend/src/notifications/emails/reset-password.tsx, packages/backend/src/notifications/emails/test-email.tsx, packages/backend/src/notifications/emails/threshold-alert.tsx, packages/backend/src/notifications/emails/verify-email.tsx, packages/backend/src/notifications/notifications.controller.spec.ts, packages/backend/src/notifications/notifications.controller.ts, packages/backend/src/notifications/services/email-provider-config.service.spec.ts
  System Architecture
    · Data Flow and Service Interaction
  Scheduled Alerts (NotificationCronService)
  Hard Limits (LimitCheckService)
  Email Delivery System
    · Pluggable Providers
    · React Email Templates
  Frontend Management (Limits Page)
  Period Calculation
  Implementation Mapping

## · Authentication and Security  (L3511)
  源文件: packages/backend/src/analytics/services/agent-analytics.service.spec.ts, packages/backend/src/auth/auth.instance.spec.ts, packages/backend/src/auth/auth.instance.ts, packages/backend/src/auth/session.guard.spec.ts, packages/backend/src/auth/session.guard.ts, packages/backend/src/common/guards/api-key.guard.spec.ts, packages/backend/src/common/guards/api-key.guard.ts, packages/backend/src/common/utils/local-ip.ts, packages/backend/src/main.ts, packages/backend/src/notifications/services/notification-rules.service.spec.ts, packages/backend/src/notifications/services/notification-rules.service.ts, packages/backend/src/otlp/guards/agent-key-auth.guard.spec.ts
  System Authentication Overview
    · Authentication Flow and Code Entities
  Better Auth and Session Management
  Agent API Key Authentication
  Security Hardening
    · Security Architecture Diagram
  Comparison of Auth Mechanisms

## · Better Auth and Session Management  (L3662)
  源文件: packages/backend/src/analytics/services/agent-analytics.service.spec.ts, packages/backend/src/auth/auth.instance.spec.ts, packages/backend/src/auth/auth.instance.ts, packages/backend/src/common/guards/api-key.guard.spec.ts, packages/backend/src/notifications/services/notification-rules.service.spec.ts, packages/backend/src/notifications/services/notification-rules.service.ts, packages/backend/src/setup/setup.controller.spec.ts, packages/backend/src/setup/setup.controller.ts, packages/backend/src/setup/setup.service.spec.ts, packages/backend/src/setup/setup.service.ts, packages/backend/test/setup.e2e-spec.ts, packages/frontend/src/components/AuthGuard.tsx
  Overview
    · Authentication Request Lifecycle
  Better Auth Configuration
    · Database Integration
    · Supported Providers
    · Security Features
  Setup Wizard Flow
    · SetupService and First Admin Creation
    · Frontend Guards and Logic
  Session Management Logic
    · Dashboard Authentication
    · Email Services
  Summary of Differences

## · Agent API Key Authentication  (L3840)
  源文件: packages/backend/src/auth/session.guard.spec.ts, packages/backend/src/auth/session.guard.ts, packages/backend/src/common/guards/api-key.guard.ts, packages/backend/src/common/utils/hash.util.spec.ts, packages/backend/src/common/utils/hash.util.ts, packages/backend/src/common/utils/local-ip.ts, packages/backend/src/database/migrations/1771500000000-HashApiKeys.ts, packages/backend/src/database/migrations/1773900000000-AddKeyPrefixIndex.spec.ts, packages/backend/src/database/migrations/1773900000000-AddKeyPrefixIndex.ts, packages/backend/src/main.ts, packages/backend/src/otlp/guards/agent-key-auth.guard.spec.ts, packages/backend/src/otlp/guards/agent-key-auth.guard.ts
  Implementation Overview
    · Key Characteristics
    · Data Flow: Authentication Request
  Core Components
    · AgentKeyAuthGuard
    · ApiKeyGeneratorService
  Key Security Entities
  Technical Reference Table

## · Security Hardening  (L3989)
  源文件: packages/backend/src/common/utils/detect-self-hosted.spec.ts, packages/backend/src/common/utils/detect-self-hosted.ts, packages/backend/src/common/utils/hash.util.spec.ts, packages/backend/src/common/utils/hash.util.ts, packages/backend/src/common/utils/secret-scrub.spec.ts, packages/backend/src/common/utils/secret-scrub.ts, packages/backend/src/common/utils/url-validation.spec.ts, packages/backend/src/common/utils/url-validation.ts, packages/backend/src/database/migrations/1771500000000-HashApiKeys.ts, packages/backend/src/database/migrations/1773900000000-AddKeyPrefixIndex.spec.ts, packages/backend/src/database/migrations/1773900000000-AddKeyPrefixIndex.ts, packages/backend/src/routing/custom-provider/probe-error.spec.ts
  SSRF Protection and URL Validation
    · URL Validation Logic Flow
  Credential Security: Hashing and Encryption
    · Agent API Key Hashing
    · Provider Credential Encryption
  Proxy Error Sanitization
  HTTP Security and Middleware
    · Helmet and CSP
    · Rate Limiting
    · Auth Guards and Loopback Bypass

## · Database and Persistence  (L4140)
  源文件: packages/backend/src/analytics/services/message-details.service.spec.ts, packages/backend/src/analytics/services/message-details.service.ts, packages/backend/src/database/database.module.ts, packages/backend/src/database/datasource.ts, packages/backend/src/entities/agent-message.entity.ts, packages/backend/src/routing/proxy/__tests__/proxy-message-recorder.spec.ts, packages/backend/src/routing/proxy/proxy-message-recorder.ts, packages/frontend/src/components/MessageDetails.tsx, packages/frontend/src/components/MessageDetailsSections.tsx, packages/frontend/src/services/api/messages.ts, packages/frontend/src/styles/data.css, packages/frontend/tests/components/MessageDetails.test.tsx
  Architecture Overview
    · Data Interaction Flow
  Entity Schema
  Database Configuration
  Migrations and Seeding
    · Automated Lifecycle

## · Entity Schema  (L4284)
  源文件: packages/backend/src/analytics/services/message-details.service.spec.ts, packages/backend/src/analytics/services/message-details.service.ts, packages/backend/src/database/database.module.ts, packages/backend/src/database/migrations/1772843035514-AddPerformanceIndexes.ts, packages/backend/src/database/migrations/1772940000000-DropRedundantIndexes.spec.ts, packages/backend/src/database/migrations/1772940000000-DropRedundantIndexes.ts, packages/backend/src/database/migrations/1772960000000-DropUnusedIndexes.spec.ts, packages/backend/src/database/migrations/1772960000000-DropUnusedIndexes.ts, packages/backend/src/database/migrations/1782200000000-AddAgentSoftDelete.spec.ts, packages/backend/src/database/migrations/1782200000000-AddAgentSoftDelete.ts, packages/backend/src/entities/agent-api-key.entity.ts, packages/backend/src/entities/agent-log.entity.ts
  Multi-Tenant Data Model
    · Natural Language to Code Entity Mapping
  Core Entities
    · 1. Identity and Access
    · 2. Provider and Routing Configuration
    · 3. Telemetry and Analytics
    · 4. Notifications and Alerts
  Data Flow: Message Recording
  Implementation Details
    · Security and Removal of SecurityEvent
    · Soft Deletion for Agents
    · Entity Summary Table

## · Database Configuration and Migrations  (L4447)
  源文件: packages/backend/src/database/database-seeder.service.spec.ts, packages/backend/src/database/database-seeder.service.ts, packages/backend/src/database/datasource.ts, packages/backend/src/database/migrations/1772960000000-PurgeNonCuratedModels.spec.ts, packages/backend/src/database/migrations/1772960000000-PurgeNonCuratedModels.ts, packages/backend/src/database/migrations/1774000000000-WidenKeyHashColumn.spec.ts, packages/backend/src/database/migrations/1774000000000-WidenKeyHashColumn.ts, packages/backend/src/database/migrations/1780000000000-DropComplexityRoutingFlag.spec.ts, packages/backend/src/database/migrations/1780000000000-DropComplexityRoutingFlag.ts, packages/backend/src/database/migrations/1782200000000-AddAgentSoftDelete.spec.ts, packages/backend/src/database/migrations/1782200000000-AddAgentSoftDelete.ts, packages/backend/src/database/migrations/1783000000000-AddModelRouteColumns.ts
  Data Persistence Strategy
    · Database Configuration (`datasource.ts`)
    · Database Entity Space to Code Mapping
  Migration and Seeding
    · Notable Migrations
    · DatabaseSeederService
  Pricing Data Synchronization
    · Synchronization Services

## · Development Guide  (L4589)
  源文件: .changeset/README.md, .changeset/config.json, .github/dependabot.yml, .gitignore, .husky/pre-commit, .prettierrc, CLAUDE.md, CONTRIBUTING.md, LICENSE, README.md, eslint.config.mjs, package-lock.json
  Monorepo Structure
  Development Workflow Overview
    · From Code to Deployment
  System Verification
    · Key Development Commands

## · Environment Setup  (L4728)
  源文件: .changeset/README.md, .changeset/config.json, .github/dependabot.yml, .gitignore, CLAUDE.md, CONTRIBUTING.md, README.md, package-lock.json, package.json, packages/backend/.env.example, packages/backend/package.json, packages/backend/src/common/common.module.ts
  Prerequisites
  Development Mode Requirements
    · MANIFEST_MODE=cloud Requirement
    · Fresh Database per Session
  Monorepo Build Pipeline
    · Project Structure
    · Core Commands
    · Build Pipeline Logic
  Configuring Personal AI Agents for Development
    · Testing with OpenClaw
    · Loopback Bypass (Auth)
    · Natural Language to Code Entity Space
  Backend Environment Configuration
    · Server Bootstrap Process
    · Request Flow to Entities

## · Testing Infrastructure  (L4925)
  源文件: .github/workflows/ci.yml, .github/workflows/release.yml, codecov.yml, packages/backend/src/app.module.ts, packages/backend/src/common/filters/spa-fallback.filter.spec.ts, packages/backend/src/common/filters/spa-fallback.filter.ts, packages/backend/src/common/utils/frontend-path.spec.ts, packages/backend/src/common/utils/frontend-path.ts, packages/backend/src/database/seed-messages.spec.ts, packages/backend/src/database/seed-messages.ts, packages/backend/test/helpers.ts, packages/backend/test/model-prices.e2e-spec.ts
  Test Orchestration and Runners
    · Cross-Package Execution
  Backend Testing (NestJS & Jest)
    · Unit Tests
    · E2E Test Suites
    · Data Entity to Test Entity Mapping
  Database Seeding and Test Data
    · Test Application Lifecycle
    · Deterministic Message Seeder
  Continuous Integration & Coverage
    · CI Workflow (`ci.yml`)
    · Codecov Integration
  Release Verification

## · CI/CD and Release Process  (L5088)
  源文件: .github/workflows/ci.yml, .github/workflows/docker-smoke.yml, .github/workflows/docker.yml, .github/workflows/release.yml, codecov.yml, docker/.env.example, docker/DOCKER_README.md, docker/Dockerfile, docker/docker-compose.yml, docker/install.sh, packages/backend/src/analytics/services/agent-analytics.service.ts, packages/frontend/package.json
  Continuous Integration (CI)
    · Workflow Orchestration
    · PostgreSQL Validation
    · Coverage and Quality
  Release Process
    · Version Detection and Tagging
    · The Docker Build Pipeline
    · Deployment and Smoke Testing
    · Image Signing and Verification

## · Glossary  (L5229)
  源文件: .changeset/README.md, .changeset/config.json, .changeset/copilot-codex-routing.md, .github/dependabot.yml, .gitignore, CLAUDE.md, CONTRIBUTING.md, README.md, package-lock.json, package.json, packages/backend/package.json, packages/backend/src/common/constants/openai-models.ts
  Routing Tiers and Scoring
    · Data Flow: Natural Language to Tier Assignment
  Agent Concepts
  Proxy Internals
    · Data Flow: Proxy Response Handling
  Authentication and Provider Types
  Infrastructure and Data Model