# Skeleton: sage（38 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | SAGE Overview | L6 | 6KB | 2 | ~1 | 13 |
| 2 | Getting Started | L128 | 6KB | 2 | ~0 | 11 |
| 3 | Key Concepts and Terminology | L313 | 6KB | 2 | ~5 | 9 |
| 4 | Core Architecture | L455 | 7KB | 2 | ~2 | 16 |
| 5 | Memory Lifecycle and Data Model | L600 | 6KB | 2 | ~3 | 7 |
| 6 | Consensus Engine (CometBFT & ABCI) | L757 | 8KB | 2 | ~1 | 20 |
| 7 | App Validators and Proof of Experience (PoE) | L926 | 7KB | 2 | ~4 | 8 |
| 8 | Transaction Types and Codec | L1064 | 8KB | 3 | ~8 | 16 |
| 9 | Storage Layer | L1250 | 5KB | 2 | ~2 | 10 |
| 10 | SQLite Store (Personal Mode) | L1375 | 6KB | 2 | ~2 | 7 |
| 11 | PostgreSQL Store and BadgerDB (Multi-Node Mode) | L1511 | 6KB | 2 | ~4 | 11 |
| 12 | Synaptic Ledger (Vault Encryption) | L1661 | 7KB | 2 | ~2 | 7 |
| 13 | Agent Interfaces | L1819 | 6KB | 2 | ~1 | 12 |
| 14 | MCP Server and Tools | L1972 | 7KB | 2 | ~2 | 17 |
| 15 | REST API | L2150 | 9KB | 2 | ~2 | 22 |
| 16 | Python SDK | L2323 | 8KB | 2 | ~2 | 20 |
| 17 | CEREBRUM Dashboard | L2485 | 6KB | 2 | ~1 | 7 |
| 18 | Dashboard Backend (Handler Layer) | L2621 | 7KB | 2 | ~2 | 14 |
| 19 | Dashboard Frontend (CEREBRUM SPA) | L2767 | 7KB | 2 | ~4 | 10 |
| 20 | Memory Import Pipeline | L2945 | 6KB | 2 | ~2 | 6 |
| 21 | Agent Identity and Access Control | L3084 | 6KB | 2 | ~4 | 11 |
| 22 | Agent Identity Management | L3226 | 8KB | 2 | ~2 | 14 |
| 23 | RBAC, Organizations, and Federation | L3385 | 7KB | 2 | ~2 | 17 |
| 24 | Inter-Agent Pipeline | L3522 | 8KB | 2 | ~2 | 10 |
| 25 | Embedding Providers | L3683 | 6KB | 2 | ~4 | 13 |
| 26 | CLI Reference (sage-gui) | L3838 | 6KB | 2 | ~7 | 13 |
| 27 | Configuration Reference | L3981 | 7KB | 3 | ~4 | 7 |
| 28 | Claude Code Integration and Hooks | L4147 | 7KB | 2 | ~3 | 9 |
| 29 | Deployment and Infrastructure | L4308 | 7KB | 2 | ~2 | 12 |
| 30 | Multi-Node Docker Deployment | L4460 | 7KB | 2 | ~2 | 10 |
| 31 | Platform Installers and Release Pipeline | L4624 | 7KB | 2 | ~0 | 16 |
| 32 | Redeployment Orchestrator | L4781 | 9KB | 2 | ~3 | 9 |
| 33 | Browser Extension | L4939 | 7KB | 2 | ~2 | 19 |
| 34 | Testing | L5096 | 4KB | 2 | ~2 | 17 |
| 35 | Unit and Integration Tests | L5231 | 8KB | 2 | ~1 | 16 |
| 36 | E2E and Load Tests | L5387 | 7KB | 2 | ~2 | 6 |
| 37 | Integrations and Extensions | L5534 | 6KB | 2 | ~2 | 7 |
| 38 | Glossary | L5658 | 7KB | 2 | ~3 | 17 |


