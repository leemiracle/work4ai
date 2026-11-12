# Skeleton: dust（26 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 27KB | 7 | ~9 | 30 |
| 2 | System Architecture | L596 | 32KB | 8 | ~4 | 29 |
| 3 | Type System and SDK | L1293 | 29KB | 14 | ~21 | 27 |
| 4 | Core Types and Schemas | L2094 | 39KB | 17 | ~16 | 25 |
| 5 | DustAPI Client | L3106 | 16KB | 5 | ~9 | 14 |
| 6 | MCP Transport Protocol | L3733 | 20KB | 6 | ~10 | 14 |
| 7 | Agent System | L4301 | 26KB | 4 | ~13 | 22 |
| 8 | Agent Configuration and Management | L4917 | 23KB | 6 | ~4 | 20 |
| 9 | Agent Builder Interface | L5340 | 27KB | 10 | ~10 | 20 |
| 10 | Agent Execution and Temporal Workflows | L6028 | 34KB | 6 | ~8 | 24 |
| 11 | Prompt Construction and LLM Integration | L6865 | 53KB | 17 | ~21 | 23 |
| 12 | Skill System | L8350 | 25KB | 4 | ~8 | 9 |
| 13 | Trigger System | L9099 | 27KB | 12 | ~6 | 21 |
| 14 | Global Agents | L9896 | 31KB | 8 | ~18 | 25 |
| 15 | MCP Tool System | L10699 | 31KB | 15 | ~3 | 24 |
| 16 | MCP Server Architecture | L11469 | 28KB | 9 | ~12 | 24 |
| 17 | Tool Discovery Pipeline | L12183 | 23KB | 11 | ~8 | 23 |
| 18 | Tool Execution and Authentication | L12810 | 33KB | 11 | ~12 | 23 |
| 19 | Conversation System | L13670 | 27KB | 13 | ~10 | 24 |
| 20 | Conversation Management API | L14363 | 41KB | 11 | ~12 | 28 |
| 21 | Message Flow and Persistence | L15461 | 26KB | 10 | ~6 | 29 |
| 22 | Event Streaming and Real-time Updates | L16090 | 40KB | 18 | ~5 | 24 |
| 23 | Conversation UI Components | L17151 | 33KB | 11 | ~9 | 21 |
| 24 | Sparkle Design System | L17934 | 23KB | 7 | ~13 | 8 |
| 25 | Component Library and Architecture | L18653 | 25KB | 5 | ~14 | 8 |
| 26 | Build System and Distribution | L19362 | 20KB | 6 | ~10 | 8 |


## · Overview  (L6)
  源文件: connectors/package.json, extension/css.d.ts, extension/package.json, extension/tsconfig.json, front/admin/db.ts, front/components/assistant/conversation/ErrorMessage.tsx, front/components/assistant/conversation/lib.ts, front/components/providers/types.ts, front/components/resources/resources_icons.tsx, front/css.d.ts, front/lib/actions/mcp.ts, front/lib/actions/mcp_icons.tsx
  Platform Purpose
  High-Level Architecture
  Core Domain Entities
  Technology Stack
  Workspace and Authentication Model
  Conversation Flow Overview
  Agent Execution Architecture
  MCP Server Integration
  Type System and Validation
  Key File Locations

## · System Architecture  (L596)
  源文件: connectors/package.json, extension/css.d.ts, extension/package.json, extension/tsconfig.json, front/admin/db.ts, front/components/assistant/conversation/ErrorMessage.tsx, front/components/assistant/conversation/lib.ts, front/components/providers/types.ts, front/components/resources/resources_icons.tsx, front/css.d.ts, front/lib/actions/mcp.ts, front/lib/actions/mcp_icons.tsx
  Purpose and Scope
  Architectural Layers
  Core Subsystems
    · Conversation Management System
    · Agent Configuration and Execution
  MCP Server Architecture
    · Internal MCP Server Registry
  Data Flow Patterns
    · Type System and Validation
    · Event Streaming Architecture
  Technology Stack
    · Core Technologies
    · Database Schema Overview
  Request Flow Example

## · Type System and SDK  (L1293)
  源文件: connectors/package.json, extension/css.d.ts, extension/package.json, extension/tsconfig.json, front/components/providers/types.ts, front/components/resources/resources_icons.tsx, front/css.d.ts, front/lib/actions/mcp_icons.tsx, front/lib/actions/mcp_internal_actions/constants.test.ts, front/lib/actions/mcp_internal_actions/constants.ts, front/lib/actions/mcp_internal_actions/remote_servers.ts, front/lib/actions/mcp_internal_actions/servers/index.ts
  Purpose and Scope
  Architecture Overview
  Core Type Definitions
    · Model Provider and Model ID Types
    · Message Type Schemas
    · Agent Configuration Types
    · Feature Flags Schema
  MCP Server Type System
  DustAPI Client Class
    · Streaming Event Types
  Runtime Type Validation
  Content Type System
  Error Handling System
  SDK Package Structure
  Type System Integration with Frontend
  SDK Consumer Patterns

