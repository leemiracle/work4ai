# Skeleton: agentdock（35 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 13KB | 5 | ~0 | 11 |
| 2 | Project Structure | L384 | 11KB | 6 | ~3 | 9 |
| 3 | Key Concepts | L733 | 13KB | 6 | ~2 | 13 |
| 4 | Architecture | L1108 | 14KB | 11 | ~2 | 9 |
| 5 | Node System | L1525 | 16KB | 8 | ~0 | 9 |
| 6 | LLM Integration | L2066 | 13KB | 10 | ~3 | 11 |
| 7 | Orchestration System | L2459 | 15KB | 8 | ~5 | 5 |
| 8 | Session Management | L2867 | 13KB | 15 | ~1 | 4 |
| 9 | Storage Abstraction | L3372 | 14KB | 7 | ~1 | 8 |
| 10 | AgentDock Core | L3751 | 15KB | 10 | ~2 | 8 |
| 11 | AgentNode | L4261 | 16KB | 10 | ~6 | 8 |
| 12 | Tool Registry | L4723 | 15KB | 5 | ~4 | 8 |
| 13 | LLM Orchestration Service | L5234 | 10KB | 7 | ~3 | 6 |
| 14 | Provider Registry | L5550 | 13KB | 6 | ~2 | 10 |
| 15 | OSS Client | L5944 | 12KB | 7 | ~3 | 8 |
| 16 | UI Components | L6327 | 14KB | 7 | ~0 | 9 |
| 17 | Chat Interface | L6732 | 14KB | 6 | ~0 | 7 |
| 18 | API Routes | L7208 | 8KB | 5 | ~4 | 6 |
| 19 | Layout System | L7455 | 12KB | 7 | ~0 | 9 |
| 20 | Settings Page | L7816 | 11KB | 6 | ~2 | 9 |
| 21 | Documentation System | L8136 | 12KB | 9 | ~0 | 7 |
| 22 | Analytics Integration | L8484 | 12KB | 5 | ~1 | 9 |
| 23 | Agents and Tools | L8870 | 13KB | 5 | ~7 | 12 |
| 24 | Agent Templates | L9273 | 14KB | 3 | ~2 | 9 |
| 25 | Custom Tools | L9682 | 16KB | 7 | ~2 | 7 |
| 26 | Deep Research Tool | L10150 | 12KB | 4 | ~1 | 8 |
| 27 | Search and API Tools | L10515 | 13KB | 8 | ~3 | 9 |
| 28 | Development Guide | L10891 | 11KB | 5 | ~8 | 4 |
| 29 | Environment Setup | L11313 | 10KB | 9 | ~8 | 6 |
| 30 | API Keys Management | L11684 | 11KB | 4 | ~5 | 11 |
| 31 | Build System | L11965 | 10KB | 8 | ~10 | 8 |
| 32 | Contributing Guidelines | L12324 | 11KB | 6 | ~0 | 3 |
| 33 | Internationalization | L12710 | 10KB | 6 | ~7 | 13 |
| 34 | i18n Structure | L12997 | 10KB | 5 | ~5 | 13 |
| 35 | Adding New Translations | L13264 | 6KB | 3 | ~2 | 9 |


## · Overview  (L6)
  源文件: .gitignore, docs/i18n/README.md, docs/i18n/arabic/README.md, docs/i18n/chinese/README.md, docs/i18n/deutsch/README.md, docs/i18n/dutch/README.md, docs/i18n/french/README.md, docs/i18n/greek/README.md, package.json, pnpm-lock.yaml, scripts/generate-favicons.js
  Repository Structure
  High-Level Architecture
  Core Concepts
    · Node-Based Architecture
    · Configurable Determinism
  Message Processing Pipeline
  Agent Configuration and Execution Flow
  Key Components
    · AgentDock Core
    · Open Source Client
    · Environment Requirements
  API Key Resolution
  Further Reading

## · Project Structure  (L384)
  源文件: .gitignore, agentdock-core/package.json, agentdock-core/pnpm-lock.yaml, agentdock-core/src/nodes/agent-node.ts, agentdock-core/tsconfig.json, package.json, pnpm-lock.yaml, scripts/clean-install.sh, scripts/generate-favicons.js
  Repository Overview
  Core Framework Structure
    · Directory Structure
    · Key Modules
  OSS Client Structure
    · Directory Structure
  Build System and Scripts
    · Core Build Process
    · Key Scripts
  Dependency Management
    · Core Framework Dependencies
    · Client Dependencies
  Scripts Directory
  Project Structure Visualization

