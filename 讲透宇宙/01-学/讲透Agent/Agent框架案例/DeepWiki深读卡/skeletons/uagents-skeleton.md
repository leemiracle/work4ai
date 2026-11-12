# Skeleton: uagents（34 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | uAgents Overview | L6 | 7KB | 2 | ~1 | 9 |
| 2 | Installation and Setup | L187 | 6KB | 2 | ~3 | 8 |
| 3 | Key Concepts | L387 | 13KB | 6 | ~4 | 9 |
| 4 | Core Components | L697 | 9KB | 5 | ~1 | 9 |
| 5 | Agent Class | L983 | 10KB | 4 | ~5 | 4 |
| 6 | Context System | L1273 | 27KB | 9 | ~7 | 4 |
| 7 | Protocol System | L1858 | 12KB | 11 | ~5 | 11 |
| 8 | Storage System | L2209 | 13KB | 6 | ~11 | 9 |
| 9 | Communication | L2555 | 9KB | 5 | ~0 | 9 |
| 10 | Message Envelopes | L2828 | 10KB | 7 | ~6 | 10 |
| 11 | ASGI Server | L3136 | 8KB | 4 | ~2 | 5 |
| 12 | Mailbox Client | L3335 | 9KB | 4 | ~2 | 5 |
| 13 | Dispenser and Dispatcher | L3531 | 9KB | 5 | ~3 | 5 |
| 14 | Address Resolution | L3739 | 8KB | 4 | ~6 | 6 |
| 15 | Agent Registration | L3953 | 9KB | 3 | ~2 | 9 |
| 16 | Almanac Contract | L4172 | 9KB | 3 | ~6 | 6 |
| 17 | Registration Policies | L4397 | 11KB | 4 | ~2 | 9 |
| 18 | Advanced Features | L4629 | 7KB | 2 | ~2 | 5 |
| 19 | Dialogues | L4790 | 7KB | 3 | ~0 | 6 |
| 20 | Quota Protocol | L4969 | 7KB | 3 | ~0 | 2 |
| 21 | Wallet Messaging | L5175 | 5KB | 3 | ~4 | 4 |
| 22 | Security Features | L5303 | 7KB | 3 | ~1 | 11 |
| 23 | Experimental Search and Mobility | L5451 | 7KB | 2 | ~2 | 10 |
| 24 | AI Integration | L5597 | 10KB | 6 | ~1 | 3 |
| 25 | LangChain Integration | L5926 | 11KB | 6 | ~4 | 7 |
| 26 | CrewAI Integration | L6218 | 10KB | 4 | ~5 | 5 |
| 27 | A2A Protocol Bridge | L6505 | 11KB | 4 | ~4 | 11 |
| 28 | AI Engine | L6783 | 10KB | 6 | ~2 | 7 |
| 29 | Chat Agent and MCP Adapter | L7000 | 9KB | 2 | ~1 | 18 |
| 30 | Development | L7149 | 5KB | 5 | ~0 | 13 |
| 31 | Contributing Guide | L7299 | 11KB | 3 | ~6 | 11 |
| 32 | Release Process | L7598 | 7KB | 2 | ~5 | 6 |
| 33 | Deployment | L7747 | 6KB | 2 | ~2 | 8 |
| 34 | Glossary | L7875 | 8KB | 2 | ~2 | 25 |


## · uAgents Overview  (L6)
  源文件: CONTRIBUTING.md, DEVELOPING.md, LICENSE, README.md, python/pyproject.toml, python/uagents-core/README.md, python/uagents-core/poetry.lock, python/uagents-core/pyproject.toml, python/uv.lock
  Purpose and Scope
  Framework Overview
  Package Relationships
  Core Components
    · Agent Class
    · Identity and Addressing
    · Protocol System
    · Context System
  Agent Communication
    · Message Envelopes
  Agent Registration and Discovery
  Storage and Persistence
  Security Features
  Summary

