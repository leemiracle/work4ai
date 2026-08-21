# Skeleton: greywall（36 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 8KB | 3 | ~4 | 7 |
| 2 | Getting Started | L217 | 6KB | 1 | ~1 | 8 |
| 3 | Installation | L432 | 8KB | 3 | ~3 | 10 |
| 4 | Quick Start Guide | L677 | 12KB | 3 | ~6 | 4 |
| 5 | CLI Reference | L1079 | 11KB | 3 | ~15 | 4 |
| 6 | Core Concepts | L1411 | 9KB | 2 | ~4 | 5 |
| 7 | Network Isolation | L1626 | 15KB | 5 | ~5 | 5 |
| 8 | Filesystem Isolation | L2047 | 9KB | 2 | ~2 | 8 |
| 9 | Security Model | L2243 | 7KB | 2 | ~2 | 5 |
| 10 | Platform Implementations | L2410 | 8KB | 2 | ~3 | 4 |
| 11 | Linux Sandboxing | L2577 | 12KB | 4 | ~1 | 3 |
| 12 | bubblewrap and Namespaces | L2944 | 18KB | 9 | ~9 | 3 |
| 13 | Landlock Filesystem Control | L3421 | 11KB | 3 | ~9 | 6 |
| 14 | Seccomp Syscall Filtering | L3674 | 14KB | 6 | ~18 | 6 |
| 15 | eBPF Violation Monitoring | L4047 | 11KB | 4 | ~9 | 4 |
| 16 | Transparent Network Proxying | L4351 | 8KB | 3 | ~4 | 4 |
| 17 | macOS Sandboxing | L4540 | 6KB | 2 | ~0 | 5 |
| 18 | Seatbelt Profile Generation | L4683 | 15KB | 3 | ~2 | 3 |
| 19 | Unified Log Monitoring | L5009 | 9KB | 2 | ~9 | 5 |
| 20 | Network Architecture | L5280 | 12KB | 5 | ~4 | 6 |
| 21 | greyproxy Service | L5566 | 7KB | 2 | ~2 | 8 |
| 22 | Proxy Bridges and Unix Sockets | L5730 | 13KB | 8 | ~5 | 2 |
| 23 | Domain-Based Filtering | L6086 | 8KB | 3 | ~2 | 3 |
| 24 | Configuration System | L6326 | 12KB | 4 | ~9 | 3 |
| 25 | Configuration Files | L6705 | 9KB | 2 | ~4 | 3 |
| 26 | Profile System | L6927 | 8KB | 3 | ~1 | 10 |
| 27 | Learning Mode | L7142 | 11KB | 3 | ~10 | 8 |
| 28 | Go Library API | L7453 | 10KB | 3 | ~4 | 5 |
| 29 | Development Guide | L7812 | 6KB | 2 | ~12 | 7 |
| 30 | Building from Source | L8023 | 5KB | 2 | ~0 | 6 |
| 31 | CI/CD Pipeline | L8191 | 10KB | 4 | ~5 | 4 |
| 32 | Release Process | L8464 | 5KB | 1 | ~1 | 7 |
| 33 | Reference | L8593 | 7KB | 4 | ~9 | 3 |
| 34 | Security Policy | L8803 | 6KB | 2 | ~2 | 2 |
| 35 | License | L8974 | 8KB | 2 | ~11 | 2 |
| 36 | Glossary | L9228 | 8KB | 3 | ~2 | 22 |


## · Overview  (L6)
  源文件: ARCHITECTURE.md, CONTRIBUTING.md, README.md, docs/index.md, docs/platform-support.md, docs/why-greywall.md, install.sh
  Purpose and Scope
  What is Greywall
  Security Model
    · The Two-Layer Isolation Model
    · Deny-by-Default Principles
  Architecture Overview
    · Core Components
  Platform Implementations
    · Linux Implementation
    · macOS Implementation
    · Feature Comparison
  Data Flow: Command Execution

