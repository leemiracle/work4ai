# Skeleton: connectonion（50 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 8KB | 2 | ~3 | 17 |
| 2 | Getting Started | L195 | 10KB | 4 | ~1 | 14 |
| 3 | Installation | L486 | 8KB | 2 | ~3 | 14 |
| 4 | Your First Agent | L703 | 9KB | 2 | ~2 | 20 |
| 5 | Project Structure | L993 | 10KB | 3 | ~3 | 9 |
| 6 | Core Concepts | L1304 | 10KB | 4 | ~6 | 10 |
| 7 | Agent Architecture | L1591 | 10KB | 3 | ~8 | 14 |
| 8 | LLM Integration | L1876 | 9KB | 1 | ~8 | 17 |
| 9 | Tools System | L2113 | 12KB | 5 | ~6 | 20 |
| 10 | Event System | L2437 | 8KB | 2 | ~5 | 6 |
| 11 | Plugin System | L2642 | 13KB | 2 | ~5 | 15 |
| 12 | Sub-Agent System | L2952 | 6KB | 2 | ~1 | 10 |
| 13 | Observability & Debugging | L3102 | 8KB | 3 | ~4 | 8 |
| 14 | Console & Logging | L3330 | 9KB | 3 | ~6 | 11 |
| 15 | Interactive Debugging | L3565 | 6KB | 2 | ~3 | 13 |
| 16 | Session Replay | L3728 | 8KB | 2 | ~2 | 5 |
| 17 | Multi-Agent Networking | L3918 | 10KB | 2 | ~4 | 13 |
| 18 | Hosting Agents | L4124 | 8KB | 2 | ~5 | 15 |
| 19 | Connecting to Remote Agents | L4366 | 7KB | 2 | ~5 | 10 |
| 20 | Trust & Authentication | L4565 | 10KB | 3 | ~1 | 14 |
| 21 | P2P Relay System | L4837 | 8KB | 3 | ~1 | 12 |
| 22 | Built-in Tools & Agents | L5038 | 10KB | 2 | ~10 | 12 |
| 23 | Useful Tools Reference | L5284 | 12KB | 4 | ~9 | 23 |
| 24 | Gmail Integration | L5575 | 11KB | 3 | ~1 | 18 |
| 25 | Browser Agent | L5853 | 9KB | 2 | ~5 | 13 |
| 26 | Email Agent Example | L6031 | 9KB | 2 | ~3 | 8 |
| 27 | CLI Reference | L6285 | 9KB | 1 | ~9 | 11 |
| 28 | Project Commands | L6572 | 14KB | 2 | ~9 | 19 |
| 29 | Authentication Commands | L6908 | 13KB | 5 | ~1 | 13 |
| 30 | Browser Commands | L7246 | 9KB | 2 | ~2 | 12 |
| 31 | Status & Management | L7422 | 12KB | 4 | ~11 | 8 |
| 32 | Development Guide | L7772 | 11KB | 2 | ~7 | 15 |
| 33 | Testing | L8110 | 11KB | 2 | ~3 | 18 |
| 34 | Mock System | L8409 | 9KB | 3 | ~11 | 11 |
| 35 | CI/CD Pipeline | L8670 | 11KB | 3 | ~9 | 10 |
| 36 | API Reference | L8942 | 10KB | 2 | ~9 | 17 |
| 37 | Agent API | L9309 | 9KB | 2 | ~9 | 18 |
| 38 | LLM API | L9559 | 8KB | 2 | ~5 | 14 |
| 39 | Tool API | L9762 | 8KB | 2 | ~2 | 16 |
| 40 | Networking API | L9970 | 9KB | 2 | ~8 | 11 |
| 41 | Best Practices | L10186 | 6KB | 3 | ~1 | 17 |
| 42 | Tool Design | L10347 | 9KB | 2 | ~4 | 13 |
| 43 | System Prompts | L10568 | 8KB | 2 | ~0 | 17 |
| 44 | When to Use LLMs vs Code | L10764 | 10KB | 3 | ~2 | 11 |
| 45 | Error Handling | L11047 | 8KB | 2 | ~6 | 6 |
| 46 | Troubleshooting | L11254 | 4KB | 2 | ~0 | 4 |
| 47 | Common Errors | L11375 | 8KB | 2 | ~3 | 8 |
| 48 | Performance Issues | L11604 | 7KB | 2 | ~2 | 6 |
| 49 | Authentication Problems | L11812 | 10KB | 2 | ~2 | 11 |
| 50 | Glossary | L12045 | 9KB | 2 | ~2 | 35 |


## · Overview  (L6)
  源文件: .gitignore, CLAUDE.md, README.md, VERSIONING.md, connectonion/__init__.py, connectonion/cli/co_ai/agent.py, connectonion/cli/main.py, docs/README.md, docs/quickstart.md, docs/templates/README.md, docs/templates/meta-agent.md, docs/templates/minimal.md
  Purpose and Scope
  Philosophy
  High-Level Architecture
    · System Architecture Diagram
  Core Components
    · 1. The Agent Orchestrator
    · 2. Multi-Provider LLM Abstraction
    · 3. Automatic Tool System
    · 4. Event & Plugin System
  Data Flow: Agent Execution Loop
    · Code Entity Execution Flow
  Key Features
    · Observability & "X-Ray" Debugging
    · Distributed Multi-Agent Networking
    · Built-in Tool Ecosystem
    · "co ai" Coding Assistant
  Project Structure Reference

## · Getting Started  (L195)
  源文件: README.md, connectonion/cli/commands/auth_commands.py, connectonion/cli/commands/create.py, connectonion/cli/commands/init.py, connectonion/cli/commands/project_cmd_lib.py, connectonion/cli/commands/reset_commands.py, connectonion/cli/commands/status_commands.py, docs/README.md, docs/quickstart.md, docs/templates/README.md, docs/templates/meta-agent.md, docs/templates/minimal.md
  Overview: Two Development Paths
  Quick Start Workflow
  CLI-Managed Path: Project Creation Flow
  Authentication System
    · Global Identity Model
  Manual Path: Direct Framework Import
    · Minimal Working Example
  Project Structure Overview
  First Agent Execution
  Next Steps