## · Installation and Setup  (L187)
  源文件: CONTRIBUTING.md, DEVELOPING.md, LICENSE, README.md, python/.pre-commit-config.yaml, python/pyproject.toml, python/src/uagents/setup.py, python/uv.lock
  System Requirements
  Installation Methods
    · Using pip
    · Optional Dependencies
  Development Environment Setup
    · 1. Clone the Repository
    · 2. Initialize with uv
    · 3. Install Pre-commit Hooks
    · 4. Running Tests
  Code Entity Space: Installation & Tooling
  Basic Configuration & Verification
    · Creating your first Agent
    · Identity and Keys
    · Automated Funding (Testnet)
  Development Guidelines
    · Linting and Formatting
    · Commit Convention
  Troubleshooting

## · Key Concepts  (L387)
  源文件: CONTRIBUTING.md, DEVELOPING.md, LICENSE, README.md, python/docs/api/uagents/agent.md, python/src/uagents/agent.py, python/uagents-core/README.md, python/uagents-core/poetry.lock, python/uagents-core/pyproject.toml
  Agents
    · Agent Identity and Lifecycle
    · Agent Configuration
  Protocols
    · Protocol Structure
    · Message and Interval Handlers
  Contexts
    · Context Hierarchy
    · Context Operations
  Communication
    · Message Flow Architecture
    · Envelope Structure
  Registration and Discovery
    · Registration Architecture
  Storage
  Identity and Security
    · Identity Management

## · Core Components  (L697)
  源文件: python/docs/api/uagents/agent.md, python/docs/api/uagents/context.md, python/docs/api/uagents/protocol.md, python/src/uagents/agent.py, python/src/uagents/context.py, python/src/uagents/protocol.py, python/tests/test_context.py, python/tests/test_model.py, python/tests/test_protocol.py
  Architecture Overview
  Agent Runtime System
  Context System
  Protocol System
  Communication Infrastructure
  Storage System
  Component Integration

## · Agent Class  (L983)
  源文件: python/docs/api/uagents/agent.md, python/src/uagents/agent.py, python/tests/test_agent.py, python/tests/test_bureau.py
  Class Overview
    · Agent Class Structure
  Agent Identity and Authentication
  Agent Initialization
    · Key Constructor Parameters
  Core Components
    · Storage
    · Communication
  Message Handling
  Registration System
  Bureau: Multi-Agent Container
  Agent Inspector
  Lifecycle Management

## · Context System  (L1273)
  源文件: python/docs/api/uagents/context.md, python/src/uagents/context.py, python/src/uagents/utils.py, python/tests/test_context.py
  Context Hierarchy
    · Context Types
  Context Lifecycle and Creation
    · Context Creation
  Message Handling Through Context
    · Key Message Handling Methods
  Message Resolution and Delivery
    · Resolution Process
  Context Properties and Agent Representation
    · Agent Representation
  Session Management and Message History
    · Sessions
    · Message History
  Differences Between Internal and External Contexts
    · Internal Context
    · External Context
  Integration with Other Framework Components
    · Key Integrations
  Context Usage in Agent Handlers
    · Context Usage Patterns
  Advanced Context Features
    · Advanced Context Features
  Summary

## · Protocol System  (L1858)
  源文件: python/docs/api/uagents/protocol.md, python/src/uagents/protocol.py, python/tests/test_model.py, python/tests/test_protocol.py, python/tests/test_protocol_spec.py, python/uagents-core/uagents_core/contrib/protocols/subscriptions/__init__.py, python/uagents-core/uagents_core/envelope.py, python/uagents-core/uagents_core/logger.py, python/uagents-core/uagents_core/models.py, python/uagents-core/uagents_core/protocol.py, python/uagents-core/uagents_core/utils/__init__.py
  Protocol Architecture
  Protocol Class
    · Core Properties
    · Protocol Initialization
  Message Handler Registration
    · Message Handler Decorators
    · Message Handler Flow
  ProtocolSpecification
    · Specification Structure
    · Interaction Mapping
  Protocol Manifest System
    · Manifest Generation
    · Digest Computation
  Protocol Roles
    · Role-Based Protocol Implementation
  Protocol Verification
    · Handler Validation
  Integration Examples
    · Subscription Protocol Specification
    · Protocol Registration with Agent

