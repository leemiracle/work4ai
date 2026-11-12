# Skeleton: openagents（30 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 10KB | 4 | ~1 | 9 |
| 2 | Architecture | L246 | 14KB | 6 | ~0 | 11 |
| 3 | Agent Types | L688 | 12KB | 7 | ~3 | 13 |
| 4 | Getting Started | L1065 | 9KB | 3 | ~1 | 8 |
| 5 | Prerequisites | L1394 | 7KB | 2 | ~2 | 5 |
| 6 | Installation | L1652 | 10KB | 2 | ~1 | 8 |
| 7 | Configuration | L2050 | 13KB | 4 | ~6 | 8 |
| 8 | Backend System | L2418 | 14KB | 7 | ~1 | 6 |
| 9 | API Endpoints | L2881 | 11KB | 3 | ~5 | 5 |
| 10 | Memory Management | L3439 | 8KB | 7 | ~0 | 6 |
| 11 | LLM Integration | L3772 | 10KB | 5 | ~9 | 3 |
| 12 | Frontend System | L4035 | 16KB | 9 | ~6 | 7 |
| 13 | Chat Interface | L4482 | 11KB | 5 | ~2 | 3 |
| 14 | State Management | L4835 | 14KB | 7 | ~6 | 6 |
| 15 | Component Structure | L5234 | 10KB | 8 | ~2 | 3 |
| 16 | Agents | L5594 | 11KB | 5 | ~2 | 11 |
| 17 | Data Agent | L5931 | 14KB | 6 | ~3 | 7 |
| 18 | Plugins Agent | L6314 | 10KB | 9 | ~3 | 3 |
| 19 | Web Agent | L6646 | 12KB | 8 | ~0 | 7 |
| 20 | Shared Adapters | L6967 | 10KB | 6 | ~6 | 5 |
| 21 | Deployment | L7283 | 9KB | 3 | ~5 | 6 |
| 22 | Docker Deployment | L7649 | 10KB | 5 | ~3 | 6 |
| 23 | Environment Variables | L7960 | 9KB | 4 | ~10 | 6 |
| 24 | Extending OpenAgents | L8215 | 11KB | 5 | ~1 | 4 |
| 25 | Creating Custom Agents | L8582 | 11KB | 4 | ~1 | 6 |
| 26 | Adding New Plugins | L8904 | 13KB | 6 | ~2 | 5 |
| 27 | Integrating New LLMs | L9342 | 9KB | 3 | ~2 | 7 |
| 28 | Contributing | L9625 | 8KB | 6 | ~0 | 3 |
| 29 | Development Workflow | L9947 | 7KB | 6 | ~0 | 2 |
| 30 | Code Style and Conventions | L10198 | 11KB | 8 | ~0 | 2 |


## · Overview  (L6)
  源文件: README.md, README_JA.md, README_KO.md, README_ZH.md, pics/data_agent_demo.png, pics/openagents_overview.png, pics/plugins_agent_demo.png, pics/system_design.png, pics/web_agent_demo.png
  System Architecture
  Component Organization
  Agent Types
  Message Flow Sequence
  Deployment Architecture
  Extensibility
    · Extending with New Agents
    · Adding New Language Models
    · Adding New Tools to Plugins Agent
  Key Architectural Characteristics

## · Architecture  (L246)
  源文件: README.md, README_ZH.md, pics/data_agent.png, pics/data_agent_demo.png, pics/openagents_overview.png, pics/plugins_agent.png, pics/plugins_agent_demo.png, pics/system_design.png, pics/web_agent.png, pics/web_agent_demo.png, README.md:38-67
  System Overview
  Component Architecture
    · Frontend Components
    · Backend Components
    · Agent Implementation
  Data Flow and Message Processing
  Code Organization
    · Backend Structure
    · Frontend Structure
    · Agent Structure
  Agent System Design
    · BaseAgent
    · Specialized Agents
    · LLM Integration
  Deployment Architecture
    · Docker Containers
    · Container Communication
    · Data Persistence
    · Environment Configuration
  Extension Points
    · Adding New Agents
    · Adding New LLMs
    · Adding New Plugins
  Conclusion

## · Agent Types  (L688)
  源文件: README.md, README_ZH.md, pics/amazon.svg, pics/data_agent.png, pics/data_agent_demo.png, pics/google_research.svg, pics/openagents_overview.png, pics/plugins_agent.png, pics/plugins_agent_demo.png, pics/salesforce.webp, pics/system_design.png, pics/web_agent.png
  Overview of Agent Types
  Agent Architecture and Framework
    · Common Components
  Data Agent
    · Core Capabilities
    · Implementation Structure
    · Use Cases
  Plugins Agent
    · Core Capabilities
    · Implementation Structure
    · Sample Plugins
  Web Agent
    · Core Capabilities
    · Implementation Structure
    · Example Use Cases
  Agent Interaction Flow
  Integration with LLM Models
  Extending Agent Types
  Summary

