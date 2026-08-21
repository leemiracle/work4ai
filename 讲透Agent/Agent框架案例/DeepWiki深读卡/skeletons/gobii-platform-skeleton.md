# Skeleton: gobii-platform（36 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Platform Overview | L6 | 21KB | 11 | ~15 | 6 |
| 2 | Getting Started | L556 | 19KB | 3 | ~23 | 3 |
| 3 | Configuration & Deployment | L1270 | 26KB | 5 | ~12 | 3 |
| 4 | User Lifecycle & Authentication | L2038 | 14KB | 7 | ~7 | 7 |
| 5 | Core Concepts | L2446 | 18KB | 8 | ~4 | 9 |
| 6 | Agents | L3019 | 17KB | 7 | ~5 | 13 |
| 7 | Task Credits | L3495 | 18KB | 9 | ~13 | 9 |
| 8 | Organizations | L4023 | 23KB | 4 | ~17 | 10 |
| 9 | Agent Management | L4811 | 29KB | 10 | ~18 | 12 |
| 10 | Creating Agents | L5613 | 20KB | 5 | ~13 | 12 |
| 11 | Configuring Agents | L6179 | 20KB | 10 | ~8 | 5 |
| 12 | Agent Event Processing | L6760 | 19KB | 5 | ~14 | 8 |
| 13 | Agent Lifecycle | L7266 | 15KB | 5 | ~7 | 14 |
| 14 | Credit & Billing System | L7664 | 26KB | 9 | ~8 | 13 |
| 15 | TaskCreditService | L8381 | 25KB | 10 | ~8 | 6 |
| 16 | Subscription Management | L9092 | 21KB | 8 | ~6 | 7 |
| 17 | Organization Billing | L9718 | 21KB | 5 | ~4 | 7 |
| 18 | Usage Analytics | L10304 | 18KB | 4 | ~9 | 5 |
| 19 | Tool Integration | L10935 | 27KB | 8 | ~22 | 18 |
| 20 | MCP Tools | L11662 | 26KB | 4 | ~17 | 7 |
| 21 | Browser Automation | L12474 | 19KB | 8 | ~11 | 8 |
| 22 | LLM Integration | L13061 | 17KB | 4 | ~7 | 8 |
| 23 | Communication Systems | L13560 | 21KB | 6 | ~4 | 12 |
| 24 | Agent Web Chat | L14146 | 15KB | 7 | ~9 | 4 |
| 25 | Email & SMS | L14573 | 30KB | 16 | ~16 | 6 |
| 26 | Peer Messaging | L15585 | 20KB | 3 | ~13 | 8 |
| 27 | User Interfaces | L16203 | 20KB | 6 | ~1 | 12 |
| 28 | Console Interface | L16777 | 23KB | 7 | ~10 | 3 |
| 29 | Homepage & AI Employee Directory | L17497 | 22KB | 7 | ~13 | 9 |
| 30 | Agent Chat Interface | L18125 | 27KB | 11 | ~22 | 4 |
| 31 | API Reference | L18882 | 15KB | 3 | ~13 | 9 |
| 32 | REST API | L19328 | 30KB | 4 | ~24 | 9 |
| 33 | Authentication & Authorization | L20506 | 15KB | 7 | ~6 | 12 |
| 34 | Development & Administration | L20979 | 21KB | 4 | ~5 | 11 |
| 35 | Django Admin Interface | L21637 | 20KB | 9 | ~8 | 3 |
| 36 | Testing & CI/CD | L22271 | 19KB | 3 | ~4 | 8 |


## · Platform Overview  (L6)
  源文件: api/admin.py, api/agent/core/event_processing.py, api/models.py, config/settings.py, console/views.py, util/subscription_helper.py
  Purpose and Scope
  Architecture Overview
    · High-Level Component Architecture
  Deployment Modes
    · Community Edition
    · Proprietary Mode
    · Configuration Toggle Pattern
  Core Subsystems
    · Agent Management
    · Event Processing Pipeline
    · Credit and Billing System
    · Tool Integration
  Data Models
    · Key Model Relationships
    · Critical Model Classes
  Request Flow
    · Web Request: Create Agent
    · API Request: Browser Task
  Technology Stack
    · Core Framework
    · External Integrations
    · Database Features
  Bootstrap and First-Run Setup
  Observability

## · Getting Started  (L556)
  源文件: api/admin.py, config/settings.py, util/subscription_helper.py
  Overview
  Prerequisites
    · Required
    · Optional
  Installation Methods
    · Docker Compose (Recommended for Development)
    · Manual Installation
  Environment Configuration
    · Configuration Hierarchy
    · Core Environment Variables
    · Community vs Proprietary Mode
    · External Service Configuration
  Database Setup
    · Initialization
    · Database Connection Tuning
  First-Run Setup
    · Setup Middleware
    · LLM Bootstrap Requirement
    · Setup Sequence Diagram
  Running the Platform
    · Development Mode
    · Component Startup Order
    · Production Deployment
  Verification
    · Service Health Checks
    · Admin Access
    · Create First Agent
  Common Configuration Patterns
    · Local Development (Community Edition)
    · Staging Environment (Proprietary Mode)
    · Production Environment (Proprietary Mode)
  Next Steps

## · Configuration & Deployment  (L1270)
  源文件: api/admin.py, config/settings.py, util/subscription_helper.py
  Deployment Modes
    · Community Edition Behavior
    · Proprietary Mode Behavior
  Environment Variables
    · Smart Local Defaults
    · Core Configuration Variables
    · External Service Configuration
  Database Configuration
    · PostgreSQL Settings
  Redis & Celery Configuration
    · Redis Usage
    · Celery Beat Scheduler
    · Task Time Limits
    · Scheduled Tasks
  Storage Backends
    · Configuration Examples
    · Static Files vs Media Files
  External Service Integration
    · Stripe (Billing & Metering)
    · Email Providers
    · SMS (Twilio)
    · Analytics Integrations
    · MCP Tools (Pipedream)
  Feature Flags & Limits
    · Credit System Configuration
    · Community Unlimited Mode
    · First-Run Setup
    · Soft Expiration Settings
  Frontend Configuration (Vite)
  Configuration Diagram: Service Integration Flow
  Authentication & Turnstile
  Deployment Checklist
    · Required Environment Variables (Production)
    · Optional Services