## · SAGE Overview  (L6)
  源文件: README.md, docs/ARCHITECTURE.md, docs/GETTING_STARTED.md, docs/connect.html, docs/index.html, papers/Paper1 - Agent Memory Infrastructure - Byzantine-Resilient Institutional Memory for Multi-Agent Systems.pdf, papers/Paper2 - Consensus-Validated Memory Improves Agent Performance on Complex Tasks.pdf, papers/Paper3 - Institutional Memory as Organizational Knowledge - AI Agents That Learn Their Jobs from Experience Not Instructions.pdf, papers/README.md, sdk/python/README.md, sdk/python/pyproject.toml, sdk/python/src/sage_sdk/__init__.py
  Deployment Modes
  System Architecture
    · High-Level Data Flow
    · Component Interaction
  Major Subsystems
  Research and Performance
  Child Pages

## · Getting Started  (L128)
  源文件: cmd/sage-gui/config.go, cmd/sage-gui/main.go, cmd/sage-gui/mcp.go, cmd/sage-gui/vault.go, cmd/sage-gui/wizard.go, docs/ARCHITECTURE.md, docs/GETTING_STARTED.md, docs/connect.html, docs/index.html, sdk/python/README.md, sdk/python/src/sage_sdk/models.py
  1. Installation
    · Build from Source
  2. Initial Setup Wizard
    · Running the Wizard
    · Setup Data Flow
  3. Connecting AI via MCP
    · Automatic Installation (Claude Code)
    · Manual Configuration (Claude Desktop)
  4. Starting the Node
  5. Verifying the System
    · Identity Resolution Logic
    · First Tool Call: Inception

## · Key Concepts and Terminology  (L313)
  源文件: README.md, internal/mcp/server.go, internal/mcp/tools.go, internal/memory/model.go, internal/store/postgres.go, internal/store/sqlite.go, internal/store/store.go, sdk/python/pyproject.toml, sdk/python/src/sage_sdk/__init__.py
  Core Data Entities
    · MemoryRecord
    · Domain
    · KnowledgeTriple
  The Consensus & Validation Layer
    · CometBFT & ABCI
    · Proof of Experience (PoE)
    · Synaptic Ledger (Vault)
  System Architecture Diagrams
    · From Natural Language to Code Entities
    · Memory Lifecycle and Validation Flow
  Glossary of Key Components

## · Core Architecture  (L455)
  源文件: .github/workflows/ci.yml, .github/workflows/release.yml, api/rest/agent_handler.go, cmd/sage-gui/node.go, deploy/Dockerfile.abci, docs/ARCHITECTURE.md, docs/GETTING_STARTED.md, go.mod, go.sum, internal/abci/app.go, internal/abci/app_test.go, internal/abci/migrate.go
  End-to-End Data Flow
    · Memory Submission Pipeline
  Major System Layers
    · 1. The Interface Layer (MCP & REST)
    · 2. The Consensus Engine (CometBFT & ABCI)
    · 3. Validation & Proof of Experience (PoE)
    · 4. The Storage Tier
  Internal Package Structure
    · System Package Interactions
  Deployment Topologies
    · Personal Deployment (`sage-gui`)
    · Multi-Node Cluster (`amid`)

## · Memory Lifecycle and Data Model  (L600)
  源文件: internal/mcp/server.go, internal/mcp/tools.go, internal/memory/confidence.go, internal/memory/model.go, internal/store/postgres.go, internal/store/sqlite.go, internal/store/store.go
  The MemoryRecord Data Model
    · Memory Types
  Memory Status State Machine
    · State Transition Diagram
  Knowledge Representation: Triples and Links
    · Knowledge Triples
    · Memory Links
  Confidence Decay and Corroboration
    · The Formula
    · Implementation Details
  Data Flow: Natural Language to Storage
    · Natural Language to Code Entity Space
    · Storage Implementation Summary

