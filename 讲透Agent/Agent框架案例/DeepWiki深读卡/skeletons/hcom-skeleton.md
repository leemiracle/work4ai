# Skeleton: hcom（45 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 7KB | 2 | ~2 | 5 |
| 2 | Getting Started | L158 | 6KB | 2 | ~1 | 12 |
| 3 | Core Concepts | L350 | 9KB | 3 | ~5 | 10 |
| 4 | Architecture | L576 | 9KB | 3 | ~2 | 8 |
| 5 | CLI Entry Points and Command Routing | L850 | 8KB | 3 | ~4 | 5 |
| 6 | Database and Event Storage | L1029 | 10KB | 2 | ~7 | 12 |
| 7 | Instance Lifecycle Management | L1297 | 10KB | 3 | ~3 | 10 |
| 8 | Message Routing and Delivery | L1513 | 12KB | 2 | ~7 | 11 |
| 9 | Terminal Integration and PTY Wrapper | L1785 | 8KB | 2 | ~3 | 9 |
| 10 | Command Reference | L1972 | 7KB | 2 | ~9 | 7 |
| 11 | Launch and Instance Management | L2142 | 10KB | 4 | ~7 | 10 |
| 12 | Messaging Commands | L2394 | 9KB | 2 | ~6 | 9 |
| 13 | Events and Query Commands | L2625 | 11KB | 3 | ~3 | 8 |
| 14 | Configuration and Management Commands | L2882 | 10KB | 4 | ~9 | 8 |
| 15 | Terminal Commands | L3099 | 8KB | 2 | ~2 | 8 |
| 16 | Configuration System | L3268 | 15KB | 6 | ~9 | 2 |
| 17 | Configuration Files and Precedence | L3688 | 8KB | 3 | ~6 | 3 |
| 18 | Terminal Presets | L3902 | 10KB | 4 | ~5 | 5 |
| 19 | Settings Reference | L4168 | 10KB | 2 | ~13 | 4 |
| 20 | Tool Integration | L4487 | 8KB | 3 | ~2 | 8 |
| 21 | Hook System Overview | L4658 | 7KB | 3 | ~2 | 6 |
| 22 | Identity and Session Binding | L4860 | 8KB | 3 | ~4 | 11 |
| 23 | Claude Code Integration | L5054 | 7KB | 3 | ~3 | 6 |
| 24 | PTY Delivery Testing and Validation | L5243 | 8KB | 2 | ~2 | 6 |
| 25 | Multi-Agent Communication | L5426 | 7KB | 4 | ~1 | 8 |
| 26 | Message Scopes and Delivery Logic | L5605 | 10KB | 2 | ~7 | 8 |
| 27 | Event Subscriptions | L5810 | 8KB | 2 | ~2 | 8 |
| 28 | Bundles and Context Sharing | L6001 | 8KB | 2 | ~6 | 6 |
| 29 | Instance Forking and Subagents | L6173 | 7KB | 2 | ~4 | 5 |
| 30 | Cross-Device Synchronization | L6341 | 10KB | 2 | ~7 | 5 |
| 31 | Relay Architecture | L6537 | 11KB | 3 | ~3 | 10 |
| 32 | Relay Setup and Operations | L6775 | 9KB | 3 | ~5 | 6 |
| 33 | Build and Distribution | L7015 | 8KB | 2 | ~2 | 8 |
| 34 | Build System and CI/CD | L7183 | 8KB | 3 | ~2 | 10 |
| 35 | Installation Methods | L7356 | 8KB | 2 | ~1 | 8 |
| 36 | Database Schema Reference | L7550 | 14KB | 3 | ~23 | 15 |
| 37 | Development Guide | L7920 | 6KB | 3 | ~0 | 5 |
| 38 | Project Structure | L8086 | 8KB | 3 | ~5 | 7 |
| 39 | Adding New Commands | L8350 | 6KB | 3 | ~2 | 5 |
| 40 | Extending Terminal Support | L8524 | 8KB | 3 | ~2 | 5 |
| 41 | Testing and CI | L8737 | 8KB | 3 | ~4 | 12 |
| 42 | Agent Skills and Workflow Patterns | L8962 | 7KB | 2 | ~2 | 5 |
| 43 | Agent Messaging Skill | L9097 | 11KB | 3 | ~6 | 5 |
| 44 | Workflow Scripting and hcom run | L9314 | 11KB | 2 | ~2 | 10 |
| 45 | Glossary | L9488 | 9KB | 2 | ~3 | 16 |


