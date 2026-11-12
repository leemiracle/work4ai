# Skeleton: openagent（45 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | OpenAgent Overview | L6 | 6KB | 2 | ~2 | 18 |
| 2 | Getting Started & Configuration | L147 | 8KB | 2 | ~5 | 24 |
| 3 | System Architecture | L331 | 8KB | 3 | ~2 | 19 |
| 4 | Core AI & Chat System | L516 | 6KB | 2 | ~2 | 12 |
| 5 | Chat UI & Session Management | L659 | 9KB | 2 | ~2 | 22 |
| 6 | Message Pipeline & AI Response Generation | L833 | 10KB | 2 | ~2 | 26 |
| 7 | Store Configuration | L1021 | 6KB | 2 | ~3 | 15 |
| 8 | Chat & Message Administration | L1145 | 7KB | 2 | ~0 | 8 |
| 9 | AI Model & Embedding Providers | L1292 | 7KB | 2 | ~2 | 8 |
| 10 | LLM Provider Integrations | L1441 | 8KB | 2 | ~3 | 34 |
| 11 | Embedding & Vector Pipeline | L1603 | 8KB | 2 | ~2 | 23 |
| 12 | Provider Management UI | L1768 | 8KB | 2 | ~5 | 12 |
| 13 | Speech & Audio Processing | L1916 | 7KB | 2 | ~2 | 14 |
| 14 | Knowledge Base & RAG | L2059 | 6KB | 2 | ~2 | 15 |
| 15 | File Storage & Management | L2199 | 7KB | 2 | ~2 | 27 |
| 16 | Document Parsing & Text Splitting | L2342 | 9KB | 2 | ~3 | 19 |
| 17 | Vector Store & Search | L2501 | 8KB | 2 | ~2 | 14 |
| 18 | Agent Tools & MCP Integration | L2659 | 7KB | 2 | ~2 | 8 |
| 19 | Built-in Tools | L2806 | 8KB | 2 | ~1 | 29 |
| 20 | MCP Server Management | L2977 | 8KB | 2 | ~2 | 13 |
| 21 | Browser & Computer-Use Agent | L3148 | 7KB | 2 | ~2 | 5 |
| 22 | Security Scanning | L3280 | 5KB | 2 | ~2 | 5 |
| 23 | Scan Engine & Providers | L3428 | 8KB | 2 | ~4 | 11 |
| 24 | Asset & Cloud Inventory | L3604 | 7KB | 3 | ~7 | 5 |
| 25 | Infrastructure Management | L3777 | 5KB | 2 | ~2 | 5 |
| 26 | Machine & Container Management | L3911 | 7KB | 3 | ~4 | 5 |
| 27 | Kubernetes Application Deployment | L4070 | 8KB | 3 | ~3 | 5 |
| 28 | Video & Multimedia | L4249 | 6KB | 2 | ~0 | 13 |
| 29 | Video Lifecycle & Annotation | L4367 | 8KB | 2 | ~4 | 14 |
| 30 | Task Analysis & Reporting | L4517 | 8KB | 2 | ~2 | 17 |
| 31 | Authentication, Permissions & Multi-tenancy | L4691 | 6KB | 2 | ~1 | 12 |
| 32 | Authentication & Session Management | L4833 | 7KB | 2 | ~3 | 18 |
| 33 | Authorization & Role-Based Access Control | L4976 | 7KB | 2 | ~0 | 10 |
| 34 | Observability & Administration | L5120 | 6KB | 1 | ~2 | 20 |
| 35 | Usage Analytics & Billing | L5254 | 6KB | 2 | ~4 | 12 |
| 36 | Activity Records & Audit Logging | L5377 | 8KB | 2 | ~3 | 27 |
| 37 | System Info & Prometheus Metrics | L5527 | 7KB | 2 | ~4 | 7 |
| 38 | Additional Features | L5695 | 7KB | 2 | ~2 | 14 |
| 39 | Articles, Forms & Graphs | L5835 | 8KB | 2 | ~2 | 14 |
| 40 | Bot Integrations & Messaging | L5998 | 7KB | 2 | ~4 | 18 |
| 41 | Image Management & Cloud Resources | L6133 | 7KB | 2 | ~2 | 10 |
| 42 | Internationalization & Frontend Infrastructure | L6279 | 6KB | 2 | ~0 | 10 |
| 43 | Internationalization (i18n) | L6399 | 7KB | 2 | ~2 | 8 |
| 44 | Frontend API Client Layer | L6546 | 7KB | 2 | ~2 | 16 |
| 45 | Glossary | L6697 | 8KB | 2 | ~2 | 21 |