## · Consensus Engine (CometBFT & ABCI)  (L757)
  源文件: .github/workflows/ci.yml, .github/workflows/release.yml, LICENSE, api/rest/agent_handler.go, cmd/amid/main.go, cmd/sage-cli/main.go, cmd/sage-gui/node.go, deploy/Dockerfile.abci, go.mod, go.sum, internal/abci/app.go, internal/abci/app_test.go
  Overview
    · Deployment Modes
  The ABCI Application (`SageApp`)
    · Block Execution Flow
  Transaction Structure (`ParsedTx`)
    · Data Flow: Natural Language to On-Chain Code
    · Transaction Types
  4-Validator Quorum Model
    · Quorum Configuration
    · Validator State Management
  Deployment with `amid`
    · Integration Diagram: `amid` Component Architecture
  Key Functions
    · `ComputeAppHash()`
    · `CheckTx()`
    · `FinalizeBlock()`

## · App Validators and Proof of Experience (PoE)  (L926)
  源文件: api/rest/access_handler.go, api/rest/dept_handler.go, api/rest/org_handler.go, api/rest/vote_handler.go, internal/appvalidator/manager.go, internal/appvalidator/manager_test.go, internal/appvalidator/validator.go, internal/appvalidator/validator_test.go
  App Validators
    · The Four Validators
    · Validator Orchestration and Quorum
  Proof of Experience (PoE)
    · Weight Computation Engine
    · Voting and Challenges
  Implementation Details
    · Key Derivation
    · Identity and Auth
    · Validator Scores and Epochs

## · Transaction Types and Codec  (L1064)
  源文件: LICENSE, api/rest/agent_handler.go, cmd/amid/main.go, cmd/sage-cli/main.go, internal/abci/app.go, internal/abci/app_test.go, internal/abci/migrate.go, internal/embedding/ollama.go, internal/mcp/tools_test.go, internal/store/badger.go, internal/tx/codec.go, internal/tx/codec_test.go
  Transaction Types (TxType)
  The ParsedTx Structure
    · Code Entity Space: ParsedTx
  Wire Format and Codec
    · Binary Layout
    · Encoding Logic
  Agent Identity Proofs
    · Proof Generation
    · Proof Verification
  Implementation Details
    · Key Functions
    · Error Handling
    · Data Flow: Transaction Broadcasting

## · Storage Layer  (L1250)
  源文件: api/rest/agent_handler.go, api/rest/helpers.go, deploy/docker-compose.yml, internal/abci/app.go, internal/abci/app_test.go, internal/abci/migrate.go, internal/store/badger.go, internal/store/postgres.go, internal/store/sqlite.go, internal/store/store.go
  Architecture Overview
    · Storage Interface Bridge
  Hybrid Storage Components
    · 1. SQLite Store (Personal Mode)
    · 2. PostgreSQL & pgvector (Multi-Node Mode)
    · 3. BadgerDB (On-Chain State)
    · 4. Synaptic Ledger (Encryption)
  Data Flow: Submission to Persistence
  Core Storage Interfaces

## · SQLite Store (Personal Mode)  (L1375)
  源文件: internal/store/postgres.go, internal/store/sqlite.go, internal/store/store.go, internal/vault/vault.go, internal/vault/vault_test.go, web/handler_ledger.go, web/handler_ledger_test.go
  Implementation Overview
    · Data Flow: Memory Submission
    · Code Entity Mapping
  Schema and Migrations
  Encryption Integration (Synaptic Ledger)
    · Encryption State Machine
    · Content Handling
  In-Memory Vector Search
  Pipeline and Message Management
  RedeploymentLock Mechanism

## · PostgreSQL Store and BadgerDB (Multi-Node Mode)  (L1511)
  源文件: api/rest/agent_handler.go, api/rest/helpers.go, deploy/docker-compose.yml, deploy/init.sql, internal/abci/app.go, internal/abci/app_test.go, internal/abci/migrate.go, internal/store/badger.go, internal/store/postgres.go, internal/store/sqlite.go, internal/store/store.go
  Hybrid Storage Architecture
    · Multi-Node Data Flow
  PostgreSQL and pgvector
    · Key Implementation Details
    · Schema: init.sql
  BadgerDB: On-Chain State
    · On-Chain Entities
    · Deterministic Hashing
  Multi-Node Deployment (Docker)
    · Service Topology
    · Startup Migrations

