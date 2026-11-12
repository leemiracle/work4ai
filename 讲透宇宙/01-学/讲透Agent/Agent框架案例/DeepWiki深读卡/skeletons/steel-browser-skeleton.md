# Skeleton: steel-browser（55 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 7KB | 2 | ~2 | 7 |
| 2 | System Architecture | L199 | 12KB | 4 | ~4 | 8 |
| 3 | Key Features | L484 | 11KB | 3 | ~4 | 13 |
| 4 | Monorepo Structure | L763 | 11KB | 6 | ~6 | 5 |
| 5 | Getting Started | L1091 | 8KB | 3 | ~4 | 9 |
| 6 | Installation | L1345 | 11KB | 4 | ~4 | 13 |
| 7 | Environment Configuration | L1672 | 19KB | 8 | ~20 | 13 |
| 8 | Docker Deployment | L2301 | 12KB | 5 | ~8 | 12 |
| 9 | Core Services | L2646 | 11KB | 4 | ~5 | 9 |
| 10 | CDPService | L2906 | 17KB | 5 | ~10 | 11 |
| 11 | SessionService | L3331 | 15KB | 6 | ~8 | 8 |
| 12 | FileService | L3775 | 13KB | 10 | ~12 | 5 |
| 13 | Browser Sessions | L4235 | 7KB | 4 | ~2 | 7 |
| 14 | Session Management API | L4421 | 13KB | 4 | ~16 | 5 |
| 15 | Session Configuration | L4746 | 10KB | 4 | ~8 | 4 |
| 16 | Session Storage & State | L4966 | 8KB | 3 | ~4 | 11 |
| 17 | Live Session Monitoring | L5170 | 13KB | 2 | ~11 | 6 |
| 18 | Quick Actions API | L5484 | 11KB | 5 | ~4 | 6 |
| 19 | Web Scraping | L5740 | 8KB | 2 | ~4 | 15 |
| 20 | Screenshots & PDF Generation | L5926 | 8KB | 2 | ~6 | 8 |
| 21 | Proxy Support | L6143 | 8KB | 2 | ~2 | 8 |
| 22 | File Management | L6354 | 10KB | 3 | ~2 | 5 |
| 23 | File API | L6569 | 16KB | 5 | ~5 | 5 |
| 24 | Archive Management | L7075 | 14KB | 4 | ~13 | 5 |
| 25 | Browser Automation Features | L7510 | 9KB | 4 | ~5 | 9 |
| 26 | CDP Integration | L7709 | 9KB | 3 | ~4 | 9 |
| 27 | Selenium Support | L7921 | 8KB | 4 | ~7 | 10 |
| 28 | Anti-Detection Features | L8116 | 8KB | 3 | ~12 | 6 |
| 29 | Request Interception & Filtering | L8334 | 10KB | 3 | ~1 | 5 |
| 30 | Browser Extensions | L8611 | 8KB | 3 | ~3 | 11 |
| 31 | Plugin System | L8841 | 13KB | 4 | ~11 | 3 |
| 32 | BasePlugin & PluginManager | L9166 | 10KB | 2 | ~8 | 12 |
| 33 | Built-in Plugins | L9465 | 9KB | 2 | ~3 | 13 |
| 34 | Real-time Communication | L9667 | 8KB | 2 | ~2 | 9 |
| 35 | WebSocket API | L9842 | 9KB | 2 | ~2 | 16 |
| 36 | Browser Instrumentation & Logging | L10022 | 10KB | 2 | ~8 | 13 |
| 37 | UI Dashboard | L10238 | 7KB | 2 | ~5 | 8 |
| 38 | Session Management Interface | L10416 | 9KB | 2 | ~4 | 13 |
| 39 | Generated API Client | L10575 | 7KB | 2 | ~4 | 7 |
| 40 | API Reference | L10771 | 13KB | 2 | ~24 | 10 |
| 41 | OpenAPI Schema | L11085 | 10KB | 3 | ~6 | 8 |
| 42 | Type System | L11358 | 11KB | 7 | ~2 | 10 |
| 43 | Deployment & Operations | L11669 | 14KB | 5 | ~16 | 9 |
| 44 | Container Architecture | L12077 | 18KB | 9 | ~10 | 8 |
| 45 | Storage & Persistence | L12612 | 10KB | 4 | ~4 | 13 |
| 46 | Network Configuration | L12833 | 8KB | 2 | ~4 | 12 |
| 47 | CI/CD Pipeline | L13049 | 7KB | 2 | ~2 | 6 |
| 48 | Health Checks & Monitoring | L13245 | 7KB | 4 | ~5 | 10 |
| 49 | Development Guide | L13439 | 8KB | 3 | ~3 | 5 |
| 50 | Development Environment Setup | L13687 | 10KB | 3 | ~9 | 9 |
| 51 | Architecture Deep Dive | L14008 | 14KB | 4 | ~7 | 12 |
| 52 | Configuration Validation | L14320 | 8KB | 2 | ~6 | 10 |
| 53 | Creating Custom Plugins | L14561 | 13KB | 4 | ~8 | 11 |
| 54 | Troubleshooting | L14923 | 7KB | 2 | ~4 | 11 |
| 55 | Glossary | L15104 | 7KB | 2 | ~2 | 20 |


## · Overview  (L6)
  源文件: Dockerfile, README.md, api/package.json, images/star_img.png, package-lock.json, package.json, render.yaml
  Purpose and Scope
  What is Steel Browser
    · Core Capabilities
  System Architecture
    · High-Level Component Architecture
    · Technology Stack
  Core Service Layer
  Monorepo Structure
  Key Features
  Deployment

## · System Architecture  (L199)
  源文件: api/src/services/cdp/cdp.service.ts, api/src/services/cdp/plugins/core/base-plugin.ts, api/src/services/cdp/plugins/core/plugin-manager.ts, api/src/services/session.service.ts, docs/ARCHITECTURE.md, docs/DEVELOPMENT_SETUP.md, docs/README.md, docs/TROUBLESHOOTING.md
  Overview
    · Monorepo Architecture
  Core Service Layer
    · Service Layer Architecture
  CDPService: Browser Orchestration Engine
    · CDPService Internal Architecture
  SessionService: Session Lifecycle Management
    · Session Lifecycle and State
  Plugin System Architecture
    · Plugin Lifecycle Hooks
    · Plugin Manager Coordination
  API & Communication Layer

