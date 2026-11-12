# Skeleton: aeon-agent（37 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 5KB | 2 | ~2 | 10 |
| 2 | Getting Started & Onboarding | L143 | 6KB | 2 | ~1 | 13 |
| 3 | Core Concepts & Terminology | L300 | 6KB | 2 | ~5 | 13 |
| 4 | Execution Engine & Orchestration | L447 | 5KB | 2 | ~1 | 6 |
| 5 | GitHub Actions Workflows | L570 | 7KB | 2 | ~1 | 6 |
| 6 | Skill Scheduling & Chaining | L719 | 6KB | 2 | ~2 | 9 |
| 7 | Notification & Post-Processing Pipeline | L855 | 7KB | 2 | ~2 | 15 |
| 8 | Skills System | L984 | 7KB | 3 | ~2 | 15 |
| 9 | Skill Definition & Lifecycle | L1146 | 8KB | 2 | ~3 | 17 |
| 10 | Research & Content Skills | L1319 | 8KB | 2 | ~4 | 30 |
| 11 | Dev & GitHub Skills | L1485 | 7KB | 2 | ~2 | 20 |
| 12 | Crypto & Market Skills | L1636 | 8KB | 2 | ~4 | 26 |
| 13 | Social & Productivity Skills | L1808 | 8KB | 2 | ~1 | 24 |
| 14 | Fleet & Instance Management Skills | L1966 | 7KB | 2 | ~2 | 15 |
| 15 | Self-Healing & Observability | L2121 | 5KB | 2 | ~1 | 9 |
| 16 | Heartbeat & Health Monitoring | L2250 | 6KB | 2 | ~2 | 8 |
| 17 | Skill Evals, Analytics & Repair | L2389 | 9KB | 2 | ~2 | 17 |
| 18 | Security & Update Management | L2571 | 8KB | 2 | ~1 | 11 |
| 19 | Memory & State Management | L2759 | 5KB | 2 | ~2 | 7 |
| 20 | Memory Directory Structure | L2874 | 6KB | 2 | ~2 | 8 |
| 21 | Issues Tracker & Reflect Skills | L3021 | 9KB | 2 | ~6 | 8 |
| 22 | Dashboard | L3200 | 5KB | 2 | ~1 | 8 |
| 23 | Dashboard UI Components | L3322 | 9KB | 2 | ~0 | 16 |
| 24 | Dashboard API Routes | L3520 | 9KB | 2 | ~2 | 24 |
| 25 | Integration Interfaces | L3690 | 5KB | 2 | ~0 | 19 |
| 26 | MCP Server (Claude Desktop & Claude Code) | L3856 | 6KB | 2 | ~1 | 14 |
| 27 | A2A Gateway (Agent-to-Agent Protocol) | L4014 | 7KB | 2 | ~5 | 15 |
| 28 | Soul & Identity Layer | L4190 | 6KB | 2 | ~2 | 7 |
| 29 | Public Site & Documentation | L4343 | 7KB | 2 | ~2 | 23 |
| 30 | Site Structure & Jekyll Configuration | L4501 | 7KB | 2 | ~4 | 18 |
| 31 | Content Generation & Syndication | L4680 | 7KB | 2 | ~1 | 12 |
| 32 | Scripts & Utilities Reference | L4826 | 7KB | 2 | ~4 | 22 |
| 33 | Prefetch & Sandbox Mitigation Scripts | L4978 | 7KB | 2 | ~2 | 12 |
| 34 | Skill Management CLI Tools | L5122 | 7KB | 2 | ~0 | 21 |
| 35 | Workflow Templates | L5292 | 5KB | 2 | ~2 | 14 |
| 36 | Available Templates & Customization | L5403 | 6KB | 2 | ~4 | 12 |
| 37 | Glossary | L5535 | 9KB | 2 | ~4 | 51 |


