<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/qa-use · page 6 Background Processing · fetched 2026-10-30 -->

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