## · Key Features  (L484)
  源文件: Dockerfile, README.md, api/src/modules/actions/actions.controller.ts, api/src/modules/actions/actions.routes.ts, api/src/modules/actions/actions.schema.ts, api/src/services/cdp/cdp.service.ts, api/src/services/cdp/plugins/core/base-plugin.ts, api/src/services/cdp/plugins/core/plugin-manager.ts, api/src/services/selenium.service.ts, api/src/utils/passthough-proxy.ts, api/src/utils/proxy.ts, images/star_img.png
  Core Browser Automation
    · Chrome DevTools Protocol (CDP)
    · Selenium WebDriver Support
  Session & State Management
    · Session Lifecycle
    · State Persistence
  Anti-Detection & Stealth Features
    · Browser Fingerprinting
    · Request Header Manipulation
  Network & Proxy Features
    · Proxy Chain Management
    · Request Interception & Filtering
  Quick Actions API
    · Scrape Endpoint
    · Screenshot & PDF
  Extensibility & Plugin System
    · Plugin Architecture
    · Chrome Extension Support
  Deployment & Operations
    · Docker Support

## · Monorepo Structure  (L763)
  源文件: api/package.json, package-lock.json, package.json, repl/README.md, repl/src/script.ts
  Overview
  Workspace Organization
  API Package Structure
    · Export Paths
  Dependency Architecture
    · API Package Peer Dependencies
  Build System
    · Build Scripts
  REPL Integration
    · REPL Script Logic
  Dependency Overrides

## · Getting Started  (L1091)
  源文件: Dockerfile, README.md, api/Dockerfile, api/entrypoint.sh, docker-compose.dev.yml, docker-compose.yml, images/star_img.png, render.yaml, ui/Dockerfile
  Installation Overview
  Installation Methods
    · Pre-built Docker Image
    · Docker Compose (Separate Services)
    · Local Node.js Development
    · Cloud Platform Deployment
  Verifying Installation
    · 1. Check API Health
    · 2. Access OpenAPI Documentation
    · 3. Test Session Creation
  Container Build Process
  Container Initialization
  Next Steps

## · Installation  (L1345)
  源文件: Dockerfile, README.md, api/Dockerfile, api/entrypoint.sh, docker-compose.dev.yml, docker-compose.yml, docs/ARCHITECTURE.md, docs/DEVELOPMENT_SETUP.md, docs/README.md, docs/TROUBLESHOOTING.md, images/star_img.png, render.yaml
  Overview
  Pre-built Docker Image
    · Basic Deployment
    · With Persistent Cache
    · Image Build Process
  Docker Compose Deployment
    · Production Deployment
    · Development Deployment
    · Service Architecture
    · Mac Silicon Compatibility
  Local Development Setup
    · Prerequisites
    · Installation Steps
    · Chrome Executable Detection
    · Custom Chrome Path
  Cloud Deployments
    · Railway Deployment
    · Render Deployment
    · Steel Cloud
  Container Initialization
  Post-Installation Verification
    · Health Check
    · API Documentation
    · CDP Debugger

## · Environment Configuration  (L1672)
  源文件: .env.example, api/.env.example, api/Dockerfile, api/entrypoint.sh, api/src/env.ts, api/src/plugins/schemas.ts, api/src/routes.ts, docker-compose.dev.yml, docker-compose.yml, ui/.env.local.example, ui/Dockerfile, ui/entrypoint.sh
  Purpose and Scope
  Configuration System Overview
    · Configuration Flow
  Configuration Sources
    · 1. System Environment Variables
    · 2. .env Files
    · 3. Docker Environment
    · 4. Runtime Overrides
  Configuration Validation
    · Validation Architecture
    · Type Transformations
  Configuration Categories
    · Server Configuration
    · Chrome Browser Configuration
    · CDP Configuration
    · Proxy Configuration
    · Logging Configuration
    · Security and Stealth Configuration
    · Storage Configuration
  Docker-Specific Configuration
    · Container Environment Variables
    · Initialization Sequence
  UI Configuration
    · UI Environment Variables
    · UI Configuration Flow
  Complete Configuration Reference
    · Environment Variables by Category
    · Configuration Access Pattern

## · Docker Deployment  (L2301)
  源文件: .dockerignore, .github/workflows/check-build.yml, Dockerfile, README.md, api/.dockerignore, api/Dockerfile, api/entrypoint.sh, docker-compose.dev.yml, docker-compose.yml, images/star_img.png, render.yaml, ui/Dockerfile
  Purpose and Scope
  Deployment Options
  Multi-Stage Build Architecture
    · API Container Build Stages
    · Combined Image Build Strategy
  Container Services and Orchestration
    · Service Architecture
  Volume Management Strategies
  Entrypoint Initialization Process
    · Initialization Sequence
  Network Configuration
  Development vs Production Compose Files
  Single Container Deployment
  Cloud Platform Deployment
    · Render.com
    · Railway

## · Core Services  (L2646)
  源文件: api/src/modules/files/files.controller.ts, api/src/modules/files/files.routes.ts, api/src/modules/files/files.schema.ts, api/src/plugins/file-storage.ts, api/src/services/cdp/cdp.service.ts, api/src/services/cdp/plugins/core/base-plugin.ts, api/src/services/cdp/plugins/core/plugin-manager.ts, api/src/services/file.service.ts, api/src/services/session.service.ts
  Service Layer Architecture
    · Service Dependency Graph
  Service Responsibilities
  CDPService
    · Core Components
    · Plugin System Hooks
  SessionService
    · Session Structure
    · Proxy Factory Pattern
  FileService
    · Archive Generation and Watching
    · File Operations API
  Service Integration Points
    · SessionService → CDPService Coordination
    · Error Handling Strategy