## · Installation  (L486)
  源文件: README.md, connectonion/cli/commands/auth_commands.py, connectonion/cli/commands/create.py, connectonion/cli/commands/init.py, connectonion/cli/commands/project_cmd_lib.py, connectonion/cli/commands/reset_commands.py, connectonion/cli/commands/status_commands.py, docs/README.md, docs/quickstart.md, docs/templates/README.md, docs/templates/meta-agent.md, docs/templates/minimal.md
  System Requirements
  Installation Methods
    · Via pip (Recommended)
  Post-Installation: Global Setup
    · Global Configuration Initialization Flow
  Project Initialization
    · The `co init` vs `co create` Commands
    · Data Flow: From CLI to Code Entities
  Authentication & Managed Keys
    · Authentication Process (`authenticate`)
  Directory Structure Reference
    · Key Files Created:
  Troubleshooting Installation
    · Resetting Configuration
    · Checking Status

## · Your First Agent  (L703)
  源文件: connectonion/cli/templates/coder/agent.py, connectonion/cli/templates/coder/prompt.md, connectonion/cli/templates/minimal/agent.py, connectonion/cli/templates/minimal/prompt.md, connectonion/cli/templates/web-research/agent.py, connectonion/llm_do.py, examples/minimal-agent/.co/config.toml, examples/minimal-agent/.co/keys/DO_NOT_SHARE, examples/minimal-agent/.co/keys/agent.key, examples/minimal-agent/.co/keys/recovery.txt, examples/minimal-agent/agent.py, examples/simple-agent/.gitignore
  Minimal Working Agent
  Agent Creation Flow
  Adding Tools
    · Function-Based Tools (Recommended)
  Task Execution Flow
  Interactive Debugging with @xray
  LLM-Do: The One-Shot Alternative
  Agent Configuration
  Authentication for Managed Keys
  Next Steps

## · Project Structure  (L993)
  源文件: connectonion/cli/commands/auth_commands.py, connectonion/cli/commands/copy_commands.py, connectonion/cli/commands/create.py, connectonion/cli/commands/init.py, connectonion/cli/commands/project_cmd_lib.py, connectonion/cli/commands/reset_commands.py, connectonion/cli/commands/status_commands.py, connectonion/useful_skills/__init__.py, connectonion/useful_skills/ship-feature/SKILL.md
  Overview
  Global Configuration (`~/.co/`)
    · Directory Structure
    · `config.toml` Schema
    · `keys.env` Contents
    · Ed25519 Keypair
  Project Configuration (`.co/`)
    · Directory Structure
    · `config.toml` Schema
  Project Root Files
    · `.env` File
    · `agent.py` File
    · `co-vibecoding-principles-docs-contexts-all-in-one.md`
  Complete File Hierarchy
  Configuration Initialization Flow
  Key Management Architecture
  Environment Variable Resolution
  Managed Files and Skills
    · Skills Directory

## · Core Concepts  (L1304)
  源文件: connectonion/core/__init__.py, connectonion/core/agent.py, connectonion/core/events.py, connectonion/core/exceptions.py, connectonion/core/llm.py, docs/concepts/events.md, docs/concepts/models.md, tests/unit/test_agent.py, tests/unit/test_events.py, tests/unit/test_groq_llm.py
  Framework Architecture Overview
    · System Architecture Diagram
  The Agent Class
    · Key Responsibilities
    · Agent Constructor
  LLM Integration
    · Model Routing Logic
    · Managed Keys (`co/` prefix)
  Tools System
    · Function-Based Tools
    · Class-Based Tools
  Event System
    · Lifecycle Hook Reference
  Plugin System
    · Plugin Composition
  Execution Flow: Component Interaction

## · Agent Architecture  (L1591)
  源文件: .gitignore, CLAUDE.md, connectonion/core/agent.py, connectonion/logger.py, docs/api.md, docs/concepts/tools.md, examples/browser-agent/CLAUDE.md, examples/browser-agent/web_automation.py, tests/real_api/manual/manual_defaults.py, tests/unit/test_agent.py, tests/unit/test_logger.py, tests/unit/test_tool_executor.py
  Agent Class Overview
  Agent Initialization
    · Constructor Parameters
    · Initialization Flow
  Session Management
    · Session State Structure
    · Multi-Turn Conversations
  Execution Loop
    · High-Level Flow
    · Detailed Loop Phases
  Lifecycle Hooks
  Tool Registry
  Logging and Observability
  Error Handling
    · Tool Execution Errors
    · Tool Not Found

## · LLM Integration  (L1876)
  源文件: connectonion/cli/templates/coder/agent.py, connectonion/cli/templates/coder/prompt.md, connectonion/cli/templates/minimal/agent.py, connectonion/cli/templates/minimal/prompt.md, connectonion/cli/templates/web-research/agent.py, connectonion/core/exceptions.py, connectonion/core/llm.py, connectonion/llm_do.py, docs/concepts/models.md, tests/integration/test_llm.py, tests/integration/test_memory_integration.py, tests/real_api/test_real_anthropic.py
  Purpose and Scope
  LLM Provider Architecture
    · Provider Abstraction Diagram
    · Core Components
  The LLM Interface
    · Core Methods
  Supported Providers & Models
    · Managed Keys (OpenOnion)
    · Bring Your Own Keys (BYOK)
  The `llm_do()` Function
    · Comparison with Agent
    · Usage Examples
  Error Handling and Credits
    · Insufficient Credits
    · Connection Issues
  Technical Implementation Details
    · Model Registry and Inference
    · Structured Output Implementation