## · Overview  (L6)
  源文件: Cargo.lock, Cargo.toml, README.md, pyproject.toml, src/commands/help.rs
  Purpose and Scope
  System Architecture
    · High-Level Entity Map
  Core Mechanisms
    · 1. Hook-Based Integration
    · 2. PTY Wrapping and Screen Capture
    · 3. SQLite Event Storage
  Data Flow: Message Delivery
  Key Components
  Multi-Agent Capabilities

## · Getting Started  (L158)
  源文件: .github/workflows/release.yml, Cargo.lock, Cargo.toml, README.md, dist-workspace.toml, install.sh, pyproject.toml, src/cli_context.rs, src/commands/list.rs, src/commands/update.rs, src/paths.rs, src/update.rs
  Installation
    · Method 1: Install Script (Recommended)
    · Method 2: Homebrew (macOS)
    · Method 3: pip / uv
    · Method 4: Build from Source
  Quick Start: Launching Agents
    · Basic Messaging Example
    · Messaging Data Flow (CLI to PTY)
  Tool Integration & Hooks
    · Hook Roles
    · Lifecycle of an Agent Launch
  Verification & Diagnostics

## · Core Concepts  (L350)
  源文件: src/commands/help.rs, src/db/instances.rs, src/db/mod.rs, src/db/notify.rs, src/instance_binding.rs, src/instance_lifecycle.rs, src/instance_names.rs, src/instances.rs, src/shared/constants.rs, src/shared/mod.rs
  The Database Hub
  Instances
    · Name Allocation
    · Instance Data Structure
    · Instance Lifecycle
  Sessions and Bindings
    · 1. session_bindings (Hook Participation)
    · 2. process_bindings (PTY Identity)
  Events and Messages
    · Event Types
    · Message Scopes and Intent
  Status States
  Identity Resolution

## · Architecture  (L576)
  源文件: Cargo.lock, Cargo.toml, README.md, pyproject.toml, src/commands/status.rs, src/hooks/mod.rs, src/main.rs, src/router.rs
  System Overview
  Entry Point and Routing
    · Action Resolution
  Database as Central Coordinator
    · Persistence and Environment
  Major Subsystems
    · Instance Lifecycle Management
    · Message Routing and Delivery
    · Terminal Integration and PTY Wrapper
  Tool Integration

## · CLI Entry Points and Command Routing  (L850)
  源文件: src/commands/mod.rs, src/commands/status.rs, src/hooks/mod.rs, src/main.rs, src/router.rs
  Application Initialization
  Action Resolution System
    · Resolution Logic
  Global Flag Extraction
  Command Dispatching
    · Native Command Dispatch
    · PTY Wrapper Entry
  Identity Resolution and Gating
  Help and Version Dispatch

## · Database and Event Storage  (L1029)
  源文件: src/db/events.rs, src/db/kv.rs, src/db/mod.rs, src/db/reqwatch_policy.rs, src/db/sessions.rs, src/db/subscriptions.rs, src/delivery/antigravity.rs, src/hooks/codex_file_edits.rs, src/identity.rs, src/instance_binding.rs, src/instance_names.rs, src/instances.rs
  Purpose and Scope
  Database Handle: HcomDb
  Schema Overview
  Schema Versioning and Archiving
    · Reconnection Logic
  Events Table: Append-Only Log
  Events View: events_v
  Event Types
    · Message Events (`type = 'message'`)
    · Status Events (`type = 'status'`)
    · Life Events (`type = 'life'`)
  Event Subscriptions
    · Subscription Logic
    · Special Subscription Types
  Notify Endpoints
  Session and Process Bindings
    · Session Bindings
    · Process Bindings
  Key-Value (KV) Store

## · Instance Lifecycle Management  (L1297)
  源文件: src/commands/kill.rs, src/core/launch_status.rs, src/db/instances.rs, src/db/mod.rs, src/db/notify.rs, src/instance_binding.rs, src/instance_lifecycle.rs, src/instance_names.rs, src/instances.rs, src/pidtrack.rs
  Instance States and Transitions
    · State Machine Diagram
    · State Definitions
  Creation and Name Generation
    · Name Generation System
    · Placeholder Reservation
  Registration and Binding
    · Binding Logic and Metadata Capture
    · Database Entity Mapping
  Heartbeat and Staleness
    · Heartbeat Logic
    · Thresholds
    · Wake Grace Period
    · Subagent Context
  Cleanup and Termination
    · Termination and Process Killing
    · Cleanup Tiers
    · Launch Failure Diagnostics