## · CDPService  (L2906)
  源文件: api/.prettierrc, api/src/scripts/index.ts, api/src/services/cdp/cdp.service.ts, api/src/services/cdp/errors/launch-errors.ts, api/src/services/cdp/plugins/core/base-plugin.ts, api/src/services/cdp/plugins/core/plugin-manager.ts, api/src/services/cdp/utils/error-handlers.ts, api/src/services/cdp/utils/validation.ts, api/src/utils/browser.ts, repl/package.json, ui/package.json
  Overview
  System Architecture
    · Core Component Architecture
    · Key Class Members
  Browser Lifecycle Management
    · Launch Process
    · Browser Launch Method
    · Shutdown Process
  Configuration System
    · BrowserLauncherOptions Structure
    · Default Configuration
    · Configuration Validation
    · Configuration Reuse Optimization
  Fingerprinting and Stealth Features
    · Fingerprint Generation Process
    · Stealth Features
  Request Interception and Filtering
    · Request Interception Flow
  Plugin System Integration
    · Plugin Hook Methods
  Error Handling and Retry Mechanism
    · Error Categories
    · Error Handling Utilities

## · SessionService  (L3331)
  源文件: api/src/plugins/browser-session.ts, api/src/services/context/chrome-context.service.ts, api/src/services/leveldb/sessionstorage.ts, api/src/services/session.service.ts, api/src/services/timezone-fetcher.service.ts, api/src/types/fastify.d.ts, api/src/utils/context.ts, api/src/utils/extensions.ts
  Purpose and Scope
  System Architecture
  Core Components
    · SessionService Class
    · Session Type
  Session Lifecycle Management
    · Session Creation Flow
    · startSession Method
    · Configuration Processing
  Session State Tracking
    · Active Session Management
  Session Termination
    · endSession Method
    · Cleanup Operations
  Proxy Management
    · ProxyFactory Pattern
    · Proxy Integration
  Service Orchestration
    · CDP vs Selenium Mode
    · Mode Switching on Termination
  TimezoneFetcher Integration
  State Reset Pattern

## · FileService  (L3775)
  源文件: api/src/modules/files/files.controller.ts, api/src/modules/files/files.routes.ts, api/src/modules/files/files.schema.ts, api/src/plugins/file-storage.ts, api/src/services/file.service.ts
  Purpose and Scope
  Architecture Overview
  Singleton Pattern
  File Storage Configuration
  File Operations
    · Save File
    · Download File
    · List Files
    · Delete File
  Path Security
  Archive Management System
    · Archive Creation Flow
    · Archive Creation Configuration
  File Watching System
    · Chokidar Configuration
  Integration with HTTP API
    · File Upload Processing
    · Archive Download Behavior
  Configuration and Limits
  Error Handling

## · Browser Sessions  (L4235)
  源文件: api/src/modules/sessions/sessions.controller.ts, api/src/modules/sessions/sessions.schema.ts, api/src/services/session.service.ts, Session Management API, Session Configuration, Session Storage & State, Live Session Monitoring
  Session Overview
  Session Lifecycle
  Session Configuration
  Session Storage & Persistence
  Live Session Monitoring
  Session Management Implementation

## · Session Management API  (L4421)
  源文件: api/src/modules/sessions/sessions.controller.ts, api/src/modules/sessions/sessions.routes.ts, api/src/modules/sessions/sessions.schema.ts, ui/src/steel-client/services.gen.ts, ui/src/steel-client/types.gen.ts
  Purpose and Scope
  Session Lifecycle Overview
  Core Endpoints
    · Create Session
    · List Sessions
    · Get Session Details
    · Get Browser Context
    · Release Session
  Session Details Schema
  Live Session Monitoring
    · Get Live Session Details
    · Get Session Debugger Stream
  Event Recording
    · Receive Recorded Events
  Request Flow Architecture
  Session Actions Within Sessions
  Generated Client Usage
  Error Handling

## · Session Configuration  (L4746)
  源文件: api/src/modules/sessions/sessions.controller.ts, api/src/modules/sessions/sessions.schema.ts, api/src/services/session.service.ts, api/src/types/browser.ts
  Configuration Object Overview
  Browser Server Options
  Session Context Configuration
    · Context Data Types
  Anti-Detection Configuration
    · Stealth and Fingerprinting
    · Fingerprint Injection Flow
  Request Filtering & Optimization
    · Ad Blocking
    · Bandwidth Optimization
  Browser Dimensions & Viewport
    · Mobile Device Logic
  Timezone Configuration
  User Preferences & Extensions
    · User Preferences
    · Chrome Extensions
  Complete Configuration Reference Table

## · Session Storage & State  (L4966)
  源文件: api/src/plugins/request-logger.ts, api/src/services/cdp/cdp.service.ts, api/src/services/cdp/plugins/core/base-plugin.ts, api/src/services/cdp/plugins/core/plugin-manager.ts, api/src/services/context/chrome-context.service.ts, api/src/services/context/types.ts, api/src/services/leveldb/localstorage.ts, api/src/services/leveldb/sessionstorage.ts, api/src/services/timezone-fetcher.service.ts, api/src/utils/context.ts, api/src/utils/extensions.ts
  Overview
  Session Context Data Structure
    · Cookie Data Structure
    · Storage & IndexedDB Structure
  Session Context Lifecycle
  Context Extraction Methods
    · 1. getBrowserState()
    · 2. getExistingPageSessionData() & extractStorageForPage()
    · 3. ChromeContextService & LevelDB Readers
  Context Injection
    · Phase 1: Immediate Cookie Injection
    · Phase 2: Dynamic Storage Injection
  Persistence Strategies
  Summary Table: Storage Providers

## · Live Session Monitoring  (L5170)
  源文件: api/src/modules/sessions/sessions.controller.ts, api/src/modules/sessions/sessions.schema.ts, api/src/plugins/browser-socket/casting.handler.ts, api/src/templates/live-session-streamer.ejs, api/src/types/casting.ts, api/src/utils/casting.ts
  Overview
  Live Session Monitoring Architecture
  Live Details Endpoint
    · Endpoint Specification
    · Response Schema
    · Implementation Details
  Session Streaming Interface
    · Endpoint Specification
    · Query Parameters
    · Single Page vs Multi-Page Mode
  WebSocket Streaming Channels
    · Cast Channel (Interactive Screencasting)
    · Other Streaming Channels
    · Collection Logic Flow
  Browser Session Metrics
  Error Handling and Resilience
    · Screencast Cleanup
    · Isolation