## · Tools System  (L2113)
  源文件: CHANGELOG.md, connectonion/core/agent.py, connectonion/logger.py, connectonion/useful_tools/browser_tools/scroll.py, connectonion/useful_tools/file_tools/README.md, connectonion/useful_tools/file_tools/__init__.py, connectonion/useful_tools/file_tools/edit.py, connectonion/useful_tools/file_tools/file_tools.py, connectonion/useful_tools/file_tools/glob.py, connectonion/useful_tools/file_tools/grep.py, connectonion/useful_tools/file_tools/multi_edit.py, connectonion/useful_tools/file_tools/read.py
  System Architecture
  Tool Creation Patterns
    · Function-Based Tools (Recommended)
    · Class-Based Tools (Stateful Operations)
  Schema Generation Pipeline
    · Docstring Processing
  Tool Registry Architecture
  Tool Execution Lifecycle
    · Execution Flow with Events
    · Error Handling
  File Tools (Special Case)
  Performance and Observability
    · Logging
    · Token Usage

## · Event System  (L2437)
  源文件: connectonion/core/__init__.py, connectonion/core/events.py, docs/concepts/events.md, docs/hook-system-options.md, examples/events_example.py, tests/unit/test_events.py
  Purpose and Scope
  Event Lifecycle Overview
    · Agent Execution Timeline
  Event Handler Implementation
    · Registration Syntax
    · Accessing Session State
  Event Types Reference
  Data Flow: The Trace System
  Critical Implementation Notes
    · Message Injection and Provider Compatibility
    · Error Handling in Events
    · Tool Cancellation

## · Plugin System  (L2642)
  源文件: connectonion/network/asgi/__init__.py, connectonion/useful_events_handlers/reflect.py, connectonion/useful_plugins/__init__.py, connectonion/useful_plugins/image_result_formatter.py, connectonion/useful_plugins/prefer_write_tool.py, connectonion/useful_plugins/re_act.py, connectonion/useful_plugins/skills.py, connectonion/useful_plugins/tool_approval/bash_parser.py, docs/concepts/plugins.md, docs/features/transcribe.md, docs/features/trust.md, docs/useful_plugins/prefer_write_tool.md
  Plugin Architecture
    · Core Concept
    · Plugin to Event System Mapping
  Plugin Structure
    · Anatomy of a Plugin
  Built-in Plugins
    · Plugin Catalog
    · re_act Plugin
    · prefer_write_tool Plugin
    · image_result_formatter Plugin
  Creating Custom Plugins
    · Advanced Plugin with Permission Logic
    · Pattern: Scoped Permissions (Skills)
    · Pattern: Bash Command Chain Validation
  Best Practices

## · Sub-Agent System  (L2952)
  源文件: README.md, connectonion/core/agent.py, docs/README.md, docs/quickstart.md, docs/templates/README.md, docs/templates/meta-agent.md, docs/templates/minimal.md, docs/templates/playwright.md, docs/templates/web-research.md, tests/unit/test_agent.py
  Overview
    · Key Benefits
  The `subagents` Plugin
    · Implementation and Hooks
  Task Delegation via `task()`
    · Data Flow: Parent to Sub-Agent
    · Sub-Agent System Architecture
  File-Based Sub-Agent Definitions
    · Discovery Hierarchy
  Cost Optimization Patterns
    · Pattern: Cheap Workers
    · Resource Tracking
    · Sub-Agent Lifecycle and Cost Flow

## · Observability & Debugging  (L3102)
  源文件: connectonion/console.py, docs/debug/auto_debug.md, docs/debug/xray.md, tests/unit/test_address.py, tests/unit/test_console.py, Console & Logging, Interactive Debugging, Session Replay
  Purpose and Scope
  Architecture Overview
    · Design Principles
  Execution Flow with Observability Hooks
  Console Output System
    · Console Architecture
    · Visual Elements
  Interactive Debugging
    · @xray Decorator
    · auto_debug Mode
  Session Replay

## · Console & Logging  (L3330)
  源文件: connectonion/console.py, connectonion/logger.py, docs/api.md, docs/concepts/tools.md, tests/real_api/manual/manual_defaults.py, tests/unit/test_address.py, tests/unit/test_console.py, tests/unit/test_logger.py, tests/unit/test_tool_executor.py, tests/unit/test_tool_executor_errors.py, tests/unit/test_tool_factory.py
  Architecture Overview
    · Component Responsibilities
  Output Destinations
    · Three Logging Channels
  Console Output Format
    · Visual Design System
    · Banner Format
    · Tool Display Formatting
  Configuration Modes
    · Logger Initialization
    · Configuration Matrix
  Session Logging (Evals)
    · File Naming Strategy
    · Run Tracking
    · Run YAML Format
  Tool Execution Logging
    · Error Handling in Logs
  Performance Considerations

## · Interactive Debugging  (L3565)
  源文件: docs/debug/auto_debug.md, docs/debug/xray.md, examples/simple-agent/.gitignore, examples/simple-agent/README.md, examples/simple-agent/agent.py, examples/simple-agent/agent_debug.py, examples/simple-agent/test_e2e.py, examples/simple-agent/test_network.py, examples/simple-agent/tests/test_api_integration.py, examples/simple-agent/tests/test_debug_features.py, examples/simple-agent/tests/test_models.py, tests/unit/test_auto_debug_exception.py
  Purpose and Scope
  Debugging Architecture Overview
  The @xray Decorator
    · Context Access
    · Implementation Example
  Interactive Debugging with auto_debug()
    · Breakpoint Actions
    · Variable Modification (REPL)
  AI-Powered Runtime Inspection
    · Key Inspector Capabilities
  Usage Summary

## · Session Replay  (L3728)
  源文件: connectonion/cli/commands/ai_commands.py, connectonion/core/tool_executor.py, connectonion/useful_plugins/eval.py, connectonion/useful_plugins/ulw.py, docs/session-persistence.md
  Overview
  Session Recording Architecture
    · Execution to Code Entity Mapping
  Session Data Structure
  Evaluation and Replay Logic
    · Logic Flow: Natural Language to Code
  Replay vs. Autonomous Modes (ULW)
  Client-Side Persistence
  Best Practices for Replayable Tools