## · Message Routing and Delivery  (L1513)
  源文件: src/commands/events.rs, src/commands/listen.rs, src/commands/send.rs, src/commands/term.rs, src/db/reqwatch_policy.rs, src/db/subscriptions.rs, src/delivery.rs, src/delivery/antigravity.rs, src/messages.rs, src/pty/mod.rs, src/pty/screen.rs
  Message Flow Overview
  Scope Computation and Addressing
    · Scope Types
    · Target Resolution Logic
  Sender Identity Resolution
    · Identity Types
    · Resolution Logic
  Message Envelope and Bundles
    · Envelope Fields
    · Inline Bundles
  Delivery and Notification
    · The Notification Registry
    · Delivery Execution and Gating
    · Tool-Specific Injection Strategies
    · Request-Watch Subscriptions
  Screen Capture and Injection Mechanisms
    · Inject Port and RPC
    · Screen Tracking (vt100)
    · Injection Synchronization
  Summary Table: Routing Logic

## · Terminal Integration and PTY Wrapper  (L1785)
  源文件: src/core/tips.rs, src/delivery.rs, src/pty/inject.rs, src/pty/mod.rs, src/pty/screen.rs, src/pty/shared.rs, src/pty/win.rs, src/shared/terminal_presets.rs, src/terminal.rs
  Purpose and Scope
  Terminal Preset System
    · Preset Resolution and Detection
    · Terminal Command Templates
  PTY Wrapper Architecture
    · Component Interaction
    · Cross-Platform Implementation
  Screen Capture and VT100 Parsing
    · ScreenTracker Implementation
    · Escape Sequence Safety
  Injection and Delivery Mechanisms
    · The Delivery Loop
    · TCP Inject Server
  Status and Lifecycle Integration

## · Command Reference  (L1972)
  源文件: src/commands/help.rs, src/commands/mod.rs, Launch and Instance Management, Messaging Commands, Events and Query Commands, Configuration and Management Commands, Terminal Commands
  Command Structure and Invocation
    · Argument Syntax
  Identity and Context Resolution
    · Resolution Logic
    · Code Entity Mapping: Identity Resolution
  Common Flags and Filters
    · Shared Filter Flags
  Output Formats
  System Health and Workflow Execution
    · Tool Verification and Dispatch
  Command Reference Summary

## · Launch and Instance Management  (L2142)
  源文件: src/commands/fork.rs, src/commands/hooks.rs, src/commands/kill.rs, src/commands/launch.rs, src/commands/resume.rs, src/commands/start.rs, src/commands/stop.rs, src/core/launch_status.rs, src/pidtrack.rs, src/relay/control.rs
  Overview
  Launch Commands
    · Syntax
    · Tool Detection and Dispatch
    · Launch Execution Flow
    · Launch Flags
  Resume and Fork Commands
    · Usage
    · Resume Flow
    · Resume vs Fork
  Start Command
    · Start Variants
    · Subagent Detection
    · Task Blocking
  Stop and Kill Commands
    · Stop Command
    · Kill Command
  Lifecycle State Transitions
  Summary Matrix

## · Messaging Commands  (L2394)
  源文件: .github/workflows/release.yml, install.sh, src/cli_context.rs, src/commands/events.rs, src/commands/list.rs, src/commands/listen.rs, src/commands/send.rs, src/commands/term.rs, src/messages.rs
  Overview
  Send Command
    · Basic Syntax
    · Argument Parsing and Targeting
    · Sender Identity
    · Inline Bundles
    · Implementation and Data Flow
  List Command
    · Usage and Output Modes
    · Unread Message Tracking
    · Instance Lifecycle Cleanup
  Implementation Details

## · Events and Query Commands  (L2625)
  源文件: src/commands/events.rs, src/commands/listen.rs, src/commands/send.rs, src/commands/term.rs, src/db/reqwatch_policy.rs, src/db/subscriptions.rs, src/delivery/antigravity.rs, src/messages.rs
  Overview
  Event Types and Schema
    · Event Storage Architecture
    · Event Type Schemas
  Query Command (`hcom events`)
    · Basic Usage
    · Event Streamlining
    · Filter Flags
    · Query Flow Diagram
  Event Subscriptions (`hcom events sub`)
    · Subscription Mechanism
    · Creating Subscriptions
    · Request Watches and Policies
    · Management
  Listen Command
    · Listen Implementation
  Remote Event Queries and RPC
  Filter Logic and Shortcuts
    · Expanded Shortcuts
    · Filter Constraints
  Collision Detection