## · OpenAgent Overview  (L6)
  源文件: CONTRIBUTING.md, README.md, README_zh.md, conf/app.conf, conf/conf.go, docker-compose.yml, main.go, object/adapter.go, object/init.go, routers/router.go, routers/static_filter.go, scripts/install.ps1
  Core Capabilities
  High-Level Architecture
    · Conceptual System Flow
  Major Subsystems Relation
    · Code-to-Navigation Mapping
  Initialization Sequence

## · Getting Started & Configuration  (L147)
  源文件: .github/workflows/build.yml, .gitignore, .goreleaser.yaml, CONTRIBUTING.md, Dockerfile, README.md, README_zh.md, conf/app.conf, conf/conf.go, docker-compose.yml, docker-entrypoint.sh, embed.go
  Installation & Deployment
    · Binary Installation
    · Docker Setup
    · Build Pipeline
  Configuration Management
    · Backend: app.conf & Environment Variables
    · Frontend: WebConfig Injection
  Startup Initialization Sequence
    · Initialization Flow
    · Middleware Pipeline (Filters)
  Configuration Data Flow
  Built-in Resource Initialization

## · System Architecture  (L331)
  源文件: authz/authz.go, conf/app.conf, conf/conf.go, controllers/base.go, controllers/message_answer_job.go, main.go, object/adapter.go, object/init.go, routers/authz_filter.go, routers/auto_signin_filter.go, routers/base.go, routers/router.go
  High-Level Data Flow
  Backend Architecture (Go & Beego)
    · 1. Request Filter Pipeline
    · 2. Controller Layer
    · 3. Persistence Layer (XORM)
  Frontend Architecture (React & Ant Design)
    · 1. Component Structure
    · 2. Routing and Navigation
    · 3. Navigation Tree Configuration
  Security & Authentication (Casdoor Integration)
  Initialization Sequence

## · Core AI & Chat System  (L516)
  源文件: controllers/account.go, controllers/chat.go, controllers/message.go, controllers/message_answer.go, controllers/message_util.go, controllers/util.go, object/chat.go, object/message.go, web/src/ChatBox.js, web/src/ChatMenu.js, web/src/ChatPage.js, web/src/backend/ChatBackend.js
    · High-Level Architecture
    · AI Conversation Lifecycle
    · Core Components
    · Code Mapping: Data Entities to System Logic

## · Chat UI & Session Management  (L659)
  源文件: web/src/ChatBox.js, web/src/ChatExampleQuestions.js, web/src/ChatMenu.js, web/src/ChatMessageRender.js, web/src/ChatMessageRender.test.js, web/src/ChatPage.js, web/src/LoadSkillModal.js, web/src/MultiPaneManager.js, web/src/StoreInfoTitle.js, web/src/backend/MessageBackend.js, web/src/chat/ChatFileInput.js, web/src/chat/ChatInput.js
  ChatPage & State Management
    · Key State Properties
    · Polling & Status Tracking
  ChatBox Interaction Layer
    · Interaction Components
    · Session Persistence
  Multi-Pane Mode
    · Implementation
    · UI/Code Entity Mapping: Multi-Pane Workflow
  Message Rendering & Pipeline
    · Rendering Features
    · UI/Code Entity Mapping: Message Components
  TTS & STT Integration
    · Text-to-Speech (TTS)
    · Speech-to-Text (STT)
  Navigation & Session Management
    · Session State Flow

## · Message Pipeline & AI Response Generation  (L833)
  源文件: carrier/carrier.go, carrier/suggestion.go, carrier/title.go, controllers/account.go, controllers/chat.go, controllers/message.go, controllers/message_answer.go, controllers/message_carrier.go, controllers/message_util.go, controllers/message_writer.go, controllers/util.go, model/mcp.go
  Message Lifecycle Overview
    · 1. Request Initialization & Context Resolution
    · 2. Security & Billing Hooks
    · 3. RAG & Tool Orchestration
    · Data Flow Diagram: Message Pipeline
  Response Generation & Streaming
    · Carrier Parsing & Multi-Stage Generation
    · RefinedWriter and Event Types
    · Diagram: Streaming Entity Relationship
  Tool Execution Loop
  Message Persistence & Post-Processing
    · Final Update & Notification
    · Content Refinement
    · Regeneration Logic