## · Core Types and Schemas  (L2094)
  源文件: front/components/providers/types.ts, front/components/resources/resources_icons.tsx, front/lib/actions/mcp_icons.tsx, front/lib/actions/mcp_internal_actions/constants.test.ts, front/lib/actions/mcp_internal_actions/constants.ts, front/lib/actions/mcp_internal_actions/remote_servers.ts, front/lib/actions/mcp_internal_actions/servers/index.ts, front/lib/api/assistant/global_agents/configurations/anthropic.ts, front/lib/api/assistant/global_agents/configurations/dust/deep-dive.ts, front/lib/api/assistant/global_agents/configurations/dust/dust.ts, front/lib/api/assistant/global_agents/configurations/google.ts, front/lib/api/assistant/global_agents/configurations/helper.ts
  Overview and Architecture
  Core Type System Architecture
  FlexibleEnumSchema Pattern
  Model Provider and LLM IDs
    · Model Provider ID Schema
    · Model LLM ID Schema
    · Agent Model Configuration Schema
  Agent Configuration Schemas
    · Agent Configuration Type Hierarchy
  Conversation and Message Schemas
    · Conversation Message Type System
    · Content Fragment Schemas
  MCP (Model Context Protocol) Type Definitions
    · MCP Action Schema
    · MCP Server Icon Schemas
    · MCP Server Constants
    · MCP Validation and Approval
  Data Source and Content Node Schemas
    · Data Source Type Hierarchy
    · Retrieval Document Schema
  File Content Type Schemas
    · Supported File Formats
  Workspace and User Schemas
  Feature Flags System
    · Whitelistable Features Schema
    · Workspace Type System
  Event Streaming Schemas
    · Agent Message Event Types
  Error Handling Schemas
    · API Error Type System
  Schema Validation Patterns
    · Type Guard Functions
    · Schema Parsing and Validation
  Schema Organization and Exports
    · Export Structure
  Usage Across the Codebase
    · Type System Consumers
  Schema Evolution and Compatibility
    · Version Management
    · Common Patterns for Schema Updates

## · DustAPI Client  (L3106)
  源文件: connectors/package.json, extension/css.d.ts, extension/package.json, extension/tsconfig.json, front/css.d.ts, front/lib/api/actions/mcp/client_side_registry.ts, front/package.json, package-lock.json, package.json, sdks/js/package.json, sdks/js/src/index.ts, sdks/js/src/mcp_transport.ts
  Purpose and Scope
  Installation
  DustAPI Class Overview
    · Class Structure
  Constructor Patterns
    · Modern Constructor (Recommended)
    · Legacy Constructor
  Authentication and Credentials
    · DustAPICredentials Type
    · API Key Patterns
    · Base Headers Construction
  High-Level API Namespaces
    · Lazy Loading Pattern
    · Namespace Implementations
  Request Method
    · Request Method Signature
    · URL Construction
  Request Flow Diagram
  Response Handling
    · Result Type Pattern
    · Response Parsing with Zod
  Error Handling
    · Error Classification
    · Error Detection Utilities
  Streaming Responses
    · Streamed App Execution
    · Event Types
    · Stream Processing
  API Method Examples
    · User Information
    · Data Sources
    · Agent Configurations
    · Mention Parsing
    · Mention Suggestions
  MCP-Related Methods
    · Registration and Heartbeat
    · Request Streaming
    · Result Posting
  Workspace Management
    · Workspace ID Operations
  Usage Patterns
    · Basic Usage
    · With Dynamic Authentication
    · With Streaming

## · MCP Transport Protocol  (L3733)
  源文件: connectors/package.json, extension/css.d.ts, extension/package.json, extension/tsconfig.json, front/css.d.ts, front/lib/api/actions/mcp/client_side_registry.ts, front/package.json, package-lock.json, package.json, sdks/js/package.json, sdks/js/src/index.ts, sdks/js/src/mcp_transport.ts
  Purpose and Scope
  Architecture Overview
    · System Components Diagram
  Transport Lifecycle
    · Lifecycle State Machine
  Registration Flow
    · Registration Sequence
    · Server ID Generation
  Heartbeat Mechanism
    · Heartbeat Configuration
    · Heartbeat Processing
    · Heartbeat Failure Recovery
  Request/Response Flow
    · SSE Connection Establishment
    · Tool Execution Request/Response
  Redis Schema and TTL Management
    · Redis Key Structure
    · TTL Refresh Strategy
  Error Handling and Reconnection
    · Error Scenarios and Recovery
    · Reconnection Logic
    · LastEventId Resume Mechanism
  Implementation Details
    · Constructor Parameters
    · Transport Interface Compliance
    · Cleanup on Close
  Package Dependencies