## · Quick Actions API  (L5484)
  源文件: api/src/modules/actions/actions.controller.ts, api/src/modules/actions/actions.routes.ts, api/src/modules/actions/actions.schema.ts, api/src/services/selenium.service.ts, api/src/utils/passthough-proxy.ts, api/src/utils/proxy.ts
  Overview
    · Available Endpoints
    · When to Use Quick Actions vs Sessions
  Common Request Parameters
  Request Processing Pipeline
    · Phase 1: Proxy Setup
    · Phase 2: Browser Page Acquisition
    · Phase 3: Navigation and Execution
    · Phase 4: Cleanup and Error Handling
  Per-Request Proxy Architecture
    · Internal Bypass Configuration
    · PassthroughServer Implementation
  Browser Lifecycle Management
    · Context vs Primary Page
  Performance Timing
  Schema Validation
  Route Definitions

## · Web Scraping  (L5740)
  源文件: api/src/modules/actions/actions.controller.ts, api/src/modules/actions/actions.routes.ts, api/src/modules/actions/actions.schema.ts, api/src/services/selenium.service.ts, api/src/types/turndown.d.ts, api/src/utils/passthough-proxy.ts, api/src/utils/proxy.ts, api/src/utils/schema.ts, api/src/utils/scrape/cleanHtml.ts, api/src/utils/scrape/htmlToMarkdown.ts, api/src/utils/scrape/index.ts, api/src/utils/scrape/pdfToHtml.ts
  Web Scraping Architecture
    · System Mapping: API to Code Entities
  Request Parameters
  Scraping Process Flow
  Output Formats & Transformation
    · Metadata Extraction
  PDF Handling
  Proxy Implementation
  Error Handling

## · Screenshots & PDF Generation  (L5926)
  源文件: api/src/modules/actions/actions.controller.ts, api/src/modules/actions/actions.routes.ts, api/src/modules/actions/actions.schema.ts, api/src/services/selenium.service.ts, api/src/utils/passthough-proxy.ts, api/src/utils/proxy.ts, api/src/utils/scrape/pdfToHtml.ts, api/src/utils/scrape/safeGoTo.ts
  1. Overview
  2. API Endpoints
    · 2.1 Quick Action Endpoints
  3. Request and Response Schemas
    · 3.1 Screenshot Request Schema (`ScreenshotRequest`)
    · 3.2 PDF Request Schema (`PDFRequest`)
  4. Implementation Details
    · 4.1 Screenshot Capture
    · 4.2 PDF Generation
  5. Proxy Support
    · 5.1 ProxyServer Implementation
  6. Integration with Scraping
    · 6.1 PDF to HTML Conversion
    · 6.2 Safe Navigation
  7. Performance Tracking

## · Proxy Support  (L6143)
  源文件: api/src/modules/actions/actions.controller.ts, api/src/modules/actions/actions.routes.ts, api/src/modules/actions/actions.schema.ts, api/src/services/selenium.service.ts, api/src/services/session.service.ts, api/src/utils/passthough-proxy.ts, api/src/utils/proxy.ts, api/src/utils/requests.ts
  Overview
  Proxy Architecture
  IProxyServer Interface
  ProxyServer Implementation
    · Class Structure and Routing
    · Internal Bypass Logic
    · Traffic Accounting
  PassthroughServer & makePassthrough
    · Hop-by-Hop Header Filtering
    · Request Forwarding
  Proxy Usage Patterns
    · Session-Level Proxies
    · Per-Request Overrides (Quick Actions)
  Bandwidth Optimization
  Selenium Support

## · File Management  (L6354)
  源文件: api/src/modules/files/files.controller.ts, api/src/modules/files/files.routes.ts, api/src/modules/files/files.schema.ts, api/src/plugins/file-storage.ts, api/src/services/file.service.ts
  System Overview
    · File Management Architecture
  FileService Architecture
  Storage Structure and Path Security
    · Path Validation Flow
  File Upload Flow
  File System Watching
  File Listing and Metadata
  Archive Download Mechanism
  File Deletion and Cleanup
  Configuration

## · File API  (L6569)
  源文件: api/src/modules/files/files.controller.ts, api/src/modules/files/files.routes.ts, api/src/modules/files/files.schema.ts, api/src/plugins/file-storage.ts, api/src/services/file.service.ts
  Purpose and Scope
  API Architecture
  API Endpoints Reference
  File Upload
    · Multipart Form Data
    · Binary File Upload
    · URL Download
    · Path Validation
    · File Size Limits
  File Download
    · Single File Download
    · HEAD Request Support
  File Listing
  File Deletion
    · Single File Deletion
    · Bulk Deletion
  Archive Download
    · Endpoint Behavior
    · Archive Path
  Request/Response Schemas
    · FileUploadRequest
    · FileDetails
    · MultipleFiles
  Security Considerations
    · Path Safety
    · File System Isolation
    · Error Handling
  Plugin Registration

## · Archive Management  (L7075)
  源文件: api/src/modules/files/files.controller.ts, api/src/modules/files/files.routes.ts, api/src/modules/files/files.schema.ts, api/src/plugins/file-storage.ts, api/src/services/file.service.ts
  Overview
  Architecture
    · Archive Management System Architecture
  File Watching System
    · Watcher Configuration
    · File System Event Flow
    · Event Handlers
  Automatic Archive Generation
    · Debouncing Mechanism
    · Archive Creation Process
    · Archive File Paths
    · Concurrency Handling
    · Error Handling
  Archive Download API
    · Endpoint
    · Request/Response Flow
    · Response Headers
    · Empty Archive Handling
  Integration with File Operations
    · Automatic Regeneration Triggers
  Performance Considerations
    · Compression Level
    · Atomic File Operations
  Code Entity Reference
    · FileService Class
    · FilesController Class

## · Browser Automation Features  (L7510)
  源文件: api/src/modules/actions/actions.controller.ts, api/src/modules/actions/actions.routes.ts, api/src/modules/actions/actions.schema.ts, api/src/services/cdp/cdp.service.ts, api/src/services/cdp/plugins/core/base-plugin.ts, api/src/services/cdp/plugins/core/plugin-manager.ts, api/src/services/selenium.service.ts, api/src/utils/passthough-proxy.ts, api/src/utils/proxy.ts
  Purpose and Scope
  Core Automation Architecture
    · Session Service Orchestration
  Browser Launch Configuration
    · Key Configuration Options
  Browser Launch Process
  Target and Page Management
  Request Interception and Filtering
  Browser Extensions
  CDP Integration Details
  Selenium WebDriver Support
  Anti-Detection Features
  Request Interception & Filtering
  Browser Extensions

