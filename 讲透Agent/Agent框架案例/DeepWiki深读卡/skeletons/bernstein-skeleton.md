# Skeleton: bernstein（48 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 11KB | 2 | ~0 | 47 |
| 2 | Getting Started | L226 | 18KB | 3 | ~11 | 35 |
| 3 | Core Concepts and Terminology | L654 | 16KB | 2 | ~6 | 43 |
| 4 | Architecture | L966 | 16KB | 2 | ~0 | 36 |
| 5 | Task Server and API | L1279 | 19KB | 3 | ~6 | 30 |
| 6 | Orchestrator and Task Lifecycle | L1636 | 18KB | 3 | ~4 | 30 |
| 7 | Agent Spawning and Adapters | L1941 | 14KB | 2 | ~2 | 34 |
| 8 | Planning and Task Decomposition | L2158 | 14KB | 2 | ~0 | 33 |
| 9 | Git Integration and Worktree Isolation | L2457 | 12KB | 2 | ~0 | 32 |
| 10 | Persistence and State Management | L2650 | 17KB | 3 | ~3 | 31 |
| 11 | CLI Reference | L2924 | 12KB | 3 | ~1 | 24 |
| 12 | Run, Init, and Bootstrap Commands | L3171 | 12KB | 2 | ~2 | 30 |
| 13 | Status, Audit, and Lineage Commands | L3367 | 12KB | 2 | ~3 | 32 |
| 14 | Cost, Adapter, and Operational Commands | L3579 | 10KB | 1 | ~4 | 32 |
| 15 | TUI and Web Dashboard | L3739 | 8KB | 2 | ~0 | 33 |
| 16 | Terminal UI (TUI) | L3888 | 9KB | 2 | ~1 | 38 |
| 17 | Web Dashboard (React) | L4082 | 8KB | 2 | ~3 | 35 |
| 18 | Security and Compliance | L4253 | 10KB | 2 | ~0 | 29 |
| 19 | Authentication, Authorization, and Rate Limiting | L4419 | 11KB | 2 | ~0 | 29 |
| 20 | Command Security and Guardrails | L4611 | 11KB | 2 | ~0 | 31 |
| 21 | Audit Chain, Lineage, and Compliance | L4799 | 11KB | 2 | ~0 | 32 |
| 22 | Air-Gap and Network Security | L4984 | 10KB | 2 | ~2 | 31 |
| 23 | Observability and Cost Management | L5172 | 7KB | 2 | ~3 | 20 |
| 24 | Metrics, Tracing, and Alerting | L5311 | 14KB | 2 | ~0 | 31 |
| 25 | Cost Tracking and Budget Enforcement | L5529 | 9KB | 2 | ~0 | 33 |
| 26 | Quality Gates and Verification | L5682 | 9KB | 2 | ~2 | 32 |
| 27 | Janitor, Gate Runner, and Completion Signals | L5839 | 12KB | 2 | ~0 | 31 |
| 28 | Benchmarking and Evaluation | L6040 | 10KB | 2 | ~1 | 35 |
| 29 | Model Routing and Prompt Engineering | L6219 | 7KB | 2 | ~2 | 17 |
| 30 | Model Router and Contextual Bandit | L6353 | 10KB | 2 | ~0 | 37 |
| 31 | Prompt Engineering and Cache Locality | L6522 | 10KB | 2 | ~2 | 32 |
| 32 | Knowledge, Memory, and Self-Evolution | L6694 | 6KB | 2 | ~2 | 8 |
| 33 | Knowledge Base and Memory Layer | L6822 | 10KB | 2 | ~0 | 27 |
| 34 | Self-Evolution Loop | L7000 | 11KB | 2 | ~4 | 31 |
| 35 | Integrations and Extensions | L7177 | 8KB | 2 | ~2 | 34 |
| 36 | MCP, A2A, and Protocol Integrations | L7335 | 10KB | 2 | ~3 | 31 |
| 37 | Plugin System | L7485 | 9KB | 2 | ~2 | 31 |
| 38 | IDE Extensions and SDK | L7636 | 10KB | 2 | ~2 | 33 |
| 39 | Autofix and Auto-Heal | L7809 | 8KB | 2 | ~4 | 32 |
| 40 | Deployment and Infrastructure | L7968 | 8KB | 2 | ~2 | 22 |
| 41 | Kubernetes and Helm Deployment | L8114 | 8KB | 1 | ~4 | 22 |
| 42 | CI/CD Pipelines and Release Automation | L8282 | 13KB | 1 | ~4 | 38 |
| 43 | Docker and Sandbox Backends | L8476 | 11KB | 2 | ~1 | 30 |
| 44 | Testing Strategy | L8653 | 7KB | 1 | ~2 | 23 |
| 45 | Test Infrastructure and Patterns | L8787 | 8KB | 2 | ~0 | 33 |
| 46 | Integration, Chaos, and Pentest Suites | L8938 | 12KB | 2 | ~2 | 33 |
| 47 | Contributing and Development | L9124 | 10KB | 2 | ~2 | 40 |
| 48 | Glossary | L9319 | 12KB | 2 | ~3 | 45 |


## · Overview  (L6)
  源文件: .cursor/rules/module-map.mdc, .cursor/rules/overview.mdc, .goosehints, .plugin/plugin.json, .well-known/security.txt, AGENTS.md, CHANGELOG.md, CLAUDE.md, CONVENTIONS.md, README.md, SECURITY.md, bernstein.yaml
  Core Value Proposition
  Architectural Overview
    · System Entity Map: Bridging User Goals and Code Entities
  Key Concepts
  Codebase Organization and Navigation
  Wiki Roadmap

## · Getting Started  (L226)
  源文件: .well-known/security.txt, SECURITY.md, bernstein.yaml, docker/sandbox/docker-compose.researcher.yaml, docs/getting-started/quickstart-demo.md, docs/index.md, docs/operations/CONFIG.md, docs/operations/commands.md, docs/operations/deployment-guide.md, docs/reference/FEATURE_MATRIX.md, docs/routine-scenarios.md, docs/use-cases.md
  Installation
    · Standard Installation
    · Homebrew
    · npm Package
    · Docker
    · Air-Gap Wheelhouse Installation
  First-Run Setup with `bernstein init`
    · The `.sdd/` Directory Structure
    · Layout Diagram
  The `bernstein.yaml` Configuration File
    · Key Config Sections
  Quickstart Examples
    · Run from Goal String
    · Run from Plan File
    · Run Lifecycle Diagram
  Pre-flight Verification with `bernstein doctor`
    · Checks Performed
    · Doctor Command Flow
    · Usage
  Examples and Plan Library
    · Example Plans Include
    · Plan File Structure