## · Multi-Agent Networking  (L3918)
  源文件: connectonion/network/asgi/http.py, connectonion/network/asgi/websocket.py, connectonion/network/connect.py, connectonion/network/host/routes.py, connectonion/network/host/server.py, connectonion/network/host/session/active.py, docs/network/README.md, docs/network/connect.md, docs/network/session-reconnect.md, docs/network/websocket-protocol.md, tests/unit/test_asgi_http.py, tests/unit/test_host_routes.py
  Core Components
    · host()
    · connect()
    · P2P Relay
  System Architecture
  Message Flow & Reconnection
  Protocol Reference
    · HTTP Endpoints
    · WebSocket Messages
  Implementation Details
    · Result Persistence
    · Endpoint Resolution
  Next Steps

## · Hosting Agents  (L4124)
  源文件: connectonion/cli/co_ai/prompts/connectonion/network/host.md, connectonion/cli/co_ai/prompts/tools/ask_user.md, connectonion/cli/co_ai/tools/todo_list.py, connectonion/network/asgi/http.py, connectonion/network/host/__init__.py, connectonion/network/host/routes.py, connectonion/network/host/server.py, connectonion/network/host/session/__init__.py, connectonion/network/host/session/merge.py, connectonion/network/host/session/storage.py, connectonion/network/host/session/ui.py, connectonion/network/static/docs.html
  Purpose and Function Signature
  Request Flow Architecture
  HTTP API Endpoints
    · POST /input
    · GET /info
  WebSocket API (`/ws`)
  Session Management and Storage
  Deployment and Scaling
    · Worker Isolation
    · Admin Endpoints

## · Connecting to Remote Agents  (L4366)
  源文件: connectonion/network/asgi/websocket.py, connectonion/network/connect.py, connectonion/network/host/session/active.py, docs/network/README.md, docs/network/connect.md, docs/network/io.md, docs/network/session-reconnect.md, docs/network/session-websocket-lifecycle.md, docs/network/websocket-protocol.md, tests/unit/test_host_session.py
  Overview
  Network Architecture
    · Data Flow Diagram
  The Connection Protocol
    · WebSocket Lifecycle
    · Message Reference (Client → Server)
  Session Management & Reconnection
    · Active Session Registry
  Endpoint Resolution (Direct vs. Relay)
    · Resolution Logic
  Client-Side UI Events
  Summary of Key Classes

## · Trust & Authentication  (L4565)
  源文件: connectonion/address.py, connectonion/network/host/config.py, connectonion/network/host/host.yaml, docs/features/permissions.md, docs/network/host-config.md, docs/useful_plugins/tool_approval.md, docs/windows-support.md, tests/integration/test_config_permissions.py, tests/unit/test_announce.py, tests/unit/test_decorators.py, tests/unit/test_email_functions.py, tests/unit/test_trust.py
  Ed25519 Identity System
    · Keypair Structure
    · Key Generation and Storage
  Message Signing Protocol
    · ANNOUNCE Message Structure
    · Signature Verification Flow
  Trust Levels & Policies
    · Standard Trust Levels
    · Unified Permission System
    · Config-Based Auto-Approval
  Tool Approval Lifecycle
  Authentication with OpenOnion Backend
    · API Key and Email Activation
  Security Best Practices

## · P2P Relay System  (L4837)
  源文件: connectonion/network/asgi/http.py, connectonion/network/host/routes.py, connectonion/network/host/server.py, docs/design-decisions/022-raw-asgi-implementation.md, tests/integration/test_host.py, tests/integration/test_host_ws.py, tests/unit/test_asgi.py, tests/unit/test_asgi_http.py, tests/unit/test_asgi_websocket_admin_onboard.py, tests/unit/test_connect.py, tests/unit/test_host_relay.py, tests/unit/test_host_routes.py
  Architecture Overview
  Relay Server Endpoints
  Message Protocol
    · ANNOUNCE Message
    · INPUT/OUTPUT Message Flow
  Agent Discovery & Metadata
    · Address Management
    · Info Endpoint
  Session Persistence and Recovery
  Security & Trust
    · Signature Verification
    · Onboarding Flow
  Implementation Details: Raw ASGI

## · Built-in Tools & Agents  (L5038)
  源文件: connectonion/cli/browser_agent/__init__.py, connectonion/cli/browser_agent/agent.py, connectonion/cli/commands/browser_commands.py, connectonion/useful_plugins/shell_approval.py, connectonion/useful_tools/__init__.py, connectonion/useful_tools/browser_tools/browser.py, connectonion/useful_tools/diff_writer.py, connectonion/useful_tools/gmail.py, connectonion/useful_tools/shell.py, connectonion/useful_tools/terminal.py, connectonion/useful_tools/todo_list.py, connectonion/useful_tools/web_fetch.py
  Tool Architecture
  Tool Categories
    · Human-in-the-Loop Tools
    · System Interaction Tools
    · Progress Tracking Tools
    · Web & Browser Tools
    · Communication Tools
  Specialized Agents
    · Browser Agent
    · Email Agent
  Tool Quick Reference
  Next Steps

## · Useful Tools Reference  (L5284)
  源文件: CHANGELOG.md, connectonion/useful_plugins/shell_approval.py, connectonion/useful_tools/__init__.py, connectonion/useful_tools/browser_tools/scroll.py, connectonion/useful_tools/diff_writer.py, connectonion/useful_tools/file_tools/README.md, connectonion/useful_tools/file_tools/__init__.py, connectonion/useful_tools/file_tools/edit.py, connectonion/useful_tools/file_tools/file_tools.py, connectonion/useful_tools/file_tools/glob.py, connectonion/useful_tools/file_tools/grep.py, connectonion/useful_tools/file_tools/multi_edit.py
  Purpose and Scope
  Tool Architecture Overview
  FileTools - Claude Code-style Operations
    · Key Features
    · API Reference
  DiffWriter - Interactive File Writing
    · Permission Modes
    · API Reference
    · Approval Workflow
  Shell - Command Execution
    · Key Features
    · Safety with `shell_approval` Plugin
  TodoList - Task Tracking
    · Key Features
  WebFetch - Web Content Retrieval
    · Key Features
  Terminal Utilities - Interactive Inputs

