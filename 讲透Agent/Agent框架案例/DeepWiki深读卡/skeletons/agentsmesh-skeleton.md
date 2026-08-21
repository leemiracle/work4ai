# Skeleton: agentsmesh（41 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 11KB | 2 | ~13 | 36 |
| 2 | Architecture | L271 | 19KB | 6 | ~17 | 35 |
| 3 | Core Concepts | L663 | 16KB | 5 | ~12 | 31 |
| 4 | Backend | L1007 | 14KB | 4 | ~10 | 32 |
| 5 | REST API Routes | L1356 | 22KB | 2 | ~61 | 22 |
| 6 | gRPC API and Runner Communication | L1806 | 17KB | 5 | ~25 | 31 |
| 7 | Runner Connection Manager | L2183 | 11KB | 6 | ~11 | 14 |
| 8 | MCP and Mesh Service | L2444 | 19KB | 6 | ~24 | 22 |
| 9 | Ticket Service | L2947 | 16KB | 4 | ~13 | 19 |
| 10 | Billing and Subscriptions | L3318 | 16KB | 4 | ~25 | 11 |
| 11 | Configuration | L3698 | 18KB | 5 | ~39 | 18 |
| 12 | PKI and mTLS | L4142 | 15KB | 4 | ~18 | 7 |
| 13 | Object Storage | L4546 | 11KB | 4 | ~12 | 11 |
| 14 | Real-time Events and WebSocket | L4848 | 15KB | 3 | ~13 | 25 |
| 15 | Runner | L5239 | 15KB | 4 | ~20 | 17 |
| 16 | Installation and Registration | L5652 | 13KB | 4 | ~15 | 17 |
| 17 | CLI Reference | L5980 | 13KB | 6 | ~19 | 17 |
| 18 | gRPC Client | L6349 | 13KB | 3 | ~17 | 17 |
| 19 | Pod and Terminal Management | L6665 | 16KB | 5 | ~12 | 17 |
| 20 | Relay Client | L7050 | 14KB | 5 | ~16 | 9 |
| 21 | MCP Server | L7413 | 17KB | 3 | ~22 | 12 |
| 22 | Workspace and Git Management | L7792 | 11KB | 4 | ~5 | 11 |
| 23 | Auto-Update | L8090 | 10KB | 3 | ~9 | 7 |
| 24 | Relay | L8352 | 13KB | 4 | ~11 | 9 |
| 25 | Channel and Session Management | L8617 | 18KB | 4 | ~20 | 9 |
| 26 | Backend Registration and Heartbeat | L9007 | 15KB | 3 | ~10 | 23 |
| 27 | Web Frontend | L9362 | 14KB | 4 | ~18 | 28 |
| 28 | Terminal Workspace | L9730 | 19KB | 6 | ~16 | 17 |
| 29 | Ticket Management | L10131 | 18KB | 5 | ~18 | 18 |
| 30 | AgentsMesh Network View | L10611 | 18KB | 6 | ~26 | 19 |
| 31 | Channels and Chat | L11029 | 13KB | 5 | ~15 | 8 |
| 32 | Real-time State Management | L11349 | 18KB | 5 | ~31 | 11 |
| 33 | Environment and API Configuration | L11775 | 10KB | 3 | ~7 | 4 |
| 34 | Web Admin | L12025 | 12KB | 5 | ~12 | 15 |
| 35 | Development Environment | L12278 | 16KB | 3 | ~14 | 22 |
| 36 | Docker Compose Services | L12699 | 16KB | 2 | ~41 | 22 |
| 37 | Local Runner and Gitea Setup | L13165 | 11KB | 4 | ~8 | 14 |
| 38 | Deployment | L13435 | 9KB | 2 | ~12 | 22 |
| 39 | CI/CD Pipeline | L13693 | 15KB | 4 | ~20 | 11 |
| 40 | Release Process | L14066 | 15KB | 3 | ~17 | 25 |
| 41 | On-Premise Deployment | L14455 | 18KB | 5 | ~19 | 25 |


## · Overview  (L6)
  源文件: .claude/skills/worktree/SKILL.md, CLAUDE.md, README.md, backend/internal/api/grpc/runner_adapter_mcp.go, backend/internal/api/grpc/runner_adapter_mcp_ticket.go, backend/internal/service/ticket/ticket_query.go, backend/internal/service/ticket/ticket_query_test.go, deploy/dev/.gitignore, deploy/dev/backend.Dockerfile, deploy/dev/docker-compose.yml, deploy/dev/init-seed.sh, deploy/dev/nginx/conf.d/default.conf
  What is AgentsMesh?
  BYOK (Bring Your Own Key)
  Self-Hosted Execution Model
  Key Components
  Supported Agents
  Tech Stack
  Project Layout
  Quick Start

## · Architecture  (L271)
  源文件: .claude/skills/gh-merge/SKILL.md, .claude/skills/worktree/SKILL.md, CLAUDE.md, README.md, backend/cmd/server/eventbus_relay.go, backend/cmd/server/main.go, backend/internal/api/grpc/command_sender_adapter.go, backend/internal/api/grpc/runner_adapter_mcp.go, backend/internal/api/grpc/runner_adapter_mcp_ticket.go, backend/internal/api/grpc/runner_adapter_send.go, backend/internal/api/grpc/runner_adapter_send_extra_test.go, backend/internal/api/grpc/runner_adapter_test.go
  Control Plane vs. Data Plane
  Component Topology
  Control Plane: gRPC + mTLS
    · Protocol Definition
    · Backend-Side Control Plane Components
    · Runner-Side Control Plane Components
  Data Plane: WebSocket Terminal Streaming
    · Relay Architecture
    · Runner Relay Client
    · Relay Token Refresh
  MCP over gRPC
  Real-Time Events: EventBus → WebSocket Hub
  PKI and mTLS
  Network Ports and Endpoints
  Pod Creation Data Flow