## · Storage System  (L2209)
  源文件: python/docs/api/uagents/storage/__init__.md, python/src/uagents/experimental/dialogues/__init__.py, python/src/uagents/storage/__init__.py, python/tests/test_agent_registration.py, python/tests/test_storage.py, python/uagents-core/uagents_core/config.py, python/uagents-core/uagents_core/contrib/protocols/chat/__init__.py, python/uagents-core/uagents_core/storage.py, python/uagents-core/uagents_core/utils/subscriptions.py
  Storage Architecture
    · Local Storage Architecture
    · Storage Method Details
  Agent Storage Integration
    · Agent Storage Initialization
    · Storage Property Access
  Storage System Components
    · Component Integration Architecture
    · Storage Usage by Component
  Message History Storage
    · Storage Key Patterns
  Dialogue Storage
    · Dialogue Storage Architecture
    · Dialogue Session Management
  Private Key Storage
    · Private Key Management Functions
    · Function Signatures and Usage
  External Storage Integration
    · ExternalStorage Usage
    · External Storage Methods
    · Authentication and Attestation
  Summary

## · Communication  (L2555)
  源文件: python/docs/api/uagents/communication.md, python/docs/api/uagents/dispatch.md, python/docs/api/uagents/registration.md, python/src/uagents/asgi.py, python/src/uagents/communication.py, python/src/uagents/dispatch.py, python/src/uagents/query.py, python/tests/test_rest.py, python/tests/test_server.py
  Communication System Overview
    · Communication Architecture
    · Context Class Hierarchy
  Message Envelopes
  Message Flow Patterns
    · Asynchronous Messaging
    · Synchronous Messaging
  Message Sending Components
    · Dispenser
    · Resolver System
  Message Receiving Components
    · ASGI Server
    · Dispatcher
  Mailbox Communication
  Standalone Message Functions
  REST API Communication

## · Message Envelopes  (L2828)
  源文件: python/tests/test_msg_verify.py, python/uagents-core/uagents_core/contrib/protocols/subscriptions/__init__.py, python/uagents-core/uagents_core/envelope.py, python/uagents-core/uagents_core/logger.py, python/uagents-core/uagents_core/models.py, python/uagents-core/uagents_core/protocol.py, python/uagents-core/uagents_core/types.py, python/uagents-core/uagents_core/utils/__init__.py, python/uagents-core/uagents_core/utils/messages.py, python/uagents-core/uagents_core/utils/resolver.py
  Envelope Class Structure
    · Core Envelope Fields
  Envelope Payload Operations
  Envelope Generation Utilities
  Message Sending with Envelopes
    · Core Message Sending Function
    · HTTP Message Transport
  Endpoint Resolution and Delivery
    · Address Resolution Flow
    · Delivery Status Tracking
  Protocol Integration
    · Protocol Digest Computation
    · Model Digest Computation
  Integration with Other uAgents Components

## · ASGI Server  (L3136)
  源文件: python/docs/api/uagents/query.md, python/src/uagents/asgi.py, python/src/uagents/query.py, python/tests/test_rest.py, python/tests/test_server.py
  Server Architecture
    · Core Components
    · Message Processing Flow
  REST Endpoint Management
    · Endpoint Registration
    · Agent Inspector Endpoints
  Server Integration
    · Agent Lifecycle Integration
    · Synchronous Message Handling
  Configuration and Deployment

## · Mailbox Client  (L3335)
  源文件: python/docs/api/uagents/experimental/search/__init__.md, python/docs/api/uagents/mailbox.md, python/src/uagents/experimental/search/__init__.py, python/src/uagents/mailbox.py, python/tests/test_config.py
  Overview
  Registration Process
  Authentication Flow (Attestation)
  Message Polling and Processing
  Key Components
    · MailboxClient
    · Data Models
  Envelope Handling and Security
  Integration with Agents
  Relationship with ASGI Server

