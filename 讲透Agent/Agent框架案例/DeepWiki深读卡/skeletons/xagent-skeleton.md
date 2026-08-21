# Skeleton: xagent（29 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 7KB | 5 | ~9 | 4 |
| 2 | Architecture | L238 | 11KB | 6 | ~2 | 7 |
| 3 | Installation and Setup | L602 | 9KB | 4 | ~0 | 12 |
| 4 | XAgent Core | L967 | 12KB | 6 | ~3 | 9 |
| 5 | Task Planning System | L1312 | 14KB | 9 | ~2 | 14 |
| 6 | Tool System | L1688 | 11KB | 7 | ~2 | 10 |
| 7 | Command Line Interface | L2000 | 9KB | 2 | ~5 | 5 |
| 8 | OpenAI Integration | L2292 | 10KB | 5 | ~4 | 5 |
| 9 | Task Recording | L2579 | 12KB | 11 | ~6 | 8 |
| 10 | ToolServer | L2999 | 11KB | 5 | ~5 | 7 |
| 11 | ToolServer Architecture | L3365 | 16KB | 9 | ~8 | 5 |
| 12 | Tool Types and Capabilities | L3807 | 10KB | 5 | ~2 | 6 |
| 13 | ToolServer Management | L4145 | 11KB | 5 | ~3 | 4 |
| 14 | XAgentServer | L4460 | 9KB | 4 | ~4 | 6 |
| 15 | Server Architecture | L4780 | 14KB | 8 | ~4 | 6 |
| 16 | WebSocket Interface | L5269 | 12KB | 5 | ~2 | 5 |
| 17 | Database Integration | L5628 | 12KB | 6 | ~2 | 8 |
| 18 | XAgentWeb | L6059 | 10KB | 6 | ~2 | 5 |
| 19 | User Interface Components | L6378 | 15KB | 9 | ~2 | 8 |
| 20 | Chat Interface | L6756 | 16KB | 14 | ~4 | 8 |
| 21 | Authentication | L7209 | 9KB | 5 | ~1 | 12 |
| 22 | Task Management | L7494 | 9KB | 8 | ~0 | 4 |
| 23 | File Upload and Management | L7803 | 9KB | 4 | ~3 | 11 |
| 24 | XAgentGen | L8106 | 9KB | 4 | ~0 | 10 |
| 25 | Model Generation | L8364 | 7KB | 8 | ~4 | 6 |
| 26 | Integration with XAgent | L8599 | 10KB | 5 | ~1 | 10 |
| 27 | Configuration Reference | L8896 | 11KB | 5 | ~2 | 7 |
| 28 | Deployment | L9276 | 9KB | 4 | ~0 | 7 |
| 29 | Developer Guide | L9642 | 10KB | 5 | ~6 | 14 |


## · Overview  (L6)
  源文件: README.md, README_JA.md, README_ZH.md, XAgentGen/README.md
  What is XAgent?
  System Architecture
  Core Components
  ToolServer System
  Data Flow and Communication
  Integration with XAgentGen
  Use Cases and Capabilities

## · Architecture  (L238)
  源文件: README.md, README_JA.md, README_ZH.md, XAgent/recorder.py, XAgentGen/README.md, XAgentServer/server.py, docker-compose.yml
  System Overview
  Key Components
    · XAgent Core
    · ToolServer
    · XAgentServer
    · XAgentWeb
    · XAgentGen (Optional)
  Data Flow and Persistence
  Deployment Architecture
  System Workflow
  Key Technical Specifications
  Security Architecture
  Conclusion

## · Installation and Setup  (L602)
  源文件: README.md, README_JA.md, README_ZH.md, XAgentGen/README.md, assets/config.yml, assets/gpt-3.5-turbo_config.yml, assets/gpt4_config.yml, requirements.txt, tests/__init__.py, tests/test_1106_model_openai.py, tests/test_model_alias.py, tests/test_run.py
  Overview of Setup Process
  Prerequisites
  Setting up ToolServer
    · Method 1: Pull pre-built image and start containers
    · Method 2: Build image from local sources
  Installing XAgent Core
  Configuring XAgent
    · API Key Configuration
    · Model Selection
    · Other Configuration Options
  Running XAgent
    · Command Line Interface
    · Web Interface (GUI)
  Output and Records
  Optional: Setting up XAgentGen (Custom Models)
    · Install CUDA Container Toolkit
    · Set up XAgentGen Container
    · Configure XAgent to Use Custom Model
  Troubleshooting