## · Overview  (L6)
  源文件: .github/workflows/chain-runner.yml, .outputs/.gitkeep, CLAUDE.md, README.md, SHOWCASE.md, aeon.yml, assets/architecture.jpg, assets/autonomy.jpg, assets/stack.jpg, skills/contributor-reward/SKILL.md
    · System Architecture & Logic Flow
    · Key Components
    · Data & Execution Mapping
    · Major Subsystems
    · Next Steps

## · Getting Started & Onboarding  (L143)
  源文件: README.md, aeon, aeon.yml, dashboard/app/api/auth/route.ts, dashboard/package-lock.json, dashboard/package.json, generate-skills-json, onboard, scripts/sync-upstream.sh, skills/auto-workflow/SKILL.md, skills/contributor-reward/SKILL.md, skills/onboard/SKILL.md
  Deployment Model: Zero Infrastructure
    · Data Flow: Configuration to Execution
  Step 1: Repository Initialization
  Step 2: Authentication & Secrets
    · Authentication Logic
  Step 3: Skill Configuration (`aeon.yml`)
    · Configuration Schema
  Step 4: The Onboard Validator
    · The `onboard` Skill
  Step 5: Maintenance & Upstream Sync
    · `generate-skills-json`
    · `sync-upstream.sh`

## · Core Concepts & Terminology  (L300)
  源文件: .github/workflows/aeon.yml, .github/workflows/chain-runner.yml, .github/workflows/messages.yml, .outputs/.gitkeep, CLAUDE.md, README.md, aeon.yml, export-skill, skills.json, skills/contributor-reward/SKILL.md, skills/distribute-tokens/SKILL.md, skills/skill-analytics/SKILL.md
  System Architecture Overview
    · Natural Language to Code Entity Mapping
  Core Terminology
    · 1. Skills
    · 2. The Soul
    · 3. Memory (Flat-File Database)
    · 4. Chains
    · 5. Reactive Triggers
  Data Flow & Execution Lifecycle
  The Exit Taxonomy

## · Execution Engine & Orchestration  (L447)
  源文件: .github/workflows/aeon.yml, .github/workflows/messages.yml, README.md, aeon.yml, skills/contributor-reward/SKILL.md, skills/skill-analytics/SKILL.md
  System Architecture
    · Execution Flow Diagram
  Core Workflows
    · 1. The Scheduler (`messages.yml`)
    · 2. The Execution Engine (`aeon.yml`)
  Scheduling & Chaining Logic
  Notification & Post-Processing
  Observability & Self-Healing

## · GitHub Actions Workflows  (L570)
  源文件: .github/workflows/aeon.yml, .github/workflows/chain-runner.yml, .github/workflows/messages.yml, .outputs/.gitkeep, CLAUDE.md, skills/skill-analytics/SKILL.md
  1. Skill Execution Engine (aeon.yml)
    · Trigger Types
    · Execution Lifecycle
    · Conflict-Resolution Commit Loop
  2. Scheduler & Message Poller (messages.yml)
    · Cron Matching & Dispatch
    · Inbound Messaging
  3. System Architecture Diagrams
    · From Natural Language to Code Execution
    · Sandbox & Side-Effect Patterns
  4. Workflow Constraints & Security
    · Sandbox Constraints
    · Secret Validation Logic

## · Skill Scheduling & Chaining  (L719)
  源文件: .github/workflows/aeon.yml, .github/workflows/chain-runner.yml, .github/workflows/messages.yml, .outputs/.gitkeep, CLAUDE.md, README.md, aeon.yml, skills/contributor-reward/SKILL.md, skills/skill-analytics/SKILL.md
  Scheduling Architecture
    · The Tick Cycle
    · Scheduling Data Flow: Config to Execution
  Skill Chaining
    · Execution Flow
    · Chain Definition Example
  Reactive Triggers
  Technical Implementation Details
    · Key Files and Components
    · Lifecycle of a Scheduled Run