## · Core Concepts and Terminology  (L654)
  源文件: .cursor/rules/module-map.mdc, .cursor/rules/overview.mdc, .goosehints, .plugin/plugin.json, AGENTS.md, CHANGELOG.md, CLAUDE.md, CONVENTIONS.md, README.md, docs/adapters/ADAPTER_GUIDE.md, docs/architecture/plans.md, docs/integrations/agent-session.md
  1. The Task and Agent Abstractions
    · Tasks
    · Agents and Roles
    · Technical Data Flow: Task to Agent
  2. The State Directory (`.sdd/`)
  3. Orchestration Components
    · The Janitor and Completion Signals
    · The Audit Chain and Lineage
    · Worktree Isolation
  4. Execution Lifecycle
  5. The Plan Formats: TaskPlan and Plan YAML
  6. The Agent Card
  7. The `.bernstein/rules.yaml` Organizational Rule Enforcement File

## · Architecture  (L966)
  源文件: docs/architecture/ARCHITECTURE.md, docs/gui/index.md, docs/guides/index.md, docs/operations/work-ledger.md, src/bernstein/cli/__init__.py, src/bernstein/cli/commands/ledger_cmd.py, src/bernstein/cli/commands/resume_cmd.py, src/bernstein/cli/helpers.py, src/bernstein/core/__init__.py, src/bernstein/core/agents/prompt_cache_locality.py, src/bernstein/core/agents/spawn_prompt.py, src/bernstein/core/compat_redirect_ledger.py
  The Three-Tier Model
    · 1. Frontend (CLI/TUI/Web)
    · 2. Task Server (FastAPI)
    · 3. Orchestrator and Agents
    · Three-Tier Interaction Diagram
  File-Based State Model (`.sdd/`)
  Major Subsystems Overview
    · Task Server and API
    · Orchestrator and Task Lifecycle
    · Agent Spawning and Adapters
    · Planning and Task Decomposition
    · Git Integration and Worktree Isolation
  Code Entity Mapping: Task Lifecycle
  Operational Safety and Draining

## · Task Server and API  (L1279)
  源文件: src/bernstein/core/agents/claude_max_turns.py, src/bernstein/core/lifecycle/__init__.py, src/bernstein/core/memory/sqlite_store.py, src/bernstein/core/observability/apm_integration.py, src/bernstein/core/observability/cascading_failure_circuit_breaker.py, src/bernstein/core/observability/datadog_export.py, src/bernstein/core/orchestration/adaptive_tick.py, src/bernstein/core/orchestration/convergence_guard.py, src/bernstein/core/orchestration/orchestrator_config.py, src/bernstein/core/orchestration/orchestrator_health.py, src/bernstein/core/routes/_sse.py, src/bernstein/core/routes/_unconfigured.py
  Startup and Bootstrap
    · Key Steps in Server Bootstrap
    · Task Server Component Mapping
  Route Structure and API Versioning
    · Modular Route Organization
    · API Versioning and Compatibility
    · API Data Flow Example (Task Creation & Claiming)
  Server Models (Pydantic Request/Response Schemas)
    · Highlights of Server Models
  Middleware
    · 1. Authentication and Rate Limiting
    · 2. Body Size Limiting
    · 3. Audit and Crash Guards
  Server-Sent Events (SSE)
    · Core SSE Components
    · SSE Endpoint Example
  WebSocket Support
  Summary of Task Server and API Workflow

## · Orchestrator and Task Lifecycle  (L1636)
  源文件: docs/examples/agent-prompt-template.md, docs/orchestration/worker-coordination.md, docs/release-notes/v2.16.0.md, docs/substrate/claude-code.md, mutmut_config.py, src/bernstein/adapters/council_runner.py, src/bernstein/adapters/env_isolation.py, src/bernstein/adapters/openai_agents.py, src/bernstein/adapters/openai_agents_runner.py, src/bernstein/cli/commands/stop_cmd.py, src/bernstein/cli/plan/plan_display.py, src/bernstein/cli/run_bootstrap.py
    · Orchestrator Tick Loop
    · Task State Machine
    · Batching by Role and Dependency Filtering
    · Write-Ahead Log (WAL)
    · Drain and Graceful Shutdown
    · Summary Diagram: From Natural Language Concepts to Code Entities

## · Agent Spawning and Adapters  (L1941)
  源文件: docs/operations/merge-gate.md, src/bernstein/adapters/aider.py, src/bernstein/adapters/amp.py, src/bernstein/adapters/base.py, src/bernstein/adapters/caching_adapter.py, src/bernstein/adapters/claude.py, src/bernstein/adapters/codex.py, src/bernstein/adapters/cody.py, src/bernstein/adapters/continue_dev.py, src/bernstein/adapters/cursor.py, src/bernstein/adapters/gemini.py, src/bernstein/adapters/generic.py
  The CLIAdapter Base Class
    · Key Responsibilities
    · Implementation Diagram: Adapter Hierarchy
  Agent Spawning Lifecycle
    · 1. Spawn
    · 2. Watchdog
    · 3. Reap
    · Process Flow: Natural Language to Code Execution
  The `bernstein-worker` Wrapper
  Rate-Limit Detection and Mitigation
  Supported Adapters Catalog
    · Caching Wrapper

## · Planning and Task Decomposition  (L2158)
  源文件: docs/concepts/abstracted-code-review.md, docs/concepts/action-cache.md, docs/concepts/artifact-lineage.md, docs/concepts/best-of-n.md, docs/concepts/feature-contract.md, docs/concepts/orchestrator-hardening.md, docs/concepts/phase-pipeline.md, docs/concepts/sandbox-selector.md, docs/concepts/schema-validation-retry.md, docs/concepts/spec-as-test.md, docs/concepts/swarm-migration.md, docs/concepts/team-hub.md
  The Planner and Plan YAML Schema
    · Planner Overview
    · Plan YAML Schema
    · Plan Loading and Parsing
  Manager Agent Role and Planning Workflow
    · Manager Planning Process
    · Manager Queue Review and Refinement Loop
  Auto-Decomposition of Large Tasks
  The Refinement Loop and Adversary Veto
  Vertical Slice Planning
  The Workflow DSL and Recipe Execution
  Library of Ready-Made Plans and Templates
  Data Flow Diagrams
    · Natural Language Goal to Code Entities
    · Decomposition and Refinement Lifecycle