## · XAgent Core  (L967)
  源文件: README.md, README_JA.md, README_ZH.md, XAgent/agent/utils.py, XAgent/running_recorder.py, XAgent/vector_db.py, XAgent/workflow/plan_exec.py, XAgentGen/README.md, run.py
  Architecture Overview
  Dispatcher
  Planner
    · Planning Process
    · Plan Structure
  Actor
    · Actor Responsibilities
    · Tool Interaction Process
  RunningRecorder
    · Information Recorded
  Command-Line Interface
    · Usage
    · Command-Line Parameters
  Integration with External Systems
    · OpenAI/Azure API Integration
    · ToolServer Integration
    · XAgentGen Integration (Optional)
  Core Components Workflow
  System Requirements and Configuration

## · Task Planning System  (L1312)
  源文件: XAgent/agent/dispatcher.py, XAgent/agent/plan_generate_agent/prompt.py, XAgent/agent/plan_refine_agent/prompt.py, XAgent/agent/reflect_agent/prompt.py, XAgent/agent/tool_agent/prompt.py, XAgent/agent/utils.py, XAgent/ai_functions/request/utils.py, XAgent/inner_loop_search_algorithms/ReACT.py, XAgent/running_recorder.py, XAgent/vector_db.py, XAgent/workflow/plan_exec.py, XAgent/workflow/task_handler.py
  System Overview
  Core Components and Workflow
    · 1. Plan Generation
    · 2. Plan Refinement
    · 3. Task Execution via Inner and Outer Loops
    · 4. ReACT Chain Search
    · 5. Tool Agent
    · 6. Reflection and Learning
  Data Structure: Plan Tree
  Recording and Monitoring
  Configuration Parameters
  Example Workflow
  Integration with Other XAgent Components

## · Tool System  (L1688)
  源文件: ToolServer/ToolServerNode/core/envs/pycoding.py, XAgent/agent/plan_generate_agent/prompt.py, XAgent/agent/plan_refine_agent/prompt.py, XAgent/agent/reflect_agent/prompt.py, XAgent/agent/summarize.py, XAgent/agent/tool_agent/agent.py, XAgent/agent/tool_agent/prompt.py, XAgent/ai_functions/pure_functions/task_manage_functions.yml, XAgent/ai_functions/request/obj_generator.py, XAgent/ai_functions/request/utils.py
  Architecture Overview
  Tool Agent
  Tool Calls and Schema Validation
    · Function Call Structure
    · Validation Process
  Tool Types and Implementations
    · Python Notebook Example
  Tool Usage Workflow
    · Action Summarization
  Integration with Other XAgent Components
  Schema Validation and Error Recovery
    · Schema Definition
    · Error Recovery Process
  Conclusion

## · Command Line Interface  (L2000)
  源文件: XAgent/agent/utils.py, XAgent/running_recorder.py, XAgent/vector_db.py, XAgent/workflow/plan_exec.py, run.py
  1. Overview
  2. Command Line Arguments
  3. Execution Flow
  4. Usage Examples
    · Basic Task Execution
    · Uploading Files for Processing
    · Using a Specific Model
    · Running in Quiet Mode
    · Using Manual Mode
    · Using a Custom Configuration File
  5. Quiet Mode and Logging
  6. Integration with RunningRecorder
  7. CommandLine and CommandLineParam Classes
  8. Configuration Handling
  9. Command Response Handling

## · OpenAI Integration  (L2292)
  源文件: XAgent/ai_functions/request/openai.py, XAgent/config.py, assets/config.yml, assets/gpt-3.5-turbo_config.yml, assets/gpt4_config.yml
  1. Integration Overview
  2. Configuration System
    · 2.1 Model Configuration
    · 2.2 API Key Configuration
  3. Request Handling Mechanism
    · 3.1 Version Compatibility
    · 3.2 Retry Logic
  4. Context Length Management
  5. Model Name Normalization
  6. API Configuration Retrieval
  7. Azure OpenAI Integration
  8. Configuration Options
  9. Error Handling