## · Synaptic Ledger (Vault Encryption)  (L1661)
  源文件: internal/store/postgres.go, internal/store/sqlite.go, internal/store/store.go, internal/vault/vault.go, internal/vault/vault_test.go, web/handler_ledger.go, web/handler_ledger_test.go
  Vault Architecture and Key Derivation
    · Key Derivation Flow (Argon2id)
    · The `vault.key` Format
  Data Flow: Code to Entity Mapping
    · Encryption Implementation Mapping
  Content and Embedding Encryption
    · Content Encryption
    · Embedding Encryption
  State Machine: Locked vs. Unlocked
    · Vault State Transitions
    · State Behavior
  Passphrase Management and Recovery
    · Passphrase Change
    · Recovery Key Mechanism

## · Agent Interfaces  (L1819)
  源文件: README.md, api/rest/memory_handler.go, api/rest/pipe_handler.go, api/rest/server.go, internal/mcp/server.go, internal/mcp/server_test.go, internal/mcp/tools.go, internal/store/pipeline_test.go, sdk/python/pyproject.toml, sdk/python/src/sage_sdk/__init__.py, sdk/python/src/sage_sdk/async_client.py, sdk/python/src/sage_sdk/client.py
    · Interface Overview
    · 1. MCP Server and Tools
    · 2. REST API
    · 3. Python SDK
    · Data Flow: Natural Language to Code Entity

## · MCP Server and Tools  (L1972)
  源文件: LICENSE, cmd/amid/main.go, cmd/sage-cli/main.go, cmd/sage-gui/config.go, cmd/sage-gui/mcp.go, cmd/sage-gui/mcp_test.go, extension/chrome/manifest.json, extension/manifest.firefox.json, extension/store-listing.md, internal/embedding/ollama.go, internal/mcp/server.go, internal/mcp/tools.go
  JSON-RPC 2.0 Implementation
    · Core Request/Response Loop
    · Data Flow: Tool Call to REST API
  SAGE Tools Reference
    · 1. Consciousness & Session Tools
    · 2. Memory Management Tools
    · 3. Pipeline & Task Tools
  Turn Discipline and Auto-Inception
    · Turn Discipline Enforcement
    · Auto-Inception
    · Memory Mode Configuration
  Technical Architecture Diagrams
    · Diagram 1: MCP Tool Dispatch Logic
    · Diagram 2: Identity Resolution and Server Initialization
  Configuration and Deployment
    · Identity Resolution Priority
    · Self-Healing Integration

## · REST API  (L2150)
  源文件: CONTRIBUTING.md, api/openapi.yaml, api/rest/access_handler.go, api/rest/dept_handler.go, api/rest/memory_handler.go, api/rest/middleware/auth.go, api/rest/middleware/middleware_test.go, api/rest/middleware/ratelimit.go, api/rest/org_handler.go, api/rest/server.go, api/rest/vote_handler.go, cmd/sage-gui/node_controller.go
  Server Architecture
    · Key Components
    · Data Flow: REST to Consensus
  Authentication and Security
    · Ed25519 Signature Scheme
    · Replay Protection
    · Rate Limiting
  Endpoint Categories
    · Memory Management
    · Governance and Validation
    · Agent and Organization
  Domain Access Control
  Request and Response Types

## · Python SDK  (L2323)
  源文件: .gitignore, CONTRIBUTING.md, api/openapi.yaml, api/rest/pipe_handler.go, docs/og-image.png, extension/build.sh, integrations/levelup/sage_bridge.py, internal/store/pipeline_test.go, papers/Paper4 - Longitudinal Learning in Governed Multi-Agent Systems - How Institutional Memory Improves Agent Performance Over Time.pdf, sdk/python/examples/async_example.py, sdk/python/examples/complete_walkthrough.py, sdk/python/examples/federation.py
  Core Components
    · Agent Identity (`AgentIdentity`)
    · SageClient and AsyncSageClient
    · Pydantic Models
  Data Flow: SDK to Consensus
  SDK Methods
    · Memory Operations
    · Pipeline Operations
  Integration Patterns
    · SageBridge Integration
    · Usage Example: Full Lifecycle
  Error Handling