## · Getting Started  (L217)
  源文件: README.md, docs/quickstart.md, install.sh, internal/proxy/detect.go, internal/proxy/install.go, internal/proxy/start.go, internal/sandbox/color.go, internal/sandbox/linux_features_stub.go
  Prerequisites and Dependencies
  Installation Overview
    · Installation Flow
    · Quick Install Commands
  Verifying Installation
    · System Check
    · greyproxy Service
  Your First Sandboxed Command
    · Deny-by-Default Model
    · Basic Usage Examples
  Working with Profiles
    · Built-in Agent Profiles
    · Learning Mode
  Configuration
  Next Steps

## · Installation  (L432)
  源文件: .github/workflows/release.yml, .goreleaser.yaml, README.md, install.sh, internal/proxy/brew.go, internal/proxy/detect.go, internal/proxy/install.go, internal/proxy/start.go, internal/sandbox/color.go, internal/sandbox/linux_features_stub.go
  Installation Methods Overview
  Platform Requirements
    · Linux Requirements
    · macOS Requirements
  Homebrew Installation (macOS)
  install.sh Script Installation
    · Script Workflow
    · Script Behavior
  Alternative Installation Methods
    · Go Install
    · Build from Source
  greyproxy Setup
    · Setup Workflow
    · Key Implementation Details
  Verification
    · Dependency Status Logic
    · Colorized Output

## · Quick Start Guide  (L677)
  源文件: README.md, cmd/greywall/main.go, docs/quickstart.md, install.sh
  Prerequisites and Verification
  Your First Sandboxed Command
    · Default Behavior: Network Blocked
    · Using Shell Expansion
    · Enabling Debug Output
  Basic Usage Patterns
    · Port Exposure for Development Servers
    · Monitoring Sandbox Violations
    · Custom Configuration Files
  Working with Profiles
    · Auto-Detection and First-Run Experience
    · Explicit Profile Loading
    · Listing and Inspecting Profiles
  Learning Mode Workflow
    · Step 1: Run in Learning Mode
    · Step 2: Profile Generation
    · Step 3: Auto-Loading on Next Run
  Common Use Cases
    · Running AI Coding Agents
    · Development Server with Port Exposure
    · Custom Network Routing
    · Command Deny Rules
  Quick Reference
    · Essential Commands
    · Common Flags

## · CLI Reference  (L1079)
  源文件: cmd/greywall/main.go, docs/agents.md, docs/cli-reference.md, docs/templates.md
  Command Overview
  Root Command: `greywall`
    · Syntax
    · Global Flags
    · Command Specification Methods
  Command Execution Flow
  Subcommands
    · `greywall check`
    · `greywall setup`
    · `greywall profiles`
  Flag Processing and Configuration Merging
  Environment Variables
  Exit Codes
  Command-to-Code Entity Mapping

## · Core Concepts  (L1411)
  源文件: docs/benchmarking.md, docs/concepts.md, docs/library.md, docs/security-model.md, internal/sandbox/manager.go
  Deny-by-Default Security Model
  Two-Layer Isolation Architecture
    · Architecture Diagram: Natural Language to Code Entities
  Sandbox Lifecycle
    · Lifecycle Phases Diagram
    · Phase 1: Manager Initialization
    · Phase 2: Command Wrapping
    · Phase 3: Execution and Monitoring
    · Phase 4: Cleanup
  Configuration System
    · Configuration Components
  Summary

## · Network Isolation  (L1626)
  源文件: internal/config/config.go, internal/sandbox/integration_macos_test.go, internal/sandbox/linux.go, internal/sandbox/macos.go, internal/sandbox/macos_test.go
  Purpose and Scope
  Two-Layer Isolation Model
  Platform-Specific Implementations
  Linux: Transparent Proxying Architecture
    · Network Namespace Isolation
    · TUN Device and tun2socks
    · Unix Socket Bridges
    · DNS Resolution
  macOS: Seatbelt Profile Network Rules
    · Profile Generation
    · Proxy Environment Variables
  greyproxy Service
  Domain-Based Filtering
    · Configuration
    · Wildcard Matching
  Localhost Controls
    · AllowLocalBinding
    · AllowLocalOutbound
    · Exposed Ports (ForwardPorts)
  Network Isolation Flow Comparison
    · Linux Transparent Proxy Flow
    · macOS Environment Variable Flow