## · Configuration and Management Commands  (L2882)
  源文件: src/commands/bundle.rs, src/commands/config.rs, src/commands/relay.rs, src/config.rs, src/relay/mod.rs, src/relay/worker.rs, src/transcript/codex.rs, src/transcript/gemini.rs
  Configuration Management (`hcom config`)
    · Configuration Key Registry
    · Config Command Operations
    · Implementation Details
  Bundle Management (`hcom bundle`)
    · Bundle Structure and Storage
    · Bundle Commands Overview
  Tool Hook Management (`hcom hooks`)
    · Hook Operations
  Relay Management (`hcom relay`)
    · Relay Status and Identity
    · Relay Implementation Architecture
  System Reset and Updates
    · System Reset (`hcom reset`)
    · System Update (`hcom update`)

## · Terminal Commands  (L3099)
  源文件: src/commands/events.rs, src/commands/listen.rs, src/commands/send.rs, src/commands/term.rs, src/delivery.rs, src/messages.rs, src/pty/mod.rs, src/pty/screen.rs
  Purpose and Scope
  Command Overview
  Screen Inspection
    · Basic Usage
    · JSON Output and State
    · PTY Stream Safety
  Text Injection
    · Command Syntax
    · Injection Mechanism
  PTY Delivery Integration
  Debug Logging
    · Enable/Disable Logging
    · Implementation Details

## · Configuration System  (L3268)
  源文件: src/commands/config.rs, src/config.rs
  Two-Layer Architecture
    · Architecture Diagram
    · Config: Runtime Environment Layer
    · HcomConfig: User Settings Layer
  Configuration Precedence Chain
    · Precedence Flow Diagram
    · Load Sequence
    · Special Case: Relay Field Isolation
  Type System and Coercion
    · TomlFieldValue Enum
    · Coercion Rules by Field Type
  Validation System
    · Validation Architecture
    · Validation Rules by Field
    · Dangerous Character Filtering
  Persistence and Serialization
    · Serialization Targets
    · TOML Field Mapping
  Terminal Preset System
    · Preset Merging Logic
    · MergedPreset Structure
  Summary

## · Configuration Files and Precedence  (L3688)
  源文件: src/commands/config.rs, src/config.rs, src/shell_env.rs
  Configuration Architecture
    · Code Entity Space: Configuration Components
    · Config - Runtime Environment
    · HcomConfig - User Settings
  Configuration Files
    · config.toml
    · config.env (Legacy)
    · env File
    · shell_env.json (Cache)
  Precedence Order
    · Special Field Handling: Relay Security
  Field Mappings
    · Field Name to TOML Path
    · Field Name to Environment Variable
  Terminal Preset Merging

## · Terminal Presets  (L3902)
  源文件: src/commands/config.rs, src/config.rs, src/core/tips.rs, src/shared/terminal_presets.rs, src/terminal.rs
  Preset Anatomy
    · Command Template Placeholders
  Built-In Presets
    · Detection Logic
    · Platform-Specific Handling
  User-Defined TOML Presets
    · TOML Preset Format
    · Override Example
  Preset Resolution and Merging
    · Merging Logic
  Custom Command Templates
  Environment Detection for Same-Terminal Launches
  Close Command Execution
    · Close Flow
  Terminal Context Variable Stripping
  Kitty Remote Control Integration

## · Settings Reference  (L4168)
  源文件: src/commands/config.rs, src/config.rs, src/shared/constants.rs, src/shared/mod.rs
  Configuration Architecture Overview
  Settings by Category
    · Launch Settings
    · Tool-Specific Settings
    · Terminal Settings
    · Relay Settings
    · Preferences
  Detailed Settings Reference
    · tag
    · hints
    · subagent_timeout
    · auto_subscribe
    · terminal
    · relay_* Settings
  Internal Implementation Details

## · Tool Integration  (L4487)
  源文件: src/hooks/claude.rs, src/hooks/common.rs, src/hooks/opencode.rs, src/integration_spec.rs, src/launcher.rs, src/tool.rs, src/tui/model.rs, src/tui/rpc.rs
  Integration Overview
  Hook-Based Integration
    · Hook Architecture
    · Hook Safety and Gating
  PTY Wrapper Integration
    · PTY Wrapper Architecture
  Tool-Specific Capabilities
  Integration Flow: Message Delivery
  Next Steps