## · Core Concepts  (L663)
  源文件: README.md, backend/internal/api/grpc/runner_adapter_mcp.go, backend/internal/api/grpc/runner_adapter_mcp_ticket.go, backend/internal/service/mesh/service.go, backend/internal/service/ticket/ticket_query.go, backend/internal/service/ticket/ticket_query_test.go, docs/images/architecture.svg, runner/internal/mcp/grpc_client.go, runner/internal/mcp/http_server.go, runner/internal/mcp/http_tools_format_integration_test.go, runner/internal/mcp/http_tools_ticket.go, runner/internal/mcp/tools/types_client.go
  Concept Overview
  Infrastructure Concepts
    · Runner
    · Relay
    · Backend
  Execution Concepts
    · Pod (AgentPod)
    · Sandbox
    · Workspace
  Collaboration Concepts
    · AgentsMesh (the feature)
    · MCP (Model Context Protocol)
    · Binding
    · Channel
  Project Management Concepts
    · Ticket
  Organizational Concepts
    · Organization and Tenant
  Concept Relationships
  Quick Reference

## · Backend  (L1007)
  源文件: .claude/skills/worktree/SKILL.md, CLAUDE.md, backend/cmd/server/eventbus_relay.go, backend/cmd/server/main.go, backend/internal/api/grpc/command_sender_adapter.go, backend/internal/api/grpc/runner_adapter_send.go, backend/internal/api/grpc/runner_adapter_send_extra_test.go, backend/internal/api/rest/internal/relay_registration.go, backend/internal/api/rest/internal/relay_registration_test.go, backend/internal/api/rest/v1/pod_terminal_connect.go, backend/internal/config/config.go, backend/internal/config/config_relay.go
  Role
  Process Entry Point
  Subsystem Map
  Key Structs and Packages
  Infrastructure Dependencies
  Network Ports
  `Services` Container
  gRPC and mTLS Conditional Initialization
  Relay Token Refresh Flow
  Graceful Shutdown
  Configuration Overview

## · REST API Routes  (L1356)
  源文件: backend/cmd/server/eventbus_relay.go, backend/cmd/server/main.go, backend/internal/api/grpc/command_sender_adapter.go, backend/internal/api/grpc/runner_adapter_send.go, backend/internal/api/grpc/runner_adapter_send_extra_test.go, backend/internal/api/rest/router.go, backend/internal/api/rest/v1/pod_terminal_connect.go, backend/internal/api/rest/v1/routes.go, backend/internal/service/runner/command_sender.go, backend/internal/service/runner/command_sender_test.go, backend/internal/service/runner/test_helper_test.go, proto/gen/go/runner/v1/runner.pb.go
  Router Construction
  Route Group Overview
  Route Group Details
    · Health Endpoints
    · Public Routes (`/api/v1`, no auth)
    · Protected Routes (JWT required)
    · Org-Scoped Routes (`/api/v1/orgs/:slug/*`)
    · External API (`/api/v1/ext/orgs/:slug/*`)
    · Admin Console Routes
    · Internal Relay API (`/api/internal/relays/*`)
  Middleware Summary

## · gRPC API and Runner Communication  (L1806)
  源文件: .claude/skills/gh-merge/SKILL.md, backend/cmd/server/eventbus_relay.go, backend/cmd/server/main.go, backend/internal/api/grpc/command_sender_adapter.go, backend/internal/api/grpc/runner_adapter_send.go, backend/internal/api/grpc/runner_adapter_send_extra_test.go, backend/internal/api/grpc/runner_adapter_test.go, backend/internal/api/rest/v1/pod_terminal_connect.go, backend/internal/service/runner/command_sender.go, backend/internal/service/runner/command_sender_test.go, backend/internal/service/runner/connection_manager.go, backend/internal/service/runner/test_helper_test.go
  Protocol Overview
  Protobuf Message Types
    · Runner → Backend (`RunnerMessage`)
    · Backend → Runner (`ServerMessage`)
  Stream Lifecycle
    · Initialization Timeout
  Backend-Side Components
    · `GRPCRunnerAdapter`
    · `GRPCCommandSender`
    · `RunnerCommandSender` interface
  Runner-Side Components
    · `GRPCConnection`
    · `client.Connection` Interface
    · `RunnerMessageHandler`
  Message Dispatch on the Runner
  MCP over gRPC
  Relay Token Refresh Flow
  Fatal Error Handling

## · Runner Connection Manager  (L2183)
  源文件: .claude/skills/gh-merge/SKILL.md, .github/workflows/release.yml, backend/internal/api/grpc/runner_adapter_test.go, backend/internal/service/runner/connection_manager.go, backend/internal/service/runner/version_checker.go, backend/internal/service/runner/version_checker_test.go, docs/rfc/RFC-003-runner-release-pipeline.md, runner/build/scripts/sign-darwin.sh, runner/internal/client/interface.go, runner/internal/relay/client_token_test.go, runner/internal/runner/message_handler.go, runner/internal/runner/message_handler_pod_create_test.go
  Overview
  Sharded Storage Architecture
  GRPCConnection Abstraction
  Connection Lifecycle
  Heartbeat Tracking
  Initialization Timeout
  Event Callbacks
  Integration with GRPCRunnerAdapter
  Manager Construction and Teardown