## · Filesystem Isolation  (L2047)
  源文件: internal/config/config.go, internal/sandbox/dangerous.go, internal/sandbox/integration_linux_test.go, internal/sandbox/integration_macos_test.go, internal/sandbox/integration_test.go, internal/sandbox/linux_landlock.go, internal/sandbox/macos.go, internal/sandbox/macos_test.go
  Deny-by-Default Security Model
  Platform-Specific Implementations
    · Linux: bubblewrap + Landlock
    · macOS: Seatbelt Profiles
  Path Rule Processing
  Default Readable and Writable Paths
  Sensitive File Protection
  macOS-Specific Symlink Handling

## · Security Model  (L2243)
  源文件: docs/credential-protection.md, docs/security-model.md, internal/sandbox/credentials.go, internal/sandbox/credentials_test.go, internal/sandbox/sanitize.go
  Defense-in-Depth Architecture
    · System Components and Enforcement Points
  Threat Model
    · Protected Threats
    · Non-Protected Threats
  Security Mechanisms
    · 1. Network Isolation (Default Deny)
    · 2. Filesystem Isolation
    · 3. Credential Protection
    · 4. Environment Sanitization
    · 5. D-Bus and Socket Isolation (Linux)
  Implementation Flow
  Visibility and Auditing

## · Platform Implementations  (L2410)
  源文件: docs/platform-support.md, internal/platform/platform.go, internal/sandbox/manager_darwin.go, internal/sandbox/manager_linux.go
  Platform Architecture Differences
    · High-Level Comparison
    · Platform Comparison Table
  Command Wrapping Flow
  Code Entity Mapping
  Filesystem Isolation
    · Linux: Mount Namespaces + Landlock
    · macOS: Seatbelt Profiles
  Network Isolation
    · Linux: Transparent Proxying
    · macOS: Environment Variables
  Next Steps

## · Linux Sandboxing  (L2577)
  源文件: docs/linux-security-features.md, internal/sandbox/linux.go, internal/sandbox/linux_features.go
  Multi-Layer Security Architecture
  Command Wrapping Flow
  Core Data Structures
    · LinuxSandboxOptions
    · Bridge Components
  Feature Detection System
    · Detection Methods
  Filesystem Isolation Models
    · Deny-by-Default Mode
    · Legacy Mode
  Deny-by-Default Mount Construction
  Network Isolation Architecture
  Security Layer Details
    · Seccomp Syscall Filter
    · eBPF Monitoring
    · Landlock Integration
  Learning Mode
  Error Handling and Fallback

## · bubblewrap and Namespaces  (L2944)
  源文件: internal/sandbox/linux.go, internal/sandbox/linux_features.go, internal/sandbox/linux_stub.go
  Purpose and Scope
  Overview of bubblewrap
  Namespace Isolation
    · Namespace Types and Isolation Boundaries
    · PID Namespace
    · Network Namespace
    · Mount Namespace
  Mount Structure Implementation
    · Intermediary Directory Creation
    · Sensitive File Masking
    · Special Filesystem Mounts
    · Resolv.conf Symlink Resolution
  Command Construction Process
    · Argument Building Flow
    · Inner Script Structure
    · Final Command Assembly
  Feature Detection and Fallbacks
    · Capability Matrix
    · Graceful Degradation
    · Ubuntu 24.04 AppArmor Issue