## · Hook System Overview  (L4658)
  源文件: src/commands/hooks.rs, src/commands/start.rs, src/hooks/claude.rs, src/hooks/common.rs, src/hooks/opencode.rs, src/hooks/utils.rs
  Purpose and Scope
  Hook Architecture Overview
    · Hook Dispatcher Architecture
  Hook Types and Payloads
    · Hook Registration by Tool
    · Common Hook Behaviors
  Hook Installation and Verification
    · Gate Check Mechanism
    · Hook Management CLI
  Message Delivery and Polling
    · Delivery Flow
    · Safe Commands
  Natural Language to Code Entity Space
    · Polling and Delivery Logic
    · Hook Life-cycle and Payload Processing

## · Identity and Session Binding  (L4860)
  源文件: src/db/events.rs, src/db/mod.rs, src/db/sessions.rs, src/hooks/claude.rs, src/hooks/codex_file_edits.rs, src/hooks/common.rs, src/hooks/opencode.rs, src/identity.rs, src/instance_binding.rs, src/instance_names.rs, src/instances.rs
  Purpose and Scope
  Three-Tier Identity System
    · Identity Relationship Diagram
  Database Schema and Identity Mapping
    · Key Entity Details
    · Merge and Switch Scenarios
  Binding Flow and Context Capture
    · Launch Context Capture
    · Late-Bound Metadata
  Identity Resolution in CLI
  Validation and Error Handling
  Key Functions Reference

## · Claude Code Integration  (L5054)
  源文件: .claude-plugin/marketplace.json, plugin/hcom/.claude-plugin/plugin.json, src/bootstrap.rs, src/hooks/claude.rs, src/hooks/common.rs, src/hooks/opencode.rs
  Purpose and Scope
  Integration Architecture
    · Claude Hook Dispatcher
  Hook Types and Lifecycle
    · Hook Execution Flow
  Session vs Process Binding
    · Session Binding (Tier 2)
    · Process Binding (Tier 3)
  Subagent Management
  PTY Delivery and Timing
  OpenCode Plugin Comparison

## · PTY Delivery Testing and Validation  (L5243)
  源文件: src/delivery.rs, src/pty/mod.rs, src/pty/screen.rs, tests/support/claude_mock.rs, tests/support/codex_mock.rs, tests/test_pty_delivery.rs
  Overview
    · Test Phases
  Screen State Detection
    · Ready Patterns and Prompt Markers
    · Screen JSON Schema
  Gate Blocking and Validation
    · Blocking Logic
    · OSC Title Detection
    · Output Safety and Title Injection
    · Data Flow Diagram: CLI to PTY
  PTY Bootstrap Injection
  Test Execution and Environment
    · Serial Execution Guard
    · Logging and Regressions
    · Execution Command
  Testing Entity Mapping

## · Multi-Agent Communication  (L5426)
  源文件: src/commands/events.rs, src/commands/listen.rs, src/commands/send.rs, src/commands/term.rs, src/db/reqwatch_policy.rs, src/db/subscriptions.rs, src/delivery/antigravity.rs, src/messages.rs
  Message Flow Architecture
    · Message Scope Resolution
    · Cursor-Based Delivery
  Event Subscriptions
    · Subscription Checking
  Context Transfer via Bundles
    · Bundle Creation Methods
  Instance Forking and Subagents
    · Lifecycle and Tracking

## · Message Scopes and Delivery Logic  (L5605)
  源文件: src/commands/events.rs, src/commands/listen.rs, src/commands/send.rs, src/commands/term.rs, src/delivery.rs, src/messages.rs, src/pty/mod.rs, src/pty/screen.rs
  Overview
  Message Scope Types
    · Broadcast Scope
    · Mentions Scope
  Scope Resolution Logic
    · Message Processing Flow
  Delivery Matching: `should_deliver_message`
    · Delivery Decision Logic
    · Key Behaviors
  Cross-Device Addressing and Device Suffixes
    · Device Suffix Handling
    · Cross-Device Matching Logic
  `delivered_to` Tracking
    · Database Schema and Views
  Mention Pattern Matching
    · Matching Rules
    · Underscore Blocking
  Tool-Specific Delivery Instructions
  Summary: Code Entity Map