## · CDP Integration  (L7709)
  源文件: api/src/modules/cdp/cdp.routes.ts, api/src/services/cdp/cdp.service.ts, api/src/services/cdp/instrumentation/cdp-events.ts, api/src/services/cdp/instrumentation/page-events.ts, api/src/services/cdp/instrumentation/target-manager.ts, api/src/services/cdp/instrumentation/types.ts, api/src/services/cdp/plugins/core/base-plugin.ts, api/src/services/cdp/plugins/core/plugin-manager.ts, api/src/types/enums.ts
  Overview
  CDPService Architecture
  Target Instrumentation & Events
    · Domain Enablement
    · Event Mapping
  Plugin System Lifecycle
  CDP Protocol Tracing
  WebSocket Proxying
  Debugger URL Generation

## · Selenium Support  (L7921)
  源文件: api/src/modules/actions/actions.controller.ts, api/src/modules/actions/actions.routes.ts, api/src/modules/actions/actions.schema.ts, api/src/modules/logs/logs.routes.ts, api/src/modules/logs/logs.schema.ts, api/src/modules/selenium/selenium.routes.ts, api/src/modules/selenium/selenium.schema.ts, api/src/services/selenium.service.ts, api/src/utils/passthough-proxy.ts, api/src/utils/proxy.ts
  Purpose and Scope
  Architecture Overview
  Selenium Server Lifecycle
    · Launching the Service
    · Key Functions and Configuration
  WebDriver Routing and Proxying
    · Command Injection
  Session Properties
    · Property Comparison
  Browser Actions Compatibility
    · Scrape and PDF Flow
  Proxy Handling
  Summary of Support

## · Anti-Detection Features  (L8116)
  源文件: api/src/scripts/fingerprint.js, api/src/scripts/index.ts, api/src/services/cdp/cdp.service.ts, api/src/services/cdp/plugins/core/base-plugin.ts, api/src/services/cdp/plugins/core/plugin-manager.ts, api/src/utils/browser.ts
  Purpose and Scope
  Overview
  Fingerprint Generation
    · Fingerprint Generator Library
    · Configuration Parameters
  Fingerprint Injection
    · Injection Mechanism
    · Fixed Constants and API Overrides
  Chrome Launch Arguments
    · Automation Detection Disablement
  Request Interception and Header Manipulation
    · Header Filtering
    · Request Interception Pipeline
  Plugin System Integration
  Summary of Implementation Entities

## · Request Interception & Filtering  (L8334)
  源文件: api/src/modules/sessions/sessions.controller.ts, api/src/modules/sessions/sessions.schema.ts, api/src/services/cdp/cdp.service.ts, api/src/services/cdp/plugins/core/base-plugin.ts, api/src/services/cdp/plugins/core/plugin-manager.ts
  Purpose and Architecture
  Request Interception Flow
  Request Interception Configuration
  Ad Blocking
    · Overview
    · Implementation
    · Blocked Hosts
    · Request Flow
  Bandwidth Optimization
    · Overview
    · Configuration Modes
    · Resource Type Filtering
    · Host and Pattern Blocking
  Header Manipulation
    · Accept-Language Removal
  Security Filtering
    · File Protocol Protection
  Implementation Details
    · Request Interception Setup
    · Handler Logic Association
  Configuration Reference
    · BrowserLauncherOptions & Schema
  Logging

## · Browser Extensions  (L8611)
  源文件: api/extensions/recorder/.gitignore, api/extensions/recorder/manifest.json, api/extensions/recorder/package-lock.json, api/extensions/recorder/package.json, api/extensions/recorder/src/background.js, api/extensions/recorder/src/inject.js, api/src/services/context/chrome-context.service.ts, api/src/services/leveldb/sessionstorage.ts, api/src/services/timezone-fetcher.service.ts, api/src/utils/context.ts, api/src/utils/extensions.ts
  Overview
  Extension Types
    · Extension Source Resolution
  Built-in Extensions: The Recorder
    · Recorder Implementation
    · WebRTC Blocking Logic
  Configuration
    · Session Creation with Extensions
  Extension Loading Mechanism
    · Launch Arguments Format
  Data Extraction and Storage
    · Storage Resolution Flow
  Extension Lifecycle

## · Plugin System  (L8841)
  源文件: api/src/services/cdp/cdp.service.ts, api/src/services/cdp/plugins/core/base-plugin.ts, api/src/services/cdp/plugins/core/plugin-manager.ts
  Purpose and Scope
  Architecture Overview
    · Plugin Architecture
  Plugin Lifecycle Hooks
    · Lifecycle Hook Reference
    · Lifecycle Event Flow
  Plugin Registration and Management
    · PluginManager Interface
    · Registration Process
    · Management Operations
  Event Dispatch Mechanism
    · Execution Characteristics
    · Error Handling Example
  Plugin Options and Configuration
    · Base Plugin Structure
    · CDPService Access
  Integration Points

## · BasePlugin & PluginManager  (L9166)
  源文件: api/src/plugins/browser-socket/handlers/cast.handler.ts, api/src/plugins/browser-socket/handlers/index.ts, api/src/services/cdp/cdp.service.ts, api/src/services/cdp/plugins/core/base-plugin.ts, api/src/services/cdp/plugins/core/index.ts, api/src/services/cdp/plugins/core/plugin-manager.ts, api/src/services/websocket-registry.service.ts, api/src/steel-browser-plugin.ts, api/src/types/index.ts, api/src/types/websocket.ts, docs/PLUGIN_DEVELOPMENT.md, ui/vite.config.ts
  Purpose and Scope
  Plugin Architecture Overview
  BasePlugin Class
    · Class Structure
    · Constructor and Service Injection
    · Lifecycle Hooks
    · Shutdown Reasons
  PluginManager Class
    · Class Structure
    · Plugin Registration and Management
    · Event Propagation Pattern
  Integration with CDPService
    · Initialization
    · Event Triggering
  Creating Custom Plugins
    · Example: Simple Hello World Plugin