## · Git Integration and Worktree Isolation  (L2457)
  源文件: docs/decisions/009-lineage-v1.md, docs/operations/worktrees.md, scripts/check_test_collection.py, src/bernstein/cli/commands/blast_radius_cmd.py, src/bernstein/cli/commands/maintenance_cmd.py, src/bernstein/cli/commands/merge_cmd.py, src/bernstein/cli/commands/session_cmd.py, src/bernstein/cli/commands/worktrees_cmd.py, src/bernstein/core/agents/agent_cost_ledger.py, src/bernstein/core/agents/agent_discovery.py, src/bernstein/core/agents/agent_identity.py, src/bernstein/core/agents/agent_ipc.py
  Worktree Lifecycle and Management
    · Lifecycle Phases
    · Worktree State Transitions
  Incremental Merge and Partial Commits
  Git Hygiene and Repository Health
    · Mechanical Cleanup (`run_gc`)
    · Pre-flight Health Checks
  GitHub Integration and PR Generation
    · Evolution Coordination
    · PR Lifecycle
  The Drain and Cleanup Sequence
    · Drain Actions

## · Persistence and State Management  (L2650)
  源文件: docs/architecture/ARCHITECTURE.md, docs/gui/index.md, docs/guides/index.md, docs/operations/deterministic-replay.md, docs/operations/replay.md, src/bernstein/core/git/changelog.py, src/bernstein/core/git/git_context.py, src/bernstein/core/knowledge/knowledge_base.py, src/bernstein/core/observability/loop_detector.py, src/bernstein/core/orchestration/deterministic.py, src/bernstein/core/orchestration/orchestrator_cleanup.py, src/bernstein/core/persistence/agent_checkpoint.py
  The .sdd/ File-Based State Model
    · Directory Composition
    · Atomic Writes and Crash Safety
  Write-Ahead Log (WAL) and Crash Recovery
    · WAL Overview
    · Crash Recovery Workflow
    · Data Flow: Orchestrator Decisions to WAL Persistence
  Agent Checkpoints
  File Locks and Atomic Writes
  Session Continuity
  The Merkle Fingerprint Store
  Disaster Recovery
  Optional PostgreSQL and Redis Backends
  Technical Diagrams: Bridging Concepts to Code Entities
    · Natural Language to WAL Code Entities
    · Agent Checkpoint Lifecycle Mapping

## · CLI Reference  (L2924)
  源文件: .cursor/rules/module-map.mdc, .cursor/rules/overview.mdc, .goosehints, AGENTS.md, CLAUDE.md, CONVENTIONS.md, README.md, docs/adapters/ADAPTER_GUIDE.md, docs/reference/cli-reference.md, docs/release-notes/unreleased.md, src/bernstein/adapters/_contract.py, src/bernstein/adapters/registry.py
    · Entrypoints Overview
  Command Organization
    · High-Level Command Grouping
    · Natural Language Goals to Code Entities Mapping
  3.1 Run, Init, and Bootstrap Commands
  3.2 Status, Audit, and Lineage Commands
  3.3 Cost, Adapter, and Operational Commands
    · Command Discovery and Help Utilities
    · Command Grouping Entity Map

## · Run, Init, and Bootstrap Commands  (L3171)
  源文件: docs/orchestration/issue-to-pr.md, docs/orchestration/worker-coordination.md, docs/substrate/claude-code.md, src/bernstein/adapters/council_runner.py, src/bernstein/adapters/env_isolation.py, src/bernstein/adapters/openai_agents.py, src/bernstein/adapters/openai_agents_runner.py, src/bernstein/cli/commands/incident_cmd.py, src/bernstein/cli/commands/postmortem_cmd.py, src/bernstein/cli/commands/status_cmd.py, src/bernstein/cli/commands/stop_cmd.py, src/bernstein/cli/plan/plan_display.py
  Initialization and Quickstart
  The Run Sequence and Preflight
    · Preflight Validation
    · Cost Estimation
    · Run Bootstrap Lifecycle
  Command Execution Flow
  Operational Control: Cook, Stop, and Dry-Run
    · Synthetic Plan Generation (`cook`)
    · Lifecycle Termination (`stop`)
    · Dry-Run Execution
  Environment and Agent Isolation

## · Status, Audit, and Lineage Commands  (L3367)
  源文件: docs/eval/yaml-harness.md, docs/operations/audit-diagnose.md, docs/operations/security-and-identity.md, docs/security/audit-log.md, src/bernstein/cli/commands/audit_cmd.py, src/bernstein/cli/commands/eval_benchmark_cmd.py, src/bernstein/cli/commands/evidence_cmd.py, src/bernstein/cli/commands/lineage_cmd.py, src/bernstein/cli/commands/lineage_replay_cmd.py, src/bernstein/compliance/__init__.py, src/bernstein/compliance/evidence_pack.py, src/bernstein/core/evidence/bundle.py
  1. Status and Monitoring (`status`, `ps`)
    · Implementation and Data Flow
    · Process Status (`ps`)
    · Entity Map: Status Monitoring
  2. Audit Chain and Integrity (`audit`)
    · The HMAC Audit Chain
    · Key Components
  3. Lineage and Provenance (`lineage`)
    · Lineage v1 vs v2
    · Commands
    · Data Structure: Lineage Record
    · Entity Map: Lineage Verification Pipeline
  4. Evidence Bundles (`compliance`)
    · Implementation Details
  5. Standalone Auditor (`bernstein-verify`)
    · Features

## · Cost, Adapter, and Operational Commands  (L3579)
  源文件: docs/adapters/conformance-canary.md, docs/cloudflare/cloudflare-mcp.md, docs/observability/task-artifacts.md, docs/operations/adapters.md, docs/operations/cost-envelopes.md, docs/operations/debug-bundle.md, docs/operations/skill-provenance.md, scripts/adapter_canary.py, src/bernstein/adapters/canary.py, src/bernstein/adapters/claude_cache_control.py, src/bernstein/adapters/claude_mcp_loader.py, src/bernstein/adapters/claude_stream_parser.py
  Cost Management and Reporting
    · Data Flow and Persistence
    · Cost Comparison and Savings
  Adapter Health and Conformance
    · Conformance Canary and Advisories
    · Conformance Harness
    · Implementation Diagram: Adapter Lifecycle
  The Doctor Command
    · Check Categories
  Artifact and Communication Operations
    · Artifact Verification
    · Signal Actions and Blockers

