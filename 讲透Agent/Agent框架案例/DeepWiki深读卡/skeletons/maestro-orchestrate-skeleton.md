# Skeleton: maestro-orchestrate（30 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 5KB | 2 | ~0 | 10 |
| 2 | Getting Started | L112 | 7KB | 2 | ~4 | 8 |
| 3 | Command Reference & Cheatsheet | L316 | 8KB | 2 | ~6 | 11 |
| 4 | Core Architecture | L476 | 6KB | 2 | ~1 | 10 |
| 5 | Generator Pipeline | L608 | 8KB | 2 | ~2 | 11 |
| 6 | Orchestration Workflow | L759 | 8KB | 2 | ~2 | 13 |
| 7 | Session State Management | L926 | 7KB | 2 | ~5 | 10 |
| 8 | Specialist Agent Roster | L1094 | 6KB | 2 | ~5 | 13 |
| 9 | MCP Server | L1229 | 6KB | 2 | ~4 | 10 |
| 10 | MCP Tool Packs | L1371 | 8KB | 2 | ~5 | 18 |
| 11 | Plan Validation & DAG Checker | L1536 | 8KB | 2 | ~1 | 13 |
| 12 | Runtime Targets | L1724 | 6KB | 1 | ~4 | 10 |
| 13 | Gemini CLI Runtime | L1865 | 7KB | 2 | ~4 | 10 |
| 14 | Claude Code Runtime | L2013 | 7KB | 2 | ~7 | 10 |
| 15 | Codex Runtime | L2174 | 6KB | 2 | ~4 | 10 |
| 16 | Qwen Code Runtime | L2320 | 6KB | 2 | ~5 | 9 |
| 17 | Hook System | L2468 | 5KB | 2 | ~2 | 8 |
| 18 | Hook Runner & Adapter Pattern | L2591 | 7KB | 2 | ~2 | 12 |
| 19 | Hook Logic & Policy Enforcer | L2738 | 7KB | 2 | ~4 | 6 |
| 20 | CI/CD & Release Pipeline | L2896 | 5KB | 2 | ~0 | 9 |
| 21 | GitHub Actions Workflows | L3008 | 7KB | 2 | ~3 | 13 |
| 22 | Idempotent Publishing & Dist-Tag Policy | L3140 | 7KB | 2 | ~2 | 9 |
| 23 | Git Hooks & Commit Conventions | L3284 | 7KB | 1 | ~6 | 13 |
| 24 | Testing Infrastructure | L3434 | 7KB | 2 | ~1 | 10 |
| 25 | Unit Tests | L3555 | 9KB | 2 | ~2 | 19 |
| 26 | Integration & Transform Tests | L3724 | 8KB | 2 | ~1 | 9 |
| 27 | Contributing Guide | L3880 | 6KB | 2 | ~0 | 12 |
| 28 | Adding Agents & Entry Points | L4032 | 7KB | 2 | ~4 | 10 |
| 29 | Version Management & Release Artifacts | L4202 | 7KB | 2 | ~0 | 6 |
| 30 | Glossary | L4367 | 6KB | 2 | ~5 | 20 |