## · Key Concepts  (L733)
  源文件: docs/i18n/README.md, docs/i18n/arabic/README.md, docs/i18n/chinese/README.md, docs/i18n/deutsch/README.md, docs/i18n/dutch/README.md, docs/i18n/french/README.md, docs/i18n/greek/README.md, docs/i18n/italian/README.md, docs/i18n/japanese/README.md, docs/i18n/korean/README.md, docs/i18n/polish/README.md, docs/i18n/russian/README.md
  Configurable Determinism
    · The Determinism Spectrum
    · Hybrid Workflow Example
  Node-Based Architecture
    · Core Node Types
    · Agent and Tool Relationship Model
  LLM Integration and Message Processing
    · LLM Integration and Message Processing Pipeline
  Agent Configuration and Execution Flow
    · Agent Configuration and Execution Flow
  Core System Components
    · Component Overview
    · High-Level System Architecture
  Further Reading

## · Architecture  (L1108)
  源文件: agentdock-core/package.json, agentdock-core/pnpm-lock.yaml, agentdock-core/src/nodes/agent-node.ts, agentdock-core/tsconfig.json, docs/i18n/chinese/README.md, docs/i18n/dutch/README.md, docs/i18n/french/README.md, docs/i18n/greek/README.md, scripts/clean-install.sh
  Core Design Philosophy
  High-Level System Overview
  Core Framework Components
    · Node System
    · LLM Integration
    · Orchestration System
    · Session Management
    · Tool Registry
    · Storage Abstraction
  OSS Client Architecture
  Message Processing Flow
  Agent Configuration and Execution Flow
  Integration with External Services
  Development Workflow
  Conclusion

## · Node System  (L1525)
  源文件: agentdock-core/package.json, agentdock-core/pnpm-lock.yaml, agentdock-core/src/nodes/agent-node.ts, agentdock-core/src/nodes/tool-registry.ts, agentdock-core/tsconfig.json, docs/analytics.md, scripts/clean-install.sh, src/app/agents/all/page.tsx, src/app/agents/page.tsx
  Core Concepts
    · Node Types
  BaseNode Interface
  AgentNode Implementation
    · AgentNode Configuration
    · Message Handling Flow
  Tool Registry
    · Key Features
    · Tool Registry Implementation
  Node System Integration
    · Node System in the Request Flow
  Node Relationships
  Node Configuration
    · Example Agent Template Configuration
  Summary

## · LLM Integration  (L2066)
  源文件: .env.example, agentdock-core/package.json, agentdock-core/pnpm-lock.yaml, agentdock-core/src/llm/index.ts, agentdock-core/src/llm/llm-orchestration-service.ts, agentdock-core/src/llm/types.ts, agentdock-core/src/nodes/agent-node.ts, agentdock-core/src/types/index.ts, agentdock-core/src/utils/message-utils.ts, agentdock-core/tsconfig.json, scripts/clean-install.sh
  Purpose and Scope
  Provider Architecture
  Core Components
    · CoreLLM
    · LLMOrchestrationService
  Message Processing Flow
  Provider Support
  Message Utilities
  API Key Management
  Token Usage Tracking
  Integration with AgentNode
  Fallback Mechanism
  Configuration Options
  Summary

## · Orchestration System  (L2459)
  源文件: .env.example, agentdock-core/src/llm/llm-orchestration-service.ts, src/components/chat/chat-container.tsx, src/components/chat/chat-status.tsx, src/hooks/use-session-info.ts
  1. Orchestration Architecture
  2. Orchestration State
  3. Tool Usage Tracking
  4. Token Usage Tracking
  5. LLM Orchestration Service
  6. Integration with API Routes
  7. Client-Side Integration
  8. Configuring Orchestration
  9. Environment Configuration
  Conclusion