## · TUI and Web Dashboard  (L3739)
  源文件: src/bernstein/cli/dashboard.py, src/bernstein/cli/run_cmd.py, src/bernstein/core/routes/status.py, src/bernstein/dashboard/templates/index.html, src/bernstein/tui/agent_duration.py, src/bernstein/tui/app.py, src/bernstein/tui/layout_persistence.py, src/bernstein/tui/log_viewer.py, src/bernstein/tui/mouse_support.py, src/bernstein/tui/notification_badge.py, src/bernstein/tui/session_recorder.py, src/bernstein/tui/snapshot_testing.py
    · System Interface Mapping
  Terminal UI (TUI)
    · Core Components and Layouts
    · Log Rendering Pipeline
    · Operational Panels
  Web Dashboard (React)
    · Implementation Details
    · Integration

## · Terminal UI (TUI)  (L3888)
  源文件: src/bernstein/cli/dashboard.py, src/bernstein/cli/run_cmd.py, src/bernstein/core/routes/status.py, src/bernstein/dashboard/templates/index.html, src/bernstein/tui/agent_duration.py, src/bernstein/tui/agent_log.py, src/bernstein/tui/app.py, src/bernstein/tui/approval_panel.py, src/bernstein/tui/command_palette.py, src/bernstein/tui/help_screen.py, src/bernstein/tui/layout_persistence.py, src/bernstein/tui/log_viewer.py
    · Data Flow and Architecture
    · Layout System and Presets
    · Log Rendering Pipeline
    · Navigation and Interaction
    · Worktree Status Panel
    · Session Recording and Testing
    · Theme System

## · Web Dashboard (React)  (L4082)
  源文件: .github/workflows/adapter-conformance-canary.yml, .github/workflows/coverage-ratchet-weekly.yml, .github/workflows/spa-bundle-freshness.yml, .github/workflows/typecheck-ts.yml, docs/assets/tui-live.svg, docs/assets/webui-agents.png, docs/assets/webui-approvals.png, docs/assets/webui-audit.png, docs/assets/webui-costs.png, docs/assets/webui-fleet.png, docs/assets/webui-renders.json, docs/assets/webui-settings.png
  Architecture and Mounting
    · Data Flow: Server to Dashboard
  Key Routes and Views
  Component Library and Theme
    · Theme Configuration
  PWA and Mobile GUI
    · PWA Configuration
  VS Code Extension Integration
    · Core Extension Entities
    · Command Mapping

## · Security and Compliance  (L4253)
  源文件: src/bernstein/core/cost/completion_budget.py, src/bernstein/core/git/merge_queue.py, src/bernstein/core/git/pr_size_governor.py, src/bernstein/core/git/worktree_claude_md.py, src/bernstein/core/git/worktree_isolation.py, src/bernstein/core/knowledge/memory_integrity.py, src/bernstein/core/observability/traces.py, src/bernstein/core/planning/workflow_importer.py, src/bernstein/core/quality/ci_monitor.py, src/bernstein/core/quality/comment_quality.py, src/bernstein/core/quality/quality_gates.py, src/bernstein/core/security/agent_card_signer.py
    · Security Architecture Overview
  5.1 Authentication, Authorization, and Rate Limiting
  5.2 Command Security and Guardrails
  5.3 Audit Chain, Lineage, and Compliance
  5.4 Air-Gap and Network Security

## · Authentication, Authorization, and Rate Limiting  (L4419)
  源文件: .github/workflows/ci-weekly-digest.yml, .github/workflows/spiffe-extra-e2e.yml, docs/orchestration/federation.md, docs/reference/spiffe-workload-identity.md, docs/security/secrets-broker.md, scripts/ci_weekly_digest.py, src/bernstein/cli/commands/citation_cmd.py, src/bernstein/cli/commands/secrets_cmd.py, src/bernstein/compliance/owasp_skills.py, src/bernstein/core/admission/models.py, src/bernstein/core/approval/gate.py, src/bernstein/core/identity/grants.py
  Authentication Architecture
    · Authentication Data Flow
  Authorization and RBAC
    · Zero-Trust Task Scoping
  Credential Grants and Secrets Broker
    · Scoped Grants
  Rate Limiting
    · 1. Auth Endpoint Protection
    · 2. Global Request Buckets
  Permission Policy and Guardrails

## · Command Security and Guardrails  (L4611)
  源文件: docs/operations/mcp-gateway.md, docs/sdd/identity-spawn-anchor.md, docs/sdd/toolcall-attestation-interlock.md, scripts/bench_toolcall_identity.py, src/bernstein/benchmark/swe_bench.py, src/bernstein/bridges/openclaw_gateway.py, src/bernstein/cli/commands/quickstart_cmd.py, src/bernstein/cli/dashboard_actions.py, src/bernstein/cli/run_confirm.py, src/bernstein/cli/status.py, src/bernstein/core/agents/claude_agent_card.py, src/bernstein/core/agents/claude_message_normalizer.py
  The Auto-Approve Pipeline
    · Command Normalization and Homoglyph Defense
    · Decision Logic and Precedence
  Always-Allow Rules and Tamper Protection
  Tool-Call Attestation Interlock
  Blocking Hooks and Elicitation
    · Interactive Elicitation
  Output Gates and DLP
    · PII and Secret Detection
    · Intent Verification
  Approval Routes and API

## · Audit Chain, Lineage, and Compliance  (L4799)
  源文件: .importlinter, README.zh-Hans.md, README.zh-TW.md, docs/operations/security-and-identity.md, src/bernstein/cli/commands/evidence_cmd.py, src/bernstein/cli/commands/lineage_cmd.py, src/bernstein/cli/commands/lineage_replay_cmd.py, src/bernstein/compliance/eu_ai_act.py, src/bernstein/core/evidence/bundle.py, src/bernstein/core/evidence/completion_gate.py, src/bernstein/core/evidence/output_diff.py, src/bernstein/core/lineage/__init__.py
  Tamper-Evident Audit Chain
    · Security and Key Management
    · Audit Event Types
  Artifact Lineage (v1/v2)
    · Lineage Versions
    · Lineage KMS Adapters
  Agent Card Signing (Detached JWS)
    · Implementation Details
  Sigstore and SLSA-3 Attestations
  Standalone Auditor: `bernstein-verify`
    · Compliance Mappings and Evidence