## · MCP and Mesh Service  (L2444)
  源文件: README.md, backend/internal/api/grpc/runner_adapter_mcp.go, backend/internal/api/grpc/runner_adapter_mcp_ticket.go, backend/internal/service/mesh/service.go, backend/internal/service/ticket/ticket_query.go, backend/internal/service/ticket/ticket_query_test.go, docs/images/architecture.svg, runner/internal/mcp/grpc_client.go, runner/internal/mcp/http_server.go, runner/internal/mcp/http_tools_format_integration_test.go, runner/internal/mcp/http_tools_ticket.go, runner/internal/mcp/tools/types_client.go
  Overview
  Runner-Side MCP Server
    · `HTTPServer`
    · `GRPCCollaborationClient`
  Backend-Side MCP Handler
    · `GRPCRunnerAdapter` — MCP Dispatch
    · Pod Creation via MCP (`mcpCreatePod`)
    · Ticket MCP Handlers
  Registered MCP Tools (Runner Side)
  Mesh Topology Service
  Channel and Binding Management
    · Channels
    · Bindings
  End-to-End Architecture Diagram

## · Ticket Service  (L2947)
  源文件: README.md, backend/internal/api/grpc/runner_adapter_mcp.go, backend/internal/api/grpc/runner_adapter_mcp_ticket.go, backend/internal/service/ticket/ticket_query.go, backend/internal/service/ticket/ticket_query_test.go, docs/images/architecture.svg, runner/internal/mcp/grpc_client.go, runner/internal/mcp/http_server.go, runner/internal/mcp/http_tools_format_integration_test.go, runner/internal/mcp/http_tools_ticket.go, runner/internal/mcp/tools/types_client.go, runner/internal/mcp/tools/types_entity.go
  Data Model
  Backend Service Layer
  REST API Endpoints
    · Key endpoint notes
  Frontend State: `useTicketStore`
  MCP Integration (AI Agent Access)
    · MCP Ticket Methods
    · Content Pagination
    · Runner-side MCP Tools
  Pod Integration
  Ticket Comments
  Labels

## · Billing and Subscriptions  (L3318)
  源文件: backend/internal/api/rest/v1/admin/subscriptions.go, backend/internal/api/rest/v1/invitations.go, backend/internal/api/rest/v1/pods.go, backend/internal/api/rest/v1/repositories.go, backend/internal/domain/organization/organization.go, backend/internal/service/billing/service.go, backend/internal/service/billing/subscription.go, backend/internal/service/organization/interface.go, backend/internal/service/organization/service.go, backend/migrations/000053_fix_missing_subscriptions.down.sql, backend/migrations/000053_fix_missing_subscriptions.up.sql
  Overview
  Domain Model
    · `Subscription` fields
    · `SubscriptionPlan` fields
    · Status constants
  Service Layer
    · Constructors
    · Payment provider abstraction
  Subscription Lifecycle
    · Key service operations
  Organization Integration
  Upgrade and Downgrade Logic
  Organization Synchronization
  Admin REST API
    · `subscriptionResponse` shape
    · All operations are audit-logged
  Custom Quotas
  Data Migration: Missing Subscriptions
  Component Diagram

## · Configuration  (L3698)
  源文件: backend/internal/api/rest/internal/relay_registration.go, backend/internal/api/rest/internal/relay_registration_test.go, backend/internal/config/config.go, backend/internal/config/config_relay.go, backend/internal/service/relay/dns_service.go, backend/internal/service/relay/dns_service_mock_test.go, backend/internal/service/relay/dns_service_sanitize_test.go, backend/migrations/000033_move_preparation_script_to_repository.down.sql, backend/migrations/000033_move_preparation_script_to_repository.up.sql, docs/images/logo.svg, relay/.env.example, relay/internal/config/config.go
  The Unified Domain Pattern
  Backend Configuration
    · `Config` Struct
    · `Load()` Function
    · Backend Environment Variables Reference
    · Relay Management Configuration (Backend-side)
  Relay Service Configuration
    · `Config` Struct (Relay)
    · Relay URL Derivation
    · Relay Environment Variables Reference
  Frontend Configuration
    · Frontend URL Resolution Priority
    · Frontend Environment Variables
  Deployment Scenarios

## · PKI and mTLS  (L4142)
  源文件: backend/cmd/server/grpc_init.go, backend/cmd/server/grpc_init_test.go, backend/internal/infra/pki/service.go, backend/internal/infra/pki/service_server.go, backend/internal/infra/pki/service_test.go, runner/internal/client/grpc_connection_options.go, runner/internal/client/grpc_tls.go
  Overview
  PKI Service (`pki.Service`)
    · Data model
    · Configuration (`pki.Config`)
    · Initialization
  Certificate Issuance
    · Runner certificates
    · Certificate validation
  Server Certificate
    · Default SANs
    · Derived SANs
  PKI Initialization Flow
  mTLS Enforcement on the gRPC Server
  Runner-Side TLS
    · Certificate files
    · Three-tier TLS credential fallback
    · Verification mode: chain-only, no hostname check
    · Certificate hot-reloading
  Certificate Renewal
    · Renewal loop
    · Renewal via REST API
    · Configurable thresholds
  End-to-End Certificate Lifecycle
  Configuration Reference