## · Session Management  (L2867)
  源文件: src/components/chat/chat-container.tsx, src/components/chat/chat-status.tsx, src/components/layout/site-sidebar.tsx, src/hooks/use-session-info.ts
  Introduction
  Session Lifecycle
  Session Identification
    · Session ID Generation
    · Session Headers
  Session State Components
    · Session Data Structure
    · Orchestration State
    · Token Usage Tracking
    · Message History Management
  Session Persistence
    · Client-Side Storage
    · Session Data Loading
  Session Management API
    · useSessionInfo Hook
    · Session Reset Functionality
  Session State Updates
    · Headers-Based Updates
    · Stream Data Updates
  Error Handling
  Integration with System Components
    · Integration with Chat API Route
    · Integration with Tool Execution
    · Integration with UI Components
  Conclusion

## · Storage Abstraction  (L3372)
  源文件: .env.example, agentdock-core/src/llm/llm-orchestration-service.ts, src/app/settings/debug-panel.tsx, src/app/settings/model-display.tsx, src/app/settings/page.tsx, src/app/settings/types.ts, src/lib/models/registry.ts, src/lib/services/model-service.ts
  Overview
  Architecture
    · Storage Architecture Diagram
    · Provider Selection Flow
  Storage Providers
    · Redis Provider
    · Vercel KV Provider
    · Memory Provider
  Secure Storage Implementation
    · Secure Storage Usage Pattern
  Usage Patterns
    · API Key Management
    · Session State and Token Usage
  Background Task Support
  Time-to-Live (TTL) Support
  Integration with Other Components
  Security Considerations
  Conclusion

## · AgentDock Core  (L3751)
  源文件: agentdock-core/package.json, agentdock-core/pnpm-lock.yaml, agentdock-core/src/index.ts, agentdock-core/src/nodes/agent-node.ts, agentdock-core/tsconfig.json, scripts/clean-install.sh, src/lib/agent-adapter.ts, src/lib/core/init.ts
  1. Architecture Overview
    · Core Components Diagram
    · Position in Overall System Architecture
  2. Key Components
    · 2.1 Node System
    · 2.2 AgentNode
    · 2.3 LLM Integration
    · 2.4 Tool Registry
    · 2.5 Orchestration System
    · 2.6 Session Management
  3. Implementation Details
    · 3.1 Export Structure
    · 3.2 Message Processing Flow
    · 3.3 Configuration and Build System
  4. Usage Patterns
    · 4.1 Creating an Agent Node
    · 4.2 System Initialization
  5. Integration with External Systems
  Summary

## · AgentNode  (L4261)
  源文件: agentdock-core/package.json, agentdock-core/pnpm-lock.yaml, agentdock-core/src/index.ts, agentdock-core/src/nodes/agent-node.ts, agentdock-core/tsconfig.json, scripts/clean-install.sh, src/lib/agent-adapter.ts, src/lib/core/init.ts
  Overview
  Class Structure and Position in System Architecture
    · Agent Node Architecture
    · Position in System Architecture
  Configuration and Initialization
    · Configuration Structure
    · Initialization Process
  Message Processing Flow
    · handleMessage Flow
    · Key Components in Message Processing
  Tool Integration
    · Tool Selection Process
    · Tool Format for LLM
  LLM Integration and Fallback Mechanism
    · LLM Selection Logic
    · LLM API Key Resolution
  System Prompt Creation
    · System Prompt Generation
    · Date and Time Injection
  BaseNode Implementation
    · Key Methods
  Integration with Agent Adapter
  Error Handling
  Performance Considerations
  Conclusion

## · Tool Registry  (L4723)
  源文件: agentdock-core/src/nodes/tool-registry.ts, docs/analytics.md, src/app/agents/all/page.tsx, src/app/agents/page.tsx, src/nodes/init.ts, src/nodes/registry.ts, src/nodes/types.ts, src/nodes/weather/components.ts
  Overview
  Architecture
    · Core Components
    · Tool Registry Interface
    · DefaultToolRegistry Implementation
    · Singleton Pattern
  Tool Structure
    · Tool Interface
    · Tool Execution Context
  Tool Registration Process
    · Tool Validation
  Tool Collection
    · Available Tool Categories
  Usage in Agent System
    · Tool Retrieval for Agents
  Example Tool: Weather
  Debugging and Utility Functions
    · Error Handling
    · Debug Helpers
  Integration with Agent Templates
  Conclusion