## · Dispenser and Dispatcher  (L3531)
  源文件: python/docs/api/uagents/communication.md, python/docs/api/uagents/dispatch.md, python/docs/api/uagents/registration.md, python/src/uagents/communication.py, python/src/uagents/dispatch.py
  Architecture Overview
    · Message Routing System Architecture
  Dispenser: Outbound Message Queue
    · Dispenser Class Structure
    · Core Methods
    · External Delivery
  Dispatcher: Inbound Message Router
    · Dispatcher Class Structure
    · Routing and Registration
    · Synchronous Response Management
  Message Flow Patterns
    · Outbound Message Sequence
    · Inbound Message Sequence
  Utility Functions

## · Address Resolution  (L3739)
  源文件: python/docs/api/uagents/experimental/dialogues/__init__.md, python/docs/api/uagents/resolver.md, python/src/uagents/resolver.py, python/uagents-core/uagents_core/types.py, python/uagents-core/uagents_core/utils/messages.py, python/uagents-core/uagents_core/utils/resolver.py
  Resolution Architecture
    · Resolver Hierarchy
  Core Resolver Classes
    · GlobalResolver
    · AlmanacApiResolver
    · NameServiceResolver
  Resolution Process Flow
    · Address Format Parsing
    · Endpoint Selection Algorithm
  Integration with Communication System
    · Resolver Usage in Message Dispatch
    · Contract Integration Functions
  Configuration and Customization
    · RulesBasedResolver
    · Configuration Parameters

## · Agent Registration  (L3953)
  源文件: python/docs/api/uagents/asgi.md, python/docs/api/uagents/types.md, python/src/uagents/config.py, python/src/uagents/crypto/__init__.py, python/src/uagents/network.py, python/src/uagents/registration.py, python/src/uagents/types.py, python/tests/test_flakey_network_registration.py, python/tests/test_registration.py
  Overview
  Registration System Architecture
  Registration Process
    · API Registration
    · Blockchain Registration
  Registration Data
  Registration Renewal
  Batch Registration Policies
  Error Handling and Retries
  Summary

## · Almanac Contract  (L4172)
  源文件: python/docs/api/uagents/config.md, python/docs/api/uagents/crypto/__init__.md, python/docs/api/uagents/network.md, python/src/uagents/config.py, python/src/uagents/crypto/__init__.py, python/src/uagents/network.py
  Contract Architecture
  AlmanacContract Class
    · Core Methods
    · Contract Configuration
  Agent Registration Process
    · Registration Message Structure
  Query Operations
    · Agent Record Queries
    · Contract State Queries
  Batch Registration
    · AlmanacContractRecord Class
  Version Compatibility
  Network Configuration and Access
  Error Handling and Resilience
    · Transaction Broadcasting
    · Common Exceptions

## · Registration Policies  (L4397)
  源文件: .gitignore, python/docs/api/uagents/asgi.md, python/docs/api/uagents/types.md, python/src/uagents/registration.py, python/src/uagents/types.py, python/tests/test_flakey_network_registration.py, python/tests/test_registration.py, python/uagents-core/uagents_core/registration.py, python/uagents-core/uagents_core/utils/registration.py
  Purpose and Scope
  Registration Policy Overview
    · Registration Policy Class Hierarchy
  Registration Policy Types
    · Single Agent Registration Policies
    · Batch Registration Policies
  Registration Process
  Registration Data
  Registration Decision Process
  Error Handling and Retry Mechanisms
  Batch Registration

## · Advanced Features  (L4629)
  源文件: python/docs/api/uagents/experimental/quota/__init__.md, python/src/uagents/experimental/dialogues/__init__.py, python/src/uagents/experimental/quota/__init__.py, python/src/uagents/storage/__init__.py, python/tests/test_agent_registration.py
  Dialogues
  Quota Protocol
  Wallet Messaging
  Security Features
    · Cryptographic Capabilities
    · Secure Storage
  Experimental Search and Mobility
  Summary of Advanced Components

## · Dialogues  (L4790)
  源文件: python/docs/api/uagents/experimental/dialogues/__init__.md, python/docs/api/uagents/resolver.md, python/src/uagents/experimental/dialogues/__init__.py, python/src/uagents/resolver.py, python/src/uagents/storage/__init__.py, python/tests/test_agent_registration.py
  Purpose and Scope
  Core Components
    · Node/Edge Graph Model
  Session Management
    · Session Lifecycle
    · Message Validation and Flow
  Cleanup and Timeouts
  Implementation Detail: State Transitions
  Natural Language to Code Mapping