## · Store Configuration  (L1021)
  源文件: controllers/store.go, object/site.go, object/site_endpoint.go, object/store.go, object/store_provider.go, object/store_test.go, routers/endpoint_filter.go, storage/casdoor.go, storage/local_file_system.go, web/src/SiteEditPage.js, web/src/StoreEditPage.js, web/src/StoreHubDrawer.js
  The Store Entity
    · Key Data Structure
  Provider Bindings and Data Flow
    · Configuration Flow Diagram
  RAG and File Integration
    · Storage Provider Abstraction
  Ownership and Sharing Model
  MCP and Tool Integration

## · Chat & Message Administration  (L1145)
  源文件: web/src/ChatEditPage.js, web/src/ChatListPage.js, web/src/FormEditPage.js, web/src/MessageEditPage.js, web/src/MessageListPage.js, web/src/RecordEditPage.js, web/src/SkillEditPage.js, web/src/VectorEditPage.js
  Administrative Overview
    · Data Flow: Admin Interface to Persistence
  Chat Session Administration
    · Key Features
    · Chat Lifecycle Management
  Message Administration
    · Message Metadata and Editing
    · Vector and Audit Integration
  Usage Analytics and Extended Forms
    · Implementation Details
  Administrative Logic and Maintenance
    · Vector and Audit Maintenance

## · AI Model & Embedding Providers  (L1292)
  源文件: go.mod, go.sum, model/provider.go, object/provider.go, object/transaction.go, object/util.go, web/src/ProviderEditPage.js, web/src/ProviderListPage.js
  Provider Architecture Overview
    · Core Provider Model
    · Code-to-System Mapping
  LLM Provider Integrations
  Embedding & Vector Pipeline
  Provider Management UI
  Speech & Audio Processing
  Provider Interaction Flow

## · LLM Provider Integrations  (L1441)
  源文件: embedding/alibabacloud.go, embedding/azure_openai.go, embedding/local.go, embedding/openai.go, embedding/provider.go, go.mod, go.sum, model/alibabacloud.go, model/azure_openai.go, model/baichuan.go, model/baiducloud.go, model/chatglm.go
  ModelProvider Abstraction
    · The ModelProvider Interface
    · Data Flow: Natural Language to Code Entities
  Provider Factory and Supported Backends
    · Supported Providers
  Pricing Engine and Token Counting
    · Token Counting Logic
    · Price Calculation
  Dry-Run Mode
  Tool Call Orchestration

## · Embedding & Vector Pipeline  (L1603)
  源文件: contest/rag_contest.go, contest/rag_contest_test.go, embedding/alibabacloud.go, embedding/azure_openai.go, embedding/cohere.go, embedding/gemini.go, embedding/huggingface.go, embedding/local.go, embedding/openai.go, embedding/provider.go, embedding/util.go, model/alibabacloud.go
  EmbeddingProvider Interface
    · Supported Backends
    · Core Interface and Data Structure
  Vector Embedding Pipeline
    · Data Flow Diagram: File to Vector
    · Implementation Details
  Search Strategies
    · 1. Default Search (Flat)
    · 2. Hierarchy Search
    · Strategy Selection Logic
  Management and Visualization
    · Data Integrity and Status Tracking
    · Vector Refresh and Updates
    · Pricing and Token Usage

## · Provider Management UI  (L1768)
  源文件: controllers/provider.go, controllers/vector.go, object/provider.go, web/src/Provider.js, web/src/ProviderEditPage.js, web/src/ProviderListPage.js, web/src/VectorListPage.js, web/src/backend/ProviderBackend.js, web/src/backend/VectorBackend.js, web/src/common/ProviderWidget.js, web/src/common/TestModelWidget.js, web/src/common/TestTtsWidget.js
  Provider Architecture Overview
    · Data Flow and Management
    · Code Entity Relationship
  ProviderListPage
    · Key Features
  ProviderEditPage
    · Dynamic Property Generation
    · Credential Masking
  Live Validation Widgets
    · TestModelWidget & EmbedTestWidget
    · TtsTestWidget
    · TestMcpWidget
  Provider Data Model