## · Agent System  (L4301)
  源文件: front/components/agent_builder/AgentBuilder.tsx, front/components/agent_builder/AgentBuilderFormContext.tsx, front/components/agent_builder/AgentBuilderLeftPanel.tsx, front/components/agent_builder/submitAgentBuilderForm.ts, front/components/agent_builder/transformAgentConfiguration.ts, front/components/agent_builder/triggers/AgentBuilderTriggersBlock.tsx, front/components/agent_builder/triggers/RecentWebhookRequests.tsx, front/components/agent_builder/triggers/TriggerCard.tsx, front/components/agent_builder/triggers/TriggerSelectionPage.tsx, front/components/agent_builder/triggers/TriggerViewsSheet.tsx, front/components/agent_builder/triggers/schedule/ScheduleEditionScheduler.tsx, front/components/agent_builder/triggers/schedule/ScheduleEditionSheet.tsx
  System Architecture
  Agent Configuration
    · Agent Statuses
    · Agent Scopes
  Agent Execution Flow
    · Step Execution and Multi-Step Reasoning
    · State Persistence with AgentStepContentResource
  Agent Builder Interface
    · Form Data Transformation
    · Pending Agent Creation
  Skills and Tool Integration
  Trigger System
  Action Approval and Validation
    · Per-Agent Approval Persistence
  Error Handling and Recovery
    · Workflow-Level Errors
    · Activity-Level Errors
    · Cost and Subagent Guardrails
  Event Streaming Architecture
  Database Schema
  API Endpoints
    · Agent Configuration Management
    · Trigger Management
    · Action Validation

## · Agent Configuration and Management  (L4917)
  源文件: front/components/agent_builder/AgentBuilder.tsx, front/components/agent_builder/AgentBuilderFormContext.tsx, front/components/agent_builder/AgentBuilderLeftPanel.tsx, front/components/agent_builder/submitAgentBuilderForm.ts, front/components/agent_builder/transformAgentConfiguration.ts, front/components/agent_builder/triggers/AgentBuilderTriggersBlock.tsx, front/components/agent_builder/triggers/RecentWebhookRequests.tsx, front/components/agent_builder/triggers/TriggerCard.tsx, front/components/agent_builder/triggers/TriggerSelectionPage.tsx, front/components/agent_builder/triggers/TriggerViewsSheet.tsx, front/components/agent_builder/triggers/schedule/ScheduleEditionScheduler.tsx, front/components/agent_builder/triggers/schedule/ScheduleEditionSheet.tsx
  Overview
  Type System Architecture
  Agent Status and Scope
  Agent Configuration CRUD API
  Form Management with React Hook Form
  Configuration Transform Pipeline
    · Server to Form Transformation
    · Form to API Transformation
    · Special Transforms
  Configuration Lifecycle Management
    · Pending Agent Creation
    · Version History and Rollback
  Trigger Management Integration
    · Trigger Permissions
  Permissions and Space Access

## · Agent Builder Interface  (L5340)
  源文件: front/components/agent_builder/AgentBuilder.tsx, front/components/agent_builder/AgentBuilderFormContext.tsx, front/components/agent_builder/AgentBuilderLeftPanel.tsx, front/components/agent_builder/submitAgentBuilderForm.ts, front/components/agent_builder/transformAgentConfiguration.ts, front/components/agent_builder/triggers/AgentBuilderTriggersBlock.tsx, front/components/agent_builder/triggers/RecentWebhookRequests.tsx, front/components/agent_builder/triggers/TriggerCard.tsx, front/components/agent_builder/triggers/TriggerSelectionPage.tsx, front/components/agent_builder/triggers/TriggerViewsSheet.tsx, front/components/agent_builder/triggers/schedule/ScheduleEditionScheduler.tsx, front/components/agent_builder/triggers/schedule/ScheduleEditionSheet.tsx
  Purpose and Scope
  Component Architecture
    · Main Components
    · AgentBuilder Component Structure
    · Left Panel Block Organization
  Form Management System
    · Schema Definition
    · Form Initialization
    · Field Arrays for Triggers
  Data Transform Pipeline
    · Transform Function Overview
    · transformAgentConfigurationToFormData
    · transformDuplicateAgentToFormData
    · Additional Configuration Flattening
  Form Submission Flow
    · Submit Handler Pipeline
    · submitAgentBuilderForm Function
    · Trigger Processing (Batch Operations)
  Trigger Management Interface
    · Triggers Block Component
    · TriggerViewsSheet Multi-Page Modal
    · Schedule Edition Form
    · Webhook Edition Form
  State Management Patterns
    · Mode-Based Initialization
    · Pending Agent Creation
    · Dirty State and Navigation Lock
    · Trigger Temporary IDs