## · Air-Gap and Network Security  (L4984)
  源文件: .github/workflows/a2a-federation-e2e.yml, .github/workflows/airgap-e2e.yml, .github/workflows/bernstein-issues-decompose.yml, .github/workflows/cluster-e2e.yml, .github/workflows/dependabot-auto-merge.yml, .github/workflows/eval-nightly.yml, .github/workflows/license-compliance.yml, .github/workflows/nightly-deep-tests.yml, .github/workflows/pentest.yml, .github/workflows/soc2-evidence-nightly.yml, docs/operations/CONFIG.md, src/bernstein/adapters/openai_agents_builtins.py
  Overview of Air-Gap Architecture
    · Data Flow and Trust Boundaries
  Distribution and Wheelhouse
    · Building and Signing
    · Verification
  Runtime Network Security
    · Socket Guard Implementation
    · Network Policy and Configuration
  The `doctor-airgap` Battery
  Adversarial Pen-Test Suite
    · Attack Surface Coverage
  Secure Configuration and Env Expansion
    · Environment Variable Expansion

## · Observability and Cost Management  (L5172)
  源文件: .cursor/rules/directory-context.mdc, docs/observability/trends.md, src/bernstein/adapters/AGENTS.md, src/bernstein/adapters/mock.py, src/bernstein/cli/AGENTS.md, src/bernstein/core/knowledge/agents_md_generator.py, src/bernstein/core/lineage/AGENTS.md, src/bernstein/core/routes/observability.py, src/bernstein/core/routes/status_dashboard.py, tests/unit/test_agents_md_generator.py, tests/unit/test_audit_004_guards_removed.py, tests/unit/test_cli_demo.py
  System Interaction Map
    · Observability and Dashboard Data Flow
  Metrics, Tracing, and Alerting
  Cost Tracking and Budget Enforcement
    · Cost and Lifecycle Code Entities
  Operational Commands

## · Metrics, Tracing, and Alerting  (L5311)
  源文件: .github/workflows/ci-macos-nightly.yml, .github/workflows/docs-observability-snapshot.yml, .github/workflows/mutation-fixed.yml, .github/workflows/pr-observability-summary.yml, docs/api/supervisor.md, docs/observability/otlp-export.md, docs/observability/snapshots/.gitkeep, docs/observability/unified-doctor.md, docs/operations/observability-overview.md, docs/sdd/otel-journal-bridge.md, scripts/observability/build_pr_summary.py, scripts/observability/gate.py
  Metrics Architecture
    · MetricsCollector and Persistence
    · Data Flow: Code to Prometheus
  OpenTelemetry and Journal-Anchored Tracing
    · Journal-Anchored Spans
    · Verification and Backfilling
  LLMWatcher and Anomaly Detection
  Provider Latency and Degradation Alerting
  Incident Timeline and Run Reports
    · Run Export
    · Incident Timeline Implementation
  Telemetry Control and Consent

## · Cost Tracking and Budget Enforcement  (L5529)
  源文件: docs/observability/task-artifacts.md, docs/operations/cost-envelopes.md, docs/operations/debug-bundle.md, docs/operations/skill-provenance.md, scripts/test_impact.py, src/bernstein/cli/commands/artifact_cmd.py, src/bernstein/cli/commands/artifacts_cmd.py, src/bernstein/cli/commands/cost.py, src/bernstein/cli/commands/debug_cmd.py, src/bernstein/core/cost/cost.py, src/bernstein/core/orchestration/run_session.py, src/bernstein/core/quality/auto_formatter.py
  System Architecture
    · Logic Flow and Code Entities
  Preflight Cost Estimation
  Model Pricing and Calculation
  Quality Metrics and Cost Justification
  CLI spend Visibility: `bernstein cost`
    · Savings Analysis
    · Reporting and Filtering
  Persistence and API
    · Endpoints

## · Quality Gates and Verification  (L5682)
  源文件: docs/operations/artifacts.md, docs/sdd/upgrade-task-ownership.md, scripts/test_impact.py, src/bernstein/core/cost/cost.py, src/bernstein/core/lineage/artifact_record.py, src/bernstein/core/lineage/figure_grounding.py, src/bernstein/core/orchestration/orchestrator_evolve.py, src/bernstein/core/orchestration/run_session.py, src/bernstein/core/quality/auto_formatter.py, src/bernstein/core/quality/benchmark_gate.py, src/bernstein/core/quality/cross_model_verifier.py, src/bernstein/core/quality/fast_path.py
  The Quality Pipeline
    · Verification Workflow
  Key Components
    · The Janitor and Gate Runner
    · Completion Signals
    · Quality Metrics and Test Impact
  Benchmarking and Evaluation
  Verification Architecture
  Sub-pages

## · Janitor, Gate Runner, and Completion Signals  (L5839)
  源文件: docs/operations/artifacts.md, docs/sdd/upgrade-task-ownership.md, scripts/test_impact.py, src/bernstein/core/cost/cost.py, src/bernstein/core/lineage/artifact_record.py, src/bernstein/core/lineage/figure_grounding.py, src/bernstein/core/orchestration/orchestrator_evolve.py, src/bernstein/core/orchestration/run_session.py, src/bernstein/core/quality/auto_formatter.py, src/bernstein/core/quality/benchmark_gate.py, src/bernstein/core/quality/cross_model_verifier.py, src/bernstein/core/quality/fast_path.py
  Overview of Verification Pipeline
    · Data Flow: Agent to Merge
    · System Component Association
  The Gate Runner and Pipeline
    · Key Features
    · Test Impact Analysis Implementation
  Completion Signals and Specialized Gates
    · 1. File and Path Signals
    · 2. Artifact Mode Criteria
    · 3. LLM Judge
  Janitor Logic and Verification Tiers
    · Work Attribution
    · Verifier Ladder
    · Diminishing Returns and Evolve Mode

## · Benchmarking and Evaluation  (L6040)
  源文件: benchmarks/bench_orchestrator.py, benchmarks/bench_task_store.py, benchmarks/swe_bench/run.py, docs/assets/ascii_logo.md, docs/eval/yaml-harness.md, docs/operations/audit-diagnose.md, docs/quality/consensus-scoring.md, docs/security/audit-log.md, src/bernstein/cli/commands/audit_cmd.py, src/bernstein/cli/commands/eval_benchmark_cmd.py, src/bernstein/compliance/__init__.py, src/bernstein/compliance/evidence_pack.py
  ProgramBench
    · Implementation Details
    · Component Association
  SWE-Bench Integration
  The Eval Harness
    · 1. ab_runner
    · 2. Scenario Runner
    · 3. Incident Synthesizer
    · Eval Data Flow
  Golden Test Suite
  Audit and Compliance Verification
    · System Component Map