## · LLM Orchestration Service  (L5234)
  源文件: .env.example, agentdock-core/src/llm/index.ts, agentdock-core/src/llm/llm-orchestration-service.ts, agentdock-core/src/llm/types.ts, agentdock-core/src/types/index.ts, agentdock-core/src/utils/message-utils.ts
  Purpose and Scope
  Architecture Overview
  Service Initialization
  Core Functionality
    · Stream Orchestration
    · Token Usage Tracking
    · Background Task Handling
  Tool Usage Tracking
  Integration with Messages and History
  Token Usage Structure
  Environment Configuration

## · Provider Registry  (L5550)
  源文件: agentdock-core/src/llm/index.ts, agentdock-core/src/llm/types.ts, agentdock-core/src/types/index.ts, agentdock-core/src/utils/message-utils.ts, src/app/settings/debug-panel.tsx, src/app/settings/model-display.tsx, src/app/settings/page.tsx, src/app/settings/types.ts, src/lib/models/registry.ts, src/lib/services/model-service.ts
  Architecture Overview
    · Provider Registry System Architecture
  Integration with AgentDock Core
    · LLM Integration Flow
  Supported LLM Providers
  Provider Metadata
  Provider-Specific Configurations
    · Configuration Types
  API Key Management
    · API Key Validation Flow
  Model Registry Integration
    · Model Fetching and Registration
  Implementation Details
    · LLM Provider Interface
    · Message Processing Flow
  Settings UI Integration
    · Settings Page API Key Management
  BYOK (Bring Your Own Key) Mode
  Conclusion

## · OSS Client  (L5944)
  源文件: package.json, pnpm-lock.yaml, scripts/generate-favicons.js, src/app/layout.tsx, src/components/layout/layout-content.tsx, src/components/providers/posthog-provider.tsx, src/lib/analytics.ts, tailwind.config.ts
  Overview
  Technology Stack
  Client Architecture
  Layout System
  Analytics Integration
    · Client-Side Analytics
  UI Component System
  Build and Development System
  Integration with AgentDock Core
  Summary

## · UI Components  (L6327)
  源文件: src/app/globals.css, src/app/layout.tsx, src/app/settings/core-settings.tsx, src/components/layout/layout-content.tsx, src/components/layout/mobile-nav.tsx, src/components/layout/site-sidebar.tsx, src/components/providers/posthog-provider.tsx, src/lib/analytics.ts, tailwind.config.ts
  Component Hierarchy and Architecture
  Layout System
  Navigation Components
  Theming System
  Analytics Integration
  Core UI Components
  Mobile Responsiveness
  Summary

## · Chat Interface  (L6732)
  源文件: src/app/chat/page.tsx, src/app/page.tsx, src/components/chat/chat-container.tsx, src/components/chat/chat-status.tsx, src/components/layout/site-header.tsx, src/components/layout/site-sidebar.tsx, src/hooks/use-session-info.ts
  Overview
  Chat Container Component
    · Key Responsibilities
    · Configuration and Initialization
  Message Flow Process
    · Client-Side Processing
    · Server-Side Processing
  Orchestration State Management
  Error Handling and Loading States
    · Loading States
    · Error Handling
  Session Management
  Debug Panel
  Chat Page Component
  Conclusion

## · API Routes  (L7208)
  源文件: src/app/api/og/route.tsx, src/components/chat/chat-container.tsx, src/components/chat/chat-status.tsx, src/components/ui/markdown-renderer.tsx, src/hooks/use-session-info.ts, src/lib/config.ts
  API Routes Architecture
  Chat API Routes
    · Request Flow
    · API Route Implementation Details
    · Response Handling
  OG Image API Route
  Session API Route
  Integration with Client Components
    · ChatContainer Integration
    · API Error Handling
  Markdown Rendering for API Responses

## · Layout System  (L7455)
  源文件: src/app/globals.css, src/app/layout.tsx, src/app/settings/core-settings.tsx, src/components/layout/layout-content.tsx, src/components/layout/mobile-nav.tsx, src/components/layout/site-sidebar.tsx, src/components/providers/posthog-provider.tsx, src/lib/analytics.ts, tailwind.config.ts
  Architecture Overview
  Core Layout Components
    · RootLayout
    · LayoutContent
  Sidebar Context
  Navigation Components
    · SiteSidebar
    · MobileNav
  Responsive Behavior
  Theme Integration
  Analytics Integration
  CSS and Styling System
  Key Interaction Flows
    · Sidebar Collapse Logic
    · Navigation Interaction
  Conclusion

