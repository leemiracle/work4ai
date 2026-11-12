# Skeleton: llocalsearch（19 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | LLocalSearch Overview | L6 | 5KB | 2 | ~2 | 4 |
| 2 | System Architecture | L135 | 8KB | 5 | ~2 | 8 |
| 3 | Agent Chain | L335 | 8KB | 2 | ~4 | 10 |
| 4 | Tool System | L505 | 8KB | 2 | ~2 | 9 |
| 5 | LLM Integration | L656 | 6KB | 2 | ~1 | 6 |
| 6 | Frontend Application | L789 | 5KB | 2 | ~2 | 13 |
| 7 | Chat Interface | L926 | 6KB | 2 | ~0 | 6 |
| 8 | Sidebar and Navigation | L1052 | 8KB | 2 | ~2 | 14 |
| 9 | Settings and Configuration | L1208 | 6KB | 2 | ~4 | 7 |
| 10 | Developer Guide | L1338 | 4KB | 2 | ~1 | 6 |
| 11 | Development Environment | L1462 | 6KB | 3 | ~2 | 13 |
| 12 | Containerization and Deployment | L1634 | 7KB | 2 | ~4 | 9 |
| 13 | API Server | L1788 | 6KB | 4 | ~2 | 8 |
| 14 | Monitoring and Metrics | L1971 | 6KB | 3 | ~1 | 5 |
| 15 | User Guide | L2119 | 5KB | 2 | ~2 | 2 |
| 16 | Installation and Setup | L2243 | 8KB | 4 | ~4 | 4 |
| 17 | Basic Usage | L2513 | 5KB | 2 | ~1 | 4 |
| 18 | Advanced Features | L2640 | 8KB | 3 | ~6 | 6 |
| 19 | Glossary | L2840 | 6KB | 2 | ~2 | 11 |


## · LLocalSearch Overview  (L6)
  源文件: LICENSE, OLLAMA_GUIDE.md, README.md, infra.drawio
  Purpose and Scope
  What is LLocalSearch?
    · Core Philosophy
  System Architecture & Data Flow
    · High-Level Entity Mapping
  Agentic Reasoning Loop
  Key Features
  Hardware and Environment Requirements
  Project Roadmap

## · System Architecture  (L135)
  源文件: backend/main.go, docker-compose.dev.yaml, docker-compose.yaml, go.work, go.work.sum, Agent Chain, Tool System, LLM Integration
  Purpose and Scope
  System Overview
    · High-Level Architecture Diagram
  Core Components
    · Backend Server
    · Agent Chain System
    · Tools System
  Data Flow
  Deployment Architecture
    · Environment Configuration
  Communication Patterns

## · Agent Chain  (L335)
  源文件: README.md.old, backend/agentChain.go, backend/go.mod, backend/go.sum, backend/llm_tools/tool_webscrape.go, backend/lschains/custom_structured_parser.go, backend/utils/customHandler.go, backend/utils/prompts.go, backend/utils/types.go, src/lib/types/types.ts
  Architecture Overview
    · Component Relationship Diagram
  Core Components
  Execution Flow
    · Sequence of Operations
  Implementation Details
    · Session Management and Vector DB Namespacing
    · Iterative Reasoning Loop
    · Streaming Protocol
  Error Recovery and Post-Processing
    · Parser Error Handling
    · Title Generation

## · Tool System  (L505)
  源文件: backend/llm_tools/simple_websearch.go, backend/llm_tools/tool_search_vector_db.go, backend/utils/llm_backends.go, backend/utils/load_localfiles.go, backend/utils/vector_db_handler.go, searxng/limiter.toml, searxng/settings.yml, searxng/uwsgi.ini, src/lib/show_logs_button.svelte
  Tool System Overview
    · Natural Language to Code Entity Mapping
  Tool Interface Structure
    · Implementation Details
    · Data Flow for SearchVectorDB
  Available Tools
    · WebSearch Tool
    · SearchVectorDB Tool
  Data Ingestion Pipeline
    · Text Processing Logic
  CustomHandler Callback Bridge
  Configuration Parameters