## · User Lifecycle & Authentication  (L2038)
  源文件: console/forms.py, console/templates/console/organization_detail.html, console/templates/partials/_org_invite_modal.html, constants/stripe.py, pages/signals.py, tests/unit/test_organizations.py, tests/unit/test_pages_signals.py
  User Signup Flow
    · Signup Signal Handler
    · UTM Attribution System
    · Analytics Event Payload
  Login & Logout Events
    · Login Handler
    · Logout Handler
    · Error Handling
  Session Management
    · Session Data Structure
    · Context Switching
  Organization Membership
    · Membership Roles
    · Invitation Flow
    · Invite Model Structure
    · Acceptance Flow
    · Seat Reservation Logic
    · Member Management
  Authentication Mechanisms
    · Web Authentication (django-allauth)
    · API Key Authentication
  Related Systems

## · Core Concepts  (L2446)
  源文件: api/agent/core/event_processing.py, api/migrations/0115_persistentagentstep_credits_fields.py, api/models.py, console/views.py, tasks/services.py, tests/unit/test_persistent_agent_step_credits.py, tests/unit/test_task_credit_service.py, tests/unit/test_tool_costs.py, util/tool_costs.py
  Dual Ownership Model
    · Ownership Enforcement Patterns
    · Key Ownership Rules
  Core Entity Types
    · Agent Hierarchy
    · Agent Relationships
  Task Credit System
    · Credit Data Model
    · Credit Configuration
    · Credit Granting Patterns
  The TASKS_UNLIMITED Constant
  Credit Consumption Flow
    · Atomic Consumption Pattern
    · Pre-Processing Credit Gate
    · Mid-Loop Tool Gating
  API Keys & Authentication
    · ApiKey Structure
    · Key Generation & Validation
    · Console Context Resolution
  Plans & Subscriptions
    · Plan Types
    · Credit Provisioning
  Communication Channels
  Budget Cycles
    · Budget Context Structure
    · Cycle Lifecycle
  Entity Relationship Overview

## · Agents  (L3019)
  源文件: api/agent/core/llm_config.py, api/agent/tools/mcp_tools.py, api/migrations/0155_persistentagent_daily_credit_limit_and_more.py, api/tasks/browser_agent_tasks.py, console/templates/console/agent_detail.html, console/templates/partials/_agent_list.html, tests/unit/test_agent_event_processing_credits.py, tests/unit/test_browser_task_follow_up.py, tests/unit/test_console.py, tests/unit/test_event_processing_llm_selection.py, tests/unit/test_llm_failover.py, tests/unit/test_mcp_tools.py
  Purpose and Scope
  Agent Architecture Overview
  PersistentAgent Model
    · Key Fields
    · Lifecycle States
    · Daily Credit Limits
  BrowserUseAgent Model
    · Key Fields
    · Browser Profile Management
    · Proxy Selection
  Agent Relationship and Responsibilities
  Agent Creation and Deletion
    · Creation Flow
    · Deletion Flow
  Agent Configuration
    · Charter
    · Schedule
    · Communication Endpoints
    · Secrets
    · MCP Tools
  Agent Execution Context
    · LLM Selection
    · Credit Gating
    · Vision Support
    · Parallel Tool Calls
  Data Model Relationships
  Summary

## · Task Credits  (L3495)
  源文件: api/agent/core/event_processing.py, api/migrations/0115_persistentagentstep_credits_fields.py, api/models.py, console/views.py, tasks/services.py, tests/unit/test_persistent_agent_step_credits.py, tests/unit/test_task_credit_service.py, tests/unit/test_tool_costs.py, util/tool_costs.py
  Purpose and Scope
  Credit Data Model
    · TaskCredit Model
    · Dual Ownership: Users vs Organizations
    · Credit Block Lifecycle
  Credit Configuration
    · TaskCreditConfig
    · ToolCreditCost
    · TASKS_UNLIMITED Constant
  Credit Provisioning
    · Subscription-Based Granting
    · Organization Seat-Based Credits
    · Additional Tasks
  Credit Consumption
    · Atomic Consumption with SELECT FOR UPDATE
    · Fractional Credits
    · Multi-Block Consumption
    · Credit-Step Linking
  Credit Gating in Agent Execution
    · Pre-Processing Gate
    · Per-Tool Mid-Loop Gate
    · Daily Credit Limits
  Owner-Aware Operations
  Usage Tracking and Thresholds
  Tool Cost Configuration
    · Default Cost
    · Per-Tool Overrides
    · Channel-Specific Costs
  Code Entity Reference
    · Key Classes and Functions

## · Organizations  (L4023)
  源文件: api/agent/core/event_processing.py, api/models.py, console/forms.py, console/templates/console/organization_detail.html, console/templates/partials/_org_invite_modal.html, console/views.py, constants/stripe.py, pages/signals.py, tests/unit/test_organizations.py, tests/unit/test_pages_signals.py
  Purpose and Scope
  Data Model Overview
    · Core Models and Relationships
    · Organization Model
    · OrganizationMembership Model
    · Role Permission Matrix
  Invitation System
    · OrganizationInvite Model
    · Invitation Flow Sequence
    · Seat Reservation Logic
  Seat-Based Billing
    · OrganizationBilling Model
    · Seat Purchase Flow
    · Overage SKU Management
  Credit Provisioning for Organizations
    · Subscription Webhook Handler
    · TaskCreditService for Organizations
  Organization-Owned Resources
    · Persistent Agents
    · API Keys
  Console Context Switching
    · Context Resolution
    · Context-Aware Views
  Database Schema Summary
    · Key Constraints and Indexes
  Usage Example: Organization Lifecycle
    · 1. Create Organization
    · 2. Add Founder as Owner
    · 3. Purchase Seats via Stripe
    · 4. Invite Team Member
    · 5. Accept Invitation
    · 6. Create Organization-Owned Agent