## · Object Storage  (L4546)
  源文件: backend/internal/infra/storage/s3.go, ci/build-onpremise.sh, ci/pack-onpremise.sh, deploy/dev/runner-ssh/README.md, deploy/onpremise/README.md, deploy/onpremise/docker-compose.yml, deploy/onpremise/scripts/generate-certs.sh, deploy/onpremise/scripts/install.sh, deploy/onpremise/scripts/load-images.sh, deploy/onpremise/seed/onpremise-seed.sql, e2e/README.md
  Overview
  Data Structures
    · `S3Config`
    · `S3Storage`
  Construction
  Operations
    · Upload
    · Delete
    · Exists
    · EnsureBucket
  URL Generation
    · `GetURL` — Public URL
    · `GetInternalURL` — Service-to-Service URL
  Configuration via Environment Variables
  MinIO Integration
  Code Entity Map

## · Real-time Events and WebSocket  (L4848)
  源文件: backend/cmd/server/eventbus_relay.go, backend/cmd/server/eventbus_setup.go, backend/cmd/server/main.go, backend/internal/api/grpc/command_sender_adapter.go, backend/internal/api/grpc/runner_adapter_send.go, backend/internal/api/grpc/runner_adapter_send_extra_test.go, backend/internal/api/rest/v1/pod_terminal_connect.go, backend/internal/service/runner/command_sender.go, backend/internal/service/runner/command_sender_test.go, backend/internal/service/runner/test_helper_test.go, proto/gen/go/runner/v1/runner.pb.go, proto/runner/v1/runner.proto
  Overview
  Backend Event Pipeline
    · Initialization Sequence
    · EventBus
    · WebSocket Hub
    · Redis Multi-Instance Sync
    · Event Publishers by Service
  Frontend Real-time Infrastructure
    · Connection Layer
    · RealtimeProvider
    · Event Routing in handleEvent
    · Reconnection Behavior
    · Loop Event Debouncing
    · Staleness Protection in usePodStore
    · Code Entity Map

## · Runner  (L5239)
  源文件: runner/.goreleaser.yml, runner/README.md, runner/cmd/runner/cmd_reactivate.go, runner/cmd/runner/cmd_register.go, runner/cmd/runner/cmd_run.go, runner/cmd/runner/main.go, runner/cmd/runner/register.go, runner/cmd/runner/service.go, runner/cmd/runner/update.go, runner/cmd/runner/webconsole.go, runner/internal/client/grpc_connection.go, runner/internal/config/config.go
  Purpose
  System Context
  Repository Layout
  CLI Commands
  Configuration
  Core `Runner` Struct
  Startup Sequence
  Registration Flow
  gRPC Connection
  Web Console
  System Service
  Certificate Lifecycle
  Self-Update
  Distribution

## · Installation and Registration  (L5652)
  源文件: runner/.goreleaser.yml, runner/README.md, runner/cmd/runner/cmd_reactivate.go, runner/cmd/runner/cmd_register.go, runner/cmd/runner/cmd_run.go, runner/cmd/runner/main.go, runner/cmd/runner/register.go, runner/cmd/runner/service.go, runner/cmd/runner/update.go, runner/cmd/runner/webconsole.go, runner/internal/client/grpc_connection.go, runner/internal/config/config.go
  Installation
    · Installation methods
    · install.sh (macOS and Linux)
    · install.ps1 (Windows)
    · Homebrew
  Registration
    · Token-based registration
    · Interactive (login) registration
    · Overwriting an existing registration
  Files Written by Registration
    · `~/.agentsmesh/config.yaml`
    · `~/.agentsmesh/certs/`
  Configuration Loading
    · Environment variable overrides
  Starting the Runner
    · System service
  Certificate Reactivation

## · CLI Reference  (L5980)
  源文件: runner/.goreleaser.yml, runner/README.md, runner/cmd/runner/cmd_reactivate.go, runner/cmd/runner/cmd_register.go, runner/cmd/runner/cmd_run.go, runner/cmd/runner/main.go, runner/cmd/runner/register.go, runner/cmd/runner/service.go, runner/cmd/runner/update.go, runner/cmd/runner/webconsole.go, runner/internal/client/grpc_connection.go, runner/internal/config/config.go
  Binary Overview
  `register` (alias: `login`)
    · Flags
    · Registration Flows
    · Files Written After Registration
  `run` (alias: `start`)
    · Flags
    · Startup Sequence
    · Config File Resolution
  `service`
    · Usage
    · Actions
    · `service install` Flags
  `webconsole` (alias: `console`)
    · Flags
    · Browser Launch
  `reactivate`
    · Flags
    · Flow
  `update`
    · Flags
    · Update Flow
  `update-endpoint`
  `version`
  Command-to-File Map

## · gRPC Client  (L6349)
  源文件: backend/cmd/server/grpc_init.go, backend/cmd/server/grpc_init_test.go, backend/internal/infra/pki/service.go, backend/internal/infra/pki/service_server.go, backend/internal/infra/pki/service_test.go, runner/cmd/runner/cmd_reactivate.go, runner/cmd/runner/cmd_register.go, runner/cmd/runner/cmd_run.go, runner/cmd/runner/main.go, runner/cmd/runner/register.go, runner/cmd/runner/service.go, runner/cmd/runner/update.go
  Overview
  Component Map
  GRPCConnection Struct
  Connection Lifecycle
    · Initialization
    · Start / Stop
    · Connection loop (connectionLoop / runConnection)
  mTLS and Certificate Hot-Reload
  Message Priority and Write Loop
  Heartbeat
  Certificate Renewal
  Fatal Error Handling
  Functional Options
  Endpoint Parsing
  Suture Integration