## · Built-in Plugins  (L9465)
  源文件: api/src/plugins/browser-session.ts, api/src/plugins/browser-socket/handlers/cast.handler.ts, api/src/plugins/browser-socket/handlers/index.ts, api/src/plugins/browser.ts, api/src/services/cdp/instrumentation/storage/in-memory-storage.ts, api/src/services/cdp/instrumentation/storage/log-storage.interface.ts, api/src/services/cdp/instrumentation/worker-events.ts, api/src/services/websocket-registry.service.ts, api/src/steel-browser-plugin.ts, api/src/types/fastify.d.ts, api/src/types/index.ts, api/src/types/websocket.ts
  Overview
  Plugin Integration Architecture
  Logging & Storage Plugin
    · Storage Selection Logic
    · DuckDB Configuration
  Browser Instrumentation & Worker Events
  WebSocket Handler Registry
    · Default Handlers
    · Handler Registration Flow
  Plugin Lifecycle Hooks
  Summary of Configuration Options

## · Real-time Communication  (L9667)
  源文件: api/src/plugins/browser-socket/browser-socket.ts, api/src/plugins/browser-socket/casting.handler.ts, api/src/plugins/browser-socket/handlers/logs.handler.ts, api/src/plugins/browser-socket/handlers/pageId.handler.ts, api/src/plugins/browser-socket/handlers/recording.handler.ts, api/src/templates/live-session-streamer.ejs, api/src/types/casting.ts, api/src/utils/casting.ts, api/src/utils/retry.ts
  Purpose and Scope
  Architecture Overview
    · Event Emission and Routing Architecture
  Live Session Casting
    · Casting Architecture
    · Interactive Events
  WebSocket Handler System
    · Default Handlers
    · Connection Upgrade Flow
  Integration with UI Dashboard
  Summary

## · WebSocket API  (L9842)
  源文件: api/src/plugins/browser-socket/browser-socket.ts, api/src/plugins/browser-socket/casting.handler.ts, api/src/plugins/browser-socket/handlers/cast.handler.ts, api/src/plugins/browser-socket/handlers/index.ts, api/src/plugins/browser-socket/handlers/logs.handler.ts, api/src/plugins/browser-socket/handlers/pageId.handler.ts, api/src/plugins/browser-socket/handlers/recording.handler.ts, api/src/services/websocket-registry.service.ts, api/src/steel-browser-plugin.ts, api/src/templates/live-session-streamer.ejs, api/src/types/casting.ts, api/src/types/index.ts
  Purpose and Scope
  WebSocket Plugin Architecture
    · Plugin Initialization
    · Handler Interface
  Available WebSocket Endpoints
    · Live Session Streaming (Casting)
    · Logs and Recording Handlers
  Connection Lifecycle and Cleanup
  CDP WebSocket Proxy

## · Browser Instrumentation & Logging  (L10022)
  源文件: api/src/plugins/browser.ts, api/src/services/cdp/instrumentation/browser-logger.ts, api/src/services/cdp/instrumentation/cdp-events.ts, api/src/services/cdp/instrumentation/page-events.ts, api/src/services/cdp/instrumentation/storage/duckdb-storage.ts, api/src/services/cdp/instrumentation/storage/in-memory-storage.ts, api/src/services/cdp/instrumentation/storage/log-storage.interface.ts, api/src/services/cdp/instrumentation/storage/safe-json.ts, api/src/services/cdp/instrumentation/target-manager.ts, api/src/services/cdp/instrumentation/types.ts, api/src/services/cdp/instrumentation/utils.ts, api/src/services/cdp/instrumentation/worker-events.ts
  Purpose and Architecture
    · Core Components
  TargetInstrumentationManager
    · Target Lifecycle and Domain Management
  Event Capture Implementation
    · Page & Network Events
    · Console & Errors
    · Protocol Tracing (CDP Events)
  BrowserLogger
  Log Storage in DuckDB
    · Schema
    · Write Buffering
    · Configuration
  Event Types Reference

## · UI Dashboard  (L10238)
  源文件: ui/src/components/sessions/session-console/session-logs.tsx, ui/src/components/sessions/session-viewer/session-viewer.tsx, ui/src/containers/session-container.tsx, ui/src/contexts/sessions-context/sessions-context.tsx, ui/src/contexts/sessions-context/sessions-context.types.ts, ui/src/lib/query-client.ts, ui/src/main.tsx, ui/src/root-layout.tsx
  Purpose and Scope
  Architecture Overview
    · UI Component to API Mapping
  Session Management Interface
  Generated API Client
    · Client-Side Data Flow
  Technology Stack
  Development Workflow
    · Running the UI
    · Configuration

## · Session Management Interface  (L10416)
  源文件: .github/ISSUE_TEMPLATE/bug_report.md, ui/src/App.tsx, ui/src/components/header/header.tsx, ui/src/components/sessions/session-console/session-devtools.tsx, ui/src/components/sessions/session-console/session-logs.tsx, ui/src/components/sessions/session-viewer/empty-state.tsx, ui/src/components/sessions/session-viewer/session-viewer.tsx, ui/src/containers/session-container.tsx, ui/src/contexts/sessions-context/sessions-context.tsx, ui/src/contexts/sessions-context/sessions-context.types.ts, ui/src/lib/query-client.ts, ui/src/main.tsx
  Purpose and Scope
  Overview
    · Key Features
    · Technology Stack
  Session Context and State Management
    · SessionsContext Implementation
  Session Viewer Component
    · Clipboard Synchronization
  Real-time Monitoring and Logs
    · Log Processing Logic
  Debugging and DevTools
  UI Layout and Navigation

## · Generated API Client  (L10575)
  源文件: api/openapi/generate.ts, api/openapi/schemas.json, api/src/config.ts, api/src/modules/sessions/sessions.routes.ts, ui/src/steel-client/schemas.gen.ts, ui/src/steel-client/services.gen.ts, ui/src/steel-client/types.gen.ts
  Overview
  Generation Pipeline
    · API to Client Bridge
  Generated Type Definitions
    · Core Request/Response Types
  Generated Service Functions
    · Client Initialization
    · Service Function Pattern
    · Key Service Functions
  Generated JSON Schemas
  Type Safety Guarantees

## · API Reference  (L10771)
  源文件: api/.env.example, api/openapi/generate.ts, api/openapi/schemas.json, api/src/config.ts, api/src/env.ts, api/src/plugins/schemas.ts, api/src/routes.ts, ui/src/steel-client/schemas.gen.ts, OpenAPI Schema, Type System
  API Overview
  Schema Registration Architecture
  HTTP Endpoint Reference
    · Health Endpoints
    · Session Management Endpoints
    · Quick Action Endpoints
    · Session Action Endpoints
    · File Operation Endpoints
    · Logs & Monitoring Endpoints
    · CDP Integration Endpoints
  Schema Type System
  Core Request/Response Schemas
    · CreateSession Schema
    · ScrapeRequest Schema
  Environment Configuration Schema
  OpenAPI Specification Generation
  Type-Safe Client Generation