## · Event Subscriptions  (L5810)
  源文件: src/commands/events.rs, src/commands/listen.rs, src/commands/send.rs, src/commands/term.rs, src/db/reqwatch_policy.rs, src/db/subscriptions.rs, src/delivery/antigravity.rs, src/messages.rs
  Architecture Overview
    · Subscription Processing Flow
  SQL Filters and events_v View
    · Available Columns in events_v
    · Composable Filter Flags
  Subscription Modes
    · Persistent vs. One-shot (--once)
    · Subscription on Behalf of Others (`--for`)
    · Subscription with Auto-Reply (`--on-hit`)
  Specialized Subscriptions
    · Collision Detection
    · Request-Watch Pattern
  Implementation Details
    · Event Streamlining
    · Thread Membership
    · Cancellation and Cleanup

## · Bundles and Context Sharing  (L6001)
  源文件: src/commands/bundle.rs, src/core/filters.rs, src/core/helpers.rs, src/hooks/family.rs, src/transcript/codex.rs, src/transcript/gemini.rs
  Purpose and Scope
  Bundle Structure and Data Model
    · Bundle Event Data Structure
  Bundle Types: Inline vs. Explicit
    · 1. Explicit Bundles
    · 2. Inline Bundles
  Bundle Lifecycle and Preparation
    · Preparation Workflow
    · Validation and Normalization
    · Detail Levels
  Technical Implementation
    · Database Interaction
    · Bundle Chaining (Lineage)
  Command Reference Summary

## · Instance Forking and Subagents  (L6173)
  源文件: src/commands/fork.rs, src/commands/resume.rs, src/hooks/claude.rs, src/hooks/common.rs, src/hooks/opencode.rs
  Overview
  Database Schema and Detection Logic
    · instances Table Fields for Relationships
    · Relationship Detection
  Task Tool Subagents
    · Subagent Architecture
    · Launch Context Inheritance
  Running Tasks Tracking
  Session Forking
    · Fork Command Logic
    · Fork Implementation Flow
  Remote Forking and RPC

## · Cross-Device Synchronization  (L6341)
  源文件: src/commands/launch.rs, src/commands/relay.rs, src/relay/control.rs, src/relay/mod.rs, src/relay/worker.rs
  Overview
  Architecture Overview
    · System Components and Code Entities
  Relay Groups and Device Identifiers
    · Relay Group Formation
    · Device Identification
  Event and Message Synchronization
    · MQTT Topic Structure
    · Security and Integrity
    · Sync Protocol
  Relay Daemon Lifecycle
    · Daemon Management
  Configuration and Security
    · Security Model

## · Relay Architecture  (L6537)
  源文件: src/commands/relay.rs, src/relay/broker.rs, src/relay/client.rs, src/relay/crypto.rs, src/relay/mod.rs, src/relay/pull.rs, src/relay/push.rs, src/relay/replay.rs, src/relay/token.rs, src/relay/worker.rs
  Purpose and Scope
  MQTT Topic Layout
    · Topic Structure and Data Flow
  State Snapshot Format
    · State Generation Logic
  Security: Encryption and Replay Protection
    · Encryption Envelope
    · Replay Guard
  Event Synchronization Protocol
    · Push Sequence
    · Pull and Merge Logic
  Remote RPC (Control Topic)
  Relay Daemon (relay-worker)
    · Daemon Architecture
  Relay Health Monitoring

## · Relay Setup and Operations  (L6775)
  源文件: src/commands/launch.rs, src/commands/relay.rs, src/relay/control.rs, src/relay/mod.rs, src/relay/worker.rs, tests/test_relay_roundtrip.rs
  Relay Lifecycle Commands
    · Initializing a Relay Group
    · Joining an Existing Group
    · Disabling and Stopping
  Relay Daemon Operations
    · Daemon Management
    · Remote RPC and Control
  Data Flow: Inbound Message Handling
  Device Identifiers and Addressing
    · Device Identity
    · Remote Instance Addressing
  Status and Troubleshooting
    · Checking Status
    · Common Troubleshooting Steps

## · Build and Distribution  (L7015)
  源文件: .github/build-setup.yml, .github/workflows/build-wheels.yml, .github/workflows/publish-pypi.yml, .github/workflows/release.yml, install.sh, src/cli_context.rs, src/commands/list.rs, src/core/bundles.rs
  Build System Overview
  Platform Target Matrix
    · Target Platforms
    · Android Special Handling
  CI/CD Workflows
    · Release Pipeline
  Update and Installation Logic
    · Distribution Channels
  Child Pages