## · Pod and Terminal Management  (L6665)
  源文件: .claude/skills/gh-merge/SKILL.md, backend/internal/api/grpc/runner_adapter_test.go, backend/internal/service/runner/connection_manager.go, runner/go.mod, runner/go.sum, runner/internal/client/interface.go, runner/internal/relay/client_token_test.go, runner/internal/runner/message_handler.go, runner/internal/runner/message_handler_pod_create_test.go, runner/internal/runner/pod.go, runner/internal/terminal/terminal.go, runner/internal/terminal/terminal_io.go
  The Pod Struct
  Pod Lifecycle
  PodStore
  The Terminal Abstraction
  Platform-Specific PTY Implementations
    · Unix — `unixPTY`
    · Windows — `windowsPTY`
  PTY Lifecycle: Start, Stop, Resize
    · Start
    · Stop
    · Resize
  Output Backpressure
    · PTY Error Handling
  Message Handler Integration
    · Agent State Bridging
  Environment Setup in `New()`
  Relationship Between Components

## · Relay Client  (L7050)
  源文件: docs/troubleshooting/relay-client-stop-timeout.md, runner/internal/relay/client.go, runner/internal/relay/client_connection.go, runner/internal/relay/client_loops.go, runner/internal/relay/client_reconnect.go, runner/internal/relay/client_test.go, runner/internal/relay/interface.go, runner/internal/relay/mock_client.go, runner/internal/runner/message_handler_relay_test.go
  Purpose
  Package Layout
  RelayClient Interface
  Client Struct
    · Constants
  Connection Lifecycle
    · `NewClient`
    · `Connect`
    · `Start`
    · `Stop`
  Read and Write Loops
    · `readLoop`
    · `writeLoop`
  Message Handling
    · Image Paste Payload Format
  Reconnection Logic
    · Backoff Parameters
    · Token Refresh
  Shutdown Race Condition Fix
  Multi-Client (Shared Relay) Behaviour
  MockClient

## · MCP Server  (L7413)
  源文件: README.md, backend/internal/api/grpc/runner_adapter_mcp.go, backend/internal/api/grpc/runner_adapter_mcp_ticket.go, backend/internal/service/ticket/ticket_query.go, backend/internal/service/ticket/ticket_query_test.go, docs/images/architecture.svg, runner/internal/mcp/grpc_client.go, runner/internal/mcp/http_server.go, runner/internal/mcp/http_tools_format_integration_test.go, runner/internal/mcp/http_tools_ticket.go, runner/internal/mcp/tools/types_client.go, runner/internal/mcp/tools/types_entity.go
  Overview
  HTTP Server
  Pod Registration
  MCP Configuration for Claude Code
  Request Flow
  Tool Architecture
  Registered Tools
    · Terminal Tools
    · Discovery Tools
    · Binding Tools
    · Channel Tools
    · Ticket Tools
    · Pod Tools
  GRPCCollaborationClient
  Backend-Side Dispatch
  Local Providers
    · PodStatusProvider
    · LocalTerminalProvider
  Tool Response Format

## · Workspace and Git Management  (L7792)
  源文件: .gitlab-ci.yml, ci/backend.Dockerfile, ci/relay.Dockerfile, ci/runner.Dockerfile, ci/web-admin.Dockerfile, ci/web.Dockerfile, runner/internal/workspace/repo_auth.go, runner/internal/workspace/workspace.go, runner/internal/workspace/workspace_utils.go, web/src/lib/terminalScheduler.ts, web/vitest.config.ts
  Overview
  Core Types
  Module Structure
  Repository Lifecycle
    · `ensureRepository` and `ensureRepositoryWithAuth`
    · `cloneBareRepository`
  Authentication
    · Token-based HTTPS
    · SSH Key
    · Probe-specific environment
  Repository Access Probing
  Custom Git Configuration
  Utility Functions
  Data Flow: Pod Workspace Setup
  `NewManager` Initialization

## · Auto-Update  (L8090)
  源文件: .github/workflows/release.yml, backend/internal/service/runner/version_checker.go, backend/internal/service/runner/version_checker_test.go, docs/rfc/RFC-003-runner-release-pipeline.md, runner/build/scripts/sign-darwin.sh, runner/internal/updater/updater.go, runner/internal/updater/updater_test.go
  System Overview
  Runner-Side: `updater` Package
    · Key Types
    · `Updater` Construction
    · Update Operation Flow
    · `Apply` and Atomic Replacement
    · Backup and Rollback
    · Prerelease Filtering
  Backend-Side: `VersionChecker`
    · Construction and Lifecycle
    · Redis Caching
    · GitHub API Request
    · `NormalizeVersion`
  Version String Conventions
  Interaction with the Release Pipeline

## · Relay  (L8352)
  源文件: relay/internal/backend/client.go, relay/internal/backend/client_test.go, relay/internal/channel/channel_manager_test.go, relay/internal/channel/helpers_test.go, relay/internal/channel/terminal_channel.go, relay/internal/channel/terminal_channel_test.go, relay/internal/server/handler_test.go, relay/internal/server/server.go, relay/internal/server/server_test.go
  Purpose
  High-Level Data Flow
  Service Structure
    · Key Types
  HTTP Endpoints
  Publisher / Subscriber Model
    · Input Control
    · Output Buffering
  Message Forwarding
  Configuration
    · TLS
  Startup and Shutdown Sequence
  Backend Communication
    · Auto-IP Detection