## · Notification & Post-Processing Pipeline  (L855)
  源文件: .github/workflows/aeon.yml, .github/workflows/messages.yml, .gitignore, add-skill, memory/issues/INDEX.md, scripts/eval-audit, scripts/postprocess-devto.sh, scripts/postprocess-farcaster.sh, scripts/postprocess-replicate.sh, scripts/prefetch-xai.sh, scripts/skill-runs, skills/agent-buzz/SKILL.md
  Notification Delivery Architecture
    · Delivery Flow
  The Deferred Execution Pattern
    · Code Entity Mapping: Sandbox to Post-Processor
  Post-Processing Scripts
    · Dev.to Syndication
    · Farcaster (via Neynar)
    · Replicate & AI Generation
  Prefetching Logic
  Analytics & Health Notifications

## · Skills System  (L984)
  源文件: .gitignore, add-skill, export-skill, generate-skills-json, onboard, scripts/postprocess-farcaster.sh, scripts/sync-upstream.sh, skills.json, skills/auto-workflow/SKILL.md, skills/distribute-tokens/SKILL.md, skills/onboard/SKILL.md, skills/skill-update-check/SKILL.md
    · System Overview
    · Skill Definition and Discovery
    · Skill Installation and Security
    · Skill Categories
    · Meta-Skills and Fleet Management
    · Skill Lifecycle Management

## · Skill Definition & Lifecycle  (L1146)
  源文件: .gitignore, add-skill, export-skill, generate-skills-json, onboard, scripts/postprocess-farcaster.sh, scripts/sync-upstream.sh, skills.json, skills/auto-workflow/SKILL.md, skills/create-skill/SKILL.md, skills/distribute-tokens/SKILL.md, skills/onboard/SKILL.md
  Anatomy of a SKILL.md
    · Frontmatter and Metadata
    · Logic Gates and Variable Injection
    · Two-Phase Pattern: RESOLVE/EXECUTE
  Skill Registry and Compilation
    · skills.json Registry
    · generate-skills-json Compiler
  Skill Management Lifecycle
    · Installation: add-skill
    · Supply-Chain Pinning: skills.lock
    · Update Auditing: skill-update-check
    · Packaging: export-skill
  Technical Architecture Diagrams
    · From Natural Language to Code Entity (Installation)
    · Skill Execution & Logic Flow
  Meta-Skills for Lifecycle Management

## · Research & Content Skills  (L1319)
  源文件: .gitignore, add-skill, scripts/postprocess-farcaster.sh, skills/article/SKILL.md, skills/daily-routine/SKILL.md, skills/deep-research/SKILL.md, skills/defi-monitor/SKILL.md, skills/defi-overview/SKILL.md, skills/digest/SKILL.md, skills/fetch-tweets/SKILL.md, skills/fork-contributor-leaderboard/SKILL.md, skills/hacker-news-digest/SKILL.md
  Overview of Content Pipeline
  Data Flow: From Search to Synthesis
    · Natural Language to Code Entity Mapping
  Technical Implementation Details
    · 1. Source Credibility & Tiering
    · 2. Narrative Detection (Reddit)
    · 3. X/Twitter Clustering
  Syndication & Distribution
    · Key Functions in Syndication:
  Meta-Research: Fleet & Skill Leaderboards

## · Dev & GitHub Skills  (L1485)
  源文件: skills/auto-merge/SKILL.md, skills/changelog/SKILL.md, skills/code-health/SKILL.md, skills/github-issues/SKILL.md, skills/github-monitor/SKILL.md, skills/github-releases/SKILL.md, skills/github-trending/SKILL.md, skills/issue-triage/SKILL.md, skills/monitor-runners/SKILL.md, skills/pr-review/SKILL.md, skills/push-recap/SKILL.md, skills/repo-actions/SKILL.md
  Architecture & Data Flow
    · High-Level Data Flow
  Core Development Skills
    · GitHub Monitor & Triage
    · Activity Synthesis
    · Repository Maintenance & Growth
  Implementation Details
    · State Collection Patterns
    · Security & Safety Gates
    · Memory Integration