## · CEREBRUM Dashboard  (L2485)
  源文件: web/handler.go, web/handler_test.go, web/import.go, web/network_handler.go, web/static/css/sage.css, web/static/js/api.js, web/static/js/app.js
    · System Overview
    · Code-to-System Mapping
    · Core Functionality
    · Data Flow: Dashboard to Consensus
    · Sub-Pages

## · Dashboard Backend (Handler Layer)  (L2621)
  源文件: internal/vault/vault.go, internal/vault/vault_test.go, web/handler.go, web/handler_ledger.go, web/handler_ledger_test.go, web/handler_pipeline.go, web/handler_test.go, web/import.go, web/network_handler.go, web/sse.go, web/sse_test.go, web/static/js/app.js
  Core Architecture and Data Flow
    · Entity Mapping: Natural Language to Code Space
  Authentication and RBAC
    · RBAC Resolution
  Real-time Events (SSE)
  Memory and Agent Management
    · On-Chain Broadcasting
    · Pre-Validation Quorum
  Synaptic Ledger (Vault) Integration
    · Key Functions:
  Update Orchestration

## · Dashboard Frontend (CEREBRUM SPA)  (L2767)
  源文件: web/handler.go, web/static/css/sage.css, web/static/js/api.js, web/static/js/app.js, web/static/js/components/confidence-badge.js, web/static/js/components/domain-filter.js, web/static/js/components/memory-card.js, web/static/js/pages/brain.js, web/static/js/pages/memory-detail.js, web/static/js/sse.js
  Core Technologies and Architecture
    · Data Flow: Real-time Updates
  BrainView: Force-Directed Visualization
    · Implementation Details
    · Navigation and Interaction
  Synaptic Ledger UI
    · State Machine Integration
  Import Pipeline (ChatGPT/Claude/Gemini)
    · Data Flow
  Task Board (Kanban)
  CSS Design System
    · Core Variables
    · Layout Components
  System Integration Map

## · Memory Import Pipeline  (L2945)
  源文件: web/autostart.go, web/handler_test.go, web/import.go, web/import_realdata_test.go, web/import_test.go, web/network_handler.go
  Import Workflow Overview
    · Two-Phase Import Flow
    · Data Flow Diagram: Import to Ledger
  Format Detection and Parsing
    · Supported Formats
    · Conversation Tree Walking
  Implementation Details
    · Processing and Enrichment
    · Component Interaction Diagram
  Validation and Error Handling

## · Agent Identity and Access Control  (L3084)
  源文件: api/rest/middleware/auth.go, api/rest/middleware/middleware_test.go, internal/auth/ed25519.go, internal/auth/ed25519_test.go, internal/store/postgres.go, internal/store/sqlite.go, internal/store/store.go, test/integration/helpers_test.go, web/handler_test.go, web/import.go, web/network_handler.go
  Identity Foundation: Ed25519 Keypairs
    · Identity Verification Flow
  Registration and On-Chain Presence
  Access Control and Hierarchy
    · Clearance Levels and RBAC
    · Organizational Hierarchy
    · Domain Access Grants
  Federation
  Summary of Identity Components

## · Agent Identity Management  (L3226)
  源文件: api/rest/middleware/auth.go, api/rest/middleware/middleware_test.go, cmd/sage-gui/config.go, cmd/sage-gui/mcp.go, internal/auth/ed25519.go, internal/auth/ed25519_test.go, internal/orchestrator/redeployer.go, internal/store/sqlite_test.go, test/integration/helpers_test.go, web/handler_test.go, web/import.go, web/network_handler.go
  Ed25519 Key Generation and Storage
    · Key Storage Formats
  Identity Resolution Priority Chain
    · Per-Project Isolation
  Request Signing and Verification
    · Authentication Data Flow
    · Request Signature Diagram
  Key Rotation and Redeployment
    · RotateAgentKey Process
  Claim Tokens and Pairing
    · Pairing Lifecycle
  Name Distinctions