## · Landlock Filesystem Control  (L3421)
  源文件: internal/sandbox/command.go, internal/sandbox/command_test.go, internal/sandbox/integration_linux_test.go, internal/sandbox/integration_test.go, internal/sandbox/linux_landlock.go, internal/sandbox/linux_landlock_stub.go
  Purpose and Scope
  Landlock in the Linux Sandbox Stack
  LandlockRuleset Type and Lifecycle
    · Key Fields and Methods
  ABI Version Support and Access Rights
    · Access Rights Mapping
  Path Rule Semantics and PATH_BENEATH
    · Path Resolution Process
  Configuration to Rules Translation
    · Default System Paths
    · Special Path Handling
    · Deny-by-Default Mode
  Glob Pattern Expansion
  Graceful Fallback Behavior
  Testing and Verification

## · Seccomp Syscall Filtering  (L3674)
  源文件: internal/sandbox/linux_ebpf.go, internal/sandbox/linux_ebpf_stub.go, internal/sandbox/linux_seccomp.go, internal/sandbox/linux_seccomp_stub.go, internal/sandbox/monitor.go, internal/sandbox/shell.go
  Purpose and Scope
  Architecture Overview
    · Seccomp Integration Flow
  SeccompFilter Class
  Blocked Syscalls
    · Syscall Categories
    · Complete Blocked Syscalls List
  TIOCSTI Terminal Injection Protection
    · Why TIOCSTI is Dangerous
    · Implementation Details
  BPF Program Generation
    · BPF Instruction Structure
    · Program Structure
    · BPF Instruction Constants
  Architecture-Specific Syscall Numbers
    · Architecture Detection and Mapping
    · Example Syscall Number Differences
  Monitoring and Logging Limitations
    · Detection via eBPF
  Cleanup and Lifecycle

## · eBPF Violation Monitoring  (L4047)
  源文件: internal/sandbox/linux.go, internal/sandbox/linux_ebpf.go, internal/sandbox/linux_seccomp.go, internal/sandbox/monitor.go
  Purpose and Scope
  Why eBPF Monitoring is Needed
  Architecture Overview
  Feature Detection and Requirements
    · Capability Requirements
    · Detection Flow
  EBPFMonitor Implementation
    · Struct Definition and Lifecycle
    · Bpftrace Integration
  Bpftrace Script Generation
    · Script Structure
    · Error Code Filtering
    · PID Filtering Strategy
  Monitored Syscalls and Operations
    · Filesystem Operations
    · Network Operations
  Event Parsing and Output
    · Parsing Flow
    · Output Format
  Comparison with macOS Log Monitoring

## · Transparent Network Proxying  (L4351)
  源文件: internal/sandbox/benchmark_test.go, internal/sandbox/linux.go, internal/sandbox/resolv_linux_test.go, internal/sandbox/tun2socks_embed.go
  Purpose and Scope
  Architecture Overview
    · System to Code Entity Mapping
  TUN Device Configuration
  tun2socks Integration
    · Binary Extraction
    · Execution in Sandbox
  Bridge Implementation
    · ProxyBridge
    · DnsBridge
  DNS Resolution Strategies
  Lifecycle and Cleanup

## · macOS Sandboxing  (L4540)
  源文件: internal/sandbox/integration_macos_test.go, internal/sandbox/macos.go, internal/sandbox/macos_test.go, internal/sandbox/manager_darwin.go, internal/sandbox/manager_linux.go
  Architecture Overview
    · Command Execution Flow
    · System Entity Mapping
  Core Components
    · MacOSSandboxParams
    · Profile Generation Logic
  Network Isolation Strategy
  Filesystem Access Control
    · Security Nuance: Operation Specificity
  Violation Monitoring
  Learning Mode

## · Seatbelt Profile Generation  (L4683)
  源文件: internal/sandbox/integration_macos_test.go, internal/sandbox/macos.go, internal/sandbox/macos_test.go
  Overview
  Profile Generation Pipeline
  Seatbelt Profile Structure
  Log Tag Embedding
  Essential Permissions
    · Process Permissions
    · Mach IPC Services
    · sysctl Access
    · Device I/O
  Network Rule Generation
    · Network Restriction Mode
  Filesystem Read Rule Generation
    · Default Deny Read Mode
    · Deny Rules Must Use Exact Operations
  Filesystem Write Rule Generation
  Path Handling and Normalization
    · Glob to Regex Conversion
    · Path Escaping
    · macOS /tmp Symlink Handling
  Move Blocking Rules
  Profile Composition
  Testing

