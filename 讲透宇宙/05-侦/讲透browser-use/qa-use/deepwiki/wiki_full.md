# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This document provides a comprehensive technical overview of the QA Use platform, an AI-powered end-to-end testing system that enables automated web application testing through natural language test definitions. The platform leverages BrowserUse AI agents to execute tests defined in plain English, providing intelligent browser automation with human-like testing capabilities.

This overview covers the high-level architecture, core components, and system interactions. For detailed implementation guidance, see [Getting Started](#2). For specific UI components and user workflows, see [User Interface](#4). For background processing details, see [Background Processing](#6).

## System Architecture Overview

QA Use is built as a modern web application with a clear separation between frontend presentation, backend services, and external AI-powered execution engines. The system orchestrates test execution through event-driven background processing while maintaining real-time visibility into test progress.

### High-Level Component Architecture

```mermaid
graph TB
    subgraph "Frontend_Layer" ["Frontend Layer"]
        NextApp["Next.js Application<br/>(app directory structure)"]
        Pages["Route Handlers<br/>page.tsx components"]
        Components["React Components<br/>TestDetails, SuiteRunDetails"]
    end
    
    subgraph "Backend_Services" ["Backend Services"] 
        ServerActions["Server Actions<br/>actions/suites, actions/tests"]
        ApiRoutes["API Routes<br/>api/inngest/route.ts"]
        InngestService["Inngest Background Jobs<br/>lib/inngest/client.ts"]
    end
    
    subgraph "Data_Layer" ["Data Layer"]
        DrizzleORM["Drizzle ORM<br/>lib/db/schema.ts"]
        PostgresDB[("PostgreSQL Database<br/>suites, tests, runs tables")]
    end
    
    subgraph "AI_Engine" ["AI Testing Engine"]
        TestingEngine["Testing Engine<br/>lib/testing-engine.ts"]
        MockTests["Mock Test Definitions<br/>lib/mock-tests.ts"]
    end
    
    subgraph "External_Services" ["External Services"]
        BrowserUseAPI["BrowserUse Cloud API<br/>api.browser-use.com"]
        ResendEmail["Resend Email Service<br/>email notifications"]
    end
    
    NextApp --> ServerActions
    NextApp --> Components
    ServerActions --> DrizzleORM
    ServerActions --> InngestService
    InngestService --> TestingEngine
    InngestService --> BrowserUseAPI
    TestingEngine --> MockTests
    TestingEngine --> BrowserUseAPI
    DrizzleORM --> PostgresDB
    InngestService --> ResendEmail
    ApiRoutes --> InngestService
```

**Sources:** [README.md:1-132](), [app/page.tsx:1-50](), [lib/db/schema.ts:1-200](), [lib/inngest/client.ts:1-50]()

### Technology Stack and Core Dependencies

The platform is built on a modern TypeScript stack with the following key technologies:

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend Framework** | Next.js 15 with App Router | Server-side rendering and routing |
| **UI Components** | React with Tailwind CSS | Component-based interface |
| **Database** | PostgreSQL with Drizzle ORM | Type-safe data persistence |
| **Background Processing** | Inngest | Event-driven job orchestration |
| **AI Testing** | BrowserUse Cloud API | AI-powered browser automation |
| **Email Notifications** | Resend API | Test failure alerts |
| **Containerization** | Docker Compose | Development and deployment |

**Sources:** [package.json:1-100](), [docker-compose.yaml:1-50](), [next.config.ts:1-20]()

## Core Components

### Database Schema and Data Model

The system uses a hierarchical data model that supports organizing tests into suites with detailed execution tracking:

```mermaid
erDiagram
    suites {
        serial id PK
        text name
        text cron_cadence
        text notifications_email
        timestamp created_at
    }
    
    tests {
        serial id PK
        text label
        text evaluation
        integer suite_id FK
        timestamp created_at
    }
    
    test_steps {
        serial id PK
        integer test_id FK
        integer order
        text description
    }
    
    suite_runs {
        serial id PK
        integer suite_id FK
        run_status status
        timestamp started_at
        timestamp finished_at
    }
    
    test_runs {
        serial id PK
        integer test_id FK
        integer suite_run_id FK
        run_status status
        text browser_use_id
        text live_url
        text public_share_url
    }
    
    test_run_steps {
        serial id PK
        integer test_run_id FK
        integer step_id FK
        run_status status
    }
    
    suites ||--o{ tests : "contains"
    suites ||--o{ suite_runs : "executes_as"
    tests ||--o{ test_steps : "composed_of"
    tests ||--o{ test_runs : "runs_as"
    suite_runs ||--o{ test_runs : "includes"
    test_runs ||--o{ test_run_steps : "tracks"
    test_steps ||--o{ test_run_steps : "executed_as"
```

**Sources:** [lib/db/schema.ts:10-150](), [lib/db/types.ts:1-50]()

### Testing Engine and AI Integration

The `TestingEngine` class serves as the core orchestrator for AI-powered test execution, handling prompt generation and result parsing:

```mermaid
graph LR
    subgraph "TestEngine_Flow" ["Testing Engine Flow"]
        TestDefinition["Test Definition<br/>(steps + evaluation)"]
        PromptGeneration["generatePrompt()<br/>lib/testing-engine.ts"]
        BrowserUseExecution["BrowserUse API<br/>executeTask()"]
        ResultValidation["AI Result Validation<br/>against success criteria"]
    end
    
    subgraph "Mock_System" ["Mock Test System"]
        MockTests["BROWSERUSE_DOCS_TESTS<br/>lib/mock-tests.ts"]
        TestCases["Pre-defined test cases<br/>for BrowserUse documentation"]
    end
    
    TestDefinition --> PromptGeneration
    PromptGeneration --> BrowserUseExecution
    BrowserUseExecution --> ResultValidation
    MockTests --> TestDefinition
```

**Sources:** [lib/testing-engine.ts:1-100](), [lib/mock-tests.ts:1-200]()

## Data Flow and Execution Pipeline

### Test Execution Orchestration

The platform uses an event-driven architecture where test execution is orchestrated through Inngest background jobs, ensuring reliable processing of long-running AI operations:

```mermaid
graph TD
    subgraph "User_Actions" ["User Actions"]
        CreateSuite["Create Test Suite<br/>actions/suites.ts"]
        TriggerRun["Execute Suite<br/>runSuite server action"]
    end
    
    subgraph "Inngest_Jobs" ["Inngest Background Processing"]
        SuiteRunJob["suite.run function<br/>lib/inngest/functions/suite.ts"]
        TestRunJob["test.run function<br/>lib/inngest/functions/test.ts"]
        EmailJob["test.failed function<br/>email notifications"]
    end
    
    subgraph "BrowserUse_Integration" ["BrowserUse Integration"]
        ApiClient["BrowserUse OpenAPI Client<br/>lib/browseruse-client.ts"]
        TaskExecution["AI Agent Execution<br/>browser automation"]
        LivePreview["Live URL Generation<br/>real-time monitoring"]
    end
    
    subgraph "Database_Updates" ["Database State Management"]
        StatusTracking["Run Status Updates<br/>pending → running → completed"]
        ResultStorage["Store execution results<br/>test_runs, test_run_steps"]
    end
    
    CreateSuite --> TriggerRun
    TriggerRun --> SuiteRunJob
    SuiteRunJob --> TestRunJob
    TestRunJob --> ApiClient
    ApiClient --> TaskExecution
    TaskExecution --> LivePreview
    TaskExecution --> StatusTracking
    StatusTracking --> ResultStorage
    TestRunJob --> EmailJob
```

**Sources:** [actions/suites.ts:1-100](), [lib/inngest/functions/suite.ts:1-150](), [lib/inngest/functions/test.ts:1-200](), [lib/browseruse-client.ts:1-100]()

### Real-time Monitoring and Updates

The system provides real-time visibility into test execution through a combination of live URLs from BrowserUse and database polling for status updates. The frontend components refresh execution state to show progress as tests run.

**Sources:** [app/suites/[id]/runs/[runId]/page.tsx:1-100](), [components/test-details.tsx:1-200]()

## Key Integration Points

### External Service Dependencies

The platform integrates with several external services to provide its full functionality:

| Service | Integration Point | Purpose |
|---------|------------------|---------|
| **BrowserUse Cloud API** | `lib/browseruse-client.ts` | AI-powered browser automation |
| **Resend Email API** | Email notification functions | Test failure alerts |
| **Inngest** | Background job processing | Reliable test orchestration |

### Environment Configuration

Critical configuration is managed through environment variables defined in the `.env` file:

- `BROWSER_USE_API_KEY`: Required for AI agent execution
- `DATABASE_URL`: PostgreSQL connection string  
- `RESEND_API_KEY`: Optional email notification service
- `INNGEST_SIGNING_KEY`: Background job service authentication

**Sources:** [.env.example:1-20](), [lib/env.ts:1-50]()

The QA Use platform demonstrates a production-ready architecture for AI-powered testing, combining modern web development practices with intelligent automation capabilities through the BrowserUse ecosystem.

---

# Page: Getting Started

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [Dockerfile](Dockerfile)
- [README.md](README.md)
- [docker-compose.dev.yaml](docker-compose.dev.yaml)
- [docker-compose.yaml](docker-compose.yaml)
- [media/run.png](media/run.png)
- [media/suite.png](media/suite.png)
- [next.config.ts](next.config.ts)
- [src/lib/api/client.ts](src/lib/api/client.ts)

</details>



This document covers the initial setup, deployment, and configuration of the QA Use platform. It provides step-by-step instructions for getting the system running locally or in production environments.

For information about the core data model and testing concepts, see [Core Concepts](#3). For details about the user interface and test management workflows, see [User Interface](#4).

## Prerequisites

The QA Use platform requires the following components before installation:

| Component | Purpose | Required |
|-----------|---------|----------|
| Docker & Docker Compose | Container orchestration | Yes |
| BrowserUse API Key | AI agent execution | Yes |
| Resend API Key | Email notifications | No |

### Obtaining API Keys

**BrowserUse API Key**: Register at [cloud.browser-use.com/billing](https://cloud.browser-use.com/billing) to obtain your API key for AI agent execution.

**Resend API Key**: Sign up at [resend.com](https://resend.com) for email notification capabilities. This is optional but recommended for production deployments.

Sources: [README.md:16-20]()

## Environment Configuration

The platform uses environment variables for external service integration and database connectivity. All configuration is managed through a `.env` file.

### Environment Variable Setup

```bash
# Copy the example configuration
cp .env.example .env
```

### Required Configuration

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `BROWSER_USE_API_KEY` | BrowserUse Cloud API authentication | `bu_live_xxx...` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@postgres:5432/qa-use` |

### Optional Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `RESEND_API_KEY` | Email service authentication | - |
| `RESEND_FROM_EMAIL` | Email sender address | `onboarding@resend.dev` |
| `INNGEST_SIGNING_KEY` | Background job security | - |
| `INNGEST_BASE_URL` | Inngest service endpoint | `http://inngest:8288` |

Sources: [.env.example:1-9](), [README.md:46-63]()

## Deployment Architecture

The platform consists of multiple containerized services orchestrated through Docker Compose. Two deployment configurations are available: development and production.

### Service Architecture

```mermaid
graph TB
    subgraph "QA Use Platform Services"
        app["app<br/>(Next.js Application)"]
        postgres["postgres<br/>(PostgreSQL Database)"]
        inngest["inngest<br/>(Background Jobs)"]
        migrate["migrate<br/>(Database Migration)"]
    end
    
    subgraph "External APIs"
        browseruse["BrowserUse Cloud API<br/>(api.browser-use.com)"]
        resend["Resend Email API<br/>(resend.com)"]
    end
    
    subgraph "Data Storage"
        pgdata["./data/postgres<br/>(Persistent Volume)"]
    end
    
    app --> postgres
    app --> inngest
    app --> browseruse
    app --> resend
    migrate --> postgres
    postgres --> pgdata
    inngest --> app
    
    app -.->|"Port 3000"| external[External Access]
    inngest -.->|"Port 8288"| external
    postgres -.->|"Port 5432"| external
```

Sources: [docker-compose.yaml:1-68](), [docker-compose.dev.yaml:1-107]()

### Development vs Production Configuration

The platform provides two Docker Compose configurations optimized for different use cases:

**Development** (`docker-compose.dev.yaml`):
- Hot reload with file watching
- Source code synchronization
- Development environment variables
- Debug-friendly container setup

**Production** (`docker-compose.yaml`):
- Optimized container builds
- Production environment settings
- Minimal resource footprint
- Security-hardened configuration

Sources: [docker-compose.dev.yaml:8-25](), [docker-compose.yaml:2-20]()

## Installation Process

### Quick Start Installation

The following commands will get the platform running with default settings:

```bash
# 1. Clone the repository
git clone https://github.com/browser-use/qa-use.git
cd qa-use

# 2. Configure environment variables
cp .env.example .env
# Edit .env with your API keys

# 3. Launch the platform
docker compose up
```

### Development Environment Setup

For active development with hot reload capabilities:

```bash
# Start development environment with file watching
docker compose -f docker-compose.dev.yaml up --watch
```

The `--watch` flag enables automatic container rebuilds when configuration files change.

Sources: [README.md:24-35](), [README.md:105-106]()

### Container Build Process

The platform uses a multi-stage Dockerfile for optimized builds:

```mermaid
graph LR
    subgraph "Build Stages"
        deps["deps<br/>(Dependencies)"]
        builder["builder<br/>(Build Assets)"]
        runner["runner<br/>(Production)"]
    end
    
    subgraph "Build Inputs"
        packagejson["package.json"]
        pnpmlock["pnpm-lock.yaml"]
        srccode["Source Code"]
    end
    
    subgraph "Build Outputs"
        nodemodules["node_modules"]
        buildassets["Built Assets"]
        prodimage["Production Image"]
    end
    
    packagejson --> deps
    pnpmlock --> deps
    deps --> nodemodules
    
    nodemodules --> builder
    srccode --> builder
    builder --> buildassets
    
    buildassets --> runner
    runner --> prodimage
```

Sources: [Dockerfile:1-37]()

## Service Dependencies and Startup Order

The platform services have specific dependency relationships that determine startup order:

```mermaid
graph TD
    postgres["postgres<br/>(Database Service)"]
    migrate["migrate<br/>(Schema Migration)"]
    app["app<br/>(Next.js Application)"]
    inngest["inngest<br/>(Background Processor)"]
    
    postgres -->|"health check"| migrate
    postgres -->|"service_healthy"| app
    migrate -->|"service_completed_successfully"| app
    app -->|"startup complete"| inngest
    
    postgres -.->|"Port 5432"| external["External Access"]
    app -.->|"Port 3000"| external
    inngest -.->|"Port 8288"| external
```

The startup sequence ensures:
1. PostgreSQL becomes healthy
2. Database migrations complete successfully  
3. Next.js application starts
4. Inngest connects to the application

Sources: [docker-compose.yaml:14-18](), [docker-compose.dev.yaml:39-43]()

## Initial Access and Verification

After successful deployment, the platform provides several access points:

| Service | URL | Purpose |
|---------|-----|---------|
| Main Application | http://localhost:3000 | Test suite management interface |
| Inngest Dashboard | http://localhost:8288 | Background job monitoring |
| PostgreSQL | localhost:5432 | Direct database access |

### Health Check Verification

Verify service health using the following endpoints:

```bash
# Check application health
curl http://localhost:3000

# Check database connectivity
docker compose logs postgres

# Check Inngest service
curl http://localhost:8288
```

### Database Migration Status

The `migrate` service automatically applies database schema changes during startup. Check migration status:

```bash
# View migration logs
docker compose logs migrate

# Check database schema
docker compose exec postgres psql -U postgres -d qa-use -c "\dt"
```

Sources: [README.md:44](), [docker-compose.yaml:52-64]()

## Troubleshooting Common Issues

### API Key Configuration

If tests fail to execute, verify BrowserUse API key configuration:

```bash
# Check environment variable loading
docker compose exec app printenv | grep BROWSER_USE_API_KEY

# Validate API connectivity
docker compose logs app | grep "browser-use"
```

### Database Connection Issues

For database connectivity problems:

```bash
# Check PostgreSQL service health
docker compose ps postgres

# View database logs
docker compose logs postgres

# Test database connection
docker compose exec postgres pg_isready -U postgres
```

### Container Build Failures

If containers fail to build:

```bash
# Clean build cache
docker system prune -f

# Rebuild without cache
docker compose build --no-cache

# Check build logs
docker compose logs app
```

Sources: [src/lib/api/client.ts:7-10](), [docker-compose.yaml:33-49]()

---

# Page: Core Concepts

# Core Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [drizzle/meta/0000_snapshot.json](drizzle/meta/0000_snapshot.json)
- [drizzle/meta/_journal.json](drizzle/meta/_journal.json)
- [src/lib/db/schema.ts](src/lib/db/schema.ts)

</details>



This document explains the fundamental data model and core entities that power the QA Use platform. It covers the database schema, entity relationships, and key concepts for organizing and executing AI-powered tests.

For information about the user interface components that interact with these entities, see [User Interface](#4). For details about how tests are executed using these data structures, see [AI Testing Engine](#5) and [Background Processing](#6).

## Data Model Overview

The QA Use platform is built around a hierarchical data model that organizes tests into suites and tracks their execution through dedicated run entities.

```mermaid
erDiagram
    suite {
        serial id PK
        text name
        cron_cadence cron_cadence
        timestamp last_cron_run_at
        text notifications_email_address
        timestamp created_at
    }
    
    test {
        serial id PK
        text label
        text evaluation
        integer suite_id FK
        timestamp created_at
    }
    
    test_step {
        serial id PK
        integer test_id FK
        integer order
        text description
        timestamp created_at
    }
    
    suite_run {
        serial id PK
        integer suite_id FK
        run_status status
        timestamp started_at
        timestamp finished_at
        timestamp created_at
    }
    
    test_run {
        serial id PK
        integer test_id FK
        integer suite_run_id FK
        run_status status
        text error
        text browser_use_id
        text live_url
        text public_share_url
        timestamp started_at
        timestamp finished_at
        timestamp created_at
    }
    
    test_run_step {
        serial id PK
        integer test_run_id FK
        integer step_id FK
        run_status status
    }
    
    suite ||--o{ test : "contains"
    suite ||--o{ suite_run : "executes as"
    test ||--o{ test_step : "composed of"
    test ||--o{ test_run : "runs as"
    suite_run ||--o{ test_run : "includes"
    test_run ||--o{ test_run_step : "tracks"
    test_step ||--o{ test_run_step : "executed as"
```

Sources: [src/lib/db/schema.ts:6-217]()

## Core Entities

### Test Suites

The `suite` table represents collections of related tests that can be executed together. Each suite functions as a container for organizing tests by feature, application area, or testing objective.

| Field | Type | Purpose |
|-------|------|---------|
| `id` | `serial` | Primary key identifier |
| `name` | `text` | Human-readable suite name |
| `cronCadence` | `cron_cadence` | Automated execution schedule (hourly/daily) |
| `lastCronRunAt` | `timestamp` | Tracks when automated execution last occurred |
| `notificationsEmailAddress` | `text` | Email recipient for test failure notifications |
| `createdAt` | `timestamp` | Suite creation timestamp |

The `cronCadence` field uses the `cron_cadence` enum with values `'hourly'` and `'daily'` to enable automated test execution scheduling.

Sources: [src/lib/db/schema.ts:6-31]()

### Tests

The `test` table defines individual test cases within a suite. Each test contains natural language instructions that will be converted into executable browser automation commands.

| Field | Type | Purpose |
|-------|------|---------|
| `id` | `serial` | Primary key identifier |
| `label` | `text` | Test name/description |
| `evaluation` | `text` | Success criteria in natural language |
| `suiteId` | `integer` | Foreign key to parent suite |
| `createdAt` | `timestamp` | Test creation timestamp |

The `evaluation` field contains the natural language criteria that the AI testing engine uses to determine whether a test passes or fails.

Sources: [src/lib/db/schema.ts:36-59]()

### Test Steps

The `testStep` table breaks down each test into ordered, executable actions. These steps represent the sequence of browser interactions that the AI agent will perform.

| Field | Type | Purpose |
|-------|------|---------|
| `id` | `serial` | Primary key identifier |
| `testId` | `integer` | Foreign key to parent test |
| `order` | `integer` | Execution sequence number |
| `description` | `text` | Natural language step instructions |
| `createdAt` | `timestamp` | Step creation timestamp |

The `order` field ensures steps execute in the correct sequence, while `description` contains human-readable instructions that get converted to browser automation commands.

Sources: [src/lib/db/schema.ts:61-85]()

## Execution Tracking

The platform maintains separate entities to track test execution independently from test definitions, enabling historical analysis and concurrent execution monitoring.

### Suite Runs

The `suiteRun` table represents individual execution instances of a test suite.

| Field | Type | Purpose |
|-------|------|---------|
| `id` | `serial` | Primary key identifier |
| `suiteId` | `integer` | Foreign key to executed suite |
| `status` | `run_status` | Current execution state |
| `startedAt` | `timestamp` | Execution start time |
| `finishedAt` | `timestamp` | Execution completion time |
| `createdAt` | `timestamp` | Run record creation timestamp |

Sources: [src/lib/db/schema.ts:99-126]()

### Test Runs

The `testRun` table tracks execution of individual tests within a suite run, including integration with the BrowserUse API for browser automation.

| Field | Type | Purpose |
|-------|------|---------|
| `id` | `serial` | Primary key identifier |
| `testId` | `integer` | Foreign key to executed test |
| `suiteRunId` | `integer` | Foreign key to parent suite run |
| `status` | `run_status` | Current execution state |
| `error` | `text` | Error message if execution fails |
| `browserUseId` | `text` | BrowserUse API execution identifier |
| `liveUrl` | `text` | Real-time execution monitoring URL |
| `publicShareUrl` | `text` | Shareable execution results URL |

The BrowserUse integration fields (`browserUseId`, `liveUrl`, `publicShareUrl`) connect the platform to external browser automation services.

Sources: [src/lib/db/schema.ts:128-186]()

### Test Run Steps

The `testRunStep` table provides granular execution tracking for individual test steps, enabling detailed progress monitoring and failure diagnosis.

| Field | Type | Purpose |
|-------|------|---------|
| `id` | `serial` | Primary key identifier |
| `testRunId` | `integer` | Foreign key to parent test run |
| `stepId` | `integer` | Foreign key to executed step definition |
| `status` | `run_status` | Individual step execution state |

A unique constraint on `(testRunId, stepId)` ensures each step is tracked exactly once per test run.

Sources: [src/lib/db/schema.ts:188-217]()

## Status Management

The platform uses a unified `run_status` enum to track execution progress across all run entities:

```mermaid
stateDiagram-v2
    [*] --> pending
    pending --> running
    running --> passed
    running --> failed
    passed --> [*]
    failed --> [*]
```

| Status | Description |
|--------|-------------|
| `pending` | Execution queued but not started |
| `running` | Currently executing |
| `passed` | Execution completed successfully |
| `failed` | Execution completed with errors |

This status model applies consistently to `suiteRun`, `testRun`, and `testRunStep` entities, providing uniform progress tracking across all execution levels.

Sources: [src/lib/db/schema.ts:89-97]()

## Entity Relationships and Data Flow

The following diagram illustrates how entities connect during the test execution lifecycle:

```mermaid
graph TD
    subgraph "Test Definitions"
        suite["suite"]
        test["test"]
        testStep["test_step"]
    end
    
    subgraph "Execution Tracking"
        suiteRun["suite_run"]
        testRun["test_run"]
        testRunStep["test_run_step"]
    end
    
    subgraph "External Integration"
        browserUse["BrowserUse API"]
        notifications["Email Notifications"]
    end
    
    suite -->|"contains"| test
    test -->|"composed_of"| testStep
    
    suite -->|"executes_as"| suiteRun
    test -->|"runs_as"| testRun
    testStep -->|"executed_as"| testRunStep
    
    suiteRun -->|"includes"| testRun
    testRun -->|"tracks"| testRunStep
    
    testRun -->|"browser_use_id"| browserUse
    suiteRun -->|"notifications_email_address"| notifications
    
    testRun -.->|"references"| testStep
    testRunStep -.->|"references"| testStep
```

This separation between definition and execution entities enables:

- **Historical tracking**: Multiple runs of the same test/suite without losing previous results
- **Concurrent execution**: Multiple suite runs can execute simultaneously
- **Detailed monitoring**: Step-level progress tracking within each test run
- **External integration**: Clean interfaces to BrowserUse API and notification systems

Sources: [src/lib/db/schema.ts:28-31](), [src/lib/db/schema.ts:52-59](), [src/lib/db/schema.ts:80-85](), [src/lib/db/schema.ts:120-126](), [src/lib/db/schema.ts:174-186](), [src/lib/db/schema.ts:208-217]()

---

# Page: User Interface

# User Interface

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/app/layout.tsx](src/app/layout.tsx)
- [src/app/page.tsx](src/app/page.tsx)

</details>



## Purpose and Scope

This document covers the web application frontend of the QA Use platform, including the React components, page structure, navigation patterns, and user interaction flows. The UI is built using Next.js with React components and provides interfaces for managing test suites, creating tests, and monitoring execution.

For information about the underlying data structures and business logic, see [Core Concepts](#3). For details about form handling and data mutations, see [Server Actions](#8). For information about reusable UI components across the application, see [Shared Components](#4.4).

## UI Architecture Overview

The QA Use platform uses a Next.js application structure with React components organized around the core entities of suites, tests, and test runs.

### Frontend Technology Stack

```mermaid
graph TB
    subgraph "Frontend Stack"
        NEXTJS["Next.js Framework"]
        REACT["React Components"]
        TAILWIND["Tailwind CSS"]
        SHADCN["shadcn/ui Components"]
    end
    
    subgraph "Core UI Pages"
        DASHBOARD["page.tsx<br/>Main Dashboard"]
        SUITE_DETAIL["suite/[id]/page.tsx<br/>Suite Details"]
        TEST_DETAIL["test/[id]/page.tsx<br/>Test Management"]
        RUN_DETAIL["run/[id]/page.tsx<br/>Execution Views"]
    end
    
    subgraph "Shared Components"
        PAGE_HEADER["PageHeader"]
        SECTION_HEADER["SectionHeader"]
        FORM_COMPONENTS["Input, Button, Dialog"]
        TABLE_COMPONENTS["Table, TableRow, TableCell"]
    end
    
    NEXTJS --> DASHBOARD
    NEXTJS --> SUITE_DETAIL
    NEXTJS --> TEST_DETAIL
    NEXTJS --> RUN_DETAIL
    
    REACT --> PAGE_HEADER
    REACT --> SECTION_HEADER
    REACT --> FORM_COMPONENTS
    REACT --> TABLE_COMPONENTS
    
    TAILWIND --> REACT
    SHADCN --> FORM_COMPONENTS
    SHADCN --> TABLE_COMPONENTS
```

**Sources:** [src/app/layout.tsx:1-36](), [src/app/page.tsx:1-120]()

## Application Layout Structure

The application uses a centralized layout pattern with consistent styling and responsive design.

### Root Layout Configuration

```mermaid
graph TD
    subgraph "RootLayout Component"
        HTML["html element<br/>lang='en'"]
        BODY["body element<br/>Geist fonts + bg-gray-50"]
        CONTAINER["div.min-h-screen"]
        CONTENT["div.max-w-6xl.mx-auto.px-3.py-12.md:py-16"]
    end
    
    subgraph "Font Configuration"
        GEIST_SANS["Geist Sans Font<br/>--font-geist-sans"]
        GEIST_MONO["Geist Mono Font<br/>--font-geist-mono"]
    end
    
    subgraph "Global Styles"
        GLOBALS["globals.css<br/>Tailwind CSS imports"]
        ANTIALIASED["antialiased class<br/>Font smoothing"]
    end
    
    HTML --> BODY
    BODY --> CONTAINER
    CONTAINER --> CONTENT
    CONTENT --> "children pages"
    
    GEIST_SANS --> BODY
    GEIST_MONO --> BODY
    GLOBALS --> BODY
    ANTIALIASED --> BODY
```

**Sources:** [src/app/layout.tsx:22-36](), [src/app/layout.tsx:7-15]()

The layout establishes a consistent container with maximum width of `6xl` (1152px) and responsive padding that creates the main content area for all pages.

## Main Dashboard Interface

The primary interface is implemented in the root page component, displaying all test suites in a tabular format with creation and navigation capabilities.

### Dashboard Component Structure

```mermaid
graph TD
    subgraph "Page Component"
        LOADER["loader() function<br/>Data fetching"]
        PAGE_COMP["Page() component<br/>Main render function"]
    end
    
    subgraph "UI Components"
        PAGE_HEADER["PageHeader<br/>title='All Suites'<br/>subtitle='QA Use'"]
        SECTION_HEADER["SectionHeader<br/>title='Test Suites'"]
        CREATE_DIALOG["CreateSuiteDialog<br/>Suite creation form"]
        SUITES_TABLE["Table component<br/>Suite listing"]
    end
    
    subgraph "Table Structure"
        TABLE_HEADER["TableHeader<br/>Name, Tests, Created, Cron, Last Run"]
        TABLE_BODY["TableBody<br/>Dynamic suite rows"]
        TABLE_ROW["TableRow per suite<br/>Suite data + View link"]
    end
    
    subgraph "Actions"
        CREATE_SUITE_ACTION["createSuiteAction<br/>Server action"]
        VIEW_LINK["Link to /suite/[id]<br/>Navigation"]
    end
    
    LOADER --> PAGE_COMP
    PAGE_COMP --> PAGE_HEADER
    PAGE_COMP --> SECTION_HEADER
    SECTION_HEADER --> CREATE_DIALOG
    PAGE_COMP --> SUITES_TABLE
    
    SUITES_TABLE --> TABLE_HEADER
    SUITES_TABLE --> TABLE_BODY
    TABLE_BODY --> TABLE_ROW
    
    CREATE_DIALOG --> CREATE_SUITE_ACTION
    TABLE_ROW --> VIEW_LINK
```

**Sources:** [src/app/page.tsx:25-76](), [src/app/page.tsx:78-108]()

### Suite Table Data Display

The main table displays suite information with the following columns:

| Column | Data Source | Formatting |
|--------|-------------|------------|
| Name | `suite.name` | Plain text display |
| Tests | `suite.tests.length` | Count with "tests" suffix |
| Created | `suite.createdAt` | Formatted via `formatDate()` |
| Cron | `suite.cronCadence` | Mapped via `getCronLabel()` |
| Last Run | `suite.lastCronRunAt` | Formatted date or "Never" |
| Actions | Navigation | Link to `/suite/${suite.id}` |

**Sources:** [src/app/page.tsx:41-73](), [src/app/page.tsx:110-119]()

### Suite Creation Dialog

The creation interface uses a modal dialog pattern with form submission:

```mermaid
graph LR
    subgraph "CreateSuiteDialog"
        TRIGGER["Button<br/>'Create Suite'<br/>Plus icon"]
        DIALOG["Dialog component<br/>Modal overlay"]
        FORM["form element<br/>action=createSuiteAction"]
        INPUT["Input field<br/>name='name'<br/>required"]
        SUBMIT["Submit Button<br/>'Create'"]
    end
    
    TRIGGER --> DIALOG
    DIALOG --> FORM
    FORM --> INPUT
    FORM --> SUBMIT
    SUBMIT --> "Server Action"
```

**Sources:** [src/app/page.tsx:78-108]()

## Dynamic Loading and Server-Side Rendering

The dashboard implements dynamic server-side rendering with data loading:

- `export const dynamic = 'force-dynamic'` ensures fresh data on each request [src/app/page.tsx:23]()
- Async `loader()` function fetches suite data before rendering [src/app/page.tsx:26]()
- Server actions handle form submissions without client-side JavaScript requirements

## Navigation Patterns

The UI implements navigation through Next.js `Link` components:

- Main dashboard accessible at root path `/`
- Suite detail pages at `/suite/[id]` [src/app/page.tsx:68]()
- External link to GitHub repository in page header [src/app/page.tsx:33]()

## Responsive Design Considerations

The layout uses Tailwind CSS responsive utilities:

- Container padding: `px-3` base, responsive on larger screens
- Vertical spacing: `py-12 md:py-16` with breakpoint variation
- Maximum width constraint: `max-w-6xl` with center alignment

**Sources:** [src/app/layout.tsx:31]()

---

# Page: Suite Management

# Suite Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/app/suite/[suiteId]/loader.ts](src/app/suite/[suiteId]/loader.ts)
- [src/app/suite/[suiteId]/page.tsx](src/app/suite/[suiteId]/page.tsx)
- [src/components/shared/SectionHeader.tsx](src/components/shared/SectionHeader.tsx)
- [src/components/suite/HistoryTab.tsx](src/components/suite/HistoryTab.tsx)
- [src/components/suite/TestsTab.tsx](src/components/suite/TestsTab.tsx)
- [src/components/suite/run/SuiteRunDetails.tsx](src/components/suite/run/SuiteRunDetails.tsx)

</details>



This document covers the user interface components and pages for creating, viewing, and managing test suites within the QA Use platform. It focuses on the suite-level management interfaces, including the main suite details page, navigation tabs, and suite configuration options.

For information about managing individual tests within a suite, see [Test Management](#4.2). For monitoring test execution and viewing results, see [Test Execution Views](#4.3).

## Suite Details Page

The primary interface for suite management is implemented as a Next.js dynamic route at `/suite/[suiteId]`. This page provides a comprehensive view of a test suite including its configuration, contained tests, and execution history.

### Page Structure and Data Loading

The suite details page follows Next.js App Router conventions with server-side data loading and client-side interactions:

```mermaid
graph TD
    URL["/suite/[suiteId]"] --> PAGE["SuitePage Component"]
    PAGE --> LOADER["loader(suiteId)"]
    LOADER --> DB[("PostgreSQL Database")]
    LOADER --> SUITE_DATA["TSuite Type"]
    
    SUITE_DATA --> SUITE_DETAILS["SuiteDetails Component"]
    SUITE_DATA --> TESTS_TAB["TestsTab Component"] 
    SUITE_DATA --> HISTORY_TAB["HistoryTab Component"]
    
    PAGE --> SERVER_ACTIONS["Server Actions"]
    SERVER_ACTIONS --> RUN_SUITE["runSuiteAction"]
    SERVER_ACTIONS --> DELETE_SUITE["deleteSuiteAction"]
    SERVER_ACTIONS --> CREATE_TEST["createTestAction"]
    SERVER_ACTIONS --> SET_CRON["setCronCadenceAction"]
    SERVER_ACTIONS --> SET_EMAIL["setNotificationsEmailAddressAction"]
```

The data loader retrieves comprehensive suite information including related tests with their steps and execution history ordered by creation date.

Sources: [src/app/suite/[suiteId]/page.tsx:1-45](), [src/app/suite/[suiteId]/loader.ts:1-38]()

### Tab-Based Navigation

The suite interface uses a tabbed layout to organize different aspects of suite management:

| Tab | Purpose | Key Components |
|-----|---------|----------------|
| Tests | View and manage tests within the suite | `TestsTab`, test listing table |
| History | View suite execution history | `HistoryTab`, run status tracking |

#### Tests Tab

The Tests tab displays all tests contained within the suite in a tabular format:

```mermaid
graph LR
    TESTS_TAB["TestsTab Component"] --> TABLE["Table Component"]
    TABLE --> TEST_ROW["Test Row"]
    TEST_ROW --> TEST_LABEL["test.label"]
    TEST_ROW --> CREATED_AT["test.createdAt"]
    TEST_ROW --> VIEW_LINK["Link to /suite/suiteId/test/testId"]
    
    SUITE_DATA["TSuite.tests[]"] --> TESTS_TAB
```

Sources: [src/components/suite/TestsTab.tsx:1-41]()

#### History Tab

The History tab shows the execution history for the suite with run status indicators:

```mermaid
graph LR
    HISTORY_TAB["HistoryTab Component"] --> TABLE["Table Component"]
    TABLE --> RUN_ROW["Suite Run Row"]
    RUN_ROW --> RUN_STATUS["RunStatusBadge"]
    RUN_ROW --> RUN_ID["run.id"]
    RUN_ROW --> RUN_DATE["run.createdAt"]
    RUN_ROW --> VIEW_LINK["Link to /suite/suiteId/run/runId"]
    
    SUITE_DATA["TSuite.runs[]"] --> HISTORY_TAB
```

Sources: [src/components/suite/HistoryTab.tsx:1-46]()

## Suite Run Details Interface

When viewing individual suite runs, the platform provides detailed execution information through the `SuiteRunDetails` component:

```mermaid
graph TD
    SUITE_RUN_URL["/suite/suiteId/run/suiteRunId"] --> SUITE_RUN_DETAILS["SuiteRunDetails Component"]
    
    SUITE_RUN_DETAILS --> PAGE_HEADER["PageHeader"]
    PAGE_HEADER --> TITLE["Suite Run #runId"]
    PAGE_HEADER --> SUBTITLE["suite.name"]
    PAGE_HEADER --> BACK_LINK["Back to Suite"]
    
    SUITE_RUN_DETAILS --> SECTION_HEADER["SectionHeader"]
    SECTION_HEADER --> TEST_STATS["nOfPassingTests, nOfFailedTests"]
    SECTION_HEADER --> STATUS_BADGE["RunStatusBadge"]
    
    SUITE_RUN_DETAILS --> TEST_RUNS_TABLE["Test Runs Table"]
    TEST_RUNS_TABLE --> TEST_RUN_ROW["Test Run Row"]
    TEST_RUN_ROW --> STATUS_ICON["RunStatusIcon"]
    TEST_RUN_ROW --> TEST_LABEL["testRun.test.label"]
    TEST_RUN_ROW --> CREATED_AT["testRun.createdAt"]
    TEST_RUN_ROW --> VIEW_TEST_RUN["Link to Test Run Details"]
    
    SUITE_RUN_DETAILS --> POLLING["Polling Component"]
```

The component automatically calculates test execution statistics and provides real-time updates through the `Polling` component when runs are in progress.

Sources: [src/components/suite/run/SuiteRunDetails.tsx:1-77]()

## Suite Actions and Server Integration

The suite management interface integrates with Next.js server actions to handle suite-level operations:

### Available Actions

| Action | Function | Purpose |
|--------|----------|---------|
| Run Suite | `runSuiteAction` | Triggers execution of all tests in the suite |
| Delete Suite | `deleteSuiteAction` | Removes the suite and all associated data |
| Create Test | `createTestAction` | Adds a new test to the suite |
| Set Cron Cadence | `setCronCadenceAction` | Configures automatic suite execution schedule |
| Set Notifications Email | `setNotificationsEmailAddressAction` | Configures email notifications for suite results |

### Action Binding Pattern

The page uses function binding to create suite-specific action handlers:

```mermaid
graph LR
    SERVER_ACTIONS["Server Actions Module"] --> BOUND_ACTIONS["Bound Actions"]
    BOUND_ACTIONS --> RUN_SUITE["runSuite(suiteIdNum)"]
    BOUND_ACTIONS --> DELETE_SUITE["deleteSuite(suiteIdNum)"]
    BOUND_ACTIONS --> CREATE_TEST["createTest(suiteIdNum)"]
    BOUND_ACTIONS --> SET_CRON["setCronCadence(suiteIdNum)"]
    BOUND_ACTIONS --> SET_EMAIL["setNotificationsEmailAddress(suiteIdNum)"]
    
    BOUND_ACTIONS --> SUITE_DETAILS["SuiteDetails Component Props"]
```

This pattern ensures type safety and eliminates the need to pass suite IDs through form data.

Sources: [src/app/suite/[suiteId]/page.tsx:29-42]()

## Real-Time Updates and Polling

Suite management interfaces implement real-time updates for active operations:

- **Suite Run Monitoring**: The `SuiteRunDetails` component includes a `Polling` component that refreshes data when `run.status` is `'running'` or `'pending'`
- **Status Indicators**: Components use `RunStatusBadge` and `RunStatusIcon` to provide visual feedback on execution states
- **Dynamic Content**: Date formatting and status calculations are performed client-side to handle timezone differences

Sources: [src/components/suite/run/SuiteRunDetails.tsx:74-75](), [src/components/shared/SectionHeader.tsx:1-31]()

---

# Page: Test Management

# Test Management

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/app/suite/[suiteId]/run/[suiteRunId]/page.tsx](src/app/suite/[suiteId]/run/[suiteRunId]/page.tsx)
- [src/app/suite/[suiteId]/test/[testId]/edit/page.tsx](src/app/suite/[suiteId]/test/[testId]/edit/page.tsx)
- [src/app/suite/[suiteId]/test/[testId]/page.tsx](src/app/suite/[suiteId]/test/[testId]/page.tsx)
- [src/app/suite/[suiteId]/test/[testId]/run/[testRunId]/page.tsx](src/app/suite/[suiteId]/test/[testId]/run/[testRunId]/page.tsx)
- [src/components/test/TestEditor.tsx](src/components/test/TestEditor.tsx)

</details>



This document covers the user interface components and workflows for creating, editing, and executing individual tests within the QA Use platform. Test management focuses on the granular level of individual test cases, their steps, and execution monitoring.

For information about managing collections of tests, see [Suite Management](#4.1). For details about viewing test execution results and monitoring runs, see [Test Execution Views](#4.3).

## Purpose and Scope

The test management system enables users to:
- Create and edit individual test cases with natural language descriptions
- Manage test steps in a sequential, ordered manner
- Execute individual tests and monitor their progress
- View detailed test run results and execution history

## Test Editor Interface

The primary interface for test management is the `TestEditor` component, which provides a comprehensive form-based editor for test creation and modification.

### TestEditor Component Architecture

```mermaid
graph TD
    TestEditor["TestEditor"] --> State["State Management"]
    TestEditor --> UI["UI Components"]
    TestEditor --> Actions["Server Actions"]
    
    State --> Reducer["reducer()"]
    State --> InitialState["getInitialState()"]
    
    UI --> Input["Input (test label)"]
    UI --> Textarea["Textarea (steps & evaluation)"]
    UI --> Button["Button (save/cancel/delete)"]
    
    Actions --> SaveTest["saveTest server action"]
    
    Reducer --> SetLabel["setLabel"]
    Reducer --> SetEvaluation["setEvaluation"] 
    Reducer --> CreateStep["createStep"]
    Reducer --> ChangeDescription["changeStepDescription"]
    Reducer --> DeleteStep["deleteStep"]
    
    InitialState --> ExistingSteps["Map existing steps"]
    InitialState --> DefaultStep["Add default step if empty"]
```

Sources: [src/components/test/TestEditor.tsx:1-230]()

### Test Data Model

The test editor manages a complex state structure that tracks both new and existing test steps:

```mermaid
graph LR
    subgraph "Test State"
        Label["label: string"]
        Evaluation["evaluation: string"]
        NextStepId["nextStepId: number"]
        Steps["steps: Step[]"]
    end
    
    subgraph "Step Types"
        NewStep["New Step"] --> NewId["id: string (vm:n)"]
        NewStep --> NewDesc["description: string"]
        NewStep --> NewStatus["status: 'new'"]
        
        ExistingStep["Existing Step"] --> ExistingId["id: string (existing:n)"]
        ExistingStep --> ExistingDesc["description: string"]
        ExistingStep --> ExistingStatus["status: 'existing'"]
        ExistingStep --> SourceId["sourceId: number"]
        ExistingStep --> Deleted["deleted: boolean"]
    end
    
    Steps --> NewStep
    Steps --> ExistingStep
```

Sources: [src/components/test/TestEditor.tsx:15-41]()

## Test Management Workflow

### Test Creation and Editing Flow

```mermaid
sequenceDiagram
    participant User
    participant TestEditor
    participant Reducer
    participant SaveTest
    participant Database
    
    User->>TestEditor: "Load test for editing"
    TestEditor->>TestEditor: "getInitialState(test)"
    TestEditor->>User: "Render form with current data"
    
    User->>TestEditor: "Modify test label"
    TestEditor->>Reducer: "dispatch({type: 'setLabel'})"
    Reducer->>TestEditor: "Return updated state"
    
    User->>TestEditor: "Add new step"
    TestEditor->>Reducer: "dispatch({type: 'createStep'})"
    Reducer->>TestEditor: "Add step with vm:id"
    
    User->>TestEditor: "Delete existing step"
    TestEditor->>Reducer: "dispatch({type: 'deleteStep'})"
    Reducer->>TestEditor: "Mark step as deleted"
    
    User->>TestEditor: "Save test"
    TestEditor->>SaveTest: "saveTest(testId, state)"
    SaveTest->>Database: "Update test and steps"
    Database->>User: "Redirect to test details"
```

Sources: [src/components/test/TestEditor.tsx:66-125](), [src/app/suite/[suiteId]/test/[testId]/edit/actions.ts]()

### Test Execution Workflow

```mermaid
graph TD
    TestDetails["TestDetails Component"] --> RunButton["Run Test Button"]
    RunButton --> RunTestAction["runTestAction"]
    RunTestAction --> InngestEvent["Trigger test execution"]
    InngestEvent --> TestRun["Create TestRun record"]
    TestRun --> BrowserUse["Execute via BrowserUse API"]
    BrowserUse --> Results["Update test results"]
    Results --> TestRunDetails["TestRunDetails view"]
```

Sources: [src/app/suite/[suiteId]/test/[testId]/page.tsx:1-29]()

## Page Structure and Routes

The test management system spans several Next.js pages with specific responsibilities:

| Route | Component | Purpose |
|-------|-----------|---------|
| `/suite/[suiteId]/test/[testId]` | `TestDetails` | View test details and trigger execution |
| `/suite/[suiteId]/test/[testId]/edit` | `TestEditor` | Edit test metadata and steps |
| `/suite/[suiteId]/test/[testId]/run/[testRunId]` | `TestRunDetails` | View specific test run results |

Sources: [src/app/suite/[suiteId]/test/[testId]/page.tsx:1-29](), [src/app/suite/[suiteId]/test/[testId]/edit/page.tsx:1-19](), [src/app/suite/[suiteId]/test/[testId]/run/[testRunId]/page.tsx:1-26]()

## State Management Pattern

The `TestEditor` uses a React `useReducer` pattern for managing complex state transitions:

### Reducer Actions

| Action Type | Payload | Effect |
|-------------|---------|--------|
| `setLabel` | `label: string` | Updates test label |
| `setEvaluation` | `evaluation: string` | Updates test evaluation criteria |
| `createStep` | None | Adds new step with generated ID |
| `changeStepDescription` | `stepId: string, description: string` | Updates step description |
| `deleteStep` | `stepId: string` | Marks step as deleted or removes if new |

### Step ID Management

The editor maintains different ID formats for tracking step state:
- New steps: `vm:${nextStepId}` format for virtual IDs
- Existing steps: `existing:${sourceId}` format for database-backed steps

Sources: [src/components/test/TestEditor.tsx:66-125]()

## Form Validation and Submission

The test editor implements client-side validation and server-side persistence:

```mermaid
graph LR
    FormState["Test Form State"] --> Validation["Client Validation"]
    Validation --> SaveButton["Save Button State"]
    
    Validation --> StepsCheck["steps.length > 0"]
    StepsCheck --> EnableSave["Enable/Disable Save"]
    
    SaveButton --> ServerAction["saveTest server action"]
    ServerAction --> Database["Persist to PostgreSQL"]
    Database --> Redirect["Redirect to test details"]
```

The save button is disabled when `state.steps.length === 0`, preventing submission of tests without steps.

Sources: [src/components/test/TestEditor.tsx:152-157](), [src/components/test/TestEditor.tsx:220-225]()

## Integration Points

The test management system integrates with several other platform components:

- **Server Actions**: Uses `saveTest` for persistence operations
- **Navigation**: Links back to suite views and test details
- **Execution Engine**: Triggers test runs through `runTestAction`
- **Results Viewing**: Connects to test run detail pages for execution monitoring

Sources: [src/app/suite/[suiteId]/test/[testId]/edit/actions.ts](), [src/app/suite/[suiteId]/test/[testId]/actions.ts]()

---

# Page: Test Execution Views

# Test Execution Views

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/app/suite/[suiteId]/test/[testId]/run/[testRunId]/loader.ts](src/app/suite/[suiteId]/test/[testId]/run/[testRunId]/loader.ts)
- [src/components/Polling.tsx](src/components/Polling.tsx)
- [src/components/test/run/TestRunDetails.tsx](src/components/test/run/TestRunDetails.tsx)

</details>



This document covers the user interface components and views for monitoring test execution and viewing test run results. These views provide real-time visibility into test progress, step-by-step execution status, and live browser previews during AI agent execution.

For information about creating and managing tests, see [Test Management](#4.2). For details about the underlying test execution engine, see [AI Testing Engine](#5).

## Overview

The test execution views consist of the primary `TestRunDetails` component that displays comprehensive information about a specific test run, including step-by-step progress, live browser preview, and final results. The interface supports real-time updates through polling mechanisms and provides direct access to external agent execution views.

Sources: [src/components/test/run/TestRunDetails.tsx:1-161]()

## Test Run Details Interface

The `TestRunDetails` component serves as the main interface for viewing test execution details. It presents information in a two-column layout with test steps on the left and live preview on the right.

### Component Structure

```mermaid
graph TD
    TestRunDetails["TestRunDetails"] --> PageHeader["PageHeader"]
    TestRunDetails --> StepsSection["Steps Section"]
    TestRunDetails --> ResultSection["Result Section"] 
    TestRunDetails --> LivePreviewSection["Live Preview Section"]
    TestRunDetails --> PollingComponent["Polling"]
    
    StepsSection --> Table["Table"]
    Table --> TableRow["TableRow (per step)"]
    TableRow --> RunStatusIcon["RunStatusIcon"]
    
    LivePreviewSection --> LivePreview["LivePreview"]
    LivePreview --> TestRunPlaceholder["TestRunPlaceholder"]
    LivePreview --> TestFinishedPlaceholder["TestFinishedPlaceholder"]
    LivePreview --> IFrame["iframe (when running)"]
    
    PageHeader --> RunStatusBadge["RunStatusBadge"]
    ResultSection --> RunStatusBadge
```

Sources: [src/components/test/run/TestRunDetails.tsx:16-106]()

### Test Steps Display

The steps section displays each test step in a table format with the following columns:

| Column | Content | Component |
|--------|---------|-----------|
| Status | Visual status indicator | `RunStatusIcon` |
| # | Step order number | Direct display |
| Description | Step description text | Direct display |

The table includes both individual test steps and the final evaluation criteria as the last row. Each step shows its current execution status through standardized status icons.

Sources: [src/components/test/run/TestRunDetails.tsx:53-80]()

### Navigation and Actions

The interface provides contextual navigation and actions through the `PageHeader`:

- **Back Navigation**: Returns to either the suite run (if part of suite execution) or individual test page
- **View Test Action**: Links to the test definition page
- **View Agent Action**: Links to the BrowserUse agent execution page (when available)

```mermaid
graph LR
    TestRunPage["Test Run Details"] --> |"Back (suiteRunId exists)"| SuiteRunPage["Suite Run"]
    TestRunPage --> |"Back (no suiteRunId)"| TestPage["Test Details"]
    TestRunPage --> |"View Test"| TestPage
    TestRunPage --> |"View Agent"| BrowserUseAgent["BrowserUse Agent"]
```

Sources: [src/components/test/run/TestRunDetails.tsx:19-35]()

## Live Preview System

The `LivePreview` component provides real-time visibility into test execution through an embedded iframe that displays the actual browser session being controlled by the AI agent.

### Preview States

The live preview system handles three distinct states:

```mermaid
stateDiagram-v2
    [*] --> Pending
    Pending --> Running
    Running --> Completed
    Running --> Failed
    Completed --> [*]
    Failed --> [*]
    
    Pending : TestRunPlaceholder
    Running : iframe with liveUrl
    Completed : TestFinishedPlaceholder
    Failed : TestFinishedPlaceholder
```

### State-Specific Rendering

| Status | Display | Component | Description |
|--------|---------|-----------|-------------|
| `pending` | Placeholder with monitor icon | `TestRunPlaceholder` | Shows "Preview will appear when test is running" |
| `running` | Live iframe | Direct iframe element | Displays real-time browser session |
| `passed`/`failed` | Completion placeholder | `TestFinishedPlaceholder` | Shows completion status with optional agent link |

The iframe uses the `liveUrl` from the test run data and includes fullscreen permissions for optimal viewing.

Sources: [src/components/test/run/TestRunDetails.tsx:108-160]()

## Real-time Status Updates

The interface implements automatic polling to provide real-time updates during test execution through the `Polling` component and `useTaskPolling` hook.

### Polling Mechanism

```mermaid
sequenceDiagram
    participant UI as "TestRunDetails"
    participant Polling as "Polling Component"
    participant Hook as "useTaskPolling"
    participant Router as "Next.js Router"
    participant Server as "Server"
    
    UI->>Polling: poll={status === 'running' || status === 'pending'}
    Polling->>Hook: useTaskPolling({run: poll})
    
    loop Every 2 seconds (when running)
        Hook->>Router: router.refresh()
        Router->>Server: Fetch updated data
        Server->>Router: Return current test status
        Router->>UI: Re-render with new data
    end
    
    Note over Hook: Stops polling when status changes to 'passed' or 'failed'
```

### Polling Configuration

The polling system automatically:
- Starts when test status is `running` or `pending`
- Refreshes every 2 seconds by default
- Stops when test reaches a terminal state (`passed`, `failed`)
- Uses `router.refresh()` to trigger full page re-render with fresh data

Sources: [src/components/test/run/TestRunDetails.tsx:103](), [src/components/Polling.tsx:1-43]()

## Data Loading and Types

The test run views rely on the `loader` function to fetch comprehensive test run data including all related entities.

### Data Structure

```mermaid
erDiagram
    TTestRun {
        id number
        status TRunStatus
        error string
        publicShareUrl string
        liveUrl string
        suiteRunId number
    }
    
    Test {
        id number
        label string
        evaluation string
        suiteId number
        createdAt Date
    }
    
    TestRunStep {
        id number
        status TRunStatus
    }
    
    TestStep {
        order number
        description string
    }
    
    TTestRun ||--|| Test : "belongs to"
    TTestRun ||--o{ TestRunStep : "has many"
    TestRunStep ||--|| TestStep : "references"
```

The `loader` function uses Drizzle ORM with nested relations to fetch all required data in a single query, including test steps and their execution status.

Sources: [src/app/suite/[suiteId]/test/[testId]/run/[testRunId]/loader.ts:1-30]()

## Result Display

The results section provides immediate feedback on test execution outcomes:

- **Success State**: Displays "Test passed" message in green text
- **Failure State**: Shows error message in red text with full error details
- **Status Badge**: Visual indicator showing current execution status

The result section is always visible regardless of test status, providing consistent feedback throughout the execution lifecycle.

Sources: [src/components/test/run/TestRunDetails.tsx:82-91]()

---

# Page: Shared Components

# Shared Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [pnpm-lock.yaml](pnpm-lock.yaml)
- [src/app/api/inngest/route.ts](src/app/api/inngest/route.ts)
- [src/app/suite/[suiteId]/loader.ts](src/app/suite/[suiteId]/loader.ts)
- [src/app/suite/[suiteId]/test/[testId]/actions.ts](src/app/suite/[suiteId]/test/[testId]/actions.ts)
- [src/components/shared/PageHeader.tsx](src/components/shared/PageHeader.tsx)
- [src/components/shared/SectionHeader.tsx](src/components/shared/SectionHeader.tsx)
- [src/components/test/TestDetails.tsx](src/components/test/TestDetails.tsx)

</details>



This page documents the reusable UI components and utilities that provide consistent user interface elements and functionality across the QA Use platform. These components form the foundation of the application's design system and are used throughout the test suite management interface.

For information about specific page components that consume these shared elements, see [Suite Management](#4.1), [Test Management](#4.2), and [Test Execution Views](#4.3).

## Overview

The shared components are organized into several categories that support different aspects of the user interface:

- **Layout Components**: Provide consistent page and section structure
- **UI Components**: Form controls, data display, and interactive elements
- **Status Components**: Display execution states and run information
- **Utility Functions**: Helper functions for formatting and common operations

## Layout Components

### PageHeader Component

The `PageHeader` component provides a consistent page-level header structure used across all major pages in the application.

```mermaid
graph TB
    subgraph "PageHeader Structure"
        PH[PageHeader]
        BL[back_link]
        TI[title]
        ST[subtitle]
        AC[actions]
    end
    
    subgraph "Usage Examples"
        TD[TestDetails]
        SD[SuiteDetails]
        ED[EditPages]
    end
    
    PH --> BL
    PH --> TI
    PH --> ST
    PH --> AC
    
    TD --> PH
    SD --> PH
    ED --> PH
```

The component accepts the following properties:
- `back`: Navigation link with href and label
- `title`: Primary page heading
- `subtitle`: Optional secondary information
- `actions`: Array of action links

Sources: [src/components/shared/PageHeader.tsx:4-49]()

### SectionHeader Component

The `SectionHeader` component provides section-level organization within pages, typically used to group related content with associated actions.

```mermaid
graph LR
    subgraph "SectionHeader Composition"
        SH[SectionHeader]
        SHT[SectionHeaderTitle]
        SHS[SectionHeaderSubtitle]
        ACT[actions_array]
    end
    
    subgraph "Action Types"
        BTN[Button_Components]
        FORM[Form_Elements]
        LINK[Link_Components]
    end
    
    SH --> SHT
    SH --> SHS
    SH --> ACT
    ACT --> BTN
    ACT --> FORM
    ACT --> LINK
```

The component supports:
- Primary section title with consistent styling
- Optional subtitle for additional context
- Flexible actions array for buttons, forms, and links

Sources: [src/components/shared/SectionHeader.tsx:4-31]()

## Component Usage Patterns

### TestDetails Component Integration

The `TestDetails` component demonstrates how shared components are composed to create complex page layouts:

```mermaid
graph TD
    subgraph "TestDetails Page Structure"
        TD[TestDetails]
        PH[PageHeader]
        SH1[SectionHeader_Steps]
        SH2[SectionHeader_Runs]
        TBL1[Table_Steps]
        TBL2[Table_Runs]
        POL[Polling]
    end
    
    subgraph "Shared Components Used"
        SHRD[shared/PageHeader]
        SHRD2[shared/SectionHeader]
        SHRD3[shared/RunStatusIcon]
        SHRD4[shared/utils_formatDate]
    end
    
    TD --> PH
    TD --> SH1
    TD --> SH2
    TD --> TBL1
    TD --> TBL2
    TD --> POL
    
    PH --> SHRD
    SH1 --> SHRD2
    SH2 --> SHRD2
    TBL2 --> SHRD3
    TBL2 --> SHRD4
```

The integration shows:
- `PageHeader` for page-level navigation and title
- Multiple `SectionHeader` instances for "Steps" and "Runs" sections
- `RunStatusIcon` within table cells for status display
- `formatDate` utility for consistent date formatting

Sources: [src/components/test/TestDetails.tsx:1-150]()

## UI Component Library

### Table Components

The application uses a comprehensive table component system for data display:

| Component | Purpose | Usage |
|-----------|---------|-------|
| `Table` | Container wrapper | Data tables throughout the app |
| `TableHeader` | Column headers | Defines table structure |
| `TableBody` | Content rows | Contains data rows |
| `TableRow` | Individual row | Wraps table cells |
| `TableCell` | Cell content | Individual data points |
| `TableHead` | Header cell | Column definitions |
| `TableFooter` | Summary rows | Additional information |

Sources: [src/components/test/TestDetails.tsx:6]()

### Button Components

The `Button` component provides consistent interactive elements with support for:
- Variant styling (`outline`, `destructive`, etc.)
- Size options (`icon`, standard)
- Icon integration with Lucide React icons

Sources: [src/components/test/TestDetails.tsx:13]()

## Status and Utility Components

### RunStatusIcon Component

The `RunStatusIcon` component provides visual indicators for test execution states:

```mermaid
graph LR
    subgraph "Status Display System"
        RSI[RunStatusIcon]
        STAT[status_prop]
        ICON[visual_indicator]
    end
    
    subgraph "Status Types"
        PEND[pending]
        RUN[running]
        SUCC[success]
        FAIL[failed]
    end
    
    RSI --> STAT
    STAT --> ICON
    STAT --> PEND
    STAT --> RUN
    STAT --> SUCC
    STAT --> FAIL
```

The component is used throughout the application to display:
- Test run status in tables
- Suite execution progress
- Individual step completion states

Sources: [src/components/test/TestDetails.tsx:10]()

### Utility Functions

#### formatDate Function

The `formatDate` utility provides consistent date formatting across the application, handling:
- Timestamp conversion
- Locale-specific formatting
- Hydration safety with `suppressHydrationWarning`

Sources: [src/components/test/TestDetails.tsx:12](), [src/components/test/TestDetails.tsx:131]()

## Component Architecture

### Reusability Strategy

The shared component architecture follows these principles:

```mermaid
graph TB
    subgraph "Component Hierarchy"
        SHARED[shared_components]
        UI[ui_components]
        PAGE[page_components]
        LAYOUT[layout_components]
    end
    
    subgraph "Dependency Flow"
        PAGE --> SHARED
        PAGE --> UI
        SHARED --> UI
        LAYOUT --> SHARED
    end
    
    subgraph "Examples"
        TD[TestDetails]
        SD[SuiteDetails]
        PH[PageHeader]
        SH[SectionHeader]
        BTN[Button]
        TBL[Table]
    end
    
    TD --> PH
    TD --> SH
    SD --> PH
    SD --> SH
    PH --> BTN
    SH --> BTN
    TD --> TBL
    SD --> TBL
```

### Import Patterns

Components follow consistent import patterns:
- Shared components imported from `../shared/ComponentName`
- UI components imported from `../ui/componentName`
- External libraries (Lucide icons, etc.) imported directly

### Composition Approach

The platform uses a composition-over-inheritance approach where:
- Complex components combine multiple shared components
- Props are passed down to configure behavior
- Actions are handled via form submissions and server actions

Sources: [src/components/test/TestDetails.tsx:8-13]()

## Integration with Server Actions

Shared components integrate seamlessly with the application's server action pattern:

```mermaid
graph LR
    subgraph "Component Layer"
        FORM[form_elements]
        BTN[Button]
        SH[SectionHeader]
    end
    
    subgraph "Server Layer"
        SA[server_actions]
        DB[database_operations]
        REVAL[revalidatePath]
    end
    
    FORM --> SA
    BTN --> SA
    SA --> DB
    SA --> REVAL
    
    SH --> FORM
```

This integration allows shared components to trigger backend operations while maintaining clean separation of concerns between UI and business logic.

Sources: [src/components/test/TestDetails.tsx:49-53](), [src/components/test/TestDetails.tsx:100-105]()

---

# Page: AI Testing Engine

# AI Testing Engine

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/lib/testing/engine.ts](src/lib/testing/engine.ts)
- [src/lib/testing/mock.ts](src/lib/testing/mock.ts)

</details>



## Purpose and Scope

The AI Testing Engine is the core component responsible for converting human-readable test definitions into structured prompts that can be executed by AI agents. It bridges the gap between natural language test descriptions and the formal instructions needed by LLM-powered browser automation agents.

This document covers the prompt generation system, response parsing, and test definition structures. For information about test execution orchestration, see [Background Processing](#6). For details about the BrowserUse API integration that actually runs these tests, see [External Integrations](#7).

## Core Architecture

The AI Testing Engine operates on a simple but powerful principle: convert structured test definitions into detailed LLM prompts that can be executed by browser automation agents.

### AI Testing Engine Flow

```mermaid
graph TD
    TestDef["TestDefinition"]
    Steps["steps: TestStep[]"]
    Eval["evaluation: string"]
    
    CreateTest["createTest()"]
    StringifyTest["stringifyTest()"]
    GetTaskPrompt["getTaskPrompt()"]
    
    SystemPrompt["SYSTEM_PROMPT"]
    FormattedTest["Formatted XML Test"]
    FullPrompt["Complete LLM Prompt"]
    
    BrowserUse["BrowserUse API"]
    RawResponse["Raw JSON Response"]
    ParseResponse["getTaskResponse()"]
    TaskResponse["TaskResponse"]
    
    TestDef --> Steps
    TestDef --> Eval
    Steps --> CreateTest
    Eval --> CreateTest
    CreateTest --> TestDef
    
    TestDef --> StringifyTest
    StringifyTest --> FormattedTest
    FormattedTest --> GetTaskPrompt
    SystemPrompt --> GetTaskPrompt
    GetTaskPrompt --> FullPrompt
    
    FullPrompt --> BrowserUse
    BrowserUse --> RawResponse
    RawResponse --> ParseResponse
    ParseResponse --> TaskResponse
```

*Sources: [src/lib/testing/engine.ts:1-243]()*

## Data Structures

The engine is built around several key TypeScript interfaces that define the structure of tests and responses.

### Test Definition Structure

```mermaid
graph TD
    TestDefinition["TestDefinition"]
    TestSuiteDefinition["TestSuiteDefinition"]
    
    Label["label: string"]
    Steps["steps: TestStep[]"]
    Evaluation["evaluation: string"]
    
    StepId["id: number"]
    StepLabel["label: string"] 
    StepDescription["description: string"]
    
    SuiteLabel["label: string"]
    Tests["tests: TestDefinition[]"]
    
    TestDefinition --> Label
    TestDefinition --> Steps
    TestDefinition --> Evaluation
    
    Steps --> StepId
    Steps --> StepLabel
    Steps --> StepDescription
    
    TestSuiteDefinition --> SuiteLabel
    TestSuiteDefinition --> Tests
    
    Tests --> TestDefinition
```

*Sources: [src/lib/testing/engine.ts:54-75]()*

### Response Structure

The engine expects responses from the AI agent in a specific JSON format defined by the `zResponse` schema:

| Field | Type | Description |
|-------|------|-------------|
| `status` | `'pass' \| 'failing'` | Overall test result |
| `steps` | `Array<{id: string, description: string}> \| null` | Successfully completed steps |
| `error` | `string \| null` | Error message if test failed |

*Sources: [src/lib/testing/engine.ts:3-18]()*

## Prompt Generation System

### System Prompt

The engine uses a comprehensive system prompt that instructs the AI agent on how to execute tests. The `SYSTEM_PROMPT` constant contains detailed instructions covering:

- Step execution requirements (exact order, no deviations)
- Success/failure criteria for individual steps
- Evaluation criteria for final state validation
- Required response format (JSON schema)
- Example tasks and responses

*Sources: [src/lib/testing/engine.ts:77-203]()*

### Test Formatting

The `stringifyTest()` function converts a `TestDefinition` into XML format that the LLM can easily parse:

```xml
<test>
  <steps>
    <step id="0" label="1">Go to docs.browser-use.com</step>
    <step id="1" label="2">Click on Cloud API V1 documentation.</step>
  </steps>
  <evaluation>The page needs to show POST request documentation.</evaluation>
</test>
```

The `getTaskPrompt()` function combines the system prompt with the formatted test to create the complete prompt sent to the AI agent.

*Sources: [src/lib/testing/engine.ts:208-230]()*

## Response Parsing

The `getTaskResponse()` function handles parsing and validation of AI agent responses:

```mermaid
graph TD
    RawOutput["Raw String Output"]
    ParseJSON["JSON.parse()"]
    ValidateSchema["zResponse.safeParse()"]
    
    SuccessPath["Valid Response"]
    ErrorPaths["Error Handling"]
    
    NoOutput["No Output"]
    ParseError["JSON Parse Error"]
    ValidationError["Schema Validation Error"]
    
    FailResponse["TaskResponse with status: 'failing'"]
    
    RawOutput --> ParseJSON
    ParseJSON --> ValidateSchema
    ValidateSchema --> SuccessPath
    
    RawOutput --> NoOutput
    ParseJSON --> ParseError
    ValidateSchema --> ValidationError
    
    NoOutput --> FailResponse
    ParseError --> FailResponse
    ValidationError --> FailResponse
    
    ErrorPaths --> FailResponse
```

*Sources: [src/lib/testing/engine.ts:23-52]()*

## Mock Test Examples

The engine includes several predefined test examples that demonstrate different scenarios:

### Test Types

| Test Name | Purpose | Expected Result |
|-----------|---------|-----------------|
| `DOCS_PASSING_SEARCH_TEST` | Demonstrates successful test execution | Pass |
| `DOCS_FAILING_EVAL_SEARCH_TEST` | Shows evaluation criteria mismatch | Fail (evaluation) |
| `DOCS_FAILING_TEST_SEARCH_TEST` | Shows step execution failure | Fail (step) |

### Example Test Structure

The `createTest()` helper function simplifies test creation by converting string arrays into properly structured `TestDefinition` objects:

```mermaid
graph LR
    StringArray["steps: string[]"]
    CreateTest["createTest()"]
    TestDefinition["TestDefinition"]
    
    StepMapping["Map to TestStep objects"]
    IdGeneration["Generate sequential IDs"]
    LabelGeneration["Generate numeric labels"]
    
    StringArray --> CreateTest
    CreateTest --> StepMapping
    StepMapping --> IdGeneration
    IdGeneration --> LabelGeneration
    LabelGeneration --> TestDefinition
```

*Sources: [src/lib/testing/mock.ts:1-51](), [src/lib/testing/engine.ts:232-242]()*

## Integration with External Systems

The AI Testing Engine serves as the translation layer between the QA Use platform and external AI services:

### Engine Integration Flow

```mermaid
graph TD
    UITestCreation["User Creates Test in UI"]
    DatabaseStorage["Test Stored in PostgreSQL"]
    InngestTrigger["Inngest Job Triggered"]
    
    EngineConversion["AI Testing Engine"]
    GetTaskPrompt["getTaskPrompt()"]
    BrowserUseAPI["BrowserUse API"]
    
    ResponseParsing["getTaskResponse()"]
    DatabaseUpdate["Update Test Run Status"]
    NotificationSystem["Email Notifications"]
    
    UITestCreation --> DatabaseStorage
    DatabaseStorage --> InngestTrigger
    InngestTrigger --> EngineConversion
    
    EngineConversion --> GetTaskPrompt
    GetTaskPrompt --> BrowserUseAPI
    BrowserUseAPI --> ResponseParsing
    
    ResponseParsing --> DatabaseUpdate
    DatabaseUpdate --> NotificationSystem
```

*Sources: [src/lib/testing/engine.ts:222-230]()*

The engine's primary responsibility is ensuring that human-readable test descriptions are converted into precise, actionable instructions that AI agents can execute reliably. It achieves this through structured data types, comprehensive prompting, and robust response validation.

---

# Page: Background Processing

# Background Processing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/components/test/run/TestRunDetails.tsx](src/components/test/run/TestRunDetails.tsx)
- [src/lib/inngest/functions.tsx](src/lib/inngest/functions.tsx)

</details>



The Background Processing system provides reliable, scalable orchestration of long-running test execution workflows using Inngest. This system handles the asynchronous execution of AI-powered browser tests, manages their lifecycle from creation to completion, and coordinates notifications and status updates.

For information about the AI Testing Engine that generates prompts for these background jobs, see [AI Testing Engine](#5). For details about external service integrations including BrowserUse API calls, see [External Integrations](#7).

## System Architecture

The background processing system is built on Inngest, which provides event-driven function orchestration with built-in retry logic, step isolation, and failure handling. The system processes two main types of events: individual test runs and complete test suite executions.

```mermaid
graph TD
    subgraph "Event Triggers"
        SINGLE_TEST["test/run event"]
        SUITE_TEST["test-suite/run event"]
    end
    
    subgraph "Inngest Functions"
        RUN_TEST["runTest function"]
        RUN_SUITE["runTestSuite function"]
        HELLO["helloWorld function"]
    end
    
    subgraph "Execution Steps"
        START["_startTestRun"]
        POLL["_pollTaskUntilFinished"]
        FINALIZE_TEST["_finalizeTestRun"]
        FINALIZE_SUITE["_finalizeSuiteRun"]
        NOTIFY["_sendSuiteNotification"]
    end
    
    subgraph "External Services"
        BROWSERUSE_API["BrowserUse API"]
        DATABASE["PostgreSQL Database"]
        RESEND_API["Resend Email API"]
    end
    
    SINGLE_TEST --> RUN_TEST
    SUITE_TEST --> RUN_SUITE
    
    RUN_TEST --> START
    RUN_TEST --> POLL
    RUN_TEST --> FINALIZE_TEST
    
    RUN_SUITE --> START
    RUN_SUITE --> POLL
    RUN_SUITE --> FINALIZE_SUITE
    RUN_SUITE --> NOTIFY
    
    START --> BROWSERUSE_API
    START --> DATABASE
    POLL --> BROWSERUSE_API
    POLL --> DATABASE
    FINALIZE_TEST --> DATABASE
    FINALIZE_SUITE --> DATABASE
    NOTIFY --> RESEND_API
    NOTIFY --> DATABASE
```

Sources: [src/lib/inngest/functions.tsx:1-401]()

## Core Inngest Functions

The system defines three main Inngest functions that handle different aspects of test execution:

### `helloWorld` Function

A utility function for testing Inngest connectivity and basic event processing.

```mermaid
graph LR
    EVENT["hello event"] --> HELLO_FUNC["helloWorld function"]
    HELLO_FUNC --> STEP["hello step"]
    STEP --> RESPONSE["Hello message"]
```

Sources: [src/lib/inngest/functions.tsx:19-33]()

### `runTest` Function

Orchestrates the execution of a single test run through multiple isolated steps:

| Step | Function | Purpose |
|------|----------|---------|
| 1 | `_startTestRun` | Initialize test run and submit to BrowserUse API |
| 2 | `_pollTaskUntilFinished` | Monitor execution until completion |
| 3 | `_finalizeTestRun` | Update final status and timestamps |

The function includes automatic failure handling that marks the test run as failed if any step throws an unrecoverable error.

Sources: [src/lib/inngest/functions.tsx:38-59]()

### `runTestSuite` Function

Coordinates the execution of multiple tests within a suite, managing parallel execution and aggregated results:

```mermaid
graph TD
    SUITE_EVENT["test-suite/run event"] --> GET_TESTS["Get test run IDs"]
    GET_TESTS --> PARALLEL_START["Parallel _startTestRun calls"]
    PARALLEL_START --> PARALLEL_POLL["Parallel _pollTaskUntilFinished calls"]
    PARALLEL_POLL --> FINALIZE["_finalizeSuiteRun"]
    FINALIZE --> NOTIFICATION["_sendSuiteNotification"]
    
    subgraph "Error Handling"
        FAILURE["onFailure handler"]
        FAILURE --> UPDATE_STATUS["Mark suite and tests as failed"]
    end
```

Sources: [src/lib/inngest/functions.tsx:64-101]()

## Test Execution Workflow

The test execution workflow follows a structured pattern that integrates with both the BrowserUse API and the local database:

### Test Initialization (`_startTestRun`)

The initialization step performs several critical operations:

1. **Data Retrieval**: Fetches test definition from database including suite, test, and step information
2. **Prompt Generation**: Converts test definition to BrowserUse-compatible prompt using `getTaskPrompt`
3. **API Submission**: Submits task to BrowserUse API with specific configuration
4. **Status Updates**: Updates database records to reflect running status

```mermaid
sequenceDiagram
    participant F as "_startTestRun"
    participant DB as "Database"
    participant API as "BrowserUse API"
    
    F->>DB: Query test run with steps
    F->>F: Build TestDefinition object
    F->>API: POST /api/v1/run-task
    API-->>F: Return task ID
    F->>DB: Update testRun.browserUseId
    F->>DB: Update testRun.status = 'running'
    F->>DB: Update suiteRun.status = 'running'
```

The BrowserUse API call includes specific configuration parameters:
- Model selection (currently `o3` for higher accuracy)
- Structured output schema for result parsing
- Proxy and adblock settings
- Maximum agent steps limit

Sources: [src/lib/inngest/functions.tsx:108-182]()

### Task Monitoring (`_pollTaskUntilFinished`)

The polling mechanism continuously monitors task execution status:

```mermaid
stateDiagram-v2
    [*] --> Polling
    Polling --> CheckStatus: GET /api/v1/task/{task_id}
    
    CheckStatus --> Running: status = 'running'
    CheckStatus --> Created: status = 'created'
    CheckStatus --> Finished: status = 'finished'
    CheckStatus --> Failed: status = 'failed'/'paused'/'stopped'
    
    Running --> UpdateLiveUrl: Update live_url if available
    Created --> UpdateLiveUrl
    UpdateLiveUrl --> WaitDelay: Wait 1 second
    WaitDelay --> Polling
    
    Finished --> ParseResult: Parse structured output
    ParseResult --> UpdatePassed: status = 'pass'
    ParseResult --> UpdateFailed: status = 'failing'
    
    UpdatePassed --> [*]
    UpdateFailed --> [*]
    Failed --> MarkFailed: Update status to 'failed'
    MarkFailed --> [*]
```

The polling function handles different response scenarios:
- **Running/Created**: Updates live URLs and continues polling
- **Finished**: Parses structured output using `getTaskResponse` and updates test/step statuses
- **Failed/Paused/Stopped**: Marks test as failed and terminates

Sources: [src/lib/inngest/functions.tsx:187-306]()

## Suite Execution Coordination

Suite execution involves coordinating multiple parallel test runs and aggregating their results:

### Parallel Execution Strategy

The `runTestSuite` function executes tests in parallel using `Promise.all()` for both the start and polling phases:

```mermaid
graph TD
    SUITE_START["Suite execution begins"] --> GET_IDS["Retrieve all test run IDs"]
    GET_IDS --> PARALLEL_INIT["Promise.all(_startTestRun)"]
    PARALLEL_INIT --> PARALLEL_POLL["Promise.all(_pollTaskUntilFinished)"]
    PARALLEL_POLL --> FINALIZE["_finalizeSuiteRun"]
    FINALIZE --> CHECK_RESULTS["Check for any failed tests"]
    CHECK_RESULTS --> PASS_SUITE["Mark suite as passed"]
    CHECK_RESULTS --> FAIL_SUITE["Mark suite as failed"]
    PASS_SUITE --> NOTIFY["_sendSuiteNotification"]
    FAIL_SUITE --> NOTIFY
    NOTIFY --> END["Suite execution complete"]
```

Sources: [src/lib/inngest/functions.tsx:89-100]()

### Result Aggregation (`_finalizeSuiteRun`)

The finalization step determines overall suite status based on individual test results:

| Condition | Suite Status |
|-----------|--------------|
| All tests passed | `passed` |
| Any test failed | `failed` |

Sources: [src/lib/inngest/functions.tsx:330-344]()

## Error Handling and Retry Logic

The background processing system implements comprehensive error handling at multiple levels:

### Function-Level Error Handling

Both `runTest` and `runTestSuite` functions define `onFailure` handlers that automatically update database records when unrecoverable errors occur:

```mermaid
graph TD
    FUNCTION_ERROR["Function throws error"] --> ON_FAILURE["onFailure handler triggered"]
    
    subgraph "runTest onFailure"
        UPDATE_TEST["Update testRun.status = 'failed'"]
    end
    
    subgraph "runTestSuite onFailure"
        UPDATE_SUITE["Update suiteRun.status = 'failed'"]
        UPDATE_ALL_TESTS["Update all testRuns.status = 'failed'"]
    end
    
    ON_FAILURE --> UPDATE_TEST
    ON_FAILURE --> UPDATE_SUITE
    UPDATE_SUITE --> UPDATE_ALL_TESTS
```

Sources: [src/lib/inngest/functions.tsx:41-47](), [src/lib/inngest/functions.tsx:67-74]()

### Step-Level Error Types

Individual steps can throw different types of errors:

- **`NonRetriableError`**: Used for data consistency issues (test not found, invalid state)
- **`RetryAfterError`**: Used for temporary API failures with specified retry delay

Sources: [src/lib/inngest/functions.tsx:2](), [src/lib/inngest/functions.tsx:159](), [src/lib/inngest/functions.tsx:209]()

## Notification System Integration

The background processing system includes automated email notifications for failed test suites:

### Notification Triggers

Notifications are sent only under specific conditions:
- Suite execution has completed with `failed` status
- Suite has a configured `notificationsEmailAddress`

### Email Composition

The `_sendSuiteNotification` function constructs emails using:
- **Template**: `SuiteFailedEmail` React component
- **Service**: Resend API client
- **Content**: Suite details, execution times, and individual test results

```mermaid
graph TD
    NOTIFICATION_CHECK["Check notification conditions"] --> HAS_EMAIL["Suite has email address?"]
    HAS_EMAIL -->|No| SKIP["Skip notification"]
    HAS_EMAIL -->|Yes| CHECK_STATUS["Suite status = 'failed'?"]
    CHECK_STATUS -->|No| SKIP
    CHECK_STATUS -->|Yes| BUILD_EMAIL["Build SuiteFailedEmail"]
    BUILD_EMAIL --> SEND["Send via Resend API"]
    SEND --> SUCCESS["Return {sent: true}"]
    SKIP --> NO_SEND["Return {sent: false}"]
```

Sources: [src/lib/inngest/functions.tsx:346-400]()

## Real-Time UI Integration

The background processing system integrates with the frontend through polling mechanisms that provide real-time updates:

### Polling Component Integration

The `TestRunDetails` component includes a `<Polling>` component that automatically refreshes the page when tests are in running or pending states:

```typescript
<Polling poll={status === 'running' || status === 'pending'} />
```

### Live Preview Updates

During test execution, the system continuously updates `liveUrl` and `publicShareUrl` fields in the database, enabling real-time browser preview in the UI:

| Test Status | Preview Behavior |
|-------------|------------------|
| `pending` | Shows placeholder message |
| `running` | Displays live iframe with BrowserUse execution |
| `passed`/`failed` | Shows completion message with link to shared recording |

Sources: [src/components/test/run/TestRunDetails.tsx:103](), [src/components/test/run/TestRunDetails.tsx:122-128]()

## Database Schema Integration

The background processing system maintains strict consistency with the database schema through transactional updates:

### Status Synchronization

The system updates multiple related entities atomically:

```mermaid
graph TD
    subgraph "Test Run Updates"
        TR_STATUS["testRun.status"]
        TR_BROWSER["testRun.browserUseId"]
        TR_LIVE["testRun.liveUrl"]
        TR_SHARE["testRun.publicShareUrl"]
        TR_ERROR["testRun.error"]
        TR_FINISHED["testRun.finishedAt"]
    end
    
    subgraph "Test Step Updates"
        TRS_STATUS["testRunStep.status"]
    end
    
    subgraph "Suite Run Updates"
        SR_STATUS["suiteRun.status"]
        SR_FINISHED["suiteRun.finishedAt"]
    end
    
    TRANSACTION["Database Transaction"] --> TR_STATUS
    TRANSACTION --> TR_BROWSER
    TRANSACTION --> TR_LIVE
    TRANSACTION --> TR_SHARE
    TRANSACTION --> TR_ERROR
    TRANSACTION --> TR_FINISHED
    TRANSACTION --> TRS_STATUS
    TRANSACTION --> SR_STATUS
    TRANSACTION --> SR_FINISHED
```

All critical updates use database transactions to ensure data consistency, particularly when updating test results and their associated step statuses.

Sources: [src/lib/inngest/functions.tsx:217-236](), [src/lib/inngest/functions.tsx:240-264]()

---

# Page: External Integrations

# External Integrations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env.example](.env.example)
- [src/lib/api/client.ts](src/lib/api/client.ts)
- [src/lib/resend/emails/SuiteFailedEmail.tsx](src/lib/resend/emails/SuiteFailedEmail.tsx)
- [src/lib/resend/emails/SuiteNotificationsSetupEmail.tsx](src/lib/resend/emails/SuiteNotificationsSetupEmail.tsx)

</details>



This document covers the external service integrations used by the QA Use platform. The platform relies on two primary external services: the BrowserUse Cloud API for AI-powered browser automation and the Resend email service for notification delivery. For information about the internal AI testing engine that coordinates with these services, see [AI Testing Engine](#5). For details about the background processing system that orchestrates these integrations, see [Background Processing](#6).

## Overview

The QA Use platform integrates with external services to provide its core functionality:

| Service | Purpose | Configuration |
|---------|---------|---------------|
| BrowserUse Cloud API | AI agent execution for browser automation | `BROWSER_USE_API_KEY` |
| Resend Email Service | Email notification delivery | `RESEND_API_KEY`, `RESEND_FROM_EMAIL` |

## BrowserUse API Integration

### Client Configuration

The platform uses an OpenAPI-generated client to communicate with the BrowserUse Cloud API. The client is configured in [src/lib/api/client.ts:1-11]() and establishes a connection to `https://api.browser-use.com/` using Bearer token authentication.

```mermaid
graph TD
    subgraph "QA Use Platform"
        CLIENT["client<br/>(OpenAPI Client)"]
        ENV_KEY["process.env.BROWSER_USE_API_KEY"]
        API_TYPES["paths type<br/>(from @/lib/api/v1)"]
    end
    
    subgraph "BrowserUse Cloud"
        API_ENDPOINT["api.browser-use.com"]
        BROWSER_AGENTS["AI Browser Agents"]
    end
    
    ENV_KEY --> CLIENT
    API_TYPES --> CLIENT
    CLIENT -->|"Bearer Token Auth"| API_ENDPOINT
    API_ENDPOINT --> BROWSER_AGENTS
    
    CLIENT -->|"HTTP Requests"| API_ENDPOINT
    API_ENDPOINT -->|"Execution Results<br/>Live URLs"| CLIENT
```

**BrowserUse API Client Architecture**

The client uses the `createClient` function from the `openapi-fetch` library to generate type-safe API calls. The `paths` type provides TypeScript definitions for all available API endpoints.

### Authentication

Authentication is handled through a Bearer token specified in the `Authorization` header. The token is sourced from the `BROWSER_USE_API_KEY` environment variable as configured in [src/lib/api/client.ts:9]().

Sources: [src/lib/api/client.ts:1-11](), [.env.example:1-2]()

## Resend Email Integration

### Email Templates

The platform includes React-based email templates for user notifications:

| Template | Purpose | File |
|----------|---------|------|
| `SuiteFailedEmail` | Notify users when test suite execution fails | [src/lib/resend/emails/SuiteFailedEmail.tsx]() |
| `SuiteNotificationsSetupEmail` | Confirm notification setup for a suite | [src/lib/resend/emails/SuiteNotificationsSetupEmail.tsx]() |

### SuiteFailedEmail Template

The `SuiteFailedEmail` component renders failure notifications with detailed information about the failed suite execution. It accepts props including `suiteId`, `suiteName`, timing information, and an array of `runs` with their respective statuses.

```mermaid
graph LR
    subgraph "Email Template Props"
        SUITE_DATA["suiteId<br/>suiteName<br/>suiteStartedAt<br/>suiteFinishedAt"]
        RUNS_DATA["runs[]<br/>(runId, runName, runStatus)"]
    end
    
    subgraph "SuiteFailedEmail Component"
        HEADER["Suite {suiteName} failed!"]
        TIMING["Started/Finished timestamps"]
        RUNS_LIST["Run status list<br/>(SUCCESS/FAILED/PENDING)"]
    end
    
    SUITE_DATA --> HEADER
    SUITE_DATA --> TIMING
    RUNS_DATA --> RUNS_LIST
```

**SuiteFailedEmail Template Structure**

The template displays suite execution details in a structured format with timing information and individual run statuses.

### Email Configuration

Email integration requires three environment variables as defined in [.env.example:4-9]():

- `RESEND_API_KEY`: Authentication token for the Resend service
- `RESEND_FROM_EMAIL`: Sender email address and display name

The configuration includes a note about using `onboarding@resend.dev` for testing and recommending domain verification for production deployments.

Sources: [src/lib/resend/emails/SuiteFailedEmail.tsx:1-46](), [src/lib/resend/emails/SuiteNotificationsSetupEmail.tsx:1-30](), [.env.example:4-9]()

## Integration Flow

### Test Execution Integration

```mermaid
sequenceDiagram
    participant Platform as "QA Use Platform"
    participant Inngest as "Inngest Background Jobs"
    participant BrowserUse as "BrowserUse API"
    participant Resend as "Resend Email Service"
    
    Platform->>Inngest: "Trigger suite execution"
    Inngest->>BrowserUse: "Submit test execution request"
    BrowserUse-->>Inngest: "Return execution ID & live URL"
    
    loop "Poll for completion"
        Inngest->>BrowserUse: "Check execution status"
        BrowserUse-->>Inngest: "Status update"
    end
    
    alt "Suite fails"
        Inngest->>Resend: "Send SuiteFailedEmail"
        Resend-->>Inngest: "Email delivery confirmation"
    end
    
    Inngest->>Platform: "Update database with results"
```

**External Service Integration Sequence**

This sequence shows how the platform coordinates between BrowserUse for test execution and Resend for failure notifications.

### Configuration Dependencies

```mermaid
graph TD
    subgraph "Environment Configuration"
        ENV_BROWSER["BROWSER_USE_API_KEY"]
        ENV_RESEND_KEY["RESEND_API_KEY"]
        ENV_RESEND_FROM["RESEND_FROM_EMAIL"]
    end
    
    subgraph "Application Services"
        CLIENT_CONFIG["client.ts<br/>createClient()"]
        EMAIL_SERVICE["Email Templates<br/>SuiteFailedEmail<br/>SuiteNotificationsSetupEmail"]
    end
    
    subgraph "External APIs"
        BROWSERUSE_API["api.browser-use.com"]
        RESEND_API["resend.com"]
    end
    
    ENV_BROWSER --> CLIENT_CONFIG
    ENV_RESEND_KEY --> EMAIL_SERVICE
    ENV_RESEND_FROM --> EMAIL_SERVICE
    
    CLIENT_CONFIG --> BROWSERUSE_API
    EMAIL_SERVICE --> RESEND_API
```

**External Integration Configuration Flow**

The diagram shows how environment variables flow through the application to configure external service connections.

Sources: [src/lib/api/client.ts:7-10](), [.env.example:1-9]()

## Error Handling and Reliability

The platform handles external service integration failures through several mechanisms:

- **Authentication Errors**: Missing or invalid API keys will cause service initialization to fail
- **Network Failures**: The Inngest background job system provides retry logic for transient failures
- **Email Delivery**: Resend provides delivery status reporting for notification reliability

The `createClient` function from `openapi-fetch` provides built-in error handling for HTTP status codes and network connectivity issues when communicating with the BrowserUse API.

Sources: [src/lib/api/client.ts:1-11]()

---

# Page: Server Actions

# Server Actions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [pnpm-lock.yaml](pnpm-lock.yaml)
- [src/app/actions.ts](src/app/actions.ts)
- [src/app/api/inngest/route.ts](src/app/api/inngest/route.ts)
- [src/app/suite/[suiteId]/test/[testId]/actions.ts](src/app/suite/[suiteId]/test/[testId]/actions.ts)
- [src/components/shared/PageHeader.tsx](src/components/shared/PageHeader.tsx)
- [src/components/test/TestDetails.tsx](src/components/test/TestDetails.tsx)

</details>



This document covers the Next.js Server Actions implementation in the QA Use platform, which handle form submissions and data mutations on the server side. Server Actions provide a seamless way to perform database operations, trigger background jobs, and manage navigation flow without requiring separate API endpoints.

For information about background job processing, see [Background Processing](#6). For database schema and operations, see [Core Concepts](#3).

## Overview

Server Actions in the QA Use platform follow a consistent pattern of input validation, database operations, cache invalidation, and navigation. The platform implements server actions for suite creation, test execution, and test deletion, integrating tightly with the Drizzle ORM database layer and Inngest background processing system.

**Core Server Action Pattern:**
```mermaid
graph TD
    Form["Form Submission"] --> Action["Server Action Function"]
    Action --> Validate["Input Validation (Zod)"]
    Validate --> DB["Database Transaction"]
    DB --> Inngest["Trigger Background Job"]
    Inngest --> Cache["Revalidate Path Cache"]
    Cache --> Redirect["Redirect to New Page"]
```

Sources: [src/app/actions.ts:1-29](), [src/app/suite/[suiteId]/test/[testId]/actions.ts:1-77]()

## Suite Management Actions

The suite creation functionality is handled by the `createSuiteAction` server action, which validates input, creates database records, and manages navigation flow.

### Suite Creation Flow

```mermaid
graph TD
    UI["Suite Creation Form"] --> createSuiteAction["createSuiteAction"]
    createSuiteAction --> zCreateSuite["Zod Validation Schema"]
    zCreateSuite --> dbInsert["db.insert(schema.suite)"]
    dbInsert --> revalidate["revalidatePath('/')"]
    revalidate --> redirect["redirect(/suite/{id})"]
```

The `createSuiteAction` function implements the following steps:

1. **Input Validation**: Uses Zod schema `zCreateSuite` to validate the suite name from form data
2. **Database Insert**: Creates new suite record using Drizzle ORM
3. **Cache Invalidation**: Calls `revalidatePath('/')` to refresh the home page cache
4. **Navigation**: Redirects user to the newly created suite detail page

Sources: [src/app/actions.ts:10-29]()

## Test Management Actions

Test-related server actions handle test execution and deletion, integrating with the Inngest background processing system for test execution orchestration.

### Test Execution Action

The `runTestAction` handles triggering individual test runs:

```mermaid
graph TD
    TestForm["Test Run Form"] --> runTestAction["runTestAction(testId, FormData)"]
    runTestAction --> dbTx["Database Transaction"]
    dbTx --> findTest["Find Test with Steps & Suite"]
    findTest --> createRun["Insert testRun Record"]
    createRun --> createSteps["Insert testRunStep Records"]
    createSteps --> sendEvent["inngest.send('test/run')"]
    sendEvent --> revalidate["revalidatePath()"]
    revalidate --> redirect["redirect to Run Details"]
```

**Key Operations:**
1. **Database Transaction**: Ensures atomicity when creating test run and step records
2. **Test Run Creation**: Inserts new `testRun` record with `pending` status
3. **Step Initialization**: Creates `testRunStep` records for each test step
4. **Background Job Trigger**: Sends Inngest event to start test execution
5. **Cache Management**: Revalidates test detail page cache
6. **Navigation**: Redirects to the test run detail page

### Test Deletion Action

The `deleteTestAction` removes test records and handles cleanup:

```mermaid
graph TD
    DeleteForm["Delete Test Form"] --> deleteTestAction["deleteTestAction(testId, FormData)"]
    deleteTestAction --> findTest["Find Test with Suite"]
    findTest --> dbDelete["db.delete(schema.test)"]
    dbDelete --> revalidate["revalidatePath(suite)"]
    revalidate --> redirect["redirect to Suite"]
```

Sources: [src/app/suite/[suiteId]/test/[testId]/actions.ts:11-77]()

## Integration Patterns

Server Actions integrate with multiple system components through established patterns:

### Database Integration

```mermaid
graph LR
    ServerAction["Server Action"] --> DrizzleORM["Drizzle ORM"]
    DrizzleORM --> PostgreSQL["PostgreSQL Database"]
    DrizzleORM --> Schema["schema.* Tables"]
    Schema --> suite["suite"]
    Schema --> test["test"]
    Schema --> testRun["testRun"]
    Schema --> testRunStep["testRunStep"]
```

**Database Patterns:**
- Use `db.transaction()` for multi-table operations
- Leverage `db.query.*` for complex joins with relations
- Apply `eq()` conditions for precise record selection
- Utilize `.returning()` for immediate access to created records

### Form Integration

Server Actions connect directly to React forms without requiring custom event handlers:

```mermaid
graph TD
    JSXForm["<form action={serverAction}>"] --> FormData["FormData Object"]
    FormData --> ServerAction["Server Action Function"]
    ServerAction --> ValidatedData["Parsed & Validated Data"]
    ValidatedData --> DatabaseOp["Database Operation"]
    DatabaseOp --> Response["Automatic Response Handling"]
```

**Form Binding Examples:**
- `<form action={runTest}>` - Binds to test execution
- `<form action={deleteTest}>` - Binds to test deletion
- `<form action={createSuiteAction}>` - Binds to suite creation

### Background Processing Integration

```mermaid
graph TD
    ServerAction["Server Action"] --> InngestSend["inngest.send()"]
    InngestSend --> EventQueue["Inngest Event Queue"]
    EventQueue --> BackgroundFunction["Background Function"]
    BackgroundFunction --> BrowserUseAPI["BrowserUse API"]
    BackgroundFunction --> DatabaseUpdate["Update Run Status"]
```

Server Actions trigger background processing by sending Inngest events with structured payloads containing necessary identifiers for job execution.

Sources: [src/components/test/TestDetails.tsx:49-53](), [src/components/test/TestDetails.tsx:100-105](), [src/app/suite/[suiteId]/test/[testId]/actions.ts:47-52]()

## Error Handling and Validation

Server Actions implement comprehensive error handling and input validation:

### Validation Pipeline

```mermaid
graph TD
    FormInput["Form Input"] --> ZodSchema["Zod Validation Schema"]
    ZodSchema --> ParseSuccess["Parse Success"]
    ZodSchema --> ParseError["Parse Error"]
    ParseSuccess --> DatabaseOp["Database Operation"]
    ParseError --> ErrorResponse["Validation Error Response"]
    DatabaseOp --> DBSuccess["Success"]
    DatabaseOp --> DBError["Database Error"]
    DBSuccess --> CacheRevalidation["Cache Revalidation"]
    DBError --> ErrorLog["Error Logging"]
```

**Error Handling Patterns:**
- Zod schema validation for type safety and input sanitization
- Database transaction rollback on operation failure
- Error logging for debugging and monitoring
- Graceful error responses to the client

### Cache Management

Server Actions coordinate with Next.js caching through `revalidatePath()` calls:

| Action | Revalidated Path | Purpose |
|--------|------------------|---------|
| `createSuiteAction` | `/` | Refresh suite list on homepage |
| `runTestAction` | `/suite/{suiteId}/test/{testId}` | Update test run list |
| `deleteTestAction` | `/suite/{suiteId}` | Remove deleted test from suite view |

Sources: [src/app/actions.ts:27](), [src/app/suite/[suiteId]/test/[testId]/actions.ts:54](), [src/app/suite/[suiteId]/test/[testId]/actions.ts:75]()

---

# Page: Development Guide

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [docker-compose.dev.yaml](docker-compose.dev.yaml)
- [media/run.png](media/run.png)
- [media/suite.png](media/suite.png)
- [next.config.ts](next.config.ts)
- [package.json](package.json)

</details>



This document provides guidance for developers working on the QA Use platform, covering development environment setup, project structure, and key development workflows. It focuses on the technical aspects of building and maintaining the AI-powered E2E testing platform.

For information about the overall system architecture and core concepts, see [Overview](#1) and [Core Concepts](#3). For deployment and production configuration, see [Getting Started](#2).

## Development Environment Setup

The QA Use platform uses a containerized development environment that provides hot reloading and automatic database migrations. The development setup consists of four main services orchestrated through Docker Compose.

### Development Services Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        DEV_APP["app<br/>Next.js Dev Server<br/>Port 3000"]
        DEV_DB["postgres<br/>PostgreSQL Database<br/>Port 5432"]
        DEV_INNGEST["inngest<br/>Background Job Server<br/>Port 8288"]
        DEV_MIGRATE["migrate<br/>Database Migration Service"]
    end
    
    subgraph "Host Machine"
        SRC["./src<br/>Source Code"]
        DATA["./data/postgres<br/>Database Volume"]
        ENV[".env<br/>Environment Variables"]
    end
    
    DEV_APP --> DEV_DB
    DEV_APP --> DEV_INNGEST
    DEV_MIGRATE --> DEV_DB
    
    SRC -.->|Hot Reload| DEV_APP
    DATA -.->|Persistence| DEV_DB
    ENV -.->|Configuration| DEV_APP
    
    DEV_INNGEST -.->|API Calls| DEV_APP
```

**Sources:** [docker-compose.dev.yaml:1-107]()

### Service Configuration

The development environment is configured through `docker-compose.dev.yaml` with the following key services:

**Application Service (`app`)**
- Built from `Dockerfile.dev` with hot reloading enabled
- Watches source files in `./src` with automatic sync
- Exposes port 3000 for the Next.js development server
- Environment variables: `WATCHPACK_POLLING=true`, `INNGEST_DEV=1`

**Database Service (`postgres`)**
- PostgreSQL 15 with health checks
- Default credentials: `postgres/postgres`
- Database name: `qa-use`
- Data persisted in `./data/postgres` volume

**Background Processing (`inngest`)**
- Inngest development server for job orchestration
- Connects to app service at `http://app:3000/api/inngest`
- Web interface available at port 8288

**Migration Service (`migrate`)**
- Runs Drizzle database migrations on startup
- Depends on healthy PostgreSQL service
- Restarts on failure to ensure migrations complete

**Sources:** [docker-compose.dev.yaml:2-46](), [docker-compose.dev.yaml:57-90]()

### Package Management and Scripts

The project uses `pnpm` as the package manager with the following key scripts defined in `package.json`:

| Script | Purpose |
|--------|---------|
| `dev` | Start Next.js development server with Turbopack |
| `build` | Create production build |
| `start` | Start production server |
| `lint` | Run ESLint checks |
| `test:types` | TypeScript type checking |
| `openapi:gen` | Generate TypeScript definitions from BrowserUse API |

**Sources:** [package.json:5-12]()

### Key Dependencies

The platform relies on several critical dependencies:

**Framework and UI:**
- `next` (15.4.2) - React framework
- `react` (19.1.0) - UI library
- `@radix-ui/*` - UI component primitives
- `tailwindcss` (^4) - CSS framework

**Data and API:**
- `drizzle-orm` (0.44.3) - Type-safe database ORM
- `pg` (8.16.3) - PostgreSQL client
- `openapi-fetch` (0.14.0) - Type-safe API client
- `zod` (4.0.5) - Schema validation

**Background Processing and AI:**
- `inngest` (3.40.1) - Background job orchestration
- `openai` (5.10.2) - OpenAI API client
- `resend` (4.7.0) - Email service

**Sources:** [package.json:13-34]()

## Development Workflow

### Local Development Process

```mermaid
flowchart TD
    START["Start Development"]
    SETUP["docker compose -f docker-compose.dev.yaml up"]
    HEALTH["Wait for Services Health Check"]
    MIGRATE["Auto-run Database Migrations"]
    DEV["Development Ready"]
    
    EDIT["Edit Source Files"]
    RELOAD["Hot Reload"]
    TEST["Test Changes"]
    
    API_GEN["Generate API Types"]
    TYPE_CHECK["Type Checking"]
    LINT["Lint Code"]
    
    START --> SETUP
    SETUP --> HEALTH
    HEALTH --> MIGRATE
    MIGRATE --> DEV
    
    DEV --> EDIT
    EDIT --> RELOAD
    RELOAD --> TEST
    TEST --> EDIT
    
    DEV --> API_GEN
    API_GEN --> TYPE_CHECK
    TYPE_CHECK --> LINT
```

**Sources:** [docker-compose.dev.yaml:8-26](), [package.json:5-12]()

### File Watching and Hot Reload

The development environment provides comprehensive file watching with different strategies for different file types:

**Hot Reload Files (sync):**
- `./src/**/*` - All source code changes trigger immediate reload

**Restart Triggers (sync+restart):**
- `./drizzle.config.ts` - Database configuration changes
- `./next.config.ts` - Next.js configuration changes  
- `./tsconfig.json` - TypeScript configuration changes

**Rebuild Triggers (rebuild):**
- `./package.json` - Dependency changes require container rebuild

**Sources:** [docker-compose.dev.yaml:10-26]()

### API Type Generation

The platform maintains type safety with external APIs through automated type generation:

```bash
pnpm openapi:gen
```

This command fetches the OpenAPI specification from `https://api.browser-use.com/openapi.json` and generates TypeScript definitions at `./src/lib/api/v1.d.ts`.

**Sources:** [package.json:11]()

## Build and Deployment

### Production Build Process

The production build uses a multi-stage Docker approach optimized for size and performance:

```mermaid
graph LR
    subgraph "Build Stages"
        DEPS["deps<br/>node:23-alpine<br/>Install Dependencies"]
        BUILDER["builder<br/>node:23-alpine<br/>Build Application"]
        RUNNER["runner<br/>node:23-alpine<br/>Production Runtime"]
    end
    
    DEPS -->|node_modules| BUILDER
    BUILDER -->|Built App| RUNNER
    
    DEPS_FILES["package.json<br/>pnpm-lock.yaml"] --> DEPS
    SOURCE["Source Code"] --> BUILDER
    FINAL["Production Image"] --> RUNNER
```

**Sources:** [Dockerfile:1-37]()

### Build Stage Details

**Dependencies Stage (`deps`):**
- Base: `node:23-alpine` 
- Installs pnpm and project dependencies
- Uses frozen lockfile for reproducible builds

**Builder Stage (`builder`):**
- Copies dependencies from deps stage
- Copies source code and builds the application
- Runs `pnpm build` to create production assets

**Runner Stage (`runner`):**
- Production-only runtime environment
- Sets `NODE_ENV=production`
- Exposes port 3000
- Runs `pnpm start` command

**Sources:** [Dockerfile:1-8](), [Dockerfile:10-21](), [Dockerfile:24-37]()

### Environment Configuration

The application requires several environment variables for proper operation. The development environment provides defaults for local services, while production requires proper configuration:

**Database Configuration:**
- `DATABASE_URL` - PostgreSQL connection string
- Default dev: `postgresql://postgres:postgres@postgres:5432/qa-use`

**External API Keys:**
- `BROWSER_USE_API_KEY` - BrowserUse API authentication
- `RESEND_API_KEY` - Email service authentication

**Background Processing:**
- `INNGEST_DEV=1` - Enables development mode for Inngest
- `INNGEST_BASE_URL` - Inngest service endpoint

**Sources:** [docker-compose.dev.yaml:28-36]()

### Development vs Production Configuration

The platform uses different configuration files for development and production environments:

| Environment | Compose File | Purpose |
|-------------|--------------|---------|
| Development | `docker-compose.dev.yaml` | Hot reload, file watching, dev services |
| Production | `docker-compose.yaml` | Optimized builds, production settings |

**Sources:** [docker-compose.dev.yaml:1-2]()

This development guide provides the foundation for working with the QA Use platform's codebase. The containerized approach ensures consistent development environments while the hot reloading capabilities enable rapid iteration during development.

---

# Page: Project Structure

# Project Structure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [postcss.config.mjs](postcss.config.mjs)
- [public/file.svg](public/file.svg)
- [public/globe.svg](public/globe.svg)
- [public/next.svg](public/next.svg)
- [public/vercel.svg](public/vercel.svg)
- [src/app/loader.ts](src/app/loader.ts)

</details>



This document explains the organization of files and directories within the QA Use codebase. It covers the Next.js application structure, key modules, configuration files, and deployment artifacts. For information about the data model and relationships, see [Core Concepts](#3). For details about UI components, see [User Interface](#4).

## Directory Overview

The QA Use platform follows a standard Next.js 14+ application structure with additional directories for database management, testing infrastructure, and background processing.

### High-Level Directory Structure

```mermaid
graph TD
    ROOT["qa-use/"]
    
    subgraph "Application Code"
        SRC["src/"]
        APP["src/app/"]
        LIB["src/lib/"]
        COMPONENTS["src/components/"]
    end
    
    subgraph "Configuration"
        CONFIG_FILES["Config Files"]
        DOCKER["Docker Files"]
        ENV["Environment"]
    end
    
    subgraph "Public Assets"
        PUBLIC["public/"]
        STATIC["Static Assets"]
    end
    
    subgraph "Dependencies"
        NODE_MODULES["node_modules/"]
        PACKAGE["package.json"]
    end
    
    ROOT --> SRC
    ROOT --> PUBLIC
    ROOT --> CONFIG_FILES
    ROOT --> DOCKER
    ROOT --> NODE_MODULES
    ROOT --> PACKAGE
    
    SRC --> APP
    SRC --> LIB
    SRC --> COMPONENTS
    
    CONFIG_FILES --> ENV
    PUBLIC --> STATIC
```

Sources: Project structure inferred from imports in [src/app/loader.ts:1-64]()

### Core Application Structure

```mermaid
graph TB
    subgraph "src/ - Application Source"
        APP_DIR["app/ - Next.js App Router"]
        LIB_DIR["lib/ - Shared Libraries"]
        COMP_DIR["components/ - React Components"]
    end
    
    subgraph "app/ - Route Definitions"
        PAGES["page.tsx files"]
        LAYOUTS["layout.tsx files"]
        LOADING["loading.tsx files"]
        API_ROUTES["api/ routes"]
        SERVER_ACTIONS["Server Actions"]
        LOADERS["loader.ts files"]
    end
    
    subgraph "lib/ - Core Modules"
        DB_LIB["db/ - Database Layer"]
        TESTING_LIB["testing/ - AI Testing Engine"]
        INNGEST_LIB["inngest/ - Background Jobs"]
        EMAIL_LIB["email/ - Notifications"]
        UTILS_LIB["utils/ - Utilities"]
    end
    
    subgraph "components/ - UI Components"
        UI_COMP["ui/ - Base Components"]
        FEATURE_COMP["Feature Components"]
        SHARED_COMP["Shared Components"]
    end
    
    APP_DIR --> PAGES
    APP_DIR --> LAYOUTS
    APP_DIR --> LOADING
    APP_DIR --> API_ROUTES
    APP_DIR --> SERVER_ACTIONS
    APP_DIR --> LOADERS
    
    LIB_DIR --> DB_LIB
    LIB_DIR --> TESTING_LIB
    LIB_DIR --> INNGEST_LIB
    LIB_DIR --> EMAIL_LIB
    LIB_DIR --> UTILS_LIB
    
    COMP_DIR --> UI_COMP
    COMP_DIR --> FEATURE_COMP
    COMP_DIR --> SHARED_COMP
```

Sources: Structure inferred from imports in [src/app/loader.ts:3-6]()

## Key Directories and Modules

### Database Layer (`src/lib/db/`)

The database layer contains all database-related code using Drizzle ORM:

| File/Directory | Purpose |
|---------------|---------|
| `db.ts` | Database connection instance |
| `schema.ts` | Drizzle schema definitions |
| `migrations/` | Database migration files |

```mermaid
graph LR
    subgraph "Database Module Structure"
        DB_INSTANCE["db.ts - Database Connection"]
        SCHEMA["schema.ts - Table Definitions"]
        MIGRATIONS["migrations/ - Schema Versions"]
    end
    
    subgraph "Schema Entities"
        SUITE_SCHEMA["suite table"]
        TEST_SCHEMA["test table"]
        TEST_STEP_SCHEMA["testStep table"]
        SUITE_RUN_SCHEMA["suiteRun table"]
        TEST_RUN_SCHEMA["testRun table"]
        TEST_RUN_STEP_SCHEMA["testRunStep table"]
    end
    
    DB_INSTANCE --> SCHEMA
    SCHEMA --> SUITE_SCHEMA
    SCHEMA --> TEST_SCHEMA
    SCHEMA --> TEST_STEP_SCHEMA
    SCHEMA --> SUITE_RUN_SCHEMA
    SCHEMA --> TEST_RUN_SCHEMA
    SCHEMA --> TEST_RUN_STEP_SCHEMA
    
    MIGRATIONS --> SCHEMA
```

Sources: [src/app/loader.ts:3-4]()

### Testing Engine (`src/lib/testing/`)

The AI-powered testing infrastructure:

| File | Purpose |
|------|---------|
| `engine.ts` | Core testing engine and prompt generation |
| `mock.ts` | Mock test definitions and sample data |

```mermaid
graph TD
    subgraph "Testing Module"
        ENGINE["engine.ts"]
        MOCK["mock.ts"]
    end
    
    subgraph "Engine Components"
        TEST_SUITE_DEF["TestSuiteDefinition type"]
        PROMPT_GEN["LLM Prompt Generation"]
        RESULT_PARSE["Result Parsing"]
    end
    
    subgraph "Mock Data"
        BROWSERUSE_DOCS["BROWSERUSE_DOCS_TEST_SUITE"]
        SAMPLE_TESTS["Sample Test Definitions"]
    end
    
    ENGINE --> TEST_SUITE_DEF
    ENGINE --> PROMPT_GEN
    ENGINE --> RESULT_PARSE
    
    MOCK --> BROWSERUSE_DOCS
    MOCK --> SAMPLE_TESTS
```

Sources: [src/app/loader.ts:5-6](), [src/app/loader.ts:8]()

### App Router Structure (`src/app/`)

The Next.js App Router implementation with file-based routing:

```mermaid
graph TB
    subgraph "App Router Files"
        ROOT_PAGE["page.tsx - Homepage"]
        ROOT_LAYOUT["layout.tsx - Root Layout"]
        ROOT_LOADER["loader.ts - Data Loader"]
    end
    
    subgraph "Route Segments"
        SUITE_ROUTES["[suiteId]/ - Suite Pages"]
        TEST_ROUTES["test/ - Test Management"]
        API_ROUTES["api/ - API Endpoints"]
    end
    
    subgraph "Data Loading Pattern"
        LOADER_FN["loader() function"]
        PAGE_DATA_TYPE["TPageData type"]
        SUITE_TYPE["TSuite type"]
    end
    
    ROOT_LOADER --> LOADER_FN
    ROOT_LOADER --> PAGE_DATA_TYPE
    ROOT_LOADER --> SUITE_TYPE
    
    LOADER_FN --> ROOT_PAGE
```

Sources: [src/app/loader.ts:10-64]()

## Configuration Files

### Framework Configuration

| File | Purpose |
|------|---------|
| `next.config.ts` | Next.js framework configuration |
| `postcss.config.mjs` | PostCSS and Tailwind CSS configuration |
| `tailwind.config.ts` | Tailwind CSS customization |
| `tsconfig.json` | TypeScript compiler configuration |

### Build and Deployment Configuration

```mermaid
graph LR
    subgraph "Configuration Files"
        NEXT_CONFIG["next.config.ts"]
        POSTCSS_CONFIG["postcss.config.mjs"]
        TAILWIND_CONFIG["tailwind.config.ts"]
        TS_CONFIG["tsconfig.json"]
    end
    
    subgraph "Docker Configuration"
        DOCKERFILE["Dockerfile"]
        DOCKER_COMPOSE["docker-compose.yaml"]
        DOCKER_DEV["docker-compose.dev.yaml"]
    end
    
    subgraph "Environment Configuration"
        ENV_EXAMPLE[".env.example"]
        ENV_LOCAL[".env.local"]
    end
    
    POSTCSS_CONFIG --> TAILWIND_CONFIG
    NEXT_CONFIG --> TS_CONFIG
```

Sources: [postcss.config.mjs:1-6]()

### PostCSS Configuration Details

The PostCSS configuration integrates Tailwind CSS for styling:

```javascript
// postcss.config.mjs
const config = {
  plugins: ["@tailwindcss/postcss"],
};
```

Sources: [postcss.config.mjs:1-6]()

## Data Loading Architecture

The application uses a centralized data loading pattern with automatic mock data seeding:

```mermaid
graph TD
    subgraph "Data Loading Flow"
        LOADER_CALL["loader() function call"]
        DB_QUERY["Database query with relations"]
        MOCK_CHECK["Check if suites exist"]
        SEED_MOCK["Seed BROWSERUSE_DOCS_TEST_SUITE"]
        RETURN_DATA["Return TPageData"]
    end
    
    subgraph "Database Operations"
        FIND_SUITES["db.query.suite.findMany()"]
        INSERT_SUITE["tx.insert(schema.suite)"]
        INSERT_TESTS["tx.insert(schema.test)"]
        INSERT_STEPS["tx.insert(schema.testStep)"]
    end
    
    LOADER_CALL --> DB_QUERY
    DB_QUERY --> FIND_SUITES
    FIND_SUITES --> MOCK_CHECK
    MOCK_CHECK -->|"No suites found"| SEED_MOCK
    SEED_MOCK --> INSERT_SUITE
    INSERT_SUITE --> INSERT_TESTS
    INSERT_TESTS --> INSERT_STEPS
    MOCK_CHECK -->|"Suites exist"| RETURN_DATA
    SEED_MOCK --> RETURN_DATA
```

Sources: [src/app/loader.ts:10-59]()

## Public Assets Structure

Static assets served directly by the web server:

| File | Purpose |
|------|---------|
| `next.svg` | Next.js logo |
| `vercel.svg` | Vercel deployment logo |
| `globe.svg` | Global/international icon |
| `file.svg` | File/document icon |

```mermaid
graph TB
    subgraph "Public Assets"
        LOGOS["Brand Logos"]
        ICONS["UI Icons"]
        STATIC["Static Resources"]
    end
    
    subgraph "SVG Assets"
        NEXT_SVG["next.svg"]
        VERCEL_SVG["vercel.svg"]
        GLOBE_SVG["globe.svg"]
        FILE_SVG["file.svg"]
    end
    
    LOGOS --> NEXT_SVG
    LOGOS --> VERCEL_SVG
    ICONS --> GLOBE_SVG
    ICONS --> FILE_SVG
```

Sources: [public/next.svg:1](), [public/vercel.svg:1](), [public/globe.svg:1](), [public/file.svg:1]()

## Import Path Conventions

The codebase uses TypeScript path mapping with the `@/` alias for clean imports:

| Import Pattern | Maps To | Purpose |
|---------------|---------|---------|
| `@/lib/db/db` | `src/lib/db/db` | Database connection |
| `@/lib/db/schema` | `src/lib/db/schema` | Database schema |
| `@/lib/testing/engine` | `src/lib/testing/engine` | Testing engine types |
| `@/lib/testing/mock` | `src/lib/testing/mock` | Mock test data |

Sources: [src/app/loader.ts:3-6]()