## · Model Routing and Prompt Engineering  (L6219)
  源文件: src/bernstein/cli/ui.py, src/bernstein/core/agents/spawner_warm_pool.py, src/bernstein/core/config/home.py, src/bernstein/core/routing/bandit_router.py, src/bernstein/core/routing/cascade.py, src/bernstein/core/routing/router_core.py, src/bernstein/sdd/validator.py, src/bernstein/tui/context_files_doctor.py, tests/integration/test_ticket_validate_cli.py, tests/unit/test_cli_ui.py, tests/unit/test_commit_stats.py, tests/unit/test_context_files_doctor.py
  Overview of Model Selection and Prompting
    · System Architecture: From Task to Execution
  Model Routing and Contextual Bandit
  Prompt Engineering and Cache Locality
    · Prompt Assembly Components
    · Bridging Context to Model Space
    · Cache Locality and Drift
  Operational Controls

## · Model Router and Contextual Bandit  (L6353)
  源文件: docs/architecture/ARCHITECTURE.md, docs/gui/index.md, docs/guides/index.md, src/bernstein/cli/ui.py, src/bernstein/core/agents/spawner_warm_pool.py, src/bernstein/core/config/home.py, src/bernstein/core/git/changelog.py, src/bernstein/core/git/git_context.py, src/bernstein/core/knowledge/knowledge_base.py, src/bernstein/core/observability/loop_detector.py, src/bernstein/core/persistence/wal.py, src/bernstein/core/routing/bandit_router.py
  Tier-Aware Router
    · Routing Strategy and Tiers
    · Budget-Aware Routing
  Contextual Bandit Router
    · Feature Extraction
    · Reward Signal and Effort Bandit
  Model Fallback and Coercion
  Provider Health Monitoring
  Routing Decision Flow
    · Logic to Entity Mapping: Routing Pipeline
  Routing Decision Logging (WAL)
    · Data Flow: Routing Decision Persistence

## · Prompt Engineering and Cache Locality  (L6522)
  源文件: docs/operations/skill-selection-rules.md, docs/operations/work-ledger.md, docs/sdd/skill-selection-rules.md, sdk/python/src/bernstein_sdk/adapters/jira.py, sdk/python/src/bernstein_sdk/client.py, sdk/python/tests/test_client.py, src/bernstein/adapters/skills_injector.py, src/bernstein/cli/__init__.py, src/bernstein/cli/commands/ledger_cmd.py, src/bernstein/cli/commands/resume_cmd.py, src/bernstein/cli/helpers.py, src/bernstein/core/__init__.py
  Prompt Assembly and Injection
    · Assembly Pipeline
    · Prompt Structure and Code Entities
  KV-Cache Locality and Optimization
    · Cache Locality Strategies
    · Cache Key Computation
  Context Compression
    · Compression Components
  Monitoring and Metrics

## · Knowledge, Memory, and Self-Evolution  (L6694)
  源文件: docs/concepts/fingerprint-memoization.md, src/bernstein/core/knowledge/knowledge_graph.py, src/bernstein/core/knowledge/rag.py, src/bernstein/core/persistence/fingerprint.py, tests/unit/test_fingerprint.py, tests/unit/test_knowledge_graph.py, tests/unit/test_rag_memo_invalidation.py, tests/unit/test_sonar_final_style_hygiene.py
  System Architecture Overview
  9.1 Knowledge Base and Memory Layer
  9.2 Self-Evolution Loop
    · Key Components:

## · Knowledge Base and Memory Layer  (L6822)
  源文件: .cursor/rules/directory-context.mdc, docs/concepts/fingerprint-memoization.md, src/bernstein/adapters/AGENTS.md, src/bernstein/adapters/mock.py, src/bernstein/cli/AGENTS.md, src/bernstein/core/knowledge/agents_md_generator.py, src/bernstein/core/knowledge/knowledge_graph.py, src/bernstein/core/knowledge/rag.py, src/bernstein/core/lineage/AGENTS.md, src/bernstein/core/persistence/fingerprint.py, src/bernstein/core/routes/observability.py, src/bernstein/core/routes/status_dashboard.py
  Architectural Overview
    · Data Flow: From Transcript to Knowledge
  Codebase Indexing and RAG
    · CodebaseIndexer (SQLite FTS5)
    · Knowledge Graph and Impact Analysis
  Fingerprint Memoization
    · The Invalidation Rule
    · Code Dependencies
  AGENTS.md and Bridge Generation
    · Generation Logic
    · Multi-Agent Context Mapping
  Memory Observability
  CLI Commands
    · `bernstein memory`
    · `bernstein knowledge`

## · Self-Evolution Loop  (L7000)
  源文件: .github/workflows/ci-macos-nightly.yml, .github/workflows/docs-observability-snapshot.yml, .github/workflows/mutation-fixed.yml, .github/workflows/pr-observability-summary.yml, docs/observability/snapshots/.gitkeep, docs/observability/unified-doctor.md, scripts/observability/build_pr_summary.py, scripts/observability/gate.py, scripts/observability/render_trends.py, src/bernstein/benchmark/swe_bench.py, src/bernstein/bridges/openclaw_gateway.py, src/bernstein/cli/commands/analyze_cmd.py
  System Architecture
    · Evolution Pipeline Components
    · Creative Pipeline: Visionary → Analyst → Gate
  Risk Tiers (L0–L3)
  Implementation Flow
    · Evolution Data Flow
  Key Classes and Functions
    · `EvolutionCoordinator`
    · `UpgradeProposal` Scoring
    · Safety Mechanisms
  Execution: `bernstein evolve`
    · Command Sequence
    · Persistence and State

## · Integrations and Extensions  (L7177)
  源文件: docs/mcp/server.md, docs/mcp/tool_tiers.md, docs/operations/autofix-tier3.md, src/bernstein/benchmark/swe_bench.py, src/bernstein/bridges/openclaw_gateway.py, src/bernstein/cli/commands/quickstart_cmd.py, src/bernstein/cli/dashboard_actions.py, src/bernstein/cli/run_confirm.py, src/bernstein/cli/status.py, src/bernstein/core/agents/claude_agent_card.py, src/bernstein/core/agents/claude_message_normalizer.py, src/bernstein/core/autofix/tier3.py
  External Protocol Support
    · Protocol Interaction Map
  Plugin System
    · Core Lifecycle Hooks
  IDE Extensions and SDK
    · VS Code Architecture
  Autofix and Auto-Heal