## · Speech & Audio Processing  (L1916)
  源文件: controllers/text_to_speech.go, embedding/alibabacloud.go, embedding/local.go, embedding/openai.go, embedding/provider.go, model/alibabacloud.go, model/silicon_flow.go, model/volcengine.go, object/message_ai.go, object/text_to_speech.go, tts/alibabacloud.go, tts/provider.go
  1. Text-to-Speech (TTS) Architecture
    · 1.1 Backend Abstraction & Flow
    · 1.2 Alibaba Cloud Implementation
    · TTS Data Flow: Text to Audio
  2. Browser-Side Voice Integration
    · 2.1 TtsHelper Logic
    · 2.2 Provider Management & Testing
    · Entity Association Diagram
  3. Embedding & Vector Processing
  4. Supported Providers & Models

## · Knowledge Base & RAG  (L2059)
  源文件: contest/rag_contest.go, contest/rag_contest_test.go, object/search.go, object/search_default.go, object/search_default_util.go, object/search_hierarchy.go, object/vector.go, object/vector_embedding.go, web/package.json, web/src/App.less, web/src/FileTree.js, web/src/LanguageSelect.js
  Overview of the RAG Pipeline
    · Conceptual to Code Mapping
  File Storage & Management
  Document Parsing & Text Splitting
  Vector Store & Search
    · Vector Data Model
    · Retrieval Strategies

## · File Storage & Management  (L2199)
  源文件: controllers/file.go, controllers/tree_file.go, controllers/util_record.go, object/file.go, object/store_provider.go, object/store_test.go, object/tree_file.go, storage/casdoor.go, storage/local_file_system.go, storage/provider.go, util/string.go, web/package.json
  StorageProvider Abstraction
    · Supported Implementations
    · Data Flow: Storage to Store
  File Entity & Persistence
  FileTree UI Component
    · Key Features
  File Management Administration
    · Admin Operations
    · File Deletion Logic

## · Document Parsing & Text Splitting  (L2342)
  源文件: audio/audio_test.go, audio/xfyun_client_test.go, object/video_import_test.go, split/basic.go, split/default.go, split/markdown.go, split/markdown_test.go, split/provider.go, split/provider_test.go, split/qa.go, txt/csv.go, txt/docx.go
  Document Parsing (`txt` package)
    · Core Parsing Logic
    · MarkItDown Integration
    · Data Flow: URL to Text
  Text Splitting (`split` package)
    · Split Strategies
    · Default Splitter Implementation Details
    · Markdown Splitter Implementation Details
  Technical Implementation Summary
    · Key Functions & Classes
    · Dependencies & Tooling

## · Vector Store & Search  (L2501)
  源文件: contest/rag_contest.go, contest/rag_contest_test.go, controllers/provider.go, controllers/vector.go, object/search.go, object/search_default.go, object/search_default_util.go, object/search_hierarchy.go, object/vector.go, object/vector_embedding.go, web/src/VectorListPage.js, web/src/VectorTooltip.js
  1. Vector Data Model
    · Vector Entity Definition
    · Diagram: Natural Language to Vector Entity Mapping
  2. Embedding-to-Vector Pipeline
    · Pipeline Execution Flow
    · Diagram: Vector Ingestion Pipeline
  3. Vector CRUD & Administration
    · Backend Operations
    · Frontend Management
  4. Search Provider Strategies
    · Default Search Strategy (`DefaultSearchProvider`)
    · Hierarchy Search Strategy (`HierarchySearchProvider`)
    · Search Implementation Table

## · Agent Tools & MCP Integration  (L2659)
  源文件: controllers/message_writer.go, model/mcp.go, object/merge_agent_tools.go, object/message_tool.go, object/resource_archive_tool.go, web/src/chat/GeneratedResourceList.js, web/src/chat/ToolCallSection.js, web/src/chat/toolCallStream.js
  Tool System Architecture
    · Tool Execution Loop
    · Natural Language to Code Entity Mapping
  Built-in Tools
  MCP Server Integration
    · Server Management
  Browser & Computer-Use Capabilities
  Administrative & Testing UI

