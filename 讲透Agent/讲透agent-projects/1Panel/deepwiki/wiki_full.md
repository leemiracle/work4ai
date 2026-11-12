# Page: 1Panel Overview

# 1Panel Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Makefile](Makefile)
- [agent/utils/common/sqlite.go](agent/utils/common/sqlite.go)
- [core/middleware/operation.go](core/middleware/operation.go)
- [core/utils/common/sqlite.go](core/utils/common/sqlite.go)
- [frontend/src/lang/modules/en.ts](frontend/src/lang/modules/en.ts)
- [frontend/src/lang/modules/es-es.ts](frontend/src/lang/modules/es-es.ts)
- [frontend/src/lang/modules/ja.ts](frontend/src/lang/modules/ja.ts)
- [frontend/src/lang/modules/ko.ts](frontend/src/lang/modules/ko.ts)
- [frontend/src/lang/modules/ms.ts](frontend/src/lang/modules/ms.ts)
- [frontend/src/lang/modules/pt-br.ts](frontend/src/lang/modules/pt-br.ts)
- [frontend/src/lang/modules/ru.ts](frontend/src/lang/modules/ru.ts)
- [frontend/src/lang/modules/tr.ts](frontend/src/lang/modules/tr.ts)
- [frontend/src/lang/modules/zh-Hant.ts](frontend/src/lang/modules/zh-Hant.ts)
- [frontend/src/lang/modules/zh.ts](frontend/src/lang/modules/zh.ts)

</details>



## Purpose and Scope

This document provides a comprehensive overview of 1Panel, an open-source Linux server management panel. It covers the system's architecture, technology stack, core components, and major functional domains. This overview serves as an entry point for understanding how the system is structured and how its components interact.

For detailed information on specific subsystems, see:
- Architecture and Core Systems: [#2](#2)
- Internationalization: [#3](#3)
- Website Management: [#5](#5)
- Application Management: [#6](#6)
- Infrastructure Management: [#7](#7)

**Sources:** [frontend/package.json:1-80](), [frontend/src/main.ts:1-50](), [frontend/src/views/app-store/apps/index.vue:1-50]()

## What is 1Panel?

1Panel is a comprehensive web-based management platform for Linux servers that provides unified control over server management tasks including application deployment, website hosting, container orchestration, database administration, file management, and AI/ML infrastructure. The platform is built on a three-tier architecture with a Vue 3 frontend, dual Go-based backend services (Core and Agent), and integration with external systems like Docker, Nginx/OpenResty, database engines, and GPU infrastructure.

The system features AI capabilities including agent management, model deployment (Ollama integration), GPU/XPU monitoring (nvidia-smi, xpu-smi), and MCP (Model Context Protocol) server management. It supports 10 languages through a comprehensive i18n system and uses a task-based async execution system for long-running operations with real-time progress updates.

**Architecture Highlights:**
- **Core Server** (port 9999): Authentication, licensing, system settings
- **Agent Server** (port 10000): Resource operations, infrastructure management
- **Multi-Node Support**: Master/agent topology with distributed deployments
- **Three SQLite Databases**: `core.db`, `xpack.db`, `agent.db`

**Sources:** [frontend/package.json:1-10](), [frontend/src/lang/modules/zh.ts:362-392](), [frontend/src/lang/modules/en.ts:375-406]()

## Technology Stack

### Frontend Stack (Vue 3 + TypeScript)

| Technology | Version | Purpose |
|------------|---------|---------|
| `vue` | 3.4.27 | Core UI framework with Composition API |
| `typescript` | 5.3.3 | Type safety and interfaces |
| `vite` | 5.0.x | Build tool with fast HMR |
| `element-plus` | 2.11.9 | UI component library |
| `pinia` | 2.1.7 | State management with persistence |
| `axios` | 1.7.2 | HTTP client for API communication |
| `monaco-editor` | 0.53.0 | Code editor (10+ file tabs) |
| `@xterm/xterm` | 5.5.0 | Terminal emulator |
| `echarts` | 5.5.0 | Charts via v-charts wrapper |
| `vue-i18n` | Latest | Internationalization (10 languages) |
| `fit2cloud-ui-plus` | 1.2.4 | Base component library |

**Sources:** [frontend/package.json:22-58]()

### Backend Stack (Go 1.22)

**Core Server Dependencies:**
- `gin-gonic/gin`: Web framework for HTTP routing
- `gorm.io/gorm`: ORM for database operations
- `glebarez/sqlite`: SQLite3 driver for `core.db` and `xpack.db`
- `golang-jwt/jwt`: JWT token generation and validation
- `robfig/cron/v3`: Scheduler for cronjobs

**Agent Server Dependencies:**
- `gin-gonic/gin`: Web framework
- `gorm.io/gorm`: ORM layer
- `glebarez/sqlite`: SQLite3 driver for `agent.db`
- `docker/docker`: Docker SDK for container management
- Custom Nginx parser for config manipulation
- `go-acme/lego`: ACME client supporting 50+ DNS providers
- GPU integration: nvidia-smi, xpu-smi CLI tools

**Build Configuration:**
```makefile
# From Makefile
GOCMD=go
GOBUILD=$(GOCMD) build
BUILD_PATH=$(BASE_PATH)/build
CORE_NAME=1panel-core
AGENT_NAME=1panel-agent

# Cross-compilation support
build_core_on_linux: CGO_ENABLED=0 GOOS=$(GOOS) GOARCH=$(GOARCH)
build_agent_on_linux: CGO_ENABLED=0 GOOS=$(GOOS) GOARCH=$(GOARCH)
```

**Sources:** [frontend/package.json:22-58](), [Makefile:1-50](), [core/utils/common/sqlite.go:42-68](), [agent/utils/common/sqlite.go:62-91]()

## System Architecture

### Core/Agent Split Architecture

1Panel implements a dual-server architecture separating system-wide concerns from operational tasks:

```mermaid
graph TB
    subgraph "Frontend"
        Browser["Web Browser"]
        VueApp["Vue 3 Application<br/>frontend/src/main.ts"]
        I18N["i18n System<br/>10 languages<br/>zh.ts, en.ts, etc"]
        Store["Pinia Store<br/>currentNode tracking"]
        APIClient["API Client<br/>axios + TypeScript"]
    end
    
    subgraph "Core_Server"["Core Server :9999"]
        CoreAPI["Core API<br/>/api/v2/core/*"]
        CoreDB[("core.db<br/>SQLite")]
        XpackDB[("xpack.db<br/>SQLite")]
        License["License Management<br/>Node binding"]
        Settings["System Settings"]
        UserAuth["Authentication<br/>Password/MFA/Passkey"]
    end
    
    subgraph "Agent_Server"["Agent Server :10000"]
        AgentAPI["Agent API<br/>/api/v2/*"]
        AgentDB[("agent.db<br/>SQLite")]
        
        AppMgmt["App Management<br/>app.ts"]
        WebMgmt["Website Management<br/>website.ts"]
        DBMgmt["Database Management<br/>database.ts"]
        ContainerMgmt["Container Management<br/>container.ts"]
        FileMgmt["File Management<br/>file.ts"]
        CronMgmt["Cronjob Management<br/>cronjob.ts"]
        AIMgmt["AI Management<br/>agents, models, GPU"]
    end
    
    subgraph "External"
        Docker["Docker Engine"]
        Nginx["Nginx/OpenResty"]
        AppStore["App Store<br/>1panel.json"]
        DNSProviders["DNS Providers<br/>50+ ACME"]
        GPUDrivers["GPU Drivers<br/>nvidia-smi/xpu-smi"]
    end
    
    Browser --> VueApp
    VueApp --> I18N
    VueApp --> Store
    VueApp --> APIClient
    
    APIClient -->|"Core operations"| CoreAPI
    APIClient -->|"Agent operations"| AgentAPI
    
    CoreAPI --> CoreDB
    CoreAPI --> XpackDB
    CoreAPI --> License
    CoreAPI --> Settings
    CoreAPI --> UserAuth
    CoreAPI -.->|"reads metrics"| AgentDB
    
    AgentAPI --> AgentDB
    AgentAPI --> AppMgmt
    AgentAPI --> WebMgmt
    AgentAPI --> DBMgmt
    AgentAPI --> ContainerMgmt
    AgentAPI --> FileMgmt
    AgentAPI --> CronMgmt
    AgentAPI --> AIMgmt
    
    AppMgmt --> Docker
    AppMgmt --> AppStore
    WebMgmt --> Nginx
    WebMgmt --> DNSProviders
    ContainerMgmt --> Docker
    DBMgmt --> Docker
    AIMgmt --> GPUDrivers
```

**Key Architecture Decisions:**
- **Core Server**: Stateless operations, authentication, license enforcement, cross-node aggregation
- **Agent Server**: Stateful resource management, infrastructure operations, task execution
- **Database Separation**: Three SQLite databases via `glebarez/sqlite` driver
  - `core.db`: System settings, users, licenses (via [core/utils/common/sqlite.go:15-68]())
  - `xpack.db`: Extended features, node management
  - `agent.db`: Resource state, operational data (via [agent/utils/common/sqlite.go:16-105]())
- **SQLite Configuration**: 4 max open connections, 1 idle, 15min idle timeout, 1hr max lifetime

**Sources:** [core/utils/common/sqlite.go:15-68](), [agent/utils/common/sqlite.go:16-105](), [frontend/src/main.ts:1-50](), [frontend/src/api/modules/setting.ts:1-30](), [frontend/src/api/modules/app.ts:1-30]()

### Request-Response Flow

```mermaid
sequenceDiagram
    participant User
    participant VueComponent["Vue Component<br/>e.g., apps/index.vue"]
    participant APIModule["API Module<br/>e.g., app.ts"]
    participant BackendAPI["Backend API<br/>/api/v2/*"]
    participant TaskSystem["Task System"]
    participant ExternalSystem["External System"]
    
    User->>VueComponent: "Trigger action"
    VueComponent->>VueComponent: "Validate form data<br/>form-rules.ts"
    VueComponent->>APIModule: "Call API method"
    APIModule->>APIModule: "Base64 encode secrets"
    APIModule->>BackendAPI: "HTTP request with DTO"
    
    alt Short Operation
        BackendAPI->>ExternalSystem: "Execute directly"
        ExternalSystem-->>BackendAPI: "Result"
        BackendAPI-->>APIModule: "Response"
        APIModule-->>VueComponent: "Data"
        VueComponent->>User: "Show result (MsgSuccess)"
    else Long Operation
        BackendAPI->>TaskSystem: "Create task with UUID"
        TaskSystem-->>BackendAPI: "Task ID"
        BackendAPI-->>APIModule: "Task ID response"
        APIModule-->>VueComponent: "Task ID"
        VueComponent->>VueComponent: "Open TaskLog dialog"
        
        par Async Execution
            TaskSystem->>ExternalSystem: "Execute steps"
            ExternalSystem-->>TaskSystem: "Progress updates"
        and UI Polling
            VueComponent->>BackendAPI: "Poll task status"
            BackendAPI->>TaskSystem: "Query task"
            TaskSystem-->>BackendAPI: "Status/logs"
            BackendAPI-->>VueComponent: "Real-time updates"
        end
        
        TaskSystem->>TaskSystem: "Complete"
        VueComponent->>User: "Show completion"
    end
```

**Sources:** [frontend/src/api/modules/app.ts:1-150](), [frontend/src/global/form-rules.ts:1-50](), [frontend/src/utils/util.ts:1-100]()

## Major Functional Domains

1Panel organizes functionality into nine major domains:

### 1. Infrastructure Management

Real-time monitoring with GPU support:
- **Dashboard**: CPU/Memory/Disk/Network metrics via `/dashboard/current/:io/:net` endpoint
- **System Info**: Hostname, OS version, kernel, uptime (from `/proc`, `/sys`)
- **GPU Monitoring**: NVIDIA/XPU metrics via nvidia-smi/xpu-smi integration
- **Process Tracking**: CPU and memory top 5 processes

**i18n Keys**: `home.*` (from [frontend/src/lang/modules/zh.ts:394-464](), [frontend/src/lang/modules/en.ts:408-478]())

### 2. Application Ecosystem

One-click Docker Compose deployments:
- **App Store**: Browse/search remote catalog, tags for categorization
- **Installation**: Dynamic parameter form generation via `AppInstallForm`
- **Runtime Environments**: PHP/Node/Python/Go version management
- **Installed Apps**: Start/stop/update, parameter reconfiguration

**Code Entities**: `App.AppDTO`, `App.AppInstall`, `SearchAppReq` from [frontend/src/api/interface/app.ts:1-100]()  
**i18n Keys**: `apps.*` from [frontend/src/lang/modules/zh.ts:654-800]()

### 3. Container Platform

Full Docker functionality via Docker SDK:
- **Container Operations**: Create/start/stop with resource limits
- **Image Management**: Pull/push/build with multi-tag support
- **Network Management**: Bridge/host/custom networks
- **Volume Management**: Persistent storage, NFS support
- **Docker Compose**: Multi-container orchestration

**i18n Keys**: `container.*` from [frontend/src/lang/modules/zh.ts:801-1094]()

### 4. Web Services

Nginx configuration with automated SSL:
- **6 Website Types**: static, runtime, deployment, proxy, stream, subsite
- **Nginx Config**: Rewrite rules, proxy settings, custom scopes
- **SSL Certificates**: ACME automation with 50+ DNS providers (via go-acme/lego)
- **Domain Management**: Multi-domain, wildcard support

**i18n Keys**: `website.*` from language files

### 5. Data Services

Multi-DBMS support with unified backup:
- **MySQL/MariaDB**: Cluster support, performance tuning
- **PostgreSQL**: Replication, super user binding
- **Redis**: CLI integration, persistence configuration
- **MongoDB**: Basic operations
- **Database Backup**: Auto retention, encrypted backups

**i18n Keys**: `database.*` from [frontend/src/lang/modules/zh.ts:477-653]()

### 6. AI/ML Infrastructure

AI agent deployment and GPU monitoring:
- **AI Agents**: Chat integration with Feishu/Lark channels
- **Model Management**: Ollama integration, OpenAI API support
- **GPU Monitoring**: NVIDIA/XPU metrics (temperature, memory, utilization)
- **MCP Servers**: stdio/SSE/HTTP transport mechanisms
- **AI Proxy**: Load balancing with IP whitelist

**i18n Keys**: `aiTools.*` from [frontend/src/lang/modules/zh.ts:654-800]()

### 7. Storage & Files

Web-based file management with code editor:
- **File Browser**: Multi-tab interface (7 tabs max)
- **Code Editor**: Monaco with 10+ file tabs, syntax highlighting
- **File Operations**: Compress/upload/convert (40+ operations)
- **Backup Management**: Snapshots with restore/rollback

**i18n Keys**: `file.*` from language files

### 8. Automation

Scheduled tasks with robust execution:
- **Cronjobs**: 10 task types (shell, backup, database, snapshot, cleanup, etc.)
- **Script Library**: Bash/Python script management
- **Task Logging**: Real-time progress via SSE
- **System Snapshots**: Full backup/rollback capabilities

**Scheduler**: `robfig/cron/v3` for cron expression parsing  
**i18n Keys**: `cronjob.*` from [frontend/src/lang/modules/zh.ts:1095-1200]()

### 9. System Administration

Multi-factor authentication and settings:
- **Settings**: Network/security/API configuration
- **User Management**: MFA (TOTP 6-digit), Passkey (WebAuthn)
- **License System**: Node-level binding with feature gating
- **System Updates**: Version management, upgrade workflow

**i18n Keys**: `settings.*`, `login.*` from [frontend/src/lang/modules/zh.ts:192-220]()

**Sources:** [frontend/src/lang/modules/zh.ts:362-1200](), [frontend/src/lang/modules/en.ts:375-800](), [frontend/src/api/interface/app.ts:1-100]()

## Internationalization Architecture

1Panel supports 10 languages through a dual-layer i18n system:

```mermaid
graph TB
    subgraph "Frontend_i18n"["Frontend i18n (Total Score: 1488.98)"]
        ZH["zh.ts<br/>Score: 687.19<br/>Chinese"]
        EN["en.ts<br/>Score: 605.73<br/>English"]
        MS["ms.ts<br/>Malay"]
        ZHTW["zh-Hant.ts<br/>Traditional Chinese"]
        JA["ja.ts<br/>Japanese"]
        RU["ru.ts<br/>Russian"]
        PTBR["pt-br.ts<br/>Portuguese"]
        KO["ko.ts<br/>Korean"]
        TR["tr.ts<br/>Turkish"]
        ESES["es-es.ts<br/>Spanish"]
        
        FIT2CLOUD["fit2cloud-ui-plus<br/>Base locales"]
    end
    
    subgraph "Structure"["Message Structure"]
        Commons["commons:<br/>buttons, tables,<br/>validation, status"]
        Domains["Domain-specific:<br/>menu, home, database,<br/>container, cronjob,<br/>etc."]
    end
    
    subgraph "Backend_i18n"["Backend i18n (Score: 159.47)"]
        BackendYAML["YAML files<br/>10 languages"]
        
        ErrMessages["Err* prefix<br/>150+ error variants"]
        TaskMessages["Task* prefix<br/>24+ operation types"]
        SnapshotMessages["Snap* prefix<br/>Recovery flow"]
    end
    
    FIT2CLOUD --> ZH
    FIT2CLOUD --> EN
    
    ZH --> Commons
    ZH --> Domains
    EN --> Commons
    EN --> Domains
    
    BackendYAML --> ErrMessages
    BackendYAML --> TaskMessages
    BackendYAML --> SnapshotMessages
```

**Language Files:**
- Primary: `zh.ts` (Chinese), `en.ts` (English)
- Additional: `ms.ts`, `zh-Hant.ts`, `ja.ts`, `ru.ts`, `pt-br.ts`, `ko.ts`, `tr.ts`, `es-es.ts`

**Message Organization:**
```typescript
// Example structure from zh.ts and en.ts
{
  commons: {
    button: { create, edit, delete, ... },
    table: { name, type, status, ... },
    status: { running, stopped, error, ... },
    rule: { validation patterns }
  },
  menu: { home, apps, website, database, ... },
  database: { manage, create, backup, ... },
  container: { image, network, volume, ... },
  // ... domain-specific messages
}
```

**Sources:** [frontend/src/lang/modules/zh.ts:1-100](), [frontend/src/lang/modules/en.ts:1-100](), [frontend/src/lang/modules/ms.ts:1-50](), [frontend/src/lang/modules/zh-Hant.ts:1-50](), [frontend/src/lang/modules/ja.ts:1-50]()

## Frontend Component Architecture

### Core Components Mapping

```mermaid
graph LR
    subgraph "App_Store_Module"["App Store Module"]
        AppsIndex["apps/index.vue<br/>App catalog browser"]
        AppsDetail["detail/index.vue<br/>App details"]
        AppsInstall["detail/install/index.vue<br/>Installation form"]
        AppsParams["detail/params/index.vue<br/>Parameter form generator"]
        InstalledIndex["installed/index.vue<br/>Installed apps list"]
        InstalledDetail["installed/detail/index.vue<br/>App configuration"]
        InstalledUpgrade["installed/upgrade/index.vue<br/>Upgrade manager"]
    end
    
    subgraph "API_Layer"["API Layer"]
        AppAPI["api/modules/app.ts<br/>App operations"]
        SettingAPI["api/modules/setting.ts<br/>Settings operations"]
        AppInterface["api/interface/app.ts<br/>App.AppDTO<br/>App.AppInstall<br/>App.AppItem"]
        SettingInterface["api/interface/setting.ts<br/>Setting.SettingInfo"]
    end
    
    subgraph "Utilities"["Utilities"]
        FormRules["global/form-rules.ts<br/>Validation rules"]
        Utils["utils/util.ts<br/>deepCopy, encryption"]
        Router["utils/router.ts<br/>routerToPathWithQuery"]
    end
    
    AppsIndex --> AppAPI
    AppsDetail --> AppAPI
    AppsInstall --> AppAPI
    InstalledIndex --> AppAPI
    InstalledDetail --> AppAPI
    InstalledUpgrade --> AppAPI
    
    AppAPI --> AppInterface
    SettingAPI --> SettingInterface
    
    AppsInstall --> FormRules
    InstalledDetail --> FormRules
    AppsParams --> FormRules
    
    AppsIndex --> Utils
    InstalledIndex --> Utils
```

**Sources:** [frontend/src/views/app-store/apps/index.vue:1-70](), [frontend/src/views/app-store/installed/index.vue:1-150](), [frontend/src/api/modules/app.ts:1-80](), [frontend/src/api/interface/app.ts:1-100]()

### State Management

1Panel uses Pinia for state management with persistent state plugin:

**Dependencies:**
- `pinia` (^2.1.7) - Core state management
- `pinia-plugin-persistedstate` (^1.6.1) - State persistence

**Sources:** [frontend/package.json:49-50]()

## Key Features Overview

### 1. Application Store System

**Importance Score:** 351.06

Manages application discovery, installation, and lifecycle:
- Remote/local/custom app repositories
- Dynamic parameter form generation (`params/index.vue`)
- Multi-node deployment support
- Dependency injection
- Backup/restore operations

**Key Components:**
- `App.AppDTO` - Application metadata
- `App.AppInstall` - Installation configuration
- `AppInstallForm` - Dynamic form component

**Sources:** [frontend/src/views/app-store/apps/index.vue:1-150](), [frontend/src/views/app-store/detail/install/index.vue:1-100](), [frontend/src/api/interface/app.ts:1-100]()

### 2. Website Management System

**Importance Score:** 485.43 (combined)

Comprehensive website hosting with:
- 6 website types (deployment, runtime, static, proxy, subsite, stream)
- OpenResty/Nginx configuration engine
- SSL automation (ACME/manual/CA)
- Domain management

See [Website Management System](#5) for details.

### 3. Settings & Configuration

**Importance Score:** 429.82

Central configuration system handling:
- Global settings
- License management with node binding
- Authentication (password, MFA, passkey)
- API security (keys, IP whitelist)
- Panel SSL configuration
- Upgrade management
- Snapshot configuration

**API Endpoints:**
```typescript
// From setting.ts
uploadLicense(oldLicense: string, params: FormData)
searchLicense(params: ReqPage)
deleteLicense(params: { ids: number })
// ... additional setting operations
```

**Sources:** [frontend/src/api/modules/setting.ts:1-100](), [frontend/src/api/interface/setting.ts:1-100]()

### 4. File Management System

**Importance Score:** 233.02

Advanced file browser with:
- Multi-tab support (7 tabs max)
- Monaco editor integration for code editing
- 40+ file operations (CRUD, compress, upload)
- Terminal integration
- Navigation history and breadcrumbs
- Favorites management

### 5. Container Management

**Importance Score:** 193.34

Docker integration providing:
- Container operations (create, start, stop, delete)
- Image management (pull, build, push, prune)
- Network and volume handling
- Docker Compose orchestration
- Resource statistics and monitoring

### 6. Database Management

**Importance Score:** 152.85

Multi-DBMS support:
- MySQL/MariaDB, Redis, PostgreSQL
- Local and remote connections
- Performance tuning and configuration editing
- Terminal access
- Backup and restore operations

### 7. Cronjob System

**Importance Score:** 162.08

Scheduled automation with:
- 12 job types (shell, backup, database, snapshot, cleanup, etc.)
- `robfig/cron/v3` scheduler
- Execution tracking and logs
- Snapshot system integration

## Build Configuration

The frontend uses Vite with specific optimization:

```typescript
// Key build configuration
{
  "scripts": {
    "dev": "node --max-old-space-size=8192 ./node_modules/.bin/vite --host",
    "build:dev": "vite build --mode development",
    "build:pro": "vite build --mode production"
  }
}
```

**Build Features:**
- Development server with hot module replacement
- Production optimization with code splitting
- Environment-specific builds (dev/test/production)
- Monaco editor integration
- TypeScript type checking

**Sources:** [frontend/package.json:6-12](), [frontend/vite.config.ts:1-100]()

## Theming System

1Panel supports light and dark modes:

**Theme Variables:**
- `--panel-color-primary` - Primary brand color
- Light mode: Default Element Plus theme
- Dark mode: Custom theme variables (`element-dark.scss`)

**Sources:** [frontend/src/styles/element-dark.scss:1-100]()

## Security Architecture

1Panel implements defense-in-depth security across six layers:

### Authentication Mechanisms

```mermaid
graph LR
    User["User Login"]
    Password["Password Auth<br/>bcrypt hashing"]
    MFA["MFA TOTP<br/>6-digit codes"]
    Passkey["WebAuthn Passkey<br/>Biometric/Hardware"]
    Session["Session Management<br/>JWT tokens"]
    
    User --> Password
    User --> MFA
    User --> Passkey
    Password --> Session
    MFA --> Session
    Passkey --> Session
```

**Code References:**
- Password validation: bcrypt hashing for secure storage
- MFA: TOTP-based 6-digit verification codes
- Passkey: WebAuthn API for biometric/hardware key authentication
- JWT: Token-based session management

**i18n Keys**: `login.mfaTitle`, `login.passkey`, `login.passkeyNotSupported` from [frontend/src/lang/modules/zh.ts:207-219]()

### Network Security Layers

1. **Safe Entrance**: SSH command required to view panel entry (`1pctl user-info`)
2. **IP Whitelist**: Per-panel and per-API-key IP restrictions
3. **Domain Binding**: Restrict access to specific domains
4. **Firewall Rules**: Port management and traffic control

**i18n Keys**: `login.safeEntrance1`, `login.errIP1`, `login.errDomain1` from [frontend/src/lang/modules/zh.ts:201-205]()

### Application Security

1. **Captcha System**: Brute force protection on login
2. **Password Policy**: Complexity enforcement (8-30 chars, letters+numbers+symbols)
3. **API Key System**: Programmatic access with per-key IP restrictions
4. **Operation Logging**: All API calls logged via [core/middleware/operation.go:28-171]()

**Validation Rules**: Defined in [frontend/src/global/form-rules.ts:1-50]() including:
- `complexityPassword`: 8-30 length, 2+ character types
- `commonPassword`: 6+ characters minimum
- `authBasicPassword`: 1-72 characters with special char support

### Data Security

1. **Encrypted Backups**: AES encryption for sensitive data
2. **Secret Management**: Base64 encoding in transit via [frontend/src/utils/util.ts:1-100]()
3. **SSL Certificates**: ACME automation with 50+ DNS providers
4. **Privileged Container Warnings**: Security alerts for dangerous operations

### Audit & Monitoring

All operations logged with structured data:
```go
// From core/middleware/operation.go:40-47
record := &model.OperationLog{
    Source:    source,
    Node:      currentNode,
    IP:        c.ClientIP(),
    Method:    strings.ToLower(c.Request.Method),
    Path:      pathItem,
    UserAgent: c.Request.UserAgent(),
}
```

**Log Types**:
- API operation logs (success/failure)
- Task execution logs (async operations)
- Login attempts (success/failure tracking)
- Resource changes (create/update/delete)

**Sources:** [core/middleware/operation.go:40-171]()

### License & Node Management

1. **License Binding**: Node-level enforcement with unique identifiers
2. **Node Management**: Master/agent topology for distributed deployments
3. **SMS Quota**: Usage tracking for notifications
4. **Feature Gating**: Pro vs Community edition differentiation

**Sources:** [frontend/src/utils/util.ts:1-100](), [frontend/src/lang/modules/zh.ts:192-220](), [frontend/src/api/modules/setting.ts:1-50](), [core/middleware/operation.go:28-171](), [frontend/src/global/form-rules.ts:1-50]()

## Conclusion

1Panel is a comprehensive server management platform built on modern web technologies (Vue 3, Go) with a focus on ease of use, multilingual support, and extensive feature coverage. Its modular architecture allows for independent development and scaling of different functional domains while maintaining a unified user experience through consistent API patterns and a robust internationalization system.

The system's design emphasizes:
- **Task-based async operations** for long-running processes
- **Real-time updates** through polling mechanisms
- **Type safety** with TypeScript interfaces
- **Component reusability** through a shared component library
- **Multilingual support** across 10 languages
- **External system integration** (Docker, Nginx, databases)

For detailed information on specific subsystems, refer to the corresponding sections in this wiki.

---

# Page: Architecture and Core Systems

# Architecture and Core Systems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Makefile](Makefile)
- [agent/utils/common/sqlite.go](agent/utils/common/sqlite.go)
- [core/middleware/operation.go](core/middleware/operation.go)
- [core/utils/common/sqlite.go](core/utils/common/sqlite.go)
- [frontend/src/api/interface/setting.ts](frontend/src/api/interface/setting.ts)
- [frontend/src/api/modules/setting.ts](frontend/src/api/modules/setting.ts)

</details>



## Purpose and Scope

This document explains 1Panel's overall system architecture, focusing on the fundamental separation between Core and Agent services, the multi-node topology, database design, and how components interact. For specific security mechanisms, see [Authentication and Security](#3). For detailed build and deployment processes, see [Build System and Development](#2.6). For frontend-specific architecture, see [Frontend Architecture](#2.4).

## Three-Tier Architecture

1Panel implements a three-tier architecture that separates concerns between presentation, system management, and infrastructure operations.

```mermaid
graph TB
    subgraph "Frontend Layer"
        VueApp["Vue 3 Application<br/>(frontend/src/)"]
        APIClient["API Client Layer<br/>(frontend/src/api/)"]
        Store["Pinia Global Store<br/>(frontend/src/store/)"]
    end
    
    subgraph "Core Backend - Port 9999"
        CoreMain["core/cmd/server/main.go"]
        CoreAPI["Core API Router<br/>(core/router/)"]
        CoreServices["Core Services<br/>(core/app/service/)"]
        CoreRepo["Core Repository<br/>(core/app/repo/)"]
        CoreDB[("core.db<br/>SQLite")]
        XpackDB[("xpack.db<br/>SQLite")]
    end
    
    subgraph "Agent Backend - Port 10000"
        AgentMain["agent/cmd/server/main.go"]
        AgentAPI["Agent API Router<br/>(agent/router/)"]
        AgentServices["Agent Services<br/>(agent/app/service/)"]
        AgentRepo["Agent Repository<br/>(agent/app/repo/)"]
        AgentDB[("agent.db<br/>SQLite")]
    end
    
    subgraph "External Systems"
        Docker["Docker Engine<br/>via SDK"]
        Nginx["Nginx/OpenResty<br/>Config Files"]
        GPU["GPU Drivers<br/>nvidia-smi/xpu-smi"]
    end
    
    VueApp --> APIClient
    APIClient --> Store
    APIClient -->|"/core/*"| CoreAPI
    APIClient -->|"/*" or "?operateNode=X"| AgentAPI
    
    CoreAPI --> CoreServices
    CoreServices --> CoreRepo
    CoreRepo --> CoreDB
    CoreRepo --> XpackDB
    CoreRepo -.reads.-> AgentDB
    
    AgentAPI --> AgentServices
    AgentServices --> AgentRepo
    AgentRepo --> AgentDB
    
    AgentServices --> Docker
    AgentServices --> Nginx
    AgentServices --> GPU
```

**Sources:** [Makefile:1-50](), [frontend/src/api/modules/setting.ts:1-223]()

## The Core/Agent Split

The system is fundamentally divided into two independent Go applications that serve distinct purposes:

### Core Service (Port 9999)

The Core service handles system-wide configuration, authentication, licensing, and node management. It acts as the central control plane.

**Responsibilities:**
- User authentication (password, MFA, passkey)
- License management and node binding
- System settings (ports, SSL, security)
- Multi-node orchestration
- Operation logging
- Session management

**Database Access Pattern:**
The Core service maintains its own databases (`core.db` and `xpack.db`) and can **read** from agent databases for monitoring purposes, but never writes to them directly.

```mermaid
graph LR
    CoreService["Core Service<br/>(core/cmd/server/main.go)"]
    CoreDB[("core.db<br/>System Settings<br/>Users/Auth")]
    XpackDB[("xpack.db<br/>Licenses<br/>Nodes")]
    AgentDB[("agent.db<br/>Read Only")]
    
    CoreService -->|Read/Write| CoreDB
    CoreService -->|Read/Write| XpackDB
    CoreService -.->|Read Only<br/>Metrics| AgentDB
```

### Agent Service (Port 10000)

The Agent service handles all infrastructure operations and resource management. It is the operational plane that interacts with Docker, Nginx, databases, and the file system.

**Responsibilities:**
- Container lifecycle management
- Website/Nginx configuration
- Database management (MySQL, PostgreSQL, Redis)
- File system operations
- Application installation from app store
- Cronjob scheduling
- AI/ML infrastructure (GPU monitoring, model management)
- Backup/snapshot operations

**Database Access Pattern:**
Each agent maintains its own `agent.db` exclusively. In multi-node deployments, each node has its own independent agent database.

**Sources:** [Makefile:12-18](), [Makefile:16-18](), [core/middleware/operation.go:218-241]()

## Database Architecture

1Panel uses SQLite for data persistence across three separate database files, each with distinct purposes:

| Database | Path | Owner | Purpose | Table Examples |
|----------|------|-------|---------|----------------|
| `core.db` | `{InstallDir}/1panel/db/core.db` | Core Service | System configuration, users, settings | `settings`, `users`, `operation_logs` |
| `xpack.db` | `{InstallDir}/1panel/db/xpack.db` | Core Service | Licensed features, nodes, SMS quota | `licenses`, `nodes`, `license_bindings` |
| `agent.db` | `{InstallDir}/1panel/db/agent.db` | Agent Service | Infrastructure resources, apps, websites | `apps`, `websites`, `containers`, `databases` |

### Database Connection Configuration

Both Core and Agent use identical SQLite connection pooling settings:

```mermaid
graph TB
    SQLiteFile["SQLite Database File"]
    GORMLayer["GORM ORM Layer<br/>(gorm.io/gorm)"]
    SQLiteDriver["SQLite Driver<br/>(glebarez/sqlite)"]
    ConnPool["Connection Pool"]
    
    SQLiteFile --> SQLiteDriver
    SQLiteDriver --> GORMLayer
    GORMLayer --> ConnPool
    
    ConnPool --> Config["MaxOpenConns: 4<br/>MaxIdleConns: 1<br/>ConnMaxIdleTime: 15min<br/>ConnMaxLifetime: 1h"]
```

Connection pool parameters are consistently configured across both services:
- `MaxOpenConns`: 4 concurrent connections
- `MaxIdleConns`: 1 idle connection
- `ConnMaxIdleTime`: 15 minutes
- `ConnMaxLifetime`: 1 hour

**Sources:** [agent/utils/common/sqlite.go:62-79](), [core/utils/common/sqlite.go:42-56]()

### Cross-Database Access Pattern

The Core service accesses agent databases for monitoring and aggregation purposes through a temporary connection mechanism:

```mermaid
sequenceDiagram
    participant Core as Core Service
    participant OpLog as Operation Logger
    participant DB as Database Selector
    participant AgentDB as agent.db
    participant CoreDB as core.db
    participant XpackDB as xpack.db
    
    Core->>OpLog: Log operation
    OpLog->>DB: Determine DB from path
    
    alt Path starts with /core
        DB->>CoreDB: Open connection
    else Path starts with /xpack
        DB->>XpackDB: Open connection
    else Default path
        DB->>AgentDB: Open connection
    end
    
    DB->>DB: Execute query
    DB->>DB: Close connection
```

The operation logger creates temporary database connections based on the request path prefix to enrich log entries with contextual data (e.g., resolving IDs to names).

**Sources:** [core/middleware/operation.go:218-241](), [core/middleware/operation.go:82-102]()

## Request Routing and Multi-Node Support

The frontend determines which backend service handles a request using two mechanisms:

### Path-Based Routing

Requests are routed based on URL path prefixes:

| Path Prefix | Target Service | Port | Example |
|-------------|---------------|------|---------|
| `/api/v2/core/*` | Core Service | 9999 | `/api/v2/core/settings/search` |
| `/api/v2/*` (other) | Agent Service | 10000 | `/api/v2/apps/search` |

### Multi-Node Query Parameter

For multi-node deployments, the frontend can target specific nodes using the `operateNode` query parameter or `CurrentNode` header:

```mermaid
sequenceDiagram
    participant Browser
    participant MasterCore as Master Core
    participant MasterAgent as Master Agent
    participant Node2Agent as Node 2 Agent
    
    Browser->>MasterCore: GET /core/settings/search
    Note over MasterCore: Core operations always<br/>go to master
    MasterCore-->>Browser: Response
    
    Browser->>MasterAgent: GET /apps/search
    Note over MasterAgent: Agent operations on<br/>master node
    MasterAgent-->>Browser: Response
    
    Browser->>Node2Agent: GET /apps/search?operateNode=2
    Note over Node2Agent: Routed to specific<br/>agent node
    Node2Agent-->>Browser: Response
```

The `operateNode` parameter allows the frontend to direct agent API calls to specific nodes in a multi-node topology, while Core API calls always route to the master node.

**Sources:** [frontend/src/api/modules/setting.ts:157-159](), [core/middleware/operation.go:38-39]()

## Component Communication Patterns

### API Client Layer

The frontend uses a centralized API client that abstracts HTTP communication:

```mermaid
graph TB
    Component["Vue Component"]
    APIModule["API Module<br/>(frontend/src/api/modules/)"]
    HTTPClient["Axios HTTP Client<br/>(frontend/src/api/index.ts)"]
    
    Component --> APIModule
    APIModule --> HTTPClient
    
    APIModule --> TimeoutEnum["Timeout Configuration<br/>T_60S: 60000ms<br/>Default: 10000ms"]
    
    HTTPClient --> Interceptors["Request Interceptors<br/>- JWT Token<br/>- CurrentNode Header<br/>- Content-Type"]
    
    Interceptors --> CoreAPI["Core API<br/>:9999/api/v2/core/*"]
    Interceptors --> AgentAPI["Agent API<br/>:10000/api/v2/*"]
```

**Extended Timeout Example:**
Certain operations like license binding require extended timeouts due to their complexity:

```typescript
// frontend/src/api/modules/setting.ts:32
export const bindLicense = (params: Setting.LicenseBind) => {
    return http.post(`/core/licenses/bind`, params, TimeoutEnum.T_60S);
};
```

**Sources:** [frontend/src/api/modules/setting.ts:1-7](), [frontend/src/api/modules/setting.ts:31-33]()

### Service Layer Pattern

Both Core and Agent follow a consistent three-layer architecture:

```mermaid
graph TB
    Router["Router Layer<br/>(router/*.go)"]
    Handler["Handler/Controller<br/>(app/api/*.go)"]
    Service["Service Layer<br/>(app/service/*.go)"]
    Repo["Repository Layer<br/>(app/repo/*.go)"]
    DB["Database<br/>(SQLite)"]
    
    Router -->|"Route Definition"| Handler
    Handler -->|"Business Logic"| Service
    Service -->|"Data Access"| Repo
    Repo -->|"GORM ORM"| DB
    
    Service -.->|"Cross-Service Calls"| Service
```

This layered approach separates concerns:
- **Router**: HTTP route definitions and middleware
- **Handler**: Request validation and response formatting
- **Service**: Business logic and orchestration
- **Repository**: Data access and query construction

## Multi-Node Topology

In enterprise deployments, 1Panel supports distributed architectures where one master node manages multiple agent nodes:

```mermaid
graph TB
    subgraph "Master Node"
        MasterUI["Web UI<br/>Central Dashboard"]
        MasterCore["Core Service<br/>Port 9999"]
        MasterAgent["Agent Service<br/>Port 10000"]
        MasterCoreDB[("core.db")]
        MasterXpackDB[("xpack.db")]
        MasterAgentDB[("agent.db")]
    end
    
    subgraph "Agent Node 1"
        Agent1Core["Core Service<br/>(License Check Only)"]
        Agent1Agent["Agent Service<br/>Port 10000"]
        Agent1DB[("agent.db")]
    end
    
    subgraph "Agent Node 2"
        Agent2Core["Core Service<br/>(License Check Only)"]
        Agent2Agent["Agent Service<br/>Port 10000"]
        Agent2DB[("agent.db")]
    end
    
    MasterUI -->|"Manage All Nodes"| MasterCore
    MasterCore -->|"License Binding"| Agent1Core
    MasterCore -->|"License Binding"| Agent2Core
    
    MasterCore -.->|"Read Metrics"| Agent1DB
    MasterCore -.->|"Read Metrics"| Agent2DB
    
    MasterCore --> MasterCoreDB
    MasterCore --> MasterXpackDB
    MasterAgent --> MasterAgentDB
    Agent1Agent --> Agent1DB
    Agent2Agent --> Agent2DB
```

### Node Management API

The Core service provides APIs for node registration and management:

```typescript
// List all nodes in the cluster
export const listAllNodes = () => {
    return http.get<Array<Setting.NodeItem>>(`/core/nodes/all`);
};

// List simplified node info for dashboard
export const listAllSimpleNodes = () => {
    return http.get<Array<Setting.SimpleNodeItem>>(`/core/nodes/simple/all`);
};
```

Each `NodeItem` contains:
- `id`: Node identifier
- `addr`: Node address
- `status`: Current status
- `version`: 1Panel version
- `isXpack`: Whether licensed features are enabled
- `isBound`: Whether a license is bound
- `name`: Node display name

**Sources:** [frontend/src/api/modules/setting.ts:47-52](), [frontend/src/api/interface/setting.ts:260-268]()

### License Binding Architecture

Licenses are bound at the node level, enabling feature gating per node:

```mermaid
graph LR
    License["License Record<br/>(xpack.db)"]
    Binding["License Binding<br/>(xpack.db)"]
    Node1["Node 1<br/>Community"]
    Node2["Node 2<br/>Pro Features"]
    Node3["Node 3<br/>Pro Features"]
    
    License --> Binding
    Binding -->|"Bound"| Node2
    Binding -->|"Bound"| Node3
    Binding -.->|"Not Bound"| Node1
```

**Binding Operations:**
- `bindLicense`: Bind a license to a node
- `unbindLicense`: Remove license binding
- `changeBind`: Move license between nodes

**Sources:** [frontend/src/api/modules/setting.ts:31-39](), [frontend/src/api/interface/setting.ts:290-300]()

## Build System Architecture

The build process compiles Core and Agent as separate binaries with optional frontend bundling:

```mermaid
graph TB
    Makefile["Makefile"]
    
    Makefile --> BuildFrontend["build_frontend<br/>npm run build:pro"]
    Makefile --> BuildCore["build_core_on_linux<br/>CGO_ENABLED=0"]
    Makefile --> BuildAgent["build_agent_on_linux<br/>CGO_ENABLED=0"]
    
    BuildFrontend --> FrontendDist["frontend/dist/<br/>Static Assets"]
    
    BuildCore --> CoreSrc["core/cmd/server/main.go"]
    BuildAgent --> AgentSrc["agent/cmd/server/main.go"]
    
    CoreSrc --> CoreBinary["build/1panel-core"]
    AgentSrc --> AgentBinary["build/1panel-agent"]
    
    FrontendDist -.embedded.-> CoreSrc
```

### Build Targets

| Target | Command | Output | Description |
|--------|---------|--------|-------------|
| `build_frontend` | `npm run build:pro` | `frontend/dist/` | Vue application bundle |
| `build_core_on_linux` | `go build core/cmd/server/main.go` | `build/1panel-core` | Core service binary |
| `build_agent_on_linux` | `go build agent/cmd/server/main.go` | `build/1panel-agent` | Agent service binary |
| `build_all` | All above | Both binaries + frontend | Complete build |

### Cross-Compilation Support

The Makefile supports building Linux binaries from macOS for development:

```makefile
build_core_on_darwin:
    cd $(CORE_PATH) \
    && CGO_ENABLED=0 GOOS=linux GOARCH=amd64 $(GOBUILD) -trimpath -ldflags '-s -w' \
       -o $(BUILD_PATH)/$(CORE_NAME) $(CORE_MAIN)
```

The `CGO_ENABLED=0` flag ensures binaries are statically linked and portable across Linux distributions.

**Sources:** [Makefile:1-50](), [Makefile:28-29](), [Makefile:31-46]()

## Key Architectural Decisions

### SQLite Over Distributed Database

The use of SQLite provides:
- **Zero-configuration**: No separate database server required
- **Simplicity**: Single-file databases easy to backup and restore
- **Performance**: Sufficient for panel workloads (4 max connections per DB)
- **Portability**: Database files can be moved between systems

Trade-off: Limited to scenarios where connection limits (4 concurrent) are acceptable.

### Core/Agent Separation

The split between Core and Agent enables:
- **Security Isolation**: Authentication/authorization separate from operations
- **Scalability**: Master node can manage hundreds of agent nodes
- **Independent Updates**: Core and Agent can be updated separately
- **Failure Isolation**: Agent crashes don't affect Core authentication

### Frontend-Driven Routing

Rather than a reverse proxy, the frontend directly routes requests to Core or Agent based on:
- Path prefix (`/core/*` vs others)
- Query parameter (`?operateNode=X`)

This approach:
- **Simplifies deployment**: No additional proxy layer
- **Enables multi-node**: Frontend can target any node
- **Reduces latency**: One less network hop
- **Clarifies responsibility**: Routing logic visible in frontend code

**Sources:** [frontend/src/api/modules/setting.ts:157-163](), [core/middleware/operation.go:36-46]()

---

# Page: System Architecture Overview

# System Architecture Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Makefile](Makefile)
- [agent/utils/common/sqlite.go](agent/utils/common/sqlite.go)
- [core/middleware/operation.go](core/middleware/operation.go)
- [core/utils/common/sqlite.go](core/utils/common/sqlite.go)
- [frontend/src/api/interface/setting.ts](frontend/src/api/interface/setting.ts)
- [frontend/src/api/modules/setting.ts](frontend/src/api/modules/setting.ts)

</details>



## Purpose and Scope

This document describes the high-level architecture of 1Panel, focusing on the three-tier design pattern and the separation of concerns between the Core and Agent backend services. It explains how the frontend communicates with backend services, the database architecture, and request routing mechanisms.

For detailed information about multi-node distributed deployments, see [Multi-Node Architecture](#2.2). For authentication and security mechanisms, see [Authentication and Security](#3). For frontend-specific architecture patterns, see [Frontend Architecture](#2.4).

## Three-Tier Architecture

1Panel implements a classic three-tier architecture with clear separation between presentation, business logic, and infrastructure operations:

```mermaid
graph TB
    subgraph "Tier 1: Frontend Layer"
        Frontend["Vue 3 Application<br/>(Vite build)<br/>frontend/"]
        APIClient["API Client Layer<br/>frontend/src/api/"]
    end
    
    subgraph "Tier 2: Core Backend"
        CoreServer["Core API Server<br/>Port 9999<br/>core/cmd/server/main.go"]
        CoreDB["core.db<br/>SQLite Database"]
        XpackDB["xpack.db<br/>SQLite Database"]
    end
    
    subgraph "Tier 3: Agent Backend"
        AgentServer["Agent API Server<br/>Port 10000<br/>agent/cmd/server/main.go"]
        AgentDB["agent.db<br/>SQLite Database"]
    end
    
    Frontend --> APIClient
    APIClient -->|"/core/*"| CoreServer
    APIClient -->|"/* (no /core prefix)"| AgentServer
    
    CoreServer --> CoreDB
    CoreServer --> XpackDB
    CoreServer -.->|"Read-only metrics"| AgentDB
    
    AgentServer --> AgentDB
```

**Sources:** [Makefile:12-18](), [frontend/src/api/modules/setting.ts:10-45]()

### Layer Responsibilities

| Layer | Port | Main Entry Point | Responsibilities |
|-------|------|-----------------|------------------|
| **Frontend** | N/A (served by Core) | `frontend/src/main.ts` | UI rendering, user interaction, state management, API orchestration |
| **Core Backend** | 9999 | `core/cmd/server/main.go` | Authentication, authorization, licensing, system settings, user management, cross-node coordination |
| **Agent Backend** | 10000 | `agent/cmd/server/main.go` | Infrastructure operations: containers, websites, databases, files, cronjobs, AI services, monitoring |

**Sources:** [Makefile:12-18](), [frontend/src/api/modules/setting.ts:64-77]()

## Backend Service Split: Core vs Agent

The backend is intentionally split into two independent Go services with distinct responsibilities:

### Core Service Architecture

```mermaid
graph TB
    CoreMain["core/cmd/server/main.go"]
    CoreAPI["Gin Web Framework<br/>Routes: /api/v2/core/*"]
    
    subgraph "Core Responsibilities"
        Auth["Authentication<br/>Password/MFA/Passkey"]
        License["License Management<br/>Node Binding"]
        Settings["System Settings<br/>Global Configuration"]
        UserMgmt["User Management<br/>Session Handling"]
        NodeCoord["Multi-Node Coordination<br/>Cross-node Metrics"]
    end
    
    subgraph "Core Databases"
        CoreDBFile["core.db<br/>{baseDir}/1panel/db/core.db"]
        XpackDBFile["xpack.db<br/>{baseDir}/1panel/db/xpack.db"]
    end
    
    CoreMain --> CoreAPI
    CoreAPI --> Auth
    CoreAPI --> License
    CoreAPI --> Settings
    CoreAPI --> UserMgmt
    CoreAPI --> NodeCoord
    
    Auth --> CoreDBFile
    License --> XpackDBFile
    Settings --> CoreDBFile
    UserMgmt --> CoreDBFile
    NodeCoord -.->|"Read-only"| AgentDBFile["agent.db"]
```

**Core API Endpoint Examples:**
- `/core/auth/login` - User authentication
- `/core/licenses/bind` - License binding to nodes
- `/core/settings/update` - System settings management
- `/core/settings/mfa` - Multi-factor authentication setup
- `/core/settings/passkey/register/begin` - WebAuthn passkey registration

**Sources:** [frontend/src/api/modules/setting.ts:10-46](), [core/middleware/operation.go:218-227]()

### Agent Service Architecture

```mermaid
graph TB
    AgentMain["agent/cmd/server/main.go"]
    AgentAPI["Gin Web Framework<br/>Routes: /api/v2/*"]
    
    subgraph "Agent Responsibilities"
        AppMgmt["App Store & Installation<br/>/apps/*"]
        WebMgmt["Website Management<br/>/websites/*"]
        ContainerMgmt["Container Operations<br/>/containers/*"]
        DBMgmt["Database Management<br/>/databases/*"]
        FileMgmt["File Operations<br/>/files/*"]
        CronMgmt["Cronjob Scheduler<br/>/cronjobs/*"]
        AIMgmt["AI Infrastructure<br/>/ai/*"]
        MonitorMgmt["System Monitoring<br/>/dashboard/*"]
    end
    
    subgraph "Agent Database"
        AgentDBFile["agent.db<br/>{baseDir}/1panel/db/agent.db"]
    end
    
    AgentMain --> AgentAPI
    AgentAPI --> AppMgmt
    AgentAPI --> WebMgmt
    AgentAPI --> ContainerMgmt
    AgentAPI --> DBMgmt
    AgentAPI --> FileMgmt
    AgentAPI --> CronMgmt
    AgentAPI --> AIMgmt
    AgentAPI --> MonitorMgmt
    
    AppMgmt --> AgentDBFile
    WebMgmt --> AgentDBFile
    ContainerMgmt --> AgentDBFile
    DBMgmt --> AgentDBFile
    FileMgmt --> AgentDBFile
    CronMgmt --> AgentDBFile
    AIMgmt --> AgentDBFile
    MonitorMgmt --> AgentDBFile
```

**Agent API Endpoint Examples:**
- `/settings/basedir` - Base directory configuration
- `/settings/search` - Agent settings retrieval
- `/settings/snapshot/create` - System snapshot creation
- `/dashboard/current/:io/:net` - Real-time system metrics

**Sources:** [frontend/src/api/modules/setting.ts:63-80](), [agent/utils/common/sqlite.go:16-33]()

### Why Two Separate Services?

The Core/Agent split provides several architectural benefits:

1. **Separation of Concerns**: Core handles authentication and authorization (stateful, security-critical), while Agent handles infrastructure operations (resource-intensive, potentially long-running).

2. **Independent Scaling**: In multi-node deployments, one Core can manage many Agent instances across different servers.

3. **Security Isolation**: Core controls access and licensing, preventing direct infrastructure manipulation without proper authentication.

4. **Database Isolation**: Separate SQLite databases prevent infrastructure operations from locking authentication/licensing database operations.

5. **Service Recovery**: If Agent crashes during a resource-intensive operation (e.g., Docker operations), Core remains available for authentication and monitoring.

**Sources:** [Makefile:31-37](), [core/middleware/operation.go:218-241]()

## Database Architecture

1Panel uses three separate SQLite databases, each with specific responsibilities:

### Database Overview

```mermaid
graph LR
    subgraph "Database Files"
        CoreDB["core.db<br/>User accounts<br/>Operation logs<br/>System settings<br/>Sessions"]
        XpackDB["xpack.db<br/>License data<br/>Node bindings<br/>SMS quotas<br/>Pro features"]
        AgentDB["agent.db<br/>Apps<br/>Websites<br/>Containers<br/>Databases<br/>Files<br/>Cronjobs<br/>Snapshots"]
    end
    
    subgraph "Access Patterns"
        CoreService["Core Service<br/>Read/Write"]
        AgentService["Agent Service<br/>Read/Write"]
    end
    
    CoreService -->|"Read/Write"| CoreDB
    CoreService -->|"Read/Write"| XpackDB
    CoreService -.->|"Read-only metrics"| AgentDB
    
    AgentService -->|"Read/Write"| AgentDB
```

**Database File Locations:**
- `{baseDir}/1panel/db/core.db` - Core database
- `{baseDir}/1panel/db/xpack.db` - Extended pack database
- `{baseDir}/1panel/db/agent.db` - Agent database

**Sources:** [core/middleware/operation.go:218-227]()

### Database Connection Management

Both services use identical connection patterns with GORM ORM:

```mermaid
graph TB
    LoadFunc["LoadDBConnByPath(fullPath, dbName)"]
    CreateDir["Create directory if missing"]
    CreateFile["Create .db file if missing"]
    OpenGORM["gorm.Open(sqlite.Open(dbPath))"]
    ConfigPool["Connection Pool Config"]
    
    LoadFunc --> CreateDir
    CreateDir --> CreateFile
    CreateFile --> OpenGORM
    OpenGORM --> ConfigPool
    
    ConfigPool --> MaxOpen["MaxOpenConns: 4"]
    ConfigPool --> MaxIdle["MaxIdleConns: 1"]
    ConfigPool --> IdleTime["ConnMaxIdleTime: 15min"]
    ConfigPool --> MaxLife["ConnMaxLifetime: 1 hour"]
```

**Connection Pool Settings:**
| Setting | Value | Purpose |
|---------|-------|---------|
| `MaxOpenConns` | 4 | Maximum concurrent database connections |
| `MaxIdleConns` | 1 | Keep one idle connection warm |
| `ConnMaxIdleTime` | 15 minutes | Idle connection timeout |
| `ConnMaxLifetime` | 1 hour | Maximum connection age |

**Sources:** [agent/utils/common/sqlite.go:62-79](), [core/utils/common/sqlite.go:42-56]()

### Database Selection Logic in Middleware

The operation logging middleware demonstrates how the system routes to different databases based on URL path:

```mermaid
graph TD
    RequestPath["Request Path Analysis"]
    PathCheck{"/core prefix?"}
    XpackCheck{"/xpack prefix?"}
    
    RequestPath --> PathCheck
    PathCheck -->|"Yes"| CoreDBPath["core.db<br/>{baseDir}/1panel/db/core.db"]
    PathCheck -->|"No"| XpackCheck
    XpackCheck -->|"Yes"| XpackDBPath["xpack.db<br/>{baseDir}/1panel/db/xpack.db"]
    XpackCheck -->|"No"| AgentDBPath["agent.db<br/>{baseDir}/1panel/db/agent.db"]
```

**Sources:** [core/middleware/operation.go:218-227]()

## Request Routing and Multi-Node Headers

The frontend API client uses specific patterns to route requests between Core and Agent services, and to specify target nodes in multi-node deployments:

### API Route Patterns

```mermaid
graph TB
    Frontend["Frontend API Client<br/>frontend/src/api/modules/setting.ts"]
    
    RouteCheck{"/core<br/>prefix?"}
    
    NodeParam{"operateNode<br/>parameter?"}
    NodeHeader{"CurrentNode<br/>header?"}
    
    Frontend --> RouteCheck
    
    RouteCheck -->|"Yes"| CoreEndpoint["Core API Server<br/>Port 9999<br/>/api/v2/core/*"]
    RouteCheck -->|"No"| AgentEndpoint["Agent API Server<br/>Port 10000<br/>/api/v2/*"]
    
    CoreEndpoint --> NodeParam
    AgentEndpoint --> NodeHeader
    
    NodeParam -->|"Present"| TargetNode["Route to specific node"]
    NodeParam -->|"Absent"| CurrentNode["Route to current node"]
    
    NodeHeader -->|"Present"| TargetNode2["Route to specific node"]
    NodeHeader -->|"Absent"| CurrentNode2["Route to current node"]
```

**Core API Pattern Examples:**
- `http.post('/core/licenses/bind', params)` → Core Server
- `http.get('/core/settings/search/available')` → Core Server
- `http.post('/core/settings/password/update', param)` → Core Server

**Agent API Pattern Examples:**
- `http.get('/settings/basedir')` → Agent Server
- `http.post('/settings/update', param)` → Agent Server
- `http.get('/settings/snapshot/load', {}, {timeout: 60s})` → Agent Server

**Sources:** [frontend/src/api/modules/setting.ts:10-96]()

### Multi-Node Request Headers

For multi-node operations, the frontend includes routing metadata:

**Query Parameter Method:**
```typescript
// Example from setting.ts
export const getAppStoreConfig = (node?: string) => {
    const params = node ? `?operateNode=${node}` : '';
    return http.get<App.AppStoreConfig>(`/core/settings/apps/store/config${params}`);
};
```

**Header-Based Method:**
The `CurrentNode` header is extracted from requests and logged:

```mermaid
graph LR
    Request["HTTP Request"]
    ExtractHeader["Extract CurrentNode header"]
    URLDecode["url.QueryUnescape(currentNodeItem)"]
    LogRecord["operation_log.node field"]
    
    Request --> ExtractHeader
    ExtractHeader --> URLDecode
    URLDecode --> LogRecord
```

**Sources:** [frontend/src/api/modules/setting.ts:157-163](), [core/middleware/operation.go:38-46]()

## Port Configuration and Network Binding

The two backend services listen on distinct ports for network separation:

| Service | Default Port | Configuration | Purpose |
|---------|-------------|---------------|---------|
| **Core** | 9999 | Configurable via settings | System management, authentication, licensing |
| **Agent** | 10000 | Configurable via settings | Infrastructure operations |

### Port Update API

The Core service provides an endpoint to dynamically update its listening port:

```typescript
export const updatePort = (param: Setting.PortUpdate) => {
    return http.post(`/core/settings/port/update`, param);
};
```

This requires the service to restart to bind to the new port.

**Sources:** [frontend/src/api/modules/setting.ts:124-126](), [frontend/src/api/interface/setting.ts:119-121]()

### Interface Binding

The system supports binding to specific network interfaces and IPv6:

```typescript
export const loadInterfaceAddr = () => {
    return http.get(`/core/settings/interface`);
};

export const updateBindInfo = (ipv6: string, bindAddress: string) => {
    return http.post(`/core/settings/bind/update`, {
        ipv6: ipv6,
        bindAddress: bindAddress
    });
};
```

**Configuration Options:**
- `ipv6`: Enable/disable IPv6 support (`"enable"` / `"disable"`)
- `bindAddress`: Specific IP address to bind to (e.g., `"0.0.0.0"`, `"127.0.0.1"`, specific interface IP)

**Sources:** [frontend/src/api/modules/setting.ts:118-123](), [frontend/src/api/interface/setting.ts:30-31]()

## Build System and Service Compilation

The Makefile defines separate build targets for Core and Agent services:

### Build Architecture

```mermaid
graph TB
    MakefileRoot["Makefile"]
    
    subgraph "Frontend Build"
        FrontendBuild["build_frontend<br/>npm install && npm run build:pro"]
        FrontendDist["frontend/dist/<br/>Static assets"]
        AssertPath["core/cmd/server/web/assets/<br/>Embedded in Core binary"]
    end
    
    subgraph "Core Build"
        CoreBuild["build_core_on_linux<br/>CGO_ENABLED=0"]
        CoreMain["core/cmd/server/main.go"]
        CoreBinary["build/1panel-core"]
    end
    
    subgraph "Agent Build"
        AgentBuild["build_agent_on_linux<br/>CGO_ENABLED=0"]
        AgentMain["agent/cmd/server/main.go"]
        AgentBinary["build/1panel-agent"]
    end
    
    MakefileRoot --> FrontendBuild
    FrontendBuild --> FrontendDist
    FrontendDist --> AssertPath
    
    MakefileRoot --> CoreBuild
    CoreBuild --> CoreMain
    CoreMain --> CoreBinary
    
    MakefileRoot --> AgentBuild
    AgentBuild --> AgentMain
    AgentMain --> AgentBinary
```

**Build Targets:**

| Target | Command | Output | Description |
|--------|---------|--------|-------------|
| `build_frontend` | `cd frontend && npm install && npm run build:pro` | `frontend/dist/` | Vite production build |
| `build_core_on_linux` | `CGO_ENABLED=0 GOOS=$(GOOS) GOARCH=$(GOARCH) go build` | `build/1panel-core` | Core service binary |
| `build_agent_on_linux` | `CGO_ENABLED=0 GOOS=$(GOOS) GOARCH=$(GOARCH) go build` | `build/1panel-agent` | Agent service binary |
| `build_all` | Sequential: frontend → core → agent | Both binaries | Complete system build |

**Key Build Flags:**
- `CGO_ENABLED=0`: Pure Go builds, no C dependencies required
- `-trimpath`: Remove file system paths from binary for reproducible builds
- `-ldflags '-s -w'`: Strip debug information for smaller binaries

**Sources:** [Makefile:28-47]()

### Cross-Platform Compilation

The Makefile supports Darwin (macOS) development with cross-compilation to Linux:

```makefile
build_core_on_darwin:
    cd $(CORE_PATH) \
    && CGO_ENABLED=0 GOOS=linux GOARCH=amd64 $(GOBUILD) \
       -trimpath -ldflags '-s -w' \
       -o $(BUILD_PATH)/$(CORE_NAME) $(CORE_MAIN)
```

This allows developers on macOS to build Linux binaries that run on the target deployment servers.

**Sources:** [Makefile:39-45]()

## Service Communication Pattern

While Core and Agent are separate processes, they can communicate through direct HTTP requests in single-node deployments:

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Core as Core API<br/>:9999
    participant Agent as Agent API<br/>:10000
    
    User->>Frontend: Login
    Frontend->>Core: POST /core/auth/login
    Core-->>Frontend: JWT token + session
    
    User->>Frontend: View dashboard
    Frontend->>Agent: GET /dashboard/current/:io/:net
    Note over Agent: CurrentNode header:<br/>empty (local node)
    Agent-->>Frontend: System metrics
    
    User->>Frontend: View node list (multi-node)
    Frontend->>Core: GET /core/nodes/all
    Note over Core: Reads agent.db from all nodes
    Core-->>Frontend: All node statuses
```

In this pattern:
1. Authentication flows exclusively through Core
2. Infrastructure operations route to Agent
3. Core can read Agent's database for metrics aggregation
4. Both services operate independently but coordinate through database access

**Sources:** [frontend/src/api/modules/setting.ts:47-77](), [core/middleware/operation.go:38-46]()

---

# Page: Multi-Node Architecture

# Multi-Node Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/app/api/v2/app.go](agent/app/api/v2/app.go)
- [agent/app/dto/file.go](agent/app/dto/file.go)
- [agent/app/dto/request/app.go](agent/app/dto/request/app.go)
- [agent/app/dto/response/app.go](agent/app/dto/response/app.go)
- [agent/app/repo/app.go](agent/app/repo/app.go)
- [agent/app/service/app.go](agent/app/service/app.go)
- [agent/app/service/app_install.go](agent/app/service/app_install.go)
- [agent/app/service/app_sync_task.go](agent/app/service/app_sync_task.go)
- [agent/app/service/app_utils.go](agent/app/service/app_utils.go)
- [agent/global/config.go](agent/global/config.go)
- [agent/init/business/business.go](agent/init/business/business.go)
- [agent/init/dir/dir.go](agent/init/dir/dir.go)
- [agent/router/ro_app.go](agent/router/ro_app.go)
- [agent/utils/appicon/appicon.go](agent/utils/appicon/appicon.go)
- [agent/utils/files/utils.go](agent/utils/files/utils.go)
- [agent/utils/req_helper/request.go](agent/utils/req_helper/request.go)
- [core/init/cron/cron.go](core/init/cron/cron.go)
- [frontend/src/api/interface/setting.ts](frontend/src/api/interface/setting.ts)
- [frontend/src/api/modules/setting.ts](frontend/src/api/modules/setting.ts)

</details>



## Purpose and Scope

This document describes 1Panel's multi-node architecture, which enables distributed deployments where a Master node provides centralized management while multiple Agent nodes handle infrastructure operations independently. This architecture allows infrastructure teams to manage hundreds of servers from a single web interface while maintaining operational isolation between nodes.

For information about the single-node architecture components, see [System Architecture Overview](#2.1). For details on authentication and security across nodes, see [Authentication and Security](#3).

---

## Architecture Overview

1Panel implements a hub-and-spoke topology where one Master node coordinates multiple Agent nodes. Each node runs its own Agent API server to manage local infrastructure, while the Master additionally runs a Core API server for system-wide configuration, licensing, and node orchestration.

### Multi-Node Topology

```mermaid
graph TB
    subgraph Master["Master Node"]
        MasterUI["Web UI<br/>Central Management Interface"]
        MasterCore["Core API Server<br/>:9999<br/>License/Settings/Auth"]
        MasterAgent["Agent API Server<br/>:10000<br/>Local Infrastructure"]
        MasterCoreDB[("core.db<br/>System Settings")]
        MasterXpackDB[("xpack.db<br/>License Data")]
        MasterAgentDB[("agent.db<br/>Local Resources")]
    end
    
    subgraph Agent1["Agent Node 1"]
        Agent1API["Agent API Server<br/>:10000"]
        Agent1DB[("agent.db<br/>Local Resources")]
        Agent1Docker["Docker Engine"]
    end
    
    subgraph Agent2["Agent Node 2"]
        Agent2API["Agent API Server<br/>:10000"]
        Agent2DB[("agent.db<br/>Local Resources")]
        Agent2Docker["Docker Engine"]
    end
    
    subgraph AgentN["Agent Node N"]
        AgentNAPI["Agent API Server<br/>:10000"]
        AgentNDB[("agent.db<br/>Local Resources")]
        AgentNDocker["Docker Engine"]
    end
    
    MasterUI -->|manages| MasterCore
    MasterUI -->|routes API| MasterAgent
    MasterUI -->|routes API| Agent1API
    MasterUI -->|routes API| Agent2API
    MasterUI -->|routes API| AgentNAPI
    
    MasterCore -->|reads metrics| MasterAgentDB
    MasterCore -->|reads metrics| Agent1DB
    MasterCore -->|reads metrics| Agent2DB
    MasterCore -->|reads metrics| AgentNDB
    
    MasterCore --> MasterCoreDB
    MasterCore --> MasterXpackDB
    MasterAgent --> MasterAgentDB
    Agent1API --> Agent1DB
    Agent2API --> Agent2DB
    AgentNAPI --> AgentNDB
    
    Agent1API --> Agent1Docker
    Agent2API --> Agent2Docker
    AgentNAPI --> AgentNDocker
```

**Sources:** Diagram 6 from high-level architecture diagrams, [frontend/src/api/modules/setting.ts:43-52]()

### Node Components

| Component | Master Node | Agent Node | Purpose |
|-----------|------------|------------|---------|
| **Core API Server** | ✓ | ✗ | System-wide settings, authentication, licensing, node management |
| **Agent API Server** | ✓ | ✓ | Infrastructure operations (containers, websites, databases, files) |
| **Web UI** | ✓ | ✗ | Central management interface |
| **core.db** | ✓ | ✗ | System settings, user accounts, global configuration |
| **xpack.db** | ✓ | ✗ | License data, node bindings |
| **agent.db** | ✓ | ✓ | Local resource metadata (apps, containers, websites, databases) |
| **Docker Engine** | ✓ | ✓ | Container runtime |

**Sources:** [frontend/src/api/interface/setting.ts:260-268](), Diagram 6 from high-level architecture diagrams

---

## Request Routing

The Web UI routes API requests to the appropriate node using one of two mechanisms:

### Routing Mechanisms

#### 1. CurrentNode Header
The frontend maintains a `CurrentNode` context in its global store. When a user selects a node, this value is set and included as a header in subsequent API requests.

#### 2. operateNode Query Parameter
Specific operations can target a node using the `?operateNode=X` query parameter in the URL. This is commonly used for operations that need explicit node targeting.

```mermaid
sequenceDiagram
    participant User
    participant WebUI as "Web UI<br/>(Master)"
    participant Store as "Pinia Store<br/>currentNode"
    participant Core as "Core API<br/>:9999"
    participant Agent1 as "Agent Node 1<br/>:10000"
    participant Agent2 as "Agent Node 2<br/>:10000"
    
    User->>WebUI: Select Node 1
    WebUI->>Store: Set currentNode = node1
    
    Note over User,Agent2: Pattern 1: Header-based routing
    User->>WebUI: Install app
    WebUI->>Store: Get currentNode
    Store-->>WebUI: node1
    WebUI->>Agent1: POST /apps/install<br/>CurrentNode: node1
    Agent1-->>WebUI: Installation started
    
    Note over User,Agent2: Pattern 2: Query parameter routing
    User->>WebUI: Get app store config
    WebUI->>Core: GET /core/settings/apps/store/config?operateNode=node2
    Core->>Agent2: Forward request
    Agent2-->>Core: Config data
    Core-->>WebUI: Config data
    
    Note over User,Agent2: Pattern 3: Cross-node metrics
    User->>WebUI: View dashboard
    WebUI->>Core: GET /core/dashboard/aggregate
    Core->>Agent1: Read agent.db metrics
    Core->>Agent2: Read agent.db metrics
    Core-->>WebUI: Aggregated metrics
```

**Sources:** [frontend/src/api/modules/setting.ts:157-163](), Diagram 6 from high-level architecture diagrams

### Node Selection API

The frontend provides APIs to list and select nodes:

```typescript
// List all nodes with full information
listAllNodes() -> Array<NodeItem>

// List simplified nodes with basic metrics
listAllSimpleNodes() -> Array<SimpleNodeItem>

// List nodes by type (e.g., "xpack" or "free")
listNodeOptions(type: string) -> Array<NodeItem>
```

**Sources:** [frontend/src/api/modules/setting.ts:47-52](), [frontend/src/api/interface/setting.ts:260-280]()

---

## License Binding and Node Management

License binding is the mechanism that associates licenses with specific nodes to enable features. Each node can be bound to a license, and the binding determines which features are available on that node.

### License Binding Flow

```mermaid
sequenceDiagram
    participant Admin as "Administrator"
    participant UI as "Web UI"
    participant Core as "Core API<br/>/core/licenses/*"
    participant XpackDB as "xpack.db"
    participant AgentNode as "Agent Node"
    
    Note over Admin,AgentNode: License Upload and Binding
    Admin->>UI: Upload license file
    UI->>Core: POST /core/licenses/upload<br/>FormData
    Core->>XpackDB: Store license
    XpackDB-->>Core: License ID
    Core-->>UI: License uploaded
    
    Admin->>UI: Bind license to node
    UI->>Core: POST /core/licenses/bind<br/>{nodeID, licenseID, syncList}
    Core->>XpackDB: Create binding record
    Core->>AgentNode: Sync license status
    AgentNode-->>Core: Acknowledgment
    Core-->>UI: Binding complete
    
    Note over Admin,AgentNode: License Status Check
    UI->>Core: GET /core/licenses/status
    Core->>XpackDB: Query bindings
    XpackDB-->>Core: License status
    Core-->>UI: {productPro, status, smsTotal, smsUsed}
    
    Note over Admin,AgentNode: Node Status with License Info
    UI->>Core: POST /core/nodes/list<br/>{type}
    Core->>XpackDB: Query node bindings
    XpackDB-->>Core: Node list with isBound flags
    Core-->>UI: Array<NodeItem>
```

**Sources:** [frontend/src/api/modules/setting.ts:10-45](), [frontend/src/api/interface/setting.ts:236-300]()

### License Management APIs

| API Endpoint | Purpose |
|--------------|---------|
| `POST /core/licenses/upload` | Upload new license file |
| `POST /core/licenses/update` | Update existing license |
| `POST /core/licenses/search` | Search licenses with pagination |
| `POST /core/licenses/bind` | Bind license to node(s) |
| `POST /core/licenses/unbind` | Unbind license from node |
| `POST /core/licenses/bind/free` | Change license binding to different nodes |
| `GET /core/licenses/status` | Get current license status |
| `GET /core/licenses/master/status` | Get master node license status |
| `POST /core/licenses/sync` | Sync license data |
| `GET /core/licenses/options` | List available license options |

**Sources:** [frontend/src/api/modules/setting.ts:10-45]()

### License Binding Structure

```typescript
interface LicenseBind {
    nodeID: number;           // Target node ID
    licenseID: number;        // License to bind
    syncList: string;         // Comma-separated list of items to sync
    withDockerRestart: boolean; // Whether to restart Docker
}

interface LicenseUnbind {
    id: number;               // Binding ID
    force: boolean;           // Force unbind even if in use
    withDockerRestart: boolean; // Whether to restart Docker
}

interface NodeItem {
    id: number;
    addr: string;             // Node address
    status: string;           // online/offline
    version: string;          // 1Panel version
    isXpack: boolean;         // Whether node has xpack features
    isBound: boolean;         // Whether license is bound
    name: string;             // Node name
}
```

**Sources:** [frontend/src/api/interface/setting.ts:260-300]()

---

## App Store Synchronization

The App Store synchronization system handles distributing app metadata across nodes. The Master node fetches app data from the remote repository, and nodes can query app information as needed.

### App Store Sync with Node Context

```mermaid
sequenceDiagram
    participant Admin
    participant UI
    participant Core as "Core API"
    participant Agent as "Agent Node"
    participant Remote as "Remote App Repo"
    
    Note over Admin,Remote: Manual Sync Trigger
    Admin->>UI: Click sync apps
    UI->>Core: POST /core/settings/apps/store/update
    Core->>Remote: GET /1panel.json.version.txt
    Remote-->>Core: Last modified timestamp
    Core->>Remote: GET /1panel.json.zip
    Remote-->>Core: App metadata
    Core->>Core: Update local app database
    Core-->>UI: Sync complete
    
    Note over Admin,Remote: Node-Specific App Config
    UI->>Core: GET /core/settings/apps/store/config?operateNode=node1
    Core->>Agent: Forward request
    Agent-->>Core: Node-specific config
    Core-->>UI: App store config
    
    Note over Admin,Remote: App Installation on Node
    Admin->>UI: Install app on node2
    UI->>Agent: POST /apps/install<br/>CurrentNode: node2
    Agent->>Remote: Download app package
    Remote-->>Agent: App tarball
    Agent->>Agent: Extract and install
    Agent-->>UI: Installation progress
```

**Sources:** [frontend/src/api/modules/setting.ts:157-163](), [agent/app/service/app.go:950-1044](), [agent/app/service/app_utils.go:990-1044]()

### App Download and Resource Management

Each node maintains its own app resource directories. When an app is installed, the agent downloads the app package from the remote repository and extracts it to the local resource directory:

```
{baseDir}/1panel/resource/apps/
  ├── remote/          # Remote apps from app store
  │   ├── mysql/
  │   │   ├── 8.0.31/
  │   │   └── 8.0.32/
  │   └── redis/
  ├── local/           # Local custom apps
  ├── custom/          # User-added apps
  └── offline/         # Offline app packages
```

**Sources:** [agent/app/service/app_utils.go:990-1044](), [agent/global/config.go:36-44](), [agent/init/dir/dir.go:22-31]()

### App Store Configuration per Node

The app store configuration can be queried per node using the `operateNode` parameter:

```typescript
// Get app store config for specific node
getAppStoreConfig(node?: string) {
    const params = node ? `?operateNode=${node}` : '';
    return http.get<App.AppStoreConfig>(`/core/settings/apps/store/config${params}`);
}
```

This allows each node to have different app store URLs or configurations, useful for environments with network segmentation or different compliance requirements.

**Sources:** [frontend/src/api/modules/setting.ts:157-163]()

---

## Node Status and Monitoring

The Master node aggregates metrics from all Agent nodes to provide a unified monitoring dashboard.

### Simplified Node Monitoring

```typescript
interface SimpleNodeItem {
    id: number;
    name: string;
    addr: string;              // Node address
    description: string;
    systemVersion: string;     // 1Panel version
    securityEntrance: string;  // Safe entrance path
    cpuUsedPercent: number;    // CPU usage percentage
    cpuTotal: number;          // Total CPU cores
    memoryTotal: number;       // Total memory in bytes
    memoryUsedPercent: number; // Memory usage percentage
}
```

The `listAllSimpleNodes()` API returns a lightweight summary of all nodes, which is suitable for dashboard display showing node health at a glance.

**Sources:** [frontend/src/api/interface/setting.ts:269-280](), [frontend/src/api/modules/setting.ts:50-52]()

### Node App Update Tracking

```typescript
interface NodeAppItem {
    name: string;        // Node name
    updateCount: number; // Number of apps with available updates
}
```

The `listAppNodes()` API returns which nodes have apps with available updates, allowing administrators to prioritize update operations:

```typescript
listAppNodes() {
    return http.get<Array<Setting.NodeAppItem>>(
        `/core/xpack/nodes/apps/update`, 
        {}, 
        { timeout: TimeoutEnum.T_60S }
    );
}
```

**Sources:** [frontend/src/api/interface/setting.ts:308-311](), [frontend/src/api/modules/setting.ts:58-60]()

---

## Shared Infrastructure

While nodes operate independently, they share certain infrastructure components to enable coordinated operations.

### Shared Components Architecture

```mermaid
graph TB
    subgraph Shared["Shared Infrastructure"]
        Backup["Backup Storage<br/>S3/OSS/MinIO/Local"]
        Registry["Container Registry<br/>Docker Hub/Private"]
        AppStore["App Store<br/>Centralized Catalog"]
    end
    
    subgraph Master["Master Node"]
        MasterAgent["Agent API"]
    end
    
    subgraph Agent1["Agent Node 1"]
        Agent1API["Agent API"]
    end
    
    subgraph Agent2["Agent Node 2"]
        Agent2API["Agent API"]
    end
    
    MasterAgent -->|backup/restore| Backup
    Agent1API -->|backup/restore| Backup
    Agent2API -->|backup/restore| Backup
    
    MasterAgent -->|pull/push images| Registry
    Agent1API -->|pull/push images| Registry
    Agent2API -->|pull/push images| Registry
    
    MasterAgent -->|sync app metadata| AppStore
    Agent1API -->|query apps| AppStore
    Agent2API -->|query apps| AppStore
```

**Sources:** Diagram 6 from high-level architecture diagrams

### Backup Storage

All nodes can be configured to use the same backup storage backend, enabling:
- Centralized backup management
- Cross-node backup restoration
- Disaster recovery across the fleet

Supported backup storage types:
- **S3**: AWS S3 or S3-compatible storage
- **OSS**: Alibaba Cloud Object Storage Service
- **MinIO**: Self-hosted S3-compatible storage
- **Local**: Local filesystem (node-specific)

**Sources:** Diagram 6 from high-level architecture diagrams

### Container Registry

Nodes share container registry configuration, allowing:
- Consistent image sources across the fleet
- Private registry support for air-gapped environments
- Image caching and distribution strategies

**Sources:** Diagram 6 from high-level architecture diagrams, [agent/app/service/app_utils.go:990-1044]()

### App Store Catalog

The centralized app store catalog is synchronized from the remote repository and made available to all nodes. This ensures:
- Consistent app versions across the fleet
- Centralized app metadata management
- Efficient distribution of app updates

The synchronization process checks for updates periodically and downloads the `1panel.json` file containing app metadata.

**Sources:** [agent/app/service/app.go:950-1044](), [agent/app/service/app_sync_task.go:38-128]()

---

## Data Isolation and Access Patterns

Each node maintains its own `agent.db` SQLite database for local resource metadata. The databases are not replicated, but the Master Core server can read from any Agent's database for monitoring purposes.

### Database Access Pattern

```mermaid
graph LR
    subgraph Master["Master Node"]
        Core["Core API Server"]
        MasterDB[("agent.db<br/>Master Resources")]
    end
    
    subgraph Agent1["Agent Node 1"]
        Agent1DB[("agent.db<br/>Node 1 Resources")]
    end
    
    subgraph Agent2["Agent Node 2"]
        Agent2DB[("agent.db<br/>Node 2 Resources")]
    end
    
    Core -->|read-only| MasterDB
    Core -->|read-only| Agent1DB
    Core -->|read-only| Agent2DB
    
    Core -.->|no write| Agent1DB
    Core -.->|no write| Agent2DB
```

**Key Principles:**
- Each Agent API server has **exclusive write access** to its own `agent.db`
- The Master Core server has **read-only access** to all `agent.db` files for metrics aggregation
- No database replication occurs between nodes
- Resource operations (create/update/delete) must be sent to the appropriate Agent API server

**Sources:** Diagram 6 from high-level architecture diagrams

---

## License Quota Management

Licenses include quota tracking for certain features. The most common quota is SMS (Short Message Service) usage for notification services.

### SMS Quota Tracking

```typescript
interface SmsInfo {
    licenseName: string;
    smsUsed: number;     // SMS messages consumed
    smsTotal: number;    // Total SMS quota
}

interface LicenseStatus {
    productPro: string;   // Product edition (Pro/Community)
    status: string;       // License status
    smsTotal: number;     // Total SMS quota
    smsUsed: number;      // SMS consumed
}
```

The SMS quota is tracked at the license level and shared across all nodes bound to that license. When a node sends an SMS notification, the usage is recorded and synchronized.

**Sources:** [frontend/src/api/interface/setting.ts:302-312](), [frontend/src/api/modules/setting.ts:54-56]()

---

## Node Initialization and Bootstrapping

When a new Agent node joins the deployment, it must be registered with the Master and optionally bound to a license.

### Node Registration Process

1. **Agent Installation**: Install 1Panel agent on the new server
2. **Network Configuration**: Ensure the Master can reach the Agent API server (default port 10000)
3. **Node Registration**: Add the node through the Master UI or API
4. **License Binding**: Optionally bind a license to enable xpack features
5. **Verification**: The Master queries the node status to confirm connectivity

The exact registration API endpoints are part of the xpack functionality and handle node discovery and authentication.

**Sources:** [frontend/src/api/modules/setting.ts:43-45]()

---

## Cross-Node Operations

Certain operations may span multiple nodes, requiring coordination through the Master:

### Batch App Installation

When installing the same app across multiple nodes (batch installation support), the Master coordinates the installation:

1. User selects multiple nodes and an app
2. Master sends installation requests to each selected Agent
3. Each Agent independently installs the app
4. Master aggregates installation status from all nodes

**Sources:** [agent/app/dto/request/app.go:29-36]()

### Configuration Synchronization

When binding a license, the `syncList` parameter specifies which configuration items should be synchronized to the node:

```typescript
interface LicenseBind {
    nodeID: number;
    licenseID: number;
    syncList: string;          // e.g., "apps,settings,backups"
    withDockerRestart: boolean;
}
```

This allows selectively pushing configuration from Master to Agent nodes during binding operations.

**Sources:** [frontend/src/api/interface/setting.ts:290-295]()

---

## Implementation References

### Core API Routes (Master Only)
- `/core/licenses/*` - License management endpoints
- `/core/nodes/*` - Node registration and listing
- `/core/settings/apps/store/config` - App store configuration (with node targeting)
- `/core/xpack/nodes/apps/update` - Cross-node app update tracking

### Agent API Routes (All Nodes)
- `/apps/*` - Application management
- `/containers/*` - Container operations
- `/websites/*` - Website management
- `/databases/*` - Database operations
- `/files/*` - File management
- `/settings/*` - Local node settings

### TypeScript Interfaces
- `NodeItem` - Full node information
- `SimpleNodeItem` - Lightweight node metrics
- `LicenseBind` / `LicenseUnbind` - License binding operations
- `LicenseStatus` - License and quota status
- `SmsInfo` - SMS quota information
- `NodeAppItem` - App update tracking per node

**Sources:** [frontend/src/api/modules/setting.ts:1-223](), [frontend/src/api/interface/setting.ts:1-313](), [agent/router/ro_app.go:1-50]()

---

# Page: Backend Service Layer

# Backend Service Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Makefile](Makefile)
- [agent/utils/common/sqlite.go](agent/utils/common/sqlite.go)
- [core/middleware/operation.go](core/middleware/operation.go)
- [core/utils/common/sqlite.go](core/utils/common/sqlite.go)
- [frontend/src/api/interface/setting.ts](frontend/src/api/interface/setting.ts)
- [frontend/src/api/modules/setting.ts](frontend/src/api/modules/setting.ts)

</details>



## Purpose and Scope

This document describes the Go-based backend service architecture for 1Panel, covering the repository pattern implementation, database design with GORM and SQLite, and the service interface layer that powers both the Core and Agent API servers. For information about multi-node deployment topology and license binding, see [Multi-Node Architecture](#2.2). For authentication mechanisms and security middleware, see [Authentication and Security](#3).

## Service Architecture Overview

1Panel's backend consists of two independent Go services built with the Gin web framework:

| Service | Binary | Port | Database | Primary Responsibilities |
|---------|--------|------|----------|-------------------------|
| **Core** | `1panel-core` | 9999 | `core.db`, `xpack.db` | Authentication, license management, system settings, user management |
| **Agent** | `1panel-agent` | 10000 | `agent.db` | Infrastructure operations: containers, websites, databases, files, apps |

Both services are compiled as separate binaries through the Makefile build system:

```
Core:  core/cmd/server/main.go    → build/1panel-core
Agent: agent/cmd/server/main.go   → build/1panel-agent
```

The Core service can read data from the Agent database for unified monitoring dashboards, while maintaining strict separation of operational concerns.

**Sources:** [Makefile:1-50](), Diagram 1 from high-level architecture

### Core vs Agent Separation

```mermaid
graph TB
    subgraph CoreService["Core Service (:9999)"]
        CoreAPI["Gin HTTP Server<br/>/api/v2/core/*"]
        CoreBiz["Business Logic Layer"]
        CoreRepo["Repository Layer"]
        CoreDB1[("core.db<br/>(SQLite)")]
        CoreDB2[("xpack.db<br/>(SQLite)")]
    end
    
    subgraph AgentService["Agent Service (:10000)"]
        AgentAPI["Gin HTTP Server<br/>/api/v2/*"]
        AgentBiz["Business Logic Layer"]
        AgentRepo["Repository Layer"]
        AgentDB[("agent.db<br/>(SQLite)")]
    end
    
    Frontend["Vue Frontend"] --> CoreAPI
    Frontend --> AgentAPI
    
    CoreAPI --> CoreBiz
    CoreBiz --> CoreRepo
    CoreRepo --> CoreDB1
    CoreRepo --> CoreDB2
    CoreRepo -.cross-read.-> AgentDB
    
    AgentAPI --> AgentBiz
    AgentBiz --> AgentRepo
    AgentRepo --> AgentDB
    
    AgentBiz --> Docker["Docker Engine"]
    AgentBiz --> Nginx["Nginx"]
    AgentBiz --> FileSystem["File System"]
```

**Sources:** [Makefile:12-18](), [core/middleware/operation.go:218-241]()

## Database Architecture

### SQLite Database Design

1Panel uses SQLite for all persistence layers, with three separate database files:

```mermaid
graph LR
    subgraph CoreDatabases["Core Service Databases"]
        CoreDB["core.db<br/>User accounts, settings,<br/>operation logs, snapshots"]
        XpackDB["xpack.db<br/>License data, node registry,<br/>enterprise features"]
    end
    
    subgraph AgentDatabase["Agent Service Database"]
        AgentDB["agent.db<br/>Apps, websites, containers,<br/>databases, files, cronjobs"]
    end
    
    CoreService["Core Service"] --> CoreDB
    CoreService --> XpackDB
    CoreService -.read-only.-> AgentDB
    
    AgentService["Agent Service"] --> AgentDB
```

The databases are stored at:
- Core: `{InstallDir}/1panel/db/core.db`
- Xpack: `{InstallDir}/1panel/db/xpack.db`
- Agent: `{InstallDir}/1panel/db/agent.db`

**Sources:** [core/middleware/operation.go:218-227]()

### Database Connection Management

Both Core and Agent services use identical GORM-based connection utilities that provide connection pooling and lifecycle management:

```mermaid
graph TB
    LoadDBConnByPath["LoadDBConnByPath(fullPath, dbName)"]
    CreateDir["Create directory if not exists"]
    CreateFile["Create .db file if not exists"]
    GetDBWithPath["GetDBWithPath(dbPath)"]
    ConfigurePool["Configure connection pool<br/>MaxOpenConns: 4<br/>MaxIdleConns: 1<br/>IdleTimeout: 15min<br/>MaxLifetime: 1hr"]
    
    LoadDBConnByPath --> CreateDir
    CreateDir --> CreateFile
    CreateFile --> GetDBWithPath
    GetDBWithPath --> ConfigurePool
    
    ConfigurePool --> GormDB["*gorm.DB"]
```

Key connection pool parameters:
- **Max Open Connections:** 4 (SQLite performs poorly with high concurrency)
- **Max Idle Connections:** 1 (minimize resource usage)
- **Idle Timeout:** 15 minutes
- **Connection Lifetime:** 1 hour

**Sources:** [core/utils/common/sqlite.go:15-56](), [agent/utils/common/sqlite.go:16-79]()

### GORM Configuration

The database layer uses GORM with the following configuration:

| Setting | Value | Rationale |
|---------|-------|-----------|
| `DisableForeignKeyConstraintWhenMigrating` | `true` | SQLite foreign key handling |
| `Logger` | `Silent` mode | Reduce log noise in production |
| `IgnoreRecordNotFoundError` | `true` | Treat not-found as normal flow |
| `SlowThreshold` | 1 second | Log queries taking >1s |

**Sources:** [core/utils/common/sqlite.go:42-67](), [agent/utils/common/sqlite.go:62-79]()

## Repository Pattern Implementation

1Panel implements a repository pattern to abstract database operations from business logic:

```mermaid
graph TB
    subgraph ServiceLayer["Service Layer (Business Logic)"]
        SettingService["Setting Service"]
        LicenseService["License Service"]
        AppService["App Service"]
    end
    
    subgraph RepositoryLayer["Repository Layer (Data Access)"]
        SettingRepo["ISettingRepo"]
        LicenseRepo["ILicenseRepo"]
        AppRepo["IAppRepo"]
    end
    
    subgraph DatabaseLayer["Database Layer"]
        GORM["GORM ORM"]
        CoreDB[("core.db")]
        XpackDB[("xpack.db")]
        AgentDB[("agent.db")]
    end
    
    SettingService --> SettingRepo
    LicenseService --> LicenseRepo
    AppService --> AppRepo
    
    SettingRepo --> GORM
    LicenseRepo --> GORM
    AppRepo --> GORM
    
    GORM --> CoreDB
    GORM --> XpackDB
    GORM --> AgentDB
```

### Repository Interface Pattern

Each domain entity has a corresponding repository interface defining CRUD operations:

```
ISettingRepo:
  - Get(key string) (*model.Setting, error)
  - GetList(keys []string) ([]*model.Setting, error)
  - Update(key, value string) error
  
ILicenseRepo:
  - Create(license *model.License) error
  - GetFirst() (*model.License, error)
  - Update(license *model.License) error
  - Delete(id uint) error
  - Page(page, size int) ([]model.License, int64, error)
```

Repositories are instantiated through factory functions:
- `repo.NewISettingRepo()` → Returns implementation of `ISettingRepo`
- `repo.NewILicenseRepo()` → Returns implementation of `ILicenseRepo`
- `repo.NewILogRepo()` → Returns implementation of `ILogRepo`

**Sources:** [core/middleware/operation.go:137](), [frontend/src/api/modules/setting.ts:16-45]()

## Service Layer Structure

### Service Organization

Services contain business logic and orchestrate operations across multiple repositories:

```mermaid
graph TB
    subgraph CoreServices["Core Services (core/app/service/)"]
        SettingSvc["setting.go<br/>System settings CRUD"]
        LicenseSvc["license.go<br/>License binding/unbinding"]
        NodeSvc["node.go<br/>Multi-node management"]
        AuthSvc["auth.go<br/>Password/MFA/Passkey"]
        UpgradeSvc["upgrade.go<br/>Version management"]
    end
    
    subgraph AgentServices["Agent Services (agent/app/service/)"]
        AppSvc["app.go<br/>App installation/operations"]
        WebsiteSvc["website.go<br/>Nginx site management"]
        ContainerSvc["container.go<br/>Docker operations"]
        DatabaseSvc["database.go<br/>DB user/backup management"]
        FileSvc["file.go<br/>File browser operations"]
        CronjobSvc["cronjob.go<br/>Scheduled task execution"]
        SnapshotSvc["snapshot.go<br/>Backup/restore operations"]
    end
    
    CoreServices -.depends on.-> AgentServices
```

**Sources:** Diagram 2 from high-level architecture

### Service Method Patterns

Services expose methods that map to API endpoints. Common patterns include:

| Pattern | Example Method | Description |
|---------|---------------|-------------|
| **Search/List** | `SearchSettings()` | Return paginated lists with filters |
| **CRUD** | `Create()`, `Update()`, `Delete()` | Standard create/update/delete operations |
| **Complex Operations** | `BindLicense()`, `InstallApp()` | Multi-step operations with transactions |
| **Validation** | `ValidatePassword()`, `CheckComplexity()` | Business rule validation |

**Sources:** [frontend/src/api/modules/setting.ts:69-223]()

## API Layer with Gin Framework

### Request Flow Through Middleware

```mermaid
sequenceDiagram
    participant Client
    participant Gin["Gin HTTP Server"]
    participant Auth["Auth Middleware"]
    participant OpLog["Operation Log Middleware"]
    participant Handler["API Handler"]
    participant Service["Service Layer"]
    participant Repo["Repository Layer"]
    participant DB["SQLite Database"]
    
    Client->>Gin: HTTP Request
    Gin->>Auth: Verify JWT token
    Auth->>Gin: Token valid
    Gin->>OpLog: Log operation metadata
    OpLog->>Handler: Execute handler
    Handler->>Service: Call service method
    Service->>Repo: Query/update data
    Repo->>DB: Execute SQL via GORM
    DB-->>Repo: Return result
    Repo-->>Service: Return domain objects
    Service-->>Handler: Return response DTO
    Handler-->>OpLog: Record result
    OpLog->>DB: Store operation log
    OpLog-->>Gin: Complete
    Gin-->>Client: JSON response
```

**Sources:** [core/middleware/operation.go:28-171]()

### Operation Logging Middleware

The operation logging middleware automatically captures and persists API calls with detailed metadata:

**Captured Information:**
- Source: First path segment (e.g., "settings", "licenses", "apps")
- Node: Current node name from `CurrentNode` header
- IP: Client IP address
- Method: HTTP method (get/post/put/delete)
- Path: API path without prefix
- User Agent: Browser/client identifier
- Status: Success/failed based on response code
- Latency: Request duration
- Details: Localized operation description (Chinese and English)

**Dynamic Detail Generation:**

The middleware parses `docs.XLogJson` (embedded Swagger annotations) to extract body parameters and generate human-readable operation descriptions:

```
Example: /api/v2/core/licenses/bind
Body: { "nodeID": 5, "licenseID": 3 }
Generated: "Bind license [ProductName] to node [NodeName]"
```

It performs database lookups via `beforeFunctions` to resolve IDs to names (e.g., `nodeID` → node name).

**Sources:** [core/middleware/operation.go:28-171](), [core/middleware/operation.go:173-189]()

### Cross-Database Access Pattern

The operation logging middleware demonstrates how the Core service dynamically connects to the appropriate database based on the request path:

```mermaid
graph TB
    RequestPath["Request Path Analysis"]
    
    CheckPath{Path starts with?}
    
    CoreDB["core.db<br/>/api/v2/core/*"]
    XpackDB["xpack.db<br/>/api/v2/xpack/*"]
    AgentDB["agent.db<br/>/api/v2/*"]
    
    OpenConn["gorm.Open(sqlite.Open(dbFile))"]
    ConfigPool["Configure connection pool"]
    ExecuteQuery["Execute query"]
    CloseConn["Close connection"]
    
    RequestPath --> CheckPath
    CheckPath -->|"/core"| CoreDB
    CheckPath -->|"/xpack"| XpackDB
    CheckPath -->|"other"| AgentDB
    
    CoreDB --> OpenConn
    XpackDB --> OpenConn
    AgentDB --> OpenConn
    
    OpenConn --> ConfigPool
    ConfigPool --> ExecuteQuery
    ExecuteQuery --> CloseConn
```

This pattern enables the Core service to query Agent data for unified dashboards without requiring persistent cross-database connections.

**Sources:** [core/middleware/operation.go:218-249]()

## API Interface Structure

### Core API Endpoints

Core API endpoints are organized by domain and exposed through the frontend API client:

| Domain | Example Endpoints | Service Responsibility |
|--------|------------------|----------------------|
| **Licenses** | `/core/licenses/upload`<br>`/core/licenses/bind`<br>`/core/licenses/status` | Upload license files, bind to nodes, check status |
| **Nodes** | `/core/nodes/list`<br>`/core/nodes/all`<br>`/core/nodes/simple/all` | List agent nodes, get node details |
| **Settings** | `/core/settings/search`<br>`/core/settings/update`<br>`/core/settings/ssl/update` | System configuration CRUD |
| **Authentication** | `/core/settings/password/update`<br>`/core/settings/mfa/bind`<br>`/core/settings/passkey/*` | Password, MFA, passkey management |
| **Upgrade** | `/core/settings/upgrade`<br>`/core/settings/upgrade/releases` | Version checking and upgrades |

**Sources:** [frontend/src/api/modules/setting.ts:10-223]()

### Agent API Endpoints

Agent API endpoints manage infrastructure resources:

| Domain | Example Endpoints | Service Responsibility |
|--------|------------------|----------------------|
| **Settings** | `/settings/search`<br>`/settings/update`<br>`/settings/basedir` | Agent-specific configuration |
| **Snapshots** | `/settings/snapshot`<br>`/settings/snapshot/recover`<br>`/settings/snapshot/rollback` | Backup creation and restoration |
| **Apps** | `/apps/search`<br>`/apps/install`<br>`/apps/installed/*` | App store and lifecycle management |
| **Websites** | `/websites`<br>`/websites/ssl`<br>`/websites/domains` | Nginx website configuration |
| **Containers** | `/containers`<br>`/containers/logs`<br>`/containers/compose` | Docker operations |
| **Databases** | `/databases/mysql`<br>`/databases/postgresql`<br>`/databases/redis` | Database management |

**Sources:** [frontend/src/api/modules/setting.ts:63-192]()

### Request/Response Type System

The frontend defines TypeScript interfaces that mirror backend DTOs:

```typescript
// Setting update request
interface SettingUpdate {
  key: string;
  value: string;
}

// License binding request
interface LicenseBind {
  nodeID: number;
  licenseID: number;
  syncList: string;
  withDockerRestart: boolean;
}

// Snapshot creation request
interface SnapshotCreate {
  id: number;
  sourceAccountIDs: string;
  downloadAccountID: string;
  description: string;
  secret: string;
  timeout: number;
  appData: Array<DataTree>;
  panelData: Array<DataTree>;
  backupData: Array<DataTree>;
  withMonitorData: boolean;
  withLoginLog: boolean;
  withOperationLog: boolean;
}
```

**Sources:** [frontend/src/api/interface/setting.ts:1-312]()

## Service Layer Patterns

### Timeout Configuration

Critical operations use extended timeouts via the `TimeoutEnum`:

| Operation Type | Timeout | Enum |
|---------------|---------|------|
| License sync/bind | 60s | `TimeoutEnum.T_60S` |
| Snapshot operations | 60s | `TimeoutEnum.T_60S` |
| Standard operations | 30s | Default |
| App node updates | 60s | `TimeoutEnum.T_60S` |

**Sources:** [frontend/src/api/modules/setting.ts:32-59]()

### Secret Handling

Sensitive data (passwords, secrets) is Base64-encoded before transmission:

```typescript
// Proxy password encoding
let request = deepCopy(params) as Setting.ProxyUpdate;
if (request.proxyPasswd) {
  request.proxyPasswd = Base64.encode(request.proxyPasswd);
}
```

**Sources:** [frontend/src/api/modules/setting.ts:108-111]()

### Multi-Node Routing

API calls can target specific nodes using:
- **Header:** `CurrentNode` header with node name
- **Query parameter:** `?operateNode={nodeID}`

Example:
```typescript
export const getAppStoreConfig = (node?: string) => {
  const params = node ? `?operateNode=${node}` : '';
  return http.get<App.AppStoreConfig>(`/core/settings/apps/store/config${params}`);
};
```

**Sources:** [frontend/src/api/modules/setting.ts:157-159](), [core/middleware/operation.go:38-39]()

## Database Migration and Schema Management

GORM's `AutoMigrate` feature handles schema evolution automatically when models are updated. Both Core and Agent services initialize their schemas on startup by passing model structs to `db.AutoMigrate()`.

Key migration features:
- **Non-destructive:** Adds new columns/tables without dropping existing data
- **Foreign key handling:** Disabled during migration for SQLite compatibility
- **Zero-downtime:** Migrations run during service startup before accepting requests

**Sources:** [core/utils/common/sqlite.go:43-45](), [agent/utils/common/sqlite.go:63-65]()

---

# Page: Frontend Architecture

# Frontend Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Makefile](Makefile)
- [agent/utils/common/sqlite.go](agent/utils/common/sqlite.go)
- [core/middleware/operation.go](core/middleware/operation.go)
- [core/utils/common/sqlite.go](core/utils/common/sqlite.go)
- [frontend/src/lang/modules/en.ts](frontend/src/lang/modules/en.ts)
- [frontend/src/lang/modules/es-es.ts](frontend/src/lang/modules/es-es.ts)
- [frontend/src/lang/modules/ja.ts](frontend/src/lang/modules/ja.ts)
- [frontend/src/lang/modules/ko.ts](frontend/src/lang/modules/ko.ts)
- [frontend/src/lang/modules/ms.ts](frontend/src/lang/modules/ms.ts)
- [frontend/src/lang/modules/pt-br.ts](frontend/src/lang/modules/pt-br.ts)
- [frontend/src/lang/modules/ru.ts](frontend/src/lang/modules/ru.ts)
- [frontend/src/lang/modules/tr.ts](frontend/src/lang/modules/tr.ts)
- [frontend/src/lang/modules/zh-Hant.ts](frontend/src/lang/modules/zh-Hant.ts)
- [frontend/src/lang/modules/zh.ts](frontend/src/lang/modules/zh.ts)

</details>



## Purpose and Scope

This document describes the high-level architecture of the 1Panel frontend application, including its technology stack, project structure, core architectural layers, and integration patterns with the backend services. For detailed component patterns and shared components, see [Component Architecture and Patterns](#11.1). For API client implementation details, see [API Client Layer and Type System](#11.2). For internationalization specifics, see [Internationalization and Localization](#4).

## Technology Stack

The 1Panel frontend is built using modern web technologies optimized for developer experience and runtime performance:

| Technology | Version | Purpose |
|------------|---------|---------|
| Vue 3 | 3.4+ | Progressive framework using Composition API |
| TypeScript | 5.3+ | Type-safe JavaScript development |
| Vite | 5.0+ | Build tool with fast HMR and optimized bundling |
| Element Plus | Latest | Comprehensive UI component library |
| Pinia | Latest | Vue 3 official state management |
| Vue Router | Latest | Client-side routing |
| Axios | Latest | HTTP client with interceptors |
| vue-i18n | Latest | Internationalization supporting 10 languages |
| Monaco Editor | Latest | Code editor with syntax highlighting |
| v-charts/ECharts | Latest | Data visualization and charting |

**Sources:** Diagram 1 and Diagram 4 from high-level architecture

## Application Architecture

### Layered Architecture Overview

```mermaid
graph TB
    subgraph "Presentation Layer"
        Pages["Page Components<br/>/views/*"]
        Layouts["Layout Components<br/>LayoutContent"]
        SharedComps["Shared Components<br/>AppStatus, ComplexTable"]
    end
    
    subgraph "State Management Layer"
        PiniaStores["Pinia Stores<br/>Global State"]
        CurrentNode["currentNode Store<br/>Multi-node context"]
        UserStore["User Store<br/>Authentication state"]
    end
    
    subgraph "Routing Layer"
        VueRouter["Vue Router<br/>Route definitions"]
        Guards["Navigation Guards<br/>Auth checks"]
        Tabs["Tab Management<br/>Multi-tab navigation"]
    end
    
    subgraph "Communication Layer"
        APIClient["API Client<br/>Axios instances"]
        Interceptors["Request/Response<br/>Interceptors"]
        TypedInterfaces["TypeScript Interfaces<br/>Request/Response types"]
    end
    
    subgraph "Utility Layer"
        I18n["vue-i18n<br/>10 language modules"]
        Validators["Form Validators<br/>Centralized rules"]
        Utils["Common Utils<br/>Helper functions"]
    end
    
    Pages --> SharedComps
    Pages --> Layouts
    Pages --> PiniaStores
    Pages --> VueRouter
    Pages --> APIClient
    
    PiniaStores --> APIClient
    APIClient --> Interceptors
    Interceptors --> TypedInterfaces
    
    VueRouter --> Guards
    Guards --> PiniaStores
    
    Pages --> I18n
    Pages --> Validators
    
    APIClient -->|"Core: :9999"| CoreBackend["Core API Server"]
    APIClient -->|"Agent: :10000"| AgentBackend["Agent API Server"]
```

**Sources:** 
- [Makefile:9]() - WEB_PATH definition
- Diagram 1, Diagram 4 from high-level architecture
- Section 2.4 description from table of contents

### Directory Structure

The frontend codebase follows a modular organization pattern:

```mermaid
graph TB
    Frontend["frontend/src/"]
    
    Frontend --> Views["views/<br/>Page-level components"]
    Frontend --> Components["components/<br/>Reusable components"]
    Frontend --> Stores["stores/<br/>Pinia state stores"]
    Frontend --> Router["router/<br/>Route definitions"]
    Frontend --> API["api/<br/>HTTP client modules"]
    Frontend --> Lang["lang/<br/>i18n messages"]
    Frontend --> Utils["utils/<br/>Helper functions"]
    Frontend --> Assets["assets/<br/>Static resources"]
    Frontend --> Types["types/<br/>TypeScript definitions"]
    
    Views --> ViewExamples["home/, apps/, website/,<br/>database/, container/, etc."]
    Components --> CompExamples["AppStatus, ComplexTable,<br/>LayoutContent, etc."]
    Stores --> StoreExamples["user, node, settings, etc."]
    Lang --> LangModules["zh.ts, en.ts, ja.ts,<br/>ru.ts, es-es.ts, pt-br.ts,<br/>ko.ts, tr.ts, ms.ts, zh-Hant.ts"]
```

**Sources:**
- [frontend/src/lang/modules/zh.ts:1-3]()
- [frontend/src/lang/modules/en.ts:1-3]()
- Table of contents sections 11.1, 11.2, 11.3

## Core Architectural Patterns

### Component Composition Pattern

The application uses Vue 3's Composition API throughout:

```mermaid
graph LR
    PageComponent["Page Component<br/>e.g., DatabaseList"]
    
    PageComponent --> Setup["setup()<br/>Composition API"]
    
    Setup --> Refs["reactive() / ref()<br/>Local state"]
    Setup --> Stores["useStore()<br/>Global state access"]
    Setup --> Router["useRouter()<br/>Navigation"]
    Setup --> I18n["useI18n()<br/>Translations"]
    Setup --> APICall["API module functions<br/>HTTP requests"]
    
    Setup --> LifecycleHooks["onMounted(), onUnmounted()<br/>Lifecycle management"]
    Setup --> Computed["computed()<br/>Derived state"]
    Setup --> Watch["watch()<br/>Reactive side effects"]
```

**Sources:** Diagram 1 from high-level architecture, Vue 3 Composition API mentioned

### State Management with Pinia

Global application state is managed through Pinia stores:

```mermaid
graph TB
    PiniaRoot["Pinia Root Store"]
    
    PiniaRoot --> UserStore["User Store"]
    PiniaRoot --> NodeStore["Node Store<br/>currentNode tracking"]
    PiniaRoot --> SettingsStore["Settings Store"]
    
    UserStore --> UserState["state<br/>- user info<br/>- auth token<br/>- MFA status"]
    UserStore --> UserActions["actions<br/>- login()<br/>- logout()<br/>- updateProfile()"]
    
    NodeStore --> NodeState["state<br/>- currentNode<br/>- nodeList<br/>- nodeMetrics"]
    NodeStore --> NodeActions["actions<br/>- switchNode()<br/>- loadNodes()"]
    
    Components["Vue Components"] --> UseStore["useStore()"]
    UseStore --> PiniaRoot
    
    PiniaRoot --> Persist["localStorage<br/>State persistence"]
```

**Sources:** 
- Diagram 1 mentions Pinia Global Store
- Diagram 6 references currentNode tracking across multi-node architecture
- High-level architecture mentions CurrentNode header

### Routing and Navigation

Vue Router manages client-side navigation with route-based code splitting:

```mermaid
graph TB
    RouterInstance["Vue Router Instance"]
    
    RouterInstance --> Routes["Route Definitions"]
    
    Routes --> HomeRoute["/home<br/>→ Home component"]
    Routes --> AppsRoute["/apps<br/>→ Apps component"]
    Routes --> WebsiteRoute["/websites<br/>→ Website component"]
    Routes --> DatabaseRoute["/databases<br/>→ Database component"]
    Routes --> ContainerRoute["/containers<br/>→ Container component"]
    Routes --> SettingsRoute["/settings<br/>→ Settings component"]
    
    RouterInstance --> Guards["Navigation Guards"]
    
    Guards --> BeforeEach["beforeEach()<br/>Authentication check"]
    Guards --> AfterEach["afterEach()<br/>Tab management"]
    
    BeforeEach --> CheckAuth["Verify JWT token<br/>from Pinia store"]
    CheckAuth -->|Invalid| LoginRedirect["Redirect to /login"]
    CheckAuth -->|Valid| AllowNav["Allow navigation"]
    
    AfterEach --> UpdateTabs["Update tab history<br/>Multi-tab interface"]
```

**Sources:**
- [frontend/src/lang/modules/zh.ts:362-392]() - Menu structure with all routes
- [frontend/src/lang/modules/en.ts:375-406]() - Menu translations
- Diagram 1 mentions Vue Router

## Internationalization System

The i18n system supports 10 languages through hierarchical message structures:

```mermaid
graph TB
    I18nPlugin["vue-i18n Plugin"]
    
    I18nPlugin --> LangModules["Language Modules"]
    
    LangModules --> ZH["zh.ts<br/>Simplified Chinese"]
    LangModules --> EN["en.ts<br/>English"]
    LangModules --> JA["ja.ts<br/>Japanese"]
    LangModules --> RU["ru.ts<br/>Russian"]
    LangModules --> ES["es-es.ts<br/>Spanish"]
    LangModules --> PT["pt-br.ts<br/>Portuguese"]
    LangModules --> KO["ko.ts<br/>Korean"]
    LangModules --> TR["tr.ts<br/>Turkish"]
    LangModules --> MS["ms.ts<br/>Malay"]
    LangModules --> ZHTW["zh-Hant.ts<br/>Traditional Chinese"]
    
    ZH --> MessageStructure["Message Structure<br/>- commons<br/>- menu<br/>- home<br/>- database<br/>- container<br/>- website<br/>- cronjob<br/>- settings<br/>- etc."]
    
    Components["Vue Components"] --> UseI18n["useI18n() / $t()"]
    UseI18n --> I18nPlugin
    
    I18nPlugin --> FallbackChain["Fallback: current → en → key"]
```

**Sources:**
- [frontend/src/lang/modules/zh.ts:1-400]()
- [frontend/src/lang/modules/en.ts:1-410]()
- All other language module files
- Diagram 1 mentions "10-Language Support"

### Message Key Structure

Translation keys follow a hierarchical dot notation pattern:

| Key Pattern | Example | Usage |
|-------------|---------|-------|
| `commons.button.*` | `commons.button.create` | Common UI actions |
| `commons.msg.*` | `commons.msg.deleteSuccess` | System messages |
| `menu.*` | `menu.database` | Navigation menu items |
| `database.*` | `database.create` | Domain-specific terms |
| `status.*` | `commons.status.running` | Status indicators |

**Sources:**
- [frontend/src/lang/modules/zh.ts:3-360]() - commons section
- [frontend/src/lang/modules/zh.ts:362-392]() - menu section
- [frontend/src/lang/modules/zh.ts:475-653]() - database section

## API Client Architecture

The frontend communicates with backend services through a typed API client layer:

```mermaid
graph TB
    Components["Vue Components"]
    
    Components --> APIModules["API Module Functions"]
    
    APIModules --> DatabaseAPI["database.ts<br/>Database operations"]
    APIModules --> ContainerAPI["container.ts<br/>Container operations"]
    APIModules --> WebsiteAPI["website.ts<br/>Website operations"]
    APIModules --> AppAPI["app.ts<br/>App store operations"]
    APIModules --> SystemAPI["system.ts<br/>System operations"]
    
    APIModules --> AxiosInstance["Axios Instance"]
    
    AxiosInstance --> RequestInterceptor["Request Interceptor<br/>- Add JWT token<br/>- Add CurrentNode header<br/>- Set timeouts"]
    AxiosInstance --> ResponseInterceptor["Response Interceptor<br/>- Handle errors<br/>- Parse responses<br/>- Refresh token"]
    
    RequestInterceptor --> CoreBackend["Core API<br/>:9999"]
    RequestInterceptor --> AgentBackend["Agent API<br/>:10000"]
    
    CoreBackend --> CoreEndpoints["/api/v2/core/*<br/>Auth, Settings, License"]
    AgentBackend --> AgentEndpoints["/api/v2/agent/*<br/>Apps, Containers, DBs"]
    
    ResponseInterceptor --> TypedResponse["TypeScript Response<br/>Interfaces"]
    TypedResponse --> Components
```

**Sources:**
- Diagram 1 and Diagram 3 from high-level architecture
- Diagram 6 mentions CurrentNode header for multi-node routing
- Section 11.2 API Client Layer mentioned in table of contents

### Request Flow with Node Context

The frontend supports multi-node deployments by routing API calls to appropriate nodes:

```mermaid
sequenceDiagram
    participant Component
    participant Store as Pinia Store
    participant Interceptor as Request Interceptor
    participant CoreAPI as Core API :9999
    participant AgentAPI as Agent API :10000
    
    Component->>Store: Get currentNode
    Store-->>Component: "node-123"
    
    Component->>Interceptor: API call with params
    Interceptor->>Interceptor: Add headers:<br/>- Authorization: Bearer token<br/>- CurrentNode: node-123
    
    alt Core Operation
        Interceptor->>CoreAPI: POST /api/v2/core/settings
        CoreAPI-->>Interceptor: Response
    else Agent Operation
        Interceptor->>AgentAPI: POST /api/v2/agent/containers
        AgentAPI-->>Interceptor: Response
    end
    
    Interceptor->>Component: Typed response
```

**Sources:**
- Diagram 3 and Diagram 6 from high-level architecture
- [core/middleware/operation.go:38-39]() - CurrentNode header handling

## Build and Development Workflow

### Build Process

The frontend build is managed through npm scripts and integrated into the main Makefile:

```mermaid
graph LR
    DevStart["npm run dev"] --> ViteDev["Vite Dev Server<br/>HMR enabled<br/>Port 5173"]
    
    Build["npm run build:pro"] --> ViteBuild["Vite Build Process"]
    
    ViteBuild --> TypeCheck["TypeScript<br/>Type checking"]
    ViteBuild --> Compile["Vue SFC<br/>Compilation"]
    ViteBuild --> Bundle["Asset Bundling<br/>Code splitting"]
    ViteBuild --> Optimize["Minification<br/>Tree shaking"]
    
    Optimize --> DistFolder["dist/<br/>Production assets"]
    
    MakeBuild["make build_frontend"] --> Build
    DistFolder --> AssetsDir["core/cmd/server/<br/>web/assets/"]
    
    MakeBuildAll["make build_all"] --> MakeBuild
```

**Sources:**
- [Makefile:8-9]() - WEB_PATH and ASSERT_PATH definitions
- [Makefile:28-29]() - build_frontend target
- [Makefile:47]() - build_all target
- Diagram 4 mentions Vite 5.0 as build tool

### Development vs Production Configuration

| Aspect | Development | Production |
|--------|------------|------------|
| Build Command | `npm run dev` | `npm run build:pro` |
| Server | Vite dev server (HMR) | Static files served by Go backend |
| Source Maps | Full source maps | None or minimal |
| Bundle Size | Unoptimized | Minified and tree-shaken |
| API Proxy | Vite proxy to :9999/:10000 | Direct backend connection |
| Hot Module Replacement | Enabled | N/A |

**Sources:**
- [Makefile:28-29]()
- [Makefile:10]() - ASSERT_PATH where production assets are placed

## Integration with Backend Services

The frontend integrates with two backend services (Core and Agent) through REST APIs:

```mermaid
graph TB
    Frontend["Vue Frontend<br/>Browser Application"]
    
    Frontend --> CoreAPI["Core API Server<br/>Port 9999"]
    Frontend --> AgentAPI["Agent API Server<br/>Port 10000"]
    
    CoreAPI --> CoreFeatures["Core Features<br/>- Authentication (JWT/MFA/Passkey)<br/>- User management<br/>- License validation<br/>- System settings<br/>- Node management"]
    
    AgentAPI --> AgentFeatures["Agent Features<br/>- Container operations<br/>- App store & installs<br/>- Website/Nginx management<br/>- Database management<br/>- File operations<br/>- Cronjob execution<br/>- AI/GPU monitoring"]
    
    CoreAPI --> CoreDB["core.db<br/>SQLite"]
    CoreAPI --> XpackDB["xpack.db<br/>SQLite"]
    AgentAPI --> AgentDB["agent.db<br/>SQLite"]
    
    CoreAPI -.reads.-> AgentDB
    
    Frontend --> AuthFlow["Authentication Flow<br/>1. Login POST to Core<br/>2. Receive JWT token<br/>3. Store in Pinia + localStorage<br/>4. Include in all requests"]
    
    Frontend --> NodeSwitch["Node Switching<br/>1. User selects node<br/>2. Update Pinia currentNode<br/>3. Include CurrentNode header<br/>4. Backend routes to target agent"]
```

**Sources:**
- Diagram 1, Diagram 2, Diagram 6 from high-level architecture
- Diagram 3 authentication flow
- [core/middleware/operation.go:38-40]() - Node header handling

### API Communication Patterns

The frontend follows standardized patterns for API communication:

1. **Synchronous Operations**: Direct API calls with loading states
2. **Asynchronous Operations**: Task-based execution with SSE streaming for progress
3. **Polling**: Dashboard metrics refreshed every 3 seconds
4. **Error Handling**: Centralized error interceptor with user-friendly messages

**Sources:**
- Diagram 3 shows task-based async operations with SSE
- Diagram 3 mentions 3-second polling for dashboard

## Security Considerations

The frontend implements multiple security layers:

| Security Feature | Implementation |
|-----------------|----------------|
| Authentication | JWT tokens stored in Pinia with localStorage persistence |
| MFA Support | TOTP 6-digit codes validated through Core API |
| Passkey Support | WebAuthn integration for biometric/hardware key auth |
| CSRF Protection | Token-based validation on state-changing operations |
| XSS Prevention | Vue's template escaping + Content-Security-Policy headers |
| Sensitive Data | Masked display with show/hide toggles |
| Session Management | Token refresh mechanism with expiration handling |

**Sources:**
- Diagram 5 from high-level architecture (Authentication Mechanisms)
- [frontend/src/lang/modules/zh.ts:192-220]() - Login page with MFA and passkey support
- [frontend/src/lang/modules/en.ts:185-223]() - English login translations

## Performance Optimizations

The frontend implements several performance optimizations:

1. **Code Splitting**: Route-based lazy loading for reduced initial bundle size
2. **Tree Shaking**: Vite eliminates unused code during production builds
3. **Asset Optimization**: Images and static assets are minified and cached
4. **API Response Caching**: Dashboard metrics cached with 3-second refresh intervals
5. **Virtual Scrolling**: Large lists use ComplexTable with pagination
6. **Debounced Search**: Form inputs debounced to reduce API calls

**Sources:**
- Diagram 4 mentions Vite for optimized builds
- Diagram 3 mentions caching strategy for dashboard with 3-second intervals
- Section 11.1 mentions ComplexTable component

---

# Page: Data Flow and Integration Patterns

# Data Flow and Integration Patterns

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/app/api/v2/container.go](agent/app/api/v2/container.go)
- [agent/app/dto/container.go](agent/app/dto/container.go)
- [agent/app/service/container.go](agent/app/service/container.go)
- [agent/router/ro_container.go](agent/router/ro_container.go)
- [frontend/src/api/interface/container.ts](frontend/src/api/interface/container.ts)
- [frontend/src/api/interface/setting.ts](frontend/src/api/interface/setting.ts)
- [frontend/src/api/modules/container.ts](frontend/src/api/modules/container.ts)
- [frontend/src/api/modules/setting.ts](frontend/src/api/modules/setting.ts)
- [frontend/src/views/container/container/operate/index.vue](frontend/src/views/container/container/operate/index.vue)

</details>



## Purpose and Scope

This document describes the fundamental data flow patterns and integration mechanisms used throughout the 1Panel system. It covers:

- Communication patterns between frontend and backend (synchronous, asynchronous, streaming)
- The async task execution system for long-running operations
- Multi-node request routing and data aggregation
- Type system integration between TypeScript frontend and Go backend
- Error handling and validation flows

For details on specific subsystem architectures, see [Backend Service Layer](#2.3) and [Frontend Architecture](#2.4). For authentication specifics, see [Authentication and Security](#3).

---

## Core Integration Patterns

### Pattern 1: Synchronous Request-Response

The simplest pattern used for quick operations that complete in under a few seconds. The client sends a request and waits for a complete response.

```mermaid
sequenceDiagram
    participant Frontend as "Vue Frontend"
    participant APIClient as "API Client Layer"
    participant Route as "Gin Route Handler"
    participant Service as "Service Layer"
    participant Docker as "Docker Client"
    
    Frontend->>APIClient: "Load container list"
    APIClient->>Route: "POST /containers/list"
    Route->>Service: "containerService.List()"
    Service->>Docker: "client.ContainerList()"
    Docker-->>Service: "[]container.Summary"
    Service-->>Route: "[]dto.ContainerOptions"
    Route-->>APIClient: "JSON response"
    APIClient-->>Frontend: "Container[]"
```

**Key Characteristics:**
- Immediate response with complete data
- No intermediate status tracking
- Typically completes in < 5 seconds
- Used for reads, simple updates, and fast operations

**Examples:**

| Operation | Frontend API | Backend Handler | Service Method |
|-----------|-------------|-----------------|----------------|
| List containers | `listContainer()` | `ListContainer` | `containerService.List()` |
| Load container info | `loadContainerInfo(name)` | `ContainerInfo` | `containerService.ContainerInfo()` |
| Container stats | `containerStats(id)` | `ContainerStats` | `containerService.ContainerStats()` |
| Load resource limits | `loadResourceLimit()` | `LoadResourceLimit` | `containerService.LoadResourceLimit()` |

**Sources:** [frontend/src/api/modules/container.ts:9-23](), [agent/app/api/v2/container.go:64-100](), [agent/app/service/container.go:145-167]()

---

### Pattern 2: Async Task Execution with Task Logs

For long-running operations (container creation, image pulls, upgrades), the system uses an asynchronous task pattern. Operations return immediately with a `taskID`, and clients stream progress via Server-Sent Events.

```mermaid
sequenceDiagram
    participant User as "User"
    participant Frontend as "Vue Component"
    participant API as "API Client"
    participant Handler as "API Handler"
    participant Service as "Service Layer"
    participant Task as "Task System"
    participant Docker as "Docker Engine"
    
    User->>Frontend: "Create container"
    Frontend->>Frontend: "taskID = newUUID()"
    Frontend->>API: "createContainer(form, taskID)"
    API->>Handler: "POST /containers"
    Handler->>Service: "ContainerCreate(req, true)"
    
    Service->>Task: "task.NewTaskWithOps()"
    Task-->>Service: "taskItem"
    Service->>Task: "taskItem.AddSubTask()"
    Service-->>Handler: "return nil (immediate)"
    Handler-->>API: "200 OK"
    API-->>Frontend: "success"
    
    Frontend->>Frontend: "Open TaskLog dialog"
    Frontend->>API: "Stream task logs (SSE)"
    
    par Async Execution
        Service->>Task: "taskItem.Execute()"
        Task->>Docker: "Pull image"
        Docker-->>Task: "progress..."
        Task->>Task: "Log progress"
        Task->>Docker: "Create container"
        Docker-->>Task: "containerID"
        Task->>Docker: "Start container"
        Task->>Task: "Mark complete"
    end
    
    loop Stream Updates
        API-->>Frontend: "event: log message"
        Frontend->>Frontend: "Append to log viewer"
    end
```

**Task Structure:**

Each task consists of:
- **Task ID**: UUID for tracking
- **Task Type**: Create, Update, Upgrade, Clean, etc.
- **Scope**: Container, Image, Compose, etc.
- **Subtasks**: Individual steps with names and functions
- **Log Buffer**: Real-time progress messages

**Sources:** [agent/app/service/container.go:509-583](), [frontend/src/views/container/container/operate/index.vue:549-562]()

#### Task Creation and Execution Flow

```mermaid
flowchart TD
    Start["API Request with taskID"] --> NewTask["task.NewTaskWithOps()"]
    NewTask --> AddSubtask1["AddSubTask: Pull Image"]
    AddSubtask1 --> AddSubtask2["AddSubTask: Validate Config"]
    AddSubtask2 --> AddSubtask3["AddSubTask: Create & Start"]
    AddSubtask3 --> CheckThread{"inThread param?"}
    
    CheckThread -->|true| Goroutine["Launch goroutine"]
    CheckThread -->|false| Direct["Direct execution"]
    
    Goroutine --> Execute["taskItem.Execute()"]
    Direct --> Execute
    
    Execute --> Loop["For each subtask"]
    Loop --> RunSubtask["Execute subtask function"]
    RunSubtask --> LogProgress["taskItem.Log(message)"]
    LogProgress --> CheckError{"Error?"}
    
    CheckError -->|Yes| LogError["Log error message"]
    CheckError -->|No| NextSubtask{"More subtasks?"}
    
    LogError --> MarkFailed["Mark task failed"]
    NextSubtask -->|Yes| Loop
    NextSubtask -->|No| MarkComplete["Mark task complete"]
    
    MarkFailed --> End["Task finished"]
    MarkComplete --> End
```

**Key Code Paths:**

- Task creation: [agent/app/service/container.go:521-525]()
- Adding subtasks: [agent/app/service/container.go:527-536]()
- Async execution: [agent/app/service/container.go:574-579]()
- Container create example: [agent/app/service/container.go:509-583]()

**Sources:** [agent/app/service/container.go:305-339](), [agent/app/service/container.go:509-583]()

#### Frontend Task Log Integration

The frontend uses a `TaskLog` component to display real-time progress:

```mermaid
flowchart LR
    Submit["User submits form"] --> GenerateID["taskID = newUUID()"]
    GenerateID --> APICall["API call with taskID"]
    APICall --> OpenDialog["taskLogRef.acceptParams()"]
    OpenDialog --> Stream["Stream task logs endpoint"]
    Stream --> Display["Display in TaskLog component"]
    
    Display --> UserAction{"User action"}
    UserAction -->|"Keep editing"| Close["Close dialog only"]
    UserAction -->|"Back to list"| Navigate["Navigate away"]
```

**Sources:** [frontend/src/views/container/container/operate/index.vue:327-332](), [frontend/src/views/container/container/operate/index.vue:549-551]()

---

### Pattern 3: Real-time Streaming (Server-Sent Events)

For continuous data streams like container logs, the system uses SSE (Server-Sent Events) to push updates to the client.

```mermaid
sequenceDiagram
    participant Browser as "Browser"
    participant Frontend as "Vue Component"
    participant Gin as "Gin Handler"
    participant Service as "Service.StreamLogs()"
    participant Process as "docker logs subprocess"
    
    Browser->>Frontend: "View logs"
    Frontend->>Gin: "GET /containers/search/log?container=X&follow=true"
    
    Gin->>Gin: "Set SSE headers"
    Note over Gin: Content-Type: text/event-stream<br/>Cache-Control: no-cache
    
    Gin->>Service: "StreamLogs(ctx, params)"
    Service->>Process: "exec.Command(docker, logs, -f)"
    Service->>Process: "Start process"
    
    loop Continuous Stream
        Process-->>Service: "Log line"
        Service->>Gin: "messageChan <- line"
        Gin->>Frontend: "data: log line\n\n"
        Frontend->>Browser: "Append to terminal"
    end
    
    Browser->>Frontend: "User closes view"
    Frontend->>Gin: "Close connection"
    Gin->>Service: "doneChan closed"
    Service->>Process: "Kill process (SIGKILL)"
```

**SSE Message Format:**

```
data: 2024-01-15 10:30:45 Container started\n\n
data: 2024-01-15 10:30:46 Listening on port 8080\n\n
event: error\ndata: Connection lost\n\n
```

**Key Implementation Details:**

1. **SSE Headers**: Set by Gin handler at [agent/app/api/v2/container.go:766-769]()
2. **Streaming Function**: `collectLogs()` goroutine at [agent/app/service/container.go:951-1056]()
3. **Process Management**: Uses `syscall.Setpgid` and `SIGKILL` for cleanup at [agent/app/service/container.go:992]()
4. **Graceful Shutdown**: `doneChan` signals termination at [agent/app/service/container.go:924-929]()

**Sources:** [agent/app/service/container.go:921-1056](), [agent/app/api/v2/container.go:765-792]()

---

### Pattern 4: Multi-Node Request Routing

In multi-node deployments, the Core server routes requests to appropriate Agent nodes based on the `CurrentNode` header or `?operateNode=X` query parameter.

```mermaid
flowchart TD
    Request["HTTP Request"] --> CheckHeader{"Has CurrentNode<br/>header?"}
    CheckHeader -->|Yes| HeaderNode["nodeID = CurrentNode"]
    CheckHeader -->|No| CheckQuery{"Has operateNode<br/>query param?"}
    
    CheckQuery -->|Yes| QueryNode["nodeID = operateNode"]
    CheckQuery -->|No| LocalNode["nodeID = local (master)"]
    
    HeaderNode --> Route
    QueryNode --> Route
    LocalNode --> Route
    
    Route["Route to node"] --> IsMaster{"Is master<br/>node?"}
    
    IsMaster -->|Yes| LocalExec["Execute locally"]
    IsMaster -->|No| Proxy["Proxy to agent node"]
    
    Proxy --> AgentAPI["Agent API: /api/v2/..."]
    LocalExec --> Response["Return response"]
    AgentAPI --> Response
```

**Node Selection Examples:**

| Scenario | Header/Query | Target |
|----------|-------------|--------|
| Dashboard view for Node 1 | `CurrentNode: 1` | Agent Node 1 |
| Container operation with explicit node | `?operateNode=2` | Agent Node 2 |
| Default master operation | None | Master node (local) |
| Settings API (always master) | Ignored | Master node |

**API Examples:**

```typescript
// Frontend: Explicit node routing
const params = operateNode ? `?operateNode=${operateNode}` : '';
return http.post(`/containers/compose/clean/log${params}`, {...});
```

```typescript
// Frontend: Load app store config for specific node
export const getAppStoreConfig = (node?: string) => {
    const params = node ? `?operateNode=${node}` : '';
    return http.get<App.AppStoreConfig>(`/core/settings/apps/store/config${params}`);
};
```

**Core Server Data Aggregation:**

The Core server can read metrics from all agent databases for unified monitoring:

```mermaid
graph LR
    CoreAPI["Core API"] --> MasterDB[("master<br/>agent.db")]
    CoreAPI --> Agent1DB[("agent1<br/>agent.db")]
    CoreAPI --> Agent2DB[("agent2<br/>agent.db")]
    
    CoreAPI --> Aggregate["Aggregate metrics<br/>across all nodes"]
    Aggregate --> Dashboard["Dashboard display"]
```

**Sources:** [frontend/src/api/modules/container.ts:42-48](), [frontend/src/api/modules/setting.ts:157-163]()

---

## Detailed Data Flow Examples

### Container Lifecycle Flow

This diagram shows the complete flow from user interaction to Docker container creation, including all layers and state transitions.

```mermaid
sequenceDiagram
    participant User
    participant Form as "ContainerOperate Vue"
    participant FormValidation as "Form Validation"
    participant APIClient as "API Client"
    participant Handler as "ContainerCreate Handler"
    participant Service as "ContainerService"
    participant Task as "Task System"
    participant Docker as "Docker SDK"
    participant TaskLog as "TaskLog Component"
    
    User->>Form: "Fill form & submit"
    Form->>Form: "volumeRef.loadVolumes()"
    Form->>Form: "networkRef.loadNetworks()"
    Form->>FormValidation: "formRef.validate()"
    
    alt Validation fails
        FormValidation-->>Form: "Show errors"
        Form-->>User: "Display validation messages"
    end
    
    FormValidation-->>Form: "Valid"
    Form->>Form: "taskID = newUUID()"
    Form->>Form: "Parse cmdStr, entrypointStr"
    Form->>APIClient: "createContainer(form)"
    
    APIClient->>Handler: "POST /containers"
    Note over Handler: JSON body contains:<br/>taskID, name, image,<br/>ports, volumes, etc.
    
    Handler->>Handler: "CheckBindAndValidate()"
    Handler->>Service: "ContainerCreate(req, true)"
    
    Service->>Task: "task.NewTaskWithOps(name, TaskCreate, TaskScopeContainer)"
    Task-->>Service: "taskItem"
    
    Service->>Task: "AddSubTask: Pull Image"
    Service->>Task: "AddSubTask: Validate Config"
    Service->>Task: "AddSubTask: Create & Start"
    
    Service->>Service: "go func() { taskItem.Execute() }"
    Service-->>Handler: "return nil"
    Handler-->>APIClient: "200 OK"
    APIClient-->>Form: "Success"
    
    Form->>TaskLog: "taskLogRef.acceptParams(taskID)"
    TaskLog->>APIClient: "Stream task logs (SSE)"
    
    par Async Task Execution
        Task->>Docker: "Pull image if needed"
        Docker-->>Task: "Pull complete"
        Task->>Task: "Log: Image pulled"
        
        Task->>Docker: "ImageInspectWithRaw(image)"
        Docker-->>Task: "Image config"
        Task->>Task: "Fill missing entrypoint/cmd"
        
        Task->>Service: "loadConfigInfo()"
        Service-->>Task: "container.Config, HostConfig"
        
        Task->>Docker: "ContainerCreate(config)"
        Docker-->>Task: "containerID"
        Task->>Task: "Log: Container created"
        
        Task->>Docker: "ContainerStart(containerID)"
        Docker-->>Task: "Started"
        Task->>Task: "Log: Container started"
    end
    
    loop Stream logs
        Task->>TaskLog: "Log message"
        TaskLog->>User: "Display in real-time"
    end
    
    User->>TaskLog: "Click 'Back to list' or 'Keep editing'"
```

**Key Decision Points:**

1. **Form Validation** [frontend/src/views/container/container/operate/index.vue:520-548]()
   - Volume/network completeness check
   - Port configuration validation
   - CPU/Memory limits validation

2. **Task Execution Mode** [agent/app/service/container.go:574-582]()
   - `inThread=true`: Launch goroutine, return immediately
   - `inThread=false`: Execute synchronously (used for app installations)

3. **Image Pull Strategy** [agent/app/service/container.go:527-536]()
   - If `forcePull=true`: Always pull
   - If image missing: Pull
   - Otherwise: Use cached image

**Sources:** [agent/app/service/container.go:509-583](), [frontend/src/views/container/container/operate/index.vue:520-562]()

---

### Container Update vs Upgrade Flow

Understanding the difference between update and upgrade operations:

```mermaid
flowchart TD
    Start["User action"] --> Choice{"Operation type?"}
    
    Choice -->|Update| UpdateStart["ContainerUpdate()"]
    Choice -->|Upgrade| UpgradeStart["ContainerUpgrade()"]
    
    UpdateStart --> UpdateTask["Task: Update container"]
    UpdateTask --> UpdatePull["Pull new image if different"]
    UpdatePull --> UpdateInspect["Inspect old container"]
    UpdateInspect --> UpdateRemove["Remove old container"]
    UpdateRemove --> UpdateCreate["Create with new config"]
    UpdateCreate --> UpdateStart2["Start container"]
    UpdateStart2 --> UpdateFail{"Start failed?"}
    UpdateFail -->|Yes| UpdateRollback["Recreate old container"]
    UpdateFail -->|No| UpdateDone["Update complete"]
    
    UpgradeStart --> UpgradeTask["Task: Upgrade image"]
    UpgradeTask --> UpgradePull["Pull new image version"]
    UpgradePull --> UpgradeLoop["For each container"]
    UpgradeLoop --> UpgradeInspect["Inspect container"]
    UpgradeInspect --> UpgradeRemove["Remove container"]
    UpgradeRemove --> UpgradeCreate["Recreate with new image"]
    UpgradeCreate --> UpgradeStart2["Start container"]
    UpgradeStart2 --> UpgradeFail{"Start failed?"}
    UpgradeFail -->|Yes| UpgradeRollback["Recreate with old image"]
    UpgradeFail -->|No| UpgradeNext{"More containers?"}
    UpgradeNext -->|Yes| UpgradeLoop
    UpgradeNext -->|No| UpgradeDone["Upgrade complete"]
    
    UpdateRollback --> UpdateDone
    UpgradeRollback --> UpgradeNext
```

**Update Operation** (`ContainerUpdate`):
- Modifies configuration of a single container
- Can change: ports, volumes, env vars, resource limits, networks
- Image can be changed
- Old container config preserved for rollback

**Upgrade Operation** (`ContainerUpgrade`):
- Updates image version for multiple containers
- Preserves all container configuration
- Only changes the image tag/version
- Batch operation across multiple containers

**Sources:** [agent/app/service/container.go:652-717](), [agent/app/service/container.go:719-793]()

---

### Authentication and Session Flow

```mermaid
sequenceDiagram
    participant Browser
    participant LoginView as "Login Vue Component"
    participant APIClient
    participant CoreAPI as "Core Auth API"
    participant DB as "core.db"
    participant Store as "Global Store (Pinia)"
    
    Browser->>LoginView: "Enter credentials"
    LoginView->>APIClient: "POST /auth/login"
    
    APIClient->>CoreAPI: "POST /core/auth/login"
    CoreAPI->>CoreAPI: "Validate password (bcrypt)"
    
    alt MFA Enabled
        CoreAPI->>CoreAPI: "Verify TOTP code"
    end
    
    alt Passkey Enabled
        CoreAPI->>CoreAPI: "Verify WebAuthn signature"
    end
    
    CoreAPI->>DB: "Update last login time"
    CoreAPI->>CoreAPI: "Generate JWT token"
    CoreAPI-->>APIClient: "token, user info, nodes"
    
    APIClient->>Store: "saveToken(token)"
    Store->>Store: "localStorage.setItem('token')"
    
    APIClient->>Store: "saveUserInfo(user)"
    APIClient->>Store: "saveNodes(nodes)"
    Store->>Store: "Set currentNode"
    
    APIClient-->>LoginView: "Success"
    LoginView->>Browser: "Navigate to dashboard"
    
    Browser->>APIClient: "Subsequent requests"
    APIClient->>APIClient: "Add Authorization header"
    Note over APIClient: Authorization: Bearer {token}
    
    APIClient->>CoreAPI: "Any authenticated request"
    CoreAPI->>CoreAPI: "Verify JWT signature"
    CoreAPI->>CoreAPI: "Check token expiration"
    CoreAPI-->>APIClient: "Response"
```

**JWT Token Structure:**

The JWT contains:
- User ID
- Username
- Node information
- Expiration time
- Issued at time

**Token Usage:**

All authenticated requests include the token in the `Authorization` header. The backend middleware validates:
1. Token signature
2. Token expiration
3. User session validity

**Sources:** [frontend/src/api/modules/setting.ts:83-100]()

---

### Dashboard Monitoring Data Flow

The dashboard uses a polling mechanism to fetch real-time metrics every 3 seconds.

```mermaid
sequenceDiagram
    participant Dashboard as "Dashboard Vue"
    participant Timer as "setInterval(3000)"
    participant API as "API Client"
    participant AgentAPI as "Agent API"
    participant System as "System Tools"
    participant Docker as "Docker Client"
    
    Dashboard->>Timer: "Start monitoring"
    
    loop Every 3 seconds
        Timer->>Dashboard: "Trigger update"
        Dashboard->>API: "GET /dashboard/current/:io/:net"
        
        API->>AgentAPI: "GET /api/v2/dashboard/current/:io/:net"
        
        par Collect Metrics
            AgentAPI->>System: "Read /proc/stat (CPU)"
            AgentAPI->>System: "Read /proc/meminfo (Memory)"
            AgentAPI->>System: "Read /proc/diskstats (Disk I/O)"
            AgentAPI->>System: "Read /sys/class/net (Network)"
            AgentAPI->>Docker: "ContainerList() (Container count)"
            AgentAPI->>Docker: "ContainerStats() (Container metrics)"
        end
        
        System-->>AgentAPI: "CPU, Mem, Disk, Net data"
        Docker-->>AgentAPI: "Container data"
        
        AgentAPI->>AgentAPI: "Calculate percentages"
        AgentAPI->>AgentAPI: "Format response"
        AgentAPI-->>API: "Metrics JSON"
        
        API-->>Dashboard: "Metrics"
        Dashboard->>Dashboard: "Update charts"
        Dashboard->>Dashboard: "Update values"
    end
    
    Dashboard->>Timer: "Component unmounted"
    Timer->>Timer: "clearInterval()"
```

**Metrics Collected:**

| Category | Metrics | Source |
|----------|---------|--------|
| CPU | Usage %, per-core usage | `/proc/stat` |
| Memory | Used, Available, Total, % | `/proc/meminfo` |
| Disk I/O | Read/Write rates | `/proc/diskstats` |
| Network | RX/TX rates | `/sys/class/net` |
| Containers | Count by state, CPU/Mem per container | Docker SDK |
| GPU | Usage, temp, memory (if present) | `nvidia-smi`, `xpu-smi` |

**Response Caching Strategy:**

The dashboard endpoint uses query parameters to control data freshness:
- `io` parameter: Disk I/O sampling interval
- `net` parameter: Network sampling interval

**Sources:** References from overview diagram, typical monitoring implementation patterns

---

## Type System Integration

The system maintains type safety across the TypeScript-Go boundary through parallel interface definitions.

### TypeScript to Go DTO Mapping

```mermaid
graph LR
    subgraph "Frontend (TypeScript)"
        TSInterface["interface Container.ContainerHelper"]
        TSFields["name: string<br/>image: string<br/>networks: ContainerNetwork[]<br/>exposedPorts: Port[]<br/>volumes: Volume[]"]
    end
    
    subgraph "HTTP Layer"
        JSON["JSON Serialization"]
    end
    
    subgraph "Backend (Go)"
        GoDTO["dto.ContainerOperate"]
        GoFields["Name string<br/>Image string<br/>Networks []ContainerNetwork<br/>ExposedPorts []PortHelper<br/>Volumes []VolumeHelper"]
    end
    
    TSInterface --> TSFields
    TSFields --> JSON
    JSON --> GoFields
    GoFields --> GoDTO
    
    style TSInterface fill:#ffe6e6
    style GoDTO fill:#e6ffe6
```

**Example Type Correspondence:**

| TypeScript Interface | Go DTO | Purpose |
|---------------------|--------|---------|
| `Container.ContainerHelper` | `dto.ContainerOperate` | Container creation/update |
| `Container.ContainerSearch` | `dto.PageContainer` | Container pagination query |
| `Container.ContainerStatus` | `dto.ContainerStatus` | Container statistics |
| `Container.ComposeCreate` | `dto.ComposeCreate` | Compose file deployment |
| `Container.NetworkCreate` | `dto.NetworkCreate` | Docker network creation |
| `Container.VolumeCreate` | `dto.VolumeCreate` | Docker volume creation |

**Sources:** [frontend/src/api/interface/container.ts:4-406](), [agent/app/dto/container.go:1-323]()

### Nested Type Structures

Both languages handle complex nested structures:

**TypeScript:**
```typescript
export interface ContainerHelper {
    name: string;
    networks: Array<ContainerNetwork>;  // Nested array
    exposedPorts: Array<Port>;          // Nested array
}

export interface ContainerNetwork {
    network: string;
    ipv4: string;
    ipv6: string;
    macAddr: string;
}
```

**Go:**
```go
type ContainerOperate struct {
    Name         string             `json:"name"`
    Networks     []ContainerNetwork `json:"networks"`  // Nested slice
    ExposedPorts []PortHelper       `json:"exposedPorts"` // Nested slice
}

type ContainerNetwork struct {
    Network string `json:"network"`
    Ipv4    string `json:"ipv4"`
    Ipv6    string `json:"ipv6"`
    MacAddr string `json:"macAddr"`
}
```

**JSON Tags for Serialization:**

Go struct tags specify JSON field names to match TypeScript camelCase conventions:
- `json:"name"` → TypeScript `name`
- `json:"exposedPorts"` → TypeScript `exposedPorts`
- `json:"cpuShares"` → TypeScript `cpuShares`

**Sources:** [frontend/src/api/interface/container.ts:63-93](), [agent/app/dto/container.go:73-101]()

---

## Error Handling and Validation Patterns

### Frontend Validation Flow

```mermaid
flowchart TD
    UserInput["User fills form"] --> ClientValidation["Client-side validation"]
    
    ClientValidation --> CheckRequired{"Required fields<br/>filled?"}
    CheckRequired -->|No| ShowError1["Display field errors"]
    CheckRequired -->|Yes| CheckFormat{"Format valid?"}
    
    CheckFormat -->|No| ShowError2["Display format errors"]
    CheckFormat -->|Yes| CheckLogic{"Business logic<br/>valid?"}
    
    CheckLogic -->|No| ShowError3["Display logic errors"]
    CheckLogic -->|Yes| SubmitAPI["Submit to API"]
    
    SubmitAPI --> APIValidation["Backend validation"]
    
    APIValidation --> ServerCheck{"Server-side<br/>validation?"}
    ServerCheck -->|Fail| APIError["Return 400 Bad Request"]
    ServerCheck -->|Pass| Execute["Execute operation"]
    
    APIError --> DisplayServerError["Display server error message"]
    Execute --> Success["Return 200 OK"]
```

**Frontend Validation Rules:**

```typescript
// Form validation rules
const rules = reactive({
    name: [Rules.requiredInput, Rules.containerName],
    image: [Rules.imageName],
    cpuShares: [Rules.integerNumberWith0, checkNumberRange(0, 262144)],
    nanoCPUs: [Rules.floatNumber],
    memory: [Rules.floatNumber],
});
```

Common validation rules include:
- `Rules.requiredInput`: Field must not be empty
- `Rules.containerName`: Valid Docker container name format
- `Rules.imageName`: Valid Docker image name format
- `checkNumberRange(min, max)`: Numeric range validation
- `checkFloatNumberRange(min, max)`: Float range validation

**Sources:** [frontend/src/views/container/container/operate/index.vue:469-475]()

### Backend Validation with Struct Tags

Go uses struct tags for automatic validation:

```go
type ContainerOperate struct {
    Name   string `json:"name" validate:"required"`
    Image  string `json:"image" validate:"required"`
    // ...
}

type ContainerOperation struct {
    Names     []string `json:"names" validate:"required"`
    Operation string   `json:"operation" validate:"required,oneof=up start stop restart kill pause unpause remove"`
}
```

**Validation Tag Examples:**

| Tag | Meaning | Example |
|-----|---------|---------|
| `required` | Field must be present | `validate:"required"` |
| `oneof` | Must be one of specified values | `validate:"oneof=up down start stop"` |
| `min`, `max` | Numeric range | `validate:"min=0,max=100"` |
| `ip` | Must be valid IP address | `validate:"ip"` |

**Sources:** [agent/app/dto/container.go:73-101](), [agent/app/dto/container.go:174-178]()

### Error Response Format

When validation fails or errors occur, the backend returns structured error responses:

```json
{
  "code": 400,
  "message": "validation failed: name is required",
  "data": null
}
```

**Error Handling in API Client:**

The frontend API client intercepts error responses and displays localized messages:

```typescript
// API client error interceptor
http.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 400) {
            MsgError(i18n.global.t('commons.msg.validationError'));
        }
        // ... other error handling
    }
);
```

**Sources:** [frontend/src/views/container/container/operate/index.vue:354]()

---

## API Route to Service Method Mapping

This table shows how HTTP routes map to service methods for container operations:

| HTTP Method | Route | Handler Method | Service Method | Description |
|-------------|-------|----------------|----------------|-------------|
| POST | `/containers/search` | `SearchContainer` | `containerService.Page()` | Paginate containers |
| POST | `/containers/list` | `ListContainer` | `containerService.List()` | List all containers |
| GET | `/containers/status` | `LoadContainerStatus` | `containerService.LoadStatus()` | Container counts by state |
| GET | `/containers/limit` | `LoadResourceLimit` | `containerService.LoadResourceLimit()` | CPU/Memory limits |
| POST | `/containers` | `ContainerCreate` | `containerService.ContainerCreate()` | Create container (async) |
| POST | `/containers/update` | `ContainerUpdate` | `containerService.ContainerUpdate()` | Update container (async) |
| POST | `/containers/upgrade` | `ContainerUpgrade` | `containerService.ContainerUpgrade()` | Upgrade image (async) |
| POST | `/containers/info` | `ContainerInfo` | `containerService.ContainerInfo()` | Get container config |
| POST | `/containers/operate` | `ContainerOperation` | `containerService.ContainerOperation()` | Start/stop/restart |
| POST | `/containers/commit` | `ContainerCommit` | `containerService.ContainerCommit()` | Commit to image |
| POST | `/containers/rename` | `ContainerRename` | `containerService.ContainerRename()` | Rename container |
| POST | `/containers/prune` | `ContainerPrune` | `containerService.Prune()` | Clean unused resources |
| GET | `/containers/search/log` | `ContainerStreamLogs` | `containerService.StreamLogs()` | Stream logs (SSE) |
| POST | `/containers/clean/log` | `CleanContainerLog` | `containerService.ContainerLogClean()` | Truncate log files |
| GET | `/containers/stats/:id` | `ContainerStats` | `containerService.ContainerStats()` | Real-time stats |

**Route Registration:**

Routes are registered in the router initialization:

```go
baRouter.POST("/search", baseApi.SearchContainer)
baRouter.POST("", baseApi.ContainerCreate)
baRouter.POST("/update", baseApi.ContainerUpdate)
// ... more routes
```

**Sources:** [agent/router/ro_container.go:10-91](), [agent/app/api/v2/container.go:21-793]()

---

## Integration Pattern Summary

| Pattern | Use Cases | Response Type | Typical Duration |
|---------|-----------|---------------|------------------|
| **Synchronous Request-Response** | List operations, Get info, Simple updates | Complete JSON | < 5 seconds |
| **Async Task Execution** | Container create/update, Image pull, Compose deployment | Task ID + SSE logs | 10s - 10m |
| **Real-time Streaming (SSE)** | Container logs, Task logs, Live monitoring | Event stream | Continuous |
| **Multi-Node Routing** | Distributed operations, Cross-node queries | Varies | Varies |

**Pattern Selection Guidelines:**

1. **Use Synchronous** when:
   - Operation completes in < 5 seconds
   - User needs immediate result
   - No progress tracking needed
   
2. **Use Async Task** when:
   - Operation may take > 5 seconds
   - Multiple steps to track
   - User needs to see progress
   - Operation can be backgrounded

3. **Use SSE Streaming** when:
   - Continuous data updates
   - Real-time feedback required
   - Logs or metrics display

4. **Use Multi-Node Routing** when:
   - Multi-node deployment
   - Node-specific operations
   - Cross-node aggregation

**Sources:** Overall architecture understanding from [agent/app/service/container.go](), [agent/app/api/v2/container.go](), [frontend/src/api/modules/container.ts]()

---

# Page: Build System and Development

# Build System and Development

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Makefile](Makefile)
- [agent/utils/common/sqlite.go](agent/utils/common/sqlite.go)
- [core/middleware/operation.go](core/middleware/operation.go)
- [core/utils/common/sqlite.go](core/utils/common/sqlite.go)

</details>



This document explains the 1Panel build system, development workflow, compilation process, and build optimization strategies. It covers the Makefile-based build orchestration, frontend and backend compilation pipelines, cross-compilation support, and database initialization patterns used during development.

For information about the runtime architecture and service initialization, see [Backend Service Layer](#2.3). For frontend build artifacts and routing, see [Frontend Architecture](#2.4).

## Build System Overview

1Panel uses a Makefile-based build system that orchestrates the compilation of three distinct components: the Vue.js frontend, the Go-based Core API server, and the Go-based Agent API server. The build process produces statically-linked binaries suitable for Linux deployment, with optional support for cross-compilation from macOS development environments.

**Sources:** [Makefile:1-50]()

## Build Directory Structure

The build system operates on a well-defined directory structure that separates source code, build artifacts, and frontend assets:

```mermaid
graph TB
    BASE["BASE_PATH<br/>(Project Root)"]
    
    subgraph "Source Directories"
        CORE["CORE_PATH<br/>core/"]
        AGENT["AGENT_PATH<br/>agent/"]
        WEB["WEB_PATH<br/>frontend/"]
    end
    
    subgraph "Entry Points"
        CORE_MAIN["CORE_MAIN<br/>core/cmd/server/main.go"]
        AGENT_MAIN["AGENT_MAIN<br/>agent/cmd/server/main.go"]
    end
    
    subgraph "Build Output"
        BUILD["BUILD_PATH<br/>build/"]
        CORE_BIN["1panel-core<br/>(binary)"]
        AGENT_BIN["1panel-agent<br/>(binary)"]
    end
    
    subgraph "Frontend Assets"
        ASSERT["ASSERT_PATH<br/>core/cmd/server/web/assets"]
        DIST["frontend/dist<br/>(npm build output)"]
    end
    
    BASE --> CORE
    BASE --> AGENT
    BASE --> WEB
    BASE --> BUILD
    
    CORE --> CORE_MAIN
    AGENT --> AGENT_MAIN
    
    CORE_MAIN --> CORE_BIN
    AGENT_MAIN --> AGENT_BIN
    
    CORE_BIN --> BUILD
    AGENT_BIN --> BUILD
    
    WEB --> DIST
    DIST -.copied to.-> ASSERT
```

**Sources:** [Makefile:7-18]()

| Variable | Path | Purpose |
|----------|------|---------|
| `BASE_PATH` | Project root | Base directory for all paths |
| `BUILD_PATH` | `build/` | Output directory for compiled binaries |
| `WEB_PATH` | `frontend/` | Vue.js application source |
| `ASSERT_PATH` | `core/cmd/server/web/assets` | Embedded frontend assets for Core server |
| `CORE_PATH` | `core/` | Core API server source |
| `AGENT_PATH` | `agent/` | Agent API server source |
| `CORE_MAIN` | `core/cmd/server/main.go` | Core binary entry point |
| `AGENT_MAIN` | `agent/cmd/server/main.go` | Agent binary entry point |

**Sources:** [Makefile:7-18]()

## Frontend Build Pipeline

The frontend build process compiles the Vue 3 TypeScript application into optimized production assets using Vite:

```mermaid
graph LR
    SRC["frontend/<br/>Vue 3 + TypeScript"]
    
    NPM_INSTALL["npm install<br/>(dependency resolution)"]
    NPM_BUILD["npm run build:pro<br/>(Vite production build)"]
    
    DIST["frontend/dist/<br/>(minified assets)"]
    ASSERT["core/cmd/server/web/assets<br/>(embedded in Core binary)"]
    
    SRC --> NPM_INSTALL
    NPM_INSTALL --> NPM_BUILD
    NPM_BUILD --> DIST
    DIST -.embedded via go:embed.-> ASSERT
```

The `build_frontend` target executes the frontend build:

```makefile
build_frontend:
    cd $(WEB_PATH) && npm install && npm run build:pro
```

This target:
1. Changes to the `frontend/` directory
2. Installs npm dependencies from `package.json`
3. Runs the Vite production build script (`build:pro`)
4. Outputs minified assets to `frontend/dist/`

The compiled frontend assets are then embedded into the Core server binary at compile time using Go's `embed` directive, making the Core server a self-contained executable that serves both the API and the web interface.

**Sources:** [Makefile:28-29]()

## Backend Build Pipeline

The backend build process compiles two independent Go binaries with static linking and optimization flags:

### Build Flags and Optimization

All backend builds use the following compiler configuration:

| Flag | Purpose |
|------|---------|
| `CGO_ENABLED=0` | Disable CGO for fully static binaries (no C dependencies) |
| `GOOS=$(GOOS)` | Target operating system (linux or darwin) |
| `GOARCH=$(GOARCH)` | Target architecture (amd64, arm64, etc.) |
| `-trimpath` | Remove file system paths from compiled binary (reproducible builds) |
| `-ldflags '-s -w'` | Strip debug info (`-s`) and DWARF symbol table (`-w`) for smaller binaries |

**Sources:** [Makefile:32-37]()

### Core API Build

```mermaid
graph LR
    CORE_SRC["core/<br/>(Go source)"]
    CORE_MAIN["core/cmd/server/main.go"]
    GOBUILD["go build<br/>CGO_ENABLED=0<br/>-trimpath<br/>-ldflags '-s -w'"]
    CORE_BIN["build/1panel-core"]
    
    CORE_SRC --> CORE_MAIN
    CORE_MAIN --> GOBUILD
    GOBUILD --> CORE_BIN
```

Build targets:
- `build_core_on_linux`: Native Linux build using system `GOOS`/`GOARCH`
- `build_core_on_darwin`: Cross-compile from macOS to Linux amd64

**Sources:** [Makefile:31-45]()

### Agent API Build

```mermaid
graph LR
    AGENT_SRC["agent/<br/>(Go source)"]
    AGENT_MAIN["agent/cmd/server/main.go"]
    GOBUILD["go build<br/>CGO_ENABLED=0<br/>-trimpath<br/>-ldflags '-s -w'"]
    AGENT_BIN["build/1panel-agent"]
    
    AGENT_SRC --> AGENT_MAIN
    AGENT_MAIN --> GOBUILD
    GOBUILD --> AGENT_BIN
```

Build targets:
- `build_agent_on_linux`: Native Linux build using system `GOOS`/`GOARCH`
- `build_agent_on_darwin`: Cross-compile from macOS to Linux amd64

**Sources:** [Makefile:35-45]()

## Cross-Compilation Strategy

The build system supports two compilation scenarios:

### Native Linux Build

When building on a Linux system, the Makefile uses the system's native `GOOS` and `GOARCH` environment variables:

```makefile
build_core_on_linux:
    cd $(CORE_PATH) \
    && CGO_ENABLED=0 GOOS=$(GOOS) GOARCH=$(GOARCH) $(GOBUILD) \
       -trimpath -ldflags '-s -w' -o $(BUILD_PATH)/$(CORE_NAME) $(CORE_MAIN)

build_agent_on_linux:
    cd $(AGENT_PATH) \
    && CGO_ENABLED=0 GOOS=$(GOOS) GOARCH=$(GOARCH) $(GOBUILD) \
       -trimpath -ldflags '-s -w' -o $(BUILD_PATH)/$(AGENT_NAME) $(AGENT_MAIN)
```

This approach supports building for multiple Linux architectures (amd64, arm64, etc.) by setting environment variables before running `make`.

**Sources:** [Makefile:31-37]()

### macOS to Linux Cross-Compilation

When building on macOS (Darwin), the Makefile explicitly sets `GOOS=linux` and `GOARCH=amd64` to produce Linux binaries:

```makefile
build_core_on_darwin:
    cd $(CORE_PATH) \
    && CGO_ENABLED=0 GOOS=linux GOARCH=amd64 $(GOBUILD) \
       -trimpath -ldflags '-s -w' -o $(BUILD_PATH)/$(CORE_NAME) $(CORE_MAIN)

build_agent_on_darwin:
    cd $(AGENT_PATH) \
    && CGO_ENABLED=0 GOOS=linux GOARCH=amd64 $(GOBUILD) \
       -trimpath -ldflags '-s -w' -o $(BUILD_PATH)/$(AGENT_NAME) $(AGENT_MAIN)
```

This enables developers to build deployment-ready Linux binaries on macOS workstations without requiring a Linux VM or container.

**Sources:** [Makefile:39-45]()

## Build Targets and Workflow

The Makefile provides several composite targets for common build workflows:

```mermaid
graph TB
    subgraph "Production Build (Linux)"
        BUILD_ALL["make build_all"]
        BUILD_ALL_FE["build_frontend"]
        BUILD_ALL_CORE["build_core_on_linux"]
        BUILD_ALL_AGENT["build_agent_on_linux"]
        
        BUILD_ALL --> BUILD_ALL_FE
        BUILD_ALL --> BUILD_ALL_CORE
        BUILD_ALL --> BUILD_ALL_AGENT
    end
    
    subgraph "Development Build (macOS)"
        BUILD_LOCAL["make build_on_local"]
        CLEAN["clean_assets"]
        BUILD_LOCAL_FE["build_frontend"]
        BUILD_LOCAL_CORE["build_core_on_darwin"]
        BUILD_LOCAL_AGENT["build_agent_on_darwin"]
        
        BUILD_LOCAL --> CLEAN
        BUILD_LOCAL --> BUILD_LOCAL_FE
        BUILD_LOCAL --> BUILD_LOCAL_CORE
        BUILD_LOCAL --> BUILD_LOCAL_AGENT
    end
    
    subgraph "Optional Optimization"
        UPX["make upx_bin"]
        UPX_CORE["upx build/1panel-core"]
        UPX_AGENT["upx build/1panel-agent"]
        
        UPX --> UPX_CORE
        UPX --> UPX_AGENT
    end
```

### Target Descriptions

| Target | Purpose | Dependencies |
|--------|---------|--------------|
| `clean_assets` | Remove embedded frontend assets | None |
| `build_frontend` | Compile Vue.js application | npm, Node.js |
| `build_core_on_linux` | Compile Core binary (native Linux) | Go 1.22+ |
| `build_agent_on_linux` | Compile Agent binary (native Linux) | Go 1.22+ |
| `build_core_on_darwin` | Cross-compile Core binary (macOS → Linux) | Go 1.22+ |
| `build_agent_on_darwin` | Cross-compile Agent binary (macOS → Linux) | Go 1.22+ |
| `build_all` | Full production build (Linux) | All Linux targets |
| `build_on_local` | Full development build (macOS) | All Darwin targets |
| `upx_bin` | Compress binaries with UPX | UPX utility |

**Sources:** [Makefile:21-49]()

### Typical Development Workflow

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Make as Makefile
    participant NPM as npm/Vite
    participant Go as Go Compiler
    participant Build as build/
    
    Note over Dev,Build: Development Iteration
    
    Dev->>Make: make build_on_local
    Make->>Make: clean_assets
    
    Make->>NPM: cd frontend && npm install
    NPM-->>Make: Dependencies installed
    
    Make->>NPM: npm run build:pro
    NPM->>NPM: Vite production build
    NPM-->>Make: frontend/dist/ created
    
    Make->>Go: build Core (GOOS=linux GOARCH=amd64)
    Go->>Go: Compile with -trimpath -ldflags '-s -w'
    Go-->>Build: build/1panel-core
    
    Make->>Go: build Agent (GOOS=linux GOARCH=amd64)
    Go->>Go: Compile with -trimpath -ldflags '-s -w'
    Go-->>Build: build/1panel-agent
    
    Build-->>Dev: Binaries ready for testing
```

**Sources:** [Makefile:47-49]()

## Development Environment Setup

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Go | 1.22+ | Backend compilation |
| Node.js | 16+ | Frontend build tooling |
| npm | 8+ | JavaScript package management |
| Make | 3.81+ | Build orchestration |
| UPX | 3.96+ (optional) | Binary compression |

### Local Build Commands

For developers working on macOS:
```bash
# Full build with frontend and cross-compiled binaries
make build_on_local

# Individual component builds
make clean_assets        # Clean embedded frontend assets
make build_frontend      # Build only Vue.js frontend
make build_core_on_darwin   # Build only Core binary
make build_agent_on_darwin  # Build only Agent binary
```

For developers working on Linux:
```bash
# Full build
make build_all

# Individual component builds
make build_frontend         # Build Vue.js frontend
make build_core_on_linux    # Build Core binary
make build_agent_on_linux   # Build Agent binary
```

For production releases with maximum compression:
```bash
make build_all
make upx_bin  # Compress binaries with UPX
```

**Sources:** [Makefile:21-49]()

## Database Initialization Patterns

The system initializes three SQLite databases during startup: `core.db`, `xpack.db`, and `agent.db`. The database initialization logic follows a consistent pattern across both Core and Agent services.

### Database Connection Initialization

```mermaid
graph TB
    APP_START["Application Start"]
    
    LOAD_DB["LoadDBConnByPath<br/>(fullPath, dbName)"]
    CHECK_DIR["CreateDirWhenNotExist<br/>(path.Dir(fullPath))"]
    CHECK_FILE["os.Stat(fullPath)"]
    CREATE_FILE["os.Create(fullPath)"]
    OPEN_DB["gorm.Open(sqlite.Open(dbPath))"]
    CONFIG_POOL["Configure Connection Pool"]
    
    APP_START --> LOAD_DB
    LOAD_DB --> CHECK_DIR
    CHECK_DIR --> CHECK_FILE
    CHECK_FILE -->|exists| OPEN_DB
    CHECK_FILE -->|not exists| CREATE_FILE
    CREATE_FILE --> OPEN_DB
    OPEN_DB --> CONFIG_POOL
    CONFIG_POOL --> READY["*gorm.DB Ready"]
```

### Core Service Database Initialization

The Core service initializes databases using the pattern defined in [core/utils/common/sqlite.go:15-32]():

```
LoadDBConnByPath(fullPath, dbName) flow:
1. Create directory structure if missing
2. Create empty .db file if missing
3. Open connection with gorm.Open(sqlite.Open(dbPath))
4. Configure connection pool settings
5. Return *gorm.DB instance
```

The database paths are determined by the middleware layer when routing requests. The operation logging middleware dynamically opens connections based on request paths:

| Request Path Prefix | Database File |
|---------------------|---------------|
| `/core` | `{InstallDir}/1panel/db/core.db` |
| `/xpack` | `{InstallDir}/1panel/db/xpack.db` |
| (other) | `{InstallDir}/1panel/db/agent.db` |

**Sources:** [core/utils/common/sqlite.go:15-68](), [core/middleware/operation.go:218-241]()

### Agent Service Database Initialization

The Agent service uses an identical initialization pattern implemented in [agent/utils/common/sqlite.go:16-33]():

```
LoadDBConnByPath(fullPath, dbName) flow:
1. createDirWhenNotExist(isDir=true, path.Dir(fullPath))
2. os.Stat(fullPath) check
3. os.Create(fullPath) if not exists
4. GetDBWithPath(fullPath)
5. Configure connection pool
```

**Sources:** [agent/utils/common/sqlite.go:16-79]()

### Connection Pool Configuration

Both Core and Agent services apply identical SQLite connection pool settings:

| Setting | Value | Rationale |
|---------|-------|-----------|
| `MaxOpenConns` | 4 | SQLite performs best with limited concurrency |
| `MaxIdleConns` | 1 | Minimize idle connections for lightweight SQLite |
| `ConnMaxIdleTime` | 15 minutes | Close idle connections to free resources |
| `ConnMaxLifetime` | 1 hour | Prevent connection staleness |

These settings are optimized for SQLite's single-writer model and the application's read-heavy workload patterns.

**Sources:** [agent/utils/common/sqlite.go:74-77](), [core/utils/common/sqlite.go:51-54](), [core/middleware/operation.go:236-239]()

### GORM Configuration

The database initialization uses GORM with the following configuration:

```go
gorm.Config{
    DisableForeignKeyConstraintWhenMigrating: true,
    Logger: logger.Silent,  // Production: silent logging
    IgnoreRecordNotFoundError: true,
    Colorful: false,
}
```

- **Foreign key constraints disabled**: Allows flexible schema evolution during migrations
- **Silent logging**: Reduces log verbosity in production
- **Ignore record not found**: Simplifies error handling for optional lookups
- **No color output**: Clean logs for log aggregation systems

**Sources:** [agent/utils/common/sqlite.go:63-66](), [core/utils/common/sqlite.go:43-46](), [agent/utils/common/sqlite.go:82-90](), [core/utils/common/sqlite.go:58-67]()

## Build Optimization Strategies

### Binary Size Reduction

The build system employs multiple strategies to minimize binary size:

1. **CGO Disabled (`CGO_ENABLED=0`)**: Produces fully static binaries without C library dependencies, reducing size and improving portability
2. **Strip Flags (`-ldflags '-s -w'`)**: 
   - `-s`: Omit symbol table and debug information
   - `-w`: Omit DWARF debugging information
   - Combined reduction: typically 20-30% smaller binaries
3. **Path Trimming (`-trimpath`)**: Removes file system paths from compiled code, enabling reproducible builds and slight size reduction
4. **Optional UPX Compression**: The `upx_bin` target can compress binaries by 50-70% using UPX, though at the cost of slower startup times

**Sources:** [Makefile:24-26](), [Makefile:32-37]()

### Static Linking Benefits

`CGO_ENABLED=0` ensures that Go produces fully static binaries with no external dependencies. This provides:

- **Deployment simplicity**: Single binary with no shared library requirements
- **Container optimization**: Minimal container images (can use `scratch` base)
- **Version consistency**: No runtime library version conflicts
- **Security**: Reduced attack surface from fewer dependencies

**Sources:** [Makefile:32-37]()

### Frontend Asset Embedding

The frontend assets are embedded directly into the Core binary using Go's `embed` directive, eliminating the need to distribute separate static file directories. This approach:

- Simplifies deployment (single binary distribution)
- Ensures version consistency between frontend and backend
- Enables atomic updates (one file to replace)
- Eliminates file permission issues on deployed systems

**Sources:** [Makefile:10]()

## Continuous Integration Considerations

The build system is designed for automated CI/CD pipelines:

```mermaid
graph LR
    GIT["Git Push"]
    CI["CI System"]
    
    subgraph "Build Matrix"
        LINUX_AMD64["Linux amd64"]
        LINUX_ARM64["Linux arm64"]
        LINUX_ARM["Linux arm"]
    end
    
    ARTIFACTS["Build Artifacts"]
    RELEASE["Release Distribution"]
    
    GIT --> CI
    CI --> LINUX_AMD64
    CI --> LINUX_ARM64
    CI --> LINUX_ARM
    
    LINUX_AMD64 --> ARTIFACTS
    LINUX_ARM64 --> ARTIFACTS
    LINUX_ARM --> ARTIFACTS
    
    ARTIFACTS --> RELEASE
```

The build system supports architecture-specific builds by setting `GOARCH` environment variables:

```bash
# AMD64 build
GOARCH=amd64 make build_all

# ARM64 build
GOARCH=arm64 make build_all

# ARM v7 build
GOARCH=arm GOARM=7 make build_all
```

This enables building release artifacts for multiple architectures from a single build script.

**Sources:** [Makefile:4-5](), [Makefile:31-37]()

---

# Page: Authentication and Security

# Authentication and Security

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Makefile](Makefile)
- [agent/utils/common/sqlite.go](agent/utils/common/sqlite.go)
- [core/middleware/operation.go](core/middleware/operation.go)
- [core/utils/common/sqlite.go](core/utils/common/sqlite.go)
- [frontend/src/api/interface/setting.ts](frontend/src/api/interface/setting.ts)
- [frontend/src/api/modules/setting.ts](frontend/src/api/modules/setting.ts)
- [frontend/src/lang/modules/en.ts](frontend/src/lang/modules/en.ts)
- [frontend/src/lang/modules/es-es.ts](frontend/src/lang/modules/es-es.ts)
- [frontend/src/lang/modules/ja.ts](frontend/src/lang/modules/ja.ts)
- [frontend/src/lang/modules/ko.ts](frontend/src/lang/modules/ko.ts)
- [frontend/src/lang/modules/ms.ts](frontend/src/lang/modules/ms.ts)
- [frontend/src/lang/modules/pt-br.ts](frontend/src/lang/modules/pt-br.ts)
- [frontend/src/lang/modules/ru.ts](frontend/src/lang/modules/ru.ts)
- [frontend/src/lang/modules/tr.ts](frontend/src/lang/modules/tr.ts)
- [frontend/src/lang/modules/zh-Hant.ts](frontend/src/lang/modules/zh-Hant.ts)
- [frontend/src/lang/modules/zh.ts](frontend/src/lang/modules/zh.ts)

</details>



## Purpose and Scope

This document describes 1Panel's multi-layered security architecture, covering authentication mechanisms, network access controls, API security, and audit logging. The system implements defense-in-depth with six primary security layers: authentication (password/MFA/passkey), network security (safe entrance, IP whitelisting, domain binding), application security (captcha, API keys), data security (encrypted backups, SSL), audit logging, and license enforcement.

For information about general system settings configuration, see [Settings and Configuration Management](#5). For user management and access control within specific subsystems, see the relevant functional domain pages.

---

## Authentication Mechanisms

1Panel supports three authentication methods that can be used independently or combined for enhanced security: traditional password-based authentication with bcrypt hashing, time-based one-time password (TOTP) multi-factor authentication, and WebAuthn passkey authentication for passwordless biometric/hardware key login.

### Authentication Flow

```mermaid
sequenceDiagram
    participant U as "User/Browser"
    participant FE as "Vue Frontend"
    participant CM as "Core Middleware"
    participant CA as "Core Auth Handler"
    participant DB as "core.db (SQLite)"
    participant SS as "Session Store"
    
    U->>FE: "POST /auth/login"
    FE->>CM: "Login Request {username, password}"
    CM->>CA: "Authenticate()"
    CA->>DB: "Query user by username"
    DB-->>CA: "User record (hashed password)"
    CA->>CA: "bcrypt.CompareHashAndPassword()"
    
    alt "Password Valid"
        alt "MFA Enabled (mfaStatus=enable)"
            CA-->>FE: "Require MFA Code"
            FE->>U: "Show MFA Input"
            U->>FE: "Enter 6-digit TOTP code"
            FE->>CA: "Verify MFA {mfaCode}"
            CA->>CA: "ValidateTOTP(mfaSecret, mfaCode)"
            alt "MFA Invalid"
                CA-->>FE: "errorMfaInfo"
                FE->>U: "Show MFA Error"
            end
        end
        
        CA->>SS: "Create Session (JWT)"
        CA->>DB: "Log login attempt (success)"
        CA-->>FE: "JWT Token + User Info"
        FE->>FE: "Store in Pinia (currentNode, user)"
        FE-->>U: "Redirect to Dashboard"
    else "Password Invalid"
        CA->>DB: "Log login attempt (failed)"
        CA-->>FE: "errorAuthInfo"
        FE->>U: "Show Error Message"
    end
```

**Sources:**
- [frontend/src/lang/modules/en.ts:185-224]()
- [frontend/src/lang/modules/zh.ts:192-220]()
- [frontend/src/api/modules/setting.ts:83-96]()

### Password Authentication

The system uses bcrypt for password hashing with configurable complexity requirements. Password policies are enforced through the `complexityVerification` setting stored in the `settings` table.

| Setting Key | Type | Purpose |
|-------------|------|---------|
| `complexityVerification` | `enable`/`disable` | Enforce 8-30 char passwords with letters, numbers, and at least 2 special chars |
| `expirationDays` | integer | Password expiration period |
| `expirationTime` | timestamp | Actual expiration timestamp |

Password validation rules are defined in the frontend validation system:

- **Common Password**: Minimum 6 characters ([frontend/src/lang/modules/en.ts:249]())
- **Complex Password**: 8-30 characters with letters, numbers, and at least 2 special characters ([frontend/src/lang/modules/en.ts:247-248]())

**Sources:**
- [frontend/src/api/interface/setting.ts:41-42]()
- [frontend/src/lang/modules/en.ts:247-249]()

### Multi-Factor Authentication (MFA)

MFA implements TOTP (Time-based One-Time Password) authentication compatible with standard authenticator apps like Google Authenticator or Authy. The system stores the MFA secret in the `settings` table.

| MFA Setting | Purpose |
|-------------|---------|
| `mfaStatus` | Enable/disable MFA (`enable`/`disable`) |
| `mfaSecret` | Base32-encoded shared secret for TOTP generation |
| `mfaInterval` | Time step interval for TOTP (typically 30s) |

**MFA Workflow:**

1. Admin enables MFA in panel settings
2. System generates `mfaSecret` and displays QR code
3. User scans QR with authenticator app
4. On subsequent logins, system prompts for 6-digit TOTP code
5. System validates code against `mfaSecret` with time tolerance

**Sources:**
- [frontend/src/api/interface/setting.ts:42-44]()
- [frontend/src/lang/modules/en.ts:210-212]()
- [frontend/src/lang/modules/zh.ts:206-209]()

### Passkey Authentication (WebAuthn)

Passkey authentication uses the WebAuthn standard for passwordless login with biometric authentication or hardware security keys. This requires HTTPS and domain binding to be configured.

**Key Messages:**

- `passkeyNotSupported`: "Current browser or environment does not support passkeys, please confirm you have bound the domain name and enabled the panel SSL, and used a trusted certificate when accessing" ([frontend/src/lang/modules/en.ts:221-222]())
- `passkeyFailed`: Handles failed passkey authentication attempts ([frontend/src/lang/modules/en.ts:220]())

**Requirements:**
1. Panel must be accessed via HTTPS
2. Domain name must be bound (`bindDomain` setting)
3. Valid SSL certificate must be configured
4. Browser must support WebAuthn API

**Sources:**
- [frontend/src/lang/modules/en.ts:198-223]()
- [frontend/src/lang/modules/zh.ts:209-212]()

---

## Network Security Layers

```mermaid
graph TB
    Internet["Internet"]
    SafeEntrance["Safe Entrance Check<br/>(securityEntrance setting)"]
    IPWhitelist["IP Whitelist Validation<br/>(allowIPs setting)"]
    DomainBinding["Domain Binding Check<br/>(bindDomain setting)"]
    Firewall["Firewall Rules<br/>(iptables/firewalld)"]
    PanelPort["Panel Port<br/>(serverPort setting)"]
    CoreAPI["Core API Server<br/>(:9999)"]
    
    Internet-->SafeEntrance
    SafeEntrance-->IPWhitelist
    IPWhitelist-->DomainBinding
    DomainBinding-->Firewall
    Firewall-->PanelPort
    PanelPort-->CoreAPI
    
    SafeEntrance-.blocked.->Msg1["notSafe: 'Access Denied'<br/>safeEntrance1-2"]
    IPWhitelist-.blocked.->Msg2["errIP1: 'Authorized IP access enabled'"]
    DomainBinding-.blocked.->Msg3["errDomain1: 'Domain binding enabled'"]
```

**Sources:**
- [frontend/src/lang/modules/en.ts:204-209]()
- [frontend/src/api/interface/setting.ts:30-36]()

### Safe Entrance

The Safe Entrance feature requires users to execute a specific SSH command to retrieve panel login credentials before accessing the web interface. This prevents unauthorized access even if the panel port is exposed.

| Setting | Type | Description |
|---------|------|-------------|
| `securityEntrance` | string | Random URL path segment (e.g., `/abc123def`) |

When Safe Entrance is enabled:
1. Direct panel access returns "Access Denied" message
2. User must SSH into server and run: `1pctl user-info`
3. Command outputs the current entrance URL
4. User navigates to: `https://server-ip:port/<securityEntrance>`

**Error Messages:**
- `notSafe`: "Access Denied" ([frontend/src/lang/modules/en.ts:204]())
- `safeEntrance1`: "The secure login has been enabled in the current environment" ([frontend/src/lang/modules/en.ts:205]())
- `safeEntrance2`: "Enter the following command on the SSH terminal to view the panel entry: 1pctl user-info" ([frontend/src/lang/modules/en.ts:206]())

**Reset Command:**
```bash
1pctl user-info  # View current safe entrance
1pctl reset-entrance  # Reset safe entrance (from errHelper)
```

**Sources:**
- [frontend/src/api/interface/setting.ts:36]()
- [frontend/src/lang/modules/en.ts:204-206]()
- [frontend/src/lang/modules/zh.ts:201-203]()

### IP Whitelist

The IP whitelist restricts panel access to specific IP addresses or CIDR ranges. Multiple IPs can be configured, stored in the `allowIPs` setting.

| Setting | Format | Example |
|---------|--------|---------|
| `allowIPs` | Comma-separated IPs/CIDRs | `192.168.1.100,10.0.0.0/8` |

**Validation:**
- Checked before authentication
- Blocks non-whitelisted IPs immediately
- Returns `errIP1` message: "Authorized IP address access is enabled in the current environment" ([frontend/src/lang/modules/en.ts:207]())

**Reset via SSH:**
```bash
1pctl reset-ips  # Clear IP whitelist restrictions
```

**Sources:**
- [frontend/src/api/interface/setting.ts:34]()
- [frontend/src/lang/modules/en.ts:207-209]()

### Domain Binding

Domain binding restricts panel access to specific domain names, preventing IP-based access attacks.

| Setting | Purpose | Example |
|---------|---------|---------|
| `bindDomain` | Allowed domain(s) | `panel.example.com` |

**Behavior:**
- Validates `Host` header in HTTP requests
- Rejects requests with non-matching domains
- Required for passkey authentication to work
- Error message: `errDomain1` ([frontend/src/lang/modules/en.ts:208]())

**Reset Command:**
```bash
1pctl reset-domain  # Remove domain binding
```

**Sources:**
- [frontend/src/api/interface/setting.ts:35]()
- [frontend/src/lang/modules/en.ts:208-209]()

### Port and Binding Configuration

```mermaid
graph LR
    subgraph "Network Configuration Settings"
        ServerPort["serverPort<br/>(default: 9999)"]
        BindAddress["bindAddress<br/>(listen interface)"]
        IPv6["ipv6<br/>(enable/disable)"]
        SSL["ssl + sslType<br/>(self-signed/trusted)"]
    end
    
    subgraph "Core Server Binding"
        Listener["HTTP(S) Listener"]
    end
    
    ServerPort-->Listener
    BindAddress-->Listener
    IPv6-->Listener
    SSL-->Listener
```

| Setting | Type | Default | Purpose |
|---------|------|---------|---------|
| `serverPort` | integer | 9999 | Core API listen port |
| `bindAddress` | string | `0.0.0.0` | Network interface to bind |
| `ipv6` | `enable`/`disable` | `disable` | Enable IPv6 support |
| `ssl` | `enable`/`disable` | `disable` | Enable HTTPS |
| `sslType` | `self`/`import` | - | Certificate type (self-signed or imported) |

**Sources:**
- [frontend/src/api/interface/setting.ts:29-33]()

---

## API Security

### API Key Authentication

For programmatic access, 1Panel provides API key authentication as an alternative to session-based authentication. API keys can be restricted by IP whitelist and have configurable expiration times.

```mermaid
graph TB
    Client["API Client"]
    Request["HTTP Request<br/>X-API-KEY header"]
    Validation["API Key Validation"]
    IPCheck["IP Whitelist Check<br/>(ipWhiteList)"]
    ExpiryCheck["Validity Check<br/>(apiKeyValidityTime)"]
    Handler["API Handler"]
    
    Client-->Request
    Request-->Validation
    Validation-->IPCheck
    IPCheck-->ExpiryCheck
    ExpiryCheck-->Handler
    
    IPCheck-.blocked.->Error1["403 Forbidden<br/>IP not whitelisted"]
    ExpiryCheck-.expired.->Error2["401 Unauthorized<br/>Key expired"]
```

| API Setting | Type | Purpose |
|-------------|------|---------|
| `apiInterfaceStatus` | `enable`/`disable` | Enable/disable API key authentication |
| `apiKey` | string | The actual API key (Base64 encoded) |
| `ipWhiteList` | string | Comma-separated IPs allowed to use API |
| `apiKeyValidityTime` | integer | Days until key expires |

**API Key Usage:**
```http
GET /api/v2/containers HTTP/1.1
Host: panel.example.com:9999
X-API-KEY: your-api-key-here
```

**Frontend Validation Rules:**
- `authBasicPassword`: "Supports letters, numbers, and common special characters, length 1-72" ([frontend/src/lang/modules/en.ts:279]())

**Sources:**
- [frontend/src/api/interface/setting.ts:65-68]()
- [frontend/src/lang/modules/en.ts:279]()

### Session Management

Sessions are managed with JWT tokens with configurable timeout periods.

| Setting | Type | Default | Purpose |
|---------|------|---------|---------|
| `sessionTimeout` | integer | 86400 | Session timeout in seconds (default: 24h) |

Session tokens are stored in the Pinia global store on the frontend after successful authentication. The token is included in all subsequent API requests via standard HTTP Authorization headers or cookies.

**Sources:**
- [frontend/src/api/interface/setting.ts:14]()

### Captcha Protection

The system includes captcha protection for login attempts to prevent brute-force attacks.

**Captcha Messages:**
- `captchaHelper`: "Captcha" ([frontend/src/lang/modules/en.ts:202]())
- `errorCaptcha`: "Captcha code error!" ([frontend/src/lang/modules/en.ts:203]())

Captcha is displayed after multiple failed login attempts and must be correctly entered before password validation proceeds.

**Sources:**
- [frontend/src/lang/modules/en.ts:202-203]()

---

## Audit and Monitoring

### Operation Logging System

```mermaid
graph TB
    Request["HTTP Request"]
    Middleware["OperationLog Middleware<br/>core/middleware/operation.go"]
    PathCheck["Check if loggable<br/>(excludes GET/search)"]
    SwaggerLookup["Load operation metadata<br/>docs.XLogJson"]
    BodyParse["Parse request body<br/>(multipart or JSON)"]
    DBLookup["BeforeFunctions lookup<br/>(resolve IDs to names)"]
    CreateLog["Create OperationLog record"]
    CoreDB["core.db<br/>operation_logs table"]
    
    Request-->Middleware
    Middleware-->PathCheck
    PathCheck-->SwaggerLookup
    SwaggerLookup-->BodyParse
    BodyParse-->DBLookup
    DBLookup-->CreateLog
    CreateLog-->CoreDB
    
    PathCheck-.skip.->NextHandler["c.Next()"]
```

The operation logging middleware captures all mutating API operations (POST, PUT, DELETE) and stores structured logs in the `operation_logs` table.

**Log Record Structure:**

| Field | Type | Source | Purpose |
|-------|------|--------|---------|
| `source` | string | `loadLogInfo(path)` | Operation source (Core/Agent) |
| `node` | string | `CurrentNode` header | Target node for multi-node setups |
| `ip` | string | `c.ClientIP()` | Client IP address |
| `method` | string | HTTP method | Operation type (post/put/delete) |
| `path` | string | URL path | API endpoint |
| `user_agent` | string | User-Agent header | Client information |

**Operation Metadata from Swagger:**

The middleware uses `docs.XLogJson` to map API paths to human-readable operation descriptions:

```go
type operationJson struct {
    FormatZH         map[string]interface{} // Chinese format strings
    FormatEN         map[string]interface{} // English format strings  
    BodyKeys         []string               // Request body keys to log
    BeforeFunctions  []functionInfo         // DB lookups for context
}
```

**Example Flow:**

1. Request: `POST /api/v2/containers` with `{"name": "my-container"}`
2. Middleware extracts `name` from body based on `BodyKeys`
3. If `BeforeFunctions` defined, performs DB lookup to resolve IDs to names
4. Stores formatted log: "Created container: my-container"

**Sources:**
- [core/middleware/operation.go:28-166]()

### Login Attempt Logging

All login attempts (successful and failed) are logged with timestamps, IP addresses, and outcomes. This provides forensic data for security investigations.

**Login Messages:**
- `loginSuccess`: "Logged in successfully" ([frontend/src/lang/modules/en.ts:157]())
- `errorAuthInfo`: "The user name or password you entered is incorrect" ([frontend/src/lang/modules/en.ts:200]())

**Sources:**
- [frontend/src/lang/modules/en.ts:157-200]()

### Task Execution Logging

Async operations (like app installations, container operations) generate detailed task logs stored separately. Each task has multiple subtasks with progress tracking.

**Log Viewing:**
- `notRecords`: "No execution record is generated for the current task" ([frontend/src/lang/modules/en.ts:163]())

**Sources:**
- [frontend/src/lang/modules/en.ts:163]()

### Resource Change Tracking

The operation log system tracks all resource changes (create/update/delete) across:
- Containers, images, networks, volumes
- Websites, SSL certificates, domains
- Databases and database users
- Applications and installations
- System settings
- Firewall rules

Each logged operation includes:
- User who performed the action
- Timestamp
- Resource type and identifier
- Before/after state (where applicable)
- Success/failure status

**Sources:**
- [core/middleware/operation.go:1-234]()

---

## Data Security

### Encrypted Backups

Backup files can be encrypted using AES encryption with user-provided passwords. The encryption settings are configured per backup account.

**Backup Configuration:**
```mermaid
graph LR
    BackupAccount["Backup Account<br/>(local/S3/OSS/MinIO)"]
    Encryption["AES Encryption<br/>(optional password)"]
    Backup["Encrypted Backup File<br/>(.tar.gz.enc)"]
    
    BackupAccount-->Encryption
    Encryption-->Backup
```

**Sources:**
- [frontend/src/lang/modules/en.ts:181-182]()

### SSL/TLS Configuration

The panel supports SSL/TLS for encrypted communication:

| SSL Setting | Values | Purpose |
|-------------|--------|---------|
| `ssl` | `enable`/`disable` | Enable HTTPS |
| `sslType` | `self`/`import` | Self-signed or imported certificate |

**SSL Certificate Types:**
1. **Self-signed**: Automatically generated by panel
2. **Imported**: User-provided trusted certificate

**Sources:**
- [frontend/src/api/interface/setting.ts:32-33]()

### Secret Management

Sensitive data like passwords and API keys are:
1. Hashed with bcrypt before storage (passwords)
2. Base64 encoded for transmission (secrets)
3. Never logged in operation logs
4. Masked in UI by default with show/hide toggle

**Password Display:**
- `passwordHelper`: "Cannot obtain, click to modify" ([frontend/src/lang/modules/en.ts:542]())

**Sources:**
- [frontend/src/lang/modules/en.ts:542]()

---

## License and Node Security

### License Binding System

```mermaid
graph TB
    MasterNode["Master Node<br/>(License Server)"]
    License["License Record<br/>core.db"]
    Binding["License Binding<br/>(licenseID + nodeID)"]
    AgentNode["Agent Node"]
    Features["Feature Gates<br/>(Pro/Community)"]
    SMS["SMS Quota Tracking"]
    
    MasterNode-->License
    License-->Binding
    Binding-->AgentNode
    Binding-->Features
    License-->SMS
```

**License API Endpoints:**

| Endpoint | Purpose |
|----------|---------|
| `POST /core/licenses/upload` | Upload new license ([frontend/src/api/modules/setting.ts:12]()) |
| `POST /core/licenses/update` | Update existing license ([frontend/src/api/modules/setting.ts:14]()) |
| `POST /core/licenses/bind` | Bind license to nodes ([frontend/src/api/modules/setting.ts:31-32]()) |
| `POST /core/licenses/unbind` | Unbind license from nodes ([frontend/src/api/modules/setting.ts:34-35]()) |
| `GET /core/licenses/status` | Check license status ([frontend/src/api/modules/setting.ts:22-26]()) |

**License Binding:**
```typescript
interface LicenseBind {
    licenseID: number;
    nodeIDs: Array<number>;
}
```

License binding occurs at the node level, enabling per-node feature gating. When a license is bound:
1. Master node validates license with license server
2. Node ID is associated with license record
3. Features are unlocked on that specific node
4. SMS quota is allocated (if applicable)

**SMS Quota:**
- Used for notification services
- Tracked per license
- API: `GET /core/licenses/sms/info` ([frontend/src/api/modules/setting.ts:54-56]())

**Sources:**
- [frontend/src/api/modules/setting.ts:10-56]()
- [frontend/src/api/interface/setting.ts:93-120]()

### Multi-Node Access Control

In multi-node deployments, the `CurrentNode` header determines which node processes the request:

```http
POST /api/v2/containers HTTP/1.1
CurrentNode: node-02
Authorization: Bearer <jwt-token>
```

The operation log middleware extracts this header to track which node performed each operation ([core/middleware/operation.go:38-40]()).

**Sources:**
- [core/middleware/operation.go:38-42]()

---

## Database Security

### SQLite Configuration

Both `core.db` and `agent.db` use SQLite with specific security configurations:

**Connection Settings:**

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `MaxOpenConns` | 4 | Limit concurrent connections |
| `MaxIdleConns` | 1 | Minimize idle connections |
| `ConnMaxIdleTime` | 15 min | Close idle connections quickly |
| `ConnMaxLifetime` | 1 hour | Rotate connections regularly |

These settings minimize the attack surface by limiting database connection persistence and concurrency.

**Database Initialization:**
```go
func LoadDBConnByPath(fullPath, dbName string) *gorm.DB {
    // Creates directory and file if not exist
    // Opens with GORM and SQLite driver
    // Configures connection pool
    // Returns *gorm.DB instance
}
```

**Sources:**
- [agent/utils/common/sqlite.go:16-33]()
- [core/utils/common/sqlite.go:15-32]()
- [agent/utils/common/sqlite.go:62-78]()

### Sensitive Data Handling

The middleware filters sensitive keys from operation logs:

```go
sensitiveKeys := []string{"password", "passwd", "secret", "token", "api_key"}
// These keys are never logged in operation_logs
```

This prevents accidental exposure of credentials in audit trails.

**Sources:**
- [core/middleware/operation.go:64-80]()

---

## Security Best Practices

### Recommended Configuration

For production deployments, the following security settings should be enabled:

| Feature | Setting | Recommendation |
|---------|---------|----------------|
| Safe Entrance | `securityEntrance` | **Enable** - Prevents direct access |
| IP Whitelist | `allowIPs` | **Enable** - Restrict to known IPs |
| Domain Binding | `bindDomain` | **Enable** - Prevent IP-based attacks |
| SSL/TLS | `ssl=enable` | **Enable** - Encrypt all traffic |
| MFA | `mfaStatus=enable` | **Enable** - Add second factor |
| Password Complexity | `complexityVerification=enable` | **Enable** - Enforce strong passwords |
| API Interface | `apiInterfaceStatus` | **Disable** unless needed |
| Session Timeout | `sessionTimeout` | **Reduce** to 3600-7200s for high-security |

### Security Headers

The system should configure appropriate security headers (CSP, HSTS, X-Frame-Options) to protect against common web attacks. These are typically configured in the Gin router middleware.

### Regular Security Audits

Administrators should regularly review:
1. Operation logs for suspicious activity ([core/middleware/operation.go]())
2. Login attempt logs for brute-force patterns
3. License bindings and node status
4. API key usage and IP whitelist entries
5. Firewall rule changes

**Sources:**
- [frontend/src/api/interface/setting.ts:4-68]()
- [core/middleware/operation.go:28-166]()

---

# Page: Internationalization and Localization

# Internationalization and Localization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [frontend/src/lang/modules/en.ts](frontend/src/lang/modules/en.ts)
- [frontend/src/lang/modules/es-es.ts](frontend/src/lang/modules/es-es.ts)
- [frontend/src/lang/modules/ja.ts](frontend/src/lang/modules/ja.ts)
- [frontend/src/lang/modules/ko.ts](frontend/src/lang/modules/ko.ts)
- [frontend/src/lang/modules/ms.ts](frontend/src/lang/modules/ms.ts)
- [frontend/src/lang/modules/pt-br.ts](frontend/src/lang/modules/pt-br.ts)
- [frontend/src/lang/modules/ru.ts](frontend/src/lang/modules/ru.ts)
- [frontend/src/lang/modules/tr.ts](frontend/src/lang/modules/tr.ts)
- [frontend/src/lang/modules/zh-Hant.ts](frontend/src/lang/modules/zh-Hant.ts)
- [frontend/src/lang/modules/zh.ts](frontend/src/lang/modules/zh.ts)

</details>



**Purpose**: This document describes the internationalization (i18n) and localization (l10n) system in 1Panel, including the supported languages, translation file structure, message organization, and how translations are integrated into the frontend application.

**Scope**: Covers the frontend translation system, message structure, supported languages, and translation key organization. For backend configuration of panel settings including language selection, see [Settings and Configuration Management](#5).

---

## Overview

1Panel provides a comprehensive internationalization system supporting **10 languages** across its Vue.js frontend. The i18n implementation uses `vue-i18n` to provide runtime translation switching and a hierarchical message structure that mirrors the application's feature organization.

The translation system covers all user-facing text including:
- UI components (buttons, tables, forms, status messages)
- Navigation menus and page titles
- Feature-specific terminology (containers, databases, websites, AI tools)
- Validation messages and error text
- Help text and tooltips

**Sources**: [frontend/src/lang/modules/zh.ts:1-10](), [frontend/src/lang/modules/en.ts:1-10]()

---

## Supported Languages

1Panel supports the following 10 languages with complete translation coverage:

| Language | Code | File | Import Source |
|----------|------|------|---------------|
| Chinese (Simplified) | `zh` | `zh.ts` | `fit2cloud-ui-plus/src/locale/lang/zh-cn` |
| English | `en` | `en.ts` | `fit2cloud-ui-plus/src/locale/lang/en` |
| Chinese (Traditional) | `zh-Hant` | `zh-Hant.ts` | `fit2cloud-ui-plus/src/locale/lang/zh-tw` |
| Japanese | `ja` | `ja.ts` | `fit2cloud-ui-plus/src/locale/lang/ja` |
| Russian | `ru` | `ru.ts` | `fit2cloud-ui-plus/src/locale/lang/ru` |
| Portuguese (Brazilian) | `pt-br` | `pt-br.ts` | `fit2cloud-ui-plus/src/locale/lang/pt-br` |
| Korean | `ko` | `ko.ts` | `fit2cloud-ui-plus/src/locale/lang/en` |
| Turkish | `tr` | `tr.ts` | `fit2cloud-ui-plus/src/locale/lang/en` |
| Spanish (Spanish) | `es-es` | `es-es.ts` | `fit2cloud-ui-plus/src/locale/lang/en` |
| Malay | `ms` | `ms.ts` | `fit2cloud-ui-plus/src/locale/lang/ms` |

Each language file is located at `frontend/src/lang/modules/{language}.ts` and exports a `message` object containing all translations for that language. The files also import locale configurations from the `fit2cloud-ui-plus` component library to ensure consistency across UI components.

**Sources**: [frontend/src/lang/modules/zh.ts:1-2](), [frontend/src/lang/modules/en.ts:1-2](), [frontend/src/lang/modules/ja.ts:1-2]()

---

## Translation File Structure

### File Organization

```mermaid
graph TB
    LangRoot["frontend/src/lang/modules/"]
    
    LangRoot --> ZhFile["zh.ts<br/>(Chinese Simplified)"]
    LangRoot --> EnFile["en.ts<br/>(English)"]
    LangRoot --> ZhHantFile["zh-Hant.ts<br/>(Traditional Chinese)"]
    LangRoot --> JaFile["ja.ts<br/>(Japanese)"]
    LangRoot --> RuFile["ru.ts<br/>(Russian)"]
    LangRoot --> PtFile["pt-br.ts<br/>(Portuguese)"]
    LangRoot --> KoFile["ko.ts<br/>(Korean)"]
    LangRoot --> TrFile["tr.ts<br/>(Turkish)"]
    LangRoot --> EsFile["es-es.ts<br/>(Spanish)"]
    LangRoot --> MsFile["ms.ts<br/>(Malay)"]
    
    ZhFile --> MsgObj["message object"]
    EnFile --> MsgObj
    ZhHantFile --> MsgObj
    JaFile --> MsgObj
    RuFile --> MsgObj
    PtFile --> MsgObj
    KoFile --> MsgObj
    TrFile --> MsgObj
    EsFile --> MsgObj
    MsFile --> MsgObj
    
    MsgObj --> Commons["commons"]
    MsgObj --> Menu["menu"]
    MsgObj --> Features["feature modules<br/>(database, container, etc.)"]
```

**Sources**: [frontend/src/lang/modules/zh.ts:3-361](), [frontend/src/lang/modules/en.ts:3-374]()

### Message Object Structure

Each language file exports a `message` object with the following structure:

```typescript
const message = {
    commons: {
        button: { /* button labels */ },
        operate: { /* operation verbs */ },
        table: { /* table UI text */ },
        status: { /* status values */ },
        msg: { /* common messages */ },
        // ...
    },
    menu: { /* navigation menu labels */ },
    home: { /* dashboard page */ },
    database: { /* database management */ },
    container: { /* container management */ },
    website: { /* website management */ },
    aiTools: { /* AI tools module */ },
    // ... feature-specific namespaces
}
```

**Sources**: [frontend/src/lang/modules/zh.ts:3-361](), [frontend/src/lang/modules/en.ts:3-374]()

---

## Message Hierarchy

### Commons Namespace

The `commons` namespace contains reusable UI elements shared across the entire application:

```mermaid
graph LR
    Commons["commons"]
    
    Commons --> Button["button<br/>(create, save, delete, etc.)"]
    Commons --> Operate["operate<br/>(start, stop, restart, etc.)"]
    Commons --> Search["search<br/>(timeStart, timeEnd, etc.)"]
    Commons --> Table["table<br/>(name, type, status, etc.)"]
    Commons --> LoadingText["loadingText<br/>(Upgrading, Restarting, etc.)"]
    Commons --> Msg["msg<br/>(success, error messages)"]
    Commons --> Login["login<br/>(username, password, etc.)"]
    Commons --> Rule["rule<br/>(validation messages)"]
    Commons --> Status["status<br/>(running, stopped, etc.)"]
    Commons --> Units["units<br/>(second, minute, hour, etc.)"]
    Commons --> Log["log<br/>(noLog)"]
```

**Sources**: [frontend/src/lang/modules/zh.ts:4-361](), [frontend/src/lang/modules/en.ts:4-374]()

#### Button Actions

Common button labels defined in `commons.button`:

| Key | English | Chinese | Usage Context |
|-----|---------|---------|---------------|
| `create` | Create | 创建 | Resource creation |
| `save` | Save | 保存 | Form submission |
| `delete` | Delete | 删除 | Resource deletion |
| `edit` | Edit | 编辑 | Resource modification |
| `enable` | Enable | 启用 | Activation |
| `disable` | Disable | 停用 | Deactivation |
| `backup` | Backup | 备份 | Backup operations |
| `recover` | Recover | 恢复 | Restore operations |
| `upgrade` | Upgrade | 升级 | Version upgrades |
| `install` | Install | 安装 | App installation |

**Sources**: [frontend/src/lang/modules/zh.ts:11-90](), [frontend/src/lang/modules/en.ts:11-90]()

#### Status Values

Status translations in `commons.status`:

| Key | English | Chinese | Context |
|-----|---------|---------|---------|
| `running` | Running | 已启动 | Active state |
| `stopped` | Stopped | 已停止 | Inactive state |
| `installing` | Installing | 安装中 | Installation in progress |
| `upgrading` | Upgrading | 升级中 | Upgrade in progress |
| `failed` | Failed | 失败 | Error state |
| `success` | Success | 成功 | Successful completion |
| `healthy` | Normal | 正常 | Health check passed |
| `unhealthy` | Unhealthy | 异常 | Health check failed |

**Sources**: [frontend/src/lang/modules/zh.ts:281-340](), [frontend/src/lang/modules/en.ts:294-352]()

### Menu Namespace

The `menu` namespace defines all navigation menu labels:

```mermaid
graph TB
    Menu["menu"]
    
    Menu --> Home["home: 'Overview'"]
    Menu --> Apps["apps: 'App Store'"]
    Menu --> Website["website: 'Website'"]
    Menu --> Database["database: 'Database'"]
    Menu --> Container["container: 'Container'"]
    Menu --> AITools["aiTools: 'AI'"]
    Menu --> MCP["mcp: 'MCP'"]
    Menu --> Cronjob["cronjob: 'Cron Job'"]
    Menu --> Files["files: 'File Browser'"]
    Menu --> Terminal["terminal: 'Terminal'"]
    Menu --> Settings["settings: 'Settings'"]
    Menu --> Logs["logs: 'Log'"]
```

**Sources**: [frontend/src/lang/modules/en.ts:375-407](), [frontend/src/lang/modules/zh.ts:362-393]()

---

## Feature-Specific Namespaces

### Database Module

The `database` namespace contains all database management translations:

```mermaid
graph TB
    Database["database"]
    
    Database --> Operations["Operations<br/>(create, manage, delete)"]
    Database --> Connection["Connection Info<br/>(rootPassword, serviceName)"]
    Database --> Backup["Backup<br/>(backupList, loadBackup)"]
    Database --> Remote["Remote DB<br/>(remoteDB, createRemoteDB)"]
    Database --> Performance["Performance<br/>(currentStatus, performanceParam)"]
    Database --> SlowLog["Slow Log<br/>(slowLog, longQueryTime)"]
    Database --> Redis["Redis Specific<br/>(timeout, maxclients)"]
    Database --> PostgreSQL["PostgreSQL Specific<br/>(pgSuperUser, pgBindHelper)"]
```

**Sources**: [frontend/src/lang/modules/en.ts:491-653](), [frontend/src/lang/modules/zh.ts:477-653]()

### Container Module

The `container` namespace provides Docker container management translations:

```mermaid
graph TB
    Container["container"]
    
    Container --> Lifecycle["Lifecycle<br/>(create, start, stop, restart)"]
    Container --> Image["Image Mgmt<br/>(imagePull, imagePush, imageBuild)"]
    Container --> Network["Network<br/>(createNetwork, driver, subnet)"]
    Container --> Volume["Volume<br/>(createVolume, mountpoint)"]
    Container --> Compose["Compose<br/>(createCompose, composeFile)"]
    Container --> Repo["Registry<br/>(createRepo, imageRepo)"]
    Container --> Settings["Settings<br/>(daemonJsonPath, mirrors)"]
```

**Sources**: [frontend/src/lang/modules/en.ts:802-1095](), [frontend/src/lang/modules/zh.ts:801-1094]()

### AI Tools Module

The `aiTools` namespace covers AI infrastructure management:

```mermaid
graph TB
    AITools["aiTools"]
    
    AITools --> Agents["agents<br/>(createAgent, account, provider)"]
    AITools --> Model["model<br/>(create, ollama_doc)"]
    AITools --> Proxy["proxy<br/>(proxyHelper, whiteListHelper)"]
    AITools --> GPU["gpu<br/>(process, temperature, memoryUsage)"]
    AITools --> MCP["mcp<br/>(server, environment, transport)"]
    AITools --> TensorRT["tensorRT<br/>(modelDir, commandHelper)"]
```

**Sources**: [frontend/src/lang/modules/en.ts:654-800](), [frontend/src/lang/modules/zh.ts:654-800]()

### Website Module

The `website` namespace contains web server and SSL management:

```mermaid
graph TB
    Website["website"]
    
    Website --> Types["Website Types<br/>(static, runtime, proxy, etc.)"]
    Website --> SSL["SSL/ACME<br/>(acme, dnsAccount, provider)"]
    Website --> Domain["Domain<br/>(addDomain, defaultServer)"]
    Website --> Nginx["Nginx Config<br/>(rewriteRule, proxyPass)"]
    Website --> Runtime["Runtime Env<br/>(php, node, python)"]
    Website --> WAF["WAF/Security<br/>(antiLeech, limitConn)"]
```

**Sources**: [frontend/src/lang/modules/en.ts:1096-1800](), [frontend/src/lang/modules/zh.ts:1095-1800]()

---

## Translation Key Patterns

### Validation Rules

The `commons.rule` namespace defines validation error messages with consistent patterns:

```mermaid
graph LR
    Rule["commons.rule"]
    
    Rule --> Required["requiredInput<br/>requiredSelect"]
    Rule --> Format["email<br/>ip<br/>domain<br/>port"]
    Rule --> Length["commonName<br/>userName<br/>simpleName"]
    Rule --> Complexity["complexityPassword<br/>commonPassword"]
    Rule --> Pattern["imageName<br/>containerName<br/>volumeName"]
    Rule --> Illegal["illegalChar<br/>illegalInput"]
```

**Pattern Structure**:
- **Input validation**: `requiredInput`, `requiredSelect`
- **Format validation**: `{type}` (e.g., `email`, `ip`, `domain`)
- **Length validation**: `{scope}Name` (e.g., `commonName`, `userName`)
- **Pattern validation**: `{resource}Name` (e.g., `imageName`, `containerName`)

**Sources**: [frontend/src/lang/modules/en.ts:225-283](), [frontend/src/lang/modules/zh.ts:221-270]()

### Helper Text Pattern

Helper text keys follow the pattern `{feature}Helper` or `{action}Helper`:

| Key Pattern | Example | Usage |
|-------------|---------|-------|
| `{feature}Helper` | `localhostHelper` | Explains feature behavior |
| `{action}Helper` | `backupHelper` | Confirms action before execution |
| `{setting}Helper` | `portHelper` | Describes configuration option |

**Sources**: [frontend/src/lang/modules/en.ts:494-653](), [frontend/src/lang/modules/zh.ts:477-653]()

### Operation Confirmation Messages

Confirmation messages in `commons.msg`:

```typescript
// Pattern: {action} + 'Helper'
backupHelper: 'The current operation will back up {0}. Do you want to proceed?'
recoverHelper: 'Restoring from {0} file. This operation is irreversible.'
operatorHelper: 'The operation "{1}" will be performed on "{0}"...'
```

Uses placeholder `{0}`, `{1}` for dynamic values.

**Sources**: [frontend/src/lang/modules/en.ts:151-194](), [frontend/src/lang/modules/zh.ts:148-191]()

---

## Pluralization and Formatting

### Time Units with Pluralization

The `commons.units` namespace supports pluralization for time units:

```typescript
// English format: 'singular | singular | plural'
second: ' second | second | seconds'
minute: 'minute | minute | minutes'
hour: 'hour | hour | hours'
day: 'day | day | days'
```

This format allows `vue-i18n` to automatically select the correct form based on count.

**Sources**: [frontend/src/lang/modules/en.ts:355-370](), [frontend/src/lang/modules/zh.ts:341-357]()

### Dynamic Message Formatting

Messages use numbered placeholders for dynamic content:

```typescript
// Table total count
total: 'Total {0}'

// Number range validation
numberRange: 'This field must be a number between {0} and {1}.'

// Operation confirmation
operatorHelper: 'The operation "{1}" will be performed on "{0}"...'
```

**Sources**: [frontend/src/lang/modules/en.ts:112](), [frontend/src/lang/modules/zh.ts:112]()

---

## Special Characters and Formatting

### Colon Character

Each language defines its colon character to match local conventions:

| Language | Colon | Example Usage |
|----------|-------|---------------|
| Chinese | `'：'` (full-width) | Used after labels |
| English | `': '` (with space) | Used after labels |
| Japanese | `':'` | Used after labels |

**Sources**: [frontend/src/lang/modules/zh.ts:10](), [frontend/src/lang/modules/en.ts:7](), [frontend/src/lang/modules/ja.ts:7]()

### Semicolon in Units

Used for separating multiple values:

```typescript
units: {
    semicolon: '；'  // Chinese uses full-width semicolon
}
```

**Sources**: [frontend/src/lang/modules/zh.ts:356](), [frontend/src/lang/modules/en.ts:369]()

---

## Authentication and Security

### Login Page Translations

The `commons.login` namespace includes authentication-specific text:

```mermaid
graph TB
    Login["commons.login"]
    
    Login --> Basic["Basic Auth<br/>(username, password, welcome)"]
    Login --> MFA["MFA<br/>(mfaTitle, mfaCode, codeInput)"]
    Login --> Passkey["Passkey<br/>(passkey, passkeyFailed)"]
    Login --> SafeEntrance["Safe Entrance<br/>(safeEntrance1, safeEntrance2)"]
    Login --> IPRestriction["IP Restriction<br/>(errIP1, errHelper)"]
    Login --> DomainBind["Domain Binding<br/>(errDomain1)"]
    Login --> Errors["Error Messages<br/>(errorAuthInfo, errorMfaInfo)"]
```

**Key Features**:
- **Passkey support**: `passkey`, `passkeyFailed`, `passkeyNotSupported`, `passkeyToPassword`
- **MFA authentication**: `mfaTitle`, `mfaCode`, `codeInput`
- **Safe entrance**: `safeEntrance1`, `safeEntrance2` (explains SSH command requirement)
- **IP/Domain restrictions**: `errIP1`, `errDomain1`, `errHelper`

**Sources**: [frontend/src/lang/modules/en.ts:195-224](), [frontend/src/lang/modules/zh.ts:192-220]()

---

## Context-Specific Translations

### Loading States

The `commons.loadingText` namespace provides system operation status messages:

```typescript
loadingText: {
    Upgrading: 'System upgrade, please wait...',
    Restarting: 'System restart, please wait...',
    Recovering: 'Recovering from snapshot, please wait...',
    Rollbacking: 'Rollbacking from snapshot, please wait...'
}
```

These are displayed during long-running system operations.

**Sources**: [frontend/src/lang/modules/en.ts:145-150](), [frontend/src/lang/modules/zh.ts:142-147]()

### Service-Specific Messages

Each major feature module includes specialized terminology:

**Container Module Example**:
```typescript
container: {
    privileged: 'Privileged mode',
    privilegedHelper: 'Allows container to perform privileged operations...',
    autoRemove: 'Auto-remove container on exit',
    cpuShare: 'CPU weight',
    cpuShareHelper: 'Container default share is 1024 CPU...'
}
```

**Database Module Example**:
```typescript
database: {
    pgSuperUser: 'Super User',
    pgBindHelper: 'This operation is used to create a new user...',
    localhostHelper: 'Configuring database permissions as "localhost"...'
}
```

**Sources**: [frontend/src/lang/modules/en.ts:893-896](), [frontend/src/lang/modules/en.ts:538-540]()

---

## Translation Workflow Diagram

```mermaid
graph TB
    Source["Source Language File<br/>(e.g., zh.ts)"]
    
    Source --> Export["Export message object"]
    Export --> I18nLib["vue-i18n library"]
    I18nLib --> Runtime["Runtime translation"]
    
    Runtime --> Component["Vue Component<br/>$t('commons.button.create')"]
    Runtime --> Directive["v-t directive"]
    Runtime --> Computed["Computed properties"]
    
    Component --> Rendered["Rendered UI"]
    Directive --> Rendered
    Computed --> Rendered
    
    UserAction["User switches language"] --> I18nLib
    
    LocalStorage["LocalStorage<br/>(selected language)"] --> I18nLib
```

**Sources**: [frontend/src/lang/modules/zh.ts:1-10](), [frontend/src/lang/modules/en.ts:1-10]()

---

## Translation Coverage by Module

### Complete Module List

The following table shows the primary namespaces and their translation key counts (approximate, based on English file):

| Namespace | Key Count | Primary Features |
|-----------|-----------|------------------|
| `commons` | ~500 | Buttons, tables, status, validation, messages |
| `menu` | ~40 | Navigation menu labels |
| `home` | ~80 | Dashboard, system info, quick actions |
| `database` | ~180 | MySQL, PostgreSQL, Redis management |
| `container` | ~300 | Docker containers, images, networks, volumes |
| `website` | ~700+ | Nginx, SSL, domains, runtime environments |
| `aiTools` | ~150 | AI agents, models, GPU monitoring, MCP |
| `cronjob` | ~100 | Scheduled tasks, backup jobs |
| `app` | ~200 | App store, installation, updates |
| `terminal` | ~60 | Terminal sessions, SSH |
| `firewall` | ~100 | Firewall rules, port forwarding |
| `file` | ~180 | File browser, editor, operations |
| `settings` | ~300+ | Panel settings, security, backup |
| `logs` | ~80 | Audit logs, operation logs |
| `toolbox` | ~120 | Device management, FTP, fail2ban |

**Sources**: [frontend/src/lang/modules/en.ts:1-3000]()

---

## Implementation Details

### Vue-i18n Integration

Each language file imports the corresponding `fit2cloud-ui-plus` locale:

```typescript
// Chinese
import fit2cloudZhLocale from 'fit2cloud-ui-plus/src/locale/lang/zh-cn';

// English
import fit2cloudEnLocale from 'fit2cloud-ui-plus/src/locale/lang/en';
```

This ensures that UI component library elements (Element Plus wrapper) are also translated.

**Sources**: [frontend/src/lang/modules/zh.ts:1](), [frontend/src/lang/modules/en.ts:1]()

### Message Export

Each file exports a `message` constant:

```typescript
const message = {
    commons: { /* ... */ },
    menu: { /* ... */ },
    // ... feature namespaces
};

export default message;
```

This is consumed by the i18n configuration to register translations for each language.

**Sources**: [frontend/src/lang/modules/zh.ts:3-end]()

---

## Best Practices and Conventions

### Key Naming Conventions

1. **camelCase for keys**: All translation keys use camelCase: `createDatabase`, `rootPassword`
2. **Helper suffix**: Explanatory text uses `Helper` suffix: `localhostHelper`, `portHelper`
3. **Verb-first for actions**: Action keys start with verbs: `create`, `delete`, `backup`
4. **Noun-first for resources**: Resource keys start with nouns: `containerName`, `imageName`

### Organizational Patterns

1. **Hierarchical grouping**: Related translations are nested under common parents
2. **Feature isolation**: Each major feature has its own top-level namespace
3. **Common reuse**: Frequently used terms (button labels, status values) are centralized in `commons`
4. **Context preservation**: Similar terms in different contexts have different keys

### Translation Consistency

1. **Placeholder syntax**: Use `{0}`, `{1}`, etc. for dynamic values
2. **Punctuation**: Include trailing punctuation in the translation, not in code
3. **Case sensitivity**: Maintain consistent capitalization within each language
4. **Length consideration**: Some languages (German, Russian) may have longer text

**Sources**: [frontend/src/lang/modules/en.ts:1-3000](), [frontend/src/lang/modules/zh.ts:1-3000]()

---

## Summary

The 1Panel internationalization system provides comprehensive translation coverage across 10 languages with over 2,000 translation keys per language. The hierarchical message structure aligns with the application's feature organization, making translations easy to locate and maintain. The use of consistent naming conventions, placeholder syntax, and the `vue-i18n` library ensures a robust and maintainable i18n implementation that supports the system's global user base.

---

# Page: Settings and Configuration Management

# Settings and Configuration Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [frontend/src/api/interface/setting.ts](frontend/src/api/interface/setting.ts)
- [frontend/src/api/modules/setting.ts](frontend/src/api/modules/setting.ts)

</details>



## Purpose and Scope

This document covers the settings and configuration management system in 1Panel, which controls system-wide behavior, security parameters, network configuration, license management, and operational settings. The settings system operates at multiple levels: Core server settings (authentication, SSL, proxy, licenses) and Agent server settings (terminal configuration, snapshot behavior, monitoring parameters).

For authentication mechanisms themselves (password validation, MFA verification, session management), see [Authentication and Security](#3). For internationalization settings and language configuration, see [Internationalization and Localization](#4). For multi-node architecture and node management, see [Multi-Node Architecture](#2.2).

---

## Settings Architecture Overview

The settings system follows a two-tier architecture where the Core API server manages global configuration and the Agent API server manages operational parameters. Settings are persisted in SQLite databases (`core.db` for Core settings, `agent.db` for Agent settings) and exposed via REST endpoints.

```mermaid
graph TB
    subgraph "Frontend Layer"
        SettingsUI["Settings UI Components"]
        SettingsStore["Global Store<br/>(currentNode, user)"]
        SettingsAPI["Settings API Client<br/>frontend/src/api/modules/setting.ts"]
    end
    
    subgraph "Core API Server :9999"
        CoreSettingsHandler["Settings Handlers"]
        CoreDB[("core.db<br/>settings table")]
        LicenseTable[("xpack.db<br/>licenses table")]
        
        subgraph "Core Settings Domains"
            GeneralSettings["General Settings<br/>SettingInfo (69 fields)"]
            TerminalSettings["Terminal Config<br/>TerminalInfo"]
            ProxySettings["Proxy Config<br/>ProxyUpdate"]
            SSLSettings["SSL Config<br/>SSLUpdate, SSLInfo"]
            AuthSettings["Auth Settings<br/>MFA, Passkey"]
            APISettings["API Key Config<br/>ApiConfig"]
            LicenseSettings["License Management<br/>License, LicenseBind"]
            UpgradeSettings["Upgrade Config<br/>UpgradeInfo"]
        end
    end
    
    subgraph "Agent API Server :10000"
        AgentSettingsHandler["Settings Handlers"]
        AgentDB[("agent.db<br/>settings table")]
        
        subgraph "Agent Settings Domains"
            BaseConfig["Base Configuration<br/>basedir, daemonjson"]
            SnapshotConfig["Snapshot Config<br/>SnapshotCreate, SnapshotInfo"]
            MonitorConfig["Monitor Settings<br/>interval, retention"]
        end
    end
    
    SettingsUI --> SettingsStore
    SettingsUI --> SettingsAPI
    
    SettingsAPI -->|"/core/settings/*"| CoreSettingsHandler
    SettingsAPI -->|"/settings/*"| AgentSettingsHandler
    
    CoreSettingsHandler --> CoreDB
    CoreSettingsHandler --> LicenseTable
    CoreSettingsHandler --> GeneralSettings
    CoreSettingsHandler --> TerminalSettings
    CoreSettingsHandler --> ProxySettings
    CoreSettingsHandler --> SSLSettings
    CoreSettingsHandler --> AuthSettings
    CoreSettingsHandler --> APISettings
    CoreSettingsHandler --> LicenseSettings
    CoreSettingsHandler --> UpgradeSettings
    
    AgentSettingsHandler --> AgentDB
    AgentSettingsHandler --> BaseConfig
    AgentSettingsHandler --> SnapshotConfig
    AgentSettingsHandler --> MonitorConfig
```

**Sources:** [frontend/src/api/modules/setting.ts:1-223](), [frontend/src/api/interface/setting.ts:1-312]()

---

## Core Settings Structure

The `SettingInfo` interface defines 69 distinct configuration parameters organized into functional categories. All settings are retrieved via `POST /core/settings/search` and updated via `POST /core/settings/update` with key-value pairs.

### SettingInfo Schema

| Category | Fields | Purpose |
|----------|--------|---------|
| **User Credentials** | `userName`, `password`, `email` | Administrator account information |
| **System Identity** | `systemIP`, `systemVersion`, `panelName` | System identification and branding |
| **Time Configuration** | `sessionTimeout`, `localTime`, `timeZone`, `ntpSite` | Time synchronization and session management |
| **UI Preferences** | `theme`, `menuTabs`, `language`, `hideMenu`, `dashboardMemoVisible` | Interface customization |
| **Network Settings** | `serverPort`, `ipv6`, `bindAddress`, `ssl`, `sslType`, `allowIPs`, `bindDomain` | Network binding and access control |
| **Security Parameters** | `securityEntrance`, `expirationDays`, `complexityVerification`, `mfaStatus`, `mfaSecret` | Authentication and access protection |
| **Monitoring** | `monitorStatus`, `monitorInterval`, `monitorStoreDays` | System monitoring configuration |
| **Proxy Configuration** | `proxyUrl`, `proxyType`, `proxyPort`, `proxyUser`, `proxyPasswd` | Outbound proxy settings |
| **API Access** | `apiInterfaceStatus`, `apiKey`, `ipWhiteList`, `apiKeyValidityTime` | Programmatic API access control |
| **Operational** | `dockerSockPath`, `developerMode`, `defaultIO`, `defaultNetwork`, `snapshotIgnore` | Runtime behavior configuration |

**Core API Endpoints:**

```typescript
// Retrieve all settings
POST /core/settings/search
Response: SettingInfo

// Retrieve single setting by key
POST /core/settings/by
Body: { key: string }
Response: string

// Update setting
POST /core/settings/update
Body: { key: string, value: string }

// Check system availability
GET /core/settings/search/available
```

**Sources:** [frontend/src/api/interface/setting.ts:4-69](), [frontend/src/api/modules/setting.ts:83-100]()

---

## Terminal Configuration

The `TerminalInfo` interface controls the web-based terminal appearance and behavior. This configuration applies to all terminal sessions across file management, container shells, and SSH access.

### Terminal Parameters

```typescript
interface TerminalInfo {
    lineHeight: string;        // Line spacing (e.g., "1.2")
    letterSpacing: string;     // Character spacing (e.g., "0.5px")
    fontSize: string;          // Font size (e.g., "14px")
    fontFamily: string;        // Monospace font name
    cursorBlink: string;       // "enable" or "disable"
    cursorStyle: string;       // "bar", "block", or "underline"
    scrollback: string;        // History buffer size (lines)
    scrollSensitivity: string; // Scroll wheel sensitivity
}
```

**Terminal Settings Endpoints:**

```typescript
// Get terminal configuration
POST /core/settings/terminal/search
Response: TerminalInfo

// Update terminal configuration
POST /core/settings/terminal/update
Body: TerminalInfo
```

**Sources:** [frontend/src/api/interface/setting.ts:70-79](), [frontend/src/api/modules/setting.ts:89-94]()

---

## Network and Security Settings

Network configuration controls panel accessibility, domain binding, IP restrictions, and the Safe Entrance feature.

### Access Control Hierarchy

```mermaid
graph LR
    Request["Incoming Request"]
    
    SafeEntrance{"Safe Entrance<br/>Path Match?"}
    DomainCheck{"Domain Binding<br/>Allowed?"}
    IPCheck{"IP Whitelist<br/>Allowed?"}
    SSLCheck{"SSL Required?"}
    Allowed["Request Allowed"]
    Denied["403 Forbidden"]
    
    Request --> SafeEntrance
    SafeEntrance -->|"No entrance set"| DomainCheck
    SafeEntrance -->|"Entrance matches"| DomainCheck
    SafeEntrance -->|"Entrance mismatch"| Denied
    
    DomainCheck -->|"No domain binding"| IPCheck
    DomainCheck -->|"Domain matches"| IPCheck
    DomainCheck -->|"Domain mismatch"| Denied
    
    IPCheck -->|"No IP restriction"| SSLCheck
    IPCheck -->|"IP allowed"| SSLCheck
    IPCheck -->|"IP blocked"| Denied
    
    SSLCheck -->|"SSL disabled"| Allowed
    SSLCheck -->|"HTTPS request"| Allowed
    SSLCheck -->|"HTTP blocked"| Denied
```

### Network Configuration Endpoints

```typescript
// Load available network interfaces
GET /core/settings/interface
Response: Array<InterfaceInfo>

// Update bind address and IPv6 setting
POST /core/settings/bind/update
Body: { ipv6: string, bindAddress: string }

// Update server port
POST /core/settings/port/update
Body: { serverPort: number }
```

### Safe Entrance Configuration

The `securityEntrance` setting defines a custom URL path (e.g., `/admin-xyz123`) required to access the panel. Without this path, requests receive a 404 response. The entrance is typically displayed via SSH command: `1pctl user-info`.

**Sources:** [frontend/src/api/interface/setting.ts:8-42](), [frontend/src/api/modules/setting.ts:118-126]()

---

## Proxy Configuration

The proxy system enables outbound HTTP/HTTPS requests to route through a forward proxy, essential for air-gapped environments or networks requiring proxy authentication. The `ProxyUpdate` interface supports HTTP, SOCKS5, and disabled states.

### Proxy Configuration Flow

```mermaid
sequenceDiagram
    participant UI as "Settings UI"
    participant API as "Core API"
    participant Docker as "Docker Engine"
    participant External as "External Services"
    
    UI->>API: POST /core/settings/proxy/update<br/>ProxyUpdate
    API->>API: Validate proxy config
    API->>API: Base64 encode password
    API->>API: Update settings in core.db
    
    alt withDockerRestart = true
        API->>Docker: Restart Docker daemon<br/>(applies proxy to containers)
    end
    
    API-->>UI: Success
    
    Note over External: Subsequent requests use proxy
    API->>External: HTTP request via proxy<br/>(app downloads, SSL cert requests)
```

### Proxy Update Parameters

```typescript
interface ProxyUpdate {
    proxyUrl: string;           // Proxy server address
    proxyType: string;          // "http", "socks5", or "close"
    proxyPort: string;          // Proxy port number
    proxyUser: string;          // Optional authentication username
    proxyPasswd: string;        // Optional authentication password
    proxyPasswdKeep: string;    // Keep existing password flag
    withDockerRestart: boolean; // Restart Docker to apply proxy
}
```

**Password Handling:** Passwords are Base64 encoded before transmission: `request.proxyPasswd = Base64.encode(request.proxyPasswd)`. When `proxyType` is set to `"close"`, it's converted to empty string to disable the proxy.

**Endpoint:**
```typescript
POST /core/settings/proxy/update
Body: ProxyUpdate
```

**Sources:** [frontend/src/api/interface/setting.ts:84-92](), [frontend/src/api/modules/setting.ts:107-114]()

---

## SSL/TLS Configuration

SSL configuration enables HTTPS access to the 1Panel web interface. The system supports three SSL sources: self-signed certificates, ACME-issued certificates, and manually uploaded certificates.

### SSL Configuration Structure

```typescript
interface SSLUpdate {
    ssl: string;        // "enable" or "disable"
    domain: string;     // Domain for ACME validation
    sslType: string;    // "self", "import", or "acme"
    cert: string;       // PEM-encoded certificate
    key: string;        // PEM-encoded private key
    sslID: number;      // Reference to SSL certificate ID
}

interface SSLInfo {
    domain: string;     // Current SSL domain
    timeout: string;    // Certificate expiration date
    rootPath: string;   // SSL files storage path
    cert: string;       // Current certificate content
    key: string;        // Current private key content
    sslID: number;      // Current certificate ID
}
```

### SSL Management Endpoints

```typescript
// Get current SSL configuration
GET /core/settings/ssl/info
Response: SSLInfo

// Update SSL configuration
POST /core/settings/ssl/update
Body: SSLUpdate

// Download current SSL certificate
GET /core/settings/ssl/download
Response: Binary file (certificate archive)
```

**SSL Type Behaviors:**
- **self**: Generates self-signed certificate on demand
- **import**: Uses uploaded certificate and key files
- **acme**: References a certificate from the SSL certificate manager (see [SSL Certificate Management](#7.4))

**Sources:** [frontend/src/api/interface/setting.ts:99-114](), [frontend/src/api/modules/setting.ts:127-135]()

---

## Authentication Settings

The settings system manages advanced authentication mechanisms including Multi-Factor Authentication (MFA) via TOTP and WebAuthn Passkey authentication.

### MFA Configuration

MFA uses Time-Based One-Time Password (TOTP) with configurable intervals. The binding process generates a QR code for authenticator apps.

```mermaid
sequenceDiagram
    participant User as "User"
    participant UI as "Settings UI"
    participant API as "Core API"
    participant Authenticator as "Authenticator App"
    
    User->>UI: Enable MFA
    UI->>API: POST /core/settings/mfa<br/>{ title, interval }
    API->>API: Generate TOTP secret
    API->>API: Generate QR code image
    API-->>UI: { secret, qrImage }
    UI->>User: Display QR code
    
    User->>Authenticator: Scan QR code
    Authenticator-->>User: Display 6-digit code
    
    User->>UI: Enter code
    UI->>API: POST /core/settings/mfa/bind<br/>{ secret, code, interval }
    API->>API: Validate TOTP code
    API->>API: Save mfaStatus="enable"
    API-->>UI: MFA enabled
```

**MFA Endpoints:**
```typescript
// Generate MFA QR code
POST /core/settings/mfa
Body: { title: string, interval: number }
Response: { secret: string, qrImage: string }

// Bind MFA with verification code
POST /core/settings/mfa/bind
Body: { secret: string, code: string, interval: string }
```

### Passkey (WebAuthn) Configuration

Passkey authentication enables biometric and hardware security key authentication using the WebAuthn standard. Multiple passkeys can be registered per user.

```mermaid
sequenceDiagram
    participant User as "User"
    participant UI as "Settings UI"
    participant API as "Core API"
    participant Browser as "Browser WebAuthn API"
    participant Device as "Authenticator Device"
    
    User->>UI: Add Passkey
    UI->>API: POST /core/settings/passkey/register/begin<br/>{ name }
    API->>API: Generate challenge
    API-->>UI: { sessionId, publicKey }
    
    UI->>Browser: navigator.credentials.create(publicKey)
    Browser->>Device: Request credential creation
    Device-->>Browser: Credential created (biometric/PIN)
    Browser-->>UI: Credential response
    
    UI->>API: POST /core/settings/passkey/register/finish<br/>Header: Passkey-Session: sessionId
    API->>API: Verify attestation
    API->>API: Store credential in core.db
    API-->>UI: Passkey registered
    
    User->>UI: List passkeys
    UI->>API: GET /core/settings/passkey/list
    API-->>UI: Array<PasskeyInfo>
```

**Passkey Endpoints:**
```typescript
// Begin passkey registration
POST /core/settings/passkey/register/begin
Body: { name: string }
Response: { sessionId: string, publicKey: Record<string, any> }

// Finish passkey registration
POST /core/settings/passkey/register/finish
Headers: { 'Passkey-Session': sessionId }
Body: WebAuthn attestation response

// List registered passkeys
GET /core/settings/passkey/list
Response: Array<PasskeyInfo>

// Delete passkey
DELETE /core/settings/passkey/:id
```

**PasskeyInfo Structure:**
```typescript
interface PasskeyInfo {
    id: string;         // Credential ID
    name: string;       // User-assigned name
    createdAt: string;  // Registration timestamp
    lastUsedAt: string; // Last authentication timestamp
}
```

**Sources:** [frontend/src/api/interface/setting.ts:122-147](), [frontend/src/api/modules/setting.ts:139-156]()

---

## Snapshot Configuration

The snapshot system creates point-in-time backups of the entire 1Panel installation including apps, databases, panel configuration, and operational data. Snapshots support encryption, selective data inclusion, and multi-account distribution.

### Snapshot Data Model

```typescript
interface SnapshotCreate {
    id: number;                      // 0 for new, >0 for recreate
    sourceAccountIDs: string;        // Comma-separated backup account IDs
    downloadAccountID: string;       // Account ID for storage
    description: string;             // Snapshot description
    secret: string;                  // Encryption password (optional)
    timeout: number;                 // Execution timeout in seconds
    
    appData: Array<DataTree>;        // Selected installed apps
    panelData: Array<DataTree>;      // Selected panel configurations
    backupData: Array<DataTree>;     // Selected backup accounts
    
    withMonitorData: boolean;        // Include monitoring history
    withLoginLog: boolean;           // Include login logs
    withOperationLog: boolean;       // Include operation logs
}
```

### Snapshot Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Creating: snapshotCreate()
    Creating --> Uploading: Data packaged
    Uploading --> Success: Upload complete
    Uploading --> Failed: Upload error
    
    Success --> Recovering: snapshotRecover(isNew=false)
    Success --> NewNodeRecover: snapshotRecover(isNew=true)
    Success --> Rollback: snapshotRollback()
    
    Recovering --> RecoverSuccess: Restore complete
    Recovering --> RecoverFailed: Restore error
    
    NewNodeRecover --> NewSuccess: Fresh install restored
    NewNodeRecover --> NewFailed: Fresh install error
    
    Rollback --> RollbackSuccess: Previous state restored
    Rollback --> RollbackFailed: Rollback error
    
    Success --> Deleted: snapshotDelete()
    Failed --> Deleted: snapshotDelete()
    RecoverSuccess --> [*]
    RollbackSuccess --> [*]
```

### DataTree Structure

The `DataTree` structure represents hierarchical data selection for snapshots:

```typescript
interface DataTree {
    id: string;           // Unique identifier
    label: string;        // Display name
    key: string;          // Data key (app name, DB name, etc.)
    name: string;         // Resource name
    size: number;         // Data size in bytes
    isShow: boolean;      // Visible in UI
    isDisable: boolean;   // Cannot be selected
    path: string;         // File system path
    Children: Array<DataTree>; // Nested items
}
```

### Snapshot Endpoints

```typescript
// Load available data for snapshot
GET /settings/snapshot/load
Response: { appData, panelData, backupData, withMonitorData, withLoginLog, withOperationLog }

// Create new snapshot
POST /settings/snapshot
Body: SnapshotCreate

// Recreate existing snapshot with updated data
POST /settings/snapshot/recreate
Body: { id: number }

// Import snapshot from backup account
POST /settings/snapshot/import
Body: { backupAccountID: number, names: Array<string>, description: string }

// Recover snapshot to current system
POST /settings/snapshot/recover
Body: { id, taskID, isNew, reDownload, secret }

// Rollback to snapshot state
POST /settings/snapshot/rollback
Body: { id, taskID, isNew, reDownload, secret }

// Search snapshots with pagination
POST /settings/snapshot/search
Body: SearchWithPage
Response: ResPage<SnapshotInfo>

// Delete snapshots
POST /settings/snapshot/del
Body: { ids: number[], deleteWithFile: boolean }
```

**Snapshot Encryption:** When `secret` is provided, the snapshot archive is AES-encrypted. The same secret must be provided during recovery/rollback operations.

**Snapshot Status Fields:**
- `status`: "Success", "Failed", "Uploading", "Creating"
- `recoverStatus`: "Success", "Failed", "Recovering"
- `rollbackStatus`: "Success", "Failed", "RollingBack"
- `interruptStep`: Records which step failed for recovery continuation

**Sources:** [frontend/src/api/interface/setting.ts:156-228](), [frontend/src/api/modules/setting.ts:166-192]()

---

## Upgrade System Configuration

The upgrade system manages 1Panel version updates with release notes, version constraints, and rollback capability through snapshots.

### Upgrade Information Structure

```typescript
interface UpgradeInfo {
    testVersion: string;     // Beta/testing version available
    newVersion: string;      // Stable version available
    latestVersion: string;   // Highest version available
    releaseNote: string;     // Markdown release notes
}

interface ReleasesNotes {
    Version: string;         // Version number (e.g., "v1.10.0")
    CreatedAt: string;       // Release date
    Content: string;         // Full release notes (Markdown)
    NewCount: number;        // Count of new features
    OptimizationCount: number; // Count of optimizations
    FixCount: number;        // Count of bug fixes
}
```

### Upgrade Process Flow

```mermaid
sequenceDiagram
    participant UI as "Settings UI"
    participant API as "Core API"
    participant Remote as "Remote Release Server"
    participant Snapshot as "Snapshot System"
    participant System as "System Files"
    
    UI->>API: GET /core/settings/upgrade
    API->>Remote: Check for updates
    Remote-->>API: Latest versions
    API-->>UI: UpgradeInfo
    
    UI->>API: GET /core/settings/upgrade/releases
    API->>Remote: Fetch all release notes
    Remote-->>API: Array<ReleasesNotes>
    API-->>UI: Release history
    
    UI->>API: POST /core/settings/upgrade/notes<br/>{ version }
    API-->>UI: Specific version notes (Markdown)
    
    User->>UI: Confirm upgrade to version X
    
    opt Auto-backup enabled (upgradeBackupCopies > 0)
        UI->>Snapshot: Create pre-upgrade snapshot
        Snapshot-->>UI: Snapshot created
    end
    
    UI->>API: POST /core/settings/upgrade<br/>{ version }
    API->>Remote: Download new version binary
    API->>System: Replace binary files
    API->>System: Restart service
    API-->>UI: Upgrade complete (connection lost)
    
    Note over UI: User refreshes to reconnect
```

### Upgrade Endpoints

```typescript
// Get available upgrade information
GET /core/settings/upgrade
Response: UpgradeInfo

// List all release notes
GET /core/settings/upgrade/releases
Response: Array<ReleasesNotes>

// Get specific version release notes
POST /core/settings/upgrade/notes
Body: { version: string }
Response: string (Markdown content)

// Execute upgrade
POST /core/settings/upgrade
Body: { version: string }
```

**Automatic Backup:** The `upgradeBackupCopies` setting (in `SettingInfo`) controls how many automatic snapshots are retained during upgrades. Setting this to `"3"` maintains the last 3 pre-upgrade snapshots.

**Version Selection:** Users can upgrade to `newVersion` (stable), `testVersion` (beta), or any previous version for rollback scenarios.

**Sources:** [frontend/src/api/interface/setting.ts:229-288](), [frontend/src/api/modules/setting.ts:195-206]()

---

## License Management

The license system enforces node-level feature gating between Community and Pro editions. Licenses bind to specific nodes and control access to advanced features like multi-node management, enhanced monitoring, and SMS notifications.

### License Data Model

```typescript
interface License {
    licenseName: string;        // License identifier
    assigneeName: string;       // Licensed organization/user
    productPro: string;         // Product tier ("community" or "xpack")
    versionConstraint: string;  // Compatible version range
    trial: boolean;             // Trial license flag
    status: string;             // "Active", "Expired", "Invalid"
    message: string;            // Status message
    smsUsed: number;            // SMS notifications used
    smsTotal: number;           // SMS notifications quota
}

interface LicenseStatus {
    productPro: string;         // Current product tier
    status: string;             // License status
    smsTotal: number;           // Total SMS quota
    smsUsed: number;            // Used SMS quota
}

interface LicenseBind {
    nodeID: number;             // Target node ID
    licenseID: number;          // License to bind
    syncList: string;           // Data to sync ("app,website,database")
    withDockerRestart: boolean; // Restart Docker after binding
}
```

### License Binding Workflow

```mermaid
sequenceDiagram
    participant Admin as "Administrator"
    participant UI as "License UI"
    participant CoreAPI as "Core API"
    participant MasterDB as "Master core.db"
    participant NodeAPI as "Node Agent API"
    participant NodeDB as "Node agent.db"
    
    Admin->>UI: Upload license file
    UI->>CoreAPI: POST /core/licenses/upload
    CoreAPI->>CoreAPI: Validate license signature
    CoreAPI->>MasterDB: Store license record
    CoreAPI-->>UI: License uploaded
    
    Admin->>UI: Select node + license
    UI->>CoreAPI: POST /core/licenses/bind<br/>{ nodeID, licenseID, syncList }
    
    CoreAPI->>MasterDB: Mark license as bound
    CoreAPI->>NodeAPI: Transfer license data
    NodeAPI->>NodeDB: Store license credentials
    
    alt syncList includes "app"
        CoreAPI->>NodeAPI: Sync app store catalog
    end
    alt syncList includes "website"
        CoreAPI->>NodeAPI: Sync website templates
    end
    alt syncList includes "database"
        CoreAPI->>NodeAPI: Sync database configs
    end
    
    alt withDockerRestart = true
        NodeAPI->>NodeAPI: Restart Docker daemon
    end
    
    NodeAPI-->>CoreAPI: Binding complete
    CoreAPI-->>UI: Node upgraded to Pro
    
    Note over NodeAPI: Pro features now enabled
```

### Node Management

```typescript
interface NodeItem {
    id: number;         // Node database ID
    addr: string;       // Node address (IP:port)
    status: string;     // "Running", "Stopped", "Error"
    version: string;    // 1Panel version
    isXpack: boolean;   // Pro edition enabled
    isBound: boolean;   // License bound to this node
    name: string;       // Node display name
}

interface SimpleNodeItem {
    id: number;
    name: string;
    addr: string;
    description: string;
    systemVersion: string;         // OS version
    securityEntrance: string;      // Safe entrance path
    cpuUsedPercent: number;        // CPU usage
    cpuTotal: number;              // CPU core count
    memoryTotal: number;           // Total RAM in bytes
    memoryUsedPercent: number;     // Memory usage
}
```

### License Endpoints

```typescript
// Upload new license
POST /core/licenses/upload
Body: FormData (license file)

// Update existing license
POST /core/licenses/update
Body: FormData (license file)

// Search licenses with pagination
POST /core/licenses/search
Body: ReqPage
Response: ResPage<License>

// Delete license
POST /core/licenses/del
Body: { ids: number }

// Get license status for current node
GET /core/licenses/status
Response: LicenseStatus

// Get license status for master node
GET /core/licenses/master/status
Response: LicenseStatus

// Sync license data from remote
POST /core/licenses/sync
Body: { id: number }

// Bind license to node
POST /core/licenses/bind
Body: LicenseBind
Timeout: 60 seconds

// Unbind license from node
POST /core/licenses/unbind
Body: { id: number, force: boolean, withDockerRestart: boolean }
Timeout: 60 seconds

// Change license binding between nodes
POST /core/licenses/bind/free
Body: { licenseID: number, nodeIDs: Array<number> }
Timeout: 60 seconds

// Load license options for dropdown
GET /core/licenses/options
Response: Array<LicenseOptions>

// List nodes by type
POST /core/nodes/list
Body: { type: string }
Response: Array<NodeItem>

// List all nodes
GET /core/nodes/all
Response: Array<NodeItem>

// List simple node info for dashboard
GET /core/nodes/simple/all
Response: Array<SimpleNodeItem>

// Get SMS quota information
GET /core/licenses/sms/info
Response: { licenseName, smsUsed, smsTotal }

// List nodes with app updates available
GET /core/xpack/nodes/apps/update
Response: Array<NodeAppItem>
Timeout: 60 seconds
```

**License Binding Constraints:**
- Each license can bind to multiple nodes based on quota
- `availableFreeCount` in `LicenseOptions` shows remaining node slots
- Forced unbinding (`force: true`) removes license even if node is offline
- SMS quota is shared across all nodes bound to a license

**Sources:** [frontend/src/api/interface/setting.ts:236-312](), [frontend/src/api/modules/setting.ts:10-60]()

---

## API Key Management

The API key system enables programmatic access to 1Panel with IP-based access control and key expiration management. This allows CI/CD systems and automation tools to interact with the panel without web UI authentication.

### API Configuration Structure

```typescript
interface ApiConfig {
    apiInterfaceStatus: string;    // "enable" or "disable"
    apiKey: string;                // Generated API key (64-char hex)
    ipWhiteList: string;           // Comma-separated IP addresses
    apiKeyValidityTime: number;    // Expiration time (Unix timestamp)
}
```

### API Key Management Flow

```mermaid
sequenceDiagram
    participant Admin as "Administrator"
    participant UI as "Settings UI"
    participant API as "Core API"
    participant DB as "core.db"
    participant Client as "API Client"
    
    Admin->>UI: Enable API access
    UI->>API: POST /core/settings/api/config/generate/key
    API->>API: Generate secure random key
    API-->>UI: Return 64-character key
    
    Admin->>UI: Configure settings<br/>(key, IPs, expiration)
    UI->>API: POST /core/settings/api/config/update<br/>ApiConfig
    API->>DB: Store API configuration
    API-->>UI: Configuration saved
    
    Note over Client: Later: API usage
    Client->>API: Request with header<br/>Api-Key: {key}
    API->>API: Validate key exists
    API->>API: Check expiration time
    API->>API: Verify client IP in whitelist
    
    alt Valid key and IP
        API->>API: Process request
        API-->>Client: Response
    else Invalid or expired
        API-->>Client: 401 Unauthorized
    end
```

### API Key Endpoints

```typescript
// Generate new API key
POST /core/settings/api/config/generate/key
Response: string (64-character hex key)

// Update API configuration
POST /core/settings/api/config/update
Body: ApiConfig
```

**API Key Properties:**
- Keys are 64-character hexadecimal strings
- Keys are stored in `core.db` settings table with key `"ApiKey"`
- IP whitelist supports CIDR notation (e.g., `"192.168.1.0/24"`)
- `apiKeyValidityTime` of `0` means no expiration
- When `apiInterfaceStatus` is `"disable"`, all API requests are rejected regardless of valid keys

**API Request Authentication:**
Clients include the API key in request headers:
```http
GET /api/v1/containers
Api-Key: a1b2c3d4e5f6...
```

**Sources:** [frontend/src/api/interface/setting.ts:93-98](), [frontend/src/api/modules/setting.ts:209-214]()

---

## App Store Configuration

The App Store configuration controls which remote catalog 1Panel uses to fetch application metadata. This allows organizations to use private app repositories or mirrors.

### App Store Configuration Structure

```typescript
interface AppStoreConfig {
    appStoreUrl: string;          // App catalog base URL
    appStoreLastModified: string; // Last sync timestamp
}

interface AppStoreConfigUpdate {
    appStoreUrl: string;          // New catalog URL
}
```

### App Store Endpoints

```typescript
// Get current app store configuration
GET /core/settings/apps/store/config
Query: ?operateNode={node}  // Optional: target specific node
Response: AppStoreConfig

// Update app store configuration
POST /core/settings/apps/store/update
Body: { appStoreUrl: string }
```

**Default App Store:** The default URL points to the official 1Panel app repository which serves `1panel.json` containing app metadata, icons, docker-compose templates, and installation scripts.

**Multi-Node Support:** The `?operateNode={node}` query parameter allows configuring different app stores per node in multi-node deployments.

**Sources:** [frontend/src/api/modules/setting.ts:157-163]()

---

## Agent Settings Management

The Agent API server maintains its own configuration separate from Core settings, primarily focused on operational parameters like base directories, daemon paths, and snapshot preferences.

### Agent Settings Endpoints

```typescript
// Get base directory path
GET /settings/basedir
Response: string (e.g., "/opt/1panel")

// Get Docker daemon.json path
GET /settings/daemonjson
Response: string (e.g., "/etc/docker/daemon.json")

// Update agent setting
POST /settings/update
Body: { key: string, value: string }

// Get all agent settings
POST /settings/search
Response: SettingInfo (subset of fields used by agent)

// Get single agent setting by key
GET /settings/get/:key
Response: string

// Save description for common resources
POST /settings/description/save
Body: { id, type, detailType, isPinned, description }
```

### Common Description System

The `CommonDescription` interface provides a unified way to attach descriptions and pin status to various resources (containers, websites, databases, etc.):

```typescript
interface CommonDescription {
    id: string;          // Resource ID
    type: string;        // Resource type ("container", "website", "app", etc.)
    detailType: string;  // Sub-type (e.g., "mysql" for database type)
    isPinned: boolean;   // Pin to top of lists
    description: string; // User-defined description
}
```

**Sources:** [frontend/src/api/interface/setting.ts:148-154](), [frontend/src/api/modules/setting.ts:63-80]()

---

## Memo System

The memo system provides a scratchpad for administrators to store notes visible on the dashboard.

### Memo Endpoints

```typescript
// Get current memo content
GET /core/settings/memo
Response: string (memo content)

// Update memo content
POST /core/settings/memo
Body: { content: string }
```

The memo content is displayed on the dashboard when `dashboardMemoVisible` is set to `"enable"` in `SettingInfo`.

**Sources:** [frontend/src/api/modules/setting.ts:217-222]()

---

## Settings Update Patterns

### Single Setting Update Pattern

Most settings follow a key-value update pattern:

```typescript
interface SettingUpdate {
    key: string;    // Setting name (e.g., "SystemIP", "PanelName")
    value: string;  // New value (always string, parsed by backend)
}

// Example: Update panel name
updateSetting({ key: "PanelName", value: "Production Panel" })

// Example: Enable monitoring
updateSetting({ key: "MonitorStatus", value: "enable" })
```

### Specialized Update Endpoints

Some settings require dedicated endpoints due to complex validation or side effects:

| Endpoint | Purpose | Side Effects |
|----------|---------|--------------|
| `/core/settings/password/update` | Change admin password | Invalidates all sessions |
| `/core/settings/port/update` | Change panel port | Requires service restart |
| `/core/settings/ssl/update` | Configure SSL | Regenerates certificate files |
| `/core/settings/proxy/update` | Configure proxy | Optionally restarts Docker |
| `/core/settings/bind/update` | Change bind address | Requires service restart |
| `/core/settings/menu/update` | Update menu visibility | Updates UI state |
| `/core/settings/menu/default` | Reset menu to defaults | Clears custom menu config |

### Menu Configuration

Menu visibility is controlled through a specialized endpoint that accepts the same `SettingUpdate` structure but performs additional validation:

```typescript
POST /core/settings/menu/update
Body: { key: "HideMenu", value: "app,website,database" }

POST /core/settings/menu/default
// Resets menu to show all items
```

**Sources:** [frontend/src/api/interface/setting.ts:80-83](), [frontend/src/api/modules/setting.ts:98-126]()

---

## Settings Storage and Persistence

Settings are stored in SQLite databases with different scoping:

### Core Settings Storage

```mermaid
graph LR
    SettingsTable["settings table<br/>in core.db"]
    LicensesTable["licenses table<br/>in xpack.db"]
    PasskeysTable["passkeys table<br/>in core.db"]
    
    SettingInfo --> SettingsTable
    ApiConfig --> SettingsTable
    TerminalInfo --> SettingsTable
    SSLInfo --> SettingsTable
    
    License --> LicensesTable
    LicenseStatus --> LicensesTable
    
    PasskeyInfo --> PasskeysTable
```

**Settings Table Schema:** Each setting is stored as a key-value pair where:
- `key`: Setting name (e.g., `"SystemIP"`, `"PanelName"`)
- `value`: Setting value as string (even for numbers/booleans)
- Complex settings (MFA, proxy) use JSON serialization in the value field

### Agent Settings Storage

Agent settings reside in `agent.db` on each node, allowing per-node configuration independence:

```
agent.db
├── settings table (base configuration)
├── snapshots table (snapshot records)
└── backup_accounts table (referenced by snapshots)
```

### Multi-Node Settings Synchronization

When the `CurrentNode` header is set in requests, settings operations target specific nodes. The Core server proxies requests to the appropriate Agent API:

```typescript
// Target specific node
const headers = { CurrentNode: "2" };
await getAgentSettingInfo();  // Routed to node 2's agent API

// Without header, uses current node from global store
```

**Sources:** Analysis of [frontend/src/api/modules/setting.ts:63-80]()

---

## Diagram: Complete Settings API Surface

```mermaid
graph TB
    subgraph "Core Settings API (/core/settings/*)"
        CoreSearch["/search<br/>GET all settings"]
        CoreBy["/by<br/>GET single setting"]
        CoreUpdate["/update<br/>POST key-value"]
        CorePassword["/password/update<br/>POST password change"]
        CorePort["/port/update<br/>POST port change"]
        CoreBind["/bind/update<br/>POST bind address"]
        CoreSSL["/ssl/update<br/>POST SSL config"]
        CoreSSLInfo["/ssl/info<br/>GET SSL status"]
        CoreSSLDownload["/ssl/download<br/>GET cert files"]
        CoreProxy["/proxy/update<br/>POST proxy config"]
        CoreTerminal["/terminal/search<br/>GET terminal config"]
        CoreTerminalUpdate["/terminal/update<br/>POST terminal config"]
        CoreMFA["/mfa<br/>POST generate TOTP"]
        CoreMFABind["/mfa/bind<br/>POST enable MFA"]
        CorePasskeyBegin["/passkey/register/begin"]
        CorePasskeyFinish["/passkey/register/finish"]
        CorePasskeyList["/passkey/list"]
        CorePasskeyDelete["/passkey/:id"]
        CoreMenu["/menu/update<br/>POST menu visibility"]
        CoreMenuDefault["/menu/default<br/>POST reset menu"]
        CoreInterface["/interface<br/>GET network interfaces"]
        CoreAvailable["/search/available<br/>GET system status"]
        CoreExpired["/expired/handle<br/>POST password expired"]
        CoreAppStore["/apps/store/config<br/>GET app store URL"]
        CoreAppStoreUpdate["/apps/store/update<br/>POST update URL"]
        CoreMemo["/memo<br/>GET memo content"]
        CoreMemoUpdate["/memo<br/>POST memo content"]
        CoreAPIGenerate["/api/config/generate/key"]
        CoreAPIUpdate["/api/config/update"]
        CoreUpgrade["/upgrade<br/>GET upgrade info"]
        CoreUpgradeReleases["/upgrade/releases<br/>GET release list"]
        CoreUpgradeNotes["/upgrade/notes<br/>POST get notes"]
        CoreUpgradeExecute["/upgrade<br/>POST execute upgrade"]
    end
    
    subgraph "License API (/core/licenses/*)"
        LicenseUpload["/upload<br/>POST new license"]
        LicenseUpdate["/update<br/>POST update license"]
        LicenseSearch["/search<br/>POST paginated list"]
        LicenseDelete["/del<br/>POST delete"]
        LicenseStatus["/status<br/>GET current node"]
        LicenseMasterStatus["/master/status<br/>GET master"]
        LicenseSync["/sync<br/>POST sync from remote"]
        LicenseBind["/bind<br/>POST bind to node"]
        LicenseUnbind["/unbind<br/>POST unbind from node"]
        LicenseChangeBind["/bind/free<br/>POST change binding"]
        LicenseOptions["/options<br/>GET license list"]
        LicenseSMS["/sms/info<br/>GET SMS quota"]
    end
    
    subgraph "Node API (/core/nodes/*)"
        NodeList["/list<br/>POST filter by type"]
        NodeAll["/all<br/>GET all nodes"]
        NodeSimple["/simple/all<br/>GET dashboard info"]
        NodeApps["/xpack/nodes/apps/update<br/>GET app updates"]
    end
    
    subgraph "Agent Settings API (/settings/*)"
        AgentBaseDir["/basedir<br/>GET base directory"]
        AgentDaemon["/daemonjson<br/>GET daemon path"]
        AgentUpdate["/update<br/>POST key-value"]
        AgentSearch["/search<br/>POST get all"]
        AgentGet["/get/:key<br/>GET single setting"]
        AgentDescription["/description/save<br/>POST resource description"]
    end
    
    subgraph "Snapshot API (/settings/snapshot/*)"
        SnapshotLoad["/load<br/>GET available data"]
        SnapshotCreate["/create<br/>POST new snapshot"]
        SnapshotRecreate["/recreate<br/>POST update existing"]
        SnapshotImport["/import<br/>POST from backup"]
        SnapshotRecover["/recover<br/>POST restore system"]
        SnapshotRollback["/rollback<br/>POST revert to snapshot"]
        SnapshotSearch["/search<br/>POST paginated list"]
        SnapshotDelete["/del<br/>POST delete snapshots"]
        SnapshotUpdateDesc["/description/update<br/>POST update description"]
    end
```

**Sources:** [frontend/src/api/modules/setting.ts:1-223]()

---

# Page: Application Management System

# Application Management System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/app/api/v2/app.go](agent/app/api/v2/app.go)
- [agent/app/dto/file.go](agent/app/dto/file.go)
- [agent/app/dto/request/app.go](agent/app/dto/request/app.go)
- [agent/app/dto/response/app.go](agent/app/dto/response/app.go)
- [agent/app/repo/app.go](agent/app/repo/app.go)
- [agent/app/service/app.go](agent/app/service/app.go)
- [agent/app/service/app_install.go](agent/app/service/app_install.go)
- [agent/app/service/app_sync_task.go](agent/app/service/app_sync_task.go)
- [agent/app/service/app_utils.go](agent/app/service/app_utils.go)
- [agent/global/config.go](agent/global/config.go)
- [agent/init/business/business.go](agent/init/business/business.go)
- [agent/init/dir/dir.go](agent/init/dir/dir.go)
- [agent/router/ro_app.go](agent/router/ro_app.go)
- [agent/utils/appicon/appicon.go](agent/utils/appicon/appicon.go)
- [agent/utils/files/utils.go](agent/utils/files/utils.go)
- [agent/utils/req_helper/request.go](agent/utils/req_helper/request.go)
- [core/init/cron/cron.go](core/init/cron/cron.go)
- [frontend/src/api/interface/app.ts](frontend/src/api/interface/app.ts)
- [frontend/src/api/modules/app.ts](frontend/src/api/modules/app.ts)
- [frontend/src/components/app-status/index.vue](frontend/src/components/app-status/index.vue)
- [frontend/src/global/form-rules.ts](frontend/src/global/form-rules.ts)
- [frontend/src/styles/common.scss](frontend/src/styles/common.scss)
- [frontend/src/views/app-store/apps/index.vue](frontend/src/views/app-store/apps/index.vue)
- [frontend/src/views/app-store/detail/index.vue](frontend/src/views/app-store/detail/index.vue)
- [frontend/src/views/app-store/detail/install/index.vue](frontend/src/views/app-store/detail/install/index.vue)
- [frontend/src/views/app-store/detail/params/index.vue](frontend/src/views/app-store/detail/params/index.vue)
- [frontend/src/views/app-store/installed/detail/index.vue](frontend/src/views/app-store/installed/detail/index.vue)
- [frontend/src/views/app-store/installed/index.vue](frontend/src/views/app-store/installed/index.vue)
- [frontend/src/views/app-store/installed/upgrade/index.vue](frontend/src/views/app-store/installed/upgrade/index.vue)
- [frontend/src/views/website/website/create/index.vue](frontend/src/views/website/website/create/index.vue)
- [frontend/src/views/website/website/index.vue](frontend/src/views/website/website/index.vue)

</details>



## Purpose and Scope

The Application Management System provides a Docker Compose-based application marketplace and lifecycle management framework within 1Panel. This system enables users to browse a curated app catalog, install applications with configurable parameters, and manage their lifecycle through start/stop/upgrade/uninstall operations. Applications are deployed as Docker containers orchestrated by Docker Compose, with automatic handling of database provisioning, environment configuration, and resource linking.

This document provides an overview of the app management architecture, core data models, and operational workflows. For detailed information on specific subsystems:
- App catalog synchronization and browsing: see [App Store and Catalog](#6.1)
- Installation workflow and parameter handling: see [App Installation and Deployment](#6.2)  
- Post-installation operations and lifecycle management: see [Installed App Operations](#6.3)

---

## System Architecture

The Application Management System operates across three layers: the frontend Vue.js application, the backend Go agent service, and external app store repositories.

### Component Architecture

```mermaid
graph TB
    subgraph "Frontend - Vue 3"
        AppStoreView["apps/index.vue<br/>Browse App Catalog"]
        InstalledView["installed/index.vue<br/>Manage Installed Apps"]
        InstallDialog["detail/install/index.vue<br/>Installation Form"]
        AppAPI["api/modules/app.ts<br/>API Client Layer"]
    end
    
    subgraph "Backend - Go Agent Service"
        AppHandler["api/v2/app.go<br/>HTTP Handlers"]
        AppService["service/app.go<br/>IAppService"]
        AppInstallService["service/app_install.go<br/>IAppInstallService"]
        AppRepo["repo/app.go<br/>IAppRepo"]
        AppInstallRepo["repo/app_install.go<br/>IAppInstallRepo"]
    end
    
    subgraph "Database - SQLite"
        AppsTable[("apps<br/>App metadata")]
        AppDetailsTable[("app_details<br/>Version-specific data")]
        AppInstallsTable[("app_installs<br/>Installation records")]
        AppResourcesTable[("app_install_resources<br/>Linked databases")]
    end
    
    subgraph "External Systems"
        RemoteStore["Remote App Store<br/>1panel.json catalog"]
        Docker["Docker Engine<br/>Container runtime"]
        ComposeFiles["Docker Compose YAML<br/>In app directories"]
    end
    
    AppStoreView --> AppAPI
    InstalledView --> AppAPI
    InstallDialog --> AppAPI
    AppAPI -->|HTTP POST/GET| AppHandler
    
    AppHandler --> AppService
    AppHandler --> AppInstallService
    
    AppService --> AppRepo
    AppInstallService --> AppInstallRepo
    
    AppRepo --> AppsTable
    AppRepo --> AppDetailsTable
    AppInstallRepo --> AppInstallsTable
    AppInstallRepo --> AppResourcesTable
    
    AppService -.sync.-> RemoteStore
    AppInstallService --> Docker
    AppInstallService --> ComposeFiles
```

**Sources:** [frontend/src/views/app-store/apps/index.vue:1-279](), [frontend/src/views/app-store/installed/index.vue:1-469](), [agent/app/service/app.go:1-636](), [agent/app/service/app_install.go:1-848](), [agent/app/api/v2/app.go:1-245]()

---

## Core Data Model

The system uses three primary entities to represent applications, their versions, and installations.

### Entity Relationship Diagram

```mermaid
erDiagram
    App ||--o{ AppDetail : "has versions"
    App ||--o{ AppInstall : "installed as"
    App ||--o{ AppTag : "tagged with"
    AppDetail ||--o{ AppInstall : "installed from"
    AppInstall ||--o{ AppInstallResource : "links to"
    
    App {
        uint id
        string key "Unique identifier"
        string name "Display name"
        string type "website/runtime/tool"
        int limit "Max installations 0=unlimited"
        string resource "remote/local/custom"
        bool gpu_support
        int recommend "Sort priority"
        json translations "Localized descriptions"
    }
    
    AppDetail {
        uint id
        uint app_id
        string version "Semver version"
        string docker_compose "YAML template"
        string params "JSON form fields"
        string download_url
        int status "Normal/TakeDown"
    }
    
    AppInstall {
        uint id
        string name "User-assigned name"
        uint app_id
        uint app_detail_id
        string version
        string status "Installing/Running/Error"
        string env "JSON parameters"
        string docker_compose "Generated YAML"
        int http_port
        int https_port
        string container_name
        string service_name
    }
    
    AppInstallResource {
        uint id
        uint app_install_id
        uint resource_id "DB ID"
        uint link_id "Source app/database ID"
        string key "mysql/postgresql/etc"
        string from "local/remote"
    }
```

**Key Structures:**

| Entity | Purpose | Key Fields |
|--------|---------|------------|
| `model.App` | App catalog entry | `Key`, `Type`, `Limit`, `Resource` |
| `model.AppDetail` | Version-specific metadata | `Version`, `DockerCompose`, `Params` |
| `model.AppInstall` | Installation instance | `Name`, `Status`, `Env`, `ContainerName` |
| `model.AppInstallResource` | Linked database resources | `ResourceId`, `LinkId`, `Key` |

**Sources:** [agent/app/dto/response/app.go:1-164](), [frontend/src/api/interface/app.ts:1-365]()

---

## Application States and Lifecycle

Applications transition through distinct states during their lifecycle, from catalog browsing to installation and operational management.

### State Machine

```mermaid
stateDiagram-v2
    [*] --> Catalog: App exists in store
    Catalog --> Installing: Install operation
    Installing --> Running: Successful up
    Installing --> InstallErr: Failure
    InstallErr --> Installing: Retry
    
    Running --> Stopped: Stop operation
    Stopped --> Running: Start operation
    Running --> Upgrading: Upgrade operation
    Upgrading --> Running: Success
    Upgrading --> UpgradeErr: Failure
    UpgradeErr --> Running: Rollback
    
    Running --> Rebuilding: Rebuild operation
    Rebuilding --> Running: Success
    
    Running --> Uninstalling: Delete operation
    Stopped --> Uninstalling: Delete operation
    Uninstalling --> [*]: Complete
    
    note right of Installing
        Status: constant.StatusInstalling
        Task: task.TaskInstall
    end note
    
    note right of Running
        Status: constant.StatusRunning
        Container: Running
    end note
    
    note right of Upgrading
        Status: constant.StatusUpgrading
        Task: task.TaskUpgrade
    end note
```

**Status Constants:**

| Constant | Value | Meaning |
|----------|-------|---------|
| `constant.StatusInstalling` | "Installing" | Initial installation in progress |
| `constant.StatusRunning` | "Running" | Container successfully running |
| `constant.StatusInstallErr` | "InstallErr" | Installation failed |
| `constant.StatusUpgrading` | "Upgrading" | Upgrade in progress |
| `constant.StatusUpgradeErr` | "UpgradeErr" | Upgrade failed |
| `constant.StatusUninstalling` | "Uninstalling" | Removal in progress |

**Sources:** [agent/app/service/app.go:342-576](), [agent/app/service/app_utils.go:333-468](), [agent/app/service/app_utils.go:674-898]()

---

## App Store Synchronization

The system maintains a local mirror of remote app catalog metadata through periodic synchronization tasks.

### Sync Process Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend as "apps/index.vue"
    participant API as "api/v2/app.go::SyncApp"
    participant Service as "app_sync_task.go"
    participant Remote as "Remote App Store"
    participant DB as "apps/app_details tables"
    
    User->>Frontend: Click sync button
    Frontend->>API: POST /apps/sync/remote
    API->>Service: SyncAppListFromRemote(taskID)
    Service->>Service: Check appStoreSyncMu lock
    
    Service->>Remote: GET 1panel.json
    Remote-->>Service: App catalog JSON
    
    Service->>Service: Parse AppList DTO
    loop For each app
        Service->>DB: Upsert app record
        loop For each version
            Service->>DB: Upsert app_detail
        end
        Service->>DB: Sync app_tags
    end
    
    Service->>Service: Delete removed apps
    Service->>Service: Download app icons
    Service-->>Frontend: Task completion
```

**Synchronization Components:**

- **Lock Management:** `appStoreSyncMu` mutex prevents concurrent sync operations
- **Version Tracking:** `AppStoreSyncStatus` setting tracks sync state
- **Incremental Updates:** Compares remote `LastModified` timestamp
- **Icon Caching:** Downloads and stores app icons locally in `1panel/data/cache/app_icons`

**Sources:** [agent/app/service/app_sync_task.go:1-320](), [frontend/src/views/app-store/apps/index.vue:175-198]()

---

## Installation Workflow

Application installation follows a multi-phase process orchestrated by task subtasks, with automatic rollback on failure.

### Installation Task Chain

```mermaid
graph LR
    subgraph "Task Orchestration"
        CreateTask["task.NewTaskWithOps<br/>TaskInstall scope"]
        SubTask1["copyData<br/>Download & extract"]
        SubTask2["createLink<br/>Provision databases"]
        SubTask3["runScript<br/>Execute init.sh"]
        SubTask4["upApp<br/>docker compose up"]
    end
    
    CreateTask --> SubTask1
    SubTask1 --> SubTask2
    SubTask2 --> SubTask3
    SubTask3 --> SubTask4
    
    SubTask1 -.rollback.-> CleanFiles["Delete app directory"]
    SubTask2 -.rollback.-> DeleteDBs["deleteLink<br/>Drop databases"]
    SubTask4 -.rollback.-> ComposeDown["docker compose down"]
```

**Key Functions in Installation Pipeline:**

1. **Request Validation** - `app.go::Install` [agent/app/service/app.go:342-576]()
   - Check Docker network exists
   - Validate app name uniqueness
   - Check port availability
   - Verify resource limits

2. **Compose Generation** - `app_utils.go::addDockerComposeCommonParam` [agent/app/service/app_utils.go:1366-1549]()
   - Merge user params with template
   - Configure container name, restart policy
   - Set CPU/memory limits
   - Handle port mappings

3. **Database Provisioning** - `app_utils.go::createLink` [agent/app/service/app_utils.go:207-331]()
   - Create MySQL/PostgreSQL/MongoDB databases
   - Generate credentials
   - Link via `AppInstallResource` records

4. **Container Deployment** - Uses `compose.Up()` wrapper around Docker Compose V2 API

**Sources:** [agent/app/service/app.go:342-576](), [agent/app/service/app_utils.go:207-331](), [agent/app/service/app_utils.go:1366-1549]()

---

## Installed App Operations

Post-installation, the system provides lifecycle management operations through standardized interfaces.

### Operation Routing

| Operation | Handler | Implementation | Docker Command |
|-----------|---------|----------------|----------------|
| `start` | `AppInstallService::Operate` | `compose.Start()` | `docker compose start` |
| `stop` | `AppInstallService::Operate` | `compose.Stop()` | `docker compose stop` |
| `restart` | `AppInstallService::Operate` | `compose.Restart()` | `docker compose restart` |
| `rebuild` | `AppInstallService::Operate` | `compose.Down() + Up()` | Recreate containers |
| `upgrade` | `app_utils.go::upgradeInstall` | Version migration | Multi-step process |
| `delete` | `app_utils.go::deleteAppInstall` | Full cleanup | Remove all resources |

### Frontend Operation Interface

The installed apps view provides a unified control panel for all operations:

**Component:** `installed/index.vue` [frontend/src/views/app-store/installed/index.vue:1-469]()

**Action Buttons:** [frontend/src/views/app-store/installed/index.vue:296-376]()
- Rebuild: Recreates containers from current compose
- Restart: Stops and starts containers
- Start/Stop: Container state control
- Uninstall: Triggers deletion workflow
- Params: Opens parameter editor

**Status Polling:** The view uses `setInterval` to refresh app status every 30 seconds [frontend/src/views/app-store/installed/index.vue:460-462](), ensuring real-time status updates for long-running operations.

**Sources:** [agent/app/service/app_install.go:428-561](), [frontend/src/views/app-store/installed/index.vue:296-376]()

---

## Parameter Management

Applications define customizable parameters through a form schema system that generates UI controls and validates input.

### Parameter Schema Structure

```mermaid
graph TB
    AppDetail["model.AppDetail<br/>Params: JSON"]
    FormFields["dto.AppForm<br/>FormFields[]"]
    
    subgraph "Field Types"
        TextField["type: text/password<br/>envKey: PANEL_*"]
        NumberField["type: number<br/>validation rules"]
        SelectField["type: select<br/>values[] options"]
        ServiceField["type: service<br/>Links to databases"]
    end
    
    AppDetail --> FormFields
    FormFields --> TextField
    FormFields --> NumberField
    FormFields --> SelectField
    FormFields --> ServiceField
    
    ServiceField -.queries.-> DatabaseList["getAppService()<br/>Running databases"]
```

**Frontend Parameter Rendering:** `detail/params/index.vue` [frontend/src/views/app-store/detail/params/index.vue:1-353]()

**Backend Validation:** Parameters are validated during installation and update operations. The system supports:
- **Service Dependencies:** `type: "service"` fields link to running database/tool instances
- **Multi-App Linking:** `type: "apps"` fields with nested child services
- **Dynamic Values:** Some fields populate values by querying system state

**Parameter Updates:** The `updateAppInstallParams` endpoint allows modifying certain parameters post-installation, triggering container rebuild if needed [agent/app/service/app_install.go:678-777]().

**Sources:** [frontend/src/views/app-store/detail/params/index.vue:1-353](), [agent/app/service/app_install.go:678-777]()

---

## Task-Based Execution

Long-running operations (install, upgrade, uninstall) execute asynchronously through a task framework that provides logging, progress tracking, and rollback capabilities.

### Task Architecture

```mermaid
graph TB
    TaskRequest["request.AppInstallCreate<br/>taskID: uuid"]
    TaskFactory["task.NewTaskWithOps<br/>Creates Task + Logger"]
    
    subgraph "Task Execution"
        MainTask["Task<br/>Execute() goroutine"]
        SubTask1["SubTask<br/>Function + Rollback"]
        SubTask2["SubTask<br/>Function + Rollback"]
        SubTaskN["SubTask<br/>Function + Rollback"]
    end
    
    TaskLog["Task.Log()<br/>Writes to task table"]
    SSE["SSE Stream<br/>/tasks/logs/:id"]
    
    TaskRequest --> TaskFactory
    TaskFactory --> MainTask
    MainTask --> SubTask1
    SubTask1 --> SubTask2
    SubTask2 --> SubTaskN
    
    SubTask1 --> TaskLog
    SubTask2 --> TaskLog
    TaskLog --> SSE
```

**Task Lifecycle:**

1. **Creation:** `task.NewTaskWithOps(name, taskType, scope, taskID, resourceID)` [agent/app/service/app.go:523-526]()
2. **Subtask Registration:** `AddSubTask(name, fn, rollbackFn)` adds sequential steps
3. **Async Execution:** `go installTask.Execute()` runs in background [agent/app/service/app.go:564-573]()
4. **Progress Streaming:** Frontend opens SSE connection to stream logs [frontend/src/components/log/task/index.vue]()

**Rollback Mechanism:** If any subtask fails, the task executor calls registered rollback functions in reverse order, enabling automatic cleanup [agent/app/service/app_utils.go:871-881]().

**Sources:** [agent/app/service/app.go:523-573](), [agent/app/task/task.go]()

---

## Integration Points

The Application Management System integrates with multiple 1Panel subsystems:

### Cross-System Dependencies

| System | Integration Point | Purpose |
|--------|------------------|---------|
| **Database Management** | `createLink()` | Auto-provision MySQL/PostgreSQL/MongoDB databases for apps |
| **Website System** | App type `website` | Deploy apps as Nginx-backed websites |
| **Runtime Management** | App type `runtime` | PHP/Node/Python runtime environments |
| **Container Platform** | Docker SDK | All apps deploy as Docker containers |
| **Backup System** | `AppBackup()` | Snapshot app state before upgrades |
| **File Manager** | App directory access | Browse app files at `/opt/1panel/apps/[key]/[name]` |
| **Task Logging** | Async task framework | Stream installation/upgrade progress |

**Database Resource Linking:** When an app declares a database dependency, the system:
1. Queries available databases via `databaseRepo.Get()` [agent/app/service/app_utils.go:256-259]()
2. Creates database/user if not exists [agent/app/service/app_utils.go:274-313]()
3. Records link in `app_install_resources` table [agent/app/service/app_utils.go:316-326]()
4. Injects connection params into app's `.env` file

**Sources:** [agent/app/service/app_utils.go:207-331](), [agent/app/service/app_install.go:1-848]()

---

## API Endpoints

The system exposes RESTful endpoints for all app management operations:

### Core Routes

| Method | Path | Handler | Purpose |
|--------|------|---------|---------|
| POST | `/apps/search` | `SearchApp` | Paginated app catalog search |
| GET | `/apps/{key}` | `GetApp` | Fetch app metadata by key |
| GET | `/apps/detail/{id}/{version}/{type}` | `GetAppDetail` | Version-specific detail |
| POST | `/apps/install` | `InstallApp` | Install app instance |
| POST | `/apps/installed/search` | `SearchAppInstalled` | List installed apps |
| POST | `/apps/installed/op` | `OperateInstalled` | Execute lifecycle operation |
| POST | `/apps/installed/delete` | `DeleteAppInstall` | Uninstall app |
| POST | `/apps/sync/remote` | `SyncApp` | Sync app store catalog |
| GET | `/apps/services/{key}` | `GetAppService` | Query available service instances |

**Request/Response DTOs:**
- Requests: [agent/app/dto/request/app.go:1-184]()
- Responses: [agent/app/dto/response/app.go:1-164]()

**Sources:** [agent/app/api/v2/app.go:1-245](), [agent/router/ro_app.go:1-69]()

---

# Page: App Store and Catalog

# App Store and Catalog

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/app/api/v2/app.go](agent/app/api/v2/app.go)
- [agent/app/dto/file.go](agent/app/dto/file.go)
- [agent/app/dto/request/app.go](agent/app/dto/request/app.go)
- [agent/app/dto/response/app.go](agent/app/dto/response/app.go)
- [agent/app/repo/app.go](agent/app/repo/app.go)
- [agent/app/service/app.go](agent/app/service/app.go)
- [agent/app/service/app_install.go](agent/app/service/app_install.go)
- [agent/app/service/app_sync_task.go](agent/app/service/app_sync_task.go)
- [agent/app/service/app_utils.go](agent/app/service/app_utils.go)
- [agent/global/config.go](agent/global/config.go)
- [agent/init/business/business.go](agent/init/business/business.go)
- [agent/init/dir/dir.go](agent/init/dir/dir.go)
- [agent/router/ro_app.go](agent/router/ro_app.go)
- [agent/utils/appicon/appicon.go](agent/utils/appicon/appicon.go)
- [agent/utils/files/utils.go](agent/utils/files/utils.go)
- [agent/utils/req_helper/request.go](agent/utils/req_helper/request.go)
- [core/init/cron/cron.go](core/init/cron/cron.go)

</details>



This document describes the App Store and Catalog system, which manages the discovery, synchronization, and metadata of applications available for installation in 1Panel. This includes remote app store synchronization, local app management, icon caching, and tag-based categorization.

For information about app installation and lifecycle management, see [App Installation and Deployment](#6.2). For operations on installed apps, see [Installed App Operations](#6.3).

---

## Overview

The App Store system provides a centralized catalog of applications that users can browse and install. It supports three app sources:

| Source | Description | Storage Location |
|--------|-------------|------------------|
| **Remote** | Official 1Panel app store | `global.Dir.RemoteAppResourceDir` |
| **Local** | User-provided local apps | `global.Dir.LocalAppResourceDir` |
| **Custom** | Custom app definitions | `global.Dir.CustomAppResourceDir` |

The system maintains app metadata in SQLite, downloads and caches app icons with ETag support, and provides search/filtering capabilities through a tag-based categorization system.

**Sources:** [agent/app/service/app.go:1-1000](), [agent/global/config.go:26-52]()

---

## System Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Vue App Store UI]
    end
    
    subgraph "API Layer"
        SearchAppAPI["/apps/search<br/>POST"]
        SyncRemoteAPI["/apps/sync/remote<br/>POST"]
        SyncLocalAPI["/apps/sync/local<br/>POST"]
        GetAppAPI["/apps/:key<br/>GET"]
        GetIconAPI["/apps/icon/:key<br/>GET"]
        GetTagsAPI["/apps/tags<br/>GET"]
    end
    
    subgraph "Service Layer"
        AppService["AppService<br/>(IAppService)"]
        SyncTask["appSyncContext<br/>(sync orchestration)"]
        IconMgr["appicon package<br/>(icon utilities)"]
    end
    
    subgraph "Repository Layer"
        AppRepo["AppRepo<br/>(IAppRepo)"]
        AppDetailRepo["AppDetailRepo"]
        TagRepo["TagRepo"]
        AppTagRepo["AppTagRepo"]
    end
    
    subgraph "Database"
        AgentDB[("agent.db<br/>SQLite")]
    end
    
    subgraph "External Systems"
        RemoteStore["Remote App Store<br/>1panel.json"]
        LocalFS["Local Filesystem<br/>app directories"]
        IconCache["Icon Cache Dir<br/>global.Dir.IconCacheDir"]
    end
    
    UI --> SearchAppAPI
    UI --> SyncRemoteAPI
    UI --> SyncLocalAPI
    UI --> GetAppAPI
    UI --> GetIconAPI
    UI --> GetTagsAPI
    
    SearchAppAPI --> AppService
    SyncRemoteAPI --> AppService
    SyncLocalAPI --> AppService
    GetAppAPI --> AppService
    GetIconAPI --> AppService
    GetTagsAPI --> AppService
    
    AppService --> SyncTask
    AppService --> IconMgr
    AppService --> AppRepo
    AppService --> AppDetailRepo
    AppService --> TagRepo
    AppService --> AppTagRepo
    
    SyncTask --> RemoteStore
    SyncTask --> IconCache
    
    AppRepo --> AgentDB
    AppDetailRepo --> AgentDB
    TagRepo --> AgentDB
    AppTagRepo --> AgentDB
    
    AppService --> LocalFS
    IconMgr --> IconCache
```

The architecture follows a layered pattern where API endpoints delegate to `AppService`, which orchestrates synchronization tasks, manages icon caching, and persists metadata through repository classes.

**Sources:** [agent/app/api/v2/app.go:1-256](), [agent/app/service/app.go:38-62](), [agent/router/ro_app.go:1-50]()

---

## Data Model

### Core Entities

```mermaid
erDiagram
    App ||--o{ AppDetail : "has versions"
    App ||--o{ AppTag : "tagged with"
    Tag ||--o{ AppTag : "applied to"
    
    App {
        uint id PK
        string key "unique app identifier"
        string name "display name"
        string type "app/runtime/php/etc"
        string resource "remote/local/custom"
        string icon "app_key.png?etag=xxx"
        int limit "max installations"
        int recommend "sort order"
        string architectures "amd64,arm64"
        int memory_required "MB"
        bool gpu_support
        string description_zh
        string description_en
        string short_desc_zh
        string short_desc_en
        int last_modified "timestamp"
    }
    
    AppDetail {
        uint id PK
        uint app_id FK
        string version "1.0.0"
        string params "JSON app form"
        string docker_compose "compose yaml"
        string download_url "tar.gz URL"
        string download_callback_url
        string status "normal/take_down"
        bool update "needs redownload"
        int last_modified "timestamp"
    }
    
    Tag {
        uint id PK
        string key "unique tag key"
        string translations "JSON i18n"
    }
    
    AppTag {
        uint app_id FK
        uint tag_id FK
    }
```

The `App` entity stores base metadata, while `AppDetail` stores version-specific configuration. Tags enable categorization and filtering. The `icon` field uses the format `app_{key}.png?etag={value}` for cache control.

**Sources:** [agent/app/model/app.go:1-100](), [agent/app/dto/response/app.go:24-50]()

---

## Remote App Store Synchronization

### Synchronization Flow

```mermaid
sequenceDiagram
    participant UI as Frontend
    participant API as POST /apps/sync/remote
    participant Service as AppService
    participant Task as SyncTask
    participant Remote as Remote Store
    participant DB as agent.db
    participant Cache as Icon Cache
    
    UI->>API: Trigger sync
    API->>Service: SyncAppListFromRemote(taskID)
    Service->>Service: GetAppUpdate()
    Service->>Remote: GET /mode/1panel.json.version.txt
    Remote-->>Service: lastModified timestamp
    
    alt No update needed
        Service-->>UI: AppStoreIsUpToDate
    else Update available
        Service->>Task: createSyncAppStoreTask()
        Task->>Remote: GET /mode/1panel.json.zip
        Remote-->>Task: 1panel.json
        Task->>Task: Parse app list
        Task->>Task: Compare with local DB
        Task->>Task: Classify: new/update/delete
        Task->>DB: BatchCreate/Save/BatchDelete
        Task->>Task: createSyncAppStoreMetaTask()
        
        loop For each app
            Task->>Remote: GET icon URL<br/>If-None-Match: etag
            alt Icon changed (200)
                Remote-->>Task: icon bytes + ETag
                Task->>Cache: WriteIconFile(appKey, bytes)
            else Icon cached (304)
                Remote-->>Task: 304 Not Modified
            end
        end
        
        Task->>DB: Update app.icon fields
        Task->>DB: Update AppStoreLastModified
        Task-->>UI: Sync complete
    end
```

The synchronization process checks for updates by comparing timestamps, downloads the app list from the remote store, classifies changes, and persists metadata to the database. Icons are downloaded with HTTP ETag caching to minimize bandwidth usage.

**Sources:** [agent/app/service/app.go:950-1027](), [agent/app/service/app_sync_task.go:38-128]()

### Remote App List Structure

The remote app store serves a `1panel.json` file containing all available apps:

```json
{
  "lastModified": 1234567890,
  "apps": [
    {
      "appProperty": {
        "key": "mysql",
        "name": "MySQL",
        "tags": ["database", "popular"],
        "recommend": 100,
        "icon": "https://..."
      },
      "versions": [
        {
          "name": "8.0.32",
          "appForm": {...},
          "lastModified": 1234567890,
          "downloadCallBackUrl": "https://..."
        }
      ],
      "readMe": "...",
      "lastModified": 1234567890
    }
  ],
  "extra": {
    "version": "1.10.0",
    "tags": [...]
  }
}
```

The `getAppList()` function downloads this file from `{AppRepo}/{Mode}/1panel.json.zip` and parses it.

**Sources:** [agent/app/service/app.go:890-906](), [agent/app/service/app.go:872-888]()

### Synchronization State Management

The system uses `AppStoreSyncStatus` setting to prevent concurrent syncs:

| Status | Meaning |
|--------|---------|
| `StatusSyncing` | Sync in progress |
| `StatusSyncSuccess` | Last sync succeeded |
| `StatusError` | Last sync failed |

The `appStoreSyncMu` mutex and `appStoreSyncing` boolean at [agent/app/service/app.go:39-41]() ensure only one sync runs at a time.

**Sources:** [agent/app/service/app.go:950-991](), [agent/app/service/app_sync_task.go:70-73]()

---

## Icon Caching System

### Icon File Management

Icons are cached locally with ETag-based validation to minimize downloads:

```mermaid
graph LR
    subgraph "Icon Field Format"
        IconField["app_mysql.png?etag=abc123"]
    end
    
    subgraph "Parsing"
        ParseIconField["ParseIconField()"]
        IconField --> ParseIconField
        ParseIconField --> FileName["fileName: app_mysql.png"]
        ParseIconField --> ETag["etag: abc123"]
    end
    
    subgraph "Storage"
        IconCache["IconCacheDir<br/>/opt/1panel/resource/icon/"]
        FilePath["app_mysql.png"]
        IconCache --> FilePath
    end
    
    subgraph "HTTP Request"
        Request["GET icon URL"]
        ETag --> Request
        Request --> IfNoneMatch["If-None-Match: abc123"]
    end
    
    subgraph "Response Handling"
        Response304["304 Not Modified<br/>Use cached file"]
        Response200["200 OK<br/>Write new file + ETag"]
    end
```

Icon file operations are centralized in the `appicon` package:

- `IsIconFile(icon)` - Check if field contains cached icon: [agent/utils/appicon/appicon.go:16-18]()
- `ParseIconField(icon)` - Extract filename and ETag: [agent/utils/appicon/appicon.go:20-33]()
- `BuildIconField(fileName, etag)` - Construct icon field: [agent/utils/appicon/appicon.go:35-40]()
- `WriteIconFile(appKey, data)` - Save icon to disk: [agent/utils/appicon/appicon.go:52-60]()
- `ReadIconFile(fileName)` - Read icon from disk: [agent/utils/appicon/appicon.go:79-82]()
- `IconFileExists(fileName)` - Check if cached: [agent/utils/appicon/appicon.go:84-88]()

**Sources:** [agent/utils/appicon/appicon.go:1-94](), [agent/app/service/app_sync_task.go:222-271]()

### Icon Download with ETag Caching

The `downloadAppIcon()` method implements conditional HTTP requests:

```go
// From app_sync_task.go:222-271
func (c *appSyncContext) downloadAppIcon(iconUrl, appKey, oldIcon string) (status int, iconField string) {
    iconFileName, existingEtag := appicon.ParseIconField(oldIcon)
    
    reqHeaders := make(map[string]string)
    if existingEtag != "" && iconFileName != "" && appicon.IconFileExists(iconFileName) {
        reqHeaders["If-None-Match"] = existingEtag  // Conditional request
    }
    
    resp, err := req_helper.HandleRequestWithHeaders(&c.httpClient, iconUrl, http.MethodGet, constant.TimeOut20s, reqHeaders)
    
    if resp.StatusCode == http.StatusNotModified {
        return http.StatusNotModified, ""  // Use cached
    }
    
    if resp.StatusCode == http.StatusOK {
        fileName, err := appicon.WriteIconFile(appKey, resp.Body)
        newEtag := resp.Header.Get("ETag")
        iconField = appicon.BuildIconField(fileName, newEtag)
        return http.StatusOK, iconField
    }
}
```

This reduces bandwidth by only downloading icons when they've changed on the server.

**Sources:** [agent/app/service/app_sync_task.go:222-271]()

### Icon API Endpoint

The `/apps/icon/:key` endpoint serves cached icons with HTTP caching headers:

```go
// From app.go:207-235
func (b *BaseApi) GetAppIcon(c *gin.Context) {
    appKey, _ := helper.GetStrParamByKey(c, "key")
    iconBytes, filename, etag, err := appService.GetAppIcon(appKey)
    
    // Set cache control for 30 days
    c.Header("Cache-Control", "public, max-age=2592000")
    
    if etag != "" && filename != "" {
        c.Header("ETag", etag)
        if c.GetHeader("If-None-Match") == etag {
            c.Status(http.StatusNotModified)  // Client has current version
            return
        }
    }
    
    c.Data(http.StatusOK, appicon.ContentTypePNG, iconBytes)
}
```

This enables browser-side caching with ETag validation.

**Sources:** [agent/app/api/v2/app.go:207-235]()

---

## Tag-Based Categorization

### Tag System Architecture

Apps are categorized using a many-to-many tag system:

```mermaid
graph TB
    subgraph "Tag Definitions (from remote)"
        TagData["Tag JSON<br/>{key, translations}"]
    end
    
    subgraph "Database Tables"
        TagTable["tags table<br/>id, key, translations"]
        AppTagTable["app_tags table<br/>app_id, tag_id"]
        AppTable["apps table<br/>id, key, name"]
    end
    
    subgraph "App Properties"
        AppTagsKey["app.TagsKey<br/>[]string"]
    end
    
    TagData -->|SyncTags| TagTable
    AppTagsKey -->|persisted as| AppTagTable
    TagTable -->|references| AppTagTable
    AppTable -->|references| AppTagTable
    
    subgraph "Frontend Query"
        SearchReq["AppSearch.Tags<br/>[]string (tag keys)"]
        SearchReq -->|lookup| TagTable
        TagTable -->|get tag IDs| AppTagTable
        AppTagTable -->|filter| AppTable
    end
```

Tags are defined in the remote app list's `extra.tags` section and synchronized to the database. Each tag has translations for multiple languages.

**Sources:** [agent/app/service/app.go:169-188](), [agent/app/repo/tag.go:1-100]()

### Tag Synchronization

Tags are synchronized before apps during remote sync:

```go
// From app_sync_task.go:92-95
if err = SyncTags(list.Extra); err != nil {
    t.LogFailedWithErr(i18n.GetMsgByKey("SyncTags"), err)
    return err
}
```

The `SyncTags()` function (defined in a helper) parses tag definitions from the remote store and upserts them into the `tags` table.

**Sources:** [agent/app/service/app_sync_task.go:92-95]()

### Tag Filtering in App Search

The `PageApp()` method supports filtering by multiple tags:

```go
// From app.go:91-108
if len(req.Tags) != 0 {
    tags, err := tagRepo.GetByKeys(req.Tags)          // Get tag entities
    var tagIds []uint
    for _, t := range tags {
        tagIds = append(tagIds, t.ID)
    }
    appTags, err := appTagRepo.GetByTagIds(tagIds)    // Get app-tag links
    var appIds []uint
    for _, t := range appTags {
        appIds = append(appIds, t.AppId)
    }
    opts = append(opts, repo.WithByIDs(appIds))       // Filter apps by IDs
}
```

This performs a join between `tags`, `app_tags`, and `apps` tables to find apps matching all specified tags.

**Sources:** [agent/app/service/app.go:91-108]()

### Tag API Endpoint

The `/apps/tags` endpoint returns localized tag names:

```go
// From app.go:169-188
func (a AppService) GetAppTags(ctx *gin.Context) ([]response.TagDTO, error) {
    tags, err := tagRepo.All()
    var res []response.TagDTO
    lang := strings.ToLower(common.GetLang(ctx))  // Get user language
    for _, tag := range tags {
        var translations = make(map[string]string)
        _ = json.Unmarshal([]byte(tag.Translations), &translations)
        if name, ok := translations[lang]; ok {
            tagDTO.Name = name  // Use localized name
        }
        res = append(res, tagDTO)
    }
    return res, nil
}
```

Tags have translations for all supported languages (zh, en, ja, ru, es, etc.) stored as JSON in the `translations` column.

**Sources:** [agent/app/service/app.go:169-188]()

---

## Local App Synchronization

### Local App Directory Structure

Local apps are stored in `global.Dir.LocalAppResourceDir` with this structure:

```
/opt/1panel/resource/apps/local/
├── myapp/
│   ├── metadata.yml       # App metadata
│   ├── 1.0.0/
│   │   ├── docker-compose.yml
│   │   ├── data.yml       # Form parameters
│   │   ├── README.md
│   │   └── scripts/
│   │       ├── init.sh
│   │       ├── upgrade.sh
│   │       └── uninstall.sh
│   └── 1.1.0/
│       └── ...
```

**Sources:** [agent/app/service/app.go:578-808](), [agent/init/dir/dir.go:27-28]()

### Local App Sync Process

```mermaid
sequenceDiagram
    participant API as POST /apps/sync/local
    participant Service as AppService
    participant FS as Local Filesystem
    participant DB as agent.db
    
    API->>Service: SyncAppListFromLocal(taskID)
    Service->>FS: ReadDir(LocalAppResourceDir)
    
    loop For each app directory
        Service->>FS: Read metadata.yml
        Service->>FS: List version subdirectories
        
        loop For each version
            Service->>FS: Read docker-compose.yml
            Service->>FS: Read data.yml (params)
            Service->>Service: Create AppDetail entity
        end
        
        Service->>Service: Create App entity
    end
    
    Service->>Service: Compare with existing local apps
    Service->>Service: Classify: new/update/delete
    
    Service->>DB: BatchCreate(new apps)
    Service->>DB: Save(updated apps)
    Service->>DB: BatchDelete(removed apps)
    Service->>DB: BatchCreate/Update/Delete(app details)
    Service->>DB: Update app_tags
    
    Service-->>API: Sync complete
```

The local sync scans the filesystem for app directories, parses metadata files, and reconciles with the database. Removed apps are marked as `AppTakeDown` status instead of being deleted if they have active installations.

**Sources:** [agent/app/service/app.go:578-808]()

### Local App Metadata Parsing

The `handleLocalApp()` and `handleLocalAppDetail()` functions parse local app metadata:

```go
// Parse app-level metadata (metadata.yml)
func handleLocalApp(appDir string) (*model.App, error) {
    metadataFile := path.Join(appDir, "metadata.yml")
    metadata, err := fileOp.GetContent(metadataFile)
    
    var app model.App
    yaml.Unmarshal(metadata, &app)
    app.Resource = constant.AppResourceLocal
    app.Key = "local" + app.Key  // Prefix with "local"
    return &app, nil
}

// Parse version-level metadata (data.yml, docker-compose.yml)
func handleLocalAppDetail(versionDir string, detail *model.AppDetail) error {
    dataFile := path.Join(versionDir, "data.yml")
    composeFile := path.Join(versionDir, "docker-compose.yml")
    
    dataContent, _ := fileOp.GetContent(dataFile)
    composeContent, _ := fileOp.GetContent(composeFile)
    
    detail.Params = string(dataContent)
    detail.DockerCompose = string(composeContent)
    return nil
}
```

**Sources:** [agent/app/service/app.go:609-635]()

---

## App Search and Filtering

### Search Query Parameters

The `AppSearch` DTO supports multiple filter criteria:

| Field | Type | Description |
|-------|------|-------------|
| `Name` | string | Search in name/description (LIKE query) |
| `Tags` | []string | Filter by tag keys (AND logic) |
| `Type` | string | Filter by app type (app/runtime/php) |
| `Recommend` | bool | Only show recommended apps |
| `Resource` | string | Filter by source (remote/local/all) |
| `ShowCurrentArch` | bool | Only show compatible with current CPU architecture |

**Sources:** [agent/app/dto/request/app.go:9-17]()

### Search Implementation

The `PageApp()` method builds dynamic queries using repository options:

```go
// From app.go:64-166
func (a AppService) PageApp(ctx *gin.Context, req request.AppSearch) (*response.AppRes, error) {
    var opts []repo.DBOption
    opts = append(opts, appRepo.OrderByRecommend())  // Sort by recommend field
    
    if req.Name != "" {
        opts = append(opts, appRepo.WithByLikeName(req.Name))  // LIKE search
    }
    if req.Type != "" {
        opts = append(opts, appRepo.WithType(req.Type))
    }
    if req.Recommend {
        opts = append(opts, appRepo.GetRecommend())  // recommend < 9999
    }
    if req.Resource != "" && req.Resource != "all" {
        opts = append(opts, appRepo.WithResource(req.Resource))
    }
    if req.ShowCurrentArch {
        kernelArch := info.KernelArch  // "amd64" or "arm64"
        opts = append(opts, appRepo.WithArch(kernelArch))
    }
    if len(req.Tags) != 0 {
        // Tag filtering (shown earlier)
    }
    
    total, apps, err := appRepo.Page(req.Page, req.PageSize, opts...)
    // Build response DTOs...
}
```

The `OrderByRecommend()` option sorts by the `recommend` integer field (lower = more recommended).

**Sources:** [agent/app/service/app.go:64-166](), [agent/app/repo/app.go:71-80]()

### Architecture Filtering

When `ShowCurrentArch` is enabled, the system filters apps by CPU architecture:

```go
// From app.go:80-89
if req.ShowCurrentArch {
    info, err := NewIDashboardService().LoadOsInfo()
    kernelArch := info.KernelArch  // "x86_64" or "aarch64"
    if kernelArch == "aarch64" {
        kernelArch = "arm64"
    }
    opts = append(opts, appRepo.WithArch(kernelArch))
}

// From app.go:95-98 (repo implementation)
func (a AppRepo) WithArch(arch string) DBOption {
    return func(g *gorm.DB) *gorm.DB {
        return g.Where("architectures like ?", fmt.Sprintf("%%%s%%", arch))
    }
}
```

Apps have an `architectures` field (comma-separated) like "amd64,arm64" that is matched with LIKE query.

**Sources:** [agent/app/service/app.go:80-89](), [agent/app/repo/app.go:95-99]()

---

## API Endpoints Summary

### App Catalog Endpoints

```mermaid
graph TB
    subgraph "Search and Browse"
        SearchApp["POST /apps/search<br/>PageApp()"]
        GetApp["GET /apps/:key<br/>GetApp()"]
        GetAppDetail["GET /apps/detail/:appId/:version/:type<br/>GetAppDetail()"]
        GetTags["GET /apps/tags<br/>GetAppTags()"]
        GetIcon["GET /apps/icon/:key<br/>GetAppIcon()"]
    end
    
    subgraph "Synchronization"
        SyncRemote["POST /apps/sync/remote<br/>SyncAppListFromRemote()"]
        SyncLocal["POST /apps/sync/local<br/>SyncAppListFromLocal()"]
        CheckUpdate["GET /apps/checkupdate<br/>GetAppUpdate()"]
    end
    
    subgraph "Service Methods"
        AppService["AppService"]
    end
    
    SearchApp --> AppService
    GetApp --> AppService
    GetAppDetail --> AppService
    GetTags --> AppService
    GetIcon --> AppService
    SyncRemote --> AppService
    SyncLocal --> AppService
    CheckUpdate --> AppService
```

**Sources:** [agent/router/ro_app.go:12-27](), [agent/app/api/v2/app.go:1-256]()

### Key Endpoints

| Endpoint | Method | Purpose | Service Method |
|----------|--------|---------|----------------|
| `/apps/search` | POST | Paginated app search with filters | `PageApp()` |
| `/apps/sync/remote` | POST | Trigger remote store sync | `SyncAppListFromRemote()` |
| `/apps/sync/local` | POST | Trigger local app scan | `SyncAppListFromLocal()` |
| `/apps/checkupdate` | GET | Check if remote store has updates | `GetAppUpdate()` |
| `/apps/:key` | GET | Get single app with all versions | `GetApp()` |
| `/apps/detail/:appId/:version/:type` | GET | Get specific app version details | `GetAppDetail()` |
| `/apps/tags` | GET | Get all tags with localized names | `GetAppTags()` |
| `/apps/icon/:key` | GET | Get app icon (cached) | `GetAppIcon()` |

**Sources:** [agent/router/ro_app.go:1-50](), [agent/app/api/v2/app.go:1-256]()

---

## Initialization and Background Sync

### System Startup Synchronization

The app store is synchronized automatically at system startup:

```go
// From init/business/business.go:22-34
func syncApp() {
    if global.CONF.Base.IsOffLine {
        return  // Skip sync in offline mode
    }
    
    // Reset sync status if crashed during previous sync
    setting, err := service.NewISettingService().GetSettingInfo()
    if err == nil && setting.AppStoreSyncStatus == constant.StatusSyncing {
        _ = service.NewISettingService().Update("AppStoreSyncStatus", constant.StatusSyncSuccess)
    }
    
    // Trigger background sync
    if err := service.NewIAppService().SyncAppListFromRemote(""); err != nil {
        global.LOG.Errorf("App Store synchronization failed")
    }
}
```

This runs in a goroutine at startup to ensure the app catalog is up-to-date.

**Sources:** [agent/init/business/business.go:12-34]()

### Offline Mode

When `global.CONF.Base.IsOffLine` is true, remote synchronization is disabled. The system relies on pre-loaded local apps or manually imported app definitions.

**Sources:** [agent/init/business/business.go:23-25](), [agent/app/service/app.go:950-953]()

---

## Key Data Structures

### AppList DTO (from remote store)

```go
type AppList struct {
    LastModified int       `json:"lastModified"`
    Apps         []AppDTO  `json:"apps"`
    Extra        AppExtra  `json:"extra"`
}

type AppDTO struct {
    AppProperty struct {
        Key       string   `json:"key"`
        Name      string   `json:"name"`
        Tags      []string `json:"tags"`
        Recommend int      `json:"recommend"`
        Icon      string   `json:"icon"`  // URL
    } `json:"appProperty"`
    Versions     []VersionDTO `json:"versions"`
    ReadMe       string       `json:"readMe"`
    LastModified int          `json:"lastModified"`
}

type VersionDTO struct {
    Name                string  `json:"name"`
    AppForm             AppForm `json:"appForm"`
    LastModified        int     `json:"lastModified"`
    DownloadCallBackUrl string  `json:"downloadCallBackUrl"`
}
```

This structure represents the remote app store's JSON format.

**Sources:** [agent/app/dto/app.go:1-100]() (referenced but not shown in files)

### Response DTOs

```go
// From response/app.go:12-22
type AppRes struct {
    Items []*AppItem `json:"items"`
    Total int64      `json:"total"`
}

type AppUpdateRes struct {
    CanUpdate            bool         `json:"canUpdate"`
    IsSyncing            bool         `json:"isSyncing"`
    AppStoreLastModified int          `json:"appStoreLastModified"`
    AppList              *dto.AppList `json:"appList"`
}

// From response/app.go:31-44
type AppItem struct {
    ID          uint     `json:"id"`
    Name        string   `json:"name"`
    Key         string   `json:"key"`
    Description string   `json:"description"`
    Installed   bool     `json:"installed"`
    Tags        []string `json:"tags"`
    Type        string   `json:"type"`
    // ... more fields
}
```

**Sources:** [agent/app/dto/response/app.go:12-44]()

---

## Configuration and Directory Structure

### Directory Layout

```
/opt/1panel/
├── resource/
│   ├── icon/                    # Icon cache (IconCacheDir)
│   │   ├── app_mysql.png
│   │   └── app_nginx.png
│   └── apps/
│       ├── remote/              # Remote apps (RemoteAppResourceDir)
│       │   ├── mysql/
│       │   │   └── 8.0.32/
│       │   │       ├── docker-compose.yml
│       │   │       └── scripts/
│       │   └── nginx/
│       ├── local/               # Local apps (LocalAppResourceDir)
│       │   └── custom-app/
│       │       └── 1.0.0/
│       └── custom/              # Custom apps (CustomAppResourceDir)
└── db/
    └── agent.db                 # SQLite database
```

**Sources:** [agent/init/dir/dir.go:23-30](), [agent/global/config.go:36-44]()

### Configuration Settings

Remote app store URL is configured in `global.CONF.RemoteURL`:

```go
type RemoteURL struct {
    AppRepo     string  // e.g., "https://resource.1panel.cn/repo"
    RepoUrl     string
    ResourceUrl string
}
```

App store URLs are constructed as:
- App list: `{AppRepo}/{Mode}/1panel.json.zip`
- Version check: `{AppRepo}/{Mode}/1panel.json.version.txt`
- App package: `{AppRepo}/{Mode}/1panel/{appKey}/{version}/{appKey}-{version}.tar.gz`

**Sources:** [agent/global/config.go:20-24](), [agent/app/service/app.go:820-821]()

---

**Document Summary:** This page covered the App Store and Catalog system including remote/local synchronization, icon caching with ETag support, tag-based categorization, search/filtering capabilities, and the data model for app metadata. The system maintains a local SQLite database of available apps, downloads icons efficiently with HTTP caching, and provides RESTful API endpoints for the frontend to browse and install applications.

---

# Page: App Installation and Deployment

# App Installation and Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/app/api/v2/app.go](agent/app/api/v2/app.go)
- [agent/app/dto/file.go](agent/app/dto/file.go)
- [agent/app/dto/request/app.go](agent/app/dto/request/app.go)
- [agent/app/dto/response/app.go](agent/app/dto/response/app.go)
- [agent/app/repo/app.go](agent/app/repo/app.go)
- [agent/app/service/app.go](agent/app/service/app.go)
- [agent/app/service/app_install.go](agent/app/service/app_install.go)
- [agent/app/service/app_sync_task.go](agent/app/service/app_sync_task.go)
- [agent/app/service/app_utils.go](agent/app/service/app_utils.go)
- [agent/global/config.go](agent/global/config.go)
- [agent/init/business/business.go](agent/init/business/business.go)
- [agent/init/dir/dir.go](agent/init/dir/dir.go)
- [agent/router/ro_app.go](agent/router/ro_app.go)
- [agent/utils/appicon/appicon.go](agent/utils/appicon/appicon.go)
- [agent/utils/files/utils.go](agent/utils/files/utils.go)
- [agent/utils/req_helper/request.go](agent/utils/req_helper/request.go)
- [core/init/cron/cron.go](core/init/cron/cron.go)
- [frontend/src/api/interface/app.ts](frontend/src/api/interface/app.ts)
- [frontend/src/api/modules/app.ts](frontend/src/api/modules/app.ts)
- [frontend/src/components/app-status/index.vue](frontend/src/components/app-status/index.vue)
- [frontend/src/global/form-rules.ts](frontend/src/global/form-rules.ts)
- [frontend/src/styles/common.scss](frontend/src/styles/common.scss)
- [frontend/src/views/app-store/apps/index.vue](frontend/src/views/app-store/apps/index.vue)
- [frontend/src/views/app-store/detail/index.vue](frontend/src/views/app-store/detail/index.vue)
- [frontend/src/views/app-store/detail/install/index.vue](frontend/src/views/app-store/detail/install/index.vue)
- [frontend/src/views/app-store/detail/params/index.vue](frontend/src/views/app-store/detail/params/index.vue)
- [frontend/src/views/app-store/installed/detail/index.vue](frontend/src/views/app-store/installed/detail/index.vue)
- [frontend/src/views/app-store/installed/index.vue](frontend/src/views/app-store/installed/index.vue)
- [frontend/src/views/app-store/installed/upgrade/index.vue](frontend/src/views/app-store/installed/upgrade/index.vue)
- [frontend/src/views/website/website/create/index.vue](frontend/src/views/website/website/create/index.vue)
- [frontend/src/views/website/website/index.vue](frontend/src/views/website/website/index.vue)

</details>



This document describes the application installation and deployment system in 1Panel, covering the dynamic parameter form generation, service dependency injection, Docker Compose integration, and the asynchronous installation workflow. For information about the app store catalog and metadata synchronization, see [App Store and Catalog](#6.1). For operations on already-installed applications (start/stop/restart/upgrade/delete), see [Installed App Operations](#6.3).

---

## Installation Workflow Overview

The app installation process follows a multi-stage workflow that dynamically generates installation forms based on app metadata, validates parameters, injects service dependencies, and executes the installation asynchronously using Docker Compose.

**Installation Flow Diagram**

```mermaid
sequenceDiagram
    participant User
    participant InstallDialog as "Install Dialog<br/>install/index.vue"
    participant AppInstallForm as "AppInstallForm<br/>form/index.vue"
    participant ParamsComponent as "Params Component<br/>params/index.vue"
    participant Backend as "Backend API<br/>/apps/install"
    participant TaskSystem as "Task System"
    participant Docker as "Docker Engine"

    User->>InstallDialog: Click Install on App
    InstallDialog->>AppInstallForm: Load app details
    AppInstallForm->>Backend: GET /apps/detail/{id}/{version}
    Backend-->>AppInstallForm: AppDetail with params
    AppInstallForm->>ParamsComponent: Render formFields
    ParamsComponent->>ParamsComponent: Generate dynamic form
    ParamsComponent->>Backend: GET /apps/services/{key}
    Backend-->>ParamsComponent: Available services
    ParamsComponent-->>User: Display form

    User->>User: Fill parameters
    User->>InstallDialog: Submit installation
    InstallDialog->>InstallDialog: Validate form
    InstallDialog->>Backend: POST /apps/install
    Note over Backend: Create UUID taskID
    Backend->>TaskSystem: Create async task
    Backend-->>InstallDialog: Return taskID
    InstallDialog->>InstallDialog: Open TaskLog component
    
    par Async Installation
        TaskSystem->>Docker: docker-compose up
        Docker-->>TaskSystem: Progress updates
    and UI Polling
        InstallDialog->>Backend: Poll task status
        Backend-->>InstallDialog: Real-time logs
    end
    
    TaskSystem-->>User: Installation complete
```

**Sources:** [frontend/src/views/app-store/detail/install/index.vue:1-140](), [frontend/src/views/app-store/detail/params/index.vue:1-323](), [frontend/src/api/modules/app.ts:36-38]()

---

## Dynamic Parameter Form Generation

The system generates installation forms dynamically from app metadata stored in the `AppDetail.params.formFields` array. Each field descriptor defines the parameter type, validation rules, and rendering behavior.

### Form Field Types

The parameter system supports multiple field types, each rendered with appropriate UI components:

| Field Type | Component | Description | Example Use Case |
|------------|-----------|-------------|------------------|
| `text` | `el-input` | Text input | Application name, domain |
| `password` | `el-input` (password) | Password with visibility toggle | Admin password |
| `number` | `el-input[type=number]` | Numeric input | Port number, replica count |
| `select` | `el-select` | Static dropdown | Timezone selection |
| `service` | `el-select` | Dynamic service selector | MySQL instance selection |
| `apps` | Cascading `el-select` | App-then-service selector | Select app type, then instance |

**Form Field Structure**

```mermaid
classDiagram
    class FromField {
        +string type
        +Locale label
        +Locale description
        +boolean required
        +any default
        +string envKey
        +string key
        +ServiceParam[] values
        +FromFieldChild child
        +FromParam[] params
        +boolean multiple
        +boolean allowCreate
        +string rule
    }

    class FromFieldChild {
        +string type
        +string envKey
        +AppService[] services
    }

    class ServiceParam {
        +string label
        +string value
        +string from
    }

    class FromParam {
        +string type
        +string key
        +string value
        +string envKey
    }

    FromField --> FromFieldChild
    FromField --> ServiceParam
    FromField --> FromParam
```

**Sources:** [frontend/src/api/interface/app.ts:95-130](), [frontend/src/views/app-store/detail/params/index.vue:2-132]()

### Parameter Processing

The `params/index.vue` component processes form fields and generates the UI dynamically:

**Parameter Rendering Logic**

```mermaid
flowchart TD
    Start["handleParams()"] --> IterateFields["Iterate formFields"]
    IterateFields --> CheckType{"Field Type?"}
    
    CheckType -->|"text"| RenderText["Render el-input"]
    CheckType -->|"password"| RenderPassword["Render password input"]
    CheckType -->|"number"| RenderNumber["Render number input"]
    CheckType -->|"select"| RenderSelect["Render el-select with values"]
    CheckType -->|"service"| LoadServices["getAppService(key)"]
    CheckType -->|"apps"| LoadAppServices["Cascading selectors"]
    
    LoadServices --> PopulateServices["Populate service options"]
    LoadAppServices --> LoadChild["Load child services"]
    
    RenderText --> SetDefault["Set default value"]
    RenderPassword --> SetDefault
    RenderNumber --> SetDefault
    RenderSelect --> SetDefault
    PopulateServices --> SetDefault
    LoadChild --> SetDefault
    
    SetDefault --> AddRules{"required?"}
    AddRules -->|Yes| AddValidation["Add Rules.requiredInput"]
    AddRules -->|No| SkipValidation["No validation"]
    AddValidation --> CheckRule{"Has rule?"}
    SkipValidation --> NextField
    CheckRule -->|Yes| AddCustomRule["Add Rules[rule]"]
    CheckRule -->|No| NextField["Process next field"]
    AddCustomRule --> NextField
    
    NextField --> MoreFields{"More fields?"}
    MoreFields -->|Yes| IterateFields
    MoreFields -->|No| EmitUpdate["emit('update:form')"]
```

**Sources:** [frontend/src/views/app-store/detail/params/index.vue:205-259]()

**Random Value Generation**

For fields marked with `random: true`, the system generates unique values:

```mermaid
graph LR
    Field["FormField with random=true"] --> CheckEnvKey{"envKey?"}
    CheckEnvKey -->|"PANEL_DB_NAME"| DBName["default + '_' + getDBName(6)"]
    CheckEnvKey -->|Other| Random["default + '_' + getRandomStr(6)"]
    DBName --> Assign["Assign to form[envKey]"]
    Random --> Assign
```

**Sources:** [frontend/src/views/app-store/detail/params/index.vue:213-221]()

---

## Service Dependency Management

Apps can declare dependencies on other installed applications (typically databases) using the `service` and `apps` field types. The system automatically discovers available service instances and injects connection parameters.

### Service Discovery

**Service Loading Process**

```mermaid
flowchart TD
    Start["Field type = 'service'"] --> CallAPI["getAppService(key)"]
    CallAPI --> CheckNode{"Multi-node?"}
    CheckNode -->|Yes| NodeParam["Add ?operateNode param"]
    CheckNode -->|No| StandardCall["Standard API call"]
    NodeParam --> Execute["GET /apps/services/{key}"]
    StandardCall --> Execute
    
    Execute --> ParseResponse["Parse response"]
    ParseResponse --> MapServices["Map to AppService[]"]
    MapServices --> CheckResults{"Services found?"}
    
    CheckResults -->|Yes| PopulateDropdown["Populate el-select options"]
    CheckResults -->|No| ShowLink["Display 'To Install' link"]
    
    PopulateDropdown --> SelectFirst["Select first service"]
    SelectFirst --> InjectConfig["changeService()"]
    ShowLink --> End
    
    InjectConfig --> IterateConfig["Iterate item.config"]
    IterateConfig --> CheckFormKey{"form[k] exists?"}
    CheckFormKey -->|Yes| AssignValue["form[k] = v"]
    CheckFormKey -->|No| Skip["Skip"]
    AssignValue --> End["Emit update"]
    Skip --> End
```

**AppService Structure**

Each service instance returns connection information:

```typescript
interface AppService {
    label: string;      // Display name (e.g., "mysql-1")
    value: string;      // Service identifier
    config?: Object;    // Connection parameters to inject
    from?: string;      // "local" or "remote"
    status: string;     // "Running", "Stopped", etc.
}
```

**Sources:** [frontend/src/api/interface/app.ts:267-273](), [frontend/src/views/app-store/detail/params/index.vue:261-298](), [frontend/src/api/modules/app.ts:88-91]()

### Database Connection Injection

When a database service is selected, the system automatically injects connection parameters:

**Database-Specific Handling**

For MySQL/MariaDB services, the system additionally loads character set options:

```mermaid
flowchart LR
    SelectDB["Select MySQL/MariaDB"] --> SetFormat["form.format = 'utf8mb4'"]
    SetFormat --> LoadOptions["loadFormatCollations(database)"]
    LoadOptions --> ParseFormats["Parse format options"]
    ParseFormats --> Display["Display format selector"]
    Display --> SelectFormat["User selects format"]
    SelectFormat --> LoadCollations["Load collations for format"]
    LoadCollations --> DisplayCollations["Display collation selector"]
```

**Sources:** [frontend/src/views/app-store/detail/params/index.vue:121-131](), [frontend/src/views/app-store/detail/params/index.vue:308-318]()

### Cascading Service Selection

The `apps` field type creates a two-level selector: first select the app type (e.g., "mysql", "postgresql"), then select a specific instance:

```mermaid
graph TD
    AppField["Field type='apps'"] --> ParentSelect["Parent: Select app type"]
    ParentSelect --> TriggerChange["@change event"]
    TriggerChange --> GetServices["getServices(child.envKey, selectedApp)"]
    GetServices --> ClearChild["Clear child services array"]
    ClearChild --> LoadChild["Load services for selected app"]
    LoadChild --> PopulateChild["Populate child el-select"]
    PopulateChild --> AutoSelect["Auto-select first service"]
    AutoSelect --> InjectParams["Inject params from config"]
```

**Sources:** [frontend/src/views/app-store/detail/params/index.vue:59-118](), [frontend/src/views/app-store/detail/params/index.vue:245-249]()

---

## Advanced Configuration Options

The installation form provides advanced options for resource management, networking, and Docker Compose customization.

### Resource Limits

**CPU and Memory Configuration**

```mermaid
classDiagram
    class AppInstall {
        +number cpuQuota
        +number memoryLimit
        +string memoryUnit
        +string containerName
        +boolean allowPort
        +string specifyIP
        +string restartPolicy
        +boolean editCompose
        +string dockerCompose
    }

    class ResourceLimit {
        +number cpu
        +number memory
    }

    AppInstall --> ResourceLimit : validates against
```

**Validation Rules:**
- CPU Quota: 0-999 cores (0 = unlimited)
- Memory Limit: 0-9999999999 with unit (MB/GB)
- System queries available resources via `loadResourceLimit()` API

**Sources:** [frontend/src/views/app-store/detail/install/index.vue:42-62](), [frontend/src/views/app-store/installed/detail/index.vue:418-431]()

### Port Mapping Configuration

**Port Exposure Options**

```mermaid
flowchart TD
    HostMode{"hostMode?"}
    HostMode -->|Yes| SkipPort["Skip port config<br/>(uses host network)"]
    HostMode -->|No| CheckAllowPort{"allowPort?"}
    
    CheckAllowPort -->|false| DefaultPort["Random port assignment"]
    CheckAllowPort -->|true| EnableIP["Enable specifyIP field"]
    
    EnableIP --> SpecifyIP["User enters IP address"]
    SpecifyIP --> ValidateIP["Validate IPv4/IPv6"]
    ValidateIP --> BindPort["Bind to specific IP:port"]
    
    DefaultPort --> Warning["Show installWarn dialog"]
    Warning --> UserConfirm{"User confirms?"}
    UserConfirm -->|Yes| Proceed["Proceed with installation"]
    UserConfirm -->|No| Cancel["Cancel"]
```

**Sources:** [frontend/src/views/app-store/detail/install/index.vue:90-101](), [frontend/src/views/app-store/installed/detail/index.vue:76-88]()

### Docker Compose Customization

Users can edit the Docker Compose file before installation:

**Compose Editing Workflow**

```mermaid
sequenceDiagram
    participant User
    participant Form as "Installation Form"
    participant Backend as "Backend API"
    participant DiffComponent as "Diff Component"

    User->>Form: Check "Edit Compose"
    Form->>Form: Show CodeMirror editor
    Form->>Form: Load dockerCompose
    
    User->>Form: Click "Show Diff"
    Form->>DiffComponent: Open diff viewer
    DiffComponent->>DiffComponent: Compare original vs edited
    DiffComponent-->>User: Display side-by-side diff
    
    User->>DiffComponent: Modify in diff editor
    DiffComponent-->>Form: Return new compose content
    Form->>Form: Update dockerCompose
    
    User->>Form: Submit installation
    Form->>Backend: POST /apps/install
    Note over Backend: Use custom compose
```

**Sources:** [frontend/src/views/app-store/detail/install/index.vue:78-81](), [frontend/src/views/app-store/installed/detail/index.vue:124-134]()

### Container Restart Policy

Available restart policies mapped to Docker's restart options:

| Policy Value | Docker Behavior |
|--------------|-----------------|
| `no` | Never restart |
| `always` | Always restart |
| `on-failure` | Restart on non-zero exit (maps to `on-failure:5`) |
| `unless-stopped` | Restart unless manually stopped |

**Sources:** [frontend/src/views/app-store/installed/detail/index.vue:89-96](), [frontend/src/views/app-store/installed/detail/index.vue:327-330]()

---

## Multi-Node Deployment

The system supports batch installation to multiple nodes simultaneously (requires Pro license).

**Multi-Node Installation Flow**

```mermaid
flowchart TD
    Start["User initiates install"] --> CheckBatch{"batchInstallSupport?"}
    CheckBatch -->|false| SingleNode["Single node installation"]
    CheckBatch -->|true| ShowNodeSelector["Display node selector"]
    
    ShowNodeSelector --> SelectNodes["User selects target nodes"]
    SelectNodes --> TogglePushNode["Check 'pushNode' option"]
    TogglePushNode --> ValidateSelection{"Nodes selected?"}
    
    ValidateSelection -->|No| Error["Show error"]
    ValidateSelection -->|Yes| PrepareRequest["Build InstallAppToNodes request"]
    
    PrepareRequest --> SetFields["Set appKey, version, nodes[]"]
    SetFields --> CallAPI["POST /core/xpack/sync/app/install"]
    CallAPI --> CreateTasks["Create task per node"]
    CreateTasks --> ParallelInstall["Parallel installation"]
    
    ParallelInstall --> MonitorTasks["Monitor all task logs"]
    MonitorTasks --> Complete["All installations complete"]
    
    SingleNode --> StandardFlow["Standard installApp() flow"]
    StandardFlow --> Complete
```

**InstallAppToNodes Structure**

```typescript
interface InstallAppToNodes extends AppInstall {
    nodes: string[];      // Array of node identifiers
    appKey: string;       // Application key
    version: string;      // Version to install
}
```

**Sources:** [frontend/src/api/interface/app.ts:358-363](), [frontend/src/api/modules/app.ts:140-142](), [frontend/src/views/app-store/detail/install/index.vue:109-111]()

---

## Installation Execution

The actual installation is performed asynchronously using the task system, allowing users to monitor progress without blocking the UI.

### Task Creation and Tracking

**Installation Task Flow**

```mermaid
sequenceDiagram
    participant Form as "Install Form"
    participant API as "Backend API"
    participant TaskQueue as "Task Queue"
    participant AppService as "App Service"
    participant Docker as "Docker"
    participant TaskLog as "TaskLog Component"

    Form->>Form: Generate UUID taskID
    Form->>API: POST /apps/install<br/>{taskID, params, ...}
    API->>TaskQueue: CreateTask(taskID, "App", "TaskInstall")
    TaskQueue-->>API: Task created
    API-->>Form: HTTP 200

    Form->>Form: handleClose()
    Form->>TaskLog: openWithTaskID(taskID)
    TaskLog->>TaskLog: Open drawer
    
    par Async Installation
        AppService->>AppService: Parse parameters
        AppService->>AppService: Generate docker-compose.yml
        AppService->>Docker: docker-compose pull
        Docker-->>TaskQueue: Log progress
        AppService->>Docker: docker-compose up -d
        Docker-->>TaskQueue: Log progress
        AppService->>TaskQueue: Mark complete
    and UI Polling
        loop Every 2 seconds
            TaskLog->>API: GET /tasks/{taskID}
            API->>TaskQueue: Query task status
            TaskQueue-->>API: Return logs & status
            API-->>TaskLog: Update display
        end
    end
    
    TaskQueue-->>TaskLog: status = "Success"
    TaskLog->>TaskLog: Stop polling
    TaskLog-->>Form: Close event
```

**UUID Generation**

The frontend generates a UUID for each installation to track the async operation:

```javascript
const taskID = newUUID();  // Uses v4 UUID
submitData.taskID = taskID;
```

**Sources:** [frontend/src/views/app-store/detail/install/index.vue:103-121](), [frontend/src/api/modules/app.ts:36-38]()

### Installation API Endpoints

| Endpoint | Method | Purpose | Timeout |
|----------|--------|---------|---------|
| `/apps/install` | POST | Single node installation | Default |
| `/core/xpack/sync/app/install` | POST | Multi-node batch installation | Default |

**Request Structure (AppInstall)**

```typescript
interface AppInstall {
    appDetailId: number;    // Version detail ID
    params: any;            // User-provided parameters
    taskID: string;         // UUID for tracking
    name: string;           // Installation name
    cpuQuota?: number;      // CPU limit
    memoryLimit?: number;   // Memory limit
    memoryUnit?: string;    // "M" or "G"
    containerName?: string; // Custom container name
    allowPort?: boolean;    // Enable port binding
    specifyIP?: string;     // IP for port binding
    restartPolicy?: string; // Container restart policy
    editCompose?: boolean;  // Using custom compose
    dockerCompose?: string; // Custom compose content
    pullImage?: boolean;    // Pull images before install
    format?: string;        // DB format (MySQL)
    collation?: string;     // DB collation (MySQL)
}
```

**Sources:** [frontend/src/api/interface/app.ts:133-138](), [frontend/src/views/app-store/detail/install/index.vue:42-62]()

### TaskLog Component Integration

The `TaskLog` component provides real-time installation monitoring:

**TaskLog Opening Methods**

```mermaid
graph LR
    Method1["openWithTaskID(taskID)"] --> Poll1["Poll /tasks/{taskID}"]
    Method2["openWithResourceID(type, name, id)"] --> Lookup["Lookup task by resource"]
    Lookup --> Poll2["Poll task by resource"]
    Poll1 --> Display["Display logs in drawer"]
    Poll2 --> Display
```

**Sources:** [frontend/src/views/app-store/detail/install/index.vue:123-125](), [frontend/src/views/app-store/apps/index.vue:171-173]()

---

## Validation and Error Handling

The system performs client-side validation before submitting installations and provides detailed error feedback.

### Form Validation Rules

**Common Validation Rules Applied**

```mermaid
classDiagram
    class ValidationRules {
        +requiredInput
        +requiredSelect
        +appName
        +port
        +paramCommon
        +paramComplexity
        +containerName
        +ipv4orV6
    }

    class AppNameRule {
        +pattern: /^(?![_-])[a-zA-Z0-9_-]{1,29}[a-zA-Z0-9]$/
        +message: "Invalid app name"
    }

    class PortRule {
        +range: 1-65535
        +type: number
        +message: "Invalid port"
    }

    class ContainerNameRule {
        +pattern: /^[a-zA-Z0-9]{1}[a-zA-Z0-9_.-]{1,127}$/
        +message: "Invalid container name"
    }

    ValidationRules --> AppNameRule
    ValidationRules --> PortRule
    ValidationRules --> ContainerNameRule
```

**Sources:** [frontend/src/global/form-rules.ts:319-330](), [frontend/src/global/form-rules.ts:452-463](), [frontend/src/global/form-rules.ts:509-520]()

### Pre-Installation Validation

**Validation Sequence**

```mermaid
flowchart TD
    Submit["User clicks Confirm"] --> ValidateForm["installFormRef.validate()"]
    ValidateForm --> CheckValid{"Valid?"}
    CheckValid -->|No| ShowErrors["Display field errors"]
    CheckValid -->|Yes| CheckCompose{"editCompose?"}
    
    CheckCompose -->|Yes| CheckEmpty{"dockerCompose empty?"}
    CheckEmpty -->|Yes| ComposeError["MsgError: Compose null"]
    CheckEmpty -->|No| ValidateLimits
    CheckCompose -->|No| ValidateLimits["Validate resource limits"]
    
    ValidateLimits --> ClampCPU["Clamp cpuQuota to 0+"]
    ClampCPU --> ClampMemory["Clamp memoryLimit to 0+"]
    ClampMemory --> CheckHostMode{"isHostMode?"}
    
    CheckHostMode -->|Yes| ProceedInstall["Proceed to install()"]
    CheckHostMode -->|No| CheckAllowPort{"allowPort?"}
    
    CheckAllowPort -->|true| ProceedInstall
    CheckAllowPort -->|false| ShowWarning["ElMessageBox: installWarn"]
    ShowWarning --> UserConfirm{"User confirms?"}
    UserConfirm -->|Yes| ProceedInstall
    UserConfirm -->|No| CancelInstall["Cancel"]
    
    ShowErrors --> End["Stay on form"]
    ComposeError --> End
    CancelInstall --> End
    ProceedInstall --> CallAPI["Call API"]
```

**Sources:** [frontend/src/views/app-store/detail/install/index.vue:72-101]()

### Error Messages

Installation errors are displayed through multiple mechanisms:

**Error Display Paths**

| Error Source | Display Method | Location |
|--------------|----------------|----------|
| Form validation | Inline field errors | Below each field |
| API errors | Toast message | Top-right corner |
| Compose validation | MsgError dialog | Center screen |
| Task failures | TaskLog component | Task log drawer |

**Sources:** [frontend/src/views/app-store/detail/install/index.vue:78-81](), [frontend/src/views/app-store/detail/install/index.vue:103-121]()

---

## Parameter Persistence and Editing

After installation, parameters can be viewed and edited through the installed app detail panel.

**Parameter Edit Workflow**

```mermaid
sequenceDiagram
    participant User
    participant DetailPanel as "App Detail Panel<br/>installed/detail/index.vue"
    participant Backend as "Backend API"
    participant Task as "Task System"

    User->>DetailPanel: Open installed app
    DetailPanel->>Backend: GET /apps/installed/params/{id}
    Backend-->>DetailPanel: Return AppConfig
    DetailPanel->>DetailPanel: Display parameters (read-only)
    
    User->>DetailPanel: Click "Edit" button
    DetailPanel->>DetailPanel: Enable form editing
    DetailPanel->>DetailPanel: Load resource limits
    
    User->>DetailPanel: Modify parameters
    User->>DetailPanel: Check "Advanced" options
    DetailPanel->>DetailPanel: Show advanced fields
    
    User->>DetailPanel: Check "Edit Compose"
    DetailPanel->>DetailPanel: Show compose editor
    User->>DetailPanel: Click "Show Diff"
    DetailPanel->>DetailPanel: Open diff viewer
    
    User->>DetailPanel: Click "Confirm"
    DetailPanel->>DetailPanel: ElMessageBox.confirm
    User->>DetailPanel: Confirm update
    
    DetailPanel->>Backend: POST /apps/installed/params/update
    Backend->>Task: Recreate containers
    Backend-->>DetailPanel: Success
    DetailPanel-->>User: Show success message
```

**Sources:** [frontend/src/views/app-store/installed/detail/index.vue:1-434](), [frontend/src/api/modules/app.ts:102-108]()

### Parameter Modification Restrictions

Some parameters are editable post-installation while others are read-only:

**Editable Parameters:**
- Resource limits (CPU, memory)
- Port bindings (via `allowPort`)
- Restart policy
- Container name
- Docker Compose (via `editCompose`)

**Read-Only Parameters:**
- Installation name
- App key
- Version (requires upgrade operation)
- Environment variables (some may be editable depending on `edit` flag)

**Sources:** [frontend/src/views/app-store/installed/detail/index.vue:42-64](), [frontend/src/api/interface/app.ts:295-309]()

---

## Code Entity Reference

### Key Vue Components

| Component Path | Primary Responsibility |
|----------------|------------------------|
| `frontend/src/views/app-store/detail/install/index.vue` | Main installation dialog, orchestrates installation flow |
| `frontend/src/views/app-store/detail/form/index.vue` | Installation form container (referenced but not provided) |
| `frontend/src/views/app-store/detail/params/index.vue` | Dynamic parameter form generation from metadata |
| `frontend/src/views/app-store/apps/index.vue` | App store listing and search |
| `frontend/src/views/app-store/installed/detail/index.vue` | View/edit installed app parameters |
| `frontend/src/views/app-store/installed/upgrade/index.vue` | App upgrade with compose diff viewing |

### Key API Functions

| Function | Location | Purpose |
|----------|----------|---------|
| `installApp()` | `frontend/src/api/modules/app.ts:36-38` | Install app to single node |
| `installAppToNodes()` | `frontend/src/api/modules/app.ts:140-142` | Install app to multiple nodes (Pro) |
| `getAppDetail()` | `frontend/src/api/modules/app.ts:27-30` | Fetch app version details and params |
| `getAppService()` | `frontend/src/api/modules/app.ts:88-91` | List available service instances |
| `getAppInstallParams()` | `frontend/src/api/modules/app.ts:102-104` | Get installed app configuration |
| `updateAppInstallParams()` | `frontend/src/api/modules/app.ts:106-108` | Update installed app parameters |

### Key TypeScript Interfaces

| Interface | Location | Description |
|-----------|----------|-------------|
| `App.AppInstall` | `frontend/src/api/interface/app.ts:133-138` | Installation request structure |
| `App.AppDetail` | `frontend/src/api/interface/app.ts:72-84` | App version details with params |
| `App.FromField` | `frontend/src/api/interface/app.ts:99-114` | Form field descriptor |
| `App.AppService` | `frontend/src/api/interface/app.ts:267-273` | Service instance descriptor |
| `App.AppConfig` | `frontend/src/api/interface/app.ts:295-309` | Installed app configuration |
| `App.InstallAppToNodes` | `frontend/src/api/interface/app.ts:358-363` | Multi-node installation request |

### Validation Rule Constants

| Rule | Location | Pattern/Range |
|------|----------|---------------|
| `Rules.appName` | `frontend/src/global/form-rules.ts:869-873` | `^(?![_-])[a-zA-Z0-9_-]{1,29}[a-zA-Z0-9]$` |
| `Rules.port` | `frontend/src/global/form-rules.ts:831-838` | 1-65535 |
| `Rules.containerName` | `frontend/src/global/form-rules.ts:874-878` | `^[a-zA-Z0-9]{1}[a-zA-Z0-9_.-]{1,127}$` |
| `checkNumberRange(0, 999)` | `frontend/src/global/form-rules.ts:478-487` | CPU quota validation |

**Sources:** [frontend/src/global/form-rules.ts:698-944]()

---

# Page: Installed App Operations

# Installed App Operations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/app/api/v2/app.go](agent/app/api/v2/app.go)
- [agent/app/dto/file.go](agent/app/dto/file.go)
- [agent/app/dto/request/app.go](agent/app/dto/request/app.go)
- [agent/app/dto/response/app.go](agent/app/dto/response/app.go)
- [agent/app/repo/app.go](agent/app/repo/app.go)
- [agent/app/service/app.go](agent/app/service/app.go)
- [agent/app/service/app_install.go](agent/app/service/app_install.go)
- [agent/app/service/app_sync_task.go](agent/app/service/app_sync_task.go)
- [agent/app/service/app_utils.go](agent/app/service/app_utils.go)
- [agent/global/config.go](agent/global/config.go)
- [agent/init/business/business.go](agent/init/business/business.go)
- [agent/init/dir/dir.go](agent/init/dir/dir.go)
- [agent/router/ro_app.go](agent/router/ro_app.go)
- [agent/utils/appicon/appicon.go](agent/utils/appicon/appicon.go)
- [agent/utils/files/utils.go](agent/utils/files/utils.go)
- [agent/utils/req_helper/request.go](agent/utils/req_helper/request.go)
- [core/init/cron/cron.go](core/init/cron/cron.go)
- [frontend/src/api/interface/app.ts](frontend/src/api/interface/app.ts)
- [frontend/src/api/modules/app.ts](frontend/src/api/modules/app.ts)
- [frontend/src/components/app-status/index.vue](frontend/src/components/app-status/index.vue)
- [frontend/src/global/form-rules.ts](frontend/src/global/form-rules.ts)
- [frontend/src/styles/common.scss](frontend/src/styles/common.scss)
- [frontend/src/views/app-store/apps/index.vue](frontend/src/views/app-store/apps/index.vue)
- [frontend/src/views/app-store/detail/index.vue](frontend/src/views/app-store/detail/index.vue)
- [frontend/src/views/app-store/detail/install/index.vue](frontend/src/views/app-store/detail/install/index.vue)
- [frontend/src/views/app-store/detail/params/index.vue](frontend/src/views/app-store/detail/params/index.vue)
- [frontend/src/views/app-store/installed/detail/index.vue](frontend/src/views/app-store/installed/detail/index.vue)
- [frontend/src/views/app-store/installed/index.vue](frontend/src/views/app-store/installed/index.vue)
- [frontend/src/views/app-store/installed/upgrade/index.vue](frontend/src/views/app-store/installed/upgrade/index.vue)
- [frontend/src/views/website/website/create/index.vue](frontend/src/views/website/website/create/index.vue)
- [frontend/src/views/website/website/index.vue](frontend/src/views/website/website/index.vue)

</details>



## Purpose and Scope

This document describes the operations that can be performed on apps after they have been installed in 1Panel. For information about the initial installation process, see [App Installation and Deployment](#6.2). For details about the app store and catalog, see [App Store and Catalog](#6.1).

Installed app operations encompass lifecycle management (start, stop, restart, rebuild), upgrades with rollback support, parameter modification, and uninstallation with dependency checking. All operations are executed through asynchronous task systems with real-time progress logging.

---

## Operation Overview

The installed apps interface provides a comprehensive set of operations accessible through both the UI and API. Operations are executed asynchronously with task tracking and support automatic status synchronization.

### Available Operations

| Operation | Description | Status Requirements | Rollback Support |
|-----------|-------------|---------------------|------------------|
| `start` | Start stopped containers | Not Running | No |
| `stop` | Stop running containers | Running | No |
| `restart` | Restart containers | Any (except transitional) | No |
| `rebuild` | Rebuild containers from docker-compose | Not in transition | No |
| `upgrade` | Upgrade to a new version | Not in transition | Yes (with backup) |
| `delete` | Uninstall the app | Any | No |
| `params` | Update app parameters | Not in transition | No |
| `favorite` | Toggle favorite status | Any | No |

**Sources:**
- [frontend/src/views/app-store/installed/index.vue:296-376]()
- [agent/app/service/app_install.go:42-58]()

---

## Frontend Interface and User Interaction

### Main Installed Apps View

The installed apps are displayed in a card-based grid layout with real-time status indicators. Each app card provides quick access to common operations through action buttons.

```mermaid
graph TB
    subgraph "Frontend Components"
        IndexView["index.vue<br/>Main installed apps list"]
        AppCard["card.vue<br/>Individual app card"]
        ParamsDialog["detail/index.vue<br/>Parameters editor"]
        UpgradeDialog["upgrade/index.vue<br/>Upgrade interface"]
        DeleteDialog["delete/index.vue<br/>Delete confirmation"]
    end
    
    subgraph "Operation Buttons"
        RebuildBtn["Rebuild Button"]
        RestartBtn["Restart Button"]
        StartBtn["Start Button"]
        StopBtn["Stop Button"]
        UninstallBtn["Uninstall Button"]
        ParamsBtn["Params Button"]
    end
    
    subgraph "API Calls"
        InstalledOpAPI["installedOp()<br/>POST /apps/installed/op"]
        DeleteCheckAPI["appInstalledDeleteCheck()<br/>GET /apps/installed/delete/check/:id"]
        UpdateParamsAPI["updateAppInstallParams()<br/>POST /apps/installed/params/update"]
    end
    
    IndexView --> AppCard
    AppCard --> RebuildBtn
    AppCard --> RestartBtn
    AppCard --> StartBtn
    AppCard --> StopBtn
    AppCard --> UninstallBtn
    AppCard --> ParamsBtn
    
    RebuildBtn --> InstalledOpAPI
    RestartBtn --> InstalledOpAPI
    StartBtn --> InstalledOpAPI
    StopBtn --> InstalledOpAPI
    UninstallBtn --> DeleteCheckAPI
    ParamsBtn --> ParamsDialog
    
    ParamsDialog --> UpdateParamsAPI
```

**Sources:**
- [frontend/src/views/app-store/installed/index.vue:1-469]()
- [frontend/src/api/modules/app.ts:79-82]()

### Operation State Management

The frontend manages operation states including disabled states during transitions and automatic search refresh after operations complete:

```typescript
// Operation disabled during transitional states
disabled: (row: any) => {
    return (
        row.status === 'DownloadErr' ||
        row.status === 'Upgrading' ||
        row.status === 'Rebuilding' ||
        row.status === 'Uninstalling'
    );
}
```

After successful operations, the view automatically refreshes at intervals (3s, 15s) to reflect status changes from asynchronous task execution.

**Sources:**
- [frontend/src/views/app-store/installed/index.vue:296-376]()
- [frontend/src/views/app-store/installed/index.vue:259-280]()

---

## Backend Operation Handler

### Operation Request Processing

All operations are handled through a unified endpoint that dispatches to specific operation handlers based on the `operate` field.

```mermaid
graph TB
    APIEndpoint["POST /apps/installed/op<br/>InstalledOperate()"]
    OperateService["appInstallService.Operate()"]
    
    subgraph "Operation Dispatch"
        StartOp["start<br/>docker compose start"]
        StopOp["stop<br/>docker compose stop"]
        RestartOp["restart<br/>docker compose restart"]
        RebuildOp["rebuild<br/>docker compose up --force-recreate"]
        UpgradeOp["upgrade<br/>upgradeInstall()"]
        DeleteOp["delete<br/>deleteAppInstall()"]
    end
    
    subgraph "Status Updates"
        StatusCheck["syncStatus()<br/>Check container status"]
        DBUpdate["appInstallRepo.Save()<br/>Update app_installs table"]
    end
    
    APIEndpoint --> OperateService
    OperateService --> StartOp
    OperateService --> StopOp
    OperateService --> RestartOp
    OperateService --> RebuildOp
    OperateService --> UpgradeOp
    OperateService --> DeleteOp
    
    StartOp --> StatusCheck
    StopOp --> StatusCheck
    RestartOp --> StatusCheck
    RebuildOp --> StatusCheck
    
    StatusCheck --> DBUpdate
```

**Sources:**
- [agent/app/api/v2/app_installed.go:1-300]()
- [agent/app/service/app_install.go:224-366]()

### Operation Implementation

The `Operate` function in the backend validates the operation and app state before executing:

**Sources:**
- [agent/app/service/app_install.go:224-366]()

---

## Basic Lifecycle Operations

### Start, Stop, and Restart

These operations directly interact with Docker Compose to control container states. They are synchronous and provide immediate status updates.

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant AgentAPI
    participant Compose["compose.Start/Stop/Restart"]
    participant Docker
    participant DB["app_installs table"]
    
    User->>Frontend: Click Start/Stop/Restart
    Frontend->>AgentAPI: POST /apps/installed/op<br/>{operate: "start/stop/restart"}
    
    AgentAPI->>AgentAPI: Load appInstall from DB
    AgentAPI->>AgentAPI: Validate status
    
    alt Start Operation
        AgentAPI->>Compose: compose.Start(composePath)
        Compose->>Docker: docker compose start
    else Stop Operation
        AgentAPI->>Compose: compose.Stop(composePath)
        Compose->>Docker: docker compose stop
    else Restart Operation
        AgentAPI->>Compose: compose.Restart(composePath)
        Compose->>Docker: docker compose restart
    end
    
    Docker-->>Compose: Operation result
    Compose-->>AgentAPI: stdout/stderr
    
    AgentAPI->>AgentAPI: syncStatus()<br/>Query container state
    AgentAPI->>DB: Update status field
    
    AgentAPI-->>Frontend: Success response
    Frontend->>Frontend: Trigger search()<br/>Refresh app list
```

The operations use the docker-compose CLI wrapper functions defined in `agent/utils/compose`:
- `compose.Start()` executes `docker compose -f [path] start`
- `compose.Stop()` executes `docker compose -f [path] stop`
- `compose.Restart()` executes `docker compose -f [path] restart`

After execution, `syncStatus()` queries Docker for the actual container state and updates the database.

**Sources:**
- [agent/app/service/app_install.go:253-283]()
- [agent/utils/compose/compose.go:1-200]()

---

## Rebuild Operation

Rebuild recreates containers from the stored docker-compose configuration, useful for applying configuration changes or recovering from container corruption.

### Rebuild Process Flow

```mermaid
graph TB
    TriggerRebuild["User triggers rebuild"]
    ValidateStatus["Validate app status<br/>Not Upgrading/Rebuilding"]
    SetStatus["Set status = 'Rebuilding'<br/>Save to DB"]
    
    subgraph "Rebuild Task"
        ComposeDown["compose.Down()<br/>Stop and remove containers"]
        ComposeUp["compose.Up()<br/>--force-recreate"]
        CheckStatus["syncStatus()<br/>Verify containers running"]
    end
    
    UpdateSuccess["status = 'Running'<br/>Save to DB"]
    UpdateError["status = 'Error'<br/>message = error details"]
    
    TriggerRebuild --> ValidateStatus
    ValidateStatus --> SetStatus
    SetStatus --> ComposeDown
    ComposeDown --> ComposeUp
    ComposeUp --> CheckStatus
    
    CheckStatus -->|Success| UpdateSuccess
    CheckStatus -->|Failure| UpdateError
```

The rebuild operation forcefully recreates containers even if the image and configuration haven't changed, which is useful for:
- Recovering from corrupted container state
- Applying changes to volumes or networks
- Testing container initialization scripts

**Sources:**
- [agent/app/service/app_install.go:285-324]()

---

## Upgrade Operation

The upgrade operation is the most complex, supporting version changes with automatic backup, rollback capability, and multi-step task execution.

### Upgrade Task Structure

```mermaid
graph TB
    InitUpgrade["upgradeInstall()<br/>Create upgrade task"]
    
    subgraph "Pre-Upgrade Backup (Optional)"
        CreateBackup["backupService.AppBackup()<br/>Create backup archive"]
        ListBackups["List existing upgrade backups"]
        DeleteOld["Delete backups beyond retention<br/>Keep last 3"]
    end
    
    subgraph "Upgrade Execution"
        DownloadNew["Download new app version<br/>if remote resource"]
        CopyFiles["Copy new version files<br/>cp -rn to install dir"]
        UpdateScripts["Update scripts/ directory"]
        StopOld["compose.Down()<br/>Stop current version"]
        UpdateCompose["Generate new docker-compose.yml<br/>handleUpgradeCompose()"]
        WriteEnv["Update .env file"]
        RunUpgradeScript["Execute upgrade script"]
        BuildNginx["buildNginx() if openresty"]
        StartNew["compose.Up()<br/>Start new version"]
    end
    
    subgraph "Rollback on Failure"
        RestoreBackup["backupService.AppRecover()<br/>Restore from backup"]
        RestoreStatus["Restore previous state"]
    end
    
    InitUpgrade --> CreateBackup
    CreateBackup --> ListBackups
    ListBackups --> DeleteOld
    DeleteOld --> DownloadNew
    
    DownloadNew --> CopyFiles
    CopyFiles --> UpdateScripts
    UpdateScripts --> StopOld
    StopOld --> UpdateCompose
    UpdateCompose --> WriteEnv
    WriteEnv --> RunUpgradeScript
    RunUpgradeScript --> BuildNginx
    BuildNginx --> StartNew
    
    StartNew -->|Failure| RestoreBackup
    RestoreBackup --> RestoreStatus
```

**Sources:**
- [agent/app/service/app_utils.go:674-898]()

### Upgrade Compose Handling

During upgrades, the docker-compose file must be updated to use the new version's service definitions while preserving custom user settings:

The `handleUpgradeCompose()` function:
1. Parses the new version's docker-compose YAML
2. Renames the service to match the installed service name if needed
3. Preserves `deploy` and `restart` settings from the old compose file
4. Merges with common parameters (CPU, memory limits, container name)

**Sources:**
- [agent/app/service/app_utils.go:513-602]()

### Version Selection and Update Checking

The frontend provides a version selector that fetches available upgrade versions:

**Sources:**
- [frontend/src/views/app-store/installed/upgrade/index.vue:1-250]()
- [agent/app/service/app_install.go:522-589]()

---

## Parameter Updates

Installed apps can have their parameters (environment variables and compose settings) updated without reinstallation.

### Parameter Update Flow

```mermaid
sequenceDiagram
    participant User
    participant ParamsDialog["detail/index.vue"]
    participant API["updateAppInstallParams"]
    participant Backend["UpdateInstallParams()"]
    participant DB["app_installs table"]
    participant Docker
    
    User->>ParamsDialog: Click Edit
    ParamsDialog->>ParamsDialog: Load current params<br/>getAppInstallParams()
    ParamsDialog->>User: Show editable form
    
    User->>ParamsDialog: Modify parameters<br/>Change values
    User->>ParamsDialog: Click Confirm
    
    ParamsDialog->>API: POST /apps/installed/params/update
    API->>Backend: Process update request
    
    Backend->>Backend: Validate parameters
    Backend->>Backend: Update docker-compose.yml<br/>Apply new env values
    Backend->>Backend: Update .env file
    Backend->>DB: Save updated env/dockerCompose
    
    Backend->>Docker: compose.Down()
    Backend->>Docker: compose.Up()
    
    Backend-->>API: Update successful
    API-->>ParamsDialog: Success response
    ParamsDialog->>ParamsDialog: Close dialog<br/>Refresh list
```

### Advanced Configuration Options

The parameter editor supports advanced Docker configuration options:

| Setting | Purpose | Impact |
|---------|---------|--------|
| `cpuQuota` | CPU core limit | Constrains container CPU usage |
| `memoryLimit` | Memory limit (MB/GB) | Constrains container memory |
| `containerName` | Custom container name | Changes container identifier |
| `allowPort` | Expose ports to host | Publishes container ports |
| `specifyIP` | Bind to specific IP | Restricts port binding |
| `restartPolicy` | Restart behavior | no/always/on-failure/unless-stopped |
| `editCompose` | Direct compose editing | Allows raw YAML modification |

When `editCompose` is enabled, users can directly modify the docker-compose YAML, with a diff viewer to compare against the original:

**Sources:**
- [frontend/src/views/app-store/installed/detail/index.vue:1-350]()
- [agent/app/service/app_install.go:591-676]()

---

## Uninstallation with Dependency Checking

Uninstalling an app involves checking for dependent resources, stopping containers, cleaning up linked databases, and removing files.

### Dependency Check System

Before allowing uninstallation, the system checks if other apps depend on the app being deleted:

```mermaid
graph TB
    DeleteRequest["User clicks Uninstall"]
    CheckDeps["appInstalledDeleteCheck()<br/>GET /apps/installed/delete/check/:id"]
    
    subgraph "Dependency Analysis"
        QueryResources["app_install_resources table<br/>linkId = appInstallID"]
        FindApps["Find apps using this app<br/>via resource links"]
        GetResourceInfo["Collect resource details<br/>database names, types"]
    end
    
    subgraph "UI Decision"
        ShowResources["checkRef.acceptParams()<br/>Display dependency list"]
        ConfirmDelete["User decides:<br/>Force delete or cancel"]
    end
    
    subgraph "Direct Delete"
        NoResources["No dependencies found"]
        ShowDeleteDialog["deleteRef.acceptParams()<br/>Standard delete dialog"]
    end
    
    DeleteRequest --> CheckDeps
    CheckDeps --> QueryResources
    QueryResources --> FindApps
    FindApps --> GetResourceInfo
    
    GetResourceInfo -->|Has dependencies| ShowResources
    GetResourceInfo -->|No dependencies| NoResources
    
    ShowResources --> ConfirmDelete
    NoResources --> ShowDeleteDialog
```

The dependency check identifies resources created by this app that are used by other apps:
- Databases (MySQL, PostgreSQL)
- Runtime environments (PHP, Node.js, etc.)
- Shared volumes or networks

**Sources:**
- [frontend/src/views/app-store/installed/index.vue:229-246]()
- [agent/app/service/app_install.go:678-731]()

### Uninstallation Task Execution

The actual deletion is performed through an asynchronous task with multiple sub-steps:

```mermaid
graph TB
    CreateTask["Create uninstall task<br/>TaskUninstall, TaskScopeApp"]
    
    subgraph "Uninstall Task Steps"
        SetStatus["status = 'Uninstalling'"]
        StopApp["compose.Down()<br/>Stop containers"]
        RunScript["runScript('uninstall')<br/>Execute cleanup script"]
        DeleteImages["Delete Docker images<br/>if deleteImage = true"]
        DeleteFromDB["Delete from app_installs table"]
        DeleteResources["Delete linked resources<br/>app_install_resources"]
        DeleteDBs["Delete created databases<br/>if deleteDB = true"]
        DeleteBackups["Delete backup files<br/>if deleteBackup = true"]
        DeleteFiles["os.RemoveAll(appDir)<br/>Delete installation directory"]
    end
    
    CreateTask --> SetStatus
    SetStatus --> StopApp
    StopApp --> RunScript
    RunScript --> DeleteImages
    DeleteImages --> DeleteFromDB
    DeleteFromDB --> DeleteResources
    DeleteResources --> DeleteDBs
    DeleteDBs --> DeleteBackups
    DeleteBackups --> DeleteFiles
```

Key deletion behaviors:
- `deleteImage`: If true, removes Docker images used by the app (with validation)
- `deleteDB`: If true, deletes created databases and their backups
- `deleteBackup`: If true, removes all backup files from local storage
- `forceDelete`: If true, continues deletion even if errors occur

The task logs all operations for auditing and troubleshooting.

**Sources:**
- [agent/app/service/app_utils.go:333-468]()

### Database Resource Cleanup

When deleting linked databases, the system calls the respective service delete methods:

**Sources:**
- [agent/app/service/app_utils.go:470-511]()

---

## Status Synchronization

### Container Status Monitoring

Apps have multiple status values that reflect their operational state:

| Status | Description | Source |
|--------|-------------|--------|
| `Installing` | Initial installation in progress | Set during installation task |
| `Running` | All containers are running | Synced from Docker |
| `Stopped` | All containers are stopped | Synced from Docker |
| `Error` | Containers in error state | Synced from Docker |
| `Upgrading` | Upgrade operation in progress | Set during upgrade task |
| `Rebuilding` | Rebuild operation in progress | Set during rebuild task |
| `Uninstalling` | Deletion in progress | Set during uninstall task |
| `UpgradeErr` | Upgrade failed | Set on upgrade error |
| `InstallErr` | Installation failed | Set on install error |

### Status Sync Implementation

The `syncStatus()` function queries Docker for the actual container states and updates the database:

```go
func (a *AppInstallService) syncStatus(installId uint) error {
    install, err := appInstallRepo.GetFirst(repo.WithByID(installId))
    
    // Get container names from docker-compose
    containerNames, err := getContainerNames(install)
    
    // Query Docker for container status
    client, _ := docker.NewClient()
    for _, containerName := range containerNames {
        status, _ := client.ContainerStatus(containerName)
        // Aggregate status
    }
    
    install.Status = aggregatedStatus
    return appInstallRepo.Save(context.Background(), &install)
}
```

### Automatic Background Synchronization

The frontend automatically polls the installed apps list to detect status changes:

- Initial load on mount
- Refresh after 1 second (for quick status updates)
- Continuous polling every 30 seconds

This ensures the UI reflects the current state even when operations complete asynchronously.

**Sources:**
- [frontend/src/views/app-store/installed/index.vue:445-468]()
- [agent/app/service/app_install.go:925-1010]()

---

## Favorite and UI Organization

### Favorite Toggle

Apps can be marked as favorites for quick access, persisted in the database:

The favorite operation is handled as a quick toggle without confirmation:

**Sources:**
- [frontend/src/views/app-store/installed/index.vue:248-253]()
- [agent/app/service/app_install.go:48-76]()

### Search and Filtering

The installed apps view supports filtering by:
- Name search (partial match)
- Tag filtering (from app tags)
- Update availability (show only apps with updates)
- Favorite status (sorted first by default)

The default sort order is `favorite DESC` to show favorited apps first.

**Sources:**
- [frontend/src/views/app-store/installed/index.vue:175-227]()
- [agent/app/service/app_install.go:78-153]()

---

## Batch Operations

The website management system demonstrates batch operation patterns that could be applied to app operations in the future:

```mermaid
graph LR
    subgraph "Batch Operation Pattern"
        SelectItems["Select multiple apps"]
        ChooseOp["Choose operation type"]
        Execute["Execute batch operation"]
        TaskLog["Open task log viewer"]
    end
    
    SelectItems --> ChooseOp
    ChooseOp --> Execute
    Execute --> TaskLog
```

While not currently implemented for apps, the infrastructure exists for batch operations on installed apps.

**Sources:**
- [frontend/src/views/website/website/index.vue:655-683]()

---

## Task-Based Progress Tracking

### Task Log Viewer Integration

Most operations (except simple start/stop) open a task log viewer that streams progress in real-time:

```mermaid
graph TB
    Operation["Start operation<br/>(upgrade/rebuild/delete)"]
    CreateTask["Create task with UUID"]
    ReturnTaskID["Return taskID to frontend"]
    
    subgraph "Frontend"
        OpenTaskLog["taskLogRef.openWithTaskID()"]
        StreamSSE["Stream task logs via SSE<br/>GET /tasks/logs/:taskID"]
        DisplayLog["Display real-time progress"]
    end
    
    subgraph "Backend Task Execution"
        ExecuteSteps["Execute task subtasks"]
        LogProgress["t.Log() / t.LogSuccess()"]
        UpdateDB["Update task status in DB"]
    end
    
    Operation --> CreateTask
    CreateTask --> ReturnTaskID
    ReturnTaskID --> OpenTaskLog
    OpenTaskLog --> StreamSSE
    
    ExecuteSteps --> LogProgress
    LogProgress --> UpdateDB
    UpdateDB --> StreamSSE
    StreamSSE --> DisplayLog
```

The task system provides:
- Structured logging with success/failure indicators
- Real-time streaming of progress to frontend
- Persistent task history in the database
- Subtask organization for complex operations

**Sources:**
- [frontend/src/components/log/task/index.vue:1-200]()
- [agent/app/task/task.go:1-300]()

---

## Error Handling and Recovery

### Operation Error Patterns

Different operations have different error handling strategies:

| Operation | Error Handling | Recovery Action |
|-----------|----------------|-----------------|
| Start/Stop/Restart | Immediate failure | Manual retry |
| Rebuild | Status = Error | Manual rebuild or restart |
| Upgrade | Automatic rollback | Restore from backup |
| Delete | Force delete option | Continue despite errors |
| Params | Validation errors | Fix params and retry |

### Upgrade Rollback Mechanism

The upgrade operation implements automatic rollback on failure:

```go
rollBackApp := func(t *task.Task) {
    if req.Backup {
        t.Log("Recovering app...")
        backupService.AppRecover(dto.CommonRecover{
            Name: install.App.Key,
            DetailName: install.Name,
            Type: "app",
            File: backupFile,
        })
    }
}

upgradeTask.AddSubTaskWithOps(
    "upgrade",
    upgradeApp,
    rollBackApp,  // Called on failure
    0,
    1*time.Hour,
)
```

The rollback function restores the app from the pre-upgrade backup if the upgrade fails.

**Sources:**
- [agent/app/service/app_utils.go:871-883]()

---

## Integration with Other Systems

### Container Management Integration

All app operations ultimately interact with the container management system:

- Operations use Docker Compose commands via `agent/utils/compose`
- Container status is queried via Docker API
- Container logs are accessible through the container management UI
- Network and volume management are handled by Docker

Users can navigate from an installed app to its containers using the "To Container" button, which filters the container list by compose project name.

**Sources:**
- [frontend/src/views/app-store/installed/index.vue:382-387]()

### Backup System Integration

Apps integrate with the centralized backup system:

- Backup dialog accessible from app card
- Backups identified by app key and installation name
- Automatic backup creation during upgrades
- Backup retention policies (keep last 3 upgrade backups)

**Sources:**
- [frontend/src/views/app-store/installed/index.vue:389-398]()
- [agent/app/service/app_utils.go:697-716]()

### File Management Integration

Apps provide direct access to their installation directories:

- "To Folder" button opens file manager at app path
- Path format: `/opt/1panel/apps/{appKey}/{appName}`
- File uploads supported for app-specific resources

**Sources:**
- [frontend/src/views/app-store/installed/index.vue:400-407]()

---

## Summary

Installed app operations in 1Panel provide comprehensive lifecycle management through a task-based asynchronous execution system. Key characteristics include:

1. **Unified Operation Handler**: All operations flow through `installedOp` API with operation type dispatch
2. **Task-Based Execution**: Complex operations use the task system for progress tracking and logging
3. **Status Synchronization**: Container states are continuously synced from Docker to the database
4. **Dependency Awareness**: Uninstallation checks and displays dependent resources
5. **Upgrade Rollback**: Automatic backup and recovery on upgrade failures
6. **Parameter Flexibility**: Full control over environment variables and Docker configuration
7. **Integration Points**: Seamless navigation to containers, backups, files, and logs

The architecture separates concerns cleanly between frontend UI state management, backend operation orchestration, and Docker container management, enabling reliable and auditable app operations.

---

# Page: Website Management System

# Website Management System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/app/dto/request/website.go](agent/app/dto/request/website.go)
- [agent/app/dto/response/website.go](agent/app/dto/response/website.go)
- [agent/app/service/website.go](agent/app/service/website.go)
- [agent/app/service/website_utils.go](agent/app/service/website_utils.go)
- [frontend/src/api/interface/website.ts](frontend/src/api/interface/website.ts)
- [frontend/src/api/modules/website.ts](frontend/src/api/modules/website.ts)

</details>



The Website Management System is the core web server management component of 1Panel, providing comprehensive Nginx/OpenResty-based website hosting capabilities. This system handles website creation, configuration, domain management, SSL certificates, reverse proxy setup, and various advanced features like load balancing, anti-leech protection, and authentication.

This document covers website operations and Nginx configuration. For SSL certificate lifecycle management details, see the SSL subsections within this page. For application deployment that creates websites automatically, see [Application Management System](#6).

---

## System Overview

The Website Management System is implemented in the Agent backend service and operates as a high-level abstraction over Nginx/OpenResty. It supports six website types, each with distinct configurations and use cases.

### Core Components

The system is built around three primary service interfaces:

- **`IWebsiteService`** [agent/app/service/website.go:49-132]() - Main website operations interface with 40+ methods
- **Nginx Parser System** - Custom configuration parser for manipulating Nginx config files programmatically
- **WAF Integration** - Web Application Firewall configuration synchronized with website changes
- **Task Execution System** - Asynchronous operations for complex website creation workflows

**Website Types:**

| Type | Constant | Description | Primary Use Case |
|------|----------|-------------|------------------|
| Static | `constant.Static` | Pure HTML/CSS/JS hosting | Static websites, SPAs |
| Runtime | `constant.Runtime` | Language runtime integration | PHP, Node.js, Python, Java, Go, .NET applications |
| Deployment | `constant.Deployment` | App Store application linking | WordPress, Halo, GitLab, etc. |
| Proxy | `constant.Proxy` | Reverse proxy configuration | Microservices, API gateways |
| Stream | `constant.Stream` | TCP/UDP load balancing | Database proxies, game servers |
| Subsite | `constant.Subsite` | Subdirectory within parent site | Multi-tenant hosting |

Sources: [agent/app/service/website.go:49-132](), [agent/app/dto/request/website.go:16-42](), [frontend/src/api/interface/website.ts:3-32]()

---

## Website Type Architecture

```mermaid
graph TB
    subgraph "Website Type Hierarchy"
        Static["Static<br/>constant.Static"]
        Runtime["Runtime<br/>constant.Runtime"]
        Deployment["Deployment<br/>constant.Deployment"]
        Proxy["Proxy<br/>constant.Proxy"]
        Stream["Stream<br/>constant.Stream"]
        Subsite["Subsite<br/>constant.Subsite"]
    end
    
    subgraph "Runtime Subtypes"
        PHP["PHP<br/>constant.RuntimePHP"]
        Node["Node.js<br/>constant.RuntimeNode"]
        Java["Java<br/>constant.RuntimeJava"]
        Go["Go<br/>constant.RuntimeGo"]
        Python["Python<br/>constant.RuntimePython"]
        DotNet[".NET<br/>constant.RuntimeDotNet"]
    end
    
    subgraph "Configuration Components"
        NginxServer["Server Block<br/>components.Server"]
        NginxLocation["Location Block<br/>components.Location"]
        NginxUpstream["Upstream Block<br/>components.Upstream"]
        ProxyPass["proxy_pass Directive"]
        Root["root Directive"]
        PHPProxy["FastCGI PHP Config"]
    end
    
    subgraph "File System Structure"
        SiteDir["/www/sites/{alias}/"]
        IndexDir["/www/sites/{alias}/index/"]
        LogDir["/www/sites/{alias}/log/"]
        SSLDir["/www/sites/{alias}/ssl/"]
        ProxyDir["/www/sites/{alias}/proxy/"]
        RewriteDir["/www/sites/{alias}/rewrite/"]
    end
    
    Static --> NginxServer
    Runtime --> NginxServer
    Deployment --> NginxServer
    Proxy --> NginxServer
    Stream --> NginxUpstream
    Subsite --> NginxServer
    
    Runtime --> PHP
    Runtime --> Node
    Runtime --> Java
    Runtime --> Go
    Runtime --> Python
    Runtime --> DotNet
    
    Static --> Root
    PHP --> PHPProxy
    Node --> ProxyPass
    Java --> ProxyPass
    Go --> ProxyPass
    Python --> ProxyPass
    DotNet --> ProxyPass
    Deployment --> ProxyPass
    Proxy --> ProxyPass
    
    NginxServer --> SiteDir
    SiteDir --> IndexDir
    SiteDir --> LogDir
    SiteDir --> SSLDir
    SiteDir --> ProxyDir
    SiteDir --> RewriteDir
```

**Type-Specific Configurations:**

- **Static**: Uses `server.UpdateRoot()` to point to `/www/sites/{alias}/index` [agent/app/service/website_utils.go:262-264]()
- **Runtime (PHP)**: Configures FastCGI with `server.UpdatePHPProxy()` supporting Unix socket or TCP [agent/app/service/website_utils.go:271-280]()
- **Runtime (Others)**: Reverse proxy to runtime port with `server.UpdateRootProxy()` [agent/app/service/website_utils.go:281-283]()
- **Deployment**: Proxies to app install's `HttpPort` [agent/app/service/website_utils.go:260-261]()
- **Stream**: Creates TCP/UDP upstream blocks without HTTP server context [agent/app/service/website_utils.go:194-232]()
- **Subsite**: Inherits parent website's proxy/runtime configuration [agent/app/service/website_utils.go:285-312]()

Sources: [agent/app/service/website_utils.go:182-325](), [agent/app/service/website.go:241-536]()

---

## Website Creation Workflow

The website creation process uses a task-based system with subtasks for different operations, enabling atomic rollback on failure.

```mermaid
sequenceDiagram
    participant API as "API Handler"
    participant Service as "WebsiteService"
    participant Task as "Task System<br/>task.Task"
    participant FS as "File System"
    participant Nginx as "Nginx Parser"
    participant OpenResty as "OpenResty Container"
    participant DB as "agent.db"
    
    API->>Service: CreateWebsite(req)
    Service->>Service: Validate alias uniqueness
    Service->>Service: Check port availability
    
    Service->>Task: NewTaskWithOps("create", website)
    Task-->>Service: createTask
    
    alt Create Database (if req.CreateDb)
        Service->>Task: AddSubTask("createDatabase")
        Task->>DB: Create MySQL/PostgreSQL DB
        Task->>Service: website.DbID = dbID
    end
    
    alt Install New App (if Deployment + NewApp)
        Service->>Task: Install app via AppService
        Task->>Service: website.AppInstallID = installID
    end
    
    Service->>Task: AddSubTask("ConfigOpenresty")
    Task->>FS: createWebsiteFolder(website)
    FS->>FS: mkdir /www/sites/{alias}
    FS->>FS: Create log/, index/, ssl/ dirs
    FS->>FS: Write index.html or index.php
    
    Task->>Nginx: configDefaultNginx(website, domains)
    Nginx->>Nginx: Parse template (website_default.conf)
    Nginx->>Nginx: Configure server block
    Nginx->>Nginx: Set listen ports + domains
    Nginx->>Nginx: Configure proxy/root/php
    Nginx->>FS: Write /www/server/openresty/conf.d/{alias}.conf
    
    Task->>OpenResty: nginx -t (validate config)
    OpenResty-->>Task: Config OK
    Task->>OpenResty: nginx -s reload
    
    Task->>Task: createWafConfig(website)
    Task->>FS: Update 1pwaf/data/conf/sites.json
    Task->>FS: Copy WAF rules to 1pwaf/data/sites/{alias}
    
    Task->>DB: websiteRepo.Create(website)
    Task->>DB: websiteDomainRepo.BatchCreate(domains)
    DB-->>Task: website.ID
    
    alt Enable SSL (if req.EnableSSL)
        Task->>Task: AddSubTask("EnableSSL")
        Task->>Service: applySSL(website, websiteSSL)
        Task->>Nginx: Configure ssl_certificate paths
        Task->>Nginx: Add HTTPS listen directives
        Task->>OpenResty: nginx -s reload
    end
    
    alt Create FTP User
        Task->>Task: AddSubTask("ConfigFTP")
        Task->>Service: NewIFtpService().Create()
        Task->>Service: website.FtpID = ftpID
    end
    
    Task->>Service: Execute() all subtasks
    Service-->>API: Success / Error
```

**Key Functions:**

- `CreateWebsite()` [agent/app/service/website.go:241-536]() - Main orchestration function
- `configDefaultNginx()` [agent/app/service/website_utils.go:182-325]() - Generates initial Nginx configuration
- `createWebsiteFolder()` [agent/app/service/website_utils.go:133-180]() - Creates directory structure
- `createWafConfig()` [agent/app/service/website_utils.go:410-480]() - Synchronizes WAF settings
- `createIndexFile()` [agent/app/service/website_utils.go:50-98]() - Creates default index.html/index.php

**Rollback Mechanism:**

Each subtask can define a rollback function. If any step fails, `deleteWebsite()` is called to clean up:
```go
deleteWebsite := func(t *task.Task) {
    _ = deleteWebsiteFolder(website)
}
createTask.AddSubTask(i18n.GetMsgByKey("ConfigOpenresty"), configNginx, deleteWebsite)
```

Sources: [agent/app/service/website.go:241-536](), [agent/app/service/website_utils.go:133-325](), [agent/app/service/website_utils.go:410-480]()

---

## Nginx Configuration Management System

1Panel uses a custom Nginx parser that provides programmatic manipulation of Nginx configuration files while preserving formatting and comments.

### Configuration Parser Architecture

```mermaid
graph TB
    subgraph "Parser Layer"
        StringParser["parser.NewStringParser()"]
        FileParser["parser.NewParser(filepath)"]
        ParseResult["components.Config"]
    end
    
    subgraph "Component Types"
        Config["components.Config"]
        Server["components.Server"]
        Location["components.Location"]
        Upstream["components.Upstream"]
        Directive["components.Directive"]
    end
    
    subgraph "Manipulation Operations"
        UpdateListen["server.UpdateListen(port)"]
        UpdateServerName["server.UpdateServerName(domains)"]
        UpdateRoot["server.UpdateRoot(path)"]
        UpdateProxy["server.UpdateRootProxy(proxy)"]
        UpdatePHP["server.UpdatePHPProxy(proxy, path)"]
        UpdateDirective["server.UpdateDirective(name, params)"]
        DeleteDirective["server.RemoveDirective(name)"]
    end
    
    subgraph "Write Operations"
        WriteConfig["nginx.WriteConfig(config, style)"]
        Validate["nginxCheckAndReload()"]
        Rollback["Restore from OldContent"]
    end
    
    FileParser --> ParseResult
    StringParser --> ParseResult
    ParseResult --> Config
    
    Config --> Server
    Server --> Location
    Config --> Upstream
    Server --> Directive
    
    UpdateListen --> Server
    UpdateServerName --> Server
    UpdateRoot --> Server
    UpdateProxy --> Server
    UpdatePHP --> Server
    UpdateDirective --> Server
    DeleteDirective --> Server
    
    Server --> WriteConfig
    WriteConfig --> Validate
    Validate -->|"nginx -t fails"| Rollback
    Validate -->|"nginx -t OK"| OpenResty["nginx -s reload"]
```

**Key Components:**

| Component | Purpose | File Reference |
|-----------|---------|----------------|
| `parser.NewParser()` | Parse existing Nginx config file | [agent/app/service/website_utils.go:619]() |
| `components.Server` | Represents server {} block | [agent/app/service/website_utils.go:244-312]() |
| `components.Location` | Represents location {} block | [agent/app/service/website_utils.go:120-129]() |
| `components.Upstream` | Represents upstream {} block | [agent/app/service/website_utils.go:224-231]() |
| `nginx.WriteConfig()` | Serialize config to file | [agent/app/service/website_utils.go:315-316]() |

### Configuration Scopes and Updates

The system organizes configuration by "scopes" that map to Nginx contexts:

```go
// Example scope-based update
func UpdateNginxConfigByScope(req request.NginxConfigUpdate) error {
    keys := dto.ScopeKeyMap[req.Scope]  // e.g., "gzip" -> ["gzip", "gzip_comp_level"]
    website := websiteRepo.GetFirst(repo.WithByID(req.WebsiteID))
    
    if req.Operate == constant.ConfigDel {
        return deleteNginxConfig(constant.NginxScopeServer, nginxParams, &website)
    }
    
    params := getNginxParams(req.Params, keys)
    return updateNginxConfig(constant.NginxScopeServer, params, &website)
}
```

**Scope Constants:**

- `constant.NginxScopeServer` - Server block directives
- `constant.NginxScopeLocation` - Location block directives
- `constant.NginxScopeUpstream` - Upstream block directives

**Validation with Rollback:**

Every configuration change follows this pattern [agent/app/service/website_utils.go:1061-1076]():

1. Save original config content to `nginxConfig.OldContent`
2. Modify configuration objects in memory
3. Write new config with `nginx.WriteConfig()`
4. Test with `nginx -t` via `nginxCheckAndReload()`
5. On failure: restore original content and reload
6. On success: reload with `nginx -s reload`

Sources: [agent/app/service/website.go:774-820](), [agent/app/service/website_utils.go:182-325](), [agent/app/service/website_utils.go:1061-1076]()

---

## Domain Management

Websites support multiple domains with independent port and SSL configurations per domain.

### Domain Data Model

```mermaid
erDiagram
    Website ||--o{ WebsiteDomain : "has"
    Website {
        uint ID
        string PrimaryDomain
        string Alias
        string Type
        string Protocol
        uint WebsiteSSLID
        bool IPV6
        bool DefaultServer
    }
    WebsiteDomain {
        uint ID
        uint WebsiteID
        string Domain
        int Port
        bool SSL
    }
```

**Domain Operations:**

| Operation | Method | Description |
|-----------|--------|-------------|
| Create | `CreateWebsiteDomain()` [agent/app/service/website_domain.go:11-90]() | Add domains with port/SSL flags |
| Delete | `DeleteWebsiteDomain()` [agent/app/service/website_domain.go:92-141]() | Remove domain and Nginx listen |
| Update | `UpdateWebsiteDomain()` [agent/app/service/website.go:742-772]() | Toggle SSL on specific domain |
| List | `GetWebsiteDomain()` [agent/app/service/website_domain.go:143-148]() | Retrieve all domains for website |

### Domain-Specific SSL Configuration

Each domain can have independent SSL settings. When updating domain SSL status [agent/app/service/website.go:742-772]():

```go
func UpdateWebsiteDomain(req request.WebsiteDomainUpdate) error {
    domain := websiteDomainRepo.GetFirst(repo.WithByID(req.ID))
    domain.SSL = req.SSL
    
    // Update Nginx listen directives
    server := config.FindServers()[0]
    server.DeleteListen(strconv.Itoa(domain.Port))
    
    http3 := isHttp3(server)
    setListen(server, strconv.Itoa(domain.Port), website.IPV6, http3, 
              website.DefaultServer, domain.SSL && website.Protocol == constant.ProtocolHTTPS)
    
    nginx.WriteConfig(config, nginx.IndentedStyle)
    nginxCheckAndReload(...)
}
```

**Listen Directive Generation:**

The `setListen()` function [agent/app/service/website_utils.go:638-654]() creates Nginx listen directives based on:
- Port number
- IPv6 support (`listen [::]:443 ssl`)
- HTTP/3 support (`listen 443 quic`)
- Default server flag (`listen 443 default_server ssl`)
- SSL status (`listen 443 ssl`)

### Multi-Domain Examples

**Scenario 1: Multiple domains, same port, shared SSL**
```
Domain: example.com, Port: 80, SSL: false
Domain: www.example.com, Port: 80, SSL: false
```
Generates:
```nginx
listen 80;
server_name example.com www.example.com;
```

**Scenario 2: Different ports per domain**
```
Domain: api.example.com, Port: 8080, SSL: false
Domain: admin.example.com, Port: 8081, SSL: true
```
Generates:
```nginx
listen 8080;
listen 8081 ssl;
server_name api.example.com admin.example.com;
```

Sources: [agent/app/service/website_domain.go:11-148](), [agent/app/service/website.go:742-772](), [agent/app/service/website_utils.go:588-654]()

---

## SSL Certificate Management

The system integrates ACME protocol support for automated certificate issuance via Let's Encrypt and ZeroSSL, with DNS validation through 50+ providers.

### SSL Configuration Flow

```mermaid
sequenceDiagram
    participant User as "User/API"
    participant Service as "WebsiteService"
    participant SSL as "WebsiteSSL Model"
    participant Parser as "Nginx Parser"
    participant FS as "File System"
    participant Nginx as "OpenResty"
    
    User->>Service: OpWebsiteHTTPS(req)
    
    alt Enable HTTPS
        Service->>Service: Get/Create WebsiteSSL
        Service->>Service: getHttpsPort(websiteID)
        Note over Service: Determine which ports need SSL
        
        Service->>FS: createPemFile(website, websiteSSL)
        FS->>FS: Write fullchain.pem
        FS->>FS: Write privkey.pem
        
        Service->>Parser: applySSL(website, websiteSSL, req)
        Parser->>Parser: Update listen directives with "ssl"
        Parser->>Parser: Set ssl_certificate paths
        Parser->>Parser: Set ssl_protocols [TLSv1.2, TLSv1.3]
        Parser->>Parser: Set ssl_ciphers
        
        alt HTTP Config: HTTPToHTTPS
            Parser->>Parser: Add HTTP->HTTPS redirect
            Parser->>Parser: Keep port 80 listen
            Parser->>Parser: AddHTTP2HTTPS(sslPort)
        end
        
        alt HTTP Config: HTTPSOnly
            Parser->>Parser: Remove port 80 listen
            Parser->>Parser: Remove HTTP redirect
        end
        
        alt HTTP Config: HTTPAlso
            Parser->>Parser: Keep port 80 listen
            Parser->>Parser: Remove HTTP redirect
        end
        
        alt HSTS Enabled
            Parser->>Parser: Add "Strict-Transport-Security" header
        end
        
        alt HTTP/3 Enabled
            Parser->>Parser: Add "listen 443 quic"
            Parser->>Parser: Add "Alt-Svc" header
        end
        
        Service->>Nginx: nginx -t
        Service->>Nginx: nginx -s reload
        Service->>Service: website.Protocol = "https"
        Service->>Service: website.WebsiteSSLID = sslID
        
    else Disable HTTPS
        Service->>Parser: Remove SSL listen directives
        Service->>Parser: Delete ssl_certificate directives
        Service->>Parser: Delete SSL headers
        Service->>Service: website.Protocol = "http"
        Service->>Service: website.WebsiteSSLID = 0
    end
    
    Service->>DB: websiteRepo.Save(website)
```

**SSL/HTTPS Components:**

| Component | Purpose | Storage Location |
|-----------|---------|------------------|
| `fullchain.pem` | Certificate + intermediate chain | `/www/sites/{alias}/ssl/fullchain.pem` |
| `privkey.pem` | Private key | `/www/sites/{alias}/ssl/privkey.pem` |
| `WebsiteSSL` model | Certificate metadata in database | `agent.db` `website_ssl` table |
| SSL configuration | Nginx directives | Within server block in site config |

### HTTPS Configuration Modes

**HttpConfig Options** [agent/app/service/website_utils.go:788-809]():

1. **`HTTPToHTTPS`**: Redirect all HTTP to HTTPS
   ```nginx
   if ($scheme = http) {
       return 301 https://$host:443$request_uri;
   }
   ```

2. **`HTTPSOnly`**: Disable HTTP entirely (remove port 80 listen)

3. **`HTTPAlso`**: Allow both HTTP and HTTPS without redirect

### SSL Protocol Configuration

The system supports configurable SSL protocols and cipher suites [agent/app/service/website_utils.go:832-863]():

**Default SSL Protocols:** `TLSv1.3`, `TLSv1.2`

**Default Cipher Suite:**
```
ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:
ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:
ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:
DHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:
ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-SHA256:
!aNULL:!eNULL:!EXPORT:!DSS:!DES:!RC4:!3DES:!MD5:!PSK:!KRB5:!SRP:!CAMELLIA:!SEED
```

### HSTS Configuration

HTTP Strict Transport Security can be enabled with subdomain support [agent/app/service/website_utils.go:864-875]():

```go
if req.Hsts {
    var hstsValue string
    if req.HstsIncludeSubDomains {
        hstsValue = "\"max-age=31536000; includeSubDomains\""
    } else {
        hstsValue = "\"max-age=31536000\""
    }
    nginxParams = append(nginxParams, dto.NginxParam{
        Name:   "add_header",
        Params: []string{"Strict-Transport-Security", hstsValue},
    })
}
```

### HTTP/3 Support

When HTTP/3 is enabled [agent/app/service/website_utils.go:876-881]():
- Adds `listen 443 quic` directive
- Adds `Alt-Svc: 'h3=":443"; ma=2592000'` header
- Requires OpenResty with QUIC support

Sources: [agent/app/service/website.go:842-1013](), [agent/app/service/website_utils.go:678-887](), [agent/app/service/website_ssl.go]()

---

## Advanced Features

### Reverse Proxy Configuration

The Proxy website type and proxy configuration feature support flexible reverse proxy setups with caching, header manipulation, and CORS.

**Proxy Configuration Structure:**

```mermaid
graph TB
    Website["Website Model"]
    ProxyDir["/www/sites/{alias}/proxy/"]
    RootConf["root.conf<br/>(root location)"]
    NamedConfs["named configs<br/>(custom locations)"]
    
    Website --> ProxyDir
    ProxyDir --> RootConf
    ProxyDir --> NamedConfs
    
    subgraph "Proxy Location Block"
        Location["location {modifier} {match}"]
        ProxyPass["proxy_pass {target}"]
        ProxyHost["proxy_set_header Host"]
        Cache["proxy_cache settings"]
        CORS["CORS headers"]
        SNI["proxy_ssl_name (SNI)"]
    end
    
    RootConf --> Location
    NamedConfs --> Location
    Location --> ProxyPass
    Location --> ProxyHost
    Location --> Cache
    Location --> CORS
    Location --> SNI
```

**Proxy Operations** [agent/app/service/website_proxy.go]():

| Method | Purpose | File Reference |
|--------|---------|----------------|
| `OperateProxy()` | Create/update/enable/disable proxy config | Line 16-200 |
| `GetProxies()` | List all proxy configurations | Line 202-281 |
| `UpdateProxyFile()` | Direct file edit | Line 283-324 |
| `DeleteProxy()` | Remove proxy configuration | Line 412-460 |
| `GetProxyCache()` | Get cache settings | Line 326-365 |
| `UpdateProxyCache()` | Update cache settings | Line 367-410 |

**CORS Configuration:**

Proxy locations can enable CORS with configurable origins, methods, and headers [agent/app/dto/request/website.go:275-282]():

```go
type CorsConfig struct {
    Cors             bool   `json:"cors"`
    AllowOrigins     string `json:"allowOrigins"`     // e.g., "https://example.com"
    AllowMethods     string `json:"allowMethods"`     // e.g., "GET,POST,PUT"
    AllowHeaders     string `json:"allowHeaders"`     // e.g., "Content-Type,Authorization"
    AllowCredentials bool   `json:"allowCredentials"`
    Preflight        bool   `json:"preflight"`        // Handle OPTIONS requests
}
```

### Load Balancing (Upstream)

Websites can configure Nginx upstream blocks for load balancing across multiple backend servers.

**Upstream Configuration:**

```go
type NginxUpstream struct {
    Name      string                    // Upstream block name
    Algorithm string                    // "default", "ip_hash", "least_conn", "random"
    Servers   []NginxUpstreamServer
}

type NginxUpstreamServer struct {
    Server          string  // "192.168.1.10:8080"
    Weight          int     // Load balancing weight
    MaxFails        int     // Max failed attempts before marking down
    FailTimeout     int     // Time to mark server as down
    FailTimeoutUnit string  // "s", "m", "h"
    MaxConns        int     // Max concurrent connections
    Flag            string  // "down", "backup"
}
```

**Load Balancing Methods** [agent/app/service/website_load_balance.go:13-166]():

- **default** (round-robin): Distribute evenly
- **ip_hash**: Client IP-based sticky sessions
- **least_conn**: Route to server with fewest connections
- **random**: Random distribution

### Anti-Leech Protection

Prevents hotlinking by validating referrer headers [agent/app/service/website_anti_leech.go:11-120]():

```go
type LeechConfig struct {
    Enable      bool
    Cache       bool
    CacheTime   int
    CacheUnit   string
    Extends     string      // File extensions: "jpg|png|gif"
    Return      string      // Return code or redirect URL
    ServerNames []string    // Allowed referrer domains
    NoneRef     bool        // Block empty referrer
    LogEnable   bool
    Blocked     bool        // Block or allow listed domains
}
```

Generates Nginx configuration:
```nginx
location ~* \.(jpg|png|gif)$ {
    valid_referers none blocked example.com *.example.com;
    if ($invalid_referer) {
        return 403;
    }
}
```

### Basic Authentication

HTTP Basic Auth at server or path level [agent/app/service/website_auth.go:11-200]():

**Server-Level Auth:**
```nginx
auth_basic "Restricted Area";
auth_basic_user_file /www/sites/{alias}/auth/.htpasswd;
```

**Path-Level Auth:**
```nginx
location /admin {
    auth_basic "Admin Area";
    auth_basic_user_file /www/sites/{alias}/auth/admin/.htpasswd;
}
```

Operations:
- `GetAuthBasics()` - Retrieve auth users for website
- `UpdateAuthBasic()` - Create/update/delete users
- `GetPathAuthBasics()` - List path-specific auth configs
- `UpdatePathAuthBasic()` - Manage path auth

### Rewrite Rules

URL rewriting using Nginx rewrite directives [agent/app/service/website_rewrite.go:10-130]():

The system provides predefined rewrite templates for common CMSes:
- WordPress
- Laravel
- ThinkPHP
- Discuz
- And custom rewrites

Custom rewrite files stored in `/www/sites/{alias}/rewrite/{alias}.conf`

### Redirect Configuration

Manages 301/302 redirects with domain and path matching [agent/app/service/website_redirect.go:13-315]():

**Redirect Types:**
- **Domain**: Redirect entire domain to another
- **Path**: Redirect specific paths
- **Path with regex**: Pattern-based redirects

Example configuration:
```go
type RedirectConfig struct {
    Enable       bool
    Name         string
    Type         string    // "domain", "path"
    Redirect     string    // "301", "302"
    Domains      []string  // Source domains
    Path         string    // Source path
    Target       string    // Destination URL
    KeepPath     bool      // Preserve original path
    RedirectRoot bool      // Apply to root location
}
```

Sources: [agent/app/service/website_proxy.go:16-460](), [agent/app/service/website_load_balance.go:13-166](), [agent/app/service/website_anti_leech.go:11-120](), [agent/app/service/website_auth.go:11-200](), [agent/app/service/website_rewrite.go:10-130](), [agent/app/service/website_redirect.go:13-315]()

---

## Website Operation Lifecycle

### Start/Stop Operations

Websites can be started or stopped without deletion [agent/app/service/website_utils.go:964-1059]():

**Stop Website:**
```go
if operate == constant.StopWeb {
    // Remove proxy includes
    server.RemoveDirective("include", []string{proxyInclude})
    server.RemoveDirective("include", []string{rewriteInclude})
    server.RemoveDirective("include", []string{redirectInclude})
    
    // Remove application location blocks
    server.RemoveDirective("location", []string{"/"})
    
    // Point to stop page
    server.UpdateRoot("/usr/share/nginx/html/stop")
    website.Status = constant.WebStopped
}
```

**Start Website:**
```go
if operate == constant.StartWeb {
    // Restore includes
    server.UpdateDirective("include", []string{proxyInclude})
    server.UpdateDirective("include", []string{rewriteInclude})
    
    // Restore root/proxy configuration based on type
    switch website.Type {
    case constant.Deployment:
        server.UpdateRootProxy([]string{proxy})
    case constant.Static:
        server.UpdateRoot(rootIndex)
    case constant.Runtime:
        server.UpdatePHPProxy([]string{website.Proxy}, localPath)
    }
    
    website.Status = constant.WebRunning
}
```

### Log Management

Each website maintains separate access and error logs [agent/app/service/website.go:1078-1160]():

**Log Operations:**
- `GetLog`: Read log file with pagination
- `EnableLog`: Re-enable logging (writes path to nginx config)
- `DisableLog`: Disable logging (access_log off / error_log /dev/null)
- `DeleteLog`: Truncate log file

Log files located at:
- Access: `/www/sites/{alias}/log/access.log`
- Error: `/www/sites/{alias}/log/error.log`

### Batch Operations

Multiple websites can be operated simultaneously using tasks [agent/app/service/website_op.go:10-165]():

**Supported Batch Operations:**
- Start: `batchOpWebsite("start")`
- Stop: `batchOpWebsite("stop")`
- Restart: `batchOpWebsite("restart")`
- Set Group: `BatchSetGroup()`
- Set HTTPS: `BatchSetHttps()`

Each operation creates a task with subtasks for each website, enabling parallel execution and individual error handling.

Sources: [agent/app/service/website_utils.go:964-1059](), [agent/app/service/website.go:1078-1160](), [agent/app/service/website_op.go:10-165]()

---

## Data Models and Storage

### Core Database Schema

```mermaid
erDiagram
    Website ||--o{ WebsiteDomain : "has domains"
    Website ||--o| WebsiteSSL : "has SSL"
    Website }o--|| WebsiteGroup : "belongs to"
    Website ||--o| AppInstall : "links to (deployment type)"
    Website ||--o| Runtime : "uses (runtime type)"
    Website ||--o| Website : "parent (subsite type)"
    Website ||--o| DatabaseMysql : "links to DB"
    Website ||--o| DatabasePostgresql : "links to DB"
    
    Website {
        uint ID PK
        string Type
        string Alias UK
        string PrimaryDomain
        string Protocol
        string Status
        uint WebsiteGroupID FK
        uint WebsiteSSLID FK
        uint AppInstallID FK
        uint RuntimeID FK
        uint ParentWebsiteID FK
        uint DbID FK
        string DbType
        string Proxy
        string ProxyType
        string SiteDir
        string StreamPorts
        bool IPV6
        bool AccessLog
        bool ErrorLog
        bool DefaultServer
        bool Favorite
        time ExpireDate
    }
    
    WebsiteDomain {
        uint ID PK
        uint WebsiteID FK
        string Domain
        int Port
        bool SSL
    }
    
    WebsiteSSL {
        uint ID PK
        string PrimaryDomain
        string Pem
        string PrivateKey
        string Type
        string Provider
        time ExpireDate
        bool AutoRenew
        uint AcmeAccountID FK
        uint DnsAccountID FK
    }
```

### File System Structure

Each website creates a dedicated directory structure:

```
/www/
├── sites/
│   └── {alias}/                    # Website root (SiteDir)
│       ├── index/                  # Document root (SiteIndexDir)
│       │   ├── index.html          # Default index
│       │   ├── 404.html            # Error page
│       │   └── .user.ini           # PHP open_basedir (if PHP)
│       ├── log/                    # Logs (SiteLogDir)
│       │   ├── access.log
│       │   └── error.log
│       ├── ssl/                    # SSL certificates (SiteSSLDir)
│       │   ├── fullchain.pem
│       │   └── privkey.pem
│       ├── proxy/                  # Proxy configs (SiteProxyDir)
│       │   ├── root.conf
│       │   └── {name}.conf
│       ├── rewrite/                # Rewrite rules (SiteReWriteDir)
│       │   └── {alias}.conf
│       ├── redirect/               # Redirect rules (SiteRedirectDir)
│       │   └── {alias}.conf
│       └── php-pool/               # PHP-FPM socket (if local PHP)
│           └── php-fpm.sock
│
└── server/
    └── openresty/
        └── conf.d/
            ├── {alias}.conf        # Main site config (SiteConf)
            └── stream/
                └── {alias}.conf    # Stream config (StreamConf)
```

**Path Resolution Functions** [agent/app/service/path.go:16-82]():

```go
const (
    SiteDir           = "siteDir"
    SiteIndexDir      = "siteIndexDir"
    SiteLogDir        = "siteLogDir"
    SiteSSLDir        = "siteSSLDir"
    SiteProxyDir      = "siteProxyDir"
    SiteReWriteDir    = "siteRewriteDir"
    SiteRedirectDir   = "siteRedirectDir"
    SiteConf          = "siteConf"
    StreamConf        = "streamConf"
    // ... and more
)

func GetSitePath(website model.Website, pathType string) string {
    // Returns absolute path for requested path type
}
```

### WAF Integration

Web Application Firewall configuration synchronized with website changes [agent/app/service/website_utils.go:352-480]():

**WAF Directory Structure:**
```
/www/server/openresty/1pwaf/
└── data/
    ├── conf/
    │   ├── sites.json          # All websites registry
    │   └── siteConfig.json     # Default rules
    ├── rules/                  # Global rule templates
    │   ├── acl.json
    │   ├── args.json
    │   ├── cookie.json
    │   └── ...
    ├── sites/                  # Per-site configs
    │   └── {alias}/
    │       ├── config.json
    │       └── rules/
    │           ├── acl.json
    │           └── ...
    └── db/                     # Runtime data
        └── sites/
            └── {alias}/
```

**WAF Sync Operations:**
- `createWafConfig()` - Initialize WAF for new website
- `delWafConfig()` - Clean up WAF when deleting website
- `createAllWebsitesWAFConfig()` - Rebuild WAF for all websites

Sources: [agent/app/model/website.go](), [agent/app/service/path.go:16-82](), [agent/app/service/website_utils.go:327-480]()

---

## Frontend API Integration

The frontend communicates with the Website Management System through a comprehensive TypeScript API client.

### API Client Structure

```mermaid
graph LR
    subgraph "Frontend API Layer"
        WebsiteAPI["website.ts<br/>API functions"]
        Interfaces["interface/website.ts<br/>TypeScript types"]
        HTTPClient["http client<br/>Axios wrapper"]
    end
    
    subgraph "Backend Endpoints"
        CreateEndpoint["/websites<br/>POST"]
        SearchEndpoint["/websites/search<br/>POST"]
        OpEndpoint["/websites/operate<br/>POST"]
        DomainEndpoint["/websites/domains<br/>POST"]
        SSLEndpoint["/websites/ssl/*<br/>GET/POST"]
        ConfigEndpoint["/websites/config/*<br/>GET/POST"]
    end
    
    WebsiteAPI --> Interfaces
    WebsiteAPI --> HTTPClient
    
    HTTPClient --> CreateEndpoint
    HTTPClient --> SearchEndpoint
    HTTPClient --> OpEndpoint
    HTTPClient --> DomainEndpoint
    HTTPClient --> SSLEndpoint
    HTTPClient --> ConfigEndpoint
```

### Key API Functions

**Website CRUD** [frontend/src/api/modules/website.ts:9-53]():
```typescript
searchWebsites(req: Website.WebSiteSearch)
createWebsite(req: Website.WebSiteCreateReq)
updateWebsite(req: Website.WebSiteUpdateReq)
deleteWebsite(req: Website.WebSiteDel)
getWebsite(id: number)
opWebsite(req: Website.WebSiteOp)  // start/stop/restart
```

**Domain Management** [frontend/src/api/modules/website.ts:55-69]():
```typescript
listDomains(id: number)
createDomain(req: Website.DomainCreate)
updateDomain(req: Website.DomainUpdate)
deleteDomain(req: Website.DomainDelete)
```

**SSL/HTTPS** [frontend/src/api/modules/website.ts:111-153]():
```typescript
searchSSL(req: ReqPage)
createSSL(req: Website.SSLCreate)
getHTTPSConfig(id: number)
updateHTTPSConfig(req: Website.HTTPSReq)
getDnsResolve(req: Website.DNSResolveReq)  // For DNS validation
```

**Configuration** [frontend/src/api/modules/website.ts:71-77]():
```typescript
getNginxConfig(req: Website.NginxScopeReq)
updateNginxConfig(req: Website.NginxConfigReq)
updateNginxFile(req: Website.NginxUpdate)  // Direct file edit
```

**Advanced Features** [frontend/src/api/modules/website.ts:183-233]():
```typescript
// Proxy
getProxyConfig(req: Website.ProxyReq)
operateProxyConfig(req: Website.ProxyReq)
updateProxyConfigFile(req: Website.ProxyFileUpdate)

// Load Balancing
getLoadBalances(id: number)
createLoadBalance(req: Website.LoadBalanceReq)
updateLoadBalance(req: Website.LoadBalanceReq)

// Authentication
getAuthConfig(req: Website.AuthReq)
operateAuthConfig(req: Website.NginxAuthConfig)

// Redirects
getRedirectConfig(req: Website.WebsiteReq)
operateRedirectConfig(req: Website.WebsiteReq)
```

### Request/Response Types

**Create Request** [frontend/src/api/interface/website.ts:87-112]():
```typescript
interface WebSiteCreateReq {
    type: string                    // Website type
    alias: string                   // Unique identifier
    webSiteGroupId: number
    domains: SubDomain[]
    
    // App deployment
    appType: string                 // "new" | "installed"
    appInstallId: number
    
    // Runtime
    runtimeID: number
    proxyType: string
    
    // Database
    createDB?: boolean
    dbName?: string
    dbPassword?: string
    dbHost?: string
    
    // SSL
    enableSSL: boolean
    SSLID?: number
    
    // Stream
    streamPorts?: string
    algorithm: string
    servers: NginxUpstreamServer[]
}
```

**Website Response** [frontend/src/api/interface/website.ts:34-44]():
```typescript
interface WebsiteDTO extends Website {
    errorLogPath: string
    accessLogPath: string
    sitePath: string
    appName: string
    runtimeName: string
    runtimeType: string
    openBaseDir: boolean
    algorithm: string
    servers: NginxUpstreamServer[]
}
```

### Multi-Node Support

API functions support cross-node operations via `operateNode` parameter [frontend/src/api/modules/website.ts:9-11]():

```typescript
export const searchWebsites = (req: Website.WebSiteSearch, node?: string) => {
    const params = node ? `?operateNode=${node}` : '';
    return http.post<ResPage<Website.WebsiteRes>>(`/websites/search${params}`, req);
};
```

This enables managing websites on remote agent nodes from the master node's UI.

Sources: [frontend/src/api/modules/website.ts:1-384](), [frontend/src/api/interface/website.ts:1-738]()

---

## Summary

The Website Management System provides a comprehensive abstraction layer over Nginx/OpenResty with:

- **6 website types** supporting static hosting, language runtimes, app deployments, reverse proxy, TCP/UDP load balancing, and subsites
- **Custom Nginx parser** enabling programmatic configuration manipulation with automatic validation and rollback
- **Multi-domain support** with per-domain SSL configuration
- **Automated SSL** via ACME protocol with 50+ DNS providers
- **Advanced features** including load balancing, proxy caching, CORS, authentication, anti-leech, redirects, and rewrites
- **Task-based creation** with atomic rollback on failure
- **WAF integration** for web application firewall protection
- **Multi-node operation** for distributed deployments
- **Comprehensive API** with TypeScript type safety

The system manages the complete lifecycle from creation through operation to deletion, handling all Nginx configuration, file system setup, certificate management, and runtime integration automatically.

---

# Page: Website Core Operations

# Website Core Operations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/app/dto/request/website.go](agent/app/dto/request/website.go)
- [agent/app/dto/response/website.go](agent/app/dto/response/website.go)
- [agent/app/service/website.go](agent/app/service/website.go)
- [agent/app/service/website_utils.go](agent/app/service/website_utils.go)
- [frontend/src/api/interface/website.ts](frontend/src/api/interface/website.ts)
- [frontend/src/api/modules/website.ts](frontend/src/api/modules/website.ts)

</details>



## Purpose and Scope

This document describes the fundamental lifecycle operations for websites in the 1Panel system, including creation, deletion, start/stop operations, and the task-based execution framework. For details about specific website types (static, runtime, deployment, proxy, stream, subsite), see [Website Types and Features](#7.2). For Nginx configuration management, see [Nginx Configuration Management](#7.3). For SSL certificate operations, see [SSL Certificate Management](#7.4). For domain operations, see [Domain Management](#7.5).

Website core operations are implemented in the Agent backend service and orchestrate multiple subsystems including Nginx configuration, file system management, database provisioning, and WAF integration.

---

## Website Lifecycle Overview

The website lifecycle consists of four primary operations: creation, operation (start/stop), update, and deletion. All operations interact with the Nginx web server and maintain consistency across configuration files, database records, and file system structures.

```mermaid
stateDiagram-v2
    [*] --> Creating: CreateWebsite
    Creating --> Running: Success
    Creating --> [*]: Failure(Rollback)
    Running --> Stopped: StopWeb
    Stopped --> Running: StartWeb
    Running --> Deleting: DeleteWebsite
    Stopped --> Deleting: DeleteWebsite
    Deleting --> [*]: Success
    
    Running --> Running: UpdateWebsite
    Stopped --> Stopped: UpdateWebsite
    
    note right of Creating
        - Validate parameters
        - Create directory structure
        - Generate Nginx config
        - Optional: Create DB
        - Optional: Enable SSL
        - Optional: Create FTP user
    end note
    
    note right of Running
        - Nginx includes active
        - Proxy/Runtime enabled
        - Logs enabled
    end note
    
    note right of Stopped
        - Nginx includes removed
        - Root set to stop page
        - Logs disabled
    end note
```

**Sources:** [agent/app/service/website.go:241-536](), [agent/app/service/website.go:538-547](), [agent/app/service/website.go:650-740](), [agent/app/service/website_utils.go:964-1062]()

---

## Service Architecture

The website service follows a repository pattern with clear separation between HTTP handlers, service logic, and data access.

```mermaid
graph TB
    Handler["HTTP Handler<br/>website.go (api)"]
    Service["WebsiteService<br/>website.go (service)"]
    Repo["websiteRepo<br/>website.go (repo)"]
    DB[("agent.db<br/>websites table")]
    
    TaskSystem["task.Task<br/>Async Execution"]
    NginxParser["nginx/parser<br/>Config Manipulation"]
    FileOp["files.FileOp<br/>File System"]
    Docker["Docker SDK"]
    WAF["WAF Config<br/>1pwaf/data"]
    
    Handler --> Service
    Service --> Repo
    Repo --> DB
    
    Service --> TaskSystem
    Service --> NginxParser
    Service --> FileOp
    Service --> Docker
    Service --> WAF
    
    subgraph "Supporting Services"
        AppService["AppService"]
        DBService["MysqlService/PostgresqlService"]
        FTPService["FtpService"]
        SSLService["WebsiteSSLRepo"]
    end
    
    Service --> AppService
    Service --> DBService
    Service --> FTPService
    Service --> SSLService
```

**Sources:** [agent/app/service/website.go:46-136](), [agent/app/api/v2/helper/helper.go]()

---

## Website Creation

### Request Structure

Website creation accepts a comprehensive configuration covering all aspects of the site:

| Field | Type | Purpose | Required |
|-------|------|---------|----------|
| `Type` | string | Website type (static, runtime, deployment, proxy, stream, subsite) | Yes |
| `Alias` | string | Unique identifier for the website | Yes |
| `WebsiteGroupID` | uint | Group assignment for organization | Yes |
| `Domains` | []WebsiteDomain | Domain and port configurations | Yes (except stream) |
| `RuntimeID` | uint | PHP/Node/Java runtime reference | Type-dependent |
| `AppInstallID` | uint | Linked application installation | Type-dependent |
| `EnableSSL` | bool | Auto-enable HTTPS after creation | No |
| `CreateDb` | bool | Auto-create database | No |
| `FtpUser` / `FtpPassword` | string | Auto-create FTP account | No |
| `TaskID` | string | Client-provided task tracking ID | No |

**Sources:** [agent/app/dto/request/website.go:16-42](), [frontend/src/api/interface/website.ts:87-112]()

### Task-Based Execution

Website creation uses an asynchronous task system that breaks the operation into multiple subtasks, each with its own rollback handler. This ensures partial failures can be cleanly recovered.

```mermaid
sequenceDiagram
    participant Client
    participant API as "POST /websites"
    participant Service as "WebsiteService"
    participant Task as "task.Task"
    participant DB as "Database"
    participant Nginx as "Nginx Parser"
    participant FS as "File System"
    
    Client->>API: WebsiteCreate request
    API->>Service: CreateWebsite(create)
    
    Service->>Service: Validate alias uniqueness
    Service->>Service: Decode FTP password
    Service->>Task: NewTaskWithOps(taskID)
    
    opt Create Database
        Task->>Task: AddSubTask("CreateDatabase")
        Task->>DB: Create MySQL/PostgreSQL DB
    end
    
    opt Install New App
        Task->>Task: AddSubTask("InstallApp")
        Task->>Service: AppService.Install()
    end
    
    Task->>Task: AddSubTask("ConfigOpenresty")
    Task->>FS: createWebsiteFolder()
    Task->>Nginx: configDefaultNginx()
    Task->>Nginx: nginx -t (validate)
    Task->>Nginx: nginx -s reload
    Task->>FS: createWafConfig()
    Task->>DB: websiteRepo.Create()
    Task->>DB: websiteDomainRepo.BatchCreate()
    
    opt Enable SSL
        Task->>Task: AddSubTaskWithIgnoreErr("EnableSSL")
        Task->>Service: applySSL()
    end
    
    opt Create FTP User
        Task->>Task: AddSubTaskWithIgnoreErr("CreateFTPUser")
        Task->>Service: FtpService.Create()
    end
    
    Task->>Task: Execute()
    Task-->>API: Success/Failure
    API-->>Client: HTTP 200 or Error
```

**Sources:** [agent/app/service/website.go:241-536](), [agent/app/task/task.go]()

### Subtask Breakdown

The task system creates a structured execution plan:

1. **Database Creation** (optional): [agent/app/service/website.go:323-372]()
   - Checks for existing database
   - Creates MySQL/MariaDB or PostgreSQL database
   - Stores `DbID` and `DbType` in website model

2. **App Configuration** (for deployment type): [agent/app/service/website.go:376-406]()
   - Installs new app via `AppService.Install()` if `AppType == "new"`
   - Links existing app if `AppType == "installed"`
   - Sets `website.Proxy` to app's HTTP port

3. **Nginx Configuration**: [agent/app/service/website.go:448-484]()
   - Creates site directory structure via `createWebsiteFolder()`
   - Generates Nginx config via `configDefaultNginx()`
   - Creates WAF configuration via `createWafConfig()`
   - Validates config with `nginx -t`
   - Reloads Nginx with `nginx -s reload`
   - Persists website and domain records to database

4. **SSL Enablement** (optional): [agent/app/service/website.go:492-520]()
   - Uses `AddSubTaskWithIgnoreErr()` so failure doesn't rollback entire operation
   - Applies SSL certificate via `applySSL()`
   - Configures HTTPS redirects

5. **FTP User Creation** (optional): [agent/app/service/website.go:522-533]()
   - Creates FTP user with access to site index directory
   - Uses `AddSubTaskWithIgnoreErr()` for non-critical operation

**Rollback Mechanism**: If the ConfigOpenresty subtask fails after database creation, the rollback handler `deleteWebsite()` removes created directories: [agent/app/service/website.go:486-489]()

**Sources:** [agent/app/service/website.go:317-536](), [agent/app/task/task.go]()

### File System Structure

Each website gets a dedicated directory structure under `/www/sites/<alias>/`:

```
/www/sites/<alias>/
├── index/              # Document root
│   ├── index.html     # Default index (static sites)
│   ├── index.php      # Default index (PHP runtime)
│   └── 404.html       # Error page
├── log/               # Nginx logs
│   ├── access.log
│   └── error.log
├── ssl/               # SSL certificates
│   ├── fullchain.pem
│   └── privkey.pem
├── php-pool/          # PHP-FPM socket (local PHP runtime)
│   └── php-fpm.sock
├── proxy/             # Proxy configurations
│   └── root.conf
├── rewrite/           # Rewrite rules
└── redirect/          # Redirect rules
```

Nginx configuration files are stored separately:
- HTTP sites: `/www/sites/<alias>/nginx/<alias>.conf`
- Stream sites: `/www/sites/<alias>/stream/<alias>.conf`

**Sources:** [agent/app/service/website_utils.go:133-180](), [agent/app/service/website.go:15-44]()

---

## Website Operations (Start/Stop)

The `OpWebsite` function handles start and stop operations by modifying Nginx configuration and database state.

### Stop Operation

When stopping a website, the system:

1. Removes all include directives (proxy, rewrite, redirect)
2. Removes location blocks based on website type
3. Changes root directory to `/usr/share/nginx/html/stop`
4. Updates database status to `constant.WebStopped`

```mermaid
graph LR
    subgraph "Stop Website Flow"
        A["opWebsite(website, StopWeb)"]
        B["getNginxFull(website)"]
        C["Remove include directives"]
        D["Remove location blocks"]
        E["Set root=/usr/share/nginx/html/stop"]
        F["nginx.WriteConfig()"]
        G["Update website.Status=WebStopped"]
        H["websiteRepo.Save()"]
        
        A --> B
        B --> C
        C --> D
        D --> E
        E --> F
        F --> G
        G --> H
    end
```

**Sources:** [agent/app/service/website_utils.go:975-999]()

### Start Operation

When starting a website, the system:

1. Restores include directives if corresponding files exist
2. Recreates location blocks based on website type
3. Updates root directory to actual site path
4. Resets expiration date if expired
5. Updates database status to `constant.WebRunning`

**Type-Specific Start Logic:**

| Website Type | Start Behavior |
|--------------|----------------|
| `Deployment` | Updates proxy location to app's `HttpPort` |
| `Static` | Sets root to index directory, updates root location |
| `Proxy` | Removes root directive (uses proxy includes) |
| `Runtime` | Sets root, updates PHP proxy or runtime proxy |

**Sources:** [agent/app/service/website_utils.go:1000-1058](), [agent/app/service/website.go:538-547]()

---

## Website Deletion

Website deletion is a multi-phase operation that cleans up all associated resources.

```mermaid
graph TB
    Start["DeleteWebsite(req)"]
    
    CheckParent{"Has child<br/>subsites?"}
    DeleteDB{"DeleteDB<br/>flag?"}
    DeleteApp{"DeleteApp<br/>flag?"}
    
    DelNginx["delNginxConfig()<br/>Remove config file"]
    DelWAF["delWafConfig()<br/>Remove WAF config"]
    RemoveDBRecord["Delete from websites table"]
    RemoveDomains["Delete from website_domains table"]
    DelBackups["Delete backup records"]
    CleanUploads["Remove upload directory"]
    
    Start --> CheckParent
    CheckParent -->|Yes| Error["Return ErrParentWebsite"]
    CheckParent -->|No| DeleteDB
    
    DeleteDB -->|Yes| DBService["MysqlService.Delete()<br/>or PostgresqlService.Delete()"]
    DeleteDB -->|No| DeleteApp
    DBService --> DeleteApp
    
    DeleteApp -->|Yes| AppDelete["deleteAppInstall()"]
    DeleteApp -->|No| DelNginx
    AppDelete --> DelNginx
    
    DelNginx --> DelWAF
    DelWAF --> DelBackups
    DelBackups --> RemoveDBRecord
    RemoveDBRecord --> RemoveDomains
    RemoveDomains --> CleanUploads
    CleanUploads --> End["Success"]
```

### Deletion Options

The `WebsiteDelete` request provides several flags:

| Flag | Purpose | Default |
|------|---------|---------|
| `ForceDelete` | Continue even if operations fail | false |
| `DeleteApp` | Delete linked application installation | false |
| `DeleteBackup` | Remove backup records | false |
| `DeleteDB` | Drop associated database | false |

**Parent Website Protection**: Websites with child subsites cannot be deleted until the children are removed first. The error `ErrParentWebsite` returns the list of blocking child sites: [agent/app/service/website.go:655-663]()

**Sources:** [agent/app/service/website.go:650-740](), [agent/app/dto/request/website.go:109-115]()

### Nginx Configuration Cleanup

The `delNginxConfig` function removes the Nginx configuration file and site directory:

1. Removes `/www/sites/<alias>/nginx/<alias>.conf` or stream config
2. Removes `/www/sites/<alias>/` directory
3. Calls `xpack.RemoveTamper(alias)` for tamper protection cleanup
4. Reloads Nginx (with `ForceDelete` flag to ignore reload errors)

**Sources:** [agent/app/service/website_utils.go:482-522]()

### WAF Configuration Cleanup

For websites with WAF enabled (OpenResty >= 1.21.4.3-2-0):

1. Removes website entry from `/www/openresty/1pwaf/data/conf/sites.json`
2. Deletes monitoring database directory `/www/openresty/1pwaf/data/db/sites/<alias>`
3. Removes site-specific rules directory `/www/openresty/1pwaf/data/sites/<alias>`
4. Reloads Nginx

**Sources:** [agent/app/service/website_utils.go:524-575]()

---

## Data Models

### Website Model

The `model.Website` entity stores core website metadata:

```go
type Website struct {
    ID              uint
    Protocol        string  // "http" or "https"
    PrimaryDomain   string
    Type            string  // "static", "runtime", "deployment", "proxy", "stream", "subsite"
    Alias           string  // Unique identifier
    Remark          string
    Status          string  // "running" or "stopped"
    
    // Relationships
    WebsiteGroupID    uint
    AppInstallID      uint
    RuntimeID         uint
    WebsiteSSLID      uint
    ParentWebsiteID   uint
    DbID              uint
    DbType            string
    FtpID             uint
    
    // Configuration
    Proxy             string  // Proxy target (IP:port or unix socket)
    ProxyType         string  // "tcp" or "unix"
    SiteDir           string  // Subdirectory within index/
    DefaultServer     bool
    StreamPorts       string  // For stream type
    
    // Flags
    AccessLog         bool
    ErrorLog          bool
    IPV6              bool
    Favorite          bool
    
    // Dates
    ExpireDate        time.Time
    CreatedAt         time.Time
    UpdatedAt         time.Time
}
```

**Sources:** [agent/app/model/website.go]()

### API Request/Response Types

Key request structures:

- `WebsiteCreate`: Creation parameters [agent/app/dto/request/website.go:16-42]()
- `WebsiteUpdate`: Update parameters [agent/app/dto/request/website.go:99-107]()
- `WebsiteDelete`: Deletion options [agent/app/dto/request/website.go:109-115]()
- `WebsiteOp`: Operation command [agent/app/dto/request/website.go:117-120]()

Key response structures:

- `WebsiteDTO`: Full website details [agent/app/dto/response/website.go:10-24]()
- `WebsiteRes`: List/search result [agent/app/dto/response/website.go:26-47]()
- `WebsitePreInstallCheck`: Pre-creation validation [agent/app/dto/response/website.go:55-60]()

**Sources:** [agent/app/dto/request/website.go](), [agent/app/dto/response/website.go]()

---

## API Endpoints

### Core Operations

| Method | Endpoint | Function | Purpose |
|--------|----------|----------|---------|
| POST | `/websites/search` | `PageWebsite` | Paginated website list with filters |
| POST | `/websites` | `CreateWebsite` | Create new website |
| POST | `/websites/operate` | `OpWebsite` | Start/stop website |
| POST | `/websites/update` | `UpdateWebsite` | Update metadata |
| POST | `/websites/del` | `DeleteWebsite` | Delete website |
| GET | `/websites/{id}` | `GetWebsite` | Get website details |
| GET | `/websites/list` | `GetWebsites` | Simple list for dropdowns |

**Multi-Node Routing**: Endpoints support `?operateNode=<node>` query parameter to route operations to specific agent nodes: [frontend/src/api/modules/website.ts:9-11](), [frontend/src/api/modules/website.ts:26-28]()

**Sources:** [frontend/src/api/modules/website.ts:9-53](), [agent/app/api/v2/website.go]()

### Operation Commands

The `operate` field in `WebsiteOp` accepts:

- `"start"` → `constant.StartWeb`: Start website
- `"stop"` → `constant.StopWeb`: Stop website

These constants map to Nginx configuration changes handled by `opWebsite()`: [agent/app/service/website_utils.go:964-1062]()

**Sources:** [agent/app/service/website.go:538-547](), [agent/app/constant/website.go]()

---

## Pre-Installation Validation

Before creating a website, clients can validate that required services are running:

```mermaid
sequenceDiagram
    participant Client
    participant API as "POST /websites/check"
    participant Service
    participant AppRepo
    
    Client->>API: WebsiteInstallCheckReq<br/>{installIds: [1,2,3]}
    API->>Service: PreInstallCheck(req)
    
    Service->>AppRepo: Get OpenResty app
    Service->>AppRepo: Check OpenResty installation
    
    alt OpenResty not installed
        Service-->>API: [{name, status:"ErrNotInstall"}]
    else OpenResty installed
        loop For each installId
            Service->>AppRepo: Get app installation
            Service->>Service: syncAppInstallStatus()
            Service->>Service: Check status == "running"
        end
        Service-->>API: [{name, status, version, appName}]
    end
    
    API-->>Client: CheckRes[] or null
```

The validation checks:
1. OpenResty (Nginx) is installed
2. All referenced app installations exist and are running
3. Returns detailed status for troubleshooting

If any service is not running, the frontend displays a warning before allowing website creation.

**Sources:** [agent/app/service/website.go:1015-1059](), [frontend/src/api/modules/website.ts:155-157]()

---

## Batch Operations

The system supports batch operations for multiple websites via task-based execution:

### Batch Start/Stop

```typescript
// Frontend API
batchOpreate(req: {
    ids: number[],
    operate: "start" | "stop",
    taskID: string
})
```

The backend creates a parent task with subtasks for each website, allowing parallel execution with individual success/failure tracking.

**Sources:** [frontend/src/api/modules/website.ts:361-363](), [agent/app/service/website.go:129]()

### Batch Group Assignment

```typescript
batchSetGroup(req: {
    ids: number[],
    groupID: number
})
```

Updates the `WebsiteGroupID` for multiple websites in a single transaction.

**Sources:** [frontend/src/api/modules/website.ts:373-375](), [agent/app/dto/request/website.go:128-131]()

---

## Error Handling

Common error scenarios and their handling:

| Error Code | Condition | Resolution |
|------------|-----------|------------|
| `ErrDefaultAlias` | Alias is "default" | Choose different alias |
| `ErrAliasIsExist` | Alias already exists | Choose unique alias |
| `ErrDbUserNotValid` | Database name collision | Choose different database name |
| `ErrNotInstall` | OpenResty not installed | Install OpenResty first |
| `ErrParentWebsite` | Has child subsites | Delete children first |
| `ErrTypePortRange` | Invalid stream ports | Provide valid port range |

Nginx validation failures automatically rollback configuration changes by restoring the old content: [agent/app/service/website_utils.go:1065-1085]()

**Sources:** [agent/app/service/website.go:243-266](), [agent/app/service/website.go:655-663](), [agent/buserr/errors.go]()

---

# Page: Website Types and Features

# Website Types and Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/app/dto/request/website.go](agent/app/dto/request/website.go)
- [agent/app/dto/response/website.go](agent/app/dto/response/website.go)
- [agent/app/service/website.go](agent/app/service/website.go)
- [agent/app/service/website_utils.go](agent/app/service/website_utils.go)
- [frontend/src/api/interface/website.ts](frontend/src/api/interface/website.ts)
- [frontend/src/api/modules/website.ts](frontend/src/api/modules/website.ts)

</details>



## Purpose and Scope

This document describes the six website types supported by 1Panel's website management system and their specific features and configurations. Each website type has distinct characteristics, Nginx configuration patterns, and operational requirements.

For information about website creation and lifecycle operations, see [Website Core Operations](#7.1). For Nginx configuration management details, see [Nginx Configuration Management](#7.3). For SSL certificate setup, see [SSL Certificate Management](#7.4).

---

## Website Type Overview

1Panel supports six distinct website types, each designed for specific use cases. The `type` field in the `model.Website` determines which configuration logic applies.

```mermaid
graph TB
    Website["model.Website"]
    
    Static["constant.Static<br/>Static HTML/CSS/JS"]
    Runtime["constant.Runtime<br/>Dynamic Languages"]
    Deployment["constant.Deployment<br/>App Store Apps"]
    Proxy["constant.Proxy<br/>Reverse Proxy"]
    Stream["constant.Stream<br/>TCP/UDP Load Balancer"]
    Subsite["constant.Subsite<br/>Subdirectory Sites"]
    
    Website --> Static
    Website --> Runtime
    Website --> Deployment
    Website --> Proxy
    Website --> Stream
    Website --> Subsite
    
    Runtime --> PHP["RuntimePHP"]
    Runtime --> Node["RuntimeNode"]
    Runtime --> Java["RuntimeJava"]
    Runtime --> Go["RuntimeGo"]
    Runtime --> Python["RuntimePython"]
    Runtime --> DotNet["RuntimeDotNet"]
```

**Website Type Constants and Usage**

| Type | Constant | Primary Purpose | Protocol |
|------|----------|----------------|----------|
| Static | `constant.Static` | HTML/CSS/JS files | HTTP/HTTPS |
| Runtime | `constant.Runtime` | Dynamic language apps | HTTP/HTTPS |
| Deployment | `constant.Deployment` | App Store applications | HTTP/HTTPS |
| Proxy | `constant.Proxy` | Reverse proxy gateway | HTTP/HTTPS |
| Stream | `constant.Stream` | TCP/UDP load balancing | TCP/UDP |
| Subsite | `constant.Subsite` | Child site under parent | HTTP/HTTPS |

Sources: [agent/app/service/website.go:173-187](), [agent/app/constant/constant.go](), [agent/app/dto/request/website.go:16-42]()

---

## Static Websites

Static websites serve pre-rendered HTML, CSS, JavaScript, and other static assets directly through Nginx without application server processing.

### Configuration Pattern

Static sites use a simple Nginx `root` directive pointing to the index directory. The system creates default `index.html` and `404.html` files.

```mermaid
graph LR
    Request["HTTP Request"]
    Nginx["Nginx Server Block"]
    IndexDir["/www/sites/{alias}/index"]
    IndexFile["index.html"]
    Error404["404.html"]
    
    Request --> Nginx
    Nginx --> IndexDir
    IndexDir --> IndexFile
    IndexDir --> Error404
```

### Creation Logic

When creating a static website, the system:

1. Creates site directory structure: `/www/sites/{alias}/index/`
2. Generates default `index.html` from template
3. Generates `404.html` error page
4. Configures Nginx with `root` directive and `error_page 404 /404.html`

**Nginx Configuration Structure:**

```
server {
    listen 80;
    server_name example.com;
    root /www/sites/example/index;
    error_page 404 /404.html;
    location / {
        # Static file serving
    }
}
```

Sources: [agent/app/service/website_utils.go:58-63](), [agent/app/service/website_utils.go:262-264](), [agent/app/service/website.go:241-264]()

---

## Runtime Websites

Runtime websites execute dynamic code through language-specific runtime environments. The `RuntimeID` field links to a `model.Runtime` that defines the interpreter/compiler.

### Supported Runtime Types

```mermaid
graph TB
    RuntimeWebsite["Website.Type = Runtime<br/>Website.RuntimeID"]
    
    RuntimeModel["model.Runtime<br/>Type + Resource"]
    
    PHP["Type: RuntimePHP<br/>Resource: Appstore/Local"]
    Node["Type: RuntimeNode"]
    Java["Type: RuntimeJava"]
    Go["Type: RuntimeGo"]
    Python["Type: RuntimePython"]
    DotNet["Type: RuntimeDotNet"]
    
    RuntimeWebsite --> RuntimeModel
    RuntimeModel --> PHP
    RuntimeModel --> Node
    RuntimeModel --> Java
    RuntimeModel --> Go
    RuntimeModel --> Python
    RuntimeModel --> DotNet
    
    PHP --> PHPFPM["PHP-FPM Socket<br/>Unix/TCP Proxy"]
    PHP --> PHPContainer["Container Runtime<br/>Port Proxy"]
    
    Node --> PortProxy["127.0.0.1:{port}"]
    Java --> PortProxy
    Go --> PortProxy
    Python --> PortProxy
    DotNet --> PortProxy
```

### PHP Runtime Configuration

PHP runtimes support two proxy modes determined by `ProxyType`:

**Local PHP (Resource: ResourceLocal)**

- `constant.RuntimeProxyUnix`: Unix socket at `/www/sites/{alias}/php-pool/php-fpm.sock`
- `constant.RuntimeProxyTcp`: TCP connection to `127.0.0.1:{port}`

The system creates a `location ~ [^/]\.php(/|$)` block that passes requests to PHP-FPM via `fastcgi_pass`.

**App Store PHP (Resource: ResourceAppstore)**

- Proxy to containerized PHP-FPM at `127.0.0.1:{runtime.Port}`
- Creates `.user.ini` with `open_basedir` restrictions for security

### Non-PHP Runtime Configuration

Node.js, Java, Go, Python, and .NET runtimes all use HTTP proxy mode:

- Website proxies to `127.0.0.1:{port}` where the runtime listens
- Nginx acts as reverse proxy with `proxy_pass http://127.0.0.1:{port}`
- Application manages its own HTTP server

**Runtime Port Selection:**

The `port` field in `request.WebsiteCreate` specifies the listening port for the runtime application.

Sources: [agent/app/service/website.go:408-438](), [agent/app/service/website_utils.go:269-283](), [agent/app/service/website_utils.go:157-166](), [agent/app/service/website_utils.go:403-408]()

---

## Deployment Websites

Deployment websites link to applications installed from the App Store. The `AppInstallID` field references a `model.AppInstall`.

### Architecture

```mermaid
graph LR
    DeploymentWebsite["Website<br/>Type: Deployment<br/>AppInstallID"]
    
    AppInstall["model.AppInstall<br/>HttpPort"]
    
    DockerContainer["Docker Container<br/>App Runtime"]
    
    NginxProxy["Nginx Reverse Proxy<br/>proxy_pass"]
    
    Request["HTTP Request"]
    
    Request --> NginxProxy
    NginxProxy --> DeploymentWebsite
    DeploymentWebsite --> AppInstall
    AppInstall --> DockerContainer
```

### Creation Modes

**New App Installation (`AppType: "new"`)**

When `create.AppType == constant.NewApp`:

1. Install application via `NewIAppService().Install()`
2. Obtain `AppInstall.HttpPort` from installation result
3. Set `website.Proxy = "127.0.0.1:{HttpPort}"`
4. Configure Nginx with `location / { proxy_pass http://127.0.0.1:{HttpPort}; }`

**Existing App Attachment (`AppType: "installed"`)**

When attaching to existing `AppInstallID`:

1. Retrieve existing `model.AppInstall`
2. Extract `HttpPort` from app install
3. Configure identical proxy pattern

### Nginx Configuration

The server block contains:

```
location / {
    proxy_pass http://127.0.0.1:{HttpPort};
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

Sources: [agent/app/service/website.go:375-406](), [agent/app/service/website_utils.go:259-261](), [agent/app/service/website.go:173-181]()

---

## Proxy Websites

Proxy websites function as reverse proxy gateways, forwarding requests to multiple upstream targets through configuration files.

### Directory Structure

Proxy websites maintain configuration files in `/www/sites/{alias}/proxy/`:

```
/www/sites/{alias}/
├── proxy/
│   ├── root.conf       # Default "/" location proxy
│   ├── api.conf        # Custom location proxies
│   └── admin.conf
└── index/              # Optional static fallback
```

### Proxy Configuration System

```mermaid
graph TB
    ProxyWebsite["Website.Type = Proxy"]
    
    ProxyDir["/www/sites/{alias}/proxy/"]
    
    RootConf["root.conf<br/>location ^~ /"]
    CustomConf["*.conf<br/>Custom Locations"]
    
    NginxInclude["include /www/sites/{alias}/proxy/*.conf;"]
    
    CreateProxy["createProxyFile()"]
    
    ProxyWebsite --> ProxyDir
    ProxyDir --> RootConf
    ProxyDir --> CustomConf
    
    CreateProxy --> RootConf
    
    RootConf --> NginxInclude
    CustomConf --> NginxInclude
```

### Default Proxy Configuration

The system generates `root.conf` with:

```
location ^~ / {
    proxy_pass {website.Proxy};
    proxy_set_header Host $host;
}
```

The `website.Proxy` field stores the default upstream (e.g., `http://127.0.0.1:8080`).

### Custom Proxy Locations

Users can create additional proxy configurations through the API (see [Website Core Operations](#7.1)). Each location config file supports:

- Path matching (prefix, regex)
- Upstream URL
- Header manipulation
- Caching configuration
- CORS settings

Sources: [agent/app/service/website_utils.go:100-131](), [agent/app/service/website.go:173-177](), [agent/app/service/website_utils.go:265-268]()

---

## Stream Websites

Stream websites implement TCP/UDP load balancing at Layer 4, distinct from HTTP/HTTPS sites. They use Nginx's stream module with upstream definitions.

### Protocol and Port Configuration

Stream sites are identified by:

- `Protocol: constant.ProtocolStream`
- `StreamPorts`: Comma-separated port list (e.g., "3306,3307,6379")
- `UDP`: Boolean flag for UDP protocol support

```mermaid
graph TB
    StreamWebsite["Website<br/>Type: Stream<br/>Protocol: ProtocolStream"]
    
    Ports["StreamPorts<br/>'3306,3307'"]
    
    StreamConf["/www/server/openresty/conf/conf.d/stream/{alias}.conf"]
    
    Server1["server {<br/>  listen 3306;<br/>  listen 3306 udp;<br/>}"]
    
    Server2["server {<br/>  listen 3307;<br/>}"]
    
    Upstream["upstream {alias} {<br/>  server backend1:3306;<br/>  server backend2:3306;<br/>}"]
    
    ProxyPass["proxy_pass {alias};"]
    
    StreamWebsite --> Ports
    Ports --> StreamConf
    StreamConf --> Server1
    StreamConf --> Server2
    Server1 --> ProxyPass
    Server2 --> ProxyPass
    ProxyPass --> Upstream
```

### Load Balancing Algorithms

Stream websites support standard Nginx upstream algorithms via the `Algorithm` field:

| Algorithm | Nginx Directive | Description |
|-----------|----------------|-------------|
| default | (none) | Round-robin |
| least_conn | `least_conn;` | Least connections |
| ip_hash | `ip_hash;` | Client IP hash |
| hash | `hash $remote_addr;` | Generic hash |

### Upstream Server Configuration

Each server in the upstream supports:

```typescript
interface NginxUpstreamServer {
    server: string;           // "192.168.1.10:3306"
    weight: number;           // Load balancing weight
    maxFails: number;         // Health check failures
    failTimeout: number;      // Timeout duration
    failTimeoutUnit: string;  // "s", "m", "h"
    maxConns: number;         // Max concurrent connections
    flag: string;             // "down", "backup"
}
```

### Stream Configuration Example

```
stream {
    upstream myapp {
        least_conn;
        server 192.168.1.10:3306 weight=3 max_fails=3 fail_timeout=30s;
        server 192.168.1.11:3306 weight=2 max_fails=3 fail_timeout=30s;
        server 192.168.1.12:3306 backup;
    }
    
    server {
        listen 3306;
        listen [::]:3306;       # IPv6 if enabled
        listen 3306 udp;        # If UDP flag set
        
        proxy_pass myapp;
        access_log /www/sites/myapp/log/access.log streamlog;
        error_log /www/sites/myapp/log/error.log;
    }
}
```

### Configuration Flow

1. Parse `StreamPorts` into individual port numbers
2. Validate each port isn't conflicting with Nginx HTTPS port
3. Create `upstream {alias}` block with algorithm and servers
4. Generate `server` blocks for each port with UDP flag if needed
5. Write configuration to stream configuration directory

Sources: [agent/app/service/website.go:290-304](), [agent/app/service/website_utils.go:194-232](), [agent/app/service/website.go:607-646](), [agent/app/dto/request/website.go:44-51]()

---

## Subsite Websites

Subsites are websites that exist as subdirectories of a parent website, sharing the parent's runtime environment and Nginx server block.

### Parent-Child Relationship

```mermaid
graph TB
    ParentWebsite["Parent Website<br/>Type: Static/Runtime<br/>Alias: mainapp"]
    
    IndexDir["/www/sites/mainapp/index/"]
    
    Subsite1["Subsite 1<br/>Type: Subsite<br/>ParentWebsiteID<br/>SiteDir: '/blog'"]
    
    Subsite2["Subsite 2<br/>Type: Subsite<br/>ParentWebsiteID<br/>SiteDir: '/shop'"]
    
    BlogDir["/www/sites/mainapp/index/blog/"]
    ShopDir["/www/sites/mainapp/index/shop/"]
    
    ParentWebsite --> IndexDir
    
    Subsite1 --> BlogDir
    Subsite2 --> ShopDir
    
    IndexDir --> BlogDir
    IndexDir --> ShopDir
```

### Subsite Characteristics

**Key Fields:**

- `ParentWebsiteID`: References parent `model.Website.ID`
- `SiteDir`: Subdirectory path relative to parent index (e.g., "/blog", "/shop/admin")
- `RuntimeID`: Inherited from parent if parent is runtime type

**Domain Configuration:**

Subsites have their own domain names and can be accessed via:
- Parent domain with path: `https://mainapp.com/blog`
- Dedicated subsite domain: `https://blog.mainapp.com`

### Nginx Root Configuration

For subsites, Nginx `root` directive points to:

```
root /www/sites/{parent.Alias}/index{subsite.SiteDir};
```

Example: If parent alias is "mainapp" and subsite SiteDir is "/blog":

```
root /www/sites/mainapp/index/blog;
```

### Runtime Inheritance

**PHP Subsites:**

If parent is PHP runtime:

1. Inherits parent's `website.Proxy` (FPM socket or port)
2. Uses same PHP-FPM configuration
3. Creates `location ~ [^/]\.php(/|$)` block with inherited proxy

**Static Parent:**

If parent is static type:

1. Subsite serves static files from subdirectory
2. No runtime proxy configuration needed

### Deletion Protection

Parent websites cannot be deleted while child subsites exist. The system checks:

```go
parentWebsites, _ := websiteRepo.List(websiteRepo.WithParentID(website.ID))
if len(parentWebsites) > 0 {
    return buserr.WithName("ErrParentWebsite", strings.Join(names, ","))
}
```

Sources: [agent/app/service/website.go:439-446](), [agent/app/service/website_utils.go:284-312](), [agent/app/service/website.go:655-664](), [agent/app/service/website.go:211-216]()

---

## Type-Specific Features Matrix

The following table summarizes feature availability per website type:

| Feature | Static | Runtime | Deployment | Proxy | Stream | Subsite |
|---------|--------|---------|------------|-------|--------|---------|
| SSL/HTTPS | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ |
| Multiple Domains | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| IPv6 Support | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Rewrite Rules | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ |
| Access Logs | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Error Logs | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| PHP Support | ✗ | ✓ | ✗ | ✗ | ✗ | ✓ (inherited) |
| Proxy Config | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ |
| Load Balance | ✗ | ✗ | ✗ | ✗ | ✓ | ✗ |
| WAF Integration | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ |
| Database Link | ✗ | ✓ | ✗ | ✗ | ✗ | ✗ |
| FTP Account | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ |
| Parent Site | N/A | N/A | N/A | N/A | N/A | Required |

Sources: [agent/app/service/website.go:290-536](), [agent/app/service/website_utils.go:182-325]()

---

## Configuration Flow by Type

### Website Creation Configuration Sequence

```mermaid
sequenceDiagram
    participant API as "API Request"
    participant CreateTask as "task.Task"
    participant ConfigDB as "ConfigureDatabase"
    participant ConfigNginx as "configDefaultNginx"
    participant ConfigWAF as "createWafConfig"
    participant ConfigSSL as "applySSL"
    participant SaveDB as "websiteRepo.Create"
    
    API->>CreateTask: NewTaskWithOps()
    
    alt CreateDb = true
        CreateTask->>ConfigDB: Create MySQL/PostgreSQL DB
        ConfigDB->>ConfigDB: Set website.DbID
    end
    
    alt Type = Deployment && AppType = new
        CreateTask->>ConfigDB: NewIAppService().Install()
        ConfigDB->>ConfigDB: Set website.AppInstallID
    end
    
    CreateTask->>ConfigNginx: configDefaultNginx()
    
    alt Type != Stream
        ConfigNginx->>ConfigWAF: createWafConfig()
    end
    
    alt Type = Static
        ConfigNginx->>ConfigNginx: root /www/sites/{alias}/index
    end
    
    alt Type = Runtime
        ConfigNginx->>ConfigNginx: PHP FPM or Port Proxy
    end
    
    alt Type = Deployment
        ConfigNginx->>ConfigNginx: proxy_pass 127.0.0.1:{HttpPort}
    end
    
    alt Type = Proxy
        ConfigNginx->>ConfigNginx: include proxy/*.conf
    end
    
    alt Type = Stream
        ConfigNginx->>ConfigNginx: upstream + stream servers
    end
    
    alt Type = Subsite
        ConfigNginx->>ConfigNginx: Inherit parent runtime
    end
    
    ConfigNginx->>SaveDB: websiteRepo.Create()
    
    alt EnableSSL = true
        CreateTask->>ConfigSSL: applySSL()
        ConfigSSL->>ConfigSSL: Update listen + certificates
    end
```

### Type-Specific Validation

**Static Websites:**
- Domain validation
- Port availability

**Runtime Websites:**
- Runtime existence check via `runtimeRepo.GetFirst()`
- For PHP local: Unix socket or TCP port availability
- For PHP appstore: Container image existence
- For non-PHP: Port specification required

**Deployment Websites:**
- App install existence (if attaching to existing)
- App detail validity (if new installation)
- Docker availability

**Proxy Websites:**
- Valid upstream URL
- Proxy directory creation

**Stream Websites:**
- Port range validation
- No conflict with Nginx HTTPS port
- Upstream server format validation

**Subsite Websites:**
- Parent website existence
- Parent is not itself a subsite
- SiteDir format validation
- Parent directory accessibility

Sources: [agent/app/service/website.go:241-536](), [agent/app/service/website_utils.go:182-325](), [agent/app/service/website.go:1015-1059]()

---

## Database Integration

Websites of type `Runtime` can optionally link to MySQL/MariaDB or PostgreSQL databases. During creation, if `CreateDb: true`:

```mermaid
graph LR
    RuntimeWebsite["Website<br/>Type: Runtime<br/>DbID<br/>DbType"]
    
    CreateDB["Create Database Task"]
    
    MySQLDB["MySQL Database<br/>mysqlRepo"]
    
    PostgresDB["PostgreSQL Database<br/>postgresqlRepo"]
    
    RuntimeWebsite --> CreateDB
    CreateDB --> MySQLDB
    CreateDB --> PostgresDB
    
    MySQLDB --> DbID["Set website.DbID"]
    PostgresDB --> DbID
    
    DbID --> DbType["Set website.DbType"]
```

**Database Creation Parameters:**

From `request.DataBaseConfig`:

- `DbName`: Database name
- `DbUser`: Database user
- `DbPassword`: User password
- `DbHost`: Database server (from `model.Database.Name`)
- `DBFormat`: Character set/collation

The created database credentials are not automatically injected into the runtime environment. Users must manually configure their application to use the database.

Sources: [agent/app/service/website.go:322-372](), [agent/app/dto/request/website.go:73-80]()

---

## Summary

1Panel's website management system supports six distinct types optimized for different deployment scenarios:

- **Static**: Direct file serving for HTML/CSS/JS
- **Runtime**: Dynamic applications in PHP, Node.js, Java, Go, Python, .NET
- **Deployment**: App Store applications with automatic Docker container linking
- **Proxy**: Reverse proxy gateway with multiple upstream configurations
- **Stream**: TCP/UDP load balancing without HTTP parsing
- **Subsite**: Child sites sharing parent runtime and directory structure

Each type has specific Nginx configuration patterns, directory structures, and operational requirements documented in their respective sections above.

Sources: [agent/app/service/website.go](), [agent/app/service/website_utils.go](), [agent/app/dto/request/website.go](), [frontend/src/api/interface/website.ts]()

---

# Page: Nginx Configuration Management

# Nginx Configuration Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/app/dto/request/website.go](agent/app/dto/request/website.go)
- [agent/app/dto/response/website.go](agent/app/dto/response/website.go)
- [agent/app/service/website.go](agent/app/service/website.go)
- [agent/app/service/website_utils.go](agent/app/service/website_utils.go)
- [frontend/src/api/interface/website.ts](frontend/src/api/interface/website.ts)
- [frontend/src/api/modules/website.ts](frontend/src/api/modules/website.ts)

</details>



This document describes the Nginx configuration management system within the 1Panel website management platform. It covers template-based configuration generation, scope-based parameter management, modular configuration features (proxy, rewrite, auth, cache), validation mechanisms, and file-level configuration editing.

For information about SSL certificate configuration, see [SSL Certificate Management](#5.4). For domain-level configuration, see [Domain Management](#5.5). For overall website operations, see [Website Core Operations](#5.1).

---

## Configuration Architecture

The Nginx configuration system operates through a multi-layered architecture that separates configuration generation, parameter management, validation, and application phases.

```mermaid
graph TB
    subgraph "Configuration Sources"
        TEMPLATES["nginx_conf Templates<br/>website_default.conf<br/>stream_default.conf"]
        PARAMS["Parameter Updates<br/>dto.NginxParam"]
        FILES["Direct File Edits<br/>Config Files"]
    end
    
    subgraph "Configuration Management Layer"
        PARSER["parser.NewParser()<br/>parser.NewStringParser()"]
        CONFIG["components.Config<br/>components.Server<br/>components.Location"]
        VALIDATOR["nginxCheckAndReload()"]
    end
    
    subgraph "Scope-Based Operations"
        SERVER["Server Scope<br/>constant.NginxScopeServer"]
        LOCATION["Location Scope<br/>constant.NginxScopeLocation"]
        SCOPEMAP["dto.ScopeKeyMap<br/>Feature → Keys"]
    end
    
    subgraph "Configuration Modules"
        PROXY["Proxy Module<br/>WebsiteProxyConfig"]
        REWRITE["Rewrite Module<br/>NginxRewriteReq"]
        AUTH["Auth Module<br/>NginxAuthConfig"]
        CACHE["Cache Module<br/>WebsiteCacheConfig"]
        LB["Load Balance<br/>NginxUpstream"]
    end
    
    subgraph "Storage & Application"
        SITEDIR["Site Directory<br/>/www/sites/{alias}/"]
        SITECONF["site.conf<br/>stream.conf"]
        NGINX["OpenResty Container<br/>Reload/Check"]
    end
    
    TEMPLATES --> PARSER
    PARAMS --> CONFIG
    FILES --> PARSER
    
    PARSER --> CONFIG
    CONFIG --> VALIDATOR
    
    SERVER --> CONFIG
    LOCATION --> CONFIG
    SCOPEMAP --> CONFIG
    
    PROXY --> PARAMS
    REWRITE --> PARAMS
    AUTH --> PARAMS
    CACHE --> PARAMS
    LB --> PARAMS
    
    VALIDATOR --> SITECONF
    SITECONF --> NGINX
    NGINX -->|Validation Failure| VALIDATOR
    
    SITEDIR --> SITECONF
```

**Sources:** [agent/app/service/website.go:774-820](), [agent/app/service/website_utils.go:182-325]()

---

## Template-Based Configuration Generation

During website creation, Nginx configuration files are generated from embedded templates. The system uses the `nginx_conf` package to provide base configurations that are then customized based on website type and parameters.

### Template Selection and Initialization

| Website Type | Template File | Configuration Path |
|-------------|---------------|-------------------|
| `constant.Stream` | `stream_default.conf` | `/www/sites/{alias}/stream.conf` |
| All other types | `website_default.conf` | `/www/sites/{alias}/conf/site.conf` |

```mermaid
graph LR
    CREATE["Website Creation<br/>configDefaultNginx()"]
    TYPE{{"Website Type"}}
    
    STREAM["Stream Template<br/>nginx_conf.GetWebsiteFile()"]
    HTTP["HTTP Template<br/>nginx_conf.GetWebsiteFile()"]
    
    PARSE["parser.NewStringParser()"]
    CONFIG["components.Config"]
    
    CUSTOMIZE["Customize Configuration<br/>setListen()<br/>UpdateDirective()<br/>UpdateRoot()"]
    
    WRITE["nginx.WriteConfig()<br/>nginx.IndentedStyle"]
    CHECK["opNginx()<br/>constant.NginxCheck"]
    RELOAD["opNginx()<br/>constant.NginxReload"]
    
    CREATE --> TYPE
    TYPE -->|stream| STREAM
    TYPE -->|other| HTTP
    
    STREAM --> PARSE
    HTTP --> PARSE
    PARSE --> CONFIG
    CONFIG --> CUSTOMIZE
    CUSTOMIZE --> WRITE
    WRITE --> CHECK
    CHECK --> RELOAD
```

**Key Operations:**

1. **Template Loading**: `nginx_conf.GetWebsiteFile()` returns embedded template content [agent/app/service/website_utils.go:198-236]()
2. **Parser Initialization**: `parser.NewStringParser()` creates a parser from template string [agent/app/service/website_utils.go:199,236]()
3. **Configuration Customization**: Template is modified based on website type and parameters [agent/app/service/website_utils.go:244-312]()
4. **File Writing**: `nginx.WriteConfig()` writes the configuration with indented style [agent/app/service/website_utils.go:315]()

**Sources:** [agent/app/service/website_utils.go:182-325](), [agent/app/service/website.go:448-451]()

---

## Scope-Based Parameter Management

The configuration system organizes parameters into scopes, allowing granular control over specific Nginx directives without manual file editing.

### Scope Hierarchy

```mermaid
graph TD
    ROOT["Nginx Configuration"]
    
    SERVER["Server Block<br/>constant.NginxScopeServer"]
    LOCATION["Location Block<br/>constant.NginxScopeLocation"]
    
    ROOT --> SERVER
    SERVER --> LOCATION
    
    SERVER --> SSL["SSL Directives<br/>ssl_certificate<br/>ssl_certificate_key"]
    SERVER --> LISTEN["Listen Directives<br/>listen 80<br/>listen 443 ssl"]
    SERVER --> LOGS["Log Directives<br/>access_log<br/>error_log"]
    
    LOCATION --> PROXY["Proxy Directives<br/>proxy_pass<br/>proxy_set_header"]
    LOCATION --> REWRITE["Rewrite Directives<br/>rewrite<br/>return"]
    LOCATION --> AUTH["Auth Directives<br/>auth_basic<br/>auth_basic_user_file"]
```

**Sources:** [agent/app/service/website.go:774-820]()

### Parameter Structure

The `dto.NginxParam` structure represents a single configuration directive with its parameters:

```
NginxParam {
    Name: string           // Directive name (e.g., "proxy_pass", "listen")
    Params: []string       // Directive parameters (e.g., ["http://127.0.0.1:8080"])
}
```

**API Flow for Scope-Based Configuration:**

```mermaid
sequenceDiagram
    participant Frontend
    participant API as "/api/v2/websites/config"
    participant Service as "WebsiteService"
    participant Parser as "nginx.Parser"
    participant Validator as "nginxCheckAndReload()"
    participant Nginx as "OpenResty"
    
    Frontend->>API: POST GetNginxConfigByScope<br/>{websiteId, scope}
    API->>Service: GetNginxConfigByScope()
    Service->>Service: dto.ScopeKeyMap[scope]
    Service->>Parser: getNginxParamsByKeys()
    Parser-->>Service: []NginxParam
    Service-->>API: WebsiteNginxConfig
    API-->>Frontend: {enable, params}
    
    Frontend->>API: POST UpdateNginxConfigByScope<br/>{websiteId, scope, operate, params}
    API->>Service: UpdateNginxConfigByScope()
    
    alt operate == ConfigDel
        Service->>Service: deleteNginxConfig()
    else operate == ConfigNew
        Service->>Service: updateNginxConfig()
    end
    
    Service->>Parser: nginx.WriteConfig()
    Parser->>Validator: nginxCheckAndReload()
    Validator->>Nginx: docker exec nginx -t
    
    alt validation success
        Validator->>Nginx: docker exec nginx -s reload
        Validator-->>Service: success
        Service-->>API: success
        API-->>Frontend: success
    else validation failure
        Validator->>Parser: Restore old content
        Validator-->>Service: error
        Service-->>API: error
        API-->>Frontend: error
    end
```

**Sources:** [agent/app/service/website.go:774-820](), [frontend/src/api/modules/website.ts:71-77]()

### Scope-to-Keys Mapping

The `dto.ScopeKeyMap` maps feature names to their associated Nginx directive keys. This allows the system to retrieve and update related directives as a group:

```
ScopeKeyMap = {
    "ssl": ["ssl_certificate", "ssl_certificate_key", "ssl_protocols", "ssl_ciphers"],
    "cache": ["proxy_cache", "proxy_cache_valid", "proxy_cache_key"],
    "gzip": ["gzip", "gzip_types", "gzip_min_length"],
    // ... more mappings
}
```

**Sources:** [agent/app/service/website.go:775-776,806-808]()

---

## Configuration Modules

The Nginx configuration system provides specialized modules for different features. Each module has its own configuration structure and update logic.

### Proxy Configuration Module

Manages reverse proxy settings including cache, CORS, and upstream configuration.

**Data Structures:**
- `request.WebsiteProxyConfig` [agent/app/dto/request/website.go:253-273]()
- Frontend: `Website.ProxyConfig` [frontend/src/api/interface/website.ts:421-449]()

**Key Directives:**
- `proxy_pass`: Upstream target
- `proxy_set_header`: Header forwarding
- `proxy_cache`: Caching configuration
- CORS headers: `add_header Access-Control-*`

**API Endpoints:**
- GET: `/websites/proxies` via `getProxyConfig()` [frontend/src/api/modules/website.ts:183-185]()
- POST: `/websites/proxies/update` via `operateProxyConfig()` [frontend/src/api/modules/website.ts:187-189]()
- POST: `/websites/proxies/file` via `updateProxyConfigFile()` [frontend/src/api/modules/website.ts:191-193]()

**Sources:** [agent/app/service/website.go:106-112](), [agent/app/dto/request/website.go:253-273]()

### Rewrite Configuration Module

Manages URL rewriting rules using Nginx rewrite directives.

**Data Structures:**
- `request.NginxRewriteReq` [agent/app/dto/request/website.go:385-388]()
- `response.NginxRewriteRes` [agent/app/dto/response/website.go:94-96]()

**API Endpoints:**
- POST: `/websites/rewrite` via `getRewriteConfig()` [frontend/src/api/modules/website.ts:167-169]()
- POST: `/websites/rewrite/update` via `updateRewriteConfig()` [frontend/src/api/modules/website.ts:171-173]()
- POST: `/websites/rewrite/custom` via `operateCustomRewrite()` [frontend/src/api/modules/website.ts:345-347]()

**Sources:** [agent/app/service/website.go:119-122](), [frontend/src/api/modules/website.ts:167-173]()

### Authentication Module

Manages HTTP Basic Authentication at both server and location levels.

**Configuration Levels:**

| Scope | Use Case | Data Structure |
|-------|----------|----------------|
| Server-wide | Protect entire website | `NginxAuthConfig` |
| Path-specific | Protect specific locations | `NginxPathAuthConfig` |

**Data Structures:**
- `request.NginxAuthConfig` [agent/app/dto/request/website.go:475-484]()
- `request.NginxPathAuthConfig` [agent/app/dto/request/website.go:486-493]()

**API Endpoints:**
- POST: `/websites/auths` via `getAuthConfig()` [frontend/src/api/modules/website.ts:199-201]()
- POST: `/websites/auths/update` via `operateAuthConfig()` [frontend/src/api/modules/website.ts:203-205]()
- POST: `/websites/auths/path` via `getPathAuthConfig()` [frontend/src/api/modules/website.ts:207-209]()
- POST: `/websites/auths/path/update` via `operatePathAuthConfig()` [frontend/src/api/modules/website.ts:211-213]()

**Sources:** [agent/app/service/website.go:124-127](), [agent/app/dto/request/website.go:475-493]()

### Redirect Configuration Module

Manages HTTP redirects including domain redirects, path redirects, and redirect types (301, 302).

**Data Structures:**
- `request.RedirectConfig` [frontend/src/api/interface/website.ts:517-531]()

**Redirect Types:**
- Domain redirect: Redirect all traffic from one domain to another
- Path redirect: Redirect specific paths
- Root redirect: Redirect root path only

**API Endpoints:**
- POST: `/websites/redirect` via `getRedirectConfig()` [frontend/src/api/modules/website.ts:223-225]()
- POST: `/websites/redirect/update` via `operateRedirectConfig()` [frontend/src/api/modules/website.ts:227-229]()
- POST: `/websites/redirect/file` via `updateRedirectConfigFile()` [frontend/src/api/modules/website.ts:231-233]()

**Sources:** [agent/app/service/website.go:86-88](), [frontend/src/api/modules/website.ts:223-233]()

### Load Balance Configuration Module

Manages Nginx upstream configuration for load balancing across multiple backend servers.

**Data Structure:**

```mermaid
graph LR
    UPSTREAM["dto.NginxUpstream"]
    
    UPSTREAM --> NAME["Name: string"]
    UPSTREAM --> ALGO["Algorithm: string"]
    UPSTREAM --> SERVERS["Servers: []NginxUpstreamServer"]
    
    SERVERS --> SERVER1["Server"]
    SERVERS --> SERVER2["Server"]
    
    SERVER1 --> S1_ADDR["server: string"]
    SERVER1 --> S1_WEIGHT["weight: number"]
    SERVER1 --> S1_FAILS["maxFails: number"]
    SERVER1 --> S1_TIMEOUT["failTimeout: number"]
    SERVER1 --> S1_CONNS["maxConns: number"]
    SERVER1 --> S1_FLAG["flag: string"]
```

**Supported Algorithms:**
- `default`: Round-robin (no directive)
- `ip_hash`: Client IP-based distribution
- `least_conn`: Least connections
- `hash`: Generic hash-based

**API Endpoints:**
- GET: `/websites/{id}/lbs` via `getLoadBalances()` [frontend/src/api/modules/website.ts:297-299]()
- POST: `/websites/lbs/create` via `createLoadBalance()` [frontend/src/api/modules/website.ts:301-303]()
- POST: `/websites/lbs/update` via `updateLoadBalance()` [frontend/src/api/modules/website.ts:309-311]()
- POST: `/websites/lbs/del` via `deleteLoadBalance()` [frontend/src/api/modules/website.ts:305-307]()
- POST: `/websites/lbs/file` via `updateLoadBalanceFile()` [frontend/src/api/modules/website.ts:313-315]()

**Sources:** [agent/app/service/website.go:100-105](), [frontend/src/api/modules/website.ts:297-315]()

---

## Validation and Reload Mechanism

All configuration changes go through a validation process before being applied to prevent Nginx from entering an invalid state.

### Validation Workflow

```mermaid
graph TD
    START["Configuration Update Request"]
    
    BACKUP["Backup Current Config<br/>nginxConfig.OldContent"]
    MODIFY["Modify Configuration<br/>nginx.WriteConfig()"]
    
    VALIDATE["Validation Phase<br/>nginxCheckAndReload()"]
    
    CHECK["nginx -t<br/>opNginx(NginxCheck)"]
    CHECK_RESULT{{"Check Result"}}
    
    RELOAD["nginx -s reload<br/>opNginx(NginxReload)"]
    SUCCESS["Return Success"]
    
    ROLLBACK["Restore Old Content<br/>fileOp.WriteFile()"]
    FAIL["Return Error"]
    
    START --> BACKUP
    BACKUP --> MODIFY
    MODIFY --> VALIDATE
    
    VALIDATE --> CHECK
    CHECK --> CHECK_RESULT
    
    CHECK_RESULT -->|Valid| RELOAD
    RELOAD --> SUCCESS
    
    CHECK_RESULT -->|Invalid| ROLLBACK
    ROLLBACK --> FAIL
```

**Sources:** [agent/app/service/website_utils.go:755-781]()

### Validation Function: nginxCheckAndReload()

The `nginxCheckAndReload()` function implements a safe configuration update process:

**Parameters:**
- `oldContent []byte`: Original configuration for rollback
- `filePath string`: Configuration file path
- `containerName string`: OpenResty container name

**Process:**

1. **Configuration Check** [agent/app/service/website_utils.go:761-765]()
   - Executes: `docker exec {container} nginx -t`
   - Validates syntax and directive correctness
   - Returns error if validation fails

2. **Configuration Reload** [agent/app/service/website_utils.go:766-770]()
   - Executes: `docker exec {container} nginx -s reload`
   - Applies new configuration
   - Returns error if reload fails

3. **Rollback on Failure** [agent/app/service/website_utils.go:771-779]()
   - Restores `oldContent` to `filePath`
   - Prevents Nginx from running with invalid configuration
   - Returns descriptive error message

**Sources:** [agent/app/service/website_utils.go:755-781]()

### Container Operation: opNginx()

The `opNginx()` function executes Nginx control commands within the OpenResty container:

**Supported Operations:**
- `constant.NginxCheck`: Validate configuration (`nginx -t`)
- `constant.NginxReload`: Reload configuration (`nginx -s reload`)
- `constant.NginxStop`: Stop Nginx (`nginx -s stop`)
- `constant.NginxStart`: Start Nginx (via Docker API)
- `constant.NginxRestart`: Restart container

**Implementation:**
- Uses Docker exec API for check/reload operations
- Uses Docker container API for start/stop/restart operations
- Returns error with command output on failure

**Sources:** [agent/app/service/website_utils.go:1066-1103]()

---

## File-Based Configuration Management

In addition to scope-based parameter updates, the system supports direct editing of Nginx configuration files through the frontend.

### Configuration File Access

```mermaid
graph LR
    FRONTEND["Frontend Editor"]
    
    API_GET["GET /websites/{id}/config/{type}"]
    API_UPDATE["POST /websites/nginx/update"]
    
    SERVICE_GET["GetWebsiteNginxConfig()"]
    SERVICE_UPDATE["UpdateNginxConfigFile()"]
    
    FILEOP["files.NewFileInfo()"]
    PARSER["parser.NewParser()"]
    
    VALIDATE["nginxCheckAndReload()"]
    
    CONFFILE["Configuration File<br/>/www/sites/{alias}/conf/site.conf"]
    
    FRONTEND -->|Read| API_GET
    API_GET --> SERVICE_GET
    SERVICE_GET --> FILEOP
    FILEOP --> CONFFILE
    CONFFILE -->|Content| FILEOP
    FILEOP -->|FileInfo| SERVICE_GET
    SERVICE_GET -->|response.FileInfo| API_GET
    API_GET -->|File content| FRONTEND
    
    FRONTEND -->|Edit & Save| API_UPDATE
    API_UPDATE --> SERVICE_UPDATE
    SERVICE_UPDATE --> PARSER
    PARSER --> VALIDATE
    VALIDATE -->|Valid| CONFFILE
    VALIDATE -->|Invalid| SERVICE_UPDATE
    SERVICE_UPDATE -->|Result| API_UPDATE
    API_UPDATE -->|Result| FRONTEND
```

**Sources:** [agent/app/service/website.go:822-840](), [frontend/src/api/modules/website.ts:47-49,159-161]()

### File Reading Process

**API Endpoint:** `GET /websites/{id}/config/{type}`

**Backend Implementation:** [agent/app/service/website.go:822-840]()

1. Retrieve website record by ID
2. Determine configuration path based on `configType`:
   - `constant.AppOpenresty`: Returns `GetWebsiteConfigPath(website)`
3. Create `files.FileInfo` with `Expand: true` to read content
4. Return `response.FileInfo` containing file metadata and content

**Sources:** [agent/app/service/website.go:822-840]()

### File Update Process

**API Endpoint:** `POST /websites/nginx/update`

**Request Structure:**
```typescript
NginxUpdate {
    id: number          // Website ID
    content: string     // New configuration content
}
```

**Backend Processing Flow:**

1. **Retrieve Website**: Get website record to obtain configuration path
2. **Parse Configuration**: Validate syntax using `parser.NewParser()`
3. **Backup Content**: Store current configuration for rollback
4. **Write New Config**: Save new content to file
5. **Validate**: Run `nginxCheckAndReload()` with backup content
6. **Return Result**: Success or error with rollback

**Sources:** [frontend/src/api/modules/website.ts:159-161](), [agent/app/service/website.go:822-840]()

---

## Configuration Update Patterns

The system employs different patterns for configuration updates depending on the complexity and scope of changes.

### Pattern 1: Scope-Based Parameter Update

Used for modular features with predefined directive sets (SSL, cache, gzip, etc.).

**Characteristics:**
- Uses `dto.ScopeKeyMap` to identify related directives
- Updates multiple related parameters atomically
- Supports enable/disable toggle via `operate` parameter

**Example Flow:**

```mermaid
sequenceDiagram
    participant Client
    participant API
    participant Service
    participant Config
    
    Client->>API: updateNginxConfig({scope: "ssl", operate: "add"})
    API->>Service: UpdateNginxConfigByScope()
    Service->>Service: Get keys from ScopeKeyMap["ssl"]
    Service->>Service: getNginxParams(params, keys)
    Service->>Config: updateNginxConfig(scope, params)
    Config->>Config: Find server block
    Config->>Config: Update directives
    Config->>Config: nginx.WriteConfig()
    Config->>Config: nginxCheckAndReload()
    Config-->>Service: Result
    Service-->>API: Result
    API-->>Client: Result
```

**Sources:** [agent/app/service/website.go:795-820]()

### Pattern 2: Feature-Specific Configuration

Used for complex features with custom configuration structures (proxy, rewrite, auth).

**Characteristics:**
- Custom configuration parsing and generation logic
- Feature-specific validation rules
- May involve multiple configuration files

**Example: Proxy Configuration:**

1. Frontend sends `WebsiteProxyConfig` with all proxy settings
2. Backend validates proxy target and settings
3. Generates location block with proxy directives
4. Optionally generates proxy cache configuration
5. Writes configuration and validates

**Sources:** [agent/app/service/website.go:106-112](), [agent/app/dto/request/website.go:253-273]()

### Pattern 3: Direct File Edit

Used when scope-based or feature-specific patterns don't apply, or when users need full control.

**Characteristics:**
- Complete configuration file provided by user
- Full syntax validation via `parser.NewParser()`
- High flexibility, high risk (requires manual correctness)

**Sources:** [agent/app/service/website.go:822-840](), [frontend/src/api/modules/website.ts:159-161]()

---

## Configuration Path Resolution

The system uses consistent path conventions for storing website configurations.

### Path Structure

```
/www/sites/{alias}/
├── conf/
│   └── site.conf          # HTTP/HTTPS site configuration
├── stream.conf            # Stream (TCP/UDP) configuration
├── proxy/
│   └── *.conf            # Proxy configuration files
├── ssl/
│   ├── certificate.pem   # SSL certificate
│   └── private.key       # SSL private key
├── index/                # Website root directory
└── log/
    ├── access.log        # Access log
    └── error.log         # Error log
```

**Path Helper Functions:**

| Function | Purpose | Returns |
|----------|---------|---------|
| `GetSiteDir(alias)` | Base site directory | `/www/sites/{alias}` |
| `GetSitePath(website, SiteConf)` | HTTP config path | `/www/sites/{alias}/conf/site.conf` |
| `GetSitePath(website, StreamConf)` | Stream config path | `/www/sites/{alias}/stream.conf` |
| `GetWebsiteConfigPath(website)` | Config path by type | Type-specific path |

**Sources:** [agent/app/service/website_utils.go:1139-1173]()

---

## Integration with Configuration System

The Nginx configuration management integrates with other website management subsystems:

```mermaid
graph TD
    NGINX["Nginx Configuration<br/>Management"]
    
    SSL["SSL Certificate<br/>Management"]
    DOMAIN["Domain<br/>Management"]
    WEBSITE["Website<br/>Operations"]
    RUNTIME["Runtime<br/>Configuration"]
    
    NGINX --> SSL
    NGINX --> DOMAIN
    NGINX --> WEBSITE
    NGINX --> RUNTIME
    
    SSL -->|Certificate Path| NGINX
    SSL -->|Enable HTTPS| NGINX
    
    DOMAIN -->|Listen Directives| NGINX
    DOMAIN -->|Server Name| NGINX
    
    WEBSITE -->|Create| NGINX
    WEBSITE -->|Delete| NGINX
    WEBSITE -->|Update| NGINX
    
    RUNTIME -->|PHP Proxy| NGINX
    RUNTIME -->|Proxy Pass| NGINX
    
    NGINX -->|Reload| OPENRESTY["OpenResty Container"]
    NGINX -->|Validate| OPENRESTY
```

**Cross-System Operations:**

1. **Website Creation**: Generates initial Nginx configuration from template [agent/app/service/website.go:448-451]()
2. **SSL Enablement**: Updates server block with SSL directives [agent/app/service/website.go:492-519]()
3. **Domain Addition**: Adds listen and server_name directives [agent/app/service/website_utils.go:588-614]()
4. **Runtime Change**: Updates proxy_pass directives for PHP runtime [agent/app/service/website.go:59]()

**Sources:** [agent/app/service/website.go:241-536](), [agent/app/service/website_utils.go:182-325]()

---

# Page: SSL Certificate Management

# SSL Certificate Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/app/dto/request/website.go](agent/app/dto/request/website.go)
- [agent/app/dto/response/website.go](agent/app/dto/response/website.go)
- [agent/app/service/website.go](agent/app/service/website.go)
- [agent/app/service/website_utils.go](agent/app/service/website_utils.go)
- [agent/go.mod](agent/go.mod)
- [agent/go.sum](agent/go.sum)
- [agent/utils/ssl/dns_provider.go](agent/utils/ssl/dns_provider.go)
- [core/go.mod](core/go.mod)
- [core/go.sum](core/go.sum)
- [frontend/src/api/interface/website.ts](frontend/src/api/interface/website.ts)
- [frontend/src/api/modules/website.ts](frontend/src/api/modules/website.ts)
- [frontend/src/global/mimetype.ts](frontend/src/global/mimetype.ts)
- [frontend/src/views/website/ssl/dns-account/create/index.vue](frontend/src/views/website/ssl/dns-account/create/index.vue)

</details>



This document covers the SSL certificate management system within 1Panel, including certificate creation, ACME integration, DNS validation methods, and automated certificate lifecycle management. The system provides comprehensive SSL certificate management capabilities through both manual and automated processes.

For website configuration and Nginx integration, see [Website Management System](#4.2). For runtime environment management, see [Runtime Management](#4.3).

## Core System Architecture

The SSL certificate management system integrates frontend Vue.js components with backend Go services to provide automated certificate lifecycle management. The system manages both standalone SSL certificates and their application to websites through Nginx configuration.

### SSL Management Components

```mermaid
graph TB
    subgraph "Frontend API Layer"
        SSLAPI["website.ts<br/>createSSL(), getSSL(), updateSSL()"]
        HTTPSAPI["website.ts<br/>getHTTPSConfig(), updateHTTPSConfig()"]
        DnsAPI["website.ts<br/>searchDnsAccount(), createDnsAccount()"]
        AcmeAPI["website.ts<br/>searchAcmeAccount(), createAcmeAccount()"]
    end
    
    subgraph "Frontend Components"
        SSLIndex["ssl/index.vue<br/>Certificate listing & management"]
        SSLCreate["ssl/create/index.vue<br/>Certificate creation form"] 
        DNSAccountCreate["ssl/dns-account/create/index.vue<br/>DNS provider credentials"]
        HTTPSDialog["HTTPS configuration dialog<br/>Enable/disable HTTPS per website"]
    end
    
    subgraph "Backend Website Service"
        GetWebsiteHTTPS["GetWebsiteHTTPS(websiteId)<br/>agent/app/service/website.go:842"]
        OpWebsiteHTTPS["OpWebsiteHTTPS(req)<br/>agent/app/service/website.go:901"]
        ApplySSL["applySSL(website, websiteSSL, req)<br/>agent/app/service/website_utils.go:740"]
    end
    
    subgraph "Backend SSL Utilities"
        CreatePemFile["createPemFile(website, websiteSSL)<br/>website_utils.go:678"]
        GetHttpsPort["getHttpsPort(websiteID)<br/>website_utils.go:711"]
        SetListen["setListen(server, port, ipv6, ssl)<br/>website_utils.go:638"]
    end
    
    subgraph "Data Models"
        WebsiteSSL["model.WebsiteSSL<br/>Pem, PrivateKey, Provider, AutoRenew"]
        Website["model.Website<br/>WebsiteSSLID, Protocol, HttpConfig"]
        WebsiteDomain["model.WebsiteDomain<br/>Domain, Port, SSL flag"]
    end
    
    SSLAPI --> SSLCreate
    HTTPSAPI --> HTTPSDialog
    DnsAPI --> DNSAccountCreate
    AcmeAPI --> SSLCreate
    
    SSLIndex --> SSLCreate
    HTTPSDialog --> GetWebsiteHTTPS
    HTTPSDialog --> OpWebsiteHTTPS
    
    OpWebsiteHTTPS --> ApplySSL
    ApplySSL --> CreatePemFile
    ApplySSL --> GetHttpsPort
    ApplySSL --> SetListen
    
    ApplySSL --> WebsiteSSL
    OpWebsiteHTTPS --> Website
    SetListen --> WebsiteDomain
```

Sources: [frontend/src/api/modules/website.ts:111-153](), [agent/app/service/website.go:842-1013](), [agent/app/service/website_utils.go:638-831]()

## SSL Application to Websites

The system applies SSL certificates to websites through the `OpWebsiteHTTPS` operation, which modifies Nginx configuration and updates website protocol settings.

### HTTPS Operation Workflow

```mermaid
flowchart TD
    HTTPSRequest["updateHTTPSConfig(req)<br/>frontend/src/api/modules/website.ts:151"]
    OpWebsiteHTTPS["OpWebsiteHTTPS(ctx, req)<br/>agent/app/service/website.go:901"]
    
    EnableCheck{"req.Enable?"}
    
    DisableSSL["Disable HTTPS Path"]
    RemoveListens["Remove SSL listens<br/>removeSSLListen()"]
    DeleteNginxConfig["Delete SSL directives<br/>deleteNginxConfig()"]
    SetHTTP["website.Protocol = HTTP<br/>WebsiteSSLID = 0"]
    
    EnableSSL["Enable HTTPS Path"]
    TypeCheck{"req.Type"}
    
    ExistedSSL["Type: constant.SSLExisted<br/>Use existing certificate"]
    ManualSSL["Type: constant.SSLManual<br/>Upload certificate manually"]
    
    GetWebsiteSSL["websiteSSLRepo.GetFirst()<br/>Retrieve certificate"]
    CreateManualSSL["getManualWebsiteSSL(req)<br/>Parse uploaded certificate"]
    
    ApplySSLFunc["applySSL(website, websiteSSL, req)<br/>agent/app/service/website_utils.go:740"]
    
    GetDomains["websiteDomainRepo.GetBy()<br/>Get all website domains"]
    GetHttpsPorts["getHttpsPort(websiteID)<br/>Determine HTTPS ports"]
    
    UpdateListens["Update Nginx listen directives<br/>setListen() with ssl=true"]
    ConfigureHTTP2["server.UpdateDirective('http2', on)"]
    
    HTTPConfigSwitch{"req.HttpConfig"}
    
    HTTPSOnly["constant.HTTPSOnly<br/>Remove HTTP listens"]
    HTTPToHTTPS["constant.HTTPToHTTPS<br/>Add redirect if ($scheme = http)"]
    HTTPAlso["constant.HTTPAlso<br/>Keep HTTP + HTTPS"]
    
    CreatePemFiles["createPemFile(website, websiteSSL)<br/>Write fullchain.pem, privkey.pem"]
    UpdateSSLParams["Update ssl_certificate paths<br/>Update ssl_protocols, ssl_ciphers"]
    
    ChangeHSTS["ChangeHSTSConfig(hsts, http3)<br/>Add Strict-Transport-Security header"]
    
    SaveWebsite["websiteRepo.Save(website)<br/>Persist changes"]
    
    HTTPSRequest --> OpWebsiteHTTPS
    OpWebsiteHTTPS --> EnableCheck
    
    EnableCheck -->|"false"| DisableSSL
    DisableSSL --> RemoveListens
    RemoveListens --> DeleteNginxConfig
    DeleteNginxConfig --> SetHTTP
    SetHTTP --> SaveWebsite
    
    EnableCheck -->|"true"| EnableSSL
    EnableSSL --> TypeCheck
    
    TypeCheck -->|"existed"| ExistedSSL
    TypeCheck -->|"manual"| ManualSSL
    
    ExistedSSL --> GetWebsiteSSL
    ManualSSL --> CreateManualSSL
    
    GetWebsiteSSL --> ApplySSLFunc
    CreateManualSSL --> ApplySSLFunc
    
    ApplySSLFunc --> GetDomains
    GetDomains --> GetHttpsPorts
    GetHttpsPorts --> UpdateListens
    UpdateListens --> ConfigureHTTP2
    
    ConfigureHTTP2 --> HTTPConfigSwitch
    
    HTTPConfigSwitch -->|"HTTPSOnly"| HTTPSOnly
    HTTPConfigSwitch -->|"HTTPToHTTPS"| HTTPToHTTPS
    HTTPConfigSwitch -->|"HTTPAlso"| HTTPAlso
    
    HTTPSOnly --> CreatePemFiles
    HTTPToHTTPS --> CreatePemFiles
    HTTPAlso --> CreatePemFiles
    
    CreatePemFiles --> UpdateSSLParams
    UpdateSSLParams --> ChangeHSTS
    ChangeHSTS --> SaveWebsite
```

### HTTP/HTTPS Configuration Modes

The system supports three modes for handling HTTP/HTTPS traffic, defined as constants in the backend:

| Mode Constant | Frontend Value | Behavior |
|--------------|----------------|----------|
| `constant.HTTPSOnly` | `"HTTPSOnly"` | Only HTTPS listen, remove all HTTP listens |
| `constant.HTTPToHTTPS` | `"HTTPToHTTPS"` | Both HTTP and HTTPS listen, redirect HTTP to HTTPS via `if ($scheme = http)` |
| `constant.HTTPAlso` | `"HTTPAlso"` | Both HTTP and HTTPS listen, no redirect |

Sources: [agent/app/service/website.go:901-1013](), [agent/app/service/website_utils.go:740-831](), [agent/app/service/website_utils.go:678-709](), [frontend/src/api/modules/website.ts:147-153]()

## ACME Integration System

The system integrates with multiple ACME Certificate Authorities through the `AcmeClient` implementation and supports various authentication methods:

### Supported ACME Providers

| Provider | Type Value | Authentication Method |
|----------|-----------|----------------------|
| Let's Encrypt | `letsencrypt` | Standard ACME registration |
| ZeroSSL | `zerossl` | EAB (External Account Binding) |
| Buypass | `buypass` | Standard ACME registration |
| Google Public CA | `google` | EAB (External Account Binding) |
| Custom ACME Server | `custom` | Custom CA directory URL |

### ACME Client Architecture

```mermaid
graph TB
    subgraph "Frontend Account Management"
        AcmeForm["ACME Account Form<br/>acme-account/create/index.vue"]
        AccountTypes["AcmeAccountTypes<br/>from mimetype.ts"]
        KeyTypes["KeyTypes<br/>P256, P384, RSA 2048-4096"]
    end
    
    subgraph "Backend ACME Client"
        AcmeClient["AcmeClient struct<br/>ssl.NewAcmeClient()"]
        LegoClient["Lego Client<br/>lego.NewClient()"]
        AcmeUser["AcmeUser struct<br/>Email, Registration, Key"]
    end
    
    subgraph "ACME Registration Methods"
        StandardReg["Standard Registration<br/>client.Registration.Register()"]
        EABReg["EAB Registration<br/>RegisterWithExternalAccountBinding()"]
        ZeroSSLEAB["ZeroSSL EAB<br/>getZeroSSLEabCredentials()"]
    end
    
    subgraph "Certificate Operations"
        DNSChallenge["DNS-01 Challenge<br/>client.UseDns()"]
        HTTPChallenge["HTTP-01 Challenge<br/>client.UseHTTP()"]
        ObtainCert["Certificate Obtain<br/>client.ObtainSSL()"]
        RevokeCert["Certificate Revoke<br/>client.RevokeSSL()"]
    end
    
    AcmeForm --> AccountTypes
    AccountTypes --> KeyTypes
    AcmeForm --> AcmeClient
    
    AcmeClient --> LegoClient
    AcmeClient --> AcmeUser
    
    LegoClient --> StandardReg
    LegoClient --> EABReg
    EABReg --> ZeroSSLEAB
    
    AcmeClient --> DNSChallenge
    AcmeClient --> HTTPChallenge
    AcmeClient --> ObtainCert
    AcmeClient --> RevokeCert
```

### Key Type Support

The system supports multiple cryptographic key types defined in `KeyTypes`:

| Label | Value | Key Type |
|-------|--------|----------|
| EC 256 | `P256` | ECDSA P-256 |
| EC 384 | `P384` | ECDSA P-384 |
| RSA 2048 | `2048` | RSA 2048-bit |
| RSA 3072 | `3072` | RSA 3072-bit |
| RSA 4096 | `4096` | RSA 4096-bit |

Sources: [agent/utils/ssl/acme.go:28-178](), [agent/utils/ssl/client.go:28-38](), [frontend/src/global/mimetype.ts:158-172](), [frontend/src/views/website/ssl/create/index.vue:29-49]()

## DNS Validation Methods

The system supports automated DNS record management through integrated DNS providers and manual DNS validation for unsupported providers:

### Supported DNS Providers

The system supports 25+ DNS providers defined in `DNSTypes`:

| Provider Category | DNS Types | Authentication Method |
|------------------|-----------|----------------------|
| **Chinese Cloud** | AliYun, TencentCloud, HuaweiCloud, BaiduCloud | Access Key + Secret Key |
| **International Cloud** | CloudFlare, Vercel, CloudDNS | API Token/Key |
| **Domain Registrars** | GoDaddy, NameCheap, NameSilo, NameCom | API Key + Secret |
| **Specialized DNS** | Dynu, ClouDNS, Spaceship, RegRu | Various auth methods |

### DNS Account Configuration Architecture

```mermaid
graph TB
    subgraph "DNS Account Management"
        DNSAccountForm["DNS Account Form<br/>dns-account/create/index.vue"]
        DNSTypes["DNSTypes array<br/>from mimetype.ts"]
        AuthConfig["Authorization Config<br/>API keys, tokens, credentials"]
    end
    
    subgraph "DNS Provider Integration"
        DNSClient["DNS Provider Client<br/>ssl.getDNSProviderConfig()"]
        ProviderAuth["Provider Authentication<br/>dnsAccount.Authorization"]
        DNSChallenge["DNS-01 Challenge<br/>client.UseDns()"]
    end
    
    subgraph "DNS Validation Settings"
        CNAME["CNAME Support<br/>websiteSSL.DisableCNAME"]
        Nameservers["Custom Nameservers<br/>nameserver1, nameserver2"]
        SkipDNS["Skip DNS Check<br/>websiteSSL.SkipDNS"]
    end
    
    subgraph "Challenge Process"
        RecordCreation["TXT Record Creation<br/>Automated via API"]
        ValidationWait["Validation Wait<br/>DNS propagation"]
        RecordCleanup["Record Cleanup<br/>Automatic removal"]
    end
    
    DNSAccountForm --> DNSTypes
    DNSTypes --> AuthConfig
    AuthConfig --> DNSClient
    
    DNSClient --> ProviderAuth
    ProviderAuth --> DNSChallenge
    
    DNSChallenge --> CNAME
    CNAME --> Nameservers
    Nameservers --> SkipDNS
    
    DNSChallenge --> RecordCreation
    RecordCreation --> ValidationWait
    ValidationWait --> RecordCleanup
```

### DNS Provider Authentication Examples

Different DNS providers require different authentication methods:

| Provider | Required Fields | Example Configuration |
|----------|----------------|----------------------|
| CloudFlare | `email`, `apiKey` | Email + API Token |
| AliYun | `accessKey`, `secretKey` | Access Key + Secret Key |
| GoDaddy | `apiKey`, `apiSecret` | API Key + API Secret |
| NameCheap | `apiKey`, `apiUser` | API Key + Username |

### Manual DNS Validation

For unsupported providers or custom DNS setups, manual validation is available:

```mermaid
graph LR
    ManualRequest["Manual DNS Request<br/>provider: 'dnsManual'"]
    DNSResolve["GetDNSResolve()<br/>Generate TXT records"]
    UserAction["User Creates TXT Records<br/>Manual DNS management"]
    Validation["Manual Validation<br/>User confirms DNS setup"]
    CertIssue["Certificate Issuance<br/>After DNS verification"]
    
    ManualRequest --> DNSResolve
    DNSResolve --> UserAction
    UserAction --> Validation
    Validation --> CertIssue
```

Sources: [frontend/src/global/mimetype.ts:174-255](), [frontend/src/views/website/ssl/dns-account/create/index.vue:1-255](), [agent/app/service/website_ssl.go:424-451](), [agent/utils/ssl/client.go:40-65]()

## Certificate Lifecycle Management

The SSL management system provides automated lifecycle management through status tracking, automatic renewal, and post-processing operations:

### Certificate Status Constants

The backend uses specific status constants defined in the `constant` package:

| Status Constant | Frontend Display | Description |
|----------------|------------------|-------------|
| `constant.SSLInit` | `init` | Initial certificate creation |
| `constant.SSLApply` | `applying` | Certificate request in progress |
| `constant.SSLReady` | `success` | Certificate successfully issued |
| `constant.SSLApplyError` | `applyError` | Certificate application failed |
| `constant.StatusError` | `error` | General error state |

### SSL Certificate Types

The system distinguishes between certificate types using the `Type` field:

| Type Constant | Value | Description |
|--------------|--------|-------------|
| `constant.SSLExisted` | `"existed"` | Use existing certificate from certificate list |
| `constant.SSLManual` | `"manual"` | Manually uploaded certificate |
| `constant.SSLAuto` | `"auto"` | Automatically obtained via ACME |

### Certificate Lifecycle State Machine

```mermaid
stateDiagram-v2
    [*] --> SSLInit : "websiteSSLRepo.Create()"
    SSLInit --> SSLApply : "ObtainSSL() called"
    SSLApply --> SSLReady : "Certificate obtained successfully"
    SSLApply --> SSLApplyError : "ACME validation failed"
    SSLApply --> StatusError : "Network/system error"
    SSLReady --> SSLApply : "Manual renewal triggered"
    SSLReady --> SSLReady : "Auto renewal success"
    SSLApplyError --> SSLApply : "Retry after fix"
    StatusError --> SSLApply : "Retry after system recovery"
```

### Post-Processing Operations

The system executes post-processing operations after successful certificate issuance:

```mermaid
graph TD
    CertificateReady["Certificate Ready<br/>constant.SSLReady"]
    
    PostProcessing["Post-Processing Check<br/>websiteSSL fields"]
    
    DirectoryPush["Directory Push<br/>websiteSSL.PushDir"]
    PushOperation["saveCertificateFile()<br/>Copy to websiteSSL.Dir"]
    
    ShellExecution["Shell Execution<br/>websiteSSL.ExecShell"]
    ShellCommand["cmd.RunBashC()<br/>Execute websiteSSL.Shell"]
    
    SystemSSLUpdate["System SSL Update<br/>reloadSystemSSL()"]
    SystemReload["System Certificate Reload<br/>req_helper.PostLocalCore()"]
    
    WebsiteUpdate["Website SSL Update<br/>Update Nginx configs"]
    NginxReload["Nginx Reload<br/>opNginx(reload)"]
    
    NodePush["Node Push<br/>websiteSSL.PushNode"]
    NodeDistribution["xpack.PushSSLToNode()<br/>Distribute to cluster nodes"]
    
    CertificateReady --> PostProcessing
    
    PostProcessing --> DirectoryPush
    DirectoryPush --> PushOperation
    
    PostProcessing --> ShellExecution  
    ShellExecution --> ShellCommand
    
    PostProcessing --> SystemSSLUpdate
    SystemSSLUpdate --> SystemReload
    
    PostProcessing --> WebsiteUpdate
    WebsiteUpdate --> NginxReload
    
    PostProcessing --> NodePush
    NodePush --> NodeDistribution
```

### Automatic Renewal System

The system supports automatic certificate renewal based on expiration dates:

| Configuration | Backend Field | Purpose |
|---------------|---------------|---------|
| Auto Renewal | `websiteSSL.AutoRenew` | Enable/disable automatic renewal |
| Directory Push | `websiteSSL.PushDir` + `websiteSSL.Dir` | Copy certificates to custom directory |
| Shell Execution | `websiteSSL.ExecShell` + `websiteSSL.Shell` | Run custom post-renewal scripts |
| Node Distribution | `websiteSSL.PushNode` + `websiteSSL.Nodes` | Distribute to cluster nodes |

Sources: [agent/app/service/website_ssl.go:245-411](), [agent/app/service/website_ssl.go:413-422](), [agent/app/service/website_ssl.go:219-243](), [frontend/src/views/website/ssl/index.vue:76-97]()

## User Interface Components

### Main SSL Management Interface

The primary SSL management interface (`frontend/src/views/website/ssl/index.vue`) provides:

- **Certificate Listing**: Displays all SSL certificates with status, domains, and expiration
- **Bulk Operations**: Multi-select deletion and management
- **Quick Actions**: Create, upload, self-signed certificate generation
- **Account Management**: ACME and DNS account configuration access

Key UI operations:

| Button/Action | Function | Component Reference |
|---------------|----------|-------------------|
| Create | `openSSL()` | `sslCreateRef` |
| Upload | `openUpload()` | `sslUploadRef` |
| Self-Signed | `openCA()` | `caRef` |
| ACME Account | `openAcmeAccount()` | `acmeAccountRef` |
| DNS Account | `openDnsAccount()` | `dnsAccountRef` |

### Certificate Creation Form

The creation form (`frontend/src/views/website/ssl/create/index.vue`) supports:

- **Domain Configuration**: Primary domain and alternative names
- **Provider Selection**: DNS account, manual DNS, HTTP, or self-signed
- **Advanced Options**: Custom nameservers, CNAME handling, DNS skip options
- **Post-Processing**: Directory push and shell execution configuration

### Certificate Detail View

The detail view (`frontend/src/views/website/ssl/detail/index.vue`) provides:

- **Certificate Information**: Domain, organization, validity dates
- **Certificate Content**: PEM-formatted certificate and private key display
- **Copy Functionality**: Easy copying of certificate data

Sources: [frontend/src/views/website/ssl/index.vue:5-24](), [frontend/src/views/website/ssl/index.vue:336-362](), [frontend/src/views/website/ssl/detail/index.vue:1-67]()

---

# Page: Domain Management

# Domain Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/app/dto/request/website.go](agent/app/dto/request/website.go)
- [agent/app/dto/response/website.go](agent/app/dto/response/website.go)
- [agent/app/service/website.go](agent/app/service/website.go)
- [agent/app/service/website_utils.go](agent/app/service/website_utils.go)
- [frontend/src/api/interface/website.ts](frontend/src/api/interface/website.ts)
- [frontend/src/api/modules/website.ts](frontend/src/api/modules/website.ts)

</details>



This document describes the domain management subsystem within the Website Management System. It covers domain CRUD operations, the distinction between primary and additional domains, per-domain port and SSL configuration, and the automatic SSL certificate selection algorithm that supports wildcard matching.

For information about overall website operations, see [Website Core Operations](#5.1). For SSL certificate acquisition and management, see [SSL Certificate Management](#5.4). For Nginx configuration generation that consumes domain data, see [Nginx Configuration Management](#5.3).

---

## Domain Data Model

Each website in 1Panel can have multiple domains. Domains are represented by distinct data structures at the database, API, and Nginx configuration layers.

### Domain Entity Structure

| Field | Type | Description |
|-------|------|-------------|
| `id` | uint | Primary key |
| `domain` | string | Domain name (e.g., `example.com`, `*.example.com`) |
| `port` | int | Port number for this domain (default: 80 for HTTP, 443 for HTTPS) |
| `websiteID` | uint | Foreign key to website |
| `ssl` | bool | Whether SSL is enabled for this domain |
| `sslCert` | string | Associated SSL certificate identifier |
| `createdAt` | time | Creation timestamp |

**Primary vs Additional Domains:**
- **Primary Domain**: Stored in `website.primaryDomain` (string field on the website record)
- **Additional Domains**: Stored as separate `Domain` records in the `domains` table with `websiteID` foreign key

Sources: [frontend/src/api/interface/website.ts:178-185](), [agent/app/model/website.go]()

---

## Domain Architecture

### Domain Management Components

```mermaid
graph TB
    subgraph "Frontend Layer"
        DomainList["DomainList Component<br/>domain/index.vue"]
        DomainDialog["DomainDialog Component<br/>create dialog"]
        WebsiteForm["Website Creation Form<br/>create/index.vue"]
    end
    
    subgraph "API Layer"
        DomainAPI["Domain API Module<br/>modules/website.ts"]
        
        DomainInterface["Domain TypeScript Interfaces<br/>interface/website.ts"]
    end
    
    subgraph "Backend Services"
        WebsiteSvc["WebsiteService<br/>website.go"]
        
        subgraph "Domain Operations"
            GetDomains["GetDomains()"]
            CreateDomain["CreateDomain()"]
            DeleteDomain["DeleteDomain()"]
            UpdateDomainSSL["updateDomainSSL()"]
        end
        
        DomainValidation["Domain Validation<br/>validateDomain()"]
        SSLSelection["SSL Auto-Selection<br/>selectSSLForDomain()"]
    end
    
    subgraph "Data Layer"
        DomainRepo["DomainRepo<br/>repo/website_domain.go"]
        WebsiteRepo["WebsiteRepo"]
        DB[("Database<br/>domains table<br/>websites table")]
    end
    
    subgraph "Nginx Layer"
        NginxConfig["Nginx Config Generator<br/>website_utils.go"]
        ServerBlock["Server Block Generation<br/>configServerBlock()"]
    end
    
    DomainList --> DomainAPI
    DomainDialog --> DomainAPI
    WebsiteForm --> DomainAPI
    
    DomainAPI --> DomainInterface
    DomainAPI --> WebsiteSvc
    
    WebsiteSvc --> GetDomains
    WebsiteSvc --> CreateDomain
    WebsiteSvc --> DeleteDomain
    WebsiteSvc --> UpdateDomainSSL
    
    WebsiteSvc --> DomainValidation
    WebsiteSvc --> SSLSelection
    
    GetDomains --> DomainRepo
    CreateDomain --> DomainRepo
    DeleteDomain --> DomainRepo
    UpdateDomainSSL --> DomainRepo
    
    DomainRepo --> DB
    WebsiteRepo --> DB
    
    WebsiteSvc --> NginxConfig
    NginxConfig --> ServerBlock
    ServerBlock -->|"Generates server_name"| NginxFile["Nginx Config File"]
```

Sources: [frontend/src/views/website/website/domain/index.vue](), [frontend/src/api/modules/website.ts:29-37](), [agent/app/service/website.go:52-59]()

---

## Domain CRUD Operations

### Creating a Domain

Domain creation occurs in two contexts:
1. **During website creation**: Primary domain and optional additional domains are specified
2. **After website creation**: Additional domains can be added to existing websites

**Create Domain Request Structure:**

```typescript
interface DomainCreate {
    websiteId: number;
    domain: string;
    port: number;
}
```

**Backend Creation Flow:**

```mermaid
sequenceDiagram
    participant Client as Frontend
    participant API as POST /websites/:id/domains
    participant Service as WebsiteService
    participant Validator as Domain Validator
    participant Repo as DomainRepo
    participant Nginx as Nginx Config Writer
    participant NginxCmd as nginx -s reload
    
    Client->>API: createDomain(request)
    API->>Service: CreateDomain(req)
    
    Service->>Validator: validateDomain(domain)
    Validator->>Validator: Check DNS format
    Validator->>Validator: Check special characters
    Validator->>Validator: Check punycode (Chinese domains)
    Validator-->>Service: Validation result
    
    Service->>Repo: CheckDomainExist(domain)
    Repo-->>Service: Exists check
    
    alt Domain already exists
        Service-->>Client: Error: Domain already bound
    end
    
    Service->>Repo: Create(domain)
    Repo-->>Service: Domain created
    
    Service->>Nginx: UpdateNginxConfig(website)
    Nginx->>Nginx: Add server_name to config
    Nginx->>NginxCmd: nginx -t
    NginxCmd-->>Nginx: Config valid
    Nginx->>NginxCmd: nginx -s reload
    NginxCmd-->>Nginx: Reloaded
    
    Service-->>Client: Success
```

**Domain Validation Rules:**

| Rule | Description | Regex/Logic |
|------|-------------|-------------|
| DNS Format | Valid DNS characters | `^([a-zA-Z0-9*]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$` |
| Wildcard | Supports `*.domain.com` format | Must start with `*.` if wildcard |
| Punycode | Converts Chinese domains | Uses `idna.ToASCII()` for internationalized domains |
| Port Range | Valid port number | 1-65535 |
| Uniqueness | No duplicate domains across all websites | Database constraint check |

Sources: [agent/app/service/website.go:500-600](), [frontend/src/api/modules/website.ts:29-31](), [agent/app/service/website_utils.go:400-500]()

### Reading Domains

**GetDomains Operation:**

```mermaid
graph LR
    Request["GET /websites/:id/domains"] --> Service["GetDomains(websiteID)"]
    Service --> Repo["DomainRepo.GetBy(websiteID)"]
    Repo --> DB[("SELECT * FROM domains<br/>WHERE website_id = ?")]
    DB --> Transform["Transform to DTO"]
    Transform --> Response["[]Domain with SSL status"]
```

The response includes computed SSL information:
- `ssl`: Boolean indicating if SSL is enabled for this domain
- `sslCert`: Name of the associated certificate (if any)
- `sslExpireDate`: Certificate expiration date

Sources: [agent/app/service/website.go:1000-1100](), [frontend/src/api/modules/website.ts:33-35]()

### Updating Domain SSL Configuration

Domains can have their SSL configuration updated independently:

**Update Request:**
```typescript
interface DomainUpdate {
    id: number;
    ssl: boolean;
    websiteID: number;
}
```

**Update Process:**
1. Toggle `ssl` flag on domain record
2. If enabling SSL: Run SSL auto-selection algorithm (see below)
3. Regenerate Nginx server block with appropriate `ssl_certificate` directives
4. Validate and reload Nginx configuration

Sources: [agent/app/service/website.go:1200-1300](), [frontend/src/views/website/website/domain/index.vue:100-200]()

### Deleting a Domain

**Constraints:**
- Cannot delete the primary domain (must delete website instead)
- Must have at least one domain remaining on the website

```mermaid
sequenceDiagram
    participant Client
    participant API as DELETE /websites/domains/:id
    participant Service as WebsiteService
    participant Repo as DomainRepo
    participant Nginx as Nginx Config
    
    Client->>API: deleteDomain(domainID)
    API->>Service: DeleteDomain(domainID)
    
    Service->>Repo: GetByID(domainID)
    Repo-->>Service: Domain record
    
    Service->>Service: Check if primary domain
    alt Is primary domain
        Service-->>Client: Error: Cannot delete primary
    end
    
    Service->>Repo: CountByWebsiteID(websiteID)
    Repo-->>Service: Domain count
    
    alt Only one domain remains
        Service-->>Client: Error: Must keep at least one domain
    end
    
    Service->>Repo: Delete(domainID)
    Service->>Nginx: RegenerateConfig(websiteID)
    Service-->>Client: Success
```

Sources: [agent/app/service/website.go:1400-1500](), [frontend/src/api/modules/website.ts:37]()

---

## Primary Domain vs Additional Domains

### Conceptual Distinction

| Aspect | Primary Domain | Additional Domains |
|--------|----------------|-------------------|
| Storage | `websites.primary_domain` column | `domains` table rows |
| Quantity | Exactly one per website | Zero or more |
| Required | Yes (always present) | No (optional) |
| Deletion | Deletes entire website | Deletes only the domain |
| Display | Shown first in UI | Listed below primary |
| Default SSL | Inherits website SSL config | Can be configured independently |

**Why This Distinction Exists:**

The primary domain serves as the canonical identifier for the website and is used for:
- Website site path generation: `/www/sites/{primaryDomain}/`
- Default Nginx server block ordering
- Backup file naming
- Log file naming conventions
- Display name in website lists

Sources: [agent/app/model/website.go:20-50](), [frontend/src/views/website/website/create/index.vue:100-150]()

### Data Flow Example

**Website with Multiple Domains:**

```mermaid
graph TD
    Website["Website Record<br/>ID: 1<br/>primary_domain: 'example.com'<br/>protocol: 'https'"]
    
    Domain1["Domain Record<br/>ID: 101<br/>domain: 'www.example.com'<br/>port: 443<br/>ssl: true"]
    
    Domain2["Domain Record<br/>ID: 102<br/>domain: 'api.example.com'<br/>port: 443<br/>ssl: true"]
    
    Domain3["Domain Record<br/>ID: 103<br/>domain: 'staging.example.com'<br/>port: 8080<br/>ssl: false"]
    
    Website --> Domain1
    Website --> Domain2
    Website --> Domain3
    
    NginxConfig["Nginx Server Block:<br/>server_name example.com<br/>           www.example.com<br/>           api.example.com<br/>           staging.example.com:8080;"]
    
    Domain1 --> NginxConfig
    Domain2 --> NginxConfig
    Domain3 --> NginxConfig
```

Sources: [agent/app/service/website_utils.go:200-300]()

---

## Port Configuration per Domain

Each domain can have an independent port configuration. This enables scenarios like:
- Running HTTP and HTTPS on the same website
- Custom port routing for specific domains
- Multi-port applications

### Port Configuration Rules

**Default Port Assignment:**

| Protocol | SSL Enabled | Default Port |
|----------|-------------|--------------|
| HTTP | false | 80 |
| HTTPS | true | 443 |
| Custom | - | User-specified (1-65535) |

**Port in Nginx Configuration:**

When a domain has a non-standard port, it is included in the `server_name` directive:

```nginx
# Standard ports (omitted in server_name)
server {
    listen 80;
    server_name example.com www.example.com;
}

# Custom port (included in server_name)
server {
    listen 8080;
    server_name example.com:8080;
}
```

**Port Update Process:**

```mermaid
sequenceDiagram
    participant UI as Domain Config UI
    participant API as updateDomain API
    participant Service as WebsiteService
    participant PortCheck as Port Validator
    participant Nginx as Nginx Generator
    
    UI->>API: Update domain port
    API->>Service: UpdateDomain(domain, newPort)
    
    Service->>PortCheck: validatePort(newPort)
    PortCheck->>PortCheck: Check range (1-65535)
    PortCheck->>PortCheck: Check if port available
    PortCheck-->>Service: Valid
    
    Service->>Service: domain.port = newPort
    Service->>Service: Save to database
    
    Service->>Nginx: RegenerateNginxConfig()
    Nginx->>Nginx: Generate listen directive
    Nginx->>Nginx: Generate server_name with port
    
    Service-->>UI: Success
```

Sources: [agent/app/service/website_utils.go:500-600](), [frontend/src/views/website/website/domain/index.vue:200-250]()

---

## SSL Certificate Assignment per Domain

Domains can have individual SSL certificate assignments, enabling:
- Different certificates for different subdomains
- Wildcard certificate sharing across multiple domains
- SNI (Server Name Indication) support

### SSL Assignment Data Model

**Domain SSL Fields:**

```typescript
interface Domain {
    ssl: boolean;              // Is SSL enabled?
    sslCert: string;           // Certificate identifier (website_ssl.id)
}
```

**WebsiteSSL Record (referenced by sslCert):**

```typescript
interface WebsiteSSL {
    id: number;
    primaryDomain: string;     // Certificate primary domain
    type: string;              // "letsEncrypt" | "manual" | "selfSigned"
    provider: string;          // ACME provider
    domains: string[];         // All domains covered by this cert
    keyType: string;           // "RSA" | "ECC"
    autoRenew: boolean;
    expireDate: Date;
}
```

### Nginx SSL Configuration Generation

**Per-Domain SSL Block:**

```mermaid
graph TB
    Start[/"Generate Nginx Config"/]
    
    LoadDomains["Load all domains<br/>for website"]
    
    GroupBySSL{"Group domains<br/>by SSL certificate"}
    
    SSLGroup1["SSL Cert A:<br/>example.com<br/>www.example.com"]
    
    SSLGroup2["SSL Cert B:<br/>api.example.com"]
    
    NoSSL["No SSL:<br/>staging.example.com"]
    
    GenBlock1["Generate server block:<br/>listen 443 ssl;<br/>server_name example.com www.example.com;<br/>ssl_certificate /path/to/certA.pem;"]
    
    GenBlock2["Generate server block:<br/>listen 443 ssl;<br/>server_name api.example.com;<br/>ssl_certificate /path/to/certB.pem;"]
    
    GenBlock3["Generate server block:<br/>listen 80;<br/>server_name staging.example.com;"]
    
    WriteConfig["Write to<br/>/www/sites/{alias}/nginx.conf"]
    
    Start --> LoadDomains
    LoadDomains --> GroupBySSL
    GroupBySSL --> SSLGroup1
    GroupBySSL --> SSLGroup2
    GroupBySSL --> NoSSL
    
    SSLGroup1 --> GenBlock1
    SSLGroup2 --> GenBlock2
    NoSSL --> GenBlock3
    
    GenBlock1 --> WriteConfig
    GenBlock2 --> WriteConfig
    GenBlock3 --> WriteConfig
```

Sources: [agent/app/service/website_utils.go:700-900]()

---

## Auto-SSL Selection Algorithm

When SSL is enabled for a domain but no specific certificate is assigned, the system automatically selects an appropriate certificate using a matching algorithm that supports wildcard domains.

### Selection Algorithm Logic

```mermaid
flowchart TD
    Start[/"Auto-SSL Selection<br/>for domain: 'api.example.com'"/]
    
    LoadCerts["Load all WebsiteSSL records<br/>associated with this website"]
    
    CheckEmpty{"Any certificates<br/>available?"}
    
    NoMatch["Return: No SSL<br/>(ssl disabled for this domain)"]
    
    ExactMatch{"Find certificate where<br/>domain IN cert.domains<br/>(exact match)"}
    
    UseExact["Use this certificate<br/>Set domain.sslCert = cert.id"]
    
    WildcardMatch{"Find certificate with<br/>wildcard domain that matches"}
    
    CheckWildcard["For each cert.domain starting with '*.':<br/>Extract base: '*.example.com' → 'example.com'<br/>Check if domain ends with base"]
    
    UseWildcard["Use this certificate<br/>Set domain.sslCert = cert.id"]
    
    Start --> LoadCerts
    LoadCerts --> CheckEmpty
    CheckEmpty -->|No| NoMatch
    CheckEmpty -->|Yes| ExactMatch
    
    ExactMatch -->|Found| UseExact
    ExactMatch -->|Not found| WildcardMatch
    
    WildcardMatch --> CheckWildcard
    CheckWildcard -->|Match found| UseWildcard
    CheckWildcard -->|No match| NoMatch
```

### Wildcard Matching Implementation

**Example Certificate:**
```
Certificate ID: 10
Primary Domain: *.example.com
Domains: ["*.example.com", "example.com"]
```

**Matching Logic:**

| Domain to Match | Certificate Domain | Match Type | Result |
|-----------------|-------------------|------------|---------|
| `example.com` | `example.com` | Exact | ✓ Match |
| `www.example.com` | `*.example.com` | Wildcard | ✓ Match |
| `api.example.com` | `*.example.com` | Wildcard | ✓ Match |
| `staging.api.example.com` | `*.example.com` | Wildcard | ✗ No match (subdomain depth) |
| `other.com` | `*.example.com` | Wildcard | ✗ No match (different domain) |

**Wildcard Matching Code Reference:**

The matching algorithm is implemented in the `selectSSLForDomain()` function:

1. **Exact Match Phase**: `domain == cert.Domain` for each domain in certificate
2. **Wildcard Match Phase**: For domains starting with `*.`:
   - Extract base domain: `strings.TrimPrefix(certDomain, "*.")`
   - Check suffix: `strings.HasSuffix(domain, "." + baseDomain)`
   - Verify single-level: `!strings.Contains(prefix, ".")`

Sources: [agent/app/service/website_utils.go:1100-1250]()

### Priority Order

When multiple certificates could match a domain, priority is:

1. **Exact match** (highest priority)
2. **Most specific wildcard** (e.g., `*.api.example.com` beats `*.example.com`)
3. **Newest certificate** (by creation date)

Sources: [agent/app/service/website_utils.go:1200-1250]()

---

## Domain Validation and Constraints

### Validation Rules Summary

**Input Validation:**

```mermaid
graph LR
    Input["Domain Input:<br/>'例子.中国'"]
    
    PunycodeCheck{"Contains<br/>non-ASCII?"}
    
    Convert["Convert to Punycode:<br/>'xn--fsq270a.xn--fiqs8s'"]
    
    DNSValidate["DNS Format Validation:<br/>Regex check"]
    
    UniqueCheck["Uniqueness Check:<br/>Query existing domains"]
    
    Valid["Valid Domain"]
    
    Input --> PunycodeCheck
    PunycodeCheck -->|Yes| Convert
    PunycodeCheck -->|No| DNSValidate
    Convert --> DNSValidate
    DNSValidate --> UniqueCheck
    UniqueCheck --> Valid
```

**Validation Error Messages:**

| Error Code | Condition | Message (i18n key) |
|------------|-----------|-------------------|
| `ErrDomainFormat` | Invalid DNS format | `website.domainFormatErr` |
| `ErrDomainExist` | Domain already exists | `website.domainExist` |
| `ErrWildcardInvalid` | Invalid wildcard usage | `website.wildcardErr` |
| `ErrPortInvalid` | Port out of range | `commons.rule.port` |
| `ErrInternationalDomain` | Punycode conversion failed | `website.punycodeErr` |

Sources: [agent/app/service/website_utils.go:300-450](), [frontend/src/lang/modules/en.ts:1800-1850]()

### International Domain Name (IDN) Support

The system supports internationalized domains (e.g., Chinese characters) through automatic Punycode conversion:

**Conversion Example:**

| Input | Punycode Output |
|-------|----------------|
| `例子.中国` | `xn--fsq270a.xn--fiqs8s` |
| `テスト.jp` | `xn--zckzah.jp` |
| `مثال.السعودية` | `xn--mgbh0fb.xn--mgberp4a5d4ar` |

The conversion happens transparently during domain creation and is stored in Punycode format in the database and Nginx configuration.

Sources: [agent/app/service/website_utils.go:350-400]()

---

## Integration with Nginx Configuration

### Server Name Generation

Domains are aggregated into Nginx `server_name` directives:

**Generation Logic:**

```go
// Pseudocode
func generateServerName(website Website, domains []Domain) string {
    names := []string{website.PrimaryDomain}
    
    for _, domain := range domains {
        if domain.Port == 80 || domain.Port == 443 {
            names = append(names, domain.Domain)
        } else {
            names = append(names, domain.Domain + ":" + strconv.Itoa(domain.Port))
        }
    }
    
    return strings.Join(names, " ")
}
```

**Example Output:**

```nginx
server {
    listen 80;
    listen 443 ssl http2;
    server_name example.com www.example.com api.example.com staging.example.com:8080;
    
    ssl_certificate /opt/1panel/data/apps/openresty/core/ssl/example.com.pem;
    ssl_certificate_key /opt/1panel/data/apps/openresty/core/ssl/example.com.key;
    
    # ... rest of configuration
}
```

Sources: [agent/app/service/website_utils.go:600-700]()

### Configuration Reload Workflow

```mermaid
sequenceDiagram
    participant Domain as Domain CRUD Operation
    participant Service as WebsiteService
    participant Generator as Config Generator
    participant Parser as Nginx Parser
    participant FileSystem as File System
    participant Nginx as Nginx Process
    
    Domain->>Service: Domain created/updated/deleted
    Service->>Generator: RegenerateConfig(websiteID)
    
    Generator->>Generator: Load website + all domains
    Generator->>Generator: Group by SSL certificate
    Generator->>Generator: Generate server blocks
    
    Generator->>Parser: Parse existing config
    Parser-->>Generator: AST tree
    
    Generator->>Generator: Update server_name directives
    Generator->>Generator: Update SSL directives
    
    Generator->>FileSystem: Write config file
    FileSystem-->>Generator: Written
    
    Generator->>Nginx: nginx -t (validate)
    Nginx-->>Generator: Valid
    
    Generator->>Nginx: nginx -s reload
    Nginx-->>Generator: Reloaded
    
    Generator-->>Service: Success
```

Sources: [agent/app/service/website_utils.go:100-200](), [agent/utils/nginx/nginx.go]()

---

## API Reference

### Domain Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/websites/:id/domains` | List all domains for website |
| POST | `/websites/:id/domains` | Create new domain |
| PUT | `/websites/domains/:id` | Update domain (port, SSL) |
| DELETE | `/websites/domains/:id` | Delete domain |

**Request/Response Examples:**

**Create Domain:**
```json
POST /websites/1/domains
{
  "domain": "api.example.com",
  "port": 443
}

Response 200:
{
  "id": 102,
  "domain": "api.example.com",
  "port": 443,
  "websiteID": 1,
  "ssl": false,
  "sslCert": "",
  "createdAt": "2024-01-15T10:30:00Z"
}
```

**List Domains:**
```json
GET /websites/1/domains

Response 200:
{
  "items": [
    {
      "id": 101,
      "domain": "www.example.com",
      "port": 443,
      "ssl": true,
      "sslCert": "10",
      "sslExpireDate": "2024-06-15T00:00:00Z"
    },
    {
      "id": 102,
      "domain": "api.example.com",
      "port": 443,
      "ssl": true,
      "sslCert": "10"
    }
  ]
}
```

Sources: [frontend/src/api/modules/website.ts:29-40](), [agent/app/api/v2/website.go]()

---

# Page: Infrastructure Management

# Infrastructure Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/app/api/v2/container.go](agent/app/api/v2/container.go)
- [agent/app/dto/container.go](agent/app/dto/container.go)
- [agent/app/service/container.go](agent/app/service/container.go)
- [agent/router/ro_container.go](agent/router/ro_container.go)
- [frontend/src/api/interface/container.ts](frontend/src/api/interface/container.ts)
- [frontend/src/api/interface/database.ts](frontend/src/api/interface/database.ts)
- [frontend/src/api/interface/file.ts](frontend/src/api/interface/file.ts)
- [frontend/src/api/modules/container.ts](frontend/src/api/modules/container.ts)
- [frontend/src/api/modules/database.ts](frontend/src/api/modules/database.ts)
- [frontend/src/api/modules/files.ts](frontend/src/api/modules/files.ts)
- [frontend/src/views/container/container/operate/index.vue](frontend/src/views/container/container/operate/index.vue)
- [frontend/src/views/database/mysql/index.vue](frontend/src/views/database/mysql/index.vue)
- [frontend/src/views/database/mysql/setting/index.vue](frontend/src/views/database/mysql/setting/index.vue)
- [frontend/src/views/database/redis/index.vue](frontend/src/views/database/redis/index.vue)
- [frontend/src/views/database/redis/setting/index.vue](frontend/src/views/database/redis/setting/index.vue)
- [frontend/src/views/host/file-management/code-editor/index.vue](frontend/src/views/host/file-management/code-editor/index.vue)
- [frontend/src/views/host/file-management/index.vue](frontend/src/views/host/file-management/index.vue)

</details>



## Purpose and Scope

Infrastructure Management encompasses the core operational capabilities of 1Panel for managing server resources. This module provides three primary subsystems:

1. **Container Management** - Full lifecycle management of Docker containers, images, networks, volumes, and Docker Compose applications. See [Container Management](#8.1) for details.
2. **Database Management** - Administration of MySQL/MariaDB, PostgreSQL, and Redis databases including creation, configuration, backups, and terminal access. See [Database Management](#8.2) for details.
3. **File Management** - Web-based file browser with Monaco code editor, supporting multi-tab editing, file operations, and terminal integration. See [File Management System](#8.3) for details.

These subsystems share common architectural patterns: a Vue.js frontend communicating with Go backend services through RESTful APIs, with operations executed asynchronously via the task system for long-running processes.

---

## System Architecture Overview

### Infrastructure Management Component Map

```mermaid
graph TB
    subgraph "Frontend: Vue Components"
        ContainerUI["views/container/container/operate/index.vue"]
        MySQLUI["views/database/mysql/index.vue"]
        RedisUI["views/database/redis/index.vue"]
        FileUI["views/host/file-management/index.vue"]
        CodeEditor["views/host/file-management/code-editor/index.vue"]
    end
    
    subgraph "Frontend: API Layer"
        ContainerAPI["api/modules/container.ts"]
        DatabaseAPI["api/modules/database.ts"]
        FileAPI["api/modules/files.ts"]
    end
    
    subgraph "Backend: API Handlers"
        ContainerHandler["app/api/v2/container.go<br/>BaseApi.SearchContainer<br/>BaseApi.ContainerCreate"]
        DatabaseHandler["app/api/v2/database.go"]
        FileHandler["app/api/v2/file.go"]
    end
    
    subgraph "Backend: Service Layer"
        ContainerSvc["app/service/container.go<br/>ContainerService.Page<br/>ContainerService.ContainerCreate"]
        DatabaseSvc["app/service/database.go"]
        FileSvc["app/service/file.go"]
    end
    
    subgraph "Backend: Task System"
        TaskMgr["app/task/task.go<br/>NewTaskWithOps<br/>Task.Execute"]
    end
    
    subgraph "External Systems"
        Docker["Docker Engine<br/>client.ContainerList<br/>client.ContainerCreate"]
        MySQL["MySQL/MariaDB<br/>via GORM"]
        Redis["Redis Server<br/>redis-cli"]
        FileSystem["File System<br/>os.OpenFile<br/>filepath.Walk"]
    end
    
    ContainerUI --> ContainerAPI
    MySQLUI --> DatabaseAPI
    RedisUI --> DatabaseAPI
    FileUI --> FileAPI
    CodeEditor --> FileAPI
    
    ContainerAPI --> ContainerHandler
    DatabaseAPI --> DatabaseHandler
    FileAPI --> FileHandler
    
    ContainerHandler --> ContainerSvc
    DatabaseHandler --> DatabaseSvc
    FileHandler --> FileSvc
    
    ContainerSvc --> TaskMgr
    DatabaseSvc --> TaskMgr
    FileSvc --> TaskMgr
    
    ContainerSvc --> Docker
    DatabaseSvc --> MySQL
    DatabaseSvc --> Redis
    FileSvc --> FileSystem
```

**Sources:**
- [frontend/src/views/container/container/operate/index.vue:1-350]()
- [frontend/src/views/database/mysql/index.vue:1-266]()
- [frontend/src/views/host/file-management/index.vue:1-650]()
- [frontend/src/api/modules/container.ts:1-232]()
- [frontend/src/api/modules/database.ts:1-195]()
- [frontend/src/api/modules/files.ts:1-181]()
- [agent/app/api/v2/container.go:1-100]()
- [agent/app/service/container.go:1-100]()

---

## Core Data Structures and Interfaces

The infrastructure management subsystems share common architectural patterns in how they define data structures and API interfaces.

### Container Management DTOs

| DTO Type | Purpose | Key Fields |
|----------|---------|------------|
| `PageContainer` | Search/filter containers | `name`, `state`, `filters`, `orderBy` |
| `ContainerInfo` | Container display data | `containerID`, `name`, `state`, `ports`, `isFromApp` |
| `ContainerOperate` | Create/update container | `name`, `image`, `networks[]`, `exposedPorts[]`, `volumes[]` |
| `ContainerUpgrade` | Upgrade container image | `names[]`, `image`, `forcePull` |
| `ComposeInfo` | Docker Compose project | `name`, `configFile`, `containers[]`, `env` |

**Sources:**
- [agent/app/dto/container.go:1-285]()
- [frontend/src/api/interface/container.ts:1-407]()

### Database Management DTOs

| DTO Type | Purpose | Key Fields |
|----------|---------|------------|
| `DatabaseOption` | Database connection selector | `id`, `from`, `type`, `database`, `version` |
| `MysqlDBInfo` | MySQL database record | `id`, `name`, `username`, `password`, `permission` |
| `PostgresqlDBInfo` | PostgreSQL database record | `id`, `name`, `username`, `superUser` |
| `RedisConf` | Redis configuration | `port`, `timeout`, `maxclients`, `maxmemory` |
| `BaseInfo` | Database connection info | `name`, `port`, `password`, `containerName` |

**Sources:**
- [frontend/src/api/interface/database.ts:1-350]()

### File Management DTOs

| DTO Type | Purpose | Key Fields |
|----------|---------|------------|
| `ReqFile` | File listing request | `path`, `search`, `showHidden`, `sortBy` |
| `File` | File/directory info | `path`, `name`, `size`, `isDir`, `mode`, `user`, `group` |
| `FileCreate` | Create file/directory | `path`, `isDir`, `mode`, `isLink` |
| `FileCompress` | Compress files | `files[]`, `type`, `dst`, `secret` |
| `Favorite` | Bookmarked path | `path`, `isDir`, `name` |

**Sources:**
- [frontend/src/api/interface/file.ts:1-264]()

---

## API Routes and Service Mapping

### Container Routes to Services

```mermaid
graph LR
    subgraph "HTTP Routes (router/ro_container.go)"
        R1["POST /containers/search"]
        R2["POST /containers"]
        R3["POST /containers/update"]
        R4["POST /containers/operate"]
        R5["POST /containers/compose"]
        R6["POST /containers/image/pull"]
        R7["POST /containers/network"]
        R8["POST /containers/volume"]
    end
    
    subgraph "API Handlers (app/api/v2/container.go)"
        H1["BaseApi.SearchContainer"]
        H2["BaseApi.ContainerCreate"]
        H3["BaseApi.ContainerUpdate"]
        H4["BaseApi.ContainerOperation"]
        H5["BaseApi.CreateCompose"]
        H6["BaseApi.ImagePull"]
        H7["BaseApi.CreateNetwork"]
        H8["BaseApi.CreateVolume"]
    end
    
    subgraph "Service Methods (app/service/container.go)"
        S1["ContainerService.Page"]
        S2["ContainerService.ContainerCreate"]
        S3["ContainerService.ContainerUpdate"]
        S4["ContainerService.ContainerOperation"]
        S5["ContainerService.CreateCompose"]
        S6["ImageService.ImagePull"]
        S7["ContainerService.CreateNetwork"]
        S8["ContainerService.CreateVolume"]
    end
    
    R1 --> H1
    R2 --> H2
    R3 --> H3
    R4 --> H4
    R5 --> H5
    R6 --> H6
    R7 --> H7
    R8 --> H8
    
    H1 --> S1
    H2 --> S2
    H3 --> S3
    H4 --> S4
    H5 --> S5
    H6 --> S6
    H7 --> S7
    H8 --> S8
```

**Sources:**
- [agent/router/ro_container.go:1-92]()
- [agent/app/api/v2/container.go:1-700]()
- [agent/app/service/container.go:1-920]()

### Database API Endpoints

| Endpoint Pattern | Purpose | Frontend Caller |
|-----------------|---------|-----------------|
| `POST /databases/search` | List MySQL databases | `searchMysqlDBs()` |
| `POST /databases` | Create MySQL database | `addMysqlDB()` |
| `POST /databases/pg/search` | List PostgreSQL databases | `searchPostgresqlDBs()` |
| `POST /databases/redis/conf` | Load Redis config | `loadRedisConf()` |
| `POST /databases/common/load/file` | Load config file | `loadDBFile()` |
| `GET /databases/db/list/{type}` | List database instances | `listDatabases()` |

**Sources:**
- [frontend/src/api/modules/database.ts:1-195]()

### File Management API Endpoints

| Endpoint Pattern | Purpose | Frontend Caller |
|-----------------|---------|-----------------|
| `POST /files/search` | List files/directories | `getFilesList()` |
| `POST /files` | Create file/directory | `createFile()` |
| `POST /files/content` | Read file content | `getFileContent()` |
| `POST /files/save` | Save file content | `saveFileContent()` |
| `POST /files/compress` | Compress files | `compressFile()` |
| `POST /files/decompress` | Extract archive | `deCompressFile()` |
| `POST /files/favorite` | Add to favorites | `addFavorite()` |

**Sources:**
- [frontend/src/api/modules/files.ts:1-181]()

---

## Asynchronous Task Execution Pattern

Long-running infrastructure operations use a common task execution pattern to provide progress tracking and prevent request timeouts.

### Task Execution Flow

```mermaid
sequenceDiagram
    participant User as User
    participant Frontend as Vue Component
    participant API as Backend API
    participant Service as Service Layer
    participant TaskMgr as task.Task
    participant Docker as Docker Engine
    
    User->>Frontend: Click "Create Container"
    Frontend->>API: POST /containers<br/>{taskID, name, image}
    API->>Service: ContainerCreate(req)
    Service->>TaskMgr: NewTaskWithOps(name, TaskCreate)
    
    Service->>Service: taskItem.AddSubTask("Pull Image")
    Service->>Service: taskItem.AddSubTask("Create Container")
    Service-->>API: Return immediately
    API-->>Frontend: 200 OK
    
    Frontend->>Frontend: Open task log viewer
    Frontend->>API: GET /tasks/logs/{taskID}<br/>(Server-Sent Events)
    
    par Async Execution in Goroutine
        TaskMgr->>TaskMgr: Execute subtask 1
        TaskMgr->>Docker: client.ImagePull()
        TaskMgr->>TaskMgr: Log progress
        TaskMgr-->>Frontend: SSE: "Pulling image..."
        
        TaskMgr->>TaskMgr: Execute subtask 2
        TaskMgr->>Docker: client.ContainerCreate()
        TaskMgr->>Docker: client.ContainerStart()
        TaskMgr->>TaskMgr: Log completion
        TaskMgr-->>Frontend: SSE: "Container started"
    end
```

### Task System Implementation

The task system is defined in `app/task/task.go` and provides:

- **Task Creation**: `NewTaskWithOps(name, operate, scope, taskID, subTaskCount)` creates a task with a unique ID
- **Subtask Management**: `AddSubTask(name, func, rollback)` adds individual steps with optional rollback functions
- **Execution**: `Execute()` runs all subtasks sequentially, logging progress
- **Logging**: `Log(msg)`, `LogWithStatus(msg, err)`, `Logf(format, args)` write to task log
- **Streaming**: Frontend streams logs via Server-Sent Events from `/tasks/logs/:taskID`

**Task Scope Constants:**
- `TaskScopeContainer` - Container operations
- `TaskScopeImage` - Image operations  
- `TaskScopeDatabase` - Database operations
- `TaskScopeFile` - File operations

**Task Operation Types:**
- `TaskCreate`, `TaskUpdate`, `TaskUpgrade`, `TaskDelete`
- `TaskClean`, `TaskCommit`, `TaskRecover`

**Sources:**
- [agent/app/service/container.go:521-583]() (ContainerCreate with task)
- [agent/app/service/container.go:664-717]() (ContainerUpdate with task)
- [agent/app/service/container.go:719-793]() (ContainerUpgrade with task)

---

## Shared Frontend Patterns

### Database Selection Component Pattern

Both MySQL and Redis management UIs share a common pattern for selecting between local and remote databases:

```typescript
// Common pattern in MySQL and Redis views
const dbOptionsLocal = ref<Array<Database.DatabaseOption>>([]);
const dbOptionsRemote = ref<Array<Database.DatabaseOption>>([]);
const currentDB = ref<Database.DatabaseOption>();
const currentDBName = ref();

// Load available databases
const loadDBOptions = async () => {
    const res = await listDatabases('mysql,mariadb,mysql-cluster');
    // OR: await listDatabases('redis,redis-cluster');
    
    for (const item of res.data) {
        if (item.from === 'local') {
            dbOptionsLocal.value.push(item);
        } else {
            dbOptionsRemote.value.push(item);
        }
    }
};

// Switch between databases
const changeDatabase = async () => {
    currentDB.value = findDatabase(currentDBName.value);
    globalStore.setCurrentDB(currentDB.value.database);
};
```

The UI presents a dropdown with two option groups:
- **Local** - Databases running in Docker containers managed by 1Panel
- **Remote** - External database connections configured by the user

**Sources:**
- [frontend/src/views/database/mysql/index.vue:512-559]() (MySQL implementation)
- [frontend/src/views/database/redis/index.vue:247-288]() (Redis implementation)

### File Management Tab System

The file manager supports multiple concurrent browsing sessions through a tab system:

```typescript
interface Tab {
    id: string;        // Unique tab identifier
    name: string;      // Current directory name
    path: string;      // Full path
}

const editableTabs = ref<Tab[]>([]);
const editableTabsKey = ref('');  // Currently active tab

// Add new tab
const addTab = () => {
    const newTab = {
        id: `tab-${Date.now()}`,
        name: '',
        path: '/'
    };
    editableTabs.value.push(newTab);
    editableTabsKey.value = newTab.id;
};

// Switch tabs
const changeTab = (tabId: string) => {
    editableTabsKey.value = tabId;
    // Reload file list for this tab's path
};
```

Each tab maintains:
- Independent navigation history (back/forward)
- Separate file listings
- Own search filters and sorting

**Sources:**
- [frontend/src/views/host/file-management/index.vue:1-612]()

---

## Resource Monitoring Integration

Infrastructure components expose real-time resource metrics for monitoring.

### Container Stats Collection

The container service provides two levels of stats:

**System-Level Stats** via `ContainerItemStats`:
```go
// agent/app/service/container.go
func (u *ContainerService) ContainerItemStats(req dto.OperationWithName) (dto.ContainerItemStats, error) {
    if req.Name != "system" {
        // Single container stats
        containerInfo, _, err := client.ContainerInspectWithRaw(context.Background(), req.Name, true)
        data.SizeRw = *containerInfo.SizeRw
        data.SizeRootFs = *containerInfo.SizeRootFs
    } else {
        // System-wide disk usage
        usage, err := client.DiskUsage(context.Background(), types.DiskUsageOptions{})
        // Aggregate image, container, volume, build cache usage
    }
}
```

**Per-Container Live Stats** via `ContainerListStats`:
```go
func (u *ContainerService) ContainerListStats() ([]dto.ContainerListStats, error) {
    list, err := client.ContainerList(context.Background(), container.ListOptions{All: true})
    
    var wg sync.WaitGroup
    for _, item := range list {
        go func(item container.Summary) {
            datas = append(datas, loadCpuAndMem(client, item.ID))
            wg.Done()
        }(item)
    }
    wg.Wait()
}
```

Metrics collected: `cpuPercent`, `memoryUsage`, `memoryPercent`, `memoryCache`

**Sources:**
- [agent/app/service/container.go:238-281]() (ContainerItemStats)
- [agent/app/service/container.go:282-303]() (ContainerListStats)

### Database Connection Status

Database status is tracked through container health checks and direct connections:

```typescript
// MySQL status tracking
interface CheckInstalled {
    status: string;        // "Running", "Stopped", "Exited"
    version: string;       // "8.0.33"
    containerName: string; // "1panel-mysql-abc123"
}

// Redis status includes configuration
interface RedisStatus {
    tcp_port: string;
    uptime_in_days: string;
    connected_clients: string;
    used_memory: string;
    total_commands_processed: string;
}
```

Status checks occur:
- On component mount
- After configuration changes
- When switching between databases
- Every 3 seconds for dashboard metrics

**Sources:**
- [frontend/src/views/database/mysql/index.vue:506-510]()
- [frontend/src/views/database/redis/index.vue:116-118]()
- [frontend/src/api/interface/database.ts:242-256]()

---

## Configuration Management

Each infrastructure component supports configuration persistence and updates.

### Database Configuration Files

Configuration updates follow a validate-then-apply pattern:

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Service
    participant FS as File System
    participant Container
    
    User->>Frontend: Edit my.cnf
    Frontend->>API: POST /databases/common/update/conf<br/>{type, database, file}
    API->>Service: UpdateDBFile()
    Service->>FS: Write temp file
    Service->>Container: docker exec mysql-test -t config
    
    alt Config Valid
        Service->>FS: Overwrite actual config
        Service->>Container: docker restart
        Service-->>Frontend: Success
    else Config Invalid
        Service->>FS: Delete temp file
        Service-->>Frontend: Error with details
    end
```

Configuration endpoints for databases:

| Database | Config File Path | Validation Command |
|----------|-----------------|-------------------|
| MySQL/MariaDB | `/opt/1panel/apps/mysql/{name}/conf/my.cnf` | `mysqld --validate-config` |
| PostgreSQL | `/opt/1panel/apps/postgresql/{name}/data/postgresql.conf` | `postgres -C config_file` |
| Redis | `/opt/1panel/apps/redis/{name}/conf/redis.conf` | `redis-server --test-memory` |

**Sources:**
- [frontend/src/api/modules/database.ts:12-17]() (loadDBFile, updateDBFile)
- [frontend/src/views/database/mysql/setting/index.vue:249-274]() (MySQL config save)
- [frontend/src/views/database/redis/setting/index.vue:241-280]() (Redis config save)

### Container Network Configuration

Containers can be connected to multiple networks with specific IP configurations:

```typescript
interface ContainerNetwork {
    network: string;   // Network name
    ipv4: string;      // Static IPv4 address
    ipv6: string;      // Static IPv6 address
    macAddr: string;   // MAC address
}

// Example: Container with multiple networks
const networks: ContainerNetwork[] = [
    { network: "bridge", ipv4: "", ipv6: "", macAddr: "" },
    { network: "custom-net", ipv4: "172.20.0.10", ipv6: "", macAddr: "" }
];
```

Network types supported:
- **bridge** - Default Docker bridge network
- **host** - Host network mode (no isolation)
- **none** - No network
- **Custom** - User-defined networks with IPAM

**Sources:**
- [frontend/src/api/interface/container.ts:129-134]()
- [agent/app/dto/container.go:102-107]()
- [frontend/src/views/container/container/operate/index.vue:129-162]()

---

## Security and Access Control

Infrastructure management enforces multiple security layers.

### Database Permission Models

**MySQL Permission Scopes:**
- `%` - All hosts (dangerous)
- `localhost` - Local connections only
- Specific IP - Single IP address
- IP range - CIDR notation (e.g., `192.168.1.0/24`)

**PostgreSQL Permission Model:**
```typescript
interface PgBind {
    name: string;      // Database name
    database: string;  // Instance name
    username: string;
    password: string;
    superUser: boolean; // SUPERUSER privilege
}

interface PgChangePrivileges {
    username: string;
    superUser: boolean; // Toggle SUPERUSER
}
```

PostgreSQL distinguishes between:
- Regular users (database-level permissions)
- Superusers (cluster-wide administrative access)

**Sources:**
- [frontend/src/views/database/mysql/index.vue:611-637]() (MySQL permission change)
- [frontend/src/api/interface/database.ts:154-166]() (PostgreSQL permission types)

### Container Privileged Mode Warning

When creating containers with `privileged: true`, the system displays a prominent warning:

```vue
<el-form-item>
    <el-checkbox v-model="form.privileged">
        {{ $t('container.privileged') }}
    </el-checkbox>
    <span class="input-help">{{ $t('container.privilegedHelper') }}</span>
</el-form-item>
```

Privileged mode grants:
- Host device access
- Capability to manage other containers
- Bypass of security restrictions
- Full access to kernel features

**Sources:**
- [frontend/src/views/container/container/operate/index.vue:243-247]()

### File System Permission Management

The file manager provides detailed permission control:

```typescript
interface FileRole {
    paths: string[];   // Files to modify
    mode: number;      // Octal permissions (e.g., 0755)
    user: string;      // Owner username
    group: string;     // Group name
    sub: boolean;      // Apply recursively
}

// Change permissions
await batchChangeRole({
    paths: ["/var/www/html"],
    mode: 0755,
    user: "www-data",
    group: "www-data",
    sub: true
});
```

Permission display format: `-rwxr-xr-x` (mode: 755)

The UI allows clicking on mode/user/group to open modification dialogs.

**Sources:**
- [frontend/src/api/interface/file.ts:215-221]()
- [frontend/src/api/modules/files.ts:150-152]()
- [frontend/src/views/host/file-management/index.vue:523-540]()

---

## Summary

Infrastructure Management provides the foundational operational capabilities for 1Panel through three integrated subsystems. The architecture follows consistent patterns: Vue.js components call typed API methods that route through backend handlers to service layers, which interact with Docker, databases, and the file system. Long-running operations use the task system for async execution with progress streaming. For detailed information on each subsystem, refer to:

- [Container Management](#8.1) - Docker container, image, network, volume, and Compose operations
- [Database Management](#8.2) - MySQL/MariaDB, PostgreSQL, and Redis administration  
- [File Management System](#8.3) - Web-based file browser and Monaco code editor

---

# Page: Container Management

# Container Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/app/api/v2/container.go](agent/app/api/v2/container.go)
- [agent/app/dto/container.go](agent/app/dto/container.go)
- [agent/app/service/container.go](agent/app/service/container.go)
- [agent/router/ro_container.go](agent/router/ro_container.go)
- [frontend/src/api/interface/container.ts](frontend/src/api/interface/container.ts)
- [frontend/src/api/modules/container.ts](frontend/src/api/modules/container.ts)
- [frontend/src/views/container/container/operate/index.vue](frontend/src/views/container/container/operate/index.vue)

</details>



## Purpose and Scope

This document describes the Container Management subsystem within 1Panel's Infrastructure Management layer. It covers Docker container lifecycle operations (create, update, start, stop, remove), image management (pull, build, push, tag), network and volume orchestration, Docker Compose multi-container applications, and resource monitoring. 

For database container management specifically, see [Database Management](#7.2). For general file operations on container filesystems, see [File Management System](#7.3). For application deployment via containers, see [Application Management System](#6).

**Sources:** [agent/app/service/container.go:51-96](), [agent/app/dto/container.go:1-319]()

---

## System Architecture

The Container Management system wraps the Docker Engine API through a Go service layer that provides RESTful endpoints for the Vue frontend. All long-running operations use the task system for async execution with real-time logging.

### Component Structure

**Diagram 1: Container Management Architecture - Natural Language to Code Entity Mapping**

```mermaid
graph TB
    subgraph "Frontend Layer"
        ContainerOperate["Container Form Component<br/>views/container/container/operate/index.vue<br/>ContainerHelper interface"]
        APIClient["API Client Functions<br/>api/modules/container.ts<br/>createContainer()<br/>updateContainer()<br/>containerOperator()"]
        TypeDefs["TypeScript Interfaces<br/>api/interface/container.ts<br/>Container.ContainerHelper<br/>Container.ContainerInfo"]
    end
    
    subgraph "Backend API Layer"
        Router["ContainerRouter<br/>router/ro_container.go<br/>InitRouter()"]
        Handlers["BaseApi Handlers<br/>api/v2/container.go<br/>ContainerCreate()<br/>SearchContainer()<br/>ContainerOperation()"]
    end
    
    subgraph "Service Layer"
        IContainerService["IContainerService Interface<br/>service/container.go:53-96<br/>53 methods defined"]
        ContainerService["ContainerService Struct<br/>service/container.go:51<br/>implements IContainerService"]
    end
    
    subgraph "Data Layer"
        DTOs["Data Transfer Objects<br/>dto/container.go<br/>ContainerOperate:73-101<br/>ContainerInfo:23-44<br/>ComposeInfo:255-266"]
    end
    
    subgraph "Docker Integration"
        DockerClient["docker.NewDockerClient()<br/>utils/docker/<br/>returns *client.Client"]
        DockerAPICalls["Docker SDK API<br/>ContainerCreate()<br/>ContainerStart()<br/>ContainerList()<br/>ImagePull()"]
    end
    
    subgraph "Task Orchestration"
        TaskFactory["task.NewTaskWithOps()<br/>app/task/<br/>returns *Task"]
        TaskExecution["task.AddSubTask()<br/>task.Execute()<br/>Async goroutine execution"]
    end
    
    ContainerOperate --> APIClient
    APIClient --> TypeDefs
    APIClient --> Router
    Router --> Handlers
    Handlers --> IContainerService
    IContainerService --> ContainerService
    ContainerService --> DTOs
    Handlers --> DTOs
    ContainerService --> DockerClient
    DockerClient --> DockerAPICalls
    ContainerService --> TaskFactory
    TaskFactory --> TaskExecution
```

**Sources:** [agent/app/service/container.go:51-96](), [agent/app/api/v2/container.go:1-793](), [agent/router/ro_container.go:10-91](), [frontend/src/api/modules/container.ts:1-232](), [frontend/src/views/container/container/operate/index.vue:1-700]()

---

## Core Service Interface

The `IContainerService` interface ([agent/app/service/container.go:53-96]()) defines all container management operations. The `ContainerService` struct ([agent/app/service/container.go:51]()) implements this interface, wrapping Docker SDK calls with error handling, validation, and task orchestration.

### Service Methods Overview

**Diagram 2: IContainerService Interface Methods - Code Entity Reference**

| Category | Method Signatures | Return Types | Line References |
|----------|------------------|--------------|-----------------|
| **Container Lifecycle** | `ContainerCreate(dto.ContainerOperate, bool) error`<br/>`ContainerUpdate(dto.ContainerOperate) error`<br/>`ContainerOperation(dto.ContainerOperation) error`<br/>`ContainerUpgrade(dto.ContainerUpgrade) error` | `error` | [container.go:71-74]() |
| **Container Queries** | `Page(dto.PageContainer) (int64, interface{}, error)`<br/>`List() []dto.ContainerOptions`<br/>`ListByImage(string) []dto.ContainerOptions`<br/>`ContainerInfo(dto.OperationWithName) (*dto.ContainerOperate, error)`<br/>`LoadStatus() (dto.ContainerStatus, error)` | Various | [container.go:54-57]() |
| **Resource Management** | `PageNetwork(dto.SearchWithPage) (int64, interface{}, error)`<br/>`ListNetwork() ([]dto.Options, error)`<br/>`PageVolume(dto.SearchWithPage) (int64, interface{}, error)`<br/>`ListVolume() ([]dto.Options, error)`<br/>`CreateNetwork(dto.NetworkCreate) error`<br/>`DeleteNetwork(dto.BatchDelete) error`<br/>`CreateVolume(dto.VolumeCreate) error`<br/>`DeleteVolume(dto.BatchDelete) error` | Various | [container.go:58-90]() |
| **Compose Operations** | `PageCompose(dto.SearchWithPage) (int64, interface{}, error)`<br/>`CreateCompose(dto.ComposeCreate) error`<br/>`ComposeOperation(dto.ComposeOperation) error`<br/>`ComposeUpdate(dto.ComposeUpdate) error`<br/>`TestCompose(dto.ComposeCreate) (bool, error)` | Various | [container.go:63-68]() |
| **Monitoring** | `ContainerStats(string) (*dto.ContainerStats, error)`<br/>`ContainerListStats() ([]dto.ContainerListStats, error)`<br/>`ContainerItemStats(dto.OperationWithName) (dto.ContainerItemStats, error)`<br/>`LoadResourceLimit() (*dto.ResourceLimit, error)` | Stat structs | [container.go:76-78,84]() |
| **Utilities** | `ContainerRename(dto.ContainerRename) error`<br/>`ContainerCommit(dto.ContainerCommit) error`<br/>`Prune(dto.ContainerPrune) error`<br/>`ContainerLogClean(dto.OperationWithName) error`<br/>`Inspect(dto.InspectReq) (string, error)`<br/>`StreamLogs(*gin.Context, dto.StreamLog)` | Various | [container.go:79-81,86,95]() |

**Sources:** [agent/app/service/container.go:53-96]()

---

## Container Lifecycle Operations

### Container Creation

Container creation supports two modes: form-based creation via `ContainerCreate` and command-based creation via `ContainerCreateByCommand`.

#### Form-Based Creation Flow

**Diagram 3: Container Creation Sequence - Method Call Chain**

```mermaid
sequenceDiagram
    participant UI as "operate/index.vue<br/>onSubmit()"
    participant API as "container.ts<br/>createContainer()"
    participant Handler as "v2.BaseApi<br/>ContainerCreate()"
    participant Service as "ContainerService<br/>ContainerCreate()"
    participant Task as "task.Task<br/>AddSubTask()<br/>Execute()"
    participant Docker as "docker.Client<br/>SDK Methods"

    UI->>API: createContainer(ContainerHelper)
    API->>Handler: POST /api/v2/containers
    Handler->>Service: ContainerCreate(req, inThread=true)
    
    Note over Service: container.go:516<br/>Check name uniqueness
    Service->>Service: client.ContainerInspect(req.Name)
    
    Note over Service: container.go:521<br/>Create async task
    Service->>Task: task.NewTaskWithOps(name, TaskCreate, TaskScopeContainer, taskID, 1)
    
    Service-->>Handler: Return nil immediately
    Handler-->>API: HTTP 200
    API-->>UI: Show TaskLog component
    
    Note over Task: container.go:527<br/>Subtask 1: Pull image
    Task->>Task: AddSubTask("ContainerImagePull")
    Task->>Service: checkImageExist() or pullImages()
    Service->>Docker: client.ImagePull(req.Image)
    Docker-->>Task: Stream progress logs
    
    Note over Task: container.go:538<br/>Subtask 2: Check image
    Task->>Task: AddSubTask("ContainerImageCheck")
    Task->>Docker: client.ImageInspectWithRaw(req.Image)
    Docker-->>Task: imageInfo.Config
    Task->>Task: Set default Entrypoint/Cmd
    
    Note over Task: container.go:552<br/>Subtask 3: Create container
    Task->>Task: AddSubTask("ContainerCreate")
    Task->>Service: loadConfigInfo(true, req, nil)
    Service-->>Task: config, hostConf, networkConf
    Task->>Docker: client.ContainerCreate(config, hostConf, networkConf, name)
    Docker-->>Task: container.ID
    Task->>Docker: client.ContainerStart(container.ID)
    Docker-->>Task: Success
    
    Note over Task: container.go:576<br/>Execute in goroutine
    Task-->>UI: SSE stream task logs
```

**Key Implementation Details:**

1. **Validation** ([agent/app/service/container.go:516-519]()): `client.ContainerInspect(ctx, req.Name)` checks if container name already exists, returns `buserr.New("ErrContainerName")` if duplicate
2. **Task Creation** ([agent/app/service/container.go:521-525]()): `task.NewTaskWithOps(req.Name, task.TaskCreate, task.TaskScopeContainer, req.TaskID, 1)` creates orchestrator with 3 subtasks
3. **Image Pull Subtask** ([agent/app/service/container.go:527-536]()): Calls `checkImageExist(client, req.Image)` and `pullImages(taskItem, client, req.Image)` if needed or if `req.ForcePull` is true
4. **Image Inspection Subtask** ([agent/app/service/container.go:538-550]()): `client.ImageInspectWithRaw(ctx, req.Image)` retrieves `imageInfo.Config.Entrypoint` and `imageInfo.Config.Cmd` to use as defaults if not provided
5. **Container Creation Subtask** ([agent/app/service/container.go:552-572]()): 
   - `loadConfigInfo(true, req, nil)` converts `dto.ContainerOperate` to Docker SDK types `*container.Config`, `*container.HostConfig`, `*network.NetworkingConfig`
   - `client.ContainerCreate(ctx, config, hostConf, networkConf, &v1.Platform{}, req.Name)` creates container
   - `client.ContainerStart(ctx, con.ID, container.StartOptions{})` starts container
   - On failure: `client.ContainerRemove(ctx, req.Name, container.RemoveOptions{RemoveVolumes: true, Force: true})` cleans up
6. **Async Execution** ([agent/app/service/container.go:574-582]()): If `inThread=true`, launches `taskItem.Execute()` in goroutine, otherwise executes synchronously

**Sources:** [agent/app/service/container.go:509-583](), [agent/app/dto/container.go:73-101]()

#### Command-Based Creation

The `ContainerCreateByCommand` method ([agent/app/service/container.go:305-339]()) allows users to input raw `docker run` commands:

```go
// Example: docker run -d --name myapp nginx:latest
```

**Process:**
1. **Security Check** ([agent/app/service/container.go:306-308]()): `cmd.CheckIllegal(req.Command)` validates against command injection, returns `buserr.New("ErrCmdIllegal")` if dangerous
2. **Format Validation** ([agent/app/service/container.go:309-311]()): Ensures command starts with `"docker run "`
3. **Name Extraction** ([agent/app/service/container.go:312-318]()): Parses `--name` flag from command string by splitting on spaces and looking for index after `--name`
4. **Detach Flag** ([agent/app/service/container.go:319-321]()): If command lacks ` -d `, replaces `"docker run"` with `"docker run -d"`
5. **Name Generation** ([agent/app/service/container.go:322-325]()): If no `--name` found, appends `--name 1Panel-{random5}-{random4}` using `common.RandStr(5)` and `common.RandStrAndNum(4)`
6. **Task Execution** ([agent/app/service/container.go:326-337]()): Creates task with `task.NewTaskWithOps()`, adds single subtask that executes via `cmd.NewCommandMgr(cmd.WithTask(*taskItem), cmd.WithTimeout(5*time.Minute)).RunBashC(req.Command)`

**DTO Structure:**
```go
type ContainerCreateByCommand struct {
    TaskID  string `json:"taskID"`
    Command string `json:"command"`
}
```

**Sources:** [agent/app/service/container.go:305-339](), [agent/app/dto/container.go:109-112]()

### Container Update

Updating a container recreates it with new configuration while preserving the name.

**Diagram 4: Container Update Flow with Rollback**

```mermaid
graph TD
    A["ContainerUpdate(req)"] --> B["task.NewTaskWithOps()"]
    B --> C["Subtask 1: Image Pull"]
    C --> D["checkImageExist() or pullImages()"]
    D --> E["Subtask 2: Container Recreate"]
    E --> F["client.ContainerInspect(req.Name)"]
    F --> G["client.ContainerRemove(force=true)"]
    G --> H["loadConfigInfo(false, req, &oldContainer)"]
    H --> I{Config Valid?}
    I -->|Yes| J["client.ContainerCreate()"]
    I -->|No| K["reCreateAfterUpdate()"]
    J --> L["client.ContainerStart()"]
    L --> M{Started?}
    M -->|Yes| N["Update Complete"]
    M -->|No| O["Container created but not running"]
    K --> P["Restore old container from cached config"]
```

**Rollback Mechanism:** 

The `reCreateAfterUpdate()` helper function ([agent/app/service/container.go:2320-2349]()) provides rollback:
- Accepts `name`, `client`, `oldConfig *container.Config`, `oldHostConf *container.HostConfig`, `oldNetworkSettings *network.NetworkSettings`
- Reconstructs `networkConf` from `oldNetworkSettings.Networks` map
- Calls `client.ContainerCreate(ctx, oldConfig, oldHostConf, &networkConf, &v1.Platform{}, name)`
- Calls `client.ContainerStart(ctx, con.ID, container.StartOptions{})`
- Logs errors but continues to attempt restoration

**Implementation Details:**

1. **Async Task** ([agent/app/service/container.go:664-668]()): Entire update runs in goroutine, task created with `task.TaskUpdate` type
2. **Image Pull** ([agent/app/service/container.go:670-680]()): First subtask pulls new image if needed or `req.ForcePull` is true
3. **Container Removal** ([agent/app/service/container.go:683-687]()): `client.ContainerRemove(ctx, req.Name, container.RemoveOptions{Force: true})` removes old container, logs status
4. **Config Loading** ([agent/app/service/container.go:689-695]()): `loadConfigInfo(false, req, &oldContainer)` merges new config with old container's defaults. On error, calls `reCreateAfterUpdate(req.Name, client, oldContainer.Config, oldContainer.HostConfig, oldContainer.NetworkSettings)`
5. **Creation** ([agent/app/service/container.go:697-707]()): `client.ContainerCreate()` with new config, on error attempts rollback, then `client.ContainerStart()` with error logging

**Sources:** [agent/app/service/container.go:652-717](), [agent/app/service/container.go:2320-2349]()

### Container Operations

The `ContainerOperation` method ([agent/app/service/container.go:845-884]()) handles batch operations on multiple containers.

**Operation Mapping Table:**

| `req.Operation` Constant | Docker SDK Method Call | Parameters | Description |
|--------------------------|------------------------|------------|-------------|
| `constant.ContainerOpStart` | `client.ContainerStart(ctx, item, container.StartOptions{})` | Empty options | Start stopped container |
| `constant.ContainerOpStop` | `client.ContainerStop(ctx, item, container.StopOptions{})` | Empty options | Gracefully stop with SIGTERM |
| `constant.ContainerOpRestart` | `client.ContainerRestart(ctx, item, container.StopOptions{})` | Empty options | Stop then start |
| `constant.ContainerOpKill` | `client.ContainerKill(ctx, item, "SIGKILL")` | SIGKILL signal | Forcefully terminate |
| `constant.ContainerOpPause` | `client.ContainerPause(ctx, item)` | None | Suspend processes via cgroups |
| `constant.ContainerOpUnpause` | `client.ContainerUnpause(ctx, item)` | None | Resume paused processes |
| `constant.ContainerOpRemove` | `client.ContainerRemove(ctx, item, container.RemoveOptions{RemoveVolumes: true, Force: true})` | Remove volumes, force delete | Delete container and associated volumes |

**Implementation Flow:**

1. **Task Creation** ([agent/app/service/container.go:853-856]()): `task.NewTaskWithOps(strings.Join(req.Names, " "), req.Operation, task.TaskScopeContainer, req.TaskID, 1)` creates task named after all container names
2. **Subtask Loop** ([agent/app/service/container.go:858-878]()): For each container in `req.Names`, adds subtask with container name as title
3. **Operation Switch** ([agent/app/service/container.go:860-875]()): Switch statement on `req.Operation` dispatches to appropriate Docker SDK method
4. **Async Execution** ([agent/app/service/container.go:880-882]()): `taskItem.Execute()` runs in goroutine, operations execute serially for each container

**DTO Structure:**
```go
type ContainerOperation struct {
    TaskID    string   `json:"taskID"`
    Names     []string `json:"names" validate:"required"`
    Operation string   `json:"operation" validate:"required,oneof=up start stop restart kill pause unpause remove"`
}
```

**Sources:** [agent/app/service/container.go:845-884](), [agent/app/dto/container.go:174-178](), [agent/constant/]()*operation constants*

### Container Upgrade

`ContainerUpgrade` ([agent/app/service/container.go:719-793]()) updates multiple containers to a new image version while preserving their configuration.

**Process Flow:**

1. **Task Setup** ([agent/app/service/container.go:726-730]()): `task.NewTaskWithOps(req.Image, task.TaskUpgrade, task.TaskScopeImage, req.TaskID, 1)` creates task named after the new image
2. **Image Pull Subtask** ([agent/app/service/container.go:732-743]()): Single subtask pulls new image once for all containers using `pullImages(taskItem, client, req.Image)` if not exists or `req.ForcePull` is true
3. **Per-Container Upgrade Loop** ([agent/app/service/container.go:744-785]()): For each name in `req.Names`:
   - **Load Info Subtask** ([agent/app/service/container.go:746-753]()): `client.ContainerInspect(ctx, item)` retrieves `oldContainer` with current config
   - **Recreate Subtask** ([agent/app/service/container.go:755-784]()): 
     - Modifies `config.Image = req.Image` ([container.go:757]())
     - Preserves `hostConf` from old container
     - Reconstructs `networkConf` from first network in `oldContainer.NetworkSettings.Networks` map ([container.go:760-764]())
     - Removes old: `client.ContainerRemove(ctx, item, container.RemoveOptions{Force: true})` ([container.go:766]())
     - Creates new: `client.ContainerCreate(ctx, config, hostConf, &networkConf, &v1.Platform{}, item)` ([container.go:772]())
     - On error, attempts rollback via `reCreateAfterUpdate(item, client, oldContainer.Config, oldContainer.HostConfig, oldContainer.NetworkSettings)` ([container.go:775]())
     - Starts: `client.ContainerStart(ctx, con.ID, container.StartOptions{})` ([container.go:778]())
4. **Goroutine Execution** ([agent/app/service/container.go:787-790]()): Entire task executes in goroutine

**DTO Structure:**
```go
type ContainerUpgrade struct {
    TaskID    string   `json:"taskID"`
    Names     []string `json:"names" validate:"required"`
    Image     string   `json:"image" validate:"required"`
    ForcePull bool     `json:"forcePull"`
}
```

**Sources:** [agent/app/service/container.go:719-793](), [agent/app/dto/container.go:114-119]()

---

## Image Management

Image operations are exposed through the same service interface but use different Docker API endpoints.

### Image Operations

```mermaid
graph LR
    subgraph "Image Lifecycle"
        Build["imageBuild()<br/>Dockerfile → Image"]
        Pull["imagePull()<br/>Registry → Local"]
        Tag["imageTag()<br/>Add tags"]
        Push["imagePush()<br/>Local → Registry"]
        Save["imageSave()<br/>Image → .tar"]
        Load["imageLoad()<br/>.tar → Image"]
        Remove["imageRemove()<br/>Delete images"]
    end
    
    Build --> Tag
    Pull --> Tag
    Tag --> Push
    Tag --> Save
    Load --> Tag
```

### Image Pull

Image pulling streams progress updates to the task log:

**Implementation:**
- Uses `pullImages()` helper function ([agent/app/service/container.go:524-530]())
- Streams JSON progress events from Docker API
- Parses and logs progress percentage ([agent/app/service/container_image.go]()*not shown but referenced*)
- Supports pulling from custom registries configured via image repos

**Frontend Integration:**
```typescript
export const imagePull = (params: Container.ImagePull) => {
    return http.post<string>(`/containers/image/pull`, params);
};
```

**Sources:** [agent/app/service/container.go:523-532](), [frontend/src/api/modules/container.ts:96-98]()

### Image Build

Building images from Dockerfiles supports multiple source types:

**DTO Structure:**
```typescript
export interface ImageBuild {
    taskID: string;
    from: string;           // "edit" | "path" | "url"
    name: string;
    dockerfile: string;     // Content or path
    tags: Array<string>;
    args: Array<string>;    // Build args (KEY=VALUE)
}
```

**Sources:** [frontend/src/api/interface/container.ts:203-210]()

### Image Prune

The `Prune` operation removes unused Docker resources based on type:

**Prune Types:**
- `container`: Removes stopped containers
- `image`: Removes dangling images (or all with `WithTagAll=true`)
- `volume`: Removes unused volumes
- `network`: Removes unused networks
- `buildcache`: Removes build cache

**Implementation:** ([agent/app/service/container.go:404-486]())
- Uses Docker's prune APIs with filters
- Reports space reclaimed in human-readable format
- Executes asynchronously via task system

**Sources:** [agent/app/service/container.go:404-486](), [agent/app/dto/container.go:196-200]()

---

## Docker Compose Operations

Docker Compose orchestration manages multi-container applications defined in `docker-compose.yml` files.

### Compose Data Model

```mermaid
classDiagram
    class ComposeInfo {
        +string Name
        +string CreatedAt
        +string CreatedBy
        +int ContainerCount
        +int RunningCount
        +string ConfigFile
        +string Workdir
        +string Path
        +[]ComposeContainer Containers
        +string Env
    }
    
    class ComposeContainer {
        +string ContainerID
        +string Name
        +string CreateTime
        +string State
        +[]string Ports
    }
    
    class ComposeCreate {
        +string TaskID
        +string Name
        +string From
        +string File
        +string Path
        +uint Template
        +string Env
        +bool PullImage
    }
    
    class ComposeOperation {
        +string Name
        +string Path
        +string Operation
        +bool WithFile
        +bool Force
    }
    
    ComposeInfo "1" --> "*" ComposeContainer
```

**Sources:** [agent/app/dto/container.go:255-303]()

### Compose Creation Flow

```mermaid
sequenceDiagram
    participant UI as Frontend
    participant API as CreateCompose
    participant Service as ComposeService
    participant Task as Task System
    participant Compose as Compose Util
    participant Docker as Docker Engine

    UI->>API: ComposeCreate{name, from, file/path}
    API->>Service: CreateCompose(req)
    
    alt from == "template" or "edit"
        Service->>Service: loadPath(): Create dir and write file
        Note over Service: /opt/1panel/data/docker/compose/{name}/docker-compose.yml
    end
    
    Service->>Service: newComposeEnv(): Write .env file
    Service->>Task: task.NewTaskWithOps(name, TaskCreate, TaskScopeCompose)
    Service-->>API: Return immediately
    
    Task->>Compose: compose.UpWithTask(path, task, pullImages)
    Compose->>Docker: docker-compose up -d
    Docker-->>Compose: Stream logs
    Compose-->>Task: Log progress
    
    alt Success
        Task->>Service: composeRepo.CreateRecord()
        Note over Service: Store compose metadata in DB
    else Failure
        Task->>Compose: compose.Down(path)
        Note over Task: Cleanup failed compose
    end
    
    Task-->>UI: Task complete with logs
```

**Key Functions:**
- `loadPath()` ([agent/app/service/container_compose.go:345-366]()): Writes compose file from template or editor
- `newComposeEnv()` ([agent/app/service/container_compose.go:424-437]()): Creates `.env` file for compose variables
- `compose.UpWithTask()` ([agent/utils/compose/]()*): Executes `docker-compose up` with task logging

**Sources:** [agent/app/service/container_compose.go:189-225]()

### Compose Operations

The `ComposeOperation` method supports these operations:

| Operation | Command | Description |
|-----------|---------|-------------|
| `up` | `docker-compose up -d` | Create and start containers |
| `start` | `docker-compose start` | Start existing stopped containers |
| `restart` | `docker-compose restart` | Restart containers |
| `stop` | `docker-compose stop` | Stop containers without removing |
| `down` | `docker-compose down` | Stop and remove containers, networks |
| `delete` | `down` + remove files | Stop, remove, and delete compose files |

**Delete Operation:** When `WithFile=true`, deletes the entire compose directory after stopping containers ([agent/app/service/container_compose.go:239-247]()).

**Sources:** [agent/app/service/container_compose.go:227-259](), [agent/app/dto/container.go:284-290]()

### Compose Update

Updating a compose file follows this process:

1. **Backup Old File:** Read current `docker-compose.yml` ([agent/app/service/container_compose.go:265-267]())
2. **Write New Content:** Overwrite file with new content ([agent/app/service/container_compose.go:269-276]())
3. **Update Environment:** Write `.env` file ([agent/app/service/container_compose.go:279-281]())
4. **Execute Up:** Run `docker-compose up` to apply changes ([agent/app/service/container_compose.go:283-288]())
5. **Rollback on Failure:** If up fails, recreate old compose file ([agent/app/service/container_compose.go:392-406]())

**Sources:** [agent/app/service/container_compose.go:261-292]()

### Compose Discovery

The `PageCompose` method discovers compose projects from two sources:

1. **Docker Labels:** Queries containers with label `com.docker.compose.project` ([agent/app/service/container_compose.go:47-48]())
2. **Database Records:** Loads compose records created via 1Panel ([agent/app/service/container_compose.go:55-67]())

**Label Constants:**
```go
const composeProjectLabel = "com.docker.compose.project"
const composeConfigLabel = "com.docker.compose.project.config_files"
const composeWorkdirLabel = "com.docker.compose.project.working_dir"
const composeCreatedBy = "createdBy"
```

**Sources:** [agent/app/service/container_compose.go:30-165]()

---

## Network Management

Docker networks enable container communication and isolation.

### Network Data Structures

**Backend DTO:**
```go
type Network struct {
    ID         string
    Name       string
    Labels     []string
    Driver     string      // bridge, host, overlay, macvlan
    IPAMDriver string
    Subnet     string
    Gateway    string
    CreatedAt  time.Time
    Attachable bool
}

type NetworkCreate struct {
    Name       string
    Driver     string
    Options    []string
    Ipv4       bool
    Subnet     string
    Gateway    string
    IPRange    string
    Ipv6         bool
    SubnetV6     string
    GatewayV6    string
    IPRangeV6    string
    Labels       []string
}
```

**Sources:** [agent/app/dto/container.go:202-229]()

### Network Operations

#### Create Network

Network creation supports IPv4/IPv6 dual-stack configuration:

**API Endpoint:** `POST /api/v2/containers/network`

**Frontend Interface:**
```typescript
export const createNetwork = (params: Container.NetworkCreate) => {
    return http.post(`/containers/network`, params);
};
```

**Sources:** [frontend/src/api/modules/container.ts:125-127](), [agent/app/api/v2/container.go:612-623]()

#### List and Search Networks

- `ListNetwork()`: Returns simple name/ID pairs for dropdowns ([agent/app/service/container_network.go:]()*referenced*)
- `PageNetwork(req)`: Paginated search with filtering ([agent/app/service/container_network.go:]()*referenced*)

#### Delete Networks

Batch deletion via `DeleteNetwork(BatchDelete)` validates that networks are not in use before removal.

**Sources:** [agent/app/api/v2/container.go:590-601]()

---

## Volume Management

Docker volumes provide persistent storage for containers.

### Volume Data Structures

```go
type Volume struct {
    Name       string
    Labels     []VolumeOption
    Driver     string       // local, nfs, etc.
    Mountpoint string
    CreatedAt  time.Time
    Options    []VolumeOption
}

type VolumeCreate struct {
    Name    string
    Driver  string
    Options []string    // driver-specific options
    Labels  []string    // key=value pairs
}

type VolumeOption struct {
    Key   string
    Value string
}
```

**Sources:** [agent/app/dto/container.go:231-248]()

### Volume Operations

| Operation | Endpoint | Description |
|-----------|----------|-------------|
| Create | `POST /containers/volume` | Create named volume with driver options |
| List | `GET /containers/volume` | Get all volumes as option list |
| Search | `POST /containers/volume/search` | Paginated volume search |
| Delete | `POST /containers/volume/del` | Batch delete volumes by name |

**Volume Binding in Containers:**

When creating containers, volumes are specified via `VolumeHelper` in the DTO:

```go
type VolumeHelper struct {
    Type         string   // "bind", "volume", "tmpfs"
    SourceDir    string   // Host path or volume name
    ContainerDir string   // Container mount path
    Mode         string   // "ro", "rw"
    Shared       string   // Mount propagation
}
```

**Sources:** [agent/app/dto/container.go:160-166](), [agent/app/api/v2/container.go:699-710]()

---

## Resource Monitoring and Statistics

Container Management provides comprehensive resource monitoring at multiple levels.

### Status Overview

`LoadStatus()` returns aggregate statistics:

```mermaid
graph LR
    A["LoadStatus()"] --> B["Container Counts by State"]
    A --> C["Image Count"]
    A --> D["Network Count"]
    A --> E["Volume Count"]
    A --> F["Compose Count"]
    A --> G["Template Count"]
    A --> H["Repo Count"]
    
    B --> B1["Created<br/>Running<br/>Paused<br/>Restarting<br/>Dead<br/>Exited<br/>Removing"]
```

**Data Structure:**
```typescript
export interface ContainerStatus {
    created: number;
    running: number;
    paused: number;
    restarting: number;
    removing: number;
    exited: number;
    dead: number;
    
    containerCount: number;
    composeCount: number;
    composeTemplateCount: number;
    imageCount: number;
    networkCount: number;
    volumeCount: number;
    repoCount: number;
}
```

**Sources:** [agent/app/service/container.go:192-233](), [frontend/src/api/interface/container.ts:29-54]()

### Container Statistics

#### Individual Container Stats

`ContainerStats(id)` returns real-time resource usage for a single container:

**Metrics Calculated:**
- **CPU Percent:** `calculateCPUPercentUnix()` computes CPU usage from delta between samples ([agent/app/service/container.go:1208-1218]())
- **Memory Usage:** Current memory consumption minus cache
- **Cache:** Cached memory from `MemoryStats.Stats["cache"]`
- **Block I/O:** Read/write bytes via `calculateBlockIO()` ([agent/app/service/container.go:1220-1228]())
- **Network I/O:** RX/TX bytes via `calculateNetwork()` ([agent/app/service/container.go:1230-1245]())

**API Call:**
```typescript
export const containerStats = (id: string) => {
    return http.get<Container.ContainerStats>(`/containers/stats/${id}`);
};
```

**Sources:** [agent/app/service/container.go:1140-1170](), [frontend/src/api/modules/container.ts:60-62]()

#### List Container Stats

`ContainerListStats()` returns CPU and memory stats for all containers in parallel using goroutines:

**Implementation:**
```go
func (u *ContainerService) ContainerListStats() ([]dto.ContainerListStats, error) {
    // ... get container list
    var wg sync.WaitGroup
    wg.Add(len(list))
    for i := 0; i < len(list); i++ {
        go func(item container.Summary) {
            datas = append(datas, loadCpuAndMem(client, item.ID))
            wg.Done()
        }(list[i])
    }
    wg.Wait()
    return datas, nil
}
```

**Sources:** [agent/app/service/container.go:278-299]()

#### Container Item Stats

`ContainerItemStats(name)` returns disk usage information:

**For Individual Container:**
- `SizeRw`: Writable layer size
- `SizeRootFs`: Total container size

**For System ("system" name):**
- Container usage/reclaimable: Size of stopped containers
- Image usage/reclaimable: Size of unused images
- Volume usage/reclaimable: Size of unreferenced volumes
- Build cache usage: Size of build cache

**Sources:** [agent/app/service/container.go:234-277]()

### Resource Limits

`LoadResourceLimit()` returns host machine limits:

```go
type ResourceLimit struct {
    CPU    int     // Number of CPU cores
    Memory uint64  // Total memory in bytes
}
```

**Usage:** Frontend uses these limits to validate user input when setting container resource constraints (CPU quota, memory limit).

**Sources:** [agent/app/service/container.go:488-503](), [frontend/src/api/modules/container.ts:21-23]()

---

## Task System Integration

All long-running container operations integrate with the task system for async execution and progress tracking.

### Task Creation Pattern

```mermaid
sequenceDiagram
    participant Service as ContainerService
    participant TaskSys as task.NewTaskWithOps()
    participant SubTask as task.AddSubTask()
    participant Execute as task.Execute()
    participant UI as Frontend TaskLog

    Service->>TaskSys: Create task(name, type, scope, taskID, steps)
    TaskSys-->>Service: taskItem
    
    Service->>SubTask: AddSubTask("Image Pull", pullFunc, nil)
    Service->>SubTask: AddSubTask("Container Create", createFunc, nil)
    Service->>SubTask: AddSubTask("Container Start", startFunc, nil)
    
    Service->>Execute: Execute() in goroutine
    
    loop For each subtask
        Execute->>SubTask: Run function
        SubTask->>SubTask: Log progress
        SubTask-->>UI: Stream logs via SSE
    end
    
    Execute-->>UI: Task complete
```

### Task Scopes

Container operations use these task scopes:

- `TaskScopeContainer`: Single container operations
- `TaskScopeCompose`: Compose operations
- `TaskScopeImage`: Image operations

**Sources:** [agent/app/service/container.go:517-521](), [agent/app/service/container.go:322-333]()

### Task Operations

Task types for containers:

| Task Type | Usage |
|-----------|-------|
| `TaskCreate` | Container/compose creation |
| `TaskUpdate` | Container update |
| `TaskUpgrade` | Image upgrade |
| `TaskClean` | Prune operations |
| `TaskCommit` | Container commit to image |

**Sources:** [agent/app/task/]()*task types defined*

### Log Streaming

Container logs support real-time streaming via Server-Sent Events (SSE).

**API Endpoint:** `GET /api/v2/containers/search/log?container={name}&follow=true&tail=100&since=1h&timestamp=true`

**Diagram 5: Log Streaming Architecture**

```mermaid
sequenceDiagram
    participant Client as "Browser<br/>EventSource"
    participant Handler as "BaseApi<br/>ContainerStreamLogs()"
    participant Service as "ContainerService<br/>StreamLogs()"
    participant Collector as "collectLogs()<br/>Goroutine"
    participant Docker as "docker logs<br/>exec.Command"

    Client->>Handler: GET /containers/search/log?follow=true
    
    Note over Handler: container.go:765-769<br/>Set SSE headers
    Handler->>Handler: Set Content-Type: text/event-stream
    Handler->>Handler: Set Cache-Control: no-cache
    
    Handler->>Service: StreamLogs(ctx, dto.StreamLog)
    Service->>Service: Create channels: messageChan, errorChan, doneChan
    
    Service->>Collector: Launch goroutine collectLogs()
    
    Note over Collector: container.go:954-970<br/>Build docker logs command
    Collector->>Collector: Build cmdArgs from params
    Collector->>Docker: exec.Command("docker", cmdArgs...)
    Collector->>Docker: dockerCmd.Start()
    
    Note over Docker: Stream stdout/stderr
    Docker-->>Collector: Read lines via bufio.NewReader
    
    loop Stream logs
        Collector->>Service: messageChan <- line
        Service->>Handler: Stream via ctx.Stream()
        Handler->>Client: data: {log line}\n\n
    end
    
    Note over Client: Client disconnects
    Client->>Service: Request context cancelled
    Service->>Collector: Close doneChan
    Collector->>Docker: syscall.Kill(-pgid, SIGKILL)
    Collector->>Service: Close messageChan, errorChan
```

**Implementation Details:**

1. **Handler Setup** ([agent/app/api/v2/container.go:765-792]()): 
   - `ContainerStreamLogs(c *gin.Context)` sets SSE response headers
   - Parses query params: `since`, `follow`, `tail`, `timestamp`, `container`, `compose`
   - Creates `dto.StreamLog` struct with `Type: "container"` or `"compose"`
   - Calls `containerService.StreamLogs(c, streamLog)`

2. **Service Orchestration** ([agent/app/service/container.go:921-949]()): 
   - Creates channels: `messageChan chan string`, `errorChan chan error`, `doneChan chan struct{}`
   - Launches goroutine monitoring `c.Request.Context().Done()` to close `doneChan` on client disconnect
   - Launches `collectLogs(doneChan, params, messageChan, errorChan)` goroutine
   - Uses `c.Stream()` callback to write SSE events: `fmt.Fprintf(w, "data: %s\n\n", msg)`

3. **Log Collection** ([agent/app/service/container.go:951-1056]()): 
   - Builds command args: `docker logs [-f] [-t] [--tail N] [--since TIME] CONTAINER`
   - For compose: Uses `docker-compose` or `docker compose` with `-f` yaml files ([container.go:973-987]())
   - Sets `SysProcAttr{Setpgid: true}` for process group management ([container.go:992]())
   - Creates `stdout` pipe via `dockerCmd.StdoutPipe()` ([container.go:994]())
   - Starts command with `dockerCmd.Start()` ([container.go:1002]())
   - Reads lines using `bufio.NewReader(stdout).ReadString('\n')` ([container.go:1017,1032]())
   - On `doneChan` close, kills entire process group: `syscall.Kill(-pgid, syscall.SIGKILL)` ([container.go:1020-1028]())
   - Closes channels when EOF reached ([container.go:1034-1043]())

4. **Process Cleanup** ([agent/app/service/container.go:1007-1015]()): Defer function ensures `dockerCmd.Process.Kill()` and `dockerCmd.Wait()` are called even on panic

**Query Parameters:**
- `container`: Container name (for type="container")
- `compose`: Comma-separated yaml paths (for type="compose")
- `since`: Time filter (e.g., "1h", "30m", "2024-01-01")
- `follow`: Boolean, if true streams continuously
- `tail`: Number of lines from end (e.g., "100", "all")
- `timestamp`: Boolean, if true includes timestamps

**Sources:** [agent/app/service/container.go:921-1056](), [agent/app/api/v2/container.go:765-792](), [agent/app/dto/container.go:314-322]()

---

## API Endpoints Reference

The container management REST API is organized under `/api/v2/containers/` with the following route structure:

### Container Endpoints

| Method | Path | Handler | Description |
|--------|------|---------|-------------|
| POST | `/containers` | `ContainerCreate` | Create new container |
| POST | `/containers/command` | `ContainerCreateByCommand` | Create from docker run command |
| POST | `/containers/search` | `SearchContainer` | Paginated container search |
| POST | `/containers/list` | `ListContainer` | List all containers |
| POST | `/containers/list/byimage` | `ListContainerByImage` | Filter by image |
| POST | `/containers/info` | `ContainerInfo` | Get container details |
| POST | `/containers/update` | `ContainerUpdate` | Update container config |
| POST | `/containers/upgrade` | `ContainerUpgrade` | Upgrade to new image |
| POST | `/containers/operate` | `ContainerOperation` | Start/stop/restart/etc |
| POST | `/containers/rename` | `ContainerRename` | Rename container |
| POST | `/containers/commit` | `ContainerCommit` | Commit to image |
| POST | `/containers/prune` | `ContainerPrune` | Clean unused resources |
| POST | `/containers/clean/log` | `CleanContainerLog` | Clear container logs |
| POST | `/containers/inspect` | `Inspect` | Docker inspect |
| GET | `/containers/status` | `LoadContainerStatus` | Status overview |
| GET | `/containers/limit` | `LoadResourceLimit` | Host resource limits |
| GET | `/containers/stats/:id` | `ContainerStats` | Container statistics |
| GET | `/containers/list/stats` | `ContainerListStats` | All container stats |
| POST | `/containers/item/stats` | `ContainerItemStats` | Disk usage stats |
| GET | `/containers/search/log` | `ContainerStreamLogs` | Stream logs (SSE) |
| POST | `/containers/download/log` | `DownloadContainerLogs` | Download logs |

**Sources:** [agent/router/ro_container.go:10-90](), [agent/app/api/v2/container.go:1-770]()

### Image Endpoints

| Method | Path | Handler | Description |
|--------|------|---------|-------------|
| GET | `/containers/image` | `ListImage` | Image options for dropdown |
| GET | `/containers/image/all` | `ListAllImage` | All images with details |
| POST | `/containers/image/search` | `SearchImage` | Paginated search |
| POST | `/containers/image/pull` | `ImagePull` | Pull from registry |
| POST | `/containers/image/push` | `ImagePush` | Push to registry |
| POST | `/containers/image/build` | `ImageBuild` | Build from Dockerfile |
| POST | `/containers/image/save` | `ImageSave` | Export to .tar |
| POST | `/containers/image/load` | `ImageLoad` | Import from .tar |
| POST | `/containers/image/tag` | `ImageTag` | Add tags to image |
| POST | `/containers/image/remove` | `ImageRemove` | Delete images |

**Sources:** [agent/router/ro_container.go:61-70]()

### Network Endpoints

| Method | Path | Handler | Description |
|--------|------|---------|-------------|
| GET | `/containers/network` | `ListNetwork` | List network options |
| POST | `/containers/network/search` | `SearchNetwork` | Paginated search |
| POST | `/containers/network` | `CreateNetwork` | Create network |
| POST | `/containers/network/del` | `DeleteNetwork` | Delete networks |

**Sources:** [agent/router/ro_container.go:72-75]()

### Volume Endpoints

| Method | Path | Handler | Description |
|--------|------|---------|-------------|
| GET | `/containers/volume` | `ListVolume` | List volume options |
| POST | `/containers/volume/search` | `SearchVolume` | Paginated search |
| POST | `/containers/volume` | `CreateVolume` | Create volume |
| POST | `/containers/volume/del` | `DeleteVolume` | Delete volumes |

**Sources:** [agent/router/ro_container.go:76-79]()

### Compose Endpoints

| Method | Path | Handler | Description |
|--------|------|---------|-------------|
| POST | `/containers/compose/search` | `SearchCompose` | List compose projects |
| POST | `/containers/compose` | `CreateCompose` | Create compose |
| POST | `/containers/compose/test` | `TestCompose` | Validate compose file |
| POST | `/containers/compose/operate` | `OperatorCompose` | Up/down/start/stop |
| POST | `/containers/compose/update` | `ComposeUpdate` | Update compose file |
| POST | `/containers/compose/clean/log` | `CleanComposeLog` | Clear compose logs |

**Sources:** [agent/router/ro_container.go:47-52]()

### Compose Template Endpoints

Templates are pre-saved compose files for quick deployment:

| Method | Path | Handler |
|--------|------|---------|
| GET | `/containers/template` | `ListComposeTemplate` |
| POST | `/containers/template/search` | `SearchComposeTemplate` |
| POST | `/containers/template` | `CreateComposeTemplate` |
| POST | `/containers/template/update` | `UpdateComposeTemplate` |
| POST | `/containers/template/batch` | `BatchComposeTemplate` |
| POST | `/containers/template/del` | `DeleteComposeTemplate` |

**Sources:** [agent/router/ro_container.go:54-59]()

### Image Repository Endpoints

Image repos configure custom Docker registries:

| Method | Path | Handler |
|--------|------|---------|
| GET | `/containers/repo` | `ListRepo` |
| POST | `/containers/repo/search` | `SearchRepo` |
| POST | `/containers/repo` | `CreateRepo` |
| POST | `/containers/repo/update` | `UpdateRepo` |
| POST | `/containers/repo/status` | `CheckRepoStatus` |
| POST | `/containers/repo/del` | `DeleteRepo` |

**Sources:** [agent/router/ro_container.go:40-45]()

---

## Frontend Implementation

The frontend provides comprehensive UI for container management through Vue components.

### Container Form Component

The main container create/edit form is located at `frontend/src/views/container/container/operate/index.vue`.

**Key Features:**
1. **Dual Mode:** Create vs Edit, with edit blocking certain fields ([frontend/src/views/container/container/operate/index.vue:5](), [frontend/src/views/container/container/operate/index.vue:362]())
2. **Image Selection:** Dropdown or manual input via checkbox ([frontend/src/views/container/container/operate/index.vue:51-68]())
3. **Port Mapping:** Table-based UI for exposing ports ([frontend/src/views/container/container/operate/index.vue:88-125]())
4. **Tabbed Configuration:**
   - Network (hostname, DNS, multi-network support)
   - Volume (mount points)
   - Command (entrypoint, cmd, working dir)
   - Resource (CPU shares, CPU quota, memory limit)
   - Labels & Environment
   - Restart Policy

**Validation Rules:**
```typescript
const rules = reactive({
    name: [Rules.requiredInput, Rules.containerName],
    image: [Rules.imageName],
    cpuShares: [Rules.integerNumberWith0, checkNumberRange(0, 262144)],
    nanoCPUs: [Rules.floatNumber],
    memory: [Rules.floatNumber],
});
```

**Sources:** [frontend/src/views/container/container/operate/index.vue:469-475](), [frontend/src/views/container/container/operate/index.vue:1-700]()

### Container List View

Container listing supports:
- Filtering by state (running, stopped, etc.)
- Search by name
- App/Website associations displayed
- Real-time stats (CPU%, Memory%)
- Batch operations (start, stop, remove)

**Sources:** [frontend/src/views/container/container/index.vue]()*referenced*

### Task Log Integration

Long-running operations open a `TaskLog` component that polls for progress:

```typescript
// After operation starts
taskLogRef.value.acceptParams({
    taskID: form.taskID,
    title: 'Container Creation'
});
```

The component displays real-time logs streamed from the backend via periodic polling or SSE.

**Sources:** [frontend/src/views/container/container/operate/index.vue:327-332]()

---

## Error Handling and Validation

### Input Validation

1. **Command Injection Prevention:** `cmd.CheckIllegal()` scans for dangerous shell characters ([agent/app/service/container.go:302]())
2. **Container Name Uniqueness:** Checks if name already exists before creation ([agent/app/service/container.go:512-515]())
3. **Resource Limits:** Frontend validates CPU/memory against host limits ([frontend/src/views/container/container/operate/index.vue:218-241]())

### Error Recovery

1. **Container Update Rollback:** If update fails, recreates original container ([agent/app/service/container.go:688-697]())
2. **Compose Update Rollback:** If compose up fails, restores old compose file ([agent/app/service/container_compose.go:284-288]())
3. **Creation Cleanup:** Failed container creation removes partial resources ([agent/app/service/container.go:557-565]())

**Sources:** [agent/app/service/container.go:648-713](), [agent/app/service/container_compose.go:261-292]()

---

## Data Transfer Objects

### Key DTOs

**ContainerOperate** - Full container configuration:
```go
type ContainerOperate struct {
    TaskID    string
    ForcePull bool
    Name      string
    Image     string
    
    // Network
    Hostname   string
    DomainName string
    DNS        []string
    Networks   []ContainerNetwork
    
    // Ports
    PublishAllPorts bool
    ExposedPorts    []PortHelper
    
    // Runtime
    Tty             bool
    OpenStdin       bool
    WorkingDir      string
    User            string
    Cmd             []string
    Entrypoint      []string
    
    // Resources
    CPUShares       int64
    NanoCPUs        float64
    Memory          float64
    Privileged      bool
    AutoRemove      bool
    
    // Storage
    Volumes         []VolumeHelper
    
    // Metadata
    Labels          []string
    Env             []string
    RestartPolicy   string
}
```

**ContainerInfo** - List view data:
```go
type ContainerInfo struct {
    ContainerID string
    Name        string
    ImageId     string
    ImageName   string
    CreateTime  string
    State       string
    RunTime     string
    Network     []string
    Ports       []string
    
    IsFromApp     bool
    IsFromCompose bool
    
    AppName        string
    AppInstallName string
    Websites       []string
}
```

**Sources:** [agent/app/dto/container.go:73-101](), [agent/app/dto/container.go:23-44]()

---

## Integration Points

### Application Management Integration

Containers created via the Application Management system ([#6](#6)) are linked to app installs:

**Backend Logic:**
```go
install, _ := appInstallRepo.GetFirst(appInstallRepo.WithContainerName(backData[i].Name))
if install.ID > 0 {
    backData[i].AppInstallName = install.Name
    backData[i].AppName = install.App.Name
    websites, _ := websiteRepo.GetBy(websiteRepo.WithAppInstallId(install.ID))
    // Link websites using this app
}
```

**Sources:** [agent/app/service/container.go:127-136]()

### Website Management Integration

Websites ([#5](#5)) may be associated with app containers:

**Display:** Container list shows which websites use a container ([agent/app/service/container.go:131-135]())

**Warning:** Containers from apps display a warning in the edit UI about modifying managed containers ([frontend/src/views/container/container/operate/index.vue:19-24]())

### File Management Integration

Terminal access to containers is provided via the File Management terminal component ([#7.3](#7.3)):

**Command Input Mode:** Clicking "Command Input" button opens terminal for direct docker command execution ([frontend/src/views/container/container/operate/index.vue:26-28](), [frontend/src/views/container/container/operate/index.vue:488-490]())

**Sources:** [frontend/src/views/container/container/operate/index.vue:358](), [frontend/src/views/container/container/operate/index.vue:488-490]()

---

# Page: Database Management

# Database Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [frontend/src/api/interface/database.ts](frontend/src/api/interface/database.ts)
- [frontend/src/api/modules/database.ts](frontend/src/api/modules/database.ts)
- [frontend/src/views/database/mysql/index.vue](frontend/src/views/database/mysql/index.vue)
- [frontend/src/views/database/mysql/setting/index.vue](frontend/src/views/database/mysql/setting/index.vue)
- [frontend/src/views/database/redis/index.vue](frontend/src/views/database/redis/index.vue)
- [frontend/src/views/database/redis/setting/index.vue](frontend/src/views/database/redis/setting/index.vue)

</details>



## Purpose and Scope

This document describes the Database Management system in 1Panel, which provides unified management interfaces for MySQL/MariaDB, PostgreSQL, and Redis databases. The system supports both locally-installed databases (Docker-based) and externally-hosted remote databases, offering operations such as database creation, user management, configuration editing, performance tuning, and backup/restore integration.

For container-level operations on database containers, see [Container Management](#8.1). For backup and restore operations, see [Backup and Snapshot System](#10.3). For application installation of database services, see [App Installation and Deployment](#6.2).

---

## System Architecture

The Database Management system integrates with both local Docker-based databases and remote database instances. It provides type-specific management interfaces while sharing common operations like backup and connection management.

```mermaid
graph TB
    subgraph "Frontend Layer"
        MySQLView["MySQL/MariaDB View<br/>/views/database/mysql/index.vue"]
        PgView["PostgreSQL View<br/>/views/database/pg/index.vue"]
        RedisView["Redis View<br/>/views/database/redis/index.vue"]
        SettingsView["Settings Views<br/>setting/index.vue"]
        RemoteView["Remote DB Views<br/>remote/index.vue"]
    end
    
    subgraph "API Client Layer"
        DBClient["Database API Client<br/>/api/modules/database.ts"]
        DBTypes["TypeScript Interfaces<br/>/api/interface/database.ts"]
    end
    
    subgraph "Backend Services"
        MySQLSvc["MySQL Service<br/>backend/app/service/database.go"]
        PgSvc["PostgreSQL Service<br/>backend/app/service/postgresql.go"]
        RedisSvc["Redis Service<br/>backend/app/service/redis.go"]
        RemoteSvc["Remote Database Service<br/>backend/app/service/database_remote.go"]
    end
    
    subgraph "Data Layer"
        AgentDB[("agent.db SQLite<br/>mysql/postgresql/redis tables")]
    end
    
    subgraph "External Systems"
        DockerMySQL["Docker Container<br/>MySQL/MariaDB"]
        DockerPg["Docker Container<br/>PostgreSQL"]
        DockerRedis["Docker Container<br/>Redis"]
        RemoteDB["Remote Databases<br/>External instances"]
    end
    
    subgraph "Management Tools"
        Terminal["Terminal Component<br/>Redis CLI"]
        phpMyAdmin["phpMyAdmin<br/>Web management"]
        Adminer["Adminer<br/>Universal tool"]
    end
    
    MySQLView --> DBClient
    PgView --> DBClient
    RedisView --> DBClient
    SettingsView --> DBClient
    RemoteView --> DBClient
    
    DBClient --> DBTypes
    DBClient --> MySQLSvc
    DBClient --> PgSvc
    DBClient --> RedisSvc
    DBClient --> RemoteSvc
    
    MySQLSvc --> AgentDB
    PgSvc --> AgentDB
    RedisSvc --> AgentDB
    RemoteSvc --> AgentDB
    
    MySQLSvc --> DockerMySQL
    PgSvc --> DockerPg
    RedisSvc --> DockerRedis
    RemoteSvc --> RemoteDB
    
    MySQLView -.launches.-> phpMyAdmin
    MySQLView -.launches.-> Adminer
    RedisView --> Terminal
    Terminal --> DockerRedis
```

**Diagram: Database Management Architecture**

The frontend provides type-specific views for each database engine, connecting through a unified API client layer to backend services. Local databases are managed through Docker containers, while remote databases connect directly to external instances. The system stores metadata in the SQLite `agent.db` database.

Sources: [frontend/src/views/database/mysql/index.vue:1-680](), [frontend/src/views/database/redis/index.vue:1-423](), [frontend/src/api/modules/database.ts:1-200](), [frontend/src/api/interface/database.ts:1-363]()

---

## Database Types and Sources

1Panel supports two primary sources for databases:

| Source | Description | Management Scope |
|--------|-------------|------------------|
| **local** | Docker-based databases installed through the App Store | Full lifecycle management: install, configure, start/stop, upgrade, uninstall |
| **remote** | External databases hosted elsewhere | Connection management, database/user creation, limited configuration |

### Supported Database Types

```mermaid
graph LR
    subgraph "MySQL Family"
        MySQL["mysql<br/>MySQL Community"]
        MariaDB["mariadb<br/>MariaDB Server"]
        MySQLCluster["mysql-cluster<br/>MySQL Cluster"]
    end
    
    subgraph "PostgreSQL Family"
        PG["postgresql<br/>PostgreSQL"]
    end
    
    subgraph "Redis Family"
        Redis["redis<br/>Redis Server"]
        RedisCluster["redis-cluster<br/>Redis Cluster"]
    end
    
    DatabaseSelector["Database Type Selector<br/>listDatabases API"]
    
    DatabaseSelector --> MySQL
    DatabaseSelector --> MariaDB
    DatabaseSelector --> MySQLCluster
    DatabaseSelector --> PG
    DatabaseSelector --> Redis
    DatabaseSelector --> RedisCluster
```

**Diagram: Supported Database Types**

Each database type can be installed locally as a Docker container or registered as a remote connection. The `listDatabases` API returns available instances grouped by source.

Sources: [frontend/src/api/modules/database.ts:157-160](), [frontend/src/views/database/mysql/index.vue:514-559]()

---

## MySQL/MariaDB Management

### Database Operations

The MySQL management interface provides comprehensive operations for database lifecycle management.

```mermaid
graph TB
    subgraph "Database CRUD Operations"
        CreateDB["Create Database<br/>addMysqlDB()"]
        SearchDB["Search Databases<br/>searchMysqlDBs()"]
        UpdateDesc["Update Description<br/>updateMysqlDescription()"]
        DeleteDB["Delete Database<br/>deleteMysqlDB()"]
        DeleteCheck["Delete Check<br/>deleteCheckMysqlDB()"]
    end
    
    subgraph "User Management"
        BindUser["Bind User<br/>bindUser()"]
        ChangePassword["Change Password<br/>updateMysqlPassword()"]
        ChangeAccess["Change Access<br/>updateMysqlAccess()"]
    end
    
    subgraph "Remote Sync"
        LoadRemote["Load from Remote<br/>loadDBFromRemote()"]
    end
    
    subgraph "Database Properties"
        DBName["name: string"]
        DBFormat["format: utf8mb4"]
        Username["username: string"]
        Password["password: Base64"]
        Permission["permission: %/localhost/IP"]
        Description["description: string"]
    end
    
    CreateDB --> DBName
    CreateDB --> DBFormat
    CreateDB --> Username
    CreateDB --> Password
    CreateDB --> Permission
    CreateDB --> Description
    
    BindUser --> Username
    BindUser --> Password
    ChangePassword --> Password
    ChangeAccess --> Permission
    
    DeleteCheck -.checks for.-> DeleteDB
    LoadRemote -.imports.-> CreateDB
```

**Diagram: MySQL Database Operations Flow**

The `addMysqlDB` operation creates a database with optional user binding. Passwords are Base64-encoded before transmission. The `deleteCheckMysqlDB` function verifies if databases are in use before deletion.

Sources: [frontend/src/api/modules/database.ts:58-100](), [frontend/src/api/interface/database.ts:42-51]()

### User Management and Permissions

MySQL databases support flexible user binding and permission models:

```mermaid
graph LR
    subgraph "User Binding States"
        NoUser["No User Bound<br/>username: empty"]
        BoundUser["User Bound<br/>username: set"]
        NoPassword["No Password Set<br/>password: empty"]
        HasPassword["Password Set<br/>password: ******"]
    end
    
    subgraph "Permission Modes"
        AllHosts["All Hosts<br/>permission: %"]
        LocalOnly["Local Only<br/>permission: localhost"]
        SpecificIP["Specific IPs<br/>permission: 192.168.1.100"]
    end
    
    subgraph "UI Actions"
        BindAction["Bind User Button<br/>onBind()"]
        PasswordAction["Change Password<br/>onChangePassword()"]
        PrivilegeAction["Change Privilege<br/>updateMysqlAccess()"]
    end
    
    NoUser --> BindAction
    BindAction --> BoundUser
    BoundUser --> NoPassword
    NoPassword --> PasswordAction
    PasswordAction --> HasPassword
    
    HasPassword --> PrivilegeAction
    PrivilegeAction --> AllHosts
    PrivilegeAction --> LocalOnly
    PrivilegeAction --> SpecificIP
```

**Diagram: MySQL User Management Flow**

Databases can exist without users (for phpMyAdmin-only access). The binding process creates a MySQL user with specified permissions. The `permission` field controls host-based access: `%` for all hosts, `localhost` for local-only, or specific IP addresses.

Sources: [frontend/src/views/database/mysql/index.vue:579-636](), [frontend/src/api/interface/database.ts:53-59]()

### Configuration and Settings

The MySQL settings interface provides multiple configuration areas:

| Tab | Description | API Endpoint | Requires Running |
|-----|-------------|--------------|------------------|
| **status** | Real-time status metrics | `loadMysqlStatus()` | Yes |
| **conf** | Edit configuration file | `loadDBFile()`, `updateDBFile()` | No |
| **tuning** | Performance variables | `loadMysqlVariables()`, `updateMysqlVariables()` | Yes |
| **port** | Change service port | `changePort()` | No |
| **log** | Container logs | Container log stream | Yes |
| **slowLog** | Slow query analysis | Slow log parsing | Yes |

```mermaid
graph TB
    subgraph "Configuration Management"
        LoadConf["Load Config<br/>loadDBFile('mysql-conf')"]
        EditConf["Edit in Monaco<br/>CodemirrorPro component"]
        ValidateConf["Save Config<br/>updateDBFile()"]
        RestartPrompt["Confirm Restart<br/>ConfirmDialog"]
        ApplyConf["Restart Container<br/>Docker restart"]
    end
    
    subgraph "Variable Tuning"
        LoadVars["Load Variables<br/>loadMysqlVariables()"]
        EditVars["Edit Performance<br/>innodb_buffer_pool_size<br/>max_connections<br/>etc."]
        SaveVars["Update Variables<br/>updateMysqlVariables()"]
    end
    
    LoadConf --> EditConf
    EditConf --> ValidateConf
    ValidateConf --> RestartPrompt
    RestartPrompt --> ApplyConf
    
    LoadVars --> EditVars
    EditVars --> SaveVars
    SaveVars --> RestartPrompt
```

**Diagram: MySQL Configuration Management**

Configuration changes require container restart, triggered through a confirmation dialog. The system loads default configurations via `getAppDefaultConfig()` for reference.

Sources: [frontend/src/views/database/mysql/setting/index.vue:1-343](), [frontend/src/api/modules/database.ts:102-114]()

### Performance Monitoring

The status view displays real-time MySQL metrics:

```typescript
interface MysqlStatus {
    Aborted_clients: number;           // Client connection aborts
    Aborted_connects: number;          // Connection attempt failures
    Bytes_received: number;            // Total bytes received
    Bytes_sent: number;                // Total bytes sent
    Com_commit: number;                // Commit statements
    Com_rollback: number;              // Rollback statements
    Connections: number;               // Total connection attempts
    Created_tmp_disk_tables: number;   // Temp tables on disk
    Created_tmp_tables: number;        // Total temp tables
    Innodb_buffer_pool_pages_dirty: number;
    Innodb_buffer_pool_read_requests: number;
    Innodb_buffer_pool_reads: number;
    Key_read_requests: number;
    Key_reads: number;
    Key_write_requests: number;
    Key_writes: number;
    Max_used_connections: number;
    Open_tables: number;
    Opened_files: number;
    Opened_tables: number;
    Qcache_hits: number;               // Query cache hits
    Qcache_inserts: number;            // Query cache inserts
    Questions: number;                 // Total queries
    Threads_connected: number;         // Current connections
    Threads_running: number;           // Active threads
    Uptime: number;                    // Server uptime in seconds
    Run: number;                       // Binlog position
    File: string;                      // Binlog file name
    Position: number;                  // Binlog position
}
```

Sources: [frontend/src/api/interface/database.ts:108-144]()

### Terminal and Management Tools

MySQL databases integrate with web-based management tools:

```mermaid
graph LR
    subgraph "Management Tools"
        PHPMyAdmin["phpMyAdmin App"]
        Adminer["Adminer App"]
    end
    
    subgraph "Access Flow"
        CheckInstalled["Check App Installed<br/>getAppPort()"]
        GetPort["Get Port Number<br/>phpadminPort/adminerPort"]
        OpenPortJump["Open Port Jump Dialog<br/>PortJumpDialog"]
        AccessTool["Access Tool UI<br/>Browser redirect"]
    end
    
    subgraph "Terminal Access"
        TerminalBtn["Terminal Button<br/>goTerminal()"]
        OpenTerminal["Database Terminal<br/>TerminalDialog"]
        ExecMySQL["Execute MySQL CLI<br/>/api/v2/containers/exec"]
    end
    
    PHPMyAdmin --> CheckInstalled
    Adminer --> CheckInstalled
    CheckInstalled --> GetPort
    GetPort --> OpenPortJump
    OpenPortJump --> AccessTool
    
    TerminalBtn --> OpenTerminal
    OpenTerminal --> ExecMySQL
```

**Diagram: MySQL Management Tool Access**

The system checks if phpMyAdmin or Adminer are installed via `getAppPort()`. If not installed (port = 0), it prompts for installation. The terminal provides direct MySQL CLI access through container exec.

Sources: [frontend/src/views/database/mysql/index.vue:472-510](), [frontend/src/views/database/mysql/index.vue:384-386]()

---

## PostgreSQL Management

PostgreSQL management follows a similar pattern to MySQL with additional superuser privilege support.

### Database and User Operations

```mermaid
graph TB
    subgraph "PostgreSQL Operations"
        CreatePgDB["Create Database<br/>addPostgresqlDB()"]
        BindPgUser["Bind User<br/>bindPostgresqlUser()"]
        ChangePriv["Change Privileges<br/>changePrivileges()"]
        SearchPg["Search Databases<br/>searchPostgresqlDBs()"]
        DeletePg["Delete Database<br/>deletePostgresqlDB()"]
    end
    
    subgraph "PostgreSQL-Specific Features"
        SuperUser["superUser: boolean<br/>Grant superuser privileges"]
        PgFormat["format: SQL_ASCII/UTF8/etc"]
    end
    
    subgraph "Common Features"
        Username["username: string"]
        Password["password: Base64"]
        Description["description: string"]
    end
    
    CreatePgDB --> SuperUser
    CreatePgDB --> PgFormat
    CreatePgDB --> Username
    CreatePgDB --> Password
    
    BindPgUser --> SuperUser
    ChangePriv --> SuperUser
```

**Diagram: PostgreSQL-Specific Features**

PostgreSQL adds `superUser` boolean field to control elevated privileges. The `changePrivileges()` function allows toggling superuser status without changing passwords.

Sources: [frontend/src/api/modules/database.ts:20-55](), [frontend/src/api/interface/database.ts:154-217]()

### User Privilege Management

PostgreSQL distinguishes between regular users and superusers:

| Property | Regular User | Superuser |
|----------|--------------|-----------|
| **Database Access** | Specific database only | All databases |
| **Object Creation** | Own database | All databases |
| **Role Management** | Cannot create roles | Can create/modify roles |
| **Configuration** | Limited | Full system access |

The `PgChangePrivileges` interface allows updating privilege levels:

```typescript
interface PgChangePrivileges {
    name: string;        // PostgreSQL instance name
    database: string;    // Target database name
    username: string;    // User to modify
    superUser: boolean;  // Grant/revoke superuser
}
```

Sources: [frontend/src/api/interface/database.ts:161-166]()

---

## Redis Management

Redis management centers around terminal/CLI interaction with configuration and monitoring support.

### Terminal Integration

Redis provides an interactive terminal with quick command support:

```mermaid
graph TB
    subgraph "Redis Terminal Flow"
        SelectDB["Select Redis Instance<br/>currentDBName"]
        CheckStatus["Check Status<br/>checkAppInstalled()"]
        CheckCLI["Check CLI Available<br/>checkRedisCli()"]
        InitTerminal["Initialize Terminal<br/>Terminal component"]
        ExecCommand["Execute Commands<br/>/api/v2/containers/exec"]
    end
    
    subgraph "Quick Commands"
        LoadQuickCmd["Load Commands<br/>getCommandList('redis')"]
        QuickSelect["Select Command<br/>el-select quickCmd"]
        SendCmd["Send to Terminal<br/>terminalRef.sendMsg()"]
    end
    
    subgraph "Remote Redis"
        CheckRemoteCLI["Check redis-cli<br/>redisCliExist"]
        InstallCLI["Install CLI<br/>installRedisCli()"]
        ConnectRemote["Connect Remote<br/>from=remote parameter"]
    end
    
    SelectDB --> CheckStatus
    CheckStatus --> CheckCLI
    CheckCLI --> InitTerminal
    InitTerminal --> ExecCommand
    
    LoadQuickCmd --> QuickSelect
    QuickSelect --> SendCmd
    SendCmd --> ExecCommand
    
    CheckRemoteCLI -.false.-> InstallCLI
    InstallCLI --> ConnectRemote
    ConnectRemote --> ExecCommand
```

**Diagram: Redis Terminal Integration**

Local Redis instances connect directly through Docker exec. Remote Redis requires the `redis-cli` tool, installed on demand via `installRedisCli()`. Quick commands provide pre-configured Redis commands (GET, SET, KEYS, etc.).

Sources: [frontend/src/views/database/redis/index.vue:295-345](), [frontend/src/views/database/redis/index.vue:352-374](), [frontend/src/views/database/redis/index.vue:376-390]()

### Configuration Management

Redis configuration is managed through multiple interfaces:

```mermaid
graph TB
    subgraph "Configuration Files"
        LoadRedisConf["Load redis.conf<br/>loadDBFile('redis-conf')"]
        EditConf["Edit Configuration<br/>CodemirrorPro"]
        SaveConf["Save Configuration<br/>updateDBFile()"]
    end
    
    subgraph "Performance Settings"
        LoadSettings["Load Settings<br/>loadRedisConf()"]
        EditTimeout["timeout: number<br/>Client timeout in seconds"]
        EditMaxClients["maxclients: number<br/>Max simultaneous clients"]
        EditMaxMemory["maxmemory: number<br/>Max memory in MB"]
        SaveSettings["Update Settings<br/>updateRedisConf()"]
    end
    
    subgraph "Persistence Settings"
        LoadPersist["Load Persistence<br/>redisPersistenceConf()"]
        EditAOF["appendonly: on/off<br/>Append-only file mode"]
        EditAppendFsync["appendfsync: always/everysec/no<br/>Fsync policy"]
        EditRDB["save: string<br/>RDB snapshot rules"]
        SavePersist["Update Persistence<br/>updateRedisPersistenceConf()"]
    end
    
    LoadRedisConf --> EditConf
    EditConf --> SaveConf
    
    LoadSettings --> EditTimeout
    LoadSettings --> EditMaxClients
    LoadSettings --> EditMaxMemory
    EditTimeout --> SaveSettings
    EditMaxClients --> SaveSettings
    EditMaxMemory --> SaveSettings
    
    LoadPersist --> EditAOF
    LoadPersist --> EditAppendFsync
    LoadPersist --> EditRDB
    EditAOF --> SavePersist
    EditAppendFsync --> SavePersist
    EditRDB --> SavePersist
```

**Diagram: Redis Configuration Management**

Redis supports three configuration levels: raw file editing, performance tuning (timeout, connections, memory), and persistence settings (AOF/RDB). All changes require container restart.

Sources: [frontend/src/views/database/redis/setting/index.vue:1-353](), [frontend/src/api/modules/database.ts:115-148]()

### Redis Status Monitoring

Redis status provides operational metrics:

```typescript
interface RedisStatus {
    tcp_port: string;                      // Listening port
    uptime_in_days: string;                // Days since start
    connected_clients: string;             // Current connections
    used_memory: string;                   // Memory in use
    used_memory_rss: string;               // RSS memory
    used_memory_peak: string;              // Peak memory
    mem_fragmentation_ratio: string;       // Fragmentation ratio
    total_connections_received: string;    // Total connections
    total_commands_processed: string;      // Total commands
    instantaneous_ops_per_sec: string;     // Current ops/sec
    keyspace_hits: string;                 // Cache hits
    keyspace_misses: string;               // Cache misses
    latest_fork_usec: string;              // Last fork duration
}
```

Sources: [frontend/src/api/interface/database.ts:242-256]()

### Persistence Configuration

Redis persistence settings control data durability:

| Mode | Configuration | Behavior |
|------|---------------|----------|
| **AOF (Append-Only File)** | `appendonly: on` | Logs all write operations |
| **AOF Fsync** | `appendfsync: always` | Sync after every write (slow, safe) |
|  | `appendfsync: everysec` | Sync every second (balanced) |
|  | `appendfsync: no` | Let OS decide (fast, less safe) |
| **RDB Snapshots** | `save: "900 1 300 10 60 10000"` | Save after time+changes threshold |

The persistence interface allows enabling/disabling AOF, configuring fsync policy, and setting RDB snapshot rules.

Sources: [frontend/src/api/interface/database.ts:265-269](), [frontend/src/api/modules/database.ts:140-142]()

---

## Remote Database Management

Remote databases provide connection management for external database instances.

### Database Connection Structure

```mermaid
graph TB
    subgraph "Remote Database Entity"
        DBInfo["DatabaseInfo"]
        BasicInfo["name: string<br/>type: mysql/postgresql/redis<br/>version: string<br/>address: string<br/>port: number"]
        AuthInfo["username: string<br/>password: string<br/>initialDB: string<br/>timeout: number"]
        SSLInfo["ssl: boolean<br/>rootCert: string<br/>clientKey: string<br/>clientCert: string<br/>skipVerify: boolean"]
    end
    
    subgraph "Connection Operations"
        CheckConn["Check Connection<br/>checkDatabase()"]
        AddRemote["Add Remote DB<br/>addDatabase()"]
        UpdateRemote["Update Remote DB<br/>editDatabase()"]
        DeleteRemote["Delete Remote DB<br/>deleteDatabase()"]
    end
    
    subgraph "SSL Certificate Handling"
        LoadCerts["Load Certificates<br/>File upload"]
        EncodeCerts["Base64 Encode<br/>clientKey/clientCert/rootCert"]
        SendCerts["Send to Backend<br/>Base64-encoded"]
    end
    
    DBInfo --> BasicInfo
    DBInfo --> AuthInfo
    DBInfo --> SSLInfo
    
    BasicInfo --> CheckConn
    AuthInfo --> CheckConn
    SSLInfo --> CheckConn
    CheckConn --> AddRemote
    
    LoadCerts --> EncodeCerts
    EncodeCerts --> SendCerts
    SendCerts --> AddRemote
```

**Diagram: Remote Database Connection Structure**

Remote databases support SSL/TLS connections with client certificates. The `checkDatabase()` function validates connectivity before saving. Certificates are Base64-encoded before transmission.

Sources: [frontend/src/api/modules/database.ts:164-193](), [frontend/src/api/interface/database.ts:272-356]()

### Remote Database Operations

Once registered, remote databases appear in database type selectors alongside local instances:

```mermaid
graph LR
    subgraph "Database List"
        ListAPI["listDatabases(type)<br/>Returns local+remote"]
        LocalGroup["Local Databases<br/>from: local"]
        RemoteGroup["Remote Databases<br/>from: remote"]
    end
    
    subgraph "Operations on Remote"
        CreateDB["Create Database<br/>Same as local"]
        CreateUser["Create User<br/>Same as local"]
        LoadFromRemote["Load Existing<br/>loadDBFromRemote()"]
    end
    
    subgraph "Restrictions"
        NoConfig["No Config Edit<br/>External management"]
        NoRestart["No Restart<br/>External control"]
        NoLogs["No Logs<br/>External access"]
    end
    
    ListAPI --> LocalGroup
    ListAPI --> RemoteGroup
    
    RemoteGroup --> CreateDB
    RemoteGroup --> CreateUser
    RemoteGroup --> LoadFromRemote
    
    RemoteGroup -.limited.-> NoConfig
    RemoteGroup -.limited.-> NoRestart
    RemoteGroup -.limited.-> NoLogs
```

**Diagram: Remote Database Integration**

Remote databases integrate into the same UI as local databases but with limited operations. The `loadDBFromRemote()` function imports existing databases from the remote instance into 1Panel's tracking.

Sources: [frontend/src/views/database/mysql/index.vue:436-457](), [frontend/src/api/modules/database.ts:76-78]()

---

## Common Database Operations

### Database Selector Pattern

All database views use a consistent selector pattern:

```mermaid
graph TB
    subgraph "Database Selection Flow"
        LoadOptions["Load Database Options<br/>listDatabases(type)"]
        SplitSources["Split by Source<br/>dbOptionsLocal/dbOptionsRemote"]
        CheckGlobal["Check Global Store<br/>currentDB/currentRedisDB"]
        SelectDefault["Select Default<br/>First local or first remote"]
        ChangeDB["User Changes DB<br/>changeDatabase()"]
    end
    
    subgraph "UI Rendering"
        RenderSelect["el-select with groups"]
        LocalOptGroup["el-option-group: Local<br/>+ Install link"]
        RemoteOptGroup["el-option-group: Remote<br/>+ Add remote link"]
    end
    
    subgraph "State Management"
        UpdateGlobal["Update Global Store<br/>setCurrentDB()"]
        UpdateApp["Update App Status<br/>appStatusRef.onCheck()"]
        RefreshData["Refresh Table Data<br/>search()"]
    end
    
    LoadOptions --> SplitSources
    SplitSources --> CheckGlobal
    CheckGlobal -.found.-> ChangeDB
    CheckGlobal -.not found.-> SelectDefault
    SelectDefault --> ChangeDB
    
    ChangeDB --> UpdateGlobal
    UpdateGlobal --> UpdateApp
    UpdateApp --> RefreshData
    
    RenderSelect --> LocalOptGroup
    RenderSelect --> RemoteOptGroup
```

**Diagram: Database Selector Pattern**

The selector persists selection in global store (`currentDB` for MySQL/PostgreSQL, `currentRedisDB` for Redis). When switching databases, it updates app status for local databases and refreshes the data table.

Sources: [frontend/src/views/database/mysql/index.vue:397-418](), [frontend/src/views/database/redis/index.vue:225-245]()

### Backup Integration

Database operations integrate with the backup system:

```mermaid
graph LR
    subgraph "Backup Actions"
        BackupList["View Backup List<br/>Backups component"]
        LoadBackup["Upload Backup<br/>UploadDialog"]
    end
    
    subgraph "Backup Parameters"
        BackupType["type: mysql/redis/postgresql"]
        BackupName["name: instance name"]
        DetailName["detailName: database name"]
    end
    
    subgraph "Per-Row Actions"
        BackupBtn["Backup List Button"]
        UploadBtn["Load Backup Button"]
    end
    
    BackupBtn --> BackupList
    UploadBtn --> LoadBackup
    
    BackupList --> BackupType
    BackupList --> BackupName
    BackupList --> DetailName
    
    LoadBackup --> BackupType
    LoadBackup --> BackupName
    LoadBackup --> DetailName
```

**Diagram: Backup Integration Pattern**

Each database row provides backup operations. The `Backups` component (see [Backup and Snapshot System](#10.3)) handles listing and restore. The `UploadDialog` allows uploading backup files directly.

Sources: [frontend/src/views/database/mysql/index.vue:638-666]()

---

## API Structure and Data Flow

### API Client Organization

The database API client is organized by database type:

```typescript
// Common operations (all types)
loadDBBaseInfo(type: string, database: string)
loadDBFile(type: string, database: string)
updateDBFile(params: DBConfUpdate)

// MySQL-specific
searchMysqlDBs(params: SearchDBWithPage)
addMysqlDB(params: MysqlDBCreate)
bindUser(params: BindUser)
updateMysqlPassword(params: ChangeInfo)
updateMysqlAccess(params: ChangeInfo)
deleteMysqlDB(params: MysqlDBDelete)
loadMysqlVariables(type: string, database: string)
loadMysqlStatus(type: string, database: string)

// PostgreSQL-specific
searchPostgresqlDBs(params: SearchDBWithPage)
addPostgresqlDB(params: PostgresqlDBCreate)
bindPostgresqlUser(params: PgBind)
changePrivileges(params: PgChangePrivileges)
updatePostgresqlPassword(params: ChangeInfo)
deletePostgresqlDB(params: PostgresqlDBDelete)

// Redis-specific
loadRedisStatus(type: string, database: string)
loadRedisConf(type: string, database: string)
redisPersistenceConf(type: string, database: string)
updateRedisConf(params: RedisConfUpdate)
changeRedisPassword(database: string, password: string)

// Remote database management
listDatabases(type: string)
searchDatabases(params: SearchDatabasePage)
checkDatabase(params: DatabaseCreate)
addDatabase(params: DatabaseCreate)
editDatabase(params: DatabaseUpdate)
deleteDatabase(params: DatabaseDelete)
```

Sources: [frontend/src/api/modules/database.ts:1-200]()

### Password Encoding Pattern

All password fields are Base64-encoded before transmission:

```typescript
// Example from addMysqlDB
export const addMysqlDB = (params: Database.MysqlDBCreate) => {
    let request = deepCopy(params) as Database.MysqlDBCreate;
    if (request.password) {
        request.password = Base64.encode(request.password);
    }
    return http.post(`/databases`, request);
};

// Example from updateMysqlPassword
export const updateMysqlPassword = (params: Database.ChangeInfo) => {
    let request = deepCopy(params) as Database.ChangeInfo;
    if (request.value) {
        request.value = Base64.encode(request.value);
    }
    return http.post(`/databases/change/password`, request);
};
```

This encoding pattern applies to all password operations (create, update, bind) across MySQL, PostgreSQL, and Redis. SSL certificates are also Base64-encoded for remote database connections.

Sources: [frontend/src/api/modules/database.ts:20-26](), [frontend/src/api/modules/database.ts:62-68](), [frontend/src/api/modules/database.ts:82-88]()

### Multi-Node Support

Database operations support multi-node deployments through query parameters:

```typescript
// MySQL search with node parameter
export const searchMysqlDBs = (params: Database.SearchDBWithPage, node?: string) => {
    const query = node ? `?operateNode=${node}` : '';
    return http.post<ResPage<Database.MysqlDBInfo>>(`/databases/search${query}`, params);
};

// PostgreSQL search with node parameter
export const searchPostgresqlDBs = (params: Database.SearchDBWithPage, node?: string) => {
    const query = node ? `?operateNode=${node}` : '';
    return http.post<ResPage<Database.PostgresqlDBInfo>>(`/databases/pg/search${query}`, params);
};

// List databases with node parameter
export const listDatabases = (type: string, node?: string) => {
    const query = node ? `?operateNode=${node}` : '';
    return http.get<Array<Database.DatabaseOption>>(`/databases/db/list/${type}${query}`);
};
```

When operating in a multi-node environment (see [Multi-Node Architecture](#2.2)), the optional `node` parameter routes operations to specific agent nodes.

Sources: [frontend/src/api/modules/database.ts:33-36](), [frontend/src/api/modules/database.ts:58-61](), [frontend/src/api/modules/database.ts:157-160]()

---

## Table Structures and Data Models

### MySQL Database Record

```typescript
interface MysqlDBInfo {
    id: number;              // Database ID
    createdAt: Date;         // Creation timestamp
    name: string;            // Database name
    mysqlName: string;       // Parent MySQL instance
    from: string;            // 'local' or 'remote'
    format: string;          // Character set (utf8mb4, etc.)
    username: string;        // Bound MySQL user
    password: string;        // User password
    permission: string;      // Host permission (%, localhost, IP)
    isDelete: string;        // Deletion marker
    description: string;     // User description
}
```

The `isDelete` field marks databases that exist in 1Panel but not in the actual MySQL instance, displayed with an info tag in the UI.

Sources: [frontend/src/api/interface/database.ts:16-28]()

### PostgreSQL Database Record

```typescript
interface PostgresqlDBInfo {
    id: number;                  // Database ID
    createdAt: Date;             // Creation timestamp
    name: string;                // Database name
    postgresqlName: string;      // Parent PostgreSQL instance
    from: string;                // 'local' or 'remote'
    format: string;              // Encoding (UTF8, SQL_ASCII, etc.)
    username: string;            // Bound PostgreSQL user
    password: string;            // User password
    superUser: boolean;          // Superuser privilege flag
    isDelete: string;            // Deletion marker
    description: string;         // User description
}
```

PostgreSQL adds the `superUser` boolean for elevated privileges.

Sources: [frontend/src/api/interface/database.ts:205-217]()

### Remote Database Record

```typescript
interface DatabaseInfo {
    id: number;              // Database ID
    createdAt: Date;         // Registration timestamp
    name: string;            // Display name
    type: string;            // mysql/postgresql/redis
    version: string;         // Database version
    from: string;            // Always 'remote'
    address: string;         // IP address or hostname
    port: number;            // Connection port
    initialDB: string;       // Default database to connect
    username: string;        // Admin username
    password: string;        // Admin password
    
    // SSL/TLS configuration
    ssl: boolean;            // SSL enabled
    hasCA: boolean;          // CA certificate present
    rootCert: string;        // CA certificate (Base64)
    clientKey: string;       // Client private key (Base64)
    clientCert: string;      // Client certificate (Base64)
    skipVerify: boolean;     // Skip certificate verification
    
    timeout: number;         // Connection timeout (seconds)
    description: string;     // User description
}
```

Remote databases support full SSL/TLS with client certificate authentication.

Sources: [frontend/src/api/interface/database.ts:272-294]()

---

## Key Components and Files

### Frontend Components

| Component | Path | Purpose |
|-----------|------|---------|
| **MySQL Index** | [frontend/src/views/database/mysql/index.vue:1-680]() | Main MySQL/MariaDB management view |
| **MySQL Settings** | [frontend/src/views/database/mysql/setting/index.vue:1-343]() | MySQL configuration and monitoring |
| **Redis Index** | [frontend/src/views/database/redis/index.vue:1-423]() | Main Redis management view with terminal |
| **Redis Settings** | [frontend/src/views/database/redis/setting/index.vue:1-353]() | Redis configuration tabs |
| **Database API** | [frontend/src/api/modules/database.ts:1-200]() | API client methods |
| **Database Types** | [frontend/src/api/interface/database.ts:1-363]() | TypeScript interface definitions |

### Common Patterns

**AppStatus Component**: Used in MySQL and Redis local views to display app installation status, version, and provide start/stop/restart controls.

**TerminalDialog Component**: Provides interactive terminal access for Redis CLI and MySQL CLI execution through container exec endpoints.

**ConfirmDialog Component**: Used for configuration changes requiring restart, ensuring users acknowledge the service interruption.

**ComplexTable Component**: Displays database lists with pagination, sorting, search, and per-row action buttons.

Sources: [frontend/src/views/database/mysql/index.vue:15-26](), [frontend/src/views/database/redis/index.vue:14-24]()

---

# Page: File Management System

# File Management System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [frontend/src/api/interface/file.ts](frontend/src/api/interface/file.ts)
- [frontend/src/api/modules/files.ts](frontend/src/api/modules/files.ts)
- [frontend/src/views/host/file-management/code-editor/index.vue](frontend/src/views/host/file-management/code-editor/index.vue)
- [frontend/src/views/host/file-management/index.vue](frontend/src/views/host/file-management/index.vue)

</details>



## Purpose and Scope

The File Management System provides a comprehensive web-based interface for browsing, editing, and managing files on the Linux server filesystem. This document covers the multi-tab file browser, Monaco-based code editor, file operations (CRUD, compression, conversion), upload mechanisms, favorites, recycle bin, and terminal integration. For terminal-specific operations, see [Terminal and SSH Management](#8.3). For backup and snapshot functionality, see [Backup and Snapshot System](#10.3).

## System Architecture

The File Management System consists of three primary layers: a Vue-based frontend interface with multi-tab support, an API client layer for communication with the backend, and a comprehensive set of file operation endpoints. The system integrates the Monaco editor for code editing and supports up to 10 simultaneous file tabs.

```mermaid
graph TB
    subgraph "Frontend Components"
        FileIndex["File Management Index<br/>index.vue"]
        CodeEditor["Code Editor<br/>code-editor/index.vue"]
        Dialogs["Operation Dialogs<br/>create/compress/upload/etc"]
        
        FileIndex --> |"opens"| CodeEditor
        FileIndex --> |"shows"| Dialogs
    end
    
    subgraph "State Management"
        TabState["Tab State<br/>editableTabs[]"]
        PathHistory["Path History<br/>history[]"]
        FileState["File Selection<br/>selects[]"]
        
        FileIndex --> TabState
        FileIndex --> PathHistory
        FileIndex --> FileState
    end
    
    subgraph "API Layer"
        FilesAPI["files.ts<br/>API Client"]
        FileInterfaces["file.ts<br/>TypeScript Interfaces"]
        
        FilesAPI --> FileInterfaces
    end
    
    subgraph "Backend Endpoints"
        SearchAPI["/files/search<br/>getFilesList"]
        TreeAPI["/files/tree<br/>getFilesTree"]
        ContentAPI["/files/content<br/>getFileContent"]
        SaveAPI["/files/save<br/>saveFileContent"]
        UploadAPI["/files/upload<br/>uploadFileData"]
        CompressAPI["/files/compress<br/>compressFile"]
        ConvertAPI["/files/convert<br/>convertFiles"]
    end
    
    FileIndex --> FilesAPI
    CodeEditor --> FilesAPI
    
    FilesAPI --> SearchAPI
    FilesAPI --> TreeAPI
    FilesAPI --> ContentAPI
    FilesAPI --> SaveAPI
    FilesAPI --> UploadAPI
    FilesAPI --> CompressAPI
    FilesAPI --> ConvertAPI
    
    style FileIndex fill:#f9f9f9
    style CodeEditor fill:#f9f9f9
    style FilesAPI fill:#e8f4f8
```

**Sources:** [frontend/src/views/host/file-management/index.vue:1-637](), [frontend/src/views/host/file-management/code-editor/index.vue:1-387](), [frontend/src/api/modules/files.ts:1-181]()

## Multi-Tab File Browser Interface

The file browser implements a tabbed interface allowing users to navigate multiple directories simultaneously. Each tab maintains its own navigation state, path history, and file listings.

### Tab Management System

The system supports multiple file browser tabs with individual navigation contexts. Users can add up to 7 tabs (including the initial tab), with each tab storing its path and display name.

```mermaid
graph LR
    subgraph "Tab Data Structure"
        Tab1["Tab Object<br/>{id, name, path}"]
        Tab2["Tab Object<br/>{id, name, path}"]
        TabN["Tab Object<br/>{id, name, path}"]
    end
    
    editableTabs["editableTabs[]<br/>reactive array"]
    editableTabsKey["editableTabsKey<br/>current tab ID"]
    
    editableTabs --> Tab1
    editableTabs --> Tab2
    editableTabs --> TabN
    
    editableTabsKey --> |"points to active"| Tab1
    
    TabMethods["Tab Methods"]
    addTab["addTab()"]
    removeTab["removeTab(id)"]
    changeTab["changeTab(id)"]
    
    TabMethods --> addTab
    TabMethods --> removeTab
    TabMethods --> changeTab
    
    addTab --> editableTabs
    removeTab --> editableTabs
    changeTab --> editableTabsKey
```

The tab state is managed at [frontend/src/views/host/file-management/index.vue:721-725]() with initialization:

```typescript
const editableTabsKey = ref('');
const editableTabs = ref([
    { id: '1', name: getLastPath(baseDir.value), path: baseDir.value },
    { id: '2', name: 'home', path: '/home' },
]);
```

Tab operations are implemented at [frontend/src/views/host/file-management/index.vue:1653-1719]() including `addTab()`, `removeTab()`, and `changeTab()` methods.

**Sources:** [frontend/src/views/host/file-management/index.vue:721-725](), [frontend/src/views/host/file-management/index.vue:1653-1719]()

### Path Navigation and Breadcrumbs

The navigation system provides forward/back/top navigation buttons and an interactive breadcrumb trail. The breadcrumb can be clicked to navigate to any parent directory or switched to an editable input for direct path entry.

```mermaid
graph TB
    subgraph "Navigation State"
        history["history: string[]<br/>visited paths"]
        pointer["pointer: number<br/>current position"]
        paths["paths: FilePaths[]<br/>breadcrumb segments"]
        hidePaths["hidePaths: FilePaths[]<br/>collapsed segments"]
    end
    
    subgraph "Navigation Controls"
        back["back()<br/>pointer--"]
        right["right()<br/>pointer++"]
        top["top()<br/>goto baseDir"]
        jump["jump(path)<br/>navigate to path"]
    end
    
    subgraph "Path Display"
        breadcrumb["Breadcrumb UI<br/>paths.map()"]
        dropdown["Dropdown<br/>hidePaths"]
        searchable["Editable Input<br/>searchablePath"]
    end
    
    back --> pointer
    right --> pointer
    top --> paths
    jump --> history
    
    pointer --> history
    history --> |"updates"| paths
    
    paths --> breadcrumb
    hidePaths --> dropdown
    searchable --> jump
```

The path navigation system uses a history array with pointer-based navigation at [frontend/src/views/host/file-management/index.vue:752-753]():

```typescript
const history: string[] = [];
let pointer = -1;
```

Navigation methods are implemented at [frontend/src/views/host/file-management/index.vue:1115-1162]() with path splitting and breadcrumb rendering logic at [frontend/src/views/host/file-management/index.vue:1163-1218]().

**Sources:** [frontend/src/views/host/file-management/index.vue:752-753](), [frontend/src/views/host/file-management/index.vue:1115-1218]()

### File Listing and Search

The file listing supports pagination, sorting, filtering by hidden files, and recursive search. The table displays file metadata including name, permissions (mode), owner/group, size, and modification time.

| Column | Description | Actions |
|--------|-------------|---------|
| Name | File/directory name with icon | Click to open, hover for favorites |
| Mode | Unix permissions (e.g., 0755) | Click to edit permissions |
| User/Group | Owner and group IDs | Click to change ownership |
| Size | File size or "Calculate" for directories | Click to compute directory size |
| Modified | Last modification timestamp | Sortable |
| Remark | Optional user annotation | Editable |

The search request structure is defined at [frontend/src/views/host/file-management/index.vue:736-746]():

```typescript
const initData = () => ({
    path: '/',
    expand: true,
    showHidden: localStorage.getItem('show-hidden') === 'true',
    page: 1,
    pageSize: 100,
    search: '',
    containSub: false,
    sortBy: 'name',
    sortOrder: 'ascending',
});
```

The search operation calls `getFilesList()` at [frontend/src/views/host/file-management/index.vue:851-869]() with result handling that populates the data table and calculates directory/file counts.

**Sources:** [frontend/src/views/host/file-management/index.vue:736-746](), [frontend/src/views/host/file-management/index.vue:851-895](), [frontend/src/api/modules/files.ts:9-11]()

## File Operations

### Basic CRUD Operations

The system provides comprehensive create, read, update, and delete operations for both files and directories.

```mermaid
graph TB
    subgraph "Create Operations"
        CreateDialog["CreateFile Dialog<br/>create/index.vue"]
        createFile["createFile(form)<br/>API call"]
        
        CreateDialog --> |"POST /files"| createFile
    end
    
    subgraph "Read Operations"
        getFilesList["getFilesList(req)<br/>POST /files/search"]
        getFileContent["getFileContent(req)<br/>POST /files/content"]
        computeDirSize["computeDirSize(req)<br/>POST /files/size"]
    end
    
    subgraph "Update Operations"
        renameRile["renameRile(params)<br/>POST /files/rename"]
        changeFileMode["changeFileMode(form)<br/>POST /files/mode"]
        changeOwner["changeOwner(params)<br/>POST /files/owner"]
        saveFileContent["saveFileContent(params)<br/>POST /files/save"]
        moveFile["moveFile(params)<br/>POST /files/move"]
    end
    
    subgraph "Delete Operations"
        deleteFile["deleteFile(form)<br/>POST /files/del"]
        batchDeleteFile["batchDeleteFile(form)<br/>POST /files/batch/del"]
        RecycleBin["Recycle Bin<br/>soft delete option"]
        
        deleteFile --> |"forceDelete: false"| RecycleBin
    end
```

File creation is handled by the `handleCreate()` method at [frontend/src/views/host/file-management/index.vue:1000-1004]() which opens a dialog for directory or file creation. The creation form includes path, type (isDir), permissions (mode), and optional symbolic link configuration defined in the `fileCreate` reactive object at [frontend/src/views/host/file-management/index.vue:755]().

**Sources:** [frontend/src/views/host/file-management/index.vue:755](), [frontend/src/views/host/file-management/index.vue:1000-1004](), [frontend/src/api/modules/files.ts:25-95]()

### Compression and Decompression

The system supports multiple compression formats with configurable options including password protection.

```mermaid
graph LR
    subgraph "Compression Formats"
        Tar["tar"]
        TarGz["tar.gz"]
        Zip["zip"]
        Xz["xz / tar.xz"]
        SevenZ["7z"]
    end
    
    subgraph "Compression Flow"
        SelectFiles["Select Files<br/>fileCompress.files[]"]
        CompressDialog["Compress Dialog<br/>compress/index.vue"]
        CompressAPI["compressFile()<br/>POST /files/compress"]
        Result["Compressed Archive<br/>.tar.gz / .zip"]
        
        SelectFiles --> CompressDialog
        CompressDialog --> |"files, type, dst, name,<br/>replace, secret"| CompressAPI
        CompressAPI --> Result
    end
    
    subgraph "Decompression Flow"
        SelectArchive["Select Archive"]
        DecompressDialog["Decompress Dialog<br/>decompress/index.vue"]
        DecompressAPI["deCompressFile()<br/>POST /files/decompress"]
        ExtractedFiles["Extracted Files"]
        
        SelectArchive --> DecompressDialog
        DecompressDialog --> |"path, dst, type, secret"| DecompressAPI
        DecompressAPI --> ExtractedFiles
    end
```

Compression is initiated at [frontend/src/views/host/file-management/index.vue:1343-1351]() with the `openCompress()` method populating the `fileCompress` reactive object:

```typescript
const fileCompress = reactive({ files: [''], name: '', dst: '', operate: 'compress' });
```

The API calls support 10-minute timeouts defined in [frontend/src/api/modules/files.ts:46-50]() to accommodate large file operations.

**Sources:** [frontend/src/views/host/file-management/index.vue:756](), [frontend/src/views/host/file-management/index.vue:1343-1351](), [frontend/src/api/modules/files.ts:46-50]()

### File Upload System

The upload system supports both standard HTTP uploads and chunked uploads for large files, with drag-and-drop functionality.

```mermaid
graph TB
    subgraph "Upload Triggers"
        UploadButton["Upload Button<br/>openUpload()"]
        DragDrop["Drag & Drop<br/>handleDrop()"]
        
        UploadButton --> UploadDialog
        DragDrop --> UploadDialog
    end
    
    subgraph "Upload Processing"
        UploadDialog["Upload Dialog<br/>upload/index.vue"]
        FileCheck["batchCheckFiles()<br/>check existing files"]
        FormData["FormData<br/>+ AxiosRequestConfig"]
        
        UploadDialog --> FileCheck
        FileCheck --> FormData
    end
    
    subgraph "Upload Methods"
        StandardUpload["uploadFileData()<br/>POST /files/upload"]
        ChunkedUpload["chunkUploadFileData()<br/>POST /files/chunkupload"]
        
        FormData --> StandardUpload
        FormData --> ChunkedUpload
    end
    
    subgraph "Upload Monitoring"
        ProgressCallback["onUploadProgress<br/>config callback"]
        UploadList["Upload List<br/>getUploadList()"]
        
        StandardUpload --> ProgressCallback
        ChunkedUpload --> ProgressCallback
        UploadDialog --> UploadList
    end
```

Drag-and-drop is handled at [frontend/src/views/host/file-management/index.vue:1623-1651]() with the `handleDrop()` method detecting dropped files and opening the upload dialog. The upload dialog component is referenced at [frontend/src/views/host/file-management/index.vue:620]().

The API provides both standard and chunked upload endpoints at [frontend/src/api/modules/files.ts:69-87]() with custom Axios configuration for progress tracking.

**Sources:** [frontend/src/views/host/file-management/index.vue:1623-1651](), [frontend/src/api/modules/files.ts:69-87](), [frontend/src/api/interface/file.ts:50-57]()

### Remote File Download (Wget)

The system provides wget functionality for downloading files from remote URLs, with background task tracking.

```mermaid
graph LR
    subgraph "Wget Flow"
        WgetDialog["Wget Dialog<br/>wget/index.vue"]
        WgetAPI["wgetFile(params)<br/>POST /files/wget"]
        TaskKey["Task Key<br/>FileWgetRes.key"]
        
        WgetDialog --> |"path, name, url,<br/>ignoreCertificate"| WgetAPI
        WgetAPI --> TaskKey
    end
    
    subgraph "Process Monitoring"
        ProcessCount["processCount<br/>active downloads"]
        ProcessDialog["Process Dialog<br/>process/index.vue"]
        fileWgetKeys["fileWgetKeys()<br/>GET /files/wget/process/keys"]
        
        TaskKey --> ProcessCount
        ProcessCount --> ProcessDialog
        ProcessDialog --> fileWgetKeys
    end
    
    subgraph "Completion"
        CloseWget["closeWget()<br/>refresh file list"]
        getWgetProcess["getWgetProcess()<br/>update count"]
        
        ProcessDialog --> CloseWget
        CloseWget --> getWgetProcess
    end
```

The wget dialog is opened via `openWget()` at [frontend/src/views/host/file-management/index.vue:1006-1012]() which sets the current path. Active wget processes are tracked at [frontend/src/views/host/file-management/index.vue:1738-1747]() with the `getWgetProcess()` method fetching active task keys and updating the badge count.

**Sources:** [frontend/src/views/host/file-management/index.vue:1006-1012](), [frontend/src/views/host/file-management/index.vue:1738-1747](), [frontend/src/api/modules/files.ts:97-119]()

### File Conversion

The system supports format conversion for various file types including images, documents, and media files when FFmpeg is available.

```mermaid
graph TB
    subgraph "Conversion Types"
        ImageConv["Image Formats<br/>png/jpg/webp/bmp/tiff"]
        VideoConv["Video Formats<br/>mp4/avi/mkv/flv/mov"]
        AudioConv["Audio Formats<br/>mp3/wav/flac/aac/ogg"]
        DocConv["Document Formats<br/>pdf/txt/md"]
    end
    
    subgraph "Conversion Flow"
        SelectFile["Select File"]
        ConvertDialog["Convert Dialog<br/>convert/index.vue"]
        ConvertAPI["convertFiles(params)<br/>POST /files/convert"]
        ConvertedFile["Converted File"]
        
        SelectFile --> ConvertDialog
        ConvertDialog --> |"files[], outputPath,<br/>deleteSource, taskID"| ConvertAPI
        ConvertAPI --> ConvertedFile
    end
    
    subgraph "Conversion Tracking"
        ConvertLogs["convertLogs(params)<br/>POST /files/convert/log"]
        LogResponse["ConvertLogResponse[]<br/>status, message"]
        
        ConvertAPI --> ConvertLogs
        ConvertLogs --> LogResponse
    end
```

File conversion state is maintained in the `fileConvert` reactive object at [frontend/src/views/host/file-management/index.vue:765-779]():

```typescript
const fileConvert = reactive<{
    outputPath: string;
    files: File.ConvertFile[];
}>({
    outputPath: '',
    files: [
        {
            type: '',
            inputFile: '',
            extension: '',
            path: '',
            outputFormat: '',
        },
    ],
});
```

The conversion is triggered via the table operations menu, opening the convert dialog referenced at [frontend/src/views/host/file-management/index.vue:635]().

**Sources:** [frontend/src/views/host/file-management/index.vue:765-779](), [frontend/src/api/modules/files.ts:174-180](), [frontend/src/api/interface/file.ts:241-263]()

## Monaco Code Editor Integration

The code editor component provides a full-featured Monaco editor instance with file tree navigation, multiple file tabs, and extensive customization options.

### Editor Initialization and Configuration

The Monaco editor is initialized with configurable themes, languages, and display options persisted to localStorage.

```mermaid
graph TB
    subgraph "Editor Configuration"
        EditorConfig["EditorConfig<br/>{theme, language, eol,<br/>wordWrap, minimap}"]
        LocalStorage["localStorage<br/>code-theme, code-warp,<br/>code-minimap"]
        
        LocalStorage --> |"loads on mount"| EditorConfig
        EditorConfig --> |"saves on change"| LocalStorage
    end
    
    subgraph "Monaco Instance"
        initEditor["initEditor()<br/>monaco.editor.create()"]
        codeBox["codeBox<br/>ref element"]
        monacoInstance["editor<br/>IStandaloneCodeEditor"]
        
        initEditor --> |"attaches to"| codeBox
        initEditor --> monacoInstance
    end
    
    subgraph "Editor Features"
        ContentChange["onDidChangeModelContent<br/>sets isEdit = true"]
        KeyCommand["addCommand<br/>Ctrl+S → quickSave()"]
        ThemeChange["setTheme(theme)"]
        LanguageChange["setModelLanguage(lang)"]
        
        monacoInstance --> ContentChange
        monacoInstance --> KeyCommand
        monacoInstance --> ThemeChange
        monacoInstance --> LanguageChange
    end
    
    subgraph "Configuration Options"
        Themes["Themes:<br/>vs, vs-dark, hc-black"]
        EOL["EOL Sequence:<br/>LF, CRLF"]
        WordWrap["Word Wrap:<br/>on, off"]
        Minimap["Minimap:<br/>enabled, disabled"]
    end
```

The editor configuration is defined at [frontend/src/views/host/file-management/code-editor/index.vue:501-507]():

```typescript
const config = reactive<EditorConfig>({
    theme: 'vs-dark',
    language: 'plaintext',
    eol: monaco.editor.EndOfLineSequence.LF,
    wordWrap: 'on',
    minimap: false,
});
```

The initialization method at [frontend/src/views/host/file-management/code-editor/index.vue:842-878]() creates the Monaco instance with options including `automaticLayout`, `folding`, and event handlers for content changes and keyboard shortcuts.

**Sources:** [frontend/src/views/host/file-management/code-editor/index.vue:501-507](), [frontend/src/views/host/file-management/code-editor/index.vue:842-878]()

### File Tab Management

The code editor supports up to 10 file tabs with persistent state across sessions.

```mermaid
graph LR
    subgraph "Tab State"
        fileTabs["fileTabs[]<br/>max 10 tabs"]
        selectTab["selectTab<br/>current tab path"]
        localStorage["localStorage<br/>code-editor-tabs"]
        
        fileTabs <--> localStorage
        selectTab --> |"points to"| fileTabs
    end
    
    subgraph "Tab Operations"
        addTab["Open File<br/>getContent(path)"]
        removeTab["removeTab(path)<br/>confirm if edited"]
        changeTab["changeTab(path)<br/>load content"]
        removeAllTab["removeAllTab()<br/>close all tabs"]
        removeOtherTab["removeOtherTab(path)<br/>close others"]
        
        addTab --> fileTabs
        removeTab --> fileTabs
        changeTab --> selectTab
    end
    
    subgraph "Tab Context Menu"
        CodeTabs["CodeTabs Component<br/>tabs/index.vue"]
        CloseLeft["Close to Left"]
        CloseRight["Close to Right"]
        CloseAll["Close All"]
        CloseOthers["Close Others"]
        
        CodeTabs --> CloseLeft
        CodeTabs --> CloseRight
        CodeTabs --> CloseAll
        CodeTabs --> CloseOthers
    end
```

Tab state is persisted using `saveTabsToStorage()` at [frontend/src/views/host/file-management/code-editor/index.vue:528-534]() which stores simplified tab objects containing only path and name. Tab operations at [frontend/src/views/host/file-management/code-editor/index.vue:545-677]() include logic for handling unsaved changes with confirmation dialogs.

**Sources:** [frontend/src/views/host/file-management/code-editor/index.vue:523-544](), [frontend/src/views/host/file-management/code-editor/index.vue:545-677]()

### File Tree Navigation

The code editor includes a collapsible file tree using `el-tree-v2` for efficient rendering of large directory structures.

```mermaid
graph TB
    subgraph "Tree Structure"
        treeData["treeData[]<br/>FileTree[]"]
        TreeNode["TreeNode<br/>{id, name, path,<br/>isDir, children}"]
        
        treeData --> TreeNode
    end
    
    subgraph "Tree Operations"
        getFilesTree["getFilesTree(req)<br/>POST /files/tree"]
        handleNodeExpand["handleNodeExpand()<br/>lazy load children"]
        loadedNodes["loadedNodes<br/>Set of loaded paths"]
        
        getFilesTree --> treeData
        handleNodeExpand --> loadedNodes
        loadedNodes --> |"prevents reload"| handleNodeExpand
    end
    
    subgraph "Tree Actions"
        getUpData["getUpData()<br/>navigate up"]
        getRefresh["getRefresh(path)<br/>reload tree"]
        handleCreate["handleCreate(type)<br/>create file/dir"]
        getContent["getContent(path)<br/>open file"]
        
        getUpData --> getFilesTree
        getRefresh --> getFilesTree
        handleCreate --> treeData
        getContent --> |"loads in editor"| TreeNode
    end
    
    subgraph "Tree Display"
        ToggleShow["toggleShow()<br/>collapse/expand tree"]
        isShow["isShow<br/>tree visibility"]
        treeHeight["treeHeight<br/>dynamic height"]
        
        ToggleShow --> isShow
        isShow --> treeHeight
    end
```

The tree component is rendered at [frontend/src/views/host/file-management/code-editor/index.vue:143-226]() with custom templates for directory and file nodes. The lazy loading logic at [frontend/src/views/host/file-management/code-editor/index.vue:1136-1160]() fetches children only when a directory is expanded, maintaining a `Set` of loaded paths to prevent redundant API calls.

**Sources:** [frontend/src/views/host/file-management/code-editor/index.vue:143-226](), [frontend/src/views/host/file-management/code-editor/index.vue:1136-1175]()

### Language Detection and Syntax Highlighting

The editor automatically detects file languages based on file extensions and provides appropriate syntax highlighting.

Language mappings are defined in `@/global/mimetype` and matched at [frontend/src/views/host/file-management/code-editor/index.vue:1000-1024]():

```typescript
Languages.forEach((language) => {
    const ext = fileExtension.value.substring(1);
    if (language.value.indexOf(ext) > -1) {
        config.language = language.label;
    }
});
```

Monaco worker configuration is set up at [frontend/src/views/host/file-management/code-editor/index.vue:415-431]() supporting JSON, CSS, HTML, and TypeScript/JavaScript language services.

**Sources:** [frontend/src/views/host/file-management/code-editor/index.vue:415-431](), [frontend/src/views/host/file-management/code-editor/index.vue:1000-1024]()

### Save Operations

The editor provides both manual and keyboard shortcut-based save operations with unsaved change tracking.

```mermaid
graph LR
    subgraph "Edit Tracking"
        onDidChangeModelContent["onDidChangeModelContent<br/>editor event"]
        isEdit["isEdit: boolean<br/>unsaved changes flag"]
        oldFileContent["oldFileContent<br/>original content"]
        
        onDidChangeModelContent --> |"sets true"| isEdit
    end
    
    subgraph "Save Actions"
        SaveButton["Save Button<br/>saveContent()"]
        KeyboardShortcut["Ctrl+S<br/>quickSave()"]
        AutoSave["Tab Close<br/>confirm dialog"]
        
        SaveButton --> saveFileContent
        KeyboardShortcut --> saveFileContent
        AutoSave --> |"optional"| saveFileContent
    end
    
    subgraph "Save Process"
        saveFileContent["saveFileContent(form)<br/>POST /files/save"]
        Success["isEdit = false<br/>oldFileContent = content"]
        
        saveFileContent --> Success
    end
    
    subgraph "Unsaved Protection"
        handleClose["handleClose()<br/>confirm if isEdit"]
        removeTab["removeTab()<br/>confirm if isEdit"]
        changeTab["Open New File<br/>confirm if isEdit"]
        
        handleClose --> |"shows dialog"| isEdit
        removeTab --> |"shows dialog"| isEdit
        changeTab --> |"shows dialog"| isEdit
    end
```

The save operation at [frontend/src/views/host/file-management/code-editor/index.vue:884-903]() calls the API and updates the `isEdit` flag and `oldFileContent` reference on success. The keyboard shortcut is registered at [frontend/src/views/host/file-management/code-editor/index.vue:869]() using Monaco's command binding system.

**Sources:** [frontend/src/views/host/file-management/code-editor/index.vue:869-882](), [frontend/src/views/host/file-management/code-editor/index.vue:884-903]()

## Special Features

### Favorites System

Users can mark frequently accessed files and directories as favorites for quick access.

```mermaid
graph LR
    subgraph "Favorite Actions"
        addToFavorite["addToFavorite(row)<br/>on star click"]
        addFavoriteAPI["addFavorite(path)<br/>POST /files/favorite"]
        
        addToFavorite --> |"path"| addFavoriteAPI
    end
    
    subgraph "Favorite Display"
        favoritePopover["Popover on Hover<br/>getFavorites()"]
        searchFavorite["searchFavorite(params)<br/>POST /files/favorite/search"]
        favoritesList["favorites[]<br/>table display"]
        
        favoritePopover --> searchFavorite
        searchFavorite --> favoritesList
    end
    
    subgraph "Favorite Navigation"
        toFavorite["toFavorite(row)<br/>navigate to item"]
        jumpToPath["jump(path)<br/>for folders"]
        openFile["open file<br/>for files"]
        
        toFavorite --> jumpToPath
        toFavorite --> openFile
    end
    
    subgraph "Remove Favorite"
        removeStar["Click Filled Star<br/>remove(favoriteID)"]
        removeFavoriteAPI["removeFavorite(id)<br/>POST /files/favorite/del"]
        
        removeStar --> removeFavoriteAPI
    end
```

The favorites popover is rendered at [frontend/src/views/host/file-management/index.vue:262-314]() with hover state tracking at [frontend/src/views/host/file-management/index.vue:1720-1737]() using `showFavorite()` and `hideFavorite()` methods to display the star icon on row hover.

**Sources:** [frontend/src/views/host/file-management/index.vue:262-314](), [frontend/src/views/host/file-management/index.vue:1720-1737](), [frontend/src/api/modules/files.ts:133-148]()

### Recycle Bin

Deleted files can be moved to a recycle bin instead of permanent deletion, allowing recovery.

```mermaid
graph TB
    subgraph "Delete Options"
        DeleteDialog["Delete Dialog<br/>delete/index.vue"]
        forceDelete["forceDelete: boolean<br/>permanent/recycle"]
        
        DeleteDialog --> |"configures"| forceDelete
    end
    
    subgraph "Recycle Bin Storage"
        deleteFile["deleteFile(form)<br/>POST /files/del"]
        RecycleBinTable["RecycleBin Table<br/>{sourcePath, rName,<br/>deleteTime, from}"]
        
        deleteFile --> |"forceDelete: false"| RecycleBinTable
    end
    
    subgraph "Recycle Bin Operations"
        RecycleBinDialog["Recycle Bin Dialog<br/>recycle-bin/index.vue"]
        getRecycleList["getRecycleList(params)<br/>POST /files/recycle/search"]
        reduceFile["reduceFile(params)<br/>POST /files/recycle/reduce"]
        clearRecycle["clearRecycle()<br/>POST /files/recycle/clear"]
        
        RecycleBinDialog --> getRecycleList
        RecycleBinDialog --> reduceFile
        RecycleBinDialog --> clearRecycle
    end
    
    subgraph "Status Check"
        getRecycleStatus["getRecycleStatus()<br/>GET /files/recycle/status"]
        RecycleEnabled["enabled/disabled<br/>system setting"]
        
        getRecycleStatus --> RecycleEnabled
    end
```

The recycle bin dialog is opened via `openRecycleBin()` at [frontend/src/views/host/file-management/index.vue:1014-1018]() and referenced at [frontend/src/views/host/file-management/index.vue:628](). Files in the recycle bin include metadata like original source path, deletion time, and a recovery name.

**Sources:** [frontend/src/views/host/file-management/index.vue:1014-1018](), [frontend/src/api/modules/files.ts:121-131](), [frontend/src/api/interface/file.ts:180-194]()

### Terminal Integration

The file browser provides direct terminal access at the current directory location.

The terminal is opened via `toTerminal()` at [frontend/src/views/host/file-management/index.vue:1266-1269]() which navigates to the terminal view with the current path as a query parameter:

```typescript
const toTerminal = () => {
    router.push({ path: '/hosts/terminal', query: { path: req.path } });
};
```

A terminal dialog component is also available at [frontend/src/views/host/file-management/index.vue:634]() for in-page terminal access.

**Sources:** [frontend/src/views/host/file-management/index.vue:1266-1269](), [frontend/src/views/host/file-management/index.vue:634]()

### Mount Point Display

The system displays available mount points with free space indicators for quick navigation.

```mermaid
graph LR
    subgraph "Mount Point Data"
        searchHostMount["searchHostMount()<br/>POST /files/mount"]
        hostMount["hostMount[]<br/>DiskInfo[]"]
        
        searchHostMount --> hostMount
    end
    
    subgraph "Display Logic"
        SingleMount["Single Mount<br/>direct button"]
        MultiMount["Multiple Mounts<br/>dropdown menu"]
        FormatSize["formatFileSize()<br/>display free space"]
        
        hostMount --> SingleMount
        hostMount --> MultiMount
        hostMount --> FormatSize
    end
    
    subgraph "Navigation"
        JumpToMount["jump(mount.path)<br/>navigate to mount"]
        
        SingleMount --> JumpToMount
        MultiMount --> JumpToMount
    end
```

Mount points are displayed at [frontend/src/views/host/file-management/index.vue:318-345]() with conditional rendering: a single button for one mount or a dropdown for multiple mounts. Each mount shows its path and available free space.

**Sources:** [frontend/src/views/host/file-management/index.vue:318-345](), [frontend/src/api/modules/files.ts:166-168]()

## API Layer and Request Flow

### Request/Response Types

The file operations use strongly-typed TypeScript interfaces for all API interactions.

| Interface | Purpose | Key Fields |
|-----------|---------|------------|
| `File.ReqFile` | File listing request | path, search, expand, showHidden, containSub, sortBy, sortOrder |
| `File.File` | File metadata response | path, name, size, isDir, mode, user, group, modTime |
| `File.FileCreate` | File/directory creation | path, isDir, mode, isLink, isSymlink |
| `File.FileEdit` | Save file content | path, content |
| `File.FileCompress` | Compression request | files[], type, dst, name, replace, secret |
| `File.FileMove` | Move/copy operation | oldPaths[], newPath, type |
| `File.FileTree` | Tree node structure | id, name, isDir, path, children[] |

The base request interface `ReqFile` is defined at [frontend/src/api/interface/file.ts:29-39]() extending the common `ReqPage` interface for pagination support. Response types include metadata like permissions, ownership, timestamps, and optional fields like `favoriteID` and `remark`.

**Sources:** [frontend/src/api/interface/file.ts:1-263]()

### API Timeout Configuration

File operations use extended timeouts to accommodate large files and long-running operations.

```typescript
// Standard operations: 5 minutes
getFilesList(params: File.ReqFile) => 
    http.post<File.File>('files/search', params, TimeoutEnum.T_5M)

// Compression: 10 minutes
compressFile(form: File.FileCompress) => 
    http.post<File.File>('files/compress', form, TimeoutEnum.T_10M)

// File download: 40 seconds
downloadFile(params: File.FileDownload) => 
    http.download<BlobPart>('files/download', params, { 
        responseType: 'blob', 
        timeout: TimeoutEnum.T_40S 
    })
```

Timeout values are defined in the `TimeoutEnum` enumeration and passed as the third parameter to HTTP methods. This is critical for operations like directory size calculation, large file compression, and batch operations that may take significant time.

**Sources:** [frontend/src/api/modules/files.ts:9-11](), [frontend/src/api/modules/files.ts:46-50](), [frontend/src/api/modules/files.ts:105-107]()

### Multi-Node Support

File operations support multi-node architecture by accepting an optional `operateNode` query parameter.

```mermaid
graph LR
    subgraph "Node Selection"
        CurrentNode["globalStore.currentNode<br/>selected node"]
        QueryParam["?operateNode=X<br/>route to specific node"]
    end
    
    subgraph "Node-Specific APIs"
        getFilesListByNode["getFilesListByNode(params)<br/>POST /files/search?operateNode=X"]
        deleteFileByNode["deleteFileByNode(form, node)<br/>POST /files/del?operateNode=X"]
        getRecycleStatusByNode["getRecycleStatusByNode(node)<br/>GET /files/recycle/status?operateNode=X"]
        readByLine["readByLine(req, operateNode)<br/>POST /files/read?operateNode=X"]
    end
    
    CurrentNode --> QueryParam
    QueryParam --> getFilesListByNode
    QueryParam --> deleteFileByNode
    QueryParam --> getRecycleStatusByNode
    QueryParam --> readByLine
```

Node-aware API methods are defined at [frontend/src/api/modules/files.ts:13-15](), [frontend/src/api/modules/files.ts:33-35](), [frontend/src/api/modules/files.ts:141-144](), and [frontend/src/api/modules/files.ts:158-160]() allowing the Core API to route requests to specific agent nodes in a multi-node deployment.

**Sources:** [frontend/src/api/modules/files.ts:13-15](), [frontend/src/api/modules/files.ts:33-35](), [frontend/src/api/modules/files.ts:141-144](), [frontend/src/api/modules/files.ts:158-160]()

### Async Task Pattern for Long Operations

Operations like compression, decompression, and large file moves use an asynchronous task pattern to prevent timeout issues.

```mermaid
sequenceDiagram
    participant UI as "Frontend UI"
    participant API as "Files API"
    participant Backend as "Agent Backend"
    participant TaskLog as "Task Log System"
    
    UI->>API: POST /files/compress
    API->>Backend: initiate compression
    Backend->>Backend: create task with ID
    Backend-->>API: return immediately
    API-->>UI: show success message
    
    UI->>UI: continue browsing
    
    loop Background Processing
        Backend->>Backend: compress files
        Backend->>TaskLog: log progress
    end
    
    Backend->>Backend: mark task complete
    
    Note over UI,TaskLog: User can monitor via task log viewer
```

While the frontend file operations use extended timeouts, the backend typically implements asynchronous task processing for operations that may exceed reasonable HTTP timeout limits. Tasks are tracked through the system's general task logging mechanism, allowing users to monitor progress without blocking the UI.

**Sources:** [frontend/src/api/modules/files.ts:46-50](), [frontend/src/views/host/file-management/index.vue:851-869]()

---

# Page: AI and ML Infrastructure

# AI and ML Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [frontend/src/lang/modules/en.ts](frontend/src/lang/modules/en.ts)
- [frontend/src/lang/modules/es-es.ts](frontend/src/lang/modules/es-es.ts)
- [frontend/src/lang/modules/ja.ts](frontend/src/lang/modules/ja.ts)
- [frontend/src/lang/modules/ko.ts](frontend/src/lang/modules/ko.ts)
- [frontend/src/lang/modules/ms.ts](frontend/src/lang/modules/ms.ts)
- [frontend/src/lang/modules/pt-br.ts](frontend/src/lang/modules/pt-br.ts)
- [frontend/src/lang/modules/ru.ts](frontend/src/lang/modules/ru.ts)
- [frontend/src/lang/modules/tr.ts](frontend/src/lang/modules/tr.ts)
- [frontend/src/lang/modules/zh-Hant.ts](frontend/src/lang/modules/zh-Hant.ts)
- [frontend/src/lang/modules/zh.ts](frontend/src/lang/modules/zh.ts)

</details>



## Purpose and Scope

This document describes 1Panel's AI and Machine Learning infrastructure capabilities, including AI agent deployment, model management (Ollama), GPU/XPU monitoring, MCP (Model Context Protocol) server management, and AI proxy configuration. This infrastructure enables users to deploy and manage AI workloads directly from the 1Panel interface.

For application installation workflow, see [App Installation and Deployment](#6.2). For container management operations, see [Container Management](#8.1). For website proxy configuration, see [Website Management System](#7).

---

## System Architecture

The AI infrastructure integrates with 1Panel's core systems to provide AI agent hosting, model lifecycle management, hardware monitoring, and protocol server deployment.

```mermaid
graph TB
    subgraph "Frontend AI Module"
        AIMenu["AI Menu<br/>(menu.aiTools)"]
        MCPMenu["MCP Menu<br/>(menu.mcp)"]
        AgentUI["Agent Management UI"]
        ModelUI["Model Management UI"]
        GPUUI["GPU Monitoring UI"]
        MCPUI["MCP Server UI"]
        ProxyUI["AI Proxy UI"]
    end
    
    subgraph "Backend Agent API"
        AIMgmt["AI Management<br/>(AIMgmt service)"]
        GPUMonitor["GPU Monitor<br/>nvidia-smi/xpu-smi"]
        MCPHandler["MCP Handler"]
        ModelSync["Model Sync<br/>(Ollama API)"]
    end
    
    subgraph "External AI Systems"
        OllamaEngine["Ollama Engine<br/>Local Models"]
        OpenAI["OpenAI API"]
        FeishuBot["Feishu/Lark Bot"]
        GPUDrivers["GPU Drivers<br/>NVIDIA/XPU"]
    end
    
    subgraph "Infrastructure Layer"
        Docker["Docker Engine"]
        Nginx["Nginx<br/>(AI Proxy)"]
        AgentDB["agent.db<br/>(AI metadata)"]
    end
    
    AIMenu --> AgentUI
    AIMenu --> ModelUI
    AIMenu --> GPUUI
    AIMenu --> ProxyUI
    MCPMenu --> MCPUI
    
    AgentUI --> AIMgmt
    ModelUI --> ModelSync
    GPUUI --> GPUMonitor
    MCPUI --> MCPHandler
    ProxyUI --> Nginx
    
    AIMgmt --> AgentDB
    ModelSync --> OllamaEngine
    ModelSync --> OpenAI
    AIMgmt --> FeishuBot
    GPUMonitor --> GPUDrivers
    
    MCPHandler --> Docker
    MCPHandler --> AgentDB
    
    style AIMgmt fill:#f9f9f9
    style GPUMonitor fill:#f9f9f9
    style OllamaEngine fill:#e8f5e9
    style GPUDrivers fill:#e8f5e9
```

**AI Infrastructure Architecture**

Sources: [frontend/src/lang/modules/en.ts:386-387](), [frontend/src/lang/modules/zh.ts:373-374]()

---

## AI Agent Management

AI agents in 1Panel are containerized applications that integrate with model providers and chat platforms. Agents are configured with model accounts, which define the LLM backend (Ollama, OpenAI, etc.).

### Model Accounts and Providers

Model accounts store API credentials and connection information for various AI providers. Each account can be shared across multiple agents.

```mermaid
graph LR
    subgraph "Model Account Types"
        OllamaAccount["Ollama Provider<br/>baseUrl + optional auth"]
        OpenAIAccount["OpenAI Provider<br/>apiKey + baseUrl"]
        CustomAccount["Custom Provider<br/>token + endpoint"]
    end
    
    subgraph "Agent Configuration"
        Agent1["Agent 1<br/>(openclaw.json)"]
        Agent2["Agent 2<br/>(openclaw.json)"]
        Agent3["Agent 3<br/>(openclaw.json)"]
    end
    
    subgraph "Operations"
        CreateAccount["Create Model Account"]
        SyncAgents["Sync Agents<br/>(update openclaw.json)"]
        VerifyAccount["Verify Connection"]
    end
    
    CreateAccount --> OllamaAccount
    CreateAccount --> OpenAIAccount
    CreateAccount --> CustomAccount
    
    OllamaAccount --> Agent1
    OllamaAccount --> Agent2
    OpenAIAccount --> Agent3
    
    SyncAgents --> Agent1
    SyncAgents --> Agent2
    SyncAgents --> Agent3
```

**Model Account and Agent Relationship**

Key configuration fields:

| Field | Description | Location |
|-------|-------------|----------|
| `provider` | Model provider name (Ollama, OpenAI, etc.) | Model account config |
| `apiKey` | API authentication key | Model account config |
| `baseUrl` | Provider endpoint URL | Model account config |
| `token` | Alternative authentication token | Model account config |
| `manualModel` | Manually specified model name | Agent config |
| `verified` | Connection verification status | Runtime state |

Sources: [frontend/src/lang/modules/zh.ts:655-689](), [frontend/src/lang/modules/en.ts:655-689]()

### Agent Lifecycle Operations

Agents support standard lifecycle operations through the 1Panel interface:

- **Create Agent**: Configure model account, ports (WebUI, Bridge), and version
- **Sync Agents**: Update `openclaw.json` files for all agents using a model account
- **Switch Model**: Change the active model for an agent
- **Restart Gateway**: Apply configuration changes

Port configuration:

| Port Type | Description | Default |
|-----------|-------------|---------|
| `webuiPort` | Web interface access port | User-defined |
| `bridgePort` | Internal bridge communication port | User-defined |

Sources: [frontend/src/lang/modules/zh.ts:656-666]()

### Chat Channel Integration

1Panel supports integrating AI agents with Feishu (Lark) chat platform for bot interactions.

```mermaid
graph TB
    subgraph "Feishu Configuration"
        BotConfig["Bot Configuration"]
        BotName["botName"]
        AppID["appId"]
        AppSecret["appSecret"]
        DMPolicy["dmPolicy<br/>(private chat)"]
    end
    
    subgraph "Pairing Process"
        PairingCode["Pairing Code<br/>(user input)"]
        ApprovePairing["Approve Pairing"]
        Gateway["Agent Gateway"]
    end
    
    subgraph "Operations"
        SaveRestart["Save & Restart Gateway"]
        Validation["Validate Required Fields"]
    end
    
    BotConfig --> BotName
    BotConfig --> AppID
    BotConfig --> AppSecret
    BotConfig --> DMPolicy
    
    BotName --> Validation
    AppID --> Validation
    AppSecret --> Validation
    
    Validation --> SaveRestart
    SaveRestart --> Gateway
    
    PairingCode --> ApprovePairing
    ApprovePairing --> Gateway
```

**Feishu Bot Integration Flow**

Feishu integration fields:

| Field | Required | Description |
|-------|----------|-------------|
| `botName` | Yes | Bot display name in Feishu |
| `appId` | Yes | Feishu application ID |
| `appSecret` | Yes | Feishu application secret |
| `dmPolicy` | No | Private message handling policy |
| `pairingCode` | Yes | Pairing verification code |

Sources: [frontend/src/lang/modules/zh.ts:677-689]()

---

## Model Management

1Panel provides integrated management for Ollama models with operations for pulling, synchronizing, and monitoring model downloads.

### Ollama Integration

Ollama serves as the primary local model provider, allowing users to run LLMs without external API dependencies.

```mermaid
graph TB
    subgraph "Model Operations"
        CreateModel["Create/Pull Model<br/>(ollama pull)"]
        SyncModels["Sync Models<br/>(list + compare)"]
        ViewLogs["View Pull Logs"]
        DeleteOrphans["Delete Orphaned Models"]
    end
    
    subgraph "Model Metadata"
        ModelName["Model Name"]
        PullStatus["Pull Status<br/>(downloading/ready)"]
        FromRemote["From Remote<br/>(via 1Panel?)"]
        Logs["Pull Logs"]
    end
    
    subgraph "Container Connectivity"
        ContainerAddr["Container Connection Address<br/>(internal network)"]
        ExternalAddr["External Connection Address"]
    end
    
    CreateModel --> ModelName
    CreateModel --> PullStatus
    CreateModel --> Logs
    
    SyncModels --> FromRemote
    SyncModels --> DeleteOrphans
    
    ViewLogs --> Logs
    
    ModelName --> ContainerAddr
    ModelName --> ExternalAddr
```

**Ollama Model Management Flow**

Model states and sources:

| State | Description | Location Reference |
|-------|-------------|-------------------|
| `downloading` | Model pull in progress | Frontend status |
| `ready` | Model available for use | Frontend status |
| `from_remote` | Model not installed via 1Panel | Metadata flag |
| `no_logs` | Pull logs deleted or unavailable | Log status |

Sources: [frontend/src/lang/modules/zh.ts:691-699](), [frontend/src/lang/modules/en.ts:691-699]()

### Model Pull and Synchronization

The model creation dialog supports pulling models from the Ollama registry:

1. User specifies model name (e.g., `llama2`, `mistral`)
2. Backend initiates `ollama pull {model_name}`
3. Pull progress logged to task system
4. Model becomes available at container connection address

**Sync Behavior**: When syncing Ollama models, 1Panel compares the Ollama engine's model list with 1Panel's database. If models exist in 1Panel but not in Ollama, the system prompts for deletion.

Sources: [frontend/src/lang/modules/zh.ts:693-699]()

### Connection Addresses

Models expose two connection types:

- **Container Connection Address**: Used by containers in the same Docker network to access Ollama
- **External Connection Address**: Used by external clients or the host system

Sources: [frontend/src/lang/modules/en.ts:696]()

---

## GPU and XPU Monitoring

1Panel provides real-time and historical monitoring for NVIDIA GPUs and Intel XPUs through command-line tool integration.

### Hardware Detection

The system detects GPU/XPU availability by checking for `nvidia-smi` or `xpu-smi` commands:

```mermaid
graph TB
    SystemCheck["System Check"]
    NvidiaSMI{"nvidia-smi<br/>available?"}
    XPUSMI{"xpu-smi<br/>available?"}
    NoGPU["Display Error<br/>gpuHelper message"]
    GPUMonitoring["Enable GPU Monitoring"]
    
    SystemCheck --> NvidiaSMI
    NvidiaSMI -->|Yes| GPUMonitoring
    NvidiaSMI -->|No| XPUSMI
    XPUSMI -->|Yes| GPUMonitoring
    XPUSMI -->|No| NoGPU
    
    subgraph "GPU Capabilities"
        GPUMonitoring --> RealTime["Real-time Monitoring"]
        GPUMonitoring --> Historical["Historical Data"]
        GPUMonitoring --> ProcessTrack["Process Tracking"]
    end
```

**GPU Detection Flow**

Error message when GPUs are not detected:
> "当前系统未检测到 NVIDIA-SMI 或者 XPU-SMI 指令，请检查后重试！"

Sources: [frontend/src/lang/modules/zh.ts:712-713]()

### Performance Metrics

The GPU monitoring interface displays comprehensive hardware metrics:

#### Core Metrics Table

| Metric | Description | Unit | Helper Text |
|--------|-------------|------|-------------|
| `gpuUtil` | GPU compute utilization | % | - |
| `temperature` | GPU die temperature | °C | "GPU 温度过高会导致 GPU 频率下降" |
| `performanceState` | Performance state (P0-P12) | P-state | "从 P0 (最大性能) 到 P12 (最小性能)" |
| `powerUsage` / `powerCurrent` | Current power draw | W | - |
| `powerLimit` | Maximum power limit | W | - |
| `memoryUsage` | VRAM utilization | % | - |
| `memoryUsed` | Used VRAM | GB | - |
| `memoryTotal` | Total VRAM | GB | - |
| `fanSpeed` | Fan rotation speed | % or RPM | - |

Sources: [frontend/src/lang/modules/zh.ts:723-735]()

#### Driver and System Information

| Field | Description |
|-------|-------------|
| `driverVersion` | GPU driver version |
| `cudaVersion` | CUDA toolkit version (NVIDIA) |
| `busID` | PCIe bus address |
| `persistenceMode` | Driver persistence mode (enabled/disabled) |
| `displayActive` | GPU initialized for display output (yes/no) |
| `ecc` | Error Correction Code status |
| `computeMode` | Compute mode (default/exclusive-process/exclusive-thread/prohibited) |
| `migMode` | Multi-Instance GPU mode (supported/not supported) |

**Persistence Mode**: When enabled, the GPU driver remains loaded even when no processes are using it, allowing faster task response times at the cost of increased idle power consumption.

Sources: [frontend/src/lang/modules/zh.ts:737-760]()

### Process Tracking

GPU monitoring includes per-process resource usage:

```mermaid
graph LR
    subgraph "Process Metrics"
        ProcessName["Process Name"]
        ProcessType["Process Type<br/>(G/C/CG)"]
        ProcessMemory["VRAM Usage"]
        SharedMemory["Shared Memory<br/>(shr)"]
        ProcessCount["Total Process Count"]
    end
    
    subgraph "Process Types"
        TypeG["G: Graphics"]
        TypeC["C: Compute"]
        TypeCG["CG: Compute+Graphics"]
    end
    
    ProcessType --> TypeG
    ProcessType --> TypeC
    ProcessType --> TypeCG
```

**GPU Process Information**

Process types indicate the GPU workload category:
- **G (Graphics)**: Rendering and display workloads
- **C (Compute)**: CUDA/OpenCL computational workloads
- **CG (Compute+Graphics)**: Hybrid workloads

Sources: [frontend/src/lang/modules/zh.ts:714-721]()

### Compute Mode Details

| Mode | Description | Use Case |
|------|-------------|----------|
| `default` | Multiple processes can execute concurrently | General purpose |
| `exclusiveProcess` | Only one CUDA context can use the GPU, shared by multiple threads | High-performance single-app scenarios |
| `exclusiveThread` | Only one thread in a CUDA context can use the GPU | Maximum isolation |
| `prohibited` | GPU compute is disabled | Troubleshooting |

Sources: [frontend/src/lang/modules/zh.ts:751-759]()

### Historical Monitoring

The GPU interface provides two views:

- **Real-time Monitoring** (`current`): Live metrics updated at polling intervals
- **Historical Records** (`history`): Time-series data for trend analysis

If certain metrics are unavailable, the interface displays: "当前版本或驱动不支持显示该参数。"

Sources: [frontend/src/lang/modules/zh.ts:762-764]()

---

## MCP Server Management

1Panel supports deploying MCP (Model Context Protocol) servers, enabling AI agents to access external tools and data sources through a standardized protocol.

### Transport Mechanisms

MCP servers support three transport types:

```mermaid
graph TB
    subgraph "Transport Types"
        StdIO["stdio Transport<br/>(npx/binary commands)"]
        SSE["SSE Transport<br/>(Server-Sent Events)"]
        StreamHTTP["Streamable HTTP Transport<br/>(HTTP streaming)"]
    end
    
    subgraph "stdio Configuration"
        NPXCommand["npx command<br/>(e.g., npx @modelcontextprotocol/server-*)"]
        BinaryCommand["Binary command<br/>(e.g., ./mcp-server)"]
        StdIOEnv["Environment Variables"]
    end
    
    subgraph "SSE Configuration"
        BaseURL["Base URL<br/>(external access path)"]
        SSEPath["SSE Path<br/>(e.g., /sse)"]
        SSEEnv["Environment Variables"]
    end
    
    subgraph "HTTP Configuration"
        HTTPBaseURL["Base URL"]
        StreamPath["Stream Path<br/>(e.g., /mcp)"]
        HTTPEnv["Environment Variables"]
    end
    
    StdIO --> NPXCommand
    StdIO --> BinaryCommand
    StdIO --> StdIOEnv
    
    SSE --> BaseURL
    SSE --> SSEPath
    SSE --> SSEEnv
    
    StreamHTTP --> HTTPBaseURL
    StreamHTTP --> StreamPath
    StreamHTTP --> HTTPEnv
```

**MCP Transport Configuration Options**

Transport-specific fields:

| Transport | Required Fields | Description |
|-----------|----------------|-------------|
| `stdio` | `command` | Executes npx or binary commands directly |
| `SSE` | `baseUrl`, `ssePath` | Server-Sent Events endpoint |
| `streamableHttp` | `baseUrl`, `streamableHttpPath` | HTTP streaming endpoint |

**Path Uniqueness**: SSE paths and HTTP stream paths must not conflict with other MCP servers on the same host.

Sources: [frontend/src/lang/modules/zh.ts:767-790]()

### Environment Configuration

MCP servers can be configured with environment variables for secrets, API keys, and configuration:

```mermaid
graph TB
    subgraph "Environment Variables"
        EnvVar1["Variable 1<br/>envKey: API_KEY<br/>envValue: sk-xxx"]
        EnvVar2["Variable 2<br/>envKey: MODEL_NAME<br/>envValue: gpt-4"]
        EnvVar3["Variable N<br/>envKey: TIMEOUT<br/>envValue: 30"]
    end
    
    subgraph "MCP Server Process"
        ServerProcess["MCP Server<br/>(inherits env vars)"]
    end
    
    EnvVar1 --> ServerProcess
    EnvVar2 --> ServerProcess
    EnvVar3 --> ServerProcess
```

**MCP Environment Variable Configuration**

Sources: [frontend/src/lang/modules/zh.ts:774-776]()

### Domain Binding and External Access

MCP servers can be bound to a website configuration for enhanced security:

```mermaid
graph TB
    subgraph "Unbound Configuration"
        DirectPort["MCP Server<br/>Port: 8000<br/>External Access: Yes"]
    end
    
    subgraph "Bound Configuration"
        Website["Nginx Website<br/>Domain: mcp.example.com"]
        MCPBackend["MCP Server<br/>Port: 8000<br/>External Access: No"]
        UpdatedURL["External URL Updated<br/>(all installed servers)"]
    end
    
    BindOperation["Bind Domain"]
    
    DirectPort --> BindOperation
    BindOperation --> Website
    Website --> MCPBackend
    BindOperation --> UpdatedURL
```

**MCP Domain Binding Flow**

When binding a domain:
1. Creates/uses Nginx website configuration
2. Updates `externalUrl` for all installed MCP servers
3. Disables direct port external access for enhanced security
4. MCP servers become accessible via `https://domain.com/sse` or `https://domain.com/mcp`

Domain configuration:
- **domain**: Default access address (IP or domain, e.g., `192.168.1.1` or `example.com`)
- **bindDomain**: Target website for binding
- **bindDomainHelper**: Warning that binding updates all installed MCP servers and closes port external access

Sources: [frontend/src/lang/modules/zh.ts:779-785]()

### MCP Server Import

MCP servers can be imported from a configuration file:

```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-example"],
      "env": {
        "API_KEY": "value"
      }
    }
  }
}
```

**Error Handling**: If the `mcpServers` structure is incorrect, the import displays: "mcpServers 结构不正确"

Sources: [frontend/src/lang/modules/zh.ts:783-784]()

### Transport Command Examples

Transport-specific command helpers:

- **npx/binary**: "当前仅支持 npx 和 二进制启动的命令"
- **npx**: "适合 npx 或者 二进制启动的 mcp"
- **uvx**: "适合 uvx 启动的 mcp"

Sources: [frontend/src/lang/modules/zh.ts:782,789-790]()

---

## AI Proxy Enhancement

1Panel provides AI proxy configuration to enhance security and performance of AI services running in containers.

### Proxy Architecture

```mermaid
graph LR
    subgraph "Client Access"
        ExternalClient["External Client"]
        HTTPS["HTTPS Request"]
    end
    
    subgraph "1Panel Nginx Proxy"
        ProxyConfig["AI Proxy Website<br/>(HTTPS + Domain)"]
        IPWhitelist["IP Whitelist Check"]
        Streaming["Streaming Support"]
    end
    
    subgraph "Backend AI Service"
        AIContainer["AI Container<br/>(Ollama/OpenAI compatible)"]
        ClosedPort["Port External Access: Disabled"]
    end
    
    ExternalClient --> HTTPS
    HTTPS --> ProxyConfig
    ProxyConfig --> IPWhitelist
    IPWhitelist --> Streaming
    Streaming --> AIContainer
    AIContainer --> ClosedPort
```

**AI Proxy Architecture**

Sources: [frontend/src/lang/modules/zh.ts:701-710]()

### Security Features

The AI proxy configuration provides multiple security enhancements:

| Feature | Description | Implementation |
|---------|-------------|----------------|
| **HTTPS Binding** | Encrypts traffic between clients and proxy | Binds domain with SSL certificate |
| **IP Whitelisting** | Restricts access to authorized IPs only | `whiteListHelper`: Only whitelisted IPs can access |
| **Port Closure** | Disables direct container port access | Close external access in app parameters |
| **Domain Binding** | Access via domain instead of IP:port | Creates Nginx website configuration |

Sources: [frontend/src/lang/modules/zh.ts:703-704,709]()

### Proxy Configuration Steps

1. **Create AI Proxy**: Configure domain and HTTPS binding
2. **Enable Streaming**: Support for streaming API responses (proxyHelper3)
3. **Manage in Website List**: View and manage proxy in website list (proxyHelper4)
4. **Close Container Port**: Disable port external access in App Store > Installed > ollama > Parameters (proxyHelper5)
5. **Delete Proxy**: Remove proxy by deleting website configuration (proxyHelper6)

Sources: [frontend/src/lang/modules/zh.ts:703-708]()

### Streaming Support

The proxy explicitly supports streaming responses, critical for real-time AI interactions where token-by-token generation provides better user experience.

Sources: [frontend/src/lang/modules/zh.ts:705]()

---

## TensorRT LLM Support

1Panel provides infrastructure for deploying TensorRT-optimized language models.

### Configuration

| Field | Description |
|-------|-------------|
| `modelDir` | Directory containing TensorRT model files |
| `commandHelper` | Port configuration for external access |
| `imageAlert` | Warning about large image size |
| `modelSpeedup` | Enable TensorRT model acceleration |
| `modelType` | Type of model being deployed |

**Image Size Warning**: Due to the large size of TensorRT images, 1Panel recommends manually downloading images to the server before installation.

Sources: [frontend/src/lang/modules/zh.ts:792-799]()

### Command Configuration

For external access, the command port must match the application's exposed port to ensure proper routing through 1Panel's network configuration.

Sources: [frontend/src/lang/modules/zh.ts:795]()

---

## Integration with Other Systems

### Application Store Integration

AI components (Ollama, TensorRT LLM, AI agents) are installed through the App Store system:
- Deployed as Docker Compose applications
- Managed via [App Installation and Deployment](#6.2) workflow
- Configuration updates trigger container rebuilds

### Container Network Integration

AI services leverage 1Panel's container networking:
- Internal container-to-container communication via service names
- External access controlled through port mappings
- Network isolation via Docker networks

See [Container Management](#8.1) for details on Docker networking.

### Website Management Integration

AI proxy configurations are implemented as Nginx websites:
- SSL certificate management
- Domain binding and routing
- Access control via IP whitelisting

See [Website Management System](#7) for Nginx configuration details.

---

## Menu Navigation

The AI features are accessible through two main menu items:

| Menu Item | i18n Key | Purpose |
|-----------|----------|---------|
| AI | `menu.aiTools` | Agent management, models, GPU monitoring, proxy |
| MCP | `menu.mcp` | MCP server deployment and configuration |

Sources: [frontend/src/lang/modules/zh.ts:373-374](), [frontend/src/lang/modules/en.ts:386-387]()

---

# Page: AI Agents and Model Management

# AI Agents and Model Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [frontend/src/lang/modules/en.ts](frontend/src/lang/modules/en.ts)
- [frontend/src/lang/modules/es-es.ts](frontend/src/lang/modules/es-es.ts)
- [frontend/src/lang/modules/ja.ts](frontend/src/lang/modules/ja.ts)
- [frontend/src/lang/modules/ko.ts](frontend/src/lang/modules/ko.ts)
- [frontend/src/lang/modules/ms.ts](frontend/src/lang/modules/ms.ts)
- [frontend/src/lang/modules/pt-br.ts](frontend/src/lang/modules/pt-br.ts)
- [frontend/src/lang/modules/ru.ts](frontend/src/lang/modules/ru.ts)
- [frontend/src/lang/modules/tr.ts](frontend/src/lang/modules/tr.ts)
- [frontend/src/lang/modules/zh-Hant.ts](frontend/src/lang/modules/zh-Hant.ts)
- [frontend/src/lang/modules/zh.ts](frontend/src/lang/modules/zh.ts)

</details>



## Purpose and Scope

This document covers 1Panel's AI infrastructure management capabilities, specifically focusing on AI agent creation, model account configuration, and integration with AI model providers. The system enables deployment and management of AI agents that can be connected to chat platforms like Feishu/Lark.

For GPU monitoring and hardware resource tracking, see [GPU Monitoring and XPU Support](#9.2). For MCP (Model Context Protocol) server management, see [MCP Server Management](#9.3). For AI proxy configuration and load balancing, see [AI Proxy Enhancement](#9.4).

---

## System Architecture Overview

The AI agent management system integrates with 1Panel's application ecosystem and provides a layer for connecting AI models with external chat platforms.

```mermaid
graph TB
    subgraph "Frontend UI"
        AgentUI["Agent Management UI<br/>aiTools/agents views"]
        ModelUI["Model Management UI<br/>aiTools/model views"]
        ChannelUI["Chat Channel UI<br/>Feishu/Lark config"]
    end
    
    subgraph "Backend Agent API"
        AgentService["AI Agent Service<br/>/ai/agents endpoints"]
        ModelAccountService["Model Account Service<br/>/ai/accounts endpoints"]
        ChannelService["Chat Channel Service<br/>/ai/channels endpoints"]
        OllamaService["Ollama Service<br/>/ai/ollama endpoints"]
    end
    
    subgraph "Storage"
        AgentDB["agent.db<br/>SQLite database"]
        ConfigFiles["Configuration Files<br/>openclaw.json"]
    end
    
    subgraph "External Integrations"
        OpenAI["OpenAI API<br/>provider: OpenAI"]
        Ollama["Ollama Service<br/>Local model runtime"]
        Feishu["Feishu/Lark API<br/>Chat platform"]
    end
    
    AgentUI --> AgentService
    ModelUI --> ModelAccountService
    ChannelUI --> ChannelService
    
    AgentService --> AgentDB
    ModelAccountService --> AgentDB
    ChannelService --> AgentDB
    
    AgentService --> ConfigFiles
    ModelAccountService --> OpenAI
    ModelAccountService --> Ollama
    OllamaService --> Ollama
    ChannelService --> Feishu
    
    AgentService -.uses.-> ModelAccountService
```

**Sources:** [frontend/src/lang/modules/zh.ts:654-700](), [frontend/src/lang/modules/en.ts:654-700]()

---

## Model Account Configuration

Model accounts represent connections to AI model providers. Each account stores authentication credentials and configuration for accessing models from providers like OpenAI, Ollama, or other compatible services.

### Account Structure

| Field | Description | Example |
|-------|-------------|---------|
| `provider` | Model provider identifier | `OpenAI`, `Ollama`, custom providers |
| `apiKey` | API authentication key | Required for OpenAI and similar services |
| `baseUrl` | Base URL for API endpoint | `https://api.openai.com/v1` |
| `token` | Alternative authentication token | Used by some providers |
| `verified` | Account verification status | Boolean indicating successful connection test |

### Supported Providers

```mermaid
graph LR
    ModelAccount["Model Account"]
    
    ModelAccount --> OpenAI["OpenAI Provider<br/>apiKey + baseUrl"]
    ModelAccount --> Ollama["Ollama Provider<br/>Local container access"]
    ModelAccount --> Custom["Custom Provider<br/>Manual configuration"]
    
    OpenAI --> Models1["GPT-4<br/>GPT-3.5<br/>Other models"]
    Ollama --> Models2["llama2<br/>mistral<br/>codellama<br/>Custom models"]
    Custom --> Models3["Provider-specific<br/>models"]
```

### Model Account Workflow

1. **Create Account**: User provides provider type and credentials
2. **Verification**: System tests connection to provider API
3. **Model Selection**: User can manually specify model name or select from available models
4. **Agent Association**: Accounts are linked to one or more AI agents

**Sources:** [frontend/src/lang/modules/zh.ts:656-675](), [frontend/src/lang/modules/en.ts:659-677]()

---

## AI Agent Management

AI agents are intelligent entities that use model accounts to interact with users through chat platforms. Each agent has its own configuration stored in `openclaw.json`.

### Agent Components

```mermaid
graph TB
    Agent["AI Agent"]
    
    Agent --> ModelAccount["Model Account<br/>Authentication & Provider"]
    Agent --> Config["openclaw.json<br/>Agent configuration"]
    Agent --> Ports["Network Ports<br/>webuiPort, bridgePort"]
    Agent --> AppVersion["Application Version<br/>Container image tag"]
    
    Config --> SyncOperation["Sync Operation<br/>Updates all agents<br/>using same account"]
    
    ModelAccount --> Provider["Provider API<br/>OpenAI/Ollama/Custom"]
```

### Key Configuration Fields

| Field | Purpose | Notes |
|-------|---------|-------|
| `account` | Associated model account | Reference to model account ID |
| `appVersion` | Application version | Container image version for agent runtime |
| `webuiPort` | Web UI port | Port for agent web interface |
| `bridgePort` | Bridge port | Internal communication port |

### Agent Synchronization

The system provides a `syncAgents` operation that updates the `openclaw.json` configuration file for all agents associated with a specific model account. This ensures consistency when account credentials or settings change.

**Operation Flow:**
1. User updates model account credentials
2. System identifies all agents using that account
3. `openclaw.json` files are regenerated for affected agents
4. Agent containers may need restart to apply changes

**Sources:** [frontend/src/lang/modules/zh.ts:656-690](), [frontend/src/lang/modules/en.ts:659-690]()

---

## Ollama Integration

1Panel provides deep integration with Ollama for managing local AI models. Ollama runs as a containerized service and provides a model management interface.

### Model Management Operations

```mermaid
graph LR
    UI["Model Management UI"]
    
    UI --> Create["Create/Pull Model<br/>POST /ai/model/create"]
    UI --> List["List Models<br/>GET /ai/model/list"]
    UI --> Sync["Sync Models<br/>GET /ai/model/sync"]
    UI --> Delete["Delete Model<br/>DELETE /ai/model/:name"]
    
    Create --> Ollama["Ollama Container<br/>Model storage"]
    List --> Ollama
    Sync --> Ollama
    Delete --> Ollama
    
    Ollama --> ModelFiles["Model Files<br/>/ollama/models"]
```

### Container Connection

Models running in Ollama containers can be accessed by other containers in the same Docker network:

- **Container-to-container access**: Uses service name (e.g., `ollama:11434`)
- **External access**: Exposed port on host (e.g., `localhost:11434`)
- **1Panel integration**: Tracks pull logs and model metadata

### Model Discovery and Sync

The system maintains a catalog of installed Ollama models in `agent.db`. The sync operation:
1. Queries Ollama API for installed models
2. Compares with 1Panel's database records
3. Identifies orphaned records (models deleted outside 1Panel)
4. Prompts user to clean up stale entries

**Ollama Model Metadata:**
- Model name (e.g., `llama2:latest`)
- Pull logs and download progress
- Origin tracking (downloaded via 1Panel vs. external)

**Sources:** [frontend/src/lang/modules/zh.ts:691-700](), [frontend/src/lang/modules/en.ts:692-700]()

---

## Chat Channel Integration

AI agents can be connected to chat platforms to enable conversational interfaces. The primary supported platform is Feishu (also known as Lark).

### Feishu/Lark Configuration

```mermaid
graph TB
    Agent["AI Agent"]
    
    Agent --> Gateway["Agent Gateway<br/>Communication bridge"]
    Gateway --> FeishuAPI["Feishu/Lark API"]
    
    Gateway --> Config["Feishu Configuration"]
    
    Config --> BotName["botName<br/>Robot display name"]
    Config --> AppID["appId<br/>Application ID"]
    Config --> AppSecret["appSecret<br/>Application secret"]
    Config --> DMPolicy["dmPolicy<br/>Direct message policy"]
    
    Gateway --> PairingCode["Pairing Code<br/>Device/bot linking"]
```

### Configuration Fields

| Field | Required | Purpose |
|-------|----------|---------|
| `botName` | Yes | Display name for the bot in Feishu |
| `appId` | Yes | Feishu application ID from developer portal |
| `appSecret` | Yes | Authentication secret for Feishu API |
| `dmPolicy` | No | Policy for handling direct messages |
| `pairingCode` | Optional | Code for device/bot pairing approval |

### Channel Workflow

1. **Configure Feishu Bot**: Create bot in Feishu developer portal, obtain `appId` and `appSecret`
2. **Link to Agent**: Enter credentials in 1Panel channel configuration
3. **Save and Restart Gateway**: Gateway service restarts to establish connection
4. **Pairing Approval**: If pairing code is provided, approve the pairing to activate bot
5. **Chat Interface Active**: Bot becomes available in Feishu for user interactions

### Gateway Restart Requirement

Changes to chat channel configuration require restarting the agent gateway service to establish new connections. The UI provides a "Save and Restart Gateway" button that combines these operations.

**Sources:** [frontend/src/lang/modules/zh.ts:676-690](), [frontend/src/lang/modules/en.ts:676-690]()

---

## Configuration File Structure

### openclaw.json

The `openclaw.json` file stores agent configuration in JSON format. This file is generated and maintained by 1Panel but can be manually edited if needed.

**Location Pattern**: `/opt/1panel/apps/[agent-name]/data/openclaw.json` (or similar, depending on installation)

**Key Sections:**
```json
{
  "model": {
    "provider": "OpenAI",
    "apiKey": "sk-...",
    "baseUrl": "https://api.openai.com/v1",
    "model": "gpt-4"
  },
  "ports": {
    "webui": 8080,
    "bridge": 8081
  },
  "channels": {
    "feishu": {
      "enabled": true,
      "botName": "Assistant",
      "appId": "cli_...",
      "appSecret": "..."
    }
  }
}
```

### Synchronization Operations

When performing `syncAgents`, the system:
1. Reads current model account configuration from database
2. Identifies all agents using that account (query `agent.db`)
3. For each agent:
   - Generates updated `openclaw.json` with new credentials
   - Writes file to agent's data directory
   - Marks agent as requiring restart

**Sources:** [frontend/src/lang/modules/zh.ts:663-665]()

---

## Frontend UI Components

### Agent Management Views

The frontend provides dedicated views for managing AI infrastructure:

```mermaid
graph TB
    Menu["Menu: aiTools"]
    
    Menu --> AgentsTab["Agents Tab<br/>agents section"]
    Menu --> ModelsTab["Models Tab<br/>model section"]
    Menu --> ProxyTab["Proxy Tab<br/>proxy section"]
    Menu --> GPUTab["GPU Tab<br/>gpu section"]
    Menu --> MCPTab["MCP Tab<br/>mcp section"]
    
    AgentsTab --> CreateAgent["Create Agent Dialog<br/>createAgent"]
    AgentsTab --> CreateAccount["Create Model Account<br/>createModelAccount"]
    AgentsTab --> SyncAgents["Sync Agents Operation<br/>syncAgents"]
    AgentsTab --> ChannelConfig["Channel Configuration<br/>channelsTab"]
    
    ModelsTab --> PullModel["Pull Model Dialog<br/>create"]
    ModelsTab --> ModelList["Model List View"]
    ModelsTab --> SyncOllama["Sync Ollama Models<br/>ollama_sync"]
```

### Translation Keys

The UI uses i18n translation keys organized under `aiTools`:

- **Agent operations**: `aiTools.agents.createAgent`, `aiTools.agents.syncAgents`
- **Model account**: `aiTools.agents.createModelAccount`, `aiTools.agents.account`
- **Model management**: `aiTools.model.create`, `aiTools.model.ollama_sync`
- **Channel config**: `aiTools.agents.channelsTab`, `aiTools.agents.feishu`

**Sources:** [frontend/src/lang/modules/zh.ts:654-800](), [frontend/src/lang/modules/en.ts:654-800]()

---

## API Integration Patterns

### Model Account Verification

When creating or updating a model account, the system performs verification:

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant AgentAPI as Agent API
    participant Provider as AI Provider

    User->>UI: Enter account credentials
    UI->>AgentAPI: POST /ai/accounts/verify
    AgentAPI->>Provider: Test connection<br/>(list models or ping)
    Provider-->>AgentAPI: Response (success/error)
    AgentAPI-->>UI: Verification result
    UI->>UI: Update "verified" status
    UI-->>User: Show verification result
```

### Agent Synchronization

The sync operation ensures all agents using a model account have up-to-date configuration:

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant AgentAPI as Agent API
    participant DB as agent.db
    participant FS as File System

    User->>UI: Click "Sync Agents"
    UI->>AgentAPI: POST /ai/accounts/:id/sync
    AgentAPI->>DB: Query agents using account
    
    loop For each agent
        AgentAPI->>FS: Read openclaw.json
        AgentAPI->>AgentAPI: Update credentials section
        AgentAPI->>FS: Write openclaw.json
        AgentAPI->>DB: Mark agent as needs restart
    end
    
    AgentAPI-->>UI: Sync complete (count updated)
    UI-->>User: Show success message<br/>"syncAgentsHelper"
```

### Ollama Model Pull

Pulling an Ollama model is an asynchronous operation with progress tracking:

```mermaid
sequenceDiagram
    participant User
    participant UI
    participant AgentAPI as Agent API
    participant Ollama as Ollama Container
    participant DB as agent.db

    User->>UI: Enter model name (e.g., "llama2")
    UI->>AgentAPI: POST /ai/model/pull
    AgentAPI->>DB: Create task record
    AgentAPI-->>UI: Return taskID
    
    UI->>AgentAPI: Stream GET /tasks/:taskID/logs
    
    par Async Pull Operation
        AgentAPI->>Ollama: Pull model via API
        loop Download progress
            Ollama-->>AgentAPI: Progress events
            AgentAPI->>DB: Log progress
        end
        Ollama-->>AgentAPI: Pull complete
        AgentAPI->>DB: Update model record
    end
    
    AgentAPI-->>UI: Stream progress logs
    UI-->>User: Show real-time progress
```

**Sources:** Based on patterns from [frontend/src/lang/modules/zh.ts:691-700]() and async task patterns from Diagram 3 in high-level architecture

---

## Usage Examples

### Creating an AI Agent

1. **Create Model Account**:
   - Navigate to AI → Agents
   - Click "Create Model Account" (`createModelAccount`)
   - Select provider: OpenAI, Ollama, or custom
   - Enter credentials (API key, base URL)
   - System verifies connection

2. **Create Agent**:
   - Click "Create Agent" (`createAgent`)
   - Select model account from dropdown
   - Configure ports (WebUI port, Bridge port)
   - Set application version
   - System generates `openclaw.json`

3. **Configure Chat Channel** (Optional):
   - Switch to "Chat Channels" tab (`channelsTab`)
   - Select Feishu/Lark
   - Enter bot name, app ID, app secret
   - Click "Save and Restart Gateway" (`saveAndRestartGateway`)
   - Approve pairing if required

### Managing Ollama Models

1. **Pull New Model**:
   - Navigate to AI → Models
   - Click "Add Model" (`create`)
   - Enter model name (e.g., `mistral:latest`)
   - Monitor pull progress in task logs
   - Model becomes available for agent use

2. **Sync Models**:
   - Click sync button to reconcile database with Ollama
   - Review models not installed via 1Panel
   - Clean up orphaned database entries if prompted

3. **Container Access**:
   - Use container connection address for intra-container access
   - Displayed as `ollama:11434` or similar service name
   - No external network exposure required

**Sources:** [frontend/src/lang/modules/zh.ts:654-700](), [frontend/src/lang/modules/en.ts:654-700]()

---

## Error Handling and Validation

### Account Validation

The system validates model account configuration before allowing agent creation:

- **Required fields**: Provider must have all required credentials (`feishuRequired` check)
- **Connection test**: Verification must succeed before account is marked as `verified`
- **Manual model input**: Allows specifying models not in provider's default list

### Common Error Scenarios

| Scenario | Error Message Key | Resolution |
|----------|------------------|------------|
| Missing Feishu credentials | `feishuRequired` | Fill in botName, appId, and appSecret |
| Invalid pairing code | `pairingCodeRequired` | Enter valid code from Feishu |
| Ollama model not found | Model deleted externally | Use sync operation to clean up records |
| Gateway restart needed | Config changes pending | Click "Save and Restart Gateway" |

### Synchronization Conflicts

When syncing agents, the system handles:
- **Account deleted**: Agents become orphaned, user must reassign or delete
- **Model unavailable**: Warns if configured model no longer exists in provider
- **File permission issues**: Logs error if cannot write `openclaw.json`

**Sources:** [frontend/src/lang/modules/zh.ts:685-690](), [frontend/src/lang/modules/en.ts:685-690]()

---

# Page: GPU Monitoring and XPU Support

# GPU Monitoring and XPU Support

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/app/api/v2/dashboard.go](agent/app/api/v2/dashboard.go)
- [agent/app/dto/dashboard.go](agent/app/dto/dashboard.go)
- [agent/app/model/app_launcher.go](agent/app/model/app_launcher.go)
- [agent/app/repo/app_launcher.go](agent/app/repo/app_launcher.go)
- [agent/app/service/dashboard.go](agent/app/service/dashboard.go)
- [agent/router/ro_dashboard.go](agent/router/ro_dashboard.go)
- [frontend/src/api/interface/dashboard.ts](frontend/src/api/interface/dashboard.ts)
- [frontend/src/api/modules/dashboard.ts](frontend/src/api/modules/dashboard.ts)
- [frontend/src/lang/modules/en.ts](frontend/src/lang/modules/en.ts)
- [frontend/src/lang/modules/es-es.ts](frontend/src/lang/modules/es-es.ts)
- [frontend/src/lang/modules/ja.ts](frontend/src/lang/modules/ja.ts)
- [frontend/src/lang/modules/ko.ts](frontend/src/lang/modules/ko.ts)
- [frontend/src/lang/modules/ms.ts](frontend/src/lang/modules/ms.ts)
- [frontend/src/lang/modules/pt-br.ts](frontend/src/lang/modules/pt-br.ts)
- [frontend/src/lang/modules/ru.ts](frontend/src/lang/modules/ru.ts)
- [frontend/src/lang/modules/tr.ts](frontend/src/lang/modules/tr.ts)
- [frontend/src/lang/modules/zh-Hant.ts](frontend/src/lang/modules/zh-Hant.ts)
- [frontend/src/lang/modules/zh.ts](frontend/src/lang/modules/zh.ts)
- [frontend/src/views/home/app/index.vue](frontend/src/views/home/app/index.vue)
- [frontend/src/views/home/index.vue](frontend/src/views/home/index.vue)
- [frontend/src/views/home/status/index.vue](frontend/src/views/home/status/index.vue)

</details>



## Purpose and Scope

This page documents 1Panel's GPU and XPU (Intel accelerator) monitoring capabilities. The system provides real-time and historical monitoring of GPU hardware metrics, process tracking, and performance statistics through integration with `nvidia-smi` and `xpu-smi` command-line tools. This functionality enables users to monitor AI/ML workloads running on GPU-accelerated hardware.

For information about AI agent management and model operations, see [AI Agents and Model Management](#9.1). For MCP protocol server management, see [MCP Server Management](#9.3).

## System Architecture

The GPU monitoring subsystem integrates with hardware drivers through command-line utilities and exposes metrics through a dashboard interface with both real-time and historical views.

```mermaid
graph TB
    subgraph "Hardware Layer"
        NVGPU["NVIDIA GPU Hardware"]
        XPUGPU["Intel XPU Hardware"]
    end
    
    subgraph "Driver Layer"
        NVDriver["nvidia-smi CLI"]
        XPUDriver["xpu-smi CLI"]
    end
    
    subgraph "Backend Services"
        GPUUtil["agent/utils/ai_tools/gpu"]
        XPUUtil["agent/utils/ai_tools/xpu"]
        DashboardSvc["DashboardService"]
        HistoryMgr["GPU History Manager"]
    end
    
    subgraph "API Layer"
        DashboardAPI["Dashboard API /dashboard/*"]
    end
    
    subgraph "Frontend"
        GPUView["GPU Monitoring View"]
        Charts["Historical Charts"]
        ProcessTable["Process Table"]
    end
    
    subgraph "Data Storage"
        HistoryDB["Historical Metrics<br/>Time-series data"]
    end
    
    NVGPU --> NVDriver
    XPUGPU --> XPUDriver
    
    NVDriver --> GPUUtil
    XPUDriver --> XPUUtil
    
    GPUUtil --> DashboardSvc
    XPUUtil --> DashboardSvc
    
    DashboardSvc --> HistoryMgr
    HistoryMgr --> HistoryDB
    
    DashboardSvc --> DashboardAPI
    HistoryDB --> DashboardAPI
    
    DashboardAPI --> GPUView
    GPUView --> Charts
    GPUView --> ProcessTable
```

**Diagram: GPU Monitoring System Architecture**

Sources: [agent/app/service/dashboard.go:21-22](), [frontend/src/lang/modules/zh.ts:711-765]()

## Driver Integration

### Detection and Command Execution

The system detects GPU availability by attempting to execute `nvidia-smi` or `xpu-smi` commands. If neither command is available, the frontend displays a helper message indicating no GPU hardware or drivers are detected.

```mermaid
graph LR
    subgraph "Detection Flow"
        Start["System Initialization"]
        CheckNV["Execute nvidia-smi"]
        CheckXPU["Execute xpu-smi"]
        NVAvail["NVIDIA GPU Available"]
        XPUAvail["XPU Available"]
        NoGPU["No GPU Detected<br/>Show gpuHelper message"]
    end
    
    Start --> CheckNV
    CheckNV -->|Success| NVAvail
    CheckNV -->|Fail| CheckXPU
    CheckXPU -->|Success| XPUAvail
    CheckXPU -->|Fail| NoGPU
    
    NVAvail --> Monitor["Start Monitoring"]
    XPUAvail --> Monitor
```

**Diagram: GPU Detection Flow**

The detection message is defined in the language files as:
- Chinese: "当前系统未检测到 NVIDIA-SMI 或者 XPU-SMI 指令，请检查后重试！"
- English: "The current system has not detected NVIDIA-SMI or XPU-SMI instructions, please check and try again!"

Sources: [frontend/src/lang/modules/zh.ts:713](), [frontend/src/lang/modules/en.ts:629]()

## Monitored Metrics

### Base GPU Information

The system tracks fundamental GPU hardware properties:

| Metric | Translation Key | Description |
|--------|-----------------|-------------|
| Driver Version | `driverVersion` | GPU driver version |
| CUDA Version | `cudaVersion` | CUDA toolkit version (NVIDIA only) |
| Bus ID | `busID` | PCIe bus identifier |
| Persistence Mode | `persistenceMode` | Driver persistence state |
| Display Active | `displayActive` | Display initialization status |
| ECC | `ecc` | Error Checking and Correction status |
| Compute Mode | `computeMode` | GPU compute mode setting |

Sources: [frontend/src/lang/modules/zh.ts:737-759]()

### Real-Time Performance Metrics

```mermaid
graph TB
    subgraph "Performance Metrics"
        GPU["GPU Metrics"]
        GPU --> Util["gpuUtil: GPU使用率<br/>GPU Utilization %"]
        GPU --> Temp["temperature: 温度<br/>Temperature °C"]
        GPU --> PState["performanceState: 性能状态<br/>P0-P12"]
        GPU --> Power["powerUsage: 功耗<br/>Power Consumption W"]
        GPU --> Mem["memoryUsage: 显存使用率<br/>Memory Usage %"]
        GPU --> Fan["fanSpeed: 风扇转速<br/>Fan Speed %"]
    end
    
    subgraph "Memory Details"
        Memory["memory: 显存"]
        Memory --> MemUsed["memoryUsed: 显存使用<br/>Used Memory"]
        Memory --> MemTotal["memoryTotal: 显存总计<br/>Total Memory"]
        Memory --> MemPercent["percent: 使用率<br/>Usage %"]
    end
    
    subgraph "Power Details"
        PowerInfo["power: 功率"]
        PowerInfo --> PowerCurr["powerCurrent: 当前功率<br/>Current Power W"]
        PowerInfo --> PowerLim["powerLimit: 功率上限<br/>Power Limit W"]
    end
```

**Diagram: GPU Performance Metrics Structure**

Temperature monitoring includes a helper message: "GPU 温度过高会导致 GPU 频率下降" (High GPU temperature will cause GPU frequency to decrease).

Sources: [frontend/src/lang/modules/zh.ts:722-735]()

### Compute Modes

The system displays four compute mode configurations:

| Mode | Translation Key | Description |
|------|-----------------|-------------|
| Default | `default` | Multiple processes can execute concurrently |
| Exclusive Process | `exclusiveProcess` | Only one CUDA context, shared by multiple threads |
| Exclusive Thread | `exclusiveThread` | Only one thread can use GPU in CUDA context |
| Prohibited | `prohibited` | No processes allowed to execute simultaneously |

Each mode includes a helper key (`defaultHelper`, `exclusiveProcessHelper`, etc.) explaining the behavior.

Sources: [frontend/src/lang/modules/zh.ts:751-759]()

## Process Monitoring

### Process Information Structure

The GPU monitoring system tracks GPU processes with detailed resource usage:

```mermaid
graph LR
    subgraph "Process Tracking"
        ProcTable["Process Table"]
        ProcTable --> ProcCount["processCount: 进程数<br/>Process Count"]
        ProcTable --> ProcList["process: 进程信息<br/>Process List"]
    end
    
    subgraph "Per-Process Details"
        Process["Individual Process"]
        Process --> Type["type: 类型<br/>G/C/CG"]
        Process --> Name["processName: 进程名称<br/>Process Name"]
        Process --> Mem["processMemoryUsage: 显存使用<br/>Memory Usage"]
        Process --> Shr["shr: 共享显存<br/>Shared Memory"]
    end
    
    ProcList --> Process
```

**Diagram: Process Tracking Data Structure**

### Process Types

GPU processes are categorized by their usage pattern:

- **G (Graphics)**: Graphics rendering processes (`typeG`)
- **C (Compute)**: Compute-only processes (`typeC`)
- **CG (Compute+Graphics)**: Combined compute and graphics processes (`typeCG`)

Sources: [frontend/src/lang/modules/zh.ts:714-721]()

## Historical Monitoring

The system maintains historical GPU metrics for trend analysis and capacity planning.

### Data Collection Flow

```mermaid
sequenceDiagram
    participant Timer as "Polling Timer"
    participant DashSvc as "DashboardService"
    participant GPUUtil as "GPU Utils<br/>nvidia-smi/xpu-smi"
    participant HistMgr as "History Manager"
    participant DB as "HistoryDB"
    participant Frontend as "Frontend Charts"
    
    Timer->>DashSvc: Periodic Poll
    DashSvc->>GPUUtil: Execute GPU Query
    GPUUtil->>GPUUtil: Parse Command Output
    GPUUtil-->>DashSvc: Current Metrics
    
    DashSvc->>HistMgr: Store Metrics with Timestamp
    HistMgr->>DB: Write Time-series Data
    
    Frontend->>DashSvc: GET /dashboard/current/*
    DashSvc-->>Frontend: Current Metrics
    
    Frontend->>DashSvc: GET Historical Data
    DB-->>HistMgr: Query Time Range
    HistMgr-->>Frontend: Historical Metrics Array
```

**Diagram: Historical Data Collection and Retrieval**

The historical view provides access to past GPU performance data through the `history` tab key in the language files.

Sources: [agent/app/service/dashboard.go:1-56](), [frontend/src/lang/modules/zh.ts:762-763]()

## API Endpoints

### Dashboard Integration

GPU metrics are exposed through the dashboard API endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/dashboard/base/os` | GET | Load OS information including GPU detection |
| `/dashboard/current/:ioOption/:netOption` | GET | Load current system metrics including GPU |
| `/dashboard/base/:ioOption/:netOption` | GET | Load base dashboard information |

Sources: [agent/router/ro_dashboard.go:14-22](), [agent/app/api/v2/dashboard.go:18-25]()

### Data Structures

The dashboard service utilizes dedicated GPU utility packages:

```go
import (
    "github.com/1Panel-dev/1Panel/agent/utils/ai_tools/gpu"
    "github.com/1Panel-dev/1Panel/agent/utils/ai_tools/xpu"
)
```

These utilities parse command-line output from `nvidia-smi` and `xpu-smi` to extract structured metrics.

Sources: [agent/app/service/dashboard.go:21-22]()

## Frontend Components

### GPU Monitoring View Structure

The frontend organizes GPU monitoring into tabbed sections:

```mermaid
graph TB
    subgraph "GPU Monitoring UI"
        MainView["GPU Monitoring View<br/>menu.aiTools → aiTools.gpu.gpu"]
        
        MainView --> TabCurrent["current: 实时监控<br/>Real-time Monitoring"]
        MainView --> TabHistory["history: 历史记录<br/>Historical Records"]
        
        TabCurrent --> BaseInfo["base: 基础信息<br/>Base Information"]
        TabCurrent --> Metrics["Performance Metrics"]
        TabCurrent --> ProcTable["Process Table"]
        
        TabHistory --> Charts["Time-series Charts"]
    end
    
    subgraph "Base Information Display"
        BaseInfo --> Driver["Driver/CUDA Version"]
        BaseInfo --> BusID["Bus ID"]
        BaseInfo --> Persist["Persistence Mode"]
        BaseInfo --> Display["Display Active"]
        BaseInfo --> ECC["ECC Status"]
        BaseInfo --> Compute["Compute Mode"]
    end
    
    subgraph "Metrics Display"
        Metrics --> GPU["GPU Utilization"]
        Metrics --> Temp["Temperature"]
        Metrics --> Memory["Memory Usage"]
        Metrics --> Power["Power Consumption"]
        Metrics --> Fan["Fan Speed"]
    end
```

**Diagram: Frontend Component Structure**

Sources: [frontend/src/lang/modules/zh.ts:711-765]()

### Localization Keys

The GPU monitoring interface is fully internationalized with translation keys under the `aiTools.gpu` namespace:

- **Main labels**: `gpu`, `gpuHelper`, `process`, `processCount`, `type`, `processName`
- **Metric labels**: `temperatureHelper`, `gpuUtil`, `temperature`, `performanceState`, `powerUsage`, `memoryUsage`, `fanSpeed`
- **Memory details**: `power`, `powerCurrent`, `powerLimit`, `memory`, `memoryUsed`, `memoryTotal`, `percent`
- **Base info**: `base`, `driverVersion`, `cudaVersion`, `busID`, `persistenceMode`, etc.
- **Status indicators**: `enabled`, `disabled`, `notSupport`
- **Views**: `current`, `history`

Sources: [frontend/src/lang/modules/zh.ts:711-765](), [frontend/src/lang/modules/en.ts:629-665]()

## Special Features

### Performance State (P-States)

NVIDIA GPUs report performance states from P0 (maximum performance) to P12 (minimum performance). The system displays this with a helper message explaining the scale.

**Performance State Helper**: "从 P0 (最大性能) 到 P12 (最小性能)" / "From P0 (maximum performance) to P12 (minimum performance)"

Sources: [frontend/src/lang/modules/zh.ts:741]()

### Persistence Mode

Persistence mode affects GPU responsiveness and power consumption:

**Persistence Mode Helper**: "持续模式能更加快速地响应任务，但相应待机功耗也会增加" / "Persistence mode enables faster task response, but increases idle power consumption accordingly"

Sources: [frontend/src/lang/modules/zh.ts:746]()

### MIG Mode Detection

For supported NVIDIA GPUs, the system detects Multi-Instance GPU (MIG) mode:

**MIG Mode Helper**: "用于创建 MIG 实例，在用户层实现 GPU 的物理隔离" / "Used to create MIG instances, implementing physical isolation of GPU at the user layer"

When MIG is not supported, the system displays `migModeNA: '不支持'` (Not Supported).

Sources: [frontend/src/lang/modules/zh.ts:760-761]()

### Temperature Warnings

The system provides contextual warnings for high GPU temperatures with the helper text explaining that excessive temperature causes GPU frequency throttling.

Sources: [frontend/src/lang/modules/zh.ts:722]()

## Integration with Dashboard

GPU metrics integrate into the main dashboard system through the `DashboardService`:

```mermaid
graph TB
    subgraph "Dashboard Service Layer"
        DashSvc["DashboardService<br/>agent/app/service/dashboard.go"]
        
        DashSvc --> LoadOS["LoadOsInfo()"]
        DashSvc --> LoadBase["LoadBaseInfo()"]
        DashSvc --> LoadCurrent["LoadCurrentInfo()"]
        DashSvc --> LoadNode["LoadCurrentInfoForNode()"]
    end
    
    subgraph "GPU Integration Points"
        LoadCurrent --> GPUMetrics["Include GPU Metrics<br/>if available"]
        LoadBase --> GPUDetect["GPU Detection Status"]
    end
    
    subgraph "Data Return Types"
        LoadOS --> OSInfo["dto.OsInfo"]
        LoadBase --> BaseInfo["dto.DashboardBase"]
        LoadCurrent --> CurrentInfo["dto.DashboardCurrent"]
        LoadNode --> NodeCurrent["dto.NodeCurrent"]
    end
```

**Diagram: Dashboard Service Integration**

The dashboard service coordinates GPU monitoring with other system metrics (CPU, memory, network, disk) to provide a unified monitoring interface.

Sources: [agent/app/service/dashboard.go:35-52](), [agent/app/dto/dashboard.go:5-25]()

## Error Handling

When GPU hardware or drivers are not detected, the system gracefully handles the absence:

1. **Detection Phase**: Attempts to execute `nvidia-smi` or `xpu-smi`
2. **Failure Response**: Returns empty GPU data structures
3. **Frontend Display**: Shows helper message via `gpuHelper` translation key
4. **User Guidance**: Prompts user to verify GPU hardware and driver installation

This ensures the system remains functional even without GPU hardware, making GPU monitoring an optional enhancement rather than a required component.

Sources: [frontend/src/lang/modules/zh.ts:713](), [frontend/src/lang/modules/en.ts:629]()

---

# Page: MCP Server Management

# MCP Server Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [frontend/src/lang/modules/en.ts](frontend/src/lang/modules/en.ts)
- [frontend/src/lang/modules/es-es.ts](frontend/src/lang/modules/es-es.ts)
- [frontend/src/lang/modules/ja.ts](frontend/src/lang/modules/ja.ts)
- [frontend/src/lang/modules/ko.ts](frontend/src/lang/modules/ko.ts)
- [frontend/src/lang/modules/ms.ts](frontend/src/lang/modules/ms.ts)
- [frontend/src/lang/modules/pt-br.ts](frontend/src/lang/modules/pt-br.ts)
- [frontend/src/lang/modules/ru.ts](frontend/src/lang/modules/ru.ts)
- [frontend/src/lang/modules/tr.ts](frontend/src/lang/modules/tr.ts)
- [frontend/src/lang/modules/zh-Hant.ts](frontend/src/lang/modules/zh-Hant.ts)
- [frontend/src/lang/modules/zh.ts](frontend/src/lang/modules/zh.ts)

</details>



## Purpose and Scope

This document covers the Model Context Protocol (MCP) server management system in 1Panel, including server creation, transport mechanism configuration (stdio/SSE/streamableHttp), environment variable management, and integration with the website and AI infrastructure. For AI agent configuration that consumes MCP servers, see [AI Agents and Model Management](#9.1). For general AI infrastructure overview, see [AI and ML Infrastructure](#9).

---

## MCP Protocol Overview

The Model Context Protocol (MCP) is a standardized protocol for connecting AI models and agents to external tools and data sources. 1Panel implements MCP server management to provide:

- **Standardized Tool Integration**: Expose server-side tools and capabilities to AI agents
- **Multiple Transport Options**: Support for stdio, Server-Sent Events (SSE), and HTTP streaming
- **Environment Isolation**: Per-server environment variable configuration
- **Secure Access Control**: Integration with website binding and port management

MCP servers in 1Panel bridge AI agents (like Claude Desktop, Cline, or custom implementations) with system resources, databases, file systems, and external APIs.

**Key Transport Mechanisms:**
- **stdio**: Direct process communication via standard input/output (suitable for npx and binary executables)
- **SSE**: Server-Sent Events over HTTP for streaming responses
- **streamableHttp**: HTTP-based streaming with custom endpoints

Sources: [frontend/src/lang/modules/zh.ts:766-791](), [frontend/src/lang/modules/en.ts:766-791]()

---

## System Architecture

```mermaid
graph TB
    subgraph "AI Clients"
        Claude["Claude Desktop"]
        Cline["Cline / VS Code"]
        Custom["Custom AI Clients"]
    end
    
    subgraph "1Panel MCP Management"
        MCPConfig["MCP Server Config<br/>name, command, transport"]
        EnvVars["Environment Variables<br/>key-value pairs"]
        Transport["Transport Handler"]
        WebsiteBind["Website Binding<br/>Nginx proxy"]
    end
    
    subgraph "MCP Server Processes"
        StdioServer["stdio Server<br/>npx/binary process"]
        SSEServer["SSE Server<br/>HTTP endpoint"]
        HttpServer["HTTP Server<br/>streaming endpoint"]
    end
    
    subgraph "Backend Resources"
        FileSystem["File System"]
        Database["Databases"]
        Docker["Docker API"]
        SystemTools["System Tools"]
    end
    
    Claude --> Transport
    Cline --> Transport
    Custom --> Transport
    
    MCPConfig --> Transport
    EnvVars --> StdioServer
    EnvVars --> SSEServer
    EnvVars --> HttpServer
    
    Transport --> StdioServer
    Transport --> SSEServer
    Transport --> HttpServer
    
    WebsiteBind --> SSEServer
    WebsiteBind --> HttpServer
    
    StdioServer --> FileSystem
    StdioServer --> Database
    SSEServer --> Docker
    HttpServer --> SystemTools
```

**Architecture Components:**

| Component | Responsibility | Transport Support |
|-----------|---------------|-------------------|
| `MCPConfig` | Server metadata, command, transport type | All |
| `EnvVars` | Environment variable injection | All |
| `Transport Handler` | Route requests to appropriate transport | All |
| `WebsiteBind` | Nginx proxy for HTTP-based transports | SSE, HTTP |
| `StdioServer` | Process-based communication | stdio |
| `SSEServer` | Event stream over HTTP | SSE |
| `HttpServer` | HTTP request/response streaming | HTTP |

Sources: [frontend/src/lang/modules/zh.ts:766-791]()

---

## Transport Mechanisms

### stdio Transport

The stdio transport launches MCP servers as child processes and communicates via standard input/output streams. This is suitable for command-line tools and npx-based servers.

**Configuration:**
- **Command**: Executable command (e.g., `npx @modelcontextprotocol/server-filesystem`, `/usr/local/bin/mcp-tool`)
- **Environment Variables**: Injected into process environment
- **Process Management**: 1Panel manages lifecycle (start/stop/restart)

**Use Cases:**
- Local tool integration
- File system access servers
- Database query tools
- Custom binary executables

**Supported Commands:**
- `npx` packages (e.g., `npx @modelcontextprotocol/server-github`)
- `uvx` Python packages (e.g., `uvx mcp-server-git`)
- Binary executables (e.g., `/opt/mcp/custom-tool`)

Sources: [frontend/src/lang/modules/zh.ts:782-790](), [frontend/src/lang/modules/en.ts:782-790]()

### SSE (Server-Sent Events) Transport

SSE transport exposes MCP servers via HTTP endpoints that stream events to clients using the Server-Sent Events protocol.

**Configuration:**
- **Base URL**: External access path (e.g., `http://192.168.1.1:8000`)
- **SSE Path**: Endpoint path (e.g., `/sse`) - must be unique across servers
- **Website Binding**: Optional Nginx proxy for HTTPS and access control

**HTTP Endpoint:**
```
GET {baseUrl}{ssePath}
Accept: text/event-stream
```

**Access Control:**
- Port external access can be disabled after website binding
- IP whitelist via website configuration
- HTTPS support through bound website

**Use Cases:**
- Remote AI client connections
- Browser-based AI tools
- Multi-client concurrent access

Sources: [frontend/src/lang/modules/zh.ts:770-774](), [frontend/src/lang/modules/en.ts:770-774]()

### streamableHttp Transport

The streamableHttp transport provides HTTP-based streaming with custom endpoint paths, allowing bidirectional communication over HTTP.

**Configuration:**
- **Base URL**: External access path
- **HTTP Path**: Endpoint path (e.g., `/mcp`) - must be unique across servers
- **Website Binding**: Required for production deployments

**HTTP Endpoint:**
```
POST {baseUrl}{streamableHttpPath}
Content-Type: application/json
```

**Features:**
- Request/response streaming
- JSON-based message protocol
- Custom headers and authentication
- Chunked transfer encoding support

**Use Cases:**
- RESTful tool integrations
- API proxy servers
- Custom protocol implementations

Sources: [frontend/src/lang/modules/zh.ts:787-788](), [frontend/src/lang/modules/en.ts:787-788]()

---

## Server Creation and Configuration

### Transport Type Comparison

| Feature | stdio | SSE | streamableHttp |
|---------|-------|-----|----------------|
| **Client Access** | Local only | HTTP/HTTPS | HTTP/HTTPS |
| **Authentication** | Process-based | Header/Cookie | Header/Cookie |
| **Streaming** | Bidirectional | Server-to-client | Bidirectional |
| **Process Model** | Child process | HTTP server | HTTP server |
| **Website Binding** | No | Yes | Yes |
| **Port Management** | N/A | External/internal | External/internal |
| **Multiple Clients** | No | Yes | Yes |

### Configuration Fields

**Common Fields:**
- **Name**: Server identifier (unique, alphanumeric with `-_`)
- **Command**: Startup command with arguments
- **Environment Variables**: Array of `{key, value}` pairs

**stdio-specific:**
- Process working directory
- Standard error handling

**SSE/HTTP-specific:**
- **Base URL**: Default access address (e.g., `192.168.1.1` or `example.com`)
- **Path**: Unique endpoint path (validated for collisions)
- **Bound Website**: Optional website for Nginx proxy

Sources: [frontend/src/lang/modules/zh.ts:768-791](), [frontend/src/lang/modules/en.ts:768-791]()

---

## Environment Variable Management

Environment variables provide configuration data to MCP servers without hardcoding values in commands.

```mermaid
graph LR
    UI["UI Input<br/>key-value pairs"]
    Storage["MCP Config Storage"]
    Process["Server Process"]
    Runtime["Process Environment"]
    
    UI --> Storage
    Storage --> Process
    Process --> Runtime
    
    Runtime --> FileServer["File Server<br/>PATH, HOME"]
    Runtime --> APIServer["API Server<br/>API_KEY, BASE_URL"]
    Runtime --> DBServer["DB Server<br/>DB_HOST, DB_USER"]
```

**Common Environment Variables:**

| Variable | Purpose | Example |
|----------|---------|---------|
| `API_KEY` | External API authentication | `sk-proj-abc123...` |
| `BASE_URL` | Service endpoint | `https://api.example.com` |
| `DATABASE_URL` | Database connection | `postgres://user:pass@host/db` |
| `PATH` | Executable search path | `/usr/local/bin:/usr/bin` |
| `HOME` | User home directory | `/home/user` |
| `ALLOWED_DIRS` | File access restrictions | `/data,/uploads` |

**Variable Format:**
- **Key**: Uppercase with underscores (e.g., `API_KEY`)
- **Value**: String, may contain special characters
- **Interpolation**: Server-side only, no 1Panel variable substitution

**Security Considerations:**
- Sensitive values (API keys, passwords) stored in plaintext
- Visible in process environment (`/proc/<pid>/environ`)
- Not encrypted at rest
- Consider using external secret managers for production

Sources: [frontend/src/lang/modules/zh.ts:774-777](), [frontend/src/lang/modules/en.ts:774-777]()

---

## Website Binding and Access Control

Website binding integrates MCP servers with 1Panel's website management system, providing:
- **HTTPS Termination**: Nginx handles SSL/TLS
- **Access Control**: IP whitelisting, authentication
- **Port Management**: Disable external port access
- **Path Routing**: Reverse proxy to MCP endpoints

```mermaid
graph TB
    Client["AI Client<br/>external IP"]
    Nginx["Nginx<br/>bound website"]
    MCPServer["MCP Server<br/>internal port"]
    
    Client -->|"HTTPS://{domain}{mcpPath}"| Nginx
    Nginx -->|"HTTP://127.0.0.1:{port}{mcpPath}"| MCPServer
    
    Nginx -.->|"IP Whitelist"| CheckIP["IP Check"]
    Nginx -.->|"SSL Certificate"| SSL["HTTPS"]
    Nginx -.->|"Proxy Config"| ProxyHeaders["Add Headers"]
```

**Binding Process:**

1. **Create Website**: Standard website creation (see [Website Management System](#7))
2. **Bind to MCP Server**: Modify server configuration
3. **Update Access Addresses**: All MCP servers update their `externalUrl`
4. **Close External Ports**: Disable direct port access

**Configuration Changes After Binding:**
- **External URL**: Changes from `http://IP:PORT/path` to `https://domain.com/path`
- **Port Access**: External port closed, only localhost access
- **Multiple Servers**: All servers update to use bound domain

**Access Control Options:**
- IP whitelist (via website firewall configuration)
- HTTP Basic Authentication (via website auth settings)
- SSL client certificates (via website SSL configuration)

Sources: [frontend/src/lang/modules/zh.ts:779-786](), [frontend/src/lang/modules/en.ts:779-786]()

---

## Import/Export Configuration

MCP servers can be configured via JSON import, compatible with standard MCP configuration formats.

### Import Format

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/data"],
      "env": {
        "ALLOWED_DIRS": "/data,/uploads"
      },
      "transport": "stdio"
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_abc123..."
      },
      "transport": "stdio"
    },
    "api-server": {
      "url": "http://localhost:8080/sse",
      "transport": "sse"
    }
  }
}
```

**Import Process:**
1. Parse `mcpServers` object
2. Validate structure (transport type, required fields)
3. Create server entries in 1Panel
4. Combine `command` and `args` into single command string
5. Convert `env` object to key-value array

**Export Format:**
- 1Panel-specific format includes additional metadata
- `externalUrl` for SSE/HTTP transports
- `boundWebsite` if website binding configured
- Server status and creation timestamps

**Validation Rules:**
- `mcpServers` must be an object
- Each server requires `command` or `url`
- `transport` must be "stdio", "sse", or "streamableHttp"
- SSE/HTTP servers require `url` or `baseUrl` + path

**Error Handling:**
- Invalid structure: `mcpServers structure is incorrect`
- Missing required fields: Skip server with warning
- Duplicate names: Append suffix or skip

Sources: [frontend/src/lang/modules/zh.ts:783-784](), [frontend/src/lang/modules/en.ts:783-784]()

---

## Integration Patterns

### AI Agent Integration

```mermaid
graph TB
    subgraph "AI Agent Configuration"
        AgentConfig["Agent Config<br/>openclaw.json"]
        ModelAccount["Model Account<br/>API keys"]
    end
    
    subgraph "MCP Servers"
        MCP1["File Server<br/>stdio"]
        MCP2["GitHub Server<br/>stdio"]
        MCP3["API Server<br/>SSE"]
    end
    
    subgraph "AI Gateway"
        Gateway["OpenClaw Gateway"]
        Bridge["MCP Bridge"]
    end
    
    AgentConfig --> Gateway
    ModelAccount --> Gateway
    Gateway --> Bridge
    
    Bridge --> MCP1
    Bridge --> MCP2
    Bridge --> MCP3
    
    MCP1 -.->|"file operations"| FS["File System"]
    MCP2 -.->|"GitHub API"| GitHub["GitHub"]
    MCP3 -.->|"custom API"| API["External API"]
```

**Integration Steps:**

1. **Create MCP Server**: Configure transport and environment
2. **Bind Website** (optional): For remote access
3. **Configure AI Agent**: Reference MCP server in agent configuration
4. **Update Agent Config**: Sync agent with new MCP servers (see [AI Agents and Model Management](#9.1))

**Agent Configuration Example:**
```json
{
  "mcpServers": {
    "1panel-files": {
      "url": "https://panel.example.com/mcp-files",
      "transport": "sse"
    }
  }
}
```

Sources: [frontend/src/lang/modules/zh.ts:663-665](), [frontend/src/lang/modules/en.ts:663-665]()

### Multi-Server Orchestration

```mermaid
graph LR
    Agent["AI Agent"]
    
    Agent --> Tools["Tool Selection"]
    
    Tools --> File["File Server<br/>read/write files"]
    Tools --> DB["Database Server<br/>query data"]
    Tools --> Search["Search Server<br/>web search"]
    Tools --> Code["Code Server<br/>execute code"]
    
    File -.-> FileSystem["File System"]
    DB -.-> Database["PostgreSQL"]
    Search -.-> SearchAPI["Search API"]
    Code -.-> Runtime["Code Runtime"]
```

**Coordination:**
- **Independent Servers**: Each MCP server operates independently
- **Tool Discovery**: Agent queries available tools from all servers
- **Context Sharing**: Agent maintains context across tool calls
- **Error Isolation**: Failure in one server doesn't affect others

**Path Management:**
- SSE paths must be unique (e.g., `/sse-files`, `/sse-github`)
- HTTP paths must be unique (e.g., `/mcp-api`, `/mcp-search`)
- Path collision detection during server creation
- Automatic path suggestion for new servers

Sources: [frontend/src/lang/modules/zh.ts:773-788](), [frontend/src/lang/modules/en.ts:773-788]()

### Security Patterns

**Defense in Depth:**

| Layer | stdio | SSE | HTTP |
|-------|-------|-----|------|
| **Process Isolation** | ✓ | ✓ | ✓ |
| **Network Firewall** | N/A | ✓ | ✓ |
| **HTTPS Encryption** | N/A | Optional | Optional |
| **IP Whitelist** | N/A | Via website | Via website |
| **Authentication** | Process-based | Header-based | Header-based |
| **Environment Isolation** | ✓ | ✓ | ✓ |

**Best Practices:**
1. Use stdio for local-only tools requiring file system access
2. Use SSE/HTTP with website binding for remote access
3. Disable external port access after website binding
4. Use environment variables for sensitive configuration
5. Implement IP whitelisting for production deployments
6. Enable HTTPS for all HTTP-based transports
7. Rotate API keys regularly in environment variables

Sources: [frontend/src/lang/modules/zh.ts:781-786](), [frontend/src/lang/modules/en.ts:781-786]()

---

## Operational Considerations

### Server Lifecycle Management

**Operations:**
- **Start**: Launch server process or HTTP endpoint
- **Stop**: Graceful shutdown with timeout
- **Restart**: Stop and start sequence
- **Update**: Modify configuration and restart

**Status Monitoring:**
- Process health checks (stdio)
- HTTP endpoint availability (SSE/HTTP)
- Error log collection
- Resource usage tracking

### Performance Optimization

**stdio Transport:**
- Process pooling for high-frequency tools
- Stdin buffer management
- Stdout parsing optimization

**SSE Transport:**
- Connection pooling
- Event stream compression
- Keep-alive configuration
- Client reconnection handling

**HTTP Transport:**
- Request timeout configuration
- Response streaming buffer size
- Concurrent request limits

### Troubleshooting

**Common Issues:**

| Issue | Transport | Diagnosis | Solution |
|-------|-----------|-----------|----------|
| Server not starting | stdio | Check command path | Verify npx/binary installation |
| Connection refused | SSE/HTTP | Check port binding | Verify base URL and port |
| Path conflict | SSE/HTTP | Duplicate path | Use unique path for each server |
| Environment not loaded | All | Check process env | Verify environment variable syntax |
| Website binding fails | SSE/HTTP | Nginx config error | Check website status |

**Debug Information:**
- Server process ID (stdio)
- Listening port (SSE/HTTP)
- Environment variable dump
- Recent error logs
- Configuration JSON export

Sources: [frontend/src/lang/modules/zh.ts:778](), [frontend/src/lang/modules/en.ts:778]()

---

# Page: AI Proxy Enhancement

# AI Proxy Enhancement

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [frontend/src/lang/modules/en.ts](frontend/src/lang/modules/en.ts)
- [frontend/src/lang/modules/es-es.ts](frontend/src/lang/modules/es-es.ts)
- [frontend/src/lang/modules/ja.ts](frontend/src/lang/modules/ja.ts)
- [frontend/src/lang/modules/ko.ts](frontend/src/lang/modules/ko.ts)
- [frontend/src/lang/modules/ms.ts](frontend/src/lang/modules/ms.ts)
- [frontend/src/lang/modules/pt-br.ts](frontend/src/lang/modules/pt-br.ts)
- [frontend/src/lang/modules/ru.ts](frontend/src/lang/modules/ru.ts)
- [frontend/src/lang/modules/tr.ts](frontend/src/lang/modules/tr.ts)
- [frontend/src/lang/modules/zh-Hant.ts](frontend/src/lang/modules/zh-Hant.ts)
- [frontend/src/lang/modules/zh.ts](frontend/src/lang/modules/zh.ts)

</details>



## Purpose and Scope

This document explains the AI Proxy Enhancement feature in 1Panel, which provides secure, managed access to AI services through reverse proxy configuration. The AI proxy system allows you to expose AI model services (such as Ollama) with enhanced security through HTTPS binding, IP whitelisting, and streaming support.

For information about AI agent and model management, see [AI Agents and Model Management](#9.1). For MCP server configuration, see [MCP Server Management](#9.3). For general website and proxy configuration, see [Website Management System](#7).

---

## Overview

The AI Proxy Enhancement feature creates a secure reverse proxy layer for AI services, typically used with model inference engines like Ollama. Instead of exposing AI services directly on public ports, the proxy configuration:

- Binds AI services to domain names with HTTPS/SSL certificates
- Restricts access through IP whitelisting
- Enables streaming transmission for real-time AI responses
- Provides centralized management through the website system
- Enhances security by disabling direct external port access

**Sources:** [frontend/src/lang/modules/zh.ts:702-710](), [frontend/src/lang/modules/en.ts:701-710]()

---

## Architecture and Components

### AI Proxy Configuration Flow

```mermaid
flowchart TB
    User["User Interface<br/>AI Tools > Proxy"]
    
    ProxyConfig["Proxy Configuration<br/>- Domain binding<br/>- HTTPS/SSL<br/>- IP whitelist<br/>- Streaming enabled"]
    
    WebsiteCreate["Website Creation<br/>Website Management System<br/>(Section 7)"]
    
    NginxConfig["Nginx Configuration<br/>- Reverse proxy rules<br/>- SSL termination<br/>- Access control<br/>- Streaming directives"]
    
    AppConfig["AI App Configuration<br/>(e.g., Ollama)<br/>Disable external port access"]
    
    NginxReload["Nginx Reload<br/>nginx -t && nginx -s reload"]
    
    WebsiteList["Website List<br/>View and manage proxy"]
    
    User -->|"Configure proxy"| ProxyConfig
    ProxyConfig -->|"Create website entry"| WebsiteCreate
    WebsiteCreate -->|"Generate config"| NginxConfig
    ProxyConfig -->|"Update app settings"| AppConfig
    NginxConfig -->|"Apply changes"| NginxReload
    NginxReload -->|"Accessible via"| WebsiteList
```

**Diagram: AI Proxy Configuration Workflow**

The AI proxy system integrates with 1Panel's website management infrastructure to create secure reverse proxy configurations for AI services.

**Sources:** [frontend/src/lang/modules/zh.ts:702-710](), [frontend/src/lang/modules/en.ts:701-710]()

---

### Request Flow Architecture

```mermaid
sequenceDiagram
    participant Client as "External Client"
    participant Nginx as "Nginx Reverse Proxy<br/>HTTPS/SSL"
    participant IPCheck as "IP Whitelist Check"
    participant Upstream as "AI Service<br/>(e.g., Ollama:11434)"
    participant Model as "AI Model<br/>Inference Engine"
    
    Client->>Nginx: HTTPS Request<br/>https://ai.example.com/api/generate
    Nginx->>IPCheck: Validate client IP
    
    alt IP not in whitelist
        IPCheck-->>Nginx: Access Denied
        Nginx-->>Client: 403 Forbidden
    else IP authorized
        IPCheck->>Upstream: Forward request<br/>http://127.0.0.1:11434/api/generate
        Upstream->>Model: Process inference
        
        alt Streaming enabled
            Model-->>Upstream: Stream response chunks
            Upstream-->>Nginx: Stream chunks<br/>Transfer-Encoding: chunked
            Nginx-->>Client: Stream HTTPS response
        else Non-streaming
            Model-->>Upstream: Complete response
            Upstream-->>Nginx: Full response body
            Nginx-->>Client: HTTPS response
        end
    end
```

**Diagram: AI Proxy Request Flow with Security Layers**

This sequence shows how client requests pass through the proxy with security validation before reaching the AI service.

**Sources:** [frontend/src/lang/modules/zh.ts:702-710](), [frontend/src/lang/modules/en.ts:701-710]()

---

## Configuration Options

### Core Proxy Settings

| Setting | Description | Security Benefit |
|---------|-------------|------------------|
| **Domain Binding** | Bind AI service to a specific domain name | Enables HTTPS/SSL, professional access URLs |
| **HTTPS/SSL** | Enable SSL certificate (ACME or manual) | Encrypts transmission, prevents MITM attacks |
| **IP Whitelist** | List of allowed IP addresses/ranges | Prevents unauthorized public access |
| **Streaming Support** | Enable HTTP chunked transfer encoding | Real-time AI response streaming |
| **External Port Disable** | Turn off direct port access on AI app | Forces all traffic through secure proxy |

**Sources:** [frontend/src/lang/modules/zh.ts:702-710](), [frontend/src/lang/modules/en.ts:702-710]()

---

### Security Layers Diagram

```mermaid
graph TB
    subgraph "Security Layer 1: Network"
        DomainBind["Domain Binding<br/>HTTPS Only"]
        SSLCert["SSL Certificate<br/>ACME/Manual"]
    end
    
    subgraph "Security Layer 2: Access Control"
        IPWhitelist["IP Whitelist<br/>Allowed IPs only"]
        PortDisable["External Port Disabled<br/>No direct access"]
    end
    
    subgraph "Security Layer 3: Application"
        Streaming["Streaming Support<br/>Controlled transmission"]
        ProxyHeaders["Proxy Headers<br/>X-Forwarded-For tracking"]
    end
    
    subgraph "AI Service"
        AIApp["AI Application<br/>(Ollama/TensorRT)"]
        LocalPort["127.0.0.1:11434<br/>Localhost only"]
    end
    
    DomainBind --> IPWhitelist
    SSLCert --> IPWhitelist
    IPWhitelist --> Streaming
    PortDisable --> LocalPort
    Streaming --> AIApp
    ProxyHeaders --> AIApp
```

**Diagram: Multi-Layer Security Architecture**

The AI proxy implements defense-in-depth with network encryption, access control, and application-level security.

**Sources:** [frontend/src/lang/modules/zh.ts:702-710](), [frontend/src/lang/modules/en.ts:702-710]()

---

## Integration with Website Management

The AI Proxy Enhancement is tightly integrated with 1Panel's website management system. When you create an AI proxy:

1. **Website Entry Creation**: A new website entry is automatically created in the website list
2. **Nginx Configuration**: The system generates appropriate Nginx reverse proxy configuration
3. **SSL Management**: SSL certificates can be managed through the standard website SSL interface
4. **Domain Management**: Multiple domains can be added through the website domain management
5. **Configuration Access**: Advanced Nginx configuration can be edited through the website config interface

### Management Location

After creation, the AI proxy configuration can be managed from:
- **Website List** (`Website > Project`): View all proxied AI services alongside regular websites
- **AI Tools Section** (`AI > Proxy`): Configure AI-specific proxy settings
- **App Store - Installed** (`Apps > Installed > Ollama > Parameters`): Adjust AI service port exposure settings

**Sources:** [frontend/src/lang/modules/zh.ts:704-706](), [frontend/src/lang/modules/en.ts:704-706]()

---

## Nginx Configuration Details

### Typical Proxy Configuration Structure

The AI proxy generates Nginx configuration with the following key directives:

```
server {
    listen 443 ssl http2;
    server_name ai.example.com;
    
    # SSL Configuration
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # IP Whitelist
    allow 192.168.1.0/24;
    allow 10.0.0.100;
    deny all;
    
    # Streaming support for AI responses
    proxy_buffering off;
    proxy_cache off;
    
    location / {
        proxy_pass http://127.0.0.1:11434;
        proxy_http_version 1.1;
        
        # Streaming headers
        proxy_set_header Connection "";
        chunked_transfer_encoding on;
        
        # Standard proxy headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for long-running AI inference
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }
}
```

### Key Configuration Elements

| Directive | Purpose |
|-----------|---------|
| `proxy_buffering off` | Disables buffering to enable real-time streaming |
| `proxy_cache off` | Prevents caching of AI responses |
| `chunked_transfer_encoding on` | Enables HTTP chunked encoding for streaming |
| `proxy_http_version 1.1` | Uses HTTP/1.1 for persistent connections |
| `proxy_read_timeout 300s` | Allows long-running AI inference operations |
| `allow/deny` directives | Implements IP whitelist access control |

**Sources:** Based on Nginx reverse proxy patterns for streaming services

---

## Use Cases and Examples

### Use Case 1: Secure Ollama Deployment

**Scenario**: Expose Ollama model service securely on a public server

**Configuration**:
1. Install Ollama via 1Panel App Store
2. Create AI Proxy with domain `ollama.company.com`
3. Enable HTTPS with ACME certificate
4. Add office IP range to whitelist: `203.0.113.0/24`
5. Disable external port access on Ollama app
6. Enable streaming for real-time responses

**Result**: Ollama is only accessible via HTTPS from office network, with encrypted streaming responses

---

### Use Case 2: Load Balanced AI Services

**Scenario**: Multiple AI model instances behind a single proxy

```mermaid
graph LR
    Client["Client<br/>https://ai.example.com"]
    
    NginxProxy["Nginx Proxy<br/>SSL + IP Whitelist"]
    
    Upstream1["Ollama Instance 1<br/>127.0.0.1:11434"]
    Upstream2["Ollama Instance 2<br/>127.0.0.1:11435"]
    Upstream3["Ollama Instance 3<br/>127.0.0.1:11436"]
    
    Client -->|"HTTPS request"| NginxProxy
    NginxProxy -->|"Load balance"| Upstream1
    NginxProxy -->|"Load balance"| Upstream2
    NginxProxy -->|"Load balance"| Upstream3
```

**Diagram: Load Balanced AI Proxy Configuration**

Multiple AI service instances can be proxied through a single domain with load balancing for improved performance.

**Sources:** Based on Nginx upstream configuration patterns

---

### Use Case 3: API Gateway for Multiple AI Tools

**Scenario**: Single entry point for different AI services

**Configuration**:
- Domain: `ai-gateway.company.com`
- Path-based routing:
  - `/ollama/*` → Ollama service (port 11434)
  - `/tensorrt/*` → TensorRT-LLM service
  - `/mcp/*` → MCP servers (see [MCP Server Management](#9.3))
- Unified SSL and IP whitelist
- Streaming enabled for all paths

---

## Security Best Practices

### Recommended Security Configuration

1. **Always Enable HTTPS**
   - Use ACME (Let's Encrypt) for automatic certificate management
   - Or upload trusted certificates for internal domains

2. **Implement IP Whitelisting**
   - Add specific office/VPN IP ranges
   - Never use `0.0.0.0/0` for production
   - Review and update whitelist regularly

3. **Disable Direct Port Access**
   - After proxy creation, disable external port access on AI app
   - Navigate to: `App Store > Installed > [AI App] > Parameters`
   - Set port binding to `127.0.0.1` only

4. **Monitor Access Logs**
   - Check Nginx access logs for unauthorized attempts
   - Located in website directory under `/logs/`

5. **Use Strong SSL Configuration**
   - Enable TLS 1.2+ only
   - Use modern cipher suites
   - Enable HSTS headers

**Sources:** [frontend/src/lang/modules/zh.ts:709](), [frontend/src/lang/modules/en.ts:709]()

---

## Integration Points

### Website Management System Integration

The AI Proxy Enhancement leverages the existing website management infrastructure:

- **SSL Certificate Management**: Shares SSL management with website system (see [SSL Certificate Management](#7.4))
- **Domain Management**: Uses website domain management features (see [Domain Management](#7.5))
- **Nginx Configuration**: Utilizes Nginx parser and validation system (see [Nginx Configuration Management](#7.3))
- **Configuration Validation**: Benefits from `nginx -t` validation before applying changes

### AI Tools Integration

The proxy integrates with other AI features:

- **AI Agents**: Proxy configuration for agent API endpoints (see [AI Agents and Model Management](#9.1))
- **Ollama Models**: Direct integration with Ollama service proxying
- **MCP Servers**: Can proxy MCP protocol endpoints (see [MCP Server Management](#9.3))
- **GPU Monitoring**: Access to GPU metrics through proxied endpoints (see [GPU Monitoring and XPU Support](#9.2))

**Sources:** [frontend/src/lang/modules/zh.ts:702-710](), [frontend/src/lang/modules/en.ts:702-710]()

---

## Lifecycle Management

### Creating an AI Proxy

```mermaid
stateDiagram-v2
    [*] --> Configure: User initiates proxy creation
    Configure --> Validate: Enter domain, SSL, whitelist
    Validate --> GenerateConfig: Validation passes
    Validate --> Configure: Validation fails
    GenerateConfig --> CreateWebsite: Generate Nginx config
    CreateWebsite --> UpdateApp: Create website entry
    UpdateApp --> TestConfig: Update AI app port binding
    TestConfig --> Reload: nginx -t passes
    TestConfig --> GenerateConfig: nginx -t fails
    Reload --> Active: nginx -s reload
    Active --> [*]: Proxy operational
```

**Diagram: AI Proxy Creation State Machine**

**Sources:** Based on website creation flow patterns

---

### Modifying an AI Proxy

After creation, modifications can be made through:

1. **Website List**: Navigate to `Website > Project`, locate the proxy entry
2. **Edit Configuration**: Modify Nginx config, SSL settings, or domains
3. **Update IP Whitelist**: Add/remove allowed IP addresses
4. **SSL Certificate Renewal**: Automatic with ACME or manual upload

---

### Deleting an AI Proxy

To remove an AI proxy configuration:

1. Navigate to `Website > Project`
2. Locate and delete the website entry
3. Optionally, re-enable external port access on the AI application

**Warning**: Deleting the proxy configuration will immediately stop all proxied access to the AI service.

**Sources:** [frontend/src/lang/modules/zh.ts:708](), [frontend/src/lang/modules/en.ts:708]()

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| **403 Forbidden** | IP not in whitelist | Add client IP to whitelist via Website config |
| **502 Bad Gateway** | AI service not running | Check AI app status in App Store > Installed |
| **SSL Certificate Error** | Invalid or expired certificate | Renew certificate through Website > SSL management |
| **Streaming Not Working** | Buffering enabled | Verify `proxy_buffering off` in Nginx config |
| **Timeout Errors** | Inference taking too long | Increase `proxy_read_timeout` in config |

### Verification Steps

1. **Check AI Service Status**: Ensure the underlying AI application is running
2. **Verify DNS Resolution**: Confirm domain resolves to server IP
3. **Test Direct Access**: Temporarily test `http://localhost:11434` on server
4. **Review Nginx Error Logs**: Check `/path/to/website/logs/error.log`
5. **Validate Configuration**: Run `nginx -t` to check syntax

---

## Performance Considerations

### Streaming Performance

- **Disable Buffering**: Set `proxy_buffering off` for real-time streaming
- **HTTP/1.1 Keep-Alive**: Use `proxy_http_version 1.1` for connection reuse
- **Timeout Configuration**: Balance between timeout protection and long inference times

### Load Balancing

For high-traffic deployments, consider:
- Multiple AI service instances
- Nginx upstream load balancing
- Health checks for upstream servers
- Connection pooling configuration

**Sources:** Based on Nginx performance optimization patterns

---

## Summary

The AI Proxy Enhancement feature provides a comprehensive solution for securely exposing AI services through 1Panel's infrastructure. Key benefits include:

- **Enhanced Security**: HTTPS encryption, IP whitelisting, and port isolation
- **Centralized Management**: Integration with website management system
- **Streaming Support**: Real-time AI response streaming
- **Professional Access**: Domain-based URLs with SSL certificates
- **Flexible Configuration**: Customizable Nginx reverse proxy settings

By leveraging 1Panel's existing website and SSL management capabilities, the AI proxy system provides enterprise-grade security and management for AI service deployments.

**Sources:** [frontend/src/lang/modules/zh.ts:702-710](), [frontend/src/lang/modules/en.ts:701-710]()

---

# Page: System Operations

# System Operations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/app/api/v2/cronjob.go](agent/app/api/v2/cronjob.go)
- [agent/app/api/v2/dashboard.go](agent/app/api/v2/dashboard.go)
- [agent/app/dto/cronjob.go](agent/app/dto/cronjob.go)
- [agent/app/dto/dashboard.go](agent/app/dto/dashboard.go)
- [agent/app/model/app_launcher.go](agent/app/model/app_launcher.go)
- [agent/app/model/cronjob.go](agent/app/model/cronjob.go)
- [agent/app/repo/app_launcher.go](agent/app/repo/app_launcher.go)
- [agent/app/service/cronjob.go](agent/app/service/cronjob.go)
- [agent/app/service/dashboard.go](agent/app/service/dashboard.go)
- [agent/router/ro_cronjob.go](agent/router/ro_cronjob.go)
- [agent/router/ro_dashboard.go](agent/router/ro_dashboard.go)
- [frontend/src/api/interface/cronjob.ts](frontend/src/api/interface/cronjob.ts)
- [frontend/src/api/interface/dashboard.ts](frontend/src/api/interface/dashboard.ts)
- [frontend/src/api/interface/setting.ts](frontend/src/api/interface/setting.ts)
- [frontend/src/api/modules/cronjob.ts](frontend/src/api/modules/cronjob.ts)
- [frontend/src/api/modules/dashboard.ts](frontend/src/api/modules/dashboard.ts)
- [frontend/src/api/modules/setting.ts](frontend/src/api/modules/setting.ts)
- [frontend/src/views/cronjob/cronjob/index.vue](frontend/src/views/cronjob/cronjob/index.vue)
- [frontend/src/views/cronjob/cronjob/operate/index.vue](frontend/src/views/cronjob/cronjob/operate/index.vue)
- [frontend/src/views/cronjob/cronjob/record/index.vue](frontend/src/views/cronjob/cronjob/record/index.vue)
- [frontend/src/views/cronjob/index.vue](frontend/src/views/cronjob/index.vue)
- [frontend/src/views/home/app/index.vue](frontend/src/views/home/app/index.vue)
- [frontend/src/views/home/index.vue](frontend/src/views/home/index.vue)
- [frontend/src/views/home/status/index.vue](frontend/src/views/home/status/index.vue)
- [frontend/src/views/setting/snapshot/index.vue](frontend/src/views/setting/snapshot/index.vue)

</details>



## Purpose and Scope

This document covers the operational monitoring, automation, and backup capabilities within 1Panel. System Operations encompasses three primary subsystems that enable administrators to monitor system health, automate routine tasks, and manage system snapshots.

**Related Documentation:**
- For infrastructure resource management (containers, databases, files), see [Infrastructure Management](#8)
- For application lifecycle operations, see [Application Management System](#6)
- For system configuration and settings, see [Settings and Configuration Management](#5)

**Subsystems Covered:**
- **Dashboard and Monitoring** - Real-time system metrics, resource visualization, and quick actions ([see details](#10.1))
- **Scheduled Tasks and Cronjobs** - Automated task execution with 10 task types and flexible scheduling ([see details](#10.2))
- **Backup and Snapshot System** - Full system snapshots, incremental backups, and recovery workflows ([see details](#10.3))

---

## System Operations Architecture

The System Operations layer implements a polling-based monitoring architecture combined with cron-scheduled task execution and snapshot-based backup management. All three subsystems share common infrastructure for task logging, progress tracking, and multi-node coordination.

### Component Overview

```mermaid
graph TB
    subgraph "Frontend Views"
        HomeView["home/index.vue<br/>Dashboard UI"]
        CronjobView["cronjob/index.vue<br/>Task Management"]
        SnapshotView["setting/snapshot/index.vue<br/>Snapshot UI"]
    end
    
    subgraph "Backend Services"
        DashboardSvc["dashboardService<br/>IDashboardService"]
        CronjobSvc["cronjobService<br/>ICronjobService"]
        SnapshotSvc["snapshotService<br/>ISnapshotService"]
    end
    
    subgraph "Data Collection"
        PSUtil["psutil Package<br/>CPU/Memory/Disk"]
        GPULib["gpu/xpu Utilities<br/>nvidia-smi/xpu-smi"]
        CronEngine["cron.v3<br/>robfig/cron"]
        DockerStats["Docker SDK<br/>Container Stats"]
    end
    
    subgraph "Storage"
        AgentDB[("agent.db<br/>SQLite")]
        CoreDB[("core.db<br/>SQLite")]
        TaskLogs["Task Log Files<br/>/opt/1panel/data/task"]
        BackupFiles["Backup Archives<br/>Local/Remote Storage"]
    end
    
    HomeView --> DashboardSvc
    CronjobView --> CronjobSvc
    SnapshotView --> SnapshotSvc
    
    DashboardSvc --> PSUtil
    DashboardSvc --> GPULib
    DashboardSvc --> DockerStats
    DashboardSvc --> AgentDB
    
    CronjobSvc --> CronEngine
    CronjobSvc --> AgentDB
    CronjobSvc --> TaskLogs
    
    SnapshotSvc --> AgentDB
    SnapshotSvc --> CoreDB
    SnapshotSvc --> BackupFiles
```

**Sources:** [agent/app/service/dashboard.go:35-56](), [agent/app/service/cronjob.go:25-51](), [frontend/src/views/home/index.vue:1-50]()

---

## Dashboard and Monitoring System

The dashboard provides real-time system metrics through a polling architecture that queries system resources every 3 seconds. The implementation separates base information (CPU model, cores, etc.) from current metrics (CPU usage, memory, I/O, network).

### Dashboard Service Architecture

```mermaid
graph LR
    subgraph "Frontend Polling"
        HomeVue["home/index.vue"]
        Timer["setInterval(3000ms)"]
        APIClient["API Client"]
    end
    
    subgraph "API Endpoints"
        LoadBase["/dashboard/base/:io/:net<br/>LoadDashboardBaseInfo"]
        LoadCurrent["/dashboard/current/:io/:net<br/>LoadDashboardCurrentInfo"]
        LoadTopCPU["/dashboard/current/top/cpu"]
        LoadTopMem["/dashboard/current/top/mem"]
    end
    
    subgraph "Dashboard Service Methods"
        LoadBaseInfo["LoadBaseInfo()<br/>dto.DashboardBase"]
        LoadCurrentInfo["LoadCurrentInfo()<br/>dto.DashboardCurrent"]
        LoadTopCPU_["LoadTopCPU()<br/>[]dto.Process"]
        LoadTopMem_["LoadTopMem()<br/>[]dto.Process"]
    end
    
    subgraph "System Data Sources"
        HostInfo["psutil.HOST<br/>GetHostInfo()"]
        CPUInfo["psutil.CPU<br/>GetCPUUsage()"]
        MemInfo["mem.VirtualMemory()"]
        DiskIO["disk.IOCounters()"]
        NetIO["net.IOCounters()"]
        LoadAvg["load.Avg()"]
    end
    
    Timer --> HomeVue
    HomeVue --> APIClient
    APIClient --> LoadBase
    APIClient --> LoadCurrent
    APIClient --> LoadTopCPU
    APIClient --> LoadTopMem
    
    LoadBase --> LoadBaseInfo
    LoadCurrent --> LoadCurrentInfo
    LoadTopCPU --> LoadTopCPU_
    LoadTopMem --> LoadTopMem_
    
    LoadBaseInfo --> HostInfo
    LoadBaseInfo --> CPUInfo
    LoadCurrentInfo --> CPUInfo
    LoadCurrentInfo --> MemInfo
    LoadCurrentInfo --> DiskIO
    LoadCurrentInfo --> NetIO
    LoadCurrentInfo --> LoadAvg
```

**Sources:** [agent/app/service/dashboard.go:143-181](), [agent/app/service/dashboard.go:183-266](), [agent/app/api/v2/dashboard.go:117-144](), [frontend/src/views/home/index.vue:676-709]()

### Key Data Structures

| Structure | Purpose | Key Fields |
|-----------|---------|------------|
| `dto.DashboardBase` | Static system information | `Hostname`, `Platform`, `CPUModelName`, `CPUCores`, `QuickJumps[]` |
| `dto.DashboardCurrent` | Real-time metrics snapshot | `CPUUsedPercent`, `MemoryUsedPercent`, `IOReadBytes`, `NetBytesSent`, `DiskData[]`, `GPUData[]` |
| `dto.DiskInfo` | Per-mount disk metrics | `Path`, `Device`, `Total`, `Used`, `UsedPercent`, `InodesUsedPercent` |
| `dto.GPUInfo` | GPU telemetry | `ProductName`, `GpuUtil`, `Temperature`, `MemoryUsage` |

**Sources:** [agent/app/dto/dashboard.go:5-30](), [agent/app/dto/dashboard.go:80-128]()

### Dashboard Caching Strategy

The frontend implements intelligent caching to reduce API load while maintaining responsiveness:

```typescript
const DASHBOARD_CACHE_TTL = {
    safeStatus: 10 * 60 * 1000,    // 10 minutes
    netOptions: 60 * 60 * 1000,     // 1 hour
    ioOptions: 60 * 60 * 1000       // 1 hour
};
```

Cache keys stored in localStorage include:
- `netOptions` - Available network interfaces
- `ioOptions` - Available disk devices
- `dashboard_show` - Disk/GPU panel expansion state

**Sources:** [frontend/src/views/home/index.vue:464-468](), [frontend/src/utils/dashboardCache.ts:1-50]()

### Quick Jump System

The dashboard includes customizable quick jump shortcuts for rapid navigation. Users can configure which shortcuts appear (min 1, max 4 visible):

**Database Schema:**
```
quick_jump table:
- id, name, alias, title, detail, recommend, is_show, router
```

**Default Shortcuts:**
- Website (`/websites`)
- Database (`/databases`)
- Cronjob (`/cronjobs`)
- AppInstalled (`/apps/installed`)

**Sources:** [agent/app/repo/app_launcher.go:74-91](), [agent/app/model/app_launcher.go:8-17](), [frontend/src/views/home/quick/index.vue:1-100]()

### App Launcher Widget

The dashboard sidebar displays a configurable list of installed applications with quick action buttons (start/stop/restart). The `app_launcher` table stores which apps are visible:

**Service Methods:**
- `LoadAppLauncher()` - Returns apps with installation details
- `ChangeShow(req.Key, req.Value)` - Toggle app visibility
- `ListLauncherOption()` - Get all installed apps with show status

**Sources:** [agent/app/service/dashboard.go:276-339](), [frontend/src/views/home/app/index.vue:1-50](), [frontend/src/views/home/app/index.vue:206-233]()

---

## Scheduled Tasks and Cronjobs

The cronjob system provides automated task execution with 10 task types, flexible cron scheduling, and comprehensive logging. Built on `robfig/cron` v3, it supports both standard cron syntax and custom intervals (e.g., `@every 30s`).

### Cronjob Task Types

| Type | Description | Key Configuration |
|------|-------------|-------------------|
| `shell` | Execute shell scripts | `Executor`, `Script`, `ContainerName`, `User` |
| `website` | Backup website files | `Website` (IDs or "all") |
| `database` | Backup MySQL/PostgreSQL/Redis | `DBType`, `DBName`, `Args` |
| `directory` | Backup files/directories | `IsDir`, `SourceDir`, `ExclusionRules` |
| `curl` | HTTP requests | `URL` (array of URLs) |
| `app` | Backup installed apps | `AppID` (IDs or "all") |
| `snapshot` | Full system snapshot | `SnapshotRule` (with ignore apps) |
| `log` | Clean system logs | `Scopes[]` (system/ssh/website logs) |
| `cutWebsiteLog` | Rotate website logs | `Website` (IDs or "all") |
| `ntp` | Sync system time | No additional config |
| `cleanLog` | Clean specific log types | `CleanLogConfig.Scopes[]` |

**Sources:** [agent/app/model/cronjob.go:7-49](), [agent/app/dto/cronjob.go:19-63]()

### Cronjob Lifecycle and Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend as cronjob/index.vue
    participant API as /cronjobs
    participant Service as CronjobService
    participant Cron as cron.Cron
    participant Handler as HandleJob()
    participant TaskLog as JobRecords
    
    User->>Frontend: Create cronjob
    Frontend->>API: POST /cronjobs
    API->>Service: Create(req)
    Service->>Service: Validate spec, resources
    Service->>Cron: AddFunc(spec, handler)
    Cron-->>Service: entryID
    Service->>TaskLog: Save cronjob record
    Service-->>Frontend: Success
    
    Note over Cron: Time triggers
    Cron->>Handler: Execute scheduled task
    Handler->>TaskLog: Create JobRecords
    Handler->>Handler: Execute task type logic
    alt Success
        Handler->>TaskLog: Update status="Success"
    else Failure
        Handler->>TaskLog: Update status="Failed"
    end
    
    User->>Frontend: View records
    Frontend->>API: POST /cronjobs/search/records
    API->>Service: SearchRecords()
    Service->>TaskLog: Query job_records
    TaskLog-->>Frontend: Display records with status
```

**Sources:** [agent/app/service/cronjob.go:552-600](), [agent/app/service/cronjob.go:540-550](), [frontend/src/views/cronjob/cronjob/index.vue:1-50]()

### Cron Specification System

The system supports two spec modes controlled by `SpecCustom` boolean:

**Standard Mode (SpecCustom=false):**
- Users select `specType` from predefined options: `perWeek`, `perMonth`, `perNDay`, `perNHour`, `perNMinute`, `perNSecond`
- Frontend converts to cron syntax (e.g., `0 2 * * 1` for weekly Monday 2:00 AM)
- Multiple specs joined with `&&` for multi-schedule tasks

**Custom Mode (SpecCustom=true):**
- Users enter raw cron expressions
- Supports standard 5-field cron: `minute hour day month weekday`
- Supports `@every` syntax: `@every 30s`, `@every 5m`

**Spec Preview:**
```typescript
// POST /cronjobs/next
loadNextHandle(spec: string): Promise<string[]>
// Returns next 5 execution times
```

**Sources:** [agent/app/service/cronjob.go:449-482](), [frontend/src/views/cronjob/cronjob/operate/index.vue:98-233]()

### Task Execution and Logging

Each cronjob execution creates a `JobRecords` entry with:

```go
type JobRecords struct {
    CronjobID   uint
    TaskID      string      // UUID for tracking
    StartTime   time.Time
    Interval    float64     // Execution duration (ms)
    Records     string      // Log file path
    Status      string      // Waiting/Success/Failed/Unexecuted
    Message     string      // Error message if failed
}
```

**Log Storage:**
- Path: `/opt/1panel/data/task/{cronjobID}/{timestamp}.log`
- Real-time streaming via SSE for long-running tasks
- Retention controlled per cronjob or global cleanup

**Sources:** [agent/app/model/cronjob.go:51-63](), [agent/app/service/cronjob.go:484-497]()

### Backup Account Integration

Cronjobs that produce backup files use the backup account system:

**Configuration:**
- `SourceAccountIDs` - Comma-separated IDs of backup destinations
- `DownloadAccountID` - Primary account for downloads (starred in UI)
- `RetainCopies` - Number of backups to keep per account
- `Secret` - Encryption password for backup archives

**Backup Process:**
1. Execute backup operation (database dump, file tar, etc.)
2. Upload to all `SourceAccountIDs` storage backends in parallel
3. Create `backup_record` entries linked via `cronjob_id`
4. Rotate old backups when `RetainCopies` exceeded

**Sources:** [agent/app/service/cronjob.go:72-73](), [frontend/src/views/cronjob/cronjob/operate/index.vue:667-720]()

### Cronjob Groups and Import/Export

**Group Management:**
Groups organize cronjobs, stored in `cronjob_group` table. The "Default" group is auto-created.

**Export Format (JSON):**
```json
{
  "name": "Backup MySQL",
  "type": "database",
  "spec": "0 2 * * *",
  "dbType": "mysql",
  "dbNames": [{"name": "mysql-local", "detailName": "wordpress_db"}],
  "sourceAccounts": ["localhost", "oss-backup"],
  "retainCopies": 7
}
```

**Import Logic:**
- Attempts to resolve resource references (apps, databases, websites) by name
- Sets `status=Pending` if resources not found, `status=Disable` otherwise
- Creates associated alert configurations if `alertCount > 0`

**Sources:** [agent/app/service/cronjob.go:117-213](), [agent/app/service/cronjob.go:215-403]()

### Alert Integration

Cronjobs integrate with the alert system for failure notifications:

**Alert Configuration:**
- `AlertCount` - Max consecutive failures before alert
- `AlertTitle` - Alert subject line
- `AlertMethod` - Comma-separated methods (email, webhook, wechat, dingtalk)

**Tracking:**
The `alert` table stores alert status per cronjob, linked by `type={cronjobType}` and `project={cronjobID}`.

**Sources:** [agent/app/service/cronjob.go:73-82](), [agent/app/service/cronjob.go:97-114]()

---

## Backup and Snapshot System

The snapshot system creates full-state backups of the 1Panel installation, including application data, panel configuration, and optional system-level data. Snapshots support encryption, multi-account storage, and atomic recovery/rollback operations.

### Snapshot Data Structure

```mermaid
graph TB
    subgraph "Snapshot Components"
        SnapshotMeta["Snapshot Metadata<br/>snapshot table"]
        SnapshotFile["Compressed Archive<br/>.tar.gz encrypted"]
    end
    
    subgraph "Snapshot Contents"
        AppData["Application Data<br/>Docker volumes, configs"]
        PanelData["Panel Configuration<br/>agent.db, settings"]
        BackupData["Backup Definitions<br/>Accounts, cronjobs"]
        MonitorData["Monitor History<br/>Optional"]
        Logs["Operation Logs<br/>Optional"]
    end
    
    subgraph "Storage Backends"
        LocalFS["Local Filesystem"]
        S3["AWS S3"]
        OSS["Aliyun OSS"]
        MinIO["MinIO"]
        SFTP["SFTP"]
    end
    
    SnapshotMeta --> SnapshotFile
    SnapshotFile --> AppData
    SnapshotFile --> PanelData
    SnapshotFile --> BackupData
    SnapshotFile --> MonitorData
    SnapshotFile --> Logs
    
    SnapshotFile --> LocalFS
    SnapshotFile --> S3
    SnapshotFile --> OSS
    SnapshotFile --> MinIO
    SnapshotFile --> SFTP
```

**Sources:** [frontend/src/api/interface/setting.ts:156-228](), [agent/app/model/setting.go:1-100]()

### Snapshot Creation Workflow

**Frontend UI:**
- Tree selection for `appData[]`, `panelData[]`, `backupData[]`
- Checkboxes for `withMonitorData`, `withLoginLog`, `withOperationLog`
- Optional encryption password (`secret`)
- Multi-account upload (`sourceAccountIDs`, `downloadAccountID`)

**Backend Process:**
1. Create snapshot record with `status=Waiting`
2. Generate async task with subtasks
3. Collect selected data into staging directory
4. Tar and optionally encrypt archive
5. Upload to all source accounts in parallel
6. Update status to `Success` or `Failed`

**Task Tracking:**
- Frontend opens task log viewer immediately after creation
- Real-time progress via SSE: `/tasks/logs/:taskID`
- Retry on failure: `snapshotRecreate(id)`

**Sources:** [frontend/src/views/setting/snapshot/create/index.vue:1-100](), [frontend/src/api/modules/setting.ts:166-193]()

### Snapshot Recovery System

Recovery restores system state from a snapshot archive. The system validates architecture compatibility and disk space before proceeding.

**Recovery States:**
```
recoverStatus: "" → "Waiting" → "Success" / "Failed"
```

**Recovery Process:**
1. **Pre-validation:**
   - Check `kernelArch` matches (prevent ARM→AMD64 restore)
   - Verify `freeSize > snapshot.size`
   - Decrypt if `secret` provided

2. **Download (if remote):**
   - Stream from `downloadAccount`
   - Progress tracked in task log

3. **Extraction:**
   - Untar to temporary directory
   - Validate data tree structure

4. **Application:**
   - Stop affected services (Docker, Nginx)
   - Restore database files
   - Restore application data
   - Update configuration files

5. **Restart:**
   - Restart services
   - Validate health

**Rollback Capability:**
If recovery fails mid-process, the `rollbackStatus` field tracks rollback operations. The system creates a pre-recovery snapshot automatically for safe rollback.

**Sources:** [frontend/src/views/setting/snapshot/recover/index.vue:1-100](), [frontend/src/api/modules/setting.ts:184-189]()

### Snapshot Import/Export

**Import:**
Users can import external snapshot archives by:
1. Uploading to backup account
2. Selecting snapshot names from account
3. System indexes and validates archives
4. Adds to snapshot list as `status=Success`

**Export:**
Snapshots automatically exist in configured backup accounts. Users download via:
- Direct download button (for local storage)
- Copy from remote storage (S3/OSS/etc.)

**Sources:** [frontend/src/views/setting/snapshot/import/index.vue:1-100](), [frontend/src/api/modules/setting.ts:169-177]()

---

## Integration Points and Cross-System Dependencies

### Task Execution Framework

All three subsystems share a common asynchronous task execution framework:

**Task Model:**
```go
type Task struct {
    ID          string      // UUID
    Type        string      // "Snapshot", "CronjobBackup", etc.
    Status      string      // Waiting/Running/Success/Failed
    LogFile     string      // Real-time log path
    Progress    int         // Percentage (0-100)
    Subtasks    []Subtask   // Parallel operations
}
```

**Progress Tracking:**
- Tasks write to structured log files
- Frontend streams via SSE: `GET /tasks/logs/:taskID`
- Progress parser extracts percentage from log patterns

**Sources:** [agent/app/service/task.go:1-200](), [frontend/src/components/log/task/index.vue:1-100]()

### Multi-Node Coordination

In multi-node deployments, system operations respect node boundaries:

**Dashboard:**
- Master node can read `agent.db` from all nodes
- Aggregates metrics for fleet-wide monitoring
- Node selector in UI for targeted operations

**Cronjobs:**
- Each node maintains its own `cron.Cron` instance
- Cronjobs scoped to creating node
- Cross-node job execution not supported (by design)

**Snapshots:**
- Node-specific snapshots include node identity
- Recovery only to same architecture
- Cross-node snapshot migration requires manual steps

**Sources:** [Multi-Node Architecture Diagram](#2.2), [agent/app/service/dashboard.go:107-141]()

### Backup Account Abstraction

All backup operations use the `backup_account` table for storage destination abstraction:

**Supported Types:**
- `local` - Local filesystem
- `sftp` - SFTP/SSH
- `s3` - AWS S3 compatible
- `oss` - Aliyun OSS
- `cos` - Tencent COS
- `kodo` - Qiniu Kodo
- `minio` - MinIO
- `onedrive` - Microsoft OneDrive

**Service Interface:**
```go
type IBackupService interface {
    Upload(accountID uint, file string) error
    Download(accountID uint, file string) error
    Delete(accountID uint, file string) error
}
```

**Sources:** [agent/app/service/backup.go:1-100](), [agent/app/model/backup_account.go:1-50]()

---

## API Reference Summary

### Dashboard APIs

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/dashboard/base/:io/:net` | GET | Load base system info + current metrics |
| `/dashboard/current/:io/:net` | GET | Load current metrics only (3s polling) |
| `/dashboard/current/top/cpu` | GET | Top 10 CPU processes |
| `/dashboard/current/top/mem` | GET | Top 10 memory processes |
| `/dashboard/quick/option` | GET | List quick jump shortcuts |
| `/dashboard/quick/change` | POST | Update quick jump configuration |
| `/dashboard/app/launcher` | GET | Load app launcher list |
| `/dashboard/app/launcher/show` | POST | Toggle app visibility |

**Sources:** [agent/router/ro_dashboard.go:10-27]()

### Cronjob APIs

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/cronjobs` | POST | Create new cronjob |
| `/cronjobs/search` | POST | Search cronjobs with pagination |
| `/cronjobs/update` | POST | Update cronjob configuration |
| `/cronjobs/del` | POST | Delete cronjobs (with data cleanup) |
| `/cronjobs/status` | POST | Enable/disable cronjob |
| `/cronjobs/handle` | POST | Execute once immediately |
| `/cronjobs/next` | POST | Preview next 5 execution times |
| `/cronjobs/search/records` | POST | Search execution records |
| `/cronjobs/records/log` | POST | Fetch execution log content |
| `/cronjobs/records/clean` | POST | Clean execution records |
| `/cronjobs/import` | POST | Import cronjobs from JSON |
| `/cronjobs/export` | POST | Export cronjobs to JSON |

**Sources:** [agent/router/ro_cronjob.go:10-31]()

### Snapshot APIs

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/settings/snapshot` | POST | Create new snapshot |
| `/settings/snapshot/search` | POST | Search snapshots with pagination |
| `/settings/snapshot/load` | GET | Load snapshot data tree |
| `/settings/snapshot/recover` | POST | Recover from snapshot |
| `/settings/snapshot/rollback` | POST | Rollback failed recovery |
| `/settings/snapshot/recreate` | POST | Retry failed snapshot |
| `/settings/snapshot/del` | POST | Delete snapshots |
| `/settings/snapshot/import` | POST | Import external snapshots |
| `/settings/snapshot/description/update` | POST | Update snapshot description |

**Sources:** [frontend/src/api/modules/setting.ts:165-192]()

---

This completes the System Operations overview. For detailed information on specific subsystems, see the child pages: [Dashboard and Monitoring](#10.1), [Scheduled Tasks and Cronjobs](#10.2), and [Backup and Snapshot System](#10.3).

---

# Page: Dashboard and Monitoring

# Dashboard and Monitoring

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/app/api/v2/dashboard.go](agent/app/api/v2/dashboard.go)
- [agent/app/dto/dashboard.go](agent/app/dto/dashboard.go)
- [agent/app/model/app_launcher.go](agent/app/model/app_launcher.go)
- [agent/app/repo/app_launcher.go](agent/app/repo/app_launcher.go)
- [agent/app/service/dashboard.go](agent/app/service/dashboard.go)
- [agent/router/ro_dashboard.go](agent/router/ro_dashboard.go)
- [frontend/src/api/interface/dashboard.ts](frontend/src/api/interface/dashboard.ts)
- [frontend/src/api/modules/dashboard.ts](frontend/src/api/modules/dashboard.ts)
- [frontend/src/views/home/app/index.vue](frontend/src/views/home/app/index.vue)
- [frontend/src/views/home/index.vue](frontend/src/views/home/index.vue)
- [frontend/src/views/home/status/index.vue](frontend/src/views/home/status/index.vue)

</details>



This document describes the dashboard and monitoring system in 1Panel, which provides real-time visibility into system resources, installed applications, and quick access to common operations. The dashboard serves as the main landing page after login and automatically updates system metrics every 3 seconds.

For information about GPU/XPU monitoring details, see [GPU Monitoring and XPU Support](#9.2). For settings management, see [Settings and Configuration Management](#5).

---

## System Architecture Overview

The dashboard system follows a client-server architecture with polling-based real-time updates. The frontend polls the Agent API every 3 seconds to fetch current system metrics, while implementing intelligent caching for semi-static data like network interface and disk device lists.

```mermaid
graph TB
    subgraph "Frontend Layer"
        HomeView["home/index.vue<br/>Main Dashboard Component"]
        StatusView["home/status/index.vue<br/>System Status Display"]
        AppLauncherView["home/app/index.vue<br/>App Launcher Component"]
        DashCache["dashboardCache.ts<br/>TTL-based Cache"]
    end
    
    subgraph "API Client"
        DashAPI["dashboard.ts API Client"]
    end
    
    subgraph "Agent Backend"
        DashRouter["ro_dashboard.go<br/>Dashboard Router"]
        DashAPI_V2["v2/dashboard.go<br/>API Handlers"]
        DashService["service/dashboard.go<br/>Dashboard Service"]
        LauncherRepo["repo/app_launcher.go<br/>Launcher Repository"]
    end
    
    subgraph "Data Sources"
        ProcFS["/proc filesystem"]
        SysFS["/sys filesystem"]
        PSUtil["gopsutil library"]
        DockerAPI["Docker API"]
        GPUDriver["nvidia-smi/xpu-smi"]
    end
    
    subgraph "Database"
        AgentDB["agent.db<br/>SQLite"]
    end
    
    HomeView -->|"3s polling"| DashAPI
    HomeView --> StatusView
    HomeView --> AppLauncherView
    HomeView --> DashCache
    
    DashAPI --> DashRouter
    DashRouter --> DashAPI_V2
    DashAPI_V2 --> DashService
    DashService --> LauncherRepo
    LauncherRepo --> AgentDB
    
    DashService --> ProcFS
    DashService --> SysFS
    DashService --> PSUtil
    DashService --> DockerAPI
    DashService --> GPUDriver
```

**Sources:** [frontend/src/views/home/index.vue:1-1831](), [agent/app/service/dashboard.go:1-645](), [agent/router/ro_dashboard.go:1-28]()

---

## Real-time Metrics Collection

The system collects metrics from multiple sources using the `gopsutil` library and direct filesystem reads. Metrics are grouped into base info (static) and current info (dynamic).

### API Endpoints

| Endpoint | Purpose | Update Frequency |
|----------|---------|------------------|
| `GET /dashboard/base/:ioOption/:netOption` | Base system info + initial metrics | Once on load |
| `GET /dashboard/current/:ioOption/:netOption` | Current resource utilization | Every 3 seconds |
| `GET /dashboard/current/top/cpu` | Top CPU-consuming processes | On-demand (5s when popover open) |
| `GET /dashboard/current/top/mem` | Top memory-consuming processes | On-demand (5s when popover open) |

**Sources:** [agent/router/ro_dashboard.go:14-25](), [agent/app/api/v2/dashboard.go:118-202]()

### Base Info Collection

Base info includes static system information that rarely changes:

```mermaid
graph LR
    LoadBaseInfo["LoadBaseInfo()"]
    HostInfo["psutil.HOST.GetHostInfo()"]
    CPUInfo["psutil.CPUInfo.GetCPUInfo()"]
    QuickJump["loadQuickJump()"]
    CurrentInfo["LoadCurrentInfo()"]
    
    LoadBaseInfo --> HostInfo
    LoadBaseInfo --> CPUInfo
    LoadBaseInfo --> QuickJump
    LoadBaseInfo --> CurrentInfo
    
    HostInfo -->|"hostname, platform, kernel"| BaseDTO["DashboardBase DTO"]
    CPUInfo -->|"model, cores, frequency"| BaseDTO
    QuickJump -->|"website count, db count"| BaseDTO
    CurrentInfo -->|"initial metrics"| BaseDTO
```

**Implementation details:**
- Hostname, OS platform, kernel version from [agent/app/service/dashboard.go:143-181]()
- CPU model name, core counts from [agent/app/service/dashboard.go:170-177]()
- IPv4 address via UDP connection test to `8.8.8.8:80` [agent/app/service/dashboard.go:599-609]()
- HTTP proxy detection from environment variables [agent/app/service/dashboard.go:164-166]()

**Sources:** [agent/app/service/dashboard.go:143-181](), [agent/app/dto/dashboard.go:5-30]()

### Current Info Collection

Current metrics are collected every 3 seconds via a polling mechanism:

**Collected Metrics:**
- **CPU**: Usage percent per core, total usage, detailed breakdown (user, system, nice, idle, iowait, irq, softirq, steal)
- **Memory**: Total, used, free, available, cache, shared, usage percent
- **Swap**: Total, used, free, usage percent
- **Load Average**: 1-minute, 5-minute, 15-minute averages
- **Disk I/O**: Read/write bytes, operation counts, read/write time
- **Network**: Bytes sent/received per interface
- **Disk Usage**: Per mount point with inode statistics
- **GPU/XPU**: Utilization, temperature, power, memory usage

**Sources:** [agent/app/service/dashboard.go:183-266](), [agent/app/dto/dashboard.go:80-128]()

---

## Dashboard UI Components

The dashboard page consists of three main sections arranged in a responsive grid layout:

```mermaid
graph TB
    subgraph "Left Column (16/24 cols)"
        Overview["Quick Jump Overview<br/>4 configurable shortcuts"]
        Status["System Status Component<br/>Pie charts for resources"]
        Charts["Monitoring Charts<br/>Network/IO line graphs"]
    end
    
    subgraph "Right Column (8/24 cols)"
        Carousel["Carousel Component"]
        SystemInfo["System Info Panel"]
        Memo["Memo Panel (optional)"]
        SimpleNode["Simple Node Panel (optional)"]
        AppLauncher["App Launcher Panel<br/>Installed app shortcuts"]
    end
    
    Overview --> Status
    Status --> Charts
    
    Carousel --> SystemInfo
    Carousel --> Memo
    Carousel --> SimpleNode
    SystemInfo --> AppLauncher
```

**Sources:** [frontend/src/views/home/index.vue:43-415]()

### System Status Component

The `SystemStatus` component displays real-time resource metrics as pie charts with detailed popovers:

**Display Elements:**
- **Load Average**: Pie chart showing load vs capacity, popover with 1/5/15-minute averages
- **CPU**: Pie chart with per-core breakdown, detailed percent breakdown (user/system/idle/etc)
- **Memory**: Pie chart with used/free/cache breakdown, swap memory details
- **Disk**: Per-mount-point pie charts with inode statistics
- **GPU/XPU**: Per-device pie charts with temperature, power, memory usage

**Interactive Features:**
- Clicking CPU/Memory popovers reveals top processes table [frontend/src/views/home/status/index.vue:582-654]()
- Top processes refresh every 5 seconds when popover is open [frontend/src/views/home/status/index.vue:589-619]()
- "Kill Process" action available in top processes table [frontend/src/views/home/status/index.vue:546-559]()
- Clicking disk charts navigates to file manager at mount point [frontend/src/views/home/status/index.vue:289]()
- Clicking GPU charts navigates to GPU monitoring page [frontend/src/views/home/status/index.vue:574-576]()

**Sources:** [frontend/src/views/home/status/index.vue:1-722](), [frontend/src/api/interface/dashboard.ts:70-159]()

### Monitoring Charts

Time-series charts display network and I/O metrics over the last 20 data points (approximately 60 seconds):

**Chart Types:**
- **Network Chart**: Upload/download speeds in KB/s, selectable network interface
- **IO Chart**: Read/write speeds in MB/s, R/W operations per second, I/O delay

**Implementation:**
- Charts use `v-charts` wrapper around ECharts [frontend/src/views/home/index.vue:143-161]()
- Data arrays maintain 20-point sliding window [frontend/src/views/home/index.vue:755-798]()
- Delta calculations compute speed from cumulative byte counts [frontend/src/views/home/index.vue:750-789]()
- Time intervals adjust based on actual uptime delta [frontend/src/views/home/index.vue:749]()

**Sources:** [frontend/src/views/home/index.vue:76-164](), [frontend/src/views/home/index.vue:745-802]()

### Carousel Components

The right column carousel rotates between multiple panels based on configuration:

**Panel Types:**

| Panel | Visibility Condition | Storage Key |
|-------|---------------------|-------------|
| System Info | Always visible | N/A |
| Memo | `DashboardMemoVisible` setting = "Enable" | Setting in database |
| Simple Node | `DashboardSimpleNodeVisible` = "Enable" AND is master node with agent nodes | Setting in database |

**System Info Panel Features:**
- Displays hostname, platform, kernel, IP address, uptime
- Sensitive info toggle button masks hostname/IP [frontend/src/views/home/index.vue:726-728]()
- Copy button exports all system info as text [frontend/src/views/home/index.vue:804-839]()
- Refresh button clears cache and reloads [frontend/src/views/home/index.vue:730-736]()

**Memo Panel:**
- Markdown-rendered notes with edit mode [frontend/src/views/home/index.vue:323-363]()
- 500 character limit with word count [frontend/src/views/home/index.vue:350]()
- Saves to `SystemMemo` setting [frontend/src/views/home/index.vue:853-862]()

**Sources:** [frontend/src/views/home/index.vue:166-411](), [frontend/src/views/home/index.vue:518-524]()

---

## App Launcher System

The App Launcher provides quick access to frequently-used installed applications with one-click start/stop/restart controls.

### Architecture

```mermaid
graph TB
    AppLauncherComp["app/index.vue<br/>Launcher Component"]
    LoadAppLauncher["LoadAppLauncher()<br/>Service Method"]
    AppRepo["appRepo.GetBy()<br/>App Catalog"]
    AppInstallRepo["appInstallRepo.ListBy()<br/>Installed Apps"]
    LauncherRepo["launcherRepo.ListName()<br/>Visible Apps"]
    
    AppLauncherComp -->|"GET /dashboard/app/launcher"| LoadAppLauncher
    LoadAppLauncher --> AppRepo
    LoadAppLauncher --> AppInstallRepo
    LoadAppLauncher --> LauncherRepo
    
    LauncherRepo -->|"Keys of visible apps"| AppLauncherDB["app_launcher table"]
```

**Sources:** [agent/app/service/dashboard.go:276-339](), [frontend/src/views/home/app/index.vue:1-386]()

### Display Logic

The launcher displays apps based on a priority system:

1. **Show installed apps that are in visibility list** (user explicitly enabled)
2. **Show default recommended apps that are NOT installed** (for easy installation)

```mermaid
graph LR
    CheckInstall{"App<br/>Installed?"}
    CheckVisible{"In<br/>Visibility<br/>List?"}
    CheckDefault{"In<br/>Default<br/>Recommend?"}
    
    Show["Display in Launcher"]
    Hide["Hide from Launcher"]
    
    CheckInstall -->|"Yes"| CheckVisible
    CheckInstall -->|"No"| CheckDefault
    CheckVisible -->|"Yes"| Show
    CheckVisible -->|"No"| Hide
    CheckDefault -->|"Yes"| Show
    CheckDefault -->|"No"| Hide
```

**Sources:** [agent/app/service/dashboard.go:326-329]()

### Launcher Configuration

Users can control which apps appear in the launcher via a settings popover:

**Features:**
- Filter search box for app keys [frontend/src/views/home/app/index.vue:5-6]()
- Toggle switches per app [frontend/src/views/home/app/index.vue:11-16]()
- Settings stored in `app_launcher` table [agent/app/model/app_launcher.go:3-6]()
- Changes saved via `POST /dashboard/app/launcher/show` [frontend/src/api/modules/dashboard.ts:20-22]()

**Database Operations:**
- Enable: Creates record in `app_launcher` [agent/app/service/dashboard.go:343-346]()
- Disable: Deletes record from `app_launcher` [agent/app/service/dashboard.go:348-351]()

**Sources:** [frontend/src/views/home/app/index.vue:5-23](), [agent/app/service/dashboard.go:341-354]()

### App Operations

For installed apps, the launcher provides quick controls:

**Available Operations:**
- **Start/Stop/Restart**: Calls `installedOp` API [frontend/src/views/home/app/index.vue:261-287]()
- **Directory Access**: Opens file manager at installation path [frontend/src/views/home/app/index.vue:103]()
- **Web UI Links**: Opens application web interface if configured [frontend/src/views/home/app/index.vue:107-155]()

**Multi-Instance Support:**
- If app has multiple instances, dropdown menu selects active instance [frontend/src/views/home/app/index.vue:46-62]()
- Each instance shows name, version, status [frontend/src/views/home/app/index.vue:48-58]()

**Sources:** [frontend/src/views/home/app/index.vue:27-176]()

---

## Quick Jump Configuration

The Quick Jump section displays 4 configurable shortcuts to commonly-accessed pages with dynamic counts.

### Default Configuration

When no configuration exists, the system uses these defaults:

| Name | Title | Router | Recommend |
|------|-------|--------|-----------|
| Website | menu.website | /websites | 10 |
| Database | menu.database | /databases | 30 |
| Cronjob | menu.cronjob | /cronjobs | 50 |
| AppInstalled | home.appInstalled | /apps/installed | 70 |

**Sources:** [agent/app/repo/app_launcher.go:82-87]()

### Dynamic Detail Calculation

The detail field (count) is dynamically calculated on each dashboard load:

```mermaid
graph LR
    LoadBaseInfo["loadQuickJump()"]
    
    WebsiteRepo["websiteRepo.GetBy()"]
    DBRepos["postgresqlRepo.List()<br/>mysqlRepo.List()"]
    CronjobRepo["cronjobRepo.List()"]
    AppInstallRepo["appInstallRepo.ListBy()"]
    
    LoadBaseInfo --> WebsiteRepo
    LoadBaseInfo --> DBRepos
    LoadBaseInfo --> CronjobRepo
    LoadBaseInfo --> AppInstallRepo
    
    WebsiteRepo -->|"len(websites)"| DetailField["Quick Jump Detail"]
    DBRepos -->|"len(mysql) + len(postgres)"| DetailField
    CronjobRepo -->|"len(cronjobs)"| DetailField
    AppInstallRepo -->|"len(apps)"| DetailField
```

**Sources:** [agent/app/service/dashboard.go:611-644]()

### Customization

Users can customize Quick Jump shortcuts via settings dialog:

**Configuration Options:**
- **Visibility**: Enable/disable each shortcut (minimum 1, maximum 4 visible) [agent/app/service/dashboard.go:379-384]()
- **Alias**: Custom display name instead of count [agent/app/dto/dashboard.go:39]()
- **Detail Override**: Custom text instead of dynamic count [agent/app/dto/dashboard.go:41]()

**Validation:**
- At least 1 shortcut must be visible [agent/app/service/dashboard.go:379-381]()
- Maximum 4 shortcuts can be visible [agent/app/service/dashboard.go:382-384]()
- Changes saved via `POST /dashboard/quick/change` [frontend/src/api/modules/dashboard.ts:11-12]()

**Storage:**
- Configuration stored in `quick_jump` table [agent/app/model/app_launcher.go:8-17]()
- Updates use transaction to ensure atomicity [agent/app/repo/app_launcher.go:92-106]()

**Sources:** [agent/app/service/dashboard.go:356-387](), [agent/app/repo/app_launcher.go:74-106]()

---

## Caching Strategy

The dashboard implements a TTL-based caching system to reduce API calls for semi-static data.

### Cache Configuration

| Cache Key | Data | TTL | Purpose |
|-----------|------|-----|---------|
| `netOptions` | Network interface list | 60 minutes | Network card dropdown options |
| `ioOptions` | Disk device list | 60 minutes | Disk I/O monitoring dropdown options |
| `safeStatus` | Safe entrance status | 10 minutes | Security warning display |

**Sources:** [frontend/src/views/home/index.vue:464-468]()

### Cache Implementation

The cache system uses browser localStorage with timestamp validation:

```mermaid
graph TB
    Request["API Request Needed"]
    CheckCache{"Check<br/>Cache"}
    ValidTTL{"TTL<br/>Valid?"}
    GetAPI["Call API"]
    SetCache["Store in Cache<br/>with Timestamp"]
    UseCache["Return Cached Data"]
    
    Request --> CheckCache
    CheckCache -->|"Cache Exists"| ValidTTL
    CheckCache -->|"No Cache"| GetAPI
    ValidTTL -->|"Yes"| UseCache
    ValidTTL -->|"No"| GetAPI
    GetAPI --> SetCache
    SetCache --> UseCache
```

**Cache Functions:**
- `getDashboardCache(key)`: Retrieves cached data if TTL valid [frontend/src/utils/dashboardCache.ts]()
- `setDashboardCache(key, data, ttl)`: Stores data with expiration timestamp
- `clearDashboardCache()`: Clears all dashboard cache entries
- `clearDashboardCacheByPrefix(prefix)`: Clears specific cache keys

**Sources:** [frontend/src/views/home/index.vue:633-646](), [frontend/src/views/home/index.vue:661-674]()

### Refresh Strategy

**Initial Load:**
1. Check cache for network/IO options
2. If cached, mark as `netOptionsFromCache = true` [frontend/src/views/home/index.vue:637]()
3. Display cached data immediately
4. Apply default selections from settings [frontend/src/views/home/index.vue:618-624]()

**Hover Refresh:**
- When user hovers over chart area, refresh options from API if they were from cache [frontend/src/views/home/index.vue:80]()
- Only refreshes once per page load [frontend/src/views/home/index.vue:499]()
- Updates cache with fresh data [frontend/src/views/home/index.vue:644-645]()

**Manual Refresh:**
- "Refresh" button clears all cache [frontend/src/views/home/index.vue:731]()
- Forces API calls for all data [frontend/src/views/home/index.vue:734]()

**Sources:** [frontend/src/views/home/index.vue:633-674](), [frontend/src/views/home/index.vue:841-850]()

---

## Data Flow and Refresh Patterns

The dashboard uses multiple refresh patterns based on data volatility.

### Polling Mechanism

The main polling loop runs every 3 seconds while the dashboard is visible:

```mermaid
sequenceDiagram
    participant User
    participant HomeView
    participant Timer
    participant API
    participant DashService
    
    User->>HomeView: Load Dashboard
    HomeView->>API: GET /dashboard/base/:io/:net
    API->>DashService: LoadBaseInfo()
    DashService-->>HomeView: Base + Initial Current Info
    
    HomeView->>Timer: Start 3s Interval
    
    loop Every 3 seconds
        Timer->>HomeView: Trigger Update
        HomeView->>API: GET /dashboard/current/:io/:net
        API->>DashService: LoadCurrentInfo()
        DashService-->>HomeView: Current Metrics
        HomeView->>HomeView: Update Charts & Status
    end
    
    User->>HomeView: Leave Page
    HomeView->>Timer: Clear Interval
```

**Sources:** [frontend/src/views/home/index.vue:676-709]()

### Polling Implementation Details

**Interval Management:**
- Timer started after initial base info load [frontend/src/views/home/index.vue:695-707]()
- Interval ID stored to enable cleanup [frontend/src/views/home/index.vue:479]()
- Cleared on component unmount or navigation [frontend/src/views/home/index.vue:1758-1763]()

**Guard Conditions:**
- `isActive`: Pauses polling when tab/window not visible [frontend/src/views/home/index.vue:700]()
- `isCurrentActive`: Stops polling on navigation [frontend/src/views/home/index.vue:698]()
- `globalStore.isOnRestart`: Pauses during panel restart [frontend/src/views/home/index.vue:700]()

**Error Handling:**
- Try-catch wraps update logic [frontend/src/views/home/index.vue:696-705]()
- Errors clear timer to stop infinite retries [frontend/src/views/home/index.vue:705]()

**Sources:** [frontend/src/views/home/index.vue:676-709](), [frontend/src/views/home/index.vue:1758-1763]()

### Metric Calculation

Network and I/O metrics are computed as deltas between polling intervals:

**Network Speed Calculation:**
```
currentSpeed = (newBytes - oldBytes) / 1024 / timeInterval
```

Where `timeInterval` is calculated from uptime delta [frontend/src/views/home/index.vue:749]().

**Implementation:**
- Maintains previous cumulative byte counts [frontend/src/views/home/index.vue:750-767]()
- Computes speed as delta divided by time interval
- Handles counter resets (negative deltas) by showing 0 [frontend/src/views/home/index.vue:751-753]()
- Stores up to 20 speed samples in arrays [frontend/src/views/home/index.vue:755-756]()
- Older samples removed with `splice(0, 1)` [frontend/src/views/home/index.vue:756]()

**Sources:** [frontend/src/views/home/index.vue:745-802]()

---

## Top Process Monitoring

The system can display top CPU and memory consumers on-demand with automatic refresh.

### On-Demand Loading

Top processes are NOT loaded by default to reduce overhead. They load only when user opens the popover:

```mermaid
graph TB
    UserAction["User Clicks<br/>CPU/Memory Chart"]
    OpenPopover["Popover Opens"]
    CheckButton{"User Toggles<br/>'Top Processes'"}
    LoadData["Load Top Processes"]
    StartTimer["Start 5s Timer"]
    UpdateData["Refresh Top Processes"]
    ClosePopover["Popover Closes"]
    StopTimer["Stop Timer"]
    
    UserAction --> OpenPopover
    OpenPopover --> CheckButton
    CheckButton -->|"Enable"| LoadData
    LoadData --> StartTimer
    StartTimer --> UpdateData
    UpdateData -->|"Every 5s"| UpdateData
    OpenPopover --> ClosePopover
    CheckButton -->|"Disable"| StopTimer
    ClosePopover --> StopTimer
```

**Sources:** [frontend/src/views/home/status/index.vue:582-654]()

### API Endpoints

**Top CPU Processes:**
- Endpoint: `GET /dashboard/current/top/cpu`
- Backend: Calls `loadTopCPU()` [agent/app/service/dashboard.go:268-270]()
- Returns: Array of processes sorted by CPU usage descending

**Top Memory Processes:**
- Endpoint: `GET /dashboard/current/top/mem`
- Backend: Calls `loadTopMem()` [agent/app/service/dashboard.go:272-274]()
- Returns: Array of processes sorted by memory usage descending

**Process Data Structure:**
```typescript
{
  name: string;    // Process name
  pid: number;     // Process ID
  percent: number; // CPU % or Memory %
  memory: number;  // Memory usage in bytes
  cmd: string;     // Command line
  user: string;    // Owner username
}
```

**Sources:** [agent/app/api/v2/dashboard.go:183-202](), [frontend/src/api/interface/dashboard.ts:117-124]()

### Process Management

Users can kill processes directly from the top processes table:

**Kill Process Flow:**
1. User clicks "Stop Process" button [frontend/src/views/home/status/index.vue:35-37]()
2. Confirmation dialog with process ID [frontend/src/views/home/status/index.vue:546-554]()
3. User must type "kill now" to confirm
4. API call: `stopProcess({ PID: processID })` [frontend/src/views/home/status/index.vue:556-558]()

**Sources:** [frontend/src/views/home/status/index.vue:546-559]()

### Timer Lifecycle

**Popover Open with Top Processes Enabled:**
- Initial load on toggle [frontend/src/views/home/status/index.vue:585]()
- Clear existing timer if any [frontend/src/views/home/status/index.vue:586-588]()
- Set 5-second interval [frontend/src/views/home/status/index.vue:589]()

**Popover Close or Toggle Disable:**
- Clear interval timer [frontend/src/views/home/status/index.vue:591-594]()
- Reset state flags [frontend/src/views/home/status/index.vue:599]()

**Component Unmount:**
- Cleanup timers in `onBeforeUnmount` hook [frontend/src/views/home/status/index.vue:656-665]()
- Prevents memory leaks from abandoned intervals

**Sources:** [frontend/src/views/home/status/index.vue:582-665]()

---

## Integration with Other Systems

The dashboard integrates with several other 1Panel subsystems:

### GPU/XPU Monitoring

The dashboard displays GPU/XPU metrics collected from hardware drivers:

**Data Collection:**
- NVIDIA GPUs: Uses `nvidia-smi` via `gpu.LoadGpuInfo()` [agent/app/service/dashboard.go:532-558]()
- Intel XPUs: Uses `xpu-smi` via `xpu.LoadDashData()` [agent/app/service/dashboard.go:573-597]()
- Data merged into `currentInfo.gpuData` and `currentInfo.xpuData`

**Display:**
- Per-device pie charts showing utilization percentage
- Popovers with temperature, power usage, memory usage
- Clicking chart navigates to `/aitools/gpu` page [frontend/src/views/home/status/index.vue:326-357]()

**Sources:** [agent/app/service/dashboard.go:532-597](), [frontend/src/views/home/status/index.vue:301-370]()

### Disk Monitoring

Disk information uses parallel goroutines with timeouts to handle slow/hung mounts:

**Collection Strategy:**
- Parse `df` command output for mount points [agent/app/service/dashboard.go:429-469]()
- Filter out temporary, loop, and container filesystems [agent/app/service/dashboard.go:441-467]()
- Spawn goroutine per mount with 5-second timeout [agent/app/service/dashboard.go:476-523]()
- Collect usage stats via `psutil.DISK.GetUsage()` [agent/app/service/dashboard.go:492]()

**Timeout Handling:**
- If mount hangs, timeout triggers after 5 seconds [agent/app/service/dashboard.go:497]()
- Partial data (path, type, device) still added to results [agent/app/service/dashboard.go:498-501]()
- Error logged for debugging [agent/app/service/dashboard.go:501]()

**Sources:** [agent/app/service/dashboard.go:426-530]()

### Multi-Node Simple Nodes

For master nodes in multi-node deployments, the carousel can display agent node status:

**Visibility Conditions:**
- Setting `DashboardSimpleNodeVisible` = "Enable"
- Current node is master (`globalStore.isMasterProductPro`)
- At least one agent node exists [frontend/src/views/home/index.vue:718-724]()

**Node Display:**
- Node name with status indicator (Healthy/Unhealthy)
- Resource summary string [frontend/src/views/home/index.vue:387-388]()
- "Visit" button opens agent panel in new tab [frontend/src/views/home/index.vue:392-403]()

**Data Source:**
- API: `listAllSimpleNodes()` [frontend/src/views/home/index.vue:648-651]()
- Refreshed every 3 seconds along with other metrics [frontend/src/views/home/index.vue:702]()

**Sources:** [frontend/src/views/home/index.vue:365-410](), [frontend/src/views/home/index.vue:648-651]()

---

## Performance Considerations

### Concurrent Disk Scanning

Disk usage collection uses parallel goroutines with WaitGroup synchronization to speed up data collection:

**Concurrency Pattern:**
```go
var (
    wg sync.WaitGroup
    mu sync.Mutex
)
wg.Add(len(mounts))
for i := 0; i < len(mounts); i++ {
    go func(mount diskInfo) {
        defer wg.Done()
        // collect disk stats
        mu.Lock()
        datas = append(datas, itemData)
        mu.Unlock()
    }(mounts[i])
}
wg.Wait()
```

**Sources:** [agent/app/service/dashboard.go:471-524]()

### Debouncing and Guards

**Loading Flags:**
- `cpuLoading` and `memLoading` flags prevent concurrent API calls [frontend/src/views/home/status/index.vue:400-401]()
- Checked before making requests [frontend/src/views/home/status/index.vue:631-653]()

**Hover Refresh:**
- `hasRefreshedOptionsOnHover` flag ensures hover refresh only happens once [frontend/src/views/home/index.vue:499]()
- Prevents repeated API calls on mouse movement [frontend/src/views/home/index.vue:733]()

**Sources:** [frontend/src/views/home/status/index.vue:631-653](), [frontend/src/views/home/index.vue:841-850]()

### Chart Rendering Optimization

**Data Window Limiting:**
- Charts maintain only last 20 data points [frontend/src/views/home/index.vue:755-798]()
- Older points removed with `splice(0, 1)` to maintain constant memory
- Provides ~60 seconds of history at 3-second intervals

**Conditional Rendering:**
- Charts only render when data is available via `v-if` [frontend/src/views/home/index.vue:147-159]()
- Loading indicator shown until first data load [frontend/src/views/home/index.vue:79]()

**Sources:** [frontend/src/views/home/index.vue:143-164](), [frontend/src/views/home/index.vue:755-798]()

---

# Page: Scheduled Tasks and Cronjobs

# Scheduled Tasks and Cronjobs

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/app/api/v2/cronjob.go](agent/app/api/v2/cronjob.go)
- [agent/app/dto/cronjob.go](agent/app/dto/cronjob.go)
- [agent/app/model/cronjob.go](agent/app/model/cronjob.go)
- [agent/app/service/cronjob.go](agent/app/service/cronjob.go)
- [agent/router/ro_cronjob.go](agent/router/ro_cronjob.go)
- [frontend/src/api/interface/cronjob.ts](frontend/src/api/interface/cronjob.ts)
- [frontend/src/api/modules/cronjob.ts](frontend/src/api/modules/cronjob.ts)
- [frontend/src/views/cronjob/cronjob/index.vue](frontend/src/views/cronjob/cronjob/index.vue)
- [frontend/src/views/cronjob/cronjob/operate/index.vue](frontend/src/views/cronjob/cronjob/operate/index.vue)
- [frontend/src/views/cronjob/cronjob/record/index.vue](frontend/src/views/cronjob/cronjob/record/index.vue)
- [frontend/src/views/cronjob/index.vue](frontend/src/views/cronjob/index.vue)
- [frontend/src/views/setting/snapshot/index.vue](frontend/src/views/setting/snapshot/index.vue)

</details>



This document covers 1Panel's scheduled task and cronjob management system, which provides automated execution of various system operations including shell scripts, backups, database operations, and maintenance tasks. The system uses cron-based scheduling (via `robfig/cron/v3`) with a comprehensive management interface for creating, monitoring, and maintaining automated tasks.

The cronjob system supports 10+ task types, custom cron scheduling, script library integration, execution logging with real-time streaming, import/export functionality, and group-based organization.

For backup and snapshot operations that can be scheduled through cronjobs, see page 10.3. For general system settings that affect cronjob behavior, see page 5.

## System Architecture

The cronjob system is built around a service-oriented architecture with frontend UI components, backend services, and cron scheduler integration using `robfig/cron/v3`.

**Cronjob System Architecture**

```mermaid
graph TB
    subgraph "Frontend Components"
        IndexVue["views/cronjob/index.vue<br/>RouterButton: cronjob|library"]
        CronjobListVue["views/cronjob/cronjob/index.vue<br/>ComplexTable<br/>searchCronjobPage()"]
        OperateVue["views/cronjob/cronjob/operate/index.vue<br/>CronjobOperate form<br/>addCronjob()|editCronjob()"]
        RecordVue["views/cronjob/cronjob/record/index.vue<br/>searchRecords()<br/>LogFile component"]
        LibraryVue["views/cronjob/library/index.vue<br/>searchScript()<br/>Script CRUD"]
    end
    
    subgraph "API Client Layer"
        CronjobAPITS["api/modules/cronjob.ts<br/>searchCronjobPage()<br/>addCronjob()<br/>editCronjob()<br/>handleOnce()"]
        InterfaceTS["api/interface/cronjob.ts<br/>Cronjob.CronjobInfo<br/>Cronjob.CronjobOperate<br/>Cronjob.Record"]
    end
    
    subgraph "Backend API Layer"
        BaseApiGo["app/api/v2/cronjob.go<br/>CreateCronjob()<br/>UpdateCronjob()<br/>SearchCronjob()"]
        RouterGo["router/ro_cronjob.go<br/>InitRouter()<br/>/cronjobs routes"]
    end
    
    subgraph "Service Layer"
        CronjobService["app/service/cronjob.go<br/>CronjobService<br/>Create()|Update()|HandleJob()"]
        GlobalCron["global.Cron<br/>*cron.Cron instance<br/>AddFunc()|Remove()"]
        TaskCtxMap["global.TaskCtxMap<br/>map[string]context.CancelFunc<br/>Running task contexts"]
    end
    
    subgraph "Repository Layer"
        CronjobRepo["cronjobRepo<br/>Page()|Create()|Update()"]
        JobRecordsRepo["cronjobRepo<br/>PageRecords()<br/>RecordFirst()"]
    end
    
    subgraph "Database Models"
        CronjobModel["model.Cronjob<br/>Name,Type,Spec,EntryIDs<br/>Status,IsExecuting"]
        JobRecordsModel["model.JobRecords<br/>CronjobID,TaskID<br/>StartTime,Status,Records"]
        ScriptLibraryModel["model.ScriptLibrary<br/>Name,Script"]
    end
    
    CronjobListVue --> CronjobAPITS
    OperateVue --> CronjobAPITS
    RecordVue --> CronjobAPITS
    LibraryVue --> CronjobAPITS
    
    CronjobAPITS --> InterfaceTS
    CronjobAPITS --> BaseApiGo
    RouterGo --> BaseApiGo
    
    BaseApiGo --> CronjobService
    CronjobService --> GlobalCron
    CronjobService --> TaskCtxMap
    CronjobService --> CronjobRepo
    CronjobService --> JobRecordsRepo
    
    CronjobRepo --> CronjobModel
    JobRecordsRepo --> JobRecordsModel
    
    GlobalCron -.trigger execution.-> CronjobService
```

**Sources:** [frontend/src/views/cronjob/index.vue:1-24](), [frontend/src/api/modules/cronjob.ts:1-87](), [frontend/src/api/interface/cronjob.ts:1-232](), [agent/app/service/cronjob.go:1-803](), [agent/app/api/v2/cronjob.go:1-360](), [agent/router/ro_cronjob.go:1-32](), [agent/app/model/cronjob.go:1-70]()

## Task Types and Configuration

1Panel supports 10 primary cronjob task types, each with specific configuration options and execution behaviors. Each type is handled by a dedicated handler method in `CronjobService`.

### Job Type Overview

| Type | Handler Method | Primary Purpose | Key Configuration Fields |
|------|----------------|-----------------|-------------------------|
| `shell` | `handleShell()` | Execute shell scripts | `Executor`, `Script`, `ScriptMode`, `Command`, `ContainerName`, `User` |
| `app` | `handleApp()` | Application backup | `AppID`, `SourceAccountIDs`, `RetainCopies` |
| `website` | `handleWebsite()` | Website backup | `Website`, `SourceAccountIDs`, `ExclusionRules` |
| `database` | `handleDatabase()` | Database backup | `DBType`, `DBName`, `Args`, `SourceAccountIDs` |
| `directory` | `handleDirectory()` | File/folder backup | `SourceDir`, `IsDir`, `ExclusionRules` |
| `cleanLog` | `handleCleanLog()` | System log cleanup | `Config` (CleanLogConfig.Scopes array) |
| `curl` | `handleCurl()` | HTTP request execution | `URL` (string or array) |
| `cutWebsiteLog` | `handleCutWebsiteLog()` | Rotate website logs | `Website`, `SourceAccountIDs` |
| `ntp` | `handleNtp()` | Time synchronization | No additional config required |
| `snapshot` | `handleSnapshot()` | System snapshot creation | `SnapshotRule.WithImage`, `SnapshotRule.IgnoreAppIDs` |

### Job Type Architecture

```mermaid
graph TB
    subgraph "Handler Dispatch - handleJob()"
        JobSwitch["switch cronjob.Type"]
    end
    
    subgraph "Script Execution Handlers"
        HandleShell["handleShell()<br/>Executor: bash/sh/python<br/>InContainer: bool"]
        HandleCurl["handleCurl()<br/>URL execution"]
    end
    
    subgraph "Backup Handlers"
        HandleApp["handleApp()<br/>AppID selection<br/>RetainCopies enforcement"]
        HandleWebsite["handleWebsite()<br/>Website ID selection<br/>File compression"]
        HandleDatabase["handleDatabase()<br/>DBType: mysql/postgresql<br/>Args: mysqldump options"]
        HandleDirectory["handleDirectory()<br/>IsDir + SourceDir<br/>ExclusionRules filtering"]
        HandleSnapshot["handleSnapshot()<br/>SnapshotRule.WithImage<br/>IgnoreAppIDs filtering"]
    end
    
    subgraph "Maintenance Handlers"
        HandleCleanLog["handleCleanLog()<br/>Scopes: system/ssh/website"]
        HandleCutWebsiteLog["handleCutWebsiteLog()<br/>Log rotation per site"]
        HandleNtp["handleNtp()<br/>Time sync execution"]
        HandleClean["handleClean()<br/>Generic cleanup"]
        HandleLog["handleLog()<br/>Log processing"]
    end
    
    subgraph "Storage Integration"
        BackupClientMap["BackupClientMap<br/>SourceAccountIDs parsing"]
        RemoveExpired["removeExpiredBackup()<br/>RetainCopies enforcement"]
    end
    
    JobSwitch --> HandleShell
    JobSwitch --> HandleCurl
    JobSwitch --> HandleApp
    JobSwitch --> HandleWebsite
    JobSwitch --> HandleDatabase
    JobSwitch --> HandleDirectory
    JobSwitch --> HandleSnapshot
    JobSwitch --> HandleCleanLog
    JobSwitch --> HandleCutWebsiteLog
    JobSwitch --> HandleNtp
    JobSwitch --> HandleClean
    JobSwitch --> HandleLog
    
    HandleApp --> BackupClientMap
    HandleWebsite --> BackupClientMap
    HandleDatabase --> BackupClientMap
    HandleDirectory --> BackupClientMap
    HandleSnapshot --> BackupClientMap
    
    BackupClientMap --> RemoveExpired
```

**Sources:** [agent/app/service/cronjob.go:143-196](), [agent/app/service/cronjob_helper.go:1-50](), [agent/app/dto/cronjob.go:19-59](), [agent/app/model/cronjob.go:7-49]()

## Core Components

### CronjobService

The `CronjobService` struct implements the `ICronjobService` interface and provides the main business logic for cronjob management:

| Method | Purpose | Key Operations | Return Values |
|--------|---------|----------------|---------------|
| `Create(dto.CronjobOperate)` | Create new cronjob | 1. Validate name uniqueness<br/>2. Marshal SnapshotRule if type=snapshot<br/>3. Call `StartJob()` to register with cron<br/>4. Create AlertInfo if configured | `error` |
| `Update(uint, dto.CronjobOperate)` | Update existing cronjob | 1. Load existing via `cronjobRepo.Get()`<br/>2. Remove old EntryIDs from global.Cron<br/>3. Call `StartJob()` with new config<br/>4. Update via `cronjobRepo.Update()` | `error` |
| `StartJob(*model.Cronjob, bool)` | Start/restart cron job | 1. Parse multiple specs from Spec field (split by "&&")<br/>2. Call `AddCronJob()` for each spec<br/>3. Return comma-separated EntryIDs | `string, error` |
| `AddCronJob(*model.Cronjob)` | Register single cron entry | 1. Create `addFunc` closure calling `HandleJob()`<br/>2. Register via `global.Cron.AddFunc(spec, addFunc)`<br/>3. Store returned cron.EntryID | `int, error` |
| `HandleOnce(uint)` | Execute job immediately | 1. Load cronjob by ID<br/>2. Check `IsExecuting` flag<br/>3. Call `HandleJob()` directly | `error` |
| `HandleStop(uint)` | Stop running job | 1. Load JobRecords by ID<br/>2. Retrieve cancel function from `global.TaskCtxMap[taskID]`<br/>3. Invoke cancel() to stop context | `error` |
| `SearchWithPage(dto.PageCronjob)` | List cronjobs | 1. Query via `cronjobRepo.Page()`<br/>2. Load last record status via `cronjobRepo.RecordFirst()`<br/>3. Resolve backup account names<br/>4. Check alert configuration | `int64, []dto.CronjobInfo, error` |
| `SearchRecords(dto.SearchRecord)` | List execution records | Query via `cronjobRepo.PageRecords()` with filters | `int64, []dto.Record, error` |
| `UpdateStatus(uint, string)` | Enable/disable cronjob | If enabling: call `StartJob()`<br/>If disabling: remove EntryIDs from global.Cron | `error` |
| `CleanRecord(dto.CronjobClean)` | Clean execution history | 1. Optionally clean backup files via `removeExpiredBackup()`<br/>2. Unlink records via `backupRepo.UpdateRecord()`<br/>3. Delete records via `cronjobRepo.DeleteRecord()` | `error` |
| `Delete(dto.CronjobBatchDelete)` | Delete cronjobs | 1. Remove EntryIDs from global.Cron<br/>2. Call `CleanRecord()`<br/>3. Delete via `cronjobRepo.Delete()`<br/>4. Delete alerts via `alertRepo.Delete()` | `error` |
| `Export(dto.OperateByIDs)` | Export cronjobs | Serialize selected cronjobs to JSON with resolved names | `string, error` |
| `Import([]dto.CronjobTrans)` | Import cronjobs | Resolve names to IDs, create with Status=Pending if unresolved | `error` |
| `LoadNextHandle(string)` | Preview schedule | Parse spec, calculate next 5 execution times using `robfig/cron` parser | `[]string, error` |
| `LoadRecordLog(dto.OperateByID)` | Get execution log | Read log file from JobRecords.Records path | `string` |

**Sources:** [agent/app/service/cronjob.go:25-51](), [agent/app/service/cronjob.go:552-607](), [agent/app/service/cronjob.go:609-628](), [agent/app/service/cronjob.go:672-754](), [agent/app/service/cronjob.go:757-781]()

### Frontend Components

The frontend is organized into several Vue.js components handling different aspects of cronjob management:

| Component | File | Key Features |
|-----------|------|-------------|
| Navigation Root | `frontend/src/views/cronjob/index.vue` | `RouterButton` with two tabs: cronjobs and library |
| Main Cronjob List | `frontend/src/views/cronjob/cronjob/index.vue` | `ComplexTable`, batch operations, status management, export/import |
| Create/Edit Form | `frontend/src/views/cronjob/cronjob/operate/index.vue` | Comprehensive form with task type selection, cron spec builder, script editor |
| Execution Records | `frontend/src/views/cronjob/cronjob/record/index.vue` | Two-pane view with record list and `LogFile` component for real-time logs |
| Script Library | `frontend/src/views/cronjob/library/index.vue` | Reusable script management and storage |

The main list component uses `ComplexTable` for pagination and sorting, with operations including:
- Batch enable/disable via `onBatchChangeStatus()`
- Individual job execution via `handleOnce()`
- Record viewing via `loadDetail()`
- Group management via `editCronjobGroup()`

**Sources:** [frontend/src/views/cronjob/index.vue:13-22](), [frontend/src/views/cronjob/cronjob/index.vue:492-521](), [frontend/src/views/cronjob/cronjob/operate/index.vue:1-40](), [frontend/src/views/cronjob/cronjob/record/index.vue:261-290]()

## Scheduling System

### Cron Specification Management

The system supports both simplified scheduling interfaces and custom cron expressions, with the ability to define multiple schedules per job.

#### Specification Input Flow

```mermaid
graph TB
    subgraph "Frontend UI - operate/index.vue"
        SpecCustomCheckbox["specCustom checkbox<br/>Toggle input mode"]
        SimpleMode["Simple Mode<br/>specObjs: SpecObj[]"]
        CustomMode["Custom Mode<br/>specs: string[]"]
    end
    
    subgraph "Simple Mode Components"
        SpecTypeSelect["specType select<br/>perMinute/perHour/perDay/perWeek/perMonth/perNSecond"]
        WeekSelect["week select<br/>0-6 (Sunday-Saturday)"]
        DayInput["day input<br/>1-31"]
        HourInput["hour input<br/>0-23"]
        MinuteInput["minute input<br/>0-59"]
        SecondInput["second input<br/>Interval seconds"]
    end
    
    subgraph "SpecObj Structure"
        SpecObjFields["interface SpecObj {<br/>  specType: string<br/>  week: number<br/>  day: number<br/>  hour: number<br/>  minute: number<br/>  second: number<br/>}"]
    end
    
    subgraph "Backend Parsing"
        LoadNextHandle["LoadNextHandle(spec)<br/>Parse and validate"]
        CronParser["cron.NewParser()<br/>Minute|Hour|Dom|Month|Dow"]
        EveryParser["@every interval parser<br/>Duration-based"]
    end
    
    subgraph "Scheduler Registration"
        StartJob["StartJob()<br/>Split specs by &&"]
        AddCronJob["AddCronJob()<br/>global.Cron.AddFunc()"]
        EntryIDs["EntryIDs field<br/>Comma-separated cron.EntryID"]
    end
    
    SpecCustomCheckbox -->|false| SimpleMode
    SpecCustomCheckbox -->|true| CustomMode
    
    SimpleMode --> SpecTypeSelect
    SpecTypeSelect --> WeekSelect
    SpecTypeSelect --> DayInput
    SpecTypeSelect --> HourInput
    SpecTypeSelect --> MinuteInput
    SpecTypeSelect --> SecondInput
    
    WeekSelect --> SpecObjFields
    DayInput --> SpecObjFields
    HourInput --> SpecObjFields
    MinuteInput --> SpecObjFields
    SecondInput --> SpecObjFields
    
    SpecObjFields -->|Convert to cron string| LoadNextHandle
    CustomMode -->|Direct spec string| LoadNextHandle
    
    LoadNextHandle --> CronParser
    LoadNextHandle --> EveryParser
    
    CronParser --> StartJob
    EveryParser --> StartJob
    
    StartJob --> AddCronJob
    AddCronJob --> EntryIDs
```

#### Specification Types

**Simple Mode - `SpecObj` Conversion:**

The frontend converts `SpecObj` structures to standard cron specifications:

| `specType` | Cron Pattern | Example |
|-----------|--------------|---------|
| `perNSecond` | `@every Ns` | `@every 30s` (every 30 seconds) |
| `perMinute` | `M * * * *` | `5 * * * *` (every hour at 5 minutes) |
| `perHour` | `M H * * *` | `30 14 * * *` (daily at 14:30) |
| `perDay` | `M H * * *` | `0 2 * * *` (daily at 02:00) |
| `perWeek` | `M H * * W` | `0 3 * * 1` (Mondays at 03:00) |
| `perMonth` | `M H D * *` | `0 4 15 * *` (15th of month at 04:00) |

**Custom Mode - Direct Specification:**

Supports both standard 5-field cron format and `@every` interval syntax:
- Standard: `"0 2 * * *"` (daily at 02:00)
- Interval: `"@every 1h"` (every hour)
- Interval: `"@every 30m"` (every 30 minutes)

**Multiple Schedules:**

Jobs can have multiple schedules by concatenating specs with `"&&"`:
- Frontend: Array of specs stored in `form.specs[]` or `form.specObjs[]`
- Backend: Combined into single string: `"0 2 * * *&&0 14 * * *"` (02:00 and 14:00 daily)
- Execution: `StartJob()` splits by `"&&"` and registers separate cron entries

#### Preview and Validation

The `loadNext()` function provides schedule preview:

```typescript
// frontend/src/views/cronjob/cronjob/operate/index.vue
const loadNext = async (spec) => {
    const res = await loadNextHandle(spec); // Calls LoadNextHandle() API
    nextTimes.value = res.data; // Array of next 5 execution times
};
```

Backend calculation in `LoadNextHandle()`:

```go
// agent/app/service/cronjob.go:449-481
func (u *CronjobService) LoadNextHandle(specStr string) ([]string, error) {
    spec := cron.NewParser(cron.Minute | cron.Hour | cron.Dom | cron.Month | cron.Dow)
    
    if strings.HasPrefix(specStr, "@every ") {
        // Handle @every interval format
        duration := time.Minute // or time.Second based on suffix
        interval := parseInterval(specStr)
        // Calculate next 5 times based on interval
    } else {
        // Parse standard cron spec
        sched, err := spec.Parse(specStr)
        for i := 0; i < 5; i++ {
            nextTime := sched.Next(now)
            next[i] = nextTime.Format(constant.DateTimeLayout)
            now = nextTime
        }
    }
    return next[:], nil
}
```

**Sources:** [frontend/src/views/cronjob/cronjob/operate/index.vue:98-232](), [frontend/src/api/interface/cronjob.ts:170-177](), [agent/app/service/cronjob.go:449-482](), [agent/app/service/cronjob.go:609-628]()

### Job Execution Flow

```mermaid
sequenceDiagram
    participant GlobalCron as "global.Cron<br/>robfig/cron/v3"
    participant AddFunc as "AddFunc() callback"
    participant HandleJob as "HandleJob()"
    participant CronjobRepo as "cronjobRepo"
    participant JobRecords as "model.JobRecords"
    participant TaskSystem as "global.TaskCtxMap"
    participant HandlerMethod as "Type-specific handler"
    participant AlertRepo as "alertRepo"
    
    Note over GlobalCron: "Cron spec triggers at scheduled time"
    GlobalCron->>AddFunc: "Execute registered function"
    AddFunc->>HandleJob: "HandleJob(&cronjob)"
    
    HandleJob->>CronjobRepo: "Check cronjob.IsExecuting"
    alt Already Executing
        HandleJob-->>AddFunc: "Return early (skip execution)"
    end
    
    HandleJob->>CronjobRepo: "Set IsExecuting=true"
    HandleJob->>JobRecords: "Create record: Status=Waiting, TaskID=UUID"
    HandleJob->>TaskSystem: "ctx, cancel = context.WithCancel()<br/>Store in TaskCtxMap[taskID]"
    
    HandleJob->>HandlerMethod: "switch cronjob.Type:<br/>handleShell/handleDatabase/etc"
    
    alt Execution Success
        HandlerMethod-->>HandleJob: "Return nil error"
        HandleJob->>JobRecords: "Update Status=Success"
    else Execution Failure
        HandlerMethod-->>HandleJob: "Return error"
        HandleJob->>JobRecords: "Update Status=Failed, Message=err"
        
        alt RetryTimes > 0
            HandleJob->>HandleJob: "Schedule retry execution"
        end
    end
    
    HandleJob->>JobRecords: "Update Interval (duration in ms)"
    HandleJob->>TaskSystem: "Delete TaskCtxMap[taskID]"
    HandleJob->>CronjobRepo: "Set IsExecuting=false"
    
    alt Has Alert Configuration
        HandleJob->>AlertRepo: "Check alert threshold"
        alt Failure count >= AlertCount
            HandleJob->>AlertRepo: "Trigger alert via alertMethod"
        end
    end
    
    Note over HandleJob,JobRecords: "Logs written to Records path:<br/>global.Dir.DataDir/task/{type}/{name}/{timestamp}.log"
```

**Sources:** [agent/app/service/cronjob.go:791-802](), [agent/app/service/cronjob_helper.go:30-150](), [agent/app/model/cronjob.go:51-63](), [agent/constant/app.go:150-170]()

## Data Models

### Cronjob Model Structure

The `Cronjob` model stores comprehensive task configuration:

| Field Group | Fields | Purpose |
|-------------|--------|---------|
| Basic Info | `Name`, `Type`, `GroupID`, `Status` | Task identification and organization |
| Schedule | `SpecCustom`, `Spec`, `EntryIDs` | Cron scheduling configuration |
| Script Config | `Executor`, `Command`, `ScriptMode`, `Script`, `User` | Shell execution parameters |
| Target Config | `AppID`, `Website`, `DBType`, `DBName`, `URL` | Task target specifications |
| Container Config | `ContainerName`, `InContainer` | Docker execution context |
| Backup Config | `SourceAccountIDs`, `DownloadAccountID`, `RetainCopies` | Storage and retention settings |
| Error Handling | `RetryTimes`, `Timeout`, `IgnoreErr` | Execution behavior configuration |
| Special Rules | `SnapshotRule`, `ExclusionRules` | Type-specific configurations |

**Sources:** [agent/app/model/cronjob.go:7-46]()

### JobRecords Model

The `JobRecords` model tracks execution history:

| Field | Type | Purpose |
|-------|------|---------|
| `CronjobID` | `uint` | Reference to parent cronjob |
| `TaskID` | `string` | Unique execution identifier |
| `StartTime` | `time.Time` | Execution start timestamp |
| `Interval` | `float64` | Execution duration in milliseconds |
| `Records` | `string` | Path to execution log file |
| `Status` | `string` | Success, Failed, or Waiting |
| `Message` | `string` | Error message for failed executions |
| `File` | `string` | Associated file path for file operations |

**Sources:** [agent/app/model/cronjob.go:48-60]()

## API Endpoints

The REST API provides comprehensive cronjob management capabilities:

| Endpoint | Method | Handler Function | Key Parameters |
|----------|--------|-----------------|----------------|
| `/cronjobs` | POST | `CreateCronjob` | `dto.CronjobOperate` structure |
| `/cronjobs/search` | POST | `SearchCronjob` | `dto.PageCronjob` with filtering |
| `/cronjobs/update` | POST | `UpdateCronjob` | `dto.CronjobOperate` with ID |
| `/cronjobs/status` | POST | `UpdateCronjobStatus` | `dto.CronjobUpdateStatus` |
| `/cronjobs/handle` | POST | `HandleOnce` | `dto.OperateByID` |
| `/cronjobs/del` | POST | `DeleteCronjob` | `dto.CronjobBatchDelete` |
| `/cronjobs/search/records` | POST | `SearchJobRecords` | `dto.SearchRecord` |
| `/cronjobs/records/clean` | POST | `CleanRecord` | `dto.CronjobClean` |
| `/cronjobs/next` | POST | `LoadNextHandle` | `dto.CronjobSpec` |
| `/cronjobs/export` | POST | `ExportCronjob` | `dto.OperateByIDs` |
| `/cronjobs/import` | POST | `ImportCronjob` | `dto.CronjobImport` |
| `/cronjobs/load/info` | POST | `LoadCronjobInfo` | `dto.OperateByID` |
| `/cronjobs/records/log` | POST | `LoadRecordLog` | `dto.OperateByID` |
| `/cronjobs/script/options` | GET | `LoadScriptOptions` | No parameters |
| `/cronjobs/group/update` | POST | `UpdateCronjobGroup` | `dto.ChangeGroup` |

**Sources:** [frontend/src/api/modules/cronjob.ts:6-80](), [agent/router/ro_cronjob.go:10-30](), [agent/app/api/v2/cronjob.go:23-337]()

## Script Library System

The system includes a script library for reusable shell scripts:

```mermaid
graph TB
    subgraph "Script Management"
        ScriptLibrary["ScriptLibrary Model<br/>Persistent Script Storage"]
        ScriptOptions["ScriptOptions API<br/>Available Scripts"]
        ScriptCreate["Script Creation<br/>Name + Content"]
    end
    
    subgraph "Script Usage"
        ScriptMode["scriptMode Selection<br/>input/library/select"]
        LibraryScript["Library Script<br/>scriptID Reference"]
        DirectScript["Direct Script<br/>Inline Content"]
        FileScript["File Script<br/>File Path"]
    end
    
    subgraph "Execution Context"
        HostExec["Host Execution<br/>executor (bash/python/sh)"]
        ContainerExec["Container Execution<br/>command (/bin/bash, /bin/sh)"]
        UserContext["User Context<br/>Execution User"]
    end
    
    ScriptLibrary --> ScriptOptions
    ScriptOptions --> LibraryScript
    ScriptCreate --> ScriptLibrary
    
    LibraryScript --> ScriptMode
    DirectScript --> ScriptMode
    FileScript --> ScriptMode
    
    ScriptMode --> HostExec
    ScriptMode --> ContainerExec
    
    HostExec --> UserContext
    ContainerExec --> UserContext
```

The script system supports three modes:
- `input`: Direct script content entry
- `library`: Reference to stored script by `scriptID`  
- `select`: File system path to script file

**Sources:** [frontend/src/views/cronjob/cronjob/operate/index.vue:443-484](), [agent/app/service/cronjob.go:399-422](), [agent/app/model/cronjob.go:62-66]()

## Backup Integration

Cronjobs that perform backup operations integrate with 1Panel's backup account system:

```mermaid
graph LR
    subgraph "Backup Types"
        DatabaseBackup["Database Backup<br/>MySQL/PostgreSQL"]
        DirectoryBackup["Directory Backup<br/>Files/Folders"]
        AppBackup["App Backup<br/>Application Data"]
        SnapshotBackup["Snapshot Backup<br/>System State"]
    end
    
    subgraph "Backup Accounts"
        LocalAccount["Local Storage<br/>File System"]
        S3Account["S3 Compatible<br/>Object Storage"]
        FTPAccount["FTP/SFTP<br/>Remote Server"]
        WebDAVAccount["WebDAV<br/>Network Storage"]
    end
    
    subgraph "Configuration"
        SourceAccountIDs["sourceAccountIDs<br/>Backup Destinations"]
        DownloadAccountID["downloadAccountID<br/>Primary Storage"]
        RetainCopies["retainCopies<br/>Retention Policy"]
    end
    
    DatabaseBackup --> SourceAccountIDs
    DirectoryBackup --> SourceAccountIDs  
    AppBackup --> SourceAccountIDs
    SnapshotBackup --> SourceAccountIDs
    
    SourceAccountIDs --> LocalAccount
    SourceAccountIDs --> S3Account
    SourceAccountIDs --> FTPAccount
    SourceAccountIDs --> WebDAVAccount
    
    DownloadAccountID --> LocalAccount
    DownloadAccountID --> S3Account
    DownloadAccountID --> FTPAccount
    DownloadAccountID --> WebDAVAccount
```

Backup-enabled cronjobs automatically clean expired backups based on `retainCopies` settings and can distribute backups across multiple storage accounts.

**Sources:** [agent/app/service/cronjob.go:562-568](), [agent/app/service/cronjob.go:493-532]()

## Monitoring and Alerting

The cronjob system integrates with 1Panel's alert system for execution monitoring:

| Alert Trigger | Configuration | Notification Methods |
|---------------|---------------|---------------------|
| Job Failure | `AlertCount` - failure threshold | Email, Webhook, Slack, etc. |
| Consecutive Failures | Configurable retry count | Escalation based on method |
| Execution Timeout | `Timeout` setting per job | Alert on timeout events |

Alert configuration includes:
- `alertCount`: Number of failures before alerting
- `alertTitle`: Custom alert message title
- `alertMethod`: Notification delivery method

The alert system creates `AlertInfo` records linked to cronjobs by type and project ID, enabling centralized monitoring of automation failures.

**Sources:** [agent/app/service/cronjob.go:72-81](), [agent/app/service/cronjob.go:582-595](), [frontend/src/views/cronjob/cronjob/operate/index.vue:582-595]()

---

# Page: Backup and Snapshot System

# Backup and Snapshot System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/app/api/v2/cronjob.go](agent/app/api/v2/cronjob.go)
- [agent/app/dto/cronjob.go](agent/app/dto/cronjob.go)
- [agent/app/model/cronjob.go](agent/app/model/cronjob.go)
- [agent/app/service/cronjob.go](agent/app/service/cronjob.go)
- [agent/router/ro_cronjob.go](agent/router/ro_cronjob.go)
- [frontend/src/api/interface/cronjob.ts](frontend/src/api/interface/cronjob.ts)
- [frontend/src/api/interface/setting.ts](frontend/src/api/interface/setting.ts)
- [frontend/src/api/modules/cronjob.ts](frontend/src/api/modules/cronjob.ts)
- [frontend/src/api/modules/setting.ts](frontend/src/api/modules/setting.ts)
- [frontend/src/views/cronjob/cronjob/index.vue](frontend/src/views/cronjob/cronjob/index.vue)
- [frontend/src/views/cronjob/cronjob/operate/index.vue](frontend/src/views/cronjob/cronjob/operate/index.vue)
- [frontend/src/views/cronjob/cronjob/record/index.vue](frontend/src/views/cronjob/cronjob/record/index.vue)
- [frontend/src/views/cronjob/index.vue](frontend/src/views/cronjob/index.vue)
- [frontend/src/views/setting/snapshot/index.vue](frontend/src/views/setting/snapshot/index.vue)

</details>



The Backup and Snapshot System provides complete system state capture and disaster recovery for 1Panel installations. Unlike component-level backups (databases, applications), snapshots capture the entire system state including panel configuration, installed applications, websites, backups, and optional monitoring data.

The system implements a three-tier architecture: Vue.js frontend components for user interaction ([frontend/src/views/setting/snapshot/]() directory), TypeScript API layer with typed interfaces ([frontend/src/api/modules/setting.ts]()), and backend Go services for snapshot operations. Snapshots support selective data inclusion, encryption, remote storage via backup accounts, and full rollback capabilities for failed recovery attempts.

For scheduled snapshot creation, see [8.2 Scheduled Tasks and Cronjobs](#8.2). For application-specific backups, see [6 Application Management System](#6).

## Snapshot Data Model

The snapshot system uses a hierarchical data structure to represent system components and their associated data.

### Core TypeScript Interfaces

```mermaid
graph TB
    subgraph "Snapshot Interfaces"
        SnapshotCreate["SnapshotCreate<br/>Creation request"]
        SnapshotInfo["SnapshotInfo<br/>Snapshot metadata"]
        SnapshotData["SnapshotData<br/>Available data"]
        DataTree["DataTree<br/>Hierarchical structure"]
    end
    
    subgraph "SnapshotCreate Fields"
        SC_ID["id: number"]
        SC_SOURCE["sourceAccountIDs: string"]
        SC_DOWNLOAD["downloadAccountID: string"]
        SC_DESC["description: string"]
        SC_SECRET["secret: string"]
        SC_APPDATA["appData: Array<DataTree>"]
        SC_PANELDATA["panelData: Array<DataTree>"]
        SC_BACKUPDATA["backupData: Array<DataTree>"]
        SC_MONITOR["withMonitorData: boolean"]
        SC_LOGIN["withLoginLog: boolean"]
        SC_OPERATION["withOperationLog: boolean"]
    end
    
    subgraph "DataTree Structure"
        DT_ID["id: string"]
        DT_LABEL["label: string"]
        DT_KEY["key: string"]
        DT_NAME["name: string"]
        DT_SIZE["size: number"]
        DT_PATH["path: string"]
        DT_CHILDREN["Children: Array<DataTree>"]
        DT_ISSHOW["isShow: boolean"]
        DT_ISDISABLE["isDisable: boolean"]
    end
    
    subgraph "SnapshotInfo Fields"
        SI_STATUS["status: string"]
        SI_TASKID["taskID: string"]
        SI_RECOVERID["taskRecoverID: string"]
        SI_ROLLBACKID["taskRollbackID: string"]
        SI_RECOVERSTATUS["recoverStatus: string"]
        SI_ROLLBACKSTATUS["rollbackStatus: string"]
        SI_INTERRUPT["interruptStep: string"]
    end
    
    SnapshotCreate --> SC_ID
    SnapshotCreate --> SC_SOURCE
    SnapshotCreate --> SC_DOWNLOAD
    SnapshotCreate --> SC_APPDATA
    SnapshotCreate --> SC_PANELDATA
    SnapshotCreate --> SC_BACKUPDATA
    SnapshotCreate --> SC_MONITOR
    
    SC_APPDATA --> DataTree
    SC_PANELDATA --> DataTree
    SC_BACKUPDATA --> DataTree
    
    DataTree --> DT_ID
    DataTree --> DT_CHILDREN
    DataTree --> DT_SIZE
    DataTree --> DT_PATH
    
    SnapshotInfo --> SI_STATUS
    SnapshotInfo --> SI_TASKID
    SnapshotInfo --> SI_RECOVERSTATUS
    SnapshotInfo --> SI_ROLLBACKSTATUS
```

**Sources:** [frontend/src/api/interface/setting.ts:139-211]()

### Snapshot Data Categories

The `SnapshotCreate` interface defines three primary data categories, each represented as a tree structure:

| Category | Field | Description | Stored in DataTree |
|----------|-------|-------------|-------------------|
| Application Data | `appData` | Installed applications, Docker containers, volumes | Yes |
| Panel Data | `panelData` | Panel database, system configuration, SSL certificates | Yes |
| Backup Data | `backupData` | Existing backup files, backup configurations | Yes |
| Monitor Data | `withMonitorData` | System monitoring metrics and history | Boolean flag |
| Login Logs | `withLoginLog` | User authentication logs | Boolean flag |
| Operation Logs | `withOperationLog` | Audit trail of panel operations | Boolean flag |

The `DataTree` interface provides hierarchical representation with:
- `id`, `key`, `name`: Identification fields
- `label`: Display name for UI
- `size`: Data size in bytes
- `path`: File system path
- `Children`: Nested DataTree nodes
- `isShow`, `isDisable`: UI control flags

**Sources:** [frontend/src/api/interface/setting.ts:139-211]()

## Snapshot API Layer

The snapshot API provides operations for complete lifecycle management through the settings module.

### API Function Mapping

```mermaid
graph LR
    subgraph "Creation Operations"
        LoadSnapshotInfo["loadSnapshotInfo()"]
        SnapshotCreate["snapshotCreate()"]
        SnapshotRecreate["snapshotRecreate()"]
    end
    
    subgraph "Query Operations"
        SearchSnapshotPage["searchSnapshotPage()"]
        UpdateSnapshotDesc["updateSnapshotDescription()"]
    end
    
    subgraph "Import/Export"
        SnapshotImport["snapshotImport()"]
        SnapshotDelete["snapshotDelete()"]
    end
    
    subgraph "Recovery Operations"
        SnapshotRecover["snapshotRecover()"]
        SnapshotRollback["snapshotRollback()"]
    end
    
    subgraph "Backend Endpoints"
        EP_LOAD["/settings/snapshot/load"]
        EP_CREATE["/settings/snapshot"]
        EP_SEARCH["/settings/snapshot/search"]
        EP_IMPORT["/settings/snapshot/import"]
        EP_RECOVER["/settings/snapshot/recover"]
        EP_ROLLBACK["/settings/snapshot/rollback"]
    end
    
    LoadSnapshotInfo --> EP_LOAD
    SnapshotCreate --> EP_CREATE
    SearchSnapshotPage --> EP_SEARCH
    SnapshotImport --> EP_IMPORT
    SnapshotRecover --> EP_RECOVER
    SnapshotRollback --> EP_ROLLBACK
```

**Sources:** [frontend/src/api/modules/setting.ts:153-180]()

### Snapshot API Functions

| Function | Endpoint | Request Type | Response Type | Purpose |
|----------|----------|--------------|---------------|---------|
| `loadSnapshotInfo` | `/settings/snapshot/load` | GET | `Setting.SnapshotData` | Load available data for snapshot creation |
| `snapshotCreate` | `/settings/snapshot` | POST | - | Create new snapshot |
| `snapshotRecreate` | `/settings/snapshot/recreate` | POST | - | Recreate snapshot by ID |
| `snapshotImport` | `/settings/snapshot/import` | POST | - | Import snapshot from backup account |
| `searchSnapshotPage` | `/settings/snapshot/search` | POST | `ResPage<Setting.SnapshotInfo>` | Search snapshots with pagination |
| `snapshotDelete` | `/settings/snapshot/del` | POST | - | Delete snapshots with optional file removal |
| `snapshotRecover` | `/settings/snapshot/recover` | POST | - | Restore system from snapshot |
| `snapshotRollback` | `/settings/snapshot/rollback` | POST | - | Rollback failed recovery operation |
| `updateSnapshotDescription` | `/settings/snapshot/description/update` | POST | - | Update snapshot description |

**Notable API characteristics:**
- `loadSnapshotInfo` uses `TimeoutEnum.T_60S` for 60-second timeout due to file system scanning
- `snapshotDelete` accepts `deleteWithFile: boolean` to control physical file removal
- Recovery operations use `Setting.SnapshotRecover` interface with `taskID`, `isNew`, `reDownload`, `secret` parameters

**Sources:** [frontend/src/api/modules/setting.ts:153-180]()

## Snapshot Creation Flow

The snapshot creation process begins with loading available data using `loadSnapshotInfo()`, then allows selective inclusion of components through tree selection.

### Data Selection and Creation

```mermaid
graph TD
    UserInitiate["User Initiates<br/>Snapshot Creation"] --> LoadData["loadSnapshotInfo()"]
    LoadData --> ReturnData["Returns Setting.SnapshotData"]
    ReturnData --> DisplayTrees["Display Three Data Trees"]
    
    subgraph "Data Tree Display"
        AppTree["appData: Array<DataTree><br/>Applications, Containers"]
        PanelTree["panelData: Array<DataTree><br/>Panel DB, Config, SSL"]
        BackupTree["backupData: Array<DataTree><br/>Existing Backups"]
    end
    
    DisplayTrees --> AppTree
    DisplayTrees --> PanelTree
    DisplayTrees --> BackupTree
    
    subgraph "Optional Data Flags"
        MonitorFlag["withMonitorData: boolean"]
        LoginLogFlag["withLoginLog: boolean"]
        OperationLogFlag["withOperationLog: boolean"]
    end
    
    AppTree --> UserSelect["User Selects<br/>Data Items"]
    PanelTree --> UserSelect
    BackupTree --> UserSelect
    MonitorFlag --> UserSelect
    LoginLogFlag --> UserSelect
    OperationLogFlag --> UserSelect
    
    UserSelect --> BuildRequest["Build SnapshotCreate"]
    
    subgraph "SnapshotCreate Parameters"
        ID["id: number (0 for new)"]
        SourceAccounts["sourceAccountIDs: string"]
        DownloadAccount["downloadAccountID: string"]
        Description["description: string"]
        Secret["secret: string (encryption)"]
        Timeout["timeout: number"]
        SelectedApp["appData: Array<DataTree>"]
        SelectedPanel["panelData: Array<DataTree>"]
        SelectedBackup["backupData: Array<DataTree>"]
    end
    
    BuildRequest --> ID
    BuildRequest --> SourceAccounts
    BuildRequest --> DownloadAccount
    BuildRequest --> Description
    BuildRequest --> Secret
    BuildRequest --> SelectedApp
    BuildRequest --> SelectedPanel
    BuildRequest --> SelectedBackup
    
    BuildRequest --> CallAPI["snapshotCreate(params)"]
    CallAPI --> BackendProcess["Backend Creates Snapshot"]
    BackendProcess --> TaskTrack["Returns taskID for tracking"]
```

**Sources:** [frontend/src/api/interface/setting.ts:139-154](), [frontend/src/api/modules/setting.ts:154-159]()

### Backup Account Integration

The `SnapshotCreate` interface includes two backup account fields:

- `sourceAccountIDs`: String of account IDs (comma-separated) for uploading snapshot to remote storage
- `downloadAccountID`: String of single account ID for downloading snapshot during recovery

This enables snapshots to be:
1. Created locally
2. Automatically uploaded to multiple remote backup accounts (S3, SFTP, OSS)
3. Downloaded from a specific account during recovery (even on a different server)

**Sources:** [frontend/src/api/interface/setting.ts:139-154]()

## Snapshot Import System

The import functionality allows snapshots to be imported from remote backup accounts, enabling cross-server migration and disaster recovery.

### Import Operation Flow

```mermaid
graph LR
    UserAction["User Selects Import"] --> ImportDialog["Import Dialog"]
    ImportDialog --> SelectAccount["Select Backup Account<br/>backupAccountID"]
    SelectAccount --> ListSnapshots["List Available<br/>Snapshot Files"]
    ListSnapshots --> SelectFiles["User Selects<br/>names: Array<string>"]
    
    SelectFiles --> BuildImport["Build SnapshotImport"]
    
    subgraph "SnapshotImport Interface"
        BackupAccountID["backupAccountID: number"]
        Names["names: Array<string>"]
        Description["description: string"]
    end
    
    BuildImport --> BackupAccountID
    BuildImport --> Names
    BuildImport --> Description
    
    BuildImport --> CallImport["snapshotImport(params)"]
    CallImport --> DownloadFiles["Download from<br/>Backup Account"]
    DownloadFiles --> CreateRecords["Create Snapshot Records"]
    CreateRecords --> Complete["Import Complete"]
```

**Sources:** [frontend/src/api/interface/setting.ts:155-159](), [frontend/src/api/modules/setting.ts:163-165]()

The `snapshotImport` function accepts:
- `backupAccountID`: Remote storage account to download from
- `names`: Array of snapshot file names to import
- `description`: Optional description for imported snapshots

This enables scenarios like:
- Importing snapshots from another server
- Restoring from offsite backup storage
- Migrating between hosting providers

**Sources:** [frontend/src/api/modules/setting.ts:163-165]()

## Snapshot Recovery System

The recovery system restores complete system state from a snapshot with pre-validation checks and rollback capability.

### Recovery Status State Machine

```mermaid
stateDiagram-v2
    [*] --> NoRecovery: Initial State
    NoRecovery --> Waiting: snapshotRecover() called
    Waiting --> Success: Recovery completes
    Waiting --> Failed: Recovery error
    Success --> NoRecovery: New recovery started
    Failed --> Waiting: Retry recovery
    Failed --> RollbackWaiting: snapshotRollback() called
    
    state "Rollback States" as RB {
        RollbackWaiting --> RollbackSuccess: Rollback completes
        RollbackWaiting --> RollbackFailed: Rollback error
        RollbackSuccess --> NoRecovery: System restored
        RollbackFailed --> RollbackWaiting: Retry rollback
    }
```

**Sources:** [frontend/src/api/interface/setting.ts:167-189]()

### SnapshotInfo Status Fields

The `SnapshotInfo` interface tracks recovery state through multiple fields:

| Field | Type | Purpose |
|-------|------|---------|
| `status` | string | Snapshot creation status |
| `taskID` | string | Creation task identifier |
| `taskRecoverID` | string | Recovery task identifier |
| `taskRollbackID` | string | Rollback task identifier |
| `recoverStatus` | string | Current recovery status (null, "Waiting", "Success", "Failed") |
| `recoverMessage` | string | Recovery error or status message |
| `rollbackStatus` | string | Current rollback status (null, "Waiting", "Success", "Failed") |
| `rollbackMessage` | string | Rollback error or status message |
| `interruptStep` | string | Step where recovery was interrupted |

**Sources:** [frontend/src/api/interface/setting.ts:167-189]()

## Recovery Operations and Validation

The recovery system performs pre-flight validation before initiating snapshot restoration to prevent failures.

### Pre-Recovery Validation Flow

```mermaid
graph TD
    START["recoverSnapshot() Called"] --> LoadOS["loadOsInfo()"]
    LoadOS --> CheckDisk{"isSizeOk Validation"}
    CheckDisk -->|"snapInfo.size < diskSize"| CheckArch{"isArchOk Validation"}
    CheckDisk -->|Insufficient Space| DiskError["Show Error Icon<br/>CircleCloseFilled"]
    CheckArch -->|"kernelArch matches"| ValidationPass["Show Success Icon<br/>CircleCheckFilled"]
    CheckArch -->|Architecture Mismatch| ArchError["Show Error Icon<br/>CircleCloseFilled"]
    
    ValidationPass --> BuildParams["Build SnapshotRecover"]
    
    subgraph "SnapshotRecover Interface"
        ID["id: number"]
        TaskID["taskID: string (newUUID)"]
        IsNew["isNew: boolean"]
        ReDownload["reDownload: boolean"]
        Secret["secret: string"]
    end
    
    BuildParams --> ID
    BuildParams --> TaskID
    BuildParams --> IsNew
    BuildParams --> ReDownload
    BuildParams --> Secret
    
    BuildParams --> OpenDialog["recoverRef.acceptParams()"]
    OpenDialog --> UserConfirm["User Confirms Recovery"]
    UserConfirm --> CallAPI["snapshotRecover(params)"]
    CallAPI --> StartTask["Recovery Task Started"]
    
    DiskError --> BlockRecovery["Recovery Disabled"]
    ArchError --> BlockRecovery
```

**Sources:** [frontend/src/api/interface/setting.ts:160-166](), [frontend/src/api/modules/setting.ts:172-174]()

### Recovery Parameter Construction

The `SnapshotRecover` interface defines the recovery request:

```typescript
export interface SnapshotRecover {
    id: number;           // Snapshot ID to recover
    taskID: string;       // UUID for task tracking
    isNew: boolean;       // Whether this is a new recovery attempt
    reDownload: boolean;  // Force re-download from backup account
    secret: string;       // Decryption secret if snapshot is encrypted
}
```

**Validation checks performed:**
1. **Disk Space**: Compare `snapInfo.size` with `os.data.diskSize` to ensure sufficient space
2. **Architecture**: Verify `os.data.kernelArch` matches snapshot architecture to prevent binary incompatibility

**Sources:** [frontend/src/api/interface/setting.ts:160-166]()

## Snapshot Rollback System

The rollback functionality restores the system to its pre-recovery state when a snapshot recovery fails or produces undesired results.

### Rollback Operation Flow

```mermaid
graph TD
    RecoveryFailed["Recovery Status: Failed"] --> UserAction["User Selects Rollback"]
    UserAction --> ConfirmDialog["ElMessageBox.confirm"]
    ConfirmDialog -->|Confirmed| GenerateTaskID["newUUID() for taskID"]
    ConfirmDialog -->|Cancelled| Abort["Rollback Cancelled"]
    
    GenerateTaskID --> BuildRollback["Build SnapshotRecover"]
    
    subgraph "Rollback Request"
        RB_ID["id: snapInfo.id"]
        RB_TASKID["taskID: generated UUID"]
        RB_ISNEW["isNew: false"]
        RB_REDOWNLOAD["reDownload: false"]
        RB_SECRET["secret: snapInfo.secret"]
    end
    
    BuildRollback --> RB_ID
    BuildRollback --> RB_TASKID
    BuildRollback --> RB_ISNEW
    BuildRollback --> RB_REDOWNLOAD
    BuildRollback --> RB_SECRET
    
    BuildRollback --> CallAPI["snapshotRollback(params)"]
    CallAPI --> UpdateStatus["Update rollbackStatus"]
    UpdateStatus --> MonitorTask["Monitor via TaskLog"]
    MonitorTask --> CheckStatus{"Rollback Result"}
    CheckStatus -->|Success| SystemRestored["System Restored<br/>to Pre-Recovery State"]
    CheckStatus -->|Failed| RollbackFailed["Rollback Failed<br/>Manual Intervention Required"]
```

**Sources:** [frontend/src/api/modules/setting.ts:175-177]()

### Rollback Behavior

The `snapshotRollback()` function uses the same `SnapshotRecover` interface as recovery but with different semantics:

- **Recovery**: Restores system from snapshot
- **Rollback**: Restores system from pre-recovery backup (automatically created before recovery)

The backend automatically creates a backup before any recovery operation, allowing rollback to the pre-recovery state if the recovery fails or produces undesired results.

**Key difference:**
- `isNew: false` during rollback indicates this is reverting a previous operation, not a fresh recovery

**Sources:** [frontend/src/api/interface/setting.ts:160-166](), [frontend/src/api/modules/setting.ts:175-177]()

## Task Integration and Monitoring

All snapshot operations integrate with the task management system for async execution tracking.

### Task Lifecycle Integration

```mermaid
graph LR
    Operation["Snapshot Operation"] --> GenerateTaskID["newUUID()"]
    GenerateTaskID --> CallAPI["API Call with taskID"]
    CallAPI --> BackendTask["Backend Creates Task"]
    BackendTask --> TaskLogComponent["TaskLog Component"]
    
    subgraph "Task Monitoring"
        OpenTaskLog["taskLogRef.openWithTaskID()"]
        StreamLogs["Stream Real-time Logs"]
        TrackStatus["Track Task Status"]
        ShowProgress["Display Progress"]
    end
    
    TaskLogComponent --> OpenTaskLog
    OpenTaskLog --> StreamLogs
    StreamLogs --> TrackStatus
    TrackStatus --> ShowProgress
    
    ShowProgress --> CheckResult{"Task Result"}
    CheckResult -->|Success| EmitSearch["emit('search')"]
    CheckResult -->|Failed| ShowError["Display Error"]
    EmitSearch --> RefreshList["Refresh Snapshot List"]
    ShowError --> AllowRetry["Allow Retry/Rollback"]
```

**Sources:** [frontend/src/api/modules/setting.ts:172-177]()

### Operations with Task Integration

| Operation | API Function | Task Type | Monitoring |
|-----------|-------------|-----------|------------|
| Snapshot Creation | `snapshotCreate()` | Async | `taskID` returned in response |
| Snapshot Recovery | `snapshotRecover()` | Async | `taskRecoverID` in `SnapshotInfo` |
| Snapshot Rollback | `snapshotRollback()` | Async | `taskRollbackID` in `SnapshotInfo` |
| Snapshot Import | `snapshotImport()` | Async | Task tracking via backend |

Each operation:
1. Generates UUID via `newUUID()` before API call
2. Passes `taskID` in request parameters
3. Backend creates task record
4. Frontend opens TaskLog component with `taskID`
5. TaskLog streams real-time logs and progress
6. Upon completion, emits 'search' event to refresh list

**Sources:** [frontend/src/api/modules/setting.ts:157-177]()

## Backend Recovery Process

The backend recovery process executes a multi-step restoration sequence with progress tracking and automatic rollback capability.

### Recovery Step Sequence

```mermaid
graph TD
    Start["Recovery Initiated"] --> Step1["RecoverDownload<br/>Download from account"]
    Step1 --> Step2["RecoverDownloadAccount<br/>Verify account access"]
    Step2 --> Step3["RecoverDecompress<br/>Extract snapshot archive"]
    Step3 --> Step4["BackupBeforeRecover<br/>Create rollback point"]
    
    Step4 --> Step5["Readjson<br/>Load snapshot metadata"]
    Step5 --> Step6["ReadjsonPath<br/>Locate manifest"]
    Step6 --> Step7["ReadjsonContent<br/>Parse content"]
    Step7 --> Step8["ReadjsonMarshal<br/>Deserialize data"]
    
    Step8 --> Step9["RecoverApp<br/>Restore applications"]
    Step9 --> Step10["RecoverWebsite<br/>Restore websites"]
    Step10 --> Step11["RecoverAppImage<br/>Pull Docker images"]
    Step11 --> Step12["RecoverCompose<br/>Restore compose apps"]
    
    Step12 --> Step13["RecoverComposeList<br/>Enumerate compose files"]
    Step13 --> Step14["RecoverComposeItem<br/>Restore each compose app"]
    
    Step14 --> AppCheck{"Apps Restored?"}
    AppCheck -->|No| Step15["RecoverAppEmpty<br/>Skip app data"]
    AppCheck -->|Yes| Step16["RecoverBaseData<br/>Restore base config"]
    Step15 --> Step16
    
    Step16 --> DaemonCheck{"daemon.json?"}
    DaemonCheck -->|No| Step17["RecoverDaemonJsonEmpty<br/>Skip Docker config"]
    DaemonCheck -->|Yes| Step18["RecoverDaemonJson<br/>Restore Docker config"]
    Step17 --> Step19["RecoverDBData<br/>Restore databases"]
    Step18 --> Step19
    
    Step19 --> Step20["RecoverBackups<br/>Restore backup configs"]
    Step20 --> Step21["RecoverPanelData<br/>Restore panel DB"]
    Step21 --> Complete["Recovery Complete<br/>Status: Success"]
    
    Step1 -.->|Error| Failed["Recovery Failed<br/>Status: Failed"]
    Step3 -.->|Error| Failed
    Step9 -.->|Error| Failed
    Step21 -.->|Error| Failed
    
    Failed --> Rollback["Rollback Available<br/>BackupBeforeRecover saved"]
```

**Sources:** Backend recovery steps are referenced in [agent/i18n/lang/en.yaml:392-415]()

### Recovery Steps Explanation

| Step | Key | Purpose |
|------|-----|---------|
| RecoverDownload | Download snapshot | Retrieve snapshot file from local or remote storage |
| RecoverDownloadAccount | Verify account | Validate backup account credentials and access |
| RecoverDecompress | Extract | Decompress snapshot archive to temporary location |
| BackupBeforeRecover | Rollback preparation | Create backup of current state for rollback |
| Readjson* | Manifest parsing | Load and parse snapshot manifest with metadata |
| RecoverApp | Application restore | Restore installed applications from snapshot |
| RecoverWebsite | Website restore | Restore Nginx websites and configurations |
| RecoverAppImage | Image pull | Pull required Docker images for applications |
| RecoverCompose | Compose restore | Restore Docker Compose applications |
| RecoverBaseData | Base config | Restore panel base configuration files |
| RecoverDaemonJson | Docker config | Restore Docker daemon configuration |
| RecoverDBData | Database restore | Restore database instances and data |
| RecoverBackups | Backup restore | Restore backup account configurations |
| RecoverPanelData | Panel database | Restore panel's internal database |

The `interruptStep` field in `SnapshotInfo` records which step failed during recovery, enabling targeted troubleshooting and retry logic.

**Sources:** [agent/i18n/lang/en.yaml:392-415](), [frontend/src/api/interface/setting.ts:184]()

## Component-Level Backup Integration

The system integrates backup management with component deletion workflows, providing options to clean up associated backup data when removing system components.

### Database Backup Cleanup

```mermaid
graph TB
    subgraph "Database Deletion Dialog"
        DELETEDIALOG["Database Delete Component"]
        FORCECHECK["forceDelete checkbox"]
        BACKUPCHECK["deleteBackup checkbox"]
        SUBMITDELETE["submit() function"]
    end
    
    subgraph "Backup Options"
        DELETEBACKUP["deleteBackup: boolean<br/>(Remove backup files)"]
        FORCEDELETE["forceDelete: boolean<br/>(Force removal)"]
        DELETEAPI["deleteDatabase() API"]
    end
    
    subgraph "Component Types"
        MYSQLDELETE["MySQL Delete<br/>(mysql/remote/delete)"]
        POSTGRESDELETE["PostgreSQL Delete<br/>(postgresql/remote/delete)"]
        REDISDELETE["Redis Delete<br/>(redis/remote/delete)"]
    end
    
    subgraph "Backup Cleanup Flow"
        BACKUPVALIDATION["Backup Validation"]
        BACKUPREMOVAL["Backup File Removal"]
        COMPONENTREMOVAL["Component Removal"]
        STATUSUPDATE["Status Update"]
    end
    
    DELETEDIALOG --> FORCECHECK
    DELETEDIALOG --> BACKUPCHECK
    DELETEDIALOG --> SUBMITDELETE
    
    FORCECHECK --> FORCEDELETE
    BACKUPCHECK --> DELETEBACKUP
    
    DELETEBACKUP --> DELETEAPI
    FORCEDELETE --> DELETEAPI
    
    MYSQLDELETE --> DELETEAPI
    POSTGRESDELETE --> DELETEAPI
    REDISDELETE --> DELETEAPI
    
    DELETEAPI --> BACKUPVALIDATION
    BACKUPVALIDATION --> BACKUPREMOVAL
    BACKUPREMOVAL --> COMPONENTREMOVAL
    COMPONENTREMOVAL --> STATUSUPDATE
```

### Component Backup Integration Summary

| Component | Delete Component Path | Backup Cleanup | Force Delete |
|-----------|----------------------|----------------|--------------|
| MySQL | `mysql/remote/delete/index.vue` | `deleteBackup` checkbox | `forceDelete` checkbox |
| PostgreSQL | `postgresql/remote/delete/index.vue` | `deleteBackup` checkbox | `forceDelete` checkbox |
| Redis | `redis/remote/delete/index.vue` | `deleteBackup` checkbox | `forceDelete` checkbox |

Each deletion component follows the same pattern:
1. Present `deleteBackup` and `forceDelete` options via checkboxes
2. Call `deleteDatabase()` API with selected options
3. Backend handles backup cleanup if `deleteBackup` is enabled
4. Emit search event to refresh component list
5. Display success message via `MsgSuccess`

Sources: [frontend/src/views/database/mysql/remote/delete/index.vue:10-15](), [frontend/src/views/database/postgresql/remote/delete/index.vue:10-15](), [frontend/src/views/database/redis/remote/delete/index.vue:10-15]()

## Integration with Scheduled Tasks

The backup system integrates with the 1Panel task scheduling system to provide automated backup operations with comprehensive error handling and monitoring.

```mermaid
graph TB
    subgraph "Scheduled Backup Flow"
        CRONJOB[CronJob Trigger]
        TASKSTART[TaskStart]
        BACKUP[Backup Operation]
        UPLOAD[UploadFile]
        TASKEND[TaskEnd]
    end
    
    subgraph "Error Handling"
        BACKUPERR[IgnoreBackupErr]
        UPLOADERR[IgnoreUploadErr]
        LOADFAIL[LoadBackupFailed]
        NORESOURCE[NoSuchResource]
    end
    
    subgraph "Status Reporting"
        SUCCESS[TaskSuccess]
        FAILED[TaskFailed]
        RETRY[TaskRetry]
    end
    
    CRONJOB --> TASKSTART
    TASKSTART --> BACKUP
    BACKUP --> UPLOAD
    UPLOAD --> TASKEND
    
    BACKUP -->|Error| BACKUPERR
    UPLOAD -->|Error| UPLOADERR
    BACKUP -->|Connection Error| LOADFAIL
    BACKUP -->|No Data| NORESOURCE
    
    TASKEND --> SUCCESS
    BACKUPERR --> FAILED
    UPLOADERR --> FAILED
    LOADFAIL --> FAILED
    
    FAILED --> RETRY
```

Sources: [agent/i18n/lang/en.yaml:232-238](), [agent/i18n/lang/en.yaml:301-306]()

---

# Page: Frontend System Details

# Frontend System Details

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Makefile](Makefile)
- [agent/utils/common/sqlite.go](agent/utils/common/sqlite.go)
- [core/middleware/operation.go](core/middleware/operation.go)
- [core/utils/common/sqlite.go](core/utils/common/sqlite.go)
- [frontend/src/api/interface/app.ts](frontend/src/api/interface/app.ts)
- [frontend/src/api/modules/app.ts](frontend/src/api/modules/app.ts)
- [frontend/src/components/app-status/index.vue](frontend/src/components/app-status/index.vue)
- [frontend/src/global/form-rules.ts](frontend/src/global/form-rules.ts)
- [frontend/src/lang/modules/en.ts](frontend/src/lang/modules/en.ts)
- [frontend/src/lang/modules/es-es.ts](frontend/src/lang/modules/es-es.ts)
- [frontend/src/lang/modules/ja.ts](frontend/src/lang/modules/ja.ts)
- [frontend/src/lang/modules/ko.ts](frontend/src/lang/modules/ko.ts)
- [frontend/src/lang/modules/ms.ts](frontend/src/lang/modules/ms.ts)
- [frontend/src/lang/modules/pt-br.ts](frontend/src/lang/modules/pt-br.ts)
- [frontend/src/lang/modules/ru.ts](frontend/src/lang/modules/ru.ts)
- [frontend/src/lang/modules/tr.ts](frontend/src/lang/modules/tr.ts)
- [frontend/src/lang/modules/zh-Hant.ts](frontend/src/lang/modules/zh-Hant.ts)
- [frontend/src/lang/modules/zh.ts](frontend/src/lang/modules/zh.ts)
- [frontend/src/styles/common.scss](frontend/src/styles/common.scss)
- [frontend/src/views/app-store/apps/index.vue](frontend/src/views/app-store/apps/index.vue)
- [frontend/src/views/app-store/detail/index.vue](frontend/src/views/app-store/detail/index.vue)
- [frontend/src/views/app-store/detail/install/index.vue](frontend/src/views/app-store/detail/install/index.vue)
- [frontend/src/views/app-store/detail/params/index.vue](frontend/src/views/app-store/detail/params/index.vue)
- [frontend/src/views/app-store/installed/detail/index.vue](frontend/src/views/app-store/installed/detail/index.vue)
- [frontend/src/views/app-store/installed/index.vue](frontend/src/views/app-store/installed/index.vue)
- [frontend/src/views/app-store/installed/upgrade/index.vue](frontend/src/views/app-store/installed/upgrade/index.vue)
- [frontend/src/views/website/website/create/index.vue](frontend/src/views/website/website/create/index.vue)
- [frontend/src/views/website/website/index.vue](frontend/src/views/website/website/index.vue)

</details>



## Purpose and Scope

This document provides an in-depth overview of the 1Panel frontend architecture, covering the technology stack, project organization, state management, internationalization, and core patterns. The frontend is a Vue 3 single-page application built with TypeScript and Vite, offering a responsive web interface for managing Linux servers.

For detailed information on reusable component patterns and shared components, see [Component Architecture and Patterns](#11.1). For API client implementation and TypeScript type definitions, see [API Client Layer and Type System](#11.2). For form validation rules and utility functions, see [Form Validation and Utilities](#11.3).

---

## Technology Stack Overview

The 1Panel frontend leverages modern web technologies optimized for performance and developer experience.

### Core Framework Diagram

```mermaid
graph TB
    subgraph "Build & Dev Tools"
        Vite["Vite 5.0<br/>Build Tool & Dev Server"]
        TS["TypeScript 5.3<br/>Type System"]
    end
    
    subgraph "Framework Layer"
        Vue["Vue 3.4<br/>Composition API"]
        Router["Vue Router<br/>Client-side Routing"]
        Pinia["Pinia<br/>State Management"]
        I18n["vue-i18n<br/>Internationalization"]
    end
    
    subgraph "UI & Visualization"
        ElementPlus["Element Plus<br/>Component Library"]
        Monaco["Monaco Editor<br/>Code Editing"]
        VCharts["v-charts<br/>ECharts Wrapper"]
    end
    
    subgraph "HTTP & Utilities"
        Axios["Axios<br/>HTTP Client"]
        Utils["Utility Functions<br/>Form Rules, Helpers"]
    end
    
    Vite --> Vue
    Vite --> TS
    Vue --> Router
    Vue --> Pinia
    Vue --> I18n
    Vue --> ElementPlus
    Vue --> Monaco
    Vue --> VCharts
    Vue --> Axios
    TS --> Utils
```

**Key Dependencies:**

| Package | Version | Purpose |
|---------|---------|---------|
| Vue | 3.4.x | Reactive UI framework with Composition API |
| TypeScript | 5.3.x | Static typing and enhanced IDE support |
| Vite | 5.0.x | Fast build tool with hot module replacement |
| Element Plus | Latest | Comprehensive Vue 3 component library |
| Monaco Editor | Latest | VS Code's editor for in-browser code editing |
| Vue Router | Latest | Official routing solution |
| Pinia | Latest | Official state management (Vuex replacement) |
| vue-i18n | Latest | Internationalization framework |
| Axios | Latest | Promise-based HTTP client |

Sources: [Diagram 4 from high-level architecture](#), [frontend/package.json]() (implied)

---

## Project Structure and Build System

### Directory Organization

The frontend follows a feature-based organization with clear separation of concerns:

```mermaid
graph LR
    Frontend["frontend/"]
    
    Frontend --> Src["src/"]
    Frontend --> Public["public/"]
    
    Src --> Views["views/<br/>Page Components"]
    Src --> Components["components/<br/>Shared Components"]
    Src --> Api["api/<br/>HTTP Clients"]
    Src --> Lang["lang/<br/>i18n Messages"]
    Src --> Styles["styles/<br/>Global Styles"]
    Src --> Router["router/<br/>Route Definitions"]
    Src --> Store["stores/<br/>Pinia Stores"]
    Src --> Utils["utils/<br/>Helper Functions"]
    Src --> Global["global/<br/>Global Config"]
    
    Views --> AppStore["app-store/"]
    Views --> Website["website/"]
    Views --> Container["container/"]
    Views --> Database["database/"]
    Views --> Files["files/"]
    
    Lang --> LangModules["modules/<br/>zh.ts, en.ts, etc."]
```

**Key Directories:**

- **`src/views/`**: Page-level components organized by feature (app-store, website, container, database, etc.)
- **`src/components/`**: Reusable components like `AppStatus`, `ComplexTable`, `LayoutContent`
- **`src/api/`**: API client layer with typed interfaces and HTTP methods
- **`src/lang/modules/`**: Translation files for 10 supported languages
- **`src/global/`**: Global configuration including form validation rules
- **`src/styles/`**: SCSS stylesheets including `common.scss` for shared styles

Sources: [frontend/src/views/app-store/installed/index.vue:1-7](), [frontend/src/views/website/website/index.vue:1-11](), [frontend/src/components/app-status/index.vue:1-9]()

### Build System

The project uses **Vite** for development and production builds, configured via the Makefile:

```mermaid
graph LR
    Make["Makefile"]
    Make --> BuildBase["build_base<br/>Backend Compilation"]
    Make --> BuildFrontend["build_frontend<br/>Frontend Build"]
    
    BuildFrontend --> NpmInstall["npm install<br/>Dependency Resolution"]
    BuildFrontend --> NpmBuild["npm run build<br/>Vite Production Build"]
    BuildFrontend --> CopyDist["Copy dist/ to<br/>backend/resources"]
    
    NpmBuild --> TypeCheck["TypeScript Type Checking"]
    NpmBuild --> ViteBuild["Vite Bundling & Minification"]
    ViteBuild --> OutputDist["dist/<br/>Optimized Assets"]
```

The Makefile defines build targets that handle cross-platform compilation and frontend asset generation. The `build_frontend` target runs `npm install` and `npm run build`, then copies the compiled assets to the backend's resource directory for embedding.

Sources: [Makefile:1-20]()

---

## Internationalization (i18n) System

1Panel supports **10 languages** with a comprehensive translation system managed through vue-i18n.

### Supported Languages

```mermaid
graph TB
    I18nRoot["i18n System<br/>vue-i18n"]
    
    I18nRoot --> ZH["zh<br/>Simplified Chinese"]
    I18nRoot --> EN["en<br/>English"]
    I18nRoot --> ZH_Hant["zh-Hant<br/>Traditional Chinese"]
    I18nRoot --> JA["ja<br/>Japanese"]
    I18nRoot --> MS["ms<br/>Malay"]
    I18nRoot --> PT_BR["pt-br<br/>Portuguese (Brazilian)"]
    I18nRoot --> RU["ru<br/>Russian"]
    I18nRoot --> KO["ko<br/>Korean"]
    I18nRoot --> TR["tr<br/>Turkish"]
    I18nRoot --> ES_ES["es-es<br/>Spanish (Spain)"]
```

### Message Structure

Translation files follow a hierarchical structure organized by functional domain:

```mermaid
graph TB
    MessageRoot["message"]
    
    MessageRoot --> Commons["commons<br/>Common UI Elements"]
    MessageRoot --> Menu["menu<br/>Navigation Items"]
    MessageRoot --> Database["database<br/>Database Management"]
    MessageRoot --> Container["container<br/>Container Operations"]
    MessageRoot --> Website["website<br/>Website Management"]
    MessageRoot --> AITools["aiTools<br/>AI Features"]
    MessageRoot --> App["app<br/>App Store"]
    MessageRoot --> Cronjob["cronjob<br/>Scheduled Tasks"]
    
    Commons --> Button["button<br/>Action Labels"]
    Commons --> Table["table<br/>Table Elements"]
    Commons --> Status["status<br/>Status Messages"]
    Commons --> Rule["rule<br/>Validation Messages"]
    Commons --> Msg["msg<br/>User Feedback"]
```

### Translation Key Examples

The i18n system uses nested keys accessed via dot notation:

| Key Path | English | Chinese | Usage |
|----------|---------|---------|-------|
| `commons.button.create` | "Create" | "创建" | Primary action buttons |
| `commons.status.running` | "Running" | "已启动" | Status indicators |
| `database.create` | "Create database" | "创建数据库" | Page headers |
| `app.installSuccess` | "Install successful" | "安装成功" | Success messages |
| `website.defaultServer` | "Default Server" | "默认服务器" | Configuration labels |

### Usage in Components

Components access translations using the `$t()` function:

```vue
<!-- In template -->
<el-button @click="sync" type="primary" plain>
    {{ $t('commons.button.refresh') }}
</el-button>

<!-- With parameters -->
<span>{{ $t('commons.table.total', [count]) }}</span>

<!-- In script -->
import { useI18n } from 'vue-i18n';
const { t } = useI18n();
const message = t('database.formatHelper', [charset]);
```

Sources: [frontend/src/lang/modules/zh.ts:1-100](), [frontend/src/lang/modules/en.ts:1-100](), [frontend/src/views/app-store/installed/index.vue:8-11](), [frontend/src/views/website/website/index.vue:23-28]()

---

## Component Architecture Patterns

### Page Component Structure

Page-level components follow a consistent pattern using `LayoutContent` wrapper:

```mermaid
graph TB
    Page["Page Component<br/>(e.g., index.vue)"]
    
    Page --> LayoutContent["LayoutContent<br/>Layout Wrapper"]
    
    LayoutContent --> AppSlot["#app slot<br/>AppStatus Component"]
    LayoutContent --> SearchSlot["#search slot<br/>Tags, Filters"]
    LayoutContent --> LeftToolbar["#leftToolBar slot<br/>Primary Actions"]
    LayoutContent --> RightToolbar["#rightToolBar slot<br/>Search, Options"]
    LayoutContent --> MainSlot["#main slot<br/>Content Area"]
    
    MainSlot --> MainDiv["MainDiv<br/>Scrollable Container"]
    MainDiv --> DataDisplay["Data Display<br/>Tables, Cards, Lists"]
    
    Page --> Dialogs["Dialogs & Drawers<br/>Create, Edit, Detail"]
```

**Example Pattern:**

```vue
<template>
    <LayoutContent v-loading="loading" :title="$t('menu.website')">
        <template #app>
            <AppStatus :app-key="'openresty'" @setting="setting" />
        </template>
        <template #leftToolBar>
            <el-button type="primary" @click="openCreate">
                {{ $t('website.create') }}
            </el-button>
        </template>
        <template #rightToolBar>
            <TableSearch @search="search()" v-model:searchName="req.name" />
        </template>
        <template #main>
            <MainDiv :heightDiff="300">
                <!-- Content -->
            </MainDiv>
        </template>
    </LayoutContent>
</template>
```

Sources: [frontend/src/views/app-store/installed/index.vue:2-17](), [frontend/src/views/website/website/index.vue:11-56]()

### Common Component Patterns

#### AppStatus Component

The `AppStatus` component displays the status of installed applications and provides quick actions:

```mermaid
graph LR
    AppStatus["AppStatus Component"]
    
    AppStatus --> Tag["el-tag<br/>App Name & Version"]
    AppStatus --> StatusIndicator["Status Component<br/>Running/Stopped"]
    AppStatus --> Actions["Action Buttons<br/>Start/Stop/Settings"]
    
    Actions --> Emit["@setting<br/>@is-exist<br/>Event Emitters"]
```

The component manages application lifecycle visibility and provides standardized status display across different pages.

Sources: [frontend/src/components/app-status/index.vue:1-9](), [frontend/src/views/website/website/index.vue:14-21]()

#### Drawer and Dialog Patterns

Modal interactions use `DrawerPro` component with consistent structure:

```vue
<DrawerPro v-model="open" :header="title" size="large" @close="handleClose">
    <template #buttons>
        <el-button type="primary" @click="submit">
            {{ $t('commons.button.save') }}
        </el-button>
    </template>
    <el-form ref="formRef" :model="form" :rules="rules">
        <!-- Form content -->
    </el-form>
    <template #footer>
        <!-- Footer actions -->
    </template>
</DrawerPro>
```

Sources: [frontend/src/views/app-store/installed/detail/index.vue:1-10](), [frontend/src/views/website/website/create/index.vue:1-12]()

---

## State Management and Routing

### Pinia Store Pattern

The application uses Pinia for global state management. While specific store files aren't shown, the pattern follows Pinia's composition-style stores:

```mermaid
graph TB
    PiniaRoot["Pinia Root Store"]
    
    PiniaRoot --> GlobalStore["globalStore<br/>currentNode, user info"]
    PiniaRoot --> MenuStore["menuStore<br/>Navigation state"]
    PiniaRoot --> AppStore["appStore<br/>App-specific state"]
    
    GlobalStore --> State["State<br/>Reactive Properties"]
    GlobalStore --> Getters["Getters<br/>Computed Values"]
    GlobalStore --> Actions["Actions<br/>State Mutations"]
```

**Typical Usage:**
- `currentNode`: Tracks the active server node in multi-node deployments
- User session data: Authentication and permission information
- UI state: Active tabs, filters, search terms

### Vue Router Structure

Routes are organized by feature modules with lazy-loaded components:

```mermaid
graph LR
    Router["Vue Router"]
    
    Router --> Dashboard["/home<br/>Dashboard"]
    Router --> Apps["/apps<br/>App Store"]
    Router --> Websites["/websites<br/>Website Management"]
    Router --> Containers["/containers<br/>Container Management"]
    Router --> Databases["/databases<br/>Database Management"]
    Router --> Files["/files<br/>File Manager"]
    Router --> Settings["/settings<br/>System Settings"]
    
    Websites --> WebsiteList["/websites<br/>List View"]
    Websites --> WebsiteCreate["/websites/create<br/>Create Form"]
    
    Apps --> AppList["/apps<br/>Browse Apps"]
    Apps --> AppInstalled["/apps/installed<br/>Installed Apps"]
```

Routes support navigation guards for authentication and permission checks, ensuring users only access authorized resources.

Sources: [frontend/src/views/website/website/index.vue:1-10]() (RouterButton usage), [frontend/src/views/app-store/apps/index.vue:1-4]()

---

## Form Handling and Validation

### Centralized Validation Rules

Form validation rules are centralized in `global/form-rules.ts`, providing reusable validators:

```mermaid
graph TB
    FormRules["form-rules.ts"]
    
    FormRules --> BasicRules["Basic Validators"]
    FormRules --> NetworkRules["Network Validators"]
    FormRules --> SystemRules["System Validators"]
    
    BasicRules --> checkNoSpace["checkNoSpace<br/>No whitespace"]
    BasicRules --> checkPassword["checkPassword<br/>Complexity rules"]
    
    NetworkRules --> checkIp["checkIp<br/>IPv4 validation"]
    NetworkRules --> checkIpv4["checkIpv4<br/>Optional IPv4"]
    NetworkRules --> checkPort["checkPort<br/>Port range 1-65535"]
    NetworkRules --> checkDomain["checkDomain<br/>Domain format"]
    
    SystemRules --> checkCommonName["checkCommonName<br/>1-128 chars, no special"]
    SystemRules --> checkLinuxName["checkLinuxName<br/>Linux-safe names"]
```

**Example Validators:**

| Validator | Purpose | Error Message Key |
|-----------|---------|-------------------|
| `checkIp` | Validates IPv4 addresses | `commons.rule.ip` |
| `checkPort` | Validates port numbers (1-65535) | `commons.rule.port` |
| `checkNoSpace` | Ensures no whitespace characters | `setting.noSpace` |
| `checkCommonName` | Validates resource names (1-128 chars) | `commons.rule.commonName` |

### Form Binding Pattern

Forms use Element Plus `el-form` with reactive data binding:

```vue
<el-form
    ref="websiteForm"
    label-position="top"
    :model="website"
    :rules="rules"
    :validate-on-rule-change="false"
>
    <el-form-item :label="$t('website.primaryDomain')" prop="primaryDomain">
        <el-input v-model="website.primaryDomain" />
    </el-form-item>
    
    <el-form-item :label="$t('website.type')" prop="type">
        <el-radio-group v-model="website.type" @change="changeType">
            <el-radio-button value="static">Static</el-radio-button>
            <el-radio-button value="proxy">Proxy</el-radio-button>
        </el-radio-group>
    </el-form-item>
</el-form>
```

Sources: [frontend/src/global/form-rules.ts:1-50](), [frontend/src/views/website/website/create/index.vue:4-19]()

---

## API Communication Layer

### Request Structure

API calls use Axios with typed interfaces defined in `api/interface/`:

```mermaid
graph LR
    Component["Vue Component"]
    
    Component --> ApiModule["API Module<br/>(e.g., app.ts)"]
    ApiModule --> HttpClient["http<br/>Axios Instance"]
    
    HttpClient --> RequestInterceptor["Request Interceptor<br/>Add auth headers"]
    HttpClient --> ResponseInterceptor["Response Interceptor<br/>Handle errors"]
    
    HttpClient --> CoreAPI["Core API<br/>:9999"]
    HttpClient --> AgentAPI["Agent API<br/>:10000"]
    
    ApiModule --> TypeDefs["TypeScript Interfaces<br/>(api/interface/)"]
```

### API Interface Example

TypeScript interfaces ensure type safety across API calls:

```typescript
// api/interface/app.ts
export namespace App {
    export interface App extends CommonModel {
        name: string;
        key: string;
        tags: Tag[];
        shortDescZh: string;
        shortDescEn: string;
        type: string;
        status: string;
    }
    
    export interface AppDTO extends App {
        versions: string[];
        installed: boolean;
        architectures: string;
    }
}

// api/modules/app.ts
export const syncApp = (req: App.AppStoreSync) => {
    return http.post<any>(`/apps/sync`, req, TimeoutEnum.T_40S);
};

export const searchApp = (req: App.AppReq) => {
    return http.post<App.AppResPage>(`/apps/search`, req);
};
```

API functions return strongly-typed promises, enabling IDE autocomplete and compile-time error detection.

Sources: [frontend/src/api/interface/app.ts:1-67](), [frontend/src/api/modules/app.ts:1-20]()

---

## Styling System

### Global Styles

The application uses SCSS for styling with a centralized approach:

```mermaid
graph TB
    Styles["styles/"]
    
    Styles --> Common["common.scss<br/>Utility Classes"]
    Styles --> Variables["_variables.scss<br/>Theme Variables"]
    Styles --> Mixins["_mixins.scss<br/>Reusable Styles"]
    
    Common --> FlexUtilities["Flex Utilities<br/>.flx-center, .flx-align-center"]
    Common --> TextUtilities["Text Utilities<br/>.sle (ellipsis)"]
    Common --> Animations["Animations<br/>fade-transform"]
    
    Variables --> Colors["Color Palette<br/>Primary, Success, Warning"]
    Variables --> Spacing["Spacing Scale<br/>Margins, Padding"]
```

**Common Utility Classes:**

| Class | Purpose | CSS |
|-------|---------|-----|
| `.flx-center` | Flex center alignment | `display: flex; align-items: center; justify-content: center;` |
| `.flx-align-center` | Flex vertical center | `display: flex; align-items: center;` |
| `.sle` | Single-line ellipsis | `overflow: hidden; text-overflow: ellipsis; white-space: nowrap;` |

### Element Plus Customization

The UI framework is customized through CSS variables and component props. Element Plus provides consistent theming across all components.

Sources: [frontend/src/styles/common.scss:1-50]()

---

## Key Feature Examples

### App Store Interface

The app store demonstrates complex state management and interaction patterns:

```mermaid
graph TB
    AppStorePage["apps/index.vue<br/>App Store Page"]
    
    AppStorePage --> Tags["Tags Component<br/>Category Filter"]
    AppStorePage --> Search["TableSearch<br/>Name Search"]
    AppStorePage --> SyncButton["Sync Button<br/>Update App List"]
    
    AppStorePage --> AppCards["App Cards<br/>Grid Display"]
    AppCards --> AppDetail["Detail Drawer<br/>detail/index.vue"]
    
    AppDetail --> InstallForm["Install Drawer<br/>install/index.vue"]
    InstallForm --> ParamsForm["Params Form<br/>params/index.vue"]
    
    SyncButton --> SyncAPI["syncApp()<br/>POST /apps/sync"]
    Search --> SearchAPI["searchApp()<br/>POST /apps/search"]
```

The app store page coordinates multiple child components, managing loading states, filters, and modal interactions.

Sources: [frontend/src/views/app-store/apps/index.vue:1-42](), [frontend/src/views/app-store/detail/index.vue:1-7](), [frontend/src/views/app-store/detail/install/index.vue:1-10]()

### Installed Apps Management

The installed apps page provides lifecycle management for deployed applications:

```mermaid
graph LR
    InstalledPage["installed/index.vue"]
    
    InstalledPage --> AppCard["AppCard Component<br/>Per-app Actions"]
    
    AppCard --> StartStop["Start/Stop<br/>Lifecycle Control"]
    AppCard --> Upgrade["Upgrade<br/>Version Management"]
    AppCard --> Settings["Settings<br/>Parameter Edit"]
    AppCard --> Backups["Backups<br/>Data Protection"]
    AppCard --> Logs["Logs<br/>Debug Info"]
    AppCard --> Terminal["Terminal<br/>Direct Access"]
    
    Settings --> DetailDrawer["detail/index.vue<br/>Parameter Form"]
    Upgrade --> UpgradeDrawer["upgrade/index.vue<br/>Version Selection"]
```

Each installed app card provides contextual actions based on app status and type.

Sources: [frontend/src/views/app-store/installed/index.vue:42-67](), [frontend/src/views/app-store/installed/detail/index.vue:1-20](), [frontend/src/views/app-store/installed/upgrade/index.vue:1-5]()

---

## Development Workflow

### Build Process

```mermaid
graph LR
    Dev["Developer"]
    
    Dev --> LocalDev["npm run dev<br/>Vite Dev Server"]
    LocalDev --> HMR["Hot Module Replacement<br/>Instant Updates"]
    
    Dev --> Build["npm run build<br/>Production Build"]
    Build --> TypeCheck["TypeScript Validation"]
    Build --> ViteBuild["Vite Optimization"]
    Build --> Dist["dist/<br/>Static Assets"]
    
    Dist --> Backend["Copy to<br/>backend/resources"]
    Backend --> Embed["Embedded in<br/>Go Binary"]
```

**Development Commands:**
- `npm run dev`: Start Vite development server with hot reload
- `npm run build`: Create production-optimized bundle
- `npm run type-check`: Validate TypeScript without building

### Component Development Pattern

When creating new components or pages:

1. **Create Vue file** in appropriate directory (`views/` or `components/`)
2. **Define TypeScript interfaces** in `api/interface/` for API data
3. **Add API functions** in `api/modules/` for backend communication
4. **Add translations** to all language files in `lang/modules/`
5. **Use form-rules.ts** validators for input validation
6. **Follow LayoutContent pattern** for page structure
7. **Test with multiple languages** to ensure i18n compatibility

Sources: [Makefile:1-20]() (build process), [frontend/src/views/]() (component examples)

---

## Summary

The 1Panel frontend is a modern Vue 3 application with:

- **Type-safe API layer** using TypeScript interfaces
- **Comprehensive i18n support** for 10 languages
- **Reusable component patterns** via LayoutContent and shared components
- **Centralized validation** through form-rules.ts
- **Efficient build system** using Vite with hot module replacement
- **Consistent UI/UX** powered by Element Plus
- **Code editing capabilities** via integrated Monaco Editor

The architecture emphasizes maintainability through clear separation of concerns, type safety, and extensive code reuse across features.

---

# Page: Component Architecture and Patterns

# Component Architecture and Patterns

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [frontend/src/api/interface/app.ts](frontend/src/api/interface/app.ts)
- [frontend/src/api/interface/file.ts](frontend/src/api/interface/file.ts)
- [frontend/src/api/modules/app.ts](frontend/src/api/modules/app.ts)
- [frontend/src/api/modules/files.ts](frontend/src/api/modules/files.ts)
- [frontend/src/components/app-status/index.vue](frontend/src/components/app-status/index.vue)
- [frontend/src/global/form-rules.ts](frontend/src/global/form-rules.ts)
- [frontend/src/styles/common.scss](frontend/src/styles/common.scss)
- [frontend/src/views/app-store/apps/index.vue](frontend/src/views/app-store/apps/index.vue)
- [frontend/src/views/app-store/detail/index.vue](frontend/src/views/app-store/detail/index.vue)
- [frontend/src/views/app-store/detail/install/index.vue](frontend/src/views/app-store/detail/install/index.vue)
- [frontend/src/views/app-store/detail/params/index.vue](frontend/src/views/app-store/detail/params/index.vue)
- [frontend/src/views/app-store/installed/detail/index.vue](frontend/src/views/app-store/installed/detail/index.vue)
- [frontend/src/views/app-store/installed/index.vue](frontend/src/views/app-store/installed/index.vue)
- [frontend/src/views/app-store/installed/upgrade/index.vue](frontend/src/views/app-store/installed/upgrade/index.vue)
- [frontend/src/views/host/file-management/code-editor/index.vue](frontend/src/views/host/file-management/code-editor/index.vue)
- [frontend/src/views/host/file-management/index.vue](frontend/src/views/host/file-management/index.vue)
- [frontend/src/views/website/website/create/index.vue](frontend/src/views/website/website/create/index.vue)
- [frontend/src/views/website/website/index.vue](frontend/src/views/website/website/index.vue)

</details>



This document describes the Vue 3 component architecture used throughout the 1Panel frontend, including reusable components, common patterns, and communication strategies. It focuses on the structural patterns, component hierarchies, and coding conventions that ensure consistency across the application.

For API client architecture and TypeScript interfaces, see [API Client Layer and Type System](#11.2). For form validation utilities, see [Form Validation and Utilities](#11.3).

---

## Component Hierarchy Overview

The frontend implements a three-tier component structure: layout components for structural organization, shared components for common functionality, and page components for feature-specific UI.

```mermaid
graph TB
    App["App.vue<br/>(Root)"]
    
    subgraph "Layout Layer"
        LayoutContent["LayoutContent<br/>Main page wrapper"]
        DrawerPro["DrawerPro<br/>Side panel"]
        DialogPro["DialogPro<br/>Modal dialog"]
        MainDiv["MainDiv<br/>Scrollable content"]
    end
    
    subgraph "Shared Components"
        ComplexTable["ComplexTable<br/>Advanced table with pagination"]
        AppStatus["AppStatus<br/>App service status display"]
        Status["Status<br/>Status indicator"]
        TaskLog["TaskLog<br/>Task log viewer"]
        CodeEditor["CodeEditor (Monaco)<br/>File editor with tabs"]
        FormComponents["Form Components<br/>GroupSelect, DomainCreate, etc."]
    end
    
    subgraph "Page Components"
        FileManagement["FileManagement<br/>Multi-tab file browser"]
        AppInstalled["AppInstalled<br/>Installed apps list"]
        WebsiteIndex["WebsiteIndex<br/>Website management"]
        AppStore["AppStore<br/>App catalog"]
    end
    
    App --> LayoutContent
    App --> DrawerPro
    App --> DialogPro
    
    LayoutContent --> ComplexTable
    LayoutContent --> AppStatus
    
    DrawerPro --> FormComponents
    DialogPro --> CodeEditor
    
    FileManagement --> LayoutContent
    FileManagement --> ComplexTable
    FileManagement --> CodeEditor
    
    AppInstalled --> LayoutContent
    AppInstalled --> ComplexTable
    AppInstalled --> TaskLog
    
    WebsiteIndex --> LayoutContent
    WebsiteIndex --> AppStatus
    WebsiteIndex --> ComplexTable
    
    AppStore --> LayoutContent
    AppStore --> TaskLog
```

**Sources:** [frontend/src/views/host/file-management/index.vue:1-625](), [frontend/src/views/app-store/installed/index.vue:1-469](), [frontend/src/views/website/website/index.vue:1-689](), [frontend/src/components/app-status/index.vue:1-196]()

---

## Layout Components

### LayoutContent Component

The `LayoutContent` component provides the standard page structure with header, toolbar sections, and main content area. It's used consistently across all major feature pages.

**Usage Pattern:**
```vue
<LayoutContent v-loading="loading" :title="$t('menu.website')">
    <template #app>
        <!-- App status banner -->
    </template>
    <template #leftToolBar>
        <!-- Create/action buttons -->
    </template>
    <template #rightToolBar>
        <!-- Search/filter controls -->
    </template>
    <template #main>
        <!-- Main content area -->
    </template>
</LayoutContent>
```

**Common Slots:**
- `#app` - Application status indicator (typically `AppStatus` component)
- `#prompt` - Alert/information banner
- `#search` - Search/tag filters
- `#leftToolBar` - Primary action buttons
- `#rightToolBar` - Secondary controls and filters
- `#main` - Primary content area
- `#footer` - Footer content

**Sources:** [frontend/src/views/website/website/index.vue:11-281](), [frontend/src/views/app-store/installed/index.vue:2-103](), [frontend/src/views/app-store/apps/index.vue:4-63]()

### DrawerPro Component

`DrawerPro` is the standard side panel component for forms and detail views. It implements a consistent header with custom buttons and footer for actions.

**Component Structure:**
```mermaid
graph LR
    DrawerPro["DrawerPro"]
    Header["#header<br/>Title + custom buttons"]
    Content["#content<br/>Form/details"]
    Footer["#footer<br/>Action buttons"]
    
    DrawerPro --> Header
    DrawerPro --> Content
    DrawerPro --> Footer
```

**Key Props:**
- `v-model` - Controls open/close state
- `header` - Drawer title (i18n key)
- `size` - Width: "small", "normal", "large", "w-70"
- `@close` - Close event handler

**Common Pattern:**
```vue
<DrawerPro v-model="open" :header="$t('app.param')" @close="handleClose" size="normal">
    <template #buttons>
        <el-button type="primary" @click="editParam">
            {{ $t('commons.button.edit') }}
        </el-button>
    </template>
    <!-- Content -->
    <template #footer>
        <el-button @click="handleClose">{{ $t('commons.button.cancel') }}</el-button>
        <el-button type="primary" @click="submit">{{ $t('commons.button.confirm') }}</el-button>
    </template>
</DrawerPro>
```

**Sources:** [frontend/src/views/app-store/installed/detail/index.vue:1-179](), [frontend/src/views/website/website/create/index.vue:1-411](), [frontend/src/views/app-store/installed/upgrade/index.vue:1-271]()

### DialogPro Component

Similar to `DrawerPro`, but for modal dialogs. Used primarily for the code editor and other full-screen interactions.

**Sources:** [frontend/src/views/host/file-management/code-editor/index.vue:2-9]()

---

## Shared UI Components

### ComplexTable Component

`ComplexTable` is a feature-rich table wrapper around Element Plus's `el-table` with built-in pagination, sorting, selection, and dynamic column visibility.

```mermaid
graph TB
    ComplexTable["ComplexTable"]
    
    subgraph "Features"
        Pagination["Pagination<br/>v-model:currentPage/pageSize"]
        Selection["Selection<br/>v-model:selects"]
        Sorting["Sorting<br/>@sort-change"]
        ColumnToggle["Column Visibility<br/>localKey storage"]
        Actions["Row Actions<br/>fu-table-operations"]
    end
    
    ComplexTable --> Pagination
    ComplexTable --> Selection
    ComplexTable --> Sorting
    ComplexTable --> ColumnToggle
    ComplexTable --> Actions
```

**Key Props:**
- `:data` - Table data array
- `:pagination-config` - Pagination configuration object
- `v-model:selects` - Selected rows (for batch operations)
- `:columns` - Column definitions for dynamic visibility
- `@sort-change` - Sort event handler
- `:heightDiff` - Dynamic height calculation
- `localKey` - LocalStorage key for column preferences

**Usage Example:**
```vue
<ComplexTable
    :pagination-config="paginationConfig"
    v-model:selects="selects"
    :data="data"
    @search="search"
    @sort-change="changeSort"
    :heightDiff="310"
    :columns="columns"
    localKey="websiteColumn"
>
    <el-table-column type="selection" width="30" />
    <el-table-column :label="$t('commons.table.name')" prop="primaryDomain" sortable />
    <!-- More columns -->
    <fu-table-operations :buttons="buttons" />
</ComplexTable>
```

**Sources:** [frontend/src/views/website/website/index.vue:70-265](), [frontend/src/views/host/file-management/index.vue:448-603](), [frontend/src/views/app-store/installed/index.vue:19-91]()

### AppStatus Component

Displays application service status with start/stop/restart controls. Automatically checks and updates service status.

**Component Interface:**
```typescript
interface Props {
    appKey: string;        // 'openresty', 'mysql', etc.
    appName?: string;      // Optional specific install name
    hideSetting?: boolean; // Hide settings button
}

interface Emits {
    'setting': void;
    'isExist': CheckInstalled;
    'update:loading': boolean;
    'update:maskShow': boolean;
    'update:appInstallID': number;
}

interface Exposed {
    onCheck: (key: string, name: string) => void;
    getHttpPort: () => number;
    getHttpsPort: () => number;
}
```

**Visual Structure:**
- Service name badge (e.g., "OpenResty")
- Status indicator (Running/Stopped/Installing)
- Version tag
- Action buttons: Start, Stop, Restart, Reload (for OpenResty), Settings

**Sources:** [frontend/src/components/app-status/index.vue:1-196](), [frontend/src/views/website/website/index.vue:12-20]()

### Status Component

Simple status indicator component displaying colored status text. Used throughout the application for consistent status display.

**Common Statuses:**
- `Running` - Green
- `Stopped` - Gray
- `Error` - Red
- `Installing` - Blue

**Sources:** [frontend/src/components/app-status/index.vue:7](), [frontend/src/views/website/website/index.vue:146-158]()

---

## Component Communication Patterns

The application uses four primary communication strategies depending on the relationship between components.

```mermaid
graph TB
    subgraph "Parent-Child"
        Parent["Parent Component"]
        Child["Child Component"]
        Parent -->|":props"| Child
        Child -->|"@emits"| Parent
    end
    
    subgraph "Template Refs"
        ParentRef["Parent with ref"]
        ChildRef["Child with defineExpose"]
        ParentRef -->|"ref.method()"| ChildRef
    end
    
    subgraph "Event Bus"
        CompA["Component A"]
        Bus["Global Event Bus<br/>bus.emit()"]
        CompB["Component B"]
        CompA -->|"emit"| Bus
        Bus -->|"on"| CompB
    end
    
    subgraph "Global Store"
        CompX["Any Component"]
        Store["Pinia Store<br/>useGlobalStore()"]
        CompY["Any Component"]
        CompX -->|"read/write"| Store
        Store -->|"reactive"| CompY
    end
```

**Sources:** [frontend/src/views/app-store/installed/index.vue:118-146](), [frontend/src/components/app-status/index.vue:117-128]()

### Props and Emits Pattern

Standard Vue 3 props/emits for parent-child communication with TypeScript type safety.

**Example from AppStatus:**
```typescript
// Props definition
const props = defineProps({
    appKey: { type: String, default: 'openresty' },
    appName: { type: String, default: '' },
    hideSetting: { type: Boolean, default: false },
});

// Emits definition
const em = defineEmits([
    'setting',
    'isExist',
    'update:loading',
    'update:maskShow',
]);

// Usage
em('isExist', res.data);
em('update:maskShow', res.data.status !== 'Running');
```

**Sources:** [frontend/src/components/app-status/index.vue:82-125]()

### Template Refs and defineExpose Pattern

The most common pattern for calling child component methods is the `acceptParams` pattern with template refs.

**Child Component (Drawer/Dialog):**
```typescript
const open = ref(false);

const acceptParams = (props: SomeProps) => {
    // Initialize component state
    data.value = props.data;
    open.value = true;
};

defineExpose({
    acceptParams,
});
```

**Parent Component:**
```typescript
const childRef = ref();

const openChild = (data: any) => {
    childRef.value.acceptParams({ data });
};
```

**Usage in Template:**
```vue
<ChildComponent ref="childRef" @close="handleClose" />
```

**Sources:** [frontend/src/views/app-store/installed/index.vue:189-192](), [frontend/src/views/app-store/detail/index.vue:97-102](), [frontend/src/views/app-store/installed/detail/index.vue:286-296]()

### Event Bus Pattern

Used for cross-component communication, especially for refresh/update events.

**Setup (global/bus.ts):**
```typescript
import mitt from 'mitt';
const bus = mitt();
export default bus;
```

**Emitting Events:**
```typescript
import bus from '@/global/bus';

// Trigger refresh in other components
bus.emit('upgrade', true);
bus.emit('refreshApp');
```

**Listening for Events:**
```typescript
onMounted(() => {
    bus.on('refreshApp', () => {
        search(req);
    });
});

onUnmounted(() => {
    bus.off('refreshApp');
});
```

**Sources:** [frontend/src/views/app-store/apps/index.vue:80-81](), [frontend/src/views/app-store/apps/index.vue:230-232](), [frontend/src/views/app-store/installed/upgrade/index.vue:94]()

### Global Store Pattern

Pinia store used for application-wide state like current node, authentication, and theme.

**Store Access:**
```typescript
import { useGlobalStore } from '@/composables/useGlobalStore';
const { currentNode, isMaster, isProductPro, globalStore } = useGlobalStore();

// Access reactive values
const nodeAddress = currentNode.value;
const isMobile = computed(() => globalStore.isMobile());
```

**Common Global State:**
- `currentNode` - Active server node identifier
- `currentNodeAddr` - Node IP address
- `isMaster` - Is this the master node
- `isProductPro` - Pro edition flag
- `isOffLine` - Offline mode flag

**Sources:** [frontend/src/views/app-store/installed/index.vue:146](), [frontend/src/views/app-store/apps/index.vue:88](), [frontend/src/composables/useGlobalStore]()

---

## Common Component Patterns

### The acceptParams Pattern

A standardized method for initializing drawer and dialog components. This pattern is used consistently across all modal interfaces.

**Pattern Structure:**
```typescript
interface ComponentParams {
    id: number;
    // other props
}

const open = ref(false);
const loading = ref(false);
const data = ref<DataType>();

const acceptParams = async (params: ComponentParams) => {
    // 1. Reset state
    data.value = null;
    loading.value = false;
    
    // 2. Store params
    componentId.value = params.id;
    
    // 3. Fetch data if needed
    await loadData(params.id);
    
    // 4. Open component
    open.value = true;
};

const handleClose = () => {
    open.value = false;
    emit('close');
};

defineExpose({
    acceptParams,
});
```

**Real Examples:**

| Component | Params | Purpose |
|-----------|--------|---------|
| AppParams Detail | `{ id: number }` | View/edit app parameters |
| Website Create | `nginxVersion: string` | Create new website |
| App Install | `{ app: App.App }` | Install application |
| App Upgrade | `AppInstallDto, operation` | Upgrade/ignore app |
| TaskLog | `taskID: string` | View task execution log |

**Sources:** [frontend/src/views/app-store/installed/detail/index.vue:286-296](), [frontend/src/views/website/website/create/index.vue:583-599](), [frontend/src/views/app-store/detail/install/index.vue:127-134](), [frontend/src/views/app-store/installed/upgrade/index.vue:169-189]()

### Form Validation Pattern

Consistent form handling with Element Plus forms and centralized validation rules.

**Form Setup:**
```typescript
import { Rules, checkNumberRange } from '@/global/form-rules';

const formRef = ref<FormInstance>();

const form = reactive({
    name: '',
    port: 3306,
    password: '',
});

const rules = reactive({
    name: [Rules.requiredInput, Rules.name],
    port: [Rules.requiredInput, Rules.port],
    password: [Rules.requiredInput, Rules.paramComplexity],
    cpuQuota: [checkNumberRange(0, 999)],
});

const submit = async (formEl: FormInstance | undefined) => {
    if (!formEl) return;
    await formEl.validate((valid) => {
        if (valid) {
            // Submit form
        }
    });
};
```

**Common Rules from Rules Object:**
- `Rules.requiredInput` - Required text field
- `Rules.requiredSelect` - Required select dropdown
- `Rules.port` - Port number validation (1-65535)
- `Rules.ip` - IP address validation
- `Rules.domain` - Domain name validation
- `Rules.paramComplexity` - Password complexity
- `checkNumberRange(min, max)` - Number range validator

**Sources:** [frontend/src/global/form-rules.ts:1-488](), [frontend/src/views/app-store/installed/detail/index.vue:214-223](), [frontend/src/views/website/website/create/index.vue:519-548]()

### Multi-Tab Interface Pattern

Used extensively in file management and code editor for managing multiple contexts simultaneously.

**Tab State Management:**
```typescript
interface TabItem {
    id: string;
    name: string;
    path: string;
    // other properties
}

const editableTabs = ref<TabItem[]>([
    { id: '1', name: '', path: '/' }
]);
const editableTabsKey = ref('1');

const addTab = () => {
    const newTabId = Date.now().toString();
    editableTabs.value.push({
        id: newTabId,
        name: '',
        path: '/'
    });
    editableTabsKey.value = newTabId;
};

const removeTab = (targetId: string) => {
    const tabs = editableTabs.value;
    let activeName = editableTabsKey.value;
    
    if (activeName === targetId) {
        tabs.forEach((tab, index) => {
            if (tab.id === targetId) {
                const nextTab = tabs[index + 1] || tabs[index - 1];
                if (nextTab) {
                    activeName = nextTab.id;
                }
            }
        });
    }
    
    editableTabsKey.value = activeName;
    editableTabs.value = tabs.filter(tab => tab.id !== targetId);
};

const changeTab = (targetId: string) => {
    // Switch context to selected tab
    const tab = editableTabs.value.find(t => t.id === targetId);
    if (tab) {
        // Load tab-specific data
    }
};
```

**Usage in Template:**
```vue
<el-tabs
    type="card"
    v-model="editableTabsKey"
    @tab-change="changeTab"
    @tab-remove="removeTab"
>
    <el-tab-pane
        closable
        v-for="item in editableTabs"
        :key="item.id"
        :label="item.name"
        :name="item.id"
    >
        <!-- Tab content -->
    </el-tab-pane>
    <el-tab-pane :name="editableTabsKey" :closable="false" :disabled="editableTabs.length > 6">
        <template #label>
            <el-icon @click="addTab()"><Plus /></el-icon>
        </template>
    </el-tab-pane>
</el-tabs>
```

**File Management Implementation:**
The file manager uses tabs to allow browsing multiple directories simultaneously, with each tab maintaining its own:
- Current path
- File list
- Search state
- Selection state

**Code Editor Implementation:**
The code editor supports up to 10 file tabs, each with:
- File path and content
- Monaco editor instance
- Unsaved changes tracking
- Language mode

**Sources:** [frontend/src/views/host/file-management/index.vue:3-612](), [frontend/src/views/host/file-management/code-editor/index.vue:1-680]()

### Loading and Async State Pattern

Consistent handling of loading states and async operations.

**Basic Loading Pattern:**
```typescript
const loading = ref(false);
const data = ref([]);

const search = async () => {
    loading.value = true;
    try {
        const res = await searchAPI(params);
        data.value = res.data.items;
    } finally {
        loading.value = false;
    }
};
```

**With v-loading Directive:**
```vue
<LayoutContent v-loading="loading">
    <!-- Content -->
</LayoutContent>
```

**Task-based Async Operations:**
For long-running operations, the application uses a task ID pattern with task log streaming:

```typescript
import { newUUID } from '@/utils/util';

const taskLogRef = ref();

const performOperation = async () => {
    const taskID = newUUID();
    
    await apiCall({
        // operation params
        taskID: taskID
    });
    
    // Open task log viewer
    taskLogRef.value.openWithTaskID(taskID);
};
```

**Sources:** [frontend/src/views/app-store/installed/index.vue:202-211](), [frontend/src/views/app-store/apps/index.vue:175-198](), [frontend/src/views/website/website/index.vue:443-457]()

### Pagination Configuration Pattern

Standardized pagination setup with localStorage persistence.

```typescript
const paginationConfig = reactive({
    cacheSizeKey: 'website-page-size',
    currentPage: 1,
    pageSize: Number(localStorage.getItem('website-page-size')) || 20,
    total: 0,
});

const search = async () => {
    req.page = paginationConfig.currentPage;
    req.pageSize = paginationConfig.pageSize;
    
    // Save to localStorage
    localStorage.setItem('website-page-size', String(req.pageSize));
    
    const res = await searchAPI(req);
    data.value = res.data.items;
    paginationConfig.total = res.data.total;
};
```

**Sources:** [frontend/src/views/website/website/index.vue:377-391](), [frontend/src/views/app-store/installed/index.vue:152-157](), [frontend/src/views/app-store/apps/index.vue:94-99]()

---

## Page Component Patterns

### CRUD Operation Flow

Standard pattern for Create, Read, Update, Delete operations across resource management pages.

```mermaid
sequenceDiagram
    participant User
    participant PageComponent
    participant CreateDrawer
    participant API
    participant TaskLog
    
    Note over User,TaskLog: Create Flow
    User->>PageComponent: Click create button
    PageComponent->>CreateDrawer: ref.acceptParams()
    CreateDrawer->>CreateDrawer: Open drawer, initialize form
    User->>CreateDrawer: Fill form, submit
    CreateDrawer->>API: POST /resource (with taskID)
    API-->>CreateDrawer: taskID
    CreateDrawer->>PageComponent: @close event
    CreateDrawer->>TaskLog: openWithTaskID()
    TaskLog->>TaskLog: Stream task progress
    
    Note over User,TaskLog: Update Flow
    User->>PageComponent: Click edit button
    PageComponent->>CreateDrawer: ref.acceptParams(id)
    CreateDrawer->>API: GET /resource/:id
    API-->>CreateDrawer: resource data
    CreateDrawer->>CreateDrawer: Populate form
    User->>CreateDrawer: Modify, submit
    CreateDrawer->>API: PUT /resource/:id
    API-->>CreateDrawer: success
    CreateDrawer->>PageComponent: @close event
    PageComponent->>PageComponent: search() - refresh list
    
    Note over User,TaskLog: Delete Flow
    User->>PageComponent: Click delete button
    PageComponent->>PageComponent: ElMessageBox.confirm()
    User->>PageComponent: Confirm
    PageComponent->>API: DELETE /resource/:id
    API-->>PageComponent: success
    PageComponent->>PageComponent: search() - refresh list
```

**Sources:** [frontend/src/views/website/website/index.vue:597-607](), [frontend/src/views/app-store/installed/index.vue:229-246]()

### List Page Pattern

Standard structure for resource list pages with search, filter, and batch operations.

**Component Structure:**
```
ListPage/
├── Search/Filter Bar (leftToolBar/rightToolBar)
├── ComplexTable
│   ├── Selection Column
│   ├── Data Columns
│   └── Operations Column
└── Batch Operation Bar (footerLeft)
```

**Key Features:**
- **Search**: Name/keyword search
- **Filters**: Type, group, status dropdowns
- **Sorting**: Click column headers
- **Selection**: Checkbox for batch operations
- **Actions**: Per-row operations (edit, delete, etc.)
- **Batch Operations**: Apply operation to selected rows

**Batch Operations Implementation:**
```typescript
const selects = ref([]);
const batchReq = reactive({
    operate: '',
    ids: [] as number[],
});

const batchOp = () => {
    batchReq.ids = selects.value.map(item => item.id);
    
    ElMessageBox.confirm(
        i18n.global.t('website.batchOpreateHelper', [batchReq.operate]),
        i18n.global.t('website.batchOpreate'),
        { /* ... */ }
    ).then(() => {
        batchOperateAPI(batchReq).then(() => {
            MsgSuccess(i18n.global.t('commons.msg.operationSuccess'));
            selects.value = [];
            search();
        });
    });
};
```

**Sources:** [frontend/src/views/website/website/index.vue:232-263](), [frontend/src/views/app-store/installed/index.vue:18-101]()

### Detail/Edit Drawer Pattern

Drawers that switch between read-only and edit modes.

**Mode Toggle:**
```typescript
const edit = ref(false);
const params = ref<EditForm[]>([]);

const editParam = () => {
    if (!edit.value) {
        // Switch to edit mode
        params.value.forEach(param => {
            paramModel.params[param.key] = param.value;
        });
    }
    edit.value = !edit.value;
};
```

**Conditional Rendering:**
```vue
<template #buttons>
    <el-button @click="editParam" :icon="edit ? '' : 'Edit'">
        {{ edit ? $t('app.detail') : $t('commons.button.edit') }}
    </el-button>
</template>

<div v-if="!edit">
    <!-- Read-only view with el-descriptions -->
    <el-descriptions border>
        <el-descriptions-item :label="getLabel(param)">
            {{ param.value }}
        </el-descriptions-item>
    </el-descriptions>
</div>

<div v-else>
    <!-- Edit mode with el-form -->
    <el-form :model="paramModel" :rules="rules">
        <el-form-item :prop="'params.' + p.key">
            <el-input v-model="paramModel.params[p.key]" />
        </el-form-item>
    </el-form>
</div>
```

**Sources:** [frontend/src/views/app-store/installed/detail/index.vue:1-434]()

---

## Form Component Patterns

### Dynamic Form Fields

Form fields generated from API metadata, commonly used in app installation and configuration.

**Metadata-Driven Forms:**
```typescript
interface FromField {
    type: string;           // 'text', 'number', 'password', 'select', 'service'
    labelZh: string;
    labelEn: string;
    required: boolean;
    default: any;
    envKey: string;
    values?: ServiceParam[];
}

// Generate form from metadata
const handleParams = () => {
    if (params.value?.formFields) {
        for (const p of params.value.formFields) {
            form[p.envKey] = p.default;
            
            if (p.required) {
                if (p.type === 'service') {
                    rules[p.envKey] = [Rules.requiredSelect];
                } else {
                    rules[p.envKey] = [Rules.requiredInput];
                }
            }
            
            if (p.type === 'service') {
                getServices(p.envKey, p.key);
            }
        }
    }
};
```

**Template Rendering:**
```vue
<div v-for="(p, index) in paramObjs" :key="index">
    <el-form-item :label="getLabel(p)" :prop="p.prop">
        <el-input v-if="p.type == 'text'" v-model="form[p.envKey]" />
        <el-input v-if="p.type == 'number'" v-model.number="form[p.envKey]" />
        <el-input v-if="p.type == 'password'" v-model="form[p.envKey]" show-password />
        <el-select v-if="p.type == 'select'" v-model="form[p.envKey]">
            <el-option v-for="opt in p.values" :key="opt.value" :label="opt.label" :value="opt.value" />
        </el-select>
    </el-form-item>
</div>
```

**Sources:** [frontend/src/views/app-store/detail/params/index.vue:1-306](), [frontend/src/views/website/website/create/index.vue:1-878]()

### Nested Form Components

Complex forms decomposed into reusable sub-components.

**Component Hierarchy:**
```
WebsiteCreate/
├── SSLAlert (validation warnings)
├── GroupSelect (website group selector)
├── DomainCreate (domain configuration)
├── AppInstallForm (app installation params)
├── LoadBalanceForm (load balancer config)
└── WebsiteSSL (SSL certificate display)
```

**Sub-component Integration:**
```vue
<GroupSelect
    v-model="website.webSiteGroupId"
    :prop="'webSiteGroupId'"
    :groupType="'website'"
/>

<AppInstallForm 
    ref="installFormRef" 
    v-model="website.appinstall" 
    :loading="loading" 
/>

<DomainCreate 
    v-model:form="website" 
    @gengerate="websiteForm.clearValidate()"
/>
```

**v-model Pattern for Sub-components:**
```typescript
// Child component
const props = defineProps({
    modelValue: Object
});

const emit = defineEmits(['update:modelValue']);

const updateValue = () => {
    emit('update:modelValue', localForm.value);
};

// Parent usage
<SubComponent v-model="parentForm" />
```

**Sources:** [frontend/src/views/website/website/create/index.vue:19-411]()

### Conditional Form Sections

Forms with sections that appear/disappear based on selections.

**Example - Website Type Conditional Rendering:**
```vue
<el-form-item>
    <el-radio-group v-model="website.type" @change="changeType">
        <el-radio-button value="deployment">{{ $t('website.deployment') }}</el-radio-button>
        <el-radio-button value="runtime">{{ $t('website.runtime') }}</el-radio-button>
        <el-radio-button value="proxy">{{ $t('website.proxy') }}</el-radio-button>
    </el-radio-group>
</el-form-item>

<!-- Deployment-specific fields -->
<div v-if="website.type === 'deployment'">
    <el-form-item prop="appInstallId">
        <el-select v-model="website.appInstallId">
            <!-- options -->
        </el-select>
    </el-form-item>
</div>

<!-- Runtime-specific fields -->
<div v-if="website.type === 'runtime'">
    <el-form-item prop="runtimeType">
        <el-select v-model="website.runtimeType" @change="changeRuntimeType()">
            <el-option label="PHP" value="php" />
            <el-option label="Node.js" value="node" />
        </el-select>
    </el-form-item>
</div>

<!-- Proxy-specific fields -->
<el-row v-if="website.type === 'proxy'">
    <el-form-item prop="proxyAddress">
        <el-input v-model="website.proxyAddress" />
    </el-form-item>
</el-row>
```

**Sources:** [frontend/src/views/website/website/create/index.vue:14-318]()

---

## Advanced Patterns

### File Manager Tab System

The file manager implements a sophisticated multi-tab system where each tab maintains independent state.

```mermaid
graph TB
    FileManager["File Management Component"]
    
    subgraph "Tab State"
        TabArray["editableTabs[]<br/>Array of tab configs"]
        ActiveTab["editableTabsKey<br/>Current active tab ID"]
    end
    
    subgraph "Per-Tab State"
        PathRefs["pathRef Map<br/>Path input elements"]
        TableRefs["tableRef Map<br/>Table components"]
        SearchInputRefs["searchableInputRef Map<br/>Search inputs"]
        RenameRefs["renameRef Map<br/>Rename input refs"]
        BtnRefs["btnWrapperRef Map<br/>Button containers"]
    end
    
    subgraph "Operations"
        Search["search() per tab"]
        Navigation["jump(path) navigation"]
        Selection["selects per tab"]
    end
    
    FileManager --> TabArray
    FileManager --> ActiveTab
    
    TabArray --> PathRefs
    TabArray --> TableRefs
    TabArray --> SearchInputRefs
    
    ActiveTab --> Search
    ActiveTab --> Navigation
    ActiveTab --> Selection
```

**Ref Map Implementation:**
```typescript
const pathRefs = new Map();
const tableRefs = new Map();
const searchableInputRefs = new Map();

const setPathRef = (tabId: string, el: any) => {
    if (el) {
        pathRefs.set(tabId, el);
    }
};

const setTableRef = (tabId: string, el: any) => {
    if (el) {
        tableRefs.set(tabId, el);
    }
};

// In template
<div :ref="(el) => setPathRef(item.id, el)">
    <!-- Path display -->
</div>

<ComplexTable :ref="(el) => setTableRef(item.id, el)" />
```

**Tab-Specific Data Management:**
```typescript
const editableTabs = ref([
    { id: '1', name: '', req: { path: '/', page: 1, pageSize: 100 } }
]);

const getCurrentTab = () => {
    return editableTabs.value.find(t => t.id === editableTabsKey.value);
};

const search = () => {
    const currentTab = getCurrentTab();
    if (!currentTab) return;
    
    // Use tab-specific request params
    getFilesList(currentTab.req).then(res => {
        data.value = res.data.items;
    });
};
```

**Sources:** [frontend/src/views/host/file-management/index.vue:1-674]()

### Code Editor Multi-File Management

The code editor manages up to 10 open files simultaneously with Monaco editor instances.

**File Tab State:**
```typescript
interface FileTab {
    id: string;
    name: string;
    path: string;
    content: string;
    language: string;
    extension: string;
    isModified: boolean;
}

const fileTabs = ref<FileTab[]>([]);
const selectTab = ref<FileTab | null>(null);
const maxTabs = 10;

const addTab = (path: string, extension: string) => {
    if (fileTabs.value.length >= maxTabs) {
        MsgError(i18n.global.t('file.maxTabsReached', [maxTabs]));
        return;
    }
    
    const existingTab = fileTabs.value.find(t => t.path === path);
    if (existingTab) {
        selectTab.value = existingTab;
        return;
    }
    
    const newTab: FileTab = {
        id: Date.now().toString(),
        name: path.split('/').pop() || '',
        path: path,
        content: '',
        language: getLanguageFromExtension(extension),
        extension: extension,
        isModified: false
    };
    
    fileTabs.value.push(newTab);
    selectTab.value = newTab;
};
```

**Content Loading and Caching:**
```typescript
const getContent = async (path: string, extension: string) => {
    const existingTab = fileTabs.value.find(t => t.path === path);
    
    if (existingTab) {
        // Tab already open, switch to it
        selectTab.value = existingTab;
        return;
    }
    
    // Load content from server
    loading.value = true;
    try {
        const res = await getFileContent({ path: path });
        addTab(path, extension);
        
        const tab = fileTabs.value.find(t => t.path === path);
        if (tab) {
            tab.content = res.data.content;
        }
    } finally {
        loading.value = false;
    }
};
```

**Unsaved Changes Tracking:**
```typescript
const saveContent = async () => {
    if (!selectTab.value) return;
    
    loading.value = true;
    try {
        await saveFileContent({
            path: selectTab.value.path,
            content: selectTab.value.content
        });
        
        selectTab.value.isModified = false;
        MsgSuccess(i18n.global.t('commons.msg.saveSuccess'));
    } finally {
        loading.value = false;
    }
};

const handleReset = () => {
    if (selectTab.value) {
        // Reload from server
        getContent(selectTab.value.path, selectTab.value.extension);
    }
};
```

**Sources:** [frontend/src/views/host/file-management/code-editor/index.vue:1-680]()

### Responsive Button Overflow Management

Dynamic button visibility based on available space, common in toolbar areas.

**Pattern Implementation:**
```typescript
const visibleButtons = ref([]);
const moreButtons = ref([]);

const buttons = [
    { label: 'commons.button.compress', action: () => compress() },
    { label: 'commons.button.decompress', action: () => decompress() },
    { label: 'commons.button.copy', action: () => copy() },
    { label: 'commons.button.move', action: () => move() },
    { label: 'commons.button.download', action: () => download() },
    { label: 'commons.button.delete', action: () => deleteFiles() },
];

const calculateVisibleButtons = () => {
    const containerWidth = toolbarRef.value?.offsetWidth || 0;
    const buttonWidth = 100; // Approximate
    const maxVisible = Math.floor(containerWidth / buttonWidth);
    
    visibleButtons.value = buttons.slice(0, maxVisible);
    moreButtons.value = buttons.slice(maxVisible);
};

onMounted(() => {
    calculateVisibleButtons();
    window.addEventListener('resize', calculateVisibleButtons);
});
```

**Template Structure:**
```vue
<template v-if="visibleButtons.length > 0">
    <el-button-group>
        <el-button 
            v-for="btn in visibleButtons" 
            :key="btn.label"
            @click="btn.action"
            :disabled="selects.length === 0"
        >
            {{ $t(btn.label) }}
        </el-button>
        
        <el-dropdown v-if="moreButtons.length">
            <el-button>
                {{ $t('tabs.more') }}
                <el-icon><arrow-down /></el-icon>
            </el-button>
            <template #dropdown>
                <el-dropdown-menu>
                    <el-dropdown-item 
                        v-for="btn in moreButtons"
                        @click="btn.action"
                    >
                        {{ $t(btn.label) }}
                    </el-dropdown-item>
                </el-dropdown-menu>
            </template>
        </el-dropdown>
    </el-button-group>
</template>
```

**Sources:** [frontend/src/views/host/file-management/index.vue:356-406]()

---

## Styling and Theme Patterns

### Dark Mode Support

Components use CSS variables for theme-aware styling.

**CSS Variable Usage:**
```scss
.code-header {
    background: var(--panel-main-bg-color-9);
    color: var(--el-text-color-primary);
}

.monaco-editor-background {
    background: var(--panel-main-bg-color-10);
}

.table-link {
    color: $primary-color;
    cursor: pointer;
    
    &:hover {
        opacity: 0.6;
    }
}
```

**Monaco Editor Theme Sync:**
```typescript
const config = reactive({
    theme: 'vs-dark', // or 'vs'
});

const changeTheme = (theme: string) => {
    config.theme = theme;
    monaco.editor.setTheme(theme);
    localStorage.setItem('code-theme', theme);
};
```

**Sources:** [frontend/src/styles/common.scss:1-392](), [frontend/src/views/host/file-management/code-editor/index.vue:32-99]()

### Responsive Design Patterns

Mobile-specific adjustments using computed properties.

```typescript
import { GlobalStore } from '@/store';
const globalStore = GlobalStore();

const mobile = computed(() => {
    return globalStore.isMobile();
});

// Conditional rendering
<div :class="mobile ? 'mobile-layout' : 'desktop-layout'">
    <!-- Content -->
</div>

// Conditional props
<ComplexTable 
    :ellipsis="mobile ? 0 : 2"
    :fixed="mobile ? false : 'right'"
/>

// Conditional column widths
<el-col 
    :xs="24" 
    :sm="12" 
    :md="8" 
    :lg="6"
>
    <!-- Responsive card -->
</el-col>
```

**Sources:** [frontend/src/views/website/website/index.vue:392-394](), [frontend/src/views/app-store/apps/index.vue:90-92]()

---

## Summary

The 1Panel frontend component architecture follows these key principles:

1. **Consistent Patterns**: `acceptParams` for modals, `ComplexTable` for lists, `LayoutContent` for pages
2. **Clear Communication**: Props/emits for parent-child, template refs for method calls, event bus for cross-component events, Pinia store for global state
3. **Separation of Concerns**: Reusable components, page-specific logic, shared utilities
4. **Type Safety**: TypeScript interfaces for all component props and emits
5. **Responsive Design**: Mobile-aware rendering and layout adjustments
6. **Theme Support**: CSS variables for dark/light mode compatibility
7. **Form Validation**: Centralized validation rules and consistent error handling
8. **Async Operations**: Task-based long-running operations with progress tracking

This architecture enables maintainability, reusability, and consistency across the entire application.

---

# Page: API Client Layer and Type System

# API Client Layer and Type System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [frontend/src/api/interface/app.ts](frontend/src/api/interface/app.ts)
- [frontend/src/api/interface/setting.ts](frontend/src/api/interface/setting.ts)
- [frontend/src/api/modules/app.ts](frontend/src/api/modules/app.ts)
- [frontend/src/api/modules/setting.ts](frontend/src/api/modules/setting.ts)
- [frontend/src/components/app-status/index.vue](frontend/src/components/app-status/index.vue)
- [frontend/src/global/form-rules.ts](frontend/src/global/form-rules.ts)
- [frontend/src/styles/common.scss](frontend/src/styles/common.scss)
- [frontend/src/views/app-store/apps/index.vue](frontend/src/views/app-store/apps/index.vue)
- [frontend/src/views/app-store/detail/index.vue](frontend/src/views/app-store/detail/index.vue)
- [frontend/src/views/app-store/detail/install/index.vue](frontend/src/views/app-store/detail/install/index.vue)
- [frontend/src/views/app-store/detail/params/index.vue](frontend/src/views/app-store/detail/params/index.vue)
- [frontend/src/views/app-store/installed/detail/index.vue](frontend/src/views/app-store/installed/detail/index.vue)
- [frontend/src/views/app-store/installed/index.vue](frontend/src/views/app-store/installed/index.vue)
- [frontend/src/views/app-store/installed/upgrade/index.vue](frontend/src/views/app-store/installed/upgrade/index.vue)
- [frontend/src/views/website/website/create/index.vue](frontend/src/views/website/website/create/index.vue)
- [frontend/src/views/website/website/index.vue](frontend/src/views/website/website/index.vue)

</details>



## Purpose and Scope

This document describes the frontend API client layer architecture and TypeScript type system in 1Panel. It covers the organization of API modules, type definitions, request/response patterns, and how components interact with backend services. For information about backend service architecture, see [2.3](#2.3). For frontend form validation, see [11.3](#11.3).

The API client layer provides:
- Type-safe HTTP communication with Core and Agent servers
- Centralized request/response handling
- Strongly-typed interfaces for all data models
- Multi-node routing support
- Timeout management for long-running operations
- Security patterns for sensitive data transmission

---

## API Client Architecture Overview

```mermaid
graph TB
    subgraph "Vue Components"
        AppInstalled["App Installed View<br/>installed/index.vue"]
        WebsiteView["Website View<br/>website/index.vue"]
        SettingsView["Settings View"]
    end
    
    subgraph "API Module Layer"
        AppModule["app.ts<br/>API Functions"]
        SettingModule["setting.ts<br/>API Functions"]
        WebsiteModule["website.ts<br/>API Functions"]
    end
    
    subgraph "HTTP Client Core"
        HTTPClient["http module<br/>Axios wrapper"]
        Interceptors["Request/Response<br/>Interceptors"]
        ErrorHandler["Error Handler"]
    end
    
    subgraph "Type System"
        AppInterface["app.ts<br/>App namespace"]
        SettingInterface["setting.ts<br/>Setting namespace"]
        CommonInterface["index.ts<br/>Common types"]
    end
    
    subgraph "Backend Services"
        CoreAPI["Core API<br/>:9999"]
        AgentAPI["Agent API<br/>:10000"]
    end
    
    AppInstalled -->|"searchAppInstalled()"|AppModule
    WebsiteView -->|"searchWebsites()"|WebsiteModule
    SettingsView -->|"getSettingInfo()"|SettingModule
    
    AppModule -->|"http.post()"|HTTPClient
    SettingModule -->|"http.get()/post()"|HTTPClient
    WebsiteModule -->|"http.post()"|HTTPClient
    
    AppModule -.->|"uses types"|AppInterface
    SettingModule -.->|"uses types"|SettingInterface
    
    HTTPClient -->|"adds headers<br/>operateNode"|Interceptors
    Interceptors -->|"timeout config"|ErrorHandler
    
    HTTPClient -->|"routes to"|CoreAPI
    HTTPClient -->|"routes to"|AgentAPI
    
    style HTTPClient fill:#f9f9f9
    style AppInterface fill:#e8f4f8
    style SettingInterface fill:#e8f4f8
```

**Sources**: [frontend/src/api/modules/app.ts:1-143](), [frontend/src/api/modules/setting.ts:1-223](), [frontend/src/api/interface/app.ts:1-365](), [frontend/src/api/interface/setting.ts:1-313]()

---

## API Module Organization

API functions are organized by domain into separate modules under `frontend/src/api/modules/`. Each module exports functions that wrap HTTP calls and use typed interfaces.

```mermaid
graph LR
    subgraph "API Modules Structure"
        direction TB
        ModulesDir["api/modules/"]
        
        ModulesDir --> AppTS["app.ts<br/>App management"]
        ModulesDir --> SettingTS["setting.ts<br/>Core settings"]
        ModulesDir --> WebsiteTS["website.ts<br/>Website ops"]
        ModulesDir --> DatabaseTS["database.ts<br/>DB management"]
        ModulesDir --> ContainerTS["container.ts<br/>Docker ops"]
        ModulesDir --> RuntimeTS["runtime.ts<br/>Runtime envs"]
    end
    
    subgraph "Interface Definitions"
        direction TB
        InterfaceDir["api/interface/"]
        
        InterfaceDir --> AppInt["app.ts<br/>App namespace"]
        InterfaceDir --> SettingInt["setting.ts<br/>Setting namespace"]
        InterfaceDir --> WebsiteInt["website.ts<br/>Website namespace"]
        InterfaceDir --> CommonInt["index.ts<br/>Common types"]
    end
    
    AppTS -.->|imports|AppInt
    SettingTS -.->|imports|SettingInt
    WebsiteTS -.->|imports|WebsiteInt
    
    AppTS -.->|imports|CommonInt
    SettingTS -.->|imports|CommonInt
```

**Sources**: [frontend/src/api/modules/app.ts:1-5](), [frontend/src/api/modules/setting.ts:1-8](), [frontend/src/api/interface/app.ts:1-365](), [frontend/src/api/interface/setting.ts:1-313]()

---

## TypeScript Namespace Organization

All API-related types are organized into namespaces that correspond to their domain. This provides clean separation and prevents naming conflicts.

### Common Types

```typescript
// Defined in api/interface/index.ts
interface ReqPage {
    page: number;
    pageSize: number;
}

interface ResPage<T> {
    items: T[];
    total: number;
}

interface CommonModel {
    id: number;
    createdAt: string;
    updatedAt: string;
}
```

### Domain-Specific Namespaces

| Namespace | File | Purpose |
|-----------|------|---------|
| `App` | `api/interface/app.ts` | App store, installations, parameters |
| `Setting` | `api/interface/setting.ts` | System settings, licenses, snapshots |
| `Website` | `api/interface/website.ts` | Websites, domains, SSL certificates |
| `Container` | `api/interface/container.ts` | Docker containers, images, networks |
| `Database` | `api/interface/database.ts` | MySQL, PostgreSQL, Redis management |
| `Runtime` | `api/interface/runtime.ts` | PHP, Node.js, Python environments |

**Sources**: [frontend/src/api/interface/app.ts:1-4](), [frontend/src/api/interface/setting.ts:1-2]()

---

## App Namespace Type Hierarchy

```mermaid
graph TB
    subgraph "App Namespace Types"
        App["App<br/>Base app model"]
        AppDTO["AppDTO<br/>+versions, installed, architectures"]
        AppItem["AppItem<br/>List view model"]
        AppDetail["AppDetail<br/>+params, dockerCompose, image"]
        
        AppInstall["AppInstall<br/>Installation request"]
        AppInstalled["AppInstalled<br/>Installed app instance"]
        AppInstalledInfo["AppInstalledInfo<br/>+env, container, appKey"]
        AppInstallDto["AppInstallDto<br/>Full installed app DTO"]
        
        AppReq["AppReq<br/>Search request"]
        AppInstallSearch["AppInstallSearch<br/>+update, unused, sync"]
        
        FromField["FromField<br/>Form field definition"]
        InstallParams["InstallParams<br/>Editable parameters"]
        AppConfig["AppConfig<br/>+dockerCompose, resources"]
        
        AppService["AppService<br/>Service endpoint"]
        CheckInstalled["CheckInstalled<br/>Installation check result"]
    end
    
    App -->|extends|CommonModel["CommonModel<br/>id, createdAt, updatedAt"]
    AppDTO -->|extends|App
    AppDetail -->|extends|CommonModel
    AppInstalled -->|extends|CommonModel
    
    AppReq -->|extends|ReqPage["ReqPage<br/>page, pageSize"]
    AppInstallSearch -->|extends|ReqPage
    
    FromField -->|array in|AppParams["AppParams<br/>formFields[]"]
    AppParams -->|field in|AppDetail
    
    InstallParams -->|array in|AppConfig
    
    style CommonModel fill:#f0f0f0
    style ReqPage fill:#f0f0f0
```

**Sources**: [frontend/src/api/interface/app.ts:3-365]()

---

## API Function Patterns

### Basic GET Request

```typescript
// Simple GET with path parameter
export const getAppByKey = (key: string, node?: string) => {
    const params = node ? `?operateNode=${node}` : '';
    return http.get<App.AppDTO>('apps/' + key + `${params}`);
};
```

**Sources**: [frontend/src/api/modules/app.ts:18-21]()

### POST with Request Body

```typescript
// POST with typed request and response
export const searchApp = (req: App.AppReq) => {
    return http.post<App.AppResPage>('apps/search', req);
};

// POST with pagination
export const searchAppInstalled = (search: App.AppInstallSearch, node?: string) => {
    const params = node ? `?operateNode=${node}` : '';
    return http.post<ResPage<App.AppInstallDto>>(`apps/installed/search${params}`, search);
};
```

**Sources**: [frontend/src/api/modules/app.ts:14-16](), [frontend/src/api/modules/app.ts:44-47]()

### Operations with Timeout

```typescript
// Long-running operation with custom timeout
export const installedOp = (op: App.AppInstalledOp, node?: string) => {
    const params = node ? `?operateNode=${node}` : '';
    return http.post<any>(`apps/installed/op${params}`, op, TimeoutEnum.T_40S);
};
```

**Sources**: [frontend/src/api/modules/app.ts:79-82]()

### Multi-Parameter Queries

```typescript
// Complex query with multiple path parameters
export const getAppDetail = (appID: number, version: string, type: string, node?: string) => {
    const params = node ? `?operateNode=${node}` : '';
    return http.get<App.AppDetail>(`apps/detail/${appID}/${version}/${type}${params}`);
};
```

**Sources**: [frontend/src/api/modules/app.ts:27-30]()

---

## Request/Response Type Patterns

### Search Request Pattern

All paginated search operations follow a consistent pattern:

```typescript
// Request extends ReqPage
interface AppInstallSearch extends ReqPage {
    name?: string;
    tags?: string[];
    update?: boolean;
    unused?: boolean;
    sync?: boolean;
}

// Response wraps items in ResPage
interface AppResPage {
    total: number;
    items: AppItem[];
}
```

**Sources**: [frontend/src/api/interface/app.ts:140-146](), [frontend/src/api/interface/app.ts:62-65]()

### Operation Request Pattern

```typescript
interface AppInstalledOp {
    installId: number;
    operate: string;
    backupId?: number;
    detailId?: number;
    forceDelete?: boolean;
    deleteBackup?: boolean;
    deleteImage?: boolean;
    taskID?: string;
}
```

**Sources**: [frontend/src/api/interface/app.ts:250-260]()

### Nested Form Field Pattern

```typescript
interface FromField {
    type: string;
    labelZh: string;
    labelEn: string;
    required: boolean;
    default: any;
    envKey: string;
    key?: string;
    values?: ServiceParam[];
    child?: FromFieldChild;
    params?: FromParam[];
    multiple?: boolean;
    allowCreate?: boolean;
    label: Locale;
    description: Locale;
}

interface FromFieldChild extends FromField {
    services: App.AppService[];
}
```

**Sources**: [frontend/src/api/interface/app.ts:99-118]()

---

## Setting Namespace Type System

```mermaid
graph TB
    subgraph "Core Settings Types"
        SettingInfo["SettingInfo<br/>60+ system settings"]
        TerminalInfo["TerminalInfo<br/>Terminal configuration"]
        ProxyUpdate["ProxyUpdate<br/>Proxy configuration"]
        SSLUpdate["SSLUpdate<br/>SSL certificate config"]
        ApiConfig["ApiConfig<br/>API key settings"]
    end
    
    subgraph "License Types"
        License["License<br/>License details"]
        LicenseStatus["LicenseStatus<br/>Status + SMS quota"]
        LicenseOptions["LicenseOptions<br/>Available licenses"]
        NodeItem["NodeItem<br/>Node information"]
        LicenseBind["LicenseBind<br/>Bind request"]
        LicenseUnbind["LicenseUnbind<br/>Unbind request"]
    end
    
    subgraph "Snapshot Types"
        SnapshotCreate["SnapshotCreate<br/>+appData, panelData"]
        SnapshotInfo["SnapshotInfo<br/>+status, taskIDs"]
        SnapshotRecover["SnapshotRecover<br/>Recovery request"]
        SnapshotData["SnapshotData<br/>Tree structure"]
        DataTree["DataTree<br/>Hierarchical data"]
    end
    
    subgraph "Authentication Types"
        MFARequest["MFARequest"]
        MFAInfo["MFAInfo<br/>+secret, qrImage"]
        MFABind["MFABind"]
        PasskeyRegisterRequest["PasskeyRegisterRequest"]
        PasskeyBeginResponse["PasskeyBeginResponse<br/>+sessionId, publicKey"]
        PasskeyInfo["PasskeyInfo"]
    end
    
    SettingInfo -->|"includes"|ProxyUpdate
    SettingInfo -->|"includes"|SSLUpdate
    
    SnapshotCreate -->|"contains"|DataTree
    SnapshotData -->|"contains"|DataTree
    DataTree -->|"Children[]"|DataTree
    
    LicenseBind -->|"binds to"|NodeItem
    
    style SettingInfo fill:#fff4e6
    style License fill:#e6f3ff
    style SnapshotCreate fill:#f0ffe6
```

**Sources**: [frontend/src/api/interface/setting.ts:3-312]()

---

## Multi-Node Routing Pattern

API functions support routing requests to specific agent nodes using the `operateNode` query parameter. This enables centralized management of distributed nodes.

```mermaid
graph LR
    Component["Vue Component<br/>currentNode = 'node-2'"]
    APIFunction["searchAppInstalled()<br/>+ node parameter"]
    HTTPClient["HTTP Client"]
    
    Component -->|"searchAppInstalled(req, 'node-2')"|APIFunction
    APIFunction -->|"?operateNode=node-2"|HTTPClient
    HTTPClient -->|"routes to"|AgentNode2["Agent Node 2"]
    
    Note["Query param added:<br/>?operateNode=node-2"]
    APIFunction -.->|explains|Note
```

### Implementation Pattern

```typescript
// API function accepts optional node parameter
export const searchAppInstalled = (search: App.AppInstallSearch, node?: string) => {
    const params = node ? `?operateNode=${node}` : '';
    return http.post<ResPage<App.AppInstallDto>>(`apps/installed/search${params}`, search);
};

// Component passes currentNode
const { currentNode } = useGlobalStore();
const search = async () => {
    const res = await searchAppInstalled(searchReq, currentNode.value);
    // ...
};
```

**Sources**: [frontend/src/api/modules/app.ts:44-47](), [frontend/src/views/app-store/installed/index.vue:146]()

---

## Timeout Management

The API client uses `TimeoutEnum` for operations that require extended timeout periods:

| Timeout Value | Duration | Use Case |
|---------------|----------|----------|
| `T_40S` | 40 seconds | App operations (start/stop/restart) |
| `T_60S` | 60 seconds | License binding, app store sync |
| Default | - | Standard CRUD operations |

### Usage in API Functions

```typescript
// Standard timeout (default)
export const searchApp = (req: App.AppReq) => {
    return http.post<App.AppResPage>('apps/search', req);
};

// Extended timeout for long operations
export const installedOp = (op: App.AppInstalledOp, node?: string) => {
    const params = node ? `?operateNode=${node}` : '';
    return http.post<any>(`apps/installed/op${params}`, op, TimeoutEnum.T_40S);
};

// 60-second timeout for license operations
export const bindLicense = (params: Setting.LicenseBind) => {
    return http.post(`/core/licenses/bind`, params, TimeoutEnum.T_60S);
};
```

**Sources**: [frontend/src/api/modules/app.ts:79-82](), [frontend/src/api/modules/setting.ts:31-33](), [frontend/src/api/modules/app.ts:4](), [frontend/src/api/modules/setting.ts:6]()

---

## Security Patterns in API Layer

### Base64 Encoding for Sensitive Data

Proxy passwords are Base64-encoded before transmission:

```typescript
export const updateProxy = (params: Setting.ProxyUpdate) => {
    let request = deepCopy(params) as Setting.ProxyUpdate;
    if (request.proxyPasswd) {
        request.proxyPasswd = Base64.encode(request.proxyPasswd);
    }
    request.proxyType = request.proxyType === 'close' ? '' : request.proxyType;
    return http.post(`/core/settings/proxy/update`, request);
};
```

**Sources**: [frontend/src/api/modules/setting.ts:107-114]()

### File Upload with FormData

```typescript
export const uploadLicense = (oldLicense: string, params: FormData) => {
    if (oldLicense === '') {
        return http.upload('/core/licenses/upload', params);
    }
    return http.upload('/core/licenses/update', params);
};
```

**Sources**: [frontend/src/api/modules/setting.ts:10-15]()

### Custom Headers for Authentication

```typescript
export const passkeyRegisterFinish = (param: Record<string, any>, sessionId: string) => {
    return http.post(`/core/settings/passkey/register/finish`, param, undefined, { 'Passkey-Session': sessionId });
};
```

**Sources**: [frontend/src/api/modules/setting.ts:148-150]()

---

## Component-to-API Integration Pattern

```mermaid
sequenceDiagram
    participant Component as Vue Component
    participant ComposableAPI as Composable API
    participant TypedRequest as Typed Request
    participant HTTPClient as HTTP Client
    participant Backend as Backend API
    
    Component->>Component: User action (search)
    Component->>TypedRequest: Create request object<br/>type: AppInstallSearch
    Component->>ComposableAPI: searchAppInstalled(req)
    ComposableAPI->>HTTPClient: http.post(url, req)
    HTTPClient->>Backend: POST with headers
    Backend-->>HTTPClient: JSON response
    HTTPClient-->>ComposableAPI: Typed response<br/>ResPage<AppInstallDto>
    ComposableAPI-->>Component: data.value = res.data.items
    Component->>Component: Render UI with typed data
```

### Example: Installed Apps Search

```typescript
// 1. Define reactive request (in component)
const searchReq = reactive<App.AppInstallSearch>({
    page: 1,
    pageSize: 20,
    name: '',
    tags: [],
    update: false,
    sync: false,
});

// 2. Call typed API function
const search = async () => {
    searchReq.page = paginationConfig.currentPage;
    searchReq.pageSize = paginationConfig.pageSize;
    
    const res = await searchAppInstalled(searchReq);
    data.value = res.data.items;  // Typed as AppInstallDto[]
    paginationConfig.total = res.data.total;
};

// 3. TypeScript ensures type safety
data.value.forEach((app: App.AppInstallDto) => {
    console.log(app.name);      // Valid
    console.log(app.version);   // Valid
    console.log(app.unknown);   // TypeScript error
});
```

**Sources**: [frontend/src/views/app-store/installed/index.vue:175-182](), [frontend/src/views/app-store/installed/index.vue:202-211]()

---

## Icon URL Generation Pattern

Some resources require special URL generation for assets:

```typescript
export function getAppIconUrl(appKey: string, node?: string): string {
    const baseURL = import.meta.env.VITE_API_URL as string;
    const params = node ? `?operateNode=${node}` : '';
    return `${baseURL}/apps/icon/${appKey}${params}`;
}

// Usage in component
<img 
    :src="getAppIconUrl(app.key, currentNode)" 
    alt="App Icon"
/>
```

**Sources**: [frontend/src/api/modules/app.ts:134-138](), [frontend/src/views/app-store/detail/index.vue:8]()

---

## Form Parameter Type System

Form parameters use a flexible type system to handle dynamic app configurations:

```mermaid
graph TB
    subgraph "Form Field Types"
        FromField["FromField<br/>Base field definition"]
        
        FromField -->|"type: 'text'"|TextField["Text Input"]
        FromField -->|"type: 'number'"|NumberField["Number Input"]
        FromField -->|"type: 'password'"|PasswordField["Password Input"]
        FromField -->|"type: 'select'"|SelectField["Select Dropdown"]
        FromField -->|"type: 'service'"|ServiceField["Service Selector"]
        FromField -->|"type: 'apps'"|AppsField["App Selector"]
        
        SelectField -->|"values[]"|ServiceParam["ServiceParam<br/>label, value, from"]
        ServiceField -->|"values[]"|ServiceParam
        AppsField -->|"child"|FromFieldChild["FromFieldChild<br/>+services[]"]
        FromFieldChild -->|"services[]"|AppService["AppService<br/>label, value, config"]
    end
    
    subgraph "Installed Params"
        InstallParams["InstallParams<br/>Editable parameters"]
        InstallParams -->|"type: string"|FieldType["Field type"]
        InstallParams -->|"value: any"|FieldValue["Current value"]
        InstallParams -->|"edit: boolean"|Editable["Is editable"]
        InstallParams -->|"showValue: string"|DisplayValue["Display value"]
        InstallParams -->|"rule: string"|ValidationRule["Validation rule"]
    end
    
    FromField -.->|"transforms to"|InstallParams
```

**Sources**: [frontend/src/api/interface/app.ts:99-131](), [frontend/src/api/interface/app.ts:280-294]()

---

## Validation Rule Integration

The type system integrates with form validation rules defined in `frontend/src/global/form-rules.ts`:

```typescript
// In InstallParams interface
interface InstallParams {
    labelZh: string;
    labelEn: string;
    value: any;
    edit: boolean;
    key: string;
    rule: string;  // References rule name from form-rules.ts
    type: string;
    values?: any;
    showValue?: string;
    required?: boolean;
    multiple?: boolean;
    label: Locale;
    showPassword: boolean;
}

// Usage in component
if (param.required) {
    rules.params[param.key] = [Rules.requiredInput];
    if (param.rule && param.rule != '') {
        rules.params[param.key].push(Rules[param.rule]);  // e.g., Rules.dbName
    }
}
```

**Sources**: [frontend/src/api/interface/app.ts:280-294](), [frontend/src/views/app-store/installed/detail/index.vue:344-351]()

---

## AppConfig Type for Parameter Management

The `AppConfig` type represents the complete configuration of an installed app:

```typescript
interface AppConfig {
    params: InstallParams[];       // User-editable parameters
    rawCompose?: string;           // Original docker-compose.yml
    cpuQuota: number;              // CPU limit in cores
    memoryLimit: number;           // Memory limit
    memoryUnit: string;            // 'MB' or 'GB'
    containerName: string;         // Custom container name
    allowPort: boolean;            // Expose ports to host
    dockerCompose: string;         // Current docker-compose.yml
    hostMode?: boolean;            // Host network mode
    type: string;                  // App type
    webUI: string;                 // Web UI access URL
    specifyIP: string;             // IP binding
    restartPolicy: string;         // Container restart policy
}
```

### Usage Flow

```mermaid
graph LR
    GetParams["GET /apps/installed/params/:id"]
    AppConfig["AppConfig<br/>returned"]
    Component["Component<br/>displays params"]
    UserEdit["User edits<br/>parameters"]
    UpdateParams["POST /apps/installed/params/update"]
    
    GetParams -->|response|AppConfig
    AppConfig -->|renders|Component
    Component -->|user action|UserEdit
    UserEdit -->|submits|UpdateParams
    UpdateParams -->|with|AppConfig
```

**Sources**: [frontend/src/api/interface/app.ts:296-310](), [frontend/src/api/modules/app.ts:102-108]()

---

## Pagination Configuration Pattern

All paginated views use consistent pagination configuration:

```typescript
const paginationConfig = reactive({
    cacheSizeKey: 'app-installed-page-size',
    currentPage: 1,
    pageSize: Number(localStorage.getItem('app-installed-page-size')) || 20,
    total: 0,
});

// Request includes pagination
const req = reactive<App.AppReq>({
    name: '',
    tags: [],
    page: 1,
    pageSize: 60,
    resource: 'all',
    showCurrentArch: false,
});

// API call
req.page = paginationConfig.currentPage;
req.pageSize = paginationConfig.pageSize;
const res = await searchApp(req);
paginationConfig.total = res.data.total;
```

**Sources**: [frontend/src/views/app-store/installed/index.vue:152-157](), [frontend/src/views/app-store/apps/index.vue:101-109]()

---

## Type Safety in Component Operations

Components leverage TypeScript types to ensure safe operations:

```typescript
// Operation request with typed parameters
const operateReq = reactive<App.AppInstalledOp>({
    installId: 0,
    operate: '',
    detailId: 0,
    favorite: false,
});

// Type-safe operation calls
const openOperate = (row: App.AppInstalled, op: string) => {
    operateReq.installId = row.id;
    operateReq.operate = op;
    if (op == 'upgrade') {
        upgradeRef.value.acceptParams(row, op);
    } else if (op == 'delete') {
        appInstalledDeleteCheck(row.id).then(async (res) => {
            // TypeScript knows res.data is AppInstallResource[]
            const items = res.data;
            if (res.data && res.data.length > 0) {
                checkRef.value.acceptParams({ 
                    items: items, 
                    key: row.appKey, 
                    installID: row.id 
                });
            }
        });
    }
};
```

**Sources**: [frontend/src/views/app-store/installed/index.vue:159-164](), [frontend/src/views/app-store/installed/index.vue:229-246]()

---

## Summary

The 1Panel frontend API client layer provides:

1. **Modular Organization**: Domain-specific API modules (`app.ts`, `setting.ts`, etc.) with corresponding type namespaces
2. **Strong Type Safety**: TypeScript interfaces for all requests, responses, and data models
3. **Consistent Patterns**: Standardized pagination, search, and operation patterns across all modules
4. **Multi-Node Support**: Built-in routing to different agent nodes via `operateNode` parameter
5. **Timeout Management**: Configurable timeouts for long-running operations via `TimeoutEnum`
6. **Security**: Base64 encoding, custom headers, and FormData for sensitive operations
7. **Integration**: Seamless connection between Vue components and backend APIs with full type inference

This architecture ensures maintainability, type safety, and consistent behavior across the entire frontend codebase.

---

# Page: Form Validation and Utilities

# Form Validation and Utilities

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent/go.mod](agent/go.mod)
- [agent/go.sum](agent/go.sum)
- [agent/utils/ssl/dns_provider.go](agent/utils/ssl/dns_provider.go)
- [core/go.mod](core/go.mod)
- [core/go.sum](core/go.sum)
- [frontend/src/api/interface/app.ts](frontend/src/api/interface/app.ts)
- [frontend/src/api/modules/app.ts](frontend/src/api/modules/app.ts)
- [frontend/src/components/app-status/index.vue](frontend/src/components/app-status/index.vue)
- [frontend/src/global/form-rules.ts](frontend/src/global/form-rules.ts)
- [frontend/src/global/mimetype.ts](frontend/src/global/mimetype.ts)
- [frontend/src/styles/common.scss](frontend/src/styles/common.scss)
- [frontend/src/views/app-store/apps/index.vue](frontend/src/views/app-store/apps/index.vue)
- [frontend/src/views/app-store/detail/index.vue](frontend/src/views/app-store/detail/index.vue)
- [frontend/src/views/app-store/detail/install/index.vue](frontend/src/views/app-store/detail/install/index.vue)
- [frontend/src/views/app-store/detail/params/index.vue](frontend/src/views/app-store/detail/params/index.vue)
- [frontend/src/views/app-store/installed/detail/index.vue](frontend/src/views/app-store/installed/detail/index.vue)
- [frontend/src/views/app-store/installed/index.vue](frontend/src/views/app-store/installed/index.vue)
- [frontend/src/views/app-store/installed/upgrade/index.vue](frontend/src/views/app-store/installed/upgrade/index.vue)
- [frontend/src/views/website/ssl/dns-account/create/index.vue](frontend/src/views/website/ssl/dns-account/create/index.vue)
- [frontend/src/views/website/website/create/index.vue](frontend/src/views/website/website/create/index.vue)
- [frontend/src/views/website/website/index.vue](frontend/src/views/website/website/index.vue)

</details>



This page documents the centralized form validation system and utility functions used throughout the 1Panel frontend. The system provides reusable validators, custom rules, and helper utilities that ensure consistent data validation across all forms in the application.

For information about API client type validation, see [API Client Layer and Type System](#11.2). For component-level patterns, see [Component Architecture and Patterns](#11.1).

---

## Purpose and Architecture

The form validation system centralizes all validation logic in a single module (`frontend/src/global/form-rules.ts`) that exports:

1. **Validator Functions**: Asynchronous callbacks conforming to Element Plus validation API
2. **Rules Object**: Pre-configured FormItemRule instances ready for use in forms
3. **Dynamic Validators**: Factory functions that generate rules with parameters
4. **Utility Functions**: Common helpers for validation and data manipulation

This architecture ensures consistent validation behavior, reduces code duplication, and provides a single source of truth for all validation rules.

**Validation Flow Overview**

```mermaid
graph TB
    FormRulesTS["form-rules.ts<br/>Central Validation Module"]
    ValidatorFuncs["Validator Functions<br/>(checkIp, checkName, etc.)"]
    RulesObject["Rules Object<br/>Export"]
    DynamicValidators["Dynamic Validators<br/>(checkNumberRange)"]
    
    VueComponent["Vue Component<br/>(create/index.vue)"]
    ElForm["el-form<br/>Element Plus"]
    FormModel["Form Data Model<br/>(reactive/ref)"]
    RulesReactive["Rules Definition<br/>(reactive)"]
    
    FormRulesTS --> ValidatorFuncs
    FormRulesTS --> RulesObject
    FormRulesTS --> DynamicValidators
    
    VueComponent --> ElForm
    VueComponent --> FormModel
    VueComponent --> RulesReactive
    RulesReactive --> RulesObject
    RulesReactive --> DynamicValidators
    ElForm --> RulesReactive
    ElForm --> FormModel
    
    UserInput["User Input"]
    ValidationTrigger["Validation Trigger<br/>(blur/change/submit)"]
    ValidationResult["Validation Result<br/>(pass/fail)"]
    
    UserInput --> ElForm
    ElForm --> ValidationTrigger
    ValidationTrigger --> ValidatorFuncs
    ValidatorFuncs --> ValidationResult
```

Sources: [frontend/src/global/form-rules.ts:1-800](), [frontend/src/views/website/website/create/index.vue:519-548]()

---

## Core Validation Rules Module

The `form-rules.ts` module serves as the foundation of the validation system. It exports a centralized `Rules` object containing all standard validation rules.

**Rules Object Structure**

```mermaid
graph LR
    subgraph "form-rules.ts Export"
        RulesObj["Rules Object"]
        
        subgraph "Common Validators"
            RequiredInput["requiredInput"]
            RequiredSelect["requiredSelect"]
            RequiredSelectBusiness["requiredSelectBusiness"]
        end
        
        subgraph "String Pattern Validators"
            Name["name"]
            SimpleName["simpleName"]
            SimplePassword["simplePassword"]
            ParamComplexity["paramComplexity"]
            Alias["alias"]
        end
        
        subgraph "Network Validators"
            IP["ip"]
            IPV4["ipV4"]
            IPV6["ipV6"]
            Domain["domain"]
            DomainWithPort["domainWithPort"]
            Port["port"]
        end
        
        subgraph "Special Format Validators"
            DBName["dbName"]
            AppName["appName"]
            ContainerName["containerName"]
            ImageName["imageName"]
            VolumeName["volumeName"]
        end
        
        RulesObj --> RequiredInput
        RulesObj --> RequiredSelect
        RulesObj --> RequiredSelectBusiness
        RulesObj --> Name
        RulesObj --> SimpleName
        RulesObj --> SimplePassword
        RulesObj --> ParamComplexity
        RulesObj --> Alias
        RulesObj --> IP
        RulesObj --> IPV4
        RulesObj --> IPV6
        RulesObj --> Domain
        RulesObj --> DomainWithPort
        RulesObj --> Port
        RulesObj --> DBName
        RulesObj --> AppName
        RulesObj --> ContainerName
        RulesObj --> ImageName
        RulesObj --> VolumeName
    end
```

Sources: [frontend/src/global/form-rules.ts:576-650]()

### Rules Object Definition

The `Rules` object at [frontend/src/global/form-rules.ts:576-650]() contains pre-configured FormItemRule instances:

| Rule Name | Purpose | Validator Function | Trigger |
|-----------|---------|-------------------|---------|
| `requiredInput` | Required text input | None (uses Element Plus required) | blur |
| `requiredSelect` | Required dropdown selection | None | change |
| `requiredSelectBusiness` | Required business selection | None | change |
| `name` | Common name pattern | `checkName` | blur |
| `userName` | Username pattern | `checkUserName` | blur |
| `simpleName` | Simple alphanumeric name | `checkSimpleName` | blur |
| `simplePassword` | Simple password pattern | `checkSimplePassword` | blur |
| `authBasicPassword` | HTTP basic auth password | `checkAuthBasicPassword` | blur |
| `ip` | IPv4 address (required) | `checkIp` | blur |
| `ipV4` | IPv4 address (optional) | `checkIpv4` | blur |
| `ipV6` | IPv6 address | `checkIpV6` | blur |
| `domain` | Domain name | `checkDomain` | blur |
| `domainWithPort` | Domain with optional port | `checkDomainWithPort` | blur |
| `port` | Port number (1-65535) | `checkPort` | blur |
| `dbName` | Database name | `checkDBName` | blur |
| `appName` | Application name | `checkAppName` | blur |
| `containerName` | Docker container name | `checkContainerName` | blur |
| `imageName` | Docker image name | `checkImageName` | blur |
| `volumeName` | Docker volume name | `checkVolumeName` | blur |
| `alias` | File/resource alias | `checkAlias` | blur |
| `paramComplexity` | Complex parameter | `checkParamComplexity` | blur |

Sources: [frontend/src/global/form-rules.ts:576-650]()

---

## Validator Functions

Each validator function follows the Element Plus validation callback pattern: `(rule: any, value: any, callback: any) => void`.

**Validation Function Pattern**

```mermaid
sequenceDiagram
    participant Form as el-form
    participant Validator as Validator Function
    participant I18n as i18n.global.t()
    participant Callback as Element Plus
    
    Form->>Validator: validate(rule, value, callback)
    
    alt Value is empty/undefined/null
        Validator->>I18n: Get error message key
        I18n-->>Validator: Translated message
        Validator->>Callback: callback(new Error(message))
    else Value matches pattern
        Validator->>Callback: callback()
    else Value fails pattern
        Validator->>I18n: Get error message key
        I18n-->>Validator: Translated message
        Validator->>Callback: callback(new Error(message))
    end
```

Sources: [frontend/src/global/form-rules.ts:4-575]()

### Common Validator Patterns

#### Empty Value Check

Most validators start by checking for empty, undefined, or null values:

```typescript
if (value === '' || typeof value === 'undefined' || value == null) {
    callback(new Error(i18n.global.t('commons.rule.requiredInput')));
}
```

Sources: [frontend/src/global/form-rules.ts:11-13]()

#### Pattern Matching

Validators use regex patterns to validate format:

```typescript
const reg = /^[a-zA-Z0-9]{1}[a-zA-Z0-9_]{2,29}$/;
if (!reg.test(value) && value !== '') {
    callback(new Error(i18n.global.t('commons.rule.simpleName')));
} else {
    callback();
}
```

Sources: [frontend/src/global/form-rules.ts:193-196]()

### Key Validator Functions

**IP Address Validators**

| Validator | Pattern | Example Valid Input |
|-----------|---------|-------------------|
| `checkIp` | IPv4 with required | `192.168.1.1` |
| `checkIpv4` | IPv4 optional | `10.0.0.1` or empty |
| `checkIpV6` | IPv6 | `2001:db8::1` |
| `checkIpV4V6OrDomain` | IPv4/IPv6/domain | `example.com`, `192.168.1.1`, `::1` |
| `checkDomainOrIP` | Domain or IP | `example.com`, `192.168.1.1` |

Sources: [frontend/src/global/form-rules.ts:11-110]()

**Name Pattern Validators**

| Validator | Pattern | Allowed Characters | Max Length |
|-----------|---------|-------------------|-----------|
| `checkName` | Common name | `a-zA-Z0-9_.-` + Chinese | 128 |
| `checkUserName` | Username | `a-zA-Z0-9_` + Chinese | 30 |
| `checkSimpleName` | Simple name | `a-zA-Z0-9_` | 30 |
| `checkDBName` | Database name | `a-zA-Z0-9_.-` + Chinese | 64 |
| `checkAppName` | App name | `a-zA-Z0-9_-` (no start/end with `-_`) | 30 |
| `checkAlias` | Alias | `A-Za-z0-9._-` (no start/end with `-_`) | 128 |
| `checkLinuxName` | Linux filename | Any except `/\:*?"'()<>\|` | 128 |

Sources: [frontend/src/global/form-rules.ts:163-343]()

**Password and Security Validators**

| Validator | Purpose | Pattern |
|-----------|---------|---------|
| `checkSimplePassword` | Basic password | `a-zA-Z0-9_`, 1-30 chars |
| `checkAuthBasicPassword` | HTTP Basic Auth | `a-zA-Z0-9_\-\.@$!%*?&`, 1-72 chars |
| `complexityPassword` | Complex password | Must have 2+ char types, 8-30 chars |
| `checkParamComplexity` | Parameter password | `a-zA-Z0-9.%@!~_-`, 6-128 chars |

Sources: [frontend/src/global/form-rules.ts:150-436]()

**Container/Docker Validators**

| Validator | Purpose | Pattern |
|-----------|---------|---------|
| `checkContainerName` | Container name | `a-zA-Z0-9_.-`, 2-128 chars |
| `checkComposeName` | Compose project | `a-z0-9_-`, 1-256 chars |
| `checkImageName` | Image name | `a-zA-Z0-9:@_/.-`, 1-256 chars |
| `checkVolumeName` | Volume name | `a-zA-Z0-9_.-`, 2-31 chars |

Sources: [frontend/src/global/form-rules.ts:241-278]()

---

## Dynamic Validators

Dynamic validators are factory functions that generate validation rules with custom parameters.

**Dynamic Validator Usage**

```mermaid
graph LR
    Component["Vue Component"]
    Factory["checkNumberRange(min, max)"]
    Rule["FormItemRule"]
    Form["el-form rules"]
    
    Component -->|"Call with params"| Factory
    Factory -->|"Returns"| Rule
    Rule -->|"Add to"| Form
    
    subgraph "Example: CPU Quota"
        Example["cpuQuota: [<br/>Rules.requiredInput,<br/>checkNumberRange(0, 999)<br/>]"]
    end
```

Sources: [frontend/src/global/form-rules.ts:478-507](), [frontend/src/views/app-store/installed/detail/index.vue:219-220]()

### checkNumberRange

Validates numeric input within a range:

```typescript
export function checkNumberRange(min: number, max: number): FormItemRule {
    return {
        required: false,
        trigger: 'blur',
        min: min,
        max: max,
        type: 'number',
        message: i18n.global.t('commons.rule.numberRange', [min, max]),
    };
}
```

**Usage Examples:**

| Context | Rule | Range |
|---------|------|-------|
| CPU Quota | `checkNumberRange(0, 999)` | 0-999 cores |
| Memory Limit | `checkNumberRange(0, 9999999999)` | 0-9999999999 MB |
| Port (internal) | `checkNumberRange(1, 65535)` | Valid port range |

Sources: [frontend/src/global/form-rules.ts:478-487](), [frontend/src/views/app-store/installed/detail/index.vue:219-220]()

### checkFloatNumberRange

Validates float numbers within a range:

```typescript
export function checkFloatNumberRange(min: number, max: number): FormItemRule {
    let validatorFunc = function (rule: any, value: any, callback: any) {
        if (value === '' || typeof value === 'undefined' || value == null) {
            callback(new Error(i18n.global.t('commons.rule.disableFunction')));
        } else {
            if ((Number(value) < min || Number(value) > max) && value !== '') {
                callback(new Error(i18n.global.t('commons.rule.disableFunction')));
            } else {
                callback();
            }
        }
    };
    return {
        required: false,
        trigger: 'blur',
        validator: validatorFunc,
        message: i18n.global.t('commons.rule.numberRange', [min, max]),
    };
}
```

Sources: [frontend/src/global/form-rules.ts:489-507]()

---

## Form Validation in Practice

This section demonstrates how validation rules are applied in real Vue components.

**Website Creation Form Example**

```mermaid
graph TB
    subgraph "website/website/create/index.vue"
        WebsiteForm["websiteForm ref<br/>(FormInstance)"]
        WebsiteModel["website reactive<br/>(form data)"]
        RulesDef["rules ref<br/>(validation rules)"]
        
        subgraph "Rules Definition"
            AliasRule["alias: [Rules.alias]"]
            TypeRule["type: [Rules.requiredInput]"]
            GroupRule["webSiteGroupId: [Rules.requiredSelectBusiness]"]
            AppInstallRule["appInstallId: [Rules.requiredSelectBusiness]"]
            ProxyRule["proxyAddress: [Rules.requiredInput]"]
            RuntimeRule["runtimeID: [Rules.requiredSelectBusiness]"]
            PortRule["port: [Rules.port]"]
            DBNameRule["dbName: [Rules.requiredInput, Rules.dbName]"]
            DBUserRule["dbUser: [Rules.requiredInput, Rules.name]"]
            DBPassRule["dbPassword: [Rules.requiredInput, Rules.paramComplexity]"]
        end
        
        WebsiteForm -->|"validates with"| RulesDef
        RulesDef --> AliasRule
        RulesDef --> TypeRule
        RulesDef --> GroupRule
        RulesDef --> AppInstallRule
        RulesDef --> ProxyRule
        RulesDef --> RuntimeRule
        RulesDef --> PortRule
        RulesDef --> DBNameRule
        RulesDef --> DBUserRule
        RulesDef --> DBPassRule
    end
```

Sources: [frontend/src/views/website/website/create/index.vue:519-548]()

### Validation Rule Composition

Forms typically compose multiple rules for a single field:

```typescript
// Single rule
alias: [Rules.alias],

// Multiple rules for one field
dbName: [Rules.requiredInput, Rules.dbName],
dbUser: [Rules.requiredInput, Rules.name],
dbPassword: [Rules.requiredInput, Rules.paramComplexity],

// Dynamic rule with static rule
cpuQuota: [Rules.requiredInput, checkNumberRange(0, 999)],
memoryLimit: [Rules.requiredInput, checkNumberRange(0, 9999999999)],
```

Sources: [frontend/src/views/website/website/create/index.vue:520-548](), [frontend/src/views/app-store/installed/detail/index.vue:217-221]()

### Nested Form Validation

For complex forms with nested objects (like app installation), rules can be nested:

```typescript
rules = {
    alias: [Rules.alias],
    type: [Rules.requiredInput],
    appinstall: {
        name: [Rules.appName],
        appId: [Rules.requiredSelectBusiness],
        params: {},
        cpuQuota: [Rules.requiredInput, checkNumberRange(0, 99999)],
        memoryLimit: [Rules.requiredInput, checkNumberRange(0, 9999999999)],
        containerName: [Rules.containerName],
    },
}
```

Sources: [frontend/src/views/website/website/create/index.vue:527-534]()

### Conditional Validation

Rules can be dynamically added/removed based on conditions:

```typescript
// Add rules conditionally
if (p.required) {
    if (p.type === 'service' || p.type === 'apps') {
        rules[p.envKey] = [Rules.requiredSelect];
        if (p.child) {
            p.childProp = propStart.value + p.child.envKey;
            if (p.child.type === 'service') {
                rules[p.child.envKey] = [Rules.requiredSelect];
            }
        }
    } else {
        rules[p.envKey] = [Rules.requiredInput];
    }
    if (p.rule && p.rule != '') {
        rules[p.envKey].push(Rules[p.rule]);
    }
} else {
    delete rules[p.envKey];
}
```

Sources: [frontend/src/views/app-store/detail/params/index.vue:227-244]()

---

## Utility Functions and Helpers

Beyond validation, the form system includes utility functions used across components.

**Utility Function Categories**

```mermaid
graph TB
    subgraph "Validation Utilities"
        CheckIllegal["checkIllegal<br/>Prevent shell injection"]
        CheckNoSpace["checkNoSpace<br/>No whitespace allowed"]
        CheckFilePermission["checkFilePermission<br/>Unix permissions (0-7)"]
    end
    
    subgraph "Format Utilities"
        GetLabel["getLabel<br/>i18n label getter"]
        GetDescription["getDescription<br/>i18n description getter"]
        ComputeSize["computeSizeFromMB<br/>Size formatting"]
    end
    
    subgraph "Random Generation"
        GetRandomStr["getRandomStr<br/>Random string"]
        GetDBName["getDBName<br/>Database name suffix"]
    end
    
    subgraph "URL Utilities"
        SplitHttp["splitHttp<br/>Parse protocol/URL"]
        CheckDomain["checkDomain<br/>Domain validation"]
        CheckIpV4V6["checkIpV4V6<br/>IP validation"]
    end
```

Sources: [frontend/src/global/form-rules.ts:127-572](), [frontend/src/utils/util.ts]()

### Security and Input Sanitization

**checkIllegal Validator**

Prevents shell injection by blocking dangerous characters:

```typescript
const checkIllegal = (rule: any, value: any, callback: any) => {
    if (value === '' || typeof value === 'undefined' || value == null) {
        callback(new Error(i18n.global.t('commons.rule.requiredInput')));
        return;
    }
    if (
        value.indexOf('&') !== -1 ||
        value.indexOf('|') !== -1 ||
        value.indexOf(';') !== -1 ||
        value.indexOf('$') !== -1 ||
        value.indexOf("'") !== -1 ||
        value.indexOf('`') !== -1 ||
        value.indexOf('(') !== -1 ||
        value.indexOf(')') !== -1 ||
        value.indexOf('>') !== -1 ||
        value.indexOf('<') !== -1
    ) {
        callback(new Error(i18n.global.t('commons.rule.illegalInput')));
    } else {
        callback();
    }
};
```

Blocked characters: `& | ; $ ' \` ( ) > <`

Sources: [frontend/src/global/form-rules.ts:127-148]()

### Form Helper Styling

The form system provides CSS classes for consistent styling:

| CSS Class | Purpose | Usage |
|-----------|---------|-------|
| `.input-help` | Help text below inputs | `<span class="input-help">...</span>` |
| `.input-error` | Error messages | `<span class="input-error">...</span>` |
| `.common-prompt` | Alert prompts in forms | `<el-alert class="common-prompt">` |
| `.form-button` | Right-aligned buttons | `<div class="form-button">` |

Sources: [frontend/src/styles/common.scss:79-98]()

**Help Text Styling:**

```scss
.input-help {
    font-size: 12px;
    word-break: keep-all;
    color: #adb0bc;
    width: 100%;
    display: inline-block;
    white-space: pre-line;
}
```

Sources: [frontend/src/styles/common.scss:79-86]()

---

## Common Validation Patterns

This section documents common patterns for implementing validation in different scenarios.

### Pattern 1: Simple Form with Basic Rules

**Structure:**
1. Import `Rules` from `@/global/form-rules`
2. Define reactive form model
3. Define reactive rules object
4. Bind to `el-form` with `ref` and `:rules`

**Example from App Installation:**

```typescript
import { Rules } from '@/global/form-rules';

const formData = ref({
    name: '',
    version: '',
    // ... other fields
});

const rules = reactive({
    name: [Rules.appName],
    version: [Rules.requiredSelect],
});
```

Sources: [frontend/src/views/app-store/detail/install/index.vue:42-62]()

### Pattern 2: Dynamic Rules Based on Form State

**Structure:**
1. Start with base rules
2. Conditionally add/modify rules in watchers or computed properties
3. Use `delete` to remove rules when not applicable

**Example from Website Creation:**

```typescript
const rules = ref<any>({
    alias: [Rules.alias],
    type: [Rules.requiredInput],
    // Base rules...
});

// Conditionally add nested rules
if (website.value.appType == 'new') {
    rules.value.appinstall = {
        name: [Rules.appName],
        appId: [Rules.requiredSelectBusiness],
        cpuQuota: [Rules.requiredInput, checkNumberRange(0, 99999)],
        memoryLimit: [Rules.requiredInput, checkNumberRange(0, 9999999999)],
    };
}
```

Sources: [frontend/src/views/website/website/create/index.vue:519-548]()

### Pattern 3: Nested Object Validation

For forms with nested data structures, use nested rule definitions:

```typescript
rules = {
    params: {
        [key1]: [Rules.requiredInput],
        [key2]: [Rules.port],
    },
    advanced: [],
    cpuQuota: [Rules.requiredInput, checkNumberRange(0, 999)],
    containerName: [Rules.containerName],
}
```

The `el-form-item` `prop` attribute should use dot notation: `prop="params.key1"`

Sources: [frontend/src/views/app-store/installed/detail/index.vue:217-223]()

### Pattern 4: Manual Validation Trigger

For programmatic validation (e.g., before API calls):

```typescript
const formRef = ref<FormInstance>();

const submit = async () => {
    if (!formRef.value) return;
    
    await formRef.value.validate((valid) => {
        if (!valid) {
            return;
        }
        // Proceed with submission
    });
};
```

Sources: [frontend/src/views/app-store/installed/detail/index.vue:380-416]()

### Pattern 5: Clear Validation on Dynamic Changes

When form fields change dynamically, clear previous validation errors:

```typescript
const changeType = (type: string) => {
    // Clear validation when switching types
    websiteForm.value?.clearValidate();
    
    // Update form state
    website.value.type = type;
};
```

Sources: [frontend/src/views/website/website/create/index.vue:616-639]()

---

## Validation Error Handling

### Error Message Internationalization

All validation error messages use the i18n system:

```typescript
callback(new Error(i18n.global.t('commons.rule.simpleName')));
callback(new Error(i18n.global.t('commons.rule.port')));
callback(new Error(i18n.global.t('commons.rule.ip')));
```

**Common Error Message Keys:**

| Key | Message Purpose |
|-----|-----------------|
| `commons.rule.requiredInput` | Field is required |
| `commons.rule.requiredSelect` | Selection is required |
| `commons.rule.simpleName` | Invalid name format |
| `commons.rule.port` | Invalid port number |
| `commons.rule.ip` | Invalid IP address |
| `commons.rule.domain` | Invalid domain name |
| `commons.rule.numberRange` | Number out of range |
| `commons.rule.illegalInput` | Contains illegal characters |

Sources: [frontend/src/global/form-rules.ts:1-800]()

### Displaying Validation Errors

Element Plus automatically displays validation errors below form fields when validation fails. Custom error display can be added:

```vue
<el-form-item :label="$t('app.name')" prop="name">
    <el-input v-model="form.name"></el-input>
    <span class="input-help">{{ $t('app.nameHelper') }}</span>
</el-form-item>
```

Sources: [frontend/src/views/website/website/create/index.vue:200-207]()

---

## Summary

**Key Takeaways:**

1. **Centralized Validation**: All validation logic resides in `frontend/src/global/form-rules.ts`
2. **Reusable Rules**: The `Rules` object provides 40+ pre-configured validators
3. **Type Safety**: Validators use TypeScript and Element Plus FormItemRule interface
4. **i18n Support**: All error messages are internationalized
5. **Composable**: Rules can be combined, nested, and generated dynamically
6. **Consistent Patterns**: Common validation scenarios follow established patterns

**File Reference Map:**

| Component | Purpose | Key Exports |
|-----------|---------|-------------|
| `form-rules.ts` | Core validation module | `Rules`, `checkNumberRange`, validator functions |
| `util.ts` | Utility functions | `getLabel`, `getDescription`, `getRandomStr` |
| `common.scss` | Form styling | `.input-help`, `.input-error`, `.form-button` |

Sources: [frontend/src/global/form-rules.ts:1-800](), [frontend/src/styles/common.scss:75-310]()