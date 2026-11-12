<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/qa-use · page 3 Core Concepts · fetched 2026-10-30 -->

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