## · Crypto & Market Skills  (L1636)
  源文件: export-skill, skills.json, skills/action-converter/SKILL.md, skills/article/SKILL.md, skills/deal-flow/SKILL.md, skills/defi-monitor/SKILL.md, skills/distribute-tokens/SKILL.md, skills/fork-contributor-leaderboard/SKILL.md, skills/hacker-news-digest/SKILL.md, skills/monitor-kalshi/SKILL.md, skills/monitor-kalshi/watchlist.md, skills/morning-brief/SKILL.md
  Architecture & Data Flow
    · Market Intelligence Pipeline
  On-Chain Monitoring & Treasury
    · On-Chain Monitor
    · Token Distribution
  Market Analysis & Signal Detection
    · Token Movers
    · Prediction Markets (Kalshi & Polymarket)
  Meta-Crypto Skills: Leaderboards
  Summary Table of Crypto Skills

## · Social & Productivity Skills  (L1808)
  源文件: images/.gitkeep, scripts/postprocess-admanage-create.sh, scripts/postprocess-admanage.sh, skills/action-converter/SKILL.md, skills/aixbt-pulse/SKILL.md, skills/channel-recap/SKILL.md, skills/create-campaign/SKILL.md, skills/create-campaign/config.example.yaml, skills/evening-recap/SKILL.md, skills/farcaster-digest/SKILL.md, skills/goal-tracker/SKILL.md, skills/idea-capture/SKILL.md
  Overview of Social Engagement
    · Data Flow: Social Content Pipeline
  Social Curation Skills
    · Telegram Digest & Channel Recap
    · Farcaster Digest
    · Reply Maker & Write Tweet
  Productivity & Meta-Skills
    · Action Converter
    · Goal Tracker & Weekly Review
  Growth & Ad Management
    · Key Safety Guardrails for Ads
  Content Generation: Startup Ideas
    · Memo Schema Requirements

## · Fleet & Instance Management Skills  (L1966)
  源文件: generate-skills-json, onboard, scripts/sync-upstream.sh, skills/article/SKILL.md, skills/auto-workflow/SKILL.md, skills/fleet-control/SKILL.md, skills/fork-contributor-leaderboard/SKILL.md, skills/fork-fleet/SKILL.md, skills/fork-skill-digest/SKILL.md, skills/hacker-news-digest/SKILL.md, skills/morning-brief/SKILL.md, skills/onboard/SKILL.md
  Core Management Skills
    · Fleet Control Data Flow
  Instance Spawning & Configuration
    · Provisioning Workflow
  Community & Skill Analytics
    · Contributor & Skill Leaderboards
    · The `skills.json` Manifest
  Automated Workflow Engine
    · Recommendation Logic
  Onboarding & Health Validation

## · Self-Healing & Observability  (L2121)
  源文件: docs/_config.yml, docs/status.md, memory/skill-health/.gitkeep, skills/heartbeat/SKILL.md, skills/reflect/SKILL.md, skills/skill-evals/SKILL.md, skills/skill-evals/evals.json, skills/skill-health/SKILL.md, skills/skill-repair/SKILL.md
    · The Self-Healing Loop
    · Heartbeat & Health Monitoring
    · Skill Evals, Analytics & Repair
    · Security & Update Management
    · Memory-State Association

## · Heartbeat & Health Monitoring  (L2250)
  源文件: docs/_config.yml, docs/status.md, memory/cron-state.json, memory/skill-health/.gitkeep, skills/heartbeat/SKILL.md, skills/reflect/SKILL.md, skills/skill-health/SKILL.md, skills/skill-health/tests/smoke.sh
  Overview
  Implementation & Data Flow
    · Data Sources
    · Code Entity Space: Heartbeat Logic
  Health Classification & Priority Tiers
    · P0 — Critical Failures (DEGRADED)
    · P1-P3 — Warnings (WATCH)
  Public Status Page (`docs/status.md`)
    · Token Pulse Integration
  Skill Health & Self-Healing (Complementary System)
    · Notification Deduplication