## · Agent Execution and Temporal Workflows  (L6028)
  源文件: front/components/assistant/conversation/ErrorMessage.tsx, front/lib/actions/constants.ts, front/lib/actions/mcp.ts, front/lib/api/assistant/call_llm.ts, front/lib/api/assistant/conversation/title.ts, front/lib/api/assistant/conversation/validate_actions.ts, front/lib/api/assistant/conversation_rendering/helpers.test.ts, front/lib/api/assistant/conversation_rendering/helpers.ts, front/lib/api/assistant/conversation_rendering/index.ts, front/lib/api/assistant/conversation_rendering/message_rendering.test.ts, front/lib/api/assistant/conversation_rendering/message_rendering.ts, front/lib/api/assistant/conversation_rendering/pruning.ts
  Overview
  Workflow Architecture
    · Temporal Workflow and Activities
    · Workflow Execution Flow
  Workflow Lifecycle
    · Launching Workflows
    · Step Iteration Loop
    · Cancellation Handling
  Step Execution Coordination
    · executeStepIteration Function
    · runModelAndCreateActionsActivity Wrapper
  Model Execution
    · Tool Resolution and Prompt Construction
    · LLM Stream Processing
    · AgentStepContent Creation
  Tool Action Creation
    · createToolActionsActivity
    · Action Status Determination
    · AgentMCPActionResource Creation
  Tool Execution
    · runToolActivity
    · Tool Event Streaming
    · Tool Retry Policies
  Event Publishing and Database Updates
    · updateResourceAndPublishEvent
    · Database Update Processing
    · Event Coalescing
  Finalization Activities
    · Success Finalization
    · Error Finalization
    · Conversation Title Generation
  Resume and Approval Flows
    · Resume from Blocked Actions
    · Approval Event Publishing
  Error Handling and Retry Strategies
    · Retryable vs Terminal Errors
    · Cost and Subagent Guardrails
    · Timeout Handling
  Worker Configuration
    · Activity Registration
    · Bundling and Deployment

## · Prompt Construction and LLM Integration  (L6865)
  源文件: front/lib/actions/constants.ts, front/lib/api/assistant/call_llm.ts, front/lib/api/assistant/conversation_rendering/helpers.test.ts, front/lib/api/assistant/conversation_rendering/helpers.ts, front/lib/api/assistant/conversation_rendering/index.ts, front/lib/api/assistant/conversation_rendering/message_rendering.test.ts, front/lib/api/assistant/conversation_rendering/message_rendering.ts, front/lib/api/assistant/conversation_rendering/pruning.ts, front/lib/api/assistant/generation.test.ts, front/lib/api/assistant/generation.ts, front/lib/api/assistant/jit_actions.test.ts, front/lib/api/assistant/jit_actions.ts
  Purpose and Scope
  System Architecture
  Prompt Construction
    · Structured System Prompt Design
    · Prompt Section Builders
    · Cache Tier Assignment
  Conversation Rendering and Token Management
    · Message Rendering Pipeline
    · User Message Rendering
    · Agent Message Rendering
    · Token Counting
    · Context Pruning Strategy
  LLM Client Integration
    · Base LLM Class
    · Provider Implementations
  Streaming and Output Processing
    · LLM Event Types
    · Heartbeat Mechanism
    · Output Accumulation
  Supporting Systems
    · Observability and Tracing
    · Error Handling and Retries
    · Tool Call Parsing
  Integration with Agent Loop

## · Skill System  (L8350)
  源文件: front/components/skill_builder/SkillBuilderFormContext.tsx, front/components/skill_builder/submitSkillBuilderForm.ts, front/components/skills/SkillDetailsButtonBar.tsx, front/components/skills/SkillDetailsSheet.tsx, front/components/skills/SkillInfoTab.tsx, front/components/skills/SkillsTable.tsx, front/lib/models/skill.ts, front/lib/resources/skill/skill_resource.ts, front/types/assistant/skill_configuration.ts
  Overview
  Skill Types
    · Custom Skills
    · Global Skills
    · Skill Extension
  Skill Architecture
  Skill Components
    · Instructions
    · MCP Server References (Tools)
    · Attached Knowledge
    · File Attachments
  Skill States and Lifecycle
    · Status Enum
    · Lifecycle Operations
    · Versioning
  Permission System
    · Requested Space IDs
    · Editor Groups
  Agent Integration
    · Enabled Skills
    · Equipped Skills
    · Auto-Enabled Skills
    · Discoverable Skills
  Data Model
  Resource Layer
    · Unified Fetch API
    · Query Options
    · Mutation Operations
    · Permission Helpers
  API Endpoints
    · GET /api/w/[wId]/skills
    · POST /api/w/[wId]/skills
    · GET /api/w/[wId]/skills/[sId]
    · PATCH /api/w/[wId]/skills/[sId]
    · DELETE /api/w/[wId]/skills/[sId]
    · PATCH /api/w/[wId]/skills/[sId]/editors
  Usage Tracking