## · MCP, A2A, and Protocol Integrations  (L7335)
  源文件: docs/mcp/server.md, docs/mcp/tool_tiers.md, docs/operations/autofix-tier3.md, docs/orchestration/federation.md, src/bernstein/cli/commands/citation_cmd.py, src/bernstein/core/approval/gate.py, src/bernstein/core/autofix/tier3.py, src/bernstein/core/orchestration/federation.py, src/bernstein/core/orchestration/federation_contract.py, src/bernstein/core/protocols/mcp/claim_receipt.py, src/bernstein/core/protocols/mcp/tool_tiers.py, src/bernstein/core/quality/citation_verifier.py
  Model Context Protocol (MCP)
    · Implementation Details
    · Exposed Tools
  A2A (Agent-to-Agent) Federation
    · Federation Layer
  Security and Authentication
    · Multi-Strategy Authentication
    · Permission Policy
  Protocol Mapping: Natural Language to Code Entities
    · MCP Request Lifecycle
    · Zero-Trust Auth Flow

## · Plugin System  (L7485)
  源文件: src/bernstein/benchmark/swe_bench.py, src/bernstein/bridges/openclaw_gateway.py, src/bernstein/cli/commands/quickstart_cmd.py, src/bernstein/cli/dashboard_actions.py, src/bernstein/cli/run_confirm.py, src/bernstein/cli/status.py, src/bernstein/core/agents/claude_agent_card.py, src/bernstein/core/agents/claude_message_normalizer.py, src/bernstein/core/orchestration/run_report.py, src/bernstein/core/persistence/file_health.py, src/bernstein/core/plugins_core/plugin_installer.py, src/bernstein/core/security/command_policy.py
  Architecture and Data Flow
    · Hook Registry and Lifecycle
    · Natural Language to Code Entity Space: Plugin Discovery
  Key Lifecycle Events
  The Plugin Manager
    · Execution Flow: Hook Dispatch
  Implementation Details
    · Hook Protocol and Interactive Elicitation
    · Security and Policy Enforcement
  Custom Plugins and Installation
    · Plugin Installation Sources
    · Creating a Plugin

## · IDE Extensions and SDK  (L7636)
  源文件: .github/workflows/adapter-conformance-canary.yml, .github/workflows/coverage-ratchet-weekly.yml, .github/workflows/typecheck-ts.yml, docs/operations/chat-bridges.md, docs/release-notes/v2.9.0.md, packages/vscode/.vscodeignore, packages/vscode/package-lock.json, packages/vscode/package.json, packages/vscode/tsconfig.json, sdk/python/src/bernstein_sdk/adapters/jira.py, sdk/python/src/bernstein_sdk/client.py, sdk/python/tests/test_client.py
  VS Code Extension
    · Extension Architecture and Providers
    · Command Registry and Data Flow
    · Data Flow: Editor to Code Entity
  SDK and API Clients
    · Python SDK
    · TypeScript SDK
    · Cloudflare Bridges (MCP)
  Chat Bridges: Discord and Slack
    · Discord Bridge
    · Slack Bridge
  Integrations Directory

## · Autofix and Auto-Heal  (L7809)
  源文件: .github/actions/bootstrap/action.yml, .github/workflows/auto-heal.yml, .github/workflows/bernstein-ci-fix.yml, .github/workflows/ci.yml, .github/workflows/cifuzz-pr.yml, .github/workflows/cluster-tunnel-e2e.yml, .github/workflows/codeql.yml, .github/workflows/contract-drift-autofix.yml, .github/workflows/dependency-review.yml, .github/workflows/docs-drift.yml, .github/workflows/release-major-minor.yml, .github/workflows/sbom.yml
  1. The Autofix Daemon
    · Escalation Ladder
    · Data Flow: CI Failure to Dispatch
  2. Auto-Heal Workflow (v2)
    · Bayesian Confidence and Bandit Selection
    · Cordon and Safety Rails
  3. Specialized Autofix Workflows
    · Contract Drift Autofix
    · Bernstein CI Fix (Fallback)
  4. The `bernstein autofix` Command
    · Configuration

## · Deployment and Infrastructure  (L7968)
  源文件: Dockerfile, action/entrypoint.sh, deploy/github-app/app.yml, deploy/grafana/dashboards/bernstein-otel.json, deploy/grafana/provisioning/dashboards/bernstein.yml, deploy/helm/bernstein/Chart.yaml, deploy/otel-collector/otel-collector-config.yaml, deploy/prometheus/prometheus.yml, docker-compose.yaml, docker/demo/Dockerfile, docker/demo/demo-cycle.sh, docs/integrations/github-action.md
  Infrastructure Overview
    · Code to Infrastructure Mapping
  Deployment Options
    · 1. Kubernetes and Helm
    · 2. Docker and Sandbox Backends
    · 3. CI/CD and Release Automation
  Deployment Topology
    · Automated Maintenance and Debugging
  Deployment Configuration Summary

## · Kubernetes and Helm Deployment  (L8114)
  源文件: Dockerfile, action/entrypoint.sh, deploy/github-app/app.yml, deploy/grafana/dashboards/bernstein-otel.json, deploy/grafana/provisioning/dashboards/bernstein.yml, deploy/helm/bernstein/Chart.yaml, deploy/otel-collector/otel-collector-config.yaml, deploy/prometheus/prometheus.yml, docker-compose.yaml, docker/demo/Dockerfile, docker/demo/demo-cycle.sh, docs/integrations/github-action.md
  Deployment Architecture
    · Component Topology
    · System Data Flow and Code Entities
  State Management and Persistence
    · The .sdd/ Directory Structure
  Security and Secrets
  Observability and Monitoring
    · Metrics Pipeline
    · Dashboards
  Container Image Strategy
    · Image Entrypoints
  Scaling and Lifecycle
    · Worker Scaling
    · Health Checks