## · Channel and Session Management  (L8617)
  源文件: relay/internal/backend/client.go, relay/internal/backend/client_test.go, relay/internal/channel/channel_manager_test.go, relay/internal/channel/helpers_test.go, relay/internal/channel/terminal_channel.go, relay/internal/channel/terminal_channel_test.go, relay/internal/server/handler_test.go, relay/internal/server/server.go, relay/internal/server/server_test.go
  Purpose
  Core Types
    · `TerminalChannel`
    · `Subscriber`
    · `ChannelConfig`
  Data Flow
  Message Types
  Publisher Lifecycle
  Subscriber Lifecycle
  Broadcast and Write Safety
  Input Control
  Output Buffer
  ChannelManager
    · Pending Connection Matching
    · `MaxSubscribersError`
    · `ChannelStats`
  Channel Closed Lifecycle
  HTTP Endpoints and Handler Integration
  Graceful Shutdown

## · Backend Registration and Heartbeat  (L9007)
  源文件: backend/internal/api/rest/internal/relay_registration.go, backend/internal/api/rest/internal/relay_registration_test.go, backend/internal/config/config.go, backend/internal/config/config_relay.go, backend/internal/service/relay/dns_service.go, backend/internal/service/relay/dns_service_mock_test.go, backend/internal/service/relay/dns_service_sanitize_test.go, backend/migrations/000033_move_preparation_script_to_repository.down.sql, backend/migrations/000033_move_preparation_script_to_repository.up.sql, docs/images/logo.svg, relay/.env.example, relay/internal/backend/client.go
  Purpose and Scope
  Overview
  Client Construction
  Registration
    · Retry Logic
  Backend-Side Registration Handler
  Heartbeat
    · SendHeartbeat
    · StartHeartbeat Loop
  TLS Certificate Management
  Session Close Notification
  Graceful Unregistration
  Configuration Reference

## · Web Frontend  (L9362)
  源文件: .claude/skills/worktree/SKILL.md, CLAUDE.md, deploy/dev/.gitignore, deploy/dev/backend.Dockerfile, deploy/dev/docker-compose.yml, deploy/dev/init-seed.sh, deploy/dev/nginx/conf.d/default.conf, deploy/dev/nginx/nginx.conf, deploy/dev/runner-entrypoint.sh, deploy/dev/runner.Dockerfile, deploy/dev/seed/seed.sql, deploy/dev/traefik/dynamic/grpc.yml
  Purpose and Scope
  Tech Stack
  Application Structure
  Component and System Map
  API Communication Layer
  State Management
  Theming
  Key Shared UI Components
    · `Markdown`
    · `BlockEditor` / `BlockViewer`
    · Mobile Layout
  Providers
  Main User Flows
  Development

## · Terminal Workspace  (L9730)
  源文件: web/src/components/ide/CreatePodModal.tsx, web/src/components/ide/IDEShell.tsx, web/src/components/ide/SideBar.tsx, web/src/components/ide/sidebar/MeshSidebarContent.tsx, web/src/components/ide/sidebar/RunnersSidebarContent.tsx, web/src/components/mobile/MobileHeader.tsx, web/src/components/mobile/MobileSidebar.tsx, web/src/components/settings/organization/RunnersSettings.tsx, web/src/components/tickets/TicketPodPanel.tsx, web/src/components/workspace/TerminalPane.tsx, web/src/components/workspace/TerminalSwiper.tsx, web/src/components/workspace/TerminalTabs.tsx
  Overview
  TerminalConnectionPool
    · Connection Pooling Model
    · Binary Protocol (MsgType)
    · subscribe() and Connection Lifecycle
    · Reconnection
    · Input Deduplication
    · Resize Debouncing
    · Status Change Events
  useTerminal Hook
    · Signature
    · Initialization sequence
    · Key design decisions
    · Terminal Theme
  TerminalPane Component
    · Props
    · Render logic
  useWorkspaceStore
    · State shape
    · Key actions
    · TerminalRegistry
  Workspace Layout
    · Layout selection diagram
    · Desktop: TerminalTabs
    · Mobile: TerminalSwiper
    · Mobile: TerminalToolbar
  Component Dependency Map
  Workspace Page
  Opening a Terminal from Other Views

## · Ticket Management  (L10131)
  源文件: web/src/components/billing/CancelSubscriptionDialog.tsx, web/src/components/settings/organization/__tests__/APIKeysSettings.test.tsx, web/src/components/tickets/KanbanBoard.tsx, web/src/components/tickets/TicketCreateDialog.tsx, web/src/components/tickets/TicketDetail.tsx, web/src/components/tickets/TicketDetailPane.tsx, web/src/components/tickets/TicketDetailSidebar.tsx, web/src/components/tickets/__tests__/TicketCard.test.tsx, web/src/components/tickets/__tests__/TicketCreateDialog.test.tsx, web/src/components/tickets/__tests__/TicketDetail.test.tsx, web/src/components/tickets/index.ts, web/src/components/ui/__tests__/responsive-dialog.test.tsx
  Data Model
  `useTicketStore` — Zustand Store
  `ticketApi` — REST API Client
  `TicketsPage` — Route Entry Point
  Views
    · List View
    · Board View — `KanbanBoard`
  `TicketDetail` — Full Page Detail View
  `TicketDetailSidebar` — Properties and Pod Panel
    · `SidebarPodSection`
    · Properties Panel
  `TicketDetailPane` — Inline Side Panel
  `TicketCreateDialog` — Creation Form
  Keyboard Navigation — `TicketKeyboardHandler`
  `useTicketExtraData` Hook
  Component Map