## · Trigger System  (L9099)
  源文件: front/components/agent_builder/AgentBuilder.tsx, front/components/agent_builder/AgentBuilderFormContext.tsx, front/components/agent_builder/AgentBuilderLeftPanel.tsx, front/components/agent_builder/submitAgentBuilderForm.ts, front/components/agent_builder/transformAgentConfiguration.ts, front/components/agent_builder/triggers/AgentBuilderTriggersBlock.tsx, front/components/agent_builder/triggers/RecentWebhookRequests.tsx, front/components/agent_builder/triggers/TriggerCard.tsx, front/components/agent_builder/triggers/TriggerSelectionPage.tsx, front/components/agent_builder/triggers/TriggerViewsSheet.tsx, front/components/agent_builder/triggers/schedule/ScheduleEditionScheduler.tsx, front/components/agent_builder/triggers/schedule/ScheduleEditionSheet.tsx
  Purpose and Scope
  Trigger Types and Data Model
    · Core Type Definitions
  Trigger Lifecycle and Status Management
    · Status States
    · Temporal Workflow Integration
    · Bulk Operations for Workspace Management
  Schedule Triggers
    · Configuration and Cron Expression
    · AI-Assisted Cron Generation
    · Temporal Schedule Workflow
    · Form Schema
  Webhook Triggers
    · Configuration and Webhook Sources
    · Webhook Configuration Structure
    · Event Filtering System
    · AI-Assisted Filter Generation
    · Rate Limiting and Execution Modes
    · Webhook Request History
  Permission Model: Editor and Subscribers
    · Editor vs Subscriber Roles
    · Subscriber Management API
  UI Components
    · Agent Builder Triggers Block
    · Form Field Arrays for Batch Operations
    · Multi-Page Sheet for Trigger Configuration
  Backend Architecture
    · Resource Layer: TriggerResource
    · Database Schema
  API Endpoints
    · Trigger CRUD API
    · Subscriber Management API
    · AI Assistant Endpoints
  Submission Flow
    · Form Submission in Agent Builder
    · Validation Rules
  Integration with Agent Execution

## · Global Agents  (L9896)
  源文件: front/components/providers/types.ts, front/components/resources/resources_icons.tsx, front/lib/actions/mcp_icons.tsx, front/lib/actions/mcp_internal_actions/constants.test.ts, front/lib/actions/mcp_internal_actions/constants.ts, front/lib/actions/mcp_internal_actions/remote_servers.ts, front/lib/actions/mcp_internal_actions/servers/index.ts, front/lib/api/assistant/global_agents/configurations/anthropic.ts, front/lib/api/assistant/global_agents/configurations/dust/deep-dive.ts, front/lib/api/assistant/global_agents/configurations/dust/dust.ts, front/lib/api/assistant/global_agents/configurations/google.ts, front/lib/api/assistant/global_agents/configurations/helper.ts
  Overview and Purpose
  Global Agent Identifier System
  Dynamic Content Injection
  The Dust Agent Family
  Model-Direct Agents
  HELPER Agent
  DEEP_DIVE Agent
  SIDEKICK Agent
  Auto-Enabled MCP Servers
  Global Agent Settings
  Global Agent Fetching

## · MCP Tool System  (L10699)
  源文件: front/components/actions/mcp/InternalMCPBearerTokenForm.tsx, front/components/actions/mcp/MCPServerHeaders.tsx, front/components/actions/mcp/RemoteMCPForm.tsx, front/components/actions/mcp/create/CustomHeadersConfigurationSection.tsx, front/components/providers/types.ts, front/components/resources/resources_icons.tsx, front/lib/actions/mcp_actions.ts, front/lib/actions/mcp_authentication.ts, front/lib/actions/mcp_icons.tsx, front/lib/actions/mcp_internal_actions/constants.test.ts, front/lib/actions/mcp_internal_actions/constants.ts, front/lib/actions/mcp_internal_actions/remote_servers.ts
  Architecture Overview
  Server Types and Registration
    · Internal MCP Servers
    · Client-Side MCP Servers
    · Remote MCP Servers
  Tool Discovery and Configuration
    · Tool Naming and Disambiguation
  Tool Execution Pipeline
    · Action Status Lifecycle
  Approval and Validation System
    · Argument-Level Approval
  Integration with Agent Loop
    · Retry Policies
  Tool Output and Progress Streaming
    · Output Item Storage
  Key Classes and Resources
    · AgentMCPActionResource
    · MCPServerViewResource
    · Tool Configuration Types
  Error Handling and Authentication
  Constants and Configuration

## · MCP Server Architecture  (L11469)
  源文件: front/components/actions/mcp/InternalMCPBearerTokenForm.tsx, front/components/actions/mcp/MCPServerHeaders.tsx, front/components/actions/mcp/RemoteMCPForm.tsx, front/components/actions/mcp/create/CustomHeadersConfigurationSection.tsx, front/components/providers/types.ts, front/components/resources/resources_icons.tsx, front/lib/actions/mcp_actions.ts, front/lib/actions/mcp_authentication.ts, front/lib/actions/mcp_icons.tsx, front/lib/actions/mcp_internal_actions/constants.test.ts, front/lib/actions/mcp_internal_actions/constants.ts, front/lib/actions/mcp_internal_actions/remote_servers.ts
  Server Types and Identification
    · Server Type Classification
    · Internal MCP Servers
    · Remote MCP Servers
    · Server ID Parsing
  MCPServerViewResource: Configuration Layer
    · Resource Model
    · Key Methods
    · System vs Custom Views
    · Conflict Prevention
  Server Metadata and Capabilities
    · Metadata Structure
    · Tool Stakes and Approval
    · Retry Policies
    · Availability and Restrictions
  Authentication and Authorization
    · Authentication Methods
    · OAuth Connection Management
    · Authentication Error Handling
    · Token Caching and Refresh
  Connection Management
    · Connection Establishment
    · Proxy Configuration
    · Transport Types
  Integration with Agent System
    · Agent Loop Integration
    · Skill Integration
    · Global Agent Auto-Enablement
    · Space-Scoped Access