## · Agent Management  (L4811)
  源文件: agents/services.py, api/agent/core/event_processing.py, api/models.py, console/templates/partials/_agent_contact_form.html, console/views.py, pages/templates/ai_directory/detail.html, pages/templates/ai_directory/index.html, pages/templates/home.html, pages/views.py, tests/unit/test_agent_limits.py, tests/unit/test_ai_employee_directory.py, tests/unit/test_console_context.py
  Purpose and Scope
  Core Data Models
    · Dual-Agent Architecture
    · PersistentAgent Fields
    · BrowserUseAgent Fields
  Agent Provisioning Flow
    · Provisioning Sequence
    · Provisioning Service Methods
  Agent Quota System
    · Quota Enforcement Layers
    · UserQuota Model
    · Validation Hooks
  Ownership Models: Personal vs Organization
    · Ownership Resolution
    · Context Switching
  AI Employee Templates
    · Template Data Model
    · AIEmployeeTemplateService
    · Schedule Jitter
  Agent Creation UI Flow
    · Creation Workflow
    · Session State Management
  Agent Limit Enforcement
    · Enforcement Points
    · Quota Calculation Logic
  Organization Agent Management
    · Organization Context Flow
    · Agent Filtering by Context
    · Role-Based Access Control
  Agent Lifecycle States
    · State Definitions
    · State Transitions
    · Soft Deletion
  Agent-to-Agent Communication
    · Peer Link Architecture
    · Quota Enforcement
  Summary

## · Creating Agents  (L5613)
  源文件: agents/services.py, api/agent/core/event_processing.py, api/models.py, console/templates/partials/_agent_contact_form.html, console/views.py, pages/templates/ai_directory/detail.html, pages/templates/ai_directory/index.html, pages/templates/home.html, pages/views.py, tests/unit/test_agent_limits.py, tests/unit/test_ai_employee_directory.py, tests/unit/test_console_context.py
  Purpose and Scope
  Agent Creation Flow Overview
    · High-Level Creation Sequence
  Entry Points
    · Homepage Charter Form
    · AI Employee Directory (Template-Based Creation)
  Contact Configuration Step
    · Contact Configuration Form Fields
    · Organization Context and Ownership
  Quota Enforcement
    · Quota Calculation Flow
    · Validation in BrowserUseAgent.clean()
  Agent Provisioning Service
    · Provisioning Service Interface
    · Provisioning Steps (Inferred)
    · Data Models Created
  Template Application
    · Template Default Application
  Post-Creation Event Queue
  Summary: Key Code Entities

## · Configuring Agents  (L6179)
  源文件: api/migrations/0155_persistentagent_daily_credit_limit_and_more.py, console/templates/console/agent_detail.html, console/templates/partials/_agent_list.html, tests/unit/test_agent_event_processing_credits.py, tests/unit/test_console.py
  Purpose and Scope
  Configuration Interface Overview
  Basic Settings
    · Agent Name
    · Charter (Assignment)
    · Active Status
  Credit & Resource Limits
    · Daily Credit Limit
    · Daily Credit UI Components
  Ownership & Context
    · User vs Organization Ownership
  Communication Settings
    · Email Configuration
    · SMS Configuration
    · Communication Allowlist
  Secrets Management
  Peer Links (Agent-to-Agent Communication)
    · Link Configuration
    · Quota Enforcement
    · UI Management
  Ownership Transfer
    · Transfer Flow
    · Invitation Creation
    · Pending Transfer State
  Deletion
    · Delete Flow
  Configuration Persistence

## · Agent Event Processing  (L6760)
  源文件: api/agent/core/event_processing.py, api/migrations/0155_persistentagent_daily_credit_limit_and_more.py, api/models.py, console/templates/console/agent_detail.html, console/templates/partials/_agent_list.html, console/views.py, tests/unit/test_agent_event_processing_credits.py, tests/unit/test_console.py
  Purpose and Scope
  System Overview
  Entry Point: `process_agent_events()`
    · Distributed Locking
    · Budget Context Management
  Credit Gating Architecture
    · Pre-Processing Credit Gate
    · Daily Credit Limit Calculation
    · Per-Tool Credit Gate
  The Agent Loop: `_run_agent_loop()`
    · Loop Structure
    · Prompt Building with Promptree
    · LLM Tier Selection
  LLM Completion with Failover
    · Failover Flow
    · Token Usage Tracking
    · Exponential Backoff Wrapper
  Tool Execution
    · Tool Type Dispatch
    · Browser Tasks
    · MCP Tool Execution
    · Communication Tools
  State Management
    · Step Recording
    · System Steps for Errors
    · Budget Cycle Closing
  Code Entity Reference
    · Key Functions
    · Key Models
    · Key Constants
  Testing

## · Agent Lifecycle  (L7266)
  源文件: AGENTS.md, api/exceptions.py, api/migrations/0145_browseruseagenttask_organization_and_more.py, api/migrations/0155_persistentagent_daily_credit_limit_and_more.py, api/serializers.py, api/services/persistent_agents.py, api/urls.py, api/views.py, console/templates/console/agent_detail.html, console/templates/partials/_agent_list.html, tests/unit/test_agent_event_processing_credits.py, tests/unit/test_api.py
  Agent Lifecycle States
    · Life State Enumeration
    · Activation Flag
  State Transition Diagram
  Activation and Deactivation
    · User-Initiated Activation Toggle
  Soft Deletion (API DELETE)
    · Soft Delete Behavior
    · Why Soft Delete?
  Hard Deletion (Console UI)
    · Hard Delete Flow
    · Deletion Safeguards
  Lifecycle Hooks and Side Effects
    · On Agent Creation
    · On Activation
    · On Deactivation
    · On Soft Deletion
    · On Hard Deletion
  Daily Credit Limits and Lifecycle
    · Daily Limit Lifecycle
    · Daily Limit Enforcement
    · Daily Limit Configuration
  Agent Ownership Transfer Lifecycle
    · Transfer States
    · Transfer Lifecycle Details
  Lifecycle Code Entities Reference
    · Key Models
    · Key Service Methods
    · Key Tests
  Summary