## · Task Recording  (L2579)
  源文件: XAgent/agent/utils.py, XAgent/recorder.py, XAgent/running_recorder.py, XAgent/vector_db.py, XAgent/workflow/plan_exec.py, XAgentServer/server.py, docker-compose.yml, run.py
  1. Overview of Task Recording
  2. Recording Components
    · 2.1 Server Mode Recording
    · 2.2 CLI Mode Recording
  3. Recorded Data Types
    · 3.1 LLM Interactions
    · 3.2 Tool Interactions
    · 3.3 Plan Refinements
    · 3.4 Configurations and Queries
  4. Using the Task Recording System
    · 4.1 Command Line Options
    · 4.2 Caching and Performance Optimization
    · 4.3 Replaying Previous Executions
  5. Database Schema (Server Mode)
  6. File System Structure (CLI Mode)
  7. Integration with XAgent Core
  8. Technical Implementation Details
    · 8.1 Data Serialization
    · 8.2 Record Type Enumeration
  9. Best Practices and Considerations

## · ToolServer  (L2999)
  源文件: README.md, README_JA.md, README_ZH.md, ToolServer/README.md, ToolServer/README_ZH.md, ToolServer/ToolServerNode/core/envs/web.py, XAgentGen/README.md
  Introduction
    · ToolServer Architecture Overview
  System Components
    · ToolServerManager
    · ToolServerMonitor
    · ToolServerNode
    · Component Interactions Sequence
  Tool System
    · Tool Registration System
    · Available Tools
  API Documentation
    · API Endpoints
    · Tool Execution Flow
  Configuration
    · Configuration Files
    · Key Configuration Options
  Building and Running ToolServer
    · Starting with Pre-built Images
    · Building from Source
  Integration with XAgent
  Security Considerations
  Conclusion

## · ToolServer Architecture  (L3365)
  源文件: ToolServer/README.md, ToolServer/README_ZH.md, ToolServer/ToolServerManager/main.py, ToolServer/ToolServerManager/node_checker.py, ToolServer/ToolServerNode/core/envs/web.py
  Overview
  Components
    · ToolServerManager
    · ToolServerMonitor
    · ToolServerNode
  Communication Flow
  Database and State Management
  Docker Integration
  API Endpoints
  Monitoring and Lifecycle Management
  Integration with XAgent Core
  Security Considerations
  Configuration Options

## · Tool Types and Capabilities  (L3807)
  源文件: ToolServer/README.md, ToolServer/README_ZH.md, ToolServer/ToolServerNode/core/envs/pycoding.py, ToolServer/ToolServerNode/core/envs/web.py, XAgent/agent/summarize.py, XAgent/ai_functions/pure_functions/task_manage_functions.yml
  Tool Overview
  Tool Architecture
  Detailed Tool Descriptions
    · File Editor
    · Python Notebook
    · Web Browser
    · Shell
    · Rapid API
  Tool Execution Flow
  Tool Discoverability and Selection
  Tool Integration with XAgent
  Tool Extension

## · ToolServer Management  (L4145)
  源文件: ToolServer/ToolServerManager/main.py, ToolServer/ToolServerManager/models.py, ToolServer/ToolServerManager/node_checker.py, ToolServer/ToolServerManager/requirements.txt
  1. ToolServer Management Components
    · 1.1 ToolServerManager
    · 1.2 NodeChecker
    · 1.3 ToolServerNode
  2. ToolServerNode Lifecycle Management
    · 2.1 Node Creation
    · 2.2 Node Reconnection
    · 2.3 Node Closure
    · 2.4 Node Release
  3. Node Monitoring and Health Checking
    · 3.1 Node Status Checking
    · 3.2 Automatic Health Monitoring
  4. Request Routing to Nodes
  5. Configuration Parameters
  6. Dependencies and Requirements