## · Built-in Tools  (L2806)
  源文件: controllers/skill.go, controllers/snapshot.go, object/skill.go, object/snapshot.go, object/snapshot_tool.go, object/tool.go, skills/powerpoint/SKILL.md, skills/powerpoint/references/pptxgenjs.md, tool/browser.go, tool/local_file.go, tool/office.go, tool/office_excel.go
  Tool Architecture & Registration
    · Data Flow: Natural Language to Code Entity
  Tool Implementations
    · Web Search & Fetch
    · Office & Local Files
    · Multimedia & Automation
  Tool Management UI
    · ToolEditPage
    · TestToolWidget

## · MCP Server Management  (L2977)
  源文件: controllers/message_writer.go, controllers/server.go, mcp/scan.go, mcp/tools.go, model/mcp.go, object/server.go, web/src/ScaleEditPage.js, web/src/ServerEditPage.js, web/src/ServerListPage.js, web/src/ServerStorePage.js, web/src/backend/ServerBackend.js, web/src/chat/ToolCallSection.js
  Overview and Architecture
    · Data Flow: Tool Discovery and Execution
  MCP Server Entity
    · Tool Schema
  Tool Discovery and Intranet Scanning
    · `GetToolsFromURL`
    · Intranet Scanning
  Management UI
    · ServerListPage and ServerStorePage
    · ServerEditPage
  Tool Execution and Streaming
    · Backend Execution Loop
    · Frontend Streaming
  Testing Tools with `TestMcpWidget`
  Tool Set Construction

## · Browser & Computer-Use Agent  (L3148)
  源文件: controllers/chrome_connect.go, routers/cors_filter.go, tool/browser_use.go, tool/browser_use_chrome_ext.go, web/src/OsDesktop.css
  Browser Use Tool
    · Session Management
    · Built-in Actions
    · Data Flow: Browser Interaction
  OS Desktop UI & Window Management
    · Window Management
  Chrome Extension Integration
    · Extension Communication Protocol
  Key Functions and Classes

## · Security Scanning  (L3280)
  源文件: object/adapter.go, routers/router.go, web/src/App.js, web/src/ManagementPage.js, web/src/component/nav-item-tree/NavItemTree.js
  System Overview
    · Component Relationship
  Scan Job Processing
    · Job Lifecycle
  Scan Engine & Providers
  Asset & Cloud Inventory
    · Key Features
  Security UI Components

## · Scan Engine & Providers  (L3428)
  源文件: conf/app.conf, conf/conf.go, main.go, object/adapter.go, object/init.go, routers/router.go, routers/static_filter.go, web/src/App.js, web/src/Conf.js, web/src/ManagementPage.js, web/src/component/nav-item-tree/NavItemTree.js
  ScanProvider Interface
  Supported Scan Tools
    · 1. Nmap (Network Mapping)
    · 2. OS Patch (Windows Auditing)
    · 3. Nuclei (Vulnerability Scanning)
    · 4. Other Providers
  Scan Job Processing
    · Execution Workflow
    · Distributed Logic & Target Matching
    · Job State Transitions
  Natural Language to Code Entity Space
    · Scan Execution Logic
    · Result Rendering Pipeline
  Result Rendering
    · OS Patch Specific Rendering

## · Asset & Cloud Inventory  (L3604)
  源文件: object/adapter.go, routers/router.go, web/src/App.js, web/src/ManagementPage.js, web/src/component/nav-item-tree/NavItemTree.js
  Asset Data Model
  Cloud Provider Parsing (Alibaba Cloud)
    · Scan & Sync Flow
    · Asset Conversion Diagram
  Asset List & Visualization
    · Graph Visualization
    · Graph Rendering Logic
  Assets and Scan Targets
    · Scan Target Resolution
    · Scan Detail Popover
  Navigation & UI Integration
    · Sidebar Mapping
  Key Implementation Files

## · Infrastructure Management  (L3777)
  源文件: object/adapter.go, routers/router.go, web/src/App.js, web/src/ManagementPage.js, web/src/component/nav-item-tree/NavItemTree.js
    · Infrastructure Overview
    · Machine & Container Management
    · Kubernetes Application Deployment
    · Workbench & Infrastructure Catalog

## · Machine & Container Management  (L3911)
  源文件: object/adapter.go, routers/router.go, web/src/App.js, web/src/ManagementPage.js, web/src/component/nav-item-tree/NavItemTree.js
  Compute Resource Architecture
    · Machine Data Flow
  Machine Management
    · Machine Data Model
    · Provider Abstraction (`pkgmachine`)
    · Cloud Synchronization
  Container Management
    · Container UI Components
    · Data Interaction
  Remote Connectivity
    · Connection Logic
  Implementation Details
    · Database Persistence
    · Navigation and Routing
    · Security & Masking