## · Credit & Billing System  (L7664)
  源文件: api/migrations/0115_persistentagentstep_credits_fields.py, console/forms.py, console/templates/console/organization_detail.html, console/templates/partials/_org_invite_modal.html, constants/stripe.py, pages/signals.py, tasks/services.py, tests/unit/test_organizations.py, tests/unit/test_pages_signals.py, tests/unit/test_persistent_agent_step_credits.py, tests/unit/test_task_credit_service.py, tests/unit/test_tool_costs.py
  Purpose and Scope
  Architecture Overview
  Core Data Models
    · TaskCredit
    · Billing Models
  TaskCreditService
    · Credit Granting
    · Credit Consumption
    · Entitlement Calculation
  Subscription Lifecycle Management
    · Stripe Webhook Processing
    · Subscription Cancellation
  Organization Billing
    · Seat Purchase Flow
    · Seat Reduction and Scheduling
    · Overage SKU Management
  Usage Tracking and Metering
    · Credit Consumption Tracking
    · Threshold Notifications
    · Stripe Metering (Overage Billing)
  Configuration and Customization
    · TaskCreditConfig (Singleton)
    · ToolCreditCost (Per-Tool Overrides)
    · Community Edition Unlimited Mode
  Error Handling and Edge Cases
    · Negative Available Credits
    · Concurrent Consumption Race Conditions
    · Expired Credits
    · Voided Credits
  Key Methods Reference

## · TaskCreditService  (L8381)
  源文件: api/migrations/0115_persistentagentstep_credits_fields.py, tasks/services.py, tests/unit/test_persistent_agent_step_credits.py, tests/unit/test_task_credit_service.py, tests/unit/test_tool_costs.py, util/tool_costs.py
  Purpose and Scope
  Core Concepts
    · TaskCredit Model
    · Owner Model
    · Credit Types
    · Fractional Credits
  Architecture Overview
  Credit Granting
    · Subscription-Based Granting for Users
    · Subscription-Based Granting for Organizations
  Credit Consumption
    · Atomic Consumption with SELECT FOR UPDATE
    · Fractional Consumption
    · Additional Tasks (Overage Credits)
    · Check-and-Consume Pattern
  Owner-Aware Operations
    · Dual Ownership Detection
    · Owner-Polymorphic Methods
    · Organization-Specific Differences
  Credit Calculations
    · Available Tasks Calculation
    · Percentage Used Calculation
  Tool Credit Costs
    · Configurable Cost System
    · Channel-Based Cost Lookup
    · Most Expensive Tool Cost
  Threshold Notifications
  Community Edition Mode
    · Unlimited Credits Flag
  Integration Points
    · Agent Event Processing
    · PersistentAgentStep Credit Linking
    · Stripe Metering Integration
  Database Schema Relationships

## · Subscription Management  (L9092)
  源文件: console/forms.py, console/templates/console/organization_detail.html, console/templates/partials/_org_invite_modal.html, constants/stripe.py, pages/signals.py, tests/unit/test_organizations.py, tests/unit/test_pages_signals.py
  Purpose and Scope
  System Overview
    · High-Level Flow
  Webhook Event Handler
    · Event Processing Pipeline
    · Subscription Sync with Fallback
  Owner Resolution
  Subscription Lifecycle Events
    · Deletion Events (`customer.subscription.deleted`)
    · Active Subscriptions (`status == 'active'`)
  User Subscription Handling
    · Billing Cycle Anchor Alignment
  Organization Subscription Handling
    · Seat Quantity Extraction
    · Credit Granting Logic by Billing Reason
    · Billing Record Updates
  Overage SKU Management
    · Overage Item Attachment
    · Detached Pending State
  Billing Reason Extraction
  Helper Functions for Data Extraction
    · `_get_stripe_data_value(container, key)`
    · `_coerce_datetime(value)`
    · `_coerce_bool(value)`
  Integration with Credit System
    · User Credit Grant
    · Organization Credit Grant
  Observability and Tracing
  Error Handling
  Test Coverage
    · User Subscription Tests
    · Organization Subscription Tests
  Configuration Dependencies
    · Stripe Settings
    · Plan Configuration
  Analytics Integration
  Summary

## · Organization Billing  (L9718)
  源文件: console/forms.py, console/templates/console/organization_detail.html, console/templates/partials/_org_invite_modal.html, constants/stripe.py, pages/signals.py, tests/unit/test_organizations.py, tests/unit/test_pages_signals.py
  Purpose and Scope
  Seat-Based Billing Model
    · Key Concepts
  OrganizationBilling Model
    · Core Fields
    · Pending Seat Changes
  Seat Purchase Flows
    · Diagram: Seat Checkout Decision Tree
    · Initial Purchase (No Existing Subscription)
    · Adding Seats to Existing Subscription
    · Overage SKU Detachment During Portal Updates
  Seat Reduction with Subscription Schedules
    · Diagram: Seat Reduction Flow
    · Schedule Creation Process
    · Replacing Existing Schedules
    · Canceling Pending Reductions
  Overage SKU Management
    · Configuration
    · Automatic Attachment on Subscription Creation/Update
    · Attachment Logic
    · Detached Pending State
  Webhook Processing for Organizations
    · Diagram: Webhook Flow for Organizations
    · Organization Identification
    · Billing Reason and Credit Granting
    · Billing Reason Resolution
    · Subscription Field Updates
    · Pending Seat Change Clearance
  UI Integration
    · Organization Detail Page
    · Seat Availability Checks
  Integration with TaskCreditService
  Error Handling and Edge Cases
    · Missing Billing Record
    · Portal Failure Fallback
    · Auto-Paging Iterator Errors
  Summary