## · Build System and CI/CD  (L7183)
  源文件: .github/build-setup.yml, .github/workflows/build-wheels.yml, .github/workflows/ci.yml, .github/workflows/publish-pypi.yml, .github/workflows/release.yml, Justfile, install.sh, src/cli_context.rs, src/commands/list.rs, src/core/bundles.rs
  Overview
  Maturin and Wheel Configuration
  GitHub Actions CI/CD Workflows
    · Continuous Integration (`ci.yml`)
    · Real-Tool Integration Testing
  Wheel Build and PyPI Distribution
    · Data Flow: Compilation to PyPI
    · Android/Termux Specialized Build
  Android NDK Setup
    · Toolchain Mapping
    · Implementation Detail

## · Installation Methods  (L7356)
  源文件: .github/workflows/release.yml, dist-workspace.toml, install.sh, src/cli_context.rs, src/commands/list.rs, src/commands/update.rs, src/paths.rs, src/update.rs
  Purpose and Scope
  Installation Method Overview
  Installation Flow Diagram
  Update Command Detection
  Curl Installer Script (`install.sh`)
    · Shim Implementation
  Distribution Model and CI/CD
    · Release Process
    · Target Matrix
  Platform Specifics
    · Android (Termux)
    · Windows
  Build Configuration Entity Mapping

## · Database Schema Reference  (L7550)
  源文件: src/db/events.rs, src/db/instances.rs, src/db/kv.rs, src/db/mod.rs, src/db/notify.rs, src/db/reqwatch_policy.rs, src/db/sessions.rs, src/db/subscriptions.rs, src/delivery/antigravity.rs, src/hooks/codex_file_edits.rs, src/identity.rs, src/instance_binding.rs
  Schema Version Management
  Database Configuration
  Core Tables
    · `instances` Table
    · `events` Table
    · `session_bindings` Table
    · `process_bindings` Table
    · `notify_endpoints` Table
    · `kv` Table
  Entity Relationship Diagram
  Views and Virtual Tables
    · `events_v` View
  Database Access Patterns
    · Message Delivery Flow
    · Identity Binding Sequence

## · Development Guide  (L7920)
  源文件: Cargo.lock, Cargo.toml, README.md, pyproject.toml, src/main.rs
  Project Structure
    · Directory Layout
  Adding New Commands
    · Command Implementation Pattern
  Extending Terminal Support
    · Preset Responsibilities
  Testing and CI
    · PTY Integration Tests
  Build System (Maturin)

## · Project Structure  (L8086)
  源文件: Cargo.lock, Cargo.toml, README.md, pyproject.toml, src/shared/constants.rs, src/shared/mod.rs, src/shared/platform.rs
  Hybrid Rust/Python Architecture
  Package Configuration
    · pyproject.toml
    · Cargo.toml
  Directory Structure and Module Organization
    · Platform and Path Utilities
    · Shared Constants and Identity
    · Build Profiles and Optimization
    · Version Synchronization

## · Adding New Commands  (L8350)
  源文件: src/commands/mod.rs, src/commands/status.rs, src/hooks/mod.rs, src/main.rs, src/router.rs
  Command Routing Architecture
    · Dispatch Logic Flow
    · Action Resolution
  Implementing a New Command
    · 1. Define the Command Module
    · 2. Implement Clap Parsing
    · 3. Register in the Router
  Data Flow: From CLI to Logic
  Command Context and Previews
  Global Flags vs. Local Flags

## · Extending Terminal Support  (L8524)
  源文件: src/commands/config.rs, src/config.rs, src/core/tips.rs, src/shared/terminal_presets.rs, src/terminal.rs
  Terminal Integration Architecture
    · Data Flow: Launching a Terminal
  Implementing Terminal Presets
    · The TerminalPreset Structure
    · Adding a New Preset
  Command Templates and Placeholders
    · Open Command Placeholders
    · Close Command Placeholders
  Pane ID Extraction and Detection
    · Environment Detection Logic
    · Terminal Context Stripping
  Binary and App Path Resolution
    · macOS App Fallbacks
  User-Defined Custom Presets
    · Managed vs Unmanaged Closing
  Troubleshooting and Debugging
    · Terminal Debug Mode
    · Log Inspection