## · Kubernetes Application Deployment  (L4070)
  源文件: object/adapter.go, routers/router.go, web/src/App.js, web/src/ManagementPage.js, web/src/component/nav-item-tree/NavItemTree.js
  System Overview
    · Core Entities
    · Data Flow: From Template to Pods
  Template Catalog and Manifest Generation
    · Manifest Pipeline
  Deployment Pipeline (object/application_k8s.go)
    · Key Functions
  Observability and Monitoring
    · Cache Manager (`object/cache_manager.go`)
    · Metrics Integration
  User Interface Components
    · ApplicationListPage
    · ApplicationEditPage
    · TemplateEditPage
    · Navigation Integration

## · Video & Multimedia  (L4249)
  源文件: controllers/scale.go, controllers/task.go, object/task.go, web/src/TaskAnalysisBarChart.js, web/src/TaskAnalysisPieChart.js, web/src/TaskAnalysisRadarChart.js, web/src/TaskAnalysisReport.js, web/src/TaskEditPage.js, web/src/TaskListPage.js, web/src/backend/TaskBackend.js, web/src/taskAnalysisScoreBands.js, web/src/taskReportDocx.js
    · Video Management Architecture
    · Video Lifecycle & Annotation
    · Task Analysis & Reporting

## · Video Lifecycle & Annotation  (L4367)
  源文件: controllers/resource.go, controllers/scale.go, controllers/task.go, controllers/task_upload.go, object/resource.go, object/task.go, web/src/ResourceListPage.js, web/src/TaskEditPage.js, web/src/TaskListPage.js, web/src/WordCloudChart.js, web/src/backend/ResourceBackend.js, web/src/backend/TaskBackend.js
  Video & Task Data Model
    · The Task Entity
    · Entity Mapping
  Upload & Resource Management
  AI Analysis & Annotation Workflow
    · 1. Task Analysis
    · 2. Manual Annotation (Labeling)
    · 3. Word Cloud & Visualization
  Review & Permission Workflow
    · Multi-Stage Review
    · Role Access Levels
    · Data Protection

## · Task Analysis & Reporting  (L4517)
  源文件: controllers/scale.go, controllers/task.go, object/message_fake.go, object/task.go, object/task_analyze.go, web/src/ConfTask.js, web/src/TaskAnalysisBarChart.js, web/src/TaskAnalysisPieChart.js, web/src/TaskAnalysisRadarChart.js, web/src/TaskAnalysisReport.js, web/src/TaskEditPage.js, web/src/TaskListPage.js
  1. Data Model: Task & Scale
    · Task Entity
    · TaskResult Structure
  2. AI-Driven Task Analysis
    · Analysis Workflow
    · Technical Data Flow: Natural Language to Code Entity
  3. Frontend Implementation: TaskEditPage
    · Key Features
  4. Reporting & Visualization
    · Visualization Components
    · Backend/Frontend Interaction Diagram
  5. DOCX Report Export
    · Implementation Details (`taskReportDocx.js`)

## · Authentication, Permissions & Multi-tenancy  (L4691)
  源文件: authz/authz.go, controllers/casdoor_user.go, controllers/message_answer_job.go, controllers/permission.go, controllers/signin.go, controllers/storage_provider.go, object/store_share.go, object/user.go, routers/authz_filter.go, web/src/StoreShareModal.js, web/src/backend/AccountBackend.js, web/src/backend/OrganizationUserBackend.js
  Security Architecture Overview
    · Request Authorization Flow
  Authentication & Session Management
    · Key Components:
  Authorization & RBAC
    · Role Hierarchy & Casbin
    · Store Isolation & Sharing
  Authorization Filter Pipeline
    · Key Security Entities:
  Child Pages

## · Authentication & Session Management  (L4833)
  源文件: controllers/casdoor_user.go, controllers/permission.go, controllers/signin.go, controllers/storage_provider.go, object/store_share.go, object/user.go, routers/auto_signin_filter.go, routers/base.go, web/craco.config.js, web/mv.js, web/public/index.html, web/public/manifest.json
  Casdoor SSO Integration
    · Initialization Sequence
  Sign-in & Sign-out Flow
    · Password Authentication
    · Session Management
  Auto-Signin Filter
  Backend Request Processing
    · Key Functions
  Session Configuration
  Frontend Auth Components
    · AuthCallback
    · Account Management