## · Tool Discovery Pipeline  (L12183)
  源文件: front/components/actions/mcp/InternalMCPBearerTokenForm.tsx, front/components/actions/mcp/MCPServerHeaders.tsx, front/components/actions/mcp/RemoteMCPForm.tsx, front/components/actions/mcp/create/CustomHeadersConfigurationSection.tsx, front/components/assistant/conversation/ErrorMessage.tsx, front/lib/actions/mcp.ts, front/lib/actions/mcp_actions.ts, front/lib/actions/mcp_authentication.ts, front/lib/actions/mcp_metadata.ts, front/lib/api/assistant/conversation/title.ts, front/lib/api/assistant/conversation/validate_actions.ts, front/lib/api/mcp.ts
  Purpose and Scope
  Discovery Flow Overview
  Source Aggregation and Deduplication
    · Input Sources
    · Deduplication Logic
  Name Disambiguation
    · Disambiguation Algorithm
  Tool Listing from Servers
    · Server-Side Tool Listing
    · Client-Side Tool Listing
  Tool Validation
    · Name Validation
    · Schema Validation
  Description Enhancement
    · Enhancement Logic
  Configuration Assembly
    · Server-Side Configuration Assembly
    · Client-Side Configuration Assembly
    · Configuration Flow Diagram
  Result Format
    · Aggregate Structure
  Error Handling
    · Per-Server Error Collection
  Integration with Agent Loop

## · Tool Execution and Authentication  (L12810)
  源文件: front/components/actions/mcp/InternalMCPBearerTokenForm.tsx, front/components/actions/mcp/MCPServerHeaders.tsx, front/components/actions/mcp/RemoteMCPForm.tsx, front/components/actions/mcp/create/CustomHeadersConfigurationSection.tsx, front/components/assistant/conversation/ErrorMessage.tsx, front/lib/actions/mcp.ts, front/lib/actions/mcp_actions.ts, front/lib/actions/mcp_authentication.ts, front/lib/actions/mcp_metadata.ts, front/lib/api/assistant/conversation/title.ts, front/lib/api/assistant/conversation/validate_actions.ts, front/lib/api/mcp.ts
  Purpose and Scope
  Tool Execution Flow Overview
    · Core Execution Pipeline
    · Tool Call Mechanics
    · Event Stream and Race Condition
  Authentication and Connection Management
    · Connection Parameter Construction
    · OAuth Token Resolution for Remote Servers
    · Authentication Flow for Internal Servers
    · OAuth Token Refresh on 401/403
  Approval Workflows and Tool Stakes
    · Tool Stake Levels
    · Approval Status Determination
    · Validation and Resume Flow
    · Per-Argument Approval for Medium Stakes
  Retry Policies and Error Handling
    · Retry Policy Types
    · Timeout Handling
    · Error Categories and Propagation
  Activity Integration and Event Publishing
    · Activity Lifecycle
    · Deferred Event Publishing
    · Heartbeat and Cancellation
    · Event Coalescing for High Throughput
  Output Storage and Size Limits
    · Storage Strategy
    · Size Validation for Remote Servers

## · Conversation System  (L13670)
  源文件: front/admin/db.ts, front/components/agent_builder/AgentBuilderContext.tsx, front/components/agent_builder/AgentBuilderLayout.tsx, front/components/agent_builder/AgentBuilderPreview.tsx, front/components/agent_builder/AgentBuilderRightPanel.tsx, front/components/agent_builder/AgentBuilderTemplate.tsx, front/components/agent_builder/hooks/useAgentPreview.ts, front/components/assistant/conversation/AgentInputBar.tsx, front/components/assistant/conversation/AgentMessage.tsx, front/components/assistant/conversation/ConversationContainer.tsx, front/components/assistant/conversation/ConversationError.tsx, front/components/assistant/conversation/ConversationLayout.tsx
  Purpose and Scope
  Core Concepts
    · Conversations
    · Messages
    · Message Status and Lifecycle
    · Participants
  Database Schema
    · Core Models
    · Advisory Locks
  ConversationResource API
    · Resource Pattern
    · Permission Model
  Message Lifecycle
    · Creating User Messages
    · Rate Limiting
    · Editing User Messages
    · Deleting Messages
  Transaction Management
    · Rank and Version Assignment
    · Deadlock Prevention
  Event Streaming and Real-time Updates
    · Event Types
    · Event Publishing
    · Client-Side State Management
  Conversation UI Components
    · Component Hierarchy
    · VirtuosoMessageList Integration
    · Input Bar Architecture
    · Streaming UI Updates
  Integration with Agent System
    · Workflow Orchestration
    · Mentions and Participant Management
    · Content Fragments
  Conversation Branches