## · Skill Evals, Analytics & Repair  (L2389)
  源文件: .github/workflows/aeon.yml, .github/workflows/messages.yml, dashboard/lib/config.ts, dashboard/lib/constants.ts, docs/skill-graph.md, memory/issues/INDEX.md, scripts/eval-audit, scripts/postprocess-replicate.sh, scripts/prefetch-xai.sh, scripts/skill-runs, skills/agent-buzz/SKILL.md, skills/cost-report/SKILL.md
  Quality Scoring & Evaluation Framework
    · The `skill-evals` Pipeline
    · The `eval-audit` Utility
  Fleet Analytics & Exit Taxonomy
    · Exit Taxonomy
    · Anomaly Detection
  Skill Repair & Auto-Patching
    · Repair Workflow
    · The Prefetch Pattern
  Skill Graph & Dependencies
    · Dependency Mapping Logic
    · Self-Healing Loop Visualization

## · Security & Update Management  (L2571)
  源文件: .gitignore, add-skill, articles/workflow-security-audit-2026-04-11.md, scripts/postprocess-farcaster.sh, skills/security-digest/SKILL.md, skills/security/trusted-sources.txt, skills/skill-security-scan/SKILL.md, skills/skill-security-scan/scan.sh, skills/skill-update-check/SKILL.md, skills/syndicate-article/SKILL.md, skills/workflow-security-audit/SKILL.md
  Supply Chain Integrity: skills.lock
    · Data Model
    · Implementation in add-skill
  Skill Security Scanning
    · Threat Categories & Detection
    · Trusted Sources & Baselines
    · Security Scan Logic Flow
  Update Management & Drift Detection
    · Triage & Enrichment
    · Priority Assignment
  Workflow Security Auditing
    · Automated Tooling
    · Critical Injection Patterns
    · Remediation Strategy
  Security Digest & Threat Intelligence
    · Data Sources & Enrichment
    · Action Tiers

## · Memory & State Management  (L2759)
  源文件: articles/.gitkeep, articles/changelog-2026-03-19.md, memory/MEMORY.md, memory/cron-state.json, memory/logs/.gitkeep, memory/logs/2026-03-19.md, memory/watched-repos.md
    · Persistence Mechanism
    · Core Memory Components
    · Memory Interaction Flow
  Memory Directory Structure (5.1)
  Issues Tracker & Reflect Skills (5.2)

## · Memory Directory Structure  (L2874)
  源文件: articles/.gitkeep, articles/changelog-2026-03-19.md, memory/MEMORY.md, memory/cron-state.json, memory/logs/.gitkeep, memory/logs/2026-03-19.md, memory/topics/.gitkeep, memory/watched-repos.md
  Overview of Memory Architecture
    · Data Flow and Persistence
    · Memory Organization Diagram
  Core Memory Files
    · memory/MEMORY.md
    · memory/cron-state.json
    · memory/logs/
    · memory/watched-repos.md
  Observability and Analytics
    · Token Usage and Cost Tracking
    · Skill Health and Quality
  Memory to Code Mapping
  Implementation Details

## · Issues Tracker & Reflect Skills  (L3021)
  源文件: .github/workflows/chain-runner.yml, .outputs/.gitkeep, CLAUDE.md, memory/skill-health/.gitkeep, skills/last30/SKILL.md, skills/reflect/SKILL.md, skills/skill-health/SKILL.md, skills/weekly-shiplog/SKILL.md
  1. Structured Issues Tracker
    · 1.1 Issue Lifecycle & Taxonomy
    · 1.2 The INDEX.md and ISS-NNN Pattern
    · 1.3 Data Flow: Detection to Resolution
  2. Skill Health Monitoring (`skill-health`)
    · 2.1 Classification Logic
    · 2.2 Issue Reconciliation
  3. Reflect & Consolidation Skills
    · 3.1 Weekly Reflect (`reflect`)
    · 3.2 Last 30 Days (`last30`)
    · 3.3 Weekly Shiplog (`weekly-shiplog`)
  4. Implementation Details
    · 4.1 Memory File Interactions
    · 4.2 Chain Execution and Context