## · Usage Analytics  (L10304)
  源文件: config/urls.py, console/usage_views.py, frontend/src/components/usage/types.ts, frontend/src/screens/UsageScreen.tsx, tests/unit/test_usage_trends_api.py
  Purpose and Scope
  Core Concepts
    · API Agent
    · Data Sources
    · Context Awareness
  API Endpoints
    · Endpoint Overview
    · Summary Endpoint
    · Trend Endpoint
    · Tool Breakdown Endpoint
    · Leaderboard Endpoint
    · Agents List Endpoint
  Data Flow Architecture
  Query Construction Patterns
    · Agent Filtering
    · Credit Expression
  Frontend Integration
    · UsageScreen Component
    · Date Range Handling
    · State Synchronization
  Testing Strategy
    · Key Test Cases
  Common Query Patterns
    · Filtering by Agent
    · Custom Date Range
    · Organization Context
  Performance Considerations

## · Tool Integration  (L10935)
  源文件: api/agent/core/llm_config.py, api/agent/tools/mcp_manager.py, api/agent/tools/mcp_tools.py, api/integrations/pipedream_connect.py, api/migrations/0127_pipedream_connect_session.py, api/migrations/0137_add_trello_tool_friendly_names.py, api/tasks/browser_agent_tasks.py, tests/unit/test_browser_task_follow_up.py, tests/unit/test_event_processing_llm_selection.py, tests/unit/test_llm_failover.py, tests/unit/test_mcp_tools.py, tests/unit/test_pipedream_connect.py
  Overview
  System Architecture
    · High-Level Component Interaction
  MCP Tool Integration
    · Tool Discovery and Enablement Flow
    · Tool Execution
  Pipedream OAuth Integration
    · Connect Link Flow
  Browser Automation
    · Browser Task Execution Architecture
    · Browser Task Follow-Up
  LLM Provider Integration
    · Token-Based Tier Selection
    · LLM Failover Execution
  Configuration
    · MCP Server Configuration
    · Tool Blacklist
    · Browser Configuration
  Integration Patterns
    · Tool Discovery Pattern
    · Tool Execution Pattern
    · Browser Automation Pattern
  Limitations and Constraints
    · MCP Tool Limits
    · Browser Automation Limits
    · LLM Integration Limits
  Testing

## · MCP Tools  (L11662)
  源文件: api/agent/tools/mcp_manager.py, api/integrations/pipedream_connect.py, api/migrations/0127_pipedream_connect_session.py, api/migrations/0137_add_trello_tool_friendly_names.py, tests/unit/test_pipedream_connect.py, tests/unit/test_pipedream_greenhouse.py, tests/unit/test_pipedream_trello.py
  Purpose and Scope
  Overview
  System Architecture
    · Core Components
  MCP Server Configuration
    · Available Servers
    · Server Dataclass Structure
    · Bright Data Configuration
    · Pipedream Configuration
  Tool Discovery and Enablement
    · Discovery Flow
    · Tool Catalog Format
    · LRU Eviction Policy
  Tool Blacklisting
  Tool Naming Conventions
    · Prefixed vs Unprefixed
  Tool Execution
    · Execution Flow
    · Usage Tracking
  Pipedream Connect OAuth Flow
    · Architecture
    · Connect Link Detection
    · Session Reuse Logic
    · Expired Link Handling
  Per-Agent Pipedream Clients
    · Client Cache Key
    · Headers for Per-Agent Clients
  Tool Information Dataclass
  Default Enabled Tools
  Token Management for Pipedream
    · OAuth Client Credentials Flow
  Initialization and Cleanup
    · Initialization
    · Cleanup
  Database Models
    · PersistentAgentEnabledTool
    · PipedreamConnectSession
  API Functions
    · Core Functions
    · Manager Methods
  Example: Tool Discovery and Execution
    · Step 1: Agent Searches for Tools
    · Step 2: Tools Are Enabled
    · Step 3: Agent Executes Tool
  Testing
    · Test Coverage
  Configuration Reference
    · Environment Variables
  Logging and Observability

## · Browser Automation  (L12474)
  源文件: api/agent/core/llm_config.py, api/agent/tools/mcp_tools.py, api/tasks/browser_agent_tasks.py, tests/unit/test_browser_task_follow_up.py, tests/unit/test_event_processing_llm_selection.py, tests/unit/test_llm_failover.py, tests/unit/test_mcp_tools.py, tests/utils/llm_seed.py
  Purpose and Scope
  Architecture Overview
  Task Execution Pipeline
    · Task Creation and Queuing
    · Execution Context
  Chrome Profile Management
    · Profile Storage Architecture
    · Profile Restore Process
    · Profile Pruning and Persistence
    · Secure Tar Extraction
  LLM Provider Selection
    · Multi-Tier Failover Architecture
    · Default Provider Tiers
    · Backend Configuration
    · Vision Support
  Proxy Configuration
    · Proxy Selection Logic
    · Proxy Settings Configuration
    · Observability
  File Upload and Download
    · File Upload Configuration
    · File Download Handling
  Follow-up Scheduling
    · Budget Cycle Continuity
    · Follow-up Parameters
  Configuration Reference
    · Environment Variables
    · LLM Provider Environment Variables
    · Google Vertex AI Configuration
    · Profile Pruning Constants