## · Unified Log Monitoring  (L5009)
  源文件: internal/sandbox/integration_macos_test.go, internal/sandbox/learning_darwin.go, internal/sandbox/learning_darwin_test.go, internal/sandbox/macos.go, internal/sandbox/macos_test.go
  Monitoring Architecture
  Session Suffix Generation
    · Generation Process
    · Profile Integration
  LogMonitor Implementation
    · Structure Definition
    · Start Method
  Violation Parsing and Filtering
    · Parsing Pattern
    · Operation Type Filtering
    · Noise Filtering
  Comparison with Learning Mode (eslogger)

## · Network Architecture  (L5280)
  源文件: internal/proxy/detect.go, internal/proxy/install.go, internal/proxy/start.go, internal/sandbox/color.go, internal/sandbox/linux.go, internal/sandbox/linux_features_stub.go
  Overview
  Two-Layer Network Isolation
  Platform-Specific Implementations
    · Linux: Transparent Network Proxying
    · macOS: Environment Variable Proxy Configuration
  Network Traffic Flow
  Component Architecture
    · ProxyBridge (Linux)
    · DnsBridge (Linux)
    · greyproxy Service Integration
  Network Configuration
    · Default Ports and URLs
    · Proxy URL Configuration

## · greyproxy Service  (L5566)
  源文件: .github/workflows/release.yml, .goreleaser.yaml, internal/proxy/brew.go, internal/proxy/detect.go, internal/proxy/install.go, internal/proxy/start.go, internal/sandbox/color.go, internal/sandbox/linux_features_stub.go
  Overview
  Service Architecture
  Installation and Management
    · Automatic Installation via Homebrew
    · Manual Installation Logic
  Service Detection and Health
    · Detection Logic
    · Health Check Protocol
  Version Management
  Platform Specifics
    · Homebrew Management
    · Linux vs macOS Capabilities
  Starting the Service

## · Proxy Bridges and Unix Sockets  (L5730)
  源文件: internal/sandbox/linux.go, internal/sandbox/manager.go
  Bridge Architecture Overview
    · Complete Bridge Architecture
  ProxyBridge (Outbound Traffic)
    · ProxyBridge Structure
    · ProxyBridge Creation Flow
    · ProxyBridge socat Command
    · Credentials Handling
  DnsBridge (DNS Resolution)
    · DnsBridge Structure
    · DnsBridge Creation and socat Command
    · DNS Resolution Flow
  ReverseBridge (Inbound Connections)
    · ReverseBridge Architecture
    · ReverseBridge socat Commands
  Socket Lifecycle and Management
    · Socket Path Generation
    · Cleanup Implementation
  Integration with Sandbox
    · Bridge Initialization Sequence
    · Socket Bind Mounts
    · Inner Script Bridge Setup

## · Domain-Based Filtering  (L6086)
  源文件: docs/configuration.md, internal/config/config.go, internal/config/config_test.go
  Overview
  Configuration Model
    · Code Entity Mapping: Network Configuration
    · Configuration Examples
  Domain Matching Logic
    · Filtering Decision Flow
    · Pattern Support
  DNS Filtering
  Integration with Sandbox Configuration
    · Configuration Precedence
  Platform-Specific Enforcement
    · Linux: Transparent Interception
    · macOS: Environment Variables
  Localhost and Local Binding