## · Gmail Integration  (L5575)
  源文件: connectonion/cli/commands/__init__.py, connectonion/useful_plugins/calendar_plugin.py, connectonion/useful_plugins/gmail_plugin.py, connectonion/useful_tools/get_emails.py, connectonion/useful_tools/google_calendar.py, connectonion/useful_tools/microsoft_calendar.py, connectonion/useful_tools/outlook.py, connectonion/useful_tools/send_email.py, connectonion/useful_tools/slash_command.py, examples/email-agent/run_test.sh, examples/minimal-agent/.co/docs/co-vibecoding-principles-docs-contexts-all-in-one.md, tests/unit/test_calendar_plugin.py
  Purpose and Scope
  Architecture Overview
    · Code Entity Mapping
    · System Data Flow
  OAuth Setup Process
    · CLI Command Flow
    · Credential Format
  Gmail Class
    · Initialization and Scope Validation
    · Service Lifecycle and Token Refresh
  Core Methods
    · Reading and Content Extraction
    · Sending and Management
  Human-in-the-Loop: Gmail Plugin
    · Approval Workflow
    · Key Features
  Troubleshooting
    · Common Setup Issues

## · Browser Agent  (L5853)
  源文件: connectonion/cli/browser_agent/__init__.py, connectonion/cli/browser_agent/agent.py, connectonion/cli/browser_agent/prompts/agent.md, connectonion/cli/commands/browser_commands.py, connectonion/cli/templates/browser/prompts/agent.md, connectonion/useful_tools/browser_tools/__init__.py, connectonion/useful_tools/browser_tools/browser.py, connectonion/useful_tools/browser_tools/browser_config.py, connectonion/useful_tools/browser_tools/element_finder.py, connectonion/useful_tools/browser_tools/highlight_screenshot.py, connectonion/useful_tools/browser_tools/prompts/element_matcher.md, connectonion/useful_tools/browser_tools/scripts/extract_elements.js
  Purpose and Scope
  System Overview
    · Key Capabilities
  Architecture & Data Flow
    · Component Interaction Diagram
  Natural Language Element Finding
    · The Finding Pipeline
    · Element Identification Diagram
  Session Persistence
  Core Tool Reference
  CLI Integration

## · Email Agent Example  (L6031)
  源文件: connectonion/cli/commands/__init__.py, connectonion/useful_tools/get_emails.py, connectonion/useful_tools/send_email.py, examples/email-agent/agent.py, examples/email-agent/prompts/email_assistant.md, examples/email-agent/prompts/email_composer.md, examples/email-agent/run_test.sh, examples/minimal-agent/.co/docs/co-vibecoding-principles-docs-contexts-all-in-one.md
  Overview
  Architecture
  Gmail Tools Integration
  ReAct Pattern Implementation
    · Plan Phase: `plan_task`
    · Reflect Phase: `reflect`
  Gmail Plugin Approval Workflow
    · Before Send Approval
    · After Send CRM Sync
  Complete Execution Flow
  Running the Email Agent
    · Setup
    · Execution Loop

## · CLI Reference  (L6285)
  源文件: VERSIONING.md, connectonion/__init__.py, connectonion/cli/co_ai/agent.py, connectonion/cli/commands/auth_commands.py, connectonion/cli/commands/create.py, connectonion/cli/commands/init.py, connectonion/cli/commands/project_cmd_lib.py, connectonion/cli/commands/reset_commands.py, connectonion/cli/commands/status_commands.py, connectonion/cli/main.py, pyproject.toml
  Command Structure
    · Global Flags
  Command Overview
    · Command Categories
  Quick Reference Table
  Project Commands
    · `co init`
    · `co create`
  Authentication Commands
    · `co auth`
  Browser Commands
    · `co browser`
  Status & Management
    · `co status`
    · `co reset`
  Execution: `co ai`

## · Project Commands  (L6572)
  源文件: connectonion/cli/co_ai/plugins/system_reminder.py, connectonion/cli/co_ai/prompts/assembler.py, connectonion/cli/co_ai/prompts/main.md, connectonion/cli/commands/auth_commands.py, connectonion/cli/commands/create.py, connectonion/cli/commands/init.py, connectonion/cli/commands/project_cmd_lib.py, connectonion/cli/commands/reset_commands.py, connectonion/cli/commands/status_commands.py, connectonion/useful_tools/memory.py, docs/cli/copy.md, tests/cli/argparse_runner.py
  Command Overview
  Command Execution Flow
  co init Command
    · Syntax
    · Options
    · Behavior
  co create Command
    · Syntax
    · Arguments
    · Options
    · Behavior
  Template System
    · Available Templates
    · Custom Template AI Generation
  Authentication Integration
  API Key Detection

## · Authentication Commands  (L6908)
  源文件: connectonion/cli/commands/auth_commands.py, connectonion/cli/commands/create.py, connectonion/cli/commands/init.py, connectonion/cli/commands/project_cmd_lib.py, connectonion/cli/commands/reset_commands.py, connectonion/cli/commands/status_commands.py, connectonion/useful_tools/memory.py, tests/cli/argparse_runner.py, tests/cli/test_cli.py, tests/cli/test_cli_auth_google.py, tests/cli/test_cli_create.py, tests/cli/test_cli_init.py
  Purpose and Scope
  Command Overview
  Ed25519 Authentication Flow
    · Authentication Architecture
    · `co auth` Command
    · Core Authentication Logic
    · Key Storage Locations
  OAuth Integration Flow
    · Google OAuth Architecture
    · `co auth google` Command
    · `co auth microsoft` Command
  Key Storage and Priority
    · API Key Lookup Order
    · File Structure
  Integration with Other Commands
    · Authentication in Project Initialization
    · Authentication in Account Reset
  Security Considerations
    · Ed25519 Signature Verification
    · File Permissions

