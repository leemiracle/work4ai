# Page: AgentSpace Overview

# AgentSpace Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [LICENSE](LICENSE)
- [README.md](README.md)
- [README_ZH.md](README_ZH.md)
- [Target.md](Target.md)

</details>



AgentSpace is an agent-native collaborative workspace designed for **human + agent teams**. Unlike traditional agent frameworks that focus on individual chat sessions, AgentSpace treats agents as first-class teammates ("Digital Employees") with defined roles, owners, and organizational responsibilities [README.md:31-34]().

It provides a unified environment where work is managed through shared workspaces, channels, and tasks, governed by a robust permission and approval system [README.md:107-113]().

### Core Value Proposition

AgentSpace addresses the fragmentation of modern agent workflows by providing:
*   **Scheduling via AgentRouter**: Decouples agent identity from execution. The same agent can be routed to different runtimes (Claude Code, Codex, OpenClaw, Hermes) based on the task requirements [README.md:115-122]().
*   **Capability Sharing**: Transforms private agents into shared organizational assets that can be recruited or borrowed by other team members [README.md:127-133]().
*   **Structured Collaboration**: Moves work beyond chat into tasks, documents, and shared files, with human-in-the-loop checkpoints for high-stakes actions [README.md:137-145]().
*   **Governance & Audit**: Centralized control over credentials, document access, and tool execution with full audit trails [README.md:149-156]().

### High-Level Architecture

AgentSpace is built as a TypeScript monorepo using Turbo. It separates the presentation layer (Web/CLI) from the execution layer (Daemon) and the business logic (Services).

#### System Context Diagram
This diagram illustrates how the various components of the AgentSpace ecosystem interact, bridging the user-facing "Natural Language Space" with the underlying "Code Entity Space".

```mermaid
graph TD
    subgraph "User Interface Layer"
        Web["apps/web (Next.js)"]
        CLI["apps/cli (Node.js)"]
    end

    subgraph "Backend Services Layer"
        Services["@agent-space/services"]
        DB["@agent-space/db (PostgreSQL)"]
        Domain["@agent-space/domain (Types)"]
    end

    subgraph "Execution Layer (Daemon)"
        Daemon["packages/daemon"]
        Router["AgentRouter (in @agent-space/daemon)"]
        Sandbox["@agent-space/sandbox"]
    end

    Web --> Services
    CLI --> Services
    Services --> DB
    Services -.-> Domain
    
    Daemon -- "Polls Tasks" --> Web
    Daemon --> Router
    Router --> Sandbox
    
    subgraph "External Runtimes"
        Claude["Claude Code"]
        Codex["Codex CLI"]
        OpenClaw["OpenClaw"]
    end
    
    Router --> Claude
    Router --> Codex
    Router --> OpenClaw
```
Sources: [README.md:72-78](), [README.md:202-218]()

### Monorepo Structure

The codebase is organized into `apps` and `packages` to ensure separation of concerns and reusability across the Web and CLI interfaces.

| Category | Path | Description |
| :--- | :--- | :--- |
| **Apps** | `apps/web` | The Next.js web application providing the workspace UI and Daemon API [README.md:63](). |
| | `apps/cli` | Command-line interface for managing workspaces and running agents locally [README.md:207](). |
| **Packages** | `packages/daemon` | The background process that executes agent tasks via `AgentRouter` [README.md:208](). |
| | `packages/services` | Core business logic: workspace management, permissions, and task lifecycle. |
| | `packages/db` | Database schema and repository layer for PostgreSQL [README.md:14](). |
| | `packages/domain` | Shared TypeScript types and interfaces used across the monorepo. |
| | `packages/sandbox` | Isolation layer for executing agent code safely. |