## · Settings Page  (L7816)
  源文件: src/app/globals.css, src/app/settings/core-settings.tsx, src/app/settings/debug-panel.tsx, src/app/settings/model-display.tsx, src/app/settings/page.tsx, src/app/settings/types.ts, src/components/layout/mobile-nav.tsx, src/lib/models/registry.ts, src/lib/services/model-service.ts
  Settings Data Structure
  Key Features
    · API Key Management
    · Core Settings
    · Font Settings
    · Model Display
  Implementation Details
    · Storage and Persistence
    · Error Handling
    · ModelService Integration
  User Interface Flow
  Conclusion

## · Documentation System  (L8136)
  源文件: src/app/api/og/route.tsx, src/app/robots.ts, src/app/sitemap.ts, src/assets/fonts/Inter-SemiBold.ttf, src/components/ui/markdown-renderer.tsx, src/lib/config.ts, src/lib/metadata-utils.ts
  Overview
  Documentation File Structure and Resolution
  Markdown Rendering
  SEO and Metadata
  Navigation and User Experience
  URL Processing
  Integration with Site Architecture
  Document Processing Pipeline
  Sitemap and SEO Integration

## · Analytics Integration  (L8484)
  源文件: agentdock-core/src/nodes/tool-registry.ts, docs/analytics.md, src/app/agents/all/page.tsx, src/app/agents/page.tsx, src/app/layout.tsx, src/components/layout/layout-content.tsx, src/components/providers/posthog-provider.tsx, src/lib/analytics.ts, tailwind.config.ts
  Overview
  Implementation Architecture
  Client-Side Implementation
    · PostHog Provider
    · Integration in Root Layout
    · Usage Through Hook
  Server-Side Implementation
    · Key Components
    · Non-Blocking Design
  Configuration
  Event Flow
  Tracked Events
    · Client-Side Events
    · Server-Side Events
  Extending Analytics
    · Adding Client-Side Events
    · Adding Server-Side Events
  Debugging
    · Client-Side Debugging
    · Server-Side Debugging
  Best Practices

## · Agents and Tools  (L8870)
  源文件: agents/chandler-bing/README.md, agents/chandler-bing/template.json, agents/harvey-specter/template.json, agents/marketing-prompt-library/README.md, agents/marketing-prompt-library/template.json, agents/mental-health-guide/template.json, agents/research-agent/template.json, agents/sigmund-freud/README.md, agents/sigmund-freud/template.json, src/app/docs/layout.tsx, src/config/agent-tags.ts, src/nodes/search/index.ts
  Introduction to Agents and Tools
  Agent Templates
    · Template Structure
    · Key Template Properties
    · Agent Personality
    · Agent Categories
  Tools and Their Implementation
    · Tool Structure
    · Tool Implementation
    · Available Tools
  Agent-Tool Interaction
    · Tool Registry
    · Message Processing Flow with Tools
  Example Integrations
    · Research Assistant
    · Marketing Prompt Library Generator
  Conclusion

## · Agent Templates  (L9273)
  源文件: agents/chandler-bing/README.md, agents/chandler-bing/template.json, agents/harvey-specter/template.json, agents/mental-health-guide/template.json, agents/research-agent/template.json, agents/sigmund-freud/README.md, agents/sigmund-freud/template.json, src/app/docs/layout.tsx, src/nodes/search/index.ts
  Agent Template Overview
  Template JSON Structure
    · Metadata Fields
    · Personality Definition
    · Nodes and Node Configuration
    · Chat Settings
    · Options
  System Integration
  Template Processing Flow
  Example Templates
    · Character-Based Agent
    · Research-Focused Agent
    · Safety-Conscious Agent
  Creating Custom Agent Templates
    · Template Development Tips
  Conclusion