## · Browser Commands  (L7246)
  源文件: connectonion/cli/browser_agent/__init__.py, connectonion/cli/browser_agent/agent.py, connectonion/cli/co_ai/main.py, connectonion/cli/commands/browser_commands.py, connectonion/network/trust/__init__.py, connectonion/network/trust/factory.py, connectonion/network/trust/fast_rules.py, connectonion/network/trust/trust_agent.py, connectonion/useful_plugins/auto_compact.py, connectonion/useful_plugins/system_reminder.py, connectonion/useful_tools/bash.py, connectonion/useful_tools/browser_tools/browser.py
  Overview
  Command Invocation
    · Basic Syntax
    · Authentication Requirement
  System Architecture
    · Execution Data Flow
  BrowserAutomation Class
    · Core Implementation Details
    · Tool Methods
  Agent Configuration
    · Context Management
  Common Workflows
    · Manual Login & Session Persistence
    · Natural Language Navigation
  Error Handling

## · Status & Management  (L7422)
  源文件: connectonion/cli/commands/auth_commands.py, connectonion/cli/commands/create.py, connectonion/cli/commands/deploy_commands.py, connectonion/cli/commands/init.py, connectonion/cli/commands/project_cmd_lib.py, connectonion/cli/commands/reset_commands.py, connectonion/cli/commands/status_commands.py, tests/e2e/test_deploy.py
  Commands Overview
  `co status` - Account Status Display
    · Purpose
    · Output Information
    · API Key Lookup Order
    · Re-Authentication Flow
  `co reset` - Full Account Reset
    · Purpose
    · What Gets Deleted
    · Reset and Recreation Workflow
    · Fresh Account Registration
    · Seed Phrase Display
  Deployment Status & Management
    · Deployment Polling Logic
  Error Handling
    · `co status` Errors
    · `co reset` Errors
  Code Entity Mapping
    · Key Functions
    · Integration Points

## · Development Guide  (L7772)
  源文件: .github/workflows/tests.yml, pytest.ini, tests/.env.example, tests/README.md, tests/conftest.py, tests/fixtures/test_tools.py, tests/integration/test_agent_workflows.py, tests/integration/test_announce_only.py, tests/integration/test_auth_integration.py, tests/integration/test_benchmarks.py, tests/real_api/__init__.py, tests/real_api/conftest.py
  Purpose and Scope
  Development Environment Setup
    · Prerequisites
    · Project Structure for Development
  Test Organization Architecture
  Running Tests
    · Basic Test Execution
    · Test Configuration
    · Environment Setup for Real API Tests
  Mock System Architecture
    · MockLLM Implementation
  Test Fixtures Reference
    · Standard Fixtures
    · Real API Test Fixtures
  CI/CD Pipeline
    · Workflow Configuration
    · Tox Integration
  Benchmark Tests
    · Performance Tracking
  Writing New Tests

## · Testing  (L8110)
  源文件: .github/workflows/tests.yml, pytest.ini, tests/.env.example, tests/README.md, tests/conftest.py, tests/fixtures/test_tools.py, tests/integration/test_agent_workflows.py, tests/integration/test_announce_only.py, tests/integration/test_auth_integration.py, tests/integration/test_benchmarks.py, tests/integration/test_llm.py, tests/real_api/__init__.py
  Purpose and Scope
  Test Organization
    · Directory Structure
    · Pytest Markers
  Running Tests
    · Basic Commands
    · Environment Setup
  Test Categories
    · Diagram: Test Category Flow
    · Integration Tests
    · Real API Tests
  Mock System
    · MockLLM and Response Builders
    · Diagram: Mock System Data Flow
  Performance Benchmarks
  CI/CD Pipeline
  Writing New Tests
    · Using ProjectHelper
    · Adding a Unit Test

## · Mock System  (L8409)
  源文件: connectonion/logger.py, docs/api.md, docs/concepts/tools.md, examples/xray_debug_example.py, tests/real_api/manual/manual_defaults.py, tests/unit/test_logger.py, tests/unit/test_tool_executor.py, tests/unit/test_tool_executor_errors.py, tests/unit/test_tool_factory.py, tests/utils/__init__.py, tests/utils/mock_helpers.py
  Overview
  Core Mock Classes
    · MockLLM Class
    · Response Builder Classes
  Workflow Mockers
  Tool Execution Testing
  Test Fixtures
  Usage Patterns
    · Pattern 1: Asserting Tool Calls
    · Pattern 2: Testing Error Handling
  Summary

## · CI/CD Pipeline  (L8670)
  源文件: .github/workflows/tests.yml, connectonion/cli/commands/deploy_commands.py, tests/e2e/test_deploy.py, tests/fixtures/test_tools.py, tests/integration/test_agent_workflows.py, tests/integration/test_auth_integration.py, tests/integration/test_benchmarks.py, tests/real_api/__init__.py, tests/real_api/conftest.py, tox.ini
  Overview
  GitHub Actions Workflow
    · Workflow Structure
    · Key Configuration Details
    · Dependency Installation
    · API Key Management
  Test Categories and Markers
    · Test Marker Hierarchy
    · Marker Definitions
    · Real API Test Auto-Marking
  Performance Benchmarking
    · Benchmark Categories
  Deployment Infrastructure
    · Deployment Flow
    · Deployment Validation
  Tox Configuration
    · Tox Environments
    · Real API Test Setup

## · API Reference  (L8942)
  源文件: VERSIONING.md, connectonion/__init__.py, connectonion/cli/co_ai/agent.py, connectonion/cli/main.py, connectonion/logger.py, docs/api.md, docs/concepts/tools.md, pyproject.toml, tests/real_api/manual/manual_defaults.py, tests/unit/test_logger.py, tests/unit/test_tool_executor.py, tests/unit/test_tool_executor_errors.py
  Purpose and Scope
  Public API Organization
  Import Patterns
  Core API Modules
    · Module Dependency Diagram
  Agent API Summary
    · Constructor Signature
    · Key Methods
  LLM API Summary
    · Provider Routing
    · Core Interface
  llm_do Function
  Tool API Summary
    · Function-Based Tool Creation
    · Schema Generation Rules
  Networking API Summary
    · host() Function
    · connect() Function
  Logger API
    · Configuration
    · File Locations
  Built-in Tools Reference
  Error Handling
    · Tool Execution Errors
  Version Information

