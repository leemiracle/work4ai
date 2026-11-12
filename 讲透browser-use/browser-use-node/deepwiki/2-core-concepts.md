<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/browser-use-node · page 2 Core Concepts · fetched 2026-10-30 -->

# Core Concepts

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/client.ts](src/client.ts)
- [src/resources/tasks.ts](src/resources/tasks.ts)

</details>



This document covers the fundamental architecture and design patterns of the browser-use-node SDK. It explains how the main components work together to provide browser automation capabilities through AI agents.

For detailed usage examples, see [Basic Usage Examples](#6.1). For specific API method documentation, see [API Documentation](#7.1).

## Architecture Overview

The browser-use-node SDK follows a resource-oriented client architecture where a central `BrowserUse` client provides access to specialized API resources. Each resource handles a specific domain of functionality.

**Client-Resource Architecture**

```mermaid
graph TB
    BrowserUse["BrowserUse Client<br/>(src/client.ts:154)"]
    
    subgraph "API Resources"
        Tasks["Tasks<br/>(src/resources/tasks.ts:18)"]
        Sessions["Sessions<br/>(src/resources/sessions.ts)"]
        Users["Users<br/>(src/resources/users.ts)"]
        BrowserProfiles["BrowserProfiles<br/>(src/resources/browser-profiles.ts)"]
        AgentProfiles["AgentProfiles<br/>(src/resources/agent-profiles.ts)"]
    end
    
    subgraph "Core Infrastructure"
        APIPromise["APIPromise<br/>(src/core/api-promise.ts)"]
        ErrorHandling["Error Classes<br/>(src/core/error.ts)"]
        Authentication["Authentication<br/>X-Browser-Use-API-Key"]
    end
    
    BrowserUse --> Tasks
    BrowserUse --> Sessions
    BrowserUse --> Users
    BrowserUse --> BrowserProfiles
    BrowserUse --> AgentProfiles
    
    Tasks --> APIPromise
    Sessions --> APIPromise
    Users --> APIPromise
    BrowserProfiles --> APIPromise
    AgentProfiles --> APIPromise
    
    BrowserUse --> ErrorHandling
    BrowserUse --> Authentication
```

Sources: [src/client.ts:154-765](), [src/resources/tasks.ts:18]()

## Core Components

### BrowserUse Client

The `BrowserUse` class serves as the main entry point and handles client configuration, authentication, and request infrastructure.

**Key Configuration Options**

| Option | Purpose | Default |
|--------|---------|---------|
| `apiKey` | Authentication credential | `process.env.BROWSER_USE_API_KEY` |
| `baseURL` | API endpoint | `https://api.browser-use.com/api/v2` |
| `timeout` | Request timeout (ms) | `60000` |
| `maxRetries` | Retry attempts | `2` |
| `logLevel` | Logging verbosity | `warn` |

Sources: [src/client.ts:76-149](), [src/client.ts:181-216]()

### Resource Hierarchy

Each API resource extends `APIResource` and provides domain-specific functionality through a consistent interface pattern.

**Resource Method Patterns**

```mermaid
graph LR
    APIResource["APIResource<br/>(src/core/resource.ts)"]
    
    subgraph "Common Methods"
        Create["create()"]
        Retrieve["retrieve()"]
        Update["update()"]
        List["list()"]
        Delete["delete()"]
    end
    
    subgraph "Tasks Specific"
        Stream["stream()"]
        Run["run()"]
        GetLogs["getLogs()"]
        GetOutputFile["getOutputFile()"]
    end
    
    APIResource --> Create
    APIResource --> Retrieve
    APIResource --> Update
    APIResource --> List
    APIResource --> Delete
    
    Tasks --> Stream
    Tasks --> Run
    Tasks --> GetLogs
    Tasks --> GetOutputFile
```

Sources: [src/resources/tasks.ts:18-393]()

## Tasks: The Central Concept

Tasks represent individual browser automation jobs executed by AI agents. They are the primary unit of work in the system.

**Task Lifecycle States**

```mermaid
stateDiagram-v2
    [*] --> started
    started --> paused
    started --> finished
    started --> stopped
    paused --> started
    paused --> stopped
    finished --> [*]
    stopped --> [*]
    
    note right of started : "Task is actively running"
    note right of paused : "Execution temporarily halted"
    note right of finished : "Task completed successfully"
    note right of stopped : "Task terminated"
```

**Task Data Model**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Unique task identifier |
| `sessionId` | `string` | Associated browser session |
| `status` | `TaskStatus` | Current execution state |
| `task` | `string` | Task instruction/prompt |
| `steps` | `TaskStepView[]` | Execution steps taken |
| `doneOutput` | `string` | Final task result |

Sources: [src/resources/tasks.ts:511-559](), [src/resources/tasks.ts:466]()

## Sessions and Profiles

Sessions represent browser instances, while profiles define configuration for both browsers and AI agents.

**Profile System Architecture**

```mermaid
graph TB
    subgraph "Profile Types"
        BrowserProfile["BrowserProfile<br/>Browser settings, proxies"]
        AgentProfile["AgentProfile<br/>AI model, behavior"]
    end
    
    subgraph "Session Management"
        Session["Session<br/>Browser instance"]
        SessionActive["status: 'active'"]
        SessionStopped["status: 'stopped'"]
    end
    
    subgraph "Task Execution"
        TaskCreate["Task.create()"]
        TaskRun["Task.run()"]
    end
    
    BrowserProfile --> Session
    AgentProfile --> TaskCreate
    Session --> TaskCreate
    TaskCreate --> TaskRun
    
    Session --> SessionActive
    Session --> SessionStopped
```

Sources: [src/resources/browser-profiles.ts](), [src/resources/agent-profiles.ts](), [src/resources/sessions.ts]()

## Authentication and Configuration

The SDK uses API key authentication with configurable client options for different deployment environments.

**Configuration Sources**

```mermaid
graph TB
    subgraph "Configuration Priority"
        Constructor["Constructor Options<br/>new BrowserUse({...})"]
        Environment["Environment Variables<br/>BROWSER_USE_API_KEY"]
        Defaults["SDK Defaults<br/>timeout: 60000"]
    end
    
    subgraph "Authentication Flow"
        APIKey["API Key"]
        AuthHeaders["X-Browser-Use-API-Key Header"]
        CloudAPI["Browser Use Cloud API"]
    end
    
    Constructor --> APIKey
    Environment --> APIKey
    Defaults --> Constructor
    
    APIKey --> AuthHeaders
    AuthHeaders --> CloudAPI
```

Sources: [src/client.ts:182-196](), [src/client.ts:252-254]()

## Error Handling Architecture

The SDK implements a hierarchical error system with automatic retry logic for transient failures.

**Error Class Hierarchy**

```mermaid
graph TB
    BrowserUseError["BrowserUseError<br/>Base SDK error"]
    
    subgraph "API Errors"
        APIError["APIError<br/>HTTP response errors"]
        BadRequest["BadRequestError<br/>400"]
        Auth["AuthenticationError<br/>401"]
        NotFound["NotFoundError<br/>404"]
        RateLimit["RateLimitError<br/>429"]
        ServerError["InternalServerError<br/>500+"]
    end
    
    subgraph "Connection Errors"
        APIConnection["APIConnectionError<br/>Network failures"]
        APITimeout["APIConnectionTimeoutError<br/>Request timeouts"]
        APIAbort["APIUserAbortError<br/>User cancellation"]
    end
    
    BrowserUseError --> APIError
    BrowserUseError --> APIConnection
    BrowserUseError --> APITimeout
    BrowserUseError --> APIAbort
    
    APIError --> BadRequest
    APIError --> Auth
    APIError --> NotFound
    APIError --> RateLimit
    APIError --> ServerError
```

**Retry Logic**

The client automatically retries requests for specific conditions:
- HTTP 408 (Request Timeout)
- HTTP 409 (Conflict/Lock Timeout) 
- HTTP 429 (Rate Limited)
- HTTP 5XX (Server Errors)
- Network connection failures

Retry behavior uses exponential backoff with jitter, respecting `Retry-After` headers when provided.

Sources: [src/client.ts:744-756](), [src/client.ts:563-638](), [src/core/error.ts]()

---