## · Dashboard  (L3200)
  源文件: aeon, dashboard/app/api/auth/route.ts, dashboard/app/api/secrets/route.ts, dashboard/app/api/upload/route.ts, dashboard/app/page.tsx, dashboard/next-env.d.ts, dashboard/package-lock.json, dashboard/package.json
    · System Interaction Overview
    · Code-to-System Mapping
    · Core Functionality
    · Component Navigation

## · Dashboard UI Components  (L3322)
  源文件: dashboard/app/api/secrets/route.ts, dashboard/app/api/upload/route.ts, dashboard/app/page.tsx, dashboard/components/AuthModal.tsx, dashboard/components/ErrorScreen.tsx, dashboard/components/HQOverview.tsx, dashboard/components/ImportModal.tsx, dashboard/components/LeftSidebar.tsx, dashboard/components/LoadingScreen.tsx, dashboard/components/RightPanel.tsx, dashboard/components/ScheduleEditor.tsx, dashboard/components/SecretsPanel.tsx
  Component Architecture Overview
    · Implementation Diagram: Component Tree and Data Flow
  Primary Components
    · LeftSidebar (Skill List)
    · TopBar (Sync & Global Status)
    · SkillDetail (Per-Skill Configuration)
    · SecretsPanel
  Specialized Systems
    · SpecNode JSON-Render System
    · ImportModal & Skill Ingestion
    · Log Retrieval and Parsing
  Code Entity Mapping

## · Dashboard API Routes  (L3520)
  源文件: dashboard/.env.example, dashboard/.gitignore, dashboard/app/api/analytics/route.ts, dashboard/app/api/memory/issues/route.ts, dashboard/app/api/memory/logs/route.ts, dashboard/app/api/memory/route.ts, dashboard/app/api/memory/search/route.ts, dashboard/app/api/memory/topics/route.ts, dashboard/app/api/runs/route.ts, dashboard/app/api/secrets/route.ts, dashboard/app/api/skills/route.ts, dashboard/app/api/sync/route.ts
  Skill Management (`/api/skills`)
    · Implementation Details
    · Data Flow: Skill Configuration Update
  Execution Control (`/api/skills/[name]/run`)
  Secret Management (`/api/secrets`)
  Run History and Logs (`/api/runs`)
  Skill Ingestion (`/api/upload`)
    · Key Logic:
  Git Synchronization (`/api/sync`)
  Memory Access (`/api/memory/*`)

## · Integration Interfaces  (L3690)
  源文件: README.md, a2a-server/.gitignore, a2a-server/package.json, a2a-server/src/index.ts, a2a-server/tsconfig.json, add-a2a, add-mcp, aeon.yml, examples/README.md, examples/a2a/autogen_workflow.py, examples/a2a/crewai_task.py, examples/a2a/langchain_client.py
    · Integration Architecture Overview
  7.1 MCP Server (Claude Desktop & Claude Code)
  7.2 A2A Gateway (Agent-to-Agent Protocol)
  7.3 Soul & Identity Layer
  System Connectivity Map

## · MCP Server (Claude Desktop & Claude Code)  (L3856)
  源文件: README.md, add-mcp, aeon.yml, examples/README.md, examples/a2a/autogen_workflow.py, examples/a2a/crewai_task.py, examples/a2a/langchain_client.py, examples/a2a/openai_agents_client.py, examples/mcp/claude_desktop_config.json, examples/mcp/test_connection.py, mcp-server/package.json, mcp-server/src/index.ts
    · Purpose and Scope
  Architecture & Data Flow
    · Skill-to-Tool Mapping
    · Execution Pipeline
  Implementation Details
    · Server Core (`mcp-server/src/index.ts`)
    · Configuration and Build
  Setup and Verification
    · The `add-mcp` Script
    · Verification Flow (`test_connection.py`)
  Integration with Claude
    · Claude Desktop
    · Claude Code
    · Security and Environment