## · Custom Tools  (L9682)
  源文件: src/nodes/deep-research/README.md, src/nodes/deep-research/components.ts, src/nodes/deep-research/index.ts, src/nodes/init.ts, src/nodes/registry.ts, src/nodes/types.ts, src/nodes/weather/components.ts
  Overview of the Tool System
    · Tool System Architecture
  Tool Registry System
    · Registration Process
    · Tool Validation
  Tool Interface
    · LLM Context for Tools
  Creating Custom Tools
    · Tool Parameter Definition
    · Execute Function Implementation
    · Result Formatting
  Tool Execution Flow
  LLM Integration in Tools
    · Using LLM Within Tools
    · LLM Context Debugging
  Example: Deep Research Tool
    · Structure and Components
    · Parameter Schema
    · Execution Flow
    · UI Component Usage
  Best Practices for Custom Tools
    · Input Validation
    · Error Handling
    · Performance Considerations
    · Result Formatting
    · Documentation
  Tool Registration and Deployment
  Conclusion

## · Deep Research Tool  (L10150)
  源文件: agents/harvey-specter/template.json, agents/mental-health-guide/template.json, agents/research-agent/template.json, src/app/docs/layout.tsx, src/nodes/deep-research/README.md, src/nodes/deep-research/components.ts, src/nodes/deep-research/index.ts, src/nodes/search/index.ts
  Overview
  Architecture and Integration
  Tool Parameters
  Implementation Details
    · Core Components
    · Research Workflow
    · Error Handling and Rate Limiting
  LLM Integration
    · Analysis Process
    · LLM Prompt Design
    · Fallback Mechanism
  Report Structure
  Key Findings
  Research Statistics
  Sources
  Usage in Agent Templates
  Performance Considerations
    · Batch Processing
    · Content Cleaning and Extraction
  Example Tool Execution
  Integration with Agents

## · Search and API Tools  (L10515)
  源文件: agents/harvey-specter/template.json, agents/mental-health-guide/template.json, agents/research-agent/template.json, src/app/docs/layout.tsx, src/nodes/init.ts, src/nodes/registry.ts, src/nodes/search/index.ts, src/nodes/types.ts, src/nodes/weather/components.ts
  1. Search Tool Architecture
    · Search Tool Components
    · Search Tool Integration
  2. Tool Registration System
    · Tool Registry Architecture
    · Tool Validation Process
  3. Search Tool Implementation
    · Core Components
    · Error Handling
  4. Usage in Agent Templates
    · Example Configurations
    · Tool Configuration Examples
  5. Tool Interface and Types
    · Tool Interface
  6. Creating Custom API Tools
    · Custom Tool Implementation Pattern
    · Tool Result Formatting
  Summary

## · Development Guide  (L10891)
  源文件: .gitignore, package.json, pnpm-lock.yaml, scripts/generate-favicons.js
  Environment Setup
    · System Requirements
    · Installation Steps
  API Keys Management
    · API Key Configuration
    · Supported API Keys
    · API Key Resolution Order
  Build System
    · Development Scripts
    · Build Process Explained
    · Generated Artifacts
  Project Structure
    · Key Directories
  Development Workflow
    · Development Server
    · Testing
  Contributing Guidelines
    · Code Quality
    · Git Workflow
    · Pre-commit Hooks
  Dependency Management
    · Adding Dependencies
    · Updating Dependencies
    · Dependency Overrides
  Troubleshooting
    · Common Issues

## · Environment Setup  (L11313)
  源文件: .env.example, .gitignore, agentdock-core/src/llm/llm-orchestration-service.ts, package.json, pnpm-lock.yaml, scripts/generate-favicons.js
  System Requirements
  Installation Process
    · 1. Clone the Repository
    · 2. Install Dependencies
  Environment Configuration
    · Setting Up Environment Variables
    · Key Environment Variables
    · Storage Configuration
    · Setting Up Redis for Local Development
  Running the Application
    · Development Mode
    · Building for Production
  Project Structure
  Configuration Files
  Asset Generation
    · Favicon Generation
  Troubleshooting
    · Common Issues and Solutions
    · Clearing Generated Files
  Next Steps

## · API Keys Management  (L11684)
  源文件: .env.example, agentdock-core/src/llm/llm-orchestration-service.ts, src/app/settings/debug-panel.tsx, src/app/settings/model-display.tsx, src/app/settings/page.tsx, src/app/settings/types.ts, src/components/chat/chat-container.tsx, src/components/chat/chat-status.tsx, src/hooks/use-session-info.ts, src/lib/models/registry.ts, src/lib/services/model-service.ts
  Overview
  Key Resolution Process
    · Resolution Function
  Supported API Key Providers
  API Key Configuration Flow
  Settings Page Interface
    · Model Display Component
  BYOK (Bring Your Own Keys) Mode
  API Key Storage Architecture
  API Key Validation
  Token Usage and API Key Relationship
  Error Handling for API Key Issues
  Security Considerations
  Troubleshooting