## · Getting Started  (L1065)
  源文件: Dockerfile, README.md, README_ZH.md, backend/README.md, backend/setup_script.sh, docker-compose.yml, frontend/Dockerfile, frontend/next.config.js
  System Architecture Overview
  Deployment Options
    · Docker Deployment
    · Source Code Deployment
  LLM Configuration
  Optional Components
    · Code Interpreter Container
    · Kaggle Integration
    · Auto Tool Selection
  Component Interaction
  First-Time Usage
  Troubleshooting
  Next Steps

## · Prerequisites  (L1394)
  源文件: Dockerfile, README.md, README_ZH.md, backend/README.md, backend/setup_script.sh
  System Requirements
    · Hardware Requirements
    · Operating System Compatibility
  Software Dependencies Diagram
  Core Software Prerequisites
    · Python Environment
    · Database Requirements
  Agent-Specific Prerequisites
    · Data Agent Prerequisites
    · Plugins Agent Prerequisites
    · Web Agent Prerequisites
  External Service Credentials
    · LLM API Access
  Environment Variables
  Docker-Specific Requirements
  One-Click Setup Script

## · Installation  (L1652)
  源文件: Dockerfile, README.md, README_ZH.md, backend/README.md, backend/setup_script.sh, docker-compose.yml, frontend/Dockerfile, frontend/next.config.js
  System Overview
  Installation Options
  Prerequisites
  Source Code Installation
    · One-Click Setup Script
    · Manual Backend Setup
    · Frontend Setup
  Docker Installation
    · Basic Setup
    · Advanced Docker Configuration
  Verification
  Troubleshooting
    · Common Issues

## · Configuration  (L2050)
  源文件: Dockerfile, README.md, README_ZH.md, backend/README.md, backend/setup_script.sh, docker-compose.yml, frontend/Dockerfile, frontend/next.config.js
  Configuration Overview
  Backend Core Configuration
    · Core Environment Variables
  Database and Cache Configuration
    · MongoDB Configuration
    · Redis Configuration
  LLM API Configuration
    · OpenAI Configuration
    · Azure OpenAI Configuration
    · Anthropic Configuration
  Tool-specific Configuration
    · Kaggle Search Tool Configuration
    · Auto Plugin Selection Configuration
    · Code Execution Environment
  Deployment Configuration
    · Source Code Deployment Configuration
    · Docker Deployment Configuration
  Frontend Configuration
    · Development Configuration
    · Docker Configuration
  Configuration Best Practices

## · Backend System  (L2418)
  源文件: backend/README.md, backend/api/chat_webot.py, backend/kernel_publisher.py, backend/setup_script.sh, backend/utils/running_time_storage.py, backend/utils/user_conversation_storage.py
  Architecture Overview
  Key Components
    · API Layer
    · Memory Management
    · LLM Adapter
    · Kernel Publisher
  Data Flow
  Deployment Architecture
  Setup and Configuration
    · Prerequisites
    · Installation
  Integration with Real Agents
  Performance Considerations
  Error Handling
  Conclusion

## · API Endpoints  (L2881)
  源文件: backend/api/chat_plugin.py, backend/api/conversation.py, backend/api/tool.py, backend/memory.py, frontend/components/Chat/AgentSelect.tsx
  API Overview
    · API Architecture
  API Endpoint Reference Table
  Data Flow Through the API
  Chat Interaction APIs
    · POST /api/chat_xlang_plugin
  Tool Management APIs
    · POST /api/tool_list
    · POST /api/api_key
  Conversation Management APIs
    · POST /api/conversations/get_conversation_list
    · POST /api/conversations/get_folder_list
    · POST /api/conversation
    · POST /api/conversations/update_conversation
    · POST /api/conversations/update_folder
    · POST /api/conversations/register_folder
    · POST /api/conversations/register_conversation
    · POST /api/conversations/delete_conversation
    · POST /api/conversations/delete_folder
    · POST /api/conversations/clear
    · POST /api/conversations/stop_conversation
  Memory Management Integration
  Error Handling
  Authentication