## · OpenAPI Schema  (L11085)
  源文件: api/.env.example, api/openapi/generate.ts, api/openapi/schemas.json, api/src/config.ts, api/src/env.ts, api/src/plugins/schemas.ts, api/src/routes.ts, ui/src/steel-client/schemas.gen.ts
  Purpose and Architecture
    · System Data Flow
  Schema Plugin Registration
    · Schema Aggregation
    · Fastify Registration
    · OpenAPI Configuration
  Schema Definition Structure
    · Schema Organization by Module
    · Common Schema Patterns
  OpenAPI Document Generation
    · Generation Process
    · Server URL Injection
  Client Code Generation
    · Generated Service Functions
    · Generated TypeScript Types
    · Generated Schema Objects
  API Documentation UI
    · Scalar Configuration
    · Accessing Documentation
  Environment Integration
    · Environment Variables

## · Type System  (L11358)
  源文件: api/.env.example, api/src/env.ts, api/src/modules/sessions/sessions.controller.ts, api/src/modules/sessions/sessions.schema.ts, api/src/plugins/schemas.ts, api/src/routes.ts, api/src/services/cdp/utils/validation.ts, api/src/types/browser.ts, repl/package.json, ui/package.json
  Purpose
  Architecture Overview
  Schema Definition with Zod
    · Schema Reference System
  OpenAPI Schema Generation
    · Key Schema Types
  Type-Safe Client Generation
  Runtime Validation
  Configuration Validation
    · Dimension Validation
    · Timezone Validation
    · Configuration Comparison
  Environment Variable Validation
  Type System Components
  Complex Type Examples
    · Browser Launcher Options
    · Session Details

## · Deployment & Operations  (L11669)
  源文件: Dockerfile, README.md, api/Dockerfile, api/entrypoint.sh, docker-compose.dev.yml, docker-compose.yml, images/star_img.png, render.yaml, ui/Dockerfile
  Deployment Options
  Runtime Stack
  Container Initialization Flow
  Environment Variables
    · Core Configuration
    · Network Configuration
    · Storage Configuration
    · UI Configuration
  Docker Compose Deployment
    · Production Configuration
    · Volume Mounts
  Port Configuration
  Multi-Stage Build Process
  Graceful Shutdown
  Operational Considerations
    · Resource Requirements
    · Container Lifecycle
    · Debugging and Logging
    · Health Checks

## · Container Architecture  (L12077)
  源文件: .dockerignore, .github/workflows/check-build.yml, api/.dockerignore, api/Dockerfile, api/entrypoint.sh, docker-compose.dev.yml, docker-compose.yml, ui/Dockerfile
  Overview
  API Container Multi-Stage Build
    · Stage 1: Base Image (`base`)
    · Stage 2: Build Stage (`build`)
    · Stage 3: Production Stage (`production`)
  Container Initialization Process
    · Initialization Functions
    · Final Execution
  Runtime Process Architecture
    · Process Lifecycle
  UI Container Architecture
  Docker Compose Orchestration
    · Service Definitions
    · Network Configuration
    · Volume Strategy
  Development vs Production Configuration
  Container Lifecycle Sequence

## · Storage & Persistence  (L12612)
  源文件: api/Dockerfile, api/entrypoint.sh, api/src/modules/files/files.controller.ts, api/src/modules/files/files.routes.ts, api/src/modules/files/files.schema.ts, api/src/plugins/file-storage.ts, api/src/services/cdp/instrumentation/storage/duckdb-storage.ts, api/src/services/cdp/instrumentation/storage/safe-json.ts, api/src/services/cdp/instrumentation/utils.ts, api/src/services/file.service.ts, docker-compose.dev.yml, docker-compose.yml
  Volume Strategy Overview
    · Storage Strategy Comparison
  Puppeteer Cache Management
    · Cache Directory Configuration
    · Browser Binary Storage
  Log Storage
    · DuckDB Persistent Storage
  Session File Storage
    · File Service Architecture
  Export Files Storage
    · Temporary Export Volume
  Data Persistence Summary

## · Network Configuration  (L12833)
  源文件: .env.example, .github/workflows/build-docker.yml, api/Dockerfile, api/entrypoint.sh, api/nginx.conf, docker-compose.dev.yml, docker-compose.yml, ui/.env.local.example, ui/Dockerfile, ui/entrypoint.sh, ui/nginx.conf.template, ui/src/env.ts
  Overview
  Port Mappings and Nginx Proxying
    · Container Port Exposure
    · API Internal Proxy (Port 9223)
    · UI Proxy (Port 80)
  WebSocket Connectivity
    · Protocol Upgrades
    · Data Flow for Live Streaming
  Docker Network Architecture
    · Bridge Network Topology
    · Environment-Based Discovery
  Network Environment Variables
    · Core Configuration
    · Proxy and Bypass
  SSL/TLS and Production Considerations
    · External Termination
    · Production Build Flow

## · CI/CD Pipeline  (L13049)
  源文件: .github/labeler.yml, .github/workflows/build-docker.yml, .github/workflows/pr-checks.yml, .github/workflows/release.yml, api/nginx.conf, ui/src/env.ts
  Purpose and Scope
  Overview
  Workflow Architecture
    · Build and Push Workflow
  Pull Request Quality Checks
    · Validation Logic
  Release and Versioning
    · Automatic Version Bumping
    · Changelog Generation
  Docker Image Build Pipeline
    · Image Types
  Multi-Platform Build Configuration
    · Platform Support
    · Build Command Structure
  Container Registry Publishing
    · GitHub Container Registry (GHCR)
  Related Pages

## · Health Checks & Monitoring  (L13245)
  源文件: Dockerfile, README.md, api/.env.example, api/src/env.ts, api/src/plugins/schemas.ts, api/src/routes.ts, api/src/telemetry/noop.ts, api/src/telemetry/tracer.ts, images/star_img.png, render.yaml
  Overview
  Health Check Endpoint
    · Health Check Configuration
  Session Monitoring API
    · Session Details Endpoint
    · Session Details Schema
  Live Browser State Monitoring
    · Live Session Details Data Flow
    · Browser State Object
  Telemetry & Tracing
    · Tracer Implementation
    · Tracing Utilities
  Operational Configuration
  Monitoring Released Sessions