## · LLM Integration  (L13061)
  源文件: api/agent/core/llm_config.py, api/agent/tools/mcp_tools.py, api/tasks/browser_agent_tasks.py, tests/unit/test_browser_task_follow_up.py, tests/unit/test_event_processing_llm_selection.py, tests/unit/test_llm_failover.py, tests/unit/test_mcp_tools.py, tests/utils/llm_seed.py
  Purpose and Scope
  Architecture Overview
  Provider Configuration
    · PROVIDER_CONFIG Structure
    · Vision Support Metadata
  Tiered Failover System
    · Token-Based Tier Selection
    · Weighted Provider Distribution
  Database-Backed Configuration
    · Schema Overview
    · OpenAI-Compatible Endpoint Support
    · API Key Resolution
  Browser Automation LLM Integration
    · Native Client Instantiation
    · Browser LLM Policy
  Persistent Agent LLM Integration
    · LiteLLM Wrapper
    · Tool Choice and Parallel Calls
    · Reference Tokenizer
  Failover Execution Flow
  Configuration Management
    · Bootstrap Flow
    · LLMNotConfiguredError
    · Cache Invalidation
  Integration Points Summary

## · Communication Systems  (L13560)
  源文件: .github/workflows/ci.yml, api/agent/peer_comm.py, api/agent/peer_link_signals.py, api/agent/tools/peer_dm.py, api/apps.py, api/migrations/0151_agentcommpeerstate_agentpeerlink_and_more.py, frontend/src/components/agentChat/AgentChatLayout.tsx, frontend/src/screens/AgentChatPage.tsx, frontend/src/stores/agentChatStore.ts, frontend/src/styles/agentChatLegacy.css, tests/unit/test_agent_short_description.py, tests/unit/test_peer_agent_messaging.py
  Communication Architecture Overview
    · Channel Overview
  Communication Flow Diagram
  Web Chat System
    · Frontend Architecture
    · Timeline Event Structure
    · Auto-Scroll System
    · Message Send Flow
    · Processing Indicator
  Email & SMS Communication
    · Email Infrastructure
    · SMS Infrastructure
    · Allowlist System
  Peer Messaging System
    · Peer Link Model
    · Peer Messaging Flow
    · Rate Limiting & Quota Management
    · Debouncing & Anti-Loop Protection
    · Lifecycle Integration
    · Tool Interface
    · Peer Link Creation Signal
  Message Storage Schema
  Testing Strategy

## · Agent Web Chat  (L14146)
  源文件: frontend/src/components/agentChat/AgentChatLayout.tsx, frontend/src/screens/AgentChatPage.tsx, frontend/src/stores/agentChatStore.ts, frontend/src/styles/agentChatLegacy.css
  Purpose and Scope
  Architecture Overview
  Timeline Event Model
    · Event Types
    · Event Normalization and Merging
  Real-time Communication
    · WebSocket Connection
    · Processing Status Updates
  Message Flow: User to Agent
  State Management Architecture
    · useAgentChatStore
    · Pagination System
  Auto-scroll System
    · Scroll Pinning Mechanism
    · Pending Events Queue
    · Auto-scroll Suppression
  Processing Indicators
    · Active Processing State
    · Browser Task Cards
  Timeline Rendering
    · AgentChatLayout Component
    · Conditional Rendering Logic
  Event Styling and Animation
    · Message Bubbles
    · Incoming Animation
  Web Session Management

## · Email & SMS  (L14573)
  源文件: api/admin.py, api/agent/core/event_processing.py, api/models.py, config/settings.py, console/views.py, util/subscription_helper.py
  Overview
  Email System Architecture
    · Email Account Model
    · Email Delivery Modes
    · Inbound Email Processing
    · Outbound Email Sending
  SMS System Architecture
    · SMS Number Provisioning
    · Inbound SMS Processing
    · Outbound SMS Sending
  Communication Endpoints
    · Endpoint Hierarchy
    · Endpoint Lifecycle
  Allowlist System
    · CommsAllowlistEntry Model
    · Directional Permissions
    · Allowlist Policies
    · Allowlist Enforcement
  Message Processing
    · PersistentAgentMessage Model
    · Conversation Threading
    · Message Compaction
  Agent Communication Tools
    · send_email Tool
    · send_sms Tool
  Configuration Reference
    · Email Provider Settings
    · IMAP/SMTP Settings
    · IMAP IDLE Watcher Settings
    · SMS/Twilio Settings
    · Email Parsing Settings
  Admin Interface
    · AgentEmailAccount Admin
    · SMS Number Admin
    · CommsAllowlistEntry Admin
  Integration Examples
    · Email Account Setup Flow
    · SMS Number Provisioning Flow
    · Message Webhook Processing Flow
  Security Considerations
    · Credential Storage
    · Webhook Authentication
    · Allowlist Enforcement
    · Rate Limiting
  Troubleshooting
    · Email Not Sending
    · Email Not Received
    · SMS Not Sending
    · SMS Not Received
  Related Systems

## · Peer Messaging  (L15585)
  源文件: .github/workflows/ci.yml, api/agent/peer_comm.py, api/agent/peer_link_signals.py, api/agent/tools/peer_dm.py, api/apps.py, api/migrations/0151_agentcommpeerstate_agentpeerlink_and_more.py, tests/unit/test_agent_short_description.py, tests/unit/test_peer_agent_messaging.py
  Purpose and Scope
  Overview
  Core Data Models
    · Model Relationship Diagram
    · AgentPeerLink
    · AgentCommPeerState
    · PersistentAgentMessage Extensions
  Message Flow
    · Sequence Diagram: Sending a Peer Message
    · PeerMessagingService._lock_state() Logic
  Quota and Rate Limiting
    · Rolling Window Quota
    · Debouncing
    · Quota Exhaustion Handling
    · Quota Configuration Table
  Tool Integration
    · send_agent_message Tool Schema
    · execute_send_agent_message() Function
  Lifecycle Integration
    · Waking Expired Agents
    · Automatic Event Processing
  Conversation Threading
    · PersistentAgentConversation for Peer DMs
    · PersistentAgentCommsEndpoint
  Error Handling
    · PeerMessagingError Exception
    · Status Codes
  Signal Handlers
    · AgentPeerLink Post-Save Signal
  Testing Strategy
    · Test Batches
    · Key Test Cases
  Configuration and Setup
    · Creating a Peer Link
    · Feature Flags
    · Disabling a Link
  Architecture Summary Diagram