## · Memory Management  (L3439)
  源文件: backend/api/chat_webot.py, backend/api/tool.py, backend/kernel_publisher.py, backend/memory.py, backend/utils/running_time_storage.py, backend/utils/user_conversation_storage.py
  Overview
  Architecture
  Memory Managers
    · UserMemoryManager
    · ChatMemoryManager
    · MessageMemoryManager
  Storage Backends
    · Redis Configuration
    · MongoDB Integration
  Memory Data Structures
    · Message Pool
    · API Key Pool
  Core Memory Operations
    · Reading from Memory
    · Writing to Memory
  Message History Traversal
  Agent Memory Integration
    · Loading Agent Memory
    · Saving Agent Memory
  Usage Examples
    · Managing Conversation Context
    · Managing API Keys
  Conclusion

## · LLM Integration  (L3772)
  源文件: backend/api/language_model.py, real_agents/adapters/models/__init__.py, real_agents/adapters/models/azure_openai.py
  Purpose and Scope
  LLM Integration Architecture
  Supported LLM Models
  LLM Selection and Initialization
  LLM Adapter Class Structure
  API Endpoint for LLM Selection
  Azure OpenAI Integration
  Common Configuration Parameters
  LLM Usage Flow
  Model Registry
  Environment Configuration

## · Frontend System  (L4035)
  源文件: frontend/components/Chat/ChatRichContentItem.tsx, frontend/package-lock.json, frontend/pages/api/home/home.tsx, frontend/types/agent.ts, frontend/types/chat.ts, frontend/pages/api/home/home.tsx:67-68, frontend/components/Chat/ChatRichContentItem.tsx:21-23
  Overview
    · High-Level Architecture
  Frontend Architecture
    · Key Architectural Patterns
    · Component Architecture
  State Management
    · State Structure
    · State Management Flow
  Agent Integration
    · Agent Configuration Structure
  Chat Interface and Message Handling
    · Message Structure and Flow
    · Rich Content Rendering
  Frontend-Backend Communication
    · Message Streaming Architecture
    · API Endpoints
  Main Components and Their Interactions
    · Component Structure
  User Interaction Flow
  Message Processing Pipeline
  Error Handling and Edge Cases
  Conclusion

## · Chat Interface  (L4482)
  源文件: frontend/components/Chat/Chat.tsx, frontend/components/Chat/ChatInput.tsx, frontend/components/Chat/ChatMessage.tsx
  Component Architecture
  Chat Message Flow
  Main Components
    · Chat Component
    · ChatInput Component
    · ChatMessage Component
  Rich Content Handling
  User Interaction Model
  Settings & Configuration
  Response Streaming
  Technical Implementation Details
    · Message Structure
    · Component Communication
  Error Handling

## · State Management  (L4835)
  源文件: frontend/components/Chat/ChatRichContentItem.tsx, frontend/package-lock.json, frontend/pages/api/home/home.state.tsx, frontend/pages/api/home/home.tsx, frontend/types/agent.ts, frontend/types/chat.ts
  Overview
  State Structure
  State Initialization
  State Management Implementation
  State Update Patterns
  Conversation State Management
  Message Streaming and Rich Content Handling
  Agent and Plugin State
  Caching Mechanism
  Interaction with Backend
  Error Handling
  Key Challenges and Solutions
  UI State Integration
  Conclusion

## · Component Structure  (L5234)
  源文件: frontend/components/Chat/ChatMessage.tsx, frontend/components/Chat/SettingsModal.tsx, frontend/components/Chatbar/Chatbar.tsx
  Overview of Frontend Component Architecture
  Key Component Hierarchies
    · Sidebar Components
    · Chat Message Components
  Chat Message Structure and Rendering Flow
  Component Props Interface
    · ChatMessage Props
    · SettingsModal Props
  Detailed Component Layout Structure
  Modal Components
  Responsive Design Implementation
  Chat Message Type Handling
  Component Event Flow
  Rich Content Rendering
  Conclusion

## · Agents  (L5594)
  源文件: README.md, README_ZH.md, backend/api/language_model.py, real_agents/adapters/data_model/message.py, real_agents/adapters/data_model/plugin/spec.py, real_agents/adapters/models/__init__.py, real_agents/adapters/models/azure_openai.py, Data Agent, Plugins Agent, Web Agent, Shared Adapters
  Agent Architecture
  Agent Types
    · Data Agent
    · Plugins Agent
    · Web Agent
  Agent Message Processing
    · Message Formats
  Language Model Integration
  Plugin System Architecture
  Extending the Agent System
  Agent Interaction Flow
  Summary