## · Agent API  (L9309)
  源文件: connectonion/core/agent.py, connectonion/logger.py, docs/api.md, docs/cli/README.md, docs/cli/create.md, docs/cli/init.md, docs/concepts/agent.md, docs/concepts/llm_do.md, docs/concepts/max_iterations.md, docs/concepts/tools.md, docs/connectonion.md, docs/useful_plugins/README.md
  Purpose and Scope
  Class Entity Mapping
  Constructor
    · `Agent.__init__()`
    · Parameters
  Core Methods
    · `input()`
    · `add_tool()`
  Session State Structure
  Event Lifecycle Hooks
  Tool Registry Access
  Logging & Observability
  Error Handling

## · LLM API  (L9559)
  源文件: connectonion/cli/templates/coder/agent.py, connectonion/cli/templates/coder/prompt.md, connectonion/cli/templates/minimal/agent.py, connectonion/cli/templates/minimal/prompt.md, connectonion/cli/templates/web-research/agent.py, connectonion/core/exceptions.py, connectonion/core/llm.py, connectonion/llm_do.py, docs/concepts/models.md, tests/real_api/manual/manual_llm_do_examples.py, tests/real_api/test_real_gemini.py, tests/real_api/test_real_multi_llm.py
  Overview
    · Architecture Diagram: Natural Language to Code Entity
  Provider Factory
    · `create_llm()`
  Base LLM Interface
    · `complete()`
    · `structured_complete()`
  llm_do() Function
    · Data Flow: llm_do Execution
    · Usage Examples
  Managed Keys (OpenOnion)
    · Model Naming
    · Error Handling: Insufficient Credits
  Provider Reference
    · Supported Providers & Models
    · Gemini 3 & Thinking Models

## · Tool API  (L9762)
  源文件: connectonion/logger.py, connectonion/useful_plugins/shell_approval.py, connectonion/useful_tools/__init__.py, connectonion/useful_tools/diff_writer.py, connectonion/useful_tools/gmail.py, connectonion/useful_tools/shell.py, connectonion/useful_tools/terminal.py, connectonion/useful_tools/todo_list.py, connectonion/useful_tools/web_fetch.py, docs/api.md, docs/concepts/tools.md, tests/real_api/manual/manual_defaults.py
  Overview
  Tool Creation Function
    · `create_tool_from_function(func: Callable) -> Tool`
  Tool Interface
    · Tool Properties
    · Tool Methods
  Tool Registry & Execution
    · Tool Executor Details
  Specialized Tool APIs
    · IO-Aware Tools (e.g., `DiffWriter`)
    · Terminal Utilities
    · Approval Plugins

## · Networking API  (L9970)
  源文件: connectonion/network/asgi/http.py, connectonion/network/asgi/websocket.py, connectonion/network/connect.py, connectonion/network/host/routes.py, connectonion/network/host/server.py, connectonion/network/io/base.py, connectonion/network/io/websocket.py, docs/network/session-reconnect.md, docs/network/websocket-protocol.md, tests/unit/test_asgi_http.py, tests/unit/test_host_routes.py
  Overview
  host() Function
    · Function Signature
    · Parameters
  HTTP/WebSocket Architecture
    · Endpoint Routing
  Session Management & Reconnection
    · Session Storage
  Bidirectional IO Interface
    · IO Methods
  connect() and RemoteAgent
    · Usage Example
    · Endpoint Resolution
  Authentication & Trust
    · Request Verification Steps

## · Best Practices  (L10186)
  源文件: README.md, connectonion/cli/co_ai/prompts/connectonion/agent-design.md, connectonion/cli/co_ai/prompts/connectonion/index.md, connectonion/cli/co_ai/prompts/tools/bash.md, connectonion/cli/co_ai/prompts/workflow.md, connectonion/cli/co_ai/tools/ask_user.py, docs/README.md, docs/quickstart.md, docs/templates/README.md, docs/templates/meta-agent.md, docs/templates/minimal.md, docs/templates/playwright.md
  Core Design Philosophy
    · Function-Based Design
  Tool Design
  System Prompts
  When to Use LLMs vs Code
  Error Handling
  Summary of Best Practices

## · Tool Design  (L10347)
  源文件: connectonion/cli/co_ai/prompts/connectonion/agent-design.md, connectonion/cli/co_ai/prompts/connectonion/index.md, connectonion/cli/co_ai/prompts/tools/bash.md, connectonion/cli/co_ai/prompts/workflow.md, connectonion/cli/co_ai/tools/ask_user.py, connectonion/logger.py, docs/api.md, docs/concepts/tools.md, tests/real_api/manual/manual_defaults.py, tests/unit/test_logger.py, tests/unit/test_tool_executor.py, tests/unit/test_tool_executor_errors.py
  Core Design Philosophy
  Tool Creation Lifecycle
  Function-Based Tool Design
    · Basic Structure
    · Type Mapping Table
  Class-Based Tool Design
    · Shared State Management
  Error Handling in Tools
    · Error as Messages
    · Execution Tracing
  Tool Design Rules
  Specialized Tool Patterns
    · Interactive Tools (`ask_user`)
    · Built-in Tool Customization

## · System Prompts  (L10568)
  源文件: MANIFEST.in, connectonion/cli/templates/coder/agent.py, connectonion/cli/templates/coder/prompt.md, connectonion/cli/templates/minimal/agent.py, connectonion/cli/templates/minimal/prompt.md, connectonion/cli/templates/web-research/agent.py, connectonion/llm_do.py, connectonion/useful_prompts/README.md, connectonion/useful_prompts/__init__.py, connectonion/useful_prompts/coding_agent/README.md, connectonion/useful_prompts/coding_agent/assembler.py, connectonion/useful_prompts/coding_agent/prompts/main.md
  What System Prompts Are
  Loading Mechanisms
    · Agent Interface
    · One-Shot Interface (`llm_do`)
  Modular Prompt Assembly
    · The Assembler Pattern
    · Implementation Example
  Tool-Specific Guidance Best Practices
    · Pattern: When to Use vs. When NOT to Use
  Data Flow: Prompt to Provider
  Prompt Engineering Principles