## · RBAC, Organizations, and Federation  (L3385)
  源文件: api/rest/access_handler.go, api/rest/agent_handler.go, api/rest/dept_handler.go, api/rest/org_handler.go, api/rest/vote_handler.go, internal/abci/app.go, internal/abci/app_test.go, internal/abci/migrate.go, internal/store/badger.go, internal/store/postgres.go, internal/store/sqlite.go, internal/store/store.go
    · 1. Clearance Levels (RBAC Tiers)
    · 2. Organizational Hierarchy
    · 3. Domain-Scoped Access Grants
    · 4. Federation Agreements
    · 5. On-Chain Enforcement (ABCI)

## · Inter-Agent Pipeline  (L3522)
  源文件: api/rest/pipe_handler.go, internal/mcp/server.go, internal/mcp/tools.go, internal/store/pipeline_test.go, internal/store/postgres.go, internal/store/sqlite.go, internal/store/store.go, sdk/python/src/sage_sdk/async_client.py, sdk/python/src/sage_sdk/client.py, web/handler_pipeline.go
  System Overview
    · Pipeline Architecture and Data Flow
  Core Components
    · 1. PipelineStore Interface
    · 2. Message Schema
  Agent Interaction (MCP Tools)
    · `sage_pipe` (Send)
    · `sage_inbox` (Receive)
    · `sage_pipe_result` (Complete)
  Passive Discovery via `sage_turn`
  Maintenance and Cleanup
    · Expiry and Purging
    · Dashboard Visibility

## · Embedding Providers  (L3683)
  源文件: .gitignore, LICENSE, cmd/amid/main.go, cmd/sage-cli/main.go, docs/og-image.png, integrations/levelup/sage_bridge.py, internal/embedding/hash.go, internal/embedding/ollama.go, internal/embedding/provider.go, internal/mcp/tools_test.go, internal/tx/codec.go, internal/tx/codec_test.go
  The Provider Interface
    · `embedding.Provider` Interface
  Implementations
    · 1. Ollama (Local Semantic)
    · 2. Hash (Deterministic Pseudo-Embedding)
    · 3. Remote SAGE Endpoint
  Architecture: Natural Language to Vector Space
    · Embedding Data Flow
  Vector Search Integration
    · Search Flow: AccessQuery to Storage
  Configuration and Selection
    · Implementation Details

## · CLI Reference (sage-gui)  (L3838)
  源文件: .golangci.yml, api/rest/middleware/ratelimit.go, cmd/sage-gui/config.go, cmd/sage-gui/main.go, cmd/sage-gui/mcp.go, cmd/sage-gui/migrate.go, cmd/sage-gui/node.go, cmd/sage-gui/node_controller.go, cmd/sage-gui/quorum.go, cmd/sage-gui/seed.go, cmd/sage-gui/vault.go, cmd/sage-gui/wizard.go
  Command Overview
  Core Subcommands
    · serve
    · setup
    · mcp and mcp install
  Environment Variables
  Identity and Key Resolution
  Configuration Structure
  Maintenance and Migration

## · Configuration Reference  (L3981)
  源文件: cmd/sage-gui/config.go, cmd/sage-gui/config_test.go, cmd/sage-gui/mcp.go, docs/ARCHITECTURE.md, docs/GETTING_STARTED.md, sdk/python/README.md, sdk/python/src/sage_sdk/models.py
  Configuration Overview
    · Data Flow: Configuration Loading
  The `Config` Struct
    · Embedding Configuration (`EmbeddingConfig`)
    · Quorum Configuration (`QuorumConfig`)
    · Encryption Configuration (`EncryptionConfig`)
  Environment Variable Overrides
  Path Handling and Tilde Expansion
  Implementation Details
    · Key Functions
    · Configuration to Code Entity Mapping
    · Identity Resolution Logic