## · Overview  (L6)
  源文件: ARCHITECTURE.md, CHANGELOG.md, OVERVIEW.md, README.md, docs/architecture.md, docs/overview.md, docs/usage.md, package.json, plugins/maestro/.mcp.json, plugins/maestro/README.md
  System Concept
    · From Natural Language to Code Entities
  Key Capabilities
  Project Structure
  Wiki Organization
    · 1.1 [Getting Started](#1.1)
    · 1.2 [Command Reference & Cheatsheet](#1.2)
    · 2. [Core Architecture](#2)

## · Getting Started  (L112)
  源文件: .gitignore, CONTRIBUTING.md, GEMINI.md, USAGE.md, docs/architecture.md, docs/overview.md, docs/usage.md, package.json
  Prerequisites
  Development Setup
    · 1. Installation
    · 2. Git Hooks
    · 3. Build & Generate
  Key Commands
  System Data Flow: Source to Runtime
    · Build Pipeline Architecture
  First-Run Walkthrough by Runtime
    · Common Startup Logic
    · 1. Gemini CLI
    · 2. Claude Code
    · 3. Codex
    · 4. Qwen Code
  Workspace State Initialization
    · Workspace Initialization Mapping
  Core Configuration

## · Command Reference & Cheatsheet  (L316)
  源文件: .gitignore, EXAMPLES.md, GEMINI.md, USAGE.md, commands/maestro/execute.toml, commands/maestro/orchestrate.toml, commands/maestro/resume.toml, docs/maestro-cheatsheet.md, src/entry-points/core-command-registry.js, src/entry-points/registry.js, tests/unit/doc-drift-guard.test.js
  1. Runtime Command Matrix
    · 1.1 Command Remapping Logic
  2. Command Implementation & Data Flow
    · 2.1 Registry Structure
    · 2.2 Execution Data Flow
  3. Detailed Command Reference
    · 3.1 Orchestrate
    · 3.2 Execute
    · 3.3 Status
    · 3.4 Resume
  4. Specialist Command Architecture
    · 4.1 Standalone Workflow Protocols
  5. Summary Cheatsheet

## · Core Architecture  (L476)
  源文件: CHANGELOG.md, README.md, claude/src/references/architecture.md, docs/architecture.md, docs/overview.md, docs/usage.md, plugins/maestro/.mcp.json, plugins/maestro/README.md, plugins/maestro/src/references/architecture.md, src/references/architecture.md
    · The Canonical Source Pattern
    · Generator Pipeline
    · Orchestration Workflow
    · Session State Management
    · Specialist Agent Roster
    · Runtime Target Relationship

## · Generator Pipeline  (L608)
  源文件: docs/architecture.md, docs/overview.md, docs/runtime-codex.md, docs/runtime-gemini.md, docs/runtime-qwen.md, docs/usage.md, scripts/generate.js, src/generator/entry-point-expander.js, src/generator/payload-builder.js, tests/integration/entry-point-templates.test.js, tests/integration/zero-diff.test.js
  Pipeline Overview
    · Data Flow: Source to Runtime
  The Manifest System
    · Transform Pipeline
  Entry-Point Expansion
    · Platform Mapping Logic
    · Name Remapping
  Detached Payloads and Pruning
    · Payload Building
    · Stale Pruning
  Zero-Drift Guarantee
    · CI Enforcement

## · Orchestration Workflow  (L759)
  源文件: .gitignore, CHANGELOG.md, GEMINI.md, USAGE.md, docs/architecture.md, docs/flow.md, docs/overview.md, docs/usage.md, plugins/maestro/.mcp.json, src/skills/shared/design-dialogue/SKILL.md, src/skills/shared/execution/SKILL.md, src/skills/shared/implementation-planning/SKILL.md
  1. Workflow Modes
    · 1.1 Standard Workflow
    · 1.2 Express Workflow
  2. The 41-Step Orchestration Sequence
    · 2.1 Phase 1: Design
    · 2.2 Phase 2: Planning
    · 2.3 Phase 3: Execution
  3. Implementation and Data Flow
    · 3.1 Code Entity Mapping: Orchestration Logic
    · 3.2 HARD-GATE Enforcement
  4. Session Lifecycle
    · 4.1 Lifecycle Diagram
    · 4.2 Key Lifecycle Tools

## · Session State Management  (L926)
  源文件: CHANGELOG.md, claude/src/mcp/handlers/session-state-tools.js, docs/architecture.md, docs/overview.md, docs/usage.md, plugins/maestro/.mcp.json, plugins/maestro/src/mcp/handlers/session-state-tools.js, src/mcp/handlers/session-state-tools.js, src/skills/shared/session-management/SKILL.md, tests/unit/session-state-tools.test.js
  State Persistence Model
    · Directory Structure
    · The `active-session.md` Format
  Session Lifecycle & Transitions
    · 1. Initialization (The Design Gate)
    · 2. Phase Execution & Reconciliation
    · 3. Archival
    · Data Flow: State Transitions
  Technical Implementation
    · Transactional Safety: `withSessionState`
    · The MCP Tool Pack (Session)
    · Entity Mapping: MCP to Implementation
  Hook-Level vs. Orchestration State

## · Specialist Agent Roster  (L1094)
  源文件: .gitignore, GEMINI.md, README.md, USAGE.md, agents/architect.md, agents/coder.md, agents/debugger.md, agents/refactor.md, agents/tester.md, claude/src/platforms/shared/agent-names.js, plugins/maestro/README.md, src/platforms/shared/agent-names.js
  Specialist Domains & Capabilities
    · Agent Taxonomy by Domain
    · Capability Tiers (Access Control)
  Agent Lifecycle & Delegation
    · Stub Generation & Naming
    · Data Flow: get_agent Delegation
  Frontmatter Schema Reference
  Implementation Details
    · get_agent Tool
    · Agent Disabling

## · MCP Server  (L1229)
  源文件: CHANGELOG.md, claude/src/mcp/maestro-server.js, claude/src/version.json, gemini-extension.json, package-lock.json, plugins/maestro/.codex-plugin/plugin.json, plugins/maestro/.mcp.json, plugins/maestro/src/mcp/maestro-server.js, plugins/maestro/src/version.json, src/mcp/maestro-server.js
    · Purpose and Scope
  Architecture & Lifecycle
    · Server Startup Flow
    · Connection Strategy by Runtime
  Tool Pack Overview
    · 1. Workspace Pack
    · 2. Session Pack
    · 3. Content Pack
  Plan Validation & Safety
    · Validation Pipeline
  Code Entity Mapping
  Configuration & Environment

## · MCP Tool Packs  (L1371)
  源文件: CHANGELOG.md, claude/src/mcp/handlers/get-runtime-context.js, claude/src/mcp/handlers/session-state-core.js, claude/src/mcp/handlers/session-state-tools.js, claude/src/mcp/handlers/validate-plan.js, claude/src/mcp/validation/agent-checker.js, claude/src/mcp/validation/schema-checker.js, claude/src/platforms/claude/runtime-config.js, docs/architecture.md, docs/overview.md, docs/usage.md, plugins/maestro/.mcp.json
    · Tool Pack Architecture
  1. Workspace Pack
    · Key Tools
    · Natural Language to Code: Plan Validation Flow
  2. Session Pack
    · Lifecycle and Design Gates
    · Tools Reference
  3. Content Pack
    · Content Resolution Logic
    · Runtime Context Schema
  Implementation Details
    · Data Flow: Content Materialization
    · Dependency Management

## · Plan Validation & DAG Checker  (L1536)
  源文件: CHANGELOG.md, claude/src/mcp/handlers/session-state-core.js, claude/src/mcp/handlers/validate-plan.js, claude/src/mcp/validation/agent-checker.js, claude/src/mcp/validation/schema-checker.js, claude/src/platforms/claude/runtime-config.js, plugins/maestro/.mcp.json, tests/unit/adapter-factory.test.js, tests/unit/assess-task-complexity.test.js, tests/unit/check-layer-boundaries.test.js, tests/unit/line-reader.test.js, tests/unit/manifest-curator.test.js
  Validation Pipeline Overview
    · Data Flow & Logic Execution
  1. Schema & Structural Validation
  2. Agent Capability Enforcement
    · Capability Mismatch Detection
  3. DAG Analysis & Cycle Detection
    · Core Algorithms
  4. Parallelization Safety
    · File Overlap Checker
  5. Parallelization Profile Output

## · Runtime Targets  (L1724)
  源文件: QWEN.md, README.md, docs/runtime-claude.md, docs/runtime-codex.md, docs/runtime-gemini.md, docs/runtime-qwen.md, gemini-extension.json, plugins/maestro/README.md, qwen-extension.json, scripts/generate.js
    · Supported Runtimes Overview
    · Shared Runtime Architecture
    · Gemini CLI Runtime
    · Claude Code Runtime
    · Codex Runtime
    · Qwen Code Runtime
    · Tool Mapping Comparison

## · Gemini CLI Runtime  (L1865)
  源文件: .gitignore, GEMINI.md, USAGE.md, claude/src/platforms/shared/hook-runner.js, commands/maestro/execute.toml, commands/maestro/orchestrate.toml, commands/maestro/resume.toml, gemini-extension.json, plugins/maestro/src/platforms/shared/hook-runner.js, src/platforms/shared/hook-runner.js
  Extension Configuration
    · Manifest Structure
    · Environment Variables
  Context and Instructions (`GEMINI.md`)
    · Startup Protocol
    · Tool Mapping
  Command Definitions
  Hook System and Lifecycle
    · Hook Data Flow
    · Hook Events
  MCP Server Wiring
    · Connection Details

## · Claude Code Runtime  (L2013)
  源文件: .claude-plugin/marketplace.json, claude/.claude-plugin/plugin.json, claude/README.md, claude/src/entry-points/core-command-registry.js, claude/src/entry-points/registry.js, claude/src/platforms/shared/adapters/claude-adapter.js, docs/runtime-claude.md, src/platforms/shared/adapters/claude-adapter.js, src/platforms/shared/adapters/gemini-adapter.js, tests/integration/policy-enforcer.test.js
  Directory Layout & Manifests
    · Plugin Architecture
  Dual-Resolution MCP Server
  Agent Naming and Delegation
  Lifecycle Hooks and Policy Enforcer
    · Hook Runner and Adapter
    · PreToolUse Policy Enforcer
  Command Remapping and Skills
    · Skill Types

## · Codex Runtime  (L2174)
  源文件: claude/src/version.json, docs/runtime-codex.md, docs/runtime-gemini.md, docs/runtime-qwen.md, package-lock.json, plugins/maestro/.codex-plugin/plugin.json, plugins/maestro/src/entry-points/core-command-registry.js, plugins/maestro/src/entry-points/registry.js, plugins/maestro/src/version.json, scripts/generate.js
  Configuration and Manifests
    · MCP Server Invocation
    · Workspace Resolution Strategy
  Runtime Architecture and Data Flow
    · Codex Entity Space Mapping
  Skills and Commands
    · Command Mapping Table
  Agent Delegation and State
    · Tool Mapping
    · State Isolation
  Generation Pipeline

## · Qwen Code Runtime  (L2320)
  源文件: QWEN.md, claude/src/platforms/shared/hook-runner.js, docs/runtime-codex.md, docs/runtime-gemini.md, docs/runtime-qwen.md, plugins/maestro/src/platforms/shared/hook-runner.js, qwen-extension.json, scripts/generate.js, src/platforms/shared/hook-runner.js
  Configuration and Manifests
    · Manifest: `qwen-extension.json`
    · Context File: `QWEN.md`
    · MCP Server Wiring
  Directory Structure
  Tool Name Remapping
    · Tool Mapping Table
  Hook System and Event Flow
    · Hook Events
    · Data Flow: Natural Language to Code Entity Space
  Implementation Architecture
    · Shared Command Surface

## · Hook System  (L2468)
  源文件: .githooks/lib/semantic-git.sh, .githooks/pre-commit, claude/src/platforms/shared/hook-runner.js, plugins/maestro/src/platforms/shared/hook-runner.js, src/platforms/shared/hook-runner.js, tests/integration/git-hooks.test.js, tests/integration/hook-entrypoints.test.js, tests/unit/platform-adapters.test.js
    · Architecture Overview
    · The Adapter Pattern
    · Hook Lifecycle & Session Context
    · Integration & Reliability

## · Hook Runner & Adapter Pattern  (L2591)
  源文件: claude/src/core/stdin-reader.js, claude/src/platforms/shared/adapters/claude-adapter.js, claude/src/platforms/shared/adapters/conventions.js, plugins/maestro/src/core/stdin-reader.js, plugins/maestro/src/platforms/shared/adapters/conventions.js, src/core/stdin-reader.js, src/platforms/shared/adapters/claude-adapter.js, src/platforms/shared/adapters/conventions.js, src/platforms/shared/adapters/gemini-adapter.js, src/platforms/shared/adapters/qwen-adapter.js, tests/integration/hook-entrypoints.test.js, tests/unit/platform-adapters.test.js
  Architecture Overview
    · Hook Dispatch Flow
  The Adapter Factory Contract
    · Key Functions
  Runtime Specifics
    · Gemini Adapter
    · Claude Adapter
    · Qwen Adapter
  Data Normalization & Code Entities
  Implementation Details
    · STDIN Handling
    · Adapter Discovery
    · Error Handling & Fallbacks

## · Hook Logic & Policy Enforcer  (L2738)
  源文件: claude/src/platforms/shared/hook-runner.js, plugins/maestro/src/platforms/shared/hook-runner.js, src/platforms/shared/hook-runner.js, tests/integration/policy-enforcer.test.js, tests/integration/source-of-truth.test.js, tests/unit/hook-logic.test.js
  Hook Logic Architecture
    · Component Overview
  Session Context & State Flow
    · Data Flow: Natural Language to Code Entity Space
  The Hook Modules
    · 1. session-start-logic
    · 2. before-agent-logic
    · 3. after-agent-logic
  Policy Enforcer (Claude/Bash Security)
    · Protected Operations
    · Recursive Inspection

## · CI/CD & Release Pipeline  (L2896)
  源文件: .github/workflows/generator-check.yml, .github/workflows/nightly.yml, .github/workflows/prepare-release.yml, .github/workflows/release.yml, docs/cicd.md, justfile, scripts/npm-publish-idempotent.js, tests/unit/npm-publish-idempotent.test.js, tests/unit/workflow-security.test.js
  Workflow Ecosystem
    · CI/CD High-Level Flow
  Source-of-Truth Enforcement
  Multi-Stage Release Process
    · Release Promotion Path
  Local Development & Conventions
  Child Pages

## · GitHub Actions Workflows  (L3008)
  源文件: .github/workflows/generator-check.yml, .github/workflows/nightly.yml, .github/workflows/prepare-release.yml, .github/workflows/preview.yml, .github/workflows/rc.yml, .github/workflows/release.yml, claude/src/core/version.js, docs/cicd.md, justfile, plugins/maestro/src/core/version.js, scripts/npm-publish-idempotent.js, tests/unit/npm-publish-idempotent.test.js
    · Workflow Ecosystem
    · CI Gates & Enforcement
    · Release Pipeline Implementation
    · Workflow Security & Tokens

## · Idempotent Publishing & Dist-Tag Policy  (L3140)
  源文件: .github/workflows/release.yml, docs/cicd.md, scripts/npm-publish-idempotent.js, scripts/package-release-artifacts.js, scripts/release-artifact-manifest.js, scripts/verify-npm-pack.js, scripts/verify-release-artifacts.js, tests/unit/npm-publish-idempotent.test.js, tests/unit/workflow-security.test.js
  Overview of the Publishing Logic
    · Key Logic Flow
    · Natural Language to Code Entity Mapping
  Dist-Tag Policy
    · Validation Rules
  The `latest`-tag Repair Mechanism
    · Repair Scenarios
  Implementation Details
    · Execution Flow
    · Error Handling
  CI/CD Integration

## · Git Hooks & Commit Conventions  (L3284)
  源文件: .githooks/commit-msg, .githooks/lib/semantic-git.sh, .githooks/pre-commit, .githooks/pre-push, .github/ISSUE_TEMPLATE/bug_report.md, .github/ISSUE_TEMPLATE/config.yml, .github/ISSUE_TEMPLATE/feature_request.md, .github/PULL_REQUEST_TEMPLATE.md, .github/workflows/commit-message-check.yml, CODE_OF_CONDUCT.md, SECURITY.md, scripts/install-git-hooks.js
  Local Hook Activation
    · scripts/install-git-hooks.js
  Commit Message Conventions
    · Validation Logic
    · Allowed Types
  Semantic Branching Rules
    · Branch Formats
  Hook Implementation Detail
    · Hook Execution Flow
    · Source-of-Truth Drift Check
  CI Enforcement
    · Workflow Jobs
  Testing Infrastructure

## · Testing Infrastructure  (L3434)
  源文件: tests/integration/hook-entrypoints.test.js, tests/integration/source-of-truth.test.js, tests/unit/adapter-factory.test.js, tests/unit/assess-task-complexity.test.js, tests/unit/check-layer-boundaries.test.js, tests/unit/hook-logic.test.js, tests/unit/line-reader.test.js, tests/unit/manifest-curator.test.js, tests/unit/platform-adapters.test.js, tests/unit/protocol-dispatcher.test.js
    · Test Suite Overview
  Test Categories & Tooling
    · Layer Boundary Enforcement
    · Protocol & I/O Validation
    · Test Entity Relationship
  Unit Tests
  Integration & Transform Tests

## · Unit Tests  (L3555)
  源文件: EXAMPLES.md, claude/src/mcp/handlers/session-state-tools.js, docs/maestro-cheatsheet.md, plugins/maestro/src/mcp/handlers/session-state-tools.js, src/mcp/handlers/session-state-tools.js, tests/unit/adapter-conventions.test.js, tests/unit/adapter-factory.test.js, tests/unit/assess-task-complexity.test.js, tests/unit/check-layer-boundaries.test.js, tests/unit/doc-drift-guard.test.js, tests/unit/lib-naming.test.js, tests/unit/line-reader.test.js
    · Core Test Categories
    · Protocol & Communication Tests
    · Platform & Adapter Infrastructure
    · Integrity & Drift Guards
    · State & Validation

## · Integration & Transform Tests  (L3724)
  源文件: .github/workflows/release.yml, tests/integration/entry-point-templates.test.js, tests/integration/release-artifacts.test.js, tests/integration/source-of-truth.test.js, tests/integration/thin-entrypoints.test.js, tests/integration/zero-diff.test.js, tests/unit/hook-logic.test.js, tests/unit/release-artifact-manifest.test.js, tests/unit/workflow-security.test.js
  Overview and Scope
    · Testing Architecture
  Transform & Entry-Point Tests
    · Entry-Point Mapping
    · Logic Validation
  Integration Invariants
    · Zero-Diff Guarantee
    · Thin Entrypoint Design
    · Prohibited Patterns
  Release Artifact Validation
    · Packaging Checks
  Hook & Workflow Security
    · Hook Logic Validation
    · CI/CD Security

## · Contributing Guide  (L3880)
  源文件: .githooks/commit-msg, .githooks/pre-push, .github/ISSUE_TEMPLATE/bug_report.md, .github/ISSUE_TEMPLATE/config.yml, .github/ISSUE_TEMPLATE/feature_request.md, .github/PULL_REQUEST_TEMPLATE.md, .github/workflows/commit-message-check.yml, CODE_OF_CONDUCT.md, CONTRIBUTING.md, LICENSE, SECURITY.md, scripts/install-git-hooks.js
  Development Workflow
    · Setup and Tooling
    · The Canonical Source Rule
    · Development Cycle Diagram: Source to Runtime
  Semantic Git Conventions
    · Branch Naming
    · Commit Messages
    · Git Hook Interaction
  PR Process and Community Standards
    · Pull Request Steps
    · Community Standards
  Specialized Contribution Topics
    · Adding Agents & Entry Points
    · Version Management & Release Artifacts

## · Adding Agents & Entry Points  (L4032)
  源文件: CONTRIBUTING.md, EXAMPLES.md, agents/architect.md, agents/coder.md, agents/debugger.md, agents/refactor.md, docs/maestro-cheatsheet.md, src/entry-points/registry.js, src/generator/entry-point-expander.js, tests/unit/doc-drift-guard.test.js
  Adding a New Specialist Agent
    · 1. Define the Agent File
    · 2. Configure Frontmatter Schema
    · 3. Capability Tiers and Tools
    · 4. Implementation Flow
  Adding a New Entry Point
    · 1. Register the Command
    · 2. Configure Runtime Name Remapping
    · 3. Template Selection
    · 4. Update Doc-Drift Guard
  Verification Checklist

## · Version Management & Release Artifacts  (L4202)
  源文件: scripts/package-release-artifacts.js, scripts/release-artifact-manifest.js, scripts/release-version-metadata.js, scripts/update-versions.js, src/core/version.js, tests/unit/update-versions.test.js
  Version Synchronization
    · The update-versions.js Pipeline
    · Version Resolution Logic
  Release Artifact Packaging
    · The Packaging Workflow
    · Code Entity to Artifact Mapping
  Data Flow: Version Update to Release
    · Critical Verification Checks

## · Glossary  (L4367)
  源文件: .gitignore, CHANGELOG.md, EXAMPLES.md, GEMINI.md, README.md, USAGE.md, claude/src/version.json, docs/architecture.md, docs/flow.md, docs/maestro-cheatsheet.md, docs/overview.md, docs/usage.md
  Core Concepts & Workflow Terms
  Architectural Entities
    · Source-First Generation
    · Session State
  MCP (Model Context Protocol)
  Runtime Specifics
    · Runtime Abbreviations & Jargon
  Internal Tools & Scripts