## · Conversation Management API  (L14363)
  源文件: front/admin/db.ts, front/components/assistant/conversation/lib.ts, front/lib/api/assistant/citations.ts, front/lib/api/assistant/conversation.ts, front/lib/api/assistant/conversation/destroy.ts, front/lib/api/assistant/conversation/fetch.ts, front/lib/api/assistant/conversation/mentions.test.ts, front/lib/api/assistant/conversation/mentions.ts, front/lib/api/assistant/messages.ts, front/lib/api/assistant/participants.ts, front/lib/models/agent/conversation.ts, front/lib/models/agent/conversation_branch.ts
  Purpose and Scope
  Overview
  Core Data Models
    · Database Schema
    · Type Definitions
  Conversation Lifecycle
    · Creating Conversations
    · Updating Conversations
    · Deleting or Leaving Conversations
  Message Operations
    · Posting User Messages
    · Editing User Messages
    · Retrying Agent Messages
    · Soft Deleting Messages
  ConversationResource Interface
    · Core Methods
    · Participation Management
    · Read Status Management
  Message Versioning and Ranking
    · Rank and Version System
    · Rank Allocation
  Rate Limiting
    · Rate Limit Tiers
  Transaction Management
    · Advisory Lock Mechanism
    · Transaction Scope
  API Routes

## · Message Flow and Persistence  (L15461)
  源文件: front/admin/db.ts, front/components/assistant/conversation/ErrorMessage.tsx, front/components/assistant/conversation/lib.ts, front/lib/actions/mcp.ts, front/lib/api/assistant/citations.ts, front/lib/api/assistant/conversation.ts, front/lib/api/assistant/conversation/destroy.ts, front/lib/api/assistant/conversation/fetch.ts, front/lib/api/assistant/conversation/mentions.test.ts, front/lib/api/assistant/conversation/mentions.ts, front/lib/api/assistant/conversation/title.ts, front/lib/api/assistant/conversation/validate_actions.ts
  Purpose and Scope
  Message Creation Lifecycle
    · High-Level Flow
    · Message Creation Transaction
  Transaction Management and Advisory Locking
    · Advisory Lock Implementation
    · Message Rank Calculation
  Database Schema and Models
    · Core Message Models
    · Message Visibility and Soft Deletion
  Message Versioning and Editing
    · Edit Message Flow
    · Message Version Retrieval
  Message Deletion and Cascades
    · Soft Delete vs Hard Delete
  Mention Processing
    · Mention Creation Flow
    · Mention Validation and Project Membership
  Message Persistence Guarantees
    · Atomicity Guarantees
    · Failure Modes
  Transaction Isolation and Consistency
    · Isolation Level
    · Read-Your-Writes Consistency

## · Event Streaming and Real-time Updates  (L16090)
  源文件: front/admin/db.ts, front/components/agent_builder/AgentBuilderContext.tsx, front/components/agent_builder/AgentBuilderLayout.tsx, front/components/agent_builder/AgentBuilderPreview.tsx, front/components/agent_builder/AgentBuilderRightPanel.tsx, front/components/agent_builder/AgentBuilderTemplate.tsx, front/components/agent_builder/hooks/useAgentPreview.ts, front/components/assistant/conversation/AgentInputBar.tsx, front/components/assistant/conversation/AgentMessage.tsx, front/components/assistant/conversation/ConversationContainer.tsx, front/components/assistant/conversation/ConversationError.tsx, front/components/assistant/conversation/ConversationLayout.tsx
  Overview
  Redis Pub/Sub Architecture
    · Channel Structure and Naming
    · Event Publishing Function
  Event Coalescing Mechanism
    · globalCoalescer Buffer Management
  SSE Endpoint and Delivery
    · Connection Establishment
    · Event Filtering and Delivery
  Event Types and Publishing
    · Agent Execution Events
    · Conversation-Level Events
  Client-Side Event Consumption
    · useConversationEvents Hook
    · useAgentMessageStream Hook
    · Optimistic UI Updates
  Event Publishing Patterns
    · updateResourceAndPublishEvent Pattern
    · Deferred Event Publishing
    · Terminal Event Processing
  Summary
  Event Types and Flow Sequence
  Event Publishing and Database Consistency
    · updateResourceAndPublishEvent Pattern
    · Terminal Event Processing
  Deferred Event Batching
    · Parallel Tool Execution Event Handling
  Message Editing and Retry Flow
    · Edit User Message
    · Retry Agent Message
  Summary