## · Claude Code Integration and Hooks  (L4147)
  源文件: .claude/hooks/sage-boot-check.sh, .claude/settings.json, cmd/sage-gui/config.go, cmd/sage-gui/mcp.go, cmd/sage-gui/mcp_test.go, extension/chrome/manifest.json, extension/manifest.firefox.json, extension/store-listing.md, web/handler_memorymode_test.go
  Hook Scripts: `sage-boot.sh` and `sage-turn.sh`
    · 1. `sage-boot.sh`
    · 2. `sage-turn.sh`
    · Memory Mode Adaptation
  Installation and Configuration Merging
    · `.claude/settings.json` Deep Merge
    · `sagePermissionsConfig` Tool Allowlist
    · `CLAUDE.md` Patching
  Self-Heal Mechanism
    · Logic Flow
    · Hook Update Data Flow
  Identity Resolution in MCP Mode
    · Project-Specific Key Generation

## · Deployment and Infrastructure  (L4308)
  源文件: .github/workflows/ci.yml, .github/workflows/release.yml, .goreleaser.yaml, api/rest/helpers.go, deploy/Dockerfile.abci, deploy/docker-compose.yml, go.mod, go.sum, installer/macos/build-dmg.sh, installer/windows/build-exe.sh, installer/windows/sage-installer.nsi, server.json
  Deployment Topologies
    · 1. Personal Mode (Single-Binary)
    · 2. Multi-Node Mode (Docker Cluster)
  Infrastructure Stack (Multi-Node)
    · Data and Embedding Layer
    · Consensus and State Layer
    · Deployment Orchestration to Code Mapping
  CI/CD and Release Pipeline
    · CI Workflow
    · Release Workflow
  Infrastructure Management
    · Redeployment Orchestrator
    · Infrastructure Component Interaction
  See Also

## · Multi-Node Docker Deployment  (L4460)
  源文件: .github/workflows/ci.yml, .github/workflows/release.yml, api/rest/helpers.go, deploy/Dockerfile.abci, deploy/docker-compose.yml, go.mod, go.sum, internal/metrics/health.go, internal/metrics/server.go, server.json
  Service Topology
    · Deployment Component Overview
    · Network and Data Flow
  Configuration and Environment
    · Key Environment Variables
    · Security Posture
  Initialization and Genesis
    · init-testnet.sh
    · Database Schema
  Monitoring Stack
    · Metrics Collection
  Build Pipeline

## · Platform Installers and Release Pipeline  (L4624)
  源文件: .github/workflows/ci.yml, .github/workflows/release.yml, .goreleaser.yaml, cmd/sage-launcher/main.go, cmd/sage-launcher/proc_other.go, cmd/sage-launcher/proc_windows.go, deploy/Dockerfile.abci, go.mod, go.sum, installer/linux/build-linux.sh, installer/linux/install.sh, installer/linux/sage.desktop
  Release Pipeline Architecture
    · Pipeline Flow Diagram
  Core Binaries and GoReleaser
  macOS DMG Pipeline
    · Implementation Details
  Windows NSIS Installer
    · Key Components
  Linux Desktop Integration
    · Desktop Entry Specification
  Docker and OCI Distribution
    · Docker Image Composition
    · server.json Synchronization
  The Sage Launcher
    · Functional Logic

## · Redeployment Orchestrator  (L4781)
  源文件: .golangci.yml, cmd/sage-gui/migrate.go, internal/orchestrator/backup.go, internal/orchestrator/redeployer.go, internal/orchestrator/redeployer_test.go, internal/store/sqlite_test.go, web/pairing.go, web/pairing_test.go, web/redeploy_middleware.go
  Overview and Purpose
    · Key Responsibilities
  The 9-Phase State Machine
    · Data Flow and Orchestration Logic
  Failure Handling and Rollback
    · API Protection during Redeployment
  Implementation Details
    · NodeController Interface
    · Validator Selection
  Upgrade Migration Logic