## · Quota Protocol  (L4969)
  源文件: python/docs/api/uagents/experimental/quota/__init__.md, python/src/uagents/experimental/quota/__init__.py
  Overview
  Core Components
  QuotaProtocol Class Structure
  Usage Patterns
    · Initialization and Basic Rate Limiting
    · Access Control
  Request Flow and Rate Limiting
  Implementation Details
    · Request Tracking
    · Error Handling

## · Wallet Messaging  (L5175)
  源文件: python/src/uagents/config.py, python/src/uagents/crypto/__init__.py, python/src/uagents/network.py, python/uagents-core/uagents_core/contrib/protocols/payment/__init__.py
  Introduction
  Cryptographic Signing
    · Arbitrary Data Signing
    · Almanac Registration Signing
  Payment Protocol Integration
    · Payment State Machine
    · Protocol Components
  Ledger Interaction
    · Key Ledger Functions
    · Transaction Flow Logic
  Configuration and Constants

## · Security Features  (L5303)
  源文件: .github/ISSUE_TEMPLATE/config.yml, .github/PULL_REQUEST_TEMPLATE/release.md, .gitignore, CITATION.cff, SECURITY.md, python/src/uagents/config.py, python/src/uagents/crypto/__init__.py, python/src/uagents/network.py, python/uagents-core/uagents_core/identity.py, python/uagents-core/uagents_core/registration.py, python/uagents-core/uagents_core/utils/registration.py
  Cryptographic Foundation
  VerifiableModel Pattern
    · Data Flow: Signing and Verification
  Challenge-Response Authentication
    · Registration Flow
  Almanac Contract Security
    · Almanac Signature
  Wallet and Arbitrary Data Signing
  Security Policy and Reporting

## · Experimental Search and Mobility  (L5451)
  源文件: python/docs/api/uagents/experimental/mobility/__init__.md, python/docs/api/uagents/experimental/mobility/protocols/base_protocol.md, python/docs/api/uagents/experimental/search/__init__.md, python/docs/api/uagents/mailbox.md, python/src/uagents/experimental/mobility/__init__.py, python/src/uagents/experimental/mobility/protocols/__init__.py, python/src/uagents/experimental/mobility/protocols/base_protocol.py, python/src/uagents/experimental/search/__init__.py, python/src/uagents/mailbox.py, python/tests/test_config.py
  Experimental Search API
    · Search Criteria and Filtering
    · Key Discovery Functions
  Mobility Protocols
    · The MobilityAgent Class
    · Mobility Handshake Data Flow
    · Handshake Models
  Implementation Mapping
    · Summary of Mobility Types

## · AI Integration  (L5597)
  源文件: python/uagents-adapter/README.md, python/uagents-adapter/pyproject.toml, python/uagents-ai-engine/pyproject.toml
  Architecture Overview
  AI Framework Adapters
    · LangChain Integration
    · CrewAI Integration
  MCP Integration
  A2A Protocol Bridges
    · A2A Inbound and Outbound
  AI Engine Integration
  Summary of Integration Packages

## · LangChain Integration  (L5926)
  源文件: python/uagents-adapter/.gitignore, python/uagents-adapter/README.md, python/uagents-adapter/pyproject.toml, python/uagents-adapter/src/uagents_adapter/crewai/__init__.py, python/uagents-adapter/src/uagents_adapter/langchain/__init__.py, python/uagents-adapter/src/uagents_adapter/langchain/agent_utils.py, python/uagents-adapter/src/uagents_adapter/langchain/tools.py
  Architecture Overview
    · System Components Diagram
  Core Components
    · LangchainRegisterTool
    · Message Models and Protocols
    · AgentManager Utility
  Message Flow and Execution Patterns
    · Direct Query Execution Flow
    · Chat Protocol Execution Flow
  Configuration and Deployment
    · LangchainRegisterToolInput Schema
    · Agent Lifecycle Management
  Agentverse Integration
    · Registration and API Integration