## · AgentsMesh Network View  (L10611)
  源文件: backend/internal/service/mesh/service.go, web/src/components/ide/CreatePodModal.tsx, web/src/components/ide/IDEShell.tsx, web/src/components/ide/SideBar.tsx, web/src/components/ide/sidebar/MeshSidebarContent.tsx, web/src/components/ide/sidebar/RunnersSidebarContent.tsx, web/src/components/settings/organization/RunnersSettings.tsx, web/src/components/tickets/TicketPodPanel.tsx, web/src/components/workspace/TerminalTabs.tsx, web/src/components/workspace/WorkspaceManager.tsx, web/src/lib/api/pod.ts, web/src/messages/de/app.json
  IDEShell
    · Activity Types and Sidebar Dispatch
    · Global Modals
    · SideBar Resize
  MeshPage
    · Header Statistics
    · Chat Panel Behavior
    · Legend
  Mesh Sidebar
    · Filtering Logic
    · Node and Channel Interaction
  Topology Data Model
    · Backend Assembly Steps
  useMeshStore
  CreatePodModal
    · Props
    · Ticket Context Behavior
  WorkspaceManager and TerminalTabs
    · TerminalTabs
  TicketPodPanel
  Cross-Component Data Flow

## · Channels and Chat  (L11029)
  源文件: web/src/components/ide/BottomPanel.tsx, web/src/components/ide/BottomPanel/ChannelDetailView.tsx, web/src/components/ide/BottomPanel/types.ts, web/src/components/mesh/ChannelChatPanel.tsx, web/src/components/mesh/ChannelHeader.tsx, web/src/components/mesh/ChannelPodManager.tsx, web/src/components/mesh/MobileChannelChat.tsx, web/src/lib/api/channel.ts
  Overview
  BottomPanel and the Channels Tab
  Component Hierarchy
  ChannelChatPanel
  MobileChannelChat
  Message Sending with Pod Mentions
  ChannelPodManager
  ChannelHeader
  ChannelDocument
  channelApi
  BottomPanel/types.ts — Shared Type Contracts
  Data Flow Summary

## · Real-time State Management  (L11349)
  源文件: backend/cmd/server/eventbus_setup.go, web/src/components/ide/sidebar/WorkspaceSidebarContent.tsx, web/src/components/pwa/PushNotificationManager.tsx, web/src/hooks/usePodStatus.ts, web/src/providers/RealtimeProvider.tsx, web/src/stores/__tests__/pod.test.ts, web/src/stores/__tests__/terminalConnection.test.ts, web/src/stores/__tests__/workspace.test.ts, web/src/stores/channel.ts, web/src/stores/pod.ts, web/src/stores/runner.ts
  Architecture Overview
  RealtimeProvider
    · Key design: `getState()` instead of reactive store subscriptions
    · Event Routing Table
    · Reconnection Recovery
  Pod Store (`usePodStore`)
    · State Shape
    · `SIDEBAR_STATUS_MAP`
    · `upsertPod` — Unified Write Path
    · In-flight Request Deduplication
    · Merge Strategy During API Fetches
    · Store Actions
  Runner Store (`useRunnerStore`)
    · State Shape
  Channel Store (`useChannelStore`)
    · State Shape
    · Real-time Integration
  Workspace Store (`useWorkspaceStore`)
    · State Shape
    · Key Actions
  Store Relationship Diagram
  `usePodStatus` Hook
  Loop Run Event Debouncing

## · Environment and API Configuration  (L11775)
  源文件: web-admin/next.config.ts, web-admin/src/lib/api/base.ts, web/next.config.ts, web/src/lib/env.ts
  Overview
  URL Resolution Hierarchy
  Environment Variables Reference
  Placeholder Substitution Mechanism
  Exported URL Functions
    · `getApiBaseUrl()`
    · `getWsBaseUrl()`
    · `getOAuthBaseUrl()`
    · `getServerUrl()` and `getServerUrlSSR()`
  Deployment Scenarios
  Next.js Rewrite Proxy (Local Development)
  `ApiClient` (web-admin)
  Function-to-Deployment-Scenario Matrix

## · Web Admin  (L12025)
  源文件: backend/internal/api/rest/v1/admin/subscriptions.go, backend/internal/api/rest/v1/invitations.go, backend/internal/api/rest/v1/pods.go, backend/internal/api/rest/v1/repositories.go, backend/internal/domain/organization/organization.go, backend/internal/service/billing/service.go, backend/internal/service/billing/subscription.go, backend/internal/service/organization/interface.go, backend/internal/service/organization/service.go, backend/migrations/000053_fix_missing_subscriptions.down.sql, backend/migrations/000053_fix_missing_subscriptions.up.sql, web-admin/next.config.ts
  Application Structure
  API Client
    · URL Resolution
    · Authentication
    · Available Methods
  Environment and Domain Configuration
  Subscription Management UI
    · Component Decomposition
    · Sub-panels
  Backend Admin API
    · Key Backend Behaviours
    · Subscription Response Shape
  Relationship to Backend Billing Service

## · Development Environment  (L12278)
  源文件: .claude/skills/worktree/SKILL.md, CLAUDE.md, deploy/dev/.gitignore, deploy/dev/backend.Dockerfile, deploy/dev/dev.sh, deploy/dev/docker-compose.yml, deploy/dev/gitea/init-gitea.sh, deploy/dev/init-seed.sh, deploy/dev/nginx/conf.d/default.conf, deploy/dev/nginx/nginx.conf, deploy/dev/runner-entrypoint.sh, deploy/dev/runner-ssh/id_ed25519.pub
  Overview
  Prerequisites
  Quick Start
  Initialization Flow
    · Step Details
  Docker Service Architecture
  Seed Data
  Hot Reload
  Common Workflows
    · Viewing Logs
    · Running Database Migrations
    · Using a Local Runner Binary
    · Working with Multiple Worktrees
    · Full Teardown
  Environment Variables Reference