## · A2A Gateway (Agent-to-Agent Protocol)  (L4014)
  源文件: README.md, a2a-server/.gitignore, a2a-server/package.json, a2a-server/src/index.ts, a2a-server/tsconfig.json, add-a2a, aeon.yml, examples/README.md, examples/a2a/autogen_workflow.py, examples/a2a/crewai_task.py, examples/a2a/langchain_client.py, examples/a2a/openai_agents_client.py
  Overview and Setup
    · Setup via `add-a2a`
  Architecture and Data Flow
    · System Component Mapping
    · Task Lifecycle
  API Endpoints
    · Agent Discovery
    · JSON-RPC Interface
    · SSE Streaming
  Client Integration Examples
    · Framework Implementations
    · Example: LangChain Tool Wrapper
  Task Persistence and Eviction

## · Soul & Identity Layer  (L4190)
  源文件: .github/workflows/chain-runner.yml, .outputs/.gitkeep, CLAUDE.md, README.md, aeon.yml, assets/skill.jpg, skills/contributor-reward/SKILL.md
  Overview
    · Data Flow: Identity Injection
  Soul File Hierarchy
    · Implementation Rules
  Global Governance (`CLAUDE.md`)
    · Key Governance Modules
  Identity in the Skill Lifecycle
    · Integration with Self-Healing
  Practical Examples
    · Contributor Rewards & Identity
    · Identity across the Fleet

## · Public Site & Documentation  (L4343)
  源文件: docs/Gemfile, docs/_config.yml, docs/_data/articles.json, docs/_data/logs.json, docs/_data/memory.json, docs/_data/topics.json, docs/_layouts/default.html, docs/_layouts/post.html, docs/_posts/2026-03-19-changelog-week-of-2026-03-19.md, docs/_posts/2026-03-25-aeon-is-the-anti-openclaw.md, docs/_posts/2026-03-28-the-agent-that-fixes-itself.md, docs/activity.md
    · System Overview
    · Key Components
    · Dashboard Entities vs. Code Entities
    · Site Synchronization Logic
  Child Pages

## · Site Structure & Jekyll Configuration  (L4501)
  源文件: docs/Gemfile, docs/_config.yml, docs/_data/articles.json, docs/_data/logs.json, docs/_data/memory.json, docs/_data/topics.json, docs/_layouts/default.html, docs/_layouts/post.html, docs/_posts/2026-03-19-changelog-week-of-2026-03-19.md, docs/_posts/2026-03-25-aeon-is-the-anti-openclaw.md, docs/_posts/2026-03-28-the-agent-that-fixes-itself.md, docs/activity.md
  Jekyll Configuration
    · Navigation & Routing
  Data Synchronization Pipeline
    · `sync-site-data.sh` Execution Logic
    · Data Flow Diagram
  The Status Dashboard (`status.md`)
    · Health Monitoring Logic
    · System Status Mapping
  Templates and Styling
    · CSS and Component Styling

## · Content Generation & Syndication  (L4680)
  源文件: .gitignore, add-skill, articles/.gitkeep, docs/index.md, memory/logs/.gitkeep, scripts/generate-feed.sh, scripts/postprocess-devto.sh, scripts/postprocess-farcaster.sh, skills/rss-feed/SKILL.md, skills/skill-update-check/SKILL.md, skills/syndicate-article/SKILL.md, skills/update-gallery/SKILL.md
  Content Creation Flow
    · Article Generation
    · The Article Lifecycle
  Site Indexing & Gallery Refresh
    · Implementation Details
  RSS Feed Generation
    · The `generate-feed.sh` Script
    · Validation and Change Detection
  Syndication Pipeline
    · The Pending Payload Pattern
    · Farcaster Quality Gate

## · Scripts & Utilities Reference  (L4826)
  源文件: .gitignore, add-skill, aeon, dashboard/app/api/auth/route.ts, dashboard/package-lock.json, dashboard/package.json, generate-skills-json, memory/issues/INDEX.md, onboard, scripts/eval-audit, scripts/postprocess-devto.sh, scripts/postprocess-farcaster.sh
    · Overview of Utility Types
  Prefetch & Sandbox Mitigation
    · Sandbox Data Flow
  Skill Management CLI Tools
    · Skill Lifecycle Operations
  Dashboard & Local UI
    · Local Development Bridge
  Diagnostic & Maintenance Utilities