## · LLM Integration  (L656)
  源文件: backend/agentChain.go, backend/llm_tools/tool_search_vector_db.go, backend/lschains/format_sources_chain.go, backend/lschains/ollama_functioncall.go, backend/utils/llm_backends.go, backend/utils/vector_db_handler.go
  Overview
  Core Components
    · Ollama Client Initialization
    · Embeddings Pipeline
    · Model Management
  Vector Store Integration (ChromaDB)
    · Data Flow: Ingestion to Retrieval
    · Namespace Management
  Implementation in Agent Chain
  Constraints and Known Issues
  Configuration Summary

## · Frontend Application  (L789)
  源文件: Dockerfile, custom-server.js, nginx.conf, package-lock.json, package.json, src/app.css, src/app.d.ts, src/app.html, src/routes/+layout.ts, static/favicon.png, static/favicon.svg, svelte.config.js
  Architecture Overview
  Routing and Entry Points
  Deployment and Proxying
    · Static Deployment with Nginx
    · Node.js Development Proxy
  Technical Stack
  Component Modules
    · Chat Interface
    · Sidebar and Navigation
    · Settings and Configuration
  Data Flow with Backend

## · Chat Interface  (L926)
  源文件: src/lib/bottom_bar.svelte, src/lib/loading_message.svelte, src/lib/log_item.svelte, src/lib/log_node.svelte, src/lib/new_chat_button.svelte, src/lib/sources.svelte
  Interface Structure
  Route and Data Loading
    · Key Functions
  Rendering Pipeline (`log_item.svelte`)
    · Markdown and Sanitization
    · Tool Action Icons
    · Error Handling
  Input and Controls (`bottom_bar.svelte`)
    · Implementation Details
  Streaming Interaction
  Visual Components
    · Loading States
    · Dark Mode

## · Sidebar and Navigation  (L1052)
  源文件: src/lib/chatHistory.svelte, src/lib/chatList.svelte, src/lib/chatListItemElem.svelte, src/lib/chat_button.svelte, src/lib/loading_message.svelte, src/lib/new_chat_button.svelte, src/lib/sidebar.svelte, src/lib/sidebar_history_toggle.svelte, src/lib/sidebar_sources_toggle.svelte, src/lib/toggle_darkmode_button.svelte, src/lib/toggle_settings_button.svelte, src/lib/toggle_sidebar_button.svelte
  Purpose and Scope
  Sidebar Components Overview
  Root Navigation and Redirects
  Sidebar Container Implementation
  Navigation Controls
    · Chat and Session Management
    · Interface Toggles
  Chat History Mode
    · Chat List Items
  Loading States
  Technical Implementation Details
    · Data Flow for History Selection
    · Component Property Reference

## · Settings and Configuration  (L1208)
  源文件: src/lib/clickOutside.js, src/lib/model_switch_window.svelte, src/lib/settings_field.svelte, src/lib/settings_window.svelte, src/lib/toggle_darkmode_button.svelte, src/lib/toggle_model_switch.svelte, src/routes/+page.svelte
  Settings Interface Overview
    · Settings Component Architecture
  Configurable Parameters
    · LLM Configuration
    · Vector DB & Scraper Settings
  Implementation Details
    · Validation Pipeline (`settings_field.svelte`)
    · Model Switching Logic
    · Reset and Persistence
    · Theme Management
  UI Interaction Diagram