## · XAgentServer  (L4460)
  源文件: XAgent/recorder.py, XAgentServer/README.md, XAgentServer/README_zh.md, XAgentServer/database/change/change_desc.sql, XAgentServer/server.py, docker-compose.yml
  1. Purpose and Functionality
  2. System Architecture
    · 2.1 Component Overview
    · 2.2 Directory Structure
  3. Communication Flow
  4. Server Implementation
    · 4.1 Core Server Class
    · 4.2 Task Execution Flow
  5. Database Integration
    · 5.1 MySQL Integration
    · 5.2 Redis Integration
  6. Recording System
  7. Deployment
  8. Using XAgentServer
  9. Integration with XAgent Core
  Summary

## · Server Architecture  (L4780)
  源文件: XAgentServer/README.md, XAgentServer/README_zh.md, XAgentServer/application/websockets/base.py, XAgentServer/database/change/change_desc.sql, XAgentServer/database/models.py, XAgentServer/database/sql/create_mysql_table.sql
  Overview
  Key Components
    · Application Layer
    · Communication Layer
    · Data Persistence Layer
  WebSocket Communication Flow
  Database Schema
    · Core Tables
  Data Flow Architecture
  Server Integration with XAgent Core
  Deployment Configuration
  Component Directory Structure
  Error Handling and State Management

## · WebSocket Interface  (L5269)
  源文件: XAgentServer/application/websockets/base.py, XAgentServer/database/models.py, XAgentServer/database/sql/create_mysql_table.sql, XAgentWeb/src/views/playground/chat.vue, XAgentWeb/vite.config.ts
  WebSocket Connection Architecture
  WebSocket Connection Types
  WebSocket Connection Establishment
  WebSocket Message Protocol
    · Client to Server Messages
    · Server to Client Messages
  WebSocket Message Flow
  WebSocket Connection Management
    · Ping/Pong Mechanism
    · Error Handling
  Database Integration
  Redis State Management
  Client-Side Implementation
  Server-Side Implementation
  Proxy Configuration

## · Database Integration  (L5628)
  源文件: XAgent/recorder.py, XAgentServer/README.md, XAgentServer/README_zh.md, XAgentServer/database/__init__.py, XAgentServer/database/change/change_desc.sql, XAgentServer/database/connect.py, XAgentServer/server.py, docker-compose.yml
  Database Architecture Overview
  Connection Management
    · MySQL Connection
    · Redis Connection
  Data Flow
  MySQL Schema
  Record Types
  Recording Process
  Database Deployment
    · MySQL Container Configuration
    · Redis Container Configuration
  Data Access Patterns
    · Querying Cached Data
    · Loading Previous Sessions
  XAgentServer Integration with Databases

## · XAgentWeb  (L6059)
  源文件: XAgentWeb/src/views/playground/chat.vue, XAgentWeb/src/views/playground/components/HistorySidebar.vue, XAgentWeb/src/views/playground/index.vue, XAgentWeb/src/views/playground/share.vue, XAgentWeb/vite.config.ts
  Architecture Overview
    · Position in XAgent Ecosystem
    · Component Architecture
  WebSocket Communication
    · WebSocket Connection Flow
    · WebSocket Message Handling
  User Interface Components
    · Main Layout
    · History Sidebar
    · Chat Interface
  Task Execution Modes
    · Auto vs. Manual Mode
  Workspace Integration
  Community Features
    · Shared Conversations
  Technical Implementation
    · State Management
    · Build Configuration
  API Integration

## · User Interface Components  (L6378)
  源文件: XAgentWeb/README.md, XAgentWeb/package.json, XAgentWeb/src/views/playground/components/FileUpload.vue, XAgentWeb/src/views/playground/components/HistorySidebar.vue, XAgentWeb/src/views/playground/components/Inferencing.vue, XAgentWeb/src/views/playground/components/Setting.vue, XAgentWeb/src/views/playground/index.vue, XAgentWeb/src/views/playground/share.vue
  Overview of XAgentWeb Architecture
  Main View Components
    · Playground View
    · History Sidebar
    · Setting Component
    · File Upload Component
    · Inferencing Component
    · Share View
  State Management and Data Flow
  Component Dependency Table
  User Interaction Flow
  Summary