## · Development Guide  (L13439)
  源文件: CONTRIBUTING.md, docs/ARCHITECTURE.md, docs/DEVELOPMENT_SETUP.md, docs/README.md, docs/TROUBLESHOOTING.md
  Monorepo Structure
  Core Service Architecture
    · Key Service Classes
  Development Workflow
    · API Development Workflow
  Plugin System Architecture
    · Plugin Lifecycle Hooks
  Configuration and Environment
  Debugging Techniques
    · Enable Debug Logging
    · Browser Debugging
    · Node.js Inspector
  Troubleshooting Common Issues
    · Browser Launch Failures
    · Port Conflicts

## · Development Environment Setup  (L13687)
  源文件: api/package.json, api/src/index.ts, api/src/plugins/selenium.ts, api/tsconfig.json, docs/ARCHITECTURE.md, docs/DEVELOPMENT_SETUP.md, docs/README.md, docs/TROUBLESHOOTING.md, package-lock.json
  Prerequisites
  Development Workflow Architecture
    · Development Flow Overview
  Docker-based Development
    · Using docker-compose.dev.yml
    · Port Mappings
  Local Node.js Development
    · Installation and Setup
    · Workspace Structure
  NPM Script Reference
    · API Workspace Scripts
    · Root and UI Scripts
  Chrome Executable Configuration
    · Required Paths
    · Environment Variables
  Hot Reload and Live Development
    · API Server Auto-restart
    · Vite Hot Module Replacement (HMR)
    · Docker Volume Mounts
  Debugging Setup
    · Chrome DevTools Protocol Access
    · Node.js Debugging
    · REPL Testing
  Building for Production

## · Architecture Deep Dive  (L14008)
  源文件: api/src/plugins/browser.ts, api/src/services/cdp/cdp.service.ts, api/src/services/cdp/instrumentation/storage/in-memory-storage.ts, api/src/services/cdp/instrumentation/storage/log-storage.interface.ts, api/src/services/cdp/instrumentation/worker-events.ts, api/src/services/cdp/plugins/core/base-plugin.ts, api/src/services/cdp/plugins/core/plugin-manager.ts, api/src/services/session.service.ts, docs/ARCHITECTURE.md, docs/DEVELOPMENT_SETUP.md, docs/README.md, docs/TROUBLESHOOTING.md
  Purpose and Scope
  Service Layer Architecture
    · Core Services Overview
    · Service Responsibilities
    · Service Communication Patterns
  Dependency Injection via Fastify Plugins
    · Plugin Registration Flow
    · Decorated Services and Hooks
  Event-Driven Architecture
    · EventEmitter Pattern in CDPService
    · Plugin Lifecycle Architecture
  Error Handling Strategies
    · Categorized Error Types
    · Three-Tier Error Handling Functions
  Resource Lifecycle Management
    · Browser Instance Lifecycle
    · Cleanup Patterns
    · Memory Management Patterns

## · Configuration Validation  (L14320)
  源文件: api/.env.example, api/.prettierrc, api/src/env.ts, api/src/plugins/schemas.ts, api/src/routes.ts, api/src/services/cdp/errors/launch-errors.ts, api/src/services/cdp/utils/error-handlers.ts, api/src/services/cdp/utils/validation.ts, repl/package.json, ui/package.json
  Purpose and Scope
  Validation Functions Overview
  validateLaunchConfig
    · Validation Rules
    · Dimensions Validation
    · Proxy URL Validation
  validateTimezone
    · Validation Flow
  isSimilarConfig
    · Configuration Normalization
    · Comparison Logic
  Error Handling and Execution Utilities
    · Launch Error Types
  Environment Validation
    · Key Environment Schemas

## · Creating Custom Plugins  (L14561)
  源文件: api/src/plugins/browser-socket/handlers/cast.handler.ts, api/src/plugins/browser-socket/handlers/index.ts, api/src/services/cdp/cdp.service.ts, api/src/services/cdp/plugins/core/base-plugin.ts, api/src/services/cdp/plugins/core/plugin-manager.ts, api/src/services/websocket-registry.service.ts, api/src/steel-browser-plugin.ts, api/src/types/index.ts, api/src/types/websocket.ts, docs/PLUGIN_DEVELOPMENT.md, ui/vite.config.ts
  Overview
  Plugin Architecture
  BasePlugin Class
  Lifecycle Hooks
  Creating a Custom Plugin: Step-by-Step
    · Step 1: Create Plugin Class
    · Step 2: Implement Lifecycle Hooks
    · Step 3: Access CDPService
  Registering Your Plugin
    · Registration with PluginManager
    · Example Registration
  Error Handling
  Unregistering and Retrieval
  Shutdown Reasons

## · Troubleshooting  (L14923)
  源文件: Dockerfile, README.md, api/.prettierrc, api/src/services/cdp/errors/launch-errors.ts, api/src/services/cdp/utils/error-handlers.ts, docs/ARCHITECTURE.md, docs/DEVELOPMENT_SETUP.md, docs/README.md, docs/TROUBLESHOOTING.md, images/star_img.png, render.yaml
  Error Handling Architecture
    · Error Categorization System
    · Execution Wrappers
  Common Issues & Solutions
    · 1. Browser Launch Failures
    · 2. Docker & Container Issues
    · 3. Network & Proxy Issues
  Debugging Techniques
    · Enabling Verbose Logs
    · System Diagnostics
  Log Analysis Patterns

## · Glossary  (L15104)
  源文件: Dockerfile, README.md, api/.env.example, api/package.json, api/src/env.ts, api/src/modules/actions/actions.controller.ts, api/src/modules/actions/actions.routes.ts, api/src/modules/actions/actions.schema.ts, api/src/plugins/schemas.ts, api/src/routes.ts, api/src/services/cdp/cdp.service.ts, api/src/services/cdp/plugins/core/base-plugin.ts
  Core Domain Concepts
    · CDP (Chrome DevTools Protocol)
    · Session
    · Fingerprinting
    · Proxy Chain
  System Architecture Mapping
  Technical Terminology
  Session Lifecycle Data Flow
  Environment & Infrastructure