## · CI/CD Pipelines and Release Automation  (L8282)
  源文件: .github/actions/bootstrap/action.yml, .github/workflows/adapter-contract-drift.yml, .github/workflows/auto-heal.yml, .github/workflows/auto-release.yml, .github/workflows/bernstein-ci-fix.yml, .github/workflows/bernstein-pr-review.yml, .github/workflows/ci.yml, .github/workflows/cifuzz-pr.yml, .github/workflows/cluster-tunnel-e2e.yml, .github/workflows/codeql.yml, .github/workflows/contract-drift-autofix.yml, .github/workflows/dependency-review.yml
  Pipeline Topology and Data Flow
    · Workflow Hierarchy Diagram
  CI Gatekeeper and Planner
  Automated Release and Reconcile Loop
    · Success-Triggered Release
    · Protocol Compatibility Gate
  Supply Chain Security and Attestations
  Self-Healing Workflows
    · Auto-Heal v2
    · Bernstein CI Fix (Fallback)
  Distribution and Infrastructure
    · Docker Publishing
    · Specialized Pipelines
  Testing and Verification Pipelines

## · Docker and Sandbox Backends  (L8476)
  源文件: Dockerfile, action/entrypoint.sh, deploy/github-app/app.yml, deploy/grafana/dashboards/bernstein-otel.json, deploy/grafana/provisioning/dashboards/bernstein.yml, deploy/helm/bernstein/Chart.yaml, deploy/otel-collector/otel-collector-config.yaml, deploy/prometheus/prometheus.yml, docker-compose.yaml, docker/demo/Dockerfile, docker/demo/demo-cycle.sh, docs/architecture/sandbox.md
  Docker Image Hierarchy
    · Cluster Deployment (Docker Compose)
  Sandbox Backend Protocol
    · Registry and Discovery
    · Backend Capabilities
  First-Party Backends
    · Worktree Backend
    · Docker Backend
    · MicroVM Backend (libkrun / Firecracker)
  Web Sandbox and Self-Testing
    · Execution Flow
  Sandbox Escape Detection and Health Checks
    · Pre-flight Validation
    · Audit and Lineage

## · Testing Strategy  (L8653)
  源文件: .coverage-baseline.json, .github/workflows/coverage-ratchet.yml, benchmarks/bench_orchestrator.py, benchmarks/bench_task_store.py, benchmarks/swe_bench/run.py, docs/assets/ascii_logo.md, docs/contributing/testing.md, docs/operations/coverage-ratchet.md, scripts/coverage_ratchet.py, src/bernstein/core/routes/api_v1.py, tests/chaos/README.md, tests/chaos/test_server_restart.py
  The Test Pyramid
    · Quality Gates
  Test Infrastructure and Patterns
    · Core Fixtures
  Integration, Chaos, and Pentest Suites
    · Integration Flow: Code Entity Mapping
    · Adversarial and Chaos Testing
  Benchmarking and Performance
    · Task Store Latency

## · Test Infrastructure and Patterns  (L8787)
  源文件: .clusterfuzzlite/Dockerfile, .clusterfuzzlite/project.yaml, .coverage-baseline.json, .github/workflows/coverage-ratchet.yml, benchmarks/bench_orchestrator.py, benchmarks/bench_task_store.py, benchmarks/swe_bench/run.py, docs/assets/ascii_logo.md, docs/contributing/testing.md, docs/operations/coverage-ratchet.md, scripts/check_data_freshness.py, scripts/coverage_ratchet.py
  Subprocess-based Test Runner
    · Key Features
  Test Fixtures and Global Guards
    · Memory and Environment Guards
    · Agent Card Keystore Isolation
  Integration Test Patterns
    · The Integration Mock Adapter
    · Data Flow: Integration Task Execution
  Coverage Ratchet and Quality Gates
    · Ratchet Levels
    · Fuzzing and Mutation
  Performance Benchmarking
    · Component Association Map

## · Integration, Chaos, and Pentest Suites  (L8938)
  源文件: .github/workflows/a2a-federation-e2e.yml, .github/workflows/airgap-e2e.yml, .github/workflows/bernstein-issues-decompose.yml, .github/workflows/cluster-e2e.yml, .github/workflows/dependabot-auto-merge.yml, .github/workflows/eval-nightly.yml, .github/workflows/license-compliance.yml, .github/workflows/nightly-deep-tests.yml, .github/workflows/pentest.yml, .github/workflows/soc2-evidence-nightly.yml, docs/ENTERPRISE.md, docs/examples/agent-prompt-template.md
  Integration Test Patterns
    · Full Lifecycle and Plan Execution
    · Test Infrastructure
  Chaos Engineering
    · Server Kill and Recovery
    · Chaos CLI (`bernstein chaos`)
    · Recovery Flow Diagram
  Adversarial Pentest Suite
    · Attack Surfaces and Coverage
    · Security Entity Mapping
  Nightly Deep Test Workflows
    · Nightly Evaluation Driver

## · Contributing and Development  (L9124)
  源文件: .clusterfuzzlite/build.sh, .clusterfuzzlite/requirements.txt, .cursor/rules/module-map.mdc, .cursor/rules/overview.mdc, .goosehints, AGENTS.md, CLAUDE.md, CONTRIBUTORS.md, CONVENTIONS.md, README.md, docs/adapters/ADAPTER_GUIDE.md, docs/architecture/DEPENDENCY_RESOLVER.md
  Development Environment Setup
    · Prerequisites
    · Setup Steps
    · Optional Dependencies
  Coding Conventions and Documentation
    · Core Convention Files
    · The Module Map
  Development Workflow
    · PR Process and Code Review
    · The `agents_md` Dogfood Test
    · README API Coverage
  Technical Implementation: Documentation Sync
    · Documentation Sync Flow
  Internationalization (i18n)
  Testing and Verification
    · Execution Bootstrap Flow

## · Glossary  (L9319)
  源文件: .cursor/rules/module-map.mdc, .cursor/rules/overview.mdc, .goosehints, .plugin/plugin.json, AGENTS.md, CHANGELOG.md, CLAUDE.md, CONVENTIONS.md, README.md, docs/ENTERPRISE.md, docs/adapters/ADAPTER_GUIDE.md, docs/architecture/plans.md
  Core System Concepts
    · .sdd (State Directory)
    · Audit Chain
    · Task Lifecycle
    · Natural Language to Code Entity Map: Orchestration
  Agent & Adapter Terms
    · Adapter
    · Agent Card
    · Lineage
    · Natural Language to Code Entity Map: Agent Spawning
  Technical Abbreviations
  Component Directory
    · Core Orchestration (`src/bernstein/core/`)
    · CLI Commands (`src/bernstein/cli/`)