## · Data Agent  (L5931)
  源文件: README.md, README_ZH.md, backend/static/images/DataProfiling.cache, backend/static/images/Echarts.cache, backend/static/images/KaggleDataLoader.cache, backend/static/images/PythonCodeBuilder.cache, backend/static/images/SQLQueryBuilder.cache
  Overview and Capabilities
  Architecture
  Core Components
    · Code Generation and Execution
    · Data Sources and Loading
    · Data Visualization
    · Data Analysis
  Implementation Details
    · Request Processing Flow
    · Code to Natural Language Mapping
  Integration with OpenAgents Platform
    · Backend Integration
    · Frontend Integration
  Capabilities Comparison
  Technical Implementation
    · Data Agent Components
    · Python and SQL Code Execution
  Data Flow
  Use Cases
  Conclusion

## · Plugins Agent  (L6314)
  源文件: README.md, README_ZH.md, backend/api/chat_plugin.py
  Architecture Overview
  Key Components
    · 1. Plugin Registry
    · 2. Tool Selector
    · 3. Plugin Executor
    · 4. Agent Executor
  Plugin Execution Flow
  Auto Plugin Selection
  API Integration
    · Chat API Endpoint
    · Plugin API Keys
  Plugin Configuration
  Memory Management
  Extending with New Plugins
  Integration with OpenAgents Platform

## · Web Agent  (L6646)
  源文件: README.md, README_ZH.md, real_agents/web_agent/README.md, real_agents/web_agent/__init__.py, real_agents/web_agent/executors/web_browsing_executor.py, real_agents/web_agent/executors/webot_executor.py, real_agents/web_agent/web_browsing/base.py
  Introduction
  Architecture Overview
  Key Components
    · WebotExecutor
    · WebBrowsingExecutor
    · WebotCallingChain
  Web Agent Operation Modes
    · Basic Mode
    · React Mode
  Workflow
  Use Cases
  Chrome Extension Integration
  Technical Limitations and Considerations

## · Shared Adapters  (L6967)
  源文件: backend/api/language_model.py, real_agents/adapters/data_model/message.py, real_agents/adapters/data_model/plugin/spec.py, real_agents/adapters/models/__init__.py, real_agents/adapters/models/azure_openai.py
  Purpose and Scope
  Adapter Types Overview
  Model Adapters
    · Supported Models
    · Model Adapter Architecture
    · Model Selection Process
  Data Model Adapters
    · MessageDataModel
    · Message Formatting Constants
  Plugin Adapters
    · SpecModel
  Adapter Integration in System Architecture
  Message Processing Flow
  Model Registration and Type Mapping
  Summary

## · Deployment  (L7283)
  源文件: Dockerfile, README.md, README_ZH.md, docker-compose.yml, frontend/Dockerfile, frontend/next.config.js
  Deployment Architecture
  Deployment Options
    · System Requirements
  Docker Deployment
    · Prerequisites
    · Configuration
    · Basic Docker Deployment Steps
    · Environment Variables
    · GPU Support
    · Code Interpreter Configuration
  Source Code Deployment
    · Backend Deployment
    · Frontend Deployment
  Docker Compose Service Architecture
  Production Considerations
    · Security
    · Scaling
    · Monitoring
  Build Process
    · Backend Dockerfile
    · Frontend Dockerfile
  Troubleshooting
    · Common Issues

## · Docker Deployment  (L7649)
  源文件: Dockerfile, README.md, README_ZH.md, docker-compose.yml, frontend/Dockerfile, frontend/next.config.js
  Overview
  Docker Components
  Deployment Process
    · Prerequisites
    · Configuration
    · Building and Running
  Code Interpreter Configuration
  GPU Support
  Data Persistence
  Network Configuration
  Code to Docker Mapping
  Troubleshooting
    · Common Issues and Solutions
  Summary

## · Environment Variables  (L7960)
  源文件: Dockerfile, backend/README.md, backend/setup_script.sh, docker-compose.yml, frontend/Dockerfile, frontend/next.config.js
  Core Configuration Variables
  Backend Environment Variables
    · Database Connection Variables
    · Memory Management Variables
    · LLM Integration Variables
    · Code Execution Variables
    · Optional Tool Configuration
  Frontend Environment Variables
  Docker Deployment Environment Variables
  Setting Environment Variables
    · Development Environment
    · Using the Setup Script
    · Docker Production Environment
  Troubleshooting Environment Variables

## · Extending OpenAgents  (L8215)
  源文件: CONTRIBUTING.md, README.md, README_ZH.md, frontend/pages/_document.tsx
  Overview of Extension Points
  Creating Custom Agents
    · System Architecture for Custom Agents
    · Implementation Steps
    · Integration Flow
  Integrating New LLMs
    · Adding a Hosted LLM (API-accessible)
    · Integration Flow for Hosted LLMs
    · Adding a Self-Hosted LLM
  Adding New Plugins/Tools
    · Plugin Structure
    · Implementation Steps
    · Plugin Integration Flow
  Best Practices for Extending OpenAgents
  Example: Adding a Simple Custom Agent