## · Browser Extension  (L4939)
  源文件: cmd/sage-gui/mcp_test.go, extension/build.sh, extension/chrome/README.md, extension/chrome/background.js, extension/chrome/content.css, extension/chrome/icons/generate-icons.html, extension/chrome/icons/generate-icons.js, extension/chrome/icons/icon128.png, extension/chrome/icons/icon16.png, extension/chrome/icons/icon48.png, extension/chrome/manifest.json, extension/chrome/popup.css
    · Architecture Overview
    · Core Components
    · Quick-Action Tools
    · UI and Connection Management
    · Build and Publish Pipeline

## · Testing  (L5096)
  源文件: .github/workflows/ci.yml, .github/workflows/release.yml, LICENSE, api/rest/handlers_test.go, cmd/amid/main.go, cmd/sage-cli/main.go, deploy/Dockerfile.abci, e2e/dashboard.spec.js, e2e/network.spec.js, go.mod, go.sum, internal/embedding/ollama.go
    · Testing Overview
    · Natural Language to Code Mapping: Testing Entities
    · Test Categories
    · Component Testing Architecture
    · Summary Table: Test Coverage

## · Unit and Integration Tests  (L5231)
  源文件: LICENSE, api/rest/handlers_test.go, cmd/amid/main.go, cmd/sage-cli/main.go, internal/appvalidator/manager_test.go, internal/appvalidator/validator_test.go, internal/embedding/ollama.go, internal/mcp/tools_test.go, internal/orchestrator/redeployer_test.go, internal/tx/codec.go, internal/tx/codec_test.go, internal/tx/types.go
  Go Unit Testing
    · Synaptic Ledger (Vault) Tests
    · Transaction Codec Tests
    · MCP Tool Tests
  REST API and Handler Testing
    · Mocking Strategy
    · Code Entity Mapping: REST Testing
  Integration Testing Suite
    · Dashboard and Ledger Integration
    · Authentication Integration
  Byzantine Fault and Quorum Tests
    · Consensus and Validator Quorum
    · Multi-Node Deployment Testing
  Python SDK Testing

## · E2E and Load Tests  (L5387)
  源文件: e2e/agent-identity.spec.js, e2e/bulk-operations.spec.js, e2e/dashboard.spec.js, e2e/network.spec.js, package.json, playwright.config.js
  Playwright E2E Suite
    · Test Configuration
    · Dashboard and Navigation
    · Network and Agent Management
    · Bulk Operations and Focus Mode
    · Agent Identity and On-chain Registration
  Load Testing and Benchmarking
    · Memory Submission Benchmarks
    · Query Throughput
  Summary of Test Suites

## · Integrations and Extensions  (L5534)
  源文件: .gitignore, Dockerfile, docs/og-image.png, integrations/levelup/sage_bridge.py, sage-memory/SKILL.md, scripts/setup_studio_org.py, sdk/python/examples/sage_bridge_example.py
  SageBridge: Python Middleware Pattern
    · Implementation and Data Flow
    · SageBridge Component Interaction
  Agent Skills: SKILL.md
    · Key Instructions for Agents
  Containerized Deployment (Dockerfile)
    · Docker Configuration
  Organization Provisioning (setup_studio_org.py)
    · Provisioning Workflow
    · Implementation Details

## · Glossary  (L5658)
  源文件: README.md, api/rest/agent_handler.go, internal/abci/app.go, internal/abci/app_test.go, internal/abci/migrate.go, internal/appvalidator/validator.go, internal/mcp/server.go, internal/mcp/tools.go, internal/memory/model.go, internal/store/badger.go, internal/store/postgres.go, internal/store/sqlite.go
  Core Domain Concepts
    · MemoryRecord
    · Domain
    · ConfidenceScore
    · Synaptic Ledger (Vault)
  Architectural Components
    · ABCI Application (`SageApp`)
    · App Validators
    · Proof of Experience (PoE)
  System Mappings
    · Natural Language to Code Entity Mapping
    · Identity and RBAC Mapping
  Technical Terms Reference