## · Configuration System  (L6326)
  源文件: docs/configuration.md, internal/config/config.go, internal/config/config_test.go
  Configuration Loading Flow
  Configuration Loading Implementation
    · Stage 1: Base Configuration
    · Stage 2: Profile Resolution
    · Stage 3: CLI Flag Overrides
    · Stage 4: Default Value Application
    · Stage 5: Proxy Credential Injection
  Configuration Structure
    · Core Configuration Type
    · Field Semantics
  Profile Resolution System
    · Resolution Implementation
  Configuration Merging
    · Merge Semantics by Field Type
    · Multiple Profile Merging
  Auto-Detection and First-Run UX
    · Command Name Extraction
    · Auto-Profile Mode
  Default Values and Initialization
    · Nil vs. Empty Semantics
    · Default Denied Commands
  Configuration Precedence Summary

## · Configuration Files  (L6705)
  源文件: docs/configuration.md, internal/config/config.go, internal/config/config_test.go
  File Format and Locations
  Configuration Loading Flow
  Configuration Structure
    · Extends Field
  Network Configuration
    · Field Reference
    · Network Rules
  Filesystem Configuration
    · Deny-by-Default Read Model
    · Hard-Coded Protections
  Command Configuration
    · Default Denied Commands
    · Command Detection
  SSH Configuration
  Credential Configuration
  Merging and Defaults

## · Profile System  (L6927)
  源文件: docs/agents.md, docs/cli-reference.md, docs/templates.md, internal/profiles/base.go, internal/profiles/keyring.go, internal/profiles/profiles_test.go, internal/profiles/prompt.go, internal/profiles/registry.go, internal/profiles/resolve.go, internal/profiles/toolchains/scm.go
  Profile Types
  Profile Resolution and Precedence
  Built-in Profiles and Inheritance
    · Base Profile
    · Toolchains vs. Agents
    · Keyring Secrets (Linux)
  Profile Management and First-Run UX
    · First-Run Prompt
    · Ad-Hoc Commands
  Profile Inheritance (extends)
    · Merging Rules
    · Example: Customizing a Template
  Network Rules Precedence
    · `--no-network-rules`

## · Learning Mode  (L7142)
  源文件: docs/learning-mode.md, internal/sandbox/learning.go, internal/sandbox/learning_darwin.go, internal/sandbox/learning_darwin_test.go, internal/sandbox/learning_linux.go, internal/sandbox/learning_linux_test.go, internal/sandbox/learning_stub.go, internal/sandbox/learning_test.go
  System Overview
  Core Data Structures
    · TraceResult
    · LearnedTemplateInfo
  Template Storage
    · Directory Structure
    · Template Naming
  Path Filtering Pipeline
    · Write Path Filtering
    · Read Path Filtering
  Path Collapsing Algorithm
    · Application Directory Detection
    · Collapsing Logic
    · Deduplication
  Template Generation
    · Generated Sections
  Platform-Specific Implementation
    · Linux: strace
    · macOS: eslogger
  Code Entity Reference
    · Functions

## · Go Library API  (L7453)
  源文件: docs/benchmarking.md, docs/concepts.md, docs/library.md, internal/sandbox/manager.go, pkg/greywall/greywall.go
  Purpose and Scope
  Package Structure
  Installation
  Quick Start Example
  Manager Lifecycle
    · Manager Lifecycle Flow
    · Manager Methods
  Core Functions and Types
    · Platform Detection
    · Configuration Functions
  Configuration Types
    · Config
    · NetworkConfig
    · FilesystemConfig
  Platform Differences in Library Behavior
  Implementation Details
    · Bridge Management
    · Resource Cleanup

## · Development Guide  (L7812)
  源文件: ARCHITECTURE.md, CONTRIBUTING.md, Makefile, docs/architecture.md, docs/contributing.md, docs/faq.md, scripts/pre-commit
  Development Environment Prerequisites
    · Common Requirements
    · Linux-Specific Requirements
    · macOS-Specific Requirements
  Development Workflow
  Build System
    · Build Targets
    · Code Entity Mapping: Build System
  Testing Strategy
    · Running Tests Locally
  CI/CD and Quality Gates
    · Quality Gates
  Release Process
    · Release Commands