## · Creating Custom Agents  (L8582)
  源文件: CONTRIBUTING.md, README.md, README_ZH.md, frontend/pages/_document.tsx, real_agents/adapters/data_model/message.py, real_agents/adapters/data_model/plugin/spec.py
  Agent Architecture in OpenAgents
  Custom Agent Components & Flow
  Step-by-Step Guide to Creating a Custom Agent
    · 1. Create a New Agent Folder
    · 2. Implement Agent Logic
    · 3. Create Backend API Integration
    · 4. Register Constants
    · 5. Add Frontend Support
    · 6. Implement Message Parsing Logic
  Agent Implementation Details
    · Agent-Backend Integration
    · Message Handling
    · Working with External Tools and APIs
  Advanced Customization
    · Adding New Data Types
    · Memory and State Management
  Testing Your Custom Agent
  Example Agent Structure
  Best Practices

## · Adding New Plugins  (L8904)
  源文件: CONTRIBUTING.md, README.md, README_ZH.md, backend/api/chat_plugin.py, frontend/pages/_document.tsx
  Plugin System Architecture
  Plugin Structure
  Plugin Request Flow
  Adding a New Plugin
    · 1. Create Plugin Directory
    · 2. Create Metadata File
    · 3. Define API Specification
    · 4. Implement API Endpoints
    · 5. Register Your Plugin
  Plugin Data Processing Flow
  Authentication and API Keys
  Plugin Icon Loading
  Example Plugin Implementation
    · Directory Structure
    · ai-plugin.json
    · openapi.yaml
    · getWeather.py
  How Plugin Selection Works
  Troubleshooting
  Plugin Execution Process

## · Integrating New LLMs  (L9342)
  源文件: CONTRIBUTING.md, README.md, README_ZH.md, backend/api/language_model.py, frontend/pages/_document.tsx, real_agents/adapters/models/__init__.py, real_agents/adapters/models/azure_openai.py
  Architecture Overview
  Current LLM Support
  Integration Process
    · 1. Create a Model Adapter (if needed)
    · 2. Register the Model in the Registry
    · 3. Update the LLM API
  Example: Integrating a Hosted API Model
  Configuration and Environment Variables
  Self-Hosted Model Integration
  Best Practices
  Conclusion

## · Contributing  (L9625)
  源文件: CONTRIBUTING.md, LICENSE, frontend/pages/_document.tsx
  Contribution Overview
  Contribution Areas
  Contribution Workflow
    · Step 1: Find or Create an Issue
    · Step 2: Fork and Clone the Repository
    · Step 3: Create a Branch and Implement Changes
    · Step 4: Submit a Pull Request
  Development Environment Setup
    · Frontend Setup
    · Backend Setup
  Issue Guidelines
    · Bug Reports
    · Feature Requests
    · Documentation Improvements
  Pull Request Guidelines
  License Information
  Contribution Code of Conduct
  Non-Code Contributions

## · Development Workflow  (L9947)
  源文件: CONTRIBUTING.md, frontend/pages/_document.tsx
  Contribution Model
  Issue and Feature Lifecycle
  Setting Up Development Environment
    · Development Environment Architecture
  Contribution Workflow
    · Issue Creation
    · Pull Request Submission
  Technical Implementation Workflow
    · For Frontend Changes
    · For Backend Changes
    · For Agent System Changes
  Local Development Setup
    · Frontend Setup
    · Backend Setup
  Best Practices for Contributions
  Conclusion

## · Code Style and Conventions  (L10198)
  源文件: CONTRIBUTING.md, frontend/pages/_document.tsx
  General Coding Principles
  Project Structure Conventions
  Frontend Code Style
    · TypeScript Conventions
    · React Component Structure
    · Example Component Structure
  Backend Code Style
    · Python Code Style
    · API Endpoint Naming
  Documentation Conventions
    · Code Documentation
    · Project Documentation
  Git Workflow Conventions
    · Branch Naming
    · Commit Messages
    · Pull Request Process
  Code Review Standards
    · Pull Request Requirements
    · Review Criteria
  File Organization
  Language-Specific Conventions
    · TypeScript/JavaScript (Frontend)
    · Python (Backend)
  Issue and Feature Development Conventions
  Testing Conventions
    · Frontend Tests
    · Backend Tests
  Conclusion