## · Chat Interface  (L6756)
  源文件: XAgentWeb/index.html, XAgentWeb/src/composables/useApi.ts, XAgentWeb/src/router/index.ts, XAgentWeb/src/store/modules/config.ts, XAgentWeb/src/views/playground/chat.vue, XAgentWeb/src/views/playground/components/SubmitSubtaskInfo.vue, XAgentWeb/src/views/playground/components/WorkSpace.vue, XAgentWeb/vite.config.ts
  1. Architecture Overview
  2. WebSocket Communication
    · 2.1. Connection Types
    · 2.2. WebSocket Message Flow
  3. UI Components
    · 3.1. Component Structure
    · 3.2. Message Display
  4. Interaction Modes
    · 4.1. Mode Overview
    · 4.2. Mode Selection and Initialization
  5. Message Processing
    · 5.1. Message Types and Handling
    · 5.2. Task Control Flow
  6. Workspace Integration
    · 6.1. Workspace UI Components
    · 6.2. File Loading Process
  7. Connection Management
    · 7.1. Connection Lifecycle
    · 7.2. Connection Keep-Alive
  8. Error Handling
    · 8.1. Error Types and Responses
  9. Integration with Router
  10. State Management
    · 10.1. Store Integration

## · Authentication  (L7209)
  源文件: .gitignore, XAgentWeb/.gitignore, XAgentWeb/components.d.ts, XAgentWeb/src/components/Business/Feedback/index.vue, XAgentWeb/src/router/guard/permission.ts, XAgentWeb/src/store/modules/user.ts, XAgentWeb/src/utils/throttle.ts, XAgentWeb/src/views/exception/mobile.vue, XAgentWeb/src/views/login/component/ApplyForm.vue, XAgentWeb/src/views/login/login.vue, XAgentWeb/types/talk-type.ts, XAgentWeb/types/user.ts
  Overview
  Authentication Flow
    · Login Process
    · Registration Process
  Token Management
  Route Protection
  User Types and Access Levels
  Implementation Details
    · Local Storage for Persistence
    · Guest Account
  Security Considerations

## · Task Management  (L7494)
  源文件: XAgentWeb/src/store/modules/task.ts, XAgentWeb/src/views/playground/components/CodeViewer.vue, XAgentWeb/src/views/playground/components/Tab.vue, XAgentWeb/src/views/playground/layout.vue
  Task Data Structure
    · Task State Management
  Task Management Operations
    · Task Initialization and Progression
    · Task Refinement and Reset
    · Workspace File Management
  Task UI Components
    · Tab Interface
    · Task Execution Controls
    · Code Viewing
  Integration with Playground Layout
  Task Lifecycle
  Summary

## · File Upload and Management  (L7803)
  源文件: XAgentWeb/README.md, XAgentWeb/index.html, XAgentWeb/package.json, XAgentWeb/src/composables/useApi.ts, XAgentWeb/src/router/index.ts, XAgentWeb/src/store/modules/config.ts, XAgentWeb/src/views/playground/components/FileUpload.vue, XAgentWeb/src/views/playground/components/Inferencing.vue, XAgentWeb/src/views/playground/components/Setting.vue, XAgentWeb/src/views/playground/components/SubmitSubtaskInfo.vue, XAgentWeb/src/views/playground/components/WorkSpace.vue
  Purpose and Scope
  Overview
  File Upload Component
    · Component Implementation
    · Upload Constraints
  File Storage and Management
    · Config Store Implementation
    · Upload Process
  Workspace File Display
    · Workspace Layout
    · File Content Retrieval
    · File Type Handling
  API Integration
    · File Upload API
    · File Retrieval API
  Integration with Task Execution
    · Task Output File Display
  Security Considerations

## · XAgentGen  (L8106)
  源文件: README.md, README_JA.md, README_ZH.md, XAgentGen/README.md, XAgentGen/app.py, XAgentGen/xgen/models/__init__.py, XAgentGen/xgen/models/transformers.py, XAgentGen/xgen/parser/function_parser.py, XAgentGen/xgen/text/generate/__init__.py, XAgentGen/xgen/text/generate/regex.py
  1. Overview
  2. System Architecture
  3. Model Generation Process
    · 3.1 JSON Schema to Pydantic Models
    · 3.2 Pydantic Models to Regex Patterns
    · 3.3 Constrained Token Generation
  4. Integration with XAgent
    · 4.1 Configuration
    · 4.2 Docker Deployment
  5. Supported Models
  6. Example Usage
  Summary