## · Prefetch & Sandbox Mitigation Scripts  (L4978)
  源文件: .gitignore, add-skill, memory/issues/INDEX.md, scripts/eval-audit, scripts/postprocess-devto.sh, scripts/postprocess-farcaster.sh, scripts/postprocess-replicate.sh, scripts/prefetch-xai.sh, scripts/skill-runs, skills/agent-buzz/SKILL.md, skills/skill-update-check/SKILL.md, skills/syndicate-article/SKILL.md
  The Prefetch Pattern
    · prefetch-xai.sh
  The Pending Payload Pattern
    · Data Entity Mapping: Natural Language to Code
  Post-Processing Scripts
    · postprocess-devto.sh
    · postprocess-farcaster.sh
    · postprocess-replicate.sh
  Integration Example: syndicate-article

## · Skill Management CLI Tools  (L5122)
  源文件: .gitignore, add-skill, export-skill, generate-skills-json, memory/issues/INDEX.md, onboard, scripts/eval-audit, scripts/postprocess-farcaster.sh, scripts/postprocess-replicate.sh, scripts/prefetch-xai.sh, scripts/skill-runs, scripts/sync-upstream.sh
  Core Installation & Management Tools
    · `add-skill`
    · `generate-skills-json`
    · `export-skill`
  Maintenance & Synchronization
    · `sync-upstream.sh`
    · `skill-update-check`
  Diagnostics & Observability
    · `skill-runs`
    · `eval-audit`
  Initialization & Validation
    · `onboard`
    · `auto-workflow`

## · Workflow Templates  (L5292)
  源文件: README.md, aeon.yml, skills/changelog/SKILL.md, skills/code-health/SKILL.md, skills/contributor-reward/SKILL.md, skills/github-monitor/SKILL.md, skills/issue-triage/SKILL.md, skills/pr-review/SKILL.md, workflows/README.md, workflows/changelog.md, workflows/code-health.md, workflows/issue-triage.md
  Overview of Standalone Workflows
  From Natural Language to GitHub Actions
    · Template Execution Logic
  Template vs. Full AEON Skill
    · Comparison: Issue Triage
  Implementation Details

## · Available Templates & Customization  (L5403)
  源文件: skills/auto-merge/SKILL.md, skills/changelog/SKILL.md, skills/code-health/SKILL.md, skills/github-monitor/SKILL.md, skills/issue-triage/SKILL.md, skills/pr-review/SKILL.md, workflows/README.md, workflows/changelog.md, workflows/code-health.md, workflows/issue-triage.md, workflows/pr-review.md, workflows/security-digest.md
  Overview of Workflow Templates
    · Available Templates Mapping
  Technical Implementation & Data Flow
    · From Natural Language to Code Execution
  Customization Guide
    · 1. Trigger Configuration
    · 2. Criteria & Logic Customization
    · 3. Project Context
  Comparison: Templates vs. Full Skills
    · Key Functional Differences

## · Glossary  (L5535)
  源文件: .github/workflows/aeon.yml, .github/workflows/chain-runner.yml, .github/workflows/messages.yml, .gitignore, .outputs/.gitkeep, CLAUDE.md, README.md, a2a-server/.gitignore, a2a-server/package.json, a2a-server/src/index.ts, a2a-server/tsconfig.json, add-a2a
  Core Framework Concepts
    · Skill
    · Var
    · Soul
    · Chain (Skill Chaining)
  Execution & State Terminology
    · Execution Engine
    · Flat-File Memory
    · Exit Taxonomy
    · Reactive Trigger
  Technical Mapping Diagrams
    · Diagram 1: Natural Language to Code Entity Mapping
    · Diagram 2: Data Flow of a Skill Execution
  Infrastructure & Tooling
    · System Definitions Table