## · Docker Compose Services  (L12699)
  源文件: .claude/skills/worktree/SKILL.md, CLAUDE.md, deploy/dev/.gitignore, deploy/dev/backend.Dockerfile, deploy/dev/dev.sh, deploy/dev/docker-compose.yml, deploy/dev/gitea/init-gitea.sh, deploy/dev/init-seed.sh, deploy/dev/nginx/conf.d/default.conf, deploy/dev/nginx/nginx.conf, deploy/dev/runner-entrypoint.sh, deploy/dev/runner-ssh/id_ed25519.pub
  Service Map
  Services
    · postgres
    · redis
    · minio
    · gitea
    · adminer
    · backend
    · runner
    · relay
    · traefik
  Volumes
  Port Allocation
  Hot Reload

## · Local Runner and Gitea Setup  (L13165)
  源文件: deploy/dev/dev.sh, deploy/dev/gitea/init-gitea.sh, deploy/dev/runner-ssh/id_ed25519.pub, relay/.air.toml, runner/.gitignore, runner/.goreleaser.yml, runner/README.md, runner/internal/config/config.go, runner/internal/config/config_defaults_test.go, runner/internal/config/config_grpc_test.go, runner/internal/envpath/envpath_test.go, web/public/install.ps1
  Local Runner Binary Build
    · Build Mechanics
  Port Allocation by Worktree
    · Algorithm
  Gitea Initialization
    · Initialization Steps
    · Admin Credentials
    · Deploy Key Registration
  Runner SSH Key and Host Configuration
    · Generating the SSH Keypair
    · SSH Config for Host-Side Runners
  Registering and Running a Local Runner
  Resetting Runners
  Full dev.sh Initialization Sequence

## · Deployment  (L13435)
  源文件: .gitlab-ci.yml, backend/internal/infra/storage/s3.go, ci/backend.Dockerfile, ci/build-onpremise.sh, ci/pack-onpremise.sh, ci/relay.Dockerfile, ci/runner.Dockerfile, ci/web-admin.Dockerfile, ci/web.Dockerfile, deploy/dev/runner-ssh/README.md, deploy/onpremise/README.md, deploy/onpremise/docker-compose.yml
  Deployment Models
  Service Components and Build Artifacts
  Build Pipeline Overview
  SaaS Production Environments
  Runner Binary Distribution
  On-Premise Deployment
  Air-Gapped Packaging

## · CI/CD Pipeline  (L13693)
  源文件: .gitlab-ci.yml, ci/backend.Dockerfile, ci/relay.Dockerfile, ci/runner.Dockerfile, ci/web-admin.Dockerfile, ci/web.Dockerfile, runner/internal/workspace/repo_auth.go, runner/internal/workspace/workspace.go, runner/internal/workspace/workspace_utils.go, web/src/lib/terminalScheduler.ts, web/vitest.config.ts
  Overview
  Global Variables
  Pipeline Trigger Rules
  Test Stage
    · Unit Test Jobs
    · Build Verification Jobs
  Build Stage
  Dockerfiles
    · `ci/backend.Dockerfile`
    · `ci/web.Dockerfile`
    · `ci/web-admin.Dockerfile`
    · `ci/runner.Dockerfile`
    · `ci/relay.Dockerfile`
  Deploy Stage
    · Production Environments
    · Relay Nodes
    · Deploy Script Invocation
  Database Migrations
  Full Pipeline Flow

## · Release Process  (L14066)
  源文件: .github/workflows/release.yml, .gitlab-ci.yml, backend/internal/service/runner/version_checker.go, backend/internal/service/runner/version_checker_test.go, ci/backend.Dockerfile, ci/relay.Dockerfile, ci/runner.Dockerfile, ci/web-admin.Dockerfile, ci/web.Dockerfile, docs/rfc/RFC-003-runner-release-pipeline.md, runner/.goreleaser.yml, runner/README.md
  Overview
  Pipeline Trigger and Job Structure
  Docker Image Builds
    · Service Matrix
    · Image Tags
    · Dockerfile Internals
  Runner Binary Release (GoReleaser)
    · Build Configuration
    · Release Artifacts
    · Linux Package Contents
  macOS Code Signing
    · Signing Script
    · Required GitHub Secrets
  Homebrew Tap Update
  Release Changelog
  Post-Release: Version Distribution
    · Backend `VersionChecker`
    · Runner `Updater`
  Installation Scripts
  Creating a Release

## · On-Premise Deployment  (L14455)
  源文件: backend/internal/api/rest/internal/relay_registration.go, backend/internal/api/rest/internal/relay_registration_test.go, backend/internal/config/config.go, backend/internal/config/config_relay.go, backend/internal/infra/storage/s3.go, backend/internal/service/relay/dns_service.go, backend/internal/service/relay/dns_service_mock_test.go, backend/internal/service/relay/dns_service_sanitize_test.go, backend/migrations/000033_move_preparation_script_to_repository.down.sql, backend/migrations/000033_move_preparation_script_to_repository.up.sql, ci/build-onpremise.sh, ci/pack-onpremise.sh
  Overview
  Service Topology
  Prerequisites
  Deployment Package Structure
  Installation
    · Option 1: install.sh (Recommended)
    · Option 2: Manual Installation
  Environment Configuration
    · IP-Based Access (No Domain Required)
  SSL Certificate Generation
  Docker Services
    · MinIO (Object Storage)
  Seed Data
  Access URLs
  Runner Registration
  Air-Gapped Deployment
  Common Operations
  Data Backup and Restore
    · Database
    · Full Volume Backup
  Version Upgrades
  Troubleshooting
    · Services fail to start
    · Database connection failures
    · Runner cannot connect
  Security Notes