## · Build System  (L11965)
  源文件: agentdock-core/package.json, agentdock-core/pnpm-lock.yaml, agentdock-core/src/nodes/agent-node.ts, agentdock-core/tsconfig.json, package.json, pnpm-lock.yaml, scripts/clean-install.sh, scripts/generate-favicons.js
  Package Manager and Environment Requirements
  Project Structure and Build Components
    · Build Tools
  Core Library Build
  Build Process Flow
    · Pre-build Steps
    · Main Build
    · Post-build Steps
  Script Dependency Graph
  Favicon Generation Process
  Clean Installation Process
  Development Build Process
  TypeScript Configurations
    · Core Library TypeScript Configuration
  Dependency Management
  Troubleshooting Build Issues
  Build Command Reference

## · Contributing Guidelines  (L12324)
  源文件: docs/i18n/README.md, docs/i18n/arabic/README.md, docs/i18n/deutsch/README.md
  Contribution Workflow
    · Issue First Approach
    · Contribution Process
    · Branch Naming Conventions
    · Commit Message Guidelines
  Contribution Areas
    · Project Structure and Contribution Areas
    · Core Framework Contributions
    · Client Contributions
    · Tool Contributions
    · Documentation Contributions
  Code Standards
    · TypeScript Guidelines
    · Documentation Standards
    · Testing Requirements
  Pull Request Review Process
    · Review Criteria
    · Addressing Feedback
  Community Guidelines
    · Communication Channels
    · Code of Conduct
  Internationalization Contributions
    · Translation Guidelines
  FAQ for Contributors

## · Internationalization  (L12710)
  源文件: docs/i18n/README.md, docs/i18n/arabic/README.md, docs/i18n/chinese/README.md, docs/i18n/deutsch/README.md, docs/i18n/dutch/README.md, docs/i18n/french/README.md, docs/i18n/greek/README.md, docs/i18n/italian/README.md, docs/i18n/japanese/README.md, docs/i18n/korean/README.md, docs/i18n/polish/README.md, docs/i18n/russian/README.md
  Overview
  i18n Structure
    · Directory Organization
    · Navigation Between Translations
    · Translation Index File
  Adding New Translations
    · Translation Process
    · Translation Guidelines
    · File Structure Template
  🌐 README Translations
  i18n Implementation Details
    · Documentation vs. Application i18n
    · Translation Consistency Mechanisms
  Current Language Support
  Contribution Process
  Future i18n Considerations
  Related Resources

## · i18n Structure  (L12997)
  源文件: docs/i18n/README.md, docs/i18n/arabic/README.md, docs/i18n/chinese/README.md, docs/i18n/deutsch/README.md, docs/i18n/dutch/README.md, docs/i18n/french/README.md, docs/i18n/greek/README.md, docs/i18n/italian/README.md, docs/i18n/japanese/README.md, docs/i18n/korean/README.md, docs/i18n/polish/README.md, docs/i18n/russian/README.md
  Overview
  Directory Structure
  Language Support
  Translation Index
  Translation Content Structure
  Cross-Language Navigation
  Translation Pattern
  Translation End Reference
  Code-to-Documentation Mapping
  Translation Workflow
  Conclusion

## · Adding New Translations  (L13264)
  源文件: docs/i18n/README.md, docs/i18n/arabic/README.md, docs/i18n/deutsch/README.md, docs/i18n/italian/README.md, docs/i18n/japanese/README.md, docs/i18n/korean/README.md, docs/i18n/polish/README.md, docs/i18n/russian/README.md, docs/i18n/spanish/README.md
  Translation Directory Structure
  Step-by-Step Translation Process
    · 1. Create Language Directory
    · 2. Create Translated README
  🌐 README Translations
    · 3. Update Translation Index
    · 4. Update All Existing Translations
  Translation Reference Network
  Translation Guidelines
    · What to Translate vs. What to Preserve
    · Formatting Requirements
  Example: Section Translation
  🧠 Design Principles
  🧠 Principios de Diseño
  Translation Workflow
  Complete Checklist