## · CrewAI Integration  (L6218)
  源文件: python/uagents-adapter/README.md, python/uagents-adapter/pyproject.toml, python/uagents-adapter/src/uagents_adapter/a2a_outbound/adapter.py, python/uagents-adapter/src/uagents_adapter/a2a_outbound/ap2/bridge_mapping.py, python/uagents-adapter/src/uagents_adapter/crewai/tools.py
  Purpose and Architecture
  Core Components
    · CrewaiRegisterTool
    · Input Schema
  Registration and Conversion Process
    · Port Management
  Message Processing and Parameter Extraction
    · Chat Protocol Integration
    · Parameter Extraction Logic
  Message Handlers
    · Parameter Message Handler
  Agentverse Integration
    · README Generation
  Configuration Options
    · CrewaiRegisterToolInput Parameters
    · Schema Definition
  Error Handling

## · A2A Protocol Bridge  (L6505)
  源文件: python/uagents-adapter/src/uagents_adapter/a2a_inbound/README.md, python/uagents-adapter/src/uagents_adapter/a2a_inbound/__init__.py, python/uagents-adapter/src/uagents_adapter/a2a_inbound/adapter.py, python/uagents-adapter/src/uagents_adapter/a2a_inbound/agentverse_executor.py, python/uagents-adapter/src/uagents_adapter/a2a_inbound/cli.py, python/uagents-adapter/src/uagents_adapter/a2a_outbound/adapter.py, python/uagents-adapter/src/uagents_adapter/a2a_outbound/ap2/artifacts.py, python/uagents-adapter/src/uagents_adapter/a2a_outbound/ap2/bridge_mapping.py, python/uagents-adapter/src/uagents_adapter/a2a_outbound/readme.md, python/uagents-adapter/src/uagents_adapter/common/__init__.py, python/uagents-adapter/src/uagents_adapter/crewai/tools.py
  Architecture Overview
    · Overall A2A Bridge Architecture
  Outbound Bridge (uAgent to A2A)
    · Outbound Architecture Components
    · Payment Bridging (AP2 to uAgents)
  Inbound Bridge (A2A to uAgent)
    · Inbound Bridge Components
    · Bridge Agent Communication Flow
  Message Flow and Protocol Translation
    · Outbound Message Flow (Chat to A2A)
    · Inbound Message Flow (A2A to Chat)
  Configuration and Deployment
    · CLI Deployment
    · A2ARegisterTool
    · Security Configuration

## · AI Engine  (L6783)
  源文件: python/uagents-ai-engine/examples/simple_agent.py, python/uagents-ai-engine/pyproject.toml, python/uagents-ai-engine/src/ai_engine/__init__.py, python/uagents-ai-engine/src/ai_engine/chitchat.py, python/uagents-ai-engine/src/ai_engine/dialogue.py, python/uagents-ai-engine/src/ai_engine/messages.py, python/uagents-ai-engine/src/ai_engine/types.py
  Architecture Overview
  Response Types and Models
    · UAgentResponseType Enumeration
    · Core Response Models
  Dialogue Management Framework
    · Edge Metadata System
    · ChitChatDialogue Implementation
  Message Models
    · Base Message Structure
    · Integration Pattern Example

## · Chat Agent and MCP Adapter  (L7000)
  源文件: python/src/uagents/experimental/chat_agent/README.md, python/src/uagents/experimental/chat_agent/__init__.py, python/src/uagents/experimental/chat_agent/llm.py, python/src/uagents/experimental/chat_agent/protocol.py, python/src/uagents/experimental/chat_agent/tools.py, python/tests/examples/44-bureau-chat-agents/main.py, python/tests/examples/44-bureau-chat-agents/protocols.py, python/tests/examples/45-interactive-cards/protocols.py, python/uagents-adapter/src/uagents_adapter/mcp/__init__.py, python/uagents-adapter/src/uagents_adapter/mcp/adapter.py, python/uagents-adapter/src/uagents_adapter/mcp/protocol.py, python/uagents-core/uagents_core/config.py
  ChatAgent and ChatProtocol
    · Data Flow: Message Processing
    · Tool Extraction
  LLM Configuration
  Agent Chat Protocol (AgentChatProtocol)
    · Core Models
    · Protocol Specification
  Interactive Cards
  MCP Server Adapter