## · When to Use LLMs vs Code  (L10764)
  源文件: connectonion/cli/co_ai/prompts/connectonion/agent-design.md, connectonion/cli/co_ai/prompts/connectonion/index.md, connectonion/cli/co_ai/prompts/tools/bash.md, connectonion/cli/co_ai/prompts/workflow.md, connectonion/cli/co_ai/tools/ask_user.py, connectonion/cli/templates/coder/agent.py, connectonion/cli/templates/coder/prompt.md, connectonion/cli/templates/minimal/agent.py, connectonion/cli/templates/minimal/prompt.md, connectonion/cli/templates/web-research/agent.py, connectonion/llm_do.py
  Purpose and Scope
  Decision Framework
  Use Case: Pure Code (No LLM)
    · When to Use
    · Examples from Codebase
  Use Case: llm_do() - One-Shot LLM Calls
    · When to Use
    · Architecture
    · Examples from Codebase
  Use Case: Agent with Tools
    · When to Use
    · Architecture
    · Examples from Codebase
  Comparison Table
  Best Practices

## · Error Handling  (L11047)
  源文件: connectonion/core/agent.py, connectonion/core/exceptions.py, connectonion/core/llm.py, docs/concepts/models.md, tests/unit/test_agent.py, tests/unit/test_groq_llm.py
  Purpose and Scope
  Core Principles
  Error Flow Architecture
  Provider and Connection Errors
    · 1. Insufficient Credits (`InsufficientCreditsError`)
    · 2. Connection Failures (`LLMConnectionError`)
    · 3. Service Errors (`ProviderServiceError`)
  Tool Execution Error Handling
    · Recovery Patterns in Tools
  LLM Provider Specific Handling
  Event System and Error Hooks
  Iteration Limits
  Summary of Error States

## · Troubleshooting  (L11254)
  源文件: connectonion/console.py, docs/debug/xray.md, tests/unit/test_address.py, tests/unit/test_console.py
  Diagnostic Workflow
  Debugging Tools & Strategies
    · 1. Console & Logging
    · 2. Interactive Debugging with `@xray`
  Common Issue Categories
    · Common Errors
    · Performance Issues
    · Authentication Problems
  Code-to-System Mapping

## · Common Errors  (L11375)
  源文件: connectonion/core/exceptions.py, connectonion/core/llm.py, docs/concepts/models.md, tests/integration/test_memory_integration.py, tests/unit/test_env_autoload.py, tests/unit/test_groq_llm.py, tests/unit/test_llm_errors.py, tests/unit/test_openonion_llm.py
  Purpose and Scope
  Error Categories Overview
  Authentication & LLM Initialization Errors
    · Error: "Missing API key"
    · Error: "Unknown model"
  Managed Key & Billing Errors
    · Error: "Insufficient ConnectOnion Credits"
  Tool Execution & Structured Output Errors
    · Error: "JSON Parsing Error in Tool Arguments"
    · Error: Structured Output Refusal
  Connection & Provider Errors
    · Error: "LLMConnectionError"
    · Error: "Provider Service Error (HTTP 503)"

## · Performance Issues  (L11604)
  源文件: connectonion/cli/commands/ai_commands.py, connectonion/core/agent.py, connectonion/core/tool_executor.py, connectonion/useful_plugins/eval.py, connectonion/useful_plugins/ulw.py, tests/unit/test_agent.py
  Common Performance Symptoms
    · Slow Response Times
    · Memory Growth
    · Iteration Limit Exhaustion
  Diagnostic Tools
    · Response Time Analysis
    · Plugin-Based Evaluation
  Performance Optimization Strategies
    · Reducing LLM Calls
    · Optimizing Tool Execution
    · Logging Configuration for Performance
  Multi-Agent Performance
    · Autonomous Mode (ULW)
    · Performance Checklist

## · Authentication Problems  (L11812)
  源文件: connectonion/address.py, connectonion/cli/commands/auth_commands.py, connectonion/cli/commands/create.py, connectonion/cli/commands/init.py, connectonion/cli/commands/project_cmd_lib.py, connectonion/cli/commands/reset_commands.py, connectonion/cli/commands/status_commands.py, docs/windows-support.md, tests/unit/test_decorators.py, tests/unit/test_email_functions.py, tests/unit/test_trust.py
  Purpose and Scope
  Authentication Architecture Overview
    · Authentication Flow: OpenOnion Managed Keys
  Common Error Messages
    · "❌ No agent keys found!"
    · "❌ No API key found"
    · "❌ Registration failed: Invalid signature"
    · "❌ Authorization timed out"
  Provider-Specific Troubleshooting
    · OpenOnion Managed Keys (co/ models)
    · Windows-Specific Issues
  Code Entity Map: Authentication System
  Recovery Procedures
    · Resetting Global Identity
    · Verification and Testing

## · Glossary  (L12045)
  源文件: README.md, VERSIONING.md, connectonion/__init__.py, connectonion/cli/browser_agent/__init__.py, connectonion/cli/browser_agent/agent.py, connectonion/cli/co_ai/agent.py, connectonion/cli/commands/browser_commands.py, connectonion/cli/main.py, connectonion/core/agent.py, connectonion/network/asgi/http.py, connectonion/network/host/config.py, connectonion/network/host/host.yaml
  Core Architectural Terms
    · Agent
    · Tool / ToolRegistry
    · Session
    · Lifecycle Hooks / Events
  Networking & Hosting Jargon
    · Host
    · Trust / TrustAgent
    · Relay / Announce
  Technical Mapping: Natural Language to Code
    · Agent Execution Loop
    · Hosting and Permission Flow
  Specialized Tools & Plugins
  Permission Jargon
    · Unified Permission Format
    · Tool-Level Approval
    · Safe Tools