## · Developer Guide  (L1338)
  源文件: Makefile, OLLAMA_GUIDE.md, README.md, env-example, go.work, go.work.sum
  Development Workflow Overview
    · Core Development Components
  System Architecture for Developers
    · Service Topology
  Detailed Developer Documentation
    · [Development Environment](#4.1)
    · [Containerization and Deployment](#4.2)
    · [API Server](#4.3)
    · [Monitoring and Metrics](#4.4)
  Testing and Quality Assurance
    · Backend Testing
    · Versioning and Releases
  Troubleshooting the Development Setup

## · Development Environment  (L1462)
  源文件: .eslintrc.cjs, .prettierrc, Makefile, backend/.air.toml, backend/Dockerfile, custom-server.js, env-example, go.work, go.work.sum, package-lock.json, package.json, svelte.config.js
  Overview
  Toolchain and Configuration
    · Backend: Go Workspace and Hot-Reload
    · Frontend: SvelteKit and Vite
    · Custom Server for Local Dev
  Prerequisites
  Development Environment Setup
    · 1. Configure Environment Variables
    · 2. Makefile Targets
  Code Quality and Formatting
  Development Workflow
    · Data Flow: Local Development

## · Containerization and Deployment  (L1634)
  源文件: Dockerfile, Dockerfile.dev, backend/Dockerfile, backend/Dockerfile.dev, docker-compose.dev.yaml, docker-compose.yaml, nginx.conf, src/routes/+layout.ts, vite.config.ts
  Container Architecture Overview
    · Container Architecture Diagram
  Service Components
    · Backend Container
    · Frontend Container
    · Nginx Configuration (`nginx.conf`)
    · Infrastructure Services
  Development vs. Production Configuration
    · Configuration Comparison
  Network Topology
  Deployment Flow
    · Data Flow Entities

## · API Server  (L1788)
  源文件: backend/apiServer.go, backend/e2e/e2e_suite_test.go, backend/e2e/simple_question_test.go, backend/main.go, backend/utils/helper.go, backend/utils/prompts.go, backend/utils/types.go, src/lib/types/types.ts
  API Server Architecture
  API Endpoints
    · Stream Endpoint
    · Models Endpoint
    · Chat History and List
  Session Management
    · Client Settings Parsing
  Initialization and Tutorial
  CORS and Headers

## · Monitoring and Metrics  (L1971)
  源文件: metrics/Dockerfile, metrics/go.mod, metrics/main.go, metrics/tmp/build-errors.log, metrics/tmp/main
  Overview
  Metrics Service Architecture
  Data Collection and Privacy
    · Implementation Details
  Version Checking Logic
  API Definition
    · Request Body (`metricsReqBody`)
    · Response Body (`metricsResponse`)
    · CORS Handling
  Containerization

## · User Guide  (L2119)
  源文件: OLLAMA_GUIDE.md, README.md
  1. Installation and Setup
    · 1.1 Prerequisites
    · 1.2 Deployment Overview
  2. Basic Usage
    · 2.1 Submitting Queries
    · 2.2 Understanding the Live Stream
  3. Advanced Features
    · 3.1 Settings and Configuration
    · 3.2 Navigation and History
  4. Privacy and Transparency

## · Installation and Setup  (L2243)
  源文件: OLLAMA_GUIDE.md, README.md, docker-compose.yaml, env-example
  Prerequisites
  System Architecture Overview
  Installation Steps
    · 1. Clone the Repository
    · 2. Ollama Setup
    · 3. Environment Configuration
    · 4. Start the Docker Services
  Service Configuration Details
  Verifying Installation
  Troubleshooting
    · Common Issues
    · Checking Service Status
  Next Steps

## · Basic Usage  (L2513)
  源文件: OLLAMA_GUIDE.md, README.md, src/lib/log_item.svelte, src/lib/sources.svelte
  Starting a Conversation
    · Chat Interface Overview
  Understanding Responses
    · Response Components and Data Flow
    · Visual Tool Indicators
  Viewing Sources
  Interpreting Live Logs
  Troubleshooting Connection Issues

## · Advanced Features  (L2640)
  源文件: backend/llm_tools/simple_websearch.go, src/lib/chatList.svelte, src/lib/settings_field.svelte, src/lib/settings_window.svelte, src/lib/show_logs_button.svelte, src/lib/sidebar.svelte
  Follow-up Question Support
  Configuration Options
    · LLM Settings
    · Vector DB Settings
    · Webscraper Settings
    · Text Processing Settings
  Log and Source Management
    · Show/Hide Logs
    · Source Tracking
  Chat History Management
  User Interface Customization

## · Glossary  (L2840)
  源文件: OLLAMA_GUIDE.md, README.md, backend/agentChain.go, backend/llm_tools/tool_search_vector_db.go, backend/utils/llm_backends.go, backend/utils/prompts.go, backend/utils/types.go, backend/utils/vector_db_handler.go, docker-compose.yaml, src/lib/log_item.svelte, src/lib/types/types.ts
  Core Architectural Concepts
    · Agent Chain
    · Session Management
    · LLM/RAG Space to Code Entity Mapping
  Technical Terms & Abbreviations
  Internal Tool Definitions
    · WebSearch
    · WebScrape
    · SearchVectorDB
  Frontend Component Glossary
    · Log Rendering Pipeline
  Environment & Configuration