## · Authorization & Role-Based Access Control  (L4976)
  源文件: authz/authz.go, controllers/message_answer_job.go, routers/authz_filter.go, web/src/PermissionUtil.js, web/src/Setting.js, web/src/backend/PermissionBackend.js, web/src/backend/StorageProviderBackend.js, web/src/locales/en/data.json, web/src/locales/zh/data.json, web/src/table/FileTable.js
  RBAC Model & Roles
    · Key Roles
    · Code-to-Role Association
  Authorization Filter Pipeline
    · AuthzFilter and Casbin Enforcer
    · Request Deny Logic
  Store Isolation & Frontend Helpers
    · Store Isolation Enforcement
    · PermissionUtil Helpers
  SSE and Async Authorization

## · Observability & Administration  (L5120)
  源文件: build.sh, controllers/prometheus.go, controllers/record.go, controllers/record_chain.go, controllers/system_info.go, controllers/usage.go, object/record.go, object/record_chain.go, object/usage.go, object/usage_range.go, object/usage_test.go, riscv64.Dockerfile
  System Overview
    · Data Flow & Entity Mapping
  Usage Analytics & Billing
  Activity Records & Audit Logging
  System Info & Prometheus Metrics
  Administrative Utilities

## · Usage Analytics & Billing  (L5254)
  源文件: controllers/usage.go, go.mod, go.sum, model/provider.go, object/transaction.go, object/usage.go, object/usage_range.go, object/usage_test.go, object/util.go, web/src/UsagePage.js, web/src/UsageTable.js, web/src/backend/UsageBackend.js
  Usage Data Model
  Usage Analytics Dashboard
    · Visualization Components
    · Data Flow: Analytics Fetching
  Billing & Transaction Pipeline
    · Transaction Logic
    · Failed Transaction Retry Logic
    · Transaction Pipeline Diagram
  Key Functions & Classes Reference

## · Activity Records & Audit Logging  (L5377)
  源文件: chain/chainmaker.go, chain/chainmaker_tencent.go, chain/chainmaker_tencent_demo.go, chain/chainmaker_util.go, chain/client.go, chain/ethereum.go, controllers/form_data.go, controllers/openai_api.go, controllers/openai_writer.go, controllers/record.go, controllers/record_chain.go, object/message_cleanup.go
  Record Data Model
    · Core Attributes
    · Geographic Resolution
  Blockchain-Backed Audit Trails
    · Implementation Details
    · Key Functions
  Provider Utilities & Resolution
    · Default Provider Logic
    · Provider Resolution Flow
  Administrative View: RecordListPage
    · Features
    · Request Recording Filters

## · System Info & Prometheus Metrics  (L5527)
  源文件: build.sh, controllers/prometheus.go, controllers/system_info.go, riscv64.Dockerfile, util/system.go, util/system_test.go, web/src/SystemInfo.js
  System Monitoring Architecture
    · Data Flow for Observability
  System Information Collection
    · Key Metrics Tracked
    · Versioning Logic
  Prometheus Integration
    · Metrics Definitions
    · Endpoint Implementation
  Frontend: SystemInfo Page
    · Implementation Details
    · API Endpoints
  Natural Language to Code Mapping

## · Additional Features  (L5695)
  源文件: controllers/pipe.go, controllers/pipe_webhook.go, object/form.go, object/pipe.go, pipe/pipe.go, web/.gitignore, web/README.md, web/src/BaseListPage.js, web/src/FormDataPage.js, web/src/FormDataTablePage.js, web/src/FormListPage.js, web/src/PipeEditPage.js
  Articles, Forms & Graphs
    · Entity Relationship to UI
  Bot Integrations & Messaging (Pipes)
    · Request & Messaging Pipeline
  Image Management & Cloud Resources
  Feature Summary Table