## · User Interfaces  (L16203)
  源文件: agents/services.py, api/agent/core/event_processing.py, api/models.py, console/templates/partials/_agent_contact_form.html, console/views.py, pages/templates/ai_directory/detail.html, pages/templates/ai_directory/index.html, pages/templates/home.html, pages/views.py, tests/unit/test_agent_limits.py, tests/unit/test_ai_employee_directory.py, tests/unit/test_console_context.py
  UI Layer Architecture
  Console Interface
    · ConsoleHome Dashboard
    · Context Switching System
    · API Key Management
    · Billing Views
  Homepage & AI Employee Directory
    · Homepage Agent Spawn
    · AI Employee Directory
  Agent Creation Flow
    · Multi-Step Process
    · Contact Form View
    · Organization Permission Enforcement
  UI-Backend Integration Patterns
    · Session Management
    · Analytics Tracking
    · HTMX Interaction Pattern
  Template Organization
  Key UI Components
    · Agent Listings
    · Credit Usage Widget
  Summary

## · Console Interface  (L16777)
  源文件: api/agent/core/event_processing.py, api/models.py, console/views.py
  Architecture Overview
  Console Context Resolution
  ConsoleHome Dashboard
    · Dashboard Metrics Query
  API Key Management
    · API Key Views
    · Role-Based Permissions
    · API Key Creation Flow
  Billing & Subscription Management
    · Personal Billing
    · Organization Billing
    · Organization Seat Management
  Task Management Views
    · tasks_view
    · task_detail_view
    · task_result_view
  Agent Management Views
    · PersistentAgentsView
    · Agent Lifecycle Actions
  HTMX Integration
    · HTMX Response Patterns
  Analytics Integration
    · Organization Event Tracking
    · Tracked Events
  Billing Update Endpoints
    · update_billing_settings
    · get_billing_settings
  Profile Management
  Context Switching Flow
  Security & Permission Enforcement
    · Organization Role Hierarchy
    · Permission Denial Patterns
  Stripe Integration Points
    · Overage SKU Detachment
    · Overage SKU Reattachment

## · Homepage & AI Employee Directory  (L17497)
  源文件: agents/services.py, console/templates/partials/_agent_contact_form.html, pages/templates/ai_directory/detail.html, pages/templates/ai_directory/index.html, pages/templates/home.html, pages/views.py, tests/unit/test_agent_limits.py, tests/unit/test_ai_employee_directory.py, tests/unit/test_console_context.py
  Purpose and Scope
  Homepage Structure
    · Main Components
    · Charter Input Form
    · Recent Agents Section
    · Game of Life Animation
  AI Employee Directory
    · Directory Index
    · Template Cards
    · Template Detail Page
  Template System Architecture
    · AIEmployeeTemplateService
    · Schedule Jitter
    · Cron Description
  Agent Creation Flow
    · Template Hire Flow
    · Session State Management
    · Context Switching
  Search and Filtering
    · Directory Filters
  Analytics Integration
  Template Model Structure
  Landing Page Integration
  Agent Quota Display

## · Agent Chat Interface  (L18125)
  源文件: frontend/src/components/agentChat/AgentChatLayout.tsx, frontend/src/screens/AgentChatPage.tsx, frontend/src/stores/agentChatStore.ts, frontend/src/styles/agentChatLegacy.css
  Purpose and Scope
  Architecture Overview
  State Management with agentChatStore
    · Store Structure
    · Timeline Window Management
    · Event Normalization and Merging
    · Cursor Format and Sorting
  Layout Components
    · AgentChatLayout
    · AgentComposer
    · ProcessingIndicator
  Auto-Scroll System
    · Pinned vs Unpinned States
    · IntersectionObserver Integration
    · Scroll Position Tracking
    · Auto-Scroll Suppression
    · Pending Events Queue
  Timeline Event Processing
    · Event Types
    · Real-Time Event Reception
    · Message Sending Flow
  Real-Time Integration
    · WebSocket Connection
    · Processing Status Polling
  Processing Indicator Display
    · Task Card Structure
    · Expandable Behavior
  CSS Architecture
    · ID-Based Styling
    · Data Attributes for State
    · Animation System
  Responsive Behavior
  Initialization and Lifecycle
    · Page Initialization Flow
    · Cleanup and Unmount
  Jump to Latest Functionality
  Timeline Navigation Controls
    · Load Older Button
    · Load Newer Button
    · Loading States

## · API Reference  (L18882)
  源文件: AGENTS.md, api/exceptions.py, api/migrations/0145_browseruseagenttask_organization_and_more.py, api/serializers.py, api/services/persistent_agents.py, api/urls.py, api/views.py, tests/unit/test_api.py, tests/unit/test_api_persistent_agents.py
  Purpose and Scope
  API Overview
    · Base Configuration
    · Error Handling
  Authentication Model
  API Request Flow
  Endpoint Architecture
    · Dual-Scoped Task Endpoints
  Resource Ownership and Filtering
  Request Validation and Serialization
    · Serializer Pairs
    · Field Validation Examples
  Wait Parameter and Synchronous Results
  Credit Gating
  Pagination
  Soft Deletion
  OpenAPI Schema Generation
  Webhook Endpoints
  Common Response Patterns
    · Success Responses
    · Error Responses
  Analytics Tracking