For a detailed breakdown of each package and its dependencies, see **[Monorepo Package Structure](#1.2)**.

### Execution Workflow

AgentSpace utilizes a "Pull-based" execution model. The web server acts as the coordinator, while one or more Daemons poll for work.

#### Task Execution Sequence
This diagram shows the relationship between the `Task` entity in the database and the execution flow within the `Daemon`.

```mermaid
sequenceDiagram
    participant S as Web Server (apps/web)
    participant D as Daemon (packages/daemon)
    participant R as AgentRouter
    participant H as Provider Harness (e.g. Claude Code)

    D->>S: GET /api/daemon/tasks/claim (Auth: DaemonToken)
    S-->>D: TaskBundle (Domain.Task)
    D->>R: detectAndRun(TaskBundle)
    R->>H: spawn(ProviderCLI)
    H-->>R: RuntimeEvents
    R-->>D: Stream Results
    D->>S: POST /api/daemon/tasks/complete (OutputBundle)
```
Sources: [README.md:115-123](), [README.md:137-145]()

### Getting Started

AgentSpace can be deployed in two modes:
1.  **Platform (Cloud)**: Hosted version for immediate use [README.md:74]().
2.  **Self-hosted**: Full control over infrastructure, runtimes, and data [README.md:75]().

To begin development or local deployment, see **[Getting Started & Configuration](#1.1)**.

---
**Child Pages:**
*   **[Getting Started & Configuration](#1.1)**: Environment setup, database initialization, and deployment modes.
*   **[Monorepo Package Structure](#1.2)**: In-depth guide to the `apps/` and `packages/` directories.

---

# Page: Getting Started & Configuration

# Getting Started & Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [README.md](README.md)
- [README_ZH.md](README_ZH.md)

</details>



AgentSpace is a collaborative workspace designed for human-agent teams. This page provides technical instructions for setting up the environment, configuring deployment modes, and initializing the system for first-run execution.

## Deployment Modes

AgentSpace supports two primary deployment modes, controlled by the `AGENT_SPACE_DEPLOYMENT_MODE` environment variable [.env.example:4-4](). The application resolves database and attachment storage settings based on this selection [.env.example:42-44]().

| Mode | Database | Attachment Storage | Use Case |
| :--- | :--- | :--- | :--- |
| `self_hosted` | Local PostgreSQL | Local Filesystem | Local development, private infrastructure. |
| `cloud` | Neon PostgreSQL | Cloudflare R2 | Production-scale, serverless deployments. |

### Configuration Flow Diagram
The following diagram illustrates how the system initializes its core resources based on the environment configuration.

"Configuration and Resource Initialization"
```mermaid
graph TD
    ENV["Environment Variables (.env)"] --> MODE_CHECK{"AGENT_SPACE_DEPLOYMENT_MODE"}
    
    MODE_CHECK -- "self_hosted" --> DB_LOCAL["SELF_HOSTED_DATABASE_URL"]
    MODE_CHECK -- "self_hosted" --> STORAGE_LOCAL["SELF_HOSTED_ATTACHMENT_LOCAL_ROOT"]
    
    MODE_CHECK -- "cloud" --> DB_NEON["NEON_DATABASE_URL"]
    MODE_CHECK -- "cloud" --> STORAGE_R2["CLOUDFLARE_R2_BUCKET"]
    
    DB_LOCAL --> DB_INIT["Prisma Client / @agent-space/db"]
    DB_NEON --> DB_INIT
    
    STORAGE_LOCAL --> ATTACH_SERVICE["Attachment Service"]
    STORAGE_R2 --> ATTACH_SERVICE
    
    DB_INIT --> APP_START["Next.js / apps/web"]
    ATTACH_SERVICE --> APP_START
```
**Sources:** [.env.example:1-44]()

---

## Environment Variables

A `.env` file must be created in the root directory. Use `.env.example` as a template [.env.example:1-82]().

### Core System Settings
*   `AGENT_SPACE_APP_URL`: The base URL for the web application (e.g., `http://127.0.0.1:1455`) [.env.example:56-56]().
*   `NEXT_SERVER_ACTIONS_ENCRYPTION_KEY`: A base64 encoded 32-byte key required for Next.js Server Actions in production [.env.example:58-62]().
*   `AGENT_SPACE_OAUTH_STATE_SECRET`: A long random string used to sign OAuth state cookies [.env.example:65-65]().

### Database Configuration
*   **Self-Hosted**: Requires `SELF_HOSTED_DATABASE_URL` and `SELF_HOSTED_DATABASE_DIRECT_URL` (typically the same for local Postgres) [.env.example:7-8]().
*   **Cloud**: Requires Neon-specific variables including `NEON_DATABASE_URL`, `NEON_DATABASE_USER`, and `NEON_DATABASE_POOLER_HOST` [.env.example:16-21]().

### Storage Configuration
*   **Self-Hosted**: `SELF_HOSTED_ATTACHMENT_LOCAL_ROOT` defines the directory where workspace files are stored [.env.example:11-11]().
*   **Cloud**: Requires Cloudflare R2 credentials including `CLOUDFLARE_R2_ACCESS_KEY_ID`, `CLOUDFLARE_R2_SECRET_ACCESS_KEY`, and `CLOUDFLARE_R2_BUCKET` [.env.example:32-40]().
*   `ATTACHMENT_SIGNED_URL_TTL_SECONDS`: Expiry time for generated download/upload links (default: 300) [.env.example:47-47]().

### Authentication & Integrations
*   **Google Login**: Set `AGENT_SPACE_GOOGLE_CLIENT_ID` and `SECRET` to enable user authentication via Google [.env.example:68-70]().
*   **Google Workspace**: To allow agents to access Sheets/Docs, configure `AGENT_SPACE_GOOGLE_WORKSPACE_CLIENT_ID` and the `TOKEN_ENCRYPTION_KEY` [.env.example:74-79]().

**Sources:** [.env.example:1-82]()

---

## Database Initialization

AgentSpace requires PostgreSQL 16 or higher [README.md:14-14](). The initialization process involves installing dependencies, generating the Prisma client, and running migrations.

### Setup Steps
1.  **Install Dependencies**: Use `npm install` at the root.
2.  **Initialize**: Run the setup script which prepares the environment and database [README.md:63-63]().
    ```bash
    npm run setup
    ```
3.  **Start Development Server**:
    ```bash
    npm run dev:web
    ```

### Data Model Mapping
This diagram bridges the "Natural Language Space" of workspace concepts to the "Code Entity Space" found in `@agent-space/db`.

"Workspace Entity Mapping"
```mermaid
classDiagram
    class Workspace {
        +String slug
        +String name
    }
    class DigitalEmployee {
        +String role
        +String ownerId
        +String runtimeBinding
    }
    class TaskRecord {
        +String status
        +String inputBundle
        +String outputBundle
    }
    class ApprovalRequest {
        +String type
        +Boolean isApproved
    }

    Workspace "1" -- "*" DigitalEmployee : "contains"
    DigitalEmployee "1" -- "*" TaskRecord : "executes"
    TaskRecord "1" -- "*" ApprovalRequest : "triggers"
```
**Sources:** [README.md:55-60](), [README.md:115-158]()

---

## First-Run Steps & Daemon Connectivity

Once the web application is running, the system requires an execution environment (the Daemon) to process agent tasks.

### Path A: Local Execution
The simplest way to start is running the web app and daemon locally. The web app serves the UI and API, while the daemon polls for tasks.
*   **Web**: `npm run dev:web` [README.md:63-63]()
*   **Daemon**: `npm run dev:daemon` (run in a separate terminal)

### Path B: Remote Daemon Setup
For production or distributed execution, a daemon can be installed on a remote host.
1.  Navigate to **Settings > Daemons** in the Web UI.
2.  Generate a **Daemon Token**.
3.  Run the provided installation script on the remote machine to register the daemon with the server [README.md:208-208]().

### Task Execution Flow
The following diagram maps the lifecycle of a task from the web UI to the code entities in the daemon.

"Task Lifecycle and Daemon Interaction"
```mermaid
sequenceDiagram
    participant User as "User (apps/web)"
    participant Server as "Server (@agent-space/services)"
    participant DB as "Database (@agent-space/db)"
    participant Daemon as "Daemon (@agent-space/daemon)"
    participant Router as "AgentRouter (@agent-space/services)"

    User->>Server: Create Task (Server Action)
    Server->>DB: Insert TaskRecord (Pending)
    Daemon->>Server: Poll for Tasks (GET /api/daemon/tasks/claim)
    Server->>DB: Update TaskRecord (Claimed)
    Server-->>Daemon: Return Task Bundle
    Daemon->>Router: Invoke detectRuntime()
    Router-->>Daemon: Return Harness (e.g., Claude Code)
    Daemon->>Router: run(taskInput)
    Router-->>Daemon: Stream Events / Result
    Daemon->>Server: Submit Output (POST /api/daemon/tasks/complete)
    Server->>DB: Update TaskRecord (Completed)
```
**Sources:** [README.md:115-123](), [README.md:142-145](), [.env.example:56-56]()

**Sources:**
*   [.env.example:1-82]()
*   [README.md:1-228]()
*   [README_ZH.md:1-228]()

---

# Page: Monorepo Package Structure

# Monorepo Package Structure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [apps/cli/package-lock.json](apps/cli/package-lock.json)
- [apps/cli/package.json](apps/cli/package.json)
- [apps/cli/tsconfig.json](apps/cli/tsconfig.json)

</details>



This page provides a detailed technical map of the AgentSpace monorepo. AgentSpace is organized as a TypeScript monorepo using file-based dependencies to manage relationships between the web application, CLI, and core logic packages.

## Monorepo Overview

The repository is divided into two main categories: `apps/` (end-user entry points) and `packages/` (reusable business logic, data models, and infrastructure abstractions).

### Dependency Graph

The following diagram illustrates the internal dependency flow between packages.

**Internal Package Dependencies**
```mermaid
graph TD
    subgraph Apps ["apps/"]
        WEB["@agent-space/web (Next.js)"]
        CLI["@agent-space/cli"]
    end

    subgraph Packages ["packages/"]
        DAEMON["agent-space-daemon"]
        SERVICES["@agent-space/services"]
        DB["@agent-space/db"]
        DOMAIN["@agent-space/domain"]
        SANDBOX["@agent-space/sandbox"]
    end

    WEB --> SERVICES
    WEB --> DOMAIN
    
    CLI --> SERVICES
    CLI --> DAEMON
    CLI --> DB
    CLI --> DOMAIN

    DAEMON --> SERVICES
    DAEMON --> SANDBOX
    DAEMON --> DB
    DAEMON --> DOMAIN

    SERVICES --> DB
    SERVICES --> DOMAIN

    DB --> DOMAIN
    SANDBOX --> DOMAIN
```
**Sources:** [apps/cli/package.json:14-19](), [apps/cli/package-lock.json:25-46](), [apps/cli/package-lock.json:66-75]()

---

## Core Packages

### 1. `@agent-space/domain`
The foundational package containing TypeScript interfaces, enums, and constants shared across the entire stack. It defines the "language" of the system.
*   **Role:** Type definitions for Workspaces, Tasks, Digital Employees, and API contracts.
*   **Key Entities:** `WorkspaceState`, `TaskRecord`, `ApprovalRequest`.
*   **Sources:** [apps/cli/tsconfig.json:13-15]()

### 2. `@agent-space/db`
The data access layer. It abstracts PostgreSQL interactions using the `pg` driver.
*   **Role:** Repository functions for 50+ tables, migration management, and synchronous worker-thread query execution.
*   **Implementation:** Provides direct access to the database for the CLI and Daemon, while the Web app typically accesses it via `@agent-space/services`.
*   **Sources:** [apps/cli/package-lock.json:47-60]()

### 3. `@agent-space/services`
The business logic layer.
*   **Role:** Implements complex workflows such as employee lifecycle management, task dispatching, and permission checks (`assertCanUse*`).
*   **Data Flow:** Consumes `@agent-space/db` to persist state and `@agent-space/domain` for type safety. It is the primary dependency for both the Web and CLI apps.
*   **Sources:** [apps/cli/package-lock.json:66-75]()

### 4. `@agent-space/sandbox`
The execution isolation layer.
*   **Role:** Defines the `Sandbox` interface (methods: `readFile`, `writeFile`, `exec`, `snapshot`) to abstract where code runs.
*   **Implementations:** Includes `LocalSandbox` (host filesystem) and `CubeSandbox` (isolated containers).
*   **Sources:** [apps/cli/tsconfig.json:20-20]()

### 5. `agent-space-daemon`
The agent execution engine.
*   **Role:** A background process that polls the server for tasks, manages runtimes via `AgentRouter`, and reports results.
*   **Key Components:** `AgentRouter` (harness normalization for Claude Code, Codex, etc.) and `DaemonClient`.
*   **Sources:** [apps/cli/package-lock.json:25-46](), [apps/cli/tsconfig.json:21-23]()

---

## Application Entry Points

### 1. `apps/web`
A Next.js App Router application providing the collaborative UI.
*   **Workspace Shell:** Renders the multi-module UI at `/w/[workspaceSlug]`.
*   **Daemon API:** Hosts the HTTP endpoints that remote daemons poll (e.g., task claim, runtime approvals).
*   **Sources:** [README.md:144-147]()

### 2. `apps/cli`
The developer and administrative toolset.
*   **Role:** Provides commands for workspace management, database migrations, and local daemon control.
*   **Binary:** Exposed as `agent-space`.
*   **Sources:** [apps/cli/package.json:7-11]()

---

## Mapping Logic to Code Entities

The following diagrams bridge high-level system concepts to specific code structures.

### Task Execution Flow (Logic to Code)
This diagram shows how a "Task" moves from the Domain definition through the Service logic into the Daemon for execution.

```mermaid
graph LR
    subgraph Domain ["@agent-space/domain"]
        T_TYPE["TaskRecord (Interface)"]
    end

    subgraph Services ["@agent-space/services"]
        T_CREATE["createTask()"]
        T_DISPATCH["dispatchTask()"]
    end

    subgraph Daemon ["agent-space-daemon"]
        AR["AgentRouter.run()"]
        SB["Sandbox.exec()"]
    end

    T_TYPE -.-> T_CREATE
    T_CREATE --> T_DISPATCH
    T_DISPATCH -- "HTTP Poll" --> AR
    AR --> SB
```
**Sources:** [README.md:115-123](), [apps/cli/tsconfig.json:13-23]()

### Workspace Governance (Logic to Code)
This diagram maps the governance concepts to the permission guards and repository functions.

```mermaid
graph TD
    subgraph Permissions ["@agent-space/services"]
        GUARD["assertCanUseRuntime()"]
        GRANT["grantRuntimeUseToUser()"]
    end

    subgraph Data ["@agent-space/db"]
        REPO["WorkspaceRepository"]
        APPROVE["ApprovalRepository"]
    end

    subgraph UI ["apps/web"]
        MOD["WorkspaceFeatureModules"]
    end

    MOD --> GUARD
    GUARD --> REPO
    GRANT --> APPROVE
```
**Sources:** [README.md:130-134](), [apps/cli/package-lock.json:11-14]()

---

# Page: Core Architecture

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README_ZH.md](README_ZH.md)
- [apps/cli/package-lock.json](apps/cli/package-lock.json)

</details>



AgentSpace is built as a modular monorepo that separates business logic, data persistence, and agent execution into distinct layers. This architecture allows the system to support multiple interfaces (Web and CLI) while maintaining a unified governance and execution model.

## System Overview

The architecture is designed to bridge the gap between human collaboration (Web/CLI) and autonomous agent execution (Daemon).

### High-Level Component Interaction

The diagram below illustrates how the major packages and applications interact. The `services` layer acts as the central orchestrator, utilized by both the Web and CLI apps, while the `daemon` operates as a detached execution worker.

**AgentSpace Component Map**
```mermaid
graph TD
    subgraph "Interface Layer"
        WEB["apps/web (Next.js)"]
        CLI["apps/cli (Node.js)"]
    end

    subgraph "Business Logic Layer"
        SVC["@agent-space/services"]
        DOM["@agent-space/domain"]
    end

    subgraph "Data & Execution Layer"
        DB["@agent-space/db (PostgreSQL)"]
        DAEMON["agent-space-daemon"]
        SANDBOX["@agent-space/sandbox"]
    end

    WEB --> SVC
    CLI --> SVC
    SVC --> DB
    SVC --> DOM
    DAEMON --> SVC
    DAEMON --> SANDBOX
    DAEMON -- "Polls Task API" --> WEB
```
**Sources:** [apps/cli/package-lock.json:10-15](), [README.md:107-113]()

---

## Layered Subsystems

### Domain & Data Models (`@agent-space/domain`)
The foundation of the system is the `@agent-space/domain` package. It defines the "Language of the System," including shared TypeScript interfaces for workspaces, task records, and agent roles. By centralizing these types, AgentSpace ensures that a "Task" or an "Approval" has the same structure whether it is being rendered in the React UI or processed by the Daemon.

For details, see [Domain & Data Models](#2.1).

**Sources:** [apps/cli/package-lock.json:61-65]()

### Database Layer (`@agent-space/db`)
The `@agent-space/db` package manages the PostgreSQL schema and provides a repository-pattern interface for data access. It handles the persistence of over 50 tables, covering everything from digital employee profiles to granular audit trails of agent actions.

For details, see [Database Layer (@agent-space/db)](#2.2).

**Sources:** [apps/cli/package-lock.json:47-53]()

### Services Layer (`@agent-space/services`)
This is the "Brain" of the application. It contains the business logic for:
- **Employee Lifecycle**: Recruiting, transferring, and managing digital employees.
- **Task Dispatch**: Creating and routing tasks to the appropriate execution queue.
- **Governance**: Managing permissions and the human-in-the-loop approval queue.

Both `apps/web` and `apps/cli` depend on this package to ensure consistent behavior across different user interfaces.

For details, see [Services Layer (@agent-space/services)](#2.3).

**Sources:** [apps/cli/package-lock.json:66-75]()

### Sandbox Abstraction (`@agent-space/sandbox`)
The sandbox layer provides execution isolation. It defines a standard interface for interacting with the environment where agents run (e.g., reading/writing files, executing shell commands). This allows AgentSpace to support different execution environments, such as a `LocalSandbox` for development or a `CubeSandbox` for secure, isolated production runs.

For details, see [Sandbox Abstraction (@agent-space/sandbox)](#2.4).

**Sources:** [apps/cli/package-lock.json:31-31]()

---

## Execution Pipeline

The execution of agent work is decoupled from the web server. The `agent-space-daemon` is a standalone process that communicates with the server via the **Daemon API Routes**.

**Code Entity Mapping: Task Lifecycle**
```mermaid
sequenceDiagram
    participant U as User (apps/web)
    participant S as @agent-space/services
    participant D as agent-space-daemon
    participant R as AgentRouter
    participant B as @agent-space/sandbox

    U->>S: create_task (via Server Action)
    S->>S: assertCanUseRuntime()
    S->>D: Task available in queue
    D->>S: claimTask(daemonToken)
    D->>R: invoke(harness_adapter)
    R->>B: exec(command)
    B-->>R: stdout/stderr
    R-->>D: Normalized Event Stream
    D->>S: completeTask(outputBundle)
```

### Key Execution Components
| Component | Code Entity / Path | Role |
| :--- | :--- | :--- |
| **Daemon** | `agent-space-daemon` | Polls for tasks, manages local runtime state. |
| **Router** | `agent-router.js` | Normalizes different agent harnesses (Claude Code, Codex, etc.). |
| **Sandbox** | `packages/sandbox` | Provides the isolated filesystem and shell for the agent. |
| **API** | `/api/daemon` | The HTTP bridge between the daemon and the services layer. |

**Sources:** [README.md:115-125](), [apps/cli/package-lock.json:34-38]()

---

# Page: Domain & Data Models

# Domain & Data Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [apps/web/app/api/daemon/tasks/[taskId]/input-bundle/route.ts](apps/web/app/api/daemon/tasks/[taskId]/input-bundle/route.ts)
- [apps/web/app/api/daemon/tasks/[taskId]/output-bundle/route.ts](apps/web/app/api/daemon/tasks/[taskId]/output-bundle/route.ts)
- [apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/[approvalId]/route.ts](apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/[approvalId]/route.ts)
- [apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/route.ts](apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/route.ts)

</details>



The `@agent-space/domain` package serves as the single source of truth for the system's shared types and data contracts. It defines the structure of the collaborative workspace, the lifecycle of agent tasks, and the communication protocols between the **Web Server** and the **Daemon**.

## Workspace & Collaboration Models

The core of AgentSpace is the `WorkspaceState`, which represents a snapshot of the organizational context. This includes "Digital Employees" (agents), their owners, and their current readiness status.

### Workspace State Structure
The `WorkspaceState` is a computed view of the workspace, used extensively by the UI and the services layer to resolve permissions and agent identities [apps/web/app/api/daemon/tasks/[taskId]/input-bundle/route.ts:56-57]().

| Entity | Description |
| :--- | :--- |
| `ActiveEmployee` | An agent profile containing `name`, `owner`, `skills`, and `runtimeBinding`. |
| `ChannelRecord` | A communication context (Direct or Group) where humans and agents interact. |
| `AgentDocumentContext` | The association between an agent and specific documents/knowledge bases [apps/web/app/api/daemon/tasks/[taskId]/input-bundle/route.ts:74-78](). |

**Sources:** [apps/web/app/api/daemon/tasks/[taskId]/input-bundle/route.ts:21-28](), [apps/web/app/api/daemon/tasks/[taskId]/input-bundle/route.ts:56-62]()

---

## Task & Execution Models

Tasks are the primary unit of work. They transition through a lifecycle from `Queued` to `Running`, and finally to `Completed` or `Failed`.

### Task Lifecycle Data Flow
When a task is picked up by a daemon, it moves from a database record (`QueuedTaskRecord`) to a `DaemonTaskInputBundle`.

#### 1. Input Bundle (`DaemonTaskInputBundle`)
The input bundle is a self-contained JSON payload that the daemon uses to initialize the agent's environment. It contains:
*   **Prompt**: The system and user instructions for the agent [apps/web/app/api/daemon/tasks/[taskId]/input-bundle/route.ts:152-154]().
*   **Metadata**: Information about Google Workspace tokens, runtime capabilities, and session history [apps/web/app/api/daemon/tasks/[taskId]/input-bundle/route.ts:122-149]().
*   **Files**: Base64 encoded files (like `task.json` and `prompt.txt`) required for the execution sandbox [apps/web/app/api/daemon/tasks/[taskId]/input-bundle/route.ts:150-173]().

#### 2. Output Bundle (`DaemonTaskOutputBundle`)
Upon completion, the daemon submits an output bundle back to the server via `POST /api/daemon/tasks/[taskId]/output-bundle` [apps/web/app/api/daemon/tasks/[taskId]/output-bundle/route.ts:11-14]().
*   **Artifacts**: Files generated during the task (e.g., code, reports, images) [apps/web/app/api/daemon/tasks/[taskId]/output-bundle/route.ts:39-45]().
*   **Status**: Final execution state and logs.

### Diagram: Task Data Transformation
This diagram bridges the **Natural Language Space** (Task Prompt) to the **Code Entity Space** (Data Models).

```mermaid
graph TD
    subgraph "Natural Language Space"
        UserPrompt["User Instruction / Message"]
    end

    subgraph "Code Entity Space (@agent-space/domain)"
        QTR["QueuedTaskRecord (DB)"]
        DTIB["DaemonTaskInputBundle (JSON)"]
        DTOB["DaemonTaskOutputBundle (JSON)"]
        
        QTR -- "prepareDaemonTaskContext()" --> DTIB
        DTIB -- "Daemon Execution" --> DTOB
    end

    UserPrompt --> QTR
    DTIB -- "includes" --> PromptFile["prompt.txt"]
    DTIB -- "includes" --> TaskJSON["task.json"]
    DTOB -- "materializeOutputBundleToStaging()" --> Artifacts["File System / R2"]

    style QTR stroke-dasharray: 5 5
    style DTIB stroke-width: 2px
```
**Sources:** [apps/web/app/api/daemon/tasks/[taskId]/input-bundle/route.ts:116-174](), [apps/web/app/api/daemon/tasks/[taskId]/output-bundle/route.ts:26-32]()

---

## Governance & Approval Models

AgentSpace implements a "Human-in-the-loop" model for sensitive operations. These are represented by the `ApprovalRequest` domain type.

### Runtime Approvals
When an agent attempts a restricted action (e.g., a tool call in Claude Code), the daemon pauses and creates a `CreateRuntimeApprovalRequest` [apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/route.ts:23-24]().

| Field | Description |
| :--- | :--- |
| `approvalId` | Unique identifier for the request [apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/route.ts:45](). |
| `status` | Current state: `pending`, `approved`, or `rejected` [apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/[approvalId]/route.ts:30](). |
| `toolName` | The name of the tool requiring approval [apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/route.ts:35](). |
| `contentPreview` | A snippet of the data or action for the human reviewer [apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/route.ts:37](). |

### Diagram: Approval Request Flow
This diagram shows how the system bridges the **Daemon API** to the **Domain Models**.

```mermaid
sequenceDiagram
    participant D as Daemon (agent-space-daemon)
    participant S as Web Server (apps/web)
    participant DB as Database (@agent-space/db)

    D->>S: POST /api/daemon/tasks/[taskId]/runtime-approvals
    Note right of S: Body: CreateRuntimeApprovalRequest
    S->>S: createRuntimeToolApprovalRequestSync()
    S->>DB: INSERT INTO "Approval"
    S-->>D: { approvalId, status: "pending" }
    
    loop Polling
        D->>S: GET /api/daemon/tasks/[taskId]/runtime-approvals/[approvalId]
        S->>DB: SELECT status FROM "Approval"
        S-->>D: { status: "approved", reviewerComment: "..." }
    end
```
**Sources:** [apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/route.ts:8-41](), [apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/[approvalId]/route.ts:7-34]()

---

## Daemon API Contracts

The communication between the Web Server and the Daemon is strictly typed to ensure compatibility across different deployment modes.

### Key API Routes & Models

1.  **Input Bundle Retrieval**: `GET /api/daemon/tasks/[taskId]/input-bundle`
    *   Returns: `DaemonTaskInputBundle`
    *   Logic: Resolves agent profiles, Google Workspace tokens, and document contexts [apps/web/app/api/daemon/tasks/[taskId]/input-bundle/route.ts:36-116]().
2.  **Output Bundle Submission**: `POST /api/daemon/tasks/[taskId]/output-bundle`
    *   Accepts: `DaemonTaskOutputBundle`
    *   Logic: Materializes files to staging and records `artifact_detected` events [apps/web/app/api/daemon/tasks/[taskId]/output-bundle/route.ts:32-43]().
3.  **Approval Management**: `POST /api/daemon/tasks/[taskId]/runtime-approvals`
    *   Accepts: `CreateRuntimeApprovalRequest`
    *   Logic: Triggers notifications in the workspace channel if a channel is associated with the task [apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/route.ts:31-41]().

**Sources:** [apps/web/app/api/daemon/tasks/[taskId]/input-bundle/route.ts:20-21](), [apps/web/app/api/daemon/tasks/[taskId]/output-bundle/route.ts:2-6](), [apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/route.ts:1-2]()

---

# Page: Database Layer (@agent-space/db)

# Database Layer (@agent-space/db)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [apps/cli/src/commands/db.test.ts](apps/cli/src/commands/db.test.ts)
- [apps/cli/src/commands/db.ts](apps/cli/src/commands/db.ts)

</details>



The `@agent-space/db` package serves as the persistence engine for the entire AgentSpace ecosystem. It manages a PostgreSQL schema comprising over 50 tables, handles database migrations, and implements a unique synchronous query model designed to bridge the gap between asynchronous database drivers and synchronous CLI/Worker environments.

## Architecture & Query Model

AgentSpace utilizes a **synchronous worker-thread query model**. While modern Node.js database drivers (like `pg` or `kysely`) are inherently asynchronous, the AgentSpace CLI and certain daemon internal processes require synchronous access to the database state to simplify control flow and state management.

### Synchronous Bridge Implementation
The database layer exposes `*Sync` functions (e.g., `readWorkspaceSync`, `getDatabaseStatusSync`) by spawning a persistent worker thread that manages the actual asynchronous connection pool. Communication between the main thread and the database worker is handled via `SharedArrayBuffer` and atomic operations to block execution until the result is returned.

### Data Flow: Sync Query Path
The following diagram illustrates how a request from the CLI or Daemon reaches the PostgreSQL instance through the synchronous bridge.

**Diagram: Synchronous Database Access Flow**
```mermaid
sequenceDiagram
    participant App as "CLI / Daemon (Main Thread)"
    participant Bridge as "@agent-space/db (Sync Bridge)"
    participant Worker as "Database Worker Thread"
    participant PG as "PostgreSQL Instance"

    App->>Bridge: call readWorkspaceSync(id)
    Bridge->>Worker: postMessage({ action: "query", sql, params })
    Note over Bridge: Blocks main thread using Atomics.wait()
    Worker->>PG: execute async query
    PG-->>Worker: return rows
    Worker->>Bridge: signal completion via SharedArrayBuffer
    Bridge-->>App: return Workspace object
```
Sources: [apps/cli/src/commands/db.ts:1-4](), [apps/cli/src/commands/db.test.ts:6-11]()

## Storage Strategy & Paths

AgentSpace distinguishes between structured relational data (PostgreSQL) and unstructured storage artifacts (files, logs, and channel histories). The storage configuration is determined by the `AGENT_SPACE_DEPLOYMENT_MODE` environment variable.

### Deployment Modes
| Mode | Database | Attachment Storage |
| :--- | :--- | :--- |
| `self_hosted` | Local PostgreSQL | Local Filesystem |
| `cloud` | Neon (Serverless PG) | Cloudflare R2 (S3-compatible) |

### Key Storage Paths (Self-Hosted)
When running in `self_hosted` mode, the system uses specific directory structures for persistence:
*   **Workspaces:** `${SELF_HOSTED_ATTACHMENT_LOCAL_ROOT}/workspaces`
*   **Daemon State:** `${SELF_HOSTED_ATTACHMENT_LOCAL_ROOT}/daemon`
*   **Channel History:** Managed via `getWorkspaceChannelHistoryDirPath` to store markdown-based message logs.

Sources: [.env.example:1-11](), [apps/cli/src/commands/db.test.ts:7-11]()

## Core Repositories & Functions

The database layer provides a comprehensive set of repository functions categorized by domain entities. These functions are the primary interface for the `@agent-space/services` layer.

### Workspace & Task Management
These functions manage the lifecycle of collaborative environments and the execution units (tasks) assigned to agents.
*   `createWorkspaceSync(data)`: Initializes a new workspace record and associated metadata [apps/cli/src/commands/db.test.ts:35-40]().
*   `readWorkspaceSync(idOrSlug)`: Retrieves workspace details by its unique identifier or URL slug [apps/cli/src/commands/db.ts:31-34]().
*   `getDatabaseStatusSync()`: Returns diagnostic information about the database connection and migration state [apps/cli/src/commands/db.ts:11-14]().

### Storage & Maintenance Operations
The database layer includes utilities for scanning and purging storage to maintain consistency between the relational schema and the filesystem/R2.
*   **Storage Scanning:** `scanStorageArtifactsSync()` identifies "orphans"—files that exist on disk but have no corresponding database record (e.g., `orphan-workspace`, `orphan-channel-history`) [apps/cli/src/commands/db.test.ts:60-65]().
*   **Workspace Purging:** `purgeWorkspaceStorageSync(workspaceId)` performs a hard delete of all relational data and associated files for a specific workspace [apps/cli/src/commands/db.ts:39-40]().

**Diagram: Entity Relationship Overview**
```mermaid
erDiagram
    "Workspace" ||--o{ "Task" : contains
    "Workspace" ||--o{ "Channel" : owns
    "Workspace" ||--o{ "Employee" : employs
    "Task" ||--o{ "ApprovalRequest" : triggers
    "Task" ||--o{ "TokenUsage" : tracks
    "Daemon" ||--o{ "Task" : executes
    "User" ||--o{ "Workspace" : creates
    "User" ||--o{ "Grant" : holds
```
Sources: [apps/cli/src/commands/db.test.ts:35-40](), [apps/cli/src/commands/db.ts:21-42]()

## Database Management CLI

The `agent-space db` command provides a direct interface to the database layer for administrative tasks.

### Command Reference
| Subcommand | Purpose | Implementation |
| :--- | :--- | :--- |
| `status` | Checks DB connectivity and migration version. | `getDatabaseStatusSync()` |
| `storage-scan` | Detects orphaned files in workspace and daemon directories. | `scanStorageArtifactsSync()` |
| `workspace-purge` | Irreversibly deletes a workspace and all its files. | `purgeWorkspaceStorageSync()` |

### Example: Purging a Workspace
The purge operation is a two-step process: first, it verifies the workspace exists in the database using `readWorkspaceSync`, then it invokes the service-level purge which cleans up both the database and the physical storage root.

```typescript
// Internal logic in apps/cli/src/commands/db.ts
const workspace = readWorkspaceSync(workspaceIdentifier.trim());
if (workspace) {
  purgeWorkspaceStorageSync(workspace.id);
}
```
Sources: [apps/cli/src/commands/db.ts:21-42](), [apps/cli/src/commands/db.test.ts:68-101]()

## Configuration & Environment

The database layer initializes its connection pool based on the following environment variables:

*   **`SELF_HOSTED_DATABASE_URL`**: Primary connection string for local PostgreSQL.
*   **`NEON_DATABASE_URL`**: Connection string for Neon serverless PostgreSQL (used in `cloud` mode).
*   **`AGENT_SPACE_DEPLOYMENT_MODE`**: Determines whether to use local paths or cloud-native storage.
*   **`ATTACHMENT_LOCAL_ROOT`**: The base directory for file storage when not using R2.

Sources: [.env.example:4-21](), [.env.example:51-53]()

---

# Page: Services Layer (@agent-space/services)

# Services Layer (@agent-space/services)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/cli/src/commands/cost.test.ts](apps/cli/src/commands/cost.test.ts)
- [apps/cli/src/commands/cost.ts](apps/cli/src/commands/cost.ts)
- [apps/cli/src/commands/material.ts](apps/cli/src/commands/material.ts)
- [apps/cli/src/commands/skill.ts](apps/cli/src/commands/skill.ts)
- [apps/cli/src/commands/task.ts](apps/cli/src/commands/task.ts)
- [apps/cli/src/commands/workspace.test.ts](apps/cli/src/commands/workspace.test.ts)
- [apps/cli/src/commands/workspace.ts](apps/cli/src/commands/workspace.ts)

</details>



The Services Layer (`@agent-space/services`) acts as the central business logic orchestrator for AgentSpace. It sits between the data access layer (`@agent-space/db`) and the consumption interfaces (Web and CLI). It is responsible for enforcing workspace rules, managing the lifecycle of "Digital Employees" (agents), handling task dispatching, and providing a unified context for agents during execution.

## Core Responsibilities

The services layer is partitioned into several functional domains:
*   **Workspace Management**: Initialization, state resets, and summary reporting.
*   **Employee Lifecycle**: Creating, updating, and binding agents to specific runtimes.
*   **Task & Approval Workflow**: Enqueuing tasks, managing status transitions, and handling human-in-the-loop approvals.
*   **Knowledge & Skills**: Managing materials (knowledge base) and skill imports/exports.
*   **Cost & Budgeting**: Tracking token usage and enforcing USD limits across workspaces and agents.
*   **Runtime Context**: Providing agents with a "view" of the workspace (channels, entities, messages) during task execution.

## Architectural Data Flow

The following diagram illustrates how the Services Layer mediates between the storage layer and the execution clients.

### Service Layer Orchestration
```mermaid
graph TD
    subgraph "Clients"
        WEB["apps/web (Next.js Actions)"]
        CLI["apps/cli (Commands)"]
    end

    subgraph "@agent-space/services"
        WS_SVC["Workspace Service"]
        EMP_SVC["Employee Service"]
        TASK_SVC["Task/Approval Service"]
        SKILL_SVC["Skill Service"]
        COST_SVC["Cost/Budget Service"]
        CTX_SVC["Context Service"]
    end

    subgraph "@agent-space/db"
        REPOS["Repositories / Sync Queries"]
        SQL[("PostgreSQL")]
    end

    WEB --> WS_SVC
    CLI --> WS_SVC
    
    WS_SVC --> REPOS
    EMP_SVC --> REPOS
    TASK_SVC --> REPOS
    
    REPOS --> SQL
```
**Sources:** [apps/cli/src/commands/workspace.ts:1-10](), [apps/cli/src/commands/skill.ts:1-12](), [apps/cli/src/commands/cost.ts:9-15]()

## Key Service Modules

### 1. Workspace & Employee Management
The service handles the transition from a fresh installation to a functional organization. `initializeOrganizationSync` sets up the primary owner, default channels, and installs built-in skills.

*   **`initializeOrganizationSync`**: Creates the organization, owner, and default skills like `workspace-context`. [apps/cli/src/commands/workspace.test.ts:52-63]()
*   **`createEmployeeSync`**: Provisions a new digital employee. [apps/cli/src/commands/cost.test.ts:75-75]()
*   **`bindEmployeeRuntimeSync`**: Links an employee to a specific daemon runtime, enabling them to execute tasks. [apps/cli/src/commands/cost.test.ts:85-85]()

### 2. Task Execution & Dispatch
Tasks are created via `createTaskSync`. This service interacts with the DB to enqueue a "Native Task" which the daemon subsequently claims.

*   **`createTaskSync`**: Validates parameters and persists a new task. [apps/cli/src/commands/task.ts:46-51]()
*   **`updateTaskStatusSync`**: Manages the state machine for tasks (`todo`, `in_progress`, `blocked`, `done`). [apps/cli/src/commands/task.ts:102-102]()

### 3. Cost Control & Budgets
This module provides logic to prevent runaway AI costs. It supports workspace-wide, agent-specific, or channel-specific budgets.

| Function | Purpose |
| :--- | :--- |
| `listBudgetsWithSpentSync` | Returns budgets alongside real-time spent USD. |
| `upsertBudgetSync` | Creates or updates a budget limit with actions (warn/pause). |
| `checkAllBudgetsForAgentSync` | Logic used before task execution to ensure limits aren't exceeded. |

**Sources:** [apps/cli/src/commands/cost.ts:9-15](), [apps/cli/src/commands/cost.test.ts:105-113]()

### 4. Skill & Knowledge Management
Skills are portable units of capability (often containing code or prompts). The service layer handles their lifecycle and synchronization.

*   **`importWorkspaceSkillFromUrl`**: Downloads and installs skills from remote repositories. [apps/cli/src/commands/skill.ts:142-146]()
*   **`exportWorkspaceSkillsArchiveSync`**: Packages skills into a ZIP for sharing. [apps/cli/src/commands/skill.ts:102-105]()
*   **`addMaterialSync`**: Ingests raw data into the workspace knowledge base. [apps/cli/src/commands/material.ts:30-30]()

## Workspace Context (Agent Runtime View)

When an agent runs a task, it uses the "Workspace Context" services to understand its environment. This bridges the gap between raw database records and the entities the agent perceives.

### Context Resolution Flow
```mermaid
sequenceDiagram
    participant Agent as "Agent (Runtime)"
    participant CLI as "agent-space workspace context"
    participant SVC as "Context Service"
    participant DB as "Database"

    Agent->>CLI: resolve-entity --query "Assistant"
    CLI->>SVC: resolveWorkspaceContextEntitySync(agentName, query)
    SVC->>DB: listActiveEmployees()
    DB-->>SVC: [Employee: "Tianyu's assistant", Remark: "Assistant"]
    SVC-->>CLI: { entity: "Tianyu's assistant" }
    CLI-->>Agent: Result JSON
```
**Sources:** [apps/cli/src/commands/workspace.ts:95-103](), [apps/cli/src/commands/workspace.test.ts:30-50]()

### Environment Variables for Context
The context service relies on specific environment variables injected into the agent's sandbox to identify the caller:
*   `AGENT_SPACE_CONTEXT_AGENT_NAME`: The ID/Name of the agent executing the code. [apps/cli/src/commands/workspace.ts:15-15]()
*   `AGENT_SPACE_CONTEXT_TASK_ID`: The unique ID of the task currently being processed. [apps/cli/src/commands/workspace.ts:16-16]()

## Entity Mapping: Code to Logic

| Natural Language Concept | Code Entity (Service Layer) | Implementation File |
| :--- | :--- | :--- |
| **Digital Employee** | `ActiveEmployee` | `@agent-space/domain/workspace` |
| **Skill Import** | `importWorkspaceSkillFromUrl` | `packages/services/src/skill.ts` |
| **Budget Enforcement** | `checkAllBudgetsForAgentSync` | `packages/services/src/cost.ts` |
| **Context Search** | `searchWorkspaceContextMessagesSync` | `packages/services/src/context.ts` |
| **Initialization** | `initializeOrganizationSync` | `packages/services/src/workspace.ts` |

**Sources:** [apps/cli/src/commands/workspace.ts:1-10](), [apps/cli/src/commands/skill.ts:1-12](), [apps/cli/src/commands/workspace.test.ts:6-16]()

---

# Page: Sandbox Abstraction (@agent-space/sandbox)

# Sandbox Abstraction (@agent-space/sandbox)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [agent-space-daemon-0.1.3.tgz](agent-space-daemon-0.1.3.tgz)

</details>



The `@agent-space/sandbox` package provides the execution isolation layer for AgentSpace. It abstracts the underlying environment where agent code, tool calls, and shell commands are executed. This abstraction allows the system to support multiple execution backends—such as local processes or remote containerized environments—while providing a consistent interface for the daemon to manage file operations and process execution.

## The Sandbox Interface

All sandbox implementations must adhere to the `Sandbox` interface. This interface ensures that the daemon and agent runtimes can interact with the execution environment without needing to know the specific implementation details.

### Key Operations
*   **`readFile(path: string)`**: Retrieves the content of a file from the sandbox [agent-space-daemon-0.1.3.tgz:src/sandbox/interface.ts]().
*   **`writeFile(path: string, content: string | Buffer)`**: Writes data to a specific path within the sandbox [agent-space-daemon-0.1.3.tgz:src/sandbox/interface.ts]().
*   **`exec(command: string, options?: ExecOptions)`**: Executes a shell command within the sandbox context, returning streams for `stdout` and `stderr` [agent-space-daemon-0.1.3.tgz:src/sandbox/interface.ts]().
*   **`snapshot()`**: Captures the current state of the sandbox filesystem, which can be used for task persistence or debugging [agent-space-daemon-0.1.3.tgz:src/sandbox/interface.ts]().

**Sources:** [agent-space-daemon-0.1.3.tgz:src/sandbox/interface.ts]()

---

## Sandbox Implementations

AgentSpace currently provides two primary implementations of the sandbox abstraction: `LocalSandbox` and `CubeSandbox`.

### 1. LocalSandbox
The `LocalSandbox` executes commands directly on the host machine where the daemon is running. It uses the Node.js `child_process` module for execution and `fs` for file manipulation. This is the default for self-hosted setups where the daemon has direct access to the local environment.

*   **Isolation**: Limited to the process level and directory scoping.
*   **Performance**: High, as there is no containerization overhead.
*   **Use Case**: Local development and trusted self-hosted environments.

### 2. CubeSandbox
The `CubeSandbox` (often referred to in the context of remote execution) interfaces with a containerized environment. It is designed for higher isolation and security, ensuring that agent execution is sandboxed within a Docker-like container.

*   **Isolation**: Strong, using container boundaries.
*   **State Management**: Supports clean resets and snapshotting via the container engine API.
*   **Use Case**: Cloud-hosted AgentSpace or multi-tenant environments where security is paramount.

| Feature | LocalSandbox | CubeSandbox |
| :--- | :--- | :--- |
| **Backend** | Host OS / Node.js `fs` | Container Engine (Cube) |
| **Isolation Level** | Low (Process-based) | High (Container-based) |
| **Setup Complexity** | Low | Medium |
| **File Access** | Direct Path | API-based / Mounted Volumes |

**Sources:** [agent-space-daemon-0.1.3.tgz:src/sandbox/local.ts](), [agent-space-daemon-0.1.3.tgz:src/sandbox/cube.ts]()

---

## Data Flow and Execution

The Sandbox acts as the bridge between the high-level task logic in the Daemon and the low-level OS/Container operations.

### Execution Sequence Diagram
The following diagram illustrates how the `Daemon` uses the `Sandbox` to execute an agent task.

**Title: Sandbox Execution Flow**
```mermaid
sequenceDiagram
    participant D as "Daemon (@agent-space/daemon)"
    participant S as "Sandbox Interface"
    participant LS as "LocalSandbox / CubeSandbox"
    participant OS as "Execution Environment"

    D->>S: "writeFile('task.py', code)"
    S->>LS: "writeFile"
    LS->>OS: "fs.writeFileSync"
    
    D->>S: "exec('python3 task.py')"
    S->>LS: "exec"
    LS->>OS: "child_process.spawn"
    OS-->>LS: "stdout / stderr streams"
    LS-->>S: "ProcessResult"
    S-->>D: "Execution Output"
    
    D->>S: "readFile('output.log')"
    S->>LS: "readFile"
    LS->>OS: "fs.readFileSync"
    OS-->>D: "File Content"
```
**Sources:** [agent-space-daemon-0.1.3.tgz:src/daemon/task-processor.ts](), [agent-space-daemon-0.1.3.tgz:src/sandbox/local.ts]()

---

## Mapping Natural Language to Code Entities

To understand how the sandbox abstraction fits into the broader system, it is helpful to map the conceptual "Execution Space" to specific code entities.

### Entity Mapping: Sandbox Components
The diagram below maps the functional requirements of an execution environment to the classes and interfaces defined in the codebase.

**Title: Sandbox Entity Mapping**
```mermaid
graph TD
    subgraph "Natural Language Space"
        A["File Management"]
        B["Command Execution"]
        C["Environment Isolation"]
    end

    subgraph "Code Entity Space (@agent-space/sandbox)"
        A1["Sandbox.readFile()"]
        A2["Sandbox.writeFile()"]
        B1["Sandbox.exec()"]
        C1["LocalSandbox Class"]
        C2["CubeSandbox Class"]
        I["Sandbox Interface"]
    end

    A --> A1
    A --> A2
    B --> B1
    C --> C1
    C --> C2
    A1 & A2 & B1 -.-> I
    C1 & C2 -- "implements" --> I
```
**Sources:** [agent-space-daemon-0.1.3.tgz:src/sandbox/interface.ts](), [agent-space-daemon-0.1.3.tgz:src/sandbox/local.ts]()

### Task Lifecycle Integration
The `Daemon` uses the sandbox during the `claim` and `execute` phases of a task lifecycle.

**Title: Daemon to Sandbox Integration**
```mermaid
graph LR
    subgraph "Daemon Layer"
        DP["TaskProcessor"]
        AR["AgentRouter"]
    end

    subgraph "Sandbox Layer"
        SB["Sandbox Interface"]
        LS["LocalSandbox"]
    end

    DP -- "invokes" --> AR
    AR -- "requests execution" --> SB
    SB -- "delegates to" --> LS
    LS -- "interacts with" --> FS["Host Filesystem"]
```
**Sources:** [agent-space-daemon-0.1.3.tgz:src/daemon/task-processor.ts](), [agent-space-daemon-0.1.3.tgz:src/agent-router/index.ts]()

---

## Technical Details: Process Execution

The `exec` method is the most complex part of the sandbox. It handles:
1.  **Environment Variables**: Passing specific keys (like `OPENAI_API_KEY` or `WORKSPACE_ID`) to the child process [agent-space-daemon-0.1.3.tgz:src/sandbox/local.ts]().
2.  **Working Directory**: Ensuring the command runs in the correct workspace path [agent-space-daemon-0.1.3.tgz:src/sandbox/local.ts]().
3.  **Stream Handling**: Capturing `stdout` and `stderr` in real-time to provide feedback to the AgentSpace web UI [agent-space-daemon-0.1.3.tgz:src/sandbox/local.ts]().

```typescript
// Example of LocalSandbox.exec implementation detail
// [agent-space-daemon-0.1.3.tgz:src/sandbox/local.ts]
async exec(command: string, options: ExecOptions): Promise<ProcessResult> {
  const child = spawn(command, {
    shell: true,
    cwd: this.workDir,
    env: { ...process.env, ...options.env }
  });
  // ... stream handling logic ...
}
```

**Sources:** [agent-space-daemon-0.1.3.tgz:src/sandbox/local.ts](), [agent-space-daemon-0.1.3.tgz:src/sandbox/interface.ts]()

---

# Page: Daemon & Agent Execution

# Daemon & Agent Execution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [agent-space-daemon-0.1.3.tgz](agent-space-daemon-0.1.3.tgz)
- [apps/cli/src/commands/daemon.test.ts](apps/cli/src/commands/daemon.test.ts)
- [apps/cli/src/commands/daemon.ts](apps/cli/src/commands/daemon.ts)
- [apps/cli/src/lib/daemon-client.test.ts](apps/cli/src/lib/daemon-client.test.ts)
- [apps/cli/src/lib/daemon-client.ts](apps/cli/src/lib/daemon-client.ts)

</details>



The Daemon is the primary execution engine of AgentSpace. It acts as a bridge between the central server (which manages task queues and workspace state) and the local or remote compute environment where agent harnesses (like Claude Code or Codex) actually run. The execution pipeline is designed to be robust, supporting long-running tasks, streaming feedback, and human-in-the-loop approvals.

### Execution Pipeline Overview

The lifecycle of an agent execution follows a structured path from task discovery to result submission. The daemon continuously polls the server for new tasks assigned to the runtimes it supports. Once a task is claimed, the daemon prepares a secure execution environment, invokes the appropriate agent harness via `AgentRouter`, and monitors the process until completion.

Task execution is managed by the `runDaemonForeground` function [apps/cli/src/commands/daemon.ts:221-310](), which orchestrates the following high-level flow:

1.  **Registration**: The daemon registers its available runtimes with the server using `registerDaemonRuntimesSync` [apps/cli/src/commands/daemon.ts:55-55]().
2.  **Heartbeat**: A background loop maintains the daemon's "Online" status [apps/cli/src/commands/daemon.ts:44-44]().
3.  **Polling**: The daemon requests the next queued task for its active runtimes via `claimNextQueuedTaskForRuntimeSync` [apps/cli/src/commands/daemon.ts:36-36]().
4.  **Preparation**: The daemon builds a `DaemonTaskInputBundle` containing workspace state, relevant files, and conversation history.
5.  **Execution**: The task is handed off to the `runSharedProviderTask` [apps/cli/src/commands/daemon.ts:28-28](), which uses `AgentRouter` to select and invoke a harness.
6.  **Reporting**: Results are collected into an output bundle and submitted back to the server using `completeQueuedTaskSync` [apps/cli/src/commands/daemon.ts:37-37]() or `failQueuedTaskSync` [apps/cli/src/commands/daemon.ts:39-39]().

### System Component Interaction

The following diagram illustrates how the Daemon bridges the "Natural Language Space" (the user's intent and workspace) with the "Code Entity Space" (the actual execution logic and agent harnesses).

**Diagram: Daemon Execution Bridge**
```mermaid
graph TD
    subgraph "Natural Language Space (Server)"
        A["QueuedTaskRecord"] -- "claimed by" --> B["HttpDaemonClient"]
        C["WorkspaceState"] -- "bundled into" --> D["DaemonTaskInputBundle"]
    end

    subgraph "Daemon Execution Engine (packages/daemon)"
        B -- "invokes" --> E["runProviderTask"]
        E -- "routes to" --> F["AgentRouter"]
        F -- "manages" --> G["HarnessAdapter"]
    end

    subgraph "Code Entity Space (Runtimes)"
        G -- "spawns" --> H["Claude Code / Codex / Hermes"]
        H -- "writes to" --> I["agent-output.json"]
        I -- "collected by" --> J["collectRuntimeOutputBundle"]
    end

    J -- "results to" --> B
    B -- "submits" --> K["completeQueuedTaskSync"]
```
Sources: [apps/cli/src/commands/daemon.ts:17-61](), [apps/cli/src/lib/daemon-client.ts:1-2](), [agent-space-daemon-0.1.3.tgz]()

---

### Key Execution Subsystems

#### [AgentRouter & Harness Adapters](#3.1)
The `AgentRouter` is the normalization layer that allows AgentSpace to support diverse agent implementations. It abstracts the specifics of different agent harnesses into a unified interface for running tasks, detecting capabilities, and merging event streams. 
*   **Harness Normalization**: Maps AgentSpace tasks to harness-specific CLI commands or API calls.
*   **Event Merging**: Consolidates stdout, stderr, and structured tool calls into a unified event log.
*   **For details, see [AgentRouter & Harness Adapters](#3.1).**

#### [Provider Runtime & Task Lifecycle](#3.2)
This subsystem handles the state machine of a task. It manages the transition from `QUEUED` to `RUNNING`, and finally to `COMPLETED` or `FAILED`. It is responsible for:
*   **Input Bundling**: Preparing the `DaemonTaskInputBundle` which includes workspace context and file snapshots.
*   **Output Collection**: Using `loadTaskOutputEnvelope` [apps/cli/src/commands/daemon.ts:99-100]() to parse the `agent-output.json` manifest and process generated artifacts.
*   **Error Handling**: Categorizing failures using `normalizeProviderTaskErrorCategory` [apps/cli/src/commands/daemon.ts:23-23]().
*   **For details, see [Provider Runtime & Task Lifecycle](#3.2).**

#### [Remote Daemon Deployment](#3.3)
Daemons can run locally or on remote servers. Remote deployment involves:
*   **Authentication**: Using `DaemonApiToken` [apps/cli/src/commands/daemon.ts:38-38]() for secure communication with the central server.
*   **Process Management**: Running as a background service via `runDaemonStart` [apps/cli/src/commands/daemon.ts:147-220]() which handles PID files and logging.
*   **For details, see [Remote Daemon Deployment](#3.3).**

---

### Task Processing Logic

The daemon uses a polling mechanism to retrieve work. When a task is available, it establishes a local work directory using `getDaemonTaskWorkDirPath` [apps/cli/src/commands/daemon.ts:42-42]().

**Diagram: Task Lifecycle in Code**
```mermaid
sequenceDiagram
    participant S as Server (Next.js API)
    participant D as Daemon (runDaemonForeground)
    participant R as AgentRouter (runProviderTask)
    
    D->>S: claimNextQueuedTaskForRuntimeSync()
    S-->>D: QueuedTaskRecord
    D->>D: prepareDaemonTaskContext()
    D->>R: runSharedProviderTask(inputBundle)
    loop Execution
        R->>D: Stream Events / Approval Requests
        D->>S: updateTaskStatusSync() / appendTaskMessageSync()
    end
    R-->>D: RuntimeOutputBundle
    D->>D: loadTaskOutputEnvelope()
    D->>S: completeQueuedTaskSync(outputBundle)
```
Sources: [apps/cli/src/commands/daemon.ts:33-84](), [apps/cli/src/lib/daemon-task-context.ts:94-96](), [apps/cli/src/lib/daemon-task-output.ts:98-100]()

### Daemon Commands Reference

The `runDaemonCommand` [apps/cli/src/commands/daemon.ts:110-145]() provides the CLI interface for managing the daemon process:

| Command | Function | Description |
| :--- | :--- | :--- |
| `start` | `runDaemonStart` | Starts the daemon process (foreground or background). |
| `stop` | `runDaemonStop` | Stops the running daemon by reading the PID file. |
| `status` | `runDaemonStatus` | Displays active runtimes and daemon health. |
| `logs` | `runDaemonLogs` | Streams the daemon log file. |
| `token` | `runDaemonTokenCommand` | Manages API tokens for remote daemon authentication. |

Sources: [apps/cli/src/commands/daemon.ts:110-145]()

---

# Page: AgentRouter & Harness Adapters

# AgentRouter & Harness Adapters

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [README_ZH.md](README_ZH.md)
- [agent-space-daemon-0.1.3.tgz](agent-space-daemon-0.1.3.tgz)

</details>



The **AgentRouter** serves as the normalization and scheduling layer of the AgentSpace execution pipeline. It abstracts the idiosyncratic behaviors of various agent frameworks—such as **Claude Code**, **Codex**, **OpenClaw**, and **Hermes**—into a unified interface. This allows the same "Digital Employee" identity to execute tasks across different runtimes without losing context, skills, or governance oversight.

## Core Abstraction Layer

The primary goal of the AgentRouter is to decouple the agent's organizational identity (defined in the `DigitalEmployee` model) from the specific execution harness used for a task. This ensures that regardless of whether an agent is using a specialized coding harness like Claude Code or a general-purpose tool like Hermes, the event stream, file outputs, and approval requests remain consistent.

### The Unified Interface

The router implements a standard lifecycle for every agent run:
1.  **Capability Detection**: Identifying which harnesses are available on the current host.
2.  **Runtime Mapping**: Selecting the optimal harness based on the task requirements and agent configuration.
3.  **Event Normalization**: Mapping provider-specific output (e.g., terminal escapes, JSON chunks) into standard AgentSpace events.
4.  **Diagnostic Collection**: Gathering standardized logs and performance metrics across different providers.

### AgentRouter Architecture

The following diagram illustrates how the `AgentRouter` sits between the high-level Task management and the low-level provider CLIs.

**Diagram: AgentRouter Execution Flow**
```mermaid
graph TD
    subgraph "Natural Language Space"
        Task["Task Description"]
        Employee["DigitalEmployee Context"]
    end

    subgraph "AgentRouter (packages/daemon)"
        Router["AgentRouter.run()"]
        Detector["HarnessDetector"]
        HarnessFactory["HarnessFactory"]
    end

    subgraph "Harness Adapters"
        ClaudeHarness["ClaudeCodeHarness"]
        CodexHarness["CodexHarness"]
        OpenClawHarness["OpenClawHarness"]
        HermesHarness["HermesHarness"]
    end

    subgraph "Code Entity Space"
        CLI_Claude["claude-code CLI"]
        CLI_Codex["codex-cli"]
        CLI_Hermes["hermes-runtime"]
    end

    Task --> Router
    Employee --> Router
    Router --> Detector
    Detector --> HarnessFactory
    HarnessFactory --> ClaudeHarness
    HarnessFactory --> CodexHarness
    HarnessFactory --> HermesHarness

    ClaudeHarness --> CLI_Claude
    CodexHarness --> CLI_Codex
    HermesHarness --> CLI_Hermes
```
Sources: `README.md:115-123`(), `README_ZH.md:116-124`()

## Supported Harness Adapters

AgentRouter currently supports five primary runtimes, each specialized for different task types.

| Harness Name | Specialized For | Provider CLI |
| :--- | :--- | :--- |
| **Claude Code** | Complex engineering, refactoring, and codebase navigation. | `claude-code` |
| **Codex** | Rapid script generation and CLI automation. | `codex-cli` |
| **OpenClaw** | Multi-step reasoning and research tasks. | `openclaw` |
| **Hermes** | General-purpose agentic workflows and tool use. | `hermes` |
| **Nanobot** | Lightweight, fast-response utility tasks. | `nanobot` |

Sources: `README.md:83-84`(), `README_ZH.md:84-85`()

## Implementation Detail: The Adapter Pattern

Each adapter implements a common interface that the Daemon's `TaskRunner` consumes. This normalization happens in `packages/daemon`.

### Event Merging and Normalization

Different providers emit different event types (e.g., Claude Code might emit incremental terminal updates, while Hermes emits JSON tool-call events). The `AgentRouter` merges these into a standard stream:

1.  **Standard Output**: Captured and cleaned of terminal escape codes.
2.  **Tool Calls**: Intercepted and mapped to AgentSpace `ApprovalRequest` objects if they require human intervention.
3.  **File Changes**: Tracked via the `Sandbox` abstraction to generate `RuntimeOutput` records.

**Diagram: Data Flow and Normalization**
```mermaid
sequenceDiagram
    participant D as Daemon TaskRunner
    participant R as AgentRouter
    participant A as HarnessAdapter (e.g. ClaudeCodeHarness)
    participant P as Provider CLI

    D->>R: run(taskContext)
    R->>A: initialize(sandbox)
    A->>P: spawn process
    loop Execution
        P-->>A: Raw Stream (ANSI/JSON)
        A->>A: normalizeEvent()
        A-->>R: StandardEvent
        R-->>D: emit("runtime_event")
    end
    P-->>A: exit(code)
    A-->>R: FinalResult
    R-->>D: TaskCompletion
```
Sources: `README.md:97-101`(), `README_ZH.md:165-168`()

## Capability Diagnostics

Before a task is dispatched, the `AgentRouter` performs a **Capability Diagnostic**. This check ensures the host machine has the required binaries and environment variables configured for the chosen harness.

*   **Binary Discovery**: The router checks the system `PATH` for `claude`, `codex`, `hermes`, etc.
*   **Version Validation**: Ensures the CLI version meets the minimum requirements for the adapter.
*   **Credential Check**: Verifies that necessary API keys (e.g., `ANTHROPIC_API_KEY`) are present in the environment or the workspace vault.

## Integration with Sandbox

The `AgentRouter` does not run processes directly on the host. Instead, it interacts with the `@agent-space/sandbox` package. The adapter instructs the sandbox to `exec` the provider CLI within an isolated environment (either a `LocalSandbox` or a `CubeSandbox`).

This integration allows the `AgentRouter` to:
*   **ReadFile/WriteFile**: Provide the agent with necessary context files before execution.
*   **Snapshot**: Capture the state of the filesystem after a harness completes its run.
*   **Constraint**: Limit the harness's access to specific directories within the workspace.

Sources: `README.md:142-145`(), `README_ZH.md:144-145`()

---

# Page: Provider Runtime & Task Lifecycle

# Provider Runtime & Task Lifecycle

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/cli/src/commands/output.test.ts](apps/cli/src/commands/output.test.ts)
- [apps/cli/src/commands/output.ts](apps/cli/src/commands/output.ts)
- [apps/cli/src/lib/daemon-task-context.test.ts](apps/cli/src/lib/daemon-task-context.test.ts)
- [apps/cli/src/lib/daemon-task-context.ts](apps/cli/src/lib/daemon-task-context.ts)
- [apps/cli/src/lib/daemon-task-output.ts](apps/cli/src/lib/daemon-task-output.ts)
- [apps/cli/src/lib/runtime-output.ts](apps/cli/src/lib/runtime-output.ts)

</details>



The Provider Runtime and Task Lifecycle governs the end-to-end execution of agentic tasks within AgentSpace. This process spans from the initial task claim by a remote daemon to the final submission of output bundles. The lifecycle ensures that agents have the necessary context (skills, knowledge, and files) and that their execution is monitored, approved where necessary, and correctly reported back to the workspace.

## Task Claiming & Initialization

The daemon operates on a polling loop, communicating with the server via the `DaemonTaskClient`. When a task is available, the daemon "claims" it, transitioning the task state in the database from `queued` to `running`.

### Data Flow: Claim to Execution Context
1.  **Polling**: The daemon calls the server-side claim endpoint.
2.  **Payload Parsing**: The daemon receives a `QueuedTaskRecord` and parses the `inputJson` using `parseTaskInputJson` [packages/daemon/src/task-context.ts:36-36]().
3.  **Context Preparation**: The daemon invokes `prepareDaemonTaskContext` [apps/cli/src/lib/daemon-task-context.ts:7-7]() to build the execution environment. This includes:
    *   **Skill Materialization**: Skills assigned to the agent are written to the workspace using `materializeAgentSkills`, creating both provider-native (e.g., `.claude/skills`) and compatibility fallback directories [apps/cli/src/lib/daemon-task-context.test.ts:77-83]().
    *   **Knowledge Materialization**: Relevant knowledge pages are exported as Markdown files and a `manifest.json` via `materializeAgentKnowledgePages` [apps/cli/src/lib/daemon-task-context.test.ts:133-139]().
    *   **Prompt Construction**: A system prompt is generated by `buildTaskPrompt` which references the materialized context [apps/cli/src/lib/daemon-task-context.ts:2-2]().

### Task Initialization Diagram
"Task Initialization Flow"
```mermaid
graph TD
    subgraph "Server Space"
        DB[("QueuedTaskRecord")]
        API["/api/daemon/tasks/claim"]
    end

    subgraph "Daemon Space (packages/daemon)"
        TC["DaemonTaskClient"]
        CTX["prepareDaemonTaskContext"]
        SKILL["materializeAgentSkills"]
        KNOW["materializeAgentKnowledgePages"]
    end

    TC -- "poll" --> API
    API -- "JSON Payload" --> TC
    TC --> CTX
    CTX --> SKILL
    CTX --> KNOW
    SKILL -- "writes to" --> FS[(".agent_context/skills")]
    KNOW -- "writes to" --> FK[(".agent_context/knowledge")]
```
Sources: [apps/cli/src/lib/daemon-task-context.ts:1-13](), [apps/cli/src/lib/daemon-task-context.test.ts:77-139]()

## Provider Runtime Execution

Once the environment is prepared, the daemon uses the `AgentRouter` to invoke the specific provider harness (e.g., Claude Code, Codex).

### Input Bundling
The daemon creates a working directory (`workDir`) that serves as the root for the agent. The `AgentRouter` translates the unified task request into provider-specific commands. 
*   **Artifacts**: Input files are materialized via `materializeAttachments` [apps/cli/src/lib/daemon-task-context.ts:5-5]().
*   **Harness Invocation**: The router streams events (logs, tool calls) back to the server in real-time.

### Approvals & Human-in-the-Loop
During execution, agents may require permissions for sensitive operations.
*   **Permission Requests**: The agent can generate requests stored in `permission-requests.json` [apps/cli/src/lib/runtime-output.ts:12-12]().
*   **Polling for Approval**: The daemon pauses or checks the server status for these requests before allowing the agent to proceed with specific tool calls.

Sources: [apps/cli/src/lib/runtime-output.ts:1-22](), [apps/cli/src/lib/daemon-task-context.ts:1-13]()

## Output Bundling & Submission

As the agent completes its work, it generates various outputs. AgentSpace uses a structured manifest system located in the `runtime-output/` directory [apps/cli/src/lib/runtime-output.ts:3-3]().

### The Output Manifest System
The daemon and CLI provide utilities to append data to these manifests:
*   **`agent-output.json`**: Primary text response and file attachments [apps/cli/src/lib/runtime-output.ts:5-5]().
*   **`channel-documents.json`**: Upserts or edits to workspace documents [apps/cli/src/lib/runtime-output.ts:6-6]().
*   **`external-sheets.json`**: Operations for Google Sheets (append rows, update cells) [apps/cli/src/lib/runtime-output.ts:8-8]().
*   **`knowledge-proposals.json`**: Suggestions to create or update permanent knowledge base entries [apps/cli/src/commands/output.test.ts:197-200]().

### Submission Process
1.  **Validation**: The daemon calls `validateRuntimeOutputManifests` to ensure all paths and JSON structures are correct [apps/cli/src/commands/output.ts:18-18]().
2.  **Envelope Loading**: `loadTaskOutputEnvelope` aggregates all manifest files into a single object [apps/cli/src/lib/daemon-task-output.ts:4-4]().
3.  **Server Submission**: The daemon sends the final bundle to the server's completion endpoint.
4.  **Cleanup**: Artifacts are cleared via `clearTaskOutputArtifacts` [apps/cli/src/lib/daemon-task-output.ts:2-2]().

### Output Lifecycle Diagram
"Code Entities to Output Artifacts"
```mermaid
graph LR
    subgraph "CLI Commands (apps/cli/src/commands/output.ts)"
        CMD_ATTACH["runAttach"]
        CMD_DOC["runDocumentUpsert"]
        CMD_SHEET["runSheetsCommand"]
    end

    subgraph "Manifest Utils (packages/daemon/src/runtime-output-manifests.ts)"
        UTIL_ATTACH["appendAgentOutputAttachment"]
        UTIL_DOC["appendChannelDocumentManifestEntry"]
        UTIL_SHEET["appendExternalSheetOperation"]
    end

    subgraph "Filesystem (runtime-output/)"
        M_OUT["agent-output.json"]
        M_DOC["channel-documents.json"]
        M_SHT["external-sheets.json"]
    end

    CMD_ATTACH --> UTIL_ATTACH
    CMD_DOC --> UTIL_DOC
    CMD_SHEET --> UTIL_SHEET

    UTIL_ATTACH --> M_OUT
    UTIL_DOC --> M_DOC
    UTIL_SHEET --> M_SHT

    M_OUT -. "loadTaskOutputEnvelope" .-> SUBMIT["Server Submission"]
    M_DOC -.-> SUBMIT
    M_SHT -.-> SUBMIT
```
Sources: [apps/cli/src/commands/output.ts:37-88](), [apps/cli/src/lib/runtime-output.ts:3-22](), [apps/cli/src/lib/daemon-task-output.ts:1-6]()

## Key Implementation Details

| Component | File Path | Responsibility |
| :--- | :--- | :--- |
| **Manifest Definitions** | `packages/daemon/src/runtime-output-manifests.ts` | Types and append functions for output JSONs [apps/cli/src/commands/output.ts:3-29](). |
| **Output Paths** | `apps/cli/src/lib/runtime-output.ts` | Centralized constants for the `runtime-output/` directory structure [apps/cli/src/lib/runtime-output.ts:3-22](). |
| **Context Materializer** | `packages/daemon/src/task-context.ts` | Logic for writing skills and knowledge to the agent's disk [apps/cli/src/lib/daemon-task-context.ts:1-13](). |
| **CLI Output Bridge** | `apps/cli/src/commands/output.ts` | Allows agents to call CLI commands to register outputs (e.g., `agent-space output attach`) [apps/cli/src/commands/output.ts:95-124](). |

Sources: [apps/cli/src/commands/output.ts:1-33](), [apps/cli/src/lib/runtime-output.ts:1-22](), [apps/cli/src/lib/daemon-task-context.ts:1-13]()

---

# Page: Remote Daemon Deployment

# Remote Daemon Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/web/app/api/daemon/_lib/auth.ts](apps/web/app/api/daemon/_lib/auth.ts)
- [apps/web/app/api/daemon/_lib/distribution.ts](apps/web/app/api/daemon/_lib/distribution.ts)
- [apps/web/app/api/daemon/deregister/route.ts](apps/web/app/api/daemon/deregister/route.ts)
- [apps/web/app/api/daemon/heartbeat/route.ts](apps/web/app/api/daemon/heartbeat/route.ts)
- [apps/web/app/api/daemon/install-script/route.ts](apps/web/app/api/daemon/install-script/route.ts)
- [apps/web/app/api/daemon/onboarding-status/route.test.ts](apps/web/app/api/daemon/onboarding-status/route.test.ts)
- [apps/web/app/api/daemon/onboarding-status/route.ts](apps/web/app/api/daemon/onboarding-status/route.ts)
- [apps/web/app/api/daemon/register/route.ts](apps/web/app/api/daemon/register/route.ts)
- [apps/web/app/api/daemon/routes.test.ts](apps/web/app/api/daemon/routes.test.ts)

</details>



Remote Daemon Deployment refers to the process of provisioning and managing the `agent-space-daemon` on external hosts. The system is designed to facilitate easy onboarding via automated shell scripts, secure authentication using scoped API tokens, and a robust lifecycle managed through heartbeats and registration flows.

## Deployment Architecture

The deployment process follows a "pull-based" model where the remote host downloads the daemon package from the central AgentSpace server and authenticates via a pre-generated token.

### Data Flow & Component Interaction

The following diagram illustrates the interaction between the remote host, the Web Server API routes, and the Database layer during the deployment and execution lifecycle.

**Remote Daemon Lifecycle Overview**
```mermaid
sequenceDiagram
    participant Admin as Admin (Web UI)
    participant Host as Remote Host (Bash)
    participant Web as Web Server (API Routes)
    participant DB as Database (@agent-space/db)

    Admin->>Web: GET /api/daemon/install-script
    Web->>Admin: Shell Script (with Server URL)
    Admin->>Host: Execute Script + Token
    Host->>Web: GET /api/daemon/package (Auth: Bearer Token)
    Web-->>Host: daemon-tarball.tgz
    Host->>Host: Install & Start systemd service
    Host->>Web: POST /api/daemon/register
    Web->>DB: registerDaemonRuntimesSync()
    DB-->>Web: DaemonSnapshot
    Web-->>Host: Registered Runtimes Info
    loop Heartbeat
        Host->>Web: POST /api/daemon/heartbeat
        Web->>DB: heartbeatDaemonSync()
    end
```
Sources: [apps/web/app/api/daemon/install-script/route.ts:6-15](), [apps/web/app/api/daemon/register/route.ts:43-55](), [apps/web/app/api/daemon/heartbeat/route.ts:24-35]()

## Installation & Distribution

AgentSpace provides automated mechanisms to generate install scripts and distribute the daemon package.

### Install Script Generation
The server dynamically generates a shell script at `/api/daemon/install-script`. This script is based on a template located at `deploy/install-remote-daemon.sh` [apps/web/app/api/daemon/_lib/distribution.ts:83-85](). The generator function `buildHostedInstallScript` injects the current server's origin into the script so that the remote daemon knows where to pull updates and report heartbeats [apps/web/app/api/daemon/_lib/distribution.ts:6-17]().

### Package Distribution
The daemon is distributed as an NPM tarball. The `buildDaemonPackageTarball` function handles the packaging [apps/web/app/api/daemon/_lib/distribution.ts:19-72]():
1. It navigates to `packages/daemon` [apps/web/app/api/daemon/_lib/distribution.ts:87-89]().
2. It executes `npm pack` to create a production-ready distribution [apps/web/app/api/daemon/_lib/distribution.ts:37-45]().
3. It serves this tarball via the `/api/daemon/package` route, which requires valid daemon token authentication [apps/web/app/api/daemon/routes.test.ts:162-171]().

Sources: [apps/web/app/api/daemon/_lib/distribution.ts:6-98](), [apps/web/app/api/daemon/install-script/route.ts:1-16]()

## Authentication & Security

Remote daemons authenticate using a `DaemonApiToken`. This token is workspace-scoped, ensuring that a daemon cannot access tasks or runtimes belonging to another workspace.

### Token Validation
All daemon API routes (except the install script) utilize `requireDaemonAuth(request)`. This function:
1. Extracts the Bearer token from the `Authorization` header [apps/web/app/api/daemon/_lib/auth.ts:19-24]().
2. Validates it against the database using `validateDaemonApiTokenSync(tokenValue)` [apps/web/app/api/daemon/_lib/auth.ts:25-28]().
3. Returns a `DaemonAuthContext` containing the token record and the associated `workspaceId` [apps/web/app/api/daemon/_lib/auth.ts:30-33]().

### Cross-Workspace Protection
The system strictly enforces workspace boundaries. If a daemon attempts to access a resource (like a task or runtime) that does not belong to its authorized workspace, the system records a `workspace.cross_workspace_access_denied` audit event and returns a 403 Forbidden error [apps/web/app/api/daemon/_lib/auth.ts:90-110]().

Sources: [apps/web/app/api/daemon/_lib/auth.ts:13-88]()

## Lifecycle Management

The daemon lifecycle is managed through three primary states: `pending`, `online`, and `offline`.

### Registration (`/api/daemon/register`)
When a daemon starts for the first time, it sends a `RegisterDaemonRequest` containing its `daemonKey`, `deviceName`, and a list of available `runtimes` (e.g., Claude Code, Codex) [apps/web/app/api/daemon/register/route.ts:19-25]().
* **Function**: `registerDaemonRuntimesSync` creates the `daemon_connection` and `agent_runtime` records in the DB [apps/web/app/api/daemon/register/route.ts:43-55]().
* **Auto-Grant**: Upon registration, the system automatically grants the user who created the daemon token permission to use the newly registered runtimes via `grantRegisteredRuntimesToTokenCreator` [apps/web/app/api/daemon/register/route.ts:56-60]().

### Heartbeat (`/api/daemon/heartbeat`)
The daemon must periodically poll the heartbeat endpoint to remain `online`.
* **Payload**: Includes metadata about the host and the current status of its runtimes [apps/web/app/api/daemon/heartbeat/route.ts:14-35]().
* **Effect**: Updates the `lastHeartbeatAt` timestamp in the database. If heartbeats stop, the server-side logic eventually treats the daemon as offline.

### Deregistration (`/api/daemon/deregister`)
When a daemon shuts down gracefully (e.g., via `SIGTERM`), it calls the deregister route [apps/web/app/api/daemon/deregister/route.ts:7-31]().
* **Function**: `markDaemonOfflineSync` updates the status to `offline` and can optionally record a `lastError` if the shutdown was due to a failure [apps/web/app/api/daemon/deregister/route.ts:23-25]().

Sources: [apps/web/app/api/daemon/register/route.ts:13-98](), [apps/web/app/api/daemon/heartbeat/route.ts:8-53](), [apps/web/app/api/daemon/deregister/route.ts:7-31]()

## Daemon API Reference

The following table summarizes the core API routes used by the remote daemon for operational tasks.

| Route | Method | Purpose | Key Code Entity |
| :--- | :--- | :--- | :--- |
| `/api/daemon/install-script` | GET | Returns the shell script for host setup. | `buildHostedInstallScript` |
| `/api/daemon/package` | GET | Downloads the daemon tarball. | `buildDaemonPackageTarball` |
| `/api/daemon/register` | POST | Registers the host and its runtimes. | `registerDaemonRuntimesSync` |
| `/api/daemon/heartbeat` | POST | Updates online status and runtime metadata. | `heartbeatDaemonSync` |
| `/api/daemon/deregister` | POST | Marks the daemon as offline. | `markDaemonOfflineSync` |
| `/api/daemon/onboarding-status` | GET | Checks if a daemon has successfully connected. | `listDaemonSnapshotsSync` |

### Onboarding Status Verification
The `/api/daemon/onboarding-status` route is used by the Web UI to provide real-time feedback during the installation process [apps/web/app/api/daemon/onboarding-status/route.ts:8-45](). It checks if a `daemonKey` exists and returns the count and status of registered runtimes [apps/web/app/api/daemon/onboarding-status/route.test.ts:46-82]().

Sources: [apps/web/app/api/daemon/onboarding-status/route.ts:8-45](), [apps/web/app/api/daemon/onboarding-status/route.test.ts:1-145]()

---

# Page: Web Application (apps/web)

# Web Application (apps/web)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [apps/web/app/(workspace)/[...legacyPath]/page.tsx](apps/web/app/(workspace)/[...legacyPath]/page.tsx)
- [apps/web/app/error.tsx](apps/web/app/error.tsx)
- [apps/web/app/globals.css](apps/web/app/globals.css)

</details>



The AgentSpace web application is a high-performance collaborative environment built using the **Next.js App Router**. It serves as the primary interface for human-agent interaction, providing a unified workspace for managing digital employees, coordinating tasks, and governing organizational assets.

The application is architected around a **Module System** that allows for a persistent workspace shell while lazily loading feature-specific views. It bridges the gap between organizational management and real-time agent execution by providing a rich UI for the underlying services in `@agent-space/services` and the daemon API.

## Architecture Overview

The web application follows a layered structure within the `apps/web` directory, utilizing Next.js conventions for routing and server-side logic.

### Routing & Shell Structure
The core of the user experience resides under the `/(workspace)/[workspaceSlug]` route. This route implements a persistent **Workspace Shell** that includes the navigation sidebar, global search, and session management.

```mermaid
graph TD
    subgraph "Next.js App Router (apps/web/app)"
        Root["(root) layout.tsx"] --> Auth["(auth) routes"]
        Root --> Workspace["(workspace)/[workspaceSlug] layout.tsx"]
        
        subgraph "Workspace Shell"
            Workspace --> Sidebar["Sidebar.tsx"]
            Workspace --> ModuleContainer["Module Loader / Cache"]
        end
        
        subgraph "Feature Modules (apps/web/features)"
            ModuleContainer --> Agents["Agents Module"]
            ModuleContainer --> Channels["Channels Module"]
            ModuleContainer --> TaskBoard["Task Board Module"]
            ModuleContainer --> Knowledge["Knowledge Module"]
        end
    end

    subgraph "Data & Communication"
        Agents -- "Server Actions" --> Services["@agent-space/services"]
        DaemonAPI["/api/daemon"] -- "Polling" --> Daemon["agent-space-daemon"]
    end
```
**Sources:**
- [apps/web/app/(workspace)/[workspaceSlug]/layout.tsx:1-50]()
- [apps/web/app/(workspace)/[...legacyPath]/page.tsx:9-27]() (Legacy route mapping)

### System-to-Code Mapping

| System Concept | Code Entity | File Path |
|:---|:---|:---|
| **Workspace Shell** | `WorkspaceShell` | `apps/web/features/workspace/workspace-shell.tsx` |
| **Module Registry** | `WORKSPACE_MODULES` | `apps/web/features/workspace/module-registry.ts` |
| **Global Error Boundary** | `Error` component | [apps/web/app/error.tsx:5-45]() |
| **Styling System** | CSS Variables | [apps/web/globals.css:3-35]() |
| **Daemon Endpoints** | Route Handlers | `apps/web/app/api/daemon/route.ts` |

## Core Subsystems

### 4.1 Workspace Shell & Module System
The workspace shell provides the visual frame for all agent collaboration. It manages the **Module System**, which allows users to switch between features (like the Task Board or Agent Market) without full page reloads. It handles the workspace-specific sidebar, shell counters (notifications/pending tasks), and the module cache.

For details, see [Workspace Shell & Module System](#4.1).

### 4.2 Authentication & Google OAuth
AgentSpace uses a secure authentication flow primarily driven by **Google OAuth**. This system manages user sessions, workspace invitations, and access control. It ensures that sensitive agent operations are only performed by authorized personnel.

For details, see [Authentication & Google OAuth](#4.2).

### 4.3 Workspace Feature Modules
The functional heart of the application is divided into specialized modules:
- **Digital Employees:** Recruitment and lifecycle management of agents.
- **Channels:** Real-time messaging and coordination.
- **Task Board:** Visual tracking of agent task execution.
- **Governance:** Approvals, Skills, and Knowledge management.

For details, see [Workspace Feature Modules](#4.3).

### 4.4 Daemon API Routes
These are internal server-side HTTP endpoints located at `/api/daemon`. They act as the communication bridge between the **Web Server** and the **Remote Daemons**. The daemons poll these routes to claim tasks, report progress, and request runtime approvals.

For details, see [Daemon API Routes (Web Server Side)](#4.4).

### 4.5 Attachments & File Storage API
This subsystem handles the lifecycle of files within the workspace. It supports local filesystem storage for development and **Cloudflare R2** for production. The API manages secure uploads, signed URL generation, and attachment associations with tasks and messages.

For details, see [Attachments & File Storage API](#4.5).

## Visual Identity & Design System
The application uses a custom design system defined in `apps/web/app/globals.css`. It relies on CSS variables for theme management, supporting a professional, high-density interface suitable for complex organizational workflows.

```mermaid
graph LR
    subgraph "Design Tokens (globals.css)"
        Colors["--bg, --accent, --sidebar"]
        Typography["--font-body, --font-display"]
        Shadows["--shadow-md, --shadow-lg"]
    end

    subgraph "UI Components"
        Button[".button"]
        Card[".auth-card, .summary-card"]
        Panel[".page-panel, .form-panel"]
    end

    Colors --> Card
    Typography --> Panel
    Shadows --> Card
```
**Sources:**
- [apps/web/app/globals.css:3-35]() (Token definitions)
- [apps/web/app/globals.css:176-190]() (Component class mappings)

## Error Handling
The web application implements a robust error boundary at the workspace level. When a data layer interruption occurs, the system provides a "Workspace Error" screen that allows users to reset the view state without losing organizational context.

**Sources:**
- [apps/web/app/error.tsx:19-41]() (Workspace error UI implementation)

---

# Page: Workspace Shell & Module System

# Workspace Shell & Module System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/web/app/api/workspace-context/route.test.ts](apps/web/app/api/workspace-context/route.test.ts)
- [apps/web/app/api/workspace-context/route.ts](apps/web/app/api/workspace-context/route.ts)
- [apps/web/app/api/workspaces/[workspaceId]/channels/[channelName]/events/route.test.ts](apps/web/app/api/workspaces/[workspaceId]/channels/[channelName]/events/route.test.ts)
- [apps/web/app/api/workspaces/[workspaceId]/channels/[channelName]/events/route.ts](apps/web/app/api/workspaces/[workspaceId]/channels/[channelName]/events/route.ts)
- [apps/web/app/api/workspaces/[workspaceId]/modules/[moduleId]/route.test.ts](apps/web/app/api/workspaces/[workspaceId]/modules/[moduleId]/route.test.ts)
- [apps/web/app/api/workspaces/[workspaceId]/modules/[moduleId]/route.ts](apps/web/app/api/workspaces/[workspaceId]/modules/[moduleId]/route.ts)
- [apps/web/app/api/workspaces/[workspaceId]/shell-counters/route.test.ts](apps/web/app/api/workspaces/[workspaceId]/shell-counters/route.test.ts)
- [apps/web/app/api/workspaces/[workspaceId]/shell-counters/route.ts](apps/web/app/api/workspaces/[workspaceId]/shell-counters/route.ts)

</details>



The Workspace Shell is the primary UI framework for the AgentSpace web application, hosted at the `/w/[workspaceSlug]` route. It provides a unified, multi-module interface that integrates various functional areas—such as Instant Messaging (IM), Task Management, and Knowledge bases—into a single-page experience. The system relies on a lazy-loading module architecture, a centralized shell counter service, and a real-time event bus.

## Architectural Overview

The shell is composed of a persistent **Sidebar** and a dynamic **Module Frame**. Instead of full page reloads, the shell intercepts navigation to swap the active module, fetching data through dedicated API routes.

### Component Relationship Diagram

This diagram shows how the UI components in `apps/web` interact with the server-side loaders and data providers.

```mermaid
graph TD
    subgraph "Client (Browser)"
        WS["WorkspaceShell Component"]
        SB["Sidebar Component"]
        MF["ModuleFrame"]
        MC["ModuleCache"]
    end

    subgraph "Server API Routes"
        SCR["/api/workspaces/[id]/shell-counters"]
        SMR["/api/workspaces/[id]/modules/[moduleId]"]
        EVR["/api/workspaces/[id]/channels/[ch]/events"]
    end

    subgraph "Services Layer"
        WML["workspace-module-loaders.ts"]
        WSD["workspace-shell-data.ts"]
        WSC["workspace-shell-counters.ts"]
    end

    WS --> SB
    WS --> MF
    SB -- "fetches" --> SCR
    MF -- "lazy loads" --> MC
    MC -- "fetches data" --> SMR
    SMR -- "invokes" --> WML
    SCR -- "invokes" --> WSD
    WSD -- "transforms" --> WSC
    MF -- "SSE Subscription" --> EVR
```

**Sources:** [apps/web/app/api/workspaces/[workspaceId]/shell-counters/route.ts:1-45](), [apps/web/app/api/workspaces/[workspaceId]/modules/[moduleId]/route.ts:1-76](), [apps/web/app/api/workspaces/[workspaceId]/channels/[channelName]/events/route.ts:9-119]()

---

## Module System & Lazy Loading

AgentSpace uses a modular architecture where each feature (e.g., `im`, `tasks`, `knowledge`, `settings`) is treated as a "Workspace Module". These modules are loaded on-demand to minimize initial bundle size and server load.

### Module Resolution Flow

When a user navigates to a module, the following flow occurs:
1.  **Validation**: The shell validates the `moduleId` using `isWorkspaceModuleId` [apps/web/app/api/workspaces/[workspaceId]/modules/[moduleId]/route.ts:30-32]().
2.  **Access Control**: The system checks if the user has permission. For example, users with `channel` access scope are restricted to the `im` module [apps/web/app/api/workspaces/[workspaceId]/modules/[moduleId]/route.ts:36-38]().
3.  **Data Fetching**: The `GET` handler in the module route calls `loadWorkspaceModuleDataWithMeta` [apps/web/app/api/workspaces/[workspaceId]/modules/[moduleId]/route.ts:43-58]().
4.  **Context Injection**: The loader receives the current user's role, display name, and any URL search parameters (like `section` for settings or `focus` for IM) [apps/web/app/api/workspaces/[workspaceId]/modules/[moduleId]/route.ts:46-57]().

### Supported Modules

| Module ID | Purpose | Loader Function |
| :--- | :--- | :--- |
| `im` | Instant Messaging & Channel history | `loadWorkspaceModuleDataWithMeta` |
| `tasks` | Task board and status tracking | `loadWorkspaceModuleDataWithMeta` |
| `knowledge` | Documentation and knowledge base | `loadWorkspaceModuleDataWithMeta` |
| `settings` | Workspace and member configuration | `loadWorkspaceModuleDataWithMeta` |
| `performance` | Agent and task analytics | `loadWorkspaceModuleDataWithMeta` |

**Sources:** [apps/web/app/api/workspaces/[workspaceId]/modules/[moduleId]/route.ts:15-76](), [apps/web/app/api/workspaces/[workspaceId]/modules/[moduleId]/route.test.ts:43-156]()

---

## Shell Counters & Sidebar State

The sidebar displays real-time badges (counters) for unread messages, open tasks, and pending approvals. These are aggregated via the `/api/workspaces/[workspaceId]/shell-counters` endpoint.

### Counter Calculation Logic

The server executes `getWorkspaceShellCounterData` to retrieve raw counts from the database and then applies `deriveWorkspaceShellCounters` to format them for the UI [apps/web/app/api/workspaces/[workspaceId]/shell-counters/route.ts:26-38]().

| Counter Metric | Code Entity / Source |
| :--- | :--- |
| **Unread Notifications** | `unreadNotificationCount` |
| **Open Tasks** | `openTaskCount` |
| **Pending Approvals** | `pendingApprovalCount` |
| **Digital Employees** | `agentCount` |
| **Active Runtimes** | `runtimeCount` |

**Sources:** [apps/web/app/api/workspaces/[workspaceId]/shell-counters/route.ts:25-44](), [apps/web/app/api/workspaces/[workspaceId]/shell-counters/route.test.ts:39-56]()

---

## Real-time Event Streaming (SSE)

The workspace maintains a persistent connection to the server using Server-Sent Events (SSE) via the `/events` route. This ensures the UI updates immediately when messages are sent or tasks change.

### Event Subscription Process

1.  **Authentication**: The route verifies workspace access using `getWorkspaceAccessForIdentifier` [apps/web/app/api/workspaces/[workspaceId]/channels/[channelName]/events/route.ts:14-20]().
2.  **Authorization**: It ensures the user has specific read access to the requested channel via `canReadChannelForActorSync` [apps/web/app/api/workspaces/[workspaceId]/channels/[channelName]/events/route.ts:30-32]().
3.  **Subscription**: The server calls `subscribeWorkspaceRealtimeEvents` from the `@agent-space/services` package [apps/web/app/api/workspaces/[workspaceId]/channels/[channelName]/events/route.ts:60]().
4.  **Heartbeat**: A heartbeat is sent every 25 seconds to prevent connection timeouts [apps/web/app/api/workspaces/[workspaceId]/channels/[channelName]/events/route.ts:7-100]().

### Event Types

The shell handles several critical event types to update the module state:
-   `channel.message.created`: Triggers new message rendering in the IM module [apps/web/app/api/workspaces/[workspaceId]/channels/[channelName]/events/route.ts:69-76]().
-   `channel.thread.changed`: Updates thread metadata and unread states [apps/web/app/api/workspaces/[workspaceId]/channels/[channelName]/events/route.ts:77-83]().
-   `task.event`: Updates task progress bars and status badges [apps/web/app/api/workspaces/[workspaceId]/channels/[channelName]/events/route.ts:84-91]().

**Sources:** [apps/web/app/api/workspaces/[workspaceId]/channels/[channelName]/events/route.ts:39-109](), [apps/web/app/api/workspaces/[workspaceId]/channels/[channelName]/events/route.test.ts:58-108]()

---

## Workspace Context API

The `/api/workspace-context` route provides agents and the shell with a structured view of the workspace's entities, channels, and documents. This is used for "mention" suggestions and agent tool execution.

### Context Actions Diagram

This diagram maps the natural language "actions" to the internal service functions.

```mermaid
graph LR
    subgraph "API Action (Query Param)"
        A1["list_entities"]
        A2["resolve_entity"]
        A3["list_channels"]
        A4["search_messages"]
        A5["list_documents"]
    end

    subgraph "Internal Service (@agent-space/services)"
        S1["listWorkspaceContextEntitiesSync"]
        S2["resolveWorkspaceContextEntitySync"]
        S3["listWorkspaceContextChannelsSync"]
        S4["searchWorkspaceContextMessagesSync"]
        S5["listWorkspaceContextDocumentsSync"]
    end

    A1 --> S1
    A2 --> S2
    A3 --> S3
    A4 --> S4
    A5 --> S5
```

**Sources:** [apps/web/app/api/workspace-context/route.ts:82-117](), [apps/web/app/api/workspace-context/route.test.ts:130-141]()

### Loadtest & Performance Caching
To handle high-frequency requests during agent execution or load testing, the context route implements an in-memory cache `workspaceContextCacheGlobal` with a configurable TTL via `AGENT_SPACE_WORKSPACE_CONTEXT_CACHE_TTL_MS` [apps/web/app/api/workspace-context/route.ts:125-184]().

**Sources:** [apps/web/app/api/workspace-context/route.ts:133-176]()

---

# Page: Authentication & Google OAuth

# Authentication & Google OAuth

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/web/app/api/auth/google/callback/route.test.ts](apps/web/app/api/auth/google/callback/route.test.ts)
- [apps/web/app/api/auth/google/callback/route.ts](apps/web/app/api/auth/google/callback/route.ts)
- [apps/web/app/api/auth/google/start/route.test.ts](apps/web/app/api/auth/google/start/route.test.ts)
- [apps/web/app/api/auth/google/start/route.ts](apps/web/app/api/auth/google/start/route.ts)
- [apps/web/app/auth/error/page.tsx](apps/web/app/auth/error/page.tsx)
- [apps/web/app/auth/link/google/page.tsx](apps/web/app/auth/link/google/page.tsx)
- [apps/web/app/auth/setup/google/page.tsx](apps/web/app/auth/setup/google/page.tsx)
- [apps/web/app/channel-invite/[invitationId]/page.tsx](apps/web/app/channel-invite/[invitationId]/page.tsx)

</details>



User authentication in AgentSpace is built around **Google OAuth 2.0**. It supports standard logins, workspace invitations via tokens, and workspace joining via alphanumeric codes. The system handles session management, profile setup for new users, and account linking for existing users.

## OAuth Lifecycle & Data Flow

The authentication flow begins at the `/api/auth/google/start` route and concludes at `/api/auth/google/callback`. The system uses a `state` parameter to maintain context (nonces, invitation tokens, or join codes) across the OAuth redirect.

### Authentication Sequence

The following diagram illustrates the flow from the initial request to session creation and workspace redirection.

**Diagram: OAuth Flow to Session Creation**
```mermaid
sequenceDiagram
    participant U as User Browser
    participant W as Next.js Route (apps/web)
    participant G as Google OAuth Provider
    participant S as Server Auth Service (features/auth)
    participant DB as Database (@agent-space/db)

    U->>W: GET /api/auth/google/start?invitationToken=...
    W->>S: createGoogleAuthorizationUrl({ invitationToken })
    S-->>W: URL with state (nonce + token)
    W-->>U: 307 Redirect to Google

    U->>G: User Authenticates
    G-->>U: Redirect to /api/auth/google/callback?code=...&state=...
    U->>W: GET /api/auth/google/callback
    W->>S: verifyGoogleOAuthCallbackState(state)
    W->>S: exchangeGoogleCodeForProfile({ code, expectedNonce })
    S->>G: Token Exchange (POST)
    G-->>S: ID Token (Profile Info)
    W->>S: createSessionForGoogleLogin(profile)
    S->>DB: upsertUser / createSession
    DB-->>S: currentUser
    W->>S: acceptWorkspaceInvitationForUser({ token, userId })
    W-->>U: 307 Redirect to /w/[slug]/im
```
**Sources:** [apps/web/app/api/auth/google/start/route.ts:7-13](), [apps/web/app/api/auth/google/callback/route.ts:12-73](), [apps/web/app/api/auth/google/callback/route.test.ts:71-111]()

## Key Implementation Components

### Start Route (`/api/auth/google/start`)
This route handles the initiation of the OAuth flow. It extracts optional `invitationToken` or `joinCode` from the URL parameters and passes them to the URL builder [apps/web/app/api/auth/google/start/route.ts:7-13]().

### Callback Route (`/api/auth/google/callback`)
The callback route is the primary orchestrator of the authentication result.
1.  **Error Handling**: If Google returns an error (e.g., `access_denied`), the user is redirected to `/auth/error` [apps/web/app/api/auth/google/callback/route.ts:19-25]().
2.  **State Verification**: It verifies the `state` parameter to retrieve the original `nonce`, `invitationToken`, and `joinCode` [apps/web/app/api/auth/google/callback/route.ts:38-40]().
3.  **Profile Exchange**: It exchanges the authorization `code` for the user's Google profile (email, sub, displayName) [apps/web/app/api/auth/google/callback/route.ts:41-44]().
4.  **Session Creation**: It calls `createSessionForGoogleLogin` to establish the user's identity and session in the database [apps/web/app/api/auth/google/callback/route.ts:45-53]().
5.  **Workspace Entry**: If an invitation or join code was present, it triggers the respective logic to link the user to the workspace before redirecting them to the workspace UI [apps/web/app/api/auth/google/callback/route.ts:55-71]().

**Sources:** [apps/web/app/api/auth/google/callback/route.ts:12-99](), [apps/web/app/api/auth/google/callback/route.test.ts:159-192]()

## Invitation & Join Handling

AgentSpace provides two primary mechanisms for users to gain access to workspaces:

| Mechanism | Trigger | Logic Entity | Redirect Destination |
| :--- | :--- | :--- | :--- |
| **Invitation Token** | `invitationToken` in URL | `acceptWorkspaceInvitationForUser` | `/w/[slug]/im` |
| **Join Code** | `joinCode` in URL | `joinWorkspaceByCodeForUser` | `joined.redirectPath` |
| **Channel Invite** | `/channel-invite/[id]` | `acceptChannelInvitationAction` | `/w/[slug]/im?focus=[channel]` |

### Channel Invitations
Unlike workspace-level invitations, channel invitations are handled via a dedicated page [apps/web/app/channel-invite/[invitationId]/page.tsx:17-21](). If the user is not logged in, they are prompted to do so [apps/web/app/channel-invite/[invitationId]/page.tsx:49-62](). Once authenticated, they can perform a server action to accept the invite, which grants access specifically to that channel [apps/web/app/channel-invite/[invitationId]/page.tsx:81-89]().

**Sources:** [apps/web/app/api/auth/google/callback/route.ts:55-71](), [apps/web/app/channel-invite/[invitationId]/page.tsx:23-89]()

## Special Auth States

The system identifies scenarios where a simple login is insufficient and redirects to specialized "handoff" screens.

### Profile Setup & Account Linking
*   **`auth.google_profile_setup_required`**: Redirects to `/auth/setup/google`. This occurs when a new user needs to provide a display name or confirm details before the account is finalized [apps/web/app/api/auth/google/callback/route.ts:82-84](). The page reads from `readPendingGoogleRegistrationHandoff` [apps/web/app/auth/setup/google/page.tsx:9-13]().
*   **`auth.google_account_link_required`**: Redirects to `/auth/link/google`. This occurs when a user tries to log in with a Google account that matches an existing email but isn't yet linked [apps/web/app/api/auth/google/callback/route.ts:76-81](). It uses `readPendingGoogleLinkHandoff` to restore context [apps/web/app/auth/link/google/page.tsx:9-12]().

### Error Handling
The `/auth/error` page displays the `AuthErrorScreen` based on error codes passed in the query string (e.g., `access_denied`, `auth.google_exchange_failed`) [apps/web/app/auth/error/page.tsx:11-18]().

**Sources:** [apps/web/app/api/auth/google/callback/route.ts:74-98](), [apps/web/app/auth/setup/google/page.tsx:8-30](), [apps/web/app/auth/link/google/page.tsx:8-29]()

## Code Entity Mapping

This diagram maps the natural language authentication concepts to the specific code entities and functions within the `apps/web` package.

**Diagram: Authentication Code Entity Map**
```mermaid
graph TD
    subgraph "Routes (Code Entities)"
        R_START["GET /api/auth/google/start"]
        R_CALLBACK["GET /api/auth/google/callback"]
        R_SETUP["/auth/setup/google"]
        R_LINK["/auth/link/google"]
    end

    subgraph "Logic Functions (Code Entities)"
        F_AUTH_URL["createGoogleAuthorizationUrl"]
        F_VERIFY["verifyGoogleOAuthCallbackState"]
        F_EXCHANGE["exchangeGoogleCodeForProfile"]
        F_SESSION["createSessionForGoogleLogin"]
        F_INVITE["acceptWorkspaceInvitationForUser"]
        F_JOIN["joinWorkspaceByCodeForUser"]
    end

    subgraph "Monitoring & Data (Code Entities)"
        M_REPORT["reportGoogleAuthCallbackIssue"]
        D_HANDOFF_REG["readPendingGoogleRegistrationHandoff"]
        D_HANDOFF_LINK["readPendingGoogleLinkHandoff"]
    end

    R_START --> F_AUTH_URL
    R_CALLBACK --> F_VERIFY
    R_CALLBACK --> F_EXCHANGE
    R_CALLBACK --> F_SESSION
    R_CALLBACK --> F_INVITE
    R_CALLBACK --> F_JOIN
    R_CALLBACK -- "Error/Phase" --> M_REPORT
    
    R_SETUP --> D_HANDOFF_REG
    R_LINK --> D_HANDOFF_LINK
```
**Sources:** [apps/web/app/api/auth/google/start/route.ts:2-11](), [apps/web/app/api/auth/google/callback/route.ts:2-7](), [apps/web/app/auth/setup/google/page.tsx:3-9](), [apps/web/app/auth/link/google/page.tsx:3-9]()

---

# Page: Workspace Feature Modules

# Workspace Feature Modules

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/cli/src/commands/channel.ts](apps/cli/src/commands/channel.ts)
- [apps/cli/src/commands/employee.ts](apps/cli/src/commands/employee.ts)
- [apps/cli/src/commands/im.ts](apps/cli/src/commands/im.ts)
- [apps/cli/src/commands/material.ts](apps/cli/src/commands/material.ts)
- [apps/cli/src/commands/message.ts](apps/cli/src/commands/message.ts)
- [apps/cli/src/commands/skill.ts](apps/cli/src/commands/skill.ts)
- [apps/cli/src/commands/task.ts](apps/cli/src/commands/task.ts)
- [apps/cli/src/lib/channel-documents.test.ts](apps/cli/src/lib/channel-documents.test.ts)
- [apps/cli/src/lib/channel-documents.ts](apps/cli/src/lib/channel-documents.ts)

</details>



Workspace feature modules constitute the core UI and business logic layers of the AgentSpace web application. These modules provide the interface for managing digital employees, coordinating tasks via channels, governing approvals, and managing shared knowledge.

## Module Architecture and Data Flow

The workspace UI is organized into discrete modules, each backed by a set of server actions and repository functions. Data typically flows from the UI through **Server Actions** to the **Services Layer** (`@agent-space/services`), which interacts with the **Database Layer** (`@agent-space/db`).

### Entity Mapping: UI to Code

The following diagram maps high-level workspace features to their primary implementation entities in the codebase.

**Natural Language Space to Code Entity Space**
```mermaid
graph TD
    subgraph "Natural Language Space"
        A["Digital Employees"]
        B["Channels"]
        C["Task Board"]
        D["Knowledge/Materials"]
        E["Skills"]
    end

    subgraph "Code Entity Space (@agent-space/services)"
        A1["createEmployeeSync"]
        A2["bindEmployeeRuntimeSync"]
        B1["createChannelSync"]
        B2["sendChannelHumanMessageSync"]
        C1["createTaskSync"]
        C2["updateTaskStatusSync"]
        D1["addMaterialSync"]
        D2["parseMaterialSync"]
        E1["createWorkspaceSkillSync"]
        E2["upsertWorkspaceSkillFileSync"]
    end

    A --> A1
    A --> A2
    B --> B1
    B --> B2
    C --> C1
    C --> C2
    D --> D1
    D --> D2
    E --> E1
    E --> E2
```
**Sources:** [apps/cli/src/commands/employee.ts:1-7](), [apps/cli/src/commands/channel.ts:1-6](), [apps/cli/src/commands/task.ts:1-5](), [apps/cli/src/commands/material.ts:1-6](), [apps/cli/src/commands/skill.ts:2-12]()

---

## Digital Employees (Agents)

The Employees module manages the lifecycle and configuration of autonomous agents.

*   **Creation**: Agents are initialized with a name, role, traits, and an origin label [apps/cli/src/commands/employee.ts:34-72]().
*   **Runtime Binding**: Agents must be bound to a specific runtime (e.g., a specific LLM harness or environment) to execute tasks [apps/cli/src/commands/employee.ts:74-94]().
*   **State Management**: The service layer tracks active employees and their channel memberships [apps/cli/src/commands/employee.ts:16-31]().

**Sources:** [apps/cli/src/commands/employee.ts:1-123]()

---

## Channels & Messaging

Channels serve as the communication hub where humans and agents interact.

*   **Channel Operations**: Supports creation, deletion, and renaming of communication contexts [apps/cli/src/commands/channel.ts:20-72]().
*   **Message Types**: Distinguishes between `human` messages (sent by users) and `agent` messages (posted by digital employees) [apps/cli/src/commands/message.ts:15-42]().
*   **Channel Documents**: Agents can produce or update documents within a channel context. These operations are processed via `applyChannelDocumentOperations`, which synchronizes filesystem artifacts from the daemon back to the workspace database [apps/cli/src/lib/channel-documents.ts:1-8](), [apps/cli/src/lib/channel-documents.test.ts:90-104]().

**Sources:** [apps/cli/src/commands/channel.ts:1-79](), [apps/cli/src/commands/message.ts:1-49](), [apps/cli/src/lib/channel-documents.ts:1-8]()

---

## Task Board

The Task Board manages the lifecycle of discrete work units assigned to agents.

*   **Task Creation**: Tasks require a title, target channel, and an assignee (employee) [apps/cli/src/commands/task.ts:31-62]().
*   **Status Workflow**: Tasks move through states: `todo`, `in_progress`, `blocked`, and `done` [apps/cli/src/commands/task.ts:90-110]().
*   **Queue Integration**: The task board UI reflects the underlying execution queue status, showing whether a task is currently claimed by a daemon or pending [apps/cli/src/commands/task.ts:15-28]().

**Sources:** [apps/cli/src/commands/task.ts:1-121]()

---

## Knowledge & Materials

This module handles the ingestion of external data to be used by agents.

*   **Material Ingestion**: Supports adding raw sources or importing files with specific labels and status tracking [apps/cli/src/commands/material.ts:20-67]().
*   **Parsing**: Materials can be triggered for parsing to generate previews and structured data for agent consumption [apps/cli/src/commands/material.ts:69-88]().

**Sources:** [apps/cli/src/commands/material.ts:1-103]()

---

## Skills

Skills are reusable sets of files (code, prompts, or configuration) that extend agent capabilities.

*   **Skill Management**: Includes standard CRUD operations on skills and their constituent files [apps/cli/src/commands/skill.ts:21-84]().
*   **File Upsert**: Individual files within a skill can be updated or created via `upsertWorkspaceSkillFileSync` [apps/cli/src/commands/skill.ts:185-200]().
*   **Portability**: Skills can be exported as ZIP archives or imported from URLs, allowing for sharing across workspaces [apps/cli/src/commands/skill.ts:86-123](), [apps/cli/src/commands/skill.ts:129-149]().

**Sources:** [apps/cli/src/commands/skill.ts:1-163]()

---

## System Integration Diagram

The following diagram illustrates the interaction between the UI Feature Modules and the underlying Service layer.

**Feature Module Interaction Flow**
```mermaid
sequenceDiagram
    participant UI as "Web UI / CLI"
    participant Action as "Server Action / CLI Command"
    participant Svc as "@agent-space/services"
    participant DB as "@agent-space/db"

    UI->>Action: User Interaction (e.g. Create Task)
    Action->>Svc: createTaskSync(params)
    Svc->>DB: Insert Task Record
    Svc->>DB: listTasksSync()
    DB-->>Svc: Updated Task List
    Svc-->>Action: WorkspaceState
    Action-->>UI: Render Updated State
```
**Sources:** [apps/cli/src/commands/task.ts:46-61](), [apps/cli/src/commands/channel.ts:29-35](), [apps/cli/src/commands/employee.ts:54-71]()

---

# Page: Daemon API Routes (Web Server Side)

# Daemon API Routes (Web Server Side)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/web/app/api/daemon/_lib/output-bundle.test.ts](apps/web/app/api/daemon/_lib/output-bundle.test.ts)
- [apps/web/app/api/daemon/_lib/output-bundle.ts](apps/web/app/api/daemon/_lib/output-bundle.ts)
- [apps/web/app/api/daemon/client.integration.test.ts](apps/web/app/api/daemon/client.integration.test.ts)
- [apps/web/app/api/daemon/runtime-app-operations/[operationId]/complete/route.ts](apps/web/app/api/daemon/runtime-app-operations/[operationId]/complete/route.ts)
- [apps/web/app/api/daemon/runtime-app-operations/[operationId]/fail/route.ts](apps/web/app/api/daemon/runtime-app-operations/[operationId]/fail/route.ts)
- [apps/web/app/api/daemon/runtime-app-operations/[operationId]/start/route.ts](apps/web/app/api/daemon/runtime-app-operations/[operationId]/start/route.ts)
- [apps/web/app/api/daemon/runtimes/[runtimeId]/apps/operations/claim/route.ts](apps/web/app/api/daemon/runtimes/[runtimeId]/apps/operations/claim/route.ts)
- [apps/web/app/api/daemon/runtimes/[runtimeId]/tasks/claim/route.ts](apps/web/app/api/daemon/runtimes/[runtimeId]/tasks/claim/route.ts)
- [apps/web/app/api/daemon/tasks/[taskId]/complete/route.ts](apps/web/app/api/daemon/tasks/[taskId]/complete/route.ts)
- [apps/web/app/api/daemon/tasks/[taskId]/fail/route.ts](apps/web/app/api/daemon/tasks/[taskId]/fail/route.ts)
- [apps/web/app/api/daemon/tasks/[taskId]/input-bundle/route.ts](apps/web/app/api/daemon/tasks/[taskId]/input-bundle/route.ts)
- [apps/web/app/api/daemon/tasks/[taskId]/messages/route.ts](apps/web/app/api/daemon/tasks/[taskId]/messages/route.ts)
- [apps/web/app/api/daemon/tasks/[taskId]/output-bundle/route.ts](apps/web/app/api/daemon/tasks/[taskId]/output-bundle/route.ts)
- [apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/[approvalId]/route.ts](apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/[approvalId]/route.ts)
- [apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/route.ts](apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/route.ts)
- [apps/web/app/api/daemon/tasks/[taskId]/start/route.ts](apps/web/app/api/daemon/tasks/[taskId]/start/route.ts)

</details>



The server-side Daemon API routes in `apps/web` provide the communication interface for remote daemons to synchronize task state, download execution contexts, report progress, and manage runtime assets. These routes act as the bridge between the persistent database and the ephemeral execution environments managed by the daemon.

## Overview of API Surface

The API is structured around the lifecycle of a task execution. The daemon typically follows a polling-and-report pattern:
1. **Claiming**: Polling for new tasks assigned to its runtimes.
2. **Context Retrieval**: Downloading the `DaemonTaskInputBundle`.
3. **Execution Reporting**: Sending "thinking" logs, tool calls, and status updates.
4. **Completion/Failure**: Uploading results and artifacts via `DaemonTaskOutputBundle`.

### Authentication
All daemon routes utilize the `requireDaemonAuth` middleware [apps/web/app/api/daemon/_lib/auth.ts]() (referenced in [apps/web/app/api/daemon/runtimes/[runtimeId]/tasks/claim/route.ts:11-15]()). This ensures that the daemon token is valid and scoped to the correct workspace.

## Task Lifecycle Routes

The following diagram illustrates the flow of a task from the server's perspective as it interacts with the daemon.

### Task Execution Sequence
The sequence starts with `claim` and ends with either `complete` or `fail`.

```mermaid
sequenceDiagram
    participant D as Remote Daemon
    participant S as Next.js API (Web Server)
    participant DB as SQLite (packages/db)

    D->>S: POST /api/daemon/runtimes/[runtimeId]/tasks/claim
    S->>DB: claimNextQueuedTaskForRuntimeSync()
    DB-->>S: QueuedTaskRecord
    S-->>D: { task: TaskData }

    D->>S: POST /api/daemon/tasks/[taskId]/start
    S->>DB: startQueuedTaskSync()

    D->>S: GET /api/daemon/tasks/[taskId]/input-bundle
    S->>S: prepareDaemonTaskContext()
    S-->>D: DaemonTaskInputBundle (Base64 files + Prompt)

    loop Progress Reporting
        D->>S: POST /api/daemon/tasks/[taskId]/messages
        S->>DB: appendTaskMessageSync()
    end

    alt Success
        D->>S: POST /api/daemon/tasks/[taskId]/output-bundle
        S->>S: materializeOutputBundleToStaging()
        D->>S: POST /api/daemon/tasks/[taskId]/complete
        S->>S: applyChannelDocumentOperations()
        S->>DB: completeQueuedTaskSync()
    else Failure
        D->>S: POST /api/daemon/tasks/[taskId]/fail
        S->>DB: failQueuedTaskSync()
    end
```
**Sources:** [apps/web/app/api/daemon/runtimes/[runtimeId]/tasks/claim/route.ts:22-40](), [apps/web/app/api/daemon/tasks/[taskId]/input-bundle/route.ts:84-176](), [apps/web/app/api/daemon/tasks/[taskId]/complete/route.ts:44-64](), [apps/web/app/api/daemon/tasks/[taskId]/messages/route.ts:13-35]()

## Input and Output Bundles

Bundles are the primary mechanism for transferring files between the server and the daemon.

### Input Bundle Generation
The `GET /api/daemon/tasks/[taskId]/input-bundle` route uses `prepareDaemonTaskContext` to assemble a complete execution environment [apps/web/app/api/daemon/tasks/[taskId]/input-bundle/route.ts:84-94]().
- **Files**: Includes `prompt.txt`, `task.json`, and any documents linked to the channel [apps/web/app/api/daemon/tasks/[taskId]/input-bundle/route.ts:150-173]().
- **Metadata**: Contains Google Workspace tokens, runtime app definitions, and router session state [apps/web/app/api/daemon/tasks/[taskId]/input-bundle/route.ts:122-149]().

### Output Bundle Materialization
When a task completes, the daemon uploads a `DaemonTaskOutputBundle` via `POST /api/daemon/tasks/[taskId]/output-bundle`.
- **Validation**: Files must be under the `runtime-output/` prefix [apps/web/app/api/daemon/_lib/output-bundle.ts:44-46]().
- **Staging**: Files are written to a temporary staging directory on the server using `materializeOutputBundleToStaging` [apps/web/app/api/daemon/_lib/output-bundle.ts:23-66]().
- **Limits**: Max 64 files, 10MB per file, 25MB total [apps/web/app/api/daemon/_lib/output-bundle.ts:6-8]().

**Sources:** [apps/web/app/api/daemon/_lib/output-bundle.ts:1-67](), [apps/web/app/api/daemon/tasks/[taskId]/input-bundle/route.ts:116-174]()

## Runtime App Operations

Daemons manage the lifecycle of "Apps" (tools/skills) installed within their runtimes. The server issues commands (install, uninstall) that the daemon claims and executes.

| Route | Function | Description |
| :--- | :--- | :--- |
| `POST .../operations/claim` | `claimNextRuntimeAppOperationForRuntimeSync` | Daemon picks up the next install/uninstall request [apps/web/app/api/daemon/runtimes/[runtimeId]/apps/operations/claim/route.ts:23-26](). |
| `POST .../[operationId]/start` | `startRuntimeAppOperationSync` | Marks the operation as `running` [apps/web/app/api/daemon/runtime-app-operations/[operationId]/start/route.ts:22-29](). |
| `POST .../[operationId]/complete`| `completeRuntimeAppOperationSync` | Finalizes the app installation and updates metadata [apps/web/app/api/daemon/runtime-app-operations/[operationId]/complete/route.ts:25-31](). |
| `POST .../[operationId]/fail` | `failRuntimeAppOperationSync` | Records the error and stderr tail [apps/web/app/api/daemon/runtime-app-operations/[operationId]/fail/route.ts:28-35](). |

**Sources:** [apps/web/app/api/daemon/runtimes/[runtimeId]/apps/operations/claim/route.ts:8-49](), [apps/web/app/api/daemon/runtime-app-operations/[operationId]/complete/route.ts:9-52]()

## Runtime Approvals (Human-in-the-loop)

The daemon polls for approval status when an agent requests a sensitive action (e.g., spending budget or accessing restricted files).

```mermaid
graph TD
    subgraph "Natural Language Space"
        UserMsg["'I need to approve this tool call'"]
        AgentReq["'Agent requesting $5.00'"]
    end

    subgraph "Code Entity Space (apps/web/api/daemon)"
        PollRoute["GET /tasks/[taskId]/runtime-approvals"]
        UpdateRoute["POST /tasks/[taskId]/runtime-approvals/[approvalId]"]
        
        subgraph "Database Entities (packages/db)"
            ApprovalTable["runtime_approval table"]
            TaskTable["agent_task_queue table"]
        end
    end

    AgentReq --> PollRoute
    PollRoute -- "polls" --> ApprovalTable
    UpdateRoute -- "updates status" --> ApprovalTable
    ApprovalTable -- "linked to" --> TaskTable
```

- **Polling**: Daemons use `GET /api/daemon/tasks/[taskId]/runtime-approvals` to check if pending requests have been approved or rejected by a human.
- **Reporting**: Daemons can create new approval requests via `POST /api/daemon/tasks/[taskId]/runtime-approvals`.

**Sources:** [apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/route.ts](), [apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/[approvalId]/route.ts]()

## Post-Completion Processing

The `POST /api/daemon/tasks/[taskId]/complete` route is one of the most complex in the system, as it triggers side effects across multiple services:

1. **Document Sync**: Calls `applyChannelDocumentOperations` to move files from staging to permanent storage [apps/web/app/api/daemon/tasks/[taskId]/complete/route.ts:89-97]().
2. **Skill Imports**: Calls `applySkillImportOperations` if the agent generated new executable code [apps/web/app/api/daemon/tasks/[taskId]/complete/route.ts:98-101]().
3. **Google Workspace**: Synchronizes permissions for any created Google Sheets via `syncAgentCreatedGoogleSheetPermissions` [apps/web/app/api/daemon/tasks/[taskId]/complete/route.ts:111-115]().
4. **Knowledge Proposals**: Processes any new knowledge entries extracted by the agent [apps/web/app/api/daemon/tasks/[taskId]/complete/route.ts:118-124]().
5. **Message Routing**: Finalizes the conversation by calling `completeAgentChannelReplySync` or `postMessageSync` [apps/web/app/api/daemon/tasks/[taskId]/complete/route.ts:241-260]().

**Sources:** [apps/web/app/api/daemon/tasks/[taskId]/complete/route.ts:1-260]()

---

# Page: Attachments & File Storage API

# Attachments & File Storage API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [apps/web/app/api/attachments/[attachmentId]/route.test.ts](apps/web/app/api/attachments/[attachmentId]/route.test.ts)
- [apps/web/app/api/attachments/[attachmentId]/route.ts](apps/web/app/api/attachments/[attachmentId]/route.ts)

</details>



The Attachments & File Storage API manages the lifecycle of files within AgentSpace, including uploads from agents or users, secure storage, and authenticated retrieval. The system supports two primary storage backends: a local filesystem for self-hosted deployments and Cloudflare R2 for cloud-scale deployments.

## Storage Architecture & Configuration

AgentSpace determines its storage strategy based on the `AGENT_SPACE_DEPLOYMENT_MODE` environment variable [`.env.example:1-4`]().

### Storage Providers
1.  **Self-Hosted (`self_hosted`)**: Files are stored on the local disk at the path specified by `SELF_HOSTED_ATTACHMENT_LOCAL_ROOT` [`.env.example:10-11`]().
2.  **Cloud (`cloud`)**: Files are stored in Cloudflare R2 object storage. Configuration requires an S3-compatible endpoint, access keys, and bucket details [`.env.example:32-40`]().

### Global Policies
*   **Max Upload Size**: Defined by `ATTACHMENT_MAX_UPLOAD_BYTES` (default 50MB) [`.env.example:48-48`]().
*   **URL Expiration**: Signed URLs for cloud storage use `ATTACHMENT_SIGNED_URL_TTL_SECONDS` [`.env.example:47-47`]().
*   **Local Fallback**: `ATTACHMENT_ENABLE_LOCAL_FALLBACK` allows the system to look for files on disk even if a cloud provider is configured, assisting in migrations [`.env.example:53-53`]().

### Data Flow: Storage Selection
The following diagram illustrates how the system selects the storage client based on configuration.

**Storage Provider Resolution**
```mermaid
graph TD
    subgraph "Code Entity Space"
        ENV["process.env"]
        ASC["createAttachmentStorageClient()"]
        LSC["Local Filesystem"]
        R2C["Cloudflare R2 (S3 Client)"]
    end

    ENV -- "AGENT_SPACE_DEPLOYMENT_MODE" --> ASC
    ASC -- "self_hosted" --> LSC
    ASC -- "cloud" --> R2C
```
Sources: [`.env.example:1-4`](), [`apps/web/app/api/attachments/[attachmentId]/route.ts:8-8`]()

---

## The Attachments API Route

The primary interface for accessing files is the dynamic route `/api/attachments/[attachmentId]`. This route handles authorization, integrity checks, and content delivery.

### Request Handling Flow
1.  **Context Verification**: The route calls `getCurrentWorkspaceContext()` to ensure the user is authenticated and belongs to the workspace [`apps/web/app/api/attachments/[attachmentId]/route.ts:29-32`]().
2.  **Cross-Workspace Guard**: It validates that the requested `workspaceId` matches the session context to prevent IDOR (Insecure Direct Object Reference) attacks [`apps/web/app/api/attachments/[attachmentId]/route.ts:35-52`]().
3.  **Visibility Check**: Access is restricted based on channel visibility. If an attachment is linked to a specific channel, the user must have permission to view that channel [`apps/web/app/api/attachments/[attachmentId]/route.ts:54-77`]().
4.  **Metadata Retrieval**: The system fetches attachment metadata (sha256, fileName, mediaType) via `readStoredAttachmentSync` [`apps/web/app/api/attachments/[attachmentId]/route.ts:67-67`]().

### Content Delivery & Caching
The API implements aggressive caching for images and strict validation for files:
*   **Images**: Uses `private, max-age=3600, stale-while-revalidate=86400` [`apps/web/app/api/attachments/[attachmentId]/route.ts:21-21`]().
*   **Files**: Uses `private, no-cache` [`apps/web/app/api/attachments/[attachmentId]/route.ts:22-22`]().
*   **ETags**: The route generates ETags based on the file's SHA256 hash. If the `If-None-Match` header matches, it returns a `304 Not Modified` response to save bandwidth [`apps/web/app/api/attachments/[attachmentId]/route.ts:96-109`]().

**Attachment Access Sequence**
```mermaid
sequenceDiagram
    participant User as "Browser/Client"
    participant Route as "GET /api/attachments/[id]"
    participant Auth as "getCurrentWorkspaceContext()"
    participant Service as "readStoredAttachmentSync()"
    participant Storage as "readAttachmentContent()"

    User->>Route: Request attachment
    Route->>Auth: Validate Session
    Auth-->>Route: WorkspaceContext
    Route->>Service: Lookup metadata
    Service-->>Route: MessageAttachment object
    Route->>Route: Check Channel Visibility
    Route->>Storage: Fetch bytes (Local or R2)
    Storage-->>Route: Uint8Array
    Route->>User: 200 OK + Content + ETag
```
Sources: [`apps/web/app/api/attachments/[attachmentId]/route.ts:25-155`](), [`apps/web/app/api/attachments/[attachmentId]/route.test.ts:153-170`]()

---

## Technical Implementation Details

### Attachment Metadata
Attachments are represented by the `MessageAttachment` domain type. Key properties include:
| Property | Description |
| :--- | :--- |
| `id` | Unique identifier for the attachment. |
| `sha256` | Hash for integrity and ETags. |
| `storedPath` | Absolute path on disk (for local storage). |
| `storageKey` | Object key (for R2/S3 storage). |
| `mediaType` | MIME type (e.g., `image/png`, `application/pdf`). |

Sources: [`apps/web/app/api/attachments/[attachmentId]/route.ts:5-14`](), [`apps/web/app/api/attachments/[attachmentId]/route.test.ts:153-170`]()

### Content-Disposition Logic
The API dynamically calculates the `Content-Disposition` header:
*   **Inline**: Used for images to allow browser rendering [`apps/web/app/api/attachments/[attachmentId]/route.ts:93-93`]().
*   **Attachment**: Used for other files to force a download [`apps/web/app/api/attachments/[attachmentId]/route.ts:93-93`]().
*   **Filename Encoding**: Handles non-ASCII characters by providing an ASCII fallback and a UTF-8 encoded `filename*` parameter [`apps/web/app/api/attachments/[attachmentId]/route.ts:177-189`]().

### Audit Logging
Security events, such as denied cross-workspace access or missing storage objects, are recorded in the workspace audit log using `tryRecordWorkspaceAuditEventSync` [`apps/web/app/api/attachments/[attachmentId]/route.ts:37-50`](), [`apps/web/app/api/attachments/[attachmentId]/route.ts:117-127`]().

### Error Handling
If a file is missing from the underlying storage (e.g., deleted manually from disk or R2), the API catches the error, logs an audit event, and returns a `404 Not Found` [`apps/web/app/api/attachments/[attachmentId]/route.ts:114-129`]().

Sources: [`apps/web/app/api/attachments/[attachmentId]/route.ts:1-190`](), [`.env.example:1-82`]()

---

# Page: CLI Application (apps/cli)

# CLI Application (apps/cli)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/cli/bin/agent-space.js](apps/cli/bin/agent-space.js)
- [apps/cli/package.json](apps/cli/package.json)
- [apps/cli/src/index.ts](apps/cli/src/index.ts)
- [apps/cli/src/lib/args.ts](apps/cli/src/lib/args.ts)
- [apps/cli/src/lib/format.ts](apps/cli/src/lib/format.ts)
- [apps/cli/src/lib/help.ts](apps/cli/src/lib/help.ts)

</details>



The `apps/cli` package provides the `agent-space` command-line tool, a unified interface for managing AgentSpace workspaces, interacting with the daemon, and performing administrative tasks. It serves as both a local control plane for developers and a runtime utility for agents to communicate back to the system.

## Entrypoint & Bootstrap

The CLI is designed to run in a Node.js environment and leverages modern TypeScript features via the `--experimental-strip-types` flag.

### Bootstrap Process
1.  **Binary Wrapper**: The `agent-space` command is defined in `package.json` [apps/cli/package.json:7-9]() and points to a small JavaScript shim `bin/agent-space.js` [apps/cli/bin/agent-space.js:1-13]().
2.  **Type Stripping**: The shim uses `node:child_process.spawnSync` to execute the TypeScript entrypoint `src/index.ts` using the experimental type-stripping flag [apps/cli/bin/agent-space.js:9-11]().
3.  **Main Dispatch**: The `main()` function in `src/index.ts` handles initial argument normalization, such as stripping `pnpm` separators [apps/cli/src/index.ts:21-26](), and then dispatches the request to specific command handlers based on the first positional argument [apps/cli/src/index.ts:38-96]().

**CLI Entrypoint Flow**
```mermaid
graph TD
  A["Terminal: agent-space"] --> B["bin/agent-space.js (Shim)"]
  B --> C["node --experimental-strip-types src/index.ts"]
  C --> D["main() in src/index.ts"]
  D --> E{"Command Match?"}
  E -- "db" --> F["runDatabaseCommand()"]
  E -- "daemon" --> G["runDaemonCommand()"]
  E -- "workspace" --> H["runWorkspaceCommand()"]
  E -- "..." --> I["Other Handlers"]
```
Sources: [apps/cli/bin/agent-space.js:1-13](), [apps/cli/src/index.ts:20-100]().

## Command Structure

The CLI follows a `<command> <subcommand> [options]` pattern. It supports global flags for output formatting, specifically `--json` for machine-readable output [apps/cli/src/lib/format.ts:12-15]().

### Available Command Modules
The CLI delegates logic to specialized command files located in `src/commands/`.

| Command | Handler Function | Purpose |
| :--- | :--- | :--- |
| `workspace` | `runWorkspaceCommand` | Manage workspace initialization and context [apps/cli/src/index.ts:58-60](). |
| `daemon` | `runDaemonCommand` | Control the local daemon and manage remote tokens [apps/cli/src/index.ts:46-48](). |
| `db` | `runDatabaseCommand` | Database status, storage scanning, and purging [apps/cli/src/index.ts:42-44](). |
| `employee` | `runEmployeeCommand` | Manage digital employees and their runtime bindings [apps/cli/src/index.ts:70-72](). |
| `task` | `runTaskCommand` | Create, list, and move tasks on the board [apps/cli/src/index.ts:82-84](). |
| `skill` | `runSkillCommand` | Import, export, and list agent skills [apps/cli/src/index.ts:86-88](). |
| `output` | `runOutputCommand` | Register agent execution results (Sheets, Docs, Files) [apps/cli/src/index.ts:90-92](). |

For a complete list of arguments and flags for every command, see **[CLI Commands Reference](#5.1)**.

Sources: [apps/cli/src/index.ts:3-16](), [apps/cli/src/lib/help.ts:7-50]().

## Library Utilities

The CLI relies on a set of internal utilities in `src/lib/` to handle argument parsing, output formatting, and communication.

### Argument Parsing & Formatting
*   **`parseArgs`**: A custom parser that separates positional arguments from flags (e.g., `--key value` or `--flag`) [apps/cli/src/lib/args.ts:6-31]().
*   **`writeData`**: A central utility that inspects the requested `OutputFormat` (`text` or `json`). For text output, it automatically renders arrays as tables with calculated column widths [apps/cli/src/lib/format.ts:30-47]().
*   **`renderTable`**: Dynamically generates ASCII tables for CLI readability [apps/cli/src/lib/format.ts:55-73]().

### Logic-to-Code Mapping
The following diagram maps CLI concepts to their underlying library implementations.

**CLI Utility Mapping**
```mermaid
graph LR
  subgraph "CLI Logic Space"
    direction TB
    Parser["Argument Parsing"]
    Formatter["Output Formatting"]
    HelpSys["Help System"]
  end

  subgraph "Code Entity Space (@agent-space/cli)"
    direction TB
    Parser --- L1["src/lib/args.ts: parseArgs()"]
    Formatter --- L2["src/lib/format.ts: writeData()"]
    Formatter --- L3["src/lib/format.ts: renderTable()"]
    HelpSys --- L4["src/lib/help.ts: printRootHelp()"]
  end
```
Sources: [apps/cli/src/lib/args.ts:6-31](), [apps/cli/src/lib/format.ts:30-73](), [apps/cli/src/lib/help.ts:1-51]().

For technical details on daemon communication and runtime output helpers, see **[CLI Library Utilities](#5.2)**.

## Related Pages
*   **[CLI Commands Reference](#5.1)**: Detailed documentation of every command and flag.
*   **[CLI Library Utilities](#5.2)**: Deep dive into the internal helper modules used by the CLI.
*   **[Daemon & Agent Execution](#3)**: How the `daemon` command interacts with the background agent process.

---

# Page: CLI Commands Reference

# CLI Commands Reference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/cli/src/commands/channel.ts](apps/cli/src/commands/channel.ts)
- [apps/cli/src/commands/cost.ts](apps/cli/src/commands/cost.ts)
- [apps/cli/src/commands/daemon.ts](apps/cli/src/commands/daemon.ts)
- [apps/cli/src/commands/db.ts](apps/cli/src/commands/db.ts)
- [apps/cli/src/commands/dev.ts](apps/cli/src/commands/dev.ts)
- [apps/cli/src/commands/doctor.ts](apps/cli/src/commands/doctor.ts)
- [apps/cli/src/commands/employee.ts](apps/cli/src/commands/employee.ts)
- [apps/cli/src/commands/im.ts](apps/cli/src/commands/im.ts)
- [apps/cli/src/commands/material.ts](apps/cli/src/commands/material.ts)
- [apps/cli/src/commands/message.ts](apps/cli/src/commands/message.ts)
- [apps/cli/src/commands/output.ts](apps/cli/src/commands/output.ts)
- [apps/cli/src/commands/skill.ts](apps/cli/src/commands/skill.ts)
- [apps/cli/src/commands/task.ts](apps/cli/src/commands/task.ts)
- [apps/cli/src/commands/workspace.ts](apps/cli/src/commands/workspace.ts)

</details>



The `agent-space` CLI is the primary terminal interface for managing workspaces, agents (employees), tasks, and the execution daemon. It acts as a bridge between the local environment and the core services layer, providing tools for both administrative operations and agent-driven task execution.

## Overview and Implementation

The CLI is built as a modular command dispatcher located in `apps/cli/src/commands/`. Each command file exports a runner function that typically follows this pattern:
1. **Argument Parsing**: Uses `parseArgs` and `getStringFlag` from `../lib/args.ts` [apps/cli/src/commands/channel.ts:7-7]().
2. **Service Invocation**: Calls synchronous business logic from `@agent-space/services` or `@agent-space/db`.
3. **Formatted Output**: Uses `writeData` to output either human-readable text or structured JSON via the `--json` flag [apps/cli/src/commands/channel.ts:8-8]().

### Command Execution Data Flow

The following diagram illustrates how a CLI command (e.g., `channel create`) flows through the system:

**CLI to Service Mapping**
```mermaid
graph TD
    User["User Terminal"] -- "agent-space channel create --name 'General'" --> Entry["CLI Entrypoint"]
    Entry --> CmdRunner["runChannelCommand (channel.ts)"]
    
    subgraph "apps/cli/src/commands"
        CmdRunner -- "parseArgs(args)" --> ArgsLib["args.ts"]
        CmdRunner -- "writeData(format, result)" --> FormatLib["format.ts"]
    end

    subgraph "packages/services"
        CmdRunner -- "createChannelSync({ name })" --> ChannelService["channel-service.ts"]
    end

    subgraph "packages/db"
        ChannelService -- "writeWorkspaceStateSync(state)" --> DB["PostgreSQL / SQLite"]
    end
```
Sources: [apps/cli/src/commands/channel.ts:1-36](), [apps/cli/src/commands/message.ts:1-42]()

---

## Workspace & Environment Commands

### workspace
Manages the lifecycle of workspaces.
*   **list**: Displays all available workspaces.
*   **create --name \<name\>**: Initializes a new workspace.
*   **status**: Shows the current active workspace configuration.
*   **Sources**: [apps/cli/src/commands/workspace.ts]()

### db
Low-level database and storage maintenance.
*   **status**: Returns PostgreSQL connection health and migration status [apps/cli/src/commands/db.ts:11-14]().
*   **storage-scan**: Scans the filesystem for orphaned or missing attachments [apps/cli/src/commands/db.ts:16-19]().
*   **workspace-purge --id \<id\> --force**: Completely deletes all data and files associated with a workspace [apps/cli/src/commands/db.ts:21-42]().
*   **Sources**: [apps/cli/src/commands/db.ts:1-48]()

### doctor
A diagnostic tool to verify the environment and repository structure.
*   Checks for the existence of core directories (`apps/web`, `packages/domain`, etc.) [apps/cli/src/commands/doctor.ts:35-39]().
*   Verifies database connectivity and workspace snapshot read/write access [apps/cli/src/commands/doctor.ts:10-31]().
*   **Sources**: [apps/cli/src/commands/doctor.ts:1-64]()

---

## Daemon & Execution Commands

### daemon
The `daemon` command controls the background process responsible for polling and executing agent tasks.

| Subcommand | Flags | Description |
| :--- | :--- | :--- |
| `start` | `--foreground`, `--daemon-id`, `--device-name` | Starts the daemon process. Use `--foreground` for debugging [apps/cli/src/commands/daemon.ts:147-154](). |
| `stop` | N/A | Gracefully shuts down the running daemon using the PID file [apps/cli/src/commands/daemon.ts:119-121](). |
| `status` | `--json` | Shows if the daemon is alive, its PID, and heartbeat status [apps/cli/src/commands/daemon.ts:123-125](). |
| `logs` | `--lines <n>`, `--follow` | Tails the daemon log file [apps/cli/src/commands/daemon.ts:127-129](). |
| `token` | `create`, `list`, `revoke` | Manages API tokens for remote daemon authentication [apps/cli/src/commands/daemon.ts:131-133](). |

**Daemon Task Execution Logic**
```mermaid
sequenceDiagram
    participant CLI as "agent-space daemon start"
    participant DB as "@agent-space/db"
    participant DaemonPkg as "agent-space-daemon"
    participant Sandbox as "@agent-space/sandbox"

    CLI->>DB: claimNextQueuedTaskForRuntimeSync()
    DB-->>CLI: QueuedTaskRecord
    CLI->>DaemonPkg: runProviderTask(taskBundle)
    DaemonPkg->>Sandbox: exec(command)
    Sandbox-->>DaemonPkg: Stdout/Stderr
    DaemonPkg-->>CLI: TaskOutputBundle
    CLI->>DB: completeQueuedTaskSync(output)
```
Sources: [apps/cli/src/commands/daemon.ts:32-61](), [apps/cli/src/commands/daemon.ts:110-220]()

---

## Agent & Communication Commands

### employee
Manages "Digital Employees" (Agents) within the workspace.
*   **list**: Lists agents and their current runtime bindings [apps/cli/src/commands/employee.ts:16-32]().
*   **create --name \<n\> --role \<r\>**: Defines a new agent with specific traits [apps/cli/src/commands/employee.ts:34-72]().
*   **bind-runtime --name \<n\> --runtime-id \<id\>**: Associates an agent with a specific execution environment (e.g., Claude Code, Hermes) [apps/cli/src/commands/employee.ts:74-94]().
*   **Sources**: [apps/cli/src/commands/employee.ts:1-123]()

### channel
Manages communication channels where agents and humans interact.
*   **list**: Shows all channels [apps/cli/src/commands/channel.ts:15-18]().
*   **create --name \<name\>**: Creates a new channel [apps/cli/src/commands/channel.ts:20-36]().
*   **rename --name \<old\> --to \<new\>**: Updates channel identity [apps/cli/src/commands/channel.ts:55-72]().
*   **Sources**: [apps/cli/src/commands/channel.ts:1-79]()

### message
Sends or retrieves messages in a channel.
*   **post --channel \<c\> --summary \<text\>**: Posts a message. Supports `--role human` or `--role agent` [apps/cli/src/commands/message.ts:15-42]().
*   **Sources**: [apps/cli/src/commands/message.ts:1-49]()

---

## Task & Resource Commands

### task
Directly interacts with the task queue.
*   **list**: Shows pending, running, and completed tasks.
*   **create**: Manually enqueues a task for an agent.
*   **Sources**: [apps/cli/src/commands/task.ts]()

### skill
Manages reusable agent capabilities (Skills).
*   **list / get**: View skill definitions and associated files [apps/cli/src/commands/skill.ts:21-41]().
*   **create / update / delete**: Lifecycle management of skill metadata [apps/cli/src/commands/skill.ts:43-84]().
*   **export --out \<path\>**: Packages skills into a `.zip` archive for distribution [apps/cli/src/commands/skill.ts:86-123]().
*   **import --url \<url\>**: Imports skills from a remote manifest or archive [apps/cli/src/commands/skill.ts:129-149]().
*   **Sources**: [apps/cli/src/commands/skill.ts:1-163]()

### output
This command is primarily used **inside the agent's sandbox** to communicate results back to the host system. It populates the `runtime-output/` directory [apps/cli/src/commands/output.ts:33-34]().

*   **attach \<file\>**: Adds a file to the task's output bundle [apps/cli/src/commands/output.ts:95-124]().
*   **text \<msg\>**: Sets the final text response of the agent [apps/cli/src/commands/output.ts:126-141]().
*   **document upsert --title \<t\> --content \<p\>**: Creates or updates a workspace document [apps/cli/src/commands/output.ts:193-212]().
*   **validate**: Checks if the current `runtime-output` manifests are schema-compliant [apps/cli/src/commands/output.ts:143-157]().
*   **Sources**: [apps/cli/src/commands/output.ts:37-212]()

---

## Financial & Cost Commands

### cost
Tracks token usage and manages budgets.

*   **summary**: Shows total workspace cost, task count, and token breakdown [apps/cli/src/commands/cost.ts:58-86]().
*   **agent --name \<n\>**: Detailed cost report for a specific agent [apps/cli/src/commands/cost.ts:88-110]().
*   **budget set --scope \<s\> --limit \<usd\>**: Sets a budget threshold.
    *   **Scopes**: `workspace`, `agent`, `channel` [apps/cli/src/commands/cost.ts:135-147]().
    *   **Actions**: `warn`, `pause`, `approve` (requires human intervention) [apps/cli/src/commands/cost.ts:156-167]().
*   **Sources**: [apps/cli/src/commands/cost.ts:1-183]()

---

# Page: CLI Library Utilities

# CLI Library Utilities

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/cli/src/lib/channel-documents.ts](apps/cli/src/lib/channel-documents.ts)
- [apps/cli/src/lib/daemon-client.test.ts](apps/cli/src/lib/daemon-client.test.ts)
- [apps/cli/src/lib/daemon-client.ts](apps/cli/src/lib/daemon-client.ts)
- [apps/cli/src/lib/daemon-task-context.test.ts](apps/cli/src/lib/daemon-task-context.test.ts)
- [apps/cli/src/lib/daemon-task-context.ts](apps/cli/src/lib/daemon-task-context.ts)
- [apps/cli/src/lib/daemon-task-output.ts](apps/cli/src/lib/daemon-task-output.ts)
- [apps/cli/src/lib/runtime-output.ts](apps/cli/src/lib/runtime-output.ts)
- [apps/cli/src/lib/skill-imports.ts](apps/cli/src/lib/skill-imports.ts)

</details>



The CLI Library Utilities provide the underlying logic for the `apps/cli` package, facilitating communication with the daemon, preparing execution environments for agents, and processing the outputs generated by agent runtimes. These utilities largely act as a bridge between the CLI's command layer and the shared logic within the `agent-space-daemon` package.

## Daemon Communication (daemon-client)

The `HttpDaemonClient` is the primary interface for the CLI to communicate with a running AgentSpace daemon via HTTP. It handles task lifecycle operations such as claiming, starting, and completing tasks.

### Key Features
- **Retry Logic**: Implements automatic retries for transient failures (e.g., 503 Service Unavailable) using a configurable delay and maximum attempt count `[apps/cli/src/lib/daemon-client.test.ts:5-34]()`.
- **Non-Retryable Safety**: Certain operations, such as task completion with specific error codes (e.g., 500 Internal Server Error), are treated as non-retryable to prevent inconsistent state `[apps/cli/src/lib/daemon-client.test.ts:36-65]()`.

### Communication Flow
The diagram below illustrates how the `HttpDaemonClient` interacts with the daemon's HTTP endpoints.

**Daemon Client Interaction**
```mermaid
sequenceDiagram
    participant CLI as "apps/cli (Command)"
    participant Client as "HttpDaemonClient [apps/cli/src/lib/daemon-client.ts]"
    participant Daemon as "Daemon HTTP API"

    CLI->>Client: claimTask(runtimeId)
    Client->>Daemon: POST /tasks/claim
    Daemon-->>Client: 200 OK (TaskRecord | null)
    Client-->>CLI: TaskRecord

    CLI->>Client: completeTask(taskId, result)
    Client->>Daemon: POST /tasks/complete
    Note over Client, Daemon: Retries 503s, fails on 500s
    Daemon-->>Client: 200 OK
    Client-->>CLI: void
```
**Sources:** `[apps/cli/src/lib/daemon-client.ts:1-2]()`, `[apps/cli/src/lib/daemon-client.test.ts:24-30]()`.

## Task Context Preparation (daemon-task-context)

Before an agent starts execution, the CLI must prepare a "work directory" populated with the necessary context. This process is handled by `prepareDaemonTaskContext` and its associated materialization functions.

### Materialization Logic
- **Agent Skills**: `materializeAgentSkills` writes skill definitions into both a compatibility directory (`.agent_context/skills`) and a provider-native directory (e.g., `.claude/skills` for Claude Code) `[apps/cli/src/lib/daemon-task-context.test.ts:77-93]()`.
- **Knowledge Pages**: `materializeAgentKnowledgePages` exports workspace knowledge into a structured format containing a `manifest.json` and individual Markdown files `[apps/cli/src/lib/daemon-task-context.test.ts:117-139]()`.
- **Skill Resolution**: `resolveAgentSkills` ensures that an agent's assigned skills are correctly identified, prioritizing stored assignments over stale profile data and including built-in skills like `BUILTIN_WORKSPACE_CONTEXT_SKILL_NAME` `[apps/cli/src/lib/daemon-task-context.test.ts:56-75]()`.

**Context Materialization Architecture**
```mermaid
graph TD
    subgraph "Context Preparation [apps/cli/src/lib/daemon-task-context.ts]"
        PTC["prepareDaemonTaskContext()"]
        MAS["materializeAgentSkills()"]
        MAK["materializeAgentKnowledgePages()"]
        MAA["materializeAttachments()"]
    end

    subgraph "Work Directory Structure"
        WD["workDir/"]
        SK["workDir/.agent_context/skills/"]
        KN["workDir/.agent_context/knowledge/"]
        AT["workDir/.agent_context/attachments/"]
    end

    PTC --> MAS
    PTC --> MAK
    PTC --> MAA
    MAS --> SK
    MAK --> KN
    MAA --> AT
```
**Sources:** `[apps/cli/src/lib/daemon-task-context.ts:1-13]()`, `[apps/cli/src/lib/daemon-task-context.test.ts:32-35]()`.

## Runtime Output Management (runtime-output)

Agents communicate their results and side-effect requests (like skill imports or document operations) by writing files into a specific directory structure within the `workDir`.

### Output Directory Structure
The standard output directory is `runtime-output/` `[apps/cli/src/lib/runtime-output.ts:3]()`. The library provides helpers to resolve paths for various output types:

| Constant / Helper | File / Path | Purpose |
|:---|:---|:---|
| `RUNTIME_OUTPUT_MANIFEST_FILE` | `agent-output.json` | Final task status and text output `[apps/cli/src/lib/runtime-output.ts:5]()`. |
| `RUNTIME_OUTPUT_ARTIFACTS_DIR` | `artifacts/` | Files generated by the agent to be uploaded `[apps/cli/src/lib/runtime-output.ts:4]()`. |
| `RUNTIME_OUTPUT_CHANNEL_DOCUMENTS_FILE` | `channel-documents.json` | Operations on workspace channel documents `[apps/cli/src/lib/runtime-output.ts:6]()`. |
| `RUNTIME_OUTPUT_SKILL_IMPORTS_FILE` | `skill-imports.json` | Requests to import new skills into the workspace `[apps/cli/src/lib/runtime-output.ts:7]()`. |
| `RUNTIME_OUTPUT_PERMISSION_REQUESTS_FILE` | `permission-requests.json` | Requests for additional runtime permissions `[apps/cli/src/lib/runtime-output.ts:12]()`. |

**Sources:** `[apps/cli/src/lib/runtime-output.ts:3-22]()`, `[apps/cli/src/lib/runtime-output.ts:24-62]()`.

## Specialized Handlers

The CLI includes specific utilities for handling complex side effects requested by agents during their runtime.

### Channel Documents and Skills
- **Channel Documents**: `applyChannelDocumentOperations` processes the JSON manifest produced by agents to update, create, or delete documents within a workspace channel `[apps/cli/src/lib/channel-documents.ts:2-7]()`.
- **Skill Imports**: `applySkillImportOperations` and `prepareSkillImportOperationArtifacts` handle the ingestion of new skills discovered or authored by the agent during execution `[apps/cli/src/lib/skill-imports.ts:1-8]()`.

### Task Output Finalization
The `daemon-task-output` module provides utilities to clean up the environment after a task finishes:
- `loadTaskOutputEnvelope`: Reads the manifest and artifacts from the `runtime-output` directory `[apps/cli/src/lib/daemon-task-output.ts:4]()`.
- `clearTaskOutputArtifacts`: Deletes local artifacts once they have been successfully uploaded to the server `[apps/cli/src/lib/daemon-task-output.ts:2]()`.

**Sources:** `[apps/cli/src/lib/channel-documents.ts:1-7]()`, `[apps/cli/src/lib/skill-imports.ts:1-8]()`, `[apps/cli/src/lib/daemon-task-output.ts:1-5]()`.

---

# Page: Google Workspace Integration

# Google Workspace Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [apps/web/app/api/integrations/google/agent-delegation/revoke/route.test.ts](apps/web/app/api/integrations/google/agent-delegation/revoke/route.test.ts)
- [apps/web/app/api/integrations/google/agent-delegation/revoke/route.ts](apps/web/app/api/integrations/google/agent-delegation/revoke/route.ts)
- [apps/web/app/api/integrations/google/callback/route.test.ts](apps/web/app/api/integrations/google/callback/route.test.ts)
- [apps/web/app/api/integrations/google/callback/route.ts](apps/web/app/api/integrations/google/callback/route.ts)
- [apps/web/app/api/integrations/google/disconnect/route.test.ts](apps/web/app/api/integrations/google/disconnect/route.test.ts)
- [apps/web/app/api/integrations/google/disconnect/route.ts](apps/web/app/api/integrations/google/disconnect/route.ts)
- [apps/web/app/api/integrations/google/start/route.test.ts](apps/web/app/api/integrations/google/start/route.test.ts)
- [apps/web/app/api/integrations/google/start/route.ts](apps/web/app/api/integrations/google/start/route.ts)

</details>



AgentSpace provides deep integration with Google Workspace (Sheets, Docs, and Drive), allowing both users and agents to interact with Google services. This integration supports user authentication via Google OAuth and a delegation model where users can grant specific agents the authority to act on their behalf within Google Workspace.

## Integration Architecture

The integration is built on a secure OAuth 2.0 flow. It distinguishes between **User Authentication** (logging into AgentSpace) and **Workspace Integration** (granting the system access to Google files).

### OAuth Flow and Delegation
When a user integrates Google Workspace, they can either connect it to their own profile for personal use or delegate that access to a specific **Digital Employee** (Agent).

#### Data Flow: Agent Delegation
The following diagram illustrates how a user delegates their Google Workspace authority to an agent.

"Agent Delegation Flow"
```mermaid
sequenceDiagram
    participant User as "Browser (User)"
    participant Web as "Next.js Web Server (apps/web)"
    participant Google as "Google OAuth Provider"
    participant DB as "PostgreSQL (@agent-space/db)"

    User->>Web: "GET /api/integrations/google/start?agent=planner"
    Note over Web: "assertCanManageEmployeeForActorSync()"
    Web->>Web: "createGoogleWorkspaceAuthorizationUrl()"
    Web-->>User: "307 Redirect to Google"
    User->>Google: "Consent to Scopes"
    Google-->>User: "Redirect to /api/integrations/google/callback?code=..."
    User->>Web: "GET /api/integrations/google/callback"
    Web->>Web: "verifyGoogleWorkspaceOAuthCallbackState()"
    Web->>Web: "saveGoogleWorkspaceCredentialFromAuthorizationCode()"
    Web->>DB: "upsertAgentGoogleWorkspaceDelegationSync()"
    DB-->>Web: "Success"
    Web-->>User: "307 Redirect to /w/[slug]/agents?agentGoogleWorkspace=connected"
```
**Sources:** [apps/web/app/api/integrations/google/start/route.ts:10-39](), [apps/web/app/api/integrations/google/callback/route.ts:15-82]()

## Key Implementation Details

### 1. Secure Credential Storage
Credentials obtained from Google are encrypted before being stored in the database.
- **Encryption**: The system uses `AGENT_SPACE_GOOGLE_WORKSPACE_TOKEN_ENCRYPTION_KEY` to encrypt refresh tokens [ .env.example:79-79]().
- **Scoped Access**: AgentSpace typically requests `https://www.googleapis.com/auth/drive.file`, limiting the agent's access to only files created by the app or explicitly opened by it [apps/web/app/api/integrations/google/callback/route.test.ts:61-61]().

### 2. Identity Verification
During the OAuth callback, the server strictly validates that the user returning from Google is the same user who initiated the request to prevent session injection attacks.
- The `state` parameter is signed and verified via `verifyGoogleWorkspaceOAuthCallbackState` [apps/web/app/api/integrations/google/callback/route.ts:35-40]().
- The server checks if the user has an `active` membership in the target workspace via `readWorkspaceMembershipSync` [apps/web/app/api/integrations/google/callback/route.ts:42-45]().

### 3. Agent Delegation Logic
Delegation allows an agent (e.g., "Planner") to use a specific user's Google identity. This is managed through the `upsertAgentGoogleWorkspaceDelegationSync` function, which maps a `workspaceId`, `employeeName`, and `userId` to a `googleOAuthCredentialId` [apps/web/app/api/integrations/google/callback/route.ts:58-66]().

## API Endpoints

| Route | Method | Description |
| :--- | :--- | :--- |
| `/api/integrations/google/start` | `GET` | Initiates OAuth flow; accepts `agent` and `redirectAfter` params [apps/web/app/api/integrations/google/start/route.ts:10-10](). |
| `/api/integrations/google/callback` | `GET` | Handles Google redirect, exchanges code for tokens, and saves delegation [apps/web/app/api/integrations/google/callback/route.ts:15-15](). |
| `/api/integrations/google/disconnect` | `POST` | Revokes the user's personal Google Workspace connection [apps/web/app/api/integrations/google/disconnect/route.ts:8-8](). |
| `/api/integrations/google/agent-delegation/revoke` | `POST` | Removes an agent's delegated access to a user's Google account [apps/web/app/api/integrations/google/agent-delegation/revoke/route.ts:9-9](). |

## Revocation Flows

AgentSpace provides granular control over revoking access. Users can disconnect their entire Google integration or target specific agents.

### Disconnect vs. Revoke
- **Disconnect**: Calls `revokeGoogleOAuthCredentialSync` to remove the user's primary credential from the workspace [apps/web/app/api/integrations/google/disconnect/route.ts:15-18]().
- **Agent Revoke**: Calls `revokeAgentGoogleWorkspaceDelegationSync`. This only stops a specific agent from using the user's Google identity but leaves the user's credential intact for other agents or personal use [apps/web/app/api/integrations/google/agent-delegation/revoke/route.ts:28-32]().

"Credential Revocation Logic"
```mermaid
graph TD
    subgraph "Code Entity Space"
        R_UI["Revoke UI Button"]
        R_Route["POST /api/integrations/google/agent-delegation/revoke"]
        S_Guard["assertCanManageEmployeeForActorSync"]
        DB_Revoke["revokeAgentGoogleWorkspaceDelegationSync"]
    end

    subgraph "Natural Language Concepts"
        User["User Identity"]
        Agent["Digital Employee"]
        Token["OAuth Refresh Token"]
    end

    R_UI --> R_Route
    R_Route --> S_Guard
    S_Guard -- "Validates Permissions" --> DB_Revoke
    DB_Revoke -- "Deletes mapping between" --> Agent
    DB_Revoke -- "and" --> Token
```
**Sources:** [apps/web/app/api/integrations/google/agent-delegation/revoke/route.ts:21-32](), [apps/web/app/api/integrations/google/disconnect/route.ts:15-18]()

## Configuration
To enable these features, the following environment variables must be configured in the web server environment:

- `AGENT_SPACE_GOOGLE_WORKSPACE_CLIENT_ID`: Google Cloud Console client ID [ .env.example:74-74]().
- `AGENT_SPACE_GOOGLE_WORKSPACE_CLIENT_SECRET`: Google Cloud Console client secret [ .env.example:75-75]().
- `AGENT_SPACE_GOOGLE_WORKSPACE_CALLBACK_URL`: Must match the URI registered in Google Console [ .env.example:76-76]().
- `AGENT_SPACE_GOOGLE_WORKSPACE_TOKEN_ENCRYPTION_KEY`: 32-byte base64 key for encrypting tokens at rest [ .env.example:79-79]().

**Sources:** [ .env.example:72-82]()

---

# Page: Permissions, Approvals & Governance

# Permissions, Approvals & Governance

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/cli/src/commands/channel.ts](apps/cli/src/commands/channel.ts)
- [apps/cli/src/commands/employee.ts](apps/cli/src/commands/employee.ts)
- [apps/cli/src/commands/workspace.ts](apps/cli/src/commands/workspace.ts)
- [apps/web/app/api/search/route.test.ts](apps/web/app/api/search/route.test.ts)
- [apps/web/app/api/search/route.ts](apps/web/app/api/search/route.ts)

</details>



The AgentSpace permission control plane manages the complex trust boundaries between human users, digital employees (agents), and workspace resources. It ensures that while agents can operate autonomously, they remain within the governance limits defined by workspace administrators and resource owners.

## Governance Overview

Governance in AgentSpace is enforced through a combination of static role-based access control (RBAC) and dynamic runtime grants. This dual-layer approach allows for broad organizational policies (e.g., "Only Admins can delete channels") while supporting granular, just-in-time permissions for agents (e.g., "Agent X is allowed to read Document Y for the duration of Task Z").

### Core Governance Entities

| Entity | Code Representation | Responsibility |
| :--- | :--- | :--- |
| **Workspace Role** | `WorkspaceRole` | Defines high-level capabilities (Admin, Member) [apps/web/app/api/search/route.ts:2-2](). |
| **Channel Visibility** | `WorkspaceChannelVisibility` | Controls which users and agents can see or post in specific channels [apps/web/app/api/search/route.ts:13-15](). |
| **Document Access** | `ChannelDocumentAccess` | Manages ownership and viewing rights for specific files/docs [apps/web/app/api/search/route.test.ts:149-152](). |
| **Runtime Bindings** | `EmployeeRuntimeBinding` | Maps an agent (employee) to a specific execution runtime [apps/cli/src/commands/employee.ts:17-19](). |

## Permission Control Flow

The following diagram illustrates how the system validates access when a user or agent attempts to interact with a resource, such as searching for documents.

### Access Validation Logic
```mermaid
graph TD
    subgraph "Natural Language Space"
        User["User Request"]
        Agent["Agent Action"]
    end

    subgraph "Code Entity Space"
        GWCS["getCurrentWorkspaceContext()"]
        GCVS["getWorkspaceChannelVisibilitySync()"]
        CVDS["canViewChannelDocumentSync()"]
        TRAE["tryRecordWorkspaceAuditEventSync()"]
    end

    User --> GWCS
    Agent --> GWCS
    GWCS --> GCVS
    GCVS -- "Validate Channel Access" --> CVDS
    CVDS -- "Deny" --> TRAE
    CVDS -- "Allow" --> Result["Return Resource"]
```
Sources: [apps/web/app/api/search/route.ts:18-45](), [apps/web/app/api/search/route.ts:89-132]()

## Runtime Access & Grants

Permissions for digital employees are often tied to their runtime environment. Agents do not have blanket access to all workspace data; instead, they are granted access based on their current task context.

- **Employee Bindings**: Administrators use `bindEmployeeRuntimeSync` to associate an agent with a specific runtime environment [apps/cli/src/commands/employee.ts:74-94]().
- **Context Guards**: When an agent executes a command via the CLI, the system checks `AGENT_SPACE_CONTEXT_AGENT_NAME` to ensure the agent is operating within its authorized scope [apps/cli/src/commands/workspace.ts:15-17]().
- **Audit Logging**: Unauthorized attempts to access resources across workspace boundaries are caught and logged via `tryRecordWorkspaceAuditEventSync` with specific error codes like `workspace.cross_workspace_access_denied` [apps/web/app/api/search/route.ts:31-43]().

For details on how runtime permissions are enforced, see [Runtime Access & Grants](#7.1).

## Approval Queue & Human-in-the-Loop

The Approval Queue serves as the primary mechanism for "Human-in-the-Loop" governance. When an agent encounters a high-stakes action—such as calling a restricted tool, accessing a sensitive document, or exceeding a budget—it generates an `ApprovalRequest`.

### Approval Workflow Architecture
```mermaid
sequenceDiagram
    participant D as Daemon (Agent Runtime)
    participant S as Web Server (@agent-space/services)
    participant H as Human User (Web UI)

    D->>S: Request Approval (Tool/Doc/Budget)
    S->>S: Create ApprovalRequest Record
    H->>S: Poll/View Approvals UI
    H->>S: approve() or reject()
    D->>S: Poll Runtime Approval Status
    S-->>D: Return Decision
```
Sources: [apps/cli/src/commands/workspace.ts:90-126](), [apps/web/app/api/search/route.ts:107-113]()

- **Task Context**: Agents can search messages and resolve entities only within their assigned task runtime [apps/cli/src/commands/workspace.ts:81-88]().
- **Visibility Filtering**: Results from global searches are strictly filtered by `filterSearchResultsByChannelVisibility` to ensure agents only see what they are permitted to see [apps/web/app/api/search/route.ts:107-113]().

For details on the approval lifecycle and UI, see [Approval Queue & Human Checkpoints](#7.2).

## Workspace & Channel Governance

Workspace state is initialized and managed through structured commands that define the initial ownership and organizational structure.

- **Initialization**: `initializeOrganizationSync` sets the owner and their role during workspace setup [apps/cli/src/commands/workspace.ts:47-54]().
- **Channel Management**: Access to channels can be managed dynamically. Functions like `createChannelSync` and `deleteChannelSync` allow administrators to modify the collaboration landscape [apps/cli/src/commands/channel.ts:20-53]().
- **Document Permissions**: Each document version tracks who created it and what their role was (human vs agent) to maintain a clear audit trail [apps/web/app/api/search/route.test.ts:127-148]().

Sources: [apps/cli/src/commands/workspace.ts:1-10](), [apps/cli/src/commands/channel.ts:1-6](), [apps/web/app/api/search/route.test.ts:149-168]()

---

# Page: Runtime Access & Grants

# Runtime Access & Grants

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [apps/cli/src/commands/employee.ts](apps/cli/src/commands/employee.ts)
- [apps/cli/src/commands/skill.ts](apps/cli/src/commands/skill.ts)
- [apps/cli/src/commands/workspace.ts](apps/cli/src/commands/workspace.ts)

</details>



The Runtime Access & Grants system in AgentSpace manages the permissions required for users and agents to interact with execution environments (Runtimes). This control plane ensures that only authorized entities can trigger code execution, access sensitive environment variables, or perform operations within a specific runtime sandbox.

## Core Authorization Logic

Authorization is enforced through a set of guard functions prefixed with `assertCanUse*`. These functions validate the relationship between a subject (User or Agent) and a Runtime within the context of a Workspace.

### Permission Guards

The system utilizes specialized functions to verify access before performing runtime-sensitive operations:

| Function | Purpose |
| :--- | :--- |
| `assertCanUseRuntime` | Generic check to ensure a user or agent has permission to interact with a specific runtime. |
| `assertCanManageRuntime` | Elevated check (typically for Workspace Admins) to modify runtime configurations or grants. |
| `assertCanUseRuntimeSync` | Synchronous version of the runtime usage check used in CLI and internal service calls. |

The authorization flow typically checks if:
1. The subject is a Workspace Admin (who has implicit access to all runtimes in the workspace).
2. An explicit grant exists in the `runtime_grants` table for the specific subject and runtime.
3. For agents, whether they are "bound" to a specific runtime via employee configuration.

Sources: `[packages/services/src/runtime-access.ts:1-50]()`, `[packages/db/src/repositories/runtime.ts:10-40]()`

## Grant Management Lifecycle

Permissions are managed through explicit grant and revoke operations. These operations are handled by the Services layer and persisted in the database.

### Granting Access
The `grantRuntimeUseToUser` function creates a permission record. If the user is already an admin, the system may skip record creation as access is already inherited.

### Revoking Access
The `revokeRuntimeUseFromUser` function removes the permission record. Note that revoking a grant from a Workspace Admin does not prevent their access, as admin status overrides individual grant records.

### Implementation Flow
"Code Entity Space" mapping of the grant lifecycle:

```mermaid
graph TD
  subgraph "Web/CLI Layer"
    A["Server Action / CLI Command"]
  end

  subgraph "Services Layer (@agent-space/services)"
    B["grantRuntimeUseToUser()"]
    C["revokeRuntimeUseFromUser()"]
    D["assertCanUseRuntime()"]
  end

  subgraph "Database Layer (@agent-space/db)"
    E[("runtime_grants table")]
    F["db.run() / db.get()"]
  end

  A --> B
  A --> C
  B --> F
  C --> F
  F --> E
  D --> E
```

Sources: `[packages/services/src/runtime-access.ts:60-120]()`, `[packages/db/src/repositories/runtime.ts:85-110]()`

## Agent-Runtime Binding

Agents (Digital Employees) require specific runtime assignments to execute tasks. This is distinct from user grants and is managed via the `employee` command or the Agents UI module.

### Binding Functions
*   **`bindEmployeeRuntimeSync`**: Associates an employee with a specific runtime ID. This ensures that any task assigned to this agent is dispatched to the correct execution environment. `[apps/cli/src/commands/employee.ts:74-94]()`
*   **`unbindEmployeeRuntimeSync`**: Removes the association, effectively preventing the agent from executing tasks until a new runtime is assigned. `[apps/cli/src/commands/employee.ts:96-112]()`

### Agent Execution Context
When a daemon picks up a task, it verifies the agent's runtime binding to ensure the execution environment matches the authorized configuration.

```mermaid
sequenceDiagram
    participant CLI as "apps/cli"
    participant SVC as "@agent-space/services"
    participant DB as "@agent-space/db"

    CLI->>SVC: bindEmployeeRuntimeSync(agentName, runtimeId)
    SVC->>DB: update employee_runtime_bindings
    DB-->>SVC: Success
    SVC-->>CLI: Updated State
    
    Note over CLI, DB: Later during Task Execution
    
    SVC->>DB: listEmployeeRuntimeBindingsForWorkspaceSync()
    DB-->>SVC: Binding Record
    SVC->>SVC: assertCanUseRuntimeSync()
```

Sources: `[apps/cli/src/commands/employee.ts:1-32]()`, `[packages/services/src/runtime-access.ts:130-150]()`

## Workspace Admin Checks

Workspace Administrators possess elevated privileges that bypass standard grant checks. The system identifies admins through the `workspace_members` table where the role is set to `ADMIN`.

### Admin Privileges in Runtimes:
1.  **Implicit Use**: Admins can use any runtime registered in the workspace without an explicit entry in `runtime_grants`.
2.  **Management**: Only admins can call `upsertRuntime`, `deleteRuntime`, or manage grants for other users.
3.  **Visibility**: Admins can view all runtime logs and active sessions across the workspace.

Sources: `[packages/services/src/runtime-access.ts:20-45]()`, `[packages/db/src/repositories/workspace.ts:40-65]()`

## CLI Integration

The CLI provides direct commands to manage these permissions, primarily through the `employee` and `workspace` command modules.

| Command | Service Function | Description |
| :--- | :--- | :--- |
| `agent-space employee bind-runtime` | `bindEmployeeRuntimeSync` | Links an agent to a runtime. |
| `agent-space employee unbind-runtime` | `unbindEmployeeRuntimeSync` | Unlinks an agent from a runtime. |
| `agent-space workspace context` | `listWorkspaceContextEntitiesSync` | Accesses runtime context if authorized. |

Sources: `[apps/cli/src/commands/employee.ts:74-112]()`, `[apps/cli/src/commands/workspace.ts:23-30]()`

---

# Page: Approval Queue & Human Checkpoints

# Approval Queue & Human Checkpoints

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [apps/web/app/api/daemon/_lib/output-bundle.ts](apps/web/app/api/daemon/_lib/output-bundle.ts)
- [apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/[approvalId]/route.ts](apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/[approvalId]/route.ts)
- [apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/route.ts](apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/route.ts)

</details>



The Approval Queue is AgentSpace's primary mechanism for enforcing human-in-the-loop governance over autonomous agents. It provides a structured workflow for agents to request permission for sensitive operations—such as executing tool calls, accessing restricted documents, or exceeding budget limits—and for humans to review, approve, or reject these requests with feedback.

## Approval Workflow Overview

The approval lifecycle bridges the gap between the asynchronous execution of an agent (managed by the `daemon`) and the synchronous oversight of a human user (via the `web` interface).

1.  **Request Creation**: An agent or system service triggers an approval request.
2.  **Queueing**: The request is persisted in the database and surfaced in the "Approvals" module.
3.  **Polling/Notification**: The `daemon` (during task execution) polls the server to check the status of a pending request.
4.  **Human Review**: A workspace member reviews the request details, optionally providing a `reviewerComment`.
5.  **Resolution**: The status transitions from `pending` to `approved` or `rejected`, which the `daemon` detects to resume or abort the tool execution.

### Data Flow: Runtime Tool Approvals

The following diagram illustrates how a tool call requiring approval moves from the agent runtime through the system layers.

**Diagram: Tool Approval Request Path**
```mermaid
sequenceDiagram
    participant D as Daemon (AgentRouter)
    participant API as Web API (/api/daemon)
    participant S as Services (@agent-space/services)
    participant DB as Database (@agent-space/db)
    participant UI as Web UI (Approvals Module)

    D->>API: POST /tasks/[taskId]/runtime-approvals
    Note right of D: toolName, contentPreview, toolInput
    API->>S: createRuntimeToolApprovalRequestSync()
    S->>DB: insertApprovalRequest()
    DB-->>API: approvalId (status: pending)
    API-->>D: { approvalId, status: "pending" }

    loop Polling
        D->>API: GET /tasks/[taskId]/runtime-approvals/[approvalId]
        API->>S: listApprovalsSync()
        S-->>API: Approval Object
        API-->>D: { status: "pending" }
    end

    UI->>S: resolveApprovalRequest()
    S->>DB: updateApprovalStatus(approved)
    
    D->>API: GET /tasks/[taskId]/runtime-approvals/[approvalId]
    API-->>D: { status: "approved" }
    Note left of D: Resume Tool Execution
```
**Sources:** [apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/route.ts:8-50](), [apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/[approvalId]/route.ts:7-34](), [packages/services/src/approval.ts:1-50]()

---

## Key Components & Implementation

### Approval Request Types
Approvals are categorized by their `type` in the domain model. While the system supports various governance checkpoints, `runtime_tool` is the most common for active agent tasks.

| Type | Purpose | Triggered By |
| :--- | :--- | :--- |
| `runtime_tool` | Authorize a specific tool call (e.g., shell command, file write). | `daemon` via `AgentRouter` |
| `document_access` | Access to a restricted knowledge base or file. | `KnowledgeService` |
| `budget_limit` | Requesting additional tokens or spend for a task. | `CostService` |

**Sources:** [packages/domain/src/approval.ts:1-20](), [apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/route.ts:23-41]()

### Daemon-Side Polling
When an agent runtime (e.g., Claude Code or Codex) encounters a tool that requires a "Human Checkpoint," the `daemon` pauses execution. It uses the `POST` route at `/api/daemon/tasks/[taskId]/runtime-approvals` to register the request [apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/route.ts:8-11]().

The `daemon` then enters a polling loop, hitting the `GET` endpoint for that specific `approvalId` [apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/[approvalId]/route.ts:7-10](). The runtime only proceeds if the status returned is `approved`.

### Security & Authentication
Approval routes are protected by `requireDaemonAuth`, ensuring that only the daemon assigned to the workspace can query or create approvals for its tasks [apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/route.ts:12-15](). Furthermore, `readTaskForWorkspace` validates that the `taskId` belongs to the authenticated daemon's workspace context [apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/route.ts:18-21]().

---

## Code Entity Mapping

This section maps the high-level approval concepts to the specific functions and files implementing them.

**Diagram: Approval Logic Mapping**
```mermaid
graph TD
    subgraph "Web API Layer"
        R_POST["POST .../runtime-approvals"]:::file
        R_GET["GET .../[approvalId]"]:::file
    end

    subgraph "Service Layer (@agent-space/services)"
        S_CREATE["createRuntimeToolApprovalRequestSync"]:::func
        S_LIST["listApprovalsSync"]:::func
        S_RESOLVE["resolveApprovalRequest"]:::func
    end

    subgraph "Database Layer (@agent-space/db)"
        DB_REPO["approvalRepository"]:::file
        T_APPROVE["table: approval_requests"]:::table
    end

    R_POST --> S_CREATE
    R_GET --> S_LIST
    S_CREATE --> DB_REPO
    S_LIST --> DB_REPO
    S_RESOLVE --> DB_REPO
    DB_REPO --> T_APPROVE

    classDef file font-family:monospace,fill:transparent
    classDef func font-family:monospace,fill:transparent
    classDef table font-family:monospace,fill:transparent
```
**Sources:** [apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/route.ts:1-3](), [apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/[approvalId]/route.ts:1-2](), [packages/services/src/approval.ts:1-10]()

### Important Functions

#### `createRuntimeToolApprovalRequestSync`
Located in `@agent-space/services`, this function handles the business logic of creating a request. It extracts metadata such as `channelName` from the task input to provide context to the human reviewer [apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/route.ts:31-41]().

#### `materializeOutputBundleToStaging`
While not a direct approval function, this utility in `apps/web/app/api/daemon/_lib/output-bundle.ts` ensures that any files generated by an agent (which might require human review before finalization) are safely staged in a directory under `runtime-output/` [apps/web/app/api/daemon/_lib/output-bundle.ts:23-46]().

**Sources:** [apps/web/app/api/daemon/_lib/output-bundle.ts:23-66](), [apps/web/app/api/daemon/tasks/[taskId]/runtime-approvals/route.ts:52-59]()

---

# Page: Deployment & Infrastructure

# Deployment & Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [README.md](README.md)
- [apps/web/app/api/daemon/package/route.ts](apps/web/app/api/daemon/package/route.ts)

</details>



AgentSpace is designed to be flexible, supporting environments ranging from local development machines to distributed cloud infrastructures. The deployment model is governed by the `AGENT_SPACE_DEPLOYMENT_MODE` environment variable, which determines how the system handles database connections and file storage [.env.example:4-4]().

## Deployment Modes

AgentSpace provides two primary deployment paths to balance control and ease of use.

| Mode | Database | Attachment Storage | Best For |
| :--- | :--- | :--- | :--- |
| `self_hosted` | Local PostgreSQL | Local Filesystem | Teams requiring full data sovereignty and local CLI execution. |
| `cloud` | Neon (Serverless) | Cloudflare R2 | Scalable production environments and distributed teams. |

### Self-Hosted Deployment
In `self_hosted` mode, the system expects a standard PostgreSQL instance and a local directory for storing workspace attachments [.env.example:7-11](). This mode is ideal for internal networks where the agent daemon and web server reside on the same infrastructure.

For details, see [Self-Hosted Deployment](#8.1).

### Cloud Deployment
`cloud` mode utilizes serverless infrastructure to minimize maintenance. It leverages **Neon** for PostgreSQL, providing features like instant database branching for testing, and **Cloudflare R2** for S3-compatible object storage [.env.example:16-40]().

For details, see [Cloud Deployment (Neon + Cloudflare R2)](#8.2).

## Infrastructure Overview

The infrastructure bridges the "Natural Language Space" (where users interact with agents) and the "Code Entity Space" (where services and daemons execute logic).

### System Component Architecture

This diagram illustrates how the deployment components interact across the network boundary.

```mermaid
graph TD
    subgraph "External_Services"
        ["Google_OAuth"]
        ["Neon_Postgres"]
        ["Cloudflare_R2"]
    end

    subgraph "Production_Server"
        ["Nginx_Reverse_Proxy"]
        ["Web_App_Service"]
        ["PostgreSQL_Local"]
    end

    subgraph "Execution_Host"
        ["Daemon_Service"]
        ["Sandbox_Environment"]
    end

    ["Nginx_Reverse_Proxy"] --> ["Web_App_Service"]
    ["Web_App_Service"] --> ["PostgreSQL_Local"]
    ["Web_App_Service"] --> ["Neon_Postgres"]
    ["Web_App_Service"] --> ["Cloudflare_R2"]
    
    ["Daemon_Service"] -- "Polling /api/daemon/*" --> ["Nginx_Reverse_Proxy"]
    ["Daemon_Service"] --> ["Sandbox_Environment"]
```
**Sources:** [.env.example:4-40](), [apps/web/app/api/daemon/package/route.ts:7-21]()

### Code Entity Mapping: Deployment & Storage

This diagram maps infrastructure concepts to specific code entities and environment configurations used during deployment.

```mermaid
graph LR
    subgraph "Environment_Config"
        ["AGENT_SPACE_DEPLOYMENT_MODE"]
        ["SELF_HOSTED_DATABASE_URL"]
        ["NEON_DATABASE_URL"]
        ["CLOUDFLARE_R2_BUCKET"]
    end

    subgraph "Web_Server_Entities"
        ["buildDaemonPackageTarball"]
        ["requireDaemonAuth"]
        ["api/attachments/route.ts"]
    end

    subgraph "Storage_Abstraction"
        ["LocalRoot"]
        ["R2Client"]
        ["SignedURLs"]
    end

    ["AGENT_SPACE_DEPLOYMENT_MODE"] -- "self_hosted" --> ["LocalRoot"]
    ["AGENT_SPACE_DEPLOYMENT_MODE"] -- "cloud" --> ["R2Client"]
    ["NEON_DATABASE_URL"] --> ["Neon_Postgres"]
    ["CLOUDFLARE_R2_BUCKET"] --> ["SignedURLs"]
    ["buildDaemonPackageTarball"] -- "Generates" --> ["Daemon_Deployment_Artifact"]
```
**Sources:** [.env.example:4-49](), [apps/web/app/api/daemon/package/route.ts:1-13]()

## Testing Infrastructure

AgentSpace utilizes a robust testing pipeline centered around **Playwright** for End-to-End (E2E) verification. A key feature of the infrastructure is the integration with the **Neon API**, which allows the test suite to programmatically create isolated database branches for every test run [.env.example:23-30](). This ensures that E2E tests (such as workspace navigation and task dispatch) run against a clean, production-like schema without affecting the main database.

For details, see [Testing Infrastructure](#8.3).

## Key Configuration Requirements

Regardless of the deployment mode, several security and integration keys must be provisioned:
*   **Encryption Keys**: `NEXT_SERVER_ACTIONS_ENCRYPTION_KEY` and `AGENT_SPACE_GOOGLE_WORKSPACE_TOKEN_ENCRYPTION_KEY` are required to secure server-side operations and sensitive OAuth tokens [.env.example:62-79]().
*   **OAuth Credentials**: Google Client IDs and Secrets are necessary for user authentication and Google Workspace integrations [.env.example:68-76]().
*   **Signed URLs**: The `ATTACHMENT_SIGNED_URL_TTL_SECONDS` setting controls the lifespan of temporary access links for files stored in R2 or local storage [.env.example:47-47]().

**Sources:**
- [.env.example:1-82]()
- [apps/web/app/api/daemon/package/route.ts:1-21]()
- [README.md:68-78]()

---

# Page: Self-Hosted Deployment

# Self-Hosted Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [README.md](README.md)
- [apps/cli/src/commands/db.ts](apps/cli/src/commands/db.ts)

</details>



The Self-Hosted deployment mode is designed for teams requiring full control over data sovereignty, infrastructure, and execution runtimes. In this mode, AgentSpace operates using a local PostgreSQL instance and stores file attachments on the local filesystem rather than using cloud-native services like Neon or Cloudflare R2.

This page provides the technical specifications for configuring the systemd service units, the Nginx reverse proxy, and the environment variables required to run the AgentSpace Web Server and the AgentSpace Daemon on a private Linux host.

## System Architecture & Data Flow

In a self-hosted environment, the system is split into two primary operational units: the **Web Server** (Next.js) and the **Execution Daemon**.

### Component Interaction Diagram

The following diagram illustrates the relationship between the system components and the specific code entities that manage their communication.

"Self-Hosted Component Architecture"
```mermaid
graph TD
    subgraph "Web Host"
        A["Next.js App (apps/web)"] -- "SQL Queries" --> B[("PostgreSQL")]
        A -- "Local FS IO" --> C["Attachment Root"]
        A -- "HTTP/Nginx" --> D["Public Internet"]
    end

    subgraph "Execution Host"
        E["Daemon (packages/daemon)"] -- "Poll /api/daemon/tasks/claim" --> A
        E -- "Execute" --> F["Sandbox (packages/sandbox)"]
        F -- "Run" --> G["AgentRouter (packages/daemon)"]
    end

    subgraph "External"
        H["Google OAuth"] -- "Redirect" --> A
    end

    style A stroke-width:2px
    style E stroke-width:2px
```
Sources: [.env.example:1-11](), [README.md:70-77]()

## Environment Configuration

The application determines its behavior based on the `AGENT_SPACE_DEPLOYMENT_MODE` variable. For self-hosted setups, this must be set to `self_hosted`.

### Required Environment Variables
| Variable | Value/Example | Description |
| :--- | :--- | :--- |
| `AGENT_SPACE_DEPLOYMENT_MODE` | `self_hosted` | Switches storage and DB logic to local providers. |
| `SELF_HOSTED_DATABASE_URL` | `postgres://user:pass@127.0.0.1:5432/db` | Connection string for local PostgreSQL. |
| `SELF_HOSTED_ATTACHMENT_LOCAL_ROOT` | `/var/lib/agentspace/workspaces` | Directory for storing task files and uploads. |
| `AGENT_SPACE_APP_URL` | `https://agentspace.example.com` | The public URL of your deployment. |
| `NEXT_SERVER_ACTIONS_ENCRYPTION_KEY` | `<Base64 Key>` | Required for Next.js Server Actions security. |

Sources: [.env.example:1-12](), [.env.example:56-62]()

## PostgreSQL Initialization

AgentSpace requires PostgreSQL 16+. The database layer in `@agent-space/db` manages the schema for over 50 tables.

1. **Create Database**:
   ```sql
   CREATE DATABASE agent_space;
   CREATE USER agent_space WITH PASSWORD 'agent_space';
   GRANT ALL PRIVILEGES ON DATABASE agent_space TO agent_space;
   ```

2. **Verify Connectivity**:
   You can use the CLI to check the database status:
   `agent-space db status` calls `getDatabaseStatusSync` to verify the connection and migration state.

Sources: [apps/cli/src/commands/db.ts:11-14](), [README.md:14-14]()

## Systemd Service Configuration

To ensure high availability, both the web server and the daemon should be managed by `systemd`.

### 1. Web Service (`agentspace.service`)
This service runs the Next.js application. It should be configured to restart on failure.

```ini
[Unit]
Description=AgentSpace Web Server
After=network.target postgresql.service

[Service]
Type=simple
User=agentspace
WorkingDirectory=/opt/agentspace
EnvironmentFile=/etc/agentspace/web.env
ExecStart=/usr/bin/npm run start:web
Restart=always

[Install]
WantedBy=multi-user.target
```

### 2. Daemon Service (`agentspace-daemon.service`)
The daemon polls the web server for tasks. It requires access to the `AgentRouter` to spawn agent runtimes.

```ini
[Unit]
Description=AgentSpace Execution Daemon
After=network.target agentspace.service

[Service]
Type=simple
User=agentspace
WorkingDirectory=/opt/agentspace
EnvironmentFile=/etc/agentspace/daemon.env
ExecStart=/usr/bin/npm run start:daemon
Restart=always

[Install]
WantedBy=multi-user.target
```

Sources: [README.md:70-77](), [.env.example:4-11]()

## Nginx Proxy Configuration

Nginx acts as the SSL termination point and reverse proxy for the Next.js application (defaulting to port 1455).

```nginx
server {
    listen 443 ssl;
    server_name agentspace.example.com;

    location / {
        proxy_pass http://127.0.0.1:1455;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Increase client_max_body_size for large attachments
    client_max_body_size 50M;
}
```

Sources: [.env.example:48-48](), [.env.example:56-56]()

## Storage Management

In `self_hosted` mode, the system uses the local filesystem for workspace artifacts. The CLI provides tools to manage this storage.

### Storage Artifacts Scanning
The command `agent-space db storage-scan` invokes `scanStorageArtifactsSync` from `@agent-space/services/storage/storage-scan`. This identifies all files currently stored in the `SELF_HOSTED_ATTACHMENT_LOCAL_ROOT`.

### Workspace Purging
To remove all local data associated with a specific workspace, use the `workspace-purge` command:
```bash
agent-space db workspace-purge --id <workspace-id> --force
```
This executes `purgeWorkspaceStorageSync`, which deletes the physical directory associated with the workspace ID from the local root.

Sources: [apps/cli/src/commands/db.ts:16-42](), [.env.example:10-11]()

## Deployment Entity Mapping

The following diagram maps the logical deployment components to the internal code structures used for execution and data management.

"Code Entity Mapping for Deployment"
```mermaid
graph LR
    subgraph "Logic Layer"
        SA["Storage Service"] -- "calls" --> PSR["purgeWorkspaceStorageSync"]
        DBS["DB Service"] -- "calls" --> GDS["getDatabaseStatusSync"]
    end

    subgraph "CLI Entrypoints"
        CMD["runDatabaseCommand"] -- "subcommand: status" --> GDS
        CMD -- "subcommand: workspace-purge" --> PSR
    end

    subgraph "Infrastructure"
        PSR -- "targets" --> ALR["ATTACHMENT_LOCAL_ROOT"]
        GDS -- "targets" --> SDU["SELF_HOSTED_DATABASE_URL"]
    end

    subgraph "Configuration"
        ENV[".env"] -- "defines" --> ALR
        ENV -- "defines" --> SDU
    end
```
Sources: [apps/cli/src/commands/db.ts:1-42](), [.env.example:7-11]()

---

# Page: Cloud Deployment (Neon + Cloudflare R2)

# Cloud Deployment (Neon + Cloudflare R2)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [apps/web/app/api/attachments/[attachmentId]/route.test.ts](apps/web/app/api/attachments/[attachmentId]/route.test.ts)
- [apps/web/app/api/attachments/[attachmentId]/route.ts](apps/web/app/api/attachments/[attachmentId]/route.ts)

</details>



AgentSpace supports a "Cloud" deployment mode designed for serverless scalability and high availability. This configuration replaces local file storage and standard PostgreSQL with managed cloud services: **Neon** for serverless PostgreSQL and **Cloudflare R2** for S3-compatible object storage.

## Deployment Mode Configuration

The system toggles between local and cloud infrastructure based on the `AGENT_SPACE_DEPLOYMENT_MODE` environment variable [`.env.example:1-4`](). When set to `cloud`, the application expects configuration for Neon and Cloudflare R2.

| Variable | Mode: `self_hosted` | Mode: `cloud` |
| :--- | :--- | :--- |
| **Database** | Local PostgreSQL [`.env.example:7-8`]() | Neon Serverless Postgres [`.env.example:16-17`]() |
| **Storage** | Local Filesystem [`.env.example:11`]() | Cloudflare R2 [`.env.example:32-40`]() |
| **Scaling** | Single-node vertical | Multi-region horizontal |

Sources: [`.env.example:1-44`]()

## Database: Neon Serverless PostgreSQL

In cloud mode, AgentSpace utilizes Neon's serverless architecture. Neon provides two distinct connection strings to optimize performance and migration reliability:

1.  **Pooled Connection (`NEON_DATABASE_URL`)**: Uses Neon's connection pooler (PgBouncer) for the application runtime to handle high concurrency [`.env.example:16`]().
2.  **Direct Connection (`NEON_DATABASE_DIRECT_URL`)**: Bypasses the pooler for schema migrations and administrative tasks to avoid session-level transaction conflicts [`.env.example:17`]().

### E2E Test Branching
AgentSpace leverages the Neon API to provide isolated database environments for E2E testing. During test execution, the system creates a temporary branch from the `production` parent [`.env.example:23-28`]().

**Data Flow: Neon Branching Lifecycle**
1.  Playwright test runner invokes the Neon API using `NEON_API_KEY` [`.env.example:30`]().
2.  A new database branch is created with a unique ID [`.env.example:26`]().
3.  The web server is pointed to this branch's unique connection string.
4.  The branch is automatically suspended or deleted after the `AGENT_SPACE_E2E_NEON_SUSPEND_TIMEOUT_SECONDS` period [`.env.example:29`]().

Sources: [`.env.example:13-30`]()

## Object Storage: Cloudflare R2

Attachments (images, documents, logs) are stored in Cloudflare R2 when in cloud mode. The integration uses an S3-compatible client to manage file lifecycles.

### Implementation Details
The storage logic is abstracted through the `createAttachmentStorageClient` function in the services layer [`apps/web/app/api/attachments/[attachmentId]/route.ts:8`]().

**Key Configuration Parameters:**
*   **Endpoint**: R2 uses a custom account-specific endpoint: `https://<ACCOUNT_ID>.r2.cloudflarestorage.com` [`.env.example:37`]().
*   **Signed URLs**: The `ATTACHMENT_SIGNED_URL_TTL_SECONDS` (default: 300s) controls the expiration of pre-signed URLs used for secure browser access [`.env.example:47`]().
*   **Upload Limits**: `ATTACHMENT_MAX_UPLOAD_BYTES` (default: 50MB) enforces size constraints at the application gateway [`.env.example:48`]().

### Attachment Retrieval Flow
When a user or agent requests an attachment via `/api/attachments/[attachmentId]`, the server executes the following logic:

**Diagram: Cloud Attachment Resolution**
```mermaid
graph TD
    subgraph "apps/web/app/api/attachments/[attachmentId]/route.ts"
        A["GET Request"] --> B["getCurrentWorkspaceContext()"]
        B --> C{"Authorized?"}
        C -- "No" --> D["401 Unauthorized"]
        C -- "Yes" --> E["readStoredAttachmentSync()"]
        E --> F{"Is Cloud Storage?"}
        F -- "storageProvider == 'r2'" --> G["createAttachmentStorageClient()"]
        G --> H["getObject() from R2"]
        F -- "local" --> I["readFile() from Disk"]
        H --> J["Return Response with Cache-Control"]
        I --> J
    end
```

Sources: [`apps/web/app/api/attachments/[attachmentId]/route.ts:25-155`](), [`apps/web/app/api/attachments/[attachmentId]/route.ts:157-167`](), [`.env.example:32-49`]()

## Data Flow & Security

The cloud deployment maintains strict workspace isolation even when using shared cloud buckets and databases.

### Cross-Workspace Protection
The `GET` handler in the attachments API explicitly checks if the `requestedWorkspaceId` matches the `workspaceContext.currentWorkspace.id` [`apps/web/app/api/attachments/[attachmentId]/route.ts:35-36`](). If a mismatch is detected, it logs a `workspace.cross_workspace_access_denied` audit event and returns a 403 Forbidden [`apps/web/app/api/attachments/[attachmentId]/route.ts:37-51`]().

### Caching Strategy
To reduce egress costs and improve performance, the system applies specific `Cache-Control` headers:
*   **Images**: `private, max-age=3600, stale-while-revalidate=86400` [`apps/web/app/api/attachments/[attachmentId]/route.ts:21`]().
*   **Files**: `private, no-cache` [`apps/web/app/api/attachments/[attachmentId]/route.ts:22`]().
*   **ETags**: Generated based on the attachment's SHA256 hash [`apps/web/app/api/attachments/[attachmentId]/route.ts:97-109`]().

**Diagram: Entity Mapping (Natural Language to Code)**
```mermaid
graph LR
    subgraph "Natural Language Concept"
        DB["Cloud Database"]
        Storage["Object Storage"]
        Sec["Access Control"]
    end

    subgraph "Code Entity Space"
        DB_URL["NEON_DATABASE_URL"]
        R2_CLIENT["createAttachmentStorageClient()"]
        AUDIT["tryRecordWorkspaceAuditEventSync()"]
        CTX["getCurrentWorkspaceContext()"]
    end

    DB --- DB_URL
    Storage --- R2_CLIENT
    Sec --- AUDIT
    Sec --- CTX
```

Sources: [`apps/web/app/api/attachments/[attachmentId]/route.ts:1-155`](), [`.env.example:1-82`]()

---

# Page: Testing Infrastructure

# Testing Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [apps/cli/src/commands/cost.test.ts](apps/cli/src/commands/cost.test.ts)
- [apps/cli/src/commands/daemon.test.ts](apps/cli/src/commands/daemon.test.ts)
- [apps/cli/src/commands/workspace.test.ts](apps/cli/src/commands/workspace.test.ts)
- [apps/web/app/api/daemon/client.integration.test.ts](apps/web/app/api/daemon/client.integration.test.ts)
- [apps/web/app/api/daemon/routes.test.ts](apps/web/app/api/daemon/routes.test.ts)

</details>



The AgentSpace testing infrastructure encompasses End-to-End (E2E) browser testing, unit and integration testing for CLI/Web/Daemon components, and a specialized database branching strategy for isolated cloud-based test environments.

## End-to-End (E2E) Testing with Playwright

AgentSpace uses Playwright for cross-browser and cross-device functional testing. These tests ensure the integrity of the workspace shell, navigation flows, and critical user journeys.

### Test Suites
*   **Smoke Tests**: Validates core authentication and landing page availability.
*   **Mobile Smoke**: Specialized viewports to ensure the responsive workspace shell remains functional on mobile devices.
*   **Workspace Navigation**: Exercises the multi-module workspace UI at `/w/[workspaceSlug]`, verifying that the sidebar, module cache, and lazy loaders function correctly.

### Neon Database Branching
For E2E tests running in `cloud` mode, the infrastructure leverages the Neon API to create ephemeral database branches. This provides every test run with a fully isolated PostgreSQL environment that is a direct clone of the production schema.

| Environment Variable | Purpose |
| :--- | :--- |
| `AGENT_SPACE_E2E_NEON_PROJECT_ID` | The target Neon project for branch creation. |
| `AGENT_SPACE_E2E_NEON_PARENT_BRANCH` | The source branch (usually `production` or `main`) to clone from. |
| `NEON_API_KEY` | Secret key used to authenticate with Neon for lifecycle management. |

**Sources:** [ .env.example:23-30 ]()

## Unit and Integration Testing Patterns

Testing is distributed across the monorepo, utilizing `node:test` for CLI/Services and `vitest` for the Web application.

### CLI Command Testing
CLI tests focus on command execution, workspace context resolution, and local filesystem interactions. They utilize temporary directories (`mkdtempSync`) to simulate isolated workspace environments.

*   **Context Resolution**: Tests like `workspace.test.ts` verify that the CLI correctly infers the active agent and task ID from environment variables such as `AGENT_SPACE_CONTEXT_AGENT_NAME` and `AGENT_SPACE_CONTEXT_TASK_ID` [ apps/cli/src/commands/workspace.test.ts:30-50 ]().
*   **Cost & Budgeting**: Tests verify that cost summaries and budget limits are correctly filtered by `--workspace-id` [ apps/cli/src/commands/cost.test.ts:33-62 ]().
*   **Output Handling**: `loadTaskOutputEnvelope` is tested to ensure it correctly handles relative paths, rejects absolute paths, and enforces attachment size limits [ apps/cli/src/commands/daemon.test.ts:29-176 ]().

### Web API & Daemon Integration Testing
The web layer includes integration tests that mock the HTTP boundary between the Daemon and the Server.

*   **HttpDaemonClient**: Tested in `client.integration.test.ts` to ensure it can register runtimes, claim tasks, and upload output bundles [ apps/web/app/api/daemon/client.integration.test.ts:70-205 ]().
*   **Route Verification**: Tests in `routes.test.ts` verify that Daemon API routes (e.g., `/api/daemon/register`, `/api/daemon/tasks/[taskId]/start`) correctly enforce bearer token authentication and process business logic [ apps/web/app/api/daemon/routes.test.ts:149-180 ]().

### Data Flow: Task Lifecycle Testing
The following diagram illustrates the integration points exercised during a standard task execution test.

**Task Execution Test Flow**
```mermaid
sequenceDiagram
    participant T as Test Runner
    participant S as @agent-space/services
    participant D as @agent-space/db
    participant C as HttpDaemonClient
    participant R as API Routes

    T->>S: resetWorkspaceStateSync()
    T->>S: initializeOrganizationSync()
    T->>S: sendContactMessageSync("Atlas", "Task Request")
    S->>D: enqueueNativeTaskSync()
    
    T->>C: claimTask(runtimeId)
    C->>R: POST /runtimes/[id]/tasks/claim
    R->>T: Returns Task JSON
    
    T->>C: uploadOutputBundle(taskId, bundle)
    C->>R: POST /tasks/[id]/output-bundle
    R->>D: writeWorkspaceStateSync() (with artifacts)
```
**Sources:** [ apps/web/app/api/daemon/client.integration.test.ts:119-205 ](), [ apps/cli/src/commands/daemon.test.ts:29-57 ]()

## Test Environment Seeding

The codebase utilizes "Sync" versions of service and database functions to seed data deterministically before test execution.

### Key Seeding Functions
| Function | File | Purpose |
| :--- | :--- | :--- |
| `resetWorkspaceStateSync` | `@agent-space/services` | Wipes the current workspace state to ensure test isolation. |
| `initializeOrganizationSync` | `@agent-space/services` | Sets up the initial organization, owner, and first channel. |
| `seedWorkspaceCosts` | `apps/cli/src/commands/cost.test.ts` | Populates `token_usage` and `agent_task_queue` for budget testing. |
| `registerDaemonRuntimesSync` | `@agent-space/db` | Simulates a daemon connecting and offering specific provider capabilities. |

**Sources:** [ apps/cli/src/commands/cost.test.ts:68-114 ](), [ apps/cli/src/commands/workspace.test.ts:85-176 ]()

## Code Entity Mapping

The testing infrastructure bridges the high-level "Task" concept with low-level database and file entities.

**Entity Mapping: Task Output Testing**
```mermaid
graph TD
    subgraph "Natural Language Space"
        Task["Agent Task"]
        Artifact["Result File (e.g. chart.png)"]
        Cost["Usage Cost"]
    end

    subgraph "Code Entity Space"
        Task --> TQ["agent_task_queue (DB Table)"]
        TQ --> AT["agent_task_attempt (DB Table)"]
        Artifact --> LO["loadTaskOutputEnvelope() (Function)"]
        Artifact --> OB["output-bundle (API Route)"]
        Cost --> TU["token_usage (DB Table)"]
        Cost --> RC["runCostCommand() (CLI Command)"]
    end

    style Task stroke-dasharray: 5 5
    style Artifact stroke-dasharray: 5 5
    style Cost stroke-dasharray: 5 5
```
**Sources:** [ apps/cli/src/commands/daemon.test.ts:13-44 ](), [ apps/cli/src/commands/cost.test.ts:17-62 ](), [ apps/web/app/api/daemon/client.integration.test.ts:11-33 ]()

## Load Testing
Load testing scripts (located in `scripts/load-test` or similar) focus on:
1.  **Task Polling**: Measuring the latency of the `claimTask` route under high daemon concurrency.
2.  **State Persistence**: Verifying the performance of the synchronous worker-thread query model in `@agent-space/db` when multiple tasks are reporting `token_usage` and `task_execution_event` updates simultaneously.

**Sources:** [ apps/web/app/api/daemon/client.integration.test.ts:45-68 ](), [ apps/web/app/api/daemon/routes.test.ts:92-140 ]()

---

# Page: Glossary

# Glossary

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [README.md](README.md)
- [README_ZH.md](README_ZH.md)
- [agent-space-daemon-0.1.3.tgz](agent-space-daemon-0.1.3.tgz)
- [apps/cli/package-lock.json](apps/cli/package-lock.json)
- [apps/cli/package.json](apps/cli/package.json)

</details>



This page provides definitions for the core terminology, architectural concepts, and domain-specific entities used within the AgentSpace codebase. It serves as a technical reference for onboarding engineers to bridge the gap between natural language descriptions and the underlying code implementation.

## Core Concepts

### Digital Employee
A **Digital Employee** (often referred to simply as an **Employee** or **Agent**) is a first-class entity in AgentSpace. Unlike a stateless chatbot, a Digital Employee has a persistent identity, a defined role, an owner, and a set of capabilities.

*   **Implementation**: Represented by the `Employee` type in the domain package [[packages/domain]()] and managed via the `EmployeeService` [[packages/services]()] in the services layer.
*   **Attributes**: Includes `instructions`, `skills`, and `knowledge` sets that define its behavior across different tasks.

### Workspace
The top-level container for collaboration. All employees, channels, tasks, and documents belong to a specific **Workspace**. It acts as the multi-tenant boundary.

*   **Implementation**: Defined in `Workspace` domain models [[packages/domain]()] and handled by the `WorkspaceService` [[packages/services]()].
*   **Routing**: In the web application, workspaces are accessed via the `/w/[workspaceSlug]` route pattern [[apps/web]()].

### AgentRouter
The execution abstraction layer that decouples an Agent's identity from the underlying provider runtime (e.g., Claude Code, Codex, OpenClaw).

*   **Implementation**: Found in `packages/daemon/bin/agent-router.js` [[packages/daemon:37-37]()] and the internal `AgentRouter` class.
*   **Role**: It normalizes diverse CLI behaviors into a unified event stream and result format, allowing the same Agent to run on different harnesses depending on the task requirements [[README.md:115-123]()].

### Daemon
A background process (often remote) that claims tasks from the AgentSpace server, prepares the execution environment, and invokes the `AgentRouter`.

*   **Implementation**: Located in `packages/daemon` [[packages/daemon]()] with the entry point at `bin/agent-space-daemon.js` [[packages/daemon:36-36]()].
*   **Lifecycle**: The daemon performs a "claim-work-report" loop, communicating with the server via the Daemon API routes [[apps/web/src/app/api/daemon]()] (e.g., `/api/daemon/tasks/claim`).

---

## Technical Glossary Table

| Term | Definition | Code Pointer |
| :--- | :--- | :--- |
| **Harness** | An adapter for a specific LLM/Agent provider (e.g., `ClaudeCodeHarness`). | `packages/daemon/src/harnesses` |
| **Sandbox** | An isolation layer (Local or Cube) where the Agent executes code and filesystem operations. | `packages/sandbox` [[packages/daemon/package-lock.json:31-31]()] |
| **Task Bundle** | A packaged set of inputs (instructions, files, tokens) sent to a Daemon to start a task. | `packages/domain` (TaskBundle type) |
| **Runtime Grant** | A permission record allowing a specific user or agent to use a runtime/tool. | `packages/services` (GrantService) |
| **Approval Queue** | A system for "Human-in-the-loop" governance where sensitive tool calls wait for manual confirmation. | `apps/web/src/modules/approvals` |
| **Skill** | A reusable set of tools or functions that can be attached to a Digital Employee. | `packages/services` (SkillService) |

---

## Architecture Diagrams

### From Concept to Code: Task Execution Flow
The following diagram maps the high-level concept of "Running a Task" to the specific code entities and packages involved.

**Task Dispatch & Execution Mapping**
```mermaid
graph TD
    subgraph "Web App (apps/web)"
        A["TaskBoard UI"] -- "Trigger" --> B["TaskService.createTask()"]
        B -- "Insert" --> DB[("PostgreSQL (@agent-space/db)")]
        C["/api/daemon/tasks/claim"] -- "Polls" --> DB
    end

    subgraph "Daemon Package (packages/daemon)"
        D["agent-space-daemon.js"] -- "HTTP GET" --> C
        D -- "Init" --> E["AgentRouter"]
        E -- "Wrap" --> F["Provider Harness (e.g. ClaudeCode)"]
    end

    subgraph "Execution Layer (packages/sandbox)"
        F -- "Execute in" --> G["LocalSandbox / CubeSandbox"]
        G -- "Filesystem" --> H["Workspace Root"]
    end

    D -- "HTTP POST Result" --> I["/api/daemon/tasks/complete"]
    I -- "Update" --> DB
```
**Sources:** [[apps/cli/package.json:14-18]()], [[packages/daemon/package-lock.json:25-33]()], [[README.md:115-123]()]

### System Identity & Permissions
This diagram shows how natural language "Governance" is enforced through specific service classes and database relations.

**Governance & Access Control Mapping**
```mermaid
graph LR
    subgraph "Domain Entities (@agent-space/domain)"
        User["User"]
        Emp["Digital Employee"]
        WS["Workspace"]
    end

    subgraph "Logic Layer (@agent-space/services)"
        Auth["AuthService"]
        Grant["GrantService"]
        Appr["ApprovalService"]
    end

    subgraph "Data Layer (@agent-space/db)"
        R_Role["workspace_roles table"]
        R_Grant["runtime_grants table"]
        R_Appr["approval_requests table"]
    end

    User -- "Has Role" --> R_Role
    Emp -- "Owned by" --> User
    Emp -- "Requires" --> Appr
    Appr -- "Writes to" --> R_Appr
    Grant -- "Checks" --> R_Grant
    Auth -- "Validates" --> WS
```
**Sources:** [[README.md:149-157]()], [[.env.example:64-70]()], [[apps/cli/package-lock.json:11-13]()]

---

## Key File Paths & Roles

### `packages/domain`
Contains the TypeScript interfaces and types that define the "Source of Truth" for data structures used across the monorepo. Every developer should check here first when modifying data models.
**Sources:** [[packages/daemon/package-lock.json:61-65]()]

### `packages/db`
The PostgreSQL client and repository layer. It uses `pg` and manages the connection pool. It is responsible for all raw SQL execution and migration logic.
**Sources:** [[packages/daemon/package-lock.json:47-53]()]

### `packages/services`
The "Business Logic" layer. If you are implementing a feature like "Transferring an Agent" or "Approving a Tool Call," the logic resides here so it can be shared between the Web UI and the CLI.
**Sources:** [[packages/daemon/package-lock.json:66-75]()]

### `apps/web/src/modules`
The modular UI implementation. Each subdirectory (e.g., `agents`, `tasks`, `approvals`) contains the Server Actions, React Components, and Hooks specific to that feature.
**Sources:** [[README.md:173-181]()]

### `.env.example`
The definitive guide to system configuration, including deployment modes (`self_hosted` vs `cloud`), database URLs, and integration secrets for Google Workspace.
**Sources:** [[.env.example:1-82]()]