## · Testing and CI  (L8737)
  源文件: .github/workflows/ci.yml, Justfile, scripts/install-mock-tools.sh, tests/cli_smoke.rs, tests/real_tool_claude.rs, tests/real_tool_codex.rs, tests/support/claude_mock.rs, tests/support/codex_mock.rs, tests/support/mock_http.rs, tests/support/mod.rs, tests/support/real_tool.rs, tests/test_pty_delivery.rs
  Purpose and Scope
  CI Pipeline
    · Workflow Configuration
    · Environment and Tooling
  PTY Delivery Integration Tests
    · Test Architecture
    · Tool-Specific Markers
  Real-Tool Lifecycle Runner
    · Mock Infrastructure
    · The Lifecycle Contract
  Hermetic CLI Smoke Tests
  Local Testing Guide

## · Agent Skills and Workflow Patterns  (L8962)
  源文件: skills/hcom-agent-messaging/SKILL.md, skills/hcom-agent-messaging/references/cross-tool.md, skills/hcom-agent-messaging/references/gotchas.md, skills/hcom-agent-messaging/references/patterns.md, skills/hcom-agent-messaging/references/script-template.md
  Overview of Agent Capabilities
    · Bridging Natural Language to Code Entities
  Agent Messaging Skill
    · Key Messaging Concepts
  Workflow Scripting and hcom run
    · Workflow Topologies
    · Scripting Requirements
    · Script Templates and Reference
  Technical Integration Flow
    · Timing and Tool-Specific Behavior

## · Agent Messaging Skill  (L9097)
  源文件: skills/hcom-agent-messaging/SKILL.md, skills/hcom-agent-messaging/references/cross-tool.md, skills/hcom-agent-messaging/references/gotchas.md, skills/hcom-agent-messaging/references/patterns.md, skills/hcom-agent-messaging/references/script-template.md
    · Purpose and Scope
  1. Skill Entry Point: SKILL.md
  2. CLI Reference for Agents
    · Launching and Lifecycle
    · Communication
    · Observation and Synchronization
  3. Cross-Tool Collaboration Guide
    · Tool Comparison Matrix
  4. Multi-Agent Communication Patterns
    · Pattern: Worker-Reviewer Feedback Loop
    · Pattern: Ensemble Consensus
    · Pattern: Sequential Cascade Pipeline
  5. Workflow Scripting
    · Scripting Key Rules
    · Topologies
  6. Common Gotchas and Troubleshooting
    · The "Script Hang"
    · Message Delivery Failures
    · Workflow Isolation
    · SQL Matching

## · Workflow Scripting and hcom run  (L9314)
  源文件: skills/hcom-agent-messaging/references/scripts/basic-messaging.sh, skills/hcom-agent-messaging/references/scripts/cascade-pipeline.sh, skills/hcom-agent-messaging/references/scripts/codex-worker.sh, skills/hcom-agent-messaging/references/scripts/cross-tool-duo.sh, skills/hcom-agent-messaging/references/scripts/ensemble-consensus.sh, skills/hcom-agent-messaging/references/scripts/review-loop.sh, src/commands/run.rs, src/scripts/bundled/confess.sh, src/scripts/bundled/debate.sh, src/scripts/bundled/fatcow.sh
  The hcom run Command
    · Script Discovery and Shadowing
    · Metadata Extraction
    · Interpreter Resolution
  Script Template and Lifecycle
    · Core Lifecycle Components
    · Technical Conventions
  Agent Topologies
    · 1. Worker-Reviewer (Sequential)
    · 2. Ensemble Consensus (Parallel)
    · 3. Pipeline (Cascade)
    · 4. Hub-Spoke (Reactive / Fatcow)
    · 5. Debate (Adversarial)
    · 6. Reactive (Confess)
  Cross-Tool Scripting Guide
    · Tool Selection
    · Identity Handling
  Debugging Reference

## · Glossary  (L9488)
  源文件: Cargo.lock, Cargo.toml, README.md, pyproject.toml, src/commands/help.rs, src/commands/launch.rs, src/core/tips.rs, src/delivery.rs, src/hooks/claude.rs, src/hooks/common.rs, src/hooks/opencode.rs, src/pty/mod.rs
  Core System Entities
    · Instance
    · Session
    · Event
    · Message
    · Bundle
  Technical Jargon & Implementation Terms
    · PTY Wrapper
    · Gate / Gating
    · Hook
    · Relay
  Architecture Diagrams
    · From Natural Language Space to Code Entity Space
    · PTY Delivery and Screen State Logic
  Terminology Reference Table