## · Articles, Forms & Graphs  (L5835)
  源文件: controllers/form_data.go, controllers/openai_api.go, controllers/openai_writer.go, object/form.go, object/provider_default.go, object/provider_util.go, web/.gitignore, web/README.md, web/src/BaseListPage.js, web/src/FormDataPage.js, web/src/FormDataTablePage.js, web/src/FormListPage.js
  1. Article Entity & Processing Pipeline
    · 1.1 Data Model
    · 1.2 Frontend Logic: Text Parsing
  2. Form & FormData System
    · 2.1 Form Categories
    · 2.2 Form Implementation Flow
    · 2.3 Blockchain Proxying
  3. Graph Entity & Visualization
    · 3.1 Data Structure
    · 3.2 Automated Graph Generation
    · 3.3 Rendering Engine
  4. Provider Resolution Logic
    · 4.1 Default Provider Resolution
    · 4.2 Key Functions
  5. Summary of Frontend Infrastructure for Lists

## · Bot Integrations & Messaging  (L5998)
  源文件: controllers/form_data.go, controllers/openai_api.go, controllers/openai_writer.go, controllers/pipe.go, controllers/pipe_webhook.go, object/pipe.go, object/provider_default.go, object/provider_util.go, pipe/discord.go, pipe/facebook_messenger.go, pipe/pipe.go, pipe/slack.go
  The Pipe Integration System
    · Core Interface and Architecture
    · Supported Messaging Platforms
    · Messaging Data Flow
  OpenAI-Compatible API
    · Implementation Details
  Configuration & Management
    · Pipe Data Model
    · Management UI

## · Image Management & Cloud Resources  (L6133)
  源文件: controllers/resource.go, controllers/task_upload.go, object/adapter.go, object/resource.go, routers/router.go, web/src/App.js, web/src/ManagementPage.js, web/src/ResourceListPage.js, web/src/backend/ResourceBackend.js, web/src/component/nav-item-tree/NavItemTree.js
  Image Entity & Cloud Integration
    · Image Data Model
    · Alibaba Cloud Image Operations
    · Image Management UI
  Resource Management System
    · The Resource Entity
    · Resource Flow: Upload & Persistence
    · Key Functions
  Task Attachments & Parsing
    · Task Document Pipeline
  Resource UI (ResourceListPage)
    · UI Features

## · Internationalization & Frontend Infrastructure  (L6279)
  源文件: web/package.json, web/src/App.less, web/src/FileTree.js, web/src/LanguageSelect.js, web/src/Setting.js, web/src/index.css, web/src/locales/en/data.json, web/src/locales/zh/data.json, web/src/shadcnTheme.js, web/yarn.lock
  Overview
  Internationalization (i18n)
    · Translation Flow
  Frontend API Client Layer
    · Backend Helper Pattern
    · UI Infrastructure Components

## · Internationalization (i18n)  (L6399)
  源文件: i18n/generate_test.go, i18n/locales/en/data.json, i18n/locales/zh/data.json, i18n/util.go, web/src/Setting.js, web/src/i18n.js, web/src/locales/en/data.json, web/src/locales/zh/data.json
  Frontend Implementation
    · Configuration and Initialization
    · Component Integration Diagram
    · Usage in Components
    · Language Selection UI
  Backend Implementation
    · Translation Mechanism
    · Backend Translation Flow
  Translation Data Structure
  Tooling and Maintenance
    · Generation and Synchronization
    · File Operations and Formatting

## · Frontend API Client Layer  (L6546)
  源文件: object/adapter.go, object/form.go, routers/router.go, web/.gitignore, web/README.md, web/src/App.js, web/src/BaseListPage.js, web/src/FormDataPage.js, web/src/FormDataTablePage.js, web/src/FormListPage.js, web/src/ManagementPage.js, web/src/SettingUtil.js
  1. Backend Helper Modules Pattern
    · Implementation Characteristics
    · Data Flow: Entity Management
  2. Request Interception: FetchFilter
    · Key Functions
  3. Administrative Base: BaseListPage
    · Core Features
  4. Context Selection: StoreSelect
    · Behavior and Constraints

## · Glossary  (L6697)
  源文件: conf/app.conf, conf/conf.go, controllers/message_answer.go, controllers/message_util.go, go.mod, go.sum, main.go, model/provider.go, object/adapter.go, object/init.go, object/transaction.go, object/util.go
  Core Entities
    · Store
    · Carrier
    · Provider
  Domain Jargon
    · RAG (Retrieval-Augmented Generation)
    · MCP (Model Context Protocol)
    · Thought Chain / Reasoning
  System Architecture Concepts
    · Message Lifecycle
    · Data Flow Diagram: Message Generation
  Technical Abbreviations
  Permission Roles
    · Authorization Entity Mapping
  Common Code Symbols