## · Development  (L7149)
  源文件: .github/CODEOWNERS, .github/ISSUE_TEMPLATE/bug-report.yml, .github/ISSUE_TEMPLATE/feature-request.yml, .github/pull_request_template.md, .github/workflows/pr-title-linting.yml, CONTRIBUTING.md, DEVELOPING.md, LICENSE, README.md, python/uagents-core/uagents_core/__init__.py, Contributing Guide, Release Process
  Development Environment Setup
    · Environment Configuration
    · Code Quality Standards
  Testing Infrastructure
    · Test Execution Workflow
  Contribution Workflow
    · PR Submission Process
  Release and Deployment
    · Release Automation

## · Contributing Guide  (L7299)
  源文件: .github/CODEOWNERS, .github/ISSUE_TEMPLATE/bug-report.yml, .github/ISSUE_TEMPLATE/feature-request.yml, .github/pull_request_template.md, .github/workflows/pr-title-linting.yml, CONTRIBUTING.md, DEVELOPING.md, LICENSE, README.md, python/.pre-commit-config.yaml, python/uagents-core/uagents_core/__init__.py
  Development Environment Setup
    · Environment Requirements
    · Repository Structure
  Development Workflow
    · Code Quality Pipeline
    · Commit Message Standards
  Issue Management
    · Issue Types and Templates
    · Bug Report Requirements
    · Feature Request Process
  Pull Request Process
    · PR Title and Content Standards
    · PR Template Requirements
  Code Review and Merging
    · Code Ownership
    · Review Requirements
    · Merge Strategy
  Testing and Quality Assurance
    · Testing Requirements
    · Quality Standards (Pre-commit)

## · Release Process  (L7598)
  源文件: .github/workflows/ci-tests.yml, .github/workflows/coverage.yml, .github/workflows/release.yml, python/README.md, python/scripts/do_release.py, python/uagents-adapter/uv.lock
  Overview
  Supported Packages
  Release Process Flow
    · 1. Version Update and Pull Request
    · 2. Automated Release Workflow Execution
  Release Tool Implementation
    · The ReleaseTool Class
    · Versioning Logic
    · Build and Release Utilities
  Environment and Secrets Management
  Special Handling for Main Package

## · Deployment  (L7747)
  源文件: python/deployment/docker/Dockerfile, python/deployment/docker/onbuild.Dockerfile, python/deployment/hello-agent/.dockerignore, python/deployment/hello-agent/README.md, python/deployment/hello-agent/agent.py, python/deployment/hello-agent/requirements.txt, python/deployment/helm/uagent/.helmignore, python/deployment/helm/uagent/Chart.yaml
  Overview of Deployment Architecture
    · Natural Language to Code Entity Space: Agent Initialization
  Docker Containerization
    · Standard Dockerfile
    · On-Build Pattern
  Kubernetes and Helm Configuration
    · Chart Structure
    · Deployment Workflow Diagram
  Reference Deployment: hello-agent
    · Configuration via Environment
    · Implementation Details
    · Exclusion Rules

## · Glossary  (L7875)
  源文件: CONTRIBUTING.md, DEVELOPING.md, LICENSE, README.md, python/docs/api/uagents/agent.md, python/docs/api/uagents/asgi.md, python/docs/api/uagents/communication.md, python/docs/api/uagents/dispatch.md, python/docs/api/uagents/registration.md, python/docs/api/uagents/types.md, python/src/uagents/agent.py, python/src/uagents/communication.py
  Core Framework Concepts
    · Agent
    · Context (`ctx`)
    · Model
  Communication and Routing
    · Envelope
    · Dispenser
    · Dispatcher
    · Resolver
    · Natural Language to Code Entity Mapping: Communication
  Registration and Discovery
    · Almanac
    · Registration Policy
    · Attestation
  Technical Abbreviations & Jargon
  Infrastructure and Tooling
    · uagents-core
    · uagents-adapter
    · LedgerClient