## · Conversation UI Components  (L17151)
  源文件: front/components/agent_builder/AgentBuilderContext.tsx, front/components/agent_builder/AgentBuilderLayout.tsx, front/components/agent_builder/AgentBuilderPreview.tsx, front/components/agent_builder/AgentBuilderRightPanel.tsx, front/components/agent_builder/AgentBuilderTemplate.tsx, front/components/agent_builder/hooks/useAgentPreview.ts, front/components/assistant/conversation/AgentInputBar.tsx, front/components/assistant/conversation/AgentMessage.tsx, front/components/assistant/conversation/ConversationContainer.tsx, front/components/assistant/conversation/ConversationError.tsx, front/components/assistant/conversation/ConversationLayout.tsx, front/components/assistant/conversation/ConversationViewer.tsx
  Purpose and Scope
  Component Hierarchy
    · Main Component Tree
  Message Rendering Components
    · MessageItem Component
    · UserMessage Component
    · AgentMessage Component
    · AgentMessageContent Sub-Component
  Input Bar Components
    · Input Bar Component Hierarchy
    · AgentInputBar
    · InputBar
    · InputBarContainer
  Context Providers
    · Context Provider Stack
    · BlockedActionsProvider
    · GenerationContextProvider
    · InputBarContext
  VirtuosoMessageList Integration
    · VirtuosoMessageList Configuration
    · Data Manipulation Methods
    · Scroll Behavior
  Message Streaming and Real-Time Updates
    · Event Processing Flow
    · Agent Message Streaming Hook
    · Conversation Event Subscription
  VirtuosoMessageListContext
    · Context Structure
    · Agent Builder Context Usage
  Message Type Definitions
    · VirtuosoMessage Type
    · MessageTemporaryState
  Conversation Container Integration
    · Component Responsibilities
  Layout and Error Handling
    · ConversationLayout
    · Error Display Components
  Agent Builder Preview Integration
    · Preview Component Structure

## · Sparkle Design System  (L17934)
  源文件: front/public/static/landing/product/Knowledge_Tooltips.jpg, sparkle/package.json, sparkle/src/components/ActionCard.tsx, sparkle/src/components/Dropdown.tsx, sparkle/src/components/SearchDropdownMenu.tsx, sparkle/src/components/index.ts, sparkle/src/stories/ActionCard.stories.tsx, sparkle/src/stories/Dropdown.stories.tsx
  Purpose and Scope
  Package Architecture and Build System
    · Package Structure
    · Build Configuration
  Component Library Architecture
    · Component Catalog
    · Foundation Dependencies
  Core Component Patterns
    · Dropdown Menu System
    · Action Card Component
  Styling and Theming System
    · Tailwind Integration
    · Dark Mode Support
  Composition Patterns and Hooks
    · Portal Mounting Strategy
    · Render Props and Component Functions
  Storybook Documentation
    · Story Organization
    · Example Story Structure
  Integration with Frontend Application
    · Import and Usage Pattern
    · Type Safety Integration
    · CSS Distribution
  Development Workflow
    · Build and Watch Scripts
    · Peer Dependencies

## · Component Library and Architecture  (L18653)
  源文件: front/public/static/landing/product/Knowledge_Tooltips.jpg, sparkle/package.json, sparkle/src/components/ActionCard.tsx, sparkle/src/components/Dropdown.tsx, sparkle/src/components/SearchDropdownMenu.tsx, sparkle/src/components/index.ts, sparkle/src/stories/ActionCard.stories.tsx, sparkle/src/stories/Dropdown.stories.tsx
  Purpose and Scope
  Component Organization
    · Export Structure
    · Component Export Pattern
  Component Architecture Patterns
    · Primitive Wrapping with Radix UI
    · Variant System with CVA
    · Composition with Sub-components
  Core Component Systems
    · Dropdown Menu System
    · ActionCard Component
  Type Safety and Props Patterns
    · Discriminated Unions
    · Link Wrapper Integration
    · Forward Ref Pattern
  Storybook Integration
    · Story Organization
    · Story Patterns
    · Interactive State Management
    · Component Development Workflow
  Specialized Component Patterns
    · SearchDropdownMenu Wrapper
    · Shared Style Constants
  Component Categories Reference
    · Complete Component List by Category
  Dependency Architecture
    · Core Dependencies
    · Peer Dependencies

## · Build System and Distribution  (L19362)
  源文件: front/public/static/landing/product/Knowledge_Tooltips.jpg, sparkle/package.json, sparkle/src/components/ActionCard.tsx, sparkle/src/components/Dropdown.tsx, sparkle/src/components/SearchDropdownMenu.tsx, sparkle/src/components/index.ts, sparkle/src/stories/ActionCard.stories.tsx, sparkle/src/stories/Dropdown.stories.tsx
  Purpose and Scope
  Build Pipeline Overview
  Build Script Configuration
  ESM Build Process
  CJS Build Process
  Tailwind CSS Compilation
  Package Exports Configuration
  Distribution Structure
  Component Export Pattern
  Consumption Patterns
    · Basic Usage
    · Direct Imports
    · Asset References
    · Side Effects Configuration
  Peer Dependencies
  Development Tools
    · Storybook Integration
    · Watch Mode
  Build Tool Dependencies
  Node.js Version Requirement