## · Model Generation  (L8364)
  源文件: XAgentGen/app.py, XAgentGen/xgen/models/__init__.py, XAgentGen/xgen/models/transformers.py, XAgentGen/xgen/parser/function_parser.py, XAgentGen/xgen/text/generate/__init__.py, XAgentGen/xgen/text/generate/regex.py
  Purpose and Scope
  Overview
  Key Components
    · FastAPI Server
    · Function Parser
    · Constrained Logits Processor
    · XTransformers Model
  Regex-Based Generation
  API Interface
    · Chat Completions Endpoint
    · Request Processing Flow
  Constrained Generation Process
  Usage Example
  Model Initialization and Configuration
  Performance Considerations

## · Integration with XAgent  (L8599)
  源文件: README.md, README_JA.md, README_ZH.md, XAgentGen/README.md, XAgentGen/app.py, XAgentGen/xgen/models/__init__.py, XAgentGen/xgen/models/transformers.py, XAgentGen/xgen/parser/function_parser.py, XAgentGen/xgen/text/generate/__init__.py, XAgentGen/xgen/text/generate/regex.py
  1. XAgentGen Overview
  2. Integration Architecture
    · 2.1 System Components
    · 2.2 Communication Flow
  3. API Interface
    · 3.1 Endpoints
    · 3.2 Request Format
    · 3.3 Response Format
  4. Function Calling Mechanism
    · 4.1 Function Parsing Process
    · 4.2 Function Schema Processing
  5. Configuration for XAgent
    · 5.1 Configuration File
    · 5.2 Docker Network Configuration
  6. Usage Example
    · 6.1 Starting XAgentGen Service
    · 6.2 Integration Flow
  7. Technical Implementation Details
    · 7.1 Constrained Text Generation
    · 7.2 Model Implementation
  8. Advantages of XAgentGen Integration

## · Configuration Reference  (L8896)
  源文件: README.md, README_JA.md, README_ZH.md, XAgentGen/README.md, assets/config.yml, assets/gpt-3.5-turbo_config.yml, assets/gpt4_config.yml
  Overview
  Configuration File Location and Format
  Configuration Structure
  API Keys Configuration
    · Structure
    · Example Configuration
    · Supported Parameters
  Default Request Configuration
  Summary Configuration
  ToolServer Configuration
  Task Processing Configuration
  RapidAPI Configuration
  Human Interaction Configuration
  Tool Management Configuration
  Record Directory Configuration
  Experiment Configuration
  XAgentGen Integration
    · Using XAgentGen
  Recommended Configurations
  Configuration Application Workflow

## · Deployment  (L9276)
  源文件: README.md, README_JA.md, README_ZH.md, XAgent/recorder.py, XAgentGen/README.md, XAgentServer/server.py, docker-compose.yml
  Deployment Architecture
  Prerequisites
  Basic Deployment
    · Setting up ToolServer
    · Container Structure
    · Running XAgent with CLI
  Full Deployment with Web Interface
    · Setting up XAgentServer
    · Accessing the Web Interface
  Optional: Deploying with XAgentGen
    · Prerequisites for XAgentGen
    · Deploying XAgentGen
  Configuration Options
    · Environment Variables
    · Configuration Files
  Data and Workspace
  Troubleshooting
    · Common Issues
    · Updating XAgent
  Security Considerations

## · Developer Guide  (L9642)
  源文件: .gitignore, XAgentWeb/.gitignore, XAgentWeb/components.d.ts, XAgentWeb/src/App.vue, XAgentWeb/src/components/Business/Feedback/index.vue, XAgentWeb/src/views/login/component/ApplyForm.vue, XAgentWeb/tsconfig.json, XAgentWeb/tsconfig.node.json, requirements.txt, start_server.py, tests/__init__.py, tests/test_1106_model_openai.py
  Development Environment Setup
    · Development Dependencies
  Project Structure
    · Key Directories
  Component Development Guidelines
    · XAgent Core Development
    · ToolServer Development
    · XAgentServer Development
    · XAgentWeb Development
  Testing Guidelines
    · Running Tests
  Contributing Workflow
    · Code Style
  Troubleshooting Development Issues
    · Common Issues
  System Integration
  Conclusion