## · REST API  (L19328)
  源文件: AGENTS.md, api/exceptions.py, api/migrations/0145_browseruseagenttask_organization_and_more.py, api/serializers.py, api/services/persistent_agents.py, api/urls.py, api/views.py, tests/unit/test_api.py, tests/unit/test_api_persistent_agents.py
  Purpose and Scope
  Base URL and Versioning
  Authentication
  URL Routing Architecture
  Core ViewSets and Serializers
  Resource: Browser-Use Agents
    · Endpoints
    · List Browser Agents
    · Create Browser Agent
  Resource: Persistent Agents
    · Endpoints
    · Create Persistent Agent
    · Update Persistent Agent
    · Soft Delete Agent
    · Timeline Endpoint
    · Messages Endpoint
    · Processing Status Endpoint
  Resource: Browser-Use Tasks
    · Endpoints
    · Create Task Flow
    · Create Task (Synchronous)
    · Secrets Encryption
    · Get Task Result
    · Cancel Task
    · Update Task (Pending Only)
  Pagination
  Error Handling
    · Error Response Format
    · HTTP Status Codes
    · Validation Error Example
    · Unhandled Exception Format
  Ownership Filtering
  Special Endpoints
    · Ping
    · Schedule Preview
  Rate Limiting and Quotas
    · Credit Gating
    · Agent Quotas
  Common Request Patterns
    · Create Agent + Submit Task
    · Poll Task Status
    · Send Message to Agent
  Testing
  Related Documentation

## · Authentication & Authorization  (L20506)
  源文件: AGENTS.md, api/agent/core/event_processing.py, api/exceptions.py, api/migrations/0145_browseruseagenttask_organization_and_more.py, api/models.py, api/serializers.py, api/services/persistent_agents.py, api/urls.py, api/views.py, console/views.py, tests/unit/test_api.py, tests/unit/test_api_persistent_agents.py
  Overview
  API Key Model
    · Dual-Ownership Structure
    · Key Limits
  Authentication Flow
    · Request Authentication
  Dual-Ownership Model
    · Resource Ownership Architecture
    · Ownership Resolution Pattern
  Permission Enforcement
    · Organization Roles
    · Resource Access Control
    · Validation in Serializers
  API Key Management
    · Console-Based Management
    · Key Generation
  API Restrictions by Key Type
    · Organization Key Restrictions
  Credit System Integration
    · Owner-Aware Credit Operations
  Implementation Examples
    · Console API Key Creation
    · Task Creation with Organization Key
    · Queryset Filtering by Ownership
  Database Constraints
    · XOR Ownership Enforcement
  Testing
    · Organization API Key Tests
  Summary

## · Development & Administration  (L20979)
  源文件: .github/workflows/ci.yml, api/admin.py, api/agent/peer_comm.py, api/agent/peer_link_signals.py, api/agent/tools/peer_dm.py, api/apps.py, api/migrations/0151_agentcommpeerstate_agentpeerlink_and_more.py, config/settings.py, tests/unit/test_agent_short_description.py, tests/unit/test_peer_agent_messaging.py, util/subscription_helper.py
  Configuration Management
    · Settings Architecture
    · Proprietary Defaults System
    · Environment Variable Categories
  Django Admin Interface
    · Custom Admin Architecture
    · Bulk Credit Granting
    · Proxy Management Actions
    · Inline Admin Optimizations
    · Custom Admin Forms
  Testing Infrastructure
    · Tag-Based Test Organization
    · Test Batching Strategy
    · Test Settings
    · Running Tests Locally
  CI/CD Pipeline
    · GitHub Actions Workflow
    · Dependency Caching
    · Test Execution
    · Combined Test Reporting
    · Concurrency Control
  Development Workflows
    · Local Development Setup
    · Admin Access Patterns
    · Test Development Guidelines
  Configuration Reference
    · Critical Environment Variables
    · Feature Flags
    · Deployment Modes
  Troubleshooting
    · Common Development Issues
    · Admin Performance Issues

## · Django Admin Interface  (L21637)
  源文件: api/admin.py, config/settings.py, util/subscription_helper.py
  Purpose and Scope
  Admin Architecture Overview
  Credit and Billing Admins
    · TaskCreditAdmin
    · TaskCreditConfigAdmin and ToolCreditCostAdmin
    · MeteringBatchAdmin
  Agent Management Admins
    · BrowserUseAgentAdmin
    · BrowserUseAgentTaskAdmin
    · PersistentAgentAdmin
  Proxy and Infrastructure Admins
    · DecodoIPBlockAdmin
    · ProxyServerAdmin
  User and Organization Admins
    · CustomUserAdmin
  Admin Forms
    · GrantPlanCreditsForm
  Performance Patterns
    · Query Optimization Techniques
  Template Customizations
    · Custom Change List Templates
  Custom URL Patterns
  Stripe Integration Patching
  Summary

## · Testing & CI/CD  (L22271)
  源文件: .github/workflows/ci.yml, api/agent/peer_comm.py, api/agent/peer_link_signals.py, api/agent/tools/peer_dm.py, api/apps.py, api/migrations/0151_agentcommpeerstate_agentpeerlink_and_more.py, tests/unit/test_agent_short_description.py, tests/unit/test_peer_agent_messaging.py
  Purpose and Scope
  Test Structure and Tagging
    · Tag-Based Batching
    · Tag Naming Conventions
  Test Batch Categories
    · Communication and Messaging
    · Agent Lifecycle and Processing
    · API and Serialization
    · Billing and Credits
    · Browser Automation
    · Tool Integration
    · Infrastructure and Utilities
    · Console and UI
    · Other Features
  CI/CD Pipeline Architecture
    · Workflow Overview
    · Job Definitions
  Environment Configuration
    · Test Settings Override
    · Environment Variables
  Dependency Management with uv
  Test Execution
    · Running Tests in CI
    · XML Output Collection
  Test Examples and Patterns
    · Example: Peer Messaging Tests
    · Mocking Celery Tasks
    · Testing Error Conditions
  CI Workflow Execution Diagram
  Concurrency Control
  Permissions
  Test Result Reporting
    · Artifact Storage
    · Combined Reporting
  Running Tests Locally
    · Running All Tests
    · Running a Specific Batch
    · Running a Specific Test
    · Running with Coverage
  Test Infrastructure Components
    · Key Testing Files and Modules
    · Test Runner Configuration
  Summary