## · Building from Source  (L8023)
  源文件: .golangci.yml, CLAUDE.md, Makefile, go.mod, go.sum, scripts/pre-commit
  Prerequisites
    · Go Version
    · System Dependencies
  Build Process
    · Development Setup
    · Compiling the Binary
    · Platform-Specific Builds
  Build Pipeline Architecture
  Dependency Management
    · Go Modules
    · Linting and Formatting
  Testing
    · Unit and Integration Tests
    · Smoke Tests
    · Logic Flow: Test to Binary Association
  Git Hooks

## · CI/CD Pipeline  (L8191)
  源文件: .github/workflows/main.yml, docs/testing.md, docs/troubleshooting.md, scripts/smoke_test.sh
  Workflow Structure
    · Pipeline Jobs Overview
  Trigger Configuration
  Build Job
    · Build Steps
  Lint Job
    · Lint Steps
  Test Jobs
    · Linux Test Job
    · macOS Test Job
  Smoke Test Suite
    · Test Categories
  Quality Gates
  Troubleshooting CI Failures

## · Release Process  (L8464)
  源文件: .github/workflows/notify-docs.yml, .github/workflows/release.yml, .goreleaser.yaml, internal/proxy/brew.go, scripts/bump_version.sh, scripts/release.sh, scripts/release_test.bats
  Release Trigger and Automation
    · Release Script Logic
    · Preflight Checks
    · Version Bumping Logic
  goreleaser Pipeline
    · Build Configuration
    · Archive and Artifacts
    · Changelog Generation
  Distribution and Homebrew
    · Homebrew Tap Integration
    · greyproxy Synchronization
    · Homebrew Management Detection
  Post-Release Notifications

## · Reference  (L8593)
  源文件: LICENSE, SECURITY.md, docs/security-model.md
  Overview
  Security Vulnerability Reporting
    · Security Reporting Workflow
    · Policy Scope
  Licensing Structure
    · Copyright Holders
    · License Key Terms
    · License Application in Codebase
  Reference Materials Relationship to Project Structure
  Key Contacts and Resources

## · Security Policy  (L8803)
  源文件: LICENSE, SECURITY.md
  Vulnerability Reporting Process
    · Contact Information
    · Required Information
    · Vulnerability Reporting Workflow
  Disclosure Timeline
  Security Support Scope
    · Covered Versions
    · Version Support Matrix
  Responsible Disclosure Philosophy
  License and Legal Framework
  Related Documentation

## · License  (L8974)
  源文件: LICENSE, SECURITY.md
  License Overview
  Copyright Holders
  Key Permissions
    · Rights Granted
    · License Scope Diagram
  Redistribution Requirements
    · Mandatory Inclusions
    · Redistribution Flow Diagram
  Patent Grant and Termination
    · Patent License Terms
    · Patent Litigation Termination Clause
  Contribution Terms
    · Default Contribution License
    · Submission Channels
  Disclaimer and Limitation of Liability
    · No Warranty
    · Limitation of Liability
  Trademark Restrictions
  Full License Reference

## · Glossary  (L9228)
  源文件: .github/workflows/release.yml, .goreleaser.yaml, README.md, install.sh, internal/config/config.go, internal/profiles/keyring.go, internal/profiles/profiles_test.go, internal/profiles/prompt.go, internal/profiles/registry.go, internal/profiles/toolchains/scm.go, internal/proxy/brew.go, internal/sandbox/integration_linux_test.go
  Security & Sandboxing Terms
    · Deny-by-Default
    · Learning Mode
    · Profile Drift
    · Credential Substitution
  Platform-Specific Technologies
  Network Architecture Terms
    · greyproxy
    · tun2socks
    · Bridge Components
    · Identification Tokens
  Implementation Diagrams
    · Logic Flow: Linux Sandbox Initialization
    · Data Flow: macOS Sandbox Monitoring
    · Bridge Architecture (Linux)